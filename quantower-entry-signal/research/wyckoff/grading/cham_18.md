# Chấm bài #18 — Tích luỹ (ACC) · 2026-06-02 01:01 → 04:24 (203 nến M1)

**Điểm: 6/10** — Bài tốt nhất trong lô: range đúng chỗ, đúng tên, hai biên chính chuẩn. Chỉ cần **sửa nhãn**: cú thủng đáy 4492.3 phải được gọi là Spring, và nhãn SOS phải dời về đúng cụm nến phá.

## Lỗi (nặng → nhẹ)

### 1. Sự kiện quyết định nhất của range bị gọi là "ST[A]" thay vì Spring — luật vi phạm: L5, và lỗi kinh điển Ca #7 nguồn 7.pdf / lỗi #6 nguồn 2.pdf (đảo chiều)
- **Thuật toán gắn:** ST[A] tại 4492.3 (01:52), coi đó là mốc đóng Phase A.
- **Đúng phải là:** đây là một **Spring** (theo L5 phân biệt bằng **thời gian quay lại**): nến 01:52 thủng 8.7 giá dưới biên chính dưới 4501.0, thân/biên độ chỉ **0.15** (nến kim), rồi **2 nến sau** giá đã đóng cửa lại trong range (01:53 c=4497.8, 01:54 c=4503.1) — dưới ngưỡng 4 nến của chính spec. Và 4492.3 là **giá thấp nhất của toàn bộ TR**, tức thoả đúng tiêu chí Spring mà giảng viên phát biểu tường minh ở Ca #19 nguồn 2.pdf. Nhãn đúng: **ST[A] = Spring** (một điểm mang hai vai, hợp lệ như Ca #2 nguồn 4.pdf), hoặc tối thiểu phải ghi "Spring".
- **Dấu hiệu quyết định trên chart:** nến kim 01:52 (VSA 2.40x, low 4492.3, close 4495.8) + hai nến hồi liền sau đưa giá về 4503.1; sau đó giá không bao giờ trở lại vùng đó nữa và kết cục là phá lên.
- **Nghi phạm trong thuật toán:** nhánh Spring/Shakeout chỉ chạy **sau khi Phase A đã chốt** (mục 5.1 — theo dõi cú thò ra biên trong Phase B). Cú rũ xảy ra **trong lúc còn đang tìm ST[A]** thì bị nhánh 4.2 chiếm trước và mất luôn nhãn. Cần cho phép nhận Spring/Shakeout ngay khi hai biên chính đã tồn tại (tức ngay sau AR), không đợi ST[A].

### 2. Nhãn SOS muộn 32 nến, đặt trên nến 17 lot — luật vi phạm: mục 8 Effort vs Result (THEORY §2.2, §6.3)
- **Thuật toán gắn:** SOS tại 03:59, giá 4529.5, volume **17 lot**, **VSA 0.92x**.
- **Đúng phải là:** SOS là cụm **03:27–03:31**: đóng cửa 4523.4 → 4525.3 → 4525.4 → 4526.2 → 4527.5 với volume 98 / 111 / **264** / 127 / **252** lot (VSA 2.9x – 5.4x). Đó chính là "spread mở rộng + volume tăng" của định nghĩa SOS.
- **Dấu hiệu quyết định trên chart:** panel khối lượng có cụm cột cao ở 03:27–03:31; chỗ dán nhãn SOS (03:56–03:59) volume là 5 / 9 / 9 / 17 lot — vùng chết nhất của cả range.
- **Nghi phạm trong thuật toán:** điều kiện "3 nến LIÊN TIẾP đóng cửa vượt biên phụ ≥30 tick **và thân ≥45%**". Các nến đẩy thật bị loại vì thân/biên độ thấp do râu dài (03:29 thân 0.05, 03:30 thân 0.43, 03:32 thân 0.16), nên chuỗi 3 nến chỉ khớp được ở cụm nến lặng sau đó (03:57 thân 0.75, 03:58 thân 0.60, 03:59 thân 0.87). Sửa: đặt nhãn tại **nến phá đầu tiên / nến volume lớn nhất trong cụm**, dùng 3 nến sau chỉ để **xác nhận**, không để định vị nhãn.

### 3. Phase C phình thành 60 nến, gần bằng Phase B (66) — luật vi phạm: L8
- **Thuật toán gắn:** C = 02:59 → 03:58 (60 nến), B = 66 nến.
- **Đúng phải là:** Phase C là phase **ngắn nhất**. Nếu SOS đặt đúng ở 03:27 thì Phase C chỉ còn ~28 nến (02:59 → 03:26) — hợp lý ngay. Đây là **hệ quả** của lỗi #2, không phải lỗi độc lập.
- **Dấu hiệu quyết định trên chart:** dải Phase C phủ cả đoạn giá **đã bứt lên trên biên chính 4522** (03:27 trở đi) — nhìn ảnh thấy rõ vạch tím Phase D nằm sau khi giá đã lên tận 4529.

### 4. Phase E chỉ 1 nến (trình bày / tham số, không phải lỗi đọc chart)
- Đích Phase E = 1.0 × chiều cao range = 21 giá từ cú phá; trong 25 nến chỉ đi được ~50% nên chốt E hình thức 1 nến. Thực tế giá chạy tiếp tới **4548.6** (04:58) = +19 giá so với mốc SOS, tức Phase E là thật, chỉ do cửa sổ 25 nến quá ngắn nên bị ghi nhận thiếu.

## Đạt
- Điều kiện mở range: MOVE 25.8 giá / 29 nến / hiệu suất **0.80**, climax VSA 5.98x đúng là nến chặn move — L1 đạt trọn.
- Biên chính = climax (4501.0) + AR (4522.0), khớp đúng mức AR, **không bị kéo theo giá** về sau — L3 đạt.
- Biên phụ đúng 1 cái mỗi bên (4492.3 do cú rũ đáy, 4522.5 do cú thăm dò đỉnh) — L3 đạt.
- Tên **Tích luỹ** khớp origin SC + phá lên thật (đóng cửa vượt biên phụ và giá chạy tới 4548.6) — L4 đạt.
- LPS[C] gán **một điểm duy nhất** (02:59 @4515.3), đúng L7; và đúng chỗ theo Ca #8 nguồn 2.pdf — thu hẹp quanh nhịp test cuối trước SOS.
- **Không có** LPS[D] và không bịa ra một cái — đúng Ca #21 nguồn 7.pdf: Phase D không bắt buộc có BU/nhịp lùi.
- Phase B (66 nến) là phase dài nhất — L9 đạt.

## Cần hỏi người học
- Với cú thủng đáy vừa đóng Phase A vừa thoả định nghĩa Spring (như 01:52 ở đây), anh muốn máy in **một nhãn ghép "ST[A] / Spring"** hay ưu tiên nhãn **Spring** rồi chốt Phase A bằng nhịp test tiếp theo?
