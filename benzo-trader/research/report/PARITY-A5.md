# PARITY A5: C# (DetectorA5) ↔ Python (setup_a_v5.detect5) — file 90d GCZ26

Nến xấu của Python (chỗ nối hợp đồng | phiên mỏng): 3697 nến, ghi ra `report/_a5_bad_bars.csv` (giờ MỞ nến UTC) và đưa vào C# qua `IsNewsBlocked`.
Số nến 86333 · phiên 65 · nạp Python 2s.
Sự kiện M5 mà C# chỉ biết trễ 1 nến (nến M1 cuối của nến M5 không phải phút :4 vì M1 thưa): 145 / 17592, trong đó 135 nằm ở 4 phiên mỏng/chỗ nối, 10 ở phiên bình thường.

## A-v5 (có VCL)

ReplayA5: 14s. ```nạp 86333 nến M1, 86333 nến có per-level; nến xấu: 3697; A-v5 (có VCL) | raw: 387 tín hiệu, 57009 trạng thái kết thúc (5.1s) | sim: 324 lệnh (324 đã đóng) (3.7s) | live: 312 lệnh (312 đã đóng) (3.6s)```

Python: raw 387 · 1 lệnh mở không chặn mở ảo 324 đã đóng (324 tổng) · có chặn mở ảo 312 đã đóng (312 tổng).

| tầng | Python | C# | khớp | % | mục tiêu |
|---|---|---|---|---|---|
| L0 mức vùng (phiên) | 65 | 65 | 65 | 100.00% | 100% (lệch lớn nhất 0.00e+00) |
| L1 tín hiệu raw | 387 | 387 | 387 | 100.00% | 100% |
| L2 trạng thái kết thúc | 56974 | 57009 | 55929 | 98.17% | 100% |
| L2 ngoài phiên mỏng/chỗ nối | 54791 | | 54791 | 100.00% | 100% |
| L3 lệnh không chặn mở ảo | 324 (đóng 324) | 324 (đóng 324) | 324 | 100.00% | đóng = 324 |
| L4 lệnh có chặn mở ảo (live) | 312 (đóng 312) | 312 (đóng 312) | 312 | 100.00% | đóng = 312 |

Ca lệch L2: chỉ Python 1045, chỉ C# 1080.
- chỉ Python: ('HVN_D1', -1, 508, 469, 'expire', 1, 0, 7)
- chỉ Python: ('HVN_D1', -1, 510, 469, 'expire', 1, 0, 8)
- chỉ Python: ('HVN_D1', -1, 513, 469, 'expire', 1, 0, 9)
- chỉ Python: ('HVN_D1', -1, 515, 469, 'expire', 1, 0, 10)
- chỉ Python: ('HVN_D1', -1, 519, 469, 'expire', 1, 0, 11)
- chỉ Python: ('HVN_D1', -1, 522, 469, 'expire', 1, 0, 12)
- chỉ Python: ('HVN_D1', -1, 524, 469, 'expire', 1, 0, 13)
- chỉ Python: ('HVN_D1', -1, 527, 469, 'expire', 1, 0, 14)
- chỉ Python: ('HVN_D1', -1, 530, 472, 'expire', 1, 0, 15)
- chỉ Python: ('HVN_D1', -1, 535, 570, 'expire', 1, 0, 16)
- chỉ Python: ('HVN_D1', -1, 604, 570, 'expire', 1, 0, 17)
- chỉ Python: ('HVN_D1', -1, 607, 570, 'expire', 1, 0, 18)
- chỉ Python: ('HVN_D1', -1, 611, 570, 'expire', 1, 0, 19)
- chỉ Python: ('HVN_D1', -1, 615, 570, 'expire', 1, 0, 20)
- chỉ Python: ('HVN_D1', -1, 619, 570, 'expire', 1, 0, 21)
- chỉ C#: ('HVN_D1', -1, 506, 469, 'expire', 1, 0, 7)
- chỉ C#: ('HVN_D1', -1, 508, 469, 'expire', 1, 0, 8)
- chỉ C#: ('HVN_D1', -1, 509, 469, 'expire', 1, 0, 9)
- chỉ C#: ('HVN_D1', -1, 513, 469, 'expire', 1, 0, 10)
- chỉ C#: ('HVN_D1', -1, 514, 469, 'expire', 1, 0, 11)
- chỉ C#: ('HVN_D1', -1, 515, 469, 'expire', 1, 0, 12)
- chỉ C#: ('HVN_D1', -1, 519, 469, 'expire', 1, 0, 13)
- chỉ C#: ('HVN_D1', -1, 522, 469, 'expire', 1, 0, 14)
- chỉ C#: ('HVN_D1', -1, 524, 469, 'expire', 1, 0, 15)
- chỉ C#: ('HVN_D1', -1, 527, 469, 'expire', 1, 0, 16)
- chỉ C#: ('HVN_D1', -1, 530, 472, 'expire', 1, 0, 17)
- chỉ C#: ('HVN_D1', -1, 535, 570, 'expire', 1, 0, 18)
- chỉ C#: ('HVN_D1', -1, 601, 570, 'expire', 1, 0, 19)
- chỉ C#: ('HVN_D1', -1, 604, 570, 'expire', 1, 0, 20)
- chỉ C#: ('HVN_D1', -1, 607, 570, 'expire', 1, 0, 21)
Trong ca lệch L2: ngoài phiên mỏng/chỗ nối 0 · có lệnh vào (n_ent>0) 0.

## A-v4 (`--novcl`)

ReplayA5: 4s. ```nạp 86333 nến M1, 86333 nến có per-level; nến xấu: 3697; A-v4 (không VCL) | raw: 245 tín hiệu, 50971 trạng thái kết thúc (1.3s) | sim: 218 lệnh (218 đã đóng) (0.5s) | live: 208 lệnh (208 đã đóng) (0.4s)```

Python: raw 245 · 1 lệnh mở không chặn mở ảo 218 đã đóng (218 tổng) · có chặn mở ảo 208 đã đóng (208 tổng).

| tầng | Python | C# | khớp | % | mục tiêu |
|---|---|---|---|---|---|
| L0 mức vùng (phiên) | 65 | 65 | 65 | 100.00% | 100% (lệch lớn nhất 0.00e+00) |
| L1 tín hiệu raw | 245 | 245 | 245 | 100.00% | 100% |
| L2 trạng thái kết thúc | 50937 | 50971 | 49894 | 97.95% | 100% |
| L2 ngoài phiên mỏng/chỗ nối | 48965 | | 48965 | 100.00% | 100% |
| L3 lệnh không chặn mở ảo | 218 (đóng 218) | 218 (đóng 218) | 218 | 100.00% | đóng = 218 |
| L4 lệnh có chặn mở ảo (live) | 208 (đóng 208) | 208 (đóng 208) | 208 | 100.00% | đóng = 208 |

Ca lệch L2: chỉ Python 1043, chỉ C# 1077.
- chỉ Python: ('HVN_D1', -1, 508, 469, 'expire', 1, 0, 7)
- chỉ Python: ('HVN_D1', -1, 510, 469, 'expire', 1, 0, 8)
- chỉ Python: ('HVN_D1', -1, 513, 469, 'expire', 1, 0, 9)
- chỉ Python: ('HVN_D1', -1, 515, 469, 'expire', 1, 0, 10)
- chỉ Python: ('HVN_D1', -1, 519, 469, 'expire', 1, 0, 11)
- chỉ Python: ('HVN_D1', -1, 522, 469, 'expire', 1, 0, 12)
- chỉ Python: ('HVN_D1', -1, 524, 469, 'expire', 1, 0, 13)
- chỉ Python: ('HVN_D1', -1, 527, 469, 'expire', 1, 0, 14)
- chỉ Python: ('HVN_D1', -1, 530, 472, 'expire', 1, 0, 15)
- chỉ Python: ('HVN_D1', -1, 535, 570, 'expire', 1, 0, 16)
- chỉ Python: ('HVN_D1', -1, 604, 570, 'expire', 1, 0, 17)
- chỉ Python: ('HVN_D1', -1, 607, 570, 'expire', 1, 0, 18)
- chỉ Python: ('HVN_D1', -1, 611, 570, 'expire', 1, 0, 19)
- chỉ Python: ('HVN_D1', -1, 615, 570, 'expire', 1, 0, 20)
- chỉ Python: ('HVN_D1', -1, 619, 570, 'expire', 1, 0, 21)
- chỉ C#: ('HVN_D1', -1, 506, 469, 'expire', 1, 0, 7)
- chỉ C#: ('HVN_D1', -1, 508, 469, 'expire', 1, 0, 8)
- chỉ C#: ('HVN_D1', -1, 509, 469, 'expire', 1, 0, 9)
- chỉ C#: ('HVN_D1', -1, 513, 469, 'expire', 1, 0, 10)
- chỉ C#: ('HVN_D1', -1, 514, 469, 'expire', 1, 0, 11)
- chỉ C#: ('HVN_D1', -1, 515, 469, 'expire', 1, 0, 12)
- chỉ C#: ('HVN_D1', -1, 519, 469, 'expire', 1, 0, 13)
- chỉ C#: ('HVN_D1', -1, 522, 469, 'expire', 1, 0, 14)
- chỉ C#: ('HVN_D1', -1, 524, 469, 'expire', 1, 0, 15)
- chỉ C#: ('HVN_D1', -1, 527, 469, 'expire', 1, 0, 16)
- chỉ C#: ('HVN_D1', -1, 530, 472, 'expire', 1, 0, 17)
- chỉ C#: ('HVN_D1', -1, 535, 570, 'expire', 1, 0, 18)
- chỉ C#: ('HVN_D1', -1, 601, 570, 'expire', 1, 0, 19)
- chỉ C#: ('HVN_D1', -1, 604, 570, 'expire', 1, 0, 20)
- chỉ C#: ('HVN_D1', -1, 607, 570, 'expire', 1, 0, 21)
Trong ca lệch L2: ngoài phiên mỏng/chỗ nối 0 · có lệnh vào (n_ent>0) 0.

Tổng thời gian 34s.

<!-- NGUYEN-NHAN -->

## Giải thích ca lệch + tiên quyết (viết tay, 2026-10-23)

**Kết luận:** tín hiệu raw (L1), lệnh sau luật "1 lệnh mở" không chặn mở ảo (L3: A-v4 218, A-v5 324) và có chặn mở ảo (L4: A-v4 208, A-v5 312) khớp **100 %** từng lệnh
(giờ vào, chiều, vào/SL/TP, vùng, kết cục, giờ thoát, R). Mức vùng từng phiên (L0) khớp 100 % (sai số lớn nhất 0). Chỉ nhật ký trạng thái kết thúc (L2) lệch ở **4 phiên mỏng**
đầu file (xem dưới); **ngoài 4 phiên đó L2 khớp 100 %**.

**Nguyên nhân duy nhất của lệch L2 = loại (b) trong plan 5.2 (nến M5 thiếu phút cuối nên C# đóng trễ 1 nến), nhưng với số lượng lớn vì dữ liệu thưa ở 4 phiên mỏng.**
- Python biết nến M1 nào là nến cuối của một nến M5 ngay khi nến đó đến (nó đã thấy nến sau trong file). C# chỉ biết nến M5 đã đóng khi nến sau tới ⇒ sự kiện M5 được xử lý trễ 1 nến
  (k = i−1) và chạy SAU lượt quét nến k. Hệ quả: một trạng thái đã hết hạn ở nến k kịp "chặn" mở lại ở Python nhưng ở C# thì đã mất ⇒ C# mở lại thêm một vòng
  (ví dụ phiên 24/07 04:xx UTC, vùng HVN_D1 bán: Python mở lại ở nến 505, 508, 510, 513…; C# mở thêm ở 506, 509, 514…; mọi vòng đều hết hạn ngay vì đỉnh cũ cách quá 30 nến).
- Thống kê: 145 / 17 592 sự kiện M5 bị trễ như vậy, trong đó **135 nằm ở 4 phiên mỏng** (thưa nến M1 vì ít giao dịch) và **10 ở phiên bình thường** — 10 ca này không đổi tín hiệu,
  không đổi trạng thái ở bất kỳ tầng nào.
- Trong ca lệch L2: không trạng thái nào có lệnh vào (n_ent = 0) và cả 4 phiên đều nằm trong danh sách nến xấu (`_a5_bad_bars.csv`, `okbar = false`) nên **không thể** ra tín hiệu ⇒ không ảnh hưởng L1/L3/L4.
- Không sửa được mà vẫn đúng thời gian thực: không thể biết nến M5 đã đóng trước khi nến sau đến. Không ca nào thuộc loại (a) (lệch dấu phẩy động ở mép vùng): 0 ca.
- Rủi ro còn lại (cần nói thẳng): với dữ liệu thưa như vậy ở phiên bình thường, C# có thể phát tín hiệu mà Python (nhìn trước 1 nến) đã huỷ trạng thái — chưa gặp ca nào trong 90 ngày (10 sự kiện trễ ở phiên bình thường đều vô hại).

## Tiên quyết (plan 5.0) — đã chạy
1. `parity_vcl.py` (chạy trên bản sao thư mục `vung-canh-lenh` trong scratchpad để không ghi đè báo cáo của phiên khác) với `VclCore.cs` đang có trong cây làm việc lúc đó:
   bộ vùng hiển thị khớp **86081/86081 nến = 100 %** (lệch lớn nhất 4,55e-13 giá), trạng thái lần chạm 554 102/554 102, 4 915 lần chạm khớp 4 915 ⇒ commit `c15d278` (vùng lịch sử) **không đổi `Display`**,
   và A5 dùng đúng `Display` này. (Lúc chạy cây làm việc có sửa dở `VclCore.cs` của phiên khác — thêm "hạng khối lịch sử" PLAN-LOC-VUNG — không đụng `Display`; parity A5 chạy lại sau đó vẫn 100 %.)
2. `python3 -m pytest test_setup_a_v5.py -q` ⇒ **15 passed** (Python chuẩn còn đúng).

## Thời gian chạy (máy Linux, Release)
- ReplayA5 A-v5 toàn file 90 ngày (86 333 nến): raw+trạng thái 5,1 s · sim 3,7 s · live 3,6 s (ngân sách plan ≤ 30 s). A-v4 (không VCL): 1,3 s / 0,5 s / 0,4 s.
- Trung bình ≈ 43 µs/nến cho cả A-v5 (VclCore ≈ 45 µs/nến chiếm phần lớn) ⇒ nạp 30 ngày lịch sử ≈ 1,5 s trên máy này (ngân sách ≤ 5 s); mỗi nến live ≪ 1 ms.

## Tái lập
`cd benzo-trader/research && python3 parity_a_v5.py` (tự chạy ReplayA5; thêm `--no-run` để chỉ so lại file đã có, `--out DIR` để ghi CSV C# ra thư mục khác).
