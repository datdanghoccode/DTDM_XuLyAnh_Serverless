import io
import os
import json
import time
import hashlib
import boto3
from botocore.exceptions import ClientError
from PIL import Image, UnidentifiedImageError

OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'cloud-image-thumbnails')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'ImageMetadata')
TARGET_WIDTH = int(os.environ.get('TARGET_WIDTH', '300'))
TARGET_HEIGHT = int(os.environ.get('TARGET_HEIGHT', '300'))
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', None)

_mock_lock_storage = set()

def get_s3_client():
    if AWS_ENDPOINT_URL:
        return boto3.client('s3', endpoint_url=AWS_ENDPOINT_URL)
    return boto3.client('s3')

def get_dynamodb_resource():
    if AWS_ENDPOINT_URL:
        return boto3.resource('dynamodb', endpoint_url=AWS_ENDPOINT_URL)
    return boto3.resource('dynamodb')

def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()

def acquire_atomic_lock(image_hash, file_name):
    try:
        ddb = get_dynamodb_resource()
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
            print('Idempotency lock: Item already exists or locked: ' + image_hash)
            return False
        print('DynamoDB lock error: ' + str(e))
        return False
    except Exception as e:
        if image_hash in _mock_lock_storage:
            print('Local fallback: Item already locked: ' + image_hash)
            return False
        _mock_lock_storage.add(image_hash)
        return True

def complete_atomic_record(image_hash, file_name, metadata):
    try:
        ddb = get_dynamodb_resource()
        table = ddb.Table(METADATA_TABLE)
        now = int(time.time())
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
    except Exception as e:
        print('DynamoDB update record error: ' + str(e))

def process_single_image(raw_bytes, file_key):
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

    except UnidentifiedImageError:
        raise ValueError('Corrupted or invalid image format: ' + file_key)
    except Exception as e:
        raise RuntimeError('Image processing failed: ' + str(e))

def lambda_handler(event, context):
    records = event.get('Records', [])
    processed_count = 0
    skipped_count = 0

    s3 = get_s3_client()

    for record in records:
        src_bucket = record['s3']['bucket']['name']
        src_key = record['s3']['object']['key']

        if src_key.startswith('thumbnails/') or src_key.endswith('/'):
            continue

        response = s3.get_object(Bucket=src_bucket, Key=src_key)
        raw_bytes = response['Body'].read()

        file_hash = calculate_sha256(raw_bytes)

        lock_acquired = acquire_atomic_lock(file_hash, src_key)
        if not lock_acquired:
            print('Idempotency violation avoided: Skipping ' + src_key)
            skipped_count += 1
            continue

        try:
            thumb_bytes, metadata = process_single_image(raw_bytes, src_key)

            dest_key = 'thumbnails/thumb_' + os.path.basename(src_key)
            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=dest_key,
                Body=thumb_bytes,
                ContentType='image/jpeg'
            )

            complete_atomic_record(file_hash, src_key, metadata)
            processed_count += 1

        except Exception as err:
            print('Error occurred: ' + str(err))
            raise err

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Batch processed successfully',
            'processed': processed_count,
            'skipped': skipped_count
        })
    }
