# Bai lam #24 — Tích lũy (ACC)

- Anh: `range_24.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-06-02 01:01:00 -> 2026-06-02 06:26:00** = 325 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4501.0, VSA=5.98x, bien do nen=7.4 gia.
- MOVE truoc climax: dai 18.3 gia, 29 nen, hieu suat huong 0.59.
- Bien CHINH (net lien, climax+AR): 4501.0 - 4521.6 = 20.6 gia (0.46% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4492.3 - 4530.0 = 37.7 gia.
- Ty le bien phu/bien chinh: **1.83x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=5.98x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **SOT phia DUOI**: trang thai=`SOT`, n=3 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.16, ty le volume nhip cuoi/dau=0.92 (can kiet).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 49798..49807 (2026-06-02 02:33:00), effort(VSA TB)=1.35x, result(bien do/ATR)=2.57, ty le er=0.52 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-06-02 01:01:00 | 2026-06-02 01:18:00 | 18 |
| B | 2026-06-02 01:19:00 | 2026-06-02 04:00:00 | 162 |
| D | 2026-06-02 04:01:00 | 2026-06-02 04:25:00 | 25 |
| E | 2026-06-02 04:26:00 | 2026-06-02 06:26:00 | 121 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-06-02 01:01:00 | 4501.0 | A | - | 5.98x | 0.07 |
| AR (yếu) | 2026-06-02 01:14:00 | 4521.6 | A | - | 1.88x | 0.04 |
| ST[A] | 2026-06-02 01:18:00 | 4511.4 | A | - | 0.81x | 0.46 |
| mSOW | 2026-06-02 01:52:00 | 4492.3 | B | - | 2.40x | 0.15 |
| SOS | 2026-06-02 04:01:00 | 4531.0 | D | - | 7.45x | 0.70 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-06-02 00:55:00 | 4511.2 | 4511.2 | 4510.6 | 4510.9 | 10 | 0.35x | 0.50 |
| -5 | 2026-06-02 00:56:00 | 4511.5 | 4512.0 | 4511.4 | 4512.0 | 5 | 0.18x | 0.83 |
| -4 | 2026-06-02 00:57:00 | 4512.2 | 4513.8 | 4511.3 | 4511.7 | 32 | 1.14x | 0.20 |
| -3 | 2026-06-02 00:58:00 | 4512.4 | 4512.5 | 4511.9 | 4512.1 | 6 | 0.22x | 0.50 |
| -2 | 2026-06-02 00:59:00 | 4512.7 | 4512.9 | 4510.6 | 4511.0 | 51 | 1.79x | 0.74 |
| -1 | 2026-06-02 01:00:00 | 4510.7 | 4512.6 | 4508.5 | 4508.6 | 128 | 3.91x | 0.51 |
| +0 **<- climax** | 2026-06-02 01:01:00 | 4508.1 | 4508.4 | 4501.0 | 4507.6 | 272 | 5.98x | 0.07 |
| +1 | 2026-06-02 01:02:00 | 4507.2 | 4510.1 | 4505.2 | 4508.6 | 105 | 2.31x | 0.29 |
| +2 | 2026-06-02 01:03:00 | 4508.9 | 4516.1 | 4508.6 | 4512.4 | 126 | 2.53x | 0.47 |
| +3 | 2026-06-02 01:04:00 | 4512.4 | 4512.9 | 4510.7 | 4511.7 | 18 | 0.36x | 0.32 |
| +4 | 2026-06-02 01:05:00 | 4512.4 | 4515.0 | 4512.1 | 4512.1 | 25 | 0.50x | 0.10 |
| +5 | 2026-06-02 01:06:00 | 4512.2 | 4513.5 | 4512.0 | 4513.5 | 13 | 0.26x | 0.87 |
