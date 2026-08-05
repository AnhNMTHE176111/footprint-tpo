# Bai lam #38 — Tích lũy (ACC)

- Anh: `range_38.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-30 01:07:00 -> 2026-06-30 06:30:00** = 323 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 3955.4, VSA=7.11x, bien do nen=25.6 gia.
- MOVE truoc climax: dai 60.1 gia, 108 nen, hieu suat huong 0.38.
- Bien CHINH (net lien, climax+AR): 3955.4 - 3994.2 = 38.8 gia (0.98% gia).
- Bien PHU (net dut, cuc tri xa nhat): 3955.4 - 3994.2 = 38.8 gia.
- Ty le bien phu/bien chinh: **1.00x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=7.11x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+1` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.99, ty le volume nhip cuoi/dau=1.36 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.42, ty le volume nhip cuoi/dau=0.47 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 77169..77175 (2026-06-30 03:09:00), effort(VSA TB)=0.83x, result(bien do/ATR)=1.57, ty le er=0.53 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-30 01:07:00 | 2026-06-30 01:49:00 | 43 |
| B | 2026-06-30 01:50:00 | 2026-06-30 03:33:00 | 104 |
| C | 2026-06-30 03:34:00 | 2026-06-30 04:29:00 | 56 |
| D | 2026-06-30 04:30:00 | 2026-06-30 06:30:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-30 01:07:00 | 3955.4 | A | - | 7.11x | 0.86 |
| AR | 2026-06-30 01:29:00 | 3994.2 | A | - | 1.37x | 0.03 |
| ST[A] | 2026-06-30 01:49:00 | 3974.5 | A | - | 0.76x | 0.20 |
| LPS[C] | 2026-06-30 03:34:00 | 3973.1 | C | - | 0.41x | 0.18 |
| SOS | 2026-06-30 04:30:00 | 4000.1 | D | - | 4.09x | 0.69 |
| LPS[D] | 2026-06-30 04:48:00 | 3997.2 | D | - | 0.44x | 0.12 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-30 01:01:00 | 3993.6 | 3997.1 | 3993.2 | 3993.9 | 108 | 0.72x | 0.08 |
| -5 | 2026-06-30 01:02:00 | 3993.3 | 3993.3 | 3988.8 | 3990.6 | 159 | 1.08x | 0.60 |
| -4 | 2026-06-30 01:03:00 | 3991.2 | 3995.1 | 3990.5 | 3994.8 | 99 | 0.69x | 0.78 |
| -3 | 2026-06-30 01:04:00 | 3993.3 | 3998.4 | 3992.8 | 3993.4 | 170 | 1.16x | 0.02 |
| -2 | 2026-06-30 01:05:00 | 3992.5 | 3993.0 | 3988.3 | 3988.6 | 234 | 1.51x | 0.83 |
| -1 | 2026-06-30 01:06:00 | 3988.2 | 3988.3 | 3976.6 | 3980.3 | 789 | 4.11x | 0.68 |
| +0 **<- climax** | 2026-06-30 01:07:00 | 3981.0 | 3981.0 | 3955.4 | 3959.1 | 2097 | 7.11x | 0.86 |
| +1 | 2026-06-30 01:08:00 | 3960.2 | 3979.3 | 3958.4 | 3975.4 | 880 | 2.62x | 0.73 |
| +2 | 2026-06-30 01:09:00 | 3975.4 | 3982.0 | 3974.8 | 3976.9 | 563 | 1.55x | 0.21 |
| +3 | 2026-06-30 01:10:00 | 3978.0 | 3983.0 | 3976.0 | 3976.0 | 292 | 0.78x | 0.29 |
| +4 | 2026-06-30 01:11:00 | 3976.2 | 3977.1 | 3971.0 | 3971.9 | 215 | 0.56x | 0.70 |
| +5 | 2026-06-30 01:12:00 | 3971.9 | 3976.0 | 3970.5 | 3973.9 | 169 | 0.43x | 0.36 |
