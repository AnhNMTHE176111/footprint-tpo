# Bai lam #07 — Tái tích lũy (RE-ACC)

- Anh: `range_07.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-13 16:47:00 -> 2026-04-14 06:26:00** = 265 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4806.7, VSA=2.72x, bien do nen=5.5 gia.
- MOVE truoc climax: dai 42.4 gia, 60 nen, hieu suat huong 0.36.
- Bien CHINH (net lien, climax+AR): 4785.7 - 4806.7 = 21.0 gia (0.44% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4783.2 - 4810.9 = 27.7 gia.
- Ty le bien phu/bien chinh: **1.32x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.72x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.36, ty le volume nhip cuoi/dau=1.51 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.57, ty le volume nhip cuoi/dau=1.89 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 18720..18721 (2026-04-13 17:29:00), effort(VSA TB)=3.45x, result(bien do/ATR)=3.93, ty le er=0.88 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-13 16:47:00 | 2026-04-13 17:27:00 | 36 |
| B | 2026-04-13 17:28:00 | 2026-04-13 18:16:00 | 26 |
| C | 2026-04-13 18:17:00 | 2026-04-13 23:03:00 | 59 |
| D | 2026-04-13 23:04:00 | 2026-04-14 00:39:00 | 24 |
| E | 2026-04-14 00:40:00 | 2026-04-14 06:26:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-04-13 16:47:00 | 4806.7 | A | - | 2.72x | 0.64 |
| AR | 2026-04-13 17:08:00 | 4785.7 | A | - | 1.71x | 0.85 |
| ST[A] | 2026-04-13 17:27:00 | 4810.9 | A | - | 0.58x | 1.00 |
| LPS[C] | 2026-04-13 18:17:00 | 4785.0 | C | - | 0.29x | 0.00 |
| ST[B] | 2026-04-13 18:27:00 | 4783.2 | B | - | 0.70x | 1.00 |
| SOS | 2026-04-13 23:04:00 | 4824.7 | D | - | 1.94x | 1.00 |
| LPS[D] | 2026-04-14 00:00:00 | 4814.6 | D | - | 1.18x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-13 16:41:00 | 4796.0 | 4797.3 | 4792.0 | 4792.0 | 12 | 1.90x | 0.75 |
| -5 | 2026-04-13 16:42:00 | 4793.0 | 4793.0 | 4791.3 | 4791.3 | 5 | 0.77x | 1.00 |
| -4 | 2026-04-13 16:43:00 | 4790.3 | 4796.1 | 4789.7 | 4796.1 | 10 | 1.47x | 0.91 |
| -3 | 2026-04-13 16:44:00 | 4798.3 | 4800.0 | 4797.7 | 4800.0 | 6 | 0.93x | 0.74 |
| -2 | 2026-04-13 16:45:00 | 4800.5 | 4801.2 | 4800.5 | 4800.7 | 6 | 0.90x | 0.29 |
| -1 | 2026-04-13 16:46:00 | 4801.2 | 4802.0 | 4800.5 | 4800.6 | 11 | 1.72x | 0.40 |
| +0 **<- climax** | 2026-04-13 16:47:00 | 4801.2 | 4806.7 | 4801.2 | 4804.7 | 20 | 2.72x | 0.64 |
| +1 | 2026-04-13 16:48:00 | 4801.4 | 4801.6 | 4799.3 | 4799.3 | 9 | 1.16x | 0.91 |
| +2 | 2026-04-13 16:50:00 | 4802.2 | 4802.9 | 4802.2 | 4802.9 | 2 | 0.26x | 1.00 |
| +3 | 2026-04-13 16:51:00 | 4803.7 | 4803.7 | 4803.0 | 4803.0 | 2 | 0.25x | 1.00 |
| +4 | 2026-04-13 16:52:00 | 4799.0 | 4799.8 | 4799.0 | 4799.0 | 4 | 0.53x | 0.00 |
| +5 | 2026-04-13 16:53:00 | 4798.7 | 4798.7 | 4796.8 | 4796.8 | 4 | 0.54x | 1.00 |
