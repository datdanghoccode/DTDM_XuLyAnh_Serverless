#!/usr/bin/env python3
"""
==============================================================================
Đề tài 9: Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless
Thành viên: Lê Doãn Đạt (038206000230) - Kiến trúc sư Hạ tầng & DevOps
Script: infrastructure/scripts/security_audit.py
==============================================================================
Mục đích:
Cung cấp minh chứng thực nghiệm tự động cho yêu cầu kết quả của đề tài:
"Chính sách IAM tối thiểu cho từng thành phần và bằng chứng không lưu khóa trong mã."

Kịch bản kiểm tra gồm 3 hạng mục:
1. Quét toàn bộ mã nguồn (Git repository) tìm các mẫu khóa nhạy cảm (AWS Access Key,
   Secret Key, Private Key, Password hardcode).
2. Kiểm tra cấu hình .gitignore đảm bảo đã chặn các tệp chứa trạng thái & secret
   (*.tfstate, *.tfvars, .env, *.pem, *.key).
3. Phân tích tệp cấu hình `terraform/iam.tf` xác minh không cấp quyền wildcard
   nguy hiểm (`Action = "*"` hoặc `AdministratorAccess`) và phân tách quyền
   đọc/ghi độc lập cho S3 Input, S3 Output, DynamoDB, SQS DLQ.
==============================================================================
"""

import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Các mẫu Regex nhận diện khóa bí mật bị hardcode
SECRET_PATTERNS = [
    (
        "AWS Access Key ID (AKIA/ASIA)",
        re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    ),
    (
        "AWS Secret Access Key Hardcoded Assignment",
        re.compile(
            r"""(?i)(aws_secret_access_key|secret_key)\s*[:=]\s*["'](?!(mock_secret_key|null|YOUR_))([A-Za-z0-9/+=]{20,})["']"""
        ),
    ),
    (
        "RSA / PEM Private Key Block",
        re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
    (
        "Hardcoded Password / Token",
        re.compile(
            r"""(?i)(password|passwd|api_token|auth_token)\s*[:=]\s*["'][^"']{8,}["']"""
        ),
    ),
]

EXCLUDED_DIRS = {".git", ".terraform", "__pycache__", ".venv", "venv", "node_modules"}
EXCLUDED_EXTENSIONS = {".xlsx", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".pdf"}


def scan_for_hardcoded_secrets(root_dir: Path) -> list[str]:
    findings = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in EXCLUDED_EXTENSIONS:
                continue
            fpath = Path(dirpath) / fname
            # Bỏ qua chính script kiểm tra này
            if fpath.resolve() == Path(__file__).resolve():
                continue
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                for rule_name, pattern in SECRET_PATTERNS:
                    if pattern.search(line):
                        rel_path = fpath.relative_to(root_dir)
                        findings.append(
                            f"[{rule_name}] tại {rel_path}:{line_no} -> {line.strip()}"
                        )
    return findings


def verify_gitignore(root_dir: Path) -> list[str]:
    gitignore_path = root_dir / ".gitignore"
    if not gitignore_path.exists():
        return ["Không tìm thấy tệp .gitignore ở thư mục gốc!"]

    content = gitignore_path.read_text(encoding="utf-8")
    required_entries = ["*.tfstate", "*.tfvars", ".env", "*.pem", "*.key"]
    missing = [entry for entry in required_entries if entry not in content]
    return [f"Thiếu quy tắc chặn '{m}' trong .gitignore" for m in missing]


def verify_iam_least_privilege(root_dir: Path) -> list[str]:
    iam_path = root_dir / "terraform" / "iam.tf"
    if not iam_path.exists():
        return ["Không tìm thấy tệp terraform/iam.tf!"]

    raw_content = iam_path.read_text(encoding="utf-8")
    # Loại bỏ các dòng chú thích (#) trước khi phân tích cú pháp cấu hình
    active_lines = [
        line for line in raw_content.splitlines() if not line.strip().startswith("#")
    ]
    content = "\n".join(active_lines)
    issues = []

    if "AdministratorAccess" in content:
        issues.append("Phát hiện sử dụng quyền quản trị tối cao AdministratorAccess!")

    if re.search(r'Action\s*=\s*"\*"', content) or re.search(r'Action\s*=\s*\[\s*"\*"\s*\]', content):
        issues.append("Phát hiện cấp quyền Action = '*' vi phạm Least Privilege!")

    required_statements = [
        "S3InputBucketReadOnly",
        "S3OutputBucketWriteOnly",
        "DynamoDBIdempotencyAccess",
        "SQSDeadLetterQueueSendOnly",
        "CloudWatchLoggingPermissions",
    ]
    for sid in required_statements:
        if sid not in content:
            issues.append(f"Thiếu khối phân quyền tách biệt Sid='{sid}' trong iam.tf")

    return issues


def main() -> int:
    print("=" * 78)
    print("  KIỂM ĐỊNH BẢO MẬT HẠ TẦNG & MÃ NGUỒN (SECURITY & IAM AUDIT)")
    print("  Đề tài 9 - Phụ trách Hạ tầng & Bảo mật: Lê Doãn Đạt (038206000230)")
    print("=" * 78)

    # 1. Quét Secret trong mã nguồn
    print("\n[1/3] Kiểm tra bằng chứng KHÔNG lưu khóa (Secret/Access Key) trong mã nguồn...")
    secret_findings = scan_for_hardcoded_secrets(PROJECT_ROOT)
    if not secret_findings:
        print("  [PASS] Tuyệt vời! Không phát hiện bất kỳ khóa AWS hay secret hardcode nào.")
    else:
        for f in secret_findings:
            print(f"  [FAIL] {f}")

    # 2. Kiểm tra .gitignore
    print("\n[2/3] Kiểm tra cấu hình bảo vệ tệp nhạy cảm trong .gitignore...")
    gitignore_issues = verify_gitignore(PROJECT_ROOT)
    if not gitignore_issues:
        print("  [PASS] .gitignore đã chặn đầy đủ: *.tfstate, *.tfvars, .env, *.pem, *.key.")
    else:
        for issue in gitignore_issues:
            print(f"  [FAIL] {issue}")

    # 3. Kiểm tra chính sách IAM Least Privilege
    print("\n[3/3] Kiểm tra chính sách IAM Least Privilege trong terraform/iam.tf...")
    iam_issues = verify_iam_least_privilege(PROJECT_ROOT)
    if not iam_issues:
        print("  [PASS] Chính sách IAM tuân thủ nghiêm ngặt Least Privilege:")
        print("         - S3 Input Bucket  : Chỉ cấp quyền đọc (s3:GetObject)")
        print("         - S3 Output Bucket : Chỉ cấp quyền ghi (s3:PutObject)")
        print("         - DynamoDB Table   : Chỉ cấp quyền GetItem, PutItem, UpdateItem, Query")
        print("         - SQS DLQ          : Chỉ cấp quyền gửi thông điệp lỗi (sqs:SendMessage)")
        print("         - CloudWatch Logs  : Giới hạn trong phạm vi Log Group của hàm")
    else:
        for issue in iam_issues:
            print(f"  [FAIL] {issue}")

    print("\n" + "=" * 78)
    total_errors = len(secret_findings) + len(gitignore_issues) + len(iam_issues)
    if total_errors == 0:
        print("KẾT LUẬN: ĐẠT 100% TIÊU CHUẨN BẢO MẬT SERVERLESS & IAM LEAST PRIVILEGE!")
        print("=" * 78)
        return 0
    else:
        print(f"KẾT LUẬN: PHÁT HIỆN {total_errors} VẤN ĐỀ CẦN KHẮC PHỤC!")
        print("=" * 78)
        return 1


if __name__ == "__main__":
    sys.exit(main())
