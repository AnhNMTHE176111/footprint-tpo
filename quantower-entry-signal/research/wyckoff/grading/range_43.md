# Bai lam #43 — Tái phân phối (RE-DIST)

- Anh: `range_43.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-07 19:18:00 -> 2026-07-08 10:57:00** = 878 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4102.7, VSA=1.53x, bien do nen=9.7 gia.
- MOVE truoc climax: dai 46.2 gia, 107 nen, hieu suat huong 0.41.
- Bien CHINH (net lien, climax+AR): 4102.7 - 4128.9 = 26.2 gia (0.64% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4091.3 - 4144.7 = 53.4 gia.
- Ty le bien phu/bien chinh: **2.04x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.94x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.71, ty le volume nhip cuoi/dau=1.12 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.23, ty le volume nhip cuoi/dau=0.13 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 85184..85201 (2026-07-08 03:18:00), effort(VSA TB)=1.43x, result(bien do/ATR)=1.58, ty le er=0.90 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-07 19:18:00 | 2026-07-07 20:23:00 | 66 |
| B | 2026-07-07 20:24:00 | 2026-07-08 08:02:00 | 638 |
| C | 2026-07-08 08:03:00 | 2026-07-08 08:39:00 | 37 |
| D | 2026-07-08 08:40:00 | 2026-07-08 08:56:00 | 17 |
| E | 2026-07-08 08:57:00 | 2026-07-08 10:57:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-07 19:15:00 | 4107.3 | A | - | 2.94x | 0.82 |
| AR | 2026-07-07 19:55:00 | 4128.9 | A | - | 3.74x | 0.32 |
| ST[A] | 2026-07-07 20:23:00 | 4117.3 | A | - | 0.38x | 0.54 |
| mSOS | 2026-07-08 06:24:00 | 4144.7 | B | - | 1.68x | 0.20 |
| LPSY[C] | 2026-07-08 08:03:00 | 4129.5 | C | - | 0.33x | 0.00 |
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
