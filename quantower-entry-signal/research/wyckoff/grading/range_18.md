# Bai lam #18 — Tích lũy (ACC)

- Anh: `range_18.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-20 01:36:00 -> 2026-05-20 16:46:00** = 724 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4491.0, VSA=6.97x, bien do nen=14.1 gia.
- MOVE truoc climax: dai 34.6 gia, 39 nen, hieu suat huong 0.41.
- Bien CHINH (net lien, climax+AR): 4491.0 - 4523.2 = 32.2 gia (0.72% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4488.0 - 4542.2 = 54.2 gia.
- Ty le bien phu/bien chinh: **1.68x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=6.97x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.35, ty le volume nhip cuoi/dau=0.49 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 38906..38911 (2026-05-20 12:09:00), effort(VSA TB)=2.48x, result(bien do/ATR)=3.62, ty le er=0.68 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-20 01:36:00 | 2026-05-20 02:37:00 | 43 |
| B | 2026-05-20 02:38:00 | 2026-05-20 14:12:00 | 528 |
| C | 2026-05-20 14:13:00 | 2026-05-20 14:20:00 | 8 |
| D | 2026-05-20 14:21:00 | 2026-05-20 14:45:00 | 25 |
| E | 2026-05-20 14:46:00 | 2026-05-20 16:46:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-20 01:36:00 | 4491.0 | A | - | 6.97x | 0.59 |
| AR | 2026-05-20 01:50:00 | 4523.2 | A | - | 5.57x | 0.58 |
| ST[A] | 2026-05-20 02:37:00 | 4501.2 | A | - | 0.88x | 0.71 |
| mSOW | 2026-05-20 04:20:00 | 4500.0 | B | - | 6.15x | 0.00 |
| mSOS | 2026-05-20 13:14:00 | 4542.2 | B | - | 0.04x | 0.00 |
| LPS[C] | 2026-05-20 14:13:00 | 4503.0 | C | - | 3.18x | 0.66 |
| SOS | 2026-05-20 14:21:00 | 4540.5 | D | - | 3.94x | 0.37 |
| LPS[D] | 2026-05-20 14:24:00 | 4532.0 | D | - | 0.58x | 0.41 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-20 01:30:00 | 4509.1 | 4509.1 | 4504.1 | 4506.8 | 25 | 4.42x | 0.46 |
| -5 | 2026-05-20 01:31:00 | 4507.8 | 4510.5 | 4507.8 | 4508.5 | 5 | 0.96x | 0.26 |
| -4 | 2026-05-20 01:32:00 | 4505.1 | 4508.7 | 4505.1 | 4508.7 | 3 | 0.57x | 1.00 |
| -3 | 2026-05-20 01:33:00 | 4511.3 | 4511.3 | 4511.3 | 4511.3 | 1 | 0.19x | 0.00 |
| -2 | 2026-05-20 01:34:00 | 4512.2 | 4512.2 | 4509.8 | 4509.8 | 4 | 0.75x | 1.00 |
| -1 | 2026-05-20 01:35:00 | 4506.8 | 4506.8 | 4503.5 | 4504.3 | 7 | 1.36x | 0.76 |
| +0 **<- climax** | 2026-05-20 01:36:00 | 4505.1 | 4505.1 | 4491.0 | 4496.8 | 54 | 6.97x | 0.59 |
| +1 | 2026-05-20 01:37:00 | 4497.2 | 4499.9 | 4496.6 | 4499.9 | 6 | 0.75x | 0.82 |
| +2 | 2026-05-20 01:38:00 | 4498.0 | 4500.6 | 4498.0 | 4500.6 | 3 | 0.37x | 1.00 |
| +3 | 2026-05-20 01:39:00 | 4502.1 | 4502.1 | 4502.1 | 4502.1 | 2 | 0.25x | 0.00 |
| +4 | 2026-05-20 01:40:00 | 4500.8 | 4500.8 | 4498.8 | 4498.9 | 3 | 0.37x | 0.95 |
| +5 | 2026-05-20 01:41:00 | 4498.9 | 4502.2 | 4498.5 | 4502.2 | 5 | 0.61x | 0.89 |
