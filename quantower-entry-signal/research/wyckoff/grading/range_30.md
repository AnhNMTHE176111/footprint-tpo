# Bai lam #30 — Phân phối (DIST)

- Anh: `range_30.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-10 06:08:00 -> 2026-06-10 08:02:00** = 114 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4245.5, VSA=2.77x, bien do nen=2.9 gia.
- MOVE truoc climax: dai 38.0 gia, 83 nen, hieu suat huong 0.38.
- Bien CHINH (net lien, climax+AR): 4231.1 - 4245.5 = 14.4 gia (0.34% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4228.6 - 4245.5 = 16.9 gia.
- Ty le bien phu/bien chinh: **1.17x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.77x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 58317..58318 (2026-06-10 06:31:00), effort(VSA TB)=1.07x, result(bien do/ATR)=1.75, ty le er=0.61 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-10 06:08:00 | 2026-06-10 06:27:00 | 20 |
| B | 2026-06-10 06:28:00 | 2026-06-10 07:09:00 | 42 |
| D | 2026-06-10 07:10:00 | 2026-06-10 07:34:00 | 25 |
| E | 2026-06-10 07:35:00 | 2026-06-10 08:02:00 | 28 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-06-10 06:08:00 | 4245.5 | A | - | 2.77x | 0.21 |
| AR | 2026-06-10 06:24:00 | 4231.1 | A | - | 0.96x | 0.69 |
| ST[A] | 2026-06-10 06:27:00 | 4239.2 | A | - | 1.24x | 0.66 |
| mSOW | 2026-06-10 06:44:00 | 4228.6 | B | - | 2.42x | 0.35 |
| SOW | 2026-06-10 07:10:00 | 4228.3 | D | - | 1.69x | 0.69 |
| LPSY[D] | 2026-06-10 07:16:00 | 4225.9 | D | - | 0.44x | 0.96 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-10 06:02:00 | 4230.5 | 4232.7 | 4230.4 | 4231.5 | 65 | 0.63x | 0.43 |
| -5 | 2026-06-10 06:03:00 | 4232.0 | 4233.4 | 4231.5 | 4233.0 | 80 | 0.77x | 0.53 |
| -4 | 2026-06-10 06:04:00 | 4233.7 | 4235.9 | 4233.5 | 4234.1 | 125 | 1.19x | 0.17 |
| -3 | 2026-06-10 06:05:00 | 4234.0 | 4235.2 | 4232.4 | 4234.6 | 81 | 0.78x | 0.21 |
| -2 | 2026-06-10 06:06:00 | 4234.7 | 4239.5 | 4234.4 | 4239.3 | 216 | 1.93x | 0.90 |
| -1 | 2026-06-10 06:07:00 | 4239.2 | 4243.1 | 4237.0 | 4243.1 | 246 | 2.04x | 0.64 |
| +0 **<- climax** | 2026-06-10 06:08:00 | 4243.2 | 4245.5 | 4242.6 | 4242.6 | 362 | 2.77x | 0.21 |
| +1 | 2026-06-10 06:09:00 | 4242.8 | 4243.4 | 4235.9 | 4236.9 | 276 | 2.04x | 0.79 |
| +2 | 2026-06-10 06:10:00 | 4237.1 | 4237.8 | 4233.8 | 4233.8 | 155 | 1.14x | 0.83 |
| +3 | 2026-06-10 06:11:00 | 4234.0 | 4235.2 | 4232.6 | 4234.0 | 95 | 0.70x | 0.00 |
| +4 | 2026-06-10 06:12:00 | 4233.2 | 4235.7 | 4232.0 | 4235.7 | 102 | 0.74x | 0.68 |
| +5 | 2026-06-10 06:13:00 | 4236.0 | 4238.9 | 4235.0 | 4237.6 | 79 | 0.57x | 0.41 |
