# Bai lam #19 — Tái phân phối (RE-DIST)

- Anh: `range_19.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-14 19:48:00 -> 2026-05-14 22:18:00** = 49 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4693.1, VSA=3.50x, bien do nen=1.2 gia.
- Bien CHINH (net lien, climax+AR): 4693.1 - 4704.8 = 11.7 gia (0.25% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4692.7 - 4704.8 = 12.1 gia.
- Ty le bien phu/bien chinh: **1.03x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.47x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 35344..35350 (2026-05-14 20:10:00), effort(VSA TB)=1.39x, result(bien do/ATR)=6.36, ty le er=0.22 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-14 19:48:00 | 2026-05-14 19:48:00 | 1 |
| B | 2026-05-14 19:49:00 | 2026-05-14 20:00:00 | 12 |
| C | 2026-05-14 20:02:00 | 2026-05-14 20:13:00 | 11 |
| D | 2026-05-14 20:14:00 | 2026-05-14 22:16:00 | 25 |
| E | 2026-05-14 22:18:00 | 2026-05-14 22:18:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| AR (yếu) | 2026-05-14 19:34:00 | 4704.8 | A | - | 1.33x | 1.00 |
| SC? | 2026-05-14 19:38:00 | 4699.3 | A | - | 4.47x | 1.00 |
| ST[A] | 2026-05-14 19:48:00 | 4693.1 | A | - | 3.50x | 0.25 |
| LPSY[C] | 2026-05-14 20:02:00 | 4696.5 | C | - | 1.33x | 0.11 |
| SOW | 2026-05-14 20:14:00 | 4689.0 | D | - | 2.65x | 1.00 |
| LPSY[D] | 2026-05-14 20:42:00 | 4690.9 | D | - | 0.76x | 0.60 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-14 19:42:00 | 4697.9 | 4697.9 | 4697.3 | 4697.3 | 2 | 0.49x | 1.00 |
| -5 | 2026-05-14 19:43:00 | 4696.3 | 4696.3 | 4695.4 | 4695.9 | 9 | 2.17x | 0.44 |
| -4 | 2026-05-14 19:44:00 | 4695.3 | 4696.6 | 4695.3 | 4696.6 | 5 | 1.15x | 1.00 |
| -3 | 2026-05-14 19:45:00 | 4694.9 | 4696.4 | 4694.7 | 4696.4 | 6 | 1.38x | 0.88 |
| -2 | 2026-05-14 19:46:00 | 4696.1 | 4696.1 | 4694.9 | 4695.6 | 3 | 0.67x | 0.42 |
| -1 | 2026-05-14 19:47:00 | 4694.2 | 4694.2 | 4694.0 | 4694.0 | 3 | 0.67x | 1.00 |
| +0 **<- climax** | 2026-05-14 19:48:00 | 4694.0 | 4694.3 | 4693.1 | 4694.3 | 18 | 3.50x | 0.25 |
| +1 | 2026-05-14 19:49:00 | 4696.8 | 4697.1 | 4696.5 | 4697.1 | 4 | 0.75x | 0.50 |
| +2 | 2026-05-14 19:50:00 | 4696.4 | 4696.9 | 4696.4 | 4696.9 | 2 | 0.38x | 1.00 |
| +3 | 2026-05-14 19:51:00 | 4695.8 | 4695.8 | 4695.8 | 4695.8 | 1 | 0.21x | 0.00 |
| +4 | 2026-05-14 19:52:00 | 4696.5 | 4697.0 | 4696.5 | 4697.0 | 2 | 0.44x | 1.00 |
| +5 | 2026-05-14 19:53:00 | 4697.3 | 4697.4 | 4697.3 | 4697.4 | 2 | 0.44x | 1.00 |
