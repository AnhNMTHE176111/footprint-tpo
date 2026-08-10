# Bai lam #24 — Tích lũy (ACC)

- Anh: `range_24.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-26 08:34:00 -> 2026-05-26 11:21:00** = 165 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4553.4, VSA=0.67x, bien do nen=2.3 gia.
- MOVE truoc climax: dai 16.6 gia, 37 nen, hieu suat huong 0.56.
- Bien CHINH (net lien, climax+AR): 4553.4 - 4560.7 = 7.3 gia (0.16% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4551.5 - 4566.1 = 14.6 gia.
- Ty le bien phu/bien chinh: **2.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.96x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.73, ty le volume nhip cuoi/dau=0.51 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 43319..43322 (2026-05-26 09:19:00), effort(VSA TB)=2.81x, result(bien do/ATR)=5.78, ty le er=0.49 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-26 08:34:00 | 2026-05-26 08:59:00 | 26 |
| B | 2026-05-26 09:00:00 | 2026-05-26 09:15:00 | 15 |
| C | 2026-05-26 09:16:00 | 2026-05-26 10:11:00 | 56 |
| D | 2026-05-26 10:12:00 | 2026-05-26 10:27:00 | 16 |
| E | 2026-05-26 10:28:00 | 2026-05-26 11:21:00 | 53 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-26 08:29:00 | 4554.1 | A | - | 2.96x | 0.49 |
| AR | 2026-05-26 08:46:00 | 4560.7 | A | - | 1.02x | 0.00 |
| ST[A] | 2026-05-26 08:59:00 | 4555.7 | A | - | 1.97x | 0.59 |
| Spring | 2026-05-26 09:16:00 | 4551.5 | C | confirmed | 0.87x | 0.46 |
| LPS[C] | 2026-05-26 09:31:00 | 4552.9 | C | - | 1.30x | 0.75 |
| SOS | 2026-05-26 10:12:00 | 4563.6 | D | - | 2.00x | 0.83 |
| LPS[D] | 2026-05-26 10:19:00 | 4560.7 | D | - | 0.31x | 0.43 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-26 08:28:00 | 4558.4 | 4558.4 | 4557.1 | 4557.3 | 31 | 1.64x | 0.85 |
| -5 | 2026-05-26 08:29:00 | 4557.8 | 4557.8 | 4554.1 | 4556.0 | 64 | 2.96x | 0.49 |
| -4 | 2026-05-26 08:30:00 | 4555.7 | 4555.7 | 4553.6 | 4554.9 | 48 | 2.13x | 0.38 |
| -3 | 2026-05-26 08:31:00 | 4555.1 | 4556.2 | 4555.1 | 4555.4 | 9 | 0.40x | 0.27 |
| -2 | 2026-05-26 08:32:00 | 4555.0 | 4555.1 | 4554.2 | 4554.8 | 24 | 1.03x | 0.22 |
| -1 | 2026-05-26 08:33:00 | 4554.4 | 4555.3 | 4554.0 | 4555.3 | 8 | 0.35x | 0.69 |
| +0 **<- climax** | 2026-05-26 08:34:00 | 4555.5 | 4555.7 | 4553.4 | 4554.3 | 15 | 0.67x | 0.52 |
| +1 | 2026-05-26 08:35:00 | 4554.2 | 4555.6 | 4554.1 | 4554.1 | 26 | 1.16x | 0.07 |
| +2 | 2026-05-26 08:36:00 | 4554.9 | 4555.2 | 4554.8 | 4554.8 | 7 | 0.32x | 0.25 |
| +3 | 2026-05-26 08:37:00 | 4555.1 | 4556.6 | 4554.8 | 4556.6 | 17 | 0.75x | 0.83 |
| +4 | 2026-05-26 08:38:00 | 4556.6 | 4557.1 | 4556.1 | 4556.1 | 18 | 0.77x | 0.50 |
| +5 | 2026-05-26 08:39:00 | 4555.9 | 4556.3 | 4555.5 | 4555.7 | 39 | 1.58x | 0.25 |
