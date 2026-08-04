# Bai lam #43 — Tích lũy (ACC)

- Anh: `range_43.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-09 00:54:00 -> 2026-07-09 06:22:00** = 328 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4079.2, VSA=2.69x, bien do nen=3.3 gia.
- MOVE truoc climax: dai 17.4 gia, 39 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4079.2 - 4088.2 = 9.0 gia (0.22% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4065.9 - 4092.3 = 26.4 gia.
- Ty le bien phu/bien chinh: **2.93x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.72x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.12, ty le volume nhip cuoi/dau=0.86 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 86553..86556 (2026-07-09 02:55:00), effort(VSA TB)=1.87x, result(bien do/ATR)=2.00, ty le er=0.94 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-09 00:54:00 | 2026-07-09 01:07:00 | 14 |
| B | 2026-07-09 01:08:00 | 2026-07-09 05:22:00 | 255 |
| C | 2026-07-09 05:23:00 | 2026-07-09 05:59:00 | 37 |
| D | 2026-07-09 06:00:00 | 2026-07-09 06:11:00 | 12 |
| E | 2026-07-09 06:12:00 | 2026-07-09 06:22:00 | 11 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-09 01:00:00 | 4080.6 | A | - | 4.72x | 0.22 |
| AR | 2026-07-09 01:01:00 | 4088.2 | A | - | 2.93x | 0.43 |
| ST[A] | 2026-07-09 01:07:00 | 4076.1 | A | - | 0.75x | 0.30 |
| mSOW | 2026-07-09 04:44:00 | 4065.9 | B | - | 3.67x | 0.74 |
| LPS[C] | 2026-07-09 05:23:00 | 4078.3 | C | - | 0.11x | 0.50 |
| mSOS | 2026-07-09 05:51:00 | 4092.3 | B | - | 2.07x | 0.52 |
| SOS | 2026-07-09 06:00:00 | 4108.5 | D | - | 8.08x | 0.93 |
| LPS[D] | 2026-07-09 06:07:00 | 4097.8 | D | - | 0.56x | 0.55 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-09 00:48:00 | 4087.6 | 4088.1 | 4086.2 | 4086.2 | 18 | 0.47x | 0.74 |
| -5 | 2026-07-09 00:49:00 | 4086.8 | 4087.2 | 4086.8 | 4087.0 | 3 | 0.08x | 0.50 |
| -4 | 2026-07-09 00:50:00 | 4087.1 | 4087.1 | 4084.3 | 4084.4 | 28 | 0.76x | 0.96 |
| -3 | 2026-07-09 00:51:00 | 4084.5 | 4085.4 | 4083.0 | 4083.5 | 45 | 1.20x | 0.42 |
| -2 | 2026-07-09 00:52:00 | 4083.2 | 4083.3 | 4081.7 | 4083.3 | 42 | 1.10x | 0.06 |
| -1 | 2026-07-09 00:53:00 | 4083.5 | 4083.7 | 4082.7 | 4082.8 | 11 | 0.32x | 0.70 |
| +0 **<- climax** | 2026-07-09 00:54:00 | 4082.5 | 4082.5 | 4079.2 | 4079.8 | 104 | 2.69x | 0.82 |
| +1 | 2026-07-09 00:55:00 | 4079.8 | 4082.4 | 4079.8 | 4081.6 | 106 | 2.60x | 0.69 |
| +2 | 2026-07-09 00:56:00 | 4081.8 | 4084.4 | 4081.1 | 4084.4 | 48 | 1.17x | 0.79 |
| +3 | 2026-07-09 00:57:00 | 4084.1 | 4084.1 | 4082.1 | 4082.1 | 22 | 0.56x | 1.00 |
| +4 | 2026-07-09 00:58:00 | 4081.9 | 4083.3 | 4081.8 | 4082.8 | 46 | 1.32x | 0.60 |
| +5 | 2026-07-09 00:59:00 | 4082.5 | 4083.5 | 4082.0 | 4082.8 | 36 | 1.07x | 0.20 |
