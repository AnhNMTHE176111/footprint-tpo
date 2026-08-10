# Chấm bài #29 — Tái phân phối (RE-DIST) · 2026-06-08 01:30 → 05:59 (269 nến)

**Điểm: 6/10** — khung range và tỷ lệ phase đọc được, SOW là cây phá thật. Phải sửa vị trí ST[A], và không được kết luận `completed` khi giá lập tức quay lại trong range.

## Lỗi (nặng → nhẹ)

### 1. Kết luận "completed / Tái phân phối" trong khi cú phá không giữ được — luật vi phạm: L10, THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** SOW (05:34, 4311.2) → LPSY[D] (05:40, 4317.6) → **Phase E dài 1 nến** → đóng range, đặt tên RE-DIST.
- **Đúng phải là:** Phase E là giai đoạn giá **rời range đi tìm vùng giá mới**. Trên ảnh, ngay sau 06:00 giá bật thẳng từ 4310 lên **4337** — tức chui lại vào trong biên chính (4323.6–4354.8) và ở lì đó tới hết chart. Cú phá đã bị vô hiệu; đúng ra phải hạ SOW xuống mSOW và đóng range ở trạng thái "chưa rõ hướng".
- **Dấu hiệu quyết định trên chart:** Phase E = **1 nến** chính là máy tự thú nhận điều này — nó chốt E rồi ngay nến sau giá lùi vào biên nên E dừng luôn. Một Phase E dài 1 nến phải được đọc là **thất bại**, không phải "hoàn tất".
- **Nghi phạm trong thuật toán:** điều kiện chốt Phase E ("đi thêm ≥ 0.5× chiều cao khi hết 25 nến") bắn **trước** khi kiểm tra giá có giữ ngoài biên hay không. Nên thêm: `len(E) < k nến` (k ~10) ⇒ không đặt tên 4 mẫu hình.

### 2. ST[A] cách climax 37% chiều cao — vẫn là nhịp giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 02:20 tại **4335.0** (biên chính 4323.6–4354.8, cao 31.2).
- **Đúng phải là:** ST[A] phải là cú quay lại **vùng climax** rồi bị chặn. 4335.0 cao hơn climax **11.4 giá = 37%** chiều cao. Nhìn ảnh: chấm ST[A] nằm rõ ràng ở giữa hai đường liền cam, trong khi cú test thật sự về vùng 4325–4327 mãi tới ~03:30 (Phase B) mới xảy ra.
- **Dấu hiệu quyết định trên chart:** hồi từ AR 4354.8 xuống 4335.0 = 63% khoảng AR↔climax → thoả ngưỡng mới 0.4 rất dư. Ngưỡng đo **từ AR** không kiểm soát được **khoảng cách tới climax** — đúng lỗi mục 13.1 chưa vá.
- **Nghi phạm trong thuật toán:** như bài #25 — cần ràng buộc thứ hai `|st_a − climax| ≤ ~0.35 × chiều cao`.

### 3. LPSY[C] đặt ở 53% chiều cao, không phải test biên trên — luật vi phạm: L8
- **Thuật toán gắn:** LPSY[C] 05:04 tại 4340.1, VSA 0.90×.
- **Đúng phải là:** LPSY[C] trước một cú phá xuống là **nhịp hồi cuối cùng lên phía biên trên**. 4340.1 chỉ nhỉnh hơn trung điểm range (4339.2) đúng 0.9 giá — nó lọt qua ràng buộc "nửa trên" bằng đúng một sợi tóc. Đỉnh thật của nhịp cuối là ~4348 quanh 04:40.
- **Nghi phạm trong thuật toán:** ràng buộc "đúng nửa range" quá lỏng; nên yêu cầu pivot nằm ở **1/3 trên** hoặc chọn đỉnh cao nhất trong cửa sổ thay vì pivot cuối cùng.

### 4. (nhẹ) Phase C 30 nến ≈ Phase D 25 nến
- L8 nói Phase C là phase ngắn nhất. Ở đây C(30) dài hơn D(25). Hệ quả trực tiếp của lỗi #3: LPSY[C] chọn quá sớm nên đoạn C bị kéo dài. Không phải lỗi độc lập.

## Đạt
- L1: MOVE 43.3 giá / 62 nến / hiệu suất 0.35 và cây climax (VSA 3.55×, biên độ 14.9 giá) là **đáy** chặn đúng đợt giảm đó — mở range chuẩn.
- L3: biên chính = climax 4323.6 + AR 4354.8, cố định; không có biên phụ nào (tỷ lệ 1.00×) và điều đó **đúng** — không cú thăm dò nào ra khỏi biên trong suốt Phase B. Đây là ca vẽ biên sạch nhất lô.
- L9: Phase B 163 nến, dài nhất — đúng; bias=−1 (chỉ với tới biên dưới) khớp với hướng phá xuống thật.
- L4: origin SC + phá xuống = Tái phân phối — đúng bảng, dù kết luận `completed` thì sai (lỗi #1).
- Khối lượng: SOW neo đúng cây VSA **7.36×** thân 0.93 — đây là cách neo nhãn phá vỡ mà các bài khác trong lô làm sai.
- Chú thích nỗ lực/kết quả er=0.63 ghi "HIỆU QUẢ" — đúng dấu.
