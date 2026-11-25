# R1-KET-QUA — vòng 1 đo Big Trade "lệnh cá mập" (Opus, 2026-11-25)

> Opus chỉ báo số và nêu chỗ nghi ngờ; **không chốt thuật toán** (Fable chốt, viết `SPEC.md`).
> Đây là **định nghĩa hiển thị**, không phải lợi thế giao dịch đã kiểm định. Không bước nào dùng giá sau vòng; không dùng chart CORVEN.
> Bảng số đầy đủ (mã × khung × phiên): `r1_results.md`. Số thô: `out_bw1_grid.csv`, `out_bw1_score.csv`, `out_bw1_pick.txt`, `out_bw1_edge.txt`, `out_bw1_profile.txt`, `out_bw1_tail.csv`, `out_bw1_selftest.txt` (ĐẠT HẾT), `out_bw1_fcal.txt`.
> Script: `bw1_common.py`, `bw1_selftest.py`, `bw1_profile.py`, `bw1_rules.py`, `bw1_score.py`, `bw1_edge.py`, `bw1_report.py`. File lớn (ngưỡng + vòng mọi cấu hình, file dấu) ở thư mục tạm `scratchpad\bw1\` (`bw1_runs.pkl`, `marks_<nhật ký>.csv.gz`), không để trong repo.

## 0. Giả định đã dùng (chỗ PLAN.md chưa nói rõ)

1. **Tên file:** script theo PLAN (`bw1_*`), bảng số cụ thể thêm ở `r1_results.md` theo yêu cầu của orchestrator (cùng nội dung số với mục 3–4 dưới đây).
2. **Nạp nhật ký:** bỏ trùng `(time_ticks, price)` giữ dòng cuối; quy giá về tick `rhu(giá / cỡ tick)`; trùng tick trong một nến giữ lệnh lớn hơn (như `BigTradeLog.CellsOf`). Volume nến (ứng viên F) = tổng buy + sell của **các ô có trong nhật ký** (nhật ký chỉ ghi ô có lệnh đơn > 0, nên volume hơi thấp hơn volume thật của nến).
3. **Nhật ký NQ còn đang được ghi trong lúc đo** (đuôi ngày 25/11). Lưới chạy trên ảnh chụp lúc 08:26 (lưu trong `bw1_runs.pkl`); số ngày đủ NQ không đổi (6).
4. **Ngày đánh giá** của một dòng = ngày đủ (≥ 1170 phút nến) trong đoạn mà **mọi nến** của ngày đều đã có ngưỡng. Vì vậy chế độ "đủ D ngày" thường không còn ngày đánh giá nào ở NQ (ghi "không có ngày đánh giá" và tính là rớt).
5. **Vàng `_GCZ26` M1 không có ngày đủ nào** (449–939 phút nến mỗi ngày, ghi ngắt quãng). Dòng "ngoài mẫu" dùng các **ngày phần ≥ 400 phút nến** (9–19/11). Số vòng mỗi ngày ở đây vì thế thấp hơn bình thường; chỉ đọc như kiểm tra bậc độ lớn.
6. **Khởi động "cửa sổ lớn dần" W_min:** có ngưỡng khi phút nến tham chiếu ≥ min(W_min, phút của cửa sổ đầy). Với F, G (cửa sổ ngắn hơn W_min) điều kiện này thành "đủ cửa sổ đầy".
7. **B:** khung chính phải có ≥ 2 ngày trước (ngày < ngày nến); khung lân cận lấy tối đa D phần tử, không cần đủ; phút tham chiếu = số nến có số liệu của cả tập × m. Chưa đủ 2 ngày → dùng A cùng (D, R). Chế độ "đủ" của B = khung chính đủ D ngày.
8. **C:** `K_L = max(1, rhu(phút nến / q))`. **D:** tổng Hill lấy i = 1..k0 đúng như PLAN; ngưỡng để số thực, không làm tròn.
9. **F:** f hiệu chỉnh theo **trung bình** vòng/ngày (trung vị nhảy bậc, không tìm nhị phân được) trên đoạn chọn M1 **từng mã**, chế độ "đủ T"; giữ nguyên cho khung khác cùng mã và cho đoạn kiểm. f vàng ≈ 3 lần f NQ (`r1_results.md` mục 4) → F cần hằng số theo mã.
10. **T2:** mức 1% = giá trị lớn thứ `n // 100 + 1` của ô M1 cùng khung 30 phút Chicago, 5 ngày giao dịch trước có số liệu ở khung đó (cần ≥ 2 ngày). Nhật ký tra: `_GC_XCEC` M1 cho vàng tháng 9, `_NQZ26` M1 cho NQ, `_GCZ26` M1 cho vàng tháng 11.
11. **T3(b):** |trung vị vòng/ngày đoạn kiểm − đoạn chọn| / đoạn chọn; dòng ngoài mẫu so với đoạn chọn `_GC_XCEC` M1. **Không dùng T3(b) để chọn** (nó cần đoạn kiểm); chỉ in kèm.
12. **T3(c):** số cặp vòng trùng (cùng tick, cùng cỡ, nến M1 nằm trong nến khung lớn) / max(số vòng hai khung), trên ngày đánh giá chung.
13. **T4 "nổ"** = ô có lệnh đơn > ngưỡng nến đó. Ô bị gộp vì nằm ≤ g tick cạnh một vòng lớn hơn trong cùng nến vẫn tính là đã thể hiện (tham lam lớn trước nên mọi ô vượt ngưỡng hoặc được vẽ, hoặc nằm cạnh vòng ≥ nó). T4(c) mức 1% của phiên = lớn thứ `n // 100 + 1` của chính phiên đó trong ngày đó, cùng nhật ký.
14. **T5(a):** mô phỏng mở chart ở đầu 6 ngày giao dịch đầu tiên có ≥ 400 phút nến của mỗi nhật ký (cắt bỏ mọi thứ trước đó). "Mức 1% của ngày" lấy trên chính nhật ký đó, nên ở M15 (mức 1% ≈ 16) khắt khe hơn M1 (≈ 9).
15. **Mốc:** luật hiện tại "Không theo CORVEN" dựng lại đúng `StatBigTrade` (StatRank: cần n × 100 ≥ 50.000, lớn thứ K + 1, K = n / 100; lớn hơn hẳn; gộp g; không giới hạn). "Theo CORVEN" dựng lại `BigTradeAdaptive` mặc định (N = BarsFor(m), K = N, sàn 5, cố định 10 khi < 5 nến, chọn ≥, tối đa 3 vòng/nến, cùng g).

## 1. Số ngày đủ (đếm lại)

| Nhật ký | Ngày đủ | Ghi chú |
|---|---|---|
| `_GC_XCEC` M1, M5 | **16** (1–22/9) | chọn 1–11/9 = 9 ngày; kiểm 14–22/9 = 7 ngày (23/9 chỉ 1049 / 940 phút) |
| `_NQZ26` M1, M15 | **6** (26/10, 27/10, 28/10, 29/10, 30/10, 2/11) | đếm lại: phần ghi thêm chỉ là 24/11 (598 phút), 3/11 (61), 25/11 (64–69) — **không thêm ngày đủ nào**. Đoạn chọn có 3 ngày nhưng ngày 26/10 là ngày đầu nhật ký, chế độ lớn dần chỉ còn **2 ngày đánh giá** (27–28/10) |
| `_GCZ26` M1 | **0** | 8 ngày phần ≥ 400 phút (9–19/11); 20/11 116 phút, 23/11 19 phút, 24/11 77 phút |
| `_GCZ26` M5 / M15 / M30 | 0 | quá ngắn, chỉ dùng ở ca biên |

## 2. Hồ sơ đuôi (rút gọn từ `out_bw1_profile.txt`)

| | Vàng M1 (16 ngày) | NQ M1 (6 ngày) | Vàng tháng 11 M1 (8 ngày phần) |
|---|---|---|---|
| Phân vị 50 / 90 / 99 / 99,9 / 99,99 | 1 / 2 / 9 / 25 / 92 | 1 / 2 / 9 / 29 / 84 | 1 / 2 / 9 / 24 / 99 |
| Ô ≥ 30 mỗi ngày (nhỏ nhất / TV / lớn nhất) | 7 / 19 / 33 | 45 / 74 / 98 | 1 / 8 / 14 |
| Ô ≥ 50 mỗi ngày | 1 / 6 / 18 | 19 / 24 / 40 | 1 / 3 / 6 |
| Ô ≥ 100 mỗi ngày | 0 / 1 / 4 | 0 / 3 / 11 | 0 / 0 / 5 |
| Lệnh lớn thứ 1 / 10 mỗi ngày | 50–500 / 25–84 | 91–581 / 60–100 | 59–200 / 16–42 |
| Hill α (k0 = 100 / 200 / 500), từng đoạn 5 ngày | 1,79/1,79/2,01 · 1,65/1,81/2,03 · 2,47/2,50/2,45 | 2,51/2,33/1,97 | 2,32/2,43/2,39 · 1,97/1,99/2,17 |

- **Đuôi không có điểm gãy rõ.** α nằm trong 1,65–2,5 và đổi theo đoạn ngày (vàng 1,8 → 2,5 giữa hai tuần) và theo k0 (NQ 2,51 → 1,97). Đúng như `RESEARCH.md`: đuôi kiểu lũy thừa, mọi ngưỡng là một lựa chọn mức hiếm.
- **Lệnh tròn số có thật:** trong nhóm ≥ 25 của vàng M1, số 25 xuất hiện 52 lần trong khi hai số kề trung bình 10,5; số 50: 18 lần (kề 2,5); số 100: 8 lần (kề 2,5). NQ: 25 xuất hiện 58 lần (kề 15). Tỉ lệ tròn số 13–18%. Hệ quả: luật "lớn hơn hẳn" mà ngưỡng rơi đúng 25/50/100 sẽ loại cả cụm lệnh tròn đó.
- **Theo giờ:** mức 1% của vàng gần như phẳng cả ngày (7–10), còn lệnh lớn nhất trung vị mỗi giờ đổi 17 → 50 (đỉnh 07–10h Chicago). NQ: mức 1% phiên Á/Âu 4–6, phiên Mỹ 10–11; lệnh lớn nhất trung vị phiên Á 20–37 (riêng 19h 146 vì vài ngày dồn), phiên Mỹ 55–97.
- **So khung:** 50 lệnh lớn nhất của M1 có mặt y hệt (cùng tick, cùng cỡ) ở khung lớn: vàng M1 → M5 48/49 (1 nến không có trong nhật ký M5), NQ M1 → M15 49/50. **Xếp hạng tuyệt đối không phụ thuộc khung.**

## 3. Kết quả từng ứng viên (cấu hình tốt nhất trên đoạn chọn)

Tiêu chí chọn ở đoạn chọn: T1, T2, T3(a), T3(c), T4 trên cả 4 nhật ký `_GC_XCEC` M1/M5 và `_NQZ26` M1/M15, cùng tham số. **Không cấu hình nào đạt hết** (262 cấu hình × khởi động). Rớt ít nhất là 2 tiêu chí, và chỗ rớt luôn là **T4(c) của NQ đoạn chọn** (lệnh lớn nhất phiên Á/Âu không nổ; chỉ 4–6 phiên đủ điều kiện trên 2 ngày).

| Ứng viên | Cấu hình tốt nhất | Rớt ở đoạn chọn | Vàng M1 vòng/ngày chọn → kiểm (ngưỡng TV) | NQ M1 chọn → kiểm (ngưỡng TV) | Vàng tháng 11 | T5 (cấu hình W690) |
|---|---|---|---|---|---|---|
| **A** hạng nhiều ngày | D = 5 (hoặc 3, 10), **R = 8** | NQ M1, M15: T4(c) | 6,5 → 6 (67 → 42) | 6 → 14 (73 → 75); kiểm rớt T1 | 5/ngày phần, ngưỡng 42 | (a) W240/W690 rớt vài lần, W1380 và "đủ" đạt; (b)(c)(d)(e) đạt |
| **B** theo khung giờ | D = 5, R = 10 | vàng T2 (vòng nhỏ nhất 22 = 2,4 × mức 1%), vàng M1 T4, NQ T4 | 7,5 → 7 (46 → 34) | 6 → 23; phiên Á kiểm 15 vòng | 7 | không chạy (rớt nhiều) |
| **C** bội số lệnh lớn thường gặp | q = 15, k = 3 | NQ T4(c) | 11,5 → 6 (45 → 42) | 6,5 → 16 (69 → 72) | 5; T2 rớt (2,47) | (a) như A; (e) lệch 7% |
| **Cx** (cố ý sai: k × mức 1% của 240') | k = 5 | T3(c) cả hai mã (trùng 16–67%), NQ M1 T1 (28/ngày) | 10 → 7 | 28 → 35 | 4 | — |
| **D** ngoại suy Hill | k0 = 200, R = 10 | NQ T4(c), NQ M15 T1 | 10 → 7 (47 → 37) | 7,5 → 16 (67 → 70) | 7 | (a) rớt nhiều hơn A ở W240 |
| **E** sàn cố định | 75 (50 cho NQ quá dày: 17–29/ngày) | NQ T4(c) | 5 → **2** (T1 kiểm rớt, T4(b) kiểm 0,57) | 5 → 16 | **1**/ngày, T4(a) 0,75 | (b)(c)(d)(e) đạt |
| **F** theo volume | T = 240, mục tiêu 6 | T3(c) cả hai mã (79%, 50%), T4 cả hai mã | 5,5 → 2 | 6 → 12 | 2 | — (f vàng ≈ 3 × f NQ) |
| **G** kỷ lục trượt | T = 480, K = 2 | vàng T2 (vòng 24 = 2,9 ×), NQ T3(c) 0,81, NQ M1 T4 | 6,5 → 6 (69 → 44, cv 0,30) | 8 → 10 (70 → 94) | 4 | — |

Đọc nhanh:
- **A, C, D cho kết quả gần như nhau** trên mọi nhật ký (cùng là "xếp hạng tuyệt đối trên nhiều ngày"). Đổi D ∈ {3, 5, 10} gần như không đổi vòng ở vàng; ở NQ D = 10 không bao giờ đầy (nhật ký chỉ có ~6,5 ngày).
- **R = 8 là mức duy nhất của A đạt T1 trên đoạn chọn của cả hai mã** (R = 6: NQ chọn 3,5/ngày < 4; R = 10: NQ chọn 8 nhưng phiên Mỹ 6,5 > 6).
- Nếu **bỏ riêng T4(c)** (giữ T4(a)(b)) thì 13 cấu hình đạt hết đoạn chọn: A với R = 8 (D = 3/5/10, ba chế độ lớn dần), C q15 k3 (ba chế độ), E 75 (`out_bw1_pick.txt`, mục "Neu BO T4(c)"). Trên đoạn kiểm, không cấu hình nào trong số đó đạt cả 4 nhật ký: NQ kiểm luôn rớt T1 (trung vị 11–16 vòng/ngày, phiên Mỹ 8–10) — trừ A D=3 R=8 ở NQ M15 (9/ngày).
- **E (sàn cố định)** ổn trên đoạn chọn nhưng sụp ngoài đoạn: vàng kiểm 2 vòng/ngày, vàng tháng 11 1 vòng/ngày, sót lệnh lớn nhất ngày (T4(a) 0,86 và 0,75) vì mức lệnh lớn của vàng tháng 11 thấp hơn tháng 9. Và cần hằng số theo mã.
- **F** rớt đúng như dự đoán: phiên vắng ngưỡng tụt (vàng có vòng chỉ 21 hợp đồng), khác khung không trùng vòng (T3(c) 50–82%), sót lệnh lớn nhất ngày.
- **B** dày ở phiên Á NQ (15 vòng phiên Á/ngày ở đoạn kiểm) và có vòng 20–26 hợp đồng ở vàng: đúng phỏng đoán của Fable.

### T5 ca biên (6 cấu hình: A D3/D5/D10 R8, C q15 k3, D k200 R10 ở W690; E 75; kèm luật hiện tại)

- **(a) chart mới mở:** W240 cho ngưỡng sau 240 phút nến, W690 sau 690, W1380 sau 1380. Với A R8 W690: vàng M1 ngày đầu 2–15 vòng, 1/6 lần mở có vòng < 3 × mức 1% (4/9: vòng 26 = 2,9 ×); NQ M15 4/6 lần mở có vòng < 3 × (do mức 1% của M15 cao gấp đôi M1, xem giả định 14). W240 rớt nhiều hơn (vàng 2/6, M5 3/6). W1380 và "đủ D ngày" đạt vì **ngày nến đầu không có vòng nào** (đổi lại chart trắng suốt 1380 phút nến). E 75 đạt mọi lần mở. Luật hiện tại rớt mọi lần (vòng 5–6 hợp đồng).
- **(b) nhật ký ngắt quãng `_GCZ26`:** M1 A R8: 40 vòng, nhỏ nhất 40; C: nhỏ nhất 40; D: nhỏ nhất 34; M5 (335 nến): 14–18 vòng, nhỏ nhất 38–47. **Đạt** (không vòng < 20). Luật hiện tại: nhỏ nhất 6 và 9 → rớt.
- **(c) ngày vắng 23–24/11 vàng:** mọi ứng viên 0 vòng (ngưỡng 42–59), **đạt**; luật hiện tại 13 vòng cỡ 9–26. NQ 24/11 (nửa ngày): A R8 3 vòng (115, 99, 127), ngưỡng 81–84.
- **(d) ngày dồn:** vàng 20/11: 9 vòng (77–352), 7 trong số đó dồn 02:01–02:30 UTC; NQ 30/10: M1 21–24 vòng, M15 17–21 vòng. **Đạt** (≤ 40). Luật hiện tại 46 / 626 / 153 vòng.
- **(e) nối hợp đồng** (`_GC_XCEC` tháng 9 + `_GCZ26` tháng 11): lệch ngưỡng trung vị 0–14%, lớn nhất 19–29% ở 690–1380 phút nến đầu sau chỗ nối, không nến nào lệch > 30%: **đạt**. Ví dụ A D5 R8: ngưỡng cuối tháng 9 = 36; 1380 nến đầu tháng 11 tính nối = 37, tính riêng = 47; chuỗi nối có thêm 9 vòng (49 so với 40) vì có ngưỡng ngay từ nến đầu tháng 11.

## 4. Trước và sau (2–3 cấu hình tốt nhất, chế độ W1380; chi tiết từng dòng ở `r1_results.md` mục 2)

Vòng/ngày = trung vị (nhỏ nhất–lớn nhất); phiên = trung vị vòng mỗi phiên; ngưỡng = trung vị ngưỡng (hợp đồng) trên các nến của phiên.

| Nhật ký · đoạn | Luật hiện tại "Không theo CORVEN" | "Theo CORVEN" (mặc định) | **A D5 R8** | **A D3 R8** | **C q15 k3** |
|---|---|---|---|---|---|
| Vàng M1 · chọn (8–9 ngày) | 233 (142–249); Á/Âu/Mỹ 77/79/67; ngưỡng 7/9/9 | 664; ngưỡng 5/5/5 | 6,5 (4–16); 1/3,5/1; ngưỡng **67/57/67**; vòng nhỏ nhất 61 | 6,5 (3–15); 1/3/1; ngưỡng 67/60/67 | 11,5 (6–20); 2/4,5/1,5; ngưỡng 45/45/45 |
| Vàng M1 · kiểm (7 ngày) | 226; ngưỡng 8/9/9 | 702 | 6 (1–15); 1/1/1; ngưỡng **44/42/39**; nhỏ nhất 36 | 6 (3–16); ngưỡng 39/39/39 | 6 (2–9); ngưỡng 42/42/42 |
| Vàng M5 · kiểm | 116; ngưỡng 10/10/11 | 255 | 5 (1–16); ngưỡng 44/42/39 | 5; ngưỡng 39 | 6; ngưỡng 42 |
| Vàng tháng 11 M1 · ngày phần | 83 (62–158) | 290 | 5 (1–10); ngưỡng 43/42/45 | 5; ngưỡng 42/42/45 | 5; ngưỡng 39/39/42 |
| NQ M1 · chọn (2 ngày) | 492,5; Á/Âu/Mỹ 81,5/123/288; ngưỡng 5/5/10 | 825 | 6 (5–7); 0,5/1/4,5; ngưỡng **75/72/72,5** | như A D5 | 6,5; ngưỡng 72/66/69 |
| NQ M1 · kiểm (3 ngày) | 609; 130/162/319; ngưỡng 6/5/10 | 906 | 14 (8–22); 3/1/9; ngưỡng **73/75/78** | 11 (9–21); 3/1/8; ngưỡng 73/79/80 | 16 (8–22); 3/2/9; ngưỡng 72 |
| NQ M15 · kiểm | 153; ngưỡng 13/11/19,5 | 84; ngưỡng 20/16/37,5 | 12 (8–19); 3/1/8 | 9 (9–19); 3/1/6 | 14 (8–19) |

Tóm số: luật hiện tại 116–609 vòng/ngày, vòng nhỏ nhất 5–10 hợp đồng; tỉ số cỡ vòng / mức 1% cùng giờ: nhỏ nhất 0,4–1,1, trung vị 1,4–3,4 (T2 rớt). Ba cấu hình trên: 5–16 vòng/ngày, vòng nhỏ nhất 34–72 hợp đồng; tỉ số nhỏ nhất 3,7–6,5, trung vị 5,6–15 (T2 đạt ở `_GC_XCEC` và NQ; C rớt T2 ở vàng tháng 11).

## 5. Những gì không đo được hoặc đo trên quá ít ngày

- **NQ chỉ có 6 ngày đủ**; đoạn chọn còn 2 ngày đánh giá (27–28/10), đoạn kiểm 3 ngày (29/10, 30/10 là ngày dồn, 2/11). T1 trung vị trên 2–3 ngày rất nhạy; T4(c) trên 4–6 phiên. Mọi kết luận NQ là sơ bộ.
- **Vàng tháng 11 không có ngày đủ**; ngoài mẫu chỉ là ngày phần. T2 ở đây có một vòng 2,47 × (mức 1% cùng giờ tính từ nhật ký ngắt quãng nên ít mẫu).
- **D = 10 trên NQ** không bao giờ đầy cửa sổ (nhật ký ~6,5 ngày): kết quả D = 10 của NQ thực chất là cửa sổ lớn dần.
- Chưa có nhật ký MGC, MNQ: không kiểm được ứng viên nào trên mã micro. E và F cần hằng số theo mã nên không tự áp cho mã khác.
- Chưa biết `MaxOneTradeVolume` của Quantower có gộp các lần khớp của một lệnh market không (`RESEARCH.md` ý 4). Nếu không gộp, lệnh cá mập bị cắt nhỏ sẽ không hiện; ngưỡng không sửa được điều này.
- T5(e) chỉ có một chỗ nối (tháng 9 → tháng 11, cách 7 tuần).
- Ứng viên H (ghép A với B) chưa chạy theo chỉ dẫn.

## 6. Chỗ Opus nghi ngờ (để Fable quyết, không phải kết luận)

1. **T4(c) mâu thuẫn trực tiếp với T1 phiên vắng.** Hai phiên NQ bị sót ở đoạn chọn là phiên Á và Âu ngày 28/10, lệnh lớn nhất 52 và 50 (≥ 5 lần mức 1% của phiên, khoảng 5), trong khi ngưỡng tuyệt đối 72–75; muốn bắt chúng phải hạ ngưỡng phiên vắng (như B) và khi đó phiên Á NQ kiểm lên 15 vòng/ngày, vàng có vòng 20–26. Đây đúng là câu hỏi "cá mập tuyệt đối hay so với giờ đó" PLAN mục 2 đã nêu; ứng viên H nhắm đúng chỗ này.
2. **T1 trên NQ đoạn kiểm rớt ở mọi luật xếp hạng tuyệt đối** vì 30/10 và 2/11 là ngày dồn và phiên Mỹ chiếm 60–70% số vòng (8–10/ngày > 6). Với 3 ngày, không phân biệt được "R quá lớn" với "tuần đó nhiều cá mập".
3. **Ngưỡng của A trôi theo thị trường:** vàng tuần 1–11/9 ngưỡng 57–67, tuần 14–22/9 39–44, tháng 11 42–45. Đó là thiết kế (giữ mật độ), nhưng nghĩa là "cá mập" của tuần yên chỉ cần ~36–40 hợp đồng. Nếu người học muốn cá mập theo nghĩa tuyệt đối hơn, cần sàn — nhưng sàn là hằng số theo mã.
4. **Khởi động:** W1380 sạch nhất cho T5(a) nhưng chart M1 mới mở sẽ trắng 23 giờ nến nếu không có nhật ký cũ; W690 cho vòng sớm hơn nhưng vài lần có vòng 2,9 × mức 1%. Trong C# nhật ký lệnh đơn được ghi ra đĩa nên thực tế có thể nạp lại lịch sử — cần Fable xem `BigTradeLog` nạp bao nhiêu ngày khi mở chart.
5. **Lệnh tròn số** (25/50/100) dày gấp 3–7 lần số kề: luật "lớn hơn hẳn" khiến khi ngưỡng đúng bằng 50 thì mọi lệnh 50 không nổ. Không ảnh hưởng tiêu chí, chỉ là điều người học có thể thấy trên chart.
