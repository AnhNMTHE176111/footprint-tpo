# Chấm bài #38 — Tích luỹ (ACC) · 2026-06-30 01:07 → 06:30 (323 nến M1)

**Điểm: 6/10** — bài tốt nhất lô: SC thật, MOVE thật, Phase B dài nhất, LPS[C] volume co đúng bài. Phải sửa hai chỗ: Phase D 121 nến nuốt luôn Phase E, và cú phá được coi là thành công dù giá lùi hẳn vào trong range 100 nến sau đó.

## Lỗi (nặng → nhẹ)

### 1. Cú phá được tính là SOS thành công dù giá lùi hẳn vào trong range ngay sau nhịp retest — luật vi phạm: L10
- **Thuật toán gắn:** SOS 04:30 (4000.1, VSA 4.09x) → LPS[D] 04:48 (3997.2) → range mang tên "Tích luỹ", coi CBR hoàn tất.
- **Đúng phải là:** L10 đòi "hồi về retest nhưng **GIỮ ĐƯỢC** ở ngoài biên". Trên ảnh, từ ~05:00 tới ~06:10 giá lình xình 3985–3993 — **dưới** biên chính trên 3994.2 tới 9 giá (90 tick, gấp 3 lần mức "lùi hẳn" 30 tick trong spec) suốt hơn 60 nến. Cú phá 04:30 vì thế là **mSOS** (phá lên rồi thu vào), dải phase phải trả về B, và cú phá thật là cây bung 06:20–06:25 lên 4045 — chỗ đó mới là SOS / Phase D / Phase E.
- **Dấu hiệu quyết định trên chart:** đường cam "biên CHINH tren 3994.2" cắt ngang qua giữa cụm nến 05:00–06:10, cụm này phần lớn nằm **dưới** đường đó.
- **Nghi phạm trong thuật toán:** mục 7 chỉ xét "giá lùi hẳn vào trong range" trong **cửa sổ 25 nến** sau SOS. Ở đây giá giữ ngoài biên đúng trong 25 nến rồi mới tụt vào, nên nhánh vô hiệu (lỗi F) không bắn. Cần kéo dài phép kiểm tới khi Phase E được chốt thật, không cắt ở 25 nến.

### 2. Phase D dài 121 nến, Phase E vắng hoàn toàn — luật vi phạm: L10, L9
- **Thuật toán gắn:** A 34 · B 113 · C 56 · **D 121** · không có E.
- **Đúng phải là:** cú bung 06:20–06:30 vượt biên trên 51 giá (1.3× chiều cao range 38.8) chính là Phase E — "giá rời range đi tìm vùng giá mới". Gán nó vào Phase D làm Phase D **dài hơn cả Phase B**, phá luôn L9.
- **Dấu hiệu quyết định trên chart:** dải "Phase D (121n)" chạy từ 04:30 tới hết range, trùm cả đoạn lình xình 100 nến **và** cả cú bung cuối.
- **Nghi phạm trong thuật toán:** đích Phase E = "đi thêm 1× chiều cao trong 25 nến, hoặc ≥50% khi hết giờ" (mục 7 câu 3). Nhịp retest ở đây kéo dài quá 25 nến và chưa đạt 50% nên Phase E không bao giờ mở, còn Phase D thì cứ kéo tới nến cuối. Hai nhánh này chặn nhau: không đủ để mở E, cũng không đủ để vô hiệu cú phá.

### 3. Phase C dài 56 nến — không phải phase ngắn nhất — luật vi phạm: L8
- **Thuật toán gắn:** Phase C = 03:34 → 04:29, **56 nến**, dài hơn Phase A (34 nến).
- **Đúng phải là:** L8 nói Phase C là phase ngắn nhất — nó là tín hiệu đầu tiên cho thấy biên bên kia sắp bị phá, không phải một đoạn 56 nến. Trên ảnh, đoạn 03:34→04:29 chứa cả một nhịp tăng 27 giá từ 3973 lên 4000 — đó là hành trình đi tới cú phá, phải thuộc Phase B (hoặc D), không phải Phase C.
- **Nghi phạm trong thuật toán:** cách gán ngược Phase C lấy swing pivot trong cửa sổ min(60 nến, ½ Phase B) rồi mở Phase C **từ đó tới cú phá** → độ dài Phase C tự động xấp xỉ cửa sổ nhìn lại (56 ≈ 60). Cửa sổ và độ dài phase bị buộc vào nhau; nên tách: LPS[C] lấy trong 60 nến, nhưng Phase C chỉ bắt đầu vài nến trước LPS[C].

### 4. ST[A] rơi ở 62% chiều cao, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 01:40, giá 3979.4.
- **Đúng phải là:** (3979.4−3955.4)/38.8 = **62% chiều cao**, cách vùng SC 24 giá. Đó là nhịp lùi đầu tiên sau AR, không phải cú test lại 3955.4. Nếu ST[A] lấy nhịp đáy 02:19–02:30 (~3967, tức 30% chiều cao) thì Phase A đúng cấu trúc hơn nhiều.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm gần đường "biên CHINH tren" hơn là đường dưới; khoảng cách tới đường 3955.4 bằng gần 2/3 cả range.
- **Nghi phạm trong thuật toán:** mục 4.2 — swing pivot 5 nến + sàn 1.5× biên độ TB luôn bắt nhịp lùi đầu tiên. Lỗi lặp 4/5 bài lô này (48% · 68% · 62% · 43%). THEORY §5 có dòng bảo lãnh cho ST ở 1/3 nửa trên, nhưng 62% chưa vào 1/3 trên, và L2 vẫn đòi "test lại vùng climax".

### 5. Chú giải nhịp nỗ lực/kết quả nói ngược dấu — lỗi trình bày chỉ số (v6)
- **Thuật toán gắn:** nhịp 03:09, effort 0.83x, result 1.57, er = 0.53 → in "vung hap thu NGHI VAN (volume nhieu, ket qua it)".
- **Đúng phải là:** effort 0.83x = volume **dưới** trung bình, result 1.57 = kết quả lớn → đây là **ít nỗ lực nhiều kết quả**, tức nghèo cung (No Supply) — dấu hiệu **sức mạnh** trong một range tích luỹ, đúng với kết cục phá lên. Câu in ra nói ngược hẳn dấu.
- **Nghi phạm trong thuật toán:** chuỗi chú giải hardcode, in y hệt ở cả 5 bài lô này với er từ 0.13 tới 0.94.

### 6. AR neo bóng nến doji — lỗi mức biên (nhẹ), đối chiếu Ca #5 nguồn 4.pdf
- **Thuật toán gắn:** AR 01:29, mức 3994.2, VSA 1.37x, **thân 0.03**.
- **Ghi rõ:** dùng cực trị của AR làm biên là chuẩn Wyckoff, nên đây không phải lỗi luật. Nhưng thân 0.03 nghĩa là 3994.2 do râu nến tạo — đúng ca mà spec mục 4.1 gọi là "AR (yếu)" và trên chart **không hề hiển thị** cảnh báo đó. Chính mức râu này làm cụm nến 05:00–06:10 nằm dưới biên (xem lỗi 1). Nên in cảnh báo "AR yếu / neo râu" khi thân < 0.15.

## Đạt
- **Climax SC xuất sắc (L1):** 01:07, biên độ **25.6 giá**, volume 2097 so nền ~150 → VSA **7.11x**, đóng cửa hồi 3.7 giá khỏi đáy. Cao trào bán thật, đúng THEORY §3.3 — không phải "climax phiên chết" như nhiều bài khác.
- MOVE trước climax (L1): giảm **60.1 giá / 108 nến**, hiệu suất 0.38; trên ảnh là downtrend liên tục từ 4038 xuống 3955, climax chặn đúng đáy.
- Biên chính = climax + AR (3955.4 / 3994.2), cố định; không có biên phụ (tỉ lệ 1.00x) — đúng L3: giá chưa từng thò ra ngoài biên chính, nên không được bịa biên phụ.
- Phase B = 113 nến, dài nhất trong nhóm A/B/C → thoả L9.
- **Bộ chỉ số Phase B đo đúng bản chất:** bias = +1 khớp chart (Phase B chạm biên trên 3994 nhưng đáy chỉ tới 3967, còn cách biên dưới 12 giá); SOT-up = SOT với **n=4** (đủ ngưỡng ≥3 lần đẩy của THEORY §7), thrust 0.78 + volume 1.43 → "hấp thụ"; SOT-dn = chớm, volume 0.34 → "cạn kiệt". Đọc gộp: đỉnh rút ngắn kèm volume tăng ở trên + đáy cạn kiệt ở dưới = cầu đang đỡ, cung hết hàng → khớp đúng kết cục phá lên. Đây là chỗ chỉ số mới thật sự nói được điều gì.
- Chuỗi effort/result của các nhãn rất đúng bài: SC 7.11x → SOS 4.09x (volume tăng ở cú phá) → LPS[C] 0.41x và LPS[D] 0.44x (test volume co). Đúng THEORY §6.4.
- LPS[C] và LPS[D] mỗi cái một điểm duy nhất, tách vai rõ trước/sau SOS — đúng L7 và tránh được lỗi gộp LPSY[C]/LPSY[D] của Ca #3 nguồn 4.pdf.
- Tên range đúng L4: origin SC + phá lên = Tích luỹ.
