# Bai lam #34 — Tích lũy (ACC)

- Anh: `range_34.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-15 12:18:00 -> 2026-06-15 15:40:00** = 202 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4345.3, VSA=1.68x, bien do nen=3.4 gia.
- MOVE truoc climax: dai 20.2 gia, 36 nen, hieu suat huong 0.51.
- Bien CHINH (net lien, climax+AR): 4345.3 - 4370.8 = 25.5 gia (0.59% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4345.3 - 4371.5 = 26.2 gia.
- Ty le bien phu/bien chinh: **1.03x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.20x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 62854..62862 (2026-06-15 13:15:00), effort(VSA TB)=1.27x, result(bien do/ATR)=5.26, ty le er=0.24 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-15 12:18:00 | 2026-06-15 13:06:00 | 49 |
| B | 2026-06-15 13:07:00 | 2026-06-15 13:14:00 | 8 |
| D | 2026-06-15 13:15:00 | 2026-06-15 13:39:00 | 25 |
| E | 2026-06-15 13:40:00 | 2026-06-15 15:40:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-15 12:20:00 | 4345.6 | A | - | 3.20x | 0.24 |
| AR | 2026-06-15 12:57:00 | 4370.8 | A | - | 0.56x | 0.50 |
| ST[A] | 2026-06-15 13:06:00 | 4362.8 | A | - | 0.98x | 0.63 |
| SOS | 2026-06-15 13:15:00 | 4373.8 | D | - | 3.57x | 0.58 |
| LPS[D] | 2026-06-15 13:33:00 | 4378.4 | D | - | 1.67x | 0.57 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-15 12:12:00 | 4358.2 | 4358.2 | 4356.3 | 4357.5 | 83 | 1.41x | 0.37 |
| -5 | 2026-06-15 12:13:00 | 4357.1 | 4357.4 | 4355.4 | 4355.4 | 101 | 1.68x | 0.85 |
| -4 | 2026-06-15 12:14:00 | 4355.4 | 4355.7 | 4351.6 | 4352.2 | 194 | 2.88x | 0.78 |
| -3 | 2026-06-15 12:15:00 | 4352.3 | 4354.2 | 4351.1 | 4351.8 | 156 | 2.23x | 0.16 |
| -2 | 2026-06-15 12:16:00 | 4351.5 | 4351.9 | 4348.7 | 4349.8 | 187 | 2.42x | 0.53 |
| -1 | 2026-06-15 12:17:00 | 4349.6 | 4349.8 | 4345.5 | 4345.5 | 282 | 3.14x | 0.95 |
| +0 **<- climax** | 2026-06-15 12:18:00 | 4345.7 | 4348.7 | 4345.3 | 4348.4 | 162 | 1.68x | 0.79 |
| +1 | 2026-06-15 12:19:00 | 4348.3 | 4348.6 | 4346.8 | 4348.1 | 142 | 1.38x | 0.11 |
| +2 | 2026-06-15 12:20:00 | 4348.0 | 4348.9 | 4345.6 | 4348.8 | 376 | 3.20x | 0.24 |
| +3 | 2026-06-15 12:21:00 | 4349.1 | 4350.7 | 4348.6 | 4349.6 | 129 | 1.07x | 0.24 |
| +4 | 2026-06-15 12:22:00 | 4349.4 | 4351.8 | 4348.9 | 4351.6 | 117 | 0.94x | 0.76 |
| +5 | 2026-06-15 12:23:00 | 4351.6 | 4352.8 | 4351.1 | 4352.1 | 84 | 0.66x | 0.29 |
