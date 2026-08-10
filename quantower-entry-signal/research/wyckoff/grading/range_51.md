# Bai lam #51 — Tích lũy (ACC)

- Anh: `range_51.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-12 22:48:00 -> 2026-07-13 00:22:00** = 93 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4076.8, VSA=7.19x, bien do nen=7.9 gia.
- MOVE truoc climax: dai 24.2 gia, 47 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4076.8 - 4088.8 = 12.0 gia (0.29% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4075.8 - 4091.4 = 15.6 gia.
- Ty le bien phu/bien chinh: **1.30x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=7.19x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 89107..89112 (2026-07-12 23:41:00), effort(VSA TB)=2.24x, result(bien do/ATR)=6.04, ty le er=0.37 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-12 22:48:00 | 2026-07-12 23:04:00 | 17 |
| B | 2026-07-12 23:05:00 | 2026-07-12 23:44:00 | 39 |
| C | 2026-07-12 23:45:00 | 2026-07-12 23:56:00 | 12 |
| D | 2026-07-12 23:57:00 | 2026-07-13 00:21:00 | 25 |
| E | 2026-07-13 00:22:00 | 2026-07-13 00:22:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-12 22:48:00 | 4076.8 | A | - | 7.19x | 0.25 |
| AR | 2026-07-12 22:52:00 | 4088.8 | A | - | 0.36x | 0.90 |
| ST[A] | 2026-07-12 23:04:00 | 4075.8 | A | - | 1.80x | 0.41 |
| LPS[C] | 2026-07-12 23:45:00 | 4083.7 | C | - | 0.91x | 0.40 |
| mSOS | 2026-07-12 23:52:00 | 4091.4 | B | - | 1.08x | 0.33 |
| SOS | 2026-07-12 23:57:00 | 4091.5 | D | - | 2.79x | 0.63 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-12 22:42:00 | 4086.5 | 4086.8 | 4085.9 | 4085.9 | 12 | 0.34x | 0.67 |
| -5 | 2026-07-12 22:43:00 | 4085.8 | 4086.8 | 4085.6 | 4086.1 | 21 | 0.60x | 0.25 |
| -4 | 2026-07-12 22:44:00 | 4086.1 | 4087.2 | 4085.6 | 4085.6 | 28 | 0.79x | 0.31 |
| -3 | 2026-07-12 22:45:00 | 4086.4 | 4086.5 | 4084.6 | 4085.4 | 44 | 1.27x | 0.53 |
| -2 | 2026-07-12 22:46:00 | 4085.1 | 4086.1 | 4084.6 | 4086.1 | 36 | 1.11x | 0.67 |
| -1 | 2026-07-12 22:47:00 | 4086.2 | 4086.8 | 4083.6 | 4083.6 | 47 | 1.42x | 0.81 |
| +0 **<- climax** | 2026-07-12 22:48:00 | 4084.0 | 4084.7 | 4076.8 | 4082.0 | 359 | 7.19x | 0.25 |
| +1 | 2026-07-12 22:49:00 | 4082.5 | 4087.1 | 4082.4 | 4085.9 | 136 | 2.43x | 0.72 |
| +2 | 2026-07-12 22:50:00 | 4085.6 | 4086.9 | 4085.4 | 4085.8 | 42 | 0.78x | 0.13 |
| +3 | 2026-07-12 22:51:00 | 4086.5 | 4088.3 | 4085.7 | 4088.0 | 40 | 0.74x | 0.58 |
| +4 | 2026-07-12 22:52:00 | 4088.6 | 4088.8 | 4086.8 | 4086.8 | 20 | 0.36x | 0.90 |
| +5 | 2026-07-12 22:53:00 | 4087.2 | 4087.2 | 4084.2 | 4084.8 | 38 | 0.67x | 0.80 |
