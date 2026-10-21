# RESULTS-D - Setup D Trap (sinh boi setup_d_trap.py, deterministic)

Dinh nghia: plan 3-D. Hang so co dinh: move ro hinh thanh <= 30 nen; nhip hoi <= 30 nen, sau >= 1.0 gia; CF trong 3 nen sau nen cuc tri; Z cach cuc tri <= 1.0 gia hoac rau cham; o volume >= 2x trung vi o (>= 3 muc). Chi phi 0,2 gia/lenh, 1 lenh mo cung luc, SL = kernel.risk (cau truc = cuc tri nhip hoi). Gio UTC / VN = UTC+7. 2 tham so tu do: min_move x retr max (luoi 3x3).

## File 90d (GCZ26, 2026-07-23 -> 2026-10-21)

Phien: 65 (sach 61). Nen M1: 86333.

### File 90d (GCZ26, 2026-07-23 -> 2026-10-21) - delta (min_move 5, retr <= 70%, TP 2R)

Lenh da dong: **7** (con mo 0). Lenh/ngay (tren 61 phien sach): **0.11**. Theo phase: A 0.066 - EU 0.016 - US 0.033 (US 19:00-23:00 VN: 0.016)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 7 | 42.9% | 0.20 | 1.07 | 1.4 | 2 |
| BUY | 4 | 50.0% | 0.40 | 1.80 | 1.6 | 1 |
| SELL | 3 | 33.3% | -0.06 | 0.10 | -0.2 | 1 |
| Tong @TP 3R | 7 | 14.3% | -0.51 | -0.90 | -3.6 | 4 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-08 | 1 | 100.0% | 1.93 | 5.60 | 1.9 | 0 |
| 2026-09 | 3 | 33.3% | -0.06 | 0.07 | -0.2 | 1 |
| 2026-10 | 3 | 33.3% | -0.12 | 0.57 | -0.3 | 2 |

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 4 | 25.0% | -0.36 | -0.28 | -1.4 | 3 |
| EU | 1 | 100.0% | 1.93 | 5.60 | 1.9 | 0 |
| US | 2 | 50.0% | 0.45 | 1.50 | 0.9 | 1 |

**TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 3 | 66.7% | 0.94 | 2.87 | 2.8 | 1 |
| TRAIN BUY | 1 | 100.0% | 1.93 | 5.60 | 1.9 | 0 |
| TRAIN SELL | 2 | 50.0% | 0.45 | 1.50 | 0.9 | 1 |
| TEST | 4 | 25.0% | -0.36 | -0.28 | -1.4 | 2 |
| TEST BUY | 3 | 33.3% | -0.12 | 0.53 | -0.3 | 1 |
| TEST SELL | 1 | 0.0% | -1.08 | -2.70 | -1.1 | 1 |

> **TEST chi co n=4 < 30: CHUA KET LUAN duoc o nua TEST.**

**Theo vung Z**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| POC_Y | 2 | 50.0% | 0.44 | 0.80 | 0.9 | 1 |
| VAH_Y | 1 | 0.0% | -1.20 | -1.20 | -1.2 | 1 |
| VAL_Y | 2 | 50.0% | 0.43 | 1.45 | 0.9 | 1 |
| VWAP_D | 2 | 50.0% | 0.43 | 2.10 | 0.9 | 1 |

**Luoi 3x3 (delta, TP 2R, toan bo thoi gian)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=3 WR 33% R -0.10 | n=13 WR 46% R 0.28 | n=22 WR 45% R 0.27 |
| 5 gia | n=1 WR 0% R -1.08 | n=7 WR 43% R 0.20 | n=11 WR 45% R 0.28 |
| 7 gia | n=1 WR 0% R -1.08 | n=4 WR 25% R -0.32 | n=4 WR 25% R -0.32 |

**Luoi 3x3 theo TRAIN/TEST (delta)** (R TB; TRAIN / TEST; n TEST)

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | - / -0.10 (n 3) | 0.41 / 0.17 (n 7) | 0.83 / -0.28 (n 11) |
| 5 gia | - / -1.08 (n 1) | 0.94 / -0.36 (n 4) | 1.34 / -0.60 (n 6) |
| 7 gia | - / -1.08 (n 1) | -1.05 / -0.08 (n 3) | -1.05 / -0.08 (n 3) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 216 -> co nen CF trong 3 nen 22 -> loai splice/thin/OFF 2 -> loai BALANCE 3 -> loai 3 nen sau nen dai nhat 0 -> loai nguoc bias 8 -> loai SL > 4 gia 2 -> vao lenh (truoc luat 1 lenh mo) 7

**Doi chung (delta)**

- cau hinh 5/70%: that R TB **0.20** (n=7) | doi chung 200 lan: R TB -0.13 (5-95%: -0.74 .. 0.65); P(doi chung >= that) = **0.20**

**5 vi du THANG (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-06 23:46 | 2026-08-07 06:46 | BUY | 4306.0 | 4303.1 | 4311.8 | VAL_Y | TP | 1.93 | move 5.7 retr 65% Z VAL_Y 4302.4 ext 4303.4 (j=13424) |
| 2026-09-15 14:26 | 2026-09-15 21:26 | SELL | 4327.2 | 4330.8 | 4320.0 | VWAP_D | TP | 1.94 | move 6.5 retr 63% Z VWAP_D 4329.1 ext 4329.7 (j=50924) |
| 2026-10-01 07:40 | 2026-10-01 14:40 | BUY | 4191.6 | 4188.7 | 4197.4 | POC_Y | TP | 1.93 | move 7.5 retr 69% Z POC_Y 4189.2 ext 4189.8 (j=66750) |

**5 vi du THUA (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-11 17:13 | 2026-09-12 00:13 | SELL | 4406.8 | 4410.6 | 4399.2 | POC_Y | SL | -1.05 | move 7.1 retr 66% Z POC_Y 4407.6 ext 4409.0 (j=48372) |
| 2026-09-22 22:12 | 2026-09-23 05:12 | BUY | 4401.5 | 4398.9 | 4406.7 | VWAP_D | SL | -1.08 | move 8.1 retr 44% Z VWAP_D 4399.7 ext 4399.2 (j=58059) |
| 2026-10-01 23:25 | 2026-10-02 06:25 | BUY | 4210.4 | 4209.4 | 4212.4 | VAH_Y | SL | -1.20 | move 5.3 retr 51% Z VAH_Y 4210.4 ext 4209.7 (j=67637) |
| 2026-10-14 05:15 | 2026-10-14 12:15 | SELL | 4183.9 | 4186.4 | 4178.9 | VAL_Y | SL | -1.08 | move 9.3 retr 54% Z VAL_Y 4185.2 ext 4186.1 (j=79003) |

### File 90d (GCZ26, 2026-07-23 -> 2026-10-21) - cell (min_move 5, retr <= 70%, TP 2R)

Lenh da dong: **2** (con mo 0). Lenh/ngay (tren 61 phien sach): **0.03**. Theo phase: A 0.016 - EU 0.000 - US 0.016 (US 19:00-23:00 VN: 0.000)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |
| BUY | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |
| SELL | 0 | -% | - | - | 0.0 | 0 |
| Tong @TP 3R | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-09 | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 1 | 0.0% | -1.12 | -1.80 | -1.1 | 1 |
| EU | 0 | -% | - | - | 0.0 | 0 |
| US | 1 | 0.0% | -1.12 | -1.90 | -1.1 | 1 |

**TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 0 | -% | - | - | 0.0 | 0 |
| TRAIN BUY | 0 | -% | - | - | 0.0 | 0 |
| TRAIN SELL | 0 | -% | - | - | 0.0 | 0 |
| TEST | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |
| TEST BUY | 2 | 0.0% | -1.12 | -1.85 | -2.2 | 2 |
| TEST SELL | 0 | -% | - | - | 0.0 | 0 |

> **TEST chi co n=2 < 30: CHUA KET LUAN duoc o nua TEST.**

**Theo vung Z**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| POC_Y | 1 | 0.0% | -1.12 | -1.90 | -1.1 | 1 |
| VWAP_D | 1 | 0.0% | -1.12 | -1.80 | -1.1 | 1 |

**Luoi 3x3 (cell, TP 2R, toan bo thoi gian)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=3 WR 33% R -0.11 | n=5 WR 20% R -0.50 | n=9 WR 22% R -0.44 |
| 5 gia | n=1 WR 0% R -1.12 | n=2 WR 0% R -1.12 | n=3 WR 0% R -1.11 |
| 7 gia | n=0 WR -% R - | n=0 WR -% R - | n=0 WR -% R - |

**Luoi 3x3 theo TRAIN/TEST (cell)** (R TB; TRAIN / TEST; n TEST)

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | - / -0.11 (n 3) | -1.07 / -0.36 (n 4) | -0.36 / -0.51 (n 5) |
| 5 gia | - / -1.12 (n 1) | - / -1.12 (n 2) | - / -1.11 (n 3) |
| 7 gia | - / - (n 0) | - / - (n 0) | - / - (n 0) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 84 -> co nen CF trong 3 nen 8 -> loai splice/thin/OFF 3 -> loai BALANCE 1 -> loai 3 nen sau nen dai nhat 0 -> loai nguoc bias 2 -> loai SL > 4 gia 0 -> vao lenh (truoc luat 1 lenh mo) 2

**Doi chung (cell)**

- cau hinh 5/70%: that R TB **-1.12** (n=2) | doi chung 200 lan: R TB -0.04 (5-95%: -1.10 .. 1.87); P(doi chung >= that) = **0.98**

**5 vi du THANG (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|

**5 vi du THUA (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-22 23:29 | 2026-09-23 06:29 | BUY | 4402.3 | 4400.7 | 4405.5 | VWAP_D | SL | -1.12 | move 5.2 retr 60% Z VWAP_D 4401.1 ext 4401.0 (j=58135) |
| 2026-09-30 20:47 | 2026-10-01 03:47 | BUY | 4190.2 | 4188.5 | 4193.6 | POC_Y | SL | -1.12 | move 5.5 retr 47% Z POC_Y 4189.2 ext 4189.7 (j=66162) |

### File 90d (GCZ26, 2026-07-23 -> 2026-10-21) - V1 delta+CFmem (min_move 5, retr <= 70%, TP 2R)

Lenh da dong: **10** (con mo 0). Lenh/ngay (tren 61 phien sach): **0.15**. Theo phase: A 0.098 - EU 0.016 - US 0.049 (US 19:00-23:00 VN: 0.016)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 10 | 40.0% | 0.12 | 0.58 | 1.2 | 2 |
| BUY | 5 | 40.0% | 0.13 | 0.50 | 0.6 | 2 |
| SELL | 5 | 40.0% | 0.10 | 0.66 | 0.5 | 2 |
| Tong @TP 3R | 10 | 10.0% | -0.68 | -1.28 | -6.8 | 7 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-08 | 2 | 50.0% | 0.43 | 1.10 | 0.9 | 1 |
| 2026-09 | 2 | 50.0% | 0.43 | 2.10 | 0.9 | 1 |
| 2026-10 | 6 | 33.3% | -0.10 | -0.10 | -0.6 | 2 |

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 6 | 16.7% | -0.58 | -1.27 | -3.5 | 5 |
| EU | 1 | 100.0% | 1.93 | 5.60 | 1.9 | 0 |
| US | 3 | 66.7% | 0.91 | 2.60 | 2.7 | 1 |

**TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 3 | 66.7% | 0.94 | 3.07 | 2.8 | 1 |
| TRAIN BUY | 2 | 50.0% | 0.43 | 1.10 | 0.9 | 1 |
| TRAIN SELL | 1 | 100.0% | 1.94 | 7.00 | 1.9 | 0 |
| TEST | 7 | 28.6% | -0.24 | -0.49 | -1.7 | 2 |
| TEST BUY | 3 | 33.3% | -0.08 | 0.10 | -0.2 | 1 |
| TEST SELL | 4 | 25.0% | -0.36 | -0.92 | -1.4 | 2 |

> **TEST chi co n=7 < 30: CHUA KET LUAN duoc o nua TEST.**

**Theo vung Z**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| POC_Y | 2 | 50.0% | 0.42 | 1.55 | 0.8 | 1 |
| VAL_EU | 1 | 100.0% | 1.88 | 3.00 | 1.9 | 0 |
| VAL_Y | 2 | 50.0% | 0.43 | 1.45 | 0.9 | 1 |
| VWAP_D | 5 | 20.0% | -0.48 | -0.64 | -2.4 | 3 |

**Luoi 3x3 (V1 delta+CFmem, TP 2R, toan bo thoi gian)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=9 WR 22% R -0.45 | n=26 WR 46% R 0.29 | n=38 WR 47% R 0.33 |
| 5 gia | n=4 WR 25% R -0.36 | n=10 WR 40% R 0.12 | n=17 WR 47% R 0.33 |
| 7 gia | n=1 WR 0% R -1.08 | n=3 WR 33% R -0.08 | n=5 WR 40% R 0.12 |

**Luoi 3x3 theo TRAIN/TEST (V1 delta+CFmem)** (R TB; TRAIN / TEST; n TEST)

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | - / -0.45 (n 9) | 0.71 / 0.02 (n 16) | 0.86 / -0.10 (n 21) |
| 5 gia | - / -0.36 (n 4) | 0.94 / -0.24 (n 7) | 1.07 / -0.19 (n 10) |
| 7 gia | - / -1.08 (n 1) | - / -0.08 (n 3) | 0.41 / -0.08 (n 3) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 216 -> co nen CF trong 3 nen 46 -> loai splice/thin/OFF 1 -> loai BALANCE 9 -> loai 3 nen sau nen dai nhat 0 -> loai nguoc bias 23 -> loai SL > 4 gia 3 -> vao lenh (truoc luat 1 lenh mo) 10

**Doi chung (V1 delta+CFmem)**

- cau hinh 5/70%: that R TB **0.12** (n=10) | doi chung 200 lan: R TB -0.23 (5-95%: -0.81 .. 0.40); P(doi chung >= that) = **0.12**

**5 vi du THANG (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-06 23:46 | 2026-08-07 06:46 | BUY | 4306.0 | 4303.1 | 4311.8 | VAL_Y | TP | 1.93 | move 5.7 retr 65% Z VAL_Y 4302.4 ext 4303.4 (j=13424) |
| 2026-09-15 14:26 | 2026-09-15 21:26 | SELL | 4327.2 | 4330.8 | 4320.0 | VWAP_D | TP | 1.94 | move 6.5 retr 63% Z VWAP_D 4329.1 ext 4329.7 (j=50924) |
| 2026-10-01 07:38 | 2026-10-01 14:38 | BUY | 4192.1 | 4189.2 | 4197.9 | POC_Y | TP | 1.93 | move 7.5 retr 69% Z POC_Y 4189.2 ext 4189.8 (j=66750) |
| 2026-10-12 18:56 | 2026-10-13 01:56 | SELL | 4191.6 | 4193.2 | 4188.4 | VAL_EU | TP | 1.88 | move 6.1 retr 39% Z VAL_EU 4193.6 ext 4192.9 (j=77064) |

**5 vi du THUA (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-31 23:57 | 2026-09-01 06:57 | BUY | 4499.9 | 4496.7 | 4506.3 | VWAP_D | SL | -1.06 | move 5.5 retr 60% Z VWAP_D 4496.6 ext 4497.0 (j=36504) |
| 2026-09-22 22:12 | 2026-09-23 05:12 | BUY | 4401.5 | 4398.9 | 4406.7 | VWAP_D | SL | -1.08 | move 8.1 retr 44% Z VWAP_D 4399.7 ext 4399.2 (j=58059) |
| 2026-10-04 23:55 | 2026-10-05 06:55 | SELL | 4169.3 | 4170.9 | 4166.1 | VWAP_D | SL | -1.13 | move 5.4 retr 37% Z VWAP_D 4170.3 ext 4170.6 (j=69047) |
| 2026-10-07 17:44 | 2026-10-08 00:44 | SELL | 4137.3 | 4139.3 | 4133.3 | VWAP_D | SL | -1.10 | move 5.0 retr 46% Z VWAP_D 4137.7 ext 4139.0 (j=72852) |
| 2026-10-16 00:59 | 2026-10-16 07:59 | BUY | 4177.2 | 4174.9 | 4181.8 | POC_Y | SL | -1.09 | move 5.1 retr 69% Z POC_Y 4175.6 ext 4175.2 (j=81507) |

### File 90d (GCZ26, 2026-07-23 -> 2026-10-21) - V2 either+CFmem (min_move 5, retr <= 70%, TP 2R)

Lenh da dong: **11** (con mo 0). Lenh/ngay (tren 61 phien sach): **0.17**. Theo phase: A 0.115 - EU 0.016 - US 0.049 (US 19:00-23:00 VN: 0.016)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 11 | 36.4% | 0.00 | 0.36 | 0.0 | 2 |
| BUY | 6 | 33.3% | -0.08 | 0.12 | -0.5 | 3 |
| SELL | 5 | 40.0% | 0.10 | 0.66 | 0.5 | 2 |
| Tong @TP 3R | 11 | 9.1% | -0.72 | -1.33 | -8.0 | 8 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2026-08 | 2 | 50.0% | 0.43 | 1.10 | 0.9 | 1 |
| 2026-09 | 3 | 33.3% | -0.09 | 0.80 | -0.3 | 2 |
| 2026-10 | 6 | 33.3% | -0.10 | -0.10 | -0.6 | 2 |

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 7 | 14.3% | -0.66 | -1.34 | -4.6 | 6 |
| EU | 1 | 100.0% | 1.93 | 5.60 | 1.9 | 0 |
| US | 3 | 66.7% | 0.91 | 2.60 | 2.7 | 1 |

**TRAIN (<= 2026-09-15) / TEST (>= 2026-09-16)**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| TRAIN | 3 | 66.7% | 0.94 | 3.07 | 2.8 | 1 |
| TRAIN BUY | 2 | 50.0% | 0.43 | 1.10 | 0.9 | 1 |
| TRAIN SELL | 1 | 100.0% | 1.94 | 7.00 | 1.9 | 0 |
| TEST | 8 | 25.0% | -0.35 | -0.65 | -2.8 | 2 |
| TEST BUY | 4 | 25.0% | -0.34 | -0.38 | -1.4 | 2 |
| TEST SELL | 4 | 25.0% | -0.36 | -0.92 | -1.4 | 2 |

> **TEST chi co n=8 < 30: CHUA KET LUAN duoc o nua TEST.**

**Theo vung Z**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| POC_Y | 2 | 50.0% | 0.42 | 1.55 | 0.8 | 1 |
| VAL_EU | 1 | 100.0% | 1.88 | 3.00 | 1.9 | 0 |
| VAL_Y | 2 | 50.0% | 0.43 | 1.45 | 0.9 | 1 |
| VWAP_D | 6 | 16.7% | -0.59 | -0.83 | -3.5 | 4 |

**Luoi 3x3 (V2 either+CFmem, TP 2R, toan bo thoi gian)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=9 WR 22% R -0.45 | n=30 WR 43% R 0.20 | n=42 WR 45% R 0.27 |
| 5 gia | n=4 WR 25% R -0.36 | n=11 WR 36% R 0.00 | n=18 WR 44% R 0.25 |
| 7 gia | n=1 WR 0% R -1.08 | n=3 WR 33% R -0.08 | n=5 WR 40% R 0.12 |

**Luoi 3x3 theo TRAIN/TEST (V2 either+CFmem)** (R TB; TRAIN / TEST; n TEST)

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | - / -0.45 (n 9) | 0.53 / -0.05 (n 17) | 0.72 / -0.14 (n 22) |
| 5 gia | - / -0.36 (n 4) | 0.94 / -0.35 (n 8) | 1.07 / -0.27 (n 11) |
| 7 gia | - / -1.08 (n 1) | - / -0.08 (n 3) | 0.41 / -0.08 (n 3) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 281 -> co nen CF trong 3 nen 53 -> loai splice/thin/OFF 3 -> loai BALANCE 11 -> loai 3 nen sau nen dai nhat 0 -> loai nguoc bias 25 -> loai SL > 4 gia 3 -> vao lenh (truoc luat 1 lenh mo) 11

**Doi chung (V2 either+CFmem)**

- cau hinh 5/70%: that R TB **0.00** (n=11) | doi chung 200 lan: R TB -0.14 (5-95%: -0.82 .. 0.54); P(doi chung >= that) = **0.29**

**5 vi du THANG (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-06 23:46 | 2026-08-07 06:46 | BUY | 4306.0 | 4303.1 | 4311.8 | VAL_Y | TP | 1.93 | move 5.7 retr 65% Z VAL_Y 4302.4 ext 4303.4 (j=13424) |
| 2026-09-15 14:26 | 2026-09-15 21:26 | SELL | 4327.2 | 4330.8 | 4320.0 | VWAP_D | TP | 1.94 | move 6.5 retr 63% Z VWAP_D 4329.1 ext 4329.7 (j=50924) |
| 2026-10-01 07:38 | 2026-10-01 14:38 | BUY | 4192.1 | 4189.2 | 4197.9 | POC_Y | TP | 1.93 | move 7.5 retr 69% Z POC_Y 4189.2 ext 4189.8 (j=66750) |
| 2026-10-12 18:56 | 2026-10-13 01:56 | SELL | 4191.6 | 4193.2 | 4188.4 | VAL_EU | TP | 1.88 | move 6.1 retr 39% Z VAL_EU 4193.6 ext 4192.9 (j=77064) |

**5 vi du THUA (rai deu theo thoi gian, khong chon loc)**

| UTC | VN | side | vao | SL | TP | Z | ket qua | R | ghi chu |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-31 23:57 | 2026-09-01 06:57 | BUY | 4499.9 | 4496.7 | 4506.3 | VWAP_D | SL | -1.06 | move 5.5 retr 60% Z VWAP_D 4496.6 ext 4497.0 (j=36504) |
| 2026-09-22 22:12 | 2026-09-23 05:12 | BUY | 4401.5 | 4398.9 | 4406.7 | VWAP_D | SL | -1.08 | move 8.1 retr 44% Z VWAP_D 4399.7 ext 4399.2 (j=58059) |
| 2026-10-04 23:55 | 2026-10-05 06:55 | SELL | 4169.3 | 4170.9 | 4166.1 | VWAP_D | SL | -1.13 | move 5.4 retr 37% Z VWAP_D 4170.3 ext 4170.6 (j=69047) |
| 2026-10-07 17:44 | 2026-10-08 00:44 | SELL | 4137.3 | 4139.3 | 4133.3 | VWAP_D | SL | -1.10 | move 5.0 retr 46% Z VWAP_D 4137.7 ext 4139.0 (j=72852) |
| 2026-10-16 00:59 | 2026-10-16 07:59 | BUY | 4177.2 | 4174.9 | 4181.8 | POC_Y | SL | -1.09 | move 5.1 retr 69% Z POC_Y 4175.6 ext 4175.2 (j=81507) |

## File 2 nam (loc splice +-2 phien, volume o duoc tinh tu per-level that)

### 2 nam - delta (5 gia, retr <= 70%, TP 2R)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 50 | 34.0% | -0.09 | 0.08 | -4.7 | 6 |
| BUY | 28 | 39.3% | 0.06 | 0.34 | 1.7 | 4 |
| SELL | 22 | 27.3% | -0.29 | -0.24 | -6.4 | 5 |
| Nua 1 (2024-08 -> 2025-07) | 35 | 31.4% | -0.18 | -0.08 | -6.2 | 6 |
|   nua 1 BUY | 17 | 35.3% | -0.06 | 0.02 | -1.1 | 4 |
|   nua 1 SELL | 18 | 27.8% | -0.28 | -0.18 | -5.1 | 5 |
| Nua 2 (2025-08 -> 2026-08) | 15 | 40.0% | 0.10 | 0.47 | 1.5 | 5 |
|   nua 2 BUY | 11 | 45.5% | 0.25 | 0.83 | 2.8 | 3 |
|   nua 2 SELL | 4 | 25.0% | -0.32 | -0.50 | -1.3 | 2 |

Lenh/ngay (492 phien sach): 0.102; theo phase A 0.053 EU 0.039 US 0.010

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 26 | 30.8% | -0.19 | -0.12 | -5.0 | 7 |
| EU | 19 | 42.1% | 0.15 | 0.67 | 2.8 | 4 |
| US | 5 | 20.0% | -0.50 | -1.12 | -2.5 | 4 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 6 | 33.3% | -0.13 | -0.20 | -0.8 | 2 |
| 2024-09 | 1 | 100.0% | 1.90 | 3.80 | 1.9 | 0 |
| 2024-10 | 1 | 0.0% | -1.12 | -1.80 | -1.1 | 1 |
| 2024-11 | 3 | 0.0% | -1.17 | -1.50 | -3.5 | 3 |
| 2024-12 | 2 | 0.0% | -1.13 | -1.80 | -2.3 | 2 |
| 2025-01 | 2 | 100.0% | 1.87 | 3.10 | 3.7 | 0 |
| 2025-02 | 5 | 20.0% | -0.52 | -0.96 | -2.6 | 4 |
| 2025-03 | 4 | 25.0% | -0.37 | -0.58 | -1.5 | 2 |
| 2025-04 | 1 | 100.0% | 1.91 | 4.40 | 1.9 | 0 |
| 2025-05 | 2 | 50.0% | 0.43 | 2.30 | 0.9 | 1 |
| 2025-06 | 4 | 25.0% | -0.38 | -0.55 | -1.5 | 3 |
| 2025-07 | 4 | 25.0% | -0.33 | -0.37 | -1.3 | 2 |
| 2025-09 | 6 | 33.3% | -0.10 | -0.47 | -0.6 | 4 |
| 2025-10 | 3 | 66.7% | 0.89 | 2.20 | 2.7 | 1 |
| 2025-12 | 3 | 66.7% | 0.90 | 3.37 | 2.7 | 1 |
| 2026-02 | 1 | 0.0% | -1.13 | -1.70 | -1.1 | 1 |
| 2026-06 | 1 | 0.0% | -1.12 | -1.80 | -1.1 | 1 |
| 2026-07 | 1 | 0.0% | -1.06 | -3.30 | -1.1 | 1 |

**Luoi 3x3 (2 nam, delta)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=34 WR 32% R -0.14 | n=77 WR 34% R -0.10 | n=122 WR 34% R -0.10 |
| 5 gia | n=25 WR 36% R -0.03 | n=50 WR 34% R -0.09 | n=69 WR 35% R -0.06 |
| 7 gia | n=7 WR 57% R 0.62 | n=11 WR 55% R 0.54 | n=14 WR 50% R 0.41 |

**Luoi 3x3 R TB: nua 1 / nua 2 (delta)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | -0.31 (n26) / 0.40 (n8) | -0.18 (n48) / 0.04 (n29) | -0.15 (n71) / -0.03 (n51) |
| 5 gia | -0.29 (n18) / 0.62 (n7) | -0.18 (n35) / 0.10 (n15) | -0.09 (n41) / -0.02 (n28) |
| 7 gia | 0.39 (n2) / 0.71 (n5) | 0.41 (n4) / 0.62 (n7) | 0.41 (n4) / 0.41 (n10) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 1587 -> co nen CF trong 3 nen 180 -> loai splice/thin/OFF 15 -> loai BALANCE 17 -> loai 3 nen sau nen dai nhat 5 -> loai nguoc bias 85 -> loai SL > 4 gia 8 -> vao lenh (truoc luat 1 lenh mo) 50

**Doi chung 2 nam (delta)**

- cau hinh 5/70%: that R TB **-0.09** (n=50) | doi chung 200 lan: R TB -0.23 (5-95%: -0.50 .. 0.06); P(doi chung >= that) = **0.21**

### 2 nam - cell (5 gia, retr <= 70%, TP 2R)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 18 | 22.2% | -0.45 | -0.88 | -8.1 | 5 |
| BUY | 11 | 9.1% | -0.84 | -1.66 | -9.2 | 7 |
| SELL | 7 | 42.9% | 0.17 | 0.34 | 1.2 | 1 |
| Nua 1 (2024-08 -> 2025-07) | 11 | 18.2% | -0.59 | -0.99 | -6.4 | 5 |
|   nua 1 BUY | 6 | 0.0% | -1.13 | -1.90 | -6.8 | 6 |
|   nua 1 SELL | 5 | 40.0% | 0.06 | 0.10 | 0.3 | 1 |
| Nua 2 (2025-08 -> 2026-08) | 7 | 28.6% | -0.23 | -0.71 | -1.6 | 2 |
|   nua 2 BUY | 5 | 20.0% | -0.50 | -1.38 | -2.5 | 3 |
|   nua 2 SELL | 2 | 50.0% | 0.43 | 0.95 | 0.9 | 1 |

Lenh/ngay (492 phien sach): 0.037; theo phase A 0.020 EU 0.012 US 0.004

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 10 | 20.0% | -0.52 | -1.27 | -5.2 | 3 |
| EU | 6 | 0.0% | -1.12 | -1.97 | -6.7 | 6 |
| US | 2 | 100.0% | 1.91 | 4.30 | 3.8 | 0 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 1 | 0.0% | -1.13 | -1.80 | -1.1 | 1 |
| 2024-10 | 2 | 0.0% | -1.12 | -1.80 | -2.2 | 2 |
| 2024-11 | 1 | 100.0% | 1.89 | 3.40 | 1.9 | 0 |
| 2025-01 | 2 | 0.0% | -1.09 | -2.45 | -2.2 | 2 |
| 2025-02 | 1 | 0.0% | -1.15 | -1.50 | -1.2 | 1 |
| 2025-03 | 2 | 0.0% | -1.13 | -1.85 | -2.3 | 2 |
| 2025-05 | 1 | 100.0% | 1.85 | 2.40 | 1.8 | 0 |
| 2025-07 | 1 | 0.0% | -1.20 | -1.20 | -1.2 | 1 |
| 2025-09 | 2 | 50.0% | 0.38 | 0.90 | 0.8 | 1 |
| 2025-11 | 1 | 0.0% | -1.05 | -4.00 | -1.1 | 1 |
| 2025-12 | 1 | 0.0% | -1.08 | -2.80 | -1.1 | 1 |
| 2026-03 | 1 | 100.0% | 1.93 | 5.20 | 1.9 | 0 |
| 2026-04 | 1 | 0.0% | -1.12 | -1.90 | -1.1 | 1 |
| 2026-07 | 1 | 0.0% | -1.06 | -3.30 | -1.1 | 1 |

**Luoi 3x3 (2 nam, cell)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=10 WR 30% R -0.21 | n=27 WR 33% R -0.11 | n=47 WR 36% R -0.02 |
| 5 gia | n=8 WR 12% R -0.74 | n=18 WR 22% R -0.45 | n=27 WR 26% R -0.33 |
| 7 gia | n=0 WR -% R - | n=2 WR 0% R -1.06 | n=5 WR 40% R 0.13 |

**Luoi 3x3 R TB: nua 1 / nua 2 (cell)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | -0.37 (n8) / 0.39 (n2) | -0.19 (n16) / 0.00 (n11) | -0.13 (n24) / 0.09 (n23) |
| 5 gia | -0.69 (n7) / -1.12 (n1) | -0.59 (n11) / -0.23 (n7) | -0.53 (n15) / -0.08 (n12) |
| 7 gia | - (n0) / - (n0) | - (n0) / -1.06 (n2) | - (n0) / 0.13 (n5) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 568 -> co nen CF trong 3 nen 53 -> loai splice/thin/OFF 6 -> loai BALANCE 5 -> loai 3 nen sau nen dai nhat 2 -> loai nguoc bias 20 -> loai SL > 4 gia 2 -> vao lenh (truoc luat 1 lenh mo) 18

**Doi chung 2 nam (cell)**

- cau hinh 5/70%: that R TB **-0.45** (n=18) | doi chung 200 lan: R TB -0.22 (5-95%: -0.75 .. 0.33); P(doi chung >= that) = **0.74**

### 2 nam - V1 delta+CFmem (5 gia, retr <= 70%, TP 2R)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 117 | 29.1% | -0.24 | -0.44 | -28.2 | 10 |
| BUY | 67 | 26.9% | -0.31 | -0.65 | -20.6 | 11 |
| SELL | 50 | 32.0% | -0.15 | -0.16 | -7.6 | 6 |
| Nua 1 (2024-08 -> 2025-07) | 71 | 33.8% | -0.11 | -0.13 | -7.8 | 9 |
|   nua 1 BUY | 39 | 30.8% | -0.20 | -0.37 | -7.8 | 9 |
|   nua 1 SELL | 32 | 37.5% | -0.00 | 0.16 | -0.0 | 6 |
| Nua 2 (2025-08 -> 2026-08) | 46 | 21.7% | -0.44 | -0.91 | -20.4 | 10 |
|   nua 2 BUY | 28 | 21.4% | -0.46 | -1.03 | -12.8 | 11 |
|   nua 2 SELL | 18 | 22.2% | -0.42 | -0.73 | -7.6 | 5 |

Lenh/ngay (492 phien sach): 0.238; theo phase A 0.104 EU 0.073 US 0.061

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 51 | 25.5% | -0.36 | -0.64 | -18.1 | 9 |
| EU | 36 | 36.1% | -0.03 | 0.11 | -1.0 | 6 |
| US | 30 | 26.7% | -0.30 | -0.76 | -9.1 | 12 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 11 | 27.3% | -0.31 | -0.75 | -3.5 | 5 |
| 2024-09 | 1 | 100.0% | 1.87 | 2.80 | 1.9 | 0 |
| 2024-10 | 3 | 33.3% | -0.13 | -0.37 | -0.4 | 2 |
| 2024-11 | 6 | 33.3% | -0.15 | -0.27 | -0.9 | 4 |
| 2024-12 | 3 | 33.3% | -0.14 | -0.43 | -0.4 | 2 |
| 2025-01 | 5 | 20.0% | -0.52 | -0.96 | -2.6 | 4 |
| 2025-02 | 6 | 16.7% | -0.62 | -1.10 | -3.7 | 5 |
| 2025-03 | 6 | 50.0% | 0.35 | 0.40 | 2.1 | 2 |
| 2025-04 | 8 | 50.0% | 0.40 | 1.01 | 3.2 | 2 |
| 2025-05 | 3 | 66.7% | 0.92 | 2.37 | 2.7 | 1 |
| 2025-06 | 12 | 33.3% | -0.12 | 0.25 | -1.4 | 5 |
| 2025-07 | 7 | 14.3% | -0.69 | -1.31 | -4.8 | 4 |
| 2025-08 | 4 | 0.0% | -1.10 | -2.25 | -4.4 | 4 |
| 2025-09 | 10 | 30.0% | -0.20 | -0.56 | -2.0 | 6 |
| 2025-10 | 2 | 100.0% | 1.90 | 4.30 | 3.8 | 0 |
| 2025-11 | 1 | 0.0% | -1.06 | -3.30 | -1.1 | 1 |
| 2025-12 | 9 | 22.2% | -0.43 | -0.52 | -3.9 | 4 |
| 2026-01 | 2 | 0.0% | -1.09 | -2.65 | -2.2 | 2 |
| 2026-02 | 5 | 0.0% | -1.08 | -2.74 | -5.4 | 5 |
| 2026-03 | 1 | 0.0% | -1.11 | -2.00 | -1.1 | 1 |
| 2026-04 | 2 | 50.0% | 0.42 | 0.70 | 0.8 | 1 |
| 2026-05 | 1 | 0.0% | -1.10 | -2.30 | -1.1 | 1 |
| 2026-06 | 5 | 40.0% | 0.10 | 0.86 | 0.5 | 3 |
| 2026-07 | 4 | 0.0% | -1.10 | -2.60 | -4.4 | 4 |

**Luoi 3x3 (2 nam, V1 delta+CFmem)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=89 WR 28% R -0.28 | n=194 WR 30% R -0.20 | n=284 WR 31% R -0.17 |
| 5 gia | n=63 WR 25% R -0.35 | n=117 WR 29% R -0.24 | n=156 WR 31% R -0.18 |
| 7 gia | n=20 WR 25% R -0.36 | n=29 WR 28% R -0.28 | n=35 WR 26% R -0.33 |

**Luoi 3x3 R TB: nua 1 / nua 2 (V1 delta+CFmem)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | -0.32 (n52) / -0.21 (n37) | -0.14 (n107) / -0.27 (n87) | -0.14 (n149) / -0.20 (n135) |
| 5 gia | -0.32 (n37) / -0.41 (n26) | -0.11 (n71) / -0.44 (n46) | -0.05 (n78) / -0.32 (n78) |
| 7 gia | -0.75 (n8) / -0.10 (n12) | -0.42 (n13) / -0.16 (n16) | -0.46 (n14) / -0.24 (n21) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 1576 -> co nen CF trong 3 nen 395 -> loai splice/thin/OFF 35 -> loai BALANCE 61 -> loai 3 nen sau nen dai nhat 5 -> loai nguoc bias 160 -> loai SL > 4 gia 17 -> vao lenh (truoc luat 1 lenh mo) 117

**Doi chung 2 nam (V1 delta+CFmem)**

- cau hinh 5/70%: that R TB **-0.24** (n=117) | doi chung 200 lan: R TB -0.20 (5-95%: -0.43 .. 0.03); P(doi chung >= that) = **0.63**

### 2 nam - V2 either+CFmem (5 gia, retr <= 70%, TP 2R)

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 134 | 28.4% | -0.26 | -0.51 | -35.1 | 11 |
| BUY | 75 | 26.7% | -0.31 | -0.66 | -23.4 | 12 |
| SELL | 59 | 30.5% | -0.20 | -0.33 | -11.7 | 7 |
| Nua 1 (2024-08 -> 2025-07) | 79 | 34.2% | -0.10 | -0.10 | -7.9 | 9 |
|   nua 1 BUY | 42 | 31.0% | -0.19 | -0.33 | -8.1 | 6 |
|   nua 1 SELL | 37 | 37.8% | 0.01 | 0.17 | 0.2 | 6 |
| Nua 2 (2025-08 -> 2026-08) | 55 | 20.0% | -0.49 | -1.11 | -27.2 | 11 |
|   nua 2 BUY | 33 | 21.2% | -0.46 | -1.08 | -15.3 | 12 |
|   nua 2 SELL | 22 | 18.2% | -0.54 | -1.16 | -11.9 | 5 |

Lenh/ngay (492 phien sach): 0.272; theo phase A 0.118 EU 0.085 US 0.069

**Theo phase**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| A | 58 | 25.9% | -0.34 | -0.68 | -19.9 | 10 |
| EU | 42 | 33.3% | -0.11 | -0.04 | -4.7 | 6 |
| US | 34 | 26.5% | -0.31 | -0.82 | -10.5 | 14 |

**Theo thang**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| 2024-08 | 12 | 25.0% | -0.38 | -0.84 | -4.6 | 6 |
| 2024-09 | 1 | 100.0% | 1.87 | 2.80 | 1.9 | 0 |
| 2024-10 | 4 | 25.0% | -0.38 | -0.72 | -1.5 | 3 |
| 2024-11 | 7 | 42.9% | 0.15 | 0.26 | 1.0 | 4 |
| 2024-12 | 3 | 33.3% | -0.14 | -0.43 | -0.4 | 2 |
| 2025-01 | 7 | 28.6% | -0.26 | -0.39 | -1.8 | 4 |
| 2025-02 | 6 | 16.7% | -0.63 | -1.07 | -3.8 | 5 |
| 2025-03 | 6 | 50.0% | 0.35 | 0.40 | 2.1 | 2 |
| 2025-04 | 8 | 50.0% | 0.40 | 1.01 | 3.2 | 2 |
| 2025-05 | 5 | 60.0% | 0.69 | 1.58 | 3.4 | 1 |
| 2025-06 | 12 | 33.3% | -0.12 | 0.25 | -1.4 | 5 |
| 2025-07 | 8 | 12.5% | -0.75 | -1.30 | -6.0 | 4 |
| 2025-08 | 5 | 0.0% | -1.10 | -2.28 | -5.5 | 5 |
| 2025-09 | 11 | 36.4% | -0.01 | -0.18 | -0.1 | 4 |
| 2025-10 | 2 | 100.0% | 1.90 | 4.30 | 3.8 | 0 |
| 2025-11 | 2 | 0.0% | -1.06 | -3.65 | -2.1 | 2 |
| 2025-12 | 10 | 20.0% | -0.50 | -0.67 | -5.0 | 5 |
| 2026-01 | 2 | 0.0% | -1.09 | -2.65 | -2.2 | 2 |
| 2026-02 | 6 | 0.0% | -1.08 | -2.92 | -6.5 | 6 |
| 2026-03 | 1 | 0.0% | -1.11 | -2.00 | -1.1 | 1 |
| 2026-04 | 3 | 33.3% | -0.10 | -0.17 | -0.3 | 2 |
| 2026-05 | 2 | 0.0% | -1.09 | -2.40 | -2.2 | 2 |
| 2026-06 | 6 | 33.3% | -0.09 | 0.08 | -0.5 | 4 |
| 2026-07 | 5 | 0.0% | -1.10 | -2.54 | -5.5 | 5 |

**Luoi 3x3 (2 nam, V2 either+CFmem)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=102 WR 28% R -0.26 | n=225 WR 30% R -0.21 | n=331 WR 32% R -0.15 |
| 5 gia | n=73 WR 25% R -0.38 | n=134 WR 28% R -0.26 | n=181 WR 30% R -0.19 |
| 7 gia | n=22 WR 23% R -0.43 | n=32 WR 25% R -0.35 | n=39 WR 26% R -0.33 |

**Luoi 3x3 R TB: nua 1 / nua 2 (V2 either+CFmem)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | -0.28 (n60) / -0.24 (n42) | -0.10 (n120) / -0.32 (n105) | -0.09 (n172) / -0.20 (n159) |
| 5 gia | -0.29 (n43) / -0.50 (n30) | -0.10 (n79) / -0.49 (n55) | -0.05 (n92) / -0.35 (n89) |
| 7 gia | -0.83 (n10) / -0.10 (n12) | -0.51 (n15) / -0.21 (n17) | -0.54 (n16) / -0.18 (n23) |

Pheu (5/70%): bay + o Z (move>=5, hoi<=70%) 2051 -> co nen CF trong 3 nen 446 -> loai splice/thin/OFF 41 -> loai BALANCE 67 -> loai 3 nen sau nen dai nhat 5 -> loai nguoc bias 181 -> loai SL > 4 gia 18 -> vao lenh (truoc luat 1 lenh mo) 134

**Doi chung 2 nam (V2 either+CFmem)**

- cau hinh 5/70%: that R TB **-0.26** (n=134) | doi chung 200 lan: R TB -0.19 (5-95%: -0.38 .. 0.00); P(doi chung >= that) = **0.72**

## VONG 2 - bo yeu cau vung Z (V3, V4)

V3 = delta, CF chat, KHONG can Z, them loc sideway phase A/Au (bien do 60 nen gan nhat < 2 x u, u = trung vi bien do 50 nen => loai). Luoi 3x3 nhu cu. V4 = V3 voi luoi move {3,4,5} x hoi {50,70%}. Cung seed 0, doi chung 200 lan. Chi tiet in cho cau hinh: V3 5/70%, V4 3/70% (o co n lon nhat - chon vi muc tieu V4 la xem n).

### V3 - file 90d

**Luoi V3 90d (R TB tong | TRAIN / TEST)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=17 R -0.39 | TRAIN -0.43 (n9) / TEST -0.35 (n8) | n=52 R -0.17 | TRAIN -0.13 (n28) / TEST -0.22 (n24) | n=78 R -0.05 | TRAIN 0.07 (n44) / TEST -0.21 (n34) |
| 5 gia | n=13 R -0.41 | TRAIN -0.24 (n7) / TEST -0.60 (n6) | n=31 R 0.08 | TRAIN 0.42 (n16) / TEST -0.29 (n15) | n=44 R 0.01 | TRAIN 0.23 (n23) / TEST -0.23 (n21) |
| 7 gia | n=8 R -0.73 | TRAIN -0.12 (n3) / TEST -1.09 (n5) | n=13 R -0.40 | TRAIN 0.11 (n5) / TEST -0.71 (n8) | n=15 R -0.28 | TRAIN -0.09 (n6) / TEST -0.42 (n9) |

Chi tiet cau hinh (move 5, hoi <= 70%): 

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 31 | 38.7% | 0.08 | 0.70 | 2.4 | 5 |
| BUY | 20 | 35.0% | -0.04 | 0.31 | -0.8 | 5 |
| SELL | 11 | 45.5% | 0.28 | 1.39 | 3.1 | 2 |
| TRAIN | 16 | 50.0% | 0.42 | 1.69 | 6.7 | 3 |
| TEST | 15 | 26.7% | -0.29 | -0.37 | -4.4 | 5 |
| Phase A (0.311 lenh/ngay) | 19 | 42.1% | 0.18 | 0.95 | 3.3 | 3 |
| Phase EU (0.098 lenh/ngay) | 6 | 50.0% | 0.42 | 1.82 | 2.5 | 2 |
| Phase US (0.098 lenh/ngay) | 6 | 16.7% | -0.58 | -1.23 | -3.5 | 3 |
| TRAIN BUY | 10 | 50.0% | 0.42 | 1.41 | 4.2 | 2 |
| TRAIN SELL | 6 | 50.0% | 0.43 | 2.17 | 2.6 | 2 |
| TEST BUY | 10 | 20.0% | -0.49 | -0.78 | -4.9 | 5 |
| TEST SELL | 5 | 40.0% | 0.11 | 0.46 | 0.5 | 2 |

Lenh/ngay tong: 0.508 (61 phien sach). TEST/nua 2 n=15 (< 30: CHUA KET LUAN)

Pheu: bay (move+hoi+delta that bai) 1200 -> co nen CF chat trong 3 nen 91 -> loai splice/thin/OFF 6 -> loai BALANCE (che do) 7 -> loai 3 nen sau nen dai nhat 1 -> loai sideway A/Au (60 nen < 2u) 0 -> loai nguoc bias 38 -> loai SL > 4 gia 8 -> vao lenh (truoc luat 1 lenh mo) 31

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **0.08** (n=31) | doi chung 200 lan: R TB -0.05 (5-95%: -0.43 .. 0.36); P(doi chung >= that) = **0.28**

### V3 - file 2 nam

**Luoi V3 2 nam (R TB tong | nua 1 / nua 2)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=162 R -0.28 | nua 1 -0.26 (n102) / nua 2 -0.30 (n60) | n=419 R -0.16 | nua 1 -0.14 (n235) / nua 2 -0.18 (n184) | n=647 R -0.12 | nua 1 -0.16 (n332) / nua 2 -0.08 (n315) |
| 5 gia | n=118 R -0.17 | nua 1 -0.23 (n78) / nua 2 -0.05 (n40) | n=257 R -0.12 | nua 1 -0.17 (n151) / nua 2 -0.04 (n106) | n=366 R -0.11 | nua 1 -0.17 (n196) / nua 2 -0.04 (n170) |
| 7 gia | n=38 R 0.01 | nua 1 0.02 (n24) / nua 2 -0.02 (n14) | n=65 R 0.15 | nua 1 0.01 (n38) / nua 2 0.36 (n27) | n=86 R 0.10 | nua 1 0.02 (n43) / nua 2 0.17 (n43) |

Chi tiet cau hinh (move 5, hoi <= 70%): 

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 257 | 32.7% | -0.12 | -0.18 | -29.9 | 7 |
| BUY | 156 | 32.1% | -0.14 | -0.35 | -21.2 | 8 |
| SELL | 101 | 33.7% | -0.09 | 0.08 | -8.7 | 6 |
| nua 1 | 151 | 31.1% | -0.17 | -0.26 | -25.8 | 7 |
| nua 2 | 106 | 34.9% | -0.04 | -0.07 | -4.1 | 6 |
| Phase A (0.171 lenh/ngay) | 84 | 33.3% | -0.10 | -0.04 | -8.4 | 6 |
| Phase EU (0.215 lenh/ngay) | 106 | 34.9% | -0.05 | 0.01 | -5.4 | 7 |
| Phase US (0.136 lenh/ngay) | 67 | 28.4% | -0.24 | -0.67 | -16.1 | 8 |
| nua 1 BUY | 88 | 30.7% | -0.18 | -0.44 | -16.1 | 8 |
| nua 1 SELL | 63 | 31.7% | -0.15 | 0.00 | -9.7 | 5 |
| nua 2 BUY | 68 | 33.8% | -0.07 | -0.24 | -5.1 | 7 |
| nua 2 SELL | 38 | 36.8% | 0.03 | 0.22 | 1.0 | 6 |

Lenh/ngay tong: 0.522 (492 phien sach). TEST/nua 2 n=106

Pheu: bay (move+hoi+delta that bai) 8043 -> co nen CF chat trong 3 nen 729 -> loai splice/thin/OFF 48 -> loai BALANCE (che do) 53 -> loai 3 nen sau nen dai nhat 8 -> loai sideway A/Au (60 nen < 2u) 0 -> loai nguoc bias 325 -> loai SL > 4 gia 38 -> vao lenh (truoc luat 1 lenh mo) 257

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **-0.12** (n=257) | doi chung 200 lan: R TB -0.16 (5-95%: -0.31 .. -0.01); P(doi chung >= that) = **0.35**

### V4 - file 90d

**Luoi V4 90d (R TB tong | TRAIN / TEST)**

| min_move \ retr max | 50% | 70% |
|---|---|---|
| 3 gia | n=19 R -0.47 | TRAIN -0.56 (n11) / TEST -0.35 (n8) | n=60 R -0.29 | TRAIN -0.32 (n35) / TEST -0.25 (n25) |
| 4 gia | n=17 R -0.39 | TRAIN -0.43 (n9) / TEST -0.35 (n8) | n=52 R -0.17 | TRAIN -0.13 (n28) / TEST -0.22 (n24) |
| 5 gia | n=13 R -0.41 | TRAIN -0.24 (n7) / TEST -0.60 (n6) | n=31 R 0.08 | TRAIN 0.42 (n16) / TEST -0.29 (n15) |

Chi tiet cau hinh (move 3, hoi <= 70%): 

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 60 | 26.7% | -0.29 | -0.35 | -17.6 | 8 |
| BUY | 35 | 25.7% | -0.32 | -0.41 | -11.2 | 8 |
| SELL | 25 | 28.0% | -0.26 | -0.28 | -6.4 | 9 |
| TRAIN | 35 | 25.7% | -0.32 | -0.18 | -11.3 | 8 |
| TEST | 25 | 28.0% | -0.25 | -0.60 | -6.3 | 6 |
| Phase A (0.475 lenh/ngay) | 29 | 37.9% | 0.04 | 0.48 | 1.2 | 4 |
| Phase EU (0.279 lenh/ngay) | 17 | 23.5% | -0.38 | -0.68 | -6.4 | 8 |
| Phase US (0.230 lenh/ngay) | 14 | 7.1% | -0.88 | -1.69 | -12.4 | 9 |
| TRAIN BUY | 20 | 30.0% | -0.19 | -0.03 | -3.9 | 5 |
| TRAIN SELL | 15 | 20.0% | -0.49 | -0.39 | -7.4 | 9 |
| TEST BUY | 15 | 20.0% | -0.49 | -0.93 | -7.3 | 8 |
| TEST SELL | 10 | 40.0% | 0.10 | -0.11 | 1.0 | 4 |

Lenh/ngay tong: 0.984 (61 phien sach). TEST/nua 2 n=25 (< 30: CHUA KET LUAN)

Pheu: bay (move+hoi+delta that bai) 2580 -> co nen CF chat trong 3 nen 154 -> loai splice/thin/OFF 10 -> loai BALANCE (che do) 9 -> loai 3 nen sau nen dai nhat 1 -> loai sideway A/Au (60 nen < 2u) 0 -> loai nguoc bias 64 -> loai SL > 4 gia 8 -> vao lenh (truoc luat 1 lenh mo) 62

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **-0.29** (n=60) | doi chung 200 lan: R TB -0.10 (5-95%: -0.40 .. 0.25); P(doi chung >= that) = **0.81**

### V4 - file 2 nam

**Luoi V4 2 nam (R TB tong | nua 1 / nua 2)**

| min_move \ retr max | 50% | 70% |
|---|---|---|
| 3 gia | n=165 R -0.27 | nua 1 -0.26 (n102) / nua 2 -0.29 (n63) | n=532 R -0.14 | nua 1 -0.13 (n308) / nua 2 -0.14 (n224) |
| 4 gia | n=162 R -0.28 | nua 1 -0.26 (n102) / nua 2 -0.30 (n60) | n=419 R -0.16 | nua 1 -0.14 (n235) / nua 2 -0.18 (n184) |
| 5 gia | n=118 R -0.17 | nua 1 -0.23 (n78) / nua 2 -0.05 (n40) | n=257 R -0.12 | nua 1 -0.17 (n151) / nua 2 -0.04 (n106) |

Chi tiet cau hinh (move 3, hoi <= 70%): 

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| Tong | 532 | 32.3% | -0.14 | -0.28 | -73.0 | 14 |
| BUY | 323 | 34.1% | -0.09 | -0.27 | -27.6 | 12 |
| SELL | 209 | 29.7% | -0.22 | -0.31 | -45.4 | 10 |
| nua 1 | 308 | 32.8% | -0.13 | -0.24 | -40.9 | 10 |
| nua 2 | 224 | 31.7% | -0.14 | -0.33 | -32.1 | 14 |
| Phase A (0.360 lenh/ngay) | 177 | 31.6% | -0.16 | -0.25 | -28.5 | 7 |
| Phase EU (0.415 lenh/ngay) | 204 | 34.3% | -0.08 | -0.21 | -16.0 | 9 |
| Phase US (0.307 lenh/ngay) | 151 | 30.5% | -0.19 | -0.41 | -28.5 | 11 |
| nua 1 BUY | 185 | 35.1% | -0.06 | -0.24 | -11.6 | 12 |
| nua 1 SELL | 123 | 29.3% | -0.24 | -0.25 | -29.3 | 10 |
| nua 2 BUY | 138 | 32.6% | -0.12 | -0.30 | -16.0 | 10 |
| nua 2 SELL | 86 | 30.2% | -0.19 | -0.39 | -16.1 | 10 |

Lenh/ngay tong: 1.081 (492 phien sach). TEST/nua 2 n=224

Pheu: bay (move+hoi+delta that bai) 18670 -> co nen CF chat trong 3 nen 1388 -> loai splice/thin/OFF 87 -> loai BALANCE (che do) 111 -> loai 3 nen sau nen dai nhat 11 -> loai sideway A/Au (60 nen < 2u) 0 -> loai nguoc bias 600 -> loai SL > 4 gia 39 -> vao lenh (truoc luat 1 lenh mo) 540

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **-0.14** (n=532) | doi chung 200 lan: R TB -0.17 (5-95%: -0.26 .. -0.07); P(doi chung >= that) = **0.34**

## Đánh giá trung thực (viết tay sau khi đọc số ở trên)

**Kết luận một dòng: chưa có lợi thế đo được. Trap (D) theo định nghĩa plan 3-D cho ~0,1 lệnh/ngày, WR 34% ở 2R (hòa vốn cần ~37%), kỳ vọng âm nhẹ trên 2 năm và n quá nhỏ ở mọi nửa thời gian.**

1. **Số lệnh quá ít để kết luận.** File 90d: 7 lệnh (0,11/ngày), TEST chỉ **4 lệnh** (<30: chưa kết luận). Phễu cho thấy chỗ chết: trong 216 lần "bẫy + ô ở Z" chỉ 22 có nến CF chặt trong 3 nến, rồi bias, BALANCE, SL>4 giá còn 7. 2 năm: 50 lệnh (0,10/ngày). So với mục tiêu 10–20 lệnh/ngày, D đóng góp ~1%.
2. **Lợi thế thật?** 2 năm, delta, cấu hình 5 giá / hồi ≤70%: R TB **−0,09**, WR 34,0%. Đối chứng 200 lần (cùng vùng/chế độ/chiều, cùng R:R): −0,23 (5–95%: −0,50..+0,06); P(đối chứng ≥ thật) = 0,21. Tức setup *có thể* hơn ngẫu nhiên ~0,14R nhưng chưa vượt ngưỡng 5% và vẫn âm tuyệt đối. Cách `cell` (ô volume ≥2× trung vị): 18 lệnh, R −0,45, đối chứng P=0,74 ⇒ **không có gì**; 90d chỉ 2 lệnh (cả hai thua).
3. **Bất đối xứng BUY/SELL (đúng như phép đo cũ báo trước):** 2 năm delta BUY n=28 R +0,06 / SELL n=22 R −0,29; nửa 2 BUY +0,25 (n=11) / SELL −0,32 (n=4). Không tách được "BUY trap thật mạnh hơn" khỏi "vàng 2 năm tăng nên mọi BUY đều đỡ". Không dùng làm cơ sở tắt/bật một chiều.
4. **Ô nào bền cả hai nửa?** Chỉ hàng "move ≥7 giá" của lưới 2 năm dương ở cả hai nửa (retr 70%: +0,41 n=4 / +0,62 n=7), nhưng tổng **n=11** và trên file 90d cùng ô đó TRAIN −1,05 (n=1) / TEST −0,08 (n=3; file 90d trùng 4 tuần cuối của nửa 2 nên không độc lập). Hàng xóm "5 giá" gần như bằng 0 hoặc âm. ⇒ **không chọn ô nào**: ô tốt nhất mà n=11 và hàng xóm xấu là dấu hiệu khớp quá mức, đúng cảnh báo plan 4.6.
5. **Theo phase (2 năm, delta):** Á n=26 R −0,19 · Âu n=19 R **+0,15** · Mỹ n=5 R −0,50. Gợi ý cơ chế (chưa kiểm định): luật "loại chế độ BALANCE" chỉ có hiệu lực **sau 19:00 VN** (trước đó chế độ = NA vì chưa có band VA Âu/IB), nên ở Á/Âu bẫy trong sideway **không bị lọc** — đúng lỗi 24/9 mà RULES.md mục B muốn loại. Á là phase tệ nhất, khớp giả thuyết này.
6. **Hai biến thể cơ chế (chốt trước khi xem kết quả biến thể, chọn vì phễu cho thấy CF chặt quá hiếm):**
   - V1 *delta + CF mềm* (nến đóng theo S **vượt đỉnh/đáy nến bẫy** thay vì CF chặt |Δ| ≥ trung vị): 117 lệnh (0,24/ngày), R **−0,24**, nửa 1 −0,11 / nửa 2 −0,44, đối chứng P=0,63. Tệ hơn bản chặt, âm ở cả hai nửa.
   - V2 *delta hoặc ô lớn + CF mềm*: 134 lệnh, R **−0,26**, nửa 1 −0,10 / nửa 2 −0,49, đối chứng P=0,72.
   ⇒ Nới CF để có thêm lệnh chỉ **thêm lệnh thua**: bằng chứng (yếu) rằng thông tin nằm ở nến CF chặt (|Δ| lớn), không nằm ở "giá vượt nến bẫy" (đó là đuổi giá sau khi nhịp hồi đã đi xong). Cả hai biến thể bị loại.
7. **Đề xuất sửa định nghĩa (chưa chạy, mỗi cái kèm cơ chế):**
   - Thêm bộ lọc sideway cho phase Á/Âu (vd biên độ 60 nến gần nhất < 1,5× trung vị biên độ move, hoặc VA phiên trước hẹp): cơ chế = bẫy chỉ có nghĩa khi có người bị nhốt theo xu hướng, mà trong sideway không có xu hướng.
   - Gộp D vào setup A/B thay vì chạy riêng: trap tại VWAP ngày/POC hôm qua trùng vùng B (hấp thụ ở VWAP), chia dữ liệu mỏng thêm là vô nghĩa với n này.
   - Chỉ khi có dữ liệu mã/kỳ khác (n ≥100 lệnh) mới thử "move ≥7 giá": hiện chỉ là giả thuyết từ 11 lệnh.
8. **Khuyến nghị theo QĐ-5:** D có WR 34% < 50% ở 2R và không dương rõ ở cả hai nửa ⇒ **tắt mặc định** trong indicator (giữ công tắc), dùng như *đọc chart* (nhãn "có bẫy ở Z"), **không** code thành signal vào lệnh.
9. **Giới hạn của phép đo này:** (a) zigzag 2 giá + hằng số cố định (move hình thành ≤30 nến, hồi ≤30 nến và ≥1 giá, CF trong 3 nến sau nến cực trị, Z cách cực trị ≤1 giá) là lựa chọn của mình, không có trong plan — đổi các hằng này sẽ đổi n; (b) 1 lệnh mở cùng lúc nên một số lệnh bị bỏ; (c) bias lấy một lần ở đầu phase (đúng yêu cầu) nên phase dài có bias cũ; (d) file 90d và 2 năm trùng 4 tuần, không coi là hai mẫu độc lập; (e) 3R còn tệ hơn 2R trên 90d (WR 14%, n=7) nên không có lý do nới TP.

