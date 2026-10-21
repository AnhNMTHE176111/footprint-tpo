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

