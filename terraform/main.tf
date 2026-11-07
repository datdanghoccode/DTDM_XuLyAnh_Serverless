# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/main.tf
# ==============================================================================
#
# Kiến trúc hạ tầng Event-Driven Serverless gồm các thành phần cốt lõi:
# 1. Object Storage (S3):
#    - Input Bucket: Tiếp nhận ảnh người dùng tải lên, kích hoạt sự kiện s3:ObjectCreated.
#    - Output Bucket: Lưu trữ ảnh thu nhỏ (thumbnail) sau xử lý.
# 2. Serverless Compute (AWS Lambda):
#    - Xử lý ảnh (resize thumbnail), trích xuất metadata, tính hash SHA-256.
# 3. Metadata & Idempotency Store (DynamoDB):
#    - Bảng metadata lưu trữ trạng thái xử lý ảnh, đóng vai trò kiểm tra tính Idempotent.
# 4. Dead-Letter Queue (SQS):
#    - Lưu trữ các sự kiện lỗi không thể phục hồi (file hỏng, timeout, logic exception).
# 5. Security & Identity (IAM Least Privilege):
#    - Cấp quyền tối thiểu độc lập cho từng thành phần, tuyệt đối không dùng secret hardcode.
#
# Các tài nguyên được phân bổ thành các tệp cấu hình chi tiết:
# - s3.tf: Cấu hình Input/Output Bucket, mã hóa AES-256, Public Access Block, S3 Trigger.
# - sqs.tf: Cấu hình Dead-Letter Queue (DLQ), thời gian lưu trữ tin nhắn 14 ngày.
# - dynamodb.tf: Cấu hình bảng metadata lưu trữ trạng thái theo mô hình Pay-Per-Request (On-demand).
# - iam.tf: Thiết lập IAM Role và Policy theo nguyên tắc Least Privilege (Quyền hạn tối thiểu).
# - lambda.tf: Cấu hình hàm Lambda, tài nguyên bộ nhớ, timeout, biến môi trường và kết nối DLQ.
# - outputs.tf: Xuất các định danh tài nguyên bàn giao cho Software Engineer và SRE.
# ==============================================================================

# Lấy thông tin tài khoản AWS hiện tại
data "aws_caller_identity" "current" {}

# Lấy thông tin Region hiện tại
data "aws_region" "current" {}

# Tạo chuỗi ngẫu nhiên giúp tên S3 Bucket không bị trùng lặp trên toàn cầu (Global Uniqueness)
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}
