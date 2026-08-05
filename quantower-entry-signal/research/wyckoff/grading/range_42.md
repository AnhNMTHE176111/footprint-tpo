# Bai lam #42 — Phân phối (DIST)

- Anh: `range_42.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-06 18:36:00 -> 2026-07-07 00:24:00** = 274 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4179.6, VSA=2.40x, bien do nen=1.5 gia.
- Bien CHINH (net lien, climax+AR): 4170.5 - 4179.6 = 9.1 gia (0.22% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4170.5 - 4179.6 = 9.1 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.29x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.67, ty le volume nhip cuoi/dau=2.22 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`SOT`, n=4 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.50, ty le volume nhip cuoi/dau=0.84 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 83454..83458 (2026-07-06 20:00:00), effort(VSA TB)=2.33x, result(bien do/ATR)=3.32, ty le er=0.70 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-06 18:36:00 | 2026-07-06 19:21:00 | 46 |
| B | 2026-07-06 19:22:00 | 2026-07-06 22:55:00 | 145 |
| C | 2026-07-06 22:56:00 | 2026-07-06 23:56:00 | 56 |
| D | 2026-07-06 23:57:00 | 2026-07-07 00:21:00 | 25 |
| E | 2026-07-07 00:22:00 | 2026-07-07 00:24:00 | 3 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-07-06 18:42:00 | 4177.1 | A | - | 3.29x | 0.43 |
| AR | 2026-07-06 19:15:00 | 4170.5 | A | - | 0.96x | 0.09 |
| ST[A] | 2026-07-06 19:21:00 | 4174.5 | A | - | 1.33x | 0.38 |
| LPSY[C] | 2026-07-06 22:56:00 | 4176.6 | C | - | 1.33x | 0.69 |
| SOW | 2026-07-06 23:57:00 | 4168.4 | D | - | 4.12x | 0.74 |
| LPSY[D] | 2026-07-07 00:05:00 | 4169.7 | D | - | 0.86x | 0.93 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-06 18:30:00 | 4173.6 | 4173.6 | 4171.6 | 4172.6 | 81 | 2.48x | 0.50 |
| -5 | 2026-07-06 18:31:00 | 4172.9 | 4172.9 | 4172.5 | 4172.6 | 14 | 0.43x | 0.75 |
| -4 | 2026-07-06 18:32:00 | 4172.4 | 4174.4 | 4172.4 | 4174.4 | 23 | 0.73x | 1.00 |
| -3 | 2026-07-06 18:33:00 | 4174.4 | 4175.9 | 4174.2 | 4175.7 | 70 | 2.01x | 0.76 |
| -2 | 2026-07-06 18:34:00 | 4175.7 | 4176.1 | 4175.5 | 4175.9 | 24 | 0.71x | 0.33 |
| -1 | 2026-07-06 18:35:00 | 4175.5 | 4178.3 | 4175.5 | 4178.3 | 87 | 2.41x | 1.00 |
| +0 **<- climax** | 2026-07-06 18:36:00 | 4178.2 | 4179.6 | 4178.1 | 4178.6 | 91 | 2.40x | 0.27 |
| +1 | 2026-07-06 18:37:00 | 4178.6 | 4179.2 | 4178.2 | 4179.2 | 31 | 0.82x | 0.60 |
| +2 | 2026-07-06 18:38:00 | 4178.8 | 4178.9 | 4177.8 | 4178.0 | 38 | 0.98x | 0.73 |
| +3 | 2026-07-06 18:39:00 | 4178.2 | 4178.2 | 4176.8 | 4177.1 | 48 | 1.18x | 0.79 |
| +4 | 2026-07-06 18:40:00 | 4177.4 | 4177.4 | 4176.8 | 4177.1 | 17 | 0.41x | 0.50 |
| +5 | 2026-07-06 18:41:00 | 4177.2 | 4177.6 | 4176.8 | 4177.0 | 12 | 0.30x | 0.25 |
