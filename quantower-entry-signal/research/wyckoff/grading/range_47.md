# Bai lam #47 — Phân phối (DIST)

- Anh: `range_47.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-15 18:31:00 -> 2026-07-16 03:24:00** = 473 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4089.1, VSA=2.00x, bien do nen=4.1 gia.
- MOVE truoc climax: dai 49.8 gia, 107 nen, hieu suat huong 0.35.
- Bien CHINH (net lien, climax+AR): 4064.4 - 4089.1 = 24.7 gia (0.60% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4055.2 - 4089.1 = 33.9 gia.
- Ty le bien phu/bien chinh: **1.37x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.52x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.19, ty le volume nhip cuoi/dau=0.49 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 93215..93233 (2026-07-15 23:28:00), effort(VSA TB)=1.01x, result(bien do/ATR)=0.19, ty le er=5.25 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-15 18:31:00 | 2026-07-15 19:12:00 | 42 |
| B | 2026-07-15 19:13:00 | 2026-07-16 00:58:00 | 286 |
| D | 2026-07-16 00:59:00 | 2026-07-16 01:23:00 | 25 |
| E | 2026-07-16 01:24:00 | 2026-07-16 03:24:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-07-15 18:30:00 | 4086.6 | A | - | 4.52x | 0.81 |
| AR | 2026-07-15 19:00:00 | 4064.4 | A | - | 1.09x | 0.22 |
| ST[A] | 2026-07-15 19:12:00 | 4069.7 | A | - | 1.70x | 0.11 |
| mSOW | 2026-07-15 19:35:00 | 4055.2 | B | - | 2.29x | 0.43 |
| SOW | 2026-07-16 00:59:00 | 4050.4 | D | - | 4.46x | 0.81 |
| LPSY[D] | 2026-07-16 01:10:00 | 4055.1 | D | - | 0.82x | 0.29 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-15 18:25:00 | 4078.0 | 4079.5 | 4078.0 | 4078.2 | 80 | 1.10x | 0.13 |
| -5 | 2026-07-15 18:26:00 | 4078.5 | 4080.0 | 4076.8 | 4077.1 | 84 | 1.15x | 0.44 |
| -4 | 2026-07-15 18:27:00 | 4077.1 | 4078.6 | 4076.4 | 4078.5 | 164 | 2.36x | 0.64 |
| -3 | 2026-07-15 18:28:00 | 4078.6 | 4079.6 | 4078.2 | 4078.6 | 100 | 1.45x | 0.00 |
| -2 | 2026-07-15 18:29:00 | 4079.0 | 4082.8 | 4078.3 | 4081.3 | 254 | 3.32x | 0.51 |
| -1 | 2026-07-15 18:30:00 | 4081.7 | 4086.6 | 4081.4 | 4085.9 | 436 | 4.52x | 0.81 |
| +0 **<- climax** | 2026-07-15 18:31:00 | 4085.5 | 4089.1 | 4085.0 | 4087.2 | 204 | 2.00x | 0.41 |
| +1 | 2026-07-15 18:32:00 | 4086.9 | 4086.9 | 4081.2 | 4082.0 | 303 | 2.67x | 0.86 |
| +2 | 2026-07-15 18:33:00 | 4082.1 | 4083.8 | 4080.3 | 4080.5 | 174 | 1.45x | 0.46 |
| +3 | 2026-07-15 18:34:00 | 4081.1 | 4081.3 | 4079.2 | 4079.7 | 137 | 1.10x | 0.67 |
| +4 | 2026-07-15 18:35:00 | 4079.7 | 4080.1 | 4078.4 | 4080.1 | 74 | 0.58x | 0.24 |
| +5 | 2026-07-15 18:36:00 | 4079.7 | 4080.6 | 4078.9 | 4079.7 | 78 | 0.60x | 0.00 |
