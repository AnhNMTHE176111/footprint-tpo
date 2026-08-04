# Chấm bài #16 — Tích luỹ (ACC) · 2026-05-12 13:16 → 05-13 02:05 (430 nến M1)

**Điểm: 3/10** — Có climax đẹp nhất trong lô, nhưng **Shakeout gán sai chỗ** (không phải đáy thấp nhất TR), **biên phụ dưới sai 33 giá**, và Phase C phình thành 87 nến. Đây đúng là lỗi kinh điển lặp nhiều nhất trong CHART_CASES.md.

## Lỗi (nặng → nhẹ)

### 1. Shakeout không phải điểm thấp nhất của TR — luật vi phạm: Ca #19 nguồn 2.pdf (quy tắc giảng viên phát biểu tường minh nhất) + L3 biên phụ = cực trị xa nhất
- **Thuật toán gắn:** Shakeout tại **4710.8** (05-12 16:54), trạng thái `confirmed`; biên phụ dưới cũng ghi 4710.8.
- **Đúng phải là:** đáy thấp nhất toàn range nằm ở **05-12 15:23, quanh 4677–4680** — thấp hơn cái gọi là "Shakeout" tới **~33 giá**, và thấp hơn biên chính dưới 4722.5 tới ~45 giá. Giảng viên đã phát biểu tường minh (Ca #19, 2.pdf): *"Spring/Shakeout bắt buộc phải có giá thấp nhất trong suốt TR"*. Vậy: biên phụ dưới phải là ~4677, và điểm 4710.8 chỉ là một nhịp hồi trong đoạn ngoài range — cùng lắm là LPS[C].
- **Dấu hiệu quyết định trên chart:** trên ảnh, cụm nến 05-12 15:00–15:40 đâm xuống tận vạch 4675.5 (đáy trục giá), trong khi đường "biên phụ dưới 4710.8" nằm cao hơn hẳn cả cụm đó. Không thể nhầm được bằng mắt.
- **Nghi phạm trong thuật toán:** biên phụ và cực trị cú rũ **chỉ được cập nhật trong phiên "theo dõi một cú phá"**, và phiên đó đã kết thúc ở mSOW 14:33 (4714.5). Sau đó giá ở **ngoài** range liên tục ~100 nến nên không có "nến thò ra từ trong range" nào để mở phiên theo dõi mới → toàn bộ đoạn 4677 bị mù. Phải cập nhật cực trị/biên phụ **mọi nến**, không chỉ trong phiên theo dõi.

### 2. Đoạn ~100 nến ngoài biên đáng lẽ là SOW thật → range phải đổi tên Tái phân phối — luật vi phạm: L4 + mục 5.1 kết cục B
- **Thuật toán gắn:** cả đoạn 14:33 → 16:54 vẫn là Phase B, range cuối cùng tên **Tích luỹ**.
- **Đúng phải là:** giá đóng cửa dưới biên chính dưới liên tục từ ~14:40 tới ~16:40 (≈120 nến), sâu 45 giá = **2 lần chiều cao biên chính** (21.9 giá). Điều kiện "ở ngoài quá 40 nến và ≥60% nến đóng ngoài biên" đã thoả từ lâu → SOW thật, range là **Tái phân phối**, và cú lên sau đó là một range MỚI.
- **Dấu hiệu quyết định trên chart:** đếm trên ảnh, khoảng 2 giờ nến liên tục nằm dưới đường 4722.5.
- **Nghi phạm trong thuật toán:** cùng gốc với lỗi 1 — nhánh đếm "40 nến ngoài biên" chỉ chạy trong phiên theo dõi cú phá; sau khi phiên đó chốt là mSOW, máy quay về Phase B và **không mở phiên mới** vì giá không "thò ra từ trong range" nữa (nó vốn đã ở ngoài).

### 3. Phase C dài 87 nến, dài hơn Phase D + E (25 + 121 = tính riêng D thì 3.5 lần) — luật vi phạm: L8 "Phase C là phase NGẮN NHẤT"
- **Thuật toán gắn:** C từ 16:54 tới 19:24 = 87 nến, tức 57% độ dài Phase B (153 nến).
- **Đúng phải là:** từ 16:54 tới 19:25 giá tăng đều từ 4711 lên 4744 — đó là **cả một chân tăng**, tức Phase D đang chạy, không phải "Phase C đang chờ xác nhận". Phase C đúng chỉ là nhịp test cuối ngay trước cú bứt (khoảng 19:00–19:25).
- **Dấu hiệu quyết định trên chart:** dải Phase C trên ảnh trải suốt đoạn nến leo dốc từ 4711 lên 4744 — nhìn là thấy đây không phải một điểm rũ.
- **Nghi phạm trong thuật toán:** Phase C bắt đầu ngay tại điểm rũ và chỉ kết thúc khi có SOS/SOW hoặc hết 120 nến. Trần 120 nến quá lỏng so với luật "C là phase ngắn nhất" — nên kẹp thêm: `độ dài C ≤ k × độ dài B` (hoặc dời mốc bắt đầu C về nhịp test cuối trước SOS như cơ chế gán ngược đang làm ở case khó).

### 4. ST[A] neo vào một cây VSA 4.71x xuyên dưới đáy climax — luật vi phạm: L2 (ST[A] phải là test, THEORY §3.3 "spread/volume thường GIẢM khi test")
- **Thuật toán gắn:** ST[A] tại 4719.1 (14:00), **VSA 4.71x**, thấp hơn mức climax 4722.5.
- **Đúng phải là:** test lại vùng climax phải co volume. Một cây 4.71x xuyên qua đáy climax là **nỗ lực bán mới**, không phải test — đây là dấu hiệu cung còn mạnh, đáng gọi mSOW/Spring hơn.
- **Nghi phạm:** ST[A] tìm bằng swing pivot thuần cấu trúc (mục 4.2), **không xét volume**. Nên thêm điều kiện mềm: nếu nến ST[A] có VSA cao hơn nến climax-cluster thì cảnh báo "ST[A] (nỗ lực mới)".

### 5. Nhãn ST[B] — mâu thuẫn với luật đã chốt (trình bày / danh pháp)
- Bài này gắn **ST[B]** tại 4721.2 (14:31). Người học đã chốt **L6: bỏ hẳn nhãn ST[B]** ("nó chả dùng làm gì cả"); brief vòng v6 lại nói ST[B] là nhãn MỚI thay UA/DA. Ghi vào mục cần hỏi, không tính điểm trừ.

## Đạt
- Climax (L1): SC 4722.5, **VSA 6.34x, biên độ 5.2 giá, 59 hợp đồng** — cao trào thật, rõ nhất trong lô 6 bài. MOVE giảm 23.6 giá / 23 nến / hiệu suất 0.57. Đạt.
- Phase A (L2): đủ 3 lần đổi hướng, kết thúc đúng tại ST[A], 45 nến.
- Biên chính (L3): 4722.5 + 4744.4, cố định, không kéo theo giá. Đạt.
- Có Phase C với nhãn shock thật (case dễ) và SOS 4746.6 VSA 2.44x thân 1.00 vượt biên phụ trên 4753.2 — đúng cơ chế L3 "SOS mạnh phải bứt biên phụ"... (tuy 4746.6 < 4753.2, xem ghi chú dưới).
- Phase E có độ dài thật 121 nến (lỗi J của v5 đã vá).
- Chỉ số Phase B: SOT hai phía cùng "chớm", thrust dưới 0.07 / volume 0.25 = cạn kiệt — khớp hình.

## Cần hỏi người học
- **ST[B] có được dùng hay không?** L6 nói bỏ hẳn, brief v6 nói dùng thay UA/DA. Cần chốt một hướng để không chấm chéo nhau ở các vòng sau.
- Khi giá **đã ở ngoài range** rồi mới đi xa hơn nữa (không có nến "thò ra từ trong"), người học muốn coi đó là (a) tiếp tục cùng một cú phá — cập nhật cực trị, hay (b) một cú phá mới? Hiện code không xử cả hai, nên mù hẳn 100 nến.
