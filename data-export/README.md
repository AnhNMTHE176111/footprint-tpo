# 📊 Kho dữ liệu — ĐỌC FILE NÀY TRƯỚC KHI CHỌN DỮ LIỆU TEST

> Cập nhật 2026-08-19. Mọi việc nâng cấp indicator / signal / backtest **phải bắt đầu từ đây**,
> đừng bốc đại file trong `data-export/`.

## ⭐ NGUỒN CHUẨN — dùng cái này

**`data-export/data-footprint/fp_GC_XCEC_Time_*.csv`** (kèm file `_bars.csv` cùng tên)

Đây là export đầu tiên có **khối lượng thật**. Đo trên 27 phiên 2026-07-20 → 08-19:

| | nến M1/phiên | hợp đồng/phiên | mức giá/phiên |
|---|---|---|---|
| ⭐ `fp_GC_XCEC_*` | **1.373** | **101.366** | 20.117 |

## ⛔ Các file CŨ — đã đo là quá mỏng, ĐỪNG dùng để kết luận

| File | Ngày | nến M1/phiên | **hợp đồng/phiên** | so với ⭐ |
|---|---|---|---|---|
| `Data_Footprint_Export.csv` | 128 (02-03→07-31) | 201 | **657** | **mỏng hơn 154×** |
| `27-7/sample.csv` | 112 (01-29→07-28) | 692 | 2.804 | mỏng hơn 36× |
| `data-footprint/fp_GCZ26_*_20260802_*.csv` | 21 (07-03→07-31) | 758 | 3.564 | mỏng hơn 28× |
| `data-footprint/Data_Footprint_Export.csv` | 23 (06-30→07-30) | 46 | 3.168 | mỏng hơn 32× |
| `data-footprint/fp_GCZ26_*_571d2h.csv` | 271 (2024-08→2026-02) | **8** | **10** | vô dụng |

### 🔴 Hệ quả phải nhớ
**Toàn bộ nghiên cứu volume trước 2026-08-19 chạy trên `Data_Footprint_Export.csv` —
tức chỉ 657 hợp đồng/phiên, dưới 1% khối lượng thật.** Gồm `MEASURE-LEVELS-RESULTS.md`
(21 rổ, kết luận "không mốc nào vượt nền 40%"), các đo HVN/POC, và phần hiệu chỉnh B8.

Kết luận "không có lợi thế" từ những đo đó **chưa đáng tin** — profile dựng từ 657 hợp đồng
gần như là nhiễu. Phải **chạy lại trên nguồn ⭐** trước khi tin. Bằng chứng cụ thể: bướu HVN
trên dữ liệu dày nhọn hơn hẳn (82% bướu có nền ≤1 giá, so với 66% trên file mỏng;
phân vị 75 của bề rộng nền tụt từ **8,3 giá xuống 0,7 giá**).

## ⚠️ Bẫy của mã liên tục `/GC:XCEC` — CHỖ NỐI HỢP ĐỒNG

`/GC:XCEC` **nối thô, KHÔNG bù chênh lệch giá**. Đo được trên chính dữ liệu này:

- **2026-07-29, lúc 20:59 → 22:00** (giờ nghỉ CME): giá nhảy **+61,2 giá** trong một bước.
  Đó là lúc mã liên tục nhả GCQ26 và bám sang GCZ26, **không phải thị trường chạy**.
- Trước chỗ nối, `/GC:XCEC` thấp hơn `GCZ26` khoảng **+59 giá** đều đặn.
- Phiên 07-29 vì thế có biên độ giả **163 giá** (3994,9 → 4157,9) và bướu HVN mạnh nhất
  rơi vào vùng giá CŨ.

**Phải làm gì:**
- Profile **NGÀY** chứa ngày nối → bỏ ngày đó khỏi thống kê.
- Profile **TUẦN/nhiều phiên** vắt qua chỗ nối → **kết quả sai**, bỏ cả cửa sổ đó.
- Vàng đổi hợp đồng khoảng 2 tháng/lần ⇒ export 2 năm sẽ có ~10-12 chỗ nối. Lọc trước khi đo.
- Cần đo sạch một hợp đồng → dùng file `fp_GCZ26_*` cùng khoảng.

## 🕐 Múi giờ
Export mới ghi **UTC** (`Lệch giờ ghi vào CSV = 0`). Kiểm chứng: giờ nghỉ 1 tiếng của CME
rơi đúng **21:00 → 22:00** trong file. Các indicator C# lại chạy `TzOffset = 7` (UTC+7) —
khi đối chiếu Python ↔ C# phải cộng bù, đừng so thẳng chuỗi giờ.

## 📥 Export dày 2 năm — ĐÃ CÓ

`fp_GC_XCEC_Time_20240801-20260819_748d9h.csv.gz` (60 MB nén / 557 MB thô) +
`_bars.csv.gz` (23 MB / 88 MB). Giải nén trước khi dùng:

```bash
cd data-export/data-footprint
gunzip -k fp_GC_XCEC_Time_20240801-20260819_748d9h.csv.gz
gunzip -k fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv.gz
```

Bản `.csv` giải nén đã được `.gitignore` chặn nên không lo commit nhầm.

Đo được: **529 phiên**, trung vị **143.142 hợp đồng/phiên**, 1.377 nến M1/phiên,
640 ngày lịch có dữ liệu. Sau khi loại ±2 phiên quanh 11 chỗ đổi hợp đồng còn
**474 phiên sạch** — đủ n để kết luận (ngưỡng cần khoảng 235 phiên).

Kết quả đã chạy trên nguồn này: `quantower-tpo-suite/MEASURE-DENSE-RESULTS.md`.

## 🧭 Phân loại file bằng HEADER
| Header bắt đầu bằng | Loại | Dùng cho |
|---|---|---|
| `bar_idx,datetime,price,bid_vol,ask_vol,…` | footprint **từng mức giá** | profile, HVN, imbalance, hấp thụ |
| `bar_idx,datetime,open,high,low,close,…` (`*_bars.csv`) | tổng hợp **theo nến** | backtest, khớp bằng `bar_idx` |
| `DateTime,UTC,Open,High,…,VSA…` | export cũ của chart | script Python cũ trong `research/` |
| `TPO-chart-*.csv`, `tpo-data/` | TPO ngày / M30 | thiên hướng đa phiên |
| `signals/*.csv` | log signal indicator ghi lúc chạy | đối chiếu Python ↔ C# |
