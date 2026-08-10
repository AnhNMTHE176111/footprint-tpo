# Chấm bài #50 — Tích lũy (ACC) · 2026-07-20 12:02 → 2026-07-21 01:16 (732 nến M1)

**Điểm: 5/10** — khung range và tên range đúng, nhưng **hai biên chính đặt sai chỗ** (nằm gọn trong nửa trên vùng đấu giá) nên kéo theo hỏng cả chuỗi nhãn giữa range: cú rũ đáy thật bị gọi thành mSOW và Phase C bị đẩy tới sát SOS. Sửa nhãn + sửa mức AR, giữ range.

## Lỗi (nặng → nhẹ)

### 1. Biên chính không mô tả vùng đấu giá — AR chốt sau đúng 4 nến — luật vi phạm: L3 (biên chính = climax + AR, phải là hai biên "quan trọng nhất")
- **Thuật toán gắn:** biên chính 4016.5 – 4021.9 = **5.4 giá (0.13%)**; biên phụ 4003.3 – 4023.9 = **20.6 giá**. Tỷ lệ biên phụ/biên chính **3.81×**, sát ngưỡng guard 4.0× nên guard không bắn.
- **Đúng phải là:** vùng cân bằng thật của 732 nến này là **4003 – 4024**. AR phải là cú bật ngược *thật* — trên ảnh, sau SC giá bật lên 4021.9 rồi lập tức lăn xuống 4003; nhịp 4 nến 12:02→12:06 chỉ là râu hồi kỹ thuật. Đúng ra AR phải chốt tại đỉnh 4023.9 (mức mà 673 nến Phase B liên tục chạm rồi dội), và biên dưới lấy 4003.3.
- **Dấu hiệu quyết định trên chart:** AR ở 12:06 có VSA **0.69×** (dưới trung bình) — chính là ca "AR (yếu)" mà spec mục 4.1 tự cảnh báo. Chiều cao 5.4 giá mà Phase B dao động trong dải 20.6 giá: biên chính chỉ chiếm **26%** dải giá thật. Mọi phép đo phái sinh (15% chiều cao = 0.8 giá) trở nên vô nghĩa.
- **Nghi phạm trong thuật toán:** nhánh tìm AR ở mục 4.1 — "swing pivot đầu tiên xác nhận 5 nến + sàn 1.5× ATR". Ở giờ tin (12:00 UTC) ATR đang phình vì chính cây climax, nên sàn chống nhiễu quá thấp và pivot 4 nến được nhận. Cần thêm điều kiện: nếu sau khi ST[A] chốt mà biên phụ vượt biên chính quá ~2×, phải **dời AR** tới cực trị mới thay vì chỉ nới biên phụ (guard 4.0× hiện chỉ xoá range, không sửa biên).

### 2. Cú rũ đáy bị hạ thành mSOW → Phase C gán ngược sai chỗ — luật vi phạm: L5, L8, và bảng 5.1 của chính spec
- **Thuật toán gắn:** `mSOW` tại 22:55 @4003.3 (Phase B), rồi Phase C chỉ dài **5 nến** với `LPS[C]` @4018.6 lúc 00:31 (gán ngược từ SOS).
- **Đúng phải là:** cú 22:31–23:00 thủng xuống 4003.3 rồi lùng bùng ngoài một lúc mới thu về, sau đó giá đi một mạch lên phá biên → theo L5 đây là **Shakeout** (SOW thất bại), tức **cú rũ của Phase C**, và Phase C phải bắt đầu từ đó. LPS[C] 00:31 giữ được, nhưng là *test sau shakeout*, không phải điểm mở Phase C.
- **Dấu hiệu quyết định trên chart:** 4003.3 là **đáy sâu nhất của cả range**, thủng biên chính dưới 13.2 giá = 2.4× chiều cao biên chính, VSA 1.57×; và toàn bộ diễn biến sau nó là đi lên tới 4040 — đúng nghĩa "một phe vừa thua". Đây là case DỄ, không phải case khó, nên không được dùng nhánh gán ngược.
- **Nghi phạm trong thuật toán:** điều kiện "cú rũ phải **vượt biên phụ** đã có" (lỗi G, mục 5.1 câu 1). Tại 22:55 biên phụ dưới đang là 4012.8 do chính ST[A] tạo, cú này vượt xa — nên đúng ra phải đủ tư cách. Nghi ngờ thứ tự đánh giá: máy nới biên phụ **trước** khi xét tư cách rũ, nên cú tự so với chính mình rồi rớt xuống mSOW.

### 3. ST[A] thủng dưới mức climax — luật vi phạm: L2 ("ST[A] là test lại vùng climax")
- **Thuật toán gắn:** `ST[A]` @4012.8, tức **dưới** mức climax 4016.5 3.7 giá.
- **Đúng phải là:** ST[A] phải bị chặn **tại hoặc trên** vùng climax; ở đây nó tạo đáy mới → không còn là test.
- **Dấu hiệu quyết định trên chart:** 3.7 giá thủng = **68% chiều cao biên chính**; nến ST[A] có VSA 3.83× và thân chỉ 0.23 — cây hấp thụ mạnh, không phải nến test volume co lại như định nghĩa ST (THEORY §3.3).
- **Nghi phạm trong thuật toán:** trần "ST[A] vượt climax ≤ 1.0× chiều cao range" (v5, lỗi D). Trần này tự vô hiệu khi range đo được quá hẹp: 1.0 × 5.4 = 5.4 giá, thủng 3.7 giá vẫn lọt. Nên đổi trần sang **× ATR** hoặc gộp với điều kiện #1.

### 4. Chỉ số nỗ lực/kết quả lấy nhịp nằm ngoài Phase B — lỗi trình bày/nhất quán
- **Thuật toán gắn:** "Nhịp nỗ lực/kết quả cao nhất **trong Phase B**" ghi kết thúc tại 2026-07-21 **00:31**, trong khi bảng phase ghi Phase B kết thúc **00:30** và 00:31 là nến mở Phase C.
- **Đúng phải là:** cửa sổ đo phải kẹp trong đúng dải Phase B.
- **Nghi phạm trong thuật toán:** off-by-one khi lấy `phaseB_end` (dùng index nến bắt đầu Phase C).

## Đạt
- **Mở range (L1):** MOVE giảm 22.9 giá / 28 nến / hiệu suất 0.67, climax là đáy thấp nhất cửa sổ, VSA 4.88× — điều kiện CẦN + ĐỦ đều thật, không phải nổ volume giữa vùng đi ngang.
- **Tên range (L4):** SC + phá lên = Tích lũy, khớp đúng hướng phá thật trên chart (4024 → 4040).
- **Tỷ lệ phase:** B 673 nến dài nhất (L9), C 5 nến ngắn nhất (L8) — đúng thứ tự, dù mốc C sai chỗ.
- **Phase D/E (L10):** SOS @4023.9 đóng cửa bứt qua **biên phụ**, LPS[D] @4025.8 hồi về nhưng giữ được bên ngoài, Phase E 28 nến giá đi tới 4040 — CBR hoàn chỉnh, đúng tinh thần L10.
- **UT[B] @4023.0:** thò trên biên chính mà chưa qua biên phụ 4023.9 → giữ ở Phase B là đúng, không bị gọi UTAD (không mắc lỗi kinh điển Ca #1 nguồn 4.pdf).
- **Chỉ số Phase B (v6) đo đúng bản chất:** SOT phía dưới n=4, thrust cuối/đầu 0.57 nhưng volume nhịp cuối/đầu **1.55×** → đọc thành "hấp thụ, đang giữ vùng"; SOT phía trên volume 0.35× → "cạn kiệt". Hai con số này nói trước rằng phe mua đang đỡ đáy và cú phá sẽ đi **lên** — đúng kết cục. Đây là phần làm tốt nhất của bài.
- Bias `+0` (test cả hai biên) khớp hình: giá chạm cả 4003 và 4024.
