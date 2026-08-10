# Bai lam #18 — Chưa rõ (SC) (ACC?)

- Anh: `range_18.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-12 16:59:00 -> 2026-05-14 19:56:00** = 1648 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4714.3, VSA=0.39x, bien do nen=0.4 gia.
- Bien CHINH (net lien, climax+AR): 4714.3 - 4769.4 = 55.1 gia (1.17% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4706.8 - 4769.4 = 62.6 gia.
- Ty le bien phu/bien chinh: **1.14x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.18x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **superseded** (bi thay the boi mot range moi sinh tu cu pha, khong dat ten 4 mau hinh) — **SINH TU CHINH MOT CU PHA**, khong co cao trao thuc su..

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`SOT`, n=4 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.46, ty le volume nhip cuoi/dau=0.68 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.37, ty le volume nhip cuoi/dau=1.14 (HAP THU (volume >= nhip dau, canh giu vung)).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 34275..34279 (2026-05-13 13:43:00), effort(VSA TB)=2.58x, result(bien do/ATR)=5.60, ty le er=0.46 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-12 16:59:00 | 2026-05-13 03:02:00 | 253 |
| B | 2026-05-13 03:09:00 | 2026-05-14 17:49:00 | 1312 |
| C | 2026-05-14 17:50:00 | 2026-05-14 19:27:00 | 58 |
| D | 2026-05-14 19:29:00 | 2026-05-14 19:56:00 | 26 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC? | 2026-05-12 17:06:00 | 4720.3 | A | - | 2.18x | 0.63 |
| AR | 2026-05-13 00:23:00 | 4769.4 | A | - | 2.04x | 1.00 |
| ST[A] | 2026-05-13 03:02:00 | 4732.6 | A | - | 1.11x | 1.00 |
| mSOW | 2026-05-14 06:22:00 | 4730.5 | B | - | 8.91x | 0.10 |
| mSOW | 2026-05-14 14:51:00 | 4728.6 | B | - | 10.59x | 0.95 |
| LPSY[C] | 2026-05-14 17:50:00 | 4721.9 | C | - | 1.13x | 1.00 |
| mSOW | 2026-05-14 18:04:00 | 4709.9 | B | - | 2.77x | 0.00 |
| SOW | 2026-05-14 19:29:00 | 4703.9 | D | - | 4.00x | 0.62 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-12 16:50:00 | 4711.9 | 4711.9 | 4711.8 | 4711.8 | 2 | 0.40x | 1.00 |
| -5 | 2026-05-12 16:51:00 | 4714.6 | 4714.6 | 4714.6 | 4714.6 | 1 | 0.20x | 0.00 |
| -4 | 2026-05-12 16:53:00 | 4712.1 | 4712.1 | 4711.9 | 4711.9 | 5 | 0.98x | 1.00 |
| -3 | 2026-05-12 16:54:00 | 4711.1 | 4712.0 | 4710.8 | 4711.9 | 12 | 2.14x | 0.67 |
| -2 | 2026-05-12 16:55:00 | 4714.4 | 4714.4 | 4714.4 | 4714.4 | 1 | 0.18x | 0.00 |
| -1 | 2026-05-12 16:58:00 | 4715.8 | 4715.8 | 4715.8 | 4715.8 | 1 | 0.19x | 0.00 |
| +0 **<- climax** | 2026-05-12 16:59:00 | 4714.7 | 4714.7 | 4714.3 | 4714.3 | 2 | 0.39x | 1.00 |
| +1 | 2026-05-12 17:00:00 | 4714.9 | 4714.9 | 4714.9 | 4714.9 | 1 | 0.20x | 0.00 |
| +2 | 2026-05-12 17:01:00 | 4715.6 | 4715.8 | 4715.0 | 4715.8 | 4 | 0.82x | 0.25 |
| +3 | 2026-05-12 17:02:00 | 4716.7 | 4719.0 | 4716.7 | 4719.0 | 6 | 1.18x | 1.00 |
| +4 | 2026-05-12 17:03:00 | 4718.7 | 4719.6 | 4718.7 | 4719.4 | 3 | 0.58x | 0.78 |
| +5 | 2026-05-12 17:04:00 | 4719.7 | 4719.7 | 4718.8 | 4718.8 | 2 | 0.39x | 1.00 |
