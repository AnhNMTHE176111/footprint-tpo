# Bai lam #48 — Phân phối (DIST)

- Anh: `range_48.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-08 03:13:00 -> 2026-07-08 07:37:00** = 264 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4141.5, VSA=3.47x, bien do nen=3.2 gia.
- Bien CHINH (net lien, climax+AR): 4135.7 - 4141.5 = 5.8 gia (0.14% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4128.4 - 4144.6 = 16.2 gia.
- Ty le bien phu/bien chinh: **2.79x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.47x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.34, ty le volume nhip cuoi/dau=0.88 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 85379..85382 (2026-07-08 06:19:00), effort(VSA TB)=1.53x, result(bien do/ATR)=1.95, ty le er=0.78 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-08 03:13:00 | 2026-07-08 03:28:00 | 16 |
| B | 2026-07-08 03:29:00 | 2026-07-08 06:51:00 | 203 |
| C | 2026-07-08 06:52:00 | 2026-07-08 07:11:00 | 20 |
| D | 2026-07-08 07:12:00 | 2026-07-08 07:36:00 | 25 |
| E | 2026-07-08 07:37:00 | 2026-07-08 07:37:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-07-08 03:13:00 | 4141.5 | A | - | 3.47x | 0.34 |
| AR (yếu) | 2026-07-08 03:18:00 | 4135.7 | A | - | 0.68x | 0.58 |
| ST[A] | 2026-07-08 03:28:00 | 4142.3 | A | - | 0.81x | 0.40 |
| mSOW | 2026-07-08 04:17:00 | 4131.4 | B | - | 1.13x | 1.00 |
| mSOS | 2026-07-08 06:41:00 | 4138.8 | B | - | 3.70x | 0.59 |
| LPSY[C] | 2026-07-08 06:52:00 | 4137.6 | C | - | 0.71x | 0.59 |
| SOW | 2026-07-08 07:12:00 | 4128.3 | D | - | 0.68x | 0.75 |
| LPSY[D] | 2026-07-08 07:32:00 | 4137.5 | D | - | 1.73x | 0.76 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-08 03:07:00 | 4133.2 | 4135.2 | 4133.0 | 4135.2 | 16 | 0.33x | 0.91 |
| -5 | 2026-07-08 03:08:00 | 4135.9 | 4138.3 | 4135.2 | 4138.3 | 76 | 1.46x | 0.77 |
| -4 | 2026-07-08 03:09:00 | 4138.0 | 4140.5 | 4137.4 | 4137.4 | 77 | 1.38x | 0.19 |
| -3 | 2026-07-08 03:10:00 | 4137.5 | 4137.9 | 4136.6 | 4137.9 | 22 | 0.42x | 0.31 |
| -2 | 2026-07-08 03:11:00 | 4138.3 | 4139.8 | 4137.7 | 4139.5 | 63 | 1.14x | 0.57 |
| -1 | 2026-07-08 03:12:00 | 4139.4 | 4140.9 | 4139.0 | 4140.0 | 34 | 0.63x | 0.32 |
| +0 **<- climax** | 2026-07-08 03:13:00 | 4139.9 | 4141.5 | 4138.3 | 4138.8 | 225 | 3.47x | 0.34 |
| +1 | 2026-07-08 03:14:00 | 4138.4 | 4139.8 | 4138.4 | 4138.9 | 65 | 0.96x | 0.36 |
| +2 | 2026-07-08 03:15:00 | 4138.7 | 4139.5 | 4138.0 | 4138.7 | 81 | 1.14x | 0.00 |
| +3 | 2026-07-08 03:16:00 | 4138.8 | 4138.8 | 4136.5 | 4136.9 | 83 | 1.12x | 0.83 |
| +4 | 2026-07-08 03:17:00 | 4137.6 | 4137.6 | 4136.2 | 4136.2 | 37 | 0.52x | 1.00 |
| +5 | 2026-07-08 03:18:00 | 4136.2 | 4136.9 | 4135.7 | 4136.9 | 49 | 0.68x | 0.58 |
