# -*- coding: utf-8 -*-
"""
web1_learning_hub/app.py
Flask Application for Web 1 Knowledge & Learning Hub (:5001).
Serves 7 academic modules and Code Walkthrough API.
"""

from flask import Flask, jsonify, render_template

def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if test_config:
        app.config.update(test_config)

    # Catalog of source code snippets for Interactive Walkthrough
    SNIPPETS = {
        "idempotency_lock": {
            "title": "Khóa Lũy Đẳng Nguyên Tử DynamoDB",
            "file": "src/lambda_function.py",
            "language": "python",
            "description": "Thao tác PutItem nguyên tử với ConditionExpression: attribute_not_exists(image_hash). Nếu nhận sự kiện trùng lặp, DynamoDB ném ConditionalCheckFailedException và handler thoát an toàn trong < 2.5 ms mà không resize lại ảnh.",
            "code": """# src/lambda_function.py - Atomic Idempotency Lock
def acquire_idempotency_lock(table, image_hash, filename, size_bytes):
    \"\"\"
    Thực hiện ghi nguyên tử có điều kiện vào bảng DynamoDB ImageMetadata.
    Triệt tiêu hoàn toàn Race Condition của phương pháp Check-then-Act.
    \"\"\"
    item = {
        'image_hash': image_hash,        # Khóa chính Partition Key (SHA-256)
        'filename': filename,
        'status': 'PROCESSING',          # Đặt trạng thái ban đầu
        'size_bytes': size_bytes,
        'created_at': int(time.time()),
        'ttl': int(time.time()) + 86400  # Tự hủy sau 24h nếu cần
    }
    try:
        table.put_item(
            Item=item,
            # Điều kiện nguyên tử ở tầng lưu trữ DynamoDB:
            ConditionExpression='attribute_not_exists(image_hash) OR #st = :failed',
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':failed': 'FAILED'}
        )
        return True, "ACQUIRED"
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Phát hiện sự kiện trùng lặp -> Bỏ qua xử lý ngay lập tức
            logger.info(f"[IDEMPOTENT] Duplicate event for hash {image_hash}. Skip processing.")
            return False, "SKIPPED_DUPLICATE"
        raise e""",
            "highlights": [15, 16, 17, 21, 22, 23]
        },
        "iam_least_privilege": {
            "title": "Chính Sách IAM Tối Thiểu (OWASP SAS-01)",
            "file": "terraform/iam.tf",
            "language": "hcl",
            "description": "Khai báo 6 Statement IAM độc lập không dùng wildcard (*). Lambda chỉ có quyền GetObject từ Input Bucket, PutObject vào Output Bucket, PutItem vào DynamoDB, và SendMessage vào SQS DLQ.",
            "code": """# terraform/iam.tf - IAM Least Privilege Policy
resource "aws_iam_policy" "lambda_least_privilege" {
  name        = "LambdaImageProcessingLeastPrivilege"
  description = "Chính sách phân quyền tối thiểu theo chuẩn OWASP Serverless SAS-01"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Statement 1: Chỉ đọc tệp từ Input Bucket
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_bucket.raw_input.arn}/*"
      },
      # Statement 2: Chỉ ghi ảnh thumbnail vào Output Bucket
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.thumbnails.arn}/*"
      },
      # Statement 3: Chỉ ghi metadata vào đúng bảng DynamoDB
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem"]
        Resource = aws_dynamodb_table.image_metadata.arn
      },
      # Statement 4: Chỉ gửi tin nhắn lỗi vào Dead-Letter Queue
      {
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.image_dlq.arn
      }
    ]
  })
}""",
            "highlights": [9, 10, 11, 16, 17, 18, 23, 24, 25, 30, 31, 32]
        },
        "sqs_dlq_redrive": {
            "title": "Hàng Đợi SQS DLQ & Cơ Chế Redrive",
            "file": "terraform/sqs.tf",
            "language": "hcl",
            "description": "Cấu hình hàng đợi đệm tải và Dead-Letter Queue cách ly Poison Pill sau 3 lần retry với exponential backoff. Thông điệp được lưu giữ 14 ngày để SRE điều tra.",
            "code": """# terraform/sqs.tf - SQS Dead-Letter Queue & Redrive Policy
resource "aws_sqs_queue" "image_dlq" {
  name                      = "cloud-image-serverless-dlq"
  message_retention_seconds = 1209600  # Lưu giữ an toàn 14 ngày
  kms_master_key_id         = "alias/aws/sqs" # Mã hóa at-rest SSE
}

resource "aws_sqs_queue" "image_event_queue" {
  name                      = "cloud-image-event-queue"
  visibility_timeout_seconds = 180     # Gấp 6 lần timeout của Lambda (30s)
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.image_dlq.arn
    maxReceiveCount     = 3            # Sau đúng 3 lần retry lỗi -> Đẩy vào DLQ
  })
}

# CloudWatch Alarm khi có thông điệp trong DLQ
resource "aws_cloudwatch_metric_alarm" "dlq_alarm" {
  alarm_name          = "ServerlessImageDLQMessagesAlarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0              # Kích hoạt báo động ngay khi DLQ > 0
}""",
            "highlights": [4, 13, 14, 15, 25]
        },
        "pillow_resize_safe": {
            "title": "Xử Lý Ảnh Trong RAM & Dọn Sạch /tmp (OWASP SAS-05)",
            "file": "src/lambda_function.py",
            "language": "python",
            "description": "Xử lý trực tiếp luồng byte trong RAM qua io.BytesIO(), kiểm tra MAX_IMAGE_PIXELS ngăn chặn Image Bomb, và dọn dẹp bộ nhớ tạm tại khối finally.",
            "code": """# src/lambda_function.py - Safe In-Memory Image Resizing
from PIL import Image, ImageOps
import io

# Giới hạn số pixel tối đa ngăn chặn Memory Exhaustion / Image Bomb
Image.MAX_IMAGE_PIXELS = 50_000_000

def generate_thumbnail_in_memory(raw_bytes):
    \"\"\"
    Resize ảnh thuần túy trong RAM (io.BytesIO), tuyệt đối không lưu ra /tmp
    ngăn ngừa rò rỉ dữ liệu giữa các lần gọi ấm (Warm Invocations).
    \"\"\"
    in_buffer = io.BytesIO(raw_bytes)
    out_buffer = io.BytesIO()
    try:
        # Xác thực cấu trúc tệp nhị phân trước khi xử lý
        with Image.open(in_buffer) as img:
            img.verify()
        
        in_buffer.seek(0)
        with Image.open(in_buffer) as img:
            img = ImageOps.exif_transpose(img)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img.save(out_buffer, format='JPEG', quality=85, optimize=True)
            return out_buffer.getvalue()
    finally:
        in_buffer.close()
        out_buffer.close()""",
            "highlights": [5, 17, 18, 24, 25, 27, 28]
        }
    }

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "app": "web1_learning_hub",
            "port": 5001,
            "modules_count": 7
        })

    @app.route("/api/code/<snippet_id>", methods=["GET"])
    def get_code_snippet(snippet_id):
        if snippet_id in SNIPPETS:
            return jsonify(SNIPPETS[snippet_id])
        return jsonify({"error": f"Snippet '{snippet_id}' not found"}), 404

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)
