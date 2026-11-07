# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/lambda.tf
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. ĐÓNG GÓI MÃ NGUỒN LAMBDA (Archive File)
# Tự động phát hiện mã nguồn:
# - Nếu bạn Trần Ngọc Lâm đã hoàn thành src/lambda_function.py, Terraform sẽ dùng file này.
# - Nếu chưa, Terraform sử dụng bootstrap handler mẫu để khởi tạo hạ tầng thành công.
# ------------------------------------------------------------------------------
data "archive_file" "lambda_payload" {
  type        = "zip"
  output_path = "${path.module}/build/lambda_package.zip"

  source {
    content  = fileexists("${path.module}/../src/lambda_function.py") ? file("${path.module}/../src/lambda_function.py") : file("${path.module}/../infrastructure/bootstrap/lambda_bootstrap.py")
    filename = "lambda_function.py"
  }
}

# ------------------------------------------------------------------------------
# 2. CLOUDWATCH LOG GROUP CHO LAMBDA
# Thiết lập thời gian lưu trữ 14 ngày để quản lý chi phí log tối ưu
# ------------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "lambda_log" {
  name              = "/aws/lambda/${var.project_name}-processor-${var.environment}"
  retention_in_days = 14

  tags = {
    Name = "${var.project_name}-lambda-logs"
    Role = "Observability - Centralized Logging"
  }
}

# ------------------------------------------------------------------------------
# 3. AWS LAMBDA FUNCTION - TRÁI TIM CỦA PIPELINE XỬ LÝ ẢNH
# Cấu hình đầy đủ:
# - Cấu hình Memory & Timeout có thể điều chỉnh để phục vụ thực nghiệm Cold Start
# - Cấu hình Dead-Letter Queue (SQS) bảo vệ khi xử lý file hỏng hoặc timeout
# - Cấu hình Biến môi trường chuẩn, không hardcode credentials
# ------------------------------------------------------------------------------
resource "aws_lambda_function" "image_processor" {
  function_name    = "${var.project_name}-processor-${var.environment}"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = var.lambda_runtime
  filename         = data.archive_file.lambda_payload.output_path
  source_code_hash = data.archive_file.lambda_payload.output_base64sha256

  # Tham số cấu hình phục vụ thực nghiệm đo Cold Start và Đánh đổi Hiệu năng - Chi phí
  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout

  # Cấu hình Hàng đợi thông điệp lỗi (Dead-Letter Config)
  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  # Bật AWS X-Ray Tracing để đo đạc độ trễ và cold start chi tiết
  tracing_config {
    mode = "Active"
  }

  # Quản lý cấu hình qua Biến môi trường (Tuyệt đối không lưu Access Key / Secret)
  environment {
    variables = {
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

  depends_on = [
    aws_iam_role_policy_attachment.lambda_least_privilege_attach,
    aws_cloudwatch_log_group.lambda_log
  ]

  tags = {
    Name       = "${var.project_name}-processor"
    Role       = "Serverless Compute - Image Resizing & Idempotency"
    MemoryMB   = tostring(var.lambda_memory_size)
    TimeoutSec = tostring(var.lambda_timeout)
  }
}
