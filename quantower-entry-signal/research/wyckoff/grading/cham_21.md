# Chấm bài #21 — Tái phân phối (RE-DIST) · 2026-06-08 01:30 → 06:01 (271 nến M1)

**Điểm: 7/10** — Cấu trúc đọc đúng, chỉ phải sửa nhãn ở cú phá: SOW neo sai cây và Phase D vẽ như "giữ được ngoài biên" trong khi giá đã đóng cửa lùi hẳn vào trong range.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SOW neo vào nến XÁC NHẬN, không neo vào cây phá — luật vi phạm: mục 9 (nhãn sai vai) + Ca #5 nguồn 4.pdf (neo mốc theo giá đóng cửa của nến mốc)
- **Thuật toán gắn:** SOW tại 05:36, giá 4304.8, VSA 2.20x, thân 0.71.
- **Đúng phải là:** MSOW tại **05:34** — O4325.0 H4325.5 L4310.7 **C4311.2**, v=871 (**VSA 7.36x**), thân **0.93**. Chính cây này đóng cửa 12.4 giá dưới biên chính 4323.6 và mở toàn bộ cú rơi. Cây 05:36 chỉ là nến giữ ngoài biên thứ ba, đã cách cây phá 6.4 giá.
- **Dấu hiệu quyết định trên chart:** thanh khối lượng vàng cao nhất cả range nằm ở 05:34 (871 lot) và 05:35 (800 lot), nhãn SOW lại nằm ở cây 370 lot ngay sau đó.
- **Nghi phạm trong thuật toán:** `BREAK_HOLD_BARS = 3` — máy phát nhãn tại nến thoả điều kiện thứ 3 mà không quay lại neo nhãn vào nến phá đầu tiên của cụm.

### 2. Phase D vẽ như CBR thành công, thực tế retest THẤT BẠI — luật vi phạm: L10
- **Thuật toán gắn:** Phase D 26 nến (05:36 → 06:01), range "completed", không có Phase E.
- **Đúng phải là:** cú phá **đạt mục tiêu nhưng không giữ được biên**. Đáy 4293.0 (05:37) = 30.6 giá dưới biên = **98% chiều cao biên chính (31.2 giá)** → đã quá mốc 50%, phải chốt **Phase E**; nhưng ngay 06:01 giá đóng **4329.8** (6.2 giá = 62 tick *trong* range), 06:02 đóng 4330.6, và tới 07:25 lên tận **4342.0** (59% chiều cao range vào lại bên trong). Phải ghi rõ "SOW đạt mục tiêu, retest hỏng", không phải một Phase D êm ả rồi đóng range.
- **Dấu hiệu quyết định trên chart:** 4 nến cuối cùng bên phải vạch Phase D đã nằm trên đường liền 4323.6.
- **Nghi phạm trong thuật toán:** trong `_try_lps_and_phase_e()`, nhánh `if failed: return False` chạy **trước** nhánh kiểm 50% ở cuối cửa sổ → cú phá đã đi 98% mà hồi vào range thì mất luôn Phase E. Đồng thời giá trị trả về `False` bị **bỏ** tại call site (dòng ~604) nên range vẫn được đóng và đặt tên ở Phase D.

### 3. LPSY[C] chọn bằng cực trị 60 nến, rơi vào nến mỏng nhất vùng — luật vi phạm: mục 8 (effort vs result), nhẹ
- **Thuật toán gắn:** LPSY[C] 05:04 @4340.1, v=**23 lot**, VSA 0.90x.
- **Đúng phải là:** 4340.1 đúng là đỉnh cao nhất Phase C nên vị trí không sai, nhưng nó nằm ở **đầu** Phase C, cách cú phá 32 nến. Nhịp hồi yếu cuối cùng ngay trước khi phá (05:29–05:33, đỉnh 4328.0) không được gắn nhãn nào — đó mới là "đợt phục hồi yếu trên biên hẹp" theo định nghĩa LPSY.
- **Nghi phạm trong thuật toán:** Phase C gán ngược lấy **đúng cực trị** trong cửa sổ 60 nến, không đòi nhịp test phải sát cú phá (mục 12.8 của tài liệu thuật toán đã tự nghi chỗ này).

### 4. Biên chỉ được chạm 1 lần mỗi bên trong suốt 163 nến Phase B — luật vi phạm: WY17 / mục "số lần chạm" CHART_CASES, nhẹ
- Phase B: đỉnh 4346.4 (còn cách biên trên **8.4 giá**), đáy 4327.4 (còn cách biên dưới **3.8 giá**) → không lần nào chạm biên, nên cả 163 nến không có một nhãn nào.
- Theo CHART_CASES, biên dưới thường cần 2–3 lần chạm mới được công nhận. Ở đây range chỉ có bằng chứng từ đúng cây climax và cây AR — độ tin cậy mỏng, dù không sai luật nào của L1–L10.

## Đạt
- **L1:** MOVE thật 53.9 giá / 62 nến / hiệu suất 0.40; climax VSA 3.55x, biên độ 14.9 giá, thân 0.85, và **là đáy thấp nhất thật của Phase A** — cây climax đang chặn move, không nằm giữa move.
- **L2:** đủ 3 lần đổi hướng; AR 4354.8 = đỉnh thật của Phase A, cách climax 31.2 giá = 58% độ dài move; ST[A] hồi 63% và bị chặn lại.
- **L3:** biên chính = climax + AR, cố định; không có biên phụ và đúng là chưa từng có giá ngoài biên trước cú phá.
- **L4:** origin SC + phá xuống = **Tái phân phối** — đúng, và khớp kết cục (sau khi hồi, giá rơi tiếp về 4309.6 lúc 08:27).
- **L9/L8:** Phase B 163 nến = dài nhất (60% range); Phase C 32 nến ngắn hơn cả A và B.
