# Chấm bài #46 — Tái phân phối (RE-DIST) · 2026-07-14 16:07 → 19:55 (228 nến M1)

**Điểm: 3/10** — Biên chính vẽ hẹp hơn một nửa vùng dao động thật, bỏ sót hẳn một cú Shakeout 13 giá, và SOW được cấp bằng oan vì biên phụ tính sai. Không nên vẽ range với hai biên này.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới KHÔNG phải cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới = 4061.8 (mSOW 17:14).
- **Đúng phải là:** khoảng 4049.5 — đáy cú sụp 18:29→18:33. Đó là mức cực trị xa nhất mà phe bán tạo được, đúng định nghĩa biên phụ.
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ dài ở 18:31 xuyên xuống tới ~4049.8, thấp hơn nét đứt 4061.8 tới **12 giá** — nhìn thấy ngay trên ảnh, nét đứt nằm cao hơn hẳn đáy đó. Trên panel volume, đúng cây đó là cột vàng cao nhất cả range.
- **Nghi phạm trong thuật toán:** cú phá 18:31 không được xử lý qua nhánh "theo dõi cú phá biên" nên không sinh nhãn và không nới biên phụ. Nghi vấn: cú này bị chặn bởi guard "mỗi range chỉ MỘT cú rũ" / "cú thăm dò mới nông hơn thì không ghi gì", hoặc bị hạ cấp vì đã có mSOW trước đó và nhánh so sánh dùng nhãn thay vì độ sâu.

### 2. Bỏ sót hẳn cú Shakeout / mất luôn Phase C — luật vi phạm: L5, L8
- **Thuật toán gắn:** không nhãn nào ở 18:31; timeline A → B → D → E, **không có Phase C**.
- **Đúng phải là:** cú 18:29→18:37 phá biên chính dưới 4063.4 tới 4049.8, lùng bùng ngoài range ~8 nến rồi rút hẳn vào trong = **Shakeout** (L5: ngoài range > 4 nến). Đó chính là Phase C của range này.
- **Dấu hiệu quyết định trên chart:** giá rời biên rồi quay lại đóng cửa trên 4063 trong vòng dưới 15 nến, kèm cột volume cao nhất range — mẫu rũ kinh điển.
- **Nghi phạm trong thuật toán:** cùng nhánh với lỗi 1. Thêm nữa: cơ chế "gán ngược Phase C khi có SOS/SOW mà range chưa từng có C" (spec mục 6, case khó) **không kích hoạt** — range có SOW 19:30 mà vẫn không có dải C nào. Nhánh gán ngược đang bị bỏ qua.

### 3. SOW được cấp bằng oan — luật vi phạm: L3 ("SOS/SOW phải đóng cửa bứt qua biên PHỤ")
- **Thuật toán gắn:** SOW 19:30 tại 4055.6 (VSA 5.87x, thân 0.87), rồi Phase D/E, đặt tên RE-DIST.
- **Đúng phải là:** với biên phụ đúng ở 4049.5, cú 19:30 đóng ở 4055.6 **chưa bứt qua biên phụ** → chỉ là mSOW, range chưa được đặt tên.
- **Dấu hiệu quyết định trên chart:** đáy 19:30 nông hơn đáy 18:31 gần 6 giá; sau đó giá hồi lên 4062 rồi tới 20:39 vẫn chỉ 4056 — không hề đi tìm vùng giá mới. Chiều cao biên chính 8.9 giá mà "Phase E" chỉ đi thêm vài giá thì chưa đạt đích 1.0× chiều cao.
- **Nghi phạm trong thuật toán:** điều kiện phá thật đo với biên phụ **hiện có** (4061.8) — biên phụ sai làm ngưỡng tụt xuống, kéo theo tên range sai.

### 4. Biên chính 8.9 giá quá hẹp so với vùng dao động thật — luật vi phạm: L3 + mục 1 tiêu chí (range thật hay nhiễu)
- **Thuật toán gắn:** biên chính 4063.4–4072.3 = 8.9 giá (0.22% giá).
- **Đúng phải là:** vùng đấu giá thật trên chart là ~4049 → 4072 (23 giá). Biên chính chỉ bao được **38%** vùng đó, nên gần như mọi nhịp trong Phase B đều "thò ra ngoài biên" — biên mất chức năng phân định.
- **Dấu hiệu quyết định trên chart:** hai đường cam nằm sát nhau ở nửa trên chart, phần lớn nến Phase B nằm dưới đường cam dưới.
- **Nghi phạm trong thuật toán:** AR được chốt bằng swing pivot đầu tiên (5 nến + sàn 1.5× biên độ TB) nên bắt đúng cú bật 9 giá đầu ở 16:16 rồi khoá luôn. Không có kiểm tra hậu nghiệm kiểu "nếu biên phụ/biên chính vượt X thì AR chọn sai pivot" — guard hiện tại chỉ bắn ở 4.0x, quá lỏng.

### 5. Phase E dài đúng 1 nến — luật vi phạm: L10 (lỗi J của v5 tái xuất)
- **Thuật toán gắn:** Phase E = 19:55 → 19:55 = 1 nến.
- **Đúng phải là:** Phase E là đoạn giá rời range đi tìm vùng giá mới; 1 nến không phải một phase. Ở bài này thực tế giá **không** rời range (20:00–20:39 vẫn quanh 4056–4062) → đúng hơn là **không có Phase E**, cú phá bị vô hiệu.
- **Nghi phạm trong thuật toán:** lỗi J được vá bằng "kéo Phase E tới khi đi xa 2× chiều cao / lùi vào biên / 120 nến", nhưng chiều cao range chỉ 8.9 giá nên điều kiện "lùi hẳn vào trong biên (30 tick = 3 giá)" bắn ngay nến kế tiếp. Ngưỡng tuyệt đối 30 tick không tương thích với range siêu hẹp.

### 6. Chú thích chỉ số nỗ lực/kết quả in NGƯỢC nghĩa — lỗi đo, không phải lỗi lọc
- **Thuật toán in:** "effort(VSA TB)=0.54x, result=1.42, tỷ lệ er=0.38 — vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** effort 0.54x là volume **thấp**, result 1.42 là biên độ **lớn** → đây là "nỗ lực ít, kết quả nhiều", tức nguồn cung nổi đã cạn (THEORY §6.3), hoàn toàn trái với câu chú thích.
- **Dấu hiệu quyết định:** so với bài #45 (er=36.67, đúng nghĩa "volume nhiều kết quả ít") và bài #48 (er=0.27, cũng bị in cùng câu) → câu diễn giải được in **bất kể** giá trị er.
- **Nghi phạm trong thuật toán:** chuỗi mô tả hard-code, thiếu nhánh `if er < 1 → "nỗ lực ít, kết quả nhiều"`. Chỉ số tự nó đo đúng, chỉ nhãn diễn giải sai.

## Đạt
- **Mục 1:** climax mang nhãn `SC?` + ghi rõ "SINH TỪ CHÍNH MỘT CÚ PHÁ, không có cao trào thực sự" — cơ chế mới, trung thực, không giả vờ có climax. Đây là điểm tiến bộ so với các vòng trước.
- **Mục 2 (ST[A]):** ST[A] 16:23 tại 4064.9, cách mức climax 4063.4 đúng 1.5 giá — test lại vùng climax rất chuẩn, Phase A kết thúc đúng tại đó. Đủ 3 lần đổi hướng.
- **Mục 4 (tên):** move trước là giảm (4092 → 4063), climax SC, phá xuống → **Tái phân phối**, khớp bảng L4. Tên đúng (dù cú phá phía sau chưa đủ tư cách).
- **Mục 5:** Phase B 186 nến = phase dài nhất, đúng L9.
- **Chỉ số bias=+0** (test cả hai biên) khớp đúng hình: có mSOW dưới và nhiều lần chạm 4072 trên.

## Cần hỏi người học
- Khi một range mới sinh từ đúng cây SOW của range trước (đây chính là SOW 16:07 của bài #45), có nên yêu cầu AR của range mới phải lớn hơn một tỷ lệ nào đó của chiều cao range cũ không? Biên chính 8.9 giá ngay dưới một range 36.3 giá trông giống nhịp retest hơn là một vùng đấu giá độc lập.
