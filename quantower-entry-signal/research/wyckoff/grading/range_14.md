# Bai lam #14 — Tái tích lũy (RE-ACC)

- Anh: `range_14.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-06 03:20:00 -> 2026-05-06 08:12:00** = 159 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4695.2, VSA=0.58x, bien do nen=1.0 gia.
- MOVE truoc climax: dai 91.7 gia, 137 nen, hieu suat huong 0.36.
- Bien CHINH (net lien, climax+AR): 4687.7 - 4695.2 = 7.5 gia (0.16% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4687.7 - 4699.2 = 11.5 gia.
- Ty le bien phu/bien chinh: **1.53x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=10.10x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.54, ty le volume nhip cuoi/dau=1.62 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 29970..29974 (2026-05-06 04:49:00), effort(VSA TB)=1.91x, result(bien do/ATR)=10.89, ty le er=0.18 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-06 03:20:00 | 2026-05-06 03:44:00 | 12 |
| B | 2026-05-06 03:48:00 | 2026-05-06 07:57:00 | 139 |
| D | 2026-05-06 07:59:00 | 2026-05-06 08:09:00 | 7 |
| E | 2026-05-06 08:10:00 | 2026-05-06 08:12:00 | 2 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-05-06 02:56:00 | 4684.5 | A | - | 10.10x | 0.67 |
| AR | 2026-05-06 03:32:00 | 4687.7 | A | - | 0.38x | 1.00 |
| ST[A] | 2026-05-06 03:44:00 | 4692.4 | A | - | 0.40x | 0.00 |
| mSOS | 2026-05-06 06:42:00 | 4709.3 | B | - | 11.27x | 0.33 |
| SOS | 2026-05-06 07:59:00 | 4728.0 | D | - | 1.38x | 1.00 |
| LPS[D] | 2026-05-06 08:01:00 | 4722.4 | D | - | 1.44x | 1.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-06 03:13:00 | 4689.9 | 4689.9 | 4689.9 | 4689.9 | 2 | 0.45x | 0.00 |
| -5 | 2026-05-06 03:14:00 | 4692.7 | 4694.1 | 4692.7 | 4692.8 | 8 | 1.70x | 0.07 |
| -4 | 2026-05-06 03:15:00 | 4692.5 | 4692.5 | 4692.5 | 4692.5 | 1 | 0.21x | 0.00 |
| -3 | 2026-05-06 03:17:00 | 4691.8 | 4691.8 | 4690.9 | 4691.4 | 6 | 1.21x | 0.44 |
| -2 | 2026-05-06 03:18:00 | 4693.3 | 4693.6 | 4693.3 | 4693.6 | 2 | 0.40x | 1.00 |
| -1 | 2026-05-06 03:19:00 | 4693.6 | 4694.4 | 4693.6 | 4694.4 | 3 | 0.59x | 1.00 |
| +0 **<- climax** | 2026-05-06 03:20:00 | 4694.2 | 4695.2 | 4694.2 | 4695.2 | 3 | 0.58x | 1.00 |
| +1 | 2026-05-06 03:23:00 | 4689.2 | 4689.2 | 4689.2 | 4689.2 | 1 | 0.19x | 0.00 |
| +2 | 2026-05-06 03:27:00 | 4690.9 | 4690.9 | 4689.4 | 4689.4 | 2 | 0.38x | 1.00 |
| +3 | 2026-05-06 03:30:00 | 4689.7 | 4689.7 | 4689.7 | 4689.7 | 1 | 0.19x | 0.00 |
| +4 | 2026-05-06 03:31:00 | 4688.0 | 4688.0 | 4688.0 | 4688.0 | 1 | 0.19x | 0.00 |
| +5 | 2026-05-06 03:32:00 | 4688.1 | 4688.1 | 4687.7 | 4687.7 | 2 | 0.38x | 1.00 |
