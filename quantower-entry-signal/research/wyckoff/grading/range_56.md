# Bai lam #56 — Chưa rõ (BCLX) (DIST?)

- Anh: `range_56.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-24 14:00:00 -> 2026-07-24 20:59:00** = 419 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4073.0, VSA=3.09x, bien do nen=4.4 gia.
- MOVE truoc climax: dai 24.6 gia, 42 nen, hieu suat huong 0.42.
- Bien CHINH (net lien, climax+AR): 4058.4 - 4073.0 = 14.6 gia (0.36% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4051.3 - 4085.2 = 33.9 gia.
- Ty le bien phu/bien chinh: **2.32x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.09x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.23, ty le volume nhip cuoi/dau=0.13 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.31, ty le volume nhip cuoi/dau=1.10 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 102487..102490 (2026-07-24 16:08:00), effort(VSA TB)=1.20x, result(bien do/ATR)=1.75, ty le er=0.69 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-24 14:00:00 | 2026-07-24 14:26:00 | 27 |
| B | 2026-07-24 14:27:00 | 2026-07-24 20:59:00 | 393 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-07-24 14:00:00 | 4073.0 | A | - | 3.09x | 0.70 |
| AR | 2026-07-24 14:17:00 | 4058.4 | A | - | 1.00x | 0.48 |
| ST[A] | 2026-07-24 14:26:00 | 4072.3 | A | - | 1.17x | 0.68 |
| mSOS | 2026-07-24 15:40:00 | 4082.5 | B | - | 0.63x | 0.74 |
| mSOW | 2026-07-24 19:16:00 | 4051.8 | B | - | 2.12x | 0.23 |
| mSOW | 2026-07-24 19:23:00 | 4052.5 | B | provisional | 1.20x | 0.60 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-24 13:54:00 | 4060.6 | 4064.1 | 4060.0 | 4062.3 | 243 | 1.92x | 0.41 |
| -5 | 2026-07-24 13:55:00 | 4062.5 | 4062.5 | 4059.3 | 4060.7 | 192 | 1.49x | 0.56 |
| -4 | 2026-07-24 13:56:00 | 4060.7 | 4063.2 | 4060.7 | 4062.9 | 227 | 1.67x | 0.88 |
| -3 | 2026-07-24 13:57:00 | 4062.1 | 4062.4 | 4060.8 | 4062.4 | 146 | 1.09x | 0.19 |
| -2 | 2026-07-24 13:58:00 | 4062.4 | 4069.7 | 4062.0 | 4069.0 | 703 | 4.24x | 0.86 |
| -1 | 2026-07-24 13:59:00 | 4069.1 | 4071.5 | 4068.2 | 4070.0 | 419 | 2.32x | 0.27 |
| +0 **<- climax** | 2026-07-24 14:00:00 | 4069.9 | 4073.0 | 4068.6 | 4073.0 | 643 | 3.09x | 0.70 |
| +1 | 2026-07-24 14:01:00 | 4072.8 | 4072.9 | 4066.5 | 4069.0 | 740 | 3.09x | 0.59 |
| +2 | 2026-07-24 14:02:00 | 4068.6 | 4071.0 | 4068.4 | 4069.3 | 184 | 0.76x | 0.27 |
| +3 | 2026-07-24 14:03:00 | 4069.4 | 4071.0 | 4067.7 | 4067.9 | 193 | 0.77x | 0.45 |
| +4 | 2026-07-24 14:04:00 | 4067.7 | 4068.2 | 4065.5 | 4065.5 | 136 | 0.54x | 0.81 |
| +5 | 2026-07-24 14:05:00 | 4065.8 | 4067.9 | 4065.8 | 4066.5 | 91 | 0.37x | 0.33 |
