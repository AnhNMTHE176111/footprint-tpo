# Bai lam #14 — Tái tích lũy (RE-ACC)

- Anh: `range_14.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-05 07:36:00 -> 2026-05-05 13:35:00** = 188 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4600.6, VSA=1.59x, bien do nen=1.1 gia.
- Bien CHINH (net lien, climax+AR): 4588.2 - 4600.6 = 12.4 gia (0.27% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4585.0 - 4603.6 = 18.6 gia.
- Ty le bien phu/bien chinh: **1.50x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=7.41x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.89, ty le volume nhip cuoi/dau=1.39 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 29454..29459 (2026-05-05 10:17:00), effort(VSA TB)=0.84x, result(bien do/ATR)=2.76, ty le er=0.30 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-05 07:36:00 | 2026-05-05 08:05:00 | 12 |
| B | 2026-05-05 08:07:00 | 2026-05-05 11:17:00 | 92 |
| C | 2026-05-05 11:20:00 | 2026-05-05 13:06:00 | 60 |
| D | 2026-05-05 13:08:00 | 2026-05-05 13:33:00 | 23 |
| E | 2026-05-05 13:34:00 | 2026-05-05 13:35:00 | 2 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-05-05 07:34:00 | 4597.2 | A | - | 7.41x | 1.00 |
| AR (yếu) | 2026-05-05 07:56:00 | 4588.2 | A | - | 0.47x | 1.00 |
| ST[A] | 2026-05-05 08:05:00 | 4596.1 | A | - | 0.30x | 0.00 |
| mSOS | 2026-05-05 10:34:00 | 4599.1 | B | - | 5.11x | 0.46 |
| LPS[C] | 2026-05-05 11:20:00 | 4595.5 | C | - | 0.37x | 0.00 |
| SOS | 2026-05-05 13:08:00 | 4625.3 | D | - | 8.00x | 0.90 |
| LPS[D] | 2026-05-05 13:29:00 | 4621.5 | D | - | 0.16x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-05 07:25:00 | 4595.3 | 4595.3 | 4595.3 | 4595.3 | 1 | 0.39x | 0.00 |
| -5 | 2026-05-05 07:26:00 | 4595.1 | 4595.1 | 4594.7 | 4594.7 | 3 | 1.15x | 1.00 |
| -4 | 2026-05-05 07:28:00 | 4593.6 | 4593.7 | 4593.6 | 4593.7 | 2 | 0.75x | 1.00 |
| -3 | 2026-05-05 07:31:00 | 4595.8 | 4595.8 | 4595.8 | 4595.8 | 1 | 0.38x | 0.00 |
| -2 | 2026-05-05 07:34:00 | 4595.2 | 4597.2 | 4595.2 | 4597.2 | 30 | 7.41x | 1.00 |
| -1 | 2026-05-05 07:35:00 | 4596.7 | 4597.7 | 4596.7 | 4597.7 | 2 | 0.49x | 1.00 |
| +0 **<- climax** | 2026-05-05 07:36:00 | 4599.5 | 4600.6 | 4599.5 | 4600.2 | 7 | 1.59x | 0.64 |
| +1 | 2026-05-05 07:39:00 | 4599.2 | 4599.2 | 4599.2 | 4599.2 | 1 | 0.23x | 0.00 |
| +2 | 2026-05-05 07:41:00 | 4600.3 | 4600.3 | 4600.3 | 4600.3 | 1 | 0.23x | 0.00 |
| +3 | 2026-05-05 07:43:00 | 4598.0 | 4598.0 | 4598.0 | 4598.0 | 2 | 0.46x | 0.00 |
| +4 | 2026-05-05 07:46:00 | 4592.3 | 4592.3 | 4592.3 | 4592.3 | 1 | 0.23x | 0.00 |
| +5 | 2026-05-05 07:47:00 | 4590.3 | 4590.3 | 4590.3 | 4590.3 | 1 | 0.23x | 0.00 |
