# Bai lam #20 — Phân phối (DIST)

- Anh: `range_20.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-21 01:41:00 -> 2026-05-21 02:15:00** = 27 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4605.4, VSA=0.29x, bien do nen=0.4 gia.
- Bien CHINH (net lien, climax+AR): 4597.6 - 4605.4 = 7.8 gia (0.17% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4595.0 - 4605.4 = 10.4 gia.
- Ty le bien phu/bien chinh: **1.33x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=1.15x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 39513..39518 (2026-05-21 02:01:00), effort(VSA TB)=1.25x, result(bien do/ATR)=6.76, ty le er=0.18 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-21 01:41:00 | 2026-05-21 01:41:00 | 1 |
| B | 2026-05-21 01:42:00 | 2026-05-21 02:02:00 | 17 |
| D | 2026-05-21 02:03:00 | 2026-05-21 02:13:00 | 8 |
| E | 2026-05-21 02:14:00 | 2026-05-21 02:15:00 | 2 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-05-21 01:31:00 | 4603.8 | A | - | 1.15x | 0.37 |
| AR (yếu) | 2026-05-21 01:33:00 | 4597.6 | A | - | 0.36x | 1.00 |
| ST[A] | 2026-05-21 01:41:00 | 4605.4 | A | - | 0.29x | 1.00 |
| mSOW | 2026-05-21 01:56:00 | 4595.0 | B | - | 2.41x | 0.95 |
| SOW | 2026-05-21 02:03:00 | 4592.1 | D | - | 1.73x | 1.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-21 01:33:00 | 4597.6 | 4599.1 | 4597.6 | 4599.1 | 4 | 0.36x | 1.00 |
| -5 | 2026-05-21 01:34:00 | 4599.8 | 4600.0 | 4598.3 | 4598.3 | 11 | 0.95x | 0.88 |
| -4 | 2026-05-21 01:35:00 | 4598.2 | 4598.5 | 4598.2 | 4598.5 | 3 | 0.33x | 1.00 |
| -3 | 2026-05-21 01:36:00 | 4601.0 | 4601.0 | 4600.2 | 4600.2 | 3 | 0.34x | 1.00 |
| -2 | 2026-05-21 01:37:00 | 4600.6 | 4600.6 | 4600.6 | 4600.6 | 1 | 0.13x | 0.00 |
| -1 | 2026-05-21 01:38:00 | 4599.0 | 4601.0 | 4599.0 | 4601.0 | 4 | 0.56x | 1.00 |
| +0 **<- climax** | 2026-05-21 01:41:00 | 4605.0 | 4605.4 | 4605.0 | 4605.4 | 2 | 0.29x | 1.00 |
| +1 | 2026-05-21 01:42:00 | 4604.9 | 4604.9 | 4604.9 | 4604.9 | 2 | 0.29x | 0.00 |
| +2 | 2026-05-21 01:44:00 | 4603.0 | 4603.0 | 4603.0 | 4603.0 | 1 | 0.15x | 0.00 |
| +3 | 2026-05-21 01:45:00 | 4602.0 | 4602.0 | 4602.0 | 4602.0 | 1 | 0.16x | 0.00 |
| +4 | 2026-05-21 01:48:00 | 4602.2 | 4602.2 | 4602.2 | 4602.2 | 2 | 0.36x | 0.00 |
| +5 | 2026-05-21 01:50:00 | 4599.8 | 4600.0 | 4599.4 | 4599.4 | 5 | 0.89x | 0.67 |
