# BỘ SẢN PHẨM HOÀN CHỈNH - ĐỀ TÀI 9
## HỌC PHẦN: ĐIỆN TOÁN ĐÁM MÂY - TRƯỜNG ĐH GIAO THÔNG VẬN TẢI TP.HCM (UTH)
* **Đề tài số 9:** Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless và đánh giá Cold Start
* **Giảng viên hướng dẫn:** TS. Lê Quốc Tuấn
* **Nhóm sinh viên thực hiện (Lớp 012012303904):**
  1. **Lê Doãn Đạt** - MSSV: `038206000230` (Người 1: Giới thiệu, Câu hỏi nghiên cứu, Lý thuyết FaaS & Bảo mật OWASP)
  2. **Trần Ngọc Lâm** - MSSV: `034206001749` (Người 2: Thiết kế Pipeline đầu-cuối, Khóa lũy đẳng DynamoDB & SQS DLQ)
  3. **Vũ Thành Đạt** - MSSV: `001206040720` (Người 3: Thực nghiệm 100 runs, Cold/Warm, Chi phí 3 mức tải & SRE Runbook)

---

### BẢNG ĐỐI CHIẾU 100% YÊU CẦU ĐỀ CƯƠNG & SLIDE BÁO CÁO (TS. LÊ QUỐC TUẤN)

| Hạng mục đề tài | Nội dung chi tiết trong đề cương | Minh chứng & Slide trình bày | Người phụ trách |
| :--- | :--- | :--- | :---: |
| **Câu hỏi nghiên cứu** | *Khi tệp được tải lên theo các nhịp không đều, kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?* | **Slide 3 & Slide 13**: Phân tích Spike load, cơ chế SQS Buffer, Lambda Scale-to-Zero, Khóa lũy đẳng DynamoDB và mô hình Pay-as-you-go ($0.045/100k ảnh). | **Lê Doãn Đạt** & Cả nhóm |
| **Mục tiêu 1** | Thiết kế chuỗi sự kiện từ lưu trữ đối tượng đến hàm xử lý và kho metadata. | **Slide 6 (Hình 1)**: S3 Input -> SQS Event Queue -> AWS Lambda (Pillow) -> S3 Thumbnails & DynamoDB ImageMetadata. | **Trần Ngọc Lâm** |
| **Mục tiêu 2** | Đảm bảo hàm có tính idempotent, xử lý được retry và đưa lỗi không phục hồi vào dead-letter queue. | **Slide 7 (Hình 2) & Slide 8**: DynamoDB `attribute_not_exists(image_hash)`, chặn lặp trong 2.1 ms; SQS DLQ cô lập sau 3 lần retry. | **Trần Ngọc Lâm** |
| **Mục tiêu 3** | Đo cold start, độ trễ đầu cuối và chi phí theo số lượng sự kiện. | **Slide 9 (Hình 4) & Slide 10 (Hình 3)**: Đo 100 lần gọi, $p_{50}=30.3\text{ms}$, $p_{95}=289.5\text{ms}$; Ước tính chi phí 3 mức tải ($0.004, $0.045, $0.452). | **Vũ Thành Đạt** |
| **Lý thuyết 1** | FaaS, event source, trigger, stateless execution, timeout, concurrency và at-least-once delivery. | **Slide 4**: Mô hình FaaS, S3 event trigger, Lambda stateless execution, timeout 30s, quản lý concurrency và xử lý mạng at-least-once. | **Lê Doãn Đạt** |
| **Lý thuyết 2** | Idempotency, retry with backoff, dead-letter queue và eventual consistency. | **Slide 4, Slide 7 & Slide 8**: Thuật toán lũy đẳng, thử lại lùi số mũ (exponential backoff), SQS DLQ 14 ngày, tính nhất quán cuối cùng. | **Lê Doãn Đạt** & **Trần Ngọc Lâm** |
| **Lý thuyết 3** | Cold start, warm invocation, package size và provisioned concurrency. | **Slide 4 & Slide 10**: Vòng đời container Firecracker, InitDuration (nạp Pillow 520ms), Warm execution (27ms), package size và tối ưu RAM. | **Lê Doãn Đạt** & **Vũ Thành Đạt** |
| **Lý thuyết 4** | Rủi ro bảo mật serverless: quyền quá rộng, injection qua sự kiện, secret và dữ liệu tạm. | **Slide 5**: Chuẩn OWASP Serverless Top 10 (Least Privilege IAM, Pillow Image.verify chống injection, STS token không hardcode secret, RAM io.BytesIO không rò rỉ /tmp). | **Lê Doãn Đạt** |
| **Thực nghiệm 1** | Tải ảnh vào object storage; sự kiện kích hoạt hàm tạo thumbnail, trích metadata và ghi trạng thái. | **Slide 6, Slide 9 & Live Demo Ca 1**: Tải ảnh 1080p -> Lambda nạp vào RAM -> resize 300x300 (giảm 89.6% size) -> ghi DynamoDB `PROCESSED`. | **Trần Ngọc Lâm** & **Vũ Thành Đạt** |
| **Thực nghiệm 2** | Gửi lặp cùng một sự kiện, tạo tệp lỗi và gây timeout để quan sát retry, trùng lặp và dead letter queue. | **Slide 7, Slide 11 & Live Demo Ca 2, 3**: Gửi lặp ảnh -> Khóa nguyên tử chặn trong 2.1 ms; Tệp hỏng/timeout -> Retry 3 lần -> chuyển vào SQS DLQ. | **Trần Ngọc Lâm** & **Vũ Thành Đạt** |
| **Thực nghiệm 3** | Đo ít nhất 100 lần gọi gồm cold và warm; phân tích p50, p95, tỷ lệ lỗi và thời gian hoàn thành. | **Slide 9 (Hình 4) & Live Demo Ca 4**: 100 invocations thô trong `benchmark_100_runs.csv`; $p_{50}=30.3\text{ms}$, $p_{95}=289.5\text{ms}$, 0% lỗi. | **Vũ Thành Đạt** |
| **Thực nghiệm 4** | Thay đổi memory/package size hoặc concurrency và đánh giá ảnh hưởng đến hiệu năng - chi phí. | **Slide 10 (Hình 3)**: Khảo sát 128MB đến 2048MB RAM; phân tích điểm ngọt **Sweet Spot 512MB RAM** (27ms, $0.021/100k req). | **Vũ Thành Đạt** |
| **Minh chứng 1** | Pipeline serverless hoạt động đầu cuối và không tạo bản ghi trùng khi nhận lại sự kiện. | **Slide 6, 7 & Web UI Flask**: Kiểm chứng thực tế không tạo bản ghi trùng lặp trong cơ sở dữ liệu DynamoDB. | **Trần Ngọc Lâm** |
| **Minh chứng 2** | Bảng phân phối độ trễ cold/warm, throughput, lỗi và ước tính chi phí cho ba mức tải. | **Slide 9 (Hình 4) & Báo cáo Word Ch.4**: Đồ thị phân phối độ trễ và cột chi phí 3 mức tải ($0.004, $0.045, $0.452). | **Vũ Thành Đạt** |
| **Minh chứng 3** | Chính sách IAM tối thiểu cho từng thành phần và bằng chứng không lưu khóa trong mã. | **Slide 5, Slide 8 & `terraform/iam.tf`**: 6 Statement IAM độc lập; script audit xác nhận 100% zero hardcoded secret. | **Lê Doãn Đạt** & **Trần Ngọc Lâm** |
| **Minh chứng 4** | Kịch bản kiểm thử lỗi, dashboard và runbook xử lý thông điệp trong hàng đợi lỗi. | **Slide 11, Slide 12 & `RUNBOOK_DLQ.md`**: Dashboard CloudWatch/Web; SOP Runbook 3 bước: Cảnh báo -> Điều tra RCA -> Redrive DLQ. | **Vũ Thành Đạt** |
| **Tài liệu tham khảo** | [20], [28], [34] và Bài giảng Chương 2. | **Slide 13 & Báo cáo Word (References)**: Kế thừa và trích dẫn chuẩn học thuật các công trình nghiên cứu FaaS quốc tế và bài giảng của Thầy Tuấn. | Cả 3 thành viên |
| **Công nghệ gợi ý** | AWS Lambda/S3/SQS, LocalStack, Python Pillow, OpenTelemetry. | **Toàn bộ hệ thống**: AWS Lambda, S3, SQS, DynamoDB, LocalStack, Python Pillow, OpenTelemetry, Terraform IaC, Flask Dashboard. | Cả 3 thành viên |

---

### LIÊN KẾT TRÌNH CHIẾU CANVA CHÍNH THỨC (CHUẨN 13 SLIDE)
* **Link Canva trình chiếu trực tiếp (Presentation View):**  
  👉 [https://www.canva.com/d/3ddpe0glVMfu_hE](https://www.canva.com/d/3ddpe0glVMfu_hE) (hoặc [https://www.canva.com/d/VLuYFh4lFKbaNOJ](https://www.canva.com/d/VLuYFh4lFKbaNOJ))
* **Link Canva chỉnh sửa (Edit URL):**  
  👉 [https://www.canva.com/d/Nf8vdG86UbwncDw](https://www.canva.com/d/Nf8vdG86UbwncDw) (hoặc [https://www.canva.com/d/I6_zU7X9_krsa3H](https://www.canva.com/d/I6_zU7X9_krsa3H))
* **Hướng dẫn chỉnh sửa trên Canva cá nhân (100% quyền):**  
  Khi mở link Canva bằng trình duyệt của bạn, nhấp vào menu **Tệp (File)** ở góc trên bên trái $\rightarrow$ chọn **Tạo bản sao (Make a copy)**. Bản thuyết trình sẽ lập tức được nhân bản vào tài khoản cá nhân của bạn với toàn quyền chỉnh sửa trực tiếp.
* **Tệp trình chiếu PowerPoint chuẩn 13 slide (Title 38pt, Content 28pt):**  
  - `SAN_PHAM_DE_TAI_9_FINAL/DTDM_ThuyetTrinh_DeTai9.pptx`
  - `SAN_PHAM_DE_TAI_9_FINAL/Canva_BaoCao_13Slide_DeTai9.pptx`
* **Tệp PDF chất lượng cao:**  
  - `SAN_PHAM_DE_TAI_9_FINAL/Canva_BaoCao_13Slide_DeTai9.pdf`

---

### DANH MỤC SẢN PHẨM BÀN GIAO TOÀN DIỆN
1. **`DTDM_BaoCao_TieuLuan_DeTai9.docx`**: Báo cáo tiểu luận học thuật chi tiết >10,000 từ, 4 chương, 25 bảng biểu chuẩn định dạng UTH.
2. **`DTDM_ThuyetTrinh_DeTai9.pptx` & `Canva_BaoCao_13Slide_DeTai9.pptx`**: Tệp slide trình chiếu 13 trang chuẩn Widescreen 16:9, Tiêu đề 38pt, Nội dung 28pt, tích hợp 4 hình ảnh/sơ đồ gốc.
3. **`KICH_BAN_THUYET_TRINH_VA_DEMO.md`**: Kịch bản nói chi tiết 10 phút (phân chia 3 thành viên theo từng giây), hướng dẫn 4 bước Live Demo và bộ câu hỏi phản biện chuyên sâu.
4. **`run_demo.bat`**: File thực thi 1-click khởi chạy Web Dashboard tương tác trên Windows.
5. **`demo_app.py`**: Web application Flask chạy tại `http://localhost:5000` với đầy đủ 4 kịch bản tương tác (Tải ảnh chuẩn, Chặn trùng lặp Idempotency, Bắt lỗi Poison Pill vào DLQ, Benchmark 100 lần gọi).
6. **`benchmark_100_runs.csv`**: Dữ liệu thực nghiệm 100 lần gọi đo đạc độ trễ InitDuration, Duration, BilledDuration, Memory, RequestID.
7. **Bộ 4 hình ảnh/biểu đồ gốc chính thức**:
   - `so_do_kien_truc_pipeline_end_to_end.jpg` (Hình 1 - Slide 6)
   - `luu_do_thuat_toan_idempotency_retry_dlq.jpg` (Hình 2 - Slide 7)
   - `bieu_do_phan_phoi_do_tre_va_chi_phi_3_muc_tai.png` (Hình 4 - Slide 9: p50=30.3ms, p95=289.5ms, chi phí 3 mức tải)
   - `bieu_do_cold_warm_va_tradeoff_ram.jpg` (Hình 3 - Slide 10: Khảo sát RAM & Sweet Spot 512MB)
8. **Mã nguồn hệ thống (`src/` & `terraform/`)**:
   - `src/lambda_function.py`: Mã nguồn xử lý ảnh, tính hash SHA-256, khóa nguyên tử DynamoDB, dọn dẹp RAM /tmp.
   - `terraform/`: Cấu hình hạ tầng dạng mã hoàn chỉnh (`main.tf`, `s3.tf`, `lambda.tf`, `dynamodb.tf`, `sqs.tf`, `iam.tf`).

---

### HƯỚNG DẪN KHỞI CHẠY LIVE DEMO (1-CLICK)
1. Nhấp đúp chuột vào file `run_demo.bat` (hoặc mở Terminal gõ lệnh: `python demo_app.py`).
2. Mở trình duyệt web truy cập địa chỉ: **`http://localhost:5000`**.
3. Thực hiện lần lượt 4 kịch bản biểu diễn trước Hội đồng:
   - **Kịch bản 1 (Ảnh chuẩn):** Chọn ảnh phong cảnh 1080p -> Bấm "Tải lên S3 & Kích hoạt Pipeline" -> Xem thumbnail 300x300 giảm ~90% dung lượng.
   - **Kịch bản 2 (Chặn trùng lặp):** Bấm gửi lại ảnh vừa tải -> Quan sát hệ thống kích hoạt khóa lũy đẳng nguyên tử `attribute_not_exists(image_hash)` từ chối xử lý trong **2.1 ms**.
   - **Kịch bản 3 (Bắt lỗi Poison Pill):** Tải file giả mạo hoặc tệp rác -> Quan sát hệ thống bắt lỗi `UnidentifiedImageError`, thử lại và tự động điều hướng an toàn vào **SQS Dead-Letter Queue**.
   - **Kịch bản 4 (Benchmark định lượng 100 lần gọi):** Bấm "Chạy Benchmark 100 lần gọi" -> Trực quan hóa đồ thị phân vị $p_{50}, p_{95}$ và xuất file CSV.
