# Bai lam #29 — Tái phân phối (RE-DIST)

- Anh: `range_29.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-08 01:30:00 -> 2026-06-08 05:59:00** = 269 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4323.6, VSA=3.55x, bien do nen=14.9 gia.
- MOVE truoc climax: dai 43.3 gia, 62 nen, hieu suat huong 0.35.
- Bien CHINH (net lien, climax+AR): 4323.6 - 4354.8 = 31.2 gia (0.72% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4323.6 - 4354.8 = 31.2 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.55x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.38, ty le volume nhip cuoi/dau=0.77 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 55406..55419 (2026-06-08 04:07:00), effort(VSA TB)=1.17x, result(bien do/ATR)=1.85, ty le er=0.63 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-08 01:30:00 | 2026-06-08 02:20:00 | 51 |
| B | 2026-06-08 02:21:00 | 2026-06-08 05:03:00 | 163 |
| C | 2026-06-08 05:04:00 | 2026-06-08 05:33:00 | 30 |
| D | 2026-06-08 05:34:00 | 2026-06-08 05:58:00 | 25 |
| E | 2026-06-08 05:59:00 | 2026-06-08 05:59:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-08 01:30:00 | 4323.6 | A | - | 3.55x | 0.85 |
| AR | 2026-06-08 02:00:00 | 4354.8 | A | - | 2.61x | 0.61 |
| ST[A] | 2026-06-08 02:20:00 | 4335.0 | A | - | 0.95x | 0.48 |
| LPSY[C] | 2026-06-08 05:04:00 | 4340.1 | C | - | 0.90x | 0.41 |
| SOW | 2026-06-08 05:34:00 | 4311.2 | D | - | 7.36x | 0.93 |
| LPSY[D] | 2026-06-08 05:40:00 | 4317.6 | D | - | 0.79x | 0.19 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-08 01:24:00 | 4349.0 | 4349.0 | 4344.5 | 4345.5 | 90 | 0.61x | 0.78 |
| -5 | 2026-06-08 01:25:00 | 4345.4 | 4346.5 | 4340.8 | 4341.1 | 170 | 1.16x | 0.75 |
| -4 | 2026-06-08 01:26:00 | 4341.2 | 4343.2 | 4340.7 | 4342.3 | 64 | 0.44x | 0.44 |
| -3 | 2026-06-08 01:27:00 | 4342.5 | 4346.7 | 4342.5 | 4343.3 | 69 | 0.50x | 0.19 |
| -2 | 2026-06-08 01:28:00 | 4343.3 | 4343.6 | 4334.9 | 4338.8 | 159 | 1.14x | 0.52 |
| -1 | 2026-06-08 01:29:00 | 4339.1 | 4339.1 | 4337.0 | 4338.3 | 143 | 1.01x | 0.38 |
| +0 **<- climax** | 2026-06-08 01:30:00 | 4338.5 | 4338.5 | 4323.6 | 4325.8 | 584 | 3.55x | 0.85 |
| +1 | 2026-06-08 01:31:00 | 4326.2 | 4341.0 | 4324.5 | 4335.0 | 429 | 2.33x | 0.53 |
| +2 | 2026-06-08 01:32:00 | 4335.1 | 4340.7 | 4334.7 | 4340.5 | 174 | 0.93x | 0.90 |
| +3 | 2026-06-08 01:33:00 | 4339.8 | 4341.4 | 4333.7 | 4335.2 | 153 | 0.80x | 0.60 |
| +4 | 2026-06-08 01:34:00 | 4335.0 | 4340.3 | 4334.4 | 4339.4 | 109 | 0.59x | 0.75 |
| +5 | 2026-06-08 01:35:00 | 4338.4 | 4340.1 | 4335.5 | 4336.9 | 104 | 0.58x | 0.33 |
