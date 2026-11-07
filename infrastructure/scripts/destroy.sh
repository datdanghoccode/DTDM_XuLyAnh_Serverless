#!/usr/bin/env bash
# ==============================================================================
# Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
# Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
# Script: destroy.sh
# Mục đích: Hủy bỏ toàn bộ tài nguyên (trên AWS hoặc LocalStack) để tránh phát sinh chi phí
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TERRAFORM_DIR="${PROJECT_ROOT}/terraform"

echo "=============================================================================="
echo "  DỌN DẸP / HỦY TÀI NGUYÊN HẠ TẦNG (SERVERLESS PIPELINE - ĐỀ TÀI 9)           "
echo "  Thành viên: Lê Doãn Đạt (038206000230) - DevOps & Infrastructure Architect "
echo "=============================================================================="

echo "Chọn môi trường muốn dọn dẹp:"
echo "  1) LocalStack (Docker)"
echo "  2) AWS Cloud thật"
read -p "Nhập lựa chọn [1 hoặc 2]: " -r CHOICE

cd "${TERRAFORM_DIR}"

if [ "${CHOICE}" == "1" ]; then
    echo "[+] Đang hủy tài nguyên trên LocalStack..."
    terraform destroy -var="use_localstack=true" -auto-approve || true
    echo "[+] Đang dừng LocalStack Docker Container..."
    cd "${PROJECT_ROOT}"
    docker compose down -v || true
    echo "[+] Đã dọn dẹp sạch sẽ môi trường LocalStack!"
elif [ "${CHOICE}" == "2" ]; then
    read -p "CẢNH BÁO: Thao tác này sẽ xóa vĩnh viễn các bucket, bảng DynamoDB và Lambda trên AWS! Tiếp tục? (y/N): " -r AWS_CONFIRM
    if [[ "${AWS_CONFIRM}" =~ ^[Yy]$ ]]; then
        echo "[+] Đang hủy tài nguyên trên AWS Cloud..."
        terraform destroy -var="use_localstack=false" -auto-approve
        echo "[+] Đã hủy toàn bộ tài nguyên trên AWS Cloud thành công!"
    else
        echo "[-] Đã hủy lệnh."
    fi
else
    echo "[-] Lựa chọn không hợp lệ."
fi
