# Bai lam #25 — Tích lũy (ACC)

- Anh: `range_25.png`
- Khung: M1 (GCQ26, gio UTC). Range: **2026-05-26 11:43:00 -> 2026-05-26 13:52:00** = 129 nen.
- Climax mo range: **SC (move GIAM bi chan)** tai gia 4538.0, VSA=2.71x, bien do nen=5.6 gia.
- MOVE truoc climax: dai 23.0 gia, 52 nen, hieu suat huong 0.60.
- Bien CHINH (net lien, climax+AR): 4538.0 - 4548.4 = 10.4 gia (0.23% gia).
- Bien PHU (net dut, cuc tri xa nhat): 4533.1 - 4556.8 = 23.7 gia.
- Ty le bien phu/bien chinh: **2.28x** (guard huy range khi > 4.0x).
- Nhan climax mang VSA=5.62x (cay volume cao nhat trong cum, KHONG can trung voi cuc tri gia).
- Trang thai range: **completed**.

## Ba chi so Phase B (v6 — CHI DO/HIEN THI, khong dung de loc)

- **Bias bat doi xung test bien**: `+0` (+1 = cham noi bien tren khong voi noi bien duoi, -1 = nguoc lai, 0 = test CA HAI bien — ca THUONG).
- **SOT phia TREN**: trang thai=`chớm`, n=2 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.23, ty le volume nhip cuoi/dau=1.00 (HAP THU (volume >= nhip dau, canh giu vung)).
- **SOT phia DUOI**: trang thai=`chớm`, n=1 nhip lien tiep rut ngan, ty le thrust cuoi/dau=0.00, ty le volume nhip cuoi/dau=0.00 (-).
- **Nhip no luc/ket qua cao nhat** trong Phase B: nen 43502..43516 (2026-05-26 12:34:00), effort(VSA TB)=1.33x, result(bien do/ATR)=0.86, ty le er=1.54 — vung hap thu NGHI VAN (volume nhieu, ket qua it).

## Phase (do dai tinh bang nen M1)

| Phase | Bat dau | Ket thuc | So nen |
|---|---|---|---|
| A | 2026-05-26 11:43:00 | 2026-05-26 11:58:00 | 16 |
| B | 2026-05-26 11:59:00 | 2026-05-26 12:30:00 | 32 |
| C | 2026-05-26 12:31:00 | 2026-05-26 12:48:00 | 18 |
| D | 2026-05-26 12:49:00 | 2026-05-26 13:01:00 | 13 |
| E | 2026-05-26 13:02:00 | 2026-05-26 13:52:00 | 51 |

## Su kien da gan nhan

| Nhan | Thoi diem | Gia | Phase | Trang thai | VSA nen do | Than/bien do |
|---|---|---|---|---|---|---|
| SC | 2026-05-26 11:35:00 | 4540.4 | A | - | 5.62x | 0.64 |
| AR | 2026-05-26 11:47:00 | 4548.4 | A | - | 1.18x | 0.80 |
| ST[A] | 2026-05-26 11:58:00 | 4536.0 | A | - | 2.18x | 0.58 |
| Spring | 2026-05-26 12:31:00 | 4533.1 | C | confirmed | 3.31x | 0.44 |
| SOS | 2026-05-26 12:49:00 | 4552.5 | D | - | 2.15x | 0.67 |

## 12 nen quanh climax (kiem dieu kien mo range)

| # | Thoi diem | O | H | L | C | Volume | VSA | than/bien |
|---|---|---|---|---|---|---|---|---|
| -6 | 2026-05-26 11:37:00 | 4545.8 | 4548.8 | 4545.3 | 4548.0 | 50 | 1.19x | 0.63 |
| -5 | 2026-05-26 11:38:00 | 4548.5 | 4548.7 | 4544.0 | 4544.2 | 24 | 0.56x | 0.91 |
| -4 | 2026-05-26 11:39:00 | 4543.6 | 4545.5 | 4541.8 | 4543.7 | 29 | 0.68x | 0.03 |
| -3 | 2026-05-26 11:40:00 | 4543.5 | 4545.0 | 4542.0 | 4544.8 | 43 | 0.98x | 0.43 |
| -2 | 2026-05-26 11:41:00 | 4545.0 | 4545.9 | 4543.6 | 4545.0 | 31 | 0.71x | 0.00 |
| -1 | 2026-05-26 11:42:00 | 4545.0 | 4545.0 | 4539.4 | 4539.8 | 45 | 1.03x | 0.93 |
| +0 **<- climax** | 2026-05-26 11:43:00 | 4539.3 | 4543.6 | 4538.0 | 4542.8 | 130 | 2.71x | 0.62 |
| +1 | 2026-05-26 11:44:00 | 4542.2 | 4543.4 | 4542.2 | 4543.4 | 33 | 0.68x | 1.00 |
| +2 | 2026-05-26 11:45:00 | 4542.6 | 4544.1 | 4541.7 | 4541.7 | 23 | 0.48x | 0.38 |
| +3 | 2026-05-26 11:46:00 | 4541.1 | 4545.2 | 4541.1 | 4545.2 | 19 | 0.40x | 1.00 |
| +4 | 2026-05-26 11:47:00 | 4545.4 | 4548.4 | 4545.4 | 4547.8 | 59 | 1.18x | 0.80 |
| +5 | 2026-05-26 11:48:00 | 4546.7 | 4547.6 | 4546.3 | 4546.5 | 16 | 0.32x | 0.15 |
