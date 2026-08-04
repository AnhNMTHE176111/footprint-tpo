# Chấm bài #26 — Phân phối (DIST) · 2026-06-04 16:19 → 17:50 (91 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây: một "vùng đấu giá" cao 6.0 giá bằng đúng 2 cây nến, đủ 5 phase trong 91 nến M1 → đây là nhiễu, và cú SOW của nó bị giá lấy lại ngay trong chính Phase D.

## Lỗi (nặng → nhẹ)

### 1. Range 6.0 giá = nhiễu chứ không phải vùng đấu giá — luật vi phạm: "range quá vụn" (CHART_CASES, Ca #4/#6/#19 nguồn 7.pdf — giảng viên đòi đổi khung khi cấu trúc không ra hình)
- **Thuật toán gắn:** biên chính 4507.2–4513.2 = **6.0 giá (0.13%)**, đủ A→E trong 91 nến.
- **Đúng phải là:** không vẽ range. 6.0 giá = 60 tick, trong khi dung sai "đóng cửa lùi hẳn qua biên" của chính thuật toán là 30 tick — tức nửa chiều cao range. Nến đơn lẻ trong vùng này có biên độ 2–3 giá, nghĩa là **2 cây nến là đi hết range**. Không có chỗ nào để một cuộc đàm phán cung–cầu diễn ra.
- **Dấu hiệu quyết định trên chart:** trục giá cả ảnh chỉ trải 4496–4514; hai đường biên chính nằm sát nhau tới mức nhãn "biên CHÍNH dưới 4507.2" đè lên chính nến giá.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range", nhưng ở đây thiếu **sàn CHIỀU CAO tối thiểu theo ATR** (ví dụ biên chính ≥ 4–5× biên độ TB 20 nến). Guard hiện có chỉ chặn range **quá cao** (3.5% giá), không chặn range quá thấp.

### 2. Phase B KHÔNG phải phase dài nhất, Phase C bằng Phase B — luật vi phạm: L9 và L8
- **Thuật toán gắn:** A 20 · B 18 · C 18 · D 25 · E 11.
- **Đúng phải là:** L9 — B dài nhất; L8 — C ngắn nhất. Ở đây **A (20) > B (18)**, **D (25) > B**, và **C = B = 18 nến**. Cả hai luật tỉ lệ phase bị phá cùng lúc, đó là dấu hiệu cấu trúc bị chia ép chứ không đọc ra từ giá.
- **Dấu hiệu quyết định trên chart:** 5 vạch tím chia gần như đều nhau trên trục thời gian — nhìn là biết chia theo sự kiện rời rạc, không theo hình.
- **Nghi phạm trong thuật toán:** không có bất kỳ kiểm tra hậu nghiệm nào về tỉ lệ phase (B dài nhất / C ngắn nhất) trước khi công bố range.

### 3. Cú SOW không giữ được ngoài biên nhưng vẫn lên Phase E và vẫn được đặt tên "Phân phối" — luật vi phạm: L10, mục 7 lỗi F
- **Thuật toán gắn:** SOW 17:15 tại 4503.4 → LPSY[D] 17:17 tại 4504.1 → Phase D tới 17:39 → Phase E 17:40–17:50 → tên **Phân phối**.
- **Đúng phải là:** L10 đòi "hồi về retest nhưng **giữ được** ở ngoài biên". Trên chart, trong lòng Phase D (khoảng 17:31) giá **đóng cửa lên tới ~4508.5**, tức vào hẳn **trên** biên chính dưới 4507.2 — cú phá đã bị lấy lại. Nhãn đúng là **mSOW**, dải phase trả về B, range **không được đặt tên**.
- **Dấu hiệu quyết định trên chart:** cụm nến xanh quanh 17:29–17:33 đóng cửa trên đường "biên CHÍNH dưới 4507.2"; và cả phần chart sau 17:45 giá dập dềnh 4505–4508.5, tức ở ngay trong range.
- **Nghi phạm trong thuật toán:** guard vô hiệu (mục 7 câu 1) chỉ bắn khi giá lùi vào trong range **trước khi đi được 50% tiến độ**. Cú SOW đã đi 4.9/6.0 giá trước, nên guard bị vô hiệu hoá; cần thêm điều kiện "**bất kỳ** nến nào trong Phase D đóng cửa trong biên → hạ cấp", không phụ thuộc thứ tự.

### 4. LPSY[D] gán vào swing pivot đầu tiên nên bỏ mất nhịp retest thật — luật vi phạm: L10, L7
- **Thuật toán gắn:** LPSY[D] 17:17 tại 4504.1, đúng **2 nến** sau SOW.
- **Đúng phải là:** nhịp hồi retest thật là nhịp 17:24→17:31 lên 4508.5 — chính nhịp đó quyết định cấu trúc sống hay chết. Cái pivot 2 nến sau SOW chỉ là một cái nảy trong đà rơi, không phải "điểm cung cuối cùng".
- **Dấu hiệu quyết định trên chart:** nhãn LPSY[D] nằm giữa cụm nến đỏ đang rơi, cách biên bị phá chỉ 3.1 giá và VSA chỉ 0.83x.
- **Nghi phạm trong thuật toán:** LPS[D]/LPSY[D] = "swing pivot ngược hướng phá **đầu tiên** được xác nhận" (mục 7 câu 2) — nên lấy nhịp hồi **cao nhất/xa nhất** trong cửa sổ 25 nến, không phải nhịp đầu tiên.

### 5. LPSY[C] đặt giữa range, không test biên nào — luật vi phạm: L8, THEORY §4.1 (LPSY)
- **Thuật toán gắn:** LPSY[C] 16:57 tại 4511.7.
- **Đúng phải là:** LPSY là đợt phục hồi yếu **sau khi đã test kháng cự**, phải neo vào biên trên 4513.2 hoặc vào vùng bị SOW bỏ lại. 4511.7 = 75% chiều cao, cách biên trên 1.5 giá nhưng không chạm, và sau nó giá còn dập dềnh 18 nến trong range → chưa có gì "cuối cùng".
- **Nghi phạm trong thuật toán:** Phase C gán ngược lấy "đỉnh cao nhất trong cửa sổ ≤60 nến" — cửa sổ này rơi trọn vào giữa Phase B nên bắt được một đỉnh cục bộ bất kỳ (mục 12.10 tài liệu đã tự nghi ngờ chỗ này).

### 6. SOW không có nỗ lực — luật vi phạm: THEORY §4.1 (SOW cần volume/spread tăng)
- **Thuật toán gắn:** SOW với VSA **1.07x** — dưới trung bình 20 nến.
- **Đúng phải là:** THEORY §6.3 có cho phép breakout không cần volume cao (nguồn cung nổi đã cạn), nên đây **không phải lỗi tự động**; nhưng ghép với việc giá lấy lại biên ngay sau đó thì kết luận rõ: không có nỗ lực, không có kết quả → không phải SOW.
- **Dấu hiệu quyết định trên chart:** thanh volume tại 17:15 thấp hơn đường TB 20 nến; cây volume vàng khổng lồ trong ảnh nằm ở 17:31 — tức ở **nhịp hồi lấy lại biên**, không phải ở cú phá. Nỗ lực đang nằm ở phe MUA.

## Đạt
- **L4 (tên theo hướng phá):** BCLX + phá xuống → Phân phối, mapping đúng bảng 4 pattern (chỉ tiếc là cú phá không hợp lệ).
- **Cơ chế mới BCLX?/"sinh từ cú phá":** ghi rõ trên tiêu đề rằng range này không có cao trào thật — trung thực, không giả vờ có climax. Đúng tinh thần cơ chế mới.
- **L3:** biên chính cố định, không có biên phụ giả (biên phụ = biên chính vì chưa ai thò ra ngoài) — trung thực.
- **Chỉ số bias = 0** (test cả hai biên) đọc đúng hình: giá lắc qua lại giữa hai biên, đây đúng là "ca thường". Đo đúng.
- **SOT hai phía = none:** đúng, vì Phase B 18 nến không đủ 3 nhịp đẩy như THEORY §7 yêu cầu. Chỉ số đang **tố cáo chính Phase B quá ngắn** — giữ nguyên, nó hữu ích.

## Cần hỏi người học
- Có đồng ý thêm **sàn chiều cao biên chính theo ATR** (ví dụ ≥ 4× biên độ TB 20 nến) không? Người học đã chốt không đặt sàn **độ dài**, nhưng sàn **chiều cao** là chuyện khác và bài này là ca điển hình đòi nó.
