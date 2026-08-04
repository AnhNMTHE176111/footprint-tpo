# Bai lam #17 — Phân phối (DIST)

- Anh: `range_17.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-14 04:36:00 -> 2026-05-14 14:01:00** = 352 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4753.0, VSA=0.91x, bien do nen=1.8 gia.
- MOVE truoc climax: dai 38.0 gia, 23 nen, hieu suat huong 0.86.
- Bien CHINH (net lien, climax+AR): 4735.0 - 4753.0 = 18.0 gia (0.38% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4728.8 - 4757.7 = 28.9 gia.
- Ty le bien phu/bien chinh: **1.61x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.33x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.28, ty le volume nhip cuoi/dau=0.91 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.32, ty le volume nhip cuoi/dau=0.32 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 34786..34794 (2026-05-14 07:02:00), effort(VSA TB)=0.97x, result(bien do/ATR)=3.91, ty le er=0.25 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-14 04:36:00 | 2026-05-14 05:48:00 | 30 |
| B | 2026-05-14 05:50:00 | 2026-05-14 13:13:00 | 277 |
| C | 2026-05-14 13:14:00 | 2026-05-14 13:29:00 | 14 |
| D | 2026-05-14 13:30:00 | 2026-05-14 13:54:00 | 25 |
| E | 2026-05-14 13:55:00 | 2026-05-14 14:01:00 | 7 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-05-14 04:32:00 | 4752.0 | A | - | 2.33x | 0.72 |
| AR | 2026-05-14 05:30:00 | 4735.0 | A | - | 4.17x | 1.00 |
| ST[A] | 2026-05-14 05:48:00 | 4743.3 | A | - | 0.42x | 0.00 |
| mSOW | 2026-05-14 06:02:00 | 4728.8 | B | - | 2.67x | 0.96 |
| mSOS | 2026-05-14 07:37:00 | 4757.7 | B | - | 0.65x | 0.00 |
| LPSY[C] | 2026-05-14 13:14:00 | 4746.4 | C | - | 0.35x | 0.00 |
| SOW | 2026-05-14 13:30:00 | 4727.1 | D | - | 6.12x | 0.38 |
| LPSY[D] | 2026-05-14 13:50:00 | 4731.4 | D | - | 1.59x | 0.60 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-14 04:27:00 | 4746.0 | 4746.0 | 4743.3 | 4745.3 | 5 | 1.03x | 0.26 |
| -5 | 2026-05-14 04:28:00 | 4743.3 | 4743.3 | 4742.1 | 4742.1 | 6 | 1.18x | 1.00 |
| -4 | 2026-05-14 04:29:00 | 4742.9 | 4745.2 | 4742.9 | 4743.8 | 5 | 0.94x | 0.39 |
| -3 | 2026-05-14 04:32:00 | 4747.0 | 4752.0 | 4747.0 | 4750.6 | 10 | 2.33x | 0.72 |
| -2 | 2026-05-14 04:33:00 | 4749.9 | 4750.3 | 4749.9 | 4750.3 | 2 | 0.49x | 1.00 |
| -1 | 2026-05-14 04:35:00 | 4750.4 | 4752.7 | 4750.4 | 4750.5 | 5 | 1.16x | 0.04 |
| +0 **<- climax** | 2026-05-14 04:36:00 | 4752.9 | 4753.0 | 4751.2 | 4751.2 | 4 | 0.91x | 0.94 |
| +1 | 2026-05-14 04:37:00 | 4749.7 | 4750.4 | 4749.6 | 4749.6 | 3 | 0.71x | 0.12 |
| +2 | 2026-05-14 04:38:00 | 4748.1 | 4748.7 | 4748.1 | 4748.7 | 2 | 0.48x | 1.00 |
| +3 | 2026-05-14 04:39:00 | 4748.5 | 4748.5 | 4748.5 | 4748.5 | 1 | 0.24x | 0.00 |
| +4 | 2026-05-14 04:40:00 | 4748.9 | 4748.9 | 4747.5 | 4747.5 | 2 | 0.47x | 1.00 |
| +5 | 2026-05-14 04:43:00 | 4745.4 | 4746.2 | 4745.4 | 4745.9 | 4 | 0.91x | 0.62 |
