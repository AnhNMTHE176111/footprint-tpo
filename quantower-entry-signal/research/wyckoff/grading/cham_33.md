# Chấm bài #33 — Tái phân phối (RE-DIST) · 2026-06-08 01:30 → 05:59 (269 nến M1)

**Điểm: 6/10** — khung range vẽ đúng và đẹp, nhưng phải sửa 2 nhãn: ST[A] và LPSY[C] đều rơi giữa range, và cú "SOW" thực chất là một Shakeout thất bại.

## Lỗi (nặng → nhẹ)

### 1. Phase D không giữ được ngoài biên — cú phá là SHAKEOUT, không phải SOW — luật vi phạm: L5, L10
- **Thuật toán gắn:** SOW 05:34 @4311.2 (VSA 7.36x) → LPSY[D] 05:40 @4317.6 → Phase E dài **1 nến**.
- **Đúng phải là:** L10 đòi retest phải **giữ được ở ngoài biên** rồi giá mới đi tiếp. Trên ảnh, sau cây rơi xuống ~4297, giá lùng bùng ngoài biên khoảng 18 nến rồi bật ngược **vào trong range**, giao dịch quanh 4325-4340 (trên biên chính dưới 4323.6) suốt ~20 nến. Đúng định nghĩa L5: phá ra, ở ngoài một lúc, rồi quay lại = **Shakeout = một SOW thất bại**.
- **Dấu hiệu quyết định trên chart:** cụm nến xanh từ ~05:52 kéo giá lên trên đường biên cam 4323.6; Phase E chỉ 1 nến chính là dấu hiệu thuật toán tự biết "không có gì đi tiếp" nhưng vẫn đóng nhãn SOW.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận SOS/SOW chỉ kiểm nến phá + volume, không kiểm **N nến sau đó có đóng cửa nào quay lại trong biên chính hay không**. Cần một cửa sổ xác nhận (vd 10-15 nến) trước khi cho phép chuyển sang Phase D; nếu vi phạm → hạ nhãn xuống Shakeout và trả cấu trúc về Phase C.

### 2. ST[A] rơi giữa range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 02:20 @4335.0.
- **Đúng phải là:** ST[A] phải quay lại **test vùng climax** (4323.6). 4335.0 nằm cách climax 11.4 giá trên một range rộng 31.2 giá, và cách trung điểm range (4339.2) đúng 4 giá — đây là "một cái ngọ nguậy giữa range", không phải test lại SC.
- **Dấu hiệu quyết định trên chart:** marker ST[A] nằm rõ ràng ở giữa hai đường biên cam, không chạm đường 4323.6.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC=0.55` — ca này hồi 63%, vừa đủ qua ngưỡng mới. Ngưỡng 0.55 vẫn cho phép ST[A] đứng giữa range. Nên đổi sang tiêu chí **khoảng cách tới mức climax ≤ k tick** (hoặc frac ≥ 0.85), thay vì đo phần trăm hồi từ AR.

### 3. LPSY[C] đặt đúng giữa range — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] 05:22 @**4339.0**; range 4323.6-4354.8 → trung điểm 4339.2.
- **Đúng phải là:** Phase C là tín hiệu đầu tiên cho thấy giá **ở biên này** bắt đầu phá biên kia — nhãn phải nằm sát một biên. Đây là điểm neo lệch đúng 0.2 giá so với tâm range, cách cả hai biên ~15 giá. Ràng buộc "gần biên" mới thêm rõ ràng **chưa chặn được ca này**.
- **Đúng phải là (cụ thể):** LPSY[C] hợp lý hơn là cú hồi lên ~4348-4350 quanh 05:10-05:14 rồi thất bại — đó là lần cuối phe mua cố giữ biên trên trước khi rơi.
- **Nghi phạm trong thuật toán:** điều kiện "gần biên" của Phase C có vẻ vẫn tính theo khoảng cách tương đối rất lỏng, hoặc chọn ứng viên theo thứ tự thời gian trước khi lọc theo vị trí. Phải lọc vị trí trước (ví dụ trong 25% range tính từ biên), rồi mới lấy ứng viên gần SOS/SOW nhất.

### 4. AR đặt tại đỉnh thứ hai, cách climax 30 nến — luật vi phạm: L2 (AR = cú bật ngược ngay sau climax)
- **Thuật toán gắn:** SC 01:30 → AR **02:00** (30 nến sau).
- **Đúng phải là:** cú bật tự động là nhịp ngay sau climax; trên ảnh giá đã bật từ 4323.6 lên ~4352 trong khoảng 01:31-01:42, sau đó chop rồi mới nhích lên 4354.8. Lấy đỉnh 02:00 làm AR khiến Phase A kéo tới 51 nến.
- **Ảnh hưởng:** nhỏ (biên trên chỉ lệch ~3 giá), xếp sau về mức nghiêm trọng.
- **Nghi phạm trong thuật toán:** AR = max(high) trong cửa sổ N nến sau climax, không đòi liên tục/không cắt tại nhịp thoái đầu tiên.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 43.3 giá / 62 nến bị chặn bởi nến 01:30 VSA **3.55x**, biên độ 14.9 giá — và nến climax này **đúng là nến neo range**, không lệch cụm như bài #32/#35. Đây là ca climax sạch nhất trong lô.
- Tỷ lệ phase đúng khung lý thuyết: B=181n (dài nhất, L9), C=12n (ngắn nhất trong nhóm B/C/D, L8), A=51n. Đây là bài duy nhất trong lô 31-36 có trật tự độ dài phase chuẩn.
- Biên chính cố định đúng L3, không bị kéo theo giá; suốt 181 nến Phase B giá không vượt ra ngoài → biên phụ = biên chính (1.00x) là kết luận trung thực, không bịa biên phụ.
- Tên range đúng L4: MOVE giảm → SC → phá xuống = Tái phân phối (dù cú phá sau đó thất bại, tên vẫn đúng theo hướng phá).
- Đọc effort/result có nội dung: SOT trên `chớm` n=2 với volume nhịp cuối/đầu 0.77 (cạn kiệt) — đúng tinh thần §7 THEORY, và khớp với việc giá không giữ nổi biên trên nửa sau Phase B.
