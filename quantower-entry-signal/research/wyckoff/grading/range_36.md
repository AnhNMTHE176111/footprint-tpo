# Bai lam #36 — Tái phân phối (RE-DIST)

- Anh: `range_36.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-23 00:22:00 -> 2026-06-23 03:18:00** = 176 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4196.0, VSA=2.48x, bien do nen=4.3 gia.
- MOVE truoc climax: dai 17.6 gia, 44 nen, hieu suat huong 0.43.
- Bien CHINH (net lien, climax+AR): 4196.0 - 4212.7 = 16.7 gia (0.40% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4188.0 - 4216.0 = 28.0 gia.
- Ty le bien phu/bien chinh: **1.68x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.48x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.49, ty le volume nhip cuoi/dau=1.02 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 70159..70180 (2026-06-23 01:27:00), effort(VSA TB)=1.18x, result(bien do/ATR)=1.26, ty le er=0.94 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-23 00:22:00 | 2026-06-23 00:50:00 | 29 |
| B | 2026-06-23 00:51:00 | 2026-06-23 01:36:00 | 46 |
| D | 2026-06-23 01:37:00 | 2026-06-23 01:43:00 | 7 |
| E | 2026-06-23 01:44:00 | 2026-06-23 03:18:00 | 95 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-23 00:22:00 | 4196.0 | A | - | 2.48x | 0.88 |
| AR | 2026-06-23 00:45:00 | 4212.7 | A | - | 2.51x | 0.85 |
| ST[A] | 2026-06-23 00:50:00 | 4207.3 | A | - | 0.48x | 0.21 |
| mSOS | 2026-06-23 01:00:00 | 4216.0 | B | - | 5.23x | 0.06 |
| mSOW | 2026-06-23 01:21:00 | 4188.0 | B | - | 1.64x | 0.95 |
| SOW | 2026-06-23 01:37:00 | 4178.7 | D | - | 5.63x | 0.82 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-23 00:16:00 | 4198.6 | 4200.4 | 4198.4 | 4199.5 | 65 | 1.79x | 0.45 |
| -5 | 2026-06-23 00:17:00 | 4199.3 | 4199.7 | 4199.3 | 4199.3 | 7 | 0.19x | 0.00 |
| -4 | 2026-06-23 00:18:00 | 4199.4 | 4200.0 | 4197.9 | 4198.6 | 11 | 0.30x | 0.38 |
| -3 | 2026-06-23 00:19:00 | 4198.5 | 4200.0 | 4198.5 | 4199.8 | 16 | 0.44x | 0.87 |
| -2 | 2026-06-23 00:20:00 | 4199.9 | 4201.0 | 4198.6 | 4199.6 | 31 | 0.88x | 0.12 |
| -1 | 2026-06-23 00:21:00 | 4200.2 | 4200.8 | 4199.9 | 4200.7 | 15 | 0.46x | 0.56 |
| +0 **<- climax** | 2026-06-23 00:22:00 | 4199.9 | 4200.3 | 4196.0 | 4196.1 | 88 | 2.48x | 0.88 |
| +1 | 2026-06-23 00:23:00 | 4197.4 | 4197.7 | 4197.0 | 4197.0 | 10 | 0.28x | 0.57 |
| +2 | 2026-06-23 00:24:00 | 4197.4 | 4200.0 | 4197.4 | 4200.0 | 18 | 0.52x | 1.00 |
| +3 | 2026-06-23 00:25:00 | 4200.3 | 4201.2 | 4197.9 | 4198.9 | 55 | 1.47x | 0.42 |
| +4 | 2026-06-23 00:26:00 | 4198.6 | 4199.3 | 4198.6 | 4199.3 | 3 | 0.08x | 1.00 |
| +5 | 2026-06-23 00:27:00 | 4200.0 | 4203.3 | 4200.0 | 4200.0 | 69 | 1.82x | 0.00 |
