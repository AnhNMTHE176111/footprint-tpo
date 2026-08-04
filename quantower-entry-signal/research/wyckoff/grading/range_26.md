# Bai lam #26 — Phân phối (DIST)

- Anh: `range_26.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-04 16:19:00 -> 2026-06-04 17:50:00** = 91 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4513.2, VSA=1.92x, bien do nen=2.7 gia.
- Bien CHINH (net lien, climax+AR): 4507.2 - 4513.2 = 6.0 gia (0.13% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4507.2 - 4513.2 = 6.0 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=1.92x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 53418..53433 (2026-06-04 17:01:00), effort(VSA TB)=1.44x, result(bien do/ATR)=2.04, ty le er=0.71 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-04 16:19:00 | 2026-06-04 16:38:00 | 20 |
| B | 2026-06-04 16:39:00 | 2026-06-04 16:56:00 | 18 |
| C | 2026-06-04 16:57:00 | 2026-06-04 17:14:00 | 18 |
| D | 2026-06-04 17:15:00 | 2026-06-04 17:39:00 | 25 |
| E | 2026-06-04 17:40:00 | 2026-06-04 17:50:00 | 11 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-06-04 16:19:00 | 4513.2 | A | - | 1.92x | 0.30 |
| AR | 2026-06-04 16:32:00 | 4507.2 | A | - | 3.39x | 0.26 |
| ST[A] | 2026-06-04 16:38:00 | 4510.6 | A | - | 0.80x | 0.00 |
| LPSY[C] | 2026-06-04 16:57:00 | 4511.7 | C | - | 2.42x | 0.31 |
| SOW | 2026-06-04 17:15:00 | 4503.4 | D | - | 1.07x | 0.58 |
| LPSY[D] | 2026-06-04 17:17:00 | 4504.1 | D | - | 0.83x | 0.43 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-04 16:13:00 | 4508.1 | 4508.7 | 4507.4 | 4507.6 | 80 | 0.57x | 0.38 |
| -5 | 2026-06-04 16:14:00 | 4507.6 | 4507.7 | 4507.0 | 4507.0 | 42 | 0.30x | 0.86 |
| -4 | 2026-06-04 16:15:00 | 4507.2 | 4509.1 | 4507.2 | 4508.4 | 69 | 0.50x | 0.63 |
| -3 | 2026-06-04 16:16:00 | 4508.3 | 4509.0 | 4507.5 | 4508.4 | 101 | 0.72x | 0.07 |
| -2 | 2026-06-04 16:17:00 | 4508.6 | 4510.3 | 4508.6 | 4509.5 | 111 | 0.78x | 0.53 |
| -1 | 2026-06-04 16:18:00 | 4509.5 | 4511.3 | 4509.5 | 4510.5 | 199 | 1.33x | 0.56 |
| +0 **<- climax** | 2026-06-04 16:19:00 | 4510.5 | 4513.2 | 4510.5 | 4511.3 | 316 | 1.92x | 0.30 |
| +1 | 2026-06-04 16:20:00 | 4511.2 | 4511.2 | 4508.3 | 4510.2 | 337 | 1.93x | 0.34 |
| +2 | 2026-06-04 16:21:00 | 4510.2 | 4511.5 | 4510.0 | 4511.3 | 56 | 0.32x | 0.73 |
| +3 | 2026-06-04 16:22:00 | 4511.3 | 4512.8 | 4511.1 | 4511.9 | 104 | 0.60x | 0.35 |
| +4 | 2026-06-04 16:23:00 | 4511.7 | 4512.3 | 4511.4 | 4511.6 | 64 | 0.37x | 0.11 |
| +5 | 2026-06-04 16:24:00 | 4511.7 | 4512.3 | 4511.7 | 4512.3 | 22 | 0.13x | 1.00 |
