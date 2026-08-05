# Bai lam #34 — Tích lũy (ACC)

- Anh: `range_34.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-15 20:44:00 -> 2026-06-16 04:16:00** = 390 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4330.2, VSA=3.06x, bien do nen=2.1 gia.
- Bien CHINH (net lien, climax+AR): 4330.2 - 4336.0 = 5.8 gia (0.13% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4327.4 - 4346.8 = 19.4 gia.
- Ty le bien phu/bien chinh: **3.34x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.06x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.88, ty le volume nhip cuoi/dau=1.87 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.15, ty le volume nhip cuoi/dau=0.59 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 63361..63376 (2026-06-15 22:49:00), effort(VSA TB)=0.65x, result(bien do/ATR)=0.98, ty le er=0.67 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-15 20:44:00 | 2026-06-15 20:36:00 | -7 |
| B | 2026-06-15 20:37:00 | 2026-06-16 02:41:00 | 303 |
| C | 2026-06-16 02:42:00 | 2026-06-16 03:41:00 | 60 |
| D | 2026-06-16 03:42:00 | 2026-06-16 03:48:00 | 7 |
| E | 2026-06-16 03:49:00 | 2026-06-16 04:16:00 | 28 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| AR (yếu) | 2026-06-15 20:28:00 | 4336.0 | A | - | 0.30x | 0.36 |
| ST[A] | 2026-06-15 20:36:00 | 4331.8 | A | - | 0.55x | 0.58 |
| SC? | 2026-06-15 20:44:00 | 4330.2 | A | - | 3.06x | 0.29 |
| mSOW | 2026-06-15 23:11:00 | 4335.9 | B | - | 4.76x | 0.20 |
| mSOW | 2026-06-16 02:05:00 | 4329.0 | B | - | 5.78x | 0.82 |
| LPS[C] | 2026-06-16 02:42:00 | 4330.3 | C | - | 2.10x | 0.44 |
| mSOS | 2026-06-16 03:34:00 | 4346.2 | B | - | 1.08x | 0.15 |
| SOS | 2026-06-16 03:42:00 | 4352.7 | D | - | 3.69x | 0.77 |
| LPS[D] | 2026-06-16 03:44:00 | 4350.7 | D | - | 2.41x | 0.53 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-15 20:38:00 | 4332.9 | 4333.9 | 4332.4 | 4333.9 | 21 | 0.50x | 0.67 |
| -5 | 2026-06-15 20:39:00 | 4334.1 | 4334.7 | 4333.6 | 4333.7 | 23 | 0.56x | 0.36 |
| -4 | 2026-06-15 20:40:00 | 4333.5 | 4334.5 | 4333.2 | 4333.5 | 50 | 1.15x | 0.00 |
| -3 | 2026-06-15 20:41:00 | 4333.7 | 4333.7 | 4332.7 | 4333.4 | 29 | 0.83x | 0.30 |
| -2 | 2026-06-15 20:42:00 | 4333.2 | 4333.4 | 4332.5 | 4332.5 | 10 | 0.30x | 0.78 |
| -1 | 2026-06-15 20:43:00 | 4332.8 | 4333.0 | 4331.9 | 4331.9 | 95 | 2.56x | 0.82 |
| +0 **<- climax** | 2026-06-15 20:44:00 | 4332.2 | 4332.3 | 4330.2 | 4331.6 | 123 | 3.06x | 0.29 |
| +1 | 2026-06-15 20:45:00 | 4331.5 | 4331.8 | 4331.1 | 4331.2 | 29 | 0.74x | 0.43 |
| +2 | 2026-06-15 20:46:00 | 4331.4 | 4331.4 | 4330.4 | 4330.9 | 33 | 0.92x | 0.50 |
| +3 | 2026-06-15 20:47:00 | 4330.8 | 4331.6 | 4330.6 | 4331.6 | 42 | 1.15x | 0.80 |
| +4 | 2026-06-15 20:48:00 | 4332.0 | 4332.4 | 4332.0 | 4332.2 | 10 | 0.27x | 0.50 |
| +5 | 2026-06-15 20:49:00 | 4332.2 | 4332.2 | 4331.6 | 4331.8 | 12 | 0.34x | 0.67 |
