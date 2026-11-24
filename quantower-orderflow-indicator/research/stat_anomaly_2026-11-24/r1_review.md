# Review vòng 1 (Fable, 2026-11-25) — chế độ ngưỡng "Không theo CORVEN"

> Đọc `R1-KET-QUA.md`, toàn bộ script `sa_*.py`, và tự chạy 4 script kiểm nhỏ (`rv1_chk1.py` … `rv1_chk4.py`, cùng thư mục).
> Kết luận: **chưa đủ để viết spec C#**. Hướng đã rõ, nhưng luật cuối (giờ Chicago + dự phòng khi thiếu lịch sử) chưa được cài thành bản chuẩn từng nến và chưa có số chuẩn để so C#. Cần một vòng đo hẹp nữa (mục 6).
> Mọi thứ ở đây vẫn là **định nghĩa hiển thị**, không phải lợi thế giao dịch.

## 1. Số của vòng 1 có tin được không

| Việc kiểm | Cách kiểm | Kết quả |
|---|---|---|
| Ngưỡng có đúng công thức, có nhìn tương lai không | Tự tính lại ngưỡng `cung_gio_K10_lc_p2` bằng vòng lặp thô trên bảng ô gốc, 120 nến ngẫu nhiên (NQ M5, GC M15), không dùng code của Opus | Lệch 0 / 120. Tập tham chiếu chỉ gồm ngày giao dịch **trước** hôm đó |
| Rò rỉ tương lai trong code | Đọc `sa_dot_rules.py`, `sa_common.py`: mặt bằng, biên độ, cửa sổ gộp đều lấy từ nến trước; nến đóng nộp sau khi đã xét; selftest cắt dữ liệu lệch 0 | Không thấy rò rỉ. Hai thước nhìn lại có dùng volume phía sau, nhưng chỉ để chấm điểm |
| "20 ô lớn nhất ngày" NQ chỉ 0,989 | Tách ô sót theo nến có / chưa có ngưỡng | NQ M5: sót 5 / 440 ô, **cả 5 nằm ở nến chưa có ngưỡng**. Chỉ tính nến có ngưỡng: 1,000. Đúng như Opus ghi |
| Mốc đối chứng | Số cũ 80.386 / 39.918 / 62.768 ra lại đúng | Lớp gộp và cách đọc dữ liệu không lệch |

Các con số lớn đều có lý do cơ chế, không phải lỗi:
- `cuon` nổ quá mức ở khung lớn (NQ M15 khớp 1,9–3,2): cửa sổ ngắn vắt qua lúc volume đang tăng, ngưỡng luôn chạy sau.
- `z_log` nổ dưới mức (0,2–0,6): volume là số nguyên nhỏ, đuôi không theo phân phối chuẩn.
- `ky_luc` khớp gần 1,0: mức danh nghĩa của nó đúng theo cách dựng, nhưng sót cực trị nhiều ở NQ (0,62–0,95).

## 2. Lỗi phương pháp tìm thấy ở vòng 1

1. **Big Trade, tiêu chí "20 ô lớn nhất ngày" bị hỏng bởi ngày cụt.** Nhật ký NQ có 7 "ngày", ngày cuối chỉ 60 nến M1; GClive có ngày 19, 77, 116 nến. 20 ô lớn nhất của một ngày cụt là ô tí hon, nên **mốc cố định 10 cũng chỉ đạt 0,893**. Khi chỉ tính ngày có từ 400 nến M1 trở lên (`rv1_chk4.py`): `cuon_T240_p1` trên NQ đạt 0,992 (M1 / M5 / M15), không phải 0,886–0,929.
2. **Big Trade, "Khớp theo giờ" trên GClive không thể đạt.** GClive chỉ có 19 giờ có nến, tiêu chí đòi 20 / 24. Số "0 cấu hình đạt" ở đó là do tiêu chí, không phải do luật.
3. **Big Trade, cửa sổ ngắn hết mẫu ở khung lớn.** `cuon_T120_p1` trên GC M15 chỉ 78% nến có ngưỡng (8 nến × 88 ô ≈ 700 mẫu, sát mức cần 500); mức 0,5% còn 72–81%. Bảng 8.4 trộn "sót vì chưa có ngưỡng" với "sót vì ngưỡng cao".
4. **Tiêu chí "Nến đầu phiên" đặt sai.** Nó trượt ở cả mốc đối chứng, và nến gây trượt là 13:30 / 14:30 UTC, lúc có tin và mở cửa cổ phiếu Mỹ. Volume lúc đó lớn thật; nhiều bóng hơn là đúng định nghĩa.
5. **Đoạn kiểm không còn "sạch".** Opus xếp hạng "trượt ít nhất" trên đoạn kiểm, và các phép thử của tôi ở mục 4 cũng chạy trên đoạn kiểm. Vòng 2 phải báo **cả đoạn chọn**; đoạn chọn giờ là đoạn xác nhận (chưa ai dùng nó để xếp hạng luật cuối).
6. **`cung_gio` kiểu λ không được đo ở bước 4.** Nó trượt Khớp chung ở đoạn chọn (NQ M15: 1,38–1,47) nên bị loại đúng luật. Hệ quả: chỉ kiểu p (phần trăm ô) còn trong cuộc.

## 3. Hai chỗ tôi nới tiêu chí, và lý do

PLAN 4.5 yêu cầu ghi riêng nếu nới sau khi xem số. Cả hai đều là nới **sau khi đã thấy kết quả**, người đọc nên biết điều đó.

- **"Nến đầu phiên": bỏ đạt / trượt, chỉ báo cáo.** Lý do ở mục 2.4.
- **"Khớp theo ngày": với phương án cùng giờ chỉ báo cáo.** Định nghĩa đã chốt là "so với cùng giờ những ngày trước". Theo định nghĩa đó, ngày vắng ít bóng hơn và ngày sôi động nhiều bóng hơn là **đúng**, không phải lệch. Tiêu chí này phạt chính điều đó. Số đo thật (đoạn kiểm, tỉ lệ nổ từng ngày / 2%): NQ M1 từ 0,43 đến 1,77; GC M5 từ 0,49 đến 1,54.

Các tiêu chí còn lại giữ nguyên ngưỡng.

## 4. Phương án thắng

### 4.1 Chấm Bid/Ask: cùng khung giờ các ngày trước, kiểu phần trăm ô

Theo tiêu chí PLAN (4.1 + 4.3), `cung_gio … p2` trượt ít nhất (3 lần trên 6 ô), và cả 3 lần trượt đều đến từ **nến chưa có ngưỡng**, không phải từ ngưỡng. `lai_mean_K20_p2` cũng trượt 3 nhưng nhiễu cao hơn 10 lần (1–3% so với 0,1–0,2%) và cần số thực. `cuon`, `z_log` không qua bước 3. `ky_luc` sót cực trị ở NQ.

Tôi đã thử nhanh ba ý trước khi giao vòng 2 (`rv1_chk2.py`, đoạn kiểm, mức 2%):

| Biến thể | NQ M1: nến có ngưỡng · 20 ô lớn nhất ngày · cực trị rõ | NQ M15 (như trước) · 5 ô lớn nhất phiên | GC M5 |
|---|---|---|---|
| Vòng 1 (giờ UTC, không dự phòng) | 0,994 · 0,989 · 0,991 | 0,994 · 0,991 · 0,989 · 0,957 | 0,995 · 1,000 · 0,997 |
| + dự phòng cuốn 120 phút khi thiếu lịch sử | 1,000 · 1,000 · 0,993 | 1,000 · 1,000 · 0,991 · 0,966 | 1,000 · 1,000 · 0,998 |
| Khung giờ tính theo **giờ Chicago** | 1,000 · 1,000 · 1,000 | 1,000 · 1,000 · 0,996 · 0,978 | 1,000 · 1,000 · 0,998 |
| + chặn thêm "phải lọt 5% lớn nhất của 120 phút vừa rồi" | 1,000 · 1,000 · 0,978 | 1,000 · 1,000 · 0,952 · 0,957 | 1,000 · 1,000 · 0,998 |

Đọc:
- **Giờ Chicago** xóa hẳn lỗi "khung giờ mới sau đổi giờ" (sàn CME chạy theo giờ Chicago, giờ nghỉ luôn 16:00–17:00). Đây là cách sửa gốc.
- **Dự phòng** vẫn cần cho 3 ngày đầu chart. Ngưỡng dự phòng so với ngưỡng chính (NQ M1, trung vị · phân vị 10–90): cuốn 120 phút 0,90 · 0,67–1,25; cuốn 240 phút 0,96 · 0,67–2,18; cuốn 480 phút 1,00 · 0,67–2,67. Cuốn 120 phút bám sát nhất.
- **Lớp chặn thêm bị loại**: nó làm sót cực trị (NQ M15 0,991 → 0,952) để đổi lấy rất ít.

Điểm yếu thật của phương án cùng giờ, phải viết cho người học:
- **Tuần chuyển hợp đồng** (NQ toàn bộ file, M5): tỉ lệ nổ thô ngày 14/09 gấp 17 lần mức danh nghĩa, nhưng sau gộp chỉ là **3,1 chấm/nến so với 1,5–2 ngày thường**, và về mức thường sau khoảng 6 ngày. Chấp nhận được, không cần cơ chế riêng.
- **3 ngày đầu chart** chạy bằng ngưỡng dự phòng.
- **Số chấm tăng theo khung** (đoạn kiểm, mức 2%, chấm/nến M1 / M5 / M15 / M30 / H1): GC 0,35 / 0,81 / 1,25 / 1,59 / 1,90; NQ 0,88 / 1,65 / 2,22 / 2,51 / 2,71. Nằm giữa bộ Ít nhiễu và bộ Không sót đang chạy.
- **Không cần sàn**: ở NQ M1 không nến nào có ngưỡng dưới 8 hợp đồng; ở GC M5 phân vị 1 của ngưỡng là 15; không có chấm ≤ 5 hợp đồng.

### 4.2 Big Trade: phân vị cuốn trên lệnh đơn

- `cung_gio` cho Big Trade **không dùng được ngoài đời**: trên nhật ký sống chỉ 49% nến có ngưỡng.
- `lai` bị loại: ở GC không mặt bằng nào ổn định hơn lệnh đơn thô; ở NQ trượt nhiều hơn `cuon`.
- `ky_luc` nổ quá nhiều ô nhỏ ở M1 (8–14% vòng ≤ 3 hợp đồng).
- Còn lại `cuon` mức 1%. Số sau khi bỏ ngày cụt (`rv1_chk4.py`):

| Nhật ký | Cửa sổ | Ô vượt theo phiên Á / Âu / Mỹ (danh nghĩa 1%) | 20 ô lớn nhất ngày · cực trị rõ | Ngưỡng (phân vị 10 / 50 / 90) |
|---|---|---|---|---|
| GC M5 (đoạn kiểm) | 240 phút | 0,98 / 0,96 / 0,93 | 1,000 · 1,000 | 9 / 11 / 14 |
| NQ M1 (6 phiên) | 120 phút | 0,69 / 0,98 / 0,97 | 0,992 · 0,992 | 4 / 6 / 11 |
| NQ M1 | 240 phút | 0,54 / 1,06 / 1,04 | 0,992 · 0,982 | 5 / 6 / 10 |
| NQ M1 | 480 phút | 0,39 / 1,17 / 1,30 | 0,992 · 0,962 | 5 / 8 / 10 |
| NQ M15 | 120 phút | 0,81 / 1,31 / 1,14 | 0,992 · 0,982 | 7 / 12 / 23 |
| NQ M15 | 480 phút | 0,45 / 1,47 / 1,44 | 0,992 · 0,942 | 8 / 15 / 21 |

Đọc: cửa sổ càng ngắn càng bám phiên (NQ phiên Á: 0,69 với 120 phút, 0,39 với 480 phút), nhưng cửa sổ ngắn lại hết mẫu ở khung lớn (mục 2.3). Vòng 2 phải đo cách nới cửa sổ theo số mẫu.
Kết luận về Big Trade vẫn yếu hơn chấm: NQ chỉ 6 phiên, không có đoạn kiểm.

## 5. Còn thiếu gì trước khi viết spec

1. Luật chấm cuối (giờ Chicago + dự phòng) chưa có bản chuẩn từng nến, chưa chạy đủ 10 ô × 2 đoạn.
2. Chưa chốt bằng số: 5 hay 10 ngày tham chiếu; có gộp khung giờ lân cận không; cần mấy ngày thì dùng ngưỡng chính; dự phòng 120 hay 240 phút.
3. Chưa đo khung lạ (M3, M10, H4) và chart nạp ít ngày.
4. Big Trade: chưa đo nhật ký chỉ có vài giờ mỗi ngày (cách dùng thật của người học: chỉ mở chart buổi tối), chưa chốt cửa sổ.
5. Chưa có **số chuẩn Python đọc đúng file CSV mà Golden đọc**, nên chưa có gì để so C#.

## 6. Việc vòng 2 (Opus; chỉ Python, không sửa C#, không commit)

Script mới đặt tiền tố `sa2_`, kết quả `out_r2_*.csv`, báo cáo `R2-KET-QUA.md`. Dùng lại `sa_common.py`, `sa_eval_lib.py`, `sa_oracle_lib.py`.

### 6.1 Luật chấm "thống kê" (bản chuẩn + bản nhanh)

- **Giờ Chicago**, tính bằng luật cố định (không dùng thư viện múi giờ): từ 08:00 UTC chủ nhật thứ hai của tháng 3 tới 07:00 UTC chủ nhật đầu tiên của tháng 11 là UTC − 5, ngoài ra UTC − 6.
- **Ngày giao dịch** = ngày của (giờ Chicago + 7 giờ). **Khung giờ** = `floor(phút trong ngày Chicago / W)`, `W = max(30, số phút một nến)`, số khung = `ceil(1440 / W)`; lân cận quay vòng.
- **Ngưỡng chính**: gộp giá trị bên > 0 của khung giờ đó (và hai khung lân cận nếu bật), mỗi khung lấy K ngày giao dịch gần nhất **trước hôm nay**. Cần khung chính có ít nhất `so_ngay_toi_thieu` ngày. `K' = floor(p × số mẫu)`, cần `số mẫu × p ≥ 5`; ngưỡng = giá trị lớn thứ K' + 1; nổ khi lớn hơn hẳn.
- **Ngưỡng dự phòng** (khi ngưỡng chính chưa có): cùng công thức trên `n = max(5, floor(T / phút + 0,5))` nến đóng gần nhất. Cả hai chưa có thì không nổ.
- Gộp ±w như vòng 1. Không che, không sàn.
- Cấu hình **gốc**: giờ Chicago, K = 10, có lân cận, tối thiểu 3 ngày, dự phòng T = 120, p = 2%.
- Chỉ đổi **một yếu tố mỗi lần** so với gốc: giờ UTC; K = 5; K = 20; không lân cận; tối thiểu 1 ngày; tối thiểu 2 ngày; T = 240; p = 1%; p = 0,5%. Cộng hai mốc đối chứng `dc_dang_chay_*`. Tổng 12 cấu hình.

### 6.2 Bảng điểm chấm (cả đoạn chọn lẫn đoạn kiểm, GC và NQ, M1 … H1)

- Tiêu chí 4.1 (Khớp chung, theo phiên, theo giờ) và 4.3 (cả năm) giữ nguyên ngưỡng; "Khớp theo ngày" và "Nến đầu phiên" chỉ báo cáo. Mỗi cấu hình: số lần trượt trên 6 ô (GC, NQ × M1, M5, M15) của **từng đoạn**, kèm trượt cái gì.
- Chấm/nến theo phiên và theo khung; phân vị 50 / 95 / lớn nhất số chấm một nến; số vượt thô mỗi nến (dùng cho ô "Nổ ở mọi mức giá").
- Chấm/nến từng ngày: nhỏ nhất / phân vị 10 / 50 / 90 / lớn nhất, kèm tên ngày ít nhất và nhiều nhất.
- Ngưỡng theo phiên (phân vị 10 / 50 / 90) và tỉ lệ nến có ngưỡng < 5.
- Tuần đổi giờ 26–30/10 và 02–06/11: số giờ có tỉ số khớp trong 0,5–2, giờ Chicago so với giờ UTC.
- Chuyển hợp đồng (NQ toàn bộ file, M1 / M5): chấm/nến từng ngày 07/09 → 25/09.
- **Chart nạp ít ngày**: với mỗi mã, M1 / M5 / M15, cắt dữ liệu chỉ còn 8 ngày giao dịch cuối; so chấm của từng ngày với khi nạp toàn bộ (số chấm chung / số chấm hợp), cho tối thiểu 1 / 2 / 3 ngày và T = 120 / 240.
- **Khung lạ** M3, M10, H4 (dựng từ bảng M1): tỉ lệ nến có ngưỡng, chấm/nến, Khớp chung.
- So tham khảo với chart CORVEN cho cấu hình gốc, nếu dùng lại được script ở `../dot_floor_2026-11-24` trong 30 phút: chỉ báo số, không chỉnh gì theo nó.

**Luật chọn viết trước** (Fable áp ở vòng 3, không bàn lại):
- Một biến thể thay cấu hình gốc khi tổng số lần trượt (hai đoạn cộng lại) **ít hơn** gốc. Bằng nhau thì giữ gốc; riêng K = 5 thắng khi bằng nhau (cần ít lịch sử hơn).
- Tối thiểu mấy ngày và T dự phòng: chọn tổ hợp có tỉ lệ chấm trùng cao nhất ở phép thử "chart nạp ít ngày"; bằng nhau (lệch dưới 0,01) thì tối thiểu 3 ngày, T = 120.
- Mức mặc định là 2% nếu cấu hình gốc không trượt gì ngoài hai tiêu chí đã chuyển sang báo cáo; nếu trượt thì báo rõ, Fable quyết.

### 6.3 Big Trade

- Sửa thước: "20 ô lớn nhất ngày" chỉ tính ngày có ≥ 400 nến M1; "5 ô lớn nhất phiên" chỉ tính (ngày × phiên) có ≥ 60 nến M1; "Khớp theo giờ" đạt khi ≥ 5/6 số giờ có nến nằm trong 0,5–2. Tách "sót vì chưa có ngưỡng" khỏi "sót vì ngưỡng".
- Luật: phân vị cuốn trên lệnh đơn, p ∈ {1%; 0,5%}, ba kiểu cửa sổ, T ∈ {120; 240}:
  - **A**: `n = max(5, floor(T / phút + 0,5))` nến có số liệu gần nhất (như vòng 1).
  - **B**: như A, nhưng nếu chưa đủ `5 / p` mẫu thì lấy thêm nến cũ hơn cho tới khi đủ, tối đa `floor(1380 / phút + 0,5)` nến.
  - **C**: như B, thêm luật bỏ nến cũ quá 720 phút so với nến đang xét.
- Đo trên GC (chọn / kiểm), NQ (6 phiên), GClive, M1 … H1: tỉ lệ nến có ngưỡng, Khớp chung và theo phiên, ba tiêu chí không sót, nhiễu, vòng/nến theo phiên, phân vị 50 / 95 / lớn nhất số vòng một nến, ngưỡng theo phiên.
- **Nhật ký chỉ có buổi tối** (cách dùng thật): từ nhật ký GC và NQ, giữ lại mỗi ngày chỉ 12:00–18:00 UTC rồi chạy lại. Báo: số nến đầu mỗi buổi chưa có ngưỡng, và tỉ lệ vòng trùng với khi có nhật ký đầy đủ (trên các nến chung).
- Hai mốc đối chứng như vòng 1.

**Luật chọn viết trước:** trong các tổ hợp có Khớp chung 0,8–1,25 và nhiễu ≤ 5% ở GC đoạn kiểm lẫn NQ, lấy tổ hợp có giá trị **nhỏ nhất** (qua GC kiểm, NQ, GClive, và phép thử buổi tối; M1 / M5 / M15) của "20 ô lớn nhất ngày" là cao nhất. Bằng nhau (lệch dưới 0,005): ưu tiên A rồi B rồi C, T = 240 trước T = 120, p = 1%.

### 6.4 Bản chuẩn đọc đúng dữ liệu của Golden + số chuẩn

- `sa2_ref.py <csv footprint> <phút> <tick> [--btlog <nhật ký>] [--set ten=gia_tri …] --marks <file>`: đọc **đúng file CSV mà `Golden stophunt --levels` đọc** (và `--btlog`), đi từng nến theo thứ tự thời gian, chỉ dùng cấu trúc C# sẽ có (mảng đếm theo khung giờ × ngày, hàng đợi nến cho dự phòng, hàng đợi biên độ cho w và g), ghi dấu đúng định dạng `--marks` của Golden. Đọc `perf/Golden/Program.cs` để khớp: cách đọc cột, nến cuối file tính là đang chạy hay đã đóng, tên loại dấu, múi giờ của cột thời gian.
- Tự kiểm: bản chuẩn này = bản nhanh của 6.1 / 6.3 từng dấu trên ít nhất GC M5, GC H1, NQ M1, NQ M15; kiểm cắt dữ liệu (không nhìn tương lai); kiểm nạp ít ngày cho ra đúng như bản nhanh.
- In bảng **số chuẩn** cho cấu hình gốc và cho p = 1%: tổng chấm đỏ, tổng chấm xanh trên `tf/fp_{GC,NQ}_m{1,5,15,60}.csv`; tổng vòng Big Trade trên `btlog_{NQ_M1,NQ_M15,GC_M5,GC_M30}.csv` (luật A, T = 240, p = 1%, và luật thắng theo 6.3 nếu khác). File trong thư mục tạm thiếu thì dựng lại bằng `../nq_calib_2026-11-24/tf_csv.py`. Ghi kèm lệnh đã chạy và mã băm (sha1) của từng file đầu vào.
- Ghi vào báo cáo mọi chỗ bản chuẩn phải đoán về hành vi C# (ví dụ volume không nguyên, nến không có ô nào, ô có volume nhưng Bid = Ask = 0).

### 6.5 Điều kiện xong vòng 2

- Mọi tự kiểm in ĐẠT.
- `R2-KET-QUA.md` có: bảng điểm 6.2 (hai đoạn), bảng 6.3, bảng số chuẩn 6.4, mục bất thường. Opus **không** chọn mặc định; chỉ áp luật chọn đã viết và ghi kết quả áp luật thành một dòng riêng cho từng luật.
