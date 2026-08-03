# Chấm bài #35 — Tích lũy (ACC) · 2026-07-07 19:15 → 2026-07-08 04:06 (470 nến M1)

**Điểm: 3/10** — Vùng cân bằng đêm là thật và tên range đúng chiều, nhưng **cái gọi là Spring không phải Spring** (không phá được đáy TR), lại bị gắn oan "thất bại", và SOS neo vào một nến **11 lot** trong khi cây phá thật to gấp 23 lần.

## Lỗi (nặng → nhẹ)

### 1. "Spring" 4104.0 không phải điểm thấp nhất của TR — luật vi phạm: L3 + CHART_CASES lỗi #6 (2.pdf, lỗi lặp nhiều nhất: 4/22 ca)
- **Thuật toán gắn:** `Spring (thất bại)` tại 22:01, giá **4104.0** (VSA 2.92x, thân 0.70).
- **Đúng phải là:** đáy thấp nhất của range là **4102.7**, đã lập từ **19:18** (2 giờ 43 phút trước). Giảng viên phát biểu tường minh: "Spring bắt buộc phải là điểm giá **THẤP NHẤT trong suốt Trading Range** — nếu đáy nghi ngờ không phá đáy cũ, dù hình dáng giống Spring vẫn chỉ là ST/LPS thường". Ở đây phải gọi là **test biên dưới / LPS**, không phải Spring, và **không** được mở Phase C từ nó.
- **Dấu hiệu quyết định trên chart:** chấm Spring nằm **trên** đường nét đứt 4102.7 — nhìn ảnh thấy ngay.
- **Nghi phạm trong thuật toán:** mục 5.1 + mục 10 đo cú rũ bằng **biên CHÍNH** (`r.solid_low = 4107.3`) nên cú thăm dò sâu 33 tick dưới nét liền tự động thành "cú rũ THẬT". Phải đo bằng **biên PHỤ** (`r.low`), giống điều kiện đã áp cho SOS/SOW. (Cùng gốc lỗi với UTAD #2 của bài #32.)

### 2. SOS neo vào nến 11 lot, thân 0.29 — dưới cả ngưỡng thân của chính spec — luật vi phạm: mục 8 (Effort vs Result) + L10
- **Thuật toán gắn:** SOS 03:41, giá 4137.1, **VSA 0.36x / 11 lot**, thân **0.29** (spec đòi thân ≥ 0.45).
- **Đúng phải là:** cây phá thật là **03:01: 252 lot, VSA 6.30x**, thân 0.85, O4131.5 → C4139.3 — bứt hẳn qua biên phụ 4137.1. SOS phải nằm ở đó, muộn nhất là 03:08 (VSA 1.46x, thân 0.77).
- **Dấu hiệu quyết định trên chart:** cụm nến tăng dốc ở 03:00-03:12 kèm thanh khối lượng nhô rõ; chấm SOS thì đặt ở đoạn giá đã đi ngang 4136-4138, khối lượng gần bằng 0.
- **Nghi phạm trong thuật toán:** SOS bắn bằng `BREAK_MAX_WAIT = 40` (ở ngoài biên quá 40 nến) chứ không bằng 3 nến quyết đoán — nên nhãn rơi đúng nến thứ 41 bất kể nến đó là gì, **bỏ qua cả điều kiện thân ≥ 45%**. Lặp lại y hệt bài #34.

### 3. Cú rũ bị gắn "(thất bại)" dù đã đạt 60% sang biên đối diện — luật vi phạm: THEORY §5 (mục tiêu tối thiểu 50%) + L8
- **Thuật toán gắn:** status `failed`.
- **Đúng phải là:** từ 4104.0 giá lên tới **4118.9 (23:10)** = **60%** quãng đường sang biên chính trên 4128.9 — vượt ngưỡng xác nhận 50%.
- **Nghi phạm trong thuật toán:** nhánh `SHOCK_MAX_WAIT` ghi đè `status = 'failed'` lên cả trường hợp đã `'confirmed'` (bug đã nêu ở bài #33).

### 4. ST[A] dừng đúng giữa range, không test vùng SC — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 20:23 giá 4117.3, VSA **0.38x** — hồi 54% chiều cao (điểm giữa range = 4118.1).
- **Đúng phải là:** ST[A] phải quay về **tiệm cận mức SC 4107.3**. Sau khi ST[A] được chốt, giá còn đi xuống thêm **13 giá** (tới 4104.0) — bằng chứng rõ là lần đổi hướng thứ 3 chưa xảy ra ở 20:23.
- **Dấu hiệu quyết định trên chart:** chấm ST[A] treo giữa hai đường nét liền; đỉnh cao nhất sau nó chỉ 4121.8 (20:26) rồi giá trượt liên tục xuống Spring.
- **Nghi phạm trong thuật toán:** `STA_MIN_RETRACE = 0.40` + `STA_CONFIRM_BARS = 5` (lặp lỗi #33, #34).

### 5. Mức SC không phải đáy thật — L3
- SC = 4107.3 (19:15) nhưng chỉ **3 nến sau** (19:18) đã có L = **4102.7**. Biên chính dưới bị phá gần như ngay lập tức, và biên phụ 4102.7 sinh ra từ **chính đợt bán tháo climax**, không phải từ một cú thăm dò phá range như L3 mô tả. Đây cũng chính là nguyên nhân gốc của lỗi #1.

### 6. Phase C 121 nến, dài thứ hai toàn range — L8
- A 69 · B 37 · **C 121** · B 218 · D 26. Phase B (tổng 255) là dài nhất — đúng L9 — nhưng Phase C phình bằng đúng `SHOCK_MAX_WAIT` (lặp lỗi #32, #33).

### 7. Phase D chỉ đi 4.9 giá / 21.6 giá chiều cao range mà range vẫn "completed" — L10
- Sau SOS, cực trị chỉ tới **4140.2 (03:49)**, tức 4.9 giá trên biên 4137.1 (**23%** chiều cao range), rồi giá lùi về 4132.5. `_try_lps_and_phase_e()` trả `False` nhưng `_fire_break()` vẫn đóng range và đặt tên (bug lặp ở #32, #34).

### 8. Range 470 nến gồm nguyên phiên đêm Á — cảnh báo bối cảnh (không phải lỗi luật)
- Từ 22:00 tới 03:00 khối lượng nến rớt về 3-30 lot. VSA (chuẩn hoá theo TB 20 nến) trong đoạn này **mất ý nghĩa** — mọi kết luận "nỗ lực ↔ kết quả" ở nửa phải ảnh đều không có nền thanh khoản để đứng. Nên gắn cờ "range hình thành trong phiên thanh khoản chết" thay vì chấm effort/result như phiên Mỹ.

## Đạt
- **L1:** MOVE giảm 52.5 giá / 104 nến / hiệu suất 0.43 bị cây VSA 2.94x (823 lot) chặn — điều kiện CẦN thoả rõ nhất trong cả lô 31-35, thấy rất rõ trên ảnh.
- **L3 (nhãn AR):** AR 19:55 = 4128.9 **trùng đúng** biên chính trên — không mắc lỗi lệch nhãn của bài #33/#34.
- **L9:** Phase B (37 + 218 = 255 nến) là phase dài nhất. Đúng.
- **L4:** origin SC + phá lên = Tích luỹ. Đúng chiều.
- **L3/L7:** mỗi bên đúng 1 biên phụ; UA (00:44, 4137.1) giữ 1 cái ở cực trị; không có nhãn ST[B] (đúng L6), không spam LPS.

## Cần hỏi người học
- Với range trải qua phiên đêm Á (khối lượng 3-30 lot/nến): có muốn **cấm bắn SOS/SOW** trong khoảng giờ thanh khoản dưới ngưỡng, hay vẫn cho bắn nhưng đánh dấu "độ tin cậy thấp"?
