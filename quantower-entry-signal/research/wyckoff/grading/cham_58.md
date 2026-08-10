# Chấm bài #58 — Tích luỹ (ACC) · 2026-07-27 03:30 → 07:41 (250 nến M1)

**Điểm: 8/10** — Vẽ đúng. Đây là bài duy nhất trong lô đi trọn A→E đúng khuôn CBR; chỉ cần sửa vị trí nhãn climax và một cảnh báo còn thiếu.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC? lệch khỏi nến mở range — luật vi phạm: L3 (mốc biên) / lỗi cụm climax
- **Thuật toán gắn:** nhãn **SC? tại 03:32, giá 4088.5** (nến +2, VSA 2.66×), trong khi mức climax và mốc mở range là **03:30, 4087.0** (nến +0, VSA 1.21×).
- **Đúng phải là:** nhãn đứng tại nến tạo ra biên dưới 4087.0. Lệch 2 nến / 1.5 giá là nhẹ hơn hẳn bài #57, nhưng vẫn khiến chấm đỏ không nằm trên biên nét liền mà nó sinh ra.
- **Dấu hiệu quyết định trên chart:** chấm SC? nằm cao hơn nét liền "biên CHÍNH duoi 4087.0" một chút, thấy rõ ở phần bên trái chart.
- **Nghi phạm trong thuật toán:** vẫn là lỗi nhãn cụm climax chưa sửa (13.1c revert).

### 2. Không gắn cờ "climax yếu" cho một range sinh từ cú phá — luật vi phạm: L1 (mức nhẹ)
- **Thuật toán gắn:** SC? với VSA nến mở **1.21×**, biên độ **1.5 giá** — dưới cả hai ngưỡng climax (2.2× / 1.4× ATR). Phiếu có ghi "[SINH TU CU PHA, khong co climax that]" nên không phải giấu, nhưng chart chỉ có dấu `?`.
- **Đúng phải là:** hoặc cờ "(yếu)" như AR, hoặc ghi thẳng trên nhãn. Người đọc chart dễ tưởng đây là cao trào bán thật.
- **Ghi chú:** move giảm trước đó (4097 → 4087 trong ~40 nến) là thật nhưng mỏng — range này đứng được là nhờ cấu trúc phía sau, không nhờ climax.

### 3. Chỉ số hiệu suất/nỗ lực chỉ đọc một nhịp — trình bày
- Phiếu chọn "nhịp nỗ lực/kết quả cao nhất" là 06:05 với er=0.61 và kết luận "nhịp HIỆU QUẢ". Trên panel volume, đoạn 05:39–06:12 mới là chỗ đáng nói: volume nở dần trong khi giá bò lên từ 4086.5 — đúng hình **hấp thụ** trước SOS. Không sai luật nào, nhưng chỉ số đang bỏ lỡ đúng đoạn cần đọc.

## Đạt
- **Phase A đủ 3 lần đổi hướng (L2):** SC? 4087.0 → AR 4095.0 (VSA 1.75×, thân 0.44 — cú bật thật) → ST[A] 04:18 tại 4088.9, cách climax **1.9 giá = 24% chiều cao**, retrace 76% khoảng AR↔climax. Phase A kết thúc đúng tại ST[A]. Đây là ca cho thấy ngưỡng 0.55 mới đang hoạt động đúng.
- **Tỉ lệ phase chuẩn (L8, L9):** A=49 · **B=120 (dài nhất)** · **C=20 (ngắn nhất)** · D=25 · E=37.
- **Phase D/E đúng CBR (L10):** mSOS 06:12 phá hụt lên 4098.4 → LPS[C] 06:20 tại 4093.3 (một điểm duy nhất, đúng L7) → **SOS 06:40 tại 4100.4 (VSA 2.05×) đóng cửa vượt cả biên phụ trên 4098.4** → LPS[D] 06:44 tại 4099.4 **giữ được trên biên chính 4095.0** → Phase E giá đi tiếp lên 4108 = hơn 1× chiều cao range. Đúng chuỗi phá → retest giữ ngoài → đi tìm vùng giá mới.
- **Tên range đúng (L4):** origin SC + phá thật lên = **Tích luỹ**.
- **Biên (L3):** biên chính 4087.0/4095.0 cố định; biên phụ mỗi bên 1 cái (4086.5 / 4098.4), đúng cực trị xa nhất, tỷ lệ 1.49×.
- **LPS[C] nằm nửa trên range** sau khi bỏ ràng buộc "đúng nửa range" — ở đây là **higher low** ngay trước SOS, đúng vai LPS, không phải lỗi.
