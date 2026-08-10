# Bai lam #50 — Tích lũy (ACC)

- Anh: `range_50.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-09 04:03:00 -> 2026-07-09 05:11:00** = 68 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4068.4, VSA=2.39x, bien do nen=1.3 gia.
- Bien CHINH (net lien, climax+AR): 4068.4 - 4073.6 = 5.2 gia (0.13% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4066.5 - 4085.3 = 18.8 gia.
- Ty le bien phu/bien chinh: **3.62x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.39x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.41, ty le volume nhip cuoi/dau=0.84 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 86643..86647 (2026-07-09 04:26:00), effort(VSA TB)=1.12x, result(bien do/ATR)=2.51, ty le er=0.45 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-09 04:03:00 | 2026-07-09 04:03:00 | 1 |
| B | 2026-07-09 04:04:00 | 2026-07-09 04:17:00 | 14 |
| C | 2026-07-09 04:18:00 | 2026-07-09 05:00:00 | 43 |
| D | 2026-07-09 05:01:00 | 2026-07-09 05:08:00 | 8 |
| E | 2026-07-09 05:09:00 | 2026-07-09 05:11:00 | 3 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| AR (yếu) | 2026-07-09 04:00:00 | 4073.6 | A | - | 1.86x | 0.88 |
| SC? | 2026-07-09 04:03:00 | 4068.4 | A | - | 2.39x | 0.77 |
| ST[A] | 2026-07-09 04:03:00 | 4068.4 | A | - | 2.39x | 0.77 |
| Spring | 2026-07-09 04:18:00 | 4066.5 | C | confirmed | 1.41x | 0.00 |
| LPS[C] | 2026-07-09 04:25:00 | 4068.5 | C | - | 0.37x | 0.87 |
| SOS | 2026-07-09 05:01:00 | 4079.1 | D | - | 8.67x | 0.67 |
| LPS[D] | 2026-07-09 05:04:00 | 4074.9 | D | - | 0.97x | 0.62 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-09 03:57:00 | 4071.7 | 4071.9 | 4071.0 | 4071.0 | 4 | 0.28x | 0.78 |
| -5 | 2026-07-09 03:58:00 | 4070.9 | 4072.1 | 4070.9 | 4072.1 | 14 | 0.96x | 1.00 |
| -4 | 2026-07-09 03:59:00 | 4071.8 | 4073.5 | 4071.8 | 4073.5 | 31 | 2.00x | 1.00 |
| -3 | 2026-07-09 04:00:00 | 4073.6 | 4073.6 | 4071.9 | 4072.1 | 31 | 1.86x | 0.88 |
| -2 | 2026-07-09 04:01:00 | 4072.1 | 4072.1 | 4070.7 | 4070.7 | 12 | 0.74x | 1.00 |
| -1 | 2026-07-09 04:02:00 | 4070.5 | 4070.5 | 4069.3 | 4069.3 | 36 | 2.01x | 1.00 |
| +0 **<- climax** | 2026-07-09 04:03:00 | 4068.7 | 4069.7 | 4068.4 | 4069.7 | 48 | 2.39x | 0.77 |
| +1 | 2026-07-09 04:04:00 | 4069.9 | 4070.7 | 4069.9 | 4070.4 | 47 | 2.14x | 0.63 |
| +2 | 2026-07-09 04:05:00 | 4070.6 | 4071.1 | 4070.6 | 4071.0 | 12 | 0.56x | 0.80 |
| +3 | 2026-07-09 04:06:00 | 4071.6 | 4072.0 | 4070.7 | 4070.7 | 6 | 0.28x | 0.69 |
| +4 | 2026-07-09 04:07:00 | 4071.0 | 4071.1 | 4070.2 | 4070.2 | 8 | 0.37x | 0.89 |
| +5 | 2026-07-09 04:08:00 | 4070.2 | 4070.4 | 4070.1 | 4070.4 | 3 | 0.14x | 0.67 |
