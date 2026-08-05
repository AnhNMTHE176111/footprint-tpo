# Bai lam #05 — Tái phân phối (RE-DIST)

- Anh: `range_05.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-03-18 13:16:00 -> 2026-03-19 03:31:00** = 143 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4918.1, VSA=1.05x, bien do nen=2.4 gia.
- MOVE truoc climax: dai 137.1 gia, 91 nen, hieu suat huong 0.37.
- Bien CHINH (net lien, climax+AR): 4918.1 - 4970.0 = 51.9 gia (1.06% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4918.1 - 4978.0 = 59.9 gia.
- Ty le bien phu/bien chinh: **1.15x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.26x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.21, ty le volume nhip cuoi/dau=0.60 (can kiet).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 7883..7885 (2026-03-18 15:02:00), effort(VSA TB)=1.62x, result(bien do/ATR)=5.06, ty le er=0.32 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-03-18 13:16:00 | 2026-03-18 14:31:00 | 27 |
| B | 2026-03-18 14:36:00 | 2026-03-18 17:38:00 | 57 |
| C | 2026-03-18 17:42:00 | 2026-03-18 20:12:00 | 34 |
| D | 2026-03-18 20:16:00 | 2026-03-19 02:58:00 | 25 |
| E | 2026-03-19 03:31:00 | 2026-03-19 03:31:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-03-18 12:43:00 | 4953.9 | A | - | 2.26x | 0.94 |
| AR | 2026-03-18 14:05:00 | 4970.0 | A | - | 0.75x | 0.00 |
| ST[A] | 2026-03-18 14:31:00 | 4937.0 | A | - | 0.95x | 1.00 |
| mSOS | 2026-03-18 17:35:00 | 4978.0 | B | - | 0.54x | 0.00 |
| LPSY[C] | 2026-03-18 17:42:00 | 4971.0 | C | - | 0.56x | 0.00 |
| SOW | 2026-03-18 20:16:00 | 4898.9 | D | - | 4.00x | 0.65 |
| LPSY[D] | 2026-03-19 01:40:00 | 4940.0 | D | - | 0.43x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-03-18 12:59:00 | 4955.7 | 4958.6 | 4955.7 | 4958.6 | 4 | 1.51x | 1.00 |
| -5 | 2026-03-18 13:00:00 | 4940.0 | 4941.0 | 4932.0 | 4932.0 | 4 | 1.43x | 0.89 |
| -4 | 2026-03-18 13:01:00 | 4935.0 | 4935.0 | 4929.0 | 4929.0 | 4 | 1.40x | 1.00 |
| -3 | 2026-03-18 13:04:00 | 4938.7 | 4938.7 | 4938.7 | 4938.7 | 1 | 0.35x | 0.00 |
| -2 | 2026-03-18 13:11:00 | 4928.0 | 4928.2 | 4926.0 | 4928.2 | 4 | 1.36x | 0.09 |
| -1 | 2026-03-18 13:15:00 | 4924.0 | 4924.0 | 4924.0 | 4924.0 | 1 | 0.34x | 0.00 |
| +0 **<- climax** | 2026-03-18 13:16:00 | 4920.5 | 4920.5 | 4918.1 | 4918.1 | 3 | 1.05x | 1.00 |
| +1 | 2026-03-18 13:18:00 | 4920.0 | 4920.0 | 4920.0 | 4920.0 | 1 | 0.35x | 0.00 |
| +2 | 2026-03-18 13:20:00 | 4928.5 | 4928.5 | 4928.5 | 4928.5 | 1 | 0.37x | 0.00 |
| +3 | 2026-03-18 13:22:00 | 4936.9 | 4939.0 | 4936.9 | 4939.0 | 2 | 0.73x | 1.00 |
| +4 | 2026-03-18 13:30:00 | 4932.3 | 4932.3 | 4930.4 | 4930.9 | 11 | 3.61x | 0.74 |
| +5 | 2026-03-18 13:33:00 | 4934.0 | 4934.0 | 4934.0 | 4934.0 | 1 | 0.36x | 0.00 |
