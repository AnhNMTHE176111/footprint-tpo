# Bai lam #32 — Tái phân phối (RE-DIST)

- Anh: `range_32.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-10 14:58:00 -> 2026-06-10 22:02:00** = 364 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4139.7, VSA=1.57x, bien do nen=5.3 gia.
- MOVE truoc climax: dai 53.1 gia, 65 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4139.7 - 4159.2 = 19.5 gia (0.47% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4126.6 - 4159.7 = 33.1 gia.
- Ty le bien phu/bien chinh: **1.70x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.83x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.43, ty le volume nhip cuoi/dau=0.75 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.29, ty le volume nhip cuoi/dau=0.22 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 58958..58975 (2026-06-10 17:28:00), effort(VSA TB)=0.94x, result(bien do/ATR)=0.20, ty le er=4.79 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-10 14:58:00 | 2026-06-10 15:19:00 | 22 |
| B | 2026-06-10 15:20:00 | 2026-06-10 19:54:00 | 275 |
| D | 2026-06-10 19:55:00 | 2026-06-10 19:55:00 | 1 |
| E | 2026-06-10 19:56:00 | 2026-06-10 22:02:00 | 67 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-10 14:56:00 | 4147.9 | A | - | 3.83x | 0.73 |
| AR | 2026-06-10 15:02:00 | 4159.2 | A | - | 1.00x | 0.67 |
| ST[A] | 2026-06-10 15:19:00 | 4135.9 | A | - | 1.36x | 0.31 |
| mSOW | 2026-06-10 15:48:00 | 4131.5 | B | - | 3.90x | 0.44 |
| mSOW | 2026-06-10 17:50:00 | 4126.6 | B | - | 3.46x | 0.13 |
| SOW | 2026-06-10 19:55:00 | 4107.4 | D | - | 2.60x | 0.85 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-10 14:52:00 | 4162.8 | 4162.8 | 4160.3 | 4162.1 | 157 | 0.77x | 0.28 |
| -5 | 2026-06-10 14:53:00 | 4162.1 | 4165.6 | 4162.1 | 4163.3 | 180 | 0.88x | 0.34 |
| -4 | 2026-06-10 14:54:00 | 4163.0 | 4164.0 | 4160.0 | 4160.8 | 141 | 0.69x | 0.55 |
| -3 | 2026-06-10 14:55:00 | 4160.8 | 4161.0 | 4156.4 | 4156.9 | 332 | 1.55x | 0.85 |
| -2 | 2026-06-10 14:56:00 | 4157.0 | 4157.3 | 4147.9 | 4150.1 | 969 | 3.83x | 0.73 |
| -1 | 2026-06-10 14:57:00 | 4150.7 | 4151.4 | 4140.6 | 4141.5 | 893 | 3.09x | 0.85 |
| +0 **<- climax** | 2026-06-10 14:58:00 | 4141.5 | 4145.0 | 4139.7 | 4142.4 | 486 | 1.57x | 0.17 |
| +1 | 2026-06-10 14:59:00 | 4142.4 | 4148.0 | 4141.7 | 4147.1 | 306 | 0.98x | 0.75 |
| +2 | 2026-06-10 15:00:00 | 4147.7 | 4151.3 | 4145.5 | 4146.5 | 469 | 1.41x | 0.21 |
| +3 | 2026-06-10 15:01:00 | 4146.5 | 4158.9 | 4146.2 | 4158.4 | 396 | 1.15x | 0.94 |
| +4 | 2026-06-10 15:02:00 | 4158.3 | 4159.2 | 4154.4 | 4155.1 | 356 | 1.00x | 0.67 |
| +5 | 2026-06-10 15:03:00 | 4155.0 | 4156.6 | 4151.2 | 4151.2 | 301 | 0.82x | 0.70 |
