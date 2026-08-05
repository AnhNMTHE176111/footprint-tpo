# Bai lam #02 — Tái tích lũy (RE-ACC)

- Anh: `range_02.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-01-08 23:07:00 -> 2026-01-09 15:23:00** = 67 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4587.0, VSA=4.88x, bien do nen=0.4 gia.
- MOVE truoc climax: dai 53.7 gia, 21 nen, hieu suat huong 0.53.
- Bien CHINH (net lien, climax+AR): 4568.0 - 4587.0 = 19.0 gia (0.41% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4568.0 - 4587.0 = 19.0 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.88x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.38, ty le volume nhip cuoi/dau=1.11 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 1736..1739 (2026-01-09 12:54:00), effort(VSA TB)=2.36x, result(bien do/ATR)=35.00, ty le er=0.07 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-01-08 23:07:00 | 2026-01-09 06:41:00 | 16 |
| B | 2026-01-09 07:14:00 | 2026-01-09 12:53:00 | 27 |
| C | 2026-01-09 12:54:00 | 2026-01-09 14:09:00 | 14 |
| D | 2026-01-09 14:10:00 | 2026-01-09 15:00:00 | 9 |
| E | 2026-01-09 15:09:00 | 2026-01-09 15:23:00 | 2 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-01-08 23:07:00 | 4587.0 | A | - | 4.88x | 1.00 |
| AR | 2026-01-09 01:04:00 | 4568.0 | A | - | 0.48x | 1.00 |
| ST[A] | 2026-01-09 06:41:00 | 4584.0 | A | - | 0.29x | 0.00 |
| LPS[C] | 2026-01-09 12:54:00 | 4572.2 | C | - | 4.44x | 1.00 |
| SOS | 2026-01-09 14:10:00 | 4601.9 | D | - | 8.14x | 0.89 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-01-08 18:29:00 | 4558.4 | 4560.9 | 4558.2 | 4560.0 | 37 | 12.13x | 0.59 |
| -5 | 2026-01-08 18:53:00 | 4560.8 | 4560.8 | 4560.8 | 4560.8 | 3 | 0.95x | 0.00 |
| -4 | 2026-01-08 20:26:00 | 4576.0 | 4576.0 | 4576.0 | 4576.0 | 2 | 0.62x | 0.00 |
| -3 | 2026-01-08 20:43:00 | 4583.0 | 4583.0 | 4583.0 | 4583.0 | 1 | 0.31x | 0.00 |
| -2 | 2026-01-08 21:11:00 | 4586.2 | 4586.2 | 4586.2 | 4586.2 | 1 | 0.31x | 0.00 |
| -1 | 2026-01-08 21:20:00 | 4583.7 | 4583.7 | 4583.7 | 4583.7 | 1 | 0.32x | 0.00 |
| +0 **<- climax** | 2026-01-08 23:07:00 | 4586.6 | 4587.0 | 4586.6 | 4587.0 | 20 | 4.88x | 1.00 |
| +1 | 2026-01-08 23:54:00 | 4584.9 | 4584.9 | 4584.9 | 4584.9 | 1 | 0.24x | 0.00 |
| +2 | 2026-01-09 00:23:00 | 4578.2 | 4578.2 | 4578.2 | 4578.2 | 1 | 0.24x | 0.00 |
| +3 | 2026-01-09 01:04:00 | 4570.0 | 4570.0 | 4568.0 | 4568.0 | 2 | 0.48x | 1.00 |
| +4 | 2026-01-09 01:16:00 | 4569.0 | 4569.0 | 4569.0 | 4569.0 | 1 | 0.24x | 0.00 |
| +5 | 2026-01-09 01:44:00 | 4571.0 | 4571.0 | 4571.0 | 4571.0 | 1 | 0.24x | 0.00 |
