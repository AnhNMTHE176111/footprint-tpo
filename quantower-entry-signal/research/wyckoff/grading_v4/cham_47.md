# Chấm bài #47 — Tái phân phối (RE-DIST) · 2026-07-24 00:14 → 02:50 (156 nến M1)

**Điểm: 4/10** — Có một cái hộp thật và một cú phá thật, nhưng **chọn sai cây climax** (cây 01:04 mới là cao trào bán), và Phase D/E mỗi cái 1 nến là nhãn hình thức, không phải phase.

## Lỗi (nặng → nhẹ)

### 1. Chọn sai cây climax — cây ST[A] có nỗ lực lớn hơn cây SC — luật vi phạm: mục 8 (Effort vs Result), THEORY §3.3
- **Thuật toán gắn:** SC tại 00:14 @4043.2, VSA 4.83x, biên độ nến **2.4 giá**; rồi ST[A] tại 01:04 @4041.9, **VSA 6.69x**.
- **Đúng phải là:** cây 01:04 là cao trào bán. THEORY §3.3 nói rõ ST là cú test mà "spread/volume thường **giảm** khi giá quay lại tiệm cận SC" — ở đây ngược lại, nỗ lực ở ST[A] **lớn hơn 38%** so với cây được gọi là climax. Đọc lại cả cấu trúc: nhịp lùi nhẹ → cây 00:14 (nhỏ) → hồi lên 4053.3 → **cây 01:00–01:04 đổ mạnh về 4041.9 với volume lớn nhất nửa đầu chart**. Đó mới là "chênh lệch biên độ mở rộng + khối lượng tăng mạnh" theo định nghĩa gốc của SC. Range đúng nên mở từ 01:04, biên 4041.9–4054.1, AR = đỉnh ~4054 lúc 01:44, ST[A] = cụm đáy 02:06–02:15. Đây đúng ca chữa Ca #12 nguồn 7.pdf (nhầm thứ tự climax/AR/ST làm sai cả chuỗi phase phía sau).
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, thanh vàng cao nhất của nửa đầu range nằm đúng ở ~01:00, không nằm ở 00:14.
- **Nghi phạm trong thuật toán:** máy quét từ nến cũ tới mới và **chốt cây climax đầu tiên thoả ngưỡng** (mục 3), không so lại với các cây mạnh hơn xuất hiện sau trong Phase A. Ngưỡng 2.2x + 1.4× biên độ dễ bị một cây tầm thường "chộp" trước.

### 2. Climax 2.4 giá / MOVE 10.6 giá — cỡ nhiễu phiên Á, không có sàn tuyệt đối — luật vi phạm: L1 (về mặt cơ chế)
- **Thuật toán gắn:** MOVE trước climax dài 10.6 giá / 39 nến, hiệu suất 0.41 → coi là "MOVE xu hướng rõ ràng".
- **Đúng phải là:** L1 đòi một MOVE xu hướng **bị chặn lại**. Ở đây MOVE (10.6 giá) **đúng bằng chiều cao range sau đó** (10.9 giá) — nghĩa là cây climax không chặn xu hướng nào, nó chỉ kết thúc một nhịp lùi cùng cỡ với vùng lình xình theo sau. Kèm bối cảnh: 00:14–02:50 UTC là phiên Á, volume 11–67 lot/nến (đọc từ bảng 12 nến quanh climax).
- **Dấu hiệu quyết định trên chart:** biên chính 10.9 giá = **0.27% giá**; cây climax biên độ 2.4 giá với 145 lot. Trên vàng đó không phải "bán tháo hoảng loạn".
- **Nghi phạm trong thuật toán:** mọi ngưỡng climax đều **tương đối** với TB 20 nến, không có sàn tuyệt đối (theo tick/ATR ngày). Đúng như mục 12.1 của tài liệu thuật toán đã tự nghi: "quá lỏng ở phiên Á".

### 3. Phase D = 1 nến, Phase E = 1 nến — CBR không tồn tại — luật vi phạm: L10
- **Thuật toán gắn:** SOW 02:49 @4028.8 → Phase D (1 nến) → Phase E (1 nến), range đóng.
- **Đúng phải là:** L10 định nghĩa Phase D+E = phá biên → **hồi về retest nhưng giữ được ở ngoài** → đi tiếp. Ở đây không có nhịp hồi nào, không có LPSY[D]. Một phase dài 1 nến thì không phải phase — nên để range đóng ngay tại cây phá và **không gán D/E**. (Nhịp hồi thật xuất hiện ở 03:12–03:34 lên vùng 4034–4036, tức **sau** khi range đã đóng.)
- **Dấu hiệu quyết định trên chart:** cú phá là **một cây đỏ duy nhất** 02:47–02:49 đi thẳng từ ~4042 xuống ~4028; nhãn SOW được đặt tại **đáy** cây đó (4028.8), tức 14.4 giá **dưới** biên chính 4043.2 — không phải điểm phá biên.
- **Nghi phạm trong thuật toán:** cùng gốc với bài #46 — nhãn SOS/SOW đóng dấu ở nến xác nhận thứ 3 (mục 5.1) nên trễ, và cửa sổ Phase D 25 nến (mục 7) bị cắt sớm vì đích Phase E "0.5 × chiều cao range" quá dễ đạt khi range chỉ cao 10.9 giá — giá rơi 14 giá trong 1 nến là đã vượt đích.

### 4. Nhãn AR lệch biên chính 0.8 giá — luật vi phạm: L3 (nhẹ)
- **Thuật toán gắn:** AR @4053.3 nhưng biên chính trên 4054.1.
- **Đúng phải là:** trùng nhau. Lệch 0.8 giá (7% chiều cao range) — cùng nguyên nhân code với lỗi #4 của bài #46 (dời biên khi AR bị vượt mà không dời nhãn), ở đây mức độ nhỏ.

## Đạt
- **LPSY[C] gắn đúng vai:** @4051.0 = 72% chiều cao biên chính, sát biên trên, ngay trước cú sụp — đúng khuôn "nhịp hồi yếu cuối cùng trước khi cấu trúc sụp" (THEORY §4.1 LPSY; đối chiếu Ca #4 nguồn 4.pdf). Phase C gán ngược (case khó, L8) ở đây cho kết quả hợp lý.
- L9: Phase B (83 nến) dài nhất trong ba phase thật A/B/C.
- L4: origin SC + phá xuống thật = Tái phân phối, đúng.
- L3: ST[A] @4041.9 vượt xuống dưới mức climax và tạo biên phụ dưới 4041.9 — đúng luật biên phụ, mỗi bên 1 cái.
- L7: LPSY[C] một điểm duy nhất.

## Cần hỏi người học
- Có nên đặt **sàn tuyệt đối** cho cây climax và cho chiều cao range (ví dụ biên độ nến climax ≥ x% ATR ngày, chiều cao biên chính ≥ y giá) để chặn range cỡ nhiễu phiên Á không? L1 chỉ nói "MOVE rõ ràng" mà không cho số, nên hiện không có luật nào loại được ca này.
