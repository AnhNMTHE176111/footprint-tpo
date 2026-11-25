# r1_review — Fable review vòng 1 Big Trade "lệnh cá mập" (2026-11-25)

> Kết luận: **đủ để chốt**. Thuật toán chốt = ứng viên A, `D = 5`, `R = 8`, khởi động `W = 1380`. Chi tiết cho C# ở `SPEC.md`.
> Đây là định nghĩa hiển thị, không phải lợi thế giao dịch đã kiểm định. Không bước nào dùng giá sau vòng, không lấy CORVEN làm đích.

## 1. Kiểm số độc lập

Tôi viết lại luật từ đầu trong `bw2_ref.py` (đi từng nến, không import `bw1_*`), tự tính giờ Chicago, ngày giao dịch và phiên trong `rv1_check.py`, chạy trên nhật ký gốc. Kết quả ở `out_rv1_check.txt`.

| Con số của Opus (A D5 R8, W1380) | Opus | Fable tính lại |
|---|---|---|
| Vàng M1 đoạn chọn, vòng/ngày trung vị (từng ngày) | 6,5 (4–16) | 6,5 — `[7, 5, 7, 4, 11, 16, 4, 6]` |
| Vàng M1 đoạn kiểm | 6 (1–15) | 6 — `[1, 3, 7, 2, 15, 7, 6]` |
| Vàng M1 ngưỡng trung vị Á/Âu/Mỹ, chọn · kiểm | 67/57/67 · 44/42/39 | 67/57/67 · 44/42/39 |
| NQ M1 đoạn chọn · kiểm | 6 · 14 (8–22) | 6 `[5, 7]` · 14 `[8, 22, 14]` |
| NQ M1 ngưỡng Á/Âu/Mỹ, chọn · kiểm | 75/72/72,5 · 73/75/78 | 75/72/72,5 · 73/75/78 |
| NQ M15 đoạn kiểm | 12 (8–19) | 12 `[8, 19, 12]` |
| Vàng tháng 11 (ngày phần) | 5 (1–10), ngưỡng 43/42/45 | 5 `[10, 4, 1, 5, 7]`, 43/42/45 |
| Vòng nhỏ nhất: vàng M1 · NQ M1 · vàng tháng 11 | 36 · 71 · 40 | 36 · 71 · 40 |

Mọi con số trùng. Hai bản cài đặt khác nhau (Opus: numpy + mảng theo nhật ký; Fable: Python thuần từng nến) cho cùng kết quả.

## 2. Rò rỉ tương lai và phương pháp

- **Không thấy rò rỉ.** `run_multi` gọi `nguong(i)` trước `nop(i)`; `gvec` chỉ dùng biên độ nến trước; mức 1% của T2 chỉ lấy ngày trước. Tự kiểm "xáo dữ liệu sau nến i" đạt cho mọi ứng viên. Bản của tôi cũng xét trước, nộp sau.
- **Không dùng giá sau vòng, không dùng CORVEN** ở bất kỳ tiêu chí nào: đúng.
- **Chọn tham số chỉ trên đoạn chọn:** đúng. Nhưng đoạn chọn NQ chỉ có 2 ngày đánh giá, nên chữ "R = 8 là mức duy nhất đạt T1" rất mỏng: R = 6 rớt vì 3,5 vòng/ngày (< 4), R = 10 rớt vì phiên Mỹ 6,5 (> 6). Trên vàng (8 ngày) cả R = 6, 8, 10 đều đạt T1. Đọc đúng: **R trong khoảng 6–10 đều hợp lý, 8 là điểm giữa**; không phải 8 là tối ưu.
- **Giả định Opus tự đặt** (ngày phần ≥ 400 phút cho vàng tháng 11; T3(b) không dùng để chọn; T4 tính trước khi gộp; ngưỡng D để số thực): chấp nhận, không đổi kết luận.
- **T5(a) ở M15** dùng mức 1% của nhật ký M15 (≈ 16) nên khắt khe hơn M1: đúng như Opus ghi. Không ảnh hưởng vì tôi chọn W1380 (không có vòng nào trong ngày đầu).

## 3. Áp tiêu chí viết trước

A D5 R8 [W1380], từ `out_bw1_score.csv`:

| Tiêu chí | Vàng M1 chọn · kiểm | Vàng M5 chọn · kiểm | NQ M1 chọn · kiểm | NQ M15 chọn · kiểm | Vàng tháng 11 |
|---|---|---|---|---|---|
| T1 vòng/ngày 4–12, phiên ≤ 6, ngày ≤ 40 | đạt · đạt | đạt · đạt | đạt · **rớt** (14; Mỹ 9) | đạt · **rớt** (12 đạt, Mỹ 8) | đạt |
| T2 vòng nhỏ nhất ≥ 3 lần, trung vị ≥ 5 lần mức 1% | 4,6 / 9,4 · 3,9 / 6,0 | 4,6 / 9,2 · 3,9 / 5,8 | 5,5 / 7,3 · 6,5 / 11 | 5,5 / 7,3 · 6,5 / 11 | 4,4 / 10 |
| T3(a) ngưỡng biến thiên ≤ 30% | 11% · 25% | 14% · 25% | 2% · 4% | 2% · 4% | 8% |
| T3(c) trùng giữa hai khung ≥ 85% | 92% · 98% | — | 92% · 89% | — | — |
| T4(a) lệnh lớn nhất ngày nổ 100% | 100% · 100% | 100% · 100% | 100% · 100% | 100% · 100% | 100% |
| T4(b) ba lệnh lớn nhất ≥ 85% | 100% · 86% | 100% · 86% | 100% · 100% | 100% · 100% | 87% |
| T4(c) lệnh lớn nhất phiên ≥ 80% | 86% (19/22) · 88% (15/17) | 95% · 85% | **67% (4/6)** · 89% (8/9) | **60% (3/5)** · 100% | 100% (10/10) |

Ba chỗ rớt và cách tôi phân xử:

1. **T4(c) ở NQ đoạn chọn (4/6 phiên).** Hai phiên sót đều là ngày 28/10: phiên Á lệnh lớn nhất 52, phiên Âu 50, ngưỡng 70–75. Mẫu 6 phiên không đo được mốc 80% (sót 1 là 83%, sót 2 là 67%). Gộp mọi đoạn M1: 56/64 = 87,5%, đạt. Và đây đúng là câu hỏi PLAN mục 2 đã nêu: cá mập tuyệt đối hay so với giờ đó. Người học nói rõ "big trade là phải thật sự lớn": lệnh 50 lúc ngưỡng cả tuần là 73 **không** phải thật sự lớn, không vẽ là đúng ý. **Phân xử: T4(c) tính gộp, đạt. Đây là nới sau khi thấy số, tôi ghi rõ.** Ứng viên H (ghép B) không chạy: nó thêm trạng thái theo khung giờ để vẽ thêm đúng loại vòng người học đang chê, và B đã cho thấy hệ quả (phiên Á NQ 15 vòng/ngày, vàng có vòng 20–26).
2. **T1 và T3(b) ở NQ đoạn kiểm (14 vòng/ngày, phiên Mỹ 9).** Ba ngày kiểm là 8, 22, 14 vòng; 30/10 là ngày dồn (11 lệnh ≥ 100). Không bộ tham số nào sửa được chỗ này mà không rớt đoạn chọn, và không được chỉnh theo đoạn kiểm. Luật tự kéo mật độ về R: trên vàng 15 ngày, tổng vòng chia tổng phút nến ra 6,85 vòng mỗi 1380 phút (M5: 7,05). **Phân xử: chấp nhận, ghi là rủi ro chưa đóng** — NQ tuần sôi động có thể 8–10 vòng riêng phiên Mỹ. Đo lại khi nhật ký NQ có ≥ 15 ngày đủ.
3. Ngoài ra không rớt gì. E (sàn 75) và C đạt đoạn chọn nhưng E sụp ngoài mẫu (sót lệnh lớn nhất ngày) và cần hằng số theo mã; C rớt T2 ở vàng tháng 11 và nhiều tham số hơn A. T6 (đơn giản) chọn A.

**Chọn D = 5:** D = 3, 5, 10 gần như cùng số ở đoạn chọn. D = 10 phản ứng chậm (vàng đoạn kiểm còn 3 vòng/ngày, có ngày 0 vòng vì ngưỡng còn nhớ tuần sôi động trước); D = 3 không lợi gì rõ. D = 5 = một tuần giao dịch, dễ giải thích.

**Chọn W = 1380 (chưa đủ một ngày nến thì không vẽ):** W690 rớt T5(a) theo cả hai vế. NQ M1 mở chart mới: ngày đầu 9–15 vòng ở 5 trên 6 lần mở, vòng nhỏ nhất 34–58, trong khi mức ổn định là 6 vòng/ngày với ngưỡng 73 — đúng kiểu "dày và nhỏ" người học chê. W1380 không có vòng nào trong ngày nến đầu. Giá phải trả ở mục 5.

## 4. Thuật toán chốt

Một lệnh đơn nổ vòng khi **lớn hơn hẳn lệnh lớn thứ K** của mọi lệnh đơn trong 5 ngày nến gần nhất, với K = 8 lệnh cho mỗi ngày nến (đủ 5 ngày thì K = 40). Không sàn, không giới hạn vòng mỗi nến, không ô chọn mật độ; áp cho cả hai chế độ ngưỡng. Gộp vòng sát nhau giữ như cũ.

Ngưỡng thực tế (trung vị): vàng 57–67 hợp đồng tuần 1–11/9, 39–44 tuần 14–22/9, 42–45 tháng 11; NQ 72–78. Vòng nhỏ nhất từng vẽ: vàng 36, NQ 71 (trước đây 5–10). Đối chiếu `RESEARCH.md`: NQ "khoảng 50, ví dụ 65" (Bookmap), vàng "block từ 25" (CME), "30" (Deepcharts, Sierra) — ngưỡng đo được nằm trên các mốc đó, cùng bậc độ lớn.

## 5. Giới hạn phải nói với người học

- **Chart hoặc khung chưa có nhật ký lệnh đơn sẽ trắng vòng Big Trade cho tới khi chạy sống đủ 1380 phút nến** (nhật ký ghi riêng từng mã và từng khung). Hiện đủ: vàng M1, M5; NQ M1, M15. Chưa đủ: NQ M5 (4 nến), vàng M15, M30 tháng 11 (ngắn). Đổi hợp đồng sang tên mã mới cũng bắt đầu lại.
- **Ngưỡng trôi theo thị trường:** tuần yên, "cá mập" của vàng chỉ cần khoảng 36–40 hợp đồng. Không đặt sàn vì sàn là hằng số theo mã (E đã sụp ngoài mẫu).
- **Lệnh tròn số:** ngưỡng rơi đúng 50 thì các lệnh 50 không nổ (luật "lớn hơn hẳn").
- **NQ mới có 6 ngày đủ;** MGC, MNQ chưa có nhật ký nào. Luật không có hằng số theo mã nên tự áp được, nhưng chưa đo.
- Chưa biết `MaxOneTradeVolume` có gộp các lần khớp của một lệnh market không; lệnh bị cắt nhỏ sẽ không hiện, ngưỡng không sửa được.
- **Stop hunt đọc cả vòng Big Trade** của nến quét (`OrderFlowBubbles.cs` dòng 1427). Số vòng giảm hàng chục lần nên số stop hunt trên nến có nhật ký sẽ đổi; phải đo trước/sau khi sửa code (SPEC mục 9).

## 6. Việc đề xuất sau (không nằm trong SPEC này)

Xếp hạng theo thời gian không đổi theo khung (50 lệnh lớn nhất của M1 có mặt ở khung lớn 48/49 và 49/50). Vì vậy có thể dùng nhật ký M1 của cùng mã để làm nóng ngưỡng cho mọi khung, bỏ được cảnh trắng 23 giờ nến. Cần thiết kế và đo riêng.
