# Bai lam #22 — Tái phân phối (RE-DIST)

- Anh: `range_22.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-25 01:47:00 -> 2026-05-25 06:40:00** = 257 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4594.7, VSA=3.10x, bien do nen=2.2 gia.
- Bien CHINH (net lien, climax+AR): 4594.7 - 4602.4 = 7.7 gia (0.17% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4590.8 - 4604.3 = 13.5 gia.
- Ty le bien phu/bien chinh: **1.75x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.10x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.30, ty le volume nhip cuoi/dau=0.58 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 41824..41845 (2026-05-25 02:48:00), effort(VSA TB)=1.42x, result(bien do/ATR)=0.19, ty le er=7.58 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-25 01:47:00 | 2026-05-25 02:17:00 | 28 |
| B | 2026-05-25 02:18:00 | 2026-05-25 05:01:00 | 146 |
| C | 2026-05-25 05:05:00 | 2026-05-25 06:11:00 | 58 |
| D | 2026-05-25 06:12:00 | 2026-05-25 06:39:00 | 25 |
| E | 2026-05-25 06:40:00 | 2026-05-25 06:40:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-05-25 01:47:00 | 4594.7 | A | - | 3.10x | 0.73 |
| AR | 2026-05-25 02:09:00 | 4602.4 | A | - | 2.50x | 0.12 |
| ST[A] | 2026-05-25 02:17:00 | 4592.6 | A | - | 1.30x | 0.00 |
| mSOS | 2026-05-25 02:45:00 | 4604.3 | B | - | 3.05x | 0.50 |
| ST[B] | 2026-05-25 02:59:00 | 4593.4 | B | - | 0.81x | 0.08 |
| mSOW | 2026-05-25 04:51:00 | 4598.7 | B | - | 4.67x | 1.00 |
| LPSY[C] | 2026-05-25 05:05:00 | 4599.6 | C | - | 1.08x | 0.86 |
| SOW | 2026-05-25 06:12:00 | 4585.7 | D | - | 0.61x | 1.00 |
| LPSY[D] | 2026-05-25 06:26:00 | 4591.0 | D | - | 0.36x | 1.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-25 01:41:00 | 4603.6 | 4603.9 | 4603.0 | 4603.0 | 12 | 1.89x | 0.67 |
| -5 | 2026-05-25 01:42:00 | 4602.2 | 4602.2 | 4601.1 | 4601.1 | 6 | 0.97x | 1.00 |
| -4 | 2026-05-25 01:43:00 | 4600.2 | 4601.5 | 4600.2 | 4601.5 | 5 | 0.79x | 1.00 |
| -3 | 2026-05-25 01:44:00 | 4601.4 | 4601.4 | 4598.0 | 4598.1 | 6 | 1.01x | 0.97 |
| -2 | 2026-05-25 01:45:00 | 4596.9 | 4597.4 | 4596.9 | 4597.4 | 13 | 2.30x | 1.00 |
| -1 | 2026-05-25 01:46:00 | 4597.2 | 4597.2 | 4594.9 | 4594.9 | 12 | 1.95x | 1.00 |
| +0 **<- climax** | 2026-05-25 01:47:00 | 4594.9 | 4596.9 | 4594.7 | 4596.5 | 22 | 3.10x | 0.73 |
| +1 | 2026-05-25 01:48:00 | 4595.1 | 4599.1 | 4595.1 | 4599.1 | 6 | 0.86x | 1.00 |
| +2 | 2026-05-25 01:49:00 | 4597.6 | 4597.6 | 4597.6 | 4597.6 | 1 | 0.14x | 0.00 |
| +3 | 2026-05-25 01:50:00 | 4597.0 | 4597.0 | 4595.9 | 4595.9 | 2 | 0.29x | 1.00 |
| +4 | 2026-05-25 01:51:00 | 4597.6 | 4599.4 | 4597.6 | 4599.4 | 5 | 0.76x | 1.00 |
| +5 | 2026-05-25 01:52:00 | 4599.8 | 4599.8 | 4598.3 | 4598.3 | 3 | 0.50x | 1.00 |
