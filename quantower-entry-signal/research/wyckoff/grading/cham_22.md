# Chấm bài #22 — Tích lũy (ACC) · 2026-05-26 11:43 → 13:52 (129 nến M1)

**Điểm: 7/10** — Bài tốt nhất trong lô. Khung range, Phase A, biên, tên range đều đúng; chỉ cần **sửa nhãn Spring → Shakeout**, siết lại Phase C/D và vá chỉ số nỗ lực/kết quả.

## Lỗi (nặng → nhẹ)

### 1. Gọi Spring cho một cú lùng bùng 6-8 nến ngoài biên — luật vi phạm: L5 (Spring vs Shakeout phân biệt bằng THỜI GIAN)
- **Thuật toán gắn:** **Spring** 12:31 tại 4533.1, VSA 3.31x, trạng thái confirmed.
- **Đúng phải là:** **Shakeout** (hoặc Spring #3 / Terminal Shakeout theo THEORY §3.5). L5: Spring = phá ra rồi rút vào trong range trong **≈3-4 nến hoặc ít hơn**. Ở đây giá phá biên chính dưới 4538.0 và **lùng bùng ở ngoài** — sau đáy 12:31 còn tạo thêm đáy quanh 12:33 và 12:36 (~4535–4536) rồi mới thu vào. Cường độ cũng khớp Shakeout hơn Spring: VSA **3.31x** và xuyên biên **4.9 giá** (47% biên chính) — THEORY §3.5 xếp "volume tăng đột biến, spread mở rộng, phá sâu" vào Spring #3/Terminal Shakeout, không phải Spring #1/#2.
- **Dấu hiệu quyết định trên chart:** trên ảnh, cụm nến quanh 12:31–12:38 nằm **dưới** đường biên chính dưới 4538.0 nhiều nến liên tiếp; đáy tuyệt đối trùng đúng đường nét đứt biên phụ 4533.1.
- **Nghi phạm trong thuật toán:** ngưỡng "số nến quay lại trong range" đang quá lỏng (hoặc đo bằng nến đầu tiên có **high** trở vào trong thay vì **close** trở vào trong — Ca #5 nguồn 4.pdf: neo giá đóng cửa). Cần: `Spring nếu close trở vào range trong ≤4 nến, ngược lại Shakeout`; và thêm nhánh phân loại #1/#2/#3 theo VSA + độ sâu xuyên biên.

### 2. Phase C (18n) dài hơn Phase D (13n) — luật vi phạm: L8
- **Thuật toán gắn:** A 16n · B 32n · **C 18n** · **D 13n** · E 51n.
- **Đúng phải là:** Phase C là phase **ngắn nhất**. Ở đây C bị kéo từ 12:31 (nến shock đầu) đến 12:48, tức nó gom cả cú shakeout **và** cả nhịp bò lên 15 giá từ 4534 tới sát 4548. Đúng ra: Phase C = cú shakeout + nhịp thu vào range (~12:31–12:38, 8 nến), phần bò lên 12:39–12:48 đã là **Phase D** (cầu áp đảo, đi tìm biên trên).
- **Dấu hiệu quyết định trên chart:** trong khung "Phase C (18n)" có cả một chuỗi nến xanh thân đầy liên tiếp đi lên — đó là hành vi Phase D, không phải hành vi "test nguồn cung còn lại".
- **Nghi phạm trong thuật toán:** giống bài #21 — Phase C mở tại nến shock và đóng tại SOS. Nên đóng Phase C tại nến **thu hẳn vào trong range** (close trở vào), rồi mở D từ đó.

### 3. Thiếu LPS[D] — nhịp retest sau SOS bị bỏ — luật vi phạm: L10
- **Thuật toán gắn:** SOS 12:49 (4552.5) → nhảy thẳng Phase E 13:02, không có LPS[D].
- **Đúng phải là:** L10 định nghĩa D+E = CBR = phá biên, **hồi về retest nhưng giữ được ở ngoài biên**, rồi đi tiếp. Trên chart có đúng nhịp đó: sau khi lên 4556.8 (biên phụ trên), giá hồi về vùng 4548–4550 quanh 13:14–13:20 rồi bật tiếp lên 4561. Đó là LPS[D] và nó bị bỏ trắng.
- **Lưu ý cân nhắc (Ca #21 nguồn 7.pdf):** giảng viên đã xác nhận "không phải TR nào cũng có BU ở Phase D" — nên đây là lỗi **nhãn thiếu**, không phải lỗi cấu trúc. Nhưng ở bài này nhịp retest tồn tại rõ nên phải gắn.
- **Nghi phạm trong thuật toán:** cửa sổ tìm LPS[D] khép lại quá sớm (Phase D chỉ 13 nến, đóng ở 13:01) trong khi nhịp hồi rơi vào 13:14, tức đã bị đẩy sang Phase E.

### 4. Chỉ số nỗ lực/kết quả: bài này er đúng chiều nhưng câu diễn giải vẫn là chuỗi hardcode — THEORY §2.2
- **Thuật toán in:** effort 1.33x, result 0.86, er = **1.54** → "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)".
- **Đánh giá:** riêng bài này **đo đúng** (er > 1 = nỗ lực > kết quả, đúng là dấu hiệu hấp thụ; nhịp 12:34 nằm đúng vùng đi ngang trước shakeout — hợp lý). Nhưng đối chiếu #20 (er 0.18), #21 (0.49), #23 (0.38), #24 (0.52) in **cùng một câu** → chuỗi bị hardcode, phải vá chung.

### 5. SOT phía dưới n=1 kèm tỷ lệ 0.00 (trình bày)
- Cần in `chưa đủ nhịp (n<3)` thay vì "chớm n=1, thrust cuối/đầu=0.00" (THEORY §7: SOT cần ≥3 nhịp).

## Đạt
- **L1 — điều kiện mở range:** move giảm **23.0 giá / 52 nến**, hiệu suất 0.60, đi từ 4573 xuống 4538 — một MOVE xu hướng thật, bị đúng cây cao trào chặn lại tại cực trị 4538.0 (vol 130, VSA 2.71x, biên độ 5.6 giá, và cây 11:35 VSA 5.62x liền cụm).
- **L2 — Phase A:** đủ 3 lần đổi hướng và **ST[A] làm đúng việc**: 11:58 tại **4536.0**, tức quay lại đúng vùng climax và chọc nhẹ xuống dưới nó — chuẩn L2, khác hẳn lỗi "ST[A] giữa range" ở bài #19/#24. Phase A kết thúc đúng tại ST[A].
- **L3 — biên:** biên chính = climax 4538.0 + AR 4548.4, cố định. Biên phụ mỗi bên đúng 1: trên 4556.8, dưới 4533.1 (Shakeout) — cả hai đều là cực trị xa nhất thật (không như bài #21 bỏ mất cực trị).
- **L4 — tên range:** SC + phá **lên** thật → **Tích lũy (ACC)**, đúng.
- **L9 — Phase B dài nhất trong A–D** (32n) và đúng là giai đoạn cung/cầu đỡ nhau: giá dập dềnh 4540–4549, không bên nào đi xa hơn.
- **L10 — SOS bứt qua biên PHỤ:** SOS 12:49 dẫn tới đóng cửa trên **4556.8**, không chỉ vượt biên chính 4548.4 — đúng yêu cầu "SOS thực sự mạnh" của L3.
- **SOT phía trên** đo đúng bản chất: thrust cuối/đầu 0.23 + volume 1.00 → gọi "HẤP THỤ (volume ≥ nhịp đầu, canh giữ vùng)" khớp THEORY §7 (rút ngắn + volume lớn = nỗ lực nhiều phần thưởng ít → lực đối lập sắp xuất hiện). Đúng là ngay sau đó giá bị dìm xuống shakeout.
- **L6/L7:** không có nhãn ST[B] rác, không spam nhãn; các nhãn đều 1 điểm.
