# Chấm bài #20 — Tích luỹ (ACC) · 2026-06-04 14:51 → 17:13 (142 nến M1)

**Điểm: 2/10** — Range vẽ **lệch hẳn chỗ**: vùng đấu giá thật là 4503–4513, nằm **hoàn toàn phía trên** biên chính trên 4505 mà máy vẽ. Cái được khoanh là một cú bật V bị gò thành Trading Range (đúng lỗi "gượng ép" Ca #20 nguồn 7.pdf).

## Lỗi (nặng → nhẹ)

### 1. Không có vùng đi ngang nào NẰM TRONG range — biên dưới chỉ được chạm 1 lần — luật vi phạm: L1 (range phải là vùng đấu giá thật), và mục "Cách xác định biên range" trong CHART_CASES (biên dưới cần 2–3 lần chạm)
- **Thuật toán gắn:** range 4487.0–4505.0 (18 giá) từ 14:51 tới 17:13.
- **Đúng phải là:** vùng cân bằng thật là **4503–4513**. Từ 16:00 tới 17:13 có **67/74 nến đóng cửa TRÊN biên chính trên 4505**; mức 4487 chỉ được chạm **đúng một lần** — bởi chính cây climax. Sau climax giá bật lên một mạch (V-reversal) rồi đi ngang ở tầng giá cao hơn. Nếu vẽ, phải vẽ range **4503–4513** với biên dưới ~4503 (nhiều lần chạm), không phải 4487–4505.
- **Dấu hiệu quyết định trên chart:** hai dải Phase C (16:32–16:47) và Phase D (16:48–17:13) nằm **trọn ở trên** cả biên chính trên và biên phụ trên; nhãn LPS[C] in ở giá 4507.2 — cao hơn cả hai biên.
- **Nghi phạm trong thuật toán:** không có bước kiểm **"giá có thực sự đi ngang trong hai biên"** trước khi công nhận range (vd đếm số nến đóng cửa trong biên chính, hoặc số lần chạm mỗi biên ≥2). Hiện chỉ cần climax + AR + một cú pullback 40% là xong Phase A.

### 2. Climax không phải đáy — biên chính dưới lệch 3.2 giá — luật vi phạm: L1
- **Thuật toán gắn:** SC 4487.0 (14:51, VSA 3.32x) làm biên chính dưới.
- **Đúng phải là:** đáy thật của cú giảm là **4483.8 tại 14:53** — chỉ **2 nến sau** climax (VSA 2.31x, 800 lot). Mốc SC/biên chính dưới phải ở đó (hoặc coi 14:51–14:53 là vùng SC).
- **Dấu hiệu quyết định trên chart:** biên phụ dưới 4483.8 được vẽ ngay dưới biên chính, tạo hai đường sát nhau chỉ vì mốc gốc đặt sai một nến.
- **Nghi phạm trong thuật toán:** giống bài #16 — chỉ kiểm climax là cực trị của 240 nến **trước**, không kiểm K nến **sau**.

### 3. ST[A] là ngọ nguậy giữa range, Phase A đóng sớm — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 4497.3 (15:45), hồi 7.7 giá = **43%** chiều cao climax↔AR.
- **Đúng phải là:** ST[A] phải quay về **vùng climax** rồi bị chặn. 4497.3 còn cách climax **10.3 giá** (57% chiều cao) và ngay sau đó giá đi **lên** tiếp tới 4506.6 (UA) rồi 4513.2 — chưa hề có lần đổi hướng thứ ba. Thực tế cấu trúc này **không bao giờ** test lại đáy 4487 → Phase A chưa hoàn thành CHoCH, đúng ra phải **bỏ ứng viên**.
- **Nghi phạm trong thuật toán:** ngưỡng "ST[A] hồi ≥ **40%**" quá lỏng (cùng nghi phạm với bài #16). Nên đòi ST[A] chạm dung sai vùng climax.

### 4. LPS[C] thực chất là LPS[D] — sai vai trước/sau cú phá — luật vi phạm: lỗi kinh điển Ca #3 nguồn 4.pdf
- **Thuật toán gắn:** LPS[C] 16:32 @4507.2 (test **trước** SOS).
- **Đúng phải là:** cú phá lên đã xảy ra ở **16:08–16:11** (xem lỗi #5), nên nhịp 16:32 là **LPS[D]** — hồi retest sau phá. Bằng chứng giá: 4507.2 nằm **trên** biên chính 4505 **và trên** biên phụ 4506.6; một "test trước phá" không thể nằm ngoài cả hai biên.
- **Nghi phạm trong thuật toán:** vì SOS bị dán muộn (lỗi #5), toàn bộ ranh giới C/D bị đẩy lùi theo — Phase C (16 nến) rơi vào vùng vốn đã là Phase D.

### 5. Nhãn SOS muộn 40 nến, đặt trên nến 29 lot — luật vi phạm: mục 8 Effort vs Result
- **Thuật toán gắn:** SOS 16:48 @4510.8, volume **29 lot**, **VSA 0.23x**.
- **Đúng phải là:** SOS là cụm **16:08–16:11**: nến đầu tiên đóng cửa vượt biên phụ trên là **16:08** (c=4508.6, **VSA 3.71x**, 323 lot), tiếp 16:09 (302 lot, 3.04x), 16:10 (**445 lot**, 3.76x), 16:11 (421 lot, 3.08x). Đó là spread mở rộng + volume tăng của định nghĩa SOS.
- **Dấu hiệu quyết định trên chart:** panel khối lượng có cụm cột cao ở ~16:08–16:11 và ở 16:24; chỗ dán nhãn SOS (16:45–16:48) volume 57/71/47/29 lot.
- **Nghi phạm trong thuật toán:** cùng lỗi hệ thống của cả lô — điều kiện "3 nến liên tiếp đóng cửa vượt biên phụ ≥30 tick **và thân ≥45%**": 16:08 thiếu 1 giá so với mốc +30 tick, 16:10 (thân 0.41) và 16:11 (thân 0.15) bị loại vì thân nhỏ do râu dài, nên chuỗi chỉ khớp muộn ở cụm nến lặng 16:46–16:48. Sửa: định vị nhãn tại nến phá volume lớn nhất, dùng 3 nến sau chỉ để xác nhận.

### 6. Cú phá không đi tới đâu — nên kết luận "cấu trúc thất bại", không phải Tích luỹ hoàn tất — THEORY §9
- Sau LPS[D] 17:13 @4504.3 (đã lùi vào **dưới** biên chính trên 4505), giá đi ngang 4502.0–4509.5 suốt 78 nến tiếp theo, không có xu hướng mới. Range đóng ở Phase D là đúng theo spec, nhưng nhãn tổng "Tích luỹ (ACC)" gợi ý một kết luận mạnh hơn dữ liệu cho phép — nên gắn thêm dấu "cú phá chưa xác nhận".

## Đạt
- MOVE trước climax dài nhất lô: **56.2 giá / 66 nến**, hiệu suất 0.49 — điều kiện CẦN của L1 đạt rõ.
- Biên chính = climax + AR khớp đúng mức AR (4505.0), không bị kéo theo giá — L3 đạt.
- Biên phụ đúng 1 cái mỗi bên (4483.8 / 4506.6), đều là cực trị xa nhất — L3 đạt.
- UA (15:54 @4506.6) đặt đúng vai: thăm dò nhẹ trên biên AR, giữ ở lại Phase B chứ không nhảy sang Phase C — đúng mục 5.1 và đúng L6 (không dùng ST[B]).
- LPS[C] và LPS[D] mỗi cái **một điểm duy nhất** — đúng L7 (dù vai của LPS[C] sai, cách vẽ thì đúng).

## Cần hỏi người học
- Với ca V-reversal như bài này (giá bật khỏi đáy rồi đi ngang **ở tầng cao hơn**), anh muốn máy **bỏ ứng viên** vì Phase A không có lần chạm đáy thứ hai, hay **dời range lên** vùng đi ngang mới (4503–4513) và coi cú bật là move dẫn vào range đó?
