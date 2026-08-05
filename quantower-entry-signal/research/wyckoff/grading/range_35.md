# Bai lam #35 — Phân phối (DIST)

- Anh: `range_35.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-21 23:10:00 -> 2026-06-22 00:11:00** = 61 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4181.5, VSA=2.69x, bien do nen=2.3 gia.
- MOVE truoc climax: dai 24.6 gia, 70 nen, hieu suat huong 0.39.
- Bien CHINH (net lien, climax+AR): 4170.4 - 4181.5 = 11.1 gia (0.27% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4170.3 - 4181.5 = 11.2 gia.
- Ty le bien phu/bien chinh: **1.01x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.48x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 68684..68694 (2026-06-21 23:35:00), effort(VSA TB)=0.87x, result(bien do/ATR)=6.84, ty le er=0.13 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-21 23:10:00 | 2026-06-21 23:24:00 | 15 |
| B | 2026-06-21 23:25:00 | 2026-06-21 23:34:00 | 10 |
| D | 2026-06-21 23:35:00 | 2026-06-21 23:52:00 | 18 |
| E | 2026-06-21 23:53:00 | 2026-06-22 00:11:00 | 19 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-06-21 23:04:00 | 4176.9 | A | - | 4.48x | 0.84 |
| AR | 2026-06-21 23:16:00 | 4170.4 | A | - | 1.31x | 0.22 |
| ST[A] | 2026-06-21 23:24:00 | 4175.7 | A | - | 1.25x | 0.10 |
| SOW | 2026-06-21 23:35:00 | 4159.8 | D | - | 2.92x | 0.75 |
| LPSY[D] | 2026-06-21 23:48:00 | 4156.7 | D | - | 1.46x | 0.63 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-21 23:04:00 | 4172.6 | 4176.9 | 4172.6 | 4176.2 | 116 | 4.48x | 0.84 |
| -5 | 2026-06-21 23:05:00 | 4175.9 | 4177.0 | 4175.6 | 4176.5 | 45 | 1.63x | 0.43 |
| -4 | 2026-06-21 23:06:00 | 4176.9 | 4177.0 | 4175.3 | 4175.7 | 66 | 2.15x | 0.71 |
| -3 | 2026-06-21 23:07:00 | 4175.3 | 4177.8 | 4175.3 | 4177.7 | 39 | 1.21x | 0.96 |
| -2 | 2026-06-21 23:08:00 | 4177.5 | 4179.0 | 4177.2 | 4177.7 | 144 | 3.80x | 0.11 |
| -1 | 2026-06-21 23:09:00 | 4177.3 | 4179.9 | 4177.0 | 4179.6 | 65 | 1.68x | 0.79 |
| +0 **<- climax** | 2026-06-21 23:10:00 | 4180.0 | 4181.5 | 4179.2 | 4180.7 | 115 | 2.69x | 0.30 |
| +1 | 2026-06-21 23:11:00 | 4180.6 | 4180.6 | 4176.6 | 4177.2 | 91 | 2.00x | 0.85 |
| +2 | 2026-06-21 23:12:00 | 4177.5 | 4177.8 | 4176.3 | 4176.6 | 36 | 0.78x | 0.60 |
| +3 | 2026-06-21 23:13:00 | 4176.6 | 4177.5 | 4176.2 | 4176.2 | 57 | 1.19x | 0.31 |
| +4 | 2026-06-21 23:14:00 | 4176.2 | 4176.2 | 4174.5 | 4174.9 | 85 | 1.66x | 0.76 |
| +5 | 2026-06-21 23:15:00 | 4174.9 | 4174.9 | 4171.6 | 4172.1 | 102 | 1.85x | 0.85 |
