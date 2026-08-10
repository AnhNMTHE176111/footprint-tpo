# Chấm bài #52 — Chưa rõ (BCLX) / DIST? · 2026-07-14 12:33 → 16:32 (239 nến M1)

**Điểm: 3/10** — khung range đặt đúng chỗ (vùng cân bằng sau cú nổ tin), nhưng cả mốc climax lẫn nhãn climax đều trượt khỏi cây quyết định, ST[A] rơi giữa range, và cấu trúc đã hoàn tất lại không được đặt tên.

## Lỗi (nặng → nhẹ)

### 1. Cả mốc climax lẫn nhãn climax đều KHÔNG phải cây quyết định — luật vi phạm: L3 + mục 8
- **Thuật toán gắn:** mốc mở range = nến **12:33** (VSA **1.98x**, thân/biên 0.20); nhãn BCLX đặt ở nến **12:31** (4104.7, VSA 7.01x) — tức nhãn nằm **trước** nến mở range 2 nến.
- **Đúng phải là:** cây quyết định là **12:30**: mở 4036.1 → cao 4098.4, đi **62.3 giá trong một nến**, volume 4597 = **VSA 14.64x**. Đó mới là cao trào; hai cây sau chỉ là dư chấn.
- **Dấu hiệu quyết định trên chart:** thanh volume duy nhất chạm trần panel dưới nằm ở 12:30; nến mở range (12:33) có VSA 1.98x — **dưới cả ngưỡng climax 2.2x** của chính thuật toán.
- **Nghi phạm:** hai cửa sổ tách nhau (giá trượt tự do 8 nến, nhãn kẹp riêng) — đúng chỗ đã revert ở 13.1c. Ở ca này nó khiến range mở bằng một cây không đủ tư cách climax.

### 2. MOVE trước climax đo trùm lên chính cụm climax — luật vi phạm: L1 (lỗi I cũ tái phát)
- **Thuật toán gắn:** MOVE 78.3 giá / 179 nến / hiệu suất 0.36.
- **Đúng phải là:** trong 179 nến đó, giá chỉ bò từ ~4020 lên ~4036 (16 giá, lắc liên tục — nhìn nửa trái ảnh là thấy vùng đi ngang); **62 trong 78.3 giá là do đúng cây 12:30 tạo ra**, mà cây đó thuộc cụm climax. Loại nó ra thì move còn ~16 giá / 179 nến, hiệu suất tụt xa dưới 0.35 → **không đủ điều kiện mở range**.
- **Dấu hiệu quyết định:** hiệu suất báo 0.36, sát ngưỡng 0.35 — chỉ cần trừ đúng phần climax là rớt.
- **Nghi phạm:** phép đo move loại "nến climax" theo `climax_i` (12:33) chứ không theo cả cụm, nên 12:30–12:32 vẫn tính là move.

### 3. ST[A] rơi giữa range, kéo Phase A dài 67 nến — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:39 tại **4096.4**. Climax 4112.5, AR 4076.2 → hồi 56% khoảng AR↔climax, vừa lọt ngưỡng mới 0.55.
- **Đúng phải là:** ST[A] là cú quay lại **test vùng climax**. Cách climax **16.1 giá** trên một range cao 36.3 giá thì không phải test — nó chỉ là một cái nhấp nhô giữa range (đúng lỗi mà 13.1b đã mô tả, chưa khỏi).
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm lơ lửng giữa khung, cách nét liền trên gần một nửa chiều cao khung.
- **Nghi phạm:** `STA_MIN_AR_FRAC = 0.55` vẫn quá lỏng khi biên độ range lớn; cần thêm trần tuyệt đối theo *khoảng cách còn lại tới climax* (ví dụ ≤ 25% chiều cao range) chứ không chỉ tỷ lệ hồi từ AR.

### 4. SOW đặt muộn 25 nến so với cú phá thật — luật vi phạm: L10
- **Thuật toán gắn:** SOW 16:07 tại 4065.4 (VSA 2.31x).
- **Đúng phải là:** cây phá dứt điểm nằm ở đoạn 15:49–15:55 (giá từ 4083.5 rơi thẳng qua biên chính dưới 4076.2 và không quay lại nữa). Nhãn SOW phải hồi tố về đó.
- **Dấu hiệu quyết định:** từ 15:50 trở đi mọi nến đều đóng dưới 4076.2; SOW lại nằm ở 16:07, khi giá đã ở ngoài biên 17 nến.

### 5. Cấu trúc đã hoàn tất nhưng không được đặt tên — luật vi phạm: L4
- Trạng thái `superseded`, tiêu đề "Chưa rõ (BCLX)". Origin BCLX + phá xuống thật (giá xuống 4065 rồi tiếp tục) = **Phân phối**. Range con #53 mở đúng tại nến SOW của range này — tức cơ chế SIDEWAYS đang cắt đôi một cấu trúc duy nhất và làm mất tên cả hai phần (lỗi "SIDEWAYS cắt vụn cấu trúc thật" đã liệt ở 13.1b, chưa sửa).

## Đạt
- Biên chính 4076.2 – 4112.5 ôm đúng vùng cân bằng sau cú nổ tin; tỷ lệ biên phụ/chính **1.07×** — biên không bị kéo theo giá (L3 làm tốt).
- Tỉ lệ phase đúng: B (127n) dài nhất, C (20n) ngắn nhất (L8, L9).
- Chuỗi Phase C đọc hợp lý: mSOW 15:42 (thọc xuống 4073.5, VSA 3.40x, thất bại quay vào range) → LPSY[C] 15:47 tại 4083.5 → phá thật. Đúng tinh thần "cú rũ thất bại rồi test lại rồi mới sụp".
- LPSY[C] và LPSY[D] mỗi cái đúng một điểm, phân đúng vai trước/sau cú phá (L7 + tránh lỗi Ca #3 nguồn 4.pdf).
- Chỉ số nỗ lực/kết quả 14:01 (er=36.67, "hấp thụ nghi vấn") lần này đọc đúng chiều — hết hard-code.
