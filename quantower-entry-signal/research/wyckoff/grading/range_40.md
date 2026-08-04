# Bai lam #40 — Tích lũy (ACC)

- Anh: `range_40.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-06 00:01:00 -> 2026-07-06 01:57:00** = 116 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4182.4, VSA=3.72x, bien do nen=11.1 gia.
- MOVE truoc climax: dai 24.3 gia, 33 nen, hieu suat huong 0.45.
- Bien CHINH (net lien, climax+AR): 4182.4 - 4193.9 = 11.5 gia (0.27% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4182.4 - 4204.8 = 22.4 gia.
- Ty le bien phu/bien chinh: **1.95x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.72x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.36, ty le volume nhip cuoi/dau=0.72 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 82314..82318 (2026-07-06 01:00:00), effort(VSA TB)=2.72x, result(bien do/ATR)=5.85, ty le er=0.46 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-06 00:01:00 | 2026-07-06 00:26:00 | 26 |
| B | 2026-07-06 00:27:00 | 2026-07-06 00:59:00 | 33 |
| C | 2026-07-06 01:00:00 | 2026-07-06 01:31:00 | 32 |
| D | 2026-07-06 01:32:00 | 2026-07-06 01:56:00 | 25 |
| E | 2026-07-06 01:57:00 | 2026-07-06 01:57:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-06 00:01:00 | 4182.4 | A | - | 3.72x | 0.72 |
| AR | 2026-07-06 00:17:00 | 4193.9 | A | - | 0.59x | 0.24 |
| ST[A] | 2026-07-06 00:26:00 | 4183.0 | A | - | 3.43x | 0.70 |
| LPS[C] | 2026-07-06 01:00:00 | 4184.3 | C | - | 3.24x | 0.11 |
| mSOS | 2026-07-06 01:16:00 | 4204.8 | B | - | 0.72x | 0.04 |
| SOS | 2026-07-06 01:32:00 | 4203.7 | D | - | 2.33x | 0.26 |
| LPS[D] | 2026-07-06 01:37:00 | 4206.6 | D | - | 1.97x | 0.65 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-05 23:55:00 | 4194.6 | 4195.4 | 4194.0 | 4194.0 | 33 | 0.50x | 0.43 |
| -5 | 2026-07-05 23:56:00 | 4194.6 | 4197.7 | 4194.6 | 4196.5 | 43 | 0.64x | 0.61 |
| -4 | 2026-07-05 23:57:00 | 4197.4 | 4197.4 | 4196.5 | 4196.8 | 20 | 0.31x | 0.67 |
| -3 | 2026-07-05 23:58:00 | 4197.2 | 4197.2 | 4195.8 | 4196.8 | 20 | 0.31x | 0.29 |
| -2 | 2026-07-05 23:59:00 | 4196.2 | 4196.4 | 4195.0 | 4195.2 | 23 | 0.36x | 0.71 |
| -1 | 2026-07-06 00:00:00 | 4195.8 | 4197.5 | 4193.2 | 4193.2 | 96 | 1.43x | 0.60 |
| +0 **<- climax** | 2026-07-06 00:01:00 | 4193.3 | 4193.5 | 4182.4 | 4185.3 | 300 | 3.72x | 0.72 |
| +1 | 2026-07-06 00:02:00 | 4186.0 | 4189.3 | 4186.0 | 4188.0 | 73 | 0.90x | 0.61 |
| +2 | 2026-07-06 00:03:00 | 4188.2 | 4189.4 | 4186.6 | 4188.8 | 51 | 0.61x | 0.21 |
| +3 | 2026-07-06 00:04:00 | 4188.4 | 4189.2 | 4187.3 | 4187.6 | 47 | 0.56x | 0.42 |
| +4 | 2026-07-06 00:05:00 | 4188.0 | 4189.9 | 4188.0 | 4189.4 | 28 | 0.34x | 0.74 |
| +5 | 2026-07-06 00:06:00 | 4188.0 | 4189.8 | 4184.1 | 4184.6 | 98 | 1.36x | 0.60 |
