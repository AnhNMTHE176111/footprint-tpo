# Chấm bài #07 — Tái tích lũy (RE-ACC) · 2026-04-13 16:47 → 2026-04-14 06:26 (265 nến M1)

**Điểm: 7/10** — Khung range vẽ đúng, tên đúng, Phase D/E sạch; phải sửa 2 nhãn: bỏ ST[B] và kéo Phase C về đáy cuối cùng.

## Lỗi (nặng → nhẹ)

### 1. Còn dùng nhãn ST[B] — luật vi phạm: L6
- **Thuật toán gắn:** `ST[B] 2026-04-13 18:27 · 4783.2 · Phase B`.
- **Đúng phải là:** L6 đã bỏ hẳn ST[B]. Điểm này giá 4783.2 nằm **dưới biên chính dưới 4785.7** 2.5 giá, tức nó **phá biên** chứ không phải "test nhẹ trong range" → phải gọi **DA** (test biên dưới), và vì đây chính là cực trị xa nhất phía dưới nên nó là điểm sinh **biên phụ dưới 4783.2** (thuật toán đã vẽ đúng biên phụ nhưng gán sai tên sự kiện).
- **Dấu hiệu quyết định trên chart:** phiếu ghi biên chính dưới 4785.7, biên phụ dưới 4783.2, và nhãn ST[B] đúng bằng 4783.2 — tức nhãn ST[B] và biên phụ là cùng một cây nến.
- **Nghi phạm trong thuật toán:** nhánh gán ST[B] chưa bị gỡ khỏi bộ nhãn; và bộ phân loại test không so giá test với biên chính trước khi đặt tên (nếu giá vượt biên → phải rẽ sang DA/UT/Spring, không được rơi về ST[B]).

### 2. Phase C neo lửng giữa range, không neo đáy cuối cùng — luật vi phạm: L8
- **Thuật toán gắn:** `LPS[C] 20:38 · 4799.5`, Phase C = 20:38 → 23:03.
- **Đúng phải là:** với range 4785.7–4806.7, mức 4799.5 nằm ở **65% chiều cao range tính từ đáy** — đó là một điểm nghỉ giữa đường đi lên, không phải "tín hiệu đầu tiên giá ở biên này bắt đầu phá biên kia". Đáy hồi cuối cùng của Phase B nằm ở vùng 4785–4787 (khoảng 19:15–19:30 trên ảnh, ngay trên biên chính dưới) — LPS[C] phải neo ở đó, Phase C bắt đầu từ đó.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, từ đáy vùng 19:2x giá đi một mạch không thoái lui đáng kể tới SOS 4824.7; điểm 4799.5 chỉ là một nến nghỉ giữa chân sóng đó.
- **Nghi phạm trong thuật toán:** sau khi bỏ ràng buộc "đúng nửa range", điều kiện "gần biên" còn lại quá lỏng — 65% chiều cao vẫn được nhận là LPS[C] ở biên dưới. Cần buộc LPS[C] nằm trong ~1/3 dưới range (và LPSY[C] trong 1/3 trên).

### 3. Nhãn climax lệch cực trị (lỗi đã biết, chưa sửa) — ghi nhận
- Phiếu ghi "nhãn climax mang VSA=2.72x", trùng luôn nến mở range 16:47 với high 4806.7 = biên chính trên → **ca này KHÔNG bị lỗi**. Ghi nhận là điểm sạch.

## Đạt
- **L1:** MOVE tăng 42.4 giá / 60 nến bị chặn đúng tại cây BCLX (high 4806.7 = cực trị của move) — mở range hợp lệ.
- **L2:** đủ 3 lần đổi hướng: BCLX 16:47 → AR 4785.7 (17:08) → ST[A] 4810.9 (17:27). ST[A] hồi 120% khoảng AR↔climax, vượt hẳn mức climax → là test thật vùng climax, không lửng. Phase A kết thúc đúng tại ST[A].
- **L3:** biên chính 4785.7/4806.7 = đúng AR + climax, không bị kéo theo giá; mỗi bên đúng 1 biên phụ (4810.9 do ST[A], 4783.2 do cú phá xuống); tỷ lệ phụ/chính 1.32x — cấu trúc chặt.
- **L4:** move tăng → BCLX, phá lên thật (SOS 4824.7) → RE-ACC. Tên đúng.
- **L9/L8:** Phase B 69 nến dài nhất trong A–D, Phase C 16 nến ngắn nhất. Trật tự độ dài đúng.
- **L10:** SOS 4824.7 đóng cửa vượt **biên phụ trên 4810.9** (không chỉ biên chính) — đúng yêu cầu "SOS thật sự mạnh"; LPS[D] 4814.6 hồi về vẫn **giữ trên biên phụ**; Phase E 121 nến giá đi tìm vùng giá mới tới 4862. Đây là chuỗi D+E = CBR đúng sách.
- **Khối lượng:** SOS VSA 1.94x kèm thân nến 1.00, LPS[D] VSA 1.18x (co lại) — quan hệ nỗ lực/kết quả ở Phase D đọc được, không mâu thuẫn.
