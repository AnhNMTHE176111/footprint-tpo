# Chấm bài #08 — Chưa rõ (BCLX) (DIST?) · 2026-04-17 13:13 → 20:59 (266 nến M1)

**Điểm: 4/10** — range mở đúng chỗ, Phase A/B tỷ lệ đúng, nhưng **bỏ sót hoàn toàn cú phá xuống rành rành trên chart** và nhãn BCLX bị đẩy lệch 23 giá vào giữa vùng giá. Cấu trúc phải sửa, không phải "chưa rõ".

## Lỗi (nặng → nhẹ)

### 1. Thiếu hẳn SOW / Phase C-D-E dù chart có cú phá xuống 22 giá — luật vi phạm: L10, THEORY §4.2 Phase E ("phá vỡ hỗ trợ bằng MAJOR SOW")
- **Thuật toán gắn:** chỉ có A (31 nến) + B (236 nến), range đóng ở trạng thái "Chưa rõ (BCLX)", không một nhãn phá vỡ nào (không cả mSOW).
- **Đúng phải là:** **Phân phối (DIST)** hoàn chỉnh. Từ ~19:16 giá cắt xuống dưới biên chính dưới 4909.2 và đi thẳng tới **4886.9**, tức đóng cửa **22 giá (49% chiều cao range)** dưới biên, còn thấp hơn cả biên phụ 4908.8. Đó là SOW, kèm Phase D + E.
- **Dấu hiệu quyết định trên chart:** đoạn cuối ảnh (từ 04-17 19:16 tới 20:59) là một dãy nến đỏ liên tiếp phá xuyên hai đường ngang cam ở 4909 rồi đi tiếp không hồi lại — hoàn toàn không có nến nào đóng lại trong range. Panel volume có cột vàng nổi ở đúng nhịp đó.
- **Nghi phạm trong thuật toán:** guard **khe thời gian > 4 giờ cắt range** (lỗi K). 17/04 là thứ Sáu; range bị cắt cứng ở 20:59 trước khe cuối tuần. Nhưng cú phá đã xảy ra **trước** khe, trong ~19 nến cuối, và điều kiện xác nhận cần 3 nến đóng vượt biên phụ + thân ≥45%, hoặc 40 nến. Guard cắt range chạy **trước** khi xét xác nhận, nên cú phá bị bỏ. Phải xét cú phá đang chạy trước khi cắt range vì khe, hoặc cho phép chốt SOW/SOW-pending tại nến cuối trước khe.

### 2. Nhãn BCLX rơi vào cây bật ngược, lệch 23 giá dưới mức climax — luật vi phạm: L3 (biên chính = mức climax), CHART_CASES Ca #12 (đáy đầu tiên sau BCLX là AR, không phải sự kiện climax)
- **Thuật toán gắn:** nhãn BCLX tại **13:18 / 4930.9** (VSA 5.30x), trong khi mức climax và biên chính trên = **4953.8** (nến 13:13).
- **Đúng phải là:** BCLX là nến **13:13** — high 4953.8, VSA 3.31x, thân chỉ 0.16 (râu trên rất dài) = buying climax kinh điển: giá bị đẩy vọt lên rồi bị bán ngược ngay trong nến. Nến 13:18 (O 4923.7 → C 4930.3, volume 124) nằm **5 nến sau**, ở đáy nhịp đổ, là cây bật lên — nó thuộc nhịp **AR**, không phải climax.
- **Dấu hiệu quyết định trên chart:** trên ảnh chấm đỏ "BCLX" nằm thấp hơn đường "biên CHÍNH trên 4953.8" gần một nửa chiều cao range, và nằm ở **giữa** đoạn nến đỏ đổ xuống. Một nhãn cao trào MUA nằm giữa nhịp đổ là vô nghĩa về mặt cơ chế đấu giá.
- **Nghi phạm trong thuật toán:** cơ chế v6 tách "nhãn climax = cây VSA cao nhất trong cụm" khỏi "mức climax = cực trị". Cửa sổ cụm 8 nến bao trọn cả nhịp đổ **và** nhịp bật, nên cây volume lớn nhất rơi vào cây bật ngược. Phải giới hạn: cây mang nhãn climax bắt buộc **cùng phía cực trị** (high nến đó phải trong X tick của mức climax) và **đúng màu** theo hướng move (mục 3 điều kiện 3).

### 3. Chỉ số SOT báo `none` cả hai phía trong khi chart là dãy đỉnh thấp dần rõ ràng — lỗi chỉ số, đối chiếu THEORY §7 + §4.3 (phân phối dốc xuống)
- **Thuật toán gắn:** SOT-up = none (n=0), SOT-dn = none (n=0).
- **Đúng phải là:** SOT phía TRÊN phải bắt được. Trên ảnh, chuỗi đỉnh trong Phase B đi **thấp dần**: ~4941 (13:43) → ~4938 (14:23) → ~4936 (15:08) → ~4930 (15:57) → ~4925 (17:27) → ~4919 (19:16). Đó là 5-6 nhịp rút ngắn liên tiếp — chính là dấu hiệu #1 của phân phối (cung tăng dần Phase A→D) và là bằng chứng đủ để nghiêng hướng phá xuống **trước khi** SOW xảy ra.
- **Nghi phạm trong thuật toán:** bộ dò nhịp (leg detector) của SOT chắc chắn đang yêu cầu nhịp phải **chạm biên** hoặc phải vượt một sàn biên độ quá cao, nên không nhận ra dãy đỉnh giảm dần nằm gọn trong range. Đây là chỉ số đo **sai bản chất** ở bài này.

### 4. Chỉ số bias báo `+0` (test cả hai biên) trong khi giá chưa bao giờ chạm lại biên trên — lỗi chỉ số, liên quan THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** bias = +0, tức "test CẢ HAI biên, ca thường".
- **Đúng phải là:** **-1** (chạm nổi biên dưới, không chạm nổi biên trên). Sau climax 4953.8, đỉnh cao nhất trong toàn bộ 236 nến Phase B chỉ ~4941 — thiếu 13 giá, tức **29% chiều cao range**. Giá **không đến được phía đối diện** → đúng định nghĩa cấu trúc thất bại của THEORY §9, và là tín hiệu thêm chắc chắn cho hướng giảm.
- **Nghi phạm trong thuật toán:** dung sai "chạm biên" (10 tick = 1 giá) chắc đang được nới theo chiều cao range, hoặc bias đo bằng mức **biên phụ** (4953.8 trùng biên chính trên) thay vì đo khoảng cách thật tới biên. Với range cao 44.6 giá, thiếu 13 giá vẫn bị tính là "chạm".

### 5. ST[A] chỉ hồi được 53% chiều cao range — luật vi phạm: L2 (ST[A] test lại vùng climax)
- **Thuật toán gắn:** ST[A] tại 4933.0, cách mức climax 4953.8 tới **20.8 giá**.
- **Đúng phải là:** vẫn nhận được (L2 đo bằng cấu trúc, không đo bằng %), nhưng phải ghi rõ đây là **ST[A] ở nửa trên/giữa range, không chạm được climax** — theo THEORY §5 đó là "lực bán nhất định", tức bằng chứng phân phối ngay từ Phase A. Thuật toán ghi nhận nhãn nhưng không dùng thông tin.
- **Dấu hiệu quyết định trên chart:** ST[A] VSA 1.83x (volume **không** co lại) mà giá chỉ hồi được nửa range → nỗ lực có, kết quả kém = cung đang chờ ở trên. Đúng luật Effort vs Result (THEORY §2.2).

## Đạt
- **Mục 1 (L1):** MOVE trước climax rất thật — 107.7 giá / 140 nến, hiệu suất 0.37; đường xám trên ảnh đi từ 4836 lên 4953 gần như một mạch. Climax là đỉnh cao nhất cửa sổ, đang chặn move.
- **Mục 2 (L2):** đủ 3 lần đổi hướng, và AR 4909.2 là cú bật ngược thật (44.6 giá).
- **Mục 3 (L3):** biên chính chốt đúng climax + AR và **không** bị kéo theo giá suốt 236 nến; biên phụ gần trùng biên chính (tỷ lệ 1.01x) — nghĩa là giá thật sự chưa từng thò ra ngoài trong Phase B. Vẽ trung thực.
- **Mục 5 (L9):** Phase B = 236 nến, dài nhất, gấp 7,6 lần Phase A. Đúng tỷ lệ.
- **Mục 10 phần trung thực:** không ép đặt tên pattern khi chưa xác nhận cú phá là hành vi mới đúng của v6 — vấn đề ở đây không phải "dám để chưa rõ", mà là **cú phá thật đã có mà máy không thấy**.

## Cần hỏi người học
- Khi cú phá biên đang chạy mà gặp khe cuối tuần: chốt SOW tại nến cuối trước khe (chấp nhận Phase D/E bị cắt), hay giữ nguyên "chưa rõ" như hiện tại? Bài này là ca điển hình để phân xử.
