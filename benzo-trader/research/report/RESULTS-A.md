# RESULTS-A - Setup A Pha hoi (Benzo Trader)

Sinh boi `setup_a_pha_hoi.py --all` (deterministic, seed co dinh). Chi phi 0,2 gia/lenh, TP 3R, gio UTC va VN (UTC+7). Dinh nghia chi tiet o docstring cua script.

## 1. File 90d (GCZ26, 2026-07-23 -> 2026-10-21), TRAIN <= 09-15, TEST >= 09-16

Phien sach (khong splice/thin, >= 300 nen): **61**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **26** (con mo 0) | **0.40 lenh/ngay** tong 3 phase | theo phase: A 0.15/ngay (n=9), EU 0.07/ngay (n=4), US 0.21/ngay (n=13)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 26 | 11.5% | -0.62 | -1.93 | -16.1 | 13 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 9 | 22.2% | -0.21 | -0.61 | -1.9 | 4 |
| EU | 4 | 0.0% | -1.07 | -3.05 | -4.3 | 4 |
| US | 13 | 7.7% | -0.77 | -2.50 | -10.0 | 8 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 6 | 16.7% | -0.41 | -1.67 | -2.5 | 5 |
| VAH_Y | 5 | 0.0% | -1.08 | -2.82 | -5.4 | 5 |
| VAL_EU | 7 | 0.0% | -1.07 | -3.21 | -7.5 | 7 |
| VAL_Y | 8 | 25.0% | -0.09 | -0.45 | -0.8 | 4 |

### TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 17 | 5.9% | -0.84 | -2.54 | -14.4 | 13 |
| TEST | 9 | 22.2% | -0.20 | -0.78 | -1.8 | 6 |

> **TEST co n=9 < 30: CHUA KET LUAN DUOC tren nua TEST cua file 90d.**

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-07 | 3 | 0.0% | -1.10 | -2.13 | -3.3 | 3 |
| 2026-08 | 9 | 0.0% | -1.08 | -3.04 | -9.7 | 9 |
| 2026-09 | 9 | 33.3% | 0.26 | -0.51 | 2.3 | 3 |
| 2026-10 | 5 | 0.0% | -1.09 | -2.36 | -5.5 | 5 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 35 | 8.6% | -0.74 | 22 / -0.90 | 13 / -0.47 |
| 2 | 0.5 | 31 | 9.7% | -0.69 | 20 / -0.88 | 11 / -0.36 |
| 2 | 0.6 | 26 | 11.5% | -0.62 | 16 / -0.83 | 10 / -0.29 |
| 3 | 0.4 | 30 | 10.0% | -0.68 | 19 / -0.87 | 11 / -0.36 |
| 3 | 0.5 | 26 | 11.5% | -0.62 | 17 / -0.84 | 9 / -0.20 |
| 3 | 0.6 | 21 | 14.3% | -0.52 | 13 / -0.78 | 8 / -0.09 |
| 4 | 0.4 | 26 | 11.5% | -0.62 | 17 / -0.85 | 9 / -0.20 |
| 4 | 0.5 | 23 | 13.0% | -0.56 | 15 / -0.81 | 8 / -0.09 |
| 4 | 0.6 | 20 | 15.0% | -0.49 | 13 / -0.78 | 7 / 0.05 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 1693 nen): R TB doi chung = **-0.21** (5-95%: -0.79 .. 0.34); lenh that = **-0.62**; ti le lan doi chung >= lenh that: **87.5%**.
- **kernel.control_sample** (cung vung E, cung che do, cung chieu, 1 nen ngau nhien/lenh that, khong can trang thai pha): R TB = **-0.15** (5-95%: -0.80 .. 0.59); ti le lan doi chung >= lenh that: **88.5%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 23:14 | 2026-09-02 06:14 | SELL | A | VAL_Y | 4376.8 | 4376.7 | 4378.5 | 4371.3 | TP | 2.89 | 13 |
| 2026-09-16 17:24 | 2026-09-17 00:24 | BUY | US | VAH_EU | 4385.2 | 4385.9 | 4383.9 | 4391.9 | TP | 2.90 | 5 |
| 2026-09-27 22:29 | 2026-09-28 05:29 | SELL | A | VAL_Y | 4304.4 | 4303.5 | 4305.7 | 4296.9 | TP | 2.91 | 10 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-28 23:39 | 2026-07-29 06:39 | SELL | A | VAL_Y | 4079.2 | 4078.6 | 4080.5 | 4072.9 | SL | -1.11 | 13 |
| 2026-08-19 23:17 | 2026-08-20 06:17 | BUY | A | VAH_Y | 4576.8 | 4577.0 | 4574.8 | 4583.6 | SL | -1.09 | 10 |
| 2026-08-31 19:58 | 2026-09-01 02:58 | BUY | US | VAH_EU | 4499.2 | 4498.8 | 4496.4 | 4506.0 | SL | -1.08 | 3 |
| 2026-09-21 17:56 | 2026-09-22 00:56 | SELL | US | VAL_EU | 4383.2 | 4381.7 | 4384.8 | 4372.4 | SL | -1.06 | 18 |
| 2026-10-21 06:19 | 2026-10-21 13:19 | SELL | EU | VAL_Y | 4135.2 | 4134.1 | 4136.5 | 4126.9 | SL | -1.08 | 5 |

## 2. File 2 nam (GC lien tuc 2024-08 -> 2026-08, loc splice/thin), 2 nua cat 2025-08-01

Phien sach (khong splice/thin, >= 300 nen): **492**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **263** (con mo 0) | **0.53 lenh/ngay** tong 3 phase | theo phase: A 0.17/ngay (n=83), EU 0.10/ngay (n=50), US 0.26/ngay (n=130)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 263 | 27.0% | -0.01 | -0.15 | -3.1 | 14 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 83 | 27.7% | 0.01 | -0.26 | 1.1 | 10 |
| EU | 50 | 20.0% | -0.29 | -0.46 | -14.6 | 7 |
| US | 130 | 29.2% | 0.08 | 0.04 | 10.5 | 9 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 68 | 32.4% | 0.21 | 0.38 | 14.0 | 7 |
| VAH_Y | 67 | 23.9% | -0.14 | -0.35 | -9.3 | 10 |
| VAL_EU | 62 | 25.8% | -0.06 | -0.33 | -3.5 | 9 |
| VAL_Y | 66 | 25.8% | -0.06 | -0.33 | -4.2 | 8 |

### Hai nua (cat 2025-08-01)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Nua 1 (truoc cat) | 161 | 29.2% | 0.07 | 0.02 | 11.1 | 14 |
| Nua 2 (sau cat) | 102 | 23.5% | -0.14 | -0.43 | -14.2 | 10 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 14 | 35.7% | 0.33 | 0.43 | 4.6 | 5 |
| 2024-09 | 16 | 18.8% | -0.35 | -0.67 | -5.5 | 9 |
| 2024-10 | 21 | 42.9% | 0.62 | 1.19 | 13.0 | 4 |
| 2024-11 | 17 | 47.1% | 0.78 | 1.49 | 13.3 | 7 |
| 2024-12 | 15 | 6.7% | -0.84 | -1.73 | -12.6 | 14 |
| 2025-01 | 14 | 28.6% | 0.04 | -0.31 | 0.6 | 6 |
| 2025-02 | 14 | 35.7% | 0.32 | 0.69 | 4.5 | 3 |
| 2025-03 | 17 | 29.4% | 0.08 | 0.09 | 1.3 | 3 |
| 2025-04 | 9 | 33.3% | 0.23 | -0.12 | 2.1 | 5 |
| 2025-05 | 3 | 0.0% | -1.09 | -2.43 | -3.3 | 3 |
| 2025-06 | 11 | 18.2% | -0.36 | -0.90 | -4.0 | 5 |
| 2025-07 | 10 | 20.0% | -0.30 | -0.43 | -3.0 | 5 |
| 2025-08 | 14 | 28.6% | 0.04 | 0.07 | 0.5 | 5 |
| 2025-09 | 22 | 27.3% | 0.00 | 0.17 | 0.0 | 5 |
| 2025-10 | 7 | 28.6% | 0.08 | 0.87 | 0.5 | 3 |
| 2025-11 | 5 | 20.0% | -0.26 | -0.50 | -1.3 | 3 |
| 2025-12 | 3 | 0.0% | -1.08 | -2.97 | -3.2 | 3 |
| 2026-01 | 9 | 11.1% | -0.62 | -2.22 | -5.6 | 5 |
| 2026-02 | 4 | 25.0% | -0.06 | -0.37 | -0.3 | 3 |
| 2026-03 | 1 | 0.0% | -1.10 | -2.20 | -1.1 | 1 |
| 2026-04 | 6 | 16.7% | -0.40 | -1.82 | -2.4 | 4 |
| 2026-05 | 14 | 28.6% | 0.06 | -0.02 | 0.9 | 6 |
| 2026-06 | 6 | 16.7% | -0.40 | -1.47 | -2.4 | 5 |
| 2026-07 | 8 | 37.5% | 0.42 | 1.44 | 3.4 | 4 |
| 2026-08 | 3 | 0.0% | -1.06 | -3.57 | -3.2 | 3 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | Nua1 n / R | Nua2 n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 314 | 26.8% | -0.02 | 192 / 0.09 | 122 / -0.19 |
| 2 | 0.5 | 293 | 27.3% | 0.00 | 183 / 0.08 | 110 / -0.13 |
| 2 | 0.6 | 240 | 30.4% | 0.13 | 152 / 0.22 | 88 / -0.03 |
| 3 | 0.4 | 279 | 26.2% | -0.04 | 166 / 0.08 | 113 / -0.23 |
| 3 | 0.5 | 263 | 27.0% | -0.01 | 161 / 0.07 | 102 / -0.14 |
| 3 | 0.6 | 211 | 29.9% | 0.10 | 129 / 0.21 | 82 / -0.05 |
| 4 | 0.4 | 235 | 26.8% | -0.02 | 146 / 0.13 | 89 / -0.27 |
| 4 | 0.5 | 218 | 28.0% | 0.03 | 140 / 0.13 | 78 / -0.15 |
| 4 | 0.6 | 176 | 31.2% | 0.16 | 112 / 0.29 | 64 / -0.08 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 18740 nen): R TB doi chung = **-0.08** (5-95%: -0.24 .. 0.09); lenh that = **-0.01**; ti le lan doi chung >= lenh that: **24.0%**.
- **kernel.control_sample** (cung vung E, cung che do, cung chieu, 1 nen ngau nhien/lenh that, khong can trang thai pha): R TB = **-0.19** (5-95%: -0.36 .. -0.01); ti le lan doi chung >= lenh that: **6.0%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-01 19:42 | 2024-08-02 02:42 | BUY | US | VAH_EU | 2486.4 | 2487.4 | 2485.1 | 2494.3 | TP | 2.91 | 9 |
| 2024-11-21 03:33 | 2024-11-21 10:33 | BUY | A | VAH_Y | 2656.4 | 2657.2 | 2655.1 | 2663.5 | TP | 2.90 | 3 |
| 2025-03-05 13:28 | 2025-03-05 20:28 | SELL | US | VAL_EU | 2924.8 | 2924.0 | 2926.1 | 2917.7 | TP | 2.90 | 5 |
| 2025-09-04 08:04 | 2025-09-04 15:04 | SELL | EU | VAL_Y | 3602.8 | 3602.0 | 3604.5 | 3594.5 | TP | 2.92 | 289 |
| 2026-07-20 13:43 | 2026-07-20 20:43 | SELL | US | VAL_EU | 4019.2 | 4017.8 | 4021.4 | 4007.0 | TP | 2.94 | 59 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-08 03:13 | 2024-08-08 10:13 | SELL | A | VAL_Y | 2429.6 | 2428.6 | 2430.9 | 2421.7 | SL | -1.09 | 3 |
| 2024-12-16 04:39 | 2024-12-16 11:39 | SELL | A | VAL_Y | 2671.6 | 2670.6 | 2672.9 | 2663.7 | SL | -1.09 | 5 |
| 2025-05-13 07:13 | 2025-05-13 14:13 | BUY | EU | VAH_Y | 3264.4 | 3265.0 | 3263.1 | 3270.7 | SL | -1.11 | 6 |
| 2025-10-15 12:37 | 2025-10-15 19:37 | SELL | US | VAL_EU | 4203.6 | 4203.3 | 4207.3 | 4191.3 | SL | -1.05 | 6 |
| 2026-08-17 18:32 | 2026-08-18 01:32 | BUY | US | VAH_EU | 4458.8 | 4460.5 | 4456.7 | 4471.9 | SL | -1.05 | 141 |

# Bien the co che (moi bien the bao rieng, khong tron)

## V1 delta nen M5 pha cung chieu - 90d

Phien sach (khong splice/thin, >= 300 nen): **61**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **25** (con mo 0) | **0.38 lenh/ngay** tong 3 phase | theo phase: A 0.16/ngay (n=10), EU 0.05/ngay (n=3), US 0.20/ngay (n=12)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 25 | 16.0% | -0.45 | -1.54 | -11.2 | 11 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 10 | 20.0% | -0.30 | -0.71 | -3.0 | 4 |
| EU | 3 | 0.0% | -1.07 | -3.30 | -3.2 | 3 |
| US | 12 | 16.7% | -0.41 | -1.79 | -4.9 | 7 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 5 | 20.0% | -0.27 | -1.58 | -1.4 | 4 |
| VAH_Y | 5 | 0.0% | -1.08 | -2.82 | -5.4 | 5 |
| VAL_EU | 7 | 14.3% | -0.51 | -1.94 | -3.6 | 5 |
| VAL_Y | 8 | 25.0% | -0.10 | -0.36 | -0.8 | 3 |

### TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 15 | 6.7% | -0.81 | -2.59 | -12.2 | 11 |
| TEST | 10 | 30.0% | 0.10 | 0.03 | 1.0 | 4 |

> **TEST co n=10 < 30: CHUA KET LUAN DUOC tren nua TEST cua file 90d.**

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-07 | 2 | 0.0% | -1.11 | -2.05 | -2.2 | 2 |
| 2026-08 | 8 | 0.0% | -1.07 | -3.16 | -8.6 | 8 |
| 2026-09 | 8 | 37.5% | 0.42 | -0.06 | 3.4 | 3 |
| 2026-10 | 7 | 14.3% | -0.53 | -1.23 | -3.7 | 4 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 32 | 12.5% | -0.59 | 18 / -0.85 | 14 / -0.24 |
| 2 | 0.5 | 28 | 14.3% | -0.51 | 16 / -0.83 | 12 / -0.10 |
| 2 | 0.6 | 23 | 17.4% | -0.39 | 12 / -0.75 | 11 / -0.01 |
| 3 | 0.4 | 29 | 13.8% | -0.54 | 17 / -0.84 | 12 / -0.10 |
| 3 | 0.5 | 25 | 16.0% | -0.45 | 15 / -0.81 | 10 / 0.10 |
| 3 | 0.6 | 20 | 20.0% | -0.29 | 11 / -0.72 | 9 / 0.23 |
| 4 | 0.4 | 25 | 16.0% | -0.45 | 15 / -0.81 | 10 / 0.10 |
| 4 | 0.5 | 22 | 18.2% | -0.36 | 13 / -0.77 | 9 / 0.23 |
| 4 | 0.6 | 19 | 21.1% | -0.25 | 11 / -0.72 | 8 / 0.40 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 1487 nen): R TB doi chung = **-0.24** (5-95%: -0.64 .. 0.30); lenh that = **-0.45**; ti le lan doi chung >= lenh that: **67.5%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 23:14 | 2026-09-02 06:14 | SELL | A | VAL_Y | 4376.8 | 4376.7 | 4378.5 | 4371.3 | TP | 2.89 | 13 |
| 2026-09-16 17:24 | 2026-09-17 00:24 | BUY | US | VAH_EU | 4385.2 | 4385.9 | 4383.9 | 4391.9 | TP | 2.90 | 5 |
| 2026-09-27 22:29 | 2026-09-28 05:29 | SELL | A | VAL_Y | 4304.4 | 4303.5 | 4305.7 | 4296.9 | TP | 2.91 | 10 |
| 2026-10-12 15:54 | 2026-10-12 22:54 | SELL | US | VAL_EU | 4193.6 | 4193.3 | 4194.9 | 4188.5 | TP | 2.88 | 29 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-28 23:39 | 2026-07-29 06:39 | SELL | A | VAL_Y | 4079.2 | 4078.6 | 4080.5 | 4072.9 | SL | -1.11 | 13 |
| 2026-08-19 23:17 | 2026-08-20 06:17 | BUY | A | VAH_Y | 4576.8 | 4577.0 | 4574.8 | 4583.6 | SL | -1.09 | 10 |
| 2026-09-01 22:53 | 2026-09-02 05:53 | SELL | A | VAL_Y | 4376.8 | 4376.1 | 4378.1 | 4370.1 | SL | -1.10 | 11 |
| 2026-10-02 00:02 | 2026-10-02 07:02 | BUY | A | VAH_Y | 4210.4 | 4209.7 | 4207.6 | 4216.0 | SL | -1.10 | 9 |
| 2026-10-21 06:19 | 2026-10-21 13:19 | SELL | EU | VAL_Y | 4135.2 | 4134.1 | 4136.5 | 4126.9 | SL | -1.08 | 5 |

## V1 delta nen M5 pha cung chieu - 2 nam

Phien sach (khong splice/thin, >= 300 nen): **492**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **261** (con mo 0) | **0.53 lenh/ngay** tong 3 phase | theo phase: A 0.18/ngay (n=87), EU 0.10/ngay (n=51), US 0.25/ngay (n=123)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 261 | 28.0% | 0.03 | -0.04 | 7.1 | 17 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 87 | 29.9% | 0.10 | -0.04 | 8.7 | 10 |
| EU | 51 | 19.6% | -0.30 | -0.48 | -15.5 | 10 |
| US | 123 | 30.1% | 0.11 | 0.15 | 13.9 | 10 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 64 | 31.2% | 0.16 | 0.27 | 10.3 | 6 |
| VAH_Y | 63 | 25.4% | -0.08 | -0.23 | -5.0 | 9 |
| VAL_EU | 59 | 28.8% | 0.06 | 0.02 | 3.6 | 8 |
| VAL_Y | 75 | 26.7% | -0.02 | -0.18 | -1.8 | 8 |

### Hai nua (cat 2025-08-01)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Nua 1 (truoc cat) | 159 | 30.8% | 0.13 | 0.22 | 21.3 | 17 |
| Nua 2 (sau cat) | 102 | 23.5% | -0.14 | -0.44 | -14.2 | 11 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 13 | 38.5% | 0.44 | 0.63 | 5.7 | 4 |
| 2024-09 | 14 | 28.6% | 0.05 | 0.19 | 0.7 | 7 |
| 2024-10 | 22 | 40.9% | 0.54 | 0.98 | 11.8 | 4 |
| 2024-11 | 17 | 52.9% | 1.02 | 2.24 | 17.4 | 7 |
| 2024-12 | 14 | 0.0% | -1.10 | -2.17 | -15.4 | 14 |
| 2025-01 | 14 | 28.6% | 0.04 | -0.19 | 0.5 | 4 |
| 2025-02 | 15 | 33.3% | 0.23 | 0.45 | 3.4 | 3 |
| 2025-03 | 18 | 27.8% | 0.01 | -0.04 | 0.2 | 4 |
| 2025-04 | 8 | 37.5% | 0.40 | 0.35 | 3.2 | 4 |
| 2025-05 | 4 | 0.0% | -1.08 | -2.72 | -4.3 | 4 |
| 2025-06 | 11 | 27.3% | 0.01 | 0.15 | 0.1 | 4 |
| 2025-07 | 9 | 22.2% | -0.21 | -0.18 | -1.9 | 5 |
| 2025-08 | 13 | 23.1% | -0.18 | -0.67 | -2.3 | 5 |
| 2025-09 | 23 | 26.1% | -0.05 | 0.11 | -1.2 | 6 |
| 2025-10 | 6 | 33.3% | 0.27 | 1.75 | 1.6 | 2 |
| 2025-11 | 6 | 33.3% | 0.27 | 1.10 | 1.6 | 3 |
| 2025-12 | 2 | 0.0% | -1.09 | -2.55 | -2.2 | 2 |
| 2026-01 | 9 | 11.1% | -0.62 | -2.22 | -5.6 | 5 |
| 2026-02 | 5 | 20.0% | -0.27 | -0.84 | -1.3 | 4 |
| 2026-03 | 1 | 0.0% | -1.10 | -2.20 | -1.1 | 1 |
| 2026-04 | 7 | 14.3% | -0.49 | -2.19 | -3.4 | 5 |
| 2026-05 | 12 | 25.0% | -0.08 | -0.51 | -0.9 | 6 |
| 2026-06 | 6 | 16.7% | -0.40 | -1.47 | -2.4 | 5 |
| 2026-07 | 9 | 44.4% | 0.70 | 1.89 | 6.3 | 4 |
| 2026-08 | 3 | 0.0% | -1.06 | -3.57 | -3.2 | 3 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | Nua1 n / R | Nua2 n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 302 | 28.5% | 0.05 | 184 / 0.20 | 118 / -0.20 |
| 2 | 0.5 | 283 | 29.0% | 0.07 | 175 / 0.20 | 108 / -0.15 |
| 2 | 0.6 | 231 | 32.5% | 0.21 | 145 / 0.34 | 86 / -0.01 |
| 3 | 0.4 | 275 | 27.6% | 0.01 | 164 / 0.17 | 111 / -0.22 |
| 3 | 0.5 | 261 | 28.0% | 0.03 | 159 / 0.13 | 102 / -0.14 |
| 3 | 0.6 | 209 | 31.6% | 0.17 | 128 / 0.28 | 81 / 0.01 |
| 4 | 0.4 | 234 | 28.2% | 0.04 | 146 / 0.24 | 88 / -0.31 |
| 4 | 0.5 | 219 | 28.8% | 0.06 | 140 / 0.22 | 79 / -0.22 |
| 4 | 0.6 | 176 | 33.0% | 0.23 | 113 / 0.39 | 63 / -0.06 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 16618 nen): R TB doi chung = **-0.08** (5-95%: -0.26 .. 0.08); lenh that = **0.03**; ti le lan doi chung >= lenh that: **16.0%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-01 19:42 | 2024-08-02 02:42 | BUY | US | VAH_EU | 2486.4 | 2487.4 | 2485.1 | 2494.3 | TP | 2.91 | 9 |
| 2024-11-04 23:43 | 2024-11-05 06:43 | SELL | A | VAL_Y | 2746.0 | 2745.5 | 2747.3 | 2740.1 | TP | 2.89 | 12 |
| 2025-03-05 13:28 | 2025-03-05 20:28 | SELL | US | VAL_EU | 2924.8 | 2924.0 | 2926.1 | 2917.7 | TP | 2.90 | 5 |
| 2025-09-12 01:09 | 2025-09-12 08:09 | BUY | A | VAH_Y | 3677.2 | 3678.6 | 3675.9 | 3686.7 | TP | 2.93 | 3 |
| 2026-07-20 13:43 | 2026-07-20 20:43 | SELL | US | VAL_EU | 4019.2 | 4017.8 | 4021.4 | 4007.0 | TP | 2.94 | 59 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-08 03:13 | 2024-08-08 10:13 | SELL | A | VAL_Y | 2429.6 | 2428.6 | 2430.9 | 2421.7 | SL | -1.09 | 3 |
| 2024-12-17 18:25 | 2024-12-18 01:25 | BUY | US | VAH_EU | 2661.2 | 2661.9 | 2659.9 | 2667.9 | SL | -1.10 | 15 |
| 2025-05-22 11:49 | 2025-05-22 18:49 | SELL | EU | VAL_Y | 3301.2 | 3300.8 | 3304.2 | 3290.6 | SL | -1.06 | 48 |
| 2025-10-31 18:59 | 2025-11-01 01:59 | SELL | US | VAL_EU | 4013.2 | 4011.7 | 4014.5 | 4003.3 | SL | -1.07 | 3 |
| 2026-08-17 18:32 | 2026-08-18 01:32 | BUY | US | VAH_EU | 4458.8 | 4460.5 | 4456.7 | 4471.9 | SL | -1.05 | 141 |

## V2 giu canh (CF dong phia ngoai E) - 90d

Phien sach (khong splice/thin, >= 300 nen): **61**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **21** (con mo 0) | **0.32 lenh/ngay** tong 3 phase | theo phase: A 0.10/ngay (n=6), EU 0.05/ngay (n=3), US 0.20/ngay (n=12)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 21 | 14.3% | -0.51 | -1.75 | -10.7 | 11 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 6 | 33.3% | 0.23 | 0.50 | 1.4 | 4 |
| EU | 3 | 0.0% | -1.07 | -3.30 | -3.2 | 3 |
| US | 12 | 8.3% | -0.74 | -2.49 | -8.9 | 7 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 5 | 20.0% | -0.28 | -1.48 | -1.4 | 4 |
| VAH_Y | 3 | 0.0% | -1.07 | -3.23 | -3.2 | 3 |
| VAL_EU | 7 | 0.0% | -1.07 | -3.21 | -7.5 | 7 |
| VAL_Y | 6 | 33.3% | 0.23 | 0.47 | 1.4 | 3 |

### TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 14 | 7.1% | -0.80 | -2.44 | -11.1 | 11 |
| TEST | 7 | 28.6% | 0.06 | -0.37 | 0.4 | 4 |

> **TEST co n=7 < 30: CHUA KET LUAN DUOC tren nua TEST cua file 90d.**

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-07 | 2 | 0.0% | -1.11 | -2.05 | -2.2 | 2 |
| 2026-08 | 8 | 0.0% | -1.08 | -3.10 | -8.6 | 8 |
| 2026-09 | 8 | 37.5% | 0.42 | -0.06 | 3.4 | 2 |
| 2026-10 | 3 | 0.0% | -1.09 | -2.47 | -3.3 | 3 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | TRAIN n / R | TEST n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 31 | 9.7% | -0.69 | 19 / -0.87 | 12 / -0.42 |
| 2 | 0.5 | 27 | 11.1% | -0.64 | 17 / -0.84 | 10 / -0.29 |
| 2 | 0.6 | 24 | 12.5% | -0.59 | 14 / -0.80 | 10 / -0.29 |
| 3 | 0.4 | 25 | 12.0% | -0.60 | 16 / -0.83 | 9 / -0.20 |
| 3 | 0.5 | 21 | 14.3% | -0.51 | 14 / -0.80 | 7 / 0.06 |
| 3 | 0.6 | 18 | 16.7% | -0.42 | 11 / -0.72 | 7 / 0.06 |
| 4 | 0.4 | 22 | 13.6% | -0.54 | 15 / -0.82 | 7 / 0.06 |
| 4 | 0.5 | 19 | 15.8% | -0.45 | 13 / -0.77 | 6 / 0.25 |
| 4 | 0.6 | 17 | 17.6% | -0.38 | 11 / -0.72 | 6 / 0.25 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 1698 nen): R TB doi chung = **-0.24** (5-95%: -0.74 .. 0.30); lenh that = **-0.51**; ti le lan doi chung >= lenh that: **77.5%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-09-01 23:14 | 2026-09-02 06:14 | SELL | A | VAL_Y | 4376.8 | 4376.7 | 4378.5 | 4371.3 | TP | 2.89 | 13 |
| 2026-09-16 17:24 | 2026-09-17 00:24 | BUY | US | VAH_EU | 4385.2 | 4385.9 | 4383.9 | 4391.9 | TP | 2.90 | 5 |
| 2026-09-27 22:29 | 2026-09-28 05:29 | SELL | A | VAL_Y | 4304.4 | 4303.5 | 4305.7 | 4296.9 | TP | 2.91 | 10 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-07-28 23:39 | 2026-07-29 06:39 | SELL | A | VAL_Y | 4079.2 | 4078.6 | 4080.5 | 4072.9 | SL | -1.11 | 13 |
| 2026-08-17 18:32 | 2026-08-18 01:32 | BUY | US | VAH_EU | 4458.8 | 4460.5 | 4456.7 | 4471.9 | SL | -1.05 | 141 |
| 2026-08-28 04:49 | 2026-08-28 11:49 | SELL | A | VAL_Y | 4633.2 | 4632.9 | 4634.6 | 4627.8 | SL | -1.12 | 9 |
| 2026-09-21 17:56 | 2026-09-22 00:56 | SELL | US | VAL_EU | 4383.2 | 4381.7 | 4384.8 | 4372.4 | SL | -1.06 | 18 |
| 2026-10-21 06:19 | 2026-10-21 13:19 | SELL | EU | VAL_Y | 4135.2 | 4134.1 | 4136.5 | 4126.9 | SL | -1.08 | 5 |

## V2 giu canh (CF dong phia ngoai E) - 2 nam

Phien sach (khong splice/thin, >= 300 nen): **492**. Cell chinh = (n_hoi 3, than CF 0,5). Hoa von o 3R sau chi phi ~27% WR (0,2 gia ~ 0,1R).

Lenh da dong **252** (con mo 0) | **0.51 lenh/ngay** tong 3 phase | theo phase: A 0.16/ngay (n=80), EU 0.10/ngay (n=48), US 0.25/ngay (n=124)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 252 | 27.4% | 0.01 | -0.09 | 1.6 | 14 |

### Theo phase

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 80 | 28.7% | 0.06 | -0.13 | 4.5 | 9 |
| EU | 48 | 20.8% | -0.26 | -0.40 | -12.4 | 8 |
| US | 124 | 29.0% | 0.08 | 0.06 | 9.4 | 9 |

### Theo vung E

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| VAH_EU | 64 | 32.8% | 0.23 | 0.41 | 14.7 | 6 |
| VAH_Y | 63 | 25.4% | -0.08 | -0.20 | -4.8 | 10 |
| VAL_EU | 60 | 25.0% | -0.09 | -0.31 | -5.2 | 9 |
| VAL_Y | 65 | 26.2% | -0.05 | -0.26 | -3.1 | 7 |

### Hai nua (cat 2025-08-01)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Nua 1 (truoc cat) | 155 | 29.7% | 0.09 | 0.12 | 14.1 | 14 |
| Nua 2 (sau cat) | 97 | 23.7% | -0.13 | -0.42 | -12.5 | 11 |

### Theo thang

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 14 | 35.7% | 0.34 | 0.79 | 4.7 | 5 |
| 2024-09 | 15 | 20.0% | -0.29 | -0.62 | -4.4 | 8 |
| 2024-10 | 20 | 40.0% | 0.51 | 1.07 | 10.2 | 4 |
| 2024-11 | 16 | 50.0% | 0.90 | 1.77 | 14.4 | 6 |
| 2024-12 | 15 | 6.7% | -0.84 | -1.73 | -12.6 | 14 |
| 2025-01 | 14 | 28.6% | 0.04 | -0.31 | 0.6 | 6 |
| 2025-02 | 13 | 38.5% | 0.44 | 0.84 | 5.7 | 3 |
| 2025-03 | 17 | 29.4% | 0.08 | 0.19 | 1.4 | 3 |
| 2025-04 | 9 | 33.3% | 0.23 | -0.12 | 2.1 | 5 |
| 2025-05 | 2 | 0.0% | -1.10 | -2.30 | -2.2 | 2 |
| 2025-06 | 10 | 20.0% | -0.29 | -0.72 | -2.9 | 5 |
| 2025-07 | 10 | 20.0% | -0.30 | -0.43 | -3.0 | 5 |
| 2025-08 | 12 | 25.0% | -0.10 | -0.10 | -1.2 | 4 |
| 2025-09 | 20 | 30.0% | 0.11 | 0.39 | 2.2 | 5 |
| 2025-10 | 7 | 28.6% | 0.08 | 0.87 | 0.5 | 3 |
| 2025-11 | 5 | 20.0% | -0.26 | -0.50 | -1.3 | 3 |
| 2025-12 | 3 | 0.0% | -1.08 | -2.97 | -3.2 | 3 |
| 2026-01 | 9 | 11.1% | -0.62 | -2.22 | -5.6 | 5 |
| 2026-02 | 4 | 25.0% | -0.06 | -0.37 | -0.3 | 3 |
| 2026-03 | 1 | 0.0% | -1.10 | -2.20 | -1.1 | 1 |
| 2026-04 | 6 | 16.7% | -0.40 | -1.82 | -2.4 | 4 |
| 2026-05 | 14 | 28.6% | 0.07 | -0.11 | 0.9 | 7 |
| 2026-06 | 5 | 20.0% | -0.26 | -1.24 | -1.3 | 4 |
| 2026-07 | 8 | 37.5% | 0.42 | 1.44 | 3.4 | 4 |
| 2026-08 | 3 | 0.0% | -1.06 | -3.57 | -3.2 | 3 |

### Luoi 3x3 (so nen hoi toi thieu x ti le than CF)

| n_hoi | than CF | n | WR | R TB | Nua1 n / R | Nua2 n / R |
|---|---|---|---|---|---|---|
| 2 | 0.4 | 298 | 26.5% | -0.03 | 182 / 0.09 | 116 / -0.21 |
| 2 | 0.5 | 279 | 27.6% | 0.01 | 175 / 0.11 | 104 / -0.15 |
| 2 | 0.6 | 229 | 31.4% | 0.17 | 147 / 0.26 | 82 / -0.00 |
| 3 | 0.4 | 269 | 26.4% | -0.03 | 161 / 0.10 | 108 / -0.23 |
| 3 | 0.5 | 252 | 27.4% | 0.01 | 155 / 0.09 | 97 / -0.13 |
| 3 | 0.6 | 204 | 30.9% | 0.15 | 126 / 0.24 | 78 / -0.00 |
| 4 | 0.4 | 230 | 27.0% | -0.01 | 143 / 0.16 | 87 / -0.29 |
| 4 | 0.5 | 213 | 28.2% | 0.04 | 137 / 0.16 | 76 / -0.18 |
| 4 | 0.6 | 172 | 32.0% | 0.19 | 110 / 0.32 | 62 / -0.04 |

### Doi chung (200 lan lay mau)

- **Cung trang thai pha** (nen ngau nhien trong trang thai pha, cham E, cung chieu, SL/TP y het, bo nhip hoi + CF; ho 18755 nen): R TB doi chung = **-0.08** (5-95%: -0.24 .. 0.05); lenh that = **0.01**; ti le lan doi chung >= lenh that: **17.0%**.

#### Vi du THANG (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-01 19:42 | 2024-08-02 02:42 | BUY | US | VAH_EU | 2486.4 | 2487.4 | 2485.1 | 2494.3 | TP | 2.91 | 9 |
| 2024-11-21 03:33 | 2024-11-21 10:33 | BUY | A | VAH_Y | 2656.4 | 2657.2 | 2655.1 | 2663.5 | TP | 2.90 | 3 |
| 2025-03-05 13:28 | 2025-03-05 20:28 | SELL | US | VAL_EU | 2924.8 | 2924.0 | 2926.1 | 2917.7 | TP | 2.90 | 5 |
| 2025-09-12 01:09 | 2025-09-12 08:09 | BUY | A | VAH_Y | 3677.2 | 3678.6 | 3675.9 | 3686.7 | TP | 2.93 | 3 |
| 2026-07-20 13:43 | 2026-07-20 20:43 | SELL | US | VAL_EU | 4019.2 | 4017.8 | 4021.4 | 4007.0 | TP | 2.94 | 59 |

#### Vi du THUA (chon cach deu theo thoi gian)

| UTC | VN | chieu | phase | vung | canh E | vao | SL | TP | ket qua | R | nen hoi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024-08-08 03:13 | 2024-08-08 10:13 | SELL | A | VAL_Y | 2429.6 | 2428.6 | 2430.9 | 2421.7 | SL | -1.09 | 3 |
| 2024-12-16 04:39 | 2024-12-16 11:39 | SELL | A | VAL_Y | 2671.6 | 2670.6 | 2672.9 | 2663.7 | SL | -1.09 | 5 |
| 2025-05-02 00:22 | 2025-05-02 07:22 | BUY | A | VAH_Y | 3248.4 | 3249.4 | 3247.1 | 3256.3 | SL | -1.09 | 6 |
| 2025-10-31 18:59 | 2025-11-01 01:59 | SELL | US | VAL_EU | 4013.2 | 4011.7 | 4014.5 | 4003.3 | SL | -1.07 | 3 |
| 2026-08-17 18:32 | 2026-08-18 01:32 | BUY | US | VAH_EU | 4458.8 | 4460.5 | 4456.7 | 4471.9 | SL | -1.05 | 141 |

# Danh gia trung thuc

(Doan nay viet tay sau khi doc so lieu cua lan chay 2026-10-21; neu chay lai --all voi du lieu moi thi phai doc lai.)

**1. Setup A co loi the that khong? Chua thay.** Tren 2 nam (492 phien sach) cell chinh cho n=263, WR 27,0%, R TB -0,01, tuc ngay tai muc hoa von (~27% WR o 3R sau chi phi). Tren file 90d la -0,62R (n=26, WR 11,5%, chuoi thua 13). Hai ket qua cung huong "khong duong", va nua sau cua 2 nam (2025-08 -> 2026-08, n=102) la -0,14R, khop voi 90d gan day xau hon nua. Khong co dau hieu setup nay dua duoc WR 60-70% hay ky vong duong; WR that ~27% voi TP 3R.

**2. Doi chung: nhip hoi + CF khong them duoc gi ro rang.** Nen ngau nhien cung trang thai pha, cung chieu, cung SL/TP: -0,08R (2 nam; 24% so lan boc >= lenh that, tuc lenh that nam trong nhieu cua doi chung) va -0,21R (90d; lenh that con te hon doi chung, 87% so lan boc >= lenh that). Doi chung theo kernel.control_sample (khong can trang thai pha) -0,19R (2 nam; 6% >= lenh that): nghia la "cham canh VA bat ky luc nao" thua o 3R, va loc nhip hoi + CF keo ve ~0 nhung khong len duong. Lenh that tot hon doi chung ~+0,07..+0,18R, nho hon bien nhieu.

**3. Luoi 3x3: khong o nao ben o ca hai nua.** Tren 2 nam, ca 9 o deu am o nua 2 (-0,03..-0,31R) du nua 1 duong (+0,07..+0,29R). O tot nhat (n_hoi 4, than CF 0,6): +0,16R tong, nhung hang xom than CF 0,4/0,5 cung n_hoi am hoac xap xi 0 va nua 2 van -0,08R, n=64. Tren 90d: 8/9 o am o TEST; o (4; 0,6) TEST +0,05 chi n=7. **Khong chon o nao.** Xu huong "than CF cang lon cang tot" (+0,1..+0,16R o 0,6) nhat quan tren ca 3 hang n_hoi cua 2 nam, co the co co che that (CF manh hon = phe giu canh ro hon) nhung nho (n giam 25%) va chua qua duoc nua 2; ghi nhan, chua dung.

**4. Chi tiet co the dang de y (chua phai ket luan):**
- Phase EU (12:30-19:00 VN, E = VA hom qua) am nhat quan: -0,29R (2 nam, n=50, WR 20%), cung -0,30 o V1 va -0,26 o V2. Co che gioi thieu: plan muc 3.2 noi truoc COMEX hay co pha gia; vao theo canh VA hom qua luc chau Au co the bi quet. Nhung n=50, sai so cua WR ~ +-6% nen chi ~1,2 sigma duoi hoa von; day la thong ke tim thay SAU khi nhin so, chua dung de loc.
- US (n=130) +0,08R, vung VAH_EU +0,21R (n=68): duong nhung nho va khong qua doi chung ro rang; chua dam noi VAH la thien.
- Tan suat chi **0,4-0,5 lenh/ngay** (US ~0,2-0,26/ngay): setup A KHONG the dong gop vao muc 10-20 lenh/ngay; cung 2 nua cua 90d TEST chi n=9 (<30) nen **chua ket luan** o nua TEST.

**5. Hai bien the co che (bao rieng):** V1 (delta nen M5 pha cung chieu) 2 nam +0,03R, 90d -0,45R, nua 2 van -0,14R; V2 (CF dong o phia ngoai E) 2 nam +0,01R, 90d -0,51R. Ca hai khong sua duoc nua 2 va khong vuot doi chung ro rang (V1: 16% lan doi chung >= that o 2 nam, tot hon mot chut, nhung chua dang ke). Khong co bien the nao du manh de doi dinh nghia.

**6. De xuat (co co che, chua do):** (a) theo QD-5, setup A **nen tat mac dinh** trong indicator (van co cong tat): ky vong am o ca hai nua cua 90d va o nua 2 cua 2 nam. (b) Neu muon cuu: plan muc 3.2 noi "lan phа 1 chui lai thi khong duoi, lan 2 moi la pha sach" va "pha sau 20:30 dang tin hon" - bo do hien tai dang coi moi cu M5 dong ngoai la mot cu pha moi; thu rieng "chi vao sau cu pha thu 2 / sau 20:30 VN" va "het han trang thai sau N nen" (hien tai mot so lenh vao sau 289 nen hoi, tuc retest nhieu gio sau, khong con la phá hoi). Day la 2 y tuong co co che, can do tren ban ghi rieng, KHONG phai ket qua da kiem.

**7. Dieu chua chac:** (i) SL: mep xa vung E dat E +-1,0 gia (toi dien giai 'cach vung <= 1 gia'); nho la co ban chat hay cat tran 4 gia (SL TB ~2,5 gia) - doi nua be rong co the doi ket qua; (ii) 'move pha' (de lay L) toi dinh nghia bang cac nen M1 lui toi nen cuoi cung dong o phia trong, toi da 60 nen; (iii) trang thai pha khong het han (xem tren); (iv) WR 90d rat thap (11,5%) so voi 27% cua 2 nam co the phan anh che do thi truong 2026-08..10 (bien do lon, SL cat tran) hon la loi dinh nghia; (v) khong co ca kiem 2 lenh cung E bi `one_at_a_time` bo qua nhung van tinh vao dem 2/phien/E (bao thu).
