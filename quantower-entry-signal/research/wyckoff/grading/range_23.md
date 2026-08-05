# Bai lam #23 — Tái phân phối (RE-DIST)

- Anh: `range_23.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-27 05:33:00 -> 2026-05-27 07:50:00** = 137 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4525.6, VSA=4.84x, bien do nen=5.5 gia.
- MOVE truoc climax: dai 19.4 gia, 44 nen, hieu suat huong 0.49.
- Bien CHINH (net lien, climax+AR): 4525.6 - 4532.9 = 7.3 gia (0.16% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4523.2 - 4533.9 = 10.7 gia.
- Ty le bien phu/bien chinh: **1.47x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.84x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.51, ty le volume nhip cuoi/dau=0.92 (can kiet).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 44503..44509 (2026-05-27 06:08:00), effort(VSA TB)=0.81x, result(bien do/ATR)=2.16, ty le er=0.38 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-27 05:33:00 | 2026-05-27 05:44:00 | 12 |
| B | 2026-05-27 05:45:00 | 2026-05-27 06:07:00 | 23 |
| C | 2026-05-27 06:08:00 | 2026-05-27 06:17:00 | 10 |
| D | 2026-05-27 06:18:00 | 2026-05-27 06:25:00 | 8 |
| E | 2026-05-27 06:26:00 | 2026-05-27 07:50:00 | 85 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-27 05:33:00 | 4525.6 | A | - | 4.84x | 0.38 |
| AR | 2026-05-27 05:37:00 | 4532.9 | A | - | 1.36x | 0.25 |
| ST[A] | 2026-05-27 05:44:00 | 4523.2 | A | - | 1.01x | 0.23 |
| LPSY[C] | 2026-05-27 06:08:00 | 4530.8 | C | - | 1.36x | 0.69 |
| SOW | 2026-05-27 06:18:00 | 4520.2 | D | - | 4.23x | 0.74 |
| LPSY[D] | 2026-05-27 06:21:00 | 4521.7 | D | - | 3.13x | 0.82 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-27 05:27:00 | 4538.7 | 4539.4 | 4538.7 | 4539.4 | 6 | 0.20x | 1.00 |
| -5 | 2026-05-27 05:28:00 | 4539.1 | 4539.1 | 4539.1 | 4539.1 | 1 | 0.04x | 0.00 |
| -4 | 2026-05-27 05:29:00 | 4539.4 | 4540.1 | 4539.2 | 4539.4 | 16 | 0.57x | 0.00 |
| -3 | 2026-05-27 05:30:00 | 4539.3 | 4540.9 | 4539.0 | 4539.3 | 49 | 1.61x | 0.00 |
| -2 | 2026-05-27 05:31:00 | 4539.6 | 4540.4 | 4535.5 | 4535.5 | 76 | 2.24x | 0.84 |
| -1 | 2026-05-27 05:32:00 | 4535.6 | 4535.6 | 4529.8 | 4531.1 | 191 | 4.42x | 0.78 |
| +0 **<- climax** | 2026-05-27 05:33:00 | 4531.1 | 4531.1 | 4525.6 | 4529.0 | 268 | 4.84x | 0.38 |
| +1 | 2026-05-27 05:34:00 | 4528.5 | 4529.6 | 4526.0 | 4528.8 | 109 | 1.84x | 0.08 |
| +2 | 2026-05-27 05:35:00 | 4528.8 | 4529.1 | 4526.5 | 4527.7 | 87 | 1.45x | 0.42 |
| +3 | 2026-05-27 05:36:00 | 4527.8 | 4530.7 | 4527.2 | 4530.7 | 84 | 1.35x | 0.83 |
| +4 | 2026-05-27 05:37:00 | 4530.6 | 4532.9 | 4530.1 | 4531.3 | 89 | 1.36x | 0.25 |
| +5 | 2026-05-27 05:38:00 | 4531.5 | 4532.2 | 4531.0 | 4531.9 | 42 | 0.64x | 0.33 |
