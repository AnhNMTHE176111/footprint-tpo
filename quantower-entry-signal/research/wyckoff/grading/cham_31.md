# Chấm bài #31 — Tích lũy (ACC) · 2026-06-30 12:56 → 14:23 (87 nến M1)

**Điểm: 7/10** — Cấu trúc đọc được, tên range đúng, Phase A chuẩn; sửa 3 nhãn: mức SC, mốc SOS, và ranh giới Phase B/C.

## Lỗi (nặng → nhẹ)

### 1. SOS neo sai nến — nến phá thật bị đẩy vào trong Phase C — luật vi phạm: L10 + mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOS tại 14:16, giá 4059.7, **VSA 0.69x**, thân 0.55.
- **Đúng phải là:** SOS tại **14:09** — nến bứt biên chính trên 4047.5: O4045.0 → C4058.0, **VSA 4.17x**, thân 0.87. Nến sau (14:10) VSA 2.93x. Đó mới là "spread mở rộng + volume tăng" của định nghĩa SOS.
- **Dấu hiệu quyết định trên chart:** thanh khối lượng cao nhất toàn ảnh nằm ở 14:09 (1149 lot), còn nến được gán SOS chỉ 252 lot — thấp hơn cả TB 20 nến. Hệ quả kèm theo: **Phase D chỉ bắt đầu ở 14:16**, nên cây phá vỡ thật (14:09) bị vẽ nằm **trong Phase C** — sai vai phase.
- **Nghi phạm trong thuật toán:** `BREAK_HOLD_BARS = 3` đòi **3 nến LIÊN TIẾP** cùng thoả `thân ≥ 45%`; chuỗi thân thực tế 0.87 / 0.43 / 0.65 / 0.25 / 0.06 / 0.76 / 0.51 / 0.55 nên bộ đếm bị reset 3 lần, và `_fire_break()` stamp sự kiện tại nến xác nhận `i` chứ không tại `k['start_i']`.

### 2. Mức SC không phải đáy thật của đợt bán tháo — luật vi phạm: L3 (biên chính) + CHART_CASES lỗi #6
- **Thuật toán gắn:** SC = 4024.1 (nến 12:56) → biên chính dưới 4024.1.
- **Đúng phải là:** đáy của cụm bán tháo là **4022.1 tại 12:58** (VSA 2.60x, thân 0.70, đóng 4022.7 sát đáy). SC nên là 12:58, hoặc coi 12:55-12:58 là một cụm climax và lấy 4022.1 làm mức biên.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu, nến +2 sau climax có L = 4022.1 < 4024.1. Biên chính dưới bị phá **2 nến sau khi vừa được lập** → nó không phải một mức hỗ trợ. Đường nét đứt 4022.1 trên ảnh vì thế không phải "cú thăm dò phá range" (đúng nghĩa L3) mà chỉ là phần đuôi của chính cây climax.
- **Nghi phạm trong thuật toán:** mục 3 mở range ngay tại nến đầu tiên thoả climax; không có bước "dời mức climax xuống cực trị thấp/cao hơn trong N nến kế tiếp nếu vẫn cùng cụm bán/mua tháo".

### 3. Phase A (42 nến) dài hơn Phase B (22 nến) — luật vi phạm: L9
- **Thuật toán gắn:** A 42 · B 22 · C 16 · D 7 · E 1.
- **Đúng phải là:** Phase B phải là phase dài nhất (giai đoạn xây nguyên nhân). Ở đây "nguyên nhân" chỉ có 22 nến trong khi Phase A ngốn 42 nến.
- **Dấu hiệu quyết định trên chart:** ST[A] tại 13:37 chốt Phase A rất muộn; toàn bộ nhịp 12:56→13:37 (climax→AR→ST[A]) chiếm gần một nửa range.
- **Nghi phạm trong thuật toán:** không có lỗi tham số cụ thể — đây là hệ quả của việc range chỉ dài 87 nến: cấu trúc quá vụn để phân bổ 5 phase. Trên M1, range 87 nến với đủ A→E vẫn nằm trong vùng đáng nghi "nhiễu chứ không phải vùng đấu giá thật".

### 4. Phase E = 1 nến (lỗi TRÌNH BÀY)
- Phase E chỉ dài đúng 1 nến (14:23) vì mốc "đi thêm 1.0 × chiều cao range" đạt ngay tại nến đóng range. Đọc trên ảnh thì Phase E gần như vô hình, dù thực tế giá còn chạy tới 4078 sau đó. Nên vẽ Phase E tới hết cửa sổ 25 nến để nhìn được, hoặc ghi rõ "E đạt tại nến đầu".

## Đạt
- **L1 — điều kiện mở range:** có MOVE giảm thật (27.3 giá / 70 nến / hiệu suất 0.38) bị cây VSA 3.06x chặn lại — không phải nổ volume giữa lúc đi ngang.
- **L2 — Phase A đủ 3 lần đổi hướng:** climax → AR (4047.5, bật 23.4 giá = 86% độ dài move) → ST[A] 4027.2 hồi **87%** chiều cao về sát vùng SC, VSA co lại **1.09x** — đúng sách (ST volume/spread giảm). Đây là ST[A] tốt nhất trong cả lô 31-35.
- **L4 — tên range:** origin SC + phá lên = Tích luỹ. Đúng.
- **L3 — biên phụ:** mỗi bên tối đa 1, phía trên không sinh biên phụ vô cớ. Đúng.
- **L7 — LPS[C] chỉ 1 điểm.** Đúng. Vị trí (14:00, 4039.5) là nhịp hồi cuối trước cú bứt — vai LPS hợp lý; VSA 2.76x + thân 0.37 ở nhịp này đọc được là **hấp thụ** (nỗ lực lớn, kết quả nhỏ, đúng chiều mua), không phải lỗi.
- Không có nhãn spam, không thiếu nhãn bắt buộc.

## Cần hỏi người học
- Không có.
