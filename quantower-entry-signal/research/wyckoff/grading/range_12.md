# Bai lam #12 — Tái phân phối (RE-DIST)

- Anh: `range_12.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-04-28 02:02:00 -> 2026-04-28 05:36:00** = 78 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4715.0, VSA=0.92x, bien do nen=2.8 gia.
- MOVE truoc climax: dai 33.1 gia, 58 nen, hieu suat huong 0.43.
- Bien CHINH (net lien, climax+AR): 4715.0 - 4728.5 = 13.5 gia (0.29% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4715.0 - 4728.5 = 13.5 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=5.07x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.52, ty le volume nhip cuoi/dau=1.02 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 25784..25792 (2026-04-28 05:06:00), effort(VSA TB)=2.60x, result(bien do/ATR)=66.87, ty le er=0.04 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-04-28 02:02:00 | 2026-04-28 02:59:00 | 25 |
| B | 2026-04-28 03:00:00 | 2026-04-28 03:25:00 | 10 |
| C | 2026-04-28 03:28:00 | 2026-04-28 05:04:00 | 24 |
| D | 2026-04-28 05:06:00 | 2026-04-28 05:17:00 | 9 |
| E | 2026-04-28 05:18:00 | 2026-04-28 05:36:00 | 11 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-04-28 02:00:00 | 4715.8 | A | - | 5.07x | 0.46 |
| AR | 2026-04-28 02:16:00 | 4728.5 | A | - | 0.25x | 0.00 |
| ST[A] | 2026-04-28 02:59:00 | 4717.4 | A | - | 0.59x | 0.00 |
| LPSY[C] | 2026-04-28 03:28:00 | 4724.9 | C | - | 0.62x | 0.00 |
| SOW | 2026-04-28 05:06:00 | 4701.4 | D | - | 12.38x | 0.63 |
| LPSY[D] | 2026-04-28 05:10:00 | 4703.4 | D | - | 0.47x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-04-28 01:56:00 | 4727.8 | 4727.8 | 4727.7 | 4727.7 | 3 | 1.28x | 1.00 |
| -5 | 2026-04-28 01:57:00 | 4725.7 | 4725.7 | 4722.7 | 4722.7 | 7 | 2.64x | 1.00 |
| -4 | 2026-04-28 01:58:00 | 4721.3 | 4721.6 | 4718.4 | 4719.4 | 5 | 1.75x | 0.59 |
| -3 | 2026-04-28 01:59:00 | 4721.1 | 4721.1 | 4719.6 | 4719.6 | 2 | 0.70x | 1.00 |
| -2 | 2026-04-28 02:00:00 | 4718.4 | 4718.4 | 4715.8 | 4717.2 | 19 | 5.07x | 0.46 |
| -1 | 2026-04-28 02:01:00 | 4715.1 | 4715.1 | 4715.1 | 4715.1 | 1 | 0.28x | 0.00 |
| +0 **<- climax** | 2026-04-28 02:02:00 | 4715.0 | 4717.8 | 4715.0 | 4717.8 | 3 | 0.92x | 1.00 |
| +1 | 2026-04-28 02:03:00 | 4718.8 | 4721.2 | 4718.8 | 4721.0 | 11 | 2.93x | 0.92 |
| +2 | 2026-04-28 02:04:00 | 4721.6 | 4722.3 | 4721.6 | 4722.3 | 3 | 0.78x | 1.00 |
| +3 | 2026-04-28 02:05:00 | 4722.8 | 4724.8 | 4722.8 | 4724.8 | 4 | 1.00x | 1.00 |
| +4 | 2026-04-28 02:07:00 | 4724.4 | 4724.4 | 4724.3 | 4724.3 | 3 | 0.74x | 1.00 |
| +5 | 2026-04-28 02:09:00 | 4724.2 | 4724.2 | 4724.2 | 4724.2 | 2 | 0.50x | 0.00 |
