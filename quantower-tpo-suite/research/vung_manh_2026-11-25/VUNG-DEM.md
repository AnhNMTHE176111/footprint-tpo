# Vùng đệm quanh hộp HVN — đo các lần giá quay lại hộp (Fable, 2026-11-25)

Spec cho Opus: [`../../PLAN-VUNG-MANH.md`](../../PLAN-VUNG-MANH.md) **mục 14**. Bản tham chiếu: [`vung_dem.py`](vung_dem.py) hàm `add_buffers()`; hộp được vẽ: `vung_manh.hvn_boxes()` (đã thêm `buf_lo`, `buf_hi`).
Dữ liệu một hợp đồng: GCZ26 (tới 2026-11-09) và NQZ26 ghép thêm file mới tới 2026-11-25 08:47 UTC. Hộp = HVN dạng cụm v2 (mục 13), đã đủ điều kiện "rời xa" 2 U.

## 0. Kết luận trước

1. **Giá đảo trước khi chạm mép hộp là chuyện thường**: trong các lần giá về cách mép hộp ≤ 0,5 U, 35 % (NQ) và 42 % (GC) đảo trước mép; 24 % và 22 % đảo trong hộp; 41 % và 36 % xuyên qua mép xa.
2. **Nhưng hộp dời đi 1,5–4 U cho đúng phân phối đó** (NQ 38 / 21 / 42 %, GC 39 / 22 / 39 %). Điểm đảo không tụ quanh hộp HVN hơn quanh một mức bất kỳ. Mật độ điểm đảo gần như đều từ 0,5 U trước mép tới hết hộp — mép hộp không phải một ranh giới đo được.
3. **Giả thuyết "vùng râu"**: bề rộng đệm dựng từ đầu râu M30 không bắt điểm đảo tốt hơn đệm cố định cùng bề rộng, không hơn khi đổi chéo bề rộng giữa các hộp, không hơn hộp dời. Tương quan giữa bề rộng vùng râu và khoảng cách đảo thật: −0,16 đến +0,01. Dựng từ sườn profile hay từ số nến M30 phủ giá cũng vậy. **Không cách dựng nào được kiểm định.**
4. **Ca NQ 25/11 thì khớp**: vùng râu của người dùng trùng với một bướu phụ của chính cụm khối lượng (cao 68 % đỉnh, ở 25.620–25.650) mà hộp v2 cắt bỏ vì đã đủ bề rộng 0,45 up. Đáy 25.637,25 nằm trong bướu đó.
5. **Đề xuất**: vẽ vùng đệm = phần sườn cụm còn ≥ 50 % đỉnh nằm sát ngoài mép hộp (tối đa 0,45 up mỗi phía), màu cam nhạt hơn hộp, chỉ ở phía giá đang đứng. Ca NQ ra **25.609,75 – 25.652,25**. Lý do chọn là mô tả đúng thứ người dùng nhìn thấy và rẻ, **không phải vì đo ra lợi thế**. Không đưa vùng đệm vào hợp lưu vùng mạnh (vàng sẽ tăng lên 25–32 % thời gian). Không thêm input.

## 1. Cách đo (`python vung_dem_events.py gc|nq25`, `python vung_dem_do.py gc|nq25`)

- **Lần quay lại**: giá (nến M1) vào dải cách mép hộp ≤ 0,5 U, sau khi đã rời mép ≥ 2 U (lần đầu tính từ lúc profile chốt, đúng điều kiện "rời xa" của indicator; các lần sau cũng 2 U). Phía tiếp cận = phía giá đứng trước đó.
- **Điểm đảo**: đáy thấp nhất (tới từ trên) hoặc đỉnh cao nhất (tới từ dưới) trước khi giá bật ngược ≥ 1 U lần đầu. Đo khoảng cách tới mép gần, đơn vị U (U = biên độ M30 trung bình 5 phiên trước).
- **Đối chứng**: chính các hộp đó dời ± 1,5–4 U (3 lần mỗi hộp), mọi thứ khác giữ nguyên.
- Khoảng 5–95 % lấy bằng cách rút lại theo hộp (các lần quay lại cùng một hộp không độc lập).

| | NQZ26 | GCZ26 |
|---|---|---|
| Lần quay lại hộp thật | 192 (57 hộp) | 274 (81 hộp) |
| … hộp ngày / hộp tuần | 131 / 61 | 182 / 92 |
| Lần quay lại hộp dời | 530 | 700 |
| Bề rộng hộp (U), p10 / 50 / 90 | 0,36 / 0,45 / 0,58 | 0,40 / 0,46 / 0,63 |

## 2. Điểm đảo so với mép hộp

| Mã | Loại | Phía tiếp cận | n | Đảo trước mép | Đảo trong hộp | Xuyên qua mép xa | Khoảng cách đảo trước mép (U), p25 / 50 / 75 |
|---|---|---|---|---|---|---|---|
| NQ | hộp thật | từ trên xuống | 94 | 33 % | 27 % | 40 % | 0,13 / 0,22 / 0,38 |
| NQ | hộp thật | từ dưới lên | 98 | 37 % | 22 % | 41 % | 0,20 / 0,29 / 0,38 |
| NQ | **hộp thật** | cả hai | 192 | **35 %** [29; 41] | **24 %** [20; 29] | **41 %** [34; 48] | 0,16 / 0,28 / 0,38 |
| NQ | hộp dời | cả hai | 530 | 38 % | 21 % | 42 % | 0,14 / 0,25 / 0,40 |
| GC | hộp thật | từ trên xuống | 127 | 42 % | 22 % | 36 % | 0,18 / 0,33 / 0,40 |
| GC | hộp thật | từ dưới lên | 147 | 43 % | 21 % | 36 % | 0,18 / 0,32 / 0,39 |
| GC | **hộp thật** | cả hai | 274 | **42 %** [38; 47] | **22 %** [18; 26] | **36 %** [32; 41] | 0,18 / 0,32 / 0,40 |
| GC | hộp dời | cả hai | 700 | 39 % | 22 % | 39 % | 0,15 / 0,29 / 0,41 |

Mật độ điểm đảo theo từng dải 0,1 U (% số lần quay lại):

| | trước mép 0,4–0,5 | 0,3–0,4 | 0,2–0,3 | 0,1–0,2 | 0–0,1 | trong hộp 0–0,1 | 0,1–0,2 | 0,2–0,3 | 0,3–0,4 | 0,4–0,5 |
|---|---|---|---|---|---|---|---|---|---|---|
| NQ thật | 8,3 | 6,2 | 9,4 | 5,2 | 5,7 | 3,1 | 3,6 | 7,8 | 6,8 | 2,6 |
| NQ dời | 9,2 | 6,8 | 6,6 | 7,5 | 7,4 | 4,5 | 5,3 | 4,3 | 3,2 | 4,2 |
| GC thật | 10,6 | 11,7 | 8,4 | 5,1 | 6,6 | 6,6 | 5,1 | 4,0 | 3,6 | 2,9 |
| GC dời | 11,0 | 8,0 | 7,4 | 6,7 | 5,9 | 5,6 | 4,3 | 4,3 | 6,0 | 2,6 |

Đọc:
- Hai phía tiếp cận giống nhau. Không có lý do đo được để xử lý phía trên khác phía dưới.
- Mọi ô của hộp thật nằm trong sai số so với hộp dời. Đổi ngưỡng bật ngược sang 0,5 U hoặc 1,5 U: vẫn vậy (NQ 59 / 21 / 19 % so với 61 / 18 / 21 %; 29 / 21 / 50 % so với 27 / 17 / 56 %).
- Khi giá đảo trước mép, khoảng cách điển hình là 0,2–0,4 U (NQ khoảng 30–60 điểm, GC khoảng 2,5–5 giá). Đó là cỡ của vùng người dùng vẽ tay (60 điểm). Con số này mô tả "đảo trước một mức bất kỳ", không riêng gì hộp HVN.

## 3. Vùng đệm: so các cách dựng

Vùng đệm phía tiếp cận, bề rộng cắt ở 0,5 U. "Bắt" = điểm đảo rơi vào vùng đệm.

- **Râu M30 (giả thuyết người dùng)**: trong profile nguồn, lấy các nến M30 có thân chạm hộp (hoặc: đóng trong hộp) và râu nhô khỏi mép; đệm = từ mép tới trung vị các đầu râu.
- **Sườn profile**: nới từ mép ra ngoài khi khối lượng mượt còn ≥ 50 % (hoặc 40 %) đỉnh cụm.
- **Số nến M30 phủ giá**: nới khi số nến M30 của profile nguồn đi qua mức giá đó còn ≥ 67 % so với trong hộp.
- **Hoán vị**: giữ nguyên bộ bề rộng, đổi chéo giữa các hộp 400 lần. Nếu bề rộng mang thông tin riêng của từng hộp, số thật phải vượt khoảng hoán vị.

| Cách dựng | Mã | Bề rộng TB (U) | Bắt (thật) | Hộp dời | Đệm cố định cùng bề rộng | Hoán vị, trung bình [5; 95 %] |
|---|---|---|---|---|---|---|
| cố định 0,20 U | NQ | 0,20 | 10,9 % | 14,9 % | — | — |
| cố định 0,30 U | NQ | 0,30 | 20,3 % | 21,5 % | — | — |
| râu, thân chạm hộp | NQ | 0,38 | 25,0 % | 27,7 % | 26,0 % | 24,3 % [21,4; 27,1] |
| râu, đóng trong hộp | NQ | 0,30 | 18,2 % | 21,5 % | 20,3 % | 18,9 % [15,6; 21,9] |
| **sườn ≥ 50 %, trần 0,45 up (đề xuất)** | NQ | 0,26 | 15,6 % | 19,4 % | 16,1 % | 16,4 % [13,0; 19,8] |
| sườn ≥ 40 % | NQ | 0,36 | 23,4 % | 27,4 % | 25,5 % | 24,2 % [20,8; 27,1] |
| nến phủ ≥ 67 % | NQ | 0,26 | 16,7 % | 19,8 % | 16,1 % | 16,9 % [13,5; 20,3] |
| cố định 0,20 U | GC | 0,20 | 11,7 % | 12,6 % | — | — |
| cố định 0,30 U | GC | 0,30 | 20,1 % | 20,0 % | — | — |
| râu, thân chạm hộp | GC | 0,38 | 27,4 % | 26,9 % | 28,1 % | 27,2 % [24,5; 29,9] |
| râu, đóng trong hộp | GC | 0,30 | 22,3 % | 21,4 % | 20,4 % | 20,5 % [17,9; 23,4] |
| **sườn ≥ 50 %, trần 0,45 up (đề xuất)** | GC | 0,28 | 22,3 % | 17,6 % | 17,5 % | 20,8 % [17,5; 24,1] |
| sườn ≥ 40 % | GC | 0,39 | 31,8 % | 26,9 % | 30,7 % | 30,8 % [27,7; 34,3] |
| nến phủ ≥ 67 % | GC | 0,27 | 19,3 % | 15,1 % | 16,4 % | 19,3 % [15,7; 23,0] |

Tương quan hạng giữa bề rộng đệm và khoảng cách đảo thật (chỉ các lần đảo trước mép; NQ 67 lần, GC 116 lần):

| | râu, thân chạm hộp | râu, đóng trong hộp | sườn ≥ 50 % (đề xuất) | sườn ≥ 40 % | nến phủ ≥ 67 % |
|---|---|---|---|---|---|
| NQ | +0,01 | −0,06 | −0,11 | −0,09 | −0,02 |
| GC | −0,16 | −0,11 | +0,06 | +0,02 | +0,01 |

Đặt limit ở mép ngoài vùng đệm (lệnh treo tới khi giá bật ngược), dừng lỗ sau mép xa của hộp 0,15 U:

| Cách dựng | Mã | Khớp | Rủi ro TB (U) | Thắng 1:1 | R 1:2 mỗi lệnh [5; 95 %] | Hộp dời: thắng · R 1:2 |
|---|---|---|---|---|---|---|
| mép hộp, không đệm | NQ | 65 % | 0,63 | 45,6 % (125 lệnh) | −0,040 [−0,23; +0,14] | 44,7 % · −0,030 |
| cố định 0,30 U | NQ | 85 % | 0,92 | 47,6 % (164) | +0,003 [−0,18; +0,16] | 47,9 % · −0,029 |
| râu, thân chạm hộp | NQ | 90 % | 1,01 | 46,2 % (173) | +0,003 [−0,22; +0,19] | 49,2 % · −0,077 |
| sườn ≥ 50 % (đề xuất) | NQ | 81 % | 0,91 | 47,7 % (155) | −0,093 [−0,25; +0,07] | 48,8 % · −0,074 |
| mép hộp, không đệm | GC | 58 % | 0,63 | 48,7 % (158) | −0,013 [−0,17; +0,14] | 49,4 % · −0,016 |
| cố định 0,30 U | GC | 78 % | 0,93 | 49,3 % (213) | +0,085 [−0,08; +0,23] | 48,7 % · −0,032 |
| râu, thân chạm hộp | GC | 85 % | 1,02 | 50,6 % (233) | +0,030 [−0,12; +0,16] | 49,6 % · +0,034 |
| sườn ≥ 50 % (đề xuất) | GC | 80 % | 0,94 | 53,4 % (219) | +0,137 [−0,02; +0,30] | 48,5 % · −0,018 |

Đọc:
- **Vùng râu**: tỉ lệ bắt bằng đệm cố định cùng bề rộng, nằm giữa khoảng hoán vị, bằng hoặc thấp hơn hộp dời, ở cả hai mã. Tương quan với khoảng cách đảo thật bằng 0 hoặc hơi âm. Giả thuyết "đầu râu trong phiên nguồn chỉ ra chỗ giá sẽ đảo" **không được dữ liệu ủng hộ**.
- **Sườn profile và số nến phủ**: GC nhỉnh hơn hộp dời 4–5 điểm %, NQ thấp hơn 3–4 điểm %. Trái chiều, đều trong khoảng hoán vị.
- **Vùng đệm làm đúng một việc đo được**: tăng tỉ lệ khớp lệnh từ 58–65 % lên 80–90 %, đổi lại rủi ro mỗi lệnh lớn hơn khoảng 1,5 lần. Tỉ lệ thắng và R sau đó không khác hộp dời một cách đo được. Ô tốt nhất (GC, sườn ≥ 50 %: R +0,137) có khoảng chứa 0 và NQ cùng ô ra −0,093.
- Bề rộng nào cũng "bắt" được phần điểm đảo tỉ lệ với bề rộng của nó (khoảng 6–7 điểm % mỗi 0,1 U). Không có chỗ gãy để gọi là bề rộng đúng.

## 4. Ca NQ 20/11 → 25/11

Số thật (U ngày 25/11 = 146,8 điểm; up của phiên 20/11 = 158,0 điểm):

| | |
|---|---|
| Hộp v2 (phiên 20/11) | 25.538,50 – 25.609,75 |
| Profile phiên 20/11 ngay trên mép | tụt còn 52 % đỉnh ở 25.610, lên lại **68 % đỉnh ở 25.640**, xuống dưới 50 % từ 25.652,50 |
| Nến M30 có thân chạm hộp, đầu râu trên | 25.648,75 · 25.653,25 · 25.656,50 · 25.721,50 · 25.762,50 (trung vị 25.656,50) |
| 23/11 02:30 UTC | đáy 25.610,75 — trên mép hộp 1 điểm — bật lên 25.918 |
| 25/11 07:30 UTC | đáy **25.637,25** — trên mép hộp 27,5 điểm = 0,19 U — bật lên 25.915 |
| Vùng người dùng vẽ | khoảng 25.610 – 25.670 |

Vì sao có "vùng râu" ở đó: nó là một bướu khối lượng phụ dính liền cụm. Hộp v2 dừng ở 25.609,75 vì đã đủ bề rộng đích 0,45 up, không phải vì khối lượng hết. Râu tụ ở 25.620–25.660 và bướu phụ là một hiện tượng nhìn từ hai phía: giá có giao dịch ở đó nhưng không đóng nến M30 ở đó.

Ca này với từng cách dựng:

| Cách dựng | Vùng đệm trên | Chứa đáy 25.637,25 |
|---|---|---|
| **sườn ≥ 50 %, trần 0,45 up (đề xuất)** | 25.609,75 – **25.652,25** (42,5 điểm = 0,27 up) | có |
| sườn ≥ 40 % | 25.609,75 – 25.663,75 | có |
| râu thân chạm hộp, trung vị | 25.609,75 – 25.656,50 | có |
| râu, phân vị 25–75 | 25.653,25 – 25.721,50 | **không** |
| cố định 0,10 U | 25.609,75 – 25.624,50 | **không** |
| cố định 0,20 U | 25.609,75 – 25.639,00 | có (cách mép chưa tới 2 điểm) |
| cố định 0,30 U | 25.609,75 – 25.653,75 | có |

Ca này không phân biệt được các cách dựng: mọi cách cho bề rộng ≥ 0,2 U đều chứa nó. Ngưỡng 50 % không được chỉnh theo ca — nó là sàn sẵn có của luật nới hộp (`HvnWidenFloor`); 40 % và 30 % cũng chứa. Phía dưới hộp không có vùng đệm (khối lượng xuống dưới 50 % đỉnh chỉ vài điểm dưới mép 25.538,50 — hẹp hơn 0,05 up).

Ảnh:

| Ảnh | Nội dung |
|---|---|
| [nq_2026-11-20_den_11-25_m15.png](vung_dem/nq_2026-11-20_den_11-25_m15.png) | M15 từ phiên nguồn 20/11 tới 25/11, hộp + vùng đệm, hai lần đảo 23/11 và 25/11 |
| [nq_2026-11-25_dao_trong_vung_dem_m15.png](vung_dem/nq_2026-11-25_dao_trong_vung_dem_m15.png) | M15 riêng 25/11: đáy 25.637,25 trong vùng đệm |
| [nq_2026-11-20_phien_nguon_m15.png](vung_dem/nq_2026-11-20_phien_nguon_m15.png) | M15 phiên nguồn 20/11 16:00–20:00 UTC: các nến rút râu trên quanh mép hộp |
| [nq_2026-11-20_profile_vung_dem.png](vung_dem/nq_2026-11-20_profile_vung_dem.png) | profile phiên 20/11: bướu phụ 25.620–25.650 nằm ngoài hộp, trên vạch 50 % đỉnh |

## 5. Các lần quay lại khác (chọn tự động: lần gần nhất của mỗi loại kết cục, không lựa bằng mắt)

| Ảnh | Kết cục |
|---|---|
| [nq_2026-11-23_dao_trong_dem_1.png](vung_dem/nq_2026-11-23_dao_trong_dem_1.png) · [gc_2026-11-04_dao_trong_dem_1.png](vung_dem/gc_2026-11-04_dao_trong_dem_1.png) | đảo trong vùng đệm |
| [nq_2026-11-19_dao_truoc_dem_1.png](vung_dem/nq_2026-11-19_dao_truoc_dem_1.png) · [gc_2026-10-30_dao_truoc_dem_1.png](vung_dem/gc_2026-10-30_dao_truoc_dem_1.png) | đảo trước cả vùng đệm |
| [nq_2026-11-19_dao_trong_hop_1.png](vung_dem/nq_2026-11-19_dao_trong_hop_1.png) · [gc_2026-11-04_dao_trong_hop_1.png](vung_dem/gc_2026-11-04_dao_trong_hop_1.png) | đảo trong hộp |
| [nq_2026-11-19_xuyen_1.png](vung_dem/nq_2026-11-19_xuyen_1.png) · [gc_2026-11-09_xuyen_1.png](vung_dem/gc_2026-11-09_xuyen_1.png) | xuyên qua hộp |

## 6. Đề xuất cho indicator

**Vùng đệm = sườn cụm còn ≥ 50 % đỉnh, sát ngoài mép hộp.** Nới từ mép hộp ra ngoài chừng nào khối lượng mượt còn ≥ 50 % đỉnh cụm; tối đa 0,45 up mỗi phía; hẹp hơn 0,05 up thì bỏ. Khác luật nới hộp: không dừng vì đủ bề rộng, và được đi qua một đáy nông để lấy bướu phụ.

Vì sao chọn cách này dù không cách nào thắng trên số đo:
- Nó là đúng thứ làm ra "vùng râu" trong ca người dùng (bướu phụ của cụm), tính từ mảng khối lượng đã có sẵn trong `HvnClusters` — không cần thêm dữ liệu, không đổi theo khung chart.
- Hẹp hơn vùng râu (trung bình 0,26–0,28 U so với 0,38 U) với cùng mức "không hơn đối chứng" ⇒ ít chiếm chart hơn.
- Dùng lại hai hằng đã có (50 % = sàn nới hộp, 0,45 up = bề rộng đích); chỉ thêm một hằng 0,05.
- Bề rộng đệm theo râu và theo sườn cùng chiều vừa phải (tương quan hạng 0,42–0,46), nên trên chart hai cách thường ra vùng gần nhau.

Mật độ (`python vung_dem.py thongke nq25|gc`):

| | NQ ngày | NQ tuần | GC ngày | GC tuần |
|---|---|---|---|---|
| Phía có vùng đệm | 79 % | 93 % | 79 % | 95 % |
| Bề rộng đệm (× up), p25 / 50 / 75 | 0,15 / 0,26 / 0,40 | 0,15 / 0,35 / 0,45 | 0,17 / 0,34 / 0,45 | 0,23 / 0,45 / 0,45 |
| Chạm trần 0,45 up | 17 % | 33 % | 32 % | 52 % |

Hộp cộng cả hai vùng đệm rộng gấp khoảng 2 lần hộp (trung vị 1,9–2,4). Vì vậy:

- **Chỉ vẽ phía giá đang đứng**: giá ở trên hộp ⇒ đệm trên; giá ở dưới hộp ⇒ đệm dưới; giá trong hộp ⇒ cả hai. Số đo không cho lý do nào để coi một phía đặc biệt hơn; đây chỉ là để chart bớt rối.
- **Màu**: cùng màu cam của hộp, nền nhạt bằng nửa hộp, không viền, một nét đứt ở mép ngoài. Không có nhãn riêng; dòng Telegram "Hộp HVN" ghi thêm `đệm tới <giá>`.
- **Không thêm input**: vùng đệm đi theo công tắc "Hộp HVN" sẵn có.
- **Hợp lưu vùng mạnh: không tính vùng đệm.** Đã đo (`python vung_dem_hl.py`): nếu tính, số cụm va đập có HVN tăng từ 40 → 57 % (GC), 31 → 50 % (NQ); thời gian có vùng vàng tăng từ 23,0 → 31,7 % (GC), 14,7 → 25,3 % (NQ). Vàng vốn đã bị loãng sau v2; vùng đệm lại không có số đo nào đỡ lưng.
- **"Rời xa", bán kính 8 U, trần 2 hộp mỗi phía, gộp hộp trùng**: vẫn đo từ mép hộp, không đổi.
- **Số vàng trên chart / nhãn**: không đổi. Trạng thái cả lớp vẫn là **chưa kiểm định**.

Trạng thái trên NQZ26 lúc nến 07:30 UTC ngày 25/11 đóng (giá 25.780,25): hộp `25.538,50 – 25.609,75 · HVN ngày + tuần` có đệm trên tới 25.652,25; hộp `26.249,50 – 26.312,75` có đệm dưới từ 26.227,50; hộp `26.804,25 – 26.873,50` có đệm dưới từ 26.767,25.

## 7. Giới hạn

- NQ 192 lần quay lại trên 57 hộp, GC 274 lần trên 81 hộp; nhiều lần thuộc cùng một hộp. Hiệu ứng nhỏ hơn khoảng 6–8 điểm % ở tỉ lệ đảo sẽ không thấy được với cỡ mẫu này.
- Không tách TRAIN/TEST; GC trùng dữ liệu với các lần đo trước. Các bảng ở mục 3 có vài chục ô — một ô lệch dương (GC, sườn profile) không đủ để kết luận.
- Điểm đảo định nghĩa bằng "bật ngược 1 U"; đã thử 0,5 và 1,5 U, kết luận không đổi. Chưa xét order flow tại vùng, chưa phí, chưa trượt giá.
- Luật chọn sau khi đã nhìn ca 25/11. Điểm đỡ: ngưỡng lấy từ hằng có sẵn, và ca này không phân biệt được các cách dựng.
- Hộp tuần đang chạy (tuần này tới hết hôm qua) đổi mỗi ngày nên vùng đệm của nó cũng đổi mỗi ngày.

## 8. File

| File | Việc |
|---|---|
| `vung_dem.py` | **bản tham chiếu** `add_buffers()`; `ca nq25 2026-11-20`; `thongke nq25|gc` |
| `vung_dem_prep.py` | bộ đệm NQZ26 tới 25/11 (`vm1_nq25.pkl`), không đụng `vm1_nq.pkl` |
| `vung_dem_lib.py` | nạp dữ liệu |
| `vung_dem_events.py` | sinh lần quay lại (thật + dời) và đặc trưng các cách dựng vùng đệm |
| `vung_dem_do.py` | bảng mục 2 và 3 |
| `vung_dem_hl.py` | mật độ nếu hợp lưu tính cả vùng đệm |
| `vung_dem_ve.py` | PNG vào `vung_dem/` |
| `vung_dem_fixture.py` | `fixture/vung_dem_cases.json`, `fixture/nq25_m30_bars.csv`, `fixture/nq25_m30_levels.csv.gz`, `fixture/nq25_expected.json` |
| `vung_manh.py` | **đã sửa (chỉ thêm)**: mức HVN v2 có thêm `blo`, `bhi`; `hvn_boxes()` trả thêm `buf_lo`, `buf_hi`. Chạy lại `hvn_cum2_fixture.py`: ba file fixture v2 không đổi một byte |

Chạy lại: `python vung_dem_prep.py` → `python vung_dem_events.py nq25` → `python vung_dem_events.py gc` → `python vung_dem_do.py nq25` → `python vung_dem_do.py gc` → `python vung_dem_hl.py gc` → `python vung_dem_ve.py` → `python vung_dem_fixture.py`.
