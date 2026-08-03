# Chấm bài #19 — Tái phân phối (RE-DIST) · 2026-06-03 05:30 → 09:28 (238 nến M1)

**Điểm: 2/10** — Range mở đúng chỗ (climax VSA 11.08x là thật), nhưng từ Phase C trở đi bài này sai nền tảng: máy giữ nhãn Phase C rồi Phase B cho cả đoạn giá đã **sống hẳn bên ngoài range**, và bỏ mất cây MSOW rõ nhất trong ngày. Phải vẽ lại từ Phase B.

## Lỗi (nặng → nhẹ)

### 1. Phase C dài 121 nến, trong đó 61% số nến đóng cửa NGOÀI range — luật vi phạm: L8, L9, L10
- **Thuật toán gắn:** C = 06:34 → 08:34 = **121 nến** (đúng bằng trần "chờ tối đa 120 nến"), rồi B = 08:35 → 09:16 = 42 nến.
- **Đúng phải là:** Phase C là phase **ngắn nhất**. Ở đây nó dài hơn Phase A (55) và hơn cả tổng Phase B (9 + 42 = 51). Đoạn 06:34–08:34 có **74/121 nến đóng cửa dưới biên chính dưới 4488.6**, đáy chạm **4478.8** — thấp hơn biên chính 9.8 giá và thấp hơn cả **biên phụ 4484.8** tới 6 giá. Giá đã rời vùng cân bằng; đó là Phase D/E của một cú phá xuống, không phải Phase C.
- **Dấu hiệu quyết định trên chart:** từ 08:20 đến 08:27 giá đóng cửa liên tục dưới biên phụ với VSA 1.9x–3.0x; máy vẫn đang ở "Phase C".
- **Nghi phạm trong thuật toán:** Phase C chỉ hết hạn bằng **timeout 120 nến**, không có điều kiện "giá đóng cửa ngoài biên phụ quá N nến ⇒ đây là phá thật". Và khi timeout, đoạn đã sơn Phase C **không được trả lại** nhãn Phase B/D. Cần: (a) hạ trần Phase C xuống mức thật sự "ngắn nhất" (vd ≤ 1/3 độ dài Phase B), (b) khi shock bị đánh dấu thất bại/timeout thì viết lại dải phase của đoạn đó.

### 2. Gán Phase B cho đoạn giá đã ra ngoài range 16 giá — luật vi phạm: L9, L10
- **Thuật toán gắn:** Phase B lần 2 = 08:35 → 09:16 (42 nến).
- **Đúng phải là:** trong 42 nến đó giá xuống **4468.2** (08:58) = **16.6 giá dưới biên phụ dưới** và 20.4 giá dưới biên chính. Phase B là giai đoạn **đàm phán trong range**; không thể gán cho một đoạn nằm hoàn toàn ngoài range. Đoạn này là Phase D/E.
- **Dấu hiệu quyết định trên chart:** dải "Phase B (42n)" nằm ở vùng giá 4468–4487 trong khi cả hai đường biên vẽ ở 4484.8–4499.3.
- **Nghi phạm trong thuật toán:** cùng gốc với lỗi #1 — nhánh "cú rũ thất bại ⇒ lùi về Phase B" không kiểm giá đang ở **trong hay ngoài** range trước khi lùi.

### 3. Bỏ mất MSOW thật, dán nhãn SOW lên một nến doji volume 0.47x — luật vi phạm: mục 8 Effort vs Result
- **Thuật toán gắn:** SOW tại 09:17, giá 4476.1, **VSA 0.47x**, thân/biên độ **0.11** (doji).
- **Đúng phải là:** MSOW là nến **08:51**: mở 4482.0 → đóng **4472.0**, low 4470.3, **VSA 9.63x**, thân 0.80 — rơi 10 giá trong một nến, cột volume cao nhất cả chart. Nhãn phải ở đó.
- **Dấu hiệu quyết định trên chart:** khi máy dán nhãn SOW (09:17) giá đã **cao hơn đáy 4468.2 tới 7.9 giá** và đang hồi lên; nến 09:17 gần như không có giao dịch (53 lot).
- **Nghi phạm trong thuật toán:** nhánh dự phòng "ở ngoài quá **40 nến** mà không quay lại ⇒ phá thật" đặt nhãn **đúng tại nến thứ 40** bất kể nến đó là gì. Sửa: khi nhánh timeout bắn, phải quay lại lấy **nến biên độ/volume lớn nhất** trong đoạn ở ngoài làm mốc SOS/SOW.

### 4. Nhãn Spring và LPS[C] đặt không đúng cực trị, sai thứ tự vai — luật vi phạm: L3, và lỗi #6 nguồn 2.pdf (Spring phải là giá thấp nhất TR)
- **Thuật toán gắn:** Spring (thất bại) 06:34 @4485.8 → LPS[C] 06:45 @**4485.1**.
- **Đúng phải là:** LPS[C] không được **thấp hơn** chính điểm Spring — nếu thấp hơn thì đó là cú rũ mới (Spring sâu hơn), không phải test lại. Đáy pivot thật của cụm là **4483.7** (06:46–06:47) và biên phụ ghi 4484.8 — nghĩa là cả hai nhãn đều lệch khỏi cực trị thật.
- **Dấu hiệu quyết định trên chart:** ba mức lồng nhau Spring 4485.8 > LPS[C] 4485.1 > biên phụ 4484.8 — không thể cùng đúng.
- **Nghi phạm trong thuật toán:** LPS[C] lấy "cực trị của nhịp hồi trong dung sai vùng điểm rũ" mà không kiểm ràng buộc **không được vượt qua điểm rũ**.

### 5. Chốt "completed" + Phase E ngay lúc cú phá bị phủ nhận — luật vi phạm: L10
- Phase E chốt 1 nến tại 09:28. Ngay sau đó giá bật từ 4467.2 (09:29) lên **4496.0** (10:07) — tức **quay vào trong range 7.4 giá trên biên chính dưới**, phủ định hoàn toàn cú phá xuống. Ghi "Tái phân phối [completed]" ở đây là kết luận sai về bản chất (THEORY §9: cú phá phải đi được tới phía đối diện mới xác nhận; không đi được thì đó là **cấu trúc thất bại**, và tín hiệu nghiêng về phía **ngược lại**).

## Đạt
- Climax mở range thuyết phục nhất trong lô: VSA **11.08x** (715 lot), nến đỏ thân 0.78, chặn đúng move giảm 27.5 giá — L1 đạt.
- Biên chính = climax (4488.6) + AR (4499.3), khớp đúng mức AR, không bị kéo theo giá — L3 đạt.
- ST[A] 4487.4 chỉ 1.2 giá dưới climax, VSA 1.09x, thân 0.17 — đây là một ST[A] **đúng sách**: test lại vùng climax với volume/spread co lại (THEORY §3.3).
- Không dùng nhãn ST[B] (L6), biên phụ đúng 1 cái mỗi bên (L3).

## Cần hỏi người học
- Anh muốn định nghĩa "giá đã rời range" bằng **số nến đóng cửa liên tiếp ngoài biên phụ** (vd 5 nến) hay bằng **khoảng cách** (vd đi thêm 0.5 × chiều cao range)? Mốc này sẽ dùng để cắt Phase C/B và bắn SOS/SOW đúng chỗ.
