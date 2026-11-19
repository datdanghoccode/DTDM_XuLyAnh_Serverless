# BỘ SLIDE THUYẾT TRÌNH BÀI BÁO CÁO TOÀN DIỆN (28 SLIDES)
## HỌC PHẦN: ĐIỆN TOÁN ĐÁM MÂY — TRƯỜNG ĐH GIAO THÔNG VẬN TẢI TP.HCM (UTH)
### ĐỀ TÀI 9: XÂY DỰNG HỆ THỐNG XỬ LÝ ẢNH HƯỚNG SỰ KIỆN BẰNG SERVERLESS VÀ ĐÁNH GIÁ COLD START
* **Giảng viên hướng dẫn:** TS. Lê Quốc Tuấn
* **Nhóm sinh viên thực hiện (Lớp 012012303904):**
  1. **Lê Doãn Đạt** — MSSV: `038206000230` *(Người 1: Slide 1 - 15)*
  2. **Trần Ngọc Lâm** — MSSV: `034206001749` *(Người 2: Slide 16 - 20)*
  3. **Vũ Thành Đạt** — MSSV: `001206040720` *(Người 3: Slide 21 - 28)*

---

## 📑 BẢNG ÁNH XẠ 28 SLIDE THEO TIẾN TRÌNH THUYẾT TRÌNH

| Slide | Tiêu Đề Slide | Người Phụ Trách | Trọng Tâm Báo Cáo |
| :---: | :--- | :---: | :--- |
| **01** | Trang Tiêu Đề Chính & Thông Tin Nhóm | Lê Doãn Đạt | Giới thiệu tên đề tài, GVHD: TS. Lê Quốc Tuấn, 3 thành viên lớp 012012303904. |
| **02** | Mục Lục Tổng Thể 4 Chương Báo Cáo | Cả 3 Thành Viên | Khái quát 4 chương: FaaS, Hạ tầng Terraform, Pipeline Thuật toán, Thực nghiệm SRE. |
| **03** | Bối Cảnh Thực Tiễn & Thách Thức Lưu Lượng | Lê Doãn Đạt | Phân tích bài toán tải ảnh nhịp không đều (Bursty load) và hạn chế máy chủ EC2. |
| **04** | Câu Hỏi Nghiên Cứu & Mục Tiêu Đề Tài | Lê Doãn Đạt | Phát biểu trực diện câu hỏi nghiên cứu và 3 mục tiêu kỹ thuật cụ thể. |
| **05** | Mô Hình FaaS & Khả Năng Scale-to-Zero | Lê Doãn Đạt | Bản chất FaaS, tự động co về 0 (chi phí $0.00) và tính phí theo mili-giây. |
| **06** | So Sánh: Máy Chủ Truyền Thống vs Serverless | Lê Doãn Đạt | Bảng đối sánh 5 tiêu chí: Đơn vị triển khai, Khởi động, Chi phí, Tải rỗng, Quản trị. |
| **07** | Event Source, Trigger & Stateless Execution | Lê Doãn Đạt | S3 Event Source, Pull-based Trigger qua SQS, Nguyên lý thực thi phi trạng thái. |
| **08** | Thời Gian Timeout & Quản Lý Đồng Thời | Lê Doãn Đạt | Ngưỡng timeout 30s, công thức Concurrency, Reserved vs Provisioned Concurrency. |
| **09** | Giao Thức At-Least-Once & Yêu Cầu Idempotency| Lê Doãn Đạt | Bản chất mạng phân tán, hiện tượng gửi lặp sự kiện và yêu cầu tính lũy đẳng $f(f(x))=f(x)$. |
| **10** | Mô Hình An Ninh Chuẩn OWASP Serverless | Lê Doãn Đạt | 5 tầng phòng thủ: IAM Least Privilege, Image.verify, STS Token, AES-256, dọn /tmp. |
| **11** | Hạ Tầng Dạng Mã: Cấu Trúc 9 Tệp Terraform | Lê Doãn Đạt | Cấu trúc phân tách chức năng (Separation of Concerns) trong Terraform IaC. |
| **12** | Thiết Kế Kho Lưu Trữ Đối Tượng Amazon S3 | Lê Doãn Đạt | Phân tách 2 bucket Input/Output, Block Public Access 100%, mã hóa SSE-S3. |
| **13** | Thiết Kế Hàng Đợi SQS & DynamoDB On-Demand | Lê Doãn Đạt | SQS Event Queue, SQS DLQ 14 ngày, DynamoDB PAY_PER_REQUEST, GSI, PITR, TTL. |
| **14** | Ma Trận Phân Quyền IAM Least Privilege | Lê Doãn Đạt | 6 Statement IAM độc lập, triệt tiêu hoàn toàn `Action: "*"` và `AdministratorAccess`. |
| **15** | Bằng Chứng Kiểm Toán: Zero Hardcoded Secrets | Lê Doãn Đạt | Script `security_audit.py` quét Regex xác nhận 0 khóa bí mật, đạt 100/100 điểm an ninh. |
| **16** | Kiến Trúc Pipeline Đầu-Cuối (Hình 1) | Trần Ngọc Lâm | Sơ đồ luồng 5 trạm tự động; ví dụ minh họa nhà hàng thức ăn nhanh giờ cao điểm. |
| **17** | Thuật Toán Băm SHA-256 Định Danh Tệp | Trần Ngọc Lâm | Vân tay số nhị phân 64 ký tự thay vì tên file; ví dụ đổi tên file vẫn bắt trùng. |
| **18** | Cạm Bẫy Race Condition Của Check-then-Act | Trần Ngọc Lâm | Ví dụ 2 người cùng rút tiền tại cây ATM cùng 1 giây; vỡ tính lũy đẳng. |
| **19** | Đột Phá: Khóa Lũy Đẳng Nguyên Tử DynamoDB | Trần Ngọc Lâm | `attribute_not_exists(image_hash)`, cơ chế chiếc ghế 1 chỗ ngồi, từ chối trong $<2.5\text{ms}$. |
| **20** | Lưu Đồ Thuật Toán Lũy Đẳng & Bẫy Lỗi DLQ (Hình 2)| Trần Ngọc Lâm | Chống Image Bomb, nén Lanczos -89.6%, an toàn RAM /tmp, cô lập Poison Pill vào DLQ. |
| **21** | Thiết Kế Thực Nghiệm Tự Động 100 Lần Gọi | Vũ Thành Đạt | Kịch bản mô phỏng nhịp tải ngẫu nhiên, tập dữ liệu `benchmark_100_runs.csv`. |
| **22** | Phân Phối Độ Trễ Thực Nghiệm Cold vs Warm | Vũ Thành Đạt | Bảng phân vị $p_{50}=30.3\text{ms}, p_{90}=36.1\text{ms}, p_{95}=289.5\text{ms}, p_{99}=589.2\text{ms}$, 0% lỗi. |
| **23** | Khảo Sát RAM & Điểm Ngọt 512MB RAM (Hình 3) | Vũ Thành Đạt | Khảo sát 128MB - 2048MB; chứng minh Sweet Spot 512MB (tăng tốc 360%, chi phí tăng 8%). |
| **24** | Phân Phối Độ Trễ & Chi Phí 3 Mức Tải (Hình 4) | Vũ Thành Đạt | Dự toán chi phí 10k ($0.004), 100k ($0.045), 1M ($0.452); tiết kiệm >95% so với EC2. |
| **25** | Sổ Tay Vận Hành SRE Runbook & DLQ Redrive | Vũ Thành Đạt | Quy trình 3 bước: Cảnh báo CloudWatch $\rightarrow$ Điều tra RCA $\rightarrow$ DLQ Redrive. |
| **26** | Hệ Thống 2 Ứng Dụng Web Studio Thực Tế | Vũ Thành Đạt | Giới thiệu Web 1 (:5001), Web 2 (:5002) và bộ kiểm thử tự động TDD 22 tests. |
| **27** | Kết Luận & Định Hướng Mở Rộng Tương Lai | Cả 3 Thành Viên | Khẳng định giải quyết trọn vẹn câu hỏi nghiên cứu; mở rộng Provisioned Concurrency, AI/ML. |
| **28** | Lời Cảm Ơn & Sẵn Sàng Vấn Đáp Phản Biện | Cả 3 Thành Viên | Lời cảm ơn Thầy TS. Lê Quốc Tuấn và Hội đồng; liên kết GitHub và Live Lab. |

---

## 🔍 CHI TIẾT NỘI DUNG TỪNG SLIDE (38pt Title, 24-28pt Content)

### SLIDE 01: TRANG TIÊU ĐỀ
* **Cơ quan:** TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH — VIỆN CÔNG NGHỆ THÔNG TIN VÀ ĐIỆN, ĐIỆN TỬ
* **Tên Đề tài:** ĐỀ TÀI 9: XÂY DỰNG HỆ THỐNG XỬ LÝ ẢNH HƯỚNG SỰ KIỆN BẰNG SERVERLESS VÀ ĐÁNH GIÁ COLD START
* **Học phần:** Điện toán đám mây (Cloud Computing) — Lớp: 012012303904
* **Giảng viên hướng dẫn:** TS. Lê Quốc Tuấn
* **Sinh viên thực hiện:**
  - Lê Doãn Đạt — MSSV: 038206000230 *(Người 1)*
  - Trần Ngọc Lâm — MSSV: 034206001749 *(Người 2)*
  - Vũ Thành Đạt — MSSV: 001206040720 *(Người 3)*

### SLIDE 02: NỘI DUNG 4 CHƯƠNG CỐT LÕI
* **CHƯƠNG 1:** Cơ sở lý thuyết FaaS, Kiến trúc hướng sự kiện (EDA) và Tiêu chuẩn an ninh OWASP Serverless Top 10 *(Lê Doãn Đạt)*.
* **CHƯƠNG 2:** Thiết kế và triển khai Hạ tầng dạng mã Terraform IaC, Phân quyền IAM Least Privilege *(Lê Doãn Đạt)*.
* **CHƯƠNG 3:** Thiết kế Pipeline đầu-cuối, Thuật toán băm SHA-256 và Đột phá Khóa Lũy Đẳng Nguyên Tử DynamoDB *(Trần Ngọc Lâm)*.
* **CHƯƠNG 4:** Kết quả thực nghiệm 100 lần gọi, Điểm ngọt Sweet Spot 512MB RAM, Chi phí 3 mức tải và SRE Runbook *(Vũ Thành Đạt)*.

### SLIDE 03: BỐI CẢNH THỰC TIỄN & THÁCH THỨC LƯU LƯỢNG
* **Bùng nổ dữ liệu ảnh:** Nền tảng thương mại điện tử, mạng xã hội tiếp nhận lượng ảnh khổng lồ chất lượng cao (1080p, 4K).
* **Nhịp tải không đều (Bursty Load):** Lúc thì vắng lặng trong nhiều giờ, lúc lại bùng nổ hàng nghìn tệp cùng lúc trong các chiến dịch khuyến mãi.
* **Hạn chế của máy chủ truyền thống (EC2):** Thuê theo tải đỉnh thì lãng phí 85% chi phí lúc rỗi; dùng Auto-Scaling máy ảo thì mất 3 - 8 phút để khởi động, dễ làm sập dịch vụ lúc cao điểm.
* **Nhu cầu cấp thiết:** Kiến trúc tự động co giãn đàn hồi tức thì, xử lý tin cậy và kiểm soát chi phí tối ưu.

### SLIDE 04: CÂU HỎI NGHIÊN CỨU & MỤC TIÊU ĐỀ TÀI
* **CÂU HỎI NGHIÊN CỨU:** *"Khi tệp được tải lên theo các nhịp không đều, kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?"*
* **Mục tiêu 1:** Thiết kế chuỗi sự kiện hoàn chỉnh từ lưu trữ đối tượng (S3) -> Đệm sự kiện (SQS) -> Hàm FaaS (Lambda) -> Kho kết quả (S3 Output & DynamoDB).
* **Mục tiêu 2:** Đảm bảo hàm đạt tính lũy đẳng (Idempotent), tự động thử lại (Retry with Backoff) và cô lập lỗi không phục hồi vào Dead-Letter Queue (SQS DLQ).
* **Mục tiêu 3:** Đo lường định lượng Cold Start vs Warm Start, phân tích độ trễ phân vị (p50, p95), xác định Sweet Spot 512MB RAM và dự toán chi phí cho 3 mức tải.

### SLIDE 05: MÔ HÌNH FAAS & KHẢ NĂNG SCALE-TO-ZERO
* **Khái niệm FaaS:** Đơn vị triển khai vi mô là từng hàm nghiệp vụ độc lập. Nhà cung cấp đám mây quản lý 100% phần cứng, hệ điều hành và môi trường thực thi.
* **Scale-to-Zero Tuyệt Đối:** Khi không có sự kiện, số lượng container = 0, chi phí tính toán = $0.00 USD.
* **Co Giãn Đàn Hồi Tức Thì:** Tự động nhân bản hàng trăm container song song chỉ trong vài phần trăm giây khi có tải đột biến.
* **Tính Phí Siêu Vi Mô (Sub-second Metering):** Chi phí được tính chính xác trên cơ sở mili-giây thực thi và dung lượng bộ nhớ cấp phát (GB-seconds).

### SLIDE 06: SO SÁNH SERVERFUL VS SERVERLESS FAAS
* **Đơn vị triển khai:** EC2/VM: Cả máy ảo / OS cồng kềnh  |  Serverless: Từng hàm xử lý nghiệp vụ tinh gọn.
* **Thời gian khởi động:** EC2/VM: Mất 2 - 10 phút để boot OS  |  Serverless: Vài trăm ms (Cold) hoặc <30ms (Warm).
* **Mô hình chi phí:** EC2/VM: Thuê bao cố định 24/7 kể cả lúc rảnh  |  Serverless: Chỉ trả tiền đúng thời gian chạy.
* **Mức tải rỗng (Zero):** EC2/VM: Vẫn mất $10 - $100+/tháng  |  Serverless: Tuyệt đối $0.00 khi không có sự kiện.
* **Bảo trì hạ tầng:** EC2/VM: Tự vá Kernel, cập nhật an ninh, quản lý socket  |  Serverless: AWS đảm bảo 100%.

### SLIDE 07: EVENT SOURCE, TRIGGER & STATELESS EXECUTION
* **Event Source (Nguồn sự kiện):** Amazon S3 Input Bucket: Khi người dùng tải ảnh lên, dịch vụ tự động phát sinh tín hiệu sự kiện `s3:ObjectCreated:*`.
* **Trigger: Push-based vs Pull-based:** Nhóm không dùng Push trực tiếp vì dễ gây tràn quota Lambda. Nhóm dùng Pull-based thông qua hàng đợi SQS để làm phẳng tải đột biến (Load Leveling).
* **Thực Thi Phi Trạng Thái (Stateless):** Mỗi lần gọi hàm là một phiên hoàn toàn độc lập, container có thể bị hủy bất cứ lúc nào. Không có trạng thái phiên nào được giữ lại trong bộ nhớ giữa các lần gọi.
* **Ủy Thác Trạng Thái Bền Vững:** Toàn bộ dữ liệu tệp được lưu vào S3 và siêu dữ liệu được lưu vào bảng DynamoDB.

### SLIDE 08: THỜI GIAN TIMEOUT & QUẢN LÝ ĐỒNG THỜI
* **Giới Hạn Timeout:** Ngưỡng thời gian sống tối đa cho mỗi lần gọi (cấu hình 30 giây trong đề tài). Nếu vượt quá, Lambda bị cưỡng chế ngắt luồng (SIGKILL) để ngăn chặn tiến trình treo vô hạn.
* **Công Thức Concurrency:** $\text{Concurrency} = \text{RPS} \times \text{Duration (s)}$. Ví dụ: 100 ảnh/giây x 0.05s = Chỉ cần 5 container chạy đồng thời.
* **Reserved Concurrency:** Thiết lập hạn ngạch tối đa cho hàm để bảo vệ cơ sở dữ liệu và các dịch vụ downstream không bị sập nguồn.
* **Provisioned Concurrency:** Duy trì sẵn các container ấm 24/7 để triệt tiêu Cold Start cho các hệ thống tài chính yêu cầu SLA thời gian thực khắt khe.

### SLIDE 09: GIAO THỨC AT-LEAST-ONCE & YÊU CẦU IDEMPOTENCY
* **Bản chất mạng phân tán:** Trong hệ thống mạng không đáng tin cậy, việc giao thông điệp đúng 1 lần duy nhất (Exactly-once) là bất khả thi theo định lý CAP.
* **At-least-once Delivery:** Các dịch vụ tin cậy như S3, SQS cam kết giao thông điệp ít nhất một lần. Nếu phản hồi mạng bị rớt, cùng một sự kiện sẽ được gửi lại lần 2.
* **Thao tác người dùng:** Người dùng mất kiên nhẫn bấm đúp chuột (Double-click) nút tải lên cũng sẽ sinh ra 2 sự kiện mang cùng một ảnh trong cùng 1 mili-giây.
* **Yêu cầu bắt buộc:** Hàm Lambda phải đạt tính lũy đẳng (Idempotent): $f(f(x)) = f(x)$. Xử lý N lần cùng một sự kiện vẫn cho ra kết quả đồng nhất như khi xử lý đúng 1 lần.

### SLIDE 10: MÔ HÌNH AN NINH CHUẨN OWASP SERVERLESS TOP 10
* **SAS-01 & SAS-04 (Quyền quá rộng):** Triệt tiêu quyền `AdministratorAccess` và ký tự đại diện `'*'`. Thiết lập 6 Statement độc lập phân định rõ quyền đọc Input và quyền ghi Output.
* **SAS-05 (Injection & Image Bomb):** Giải mã an toàn qua `unquote_plus()`, kiểm tra cấu trúc nhị phân `Image.verify()` và giới hạn cứng `MAX_IMAGE_PIXELS = 50,000,000`.
* **SAS-02 (Zero Hardcoded Secrets):** Không lưu Access Key/Secret Key trong Git. Sử dụng 100% IAM Execution Role và token tạm thời AWS STS tự động xoay vòng.
* **SAS-03 (Mã hóa dữ liệu At-Rest):** Bật mã hóa AES-256 (SSE-S3) trên toàn bộ bucket và kích hoạt mã hóa toàn diện trên DynamoDB.
* **An Toàn Bộ Nhớ Tạm /tmp:** Thao tác trên luồng RAM `io.BytesIO()` và khối `finally` dọn sạch `/tmp` triệt tiêu nguy cơ rò rỉ dữ liệu giữa các lần gọi ấm.

### SLIDE 11: CẤU TRÚC MÃ NGUỒN TERRAFORM IAC
* **Nguyên tắc thiết kế:** Áp dụng nguyên tắc tách biệt chức năng (Separation of Concerns), toàn bộ hạ tầng được định nghĩa bằng mã nguồn Terraform $\ge 1.5.0$, AWS Provider $\sim> 5.0$.
* **Các tệp hạ tầng cốt lõi:** `main.tf` (cấu trúc chung, random suffix), `providers.tf` (hỗ trợ linh hoạt AWS và LocalStack), `variables.tf` (tham số hóa tài nguyên).
* **Các tệp dịch vụ nghiệp vụ:** `s3.tf` (Input/Output bucket, trigger), `sqs.tf` (Dead-Letter Queue 14 ngày), `dynamodb.tf` (bảng On-Demand, GSI, TTL, Encryption).
* **Bảo mật & Tính toán:** `iam.tf` (chính sách phân quyền tối thiểu Least Privilege), `lambda.tf` (cấu hình runtime Python 3.11, RAM 512MB, timeout 30s, X-Ray), `outputs.tf`.

### SLIDE 12: THIẾT KẾ KHO LƯU TRỮ AMAZON S3
* **Phân tách 2 Bucket độc lập:** S3 Input (`cloud-image-raw-input`) tiếp nhận ảnh gốc; S3 Output (`cloud-image-thumbnails-output`) lưu trữ ảnh thu nhỏ thành phẩm.
* **Global Uniqueness:** Tên bucket được gắn chuỗi ngẫu nhiên 6 ký tự để đảm bảo tính duy nhất toàn cầu trên toàn bộ hạ tầng đám mây AWS.
* **Block Public Access 100%:** Kích hoạt toàn bộ 4 cờ chặn truy cập công khai để ngăn chặn tuyệt đối nguy cơ rò rỉ dữ liệu ra ngoài Internet.
* **Cơ chế kích hoạt S3 Notification:** Sự kiện `s3:ObjectCreated:*` được liên kết tự động tới hàm Lambda với quyền Invoke chỉ cấp riêng cho ARN của Input Bucket.

### SLIDE 13: THIẾT KẾ HÀNG ĐỢI SQS & DYNAMODB ON-DEMAND
* **Hàng đợi đệm SQS Event Queue:** Đóng vai trò làm phẳng đột biến tải (Load Leveling), đệm các sự kiện bất đồng bộ và kiểm soát số lượng container Lambda hoạt động song song.
* **Hàng đợi lỗi SQS Dead-Letter Queue:** Thời gian lưu trữ cấu hình 14 ngày (1.209.600 giây), Visibility Timeout 60s và bật mã hóa SSE.
* **DynamoDB Billing On-Demand:** Chế độ `PAY_PER_REQUEST`: chỉ trả tiền trên số lượt đọc/ghi thực tế phát sinh, chi phí bằng $0 khi hệ thống rảnh rỗi.
* **Tính năng nâng cao trên DynamoDB:** Global Secondary Index (`FileNameIndex`) hỗ trợ truy vấn báo cáo; Point-in-Time Recovery (PITR); TTL tự động dọn bản ghi tạm sau 24h.

### SLIDE 14: MA TRẬN PHÂN QUYỀN IAM LEAST PRIVILEGE
* **Statement 1 (S3 Input Read-only):** Chỉ cấp quyền `s3:GetObject` trên ARN của Input Bucket. Không được ghi đè hay xóa ảnh gốc.
* **Statement 2 (S3 Output Write-only):** Chỉ cấp quyền `s3:PutObject` trên ARN của Output Bucket. Không có quyền đọc hay xóa thumbnail.
* **Statement 3 (DynamoDB Idempotency):** Cấp quyền `PutItem`, `UpdateItem`, `GetItem` trên đúng bảng `ImageMetadata`. Không có quyền xóa bảng hay xóa bản ghi.
* **Statement 4 (SQS DLQ Send-only):** Chỉ cấp quyền `sqs:SendMessage` trên ARN của Dead-Letter Queue. Không được quyền xóa hàng đợi.
* **Statement 5 & 6 (CloudWatch & X-Ray):** Cấp quyền ghi log điều tra an ninh và gửi trace hiệu năng về AWS X-Ray.

### SLIDE 15: KIỂM TOÁN ZERO HARDCODED SECRETS
* **IAM Execution Role & AWS STS:** Hàm Lambda tự động nhận định danh thông qua vai trò giả lập `sts:AssumeRole`. Token tạm thời có thời hạn ngắn và tự động xoay vòng.
* **Kịch bản kiểm toán an ninh tự động:** Script `security_audit.py` quét toàn bộ kho mã nguồn bằng Regex nhận diện 4 mẫu khóa nhạy cảm (AKIA/ASIA, Secret Key, Private Key, Token).
* **Kiểm tra cấu hình `.gitignore`:** Xác nhận các tệp `*.tfstate`, `*.tfvars`, `.env`, `*.pem` đã bị chặn khỏi lịch sử Git.
* **Kết quả đánh giá:** Đạt 100/100 điểm an ninh, 0 phát hiện vi phạm, đáp ứng trọn vẹn tiêu chuẩn đánh giá của Hội đồng.

### SLIDE 16: KIẾN TRÚC PIPELINE ĐẦU-CUỐI (HÌNH 1)
* *(Trình chiếu sơ đồ nét cao Hình 1)*
* **Luồng 5 trạm tự động:** Client Upload $\rightarrow$ S3 Input Bucket $\rightarrow$ SQS Event Queue $\rightarrow$ AWS Lambda Compute $\rightarrow$ S3 Thumbnails & DynamoDB ImageMetadata $\rightarrow$ SQS DLQ.
* **Ví dụ trực quan:** Mô hình nhà hàng thức ăn nhanh giờ cao điểm điều tiết qua khay order SQS.

### SLIDE 17: THUẬT TOÁN BĂM SHA-256 ĐỊNH DANH TỆP
* **Hạn chế của việc dùng tên tệp:** Nếu người dùng đổi tên từ `anh_meo.jpg` thành `avatar.png` nhưng cùng 1 ảnh, hệ thống dùng tên tệp sẽ bị đánh lừa và xử lý 2 lần.
* **Băm dòng byte nhị phân:** Lambda nạp nội dung ảnh vào RAM và tính chuỗi băm SHA-256 (256-bit) đại diện cho nội dung vật lý thực tế của ảnh.
* **Vân tay số duy nhất:** Chuỗi băm 64 ký tự Hex là duy nhất tuyệt đối. Bất kỳ sự thay đổi dù chỉ 1 bit điểm ảnh cũng làm thay đổi hoàn toàn mã băm.
* **Sử dụng làm Partition Key:** Nhóm sử dụng `image_hash` làm khóa chính của bảng DynamoDB để kiểm soát tính lũy đẳng.

### SLIDE 18: CẠM BẪY RACE CONDITION CỦA CHECK-THEN-ACT
* **Phương pháp thông thường (Anti-Pattern):** Thực hiện 2 bước tuần tự: Bước 1 gọi `getItem` kiểm tra xem ảnh đã có trong DB chưa; Bước 2 nếu chưa có thì resize ảnh rồi `putItem`.
* **Hiện tượng tranh chấp (Race Condition):** Khi có tải đột biến (Spike) hoặc người dùng bấm đúp chuột, 2 sự kiện trùng lặp đến 2 container Lambda khác nhau trong cùng 1 mili-giây.
* **Ví dụ cây ATM trực quan:** Giống như 2 người cùng rút 1 triệu tại 2 cây ATM cùng một giây từ tài khoản chỉ có 1 triệu: cả 2 cây ATM cùng thấy tài khoản còn tiền và cả 2 cùng nhả tiền!
* **Hậu quả nghiêm trọng:** Cả 2 container cùng thấy "chưa có", cả 2 cùng tốn CPU resize ảnh và cùng ghi đè dữ liệu $\rightarrow$ Vỡ tính lũy đẳng hoàn toàn!

### SLIDE 19: THUẬT TOÁN KHÓA LŨY ĐẲNG NGUYÊN TỬ
* **Thao tác nguyên tử duy nhất (Atomic Operation):** Gom việc kiểm tra và ghi nhận quyền xử lý thành một thao tác duy nhất tại tầng lưu trữ phần cứng DynamoDB.
* **Biểu thức điều kiện nguyên tử:** `ConditionExpression: attribute_not_exists(image_hash) OR status = FAILED`.
* **Cơ chế chiếc ghế 1 chỗ ngồi:** Ảnh đầu tiên đến: khóa chốt với trạng thái `PROCESSING`. Ảnh trùng lặp thứ hai đến: DynamoDB từ chối ngay lập tức bằng lỗi `ConditionalCheckFailedException`.
* **Hiệu năng vượt trội:** Hàm Lambda thứ hai bắt ngoại lệ và thoát an toàn trong **CHƯA ĐẦY 2.5 mili-giây ($< 2.5\text{ ms}$)**, không tốn CPU resize lại và không tạo bản ghi trùng lặp.

### SLIDE 20: LƯU ĐỒ THUẬT TOÁN LŨY ĐẲNG & BẪY LỖI DLQ (HÌNH 2)
* *(Trình chiếu sơ đồ nét cao Hình 2)*
* **Nhánh A (Trùng lặp):** Bắt `ConditionalCheckFailed`, thoát an toàn trong $< 2.5\text{ ms}$, không tạo bản ghi mới.
* **Nhánh B (Hợp lệ):** Nén thumbnail Lanczos 300x300 giảm 89.6% dung lượng, upload S3 Output, cập nhật DynamoDB `PROCESSED`.
* **Nhánh C (Gặp lỗi):** Bắt `UnidentifiedImageError` / `TimeoutError`, cập nhật `FAILED`, ném Exception để SQS thử lại 3 lần với Exponential Backoff $\rightarrow$ Tự động chuyển vào SQS Dead-Letter Queue (lưu 14 ngày).

### SLIDE 21: THIẾT KẾ THỰC NGHIỆM TỰ ĐỘNG 100 LẦN GỌI
* **Mục tiêu thực nghiệm:** Đo đạc khách quan và định lượng hiệu năng thực tế của hệ thống trên môi trường đám mây theo đúng đề cương của Thầy hướng dẫn.
* **Mô phỏng nhịp tải không đều (Bursty Traffic):** Kịch bản tự động kích hoạt 100 lần gọi liên tiếp đan xen giữa các đợt bùng phát (Burst) và thời gian nghỉ (Idle) để quan sát cả Cold Start và Warm Start.
* **Tập dữ liệu chuẩn `benchmark_100_runs.csv`:** Ghi nhận chi tiết từng lần gọi: `InitDuration` (thời gian khởi động microVM), `Duration` (thời gian chạy handler), `BilledDuration` và `RequestId`.
* **Phương pháp phân tích thống kê:** Tính toán các chỉ số phân vị $p_{50}, p_{75}, p_{90}, p_{95}, p_{99}$ và tỷ lệ lỗi toàn hệ thống.

### SLIDE 22: PHÂN PHỐI ĐỘ TRỄ THỰC NGHIỆM: COLD VS WARM START
* **$p_{50}$ (Trung vị) = 30.30 ms:** 50% tổng số yêu cầu được phục vụ cực nhanh trong trạng thái ấm (Warm Start).
* **$p_{75} = 33.15\text{ ms}$ & $p_{90} = 36.08\text{ ms}$:** Hệ thống duy trì độ trễ cực kỳ ổn định trên hầu hết mọi tác vụ xử lý đồ họa.
* **$p_{95}$ (Đuôi trễ) = 289.50 ms:** Bắt đầu xuất hiện hiện tượng cấp phát thêm container mới khi có xung nhịp tải tăng đột ngột.
* **$p_{99}$ (Đỉnh trễ) = 589.20 ms:** Phản ánh đầy đủ trường hợp Cold Start lần đầu tiên: khởi tạo microVM Firecracker và nạp thư viện Pillow.
* **Tỷ lệ lỗi (Error Rate):** Đạt mức tuyệt đối **0.00%** trên toàn bộ 100 lần gọi hợp lệ.

### SLIDE 23: KHẢO SÁT ĐÁNH ĐỔI RAM & ĐIỂM NGỌT (SWEET SPOT) 512MB (HÌNH 3)
* *(Trình chiếu đồ thị nét cao Hình 3)*
* **Tương quan tuyến tính giữa RAM và vCPU:** Cấp phát RAM càng cao thì CPU càng mạnh.
* **Khảo sát từ 128MB đến 2048MB:**
  - 128MB: CPU nghẽn (~0.08 vCPU), chạy mất 98.5ms, chi phí $0.0210/100k req.
  - **512MB:** Tốc độ tăng 360% (chạy chỉ mất 26.8ms), chi phí $0.0228/100k req (chỉ tăng 8% tiền).
  - 1024MB - 2048MB: Tốc độ chỉ tăng thêm vài ms do nghẽn I/O ảnh, nhưng chi phí tăng gấp đôi.
* **Khẳng định thực nghiệm:** **512 MB RAM là Điểm Ngọt (Sweet Spot) tối ưu tuyệt đối**.

### SLIDE 24: PHÂN PHỐI ĐỘ TRỄ & DỰ TOÁN CHI PHÍ 3 MỨC TẢI (HÌNH 4)
* *(Trình chiếu đồ thị cột nét cao Hình 4)*
* **Mức thấp (10,000 ảnh/tháng):** Chi phí chỉ **$0.0046 USD** (tiết kiệm 99.95% so với thuê máy chủ EC2 t2.micro $10/tháng).
* **Mức vừa (100,000 ảnh/tháng):** Chi phí chỉ **$0.0459 USD** (tiết kiệm 99.54% so với EC2).
* **Mức cao (1,000,000 ảnh/tháng):** Chi phí chỉ **$0.4590 USD** (tiết kiệm 95.41% so với EC2).

### SLIDE 25: SỔ TAY VẬN HÀNH SRE RUNBOOK & QUY TRÌNH DLQ REDRIVE
* **Bước 1: Phát hiện & Cảnh báo:** CloudWatch Alarm kích hoạt khi `ApproximateNumberOfMessagesVisible > 0`; gửi thông báo khẩn qua PagerDuty/Slack.
* **Bước 2: Điều tra nguyên nhân gốc (RCA):** Kỹ sư SRE mở giao diện kiểm tra payload tệp lỗi: nếu là file giả mạo thì xóa bỏ; nếu là lỗi timeout do ảnh lớn thì nâng RAM trong Terraform.
* **Bước 3: Khắc phục & Tái điều phối (Redrive):** Triển khai bản vá mã nguồn và nhấn nút "Kích Hoạt SQS DLQ Redrive" trên Dashboard để tự động đẩy toàn bộ thông điệp lỗi trở lại hàng đợi chính xử lý lại an toàn.
* **Cam kết dữ liệu:** Không bao giờ làm mất mát giao dịch hay đơn hàng của khách hàng.

### SLIDE 26: HỆ THỐNG 2 ỨNG DỤNG WEB STUDIO THỰC TẾ (CỔNG :5001 & :5002)
* **Web 1: Knowledge Hub (`:5001`):** Cổng học thuật 7 Module: Tra cứu lý thuyết FaaS, OWASP Top 10, Điểm ngọt 512MB RAM và Bộ trình diễn Code tương tác (Code Walkthrough).
* **Web 2: Live Lab Studio (`:5002`):** Bàn làm việc thực nghiệm: Visual Pipeline Canvas 6 trạm chuyển động xung nhịp, 6 Scenario Tabs tương tác, Telemetry Console và Modal DLQ Redrive.
* **Khởi chạy 1-Click:** Tệp `run_all.bat` tự động kiểm tra môi trường và khởi động đồng thời cả 2 máy chủ trên nền Python thuần, không cần cài đặt Docker/npm.
* **Bộ kiểm thử tự động TDD:** Đầy đủ 22 test cases kiểm thử đơn vị và tích hợp đầu-cuối đạt tỷ lệ vượt qua tuyệt đối 100%.

### SLIDE 27: KẾT LUẬN & ĐỊNH HƯỚNG MỞ RỘNG TƯƠNG LAI
* **Giải quyết trọn vẹn câu hỏi nghiên cứu:** Kiến trúc hướng sự kiện Serverless giải quyết xuất sắc bài toán nhịp tải không đều: Scale-to-Zero tiết kiệm 95% chi phí, SQS đệm tải an toàn và Khóa nguyên tử DynamoDB bảo đảm tính lũy đẳng.
* **Đạt chuẩn công nghiệp:** Tuân thủ nghiêm ngặt chuẩn an ninh OWASP Serverless Top 10, Zero Hardcoded Secrets và phân quyền IAM tối thiểu.
* **Hướng mở rộng 1: Provisioned Concurrency:** Nghiên cứu tự động mở rộng container ấm theo lịch biểu trong các khung giờ cao điểm để triệt tiêu hoàn toàn Cold Start.
* **Hướng mở rộng 2: AI/ML Pipeline & Multi-Region:** Tích hợp các mô hình học sâu nhận diện khuôn mặt/đối tượng và triển khai Active-Active trên nhiều AWS Region.

### SLIDE 28: LỜI CẢM ƠN & VẤN ĐÁP
* **Lời tri ân:** XIN TRÂN TRỌNG CẢM ƠN THẦY TS. LÊ QUỐC TUẤN VÀ QUÝ THẦY CÔ TRONG HỘI ĐỒNG ĐÃ LẮNG NGHE!
* **Phản biện:** Nhóm chúng em rất mong nhận được nhận xét và câu hỏi phản biện từ Thầy!
* **Liên kết tham khảo:**
  - GitHub Repository: `https://github.com/datdanghoccode/DTDM_XuLyAnh_Serverless`
  - Live Lab Studio: `http://localhost:5002`
  - Knowledge Hub: `http://localhost:5001`
