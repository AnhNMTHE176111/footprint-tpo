# Bai lam #28 — Tái phân phối (RE-DIST)

- Anh: `range_28.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-05 13:00:00 -> 2026-06-05 14:24:00** = 84 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4425.2, VSA=2.57x, bien do nen=7.7 gia.
- MOVE truoc climax: dai 42.2 gia, 40 nen, hieu suat huong 0.68.
- Bien CHINH (net lien, climax+AR): 4425.2 - 4446.6 = 21.4 gia (0.48% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4423.3 - 4446.6 = 23.3 gia.
- Ty le bien phu/bien chinh: **1.09x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=4.58x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `-1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`none`, n=0 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 54604..54609 (2026-06-05 13:37:00), effort(VSA TB)=1.35x, result(bien do/ATR)=4.30, ty le er=0.31 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-05 13:00:00 | 2026-06-05 13:31:00 | 32 |
| B | 2026-06-05 13:32:00 | 2026-06-05 13:36:00 | 5 |
| D | 2026-06-05 13:37:00 | 2026-06-05 13:55:00 | 19 |
| E | 2026-06-05 13:56:00 | 2026-06-05 14:24:00 | 29 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-05 12:52:00 | 4446.6 | A | - | 4.58x | 0.40 |
| AR (yếu) | 2026-06-05 13:16:00 | 4446.6 | A | - | 0.59x | 0.04 |
| ST[A] | 2026-06-05 13:31:00 | 4423.3 | A | - | 2.34x | 0.76 |
| SOW | 2026-06-05 13:37:00 | 4414.8 | D | - | 2.92x | 0.97 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-05 12:54:00 | 4447.1 | 4448.5 | 4442.9 | 4443.0 | 628 | 1.48x | 0.73 |
| -5 | 2026-06-05 12:55:00 | 4443.1 | 4446.0 | 4438.9 | 4442.3 | 931 | 2.06x | 0.11 |
| -4 | 2026-06-05 12:56:00 | 4442.0 | 4442.0 | 4438.2 | 4439.0 | 457 | 1.05x | 0.79 |
| -3 | 2026-06-05 12:57:00 | 4439.2 | 4439.3 | 4434.2 | 4436.9 | 757 | 1.66x | 0.45 |
| -2 | 2026-06-05 12:58:00 | 4436.9 | 4441.4 | 4435.0 | 4438.5 | 492 | 1.06x | 0.25 |
| -1 | 2026-06-05 12:59:00 | 4438.6 | 4438.6 | 4430.1 | 4432.1 | 840 | 1.71x | 0.76 |
| +0 **<- climax** | 2026-06-05 13:00:00 | 4432.0 | 4432.9 | 4425.2 | 4430.7 | 1421 | 2.57x | 0.17 |
| +1 | 2026-06-05 13:01:00 | 4430.7 | 4442.3 | 4430.0 | 4442.3 | 849 | 1.46x | 0.94 |
| +2 | 2026-06-05 13:02:00 | 4441.8 | 4444.1 | 4438.2 | 4438.8 | 834 | 1.36x | 0.51 |
| +3 | 2026-06-05 13:03:00 | 4438.4 | 4438.4 | 4434.1 | 4436.0 | 505 | 0.80x | 0.56 |
| +4 | 2026-06-05 13:04:00 | 4435.9 | 4437.7 | 4433.7 | 4437.6 | 368 | 0.57x | 0.43 |
| +5 | 2026-06-05 13:05:00 | 4437.9 | 4440.1 | 4437.1 | 4439.9 | 287 | 0.44x | 0.67 |
