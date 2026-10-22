# Vùng Canh Lệnh (VCL) — indicator hỗ trợ/kháng cự cho scalp vàng M1

Mục tiêu người học (2026-10-22): một indicator vẽ **vùng hỗ trợ/kháng cự gần nhất + xa vừa phải** để (1) biết chỗ canh lệnh,
(2) đặt kỳ vọng TP/SL. Vùng phải **vừa đủ**: không quá dài, không quá mỏng; độ rộng mỗi vùng khác nhau vì là vùng giá.
Quy trình: Fable thiết kế → Opus implement + đo → Fable review → sửa, tối đa 5 vòng.

## 0. Những gì đã biết (đọc trước khi làm, đừng đo lại cái đã đo)
- `benzo-trader/research/report/SR-KET-QUA.md` (65 phiên GCZ26, 07-23→10-21): **không loại mức nào** (swing, đỉnh/đáy/đóng phiên trước,
  VA hôm qua, VA Âu, số tròn, VWAP) có tỉ lệ *bật* cao hơn mức ngẫu nhiên quá sai số, theo định nghĩa Osler 2000 và Chung&Bellotti 2021.
  Số lần bật trước và tuổi mức không đổi kết quả. HVN cũng vậy (474 phiên, memory).
- Hệ quả thiết kế: **không hứa "giá tới vùng thì đảo chiều"**. Giá trị của indicator nằm ở chỗ khác:
  (a) chọn đúng **vài vùng gần nhất** để người học không phải tự vẽ; (b) **độ rộng vùng đúng cỡ nhiễu** để SL đặt ngoài vùng
  không bị quét bởi râu ngẫu nhiên; (c) **vùng kế tiếp là mốc TP thực tế** (giá có đi tới đó trong thời gian scalp hay không).
  ⇒ Thước đo thành công phải là (a)(b)(c), không chỉ "bật %".
- Tài liệu bên ngoài đã đọc (Fable, 2026-10-22):
  - Garzarelli et al. 2014 (Sci. Rep.) — cổ phiếu LSE: xác suất bật tăng theo số lần bật trước, **nhưng chỉ ở thang < ~3 phút**, biến mất ở thang lớn hơn.
    Trên dữ liệu vàng của ta không thấy hiệu ứng này (bảng swing · đã bật 1/2+ lần).
  - Bourghelle & Cellier (Euronext), Chiao 2009 (TAIFEX 100 triệu lệnh limit), Zhang: lệnh limit **dồn ở số tròn** (bội 100 > 50 > 10) ⇒ số tròn
    là chỗ có lệnh thụ động thật. Trên GCZ26 90 ngày: số tròn 10$/5$ bật ≈ ngẫu nhiên. Chưa đo bội 50$/100$ (ít ca).
  - Osler 2000: mức DUY NHẤT có lợi thế là mức do bàn giao dịch công bố (có thông tin lệnh khách) — tức **mức có bằng chứng lệnh thụ động**,
    không phải mức vẽ từ giá quá khứ. ⇒ Ý tưởng mới duy nhất đáng thử: dùng **footprint từng mức giá** làm bằng chứng lệnh thụ động (mục 2.1-E).
  - Thực hành (LuxAlgo "level clustering", các script TradingView): đường ống chuẩn = ứng viên → gộp theo khoảng cách ×ATR → chấm điểm
    (số chạm × suy giảm theo tuổi × trọng số loại) → giữ vài vùng mạnh nhất; có script tự dò ngưỡng gộp để ra đúng số vùng mục tiêu.
    Không nguồn nào có backtest.
  - Scalper vàng M1 (blog pro-scalper, vantage…): hay dùng đỉnh/đáy phiên trước, biên Á (00:00-07:00 GMT), VWAP neo London/NY, số tròn 50$.
    Không có bằng chứng số.

## 1. Dữ liệu
- **Chỉ dùng** `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260816-20260915_29d2h.csv` + `_bars.csv` (giờ UTC, ~28.9k nến M1, ~21 phiên).
- Dùng `benzo-trader/research/kernel.py` (load_bars, session_table, build_profiles, vwap_series, median_range, zigzag, value_area…).
  Nguyên tắc cứng của kernel: **không nhìn trước**. Mọi vùng tại nến i chỉ dùng nến ≤ i.
- Tách thời gian: TRAIN = 14 phiên đầu, TEST = phiên còn lại. Mọi bảng in cả 2 cột. n nhỏ ⇒ luôn in ± sai số.
- Đơn vị: 1 giá = 1 USD = 10 tick. u = trung vị biên độ M1 50 nến (kernel.median_range).

## 2. Thiết kế thuật toán (vòng 1)

### 2.1 Ứng viên (mỗi ứng viên = giá, loại, thời điểm sinh, trọng số thô)
- A. **Swing M1** k=5 (zigzag kernel hoặc pivot) — hiệu lực 2 phiên.
- B. **Swing M5** k=3 (tính từ nến M5 gộp) — trọng số cao hơn A.
- C. **Mốc phiên**: đỉnh/đáy/đóng phiên trước, VAH/VAL/POC hôm qua, POC trần (naked) ≤ 3 cái, đỉnh/đáy biên Á (sm < 450) và VA Âu sau khi chốt.
- D. **Số tròn**: bội 10$ (trọng số thấp), bội 50$ (cao), bội 100$ (cao nhất).
- E. ⭐ **Mức lệnh lớn từ footprint** (ý tưởng mới): trong file từng mức giá, mức có `volume` ≥ p99 của mức-giá trong 3 phiên gần nhất
  **và** lệch phe (|delta|/volume ≥ 0,6) hoặc `max_one_trade` lớn ⇒ coi là dấu vết lệnh thụ động lớn. Giữ mức khi giá chưa đóng xuyên
  qua nó ≥ 2u. Đây là ứng viên duy nhất có "thông tin lệnh" theo nghĩa Osler — phải đo riêng.

### 2.2 Gộp thành vùng
- Sắp theo giá, gộp đơn liên kết (single-linkage) khi khoảng cách ≤ **1,0u** (thử thêm 0,7u và 1,5u, báo cả 3).
- Biên vùng = min/max ứng viên trong cụm, đệm thêm **0,5u** mỗi phía. **Kẹp độ rộng vào [1u, 4u]**: cụm quá rộng thì tách tại khe lớn nhất.
- Mỗi vùng ghi: điểm = Σ (trọng số loại × suy giảm theo tuổi × (1 + 0,3 × số lần đã chạm)); số loại ứng viên khác nhau = **mức hợp lưu**.
- Trọng số loại khởi điểm (vòng 1, sẽ hiệu chỉnh bằng số ở vòng 2): A 1 · B 2 · C 2 (POC trần 3) · D 1/2/3 · E 2.
- Suy giảm: ×0,5 sau 2 phiên với A/B/E; C sống 1 phiên (trừ POC trần); D không suy giảm.
- **Vùng chết** khi giá đóng xuyên qua cả vùng ≥ 1u ⇒ chuyển vai (hỗ trợ↔kháng cự) với điểm ×0,7; chết hẳn nếu bị xuyên 2 lần.

### 2.3 Chọn vùng hiển thị (mỗi nến đóng)
- Giữ **2 vùng gần nhất phía trên + 2 phía dưới** giá đóng, cộng **1 vùng "xa vừa phải"** mỗi phía = vùng mạnh nhất trong khoảng
  [2u, 1,5 × biên độ phiên trước] tính từ giá. Tối đa 6 vùng trên chart.
- Chống nhấp nháy: vùng đang hiển thị chỉ bị thay nếu vùng mới có điểm > 1,2 × vùng cũ hoặc vùng cũ chết.

## 3. Phép đo (bắt buộc đủ, có đối chứng, có TRAIN/TEST)
Đối chứng cho mọi phép đo: **vùng giả** = cùng số vùng, cùng độ rộng, đặt ngẫu nhiên trong biên phiên trước ±2 giá, lặp 50 lần (như `sr_measure.py`).
1. **Bật/xuyên (Chung&Bellotti, vào dải bằng giá đóng)** — chỉ để đối chiếu với kết quả cũ; kỳ vọng ≈ đối chứng. Báo theo từng loại ứng viên
   và theo mức hợp lưu (1, 2, ≥3 loại).
2. **Độ rộng vs nhiễu**: với mỗi lần giá vào vùng rồi bật, đo "râu xuyên quá biên xa" (max xâm nhập vượt biên vùng, tính bằng u). Mục tiêu: SL đặt ở
   biên xa + 0,5u thì ≤ 15% ca bật bị quét oan. Báo phân vị 50/85/95 của xâm nhập.
3. **TP tới vùng kế tiếp**: tại mỗi lần bật khỏi vùng, TP = cạnh gần của vùng kế tiếp cùng hướng, SL = biên xa + 0,5u. Đo: % chạm TP trước SL,
   R trung bình (TP/SL distance), thời gian tới TP (phút). So với đối chứng vùng giả. Tách theo khoảng cách TP (≤3u / 3-6u / >6u).
4. **Vệ sinh chart**: số vùng trung bình hiển thị, độ rộng trung vị (u và USD), tỉ lệ nến mà giá nằm **trong** vùng (mục tiêu < 25%),
   số lần đổi vùng/giờ (nhấp nháy), % thời gian có đủ vùng cả 2 phía.
5. **Bảng đóng góp từng loại ứng viên**: với từng loại A-E, bật% − đối chứng, xâm nhập p85, TP% — để vòng 2 cắt loại vô dụng.

## 4. Giao nộp vòng 1
- `vung-canh-lenh/research/vcl.py` — thuật toán + mọi phép đo, chạy `python vcl.py` ra `report/VCL-VONG-1.md` (bảng + nhận xét ngắn).
- `vung-canh-lenh/research/ve_vcl.py` — vẽ 4 phiên (2 TRAIN, 2 TEST) nến M1 + vùng (PNG, Pillow/matplotlib) vào `report/img/`, để Fable nhìn.
- `vung-canh-lenh/research/test_vcl.py` — test không nhìn trước (vùng tại i không đổi khi cắt dữ liệu tại i), gộp/kẹp độ rộng, chuyển vai.
- Viết nhận xét **trung thực**: cái gì ≈ đối chứng thì nói thẳng. Không chọn tham số bằng TEST.
- Chưa port C#. Port Quantower khi thiết kế ổn (vòng ≥3).
