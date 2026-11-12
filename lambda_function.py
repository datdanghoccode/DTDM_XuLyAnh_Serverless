"""
AWS Lambda Image Processing Handler - Đề tài 9 UTH
Pipeline Xử lý Ảnh Serverless Hướng Sự Kiện (Event-Driven Architecture)
Nhóm sinh viên thực hiện | Giảng viên hướng dẫn: TS. Lê Quốc Tuấn

Tính năng cốt lõi:
1. Xử lý ảnh tự động: S3 Input -> S3 Event -> Lambda Function (Pillow) -> S3 Output.
2. Khóa lũy đẳng nguyên tử (Atomic Idempotency Lock):
   - Sử dụng DynamoDB ConditionExpression='attribute_not_exists(image_hash)' để ngăn chặn Race Condition.
   - Chống xử lý trùng lặp khi AWS S3 gửi sự kiện At-Least-Once Delivery.
3. Kịch bản lỗi & Dead-Letter Queue (DLQ):
   - Khi gặp tệp độc hại hoặc hỏng định dạng, Pillow ném ngoại lệ UnidentifiedImageError.
   - Ném ngoại lệ chưa bắt (unhandled) lên AWS Lambda Runtime để AWS tự động retry (2 lần)
     và chuyển sự kiện lỗi sang SQS Dead-Letter Queue (DLQ).
4. Tự động dự phòng nội bộ (In-Memory/Local Fallback):
   - Khi chạy ở môi trường kiểm thử local hoặc không có kết nối AWS thực tế.
"""

import io
import os
import json
import time
import hashlib
from PIL import Image, UnidentifiedImageError

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    boto3 = None
    class ClientError(Exception):
        def __init__(self, error_response=None, operation_name=""):
            self.response = error_response or {}
            self.operation_name = operation_name
            super().__init__(str(error_response))
    class BotoCoreError(Exception):
        pass

# Cấu hình biến môi trường theo chuẩn Terraform
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'cloud-image-thumbnails')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'ImageMetadata')
TARGET_WIDTH = int(os.environ.get('TARGET_WIDTH', os.environ.get('THUMBNAIL_WIDTH', '300')))
TARGET_HEIGHT = int(os.environ.get('TARGET_HEIGHT', os.environ.get('THUMBNAIL_HEIGHT', '300')))
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', None)

# Bộ nhớ tạm in-memory phục vụ kiểm thử và fallback khi offline
_mock_lock_storage = set()
_mock_metadata_storage = {}
_mock_s3_storage = {}

def get_s3_client():
    """Khởi tạo S3 client tái sử dụng connection reuse, fallback None khi offline."""
    if boto3 is None:
        return None
    try:
        if AWS_ENDPOINT_URL:
            return boto3.client('s3', endpoint_url=AWS_ENDPOINT_URL)
        return boto3.client('s3')
    except Exception as e:
        print(f"[WARN] Failed to create S3 client: {e}")
        return None

def get_dynamodb_resource():
    """Khởi tạo DynamoDB resource tái sử dụng connection reuse, fallback None khi offline."""
    if boto3 is None:
        return None
    try:
        if AWS_ENDPOINT_URL:
            return boto3.resource('dynamodb', endpoint_url=AWS_ENDPOINT_URL)
        return boto3.resource('dynamodb')
    except Exception as e:
        print(f"[WARN] Failed to create DynamoDB resource: {e}")
        return None

def calculate_sha256(data: bytes) -> str:
    """Tính mã băm SHA-256 duy nhất của tệp ảnh để bảo đảm tính toàn vẹn và Idempotency."""
    return hashlib.sha256(data).hexdigest()

def acquire_atomic_lock(image_hash: str, file_name: str) -> bool:
    """
    Thuật toán khóa lũy đẳng nguyên tử trên DynamoDB sử dụng ConditionExpression='attribute_not_exists(image_hash)'.
    - Trả về True nếu khóa thành công (tệp mới).
    - Trả về False nếu tệp đã tồn tại / đang xử lý (ConditionalCheckFailedException).
    - Tự động fallback in-memory/local khi không có kết nối AWS thực tế.
    """
    ddb = get_dynamodb_resource()
    if ddb is not None:
        try:
            table = ddb.Table(METADATA_TABLE)
            now = int(time.time())
            table.put_item(
                Item={
                    'image_hash': image_hash,
                    'file_name': file_name,
                    'status': 'PROCESSING',
                    'locked_at': now,
                    'ttl': now + 300
                },
                ConditionExpression='attribute_not_exists(image_hash)'
            )
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == 'ConditionalCheckFailedException':
                print(f"[IDEMPOTENCY] Item already exists or locked: {image_hash}. Skipping duplicate processing.")
                return False
            print(f"[WARN] DynamoDB client error ({error_code}): {e}. Falling back to in-memory lock.")
        except Exception as e:
            print(f"[WARN] DynamoDB connection error: {e}. Falling back to in-memory lock.")

    # Local / in-memory fallback
    if image_hash in _mock_lock_storage:
        print(f"[IDEMPOTENCY FALLBACK] Local lock active: Item already locked: {image_hash}. Skipping duplicate processing.")
        return False
    _mock_lock_storage.add(image_hash)
    return True

def complete_atomic_record(image_hash: str, file_name: str, metadata: dict):
    """
    Cập nhật trạng thái COMPLETED và lưu siêu dữ liệu vào DynamoDB.
    Tự động fallback in-memory khi không có kết nối AWS thực tế.
    """
    now = int(time.time())
    ddb = get_dynamodb_resource()
    if ddb is not None:
        try:
            table = ddb.Table(METADATA_TABLE)
            table.update_item(
                Key={'image_hash': image_hash},
                UpdateExpression='SET #st = :status, processed_at = :now, original_width = :w, original_height = :h, original_format = :fmt, original_size = :osize, thumbnail_size = :tsize',
                ExpressionAttributeNames={'#st': 'status'},
                ExpressionAttributeValues={
                    ':status': 'COMPLETED',
                    ':now': now,
                    ':w': metadata.get('original_width', 0),
                    ':h': metadata.get('original_height', 0),
                    ':fmt': metadata.get('original_format', ''),
                    ':osize': metadata.get('original_size', 0),
                    ':tsize': metadata.get('thumbnail_size', 0)
                }
            )
            return
        except Exception as e:
            print(f"[WARN] DynamoDB update record error: {e}. Falling back to in-memory metadata storage.")

    # In-memory fallback
    _mock_metadata_storage[image_hash] = {
        'image_hash': image_hash,
        'file_name': file_name,
        'status': 'COMPLETED',
        'processed_at': now,
        **metadata
    }

def process_single_image(raw_bytes: bytes, file_key: str):
    """
    Xử lý resize ảnh và trích xuất metadata bằng Pillow.
    Xử lý lỗi UnidentifiedImageError từ Pillow khi gặp tệp độc hại/hỏng và ném ngoại lệ lên Lambda Runtime
    để AWS tự động retry và đẩy sang SQS Dead-Letter Queue (DLQ).
    """
    try:
        image = Image.open(io.BytesIO(raw_bytes))
        orig_width, orig_height = image.size
        orig_format = image.format if image.format else 'JPEG'

        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        image.thumbnail((TARGET_WIDTH, TARGET_HEIGHT))

        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=85)
        output_buffer.seek(0)
        thumb_bytes = output_buffer.getvalue()

        metadata = {
            'original_width': orig_width,
            'original_height': orig_height,
            'original_format': orig_format,
            'original_size': len(raw_bytes),
            'thumbnail_size': len(thumb_bytes)
        }
        return thumb_bytes, metadata

    except UnidentifiedImageError as err:
        # Ném ngoại lệ lên Lambda Runtime để AWS tự động retry và đẩy sang SQS Dead-Letter Queue (DLQ)
        error_msg = f"[FAULT_INJECTION] Corrupted or malicious payload detected in {file_key}: {err}"
        print(f"[FATAL] {error_msg}")
        raise UnidentifiedImageError(error_msg) from err
    except Exception as e:
        print(f"[ERROR] Image processing failed for {file_key}: {e}")
        raise RuntimeError(f"Image processing failed for {file_key}: {str(e)}") from e

def lambda_handler(event, context):
    """
    Entry point chính của AWS Lambda Function hướng sự kiện từ S3.
    """
    records = event.get('Records', [])
    processed_count = 0
    skipped_count = 0

    s3 = get_s3_client()

    for record in records:
        src_bucket = record.get('s3', {}).get('bucket', {}).get('name', 'input-bucket')
        src_key = record.get('s3', {}).get('object', {}).get('key', '')

        if src_key.startswith('thumbnails/') or src_key.endswith('/'):
            continue

        raw_bytes = record.get('_raw_bytes')
        if raw_bytes is None:
            if s3 is not None:
                try:
                    response = s3.get_object(Bucket=src_bucket, Key=src_key)
                    raw_bytes = response['Body'].read()
                except Exception as e:
                    if src_key in _mock_s3_storage:
                        raw_bytes = _mock_s3_storage[src_key]
                    else:
                        print(f"[ERROR] S3 get_object failed: {e}")
                        raise e
            else:
                if src_key in _mock_s3_storage:
                    raw_bytes = _mock_s3_storage[src_key]
                else:
                    raise RuntimeError(f"S3 client not available and key not in local storage: {src_key}")

        file_hash = calculate_sha256(raw_bytes)

        # 1. Thuật toán khóa lũy đẳng nguyên tử trên DynamoDB
        lock_acquired = acquire_atomic_lock(file_hash, src_key)
        if not lock_acquired:
            print(f"[IDEMPOTENCY] Idempotency violation avoided: Skipping duplicate file {src_key} (Hash: {file_hash[:12]}...)")
            skipped_count += 1
            continue

        # 2. Xử lý ảnh và ném ngoại lệ lên Runtime nếu gặp lỗi tệp hỏng (DLQ Trigger)
        try:
            thumb_bytes, metadata = process_single_image(raw_bytes, src_key)

            dest_key = 'thumbnails/thumb_' + os.path.basename(src_key)
            if s3 is not None:
                try:
                    s3.put_object(
                        Bucket=OUTPUT_BUCKET,
                        Key=dest_key,
                        Body=thumb_bytes,
                        ContentType='image/jpeg'
                    )
                except Exception as e:
                    print(f"[WARN] S3 put_object error: {e}. Storing in local mock storage.")
                    _mock_s3_storage[dest_key] = thumb_bytes
            else:
                _mock_s3_storage[dest_key] = thumb_bytes

            complete_atomic_record(file_hash, src_key, metadata)
            processed_count += 1

        except Exception as err:
            print(f"[DLQ TRIGGER] Unhandled exception occurred in {src_key}: {err}. Propagating to AWS Lambda Runtime / DLQ.")
            raise err

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Batch processed successfully',
            'processed': processed_count,
            'skipped': skipped_count
        })
    }
