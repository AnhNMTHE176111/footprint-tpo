# Bai lam #03 — Phân phối (DIST)

- Anh: `range_03.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-01-21 06:34:00 -> 2026-01-22 05:50:00** = 127 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4989.4, VSA=0.85x, bien do nen=0.0 gia.
- MOVE truoc climax: dai 188.8 gia, 175 nen, hieu suat huong 0.38.
- Bien CHINH (net lien, climax+AR): 4941.5 - 4989.4 = 47.9 gia (0.96% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4916.4 - 4989.7 = 73.3 gia.
- Ty le bien phu/bien chinh: **1.53x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=13.62x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.93, ty le volume nhip cuoi/dau=0.69 (can kiet).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 2528..2537 (2026-01-21 15:11:00), effort(VSA TB)=0.81x, result(bien do/ATR)=9.46, ty le er=0.09 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-01-21 06:34:00 | 2026-01-21 09:31:00 | 18 |
| B | 2026-01-21 11:29:00 | 2026-01-21 20:52:00 | 70 |
| D | 2026-01-21 21:00:00 | 2026-01-22 01:57:00 | 25 |
| E | 2026-01-22 02:03:00 | 2026-01-22 05:50:00 | 15 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-01-21 06:57:00 | 4961.6 | A | - | 13.62x | 0.72 |
| AR | 2026-01-21 07:20:00 | 4941.5 | A | - | 0.12x | 0.00 |
| ST[A] | 2026-01-21 09:31:00 | 4985.9 | A | - | 0.13x | 0.00 |
| mSOW | 2026-01-21 17:31:00 | 4916.4 | B | - | 0.57x | 0.00 |
| SOW | 2026-01-21 21:00:00 | 4928.5 | D | - | 5.00x | 0.77 |
| LPSY[D] | 2026-01-22 01:21:00 | 4911.9 | D | - | 1.00x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-01-21 05:17:00 | 4978.2 | 4978.2 | 4978.2 | 4978.2 | 1 | 0.62x | 0.00 |
| -5 | 2026-01-21 05:19:00 | 4981.1 | 4981.1 | 4980.7 | 4980.7 | 2 | 1.21x | 1.00 |
| -4 | 2026-01-21 05:34:00 | 4984.5 | 4984.9 | 4984.5 | 4984.9 | 4 | 2.22x | 1.00 |
| -3 | 2026-01-21 05:42:00 | 4977.0 | 4977.0 | 4977.0 | 4977.0 | 1 | 0.56x | 0.00 |
| -2 | 2026-01-21 06:04:00 | 4977.0 | 4977.0 | 4976.1 | 4976.1 | 11 | 4.78x | 1.00 |
| -1 | 2026-01-21 06:09:00 | 4975.2 | 4977.6 | 4975.2 | 4977.6 | 2 | 0.87x | 1.00 |
| +0 **<- climax** | 2026-01-21 06:34:00 | 4989.4 | 4989.4 | 4989.4 | 4989.4 | 2 | 0.85x | 0.00 |
| +1 | 2026-01-21 06:41:00 | 4975.6 | 4975.7 | 4975.6 | 4975.7 | 2 | 0.83x | 1.00 |
| +2 | 2026-01-21 06:48:00 | 4965.0 | 4965.0 | 4965.0 | 4965.0 | 10 | 3.77x | 0.00 |
| +3 | 2026-01-21 06:57:00 | 4961.6 | 4961.6 | 4954.2 | 4956.3 | 111 | 13.62x | 0.72 |
| +4 | 2026-01-21 07:04:00 | 4944.0 | 4944.0 | 4944.0 | 4944.0 | 1 | 0.12x | 0.00 |
| +5 | 2026-01-21 07:07:00 | 4950.6 | 4950.6 | 4947.2 | 4947.2 | 3 | 0.37x | 1.00 |
