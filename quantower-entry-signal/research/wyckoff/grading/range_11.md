# Bai lam #11 — Tích lũy (ACC)

- Anh: `range_11.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-26 23:41:00 -> 2026-04-27 05:49:00** = 146 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4724.5, VSA=1.94x, bien do nen=0.6 gia.
- MOVE truoc climax: dai 39.0 gia, 28 nen, hieu suat huong 0.63.
- Bien CHINH (net lien, climax+AR): 4724.5 - 4759.1 = 34.6 gia (0.73% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4724.5 - 4760.1 = 35.6 gia.
- Ty le bien phu/bien chinh: **1.03x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.14x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 25138..25142 (2026-04-27 01:43:00), effort(VSA TB)=0.74x, result(bien do/ATR)=8.28, ty le er=0.09 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-26 23:41:00 | 2026-04-27 01:16:00 | 46 |
| B | 2026-04-27 01:17:00 | 2026-04-27 02:46:00 | 44 |
| D | 2026-04-27 02:47:00 | 2026-04-27 03:47:00 | 25 |
| E | 2026-04-27 03:49:00 | 2026-04-27 05:49:00 | 32 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-04-26 23:40:00 | 4724.7 | A | - | 4.14x | 1.00 |
| AR | 2026-04-27 01:04:00 | 4759.1 | A | - | 0.24x | 1.00 |
| ST[A] | 2026-04-27 01:16:00 | 4741.7 | A | - | 0.29x | 1.00 |
| SOS | 2026-04-27 02:47:00 | 4766.7 | D | - | 2.33x | 1.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-26 23:06:00 | 4734.5 | 4734.5 | 4734.5 | 4734.5 | 1 | 0.71x | 0.00 |
| -5 | 2026-04-26 23:17:00 | 4733.7 | 4733.7 | 4733.7 | 4733.7 | 1 | 0.71x | 0.00 |
| -4 | 2026-04-26 23:27:00 | 4731.4 | 4731.4 | 4731.4 | 4731.4 | 1 | 0.74x | 0.00 |
| -3 | 2026-04-26 23:29:00 | 4727.4 | 4727.4 | 4727.4 | 4727.4 | 1 | 0.77x | 0.00 |
| -2 | 2026-04-26 23:30:00 | 4726.3 | 4726.3 | 4726.3 | 4726.3 | 1 | 0.80x | 0.00 |
| -1 | 2026-04-26 23:40:00 | 4725.5 | 4725.5 | 4724.7 | 4724.7 | 6 | 4.14x | 1.00 |
| +0 **<- climax** | 2026-04-26 23:41:00 | 4725.1 | 4725.1 | 4724.5 | 4724.5 | 3 | 1.94x | 1.00 |
| +1 | 2026-04-26 23:59:00 | 4731.5 | 4731.5 | 4731.5 | 4731.5 | 1 | 0.67x | 0.00 |
| +2 | 2026-04-27 00:00:00 | 4728.9 | 4729.4 | 4728.9 | 4729.4 | 4 | 2.50x | 1.00 |
| +3 | 2026-04-27 00:01:00 | 4729.0 | 4729.0 | 4729.0 | 4729.0 | 1 | 0.62x | 0.00 |
| +4 | 2026-04-27 00:04:00 | 4728.3 | 4728.9 | 4728.3 | 4728.9 | 2 | 1.21x | 1.00 |
| +5 | 2026-04-27 00:06:00 | 4726.1 | 4726.1 | 4726.1 | 4726.1 | 1 | 0.61x | 0.00 |
