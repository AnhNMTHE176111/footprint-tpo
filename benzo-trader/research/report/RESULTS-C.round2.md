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

