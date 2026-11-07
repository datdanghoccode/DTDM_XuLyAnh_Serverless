#!/usr/bin/env bash
# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# Script: deploy_local.sh
# Mục đích: Tự động khởi chạy LocalStack và triển khai hạ tầng bằng Terraform
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"

echo "=============================================================================="
echo "  KHỞI TẠO HẠ TẦNG LOCALSTACK (SERVERLESS PIPELINE - ĐỀ TÀI 9)               "
echo "  Thành viên: Lê Doãn Đạt (038206000230) - DevOps & Infrastructure Architect "
echo "=============================================================================="

# 1. Kiểm tra Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo "[-] Lỗi: Máy tính chưa cài đặt Docker. Vui lòng cài Docker để chạy LocalStack."
    exit 1
fi

# 2. Khởi động LocalStack Container
echo "[+] Đang khởi động LocalStack qua Docker Compose..."
cd "${PROJECT_ROOT}"
docker compose up -d

# 3. Chờ LocalStack sẵn sàng
echo "[*] Đang chờ dịch vụ LocalStack sẵn sàng trên cổng 4566..."
MAX_ATTEMPTS=30
ATTEMPT=0
until curl -s http://localhost:4566/_localstack/health | grep -q '"s3": "available"\|"s3": "running"' || [ $ATTEMPT -ge $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    echo "    Đang đợi LocalStack khởi động... (Lần thử: $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 2
done

if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
    echo "[-] Cảnh báo: LocalStack chưa phản hồi đầy đủ trạng thái, tiếp tục thử áp dụng Terraform..."
else
    echo "[+] LocalStack đã sẵn sàng hoạt động!"
fi

# 4. Áp dụng Terraform trên LocalStack
echo "[+] Khởi tạo và triển khai Terraform với use_localstack=true..."
cd "${TERRAFORM_DIR}"

terraform init

terraform apply \
  -var="use_localstack=true" \
  -var="localstack_endpoint=http://localhost:4566" \
  -var="environment=local" \
  -auto-approve

echo ""
echo "=============================================================================="
echo "[+] TRIỂN KHAI THÀNH CÔNG HẠ TẦNG LOCALSTACK!"
echo "Các thông số hạ tầng đã được cấu hình sẵn sàng cho nhóm thực hiện kiểm thử."
echo "=============================================================================="
