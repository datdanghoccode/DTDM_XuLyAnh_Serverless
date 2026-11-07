# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/sqs.tf
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. DEAD-LETTER QUEUE (DLQ)
# Nơi chứa các thông điệp lỗi không thể xử lý sau số lần retry (file hỏng, timeout...)
# Giúp hệ thống không bị mất dữ liệu lỗi, hỗ trợ SRE kiểm tra và replay (Runbook)
# ------------------------------------------------------------------------------
resource "aws_sqs_queue" "dlq" {
  name                       = "${var.project_name}-dlq-${var.environment}"
  message_retention_seconds  = var.dlq_message_retention_seconds # Mặc định 14 ngày
  visibility_timeout_seconds = 60
  sqs_managed_sse_enabled    = true

  tags = {
    Name        = "${var.project_name}-dlq"
    Role        = "Dead-Letter Queue"
    Description = "Hang doi luu thong diep su kien loi cho SRE dieu tra va tai xu ly"
  }
}

# ------------------------------------------------------------------------------
# 2. CHÍNH SÁCH BẢO MẬT HÀNG ĐỢI SQS (Queue Policy)
# Chỉ cho phép Lambda Function của hệ thống và tài khoản sở hữu gửi message
# ------------------------------------------------------------------------------
resource "aws_sqs_queue_policy" "dlq_policy" {
  queue_url = aws_sqs_queue.dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowLambdaToSendDLQMessages"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.lambda_exec.arn
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.dlq.arn
      }
    ]
  })
}
