# Ngưỡng thích nghi theo khung và theo phiên: Big Trade, chấm Bid/Ask, kiệt sức (2026-11-24)

> Ghi chú nghiên cứu + spec để code C#. Mọi luật ở đây là **khớp mật độ / vị trí hiển thị** với chart CORVEN, **không phải lợi thế đã kiểm định**.
> Chưa sửa C#, chưa commit. Bản Python trong thư mục này là chuẩn để so C# = Python.

Phiên dùng trong mọi bảng (giờ UTC, cố định): **Á 22:00–07:00, Âu 07:00–13:30, Mỹ 13:30–22:00**. Mỹ đổi giờ ngày 01/11 nên từ đó giờ mở cửa cổ phiếu Mỹ là 14:30 UTC; ranh giới giữ cố định cho đơn giản.

## 0. Kết luận ngắn

| Dấu | Vấn đề đo được | Đề xuất |
|---|---|---|
| Big Trade (vòng mờ) | Ngưỡng 10 cố định cho số vòng **mỗi giờ** không đổi theo khung, nên số vòng **mỗi nến** tăng thẳng theo khung: NQ M1 0,46 → M15 6,6 → H1 25,7 vòng/nến; phiên Mỹ NQ M15 **15 vòng/nến**, phiên Á 2 | Ngưỡng = **lệnh đơn lớn thứ K trong N nến trước** (tự lên ở phiên Mỹ, tự xuống ở phiên Á, tự theo khung), sàn 5, gộp vòng sát nhau, tối đa 3 vòng/nến → khoảng **0,9 vòng/nến ở mọi khung, mọi phiên** |
| Chấm Bid/Ask | (a) Mức nền 20 nến bị **trễ qua phiên** ở khung lớn: NQ M30 phiên Á 0,09 chấm/nến, phiên Mỹ 3,77. (b) Cửa sổ ±4 tick cố định của GC làm khung lớn dày dần (M1 0,46 → H1 1,54). (c) So với CORVEN thì luật hiện tại **sót hơn một nửa** (recall 0,46 trên GC M1) | Một công thức cho mọi mã: nền N nến ≈ 2 giờ, cửa sổ w = max(4, biên độ/6); bỏ bộ số riêng NQ. Ba bộ số (không sót / trung gian / ít nhiễu) |
| Kiệt sức | Đuôi 6 tick của nến gần như không đổi theo khung (trung vị 11–29 hợp đồng) còn mức so sánh (volume TB mỗi ô) tăng theo khung (5 → 65), nên khung lớn gần như nến nào cũng nổ: NQ H1 1,77 dấu/nến (tối đa 2) | Giữ luật cũ **và thêm**: đuôi phải ≤ 0,8 × trung vị đuôi của N nến trước. Giữ đủ 11/11 dấu CORVEN, NQ H1 còn 0,75 dấu/nến |

Cửa sổ lịch sử dùng chung cho cả ba (mục 1). Số đo ở các mục 2–4, spec C# ở mục 5, ví dụ kiểm thử ở mục 6, tham khảo phần mềm khác ở mục 7, giới hạn ở mục 8.

**Về tiêu chí "không nhiễu nhưng tuyệt đối không bỏ sót":** với dữ liệu hiện có, "tuyệt đối không sót" **không đạt được và phần lớn không đo được**:
- Kiệt sức: đo được, 11/11 (nhưng chỉ 11 dấu của một chart).
- Chấm: đo được trên GC M1 (885 chấm CORVEN). Luật lỏng tới mức vô dụng (4,35 chấm/nến) cũng chỉ bắt 93%; bộ đề xuất bắt 70%.
- Big Trade: **không đo được** (mục 2.5).

## 1. Cửa sổ lịch sử theo khung (dùng chung)

`N = min(20, max(5, round(120 / số phút một nến)))` → M1 20 · M5 20 · M10 12 · M15 8 · M30 5 · H1 5 · H4 5. Nến không theo thời gian: 20. (`common_window.py`)

Lý do: 20 nến M30 là 10 giờ, tức mức nền của phiên Á lấy từ phiên Mỹ hôm trước. Cửa sổ khoảng 2 giờ thì nền bám phiên. Số đo cho chấm (luật hiện tại, chỉ đổi N; `dot_window.py`):

| Chấm/nến Á / Âu / Mỹ | N = 20 (hiện tại) | N theo khung |
|---|---|---|
| NQ M15 | 0,37 / 1,26 / 2,05 | 0,68 / 1,15 / 1,09 (N = 8) |
| NQ M30 | 0,09 / 1,30 / 3,77 | 0,65 / 1,25 / 1,51 (N = 5) |
| NQ H1 | 0,09 / 0,81 / 3,99 | 0,35 / 2,18 / 2,03 (N = 5) |
| GC M30 | 0,61 / 2,08 / 1,57 | 1,27 / 1,52 / 0,94 |
| GC H1 | 0,44 / 2,02 / 2,45 | 1,21 / 2,20 / 1,25 |

H1 vẫn lệch (5 nến là 5 giờ, không rút ngắn hơn được vì cần ít nhất 5 nến). M1 và M5 không đổi (N vẫn 20).

## 2. Big Trade (vòng mờ)

### 2.1 Dữ liệu

Nhật ký lệnh đơn của indicator (`%APPDATA%/OrderFlowBubbles/bigtrade-log`). Kiểm bằng `inspect_logs.py`, `bt_check.py`:
- Không dòng nào trùng (nến, giá). Thứ tự dòng trong file không theo thời gian (file M1 NQ, GCZ26) nên phải sắp lại.
- **NQ**: `_NQZ26_XCME_Time_1Minute.csv`, 25/10 22:00 → 02/11 23:59 liền mạch (6 phiên, 8.340 nến M1) + 24/11 (204 nến sống).
- **GC**: `_GC_XCEC_Time_1Minute.csv`, 31/08 → 23/09 liền mạch (16 phiên, 22.948 nến M1; cả đoạn là GCZ26, không vắt chỗ nối hợp đồng). File chỉ tới 23/09, không phải 10/11.
- **GC sống**: `_GCZ26_XCEC_Time_1Minute.csv`, 09/11 → 24/11, đứt quãng (5.517 nến), dùng kiểm ngoài mẫu.
- Dựng khung lớn từ M1 (lệnh đơn lớn nhất theo (nến khung lớn, giá)) **trùng 100%** với nhật ký khung thật: NQ M15 128.536 ô giống hệt (3.692 ô ≥ 10 ở cả hai); GC M5 222.762 ô chung giống hệt.
- Phân phối chạy lại và sống giống nhau (GC M1: phân vị 99 đều là 9; ≥ 10 hợp đồng 0,162 và 0,160 lần/nến).

### 2.2 Phân phối lệnh đơn và ngưỡng 10 cố định (`bt_measure.py`)

Lệnh đơn lớn nhất của ô: trung vị 1 ở mọi nơi. Phân vị 99 của ô và trung vị của "lệnh lớn nhất mỗi nến":

| | Á | Âu | Mỹ |
|---|---|---|---|
| NQ M1: phân vị 99 ô / lệnh lớn nhất nến (trung vị) | 5 / 3 | 6 / 4 | 10 / 10 |
| NQ M15 | 10 / 16 | 13 / 17,5 | 20 / 39 |
| NQ H1 | 14 / 32 | 20 / 39 | 29 / 71 |
| GC M1 | 8 / 2 | 10 / 4 | 9 / 4 |
| GC M15 | 13 / 11 | 16 / 16 | 15 / 14 |
| GC H1 | 18 / 22 | 21 / 27 | 20 / 25,5 |

Ngưỡng 10 cố định, vòng/nến (vòng/giờ):

| | Á | Âu | Mỹ | Tất cả | Nhiều nhất 1 nến |
|---|---|---|---|---|---|
| NQ M1 | 0,14 (8/h) | 0,21 (13/h) | 1,05 (63/h) | 0,46 | 28 |
| NQ M5 | 0,69 | 1,03 | 5,14 | 2,26 | 59 |
| NQ M15 | 2,04 | 3,09 | **15,05** | 6,64 | 85 |
| NQ M30 | 4,06 | 6,13 | 29,58 | 13,08 | 107 |
| NQ H1 | 8,07 | 18,86 | 54,47 | 25,68 | 132 |
| GC M1 | 0,11 (7/h) | 0,21 (13/h) | 0,18 (11/h) | 0,16 | 19 |
| GC M5 | 0,54 | 1,04 | 0,90 | 0,80 | 43 |
| GC M15 | 1,61 | 3,06 | 2,63 | 2,35 | 56 |
| GC M30 | 3,15 | 6,03 | 5,16 | 4,61 | 66 |
| GC H1 | 6,20 | 12,55 | 9,32 | 9,08 | 74 |

Đọc: số vòng mỗi giờ gần như không đổi theo khung (hiển nhiên, cùng một tập lệnh), nên mỗi nến khung lớn gánh nhiều vòng hơn. NQ phiên Mỹ gấp 7,5 lần phiên Á; GC chênh ít (dữ liệu tháng 9).

### 2.3 Luật đề xuất: "lớn thứ K trong N nến trước"

1. Mỗi nến **đã đóng** có số liệu lệnh đơn nộp vào hàng đợi K lệnh đơn lớn nhất của nó. N theo mục 1, `K = max(1, round(mật độ đích × N))`, mật độ đích mặc định **1,0** (K = N).
2. Ngưỡng của nến đang xét = giá trị lớn thứ K trong gộp các giá trị của N nến trước; ngưỡng dùng = `max(sàn 5, giá trị đó)`. Chưa đủ 5 nến có số liệu: dùng ngưỡng cố định 10 như cũ.
3. Ô nổ khi lệnh đơn ≥ ngưỡng dùng.
4. Gộp vòng sát nhau trong một nến: duyệt lệnh đơn giảm dần (bằng nhau thì tick thấp trước), bỏ ô cách ô đã giữ ≤ g tick, `g = max(2, round(biên độ TB N nến trước / 8))`.
5. Giữ nhiều nhất **3** vòng lớn nhất mỗi nến.
6. Cỡ vòng tính theo lệnh đơn / ngưỡng dùng (không còn / 10).

Ý nghĩa: "một lệnh đơn chỉ đáng vẽ khi nó thuộc nhóm lớn nhất của khoảng 2 giờ vừa qua (20 phút trên M1)". Chỉ dùng nến đã đóng, tất định, tính rẻ (gộp nhiều nhất N × K = 400 số).

Các cách khác đã thử (`bt_alt.py`): bội số của trung vị "lệnh lớn nhất mỗi nến" (1,5–3 ×) cho mật độ lệch theo khung nhiều hơn (NQ M5 0,52 nhưng H1 1,19 với 1,5 ×) và không điều khiển được mật độ trực tiếp. N = 10/20/40 cố định: N = 20 cố định làm phiên Á ở M30 chỉ 0,42 trong khi Mỹ 1,20; N theo khung cho 0,65 / 0,81 / 0,87 (`bt_window.py`).

### 2.4 Trước / sau (`bt_final.py`, vòng/nến Á / Âu / Mỹ → tất cả; ngưỡng trung vị Á/Âu/Mỹ)

| | Cố định 10 | **Đề xuất (1,0 · sàn 5 · gộp · tối đa 3)** | Ngưỡng Á/Âu/Mỹ | Mật độ 0,75 | Sàn 10 |
|---|---|---|---|---|---|
| NQ M1 | 0,14 / 0,21 / 1,05 → 0,46 | 0,43 / 0,50 / 0,92 → **0,61** | 5 / 5 / 9 | 0,53 | 0,33 |
| NQ M5 | 0,69 / 1,03 / 5,14 → 2,26 | 0,81 / 1,03 / 0,88 → **0,90** | 7 / 7 / 20 | 0,72 | 0,66 |
| NQ M15 | 2,04 / 3,09 / 15,05 → 6,64 | 0,77 / 1,12 / 0,96 → **0,93** | 15 / 14 / 36 | 0,73 | 0,89 |
| NQ M30 | 4,06 / 6,13 / 29,58 → 13,08 | 0,81 / 1,10 / 1,00 → **0,95** | 24 / 20 / 49 | 0,77 | 0,95 |
| NQ H1 | 8,07 / 18,86 / 54,47 → 25,68 | 0,70 / 1,36 / 1,05 → **1,01** | 48 / 23 / 64 | 0,90 | 1,01 |
| GC M1 | 0,11 / 0,21 / 0,18 → 0,16 | 0,38 / 0,56 / 0,53 → **0,48** | 5 / 5 / 5 | 0,45 | 0,15 |
| GC M5 | 0,54 / 1,04 / 0,90 → 0,80 | 0,91 / 0,99 / 0,79 → **0,90** | 6 / 8 / 9 | 0,72 | 0,56 |
| GC M15 | 1,61 / 3,06 / 2,63 → 2,35 | 0,97 / 1,02 / 0,75 → **0,92** | 10 / 13 / 14 | 0,74 | 0,83 |
| GC M30 | 3,15 / 6,03 / 5,16 → 4,61 | 1,02 / 1,03 / 0,72 → **0,93** | 15 / 18 / 20 | 0,76 | 0,91 |
| GC H1 | 6,20 / 12,55 / 9,32 → 9,08 | 0,95 / 1,12 / 0,60 → **0,90** | 20 / 24 / 31 | 0,76 | 0,90 |
| GC sống M5 (09–24/11) | 0,48 / 0,77 / 1,78 → 0,78 | 0,81 / 0,92 / 0,99 → **0,88** | 6 / 8 / 10 | 0,70 | 0,50 |
| GC sống M15 | 1,40 / 2,35 / 5,14 → 2,30 | 0,82 / 1,00 / 0,98 → **0,92** | 10 / 12 / 20 | 0,74 | 0,83 |

- Không gộp, không giới hạn thì mật độ 1,0 cho 1,2–1,95 vòng/nến và nến đông nhất tới 77 vòng; gộp + tối đa 3 đưa về 0,9 và nến đông nhất 3.
- M1 bị **sàn 5** quyết định ở phiên Á/Âu (ngưỡng thứ K chỉ khoảng 4), nên M1 ra 0,5–0,6 chứ không phải 0,9.
- Nến đầu phiên Mỹ (13:30 UTC) vẫn đông hơn trung bình vì 20 nến trước thuộc phiên Âu: NQ M5 2,0 vòng (trước là 11), NQ M15 2,8 (trước là 33), GC M15 1,4 (trước 5,5). Giới hạn 3 vòng chặn trên.

### 2.5 Mật độ đích lấy từ đâu, và recall

- **Đo được:** CORVEN vẽ 25 vòng trên 26 nến M5 GC ngày 18/11 = 0,96 vòng/nến. Đó là mốc CORVEN duy nhất cho vòng mờ, lại rơi vào giờ sôi động (12:15–14:20 UTC).
- **Lựa chọn hiển thị:** (a) giữ mật độ **theo nến** không đổi qua các khung thay vì theo giờ, vì màn hình hiện số nến như nhau ở mọi khung, độ rối là theo nến; (b) mật độ đích 1,0 (sát 0,96 của CORVEN, nghiêng về phía không sót; 0,75 nếu muốn thưa hơn); (c) sàn 5; (d) tối đa 3 vòng/nến và khoảng gộp biên độ/8.
- **Recall so với CORVEN: không đo được.** Nhật ký sống ngày 18/11 chỉ có 42/130 nến M1 trong khoảng 12:15–14:24 (6/26 nến M5 đủ dữ liệu). Chỉ 4 trong 25 vòng CORVEN nằm ở nến có số liệu: lệnh đơn lớn nhất quanh đó (±4 tick) là 14, 8, 2, 1 hợp đồng, hai giá trị sau thuộc nến thiếu 2/5 nến M1 (`bt_corven.py`). Bốn điểm, một nửa thiếu dữ liệu: không kết luận được gì, kể cả câu "vòng CORVEN đúng là lệnh đơn ≥ 10".
- Cách lấy được recall: để indicator chạy sống **liên tục trên M1** suốt một buổi CORVEN chiếu chart cùng mã, rồi chạy lại `bt_corven.py` với ảnh buổi đó.
- Vì không có recall, phần "không bỏ sót" của Big Trade chỉ bảo đảm được theo nghĩa: trong mỗi nến, vòng bị bỏ luôn nhỏ hơn mọi vòng được giữ (gộp và giới hạn đều giữ lệnh lớn nhất). Ai muốn chắc hơn thì đặt giới hạn = 0 và gộp = 0 (mật độ lên 1,2–1,95 vòng/nến).

## 3. Chấm Bid/Ask

Dữ liệu: footprint 90 ngày một hợp đồng (không chỗ nối), pickle của `../nq_calib_2026-11-24` (GC 87.362 nến M1 từ 11/08; NQ 71.047 nến M1 từ 14/09).

### 3.1 Luật hiện tại theo phiên × khung (`dot_measure.py now`)

| Chấm/nến | Á | Âu | Mỹ | Tất cả | Sàn 9 là điều kiện quyết định (Á/Âu/Mỹ) |
|---|---|---|---|---|---|
| GC M1 | 0,43 | 0,52 | 0,46 | 0,46 | 60% / 20% / 13% số nến |
| GC M5 | 0,89 | 0,95 | 0,68 | 0,84 | 0% |
| GC M15 | 0,97 | 1,42 | 1,01 | 1,11 | 0% |
| GC M30 | 0,61 | 2,08 | 1,57 | 1,34 | 0% |
| GC H1 | 0,44 | 2,02 | 2,45 | 1,54 | 0% |
| NQ M1 | 0,46 | 0,53 | 0,43 | 0,47 | 25% / 16% / 0% |
| NQ M5 | 0,64 | 0,94 | 0,81 | 0,78 | 0% |
| NQ M15 | 0,37 | 1,26 | 2,05 | 1,19 | 0% |
| NQ M30 | **0,09** | 1,30 | **3,77** | 1,67 | 0% |
| NQ H1 | 0,09 | 0,81 | 3,99 | 1,54 | 0% |

Trả lời câu hỏi:
- **Mức nền 20 nến có đủ không?** Đủ ở M1 và M5 (ba phiên gần bằng nhau). **Không đủ từ M15 trở lên**: nền trễ qua phiên, phiên Á gần trống, phiên Mỹ dày. Sửa bằng cửa sổ mục 1.
- **Sàn 9 có vô nghĩa ở M15/H1 không?** Có: từ M5 trở lên 2,8 × mức nền luôn lớn hơn 9 (0% số nến sàn quyết định). Sàn chỉ có tác dụng ở M1, nhất là phiên Á của GC (60% số nến). Sàn vô hại ở khung lớn, không cần cho nó thích nghi.
- **Có dày ở phiên Mỹ, trống ở phiên Á không?** Ở M1/M5 thì không. Ở M15 trở lên thì có, do nền trễ.

### 3.2 Công thức chung (mọi mã, mọi khung)

Với B = trung bình của trung vị volume mỗi ô, R = trung bình biên độ nến (tick), cả hai trên N nến đã đóng trước (N theo mục 1):

- cửa sổ `w = max(4, round(R / 6))`
- ngưỡng `= max(k × B, sàn)`
- che chấm xanh cách chấm đỏ ≤ h tick
- `round` = làm tròn nửa lên, `floor(x + 0,5)`

| Bộ số | k | Sàn | Che h |
|---|---|---|---|
| **Không sót** (đề xuất mặc định theo tiêu chí "giữ recall trước") | 2,0 | 5 | 2 tick |
| Trung gian | 2,4 | 5 | 2 tick |
| Ít nhiễu (mật độ M1/M5 gần bằng hôm nay) | 2,8 | 9 | max(6, round(0,75 × w)) |

Bộ số riêng cho NQ (3,5 / ±max(8, R/14) / che 12) **bỏ**: cùng một công thức, NQ ra dày hơn GC 1,3–1,6 lần ở mọi khung, đúng với tỉ lệ trên chart của chính CORVEN (NQ 2,26 chấm/nến so với GC 1,53, gấp 1,48 lần).

Vì sao w theo R/6: w cố định thì nến càng rộng càng nhiều "đỉnh cục bộ". Vì sao che 2 tick ở hai bộ đầu: luật che rộng là thứ làm mất recall nhiều nhất trên M1 (mục 3.4); che 2 tick chỉ bỏ chấm xanh nằm ngay dưới chấm đỏ, tức chấm đằng nào cũng không nhìn thấy. Với bộ ít nhiễu, che 1,5 × w xóa quá nhiều chấm xanh ở khung lớn (đỏ chiếm 72–77% trên NQ), còn max(6; 0,75 w) giữ tỉ lệ đỏ 59–68% như hiện nay (`dot_hide.py`).

### 3.3 Trước / sau, chấm/nến Á / Âu / Mỹ → tất cả (`dot_final.py`, `dot_mid.py`)

| | Hiện tại | Ít nhiễu | Trung gian | **Không sót** |
|---|---|---|---|---|
| GC M1 | 0,43 / 0,52 / 0,46 → 0,46 | 0,42 / 0,52 / 0,45 → 0,46 | 0,69 / 0,75 / 0,65 → 0,70 | 0,90 / 0,99 / 0,89 → **0,92** |
| GC M5 | 0,89 / 0,95 / 0,68 → 0,84 | 0,80 / 0,85 / 0,58 → 0,74 | 1,19 / 1,26 / 0,88 → 1,11 | 1,58 / 1,70 / 1,23 → **1,50** |
| GC M15 | 0,97 / 1,42 / 1,01 → 1,11 | 0,87 / 0,93 / 0,63 → 0,81 | 1,36 / 1,43 / 0,99 → 1,26 | 1,86 / 1,98 / 1,41 → **1,74** |
| GC M30 | 0,61 / 2,08 / 1,57 → 1,34 | 0,88 / 1,02 / 0,65 → 0,84 | 1,43 / 1,60 / 1,06 → 1,36 | 1,99 / 2,21 / 1,53 → **1,90** |
| GC H1 | 0,44 / 2,02 / 2,45 → 1,54 | 0,78 / 1,25 / 0,73 → 0,91 | 1,32 / 2,05 / 1,20 → 1,50 | 1,88 / 2,78 / 1,61 → **2,07** |
| NQ M1 | 0,46 / 0,53 / 0,43 → 0,47 | 0,64 / 0,77 / 0,64 → 0,67 | 1,12 / 1,25 / 0,98 → 1,11 | 1,49 / 1,66 / 1,39 → **1,51** |
| NQ M5 | 0,64 / 0,94 / 0,81 → 0,78 | 0,88 / 1,20 / 0,94 → 0,99 | 1,37 / 1,89 / 1,50 → 1,56 | 1,87 / 2,46 / 1,97 → **2,07** |
| NQ M15 | 0,37 / 1,26 / 2,05 → 1,19 | 0,89 / 1,38 / 1,04 → 1,08 | 1,46 / 2,19 / 1,75 → 1,77 | 2,00 / 2,84 / 2,29 → **2,34** |
| NQ M30 | 0,09 / 1,30 / 3,77 → 1,67 | 0,84 / 1,42 / 1,18 → 1,12 | 1,42 / 2,28 / 1,94 → 1,84 | 1,92 / 3,02 / 2,47 → **2,42** |
| NQ H1 | 0,09 / 0,81 / 3,99 → 1,54 | 0,51 / 1,93 / 1,47 → 1,25 | 0,83 / 3,05 / 2,54 → 2,05 | 1,22 / 3,75 / 3,06 → **2,58** |

Mọi bộ đều hết cảnh phiên Á trống / phiên Mỹ dày ở M15–M30. Nến đầu phiên Mỹ vẫn đông (NQ M5 khoảng 7 chấm với bộ ít nhiễu, 11 với bộ không sót; hiện tại 8,7), và chấm không có giới hạn số lượng mỗi nến (ô "TopN" đang có sẵn, mặc định 0).

### 3.4 So với chart CORVEN (`dot_recall.py`, `dot_recall2.py`, `dot_recall3.py`, `dot_corven_m5.py`)

Mẫu: GC M1 580 nến / 885 chấm; NQ M1 534 nến / 1.205 chấm (ngày 06/11, chart gộp hàng 8 tick); GC M5 26 nến / 16 cụm chấm (khoảng 33 chấm). Khớp M1: cùng nến, cùng màu (tím khớp cả hai), cách ≤ 3 tick. Khớp M5: cụm CORVEN có chấm cùng nến, cùng màu, cách tâm cụm ≤ 5 tick.

| Luật | GC M1 chấm/nến | GC M1 recall / precision | NQ M1 chấm/nến | NQ M1 recall / precision | GC M5: số chấm, cụm trùng |
|---|---|---|---|---|---|
| CORVEN | 1,53 | | 2,26 | | khoảng 33, 16 cụm |
| Hiện tại | 0,57 | 0,46 / 0,98 | 0,82 | 0,23 / 0,50 | 33, 7/16 |
| Ít nhiễu | 0,57 | 0,46 / 0,98 | 0,88 | 0,24 / 0,48 | 30, 7/16 |
| Trung gian | 0,83 | 0,61 / 0,92 | 1,78 | 0,38 / 0,39 | 41, 9/16 |
| **Không sót** | 1,04 | **0,70 / 0,85** | 2,17 | 0,39 / 0,33 | 49, 10/16 |
| 2,0 · sàn 5 · không che | 1,17 | 0,75 / 0,85 | 2,27 | 0,39 / 0,33 | 56, 12/16 |
| 1,6 · sàn 3 · w tối thiểu 2 · không che | 1,87 | 0,87 / 0,67 | 3,69 | 0,47 / 0,24 | 93, 12/16 |
| 1,0 · sàn 2 · ±1 tick · không che | 4,35 | 0,93 / 0,44 | 14,76 | 0,87 / 0,21 | 326, 16/16 |

Cách đọc:
- Luật hiện tại rất "sạch" (98% chấm của mình trùng chấm CORVEN trên GC) nhưng **sót 54%**. CORVEN vẽ 1,53 chấm/nến, mình 0,57.
- Thứ chặn recall, theo thứ tự: **luật che** (cùng k = 2,0, sàn 5: che rộng 0,62 → che 2 tick 0,70 → không che 0,75), rồi **bội số k**, rồi **sàn** trên M1.
- Recall có trần: luật gần như vẽ mọi ô vẫn chỉ 0,93 trên GC. Nguồn dữ liệu của CORVEN khác của mình.
- **NQ không kết luận được về vị trí**: chart CORVEN gộp 8 tick một hàng, mình xét từng tick; precision 0,2–0,5 ở mọi luật. Chỉ dùng được con số mật độ.
- GC M5 chỉ có 16 cụm trên một chart; chênh 7/16 so với 10/16 là 3 cụm.
- Công thức chung bộ ít nhiễu không làm tệ đi so với hiện tại (GC M1 0,46 / 0,98 giữ nguyên; NQ 0,24 / 0,48 so với 0,23 / 0,50; GC M5 30 chấm so với 33, chung nhau 29).

**Đánh đổi phải chọn:** bộ không sót nâng recall GC M1 từ 0,46 lên 0,70 nhưng số chấm gấp đôi (GC M1 0,46 → 0,92; NQ M15 1,19 → 2,34 chấm/nến). Từ M15 trở lên **không có mẫu CORVEN nào**, nên ở các khung đó chỉ đo được mật độ, không đo được recall.

## 4. Kiệt sức

### 4.1 Luật hiện tại theo mã × khung × phiên (`exh_now.py`; khớp đúng số của Golden C#: GC M1 12.594, NQ M5 10.849, NQ M15 5.848, NQ H1 2.087)

Luật: râu ≥ 3 tick và S6 (tổng bên soi trên 6 tick từ cực trị) ≤ 1,1 × volume TB mỗi ô của 20 nến trước.

| | Á | Âu | Mỹ | Dấu/nến | Phía nến có râu ≥ 3 | Trong đó đạt "mỏng" | S6 trung vị | Ngưỡng trung vị |
|---|---|---|---|---|---|---|---|---|
| GC M1 | 0,13 | 0,14 | 0,16 | 0,14 | 54% | 13% | 11 | 5,2 |
| GC M5 | 0,31 | 0,36 | 0,43 | 0,36 | 80% | 23% | 19 | 11,1 |
| GC M15 | 0,63 | 0,57 | 0,81 | 0,67 | 89% | 38% | 24 | 19,1 |
| GC M30 | 1,10 | 0,72 | 0,98 | 0,95 | 92% | 52% | 27 | 28,4 |
| GC H1 | 1,49 | 1,16 | 1,08 | 1,26 | 95% | 66% | 29 | 40,5 |
| NQ M1 | 0,24 | 0,30 | 0,50 | 0,35 | 80% | 21% | 11 | 5,1 |
| NQ M5 | 0,57 | 0,60 | 1,12 | 0,76 | 92% | 41% | 16 | 10,5 |
| NQ M15 | 1,30 | 0,97 | 1,39 | 1,24 | 96% | 65% | 18 | 20,9 |
| NQ M30 | 1,84 | 1,33 | 1,35 | 1,53 | 97% | 79% | 19 | 42,1 |
| NQ H1 | 1,90 | 1,89 | 1,50 | 1,77 | 98% | 90% | 20 | 64,7 |

Nghi vấn được xác nhận, kèm cơ chế: giá chỉ ở 6 tick ngoài cùng trong chốc lát dù nến dài bao nhiêu, nên **S6 gần như không tăng theo khung** (11 → 29 trên GC, 11 → 20 trên NQ), còn volume TB mỗi ô **tăng theo khung** (5 → 40 và 5 → 65). Ở NQ H1, 90% phía nến có râu đều "mỏng". Điều kiện râu ≥ 3 tick cũng gần như luôn đạt trên nến rộng.

### 4.2 So với CORVEN

- Mẫu duy nhất: 11 dấu trên 26 nến M5 GC ngày 18/11 (0,42 dấu/nến). `corven_nq_raw.csv` chỉ có ba màu đỏ / xanh / tím, **không có dấu kiệt sức nào trên NQ**.
- 11 dấu CORVEN đều có bên soi tại đúng cực trị từ 1 đến 5 hợp đồng, **không dấu nào bằng 0**; S6 từ 3 đến 17; râu từ 3 đến 41 tick trên nến rộng 32–128 tick. Vì vậy không thể đòi "bằng 0 ở cực trị", cũng không thể tăng số tick râu tối thiểu hay số tick đuôi theo biên độ mà không sót dấu (hai dấu có S8 nhảy lên 22 và 48).
- Trên toàn dữ liệu, bên soi bằng 0 tại cực trị chỉ xảy ra ở 3–13% phía nến.

### 4.3 Luật đề xuất

Giữ nguyên luật cũ và **thêm một điều kiện**: `S6 ≤ c × trung vị của S6 trên N nến đã đóng trước` (gộp cả đỉnh lẫn đáy, 2N giá trị; N theo mục 1; cần ≥ 5 nến), **c = 0,8**. Nghĩa là: đuôi phải mỏng không chỉ so với thân nến, mà cả so với đuôi của các nến gần đây. Mức so sánh này không phình theo khung.

Khớp CORVEN (`exh_final.py`): S6 / trung vị đuôi của 11 dấu CORVEN là 0,12 · 0,12 · 0,33 · 0,41 · 0,50 · 0,51 · 0,56 · 0,64 · 0,72 · 0,73 · 0,76.

| Luật | Dấu trên 26 nến | Trùng | Thừa | Sót |
|---|---|---|---|---|
| Hiện tại | 13 | 11/11 | 2 | 0 |
| **+ đuôi ≤ 0,8 × trung vị** | 12 | **11/11** | 1 | 0 |
| + đuôi ≤ 1,0 × trung vị | 13 | 11/11 | 2 | 0 |
| Chỉ điều kiện đuôi 0,8 (bỏ luật cũ) | 15 | 11/11 | 4 | 0 |
| Chỉ điều kiện đuôi 0,7 | 10 | 8/11 | 2 | 3 |

Dấu/nến, Á / Âu / Mỹ → tất cả:

| | Hiện tại | **+ đuôi 0,8** | + đuôi 1,0 |
|---|---|---|---|
| GC M1 | 0,13 / 0,14 / 0,16 → 0,14 | 0,13 / 0,14 / 0,16 → 0,14 | 0,14 |
| GC M5 | 0,31 / 0,36 / 0,43 → 0,36 | 0,31 / 0,36 / 0,41 → 0,35 | 0,36 |
| GC M15 | 0,63 / 0,57 / 0,81 → 0,67 | 0,55 / 0,51 / 0,62 → **0,56** | 0,64 |
| GC M30 | 1,10 / 0,72 / 0,98 → 0,95 | 0,70 / 0,57 / 0,68 → **0,66** | 0,79 |
| GC H1 | 1,49 / 1,16 / 1,08 → 1,26 | 0,82 / 0,61 / 0,70 → **0,72** | 0,93 |
| NQ M1 | 0,24 / 0,30 / 0,50 → 0,35 | 0,24 / 0,30 / 0,42 → 0,32 | 0,33 |
| NQ M5 | 0,57 / 0,60 / 1,12 → 0,76 | 0,52 / 0,53 / 0,63 → **0,56** | 0,66 |
| NQ M15 | 1,30 / 0,97 / 1,39 → 1,24 | 0,74 / 0,64 / 0,65 → **0,68** | 0,89 |
| NQ M30 | 1,84 / 1,33 / 1,35 → 1,53 | 0,79 / 0,69 / 0,65 → **0,71** | 0,95 |
| NQ H1 | 1,90 / 1,89 / 1,50 → 1,77 | 0,93 / 0,74 / 0,54 → **0,75** | 0,98 |

- Tỉ lệ nến có cả hai dấu (đỉnh và đáy) ở NQ H1 giảm từ 80% xuống 18%.
- **Biên an toàn mỏng:** dấu CORVEN "dày" nhất có tỉ số 0,76, ngưỡng 0,8. Chọn trên chính 11 dấu này. Muốn chắc không sót hơn thì dùng 1,0 (vẫn 11/11, mật độ khung lớn 0,8–1,0). Với trung vị, c = 1,0 nghĩa là "mỏng hơn một nửa số đuôi", tức gần như không lọc.
- Luật mới vẫn chưa xuống tới 0,42 dấu/nến của CORVEN ở khung lớn; không có chart CORVEN khung lớn để biết con số đúng.

## 5. Spec cho C#

Làm tròn ở mọi công thức: **`Math.Floor(x + 0.5)`**, không dùng `Math.Round` (làm tròn về số chẵn: 4,5 → 4, lệch Python).

### 5.1 Dùng chung

- `BaselineWindow.BarsFor(double minutesPerBar, double windowMinutes = 120)` = `minutes > 0 ? min(20, max(5, floor(window / minutes + 0.5))) : 20`. Số phút lấy như đoạn đã có ở `OrderFlowBubbles.cs` dòng ~1278 (`HistoricalData.Aggregation as HistoryAggregationTime`); không phải nến thời gian → 20.
- Ô cài đặt: **"Nền tự co theo khung"** (bool, mặc định bật; tắt = 20 nến như cũ) và **"Cửa sổ nền (phút)"** (120, hiện khi bật).
- `CellBigBaseline` hiện dùng chung một độ dài cho ba hàng đợi (TB mỗi ô, trung vị mỗi ô, biên độ). Cần tách: **TB mỗi ô giữ 20 nến** (luật kiệt sức cũ), **trung vị và biên độ dùng N**.
- Thêm vào dấu vân tay tham số mọi ô mới; đổi nhãn phiên bản (`cellbig-v19`, `bigtrade-v2`, `exh-v4`).
- Tắt hết các ô "thích nghi" phải cho đúng kết quả cũ (golden cũ không đổi).

### 5.2 Big Trade

Lớp thuần `BigTradeAdaptive` (cạnh `BigTradeLogic`), trạng thái: hàng đợi tối đa N phần tử, mỗi phần tử = (mảng K lệnh đơn lớn nhất của nến, giảm dần; biên độ tick của nến = tick cao nhất − thấp nhất trong các ô có lệnh đơn > 0).

```
K = max(1, floor(Density * N + 0.5))
Threshold():            // gọi trước khi xét nến i (đã đóng hay đang chạy), chỉ từ các nến ĐÃ ĐÓNG trước
    nếu Count < 5  -> FixedMin (BigTradeMinContracts, 10)
    v = gộp mọi giá trị trong hàng đợi, sắp giảm dần; kth = v.Count >= K ? v[K-1] : 0
    thr = max(Floor, kth); nếu Ceil > 0: thr = min(thr, Ceil)
MergeTicks():  Count >= 5 và MergeDiv > 0 và R_tb > 0 ? max(MergeMin, floor(R_tb / MergeDiv + 0.5)) : MergeMin
Select(cells, thr, g, cap):   // cells = (tick, mot) của nến
    đạt = mot > 0 && mot >= thr
    sắp theo mot giảm dần, bằng nhau thì tick tăng dần
    duyệt: nếu cap > 0 và đã giữ đủ cap -> dừng; nếu g > 0 và có ô đã giữ cách <= g tick -> bỏ; còn lại giữ
AddClosedBar(cells):    // ĐÚNG 1 lần mỗi nến đóng, SAU khi đã xét nến đó
    nếu không ô nào mot > 0 -> không làm gì (nến không có số liệu lệnh đơn)
    nộp (top K, biên độ); quá N thì bỏ phần tử cũ nhất
```

- Mặc định: Density 1,0 · Floor 5 · Ceil 0 (tắt) · MergeDiv 8 · MergeMin 2 · Cap 3 · N theo 5.1.
- Cỡ vòng: `BigTradeLogic.SizeFrac(mot, thr)` với thr là ngưỡng dùng. Màu như cũ.
- Ô cài đặt: "Big Trade · Ngưỡng tự thích nghi" (bật), "Mật độ đích (vòng/nến)" 1,0, "Sàn (hợp đồng)" 5, "Trần (0 = tắt)" 0, "Tối đa vòng mỗi nến (0 = không giới hạn)" 3, "Gộp vòng: biên độ nến chia cho (0 = chỉ gộp tối thiểu)" 8, "Gộp tối thiểu (tick)" 2. Tắt thích nghi = ngưỡng cố định như cũ (không gộp, không giới hạn).
- Tooltip nên ghi ngưỡng đang dùng: `Big trade: 1 lệnh 23 hợp đồng (ngưỡng 14) | ô ...`.
- Nhật ký lệnh đơn vẫn ghi mọi giá trị như cũ.
- **Ca biên bắt buộc xử lý:**
  1. Lịch sử không có lệnh đơn (luôn 0). Sau khi mở chart, hàng đợi rỗng → 5 nến sống đầu dùng ngưỡng 10 (vẫn áp gộp và giới hạn). Trên M15 đó là hơn một giờ.
  2. Nên làm (đề xuất, chưa đo): **làm nóng từ nhật ký**. `BigTradeLog.Load` giữ thêm giá trị (time_ticks → danh sách (giá, mot)); khi nạp nến lịch sử đã đóng mà số liệu nền tảng bằng 0, lấy lệnh đơn từ nhật ký cho cả `AddClosedBar` lẫn việc tính lại vòng. Nếu không, đổi tham số (đổi dấu vân tay) sẽ làm mất hết vòng lịch sử như hiện nay.
  3. Nến lịch sử không có số liệu **không được** nộp vào hàng đợi (nếu nộp số 0 thì ngưỡng tụt về sàn).
  4. Hàng đợi sau khoảng hở dài (hôm qua → hôm nay) vẫn dùng được nhưng lệch phiên; chấp nhận, vì 5–20 nến sống là thay hết.

### 5.3 Chấm

Trong `CellSettings(...)`, khi bật **"Chấm tự co dãn theo khung (công thức chung)"** (mặc định bật):

```
B, R = TryGetMedian / TryGetRange của N nến trước        // như hiện có, chỉ đổi độ dài hàng đợi
w = max(CellDotLocalTicks /*4*/, floor(R / 6 + 0.5))     // R <= 0 hoặc chưa có -> CellDotLocalTicks
h = max(CellDotHideBuyNearSellTicks, floor(HideRatio * w + 0.5))
ngưỡng = max(CellDotMedianRatio * B, sàn)                // Evaluate không đổi
```

- Khi bật: **không** áp `SymbolPreset.ApplyNasdaq`. Khi tắt: hành vi cũ (kể cả bộ Nasdaq).
- `CellBigLogic.Evaluate` giữ nguyên; chỉ đổi cách dựng `CellBigSettings`.
- Ô cài đặt mới: "Chấm tự co dãn theo khung" (bật), "Biên độ nến chia cho (cửa sổ)" 6, "Che theo cửa sổ (tỉ lệ)". Mặc định theo bộ số chọn:

| Ô | Không sót | Trung gian | Ít nhiễu |
|---|---|---|---|
| Bội số trung vị (`CellDotMedianRatio`) | 2,0 | 2,4 | 2,8 |
| Sàn (`CellBigMinSide`) | 5 | 5 | 9 |
| Che tối thiểu (`CellDotHideBuyNearSellTicks`) | 2 | 2 | 6 |
| Che theo cửa sổ (tỉ lệ) | 0 | 0 | 0,75 |

  Gọn nhất là một ô chọn "Bộ số chấm" ba mức, đặt bốn giá trị trên.
- Ca biên: chưa đủ 5 nến nền → không chấm (như cũ). Nến đang chạy: dùng nền của các nến đã đóng (như cũ).

### 5.4 Kiệt sức

- `ExhSettings` thêm `TailMedianRatio = 0.8` (≤ 0 = tắt, đúng luật cũ).
- `ExhaustionLogic.Detect` thêm tham số `bool hasTail, double tailMedian`; sau điều kiện cũ thêm: `if (s.TailMedianRatio > 0 && hasTail && !(sum <= s.TailMedianRatio * tailMedian)) return none;`. Chưa đủ nền đuôi thì chỉ áp luật cũ.
- Thêm hàm thuần `TailSum(top, extTick, levels, sumLevels)` (đúng vòng cộng đang có trong `Detect`).
- Nền đuôi (lớp nhỏ `ExhTailBaseline(N)`): mỗi nến **đã đóng** có giao dịch và high > low nộp **hai** số (đuôi đỉnh theo Ask, đuôi đáy theo Bid), **không phụ thuộc râu dài hay ngắn**; giữ N nến; `TryGetMedian` cần ≥ 5 nến, trả trung vị của 2 × số nến giá trị (số chẵn: trung bình hai giá trị giữa). Nộp trong `AddToBaseline`, tức sau khi nến đó đã được xét.
- Đổi `ExhSumLevels` thì phải dựng lại hàng đợi (đã nằm trong dấu vân tay).
- Ô cài đặt: "Kiệt sức · Đuôi ≤ số này × trung vị đuôi các nến trước (0 = tắt)" 0,8.

## 6. Kiểm thử và so C# = Python

Chạy (thư mục này, `PYTHONIOENCODING=utf-8`):

```bash
python bt_selftest.py     # ví dụ nhỏ + bản nhanh = bản chuẩn + ghi bt_golden_<mã>_M<khung>.csv
python dot_selftest.py    # ví dụ nhỏ + bản nhanh = bản chuẩn + số chấm chuẩn + dot_golden_<bộ>_<mã>_M<khung>.csv
python exh_common.py      # dựng X_<mã>_m<khung>.pkl (khoảng 400 MB, đã xóa sau khi đo; cần cho exh_now / exh_grid / exh_final / exh_selftest)
python exh_selftest.py    # ví dụ nhỏ + số dấu chuẩn + exh_golden_<mã>_M<khung>.csv
```

Bản chuẩn từng nến (dịch thẳng sang C#): `bt_rule.run_reference`, `dot_rule.run_reference` + `dot_rule.unified`, `exh_rule.run_reference`.

### 6.1 Ví dụ nhỏ cho unit test (đều đã chạy đạt trong các file selftest)

**Cửa sổ nền:** phút 1, 2, 5, 10, 15, 20, 30, 60, 240 → 20, 20, 20, 12, 8, 6, 5, 5, 5; phút 0 → 20.

**Big Trade**
- Giá trị lớn thứ 3 của `[[12,7,3],[9,2],[30]]` = 9. Của `[[12],[9]]` = 0 (chưa đủ 3 giá trị).
- Gộp/giới hạn, ô (tick, lệnh đơn) = (100,20) (101,30) (110,20) (104,25):
  - g = 2, tối đa 3 → (101,30) (104,25) (110,20) [100 cách 101 một tick nên bỏ]
  - g = 2, tối đa 2 → (101,30) (104,25)
  - g = 0, tối đa 0 → (101,30) (104,25) (100,20) (110,20)
  - thay 104 bằng 103: g = 2 → (101,30) (110,20)
  - (105,9) (100,9) (103,9), g = 2 → (100,9) (103,9) [bằng nhau: tick thấp trước; 105 cách 103 hai tick]
- Khoảng gộp: biên độ 3,6 → 2; 183 → 23; 20 → 3 (2,5 làm tròn lên); 0 → 2; chia cho 0 → 2.
- Chuỗi 8 nến, N = 5, mật độ 0,6 (K = 3), sàn 5, cố định 10, tối đa 3, chia 8, tối thiểu 2:

| Nến | Ô (tick, lệnh đơn) | Ngưỡng | Vòng giữ lại |
|---|---|---|---|
| 0 | (100,1) (101,6) (102,2) | 10 | không |
| 1 | (100,3) (104,8) | 10 | không |
| 2 | (99,12) (100,1) | 10 | (99,12) |
| 3 | (101,2) (102,4) | 10 | không |
| 4 | (100,7) (103,5) (110,1) | 10 | không |
| 5 | (100,7) (101,9) (102,7) (105,6) (108,15) (109,7) | **7** (gộp: 12 8 **7** 6 5 …) | (108,15) (101,9) |
| 6 | (100,0) (101,0) — không có số liệu | 9 | không; **không vào hàng đợi** |
| 7 | (100,9) (103,9) (106,9) (109,30) | **9** (nến 1–5: 15 12 **9** 8 7 …) | (109,30) (100,9) (103,9) |

  Cùng chuỗi, chia 2: nến 7 có g = 3 → (109,30) (100,9). Sàn 8: ngưỡng nến 5 = 8. Trần 6: ngưỡng nến 5 = 6.

**Chấm** (`unified(B, R, k, sàn, tỉ lệ che, che tối thiểu)` → ngưỡng, w, h)
- Ít nhiễu: (8; 39) → 22,4 · 7 · 6. (3; 16) → 9 · 4 · 6. (16,2; 183) → 45,36 · 31 · 23. (10; 0) → 28 · 4 · 6.
- Không sót: (8; 39) → 16 · 7 · 2. (2; 16) → 5 · 4 · 2.
- B = 0 hoặc chưa có → không chấm.
- Làm tròn: R = 27 → w = 5 (4,5 lên 5); R = 21 → 4.
- Một nến, ô (tick, Bid, Ask) = (100,5,30) (101,2,3) (104,25,1) (108,40,26) (112,3,24) (120,1,23), ngưỡng 22,4:
  - w = 7, che 6 → xanh {100, 120}, đỏ {108}
  - w = 7, che 8 → xanh {120}, đỏ {108}
  - w = 3, che 6 → xanh {120}, đỏ {104, 108}
- (100, Bid 30) và (102, Bid 30), w = 4 → không chấm nào (bằng nhau không tính là lớn hơn hẳn).
- Chuỗi: 5 nến nền, mỗi nến 13 ô tick 100–112, mỗi ô Bid 2, Ask 2 (B = 4, R = 12); nến xét (tick, Bid, Ask) = (100,12,1) (103,11,0) (105,2,15) (112,0,20):
  - ít nhiễu → ngưỡng 11,2 · w 4 · che 6 · xanh {112} · đỏ {100}
  - không sót → ngưỡng 8 · w 4 · che 2 · xanh {105, 112} · đỏ {100}

**Kiệt sức**
- Ô tick → (Bid, Ask): 100 (4,0) · 101 (3,1) · 102 (0,2) · 103 (5,6) · 104 (2,9) · 105 (1,3) · 110 (7,2) · 111 (0,1). Đuôi đỉnh tại 111 = 3; đuôi đáy tại 100 = 15.
- Trung vị [3, 15, 1, 8] = 5,5; [3, 15, 1] = 3.
- 5 nến nền (mở 103, cao 111, thấp 100, đóng 104, ô như trên; TB mỗi ô 5,75; trung vị đuôi 9) rồi:
  - nến y hệt → đỉnh **có** dấu (râu 7; 3 ≤ 6,325 và 3 ≤ 7,2), đáy không (15 > 6,325)
  - nến mở 109, đóng 108 → không dấu (râu đỉnh 2 tick)
- 5 nến nền đuôi rất mỏng (mở 104, cao 113, thấp 100, đóng 105; ô 100 (1,0) · 101 (1,0) · 106 (9,9) · 107 (9,9) · 112 (0,1) · 113 (0,1); trung vị đuôi 2; TB mỗi ô 6,67) rồi nến như trên → **không** dấu (3 ≤ 7,33 nhưng 3 > 1,6); đặt tỉ lệ đuôi = 0 → có dấu.

### 6.2 Số chuẩn trên dữ liệu thật

**Chấm** (chạy `perf/Golden stophunt` trên CSV của `../nq_calib_2026-11-24/tf_csv.py`; GC cần bản tương tự cho khung lớn). Tổng (đỏ + xanh):

| | Không sót | Ít nhiễu |
|---|---|---|
| GC M1 (87.362 nến) | 80.386 (47.288 + 33.098) | 39.918 (24.583 + 15.335) |
| GC M5 | 26.402 (15.221 + 11.181) | 13.106 (8.067 + 5.039) |
| GC M15 | 10.238 (5.727 + 4.511) | 4.747 (2.943 + 1.804) |
| GC M30 | 5.575 (3.069 + 2.506) | 2.464 (1.547 + 917) |
| GC H1 | 3.027 (1.644 + 1.383) | 1.329 (850 + 479) |
| NQ M1 (71.047 nến, từ 14/09) | 106.953 (58.967 + 47.986) | 47.895 (28.365 + 19.530) |
| NQ M5 | 29.450 (15.940 + 13.510) | 14.124 (8.944 + 5.180) |
| NQ M15 | 11.061 (5.906 + 5.155) | 5.118 (3.356 + 1.762) |
| NQ M30 | 5.722 (3.010 + 2.712) | 2.652 (1.733 + 919) |
| NQ H1 | 3.044 (1.587 + 1.457) | 1.476 (1.007 + 469) |

Từng chấm (nến, tick, màu): `dot_golden_<khong_sot|it_nhieu>_GC_M15.csv`, `..._NQ_M30.csv`.

**Kiệt sức** (bản chuẩn từng nến, tỉ lệ đuôi 0,8): GC M5 6.247 (luật cũ 6.382) · GC M15 3.293 (3.945) · NQ M5 7.896 (10.849) · NQ M30 1.693 (3.621). Từng dấu: `exh_golden_<mã>_M<khung>.csv`. Bản bảng nhanh (`exh_final.py`) lệch bản chuẩn 0–3 dấu do cách khởi đầu hàng đợi; **C# phải khớp bản chuẩn**.

**Big Trade** (mặc định mục 5.2, từ nhật ký; `bt_golden_*.csv` có cột nến, tick, lệnh đơn, ngưỡng, khoảng gộp): NQ M1 5.096 vòng / 8.340 nến · NQ M15 516 / 556 · GC M5 4.120 / 4.594 · GC M30 711 / 766. C# cần một đường chạy thử đọc nhật ký (time, giá, mot) làm đầu vào; `perf/Golden` chưa có.

## 7. Phần mềm khác đặt ngưỡng thế nào (tra tài liệu chính hãng 24/11/2026)

| Phần mềm | Cơ chế | Thích nghi? |
|---|---|---|
| ATAS Big Trades | Min/Max Volume cố định, hoặc **Auto Filter** ba mức (Weak / Medium / Strong) "theo mã và hoạt động thị trường"; thuật toán không công bố | Có, không rõ cách |
| ATAS Cluster Search | Min/Max cố định, Auto Filter, hoặc **phần trăm volume của nến** (Min/Max Volume Percent) | Có (theo nến) |
| Sierra Chart Large Volume Trade Indicator | Volume Threshold cố định; chỉ **cỡ và màu** dấu là tương đối (theo nến đang hiện / đã nạp) | Không |
| NinjaTrader Order Flow Trade Detector | "Minimum volume for marker" cố định; cỡ dấu theo vùng nhìn thấy hoặc phiên | Không |
| NinjaTrader Volumetric | Tỉ lệ mất cân bằng 1,5; delta tối thiểu 10; cố định | Không |
| Bookmap volume dots | Sàn cố định; cỡ chấm so với **cỡ lệnh trung bình của mã**; gộp chấm sát nhau ("Smart") | Một phần |
| Bookmap Stops & Icebergs | **Ngưỡng = trung bình + hệ số × độ lệch chuẩn** trên cửa sổ cuốn tính bằng phút, tính lại mỗi phút | Có, công bố công thức |
| Jigsaw Auction Vista | "Thuật toán tự chỉnh" cho lệnh cỡ khác thường; không công bố | Có, không rõ cách |
| Kiệt sức / đấu giá xong (ATAS, Sierra, NinjaTrader) | **Chỉ nhị phân**: một bên bằng 0 ở cực trị = đấu giá xong; Sierra có thêm sàn cố định cho "cả hai bên khác 0" | Không |
| Ngoài phần mềm | Volume tương đối theo giờ trong ngày (volume / TB cùng giờ 10 ngày, TradingView); điểm z sửa đổi theo trung vị và MAD (ngưỡng 3,5, NIST); tách mùa vụ trong ngày rồi đặt ngưỡng trên phần dư | Có |

Đánh giá với dữ liệu của mình:
- **Không phần mềm nào công bố luật tự co theo khung thời gian**; ATAS và Jigsaw có tự chỉnh nhưng giấu công thức. Luật "lớn thứ K trong N nến trước" cùng họ với ngưỡng cuốn của Bookmap (trung bình + k × độ lệch chuẩn), nhưng dùng thứ hạng vì lệnh đơn có đuôi rất dài (trung vị 1, lớn nhất 581) làm độ lệch chuẩn nhảy theo một lệnh.
- **Phần trăm volume của nến** (ATAS) và **bội số của trung vị** là điều mình đã thử cho Big Trade (`bt_alt.py`): mật độ lệch theo khung nhiều hơn luật thứ hạng.
- **Gộp chấm sát nhau** (Bookmap Smart) là cùng ý với bước gộp vòng.
- **Volume tương đối theo giờ trong ngày** sẽ trị đúng chỗ còn yếu (nến đầu phiên Mỹ, H1), nhưng cần 10 ngày lịch sử cùng giờ, mà lệnh đơn chỉ có khi chạy sống. Chưa đo; ghi lại làm hướng sau.
- **Kiệt sức = bằng 0 ở cực trị** (định nghĩa của mọi phần mềm) **không khớp CORVEN**: cả 11 dấu CORVEN đều khác 0 ở cực trị (mục 4.2). Không tìm thấy nguồn nào cho luật số "yếu nhưng khác 0".

## 8. Rủi ro và giới hạn

1. **Mẫu CORVEN rất mỏng.** Big Trade: một con số mật độ (25 vòng / 26 nến), không có recall. Kiệt sức: 11 dấu, một chart, tham số chọn trên chính mẫu. Chấm: GC M1 đủ dùng (885 chấm), NQ M1 chỉ dùng được mật độ, GC M5 16 cụm. **Từ M15 trở lên không có mẫu CORVEN nào cho cả ba loại dấu.**
2. **Nến đầu phiên** (lịch sử thuộc phiên khác): vẫn đông hơn bình thường ở cả ba luật. Big Trade có giới hạn 3; chấm thì không (NQ M5 lúc 13:30 UTC khoảng 7–11 chấm).
3. **H1 trở lên**: cửa sổ tối thiểu 5 nến là 5 giờ, vẫn vắt qua phiên. Chấm NQ H1 phiên Á 0,5 so với Âu 1,9 (bộ ít nhiễu).
4. **Nến rất ít giao dịch**: mức nền chấm nhỏ thì sàn quyết định (GC M1 phiên Á 60% số nến); Big Trade có sàn 5. Hàng đợi 5 nến (M30, H1) dễ bị một nến bất thường kéo lệch.
5. **Big Trade chỉ có khi chạy sống**: mở lại chart là mất nền cho tới khi đủ 5 nến sống, trừ khi làm nóng từ nhật ký (5.2). Dữ liệu NQ là 6 phiên chạy lại + 204 nến sống; GC 16 phiên tháng 9 + nhật ký sống đứt quãng. Chạy lại và sống cho phân phối giống nhau trên GC, chưa kiểm được trên NQ.
6. **Chỗ nối hợp đồng**: các đoạn đo đều nằm trong một hợp đồng. Trên mã liên tục `/GC:XCEC`, nến ở chỗ nối có biên độ giả → cửa sổ w và khoảng gộp phình trong N nến sau đó (tự hết sau N nến); volume không bị ảnh hưởng.
7. **MGC / MNQ chưa đo.** Cỡ lệnh và volume mỗi ô khác hẳn; sàn 5 (Big Trade, chấm) có thể sai.
8. **Mật độ không phải mục tiêu tự thân.** Luật thứ hạng ép số vòng mỗi nến gần hằng số, nên một buổi thật sự nhiều lệnh lớn và một buổi vắng trông gần giống nhau về số vòng; khác biệt chỉ còn ở cỡ vòng và con số ngưỡng trên tooltip.
9. Phiên định nghĩa theo giờ UTC cố định; hai tuần lệch giờ mùa đông giữa Mỹ và châu Âu không tách riêng.

## 9. Danh sách script

| File | Việc |
|---|---|
| `common_window.py` | Cửa sổ nền theo khung |
| `inspect_logs.py`, `bt_check.py` | Kiểm nhật ký lệnh đơn; khung dựng từ M1 = khung thật |
| `bt_common.py`, `bt_rule.py` | Nạp nhật ký, phiên; luật Big Trade (bản chuẩn + bản nhanh) |
| `bt_measure.py`, `bt_grid.py`, `bt_alt.py`, `bt_window.py`, `bt_final.py` | Phân phối; quét tham số; luật thay thế, nến đầu phiên, nhật ký sống; cửa sổ theo khung; bảng chốt |
| `bt_corven.py` | Thử khớp 25 vòng CORVEN (thiếu dữ liệu) |
| `dot_rule.py`, `dot_measure.py`, `dot_window.py`, `dot_grid.py`, `dot_hide.py`, `dot_final.py`, `dot_mid.py` | Luật chấm; đo hiện tại; cửa sổ nền; quét công thức; khoảng che; bảng chốt |
| `dot_corven.py`, `dot_corven_m5.py`, `dot_recall.py`, `dot_recall2.py`, `dot_recall3.py` | So với CORVEN: M1 hai mã, M5 26 nến, đường recall / nhiễu |
| `exh_common.py`, `exh_now.py`, `exh_grid.py`, `exh_final.py`, `exh_rule.py` | Kiệt sức: bảng đặc trưng, đo hiện tại, quét, bảng chốt, bản chuẩn |
| `bt_selftest.py`, `dot_selftest.py`, `exh_selftest.py` | Ví dụ nhỏ, bản nhanh = bản chuẩn, file chuẩn |
| `out_*.txt`, `out_*.csv` | Kết quả thô của từng script |

## 10. Đã implement (Opus, 2026-11-24)

Theo đúng spec mục 5. Khác/thêm so với spec:
- Ô số "Sàn tối thiểu (hợp đồng)" cũ chỉ dùng khi tắt "Tự co dãn"; khi bật, sàn theo bộ số (5 / 5 / 9). Ô "Dùng sàn tối thiểu" vẫn tắt được sàn ở cả hai chế độ.
- Big Trade làm nóng + vẽ lại vòng nến lịch sử từ nhật ký (`BigTradeLog.CellsOf`) khi feed không có lệnh đơn.
- Không có ô "Cửa sổ nền (phút)" (giữ 120 trong code, `BaselineWindowMinutes`).

Kiểm C# = Python (khớp từng dấu, 0 lệch):
- Chấm: 6.2 đủ 20 ô (2 bộ × GC/NQ × M1/M5/M15/M30/H1), từng chấm với `dot_golden_*`.
- Kiệt sức: GC M5 6.247 · GC M15 3.293 · NQ M5 7.896 · NQ M30 1.693, từng dấu với `exh_golden_*`.
- Big Trade: NQ M1 5.096 · NQ M15 516 · GC M5 4.120 · GC M30 711, từng vòng với `bt_golden_*` (C# đọc nhật ký do `bt_cs_log.py` dựng, `Golden.dll stophunt --zeromot --btlog ... --minutes ...`).
- Nạp nguội = nạp tăng dần (`Golden.dll inccheck`): GC M5 lệnh đơn giả lập, NQ M1 và NQ M15 từ nhật ký.
- Tắt hết (`--set CellDotAdaptive=false --set AdaptiveBaseline=false --set BigTradeAdaptiveEnabled=false --set ExhTailMedianRatio=0`) = golden cũ.
