#!/usr/bin/env bash
# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# Script: deploy_aws.sh
# Mục đích: Triển khai toàn bộ hạ tầng lên môi trường AWS Cloud thật
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"

echo "=============================================================================="
echo "  TRIỂN KHAI HẠ TẦNG LÊN AWS CLOUD (SERVERLESS PIPELINE - ĐỀ TÀI 9)           "
echo "  Thành viên: Lê Doãn Đạt (038206000230) - DevOps & Infrastructure Architect "
echo "=============================================================================="

# 1. Kiểm tra AWS CLI / Credentials
if ! command -v aws &> /dev/null; then
    echo "[!] Cảnh báo: Lệnh aws chưa được cài đặt, nhưng Terraform vẫn có thể dùng AWS_ACCESS_KEY_ID."
fi

# 2. Khởi tạo và áp dụng Terraform
cd "${TERRAFORM_DIR}"

echo "[+] Đang khởi tạo Terraform..."
terraform init

echo "[+] Đang kiểm tra kế hoạch triển khai (terraform plan)..."
terraform plan -var="use_localstack=false"

read -p "Bạn có chắc chắn muốn triển khai các tài nguyên trên lên AWS thật? (y/N): " -r CONFIRM
if [[ "${CONFIRM}" =~ ^[Yy]$ ]]; then
    echo "[+] Đang áp dụng hạ tầng lên AWS..."
    terraform apply -var="use_localstack=false" -auto-approve
    echo ""
    echo "[+] Triển khai thành công! Thông tin tài nguyên:"
    terraform output
else
    echo "[-] Đã hủy thao tác triển khai."
fi
