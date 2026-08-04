# Bai lam #46 — Tái phân phối (RE-DIST)

- Anh: `range_46.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-14 16:07:00 -> 2026-07-14 19:55:00** = 228 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4063.4, VSA=2.31x, bien do nen=5.2 gia.
- Bien CHINH (net lien, climax+AR): 4063.4 - 4072.3 = 8.9 gia (0.22% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4061.8 - 4072.3 = 10.5 gia.
- Ty le bien phu/bien chinh: **1.18x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.31x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.24, ty le volume nhip cuoi/dau=0.34 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 91645..91649 (2026-07-14 19:04:00), effort(VSA TB)=0.54x, result(bien do/ATR)=1.42, ty le er=0.38 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-14 16:07:00 | 2026-07-14 16:23:00 | 17 |
| B | 2026-07-14 16:24:00 | 2026-07-14 19:29:00 | 186 |
| D | 2026-07-14 19:30:00 | 2026-07-14 19:54:00 | 25 |
| E | 2026-07-14 19:55:00 | 2026-07-14 19:55:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-07-14 16:07:00 | 4063.4 | A | - | 2.31x | 0.54 |
| AR | 2026-07-14 16:16:00 | 4072.3 | A | - | 0.57x | 0.91 |
| ST[A] | 2026-07-14 16:23:00 | 4064.9 | A | - | 1.68x | 0.04 |
| mSOW | 2026-07-14 17:14:00 | 4061.8 | B | - | 2.93x | 0.26 |
| SOW | 2026-07-14 19:30:00 | 4055.6 | D | - | 5.87x | 0.87 |
| LPSY[D] | 2026-07-14 19:38:00 | 4058.8 | D | - | 0.96x | 0.62 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-14 16:01:00 | 4069.6 | 4071.3 | 4069.2 | 4069.5 | 148 | 0.92x | 0.05 |
| -5 | 2026-07-14 16:02:00 | 4069.8 | 4071.1 | 4069.2 | 4070.7 | 171 | 1.23x | 0.47 |
| -4 | 2026-07-14 16:03:00 | 4070.6 | 4071.1 | 4069.0 | 4070.3 | 71 | 0.52x | 0.14 |
| -3 | 2026-07-14 16:04:00 | 4070.5 | 4071.4 | 4068.9 | 4070.2 | 121 | 0.92x | 0.12 |
| -2 | 2026-07-14 16:05:00 | 4070.8 | 4070.8 | 4066.1 | 4066.9 | 292 | 2.07x | 0.83 |
| -1 | 2026-07-14 16:06:00 | 4066.7 | 4068.3 | 4066.2 | 4068.1 | 80 | 0.57x | 0.67 |
| +0 **<- climax** | 2026-07-14 16:07:00 | 4068.2 | 4068.6 | 4063.4 | 4065.4 | 355 | 2.31x | 0.54 |
| +1 | 2026-07-14 16:08:00 | 4066.0 | 4068.2 | 4065.3 | 4067.8 | 119 | 0.77x | 0.62 |
| +2 | 2026-07-14 16:09:00 | 4067.5 | 4069.8 | 4066.8 | 4067.1 | 168 | 1.07x | 0.13 |
| +3 | 2026-07-14 16:10:00 | 4068.2 | 4070.1 | 4068.2 | 4069.0 | 87 | 0.57x | 0.42 |
| +4 | 2026-07-14 16:11:00 | 4069.4 | 4070.5 | 4068.9 | 4070.5 | 81 | 0.57x | 0.69 |
| +5 | 2026-07-14 16:12:00 | 4070.6 | 4070.6 | 4069.3 | 4069.6 | 57 | 0.41x | 0.77 |
