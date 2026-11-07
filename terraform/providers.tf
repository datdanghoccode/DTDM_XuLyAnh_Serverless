# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# File: terraform/providers.tf
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

# ------------------------------------------------------------------------------
# AWS Provider Configuration
# Hỗ trợ linh hoạt cả AWS Cloud thật và LocalStack (cho môi trường kiểm thử/chấm bài)
# ------------------------------------------------------------------------------
provider "aws" {
  region = var.aws_region

  # Cấu hình bỏ qua xác thực credentials khi chạy với LocalStack
  skip_credentials_validation = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  skip_requesting_account_id  = var.use_localstack
  s3_use_path_style           = var.use_localstack

  # Khi dùng LocalStack, sử dụng mock credentials; khi dùng AWS thật, lấy từ env/profile
  access_key = var.use_localstack ? "mock_access_key" : null
  secret_key = var.use_localstack ? "mock_secret_key" : null

  # Cấu hình Endpoint chuyển hướng dịch vụ về LocalStack khi var.use_localstack = true
  dynamic "endpoints" {
    for_each = var.use_localstack ? [1] : []
    content {
      s3             = var.localstack_endpoint
      sqs            = var.localstack_endpoint
      dynamodb       = var.localstack_endpoint
      lambda         = var.localstack_endpoint
      iam            = var.localstack_endpoint
      cloudwatch     = var.localstack_endpoint
      cloudwatchlogs = var.localstack_endpoint
      sts            = var.localstack_endpoint
    }
  }

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Le Doan Dat (038206000230)"
      Course      = "Dien toan dam may - De tai 9"
    }
  }
}
