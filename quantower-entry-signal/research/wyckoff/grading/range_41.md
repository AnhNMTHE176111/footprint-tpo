# Bai lam #41 — Chưa rõ (SC) (ACC?)

- Anh: `range_41.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-06 12:43:00 -> 2026-07-06 17:15:00** = 272 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4143.3, VSA=1.28x, bien do nen=1.9 gia.
- MOVE truoc climax: dai 21.8 gia, 76 nen, hieu suat huong 0.36.
- Bien CHINH (net lien, climax+AR): 4143.3 - 4160.7 = 17.4 gia (0.42% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4140.6 - 4164.0 = 23.4 gia.
- Ty le bien phu/bien chinh: **1.34x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.27x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.70, ty le volume nhip cuoi/dau=1.17 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.37, ty le volume nhip cuoi/dau=0.88 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 83084..83100 (2026-07-06 14:02:00), effort(VSA TB)=1.40x, result(bien do/ATR)=1.68, ty le er=0.83 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-06 12:43:00 | 2026-07-06 13:15:00 | 33 |
| B | 2026-07-06 13:16:00 | 2026-07-06 16:13:00 | 178 |
| C | 2026-07-06 16:14:00 | 2026-07-06 16:49:00 | 36 |
| D | 2026-07-06 16:50:00 | 2026-07-06 17:15:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-06 12:41:00 | 4145.8 | A | - | 3.27x | 0.82 |
| AR | 2026-07-06 13:08:00 | 4160.7 | A | - | 0.71x | 0.31 |
| ST[A] | 2026-07-06 13:15:00 | 4150.7 | A | - | 1.46x | 0.39 |
| mSOS | 2026-07-06 13:34:00 | 4162.6 | B | - | 2.45x | 0.67 |
| mSOW | 2026-07-06 14:44:00 | 4140.6 | B | - | 5.13x | 0.58 |
| LPS[C] | 2026-07-06 16:14:00 | 4152.0 | C | - | 0.97x | 0.92 |
| SOS | 2026-07-06 16:50:00 | 4165.0 | D | - | 3.42x | 0.85 |
| LPS[D] | 2026-07-06 17:01:00 | 4164.1 | D | - | 1.98x | 0.90 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-06 12:37:00 | 4152.6 | 4153.5 | 4152.0 | 4153.5 | 62 | 0.57x | 0.60 |
| -5 | 2026-07-06 12:38:00 | 4153.2 | 4153.2 | 4152.0 | 4152.5 | 94 | 0.83x | 0.58 |
| -4 | 2026-07-06 12:39:00 | 4152.2 | 4152.3 | 4150.4 | 4151.6 | 235 | 1.90x | 0.32 |
| -3 | 2026-07-06 12:40:00 | 4151.2 | 4151.9 | 4150.4 | 4151.6 | 107 | 0.89x | 0.27 |
| -2 | 2026-07-06 12:41:00 | 4151.4 | 4151.4 | 4145.8 | 4146.8 | 418 | 3.27x | 0.82 |
| -1 | 2026-07-06 12:42:00 | 4146.6 | 4146.7 | 4144.1 | 4145.2 | 256 | 1.93x | 0.54 |
| +0 **<- climax** | 2026-07-06 12:43:00 | 4144.9 | 4145.2 | 4143.3 | 4145.2 | 173 | 1.28x | 0.16 |
| +1 | 2026-07-06 12:44:00 | 4145.0 | 4145.9 | 4144.6 | 4144.9 | 105 | 0.76x | 0.08 |
| +2 | 2026-07-06 12:45:00 | 4145.1 | 4149.4 | 4144.9 | 4149.0 | 244 | 1.70x | 0.87 |
| +3 | 2026-07-06 12:46:00 | 4148.8 | 4152.6 | 4148.4 | 4150.6 | 291 | 1.91x | 0.43 |
| +4 | 2026-07-06 12:47:00 | 4150.5 | 4150.9 | 4149.4 | 4149.5 | 66 | 0.44x | 0.67 |
| +5 | 2026-07-06 12:48:00 | 4149.6 | 4149.6 | 4147.5 | 4147.9 | 86 | 0.57x | 0.81 |
