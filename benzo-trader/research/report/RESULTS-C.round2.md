# VONG 2 - Setup C: hop luu (V3) va ngay khong xu huong (V4)

Cung seed (doi chung seed 1000+k), cung o khoi diem (xuyen 2 tick, rong >= 6). V3 = chi fade canh E khi trong ban kinh 0,7 gia quanh E co them >= 1 vung khac (VWAP ngay/tuan, POC/VAH/VAL hom qua, POC/VAH/VAL Au, IB, HVN ngay/tuan, naked POC; vung trung gia E bi bo). V4 = V3 + |VWAP ngay - VWAP tuan| <= 2u (u = trung vi bien do 50 nen) va close nen vao nam trong VA hom qua. Doi chung 4 lan (90d) / 3 lan (2 nam).

## V3 hop luu, TP canh/POC >= 2R

### File 90d

Lenh/ngay: **0.164** (A 0.05 | EU 0.00 | US 0.11)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 10 | 10.0% | -0.62 | -1.08 | -6.2 | 6 |
| TRAIN | 8 | 12.5% | -0.51 | -0.70 | -4.1 | 6 |
| TEST | 2 | 0.0% | -1.09 | -2.60 | -2.2 | 2 |
| rieng phase US | 7 | 14.3% | -0.41 | -0.79 | -2.8 | 4 |
| US TRAIN | 6 | 16.7% | -0.30 | -0.40 | -1.8 | 4 |
| US TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 93 | 12.9% | -0.41 | -0.96 | -38.4 | 30 |
| nconf = 2 | 10 | 10.0% | -0.62 | -1.08 | -6.2 | 6 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

Doi chung 4 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.09** (5-95%: -1.01 .. 2.10), WR doi chung 12.9%. Setup that: R TB **-0.62**, WR 10.0%. Ti le lan doi chung >= setup that: **75.0%**.

### File 2 nam

Lenh/ngay: **0.203** (A 0.07 | EU 0.04 | US 0.10)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 100 | 18.0% | 0.15 | 0.51 | 15.0 | 21 |
| H1 | 57 | 15.8% | -0.18 | -0.22 | -10.3 | 11 |
| H2 | 43 | 20.9% | 0.59 | 1.48 | 25.3 | 21 |
| rieng phase US | 47 | 21.3% | -0.16 | -0.07 | -7.5 | 8 |
| US H1 | 24 | 20.8% | -0.32 | -0.41 | -7.6 | 7 |
| US H2 | 23 | 21.7% | 0.00 | 0.28 | 0.1 | 8 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 502 | 19.3% | -0.04 | -0.11 | -19.6 | 24 |
| nconf = 2 | 85 | 18.8% | 0.22 | 0.62 | 18.8 | 17 |
| nconf >= 3 | 15 | 13.3% | -0.25 | -0.11 | -3.8 | 5 |

Doi chung 3 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.20** (5-95%: -0.45 .. -0.04), WR doi chung 17.1%. Setup that: R TB **0.15**, WR 18.0%. Ti le lan doi chung >= setup that: **0.0%**.

## V3 hop luu, TP co dinh 2R

### File 90d

Lenh/ngay: **0.180** (A 0.05 | EU 0.00 | US 0.13)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 11 | 18.2% | -0.55 | -0.98 | -6.1 | 5 |
| TRAIN | 8 | 25.0% | -0.35 | -0.26 | -2.8 | 5 |
| TEST | 3 | 0.0% | -1.08 | -2.90 | -3.2 | 3 |
| rieng phase US | 8 | 25.0% | -0.33 | -0.69 | -2.7 | 3 |
| US TRAIN | 6 | 33.3% | -0.09 | 0.18 | -0.5 | 3 |
| US TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 110 | 28.2% | -0.23 | -0.50 | -25.2 | 10 |
| nconf = 2 | 11 | 18.2% | -0.55 | -0.98 | -6.1 | 5 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

Doi chung 4 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.33** (5-95%: -0.99 .. 0.40), WR doi chung 26.4%. Setup that: R TB **-0.55**, WR 18.2%. Ti le lan doi chung >= setup that: **75.0%**.

### File 2 nam

Lenh/ngay: **0.289** (A 0.08 | EU 0.04 | US 0.17)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 142 | 26.8% | -0.31 | -0.62 | -44.5 | 10 |
| H1 | 82 | 25.6% | -0.36 | -0.61 | -29.8 | 10 |
| H2 | 60 | 28.3% | -0.25 | -0.64 | -14.8 | 10 |
| rieng phase US | 82 | 25.6% | -0.33 | -0.71 | -27.4 | 11 |
| US H1 | 46 | 28.3% | -0.27 | -0.46 | -12.3 | 7 |
| US H2 | 36 | 22.2% | -0.42 | -1.03 | -15.1 | 11 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 664 | 33.6% | -0.10 | -0.20 | -64.7 | 12 |
| nconf = 2 | 116 | 25.9% | -0.34 | -0.67 | -39.8 | 9 |
| nconf >= 3 | 26 | 30.8% | -0.18 | -0.39 | -4.7 | 5 |

Doi chung 3 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.14** (5-95%: -0.25 .. -0.04), WR doi chung 34.4%. Setup that: R TB **-0.31**, WR 26.8%. Ti le lan doi chung >= setup that: **100.0%**.

## V4 = V3 + ngay khong xu huong, TP canh/POC >= 2R

### File 90d

Lenh/ngay: **0.049** (A 0.00 | EU 0.00 | US 0.05)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| TRAIN | 2 | 0.0% | -1.08 | -2.70 | -2.2 | 2 |
| TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| rieng phase US | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| US TRAIN | 2 | 0.0% | -1.08 | -2.70 | -2.2 | 2 |
| US TEST | 1 | 0.0% | -1.07 | -3.10 | -1.1 | 1 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 93 | 12.9% | -0.41 | -0.96 | -38.4 | 30 |
| nconf = 2 | 3 | 0.0% | -1.08 | -2.83 | -3.2 | 3 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

Doi chung 4 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.68** (5-95%: -1.10 .. 0.29), WR doi chung 12.5%. Setup that: R TB **-1.08**, WR 0.0%. Ti le lan doi chung >= setup that: **75.0%**.

### File 2 nam

Lenh/ngay: **0.041** (A 0.02 | EU 0.00 | US 0.02)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 20 | 10.0% | -0.38 | -0.95 | -7.6 | 12 |
| H1 | 10 | 20.0% | 0.32 | 1.04 | 3.2 | 5 |
| H2 | 10 | 0.0% | -1.08 | -2.93 | -10.8 | 10 |
| rieng phase US | 9 | 11.1% | -0.56 | -2.03 | -5.0 | 7 |
| US H1 | 3 | 33.3% | 0.46 | 0.33 | 1.4 | 1 |
| US H2 | 6 | 0.0% | -1.07 | -3.22 | -6.4 | 6 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 502 | 19.3% | -0.04 | -0.11 | -19.6 | 24 |
| nconf = 2 | 10 | 10.0% | -0.62 | -2.03 | -6.2 | 7 |
| nconf >= 3 | 10 | 10.0% | -0.14 | 0.14 | -1.4 | 6 |

Doi chung 3 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.33** (5-95%: -0.74 .. 1.69), WR doi chung 24.3%. Setup that: R TB **-0.38**, WR 10.0%. Ti le lan doi chung >= setup that: **66.7%**.

## V4 = V3 + ngay khong xu huong, TP co dinh 2R

### File 90d

Lenh/ngay: **0.066** (A 0.00 | EU 0.00 | US 0.07)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| TRAIN | 2 | 50.0% | 0.43 | 1.30 | 0.9 | 1 |
| TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| rieng phase US | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| US TRAIN | 2 | 50.0% | 0.43 | 1.30 | 0.9 | 1 |
| US TEST | 2 | 0.0% | -1.06 | -3.30 | -2.1 | 2 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 110 | 28.2% | -0.23 | -0.50 | -25.2 | 10 |
| nconf = 2 | 4 | 25.0% | -0.32 | -1.00 | -1.3 | 2 |
| nconf >= 3 | 0 | - | - | - | 0.0 | 0 |

Doi chung 4 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **0.17** (5-95%: -0.85 .. 0.84), WR doi chung 41.7%. Setup that: R TB **-0.32**, WR 25.0%. Ti le lan doi chung >= setup that: **75.0%**.

### File 2 nam

Lenh/ngay: **0.061** (A 0.02 | EU 0.00 | US 0.04)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 30 | 20.0% | -0.49 | -1.10 | -14.8 | 9 |
| H1 | 13 | 15.4% | -0.66 | -1.32 | -8.5 | 8 |
| H2 | 17 | 23.5% | -0.37 | -0.94 | -6.3 | 7 |
| rieng phase US | 19 | 15.8% | -0.62 | -1.41 | -11.7 | 8 |
| US H1 | 6 | 16.7% | -0.62 | -1.33 | -3.7 | 4 |
| US H2 | 13 | 15.4% | -0.61 | -1.45 | -7.9 | 7 |
| nconf = 1 (chi E, khong hop luu; lan chay khong loc) | 664 | 33.6% | -0.10 | -0.20 | -64.7 | 12 |
| nconf = 2 | 14 | 14.3% | -0.67 | -1.64 | -9.4 | 7 |
| nconf >= 3 | 16 | 25.0% | -0.34 | -0.62 | -5.5 | 5 |

Doi chung 3 lan (moi lan 1 nen ngau nhien / lenh that, cung vung-che do-chieu-R:R, SL = rau nen doi chung): R TB doi chung **-0.08** (5-95%: -0.22 .. 0.03), WR doi chung 35.9%. Setup that: R TB **-0.49**, WR 20.0%. Ti le lan doi chung >= setup that: **100.0%**.

## Ket luan vong 2

| o | n TEST 90d | R TB TEST 90d | R TB H1 2 nam | R TB H2 2 nam | du tieu chuan? |
|---|---|---|---|---|---|
| V3 hop luu, TP canh/POC >= 2R | 2 | -1.09 | -0.18 | 0.59 | khong |
| V3 hop luu, TP co dinh 2R | 3 | -1.08 | -0.36 | -0.25 | khong |
| V4 = V3 + ngay khong xu huong, TP canh/POC >= 2R | 1 | -1.07 | 0.32 | -1.08 | khong |
| V4 = V3 + ngay khong xu huong, TP co dinh 2R | 2 | -1.06 | -0.66 | -0.37 | khong |

**Khong o nao dat tieu chuan (n TEST >= 30 va duong o ca 90d-TEST lan hai nua 2 nam) => ket luan cuoi: C tat mac dinh.**
