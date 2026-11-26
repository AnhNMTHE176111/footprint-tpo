# SPEC — Vòng lớn "Big Volume theo hàng" như chart M1 của CORVEN (2026-11-26)

> Chỉ là **định nghĩa hiển thị** cho giống chart CORVEN. Chưa sửa C#, chưa commit. Bản Python chuẩn từng nến: `ref_rule.py`.

## 1. CORVEN vẽ gì (đã đo)

- **Chart M1 (NQ ảnh 06/11, 5 khung Meet NQ, 18 khung Meet GC, 05–06/11): không có lớp vòng mờ riêng.** Mỗi hàng giá chỉ có một bóng đặc xanh / đỏ / tím, **đường kính lớn dần theo volume của hàng**. "Vòng to" mà mắt thấy chính là bóng của hàng có volume rất lớn.
  - Cỡ bóng (q = đường kính / đường kính chấm thường) theo `tổng volume hàng / nền` — giống nhau ở cả ba mẫu: ≤ 3 lần nền → q ≈ 0,95–1,0; 4,25 → 1,36; 5,5 → 1,6; 6,5 → 1,75; 7,5 → 2,0; 9 → 2,3; > 10 → tới 4,7 (`out_size_pairs.csv`).
  - Màu tím = **cả Bid lẫn Ask của hàng đều ≥ 1,3 × nền** (đúng 92,5% trên 1.352 bóng); còn lại xanh nếu Ask lớn hơn, đỏ nếu Bid lớn hơn.
  - Cỡ chấm thường cố định theo pixel, không đổi theo độ zoom.
- **Chart M5 GC 18/11: có 25 vòng mờ hồng / xanh nhạt.** Không luật volume nào giải thích được vị trí (hàng 1–10 tick, mọi pha: AUC ≤ 0,75; luật đề xuất dưới đây chỉ trùng 3/25). Nhật ký lệnh đơn chỉ phủ 10 trong 26 nến M5 của mẫu (có nến thiếu phút): 2 nến có vòng CORVEN có lệnh đơn lớn nhất 17 và 12 hợp đồng, 7 nến không có vòng đều ≤ 10; nến 13:50 có 2 vòng nhưng nhật ký thiếu 2 phút đầu nên không so được. Khớp với giả thuyết "một lệnh đơn ≥ khoảng 11–12 hợp đồng", nhưng mẫu quá nhỏ để kết luận.

## 2. Luật hiện tại ra gì

- Mẫu M1 05–06/11: nhật ký lệnh đơn không có ngày này (GC bắt đầu 09/11; NQ có 25/10–03/11 và từ 24/11) → **0 vòng**.
- Mẫu M5 18/11: lệnh đơn lớn nhất trong phần có nhật ký là 17, ngưỡng "cá mập" của vàng 34–76 → **0 vòng**.
- Người dùng thực tế: lịch sử không vòng; khi chạy live đủ 1380 phút nhật ký thì khoảng 8 vòng mỗi ngày (CORVEN M5: 25 vòng trong 130 phút).

## 3. Luật đề xuất

Hàng giá = lưới của kiệt sức (ExhRowGrid): NQ/MNQ 8 tick lệch 4, GC/MGC 2 tick lệch 1, mã khác từng tick.

1. Gộp ô theo hàng: `Bid`, `Ask`, `Vol` của hàng.
2. `rowBase` = trung bình trên N nến đã đóng liền trước (có giao dịch) của `tổng volume nến / số hàng có giao dịch` — **đúng công thức rowBase của kiệt sức**; N = `DesiredBaseBars()` (M1/M5 20, M15 8, M30+ 5), cần ≥ 5 nến.
3. Hàng có `ratio = Vol / rowBase ≥ 4,25` → một vòng lớn tại **tâm hàng** (kẹp trong [low, high] của nến). Không gộp hàng kề, không giới hạn số vòng mỗi nến, không sàn tuyệt đối.
4. Phía: `Ask > Bid` → buy (xanh), ngược lại sell (đỏ). Cờ hai bên: `min(Bid, Ask) ≥ 1,3 × rowBase` (CORVEN tô tím; indicator đang dành tím cho stop hunt nên agent chính quyết có dùng hay không).
5. Cỡ: đường kính = đường kính chấm × `clamp(ratio / 3,2; 1,33; 4,7)`. Với `DotSizeFrac = 0,45`: `SizeFrac = 0,45 × clamp(ratio / 3,2; 1,33; 4,7)` = 0,60 … 2,115 bề ngang nến.
6. Nến đóng nộp `tổng volume / số hàng` vào hàng đợi nền sau khi đã xét (dùng chung hàng đợi với kiệt sức được).
7. Không cần `MaxOneTradeVolume` hay nhật ký → lịch sử và live ra cùng kết quả. Không thêm ô Settings.

Tooltip gợi ý: `Big volume: hàng 27000–27001,75 · 112 hợp đồng (Bid 31, Ask 81) = 6,9 × nền 16,1`.

## 4. Độ khớp (bóng CORVEN cỡ lớn q ≥ 1,5; khớp cùng nến, lệch ≤ 1 hàng; `eval_ref.py`)

| Mẫu | Nến | CORVEN | Hiện tại: trùng / thừa / sót | Đề xuất: trùng / thừa / sót |
|---|---|---|---|---|
| GC M1 Meet 05–06/11 | 808 | 85 | 0 / 0 / 85 | 62 / 43 / 23 |
| NQ M1 Meet 06/11 | 312 | 50 | 0 / 0 / 50 | 41 / 21 / 9 |
| NQ M1 ảnh 06/11 14:39–16:01 | 83 | 9 | 0 / 0 / 9 | 9 / 2 / 0 |
| GC M5 18/11 (vòng mờ) | 26 | 25 | 0 / 0 / 25 | 3 / 11 / 22 |

- "Thừa" không tính vòng trùng bóng CORVEN cỡ 1,25–1,5 (45 vòng). Ngưỡng 4,25 chọn trên GC, giữ nguyên khi kiểm trên hai mẫu NQ.
- Cỡ vòng đề xuất so với cỡ CORVEN trên 207 cặp trùng: tương quan hạng 0,53, lệch trung vị 0,26 lần đường kính chấm.
- Chi tiết từng vòng: `out_compare_marks.csv`; ảnh soát: `dbg/cmp_IMG13.png` (ô vuông đen = vòng đề xuất), `dbg/bub_*.png` (bóng CORVEN dò được).

## 5. Các phương án đã đo (`variants.py` → `out_variants.csv`; trùng/thừa/sót cộng 3 mẫu M1)

| Phương án | Ngưỡng tốt nhất trên GC | Tổng | F1 |
|---|---|---|---|
| Hiện tại (lệnh đơn "cá mập") | — | 0 / 0 / 144 | 0 |
| V1 tổng hàng / nền TB 20 nến (**chọn**, ngưỡng 4,25) | 4,25 | 112 / 66 / 32 | 0,70 |
| V2 bên lớn của hàng / nền TB 20 | 3,5 | 89 / 28 / 55 | 0,68 |
| V3 bên lớn / nền trung vị 20 | 4,0 | 92 / 37 / 52 | 0,67 |
| V4 bên lớn, ngưỡng tuyệt đối (GC 35, NQ 150 fit riêng) | — | 67 / 35 / 77 | 0,54 |
| V5 tổng hàng / TB hàng của chính nến | 3,5 | 44 / 73 / 100 | 0,34 |
| V6 bên lớn / nền TB 120 nến | 3,0 | 119 / 108 / 25 | 0,64 |
| V7 bên lớn / nền TB 5 nến | 3,0 | 102 / 59 / 42 | 0,67 |
| V8 chỉ hàng lớn nhất nến | 3,0 | 83 / 26 / 61 | 0,66 |
| V9 bên lớn / volume nến TB 20 | 7,0 | 59 / 41 / 85 | 0,48 |
| V10 tổng hàng, tuyệt đối (GC 45, NQ 250 fit riêng) | — | 72 / 71 / 72 | 0,50 |
| V11 từng tick (không gom hàng), fit riêng từng mẫu | 4–12 | 84 / 53 / 60 | 0,60 |

## 6. Số chuẩn 90 ngày để đối chiếu C#

```
python ref_rule.py --levels <fp>.csv --tick 0.25 --symbol NQZ26 --out marks.csv [--detail chi_tiet.csv]
```

| Mã, khung | File | Số nến | Vòng lớn | Nến có vòng | Vòng / nến | sha1 file dấu |
|---|---|---|---|---|---|---|
| NQ M1 | `fp_NQZ26_XCME_Time_20260826-20261124_90d.csv` | 78.464 | **6.440** | 3.987 | 0,082 | `62229f60c82290404e100e0a3bf46328f4fc84d9` |
| GC M1 | `fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv` | 87.362 | **19.147** | 10.847 | 0,219 | `0889d8fd6c7a3d9d51ad9b9097c49fac2b6fe070` |

File dấu (`t,kind,price`, kind = `bt`, price = tâm hàng đã kẹp): `ref_marks_NQ_90d.csv`, `ref_marks_GC_90d.csv`; kèm tỷ lệ, cỡ, phía: `ref_detail_*_90d.csv`.
Hiện tại: 0 vòng trên nến không có nhật ký; trên nến có nhật ký NQ M1 56 vòng / 6.960 nến (0,008), GC M5 111 / 4.318 (0,026) (`../bigtrade_whale_2026-11-25/SPEC.md` mục 9).

## 7. Chưa chắc chắn

1. Vòng mờ kiểu chart M5 18/11 **không làm lại được từ dữ liệu lịch sử**; chỉ có một ảnh, nhật ký phủ 10/26 nến.
2. Chart M1 (05–06/11) và M5 (18/11) của CORVEN vẽ khác nhau (M1: bóng đặc to dần + tím; M5: chấm cỡ cố định + vòng mờ). Không biết do đổi phiên bản study hay do cài đặt riêng từng chart.
3. Cỡ bóng đo trên khung hình 1600 px (bán kính chấm ≈ 2,1 px) nên sai số cỡ lớn; nền 20 nến và hệ số 3,2 / 4,25 là fit, không phải tham số đọc được từ study.
4. Nến "chấm được" loại 53 nến GC / 6 nến NQ bị che hoặc nằm ngoài khung giá (nến sôi động mà ảnh không có bóng nào).
5. Mã ngoài GC/NQ và khung trên M5 chưa có chart CORVEN để đối chiếu.

## 8. Chạy lại

```
python extract_bubbles.py   # raw_bubbles.csv, raw_visible.csv, dbg/bub_*.png
python build_gt.py          # gt_bubbles.csv, gt_visible.csv
python feats.py             # _rows.pkl (đặc trưng từng hàng; tạo lại file đệm _cache_*.pkl ~250 MB trong ../exh_2026-11-26, đừng commit)
python variants.py          # out_variants.csv
python eval_ref.py          # bảng mục 4 + out_compare_marks.csv
```
