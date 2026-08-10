# Bai lam #11 — Phân phối (DIST)

- Anh: `range_11.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-23 12:06:00 -> 2026-04-23 17:40:00** = 240 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4790.9, VSA=3.68x, bien do nen=3.7 gia.
- MOVE truoc climax: dai 43.0 gia, 64 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4779.2 - 4790.9 = 11.7 gia (0.24% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4768.9 - 4795.6 = 26.7 gia.
- Ty le bien phu/bien chinh: **2.28x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.68x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.53, ty le volume nhip cuoi/dau=1.35 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.31, ty le volume nhip cuoi/dau=0.54 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 24083..24085 (2026-04-23 13:16:00), effort(VSA TB)=1.81x, result(bien do/ATR)=4.45, ty le er=0.41 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-23 12:06:00 | 2026-04-23 12:31:00 | 23 |
| B | 2026-04-23 12:32:00 | 2026-04-23 16:48:00 | 178 |
| C | 2026-04-23 16:51:00 | 2026-04-23 17:04:00 | 6 |
| D | 2026-04-23 17:05:00 | 2026-04-23 17:30:00 | 25 |
| E | 2026-04-23 17:31:00 | 2026-04-23 17:40:00 | 9 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-04-23 12:06:00 | 4790.9 | A | - | 3.68x | 0.38 |
| AR | 2026-04-23 12:16:00 | 4779.2 | A | - | 0.19x | 0.00 |
| ST[A] | 2026-04-23 12:31:00 | 4794.1 | A | - | 1.38x | 0.72 |
| UTAD | 2026-04-23 12:43:00 | 4795.6 | C | confirmed | 1.82x | 0.00 |
| mSOS | 2026-04-23 15:19:00 | 4792.4 | B | - | 0.91x | 1.00 |
| mSOW | 2026-04-23 16:05:00 | 4768.9 | B | - | 0.56x | 0.00 |
| LPSY[C] | 2026-04-23 16:51:00 | 4789.8 | C | - | 2.92x | 0.00 |
| SOW | 2026-04-23 17:05:00 | 4774.7 | D | - | 3.21x | 0.37 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-23 12:00:00 | 4771.9 | 4778.6 | 4771.9 | 4778.3 | 15 | 5.45x | 0.96 |
| -5 | 2026-04-23 12:01:00 | 4778.9 | 4783.6 | 4778.8 | 4783.6 | 10 | 3.12x | 0.98 |
| -4 | 2026-04-23 12:02:00 | 4782.9 | 4784.5 | 4782.9 | 4784.5 | 2 | 0.62x | 1.00 |
| -3 | 2026-04-23 12:03:00 | 4783.6 | 4783.6 | 4782.8 | 4782.8 | 3 | 0.90x | 1.00 |
| -2 | 2026-04-23 12:04:00 | 4782.0 | 4784.1 | 4782.0 | 4784.1 | 4 | 1.16x | 1.00 |
| -1 | 2026-04-23 12:05:00 | 4784.5 | 4786.7 | 4784.5 | 4786.7 | 5 | 1.39x | 1.00 |
| +0 **<- climax** | 2026-04-23 12:06:00 | 4787.3 | 4790.9 | 4787.2 | 4788.7 | 16 | 3.68x | 0.38 |
| +1 | 2026-04-23 12:07:00 | 4788.0 | 4788.0 | 4788.0 | 4788.0 | 1 | 0.24x | 0.00 |
| +2 | 2026-04-23 12:08:00 | 4783.3 | 4784.6 | 4782.4 | 4783.3 | 16 | 3.33x | 0.00 |
| +3 | 2026-04-23 12:09:00 | 4783.5 | 4783.5 | 4783.5 | 4783.5 | 1 | 0.21x | 0.00 |
| +4 | 2026-04-23 12:10:00 | 4783.0 | 4783.0 | 4781.8 | 4781.8 | 2 | 0.41x | 1.00 |
| +5 | 2026-04-23 12:11:00 | 4781.6 | 4782.9 | 4781.5 | 4781.5 | 12 | 2.22x | 0.07 |
