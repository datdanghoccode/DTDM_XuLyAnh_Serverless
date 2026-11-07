# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/dynamodb.tf
# ==============================================================================

# ------------------------------------------------------------------------------
# DYNAMODB TABLE - KHO LƯU TRỮ METADATA VÀ TRẠNG THÁI IDEMPOTENCY
#
# Bảng này giải quyết trực tiếp 2 mục tiêu đề tài:
# 1. Tính Idempotent: Khóa chính image_id (mã hash SHA-256 của nội dung ảnh).
#    Khi nhận sự kiện trùng lặp, Lambda kiểm tra image_id trong bảng. Nếu đã tồn
#    tại và có trạng thái "COMPLETED", hàm sẽ bỏ qua xử lý để không tạo bản ghi trùng.
# 2. Kiểm soát chi phí theo nhịp tải không đều: Sử dụng PAY_PER_REQUEST (On-Demand),
#    hệ thống chỉ tính phí trên số lượt đọc/ghi thực tế phát sinh, chi phí = 0 khi nhàn rỗi.
# ------------------------------------------------------------------------------
resource "aws_dynamodb_table" "image_metadata" {
  name         = "${var.project_name}-metadata-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "image_hash"

  # Khóa chính: image_hash (Mã hash SHA-256 của nội dung ảnh, đồng bộ với src/lambda_function.py)
  attribute {
    name = "image_hash"
    type = "S"
  }

  # Thuộc tính tên file gốc
  attribute {
    name = "file_name"
    type = "S"
  }

  # Thuộc tính mốc thời gian hoàn thành xử lý (Unix Timestamp - Number)
  attribute {
    name = "processed_at"
    type = "N"
  }

  # Global Secondary Index (GSI): Hỗ trợ truy vấn báo cáo theo tên file và thời gian xử lý
  global_secondary_index {
    name            = "FileNameIndex"
    hash_key        = "file_name"
    range_key       = "processed_at"
    projection_type = "ALL"
  }

  # Bật mã hóa bảo vệ dữ liệu ở trạng thái nghỉ (At-Rest Encryption)
  server_side_encryption {
    enabled = true
  }

  # Bật tính năng khôi phục theo thời điểm (Point-in-Time Recovery)
  point_in_time_recovery {
    enabled = true
  }

  # Bật Time-To-Live (TTL) để tự động dọn dẹp các bản ghi tạm/hết hạn nếu cần
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "${var.project_name}-metadata"
    Role        = "Metadata & Idempotency Store"
    Description = "Luu tru metadata anh va dam bao tinh Idempotent cua he thong"
  }
}
