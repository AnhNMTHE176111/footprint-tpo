# Chấm bài #18 — Phân phối (DIST) · 2026-05-24 23:16 → 2026-05-25 00:22 (65 nến M1)

**Điểm: 1/10** — Không vẽ range ở đây. Cao trào VSA **1.06x** (dưới mức "cao" 1.2x, xa mức climax 2.2x), biên chính **4.1 giá**, đủ 5 phase trong 65 nến. Đây đúng là ca "nhiễu chứ không phải vùng đấu giá thật" mà đề bài dặn phải nghi ngay.

## Lỗi (nặng → nhẹ)

### 1. Nến climax KHÔNG phải climax — VSA 1.06x, biên độ 1.7 giá — luật vi phạm: L1 (điều kiện ĐỦ không thoả), mục 3 tài liệu thuật toán
- **Thuật toán gắn:** BCLX tại 23:16, giá 4613.5, **VSA 1.06x**, biên độ nến **1.7 giá**, volume **9 hợp đồng**.
- **Đúng phải là:** không có climax nào cả. Điều kiện mở range ghi rõ: biên độ ≥ 1.4× TB20 **và** VSA ≥ 2.2x. Nến này VSA 1.06x — tức bằng đúng khối lượng trung bình. Nhìn 12 nến quanh climax: volume lần lượt 10, 3, 7, 5, 6, 4, **9**, 5, 13, 8, 4, 1. Cây "cao trào mua" có volume 9 nằm giữa một dãy 3–13. Không có bất kỳ dấu hiệu Composite Man nào.
- **Dấu hiệu quyết định trên chart:** panel volume ở vùng climax gần như phẳng sát đáy; thanh vàng duy nhất trong cả khung hình nằm ở 05-24 22:00 (trước range) và ở 23:17 (sau climax). Cây được gọi là BCLX **không** có thanh vàng.
- **Nghi phạm trong thuật toán:** hai ngưỡng mở range đo bằng **tỉ lệ tương đối** (1.4× biên độ TB20, 2.2× VSA). Ở phiên Á giờ chết, TB20 tụt xuống mức nhiễu nên tỉ lệ vọt lên dễ dàng. Người học đã chốt "không dùng sàn khối lượng tuyệt đối" (quyết định 6), nhưng ở đây **ngay cả ngưỡng tương đối cũng không thoả**: 1.06x < 2.2x. Nghĩa là range này lọt qua bằng một đường khác — nhiều khả năng cụm climax ở mục 4.0 đã **dời mốc** từ một nến khác sang 23:16 và mang theo cả tư cách climax, nhưng không kiểm lại ngưỡng VSA tại mốc mới. Đây là bug rõ ràng, đáng sửa nhất trong cả 5 bài.

### 2. Range cao 4.1 giá (0.09%) — không phải vùng cân bằng, chỉ là bề dày nhiễu — luật vi phạm: L3, THEORY §2.3
- **Thuật toán gắn:** biên chính 4609.4–4613.5 = **4.1 giá**.
- **Đúng phải là:** so sánh với chính bộ dữ liệu này — tài liệu thuật toán mục 13.1 ghi chiều cao biên chính trung vị **21.6 giá**, nhỏ nhất 6.6 giá. Range này **4.1 giá**, nhỏ hơn cả mức nhỏ nhất từng ghi nhận. Với vàng 4.1 giá = 41 tick, tức chỉ hơn một cây nến M1 bình thường lúc sôi động. Chia nhỏ 4.1 giá đó thành biên trên/biên dưới/biên phụ/Spring/SOW là đo nhiễu.
- **Dấu hiệu quyết định trên chart:** SOW ở 4602.4 nằm dưới biên dưới đúng **7 giá**; LPSY[D] 4610.6 và biên chính trên 4613.5 chồng chữ lên nhau vì cách nhau có 3 giá.
- **Nghi phạm trong thuật toán:** guard duy nhất về chiều cao là **trần** (>3.5% giá thì huỷ), không có **sàn**. Người học chốt "không đặt sàn độ dài tối thiểu cho range" (quyết định 1) — nhưng đó là sàn **số nến**, không phải sàn **chiều cao giá**. Hai cái khác nhau, nên hỏi lại.

### 3. Đủ A→B→C→D→E trong 65 nến — cấu trúc gò ép — luật vi phạm: L8, L9; đúng lỗi Ca #20 nguồn 7.pdf
- **Thuật toán gắn:** A 9 · B 28 · C 8 · D 15 · E 6 nến.
- **Đúng phải là:** Phase A **9 nến** nghĩa là climax → AR → ST[A] xong trong 9 phút. Phase E **6 nến**. Đây là điều giảng viên đã mắng ở Ca #20: "hình này gượng ép… cố gò dữ liệu cho khớp mô hình". Một chu trình Wyckoff đầy đủ (xây nguyên nhân rồi tạo kết quả — Luật Nhân Quả) không thể xong trong 65 phút với 4 giá biên độ.
- **Dấu hiệu quyết định trên chart:** năm nhãn phase chen chúc chồng lên nhau trên đầu chart, phải đọc phiếu số liệu mới tách được.

### 4. ST[A] có VSA 7.13x — cao gấp 6,7 lần cây "climax" — luật vi phạm: L2, mục 8 Effort vs Result
- **Thuật toán gắn:** BCLX VSA 1.06x → ST[A] 23:24 VSA **7.13x**, thân 0.22, giá 4614.0.
- **Đúng phải là:** ST theo định nghĩa (THEORY §3.3) là cú test lại vùng climax với **spread/volume THU HẸP**. Ở đây ngược hoàn toàn: cây test có khối lượng gấp 7 lần cây climax và tạo giá **cao hơn** climax (4614.0 > 4613.5). Cây 7.13x này mới là cao trào mua thật của cả đoạn — nó là BCLX, còn cái được gọi BCLX chỉ là nến dạo đầu.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng duy nhất trong vùng range nằm đúng tại 23:17 (ngay sau ST[A] vùng), cao vọt hẳn so với mọi thanh khác.
- **Nghi phạm trong thuật toán:** không có bước kiểm tra nhất quán "khối lượng climax phải ≥ khối lượng mọi test sau đó trong Phase A". Đây là kiểm tra rẻ và bắt được lỗi ngay.

### 5. Phase D/E chốt trong khi cú SOW đã hỏng — luật vi phạm: L10
- **Thuật toán gắn:** SOW 00:01 tại 4602.4 → LPSY[D] 00:11 tại 4610.6 → Phase E 00:16.
- **Đúng phải là:** LPSY[D] ở 4610.6 nằm **trên** biên chính dưới 4609.4, tức giá đã hồi **vào lại trong range**. L10 yêu cầu Phase D là "phá biên, hồi về retest nhưng **giữ được** ở ngoài biên". Ở đây không giữ được — giá quay hẳn vào trong. Nhìn chart, sau đó giá còn leo lên 4617 (cao hơn cả biên trên) trước khi mới thực sự giảm. Cú SOW này thất bại, phải hạ thành mSOW và trả phase về B.
- **Dấu hiệu quyết định trên chart:** chấm LPSY[D] màu tím nằm rõ ràng phía **trên** đường cam nét liền dưới (4609.4); nến sau đó tạo đỉnh mới 4617+.
- **Nghi phạm trong thuật toán:** mục 7 Câu 1 bắt "một nến đóng cửa lùi hẳn vào trong range quá **30 tick** → cú phá hỏng". Range này chỉ cao 4.1 giá = 41 tick, nên ngưỡng 30 tick tuyệt đối gần bằng **cả chiều cao range** — giá gần như không thể lùi đủ để bị coi là hỏng. Ngưỡng tuyệt đối này phải được kẹp theo chiều cao range (ví dụ min(30 tick, 25% chiều cao)).

### 6. Trình bày: cụm nhãn ở góc trên chồng lên nhau
Chữ "bien CHINH duoi 4609.4" bị nhãn LPSY[D] và "bien phu duoi" đè lên, không đọc được nếu không có phiếu số liệu. ST[A] bị cắt mất nửa trên khỏi khung hình. Lỗi trình bày, xếp cuối.

## Đạt
- **Mục 1 (một phần):** MOVE trước climax có thật và đẹp — 62.5 giá / 82 nến / hiệu suất 0.51, nhìn chart là một đợt tăng dựng đứng từ 4545 lên 4613. Điều kiện CẦN của L1 thoả; cái hỏng là điều kiện ĐỦ (climax).
- **Mục 4 — tên range:** origin BCLX + phá xuống = Phân phối, khớp L4 về mặt logic đặt tên (dù cú phá không đáng tin).
- **Mục 6 — Phase C ngắn nhất (8 nến):** đúng L8; LPSY[C] một điểm, đúng L7.
- **Mục 9:** không có ST[B], không spam nhãn.

## Cần hỏi người học
- Có nên đặt **sàn chiều cao range** (theo giá, không theo số nến) không? Quyết định 1 chỉ chốt bỏ sàn *độ dài*. Range 4.1 giá này cho thấy thiếu sàn chiều cao thì thuật toán sẽ đều đặn vẽ nhiễu phiên Á thành cấu trúc đủ 5 phase.
