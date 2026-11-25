# HVN dạng cụm v2 — tiêu chí không phụ thuộc biên độ profile (Fable, 2026-11-25)

Spec cho Opus: [`../../PLAN-VUNG-MANH.md`](../../PLAN-VUNG-MANH.md) **mục 13**. Bản tham chiếu: [`hvn_cum2.py`](hvn_cum2.py). Bản trước: [`HVN-CUM.md`](HVN-CUM.md) (gọi là v1).
Dữ liệu như v1: một hợp đồng, GCZ26 (73 phiên, 15 tuần) và NQZ26 (52 phiên, 11 tuần, tới 2026-11-24 12:00 UTC).

## 0. Kết luận trước

1. **Vì sao sót cụm NQ 25.530–25.608:** v1 đo "đủ lớn" bằng % khối lượng cả profile trên phần thân ≥ 80 % đỉnh. Thân đó ở phiên 20/11 chỉ rộng 36 điểm (6,9 % < 10 %); ở profile tuần cụm chỉ là 2,6 % và đỉnh bằng 0,35 đỉnh lớn nhất tuần (< 0,5). Cả ba phép so đều yếu đi khi profile chạy rộng (phiên 20/11 rộng 10,3 lần biên độ M30, tuần 24,9 lần).
2. **v2 đổi bốn chỗ:** (a) hộp = lõi 80 % rồi nới tới bề rộng 0,45 × biên độ M30; (b) trong mỗi vùng ± 3 lần biên độ M30 chỉ lấy đỉnh cao nhất (thay luật "≥ 50 % đỉnh lớn nhất cả profile"); (c) "đủ lớn" = chứa ≥ 12 % profile ngày / 8 % tuần **hoặc** "nổi bật tại chỗ": chứa ≥ 4,5 nến M30 khối lượng và dày ≥ 2 lần phần xung quanh; (d) số hộp tối đa tăng theo biên độ profile (2 → 4).
3. **Ba ca kiểm:**

   | Ca | Người dùng | v1 | **v2** |
   |---|---|---|---|
   | NQ phiên 20/11 | 25.530 – 25.608 | không có | **25.538,50 – 25.609,75** (11,1 %, dày gấp 2,8 lần xung quanh) |
   | NQ tuần 15 → 20/11 | 25.530 – 25.608 | không có | 27.239,25 – 27.299,00 và **25.544,25 – 25.604,00** |
   | NQ phiên 23/11 | rộng 65 điểm | 26.802,50 – 26.874,75 | **26.801,50 – 26.876,50** (nới thêm 2,75 điểm) |

4. **Số hộp mỗi phiên không tăng đáng kể:** NQ 0,90 → 0,96; GC 0,79 → 0,89. Thay đổi nằm ở phân bố: số phiên có **hai** hộp giảm (NQ 21 % → 4 %, GC 18 % → 5 %), số phiên **không có** hộp giảm (NQ 31 % → 8 %, GC 38 % → 16 %). Profile tuần: 0,45 → 1,82 hộp (NQ), 0,47 → 1,47 (GC).
5. **Hộp cũ bị đổi:** trong các phiên v1 có hộp, NQ 7/36 và GC 13/45 phiên hộp chuyển chỗ hoặc mất. Đây là thay đổi lớn hơn một lần "nới ngưỡng" — cần người dùng xem ảnh lưới (mục 4).
6. **Bán kính 4 U không đủ:** cuối dữ liệu giá 26.398,75, mép trên cụm 25.609,75 cách 789 điểm = **5,5 U**. Kể cả phát hiện đúng, hộp vẫn không được vẽ. Đề xuất: hộp HVN dùng bán kính riêng **8 U** và **tối đa 2 hộp gần nhất mỗi phía giá**.
7. **"Đáy tuần này":** tuần này mở cửa ở 25.561,50 — nằm **trong** hộp — thủng mép dưới 112 điểm (đáy 25.426,75), đóng nến đầu tiên ở 25.700,25 rồi đi lên 1.700 điểm. Đó là giá quay lại hộp và phản ứng, không phải một mức hợp lưu theo nghĩa của bộ máy. Thêm đáy/đỉnh tuần làm mức hợp lưu: đã đo thử, mẫu quá nhỏ, **chưa đưa vào spec**.
8. **Vùng mạnh:** kết luận so với đối chứng không đổi — **vẫn chưa kiểm định**. Thời gian có vùng vàng: GC 15,1 % → 23,0 %, NQ 19,0 % → 14,9 %.

## 1. Vì sao v1 sót (`python hvn_cum2.py ca nq 2026-11-20`)

| | Phiên 20/11 | Tuần 15 → 20/11 | Phiên 23/11 (ca mẫu v1) |
|---|---|---|---|
| Biên độ profile | 24.976,50 – 26.603,50 = 10,3 up | 24.976,50 – 28.279,25 = 24,9 up | 25.426,75 – 27.137,00 = 10,3 up |
| Thân ≥ 80 % đỉnh | 25.557,75 – 25.594,00 (36 điểm = 0,23 up) | 25.558,75 – 25.593,25 | 26.802,50 – 26.874,75 (0,43 up) |
| Tỉ trọng thân | 6,9 % (cần 10 %) | 1,8 % (cần 8 %) | 28,5 % |
| Đỉnh so với đỉnh lớn nhất | 1,00 | 0,35 (cần 0,50) | 1,00 |

(up = biên độ High − Low trung bình của các nến M30 trong chính profile; phiên 20/11: 158 điểm.)

- Cụm 20/11 là một bướu hình chuông: đỉnh ở 25.583, sườn dưới thoải tới 25.530, sườn trên tụt về một đáy ở 25.610 rồi mới tới bướu kế 25.640. Hộp người dùng ôm cả bướu (tới khoảng nửa chiều cao đỉnh), không chỉ phần ≥ 80 %.
- Phiên 23/11 thì đỉnh phẳng, hộp người dùng trùng phần ≥ 80 %. Hai hộp người dùng có cùng cỡ: 65 điểm = 0,39 up và 78 điểm = 0,49 up. Đó là cơ sở của luật "nới tới bề rộng đích".

## 2. Định nghĩa v2

| Tiêu chí | v1 | v2 |
|---|---|---|
| **Hộp** | thân có khối lượng mượt ≥ 80 % đỉnh | lõi ≥ 80 % đỉnh; lõi hẹp hơn **0,45 up** thì nới dần về phía còn dày hơn tới khi đủ 0,45 up; không lấy mức giá dưới 50 % đỉnh; không leo sang bướu bên cạnh (dừng khi khối lượng tăng lại quá 5 % đỉnh) |
| **Nhiều cụm** | đỉnh ≥ 50 % đỉnh lớn nhất cả profile; tối đa 2 | đỉnh phải cao nhất trong **± 3 up** quanh nó; tối đa 2 hộp, profile rộng ≥ 18 up được 3, ≥ 24 up được 4 |
| **Đủ lớn** | ≥ 10 % profile ngày, ≥ 8 % tuần | **lớn:** ≥ 12 % profile ngày, ≥ 8 % tuần — **hoặc nổi bật tại chỗ:** hộp chứa ≥ **4,5 nến M30** khối lượng (so với nến trung bình của profile) và mật độ khối lượng trong hộp ≥ **2 lần** mật độ phần profile trong ± 3 up ngoài hộp |
| Không đổi | làm mượt ± 0,05 up; luật "vai"; hộp hẹp hơn 0,20 up thì bỏ | |

Vì sao các tiêu chí mới không phụ thuộc biên độ profile:
- "4,5 nến M30" là khối lượng tuyệt đối tính theo thời gian giao dịch, không chia cho cả profile.
- "Dày gấp 2 lần xung quanh" chỉ nhìn ± 3 up quanh hộp. Cụm đứng giữa vùng mỏng (ngày chạy một chiều, tuần sập) đạt dễ; bướu nằm giữa vùng dày không đạt.
- Đỉnh so với ± 3 up thay cho đỉnh lớn nhất cả profile ⇒ cụm ở xa vùng dày nhất không còn bị đè.
- Nhánh "≥ 12 % / 8 %" giữ lại nghĩa "lớn" của v1 cho các thân to nằm giữa vùng dày (ví dụ GC tuần 25 → 30/10: 15,5 % nhưng chỉ dày gấp 1,8 lần xung quanh). 10 % nâng lên 12 % vì hộp giờ rộng hơn (trung vị 0,45 so với 0,35 up).

### Chọn thông số (`python hvn_cum2.py scan nq|gc`)

Hộp mỗi profile ngày (và % phiên có 0 / 1 / 2 hộp). Cột cuối: ba ca kiểm còn ra không.

| Biến thể | NQ | GC | 20/11 ngày · tuần · 23/11 |
|---|---|---|---|
| v1 | 0,90 (31 / 48 / 21) | 0,79 (38 / 44 / 18) | sót · sót · có |
| **v2 chốt** | **0,96 (8 / 88 / 4)** | **0,89 (16 / 78 / 5)** | có · có · có |
| không nới hộp | 0,58 (42 / 58 / 0) | 0,47 (55 / 44 / 1) | sót · sót · có |
| bề rộng đích 0,40 | 0,94 | 0,85 | có (25.541,75 – 25.605,00) |
| bề rộng đích 0,50 | 0,96 | 0,90 | có (25.534,50 – 25.613,75; 23/11 thành 26.800,50 – 26.883,75) |
| 3,5 nến | 1,04 | 0,95 | có |
| 5 nến | 0,94 | 0,84 | có |
| 6 nến | 0,88 | 0,78 | **sót** 20/11 ngày |
| dày gấp 1,8 | 0,98 | 0,92 | có |
| dày gấp 2,5 | 0,94 | 0,82 | có |
| chỉ nhánh nổi bật | 0,92 (12 / 85 / 4) | 0,79 (26 / 68 / 5) | có |
| chỉ nhánh ≥ 12 % / 8 % | 0,88 | 0,78 | **sót** 20/11 ngày và tuần |
| vùng xung quanh ± 2 up | 1,06 (6 / 83 / 12) | 0,90 | có |
| vùng xung quanh ± 4 up | 0,94 (6 / 94 / 0) | 0,85 | có |
| đỉnh ≥ 50 % đỉnh trong ± 3 up (không bắt cao nhất) | 1,40 (4 / 52 / 44) | 1,33 (12 / 42 / 45) | có |
| sàn khi nới 60 % | 0,94 | 0,86 | **sót** 20/11 ngày |

- Ca 20/11 ngày qua bằng nhánh nổi bật (11,1 % < 12 %); nó chứa 5,1 nến so với ngưỡng 4,5 — **sát ngưỡng**. Theo khối lượng, cụm này thuộc nhóm 10 % nhỏ nhất trong các hộp v2; về độ nổi bật thì nó ở mức trung vị của các phiên NQ (dày gấp 2,8 lần xung quanh). Tức là: cụm nhỏ nhưng rõ như một cụm bình thường — đúng loại v1 bỏ sót.
- "Đỉnh ≥ 50 % trong ± 3 up" cho 1,3–1,4 hộp mỗi phiên, gần nửa số phiên có hai hộp sát nhau ⇒ chọn "phải cao nhất".
- Bề rộng đích 0,45: 0,40 cho hộp 20/11 hẹp hơn hộp người dùng 15 điểm; 0,50 kéo hộp 23/11 rộng thêm 11 điểm so với v1.

Kết quả với thông số chốt:

| | NQ phiên | GC phiên | NQ tuần | GC tuần |
|---|---|---|---|---|
| Biên độ profile ÷ up, p10 / 50 / 90 | 5,5 / 7,8 / 11,1 | 5,3 / 7,4 / 10,8 | 13,1 / 19,0 / 24,9 | 12,1 / 15,0 / 24,0 |
| Hộp mỗi profile: v1 → v2 | 0,90 → 0,96 | 0,79 → 0,89 | 0,45 → 1,82 | 0,47 → 1,47 |
| % profile có 0 / 1 / 2 / 3 / 4 hộp (v2) | 8 / 88 / 4 / 0 / 0 | 16 / 78 / 5 / 0 / 0 | 0 / 45 / 36 / 9 / 9 | 7 / 53 / 27 / 13 / 0 |
| Bề rộng (× up) p10 / 50 / 90: v1 | 0,23 / 0,35 / 0,58 | 0,26 / 0,37 / 0,49 | 0,42 / 0,43 / 0,56 | 0,44 / 0,52 / 1,14 |
| Bề rộng (× up) p10 / 50 / 90: v2 | 0,43 / 0,45 / 0,51 | 0,44 / 0,45 / 0,46 | 0,45 / 0,45 / 0,52 | 0,45 / 0,46 / 0,71 |
| Tỉ trọng p10 / 50 / 90 (v2) | 12 / 17 / 26 % | 12 / 16 / 21 % | 3 / 7 / 11 % | 3 / 8 / 11 % |
| Số nến M30 tương đương p10 / 50 / 90 (v2) | 5,7 / 7,8 / 11,8 | 5,4 / 7,2 / 9,7 | 7,3 / 15,6 / 21,5 | 7,5 / 17,8 / 23,7 |

Profile tuần vẫn chỉ có 11 và 15 mẫu — số hộp tuần tăng gấp 3–4 là hệ quả của luật, **không phải thứ đã được chỉnh theo dữ liệu**.

## 3. Ba ca

| | Hộp người dùng | v2 | Phần trùng |
|---|---|---|---|
| NQ phiên 20/11 | 25.530 – 25.608 (78 điểm) | 25.538,50 – 25.609,75 (71,25 điểm = 0,45 up; lõi 25.557,75 – 25.594,00; 11,1 % = 5,1 nến; dày gấp 2,8) | 69,5 điểm = 89 % hộp người dùng |
| NQ tuần 15 → 20/11 | như trên | 25.544,25 – 25.604,00 (59,75 điểm; 2,6 % = 6,1 nến; dày gấp 2,8) — hộp thứ hai của tuần, sau 27.239,25 – 27.299,00 (8,3 %) | nằm trọn trong hộp người dùng, phủ 77 % |
| NQ phiên 23/11 | 65 điểm | 26.801,50 – 26.876,50 (75 điểm; 29,4 %) | v1 là 26.802,50 – 26.874,75 |

Hộp tuần hẹp hơn hộp ngày vì up của cả tuần (133 điểm) nhỏ hơn up của riêng phiên 20/11 (158 điểm). Trên chart hai hộp trùng nhau nên chỉ vẽ một, nhãn `HVN ngày + tuần` (mục 5).

Ảnh — xanh = v2 (vạch xanh đậm sát trục = lõi 80 %), khung cam = v1, nét đứt = hộp người dùng:

| Ảnh | Nội dung |
|---|---|
| [v2_nq_2026-11-20_phien.png](hvn_cum/v2_nq_2026-11-20_phien.png) | ca báo sót, profile phiên 20/11 + phóng vào cụm |
| [v2_nq_tuan_2026-11-16.png](hvn_cum/v2_nq_tuan_2026-11-16.png) | ca báo sót, profile tuần 15 → 20/11; nửa giữa thấy tuần này mở cửa ngay trong hộp |
| [v2_nq_2026-11-23_phien.png](hvn_cum/v2_nq_2026-11-23_phien.png) | ca mẫu cũ, v1 và v2 gần trùng |
| [v2_luoi_nq_phien.png](hvn_cum/v2_luoi_nq_phien.png) · [v2_luoi_gc_phien.png](hvn_cum/v2_luoi_gc_phien.png) | 12 phiên gần nhất mỗi mã, trước/sau |
| [v2_luoi_nq_tuan.png](hvn_cum/v2_luoi_nq_tuan.png) · [v2_luoi_gc_tuan.png](hvn_cum/v2_luoi_gc_tuan.png) | 9 tuần gần nhất mỗi mã, trước/sau |
| [v2_nq_2026-11-10_phien.png](hvn_cum/v2_nq_2026-11-10_phien.png) · [v2_gc_2026-11-05_phien.png](hvn_cum/v2_gc_2026-11-05_phien.png) | phiên v1 có hai hộp, v2 còn một |
| [v2_gc_2026-10-28_phien.png](hvn_cum/v2_gc_2026-10-28_phien.png) · [v2_nq_2026-11-17_phien.png](hvn_cum/v2_nq_2026-11-17_phien.png) | hộp chuyển lên đỉnh cao nhất; hộp nới rộng |

## 4. Hộp v1 bị đổi thế nào

| | NQ (52 phiên) | GC (73 phiên) |
|---|---|---|
| Phiên v1 có hộp | 36 | 45 |
| … v2 không còn hộp nào | 1 | 4 |
| … v2 có hộp nhưng ở chỗ khác hẳn | 6 | 9 |
| Phiên v1 không có hộp, v2 có | 13 | 20 |
| Hộp v1 còn giao với một hộp v2 | 30 / 47 (64 %) | 32 / 58 (55 %) |
| Hộp v1 mất vì nhường cho đỉnh cao hơn trong ± 3 up | 14 | 22 |

Chỗ v2 còn vụng (thấy trên ảnh lưới):
- **Đỉnh nhọn được nới thành hộp:** NQ 11-09 (27.905 – 27.964), NQ 11-11 (28.345 – 28.378), GC 10-22 (4103,5 – 4108,8). Lõi rất hẹp, hộp phần lớn là sườn. Người dùng gọi cụm 20/11 (lõi 0,23 up) là "đều", nên luật nới là cần; nhưng nó cũng nhận các đỉnh nhọn hơn thế.
- **Thân rộng nhiều răng cưa:** NQ 11-10 (thân 27.700 – 28.030). v1 cho hai hộp ở hai bướu phụ, v2 cho một hộp ở răng cao nhất (27.707,50 – 27.753,75). Không bản nào ôm cả thân. Chưa biết người dùng sẽ vẽ gì ở phiên này.
- **Hộp thứ hai gần như biến mất** (4–5 % số phiên). v1 cho phép hai hộp sát nhau cách một đáy; v2 chỉ cho khi cách nhau hơn 3 up.

## 5. Bán kính hiển thị hộp HVN (`python hvn_cum2_bk.py nq|gc`)

Cuối dữ liệu (nến 2026-11-24 12:00 UTC đóng 26.398,75; U = 143,47 điểm): mép trên hộp 25.609,75 cách giá **789 điểm = 5,5 U**; tính từ tâm cụm 25.570 là 829 điểm = 5,8 U. Bán kính hiện tại 4 U = 574 điểm ⇒ hộp không được vẽ dù có phát hiện.

Khoảng cách từ giá tới mép hộp HVN đủ điều kiện (mọi nến, v2): trung vị 5,3 U (NQ) và 4,3 U (GC). Chỉ 39 % (NQ) và 47 % (GC) số hộp nằm trong 4 U.

Số hộp HVN được vẽ mỗi nến M30 (v2):

| Bán kính | NQ: trung bình · % nến có ≥ 4 hộp · nhiều nhất | GC: trung bình · % nến có ≥ 4 hộp · nhiều nhất |
|---|---|---|
| 4 U (hiện tại) | 1,97 · 14 % · 5 | 2,16 · 21 % · 7 |
| 6 U | 2,70 · 35 % · 6 | 2,81 · 35 % · 7 |
| 8 U | 3,19 · 48 % · 6 | 3,30 · 47 % · 8 |
| 10 U | 3,62 · 61 % · 7 | 3,65 · 56 % · 8 |
| **8 U + tối đa 2 hộp gần nhất mỗi phía** | **2,39 · 19 % · 5** | **2,41 · 20 % · 5** |
| 6 U + tối đa 2 mỗi phía | 2,19 · 14 % · 5 | 2,20 · 17 % · 5 |
| 10 U + tối đa 2 mỗi phía | 2,52 · 20 % · 5 | 2,56 · 22 % · 5 |
| 8 U + tối đa 1 mỗi phía | 1,48 · 0 % · 3 | 1,54 · 0 % · 4 |

(v1 với 4 U: NQ 1,75, GC 1,94 hộp mỗi nến.)

**Đề xuất:** hộp HVN dùng bán kính riêng **8 U**, mỗi phía giá tối đa **2 hộp gần nhất** (hộp đang chứa giá vẽ thêm). So với bản đang chạy (v1, 4 U) số hộp trên chart tăng 24–37 %, không bao giờ quá 5. Không tách bán kính riêng cho hộp tuần: 6 U thì ca người dùng (5,5–5,8 U) nằm sát mép; trần "2 mỗi phía" đã lo phần rối. Vùng mạnh giữ 4 U.

Ca người dùng với luật này (nến 11:30, giá 26.442,75): vẽ `25.538,50 – 25.609,75 · HVN ngày + tuần` ở dưới, `26.801,50 – 26.876,50` và `26.946,25 – 27.002,00` ở trên. Quanh 25.540 – 25.610 hiện không có cụm va đập nào (cụm gần nhất 25.897,50 – 25.952,25) nên ở đó **chỉ có hộp HVN, không có vùng mạnh**.

Thêm nhãn gộp: hộp ngày và hộp tuần trùng nhau hơn 50 % thì vẽ một hộp, nhãn `HVN ngày + tuần` (trước chỉ ghi `HVN ngày`).

## 6. "Đáy volume profile tuần này"

Số thật: phiên thứ Sáu 20/11 đóng 25.291,00. Nến đầu tuần (2026-11-22 23:00 UTC) mở 25.561,50 — bên trong hộp 25.538,50 – 25.609,75 — xuống 25.426,75 (thủng mép dưới 111,75 điểm = 0,78 U), đóng 25.700,25. Đáy tuần này vì thế nằm ngay dưới cụm, và phần đáy của profile tuần này (25.427 – 25.770) phủ lên cụm.

Đánh giá:
- Trong bộ máy hiện tại "hợp lưu" là một **mức** trùng với một **cụm va đập** (≥ 3 lần bật) trong ± 0,10 U. Đáy tuần cách mép hộp 0,78 U, và quanh đó không có cụm va đập. Thêm "đáy tuần" vào danh sách mức sẽ **không** làm ca này hiện ra.
- Thứ người dùng thấy là **giá quay lại hộp HVN và phản ứng** — đúng cách dùng HVN đã nêu ở mục 10. Việc cần là vẽ được hộp (mục 5), không phải thêm một mức.
- Đáy/đỉnh tuần bản thân nó là một điểm va đập của chính chuỗi giá dùng để dựng cụm va đập, nên không độc lập như VWAP hay VAL.

Vẫn đo thử (mở rộng so với yêu cầu gốc; `python hvn_cum2_bien.py gc|nq`): thêm bốn mức — đáy và đỉnh tuần trước, đáy và đỉnh tuần này tới hết hôm qua — thành hai nhóm mới.

| | GC | NQ |
|---|---|---|
| % cụm va đập có hợp lưu: trước → sau | 63 → 65 | 54 → 59 |
| Vùng vẽ trung bình: trước → sau | 2,18 → 2,27 | 1,41 → 1,49 |
| % thời gian có vàng: trước → sau | 23,0 → 26,6 | 14,9 → 14,9 |
| Lần quay lại cụm trùng đáy/đỉnh tuần | 48 (38 lệnh), thắng 1:1 52,6 %, khoảng [−10,9; +19,1] | 27 (20 lệnh), thắng 35,0 % — n nhỏ |
| Đối chứng | 48,8 % | 46,5 % |

Hai mã trái chiều, mẫu 38 và 20 lệnh. **Không đề xuất thêm.** Nếu người dùng vẫn muốn, dạng nên là "đáy / đỉnh tuần trước" và "đáy / đỉnh tuần này tới hết hôm qua" (đã có code thử trong `vung_manh.py`, khoá `WK_EXT`), không phải VAL tuần này: VAL của tuần đang chạy đổi mỗi ngày và trùng một phần với VAL hôm qua.

## 7. Ảnh hưởng tới vùng mạnh (`python hvn_cum2_do.py gc|nq`)

Cách chấm và đối chứng y như HVN-CUM.md mục 4; dòng v1 chạy lại ra đúng số cũ.

### Mật độ

| | GC v1 | GC v2 | NQ v1 | NQ v2 |
|---|---|---|---|---|
| HVN đưa vào xét mỗi phiên | 4,8 | 6,5 | 5,6 | 7,3 |
| Bề rộng hộp đủ điều kiện (× U) p10 / 50 / 90 | 0,26 / 0,38 / 0,62 | 0,39 / 0,45 / 0,55 | 0,22 / 0,38 / 0,64 | 0,36 / 0,45 / 0,59 |
| % dải ± 4 U quanh giá nằm trong hộp HVN | 14 | 18 | 12 | 15 |
| % cụm va đập có hợp lưu | 58 | 63 | 52 | 54 |
| % cụm va đập có HVN | 36 | 40 | 29 | 31 |
| Vùng vẽ trung bình | 1,99 | 2,18 | 1,30 | 1,41 |
| % thời gian có vùng | 72 | 74 | 58 | 60 |
| % thời gian có vùng dính HVN | 60 | 61 | 36 | 44 |
| **% thời gian có vàng** | 15,1 | **23,0** | 19,0 | **14,9** |
| % thời gian có vàng nếu HVN ngày + HVN tuần tính một nhóm | — | 10,5 | — | 6,8 |

Vàng trên GC tăng vì profile tuần giờ có nhiều hộp hơn, và một cụm thường được đếm hai lần: một lần là HVN ngày, một lần là HVN tuần — hai nhóm cho cùng một khối lượng. Coi hai loại HVN là một nhóm khi đếm "≥ 3 nhóm" đưa vàng về 7–10 %, gần mức 6–7 % của luật gốc. Đây là đổi luật vàng nên chỉ ghi lại để người dùng chốt.

### Hiệu quả so với đối chứng (thắng 1:1, R 1:2; ngoặc vuông = khoảng 5–95 % của hiệu)

**GC — đối chứng 1.817 lần, thắng 48,8 %, R 1:2 −0,063**

| Bản | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|
| v1 | vùng được vẽ | 378 | 49,4 % (324 lệnh) | [−5,2; +6,4] | +0,025 | [−0,07; +0,26] |
| v1 | cụm có HVN | 265 | 52,3 % (220 lệnh) | [−2,7; +9,9] | +0,076 | [−0,06; +0,34] |
| v1 | vàng | 25 | 22,2 % (18 lệnh) | n nhỏ | −0,500 | n nhỏ |
| **v2** | vùng được vẽ | 409 | 49,7 % (352 lệnh) | [−5,2; +6,4] | +0,050 | [−0,05; +0,27] |
| | cụm có HVN | 276 | 51,1 % (233 lệnh) | [−4,7; +7,8] | +0,125 | [+0,00; +0,36] |
| | cụm không có HVN | 411 | 46,0 % (350 lệnh) | [−8,6; +2,9] | −0,090 | [−0,18; +0,13] |
| | hợp lưu ≥ 2 nhóm | 181 | 50,6 % (158 lệnh) | [−6,5; +9,0] | +0,099 | [−0,09; +0,39] |
| | vàng | 43 | 44,4 % (36 lệnh) | [−22,6; +13,1] | +0,000 | [−0,44; +0,56] |

**NQ — đối chứng 979 lần, thắng 46,5 %, R 1:2 −0,011**

| Bản | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|
| v1 | vùng được vẽ | 170 | 49,6 % (137 lệnh) | [−4,3; +11,3] | +0,228 | [−0,00; +0,46] |
| v1 | cụm có HVN | 108 | 45,6 % (90 lệnh) | [−9,3; +8,1] | +0,100 | [−0,14; +0,36] |
| v1 | vàng | 30 | 48,1 % (27 lệnh) | n nhỏ | +0,333 | n nhỏ |
| **v2** | vùng được vẽ | 191 | 50,0 % (156 lệnh) | [−3,8; +10,6] | +0,251 | [+0,03; +0,48] |
| | cụm có HVN | 114 | 43,3 % (97 lệnh) | [−12,1; +6,8] | +0,021 | [−0,22; +0,29] |
| | cụm không có HVN | 226 | 49,2 % (187 lệnh) | [−4,6; +12,0] | +0,087 | [−0,09; +0,33] |
| | hợp lưu ≥ 2 nhóm | 97 | 46,9 % (81 lệnh) | [−7,4; +9,2] | +0,185 | [−0,07; +0,47] |
| | vàng | 16 | 42,9 % (14 lệnh) | n nhỏ | +0,071 | n nhỏ |

Đọc bảng:
- **Tỉ lệ thắng của vùng được vẽ không khác đối chứng** ở cả hai mã, cả hai bản.
- NQ, R 1:2 của vùng được vẽ: khoảng của v2 là [+0,03; +0,48], của v1 là [−0,00; +0,46]. Đây vẫn là dấu hiệu sát 0 đã thấy từ hai lần đo trước, trên 156 lệnh, không tách TRAIN/TEST, và là một trong hàng chục ô đã nhìn. **Không coi là đã kiểm định.** Nó cũng không đến từ HVN: cụm có HVN trên NQ thắng 43,3 %, R +0,021.
- Cụm có HVN: GC 51,1 %, NQ 43,3 % — trái chiều như v1, mọi khoảng của tỉ lệ thắng chứa 0.
- Vàng: GC 36 lệnh thắng 44,4 %, NQ 14 lệnh. Không kết luận.
- **v2 không làm vùng mạnh tốt lên hay xấu đi một cách đo được.** Lý do để đổi là hộp khớp thứ người dùng nhìn thấy, không phải hiệu quả.

## 8. Cần người dùng chốt

1. Xem bốn ảnh lưới: hộp v2 (xanh) có đúng thứ muốn thấy hơn hộp v1 (khung cam) không — nhất là các phiên đỉnh nhọn được nới (mục 4).
2. Vàng trên GC lên 23 % thời gian. Giữ luật, hay tính HVN ngày + HVN tuần là một nhóm (GC 10,5 %, NQ 6,8 %)?
3. Hộp HVN: bán kính 8 U, tối đa 2 hộp mỗi phía.
4. Đáy/đỉnh tuần: không thêm (mục 6).

## 9. Giới hạn

- Thông số chỉnh theo **hai** hộp người dùng mô tả bằng số (20/11 và 23/11). Ca 20/11 ngày qua sát ngưỡng 4,5 nến (5,1).
- Tôi không xem được màn hình người dùng: 25.530–25.608 được hiểu là giá NQZ26 theo chẩn đoán của agent chính.
- 52 phiên NQ, 73 phiên GC, 11–15 tuần; không TRAIN/TEST; GC trùng dữ liệu với các lần đo trước. Luật cho profile tuần chưa được chỉnh riêng.
- Như cũ: chưa phí, chưa trượt giá, chưa xét order flow tại vùng. Chưa đo hộp HVN đứng riêng (không cần cụm va đập) có giữ giá hay không — đây vẫn là phép đo sát cách dùng nhất và chưa làm.

## 10. File

| File | Việc |
|---|---|
| `hvn_cum2.py` | bản tham chiếu v2 `clusters()`; `ca nq 2026-11-20`; `scan nq|gc` |
| `hvn_cum2_ve.py` | PNG trước/sau vào `hvn_cum/v2_*.png` |
| `hvn_cum2_bk.py` | bán kính hiển thị + trạng thái cuối dữ liệu NQ |
| `hvn_cum2_do.py` | mật độ + hiệu quả v1 so với v2 |
| `hvn_cum2_bien.py` | thử đáy/đỉnh tuần làm mức hợp lưu |
| `hvn_cum2_fixture.py` | sinh `fixture/hvn_cum2_cases.json` (19 profile), `fixture/expected_cum2.json` (689 ca GC), `fixture/nq_expected2.json` (13 ca NQ, bộ chặn chỗ nối tắt) |
| `vung_manh.py` | **đã sửa**: `HVN_MODE='cum2'` (mặc định vẫn `'cum'` để các script v1 chạy lại ra số cũ), hàm `hvn_boxes()`, `HVN_RADIUS`, `HVN_MAX_SIDE`; khoá thử nghiệm `WK_EXT`, `HVN_ONE_GROUP` (mặc định tắt) |

Chạy lại: `python prep1.py gc` → `python prep1.py nq` → `python hvn_cum2.py scan nq` → `python hvn_cum2.py ca nq 2026-11-20` → `python hvn_cum2_ve.py` → `python hvn_cum2_bk.py nq` → `python hvn_cum2_do.py gc lai` → `python hvn_cum2_do.py nq lai` → `python hvn_cum2_bien.py gc` → `python hvn_cum2_fixture.py`. File fixture v1 không bị đụng tới.
