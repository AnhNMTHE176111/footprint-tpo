# Bai lam #42 — Tái phân phối (RE-DIST)

- Anh: `range_42.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-07 19:18:00 -> 2026-07-08 10:56:00** = 877 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4102.7, VSA=1.53x, bien do nen=9.7 gia.
- MOVE truoc climax: dai 46.2 gia, 107 nen, hieu suat huong 0.41.
- Bien CHINH (net lien, climax+AR): 4102.7 - 4125.9 = 23.2 gia (0.57% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4091.3 - 4144.7 = 53.4 gia.
- Ty le bien phu/bien chinh: **2.30x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.94x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.23, ty le volume nhip cuoi/dau=0.13 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 84810..84824 (2026-07-07 20:00:00), effort(VSA TB)=1.24x, result(bien do/ATR)=0.53, ty le er=2.33 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-07 19:18:00 | 2026-07-07 19:43:00 | 26 |
| B | 2026-07-07 19:44:00 | 2026-07-08 08:16:00 | 692 |
| C | 2026-07-08 08:17:00 | 2026-07-08 08:39:00 | 23 |
| D | 2026-07-08 08:40:00 | 2026-07-08 08:55:00 | 16 |
| E | 2026-07-08 08:56:00 | 2026-07-08 10:56:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-07 19:15:00 | 4107.3 | A | - | 2.94x | 0.82 |
| AR | 2026-07-07 19:35:00 | 4125.9 | A | - | 1.23x | 0.41 |
| ST[A] | 2026-07-07 19:43:00 | 4118.9 | A | - | 0.68x | 0.07 |
| mSOS | 2026-07-08 06:24:00 | 4144.7 | B | - | 1.68x | 0.20 |
| LPSY[C] | 2026-07-08 08:17:00 | 4117.7 | C | - | 10.06x | 0.88 |
| mSOW | 2026-07-08 08:18:00 | 4091.3 | B | - | 5.32x | 0.09 |
| SOW | 2026-07-08 08:40:00 | 4075.8 | D | - | 3.18x | 0.39 |
| LPSY[D] | 2026-07-08 08:48:00 | 4087.0 | D | - | 1.09x | 0.80 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-07 19:12:00 | 4116.1 | 4116.7 | 4113.6 | 4115.3 | 500 | 2.04x | 0.26 |
| -5 | 2026-07-07 19:13:00 | 4115.5 | 4119.9 | 4114.8 | 4117.8 | 263 | 1.07x | 0.45 |
| -4 | 2026-07-07 19:14:00 | 4117.8 | 4118.0 | 4115.6 | 4116.6 | 80 | 0.33x | 0.50 |
| -3 | 2026-07-07 19:15:00 | 4116.1 | 4116.3 | 4107.3 | 4108.7 | 823 | 2.94x | 0.82 |
| -2 | 2026-07-07 19:16:00 | 4108.9 | 4110.8 | 4107.5 | 4109.3 | 366 | 1.24x | 0.12 |
| -1 | 2026-07-07 19:17:00 | 4109.3 | 4114.6 | 4109.2 | 4112.5 | 316 | 1.03x | 0.59 |
| +0 **<- climax** | 2026-07-07 19:18:00 | 4112.2 | 4112.4 | 4102.7 | 4104.2 | 502 | 1.53x | 0.82 |
| +1 | 2026-07-07 19:19:00 | 4104.2 | 4110.2 | 4104.0 | 4109.4 | 179 | 0.54x | 0.84 |
| +2 | 2026-07-07 19:20:00 | 4109.3 | 4110.7 | 4104.2 | 4107.9 | 224 | 0.67x | 0.22 |
| +3 | 2026-07-07 19:21:00 | 4107.4 | 4109.2 | 4105.2 | 4108.0 | 306 | 0.94x | 0.15 |
| +4 | 2026-07-07 19:22:00 | 4108.5 | 4112.0 | 4108.5 | 4110.7 | 176 | 0.54x | 0.63 |
| +5 | 2026-07-07 19:23:00 | 4110.4 | 4112.4 | 4109.9 | 4112.2 | 250 | 0.75x | 0.72 |
