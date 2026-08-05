# Bai lam #49 — Tái phân phối (RE-DIST)

- Anh: `range_49.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-16 01:24:00 -> 2026-07-16 03:49:00** = 145 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4041.7, VSA=1.53x, bien do nen=2.7 gia.
- Bien CHINH (net lien, climax+AR): 4041.7 - 4051.6 = 9.9 gia (0.24% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4041.2 - 4051.6 = 10.4 gia.
- Ty le bien phu/bien chinh: **1.05x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=1.53x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 93382..93401 (2026-07-16 02:16:00), effort(VSA TB)=1.11x, result(bien do/ATR)=7.09, ty le er=0.16 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-16 01:24:00 | 2026-07-16 01:53:00 | 30 |
| B | 2026-07-16 01:54:00 | 2026-07-16 02:15:00 | 22 |
| D | 2026-07-16 02:16:00 | 2026-07-16 02:40:00 | 25 |
| E | 2026-07-16 02:41:00 | 2026-07-16 03:49:00 | 69 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-07-16 01:24:00 | 4041.7 | A | - | 1.53x | 0.22 |
| AR | 2026-07-16 01:41:00 | 4051.6 | A | - | 2.88x | 0.20 |
| ST[A] | 2026-07-16 01:53:00 | 4042.5 | A | - | 0.96x | 0.14 |
| SOW | 2026-07-16 02:16:00 | 4035.8 | D | - | 2.76x | 0.39 |
| LPSY[D] | 2026-07-16 02:22:00 | 4040.4 | D | - | 1.57x | 0.71 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-16 01:18:00 | 4046.0 | 4047.0 | 4044.5 | 4047.0 | 226 | 1.90x | 0.40 |
| -5 | 2026-07-16 01:19:00 | 4046.6 | 4047.1 | 4045.9 | 4046.8 | 56 | 0.54x | 0.17 |
| -4 | 2026-07-16 01:20:00 | 4047.0 | 4047.6 | 4046.5 | 4047.2 | 33 | 0.39x | 0.18 |
| -3 | 2026-07-16 01:21:00 | 4047.2 | 4049.2 | 4047.2 | 4048.1 | 56 | 0.69x | 0.45 |
| -2 | 2026-07-16 01:22:00 | 4048.1 | 4049.9 | 4047.4 | 4047.7 | 54 | 0.72x | 0.16 |
| -1 | 2026-07-16 01:23:00 | 4047.9 | 4048.3 | 4043.8 | 4043.8 | 89 | 1.19x | 0.91 |
| +0 **<- climax** | 2026-07-16 01:24:00 | 4044.1 | 4044.4 | 4041.7 | 4043.5 | 114 | 1.53x | 0.22 |
| +1 | 2026-07-16 01:25:00 | 4043.4 | 4044.7 | 4042.8 | 4043.7 | 86 | 1.12x | 0.16 |
| +2 | 2026-07-16 01:26:00 | 4043.7 | 4043.7 | 4042.0 | 4042.9 | 48 | 0.63x | 0.47 |
| +3 | 2026-07-16 01:27:00 | 4043.1 | 4043.5 | 4041.6 | 4042.0 | 27 | 0.36x | 0.58 |
| +4 | 2026-07-16 01:28:00 | 4041.9 | 4042.0 | 4039.4 | 4041.7 | 103 | 1.31x | 0.08 |
| +5 | 2026-07-16 01:29:00 | 4041.6 | 4043.6 | 4041.4 | 4042.7 | 77 | 0.94x | 0.50 |
