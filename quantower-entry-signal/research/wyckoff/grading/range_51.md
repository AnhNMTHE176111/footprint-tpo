# Bai lam #51 — Tái tích lũy (RE-ACC)

- Anh: `range_51.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-22 12:30:00 -> 2026-07-22 15:56:00** = 206 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4139.5, VSA=1.79x, bien do nen=2.6 gia.
- MOVE truoc climax: dai 15.6 gia, 47 nen, hieu suat huong 0.50.
- Bien CHINH (net lien, climax+AR): 4110.4 - 4139.5 = 29.1 gia (0.70% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4110.4 - 4139.8 = 29.4 gia.
- Ty le bien phu/bien chinh: **1.01x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.80x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 99556..99584 (2026-07-22 13:31:00), effort(VSA TB)=1.17x, result(bien do/ATR)=12.05, ty le er=0.10 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-22 12:30:00 | 2026-07-22 13:01:00 | 32 |
| B | 2026-07-22 13:02:00 | 2026-07-22 13:30:00 | 29 |
| D | 2026-07-22 13:31:00 | 2026-07-22 13:55:00 | 25 |
| E | 2026-07-22 13:56:00 | 2026-07-22 15:56:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-07-22 12:20:00 | 4134.9 | A | - | 2.80x | 0.81 |
| AR | 2026-07-22 12:56:00 | 4110.4 | A | - | 5.03x | 0.56 |
| ST[A] | 2026-07-22 13:01:00 | 4124.6 | A | - | 1.11x | 0.49 |
| SOS | 2026-07-22 13:31:00 | 4145.7 | D | - | 4.83x | 0.47 |
| LPS[D] | 2026-07-22 13:35:00 | 4143.2 | D | - | 1.32x | 0.42 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-22 12:24:00 | 4133.8 | 4135.2 | 4133.6 | 4134.4 | 59 | 0.62x | 0.37 |
| -5 | 2026-07-22 12:25:00 | 4134.7 | 4135.5 | 4133.8 | 4134.0 | 142 | 1.45x | 0.41 |
| -4 | 2026-07-22 12:26:00 | 4134.3 | 4135.1 | 4134.0 | 4134.1 | 48 | 0.50x | 0.18 |
| -3 | 2026-07-22 12:27:00 | 4134.1 | 4135.9 | 4133.3 | 4135.8 | 134 | 1.34x | 0.65 |
| -2 | 2026-07-22 12:28:00 | 4135.8 | 4137.8 | 4135.6 | 4137.3 | 241 | 2.20x | 0.68 |
| -1 | 2026-07-22 12:29:00 | 4137.5 | 4138.0 | 4136.3 | 4137.5 | 126 | 1.12x | 0.00 |
| +0 **<- climax** | 2026-07-22 12:30:00 | 4137.8 | 4139.5 | 4136.9 | 4137.6 | 217 | 1.79x | 0.08 |
| +1 | 2026-07-22 12:31:00 | 4137.4 | 4137.5 | 4134.7 | 4134.9 | 139 | 1.11x | 0.89 |
| +2 | 2026-07-22 12:32:00 | 4134.9 | 4136.4 | 4134.0 | 4134.1 | 134 | 1.05x | 0.33 |
| +3 | 2026-07-22 12:33:00 | 4134.1 | 4134.7 | 4133.6 | 4134.7 | 63 | 0.49x | 0.55 |
| +4 | 2026-07-22 12:34:00 | 4134.4 | 4135.0 | 4132.3 | 4132.4 | 77 | 0.62x | 0.74 |
| +5 | 2026-07-22 12:35:00 | 4132.5 | 4132.9 | 4131.5 | 4132.4 | 184 | 1.47x | 0.07 |
