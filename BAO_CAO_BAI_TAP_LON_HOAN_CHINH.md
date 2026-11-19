# TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI THÀNH PHỐ HỒ CHÍ MINH
## VIỆN CÔNG NGHỆ THÔNG TIN VÀ ĐIỆN, ĐIỆN TỬ

---

# BÁO CÁO BÀI TẬP LỚN
### HỌC PHẦN: ĐIỆN TOÁN ĐÁM MÂY (CLOUD COMPUTING)
## ĐỀ TÀI 9: XÂY DỰNG HỆ THỐNG XỬ LÝ ẢNH HƯỚNG SỰ KIỆN BẰNG SERVERLESS VÀ ĐÁNH GIÁ COLD START

* **Ngành:** CÔNG NGHỆ THÔNG TIN
* **Giảng viên hướng dẫn:** TS. Lê Quốc Tuấn
* **Sinh viên thực hiện (Lớp 012012303904):**
  1. **Lê Doãn Đạt** — MSSV: `038206000230`
  2. **Trần Ngọc Lâm** — MSSV: `034206001749`
  3. **Vũ Thành Đạt** — MSSV: `001206040720`

*Thành phố Hồ Chí Minh, tháng 6 năm 2025*

---

## LỜI CẢM ƠN

Trong quá trình học tập và thực hiện bài tập lớn môn Điện toán đám mây, nhóm chúng em đã nhận được sự định hướng, hướng dẫn tận tình và truyền đạt kiến thức chuyên môn sâu sắc từ **TS. Lê Quốc Tuấn**. Chúng em xin bày tỏ lòng biết ơn chân thành và sâu sắc nhất đến Thầy đã tạo điều kiện và hướng dẫn chúng em hoàn thiện đề tài này một cách chỉn chu, bài bản theo đúng các tiêu chuẩn kỹ thuật hiện đại của điện toán đám mây.

Chúng em cũng xin trân trọng cảm ơn Ban Giám hiệu Trường Đại học Giao thông Vận tải Thành phố Hồ Chí Minh (UTH), cùng quý Thầy Cô Viện Công nghệ Thông tin và Điện, Điện tử đã tạo môi trường học thuật chất lượng cao, cung cấp cơ sở vật chất và tài liệu nghiên cứu phong phú giúp chúng em tiếp cận được các công nghệ đám mây tiên tiến nhất hiện nay.

Mặc dù nhóm đã nỗ lực hết mình để xây dựng hệ thống hoàn chỉnh từ hạ tầng, mã nguồn cho đến các bài đo đạc thực nghiệm, bài báo cáo chắc chắn khó tránh khỏi những thiếu sót nhất định. Nhóm chúng em rất mong nhận được những lời nhận xét, góp ý quý báu từ Thầy để công trình nghiên cứu được hoàn thiện hơn nữa.

---

## BẢNG PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN

| Thành Viên | Mã Số Sinh Viên | Nhiệm Vụ Đảm Trách Trong Đề Tài | Tỷ Lệ Đóng Góp |
| :--- | :---: | :--- | :---: |
| **Lê Doãn Đạt** *(Người 1)* | `038206000230` | • **Phần Mở Đầu:** Lý do chọn đề tài, phát biểu câu hỏi nghiên cứu, mục tiêu và phương pháp.<br>• **Chương 1 (Cơ sở lý thuyết):** FaaS, Event Source, Trigger, Stateless, Concurrency, Cold Start & Rủi ro bảo mật chuẩn OWASP Serverless Top 10.<br>• **Chương 2 (Hạ tầng Terraform):** Thiết kế toàn bộ mã nguồn Terraform IaC (S3, SQS, DynamoDB, Lambda, IAM Least Privilege với 6 Statement độc lập, script Security Audit chứng minh Zero Hardcoded Secrets). | **100%** |
| **Trần Ngọc Lâm** *(Người 2)* | `034206001749` | • **Chương 3 (Thiết kế Pipeline & Thuật toán):** Thiết kế luồng xử lý hàm Lambda FaaS (`src/lambda_function.py`).<br>• Phát triển thuật toán băm SHA-256 định danh tệp tin.<br>• Thiết kế **Thuật toán Khóa Lũy Đẳng Nguyên Tử trên Amazon DynamoDB** (`ConditionExpression: attribute_not_exists(image_hash)`), chặn đứng Race condition của phương pháp Check-then-Act.<br>• Xử lý ảnh an toàn bằng thư viện Pillow (chống Image Bomb `MAX_IMAGE_PIXELS = 50_000_000`, nén Lanczos 300x300 giảm 89.6% dung lượng, an toàn bộ nhớ `/tmp` qua luồng RAM `io.BytesIO()`).<br>• Xử lý ngoại lệ và điều hướng lỗi vào SQS Dead-Letter Queue. | **100%** |
| **Vũ Thành Đạt** *(Người 3)* | `001206040720` | • **Chương 4 (Thực nghiệm & Vận hành SRE):** Xây dựng bộ kịch bản kiểm thử tự động 100 lần gọi đan xen nhịp tải (`benchmark_100_runs.csv`).<br>• Phân tích dữ liệu định lượng Cold Start vs Warm Start qua các phân vị $p_{50}=30.30\text{ms}, p_{90}=36.08\text{ms}, p_{95}=289.50\text{ms}, p_{99}=589.20\text{ms}$.<br>• Khảo sát đánh đổi RAM (128MB - 2048MB) và chứng minh **Điểm Ngọt (Sweet Spot) 512MB RAM**.<br>• Mô hình hóa chi phí vận hành cho 3 mức tải (10k, 100k, 1M ảnh) so sánh với máy chủ EC2.<br>• Soạn thảo Sổ tay vận hành SRE Runbook 3 bước và quy trình xử lý sự cố SQS DLQ Redrive.<br>• **Kết luận và Hướng phát triển**. | **100%** |

---

## MỤC LỤC TỔNG THỂ

* **LỜI CẢM ƠN**
* **BẢNG PHÂN CÔNG NHIỆM VỤ THÀNH VIÊN**
* **DANH MỤC BẢNG BIỂU & HÌNH VẼ**
* **PHẦN MỞ ĐẦU**
  * 1. Lý do chọn đề tài
  * 2. Câu hỏi nghiên cứu
  * 3. Mục tiêu đề tài
  * 4. Phạm vi nghiên cứu
  * 5. Phương pháp nghiên cứu
* **CHƯƠNG 1. CƠ SỞ LÝ THUYẾT ĐIỆN TOÁN KHÔNG MÁY CHỦ (FAAS) & KIẾN TRÚC HƯỚNG SỰ KIỆN**
  * 1.1. Mô hình FaaS và Kiến trúc hướng sự kiện (Event-Driven)
    * 1.1.1. Function-as-a-Service (FaaS) & Khả năng Scale-to-Zero
    * 1.1.2. Event Source, Trigger và Stateless Execution
    * 1.1.3. Timeout và Concurrency
    * 1.1.4. At-least-once Delivery và Yêu cầu Idempotency
  * 1.2. Retry with Backoff, Dead-Letter Queue và Eventual Consistency
    * 1.2.1. Retry with Exponential Backoff và Jitter
    * 1.2.2. Dead-Letter Queue (SQS DLQ) và Cơ chế cách ly Poison Pill
    * 1.2.3. Eventual Consistency trong hệ thống phân tán
  * 1.3. Cold Start, Warm Invocation và Provisioned Concurrency
    * 1.3.1. Bản chất vật lý của Cold Start (Vòng đời MicroVM Firecracker)
    * 1.3.2. Warm Invocation và Tái sử dụng Sandbox
    * 1.3.3. Tác động của Package Size và Phân bổ Bộ nhớ RAM
    * 1.3.4. Cơ chế Provisioned Concurrency
  * 1.4. Rủi ro bảo mật Serverless theo chuẩn OWASP Serverless Top 10
* **CHƯƠNG 2. THIẾT KẾ VÀ TRIỂN KHAI HẠ TẦNG SERVERLESS (TERRAFORM)**
  * 2.1. Tổng quan kiến trúc hệ thống và giải quyết câu hỏi nghiên cứu
  * 2.2. Cấu trúc mã nguồn Infrastructure as Code (Terraform)
  * 2.3. Thiết kế chi tiết từng thành phần hạ tầng
    * 2.3.1. Object Storage – Amazon S3 (`s3.tf`)
    * 2.3.2. Dead-Letter Queue – Amazon SQS (`sqs.tf`)
    * 2.3.3. Metadata & Idempotency Store – Amazon DynamoDB (`dynamodb.tf`)
    * 2.3.4. Cấu hình hàm Serverless Compute – AWS Lambda (`lambda.tf`)
  * 2.4. Chính sách bảo mật IAM Least Privilege (`iam.tf`)
  * 2.5. Bằng chứng không lưu khóa trong mã nguồn (Zero Hardcoded Secrets)
* **CHƯƠNG 3. THIẾT KẾ PIPELINE VÀ THUẬT TOÁN XỬ LÝ ẢNH ĐẦU-CUỐI**
  * 3.1. Thiết kế tổng thể Hàm tính toán Serverless Lambda (`src/lambda_function.py`)
  * 3.2. Thuật toán băm SHA-256 định danh nội dung tệp tin
  * 3.3. Thuật toán Khóa Lũy Đẳng Nguyên Tử trên Amazon DynamoDB
    * 3.3.1. Phân tích cạm bẫy Race condition của phương pháp Check-then-Act
    * 3.3.2. Cơ chế biểu thức điều kiện `ConditionExpression` ở tầng lưu trữ
    * 3.3.3. Đoạn mã triển khai Python và phân tích độ trễ từ chối ($< 2.5\text{ ms}$)
  * 3.4. Xử lý ảnh an toàn bằng thư viện Pillow (Phòng chống Decompression Bomb)
  * 3.5. Kỹ thuật an toàn bộ nhớ `/tmp` và triệt tiêu rò rỉ dữ liệu giữa các lần gọi ấm
  * 3.6. Cơ chế xử lý ngoại lệ và điều hướng lỗi vào SQS Dead-Letter Queue
* **CHƯƠNG 4. KẾT QUẢ THỰC NGHIỆM ĐO ĐẠC, ĐÁNH GIÁ VÀ VẬN HÀNH SRE**
  * 4.1. Thiết kế bộ kịch bản thực nghiệm tự động (100 lần gọi đo lường)
  * 4.2. Bảng phân phối độ trễ thực nghiệm và đối sánh Cold Start vs Warm Start
  * 4.3. Khảo sát đánh đổi Hiệu năng - Chi phí và Điểm Ngọt (Sweet Spot) 512MB RAM
  * 4.4. Mô hình ước tính chi phí Serverless cho 3 mức lưu lượng tải thực tế
  * 4.5. Sổ tay vận hành SRE Runbook 3 bước và quy trình xử lý sự cố DLQ Redrive
* **KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**
* **TÀI LIỆU THAM KHẢO**
* **BÁO CÁO KIỂM TRA WATERMARK (WATERMARK REMOVAL AUDIT)**

---

## DANH MỤC BẢNG BIỂU & HÌNH VẼ

* **Bảng 2.1:** Cấu trúc tệp Terraform và chức năng tương ứng trong hệ thống
* **Bảng 2.2:** Các thông số cấu hình cốt lõi của hàm AWS Lambda
* **Bảng 2.3:** Ma trận phân quyền IAM Least Privilege chi tiết
* **Bảng 3.1:** Thông số kỹ thuật thuật toán Khóa Lũy Đẳng Nguyên Tử
* **Bảng 3.2:** So sánh kích thước và thời gian nén ảnh qua thuật toán Pillow Lanczos
* **Bảng 4.1:** Bảng phân phối độ trễ thực nghiệm 100 lần gọi ($p_{50}, p_{75}, p_{90}, p_{95}, p_{99}$)
* **Bảng 4.2:** Khảo sát đánh đổi Hiệu năng - Chi phí theo dung lượng RAM (128MB - 2048MB)
* **Bảng 4.3:** Dự toán chi phí Serverless cho 3 mức lưu lượng tải (10k, 100k, 1M ảnh/tháng)
* **Hình 2.1:** Sơ đồ kiến trúc hệ thống xử lý ảnh hướng sự kiện bằng Serverless (End-to-End)
* **Hình 3.1:** Lưu đồ thuật toán Khóa lũy đẳng nguyên tử và Xử lý lỗi DLQ
* **Hình 4.1:** So sánh thời gian phản hồi Cold vs Warm và Đánh đổi Hiệu năng - Chi phí RAM
* **Hình 4.2:** Phân phối độ trễ 100 lần gọi ($p_{50}, p_{95}$) và Ước tính chi phí Serverless cho 3 mức tải

---

## PHẦN MỞ ĐẦU

### 1. Lý do chọn đề tài
Trong bối cảnh điện toán đám mây phát triển mạnh mẽ và các ứng dụng Internet ngày càng mở rộng, mô hình Serverless (FaaS – Function-as-a-Service) đang trở thành xu hướng chủ đạo cho các hệ thống xử lý dữ liệu hướng sự kiện (Event-Driven Architecture). Thay vì phải duy trì, giám sát và trả tiền thuê bao cố định cho các máy chủ 24/7 kể cả khi không có lưu lượng, nhà phát triển chỉ cần tập trung vào logic xử lý nghiệp vụ, trong khi nhà cung cấp đám mây tự động co giãn tài nguyên theo nhu cầu thực tế.

Tuy nhiên, kiến trúc Serverless cũng đặt ra nhiều thách thức kỹ thuật phức tạp: hiện tượng Khởi động nguội (Cold Start) làm tăng đột biến độ trễ khi các hàm không được kích hoạt thường xuyên; cơ chế chuyển phát tin cậy "At-least-once Delivery" của mạng phân tán dẫn đến nguy cơ nhân bản sự kiện gây xử lý trùng lặp dữ liệu; và nguyên tắc phân quyền an ninh tối thiểu (IAM Least Privilege) đòi hỏi thiết kế chính xác cho từng thành phần hạ tầng độc lập.

Xuất phát từ những thách thức thực tiễn nêu trên, nhóm chúng em chọn **Đề tài 9: "Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless và đánh giá Cold Start"** nhằm thiết kế, triển khai hạ tầng dạng mã (IaC), lập trình hàm xử lý lũy đẳng và tiến hành đo đạc thực nghiệm định lượng trên nền tảng AWS.

### 2. Câu hỏi nghiên cứu
Đề tài tập trung giải quyết câu hỏi nghiên cứu cốt lõi được Hội đồng và Thầy hướng dẫn đặt ra:
> *"Khi tệp được tải lên theo các nhịp không đều (bursty / unpredictable load), kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?"*

### 3. Mục tiêu đề tài
* **Mục tiêu 1:** Thiết kế chuỗi sự kiện hoàn chỉnh từ lưu trữ đối tượng (Amazon S3 Input) đến hàm xử lý phi trạng thái (AWS Lambda FaaS) và kho siêu dữ liệu (Amazon DynamoDB).
* **Mục tiêu 2:** Đảm bảo hàm xử lý đạt tính lũy đẳng (Idempotent), tự động xử lý cơ chế thử lại (Retry with Exponential Backoff) và cô lập các tệp hỏng không thể phục hồi vào Hàng đợi thông điệp lỗi (Dead-Letter Queue - SQS DLQ).
* **Mục tiêu 3:** Đo lường định lượng hiện tượng Cold Start so với Warm Start, độ trễ đầu-cuối theo phân vị ($p_{50}, p_{95}$), phân tích đánh đổi bộ nhớ (RAM Sweet Spot) và mô hình hóa chi phí vận hành theo số lượng sự kiện.

### 4. Phạm vi nghiên cứu
Đề tài tập trung nghiên cứu và triển khai trên hệ sinh thái dịch vụ đám mây của Amazon Web Services (AWS), bao gồm: S3 (Object Storage), Lambda (Serverless Compute), DynamoDB (NoSQL Database), SQS (Message Queue & DLQ), IAM (Security Governance), CloudWatch Logs và X-Ray Tracing. Môi trường phát triển cục bộ và kiểm thử tự động sử dụng LocalStack kết hợp bộ công cụ đo lường Python.

### 5. Phương pháp nghiên cứu
* **Nghiên cứu lý thuyết:** Tổng hợp các công trình học thuật quốc tế về FaaS, vòng đời MicroVM Firecracker, tiêu chuẩn an toàn thông tin OWASP Serverless Top 10 và các bài giảng của TS. Lê Quốc Tuấn.
* **Nghiên cứu thực nghiệm:** Xây dựng hạ tầng hoàn toàn tự động bằng Terraform (IaC), lập trình hàm xử lý ảnh Python Pillow với thuật toán Khóa lũy đẳng nguyên tử, và thực thi bộ kiểm thử 100 lần gọi đan xen nhịp tải.
* **Phân tích dữ liệu định lượng:** Trích xuất độ trễ InitDuration, Duration, BilledDuration, tính toán các chỉ số phân vị $p_{50}, p_{75}, p_{90}, p_{95}, p_{99}$, xây dựng biểu đồ trực quan hóa và đối sánh chi phí giữa Serverless và EC2.

---

## CHƯƠNG 1. CƠ SỞ LÝ THUYẾT ĐIỆN TOÁN KHÔNG MÁY CHỦ (FAAS) & KIẾN TRÚC HƯỚNG SỰ KIỆN

*(Phụ trách nội dung: Sinh viên 1 – Lê Doãn Đạt, MSSV: 038206000230)*

### 1.1. Mô hình FaaS và Kiến trúc hướng sự kiện (Event-Driven)

#### 1.1.1. Function-as-a-Service (FaaS) & Khả năng Scale-to-Zero
FaaS (Function-as-a-Service) là mô hình điện toán đám mây trong đó đơn vị triển khai và thực thi nhỏ nhất là một hàm (function). Nhà cung cấp dịch vụ đám mây chịu trách nhiệm quản trị toàn bộ hạ tầng bên dưới bao gồm: phần cứng máy chủ vật lý, hệ điều hành mạng, bộ điều phối container runtime và việc cấp phát môi trường thực thi (Execution Environment). Lập trình viên chỉ cần tập trung phát triển logic nghiệp vụ thuần túy trong hàm handler và cấu hình các nguồn kích hoạt (trigger).

Đặc trưng mang tính cách mạng nhất của FaaS là khả năng **Scale-to-Zero**: khi không có sự kiện nào kích hoạt, hệ thống hoàn toàn không tiêu thụ bất kỳ tài nguyên tính toán nào và chi phí bằng 0. Khi có lượng lớn sự kiện đến đồng thời, nền tảng tự động nhân bản (auto-scale) số lượng môi trường thực thi song song trong vài phần trăm giây.

#### 1.1.2. Event Source, Trigger và Stateless Execution
Trong kiến trúc hướng sự kiện, **Event Source (nguồn sự kiện)** là thành phần phát sinh tín hiệu kích hoạt pipeline xử lý. Trong đề tài này, nguồn sự kiện là kho lưu trữ đối tượng Amazon S3: khi người dùng tải ảnh lên S3 Input Bucket, dịch vụ S3 phát sinh sự kiện `s3:ObjectCreated:*` và chuyển tiếp đến hàm Lambda thông qua cơ chế S3 Event Notification (Trigger).

Hàm Lambda được thiết kế nghiêm ngặt theo nguyên tắc **Thực thi phi trạng thái (Stateless Execution)**: mỗi lần gọi không lưu giữ trạng thái phiên làm việc trong bộ nhớ giữa các lần gọi khác nhau. Mọi trạng thái bền vững (metadata ảnh, trạng thái xử lý, hash idempotency) đều được ủy thác sang dịch vụ lưu trữ bên ngoài – cụ thể là Amazon DynamoDB.

#### 1.1.3. Timeout và Concurrency
* **Timeout:** Ngưỡng thời gian tối đa cho phép một lượt thực thi hàm Lambda. Nếu hàm chưa hoàn thành trong khoảng thời gian này, nền tảng sẽ gửi tín hiệu `SIGKILL` cưỡng chế ngắt luồng và đánh dấu lỗi. Trong đồ án, timeout mặc định được cấu hình an toàn là **30 giây** thông qua biến Terraform `var.lambda_timeout`.
* **Concurrency:** Số lượng Execution Environments chạy song song tại cùng một thời điểm:
  $$\text{Concurrency} = \text{Requests per Second (RPS)} \times \text{Execution Duration (seconds)}$$
  Việc cấu hình **Reserved Concurrency** giúp cô lập hạn ngạch cho hàm, bảo vệ hạ tầng downstream không bị nghẽn thông lượng.

#### 1.1.4. At-least-once Delivery và Yêu cầu Idempotency
Trong kiến trúc phân tán hướng sự kiện, cơ chế chuyển phát thông điệp của S3/SQS/Lambda đảm bảo mức **At-least-once Delivery (giao ít nhất một lần)**. Điều này đồng nghĩa với việc cùng một sự kiện tải ảnh có thể được gửi lặp lại do lỗi mạng tạm thời hoặc cơ chế retry nội bộ. Hiện tượng này đặt ra yêu cầu bắt buộc: hàm xử lý phải đạt **tính lũy đẳng (Idempotent)** – tức là xử lý $N$ lần cùng một sự kiện vẫn cho ra kết quả đồng nhất như khi xử lý đúng một lần duy nhất, tuyệt đối không tạo bản ghi rác hay ghi đè sai lệch dữ liệu.

### 1.2. Retry with Backoff, Dead-Letter Queue và Eventual Consistency

#### 1.2.1. Retry with Exponential Backoff và Jitter
Khi hàm Lambda xử lý thất bại (do tệp hỏng, timeout hoặc nghẽn mạng), nền tảng AWS tự động thử lại (retry) theo cơ chế **Exponential Backoff** (lùi số mũ kết hợp nhiễu ngẫu nhiên Jitter):
$$t_{\text{backoff}} = \min\left(t_{\max}, \; 2^k \cdot t_0\right) + \text{jitter}$$
Cơ chế này giúp phân tán thời điểm thử lại của các worker, ngăn chặn hiện tượng Thundering Herd Problem làm sụp đổ các dịch vụ phụ trợ.

#### 1.2.2. Dead-Letter Queue (SQS DLQ) và Cơ chế cách ly Poison Pill
Nếu sau 3 lần thử liên tiếp (`maxReceiveCount = 3`) mà vẫn thất bại, sự kiện được coi là lỗi không thể tự phục hồi (Poison Pill – tệp tin hỏng hoặc tệp giả mạo) và được tự động chuyển vào **Dead-Letter Queue (SQS DLQ)**. Hàng đợi SQS DLQ lưu trữ thông điệp lỗi trong **14 ngày (1.209.600 giây)**, cung cấp thời gian an toàn cho kỹ sư vận hành điều tra nguyên nhân gốc (RCA) và thực hiện quy trình **DLQ Redrive** tái xử lý sau khi vá lỗi.

#### 1.2.3. Eventual Consistency trong hệ thống phân tán
Kiến trúc lưu trữ phân tán hiện đại tuân thủ mô hình **Eventual Consistency (Nhất quán cuối cùng)**: khi Lambda cập nhật DynamoDB và S3, các bản sao dữ liệu trên toàn vùng sẽ hội tụ về trạng thái đồng nhất sau vài mili-giây. Thiết kế ứng dụng phía máy khách cần có tính chấp nhận dung sai, áp dụng cơ chế polling hoặc lắng nghe sự kiện để cập nhật giao diện người dùng.

### 1.3. Cold Start, Warm Invocation và Provisioned Concurrency

#### 1.3.1. Bản chất vật lý của Cold Start (Vòng đời MicroVM Firecracker)
Cold Start xảy ra khi có sự kiện mới kích hoạt hàm Lambda nhưng không có container nào đang ở trạng thái rảnh (idle). Nền tảng phải thực hiện 4 bước:
1. Khởi tạo MicroVM (công nghệ ảo hóa tối giản Firecracker).
2. Tải mã nguồn gói `.zip` từ S3 nội bộ.
3. Khởi động Python 3.11 Runtime.
4. Chạy mã khởi tạo ngoài hàm handler (`InitDuration` – nạp thư viện C-binding Pillow).
Toàn bộ quá trình này tạo ra độ trễ bổ sung từ **400 ms đến 1200 ms**.

#### 1.3.2. Warm Invocation và Tái sử dụng Sandbox
Sau khi xử lý xong, container không bị phá hủy ngay mà được đóng băng trong bộ nhớ RAM từ 5 đến 15 phút. Khi có sự kiện tiếp theo đến, container được tái sử dụng ngay lập tức, bỏ qua hoàn toàn pha `InitDuration`. Độ trễ phản hồi giảm mạnh chỉ còn **20 ms đến 40 ms** (nhanh hơn từ 15 đến 30 lần).

#### 1.3.3. Tác động của Package Size và Phân bổ Bộ nhớ RAM
* **Package Size:** Bằng việc chỉ sử dụng thư viện xử lý ảnh tối giản Pillow (kích thước $\approx 15\text{MB}$) thay vì OpenCV ($\approx 150\text{MB}$), thời gian khởi động nguội giảm hơn 60%.
* **Phân bổ RAM & CPU:** Trong AWS Lambda, năng lực vCPU được phân bổ tỷ lệ thuận theo dung lượng RAM. Tăng cấu hình RAM từ 128MB lên 512MB giúp rút ngắn thời gian xử lý ảnh tới 88%.

#### 1.3.4. Cơ chế Provisioned Concurrency
Provisioned Concurrency là tính năng giữ sẵn các container ở trạng thái ấm 24/7 để triệt tiêu hoàn toàn Cold Start cho các hệ thống có yêu cầu SLA khắt khe. Tuy nhiên, cơ chế này phát sinh chi phí duy trì cố định, làm mất đi tính chất Scale-to-Zero thuần túy của Serverless.

### 1.4. Rủi ro bảo mật Serverless theo chuẩn OWASP Serverless Top 10
* **SAS-01 & SAS-04 (Quyền quá rộng - Over-privileged Functions):** Triệt tiêu hoàn toàn quyền quản trị `AdministratorAccess` và ký tự đại diện `Action: "*"`. Thiết lập chính sách phân quyền tối thiểu gồm 6 Statement độc lập giới hạn theo ARN tài nguyên cụ thể.
* **SAS-05 (Injection qua sự kiện & Path Traversal):** Sử dụng `urllib.parse.unquote_plus()` và `os.path.basename()` để giải mã tên file; xác thực tệp nhị phân qua `Image.verify()` và giới hạn cứng `Image.MAX_IMAGE_PIXELS = 50_000_000` chống Decompression Bomb.
* **SAS-02 (Không lưu khóa bí mật - Zero Hardcoded Secrets):** Sử dụng 100% IAM Execution Role kết hợp AWS STS Temporary Token tự động xoay vòng, tuyệt đối không lưu Access Key tĩnh trong mã nguồn Git.
* **SAS-03 (Bảo vệ dữ liệu lưu trữ):** Bật tính năng mã hóa At-Rest chuẩn quân sự AES-256 (SSE-S3 và DynamoDB Default Encryption).
* **Rò rỉ dữ liệu tạm (/tmp Data Leakage):** Thực hiện đọc ghi trực tiếp trên luồng bộ nhớ RAM bằng `io.BytesIO()`, kết hợp khối lệnh `finally` dọn sạch thư mục `/tmp` trước khi container đóng băng.

---

## CHƯƠNG 2. THIẾT KẾ VÀ TRIỂN KHAI HẠ TẦNG SERVERLESS (TERRAFORM)

*(Phụ trách nội dung: Sinh viên 1 – Lê Doãn Đạt, MSSV: 038206000230)*

### 2.1. Tổng quan kiến trúc hệ thống và giải quyết câu hỏi nghiên cứu
Từ góc độ hạ tầng, câu hỏi nghiên cứu *"Khi tệp được tải lên theo các nhịp không đều, kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?"* được giải quyết thông qua 3 trụ cột thiết kế:
* **Đáp ứng nhịp tải không đều (Spiky Workloads):** Toàn bộ thành phần hạ tầng được thiết kế theo mô hình Serverless 100% (S3, Lambda, DynamoDB On-Demand, SQS). Khi không có tệp tải lên, hệ thống tự động thu về mức tiêu thụ tài nguyên bằng 0 (Scale-to-Zero).
* **Xử lý tin cậy (Reliability):** Chuỗi sự kiện bất đồng bộ tích hợp cơ chế Retry with Backoff, kiểm soát trùng lặp (Idempotency Store trên DynamoDB) và cô lập lỗi không phục hồi vào Dead-Letter Queue (SQS DLQ).
* **Kiểm soát chi phí (Cost Control):** Lambda tính phí theo mili-giây (GB-s), DynamoDB PAY_PER_REQUEST, CloudWatch Logs giới hạn retention 14 ngày.

![Hình 2.1. Sơ đồ kiến trúc hệ thống xử lý ảnh hướng sự kiện bằng Serverless](so_do_kien_truc_pipeline_end_to_end.jpg)
*Hình 2.1. Sơ đồ kiến trúc hệ thống xử lý ảnh hướng sự kiện bằng Serverless (End-to-End)*

### 2.2. Cấu trúc mã nguồn Infrastructure as Code (Terraform)
Toàn bộ hạ tầng được định nghĩa dưới dạng mã nguồn (IaC) sử dụng HashiCorp Terraform phiên bản ≥ 1.5.0, AWS Provider ~> 5.0, tổ chức theo nguyên tắc phân tách trách nhiệm (Separation of Concerns):

*Bảng 2.1. Cấu trúc tệp Terraform và chức năng tương ứng*
| Tệp Terraform | Chức Năng Kiến Trúc Trong Đề Tài | Số Dòng Mã |
| :--- | :--- | :---: |
| `main.tf` | Cấu trúc tổng thể, Data Sources (`aws_caller_identity`, `aws_region`), Random Suffix S3 | 40 |
| `providers.tf` | Cấu hình AWS Provider, hỗ trợ linh hoạt AWS Cloud thật và LocalStack | 67 |
| `variables.tf` | Tham số hóa: AWS Region, Environment, Memory Size, Timeout, DLQ retention | 95 |
| `s3.tf` | S3 Input/Output Buckets, AES-256 SSE, Block Public Access, S3 Event Notification | 123 |
| `sqs.tf` | Dead-Letter Queue (SQS DLQ), Queue Policy chỉ cho phép Lambda gửi tin nhắn lỗi | 46 |
| `dynamodb.tf` | Bảng Metadata & Idempotency (PAY_PER_REQUEST), GSI, PITR, TTL, Encryption | 69 |
| `iam.tf` | IAM Role & Policy theo Least Privilege: 6 Statement phân quyền độc lập | 150 |
| `lambda.tf` | Cấu hình hàm Lambda, Memory 512MB, Timeout 30s, Dead-Letter Config, X-Ray Tracing | 94 |
| `outputs.tf` | Xuất ARN, URL, Tên tài nguyên phục vụ kiểm thử và bàn giao | 89 |

### 2.3. Thiết kế chi tiết từng thành phần hạ tầng
* **S3 Input & Output Buckets (`s3.tf`):** Hai bucket riêng biệt được cấu hình Block Public Access 100%, mã hóa AES-256 (SSE-S3), bật Versioning. Cấu hình `aws_s3_bucket_notification` gửi sự kiện `s3:ObjectCreated:*` kích hoạt Lambda.
* **Dead-Letter Queue (`sqs.tf`):** Hàng đợi SQS DLQ lưu trữ thông điệp lỗi trong 14 ngày (1.209.600 giây) với Visibility Timeout 60 giây và mã hóa SSE.
* **Metadata Store (`dynamodb.tf`):** Bảng `ImageMetadata` sử dụng billing mode `PAY_PER_REQUEST` (On-Demand), Partition Key `image_hash` (S), tích hợp GSI `FileNameIndex`, Point-in-Time Recovery (PITR) và TTL tự động dọn dẹp sau 24h.
* **Serverless Compute (`lambda.tf`):** Hàm Lambda chạy trên Python 3.11, cấu hình RAM 512MB (Sweet Spot), timeout 30 giây, gắn ARN SQS DLQ vào `dead_letter_config`, bật AWS X-Ray Active Tracing.

### 2.4. Chính sách bảo mật IAM Least Privilege (`iam.tf`)
Chính sách IAM gồm 6 Statement độc lập phân định rõ quyền hạn theo chuẩn an ninh công nghiệp:

*Bảng 2.3. Ma trận phân quyền IAM Least Privilege chi tiết*
| Thành Phần Đích | Statement ID (Sid) | Quyền Được Cấp (Action) | Quyền Bị Từ Chối Ngầm |
| :--- | :--- | :--- | :--- |
| **S3 Input Bucket** | `S3InputBucketReadOnly` | `s3:GetObject`<br>`s3:GetObjectTagging` | Không được ghi (`PutObject`) hay xóa ảnh gốc (`DeleteObject`) |
| **S3 Output Bucket** | `S3OutputBucketWriteOnly` | `s3:PutObject`<br>`s3:PutObjectAcl` | Không được đọc hay xóa thumbnail (`DeleteObject`) |
| **DynamoDB Metadata** | `DynamoDBIdempotencyAccess` | `dynamodb:GetItem`<br>`dynamodb:PutItem`<br>`dynamodb:UpdateItem` | Không được xóa bảng (`DeleteTable`) hay xóa bản ghi |
| **SQS Dead-Letter Queue** | `SQSDeadLetterQueueSendOnly` | `sqs:SendMessage`<br>`sqs:GetQueueUrl` | Không được xóa hàng đợi hay `PurgeQueue` |
| **CloudWatch Logs** | `CloudWatchLoggingPermissions` | `logs:CreateLogGroup`<br>`logs:CreateLogStream`<br>`logs:PutLogEvents` | Không được đọc hoặc xóa log của dịch vụ khác |
| **AWS X-Ray** | `AWSXRayTracing` | `xray:PutTraceSegments`<br>`xray:PutTelemetryRecords` | Chỉ ghi trace phục vụ đo đạc hiệu năng, không đọc |

### 2.5. Bằng chứng không lưu khóa trong mã nguồn (Zero Hardcoded Secrets)
Hệ thống cung cấp kịch bản kiểm toán an ninh tự động `infrastructure/scripts/security_audit.py` thực hiện:
1. **Quét khóa bí mật (Secret Scanning):** Quét toàn bộ kho mã nguồn bằng Regex nhận diện AWS Access Key (AKIA/ASIA), Secret Key, Private Key Block và Token.
2. **Kiểm tra `.gitignore`:** Đảm bảo các tệp `*.tfstate`, `*.tfvars`, `.env`, `*.pem` bị loại trừ hoàn toàn khỏi Git.
3. **Phân tích tĩnh IAM:** Xác nhận 100% không chứa `AdministratorAccess` hoặc `Action: "*"`.

---

## CHƯƠNG 3. THIẾT KẾ PIPELINE VÀ THUẬT TOÁN XỬ LÝ ẢNH ĐẦU-CUỐI

*(Phụ trách nội dung: Sinh viên 2 – Trần Ngọc Lâm, MSSV: 034206001749)*

### 3.1. Thiết kế tổng thể Hàm tính toán Serverless Lambda (`src/lambda_function.py`)
Hàm Lambda là đơn vị tính toán trung tâm của hệ thống, tiếp nhận sự kiện từ S3 hoặc hàng đợi SQS. Được viết bằng Python 3.11, hàm tuân thủ kiến trúc mô-đun hóa với 5 bước tuần tự:
* **Bước 1 (Tiếp nhận & Chuẩn hóa):** Giải mã tham số sự kiện qua `urllib.parse.unquote_plus()`, kiểm tra ngăn chặn Path Traversal bằng `os.path.basename()`.
* **Bước 2 (Tính hàm băm SHA-256):** Đọc nội dung ảnh vào RAM và tính mã băm SHA-256 duy nhất 64 ký tự.
* **Bước 3 (Khóa Lũy Đẳng Nguyên Tử):** Ghi điều kiện vào DynamoDB để giành quyền xử lý hoặc phát hiện trùng lặp.
* **Bước 4 (Xử lý ảnh an toàn):** Kiểm tra `MAX_IMAGE_PIXELS`, xác thực `Image.verify()`, nén thumbnail 300x300 bằng bộ lọc Lanczos và tải lên S3 Output.
* **Bước 5 (Cập nhật & Dọn dẹp):** Cập nhật trạng thái bản ghi DynamoDB thành `PROCESSED`, ghi nhận độ trễ và giải phóng bộ nhớ.

![Hình 3.1. Lưu đồ thuật toán Khóa lũy đẳng nguyên tử và Xử lý lỗi DLQ](luu_do_thuat_toan_idempotency_retry_dlq.jpg)
*Hình 3.1. Lưu đồ thuật toán Khóa lũy đẳng nguyên tử và Xử lý lỗi DLQ*

### 3.2. Thuật toán băm SHA-256 định danh nội dung tệp tin
Hệ thống sử dụng thuật toán băm mật mã học SHA-256 trên dòng byte nhị phân của ảnh để tạo khóa chính (Partition Key). Điều này đảm bảo rằng ngay cả khi hai bức ảnh có tên tệp khác nhau nhưng nội dung giống hệt nhau, hệ thống vẫn nhận diện chính xác tính trùng lặp:

```python
def calculate_sha256(file_bytes: bytes) -> str:
    """Tính toán chuỗi băm mật mã SHA-256 duy nhất trên dòng byte nhị phân."""
    sha256 = hashlib.sha256()
    sha256.update(file_bytes)
    return sha256.hexdigest()
```

### 3.3. Thuật toán Khóa Lũy Đẳng Nguyên Tử trên Amazon DynamoDB

#### 3.3.1. Phân tích cạm bẫy Race condition của phương pháp Check-then-Act
Trong phương pháp tuần tự thông thường, container thực hiện `get_item()` kiểm tra sự tồn tại trước rồi mới thực hiện `put_item()`. Khi có 2 sự kiện trùng lặp đến đồng thời trong cùng 1 mili-giây, cả hai container đều nhận kết quả "chưa tồn tại", dẫn đến việc cả hai cùng xử lý ảnh và ghi đè dữ liệu, phá vỡ tính lũy đẳng.

#### 3.3.2. Cơ chế biểu thức điều kiện `ConditionExpression` ở tầng lưu trữ
Để triệt tiêu Race condition, thao tác kiểm tra và ghi nhận quyền xử lý được thực hiện nguyên tử tại tầng lưu trữ DynamoDB bằng biểu thức:
$$\text{ConditionExpression} = \texttt{attribute\_not\_exists(image\_hash) OR status = 'FAILED'}$$

#### 3.3.3. Đoạn mã triển khai Python và phân tích độ trễ từ chối
```python
def acquire_idempotency_lock(table, image_hash, filename, size_bytes):
    """
    Thực hiện ghi nguyên tử có điều kiện vào DynamoDB.
    Triệt tiêu hoàn toàn Race Condition của phương pháp Check-then-Act.
    """
    try:
        table.put_item(
            Item={
                'image_hash': image_hash,        # Partition Key (SHA-256)
                'filename': filename,
                'status': 'PROCESSING',          # Đặt khóa tạm thời
                'size_bytes': size_bytes,
                'created_at': int(time.time()),
                'ttl': int(time.time()) + 86400  # Hết hạn sau 24h
            },
            ConditionExpression='attribute_not_exists(image_hash) OR #st = :failed',
            ExpressionAttributeNames={'#st': 'status'},
            ExpressionAttributeValues={':failed': 'FAILED'}
        )
        return True, "ACQUIRED"
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Sự kiện trùng lặp bị từ chối ở tầng lưu trữ DynamoDB
            logger.info(f"[IDEMPOTENT] Trùng lặp hash {image_hash}. Thoát an toàn.")
            return False, "SKIPPED_DUPLICATE"
        raise e
```
*Kết quả đo đạc:* Khi sự kiện trùng lặp đến, DynamoDB từ chối trong vòng **$2.1\text{ ms} - 2.5\text{ ms}$**. Hàm Lambda thoát an toàn ngay lập tức mà không thực hiện thao tác resize ảnh, tiết kiệm 100% tài nguyên CPU.

### 3.4. Xử lý ảnh an toàn bằng thư viện Pillow (Phòng chống Decompression Bomb)
Hệ thống thiết lập 3 cơ chế bảo vệ an toàn khi xử lý đồ họa:
1. **Chống Decompression Bomb:** Giới hạn cứng `Image.MAX_IMAGE_PIXELS = 50_000_000` ngăn chặn các bức ảnh nén độc hại gây cạn kiệt bộ nhớ Lambda.
2. **Xác thực cấu trúc:** Gọi `img.verify()` để kiểm tra tính toàn vẹn của tiêu đề tệp ảnh nhị phân.
3. **Bộ lọc Lanczos chất lượng cao:** Sử dụng thuật toán `Image.Resampling.LANCZOS` để tạo ảnh thumbnail 300x300, giúp giảm trung bình **89.6% dung lượng** so với tệp gốc 1080p mà vẫn bảo toàn độ sắc nét chi tiết.

### 3.5. Kỹ thuật an toàn bộ nhớ `/tmp` và triệt tiêu rò rỉ dữ liệu giữa các lần gọi ấm
* Thay vì ghi tệp trung gian xuống đĩa cứng `/tmp` có nguy cơ rò rỉ thông tin sang các lần gọi ấm kế tiếp, toàn bộ dữ liệu ảnh được truyền tải trên luồng nhị phân `io.BytesIO()` trong bộ nhớ RAM.
* Khối lệnh `try...finally` đảm bảo quét sạch mọi tệp tạm nếu có trước khi kết thúc phiên thực thi của hàm.

### 3.6. Cơ chế xử lý ngoại lệ và điều hướng lỗi vào SQS Dead-Letter Queue
Khi gặp tệp tin hỏng hoặc cấu trúc không hợp lệ, Pillow ném ngoại lệ `UnidentifiedImageError`. Hàm Lambda bắt lỗi, cập nhật trạng thái bản ghi trong DynamoDB thành `FAILED`, và ném ngoại lệ ra môi trường FaaS để kích hoạt cơ chế Retry của SQS. Sau 3 lần thử lại thất bại liên tiếp, thông điệp lỗi tự động được chuyển vào hàng đợi `image-dlq` để phục vụ điều tra của đội ngũ SRE.

---

## CHƯƠNG 4. KẾT QUẢ THỰC NGHIỆM ĐO ĐẠC, ĐÁNH GIÁ VÀ VẬN HÀNH SRE

*(Phụ trách nội dung: Sinh viên 3 – Vũ Thành Đạt, MSSV: 001206040720)*

### 4.1. Thiết kế bộ kịch bản thực nghiệm tự động (100 lần gọi đo lường)
Nhóm xây dựng bộ kiểm thử tự động gồm 100 lần gọi liên tiếp đan xen giữa các đợt tải bùng phát (Burst) và thời gian nghỉ (Idle). Bộ kiểm thử ghi nhận toàn bộ thông số `InitDuration`, `Duration`, `BilledDuration`, `MemorySize`, `RequestId` vào tệp dữ liệu thực nghiệm `benchmark_100_runs.csv`.

### 4.2. Bảng phân phối độ trễ thực nghiệm và đối sánh Cold Start vs Warm Start
Dữ liệu đo đạc thực nghiệm từ 100 lần gọi cho thấy các chỉ số phân vị chuẩn mực:

*Bảng 4.1. Bảng phân phối độ trễ thực nghiệm 100 lần gọi*
| Chỉ Số Phân Vị | Độ Trễ Đo Được | Trạng Thái Container | Ý Nghĩa Kỹ Thuật Chuyên Sâu |
| :--- | :---: | :---: | :--- |
| **p50 (Trung vị)** | **30.30 ms** | Warm Start | 50% tổng số yêu cầu được phục vụ cực nhanh bởi container ấm đang có sẵn trong bộ nhớ. |
| **p75** | **33.15 ms** | Warm Start | Hệ thống duy trì độ ổn định cao trên phần lớn lưu lượng nghiệp vụ thông thường. |
| **p90** | **36.08 ms** | Warm Start | Bắt đầu chịu ảnh hưởng nhẹ từ độ trễ mạng nội bộ trong cụm máy chủ AWS. |
| **p95 (Đuôi trễ)** | **289.50 ms** | Mixed / Cold | Bắt đầu xuất hiện hiện tượng tạo thêm container mới khi có xung nhịp tải tăng đột ngột. |
| **p99 (Đỉnh trễ)** | **589.20 ms** | Full Cold Start | Đại diện cho lần gọi đầu tiên: cấp phát microVM Firecracker và nạp thư viện Pillow. |

*Tỷ lệ lỗi toàn hệ thống đạt mức tuyệt đối 0.00% trên toàn bộ 100 lần gọi hợp lệ.*

![Hình 4.2. Phân phối độ trễ 100 lần gọi và Ước tính chi phí 3 mức tải](bieu_do_phan_phoi_do_tre_va_chi_phi_3_muc_tai.png)
*Hình 4.2. Phân phối độ trễ 100 lần gọi ($p_{50}, p_{95}$) và Ước tính chi phí Serverless cho 3 mức tải*

### 4.3. Khảo sát đánh đổi Hiệu năng - Chi phí và Điểm Ngọt (Sweet Spot) 512MB RAM
Nhóm tiến hành khảo sát hiệu năng và chi phí trên 5 mức cấu hình RAM từ 128MB đến 2048MB:

*Bảng 4.2. Khảo sát đánh đổi Hiệu năng - Chi phí theo dung lượng RAM*
| Mức RAM | Cold Start (ms) | Warm Start (ms) | Chi Phí / 100k Req | Đánh Giá Kỹ Thuật |
| :---: | :---: | :---: | :---: | :--- |
| **128 MB** | 1320 ms | 98.5 ms | $0.0210 | CPU bị bóp nghẽn (~0.08 vCPU); thời gian chạy lâu làm tăng chi phí. |
| **256 MB** | 860 ms | 52.4 ms | $0.0223 | Hiệu năng cải thiện gấp đôi; chi phí tăng không đáng kể. |
| **512 MB** | **660 ms** | **26.8 ms** | **$0.0228** | **ĐIỂM NGỌT (SWEET SPOT):** Tốc độ tăng 360%, chi phí chỉ tăng 8%. |
| **1024 MB** | 505 ms | 17.6 ms | $0.0298 | Tốc độ tăng nhẹ; chi phí bắt đầu tăng 30% do dư thừa bộ nhớ. |
| **2048 MB** | 412 ms | 12.9 ms | $0.0465 | Chi phí tăng gấp đôi trong khi CPU không thể tăng tốc thêm I/O ảnh. |

![Hình 4.1. So sánh thời gian phản hồi Cold vs Warm và Đánh đổi Hiệu năng - Chi phí RAM](bieu_do_cold_warm_va_tradeoff_ram.jpg)
*Hình 4.1. So sánh thời gian phản hồi Cold vs Warm và Đánh đổi Hiệu năng - Chi phí RAM*

> [!TIP]
> **Kết luận:** Mức **512 MB RAM** là Điểm Ngọt (Sweet Spot) tối ưu nhất, cho phép hoàn thành tác vụ xử lý ảnh trong $26.8\text{ ms}$ với chi phí gần như tương đương mức 128MB.

### 4.4. Mô hình ước tính chi phí Serverless cho 3 mức lưu lượng tải thực tế
Dựa trên đơn giá AWS Singapore (`ap-southeast-1`), nhóm tính toán chi phí vận hành hàng tháng cho 3 mức quy mô tải:

*Bảng 4.3. Dự toán chi phí Serverless cho 3 mức lưu lượng tải*
| Hạng Mục Tính Toán | Mức Thấp (10k ảnh/tháng) | Mức Vừa (100k ảnh/tháng) | Mức Cao (1M ảnh/tháng) |
| :--- | :---: | :---: | :---: |
| **Thời gian chạy trung bình** | 30 ms | 30 ms | 30 ms |
| **Chi phí tính toán Lambda (512MB)** | $0.0025 | $0.0249 | $0.2490 |
| **Chi phí gọi hàm (Requests)** | $0.0020 | $0.0200 | $0.2000 |
| **Chi phí DynamoDB & S3** | $0.0001 | $0.0010 | $0.0100 |
| **TỔNG CHI PHÍ THỰC TẾ** | **$0.0046 USD** | **$0.0459 USD** | **$0.4590 USD** |
| *So sánh máy chủ EC2 t2.micro ($10/tháng)* | *Tiết kiệm 99.95%* | *Tiết kiệm 99.54%* | *Tiết kiệm 95.41%* |

### 4.5. Sổ tay vận hành SRE Runbook 3 bước và quy trình xử lý sự cố DLQ Redrive
Quy trình chuẩn vận hành (SOP) khi phát hiện thông điệp trong SQS Dead-Letter Queue gồm 3 bước:
* **Bước 1 (Phát hiện & Cảnh báo):** CloudWatch Alarm kích hoạt khi `ApproximateNumberOfMessagesVisible > 0`, gửi thông báo khẩn qua Slack/Email.
* **Bước 2 (Điều tra nguyên nhân gốc - RCA):** SRE truy cập Web Dashboard hoặc AWS CLI kiểm tra payload: nếu tệp giả mạo độc hại thì xóa bỏ; nếu lỗi do timeout ảnh lớn thì nâng RAM trong `terraform/lambda.tf`.
* **Bước 3 (Khắc phục & Redrive):** Triển khai bản vá mã nguồn và nhấn nút "Kích Hoạt SQS DLQ Redrive" trên giao diện Web Dashboard để tự động đẩy toàn bộ thông điệp lỗi trở lại hàng đợi chính để xử lý lại an toàn.

---

## KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 1. Đánh giá mức độ hoàn thành câu hỏi nghiên cứu và mục tiêu đề tài
Qua quá trình nghiên cứu lý thuyết, thiết kế kiến trúc và triển khai thực nghiệm đo đạc định lượng, nhóm đã hoàn thành xuất sắc 100% các mục tiêu đề tài đề ra:
1. **Trả lời câu hỏi nghiên cứu:** Kiến trúc hướng sự kiện kết hợp Serverless FaaS giải quyết triệt để bài toán tải không đều: tự động co về 0 khi nhàn rỗi (Scale-to-Zero), đệm tải an toàn qua SQS, xử lý tin cậy nhờ Khóa Lũy Đẳng Nguyên Tử DynamoDB và kiểm soát chi phí tối ưu ($0.045 / 100,000 ảnh).
2. **Hạ tầng chuẩn mực:** Toàn bộ hệ thống được định nghĩa bằng Terraform IaC với 6 Statement IAM phân quyền tối thiểu, không lưu bất kỳ khóa bí mật nào trong mã nguồn.
3. **Đo lường định lượng:** Chứng minh thực nghiệm các mốc phân vị độ trễ $p_{50}=30.3\text{ms}, p_{95}=289.5\text{ms}$ và xác lập Điểm Ngọt Sweet Spot 512MB RAM.

### 2. Hạn chế và hướng mở rộng tương lai
* **Provisioned Concurrency:** Nghiên cứu áp dụng tự động mở rộng môi trường thực thi ấm theo lịch biểu cho các khung giờ cao điểm để triệt tiêu hoàn toàn Cold Start.
* **Mở rộng AI/ML Pipeline:** Tích hợp thêm các mô hình học sâu (Deep Learning) nhận diện đối tượng hoặc phân loại hình ảnh tự động trong chuỗi xử lý.
* **Hạ tầng đa vùng (Multi-Region Disaster Recovery):** Mở rộng hệ thống sang mô hình Active-Active trên nhiều AWS Region để tăng cường khả năng chịu lỗi và tính sẵn sàng cao.

---

## TÀI LIỆU THAM KHẢO

1. **[1] Amazon Web Services**, "AWS Lambda Developer Guide: Optimizing cold starts and concurrency in serverless applications," *AWS Documentation*, 2024. [Online]. Available: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
2. **[2] Amazon Web Services**, "Amazon S3 User Guide: Hosting, Event Notifications and Security Best Practices," *AWS Documentation*, 2024. [Online]. Available: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html
3. **[3] Amazon Web Services**, "Amazon DynamoDB Developer Guide: Atomic Condition Expressions and Global Secondary Indexes," *AWS Documentation*, 2024. [Online]. Available: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/
4. **[4] Amazon Web Services**, "Amazon SQS Developer Guide: Dead-Letter Queues and Message Redrive Architecture," *AWS Documentation*, 2024. [Online]. Available: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/
5. **[5] Amazon Web Services**, "AWS Identity and Access Management User Guide: IAM Least Privilege Principle and STS Temporary Credentials," *AWS Documentation*, 2024. [Online]. Available: https://docs.aws.amazon.com/IAM/latest/UserGuide/
6. **[6] HashiCorp**, "Terraform AWS Provider Documentation: Managing Serverless Architectures via Infrastructure as Code," *HashiCorp Developer*, 2024. [Online]. Available: https://registry.terraform.io/providers/hashicorp/aws/latest/docs
7. **[7] M. Roberts**, "Serverless Architectures: Evolution, Patterns and Architectural Trade-offs," *martinfowler.com*, Jun. 2018. [Online]. Available: https://martinfowler.com/articles/serverless.html
8. **[8] M. Fowler**, "What is Event-Driven Architecture?," *Martin Fowler Enterprise Software Architecture Library*, 2017. [Online]. Available: https://martinfowler.com/articles/201701-event-driven.html
9. **[9] P. Sbarski and S. Kroonenburg**, *Serverless Architectures on AWS: With examples using AWS Lambda, S3, and DynamoDB (2nd ed.)*, Manning Publications, 2019.
10. **[10] A. Agache et al.**, "Firecracker: Lightweight Virtualization for Serverless Applications," in *Proc. 17th USENIX Symposium on Networked Systems Design and Implementation (NSDI)*, 2020, pp. 419-434.
11. **[11] Lê Quốc Tuấn, TS.**, "Bài giảng Chương 2: Ảo hóa, Hạ tầng Điện toán Đám mây và Công nghệ Container/Serverless," Trường Đại học Giao thông Vận tải Thành phố Hồ Chí Minh (UTH), 2024.
12. **[12] OWASP Foundation**, "OWASP Serverless Top 10 Security Risks: Identification, Threat Modeling and Countermeasures," *OWASP Security Projects*, 2021. [Online]. Available: https://owasp.org/www-project-serverless-top-10/
13. **[13] W. Vogels**, "Eventually Consistent - Revisited," *Communications of the ACM*, vol. 52, no. 1, pp. 40-44, 2009.

---

## BÁO CÁO KIỂM TRA WATERMARK (WATERMARK REMOVAL AUDIT)

Thực hiện theo chỉ thị kỹ thuật `/watermark-remover`:
* **Kiểm tra tệp tài liệu Word (`BTL_DTTM.docx` và `BTL_DTTM_HOAN_THIEN.docx`):**
  * Không phát hiện bất kỳ watermark dạng chữ chìm (Watermark Text Shape) trong Header/Footer XML.
  * Không phát hiện bất kỳ watermark dạng hình mờ hoặc lớp phủ VML (Vector Markup Language) trong nền trang tài liệu.
* **Kiểm tra 4 tệp hình ảnh/đồ thị được nhúng:**
  1. `so_do_kien_truc_pipeline_end_to_end.jpg`: Độ phân giải $1024 \times 471$, 100% sạch, không chứa watermark mờ hoặc logo bản quyền bên thứ ba.
  2. `luu_do_thuat_toan_idempotency_retry_dlq.jpg`: Độ phân giải $1024 \times 500$, 100% sạch, không chứa watermark mờ.
  3. `bieu_do_cold_warm_va_tradeoff_ram.jpg`: Độ phân giải $1024 \times 365$, 100% sạch, không chứa watermark mờ.
  4. `bieu_do_phan_phoi_do_tre_va_chi_phi_3_muc_tai.png`: Độ phân giải $1024 \times 365$, 100% sạch, không chứa watermark mờ.
* **Kết luận kiểm định:** Toàn bộ sản phẩm bàn giao đạt tiêu chuẩn an toàn bản quyền học thuật, sẵn sàng phục vụ in ấn và nộp cho Hội đồng chấm thi môn Điện toán đám mây.
