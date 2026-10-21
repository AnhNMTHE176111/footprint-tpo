# RESULTS-D - Setup D Trap (sinh boi setup_d_trap.py, deterministic)

**QD-6: chi do tren file 90d GCZ26. Bang 2 nam cu nam o `RESULTS-D-2y-cu-tham-khao.md` va chi de tham khao (sai ma hop dong), khong dung quyet dinh.** Dinh nghia: plan 3-D. Hang so co dinh: move ro hinh thanh <= 30 nen; nhip hoi <= 30 nen, sau >= 1.0 gia; CF trong 3 nen sau nen cuc tri; Z cach cuc tri <= 1.0 gia hoac rau cham; o volume >= 2x trung vi o (>= 3 muc). Chi phi 0,2 gia/lenh, 1 lenh mo cung luc, SL = kernel.risk (cau truc = cuc tri nhip hoi). Gio UTC / VN = UTC+7. 2 tham so tu do: min_move x retr max (luoi 3x3).

## VONG 3 - V5 "cho gia roi bong bong" (QD-8, Corven)

Nen tang = V3 (khong Z, move >= 5 gia cung bias, hoi <= 70%, loc sideway A/Au vo hieu vi loai 0 ca). Bong bong = nen cuc tri hoi co (delta thuan chieu hoi ma dong nua phia S) HOAC o per-level o cuc tri >= 2x trung vi o (>= 3 muc). KHONG vao ngay sau CF: cho nen M1 DONG cach gia cuc tri hoi (muc bong bong) >= d theo chieu move cu, toi da 10 nen; vao o gia dong nen do; SL = cuc tri nhip hoi (thap/cao nhat tu cuoi move den nen vao) + 0,3 (san/tran kernel.risk, > 4 gia loai); TP 2R/3R tu gia vao moi. Tham so duy nhat d in {1,0 gia ; bien do nen bong bong ; 1u (trung vi bien do 50 nen)}. Cau hinh move 5, hoi 70%, 90d, doi chung 200 lan seed 0, bootstrap 10.000 lan. Bang chinh dung 1 lenh mo cung luc; phan so sanh V3/V5 ben duoi dung simulate khong gioi han (de moi nen bay deu co ket qua).

**V3 tham chieu (cung cau hinh, CF chat ngay):**

| | n | WR | R TB | ky vong (gia/lenh) | tong R | chuoi thua dai nhat |
|---|---|---|---|---|---|---|
| V3 5/70% TP 2R | 31 | 38.7% | 0.08 | 0.70 | 2.4 | 5 |

| d | n | WR | R TB (2R) | TRAIN R (n) | TEST R (n) | R TB @3R | bootstrap 95% (2R) | doi chung P | BUY R (n) | SELL R (n) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1,0 gia | 193 | 34.2% | -0.06 | -0.03 (106) | -0.09 (87) | -0.15 | -0.06 [-0.26 .. 0.15] | 0.37 | -0.06 (94) | -0.05 (99) |
| bien do nen bong bong | 161 | 35.4% | -0.03 | 0.05 (87) | -0.12 (74) | 0.04 | -0.03 [-0.25 .. 0.20] | 0.23 | -0.08 (83) | 0.03 (78) |
| 1u | 148 | 31.1% | -0.15 | -0.25 (76) | -0.04 (72) | -0.18 | -0.15 [-0.37 .. 0.08] | 0.76 | -0.20 (78) | -0.10 (70) |

Ghi chu: TEST n < 30 => chua ket luan.

### So V5 voi V3 tren cung tap nen bay

V3 co 31 lenh (thang 12, thua 19). Moi lenh V3 gan voi cap (day,dinh) cua move; xem V5 lam gi voi chinh cap do (V5 co the vao o bong bong khac, som hon, cua cung cap; V5 con co them lenh o cap ma V3 khong co CF).

- (d = 1,0 gia) Trong 19 lenh thua cua V3, 10 lenh bi SL roi trong 60 nen sau do gia VAN cham TP cu cua V3 (dau hieu bi quet rau): V5 cho chinh cac cap do: khong vao 0, vao & thang 1, vao & thua 9.
- **d = 1,0 gia**: V5 (khong gioi han) 196 lenh, trong do 87 lenh phai dat SL thap hon muc bong bong vi gia da quet them truoc khi vao. V3 THUA 19 ca -> V5 vao & THANG 2, vao & thua 17, khong vao (tranh duoc) 0. V3 THANG 12 ca -> V5 vao & thang 11, vao & thua 1, khong vao (bo lo) 0. Ly do V5 khong vao (thang/thua cua V3 / trang thai): -
- (d = bien do nen bong bong) Trong 19 lenh thua cua V3, 10 lenh bi SL roi trong 60 nen sau do gia VAN cham TP cu cua V3 (dau hieu bi quet rau): V5 cho chinh cac cap do: khong vao 1, vao & thang 0, vao & thua 9.
- **d = bien do nen bong bong**: V5 (khong gioi han) 163 lenh, trong do 74 lenh phai dat SL thap hon muc bong bong vi gia da quet them truoc khi vao. V3 THUA 19 ca -> V5 vao & THANG 1, vao & thua 17, khong vao (tranh duoc) 1. V3 THANG 12 ca -> V5 vao & thang 10, vao & thua 1, khong vao (bo lo) 1. Ly do V5 khong vao (thang/thua cua V3 / trang thai): thang/past_top=1, thua/timeout=1
- (d = 1u) Trong 19 lenh thua cua V3, 10 lenh bi SL roi trong 60 nen sau do gia VAN cham TP cu cua V3 (dau hieu bi quet rau): V5 cho chinh cac cap do: khong vao 0, vao & thang 1, vao & thua 9.
- **d = 1u**: V5 (khong gioi han) 150 lenh, trong do 66 lenh phai dat SL thap hon muc bong bong vi gia da quet them truoc khi vao. V3 THUA 19 ca -> V5 vao & THANG 2, vao & thua 17, khong vao (tranh duoc) 0. V3 THANG 12 ca -> V5 vao & thang 10, vao & thua 1, khong vao (bo lo) 1. Ly do V5 khong vao (thang/thua cua V3 / trang thai): thang/past_top=1

**Ket luan vong 3 (viet tay tu so tren):** V5 KHONG cai thien. (1) Bo CF chat (dung nghia "khong vao ngay sau bong bong") lam so lenh tang 5-6 lan (148-193 so voi V3 31) va R TB ve ~0 am (-0,03 den -0,15; bootstrap bao tron 0, TEST n=72-87 nhung R am o ca ba d; doi chung P 0,23-0,76 = khong hon ngau nhien). (2) Tren cung cac cap (day,dinh): V3 thua 19, V5 van thua 17 (d=1 gia, 1u) hoac 17 (bien do); chi 1-2 ca duoc cuu. Trong 10 ca V3 bi quet SL roi gia van cham TP cu, V5 vao va van thua 9 ca (d=1 gia, 1u) hoac 9 + 1 khong vao (bien do): cho gia roi 1 gia khong tranh duoc quet vi gia con hoi lai nua; 87 / 74 / 66 lenh V5 phai dat SL thap hon muc bong bong (da bi quet truoc khi vao). (3) V5 bo lo it: chi 0-1 trong 12 ca V3 thang khong vao (past_top / timeout) nhung V5 cung bien 1 ca V3 thang thanh thua. (4) Phep do khong ung ho QD-8 tren du lieu 90d: ca thuc 11/10 la 1 ca, khong chung minh quy luat. D van tat mac dinh, chi doc chart.

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

- Bootstrap 95% (10000 lan) R TB delta 5/70%: **0.20** [-0.70 .. 1.49], n=7

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

- Bootstrap 95% (10000 lan) R TB cell 5/70%: **-1.12** [-1.12 .. -1.12], n=2

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

- Bootstrap 95% (10000 lan) R TB V1 delta+CFmem 5/70%: **0.12** [-0.79 .. 1.02], n=10

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

- Bootstrap 95% (10000 lan) R TB V2 either+CFmem 5/70%: **0.00** [-0.82 .. 0.83], n=11

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

## VONG 2 - bo yeu cau vung Z (V3, V4)

V3 = delta, CF chat, KHONG can Z, them loc sideway phase A/Au (bien do 60 nen gan nhat < 2 x u, u = trung vi bien do 50 nen => loai). Luoi 3x3 nhu cu. V4 = V3 voi luoi move {3,4,5} x hoi {50,70%}. Cung seed 0, doi chung 200 lan. Chi tiet in cho cau hinh: V3 5/70%, V4 3/70% (o co n lon nhat - chon vi muc tieu V4 la xem n).

### V3 - file 90d

**Luoi V3 90d (R TB tong ; TRAIN / TEST)**

| min_move \ retr max | 50% | 70% | 90% |
|---|---|---|---|
| 4 gia | n=17 R -0.39 ; TRAIN -0.43 (n9) / TEST -0.35 (n8) | n=52 R -0.17 ; TRAIN -0.13 (n28) / TEST -0.22 (n24) | n=78 R -0.05 ; TRAIN 0.07 (n44) / TEST -0.21 (n34) |
| 5 gia | n=13 R -0.41 ; TRAIN -0.24 (n7) / TEST -0.60 (n6) | n=31 R 0.08 ; TRAIN 0.42 (n16) / TEST -0.29 (n15) | n=44 R 0.01 ; TRAIN 0.23 (n23) / TEST -0.23 (n21) |
| 7 gia | n=8 R -0.73 ; TRAIN -0.12 (n3) / TEST -1.09 (n5) | n=13 R -0.40 ; TRAIN 0.11 (n5) / TEST -0.71 (n8) | n=15 R -0.28 ; TRAIN -0.09 (n6) / TEST -0.42 (n9) |

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

- Bootstrap 95% (10000 lan) R TB cau hinh chinh: **0.08** [-0.41 .. 0.57], n=31

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **0.08** (n=31) | doi chung 200 lan: R TB -0.05 (5-95%: -0.43 .. 0.36); P(doi chung >= that) = **0.28**

### V4 - file 90d

**Luoi V4 90d (R TB tong ; TRAIN / TEST)**

| min_move \ retr max | 50% | 70% |
|---|---|---|
| 3 gia | n=19 R -0.47 ; TRAIN -0.56 (n11) / TEST -0.35 (n8) | n=60 R -0.29 ; TRAIN -0.32 (n35) / TEST -0.25 (n25) |
| 4 gia | n=17 R -0.39 ; TRAIN -0.43 (n9) / TEST -0.35 (n8) | n=52 R -0.17 ; TRAIN -0.13 (n28) / TEST -0.22 (n24) |
| 5 gia | n=13 R -0.41 ; TRAIN -0.24 (n7) / TEST -0.60 (n6) | n=31 R 0.08 ; TRAIN 0.42 (n16) / TEST -0.29 (n15) |

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

- Bootstrap 95% (10000 lan) R TB cau hinh chinh: **-0.29** [-0.60 .. 0.06], n=60

**Doi chung**

- cung vung(khong co)/che do/chieu, 200 lan: that R TB **-0.29** (n=60) | doi chung 200 lan: R TB -0.10 (5-95%: -0.40 .. 0.25); P(doi chung >= that) = **0.81**

## Đánh giá trung thực (QĐ-6: chỉ file 90d GCZ26; bảng 2 năm cũ chỉ tham khảo)

**Kết luận cuối: D TẮT MẶC ĐỊNH, CHỈ ĐỌC CHART.** Không biến thể nào (vòng 1: delta, cell, V1, V2; vòng 2: V3, V4) cho kỳ vọng dương bền ở cả TRAIN lẫn TEST, và ở TEST luôn n < 30 hoặc âm.

1. **Số lệnh:** vòng 1 (cần vùng Z): 2–11 lệnh/90 ngày (≤0,18 lệnh/ngày), TEST chỉ 4–8 lệnh ⇒ chưa kết luận. Phễu: 216 lần bẫy tại Z → 22 có CF chặt → 7 lệnh. Vòng 2 (bỏ Z): V3 5/70% 31 lệnh (0,51/ngày), V4 3/70% 60 lệnh (0,98/ngày). Bỏ Z tăng n, nhưng vẫn xa mục tiêu 10–20 lệnh/ngày.
2. **Vòng 1, cấu hình 5/70%:** delta n=7 R +0,20 (TRAIN +0,94 n=3 / TEST −0,36 n=4); cell n=2, cả hai thua; V1 (CF mềm) n=10 R +0,12, TEST −0,24 (n=7); V2 n=11 R 0,00, TEST −0,35 (n=8). Mọi biến thể: TRAIN dương nhờ 2–3 lệnh, TEST âm — kiểu "tìm trên nửa đầu, chết ở nửa sau" mà plan 0 cảnh báo.
3. **V3 (không Z, loc sideway 60 nến ≥ 2u, 5/70%):** n=31, R +0,08, TRAIN +0,42 (n=16) / TEST −0,29 (n=15 < 30). Đối chứng 200 lần −0,05, P(đối chứng ≥ thật)=0,28 ⇒ không hơn ngẫu nhiên; khoảng tin cậy bootstrap ở bảng trên bao trùm 0 rất rộng. Theo phase: Á n=19 +0,18 · Âu n=6 +0,42 · Mỹ n=6 −0,58 (n quá nhỏ để tin). BUY −0,04 / SELL +0,28.
4. **V4 (3/70%):** n=60, R −0,29, TRAIN −0,32 / TEST −0,25 (n=25 < 30), đối chứng −0,10 (P=0,81: tệ hơn ngẫu nhiên). Cỡ move càng nhỏ (3→5 giá) R càng âm ở cả TRAIN và TEST: không ô nào của V4 dương ở cả hai nửa.
5. **Bộ lọc sideway đúng nguyên văn (biên độ 60 nến ≥ 2u) loại 0 ca** vì thỏa ở 99,9% số nến (biên độ 60 nến gần như luôn ≥ 2× biên độ trung vị 1 nến). Không nới/siết ngưỡng cho nó "có tác dụng" (sẽ thành tham số thứ ba). Nếu cần lọc sideway thật phải định nghĩa khác (vd biên độ 60 nến so với biên độ phiên trước).
6. **Ô nào bền cả hai nửa?** Không có. Ô V3 5/70% dương tổng (+0,08) nhưng TEST âm, hàng xóm 4 giá (−0,17) và 7 giá (−0,40) đều âm ⇒ khớp quá mức, không chọn.
7. **Bất đối xứng BUY/SELL:** quá nhiễu (n nhỏ), đảo chiều giữa các cấu hình; không kết luận.
8. **Đề xuất (chưa chạy, chỉ khi có thêm dữ liệu hợp lệ):** (a) lọc sideway bằng định nghĩa khác 60-nến/2u; (b) gộp D vào B vì cùng vùng VWAP; (c) thử move ≥7 giá khi có ≥100 lệnh. Hiện không có cơ sở bật D làm signal.
9. **Giới hạn:** hằng số tự chọn (move hình thành ≤30 nến, hồi ≤30 nến và ≥1 giá, CF trong 3 nến, Z cách cực trị ≤1 giá); 1 lệnh mở cùng lúc; bias lấy một lần đầu mỗi phase; mỗi cặp (đáy, đỉnh) zigzag vào tối đa 1 lệnh; 90 ngày chỉ là một hợp đồng, một thời kỳ giá. Bảng 2 năm trước QĐ-6 (cho kết luận cùng hướng: R −0,09 đến −0,26) nằm ở `RESULTS-D-2y-cu-tham-khao.md`, không dùng để quyết định.

