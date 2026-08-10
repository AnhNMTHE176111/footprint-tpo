# Bai lam #46 — Tái tích lũy (RE-ACC)

- Anh: `range_46.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-06 16:58:00 -> 2026-07-06 19:03:00** = 125 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4168.1, VSA=0.82x, bien do nen=1.4 gia.
- Bien CHINH (net lien, climax+AR): 4162.1 - 4168.1 = 6.0 gia (0.14% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4162.1 - 4173.8 = 11.7 gia.
- Ty le bien phu/bien chinh: **1.95x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=1.24x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed** — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.83, ty le volume nhip cuoi/dau=0.15 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 83305..83307 (2026-07-06 17:29:00), effort(VSA TB)=3.10x, result(bien do/ATR)=2.44, ty le er=1.27 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-06 16:58:00 | 2026-07-06 17:26:00 | 29 |
| B | 2026-07-06 17:27:00 | 2026-07-06 18:09:00 | 43 |
| C | 2026-07-06 18:10:00 | 2026-07-06 18:15:00 | 6 |
| D | 2026-07-06 18:16:00 | 2026-07-06 18:40:00 | 25 |
| E | 2026-07-06 18:41:00 | 2026-07-06 19:03:00 | 23 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX? | 2026-07-06 17:06:00 | 4168.1 | A | - | 1.24x | 0.35 |
| AR | 2026-07-06 17:21:00 | 4162.1 | A | - | 1.20x | 0.14 |
| ST[A] | 2026-07-06 17:26:00 | 4171.6 | A | - | 1.67x | 0.54 |
| mSOS | 2026-07-06 18:00:00 | 4173.8 | B | - | 2.55x | 0.77 |
| LPS[C] | 2026-07-06 18:10:00 | 4167.1 | C | - | 0.57x | 0.30 |
| SOS | 2026-07-06 18:16:00 | 4173.4 | D | - | 0.96x | 0.92 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-06 16:52:00 | 4165.0 | 4165.6 | 4164.9 | 4165.4 | 43 | 1.22x | 0.57 |
| -5 | 2026-07-06 16:53:00 | 4165.4 | 4166.8 | 4165.3 | 4165.8 | 42 | 1.19x | 0.27 |
| -4 | 2026-07-06 16:54:00 | 4166.1 | 4167.5 | 4166.1 | 4166.1 | 64 | 1.69x | 0.00 |
| -3 | 2026-07-06 16:55:00 | 4166.2 | 4166.2 | 4165.0 | 4165.7 | 33 | 0.85x | 0.42 |
| -2 | 2026-07-06 16:56:00 | 4165.3 | 4165.6 | 4164.6 | 4165.1 | 24 | 0.64x | 0.20 |
| -1 | 2026-07-06 16:57:00 | 4165.3 | 4167.7 | 4165.3 | 4167.5 | 55 | 1.42x | 0.92 |
| +0 **<- climax** | 2026-07-06 16:58:00 | 4167.4 | 4168.1 | 4166.7 | 4166.7 | 32 | 0.82x | 0.50 |
| +1 | 2026-07-06 16:59:00 | 4166.9 | 4167.7 | 4166.4 | 4166.9 | 73 | 1.80x | 0.00 |
| +2 | 2026-07-06 17:00:00 | 4166.9 | 4167.4 | 4166.0 | 4167.0 | 65 | 1.55x | 0.07 |
| +3 | 2026-07-06 17:01:00 | 4167.1 | 4167.1 | 4164.1 | 4164.4 | 90 | 1.98x | 0.90 |
| +4 | 2026-07-06 17:02:00 | 4165.0 | 4165.5 | 4164.2 | 4164.2 | 66 | 1.39x | 0.62 |
| +5 | 2026-07-06 17:03:00 | 4164.1 | 4165.4 | 4164.1 | 4165.1 | 38 | 0.78x | 0.77 |
