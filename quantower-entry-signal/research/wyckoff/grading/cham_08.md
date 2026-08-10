# Chấm bài #08 — Chưa rõ (BCLX) (DIST?) · 2026-04-17 13:13 → 20:59 (266 nến M1)

**Điểm: 2/10** — Range mở đúng chỗ nhưng bài **bỏ dở giữa chừng**: cú phá xuống rõ mồn một ở cuối chart không được ghi nhận, range đóng "chưa rõ hướng" trong khi mắt thường đọc ra ngay là Phân phối. Cộng thêm nhãn BCLX rơi lệch 23 giá khỏi biên chính của chính nó.

## Lỗi (nặng → nhẹ)

### 1. Bỏ sót hẳn SOW / Phase C-D-E — luật vi phạm: L4, L10
- **Thuật toán gắn:** chỉ có Phase A (31 nến) + Phase B (236 nến), range đóng ở trạng thái "Chưa rõ (BCLX)", `completed`, **không** đặt tên 4 mẫu hình.
- **Đúng phải là:** **Phân phối**. Trên ảnh, từ ~19:16 giá trượt khỏi vùng cân bằng, thủng biên chính dưới 4909.2 quanh 20:20 và đóng cửa xuống tận 4886 rồi tiếp tục — đó là một SOW đủ tiêu chuẩn (đóng cửa hẳn ngoài biên, các nến sau giữ nó ở ngoài, đúng định nghĩa L5 "phá THẬT").
- **Dấu hiệu quyết định:** biên chính dưới 4909.2; nhóm nến cuối chart nằm ở 4886–4890, thấp hơn biên 20+ giá, và không hề quay lại. Panel volume ở đoạn 20:54 có cụm thanh cao.
- **Nghi phạm trong thuật toán:** range bị **cắt tại khe thời gian** (chart nhảy từ 04-17 20:54 sang 04-19 23:09 = khe cuối tuần > 4 giờ, luật cắt range của lỗi K). Nhưng cú phá xảy ra **trước** khe — logic đang cắt range trước khi kịp kết luận cú phá đang chờ. Cần: khi cắt range vì khe, phải **chốt kết cục của cú phá đang pending** bằng dữ liệu đã có, thay vì vứt bỏ.

### 2. Nhãn BCLX rơi vào cây SAI — lệch 22.9 giá dưới biên chính do chính nó tạo — luật vi phạm: L3, mục 4.0 spec
- **Thuật toán gắn:** biên chính trên = 4953.8 (đỉnh nến 13:13), nhưng **nhãn BCLX đặt tại nến 13:18, giá 4930.9**, VSA 5.30x.
- **Đúng phải là:** nhãn climax phải nằm tại cây chặn move — nến **13:13**: high 4953.8, VSA 3.31x, **thân chỉ 0.16** (râu trên dài) — đó mới là hình dạng BCLX kinh điển. Nến 13:18 là nến **XANH** (open 4923.7 → close 4930.3) nằm giữa nhịp giảm, tức nó là một cú bật lên, không chặn gì cả.
- **Dấu hiệu quyết định:** nhìn ảnh, nhãn BCLX nằm thấp hơn đường "biên CHÍNH trên 4953.8" gần một nửa chiều cao range. Đây đúng là lỗi nặng nhất của vòng v5 (nhãn climax không neo cây climax) **tái xuất** — bản vá "kẹp theo nến mở range cố định" chưa chặn được ca này.
- **Nghi phạm trong thuật toán:** tiêu chí chọn nhãn trong cụm climax vẫn là "cây VSA cao nhất" đơn thuần (5.30x > 3.31x) mà **không kiểm màu nến khớp hướng move** (mục 3 điều kiện (3)) và không kiểm khoảng cách giá tới mức biên. Phải thêm: nến mang nhãn BCLX bắt buộc là nến chạm/sát mức biên trên và không được là nến xanh nằm dưới biên quá X giá.

### 3. ST[A] không hề test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 13:43, giá 4933.0.
- **Đúng phải là:** ST[A] là cú quay về phía climax rồi **bị chặn lần nữa** ở vùng climax. 4933.0 cách climax 4953.8 tới **20.8 giá = 47% chiều cao range** — đó là một cú ngọ nguậy giữa range, không phải test biên.
- **Dấu hiệu quyết định:** biên chính 4909.2–4953.8 (44.6 giá); ST[A] nằm ở 53% chiều cao.
- **Nghi phạm trong thuật toán:** bản vá v7 chỉ nâng ngưỡng **hồi tối thiểu** từ 0.2 lên 0.4× khoảng AR↔climax (ở đây đạt 0.53 nên lọt). Ngưỡng đó đo sai đại lượng — cần thêm ràng buộc **khoảng cách còn lại tới climax** (ví dụ ST[A] phải nằm trong 25–30% chiều cao tính từ climax). Đúng như mục 13.1 đã tự ghi nhận: "ST[A] vẫn thiếu ràng buộc khoảng cách đáy tới climax".

### 4. AR volume 0.35x mà không cảnh báo — luật vi phạm: THEORY §2.2
- **Thuật toán gắn:** AR 13:30, 4909.2, VSA **0.35x**, thân 0.35.
- **Đúng phải là:** AR là "sóng mua/bán bật ngược" — bật ngược 44.6 giá mà nỗ lực chỉ bằng 1/3 trung bình là bất thường, ít nhất phải gắn cờ như nhãn "AR (yếu)" mà hệ đã có sẵn.
- **Nghi phạm trong thuật toán:** nhãn "(yếu)" hiện chỉ bật khi AR rơi vào 1–2 nến sát climax; chưa dùng `ar_vsa` đã đo được (v6 mục 9) để gắn cờ.

### 5. Chỉ số bias báo sai — luật vi phạm: L9 (đọc effort↔result Phase B)
- **Thuật toán gắn:** `bias=+0` (test được **cả hai** biên).
- **Đúng phải là:** `-1`. Trong suốt 236 nến Phase B, đỉnh cao nhất chỉ tới ~4941 (≈71% chiều cao), **không** với nổi biên trên 4953.8; trong khi biên dưới 4909.2 bị chạm nhiều lần rồi thủng hẳn.
- **Ghi chú:** chỉ số này chỉ hiển thị, không gate — nhưng nó là thứ đáng lẽ mách đúng hướng phá (xuống), nên sai ở đây làm mất giá trị duy nhất của nó.

### 6. (Trình bày) Chart kéo dài qua khe cuối tuần
Trục thời gian nhảy từ `04-17 20:54` sang `04-19 23:09` mà không có dấu ngắt — người đọc dễ tưởng cụm nến bên phải thuộc cùng phiên với range.

## Đạt
- **Mục 1 (L1):** MOVE tăng 107.7 giá / 140 nến, hiệu suất 0.37 — một move xu hướng rất rõ, và cụm 13:10–13:13 (VSA 4.10x → 3.31x) đúng là chỗ move bị chặn. Điều kiện mở range chuẩn.
- **Mục 3 (L3):** biên chính = climax + AR, cố định; tỷ lệ biên phụ/chính 1.01x (gần như không có biên phụ) — sạch, không có ca "biên phụ tự nới rồi tự vượt".
- **Mục 5 một phần (L9):** Phase B 236/266 nến — đúng là phase dài nhất.

## Cần hỏi người học
- Khi khe thời gian > 4 giờ cắt ngang range mà **trước khe đã có một cú phá biên đang chờ kết cục**: chốt kết cục bằng dữ liệu trước khe (như tôi chấm ở đây), hay vẫn vứt và đóng range "chưa rõ"?
