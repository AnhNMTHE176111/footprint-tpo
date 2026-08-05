# Bai lam #09 — Tích lũy (ACC)

- Anh: `range_09.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-19 23:43:00 -> 2026-04-20 01:12:00** = 59 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4793.0, VSA=11.74x, bien do nen=22.0 gia.
- MOVE truoc climax: dai 34.1 gia, 43 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4793.0 - 4809.8 = 16.8 gia (0.35% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4793.0 - 4813.0 = 20.0 gia.
- Ty le bien phu/bien chinh: **1.19x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=11.74x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 21416..21425 (2026-04-20 00:20:00), effort(VSA TB)=1.36x, result(bien do/ATR)=13.99, ty le er=0.10 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-19 23:43:00 | 2026-04-20 00:01:00 | 17 |
| B | 2026-04-20 00:02:00 | 2026-04-20 00:19:00 | 13 |
| D | 2026-04-20 00:20:00 | 2026-04-20 00:59:00 | 18 |
| E | 2026-04-20 01:00:00 | 2026-04-20 01:12:00 | 12 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-04-19 23:43:00 | 4793.0 | A | - | 11.74x | 0.61 |
| AR (yếu) | 2026-04-19 23:58:00 | 4809.8 | A | - | 0.44x | 1.00 |
| ST[A] | 2026-04-20 00:01:00 | 4802.1 | A | - | 0.15x | 0.00 |
| mSOS | 2026-04-20 00:16:00 | 4813.0 | B | - | 1.67x | 0.72 |
| SOS | 2026-04-20 00:20:00 | 4815.9 | D | - | 3.88x | 0.63 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-19 23:36:00 | 4823.0 | 4823.0 | 4819.3 | 4819.5 | 5 | 1.89x | 0.95 |
| -5 | 2026-04-19 23:37:00 | 4820.3 | 4821.3 | 4820.0 | 4820.6 | 5 | 1.82x | 0.23 |
| -4 | 2026-04-19 23:38:00 | 4821.6 | 4821.6 | 4821.6 | 4821.6 | 1 | 0.43x | 0.00 |
| -3 | 2026-04-19 23:39:00 | 4819.2 | 4819.7 | 4819.1 | 4819.7 | 3 | 1.25x | 0.83 |
| -2 | 2026-04-19 23:40:00 | 4816.4 | 4816.8 | 4816.4 | 4816.8 | 3 | 1.20x | 1.00 |
| -1 | 2026-04-19 23:41:00 | 4816.8 | 4818.3 | 4816.8 | 4818.3 | 3 | 1.18x | 1.00 |
| +0 **<- climax** | 2026-04-19 23:43:00 | 4815.0 | 4815.0 | 4793.0 | 4801.5 | 71 | 11.74x | 0.61 |
| +1 | 2026-04-19 23:44:00 | 4805.1 | 4805.1 | 4805.1 | 4805.1 | 1 | 0.17x | 0.00 |
| +2 | 2026-04-19 23:45:00 | 4800.2 | 4800.2 | 4797.8 | 4797.8 | 4 | 0.66x | 1.00 |
| +3 | 2026-04-19 23:46:00 | 4793.7 | 4793.7 | 4793.4 | 4793.4 | 2 | 0.33x | 1.00 |
| +4 | 2026-04-19 23:47:00 | 4796.0 | 4798.8 | 4795.8 | 4797.0 | 6 | 0.96x | 0.33 |
| +5 | 2026-04-19 23:48:00 | 4797.4 | 4802.4 | 4797.4 | 4802.4 | 5 | 0.78x | 1.00 |
