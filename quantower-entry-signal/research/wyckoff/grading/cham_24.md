# Chấm bài #24 — Tích lũy (ACC) · 2026-06-02 01:01 → 06:26 (325 nến M1)

**Điểm: 5/10** — Range đặt đúng chỗ, climax rất rõ, tên ACC đúng; nhưng **Phase A bị chốt sai ở giữa range** và **thiếu hẳn Phase C**, nên xương sống cấu trúc lệch: nhãn mSOW ở 01:52 mới là ST[A] thật.

## Lỗi (nặng → nhẹ)

### 1. ST[A] đặt đúng ĐIỂM GIỮA range — Phase A chưa xong đã bị đóng — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 01:18 tại **4511.4**, đóng Phase A ở đó (18 nến); nhãn tại 01:52 (4492.3) bị gọi là **mSOW** và đẩy sang Phase B.
- **Đúng phải là:** biên chính là 4501.0–4521.6, điểm giữa = **4511.3**. ST[A] được đặt ở **4511.4**, tức lệch điểm giữa **0.1 giá** — đây đúng là "một cái ngọ nguậy giữa range" mà L2 cấm, không phải test lại vùng climax. ST[A] thật là cú **01:52 xuống 4492.3**: nó quay lại phía climax, chọc **xuống dưới** mức climax 4501.0 và bị chặn ở đó → đúng định nghĩa L2 (lần đổi hướng thứ 3) và đúng L3 ("ST[A] vượt qua mức climax cũng tạo biên phụ" — biên phụ dưới 4492.3 chính là nó). Vậy: **Phase A = 01:01 → 01:52 (52 nến), nhãn 01:52 = ST[A] (dạng climax-fail / Spring #3 tiềm năng), không phải mSOW; Phase B bắt đầu 01:53.**
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn `ST[A]` nằm lọt giữa hai đường biên chính, còn nhãn `mSOW` nằm đúng trên đường nét đứt biên phụ dưới 4492.3 — cây rơi đó có VSA 2.40x và là đáy tuyệt đối của toàn range. Cấu trúc "climax → AR → chọc phá đáy climax rồi bật" mới là CHoCH hoàn chỉnh.
- **Nghi phạm trong thuật toán:** nhánh `A_st` chọn **swing đầu tiên** sau AR làm ST[A] mà không kiểm khoảng cách tới mức climax. Cần gate: `|st − mức climax| ≤ ~0.35 × biên chính`, nếu swing đầu tiên không đạt thì tiếp tục đi tìm. Đây là **cùng một lỗi với bài #19** (ST[A] ở 42% range) → lỗi hệ thống, không phải ngẫu nhiên.

### 2. Thiếu hẳn Phase C — không gán ngược từ SOS — luật vi phạm: L8
- **Thuật toán gắn:** A 18n · B **162n** · **D** 25n · E 121n — nhảy thẳng B → D.
- **Đúng phải là:** L8 nói rõ ca khó (chỉ có LPS[C], khó xác nhận tại thời điểm đó) thì **chờ SOS rồi quay lại vẽ Phase C** — "có Phase D rồi mới xác định được Phase C". SOS ở 04:01 (4531.0, VSA **7.45x**). Lùi lại: từ ~03:37 giá bò lên qua biên chính trên rồi đi ngang 4526–4530 khoảng 20 nến; nhịp lùi cuối cùng trong cụm đó (quanh 03:50, giá thoái về ~4525) chính là **LPS[C]**. Phase C = ~5-8 nến ở đó.
- **Dấu hiệu quyết định trên chart:** trên ảnh có cụm nến nhỏ đi ngang sát dưới đường nét đứt biên phụ trên 4530.0 ngay trước nến SOS thân dài — đúng hình "LPS trước SOS" (và theo Ca #5/#11 nguồn 7.pdf thì cụm đi ngang này còn có thể vẽ thành LPS AREA, dù L7 chốt chỉ đánh 1 điểm).
- **Nghi phạm trong thuật toán:** không có bước hồi tố "sau khi chốt SOS, lùi tìm swing-low cuối cùng trước SOS làm LPS[C] và mở Phase C tại đó". Hiện Phase C chỉ được tạo khi bắt được shock (Spring/Shakeout/UTAD) — nên mọi ca khó đều mất Phase C.

### 3. Biên phụ trên 4530.0 do chính cú phá thành công tạo ra → lập luận vòng tròn — luật vi phạm: L3 (định nghĩa biên phụ)
- **Thuật toán gắn:** biên phụ trên = **4530.0**, rồi đòi SOS phải đóng cửa vượt nó (SOS 04:01 tại 4531.0).
- **Đúng phải là:** L3 định nghĩa biên phụ = "mức cực trị xa nhất mà **một thế lực đã cố phá range gốc** tạo ra", ngụ ý một nỗ lực **đã bị chặn**. Nhưng 4530.0 ở đây không phải một nỗ lực bị chặn — nó là **phần đang lên của chính cú phá thắng**: giá đã đóng cửa trên biên chính 4521.6 từ khoảng 03:40 và **giữ được** trên đó liên tục ~20 nến. Theo L5, "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài → đó là phá THẬT". Nghĩa là **SOS thật xảy ra ~03:40, không phải 04:01**; thuật toán tự nới biên phụ lên theo giá rồi đợi phá cái biên nó vừa nới — đúng cái "biên bị kéo theo giá" mà L3 cấm.
- **Dấu hiệu quyết định trên chart:** đoạn 03:40–04:00 gồm toàn nến đóng cửa **trên** đường biên chính trên 4521.6, không một lần thu lại vào trong range.
- **Nghi phạm trong thuật toán:** biên phụ được cập nhật bằng cực trị **không điều kiện**, không đòi "cực trị đó phải bị chặn/thu về trong range". Sửa: chỉ nới biên phụ khi cực trị mới **kèm** một cú thu về trong range (close trở vào) trong ≤N nến; nếu không thu về thì đó là cú phá thật, phải chốt SOS ngay.

### 4. Chỉ số nỗ lực/kết quả: chọn sai nhịp + diễn giải NGƯỢC — THEORY §2.2 (lỗi ĐO)
- **Thuật toán in:** "nhịp nỗ lực/kết quả **cao nhất** trong Phase B: effort 1.35x, result **2.57**, er = **0.52** → vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đúng phải là:** er = 0.52 nghĩa là kết quả gấp gần 2 lần nỗ lực — "nỗ lực ít, kết quả nhiều", **ngược hẳn** câu in ra. Trong khi Phase B của bài này (162 nến) chắc chắn có nhịp effort cao hơn 1.35x — tiêu chí chọn nhịp đang chọn theo er nhỏ nhất chứ không theo nỗ lực lớn nhất. Câu diễn giải là chuỗi hardcode (in y hệt ở cả 6 bài #19–#24 bất kể er = 0.18 hay 1.54).
- **Nghi phạm trong thuật toán:** hàm chọn nhịp dùng sai chiều so sánh; câu kết luận nằm ngoài nhánh `if er > 1`.

### 5. AR bị hạ cấp "yếu" trong khi nó là cú bật mạnh nhất của range (nhẹ, ngữ nghĩa)
- **Thuật toán gắn:** **AR (yếu)** 01:14 tại 4521.6, VSA 1.88x.
- **Đúng phải là:** AR này bật **20.6 giá trong 13 nến** ngay sau SC, VSA 1.88x — theo THEORY §3.3 (AR = sóng mua đẩy giá lên, xác lập biên trên tạm thời) thì đây là AR **bình thường/mạnh**, không "yếu". Nhãn "(yếu)" dựa trên thân/biên = 0.04 của riêng nến mốc, tức đo **một nến** thay vì đo **cú bật**.
- **Nghi phạm trong thuật toán:** tiêu chí "AR yếu" dùng thân/biên độ của nến cực trị. Nên đổi sang đo **biên độ cú bật / biên độ move trước climax** hoặc số nến của cú bật.

### 6. SOT phía trên n=1 kèm tỷ lệ 0.00 (trình bày)
- THEORY §7 đòi ≥3 nhịp. In `chưa đủ nhịp (n<3)` thay vì "chớm n=1, thrust cuối/đầu=0.00".

## Đạt
- **L1 — mở range:** move giảm 18.3 giá / 29 nến (hiệu suất 0.59) bị chặn bởi cây cao trào rất rõ tại **cực trị 4501.0**: vol **272, VSA 5.98x**, biên độ 7.4 giá, thân/biên 0.07 (nến pin đáy) — kèm cây liền trước 3.91x/128 lot. Đây là SC kinh điển, khớp THEORY §3.3 (spread mở rộng + volume tăng mạnh).
- **L3 (một phần):** biên chính = climax 4501.0 + AR 4521.6, **cố định**, không bị kéo theo giá; mỗi bên đúng 1 biên phụ; biên chính 20.6 giá (0.46%) là độ rộng lành mạnh cho M1 vàng — không phải range vụn.
- **L4 — tên range:** SC (move giảm bị chặn) + phá **lên** thật (SOS 4531.0 → Phase E đi tới 4575) → **Tích lũy (ACC)**, đúng bảng 4 mẫu hình. Bối cảnh trước range là move giảm thật nên gán SC **hợp lệ** — không mắc lỗi kinh điển "SC trong tái tích luỹ" (Ca #9/#14 nguồn 7.pdf).
- **L9 — Phase B là phase dài nhất** (162/325 nến), và đọc đúng bản chất: hai bên đỡ nhau, giá lên xuống trong 4492–4521 nhiều lần.
- **L10 — Phase E đúng nghĩa:** sau SOS giá rời range đi tìm vùng giá mới thật (4531 → 4575, +44 giá, 121 nến) — đây là Phase E thuyết phục nhất trong lô #19–#24.
- **SOT phía dưới đo đúng và là chỉ số giá trị nhất của bài:** trạng thái **SOT với n=3** (đúng ngưỡng tối thiểu THEORY §7), thrust cuối/đầu **0.16** + volume 0.92 → "cạn kiệt". Đọc bằng lời: các đáy trong Phase B rút ngắn dần còn 16% lực đẩy đầu trong khi volume không giảm → cung cạn, đúng là ngay sau đó cầu áp đảo và SOS bung. Chỉ số này đo đúng bản chất.
- **L6/L7:** không có ST[B] rác, mỗi nhãn 1 điểm, không spam.

## Cần hỏi người học
- Khi giá **đóng cửa hẳn ngoài biên chính và giữ được ở ngoài ~20 nến** nhưng chưa vượt biên phụ (như đoạn 03:40–04:00 ở đây), thì tính SOS tại lúc bứt biên chính (L5: "phá THẬT") hay vẫn chờ bứt biên phụ (L3: "SOS thực sự mạnh phải qua biên phụ")? Hai luật này chỏi nhau đúng ở ca này.
