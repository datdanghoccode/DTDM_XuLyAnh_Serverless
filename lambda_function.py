import io
import os
import json
import time
import hashlib
import boto3
from PIL import Image, UnidentifiedImageError

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'cloud-image-thumbnails')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'ImageMetadata')
TARGET_WIDTH = int(os.environ.get('TARGET_WIDTH', '300'))
TARGET_HEIGHT = int(os.environ.get('TARGET_HEIGHT', '300'))

def calculate_sha256(data):
    return hashlib.sha256(data).hexdigest()

def check_idempotency(image_hash):
    try:
        table = dynamodb.Table(METADATA_TABLE)
        response = table.get_item(Key={'image_hash': image_hash})
        if 'Item' in response:
            return True
    except Exception as e:
        print('DynamoDB read error: ' + str(e))
    return False

def save_metadata(image_hash, file_name, metadata):
    try:
        table = dynamodb.Table(METADATA_TABLE)
        item = {
            'image_hash': image_hash,
            'file_name': file_name,
            'processed_at': int(time.time()),
            'original_width': metadata.get('original_width', 0),
            'original_height': metadata.get('original_height', 0),
            'original_format': metadata.get('original_format', ''),
            'original_size': metadata.get('original_size', 0),
            'thumbnail_size': metadata.get('thumbnail_size', 0)
        }
        table.put_item(Item=item)
    except Exception as e:
        print('DynamoDB write error: ' + str(e))

def lambda_handler(event, context):
    records = event.get('Records', [])
    for record in records:
        src_bucket = record['s3']['bucket']['name']
        src_key = record['s3']['object']['key']

        if src_key.startswith('thumbnails/') or src_key.endswith('/'):
            continue

        response = s3_client.get_object(Bucket=src_bucket, Key=src_key)
        raw_bytes = response['Body'].read()

        file_hash = calculate_sha256(raw_bytes)
        if check_idempotency(file_hash):
            print('Idempotency check: File already processed, skipping: ' + src_key)
            continue

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

        except UnidentifiedImageError:
            raise Exception('Corrupted image file: ' + src_key)
        except Exception as e:
            raise Exception('Failed to process image: ' + str(e))

        dest_key = 'thumbnails/thumb_' + os.path.basename(src_key)
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=dest_key,
            Body=thumb_bytes,
            ContentType='image/jpeg'
        )

        metadata = {
            'original_width': orig_width,
            'original_height': orig_height,
            'original_format': orig_format,
            'original_size': len(raw_bytes),
            'thumbnail_size': len(thumb_bytes)
        }
        save_metadata(file_hash, src_key, metadata)

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Success'})
    }
