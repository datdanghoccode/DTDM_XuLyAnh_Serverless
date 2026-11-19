# KỊCH BẢN BÁO CÁO THUYẾT TRÌNH — NỘI DUNG CHÍNH ĐÃ HOÀN THÀNH
## ĐỀ TÀI 9: XÂY DỰNG HỆ THỐNG XỬ LÝ ẢNH HƯỚNG SỰ KIỆN BẰNG SERVERLESS VÀ ĐÁNH GIÁ COLD START
* **Giảng viên hướng dẫn:** TS. Lê Quốc Tuấn
* **Nhóm sinh viên thực hiện (Lớp 012012303904):**
  1. **Lê Doãn Đạt** — MSSV: `038206000230` *(Người 1)*
  2. **Trần Ngọc Lâm** — MSSV: `034206001749` *(Người 2)*
  3. **Vũ Thành Đạt** — MSSV: `001206040720` *(Người 3)*

---

## PHẦN A: BẢN TÓM TẮT NHANH 2 PHÚT (ELEVATOR PITCH)
*(Dùng khi Thầy yêu cầu: "Nhóm hãy tóm tắt ngắn gọn trong 2 phút những kết quả kỹ thuật đắt giá nhất đã làm được!")*

> "Kính thưa Thầy TS. Lê Quốc Tuấn và Hội đồng!  
> Đối với Đề tài 9, nhóm chúng em đã giải quyết trọn vẹn câu hỏi nghiên cứu về việc: **Xử lý tin cậy và kiểm soát chi phí khi lưu lượng tải ảnh biến động theo các nhịp không đều (Spiky Load)** thông qua 4 thành quả kỹ thuật nổi bật:
>
> 1. **Về Kiểm Soát Chi Phí:** Chúng em triển khai kiến trúc 100% Serverless bằng Terraform IaC. Khi không có tệp tải lên, hệ thống tự động co về 0 tuyệt đối (**Scale-to-Zero**, chi phí = $0.00). Với 100,000 bức ảnh, chi phí chỉ tốn **$0.045 USD** — tiết kiệm hơn **95%** so với thuê máy chủ ảo EC2 truyền thống ($10/tháng).
> 2. **Về Độ Tin Cậy & Tính Lũy Đẳng:** Để giải quyết nguy cơ trùng lặp của mạng *At-least-once*, chúng em thiết kế **Thuật toán Khóa Lũy Đẳng Nguyên Tử trên DynamoDB** (`attribute_not_exists(image_hash)`). Thuật toán triệt tiêu hoàn toàn lỗi Race Condition của phương pháp Check-then-Act, chặn đứng sự kiện trùng lặp ở tầng lưu trữ trong **$< 2.5\text{ ms}$** và không bao giờ tạo bản ghi rác.
> 3. **Về Kháng Lỗi & Vận Hành SRE:** Hệ thống bẫy được toàn bộ tệp hỏng (Poison Pill) và sự cố Timeout qua 3 lần Retry với *Exponential Backoff*, tự động cô lập vào **SQS Dead-Letter Queue (lưu 14 ngày)** và cung cấp quy trình **DLQ Redrive** tái xử lý an toàn mà không làm mất giao dịch của khách hàng.
> 4. **Về Đo Lường & Tối Ưu:** Thực nghiệm định lượng trên 100 lần gọi đo được thời gian ấm $p_{50} = 30.3\text{ ms}$, $p_{95} = 289.5\text{ ms}$, tỷ lệ lỗi 0%. Đồng thời, chúng em chứng minh thực nghiệm **Điểm Ngọt (Sweet Spot) tối ưu tuyệt đối là 512MB RAM** — giúp tăng tốc độ 360% trong khi chi phí chỉ tăng 8%.
>
> Toàn bộ sản phẩm được đóng gói gồm **2 ứng dụng Web chạy thực tế**, báo cáo 52 trang chuẩn UTH, slide 13 trang và 100% mã nguồn đã được đẩy lên GitHub. Sau đây nhóm xin báo cáo chi tiết!"

---

## PHẦN B: KỊCH BẢN THUYẾT TRÌNH CHI TIẾT PHÂN VAI 3 THÀNH VIÊN (8 - 10 PHÚT)

```
                       SƠ ĐỒ PHÂN VAI THUYẾT TRÌNH
┌─────────────────────────────────────────────────────────────────────────────┐
│ NGƯỜI 1: LÊ DOÃN ĐẠT (3 phút)                                               │
│ • Mở đầu & Trả lời trực diện Câu hỏi nghiên cứu                             │
│ • Cơ sở lý thuyết FaaS, EDA, Vòng đời Firecracker MicroVM                   │
│ • Thiết kế hạ tầng Terraform IaC, IAM Least Privilege, Zero Secrets         │
├─────────────────────────────────────────────────────────────────────────────┤
│ NGƯỜI 2: TRẦN NGỌC LÂM (3.5 phút)                                           │
│ • Kiến trúc Pipeline 5 trạm & Mã hóa tệp nhị phân SHA-256                   │
│ • Thuật toán Khóa Lũy Đẳng Nguyên Tử DynamoDB (Giải quyết Race Condition)   │
│ • Xử lý ảnh Pillow an toàn trong RAM /tmp & Cô lập lỗi SQS DLQ              │
├─────────────────────────────────────────────────────────────────────────────┤
│ NGƯỜI 3: VŨ THÀNH ĐẠT (3.5 phút)                                            │
│ • Kết quả thực nghiệm 100 lần gọi (p50, p95, Cold Start vs Warm Start)      │
│ • Khảo sát đánh đổi RAM & Chứng minh Điểm Ngọt Sweet Spot 512MB             │
│ • Bài toán kinh tế 3 mức tải & Sổ tay vận hành SRE Runbook DLQ Redrive      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 🎙️ LỜI NÓI CỦA NGƯỜI 1: LÊ DOÃN ĐẠT (3 Phút)
*(Trình bày từ Slide 1 đến Slide 5: Giới thiệu, Câu hỏi nghiên cứu, Lý thuyết FaaS & An ninh OWASP)*

> "Kính thưa Thầy TS. Lê Quốc Tuấn và toàn thể Hội đồng chấm thi!  
> Em tên là **Lê Doãn Đạt**, đại diện Nhóm thực hiện Đề tài 9: **'Xây dựng hệ thống xử lý ảnh hướng sự kiện bằng Serverless và đánh giá Cold Start'**.
>
> **1. Trả lời Câu hỏi nghiên cứu:**  
> Đề cương đặt ra câu hỏi: *'Khi tệp được tải lên theo các nhịp không đều (Spiky Load), kiến trúc hướng sự kiện có thể tự động xử lý tin cậy và kiểm soát chi phí ra sao?'*  
> Nhóm chúng em trả lời trực diện bằng 3 trụ cột kỹ thuật:
> - *Thứ nhất:* Dùng mô hình Serverless FaaS để đạt khả năng **Scale-to-Zero**. Khi không có tải, chi phí là $0. Khi có tải đột biến, hệ thống nhân bản container trong vài mili-giây và tính tiền theo từng mili-giây thực thi.
> - *Thứ hai:* Dùng hàng đợi **Amazon SQS** làm 'bình tích áp' đệm tải bất đồng bộ, bảo vệ Lambda không bị nghẽn đồng thời (Concurrency Exhaustion).
> - *Thứ ba:* Dùng **Khóa Lũy Đẳng Nguyên Tử** trên DynamoDB để loại bỏ hoàn toàn nguy cơ trùng lặp của cơ chế mạng *At-least-once delivery*.
>
> **2. Cơ sở lý thuyết nền tảng:**  
> Hệ thống vận hành theo nguyên tắc **Thực thi phi trạng thái (Stateless Execution)**. Container FaaS chạy trên công nghệ MicroVM Firecracker siêu nhẹ. Khi container đầu tiên khởi tạo, nó tốn khoảng 500ms nạp mã nguồn và thư viện Pillow — đây chính là **Cold Start**. Tuy nhiên, sau lần đầu, container được giữ ấm (**Warm Invocation**), giúp độ trễ giảm ngoạn mục xuống chỉ còn dưới 30ms.
>
> **3. Hạ tầng mã hóa Terraform & An ninh chuẩn OWASP:**  
> Em đã xây dựng toàn bộ hạ tầng bằng 9 tệp **Terraform IaC**, triển khai 6 thành phần: S3 Input, SQS Event Queue, AWS Lambda 512MB, DynamoDB On-Demand, S3 Output và SQS DLQ.  
> Tuân thủ chuẩn an ninh **OWASP Serverless Top 10**, chính sách IAM của nhóm:
> - Triệt tiêu 100% quyền `Action: "*"` hay `AdministratorAccess`.
> - Thiết lập **6 Statement độc lập phân quyền tối thiểu**: Lambda chỉ được đọc từ S3 Input và chỉ được ghi vào S3 Output; không có quyền xóa ảnh gốc hay xóa cơ sở dữ liệu.
> - Đặc biệt, nhóm đạt tiêu chuẩn **Zero Hardcoded Secrets**: 100% xác thực qua IAM Role và token tạm thời AWS STS tự động xoay vòng, không lưu bất kỳ Access Key nào trong mã nguồn Git.
>
> Tiếp theo, em xin kính mời bạn **Trần Ngọc Lâm** trình bày về thiết kế Pipeline đầu-cuối và thuật toán Khóa lũy đẳng nguyên tử!"

---

### 🎙️ LỜI NÓI CỦA NGƯỜI 2: TRẦN NGỌC LÂM (3.5 Phút)
*(Trình bày Slide 6, 7 & 8: Kiến trúc Pipeline, Thuật toán Khóa lũy đẳng, An toàn Pillow & SQS DLQ)*

> "Kính thưa Thầy và Hội đồng! Em là **Trần Ngọc Lâm**. Em phụ trách thiết kế Pipeline đầu-cuối và thuật toán xử lý ảnh lõi.
>
> **1. Luồng dữ liệu Pipeline 5 trạm:**  
> Chuỗi sự kiện diễn ra hoàn toàn tự động:
> - Người dùng tải ảnh lên S3 Input $\rightarrow$ S3 phát sinh sự kiện `s3:ObjectCreated` $\rightarrow$ Đẩy vào SQS Event Queue $\rightarrow$ Kích hoạt Lambda FaaS.
> - Lambda giải mã tên tệp an toàn bằng `unquote_plus()` chống tấn công duyệt thư mục (Path Traversal), sau đó băm toàn bộ dòng byte nhị phân của ảnh bằng thuật toán **SHA-256**. Nhóm sử dụng chuỗi băm nội dung làm Partition Key thay vì dùng tên tệp, đảm bảo tính duy nhất tuyệt đối.
>
> **2. Đột phá kỹ thuật: Thuật toán Khóa Lũy Đẳng Nguyên Tử trên DynamoDB:**  
> Trong mạng phân tán, cơ chế giao ít nhất một lần (*At-least-once*) và việc người dùng bấm đúp nút Upload sẽ gửi lại chính xác bức ảnh đó.
> - Nếu dùng phương pháp thông thường `get_item` kiểm tra trước rồi mới `put_item` (Check-then-Act), khi 2 sự kiện đến cùng lúc trong 1ms, cả 2 đều thấy chưa có và cả 2 đều xử lý $\rightarrow$ **Vỡ tính lũy đẳng do Race Condition!**
> - Để giải quyết triệt để, em gom kiểm tra và ghi nhận thành một thao tác nguyên tử duy nhất trên DynamoDB:  
>   `ConditionExpression: attribute_not_exists(image_hash) OR status = FAILED`
> - Khi sự kiện trùng lặp thứ hai đến, DynamoDB từ chối ở tầng lưu trữ và ném lỗi `ConditionalCheckFailedException`. Lambda bắt lỗi này và thoát an toàn ngay trong **$< 2.5\text{ ms}$**. Ảnh không bị resize lại, CPU không tốn tài nguyên và DynamoDB **tuyệt đối không tạo bản ghi trùng lặp**.
>
> **3. Xử lý ảnh an toàn và Phòng chống rò rỉ dữ liệu /tmp:**  
> - Chống Image Bomb: Cấu hình cứng `Image.MAX_IMAGE_PIXELS = 50,000,000` và xác thực nhị phân qua `Image.verify()`.
> - Thuật toán lấy mẫu `Lanczos` tạo thumbnail chuẩn 300x300, giúp **giảm trung bình 89.6% dung lượng** mà vẫn giữ độ sắc nét.
> - Toàn bộ quá trình nạp và resize được thực hiện thuần túy trong RAM bằng luồng `io.BytesIO()`. Khối lệnh `finally` dọn sạch thư mục `/tmp`, triệt tiêu hoàn toàn nguy cơ rò rỉ dữ liệu nhạy cảm giữa các lần gọi ấm.
>
> **4. Cô lập Poison Pill & Timeout vào SQS DLQ:**  
> Khi gặp tệp giả mạo hoặc tệp hỏng khiến Pillow ném `UnidentifiedImageError`, hoặc tác vụ vượt quá Timeout 30 giây, Lambda bắt lỗi và ném Exception để kích hoạt cơ chế Retry. Sau 3 lần thử lại thất bại liên tiếp với *Exponential Backoff*, sự kiện lỗi được tự động cô lập an toàn vào **SQS Dead-Letter Queue (lưu giữ 14 ngày)**, không làm nghẽn luồng xử lý của các ảnh hợp lệ khác.
>
> Tiếp theo, em xin kính mời bạn **Vũ Thành Đạt** trình bày phần đo lường thực nghiệm và vận hành SRE!"

---

### 🎙️ LỜI NÓI CỦA NGƯỜI 3: VŨ THÀNH ĐẠT (3.5 Phút)
*(Trình bày Slide 9 đến 13: Đo lường thực nghiệm 100 runs, Sweet Spot 512MB RAM, Chi phí & SRE Runbook)*

> "Kính thưa Thầy và Hội đồng! Em là **Vũ Thành Đạt**. Em phụ trách thực nghiệm đo đạc định lượng, đánh đổi hiệu năng - chi phí và sổ tay vận hành SRE.
>
> **1. Kết quả đo lường định lượng 100 lần gọi (100 Runs Benchmark):**  
> Nhóm đã tiến hành đo đạc thực nghiệm trên môi trường đám mây qua tệp dữ liệu `benchmark_100_runs.csv` với các nhịp tải đan xen. Kết quả ghi nhận các phân vị độ trễ chuẩn xác:
> - **$p_{50}$ (Trung vị): đạt $30.3\text{ ms}$** — 50% yêu cầu được phục vụ cực nhanh bởi container ấm.
> - **$p_{90}$: đạt $36.08\text{ ms}$** — hệ thống duy trì tính ổn định vượt trội.
> - **$p_{95}$ (Đuôi trễ): đạt $289.5\text{ ms}$** — bắt đầu xuất hiện container mới khi có xung tải đột biến.
> - **$p_{99}$ (Đỉnh trễ): đạt $589.2\text{ ms}$** — phản ánh đầy đủ trường hợp Cold Start nạp microVM và thư viện Pillow.
> - Tỷ lệ lỗi ghi nhận đạt mức tuyệt đối **0.00%** trên toàn bộ 100 lần gọi.
>
> **2. Khảo sát Đánh đổi RAM và Chứng minh Điểm Ngọt (Sweet Spot) 512MB:**  
> Trong AWS Lambda, năng lực vCPU tỷ lệ thuận với dung lượng RAM. Nhóm tiến hành khảo sát từ 128MB đến 2048MB:
> - Ở mức **128MB RAM**, CPU bị bóp nghẽn (~0.08 vCPU), thời gian chạy lâu (98.5ms) làm chi phí bị đội lên.
> - Nâng lên mức **512MB RAM**, thời gian chạy ấm giảm tới 73% (từ 98.5ms xuống chỉ còn **$26.8\text{ ms}$**), trong khi chi phí cho 100,000 lượt gọi chỉ tăng từ $0.0210 lên **$0.0228 USD** (chỉ tăng 8%).
> - Nếu nâng tiếp lên 1024MB hay 2048MB, tốc độ chỉ tăng thêm vài mili-giây nhưng chi phí tăng gấp đôi do nghẽn I/O ảnh.
> $\rightarrow$ **Kết luận thực nghiệm:** Mức **512MB RAM chính là Điểm Ngọt (Sweet Spot) tối ưu tuyệt đối** giữa hiệu năng và chi phí.
>
> **3. Dự toán chi phí cho 3 mức lưu lượng tải:**  
> - Mức thấp (10,000 ảnh/tháng): **$0.0046 USD** (tiết kiệm 99.95% so với thuê máy chủ EC2 t2.micro $10/tháng).
> - Mức vừa (100,000 ảnh/tháng): **$0.0459 USD** (tiết kiệm 99.54%).
> - Mức cao (1,000,000 ảnh/tháng): **$0.4590 USD** (tiết kiệm 95.41%).
>
> **4. Sổ tay vận hành SRE Runbook & Quy trình DLQ Redrive:**  
> Khi có thông điệp lỗi trong DLQ, quy trình SRE gồm 3 bước:
> - *Bước 1 (Cảnh báo):* CloudWatch Alarm kích hoạt khi `ApproximateNumberOfMessagesVisible > 0`.
> - *Bước 2 (Điều tra RCA):* Kỹ sư mở giao diện kiểm tra payload tệp lỗi; nếu lỗi do timeout thì nâng cấu hình RAM trong Terraform.
> - *Bước 3 (Khắc phục & Redrive):* Nhấn nút **'Kích Hoạt SQS DLQ Redrive'** trên Dashboard để tự động đẩy ngược thông điệp về hàng đợi chính để tái xử lý thành công.
>
> **5. Danh mục sản phẩm nhóm bàn giao:**  
> - Báo cáo Word học thuật hoàn chỉnh **52 trang**, 4 chương chuẩn UTH.
> - Bộ slide trình chiếu chính thức chuẩn 13 trang trên Canva và PowerPoint.
> - **2 Ứng dụng Web độc lập**: Web 1 (:5001) Học viện Kiến thức và Web 2 (:5002) Phòng Lab thực nghiệm tương tác chạy bằng `run_all.bat`.
> - Toàn bộ mã nguồn và 22 test case tự động (PASS 100%) đã được đẩy lên GitHub.
>
> Nhóm chúng em xin chân thành cảm ơn Thầy và Hội đồng đã lắng nghe. Chúng em rất mong nhận được câu hỏi phản biện từ Thầy!"

---

## PHẦN C: BỘ SỐ LIỆU ĐINH ĐỂ TỰ TIN PHẢN BIỆN (CHEAT-SHEET CHO CẢ 3 BẠN)

| Câu Hỏi Phản Biện Dự Kiến | Số Liệu & Luận Điểm Trả Lời Ngay Lập Tức | Người Trả Lời Tốt Nhất |
| :--- | :--- | :---: |
| **"Tại sao chọn 512MB RAM mà không phải 128MB hay 1024MB?"** | "Dạ thưa Thầy, vì CPU tỷ lệ thuận với RAM. Ở 128MB CPU chỉ có ~0.08 vCPU nên xử lý ảnh mất 98.5ms. Lên 512MB có ~0.33 vCPU xử lý chỉ mất 26.8ms (nhanh hơn 360%) mà chi phí chỉ tăng từ $0.021 lên $0.0228/100k ảnh (chỉ tăng 8%). Lên 1024MB chi phí tăng gấp đôi nhưng tốc độ chỉ giảm thêm 9ms do nghẽn I/O." | **Vũ Thành Đạt** |
| **"Làm sao đảm bảo tính Idempotent khi có 2 sự kiện đến cùng mili-giây?"** | "Dạ thưa Thầy, nhóm không dùng Check-then-Act (`get_item` rồi `put_item`) vì sẽ bị Race condition. Nhóm dùng thao tác nguyên tử `ConditionExpression: attribute_not_exists(image_hash)` trên DynamoDB. DynamoDB từ chối ở tầng lưu trữ phần cứng và trả về ngay trong 2.1 ms, không ghi đè và không tạo bản ghi mới." | **Trần Ngọc Lâm** |
| **"Cơ chế nào chứng minh không lưu khóa bí mật trong mã nguồn?"** | "Dạ thưa Thầy, nhóm sử dụng IAM Execution Role gắn cho Lambda, dịch vụ AWS STS tự động cấp Token tạm thời có hạn ngắn. Nhóm có script `security_audit.py` quét Regex xác nhận 0 Access Key và `.gitignore` chặn toàn bộ file `.env`, `.tfstate`." | **Lê Doãn Đạt** |
| **"Thông điệp trong SQS DLQ được xử lý ra sao?"** | "Dạ thưa Thầy, DLQ lưu giữ thông điệp lỗi trong 14 ngày. Kỹ sư SRE điều tra nguyên nhân (nếu là ảnh độc thì xóa; nếu là lỗi timeout thì sửa Terraform). Sau đó dùng tính năng SQS DLQ Redrive để đẩy ngược thông điệp về hàng đợi chính xử lý lại mà không mất dữ liệu của khách hàng." | **Vũ Thành Đạt** |
