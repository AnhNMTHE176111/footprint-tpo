# VONG 3 - Setup C: V5 "tuong limit" tai rau do + V5-nghich - CHI file 90d (QD-6)

TRAIN <= 2026-09-15, TEST tu 2026-09-16; cung seed doi chung (200 lan); bootstrap 95% 10.000 lan. Tuong dinh nghia o docstring `setup_c_v5_tuong.py`: muc <= 3 tick tu cuc tri rau; (a) tong volume >= kV x trung vi top-3-muc/nen cua 50 nen truoc; (b) delta ngu chieu do theo dung de bai (do len: sum bid >= kD x sum ask; do xuong: gương). **Bo 19:20-20:30 VN la luat gio cua He thong 3.2, khong phai tham so.** O khoi diem xuyen 2 tick, rong >= 6.

## A. Bai kiem tra co tach duoc 72 ca PHA THAT khong? (121 lenh co ban TP 2R, khong loc, chua bo gio 19:20-20:30)

Co ban: n 121, SL 88 (PHA THAT 72 / QUET RAU 16), TP 33. Phan loai PHA THAT = trong 20 nen sau SL co nen dong ngoai canh E >= 1u (nhu agent chinh).

| kV | kD | quy tac | co tuong: n | WR co tuong | SL co tuong | PHA_THAT co tuong / 72 | QUET co tuong / 16 | TP co tuong / 33 | khong tuong: n | WR khong tuong |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.5 | 2 | dung de bai (do len: bid>=kD*ask) | 6 | 16.7% | 5 | 5 | 0 | 1 | 115 | 27.8% |
| 1.5 | 3 | dung de bai (do len: bid>=kD*ask) | 1 | 0.0% | 1 | 1 | 0 | 0 | 120 | 27.5% |
| 2.0 | 2 | dung de bai (do len: bid>=kD*ask) | 4 | 25.0% | 3 | 3 | 0 | 1 | 117 | 27.4% |
| 2.0 | 3 | dung de bai (do len: bid>=kD*ask) | 0 | - | 0 | 0 | 0 | 0 | 121 | 27.3% |
| 1.5 | 2 | GUONG (do len: ask>=kD*bid) - doi chung quy uoc | 20 | 20.0% | 16 | 13 | 3 | 4 | 101 | 28.7% |
| 1.5 | 3 | GUONG (do len: ask>=kD*bid) - doi chung quy uoc | 14 | 28.6% | 10 | 8 | 2 | 4 | 107 | 27.1% |
| 2.0 | 2 | GUONG (do len: ask>=kD*bid) - doi chung quy uoc | 14 | 14.3% | 12 | 9 | 3 | 2 | 107 | 29.0% |
| 2.0 | 3 | GUONG (do len: ask>=kD*bid) - doi chung quy uoc | 8 | 25.0% | 6 | 4 | 2 | 2 | 113 | 27.4% |

(cot "SL co tuong" = so lenh SL co tuong trong 88; cot PHA_THAT/QUET/TP tinh trong tung nhom 72/16/33. Dong GUONG la phep thu quy uoc bid/ask, khong phai de bai.)

## B. V5: chi fade khi CO tuong (bo 19:20-20:30 VN)

B1 = quy tac DUNG DE BAI (do len: bid >= kD x ask). Vi quy tac nay hiem (xem muc A), them B2 = quy tac GUONG (do len: ask >= kD x bid = lenh buy market bi limit sell hap thu) chay NGUYEN luoi 4 o, bao ca bang, de khong chon o dep. Tieu chuan ket luan chinh thuc ap cho B1; B2 ghi them.

## B1. V5 DUNG DE BAI (bid >= kD x ask khi do len)

### V5 kV=1.5 kD=2, TP co dinh 2R

Lenh/ngay **0.197** (A 0.07 | EU 0.05 | US 0.08)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 12 | 25.0% | -0.35 | -0.77 | -4.2 | 5 |
| TRAIN | 6 | 33.3% | -0.10 | 0.20 | -0.6 | 2 |
| TEST | 6 | 16.7% | -0.60 | -1.75 | -3.6 | 5 |
| phase A | 4 | 25.0% | -0.35 | -1.30 | -1.4 | 3 |
| phase EU | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| phase US | 5 | 40.0% | 0.08 | 0.88 | 0.4 | 2 |

- tong: R TB -0.35, KTC bootstrap 95% [-1.09 ; 0.40], n = 12
- TEST: R TB -0.60, KTC bootstrap 95% [-1.11 ; 0.39], n = 6

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.07** (5-95%: -0.77 .. 0.70), WR doi chung 34.2%. Setup that: R TB **-0.35**, WR 25.0%. Ti le lan doi chung >= setup that: **68.5%**.

### V5 kV=1.5 kD=2, TP canh/POC >= 2R

Lenh/ngay **0.164** (A 0.05 | EU 0.05 | US 0.07)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 10 | 10.0% | -0.56 | -1.45 | -5.6 | 5 |
| TRAIN | 5 | 0.0% | -1.11 | -2.16 | -5.5 | 5 |
| TEST | 5 | 20.0% | -0.01 | -0.74 | -0.0 | 4 |
| phase A | 3 | 0.0% | -1.11 | -2.23 | -3.3 | 3 |
| phase EU | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| phase US | 4 | 25.0% | 0.24 | 0.17 | 1.0 | 2 |

- tong: R TB -0.56, KTC bootstrap 95% [-1.12 ; 0.54], n = 10
- TEST: R TB -0.01, KTC bootstrap 95% [-1.11 ; 2.18], n = 5

### V5 kV=1.5 kD=3, TP co dinh 2R

Lenh/ngay **0.098** (A 0.03 | EU 0.03 | US 0.03)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 6 | 33.3% | -0.09 | -0.23 | -0.5 | 2 |
| TRAIN | 3 | 33.3% | -0.09 | 0.97 | -0.3 | 1 |
| TEST | 3 | 33.3% | -0.09 | -1.43 | -0.3 | 2 |
| phase A | 2 | 0.0% | -1.09 | -2.55 | -2.2 | 2 |
| phase EU | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |
| phase US | 2 | 100.0% | 1.90 | 4.90 | 3.8 | 0 |

- tong: R TB -0.09, KTC bootstrap 95% [-1.09 ; 0.93], n = 6
- TEST: R TB -0.09, KTC bootstrap 95% [-1.06 ; 1.86], n = 3

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.07** (5-95%: -1.09 .. 0.90), WR doi chung 34.4%. Setup that: R TB **-0.09**, WR 33.3%. Ti le lan doi chung >= setup that: **48.5%**.

### V5 kV=1.5 kD=3, TP canh/POC >= 2R

Lenh/ngay **0.066** (A 0.02 | EU 0.03 | US 0.02)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 4 | 25.0% | 0.27 | -0.45 | 1.1 | 2 |
| TRAIN | 2 | 0.0% | -1.11 | -2.15 | -2.2 | 2 |
| TEST | 2 | 50.0% | 1.65 | 1.25 | 3.3 | 1 |
| phase A | 1 | 0.0% | -1.12 | -1.80 | -1.1 | 1 |
| phase EU | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |
| phase US | 1 | 100.0% | 4.36 | 6.10 | 4.4 | 0 |

- tong: R TB 0.27, KTC bootstrap 95% [-1.11 ; 3.00], n = 4
- TEST: R TB 1.65, KTC bootstrap 95% [-1.06 ; 4.36], n = 2

### V5 kV=2.0 kD=2, TP co dinh 2R

Lenh/ngay **0.148** (A 0.05 | EU 0.05 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 9 | 22.2% | -0.42 | -0.93 | -3.8 | 5 |
| TRAIN | 5 | 40.0% | 0.10 | 0.60 | 0.5 | 2 |
| TEST | 4 | 0.0% | -1.08 | -2.85 | -4.3 | 4 |
| phase A | 3 | 33.3% | -0.09 | -1.13 | -0.3 | 2 |
| phase EU | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| phase US | 3 | 33.3% | -0.10 | 1.17 | -0.3 | 1 |

- tong: R TB -0.42, KTC bootstrap 95% [-1.09 ; 0.57], n = 9
- TEST: R TB -1.08, KTC bootstrap 95% [-1.10 ; -1.06], n = 4

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.14** (5-95%: -1.08 .. 0.68), WR doi chung 31.9%. Setup that: R TB **-0.42**, WR 22.2%. Ti le lan doi chung >= setup that: **73.5%**.

### V5 kV=2.0 kD=2, TP canh/POC >= 2R

Lenh/ngay **0.115** (A 0.03 | EU 0.05 | US 0.03)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 7 | 0.0% | -1.10 | -2.44 | -7.7 | 7 |
| TRAIN | 4 | 0.0% | -1.11 | -2.25 | -4.4 | 4 |
| TEST | 3 | 0.0% | -1.08 | -2.70 | -3.3 | 3 |
| phase A | 2 | 0.0% | -1.10 | -2.45 | -2.2 | 2 |
| phase EU | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| phase US | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |

- tong: R TB -1.10, KTC bootstrap 95% [-1.12 ; -1.08], n = 7
- TEST: R TB -1.08, KTC bootstrap 95% [-1.11 ; -1.06], n = 3

### V5 kV=2.0 kD=3, TP co dinh 2R

Lenh/ngay **0.066** (A 0.02 | EU 0.03 | US 0.02)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 4 | 25.0% | -0.32 | -0.55 | -1.3 | 2 |
| TRAIN | 2 | 50.0% | 0.43 | 2.35 | 0.9 | 1 |
| TEST | 2 | 0.0% | -1.06 | -3.45 | -2.1 | 2 |
| phase A | 1 | 0.0% | -1.06 | -3.30 | -1.1 | 1 |
| phase EU | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |
| phase US | 1 | 100.0% | 1.95 | 7.20 | 1.9 | 0 |

- tong: R TB -0.32, KTC bootstrap 95% [-1.08 ; 1.19], n = 4
- TEST: R TB -1.06, KTC bootstrap 95% [-1.06 ; -1.06], n = 2

Doi chung 199 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.14** (5-95%: -1.11 .. 0.95), WR doi chung 32.0%. Setup that: R TB **-0.32**, WR 25.0%. Ti le lan doi chung >= setup that: **52.8%**.

### V5 kV=2.0 kD=3, TP canh/POC >= 2R

Lenh/ngay **0.033** (A 0.00 | EU 0.03 | US 0.00)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |
| TRAIN | 1 | 0.0% | -1.09 | -2.50 | -1.1 | 1 |
| TEST | 1 | 0.0% | -1.06 | -3.60 | -1.1 | 1 |
| phase A | 0 | - | - | - | 0.0 | 0 |
| phase EU | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |
| phase US | 0 | - | - | - | 0.0 | 0 |

- tong: R TB -1.07, KTC bootstrap 95% [-1.09 ; -1.06], n = 2
- TEST: R TB -1.06, KTC bootstrap 95% [- ; -], n = 1

## B2. V5 GUONG (ask >= kD x bid khi do len)

### V5-guong kV=1.5 kD=2, TP co dinh 2R

Lenh/ngay **0.410** (A 0.16 | EU 0.13 | US 0.11)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 25 | 28.0% | -0.25 | -0.41 | -6.2 | 5 |
| TRAIN | 10 | 20.0% | -0.49 | -0.74 | -4.9 | 5 |
| TEST | 15 | 33.3% | -0.09 | -0.19 | -1.4 | 5 |
| phase A | 10 | 20.0% | -0.48 | -1.54 | -4.8 | 4 |
| phase EU | 8 | 25.0% | -0.34 | -0.49 | -2.7 | 4 |
| phase US | 7 | 42.9% | 0.18 | 1.30 | 1.3 | 2 |

- tong: R TB -0.25, KTC bootstrap 95% [-0.73 ; 0.34], n = 25
- TEST: R TB -0.09, KTC bootstrap 95% [-0.70 ; 0.70], n = 15

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.12** (5-95%: -0.59 .. 0.40), WR doi chung 32.6%. Setup that: R TB **-0.25**, WR 28.0%. Ti le lan doi chung >= setup that: **62.0%**.

### V5-guong kV=1.5 kD=2, TP canh/POC >= 2R

Lenh/ngay **0.410** (A 0.16 | EU 0.13 | US 0.11)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 25 | 8.0% | -0.75 | -1.54 | -18.8 | 12 |
| TRAIN | 10 | 0.0% | -1.09 | -2.75 | -10.9 | 10 |
| TEST | 15 | 13.3% | -0.53 | -0.73 | -7.9 | 12 |
| phase A | 10 | 0.0% | -1.08 | -2.80 | -10.8 | 10 |
| phase EU | 8 | 12.5% | -0.70 | -1.36 | -5.6 | 6 |
| phase US | 7 | 14.3% | -0.33 | 0.07 | -2.3 | 4 |

- tong: R TB -0.75, KTC bootstrap 95% [-1.10 ; -0.20], n = 25
- TEST: R TB -0.53, KTC bootstrap 95% [-1.10 ; 0.40], n = 15

### V5-guong kV=1.5 kD=3, TP co dinh 2R

Lenh/ngay **0.262** (A 0.13 | EU 0.08 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 16 | 31.2% | -0.15 | 0.02 | -2.3 | 4 |
| TRAIN | 7 | 28.6% | -0.22 | -0.07 | -1.6 | 4 |
| TEST | 9 | 33.3% | -0.09 | 0.09 | -0.8 | 3 |
| phase A | 8 | 25.0% | -0.34 | -1.13 | -2.7 | 4 |
| phase EU | 5 | 20.0% | -0.49 | -0.62 | -2.4 | 3 |
| phase US | 3 | 66.7% | 0.92 | 4.13 | 2.8 | 1 |

- tong: R TB -0.15, KTC bootstrap 95% [-0.72 ; 0.60], n = 16
- TEST: R TB -0.09, KTC bootstrap 95% [-1.08 ; 0.92], n = 9

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.15** (5-95%: -0.79 .. 0.52), WR doi chung 31.5%. Setup that: R TB **-0.15**, WR 31.2%. Ti le lan doi chung >= setup that: **46.0%**.

### V5-guong kV=1.5 kD=3, TP canh/POC >= 2R

Lenh/ngay **0.262** (A 0.13 | EU 0.08 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 16 | 12.5% | -0.56 | -1.01 | -8.9 | 7 |
| TRAIN | 7 | 0.0% | -1.08 | -2.94 | -7.6 | 7 |
| TEST | 9 | 22.2% | -0.15 | 0.49 | -1.3 | 6 |
| phase A | 8 | 0.0% | -1.09 | -2.70 | -8.7 | 8 |
| phase EU | 5 | 20.0% | -0.47 | -0.58 | -2.4 | 3 |
| phase US | 3 | 33.3% | 0.72 | 2.77 | 2.2 | 1 |

- tong: R TB -0.56, KTC bootstrap 95% [-1.09 ; 0.27], n = 16
- TEST: R TB -0.15, KTC bootstrap 95% [-1.10 ; 1.15], n = 9

### V5-guong kV=2.0 kD=2, TP co dinh 2R

Lenh/ngay **0.279** (A 0.15 | EU 0.08 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 17 | 17.6% | -0.56 | -1.23 | -9.6 | 6 |
| TRAIN | 8 | 12.5% | -0.72 | -1.19 | -5.7 | 4 |
| TEST | 9 | 22.2% | -0.43 | -1.27 | -3.8 | 5 |
| phase A | 9 | 11.1% | -0.76 | -2.16 | -6.8 | 4 |
| phase EU | 5 | 20.0% | -0.49 | -1.02 | -2.5 | 3 |
| phase US | 3 | 33.3% | -0.09 | 1.20 | -0.3 | 2 |

- tong: R TB -0.56, KTC bootstrap 95% [-1.09 ; -0.02], n = 17
- TEST: R TB -0.43, KTC bootstrap 95% [-1.10 ; 0.56], n = 9

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.13** (5-95%: -0.69 .. 0.51), WR doi chung 32.2%. Setup that: R TB **-0.56**, WR 17.6%. Ti le lan doi chung >= setup that: **88.0%**.

### V5-guong kV=2.0 kD=2, TP canh/POC >= 2R

Lenh/ngay **0.279** (A 0.15 | EU 0.08 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 17 | 0.0% | -1.09 | -2.62 | -18.6 | 17 |
| TRAIN | 8 | 0.0% | -1.09 | -2.69 | -8.7 | 8 |
| TEST | 9 | 0.0% | -1.09 | -2.57 | -9.8 | 9 |
| phase A | 9 | 0.0% | -1.09 | -2.66 | -9.8 | 9 |
| phase EU | 5 | 0.0% | -1.09 | -2.46 | -5.5 | 5 |
| phase US | 3 | 0.0% | -1.09 | -2.80 | -3.3 | 3 |

- tong: R TB -1.09, KTC bootstrap 95% [-1.11 ; -1.08], n = 17
- TEST: R TB -1.09, KTC bootstrap 95% [-1.11 ; -1.08], n = 9

### V5-guong kV=2.0 kD=3, TP co dinh 2R

Lenh/ngay **0.148** (A 0.10 | EU 0.03 | US 0.02)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 9 | 22.2% | -0.42 | -0.89 | -3.8 | 4 |
| TRAIN | 5 | 20.0% | -0.48 | -0.52 | -2.4 | 3 |
| TEST | 4 | 25.0% | -0.34 | -1.35 | -1.4 | 2 |
| phase A | 6 | 16.7% | -0.59 | -1.92 | -3.5 | 4 |
| phase EU | 2 | 0.0% | -1.10 | -2.15 | -2.2 | 2 |
| phase US | 1 | 100.0% | 1.95 | 7.80 | 1.9 | 0 |

- tong: R TB -0.42, KTC bootstrap 95% [-1.09 ; 0.57], n = 9
- TEST: R TB -0.34, KTC bootstrap 95% [-1.09 ; 1.13], n = 4

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.08** (5-95%: -1.08 .. 0.91), WR doi chung 33.8%. Setup that: R TB **-0.42**, WR 22.2%. Ti le lan doi chung >= setup that: **73.5%**.

### V5-guong kV=2.0 kD=3, TP canh/POC >= 2R

Lenh/ngay **0.148** (A 0.10 | EU 0.03 | US 0.02)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 9 | 0.0% | -1.09 | -2.72 | -9.8 | 9 |
| TRAIN | 5 | 0.0% | -1.08 | -2.92 | -5.4 | 5 |
| TEST | 4 | 0.0% | -1.09 | -2.47 | -4.4 | 4 |
| phase A | 6 | 0.0% | -1.09 | -2.67 | -6.5 | 6 |
| phase EU | 2 | 0.0% | -1.10 | -2.15 | -2.2 | 2 |
| phase US | 1 | 0.0% | -1.05 | -4.20 | -1.1 | 1 |

- tong: R TB -1.09, KTC bootstrap 95% [-1.10 ; -1.07], n = 9
- TEST: R TB -1.09, KTC bootstrap 95% [-1.12 ; -1.07], n = 4

### Luoi V5 DUNG DE BAI (tong hop)

| o | n | n TRAIN | R TB TRAIN | n TEST | R TB TEST | dat (R TRAIN>0, R TEST>0, n TEST>=20)? |
|---|---|---|---|---|---|---|
| V5 kV=1.5 kD=2, TP co dinh 2R | 12 | 6 | -0.10 | 6 | -0.60 | khong |
| V5 kV=1.5 kD=2, TP canh/POC >= 2R | 10 | 5 | -1.11 | 5 | -0.01 | khong |
| V5 kV=1.5 kD=3, TP co dinh 2R | 6 | 3 | -0.09 | 3 | -0.09 | khong |
| V5 kV=1.5 kD=3, TP canh/POC >= 2R | 4 | 2 | -1.11 | 2 | 1.65 | khong |
| V5 kV=2.0 kD=2, TP co dinh 2R | 9 | 5 | 0.10 | 4 | -1.08 | khong |
| V5 kV=2.0 kD=2, TP canh/POC >= 2R | 7 | 4 | -1.11 | 3 | -1.08 | khong |
| V5 kV=2.0 kD=3, TP co dinh 2R | 4 | 2 | 0.43 | 2 | -1.06 | khong |
| V5 kV=2.0 kD=3, TP canh/POC >= 2R | 2 | 1 | -1.09 | 1 | -1.06 | khong |

### Luoi V5 GUONG (tong hop)

| o | n | n TRAIN | R TB TRAIN | n TEST | R TB TEST | dat (R TRAIN>0, R TEST>0, n TEST>=20)? |
|---|---|---|---|---|---|---|
| V5-guong kV=1.5 kD=2, TP co dinh 2R | 25 | 10 | -0.49 | 15 | -0.09 | khong |
| V5-guong kV=1.5 kD=2, TP canh/POC >= 2R | 25 | 10 | -1.09 | 15 | -0.53 | khong |
| V5-guong kV=1.5 kD=3, TP co dinh 2R | 16 | 7 | -0.22 | 9 | -0.09 | khong |
| V5-guong kV=1.5 kD=3, TP canh/POC >= 2R | 16 | 7 | -1.08 | 9 | -0.15 | khong |
| V5-guong kV=2.0 kD=2, TP co dinh 2R | 17 | 8 | -0.72 | 9 | -0.43 | khong |
| V5-guong kV=2.0 kD=2, TP canh/POC >= 2R | 17 | 8 | -1.09 | 9 | -1.09 | khong |
| V5-guong kV=2.0 kD=3, TP co dinh 2R | 9 | 5 | -0.48 | 4 | -0.34 | khong |
| V5-guong kV=2.0 kD=3, TP canh/POC >= 2R | 9 | 5 | -1.08 | 4 | -1.09 | khong |

### Doi chieu: fade khi KHONG co tuong (quy tac de bai, kV=2,0 kD=2, TP 2R co dinh, bo 19:20-20:30)

### fade khong tuong

Lenh/ngay **1.787** (A 0.72 | EU 0.43 | US 0.64)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 109 | 33.9% | -0.06 | 0.03 | -6.6 | 12 |
| TRAIN | 56 | 26.8% | -0.27 | -0.43 | -15.4 | 12 |
| TEST | 53 | 41.5% | 0.17 | 0.51 | 8.8 | 5 |
| phase A | 44 | 27.3% | -0.26 | -0.26 | -11.5 | 7 |
| phase EU | 26 | 34.6% | -0.04 | -0.16 | -1.2 | 5 |
| phase US | 39 | 41.0% | 0.16 | 0.47 | 6.1 | 7 |

- tong: R TB -0.06, KTC bootstrap 95% [-0.33 ; 0.21], n = 109
- TEST: R TB 0.17, KTC bootstrap 95% [-0.23 ; 0.56], n = 53

## C. V5-nghich: cung nen pha hut nhung KHONG co tuong => stop ngoai rau, SL = E lui vao 0,5u, TP 2R, het han 10 nen (bo 19:20-20:30)

### V5-nghich (khong tuong: kV=1.5 kD=2)

Lenh/ngay **1.164** (A 0.52 | EU 0.26 | US 0.38)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 71 | 35.2% | -0.07 | -0.35 | -5.3 | 13 |
| TRAIN | 40 | 30.0% | -0.22 | -0.71 | -9.0 | 13 |
| TEST | 31 | 41.9% | 0.12 | 0.13 | 3.7 | 5 |
| phase A | 32 | 40.6% | 0.08 | -0.03 | 2.5 | 5 |
| phase EU | 16 | 31.2% | -0.20 | -0.18 | -3.1 | 6 |
| phase US | 23 | 30.4% | -0.20 | -0.90 | -4.7 | 10 |

- tong: R TB -0.07, KTC bootstrap 95% [-0.41 ; 0.26], n = 71
- TEST: R TB 0.12, KTC bootstrap 95% [-0.37 ; 0.69], n = 31

### V5-nghich (khong tuong: kV=1.5 kD=3)

Lenh/ngay **1.213** (A 0.54 | EU 0.26 | US 0.41)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 74 | 36.5% | -0.04 | -0.29 | -2.9 | 13 |
| TRAIN | 42 | 31.0% | -0.20 | -0.67 | -8.4 | 13 |
| TEST | 32 | 43.8% | 0.17 | 0.20 | 5.5 | 5 |
| phase A | 33 | 39.4% | 0.04 | -0.06 | 1.3 | 5 |
| phase EU | 16 | 31.2% | -0.20 | -0.18 | -3.1 | 6 |
| phase US | 25 | 36.0% | -0.04 | -0.67 | -1.0 | 10 |

- tong: R TB -0.04, KTC bootstrap 95% [-0.36 ; 0.29], n = 74
- TEST: R TB 0.17, KTC bootstrap 95% [-0.30 ; 0.65], n = 32

### V5-nghich (khong tuong: kV=2.0 kD=2)

Lenh/ngay **1.148** (A 0.52 | EU 0.26 | US 0.36)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 70 | 34.3% | -0.10 | -0.36 | -7.1 | 13 |
| TRAIN | 40 | 30.0% | -0.23 | -0.70 | -9.0 | 13 |
| TEST | 30 | 40.0% | 0.06 | 0.09 | 1.9 | 7 |
| phase A | 32 | 40.6% | 0.08 | -0.01 | 2.4 | 5 |
| phase EU | 16 | 31.2% | -0.20 | -0.18 | -3.1 | 6 |
| phase US | 22 | 27.3% | -0.29 | -1.00 | -6.4 | 12 |

- tong: R TB -0.10, KTC bootstrap 95% [-0.44 ; 0.24], n = 70
- TEST: R TB 0.06, KTC bootstrap 95% [-0.44 ; 0.57], n = 30

### V5-nghich (khong tuong: kV=2.0 kD=3)

Lenh/ngay **1.197** (A 0.54 | EU 0.26 | US 0.39)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 73 | 35.6% | -0.07 | -0.31 | -4.8 | 13 |
| TRAIN | 42 | 31.0% | -0.20 | -0.65 | -8.5 | 13 |
| TEST | 31 | 41.9% | 0.12 | 0.15 | 3.7 | 7 |
| phase A | 33 | 39.4% | 0.04 | -0.04 | 1.2 | 5 |
| phase EU | 16 | 31.2% | -0.20 | -0.18 | -3.1 | 6 |
| phase US | 24 | 33.3% | -0.12 | -0.77 | -2.8 | 12 |

- tong: R TB -0.07, KTC bootstrap 95% [-0.39 ; 0.26], n = 73
- TEST: R TB 0.12, KTC bootstrap 95% [-0.37 ; 0.61], n = 31

### V5-nghich ban tho (khong loc tuong, bo 19:20-20:30) - tham chieu

Lenh/ngay **1.197** (A 0.54 | EU 0.26 | US 0.39)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 73 | 35.6% | -0.07 | -0.31 | -4.8 | 13 |
| TRAIN | 42 | 31.0% | -0.20 | -0.65 | -8.5 | 13 |
| TEST | 31 | 41.9% | 0.12 | 0.15 | 3.7 | 7 |
| phase A | 33 | 39.4% | 0.04 | -0.04 | 1.2 | 5 |
| phase EU | 16 | 31.2% | -0.20 | -0.18 | -3.1 | 6 |
| phase US | 24 | 33.3% | -0.12 | -0.77 | -2.8 | 12 |

- tong: R TB -0.07, KTC bootstrap 95% [-0.39 ; 0.26], n = 73
- TEST: R TB 0.12, KTC bootstrap 95% [-0.37 ; 0.61], n = 31

### Tong hop V5-nghich

| o | n | n TRAIN | R TB TRAIN | n TEST | R TB TEST |
|---|---|---|---|---|---|
| V5-nghich (khong tuong: kV=1.5 kD=2) | 71 | 40 | -0.22 | 31 | 0.12 |
| V5-nghich (khong tuong: kV=1.5 kD=3) | 74 | 42 | -0.20 | 32 | 0.17 |
| V5-nghich (khong tuong: kV=2.0 kD=2) | 70 | 40 | -0.23 | 30 | 0.06 |
| V5-nghich (khong tuong: kV=2.0 kD=3) | 73 | 42 | -0.20 | 31 | 0.12 |

## D. Ket luan vong 3

**Khong o V5 nao duong ca TRAIN lan TEST voi n TEST >= 20 => ket luan cuoi: C tat mac dinh.**



---

# VONG 2 - Setup C: hop luu (V3) va ngay khong xu huong (V4) - CHI file 90d (QD-6)

**QD-6: chi do tren file 90d GCZ26. File 2 nam (`fp_GC_XCEC_*`) bi bo vi du lieu footprint truoc do sai ma hop dong; moi bang 2 nam trong phan Vong 1 ben duoi chi de tham khao, KHONG dung de quyet dinh.**

TRAIN <= 2026-09-15, TEST tu 2026-09-16. Cung seed, o khoi diem (xuyen 2 tick, rong >= 6). V3 = chi fade canh E khi trong ban kinh 0,7 gia quanh E co them >= 1 vung khac (VWAP ngay/tuan, POC/VAH/VAL hom qua, POC/VAH/VAL Au, IB, HVN ngay/tuan, naked POC; vung trung gia E bi bo). V4 = V3 + |VWAP ngay - VWAP tuan| <= 2u (u = trung vi bien do 50 nen) va close nen vao nam trong VA hom qua. Doi chung 200 lan. Vi n nho, bao them khoang tin cay bootstrap 95% (10.000 lan, seed 0) cho R TB.

## 0. Moc so sanh: o khoi diem vong 1 (khong loc hop luu), file 90d

- TP poc: n 103, WR 12.6%, tong: R TB -0.43, KTC bootstrap 95% [-0.76 ; -0.06], n = 103; TEST: TEST: R TB -0.12, KTC bootstrap 95% [-0.70 ; 0.53], n = 45
- TP fixed2: n 121, WR 27.3%, tong: R TB -0.26, KTC bootstrap 95% [-0.48 ; -0.01], n = 121; TEST: TEST: R TB -0.14, KTC bootstrap 95% [-0.51 ; 0.22], n = 58

## V3 hop luu, TP canh/POC >= 2R

Lenh/ngay: **0.164** (A 0.05 | EU 0.00 | US 0.11) tren 61 phien sach

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 10 | 10.0% | -0.62 | -1.08 | -6.2 | 6 |
| TRAIN | 8 | 12.5% | -0.51 | -0.70 | -4.1 | 6 |
| TEST | 2 | 0.0% | -1.09 | -2.60 | -2.2 | 2 |
| rieng phase US | 7 | 14.3% | -0.41 | -0.79 | -2.8 | 4 |
| US TRAIN | 6 | 16.7% | -0.30 | -0.40 | -1.8 | 4 |
| US TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| phase A | 3 | 0.0% | -1.13 | -1.77 | -3.4 | 3 |
| phase EU | 0 | - | - | - | 0.0 | 0 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 93 | 12.9% | -0.41 | -0.96 | -38.4 | 30 |
| nconf = 2 | 10 | 10.0% | -0.62 | -1.08 | -6.2 | 6 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

- tong: R TB -0.62, KTC bootstrap 95% [-1.12 ; 0.35], n = 10
- TEST: R TB -1.09, KTC bootstrap 95% [-1.11 ; -1.07], n = 2

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.31** (5-95%: -1.11 .. 3.36), WR doi chung 17.6%. Setup that: R TB **-0.62**, WR 10.0%. Ti le lan doi chung >= setup that: **68.5%**.

Vi du (toi da 5 thang + 5 thua, dan deu):

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-11 18:12 | 2026-09-12 01:12 | US | SELL | 4396.4 (VAH_EU) | 4395.1 | 4397.6 | 4385.6 | TP | 3.72 |

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-31 17:43 | 2026-08-01 00:43 | US | BUY | 4106.4 (VAL_EU) | 4107.7 | 4105.8 | 4112.4 | SL | -1.11 |
| 2026-08-20 23:39 | 2026-08-21 06:39 | A | SELL | 4580.0 (VAH_Y) | 4579.7 | 4581.3 | 4550.0 | SL | -1.12 |
| 2026-08-25 15:09 | 2026-08-25 22:09 | US | BUY | 4687.2 (VAL_EU) | 4688.4 | 4685.4 | 4696.4 | SL | -1.07 |
| 2026-09-15 13:14 | 2026-09-15 20:14 | US | SELL | 4327.2 (VAH_EU) | 4326.8 | 4329.2 | 4305.6 | SL | -1.08 |
| 2026-10-21 02:07 | 2026-10-21 09:07 | A | BUY | 4135.2 (VAL_Y) | 4136.0 | 4134.1 | 4142.4 | SL | -1.11 |

## V3 hop luu, TP co dinh 2R

Lenh/ngay: **0.180** (A 0.05 | EU 0.00 | US 0.13) tren 61 phien sach

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 11 | 18.2% | -0.55 | -0.98 | -6.1 | 5 |
| TRAIN | 8 | 25.0% | -0.35 | -0.26 | -2.8 | 5 |
| TEST | 3 | 0.0% | -1.08 | -2.90 | -3.2 | 3 |
| rieng phase US | 8 | 25.0% | -0.33 | -0.69 | -2.7 | 3 |
| US TRAIN | 6 | 33.3% | -0.09 | 0.18 | -0.5 | 3 |
| US TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| phase A | 3 | 0.0% | -1.13 | -1.77 | -3.4 | 3 |
| phase EU | 0 | - | - | - | 0.0 | 0 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 110 | 28.2% | -0.23 | -0.50 | -25.2 | 10 |
| nconf = 2 | 11 | 18.2% | -0.55 | -0.98 | -6.1 | 5 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

- tong: R TB -0.55, KTC bootstrap 95% [-1.11 ; 0.27], n = 11
- TEST: R TB -1.08, KTC bootstrap 95% [-1.11 ; -1.06], n = 3

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.14** (5-95%: -0.78 .. 0.76), WR doi chung 31.9%. Setup that: R TB **-0.55**, WR 18.2%. Ti le lan doi chung >= setup that: **83.5%**.

Vi du (toi da 5 thang + 5 thua, dan deu):

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-25 16:13 | 2026-08-25 23:13 | US | SELL | 4701.6 (VAH_EU) | 4701.5 | 4704.5 | 4695.5 | TP | 1.93 |
| 2026-09-11 18:12 | 2026-09-12 01:12 | US | SELL | 4396.4 (VAH_EU) | 4395.1 | 4397.6 | 4390.1 | TP | 1.92 |

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-31 17:43 | 2026-08-01 00:43 | US | BUY | 4106.4 (VAL_EU) | 4107.7 | 4105.8 | 4111.5 | SL | -1.11 |
| 2026-08-20 23:39 | 2026-08-21 06:39 | A | SELL | 4580.0 (VAH_Y) | 4579.7 | 4581.3 | 4576.5 | SL | -1.12 |
| 2026-08-25 15:09 | 2026-08-25 22:09 | US | BUY | 4687.2 (VAL_EU) | 4688.4 | 4685.4 | 4694.4 | SL | -1.07 |
| 2026-10-06 16:50 | 2026-10-06 23:50 | US | SELL | 4184.4 (VAH_EU) | 4184.0 | 4186.9 | 4178.2 | SL | -1.07 |
| 2026-10-21 02:07 | 2026-10-21 09:07 | A | BUY | 4135.2 (VAL_Y) | 4136.0 | 4134.1 | 4139.8 | SL | -1.11 |

## V4 = V3 + ngay khong xu huong, TP canh/POC >= 2R

Lenh/ngay: **0.049** (A 0.00 | EU 0.00 | US 0.05) tren 61 phien sach

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| TRAIN | 2 | 0.0% | -1.08 | -2.70 | -2.2 | 2 |
| TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| rieng phase US | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| US TRAIN | 2 | 0.0% | -1.08 | -2.70 | -2.2 | 2 |
| US TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| phase A | 0 | - | - | - | 0.0 | 0 |
| phase EU | 0 | - | - | - | 0.0 | 0 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 93 | 12.9% | -0.41 | -0.96 | -38.4 | 30 |
| nconf = 2 | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

- tong: R TB -1.08, KTC bootstrap 95% [-1.10 ; -1.07], n = 3
- TEST: R TB -1.07, KTC bootstrap 95% [- ; -], n = 1

Doi chung 196 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.26** (5-95%: -1.14 .. 3.52), WR doi chung 18.3%. Setup that: R TB **-1.08**, WR 0.0%. Ti le lan doi chung >= setup that: **59.7%**.

Vi du (toi da 5 thang + 5 thua, dan deu):

(khong co)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-25 15:09 | 2026-08-25 22:09 | US | BUY | 4687.2 (VAL_EU) | 4688.4 | 4685.4 | 4696.4 | SL | -1.07 |
| 2026-08-25 16:43 | 2026-08-25 23:43 | US | SELL | 4701.6 (VAH_EU) | 4700.9 | 4702.9 | 4696.4 | SL | -1.10 |
| 2026-10-06 16:50 | 2026-10-06 23:50 | US | SELL | 4184.4 (VAH_EU) | 4184.0 | 4186.9 | 4146.4 | SL | -1.07 |

## V4 = V3 + ngay khong xu huong, TP co dinh 2R

Lenh/ngay: **0.066** (A 0.00 | EU 0.00 | US 0.07) tren 61 phien sach

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| TRAIN | 2 | 50.0% | 0.43 | 1.30 | 0.9 | 1 |
| TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| rieng phase US | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| US TRAIN | 2 | 50.0% | 0.43 | 1.30 | 0.9 | 1 |
| US TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| phase A | 0 | - | - | - | 0.0 | 0 |
| phase EU | 0 | - | - | - | 0.0 | 0 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 110 | 28.2% | -0.23 | -0.50 | -25.2 | 10 |
| nconf = 2 | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

- tong: R TB -0.32, KTC bootstrap 95% [-1.07 ; 1.18], n = 4
- TEST: R TB -1.06, KTC bootstrap 95% [-1.07 ; -1.06], n = 2

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.16** (5-95%: -1.12 .. 1.15), WR doi chung 31.3%. Setup that: R TB **-0.32**, WR 25.0%. Ti le lan doi chung >= setup that: **51.5%**.

Vi du (toi da 5 thang + 5 thua, dan deu):

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-25 16:13 | 2026-08-25 23:13 | US | SELL | 4701.6 (VAH_EU) | 4701.5 | 4704.5 | 4695.5 | TP | 1.93 |

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-25 15:09 | 2026-08-25 22:09 | US | BUY | 4687.2 (VAL_EU) | 4688.4 | 4685.4 | 4694.4 | SL | -1.07 |
| 2026-10-06 16:50 | 2026-10-06 23:50 | US | SELL | 4184.4 (VAH_EU) | 4184.0 | 4186.9 | 4178.2 | SL | -1.07 |
| 2026-10-13 12:40 | 2026-10-13 19:40 | US | BUY | 4207.2 (VAL_EU) | 4208.7 | 4205.4 | 4215.3 | SL | -1.06 |

## Ket luan vong 2

| o | n tong 90d | n TEST | R TB TEST | du tieu chuan (n TEST >= 30 va R TB TEST > 0)? |
|---|---|---|---|---|
| V3 hop luu, TP canh/POC >= 2R | 10 | 2 | -1.09 | khong |
| V3 hop luu, TP co dinh 2R | 11 | 3 | -1.08 | khong |
| V4 = V3 + ngay khong xu huong, TP canh/POC >= 2R | 3 | 1 | -1.07 | khong |
| V4 = V3 + ngay khong xu huong, TP co dinh 2R | 4 | 2 | -1.06 | khong |

**Khong o nao co n TEST >= 30 va R TB TEST duong => ket luan cuoi: C tat mac dinh.**

## Danh gia vong 2 (viet tay)

1. **Hop luu giet gan het lenh:** chi con 10-11 lenh / 90 ngay (0,16-0,18 lenh/ngay) o V3 va 3-4 lenh o V4; n TEST chi 1-3. Khong the ket luan, nhung huong so khong co dau hieu tot: TEST 0 thang tren moi o.
2. **KTC bootstrap rong ca bang nhau:** vd V3 TP poc tong R TB -0,62 [-1,12 ; +0,35] (n 10). Muc moc vong 1 (khong loc, n 103): -0,43 [-0,76 ; -0,06], nghia la bao ham am du co n lon hon; TEST -0,12 [-0,70 ; +0,53] (n 45) thi khong loai duoc 0.
3. **Doi chung** cua cac o V3/V4 co khoang 5-95% cuc rong (vd -1,11..+3,36) vi it lenh => khong phan biet duoc setup voi nen ngau nhien.
4. **Ngay khong xu huong (V4):** dieu kien |VWAP ngay - VWAP tuan| <= 2u rat chat (u ~ 1 gia => <= ~2 gia) nen gan nhu khong con lenh; khong kiem chung duoc gia thuyet "chan thang 8".
5. **Ket luan cuoi (theo tieu chi huong dan, chi 90d):** khong o nao co n TEST >= 30 va R TB TEST duong => **C tat mac dinh**. Muon biet hop luu co that su giup hay khong can nhieu du lieu hon (khong the lay them tu file 90d), khong nen ep ngưỡng cho no ra lenh.



---

**LUU Y (QD-6): VONG 1 duoi day. Cac bang `file 2 nam` (muc 6-9 va phan "PHAN 2 NAM") chi con THAM KHAO, KHONG dung de quyet dinh (du lieu footprint truoc do sai ma hop dong). Chi file 90d co gia tri quyet dinh.**

# RESULTS-C: Setup C Fade canh (sinh boi setup_c_fade_canh.py, deterministic)

Gio trong file = UTC, cot VN = UTC+7. Chi phi 0,2 gia/lenh. 1 lenh mo cung luc. TRAIN <= 2026-09-15, TEST tu 2026-09-16.
O khoi diem (khai bao truoc khi do): xuyen >= 2 tick, range rong >= 6 gia, TP = gan nhat trong {canh doi dien, POC} va >= 2R.

## 1. File 90d, o khoi diem, TP canh/POC (>= 2R)

Tham so: {'pen_ticks': 2, 'min_width': 6.0, 'tp_mode': 'poc'}. So phien sach (khong splice/thin, >=300 nen): **61**.

Lenh da dong **103** (con mo 0); lenh/ngay **1.689** (tong 3 phase) = A 0.70 | EU 0.33 | US 0.66

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 103 | 12.6% | -0.43 | -0.97 | -44.7 | 36 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-07 | 6 | 0.0% | -1.09 | -2.73 | -6.5 | 6 |
| 2026-08 | 30 | 0.0% | -1.08 | -3.03 | -32.3 | 30 |
| 2026-09 | 42 | 23.8% | 0.29 | 1.21 | 12.1 | 9 |
| 2026-10 | 25 | 12.0% | -0.72 | -1.76 | -17.9 | 11 |

### Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 43 | 9.3% | -0.41 | -0.61 | -17.5 | 16 |
| EU | 20 | 10.0% | -0.67 | -1.69 | -13.4 | 13 |
| US | 40 | 17.5% | -0.34 | -1.00 | -13.8 | 15 |

### TRAIN (phien <= 2026-09-15) / TEST (>= 2026-09-16)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 58 | 6.9% | -0.68 | -1.63 | -39.3 | 36 |
| TEST | 45 | 20.0% | -0.12 | -0.12 | -5.4 | 20 |

### Doi chung

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.05** (5-95%: -0.44 .. 0.62), WR doi chung 17.7%. Setup that: R TB **-0.43**, WR 12.6%. Ti le lan doi chung >= setup that: **94.0%**.

### 5 vi du THANG (chon dan deu theo thoi gian, khong chon dep)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 00:53 | 2026-09-01 07:53 | A | SELL | 4506.8 (VAH_Y) | 4506.5 | 4510.4 | 4483.2 | TP | 5.92 |
| 2026-09-15 03:24 | 2026-09-15 10:24 | A | SELL | 4353.6 (VAH_Y) | 4351.3 | 4354.7 | 4326.4 | TP | 7.26 |
| 2026-09-21 01:48 | 2026-09-21 08:48 | A | SELL | 4420.8 (VAH_Y) | 4419.3 | 4422.3 | 4392.4 | TP | 8.90 |
| 2026-09-22 02:18 | 2026-09-22 09:18 | A | BUY | 4378.4 (VAL_Y) | 4380.0 | 4376.7 | 4389.2 | TP | 2.73 |
| 2026-10-20 13:51 | 2026-10-20 20:51 | US | SELL | 4148.4 (VAH_EU) | 4146.7 | 4150.1 | 4139.6 | TP | 2.03 |

### 5 vi du THUA (dan deu theo thoi gian)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 07:07 | 2026-07-29 14:07 | EU | SELL | 4102.8 (VAH_Y) | 4102.0 | 4104.3 | 4084.0 | SL | -1.09 |
| 2026-08-19 22:53 | 2026-08-20 05:53 | A | SELL | 4576.8 (VAH_Y) | 4576.5 | 4578.2 | 4545.2 | SL | -1.12 |
| 2026-09-10 09:43 | 2026-09-10 16:43 | EU | BUY | 4433.2 (VAL_Y) | 4434.1 | 4430.9 | 4445.6 | SL | -1.06 |
| 2026-09-30 02:03 | 2026-09-30 09:03 | A | SELL | 4205.6 (VAH_Y) | 4205.5 | 4207.2 | 4189.2 | SL | -1.12 |
| 2026-10-21 12:50 | 2026-10-21 19:50 | US | SELL | 4146.0 (VAH_EU) | 4144.8 | 4147.6 | 4139.2 | SL | -1.07 |

## 2. File 90d, o khoi diem, TP co dinh 2R

Tham so: {'pen_ticks': 2, 'min_width': 6.0, 'tp_mode': 'fixed2'}. So phien sach (khong splice/thin, >=300 nen): **61**.

Lenh da dong **121** (con mo 0); lenh/ngay **1.984** (tong 3 phase) = A 0.75 | EU 0.38 | US 0.85

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 121 | 27.3% | -0.26 | -0.54 | -31.2 | 11 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-07 | 6 | 16.7% | -0.59 | -0.83 | -3.5 | 3 |
| 2026-08 | 33 | 18.2% | -0.53 | -1.37 | -17.5 | 9 |
| 2026-09 | 45 | 40.0% | 0.12 | 0.64 | 5.5 | 7 |
| 2026-10 | 37 | 21.6% | -0.43 | -1.20 | -15.7 | 11 |

### Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 46 | 28.3% | -0.23 | -0.25 | -10.7 | 8 |
| EU | 23 | 26.1% | -0.30 | -0.61 | -6.8 | 10 |
| US | 52 | 26.9% | -0.26 | -0.77 | -13.7 | 11 |

### TRAIN (phien <= 2026-09-15) / TEST (>= 2026-09-16)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 63 | 23.8% | -0.36 | -0.73 | -22.8 | 9 |
| TEST | 58 | 31.0% | -0.14 | -0.33 | -8.4 | 11 |

### Doi chung

Doi chung 200 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.13** (5-95%: -0.36 .. 0.13), WR doi chung 32.4%. Setup that: R TB **-0.26**, WR 27.3%. Ti le lan doi chung >= setup that: **76.5%**.

### 5 vi du THANG (chon dan deu theo thoi gian, khong chon dep)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-30 03:04 | 2026-07-30 10:04 | A | SELL | 4126.8 (VAH_Y) | 4126.3 | 4130.1 | 4118.7 | TP | 1.95 |
| 2026-09-08 14:53 | 2026-09-08 21:53 | US | BUY | 4437.2 (VAL_EU) | 4438.7 | 4434.8 | 4446.5 | TP | 1.95 |
| 2026-09-18 16:59 | 2026-09-18 23:59 | US | BUY | 4419.2 (VAL_EU) | 4421.1 | 4418.4 | 4426.5 | TP | 1.93 |
| 2026-09-29 00:24 | 2026-09-29 07:24 | A | BUY | 4148.0 (VAL_Y) | 4149.5 | 4146.0 | 4156.5 | TP | 1.94 |
| 2026-10-20 13:51 | 2026-10-20 20:51 | US | SELL | 4148.4 (VAH_EU) | 4146.7 | 4150.1 | 4139.9 | TP | 1.94 |

### 5 vi du THUA (dan deu theo thoi gian)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-07-29 07:07 | 2026-07-29 14:07 | EU | SELL | 4102.8 (VAH_Y) | 4102.0 | 4104.3 | 4097.4 | SL | -1.09 |
| 2026-08-20 23:39 | 2026-08-21 06:39 | A | SELL | 4580.0 (VAH_Y) | 4579.7 | 4581.3 | 4576.5 | SL | -1.12 |
| 2026-09-14 17:28 | 2026-09-15 00:28 | US | SELL | 4353.2 (VAH_EU) | 4352.6 | 4355.3 | 4347.2 | SL | -1.07 |
| 2026-10-02 12:21 | 2026-10-02 19:21 | US | BUY | 4209.6 (VAL_EU) | 4211.7 | 4208.1 | 4218.9 | SL | -1.06 |
| 2026-10-21 12:50 | 2026-10-21 19:50 | US | SELL | 4146.0 (VAH_EU) | 4144.8 | 4147.6 | 4139.2 | SL | -1.07 |

## 3. Luoi 3x3 (xuyen toi thieu x rong range toi thieu), file 90d

### TP canh/POC >= 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n TRAIN | R TB TRAIN | n TEST | R TB TEST | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 112 | 12.5% | -0.36 | 60 | -0.69 | 52 | 0.02 | -0.79 |
| 1 | 6 | 112 | 12.5% | -0.36 | 60 | -0.69 | 52 | 0.02 | -0.79 |
| 1 | 8 | 112 | 12.5% | -0.36 | 60 | -0.69 | 52 | 0.02 | -0.79 |
| 2 | 4 | 103 | 12.6% | -0.43 | 58 | -0.68 | 45 | -0.12 | -0.97 |
| 2 (o khoi diem) | 6 | 103 | 12.6% | -0.43 | 58 | -0.68 | 45 | -0.12 | -0.97 |
| 2 | 8 | 103 | 12.6% | -0.43 | 58 | -0.68 | 45 | -0.12 | -0.97 |
| 4 | 4 | 86 | 14.0% | -0.36 | 48 | -0.59 | 38 | -0.07 | -0.71 |
| 4 | 6 | 86 | 14.0% | -0.36 | 48 | -0.59 | 38 | -0.07 | -0.71 |
| 4 | 8 | 86 | 14.0% | -0.36 | 48 | -0.59 | 38 | -0.07 | -0.71 |

### TP co dinh 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n TRAIN | R TB TRAIN | n TEST | R TB TEST | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 130 | 28.5% | -0.23 | 66 | -0.31 | 64 | -0.14 | -0.40 |
| 1 | 6 | 130 | 28.5% | -0.23 | 66 | -0.31 | 64 | -0.14 | -0.40 |
| 1 | 8 | 130 | 28.5% | -0.23 | 66 | -0.31 | 64 | -0.14 | -0.40 |
| 2 | 4 | 121 | 27.3% | -0.26 | 63 | -0.36 | 58 | -0.14 | -0.54 |
| 2 (o khoi diem) | 6 | 121 | 27.3% | -0.26 | 63 | -0.36 | 58 | -0.14 | -0.54 |
| 2 | 8 | 121 | 27.3% | -0.26 | 63 | -0.36 | 58 | -0.14 | -0.54 |
| 4 | 4 | 102 | 29.4% | -0.19 | 51 | -0.37 | 51 | -0.02 | -0.39 |
| 4 | 6 | 102 | 29.4% | -0.19 | 51 | -0.37 | 51 | -0.02 | -0.39 |
| 4 | 8 | 102 | 29.4% | -0.19 | 51 | -0.37 | 51 | -0.02 | -0.39 |

### Phu luc luoi: VA hom qua o file 90d luon rong >= 10 gia nen cot 4/6/8 khong chan lenh nao (cac o giong het nhau). Quet them rong >= 12/16/20/30 (xuyen 2 tick)

#### TP canh/POC >= 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n TRAIN | R TB TRAIN | n TEST | R TB TEST | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 12 | 100 | 12.0% | -0.46 | 58 | -0.68 | 42 | -0.15 | -1.03 |
| 2 | 16 | 89 | 9.0% | -0.54 | 52 | -0.79 | 37 | -0.19 | -1.24 |
| 2 | 20 | 81 | 8.6% | -0.55 | 47 | -0.76 | 34 | -0.27 | -1.24 |
| 2 | 30 | 55 | 9.1% | -0.47 | 37 | -0.67 | 18 | -0.07 | -1.00 |

#### TP co dinh 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n TRAIN | R TB TRAIN | n TEST | R TB TEST | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 12 | 111 | 26.1% | -0.29 | 62 | -0.35 | 49 | -0.22 | -0.63 |
| 2 | 16 | 98 | 24.5% | -0.34 | 54 | -0.47 | 44 | -0.19 | -0.74 |
| 2 | 20 | 89 | 25.8% | -0.30 | 49 | -0.41 | 40 | -0.18 | -0.58 |
| 2 | 30 | 59 | 30.5% | -0.16 | 38 | -0.29 | 21 | 0.07 | -0.19 |

## 4. Chi giu lenh co delta nen ung ho manh (|delta| >= trung vi |delta| 50 nen truoc do, khong nhin truoc)

TP poc:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| moi lenh | 103 | 12.6% | -0.43 | -0.97 | -44.7 | 36 |
| delta manh | 83 | 12.0% | -0.41 | -0.86 | -34.1 | 25 |
| moi lenh TRAIN | 58 | 6.9% | -0.68 | -1.63 | -39.3 | 36 |
| delta manh TRAIN | 48 | 10.4% | -0.50 | -1.12 | -24.1 | 21 |
| moi lenh TEST | 45 | 20.0% | -0.12 | -0.12 | -5.4 | 20 |
| delta manh TEST | 35 | 14.3% | -0.28 | -0.50 | -9.9 | 25 |

TP fixed2:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| moi lenh | 121 | 27.3% | -0.26 | -0.54 | -31.2 | 11 |
| delta manh | 97 | 23.7% | -0.37 | -0.88 | -35.4 | 13 |
| moi lenh TRAIN | 63 | 23.8% | -0.36 | -0.73 | -22.8 | 9 |
| delta manh TRAIN | 51 | 23.5% | -0.37 | -0.75 | -18.8 | 13 |
| moi lenh TEST | 58 | 31.0% | -0.14 | -0.33 | -8.4 | 11 |
| delta manh TEST | 46 | 23.9% | -0.36 | -1.02 | -16.6 | 12 |

## 5. Hai bien the co che (vong 2), o khoi diem, file 90d

### V1 doi 1 nen M1 nua dong lai trong range (confirm)

TP poc:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| tong | 72 | 16.7% | -0.19 | -0.27 | -13.3 | 24 |
| TRAIN | 36 | 13.9% | -0.20 | -0.47 | -7.0 | 12 |
| TEST | 36 | 19.4% | -0.17 | -0.08 | -6.3 | 24 |
| phase A | 26 | 19.2% | -0.06 | 0.83 | -1.7 | 10 |
| phase EU | 19 | 10.5% | -0.15 | -1.07 | -2.9 | 11 |
| phase US | 27 | 18.5% | -0.32 | -0.77 | -8.7 | 10 |

Doi chung 50 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.06** (5-95%: -0.45 .. 0.61), WR doi chung 18.0%. Setup that: R TB **-0.19**, WR 16.7%. Ti le lan doi chung >= setup that: **74.0%**.

TP fixed2:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| tong | 83 | 26.5% | -0.28 | -0.52 | -23.4 | 13 |
| TRAIN | 40 | 30.0% | -0.18 | -0.24 | -7.2 | 8 |
| TEST | 43 | 23.3% | -0.38 | -0.78 | -16.2 | 13 |
| phase A | 26 | 26.9% | -0.27 | -0.12 | -7.1 | 10 |
| phase EU | 20 | 15.0% | -0.63 | -1.73 | -12.6 | 9 |
| phase US | 37 | 32.4% | -0.10 | -0.14 | -3.7 | 5 |

Doi chung 50 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.13** (5-95%: -0.38 .. 0.10), WR doi chung 32.2%. Setup that: R TB **-0.28**, WR 26.5%. Ti le lan doi chung >= setup that: **82.0%**.

### V2 chi fade lan cham thu 2+ cua canh (second_touch)

TP poc:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| tong | 96 | 12.5% | -0.43 | -0.95 | -41.0 | 34 |
| TRAIN | 53 | 7.5% | -0.64 | -1.49 | -33.9 | 34 |
| TEST | 43 | 18.6% | -0.16 | -0.27 | -7.0 | 21 |
| phase A | 40 | 7.5% | -0.45 | -0.75 | -18.1 | 16 |
| phase EU | 17 | 11.8% | -0.60 | -1.42 | -10.2 | 11 |
| phase US | 39 | 17.9% | -0.33 | -0.94 | -12.7 | 15 |

Doi chung 50 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.01** (5-95%: -0.53 .. 0.53), WR doi chung 16.9%. Setup that: R TB **-0.43**, WR 12.5%. Ti le lan doi chung >= setup that: **88.0%**.

TP fixed2:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| tong | 111 | 27.0% | -0.27 | -0.55 | -29.5 | 11 |
| TRAIN | 57 | 24.6% | -0.34 | -0.64 | -19.4 | 8 |
| TEST | 54 | 29.6% | -0.19 | -0.45 | -10.1 | 11 |
| phase A | 43 | 27.9% | -0.24 | -0.29 | -10.5 | 7 |
| phase EU | 19 | 21.1% | -0.45 | -0.95 | -8.5 | 9 |
| phase US | 49 | 28.6% | -0.21 | -0.62 | -10.5 | 10 |

Doi chung 50 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.12** (5-95%: -0.38 .. 0.18), WR doi chung 32.7%. Setup that: R TB **-0.27**, WR 27.0%. Ti le lan doi chung >= setup that: **82.0%**.

# PHAN 2 NAM: `fp_GC_XCEC_Time_20240801-20260819_748d9h` (ma lien tuc GC, loc +-2 phien quanh cho noi; 2 nua cat 2025-08-01)

Luu y: file nay trung ~1 thang (07-23 -> 08-19/2026) voi file 90d nhung la ma lien tuc GC (khac hop dong GCZ26); doi chung chay 60 lan.

## 6. 2 nam, o khoi diem, TP canh/POC

Tham so: {'pen_ticks': 2, 'min_width': 6.0, 'tp_mode': 'poc'}. So phien sach (khong splice/thin, >=300 nen): **492**.

Lenh da dong **587** (con mo 0); lenh/ngay **1.193** (tong 3 phase) = A 0.49 | EU 0.26 | US 0.45

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 587 | 19.3% | -0.03 | -0.07 | -16.9 | 29 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 26 | 15.4% | -0.60 | -0.98 | -15.5 | 11 |
| 2024-09 | 24 | 25.0% | -0.11 | 0.54 | -2.7 | 6 |
| 2024-10 | 22 | 36.4% | 0.99 | 1.14 | 21.9 | 5 |
| 2024-11 | 25 | 24.0% | 0.88 | 1.39 | 22.1 | 9 |
| 2024-12 | 24 | 20.8% | 0.19 | -0.06 | 4.5 | 5 |
| 2025-01 | 21 | 4.8% | -0.98 | -1.24 | -20.6 | 17 |
| 2025-02 | 26 | 30.8% | 0.29 | 0.65 | 7.6 | 5 |
| 2025-03 | 30 | 16.7% | 0.01 | -0.34 | 0.3 | 9 |
| 2025-04 | 25 | 16.0% | 0.03 | 0.46 | 0.8 | 8 |
| 2025-05 | 25 | 12.0% | -0.28 | -0.77 | -7.0 | 8 |
| 2025-06 | 35 | 14.3% | -0.61 | -1.03 | -21.2 | 10 |
| 2025-07 | 17 | 23.5% | -0.16 | -0.11 | -2.7 | 6 |
| 2025-08 | 24 | 33.3% | 0.56 | 1.15 | 13.5 | 5 |
| 2025-09 | 38 | 28.9% | 0.44 | 0.82 | 16.8 | 7 |
| 2025-10 | 22 | 4.5% | -0.75 | -2.35 | -16.5 | 15 |
| 2025-11 | 20 | 35.0% | 0.96 | 2.97 | 19.1 | 5 |
| 2025-12 | 25 | 12.0% | -0.55 | -1.13 | -13.7 | 12 |
| 2026-01 | 20 | 10.0% | -0.72 | -2.03 | -14.4 | 17 |
| 2026-02 | 11 | 9.1% | -0.11 | -0.46 | -1.2 | 7 |
| 2026-03 | 26 | 23.1% | 0.16 | 0.55 | 4.1 | 7 |
| 2026-04 | 30 | 6.7% | -0.85 | -2.51 | -25.5 | 19 |
| 2026-05 | 20 | 20.0% | -0.27 | -0.71 | -5.5 | 5 |
| 2026-06 | 16 | 12.5% | -0.27 | -0.27 | -4.4 | 8 |
| 2026-07 | 21 | 28.6% | 1.38 | 3.65 | 29.1 | 5 |
| 2026-08 | 14 | 7.1% | -0.41 | -0.87 | -5.8 | 9 |

### Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 240 | 15.4% | 0.01 | -0.18 | 1.8 | 39 |
| EU | 127 | 15.7% | -0.09 | -0.35 | -11.9 | 20 |
| US | 220 | 25.5% | -0.03 | 0.21 | -6.8 | 15 |

### Hai nua file 2 nam (cat 2025-08-01)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| H1 | 300 | 19.7% | -0.04 | -0.06 | -12.6 | 19 |
| H2 | 287 | 18.8% | -0.01 | -0.08 | -4.3 | 29 |

### Doi chung

Doi chung 60 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.17** (5-95%: -0.34 .. 0.04), WR doi chung 17.7%. Setup that: R TB **-0.03**, WR 19.3%. Ti le lan doi chung >= setup that: **13.3%**.

### 5 vi du THANG (chon dan deu theo thoi gian, khong chon dep)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2024-08-11 22:22 | 2024-08-12 05:22 | A | SELL | 2471.2 (VAH_Y) | 2471.1 | 2472.5 | 2468.0 | TP | 2.07 |
| 2024-12-27 09:47 | 2024-12-27 16:47 | EU | BUY | 2638.8 (VAL_Y) | 2639.3 | 2638.2 | 2644.4 | TP | 4.45 |
| 2025-07-10 12:52 | 2025-07-10 19:52 | US | BUY | 3332.0 (VAL_EU) | 3332.4 | 3331.0 | 3336.4 | TP | 2.71 |
| 2025-11-20 00:08 | 2025-11-20 07:08 | A | SELL | 4108.0 (VAH_Y) | 4106.9 | 4110.1 | 4074.4 | TP | 10.09 |
| 2026-08-07 01:12 | 2026-08-07 08:12 | A | BUY | 4299.2 (VAL_Y) | 4300.5 | 4297.5 | 4325.6 | TP | 8.30 |

### 5 vi du THUA (dan deu theo thoi gian)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2024-08-02 02:19 | 2024-08-02 09:19 | A | SELL | 2498.0 (VAH_Y) | 2497.4 | 2500.8 | 2490.0 | SL | -1.06 |
| 2025-02-17 03:18 | 2025-02-17 10:18 | A | BUY | 2912.4 (VAL_Y) | 2912.7 | 2911.6 | 2960.0 | SL | -1.18 |
| 2025-07-16 04:53 | 2025-07-16 11:53 | A | BUY | 3344.0 (VAL_Y) | 3344.1 | 3343.1 | 3369.6 | SL | -1.20 |
| 2026-01-19 16:33 | 2026-01-19 23:33 | US | SELL | 4676.8 (VAH_EU) | 4676.1 | 4677.5 | 4670.0 | SL | -1.14 |
| 2026-08-17 23:17 | 2026-08-18 06:17 | A | SELL | 4473.6 (VAH_Y) | 4473.0 | 4475.9 | 4453.6 | SL | -1.07 |

## 7. 2 nam, o khoi diem, TP co dinh 2R

Tham so: {'pen_ticks': 2, 'min_width': 6.0, 'tp_mode': 'fixed2'}. So phien sach (khong splice/thin, >=300 nen): **492**.

Lenh da dong **785** (con mo 0); lenh/ngay **1.596** (tong 3 phase) = A 0.55 | EU 0.28 | US 0.76

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 785 | 32.5% | -0.13 | -0.27 | -103.9 | 14 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 33 | 39.4% | 0.05 | -0.14 | 1.6 | 3 |
| 2024-09 | 36 | 36.1% | -0.07 | 0.16 | -2.5 | 8 |
| 2024-10 | 34 | 41.2% | 0.09 | 0.19 | 3.2 | 5 |
| 2024-11 | 33 | 33.3% | -0.14 | -0.18 | -4.5 | 5 |
| 2024-12 | 35 | 25.7% | -0.37 | -0.72 | -13.0 | 5 |
| 2025-01 | 28 | 32.1% | -0.19 | -0.18 | -5.2 | 7 |
| 2025-02 | 35 | 34.3% | -0.10 | -0.40 | -3.6 | 7 |
| 2025-03 | 40 | 42.5% | 0.15 | 0.32 | 5.8 | 7 |
| 2025-04 | 35 | 31.4% | -0.14 | -0.24 | -4.9 | 4 |
| 2025-05 | 36 | 27.8% | -0.25 | -0.43 | -9.1 | 8 |
| 2025-06 | 44 | 22.7% | -0.42 | -0.65 | -18.6 | 7 |
| 2025-07 | 27 | 33.3% | -0.12 | -0.29 | -3.3 | 8 |
| 2025-08 | 39 | 35.9% | -0.05 | 0.08 | -2.0 | 6 |
| 2025-09 | 51 | 29.4% | -0.22 | -0.41 | -11.3 | 7 |
| 2025-10 | 28 | 17.9% | -0.54 | -1.79 | -15.2 | 11 |
| 2025-11 | 30 | 36.7% | 0.03 | 0.33 | 0.8 | 14 |
| 2025-12 | 31 | 32.3% | -0.12 | -0.35 | -3.8 | 5 |
| 2026-01 | 28 | 35.7% | -0.00 | 0.01 | -0.1 | 8 |
| 2026-02 | 14 | 28.6% | -0.22 | -0.51 | -3.0 | 4 |
| 2026-03 | 28 | 35.7% | 0.01 | 0.16 | 0.2 | 6 |
| 2026-04 | 37 | 24.3% | -0.34 | -1.06 | -12.6 | 9 |
| 2026-05 | 24 | 33.3% | -0.07 | -0.09 | -1.8 | 5 |
| 2026-06 | 17 | 17.6% | -0.56 | -1.48 | -9.5 | 9 |
| 2026-07 | 26 | 53.8% | 0.53 | 1.06 | 13.8 | 3 |
| 2026-08 | 16 | 25.0% | -0.33 | -0.89 | -5.3 | 4 |

### Theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 272 | 36.8% | -0.02 | -0.05 | -4.3 | 11 |
| EU | 137 | 26.3% | -0.34 | -0.67 | -46.2 | 21 |
| US | 376 | 31.6% | -0.14 | -0.29 | -53.4 | 9 |

### Hai nua file 2 nam (cat 2025-08-01)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| H1 | 416 | 33.2% | -0.13 | -0.22 | -54.2 | 9 |
| H2 | 369 | 31.7% | -0.13 | -0.34 | -49.8 | 14 |

### Doi chung

Doi chung 60 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.19** (5-95%: -0.25 .. -0.11), WR doi chung 33.2%. Setup that: R TB **-0.13**, WR 32.5%. Ti le lan doi chung >= setup that: **11.7%**.

### 5 vi du THANG (chon dan deu theo thoi gian, khong chon dep)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2024-08-05 02:32 | 2024-08-05 09:32 | A | BUY | 2478.4 (VAL_Y) | 2479.1 | 2477.2 | 2482.9 | TP | 1.89 |
| 2025-01-13 11:09 | 2025-01-13 18:09 | EU | BUY | 2705.2 (VAL_Y) | 2705.3 | 2704.2 | 2707.5 | TP | 1.82 |
| 2025-06-18 14:11 | 2025-06-18 21:11 | US | SELL | 3405.2 (VAH_EU) | 3404.6 | 3407.2 | 3399.4 | TP | 1.92 |
| 2025-12-23 23:18 | 2025-12-24 06:18 | A | SELL | 4526.0 (VAH_Y) | 4524.9 | 4527.3 | 4520.1 | TP | 1.92 |
| 2026-08-17 02:32 | 2026-08-17 09:32 | A | SELL | 4454.4 (VAH_Y) | 4453.7 | 4456.1 | 4448.9 | TP | 1.92 |

### 5 vi du THUA (dan deu theo thoi gian)

| UTC | VN | phase | side | canh E (vung) | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2024-08-02 02:19 | 2024-08-02 09:19 | A | SELL | 2498.0 (VAH_Y) | 2497.4 | 2500.8 | 2490.6 | SL | -1.06 |
| 2025-02-05 15:26 | 2025-02-05 22:26 | US | SELL | 2897.6 (VAH_EU) | 2897.2 | 2899.7 | 2892.2 | SL | -1.08 |
| 2025-07-08 13:14 | 2025-07-08 20:14 | US | BUY | 3329.6 (VAL_EU) | 3331.6 | 3328.4 | 3338.0 | SL | -1.06 |
| 2025-12-19 02:07 | 2025-12-19 09:07 | A | BUY | 4352.8 (VAL_Y) | 4353.2 | 4350.9 | 4357.8 | SL | -1.09 |
| 2026-08-18 13:10 | 2026-08-18 20:10 | US | BUY | 4445.2 (VAL_EU) | 4447.5 | 4443.8 | 4454.9 | SL | -1.05 |

## 8. Luoi 3x3 tren 2 nam (H1 = 2024-08..2025-07, H2 = 2025-08..2026-08)

### TP canh/POC >= 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n H1 | R TB H1 | n H2 | R TB H2 | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 680 | 19.0% | -0.06 | 374 | -0.05 | 306 | -0.08 | -0.14 |
| 1 | 6 | 654 | 18.5% | -0.06 | 350 | -0.05 | 304 | -0.07 | -0.14 |
| 1 | 8 | 617 | 18.3% | -0.04 | 320 | -0.01 | 297 | -0.07 | -0.13 |
| 2 | 4 | 607 | 19.6% | -0.03 | 318 | -0.04 | 289 | -0.02 | -0.07 |
| 2 (o khoi diem) | 6 | 587 | 19.3% | -0.03 | 300 | -0.04 | 287 | -0.01 | -0.07 |
| 2 | 8 | 559 | 18.8% | -0.02 | 279 | -0.03 | 280 | -0.01 | -0.07 |
| 4 | 4 | 466 | 16.7% | -0.21 | 230 | -0.24 | 236 | -0.18 | -0.40 |
| 4 | 6 | 457 | 16.4% | -0.21 | 222 | -0.25 | 235 | -0.17 | -0.40 |
| 4 | 8 | 437 | 16.2% | -0.19 | 206 | -0.22 | 231 | -0.17 | -0.39 |

### TP co dinh 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n H1 | R TB H1 | n H2 | R TB H2 | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 928 | 31.9% | -0.16 | 529 | -0.16 | 399 | -0.16 | -0.33 |
| 1 | 6 | 860 | 32.0% | -0.15 | 468 | -0.16 | 392 | -0.15 | -0.31 |
| 1 | 8 | 773 | 32.5% | -0.14 | 399 | -0.13 | 374 | -0.14 | -0.30 |
| 2 | 4 | 849 | 32.5% | -0.13 | 474 | -0.13 | 375 | -0.14 | -0.29 |
| 2 (o khoi diem) | 6 | 785 | 32.5% | -0.13 | 416 | -0.13 | 369 | -0.13 | -0.27 |
| 2 | 8 | 714 | 32.8% | -0.12 | 361 | -0.11 | 353 | -0.13 | -0.26 |
| 4 | 4 | 676 | 30.3% | -0.19 | 363 | -0.17 | 313 | -0.21 | -0.41 |
| 4 | 6 | 624 | 30.4% | -0.18 | 318 | -0.17 | 306 | -0.20 | -0.39 |
| 4 | 8 | 566 | 30.7% | -0.17 | 272 | -0.15 | 294 | -0.19 | -0.38 |

### Phu luc luoi 2 nam: rong >= 12/16/20/30 (xuyen 2 tick)

#### TP canh/POC >= 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n H1 | R TB H1 | n H2 | R TB H2 | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 12 | 460 | 17.4% | -0.02 | 205 | -0.05 | 255 | -0.00 | -0.10 |
| 2 | 16 | 363 | 13.8% | -0.16 | 141 | -0.37 | 222 | -0.03 | -0.32 |
| 2 | 20 | 300 | 11.0% | -0.27 | 106 | -0.52 | 194 | -0.12 | -0.56 |
| 2 | 30 | 166 | 9.6% | -0.14 | 48 | -0.00 | 118 | -0.20 | -0.29 |

#### TP co dinh 2R

| xuyen (tick) | rong range >= | n tong | WR | R TB | n H1 | R TB H1 | n H2 | R TB H2 | ky vong gia/lenh |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 12 | 546 | 32.6% | -0.13 | 249 | -0.15 | 297 | -0.10 | -0.29 |
| 2 | 16 | 414 | 31.9% | -0.14 | 166 | -0.19 | 248 | -0.12 | -0.33 |
| 2 | 20 | 329 | 31.0% | -0.17 | 117 | -0.18 | 212 | -0.16 | -0.38 |
| 2 | 30 | 183 | 35.0% | -0.04 | 52 | -0.08 | 131 | -0.02 | -0.01 |

## 9. Delta manh + bien the tren 2 nam (o khoi diem)

TP poc:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| co ban | 587 | 19.3% | -0.03 | -0.07 | -16.9 | 29 |
|   co ban H1 | 300 | 19.7% | -0.04 | -0.06 | -12.6 | 19 |
|   co ban H2 | 287 | 18.8% | -0.01 | -0.08 | -4.3 | 29 |
| delta manh | 430 | 16.0% | -0.12 | -0.20 | -53.0 | 27 |
|   delta manh H1 | 226 | 15.9% | -0.22 | -0.24 | -50.0 | 24 |
|   delta manh H2 | 204 | 16.2% | -0.02 | -0.16 | -3.1 | 27 |
| V1 confirm | 427 | 19.0% | -0.08 | -0.11 | -34.1 | 29 |
|   V1 confirm H1 | 212 | 18.4% | -0.11 | -0.11 | -22.8 | 24 |
|   V1 confirm H2 | 215 | 19.5% | -0.05 | -0.10 | -11.3 | 29 |
| V2 cham thu 2+ | 545 | 17.6% | -0.10 | -0.12 | -53.2 | 36 |
|   V2 cham thu 2+ H1 | 276 | 17.8% | -0.15 | -0.14 | -41.1 | 27 |
|   V2 cham thu 2+ H2 | 269 | 17.5% | -0.04 | -0.09 | -12.0 | 36 |

TP fixed2:

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| co ban | 785 | 32.5% | -0.13 | -0.27 | -103.9 | 14 |
|   co ban H1 | 416 | 33.2% | -0.13 | -0.22 | -54.2 | 9 |
|   co ban H2 | 369 | 31.7% | -0.13 | -0.34 | -49.8 | 14 |
| delta manh | 607 | 30.8% | -0.18 | -0.38 | -110.6 | 16 |
|   delta manh H1 | 328 | 31.1% | -0.19 | -0.27 | -62.2 | 13 |
|   delta manh H2 | 279 | 30.5% | -0.17 | -0.50 | -48.5 | 12 |
| V1 confirm | 608 | 33.4% | -0.10 | -0.19 | -59.7 | 13 |
|   V1 confirm H1 | 328 | 32.0% | -0.15 | -0.30 | -49.8 | 13 |
|   V1 confirm H2 | 280 | 35.0% | -0.04 | -0.05 | -9.9 | 10 |
| V2 cham thu 2+ | 711 | 31.8% | -0.16 | -0.28 | -111.1 | 13 |
|   V2 cham thu 2+ H1 | 370 | 32.2% | -0.16 | -0.25 | -61.0 | 11 |
|   V2 cham thu 2+ H2 | 341 | 31.4% | -0.15 | -0.30 | -50.1 | 13 |

# Danh gia trung thuc (viet tay sau khi doc so; script chen nguyen van file nay khi chay lai)

1. **Co loi the that khong?** Khong. Sau chi phi 0,2 gia: o khoi diem (xuyen 2 tick, rong 6) file 90d = **-0,43R** (TP canh/POC) va **-0,26R** (TP co dinh 2R); n TEST = 45 / 58 (>= 30 nen ket luan duoc: am, WR TEST 20% / 31%). File 2 nam = **-0,03R** / **-0,13R** (n 587 / 785), hai nua gan nhu giong het nhau (H1 -0,04/-0,01; fixed2 -0,13/-0,13) => am nhe deu, khong phai may rui. WR chi 12-19% (TP xa) hoac 27-33% (2R, hoa von sau chi phi ~36%): xa muc tieu 60-70%.
2. **O nao ben ca hai nua?** Khong o nao duong o ca hai nua. Chi co 2 o TEST >= 0 va ca hai deu hong: (xuyen 1, TP poc) TEST +0,02 nhung TRAIN -0,69; (rong >= 30, fixed2) TEST +0,07 nhung n = 21 (< 30, chua ket luan) va 2 nam van -0,04. Cot "rong range 4/6/8" **khong chan lenh nao o file 90d** (VA hom qua luon >= 10 gia) nen luoi 3x3 thuc chat chi con 1 chieu (xuyen). Xuyen 4 tick te hon xuyen 2 tick o 2 nam (-0,21 vs -0,03) => xuyen sau hon KHONG phai tin hieu tot hon.
3. **Doi chung:** 2 nam: setup that (-0,03R / -0,13R) tot hon nen ngau nhien cung vung-che do-chieu (-0,17R / -0,19R) o ~87% so lan, nghia la 'phao hut + delta' them duoc ~0,06-0,14R nhung van chua vuot 0. File 90d: doi chung nhieu (khoang 5-95% rong -0,44..+0,62) nen khong phan biet duoc.
4. **Tan suat:** 90d: 1,7 (TP poc) - 2,0 (fixed2) lenh/ngay, rieng US 0,66-0,85. 2 nam: 1,2-1,6/ngay. Rieng C khong the dat 10-20 lenh/ngay.
5. **Theo phase:** 2 nam fixed2: A -0,02R (n 272, WR 36,8%, gan hoa von), EU -0,34R (te nhat), US -0,14R. Nhung 90d A = -0,23R => khong ben, khong dung de loc. Thang 8/2026 (xu huong tang manh 4400->4580): 0/30 lenh thang o TP poc, chuoi thua 36 => fade canh VA hom qua chet khi ngay co xu huong ma M5 chua kip 'dong ngoai'.
6. **Delta nen manh (|delta| >= trung vi 50 nen):** khong cai thien, thuong te hon: 90d n 103 -> 83, WR 12,6% -> 12,0% (TEST 20% -> 14%); fixed2 WR 27,3% -> 23,7%; 2 nam WR 19,3% -> 16,0%, 32,5% -> 30,8%. Delta lon o nen pha hut khong bao dam nguoc chieu thanh cong (co the la nen bi hap thu khong thanh cong, hoac chinh la dong lenh tiep dien).
7. **Hai bien the (vong 2):** V1 (doi them 1 nen M1 dong lai trong range): n giam ~30%, R TB nhich len (2 nam -0,08 / -0,10, H2 fixed2 -0,04) nhung van am o ca hai nua va 90d -0,19 / -0,28. V2 (chi lan cham thu 2+): khong tot hon co ban (2 nam -0,10 / -0,16). Khong bien the nao dung duoc.
8. **Ket luan / de xuat:** theo QD-5 (kỳ vọng am ca hai nua) C **nen tat mac dinh**. Hai huong sua co co che (CHUA do, chi la gia thuyet): (a) 'can bang' hien chi dua vao nen M5 chua dong ngoai; can them dieu kien ngay khong co xu huong (vd gia o cung phia voi VWAP tuan va VWAP ngay dang phang) vi cac ngay thua nang la ngay xu huong; (b) khong dung VA hom qua lam range cho phase A/EU, chi fade canh VA Au/IB trong phase US (US 2 nam fixed2 van -0,14R nen cung chua du). Ca hai phai do lai truoc khi tin.
