# Bai lam #47 — Chưa rõ (SC) (ACC?)

- Anh: `range_47.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-07-07 19:18:00 -> 2026-07-08 03:26:00** = 427 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4102.7, VSA=1.53x, bien do nen=9.7 gia.
- MOVE truoc climax: dai 46.2 gia, 107 nen, hieu suat huong 0.41.
- Bien CHINH (net lien, climax+AR): 4102.7 - 4128.9 = 26.2 gia (0.64% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4102.7 - 4137.1 = 34.4 gia.
- Ty le bien phu/bien chinh: **1.31x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.94x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.23, ty le volume nhip cuoi/dau=0.13 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 84889..84894 (2026-07-07 22:10:00), effort(VSA TB)=1.70x, result(bien do/ATR)=2.27, ty le er=0.75 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-07-07 19:18:00 | 2026-07-07 20:51:00 | 94 |
| B | 2026-07-07 20:52:00 | 2026-07-08 02:31:00 | 280 |
| C | 2026-07-08 02:32:00 | 2026-07-08 03:00:00 | 28 |
| D | 2026-07-08 03:01:00 | 2026-07-08 03:26:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-07-07 19:15:00 | 4107.3 | A | - | 2.94x | 0.82 |
| AR | 2026-07-07 19:55:00 | 4128.9 | A | - | 3.74x | 0.32 |
| ST[A] | 2026-07-07 20:51:00 | 4114.2 | A | - | 1.47x | 0.10 |
| mSOS | 2026-07-08 00:44:00 | 4137.1 | B | - | 0.63x | 0.27 |
| LPS[C] | 2026-07-08 02:32:00 | 4127.0 | C | - | 0.58x | 0.47 |
| SOS | 2026-07-08 03:01:00 | 4139.3 | D | - | 6.30x | 0.85 |
| LPS[D] | 2026-07-08 03:18:00 | 4135.7 | D | - | 0.68x | 0.58 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-07-07 19:12:00 | 4116.1 | 4116.7 | 4113.6 | 4115.3 | 500 | 2.04x | 0.26 |
| -5 | 2026-07-07 19:13:00 | 4115.5 | 4119.9 | 4114.8 | 4117.8 | 263 | 1.07x | 0.45 |
| -4 | 2026-07-07 19:14:00 | 4117.8 | 4118.0 | 4115.6 | 4116.6 | 80 | 0.33x | 0.50 |
| -3 | 2026-07-07 19:15:00 | 4116.1 | 4116.3 | 4107.3 | 4108.7 | 823 | 2.94x | 0.82 |
| -2 | 2026-07-07 19:16:00 | 4108.9 | 4110.8 | 4107.5 | 4109.3 | 366 | 1.24x | 0.12 |
| -1 | 2026-07-07 19:17:00 | 4109.3 | 4114.6 | 4109.2 | 4112.5 | 316 | 1.03x | 0.59 |
| +0 **<- climax** | 2026-07-07 19:18:00 | 4112.2 | 4112.4 | 4102.7 | 4104.2 | 502 | 1.53x | 0.82 |
| +1 | 2026-07-07 19:19:00 | 4104.2 | 4110.2 | 4104.0 | 4109.4 | 179 | 0.54x | 0.84 |
| +2 | 2026-07-07 19:20:00 | 4109.3 | 4110.7 | 4104.2 | 4107.9 | 224 | 0.67x | 0.22 |
| +3 | 2026-07-07 19:21:00 | 4107.4 | 4109.2 | 4105.2 | 4108.0 | 306 | 0.94x | 0.15 |
| +4 | 2026-07-07 19:22:00 | 4108.5 | 4112.0 | 4108.5 | 4110.7 | 176 | 0.54x | 0.63 |
| +5 | 2026-07-07 19:23:00 | 4110.4 | 4112.4 | 4109.9 | 4112.2 | 250 | 0.75x | 0.72 |
