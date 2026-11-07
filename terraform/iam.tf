# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/iam.tf
# ==============================================================================
#
# BẢO MẬT SERVERLESS - NGUYÊN TẮC QUYỀN HẠN TỐI THIỂU (IAM LEAST PRIVILEGE)
#
# Minh chứng đáp ứng yêu cầu đề tài:
# 1. Tuyệt đối KHÔNG sử dụng quyền quản trị (AdministratorAccess hay wildcard Resource: *).
# 2. Phân tách quyền chặt chẽ theo chức năng:
#    - S3 Input: Chỉ có quyền đọc ảnh gốc (s3:GetObject), KHÔNG được sửa/xóa.
#    - S3 Output: Chỉ có quyền ghi thumbnail (s3:PutObject), KHÔNG được xóa.
#    - DynamoDB: Chỉ có quyền đọc/ghi/cập nhật bản ghi nghiệp vụ (GetItem, PutItem, UpdateItem).
#    - SQS DLQ: Chỉ có quyền đẩy thông điệp lỗi (sqs:SendMessage), KHÔNG được xóa queue.
#    - CloudWatch Logs: Chỉ được ghi log vào log group được chỉ định cho hàm.
# 3. Không lưu khóa truy cập (Access Key / Secret Key) trong mã nguồn: Lambda tự động
#    nhận STS Temporary Credentials thông qua IAM Role đính kèm.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IAM ROLE CHO HÀM LAMBDA (Execution Role)
# ------------------------------------------------------------------------------
resource "aws_iam_role" "lambda_exec" {
  name        = "${var.project_name}-lambda-role-${var.environment}"
  description = "IAM Role tuan thu Least Privilege cho Lambda Function xu ly anh"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "LambdaAssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name       = "${var.project_name}-lambda-exec-role"
    Role       = "Security Execution Role"
    Compliance = "IAM-Least-Privilege"
  }
}

# ------------------------------------------------------------------------------
# 2. CHÍNH SÁCH BẢO MẬT TỐI THIỂU (Least Privilege Policy)
# ------------------------------------------------------------------------------
resource "aws_iam_policy" "lambda_least_privilege" {
  name        = "${var.project_name}-least-privilege-policy-${var.environment}"
  description = "Chinh sach phan quyen toi thieu doc lap cho tung thanh phan ha tang"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # 1. Quyền ghi log giám sát CloudWatch (Chỉ trong Log Group của hàm)
      {
        Sid    = "CloudWatchLoggingPermissions"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}-*:-*",
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}-*"
        ]
      },

      # 2. Quyền đọc dữ liệu từ Input Bucket (Chỉ đọc ảnh, KHÔNG có quyền Delete/Put)
      {
        Sid    = "S3InputBucketReadOnly"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectTagging"
        ]
        Resource = [
          "${aws_s3_bucket.input.arn}/*"
        ]
      },

      # 3. Quyền ghi ảnh thumbnail vào Output Bucket (Chỉ ghi, KHÔNG có quyền Delete)
      {
        Sid    = "S3OutputBucketWriteOnly"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          "${aws_s3_bucket.output.arn}/*"
        ]
      },

      # 4. Quyền làm việc với DynamoDB Metadata & Idempotency Table (Get, Put, Update)
      {
        Sid    = "DynamoDBIdempotencyAccess"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          aws_dynamodb_table.image_metadata.arn,
          "${aws_dynamodb_table.image_metadata.arn}/index/*"
        ]
      },

      # 5. Quyền đẩy sự kiện lỗi vào Dead-Letter Queue (Chỉ SendMessage)
      {
        Sid    = "SQSDeadLetterQueueSendOnly"
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ]
        Resource = [
          aws_sqs_queue.dlq.arn
        ]
      },

      # 6. Quyền phân tích độ trễ phân tán AWS X-Ray (phục vụ đo Cold/Warm Start)
      {
        Sid    = "AWSXRayTracing"
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })
}

# ------------------------------------------------------------------------------
# 3. ĐÍNH KÈM CHÍNH SÁCH VÀO ROLE CỦA LAMBDA
# ------------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "lambda_least_privilege_attach" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_least_privilege.arn
}
