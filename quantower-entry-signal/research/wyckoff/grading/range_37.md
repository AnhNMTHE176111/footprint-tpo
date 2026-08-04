# Bai lam #37 — Tái phân phối (RE-DIST)

- Anh: `range_37.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-30 00:09:00 -> 2026-06-30 00:56:00** = 47 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4017.1, VSA=2.66x, bien do nen=3.2 gia.
- MOVE truoc climax: dai 16.3 gia, 50 nen, hieu suat huong 0.39.
- Bien CHINH (net lien, climax+AR): 4017.1 - 4027.5 = 10.4 gia (0.26% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4016.1 - 4027.5 = 11.4 gia.
- Ty le bien phu/bien chinh: **1.10x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.47x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 77005..77007 (2026-06-30 00:21:00), effort(VSA TB)=0.51x, result(bien do/ATR)=1.64, ty le er=0.31 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-30 00:09:00 | 2026-06-30 00:18:00 | 10 |
| B | 2026-06-30 00:19:00 | 2026-06-30 00:36:00 | 18 |
| D | 2026-06-30 00:37:00 | 2026-06-30 00:50:00 | 14 |
| E | 2026-06-30 00:51:00 | 2026-06-30 00:56:00 | 6 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-30 00:06:00 | 4018.2 | A | - | 4.47x | 0.53 |
| AR | 2026-06-30 00:12:00 | 4027.5 | A | - | 2.55x | 0.63 |
| ST[A] | 2026-06-30 00:18:00 | 4018.3 | A | - | 0.82x | 0.62 |
| SOW | 2026-06-30 00:37:00 | 4010.1 | D | - | 6.90x | 0.55 |
| LPSY[D] | 2026-06-30 00:46:00 | 4007.6 | D | - | 0.42x | 0.48 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-30 00:03:00 | 4023.2 | 4023.6 | 4021.2 | 4022.4 | 73 | 3.13x | 0.33 |
| -5 | 2026-06-30 00:04:00 | 4022.7 | 4023.0 | 4022.0 | 4022.1 | 16 | 0.67x | 0.60 |
| -4 | 2026-06-30 00:05:00 | 4022.0 | 4022.0 | 4020.4 | 4021.1 | 44 | 1.81x | 0.56 |
| -3 | 2026-06-30 00:06:00 | 4021.1 | 4021.6 | 4018.2 | 4019.3 | 138 | 4.47x | 0.53 |
| -2 | 2026-06-30 00:07:00 | 4019.0 | 4021.5 | 4019.0 | 4020.7 | 89 | 2.67x | 0.68 |
| -1 | 2026-06-30 00:08:00 | 4020.5 | 4020.5 | 4018.5 | 4020.1 | 79 | 2.34x | 0.20 |
| +0 **<- climax** | 2026-06-30 00:09:00 | 4020.3 | 4020.3 | 4017.1 | 4018.2 | 103 | 2.66x | 0.66 |
| +1 | 2026-06-30 00:10:00 | 4018.6 | 4022.4 | 4018.6 | 4021.1 | 72 | 1.72x | 0.66 |
| +2 | 2026-06-30 00:11:00 | 4021.2 | 4025.0 | 4020.0 | 4024.8 | 88 | 1.92x | 0.72 |
| +3 | 2026-06-30 00:12:00 | 4024.6 | 4027.5 | 4024.5 | 4026.5 | 133 | 2.55x | 0.63 |
| +4 | 2026-06-30 00:13:00 | 4026.2 | 4027.0 | 4025.2 | 4026.4 | 82 | 1.46x | 0.11 |
| +5 | 2026-06-30 00:14:00 | 4026.1 | 4026.2 | 4023.3 | 4024.7 | 57 | 0.97x | 0.48 |
