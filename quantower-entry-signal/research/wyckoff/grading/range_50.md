# Bai lam #50 — Phân phối (DIST)

- Anh: `range_50.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-16 11:48:00 -> 2026-07-16 12:51:00** = 63 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4048.4, VSA=1.38x, bien do nen=4.9 gia.
- MOVE truoc climax: dai 16.8 gia, 23 nen, hieu suat huong 0.71.
- Bien CHINH (net lien, climax+AR): 4032.8 - 4048.4 = 15.6 gia (0.39% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4017.4 - 4048.7 = 31.3 gia.
- Ty le bien phu/bien chinh: **2.01x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=5.10x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 94000..94014 (2026-07-16 12:30:00), effort(VSA TB)=1.11x, result(bien do/ATR)=4.09, ty le er=0.27 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-16 11:48:00 | 2026-07-16 11:55:00 | 8 |
| B | 2026-07-16 11:56:00 | 2026-07-16 12:05:00 | 10 |
| C | 2026-07-16 12:06:00 | 2026-07-16 12:42:00 | 37 |
| D | 2026-07-16 12:43:00 | 2026-07-16 12:49:00 | 7 |
| E | 2026-07-16 12:50:00 | 2026-07-16 12:51:00 | 2 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-07-16 11:49:00 | 4047.8 | A | - | 5.10x | 0.65 |
| AR (yếu) | 2026-07-16 11:49:00 | 4032.8 | A | - | 5.10x | 0.65 |
| ST[A] | 2026-07-16 11:55:00 | 4047.3 | A | - | 0.50x | 0.48 |
| LPSY[C] | 2026-07-16 12:06:00 | 4045.4 | C | - | 2.94x | 0.64 |
| mSOW | 2026-07-16 12:16:00 | 4017.4 | B | - | 8.14x | 0.54 |
| SOW | 2026-07-16 12:43:00 | 4007.5 | D | - | 3.36x | 0.94 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-16 11:42:00 | 4037.3 | 4038.9 | 4037.3 | 4038.1 | 57 | 0.76x | 0.50 |
| -5 | 2026-07-16 11:43:00 | 4037.9 | 4041.3 | 4037.0 | 4041.3 | 131 | 1.64x | 0.79 |
| -4 | 2026-07-16 11:44:00 | 4041.3 | 4041.7 | 4039.1 | 4040.6 | 116 | 1.39x | 0.27 |
| -3 | 2026-07-16 11:45:00 | 4040.9 | 4043.0 | 4040.9 | 4042.3 | 171 | 2.05x | 0.67 |
| -2 | 2026-07-16 11:46:00 | 4042.6 | 4045.5 | 4041.5 | 4045.2 | 320 | 3.30x | 0.65 |
| -1 | 2026-07-16 11:47:00 | 4045.5 | 4046.3 | 4043.2 | 4043.9 | 111 | 1.16x | 0.52 |
| +0 **<- climax** | 2026-07-16 11:48:00 | 4043.8 | 4048.4 | 4043.5 | 4048.2 | 133 | 1.38x | 0.90 |
| +1 | 2026-07-16 11:49:00 | 4047.8 | 4047.8 | 4032.8 | 4038.0 | 632 | 5.10x | 0.65 |
| +2 | 2026-07-16 11:50:00 | 4037.8 | 4040.4 | 4034.6 | 4039.7 | 566 | 3.80x | 0.33 |
| +3 | 2026-07-16 11:51:00 | 4040.0 | 4041.8 | 4039.4 | 4041.8 | 114 | 0.75x | 0.75 |
| +4 | 2026-07-16 11:52:00 | 4042.1 | 4043.3 | 4039.1 | 4040.4 | 171 | 1.08x | 0.40 |
| +5 | 2026-07-16 11:53:00 | 4040.5 | 4044.0 | 4040.5 | 4043.4 | 103 | 0.64x | 0.83 |
