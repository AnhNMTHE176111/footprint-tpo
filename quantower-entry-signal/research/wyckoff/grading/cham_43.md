# Chấm bài #43 — Tái phân phối (RE-DIST) · 2026-07-07 19:18 → 07-08 10:57 (878 nến M1)

**Điểm: 3/10** — Phase A vẽ đẹp, tên range cuối cùng đúng, nhưng máy đọc sai hai sự kiện quan trọng nhất: một cú phá LÊN giữ 6 tiếng bị gọi là "mSOS", và cây phá xuống thật (VSA 5.32x) bị gọi là "mSOW" trong khi nhãn SOW rơi vào cây yếu hơn ở sau.

## Lỗi (nặng → nhẹ)

### 1. 281/352 nến đóng cửa trên biên chính trên mà vẫn là Phase B — luật vi phạm: L5, L3
- **Thuật toán gắn:** một nhãn **mSOS** duy nhất tại 4144.7 (08-07 06:24), toàn bộ đoạn 01:26–07:19 nằm trong Phase B.
- **Đúng phải là:** đây là một cú phá lên **có giữ được** trong gần 6 tiếng rồi mới sụp — đúng nghĩa Wyckoff đó là **SOS thất bại = Shakeout/UT lớn** (theo L5: "phá ra, lùng bùng ngoài một lúc rồi mới quay lại"). Gọi "minor" cho một cú kéo dài 350 nến là hạ cấp sai. Đúng ra: hoặc bắn SOS rồi sau đó ghi nhận vô hiệu, hoặc đánh dấu Shakeout phía trên + Phase C.
- **Dấu hiệu quyết định trên chart:** đếm trên dữ liệu gốc, từ 01:26 đến 07:19 có **281/352 nến (80%) đóng cửa TRÊN biên chính trên 4128.9** — thoả thừa điều kiện "40 nến và ≥60% đóng ngoài biên" trong chính spec.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận phá vỡ đo bằng **biên phụ** (4144.7), mà biên phụ trên do chính cú phá này nới ra. Lỗi "biên phụ tự nới rồi tự vượt" **chưa được vá** ở v7 — ngưỡng 30 tick không đụng tới cơ chế nới biên. Phải đóng băng biên phụ phía đang test, hoặc đo nhánh "ở ngoài lâu" bằng biên chính.

### 2. Cây phá xuống thật bị gán mSOW; nhãn SOW rơi vào cây yếu hơn — luật vi phạm: mục 5.1 (nhãn hồi tố về cây phá thật)
- **Thuật toán gắn:** mSOW 08:18 tại 4091.3 (**VSA 5.32x**, volume 1145) rồi SOW 08:40 tại 4075.8 (VSA 3.18x, volume 1118).
- **Đúng phải là:** MSOW là cây **08:18** — nó là cây đầu tiên đóng cửa hẳn dưới biên chính 4102.7 (C=4097.8) với volume lớn nhất cả range. Cây 08:40 là nhịp nối tiếp, cùng lắm là SOW thứ hai.
- **Dấu hiệu quyết định trên chart:** trên ảnh, đoạn 08:03→08:20 là một cột nến sụp thẳng đứng từ 4129 xuống 4091 kèm thanh volume vàng cao nhất toàn chart. Không thể gọi cây đó là "minor".
- **Nghi phạm trong thuật toán:** cùng gốc lỗi #1 — cây 08:18 tự nới biên phụ dưới xuống 4091.3, nên chính nó bị loại khỏi tư cách SOW và bị hạ cấp; vá #5 ("quét lại lấy nến VSA cao nhất trong đoạn thăm dò") đặt sai chỗ: nó chỉ chọn nến trong đoạn *thăm dò đã bị hạ cấp*, không xét lại việc hạ cấp có đúng không.

### 3. ST[A] nằm giữa range, không test vùng SC — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 20:23 tại 4117.3, VSA 0.38x.
- **Đúng phải là:** test quay về vùng 4102–4108.
- **Dấu hiệu quyết định trên chart:** biên chính 4102.7–4128.9 = 26.2 giá; ST[A] ở 4117.3 = **cách climax 14.6 giá = 56% chiều cao range**. Hồi 11.6/26.2 = 0.44 nên vẫn lọt ngưỡng 0.4 mới.
- **Nghi phạm trong thuật toán:** ngưỡng ST[A] vẫn đo bằng nhịp hồi từ AR chứ không bằng khoảng cách tới climax — lỗi lặp ở cả #41, #42, #43.

### 4. Phase C (37 nến) dài hơn Phase D (17 nến) — luật vi phạm: L8
Phase C phải là phase ngắn nhất. LPSY[C] 08:03 (nến doji VSA 0.33x, thân 0.00 — test cạn cung, chọn điểm rất hợp lý) nhưng đoạn C bị kéo tới 08:39, gần như trùm cả cú sụp. Ranh giới Phase C nên kết thúc ngay tại cây phá 08:18, và Phase D bắt đầu từ đó.

## Đạt
- L1: MOVE giảm 46.2 giá / 107 nến, hiệu suất 0.41 — move thật rõ, climax chặn đúng.
- Nhãn SC neo đúng cây: 19:15, VSA **2.94x**, thân 0.82, nến đỏ — đúng màu, đúng vai.
- AR 19:55 VSA 3.74x — cú bật ngược có nỗ lực thật, không phải râu nhiễu.
- L9: Phase B 638/878 nến — dài nhất, đúng.
- L4: origin SC (move giảm) + phá xuống thật = **Tái phân phối** — tên đúng, đây là ca mà bản cũ hay xoá oan.
- L10: LPSY[D] 08:48 tại 4087.0 hồi lên đúng mép rồi giữ ngoài biên, Phase E 121 nến giá tìm vùng giá mới ở 4055–4065 — CBR đầy đủ.
- Chú thích er=0.90 "nhịp HIỆU QUẢ" đúng dấu; SOT dưới n=3 với tỷ lệ volume 0.13 đọc là "cạn kiệt" — đúng.
