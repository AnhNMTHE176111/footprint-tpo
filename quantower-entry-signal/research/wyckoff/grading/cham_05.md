# Chấm bài #05 — Tái tích luỹ (RE-ACC) · 2026-04-13 16:47 → 2026-04-14 00:40 (145 nến M1)

**Điểm: 8/10** — **Bài tốt nhất trong lô.** Vẽ đúng cấu trúc: chỉ sửa hai nhãn. Đây là bài **duy nhất**
trong 5 bài mà Phase A → E xếp đúng thứ tự độ dài, biên chính khớp mức AR, và cú SOS bứt qua biên phụ
một cách kiểm chứng được. Giữ nguyên khung, sửa vị trí ST[A] và cách chốt Phase E.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không đặt tại cực trị của nhịp test — luật vi phạm: §4.2 thuật toán ("đánh dấu tại điểm cực trị")
- **Thuật toán gắn:** ST[A] = **4806.6** @17:37.
- **Đúng phải là:** cực trị của chính nhịp test đó là **4810.9 @17:27** — cao hơn **4.3 giá**, sớm hơn
  **10 phút**. Chính mức 4810.9 đó là mức tạo ra biên phụ trên, nên nhãn ST[A] phải nằm ở đó.
- **Dấu hiệu quyết định trên chart:** cực trị cao nhất của toàn Phase A (16:47 → 17:38) là 4810.9 @17:27;
  trong khi cả Phase B (17:39 → 20:37) đỉnh chỉ 4806.3, **không vượt** biên chính 4806.7. Vậy 4810.9
  thuộc nhịp ST[A], không phải một cú thăm dò riêng. Trên ảnh, chấm ST[A] nằm **thấp hơn** nét đứt
  "bien phu tren 4810.9" mà chính nó tạo ra.
- **Nghi phạm trong thuật toán:** §4.2 xác nhận ST[A] bằng "5 nến liên tiếp không tạo cực trị mới" rồi
  đánh dấu — nhưng có vẻ đánh dấu tại **nến xác nhận** thay vì **nến cực trị**. Sửa: lưu lại chỉ số nến
  cực trị trong lúc chờ, gắn nhãn tại chỉ số đó.

### 2. Phase E chỉ 1 nến — là một MỐC, không phải một phase — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 04-14 00:40 → 00:40 = **1 nến**.
- **Đúng phải là:** L10 nói Phase E là "giá thuận lực đi tiếp để **tìm vùng giá mới**" — một quá trình.
  Thực tế giá đi tiếp lên **4839.0 @04-14 01:12** (+22 giá trên SOS, +32 giá trên biên chính trên), tức
  Phase E thật kéo dài thêm hơn 30 phút nữa. Vẽ nó thành 1 nến rồi đóng range làm mất phần "kết quả".
- **Dấu hiệu quyết định trên chart:** vạch tím Phase E nằm ở đúng cạnh phải khung range, còn phần giá
  chạy tiếp lên 4839 thì nằm **ngoài** range đã vẽ.
- **Nghi phạm trong thuật toán:** mục 7 — Phase E được "chốt" ngay tại nến giá đi đủ **1.0 × chiều cao
  range** (4806.7 + 21.0 = 4827.7), rồi range đóng luôn. Nên cho Phase E kéo tới khi hết đà (vd tới khi
  giá lùi lại quá x% mục tiêu) chứ đừng đóng ở đúng nến chạm đích.

### 3. Nguyên nhân mỏng so với kết quả — *cảnh báo, không phải lỗi nhãn* — L: THEORY §2.2 (Nhân-Quả)
- MOVE trước climax chỉ **47.1 giá / 60 nến / hiệu suất 0.38** — sát ngưỡng 0.35, tức đợt tăng bị chặn
  không mạnh. Chiều cao range 21.0 giá cũng nhỏ. Cấu trúc vẫn hợp lệ và đã chạy đúng, nhưng "nguyên
  nhân" mỏng → không nên kỳ vọng mục tiêu lớn. Ghi nhận để đừng dùng bài này biện minh cho việc nới
  ngưỡng hiệu suất xuống dưới 0.35.
- Đáng để người viết code biết: **cả 5 bài trong lô đều có hiệu suất hướng 0.38–0.50**, tức toàn bộ nằm
  sát cửa 0.35. Ngưỡng này đang là chỗ quyết định, rất nhạy — cần quét tham số.

### 4. LPS[C] nằm ở 66% chiều cao range — *ghi nhận, hợp lệ*
- LPS[C] = 4799.5, tức không phải một nhịp lùi về sát biên dưới mà là một test cao trong range. Theo
  cách gán ngược (mục 6: lấy đáy sâu nhất trong 60 nến trước cú phá) thì đúng, và bối cảnh cũng đúng
  (giá cuộn lên cao dần trước khi bung). Không sửa — nhưng nhớ đây là **case khó** (không có cú rũ nào),
  nên Phase C ở bài này là suy ngược, không phải quan sát trực tiếp.

## Đạt
- **L1** — MOVE tăng thật bị chặn; BCLX 4806.7 **đúng là đỉnh** của move (các nến sau đều thấp hơn:
  4801.6 / 4802.9 / 4803.7 / 4799.8 / 4798.7). Bài **duy nhất trong 5 bài** gắn climax đúng cực trị.
- **L2** — đủ 3 lần đổi hướng thật: move tăng bị BCLX 4806.7 chặn → AR 4785.7 → quay lại đúng mức climax
  (4806.6 vs 4806.7) rồi bị chặn. Và ST[A] có **VSA 0.21x, thân 0.00** — test cạn khối lượng kinh điển,
  đúng định nghĩa ST (spread/volume co lại khi tiếp cận vùng climax). Phase A kết thúc đúng tại ST[A].
- **L3** — biên chính 4785.7–4806.7 **khớp đúng** mức AR + mức climax, không bị kéo theo giá. Biên phụ:
  dưới 4783.2 do **DA** tạo, trên 4810.9 do **nhịp ST[A] vượt climax** tạo — đúng cả hai nguồn L3 cho
  phép, mỗi bên đúng 1 cái.
- **L3 (SOS mạnh)** — SOS 4817.0 đóng cửa **bứt qua biên phụ trên 4810.9** (+6.1 giá), và biên phụ đó
  hình thành từ **trước** cú phá → điều kiện kiểm được, không vòng tròn (khác #01 và #02).
- **L4** — BCLX + phá lên = **Tái tích luỹ**, tên đúng; kết quả cũng đúng (giá lên 4839.0).
- **L7** — LPS[C] đúng **một điểm**; DA một điểm; không có nhãn nào spam.
- **L8** — Phase C = 20 nến, ngắn nhất (cùng Phase D). Đúng.
- **L9** — Phase B = **61 nến, dài nhất** (A=44, C=20, D=20, E=1). Bài **duy nhất trong 5 bài** không
  vi phạm L9.
- **L10** — CBR đọc được: SOS phá biên → giá giữ ngoài biên → đi tiếp tìm vùng giá mới (4814–4839).
- **Effort ↔ result** đọc được thật: panel khối lượng cho thấy cụm nỗ lực lớn ở nửa đầu (16:29–17:30)
  rồi **co lại** suốt Phase B (18:00–20:22), rồi bùng lại ở SOS — đúng dấu hiệu #2 của tài liệu (volume
  giảm dần B rồi tăng ở D), chỉ đảo chiều cho tích luỹ.

## Cần hỏi người học
- Không có.
