# Chấm bài #21 — Tái phân phối (RE-DIST) · 2026-05-27 05:33 → 07:50 (137 nến M1)

**Điểm: 3/10** — không nên vẽ range ở đây: 7.3 giá biên chính trên nền 4525 là một chỗ nghỉ 12 nến giữa đợt giảm, không phải một vùng đấu giá; và SOW được dán khi giá đã rời range 8 giá.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — 7.3 giá biên chính, Phase A dài 12 nến, cả cấu trúc A→E gói trong 68 nến — luật vi phạm: L1 + lỗi kinh điển "khung quá thô / range quá vụn"
- **Thuật toán gắn:** một TR đầy đủ Phase A→E với biên chính 4525.6–4532.9 = **7.3 giá (0.16%)**, Phase A **12 nến**, Phase B **23 nến**, Phase C **22 nến**, Phase D **12 nến**.
- **Đúng phải là:** không mở range. Bảy giá trên vàng M1 là biên độ của **một cây nến** bình thường ở phiên này — chính cây climax đã rộng 5.5 giá, tức biên chính chỉ hơn một cây nến 1.8 giá. Giá không "đàm phán" ở đây, nó chỉ đi chậm lại vài phút giữa một đợt giảm liên tục.
- **Dấu hiệu quyết định trên chart:** nhìn ảnh — sau khi range đóng, giá đi thẳng từ 4525 xuống 4507 rồi lên 4522, tức nó đi qua "vùng đấu giá" 7.3 giá này như đi qua chỗ trống. Vùng cân bằng thật của phiên là dải 4511–4522 nằm **sau** range, kéo hàng trăm nến.
- **Nghi phạm trong thuật toán:** không có **sàn chiều cao tối thiểu** cho biên chính. Có trần 3.5% nhưng không có sàn. Người học chốt "không đặt sàn độ dài (số nến)" — nhưng đó là sàn *thời gian*, không phải sàn *chiều cao*. Đề xuất: yêu cầu chiều cao biên chính ≥ 2.5–3× biên độ TB 20 nến, nếu không thì climax và AR chỉ là hai đầu của một cây nến.

### 2. SOW dán ở 4517.0 — thấp hơn biên chính dưới 8.6 giá, tức hơn MỘT lần chiều cao range — luật vi phạm: L10 + mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOW tại 06:30, giá 4517.0, VSA **1.37×**, thân 0.48.
- **Đúng phải là:** cây phá thật là cụm 06:09–06:12 (trên panel volume thấy rõ 3 thanh vàng liên tiếp cao nhất cả đoạn), nơi giá đóng cửa lần đầu xuyên 4525.6. Đến 06:30 thì đợt bán đã đi được 8.6 giá = 118% chiều cao range — đó không còn là "dấu hiệu yếu kém", đó là Phase E rồi.
- **Dấu hiệu quyết định trên chart:** VSA của nến SOW là 1.37× — **thấp hơn** cả nến AR (1.36× thì bằng) và thấp hơn hẳn cụm nến vàng ở 06:09. Lỗi B của v4 (nhãn neo nến xác nhận thứ 3) đã được vá bằng cách "hồi tố về cây VSA cao nhất", nhưng ở bài này nó vẫn ra 1.37× → cơ chế hồi tố **chưa chạy** hoặc cửa sổ hồi tố quá hẹp.
- **Nghi phạm trong thuật toán:** nhánh hồi tố nhãn SOS/SOW trong `WyFireBreak()` — hoặc điều kiện "đóng cửa vượt **biên phụ**" (4523.2) làm cửa sổ tìm cây phá bắt đầu muộn hơn cây phá thật ở biên chính.

### 3. LPSY[C] gán ngược vào một nến giữa range, không phải test biên — luật vi phạm: L8 + Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPSY[C] tại 06:08, giá **4530.8** — nằm **trong** range, cách biên chính trên 2.1 giá, cách biên chính dưới 5.2 giá.
- **Đúng phải là:** LPSY là "đợt phục hồi yếu trên biên hẹp" **tại vùng kháng cự** trước khi rơi. Một điểm nằm giữa range không phải LPSY, nó chỉ là một đỉnh dao động Phase B. Nếu bắt buộc phải có Phase C thì nó phải là cú test **sát biên chính trên 4532.9** hoặc sát biên phụ trên 4533.9.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm LPSY[C] rõ ràng nằm lơ lửng giữa hai đường cam, không chạm đường nào.
- **Nghi phạm trong thuật toán:** cơ chế "Phase C gán ngược, nhìn lại 60 nến lấy cực trị" (mục 6 case KHÓ) — nó lấy **đỉnh cao nhất trong 60 nến** mà không kiểm điều kiện "đỉnh đó phải nằm trong dung sai chạm biên". Cần thêm gate: cực trị gán ngược phải cách biên bị test ≤ 10–15 tick, nếu không thì range **không có Phase C** — chấp nhận được, tài liệu nói rõ Spring/UT không bắt buộc.

### 4. Phase E dài 69 nến trong khi Phase B chỉ 23 nến — luật vi phạm: L9
- **Thuật toán gắn:** B=23, C=22, D=12, E=69.
- **Đúng phải là:** Phase B phải là phase dài nhất. Ở đây E dài gấp 3 lần B, và C (22) gần bằng B (23) — hai luật tỉ lệ phase đều gãy.
- **Dấu hiệu quyết định trên chart:** đây là hệ quả trực tiếp của lỗi #1 — cấu trúc quá vụn nên "Phase B" chưa kịp là gì thì giá đã đi.

## Đạt
- Điều kiện MOVE trước climax: 19.4 giá / 44 nến / hiệu suất 0.49 — có move giảm thật, climax **là** đáy của cửa sổ (đọc bảng 12 nến: 4525.6 thấp nhất). Mục 1 phần "có move" **đạt**.
- Climax đúng chất: VSA 4.84×, biên độ 5.5 giá — cây nổ thật, không phải nhiễu phiên Á.
- Phase A đủ 3 lần đổi hướng: SC 4525.6 → AR 4532.9 → ST[A] 4523.2, kết thúc **đúng tại ST[A]**. L2 đạt.
- Biên chính = đúng mức climax + mức AR, không bị kéo theo giá. L3 phần biên chính đạt.
- Biên phụ mỗi bên đúng 1 cái (4523.2 dưới do ST[A] vượt climax, 4533.9 trên). L3 phần biên phụ đạt.
- Tên "Tái phân phối" khớp L4: origin SC + phá xuống thật = RE-DIST. Đúng.
- Không còn nhãn ST[B], không spam nhãn — L6 đạt.
