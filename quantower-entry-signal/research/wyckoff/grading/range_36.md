# Bai lam #36 — Phân phối (DIST)

- Anh: `range_36.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-12 08:20:00 -> 2026-06-12 11:54:00** = 214 nen.
- Climax mo range: **BCLX (move TANG bi chan)** tai gia 4242.0, VSA=0.96x, bien do nen=7.7 gia.
- MOVE truoc climax: dai 42.3 gia, 47 nen, hieu suat huong 0.52.
- Bien CHINH (net lien, climax+AR): 4232.8 - 4242.0 = 9.2 gia (0.22% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4223.6 - 4247.7 = 24.1 gia.
- Ty le bien phu/bien chinh: **2.62x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=2.89x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.67, ty le volume nhip cuoi/dau=1.25 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`xu hướng quá mạnh`, n=5 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.70, ty le volume nhip cuoi/dau=0.54 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 61254..61257 (2026-06-12 09:30:00), effort(VSA TB)=1.92x, result(bien do/ATR)=2.29, ty le er=0.84 — nhip HIEU QUA (ket qua nhieu hon no luc, khong phai hap thu).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-12 08:20:00 | 2026-06-12 08:39:00 | 20 |
| B | 2026-06-12 08:40:00 | 2026-06-12 10:57:00 | 138 |
| C | 2026-06-12 10:58:00 | 2026-06-12 11:28:00 | 31 |
| D | 2026-06-12 11:29:00 | 2026-06-12 11:53:00 | 25 |
| E | 2026-06-12 11:54:00 | 2026-06-12 11:54:00 | 1 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| BCLX | 2026-06-12 08:18:00 | 4240.3 | A | - | 2.89x | 0.85 |
| AR | 2026-06-12 08:28:00 | 4232.8 | A | - | 0.85x | 0.52 |
| ST[A] | 2026-06-12 08:39:00 | 4244.9 | A | - | 3.41x | 0.08 |
| mSOS | 2026-06-12 10:55:00 | 4234.2 | B | - | 6.18x | 0.36 |
| mSOW | 2026-06-12 10:58:00 | 4231.7 | B | provisional | 5.29x | 0.04 |
| LPSY[C] | 2026-06-12 10:58:00 | 4236.7 | C | - | 5.29x | 0.04 |
| SOW | 2026-06-12 11:29:00 | 4223.5 | D | - | 1.84x | 0.81 |
| LPSY[D] | 2026-06-12 11:46:00 | 4232.8 | D | - | 0.55x | 0.00 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-12 08:14:00 | 4225.2 | 4225.3 | 4223.2 | 4224.9 | 97 | 0.56x | 0.14 |
| -5 | 2026-06-12 08:15:00 | 4225.7 | 4227.0 | 4220.8 | 4222.5 | 133 | 0.75x | 0.52 |
| -4 | 2026-06-12 08:16:00 | 4222.4 | 4228.6 | 4222.4 | 4228.1 | 91 | 0.57x | 0.92 |
| -3 | 2026-06-12 08:17:00 | 4227.4 | 4233.4 | 4226.0 | 4232.4 | 210 | 1.39x | 0.68 |
| -2 | 2026-06-12 08:18:00 | 4231.9 | 4240.3 | 4230.4 | 4240.3 | 474 | 2.89x | 0.85 |
| -1 | 2026-06-12 08:19:00 | 4239.6 | 4241.5 | 4236.7 | 4239.1 | 337 | 2.00x | 0.10 |
| +0 **<- climax** | 2026-06-12 08:20:00 | 4239.7 | 4242.0 | 4234.3 | 4234.8 | 154 | 0.96x | 0.64 |
| +1 | 2026-06-12 08:21:00 | 4234.6 | 4239.0 | 4233.7 | 4238.6 | 144 | 0.91x | 0.75 |
| +2 | 2026-06-12 08:22:00 | 4238.7 | 4241.7 | 4238.7 | 4239.8 | 122 | 0.83x | 0.37 |
| +3 | 2026-06-12 08:23:00 | 4239.2 | 4240.1 | 4236.0 | 4238.5 | 101 | 0.69x | 0.17 |
| +4 | 2026-06-12 08:24:00 | 4238.5 | 4240.1 | 4237.4 | 4239.9 | 82 | 0.58x | 0.52 |
| +5 | 2026-06-12 08:25:00 | 4239.9 | 4240.6 | 4236.1 | 4236.1 | 96 | 0.69x | 0.84 |
