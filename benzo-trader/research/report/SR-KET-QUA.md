# Hỗ trợ / kháng cự — đo trên GCZ26 M1, 65 phiên (2026-07-23 → 10-21)

Định nghĩa đo (xem docstring `sr_measure.py`): **Osler** = 15 nến sau khi chạm, giá đóng vẫn phía cũ; **Chung** = vào dải ±u rồi thoát cùng phía (bật) hay phía kia (xuyên), theo giá đóng, tối đa 120 nến. u = trung vị biên độ M1 50 nến. Đối chứng = 10 mức ngẫu nhiên/phiên trong biên phiên trước ±2 giá, lặp 50 lần. Nến ngẫu nhiên lý thuyết: Chung ≈ 50%.

| Mức | n vào dải | Osler bật % | n (Chung) | Chung bật % | ± | bật rồi đi ≥2u % |
|---|---|---|---|---|---|---|
| Swing k=5 (tất cả) | 185207 | 56.7 | 184931 | 67.1 | 0.1 | 89.7 |
| Swing · chưa bật lần nào | 14155 | 56.5 | 14127 | 66.7 | 0.4 | 90.3 |
| Swing · đã bật 1 lần | 13433 | 56.7 | 13409 | 66.9 | 0.4 | 90.3 |
| Swing · đã bật ≥2 lần | 157619 | 56.7 | 157395 | 67.2 | 0.1 | 89.6 |
| Swing · tuổi <=120 nến | 44361 | 56.6 | 44254 | 67.2 | 0.2 | 89.8 |
| Swing · tuổi 121-480 nến | 58399 | 56.5 | 58311 | 66.6 | 0.2 | 89.5 |
| Swing · tuổi >480 nến | 82447 | 56.9 | 82366 | 67.4 | 0.2 | 89.8 |
| Đỉnh phiên trước | 462 | 57.6 | 462 | 61.7 | 2.3 | 89.5 |
| Đáy phiên trước | 498 | 58.0 | 497 | 67.2 | 2.2 | 88.6 |
| Đóng phiên trước | 1147 | 56.9 | 1147 | 67.9 | 1.5 | 90.8 |
| VAH hôm qua | 797 | 55.2 | 795 | 62.6 | 1.8 | 89.8 |
| VAL hôm qua | 809 | 58.0 | 806 | 68.1 | 1.8 | 92.7 |
| POC hôm qua | 1027 | 57.8 | 1026 | 68.2 | 1.6 | 91.3 |
| VAH Âu | 465 | 60.4 | 465 | 68.4 | 2.3 | 89.3 |
| VAL Âu | 549 | 60.5 | 549 | 68.7 | 2.1 | 87.0 |
| Số tròn 10$ | 6371 | 56.3 | 6365 | 66.2 | 0.6 | 89.7 |
| Số tròn 5$ | 6647 | 57.7 | 6640 | 67.3 | 0.6 | 88.7 |
| VWAP ngày | 2066 | 54.4 | 2062 | 65.5 | 1.1 | nan |
| VWAP tuần | 1067 | 54.5 | 1063 | 64.8 | 1.5 | nan |
| ĐỐI CHỨNG mức ngẫu nhiên | 321770 | 57.1 | 321429 | 66.7 | 0.1 | 89.0 |
| ĐỐI CHỨNG ngẫu nhiên · chỉ 19:00–04:00 VN | 120182 | 58.3 | 119841 | 67.6 | 0.1 | 88.2 |
| VAH+VAL Âu gộp | 1014 | 60.5 | 1014 | 68.5 | 1.6 | 88.1 |

## Tách đôi thời gian (Chung bật %, n)

| Mức | TRAIN ≤ 09-15 | TEST ≥ 09-16 |
|---|---|---|
| Swing | 67.4 (n=101063) | 66.8 (n=83868) |
| Ngẫu nhiên | 66.8 (n=173349) | 66.5 (n=148080) |
| VWAP ngày | 65.6 (n=1142) | 65.3 (n=920) |
| VWAP tuần | 65.0 (n=685) | 64.6 (n=378) |
| Đỉnh/đáy phiên trước | 63.3 (n=510) | 65.9 (n=449) |
| Số tròn 10$ | 66.4 (n=3854) | 65.9 (n=2511) |

## Kiểm tra độ bền (file `SR-KET-QUA-2u.md`: dải ±2u, Osler 30 nến)
Đổi dải và cửa sổ thì mọi con số dịch cùng nhau (đối chứng Chung 66,7% → 78,3%), **khoảng cách giữa mức có tên và mức ngẫu nhiên
vẫn ≈ 0**. Đối chứng cùng khung giờ 19:00–04:00 VN: 67,6% (1u) / 79,4% (2u), nên VA Âu 68,5% / 79,3% **không vượt** đối chứng.

## Đọc kết quả (agent chính)
1. **Vì sao mức ngẫu nhiên cũng "bật" 57–67%:** ở khung M1, giá đóng vào dải rồi thoát cùng phía là chuyện hình học (giá hay đóng gần
   mép phía nó tới). Osler cũng thấy mức ngẫu nhiên bật 56,2%. Vì vậy **con số bật tuyệt đối không nói gì**; chỉ hiệu so với đối chứng mới có nghĩa.
2. **Trên 65 phiên GCZ26 này, không loại mức nào bật nhiều hơn mức ngẫu nhiên quá sai số:** swing, đỉnh/đáy/đóng phiên trước,
   VA hôm qua, VA Âu, số tròn, VWAP. Số lần bật trước đó và tuổi mức cũng không làm khác đi (trái với Chung & Bellotti trên EURUSD 2018).
3. Cỡ phản ứng sau khi bật (đi ≥2u trong 30 nến) cũng ≈ đối chứng (≈89–90%).
4. **Khớp với toàn bộ phép đo trước** (hấp thụ, bong bóng, stacked imbalance, 4 setup Benzo): trong dữ liệu này, "ở vùng" không tự
   sinh lợi thế trên M1. Osler tìm thấy +4,6 điểm chỉ với mức do bàn giao dịch ngân hàng công bố (có thông tin lệnh khách), không phải mức
   vẽ từ giá quá khứ.
5. Hệ quả cho Hệ thống Đêm Vàng: giữ vùng để **tổ chức việc quan sát** (ở đâu thì nhìn kỹ), nhưng **không coi "giá tới vùng" là xác suất
   đảo chiều cao hơn**. Lợi thế nếu có phải đến từ thứ khác: thời điểm (tránh 19:20–20:30), đọc phe đang thắng, quản lý lệnh.

## Nguồn đã đọc
- Osler, C. (2000) "Support for Resistance: Technical Analysis and Intraday Exchange Rates", FRBNY Economic Policy Review —
  https://www.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.pdf
- Chung & Bellotti (2021) "Evidence and Behaviour of Support and Resistance Levels in Financial Time Series" — https://arxiv.org/abs/2101.07410
- Định nghĩa phổ thông (Murphy trích trong Osler; Babypips; NexusFi; TradeDisciple) — không có nguồn nào trong đó đo tỉ lệ giữ mức.
