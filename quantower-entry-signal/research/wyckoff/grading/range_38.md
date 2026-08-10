# Bai lam #38 — Chưa rõ (SC) (ACC?)

- Anh: `range_38.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-15 12:18:00 -> 2026-06-15 19:47:00** = 449 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4345.3, VSA=1.68x, bien do nen=3.4 gia.
- MOVE truoc climax: dai 20.2 gia, 36 nen, hieu suat huong 0.51.
- Bien CHINH (net lien, climax+AR): 4345.3 - 4391.5 = 46.2 gia (1.06% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4339.1 - 4391.5 = 52.4 gia.
- Ty le bien phu/bien chinh: **1.13x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.20x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.31, ty le volume nhip cuoi/dau=0.39 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 63227..63229 (2026-06-15 19:22:00), effort(VSA TB)=3.11x, result(bien do/ATR)=3.15, ty le er=0.99 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-15 12:18:00 | 2026-06-15 16:25:00 | 248 |
| B | 2026-06-15 16:26:00 | 2026-06-15 19:08:00 | 163 |
| C | 2026-06-15 19:09:00 | 2026-06-15 19:21:00 | 13 |
| D | 2026-06-15 19:22:00 | 2026-06-15 19:47:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-15 12:20:00 | 4345.6 | A | - | 3.20x | 0.24 |
| AR | 2026-06-15 14:06:00 | 4391.5 | A | - | 1.81x | 0.54 |
| ST[A] | 2026-06-15 16:25:00 | 4360.5 | A | - | 3.03x | 0.58 |
| ST[B] | 2026-06-15 17:52:00 | 4341.7 | B | - | 0.60x | 0.52 |
| mSOW | 2026-06-15 18:01:00 | 4341.6 | B | provisional | 2.63x | 0.59 |
| LPSY[C] | 2026-06-15 19:09:00 | 4345.1 | C | - | 1.30x | 0.14 |
| SOW | 2026-06-15 19:22:00 | 4343.9 | D | - | 7.87x | 0.43 |
| LPSY[D] | 2026-06-15 19:25:00 | 4345.6 | D | - | 0.44x | 0.50 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-15 12:12:00 | 4358.2 | 4358.2 | 4356.3 | 4357.5 | 83 | 1.41x | 0.37 |
| -5 | 2026-06-15 12:13:00 | 4357.1 | 4357.4 | 4355.4 | 4355.4 | 101 | 1.68x | 0.85 |
| -4 | 2026-06-15 12:14:00 | 4355.4 | 4355.7 | 4351.6 | 4352.2 | 194 | 2.88x | 0.78 |
| -3 | 2026-06-15 12:15:00 | 4352.3 | 4354.2 | 4351.1 | 4351.8 | 156 | 2.23x | 0.16 |
| -2 | 2026-06-15 12:16:00 | 4351.5 | 4351.9 | 4348.7 | 4349.8 | 187 | 2.42x | 0.53 |
| -1 | 2026-06-15 12:17:00 | 4349.6 | 4349.8 | 4345.5 | 4345.5 | 282 | 3.14x | 0.95 |
| +0 **<- climax** | 2026-06-15 12:18:00 | 4345.7 | 4348.7 | 4345.3 | 4348.4 | 162 | 1.68x | 0.79 |
| +1 | 2026-06-15 12:19:00 | 4348.3 | 4348.6 | 4346.8 | 4348.1 | 142 | 1.38x | 0.11 |
| +2 | 2026-06-15 12:20:00 | 4348.0 | 4348.9 | 4345.6 | 4348.8 | 376 | 3.20x | 0.24 |
| +3 | 2026-06-15 12:21:00 | 4349.1 | 4350.7 | 4348.6 | 4349.6 | 129 | 1.07x | 0.24 |
| +4 | 2026-06-15 12:22:00 | 4349.4 | 4351.8 | 4348.9 | 4351.6 | 117 | 0.94x | 0.76 |
| +5 | 2026-06-15 12:23:00 | 4351.6 | 4352.8 | 4351.1 | 4352.1 | 84 | 0.66x | 0.29 |
