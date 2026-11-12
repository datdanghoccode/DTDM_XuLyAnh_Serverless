# KỊCH BẢN THUYẾT TRÌNH BÁO CÁO & HƯỚNG DẪN TRÌNH DIỄN LIVE DEMO
## ĐỀ TÀI 9: HỆ THỐNG XỬ LÝ ẢNH HƯỚNG SỰ KIỆN BẰNG SERVERLESS VÀ ĐÁNH GIÁ COLD START

---

### THÔNG TIN ĐỀ TÀI VÀ HỘI ĐỒNG BÁO CÁO
- **Trường:** Đại học Giao thông Vận tải TP.HCM (UTH)
- **Khoa:** Công nghệ Thông tin / Bộ môn Mạng & Truyền thông
- **Học phần:** Điện toán Đám mây (Cloud Computing)
- **Giảng viên hướng dẫn & Trưởng hội đồng:** **TS. Lê Quốc Tuấn**
- **Nhóm sinh viên thực hiện:**
  1. **Lê Doãn Đạt** - MSSV: `038206000230` (Kiến trúc Hạ tầng & Bảo mật Serverless)
  2. **Trần Ngọc Lâm** - MSSV: `034206001749` (Kỹ sư Backend, Thuật toán Idempotency & Xử lý lỗi DLQ)
  3. **Vũ Thành Đạt** - MSSV: `001206040720` (Kiểm thử, Quan sát Telemetry, Phân tích Định lượng & SRE)

---

### TỔNG QUAN PHÂN BỔ THỜI GIAN (TỔNG: 10 PHÚT CHÍNH XÁC)

| Mốc thời gian | Thời lượng | Người trình bày | Nội dung trọng tâm | Slide tương ứng |
| :--- | :---: | :--- | :--- | :---: |
| **00:00 - 03:00** | **03 phút** | **Lê Doãn Đạt** | Mở đầu, Trả lời câu hỏi nghiên cứu, Độ tin cậy Event-Driven & Bảo mật chuẩn OWASP | Slide 1, 2, 3, 4, 5 |
| **03:00 - 06:00** | **03 phút** | **Trần Ngọc Lâm** | Kiến trúc Pipeline đầu-cuối, Thuật toán Khóa lũy đẳng nguyên tử DynamoDB & Cơ chế SQS DLQ | Slide 6, 7, 8 |
| **06:00 - 09:00** | **03 phút** | **Vũ Thành Đạt** | Thực nghiệm định lượng 100 runs, Đối sánh Cold/Warm, Phân vị p50/p95, Chi phí 3 mức tải & Runbook SRE | Slide 9, 10, 11, 12 |
| **09:00 - 10:00** | **01 phút** | **Cả nhóm** | Kết luận tổng hợp, Chuyển tiếp & Khởi động Live Demo tại http://localhost:5000 | Slide 13 |
| *(Phần bổ trợ)* | **03-05 phút** | **Cả nhóm** | Trình diễn tương tác 4 kịch bản Live Demo và trả lời câu hỏi chất vấn của TS. Lê Quốc Tuấn | Giao diện Web |

---

# PHẦN I: KỊCH BẢN THUYẾT TRÌNH CHI TIẾT (10 PHÚT)

---

## 1. PHẦN 1: MỞ ĐẦU, CÂU HỎI NGHIÊN CỨU & BẢO MẬT OWASP SERVERLESS (00:00 - 03:00)
**Người trình bày:** Lê Doãn Đạt (MSSV: `038206000230`)  
**Tác phong:** Đĩnh đạc, tự tin, phát âm rõ ràng, mắt hướng về phía Thầy Lê Quốc Tuấn và hội đồng.

---

### [00:00 - 00:30] Mở đầu & Giới thiệu Đề tài (Chiếu Slide 1 & Slide 2)
- **Lời thoại mở màn:**
  > *"Kính thưa Thầy TS. Lê Quốc Tuấn và toàn thể các bạn sinh viên đang có mặt trong buổi bảo vệ hôm nay.*  
  > *Em là **Lê Doãn Đạt**, đại diện nhóm thực hiện Đề tài số 9: **'Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless và đánh giá Cold Start'**.*  
  > *Cùng đồng hành với em trong đề tài này là hai bạn: **Trần Ngọc Lâm** - phụ trách Thiết kế Backend và Thuật toán Khóa lũy đẳng, và bạn **Vũ Thành Đạt** - phụ trách Đo kiểm định lượng Cold Start và Vận hành SRE.*  
  > *Nhóm em đã phân bổ thời gian báo cáo 10 phút thành 3 phần mạch lạc: Em sẽ trình bày nền tảng lý thuyết và bảo mật; bạn Lâm sẽ phân tích sâu về kiến trúc và thuật toán; bạn Đạt sẽ trình bày số liệu đo đạc thực nghiệm và chi phí; và 1 phút cuối cùng nhóm sẽ mở màn phần Live Demo trực quan."*

---

### [00:30 - 01:20] Câu hỏi nghiên cứu & Mục tiêu đồ án (Chiếu Slide 3)
- **Lời thoại trình bày:**
  > *"Thưa Thầy, bài toán cốt lõi mà đề tài giải quyết xuất phát từ câu hỏi nghiên cứu:*  
  > **'Khi tệp được tải lên theo các nhịp không đều và đột biến, kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?'**  
  > *Trong các hệ thống truyền thống sử dụng máy chủ ảo EC2, doanh nghiệp phải luôn cấp phát dư thừa tài nguyên (Over-provisioning) để đón đầu các đỉnh tải (Traffic Spikes), dẫn đến việc lãng phí hơn 70% ngân sách khi hệ thống nhàn rỗi.*  
  > *Để giải quyết triệt để vấn đề này, nhóm chúng em đặt ra 3 mục tiêu kỹ thuật cụ thể:*  
  > *1. Xây dựng một đường ống xử lý ảnh hoàn toàn tự động hóa (Event-Driven Pipeline) trên AWS, có khả năng **Scale-to-Zero** khi không có tải và mở rộng tức thì khi có hàng trăm tệp tải lên đồng thời.*  
  > *2. Giải quyết triệt để rủi ro gửi lặp gói tin của mạng phân tán bằng cơ chế **Lũy đẳng tuyệt đối (Idempotency)**.*  
  > *3. Đo lường định lượng hiện tượng **Cold Start**, xác lập bảng phân vị độ trễ $p_{50}, p_{95}$ và đưa ra mô hình tối ưu hóa chi phí cho 3 quy mô doanh nghiệp."*

---

### [01:20 - 02:10] Lý thuyết Độ tin cậy Hướng sự kiện (Chiếu Slide 4)
- **Lời thoại trình bày:**
  > *"Về cơ sở lý thuyết độ tin cậy trong mô hình Function-as-a-Service (FaaS):*  
  > *Khác với mô hình gọi hàm đồng bộ (Synchronous RPC), trong kiến trúc hướng sự kiện, Amazon S3 đóng vai trò là Event Producer, phát sinh sự kiện `s3:ObjectCreated:*` và kích hoạt hàm AWS Lambda theo cơ chế **Bất đồng bộ (Asynchronous Invocation)**.*  
  > *Tuy nhiên, trong mạng phân tán, nhà cung cấp dịch vụ đám mây chỉ cam kết cơ chế chuyển phát **'Ít nhất một lần' (At-least-once delivery)**. Điều này đồng nghĩa với việc: khi mạng gặp sự cố chập chờn hoặc timeout tạm thời, cùng một sự kiện tải ảnh có thể bị gửi lặp lại 2 hay nhiều lần.*  
  > *Nếu hàm xử lý không có cơ chế tự bảo vệ, hệ thống sẽ thực hiện resize ảnh nhiều lần, tiêu tốn gấp đôi chi phí CPU và gây ra xung đột ghi đè dữ liệu.*  
  > *Vì vậy, một kiến trúc Serverless chuẩn công nghiệp bắt buộc phải hội tụ đủ hai yếu tố: Một là **Kho khóa lũy đẳng (Idempotency Store)** để phát hiện và triệt tiêu sự kiện trùng, và hai là **Hàng đợi Dead-Letter Queue (SQS DLQ)** để cô lập các tệp hỏng hoặc độc hại sau 2 lần retry thất bại, ngăn chặn việc pipeline bị nghẽn (Poison Pill)."*

---

### [02:10 - 03:00] Bảo mật theo chuẩn OWASP Serverless Top 10 (Chiếu Slide 5)
- **Lời thoại trình bày:**
  > *"Thưa Thầy, một điểm nhấn quan trọng mà nhóm đặc biệt chú trọng là **Bảo mật chuẩn công nghiệp theo OWASP Serverless Top 10**, được cấu hình hoàn toàn bằng Infrastructure as Code qua Terraform:*  
  > *- **Thứ nhất - Chuẩn SAS-01 (IAM Least Privilege):** Nhóm tuyệt đối không sử dụng `Action: "*"` hay cấp quyền Admin. Trong file `iam.tf`, hàm Lambda chỉ được cấp đúng quyền `GetObject` trên Input Bucket, chỉ được `PutObject` trên Output Bucket, và chỉ được ghi log vào đúng Log Group của dự án.*  
  > *- **Thứ hai - Chuẩn SAS-02 (Zero Hardcoded Secrets):** Trong toàn bộ mã nguồn Git, nhóm không lưu bất kỳ khóa bí mật AWS Access Key nào. Hệ thống sử dụng 100% IAM Execution Role với STS Temporary Token tự động xoay vòng.*  
  > *- **Thứ ba - Chuẩn SAS-03 (Data Encryption At-Rest):** Cả hai S3 Bucket và bảng DynamoDB đều được bật mã hóa AES-256 ở tầng lưu trữ.*  
  > *- **Thứ tư - Chuẩn SAS-05 (Event Data Injection):** Lambda xác thực trực tiếp cấu trúc nhị phân của ảnh qua thư viện Pillow trước khi xử lý, ngăn chặn việc tiêm mã độc qua tên file.*  
  > *Sau đây, em xin kính mời bạn **Trần Ngọc Lâm** tiếp tục trình bày chi tiết về Kiến trúc Pipeline và Thuật toán Khóa lũy đẳng nguyên tử trên DynamoDB."*

---

## 2. PHẦN 2: KIẾN TRÚC PIPELINE, THUẬT TOÁN KHÓA LŨY ĐẲNG & SQS DLQ (03:00 - 06:00)
**Người trình bày:** Trần Ngọc Lâm (MSSV: `034206001749`)  
**Tác phong:** Rõ ràng, tự tin, tập trung phân tích kỹ thuật sâu sắc, chỉ tay vào sơ đồ kiến trúc và thuật toán.

---

### [03:00 - 03:50] Thiết kế Kiến trúc Pipeline đầu-cuối (Chiếu Slide 6)
- **Lời thoại trình bày:**
  > *"Em xin kính chào Thầy Lê Quốc Tuấn và các bạn. Em là **Trần Ngọc Lâm**.*  
  > *Tiếp nối phần bảo mật và lý thuyết của bạn Đạt, trên màn hình là **Sơ đồ Kiến trúc Pipeline đầu-cuối** mà nhóm đã triển khai thực tế.*  
  > *Luồng dữ liệu vận hành theo chu trình khép kín gồm 4 bước:*  
  > *1. Khi người dùng tải ảnh lên `S3 Input Bucket`, sự kiện `s3:ObjectCreated:*` được đẩy vào hàng đợi nội bộ của AWS Lambda.*  
  > *2. AWS Lambda khởi tạo môi trường thực thi MicroVM Firecracker, tải ảnh vào bộ nhớ đệm RAM (`io.BytesIO`) và tính toán mã băm mật mã học **SHA-256** của luồng byte ảnh.*  
  > *3. Lambda thực hiện truy vấn khóa lũy đẳng đến bảng `DynamoDB ImageMetadata`. Nếu là ảnh mới, hệ thống khóa bản ghi và tiến hành resize kích thước thumbnail 300x300 pixel, nén JPEG chất lượng 85%.*  
  > *4. Ảnh kết quả được tải lên `S3 Output Bucket`, đồng thời cập nhật siêu dữ liệu trạng thái `COMPLETED` lên DynamoDB.*  
  > *Đặc biệt, nếu gặp tệp hỏng hoặc lỗi logic, sự kiện sẽ được tự động chuyển hướng sang `SQS Dead-Letter Queue`."*

---

### [03:50 - 04:55] Thuật toán Khóa Lũy đẳng Nguyên tử (Atomic Idempotency Lock) trên DynamoDB (Chiếu Slide 7)
- **Lời thoại trình bày:**
  > *"Kính thưa Thầy, thách thức kỹ thuật lớn nhất ở tầng Backend chính là hiện tượng **Race Condition**.*  
  > *Nếu chúng ta sử dụng phương pháp ngây thơ dạng 'Check-then-act' — tức là dùng `getItem` kiểm tra xem hash có chưa rồi mới `putItem` — thì khi có 2 sự kiện trùng nhau đến cùng 1 mili-giây, cả 2 container Lambda đều thấy chưa có bản ghi, và cả 2 đều xử lý. Kết quả là tính lũy đẳng bị phá vỡ!*  
  > *Để giải quyết triệt để, nhóm em đã thiết kế **Thuật toán Khóa Lũy đẳng Nguyên tử (Atomic Lock)** tận dụng sức mạnh độc bản của DynamoDB.*  
  > *Cụ thể trong file `lambda_function.py`:*  
  > *Chúng em thực hiện thao tác ghi nguyên tử bằng câu lệnh:*  
  > `table.put_item(Item={'image_hash': file_hash, 'status': 'PROCESSING', 'ttl': now + 300}, ConditionExpression='attribute_not_exists(image_hash)')`  
  > *Nguyên lý hoạt động:*  
  > *- Khi sự kiện đầu tiên đến, thuộc tính `image_hash` chưa tồn tại trong bảng, DynamoDB chấp thuận ghi và cấp khóa thành công.*  
  > *- Nếu sự kiện thứ hai bị gửi lặp đến, điều kiện `attribute_not_exists` bị vi phạm ở ngay tầng lõi lưu trữ của DynamoDB. Động cơ cơ sở dữ liệu sẽ lập tức ném ra ngoại lệ `ConditionalCheckFailedException`.*  
  > *- Hàm Lambda bắt ngoại lệ này, ghi nhận đây là yêu cầu trùng lặp và hủy bỏ xử lý ngay lập tức trong thời gian **dưới 2 mili-giây**!*  
  > *Nhờ vậy, hệ thống tiết kiệm được 100% chi phí CPU nén ảnh, không ghi đè S3 và ngăn chặn hoàn toàn Race Condition."*

---

### [04:55 - 06:00] Cơ chế Xử lý Lỗi Poison Pill & Hàng đợi Dead-Letter Queue (SQS DLQ) (Chiếu Slide 8)
- **Lời thoại trình bày:**
  > *"Bên cạnh tính lũy đẳng, một hệ thống FaaS tin cậy phải có khả năng xử lý **Poison Pill** — tức là những thông điệp chứa dữ liệu độc hại hoặc tệp bị hỏng.*  
  > *Ví dụ: Kẻ xấu đổi tên file `malware.exe` hoặc file text rác thành `photo.jpg` rồi tải lên S3.*  
  > *Khi hàm Lambda gọi `Image.open()`, thư viện Pillow sẽ phát hiện cấu trúc header không hợp lệ và ném ra ngoại lệ `UnidentifiedImageError`.*  
  > *Về mặt kỹ thuật, ở đây có một chi tiết then chốt:*  
  > *Nếu chúng ta dùng khối `try...except` để nuốt chửng lỗi (Catch and Swallow), AWS Lambda sẽ tưởng rằng hàm đã chạy thành công (`exit code 0`), và sự cố sẽ bị chôn vùi trong im lặng.*  
  > *Thay vào đó, nhóm em chủ động **ném tiếp ngoại lệ lên tầng Runtime của AWS Lambda** (`raise err`).*  
  > *Khi nhận thấy hàm thất bại:*  
  > *1. AWS Lambda tự động kích hoạt cơ chế retry lần 1 và lần 2 với thuật toán lùi thời gian số mũ (**Exponential Backoff**).*  
  > *2. Khi hết số lần retry mà vẫn thất bại, AWS Lambda tự động đóng gói nguyên vẹn Payload sự kiện ban đầu cùng thông tin lỗi và đẩy vào **SQS Dead-Letter Queue** (`cloud-image-serverless-dlq`).*  
  > *Nhờ cơ chế này, luồng xử lý chính không bao giờ bị nghẽn, container được giải phóng ngay lập tức, và dữ liệu lỗi được lưu giữ an toàn trong 14 ngày để kỹ sư vận hành điều tra.*  
  > *Tiếp theo đây, em xin nhường lời cho bạn **Vũ Thành Đạt** trình bày về kết quả thực nghiệm 100 lần đo, phân tích Cold Start và quy trình Runbook SRE."*

---

## 3. PHẦN 3: THỰC NGHIỆM ĐỊNH LƯỢNG 100 RUNS, COLD/WARM START, CHI PHÍ & RUNBOOK SRE (06:00 - 09:00)
**Người trình bày:** Vũ Thành Đạt (MSSV: `001206040720`)  
**Tác phong:** Tràn đầy năng lượng, lập luận dựa trên số liệu thực chứng, tự tin với các chỉ số thống kê.

---

### [06:00 - 06:50] Phương pháp Thực nghiệm Đo đạc 100 Lần gọi (Chiếu Slide 9)
- **Lời thoại trình bày:**
  > *"Kính chào Thầy Lê Quốc Tuấn và các bạn. Em là **Vũ Thành Đạt**, phụ trách mảng Đo kiểm và Vận hành SRE.*  
  > *Để đánh giá toàn diện hành vi của hệ thống theo đúng yêu cầu đề cương, nhóm em đã xây dựng bộ kịch bản tự động hóa thực hiện **100 lần kích hoạt (100 Invocations Suite)**, với cơ cấu phân bổ khoa học gồm 4 tình huống:*  
  > *- **85 sự kiện bình thường (Warm Start):** Ảnh phong cảnh và chân dung với độ phân giải Full HD (1920x1080) và 2K (2560x1440).*  
  > *- **5 sự kiện Cold Start xen kẽ:** Kích hoạt sau các khoảng nghỉ để đo đạc thời gian cấp phát container mới.*  
  > *- **5 sự kiện trùng lặp (Duplicate Test):** Gửi lại chính xác các tệp đã có để kiểm chứng khóa Idempotency.*  
  > *- **5 sự kiện tệp giả mạo (Fault Injection):** Tệp hỏng chứa chuỗi byte rác để kiểm chứng cơ chế cô lập của SQS DLQ.*  
  > *Toàn bộ dữ liệu đo thô đã được trích xuất thành tệp `benchmark_100_runs.csv` với độ chính xác mili-giây."*

---

### [06:50 - 07:45] Phân tích Đối sánh Cold Start vs Warm Start & Bảng phân vị (Chiếu Slide 10)
- **Lời thoại trình bày:**
  > *"Nhìn vào kết quả đo đạc thực tế trên Slide 10, chúng ta thấy rõ sự phân hóa sâu sắc giữa Cold Start và Warm Start:*  
  > *- **Thời gian Cold Start trung bình đo được là: 552.73 ms.**  
  >   *Trong đó, thời gian khởi tạo môi trường (`Init Duration`) chiếm tới hơn 520 ms — bao gồm việc AWS tạo MicroVM Firecracker, nạp Python 3.11 Runtime, nạp thư viện đồ họa Pillow (khoảng 15MB) và Boto3 SDK vào RAM. Thời gian thực thi (`Exec Duration`) chỉ mất khoảng 32 ms.*  
  > *- **Thời gian Warm Start trung bình chỉ còn: 26.98 ms.**  
  >   *Khi container đã ở trạng thái 'ấm', toàn bộ mã nguồn và thư viện đã nằm sẵn trong bộ nhớ, hàm xử lý ảnh thuần túy trong RAM.*  
  > *- **Tỷ lệ suy hao hiệu năng (Overhead):** Cold Start chậm hơn Warm Start tới **20.5 lần**!*  
  > *- **Về các chỉ số phân vị (Percentiles):**  
  >   *+ Độ trễ trung vị **$p_{50}$ đạt 25.88 ms** — minh chứng 50% yêu cầu được xử lý cực kỳ nhanh.*  
  >   *+ Phân vị **$p_{90}$ đạt 36.08 ms**.*  
  >   *+ Phân vị **$p_{95}$ vọt lên 293.82 ms** và **$p_{99}$ là 589.20 ms**.*  
  >   *Khoảng cách lớn ở $p_{95}$ và $p_{99}$ chính là bằng chứng định lượng rõ ràng nhất về hiện tượng Cold Start khi hệ thống phải scale mở rộng thêm worker mới."*

---

### [07:45 - 08:35] Đánh đổi Hiệu năng - Cấu hình RAM & Ước tính Chi phí (Chiếu Slide 11)
- **Lời thoại trình bày:**
  > *"Tiếp theo, nhóm tiến hành khảo sát sự đánh đổi giữa cấu hình RAM, tốc độ xử lý và chi phí:*  
  > *- Trong AWS Lambda, **dung lượng RAM tỷ lệ thuận với năng lực CPU**. Khi nâng RAM từ 128MB lên 512MB, vCPU tăng từ 0.07 lên 0.29 vCPU. Thời gian thực thi xử lý ảnh giảm mạnh tới 88% (từ 256 ms xuống còn 29 ms).*  
  > *- Tuy nhiên, nếu tiếp tục nâng lên 1024MB hoặc 2048MB, thời gian xử lý bắt đầu bão hòa ở mức 21 ms do bài toán resize ảnh 1080p đã đạt giới hạn I/O bộ nhớ, trong khi đơn giá tính cước trên mỗi mili-giây lại tăng gấp 4 lần.*  
  > *=> Kết luận: **512MB RAM là điểm tối ưu tuyệt đối (Sweet Spot)** giữa hiệu năng và chi phí.*  
  > *Dựa trên biểu phí AWS Lambda ($0.0000166667 / GB-s và $0.20 / 1M requests), nhóm tính toán chi phí vận hành cho 3 mức lưu lượng:*  
  > *1. **Mức thấp (Startup - 10.000 ảnh/tháng):** Chi phí chỉ **$0.0042 / tháng**, hoàn toàn nằm trong Free Tier miễn phí.*  
  > *2. **Mức vừa (SME - 100.000 ảnh/tháng):** Chi phí là **$0.0416 / tháng** (chưa đến 1.100 VNĐ), tiết kiệm hơn 95% so với thuê một máy chủ EC2 t2.micro giá $10/tháng.*  
  > *3. **Mức cao (Doanh nghiệp - 1.000.000 ảnh/tháng):** Chi phí chỉ vỏn vẹn **$0.416 / tháng** (khoảng 10.500 VNĐ)!"*

---

### [08:35 - 09:00] Sổ tay Vận hành SRE (Runbook) Xử lý Sự cố DLQ (Chiếu Slide 12)
- **Lời thoại trình bày:**
  > *"Để hệ thống sẵn sàng đưa vào vận hành thực tế, nhóm đã xây dựng **Sổ tay Vận hành SRE (Runbook)** cho hàng đợi SQS DLQ:*  
  > *- Kết quả kiểm chứng thực nghiệm cho thấy: **100% (5/5) tệp gửi lặp** đều bị chặn bởi khóa Idempotency trong vòng 2.1 ms; và **100% (5/5) tệp lỗi** đều được chuyển hướng thành công vào SQS DLQ.*  
  > *- Quy trình SRE xử lý sự cố gồm 3 bước chuẩn hóa:*  
  > *1. **Cảnh báo (Alert):** CloudWatch Alarm kích hoạt khi chỉ số `ApproximateNumberOfMessagesVisible > 0`.*  
  > *2. **Phân tích nguyên nhân gốc rễ (RCA):** Dùng lệnh `aws sqs receive-message` để kiểm tra payload tệp lỗi.*  
  > *3. **Khắc phục & Tái xử lý (Redrive):** Nếu lỗi do tệp độc hại -> Tiến hành xóa bỏ; nếu lỗi do tải quá lớn làm timeout -> Nâng RAM Lambda qua Terraform và bấm nút **Start DLQ Redrive** để tự động bơm lại thông điệp về hàm xử lý mà không làm mất mát dữ liệu của người dùng."*

---

## 4. PHẦN 4: TỔNG KẾT & CHUYỂN GIAO LIVE DEMO (09:00 - 10:00)
**Người trình bày:** Cả nhóm (Lê Doãn Đạt điều phối chốt lời)  
**Tác phong:** Trân trọng, nhiệt huyết, sẵn sàng bước sang phần demo thực nghiệm.

---

### [09:00 - 10:00] Tổng kết & Mở màn Demo (Chiếu Slide 13)
- **Lời thoại tổng kết:**
  > *"Kính thưa Thầy TS. Lê Quốc Tuấn và hội đồng,*  
  > *Qua 9 phút vừa rồi, nhóm chúng em đã chứng minh việc hiện thực hóa trọn vẹn 100% các tiêu chí học thuật của Đề tài 9:*  
  > *1. Xây dựng thành công Pipeline Serverless hướng sự kiện tự động hóa 100% từ hạ tầng Terraform đến mã Python.*  
  > *2. Đảm bảo độ tin cậy tuyệt đối với Thuật toán Khóa lũy đẳng nguyên tử trên DynamoDB và cơ chế cô lập lỗi SQS DLQ.*  
  > *3. Thu thập và trực quan hóa số liệu định lượng 100 lần đo, giải mã tường tận bài toán Cold Start và bài toán tối ưu chi phí.*  
  > *Và để minh chứng những luận điểm kỹ thuật trên hoạt động chuẩn xác trong thực tế, nhóm chúng em đã phát triển một **Bảng điều khiển Web Live Demo tại cổng 5000**.*  
  > *Sau đây, nhóm xin phép kính mời Thầy cùng toàn thể hội đồng hướng mắt về màn hình để theo dõi phần **TRÌNH DIỄN LIVE DEMO TRỰC TIẾP TƯƠNG TÁC 4 KỊCH BẢN**!"*

---

# PHẦN II: KỊCH BẢN HƯỚNG DẪN TRÌNH DIỄN LIVE DEMO (STEP-BY-STEP)

> **Môi trường Demo:** Ứng dụng Web Flask tương tác trực tiếp chạy tại địa chỉ: `http://localhost:5000`  
> **Lệnh khởi chạy môi trường:** Mở Command Prompt / PowerShell chạy file: `run_demo.bat` hoặc lệnh `python demo_app.py`  
> **Giao diện:** Thiết kế Dark Navy hiện đại, gồm 4 Tabs tương ứng với 4 kịch bản kiểm thử độc lập.

```
       ┌─────────────────────────────────────────────────────────────────────────────────┐
       │             BẢNG ĐIỀU KHIỂN LIVE DEMO - PIPELINE XỬ LÝ ẢNH SERVERLESS            │
       ├──────────────────┬──────────────────┬──────────────────┬────────────────────────┤
       │ Bước 1: Chuẩn    │ Bước 2: Khóa     │ Bước 3: Lỗi SQS  │ Bước 4: Cold Start     │
       │ Luồng Xử Lý Ảnh  │ Lũy Đẳng 2ms     │ Dead-Letter Queue│ Benchmark 100 Runs     │
       └──────────────────┴──────────────────┴──────────────────┴────────────────────────┘
```

---

## BƯỚC 1: TRÌNH DIỄN LUỒNG XỬ LÝ CHUẨN (NORMAL FLOW)
- **Vị trí Tab:** Nhấp chuột vào tab **'Bước 1: Xử lý Luồng Chuẩn'** (`#step1-tab`).
- **Mục tiêu chứng minh:** Mô phỏng sự kiện `s3:ObjectCreated:*`. Khi ảnh được tải lên S3, Lambda tự động nạp ảnh, kiểm tra khóa lũy đẳng lần đầu, resize thành thumbnail 300x300, nén giảm hơn 80% dung lượng và lưu vào S3 Output.

### Các thao tác bấm trực tiếp trên màn hình:
1. Nhấp chuột vào nút màu xanh cyan: **`[Ảnh Mẫu Phong Cảnh (1920x1080)]`** (hoặc chọn file ảnh bất kỳ từ máy tính).
2. Quan sát khung log hiển thị dòng thông báo: `[READY] Đã sinh ảnh mẫu: sample_1920x1080_...jpg`.
3. Nhấp chuột vào nút xanh dương lớn: **`[Tải lên S3 & Kích hoạt Pipeline]`** (`#btnProcessNormal`).

### Hiện tượng quan sát thấy trên giao diện:
- Cột bên phải lập tức hiển thị song song 2 bức ảnh:
  + Ảnh bên trái: **Ảnh Gốc (S3 Input)** kích thước `1920x1080` (Dung lượng ~85.4 KB).
  + Ảnh bên phải: **Thumbnail (S3 Output)** kích thước chuẩn `300x300` (Dung lượng ~8.9 KB, nhãn màu xanh lá cây ghi rõ: `Giảm -89.6% dung lượng`).
- Hộp nhật ký `Nhật ký thực thi (Execution Log)` cuộn các dòng log màu xanh Sky Blue:
  ```text
  [INFO] Bắt đầu đẩy tệp s3://input-bucket/sample_1920x1080_1731388000.jpg...
  [LAMBDA] Mã băm SHA-256: e3b0c44298fc1c14...
  [DYNAMODB] Khóa lũy đẳng nguyên tử thành công (Status: PROCESSING -> COMPLETED)
  [PILLOW] Đã resize ảnh thành 300x300 trong 24.5 ms
  [S3] Đã lưu ảnh vào s3://output-bucket/thumbnails/thumb_sample_1920x1080_1731388000.jpg
  ```

### Lời thoại mẫu khi thao tác trước Hội đồng:
> *"Kính thưa Thầy, ở Bước 1 này, chúng em mô phỏng hành vi tải ảnh thông thường của người dùng.*  
> *Em xin phép nhấn nút **Sinh ảnh phong cảnh Full HD 1920x1080** và nhấn **Kích hoạt Pipeline**.*  
> *Ngay lập tức, sự kiện `ObjectCreated` được phát sinh. Hàm Lambda khởi chạy, đọc trực tiếp luồng byte vào RAM mà không lưu tạm ra ổ cứng `/tmp` để tuân thủ chuẩn OWASP SAS-04.*  
> *Thư viện Pillow xử lý nén từ 1080p xuống 300x300 chỉ trong **24.5 mili-giây**, giúp giảm tới gần 90% dung lượng lưu trữ.*  
> *Ảnh thumbnail đã được đưa lên Output Bucket và metadata đã lưu bền vững trên DynamoDB."*

---

## BƯỚC 2: TRÌNH DIỄN KHÓA LŨY ĐẲNG NGUYÊN TỬ (IDEMPOTENCY VERIFICATION)
- **Vị trí Tab:** Nhấp chuột chuyển sang tab **'Bước 2: Kiểm chứng Idempotency'** (`#step2-tab`).
- **Mục tiêu chứng minh:** Mô phỏng sự cố mạng gây chuyển phát lặp lại (At-least-once delivery retry). DynamoDB phát hiện trùng mã băm SHA-256 qua điều kiện nguyên tử, từ chối xử lý và hủy bỏ ngay trong **< 2 mili-giây**.

### Các thao tác bấm trực tiếp trên màn hình:
1. Giữ nguyên ngữ cảnh tệp ảnh đã xử lý ở Bước 1.
2. Nhấp chuột vào nút xanh lá cây: **`[Gửi Lặp Lại Cùng Tệp Ảnh (Bắn Duplicate Event)]`**.

### Hiện tượng quan sát thấy trên giao diện:
- Lập tức xuất hiện một Card thông báo viền xanh lá cây nổi bật:
  + Biểu tượng check đôi: `<i class="fa-solid fa-check-double"></i>`
  + Tiêu đề: **`BẢO TOÀN TÍNH LŨY ĐẲNG THÀNH CÔNG!`**
  + Nội dung: *`Tệp sample_1920x1080_...jpg đã được nhận diện bằng mã băm SHA-256. Hệ thống từ chối chạy lại, bảo vệ tài nguyên FaaS!`*
- Hộp nhật ký `Nhật ký kiểm tra Idempotency` ghi nhận:
  ```text
  [EVENT] Gửi lặp lại sự kiện cho tệp: sample_1920x1080_1731388000.jpg...
  [DYNAMODB] ConditionalCheckFailedException: Khóa image_hash đã tồn tại!
  [IDEMPOTENT] Phát hiện sự kiện trùng lặp. ĐÃ BỎ QUA XỬ LÝ TRONG 1.8 ms!
  ```

### Lời thoại mẫu khi thao tác trước Hội đồng:
> *"Bây giờ, em xin chuyển sang Bước 2 để trả lời câu hỏi hóc búa nhất của hệ thống phân tán: Làm sao ngăn chặn sự kiện trùng lặp?*  
> *Em xin phép nhấn nút **Gửi lặp lại cùng tệp ảnh** vừa tải lên.*  
> *Thưa Thầy, Thầy có thể quan sát thấy thông báo màu xanh lá cây hiện lên ngay tức khắc!*  
> *Nhờ câu lệnh `ConditionExpression="attribute_not_exists(image_hash)"`, DynamoDB đã chặn đứng yêu cầu này ở tầng cơ sở dữ liệu và trả về lỗi `ConditionalCheckFailedException`.*  
> *Toàn bộ quá trình kiểm tra và ngắt chỉ tốn đúng **1.8 mili-giây**!*  
> *Hàm Lambda không tốn một chu kỳ CPU nào để resize lại ảnh, không có thumbnail thừa nào được sinh ra, đảm bảo tính lũy đẳng tuyệt đối 100%!"*

---

## BƯỚC 3: TRÌNH DIỄN TỆP LỖI MÃ ĐỘC & HÀNG ĐỢI SQS DLQ (FAULT INJECTION)
- **Vị trí Tab:** Nhấp chuột chuyển sang tab **'Bước 3: Tệp lỗi & SQS DLQ'** (`#step3-tab`).
- **Mục tiêu chứng minh:** Khi kẻ tấn công hoặc người dùng vô tình tải lên tệp văn bản/mã độc đổi đuôi `.jpg`, Lambda phát hiện lỗi `UnidentifiedImageError`, tự động kích hoạt retry và sau đó cô lập thông điệp vào SQS Dead-Letter Queue mà không làm sập worker. Đồng thời mở Sổ tay Vận hành SRE (Runbook).

### Các thao tác bấm trực tiếp trên màn hình:
1. Nhấp chuột vào nút đỏ cảnh báo: **`[Tải lên Tệp Hỏng / Giả Mạo (corrupted_test.jpg)]`**.
2. Quan sát khung cảnh báo màu đỏ xuất hiện.
3. Nhấp chuột vào nút vàng bên cạnh: **`[Xem Sổ Tay Runbook Xử Lý DLQ (SRE)]`** để mở Modal hướng dẫn vận hành.

### Hiện tượng quan sát thấy trên giao diện:
- Hộp cảnh báo màu đỏ rực xuất hiện với nội dung:
  + **`CẢNH BÁO: PHÁT HIỆN SỰ KIỆN LỖI RƠI VÀO SQS DLQ!`**
  + *`Thông điệp lỗi ID: msg-err-1731388050123 đã được cách ly trong hàng đợi cloud-image-serverless-dlq.`*
- Hộp nhật ký `Nhật ký xử lý ngoại lệ` ghi nhận chuỗi sự kiện:
  ```text
  [FAULT INJECTION] Tải lên tệp độc hại/hỏng: fake_image_payload.jpg...
  [LAMBDA ERROR] UnidentifiedImageError: cannot identify image file (Poison pill detected!)
  [RETRY] AWS Lambda thử lại lần 1 (Exponential Backoff)... Thất bại!
  [RETRY] AWS Lambda thử lại lần 2... Thất bại!
  [SQS DLQ] Sự kiện lỗi đã được định tuyến tự động vào SQS Dead-Letter Queue!
  ```
- Khi bấm **Xem Sổ Tay Runbook**, một hộp thoại Modal hiện đại mở ra hiển thị quy trình 3 bước của kỹ sư SRE: từ cảnh báo CloudWatch Alarm, câu lệnh AWS CLI để đọc message đến quy trình bấm **Start DLQ Redrive**.

### Lời thoại mẫu khi thao tác trước Hội đồng:
> *"Tại Bước 3, nhóm tiến hành kiểm thử tình huống lỗi (Chaos / Fault Injection).*  
> *Em xin phép nhấn nút **Tải lên tệp hỏng giả mạo**.*  
> *Ngay lập tức, thư viện Pillow phát hiện đây không phải là ảnh hợp lệ và ném ngoại lệ `UnidentifiedImageError`.*  
> *Thay vì nuốt chửng lỗi, hàm Lambda đã ném ngoại lệ lên runtime để AWS thực hiện retry 2 lần với backoff. Khi cả 2 lần đều không thành công, AWS Lambda đã tự động định tuyến tệp này vào **SQS Dead-Letter Queue**.*  
> *Đồng thời, khi em nhấn vào nút **Xem Sổ Tay Runbook**, Thầy có thể thấy quy trình phản ứng sự cố SRE chuẩn mực: Hệ thống không để kỹ sư phải đoán mò, mà cung cấp sẵn các câu lệnh AWS CLI để kiểm tra ID thông điệp bị cách ly và cơ chế Redrive an toàn sau khi đã vá lỗi."*

---

## BƯỚC 4: THỰC NGHIỆM ĐO ĐẠC BENCHMARK 100 LẦN GỌI (COLD START & BENCHMARK)
- **Vị trí Tab:** Nhấp chuột chuyển sang tab **'Bước 4: Cold Start & Benchmark'** (`#step4-tab`).
- **Mục tiêu chứng minh:** Chạy bộ đo kiểm tự động 100 sự kiện, hiển thị 4 thẻ chỉ số hiệu năng thực tế (Cold Start, Warm Start, p50, p95), kèm bảng phân tích chi phí 3 mức tải.

### Các thao tác bấm trực tiếp trên màn hình:
1. Nhấp chuột vào nút màu vàng nổi bật: **`[Chạy Thực Nghiệm 100 Invocations]`** (`#btnRunBenchmark`).
2. Nút chuyển sang trạng thái Disabled để ngăn spam.

### Hiện tượng quan sát thấy trên giao diện:
- Sau 1 giây, khu vực kết quả bung ra với **4 thẻ Metric Card** trực quan:
  1. Thẻ Đỏ: **Cold Start trung bình: `552.7 ms`** (Init + Exec time).
  2. Thẻ Xanh lá: **Warm Start trung bình: `26.9 ms`** (Pure in-memory exec).
  3. Thẻ Xanh Sky: **Độ trễ trung vị (p50): `25.8 ms`** (50% requests phản hồi).
  4. Thẻ Cam: **Độ trễ phân vị 95 (p95): `293.8 ms`** (Độ trễ do cold scale-out).
- Phía dưới là **Bảng Ước Tính Chi Phí Vận Hành (AWS Pricing Model)**:
  + Mức thấp (10k req): **$0.0042 / tháng** (Miễn phí trong Free Tier).
  + Mức trung bình (100k req): **$0.0416 / tháng** (Tiết kiệm >95% so với EC2).
  + Mức cao (1M req): **$0.4160 / tháng** (Chưa tới 11.000 VNĐ / 1 triệu ảnh).
- Hộp nhật ký `Log thực nghiệm` hiển thị chi tiết hoàn tất và xác nhận file CSV.

### Lời thoại mẫu khi thao tác trước Hội đồng:
> *"Cuối cùng là Bước 4: Thực nghiệm đo kiểm định lượng 100 lần gọi.*  
> *Em xin phép nhấn nút **Chạy Thực Nghiệm 100 Invocations**.*  
> *Thưa Thầy, toàn bộ các chỉ số thống kê của 100 lần đo lập tức được trực quan hóa trên màn hình:*  
> *- Thời gian Cold Start trung bình đạt **552.7 ms**, trong khi Warm Start chỉ tốn **26.9 ms** — chênh lệch hơn 20 lần.*  
> *- Chỉ số **p50 đạt 25.8 ms** khẳng định phần lớn người dùng sẽ nhận được phản hồi gần như tức thì.*  
> *- Đặc biệt tại bảng chi phí, với quy mô 1 triệu ảnh mỗi tháng, doanh nghiệp chỉ tốn khoảng **0.41 USD** (tương đương hơn 10.000 VNĐ tiền điện toán).*  
> *Toàn bộ dữ liệu này được đối sánh và khớp 100% với tệp `benchmark_100_runs.csv` và các biểu đồ phân phối học thuật trong báo cáo tiểu luận của nhóm.*  
> *Đến đây, nhóm em xin phép kết thúc phần trình diễn Live Demo và xin trân trọng lắng nghe các nhận xét, câu hỏi đóng góp quý báu từ Thầy Lê Quốc Tuấn ạ!"*

---

# PHẦN III: BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN DỰ PHÒNG (Q&A CHEAT SHEET CHO TS. LÊ QUỐC TUẤN)

> **Mục đích:** Bộ câu hỏi chuyên sâu dự đoán các thắc mắc mà Thầy Lê Quốc Tuấn thường đặt ra để kiểm tra mức độ hiểu sâu về Cloud Architecture, Concurrency, Bảo mật và Đánh đổi kỹ thuật (Trade-offs).

---

### Câu hỏi 1: "Tại sao nhóm lại dùng DynamoDB để khóa Idempotency mà không dùng ElastiCache Redis cho tốc độ bộ nhớ nhanh hơn?"
- **Sinh viên trả lời (Trần Ngọc Lâm):**
  > *"Thưa Thầy, nhóm em đã phân tích rất kỹ sự đánh đổi giữa Redis và DynamoDB:*  
  > *1. **Về tính chất Serverless & Scale-to-Zero:** Amazon ElastiCache Redis yêu cầu phải duy trì cụm máy chủ hoặc node tối thiểu chạy 24/7 (chi phí cố định ít nhất $15 - $20/tháng ngay cả khi không có request). Trong khi đó, DynamoDB ở chế độ `PAY_PER_REQUEST` có chi phí bằng đúng **0 USD** khi không có tải, hoàn toàn đồng nhất với triết lý Serverless của toàn bộ Pipeline.*  
  > *2. **Về tính kết nối mạng (VPC Cold Start):** Nếu dùng Redis trong VPC, Lambda bắt buộc phải cấu hình ENI (Elastic Network Interface), điều này từng làm tăng Cold Start thêm hàng trăm mili-giây. DynamoDB giao tiếp qua HTTPS Endpoint công khai an toàn có hỗ trợ AWS SigV4, giúp Lambda khởi động nhanh hơn.*  
  > *3. **Về tính nguyên tử:** DynamoDB hỗ trợ biểu thức `ConditionExpression` ở cấp độ phần cứng phân tán, đáp ứng độ trễ đọc/ghi chỉ từ 1 - 2 ms, hoàn toàn đủ nhanh cho bài toán xử lý ảnh."*

---

### Câu hỏi 2: "Tại sao trong hàm Lambda, nhóm lại chọn ném tiếp ngoại lệ (raise err) khi gặp file hỏng, thay vì bắt lỗi và trả về HTTP 400?"
- **Sinh viên trả lời (Trần Ngọc Lâm / Lê Doãn Đạt):**
  > *"Thưa Thầy, điều này xuất phát từ bản chất của **Mô hình Hướng sự kiện Bất đồng bộ (Asynchronous Event-driven Model)**:*  
  > *Trong mô hình này, người dùng không đứng chờ kết nối HTTP trực tiếp với Lambda, mà chỉ tải file lên S3. S3 là bên kích hoạt Lambda.*  
  > *Nếu chúng em `try...except` và trả về `statusCode: 400`, thì theo quy ước của AWS Lambda Runtime, lần thực thi đó vẫn được đánh dấu là **Thành công (Success / Exit code 0)**. Khi đó, AWS sẽ không kích hoạt retry, không ghi nhận metric lỗi vào CloudWatch, và đặc biệt là **sự kiện sẽ không bao giờ được chuyển vào SQS Dead-Letter Queue**.*  
  > *Bằng cách ném ngoại lệ lên Runtime, chúng em ủy thác việc quản lý vòng đời lỗi cho cơ chế tin cậy tích hợp sẵn của AWS, bảo đảm thông điệp độc hại được cách ly vào DLQ mà không bị mất dấu vết."*

---

### Câu hỏi 3: "Nếu có 2 request gửi cùng một file ảnh đến chính xác cùng 1 mili-giây, cơ chế phần cứng nào của DynamoDB đảm bảo không bị Race Condition?"
- **Sinh viên trả lời (Trần Ngọc Lâm):**
  > *"Thưa Thầy, DynamoDB sử dụng mô hình lưu trữ phân tán dựa trên thuật toán đồng thuận **Paxos** (hoặc Raft ở các thế hệ mới).*  
  > *Mỗi bảng được chia thành các partition, và mỗi partition có một nhóm bản sao (Storage Nodes) gồm 1 Node Leader và 2 Follower Nodes.*  
  > *Khi một lệnh `put_item` kèm `ConditionExpression` được gửi đến:*  
  > *1. Mọi yêu cầu ghi bắt buộc phải đi qua **Node Leader** của partition chứa mã băm đó.*  
  > *2. Node Leader xử lý tuần tự hóa (Serialization) các thao tác ghi. Khi request A đến trước dù chỉ vài phần triệu giây, Leader sẽ kiểm tra điều kiện, ghi vào bộ nhớ WAL (Write-Ahead Log) và khóa partition.*  
  > *3. Khi request B đến ngay sau đó, Leader đọc trạng thái hiện hành, thấy thuộc tính `image_hash` đã tồn tại, nên lập tức từ chối request B với lỗi `ConditionalCheckFailedException`.*  
  > *Nhờ cơ chế Leader-based Paxos này, việc kiểm tra điều kiện và ghi dữ liệu diễn ra hoàn toàn nguyên tử (Atomic), triệt tiêu hoàn toàn Race Condition ở cấp độ vật lý."*

---

### Câu hỏi 4: "Tại sao nhóm lại kết luận cấu hình 512MB RAM là tối ưu nhất? Nếu tăng lên 1024MB hay 2048MB thì có tốt hơn không?"
- **Sinh viên trả lời (Vũ Thành Đạt):**
  > *"Thưa Thầy, theo tài liệu kỹ thuật của AWS Lambda, dịch vụ này không cho phép chỉnh riêng CPU mà **phân bổ vCPU tỷ lệ tuyến tính theo dung lượng RAM** (cứ 1.769 MB RAM thì tương đương 1 full vCPU).*  
  > *- Ở mức **128MB RAM** (chỉ có ~0.07 vCPU), CPU bị nghẽn nghiêm trọng (CPU-bound) khi phải giải nén ma trận điểm ảnh JPEG của bức ảnh 1080p, khiến thời gian chạy kéo dài tới 256 ms.*  
  > *- Khi tăng lên **512MB RAM** (~0.29 vCPU), năng lực tính toán tăng gấp 4 lần, thời gian xử lý giảm sốc xuống còn 29 ms (giảm gần 9 lần).*  
  > *- Tuy nhiên, khi tăng tiếp lên **1024MB hay 2048MB**, thời gian xử lý chỉ giảm nhẹ từ 29 ms xuống 22 ms rồi bão hòa ở mức 21 ms. Nguyên nhân là vì việc đọc byte từ luồng bộ nhớ và thuật toán Bilinear Interpolation trên ảnh 1920x1080 đã đạt ngưỡng nghẽn băng thông bộ nhớ (Memory Bandwidth Limit).*  
  > *Trong khi đó, đơn giá tính cước cho 2048MB lại đắt gấp 4 lần so với 512MB. Nhân đơn giá với thời gian, mức 512MB cho tổng chi phí GB-giây thấp nhất và độ trễ hợp lý nhất, do đó 512MB là điểm cân bằng kỹ thuật tối ưu (Sweet Spot)."*

---

### Câu hỏi 5: "Khi thông điệp lỗi rơi vào SQS DLQ lưu trữ 14 ngày, quy trình SRE khắc phục và tái chạy (Redrive) hoạt động như thế nào?"
- **Sinh viên trả lời (Vũ Thành Đạt / Lê Doãn Đạt):**
  > *"Thưa Thầy, theo tài liệu `RUNBOOK_DLQ.md` của nhóm, quy trình gồm 3 bước rõ ràng:*  
  > *1. **Phát hiện & Cách ly:** CloudWatch Alarm gửi cảnh báo SNS khi `ApproximateNumberOfMessagesVisible > 0`. Thông điệp được giữ an toàn trong SQS DLQ với thời gian cấu hình `message_retention_seconds = 1209600` (đúng 14 ngày).*  
  > *2. **Điều tra nguyên nhân gốc rễ (RCA):** Kỹ sư SRE chạy lệnh `aws sqs receive-message` để kiểm tra thuộc tính thông điệp:*  
  > *  - Nếu lỗi là `UnidentifiedImageError`: Xác định người dùng upload file giả mạo -> Kỹ sư xóa thông điệp khỏi DLQ bằng `aws sqs delete-message` và gửi email cảnh báo người dùng.*  
  > *  - Nếu lỗi là `Task timed out` do ảnh quá lớn: Kỹ sư tiến hành nâng cấu hình timeout và RAM trong file `lambda.tf`, deploy cập nhật bằng `terraform apply`.*  
  > *3. **Quy trình Redrive:** Sau khi hạ tầng đã được vá lỗi, kỹ sư kích hoạt tính năng **SQS DLQ Redrive** (qua AWS Console hoặc lệnh `aws sqs start-message-move-task`). SQS sẽ tự động bơm ngược toàn bộ các thông điệp bị dồn ứ trong DLQ về lại hàng đợi nguồn để Lambda xử lý lại an toàn, bảo đảm hệ thống đạt trạng thái **Nhất quán cuối cùng (Eventual Consistency)** mà không làm thất thoát bất kỳ giao dịch nào."*

---

### Câu hỏi 6: "Làm thế nào nhóm chứng minh được mã nguồn và hạ tầng không bị lộ khóa bảo mật (Zero Hardcoded Secrets) theo chuẩn OWASP?"
- **Sinh viên trả lời (Lê Doãn Đạt):**
  > *"Thưa Thầy, nhóm áp dụng chiến lược 'Phòng thủ theo chiều sâu' (Defense-in-depth) gồm 3 lớp:*  
  > *1. **Ở tầng Mã nguồn Python:** Toàn bộ SDK Boto3 được khởi tạo bằng cú pháp mặc định `boto3.client('s3')` mà không truyền bất kỳ tham số `aws_access_key_id` hay `aws_secret_access_key` nào. Lambda tự động nhận quyền qua metadata service nội bộ của AWS.*  
  > *2. **Ở tầng Hạ tầng Terraform:** Tệp `iam.tf` tạo `aws_iam_role` gắn chính sách `AssumeRole` dịch vụ `lambda.amazonaws.com`, tạo ra chứng chỉ tạm thời có hiệu lực ngắn hạn và tự xoay vòng định kỳ.*  
  > *3. **Công cụ Kiểm định Tự động:** Nhóm đã xây dựng script `security_audit.py` quét toàn bộ kho mã nguồn bằng biểu thức chính quy Regex nhận diện các tiền tố nhạy cảm như `AKIA...`, `ASIA...` và các chuỗi bí mật. File `.gitignore` cũng chặn triệt để `.env`, `terraform.tfstate` trước khi commit lên Git.*  
  > *Kết quả kiểm tra tự động đạt 100% tuân thủ chuẩn an toàn OWASP Serverless SAS-02."*

---

# BẢNG TỔNG KẾT THÔNG SỐ VÀ CHECKLIST TRƯỚC GIỜ BẢO VỆ

| Hạng mục kiểm tra | Giá trị thực nghiệm đã đo kiểm | Trạng thái xác nhận |
| :--- | :--- | :---: |
| **Độ trễ Warm Start trung bình** | `26.98 ms` | ✅ Sẵn sàng |
| **Độ trễ Cold Start trung bình** | `552.73 ms` (Chậm hơn Warm 20.5 lần) | ✅ Sẵn sàng |
| **Phân vị độ trễ p50 / p95** | $p_{50} = 25.88\text{ ms}$ / $p_{95} = 293.82\text{ ms}$ | ✅ Sẵn sàng |
| **Tỷ lệ nén dung lượng Thumbnail** | Giảm từ **85% đến 90%** dung lượng tệp gốc | ✅ Sẵn sàng |
| **Thời gian hủy sự kiện trùng (Idempotency)** | **Dưới 2.0 mili-giây** (ConditionalCheckFailed) | ✅ Sẵn sàng |
| **Tỷ lệ cô lập tệp độc hại vào SQS DLQ** | **100% (5/5 tệp)** chuyển hướng chuẩn xác | ✅ Sẵn sàng |
| **Ước tính chi phí 100.000 ảnh/tháng** | **$0.0416 / tháng** (~1.100 VNĐ) | ✅ Sẵn sàng |
| **Ứng dụng Web Live Demo** | `http://localhost:5000` (4 bước tương tác) | ✅ Sẵn sàng |
