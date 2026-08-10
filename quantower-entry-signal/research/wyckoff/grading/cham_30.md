# Chấm bài #30 — Tích lũy (ACC) · 2026-06-05 02:41 → 09:11 (390 nến M1)

**Điểm: 7/10** — Bài tốt nhất lô này về mặt cấu trúc: Phase A gọn, B dài, Shakeout đúng loại, CBR đủ. Còn hai lỗi vẽ biên và một nhãn sai vai.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ trên 4483.2 do chính cú phá THÀNH CÔNG sinh ra — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4483.2, đường đứt kéo ngược về đầu Phase A.
- **Đúng phải là:** phía trên **không có biên phụ**. L3 định nghĩa biên phụ = cực trị xa nhất do một thế lực **cố phá range gốc** tạo ra rồi bị đẩy về (UA/UT/DA, ST[A] vượt climax). 4483.2 là đỉnh đạt được trong Phase D **sau khi** SOS đã phá thật — đó là kết quả, không phải nỗ lực bị chặn.
- **Dấu hiệu quyết định trên chart:** suốt Phase A và B (217 nến) giá chưa từng vượt 4477 — đỉnh Phase B nằm sát biên chính trên 4476.1. Đường đứt 4483.2 vắt ngang cả vùng đó mà không có nến nào chạm.
- **Hệ quả:** SOS 06:46 tại 4479.3 bị so với một biên phụ 4483.2 do chính nó sinh ra → không bao giờ đạt tiêu chuẩn "SOS mạnh" của L3. Lỗi giống hệt bài #25.
- **Nghi phạm trong thuật toán:** hàm cập nhật biên phụ vẫn chạy sau khi Phase D đã mở. Phải khoá biên phụ tại thời điểm SOS/SOW được xác nhận.

### 2. Nhãn `mSOW` đặt ở biên TRÊN trong một range Tích luỹ — luật vi phạm: L6 + mục 9 (nhãn sai vai)
- **Thuật toán gắn:** `mSOW` 05:03 tại 4472.8 (VSA 4.08x) — nằm ở **nửa trên** range (giữa range = 4470.3), cách biên chính trên chỉ 3.3 giá; trên ảnh nó nằm ngay dưới đỉnh nhịp ~4477.
- **Đúng phải là:** một cú test biên trên rồi bị đẩy xuống thì tên đúng là **UT** (hoặc UA nếu vượt hẳn biên). L6 đã chốt: test nhẹ ở biên chỉ còn UA / DA / UT. Gọi "mSOW" cho một điểm ở biên trên vừa sai vị trí (SOW là chuyện của biên dưới) vừa lệch từ vựng với tên range đang là ACC.
- **Nhãn `mSOW` thứ hai (06:04, 4461.6)** thì đúng — nó đã ở dưới biên chính dưới 4464.5.
- **Nghi phạm:** nhánh gán mSOW/mSOS đang chọn theo "nến biên độ lớn + VSA cao trong Phase B" mà không kiểm **vị trí tương đối trong range** (bài học Ca #7 nguồn 7.pdf: vị trí trong range quyết định tên gọi).

### 3. Phase C (28 nến) dài hơn Phase D (25 nến) — luật vi phạm: L8
- Sát ranh giới nhưng vẫn sai chiều. Shakeout tạo đáy 06:18, giá đóng cửa trở lại trên 4464.5 khoảng 06:19-06:20 — Phase C nên kết ở đó (~3 nến sau Shakeout), phần còn lại (06:21→06:45, giá bò từ 4467 lên biên trên) thuộc về Phase D.
- **Nghi phạm:** Phase C đang kết thúc tại "nến trước SOS" thay vì tại nến hồi về trong biên sau cú shock.

### 4. Điều kiện L1 không kiểm được (ghi nhận, không trừ điểm)
- Phiếu số liệu bài này **thiếu hẳn dòng "MOVE truoc climax"**, và header tự ghi `[SINH TU CU PHA, khong co climax that]`, nhãn để là `SC?`. Tự khai báo như vậy là **trung thực và đúng cách** — hơn hẳn kiểu gò nhãn cho khớp mô hình mà giảng viên chê ở Ca #20 (7.pdf). Nhưng nghiêm theo L1 thì điều kiện CẦN (một MOVE rõ bị climax chặn) chưa được chứng minh, nên range này về nguyên tắc vẫn ở diện "chờ xác nhận" — và nó đã tự xác nhận bằng cấu trúc hoàn chỉnh phía sau.

## Đạt
- **Mục 2 (L2):** Phase A **23 nến**, gọn. ST[A] 03:03 tại 4462.5 xuyên nhẹ dưới climax 4464.5 → hồi 117% khoảng AR↔climax, thừa ngưỡng 55%. Phase A kết đúng tại ST[A]. Đây là ví dụ ngưỡng 0.55 chạy đúng.
- **Mục 3 (L3) — biên dưới:** biên phụ dưới 4454.8 = đáy Shakeout, đúng cực trị xa nhất, mỗi bên 1 biên. Biên chính 4464.5–4476.1 cố định, không kéo theo giá.
- **Mục 4 (L4):** origin move giảm + phá lên thật = Tích luỹ. Đúng bảng L4.
- **Mục 5 (L9):** Phase B **194 nến**, dài nhất, cách biệt lớn. Đúng L9.
- **Mục 6 (L5) — phân loại shock:** `Shakeout` gán **đúng**. Giá xuống dưới biên chính 4464.5 từ ~06:05 (mSOW 4461.6) đến ~06:19, tức lùng bùng ngoài biên khoảng 15 nến trước khi hồi — đúng định nghĩa Shakeout (một SOW thất bại), không phải Spring. Đối chiếu: bài #25 có hiện tượng gần giống mà lại gọi Spring — bài #30 mới là bài gọi đúng.
- **Mục 7 (L10):** SOS 06:46 (4479.3, VSA 2.73x) đóng cửa trên biên chính; LPS[D] 06:55 tại 4476.4 retest **giữ được trên** biên 4476.1; Phase E 121 nến đi tìm vùng giá mới lên 4499. Cụm D+E = CBR đầy đủ.
- **Mục 8:** panel volume cho thấy nhịp nỗ lực/kết quả cao nhất (05:32, effort 3.16x / result 4.19) được đánh là "hiệu quả, không phải hấp thụ" — đọc đúng; SOT phía dưới `SOT` n=3 kèm volume hấp thụ 1.04 đúng chiều với một cấu trúc chuẩn bị bung lên.
- **Mục 7 (L7):** LPS[D] chỉ đánh **1 điểm**, không vẽ vùng, không lặp. Đúng L7.
