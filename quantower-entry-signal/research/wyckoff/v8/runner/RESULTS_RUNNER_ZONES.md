# RESULTS — đổi neo vùng RunnerSignal.cs sang bộ vùng CORVEN (2026-08-01)

> Session 2 (RunnerSignal CBR M1, v5 đang chạy LIVE). Nguồn thiết kế:
> `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md`, `quantower-entry-signal/PLAN_KB_ABC.md`.
> Toàn bộ script nằm trong `v8/runner/` (thư mục riêng của session này):
> `cbr_hvn.py` (bản sao `cbr_v6.py` + `run_zone()`/`scan_zone()` mới cho PLAY2),
> `zone_engine.py` (PLAY1 + zone lookup + probe MFE + đối chứng ngẫu nhiên + chi phí),
> `measure.py` (đo cột TRƯỚC).
>
> **Bản live `RunnerSignal.cs` KHÔNG bị đổi hành vi mặc định.** Toàn bộ thay đổi nằm sau cờ
> `CorvenZoneAnchor` (mặc định `false`). Bằng chứng: `git diff` trên `RunnerSignal.cs` chỉ có
> đúng 4 dòng bị THAY (chữ ký `Scan()`/`ScanReversal()` + 2 nơi gọi, để nhận thêm tham số
> `corvenZones`) — không dòng logic gốc nào bị sửa; nhánh mới nằm sau `if (CorvenZoneAnchor)`
> luôn `return`/`continue` trước khi chạm code cũ.

## 0. Kết luận thẳng (đọc trước bảng)

**CHƯA đủ bằng chứng để chuyển live sang neo vùng CORVEN — khuyến nghị GIỮ mặc định `CorvenZoneAnchor=false`.**

Đối chứng ngẫu nhiên (P4) là phép kiểm quan trọng nhất và nó **KILL** gần như toàn bộ biến thể:

| Nhánh | Chênh EV (thật − ngẫu nhiên) | Ngưỡng PASS | Kết quả |
|---|---:|---:|---|
| KB-A PLAY2 (tuần) | **−0.005R** | ≥ +0.25R | **KILL** — vị trí vùng tuần không mang thông tin |
| KB-A PLAY1 (tuần) | **−0.329R** | ≥ +0.25R | **KILL mạnh** — random còn tốt hơn (n=11, nhiễu) |
| KB-B PLAY2 (ngày) | +0.116R | ≥ +0.25R | **KILL** — chưa đạt ngưỡng |
| KB-B PLAY1 (ngày) | +0.270R | ≥ +0.25R | Đạt ngưỡng số, nhưng **n=21 < 25 → không kết luận** |

Đây là **kết quả âm nhất quán** với bài học 2026-07-31 (`quantower-tpo-suite/BACKTEST-ZONES-V2.md`: "v2 không
chứng minh được tốt hơn ngẫu nhiên") và với `M30SessionZones` gắn vùng phiên vào QUAY_ĐẦU (n tăng, EV về 0).
Cả 3 lần đo độc lập trên 3 bộ vùng khác nhau đều cho cùng một kết luận: **thay đổi LOẠI vùng neo (từ range
nội bộ / VWAP phiên sang HVN+VWAP tuần|ngày) không tự nó tạo ra edge — có thể vì thứ đang hoạt động trong
`RunnerSignal.cs` v5 không phải "đúng vị trí vùng", mà là cấu trúc phá→hồi→tiếp/chạm→đảo TỰ THÂN cộng với
lọc xu hướng+thanh khoản đã có.**

Mặc định live giữ nguyên 100% (đã kiểm bằng diff, xem trên).

---

## 1. Bảng CBR / PLAY2 (phá vùng → hồi → tiếp diễn)

Nguồn: dxFeed 27-7, 5-7/2026. `vf=VOLFLOOR_FROZEN=20.0` (không look-ahead) cho MỌI số trong bảng
(kể cả cột TRƯỚC — đã xác nhận vf=17 look-ahead vs vf=20 cho **kết quả giống hệt** với CBR, xem P0).

| Thông số | TRƯỚC (range nội bộ M1) | SAU — KB-A (HVN+VWAP TUẦN, W_CLOSED) | SAU — KB-B (HVN+VWAP NGÀY, D_CLOSED) |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ | dxFeed 5-7/2026 | dxFeed 5-7/2026 | dxFeed 5-7/2026 |
| Neo vùng | range co hẹp 8 nến M1 nội bộ | mép HVN/VWAP tuần (≤3 HVN + VWAP tuần) | mép HVN/VWAP ngày (≤3 HVN + VWAP ngày) |
| n (số lệnh) | 55 | 38 | 56 |
| WR % | 47.3% | 34.2% | 33.9% |
| Tổng R | +49.0R | +14.0R | +20.0R |
| EV / lệnh (R) | +0.891 | +0.368 (**−0.523** ↓) | +0.357 (**−0.534** ↓) |
| MDD (R) | 6.0R | 10.0R (**+4.0 ↑ xấu hơn**) | 7.0R (+1.0 ↑ xấu hơn) |
| Tháng 5 (R) | +12.0 | **−3.0** | +8.0 |
| Tháng 6 (R) | +14.0 | +13.0 | +10.0 |
| Tháng 7 (R) | +23.0 | +4.0 | +2.0 |
| Nửa kỳ 1 (R, n) | +21.0R (n27) | −3.0R (n19) | +8.0R (n28) |
| Nửa kỳ 2 (R, n) | +28.0R (n28) | +17.0R (n19) | +12.0R (n28) |
| LONG: n / WR / EV | 27 / 37.0% / +0.481 | 18 / 44.4% / +0.778 | 26 / 34.6% / +0.385 |
| SHORT: n / WR / EV | 28 / 57.1% / +1.286 | 20 / 25.0% / +0.000 | 30 / 33.3% / +0.333 |
| EV − EV(ngẫu nhiên, 5 seed) | — (không áp dụng cho TRƯỚC) | **−0.005R** (random EV_tb=+0.373) | **+0.116R** (random EV_tb=+0.241) |
| EV @ phí 2 tick | — | +0.318 | +0.305 |
| EV @ phí 4 tick | — | +0.267 | +0.252 |
| RR đang dùng | 3.0 | 3.0 | 3.0 |
| W_CLOSED vs W_RUNNING | — | n=37 EV+0.405 (RUNNING, gần như không đổi) | n=56 EV+0.357 (D_RUNNING, giống hệt D_CLOSED) |
| Số cấu hình đã thử | 1 (GOLDEN) | 2 (W_CLOSED, W_RUNNING) | 2 (D_CLOSED, D_RUNNING) |
| **KẾT LUẬN** | — | **KILL** (đối chứng ngẫu nhiên −0.005R) | **KILL** (đối chứng ngẫu nhiên +0.116R < 0.25) |

Ghi chú: SL/TP/BVSA/BBODY/WAIT/PMIN/PMAX/HOLD_TOL/RBODY/GATE trend+VWAP+liquidity giữ **nguyên** giá trị
v5 shipped ở cả 2 cột — chỉ đổi nguồn cạnh neo. `run_zone()` KHÔNG bao gồm các toggle thử nghiệm W3/R9/R3
(chúng vốn cũng không thuộc v5 shipped).

---

## 2. Bảng QUAY_ĐẦU / PLAY1 (chạm vùng → đảo chiều)

| Thông số | TRƯỚC (VWAP phiên) | SAU — KB-A (HVN+VWAP TUẦN) | SAU — KB-B (HVN+VWAP NGÀY) |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ | dxFeed 5-7/2026 | dxFeed 5-7/2026 | dxFeed 5-7/2026 |
| Neo vùng | CHỈ VWAP phiên (tol 12 tick) | HVN/VWAP tuần (tol 12 tick) + gate R2 (25% cực trị "range gần" 50 nến) | HVN/VWAP ngày (tol 12 tick) + gate R2 |
| ConfirmOn | false (khớp v5 ScanReversal hiện tại) | false | false |
| n (số lệnh) | 27 | 11 | 21 |
| WR % | 55.6% | 36.4% | 38.1% |
| Tổng R | +10.5R | +5.0R | +11.0R |
| EV / lệnh (R) | +0.389 | +0.455 (+0.066 ↑, **nhưng n=11**) | +0.524 (+0.135 ↑, **nhưng n=21**) |
| MDD (R) | 5.0R | 4.0R | 8.0R (+3.0 ↑ xấu hơn) |
| Tháng 5 (R) | +2.0 | −1.0 | −1.0 |
| Tháng 6 (R) | +2.5 | +7.0 | +4.0 |
| Tháng 7 (R) | +6.0 | −1.0 | +8.0 |
| Nửa kỳ 1 (R, n) | +4.5R (n13) | +7.0R (n5) | +2.0R (n10) |
| Nửa kỳ 2 (R, n) | +6.0R (n14) | −2.0R (n6) | +9.0R (n11) |
| LONG: n / WR / EV | 13 / 46.2% / +0.154 | 7 / 42.9% / +0.714 | 8 / 37.5% / +0.500 |
| SHORT: n / WR / EV | 14 / 64.3% / +0.607 | 4 / 25.0% / +0.000 | 13 / 38.5% / +0.538 |
| EV − EV(ngẫu nhiên, 5 seed) | — | **−0.329R** (random EV_tb=+0.784, THẬT THUA random) | **+0.270R** (random EV_tb=+0.254, đạt ngưỡng SỐ) |
| EV @ phí 2 tick | — | +0.401 | +0.461 |
| EV @ phí 4 tick | — | +0.347 | +0.398 |
| RR đang dùng | 1.5 | 3.0 (xem probe MFE §3) | 3.0 |
| ConfirmOn=true (đối chiếu) | — | n=3 EV+0.333 (quá nhỏ) | n=7 EV+0.143 (quá nhỏ) |
| Số cấu hình đã thử | 1 (GOLDEN) | 3 (probe + confirm F/T) | 3 (probe + confirm F/T) |
| **KẾT LUẬN** | — | **KILL** (đối chứng ngẫu nhiên âm; n<15 cũng tự động KILL theo luật cỡ mẫu) | **KHÔNG KẾT LUẬN** (đạt ngưỡng đối chứng nhưng 15≤n<25) |

---

## 3. Bảng gộp portfolio (PLAY1 + PLAY2 theo từng tầng, cộng theo thời gian — CHƯA mô phỏng Dedup gộp 2 nhánh)

| Thông số | TRƯỚC (gộp CBR+QUAY_ĐẦU) | SAU — KB-A (gộp, tuần) | SAU — KB-B (gộp, ngày) |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ | dxFeed 5-7/2026 | dxFeed 5-7/2026 | dxFeed 5-7/2026 |
| Neo vùng | range nội bộ + VWAP phiên | HVN+VWAP tuần (cả 2 play) | HVN+VWAP ngày (cả 2 play) |
| n (số lệnh) | 82 | 49 | 77 |
| WR % | 50.0% | 34.7% | 35.1% |
| Tổng R | +59.5R | +19.0R | +31.0R |
| EV / lệnh (R) | +0.726 | +0.388 (**−0.338 ↓**) | +0.403 (**−0.323 ↓**) |
| MDD (R) | 7.0R | 9.0R (+2.0 ↑ xấu hơn) | 8.0R (+1.0 ↑ xấu hơn) |
| Tháng 5 (R) | +14.0 | −4.0 | +7.0 |
| Tháng 6 (R) | +16.5 | +20.0 | +14.0 |
| Tháng 7 (R) | +29.0 | +3.0 | +10.0 |
| Nửa kỳ 1 (R, n) | +24.5R (n41) | +4.0R (n24) | +14.0R (n38) |
| Nửa kỳ 2 (R, n) | +35.0R (n41) | +15.0R (n25) | +17.0R (n39) |
| LONG/SHORT | xem bảng 1+2 riêng từng play | xem bảng 1+2 | xem bảng 1+2 |
| EV − EV(ngẫu nhiên) | — | trung bình có trọng số ≈ (38×−0.005 + 11×−0.329)/49 ≈ **−0.079R** | ≈ (56×0.116 + 21×0.270)/77 ≈ **+0.158R** |
| EV @ phí 4 tick | — | ≈ +0.29 (nội suy 2 nhánh) | ≈ +0.31 (nội suy 2 nhánh) |
| RR đang dùng | 3.0 / 1.5 | 3.0 / 3.0 | 3.0 / 3.0 |
| Số cấu hình đã thử | — | 5 (PLAY2) + 6 (PLAY1) = 11/10 ⚠ hơi vượt (2 A/B bắt buộc theo plan: W_CLOSED/RUNNING, ConfirmOn F/T — không phải dò tìm để cứu kết quả) | (dùng chung bộ cấu hình trên) |
| **KẾT LUẬN** | — | **KILL** | **KILL/KHÔNG KẾT LUẬN** (PLAY2 KILL, PLAY1 không kết luận) |

---

## 4. Bảng lịch sử vòng lặp

| # | Đổi gì | n / WR / EV | Giữ hay bỏ | Vì sao |
|---|---|---|---|---|
| 1 | GOLDEN: copy `cbr_v6.py` → `cbr_hvn.py` | n=55 EV+0.891 (khớp tuyệt đối) | Giữ | Xác nhận trước khi sửa bất cứ gì |
| 2 | PLAY2 neo HVN+VWAP TUẦN (W_CLOSED) | n=38 EV+0.368 | Đo, không chọn | Thấp hơn TRƯỚC, MDD xấu hơn |
| 3 | PLAY2 W_CLOSED → W_RUNNING | n=37 EV+0.405 | Bỏ (không khác biệt đáng kể) | Chênh lệch nằm trong nhiễu mẫu nhỏ |
| 4 | PLAY2 neo HVN+VWAP NGÀY (D_CLOSED) | n=56 EV+0.357 | Đo, không chọn | Không hơn tuần; đối chứng ngẫu nhiên không qua |
| 5 | PLAY1 probe MFE (tuần, trước khi chốt RR) | n=11, P(MFE≥3R)=36.4% | Chọn RR3 tạm | n quá nhỏ để tin, dùng RR3 theo spec mặc định |
| 6 | PLAY1 probe MFE (ngày) | n=21, P(MFE≥3R)=38.1% | Cùng RR3 | Nhất quán hướng với probe tuần |
| 7 | PLAY1 neo tuần, ConfirmOn=false | n=11 EV+0.455 | Đo, không chọn | Đối chứng ngẫu nhiên ÂM (−0.329R) |
| 8 | PLAY1 neo tuần, ConfirmOn=true | n=3 EV+0.333 | Bỏ | n quá nhỏ, không dùng được |
| 9 | PLAY1 neo ngày, ConfirmOn=false | n=21 EV+0.524 | Đo, không chọn | Đạt ngưỡng đối chứng NHƯNG n<25 |
| 10 | PLAY1 neo ngày, ConfirmOn=true | n=7 EV+0.143 | Bỏ | n quá nhỏ |
| 11 | Chi phí giao dịch 0→8 tick (cả 4 biến thể) | EV còn dương ở 8 tick mọi nơi | Không phải nút nghẽn | Random-control mới là nút nghẽn, không phải phí |

**Không đi tìm cấu hình thứ 12 để cứu kết luận** — dừng đúng lúc theo luật đã đặt trước.

---

## 5. Tuần vs ngày — giả thuyết "tuần WR cao hơn" (§6.3 PLAN)

| | PLAY2 | PLAY1 | Portfolio gộp |
|---|---:|---:|---:|
| WR KB-A (tuần) | 34.2% | 36.4% | 34.7% |
| WR KB-B (ngày) | 33.9% | 38.1% | 35.1% |

**Giả thuyết SAI trên dữ liệu này** (hoặc đúng hơn: không phân biệt được — chênh lệch 0.3-1.7 điểm % trên
n=11-77 nằm hoàn toàn trong nhiễu mẫu nhỏ). KB-B (ngày) nhỉnh hơn KB-A (tuần) ở cả PLAY1 lẫn portfolio gộp,
ngược hướng kỳ vọng của CORVEN. Không đủ bằng chứng để nói tầng nào "tốt hơn" — cả hai đều KILL/không kết
luận qua đối chứng ngẫu nhiên nên câu hỏi WR-tầng-nào-cao-hơn ở đây có phần không còn ý nghĩa thực chiến.

**Kiểm tra tần suất (§6.3 mục 1):** CORVEN nói KB-A ≈ 10 lệnh/tuần ⇒ kỳ vọng ~130 lệnh/13 tuần. Đo được
n=49 (PLAY1+PLAY2 gộp) — nằm trong biên rộng [30,400] của phép kiểm conformance thô, nhưng cách xa điểm
ước tính ~130. Khả năng: (a) gate R2/trend/confirm kế thừa từ scalp v5 quá chặt khi áp cho neo tuần, hoặc
(b) "10 lệnh/tuần" của CORVEN bao gồm cả KB-C (không neo vùng, không đo trong session này).

---

## 6. Cái gì KHÔNG đo được và vì sao

- **Parity C#↔Python cho nhánh BẬT (`CorvenZoneAnchor=true`):** không có runtime Quantower/`HistoricalData`
  thật trong môi trường này để chạy `RunnerSignal.cs` và so tín hiệu 1-1 với Python. Chỉ xác nhận được
  **code-level**: build sạch (0 warning/0 error) và bằng `git diff` rằng nhánh TẮT không đổi một dòng logic
  gốc nào. Khuyến nghị: khi đưa lên Windows/Quantower, chạy replay 1 tuần dữ liệu thật, xuất CSV
  (`ExportCsv=true`), so với `zone_engine.py`/`cbr_hvn.py` cùng cửa sổ trước khi tin số C#.
- **OOS thật ngoài 5-7/2026:** vẫn là nút nghẽn cũ của cả dự án (GCQ26 qua First Notice Day 31/07) — không
  giải quyết trong session này.
- **KB-C (follow order flow trong move):** không thuộc phạm vi PLAY1/PLAY2 nên không đo ở đây.
- **Ảnh chart kiểm HVN tuần bằng mắt:** không có quyền publish artifact (theo bộ nhớ dự án), và môi trường
  này không có GUI để crop/xem chart Quantower — chỉ kiểm HVN bằng số (P1: 13 mốc tuần in ra khớp DST bằng
  mắt qua text, không qua ảnh).

## 7. Trả lời thẳng

**Có nên chuyển bản live sang neo vùng CORVEN không?** **CHƯA — chưa đủ bằng chứng, có bằng chứng khá rõ
là KHÔNG nên** (đối chứng ngẫu nhiên KILL 3/4 biến thể chính, biến thể còn lại "không kết luận" vì n nhỏ).
Bản live `RunnerSignal.cs` giữ nguyên mặc định `CorvenZoneAnchor=false`; cờ mới chỉ để người học tự bật
A/B nếu muốn tự kiểm chứng thêm bằng log thật, không phải khuyến nghị bật.
