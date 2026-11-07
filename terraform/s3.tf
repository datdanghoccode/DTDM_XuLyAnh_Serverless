# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/s3.tf
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. INPUT BUCKET - Lưu trữ ảnh người dùng tải lên
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "input" {
  bucket        = "${var.project_name}-input-${var.environment}-${random_string.suffix.result}"
  force_destroy = true # Hỗ trợ dọn dẹp sạch tài nguyên khi chạy destroy trong bài tập lớn

  tags = {
    Name        = "${var.project_name}-input"
    Role        = "Object Storage - Ingestion"
    Description = "Bucket tiep nhan anh goc tu client de kich hoat pipeline"
  }
}

# ------------------------------------------------------------------------------
# 2. OUTPUT BUCKET - Lưu trữ thumbnail và ảnh sau xử lý
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "output" {
  bucket        = "${var.project_name}-output-${var.environment}-${random_string.suffix.result}"
  force_destroy = true

  tags = {
    Name        = "${var.project_name}-output"
    Role        = "Object Storage - Processed Images"
    Description = "Bucket luu tru anh thumbnail sau khi Lambda xu ly thanh cong"
  }
}

# ------------------------------------------------------------------------------
# 3. BẢO MẬT: Chặn toàn bộ truy cập công khai (S3 Block Public Access)
# Tuân thủ nguyên tắc an toàn dữ liệu, chống rò rỉ dữ liệu lưu trữ
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_public_access_block" "input" {
  bucket = aws_s3_bucket.input.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "output" {
  bucket = aws_s3_bucket.output.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------------------------------------------------------
# 4. MÃ HÓA DỮ LIỆU: Bật Server-Side Encryption (AES-256) mặc định
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_server_side_encryption_configuration" "input" {
  bucket = aws_s3_bucket.input.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "output" {
  bucket = aws_s3_bucket.output.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ------------------------------------------------------------------------------
# 5. QUẢN LÝ PHIÊN BẢN (Versioning)
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_versioning" "input" {
  bucket = aws_s3_bucket.input.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "output" {
  bucket = aws_s3_bucket.output.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ------------------------------------------------------------------------------
# 6. S3 TRIGGER: Cấp quyền cho S3 gọi hàm Lambda
# ------------------------------------------------------------------------------
resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.image_processor.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input.arn
}

# ------------------------------------------------------------------------------
# 7. S3 EVENT NOTIFICATION: Kích hoạt Lambda khi có sự kiện s3:ObjectCreated:*
# Tự động gửi thông báo sự kiện để bắt đầu pipeline xử lý ảnh
# ------------------------------------------------------------------------------
resource "aws_s3_bucket_notification" "input_notification" {
  bucket = aws_s3_bucket.input.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.image_processor.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
