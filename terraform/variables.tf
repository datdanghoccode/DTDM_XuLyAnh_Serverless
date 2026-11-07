# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/variables.tf
# ==============================================================================

variable "aws_region" {
  description = "AWS Region triển khai hạ tầng (mặc định chọn Singapore ap-southeast-1 để tối ưu độ trễ)"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Môi trường triển khai (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Tên định danh dự án dùng làm tiền tố tài nguyên"
  type        = string
  default     = "dtdm-image-processor"
}

# ------------------------------------------------------------------------------
# Cấu hình Môi trường LocalStack
# ------------------------------------------------------------------------------
variable "use_localstack" {
  description = "Bật/Tắt chế độ chạy trên LocalStack giả lập AWS (true: chạy local không mất phí; false: chạy AWS Cloud thật)"
  type        = bool
  default     = false
}

variable "localstack_endpoint" {
  description = "Endpoint của LocalStack chạy trên Docker"
  type        = string
  default     = "http://localhost:4566"
}

# ------------------------------------------------------------------------------
# Cấu hình Hàm Serverless Compute (AWS Lambda)
# ------------------------------------------------------------------------------
variable "lambda_memory_size" {
  description = "Dung lượng RAM (MB) cấp cho Lambda function. Phục vụ thực nghiệm đo lường Cold/Warm Start & Chi phí (128, 256, 512, 1024, 2048)"
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Thời gian timeout tối đa cho một lượt thực thi của Lambda (giây)"
  type        = number
  default     = 30
}

variable "lambda_runtime" {
  description = "Runtime môi trường thực thi của hàm"
  type        = string
  default     = "python3.11"
}

variable "log_level" {
  description = "Mức độ ghi log trong CloudWatch (DEBUG, INFO, WARNING, ERROR)"
  type        = string
  default     = "INFO"
}

# ------------------------------------------------------------------------------
# Cấu hình Tham số Nghiệp vụ Xử lý ảnh & Idempotency
# ------------------------------------------------------------------------------
variable "thumbnail_width" {
  description = "Chiều rộng ảnh thumbnail tạo bởi hàm (pixel)"
  type        = number
  default     = 200
}

variable "thumbnail_height" {
  description = "Chiều cao ảnh thumbnail tạo bởi hàm (pixel)"
  type        = number
  default     = 200
}

# ------------------------------------------------------------------------------
# Cấu hình Hàng đợi lỗi (Dead-Letter Queue - SQS) & Retry
# ------------------------------------------------------------------------------
variable "dlq_max_receive_count" {
  description = "Số lần retry tối đa trước khi đưa thông điệp lỗi vào Dead-Letter Queue (DLQ)"
  type        = number
  default     = 3
}

variable "dlq_message_retention_seconds" {
  description = "Thời gian lưu trữ thông điệp trong DLQ (giây). Mặc định 14 ngày (1209600s) cho SRE phân tích và replay"
  type        = number
  default     = 1209600
}
