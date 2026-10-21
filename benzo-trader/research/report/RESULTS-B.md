# RESULTS-B (VONG 2) - Setup B Hap thu tai VWAP tuan / ngay

Sinh boi `setup_b_hap_thu.py` (deterministic). Bang vong 1 giu nguyen o CUOI file de so sanh. Gio UTC (VN = UTC+7). R sau chi phi 0,2 gia/lenh; vao o close CF, mo phong tu nen ke tiep; cung nen SL+TP => SL; 1 lenh mo; toi da 2 lenh / (vung, phien).

**WR hoa von sau chi phi:** TP 2R ~ 33-34%, TP 3R ~ 26-27% (chi phi 0,2 gia / SL ~2,5 gia ~ 0,08R). **Phase A (05:00-12:30 VN) bao RIENG**, khong tron vao EU+US (phase A khong co che do nen bo loc TREND/pha VA khong ap dung).

Du lieu: 90d (61 phien sach; TRAIN 35 / TEST 26 phien) va 2 nam (nua 1 <= 2025-08-19: 248 phien sach; nua 2: 237 phien).

Cau hinh: **BASE** = dinh nghia vong 1 (than/|delta| giam dan RONG, cum N nen, theta); **H1** = BASE + bias (chi Z = VWAP ngay; BUY chi khi close nen vao > VWAP tuan, SELL chi khi < VWAP tuan); **H2** = thay "giam dan" bang "no luc co, ket qua khong" (cum K nen: tong |delta| cac nen cung chieu M >= |delta| nen lon nhat cua move, bien do cum <= 1,5u, cuc tri cum <= Z+0,5u, nen cuoi cum cham Z); **H1+H2**. Moi cau hinh chay TP 2R va 3R (H3). Luoi = theta {0,3; 0,5} x K (BASE/H1: N) {2,3,4}. O chinh = theta 0,5, K/N 3 (khong chon theo ket qua).

Ghi chu thiet ke H2 (minh bach): "tong |delta| cung chieu M" = tong |delta| cua cac nen trong cum co delta cung dau voi M; chi nen cuoi cum phai cham Z (bien do cum <= 1,5u va cuc tri <= Z+0,5u da giu cum sat Z).

## 0. Cac o DUONG o ca 90d-TEST lan hai nua 2 nam (R TB > 0)

4 / 96 o duong o ca 3 phep do. n o TEST 90d nho => **chi la ung vien, khong phai ket luan** (n TEST < 30 => chua ket luan).

| cau hinh | TP | phase | theta | K/N | 90d TRAIN n, R | 90d TEST n, R | 2y nua1 n, R | 2y nua2 n, R |
|---|---|---|---|---|---|---|---|---|
| BASE | 3R | A | 0.3 | 3 | 5, -0.30 | 7, 0.05 | 53, 0.23 | 35, 0.04 |
| BASE | 3R | A | 0.5 | 3 | 5, -0.30 | 3, 0.25 | 35, 0.35 | 23, 0.12 |
| H1 | 2R | EU+US | 0.5 | 2 | 0, - | 2, 0.44 | 41, 0.05 | 19, 0.33 |
| H1 | 3R | EU+US | 0.3 | 2 | 2, -1.09 | 3, 0.27 | 63, 0.08 | 23, 0.48 |

## 1. Luoi theo cau hinh (moi o: `90d: TRAIN n,R | TEST n,R` va `2y: nua1 n,R | nua2 n,R`; R = R TB sau chi phi)

### BASE - dinh nghia vong 1 ("giam dan rong") - TP 2R - phase EU+US

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 3,-1.10 \| 6,-0.09<br>2y: 132,-0.08 \| 53,-0.13 | 90d: 5,0.11 \| 3,-0.07<br>2y: 76,-0.11 \| 30,-0.10 | 90d: 2,-1.10 \| 1,1.92<br>2y: 54,-0.18 \| 9,-0.76 |
| 0.5 | 90d: 0,- \| 4,-0.33<br>2y: 88,-0.13 \| 38,0.09 | 90d: 2,0.41 \| 1,-1.05<br>2y: 43,-0.01 \| 21,0.19 | 90d: 0,- \| 0,-<br>2y: 30,-0.42 \| 8,-0.72 |

### BASE - dinh nghia vong 1 ("giam dan rong") - TP 2R - phase A

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 16,-0.18 \| 9,-0.09<br>2y: 79,0.16 \| 75,-0.02 | 90d: 5,-0.50 \| 7,-0.24<br>2y: 53,0.11 \| 35,0.10 | 90d: 4,-0.33 \| 3,-1.11<br>2y: 30,-0.24 \| 15,-0.09 |
| 0.5 | 90d: 11,0.25 \| 6,0.41<br>2y: 58,0.17 \| 46,-0.18 | 90d: 5,-0.50 \| 3,-0.08<br>2y: 35,0.24 \| 23,0.08 | 90d: 2,0.43 \| 2,-1.12<br>2y: 19,0.28 \| 12,-0.34 |

### BASE - dinh nghia vong 1 ("giam dan rong") - TP 3R - phase EU+US

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 3,-1.10 \| 6,0.25<br>2y: 132,-0.12 \| 53,-0.11 | 90d: 5,0.51 \| 3,0.27<br>2y: 76,-0.19 \| 30,-0.03 | 90d: 2,-1.10 \| 1,-1.08<br>2y: 54,-0.09 \| 9,-1.10 |
| 0.5 | 90d: 0,- \| 4,-0.08<br>2y: 88,-0.30 \| 38,0.07 | 90d: 2,0.91 \| 1,-1.05<br>2y: 43,-0.10 \| 21,0.24 | 90d: 0,- \| 0,-<br>2y: 30,-0.32 \| 8,-1.09 |

### BASE - dinh nghia vong 1 ("giam dan rong") - TP 3R - phase A

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 16,-0.12 \| 9,-0.20<br>2y: 78,-0.00 \| 75,-0.03 | 90d: 5,-0.30 \| 7,0.05<br>2y: 53,0.23 \| 35,0.04 | 90d: 4,-0.08 \| 3,-1.11<br>2y: 30,-0.21 \| 15,-0.29 |
| 0.5 | 90d: 11,-0.02 \| 6,0.24<br>2y: 57,-0.00 \| 46,-0.40 | 90d: 5,-0.30 \| 3,0.25<br>2y: 35,0.35 \| 23,0.12 | 90d: 2,0.93 \| 2,-1.12<br>2y: 19,0.33 \| 12,-0.42 |

### H1 - BASE + bias (chi Z=VWAP ngay, huong theo VWAP tuan) - TP 2R - phase EU+US

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 2,-1.09 \| 3,-0.07<br>2y: 63,0.11 \| 23,0.35 | 90d: 1,1.90 \| 3,-0.07<br>2y: 41,-0.04 \| 12,-0.10 | 90d: 1,-1.08 \| 0,-<br>2y: 27,-0.35 \| 2,-1.10 |
| 0.5 | 90d: 0,- \| 2,0.44<br>2y: 41,0.05 \| 19,0.33 | 90d: 1,1.90 \| 1,-1.05<br>2y: 24,0.12 \| 10,0.11 | 90d: 0,- \| 0,-<br>2y: 15,-0.72 \| 2,-1.10 |

### H1 - BASE + bias (chi Z=VWAP ngay, huong theo VWAP tuan) - TP 2R - phase A

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 9,-0.44 \| 5,-0.50<br>2y: 43,0.06 \| 29,0.15 | 90d: 4,-0.32 \| 4,-1.08<br>2y: 22,0.10 \| 13,0.05 | 90d: 3,-0.07 \| 2,-1.10<br>2y: 14,-0.04 \| 5,0.72 |
| 0.5 | 90d: 4,-0.33 \| 3,-0.10<br>2y: 31,0.04 \| 15,-0.28 | 90d: 4,-0.32 \| 2,-1.09<br>2y: 13,-0.20 \| 10,0.09 | 90d: 2,0.43 \| 1,-1.11<br>2y: 9,0.55 \| 4,0.42 |

### H1 - BASE + bias (chi Z=VWAP ngay, huong theo VWAP tuan) - TP 3R - phase EU+US

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 2,-1.09 \| 3,0.27<br>2y: 63,0.08 \| 23,0.48 | 90d: 1,2.90 \| 3,0.27<br>2y: 41,-0.06 \| 12,-0.10 | 90d: 1,-1.08 \| 0,-<br>2y: 27,-0.24 \| 2,-1.10 |
| 0.5 | 90d: 0,- \| 2,0.94<br>2y: 41,-0.24 \| 19,0.38 | 90d: 1,2.90 \| 1,-1.05<br>2y: 24,-0.13 \| 10,0.11 | 90d: 0,- \| 0,-<br>2y: 15,-0.85 \| 2,-1.10 |

### H1 - BASE + bias (chi Z=VWAP ngay, huong theo VWAP tuan) - TP 3R - phase A

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 9,-0.66 \| 5,-0.30<br>2y: 43,0.09 \| 29,0.15 | 90d: 4,-0.07 \| 4,-1.08<br>2y: 22,0.15 \| 13,0.43 | 90d: 3,0.26 \| 2,-1.10<br>2y: 14,0.31 \| 5,1.32 |
| 0.5 | 90d: 4,-1.08 \| 3,0.23<br>2y: 31,0.04 \| 15,-0.55 | 90d: 4,-0.07 \| 2,-1.09<br>2y: 13,-0.20 \| 10,0.49 | 90d: 2,0.93 \| 1,-1.11<br>2y: 9,1.11 \| 4,0.92 |

### H2 - "no luc co, ket qua khong" (khong bias) - TP 2R - phase EU+US

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 4,-1.08 \| 4,-0.32<br>2y: 43,0.06 \| 53,-0.28 | 90d: 5,-1.07 \| 6,-0.58<br>2y: 40,-0.08 \| 43,-0.03 | 90d: 3,-0.08 \| 4,-1.08<br>2y: 27,-0.12 \| 28,0.09 |
| 0.5 | 90d: 3,-1.08 \| 4,-0.32<br>2y: 38,0.06 \| 49,-0.22 | 90d: 4,-1.07 \| 4,-1.08<br>2y: 30,-0.03 \| 38,-0.05 | 90d: 3,-0.08 \| 3,-1.08<br>2y: 21,0.03 \| 25,0.12 |

### H2 - "no luc co, ket qua khong" (khong bias) - TP 2R - phase A

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 5,-0.49 \| 4,-1.09<br>2y: 25,-0.04 \| 43,-0.12 | 90d: 2,-1.16 \| 4,-1.11<br>2y: 20,-0.38 \| 29,0.34 | 90d: 3,-0.13 \| 3,-1.10<br>2y: 12,0.12 \| 19,0.48 |
| 0.5 | 90d: 4,-0.33 \| 4,-1.09<br>2y: 19,-0.02 \| 36,-0.18 | 90d: 1,-1.12 \| 4,-1.11<br>2y: 15,-0.33 \| 26,0.39 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 11,0.23 \| 17,0.67 |

### H2 - "no luc co, ket qua khong" (khong bias) - TP 3R - phase EU+US

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 4,-1.08 \| 4,-0.07<br>2y: 42,-0.08 \| 52,-0.38 | 90d: 5,-1.07 \| 6,-0.41<br>2y: 40,-0.13 \| 43,-0.06 | 90d: 3,0.25 \| 4,-1.08<br>2y: 27,-0.23 \| 28,0.20 |
| 0.5 | 90d: 3,-1.08 \| 4,-0.07<br>2y: 37,-0.16 \| 48,-0.33 | 90d: 4,-1.07 \| 4,-1.08<br>2y: 30,-0.06 \| 38,-0.13 | 90d: 3,0.25 \| 3,-1.08<br>2y: 21,0.03 \| 25,0.20 |

### H2 - "no luc co, ket qua khong" (khong bias) - TP 3R - phase A

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 5,-0.29 \| 4,-1.09<br>2y: 25,-0.16 \| 43,-0.26 | 90d: 2,-1.16 \| 4,-1.11<br>2y: 20,-0.53 \| 29,0.69 | 90d: 3,0.21 \| 3,-1.10<br>2y: 12,-0.13 \| 19,0.79 |
| 0.5 | 90d: 4,-0.08 \| 4,-1.09<br>2y: 19,-0.28 \| 36,-0.43 | 90d: 1,-1.12 \| 4,-1.11<br>2y: 15,-0.60 \| 26,0.74 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 11,-0.04 \| 17,1.02 |

### H1+H2 - H2 + bias - TP 2R - phase EU+US

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 1,-1.09 \| 2,0.43<br>2y: 22,-0.04 \| 24,-0.33 | 90d: 2,-1.07 \| 5,-0.47<br>2y: 19,-0.03 \| 17,0.33 | 90d: 3,-0.08 \| 4,-1.08<br>2y: 10,0.06 \| 13,0.30 |
| 0.5 | 90d: 0,- \| 2,0.43<br>2y: 18,0.04 \| 23,-0.29 | 90d: 1,-1.07 \| 3,-1.08<br>2y: 14,-0.06 \| 14,0.42 | 90d: 3,-0.08 \| 3,-1.08<br>2y: 8,0.38 \| 12,0.17 |

### H1+H2 - H2 + bias - TP 2R - phase A

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 15,0.29 \| 16,0.03 | 90d: 1,-1.12 \| 3,-1.11<br>2y: 10,0.38 \| 12,0.40 | 90d: 1,-1.12 \| 1,-1.11<br>2y: 7,1.01 \| 8,0.77 |
| 0.5 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 10,0.38 \| 13,-0.17 | 90d: 1,-1.12 \| 3,-1.11<br>2y: 7,0.60 \| 10,0.69 | 90d: 1,-1.12 \| 1,-1.11<br>2y: 6,1.36 \| 7,1.03 |

### H1+H2 - H2 + bias - TP 3R - phase EU+US

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 1,-1.09 \| 2,0.93<br>2y: 22,-0.58 \| 24,-0.58 | 90d: 2,-1.07 \| 5,-0.27<br>2y: 19,-0.08 \| 17,0.09 | 90d: 3,0.25 \| 4,-1.08<br>2y: 10,0.06 \| 13,0.46 |
| 0.5 | 90d: 0,- \| 2,0.93<br>2y: 18,-0.68 \| 23,-0.56 | 90d: 1,-1.07 \| 3,-1.08<br>2y: 14,-0.27 \| 14,0.06 | 90d: 3,0.25 \| 3,-1.08<br>2y: 8,0.38 \| 12,0.25 |

### H1+H2 - H2 + bias - TP 3R - phase A

| theta \ K | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 15,0.22 \| 16,0.15 | 90d: 1,-1.12 \| 3,-1.11<br>2y: 10,0.08 \| 12,0.90 | 90d: 1,-1.12 \| 1,-1.11<br>2y: 7,0.58 \| 8,1.40 |
| 0.5 | 90d: 1,-1.12 \| 3,-1.10<br>2y: 10,0.08 \| 13,-0.17 | 90d: 1,-1.12 \| 3,-1.11<br>2y: 7,0.03 \| 10,1.29 | 90d: 1,-1.12 \| 1,-1.11<br>2y: 6,0.86 \| 7,1.75 |

## 2. O chinh (theta 0,5; K/N = 3): tong hop, lenh/ngay, ky vong, doi chung

Doi chung = rut 1 nen ngau nhien / lenh that, cung vung, che do, chieu, R:R; **200 lan tren 90d, 60 lan tren 2 nam**. "p" = ty le lan rut co R TB >= R TB that.

| cau hinh | TP | phase | 90d: n, WR, R TB, ky vong (gia/lenh) | 90d doi chung R TB (sd), p | 2y: n, WR, R TB, ky vong | 2y lenh/ngay | 2y doi chung R TB (sd), p |
|---|---|---|---|---|---|---|---|
| BASE | 2R | EU+US | 3, 33.3%, -0.08, -0.87 | -0.14 (1.02), p=41.2% | 64, 39.1%, 0.06, -0.05 | 0.13 | -0.20 (0.17), p=8.3% |
| BASE | 2R | A | 8, 25.0%, -0.34, -0.55 | -0.20 (0.51), p=59.5% | 58, 43.1%, 0.17, 0.31 | 0.12 | -0.22 (0.20), p=3.3% |
| BASE | 3R | EU+US | 3, 33.3%, 0.26, -0.17 | -0.03 (1.23), p=36.2% | 64, 28.1%, 0.01, -0.06 | 0.13 | -0.22 (0.19), p=10.0% |
| BASE | 3R | A | 8, 25.0%, -0.09, 0.16 | -0.17 (0.65), p=40.0% | 58, 34.5%, 0.26, 0.30 | 0.12 | -0.23 (0.24), p=1.7% |
| H1 | 2R | EU+US | 2, 50.0%, 0.43, -0.00 | - | 34, 41.2%, 0.12, 0.05 | 0.07 | -0.22 (0.26), p=5.0% |
| H1 | 2R | A | 6, 16.7%, -0.58, -1.65 | -0.12 (0.65), p=74.0% | 23, 34.8%, -0.07, -0.21 | 0.05 | -0.22 (0.32), p=35.0% |
| H1 | 3R | EU+US | 2, 50.0%, 0.93, 1.05 | - | 34, 26.5%, -0.06, -0.20 | 0.07 | -0.27 (0.32), p=25.0% |
| H1 | 3R | A | 6, 16.7%, -0.41, -1.27 | -0.12 (0.78), p=61.0% | 23, 30.4%, 0.10, 0.08 | 0.05 | -0.24 (0.42), p=21.7% |
| H2 | 2R | EU+US | 8, 0.0%, -1.07, -3.06 | -0.22 (0.53), p=89.5% | 68, 35.3%, -0.04, -0.07 | 0.14 | -0.20 (0.17), p=13.3% |
| H2 | 2R | A | 5, 0.0%, -1.11, -2.06 | -0.13 (0.69), p=92.5% | 41, 41.5%, 0.13, 0.20 | 0.08 | -0.22 (0.25), p=8.3% |
| H2 | 3R | EU+US | 8, 0.0%, -1.07, -3.06 | -0.29 (0.57), p=80.5% | 68, 25.0%, -0.10, -0.23 | 0.14 | -0.22 (0.22), p=28.3% |
| H2 | 3R | A | 5, 0.0%, -1.11, -2.06 | -0.12 (0.89), p=88.0% | 41, 34.1%, 0.25, 0.44 | 0.08 | -0.26 (0.27), p=6.7% |
| H1+H2 | 2R | EU+US | 4, 0.0%, -1.08, -3.00 | -0.25 (0.90), p=68.0% | 28, 42.9%, 0.18, 0.50 | 0.06 | -0.17 (0.28), p=16.7% |
| H1+H2 | 2R | A | 4, 0.0%, -1.11, -1.98 | -0.04 (0.81), p=91.5% | 17, 58.8%, 0.65, 0.95 | 0.04 | -0.28 (0.38), p=0.0% |
| H1+H2 | 3R | EU+US | 4, 0.0%, -1.08, -3.00 | -0.24 (1.13), p=58.5% | 28, 25.0%, -0.11, -0.18 | 0.06 | -0.16 (0.32), p=41.7% |
| H1+H2 | 3R | A | 4, 0.0%, -1.11, -1.98 | -0.07 (0.94), p=88.0% | 17, 47.1%, 0.77, 1.34 | 0.04 | -0.29 (0.48), p=3.3% |

Lenh/ngay 90d o chinh (TP 3R): BASE EU+US = 0.05; BASE A = 0.13; H1 EU+US = 0.03; H1 A = 0.10; H2 EU+US = 0.13; H2 A = 0.08; H1+H2 EU+US = 0.07; H1+H2 A = 0.07

## 3. Tach BUY / SELL (o chinh, EU+US)

| cau hinh | TP | huong | 90d n, WR, R TB | 2y nua1 n, R | 2y nua2 n, R |
|---|---|---|---|---|---|
| BASE | 2R | BUY | 1, 0.0%, -1.08 | 21, -0.28 | 8, 0.40 |
| BASE | 2R | SELL | 2, 50.0%, 0.43 | 22, 0.25 | 13, 0.06 |
| BASE | 3R | BUY | 1, 0.0%, -1.08 | 21, -0.18 | 8, 0.40 |
| BASE | 3R | SELL | 2, 50.0%, 0.93 | 22, -0.03 | 13, 0.14 |
| H1 | 2R | BUY | 0, -, - | 14, -0.07 | 5, 0.11 |
| H1 | 2R | SELL | 2, 50.0%, 0.43 | 10, 0.38 | 5, 0.10 |
| H1 | 3R | BUY | 0, -, - | 14, 0.01 | 5, -0.29 |
| H1 | 3R | SELL | 2, 50.0%, 0.93 | 10, -0.32 | 5, 0.50 |
| H2 | 2R | BUY | 4, 0.0%, -1.07 | 10, -0.23 | 18, -0.08 |
| H2 | 2R | SELL | 4, 0.0%, -1.08 | 20, 0.07 | 20, -0.03 |
| H2 | 3R | BUY | 4, 0.0%, -1.07 | 10, -0.33 | 18, -0.19 |
| H2 | 3R | SELL | 4, 0.0%, -1.08 | 20, 0.07 | 20, -0.08 |
| H1+H2 | 2R | BUY | 0, -, - | 7, -0.29 | 4, 0.44 |
| H1+H2 | 2R | SELL | 4, 0.0%, -1.08 | 7, 0.17 | 10, 0.41 |
| H1+H2 | 3R | BUY | 0, -, - | 7, -0.00 | 4, -0.06 |
| H1+H2 | 3R | SELL | 4, 0.0%, -1.08 | 7, -0.54 | 10, 0.11 |

## 4. Phieu loc cua H2 o chinh (theta 0,5, K=3, TP 3R, moi phase; so ung vien con lai sau tung dieu kien)

| buoc | 90d | 2 nam | 90d (H1+H2) | 2 nam (H1+H2) |
|---|---|---|---|---|
| 1 CF dung (than>=50%, delta cung chieu) + cum hop le + nen cuoi cum cham Z | 3279 | 42756 | 2114 | 30153 |
| 2 + bien do cum <= 1,5u | 857 | 11810 | 534 | 8376 |
| 3 + cuc tri cum <= Z + 0,5u | 403 | 5406 | 250 | 3850 |
| 4 + khong TREND cung chieu / pha VA-IB / nen lon nhat phien <=3 nen | 378 | 5143 | 240 | 3698 |
| 4b + bias: BUY tren / SELL duoi VWAP tuan | 0 | 0 | 161 | 2245 |
| 5 + move >= 3 gia | 236 | 1870 | 96 | 744 |
| 6 + no luc cum >= |delta| lon nhat cua move | 35 | 292 | 14 | 122 |
| 7 + |delta_CF| >= theta*max | 23 | 162 | 10 | 66 |
| 8 + risk() hop le (SL<=4 gia) | 17 | 130 | 8 | 46 |

(Dem cong ca hai vung va hai chieu M, chua gom one-at-a-time va tran 2 lenh/vung/phien. Dong 1-4b dem nen; dong 5-8 dem ung vien duyet tuan tu.)

(Thoi gian chay: 257 giay.)


## Danh gia trung thuc (vong 2)

**Ket luan: khong o nao duong o CA 90d-TEST lan hai nua 2 nam voi n du de tin. Nen TAT B mac dinh.**

1. **90d van la nut that.** Moi cau hinh o chinh chi co 2-8 lenh/phase tren 65 phien (H2 EU+US 8 lenh, thua het 8/8; H2 A 5 lenh thua het; H1+H2 4 lenh thua het). Phieu loc H2 cho thay dieu kien giet n la **"no luc cum >= |delta| lon nhat cua move"**: 236 -> 35 ung vien (90d) va 1.870 -> 292 (2 nam), tuc 85% bi loai. Ba dieu kien tiep theo (bien do cum <= 1,5u: -74%; cuc tri <= Z+0,5u: -53%; move >= 3 gia: -38% (90d) .. -64% (2 nam)) cung rat gat. Bias H1 cat them ~40-55% so nen. Ket qua: lenh/ngay 90d chi 0,03-0,13 moi phase, con xa muc 10-20 lenh/ngay.
2. **4/96 o duong o ca 3 phep do** (muc 0), nhung n TEST 90d chi 2-7 lenh => khong co gia tri thong ke; 96 o x 3 phep do cung co kha nang 4 o la ngau nhien. Hai o BASE-A (theta 0,3/0,5, N=3, TP 3R) dang ghi nhan nhat: 2 nam nua1 +0,23/+0,35 (n=53/35), nua2 +0,04/+0,12 (n=35/23), nhung 90d TRAIN am (-0,30, n=5) va TEST n=3-7.
3. **H1 (bias VWAP tuan) khong giai quyet duoc:** o chinh 2 nam EU+US H1 3R: -0,06 (n=34) vs BASE 3R +0,01 (n=64): khong tot hon, va moi o giam ~45% n. Tach BUY/SELL khong thay thien lech on dinh (BUY 3R: nua1 +0,01, nua2 -0,29; SELL 3R: nua1 -0,32, nua2 +0,50 => dao chieu giua hai nua).
4. **H2 ("no luc co, ket qua khong") khong tot hon "giam dan":** 2 nam EU+US 3R: -0,10 (n=68) vs BASE +0,01 (n=64); K=3 theta 0,5 nua1 -0,06 / nua2 -0,13; o 90d thua het. Doi chung 2 nam co R TB -0,22 (sd 0,22), H2 EU+US 3R p=28% => khong khac doi chung. Phase A, H2 K=3-4 co nua2 rat duong (+0,7..+1,0) nhung nua1 am (-0,60..-0,04) => **khong ben** (dao theo nua thoi gian).
5. **H3 (TP 2R vs 3R):** WR cao hon nhieu o 2R (EU+US BASE 39% vs 28%) nhung ky vong gan nhu khong doi (0,06 vs 0,01; phase A 0,17 vs 0,26). Khong o nao ma 2R cuu duoc setup; TP khong phai van de.
6. **Phase A (rieng):** BASE phase A la ung vien duy nhat nhin duoc o 2 nam: n=58 (~0,12 lenh/ngay), 3R R TB +0,26, WR 34,5%, doi chung -0,23 (sd 0,24) p=1,7%. NHUNG bootstrap 95% [-0,22 ; +0,74] chua 0, bo 2 thang tot nhat (2024-10, 2025-07) con n=48, R TB -0,12, chi 9/20 thang duong; 90d A o chinh n=8, R -0,09. Phase A khong co che do (NA) nen TREND/pha VA khong loai duoc; chi la mau nho, chua nen coi la loi the.
7. **Tom lai:** hai nua sua (bias + "no luc co, ket qua khong") deu khong cai thien so voi vong 1; co che nghe dung (hap thu o nhip hoi) nhung dieu kien do duoc qua khat khe, chon tin hieu qua it de vuot nhieu thua ngau nhien. Doi chung (random cung vung/che do/chieu) lai co ky vong ~-0,2R nen B khong the chi dua vao "dat trong vung".

**De xuat:** theo QD-5 dat B **tat mac dinh** (van giu cong tac). Neu muon thu tiep, 3 huong da bi do va bac bo: giam dan, "no luc co ket qua khong", bias VWAP tuan. Huong chua do: (a) doi nen xac nhan CF bang test lai Z lan 2 co volume (V1 vong 1 khong thang), (b) gop B vao A/C nhu mot bo loc cuc tri thay vi setup doc lap, (c) chi phase A voi du lieu moi >= 3 thang truoc khi tin.


---

# VONG 1 (giu nguyen de so sanh)

# RESULTS-B - Setup B Hap thu tai VWAP tuan / ngay

Sinh boi `setup_b_hap_thu.py` (deterministic). Gio UTC (VN = UTC+7). R tinh sau chi phi 0,2 gia/lenh, TP 3R, vao o close nen xac nhan, mo phong tu nen ke tiep, cung nen SL+TP => SL, 1 lenh mo cung luc, toi da 2 lenh/(vung, phien).

**Mon bai doc truoc:** voi TP 3R va chi phi, WR hoa von xap xi 25-28% (xem doi chung). Muc tieu 60-70% WR o 3R khong the do bang setup nay neu doi chung da ~25%.

Du lieu chinh: file 90d (GCZ26), 86333 nen M1, 65 phien (61 phien sach dung de chia "lenh/ngay"). TRAIN <= 2026-09-15, TEST >= 2026-09-16.

## Luoi 3x3 - Z = VWAP tuan + VWAP ngay (90d)

Moi o: `n / WR / R TB` toan bo | `TRAIN n, R TB` | `TEST n, R TB`. Hang = nguong |delta_CF|/|delta| lon nhat (theta), cot = so nen cum giam dan (N).

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 33 / 24.2% / -0.13<br>TR 18, -0.23<br>TE 15, -0.02 | 20 / 30.0% / 0.11<br>TR 10, 0.10<br>TE 10, 0.11 | 10 / 10.0% / -0.69<br>TR 6, -0.42<br>TE 4, -1.10 |
| 0.5 | 21 / 28.6% / 0.04<br>TR 11, -0.02<br>TE 10, 0.11 | 11 / 27.3% / 0.00<br>TR 7, 0.04<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |
| 0.7 | 11 / 18.2% / -0.37<br>TR 5, -0.30<br>TE 6, -0.42 | 10 / 20.0% / -0.29<br>TR 6, -0.43<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |

## Luoi 3x3 - Z = chi VWAP tuan (90d)

Moi o: `n / WR / R TB` toan bo | `TRAIN n, R TB` | `TEST n, R TB`. Hang = nguong |delta_CF|/|delta| lon nhat (theta), cot = so nen cum giam dan (N).

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 8 / 12.5% / -0.60<br>TR 5, -0.30<br>TE 3, -1.11 | 7 / 42.9% / 0.60<br>TR 4, 0.91<br>TE 3, 0.20 | 2 / 0.0% / -1.12<br>TR 1, -1.12<br>TE 1, -1.11 |
| 0.5 | 5 / 20.0% / -0.31<br>TR 3, 0.24<br>TE 2, -1.13 | 3 / 33.3% / 0.24<br>TR 2, 0.91<br>TE 1, -1.11 | 1 / 0.0% / -1.11<br>TR 0, -<br>TE 1, -1.11 |
| 0.7 | 3 / 0.0% / -1.11<br>TR 2, -1.10<br>TE 1, -1.14 | 3 / 33.3% / 0.24<br>TR 2, 0.91<br>TE 1, -1.11 | 1 / 0.0% / -1.11<br>TR 0, -<br>TE 1, -1.11 |

## Luoi 3x3 - Z = chi VWAP ngay (90d)

Moi o: `n / WR / R TB` toan bo | `TRAIN n, R TB` | `TEST n, R TB`. Hang = nguong |delta_CF|/|delta| lon nhat (theta), cot = so nen cum giam dan (N).

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 28 / 25.0% / -0.11<br>TR 15, -0.32<br>TE 13, 0.14 | 15 / 26.7% / -0.02<br>TR 7, 0.05<br>TE 8, -0.07 | 9 / 11.1% / -0.64<br>TR 5, -0.28<br>TE 4, -1.10 |
| 0.5 | 18 / 27.8% / 0.01<br>TR 9, -0.23<br>TE 9, 0.25 | 10 / 30.0% / 0.11<br>TR 6, 0.23<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |
| 0.7 | 10 / 20.0% / -0.29<br>TR 4, -0.10<br>TE 6, -0.42 | 9 / 22.2% / -0.20<br>TR 5, -0.30<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |

## Dinh nghia DUNG CHU plan (than VA |delta| giam nghiem ngat tung nen) - 90d, ca hai vung

`n / R TB` (n < 30 => khong ket luan). Cac bang luoi o tren dung "giam dan RONG" (nen cuoi cum < nen dau cum, ca than lan |delta|) vi ban chu cho n ~ 0.

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 33 / -0.13 | 1 / -1.08 | 0 / - |
| 0.5 | 21 / 0.04 | 0 / - | 0 / - |
| 0.7 | 11 / -0.37 | 0 / - | 0 / - |

### Pheu loc o chinh (theta=0.5, N=3, ca hai vung, so ung vien con lai sau moi buoc; chua gom one-at-a-time / tran 2 lenh)

| buoc | giam dan RONG | giam dan NGHIEM NGAT (chu plan) |
|---|---|---|
| 1 CF dung + cum cham Z | 1528 | 1528 |
| 2 + than/delta giam dan | 498 | 76 |
| 3 + cuc tri <= Z+0,5 | 82 | 7 |
| 4 + khong TREND/pha VA/nen lon nhat | 78 | 6 |
| 5 + move >= 3 gia | 45 | 2 |
| 6 + |delta_CF| >= theta*max | 15 | 0 |
| 7 + risk() hop le (SL<=4 gia) | 13 | 0 |

## O chinh (theta=0.5, N=3; dung dinh nghia khoi diem trong plan - KHONG chon o tot nhat)

Lenh da dong **11** (con mo 0), lenh/ngay **0.17** (tren 65 phien sach).

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 11 | 27.3% | 0.00 | 0.07 | 0.0 | 4 |

### Lenh/ngay theo phase (A 05:00-12:30 / EU 12:30-19:00 / US 19:00-04:00 VN)

| phase | n | lenh/ngay | WR | R TB |
|---|---|---|---|---|
| A | 8 | 0.12 | 25.0% | -0.09 |
| EU | 2 | 0.03 | 0.0% | -1.07 |
| US | 1 | 0.02 | 100.0% | 2.90 |

So voi muc tieu 10-20 lenh/ngay: B cho **0.17 lenh/ngay** toan ngay (US rieng: 0.02).

### Theo thang

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-08 | 4 | 25.0% | -0.11 | -0.28 | -0.5 | 2 |
| 2026-09 | 6 | 16.7% | -0.41 | -1.35 | -2.5 | 4 |
| 2026-10 | 1 | 100.0% | 2.94 | 10.00 | 2.9 | 0 |

### TRAIN / TEST

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 7 | 28.6% | 0.04 | -0.03 | 0.3 | 3 |
| TEST | 4 | 25.0% | -0.07 | 0.25 | -0.3 | 3 |

### Tach theo vung (o chinh)

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VWAP tuan | 3 | 33.3% | 0.24 | 0.47 | 0.7 | 2 |
| VWAP tuan - TRAIN | 2 | 50.0% | 0.91 | 1.75 | 1.8 | 1 |
| VWAP tuan - TEST | 1 | 0.0% | -1.11 | -2.10 | -1.1 | 1 |
| VWAP ngay | 10 | 30.0% | 0.11 | 0.34 | 1.1 | 3 |
| VWAP ngay - TRAIN | 6 | 33.3% | 0.23 | 0.40 | 1.4 | 3 |
| VWAP ngay - TEST | 4 | 25.0% | -0.07 | 0.25 | -0.3 | 3 |

### Doi chung (200 lan rut; moi lan 1 nen ngau nhien / lenh that, cung vung, che do, chieu, R:R 3)

| | WR | R TB |
|---|---|---|
| Setup B (that) | 27.3% | 0.00 |
| Doi chung trung binh | 27.8% | 0.00 |
| Doi chung do lech chuan | 15.8 diem | 0.63 |
| Doi chung moc 5% / 95% (R TB) | - | -1.10 / 1.13 |
| Ty le lan rut co R TB >= that | - | 48.5% |

Doi chung tren toan ban TRAIN/TEST xem bang tach o duoi.

Doi chung rieng TEST (n that = 4): that WR 25.0%, R TB -0.07 | doi chung WR 28.0%, R TB 0.01 (100 lan rut).

### 5 vi du THANG + 5 vi du THUA (gio UTC / VN; Z = gia VWAP luc vao)

**THANG**

| UTC | VN | chieu | Z | vung | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-10 13:16 | 2026-08-10 20:16 | SELL | 4396.8 | VWAP_W | 4395.3 | 4397.4 | 4389.0 | TP | 2.90 |
| 2026-09-04 00:40 | 2026-09-04 07:40 | BUY | 4522.9 | VWAP_D | 4524.1 | 4521.8 | 4531.0 | TP | 2.91 |
| 2026-10-01 02:34 | 2026-10-01 09:34 | BUY | 4182.7 | VWAP_D | 4185.4 | 4182.0 | 4195.6 | TP | 2.94 |

**THUA**

| UTC | VN | chieu | Z | vung | entry | SL | TP | ket qua | R |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-04 03:33 | 2026-08-04 10:33 | BUY | 4111.3 | VWAP_D | 4113.6 | 4110.8 | 4122.0 | SL | -1.07 |
| 2026-08-18 23:55 | 2026-08-19 06:55 | SELL | 4387.2 | VWAP_D | 4385.3 | 4388.2 | 4376.6 | SL | -1.07 |
| 2026-09-01 23:00 | 2026-09-02 06:00 | SELL | 4375.9 | VWAP_D | 4373.6 | 4376.6 | 4364.6 | SL | -1.07 |
| 2026-09-16 02:05 | 2026-09-16 09:05 | SELL | 4326.9 | VWAP_D | 4325.4 | 4328.1 | 4317.3 | SL | -1.07 |
| 2026-09-25 07:26 | 2026-09-25 14:26 | SELL | 4310.6 | VWAP_D | 4307.5 | 4311.3 | 4296.1 | SL | -1.05 |

## Bien the cau truc (bao rieng, chi 90d)

### V1 "test lai": da co mot lan cham Z trong 40 nen truoc cum roi roi xa >= 2 gia, nay quay lai lan hai (hinh U/test lai truoc khi dao chieu).

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 27 / 18.5% / -0.37<br>TR 15, -0.32<br>TE 12, -0.42 | 14 / 28.6% / 0.05<br>TR 6, 0.24<br>TE 8, -0.09 | 8 / 12.5% / -0.59<br>TR 4, -0.08<br>TE 4, -1.10 |
| 0.5 | 16 / 18.8% / -0.35<br>TR 9, -0.22<br>TE 7, -0.52 | 8 / 25.0% / -0.09<br>TR 4, -0.11<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |
| 0.7 | 9 / 22.2% / -0.20<br>TR 4, -0.09<br>TE 5, -0.29 | 7 / 14.3% / -0.52<br>TR 3, -1.12<br>TE 4, -0.07 | 4 / 25.0% / -0.09<br>TR 2, 0.93<br>TE 2, -1.12 |

O chinh bien the: n=8, WR 25.0%, R TB -0.09, ky vong 0.04 gia, tong R -0.7 | doi chung cung vung/che do: WR 26.6%, R TB -0.05.

### V2 "o volume lon": trong cum, co o per-level (bid+ask) lon nhat trong +-1 gia quanh Z >= 2 x trung vi o-lon-nhat 50 nen (luong lon tai Z, dung nghia "bong bong tai vung").

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 4 / 25.0% / -0.08<br>TR 2, -1.11<br>TE 2, 0.94 | 4 / 0.0% / -1.07<br>TR 2, -1.07<br>TE 2, -1.06 | 2 / 0.0% / -1.11<br>TR 1, -1.09<br>TE 1, -1.12 |
| 0.5 | 3 / 33.3% / 0.25<br>TR 1, -1.12<br>TE 2, 0.94 | 2 / 0.0% / -1.06<br>TR 1, -1.07<br>TE 1, -1.05 | 1 / 0.0% / -1.12<br>TR 0, -<br>TE 1, -1.12 |
| 0.7 | 2 / 0.0% / -1.09<br>TR 1, -1.12<br>TE 1, -1.05 | 2 / 0.0% / -1.06<br>TR 1, -1.07<br>TE 1, -1.05 | 1 / 0.0% / -1.12<br>TR 0, -<br>TE 1, -1.12 |

O chinh bien the: n=2, WR 0.0%, R TB -1.06, ky vong -3.50 gia, tong R -2.1 | doi chung cung vung/che do: WR 23.7%, R TB -0.16.

## File 2 nam `fp_GC_XCEC_Time_20240801-20260819_748d9h` (loai splice +-2 phien va ca TUAN co cho noi; profile per-level that)

Nua 1 = phien <= 2025-08-19, nua 2 = sau do. "n phien" = phien sach (khong splice/thin/tuan-splice) cua moi nua; so lenh/ngay chia cho so do.

Phien sach: nua 1 = 248, nua 2 = 237 (tong 485 / 533 phien).

### Luoi 3x3 - Z = VWAP tuan + ngay (2 nam): `n / R TB nua1 | n / R TB nua2`

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 198, WR 25.3%, -0.12<br>126, WR 26.2%, -0.05 | 123, WR 29.3%, 0.04<br>65, WR 27.7%, 0.01 | 83, WR 25.3%, -0.12<br>24, WR 12.5%, -0.59 |
| 0.5 | 139, WR 23.0%, -0.20<br>84, WR 22.6%, -0.19 | 75, WR 32.0%, 0.15<br>44, WR 31.8%, 0.18 | 48, WR 27.1%, -0.05<br>20, WR 10.0%, -0.69 |
| 0.7 | 104, WR 20.2%, -0.31<br>51, WR 27.5%, 0.01 | 51, WR 31.4%, 0.13<br>33, WR 24.2%, -0.12 | 38, WR 26.3%, -0.07<br>15, WR 6.7%, -0.83 |

### Luoi 3x3 - chi VWAP tuan (2 nam): `n / R TB nua1 | n / R TB nua2`

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 84, WR 16.7%, -0.46<br>47, WR 23.4%, -0.16 | 45, WR 22.2%, -0.24<br>25, WR 28.0%, 0.02 | 33, WR 21.2%, -0.27<br>9, WR 0.0%, -1.10 |
| 0.5 | 57, WR 15.8%, -0.49<br>31, WR 22.6%, -0.19 | 26, WR 26.9%, -0.05<br>17, WR 29.4%, 0.08 | 19, WR 31.6%, 0.15<br>6, WR 0.0%, -1.09 |
| 0.7 | 44, WR 13.6%, -0.57<br>17, WR 23.5%, -0.15 | 17, WR 17.6%, -0.41<br>12, WR 25.0%, -0.10 | 13, WR 30.8%, 0.12<br>4, WR 0.0%, -1.10 |

### Luoi 3x3 - chi VWAP ngay (2 nam): `n / R TB nua1 | n / R TB nua2`

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 154, WR 27.3%, -0.04<br>92, WR 28.3%, 0.04 | 99, WR 31.3%, 0.12<br>48, WR 25.0%, -0.10 | 69, WR 24.6%, -0.15<br>16, WR 18.8%, -0.34 |
| 0.5 | 110, WR 24.5%, -0.14<br>63, WR 22.2%, -0.20 | 61, WR 32.8%, 0.18<br>33, WR 30.3%, 0.12 | 41, WR 24.4%, -0.15<br>15, WR 13.3%, -0.56 |
| 0.7 | 82, WR 22.0%, -0.25<br>40, WR 27.5%, 0.01 | 43, WR 32.6%, 0.18<br>25, WR 20.0%, -0.29 | 34, WR 23.5%, -0.19<br>11, WR 9.1%, -0.73 |

### O chinh 2 nam (theta=0.5, N=3)

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua | lenh/ngay |
|---|---|---|---|---|---|---|---|
| Nua 1 | 75 | 32.0% | 0.15 | 0.13 | 11.4 | 10 | 0.30 |
| Nua 2 | 44 | 31.8% | 0.18 | 0.24 | 7.8 | 7 | 0.19 |
| Ca 2 nam | 119 | 31.9% | 0.16 | 0.17 | 19.2 | 10 | 0.25 |

Theo phase (ca 2 nam): A n=58 R TB 0.26; EU n=37 R TB 0.07; US n=24 R TB 0.05

Doi chung 2 nam (20 lan rut, cung vung/che do/chieu): WR 24.4%, R TB -0.22 (do lech 0.19) | that WR 31.9%, R TB 0.16.

Theo thang (2 nam, o chinh):

| | n | WR | R TB | ky vong gia/lenh | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 7 | 0.0% | -1.10 | -2.24 | -7.7 | 7 |
| 2024-09 | 3 | 33.3% | 0.18 | 1.03 | 0.5 | 2 |
| 2024-10 | 12 | 58.3% | 1.19 | 1.83 | 14.3 | 2 |
| 2024-11 | 8 | 12.5% | -0.64 | -1.39 | -5.1 | 7 |
| 2024-12 | 8 | 37.5% | 0.38 | 0.92 | 3.0 | 4 |
| 2025-01 | 4 | 0.0% | -1.15 | -1.58 | -4.6 | 4 |
| 2025-02 | 4 | 25.0% | -0.13 | -0.43 | -0.5 | 3 |
| 2025-03 | 9 | 11.1% | -0.68 | -1.54 | -6.1 | 7 |
| 2025-04 | 2 | 0.0% | -1.14 | -1.75 | -2.3 | 2 |
| 2025-05 | 1 | 0.0% | -1.11 | -2.00 | -1.1 | 1 |
| 2025-06 | 4 | 75.0% | 1.90 | 3.42 | 7.6 | 1 |
| 2025-07 | 6 | 50.0% | 0.88 | 1.12 | 5.3 | 2 |
| 2025-08 | 11 | 54.5% | 1.07 | 1.65 | 11.8 | 3 |
| 2025-09 | 14 | 35.7% | 0.33 | -0.06 | 4.6 | 4 |
| 2025-10 | 4 | 25.0% | -0.10 | -0.12 | -0.4 | 3 |
| 2025-12 | 4 | 25.0% | -0.10 | 0.35 | -0.4 | 3 |
| 2026-01 | 3 | 0.0% | -1.07 | -3.03 | -3.2 | 3 |
| 2026-02 | 1 | 0.0% | -1.11 | -2.00 | -1.1 | 1 |
| 2026-03 | 1 | 100.0% | 2.89 | 5.50 | 2.9 | 0 |
| 2026-04 | 2 | 0.0% | -1.10 | -2.30 | -2.2 | 2 |
| 2026-05 | 6 | 16.7% | -0.42 | -0.68 | -2.5 | 4 |
| 2026-06 | 1 | 100.0% | 2.95 | 11.20 | 2.9 | 0 |
| 2026-07 | 2 | 100.0% | 2.90 | 6.55 | 5.8 | 0 |
| 2026-08 | 2 | 0.0% | -1.07 | -3.05 | -2.1 | 2 |

### Bien the V1 "test lai" tren 2 nam: `n, R TB nua1 | n, R TB nua2`

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 124, 25.0%, -0.12<br>103, 27.2%, -0.01 | 80, 30.0%, 0.07<br>48, 27.1%, -0.02 | 47, 27.7%, -0.02<br>17, 17.6%, -0.39 |
| 0.5 | 80, 23.8%, -0.17<br>69, 24.6%, -0.11 | 46, 28.3%, 0.01<br>34, 32.4%, 0.20 | 28, 28.6%, 0.03<br>14, 14.3%, -0.52 |
| 0.7 | 63, 22.2%, -0.23<br>44, 29.5%, 0.09 | 31, 25.8%, -0.09<br>24, 25.0%, -0.09 | 23, 21.7%, -0.24<br>10, 10.0%, -0.69 |

Do ben o chinh 2 nam: R TB 0.16, khoang tin cay bootstrap 95% [-0.17 ; 0.50]; WR hoa von xap xi 27.6% (3R, chi phi 0,2 gia).
Bo 2 thang tot nhat (2024-10, 2025-08): n=96, WR 26.0%, R TB -0.07.

### Bien the V2 "o volume lon" tren 2 nam: `n, WR, R TB nua1 | n, WR, R TB nua2`

| theta \ N | 2 | 3 | 4 |
|---|---|---|---|
| 0.3 | 60, 33.3%, 0.21<br>21, 19.0%, -0.34 | 47, 29.8%, 0.06<br>19, 21.1%, -0.27 | 31, 25.8%, -0.10<br>7, 14.3%, -0.53 |
| 0.5 | 43, 30.2%, 0.09<br>15, 13.3%, -0.57 | 32, 34.4%, 0.25<br>14, 21.4%, -0.25 | 22, 27.3%, -0.04<br>4, 0.0%, -1.10 |
| 0.7 | 31, 29.0%, 0.05<br>11, 18.2%, -0.37 | 20, 45.0%, 0.68<br>10, 10.0%, -0.69 | 16, 31.2%, 0.13<br>4, 0.0%, -1.10 |

(2 nam: 66 giay.)

(Tong thoi gian chay: 79 giay.)

## Danh gia trung thuc (vong 1)

**Ket luan ngan: CHUA co loi the, chua dat de dua vao indicator. B khong dat muc tieu WR 60-70% / 10-20 lenh/ngay (dang o ~30% WR va ~0,2 lenh/ngay).**

1. **n qua nho tren file chinh.** Ban chu plan (than va |delta| giam NGHIEM NGAT tung nen) cho n = 0 o o chinh (N=3) tren 90d; ban "giam rong" (nen cuoi cum < nen dau cum) cho n = 11 (0,17 lenh/ngay), TEST chi 4 lenh. Theo luat plan n < 30 o TEST => **khong ket luan duoc tren 90d.** Pheu loc cho thay 1.528 ung vien (CF dung + cum cham Z) con 13 lenh: mat nhieu nhat o buoc "giam dan" (-70%) va "khong cuc tri nao vuot Z+0,5" (-84%). Doi chung tren 90d: that 27,3% / R 0,00 vs doi chung 27,8% / 0,00 (200 lan rut, 48,5% lan rut >= that) => **khong khac doi chung.**
2. **File 2 nam (n du lon hon):** o chinh (theta 0,5; N 3) n=119, WR 31,9%, R TB +0,16, nua 1 +0,15 (n=75), nua 2 +0,18 (n=44); doi chung 20 lan rut: WR 24,4%, R TB -0,22. Thoat nhin thi *duong o ca hai nua* va hon doi chung ~0,4R. NHUNG: (a) khoang tin cay bootstrap 95% cua R TB la [-0,17 ; +0,50] **bao gom 0**; WR hoa von ~27,6% nen 31,9% chua vuot ro; (b) **bo 2 thang tot nhat (2024-10, 2025-08) thi n=96, WR 26,0%, R TB -0,07** => loi nhuan do 2 thang dan; (c) chuoi thua dai nhat 10; (d) doi chung do lech 0,19 nen khoang cach 0,38 ~ 2 do lech chuan, chi la goi y.
3. **O nao ben ca hai nua?** Chi co hang N=3 (theta 0,3/0,5; ca vung tuan+ngay) duong o hai nua 2 nam (theta 0,5: +0,15/+0,18; theta 0,3: +0,04/+0,01; theta 0,7: +0,13 / -0,12 => dut). **Hang xom xau**: N=2 am o 5/6 o (-0,04..-0,31 tru mot o +0,01), N=4 am o nua 2 (-0,59..-0,83, nhung n chi 15-24). Mot o duong ma hai ben deu am = dau hieu khop qua muc, **khong chon o N=3**; chi coi la "N=3 co the dang dung vi 3 nen la ngưỡng tu nhien cua cum", can du lieu moi de xac nhan. Theo vung: tren 2 nam, VWAP ngay (N3 theta .5: +0,18/+0,12) nhin ben hon VWAP tuan (-0,05/+0,08), nguoc voi phep do cu (tuan nhinh hon ngay) va n tuan chi 26+17.
4. **Theo phase (2 nam, o chinh):** A n=58 R +0,26; EU n=37 +0,07; US n=24 +0,05. Phase A (05:00-12:30 VN) dang gop nhieu nhat nhung o phase A chua co che do (NA) nen bo loc "TREND cung chieu / pha VA" khong ap dung duoc => day cung la phan thieu bo loc, khong phai bang chung tot.
5. **Bien the cau truc (90d + 2 nam):**
   - **V1 "test lai" (da cham Z roi roi xa >= 2 gia, quay lai):** 90d o chinh n=8, WR 25%, R -0,09 (khong khac doi chung); 2 nam o chinh nua 1 +0,01 / nua 2 +0,20 nhung N=3 theta 0,7 am ca hai nua. **Khong tot hon base.**
   - **V2 "o volume lon tai Z":** 90d n=2 (khong ket luan); 2 nam o chinh nua 1 +0,25 (n=32) / nua 2 **-0,25** (n=14); hang theta 0,7: +0,68 / -0,69. **Dao chieu giua 2 nua => khong ben.** Cac luat dung ra phai thich "co bong bong lon thi hap thu that" khong thang duoc o nua sau.
6. **Neo tai nen xac nhan:** da tranh duoc — moi lenh vao o gia dong CF va do tu nen ke tiep nen WR ~28-32% o R:R 3 la **WR that**, khong phai bay "dao chieu duoc 50%" cua phep do cu. Dieu do cho thay phep do cu 57,6% (n=126) cung gan nhu khong chuyen thanh loi the khi co SL/TP that va chi phi.
7. **Dinh nghia ngan ve n vs chat luong:** muc tieu 10-20 lenh/ngay khong the dat bang B: ke ca ban 2 nam B chi cho 0,25 lenh/ngay.

**De xuat sua dinh nghia (kem ly do co che, de agent chinh quyet; chua do):**
- Bo luat "giam nghiem ngat tung nen": hap thu la *no luc (volume/delta) lon ma gia khong di tiep*; khong can than va delta cua tung nen cu giam tuan tu, chi can "khong tiep tuc mo rong ve phia M". Thay bang: tong |delta| cum >= max cua move va cuc tri cum <= Z + 0,5 (tuc phe M tan cong nhung bi chan).
- Doi "cuc tri <= Z+0,5" thanh do theo `u` (trung vi bien do 50 nen), vi 0,5 gia co dinh khong doi theo bien dong; con lai ap luat o phase A cung bo loc "chua co VA" bang cach dung VA hom qua.
- Tach phase A ra khoi B (khong co che do) hoac them bo loc dac thu cho A; ban hien tai dang tron hai che do du lieu.
- Neu giu B trong indicator: de **tat mac dinh** theo QD-5 (kỳ vong khong khac doi chung o 90d, 2 nam mong manh); chi bat lai khi co them du lieu moi (>= 3 thang live/test) xac nhan N=3 + theta 0,5.
