# Chấm bài #51 — Tái tích lũy (RE-ACC) · 2026-07-22 12:30 → 15:56 (206 nến M1)

**Điểm: 3/10** — **không nên vẽ range ở đây.** Cái gọi là "vùng cân bằng" chỉ dài 61 nến (A+B) và có hình chữ V, không có một nhịp đi ngang nào; 146 nến còn lại là D+E nằm ngoài range. Thêm nữa: thiếu hẳn Phase C dù có SOS, và nhãn BCLX đặt trước cả mốc bắt đầu range.

## Lỗi (nặng → nhẹ)

### 1. Không có giai đoạn đi ngang — climax không tạo được vùng cân bằng — luật vi phạm: L1 + THEORY §2.3 (giai đoạn 3 "đàm phán trong phạm vi cân bằng")
- **Thuật toán gắn:** range 206 nến, chiều cao biên chính 29.1 giá (0.70%).
- **Đúng phải là:** không mở range. Trên ảnh giá rơi từ 4139.5 xuống 4110.4 rồi đi **thẳng một mạch** lên 4145 — hình chữ V. Đây là một nhịp điều chỉnh trong xu hướng tăng, không phải vùng đấu giá: cung và cầu chưa hề "đàm phán" ở mức nào cả.
- **Dấu hiệu quyết định trên chart:** Phase A 32 nến + Phase B **29 nến** = 61 nến tổng thời gian giá ở trong biên, trên một range cao 29.1 giá. Giảng viên đã nhiều lần bắt lỗi "TR M1 chỉ 60-100 nến với đủ phase = nhiễu, không phải vùng đấu giá". Đối chiếu Ca #20 nguồn 7.pdf ("tái tích lũy gượng ép"): đây đúng là ca gò cấu trúc cho khớp mô hình.
- **Nghi phạm trong thuật toán:** không có ràng buộc nào giữa **chiều cao range** và **thời gian ở trong range**. Đề xuất guard: chiều cao biên chính / (ATR × √số nến A+B) — hoặc đơn giản là yêu cầu Phase B phải ≥ Phase A và ≥ Phase D+E.

### 2. Thiếu hẳn Phase C dù đã có SOS — luật vi phạm: L8 (case khó phải gán ngược Phase C)
- **Thuật toán gắn:** dải phase A(32) → B(29) → **D**(25) → E(121). Không có Phase C.
- **Đúng phải là:** spec mục 6 case KHÓ đã chốt: khi SOS bắn ra mà range chưa từng có Phase C thì nhìn ngược ≤60 nến lấy nhịp test cuối làm LPS[C], và Phase C bắt đầu từ đó. Ở đây nhánh này **không chạy**.
- **Dấu hiệu quyết định trên chart:** SOS ở 13:31, Phase B kết thúc 13:30 — Phase C dài 0 nến. Nhịp test cuối trước cú phá (đáy nhỏ quanh 13:2x, ngay dưới biên trên) là ứng viên LPS[C] hiển nhiên.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược là `min(60 nến, 1/2 độ dài Phase B)` — Phase B chỉ 29 nến nên cửa sổ co còn **14 nến**, và nếu trong 14 nến đó không có swing pivot xác nhận đủ 5 nến thì nhánh trả rỗng mà không có fallback. Cần: nếu không tìm được pivot thì lấy nến đầu tiên của nhịp đẩy cuối, chứ không được bỏ trắng Phase C.

### 3. Nhãn BCLX đặt trước mốc bắt đầu range và không nằm ở đỉnh — luật vi phạm: L3 (biên chính = *mức climax*), lỗi A của vòng chấm v4 tái phát ở dạng mới
- **Thuật toán gắn:** mức climax 4139.5 @12:30 (= mốc mở range), còn **nhãn** BCLX vẽ tại **12:20 @4134.9** — sớm hơn 10 nến, thấp hơn 4.6 giá.
- **Đúng phải là:** cơ chế v6 tách nhãn/mức là hợp lý, nhưng nhãn phải nằm **trong cụm climax** và **không được sớm hơn mốc bắt đầu range**. Trên ảnh, người đọc thấy chấm BCLX nằm giữa thân đoạn tăng, dưới đỉnh — sai thị giác nặng.
- **Dấu hiệu quyết định trên chart:** header ghi `climax ... tai gia 4139.5, VSA=1.79x` còn bảng sự kiện ghi `BCLX 12:20 4134.9 VSA=2.80x` — hai con số cho cùng một sự kiện, tự mâu thuẫn trong cùng phiếu.
- **Nghi phạm trong thuật toán:** cửa sổ chọn "cây volume cao nhất trong cụm" đang quét cả về **quá khứ** ngoài cửa sổ cụm 8 nến. Phải kẹp: `label_idx ∈ [climax_idx, climax_idx + 8]`.

### 4. ST[A] rơi giữa range, không test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** `ST[A]` @4124.6 = **49%** chiều cao range (4110.4–4139.5).
- **Đúng phải là:** ST[A] là lần thứ 3 đổi hướng, bị chặn **tại vùng climax**. Trên ảnh nhịp hồi từ AR đi thẳng tới 4139 rồi mới lùi — cái pivot 4124.6 chỉ là một cái ngọ nguậy trên đường đi lên, đúng như mô tả lỗi trong tiêu chí chấm mục 2.
- **Dấu hiệu quyết định trên chart:** nến ST[A] VSA 1.11×, thân 0.49 — không có gì chặn ở đó; giá sau đó tiếp tục lên 15 giá nữa mà không quay lại mức này.
- **Nghi phạm trong thuật toán:** ST[A] = "swing pivot đầu tiên xác nhận 5 nến + sàn 1.5× ATR" (v5 lỗi D) đang bắt pivot **quá sớm** trong một nhịp hồi liền mạch. Cần thêm điều kiện tối thiểu: ST[A] phải hồi được ≥ 2/3 chiều cao range về phía climax, hoặc phải là pivot **cuối cùng** trước khi giá đổi hướng thật.

### 5. Chỉ số nỗ lực/kết quả ghi nhãn ngược hẳn dấu hiệu — lỗi ĐO SAI BẢN CHẤT (không phải lỗi filter)
- **Thuật toán gắn:** `effort=1.17x, result=12.05, er=0.10 — vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)`.
- **Đúng phải là:** er = 0.10 nghĩa **nỗ lực nhỏ mà kết quả rất lớn** — đúng ca THEORY §6.3 "breakout không cần volume cao vì nguồn cung nổi đã thấp". Đây là dấu hiệu **mạnh**, ngược hoàn toàn với "volume nhiều kết quả ít". Đối chiếu bài #50: er=2.58 mới là hấp thụ nghi vấn.
- **Dấu hiệu quyết định trên chart:** result 12.05 (biên độ/ATR) là nhịp bung 4110→4145; nến SOS VSA 4.83×.
- **Nghi phạm trong thuật toán:** câu chú thích được in **cố định** cho mọi nhịp "cao nhất" thay vì phân nhánh theo dấu của `er` (er > ~1.5 → hấp thụ nghi vấn; er < ~0.5 → phá vỡ dễ dàng / cung cạn).

### 6. Phase E dài 121 nến = chạm trần cứng, thành phase dài nhất range — luật vi phạm: L9 (B phải là phase dài nhất)
- **Thuật toán gắn:** E = 121 nến (59% cả range), B = 29 nến.
- **Đúng phải là:** hệ quả trực tiếp của lỗi #1; nhưng cũng cho thấy giá **không** đi được 2× chiều cao (58 giá) — nó lang thang 4145–4170 rồi quay lại 4152, tức Phase E chỉ là hết giờ chứ không phải "tìm được vùng giá mới".
- **Nghi phạm trong thuật toán:** trần 120 nến của Phase E là điều kiện thoát duy nhất được dùng ở đây; nên phân biệt "E chốt vì đi đủ xa" (thành công) với "E chốt vì hết giờ" (chưa kết luận) khi hiển thị.

## Đạt
- MOVE trước climax thật: 15.6 giá / 47 nến / hiệu suất 0.50 — nhìn ảnh là đoạn tăng liền mạch 4118 → 4139.5, không phải đi ngang (L1 phần MOVE đạt).
- Tên range (L4) đúng cơ chế: BCLX + phá lên = Tái tích lũy, không mắc lỗi "phá sai hướng thì xoá range".
- Bias `+1` (chỉ chạm biên trên) đo đúng bản chất: giá không hề test lại biên dưới sau AR.
- SOT báo `none(n=0)` cả hai phía là **trung thực** — Phase B 29 nến không thể có 3 nhịp rút ngắn, không bịa số.
- SOS neo đúng cây phá thật (VSA 4.83×, thân 0.47) — lỗi B của v4 đã hết ở nhánh này.
