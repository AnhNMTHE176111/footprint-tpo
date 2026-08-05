# Bai lam #33 — Chưa rõ (SC) (ACC?)

- Anh: `range_33.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-15 12:18:00 -> 2026-06-15 20:46:00** = 508 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4345.3, VSA=1.68x, bien do nen=3.4 gia.
- MOVE truoc climax: dai 20.2 gia, 36 nen, hieu suat huong 0.51.
- Bien CHINH (net lien, climax+AR): 4345.3 - 4391.5 = 46.2 gia (1.06% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4339.1 - 4391.5 = 52.4 gia.
- Ty le bien phu/bien chinh: **1.13x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.20x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.62, ty le volume nhip cuoi/dau=1.13 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 63229..63267 (2026-06-15 20:00:00), effort(VSA TB)=1.21x, result(bien do/ATR)=1.15, ty le er=1.05 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-15 12:18:00 | 2026-06-15 15:02:00 | 165 |
| B | 2026-06-15 15:03:00 | 2026-06-15 20:20:00 | 318 |
| D | 2026-06-15 20:21:00 | 2026-06-15 20:46:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-15 12:20:00 | 4345.6 | A | - | 3.20x | 0.24 |
| AR | 2026-06-15 14:06:00 | 4391.5 | A | - | 1.81x | 0.54 |
| ST[A] | 2026-06-15 15:02:00 | 4373.0 | A | - | 1.25x | 0.33 |
| ST[B] | 2026-06-15 17:52:00 | 4341.7 | B | - | 0.60x | 0.52 |
| mSOW | 2026-06-15 19:22:00 | 4342.4 | B | - | 7.87x | 0.43 |
| SOW | 2026-06-15 20:21:00 | 4335.2 | D | - | 5.81x | 0.83 |
| LPSY[D] | 2026-06-15 20:28:00 | 4336.0 | D | - | 0.30x | 0.36 |

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
