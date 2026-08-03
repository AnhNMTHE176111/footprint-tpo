# Chấm bài #28 — Tái phân phối (RE-DIST) · 2026-06-23 00:22 → 02:15 (113 nến M1)

**Điểm: 3/10** — cú SOW **thật** đã xảy ra ở 01:16–01:20 và bị thuật toán gọi là "Shakeout (thất bại)"; nhãn SOW thật thì dán muộn 30 nến, lên một nến **tăng** không có volume, khi đợt bán đã hết. Phase D/E vì thế mất hết ý nghĩa. Thêm nữa AR neo vào đỉnh một cây râu và nhãn LPS[C] sai vai trong cấu trúc phân phối.

## Lỗi (nặng → nhẹ)

### 1. Cú phá vỡ THẬT bị gọi là "Shakeout (thất bại)" — luật vi phạm: L5 + mục 8 THEORY
- **Thuật toán gắn:** Shakeout (thất bại) tại 01:21 giá 4188.0 → lùi về Phase B.
- **Đúng phải là:** **SOW thật, Phase D bắt đầu từ 01:17**. Đây là "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài" — đúng định nghĩa phá THẬT trong L5, không phải shakeout.
- **Dấu hiệu quyết định trên chart:** **năm nến đóng cửa liên tiếp dưới** biên chính 4196.0, mỗi nến một mức thấp hơn: 01:16 C=4199.5 (VSA 2.85×) · 01:17 C=**4194.3** (2.54×) · 01:18 C=4192.0 (1.58×) · 01:19 C=4190.6 (1.52×) · 01:20 C=4188.4 (1.75×) — 8 giá trong 5 nến, volume trên trung bình suốt cả đoạn. Sau đó giá **không** lấy lại được biên: nhịp hồi cao nhất chỉ tới 4198.3 (01:27) rồi rơi tiếp.
- **Nghi phạm trong thuật toán:** điều kiện "3 nến liên tiếp thân ≥ 45%" (`SOS_BODY_MIN`). Nến 01:19 có thân = 1.3/3.2 = **0.41** → đứt chuỗi, cả cú phá bị loại. Ngưỡng thân áp cho **từng nến trong chuỗi** là quá cứng: một cú bán đúng nghĩa vẫn có nến thân 0.41 xen giữa. Nên đo thân **của cả đoạn** (tổng dịch chuyển close/tổng biên độ) hoặc chỉ đòi thân lớn ở nến đầu chuỗi.

### 2. SOW dán muộn 30 nến, lên nến TĂNG volume dưới trung bình — luật vi phạm: mục 8 THEORY (Effort vs Result)
- **Thuật toán gắn:** SOW tại 01:50, giá 4170.2, VSA **0.74×**.
- **Đúng phải là:** cây SOW quyết định là **01:37** — volume **713 = 5.63×**, giá đi từ 4184.9 xuống 4178.1 (thanh volume vàng cao nhất toàn chart); kèm cây 01:36 (313 = 3.12×).
- **Dấu hiệu quyết định trên chart:** nến 01:50 có O=4168.0 → C=4170.2, tức là **nến xanh hồi lên**; ngay sau nhãn đó giá bật ngược 10.7 giá (lên 4180.9 tại 01:59). Nhãn "dấu hiệu yếu kém" nằm đúng chỗ đợt yếu kém kết thúc.
- **Nghi phạm trong thuật toán:** cùng nguyên nhân lỗi 1 — nhãn được gắn tại nến thoả cuối cùng của chuỗi xác nhận, nên nó luôn trễ và không bao giờ trùng cây nỗ lực lớn nhất. Nên gắn nhãn **hồi tố** vào nến có VSA cao nhất trong đoạn phá vỡ.

### 3. Phase D/E khai sinh sau khi đợt bán đã xong — luật vi phạm: L10
- **Thuật toán gắn:** D = 01:50 → 02:14 (25 nến), E = 02:15 (1 nến).
- **Đúng phải là:** D từ 01:17, E khi giá đi đủ 1× chiều cao range (4196 − 20 = 4176, đạt lúc 01:42). Toàn bộ CBR đã diễn ra **trước** khi nhãn D xuất hiện.
- **Dấu hiệu quyết định trên chart:** ở nến được gán Phase E (02:15) giá đóng 4173.9 — **cao hơn** chính điểm gọi là SOW (4170.2) 3.7 giá, và đang trong nhịp hồi. Không có nhịp "retest giữ được ngoài biên" nào được đánh dấu (thiếu hẳn LPSY[D]) vì cửa sổ 25 nến sau SOW rơi vào đoạn giá đã đi ngang.

### 4. Nhãn LPS[C] sai vai trong cấu trúc tái phân phối — luật vi phạm: mục 4.1 THEORY (LPSY) + Ca #8 nguồn 7.pdf (gộp nhãn khác ngữ cảnh phase)
- **Thuật toán gắn:** **LPS[C]** tại 01:32, giá 4190.0 — đặt tại một **đáy**.
- **Đúng phải là:** **LPSY[C]** — và đặt tại **đỉnh nhịp hồi 4198.3 (01:27)**, tức lần bật lên yếu test lại biên đã mất từ bên dưới. Trong họ phân phối, "điểm cung cuối cùng" là một đỉnh hồi yếu, không phải một đáy.
- **Dấu hiệu quyết định trên chart:** tiêu đề chart ghi rõ "Tái phân phối (RE-DIST)" mà nhãn lại là LPS[C] — bài #26 và #30 cùng loại RE-DIST đều dùng LPSY[C]. Không đồng bộ trong chính lô bài.
- **Nghi phạm trong thuật toán:** dòng 551 — `'LPS[C]' if up else 'LPSY[C]'` chọn tên theo **hướng kỳ vọng của cú rũ** (shakeout ở biên dưới ⇒ up=True ⇒ LPS). Khi range chốt tên là RE-DIST thì nhãn **không được đặt lại**. Phải đổi tên nhãn theo `r.dir` lúc đóng range.

### 5. AR neo vào đỉnh một cây râu, làm biên trên phình 2.8 giá — luật vi phạm: L3 + Ca #5 nguồn 4.pdf (neo giá đóng cửa)
- **Thuật toán gắn:** AR tại 01:00, giá 4216.0 → biên chính trên = 4216.0.
- **Đúng phải là:** cú bật ngược thật kết thúc quanh **4211.8–4213.2** (đỉnh 01:08 / close cao nhất 01:02).
- **Dấu hiệu quyết định trên chart:** nến 01:00 có O=4210.6, H=4216.0, **C=4210.2 < O**, thân chỉ **0.06**, volume 215 (5.23×) — một cây râu nhọn, nỗ lực lớn mà kết quả bằng 0 (đúng dấu hiệu đảo chiều theo mục 8), rồi biên trên của cả range lại neo vào đỉnh râu đó.
- Đây là một cây **thăm dò trên đỉnh** (nỗ lực lớn, kết quả 0) nằm ở **cuối** một range tái phân phối trong giờ Á mỏng — thuật toán không đọc nó, chỉ lấy mức giá của nó làm biên.

### 6. Phase A = 45 nến > tổng Phase B = 30 nến — luật vi phạm: L9
- A=45 · B=14+16=30 · C=13 · D=25 · E=1. Cùng lỗi hệ thống của lô: Phase A không thể ngắn hơn `AR_LOOKBACK + 1 = 41` nến.

## Đạt
- **Mục 4 (L4):** tên range đúng — origin SC + phá xuống = **Tái phân phối**; không xoá range vì "phá sai hướng".
- **Mục 3 (một phần):** biên chính cố định sau Phase A, không bị kéo theo giá; biên phụ dưới 4185.6 đúng là cực trị xa nhất, mỗi bên tối đa 1.
- **Mục 6 (một phần):** cho phép Phase C **lùi về Phase B** khi cú rũ thất bại (đúng tinh thần THEORY §9 "cấu trúc thất bại") — cơ chế đúng, chỉ áp sai ca này.
- **L7:** LPS/LPSY chỉ đánh 1 điểm, không vẽ vùng.

## Cần hỏi người học
- Với cú 01:16–01:20 (5 close liên tiếp dưới biên, 8 giá, volume 1.5–2.9×) nhưng có **một** nến thân 0.41 xen giữa: anh muốn tính là **phá thật** (nới điều kiện thân) hay vẫn coi là shakeout? Câu trả lời quyết định nên sửa `SOS_BODY_MIN` theo từng nến hay theo cả đoạn.
