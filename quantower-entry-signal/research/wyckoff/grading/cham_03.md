# Chấm bài #03 — Phân phối (DIST) · 2026-01-21 06:34 → 2026-01-22 05:50 (127 nến M1)

**Điểm: 1/10** — climax hỏng, Phase C dài gấp gần 4 lần Phase B, LPSY[C] nằm ngoài range. Phải vẽ lại từ đầu.

## Lỗi (nặng → nhẹ)

### 1. Nến mở range KHÔNG có một tính chất climax nào — luật vi phạm: L1 + mục 3 spec
- **Thuật toán gắn:** climax tại 06:34, giá 4989.4, **VSA 0.85x**, **biên độ 0.0 giá** (O=H=L=C=4989.4, volume 2).
- **Đúng phải là:** điều kiện mở range của chính thuật toán đòi biên độ ≥1.4× ATR20 **và** VSA ≥2.2x. Nến này trượt cả hai. Cây cao trào thật nằm ở **+3 (06:57): volume 111, VSA 13.62x**, biên độ 7.4 giá, thân 0.72, **nến giảm** — đó mới là cây chặn move tăng 188.8 giá và mở đầu cấu trúc.
- **Dấu hiệu quyết định trên chart:** cột volume vàng khổng lồ duy nhất của cả ảnh nằm ở 01-21 ~07:00, cao gấp ~5 lần mọi cột khác — nằm **trong Phase A**, không được gán nhãn gì.
- **Nghi phạm trong thuật toán:** cơ chế tách "mức climax dời theo cực trị giá" khỏi "nhãn dời theo VSA" (v6 lỗi #1) — mức bị kéo sang một nến chấm 2 lot chỉ vì nó cao hơn 0.5 giá. Cần **khoá lại**: mức climax chỉ được dời sang nến vẫn thoả điều kiện climax gốc (VSA ≥2.2x hoặc biên độ ≥1.4× ATR).

### 2. Nhãn BCLX nằm ngoài range, thấp hơn biên trên 30 giá — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại **04:19**, giá **4958.9** — trước nến mở range (06:34) 2 giờ 15, và nằm ở **36% chiều cao range** tính từ đáy.
- **Đúng phải là:** nhãn climax phải nằm tại mức biên chính trên 4989.4.
- **Dấu hiệu quyết định trên chart:** chấm BCLX vẽ **hoàn toàn bên trái khung range**, ngồi giữa thân đường move tăng màu xám. Lỗi #4 vòng v7 tuyên bố đã kẹp cố định — **chưa vá**, lặp lại y hệt bài #01/#04/#05.

### 3. Phase C = 55 nến, dài gấp 3.7 lần Phase B (15 nến) — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A=18 · B=15 · **C=55** · D=25 · E=15.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Ở đây C chiếm **43% cả range** và B là phase **ngắn thứ hai**. Cấu trúc này tự phủ định cả hai luật tỉ lệ.
- **Dấu hiệu quyết định trên chart:** dải Phase C kéo từ 01-21 13:55 tới 20:52 và bao trọn cả cú mSOW ở 17:31 — tức nguyên một đoạn giá lùng bùng hai chiều bị nhét vào "phase ngắn nhất".
- **Nghi phạm:** cửa sổ gán ngược Phase C nới từ 0.5× lên **0.8× độ dài Phase B** (sửa #3 của v7). Vá được lỗi "thiếu Phase C" nhưng đẻ ra lỗi ngược: khi Phase B ngắn thì điểm neo LPSY[C] lùi quá xa về quá khứ, kéo Phase C phình. Cần thêm **trần tuyệt đối** cho độ dài Phase C, ví dụ ≤ độ dài Phase B.

### 4. LPSY[C] đặt ở 4989.7 — NGOÀI biên chính trên — luật vi phạm: spec v6 mục 1.5 + THEORY §4.1
- **Thuật toán gắn:** LPSY[C] 4989.7, trong khi biên chính trên = **4989.4**.
- **Đúng phải là:** spec của chính thuật toán bắt pivot Phase C phải nằm **trong range**. Và về Wyckoff, một điểm vượt qua biên trên rồi rơi xuống là **UT hoặc UTAD**, không phải LPSY — LPSY là *đợt phục hồi yếu trong biên hẹp* sau khi test kháng cự (THEORY §4.1).
- **Dấu hiệu quyết định trên chart:** nhãn LPSY[C] vẽ nằm **trên** đường nét liền biên chính trên, chồng lên nhãn "bien CHINH tren 4989.4".
- **Nghi phạm:** ràng buộc "pivot trong range" so bằng `<=` với biên nhưng mức biên đã bị dời (xem lỗi 1) nên sát nút; hoặc so bằng close còn pivot lấy theo high.

### 5. mSOW gán trên nến VSA 0.57x và ghi sai phase — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** mSOW tại 17:31, 4916.4, **VSA 0.57x**, thân 0.00; cột "Phase" ghi **B** trong khi 17:31 nằm giữa Phase C (13:55→20:52).
- **Đúng phải là:** sửa #5 của v7 nói mốc hạ cấp phải quét lại lấy **nến VSA cao nhất trong đoạn thăm dò**. Nến 0.57x thân 0 rõ ràng không phải nến mạnh nhất của đoạn. **Chưa vá.**
- **Dấu hiệu quyết định trên chart:** chấm mSOW nằm trên biên phụ nét đứt 4916.4, cây nến ở đó là một vạch mảnh không thân.

### 6. SOW không đóng cửa vượt biên phụ — luật vi phạm: L3
- **Thuật toán gắn:** SOW tại **4928.5** (VSA 5.00x, thân 0.77).
- **Đúng phải là:** biên phụ dưới đã là **4916.4**. Theo L3, SOW muốn tính là mạnh phải đóng cửa **bứt qua biên phụ**. 4928.5 nằm lửng **giữa** biên chính 4941.5 và biên phụ 4916.4 — theo chính spec v6 đó là vùng "chưa kết luận".
- **Dấu hiệu quyết định trên chart:** chấm SOW nằm rõ ràng **trên** đường nét đứt 4916.4.

## Đạt
- **ST[A] đúng vai (L2):** 4985.9 = **93% chiều cao**, test sát mức climax 4989.4 với VSA 0.13x (volume co lại). Ràng buộc 0.4 mới có tác dụng ở ca này.
- **Tên range (L4):** origin BCLX + phá xuống thật = Phân phối — đúng bảng 4 pattern, và giá sau đó rơi tiếp xác nhận.
- Chú thích er đã đổi theo dấu (er=0.09 → in "hiệu quả"), không còn hard-code "hấp thụ NGHI VẤN".
- Biên phụ nới đúng một lần bởi cú mSOW, tỷ lệ 1.53x — không còn ca "tự nới rồi tự vượt".
