# Chấm bài #41 — Chưa rõ (SC) (ACC?) · 2026-07-06 12:43 → 17:15 (272 nến M1, superseded)

**Điểm: 4/10** — Khung range và tỉ lệ Phase B đúng, nhưng ST[A] rơi giữa range (Phase A chưa xong) và **cú Spring thật bị xoá thành mSOW**, để rồi Phase C phải gán ngược vào một nhịp vô nghĩa.

## Lỗi (nặng → nhẹ)

### 1. Spring thật bị hạ cấp thành mSOW, Phase C đặt sai chỗ — L5, L8
- **Thuật toán gắn:** `mSOW` 14:44 tại 4140.6 (VSA **5.13×**, thân 0.58); Phase C mở muộn tại `LPS[C]` 16:14 (4152.0, VSA 0.97×) theo cơ chế gán ngược.
- **Đúng phải là:** cú 14:44 là **Spring** (cạnh climax của range gốc SC): phá xuống dưới biên chính 4143.3 tới 4140.6 rồi **rút vào trong range ngay**, kèm cây volume **cao nhất toàn chart** (nhìn panel dưới: thanh vàng cao nhất nằm đúng ở 14:44). Sau cú đó giá đi hết sang biên đối diện và **phá luôn biên trên** — đó chính là điều kiện xác nhận cú rũ trong THEORY §5 ("mục tiêu tối thiểu: giá phải đi đến đầu đối diện của cấu trúc"). Phase C phải neo tại 14:44.
- **Dấu hiệu quyết định trên chart:** độ sâu dưới biên = 2.7 giá = **15.5% chiều cao range** (17.4 giá) → đủ ngưỡng "mạnh"; VSA 5.13× → đủ cả hai điều kiện; và nó là **cực trị thấp nhất** của cả range (chính nó tạo biên phụ dưới 4140.6).
- **Nghi phạm trong thuật toán:** trần **Phase C = 120 nến**. Từ 14:44 tới SOS 16:50 là **126 nến** → shock "hết hạn", nhãn bị đổi thành mSOW và đoạn C bị xoá (đúng theo cơ chế lỗi C của v5). Nhưng cú rũ này **đã tới biên đối diện và đã phá thật**, chỉ chậm hơn trần 6 nến. Trần thời gian không được phép huỷ một cú rũ mà kết cục đã xác nhận nó — nên chuyển thứ tự xét: **kết cục thắng trần**.

### 2. ST[A] rơi giữa range — Phase A chưa hoàn thành — L2
- **Thuật toán gắn:** `ST[A]` 13:15 tại **4150.7**.
- **Đúng phải là:** ST[A] phải là cú quay về **test lại vùng climax** (~4143–4146). 4150.7 nằm ở **(4150.7−4143.3)/17.4 = 43%** chiều cao, tức đúng giữa range — đây là "một cái ngọ nguậy giữa range", không phải lần đổi hướng thứ 3 của CHoCH. Nhìn ảnh: nhịp 13:15 chỉ là một pullback nông trong đà tăng từ SC lên mSOS 13:34.
- **Dấu hiệu quyết định trên chart:** cú test vùng climax thật xảy ra **muộn hơn nhiều** (14:44, xuống 4140.6) — nếu đó là ST[A] thì Phase A dài ~120 nến và cấu trúc còn phải đọc lại từ đầu; nếu giữ 14:44 là Spring thì Phase A ở bài này **thiếu ST[A]** — đúng lỗi Ca #2 nguồn 7.pdf ("Thiếu ST[A]").
- **Nghi phạm trong thuật toán:** ST[A] đo bằng "swing pivot đầu tiên về phía climax, sàn 1.5× ATR" — **không có sàn khoảng cách tới mức climax**. Người học đã chốt "không đo bằng %", nhưng vẫn cần điều kiện cấu trúc: ST[A] phải là nhịp **chạm được vùng cụm climax** (trong khoảng bằng biên độ cây climax), không chỉ là pivot đầu tiên bất kể ở đâu.

### 3. Nhãn SC lơ lửng cách biên chính 2.5 giá — L3 (trình bày + đọc chart)
- **Thuật toán gắn:** nhãn SC vẽ tại 12:41 giá **4145.8** (VSA 3.27×), còn mức biên chính dưới là **4143.3** (low nến 12:43, VSA chỉ 1.28×, biên độ 1.9 giá).
- Cơ chế tách nhãn/mức của v6 là hợp lệ (đã thông báo), nhưng hệ quả trên chart: chấm đỏ SC nằm **cao hơn nét liền dưới 2.5 giá**, người đọc thấy "cao trào bán" không ở đáy. Đề nghị vẽ thêm một vạch mờ nối nhãn climax xuống mức biên, hoặc ghi rõ "cụm climax 12:41–12:43".

### 4. Phase D ngắn hơn Phase C — L8
- A 33 · B **178** · C **36** · D 26. Phase B dài nhất là đúng (L9), nhưng C = 36 > D = 26; "phase ngắn nhất" phải là C. Đây là hệ quả trực tiếp của lỗi #1: C bị gán ngược nên độ dài của nó là sản phẩm của cửa sổ 60 nến, không phải của cấu trúc.

### 5. Ba chỉ số Phase B mới
- **SOT phía dưới:** `SOT, n=3, thrust cuối/đầu = 0.37, volume 0.88 (cạn kiệt)` — **đo đúng bản chất**: đúng 3 nhịp, lực đẩy xuống rút còn 1/3 với volume giảm nhẹ, khớp THEORY §7. Đây là chỉ số dùng được.
- **SOT phía trên:** `chớm, n=2, volume 1.17 (HẤP THỤ)` — n=2 chưa đủ ngưỡng ≥3 lần đẩy của §7 để gọi tên, nhưng ghi "chớm" thì tạm chấp nhận.
- **Nỗ lực/kết quả:** `effort=1.40x, result=1.68, er=0.83` kèm kết luận "**hấp thụ NGHI VẤN (volume nhiều, kết quả ít)**". er = 0.83 < 1 nghĩa kết quả **nhiều hơn** nỗ lực — câu diễn giải sai chiều. Lỗi này giống nhau trên cả 5 bài 40–44 ⇒ câu chữ dán cứng, không đọc từ er.
- **Bias:** `+0` như cả lô.

## Đạt
- **Điều kiện mở range (L1):** MOVE giảm 21.8 giá / 76 nến / hiệu suất 0.36, bị cụm climax 12:41–12:43 chặn tại đáy. Đúng.
- **Phase B là phase dài nhất (L9):** 178/272 nến = 65% range. Đúng tinh thần "giai đoạn xây nguyên nhân".
- **Biên (L3):** biên chính cố định 4143.3/4160.7 suốt range, mỗi bên đúng 1 biên phụ (4140.6 / 4164.0) và cả hai đều là cực trị xa nhất thật.
- **SOS neo đúng cây phá thật (L3):** SOS 16:50 VSA **3.42×**, thân **0.85**, giá 4165.0 **vượt biên phụ trên 4164.0** — đúng yêu cầu "SOS mạnh phải bứt qua biên phụ". LPS[D] 17:01 tại 4164.1 giữ được ngoài biên → Phase D/E đúng khuôn CBR (L10).
- **mSOS 13:34** (4162.6, VSA 2.45×, thân 0.67) gán hợp lý: thọc qua biên trên rồi thu vào, đủ mạnh nên không phải test nhẹ.
- **Trạng thái `superseded`, không đặt tên 4 mẫu hình:** hợp lệ theo cơ chế mới. Ghi nhận để người viết code biết: với một người đọc chart, range này có SOS thật phá lên từ origin SC nên **đọc bằng mắt vẫn là Tích luỹ** — nếu range con thay thế nó cũng không đặt tên thì cả cụm mất kết luận.
