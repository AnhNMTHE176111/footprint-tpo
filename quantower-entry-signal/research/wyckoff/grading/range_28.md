# Bai lam #28 — Tái phân phối (RE-DIST)

- Anh: `range_28.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-03 05:31:00 -> 2026-06-03 09:13:00** = 222 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4486.9, VSA=2.09x, bien do nen=3.2 gia.
- MOVE truoc climax: dai 22.2 gia, 76 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4486.9 - 4496.8 = 9.9 gia (0.22% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4478.8 - 4500.5 = 21.7 gia.
- Ty le bien phu/bien chinh: **2.19x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=11.08x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.45, ty le volume nhip cuoi/dau=0.61 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 51473..51488 (2026-06-03 07:35:00), effort(VSA TB)=0.91x, result(bien do/ATR)=0.73, ty le er=1.24 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-03 05:31:00 | 2026-06-03 05:45:00 | 15 |
| B | 2026-06-03 05:46:00 | 2026-06-03 08:41:00 | 176 |
| C | 2026-06-03 08:42:00 | 2026-06-03 08:50:00 | 9 |
| D | 2026-06-03 08:51:00 | 2026-06-03 09:12:00 | 22 |
| E | 2026-06-03 09:13:00 | 2026-06-03 09:13:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-03 05:30:00 | 4488.6 | A | - | 11.08x | 0.78 |
| AR | 2026-06-03 05:37:00 | 4496.8 | A | - | 0.63x | 1.00 |
| ST[A] | 2026-06-03 05:45:00 | 4489.3 | A | - | 0.51x | 0.41 |
| mSOW | 2026-06-03 08:24:00 | 4478.8 | B | - | 2.06x | 0.29 |
| LPSY[C] | 2026-06-03 08:42:00 | 4487.2 | C | - | 1.33x | 0.23 |
| SOW | 2026-06-03 08:51:00 | 4472.0 | D | - | 9.63x | 0.80 |
| LPSY[D] | 2026-06-03 09:08:00 | 4487.5 | D | - | 0.51x | 0.43 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-03 05:25:00 | 4496.5 | 4497.5 | 4496.5 | 4497.4 | 19 | 0.67x | 0.90 |
| -5 | 2026-06-03 05:26:00 | 4497.3 | 4497.6 | 4496.5 | 4496.7 | 20 | 0.72x | 0.55 |
| -4 | 2026-06-03 05:27:00 | 4496.5 | 4496.5 | 4493.9 | 4495.3 | 103 | 3.29x | 0.46 |
| -3 | 2026-06-03 05:28:00 | 4494.9 | 4496.1 | 4494.9 | 4495.5 | 37 | 1.18x | 0.50 |
| -2 | 2026-06-03 05:29:00 | 4495.5 | 4496.8 | 4495.5 | 4496.8 | 24 | 0.80x | 1.00 |
| -1 | 2026-06-03 05:30:00 | 4496.6 | 4496.8 | 4488.6 | 4490.2 | 715 | 11.08x | 0.78 |
| +0 **<- climax** | 2026-06-03 05:31:00 | 4489.8 | 4490.1 | 4486.9 | 4487.8 | 147 | 2.09x | 0.62 |
| +1 | 2026-06-03 05:32:00 | 4488.2 | 4489.9 | 4487.7 | 4489.6 | 85 | 1.14x | 0.64 |
| +2 | 2026-06-03 05:33:00 | 4490.0 | 4492.5 | 4489.7 | 4492.3 | 88 | 1.16x | 0.82 |
| +3 | 2026-06-03 05:34:00 | 4492.7 | 4493.2 | 4492.0 | 4493.0 | 38 | 0.49x | 0.25 |
| +4 | 2026-06-03 05:35:00 | 4492.8 | 4493.8 | 4492.3 | 4493.2 | 21 | 0.27x | 0.27 |
| +5 | 2026-06-03 05:36:00 | 4493.3 | 4495.3 | 4493.3 | 4494.5 | 58 | 0.74x | 0.60 |
