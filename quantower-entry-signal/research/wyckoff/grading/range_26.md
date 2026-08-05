# Bai lam #26 — Tích lũy (ACC)

- Anh: `range_26.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-05 02:41:00 -> 2026-06-05 09:11:00** = 390 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4464.5, VSA=2.69x, bien do nen=5.0 gia.
- Bien CHINH (net lien, climax+AR): 4464.5 - 4476.1 = 11.6 gia (0.26% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4454.8 - 4483.2 = 28.4 gia.
- Ty le bien phu/bien chinh: **2.45x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.69x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`xu hướng quá mạnh`, n=5 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.75, ty le volume nhip cuoi/dau=2.72 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.40, ty le volume nhip cuoi/dau=1.04 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 54122..54124 (2026-06-05 05:32:00), effort(VSA TB)=3.16x, result(bien do/ATR)=4.19, ty le er=0.75 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-05 02:41:00 | 2026-06-05 03:03:00 | 23 |
| B | 2026-06-05 03:04:00 | 2026-06-05 06:17:00 | 194 |
| C | 2026-06-05 06:18:00 | 2026-06-05 06:45:00 | 28 |
| D | 2026-06-05 06:46:00 | 2026-06-05 07:10:00 | 25 |
| E | 2026-06-05 07:11:00 | 2026-06-05 09:11:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-06-05 02:41:00 | 4464.5 | A | - | 2.69x | 0.80 |
| AR | 2026-06-05 02:50:00 | 4476.1 | A | - | 1.17x | 0.72 |
| ST[A] | 2026-06-05 03:03:00 | 4462.5 | A | - | 1.23x | 0.42 |
| mSOW | 2026-06-05 05:03:00 | 4472.8 | B | - | 4.08x | 0.64 |
| mSOW | 2026-06-05 06:04:00 | 4461.6 | B | - | 2.14x | 0.28 |
| Shakeout | 2026-06-05 06:18:00 | 4454.8 | C | confirmed | 2.47x | 0.61 |
| SOS | 2026-06-05 06:46:00 | 4479.3 | D | - | 2.73x | 0.85 |
| LPS[D] | 2026-06-05 06:55:00 | 4476.4 | D | - | 1.44x | 0.29 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-05 02:35:00 | 4470.0 | 4470.9 | 4467.9 | 4469.6 | 88 | 1.17x | 0.13 |
| -5 | 2026-06-05 02:36:00 | 4470.4 | 4471.8 | 4470.0 | 4470.0 | 25 | 0.34x | 0.22 |
| -4 | 2026-06-05 02:37:00 | 4470.4 | 4472.1 | 4469.5 | 4471.8 | 81 | 1.05x | 0.54 |
| -3 | 2026-06-05 02:38:00 | 4472.2 | 4473.4 | 4471.1 | 4471.1 | 51 | 0.64x | 0.48 |
| -2 | 2026-06-05 02:39:00 | 4471.5 | 4472.6 | 4471.3 | 4471.4 | 23 | 0.30x | 0.08 |
| -1 | 2026-06-05 02:40:00 | 4471.5 | 4471.6 | 4468.4 | 4469.8 | 50 | 0.64x | 0.53 |
| +0 **<- climax** | 2026-06-05 02:41:00 | 4469.2 | 4469.5 | 4464.5 | 4465.2 | 240 | 2.69x | 0.80 |
| +1 | 2026-06-05 02:42:00 | 4465.5 | 4466.4 | 4464.5 | 4466.1 | 94 | 1.03x | 0.32 |
| +2 | 2026-06-05 02:43:00 | 4465.9 | 4467.2 | 4465.0 | 4467.2 | 67 | 0.74x | 0.59 |
| +3 | 2026-06-05 02:44:00 | 4467.9 | 4470.0 | 4467.9 | 4469.0 | 111 | 1.17x | 0.52 |
| +4 | 2026-06-05 02:45:00 | 4469.2 | 4473.4 | 4468.7 | 4472.8 | 178 | 1.75x | 0.77 |
| +5 | 2026-06-05 02:46:00 | 4473.1 | 4473.6 | 4471.2 | 4472.6 | 131 | 1.25x | 0.21 |
