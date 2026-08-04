# Chấm bài #29 — Tái phân phối (RE-DIST) · 2026-06-05 14:06 → 14:50 (44 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây: 44 nến M1 nhồi đủ 5 phase (B 5 nến, C 1 nến), climax VSA 0.98x, và ngay sau "Phase E" giá hồi thẳng vào lại trong biên. Đây là một nhịp thở trong xu hướng giảm, không phải vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. 44 nến với đủ A→E, Phase B 5 nến, Phase C 1 nến — luật vi phạm: L9, L8, "range quá vụn"
- **Thuật toán gắn:** A 10 · **B 5** · **C 1** · D 14 · **E 15**.
- **Đúng phải là:** L9 — B dài nhất; ở đây B là phase **ngắn thứ hai**, còn E dài nhất. Chỉ dẫn chấm nói rõ: một TR M1 dài 60–100 nến với đủ Phase A→E thì phải nghi ngay là nhiễu — bài này còn ngắn hơn nữa, **44 nến**. "Phase C 1 nến" không phải một phase, nó chỉ là cái nến đứng ngay trước cú phá.
- **Dấu hiệu quyết định trên chart:** năm vạch tím dồn vào một dải hẹp bên phải ảnh, chiếm khoảng 1/8 chiều rộng chart; toàn bộ 3/4 ảnh còn lại là một xu hướng giảm 4500 → 4390 không có cấu trúc nào.
- **Nghi phạm trong thuật toán:** thiếu kiểm tra hậu nghiệm tỉ lệ phase (B phải dài nhất, C ngắn nhất) trước khi công bố; và thiếu sàn tối thiểu cho Phase B (một Phase B 5 nến không thể "xây nguyên nhân" theo THEORY §3.2).

### 2. Nến climax có VSA 0.98x — dưới trung bình — luật vi phạm: mục 3 tài liệu thuật toán (VSA ≥ 2.2x), THEORY §3.3
- **Thuật toán gắn:** mức climax 4388.1 tại nến 14:06, **VSA 0.98x**, biên độ 7.4 giá; nhãn SC đặt ở 13:59 (VSA 4.07x, giá 4390.0).
- **Đúng phải là:** cụm cao trào thật ở 13:59–14:00 (VSA 4.07x và 2.58x). Việc dời **mốc** climax sang một nến VSA 0.98x chỉ vì nó có đáy thấp hơn 1.9 giá làm biên chính dưới neo vào một cây không có nỗ lực nào. Lệch nhãn↔mức ở đây chỉ 1.9 giá (13% chiều cao) nên chấp nhận được, nhưng cây neo biên thì sai bản chất.
- **Dấu hiệu quyết định trên chart:** thanh volume vàng khổng lồ nằm ở 13:59–14:00, còn nến 14:06 có thanh volume thấp hơn đường TB.
- **Nghi phạm trong thuật toán:** cụm climax (mục 4.0) dời mốc theo **cực trị giá** thuần, không yêu cầu nến đích cũng đạt ngưỡng VSA. Nên buộc: nến được chọn làm mốc climax phải tự nó có VSA ≥ 2.2x, hoặc giữ mốc ở cây volume và chỉ nới **biên phụ** tới cực trị mới.

### 3. Range chỉ là 14% của move đi trước — không phải vùng cân bằng — luật vi phạm: L1 (mục 1: đây có phải vùng đấu giá thật)
- **Thuật toán gắn:** MOVE trước 101.8 giá / 106 nến; range cao **14.2 giá**.
- **Đúng phải là:** 14.2/101.8 = 14% — giá chỉ đứng lại 20 nến rồi rơi tiếp. THEORY §2.3 nói vùng cân bằng là nơi giá **dành nhiều thời gian**; ở đây thời gian dừng bằng 1/5 thời gian rơi. Đọc đúng: đây là một pullback nhỏ trong downtrend, phải đợi vùng dừng thật (nó xuất hiện ngay sau: 14:37→15:31 giá dập dềnh 4370–4400, xem lỗi 4).
- **Dấu hiệu quyết định trên chart:** đường "chân MOVE" xám kéo suốt từ góc trên trái tới đúng nhãn SC — độ dốc không đổi, không có chỗ nào move bị chặn thật.
- **Nghi phạm trong thuật toán:** không có ràng buộc **tỉ lệ chiều cao range / độ dài move**. Một range hợp lệ phải là chỗ move bị chặn, tức phải hồi lại một tỉ lệ đáng kể của move (hiện chỉ 21%).

### 4. Phase E được chốt rồi giá hồi thẳng vào trong biên — luật vi phạm: L10
- **Thuật toán gắn:** Phase E 14:36→14:50, range **completed**, tên "Tái phân phối".
- **Đúng phải là:** L10 đòi "giá thuận lực đi tiếp để tìm vùng giá mới". Trên chart, chỉ 5 nến sau khi Phase E kết thúc, đợt hồi 14:51→14:57 đưa giá lên ~**4400**, tức **vào lại trong biên chính** (4388.1–4402.3), rồi 40 phút sau vẫn còn dập dềnh 4386–4400. Cú SOW này không tìm được vùng giá mới, nó chỉ mở rộng chính vùng cũ.
- **Dấu hiệu quyết định trên chart:** cụm nến xanh 14:51–14:57 leo lên đến gần đường "biên CHÍNH trên 4402.3"; nhãn biên chính dưới 4388.1 bị chính nến giá đè lên ở nửa phải ảnh.
- **Nghi phạm trong thuật toán:** Phase E chốt khi đi được 1.0× chiều cao (14.2 giá) — với range 14.2 giá thì mốc này quá dễ đạt (chỉ cần rơi thêm 14 giá trong một downtrend đang chạy 100 giá). Đích Phase E nên đo theo **ATR/độ dài move**, không chỉ theo chiều cao của một range vụn.

### 5. LPSY[C] nằm giữa range, Phase C = 1 nến — luật vi phạm: L8, THEORY §4.1 (LPSY)
- **Thuật toán gắn:** LPSY[C] 14:21 tại 4395.6 (VSA 1.12x), Phase C dài đúng 1 nến (14:21→14:21).
- **Đúng phải là:** LPSY là đợt phục hồi yếu **sau khi test kháng cự** — phải neo vào biên trên 4402.3 hoặc vào vùng cung đã lộ. 4395.6 = 53% chiều cao range, không test biên nào cả. Nếu đọc trung thực thì cấu trúc này **không có Phase C**; đừng dán một nhãn cho đủ bộ.
- **Dấu hiệu quyết định trên chart:** nhãn LPSY[C] nằm lơ lửng giữa hai đường biên, sát ngay nhãn SOW bên dưới.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = min(60 nến, 1/2 Phase B) = **2 nến** vì Phase B chỉ 5 nến → tất yếu chọn đúng nến liền trước cú phá. Đây đúng chỗ mục 12.10 tài liệu tự nghi ngờ; cần dùng số nến tuyệt đối và **bỏ hẳn Phase C nếu không tìm được nhịp test thật ở biên**.

### 6. Phase D 14 nến nhưng không có LPSY[D] — luật vi phạm: L10, L7
- **Thuật toán gắn:** Phase D 14:22→14:35, sự kiện duy nhất là SOW.
- **Đúng phải là:** trên chart có nhịp hồi nhỏ quanh 14:27–14:31 (cụm nến xanh trước khi rơi nốt về 4370) — đó là LPSY[D]. Không có nhãn nào → CBR mất mất mắt xích retest.
- **Nghi phạm trong thuật toán:** cùng nguyên nhân với bài #28 — pivot 5 nến quá chặt khi giá vẫn liên tục tạo đáy mới.

### 7. Chỉ số nỗ lực/kết quả in nhãn ngược nghĩa (lỗi ĐO — lặp cả 5 bài)
- **Thuật toán gắn:** nến 14:22, effort 1.90x, result 2.63, er=0.72 → "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er=0.72 < 1 nghĩa kết quả vẫn lớn hơn nỗ lực. Và nến 14:22 chính là nến **SOW thuộc Phase D**, không thuộc Phase B. Cả 5 bài lô này in cùng một câu "NGHI VẤN" với er từ 0.17 đến 0.72 → nhãn in cứng, không so ngưỡng nào.
- **Nghi phạm trong thuật toán:** thiếu nhánh `if er > ngưỡng` khi sinh chuỗi mô tả; biên phải cửa sổ quét Phase B lấy mốc SOW thay vì mốc kết B.

## Đạt
- **L2:** đủ 3 lần đổi hướng — climax 4388.1 → AR 4402.3 → ST[A] 4389.4. ST[A] về đúng sát mức climax (cách 1.3 giá) — đây là một ST[A] **đúng vai** nhất trong cả lô 5 bài.
- **L3:** biên chính = climax + AR, cố định; không dựng biên phụ giả (biên phụ = biên chính vì không ai thò ra ngoài).
- **L4:** SC + phá xuống → Tái phân phối, đúng bảng 4 pattern.
- **L5:** SOW (VSA 2.69x, thân 0.92) là cú đóng cửa hẳn ngoài biên, không bị gọi nhầm thành Spring/Shakeout.
- **Chỉ số bias = −1** khớp đúng hướng phá xuống. Đo đúng.
- **SOT hai phía = none:** đúng, Phase B 5 nến không thể có 3 nhịp đẩy (THEORY §7). Chỉ số đang tố cáo chính Phase B — hữu ích, giữ.
