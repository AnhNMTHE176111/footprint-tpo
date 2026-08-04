# Bai lam #15 — Tích lũy (ACC)

- Anh: `range_15.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-07 16:19:00 -> 2026-05-08 14:06:00** = 630 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4750.0, VSA=1.90x, bien do nen=2.6 gia.
- MOVE truoc climax: dai 53.5 gia, 70 nen, hieu suat huong 0.48.
- Bien CHINH (net lien, climax+AR): 4750.0 - 4768.4 = 18.4 gia (0.39% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4708.0 - 4778.8 = 70.8 gia.
- Ty le bien phu/bien chinh: **3.85x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.94x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.22, ty le volume nhip cuoi/dau=0.38 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 31408..31437 (2026-05-07 22:22:00), effort(VSA TB)=0.97x, result(bien do/ATR)=0.85, ty le er=1.14 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-07 16:19:00 | 2026-05-07 16:43:00 | 19 |
| B | 2026-05-07 16:46:00 | 2026-05-08 12:10:00 | 518 |
| C | 2026-05-08 12:12:00 | 2026-05-08 13:29:00 | 60 |
| D | 2026-05-08 13:30:00 | 2026-05-08 13:57:00 | 25 |
| E | 2026-05-08 13:58:00 | 2026-05-08 14:06:00 | 9 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-07 16:18:00 | 4753.2 | A | - | 2.94x | 1.00 |
| AR | 2026-05-07 16:28:00 | 4768.4 | A | - | 0.27x | 1.00 |
| ST[A] | 2026-05-07 16:43:00 | 4757.2 | A | - | 0.17x | 0.00 |
| mSOW | 2026-05-07 22:00:00 | 4708.0 | B | - | 0.13x | 0.00 |
| mSOS | 2026-05-08 06:29:00 | 4778.8 | B | - | 0.65x | 0.00 |
| LPS[C] | 2026-05-08 12:12:00 | 4749.9 | C | - | 2.00x | 1.00 |
| SOS | 2026-05-08 13:30:00 | 4780.7 | D | - | 4.66x | 1.00 |
| LPS[D] | 2026-05-08 13:33:00 | 4784.5 | D | - | 3.96x | 0.65 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-07 16:12:00 | 4761.3 | 4761.3 | 4760.4 | 4760.4 | 3 | 0.49x | 1.00 |
| -5 | 2026-05-07 16:13:00 | 4760.7 | 4762.3 | 4760.3 | 4762.3 | 4 | 0.70x | 0.80 |
| -4 | 2026-05-07 16:15:00 | 4760.4 | 4760.4 | 4757.4 | 4757.4 | 15 | 2.52x | 1.00 |
| -3 | 2026-05-07 16:16:00 | 4757.8 | 4759.0 | 4757.4 | 4757.4 | 7 | 1.17x | 0.25 |
| -2 | 2026-05-07 16:17:00 | 4758.2 | 4758.5 | 4756.8 | 4757.3 | 12 | 2.00x | 0.53 |
| -1 | 2026-05-07 16:18:00 | 4757.2 | 4757.2 | 4753.2 | 4753.2 | 20 | 2.94x | 1.00 |
| +0 **<- climax** | 2026-05-07 16:19:00 | 4752.5 | 4752.6 | 4750.0 | 4750.5 | 14 | 1.90x | 0.77 |
| +1 | 2026-05-07 16:20:00 | 4752.1 | 4756.5 | 4752.1 | 4756.3 | 9 | 1.19x | 0.95 |
| +2 | 2026-05-07 16:21:00 | 4758.8 | 4758.9 | 4757.0 | 4757.0 | 3 | 0.41x | 0.95 |
| +3 | 2026-05-07 16:22:00 | 4758.9 | 4760.6 | 4758.9 | 4760.6 | 2 | 0.28x | 1.00 |
| +4 | 2026-05-07 16:23:00 | 4758.5 | 4762.9 | 4758.5 | 4762.9 | 11 | 1.49x | 1.00 |
| +5 | 2026-05-07 16:24:00 | 4762.2 | 4762.2 | 4762.2 | 4762.2 | 1 | 0.14x | 0.00 |
