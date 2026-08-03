# Chấm bài #15 — Tích luỹ (ACC) · 2026-05-26 08:29 → 10:28 (118 nến M1)

**Điểm: 5/10** — Chuỗi sự kiện đọc đúng khuôn Wyckoff (đây là bài duy nhất trong lô có Shakeout đúng đáy TR + LPS[D] retest thật), nhưng biên chính chỉ cao **6.6 giá** nên cái gọi là "range" nhỏ hơn cả cú rũ của chính nó — về bản chất vẫn không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Biên chính cao 6.6 giá — nhỏ hơn cú rũ 8.7 giá mà nó phải chứa — luật vi phạm: L3 (biên chính là 2 biên quan trọng nhất) + tinh thần "TR = vùng cân bằng"
- **Thuật toán gắn:** biên chính 4554.1 – 4560.7 = **6.6 giá (0.14% giá)**. Đây là range hẹp nhất trong toàn bộ 49 range (trung vị 21.6 giá).
- **Đúng phải là:** một biên chỉ 6.6 giá trên vàng M1 là độ dày của **một nến bình thường** (biên độ nến climax đã là 3.7 giá). Hệ quả đo được: giá đóng cửa **dưới** biên chính dưới suốt **31 nến liên tiếp** (09:23 → 10:05), tức **26% toàn bộ range** nằm ngoài biên, và cú rũ xuống 4545.4 sâu **8.7 giá** — lớn hơn cả chiều cao biên chính. Khi đó biên chính không còn phân định được "trong/ngoài range".
- **Dấu hiệu quyết định trên chart:** hai đường liền cam nằm sát nhau ở giữa chart, còn phần lớn hành động giá của Phase B–C diễn ra bên dưới đường liền dưới.
- **Nghi phạm trong thuật toán:** AR chỉ cần hồi **≥30% độ dài move** (mục 4.1). Move ở đây chỉ 18.9 giá nên 30% = 5.7 giá — quá dễ đạt. Cần thêm sàn tuyệt đối cho chiều cao biên chính (ví dụ ≥ 1.5× biên độ trung bình 20 nến, hoặc ≥ 10 giá với vàng), tương ứng với guard trần 3.5% đã có ở đầu kia.

### 2. AR là một nến doji — luật vi phạm: THEORY §3.3 (AR = sóng mua đẩy giá lên) + mục 8
- **Thuật toán gắn:** AR 4560.7 (08:46), **VSA 1.02x, brat 0.00** (O4559.7 H4560.7 L4559.2 C4559.7).
- **Đúng phải là:** AR phải là một sóng bật có lực. Nến này khối lượng đúng bằng trung bình, thân bằng 0 — nó chỉ là cái râu cao nhất của một đoạn đi ngang 17 nến. Máy có nhãn cảnh báo "AR (yếu)" nhưng chỉ bắn khi AR nằm sát climax 1–2 nến, nên ca này lọt.
- **Nghi phạm trong thuật toán:** điều kiện AR chỉ đo **khoảng cách giá**, không đo nỗ lực. Nên thêm: nến AR phải có `brat` hoặc VSA vượt ngưỡng, hoặc lấy cực trị của một cụm nến có volume thay vì một nến đơn.

### 3. Điểm Shakeout đặt trên nến 0.91x, không phải cây nỗ lực — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** Shakeout tại 4545.4 (09:44), **VSA 0.91x**.
- **Đúng phải là:** cây bán thật là **09:42** (VSA **2.48x**, 78 lot, biên độ 3.5, đáy 4545.8) — chỉ cách nhau 2 nến và cao hơn đúng **0.4 giá**. Nhãn nên nằm trên cây 09:42. Xa hơn nữa, cây khởi động cả đợt rũ là **09:17 (VSA 7.73x, 182 lot)** — thanh volume cao nhất chart — mà máy không gắn nhãn gì cả.
- **Dấu hiệu quyết định trên chart:** thanh vàng cao vượt trội tại 09:17 (ngay đầu Phase B) không có nhãn nào; nhãn Shakeout thì nằm trên một nến volume tầm thường.
- **Nghi phạm trong thuật toán:** điểm rũ lấy theo `argmin(low)` thuần. Nên chọn nến VSA cao nhất trong cụm ±3 nến quanh cực trị (cùng một vá với bài #13 lỗi 2).

### 4. Phase A dài nhất, Phase B chỉ 27 nến — luật vi phạm: L9
- **Thuật toán gắn:** A 47n · B 27n · C 28n · D 16n · E 1n.
- **Đúng phải là:** Phase B phải dài nhất. Ở đây A dài hơn B **74%**, và B (27n) còn ngắn hơn C (28n) — vi phạm cả L8 lẫn L9 cùng lúc, dù chỉ lệch 1 nến.
- **Nghi phạm trong thuật toán:** Phase A ngốn 47 nến vì phải chờ "5 nến không tạo cực trị mới" để chốt ST[A]; trên một range chỉ cao 6.6 giá thì tiêu chí đó rất khó thoả nhanh.

### 5. Phase E chỉ 1 nến rồi giá quay hẳn vào trong range — luật vi phạm: L10 (Phase E = giá đi tìm vùng giá mới)
- **Thuật toán gắn:** Phase E = 1 nến (10:28), range đóng.
- **Đúng phải là:** 60 nến sau đó giá lên cao nhất 4573.7 nhưng **đóng cửa lại ở 4556.8** — tức về **dưới** cả biên chính trên 4560.7 và gần như về đúng vùng climax. Cú phá cho ~13 giá rồi trả hết. Máy chốt Phase E theo mốc "đi thêm ≥50% chiều cao range khi hết 25 nến"; vì chiều cao range chỉ 6.6 giá nên mốc đó là **3.3 giá** — quá dễ, nên Phase E được công nhận cho một cú phá thực chất thất bại.
- **Nghi phạm trong thuật toán:** đích Phase E neo theo chiều cao biên chính (mục 7). Range càng nhỏ thì đích càng dễ → tự thoả. Nên neo đích theo `max(1.0 × chiều cao range, k × ATR20)`.

## Đạt
- **Shakeout gán đúng nhất trong cả lô:** 4545.4 là **mức thấp nhất của toàn TR** — thoả đúng tiêu chí tường minh nhất của giảng viên trong CHART_CASES (2.pdf lỗi #6: Spring/Shakeout bắt buộc phải là đáy thấp nhất của TR). Bài #11 sai đúng chỗ này, bài #15 làm đúng.
- **Phân loại Spring ↔ Shakeout đúng theo L5:** giá đóng cửa dưới biên chính dưới suốt 31 nến liên tiếp — lùng bùng ngoài rất lâu, đúng là Shakeout (một SOW thất bại), không phải Spring.
- **Phase D/E đúng khuôn CBR (L10):** SOS 10:12 (VSA 2.00x, thân 0.83, đóng 4563.6 trên biên chính trên) → LPS[D] 10:19 hồi về **đúng 4560.7 = biên vừa phá** với VSA 0.31x (cạn cung) → giá đi tiếp. Đây là mẫu retest-giữ-biên sạch nhất trong 5 bài.
- LPS[D] chỉ 1 điểm, đúng L7. Không có nhãn nào bị spam.
- Phase A đủ 3 lần đổi hướng và kết thúc đúng tại ST[A] (L2); ST[A] 4551.5 phá xuống dưới climax nên sinh biên phụ — xử lý đúng L3.
- Tên range đúng L4 (SC + phá lên = Tích luỹ), và ở đây hướng phá cũng khớp diễn biến ngay sau đó (khác bài #12/#14).
- **Biên phụ ghi đúng cả hai bên:** dưới 4545.4 = đáy TR, trên 4563.6 = đỉnh SOS. Đây là bài duy nhất trong lô không sai L3.

## Cần hỏi người học
- Với range chỉ cao 6.6 giá nhưng chuỗi sự kiện lại chuẩn (Shakeout đúng đáy + LPS[D] retest thật), anh muốn máy **loại thẳng** bằng sàn chiều cao tối thiểu, hay **vẫn vẽ nhưng đánh dấu "range vụn"** để người đọc tự quyết? Lý thuyết Wyckoff không cho ngưỡng nào (THEORY §10 mục 2 ghi rõ đây là chỗ mơ hồ của tài liệu gốc).
