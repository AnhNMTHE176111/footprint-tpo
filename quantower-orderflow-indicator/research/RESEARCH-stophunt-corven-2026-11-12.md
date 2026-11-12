# Stop hunt theo định nghĩa của CORVEN: bản mẫu Python (2026-11-12)

**Kết luận ngắn** (pp = điểm phần trăm). Stop hunt kiểu CORVEN (quét mốc quan trọng + nổ bubble + fail break) **chưa có lợi thế để làm lệnh tự động**: sau phí 1 tick, kỳ vọng mỗi lệnh vẫn âm ở gần như mọi biến thể. Nhưng có một phát hiện thật: **fail break có bubble thì đảo chiều, fail break không có bubble thì đi tiếp theo hướng phá** (ví dụ range 60 nến: 56,0% đảo chiều so với 43,4%, chênh 12,6 điểm phần trăm, z = 3,8, cùng dấu ở cả hai nửa kỳ). Vì vậy nên port sang C# như **dấu đánh dấu để đọc chart**, không code thành tín hiệu vào lệnh.

Script chạy lại được: `research/stophunt_corven.py`.

## 1. Định nghĩa đã kiểm theo lời CORVEN

Nguồn: `corven-meet/2026-11-07/transcript.md`, mục 4 (0:07:47), mục 8 (0:22:41), mục 9 (0:23:45), mục 15 (0:46:03), mục 23 (1:04:00).

- Stop hunt là quét SL. Giá **quét qua một đỉnh/đáy quan trọng** (cạnh range, mốc có nhiều phản ứng, điểm cấu trúc) **mà nổ bubble** thì mới là stop hunt (0:23:45).
- Ở đỉnh, SL của bên sell là lệnh buy-stop, nên bubble có thể xanh, đỏ hoặc tím (0:24:34; ví dụ 0:22:41 là chùm bubble tím và một bubble đỏ trên râu nến).
- Fail break: phá range chỉ tính khi **nến đóng cửa**, chỉ có râu thì là fail (1:04:00, 0:43:53). Có thể chờ 1 đến 2 nến xem giá có giữ được trong range không (0:08:46).

## 2. Phương pháp

Dữ liệu: `fp_GCZ26_XCEC_Time_20260811-20261109_90d` (87.362 nến M1, một hợp đồng GCZ26 nên **không có chỗ nối hợp đồng**; giờ UTC). Mọi cửa sổ trượt qua chỗ thiếu dữ liệu (nghỉ cuối tuần, nghỉ 1 giờ) đều bị loại khỏi phần đo kết quả.

Luật bubble: đúng luật `CellBigLogic` hiện tại. Hàng 2 tick pha 1; bubble khi max(Bid, Ask) của hàng ≥ 1,3 × B và ≥ 9; B là trung bình 20 nến đóng trước của "khối lượng trung bình mỗi hàng có giao dịch". Tím khi bên yếu cũng ≥ 1,3 × B và ≥ 3; còn lại xanh (Ask trội) hoặc đỏ (Bid trội). Tâm bubble nằm ở giữa hàng.

Một đoạn mã dùng chung cho đỉnh và đáy: với đáy, đảo dấu giá rồi xử lý như đỉnh.

**Mốc quan trọng** (mọi mốc đều tính nhân quả, chỉ dùng dữ liệu trước nến đang xét):

| Mã | Mô tả | Tham số thử |
|---|---|---|
| L0 | đối chứng: đỉnh cao nhất 8 nến trước (stop hunt cũ) | 8 nến |
| L1 | đỉnh xoay mạnh k nến mỗi bên (cho phép đỉnh đôi), chưa bị quét, tuổi ≥ 2k nến | k = 5, 10, 20, 40 |
| L2 | cạnh range đi ngang: hộp N nến, cao ≤ X × trung vị biên độ nến của 100 nến trước, mỗi cạnh có ≥ 2 lần chạm (cụm cách nhau ≥ 3 nến, vùng chạm 25% chiều cao hộp). Mốc = cạnh hộp | N = 20, 40, 60; X = 4, 8 |
| L3 | đỉnh/đáy phiên và ngày (UTC): Asia 22:00-07:00, London 07:00-13:00, US 13:00-22:00; ngày chạy từ 22:00 đến 22:00. L3S = phiên đang chạy (≥ 30 nến) + phiên trước; L3D = ngày đang chạy (≥ 60 nến) + ngày trước; L3P = chỉ mốc tĩnh của phiên/ngày trước (mỗi mốc chỉ tính lần quét đầu); L3U = tất cả | 4 nhóm |

**Điều kiện tín hiệu.** Nến quét: high vượt mốc ≥ 1 tick. Bubble có tâm ≥ mốc − tol × 1 tick trong chính nến quét (tol = 0 là "từ mốc trở lên"; tol = 3 cho phép 3 tick bên dưới mốc, vì ví dụ 0:22:41 có bubble nằm sát dưới mốc). Màu bubble nào cũng được. Fail break: `fb=same` là nến quét đóng ≤ mốc; `fb=next2` là một trong hai nến sau đóng ≤ mốc (vào lệnh ở nến đó). Khoảng nghỉ 5 nến giữa hai tín hiệu cùng phía. Mỗi biến thể có hai nhóm: **CÓ BÓNG** và **KHÔNG BÓNG** (đối chứng: quét + fail break y hệt nhưng không có bubble). Tổng 15 nguồn mốc × 2 kiểu fail break × 2 mức tol = **60 biến thể**.

**Kết quả đo.**
(a) Đảo chiều trước: rào đối xứng ±1 × trung vị biên độ 100 nến, trong 20 nến; so với cơ sở của mọi nến cùng phía và cùng nửa kỳ (khoảng 50%). Chạm hai rào trong cùng nến tính 0,5; không chạm rào nào thì bỏ.
(b) E[R]: vào ở close nến tín hiệu, SL = cực trị của nến quét ± 1 tick, TP = 2R, hết hạn sau 60 nến (đóng ở close), nếu cùng nến chạm cả SL và TP thì tính SL. Phí khứ hồi 0 / 1 / 2 tick trừ vào mỗi lệnh.
(c) Chống quá khớp: nửa 1 là trước 2026-09-25 (34 ngày), nửa 2 từ ngày đó (31 ngày). Chọn biến thể chỉ trên nửa 1, rồi báo nửa 2. Báo riêng đỉnh và đáy. Có **hai cách chọn đã khai báo trước khi xem nửa 2**: A = t lớn nhất của E[R] ở phí 1 tick (n ≥ 40); B = z đảo chiều lớn nhất (n đảo chiều ≥ 100).

Giới hạn: 65 ngày, một hợp đồng; 60 biến thể nên có thể xuất hiện "đẹp" do ngẫu nhiên (các biến thể lại tương quan mạnh, nên số phép thử độc lập thấp hơn 60); các tín hiệu cách nhau 5 nến vẫn chồng lấn một phần nên sai số chuẩn hơi nhỏ quá.

## 3. Ví dụ CORVEN làm đáp án

Toạ độ ảnh đổi sang (giờ UTC, giá) bằng `calib.json` đã dùng ở các lần so bubble trước; kiểm lại bằng delta trong dữ liệu. Frame 0:09:42 là chart NQ (Nasdaq), không phải vàng, nên **loại**.

| Mã | Mô tả (nguồn) | Nến trong dữ liệu | Độ chắc |
|---|---|---|---|
| GT1 | 0:22:41 quét cạnh trên range ~4090, chùm bubble tím + 1 đỏ (zoom 0-22-52, 0-24-15). Delta trên chart -11/-14/-18 khớp dữ liệu -13/-12/-18 | 06/11 09:20-09:22, high 4090,3 / 4090,7 / 4090,3 | rõ |
| GT2 | 0:46:03 "stop hunt có bóng đỏ" ở cạnh dưới range ~4108,5 (0-46-05) | 05/11 20:43-20:47, nến 20:45 low 4108,0, bubble đỏ tâm 4108,55 | vừa |
| GT3 | 0:27:36-59 nến to quét buy-SL (-96) rồi đảo lên (0-28-00) | 06/11 08:49-08:52, nến 08:51 low 4078,9, bubble đỏ | yếu (mốc là đường xu hướng, không phải mức ngang) |
| GT4a-d | 1:04:25 "range cho stop hunt, râu nhú xuống" ở cạnh dưới range ~4143 (1-04-00) | 05/11 11:26, 11:29, 11:39, 11:54 | yếu (mốc là hộp CORVEN vẽ tay) |

Kết quả bắt được (cột HIT = số biến thể có tín hiệu CÓ BÓNG đúng phía trong cửa sổ; số trên 60 biến thể):

| Ví dụ | HIT | Biến thể bắt được | Vì sao các biến thể khác hụt |
|---|---|---|---|
| GT1 | 14/60 | L0; L1 k=5; L2 N=20 (X=4 và 8); L3S; L3U (tất cả với tol=3, riêng L0 cả tol=0) | 40 biến thể không có mốc bị quét. 8 biến thể có quét + fail break nhưng bubble (tâm 4090,15) nằm dưới mốc 4090,3 (cần tol lớn hơn 0). Hộp N=60 quá rộng vì chứa cả đoạn tăng trước đó |
| GT2 | 14/60 | L0; L1 k=5 (tol=3); L2 N=20 X=8 và N=40 X=8 (cả tol=0 và 3) | các nguồn khác không có mốc bị quét ở đó |
| GT3 | 3/60 | chỉ L0 | không có mức ngang nào bị quét (đúng bản chất: CORVEN nói về đường xu hướng) |
| GT4a | 2/60 | chỉ L0 (tol=3) | nến quét 11:26 không có bubble theo luật; bubble chỉ ở nến sau |
| GT4b | 0/60 | không | giá không đóng lại dưới mốc (không fail break) hoặc không có mốc |
| GT4c | 2/60 | chỉ L0 next2 | như trên |
| GT4d | 0/60 | không | không có mốc quan trọng nào bị quét |

Đọc kết quả: ví dụ rõ nhất (GT1, GT2) được bắt bởi mốc kiểu range (L2 N=20, N=40) và một phần bởi L1 k=5, L3S, L3U. Ba ví dụ yếu còn lại hầu như chỉ L0 bắt được, mà L0 bắt cả ~80 tín hiệu mỗi ngày nên "bắt được" không nói lên gì. Cần nhớ đáp án này tự trích từ ảnh nên có sai số vài tick và vài nến.

## 4. Kết quả

Cơ sở đảo chiều trước của mọi nến: đỉnh 50,8% / 51,5%, đáy 49,2% / 48,5% (nửa 1 / nửa 2).

### 4.1 Tín hiệu mỗi ngày, đảo chiều, E[R]

Mỗi ô: `n / (đảo chiều − cơ sở) tính bằng điểm phần trăm / E[R] ở phí 1 tick`. Cột cuối = đảo chiều CÓ BÓNG − KHÔNG BÓNG trên cả kỳ. Gộp đỉnh và đáy.

| biến thể | /ngày | CÓ BÓNG nửa 1 | CÓ BÓNG nửa 2 | KHÔNG BÓNG nửa 1 | KHÔNG BÓNG nửa 2 | chênh đảo chiều cả kỳ (pp) |
|---|---|---|---|---|---|---|
| L0 swing8, fb=next2, tol=0 | 98.3 | 3318 / -0.9 / -0.12 | 3069 / -0.6 / -0.10 | 4056 / +0.0 / -0.13 | 3987 / -0.1 / -0.17 | -0.7 |
| L0 swing8, fb=next2, tol=3 | 115.2 | 3853 / -0.4 / -0.12 | 3638 / -0.0 / -0.09 | 3530 / -0.3 / -0.14 | 3456 / -0.1 / -0.17 | -0.1 |
| L0 swing8, fb=same, tol=0 | 62.8 | 2126 / -1.0 / -0.13 | 1957 / +0.4 / -0.13 | 3464 / -0.5 / -0.14 | 3431 / +0.0 / -0.18 | -0.1 |
| L0 swing8, fb=same, tol=3 | 82.0 | 2707 / -0.8 / -0.15 | 2620 / +0.9 / -0.12 | 2942 / -0.7 / -0.14 | 2881 / -0.5 / -0.20 | +0.6 |
| L1 pivot k=10, fb=next2, tol=0 | 19.2 | 679 / +0.0 / -0.14 | 570 / +1.1 / -0.08 | 443 / -3.8 / -0.30 | 506 / +0.2 / -0.18 | +2.1 |
| L1 pivot k=10, fb=next2, tol=3 | 23.1 | 790 / +0.2 / -0.15 | 710 / +1.2 / -0.09 | 317 / -6.1 / -0.35 | 357 / +0.1 / -0.20 | +3.5 |
| L1 pivot k=10, fb=same, tol=0 | 12.3 | 437 / -0.7 / -0.13 | 362 / +1.0 / -0.09 | 367 / -2.2 / -0.28 | 427 / +0.5 / -0.19 | +0.8 |
| L1 pivot k=10, fb=same, tol=3 | 15.9 | 543 / -0.9 / -0.16 | 489 / +1.2 / -0.10 | 253 / -3.7 / -0.32 | 291 / +0.1 / -0.21 | +1.8 |
| L1 pivot k=20, fb=next2, tol=0 | 11.1 | 377 / +0.3 / -0.17 | 342 / -0.4 / -0.12 | 190 / -8.1 / -0.32 | 227 / +3.1 / -0.19 | +1.9 |
| L1 pivot k=20, fb=next2, tol=3 | 12.9 | 431 / -0.4 / -0.18 | 410 / +1.3 / -0.15 | 126 / -10.9 / -0.34 | 152 / +0.8 / -0.14 | +4.9 |
| L1 pivot k=20, fb=same, tol=0 | 7.3 | 244 / -2.9 / -0.22 | 228 / -0.8 / -0.10 | 155 / -6.3 / -0.33 | 197 / +3.3 / -0.22 | -1.1 |
| L1 pivot k=20, fb=same, tol=3 | 9.1 | 294 / -2.9 / -0.24 | 296 / +1.4 / -0.15 | 98 / -8.9 / -0.33 | 126 / -0.7 / -0.19 | +3.5 |
| L1 pivot k=40, fb=next2, tol=0 | 6.3 | 225 / +2.1 / -0.13 | 186 / +3.6 / -0.02 | 72 / -12.9 / -0.50 | 97 / +5.7 / -0.11 | +4.8 |
| L1 pivot k=40, fb=next2, tol=3 | 7.1 | 248 / +1.1 / -0.19 | 215 / +5.2 / -0.03 | 45 / -18.4 / -0.47 | 64 / +0.2 / -0.12 | +10.3 |
| L1 pivot k=40, fb=same, tol=0 | 4.2 | 147 / +2.5 / -0.16 | 124 / -0.8 / -0.02 | 57 / -7.3 / -0.54 | 82 / +7.3 / -0.13 | -0.5 |
| L1 pivot k=40, fb=same, tol=3 | 5.0 | 170 / +1.5 / -0.22 | 152 / +2.6 / -0.02 | 33 / -11.1 / -0.47 | 50 / +0.2 / -0.16 | +6.3 |
| L1 pivot k=5, fb=next2, tol=0 | 32.6 | 1135 / +0.5 / -0.14 | 985 / +0.5 / -0.11 | 1011 / -3.4 / -0.22 | 1099 / -1.4 / -0.22 | +2.8 |
| L1 pivot k=5, fb=next2, tol=3 | 40.5 | 1367 / +0.9 / -0.14 | 1267 / +0.5 / -0.13 | 758 / -5.6 / -0.23 | 805 / -0.6 / -0.21 | +3.7 |
| L1 pivot k=5, fb=same, tol=0 | 20.8 | 732 / +0.5 / -0.13 | 621 / +0.3 / -0.12 | 845 / -2.4 / -0.19 | 921 / -1.4 / -0.26 | +2.3 |
| L1 pivot k=5, fb=same, tol=3 | 28.3 | 953 / +0.6 / -0.16 | 884 / +0.3 / -0.13 | 616 / -3.9 / -0.19 | 656 / -1.7 / -0.27 | +3.3 |
| L2 range N=20 X=4, fb=next2, tol=0 | 9.4 | 311 / +0.3 / -0.20 | 302 / +3.1 / -0.01 | 393 / -1.0 / -0.17 | 375 / +0.9 / -0.17 | +1.9 |
| L2 range N=20 X=4, fb=next2, tol=3 | 11.6 | 382 / -0.7 / -0.20 | 371 / +4.5 / +0.00 | 325 / +0.0 / -0.11 | 307 / -0.3 / -0.17 | +2.1 |
| L2 range N=20 X=4, fb=same, tol=0 | 5.5 | 181 / +1.1 / -0.28 | 178 / +7.6 / +0.05 | 325 / +1.3 / -0.17 | 310 / +0.1 / -0.16 | +3.7 |
| L2 range N=20 X=4, fb=same, tol=3 | 7.8 | 256 / -0.4 / -0.31 | 248 / +8.8 / +0.05 | 258 / +3.6 / -0.07 | 245 / -2.7 / -0.18 | +3.7 |
| L2 range N=20 X=8, fb=next2, tol=0 | 17.4 | 576 / +1.8 / -0.10 | 554 / +2.3 / -0.07 | 645 / -1.7 / -0.19 | 669 / -0.4 / -0.19 | +3.1 |
| L2 range N=20 X=8, fb=next2, tol=3 | 21.0 | 693 / -0.3 / -0.14 | 675 / +3.3 / -0.07 | 529 / -2.0 / -0.16 | 548 / -1.3 / -0.18 | +3.3 |
| L2 range N=20 X=8, fb=same, tol=0 | 10.7 | 347 / +3.7 / -0.07 | 350 / +4.2 / -0.07 | 539 / -0.6 / -0.20 | 544 / -0.5 / -0.19 | +4.5 |
| L2 range N=20 X=8, fb=same, tol=3 | 14.5 | 466 / +1.0 / -0.16 | 474 / +5.7 / -0.05 | 429 / -0.1 / -0.15 | 431 / -3.2 / -0.23 | +5.1 |
| L2 range N=40 X=4, fb=next2, tol=0 | 1.5 | 51 / -5.9 / -0.23 | 46 / -2.0 / -0.11 | 45 / -1.2 / -0.43 | 63 / +17.3 / +0.40 | -14.2 |
| L2 range N=40 X=4, fb=next2, tol=3 | 2.0 | 60 / -1.6 / -0.19 | 68 / +7.5 / +0.13 | 35 / -9.9 / -0.42 | 42 / +10.1 / +0.23 | +1.7 |
| L2 range N=40 X=4, fb=same, tol=0 | 0.9 | 34 / -7.6 / -0.10 | 25 / +2.5 / -0.27 | 37 / +0.2 / -0.47 | 52 / +18.1 / +0.36 | -14.4 |
| L2 range N=40 X=4, fb=same, tol=3 | 1.4 | 43 / -1.1 / -0.15 | 45 / +10.2 / +0.07 | 28 / -8.1 / -0.39 | 32 / +16.9 / +0.28 | -0.9 |
| L2 range N=40 X=8, fb=next2, tol=0 | 15.5 | 527 / -0.3 / -0.12 | 480 / +0.8 / -0.14 | 484 / -1.8 / -0.12 | 483 / -1.7 / -0.20 | +2.0 |
| L2 range N=40 X=8, fb=next2, tol=3 | 18.3 | 612 / +0.0 / -0.12 | 579 / +0.6 / -0.13 | 387 / -2.0 / -0.11 | 378 / -1.1 / -0.18 | +1.8 |
| L2 range N=40 X=8, fb=same, tol=0 | 10.0 | 337 / -1.7 / -0.17 | 313 / +3.4 / -0.09 | 423 / -1.4 / -0.11 | 426 / -2.5 / -0.23 | +2.7 |
| L2 range N=40 X=8, fb=same, tol=3 | 13.1 | 428 / -1.2 / -0.15 | 422 / +2.4 / -0.10 | 329 / -1.4 / -0.08 | 320 / -1.8 / -0.22 | +2.2 |
| L2 range N=60 X=4, fb=next2, tol=0 | 0.1 | 3 / +16.9 / -0.04 | 2 / +0.0 / -1.10 | 4 / +0.0 / -0.33 | 5 / +9.1 / -0.54 | +4.4 |
| L2 range N=60 X=4, fb=next2, tol=3 | 0.1 | 4 / +0.4 / -0.31 | 3 / +16.2 / -1.10 | 3 / +16.4 / -0.07 | 4 / -0.7 / -0.39 | +0.0 |
| L2 range N=60 X=4, fb=same, tol=0 | 0.0 | - | - | 3 / -16.4 / -0.10 | 5 / +9.1 / -0.54 | +0.0 |
| L2 range N=60 X=4, fb=same, tol=3 | 0.1 | 2 / +0.8 / +0.41 | 2 / +0.0 / -1.07 | 2 / +0.0 / +0.42 | 4 / -0.7 / -0.39 | +0.0 |
| L2 range N=60 X=8, fb=next2, tol=0 | 10.1 | 350 / +5.2 / -0.10 | 304 / +5.6 / +0.00 | 301 / -4.9 / -0.27 | 267 / -6.9 / -0.24 | +11.2 |
| L2 range N=60 X=8, fb=next2, tol=3 | 11.8 | 413 / +3.5 / -0.16 | 356 / +3.7 / -0.03 | 228 / -3.5 / -0.18 | 207 / -5.8 / -0.19 | +8.1 |
| L2 range N=60 X=8, fb=same, tol=0 | 6.5 | 228 / +3.8 / -0.13 | 197 / +8.6 / +0.05 | 262 / -5.4 / -0.28 | 227 / -7.9 / -0.31 | +12.6 |
| L2 range N=60 X=8, fb=same, tol=3 | 8.5 | 300 / +1.7 / -0.19 | 255 / +5.5 / -0.01 | 192 / -3.4 / -0.16 | 169 / -8.3 / -0.28 | +9.1 |
| L3D ngay, fb=next2, tol=0 | 15.8 | 517 / +0.8 / -0.08 | 509 / +1.7 / -0.12 | 337 / -3.3 / -0.28 | 398 / +0.7 / -0.17 | +2.4 |
| L3D ngay, fb=next2, tol=3 | 17.4 | 565 / -0.1 / -0.12 | 565 / +2.3 / -0.12 | 265 / -5.7 / -0.32 | 315 / +0.9 / -0.20 | +3.3 |
| L3D ngay, fb=same, tol=0 | 11.1 | 366 / +2.4 / -0.05 | 357 / +1.4 / -0.16 | 311 / -2.3 / -0.29 | 350 / -0.3 / -0.18 | +3.1 |
| L3D ngay, fb=same, tol=3 | 13.2 | 430 / +2.0 / -0.10 | 429 / +2.7 / -0.12 | 237 / -4.3 / -0.33 | 268 / -1.0 / -0.25 | +4.9 |
| L3P truoc, fb=next2, tol=0 | 1.9 | 71 / +3.6 / +0.05 | 55 / +8.2 / +0.13 | 17 / +2.6 / -0.52 | 13 / -3.5 / -0.37 | +5.6 |
| L3P truoc, fb=next2, tol=3 | 2.1 | 78 / +3.2 / -0.02 | 61 / +9.0 / +0.06 | 10 / +4.5 / -0.43 | 6 / -32.8 / -0.58 | +15.1 |
| L3P truoc, fb=same, tol=0 | 1.2 | 44 / +4.5 / +0.19 | 36 / +4.0 / +0.07 | 16 / +6.0 / -0.49 | 11 / -4.4 / -0.52 | +2.5 |
| L3P truoc, fb=same, tol=3 | 1.4 | 51 / +3.9 / +0.07 | 42 / +5.8 / -0.02 | 9 / +10.7 / -0.37 | 4 / -50.0 / -1.08 | +12.5 |
| L3S phien, fb=next2, tol=0 | 23.5 | 768 / +1.1 / -0.11 | 757 / +1.7 / -0.07 | 579 / +0.1 / -0.19 | 613 / -1.0 / -0.25 | +1.8 |
| L3S phien, fb=next2, tol=3 | 26.0 | 845 / +0.7 / -0.15 | 847 / +2.7 / -0.08 | 463 / -1.0 / -0.22 | 478 / -1.4 / -0.29 | +2.9 |
| L3S phien, fb=same, tol=0 | 16.3 | 533 / +2.4 / -0.09 | 524 / +1.8 / -0.11 | 530 / +0.0 / -0.23 | 549 / -1.7 / -0.27 | +2.9 |
| L3S phien, fb=same, tol=3 | 19.5 | 637 / +2.2 / -0.12 | 633 / +2.7 / -0.12 | 408 / -0.3 / -0.24 | 418 / -3.3 / -0.33 | +4.3 |
| L3U tat ca, fb=next2, tol=0 | 23.9 | 786 / +1.3 / -0.10 | 768 / +1.8 / -0.06 | 591 / -0.4 / -0.20 | 620 / -0.8 / -0.25 | +2.1 |
| L3U tat ca, fb=next2, tol=3 | 26.5 | 862 / +0.7 / -0.14 | 859 / +2.6 / -0.07 | 473 / -1.6 / -0.23 | 487 / -1.0 / -0.27 | +3.0 |
| L3U tat ca, fb=same, tol=0 | 16.7 | 550 / +2.9 / -0.07 | 538 / +2.2 / -0.10 | 542 / -0.7 / -0.23 | 554 / -1.6 / -0.27 | +3.7 |
| L3U tat ca, fb=same, tol=3 | 20.1 | 655 / +2.5 / -0.11 | 649 / +2.8 / -0.11 | 417 / -1.1 / -0.26 | 424 / -3.0 / -0.32 | +4.7 |

### 4.2 Tách đỉnh và đáy (chỉ CÓ BÓNG)


| biến thể | ĐỈNH nửa 1 | ĐỈNH nửa 2 | ĐÁY nửa 1 | ĐÁY nửa 2 |
|---|---|---|---|---|
| L0 swing8, fb=next2, tol=0 | 1674 / -1.1 / -0.09 | 1427 / -2.7 / -0.10 | 1644 / -0.8 / -0.16 | 1642 / +1.3 / -0.10 |
| L0 swing8, fb=next2, tol=3 | 1947 / -0.5 / -0.09 | 1704 / -1.3 / -0.07 | 1906 / -0.3 / -0.15 | 1934 / +1.1 / -0.11 |
| L0 swing8, fb=same, tol=0 | 1071 / -1.1 / -0.10 | 892 / -1.6 / -0.15 | 1055 / -1.0 / -0.17 | 1065 / +2.1 / -0.12 |
| L0 swing8, fb=same, tol=3 | 1370 / -0.7 / -0.12 | 1212 / +0.6 / -0.08 | 1337 / -1.0 / -0.18 | 1408 / +1.1 / -0.15 |
| L1 pivot k=10, fb=next2, tol=0 | 329 / -4.1 / -0.20 | 271 / -1.3 / -0.09 | 350 / +4.0 / -0.08 | 299 / +3.4 / -0.06 |
| L1 pivot k=10, fb=next2, tol=3 | 380 / -3.3 / -0.21 | 345 / +0.9 / -0.06 | 410 / +3.5 / -0.09 | 365 / +1.5 / -0.13 |
| L1 pivot k=10, fb=same, tol=0 | 206 / -6.4 / -0.23 | 181 / -2.6 / -0.21 | 231 / +4.5 / -0.05 | 181 / +4.6 / +0.03 |
| L1 pivot k=10, fb=same, tol=3 | 253 / -5.1 / -0.23 | 254 / -0.1 / -0.13 | 290 / +2.9 / -0.10 | 235 / +2.6 / -0.06 |
| L1 pivot k=20, fb=next2, tol=0 | 182 / -1.6 / -0.20 | 163 / -4.9 / -0.16 | 195 / +2.1 / -0.13 | 179 / +3.7 / -0.08 |
| L1 pivot k=20, fb=next2, tol=3 | 207 / -2.2 / -0.22 | 200 / -1.0 / -0.13 | 224 / +1.2 / -0.15 | 210 / +3.4 / -0.16 |
| L1 pivot k=20, fb=same, tol=0 | 118 / -7.6 / -0.35 | 110 / -7.0 / -0.27 | 126 / +1.6 / -0.10 | 118 / +4.9 / +0.06 |
| L1 pivot k=20, fb=same, tol=3 | 140 / -6.9 / -0.35 | 148 / -1.8 / -0.21 | 154 / +0.8 / -0.15 | 148 / +4.5 / -0.08 |
| L1 pivot k=40, fb=next2, tol=0 | 100 / -1.3 / -0.31 | 89 / -1.5 / -0.04 | 125 / +4.8 / +0.02 | 97 / +8.2 / -0.01 |
| L1 pivot k=40, fb=next2, tol=3 | 116 / -2.5 / -0.35 | 107 / +1.4 / -0.05 | 132 / +4.2 / -0.05 | 108 / +8.9 / -0.01 |
| L1 pivot k=40, fb=same, tol=0 | 66 / -3.1 / -0.39 | 62 / -6.4 / -0.12 | 81 / +7.0 / +0.03 | 62 / +4.7 / +0.08 |
| L1 pivot k=40, fb=same, tol=3 | 80 / -3.3 / -0.41 | 80 / -1.5 / -0.12 | 90 / +5.8 / -0.05 | 72 / +7.0 / +0.08 |
| L1 pivot k=5, fb=next2, tol=0 | 559 / -2.9 / -0.20 | 482 / -2.0 / -0.10 | 576 / +3.7 / -0.07 | 503 / +2.9 / -0.13 |
| L1 pivot k=5, fb=next2, tol=3 | 680 / -1.7 / -0.20 | 628 / +0.1 / -0.09 | 687 / +3.4 / -0.09 | 639 / +0.9 / -0.17 |
| L1 pivot k=5, fb=same, tol=0 | 352 / -5.2 / -0.23 | 307 / -3.1 / -0.19 | 380 / +5.9 / -0.04 | 314 / +3.7 / -0.06 |
| L1 pivot k=5, fb=same, tol=3 | 465 / -3.4 / -0.24 | 451 / -0.5 / -0.14 | 488 / +4.4 / -0.09 | 433 / +1.1 / -0.13 |
| L2 range N=20 X=4, fb=next2, tol=0 | 155 / -3.4 / -0.25 | 139 / -0.0 / -0.05 | 156 / +4.0 / -0.15 | 163 / +5.9 / +0.02 |
| L2 range N=20 X=4, fb=next2, tol=3 | 188 / -3.0 / -0.23 | 175 / +3.4 / +0.03 | 194 / +1.6 / -0.16 | 196 / +5.4 / -0.02 |
| L2 range N=20 X=4, fb=same, tol=0 | 89 / -4.2 / -0.40 | 79 / +6.2 / -0.01 | 92 / +6.3 / -0.16 | 99 / +8.7 / +0.11 |
| L2 range N=20 X=4, fb=same, tol=3 | 120 / -2.9 / -0.39 | 113 / +9.8 / +0.09 | 136 / +1.9 / -0.23 | 135 / +7.9 / +0.02 |
| L2 range N=20 X=8, fb=next2, tol=0 | 281 / +0.3 / -0.06 | 255 / -0.3 / -0.09 | 295 / +3.2 / -0.14 | 299 / +4.5 / -0.06 |
| L2 range N=20 X=8, fb=next2, tol=3 | 341 / -1.1 / -0.11 | 314 / +1.9 / -0.07 | 352 / +0.5 / -0.17 | 361 / +4.6 / -0.06 |
| L2 range N=20 X=8, fb=same, tol=0 | 165 / +1.1 / -0.03 | 160 / +2.6 / -0.07 | 182 / +6.1 / -0.10 | 190 / +5.5 / -0.08 |
| L2 range N=20 X=8, fb=same, tol=3 | 221 / +0.4 / -0.12 | 218 / +5.3 / -0.02 | 245 / +1.6 / -0.20 | 256 / +6.0 / -0.07 |
| L2 range N=40 X=4, fb=next2, tol=0 | 23 / -11.6 / -0.41 | 20 / +3.5 / -0.19 | 28 / -1.1 / -0.08 | 26 / -6.2 / -0.04 |
| L2 range N=40 X=4, fb=next2, tol=3 | 26 / -8.5 / -0.26 | 31 / +9.8 / +0.04 | 34 / +3.9 / -0.14 | 37 / +5.5 / +0.20 |
| L2 range N=40 X=4, fb=same, tol=0 | 16 / -13.3 / -0.49 | 8 / +11.0 / -0.38 | 18 / -2.2 / +0.25 | 17 / -1.5 / -0.22 |
| L2 range N=40 X=4, fb=same, tol=3 | 18 / -11.9 / -0.40 | 19 / +16.9 / +0.11 | 25 / +7.3 / +0.03 | 26 / +5.3 / +0.04 |
| L2 range N=40 X=8, fb=next2, tol=0 | 253 / -2.8 / -0.15 | 217 / -5.2 / -0.19 | 274 / +2.1 / -0.09 | 263 / +5.7 / -0.11 |
| L2 range N=40 X=8, fb=next2, tol=3 | 290 / -1.3 / -0.11 | 261 / -3.6 / -0.17 | 322 / +1.3 / -0.12 | 318 / +4.0 / -0.09 |
| L2 range N=40 X=8, fb=same, tol=0 | 170 / -6.1 / -0.21 | 140 / -1.1 / -0.17 | 167 / +3.0 / -0.13 | 173 / +7.1 / -0.03 |
| L2 range N=40 X=8, fb=same, tol=3 | 205 / -3.9 / -0.17 | 190 / +0.4 / -0.14 | 223 / +1.5 / -0.13 | 232 / +4.1 / -0.06 |
| L2 range N=60 X=4, fb=next2, tol=0 | - | - | 2 / +50.8 / +0.46 | - |
| L2 range N=60 X=4, fb=next2, tol=3 | - | 2 / +48.5 / -1.14 | 3 / +17.4 / -0.07 | - |
| L2 range N=60 X=4, fb=same, tol=0 | - | - | - | - |
| L2 range N=60 X=4, fb=same, tol=3 | - | - | 2 / +0.8 / +0.41 | - |
| L2 range N=60 X=8, fb=next2, tol=0 | 170 / +2.5 / -0.11 | 141 / -0.0 / -0.20 | 180 / +7.8 / -0.08 | 163 / +10.4 / +0.18 |
| L2 range N=60 X=8, fb=next2, tol=3 | 201 / +4.7 / -0.09 | 165 / +1.0 / -0.08 | 212 / +2.2 / -0.23 | 191 / +5.9 / +0.01 |
| L2 range N=60 X=8, fb=same, tol=0 | 109 / +1.5 / -0.08 | 93 / +2.9 / -0.23 | 119 / +5.9 / -0.18 | 104 / +13.6 / +0.30 |
| L2 range N=60 X=8, fb=same, tol=3 | 144 / +4.1 / -0.06 | 116 / +5.1 / -0.07 | 156 / -0.5 / -0.30 | 139 / +5.8 / +0.05 |
| L3D ngay, fb=next2, tol=0 | 245 / -3.9 / -0.19 | 221 / -4.4 / -0.17 | 272 / +5.0 / +0.02 | 288 / +6.3 / -0.08 |
| L3D ngay, fb=next2, tol=3 | 274 / -3.9 / -0.24 | 250 / -1.7 / -0.13 | 291 / +3.5 / -0.01 | 315 / +5.4 / -0.11 |
| L3D ngay, fb=same, tol=0 | 175 / -4.5 / -0.25 | 158 / -5.9 / -0.27 | 191 / +8.7 / +0.13 | 199 / +7.3 / -0.07 |
| L3D ngay, fb=same, tol=3 | 214 / -3.6 / -0.26 | 193 / -2.3 / -0.20 | 216 / +7.5 / +0.05 | 236 / +6.8 / -0.06 |
| L3P truoc, fb=next2, tol=0 | 33 / +2.3 / -0.13 | 27 / +5.9 / +0.21 | 38 / +4.7 / +0.20 | 28 / +10.4 / +0.04 |
| L3P truoc, fb=next2, tol=3 | 37 / +0.6 / -0.23 | 30 / +10.2 / +0.29 | 41 / +5.7 / +0.18 | 31 / +7.9 / -0.16 |
| L3P truoc, fb=same, tol=0 | 23 / +3.6 / -0.13 | 20 / +6.0 / +0.08 | 21 / +5.5 / +0.54 | 16 / +1.5 / +0.07 |
| L3P truoc, fb=same, tol=3 | 27 / +1.1 / -0.27 | 23 / +11.6 / +0.19 | 24 / +7.0 / +0.46 | 19 / -1.2 / -0.27 |
| L3S phien, fb=next2, tol=0 | 362 / -2.0 / -0.16 | 329 / -3.8 / -0.09 | 406 / +3.9 / -0.07 | 428 / +5.9 / -0.05 |
| L3S phien, fb=next2, tol=3 | 406 / -1.5 / -0.20 | 372 / -1.1 / -0.07 | 439 / +2.8 / -0.09 | 475 / +5.6 / -0.09 |
| L3S phien, fb=same, tol=0 | 257 / +0.0 / -0.17 | 236 / -4.0 / -0.15 | 276 / +4.6 / -0.01 | 288 / +6.5 / -0.07 |
| L3S phien, fb=same, tol=3 | 316 / +0.3 / -0.21 | 292 / -1.5 / -0.13 | 321 / +4.1 / -0.03 | 341 / +6.2 / -0.10 |
| L3U tat ca, fb=next2, tol=0 | 371 / -2.0 / -0.18 | 332 / -3.6 / -0.08 | 415 / +4.3 / -0.03 | 436 / +5.9 / -0.05 |
| L3U tat ca, fb=next2, tol=3 | 415 / -2.0 / -0.22 | 376 / -1.1 / -0.06 | 447 / +3.1 / -0.06 | 483 / +5.5 / -0.08 |
| L3U tat ca, fb=same, tol=0 | 266 / -0.0 / -0.18 | 240 / -3.6 / -0.15 | 284 / +5.7 / +0.04 | 298 / +6.9 / -0.05 |
| L3U tat ca, fb=same, tol=3 | 327 / -0.0 / -0.22 | 297 / -1.3 / -0.14 | 328 / +4.9 / -0.00 | 352 / +6.3 / -0.08 |

### 4.3 Hai biến thể được chọn trên nửa 1, báo nửa 2

**Cách A (E[R] ở phí 1 tick, n ≥ 40): chọn L3P (mốc tĩnh phiên/ngày trước), fb=same, tol=0.** Nửa 1 có t = +0,83 nhưng chỉ n = 44. Nửa 2: n = 36, đảo chiều 54,2% (cơ sở 50,2%, z = +0,5), E[R] ở phí 1 tick = +0,07 ± 0,23. Đây là mẫu quá nhỏ, không kết luận được. Các ứng viên A kế tiếp đều có t ở nửa 1 chỉ từ +0,35 trở xuống.

**Cách B (z đảo chiều, n ≥ 100): chọn L2 range N=60, X=8, fb=next2, tol=0.**

| | n | đảo chiều (cơ sở) | E[R] phí 0 | phí 1 | phí 2 |
|---|---|---|---|---|---|
| CÓ BÓNG nửa 1 | 350 (10,3/ngày) | 55,2% (50,0%), z = +1,9 | -0,03 ± 0,08 | -0,10 ± 0,08 | -0,17 ± 0,08 |
| **CÓ BÓNG nửa 2** | 304 (9,8/ngày) | **55,5% (49,9%), z = +2,0** | +0,08 ± 0,08 | **+0,00 ± 0,08** | -0,08 ± 0,08 |
| KHÔNG BÓNG nửa 1 | 301 | 45,1% (50,0%), z = -1,7 | -0,15 | -0,27 | -0,38 |
| KHÔNG BÓNG nửa 2 | 267 | 43,0% (49,9%), z = -2,3 | -0,12 | -0,24 | -0,36 |
| Đỉnh nửa 1 / nửa 2 | 170 / 141 | 53,3% (50,8%) / 51,5% (51,5%) | -0,04 / -0,12 | -0,11 / -0,20 | -0,19 / -0,28 |
| **Đáy nửa 1 / nửa 2** | 180 / 163 | **57,1% (49,2%) / 59,0% (48,5%)** | -0,02 / +0,26 | -0,09 / +0,18 | -0,15 / +0,10 |

Gộp cả kỳ (n = 654): đảo chiều 55,3% (z = +2,7); E[R] phí 0 +0,02, phí 1 -0,05, phí 2 -0,13 (±0,06). Khi dùng rào đối xứng (cách đo (a)) thì rào trung bình khoảng 19 tick: lãi gộp ước tính khoảng +2,3 tick mỗi lệnh, còn khoảng +1,3 tick sau phí 1 tick và +0,3 tick sau phí 2 tick. Đó là con số trên giấy; chưa tính trượt giá và chưa kiểm thử bằng lệnh thật.

Điểm đáng chú ý: phía **đáy** đảo chiều rõ hơn phía đỉnh và đúng ở cả hai nửa; phía đỉnh gần như bằng cơ sở. Ở nửa 2, đáy có E[R] +0,18 ở phí 1 tick, nhưng nửa 1 lại -0,09, nên **không đủ để tin**.

### 4.4 Bubble có thật sự quyết định không (CÓ BÓNG so với KHÔNG BÓNG)

Đây là kết quả mạnh nhất. Trên gần như mọi nguồn mốc "sạch" (L1 nhỏ, L2, L3), CÓ BÓNG đảo chiều nhiều hơn KHÔNG BÓNG, còn KHÔNG BÓNG thường **thấp hơn cơ sở** (tức là phá giả mà không có bubble thường đi tiếp theo hướng phá):

| Nguồn mốc (fb, tol) | CÓ BÓNG | KHÔNG BÓNG | chênh đảo chiều | chênh E[R] (phí 0, trừ khi ghi khác) |
|---|---|---|---|---|
| L2 N=60 X=8 (same, 0) | 56,0%, n=425 | 43,4%, n=489 | +12,6 pp, z = 3,8 | +0,21 (t = 2,3) |
| L2 N=60 X=8 (next2, 0) | 55,3%, n=654 | 44,1%, n=568 | +11,2 pp, z = 3,9 | +0,16 (t = 2,0) |
| L3U (same, 3) | 52,6%, n=1304 | 47,9%, n=841 | +4,7 pp, z = 2,1 | +0,15 (t = 2,5) |
| L1 k=5 (next2, 3) | 50,7%, n=2634 | 47,0% | +3,7 pp, z = 2,3 | +0,08 ở phí 1 (t = 1,9) |
| L0 swing 8 nến (same, 0) | 49,6%, n=4083 | 49,7% | -0,1 pp, z = -0,1 | +0,03 ở phí 1 (không đáng kể) |

Với 60 biến thể, z = 3,8 vẫn vượt ngưỡng hiệu chỉnh (khoảng 3,3 cho 60 phép thử độc lập). Phần "KHÔNG BÓNG đi tiếp" là phát hiện chỉ dùng được để **tránh vào ngược** (nếu thấy fail break mà không có bubble thì đừng đánh ngược), chứ chưa phải lợi thế để vào theo hướng phá: phí ăn hết.

**Màu bubble.** Ở biến thể cách B, gộp cả kỳ: có bubble tím n = 245, E[R] phí 1 = -0,09 ± 0,09; không có tím n = 405, E[R] = -0,03 ± 0,07. Không có khác biệt đáng kể, phù hợp với việc CORVEN không phân biệt màu ở ví dụ stop hunt.

### 4.5 Đối chứng cũ L0 (swing 8 nến)

Không có lợi thế, giống kết luận ngày 2026-09-10: đảo chiều 49,2% đến 50,0% (cơ sở 50,0%), E[R] phí 1 tick từ -0,11 đến -0,13 với t khoảng -6, và có tới 60 đến 115 tín hiệu mỗi ngày nên không còn là "mốc quan trọng". Bubble không tách được gì ở L0 (CÓ BÓNG bằng KHÔNG BÓNG).

## 5. Kết luận

1. **Mốc quan trọng thật sự là điều làm bubble có nghĩa.** Với swing 8 nến, bubble không phân biệt được gì. Với cạnh range (L2) và đỉnh/đáy phiên-ngày (L3), bubble tách rõ fail break "thật" (đảo chiều) khỏi fail break "giả" (đi tiếp). Đúng tinh thần CORVEN: quét SL ở mốc quan trọng mà nổ bubble.
2. **Chưa có lợi thế giao dịch.** Mọi biến thể đều có E[R] ≤ 0 ở phí 1 đến 2 tick; biến thể chọn theo cách B hòa vốn ở phí 1 tick nửa 2 nhưng âm nửa 1. Không code thành tín hiệu vào lệnh.
3. **Nên port như dấu đánh dấu đọc chart**, để người học thấy "chỗ có nhiều SL bị quét + bubble + fail break". Nó cũng dùng được như bộ lọc cảnh báo: fail break không có bubble ở cạnh range thì khả năng giá đi tiếp theo hướng phá cao hơn.
4. **Nguồn mốc nên port:** L2 (cạnh range) là nguồn thống kê mạnh nhất và đúng cách CORVEN nói ("quanh cạnh range bên trên một tí"). L3U là lớp bổ sung ổn định (cùng dấu ở cả hai nửa) và bắt được ví dụ GT1. Hộp N=60 X=8 mạnh nhất về thống kê nhưng hụt GT1, vì chiều cao hộp tính cả đoạn đi lên trước đó; hộp N=20 X=8 bắt được GT1 và GT2 nhưng yếu hơn về thống kê (đảo chiều 53,3% đến 53,8%, z khoảng 2,1; chênh +4,5 đến +5,1 pp).
5. Điều chưa biết: phần lớn ví dụ làm đáp án tự trích từ ảnh nên sai số lớn; mẫu chỉ 65 ngày; chưa thử trên dữ liệu ngoài kỳ này (đề xuất xuất thêm 90 ngày GC trước tháng 8 rồi chạy lại đúng script).

## 6. Đặc tả thuật toán đề xuất để port sang C#

Chỉ dùng để vẽ dấu đánh dấu, không phát lệnh.

- **Bubble:** dùng thẳng `CellBigLogic` hiện tại (hàng 2 tick pha 1, ≥ 1,3 × B và ≥ 9, B = trung bình 20 nến đóng trước; tâm bubble ở giữa hàng).
- **Mốc L2 (chính):** tại nến i, xét 60 nến đóng trước đó (i-60 đến i-1), phải liên tục (thời gian trải ≤ 90 phút). `top` = high cao nhất, `bot` = low thấp nhất. Hộp hợp lệ khi `(top - bot) <= 8 x trung vị(high - low) của 100 nến đóng trước` và cả hai cạnh có ≥ 2 lần chạm. Một lần chạm là cụm nến có high ≥ `top - 0,25 x (top - bot)` (với cạnh dưới: low ≤ `bot + 0,25 x (top - bot)`), hai cụm cách nhau ≥ 3 nến. Mốc đỉnh = `top`, mốc đáy = `bot`.
- **Mốc L3 (bổ sung):** đỉnh/đáy phiên đang chạy (ít nhất 30 nến trong phiên), đỉnh/đáy ngày đang chạy (ít nhất 60 nến), đỉnh/đáy phiên trước và ngày trước (phiên trước phải có ≥ 120 nến, ngày trước ≥ 360 nến; mốc tĩnh chỉ tính lần quét đầu). Phiên theo giờ UTC: Asia 22:00-07:00, London 07:00-13:00, US 13:00-22:00; ngày chạy 22:00 đến 22:00. Khi port nhớ cộng múi giờ: indicator chạy UTC+7.
- **Sweep (đỉnh):** `high >= mốc + 1 tick`. Với đáy đối xứng.
- **Bubble tại sweep:** trong chính nến quét có bubble (màu nào cũng được) có tâm ≥ `mốc - tol x 1 tick`. Dùng **tol = 0** cho mốc L2 (thống kê tốt nhất), **tol = 3** nếu muốn khớp ví dụ CORVEN (bubble nằm sát dưới mốc); để thành tham số.
- **Fail break:** `fb=next2`: nến quét hoặc một trong hai nến kế đóng cửa ≤ mốc (đỉnh) / ≥ mốc (đáy); đánh dấu ở nến đóng cửa đầu tiên đạt điều kiện. Mốc đã bị quét thì bỏ (mốc tĩnh) hoặc tự cập nhật (mốc đang chạy và hộp trượt).
- **Khoảng nghỉ:** không đánh dấu thêm cùng phía trong 5 nến sau một dấu.
- **Tần suất kỳ vọng:** L2 N=60 X=8 khoảng 10 dấu mỗi ngày (cả hai phía); L3U khoảng 24 dấu mỗi ngày (next2). Nếu thấy dày quá thì nâng ngưỡng chiều cao hộp hoặc chỉ giữ phía đáy.
- **Nên hiển thị thêm:** cạnh của hộp, màu bubble tại chỗ quét, và nhãn "không có bubble" khi có fail break mà không có bubble (cảnh báo đi tiếp).

## 7. Cách chạy lại

`PYTHONIOENCODING=utf-8 python research/stophunt_corven.py` (khoảng 10 giây khi đã có cache; lần đầu vài chục giây vì đọc file 78 MB). Kết quả đầy đủ in ra màn hình: bảng gộp, bảng đỉnh/đáy, so CÓ BÓNG với KHÔNG BÓNG, hai cách chọn, và bảng đáp án CORVEN. Cache nằm ở thư mục tạm của phiên.
