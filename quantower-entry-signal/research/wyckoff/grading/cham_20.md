# Chấm bài #20 — Tích lũy (ACC) · 2026-05-26 11:43 → 13:52 (129 nến M1)

**Điểm: 8/10** — Bài tốt nhất lô này. Vẽ đúng: MOVE thật, climax thật, Spring thật, SOS thật, giá đi tiếp. Chỉ sửa hai nhãn và một tỉ lệ phase.

## Lỗi (nặng → nhẹ)

### 1. Phase C (29 nến) DÀI HƠN Phase B (32 nến) chỉ 3 nến — gần như vi phạm L8/L9
- **Thuật toán gắn:** A 16 · B 32 · **C 29** · D 18 · E 35 nến. Phase E là phase dài nhất, Phase C gần bằng Phase B.
- **Đúng phải là:** L9 nói B dài nhất, L8 nói C ngắn nhất. Ở đây B chỉ nhích hơn C 3 nến, và E (35) dài hơn cả B. Nguyên nhân đọc được: Phase C bắt đầu ngay tại **cây Spring 12:31** và kéo tới 12:59 — tức nó bao trọn cả nhịp giá bò từ 4533 lên 4548 sau Spring. Nhịp bò đó là **phần đầu của cú bứt**, thuộc Phase D, không phải C. Phase C nên chỉ gói cú Spring + 3-5 nến xác nhận, còn lại đẩy sang D.
- **Dấu hiệu quyết định trên chart:** giữa vạch "Phase C (29n)" và vạch "Phase D (18n)" là một nhịp tăng dựng đứng liên tục từ 4534 lên 4556 — không có chỗ nào giá dừng lại để phân định C/D; máy cắt ở giữa nhịp một cách tuỳ tiện.
- **Nghi phạm trong thuật toán:** Phase C kết thúc khi SOS được **chốt** (sau 3 nến xác nhận), nhưng SOS đã được đặt **hồi tố** về cây phá thật. Ranh giới C/D nên dời theo nhãn hồi tố đó, chứ không đứng ở nến chốt.

### 2. Nhãn SOS neo vào cây VSA 1.03x, trong khi cây phá thật có volume nổi bật hơn — luật vi phạm: mục 8, lỗi hệ thống B (còn sót)
- **Thuật toán gắn:** SOS 13:00 tại 4556.8, **VSA 1.03x**, thân 0.93.
- **Đúng phải là:** thân 0.93 và đúng hướng thì tốt, nhưng VSA 1.03x là khối lượng trung bình. Panel volume cho thấy cụm thanh vàng cao nhất của cú bứt nằm sớm hơn, quanh 12:40–12:53 — đúng đoạn giá xé từ 4540 lên 4553. SOS nên neo vào đó. Đây là cùng một bệnh với bài #16 nhưng nhẹ hơn nhiều (1.03x thay vì 0.55x).
- **Dấu hiệu quyết định trên chart:** so cột volume tại 13:00 với cụm cột vàng ở 12:40–12:53 — cụm sớm hơn cao hơn rõ.

### 3. Phase E 35 nến nhưng đoạn cuối giá đã sập lại vào trong range — luật vi phạm: L10 (biên nhẹ)
- **Thuật toán gắn:** Phase E 13:18 → 13:52, range đóng ở 13:52.
- **Đúng phải là:** đúng là giá đi tiếp lên 4562 (đạt đích). Nhưng nhìn tiếp sau mốc đóng range: khoảng 13:45–13:56 có một cây đỏ lớn kéo giá từ 4560 về 4546 — **xuyên qua biên chính trên 4548.4 vào lại trong range**. Range đóng đúng lúc (13:52) nên không sai về mặt luật, chỉ là cú phá này thọ rất ngắn. Ghi nhận để nhắc: Phase E "đi tìm vùng giá mới" ở đây chỉ giữ được ~45 phút.
- **Dấu hiệu quyết định trên chart:** cây đỏ dài ngay sau nhãn "Phase E (35n)" đưa giá xuống dưới đường cam nét liền 4548.4.
- **Đây là quan sát, không phải lỗi thuật toán** — mốc đóng range hợp luật.

### 4. ST[A] 4536.0 nằm THẤP HƠN mức climax 4538.0 — trình bày/nhãn biên phụ
- **Thuật toán gắn:** ST[A] 11:58 tại 4536.0; biên chính dưới 4538.0; biên phụ dưới 4533.1.
- **Đúng phải là:** L3 nói rõ "ST[A] vượt qua mức climax cũng tạo biên phụ". ST[A] ở 4536.0 đã vượt climax 2 giá, nên đúng ra nó phải tạo biên phụ dưới ở **4536.0** trước. Sau đó Spring xuống 4533.1 mới thay thế nó (biên phụ cũ biến mất, đúng L3). Kết quả cuối cùng **đúng**, chỉ là trên chart không thấy dấu vết của bước trung gian — không phải lỗi, ghi để xác nhận máy làm đúng L3.

## Đạt
- **Mục 1 — mở range:** đúng hoàn toàn. MOVE giảm 23.0 giá / 52 nến / hiệu suất **0.60** (cao nhất lô này); climax VSA **2.71x**, volume 130 so với dãy 24–59 quanh nó, biên độ 5.6 giá, nến **đỏ** (O 4539.3 > C... thực ra C 4542.8 > O — xem ghi chú dưới), và là đáy thấp nhất cửa sổ. Climax chặn move thật. Đúng L1.
- **Mục 2 — Phase A:** SC 4538.0 → AR 4548.4 → ST[A] 4536.0, 16 nến, kết đúng tại ST[A]. ST[A] test đúng vùng climax (vượt nhẹ 2 giá). Đúng L2.
- **Mục 3 — biên:** biên chính = climax + AR, cố định suốt range. Biên phụ đúng 1 mỗi bên (4533.1 do Spring, 4556.8 do cú bứt). Đúng L3.
- **Mục 4 — tên range:** origin SC + phá lên thật = **Tích luỹ**. Đúng L4.
- **Mục 5 — Phase B:** đọc được effort↔result: trong B giá thử biên dưới hai lần (11:59, 12:20) rồi mới có Spring — cung cạn dần.
- **Mục 6 — Phase C, đây là điểm sáng nhất:** **Spring thật, gán đúng loại theo L5.** Spring 12:31 tại 4533.1, VSA **3.31x** — cú rũ có khối lượng nổ, phá xuống dưới biên phụ, rồi rút vào trong range nhanh. Trạng thái ghi **`confirmed`** (chấm viền trắng trên ảnh) — đúng là cú rũ duy nhất của range, đúng quyết định 7 của người học. Đây là **case DỄ** chứ không phải case khó gán ngược — hiếm trong bộ này (tài liệu ghi 36/49 range là case khó).
- **Mục 7 — Phase D/E:** SOS đóng cửa bứt **qua biên phụ trên**; LPS[D] 13:13 tại 4549.9 là nhịp hồi retest **giữ được** trên biên chính 4548.4 (cao hơn 1.5 giá) — đúng CBR của L10. Phase E đi tới 4562, đạt đích.
- **Mục 9 — nhãn:** đúng vai, không thừa không thiếu. Có Spring[C] và LPS[D] mà **không** có LPS[C] — đúng, vì đây là case dễ, Phase C đã có cú rũ nên không cần gán ngược. Không lẫn LPS[C] với LPS[D] (lỗi Ca #3 nguồn 4.pdf). Mỗi cái một điểm, đúng L7. Không có ST[B], đúng L6.

## Cần hỏi người học
- Nến climax bài này có O=4539.3, C=4542.8 → **nến xanh**, nhưng được gán **SC** (mục 3(3) tài liệu thuật toán đòi nến **đỏ** chặn move giảm). Nó là nến rũ đuôi kinh điển (low 4538.0, đóng cửa gần đỉnh nến, thân 0.62) — về cơ chế Wyckoff thì đây **đúng** là Selling Climax (bán tháo rồi bị hấp thụ ngay trong nến). Vậy điều kiện "màu nến khớp hướng move" có nên gỡ bỏ, thay bằng "nến tạo cực trị + đóng cửa hồi ≥ 50% biên độ nến"? Em nghiêng về gỡ — chính điều kiện màu nến đang làm bài #19 gán SC cho một cây xanh vì lý do sai (dời mốc cụm), còn ở đây nó suýt loại oan một SC thật.
