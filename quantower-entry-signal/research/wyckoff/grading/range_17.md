# Bai lam #17 — Chưa rõ (SC) (ACC?)

- Anh: `range_17.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-12 13:16:00 -> 2026-05-12 17:24:00** = 226 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4722.5, VSA=6.34x, bien do nen=5.2 gia.
- MOVE truoc climax: dai 23.6 gia, 23 nen, hieu suat huong 0.57.
- Bien CHINH (net lien, climax+AR): 4722.5 - 4744.4 = 21.9 gia (0.46% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4714.5 - 4744.4 = 29.9 gia.
- Ty le bien phu/bien chinh: **1.37x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=6.34x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh).

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.46, ty le volume nhip cuoi/dau=0.31 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.07, ty le volume nhip cuoi/dau=0.25 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 33639..33644 (2026-05-12 15:56:00), effort(VSA TB)=2.48x, result(bien do/ATR)=5.45, ty le er=0.45 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-12 13:16:00 | 2026-05-12 14:00:00 | 45 |
| B | 2026-05-12 14:01:00 | 2026-05-12 16:58:00 | 156 |
| D | 2026-05-12 16:59:00 | 2026-05-12 17:24:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-12 13:16:00 | 4722.5 | A | - | 6.34x | 0.75 |
| AR | 2026-05-12 13:43:00 | 4744.4 | A | - | 0.88x | 0.62 |
| ST[A] | 2026-05-12 14:00:00 | 4719.1 | A | - | 4.71x | 0.36 |
| ST[B] | 2026-05-12 14:31:00 | 4721.2 | B | - | 0.55x | 0.58 |
| mSOW | 2026-05-12 15:10:00 | 4712.6 | B | - | 10.51x | 0.52 |
| SOW | 2026-05-12 16:59:00 | 4714.3 | D | - | 0.39x | 1.00 |
| LPSY[D] | 2026-05-12 17:06:00 | 4722.2 | D | - | 2.18x | 0.63 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-12 13:10:00 | 4736.7 | 4736.7 | 4736.3 | 4736.3 | 2 | 0.48x | 1.00 |
| -5 | 2026-05-12 13:11:00 | 4736.3 | 4738.1 | 4735.0 | 4738.1 | 9 | 1.98x | 0.58 |
| -4 | 2026-05-12 13:12:00 | 4737.3 | 4737.4 | 4736.3 | 4736.4 | 7 | 1.56x | 0.82 |
| -3 | 2026-05-12 13:13:00 | 4734.9 | 4734.9 | 4734.6 | 4734.6 | 3 | 0.71x | 1.00 |
| -2 | 2026-05-12 13:14:00 | 4732.0 | 4732.8 | 4731.1 | 4732.6 | 37 | 6.27x | 0.35 |
| -1 | 2026-05-12 13:15:00 | 4731.7 | 4731.7 | 4726.5 | 4728.8 | 17 | 2.60x | 0.56 |
| +0 **<- climax** | 2026-05-12 13:16:00 | 4727.2 | 4727.7 | 4722.5 | 4723.3 | 59 | 6.34x | 0.75 |
| +1 | 2026-05-12 13:17:00 | 4724.5 | 4725.8 | 4722.7 | 4725.4 | 12 | 1.25x | 0.29 |
| +2 | 2026-05-12 13:18:00 | 4724.1 | 4729.1 | 4724.1 | 4729.1 | 5 | 0.52x | 1.00 |
| +3 | 2026-05-12 13:19:00 | 4730.4 | 4730.4 | 4729.3 | 4729.4 | 5 | 0.51x | 0.91 |
| +4 | 2026-05-12 13:20:00 | 4730.7 | 4732.2 | 4729.6 | 4729.7 | 6 | 0.60x | 0.38 |
| +5 | 2026-05-12 13:21:00 | 4733.0 | 4733.0 | 4733.0 | 4733.0 | 1 | 0.10x | 0.00 |
