# Chấm bài #14 — Tái tích luỹ (RE-ACC) · 2026-05-06 03:20 → 08:12 (159 nến M1)

**Điểm: 1/10** — **Không được vẽ range ở đây.** Không có climax, range cao 7.5 giá trên vàng 4690 (0.16%) trong phiên Á thanh khoản 1–3 hợp đồng: đây là nhiễu, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Không có cao trào nào — luật vi phạm: L1 (climax là điều kiện ĐỦ, ở đây thiếu luôn) + mục 3(1) của chính spec
- **Thuật toán gắn:** BCLX, mức climax 4695.2 tại nến 03:20 — **VSA 0.58x, biên độ nến 1.0 giá, volume 3 hợp đồng**.
- **Đúng phải là:** nến mở range phải có biên độ ≥ 1.4× TB 20 nến **và** VSA ≥ 2.2x. Nến này **không thoả cả hai**. Không có cao trào thì không mở range.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax — 11/12 nến có volume 1–8 hợp đồng, 5 nến là doji O=H=L=C. Panel volume quanh 03:20 phẳng.
- **Nghi phạm trong thuật toán:** cơ chế **cụm climax** (mục 4.0) dời mốc climax sang cực trị giá mới trong 8 nến đầu, nhưng **không kiểm lại điều kiện climax tại mốc mới**. Nến gốc 02:56 (VSA 10.10x) thoả; mốc bị dời sang 03:20 (VSA 0.58x) thì range đứng trên một cây rác. Phải: dời mốc chỉ khi nến mới **vẫn** thoả ngưỡng, hoặc giữ mức = cực trị nhưng bỏ range nếu cực trị đó không có nỗ lực nào đỡ.

### 2. Nhãn BCLX vẽ ở 4684.5, thấp hơn cả biên chính dưới 4687.7 — luật vi phạm: L3 (biên chính = mức climax) + lỗi trình bày nặng
- **Thuật toán gắn:** nhãn BCLX ở giá 4684.5, mức climax ở 4695.2 — lệch **10.7 giá**, tức 1.4 lần chiều cao cả range, và nhãn nằm **hẳn ngoài khung range** phía dưới.
- **Đúng phải là:** tách nhãn/mức là cơ chế hợp lệ của v6, nhưng phải kèm trần: nếu nến mang nhãn cách mức climax quá (ví dụ) 0.5× chiều cao range thì cụm đó không phải một cụm — hai sự kiện khác nhau, và bản thân điều đó chứng minh climax không chặn được gì.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm BCLX đỏ nằm bên dưới cả đường "biên CHÍNH dưới 4687.7" — người đọc không thể hiểu climax ở đâu.

### 3. Climax không chặn được move — giá đi tiếp hẳn ra ngoài rồi range vẫn sống 139 nến "Phase B" — luật vi phạm: L1 + mục 4.0 guard "climax không chặn được move"
- **Thuật toán gắn:** Phase B từ 03:48 tới 07:57 (139 nến).
- **Đúng phải là:** từ 04:05 tới 07:39, **toàn bộ nến nằm trên cả biên chính trên 4695.2 và biên phụ trên 4699.2**, dao động 4700–4712. Giá đã bỏ range đi từ 04:05; SOS phải nằm ở đó, không phải ở 07:59.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, dải nến ở giữa chart chạy hẳn trên hai đường cam; SOS gán tại 4728.0 = **33 giá trên biên chính** = 4.4 lần chiều cao range.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #13 — ngưỡng "3 nến đóng vượt biên phụ +30 tick, thân ≥45%" đo bằng tick tuyệt đối, vô nghĩa với range chỉ 7.5 giá; guard "vượt mức climax quá 3× biên độ TB" chỉ áp trong 8 nến đầu nên không bắn về sau.

### 4. Thiếu Phase C — luật vi phạm: L8
- A(12) → B(139) → D(7) → E(2), nhảy thẳng B sang D. Cơ chế gán ngược lại không chạy, giống bài #13.

### 5. ST[A] không test lại vùng climax — luật vi phạm: L2
- ST[A] tại 4692.4, tức giữa 4687.7–4695.2. Trên một range 7.5 giá thì mọi điểm đều "giữa range" — thêm một bằng chứng nữa range này không tồn tại.

### 6. Phase E chỉ 2 nến — lỗi J của vòng v5 tái xuất ở dạng nhẹ
- Sau khi vá, Phase E phải có độ dài thật (tới khi lùi vào biên / đi 2× chiều cao / 120 nến). Ở đây 2 nến. Với chiều cao range 7.5 giá thì mốc "2× chiều cao" = 15 giá bị đạt ngay lập tức → Phase E co về gần 0. Range quá hẹp làm mọi mốc đo theo chiều cao vô nghĩa.

## Đạt
- MOVE trước climax có thật: 91.7 giá / 137 nến, hiệu suất 0.36 — nhìn ảnh là một chân tăng rõ từ 4590 lên 4695. Riêng phần này đo đúng.
- Tên range (L4): BCLX + phá lên = Tái tích luỹ. Đúng logic 4 mẫu hình (nhưng vô nghĩa vì range không hợp lệ).
- Chỉ số Phase B: SOT trên n=2, tỷ lệ volume nhịp cuối/đầu 1.62 → gắn "HẤP THỤ" — đọc đúng bản chất về mặt số học.

## Cần hỏi người học
- Đã chốt "không đặt sàn độ dài tối thiểu cho range". Nhưng còn **sàn CHIỀU CAO**? Range 7.5 giá = 0.16% giá vàng, nhỏ hơn cả biên độ một nến M1 giờ Mỹ. Có nên đặt sàn kiểu "chiều cao biên chính ≥ 3× biên độ TB 20 nến" để chặn nhóm range phiên Á này?
