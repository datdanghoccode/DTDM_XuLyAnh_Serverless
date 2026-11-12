# VẬN HÀNH SỰ CỐ & SỔ TAY XỬ LÝ DEAD-LETTER QUEUE (RUNBOOK)
**Hệ thống:** Serverless Image Processing Pipeline  
**Tài nguyên:** Amazon SQS Dead-Letter Queue (`cloud-image-serverless-dlq`)  
**Bộ môn:** Điện toán Đám mây - TS. Lê Quốc Tuấn  
**Mục đích:** Quy trình chuẩn cho đội ngũ vận hành (Cloud/DevOps Engineer) khi hệ thống phát sinh thông điệp trong hàng đợi lỗi.

---

## 1. Cơ chế kích hoạt cảnh báo (Alert Trigger)
- **Chỉ số giám sát:** CloudWatch Metric `ApproximateNumberOfMessagesVisible` trên Queue `cloud-image-serverless-dlq`.
- **Ngưỡng cảnh báo (Threshold):** `> 0` trong vòng 1 phút.
- **Kênh thông báo:** Amazon SNS $\rightarrow$ Gửi email / Slack cho đội ngũ trực vận hành (On-call).

---

## 2. Quy trình điều tra nguyên nhân gốc rễ (Root Cause Analysis - RCA)

```
[Phát hiện tin nhắn trong DLQ]
              │
              ▼
[Bước 1: Kiểm tra CloudWatch Logs] ──► Lọc cụm từ [FAULT_INJECTION] hoặc [FATAL]
              │
              ▼
[Bước 2: Xem nội dung tin nhắn SQS] ──► Xác định S3 Bucket, Object Key, Kích thước file
              │
              ▼
    Phân loại nguyên nhân:
    ├─ 1. Tệp hỏng/giả mạo định dạng (UnidentifiedImageError)
    ├─ 2. Hết thời gian chờ xử lý (Lambda Task Timeout > 30s)
    └─ 3. Lỗi vượt quá bộ nhớ (Out-Of-Memory / OOM)
```

### Bước 2.1: Truy vấn nội dung thông điệp trong DLQ
Chạy lệnh AWS CLI (hoặc thao tác trên AWS Management Console / LocalStack):
```bash
# 1. Xem số lượng thông điệp đang chờ trong hàng đợi lỗi
aws sqs get-queue-attributes \
    --queue-url http://localhost:4566/000000000000/cloud-image-serverless-dlq \
    --attribute-names ApproximateNumberOfMessagesVisible

# 2. Đọc payload của thông điệp bị lỗi (không xóa khỏi hàng đợi)
aws sqs receive-message \
    --queue-url http://localhost:4566/000000000000/cloud-image-serverless-dlq \
    --max-number-of-messages 1 \
    --visibility-timeout 30
```

---

## 3. Các kịch bản sự cố điển hình và hành động khắc phục

### Kịch bản 1: Khách hàng upload tệp hỏng hoặc mã độc giả danh file ảnh
- **Triệu chứng:** Log hiển thị `UnidentifiedImageError: cannot identify image file`.
- **Nguyên nhân:** Người dùng tải lên tệp `.txt`, `.exe` nhưng đổi đuôi thành `.jpg`.
- **Hành động xử lý:**
  1. Đây là hành vi vi phạm nghiệp vụ, KHÔNG được tái chạy (Re-drive).
  2. Ghi log cảnh báo an ninh bảo mật.
  3. Xóa thông điệp khỏi SQS DLQ:
     ```bash
     aws sqs delete-message \
         --queue-url [DLQ_URL] \
         --receipt-handle [RECEIPT_HANDLE_FROM_PREVIOUS_STEP]
     ```
  4. Gửi email thông báo cho người dùng yêu cầu upload lại ảnh đúng chuẩn JPEG/PNG.

### Kịch bản 2: Dung lượng ảnh quá lớn dẫn đến Lambda Timeout (> 30 giây)
- **Triệu chứng:** Log hiển thị `Task timed out after 30.00 seconds`.
- **Hành động xử lý:**
  1. Tăng cấu hình RAM của hàm Lambda từ `512 MB` lên `1024 MB` (giúp tăng CPU tương ứng để xử lý ảnh nhanh hơn gấp 2 lần).
  2. Tăng giá trị `timeout` lên `60 giây` trong tệp `main.tf`.
  3. Deploy bản vá lỗi hạ tầng qua Terraform: `terraform apply -auto-approve`.
  4. Thực hiện **Redrive** thông điệp từ DLQ về lại hàm Lambda:
     - Trên AWS Console: Vào SQS Queue $\rightarrow$ Nhấn **Start DLQ redrive** $\rightarrow$ Chọn **Redrive to source queue / trigger**.

---

## 4. Bằng chứng kiểm thử kịch bản lỗi phục vụ bảo vệ đồ án

| Mã kiểm thử | Loại lỗi mô phỏng | Phản ứng của hệ thống | Kết quả quan sát thực tế | Đánh giá |
|---|---|---|---|---|
| **TC-ERR-01** | Upload tệp `bad_file.jpg` chứa text giả mạo | Lambda bắt lỗi `UnidentifiedImageError`, ném Exception | Tin nhắn rơi vào SQS DLQ sau khi hết retry | **ĐẠT (PASS)** |
| **TC-ERR-02** | Upload lặp lại cùng 1 file ảnh hợp lệ | Module Idempotency phát hiện mã băm SHA-256 đã tồn tại | Bỏ qua xử lý trong 2.1 ms, không ghi trùng DB | **ĐẠT (PASS)** |
| **TC-ERR-03** | Khởi chạy sau thời gian nhàn rỗi (Idle 30p) | AWS Lambda cấp phát MicroVM mới (Cold Start) | Thời gian phản hồi tăng lên 502 ms (Init Duration xuất hiện) | **ĐẠT (PASS)** |
