# Kết quả vòng 3 — chế độ ngưỡng "Không theo CORVEN" (thống kê)

> Opus đo theo `r2_review.md` mục 6. Chỉ Python, không sửa C#, không commit. Script: `sa3_lib.py`, `sa3_ref.py`, `sa3_selftest.py`, `sa3_dot_eval.py`, `sa3_corven.py`, `sa3_numbers.py`, `sa3_report.py`. Kết quả: `out_r3_*.csv`.
> Mọi số ở đây là **định nghĩa hiển thị** (bóng = volume bất thường so với chính quá khứ của nó), không phải lợi thế giao dịch. Không dùng giá, không nhìn tương lai.
> Opus **không** chọn mặc định; mục 9 chỉ áp từng luật chọn viết trước và ghi kết quả.

Thuật ngữ trong bảng: **số cũ** = ô được tính khi vượt ngưỡng thô hoặc có chấm gần (cách vòng 2); **số "nhìn thấy"** = ô được tính chỉ khi cùng nến, cùng bên có chấm cách ≤ w tick (thứ người học thấy trên chart). Đạt / trượt của 20 ô lớn nhất ngày (≥ 99%), 5 ô lớn nhất phiên (≥ 97%), cực trị rõ (≥ 97%) tính trên số "nhìn thấy". Chọn "lớn hơn hẳn" = chấm khi ô lớn hơn hẳn mọi tick khác cùng bên trong ±w (vòng 2). Chọn tham lam = duyệt ô vượt ngưỡng từ lớn xuống, bằng nhau thì tick thấp trước, giữ ô nếu chưa có chấm nào cách ≤ w tick (giống `CellBigLogic.MergeAdjacent`).

## 1. Tự kiểm

**56/56 ĐẠT** (`out_r3_selftest.txt`). Gồm:
- Tính tay chọn tham lam: hai ô 50 và 50 cách 1 tick → giữ ô tick thấp; chuỗi 60 / 55 / 52 ở tick 200 / 203 / 206 với w = 4 → chấm ở 200 và 206 (chọn "lớn hơn hẳn" chỉ ra 200, chọn mọi ô ra cả ba); hàm chọn trực tiếp với chuỗi 20 / 15 / 12 ở tick 0 / 3 / 6 → giữ tick 0 và 6. Cả bản nhanh lẫn bản chuẩn.
- Khung lân cận bỏ trùng: khung 12 giờ (2 khung/ngày) lấy 400 mẫu, khung ngày (1 khung/ngày) lấy 200 mẫu (không cộng chính nó ba lần); bản chuẩn = bản nhanh.
- Nến rỗng (không ô nào volume > 0) bị bỏ hẳn ở bản chuẩn: chèn 2 nến rỗng, dấu và số nến chính / dự phòng / chưa có y hệt.
- Dữ liệu giả (nhiều giá trị bằng nhau) M1 / M30 / M720 × 3 cách chọn × có / không lân cận: bản chuẩn = bản nhanh.
- Dữ liệu thật: bản chuẩn = bản nhanh từng dấu trên GC M5, GC H1, NQ M1, NQ M15 cho chọn tham lam và "lớn hơn hẳn" (thêm chọn mọi ô, không lân cận, p 1% trên GC M5 và NQ M15); cắt dữ liệu ở 60% số nến cho ngưỡng và chấm trước điểm cắt y hệt; nạp 8 ngày cuối (GC M5, NQ M15) bản chuẩn = bản nhanh. CSV của Golden không có nến rỗng nào.

<details><summary>Từng dòng tự kiểm</summary>

```
ĐẠT  tính tay sel=nms, bản nhanh: ngưỡng nến 8 = 40 (tay 40), w = 4 (tay 4), chấm [(np.str_('dotB'), 200), (np.str_('dotB'), 206), (np.str_('dotS'), 100)] (tay [('dotB', 200), ('dotB', 206), ('dotS', 100)])
ĐẠT  tính tay sel=nms, bản chuẩn: chấm [('dotB', 200), ('dotB', 206), ('dotS', 100)]
ĐẠT  tính tay sel=lmax, bản nhanh: ngưỡng nến 8 = 40 (tay 40), w = 4 (tay 4), chấm [(np.str_('dotB'), 200)] (tay [('dotB', 200)])
ĐẠT  tính tay sel=lmax, bản chuẩn: chấm [('dotB', 200)]
ĐẠT  tính tay sel=all, bản nhanh: ngưỡng nến 8 = 40 (tay 40), w = 4 (tay 4), chấm [(np.str_('dotB'), 200), (np.str_('dotB'), 203), (np.str_('dotB'), 206), (np.str_('dotS'), 100), (np.str_('dotS'), 101)] (tay [('dotB', 200), ('dotB', 203), ('dotB', 206), ('dotS', 100), ('dotS', 101)])
ĐẠT  tính tay sel=all, bản chuẩn: chấm [('dotB', 200), ('dotB', 203), ('dotB', 206), ('dotS', 100), ('dotS', 101)]
ĐẠT  tính tay hàm chọn: 20/15/12 ở tick 0/3/6 -> giữ [np.True_, np.False_, np.True_] (tay T,F,T); 12/12 ở tick 0/1 -> [np.True_, np.False_] (tay T,F)
ĐẠT  khung lân cận bỏ trùng (khung 720 phút, 2 khung/ngày): số mẫu ngưỡng chính nến ngày 3 = 400 (tay 400); bản chuẩn = bản nhanh (5 chấm)
ĐẠT  khung lân cận bỏ trùng (khung 1440 phút, 1 khung/ngày): số mẫu ngưỡng chính nến ngày 3 = 200 (tay 200); bản chuẩn = bản nhanh (1 chấm)
ĐẠT  nến rỗng bị bỏ hẳn: dấu 3 = 3, nến chính/dự phòng/chưa có 0/1/7 = 0/1/7, nến rỗng 2
ĐẠT  dữ liệu giả M1 sel=nms lân cận=0: bản chuẩn 957 = bản nhanh 957 chấm (lệch 0)
ĐẠT  dữ liệu giả M1 sel=nms lân cận=1: bản chuẩn 957 = bản nhanh 957 chấm (lệch 0)
ĐẠT  dữ liệu giả M1 sel=lmax lân cận=0: bản chuẩn 949 = bản nhanh 949 chấm (lệch 0)
ĐẠT  dữ liệu giả M1 sel=lmax lân cận=1: bản chuẩn 949 = bản nhanh 949 chấm (lệch 0)
ĐẠT  dữ liệu giả M1 sel=all lân cận=0: bản chuẩn 999 = bản nhanh 999 chấm (lệch 0)
ĐẠT  dữ liệu giả M1 sel=all lân cận=1: bản chuẩn 999 = bản nhanh 999 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=nms lân cận=0: bản chuẩn 1238 = bản nhanh 1238 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=nms lân cận=1: bản chuẩn 1225 = bản nhanh 1225 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=lmax lân cận=0: bản chuẩn 1178 = bản nhanh 1178 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=lmax lân cận=1: bản chuẩn 1174 = bản nhanh 1174 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=all lân cận=0: bản chuẩn 1586 = bản nhanh 1586 chấm (lệch 0)
ĐẠT  dữ liệu giả M30 sel=all lân cận=1: bản chuẩn 1550 = bản nhanh 1550 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=nms lân cận=0: bản chuẩn 64 = bản nhanh 64 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=nms lân cận=1: bản chuẩn 63 = bản nhanh 63 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=lmax lân cận=0: bản chuẩn 61 = bản nhanh 61 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=lmax lân cận=1: bản chuẩn 60 = bản nhanh 60 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=all lân cận=0: bản chuẩn 80 = bản nhanh 80 chấm (lệch 0)
ĐẠT  dữ liệu giả M720 sel=all lân cận=1: bản chuẩn 75 = bản nhanh 75 chấm (lệch 0)
ĐẠT  GC M5: CSV Golden 17623 nến (rỗng 0) = bảng nhanh 17623 nến; giá trị bên không nguyên: 0
ĐẠT  GC M5 nen_moi: chấm bản chuẩn 16592 = bản nhanh 16592 (lệch 0); nến ngưỡng chính 17071, dự phòng 548, chưa có 4
ĐẠT  GC M5 nạp 8 ngày cuối (từ 2026-10-28 22:00:00): bản chuẩn 1915 = bản nhanh 1915 chấm; nến chính 1489, dự phòng 547, chưa có 5
ĐẠT  GC M5 sel_lmax: chấm bản chuẩn 15743 = bản nhanh 15743 (lệch 0); nến ngưỡng chính 17071, dự phòng 548, chưa có 4
ĐẠT  GC M5 sel_all: chấm bản chuẩn 30015 = bản nhanh 30015 (lệch 0); nến ngưỡng chính 17071, dự phòng 548, chưa có 4
ĐẠT  GC M5 khong_lan_can: chấm bản chuẩn 17678 = bản nhanh 17678 (lệch 0); nến ngưỡng chính 17065, dự phòng 554, chưa có 4
ĐẠT  GC M5 p1: chấm bản chuẩn 10024 = bản nhanh 10024 (lệch 0); nến ngưỡng chính 17071, dự phòng 545, chưa có 7
ĐẠT  GC M5 nen_moi: cắt dữ liệu ở nến 10573: ngưỡng và chấm trước điểm cắt y hệt (10464 chấm)
ĐẠT  GC M5 sel_lmax: cắt dữ liệu ở nến 10573: ngưỡng và chấm trước điểm cắt y hệt (9947 chấm)
ĐẠT  GC M60: CSV Golden 1470 nến (rỗng 0) = bảng nhanh 1470 nến; giá trị bên không nguyên: 0
ĐẠT  GC M60 nen_moi: chấm bản chuẩn 3308 = bản nhanh 3308 (lệch 0); nến ngưỡng chính 1424, dự phòng 45, chưa có 1
ĐẠT  GC M60 sel_lmax: chấm bản chuẩn 3046 = bản nhanh 3046 (lệch 0); nến ngưỡng chính 1424, dự phòng 45, chưa có 1
ĐẠT  GC M60 nen_moi: cắt dữ liệu ở nến 882: ngưỡng và chấm trước điểm cắt y hệt (2107 chấm)
ĐẠT  GC M60 sel_lmax: cắt dữ liệu ở nến 882: ngưỡng và chấm trước điểm cắt y hệt (1930 chấm)
ĐẠT  NQ M1: CSV Golden 71047 nến (rỗng 0) = bảng nhanh 71047 nến; giá trị bên không nguyên: 0
ĐẠT  NQ M1 nen_moi: chấm bản chuẩn 60589 = bản nhanh 60589 (lệch 0); nến ngưỡng chính 68288, dự phòng 2754, chưa có 5
ĐẠT  NQ M1 sel_lmax: chấm bản chuẩn 56983 = bản nhanh 56983 (lệch 0); nến ngưỡng chính 68288, dự phòng 2754, chưa có 5
ĐẠT  NQ M1 nen_moi: cắt dữ liệu ở nến 42628: ngưỡng và chấm trước điểm cắt y hệt (31878 chấm)
ĐẠT  NQ M1 sel_lmax: cắt dữ liệu ở nến 42628: ngưỡng và chấm trước điểm cắt y hệt (29988 chấm)
ĐẠT  NQ M15: CSV Golden 4737 nến (rỗng 0) = bảng nhanh 4737 nến; giá trị bên không nguyên: 0
ĐẠT  NQ M15 nen_moi: chấm bản chuẩn 11006 = bản nhanh 11006 (lệch 0); nến ngưỡng chính 4553, dự phòng 183, chưa có 1
ĐẠT  NQ M15 nạp 8 ngày cuối (từ 2026-11-12 23:00:00): bản chuẩn 2125 = bản nhanh 2125 chấm; nến chính 513, dự phòng 183, chưa có 1
ĐẠT  NQ M15 sel_lmax: chấm bản chuẩn 10004 = bản nhanh 10004 (lệch 0); nến ngưỡng chính 4553, dự phòng 183, chưa có 1
ĐẠT  NQ M15 sel_all: chấm bản chuẩn 41786 = bản nhanh 41786 (lệch 0); nến ngưỡng chính 4553, dự phòng 183, chưa có 1
ĐẠT  NQ M15 khong_lan_can: chấm bản chuẩn 11854 = bản nhanh 11854 (lệch 0); nến ngưỡng chính 4553, dự phòng 183, chưa có 1
ĐẠT  NQ M15 p1: chấm bản chuẩn 7696 = bản nhanh 7696 (lệch 0); nến ngưỡng chính 4553, dự phòng 182, chưa có 2
ĐẠT  NQ M15 nen_moi: cắt dữ liệu ở nến 2842: ngưỡng và chấm trước điểm cắt y hệt (6001 chấm)
ĐẠT  NQ M15 sel_lmax: cắt dữ liệu ở nến 2842: ngưỡng và chấm trước điểm cắt y hệt (5445 chấm)
TỔNG: 56/56 ĐẠT (188 s)
```
</details>

## 2. Bảng điểm: tổng số lần trượt (6 ô = GC, NQ × M1, M5, M15; 8 tiêu chí)

| Cấu hình | Trượt đoạn chọn | Trượt đoạn kiểm | Tổng | Trượt cái gì |
|---|---|---|---|---|
| Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam) | 1 | 0 | 1 | NQ M15 đoạn chọn: 5 ô lớn nhất phiên 0,913 |
| Nền mới, chọn "lớn hơn hẳn" như vòng 2 | 7 | 8 | 15 | GC M5 đoạn kiểm: 20 ô lớn nhất ngày 0,987; GC M15 đoạn kiểm: 20 ô lớn nhất ngày 0,988; NQ M1 đoạn chọn: 20 ô lớn nhất ngày 0,977; cực trị rõ 0,964; NQ M1 đoạn kiểm: 20 ô lớn nhất ngày 0,964; cực trị rõ 0,963; NQ M5 đoạn chọn: 20 ô lớn nhất ngày 0,987; cực trị rõ 0,965; NQ M5 đoạn kiểm: 20 ô lớn nhất ngày 0,964; cực trị rõ 0,955; NQ M15 đoạn chọn: 20 ô lớn nhất ngày 0,963; 5 ô lớn nhất phiên 0,909; cực trị rõ 0,948; NQ M15 đoạn kiểm: 20 ô lớn nhất ngày 0,968; cực trị rõ 0,949 |
| Nền mới, không gộp khung lân cận | 5 | 2 | 7 | GC M5 đoạn chọn: Khớp chung 1,27; GC M5 đoạn kiểm: Khớp chung 1,25; GC M15 đoạn chọn: Khớp chung 1,38; GC M15 đoạn kiểm: Khớp chung 1,34; NQ M5 đoạn chọn: Khớp chung 1,27; NQ M15 đoạn chọn: Khớp chung 1,41; 20 ô lớn nhất ngày 0,985 |
| Nền mới, p = 1% | 5 | 2 | 7 | GC M15 đoạn chọn: Khớp chung 1,29; GC M15 đoạn kiểm: Khớp chung 1,27; NQ M5 đoạn chọn: 5 ô lớn nhất phiên 0,967; NQ M15 đoạn chọn: Khớp chung 1,34; 20 ô lớn nhất ngày 0,985; 5 ô lớn nhất phiên 0,893; NQ M15 đoạn kiểm: 5 ô lớn nhất phiên 0,969 |
| Nền mới, p = 0,5% | 10 | 6 | 16 | GC M15 đoạn chọn: Khớp chung 1,35; 20 ô lớn nhất ngày 0,950; cực trị rõ 0,965; GC M15 đoạn kiểm: Khớp chung 1,33; 20 ô lớn nhất ngày 0,950; 5 ô lớn nhất phiên 0,958; NQ M5 đoạn chọn: Khớp chung 1,3; 20 ô lớn nhất ngày 0,938; 5 ô lớn nhất phiên 0,949; NQ M5 đoạn kiểm: 20 ô lớn nhất ngày 0,989; NQ M15 đoạn chọn: Khớp chung 1,51; Khớp theo phiên 1,43/1,19/1,72; 20 ô lớn nhất ngày 0,935; 5 ô lớn nhất phiên 0,882; NQ M15 đoạn kiểm: 20 ô lớn nhất ngày 0,986; 5 ô lớn nhất phiên 0,966 |
| Nền mới, tối thiểu 1 ngày | 2 | 0 | 2 | NQ M15 đoạn chọn: Khớp chung 1,25; 5 ô lớn nhất phiên 0,909 |
| Đối chứng: luật đang chạy, bộ "Không sót" | 18 | 18 | 36 | mỗi ô trượt cả 3 tiêu chí không sót (20 ô lớn nhất ngày 0,773–0,876; 5 ô lớn nhất phiên 0,758–0,951; cực trị rõ 0,768–0,856); Khớp không áp dụng |
| Đối chứng: luật đang chạy, bộ "Ít nhiễu" | 18 | 18 | 36 | mỗi ô trượt cả 3 tiêu chí không sót (20 ô lớn nhất ngày 0,605–0,795; 5 ô lớn nhất phiên 0,664–0,810; cực trị rõ 0,530–0,763); Khớp không áp dụng |

Ô M30 và H1 (chỉ báo, không tính vào luật chọn):

| Cấu hình | Trượt M30 + H1 (hai mã, hai đoạn) | Trượt cái gì |
|---|---|---|
| Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam) | 8 | GC M30 đoạn chọn: Khớp chung 1,3; GC M60 đoạn chọn: Khớp chung 1,28; GC M60 đoạn kiểm: 20 ô lớn nhất ngày 0,981; NQ M30 đoạn chọn: Khớp chung 1,31; 5 ô lớn nhất phiên 0,887; NQ M60 đoạn chọn: Khớp chung 1,25; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,107); NQ M60 đoạn kiểm: 5 ô lớn nhất phiên 0,951 |
| Nền mới, chọn "lớn hơn hẳn" như vòng 2 | 24 | GC M30 đoạn chọn: Khớp chung 1,3; cực trị rõ 0,965; GC M30 đoạn kiểm: 20 ô lớn nhất ngày 0,979; 5 ô lớn nhất phiên 0,969; cực trị rõ 0,959; GC M60 đoạn chọn: Khớp chung 1,28; 20 ô lớn nhất ngày 0,978; cực trị rõ 0,966; GC M60 đoạn kiểm: 20 ô lớn nhất ngày 0,973; NQ M30 đoạn chọn: Khớp chung 1,31; 20 ô lớn nhất ngày 0,977; 5 ô lớn nhất phiên 0,884; cực trị rõ 0,953; NQ M30 đoạn kiểm: 20 ô lớn nhất ngày 0,959; 5 ô lớn nhất phiên 0,969; cực trị rõ 0,945; NQ M60 đoạn chọn: Khớp chung 1,25; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,107); 20 ô lớn nhất ngày 0,970; 5 ô lớn nhất phiên 0,962; cực trị rõ 0,936; NQ M60 đoạn kiểm: 20 ô lớn nhất ngày 0,966; 5 ô lớn nhất phiên 0,948; cực trị rõ 0,954 |
| Nền mới, không gộp khung lân cận | 16 | GC M30 đoạn chọn: Khớp chung 1,5; Khớp theo phiên 1,44/1,5/1,57; GC M30 đoạn kiểm: Khớp chung 1,47; GC M60 đoạn chọn: Khớp chung 1,49; Khớp theo phiên 1,4/1,48/1,6; 20 ô lớn nhất ngày 0,990; GC M60 đoạn kiểm: Khớp chung 1,4; Khớp theo phiên 1,5/1,32/1,36; 20 ô lớn nhất ngày 0,985; NQ M30 đoạn chọn: Khớp chung 1,54; Khớp theo phiên 1,44/1,58/1,56; 20 ô lớn nhất ngày 0,983; NQ M60 đoạn chọn: Khớp chung 1,5; Khớp theo phiên 1,42/1,8/1,31; 20 ô lớn nhất ngày 0,978; 5 ô lớn nhất phiên 0,960 |
| Nền mới, p = 1% | 19 | GC M30 đoạn chọn: Khớp chung 1,4; 20 ô lớn nhất ngày 0,987; GC M30 đoạn kiểm: Khớp chung 1,33; 20 ô lớn nhất ngày 0,967; GC M60 đoạn chọn: Khớp chung 1,38; 20 ô lớn nhất ngày 0,971; GC M60 đoạn kiểm: Khớp chung 1,28; 20 ô lớn nhất ngày 0,946; 5 ô lớn nhất phiên 0,932; NQ M30 đoạn chọn: Khớp chung 1,49; Khớp theo phiên 1,41/1,33/1,62; 20 ô lớn nhất ngày 0,980; 5 ô lớn nhất phiên 0,873; NQ M60 đoạn chọn: Khớp chung 1,43; Khớp theo phiên 1,3/1,74/1,26; Khớp theo giờ 18/23 (giờ tệ nhất 20: 0,131); 20 ô lớn nhất ngày 0,975; 5 ô lớn nhất phiên 0,902; NQ M60 đoạn kiểm: 5 ô lớn nhất phiên 0,938 |
| Nền mới, p = 0,5% | 33 | GC M30 đoạn chọn: Khớp chung 1,48; Khớp theo phiên 1,51/1,46/1,46; 20 ô lớn nhất ngày 0,901; 5 ô lớn nhất phiên 0,902; cực trị rõ 0,951; GC M30 đoạn kiểm: Khớp chung 1,43; 20 ô lớn nhất ngày 0,875; 5 ô lớn nhất phiên 0,904; cực trị rõ 0,960; GC M60 đoạn chọn: Khớp chung 1,46; Khớp theo phiên 1,51/1,44/1,44; 20 ô lớn nhất ngày 0,869; 5 ô lớn nhất phiên 0,862; cực trị rõ 0,945; GC M60 đoạn kiểm: Khớp chung 1,37; 20 ô lớn nhất ngày 0,835; 5 ô lớn nhất phiên 0,847; NQ M30 đoạn chọn: Khớp chung 1,7; Khớp theo phiên 1,41/1,4/2,04; 20 ô lớn nhất ngày 0,887; 5 ô lớn nhất phiên 0,842; cực trị rõ 0,969; NQ M30 đoạn kiểm: 20 ô lớn nhất ngày 0,970; 5 ô lớn nhất phiên 0,969; NQ M60 đoạn chọn: Khớp chung 1,76; Khớp theo phiên 1,37/2,41/1,51; Khớp theo giờ 15/23 (giờ tệ nhất 20: 0,168); 20 ô lớn nhất ngày 0,885; 5 ô lớn nhất phiên 0,824; cực trị rõ 0,941; NQ M60 đoạn kiểm: Khớp theo giờ 18/24 (giờ tệ nhất 21: 0,0909); 20 ô lớn nhất ngày 0,973; 5 ô lớn nhất phiên 0,920 |
| Nền mới, tối thiểu 1 ngày | 8 | GC M30 đoạn chọn: Khớp chung 1,3; GC M60 đoạn chọn: Khớp chung 1,27; GC M60 đoạn kiểm: 20 ô lớn nhất ngày 0,981; NQ M30 đoạn chọn: Khớp chung 1,36; 5 ô lớn nhất phiên 0,882; NQ M60 đoạn chọn: Khớp chung 1,3; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,176); NQ M60 đoạn kiểm: 5 ô lớn nhất phiên 0,951 |

## 3. Bảng điểm chi tiết (số cũ → số "nhìn thấy")

### Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam)

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,109 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,16% | 0,00% | 0,40 | 0 |
| GC | M1 | đoạn kiểm | 1,077 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,14% | 0,00% | 0,35 | 0 |
| GC | M5 | đoạn chọn | 1,164 | 1,000 → **1,000** | 1,000 → **1,000** | 0,998 → **0,998** | 0,26% | 0,00% | 0,99 | 0 |
| GC | M5 | đoạn kiểm | 1,131 | 1,000 → **1,000** | 1,000 → **1,000** | 0,997 → **0,997** | 0,25% | 0,00% | 0,87 | 0 |
| GC | M15 | đoạn chọn | 1,233 | 0,999 → **0,999** | 0,998 → **0,998** | 0,993 → **0,993** | 0,36% | 0,00% | 1,57 | 0 |
| GC | M15 | đoạn kiểm | 1,183 | 1,000 → **1,000** | 1,000 → **1,000** | 0,990 → **0,990** | 0,50% | 0,00% | 1,37 | 0 |
| GC | M30 | đoạn chọn | 1,296 | 0,997 → **0,997** | 0,998 → **0,998** | 0,988 → **0,988** | 0,22% | 0,00% | 2,02 | Khớp chung 1,3 |
| GC | M30 | đoạn kiểm | 1,223 | 0,996 → **0,996** | 0,987 → **0,987** | 0,989 → **0,989** | 0,39% | 0,00% | 1,74 | 0 |
| GC | M60 | đoạn chọn | 1,279 | 0,995 → **0,995** | 0,995 → **0,995** | 0,992 → **0,992** | 0,38% | 0,00% | 2,39 | Khớp chung 1,28 |
| GC | M60 | đoạn kiểm | 1,176 | 0,981 → **0,981** | 0,992 → **0,992** | 0,994 → **0,994** | 0,25% | 0,00% | 2,05 | 20 ô lớn nhất ngày 0,981 |
| NQ | M1 | đoạn chọn | 1,097 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 1,22% | 0,00% | 0,75 | 0 |
| NQ | M1 | đoạn kiểm | 0,943 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,26% | 0,00% | 1,00 | 0 |
| NQ | M5 | đoạn chọn | 1,150 | 1,000 → **1,000** | 0,976 → **0,976** | 0,998 → **0,998** | 1,49% | 0,00% | 1,50 | 0 |
| NQ | M5 | đoạn kiểm | 0,940 | 1,000 → **1,000** | 0,991 → **0,991** | 0,997 → **0,997** | 0,42% | 0,00% | 1,91 | 0 |
| NQ | M15 | đoạn chọn | 1,241 | 1,000 → **1,000** | 0,913 → **0,913** | 0,992 → **0,992** | 1,32% | 0,00% | 2,12 | 5 ô lớn nhất phiên 0,913 |
| NQ | M15 | đoạn kiểm | 0,931 | 1,000 → **1,000** | 0,978 → **0,978** | 0,994 → **0,994** | 0,41% | 0,00% | 2,60 | 0 |
| NQ | M30 | đoạn chọn | 1,310 | 0,993 → **0,993** | 0,887 → **0,887** | 0,988 → **0,988** | 1,30% | 0,00% | 2,52 | Khớp chung 1,31; 5 ô lớn nhất phiên 0,887 |
| NQ | M30 | đoạn kiểm | 0,973 | 1,000 → **1,000** | 0,972 → **0,972** | 0,992 → **0,992** | 0,71% | 0,00% | 2,99 | 0 |
| NQ | M60 | đoạn chọn | 1,255 | 1,000 → **1,000** | 0,978 → **0,978** | 0,992 → **0,992** | 2,00% | 0,00% | 2,77 | Khớp chung 1,25; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,107) |
| NQ | M60 | đoạn kiểm | 0,918 | 1,000 → **1,000** | 0,951 → **0,951** | 0,993 → **0,993** | 0,13% | 0,00% | 3,11 | 5 ô lớn nhất phiên 0,951 |

### Nền mới, chọn "lớn hơn hẳn" như vòng 2

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,109 | 1,000 → **0,992** | 1,000 → **0,997** | 0,999 → **0,978** | 0,12% | 0,00% | 0,38 | 0 |
| GC | M1 | đoạn kiểm | 1,077 | 1,000 → **0,996** | 1,000 → **1,000** | 0,999 → **0,981** | 0,10% | 0,00% | 0,34 | 0 |
| GC | M5 | đoạn chọn | 1,164 | 1,000 → **0,999** | 1,000 → **0,993** | 0,998 → **0,971** | 0,19% | 0,00% | 0,94 | 0 |
| GC | M5 | đoạn kiểm | 1,131 | 1,000 → **0,987** | 1,000 → **1,000** | 0,997 → **0,972** | 0,16% | 0,00% | 0,82 | 20 ô lớn nhất ngày 0,987 |
| GC | M15 | đoạn chọn | 1,233 | 0,999 → **0,992** | 0,998 → **0,993** | 0,993 → **0,971** | 0,17% | 0,00% | 1,47 | 0 |
| GC | M15 | đoạn kiểm | 1,183 | 1,000 → **0,988** | 1,000 → **0,995** | 0,990 → **0,970** | 0,40% | 0,00% | 1,29 | 20 ô lớn nhất ngày 0,988 |
| GC | M30 | đoạn chọn | 1,296 | 0,997 → **0,994** | 0,998 → **0,998** | 0,988 → **0,965** | 0,12% | 0,00% | 1,85 | Khớp chung 1,3; cực trị rõ 0,965 |
| GC | M30 | đoạn kiểm | 1,223 | 0,996 → **0,979** | 0,987 → **0,969** | 0,989 → **0,959** | 0,32% | 0,00% | 1,62 | 20 ô lớn nhất ngày 0,979; 5 ô lớn nhất phiên 0,969; cực trị rõ 0,959 |
| GC | M60 | đoạn chọn | 1,279 | 0,995 → **0,978** | 0,995 → **0,978** | 0,992 → **0,966** | 0,16% | 0,00% | 2,19 | Khớp chung 1,28; 20 ô lớn nhất ngày 0,978; cực trị rõ 0,966 |
| GC | M60 | đoạn kiểm | 1,176 | 0,981 → **0,973** | 0,992 → **0,987** | 0,994 → **0,974** | 0,27% | 0,00% | 1,90 | 20 ô lớn nhất ngày 0,973 |
| NQ | M1 | đoạn chọn | 1,097 | 1,000 → **0,977** | 1,000 → **0,996** | 0,999 → **0,964** | 1,04% | 0,00% | 0,70 | 20 ô lớn nhất ngày 0,977; cực trị rõ 0,964 |
| NQ | M1 | đoạn kiểm | 0,943 | 1,000 → **0,964** | 1,000 → **0,997** | 0,999 → **0,963** | 0,23% | 0,00% | 0,94 | 20 ô lớn nhất ngày 0,964; cực trị rõ 0,963 |
| NQ | M5 | đoạn chọn | 1,150 | 1,000 → **0,987** | 0,976 → **0,973** | 0,998 → **0,965** | 1,24% | 0,00% | 1,39 | 20 ô lớn nhất ngày 0,987; cực trị rõ 0,965 |
| NQ | M5 | đoạn kiểm | 0,940 | 1,000 → **0,964** | 0,991 → **0,988** | 0,997 → **0,955** | 0,34% | 0,00% | 1,76 | 20 ô lớn nhất ngày 0,964; cực trị rõ 0,955 |
| NQ | M15 | đoạn chọn | 1,241 | 1,000 → **0,963** | 0,913 → **0,909** | 0,992 → **0,948** | 0,83% | 0,00% | 1,92 | 20 ô lớn nhất ngày 0,963; 5 ô lớn nhất phiên 0,909; cực trị rõ 0,948 |
| NQ | M15 | đoạn kiểm | 0,931 | 1,000 → **0,968** | 0,978 → **0,978** | 0,994 → **0,949** | 0,32% | 0,00% | 2,37 | 20 ô lớn nhất ngày 0,968; cực trị rõ 0,949 |
| NQ | M30 | đoạn chọn | 1,310 | 0,993 → **0,977** | 0,887 → **0,884** | 0,988 → **0,953** | 0,77% | 0,00% | 2,26 | Khớp chung 1,31; 20 ô lớn nhất ngày 0,977; 5 ô lớn nhất phiên 0,884; cực trị rõ 0,953 |
| NQ | M30 | đoạn kiểm | 0,973 | 1,000 → **0,959** | 0,972 → **0,969** | 0,991 → **0,945** | 0,64% | 0,00% | 2,67 | 20 ô lớn nhất ngày 0,959; 5 ô lớn nhất phiên 0,969; cực trị rõ 0,945 |
| NQ | M60 | đoạn chọn | 1,255 | 1,000 → **0,970** | 0,978 → **0,962** | 0,992 → **0,936** | 1,24% | 0,00% | 2,46 | Khớp chung 1,25; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,107); 20 ô lớn nhất ngày 0,970; 5 ô lớn nhất phiên 0,962; cực trị rõ 0,936 |
| NQ | M60 | đoạn kiểm | 0,918 | 1,000 → **0,966** | 0,951 → **0,948** | 0,993 → **0,954** | 0,14% | 0,00% | 2,79 | 20 ô lớn nhất ngày 0,966; 5 ô lớn nhất phiên 0,948; cực trị rõ 0,954 |

### Nền mới, không gộp khung lân cận

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,190 | 1,000 → **1,000** | 1,000 → **1,000** | 1,000 → **1,000** | 0,13% | 0,00% | 0,42 | 0 |
| GC | M1 | đoạn kiểm | 1,151 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,14% | 0,00% | 0,37 | 0 |
| GC | M5 | đoạn chọn | 1,272 | 1,000 → **1,000** | 1,000 → **1,000** | 1,000 → **1,000** | 0,35% | 0,00% | 1,05 | Khớp chung 1,27 |
| GC | M5 | đoạn kiểm | 1,253 | 1,000 → **1,000** | 1,000 → **1,000** | 0,998 → **0,998** | 0,44% | 0,00% | 0,94 | Khớp chung 1,25 |
| GC | M15 | đoạn chọn | 1,380 | 1,000 → **1,000** | 1,000 → **1,000** | 0,996 → **0,996** | 0,27% | 0,00% | 1,67 | Khớp chung 1,38 |
| GC | M15 | đoạn kiểm | 1,340 | 0,998 → **0,998** | 1,000 → **1,000** | 0,990 → **0,990** | 0,46% | 0,00% | 1,49 | Khớp chung 1,34 |
| GC | M30 | đoạn chọn | 1,504 | 0,994 → **0,994** | 0,997 → **0,997** | 0,989 → **0,989** | 0,19% | 0,00% | 2,13 | Khớp chung 1,5; Khớp theo phiên 1,44/1,5/1,57 |
| GC | M30 | đoạn kiểm | 1,474 | 0,994 → **0,994** | 0,992 → **0,992** | 0,982 → **0,982** | 1,05% | 0,00% | 1,88 | Khớp chung 1,47 |
| GC | M60 | đoạn chọn | 1,492 | 0,990 → **0,990** | 0,988 → **0,988** | 0,996 → **0,996** | 0,53% | 0,00% | 2,55 | Khớp chung 1,49; Khớp theo phiên 1,4/1,48/1,6; 20 ô lớn nhất ngày 0,990 |
| GC | M60 | đoạn kiểm | 1,402 | 0,985 → **0,985** | 0,992 → **0,992** | 0,995 → **0,995** | 0,68% | 0,00% | 2,25 | Khớp chung 1,4; Khớp theo phiên 1,5/1,32/1,36; 20 ô lớn nhất ngày 0,985 |
| NQ | M1 | đoạn chọn | 1,184 | 1,000 → **1,000** | 1,000 → **1,000** | 1,000 → **1,000** | 1,19% | 0,00% | 0,80 | 0 |
| NQ | M1 | đoạn kiểm | 0,995 | 1,000 → **1,000** | 1,000 → **1,000** | 1,000 → **1,000** | 0,65% | 0,00% | 1,05 | 0 |
| NQ | M5 | đoạn chọn | 1,273 | 0,995 → **0,995** | 0,998 → **0,998** | 0,999 → **0,999** | 1,37% | 0,00% | 1,63 | Khớp chung 1,27 |
| NQ | M5 | đoạn kiểm | 1,020 | 0,995 → **0,995** | 0,997 → **0,997** | 1,000 → **1,000** | 0,82% | 0,00% | 2,05 | 0 |
| NQ | M15 | đoạn chọn | 1,405 | 0,985 → **0,985** | 0,996 → **0,996** | 0,997 → **0,997** | 1,27% | 0,00% | 2,30 | Khớp chung 1,41; 20 ô lớn nhất ngày 0,985 |
| NQ | M15 | đoạn kiểm | 1,048 | 0,993 → **0,993** | 1,000 → **1,000** | 0,995 → **0,995** | 0,72% | 0,00% | 2,79 | 0 |
| NQ | M30 | đoạn chọn | 1,544 | 0,983 → **0,983** | 0,987 → **0,987** | 0,988 → **0,988** | 1,19% | 0,00% | 2,75 | Khớp chung 1,54; Khớp theo phiên 1,44/1,58/1,56; 20 ô lớn nhất ngày 0,983 |
| NQ | M30 | đoạn kiểm | 1,148 | 0,998 → **0,998** | 0,997 → **0,997** | 0,994 → **0,994** | 0,80% | 0,00% | 3,26 | 0 |
| NQ | M60 | đoạn chọn | 1,502 | 0,978 → **0,978** | 0,960 → **0,960** | 0,991 → **0,991** | 1,66% | 0,00% | 3,07 | Khớp chung 1,5; Khớp theo phiên 1,42/1,8/1,31; 20 ô lớn nhất ngày 0,978; 5 ô lớn nhất phiên 0,960 |
| NQ | M60 | đoạn kiểm | 1,070 | 0,998 → **0,998** | 1,000 → **1,000** | 0,996 → **0,996** | 1,27% | 0,00% | 3,50 | 0 |

### Nền mới, p = 1%

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,115 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,22% | 0,00% | 0,23 | 0 |
| GC | M1 | đoạn kiểm | 1,113 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,06% | 0,00% | 0,20 | 0 |
| GC | M5 | đoạn chọn | 1,195 | 1,000 → **1,000** | 0,998 → **0,998** | 0,993 → **0,993** | 0,51% | 0,00% | 0,60 | 0 |
| GC | M5 | đoạn kiểm | 1,180 | 1,000 → **1,000** | 0,997 → **0,997** | 0,990 → **0,990** | 0,54% | 0,00% | 0,53 | 0 |
| GC | M15 | đoạn chọn | 1,287 | 0,997 → **0,997** | 0,993 → **0,993** | 0,982 → **0,982** | 0,53% | 0,00% | 1,01 | Khớp chung 1,29 |
| GC | M15 | đoạn kiểm | 1,265 | 0,994 → **0,994** | 0,992 → **0,992** | 0,987 → **0,987** | 0,53% | 0,00% | 0,88 | Khớp chung 1,27 |
| GC | M30 | đoạn chọn | 1,403 | 0,987 → **0,987** | 0,984 → **0,984** | 0,983 → **0,983** | 0,66% | 0,00% | 1,36 | Khớp chung 1,4; 20 ô lớn nhất ngày 0,987 |
| GC | M30 | đoạn kiểm | 1,328 | 0,967 → **0,967** | 0,984 → **0,984** | 0,971 → **0,971** | 0,37% | 0,00% | 1,16 | Khớp chung 1,33; 20 ô lớn nhất ngày 0,967 |
| GC | M60 | đoạn chọn | 1,381 | 0,971 → **0,971** | 0,971 → **0,971** | 0,988 → **0,988** | 0,34% | 0,00% | 1,68 | Khớp chung 1,38; 20 ô lớn nhất ngày 0,971 |
| GC | M60 | đoạn kiểm | 1,281 | 0,946 → **0,946** | 0,932 → **0,932** | 0,987 → **0,987** | 0,85% | 0,00% | 1,40 | Khớp chung 1,28; 20 ô lớn nhất ngày 0,946; 5 ô lớn nhất phiên 0,932 |
| NQ | M1 | đoạn chọn | 1,121 | 1,000 → **1,000** | 0,996 → **0,996** | 0,997 → **0,997** | 1,62% | 0,00% | 0,45 | 0 |
| NQ | M1 | đoạn kiểm | 0,943 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,23% | 0,00% | 0,62 | 0 |
| NQ | M5 | đoạn chọn | 1,220 | 0,998 → **0,998** | 0,967 → **0,967** | 0,993 → **0,993** | 2,34% | 0,00% | 0,98 | 5 ô lớn nhất phiên 0,967 |
| NQ | M5 | đoạn kiểm | 0,950 | 0,995 → **0,995** | 0,988 → **0,988** | 0,995 → **0,995** | 0,47% | 0,00% | 1,30 | 0 |
| NQ | M15 | đoạn chọn | 1,345 | 0,985 → **0,985** | 0,893 → **0,893** | 0,986 → **0,986** | 2,42% | 0,00% | 1,46 | Khớp chung 1,34; 20 ô lớn nhất ngày 0,985; 5 ô lớn nhất phiên 0,893 |
| NQ | M15 | đoạn kiểm | 0,970 | 0,991 → **0,991** | 0,969 → **0,969** | 0,992 → **0,992** | 0,52% | 0,00% | 1,86 | 5 ô lớn nhất phiên 0,969 |
| NQ | M30 | đoạn chọn | 1,490 | 0,980 → **0,980** | 0,873 → **0,873** | 0,981 → **0,981** | 1,98% | 0,00% | 1,84 | Khớp chung 1,49; Khớp theo phiên 1,41/1,33/1,62; 20 ô lớn nhất ngày 0,980; 5 ô lớn nhất phiên 0,873 |
| NQ | M30 | đoạn kiểm | 1,038 | 0,998 → **0,998** | 0,972 → **0,972** | 0,988 → **0,988** | 1,18% | 0,00% | 2,22 | 0 |
| NQ | M60 | đoạn chọn | 1,434 | 0,975 → **0,975** | 0,902 → **0,902** | 0,976 → **0,976** | 2,48% | 0,00% | 2,06 | Khớp chung 1,43; Khớp theo phiên 1,3/1,74/1,26; Khớp theo giờ 18/23 (giờ tệ nhất 20: 0,131); 20 ô lớn nhất ngày 0,975; 5 ô lớn nhất phiên 0,902 |
| NQ | M60 | đoạn kiểm | 0,983 | 0,995 → **0,995** | 0,938 → **0,938** | 0,989 → **0,989** | 0,08% | 0,00% | 2,44 | 5 ô lớn nhất phiên 0,938 |

### Nền mới, p = 0,5%

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,143 | 1,000 → **1,000** | 1,000 → **1,000** | 0,997 → **0,997** | 0,40% | 0,00% | 0,13 | 0 |
| GC | M1 | đoạn kiểm | 1,147 | 1,000 → **1,000** | 1,000 → **1,000** | 0,996 → **0,996** | 0,32% | 0,00% | 0,12 | 0 |
| GC | M5 | đoạn chọn | 1,249 | 0,994 → **0,994** | 0,993 → **0,993** | 0,991 → **0,991** | 0,66% | 0,00% | 0,36 | 0 |
| GC | M5 | đoạn kiểm | 1,227 | 0,990 → **0,990** | 0,997 → **0,997** | 0,987 → **0,987** | 1,06% | 0,00% | 0,31 | 0 |
| GC | M15 | đoạn chọn | 1,355 | 0,950 → **0,950** | 0,972 → **0,972** | 0,965 → **0,965** | 1,36% | 0,00% | 0,64 | Khớp chung 1,35; 20 ô lớn nhất ngày 0,950; cực trị rõ 0,965 |
| GC | M15 | đoạn kiểm | 1,331 | 0,950 → **0,950** | 0,958 → **0,958** | 0,978 → **0,978** | 1,59% | 0,00% | 0,54 | Khớp chung 1,33; 20 ô lớn nhất ngày 0,950; 5 ô lớn nhất phiên 0,958 |
| GC | M30 | đoạn chọn | 1,476 | 0,901 → **0,901** | 0,902 → **0,902** | 0,951 → **0,951** | 0,79% | 0,00% | 0,89 | Khớp chung 1,48; Khớp theo phiên 1,51/1,46/1,46; 20 ô lớn nhất ngày 0,901; 5 ô lớn nhất phiên 0,902; cực trị rõ 0,951 |
| GC | M30 | đoạn kiểm | 1,431 | 0,875 → **0,875** | 0,904 → **0,904** | 0,960 → **0,960** | 2,15% | 0,00% | 0,76 | Khớp chung 1,43; 20 ô lớn nhất ngày 0,875; 5 ô lớn nhất phiên 0,904; cực trị rõ 0,960 |
| GC | M60 | đoạn chọn | 1,462 | 0,869 → **0,869** | 0,862 → **0,862** | 0,945 → **0,945** | 1,26% | 0,00% | 1,17 | Khớp chung 1,46; Khớp theo phiên 1,51/1,44/1,44; 20 ô lớn nhất ngày 0,869; 5 ô lớn nhất phiên 0,862; cực trị rõ 0,945 |
| GC | M60 | đoạn kiểm | 1,367 | 0,835 → **0,835** | 0,847 → **0,847** | 0,987 → **0,987** | 0,53% | 0,00% | 0,97 | Khớp chung 1,37; 20 ô lớn nhất ngày 0,835; 5 ô lớn nhất phiên 0,847 |
| NQ | M1 | đoạn chọn | 1,159 | 0,998 → **0,998** | 0,996 → **0,996** | 0,994 → **0,994** | 2,08% | 0,00% | 0,27 | 0 |
| NQ | M1 | đoạn kiểm | 0,956 | 1,000 → **1,000** | 1,000 → **1,000** | 0,997 → **0,997** | 0,27% | 0,00% | 0,37 | 0 |
| NQ | M5 | đoạn chọn | 1,296 | 0,938 → **0,938** | 0,949 → **0,949** | 0,987 → **0,987** | 2,96% | 0,00% | 0,62 | Khớp chung 1,3; 20 ô lớn nhất ngày 0,938; 5 ô lớn nhất phiên 0,949 |
| NQ | M5 | đoạn kiểm | 0,961 | 0,989 → **0,989** | 0,985 → **0,985** | 0,996 → **0,996** | 0,52% | 0,00% | 0,84 | 20 ô lớn nhất ngày 0,989 |
| NQ | M15 | đoạn chọn | 1,510 | 0,935 → **0,935** | 0,882 → **0,882** | 0,973 → **0,973** | 2,75% | 0,00% | 0,98 | Khớp chung 1,51; Khớp theo phiên 1,43/1,19/1,72; 20 ô lớn nhất ngày 0,935; 5 ô lớn nhất phiên 0,882 |
| NQ | M15 | đoạn kiểm | 1,009 | 0,986 → **0,986** | 0,966 → **0,966** | 0,987 → **0,987** | 0,74% | 0,00% | 1,29 | 20 ô lớn nhất ngày 0,986; 5 ô lớn nhất phiên 0,966 |
| NQ | M30 | đoạn chọn | 1,700 | 0,887 → **0,887** | 0,842 → **0,842** | 0,969 → **0,969** | 2,49% | 0,00% | 1,26 | Khớp chung 1,7; Khớp theo phiên 1,41/1,4/2,04; 20 ô lớn nhất ngày 0,887; 5 ô lớn nhất phiên 0,842; cực trị rõ 0,969 |
| NQ | M30 | đoạn kiểm | 1,113 | 0,970 → **0,970** | 0,969 → **0,969** | 0,974 → **0,974** | 1,37% | 0,00% | 1,62 | 20 ô lớn nhất ngày 0,970; 5 ô lớn nhất phiên 0,969 |
| NQ | M60 | đoạn chọn | 1,764 | 0,885 → **0,885** | 0,824 → **0,824** | 0,941 → **0,941** | 4,01% | 0,00% | 1,49 | Khớp chung 1,76; Khớp theo phiên 1,37/2,41/1,51; Khớp theo giờ 15/23 (giờ tệ nhất 20: 0,168); 20 ô lớn nhất ngày 0,885; 5 ô lớn nhất phiên 0,824; cực trị rõ 0,941 |
| NQ | M60 | đoạn kiểm | 1,056 | 0,973 → **0,973** | 0,920 → **0,920** | 0,974 → **0,974** | 0,65% | 0,00% | 1,85 | Khớp theo giờ 18/24 (giờ tệ nhất 21: 0,0909); 20 ô lớn nhất ngày 0,973; 5 ô lớn nhất phiên 0,920 |

### Nền mới, tối thiểu 1 ngày

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 1,116 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,11% | 0,00% | 0,40 | 0 |
| GC | M1 | đoạn kiểm | 1,077 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,14% | 0,00% | 0,35 | 0 |
| GC | M5 | đoạn chọn | 1,167 | 1,000 → **1,000** | 1,000 → **1,000** | 0,998 → **0,998** | 0,26% | 0,00% | 0,99 | 0 |
| GC | M5 | đoạn kiểm | 1,131 | 1,000 → **1,000** | 1,000 → **1,000** | 0,997 → **0,997** | 0,25% | 0,00% | 0,87 | 0 |
| GC | M15 | đoạn chọn | 1,236 | 0,999 → **0,999** | 0,998 → **0,998** | 0,993 → **0,993** | 0,40% | 0,00% | 1,57 | 0 |
| GC | M15 | đoạn kiểm | 1,183 | 1,000 → **1,000** | 1,000 → **1,000** | 0,990 → **0,990** | 0,50% | 0,00% | 1,37 | 0 |
| GC | M30 | đoạn chọn | 1,303 | 0,997 → **0,997** | 0,998 → **0,998** | 0,987 → **0,987** | 0,22% | 0,00% | 2,02 | Khớp chung 1,3 |
| GC | M30 | đoạn kiểm | 1,223 | 0,996 → **0,996** | 0,987 → **0,987** | 0,989 → **0,989** | 0,39% | 0,00% | 1,74 | 0 |
| GC | M60 | đoạn chọn | 1,266 | 0,995 → **0,995** | 0,995 → **0,995** | 0,993 → **0,993** | 0,29% | 0,00% | 2,38 | Khớp chung 1,27 |
| GC | M60 | đoạn kiểm | 1,176 | 0,981 → **0,981** | 0,992 → **0,992** | 0,994 → **0,994** | 0,25% | 0,00% | 2,05 | 20 ô lớn nhất ngày 0,981 |
| NQ | M1 | đoạn chọn | 1,110 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 1,50% | 0,00% | 0,76 | 0 |
| NQ | M1 | đoạn kiểm | 0,943 | 1,000 → **1,000** | 1,000 → **1,000** | 0,999 → **0,999** | 0,26% | 0,00% | 1,00 | 0 |
| NQ | M5 | đoạn chọn | 1,159 | 1,000 → **1,000** | 0,976 → **0,976** | 0,998 → **0,998** | 1,79% | 0,00% | 1,52 | 0 |
| NQ | M5 | đoạn kiểm | 0,940 | 1,000 → **1,000** | 0,991 → **0,991** | 0,997 → **0,997** | 0,42% | 0,00% | 1,91 | 0 |
| NQ | M15 | đoạn chọn | 1,254 | 1,000 → **1,000** | 0,909 → **0,909** | 0,992 → **0,992** | 1,30% | 0,00% | 2,15 | Khớp chung 1,25; 5 ô lớn nhất phiên 0,909 |
| NQ | M15 | đoạn kiểm | 0,931 | 1,000 → **1,000** | 0,978 → **0,978** | 0,994 → **0,994** | 0,41% | 0,00% | 2,60 | 0 |
| NQ | M30 | đoạn chọn | 1,363 | 0,993 → **0,993** | 0,882 → **0,882** | 0,988 → **0,988** | 1,88% | 0,00% | 2,56 | Khớp chung 1,36; 5 ô lớn nhất phiên 0,882 |
| NQ | M30 | đoạn kiểm | 0,973 | 1,000 → **1,000** | 0,972 → **0,972** | 0,992 → **0,992** | 0,71% | 0,00% | 2,99 | 0 |
| NQ | M60 | đoạn chọn | 1,301 | 1,000 → **1,000** | 0,980 → **0,980** | 0,993 → **0,993** | 2,77% | 0,00% | 2,84 | Khớp chung 1,3; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,176) |
| NQ | M60 | đoạn kiểm | 0,918 | 1,000 → **1,000** | 0,951 → **0,951** | 0,993 → **0,993** | 0,13% | 0,00% | 3,11 | 5 ô lớn nhất phiên 0,951 |

### Đối chứng: luật đang chạy, bộ "Không sót"

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | – | 1,000 → **0,795** | 1,000 → **0,807** | 0,997 → **0,796** | 0,35% | 0,00% | 0,75 | 20 ô lớn nhất ngày 0,795; 5 ô lớn nhất phiên 0,807; cực trị rõ 0,796 |
| GC | M1 | đoạn kiểm | – | 1,000 → **0,785** | 1,000 → **0,758** | 0,997 → **0,768** | 0,23% | 0,00% | 0,67 | 20 ô lớn nhất ngày 0,785; 5 ô lớn nhất phiên 0,758; cực trị rõ 0,768 |
| GC | M5 | đoạn chọn | – | 1,000 → **0,855** | 1,000 → **0,833** | 0,995 → **0,801** | 0,48% | 0,00% | 1,59 | 20 ô lớn nhất ngày 0,855; 5 ô lớn nhất phiên 0,833; cực trị rõ 0,801 |
| GC | M5 | đoạn kiểm | – | 1,000 → **0,825** | 1,000 → **0,823** | 0,988 → **0,790** | 0,65% | 0,00% | 1,35 | 20 ô lớn nhất ngày 0,825; 5 ô lớn nhất phiên 0,823; cực trị rõ 0,790 |
| GC | M15 | đoạn chọn | – | 1,000 → **0,876** | 1,000 → **0,881** | 0,979 → **0,841** | 0,70% | 0,00% | 1,86 | 20 ô lớn nhất ngày 0,876; 5 ô lớn nhất phiên 0,881; cực trị rõ 0,841 |
| GC | M15 | đoạn kiểm | – | 1,000 → **0,850** | 1,000 → **0,844** | 0,967 → **0,811** | 1,53% | 0,00% | 1,57 | 20 ô lớn nhất ngày 0,850; 5 ô lớn nhất phiên 0,844; cực trị rõ 0,811 |
| GC | M30 | đoạn chọn | – | 1,000 → **0,901** | 1,000 → **0,910** | 0,962 → **0,843** | 1,56% | 0,00% | 2,04 | 20 ô lớn nhất ngày 0,901; 5 ô lớn nhất phiên 0,910; cực trị rõ 0,843 |
| GC | M30 | đoạn kiểm | – | 0,994 → **0,852** | 0,997 → **0,870** | 0,955 → **0,826** | 1,72% | 0,00% | 1,69 | 20 ô lớn nhất ngày 0,852; 5 ô lớn nhất phiên 0,870; cực trị rõ 0,826 |
| GC | M60 | đoạn chọn | – | 0,987 → **0,876** | 0,984 → **0,905** | 0,948 → **0,834** | 0,81% | 0,00% | 2,24 | 20 ô lớn nhất ngày 0,876; 5 ô lớn nhất phiên 0,905; cực trị rõ 0,834 |
| GC | M60 | đoạn kiểm | – | 0,983 → **0,863** | 0,974 → **0,857** | 0,939 → **0,830** | 2,08% | 0,00% | 1,81 | 20 ô lớn nhất ngày 0,863; 5 ô lớn nhất phiên 0,857; cực trị rõ 0,830 |
| NQ | M1 | đoạn chọn | – | 1,000 → **0,773** | 1,000 → **0,831** | 0,986 → **0,825** | 1,80% | 0,00% | 0,97 | 20 ô lớn nhất ngày 0,773; 5 ô lớn nhất phiên 0,831; cực trị rõ 0,825 |
| NQ | M1 | đoạn kiểm | – | 1,000 → **0,775** | 1,000 → **0,892** | 0,991 → **0,856** | 2,97% | 0,00% | 1,26 | 20 ô lớn nhất ngày 0,775; 5 ô lớn nhất phiên 0,892; cực trị rõ 0,856 |
| NQ | M5 | đoạn chọn | – | 1,000 → **0,790** | 0,996 → **0,836** | 0,927 → **0,792** | 2,12% | 0,00% | 1,80 | 20 ô lớn nhất ngày 0,790; 5 ô lớn nhất phiên 0,836; cực trị rõ 0,792 |
| NQ | M5 | đoạn kiểm | – | 1,000 → **0,834** | 1,000 → **0,945** | 0,941 → **0,817** | 1,98% | 0,00% | 2,44 | 20 ô lớn nhất ngày 0,834; 5 ô lớn nhất phiên 0,945; cực trị rõ 0,817 |
| NQ | M15 | đoạn chọn | – | 1,000 → **0,835** | 0,976 → **0,867** | 0,885 → **0,776** | 2,26% | 0,00% | 2,04 | 20 ô lớn nhất ngày 0,835; 5 ô lớn nhất phiên 0,867; cực trị rõ 0,776 |
| NQ | M15 | đoạn kiểm | – | 1,000 → **0,818** | 0,997 → **0,951** | 0,915 → **0,815** | 1,58% | 0,00% | 2,74 | 20 ô lớn nhất ngày 0,818; 5 ô lớn nhất phiên 0,951; cực trị rõ 0,815 |
| NQ | M30 | đoạn chọn | – | 1,000 → **0,810** | 0,956 → **0,847** | 0,852 → **0,750** | 2,40% | 0,00% | 2,13 | 20 ô lớn nhất ngày 0,810; 5 ô lớn nhất phiên 0,847; cực trị rõ 0,750 |
| NQ | M30 | đoạn kiểm | – | 0,998 → **0,880** | 0,975 → **0,954** | 0,893 → **0,809** | 1,53% | 0,00% | 2,82 | 20 ô lớn nhất ngày 0,880; 5 ô lớn nhất phiên 0,954; cực trị rõ 0,809 |
| NQ | M60 | đoạn chọn | – | 0,968 → **0,825** | 0,856 → **0,769** | 0,797 → **0,702** | 2,24% | 0,00% | 2,22 | 20 ô lớn nhất ngày 0,825; 5 ô lớn nhất phiên 0,769; cực trị rõ 0,702 |
| NQ | M60 | đoạn kiểm | – | 0,995 → **0,907** | 0,895 → **0,858** | 0,868 → **0,795** | 2,42% | 0,00% | 3,07 | 20 ô lớn nhất ngày 0,907; 5 ô lớn nhất phiên 0,858; cực trị rõ 0,795 |

### Đối chứng: luật đang chạy, bộ "Ít nhiễu"

| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | – | 1,000 → **0,722** | 1,000 → **0,724** | 0,984 → **0,739** | 0,79% | 0,00% | 0,49 | 20 ô lớn nhất ngày 0,722; 5 ô lớn nhất phiên 0,724; cực trị rõ 0,739 |
| GC | M1 | đoạn kiểm | – | 1,000 → **0,756** | 1,000 → **0,738** | 0,986 → **0,735** | 1,04% | 0,00% | 0,41 | 20 ô lớn nhất ngày 0,756; 5 ô lớn nhất phiên 0,738; cực trị rõ 0,735 |
| GC | M5 | đoạn chọn | – | 1,000 → **0,795** | 1,000 → **0,791** | 0,984 → **0,763** | 1,33% | 0,00% | 0,80 | 20 ô lớn nhất ngày 0,795; 5 ô lớn nhất phiên 0,791; cực trị rõ 0,763 |
| GC | M5 | đoạn kiểm | – | 1,000 → **0,771** | 1,000 → **0,784** | 0,978 → **0,742** | 1,46% | 0,00% | 0,65 | 20 ô lớn nhất ngày 0,771; 5 ô lớn nhất phiên 0,784; cực trị rõ 0,742 |
| GC | M15 | đoạn chọn | – | 0,999 → **0,790** | 1,000 → **0,810** | 0,955 → **0,762** | 2,30% | 0,00% | 0,89 | 20 ô lớn nhất ngày 0,790; 5 ô lớn nhất phiên 0,810; cực trị rõ 0,762 |
| GC | M15 | đoạn kiểm | – | 0,990 → **0,763** | 0,995 → **0,790** | 0,931 → **0,731** | 2,73% | 0,00% | 0,69 | 20 ô lớn nhất ngày 0,763; 5 ô lớn nhất phiên 0,790; cực trị rõ 0,731 |
| GC | M30 | đoạn chọn | – | 0,979 → **0,771** | 0,993 → **0,809** | 0,931 → **0,742** | 2,67% | 0,00% | 0,91 | 20 ô lớn nhất ngày 0,771; 5 ô lớn nhất phiên 0,809; cực trị rõ 0,742 |
| GC | M30 | đoạn kiểm | – | 0,915 → **0,681** | 0,948 → **0,738** | 0,915 → **0,705** | 3,41% | 0,00% | 0,73 | 20 ô lớn nhất ngày 0,681; 5 ô lớn nhất phiên 0,738; cực trị rõ 0,705 |
| GC | M60 | đoạn chọn | – | 0,912 → **0,687** | 0,922 → **0,745** | 0,869 → **0,672** | 1,35% | 0,00% | 1,01 | 20 ô lớn nhất ngày 0,687; 5 ô lớn nhất phiên 0,745; cực trị rõ 0,672 |
| GC | M60 | đoạn kiểm | – | 0,815 → **0,625** | 0,870 → **0,696** | 0,884 → **0,687** | 2,97% | 0,00% | 0,75 | 20 ô lớn nhất ngày 0,625; 5 ô lớn nhất phiên 0,696; cực trị rõ 0,687 |
| NQ | M1 | đoạn chọn | – | 1,000 → **0,662** | 1,000 → **0,756** | 0,934 → **0,745** | 2,42% | 0,00% | 0,58 | 20 ô lớn nhất ngày 0,662; 5 ô lớn nhất phiên 0,756; cực trị rõ 0,745 |
| NQ | M1 | đoạn kiểm | – | 1,000 → **0,684** | 1,000 → **0,797** | 0,940 → **0,750** | 3,08% | 0,00% | 0,80 | 20 ô lớn nhất ngày 0,684; 5 ô lớn nhất phiên 0,797; cực trị rõ 0,750 |
| NQ | M5 | đoạn chọn | – | 1,000 → **0,605** | 0,991 → **0,700** | 0,835 → **0,626** | 3,55% | 0,00% | 0,83 | 20 ô lớn nhất ngày 0,605; 5 ô lớn nhất phiên 0,700; cực trị rõ 0,626 |
| NQ | M5 | đoạn kiểm | – | 1,000 → **0,670** | 1,000 → **0,791** | 0,869 → **0,643** | 3,62% | 0,00% | 1,23 | 20 ô lớn nhất ngày 0,670; 5 ô lớn nhất phiên 0,791; cực trị rõ 0,643 |
| NQ | M15 | đoạn chọn | – | 0,990 → **0,620** | 0,962 → **0,664** | 0,734 → **0,530** | 4,21% | 0,00% | 0,89 | 20 ô lớn nhất ngày 0,620; 5 ô lớn nhất phiên 0,664; cực trị rõ 0,530 |
| NQ | M15 | đoạn kiểm | – | 1,000 → **0,652** | 0,982 → **0,769** | 0,801 → **0,580** | 3,59% | 0,00% | 1,35 | 20 ô lớn nhất ngày 0,652; 5 ô lớn nhất phiên 0,769; cực trị rõ 0,580 |
| NQ | M30 | đoạn chọn | – | 0,900 → **0,558** | 0,929 → **0,671** | 0,648 → **0,464** | 4,62% | 0,00% | 0,93 | 20 ô lớn nhất ngày 0,558; 5 ô lớn nhất phiên 0,671; cực trị rõ 0,464 |
| NQ | M30 | đoạn kiểm | – | 0,975 → **0,675** | 0,945 → **0,775** | 0,750 → **0,532** | 3,78% | 0,00% | 1,39 | 20 ô lớn nhất ngày 0,675; 5 ô lớn nhất phiên 0,775; cực trị rõ 0,532 |
| NQ | M60 | đoạn chọn | – | 0,780 → **0,457** | 0,749 → **0,491** | 0,603 → **0,400** | 5,60% | 0,00% | 1,02 | 20 ô lớn nhất ngày 0,457; 5 ô lớn nhất phiên 0,491; cực trị rõ 0,400; nhiễu 0,056 |
| NQ | M60 | đoạn kiểm | – | 0,945 → **0,618** | 0,825 → **0,612** | 0,720 → **0,481** | 4,49% | 0,00% | 1,57 | 20 ô lớn nhất ngày 0,618; 5 ô lớn nhất phiên 0,612; cực trị rõ 0,481 |

## 4. Mật độ: nền mới và chọn "lớn hơn hẳn"

Chấm/nến tính trên nến có ngưỡng. "Vượt thô" = số ô vượt ngưỡng mỗi nến trước bước chọn (như nhau ở hai cách chọn). Theo ngày = chấm/nến của từng ngày giao dịch.

| Mã | Khung | Đoạn | Cách chọn | Chấm/nến | Á | Âu | Mỹ | Một nến: P50 / P95 / lớn nhất | Vượt thô/nến (P95, lớn nhất) | Theo ngày: nhỏ nhất / P10 / P50 / P90 / lớn nhất |
|---|---|---|---|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | tham lam | 0,40 | 0,33 | 0,43 | 0,45 | 0 / 2 / 22 | 0,58 (3, 68) | 0,19 / 0,29 / 0,38 / 0,53 / 0,66 |
| GC | M1 | đoạn chọn | lớn hơn hẳn | 0,38 | 0,32 | 0,41 | 0,43 | 0 / 2 / 21 | 0,58 (3, 68) | 0,18 / 0,28 / 0,37 / 0,51 / 0,63 |
| GC | M1 | đoạn kiểm | tham lam | 0,35 | 0,33 | 0,36 | 0,37 | 0 / 2 / 26 | 0,50 (2, 54) | 0,19 / 0,24 / 0,34 / 0,45 / 0,62 |
| GC | M1 | đoạn kiểm | lớn hơn hẳn | 0,34 | 0,32 | 0,34 | 0,36 | 0 / 2 / 21 | 0,50 (2, 54) | 0,19 / 0,23 / 0,32 / 0,43 / 0,59 |
| GC | M5 | đoạn chọn | tham lam | 0,99 | 0,90 | 1,04 | 1,05 | 0 / 4 / 35 | 1,82 (8, 79) | 0,40 / 0,71 / 0,96 / 1,36 / 1,63 |
| GC | M5 | đoạn chọn | lớn hơn hẳn | 0,94 | 0,85 | 0,99 | 1,00 | 0 / 3 / 33 | 1,82 (8, 79) | 0,40 / 0,70 / 0,92 / 1,27 / 1,51 |
| GC | M5 | đoạn kiểm | tham lam | 0,87 | 0,89 | 0,87 | 0,85 | 0 / 3 / 17 | 1,53 (7, 47) | 0,45 / 0,61 / 0,85 / 1,21 / 1,39 |
| GC | M5 | đoạn kiểm | lớn hơn hẳn | 0,82 | 0,84 | 0,83 | 0,80 | 0 / 3 / 16 | 1,53 (7, 47) | 0,44 / 0,59 / 0,82 / 1,14 / 1,28 |
| GC | M15 | đoạn chọn | tham lam | 1,57 | 1,48 | 1,65 | 1,62 | 1 / 5 / 28 | 3,73 (16, 99) | 0,61 / 1,16 / 1,56 / 2,03 / 2,67 |
| GC | M15 | đoạn chọn | lớn hơn hẳn | 1,47 | 1,38 | 1,54 | 1,51 | 1 / 4 / 24 | 3,73 (16, 99) | 0,61 / 1,11 / 1,43 / 1,84 / 2,40 |
| GC | M15 | đoạn kiểm | tham lam | 1,37 | 1,48 | 1,36 | 1,25 | 1 / 4 / 15 | 3,07 (14, 67) | 0,72 / 0,89 / 1,26 / 1,95 / 2,39 |
| GC | M15 | đoạn kiểm | lớn hơn hẳn | 1,29 | 1,38 | 1,28 | 1,19 | 1 / 4 / 13 | 3,07 (14, 67) | 0,70 / 0,85 / 1,22 / 1,78 / 2,14 |
| GC | M30 | đoạn chọn | tham lam | 2,02 | 1,96 | 2,10 | 2,02 | 2 / 6 / 24 | 5,83 (25, 262) | 0,85 / 1,40 / 1,96 / 2,67 / 3,59 |
| GC | M30 | đoạn chọn | lớn hơn hẳn | 1,85 | 1,79 | 1,93 | 1,86 | 2 / 5 / 20 | 5,83 (25, 262) | 0,78 / 1,33 / 1,83 / 2,37 / 3,11 |
| GC | M30 | đoạn kiểm | tham lam | 1,74 | 1,97 | 1,66 | 1,53 | 1 / 5 / 21 | 4,69 (19, 94) | 0,93 / 1,11 / 1,70 / 2,37 / 2,85 |
| GC | M30 | đoạn kiểm | lớn hơn hẳn | 1,62 | 1,83 | 1,53 | 1,43 | 1 / 4 / 18 | 4,69 (19, 94) | 0,93 / 1,07 / 1,60 / 2,14 / 2,50 |
| GC | M60 | đoạn chọn | tham lam | 2,39 | 2,34 | 2,67 | 2,17 | 2 / 7 / 24 | 8,61 (37, 288) | 0,90 / 1,51 / 2,22 / 3,61 / 4,35 |
| GC | M60 | đoạn chọn | lớn hơn hẳn | 2,19 | 2,12 | 2,44 | 2,01 | 2 / 6 / 19 | 8,61 (37, 288) | 0,90 / 1,38 / 2,09 / 3,11 / 3,67 |
| GC | M60 | đoạn kiểm | tham lam | 2,05 | 2,27 | 2,21 | 1,61 | 2 / 6 / 15 | 6,63 (29, 95) | 0,96 / 1,39 / 1,93 / 2,98 / 3,35 |
| GC | M60 | đoạn kiểm | lớn hơn hẳn | 1,90 | 2,09 | 2,06 | 1,52 | 2 / 5 / 11 | 6,63 (29, 95) | 0,96 / 1,37 / 1,80 / 2,67 / 2,83 |
| NQ | M1 | đoạn chọn | tham lam | 0,75 | 0,59 | 0,69 | 0,99 | 0 / 3 / 20 | 1,33 (6, 134) | 0,35 / 0,56 / 0,71 / 1,04 / 1,09 |
| NQ | M1 | đoạn chọn | lớn hơn hẳn | 0,70 | 0,55 | 0,65 | 0,92 | 0 / 3 / 18 | 1,33 (6, 134) | 0,34 / 0,54 / 0,68 / 0,96 / 1,01 |
| NQ | M1 | đoạn kiểm | tham lam | 1,00 | 0,86 | 0,82 | 1,29 | 1 / 4 / 28 | 1,92 (8, 208) | 0,65 / 0,75 / 0,95 / 1,34 / 1,55 |
| NQ | M1 | đoạn kiểm | lớn hơn hẳn | 0,94 | 0,82 | 0,78 | 1,20 | 1 / 3 / 27 | 1,92 (8, 208) | 0,61 / 0,72 / 0,90 / 1,26 / 1,41 |
| NQ | M5 | đoạn chọn | tham lam | 1,50 | 1,42 | 1,51 | 1,60 | 1 / 5 / 16 | 3,85 (16, 289) | 0,63 / 1,12 / 1,46 / 2,02 / 2,19 |
| NQ | M5 | đoạn chọn | lớn hơn hẳn | 1,39 | 1,32 | 1,40 | 1,46 | 1 / 4 / 11 | 3,85 (16, 289) | 0,59 / 1,07 / 1,36 / 1,80 / 1,97 |
| NQ | M5 | đoạn kiểm | tham lam | 1,91 | 1,88 | 1,78 | 2,05 | 2 / 5 / 39 | 5,39 (20, 193) | 1,25 / 1,45 / 1,91 / 2,52 / 2,78 |
| NQ | M5 | đoạn kiểm | lớn hơn hẳn | 1,76 | 1,73 | 1,65 | 1,89 | 1 / 5 / 35 | 5,39 (20, 193) | 1,17 / 1,34 / 1,75 / 2,32 / 2,46 |
| NQ | M15 | đoạn chọn | tham lam | 2,12 | 2,16 | 2,20 | 2,01 | 2 / 6 / 16 | 7,80 (30, 334) | 0,85 / 1,62 / 2,12 / 2,68 / 3,01 |
| NQ | M15 | đoạn chọn | lớn hơn hẳn | 1,92 | 1,95 | 2,00 | 1,83 | 2 / 5 / 10 | 7,80 (30, 334) | 0,79 / 1,48 / 1,90 / 2,43 / 2,63 |
| NQ | M15 | đoạn kiểm | tham lam | 2,60 | 2,75 | 2,57 | 2,48 | 2 / 6 / 25 | 10,24 (39, 310) | 1,72 / 1,82 / 2,61 / 3,31 / 3,82 |
| NQ | M15 | đoạn kiểm | lớn hơn hẳn | 2,37 | 2,51 | 2,36 | 2,24 | 2 / 5 / 22 | 10,24 (39, 310) | 1,59 / 1,75 / 2,36 / 2,93 / 3,27 |
| NQ | M30 | đoạn chọn | tham lam | 2,52 | 2,56 | 2,61 | 2,39 | 2 / 6 / 14 | 12,00 (45, 478) | 0,96 / 1,95 / 2,53 / 3,23 / 3,76 |
| NQ | M30 | đoạn chọn | lớn hơn hẳn | 2,26 | 2,29 | 2,34 | 2,15 | 2 / 5 / 11 | 12,00 (45, 478) | 0,87 / 1,85 / 2,26 / 2,85 / 3,26 |
| NQ | M30 | đoạn kiểm | tham lam | 2,99 | 3,20 | 2,97 | 2,78 | 3 / 7 / 20 | 15,80 (55, 387) | 1,80 / 2,19 / 2,98 / 3,97 / 4,02 |
| NQ | M30 | đoạn kiểm | lớn hơn hẳn | 2,67 | 2,84 | 2,71 | 2,47 | 2 / 6 / 16 | 15,80 (55, 387) | 1,63 / 2,05 / 2,61 / 3,40 / 3,52 |
| NQ | M60 | đoạn chọn | tham lam | 2,77 | 2,91 | 3,00 | 2,36 | 3 / 6 / 16 | 16,92 (59, 520) | 1,30 / 2,17 / 2,70 / 3,53 / 4,35 |
| NQ | M60 | đoạn chọn | lớn hơn hẳn | 2,46 | 2,61 | 2,64 | 2,10 | 2 / 5 / 10 | 16,92 (59, 520) | 1,26 / 1,95 / 2,39 / 3,10 / 3,85 |
| NQ | M60 | đoạn kiểm | tham lam | 3,11 | 3,51 | 2,96 | 2,82 | 3 / 6 / 13 | 22,23 (92, 412) | 1,87 / 2,19 / 3,07 / 3,96 / 4,04 |
| NQ | M60 | đoạn kiểm | lớn hơn hẳn | 2,79 | 3,05 | 2,72 | 2,56 | 3 / 6 / 10 | 22,23 (92, 412) | 1,65 / 2,18 / 2,76 / 3,39 / 3,65 |

Tăng số chấm khi đổi "lớn hơn hẳn" sang tham lam (chấm/nến, %):

| Mã | Đoạn | M1 | M5 | M15 | M30 | H1 |
|---|---|---|---|---|---|---|
| GC | đoạn chọn | +3,9% | +5,2% | +7,1% | +8,9% | +9,2% |
| GC | đoạn kiểm | +4,0% | +5,7% | +6,2% | +7,6% | +7,6% |
| NQ | đoạn chọn | +6,3% | +8,3% | +10,3% | +11,6% | +12,3% |
| NQ | đoạn kiểm | +6,3% | +8,5% | +9,7% | +11,8% | +11,7% |

Ngưỡng theo phiên (hợp đồng, P50 và khoảng P10–P90 của ngưỡng mỗi nến; như nhau ở hai cách chọn):

| Mã | Khung | Đoạn | Á | Âu | Mỹ | Nến có ngưỡng chính / dự phòng / chưa có |
|---|---|---|---|---|---|---|
| GC | M1 | đoạn chọn | 11 (10–14) | 14 (13–19) | 16 (13–20) | 95,0% / 5,0% / 0,02% |
| GC | M1 | đoạn kiểm | 12 (10–15) | 16 (14–20) | 18 (13–21) | 100,0% / 0,0% / 0,00% |
| GC | M5 | đoạn chọn | 18 (15–22) | 24 (20–31) | 27 (20–34) | 94,8% / 5,2% / 0,04% |
| GC | M5 | đoạn kiểm | 19 (16–24) | 26 (22–35) | 31 (22–38) | 100,0% / 0,0% / 0,00% |
| GC | M15 | đoạn chọn | 25 (21–32) | 35 (29–45) | 40 (30–51) | 94,8% / 5,1% / 0,06% |
| GC | M15 | đoạn kiểm | 28 (22–35) | 39 (31–52) | 47 (32–60) | 100,0% / 0,0% / 0,00% |
| GC | M30 | đoạn chọn | 32 (25–41) | 45 (36–61) | 55 (38–68) | 94,8% / 5,1% / 0,11% |
| GC | M30 | đoạn kiểm | 37 (28–45) | 50 (41–74) | 62 (41–83) | 100,0% / 0,0% / 0,00% |
| GC | M60 | đoạn chọn | 43 (34–54) | 62 (50–83) | 71 (55–91) | 94,8% / 5,1% / 0,11% |
| GC | M60 | đoạn kiểm | 50 (40–58) | 72 (58–88) | 86 (62–103) | 100,0% / 0,0% / 0,00% |
| NQ | M1 | đoạn chọn | 10 (8–11) | 11 (9–17) | 31 (25–45) | 93,3% / 6,7% / 0,01% |
| NQ | M1 | đoạn kiểm | 9 (8–10) | 10 (8–13) | 27 (20–35) | 100,0% / 0,0% / 0,00% |
| NQ | M5 | đoạn chọn | 16 (13–19) | 18 (14–32) | 60 (51–90) | 93,3% / 6,7% / 0,02% |
| NQ | M5 | đoạn kiểm | 15 (13–17) | 17 (13–23) | 54 (38–76) | 100,0% / 0,0% / 0,00% |
| NQ | M15 | đoạn chọn | 25 (18–29) | 27 (21–50) | 98 (79–135) | 93,3% / 6,6% / 0,04% |
| NQ | M15 | đoạn kiểm | 22 (19–26) | 25 (20–35) | 90 (62–116) | 100,0% / 0,0% / 0,00% |
| NQ | M30 | đoạn chọn | 32 (26–40) | 35 (28–68) | 131 (102–177) | 93,3% / 6,6% / 0,07% |
| NQ | M30 | đoạn kiểm | 29 (25–34) | 33 (27–48) | 120 (83–155) | 100,0% / 0,0% / 0,00% |
| NQ | M60 | đoạn chọn | 43 (36–51) | 50 (40–191) | 188 (160–227) | 93,3% / 6,5% / 0,15% |
| NQ | M60 | đoạn kiểm | 39 (34–47) | 46 (37–158) | 169 (134–200) | 100,0% / 0,0% / 0,00% |

## 5. "5 ô lớn nhất phiên" bị sót (số "nhìn thấy"), NQ M15 và M30, theo giờ UTC

| Khung | Đoạn | Cấu hình | Tổng ô sót / tổng ô | Giờ UTC: số ô sót (trong số ô top 5 rơi vào giờ đó) |
|---|---|---|---|---|
| M15 | đoạn chọn | không lân cận | 2 / 450 | 22:45: 1 (3), 19:45: 1 (64) |
| M15 | đoạn chọn | có lân cận | 39 / 450 | 13:15: 32 (49), 13:00: 6 (25), 22:45: 1 (3) |
| M15 | đoạn kiểm | không lân cận | 0 / 325 | không sót |
| M15 | đoạn kiểm | có lân cận | 7 / 325 | 13:15: 4 (13), 13:00: 3 (8) |
| M30 | đoạn chọn | không lân cận | 6 / 450 | 13:00: 5 (76), 22:30: 1 (9) |
| M30 | đoạn chọn | có lân cận | 51 / 450 | 13:00: 50 (76), 22:30: 1 (9) |
| M30 | đoạn kiểm | không lân cận | 1 / 325 | 13:00: 1 (21) |
| M30 | đoạn kiểm | có lân cận | 9 / 325 | 13:00: 9 (21) |

13:00–13:30 UTC là nửa giờ ngay trước giờ mở cửa cổ phiếu Mỹ (13:30 UTC). Có lân cận thì khung này mượn mẫu của khung 13:30 (mở cửa) nên ngưỡng bị kéo lên; không lân cận thì gần như hết sót ở giờ đó nhưng trượt Khớp chung ở nhiều ô hơn (mục 2).

## 6. Chart nạp ít ngày (nền mới; thêm tối thiểu 1 ngày và chọn "lớn hơn hẳn" để so)

Tỉ lệ trùng = số chấm có ở cả hai / số chấm có ở ít nhất một, trên những ngày có trong bản nạp ít (so với khi nạp đủ 90 ngày).

| Cấu hình | Nạp 3 ngày | Nạp 8 ngày | Nạp 15 ngày |
|---|---|---|---|
| Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam) | 0,695 | 0,870 | 0,915 |
| Nền mới, tối thiểu 1 ngày | 0,765 | 0,888 | 0,932 |
| Nền mới, chọn "lớn hơn hẳn" như vòng 2 | 0,720 | 0,881 | 0,921 |

| Mã | Khung | Số ngày nạp | Nền mới: trùng (ngày thấp nhất) | Tối thiểu 1 ngày | Chọn "lớn hơn hẳn" | Nền mới theo ngày |
|---|---|---|---|---|---|---|
| GC | M1 | 3 | 0,668 (0,571) | 0,714 (0,681) | 0,679 (0,580) | 11-05:0,694 11-06:0,571 11-09:0,866 |
| GC | M1 | 8 | 0,859 (0,647) | 0,876 (0,693) | 0,866 (0,657) | 10-29:0,693 10-30:0,647 11-02:0,875 11-03:0,923 11-04:0,961 11-05:1,000 11-06:1,000 11-09:1,000 |
| GC | M1 | 15 | 0,918 (0,643) | 0,934 (0,692) | 0,921 (0,662) | (xem CSV) |
| GC | M5 | 3 | 0,605 (0,539) | 0,657 (0,603) | 0,630 (0,566) | 11-05:0,603 11-06:0,539 11-09:0,819 |
| GC | M5 | 8 | 0,842 (0,619) | 0,848 (0,622) | 0,846 (0,620) | 10-29:0,622 10-30:0,619 11-02:0,844 11-03:0,919 11-04:0,977 11-05:1,000 11-06:1,000 11-09:1,000 |
| GC | M5 | 15 | 0,908 (0,642) | 0,917 (0,651) | 0,911 (0,653) | (xem CSV) |
| GC | M15 | 3 | 0,594 (0,536) | 0,627 (0,593) | 0,615 (0,555) | 11-05:0,593 11-06:0,536 11-09:0,796 |
| GC | M15 | 8 | 0,794 (0,432) | 0,823 (0,432) | 0,803 (0,428) | 10-29:0,432 10-30:0,578 11-02:0,825 11-03:0,948 11-04:0,995 11-05:1,000 11-06:1,000 11-09:1,000 |
| GC | M15 | 15 | 0,915 (0,652) | 0,919 (0,652) | 0,918 (0,673) | (xem CSV) |
| NQ | M1 | 3 | 0,718 (0,654) | 0,797 (0,726) | 0,741 (0,686) | 11-20:0,726 11-23:0,654 11-24:0,866 |
| NQ | M1 | 8 | 0,888 (0,682) | 0,906 (0,703) | 0,898 (0,710) | 11-13:0,703 11-16:0,682 11-17:0,889 11-18:0,925 11-19:0,976 11-20:1,000 11-23:1,000 11-24:1,000 |
| NQ | M1 | 15 | 0,916 (0,596) | 0,934 (0,736) | 0,922 (0,618) | (xem CSV) |
| NQ | M5 | 3 | 0,718 (0,663) | 0,789 (0,724) | 0,752 (0,698) | 11-20:0,724 11-23:0,663 11-24:0,837 |
| NQ | M5 | 8 | 0,872 (0,670) | 0,891 (0,670) | 0,885 (0,700) | 11-13:0,670 11-16:0,674 11-17:0,874 11-18:0,889 11-19:0,968 11-20:1,000 11-23:1,000 11-24:1,000 |
| NQ | M5 | 15 | 0,915 (0,569) | 0,932 (0,721) | 0,925 (0,602) | (xem CSV) |
| NQ | M15 | 3 | 0,675 (0,638) | 0,752 (0,638) | 0,730 (0,690) | 11-20:0,638 11-23:0,640 11-24:0,843 |
| NQ | M15 | 8 | 0,856 (0,599) | 0,881 (0,599) | 0,881 (0,652) | 11-13:0,599 11-16:0,681 11-17:0,892 11-18:0,872 11-19:0,957 11-20:1,000 11-23:1,000 11-24:1,000 |
| NQ | M15 | 15 | 0,908 (0,526) | 0,934 (0,736) | 0,920 (0,567) | (xem CSV) |

Ngày đầu tiên của bản nạp ít luôn thấp nhất: mọi khung giờ còn đang dùng ngưỡng dự phòng (120 phút gần nhất) vì chưa có ngày trước.

## 7. So tham khảo với chart CORVEN (M1, chỉ báo số, không chỉnh theo)

| Mã | Cấu hình | Nến mẫu | Chấm CORVEN/nến | Chấm mình/nến | Bắt được chấm CORVEN | Chấm mình trùng CORVEN | F1 |
|---|---|---|---|---|---|---|---|
| GC | Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam) | 580 | 1,53 | 0,28 | 22,3% | 99,4% | 0,364 |
| GC | Nền mới, chọn "lớn hơn hẳn" như vòng 2 | 580 | 1,53 | 0,27 | 22,3% | 99,4% | 0,364 |
| GC | Đối chứng: luật đang chạy, bộ "Không sót" | 580 | 1,53 | 0,83 | 59,9% | 90,0% | 0,719 |
| GC | Đối chứng: luật đang chạy, bộ "Ít nhiễu" | 580 | 1,53 | 0,57 | 45,6% | 97,6% | 0,622 |
| NQ | Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam) | 534 | 2,26 | 0,60 | 19,9% | 58,9% | 0,298 |
| NQ | Nền mới, chọn "lớn hơn hẳn" như vòng 2 | 534 | 2,26 | 0,58 | 18,9% | 57,7% | 0,285 |
| NQ | Đối chứng: luật đang chạy, bộ "Không sót" | 534 | 2,26 | 1,10 | 28,1% | 45,6% | 0,348 |
| NQ | Đối chứng: luật đang chạy, bộ "Ít nhiễu" | 534 | 2,26 | 0,88 | 23,6% | 47,6% | 0,316 |

NQ: chart CORVEN gộp hàng 8 tick nên so khớp kém tin cậy hơn GC.

## 8. Số chuẩn cho C# (bản chuẩn `sa3_ref.py`, đọc đúng file của Golden)

Theo ngày UTC: `out_r3_chuan_ngay.csv`. Lệnh, sha1 từng file đầu vào và đường dẫn file dấu: `out_r3_chuan.csv`.

| Dòng | Số nến | Chấm đỏ (Bid) | Chấm xanh (Ask) | Big Trade | Nến ngưỡng chính / dự phòng / chưa có | sha1 footprint (8 ký tự đầu) |
|---|---|---|---|---|---|---|
| GC_m1_nen_moi | 87.362 | 16.767 | 16.505 | – | 84.748 / 2.604 / 10 | f43f3762 |
| GC_m1_sel_lmax | 87.362 | 16.087 | 15.914 | – | 84.748 / 2.604 / 10 | f43f3762 |
| GC_m1_p1 | 87.362 | 9.587 | 9.441 | – | 84.748 / 2.594 / 20 | f43f3762 |
| GC_m1_khong_lan_can | 87.362 | 17.553 | 17.305 | – | 84.748 / 2.604 / 10 | f43f3762 |
| GC_m5_nen_moi | 17.623 | 8.332 | 8.260 | – | 17.071 / 548 / 4 | c16af95c |
| GC_m5_sel_lmax | 17.623 | 7.893 | 7.850 | – | 17.071 / 548 / 4 | c16af95c |
| GC_m5_p1 | 17.623 | 4.984 | 5.040 | – | 17.071 / 545 / 7 | c16af95c |
| GC_m5_khong_lan_can | 17.623 | 8.902 | 8.776 | – | 17.065 / 554 / 4 | c16af95c |
| GC_m5_sel_all | 17.623 | 15.050 | 14.965 | – | 17.071 / 548 / 4 | c16af95c |
| GC_m5_nap8ngay | 2.041 | 956 | 959 | – | 1.489 / 547 / 5 | 8ba5d1a8 |
| GC_m15_nen_moi | 5.875 | 4.342 | 4.425 | – | 5.691 / 182 / 2 | 0f5017ed |
| GC_m15_sel_lmax | 5.875 | 4.073 | 4.137 | – | 5.691 / 182 / 2 | 0f5017ed |
| GC_m15_p1 | 5.875 | 2.801 | 2.816 | – | 5.689 / 182 / 4 | 0f5017ed |
| GC_m15_khong_lan_can | 5.875 | 4.681 | 4.687 | – | 5.685 / 188 / 2 | 0f5017ed |
| GC_m60_nen_moi | 1.470 | 1.646 | 1.662 | – | 1.424 / 45 / 1 | 112440ea |
| GC_m60_sel_lmax | 1.470 | 1.512 | 1.534 | – | 1.424 / 45 / 1 | 112440ea |
| GC_m60_p1 | 1.470 | 1.148 | 1.158 | – | 1.424 / 44 / 2 | 112440ea |
| GC_m60_khong_lan_can | 1.470 | 1.771 | 1.805 | – | 1.423 / 46 / 1 | 112440ea |
| NQ_m1_nen_moi | 71.047 | 30.421 | 30.168 | – | 68.288 / 2.754 / 5 | 497ddab9 |
| NQ_m1_sel_lmax | 71.047 | 28.593 | 28.390 | – | 68.288 / 2.754 / 5 | 497ddab9 |
| NQ_m1_p1 | 71.047 | 18.782 | 18.230 | – | 68.288 / 2.748 / 11 | 497ddab9 |
| NQ_m1_khong_lan_can | 71.047 | 32.243 | 31.975 | – | 68.288 / 2.754 / 5 | 497ddab9 |
| NQ_m5_nen_moi | 14.210 | 11.988 | 11.808 | – | 13.658 / 550 / 2 | 7a44538e |
| NQ_m5_sel_lmax | 14.210 | 11.049 | 10.901 | – | 13.658 / 550 / 2 | 7a44538e |
| NQ_m5_p1 | 14.210 | 7.977 | 7.813 | – | 13.658 / 548 / 4 | 7a44538e |
| NQ_m5_khong_lan_can | 14.210 | 12.907 | 12.736 | – | 13.658 / 550 / 2 | 7a44538e |
| NQ_m15_nen_moi | 4.737 | 5.512 | 5.494 | – | 4.553 / 183 / 1 | 713fb4ab |
| NQ_m15_sel_lmax | 4.737 | 5.011 | 4.993 | – | 4.553 / 183 / 1 | 713fb4ab |
| NQ_m15_p1 | 4.737 | 3.855 | 3.841 | – | 4.553 / 182 / 2 | 713fb4ab |
| NQ_m15_khong_lan_can | 4.737 | 5.949 | 5.905 | – | 4.553 / 183 / 1 | 713fb4ab |
| NQ_m15_sel_all | 4.737 | 21.087 | 20.699 | – | 4.553 / 183 / 1 | 713fb4ab |
| NQ_m15_nap8ngay | 697 | 1.097 | 1.028 | – | 513 / 183 / 1 | b8209773 |
| NQ_m60_nen_moi | 1.185 | 1.727 | 1.720 | – | 1.139 / 45 / 1 | 19f944e8 |
| NQ_m60_sel_lmax | 1.185 | 1.528 | 1.549 | – | 1.139 / 45 / 1 | 19f944e8 |
| NQ_m60_p1 | 1.185 | 1.295 | 1.329 | – | 1.139 / 45 / 1 | 19f944e8 |
| NQ_m60_khong_lan_can | 1.185 | 1.904 | 1.940 | – | 1.139 / 45 / 1 | 19f944e8 |
| bt_NQ_M1 | 71.047 | 30.421 | 30.168 | 3.330 (vòng 2: 3.330, khớp) | 68.288 / 2.754 / 5; nến Big Trade có ngưỡng 8.331, chưa có 9 | 497ddab9 |
| bt_NQ_M15 | 4.737 | 5.512 | 5.494 | 864 (vòng 2: 864, khớp) | 4.553 / 183 / 1; nến Big Trade có ngưỡng 553, chưa có 3 | 713fb4ab |
| bt_GC_M5 | 17.623 | 8.332 | 8.260 | 1.913 (vòng 2: 1.913, khớp) | 17.071 / 548 / 4; nến Big Trade có ngưỡng 4.573, chưa có 21 | c16af95c |
| bt_GC_M30 | 2.938 | 2.770 | 2.829 | 788 (vòng 2: 788, khớp) | 2.846 / 90 / 2; nến Big Trade có ngưỡng 755, chưa có 11 | f76c5602 |

<details><summary>Lệnh đã chạy và sha1 đầy đủ</summary>

- `GC_m1_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m1.csv 1 0.1 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m1_nen_moi.csv`  
  sha1 footprint `f43f376241c004150fae25a88ce8046a42b1b04e`, bars `df15532af1bba76b9fc11fd40458643808881f70`
- `GC_m1_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m1.csv 1 0.1 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m1_sel_lmax.csv`  
  sha1 footprint `f43f376241c004150fae25a88ce8046a42b1b04e`, bars `df15532af1bba76b9fc11fd40458643808881f70`
- `GC_m1_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m1.csv 1 0.1 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m1_p1.csv`  
  sha1 footprint `f43f376241c004150fae25a88ce8046a42b1b04e`, bars `df15532af1bba76b9fc11fd40458643808881f70`
- `GC_m1_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m1.csv 1 0.1 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m1_khong_lan_can.csv`  
  sha1 footprint `f43f376241c004150fae25a88ce8046a42b1b04e`, bars `df15532af1bba76b9fc11fd40458643808881f70`
- `GC_m5_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_nen_moi.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`
- `GC_m5_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_sel_lmax.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`
- `GC_m5_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_p1.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`
- `GC_m5_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_khong_lan_can.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`
- `GC_m5_sel_all`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set sel=all --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_sel_all.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`
- `GC_m5_nap8ngay`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5_nap8.csv 5 0.1 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m5_nap8ngay.csv   (tương đương: python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --set bt=0 --from "2026-10-28 22:00" ...)`  
  sha1 footprint `8ba5d1a81302f9f38ba90f76e2773e03ab9df428`, bars `b088583eae592145544fd738565f318726abef9e`
- `GC_m15_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m15.csv 15 0.1 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m15_nen_moi.csv`  
  sha1 footprint `0f5017ed24e8c3faf138ccf119a9d69a3c8fbf15`, bars `4ca9233edbc473cfdf794cd2da265ac492e9e3cd`
- `GC_m15_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m15.csv 15 0.1 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m15_sel_lmax.csv`  
  sha1 footprint `0f5017ed24e8c3faf138ccf119a9d69a3c8fbf15`, bars `4ca9233edbc473cfdf794cd2da265ac492e9e3cd`
- `GC_m15_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m15.csv 15 0.1 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m15_p1.csv`  
  sha1 footprint `0f5017ed24e8c3faf138ccf119a9d69a3c8fbf15`, bars `4ca9233edbc473cfdf794cd2da265ac492e9e3cd`
- `GC_m15_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m15.csv 15 0.1 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m15_khong_lan_can.csv`  
  sha1 footprint `0f5017ed24e8c3faf138ccf119a9d69a3c8fbf15`, bars `4ca9233edbc473cfdf794cd2da265ac492e9e3cd`
- `GC_m60_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m60.csv 60 0.1 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m60_nen_moi.csv`  
  sha1 footprint `112440ea835e6bfc63abc1d53b805192e182d30a`, bars `2c7c7e2b431b977f6b2a9fd9b025575919a547a5`
- `GC_m60_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m60.csv 60 0.1 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m60_sel_lmax.csv`  
  sha1 footprint `112440ea835e6bfc63abc1d53b805192e182d30a`, bars `2c7c7e2b431b977f6b2a9fd9b025575919a547a5`
- `GC_m60_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m60.csv 60 0.1 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m60_p1.csv`  
  sha1 footprint `112440ea835e6bfc63abc1d53b805192e182d30a`, bars `2c7c7e2b431b977f6b2a9fd9b025575919a547a5`
- `GC_m60_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m60.csv 60 0.1 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_GC_m60_khong_lan_can.csv`  
  sha1 footprint `112440ea835e6bfc63abc1d53b805192e182d30a`, bars `2c7c7e2b431b977f6b2a9fd9b025575919a547a5`
- `NQ_m1_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m1.csv 1 0.25 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m1_nen_moi.csv`  
  sha1 footprint `497ddab9b8805d2c4298c990134584b68be451dd`, bars `14a956dd86d9d2cd2980dd6506608282473e06b7`
- `NQ_m1_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m1.csv 1 0.25 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m1_sel_lmax.csv`  
  sha1 footprint `497ddab9b8805d2c4298c990134584b68be451dd`, bars `14a956dd86d9d2cd2980dd6506608282473e06b7`
- `NQ_m1_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m1.csv 1 0.25 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m1_p1.csv`  
  sha1 footprint `497ddab9b8805d2c4298c990134584b68be451dd`, bars `14a956dd86d9d2cd2980dd6506608282473e06b7`
- `NQ_m1_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m1.csv 1 0.25 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m1_khong_lan_can.csv`  
  sha1 footprint `497ddab9b8805d2c4298c990134584b68be451dd`, bars `14a956dd86d9d2cd2980dd6506608282473e06b7`
- `NQ_m5_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m5.csv 5 0.25 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m5_nen_moi.csv`  
  sha1 footprint `7a44538ec1d5d610851c576a83d000bf162f52f5`, bars `df17ae7049c71e6d3b72ac4c6b8aac327e005c3d`
- `NQ_m5_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m5.csv 5 0.25 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m5_sel_lmax.csv`  
  sha1 footprint `7a44538ec1d5d610851c576a83d000bf162f52f5`, bars `df17ae7049c71e6d3b72ac4c6b8aac327e005c3d`
- `NQ_m5_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m5.csv 5 0.25 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m5_p1.csv`  
  sha1 footprint `7a44538ec1d5d610851c576a83d000bf162f52f5`, bars `df17ae7049c71e6d3b72ac4c6b8aac327e005c3d`
- `NQ_m5_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m5.csv 5 0.25 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m5_khong_lan_can.csv`  
  sha1 footprint `7a44538ec1d5d610851c576a83d000bf162f52f5`, bars `df17ae7049c71e6d3b72ac4c6b8aac327e005c3d`
- `NQ_m15_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_nen_moi.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`
- `NQ_m15_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_sel_lmax.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`
- `NQ_m15_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_p1.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`
- `NQ_m15_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_khong_lan_can.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`
- `NQ_m15_sel_all`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set sel=all --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_sel_all.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`
- `NQ_m15_nap8ngay`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15_nap8.csv 15 0.25 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m15_nap8ngay.csv   (tương đương: python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --set bt=0 --from "2026-11-12 23:00" ...)`  
  sha1 footprint `b82097734e6dbc88093928f3c80314c82e0402c8`, bars `b7e75303586f226ec52d25706e87e229a1cdd574`
- `NQ_m60_nen_moi`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m60.csv 60 0.25 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m60_nen_moi.csv`  
  sha1 footprint `19f944e80bd89b86535822344e8a7e23f7434f33`, bars `27018aeee02a679eee8563bf8e7a463a82491702`
- `NQ_m60_sel_lmax`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m60.csv 60 0.25 --set sel=lmax --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m60_sel_lmax.csv`  
  sha1 footprint `19f944e80bd89b86535822344e8a7e23f7434f33`, bars `27018aeee02a679eee8563bf8e7a463a82491702`
- `NQ_m60_p1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m60.csv 60 0.25 --set pbp=100 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m60_p1.csv`  
  sha1 footprint `19f944e80bd89b86535822344e8a7e23f7434f33`, bars `27018aeee02a679eee8563bf8e7a463a82491702`
- `NQ_m60_khong_lan_can`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m60.csv 60 0.25 --set lc=0 --set bt=0 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_NQ_m60_khong_lan_can.csv`  
  sha1 footprint `19f944e80bd89b86535822344e8a7e23f7434f33`, bars `27018aeee02a679eee8563bf8e7a463a82491702`
- `bt_NQ_M1`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m1.csv 1 0.25 --btlog C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\btlog_NQ_M1.csv --zeromot --set bt_w=A --set bt_T=240 --set bt_pbp=100 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_bt_NQ_M1.csv`  
  sha1 footprint `497ddab9b8805d2c4298c990134584b68be451dd`, bars `14a956dd86d9d2cd2980dd6506608282473e06b7`, nhật ký `ec1fe48e1155628179e67adec3399162b5988ea8`
- `bt_NQ_M15`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_NQ_m15.csv 15 0.25 --btlog C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\btlog_NQ_M15.csv --zeromot --set bt_w=A --set bt_T=240 --set bt_pbp=100 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_bt_NQ_M15.csv`  
  sha1 footprint `713fb4ab26572088a047269e851b1c998a796a1f`, bars `1e5506a8003d541d52254770ce66341caf1dcce2`, nhật ký `c91522189a4c0ce68fa2861f52f9814c0fabe43f`
- `bt_GC_M5`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m5.csv 5 0.1 --btlog C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\btlog_GC_M5.csv --zeromot --set bt_w=A --set bt_T=240 --set bt_pbp=100 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_bt_GC_M5.csv`  
  sha1 footprint `c16af95c1a59df3084450db93252c7427cde9413`, bars `0ae70fa571727e72aff59d45f0c2dfdcef327bb5`, nhật ký `540f6c2ef0c6674bc127c67d84bb8455291dbeb3`
- `bt_GC_M30`: `python sa3_ref.py C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\tf\fp_GC_m30.csv 30 0.1 --btlog C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\btlog_GC_M30.csv --zeromot --set bt_w=A --set bt_T=240 --set bt_pbp=100 --marks C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad\marks_r3_bt_GC_M30.csv`  
  sha1 footprint `f76c56021d535427e3cf2cb57013d8f57dbb09c8`, bars `7a01524b21dcd472908c96ca689220ad79e9ddb8`, nhật ký `9f90c4598ccdcf456799eca1175ac7bd4e605b38`
</details>

## 9. Áp luật chọn viết trước (Opus chỉ áp, không chọn mặc định)

1. **Chọn tham lam thay "lớn hơn hẳn"**: ĐÚNG cả ba điều trên 12/12 ô → luật cho thay. (a) 20 ô lớn nhất ngày nhìn thấy tham lam ≥ lớn hơn hẳn: đúng 12/12; (b) nhiễu ≤ 5% và chấm ≤ 3 hợp đồng ≤ 2%: đúng 12/12; (c) chấm/nến không cao hơn quá 15%: đúng 12/12 (tăng 3,9% – 10,3%).
2. **Không lân cận thay có lân cận** (chỉ khi tổng trượt hai đoạn ít hơn): không lân cận 7, có lân cận (nền mới) 1 → giữ có lân cận.
3. **Tối thiểu 1 ngày thay 2 ngày** (tổng trượt không nhiều hơn VÀ trùng nạp 8 ngày cao hơn ≥ 0,01): tổng trượt 2 so với 1 (NHIỀU HƠN); trùng nạp 8 ngày 0,888 so với 0,870 (chênh 0,018) → giữ tối thiểu 2 ngày.
4. **Mức mặc định giữ 2%** (luật cố định). Để tham khảo: tổng trượt p 1% = 7, p 0,5% = 16, p 2% (nền mới) = 1.

## 10. Bất thường và chỗ chỉ dẫn chưa rõ

- Với chọn tham lam, số "nhìn thấy" bằng đúng số cũ ở mọi ô (đúng như dự kiến: theo cách dựng, mọi ô vượt ngưỡng đều là chấm hoặc cách một chấm ≤ w tick). Phần còn sót của nền mới vì vậy là sót **vì ngưỡng** (ô không vượt ngưỡng), không phải vì bước chọn.
- Nền mới còn trượt một tiêu chí: NQ M15 đoạn chọn: 5 ô lớn nhất phiên 0,913 — gần hết ô sót nằm ở nến 13:00 và 13:15 UTC (mục 5), cùng cơ chế vòng 2 nêu.
- Ngoài 6 ô: nền mới GC M30 đoạn chọn trượt Khớp chung 1,3 (M30 / H1 không vào luật chọn, chỉ báo).
- Ngoài 6 ô: nền mới GC M60 đoạn chọn trượt Khớp chung 1,28 (M30 / H1 không vào luật chọn, chỉ báo).
- Ngoài 6 ô: nền mới GC M60 đoạn kiểm trượt 20 ô lớn nhất ngày 0,981 (M30 / H1 không vào luật chọn, chỉ báo).
- Ngoài 6 ô: nền mới NQ M30 đoạn chọn trượt Khớp chung 1,31; 5 ô lớn nhất phiên 0,887 (M30 / H1 không vào luật chọn, chỉ báo).
- Ngoài 6 ô: nền mới NQ M60 đoạn chọn trượt Khớp chung 1,25; Khớp theo giờ 19/23 (giờ tệ nhất 20: 0,107) (M30 / H1 không vào luật chọn, chỉ báo).
- Ngoài 6 ô: nền mới NQ M60 đoạn kiểm trượt 5 ô lớn nhất phiên 0,951 (M30 / H1 không vào luật chọn, chỉ báo).
- NQ M1 đoạn chọn nhiễu 1,2% và NQ M5 / M15 đoạn chọn 1,3–1,5%, cao hơn đoạn kiểm (0,3–0,4%) — vẫn dưới 5%. Đoạn chọn NQ có tuần chuyển hợp đồng (14/09).
- Đối chứng luật đang chạy không có "Khớp" (không phải luật phân vị) nên ba tiêu chí Khớp ghi "không áp dụng"; chúng trượt cả ba tiêu chí không sót ở mọi ô, giống vòng 2.
- Golden (`perf/Golden/Program.cs`) **chưa có tuỳ chọn `--from`**. Để C# chạy được dòng "nạp 8 ngày", `sa3_numbers.py` ghi sẵn cặp file đã cắt `tf/fp_GC_m5_nap8.csv`, `tf/fp_NQ_m15_nap8.csv` (+ `_bars.csv`) trong thư mục tạm; bản chuẩn đọc file cắt ra đúng bằng khi đọc file đủ với `--from` (có assert). Điểm bắt đầu là nến đầu của ngày giao dịch thứ 8 tính từ cuối theo giờ Chicago (GC M5: 2026-10-28 22:00 UTC; NQ M15: 2026-11-12 23:00 UTC), không phải 00:00.
- Chỉ dẫn ghi tên script tiền tố `r3_` ở dòng "Yêu cầu" nhưng mục 6 của review và phần chỉ dẫn vòng 3 ghi `sa3_`; Opus dùng `sa3_` (khớp `out_r3_*`, `R3-KET-QUA.md`).
- "Nến rỗng bỏ hẳn" không làm đổi số nào trên dữ liệu hiện có: CSV của Golden không có nến nào mà mọi ô volume = 0 (tự kiểm in "rỗng 0"). Điều này chỉ có tác dụng với dữ liệu sống.
- Phép thử nạp 3 ngày trùng thấp (0,69 gộp): với 3 ngày, ngày đầu chạy hoàn toàn bằng dự phòng 120 phút và ngày thứ hai mới có 1 ngày trước (chưa đủ tối thiểu 2), nên chỉ ngày thứ ba dùng ngưỡng chính. Đây là hành vi đã định, không phải lỗi.
- So CORVEN (GC M1, 580 nến mẫu): nền mới chỉ 0,28 chấm/nến so với CORVEN 1,53; bắt 22,3% chấm CORVEN, nhưng 99,4% chấm của mình trùng CORVEN. Nghĩa là luật thống kê thưa hơn CORVEN nhiều ở M1; chỉ báo số, không chỉnh theo (đúng chỉ dẫn).

