# Bai lam #39 — Tích lũy (ACC)

- Anh: `range_39.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-30 12:58:00 -> 2026-06-30 15:14:00** = 136 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4022.1, VSA=2.60x, bien do nen=2.7 gia.
- MOVE truoc climax: dai 25.6 gia, 72 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4022.1 - 4047.5 = 25.4 gia (0.63% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4022.1 - 4047.5 = 25.4 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.33x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.52, ty le volume nhip cuoi/dau=1.30 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 77819..77826 (2026-06-30 14:00:00), effort(VSA TB)=1.21x, result(bien do/ATR)=2.16, ty le er=0.56 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-30 12:58:00 | 2026-06-30 13:24:00 | 27 |
| B | 2026-06-30 13:25:00 | 2026-06-30 13:36:00 | 12 |
| C | 2026-06-30 13:37:00 | 2026-06-30 14:08:00 | 32 |
| D | 2026-06-30 14:09:00 | 2026-06-30 14:22:00 | 14 |
| E | 2026-06-30 14:23:00 | 2026-06-30 15:14:00 | 52 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-30 13:00:00 | 4022.9 | A | - | 3.33x | 0.66 |
| AR | 2026-06-30 13:20:00 | 4047.5 | A | - | 3.03x | 0.76 |
| ST[A] | 2026-06-30 13:24:00 | 4033.0 | A | - | 1.78x | 0.85 |
| LPS[C] | 2026-06-30 13:37:00 | 4027.2 | C | - | 1.09x | 0.61 |
| SOS | 2026-06-30 14:09:00 | 4058.0 | D | - | 4.17x | 0.87 |
| LPS[D] | 2026-06-30 14:12:00 | 4051.6 | D | - | 1.36x | 0.25 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-30 12:52:00 | 4028.2 | 4029.3 | 4027.2 | 4027.6 | 59 | 0.94x | 0.29 |
| -5 | 2026-06-30 12:53:00 | 4027.7 | 4029.4 | 4026.1 | 4028.6 | 75 | 1.26x | 0.27 |
| -4 | 2026-06-30 12:54:00 | 4028.4 | 4029.3 | 4026.5 | 4027.9 | 56 | 0.93x | 0.18 |
| -3 | 2026-06-30 12:55:00 | 4028.1 | 4028.1 | 4025.8 | 4026.4 | 155 | 2.40x | 0.74 |
| -2 | 2026-06-30 12:56:00 | 4026.6 | 4028.5 | 4024.1 | 4024.7 | 201 | 3.06x | 0.43 |
| -1 | 2026-06-30 12:57:00 | 4025.0 | 4025.5 | 4024.4 | 4024.9 | 76 | 1.20x | 0.09 |
| +0 **<- climax** | 2026-06-30 12:58:00 | 4024.6 | 4024.8 | 4022.1 | 4022.7 | 181 | 2.60x | 0.70 |
| +1 | 2026-06-30 12:59:00 | 4022.6 | 4025.5 | 4022.6 | 4023.9 | 127 | 1.72x | 0.45 |
| +2 | 2026-06-30 13:00:00 | 4023.7 | 4031.8 | 4022.9 | 4029.6 | 286 | 3.33x | 0.66 |
| +3 | 2026-06-30 13:01:00 | 4029.1 | 4030.6 | 4028.5 | 4029.0 | 76 | 0.88x | 0.05 |
| +4 | 2026-06-30 13:02:00 | 4029.2 | 4031.2 | 4028.3 | 4030.3 | 67 | 0.77x | 0.38 |
| +5 | 2026-06-30 13:03:00 | 4031.0 | 4031.6 | 4027.3 | 4027.6 | 90 | 0.99x | 0.79 |
