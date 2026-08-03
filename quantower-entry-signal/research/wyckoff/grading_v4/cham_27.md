# Chấm bài #27 — Tái tích lũy (RE-ACC) · 2026-06-21 23:04 → 2026-06-22 00:51 (107 nến M1)

**Điểm: 6/10** — bài **tốt nhất** trong lô #26–#30: Phase D/E là một CBR chuẩn, đọc được bằng số. Nhưng nhãn AR **lệch hẳn** khỏi biên chính mà chính nó phải tạo ra (lỗi vẽ/logic, phải sửa), Phase A ăn 54% range, và Phase C bị đẩy ra **ngoài** range.

## Lỗi (nặng → nhẹ)

### 1. Nhãn AR không khớp biên chính do chính nó sinh ra — luật vi phạm: L3 (biên chính = climax + AR)
- **Thuật toán gắn:** AR tại 23:40, giá **4158.0**; nhưng biên chính dưới vẽ ở **4152.9** — lệch **5.1 giá = 21% chiều cao range (24.0)**.
- **Đúng phải là:** AR = **4152.9 tại 23:48**. Đó mới là đáy của cú phản ứng sau BCLX; điểm 23:40 chỉ là một chỗ nghỉ giữa đường rơi (sau nó giá còn giảm thêm 5.1 giá nữa).
- **Dấu hiệu quyết định trên chart:** nhãn AR nằm rõ **phía trên** đường liền "bien CHINH duoi 4152.9"; đọc số: 23:47 (volume 187, VSA **3.10×**, L=4153.2) rồi 23:48 (L=**4152.9**) mới là cú bán cuối, còn nến 23:40 chỉ có volume 57 (0.86×).
- **Nghi phạm trong thuật toán:** `wyckoff_schematic.py` dòng 377–379 — khi giá phá xa hơn AR, code cập nhật `r.ar_i / r.ar_price` (nên `solid_low` thành 4152.9) nhưng **không cập nhật event AR đã `add_event()` ở dòng 345**. Nhãn và biên vì thế nói hai chuyện khác nhau. Gốc rễ: cửa sổ `AR_LOOKBACK = 40` nến cố định (đúng mục 12.2 "chỗ nên nghi ngờ" trong tài liệu thuật toán) — AR thật xảy ra ở nến thứ 44.

### 2. Phase A = 58 nến, dài hơn Phase B gấp 3.2 lần — luật vi phạm: L9
- **Thuật toán gắn:** A=58 (54% range) · B=18 · C=11 · D=20 · E=1.
- **Đúng phải là:** Phase A kết thúc tại cú chặn 23:48–23:56 (≈45–52 nến), và Phase B — đoạn đàm phán 4152.9–4176.9 — phải là phase dài nhất.
- **Nghi phạm trong thuật toán:** cùng lỗi hệ thống như bài #26 — Phase A không thể ngắn hơn `AR_LOOKBACK + 1 = 41` nến vì nhánh tìm AR chỉ chốt tại nến cố định `climax_i + 41`.

### 3. LPS[C] nằm NGOÀI biên chính → Phase C bị gán vào nhịp đã bứt phá — luật vi phạm: L8 + Ca #3 nguồn 4.pdf (lẫn LPS[C] với LPS[D])
- **Thuật toán gắn:** LPS[C] tại 00:20, giá **4178.9** — cao hơn biên chính trên **4176.9**.
- **Đúng phải là:** nhịp test cuối **bên trong** range trước khi bung là đáy cao dần 00:07 (L=4160.0) / 00:08 (L=4161.3). Điểm 00:20 nằm ngoài biên chính, đúng vai **BU / LPS sau khi vượt creek**, tức thuộc nhóm Phase D — không phải LPS[C].
- **Dấu hiệu quyết định trên chart:** nhãn LPS[C] nằm giữa đường liền 4176.9 và đường đứt 4181.5, tức đã ở ngoài range. Giá đã đóng cửa trên 4176.9 từ 00:13 (C=4176.9) và dứt khoát ở 00:14 (C=4177.6).
- **Nghi phạm trong thuật toán:** `_retro_phase_c()` dòng 623 — cửa sổ = min(60, nửa Phase B) = min(60, (00:31−00:02)/2 = 14) → chỉ được nhìn lại từ 00:17, lúc đó giá đã ở ngoài biên.

### 4. Chất lượng MOVE mở range chủ yếu do nến mở lại tuần, không do lực mua — luật vi phạm: L1 (điều kiện CẦN)
- **Thuật toán gắn:** MOVE tăng 25.5 giá / 64 nến, hiệu suất hướng 0.38 (ngưỡng là 0.35 — sát mép).
- **Đúng phải là:** chân MOVE là **đáy 4151.4 của nến 06-21 22:00, đúng nến đầu tiên sau khe cuối tuần** (`since_gap = 0`). Riêng nến đó đã đi 15.1 giá = **59% cả MOVE**; 63 nến còn lại chỉ nhích 4164 → 4176 và loanh quanh. Đó là gap-fill, không phải một move xu hướng do cầu đẩy.
- **Dấu hiệu quyết định trên chart:** nến mở lại tuần có volume **346**, gấp **3×** chính cây gọi là BCLX (116). "Cao trào mua" mà nỗ lực nhỏ hơn nến mở phiên 3 lần thì rất khó gọi là cao trào — thêm nữa 23:04 UTC tối Chủ nhật là giờ thanh khoản mỏng nhất tuần (các nến liền trước chỉ 10–28 lot), VSA 4.48× ở đây là hiệu ứng chia cho mẫu số bé.
- **Nghi phạm trong thuật toán:** phép đo MOVE không loại nến `since_gap = 0`; hiệu suất hướng bị khe giá làm đẹp lên (khe đi thẳng một mạch nên không bị trừ quãng đường lắc). Đề xuất: bỏ nến gap khỏi phép đo MOVE, và thêm điều kiện volume **tuyệt đối** cho climax bên cạnh VSA tương đối.

## Đạt
- **Mục 4 (L4):** tên range đúng — origin BCLX + phá lên = **Tái tích luỹ**.
- **Mục 7 (L10) — làm tốt nhất bài này:** SOS 00:31 → LPS[D] 00:34 (4183.0, hồi về đúng biên vừa phá 4181.5 mà **giữ được** ở ngoài) → giá đi tiếp đủ 1.0× chiều cao range (mốc 4205.5, đạt tại 00:51 với H=4206.5) → Phase E. Đây đúng là mô hình CBR như L10 mô tả.
- **Mục 8 (Effort vs Result):** volume tăng dần theo cú phá — 00:43 2.34× · 00:45 2.29× · 00:48 2.82× · 00:49 2.83×. Nỗ lực khớp kết quả, không phải phá vỡ rỗng.
- **Mục 9:** không có nhãn spam; LPS[C]/LPS[D] tách vai đúng theo trước/sau SOS; mỗi nhãn 1 điểm (L7).
- **Mục 6 (một phần):** Phase C = 11 nến, đúng là phase ngắn nhất (L8) — sai ở **vị trí**, không sai ở **độ dài**.
