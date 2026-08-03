# Chấm bài #14 — Tái phân phối (RE-DIST) · 2026-05-20 01:30 → 04:23 (120 nến M1)

**Điểm: 1/10** — **Không nên vẽ range ở đây.** 120 nến phiên Á với khối lượng trung bình **5.1 lot/nến**, ba trong năm nhãn đặt trên nến 1 lot. Đây là nhiễu thanh khoản, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range là nhiễu phiên Á, không phải vùng đấu giá — luật vi phạm: L1 (tinh thần) + lỗi kinh điển CHART_CASES "khung quá thô / range quá vụn"
- **Thuật toán gắn:** một range đủ Phase A→D trong **120 nến** (01:30–04:23 UTC = giữa phiên Á).
- **Đúng phải là:** không vẽ. Khối lượng trung bình toàn range **5.1 lot/nến**; Phase D 26 nến chỉ có **87 lot**. Theo chuẩn chấm đã chốt: một TR M1 chỉ 60–100 nến mà đủ Phase A→E thì phải nghi ngay là nhiễu.
- **Dấu hiệu quyết định trên chart:** panel volume gần như phẳng trên toàn bộ nửa phải chart; rất nhiều nến là gạch ngang (O=H=L=C) vì chỉ có 1–2 lot khớp.
- **Nghi phạm trong thuật toán:** không có **sàn khối lượng tuyệt đối** và không có lọc phiên. VSA là tỉ số nên 25 lot / TB 5.7 lot = 4.42x trông như climax, trong khi 25 lot là con số vô nghĩa trên GC.

### 2. SC không chặn move — đáy thật xuất hiện 6 nến sau đó — luật vi phạm: L1
- **Thuật toán gắn:** SC 4504.1 (01:30, VSA 4.42x).
- **Đúng phải là:** nến **01:36** rơi xuống **4491.0** với VSA **6.97x** (54 lot) — thấp hơn "SC" **13.1 giá** và mạnh hơn hẳn. Đó mới là cây chặn đợt giảm. Biên chính dưới 4504.1 vì thế sai 13.1 giá trên nền biên chính chỉ cao 19.1 giá — sai bằng 69% chiều cao range.
- **Dấu hiệu quyết định trên chart:** ngay sát phải vạch Phase A có một cây đỏ dài xuyên xuống tận nét đứt 4491.0, kèm thanh volume vàng cao nhất chart.
- **Nghi phạm trong thuật toán:** giống bài #11/#12 — mục 3(2) chỉ kiểm cực trị của cửa sổ nhìn lại, không kiểm về sau. Ca này còn dễ sửa hơn: cực trị mới xuất hiện chỉ **6 nến** sau climax.

### 3. SOW dán lên nến 1 lot, không bứt được biên phụ — luật vi phạm: L3 + THEORY §4.1 (SOW = spread + volume TĂNG)
- **Thuật toán gắn:** SOW tại 4500.0, 03:37. Nến đó: **O=H=L=C=4500.0, volume 1 lot, VSA 0.28x**.
- **Đúng phải là:** không có SOW. Biên phụ dưới là 4491.0; giá đóng cửa 4500.0 còn cách nó **9 giá**. Một nến 1 lot biên độ 0 là định nghĩa ngược của "dấu hiệu yếu kém".
- **Dấu hiệu quyết định trên chart:** nhãn SOW nằm cao hơn nét đứt biên phụ gần một nửa chiều cao range; tại đó panel volume không có thanh nào nhìn thấy.
- **Nghi phạm trong thuật toán:** điều kiện phá thật (mục 5.1 Kết cục B) yêu cầu thân ≥45% — nến `brat = 0.00` **không thể** thoả. Vậy nhánh bắn SOW này chắc chắn đi qua đường thứ hai: **"ở ngoài quá 40 nến mà không quay lại"**, và khi đó máy dán nhãn lên nến hiện tại thay vì lên cây đã đẩy giá ra. Đây là bug định vị nhãn cần vá.

### 4. LPSY[C] cũng đặt trên nến 1 lot — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** LPSY[C] tại 4501.0 (03:04), **VSA 0.18x, brat 0.00, 1 lot**.
- **Đúng phải là:** đáy thật của Phase C là **4488.0 (03:08, VSA 0.93x)** — tức trong "Phase C" giá còn phá xuống dưới cả biên phụ 4491.0 mà máy không ghi nhận gì (lặp lại lỗi L3 của bài #12/#13). Nhãn LPSY[C] đúng về hình thức (1 điểm, đúng L7) nhưng đứng trên một nến trống.

### 5. Tên range ngược với kết cục thật — luật vi phạm: L4
- **Thuật toán gắn:** Tái phân phối (phá xuống).
- **Đúng phải là:** 60 nến sau khi range đóng, giá lên **4514.0**, đóng cửa **4509.2** — trên cả biên chính dưới 4504.1. Không có đợt xả nào tiếp diễn.
- **Nghi phạm trong thuật toán:** tên chốt tại nến SOW giả (lỗi 3).

### 6. Phase A dài nhất, Phase B ngắn thứ nhì — luật vi phạm: L9
- **Thuật toán gắn:** A 49n · B 24n · C 22n · D 26n.
- **Đúng phải là:** Phase B phải là phase dài nhất (L9). Ở đây A dài gấp đôi B, và B (24n) gần bằng C (22n) — dải phase gần như chia đều bốn phần, dấu hiệu điển hình của cấu trúc bị gò ép cho khớp khuôn (CHART_CASES lỗi chung #7: "gò ép dữ liệu cho khớp mô hình").

## Đạt
- MOVE trước climax là thật: 39.9 giá / 33 nến / hiệu suất 0.46 — thoả điều kiện CẦN của L1 (đợt giảm này có thật, chỉ có điểm chặn là bị gán sai).
- AR 4523.2 rất rõ: VSA **5.57x**, bật 32.2 giá từ đáy thật 4491.0 — cú bật ngược không thể tranh luận.
- ST[A] 4501.2 với VSA 0.88x — co lại đúng tinh thần test, và Phase A kết thúc đúng tại ST[A] (L2).
- LPSY[C] và SOW mỗi loại chỉ 1 nhãn, không spam; đúng L7 về hình thức.

## Cần hỏi người học
- Anh muốn đặt **sàn khối lượng tuyệt đối** bao nhiêu lot/nến để máy được phép mở range trên GC M1? Không có con số này thì phiên Á sẽ tiếp tục sinh ra loại range như bài #14 (nghi phạm số 1 trong danh sách review của chính anh: "ngưỡng 1.4× + 2.2x có thể quá lỏng ở phiên Á").
