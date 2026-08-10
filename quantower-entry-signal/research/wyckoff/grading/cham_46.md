# Chấm bài #46 — Tái tích lũy (RE-ACC) · 2026-07-06 16:58 → 19:03 (125 nến M1) · sinh từ cú phá

**Điểm: 2/10** — Không nên vẽ range ở đây. Biên chính 6.0 giá / 125 nến với đủ 5 phase là nhiễu, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Không phải một vùng đấu giá thật — luật vi phạm: L1, và tiêu chí "khung quá thô / range quá vụn" trong CHART_CASES
- **Thuật toán gắn:** range cao **6.0 giá (0.14%)**, dài 125 nến, đủ Phase A→E.
- **Đúng phải là:** không mở range. Đây là 2 tiếng đi ngang bên trong nhịp tăng của cấu trúc lớn hơn (range #45) — nhìn ảnh thấy rõ giá chỉ đang bò lên theo bậc thang từ 4152 tới 4180.
- **Dấu hiệu quyết định:** climax `BCLX?` có **VSA 0.82x**, biên độ **1.4 giá**, thân 0.50 — không có bất kỳ tính chất cao trào nào. Phiếu tự khai "SINH TU CU PHA, khong co cao trao that". Đủ 5 phase gói trong 6 giá thì mỗi "phase" chỉ là vài cây nến M1 lắc.
- **Nghi phạm:** nhánh SIDEWAYS bỏ hẳn yêu cầu climax (mục 5.4 spec) mà **không** thay bằng bất kỳ sàn chiều cao nào. Cần sàn tuyệt đối cho chiều cao biên chính (ví dụ ≥ 3–4× ATR20), hoặc yêu cầu range con phải sống độc lập được sau khi range cha đóng.

### 2. Range con sinh khi range cha còn đang chạy — luật vi phạm: L3 (biên chính cố định) + cắt vụn cấu trúc
- **Dấu hiệu quyết định:** range này mở **16:58**, trong khi range #45 chạy tới **17:15** và LPS[D] của #45 nằm ở 17:01. Hai range chồng nhau 17 nến, một nhãn Phase D của cha nằm lọt trong Phase A của con.
- **Đúng phải là:** #45 và #46 là **một** cấu trúc tích luỹ, phá lên ở 16:50 rồi chạy tiếp tới 4180. Tách làm hai làm mất tên của cha (`superseded`) và đẻ ra một range giả ở con.

### 3. ST[A] xuyên qua mức climax 58% chiều cao, không phải test — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 17:26 tại **4171.6**, trong khi mức climax là 4168.1.
- **Dấu hiệu quyết định:** vượt climax **3.5 giá = 58% chiều cao range**; hồi từ AR = (4171.6−4162.1)/6.0 = **158% khoảng AR↔climax**. Đây là giá đang **đi tiếp**, không phải bị chặn nhẹ lần nữa.
- **Nghi phạm:** trần "ST[A] vượt climax ≤ 1.0× chiều cao range" hoàn toàn vô dụng với range hẹp — 3.5 ≤ 6.0 nên lọt. Trần này phải là tỷ lệ nhỏ hơn nhiều (0.2–0.3×) hoặc đo bằng ATR, không đo bằng chính chiều cao range.

### 4. SOS đóng cửa THẤP HƠN mSOS, và neo vào cây yếu hơn hẳn — luật vi phạm: L3
- **Thuật toán gắn:** mSOS 18:00 tại **4173.8, VSA 2.55x**; SOS 18:16 tại **4173.4, VSA 0.96x**.
- **Đúng phải là:** cây phá thật là 18:00 (hoặc cây bùng 18:17–18:20 trên ảnh). Nhãn *minor* đang đeo vào cây mạnh, nhãn *phá thật* đeo vào cây dưới trung bình — đúng lỗi 13.1b mô tả, **chưa sửa được**.
- **Dấu hiệu quyết định:** biên phụ trên ghi 4173.8 = đỉnh mSOS; SOS 4173.4 **chưa vượt** nó (thiếu 4 tick). Ca "SOS cách mSOS 1 tick" tái xuất nguyên vẹn.

### 5. Thiếu hẳn LPS[D] — luật vi phạm: L7, L10
- **Dấu hiệu quyết định:** Phase D dài 25 nến nhưng bảng sự kiện **không có nhãn nào** trong đoạn đó ngoài chính SOS. Trên ảnh, sau SOS giá lùi về ~4171 (18:22) rồi mới bung lên 4180 — nhịp retest có thật, không được ghi.

## Đạt
- **Phase C ngắn nhất (L8):** 6 nến, ngắn hơn cả D lẫn E. Đúng tỉ lệ.
- **Phase B dài nhất (L9):** 43 nến.
- **Nhãn `BCLX?` có dấu hỏi** và dòng chú thích "khong co cao trao that" — thuật toán **trung thực** về việc mình đang đoán. Ghi nhận điểm này.
- **Tên range (L4):** nếu chấp nhận khung này thì origin BCLX + phá lên = Tái tích luỹ, gọi tên đúng luật.
- Chú thích effort/result đọc đúng dấu (`er=1.27 — hấp thụ NGHI VẤN`), khớp với việc nhịp 17:29 có volume lớn mà giá không đi.
