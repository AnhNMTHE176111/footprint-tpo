# KERNEL-CHECK (kernel.py, sinh boi kernel_check.py)

File: `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (GCZ26, mot hop dong). Gio trong file = UTC; cot VN = UTC+7.

## 1. So lieu co ban (file 90d)

- So nen M1: **86333**; so phien (tach khi trong > 30 phut): **65** (phien dau 324 nen = du lieu bat dau giua phien; phien cuoi 865 nen = dang chay)
- Trung vi volume/phien: **133471** hop dong (plan ghi 133.471); trung vi nen/phien: 1379
- Phien `thin` (volume < 20% trung vi): **4** -> 2026-07-23, 2026-07-24, 2026-07-27, 2026-07-28. Du lieu tuan dau (07-23..07-28) rat mong (volume 2.672..21.081 so voi trung vi 133.471) nen profile/VA cua cac phien do khong dang tin.
- Phien dinh cho noi: 0 (file 90d la mot hop dong nen = 0)
- Cac khoang trong > 30 phut: 61-62 phut (nghi 21:00-22:00 UTC) x49; cuoi tuan ~2941 phut x12; 3065 phut x1 (dau file, T6->T2); le Labor Day 2026-09-07 trong 211 phut (phien bi cat doi: phien 09-07 chi 1.220 nen); 72 phut ngay dau file.
- Profile dung tu per-level (that): 65 phien (full), 64 phien co cua so Au.
- Che do M1 (phan bo): NA=52862, TREND_DN=10842, TREND_UP=9791, BALANCE=9786, BREAK_DN=1756, BREAK_UP=1296
  (`NA` chiem da so vi truoc 19:00 VN chua co band VA Au/IB.)

## 2. Ba ngay mau tai 19:00 VN (nen dau tien co sm = 840, tuc 12:00 UTC)

VA Au chot dung luc nay (cua so 12:30-19:00 VN). IB 19:20-20:20 chi chot sau 20:20 nen o day in gia tri CUOI kem gio chot. VWAP tuan/ngay = cong don den nen 19:00 (typical price x volume).

### Phien 2026-08-12 (19:00 VN = 2026-08-12 12:00 UTC, pos 17985)

| muc | POC | VAH | VAL |
|---|---|---|---|
| VA Au hom nay | 4475.2 | 4478.4 | 4460.4 |
| VA hom qua (2026-08-11) | 4443.2 | 4459.2 | 4424.4 |

- IB 19:20-20:20 VN: cao **4502.7**, thap **4440.0** (chot luc 2026-08-12 13:20 UTC; luc 19:00 chua co => `as_of` tra None: True)
- VWAP tuan **4433.9**, VWAP ngay **4458.5**, close nen 19:00 = 4472.3
- HVN ngay (tu profile hom qua): khong co (khong du cong x2,5) | LVN ngay: 4482.8, 4493.2
- HVN tuan (gop 3 tuan da dong, 12 phien): 4105.4 (x3.7), 4135.4 (x3.5), 4091.0 (x3.0)
- POC tran (chua bi cham) tai 19:00: 4090.4 (phien 2026-08-03), 4254.0 (phien 2026-08-05), 4382.0 (phien 2026-08-10)

### Phien 2026-09-10 (19:00 VN = 2026-09-10 12:00 UTC, pos 46721)

| muc | POC | VAH | VAL |
|---|---|---|---|
| VA Au hom nay | 4437.6 | 4458.8 | 4415.2 |
| VA hom qua (2026-09-09) | 4445.6 | 4468.4 | 4433.2 |

- IB 19:20-20:20 VN: cao **4415.6**, thap **4365.4** (chot luc 2026-09-10 13:20 UTC; luc 19:00 chua co => `as_of` tra None: True)
- VWAP tuan **4445.5**, VWAP ngay **4448.1**, close nen 19:00 = 4415.6
- HVN ngay (tu profile hom qua): 4443.4 (x3.6) | LVN ngay: 4386.4, 4405.2
- HVN tuan (gop 3 tuan da dong, 15 phien): 4482.2 (x2.7)
- POC tran (chua bi cham) tai 19:00: 4254.0 (phien 2026-08-05), 4538.4 (phien 2026-09-03), 4515.6 (phien 2026-09-04)

### Phien 2026-10-14 (19:00 VN = 2026-10-14 12:00 UTC, pos 79410)

| muc | POC | VAH | VAL |
|---|---|---|---|
| VA Au hom nay | 4166.4 | 4176.4 | 4163.2 |
| VA hom qua (2026-10-13) | 4207.6 | 4217.6 | 4185.2 |

- IB 19:20-20:20 VN: cao **4179.9**, thap **4102.8** (chot luc 2026-10-14 13:20 UTC; luc 19:00 chua co => `as_of` tra None: True)
- VWAP tuan **4194.7**, VWAP ngay **4175.2**, close nen 19:00 = 4163.8
- HVN ngay (tu profile hom qua): khong co (khong du cong x2,5) | LVN ngay: 4224.4, 4171.2
- HVN tuan (gop 3 tuan da dong, 15 phien): 4190.2 (x3.7), 4168.2 (x2.8), 4207.4 (x2.7)
- POC tran (chua bi cham) tai 19:00: 4327.6 (phien 2026-09-25), 4148.4 (phien 2026-10-08), 4207.6 (phien 2026-10-13)

## 3. File 2 nam `fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv`

- So nen M1: 724279; so phien: **533**; trung vi volume/phien: 156121
- Cho noi hop dong phat hien (khoang nghi 30-150 phut va |open - close truoc| >= 20 gia): **8**
- Phien dinh cho noi (+-2 phien quanh moi cho noi): **40** phien bi loai, con **493** phien sach (README cu ghi 529 phien / 474 sach)
- Phien `thin` trong file 2 nam: 4

| gio UTC (nen sau cho noi) | close truoc | open sau | nhay |
|---|---|---|---|
| 2025-03-27 22:00 | 3069.1 | 3099.3 | +30.2 |
| 2025-04-22 22:00 | 3392.0 | 3367.7 | -24.3 |
| 2025-05-28 22:00 | 3284.4 | 3311.8 | +27.4 |
| 2025-07-29 22:00 | 3325.3 | 3383.1 | +57.8 |
| 2025-11-25 23:00 | 4126.3 | 4167.0 | +40.7 |
| 2026-01-28 23:00 | 5411.0 | 5449.9 | +38.9 |
| 2026-05-27 22:00 | 4454.9 | 4488.0 | +33.1 |
| 2026-07-29 22:00 | 4065.5 | 4126.7 | +61.2 |

- Co them **9** lan nhay 8-20 gia dung trong khoang nghi (2026-02 -> 2026-07, thi truong bien dong manh). KHONG coi la cho noi (nguong plan = 20 gia); nguong thap hon se ra ~17 cho noi, nhieu kha nang gom ca gap that. Tong 8 cho noi ro rang (+-24..+61 gia). README cu ghi 11 cho noi - khong tai lap duoc voi nguong 20.

- Pipeline 2 nam (profile xap xi tu nen, chi de kiem toc do/do ben, KHONG dung ket luan): 1.6 giay; che do M1: NA=445480, TREND_UP=93328, TREND_DN=78642, BALANCE=74228, BREAK_UP=17669, BREAK_DN=14932
- build_profiles tu per-level 2 nam (doc chunk 2 trieu dong): 4.7 giay, 533 phien co profile

## 4. Thoi gian chay (may nay)

| buoc | giay |
|---|---|
| load_bars 90d | 0.27 |
| build_profiles (per-level 1,5 trieu dong) | 0.71 |
| zone_columns | 0.06 |
| mode_frame (M5 + che do) | 0.05 |
| zigzag 2 gia | 0.05 |
| TONG pipeline 90d | 1.14 |
| load_bars 2 nam | 2.11 |
| pipeline 2 nam voi profile XAP XI (tu nen) | 1.63 |
| build_profiles 2 nam per-level (583 MB, doc chunk) | 4.73 |

## 5. Gia dinh va quy uoc (hang so nam o `CONST` dau kernel.py)

1. **VWAP = typical price (H+L+C)/3 x volume**, cong don; gom nen hien tai (nen da dong). Giong `ProfileEngine.VwapAt`, khong dung close x volume.
2. **VWAP tuan neo phien dau tien sau khoang trong > 30 gio**; VWAP ngay reset moi phien CME (khoang trong > 30 phut).
3. **datetime = gio MO nen M1.** M5 chi "da dong" khi `t5_end <= gio mo nen M1` dang xet, nen nen M1 thu 5 cua mot M5 chua thay M5 cua chinh no.
4. **Profile**: hang = 2 tick (0,2 gia), snap `round(gia/0,2)` (lam tron banker giong C#); VA chay tren cac hang DANG CO (khong lap hang trong, giong ProfileEngine.ValueArea).
5. **FindHvn/FindLvn port 1:1** (lam muot +-5 hang, gop dinh theo 8% do rong kep 20..120 tick, cong ti le 2,5, toi da 3 HVN / 2 LVN). KHAC `research/hap-thu-tai-vung.py` o find_lvn (script do dung nguong cach 2 gia co dinh; kernel theo ProfileEngine).
6. **Phien hom qua** = phien truoc gan nhat co >= 300 nen M1 (bo manh vun nghi le) va khong co cho noi chen giua. **HVN tuan** = gop cac phien thuoc 3 tuan CME da dong (tuan = khoang trong > 30 gio); neu co cho noi trong cua so chi lay phan SAU cho noi (`partial=True`).
7. **VA Au = nen co `sm` trong [450, 840)** (12:30-19:00 VN), chot tu sm >= 840, can >= 60 nen. **IB = sm [860, 920)** (19:20-20:20), can >= 30 nen, chot tu sm >= 920.
8. **Gio neo My (`us_dst_shift=True`)**: khi My dung gio mua dong (EST), cac moc 05:00/19:00/IB lui +1h theo gio VN de van bam gio mo cua My. File 90d toan mua he nen khong anh huong; muon moc VN co dinh nhu plan thi dat `CONST["us_dst_shift"]=False`. Moc A/EU 12:30 khong doi theo DST.
9. **Che do**: band = VA Au (sau 19:00), chua co thi IB (sau 20:20), truoc 19:00 VN = `NA` (gio A va EU chua co band, plan chua dinh nghia che do cho 2 phase nay). Nen M5 dong NGOAI roi dong LAI TRONG band => ve `BALANCE` (pha hut). `TREND` = >= 2 nen M5 lien tiep ngoai cung phia va nen gan nhat cach canh >= 3 gia; con lai co nen ngoai = `BREAK_*`.
10. **naked POC**: POC (cua VA) cac phien trong 30 phien truoc chua bi gia cham (low <= POC <= high) sau khi phien do ket thuc; voi as_of -> toi da 3 gan nhat.
11. **simulate**: vao o `entry` tai nen `idx`, xet tu nen idx+1; cung nen SL va TP => SL; thoat dung gia SL/TP (khong tinh gap qua phien/cho noi - phai loc `splice` truoc); `one_at_a_time` cho lenh moi khi `idx >= exit_idx` cua lenh truoc.
12. **risk**: san = bien do nen M1 cao nhat 5 nen (gom nen vao), tran 4 gia => None; SL lam tron ra xa theo tick 0,1.
13. **zigzag**: neu day va dinh nam cung mot nen (khong biet thu tu) thi khoi dong chan tiep theo tu nen sau (bao thu). Reset moi phien.
14. Phien `thin` (volume < 20% trung vi) van duoc tra ve nhung co co `thin`; control_sample loai chung. Agent nen tu loc `thin` va `splice` khi do.
