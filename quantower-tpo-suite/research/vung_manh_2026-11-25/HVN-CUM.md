# HVN dạng cụm — định nghĩa, hiệu chỉnh theo hình người dùng vẽ, ảnh hưởng tới vùng mạnh (Fable, 2026-11-25)

Spec cho Opus: [`../../PLAN-VUNG-MANH.md`](../../PLAN-VUNG-MANH.md) mục 10–12. Bản tham chiếu: [`hvn_cum.py`](hvn_cum.py).
Dữ liệu: một hợp đồng, GCZ26 (74 phiên, 2026-07-28 → 11-09) và NQZ26 (52 phiên, 2026-09-13 → 11-24), như [`DO-LAI-GC-NQ-1-HOP-DONG.md`](DO-LAI-GC-NQ-1-HOP-DONG.md).

## 0. Kết luận trước

1. **HVN cũ không phải thứ người dùng vẽ.** HVN cũ là từng đỉnh nhọn (nền 90 % của một hàng): trung vị rộng 0,06 × biên độ M30 trên NQ (khoảng 5 điểm), 2,1 cái mỗi phiên. Hộp người dùng vẽ rộng 65 điểm — gấp 13 lần — và mỗi profile chỉ có một.
2. **Định nghĩa mới (HVN dạng cụm)** = cả thân khối lượng quanh đỉnh: mọi mức giá trong thân có khối lượng (đã làm mượt) ≥ 80 % đỉnh của thân, thân rộng ≥ 0,20 × biên độ M30, chứa ≥ 10 % khối lượng cả profile (profile tuần: ≥ 8 %), tối đa 2 thân mỗi profile.
3. **Khớp hình người dùng (NQ phiên 23/11):** hộp mới 26.802,50 – 26.874,75, rộng **72,25 điểm** so với 65 điểm vẽ tay (rộng hơn 11 %), một cụm duy nhất, chứa 28,5 % khối lượng phiên. Dịch hộp vẽ tay theo basis 51 điểm (căn tâm) thì hai hộp trùng nhau 90 %. Phần chưa chắc: vị trí POC (mục 3).
4. **Số lượng:** NQ 0,90 cụm/phiên (31 % phiên không có, 48 % có một, 21 % có hai); GC 0,79 (38 / 44 / 18). Tính theo biên độ M30 nên NQ và GC cùng hành vi: bề rộng trung vị 0,35 và 0,37.
5. **Ảnh hưởng tới vùng mạnh:** số cụm va đập có hợp lưu HVN tăng gấp đôi (GC 18 → 36 %, NQ 16 → 29 %); **thời gian có vùng vàng tăng 2–3 lần** (GC 6,9 → 15,1 %, NQ 6,0 → 19,0 %); số vùng được vẽ gần như không đổi (GC 1,78 → 1,99; NQ 1,22 → 1,30).
6. **Hiệu quả so với đối chứng: không đổi kết luận.** GC vùng được vẽ thắng 1:1 49,4 % so với đối chứng 48,8 %; NQ 49,6 % so với 46,5 %; mọi khoảng 5–95 % chứa 0 (riêng R 1:2 của NQ chạm 0 như lần trước). **Vẫn là "chưa kiểm định".**
7. **"Chỉ tính hợp lưu ở mép hộp"** gần như không khác "giao hộp" (hộp HVN và vùng va đập cùng cỡ 0,36–0,38 U nên đã giao là gần như luôn chạm mép). Chọn luật đơn giản: giao hộp.
8. **Phải bỏ điều kiện "profile hình chữ D" cũ:** chính phiên 23/11 người dùng lấy làm mẫu bị nó loại (POC nằm ở 81 % chiều cao profile vì có đuôi dưới dài 1.300 điểm). Tiêu chí "lớn và đều" giờ nằm trong bản thân cụm.

## 1. Vì sao HVN cũ nhiều, loạn, mỏng

| | NQ phiên | GC phiên |
|---|---|---|
| HVN cũ mỗi profile (đạt tỉ lệ ≥ 2,5) | 2,12 (94 % phiên có) | 0,96 (66 % phiên có) |
| Bề rộng HVN cũ (× biên độ M30) p10 / 50 / 90 | 0,02 / 0,06 / 0,20 | 0,03 / 0,17 / 0,42 |
| HVN đưa vào xét hợp lưu mỗi phiên (5 phiên + 2 tuần) | 14,4 | 6,8 |

- **Mỏng:** dải = nới từ hàng đỉnh tới khi khối lượng THÔ của hàng kế < 90 % đỉnh. Khối lượng thô răng cưa nên dừng sau 1–3 hàng.
- **Nhiều:** mỗi đỉnh cục bộ cao ≥ 2,5 lần trung bình hàng là một HVN; một thân phẳng có 3 răng cưa thành 3 HVN. Phiên NQ 23/11: ba dải 26.818–26.823, 26.852–26.855, 26.884–26.889 — cả ba nằm trong cùng một thân.
- **NQ loạn hơn GC:** ngưỡng tách đỉnh tính theo số hàng (hàng = 2 bước giá = 0,007 U trên NQ, 0,017 U trên GC), không theo biên độ.

## 2. Định nghĩa mới

Đơn vị: **up = biên độ (High − Low) trung bình của chính các nến M30 trong profile**. Không phụ thuộc phiên khác, cố định sau khi profile đóng, dùng được cho cả profile ngày lẫn tuần.

1. Dựng khối lượng theo **từng bước giá** từ thấp nhất tới cao nhất của profile (không gộp hàng).
2. Làm mượt: S[i] = tổng khối lượng trong cửa sổ ± h bước giá, h = 0,05 × up (NQ 23/11: ± 33 bước giá = ± 8,25 điểm; GC: ± 5–8 bước giá).
3. Lấy đỉnh cao nhất của S, nới hai phía khi S ≥ **80 %** đỉnh → đó là thân. Làm tiếp với chỗ cao nhất còn lại; khối nào dính liền thân trước mà không có đáy tách (đáy < 80 % đỉnh của nó) thì là vai, bỏ. Dừng khi đỉnh còn lại < 50 % đỉnh lớn nhất.
4. Giữ thân có khối lượng ≥ **10 %** cả profile (tuần: 8 %) và rộng ≥ **0,20 × up**. Tối đa 2 thân.

Ba tiêu chí của người dùng thành số:

| Yêu cầu | Số |
|---|---|
| **Đều** (thân, không phải đỉnh nhọn) | mọi mức giá trong hộp có khối lượng mượt ≥ 80 % đỉnh của hộp (chênh tối đa 20 %); hộp rộng ≥ 0,20 × biên độ M30 |
| **Đủ lớn** | hộp chứa ≥ 10 % khối lượng profile ngày (≥ 8 % profile tuần) |
| **Ít** | tối đa 2 hộp mỗi profile; hộp thứ hai phải cao ≥ 50 % hộp chính và tách bằng một đáy thật |

### Chọn thông số (`python hvn_cum.py scan nq|gc`, bảng đầy đủ ở lệnh này)

Bề rộng cụm chính phiên NQ 23/11 (điểm) — đích là 65:

| nửa cửa sổ làm mượt ↓ / ngưỡng thân → | 60 % | 70 % | 75 % | **80 %** | 85 % |
|---|---|---|---|---|---|
| 0,02 × up | 102 | 71 | 64 | 60 | 20 |
| 0,03 × up | 105 | 91 | 68 | 64 | 57 |
| **0,05 × up** | 108 | 93 | 86 | **72** | 58 |
| 0,08 × up | 113 | 93 | 86 | 77 | 64 |
| 0,12 × up | 116 | 96 | 86 | 77 | 68 |

- Ngưỡng 80 % cho 60–77 điểm ở mọi mức làm mượt — ổn định. Ngưỡng 70–75 % nhảy giữa 64 và 93 vì mép trên của thân có một bậc ở 26.872–26.888 (cao 69–76 % đỉnh). Ngưỡng 85 % với cửa sổ hẹp vỡ thành răng cưa (20 điểm).
- Làm mượt 0,05: hẹp hơn (0,02–0,03) thì 34–52 % phiên GC không còn cụm nào vì răng cưa cắt thân.

Số cụm mỗi profile ngày với ngưỡng 80 %, làm mượt 0,05, theo tỉ trọng tối thiểu:

| Tỉ trọng tối thiểu | NQ: cụm/phiên · % phiên có 0 / 1 / 2 | GC: cụm/phiên · % phiên có 0 / 1 / 2 |
|---|---|---|
| 5 % | 1,46 · 6 / 42 / 52 | 1,67 · 7 / 19 / 74 |
| 8 % | 1,21 · 13 / 52 / 35 | 1,11 · 23 / 42 / 34 |
| **10 %** | **0,90 · 31 / 48 / 21** | **0,79 · 38 / 44 / 18** |
| 12 % | 0,60 · 46 / 48 / 6 | 0,49 · 58 / 36 / 7 |
| 15 % | 0,40 · 62 / 37 / 2 | 0,19 · 81 / 19 / 0 |

Chọn 10 %: "thường một, tối đa hai". Khoảng một phần ba số phiên không có HVN — đó là các phiên xu hướng hoặc nhiều tầng, không có thân nào đủ lớn và đều (ví dụ NQ 11-13, GC 11-03 trong ảnh lưới).

Profile tuần (chỉ 11 tuần NQ, 15 tuần GC — **không đủ để chỉnh**): với 10 % thì 80 % số tuần không có cụm; với 8 % thì khoảng một nửa số tuần có đúng một cụm (NQ 45 %, GC 47 %), không tuần nào có hai. Đặt 8 % cho tuần, ghi là chọn theo mật độ.

Kết quả với thông số chốt:

| | NQ phiên | GC phiên | NQ tuần | GC tuần |
|---|---|---|---|---|
| Cụm mỗi profile | 0,90 | 0,79 | 0,45 | 0,47 |
| Bề rộng (× up) p10 / 50 / 90 | 0,23 / 0,35 / 0,58 | 0,26 / 0,37 / 0,49 | 0,42 / 0,43 / 0,56 | 0,44 / 0,52 / 1,14 |
| Tỉ trọng khối lượng p10 / 50 / 90 | 10 / 15 / 25 % | 11 / 13 / 16 % | 8 / 9 / 21 % | 8 / 9 / 18 % |
| Bề rộng cụm ÷ bề rộng vùng giá trị 70 % (trung vị) | 0,13 | 0,12 | 0,14 | 0,14 |

So với vùng giá trị 70 %: cụm chỉ bằng khoảng một phần tám bề rộng VA và chứa 10–30 % khối lượng — VA là "70 % khối lượng nằm đâu", cụm là "chỗ dày và phẳng nhất". Hai thứ khác nhau, không thay nhau được.

## 3. Khớp hình người dùng — NQZ26 phiên 2026-11-23 (`python hvn_cum.py ca nq 2026-11-23`)

Tôi không xem được ảnh chụp; số của hộp vẽ tay (26.755 → 26.820, POC khoảng 26.790 trên OANDA:NAS100USD) lấy theo mô tả của agent chính.

Phiên CME 2026-11-22 23:00 → 11-23 21:30 UTC, 46 nến M30, up = 166,4 điểm, thấp–cao 25.427 – 27.137, vùng giá trị 26.520 – 26.949.

| | Hộp vẽ tay (NAS100USD) | HVN dạng cụm (NQZ26) | HVN cũ (NQZ26) |
|---|---|---|---|
| Số hộp | 1 | **1** | 3 |
| Biên | 26.755 – 26.820 | **26.802,50 – 26.874,75** | 26.818–26.823 · 26.852–26.855 · 26.884–26.889 |
| Bề rộng | 65 điểm | **72,25 điểm** (0,43 × up) | 5 · 3 · 5 điểm |
| Tỉ trọng khối lượng phiên | — | 28,5 % | — |

- **Bề rộng: lệch +11 %.** Số hộp: khớp.
- **Basis** (NQ − NAS100USD) không đo trực tiếp được. Căn mép dưới ra 47,5; căn mép trên 54,75; căn tâm 51. Với basis 51, hộp vẽ tay nằm ở 26.806 – 26.871 trên NQ, **nằm trọn trong hộp mới, phần trùng 90 %**. Ước theo lý thuyết (25 ngày tới đáo hạn, lãi suất trừ cổ tức khoảng 3,3 %/năm) ra cỡ 60 điểm — cùng cỡ.
- **POC chưa khớp, và không kết luận được.** Căn theo POC (26.790 vẽ tay so với 26.810–26.818 trên NQ) thì basis chỉ 20–28, khi đó phần trùng còn 50 %. Lý do không tin cách căn này: thân phẳng (mọi mức trong hộp ≥ 80 % đỉnh) nên POC trượt dễ dàng trong cả hộp; và profile của CFD dựng từ khối lượng tick của OANDA, không phải khối lượng CME. Cần người dùng nhìn [ảnh cận cảnh](hvn_cum/nq_2026-11-23_phien_can_canh.png) để xác nhận.
- Mép trên của thân: khối lượng tụt mạnh ở 26.895–26.900 (từ 13.120 xuống 9.485 rồi 5.364 hợp đồng mỗi 5 điểm). Hộp mới dừng ở 26.874,75, trước bậc thềm 26.875–26.895 (cao 61–76 % đỉnh). Nếu người dùng muốn hộp ôm cả bậc thềm này thì hạ ngưỡng xuống 60–70 % (hộp 93–108 điểm) — khi đó lệch xa con số 65.
- Sau đó: phiên 11-24 (27 nến có trong file) đi qua lại hộp nhiều lần, đúng như người dùng mô tả — xem nửa phải [ảnh toàn phiên](hvn_cum/nq_2026-11-23_phien.png).

Ca GC để so: phiên 2026-10-29, HVN cũ 4038,0 – 4039,2 (1,2 giá) → HVN dạng cụm **4034,5 – 4040,6** (6,1 giá, 30,7 % khối lượng phiên) — [ảnh](hvn_cum/gc_2026-10-29_phien.png).

### Ảnh (`python hvn_cum_ve.py`)

Xám = khối lượng; đường đen = khối lượng làm mượt; **hộp xanh = HVN dạng cụm**; vạch cam = HVN cũ; nét đứt = hộp vẽ tay đã dịch basis 48; chấm chấm = VAH/VAL. Nửa phải = nến M30 của kỳ nguồn và 2 phiên sau.

| Ảnh | Nội dung |
|---|---|
| [nq_2026-11-23_phien_can_canh.png](hvn_cum/nq_2026-11-23_phien_can_canh.png) | ca người dùng vẽ, phóng vào thân, có hộp vẽ tay |
| [nq_2026-11-23_phien.png](hvn_cum/nq_2026-11-23_phien.png) | cả phiên 23/11 + giá quay lại ngày 24/11 |
| [luoi_nq_phien.png](hvn_cum/luoi_nq_phien.png) · [luoi_gc_phien.png](hvn_cum/luoi_gc_phien.png) | 12 phiên gần nhất mỗi mã, mới so với cũ |
| [luoi_nq_tuan.png](hvn_cum/luoi_nq_tuan.png) · [luoi_gc_tuan.png](hvn_cum/luoi_gc_tuan.png) | 9 tuần gần nhất mỗi mã |
| [nq_2026-11-18_phien.png](hvn_cum/nq_2026-11-18_phien.png) | một thân rõ (63 điểm, 28 %) |
| [nq_2026-11-13_phien.png](hvn_cum/nq_2026-11-13_phien.png) · [nq_tuan_2026-11-16.png](hvn_cum/nq_tuan_2026-11-16.png) | không có cụm (HVN cũ vẫn ra 3 dải) |
| [nq_2026-10-27_phien.png](hvn_cum/nq_2026-10-27_phien.png) | cụm sát ngưỡng 10 % |
| [gc_2026-10-29_phien.png](hvn_cum/gc_2026-10-29_phien.png) · [gc_2026-10-21_phien.png](hvn_cum/gc_2026-10-21_phien.png) · [gc_2026-11-03_phien.png](hvn_cum/gc_2026-11-03_phien.png) · [gc_tuan_2026-10-26.png](hvn_cum/gc_tuan_2026-10-26.png) | GC |

Chỗ định nghĩa mới còn vụng (thấy trên ảnh lưới):
- **GC 10-28:** đỉnh cao nhất (4060) quá nhọn nên bị loại, thuật toán lấy thềm 4051,3–4055,0 bên dưới (13 %). Đúng luật "đều", nhưng mắt người có thể không gọi đó là HVN của phiên.
- **NQ 11-17:** cụm 34 điểm (0,27 × up) quanh một đỉnh khá nhọn vẫn qua ngưỡng bề rộng 0,20.
- **NQ 11-10, GC 11-05, GC 10-23:** hai cụm mỗi phiên, mỗi cụm 13–20 %.

## 4. Ảnh hưởng tới vùng mạnh (`python hvn_cum_do.py gc|nq`)

Cách chấm và đối chứng y như lần trước. Dòng đầu chạy lại định nghĩa cũ và ra đúng số cũ (GC 314 lần, 49,3 %; NQ 165 lần, 50,7 %). NQ: tắt phát hiện chỗ nối.

Thay đổi kèm theo trong mọi dòng "cụm": điều kiện "đã rời xa ≥ 2 U" đo từ **mép hộp** (trước đo từ đỉnh).

### Mật độ

**GC**

| Định nghĩa HVN | HVN xét / phiên | đủ điều kiện | bề rộng hộp (× U) p10 / 50 / 90 | % dải ± 4 U quanh giá nằm trong hộp HVN | % cụm va đập có hợp lưu | % cụm có HVN | vùng vẽ TB | % thời gian có vùng | % thời gian có vùng dính HVN | % thời gian có vàng |
|---|---|---|---|---|---|---|---|---|---|---|
| cũ: đỉnh nhọn, chỉ chữ D | 6,8 | 2,8 | 0,02 / 0,24 / 0,50 | 6 | 48 | 18 | 1,78 | 71 | 38 | 6,9 |
| **cụm · giao hộp** | 4,8 | 4,6 | 0,26 / 0,38 / 0,62 | 14 | 58 | 36 | 1,99 | 72 | 60 | **15,1** |
| cụm · chỉ mép hộp | 4,8 | 4,6 | như trên | 14 | 58 | 36 | 1,99 | 72 | 60 | 12,7 |
| cụm · giao hộp · chỉ chữ D | 4,8 | 2,7 | 0,24 / 0,39 / 0,59 | 8 | 52 | 24 | 1,86 | 72 | 47 | 7,7 |
| cụm · chỉ mép hộp · chỉ chữ D | 4,8 | 2,7 | như trên | 8 | 51 | 23 | 1,85 | 72 | 47 | 5,7 |

**NQ**

| Định nghĩa HVN | HVN xét / phiên | đủ điều kiện | bề rộng hộp (× U) p10 / 50 / 90 | % dải ± 4 U quanh giá nằm trong hộp HVN | % cụm va đập có hợp lưu | % cụm có HVN | vùng vẽ TB | % thời gian có vùng | % thời gian có vùng dính HVN | % thời gian có vàng |
|---|---|---|---|---|---|---|---|---|---|---|
| cũ: đỉnh nhọn, chỉ chữ D | 14,4 | 6,0 | 0,02 / 0,06 / 0,28 | 6 | 45 | 16 | 1,22 | 57 | 21 | 6,0 |
| **cụm · giao hộp** | 5,6 | 5,3 | 0,22 / 0,38 / 0,64 | 12 | 52 | 29 | 1,30 | 58 | 36 | **19,0** |
| cụm · chỉ mép hộp | 5,6 | 5,3 | như trên | 12 | 51 | 28 | 1,28 | 58 | 36 | 19,0 |
| cụm · giao hộp · chỉ chữ D | 5,6 | 3,1 | 0,25 / 0,43 / 0,64 | 8 | 45 | 18 | 1,21 | 57 | 28 | 8,2 |
| cụm · chỉ mép hộp · chỉ chữ D | 5,6 | 3,1 | như trên | 8 | 44 | 17 | 1,20 | 57 | 24 | 8,2 |

- Số HVN đưa vào xét **giảm** (NQ 14,4 → 5,6), nhưng mỗi hộp rộng hơn nên phần giá quanh thị trường bị HVN phủ tăng gấp đôi (6 → 12–14 %).
- Số vùng trên chart gần như không đổi; cái đổi là **nhãn và màu**: nhiều vùng có thêm chữ "HVN", và vùng vàng xuất hiện 15–19 % thời gian thay vì 6–7 %.
- Phần tăng của vùng vàng đến từ hai thứ cộng lại: hộp rộng hơn, và bỏ lọc chữ D. Giữ lọc chữ D thì vàng về 6–8 % — nhưng lọc đó loại chính phiên mẫu của người dùng.

### Hiệu quả so với đối chứng

Thắng 1:1 và R 1:2; ngoặc vuông = khoảng 5–95 % của hiệu so với đối chứng.

**GC — đối chứng 1.817 lần, thắng 48,8 %, R 1:2 −0,063**

| Định nghĩa HVN | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|
| cũ | vùng được vẽ | 314 | 49,3 % | [−6,8; +7,2] | −0,018 | [−0,15; +0,25] |
| cũ | cụm có HVN | 104 | 51,2 % | [−9,2; +13,2] | +0,078 | [−0,24; +0,47] |
| cũ | vàng | 8 | 33 % (6 lệnh) | n nhỏ | −1,000 | n nhỏ |
| **cụm · giao hộp** | vùng được vẽ | 378 | 49,4 % | [−5,2; +6,4] | +0,025 | [−0,07; +0,26] |
| | cụm có HVN | 265 | 52,3 % | [−2,7; +9,9] | +0,076 | [−0,06; +0,34] |
| | cụm không có HVN | 422 | 45,5 % | [−10,0; +2,9] | −0,052 | [−0,15; +0,16] |
| | hợp lưu ≥ 2 nhóm | 165 | 53,2 % | [−4,4; +12,7] | +0,120 | [−0,11; +0,46] |
| | vàng | 25 | 22 % (18 lệnh) | n nhỏ | −0,500 | n nhỏ |
| cụm · chỉ mép hộp | vùng được vẽ | 374 | 49,7 % | [−5,1; +6,4] | +0,010 | [−0,08; +0,24] |
| | cụm có HVN | 256 | 53,6 % | [−1,5; +10,8] | +0,093 | [−0,03; +0,34] |
| | vàng | 21 | 20 % (15 lệnh) | n nhỏ | −0,600 | n nhỏ |
| cụm · giao hộp · chỉ chữ D | vùng được vẽ | 334 | 48,6 % | [−6,7; +6,1] | −0,013 | [−0,13; +0,24] |
| | cụm có HVN | 162 | 46,4 % | [−10,8; +6,1] | −0,154 | [−0,34; +0,18] |

**NQ — đối chứng 979 lần, thắng 46,5 %, R 1:2 −0,011**

| Định nghĩa HVN | Nhóm | n | thắng 1:1 | Δ thắng (điểm %) | R 1:2 | ΔR 1:2 |
|---|---|---|---|---|---|---|
| cũ | vùng được vẽ | 165 | 50,7 % | [−3,8; +12,3] | +0,255 | [+0,00; +0,50] |
| cũ | cụm có HVN | 38 | 37,5 % | [−19,6; +2,4] | +0,125 | [−0,17; +0,46] |
| cũ | vàng | 4 | 25 % (4 lệnh) | n nhỏ | −0,250 | n nhỏ |
| **cụm · giao hộp** | vùng được vẽ | 170 | 49,6 % | [−4,3; +11,3] | +0,228 | [−0,00; +0,46] |
| | cụm có HVN | 108 | 45,6 % | [−9,3; +8,1] | +0,100 | [−0,14; +0,36] |
| | cụm không có HVN | 232 | 47,9 % | [−5,4; +10,0] | +0,048 | [−0,13; +0,27] |
| | hợp lưu ≥ 2 nhóm | 94 | 50,0 % | [−4,7; +12,1] | +0,303 | [+0,02; +0,58] |
| | vàng | 30 | 48 % (27 lệnh) | n nhỏ | +0,333 | n nhỏ |
| cụm · chỉ mép hộp | vùng được vẽ | 168 | 50,7 % | [−2,5; +11,6] | +0,258 | [+0,06; +0,48] |
| | cụm có HVN | 100 | 45,8 % | [−8,0; +8,3] | +0,084 | [−0,13; +0,31] |
| | vàng | 30 | 48 % (27 lệnh) | n nhỏ | +0,333 | n nhỏ |
| cụm · giao hộp · chỉ chữ D | vùng được vẽ | 161 | 50,8 % | [−3,2; +12,3] | +0,251 | [+0,00; +0,51] |
| | cụm có HVN | 46 | 41,5 % | [−18,1; +7,8] | +0,171 | [−0,13; +0,53] |

Đọc bảng:
- **Vùng được vẽ: không khác trước, không khác đối chứng** ở tỉ lệ thắng trên cả hai mã. NQ vẫn nhỉnh ở R 1:2 với khoảng chạm 0 — giống hệt lần đo trước, không phải do HVN mới.
- **Cụm có HVN dạng cụm:** GC 52,3 % (220 lệnh), NQ 45,6 % (90 lệnh) — hai mã trái chiều, cả hai khoảng chứa 0. Không nói được HVN dạng cụm làm vùng tốt hơn hay xấu hơn.
- **Vàng:** GC 22 % trên 18 lệnh, NQ 48 % trên 27 lệnh. Mẫu quá nhỏ, và nhiều lần quay lại là cùng một vùng nên không độc lập. Không kết luận.
- **Mép hộp so với giao hộp:** chênh dưới 1,5 điểm % ở mọi dòng, số sự kiện gần trùng (GC 256 so với 265 cụm có HVN). Không có cơ sở để chọn luật phức tạp hơn.
- **Chữ D:** thêm lọc này không cải thiện dòng nào.

## 5. Đề xuất

1. **Dùng HVN dạng cụm với thông số mục 2; hợp lưu khi vùng va đập giao hộp (± 0,10 U như các mức khác); bỏ lọc chữ D; "đã rời xa ≥ 2 U" đo từ mép hộp.**
2. **Vùng vàng sẽ nhiều gấp 2–3.** Luật "≥ 3 nhóm và có HVN" giữ nguyên theo yêu cầu gốc; cần người dùng biết trước là màu vàng giờ có mặt 15–19 % thời gian. Chưa có số liệu nào nói vàng tốt hơn vùng thường.
3. **Bỏ hẳn HVN cũ**, kể cả lớp `ShowHvn`: lớp đó vẽ lại bằng hộp HVN dạng cụm (cùng một hàm với vùng mạnh), để chart và nhãn hợp lưu nói cùng một thứ. Chi tiết: PLAN mục 11.
4. Trạng thái của cả lớp vùng mạnh vẫn là **chưa kiểm định**.

## 6. Giới hạn

- Thông số hiệu chỉnh theo **một** hộp vẽ tay, qua mô tả bằng số, trên một mã khác (CFD so với hợp đồng tương lai). Bề rộng khớp; POC và basis chưa xác nhận.
- 52 phiên NQ, 74 phiên GC, 11–15 tuần. Thông số tuần (8 %) gần như chọn mù.
- Lần quay lại vùng: GC 378, NQ 170; vùng vàng 25 và 30. Không có TRAIN/TEST. GC trùng dữ liệu với các lần đo trước.
- Như cũ: chưa phí, chưa trượt giá; không xét order flow tại vùng — trong khi yêu cầu của người dùng là "canh phản ứng đảo chiều **hoặc** phá vỡ" tại hộp, tức quyết định nằm ở phản ứng tại chỗ, phép đo vào lệnh chờ ở mép không phản ánh cách dùng đó.
- Chưa đo hộp HVN đứng riêng (không cần cụm va đập) có giữ giá hay không. Đó là câu hỏi sát với cách người dùng dùng HVN nhất và nên là phép đo kế tiếp.

## 7. File

| File | Việc |
|---|---|
| `hvn_cum.py` | bản tham chiếu `clusters()`; `scan gc|nq` (bảng chọn thông số); `ca nq 2026-11-23` |
| `hvn_cum_ve.py` | vẽ PNG vào `hvn_cum/` |
| `hvn_cum_do.py` | đo mật độ + hiệu quả, 5 biến thể, `gc` / `nq` |
| `hvn_cum_fixture.py` | sinh `fixture/hvn_cum_cases.json` (11 profile, có NQ 23/11) và `fixture/expected_cum.json` (689 ca cả bộ máy) |
| `vung_manh.py` | **đã sửa**: thêm `HVN_MODE` (mặc định `cum`), `HVN_HL`, `D_ONLY` mặc định `False`, đo "rời xa" từ mép hộp. Chạy lại số cũ: `HVN_MODE=dinh D_ONLY=True` |
| `do_lai.py` | **đã sửa**: nhận `KHOA=giatri` và `nhan=ten` ở cuối dòng lệnh. Mặc định giờ chạy HVN dạng cụm |

Chạy lại: `python prep1.py gc` → `python prep1.py nq` → `python hvn_cum.py scan nq` → `python hvn_cum.py ca nq 2026-11-23` → `python hvn_cum_ve.py` → `python hvn_cum_do.py gc` → `python hvn_cum_do.py nq` → `python hvn_cum_fixture.py`. `fixture/expected.json`, `m30_bars.csv`, `m30_levels.csv.gz` cũ không bị đụng tới.
