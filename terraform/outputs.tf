# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/outputs.tf
# ==============================================================================
#
# BÀN GIAO THÔNG SỐ HẠ TẦNG CHO THÀNH VIÊN TRONG NHÓM:
# - Kỹ sư Phần mềm (Trần Ngọc Lâm): Sử dụng các biến môi trường và tên bucket/bảng
#   để hoàn thiện hàm src/lambda_function.py.
# - Kỹ sư SRE (Vũ Thành Đạt): Sử dụng input_bucket_name để tải dataset 150 file,
#   và dlq_queue_url để giám sát / kiểm thử kịch bản lỗi và viết RUNBOOK.
# ==============================================================================

output "aws_region" {
  description = "AWS Region triển khai hạ tầng"
  value       = var.aws_region
}

output "input_bucket_name" {
  description = "Tên S3 Input Bucket (Upload ảnh vào đây để kích hoạt Lambda)"
  value       = aws_s3_bucket.input.id
}

output "input_bucket_arn" {
  description = "ARN của S3 Input Bucket"
  value       = aws_s3_bucket.input.arn
}

output "output_bucket_name" {
  description = "Tên S3 Output Bucket (Nơi chứa thumbnail sau khi xử lý thành công)"
  value       = aws_s3_bucket.output.id
}

output "output_bucket_arn" {
  description = "ARN của S3 Output Bucket"
  value       = aws_s3_bucket.output.arn
}

output "dynamodb_table_name" {
  description = "Tên bảng DynamoDB lưu metadata và trạng thái Idempotency"
  value       = aws_dynamodb_table.image_metadata.name
}

output "dynamodb_table_arn" {
  description = "ARN của bảng DynamoDB lưu metadata"
  value       = aws_dynamodb_table.image_metadata.arn
}

output "dlq_queue_url" {
  description = "URL của Dead-Letter Queue (SQS) - Hàng đợi thông điệp lỗi"
  value       = aws_sqs_queue.dlq.id
}

output "dlq_queue_arn" {
  description = "ARN của Dead-Letter Queue (SQS)"
  value       = aws_sqs_queue.dlq.arn
}

output "lambda_function_name" {
  description = "Tên hàm AWS Lambda xử lý ảnh"
  value       = aws_lambda_function.image_processor.function_name
}

output "lambda_function_arn" {
  description = "ARN của hàm AWS Lambda xử lý ảnh"
  value       = aws_lambda_function.image_processor.arn
}

output "lambda_execution_role_arn" {
  description = "ARN của IAM Role thực thi của Lambda (Tuân thủ Least Privilege)"
  value       = aws_iam_role.lambda_exec.arn
}

output "environment_variables_contract" {
  description = "Bản đồ biến môi trường bàn giao cho Kỹ sư Phần mềm & SRE"
  value = {
    ENVIRONMENT      = var.environment
    INPUT_BUCKET     = aws_s3_bucket.input.id
    OUTPUT_BUCKET    = aws_s3_bucket.output.id
    METADATA_TABLE   = aws_dynamodb_table.image_metadata.name
    DLQ_URL          = aws_sqs_queue.dlq.id
    MAX_RETRY_COUNT  = tostring(var.dlq_max_receive_count)
    TARGET_WIDTH     = tostring(var.thumbnail_width)
    TARGET_HEIGHT    = tostring(var.thumbnail_height)
    THUMBNAIL_WIDTH  = tostring(var.thumbnail_width)
    THUMBNAIL_HEIGHT = tostring(var.thumbnail_height)
    LOG_LEVEL        = var.log_level
  }
}
