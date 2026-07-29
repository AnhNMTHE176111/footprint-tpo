# GĐ3 — Kiểm kê năng lực dữ liệu (feature nào test được offline?)

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | high |
| **Cần trước** | — (độc lập, chạy song song GĐ1/GĐ2 được) |
| **Chi phí** | trung bình |
| **Output** | `quantower-entry-signal/research/DATA_CAPABILITY.md` |

Vì sao pha này phải đứng **trước** pha thiết kế: nếu không biết dữ liệu chịu được gì, GĐ4 sẽ thiết kế feature
không kiểm được, và GĐ6/GĐ7 sẽ đi vào ngõ cụt. Effort `high` vì phải **chứng minh** múi giờ / định danh sản phẩm
bằng cơ chế, không phải đọc tên file.

---

=== PROMPT ===

Việc của bạn: kiểm kê toàn bộ dữ liệu có trong repo và trả lời dứt điểm **"feature nào kiểm được offline, trên bộ nào, trong bao nhiêu tháng"**. Output duy nhất: `quantower-entry-signal/research/DATA_CAPABILITY.md`.

Đây là pha **đo lường**, không phải pha thiết kế chiến lược. Không đề xuất setup, không backtest chiến lược.

## Đã kiểm sẵn (dùng luôn, không cần kiểm lại)

| File | Dòng | Khoảng thời gian | Ghi chú |
|---|---|---|---|
| `data-export/27-7/_GCQ26XCEC dxFeed ... 11_3_2025 ... 7_27_2026 ....csv` | — | 2025-11-02 23:22 → 2026-07-27 15:56 | sep=`;`, cột: `Time left;Time right;Open;High;Median;Low;Close;Typical;Volume;Quote asset volume;Weighted` — **chỉ OHLCV, KHÔNG có delta** |
| `data-export/fp-m1-6-month.csv` | 99.679 | 2026-01-27 18:50 → 2026-07-25 03:59 | **CÓ delta/bid/ask theo nến**, cột `UTC=+07:00`, ~37 cột |
| `data-export/fp-m1-1-month-data.csv` | 28.072 | — | cùng khuôn fp-m1 |
| `data-export/TPO-chart-daily.csv` | 953 | — | có `TPO,VAH,VAL,POC,Midpoint,RF,TPO Up,TPO Down,POC Count,VA Volume,Range,VA range,IB High,IB Low,IB range,IB Volume` |
| `data-export/tpo-chart-m30.csv` | 3.017 | — | cùng bộ cột TPO như trên |
| `data-export/27-7/perlevel_m1_clean.pkl` | 25MB | — | footprint **từng mức giá**, nhưng **chỉ 25 phiên rời rạc** (theo V6_PLAN §10) |
| `data-export/27-7/sample.csv` (37MB), `sample_bars.csv` (9MB) | — | — | **chưa rõ là gì → phải xác định** |

**Sự thật quan trọng đã chứng minh ngày 2026-07-29:** cột `Time left` của dxFeed là **giờ UTC, KHÔNG phải giờ VN**.
Bằng chứng: giờ 21 UTC có đúng 0 nến (khớp nghỉ CME 17:00 ET), volume trung vị đỉnh ở 13–14 UTC (mở COMEX),
tên file lệch 7h so với dòng cuối. Ghi nhớ này từng bị lưu SAI trong memory → phải kiểm lại tương tự cho
**mọi** file khác, đừng tin tên cột.

## Việc phải làm

### 1. Định danh & chuẩn hoá từng bộ
Với **mỗi** file dữ liệu (kể cả `sample.csv`, `sample_bars.csv`, cả 2 `.pkl`):
- Sản phẩm gì (GC? MGC? GCQ26? hợp đồng nào?), lấy từ đâu ra kết luận đó.
- **Tick size** và **đơn vị giá**: dự án dùng "giá" với `1 giá = 10 tick = 0.1×10`. Kiểm bằng
  **phân bố khoảng cách giữa các giá liền kề** (gcd của các mức giá), không đoán theo tên.
- **Múi giờ — phải CHỨNG MINH bằng cơ chế**, cho từng file:
  - histogram **số nến theo giờ** → tìm giờ có ~0 nến (nghỉ phiên CME 1 tiếng)
  - histogram **volume trung vị theo giờ** → đỉnh phải trùng mở COMEX
  - vị trí **khoảng trống cuối tuần**
  Kết luận dạng `cột X = UTC` / `= UTC+7` kèm 3 bằng chứng số.
- Khoảng thời gian thật (dòng đầu/cuối), số nến, **số nến thiếu** (so với lịch phiên), gap dài nhất.

### 2. Ma trận trùng lặp thời gian
Bảng: bộ nào phủ tháng nào (2025-11 → 2026-07). Chỉ rõ **cửa sổ trùng nhau của dxFeed và fp-m1**, vì đó là
cửa sổ duy nhất có thể **đối chứng 2 nguồn**.

### 3. Điều tra bắt buộc: vì sao 2 nguồn cho kết quả lệch nhau?
Đã ghi nhận: cùng giai đoạn, setup scalp cho **WR 61% trên fp-m1** nhưng **42% trên dxFeed**. Phải tìm nguyên nhân:
- Có phải khác sản phẩm/hợp đồng? khác tick? khác múi giờ nên lệch phiên?
- Có phải fp-m1 lọc bớt nến rác / dxFeed có nến volume rất nhỏ?
- So trực tiếp: lấy **cùng 1 ngày** ở cửa sổ trùng, in cạnh nhau OHLCV từng phút, đếm số nến khớp / lệch,
  và lệch bao nhiêu tick.
Kết luận rõ ràng: bộ nào là **nguồn chuẩn để chốt số**, bộ nào là **đối chứng**, và lệch bao nhiêu thì
coi là bình thường. Nếu không tìm được nguyên nhân → ghi `CHƯA GIẢI THÍCH ĐƯỢC` và nói rõ hệ quả
(mọi số phải trình trên cả 2 bộ).

### 4. Sàng cột chết
Với `fp-m1-6-month.csv` và 2 file TPO: với mỗi cột, in `số giá trị khác 0 / tổng`, `min`, `max`, `số giá trị phân biệt`.
Đánh dấu cột **toàn 0 / hằng số / gần như rỗng** là KHÔNG DÙNG ĐƯỢC.
Đã biết: `Max one trade Vol.` toàn 0 (V6_PLAN §10) → xác nhận lại và tìm xem còn cột nào tương tự.

### 5. Bảng năng lực feature — phần chính của output
Với mỗi feature dưới đây, phán quyết `CÓ / KHÔNG / MỘT PHẦN`, kèm **bộ dữ liệu nào, bao nhiêu tháng, n dự kiến**:

*Tầng bias phiên*
1. Value Area hôm nay so với hôm qua (value migration) — từ `TPO-chart-daily.csv`
2. POC clustering nhiều phiên
3. Initial Balance (IB High/Low) và giá mở so với VA hôm trước
4. VWAP phiên (đã có trong engine) + độ lệch chuẩn VWAP
5. Vùng "va chạm nhiều" (HVN) theo mức giá — cần per-level hay suy được từ M1?

*Tầng cấu trúc range (cho kịch bản 3)*
6. Phát hiện swing high/low bằng cửa sổ fractal trên M1
7. Đếm số lần chạm mỗi biên
8. Độ rộng range theo "giá" và theo tick; range tồn tại bao lâu
9. Range còn hiệu lực / đã hỏng
10. Hợp lưu biên range với VAH/VAL/POC/IB

*Tầng đo lực (xác nhận vào lệnh)*
11. Delta theo nến (dấu, độ lớn, `Delta %`)
12. Bid volume vs Ask volume theo nến
13. Cumulative delta / CVD phân kỳ
14. Độ dài nến, thân/râu, vị trí đóng (`cpos`)
15. VSA volume ratio so với SMA20 (đã có: High=1.2, climax=2.2)
16. **Delta từng mức giá** (imbalance, stacked imbalance, absorption ở một mức) — đây là chỗ nghi ngờ nhất,
    phải nói rõ 25 phiên `perlevel` đủ cho việc gì và KHÔNG đủ cho việc gì
17. Kích thước lệnh lớn nhất trong nến (nhận biết cá lớn)

Với mỗi dòng ghi thêm: **công thức chính xác** tính từ cột nào, và **rủi ro look-ahead** nếu có
(ví dụ: thống kê toàn chuỗi như `mean` cả file là look-ahead — lỗi này đã từng xảy ra với `avg_vma`).

### 6. Mục "Không kiểm được offline"
Liệt kê dứt khoát, để GĐ4 không thiết kế vào đó. Đã biết trước (V6_PLAN §10): mọi thứ cần **DOM live /
đọc dòng lệnh thời gian thực**, và cổng "lệnh lớn" do `Max one trade Vol.` toàn 0.

### 7. Mục "Hạ tầng còn thiếu"
Ví dụ: có loader cho dxFeed (`research/entry_dxfeed.py`) nhưng chưa có loader chuẩn cho TPO csv / per-level pkl.
Ghi rõ cần viết loader nào, đặt ở đâu, API ra sao (GĐ6/GĐ7 sẽ dùng).

## File nên đọc trước (chỉ những chỗ này)

- [WYCKOFF_V6_PLAN.md](../quantower-entry-signal/WYCKOFF_V6_PLAN.md) — **§10, §11, §12**
- [research/entry_dxfeed.py](../quantower-entry-signal/research/entry_dxfeed.py) — loader hiện có, hàm `load_m1`, `load_fpm1`, `tpo_counts`, `value_area`, `build_zones`
- [research/wyckoff/cbr_v6.py](../quantower-entry-signal/research/wyckoff/cbr_v6.py) — `prepare()`, để biết feature nào đã có
- **Không** đọc các file `research/*.py` cũ khác (rất nhiều, phần lớn là thử nghiệm đã chết).

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **TUYỆT ĐỐI không bịa số.** Mọi con số là output thật của lệnh vừa chạy, dán kèm output. Chưa đo → ghi "chưa đo".
3. Không tin tên cột / tên file — kiểm bằng cơ chế (xem bài học múi giờ ở trên).
4. Repo **PUBLIC**: không hardcode token.
5. Không publish lên Claude Artifacts.
6. Xong → **commit + push `origin main`** (commit `DATA_CAPABILITY.md` + script kiểm nếu có, đặt ở `research/wyckoff/`).
7. Trung thực: mục nào chưa đo được phải ghi rõ.

## Xong khi nào

- [ ] Mọi file dữ liệu (kể cả `sample.csv`, `sample_bars.csv`, 2 `.pkl`) đã được định danh: sản phẩm, tick, múi giờ **có bằng chứng số**, khoảng thời gian, số nến thiếu
- [ ] Có ma trận trùng lặp thời gian và chỉ rõ cửa sổ đối chứng dxFeed ↔ fp-m1
- [ ] Đã điều tra chênh lệch WR 61% vs 42% và đưa kết luận (hoặc ghi rõ chưa giải thích được + hệ quả)
- [ ] Có danh sách cột chết
- [ ] Bảng năng lực **đủ 17 feature**, mỗi dòng có phán quyết + bộ dữ liệu + số tháng + công thức + rủi ro look-ahead
- [ ] Có mục "không kiểm được offline" và "hạ tầng còn thiếu"
- [ ] Đã commit + push

Cuối lượt báo: bộ nào là nguồn chuẩn, **feature nào có dữ liệu tốt nhất cho kịch bản 3**, và danh sách feature phải loại khỏi thiết kế vì không kiểm được.
