# BASELINE v6 — đóng băng 2026-07-29

> File này chốt số liệu tham chiếu cho mọi pha sau (GĐ4/GĐ6/…). Nguồn: `WYCKOFF_V6_PLAN.md`
> (đọc trước file đó để hiểu bối cảnh) + `final_table.py` + `imp_reversal_sweep.py` (đã sửa 2026-07-29).
> Dữ liệu: dxFeed GCQ26, cửa sổ 5–7/2026 (xem §Giới hạn).

## 0. ⚠️ ĐỌC TRƯỚC KHI TRÍCH BẤT KỲ SỐ NÀO Ở FILE NÀY (bổ sung 2026-07-29, sau GĐ8)

[AUDIT_V7.md](AUDIT_V7.md) §7 đã kiểm và kết luận: **toàn bộ số ở file này KHÔNG có một điểm dữ liệu
out-of-sample nào.** Cửa sổ OOS 2025-11→2026-04 không chạy được (chỉ **171** nến qua gate trên 6 tháng, so
với **52.160** nến của 3 tháng in-sample = **0,33%**) → KB1/KB2/KB3 đều `n=0`. 100% số liệu đến từ **một**
cửa sổ 3 tháng, **một** regime (vàng tạo đỉnh), **một** hợp đồng.

**Hệ quả bắt buộc khi tính vốn** (AUDIT_V7 §13, điều kiện #3):

| | |
|---|---|
| EV in-sample của KB1 | +1.424R/lệnh |
| **Kỳ vọng được phép dùng để tính kích thước vị thế** | **+0.7R** (đầu dưới của khoảng chiết khấu +0.7…+1.4R) |
| Vì sao chiết khấu | kẻ sống sót của **≥94** cấu hình trên cùng một cửa sổ; Bonferroni đưa p 0.0003 → 0.028 — vẫn sống nhưng biên mỏng hơn con số thô rất nhiều |

> **Live log là phép OOS ĐẦU TIÊN của cả dự án.** Trước khi có nó, KB1 chỉ ở mức "đủ bằng chứng để thử bằng
> vốn nhỏ và ghi log", **không phải** "hệ thống đã được xác nhận". Mọi báo cáo live sau này phải so với
> +0.7R, không so với +1.424R.

**Trạng thái 3 kịch bản sau cổng GĐ8:** `KB1 = PASS (có điều kiện)` · `KB2 = FAIL` (p=0.072; phía LONG chỉ
EV +0.154R → port ở dạng `EnableReversal=false`, **không cấp vốn**) · `KB3 = FAIL/KILL` (chết ở 2 tick phí,
0 range VALID trong 6 tháng OOS → **không port**).

## 1. Bảng số CHUẨN (mỗi nhánh + portfolio gộp)

```
tag                          n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | 05:+N.N 06:+N.N 07:+N.N ✓/✗ | nua1 +N.NR(nNN) nua2 +N.NR(nNN)

CBR (v6: SẠCH+retrace60-100+RR4, dead-window UTC 02-08, liquidity ON)
  n= 33 WR=48.5% tong=+47.0R EV=+1.424 MDD= 3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓ | nua1 +14.0R(n16) nua2 +33.0R(n17)

QUAY_DAU (v2, KHÔNG đổi — 2026-07-28, chưa áp BREAK SẠCH, xem §3 vì sao)
  n= 27 WR=55.6% tong=+10.5R EV=+0.389 MDD= 5.0R | 05:+2.0 06:+2.5 07:+6.0 ✓ | nua1 +4.5R(n13) nua2 +6.0R(n14)

PORTFOLIO (gộp theo thời gian — XEM CẢNH BÁO bên dưới, KHÔNG mô phỏng dedup thật giữa 2 nhánh)
  n= 60 WR=51.7% tong=+57.5R EV=+0.958 MDD= 5.0R | 05:+7.0 06:+24.5 07:+26.0 ✓ | nua1 +17.5R(n30) nua2 +40.0R(n30)
```

**Cảnh báo về dòng PORTFOLIO:** đây là **cộng gộp hai luồng theo mốc thời gian** (mỗi lệnh CBR và mỗi lệnh
QUAY_DAU tính độc lập), **KHÔNG** mô phỏng `Dedup` gộp chung CBR+reversal như C# thật làm trên danh sách
đã trộn (một lệnh reversal cùng phía có thể "nuốt" lệnh CBR trong `DedupBars` nến — xem §7 của
`WYCKOFF_V6_PLAN.md`, "Replicator CBR exact" — nợ hạ tầng CHƯA làm). Số portfolio ở đây là **cận trên gần
đúng** cho n/tổng R, có thể lệch nhẹ xuống so với C# thật nếu 2 nhánh trùng lệnh trong cửa sổ 6 nến.

## 2. Lệnh tái lập chính xác

```bash
cd quantower-entry-signal/research/wyckoff
python3 final_table.py     # dòng "+ B4 RR4 (thay RR3)" trong mục 1 = CBR chuẩn ở trên
```

```bash
cd quantower-entry-signal/research
python3 -c "
import imp_reversal_sweep as S
B = S.bars()
sigs = S.detect(B)                       # QUAY_DAU chuẩn (LIVE gate values, chưa áp BREAK SẠCH)
res = S.score(B, sigs, S.LIVE['rr'])
print(res['closed'], res['wr'], res['net'], res['bym'])
"
```

Portfolio: gộp `cbr_v6.scan(B, cbr_v6.cfg(CLEAN=True,PMAX=1.00,RR=4.0), vf, None)` (từ `entry_dxfeed.load_m1`)
với `imp_reversal_sweep.detect(imp_reversal_sweep.bars())` (từ dxFeed CSV riêng — **2 nguồn dữ liệu build
khác nhau**, xem `entry_dxfeed.py` vs `reversal_vwap.load_dxfeed`), sort theo `dt`, cộng R theo thời gian.
Script đầy đủ đã chạy để ra bảng trên — không lưu thành file `.py` riêng (one-off), lặp lại bằng đoạn lệnh
Python ở trên cho từng nhánh rồi tự gộp nếu cần.

## 3. Cấu hình MẶC ĐỊNH đã chốt (WyckoffRunner.cs, sau GĐ5)

| Input | Giá trị | Lý do |
|---|---:|---|
| `DeadUseUtc` | **true** (mới, v6) | Khung chết là hiện tượng thị trường (CME nghỉ), phải neo UTC — xem Bước 1 plan |
| `DeadStartHour` / `DeadEndHour` | 2 / 8 (nay là **UTC**) | Không đổi số, chỉ đổi ý nghĩa neo giờ |
| `SkipDeadSession` | true | Giữ nguyên — nay mới thực sự có tác dụng |
| `CleanBreak` (BREAK SẠCH) | true | n 55→33 nhưng EV ×1.5, MDD 6→3R — xem §2 |
| `CleanLook`/`CleanWin`/`CleanClosePos` | 20/5/0.50 | Ổn định trên cao nguyên look15-25 & w4-6 |
| `PullMax` | **1.00** (từ 0.90) | +B3: n 29→33, WR không đổi nhiều, tổng R +4 |
| `RR` (CBR) | **4.0** (từ 3.0) | Khuyến nghị plan: cân bằng WR/EV/MDD. RR3 cho WR cao hơn (57.6%) nếu ưu tiên winrate — phơi input để A/B live |
| `LiquidityFilter` | **true** (giữ nguyên) | Giữ = WR/EV/MDD tốt hơn tắt (tắt: +13R nhưng MDD 4R thay vì 3R) — GĐ chưa đủ bằng chứng để đổi |
| `LiquidityRatio` | 0.75 | không đổi |
| `TrendFilter` | true | còn đóng góp thật (tắt: n39/WR43.6%/kém hơn) |
| `VwapAlign` | true (giữ, nhưng đã xác nhận **NO-OP** trên cửa sổ này) | 0 lệnh khác biệt bật/tắt — đừng tính là 1 lớp lọc đã chứng minh |
| `EnableReversal`, `RevRR=1.5`, `RevVsaConf=1.8`, … | không đổi | Nhánh QUAY_DAU giữ nguyên logic v2 (2026-07-28) |

**Không đổi vì chưa đủ bằng chứng (giữ mặc định cũ):** `RevApproachBars`, `Cooldown` (nhánh reversal),
`SlCapPts` (nhánh reversal) — tự sweep xác nhận không ràng buộc trên mẫu hiện có (n=27), nhưng KHÔNG
suy ra là "vô dụng nói chung" — mẫu quá thưa để kết luận. Đã sửa comment/label trong code cho đúng sự
thật (xem `WyckoffRunner.cs`), KHÔNG xoá input.

## 4. Kết luận BREAK SẠCH cho nhánh QUAY_DAU — ⚠️ CHẠM QUY TẮC DỪNG, CHƯA CHỐT

Test cả hai chiều bằng `imp_reversal_sweep.py::detect(clean_mode=...)` (dùng lại
`cbr_v6.counter_sweep()` của CBR, hướng tiếp cận = ngược side vì đây là fade):

```
BASELINE (không lọc)        n=27 WR=55.6% net=+10.5R  (05:+2.0 06:+2.5 07:+6.0)
YÊU CẦU SẠCH (như CBR)      n=12 WR=75.0% net=+10.5R  (05:+1.5 06:+3.5 07:+5.5)  — SHORT 8 / LONG 4
YÊU CẦU CÓ QUÉT NGƯỢC       n=15 WR=40.0% net= 0.0R   (05:+0.5 06:-1.0 07:+0.5)  — SHORT 6 / LONG 9
```
(2 nhóm rời nhau, hợp lại đúng = 27 lệnh baseline — đã tự kiểm bằng tập hợp trước khi báo cáo.)

**Cùng DẤU với CBR** (nhóm sạch tốt hơn nhóm bẩn), **KHÔNG ngược dấu** như giả thuyết cơ chế ban đầu của
plan (§7: "reversal là fade, có thể được lợi từ thị trường xoay 2 chiều"). Giả thuyết đó **không được xác
nhận** trên dữ liệu này.

**NHƯNG kết quả này chạm cả hai ngưỡng DỪNG đã đặt ra trong plan:**
- WR nhảy 55.6% → 75.0% = **+19.4 điểm** (ngưỡng dừng: >10 điểm) ✗ CHẠM
- n tụt 27 → 12 = **−55.6%** (ngưỡng dừng: >40%) ✗ CHẠM

Theo đúng luật đã đặt ("Quy tắc DỪNG… → dừng, cần soi cơ chế"), **tôi KHÔNG tự chốt kết luận định tuyến
nhánh ở đây.** Lý do cẩn trọng thêm: n=12 (nhóm sạch) < 25 → theo LUẬT CHUNG mục 4 của brief, đây là
**"không kết luận"**, dù PASS criterion kỹ thuật (WR +≥5 điểm, dương cả 3 tháng) được thoả. Hai tiêu chí
mâu thuẫn nhau (PASS về mặt số, nhưng KILL về mặt cỡ mẫu) — cần người ở effort cao hơn soi cơ chế
(vì sao SẠCH cũng tốt cho reversal, trái với trực giác Wyckoff ban đầu) trước khi quyết định có áp
BREAK SẠCH cho QUAY_DAU hay không. **Việc cần làm tiếp (đề xuất cho vòng sau, KHÔNG tự áp):**
1. Soi cơ chế: xem từng lệnh trong nhóm "sạch" (n=12) có phải bị chi phối bởi 1-2 tháng/1 phía hay không
   (đã thấy lệch SHORT 8/LONG 4 trong nhóm sạch vs LONG 9/SHORT 6 trong nhóm bẩn — có thể là confound
   theo phía, chưa kiểm).
2. Nếu xác nhận là thật (không phải nhiễu mẫu nhỏ) → cân nhắc CHỈ áp BREAK SẠCH cho phía SHORT của
   QUAY_DAU, không áp toàn bộ.
3. KHÔNG bật `CleanBreak` cho nhánh QUAY_DAU trong `WyckoffRunner.cs` cho tới khi có kết luận rõ.

## 5. Số CŨ đã lỗi thời (trước 2026-07-29 — ĐỪNG dùng)

Mọi con số trích dẫn trước 2026-07-29 (kể cả trong lịch sử chat / memory) là **stale** do 3 lỗi parity
đã sửa trong `cbr_v6.py` (xem `WYCKOFF_V6_PLAN.md` §1):
1. `trend` tính với tolerance = 0 thay vì `TrendTolPts=1.0` giá.
2. `avg_vma` dùng trung bình TOÀN CHUỖI = look-ahead, thay vì cuộn 1000 nến trước.
3. Gate trend/VWAP/thanh khoản áp ở nến PHÁ thay vì nến VÀO (`RunnerSignal.cs:570` áp ở nến vào).

Sửa 3 lỗi này đổi baseline CBR (không cắt khung chết) từ n=58/WR43.1% → **n=55/WR47.3%** (sau khi B1 sửa
khung giờ). Kết luận định tính không đổi dấu, nhưng **số tuyệt đối đã đổi** — không trộn số cũ/mới.

Ngoài ra: số "148 lệnh" ở một vài docstring nghiên cứu là SAI, số thật là **140 lệnh** (CBR 112 /
QUAY_DAU 28) trên `RunnerSignal_signals.csv` — đã sửa (`review_runner.py`, `review_export.py`).

## 6. Giới hạn (nhắc lại mỗi khi trích số — xem đầy đủ ở `WYCKOFF_V6_PLAN.md` §11)

- **dxFeed là proxy YẾU cho feed live.** Cùng kỳ 6–7/2026, nhánh scalp cho WR 61% trên `fp-m1` nhưng chỉ
  42% trên dxFeed. Số ở BASELINE này là *tương đối* (so sánh trong cùng dxFeed), không phải dự báo WR live.
- **n nhỏ.** CBR n=33/3 tháng, QUAY_DAU n=27/3 tháng. Tháng 5 đóng góp ít nhất (CBR +5R, QUAY_DAU +2R).
  GCQ26 chỉ có thanh khoản đủ từ ~tháng 5/2026 → mở rộng cửa sổ về trước là RÁC, không phải out-of-sample.
  Muốn OOS thật cần front-month/CCPA khác.
- Backtest **không** mô hình hoá spread, slippage, phí; kiểm **SL trước TP** trong cùng nến (bi quan).
- Cửa sổ 5–7/2026 là **vàng tạo đỉnh** → phía SHORT được ưu ái nói chung. Là **regime**, không phải
  cấu trúc bền vững — đừng suy ra "SHORT luôn tốt hơn LONG" cho hệ thống này.
- Dòng PORTFOLIO ở §1 là **cận trên gần đúng** (chưa mô phỏng Dedup gộp 2 nhánh) — xem cảnh báo ở §1.
- Kết luận BREAK SẠCH cho QUAY_DAU ở §4 là **CHƯA CHỐT** — đọc kỹ trước khi trích dẫn dòng đó.

## 7. Việc CHƯA làm (còn lại trong plan, không thuộc phạm vi lượt này)

- **Bước 7 — Replicator CBR exact** (`WYCKOFF_V6_PLAN.md` §8): `cbr_v6.py` chưa mô phỏng `Dedup` gộp
  CBR+reversal, C# bỏ nến cuối còn Python quét hết. Đây là nợ hạ tầng, làm khi cần độ tin cậy cao hơn.
  ✅ Phần **`volfloor` lệch đã XONG** — xem §8 bên dưới.
- Kết luận rõ ràng cho BREAK SẠCH/QUAY_DAU (§4) — cần soi cơ chế ở effort cao hơn.

## 8. Đã sửa sau cổng GĐ8 (2026-07-29) — 3 điều kiện tiền đề của AUDIT_V7 §13

| # | Việc | Trạng thái | Bằng chứng |
|---|------|-----------|-----------|
| 1 | **Look-ahead `volfloor`** — `calc_volfloor()` lấy percentile-30 volume của *toàn bộ* dữ liệu ≥2026-05 rồi dùng ở **mọi** nến (kể cả nến đầu chuỗi) | ✅ **XONG** | Thêm hằng `VOLFLOOR_FROZEN=20.0` ở [entry_dxfeed.py](../entry_dxfeed.py) (khớp `RunnerSignal.cs`); 2 chỗ gọi trong v7 ([run_kb12.py](v7/run_kb12.py), [run_kb3.py](v7/run_kb3.py)) đã chuyển sang hằng. Chạy lại: **GOLDEN OK**, KB1 vẫn `n=33 WR=48.5% +47.0R EV=+1.424`, KB2 vẫn `n=27 EV=+0.389`, portfolio vẫn `n=60 +57.5R` — **không đổi một con số nào**, đúng như audit §1.2 dự đoán. `calc_volfloor()` giữ lại (có cảnh báo) chỉ để tái lập ~15 script research cũ. |
| 2 | **Router 1-vị-thế chưa từng được dữ liệu nào test** (bỏ 0 lệnh trong 3 tháng) | ✅ **XONG** | Router tách thành `engine.route_one_position()` (dùng chung, không còn hàm lồng trong `run_kb3.py`) + [test_router.py](v7/test_router.py): **15/15 PASS**, phủ đúng nhánh chưa từng chạy (chồng thời gian, vào đúng phút đóng lệnh cũ → bỏ, ưu tiên khi trùng phút, không xếp hàng) + 2 tính chất bất biến trên 300 tín hiệu chồng dày (0 cặp chồng thời gian, giữ+bỏ=tổng). Đây là **bảng đối chiếu parity cho GĐ9**. |
| 3 | **Kỳ vọng dùng để tính vốn** phải là +0.7R, không phải +1.424R | ✅ **XONG** | Ghi ở §0 của file này. |

**Lỗi dữ liệu phát hiện thêm — cột Volume của `fp-m1-6-month.csv` hỏng tháng 6/2026:**

Đo lại xác nhận đúng như audit §G: **22.297 / 29.850 nến tháng 6 (74,7%) có `Volume=0` dù
`Ticks(from bar)>0`** → chắc chắn lỗi dữ liệu, không phải phiên vắng. Vùng hỏng **liền khối
`2026-06-04` → `2026-06-26`** (19 ngày). OHLC vẫn đúng (audit đối chiếu giá khớp tuyệt đối với dxFeed).

- **Hệ quả:** mọi feature dựa trên volume (`vma`, `vratio`, VSA, gate `volfloor`, `liqratio`, VWAP) **sai**
  trong khoảng đó. Bất kỳ kết luận nào chạy trên tháng 6 của **file này** đều vô hiệu.
- **Đã chặn tái phát:** cả 2 loader `load_fp_m1()` / `load_fp_m1_full()` trong
  [loaders.py](v7/loaders.py) giờ **in cảnh báo** khi gặp `Volume=0`, kèm hằng
  `FPM1_VOLUME_BAD_FROM/TO` và hàm lọc `fpm1_volume_ok(b)`.
- ⚠ **Không ảnh hưởng** số chuẩn ở §1: chúng chạy trên **dxFeed**, không phải fp-m1.
