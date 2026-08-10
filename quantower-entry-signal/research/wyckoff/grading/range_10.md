# Bai lam #10 — Tái phân phối (RE-DIST)

- Anh: `range_10.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-21 16:54:00 -> 2026-04-21 17:45:00** = 48 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4762.2, VSA=2.86x, bien do nen=2.4 gia.
- Bien CHINH (net lien, climax+AR): 4762.2 - 4780.5 = 18.3 gia (0.38% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4762.0 - 4780.5 = 18.5 gia.
- Ty le bien phu/bien chinh: **1.01x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.86x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 22683..22685 (2026-04-21 17:01:00), effort(VSA TB)=1.59x, result(bien do/ATR)=7.72, ty le er=0.21 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-21 16:54:00 | 2026-04-21 16:54:00 | 1 |
| B | 2026-04-21 16:55:00 | 2026-04-21 17:00:00 | 6 |
| C | 2026-04-21 17:01:00 | 2026-04-21 17:16:00 | 16 |
| D | 2026-04-21 17:18:00 | 2026-04-21 17:44:00 | 25 |
| E | 2026-04-21 17:45:00 | 2026-04-21 17:45:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| AR (yếu) | 2026-04-21 16:40:00 | 4780.5 | A | - | 0.40x | 1.00 |
| SC? | 2026-04-21 16:54:00 | 4762.2 | A | - | 2.86x | 0.58 |
| ST[A] | 2026-04-21 16:54:00 | 4762.2 | A | - | 2.86x | 0.58 |
| LPSY[C] | 2026-04-21 17:01:00 | 4773.0 | C | - | 2.26x | 0.74 |
| SOW | 2026-04-21 17:18:00 | 4755.3 | D | - | 1.98x | 0.97 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-21 16:48:00 | 4775.5 | 4775.5 | 4775.5 | 4775.5 | 1 | 0.21x | 0.00 |
| -5 | 2026-04-21 16:49:00 | 4775.7 | 4776.0 | 4775.7 | 4776.0 | 2 | 0.47x | 1.00 |
| -4 | 2026-04-21 16:50:00 | 4776.0 | 4776.0 | 4774.6 | 4774.6 | 3 | 0.80x | 1.00 |
| -3 | 2026-04-21 16:51:00 | 4773.3 | 4773.3 | 4769.3 | 4769.3 | 11 | 2.97x | 1.00 |
| -2 | 2026-04-21 16:52:00 | 4768.3 | 4770.0 | 4768.3 | 4770.0 | 5 | 1.41x | 1.00 |
| -1 | 2026-04-21 16:53:00 | 4768.9 | 4768.9 | 4765.5 | 4766.9 | 23 | 4.95x | 0.59 |
| +0 **<- climax** | 2026-04-21 16:54:00 | 4762.4 | 4764.6 | 4762.2 | 4763.8 | 15 | 2.86x | 0.58 |
| +1 | 2026-04-21 16:55:00 | 4763.9 | 4766.3 | 4763.9 | 4765.3 | 5 | 0.96x | 0.58 |
| +2 | 2026-04-21 16:56:00 | 4765.2 | 4765.2 | 4763.1 | 4764.0 | 6 | 1.11x | 0.57 |
| +3 | 2026-04-21 16:57:00 | 4764.9 | 4765.5 | 4764.9 | 4765.4 | 3 | 0.57x | 0.83 |
| +4 | 2026-04-21 16:58:00 | 4765.3 | 4765.4 | 4764.2 | 4764.2 | 10 | 1.82x | 0.92 |
| +5 | 2026-04-21 16:59:00 | 4764.9 | 4765.3 | 4762.7 | 4762.7 | 12 | 2.00x | 0.85 |
