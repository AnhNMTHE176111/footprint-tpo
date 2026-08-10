# Bai lam #29 — Chưa rõ (SC) (ACC?)

- Anh: `range_29.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-04 14:53:00 -> 2026-06-05 02:56:00** = 663 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4483.8, VSA=2.31x, bien do nen=8.7 gia.
- MOVE truoc climax: dai 50.6 gia, 68 nen, hieu suat huong 0.46.
- Bien CHINH (net lien, climax+AR): 4483.8 - 4513.2 = 29.4 gia (0.66% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4477.5 - 4513.2 = 35.7 gia.
- Ty le bien phu/bien chinh: **1.21x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=3.32x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.20, ty le volume nhip cuoi/dau=1.08 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.45, ty le volume nhip cuoi/dau=0.45 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 53763..53783 (2026-06-04 23:51:00), effort(VSA TB)=0.88x, result(bien do/ATR)=1.23, ty le er=0.71 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-04 14:53:00 | 2026-06-04 23:02:00 | 430 |
| B | 2026-06-04 23:03:00 | 2026-06-05 01:30:00 | 148 |
| C | 2026-06-05 01:31:00 | 2026-06-05 02:30:00 | 60 |
| D | 2026-06-05 02:31:00 | 2026-06-05 02:56:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-04 14:51:00 | 4487.0 | A | - | 3.32x | 0.38 |
| AR | 2026-06-04 16:19:00 | 4513.2 | A | - | 1.92x | 0.30 |
| ST[A] | 2026-06-04 23:02:00 | 4491.2 | A | - | 3.78x | 0.90 |
| mSOW | 2026-06-05 01:00:00 | 4479.5 | B | - | 6.50x | 0.21 |
| LPSY[C] | 2026-06-05 01:31:00 | 4486.2 | C | - | 1.09x | 0.26 |
| SOW | 2026-06-05 02:31:00 | 4470.7 | D | - | 5.11x | 0.04 |
| LPSY[D] | 2026-06-05 02:50:00 | 4476.1 | D | - | 1.17x | 0.72 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-04 14:47:00 | 4499.8 | 4501.4 | 4497.8 | 4498.1 | 185 | 0.85x | 0.47 |
| -5 | 2026-06-04 14:48:00 | 4498.2 | 4499.2 | 4493.4 | 4493.5 | 502 | 2.10x | 0.81 |
| -4 | 2026-06-04 14:49:00 | 4493.7 | 4495.0 | 4492.6 | 4494.0 | 280 | 1.14x | 0.13 |
| -3 | 2026-06-04 14:50:00 | 4494.4 | 4498.3 | 4493.8 | 4496.1 | 373 | 1.50x | 0.38 |
| -2 | 2026-06-04 14:51:00 | 4496.0 | 4496.0 | 4487.0 | 4492.6 | 955 | 3.32x | 0.38 |
| -1 | 2026-06-04 14:52:00 | 4492.4 | 4493.0 | 4490.5 | 4491.6 | 572 | 1.83x | 0.32 |
| +0 **<- climax** | 2026-06-04 14:53:00 | 4491.9 | 4492.5 | 4483.8 | 4485.6 | 800 | 2.31x | 0.72 |
| +1 | 2026-06-04 14:54:00 | 4485.7 | 4491.5 | 4484.7 | 4491.0 | 431 | 1.18x | 0.78 |
| +2 | 2026-06-04 14:55:00 | 4490.8 | 4493.6 | 4490.4 | 4492.7 | 321 | 0.86x | 0.59 |
| +3 | 2026-06-04 14:56:00 | 4492.7 | 4493.3 | 4489.8 | 4490.4 | 242 | 0.64x | 0.66 |
| +4 | 2026-06-04 14:57:00 | 4490.3 | 4492.9 | 4487.1 | 4491.3 | 381 | 0.97x | 0.17 |
| +5 | 2026-06-04 14:58:00 | 4491.5 | 4491.9 | 4489.7 | 4491.9 | 186 | 0.48x | 0.18 |
