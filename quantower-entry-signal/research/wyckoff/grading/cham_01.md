# Chấm bài #01 — Chưa rõ (SC) / ACC? · 2025-12-29 15:22 → 2025-12-31 21:55 (118 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây: toàn bộ cấu trúc nằm trong vùng chết cuối năm, dữ liệu thưa cỡ H1 chứ không phải M1, và biên chính rộng 100 giá thì đó là đoạn xu hướng bị cắt ngang, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range vẽ trên dữ liệu thưa — không phải một chuỗi M1 thật — luật vi phạm: mục 1 (điều kiện mở range) + ghi chú "khung quá thô / range quá vụn"
- **Thuật toán gắn:** range 118 nến, Phase A 26 nến từ 2025-12-29 15:22 tới 2025-12-30 15:47.
- **Đúng phải là:** bỏ ứng viên. 26 nến trải **24 giờ 25 phút lịch** = trung bình 59 phút/nến. Khối lượng từng nến quanh climax là **1–2 hợp đồng**, cây climax **7 hợp đồng**. Đây là tuần nghỉ cuối năm, không có phiên đấu giá nào để mà đọc Wyckoff.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax — volume 1,2,1,1,2,1,**7**,1,1,1,1,1. Panel khối lượng: cả range chỉ là các thanh sát 0, trong khi thanh vàng thật (VSA cao trên volume lớn) chỉ xuất hiện từ 01-02 trở đi, tức **sau khi range đã đóng**.
- **Nghi phạm trong thuật toán:** guard khe thời gian (lỗi K) chỉ cắt khi **một** khe > 240 phút; nó không chặn được trường hợp mọi khe đều 30–120 phút. VSA là tỷ lệ tương đối nên 7/2 = 3.33× vẫn qua ngưỡng 2.2× — đúng như mục 12.1 của tài liệu thuật toán đã tự nghi ngờ. Cần thêm điều kiện **thời gian lịch/nến** (vd nến trung bình ≤ 3 phút) chứ không cần sàn lot tuyệt đối.

### 2. Nhãn SC nằm ngoài range và cao hơn mức SC 134 giá — luật vi phạm: L3 (biên chính = mức climax) + THEORY §3.3 (SC đánh dấu cao trào bán ở **đáy**)
- **Thuật toán gắn:** nhãn `SC` tại 2025-12-29 **13:42**, giá **4545.6**; mức climax dùng làm biên chính dưới là **4411.4** tại 15:22.
- **Đúng phải là:** SC là một sự kiện, một điểm. Nhãn và mức phải trùng nến. Nếu cây volume cao nhất của cụm không phải cực trị giá thì cây đó **không phải SC** — nó là PS (hỗ trợ sơ bộ) hoặc chỉ là một nến trong đợt bán.
- **Dấu hiệu quyết định trên chart:** chấm SC vẽ ở 4545.6, tức **cao hơn cả biên chính trên 4511.7**, và nằm **7 nến trước** cạnh trái khung range. Người đọc chart nhìn thấy "cao trào bán" ở giữa đoạn giảm, phía trên đỉnh range.
- **Nghi phạm trong thuật toán:** đúng chỗ v6 mới tách "nhãn climax" (cây VSA cao nhất trong cụm) khỏi "mức climax" (cực trị giá). Cách tách này sai về khái niệm và phải bỏ; nếu vẫn muốn giữ thì tối thiểu phải **kẹp nhãn trong cửa sổ cụm 8 nến kể từ nến mở range** và chỉ cho phép nhãn ở phía climax.

### 3. ST[A] rơi giữa range → Phase A đóng sớm — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 4476.0 (2025-12-30 15:47), chốt Phase A ở đó.
- **Đúng phải là:** ST[A] phải là cú **quay về phía climax rồi bị chặn**. Climax 4411.4, AR 4511.7, chiều cao 100.3 giá → 4476.0 nằm ở **64% chiều cao tính từ climax**, tức gần giữa range. Đó là một nhịp nghỉ trong đợt trượt từ AR xuống, không phải test vùng SC. ST[A] thật là cú chạm vùng 4411–4420 vào khoảng 12-30 23:25 — chính chỗ thuật toán đang gọi là ST[B].
- **Dấu hiệu quyết định trên chart:** chấm ST[A] treo lơ lửng giữa khung; sau nó giá tiếp tục trượt thêm 60 giá xuống đúng biên climax. Một cú "test" mà sau đó giá còn đi thêm 60% chiều cao range theo hướng cũ thì không phải test.
- **Nghi phạm trong thuật toán:** v5 bỏ hết ngưỡng % cho ST[A] (lỗi D) và thay bằng swing pivot 5 nến + sàn 1.5× biên độ TB. Kết quả: **bất kỳ** pivot nào cũng thành ST[A]. Cần thêm điều kiện định tính bắt buộc: ST[A] phải chạm được **vùng climax** (vd hồi được ≥ 70–80% khoảng từ AR về mức climax), nếu không thì Phase A chưa xong và phải chờ tiếp.

### 4. Phase C còn nằm lại trên timeline với Spring `pending` — luật vi phạm: L8
- **Thuật toán gắn:** Phase C 25 nến, Spring tại 4383.6 trạng thái **pending**, range đóng ở trạng thái `completed`.
- **Đúng phải là:** cú rũ chưa xác nhận thì theo đúng quyết định người học ở v5 (lỗi C) phải **xoá đoạn C** và trả về Phase B. Range đóng mà Phase cuối cùng là một Phase C treo lửng thì bảng phase đang khẳng định một điều chưa xảy ra.
- **Dấu hiệu quyết định trên chart:** dải phase kết thúc bằng `Phase C (25n)`, không có D/E, chấm Spring viền nét đứt.
- **Nghi phạm trong thuật toán:** nhánh đóng range (do hết dữ liệu/khe thời gian) không chạy lại bước hạ cấp shock như nhánh timeout 120 nến.

### 5. Spring có VSA 0.50× — luật vi phạm: mục 8 (Effort vs Result), THEORY §3.5
- Spring #1 (kiệt sức bán, volume rất thấp) là hợp lệ về lý thuyết, nên đây **không** phải lỗi tự thân. Nhưng trong bối cảnh cả range chỉ 1–7 hợp đồng/nến thì "volume thấp" không mang thông tin gì — không đọc được nỗ lực/kết quả ở đâu cả. Ghi nhận là hệ quả của lỗi 1.

### 6. Ba chỉ số Phase B đọc `none` trên một Phase B 68 nến — lỗi ĐO
- SOT trên = `none (n=0)`, SOT dưới = `none (n=0)`, không có nhịp nỗ lực/kết quả nào được ghi. Nhưng trên chart Phase B có ít nhất 3 nhịp lên–xuống rõ (từ AR 4511.7 trượt về 4420, bật, trượt tiếp). Bộ dò nhịp thrust không tìm được nhịp nào ⇒ ngưỡng dò swing của chỉ số mới quá chặt so với dữ liệu thưa. Đây là lỗi **đo**, không phải lỗi lọc.

## Đạt
- Tên range: không đặt tên, để "Chưa rõ (SC)" — đúng L4, không gò ép (đối lập với Ca #20 nguồn 7.pdf).
- Biên chính = mức climax 4411.4 + mức AR 4511.7, giữ cố định suốt range — đúng L3.
- Biên phụ: đúng **một** cái mỗi bên, biên phụ dưới 4383.6 là cực trị xa nhất (Spring hạ cấp ST[B] 4404.5) — đúng L3.
- Phase B (68) dài nhất, Phase C (25) ngắn nhất — đúng L9/L8 về tỉ lệ.
- Bỏ hẳn nhãn ST[B] cũ ở nghĩa cũ, dùng ST[B] = test biên dưới — thống nhất với L6 phiên bản v6.

## Cần hỏi người học
- Người học đã chốt "không dùng sàn khối lượng tuyệt đối". Nhưng ca này cho thấy vấn đề không phải lot mà là **mật độ thời gian**: 26 nến/24 giờ. Có chấp nhận thêm guard "nến trung bình trong range ≤ N phút" (thuần cấu trúc thời gian, không phải sàn lot) không?
