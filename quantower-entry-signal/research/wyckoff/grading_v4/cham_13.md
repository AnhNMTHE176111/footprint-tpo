# Chấm bài #13 — Phân phối (DIST) · 2026-05-14 04:32 → 14:07 (361 nến M1)

**Điểm: 4/10** — Bài tốt nhất trong lô: Phase A đọc chuẩn, tên range đúng, SOW là cú phá thật. Chỉ cần sửa nhãn: bỏ "UTAD", gộp lại Phase B, và tính lại biên phụ dưới.

## Lỗi (nặng → nhẹ)

### 1. Gọi UTAD cho một cú vượt đỉnh giữa Phase B — luật vi phạm: THEORY §4.1/§4.2 (UTAD chỉ ở Phase C) + lỗi kinh điển CHART_CASES 4.pdf Ca #1/#3/#4 (lặp 3/5 ca)
- **Thuật toán gắn:** UTAD (thất bại) tại 4757.7, 07:37.
- **Đúng phải là:** **UT** (Upthrust trong Phase B). UTAD là cú test **cuối cùng** phá đỉnh ngay trước khi cấu trúc sụp thật. Ở đây sau nó còn **111 nến Phase B** nữa, giá còn hồi lên 4751.0 lần thứ hai (12:43) rồi mới sụp lúc 13:42 — tức "sau đỉnh vẫn còn dao động hồi lại trong range" = tiêu chí loại UTAD mà giảng viên nêu tường minh ở Ca #4 (4.pdf).
- **Dấu hiệu quyết định trên chart:** giữa nhãn UTAD (07:37) và SOW (13:42) là một dải Phase B 111 nến với hai lần giá bò lại lên vùng 4745–4751.
- **Nghi phạm trong thuật toán:** mục 5.1 gán nhãn theo **origin + độ sâu tức thời** (origin BCLX + thăm dò > 15 tick ⇒ UTAD). Sai vì UTAD là nhãn **hồi tố**: chỉ được đặt sau khi biết SOW nào là SOW thật. Đúng cách là gán UT trước, rồi khi có SOW mới nâng cấp cú rũ **cuối cùng** trước đó thành UTAD.

### 2. Nhãn đặt lên nến rỗng, không phải cây nỗ lực — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** nến 07:37 = **O=H=L=C=4757.7, volume 2 lot, VSA 0.65x**.
- **Đúng phải là:** cây tạo cú đẩy là 07:35 (VSA **2.76x**, 4752.6→4755.7), và cây bán trả lại là 07:41 (VSA **7.35x**). Máy chấm đúng vào nến doji nằm giữa hai cây đó chỉ vì nó có `high` cao nhất.
- **Dấu hiệu quyết định trên chart:** thanh volume tại 07:37 gần như không thấy, còn thanh vàng cao nhất vùng đó nằm ở 07:41.
- **Nghi phạm trong thuật toán:** điểm sự kiện lấy theo `argmax(high)` / `argmin(low)` thuần. Nên chọn nến có VSA lớn nhất trong cụm ±3 nến quanh cực trị.

### 3. Phase C 121 nến cắt Phase B làm hai — luật vi phạm: L8 (Phase C NGẮN NHẤT), L9 (Phase B DÀI NHẤT)
- **Thuật toán gắn:** A 71n → B 33n → **C 121n** → B 111n → D 26n.
- **Đúng phải là:** một Phase B liền mạch 06:47 → 13:41 (**265 nến**, phase dài nhất), Phase C rất ngắn ngay trước SOW. Con số 121 nến chính là trần chờ 120 nến rồi timeout — theo L8 thì tự động không còn là Phase C.
- **Dấu hiệu quyết định trên chart:** hai nhãn "Phase B (33n)" và "Phase B (111n)" nằm hai bên một khối Phase C mà bên trong khối đó giá không hề rời range (lo 4730.2 / hi 4757.7).
- **Nghi phạm trong thuật toán:** mục 6 vào Phase C ngay khi thấy cú rũ, rồi timeout 120 nến. Nên chỉ **vẽ** Phase C sau khi SOS/SOW đã xuất hiện (đúng như case khó ở mục 6), không vẽ trước.

### 4. Biên phụ dưới 4723.7 không phải cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới = 4723.7 (điểm DA, 13:31).
- **Đúng phải là:** **4712.2** (13:41), thấp hơn 11.5 giá và xảy ra **trước** SOW. Sai 11.5 giá ≈ 50% chiều cao biên chính.
- **Dấu hiệu quyết định trên chart:** cụm nến đỏ quanh 13:31–13:41 xuyên hẳn xuống dưới nét đứt 4723.7.
- **Nghi phạm trong thuật toán:** biên phụ chỉ được nới ở nến sinh ra nhãn UA/UT/DA (mỗi bên giữ 1 nhãn), không nới theo mọi nến thò ra. Đây là cùng một lỗi với bài #12 nhưng nhẹ hơn.

### 5. BCLX không hẳn là đỉnh — luật vi phạm: L1 (climax là cực trị chặn move) — mức độ nhẹ
- **Thuật toán gắn:** BCLX 4752.0 (04:32).
- **Đúng phải là:** 4 nến sau đó giá còn lên 4753.0 (04:36). Lệch **1.0 giá** trên nền biên chính 23.2 giá — nhẹ, không làm sai cấu trúc, nhưng cùng họ với lỗi nặng ở bài #11/#12/#14 nên ghi lại để thấy tính hệ thống.

## Đạt
- **Điều kiện mở range chuẩn nhất lô:** MOVE tăng 44.0 giá / 20 nến / hiệu suất **0.86** — đi thẳng một mạch, đúng tinh thần L1; và BCLX là đỉnh của cả cửa sổ 240 nến nhìn lại.
- **Phase A đọc đúng L2 trọn vẹn:** BCLX (2.33x) → AR 4728.8 (2.67x, thân 0.96, hồi 53% độ dài move) → ST[A] 4743.9 với VSA **0.64x** co lại rõ. Đủ 3 lần đổi hướng, kết thúc đúng tại ST[A].
- Vị trí ST[A] ở 65% chiều cao range (1/3 nửa trên) — theo THEORY §5 là "phe mua còn mạnh", khớp với việc range còn kéo thêm 7 giờ trước khi sụp.
- **SOW là cú phá thật:** 13:42, VSA 4.04x, đóng cửa 4710.0 — bứt qua cả biên phụ đã ghi (4723.7) và cả cực trị thật (4712.2).
- Tên range đúng L4: origin BCLX + phá xuống = Phân phối.
- DA gán đúng vai (thăm dò cạnh AR, không quyết định) và chỉ giữ 1 nhãn mỗi bên — đúng L3/L6.

## Trình bày
- Nhãn **DA** che mất chữ số của "bien CHINH duoi 4728.8" ở lề phải chart. Lỗi trình bày, không phải cấu trúc.

## Cần hỏi người học
- Không có. Lý thuyết đủ phân xử mọi điểm trong bài này.
