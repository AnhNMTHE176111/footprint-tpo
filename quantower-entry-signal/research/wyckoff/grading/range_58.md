# Bai lam #58 — Tích lũy (ACC)

- Anh: `range_58.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-27 03:30:00 -> 2026-07-27 07:41:00** = 250 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4087.0, VSA=1.21x, bien do nen=1.5 gia.
- Bien CHINH (net lien, climax+AR): 4087.0 - 4095.0 = 8.0 gia (0.20% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4086.5 - 4098.4 = 11.9 gia.
- Ty le bien phu/bien chinh: **1.49x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.66x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.69, ty le volume nhip cuoi/dau=1.49 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 103261..103265 (2026-07-27 06:05:00), effort(VSA TB)=1.27x, result(bien do/ATR)=2.10, ty le er=0.61 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-27 03:30:00 | 2026-07-27 04:18:00 | 49 |
| B | 2026-07-27 04:19:00 | 2026-07-27 06:19:00 | 120 |
| C | 2026-07-27 06:20:00 | 2026-07-27 06:39:00 | 20 |
| D | 2026-07-27 06:40:00 | 2026-07-27 07:04:00 | 25 |
| E | 2026-07-27 07:05:00 | 2026-07-27 07:41:00 | 37 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-07-27 03:32:00 | 4088.5 | A | - | 2.66x | 0.05 |
| AR | 2026-07-27 04:01:00 | 4095.0 | A | - | 1.75x | 0.44 |
| ST[A] | 2026-07-27 04:18:00 | 4088.9 | A | - | 0.75x | 0.83 |
| mSOS | 2026-07-27 06:12:00 | 4098.4 | B | - | 0.98x | 0.00 |
| LPS[C] | 2026-07-27 06:20:00 | 4093.3 | C | - | 1.08x | 0.33 |
| SOS | 2026-07-27 06:40:00 | 4100.4 | D | - | 2.05x | 0.17 |
| LPS[D] | 2026-07-27 06:44:00 | 4099.4 | D | - | 0.68x | 0.55 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-27 03:24:00 | 4092.2 | 4092.2 | 4091.6 | 4091.6 | 28 | 0.66x | 1.00 |
| -5 | 2026-07-27 03:25:00 | 4092.0 | 4092.0 | 4091.0 | 4091.3 | 33 | 0.77x | 0.70 |
| -4 | 2026-07-27 03:26:00 | 4091.6 | 4091.6 | 4088.4 | 4089.5 | 112 | 2.37x | 0.66 |
| -3 | 2026-07-27 03:27:00 | 4089.6 | 4090.0 | 4089.0 | 4090.0 | 23 | 0.49x | 0.40 |
| -2 | 2026-07-27 03:28:00 | 4089.9 | 4089.9 | 4088.3 | 4088.3 | 29 | 0.61x | 1.00 |
| -1 | 2026-07-27 03:29:00 | 4088.1 | 4088.1 | 4087.3 | 4087.3 | 29 | 0.62x | 1.00 |
| +0 **<- climax** | 2026-07-27 03:30:00 | 4087.4 | 4088.5 | 4087.0 | 4088.3 | 44 | 1.21x | 0.60 |
| +1 | 2026-07-27 03:31:00 | 4088.4 | 4089.8 | 4087.5 | 4089.8 | 64 | 1.66x | 0.61 |
| +2 | 2026-07-27 03:32:00 | 4090.2 | 4090.4 | 4088.5 | 4090.1 | 114 | 2.66x | 0.05 |
| +3 | 2026-07-27 03:33:00 | 4090.0 | 4092.0 | 4090.0 | 4091.8 | 71 | 1.57x | 0.90 |
| +4 | 2026-07-27 03:34:00 | 4091.7 | 4092.2 | 4091.3 | 4092.0 | 33 | 0.72x | 0.33 |
| +5 | 2026-07-27 03:35:00 | 4092.4 | 4092.6 | 4090.8 | 4090.8 | 48 | 1.03x | 0.89 |
