# Bai lam #23 — Tái phân phối (RE-DIST)

- Anh: `range_23.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-26 00:19:00 -> 2026-05-26 03:23:00** = 179 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4574.6, VSA=1.54x, bien do nen=4.4 gia.
- MOVE truoc climax: dai 25.7 gia, 59 nen, hieu suat huong 0.47.
- Bien CHINH (net lien, climax+AR): 4574.6 - 4586.0 = 11.4 gia (0.25% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4573.4 - 4586.0 = 12.6 gia.
- Ty le bien phu/bien chinh: **1.11x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.53x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=4 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.12, ty le volume nhip cuoi/dau=0.61 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 42852..42878 (2026-05-26 01:47:00), effort(VSA TB)=1.45x, result(bien do/ATR)=2.46, ty le er=0.59 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-26 00:19:00 | 2026-05-26 00:40:00 | 20 |
| B | 2026-05-26 00:41:00 | 2026-05-26 02:56:00 | 134 |
| D | 2026-05-26 02:57:00 | 2026-05-26 03:22:00 | 25 |
| E | 2026-05-26 03:23:00 | 2026-05-26 03:23:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-26 00:01:00 | 4583.4 | A | - | 4.53x | 0.70 |
| AR | 2026-05-26 00:31:00 | 4586.0 | A | - | 1.32x | 0.29 |
| ST[A] | 2026-05-26 00:40:00 | 4576.7 | A | - | 1.82x | 0.51 |
| mSOW | 2026-05-26 00:59:00 | 4579.9 | B | - | 6.31x | 0.94 |
| SOW | 2026-05-26 02:57:00 | 4565.8 | D | - | 0.96x | 0.58 |
| LPSY[D] | 2026-05-26 03:01:00 | 4569.4 | D | - | 1.25x | 1.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-26 00:13:00 | 4584.8 | 4585.1 | 4584.8 | 4585.1 | 2 | 0.17x | 1.00 |
| -5 | 2026-05-26 00:14:00 | 4586.6 | 4586.6 | 4586.6 | 4586.6 | 1 | 0.09x | 0.00 |
| -4 | 2026-05-26 00:15:00 | 4586.5 | 4586.5 | 4586.2 | 4586.2 | 2 | 0.18x | 1.00 |
| -3 | 2026-05-26 00:16:00 | 4586.1 | 4586.1 | 4583.6 | 4583.6 | 14 | 1.20x | 1.00 |
| -2 | 2026-05-26 00:17:00 | 4583.0 | 4583.0 | 4581.2 | 4581.7 | 10 | 0.86x | 0.72 |
| -1 | 2026-05-26 00:18:00 | 4582.0 | 4582.4 | 4575.4 | 4575.4 | 49 | 3.50x | 0.94 |
| +0 **<- climax** | 2026-05-26 00:19:00 | 4575.0 | 4579.0 | 4574.6 | 4579.0 | 23 | 1.54x | 0.91 |
| +1 | 2026-05-26 00:20:00 | 4578.6 | 4578.6 | 4575.2 | 4577.9 | 46 | 3.00x | 0.21 |
| +2 | 2026-05-26 00:21:00 | 4578.0 | 4580.5 | 4578.0 | 4579.9 | 38 | 2.67x | 0.76 |
| +3 | 2026-05-26 00:22:00 | 4579.5 | 4579.5 | 4575.1 | 4575.1 | 7 | 0.50x | 1.00 |
| +4 | 2026-05-26 00:23:00 | 4575.9 | 4576.2 | 4575.1 | 4576.2 | 6 | 0.43x | 0.27 |
| +5 | 2026-05-26 00:24:00 | 4576.9 | 4577.6 | 4576.9 | 4577.6 | 2 | 0.15x | 1.00 |
