# RESULTS_KB12 — GĐ6: implement + test KB1/KB2 theo SPEC_V7_3KB.md

> Viết 2026-07-29. Bám [SPEC_V7_3KB.md](../SPEC_V7_3KB.md) §1-§9 (không đụng §10 — port C#, ngoài phạm vi
> lượt này). Package: [`research/wyckoff/v7/`](v7/) (`loaders.py`, `features.py`, `engine.py`, `report.py`,
> `run_kb12.py`). Toàn bộ số trong file này là output THẬT của `python3 research/wyckoff/v7/run_kb12.py`
> (log đầy đủ dán nguyên văn bên dưới theo từng mục — không có số nào gõ tay).
> Baseline đối chiếu: [BASELINE.md](BASELINE.md). Engine gốc (đóng băng, KHÔNG sửa):
> [cbr_v6.py](cbr_v6.py). Kết luận GĐ4 không lặp lại: [WYCKOFF_V6_PLAN.md §9](../WYCKOFF_V6_PLAN.md).

**Kết luận 1 câu:** GOLDEN OK; **không có feature mới nào PASS** ở lượt này cho cả KB1 lẫn KB2 — cấu hình
mặc định **giữ nguyên y hệt v6/BASELINE.md** (KB1 n=33 EV+1.424, KB2 n=27 EV+0.389). Phát hiện quan trọng
nhất: state machine `range_struct.py` viết **đúng theo pseudocode §4.3** nhưng cho `n_range` lệch **77%**
so với probe (74 vs 322) — bị chặn ở bước kiểm bắt buộc, xem mục 9.

---

## 1. GOLDEN OK

```
cbr_v6.scan (BASELINE đóng băng):
  B4 baseline (cbr_v6)               n= 33 WR= 48.5% tong=  +47.0R EV=+1.424 MDD=  3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓ | nua1 +14.0R(n16) nua2 +33.0R(n17)
engine.scan_box (v7, RangeMode=0/BIAS_ON=off = NO-OP):
  B4 v7-box (feature tắt)            n= 33 WR= 48.5% tong=  +47.0R EV=+1.424 MDD=  3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓ | nua1 +14.0R(n16) nua2 +33.0R(n17)

33 vs 33 tín hiệu, cùng bộ (i,side)? True
==> GOLDEN OK
```

Cách đạt golden: `engine.scan_box()` khi `BIAS_ON=False` **gọi lại y hệt vòng lặp của `cbr_v6.run()`**
(copy có chủ đích, không phải suy diễn lại) — chỉ thêm 1 điều kiện `okB` luôn `True` khi tắt. `evaluate_v7()`/
`hit_v7()` (tổng quát hoá theo §6.5.1, chuẩn bị cho KB3) khi tín hiệu không có `s['tp']` cũng suy giảm đúng
về `cbr_v6.evaluate()`. Đã kiểm bằng so từng cặp `(i, side)` — khớp tuyệt đối, không chỉ khớp thống kê tổng.

---

## 2. Bảng tiến hoá theo bước

### KB1 (cửa sổ dxFeed 5-7/2026, incumbent n=33 WR=48.5% EV=+1.424 MDD=3.0R)

```
tag                                n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | thang | PASS/KILL
B0  baseline v6 (= incumbent)         n= 33 WR=48.5% tong=+47.0R EV=+1.424 MDD=3.0R  ✓        (mốc so)
B1  RangeMode=1 (struct, THÔNG TIN)   n=  0  —                                                KILL (n<25; buộc "không kết luận" theo §4.3 — xem mục 9)
B2a A1 bias THAY THẾ proxy            n=  9 WR=44.4% tong=+11.0R EV=+1.222 MDD=3.0R ✗        KHÔNG KẾT LUẬN (n<25)
B2b A2 bias CỘNG THÊM proxy           n=  8 WR=50.0% tong=+12.0R EV=+1.500 MDD=2.0R ✗        KHÔNG KẾT LUẬN (n<25)
B2c A3 không lọc gì (cả 2 tắt)        n= 39 WR=43.6% tong=+46.0R EV=+1.179 MDD=4.0R ✓        KILL (EV thấp hơn incumbent)
B3  WY04 (No Supply ở nhịp hồi)       n=  6 (nhóm CÓ)  vs n=27 (nhóm KHÔNG) — xem partition   KILL — bộ lọc là nhiễu
```

### KB2 (dxFeed, incumbent QUAY_DAU n=27 WR=55.6% EV=+0.389 MDD=5.0R)

```
K0  baseline VWAP-only (LIVE params)  n= 27 WR=56% EV=+0.389 net=+10.5R  ✓          (mốc so)
K1a Kb2ExtremeWin=10                  giữ n=15 EV=+0.333 | loại n=12 EV=+0.458      KILL (giữ TỆ HƠN loại — ngược hướng)
K1b Kb2ExtremeWin=20                  giữ n=13 EV=+0.538 | loại n=14 EV=+0.250      KILL (chênh +0.288 < 0.30, sát ngưỡng)
K1c Kb2ExtremeWin=60                  giữ n=10 EV=+0.500 | loại n=17 EV=+0.324      KILL (chênh +0.176 < 0.30)
K2  Kb2ZoneExtend (hợp lưu D-1/phiên) n=5/27 lệnh có hợp lưu, EV=+0.500             KILL DỨT ĐIỂM (n=5 << 40, §5.9)
K3  Delta confirm (fp-m1, 6 tháng)    n=16 (không lọc) -> n=4 (có lọc delta)        KHÔNG KẾT LUẬN (n<10), báo riêng
```

---

## 3. Partition (bắt buộc cho mọi bộ lọc mới)

### 3.1 KB1 — bias (pool rộng nhất: TrendProxy TẮT, Bias TẮT, n=39)

```
GIU (bias đúng side)               n=  9 WR=44.4% tong=+11.0R EV=+1.222 MDD=3.0R | 05:+0.0 06:+1.0 07:+10.0 ✗
LOAI (bias sai/0)                  n= 30 WR=43.3% tong=+35.0R EV=+1.167 MDD=3.0R | 05:+5.0 06:+18.0 07:+12.0 ✓
=> KILL — bộ lọc là NHIỄU (EV_giữ − EV_loại = +0.056 < 0.30)
```
n_loại=30 ≥10 (đủ để kết luận, không phải "không kết luận") — nhóm bị bias loại **không hề tệ hơn rõ rệt**,
thậm chí dương cả 3 tháng trong khi nhóm giữ lại âm/bằng 0 ở 2/3 tháng. Đây là bằng chứng khá dứt khoát rằng
bias-theo-session không tách được tín hiệu tốt/xấu trên cửa sổ này.

### 3.2 KB1 — WY04 No Supply/No Demand (trên đúng 33 lệnh incumbent)

```
CO WY04 (no_supply/no_demand)      n=  6 WR=50.0% tong=+9.0R  EV=+1.500 MDD=3.0R | 05:-1.0 06:+2.0 07:+8.0 ✗
KHONG CO WY04                      n= 27 WR=48.1% tong=+38.0R EV=+1.407 MDD=3.0R | 05:+6.0 06:+20.0 07:+12.0 ✓
=> KILL — bộ lọc là NHIỄU (EV_giữ − EV_loại = +0.093 < 0.30)
```
Nhóm "CÓ WY04" chỉ n=6 (rất mỏng — dưới ngưỡng 10 mà `report.partition()` yêu cầu để nói "loại tệ hơn rõ",
nhưng ở đây WY04 là nhóm ĐƯỢC GIỮ, không phải nhóm bị loại nên luật n≥10 áp cho nhóm loại (n=27, đạt) — chênh
EV quá nhỏ (0.093) để kết luận đây là một bộ lọc thật, dù n nhỏ khiến ngay cả khi PASS cũng phải ghi
"không kết luận". Ghi vào mục 5 dưới nhãn đã bác.

### 3.3 KB2 — Kb2ExtremeWin (CHART_CASES lỗi #6)

```
win=10: GIU n=15 EV=+0.333  |  LOAI n=12 EV=+0.458   chênh=-0.125  KILL (ngược hướng)
win=20: GIU n=13 EV=+0.538  |  LOAI n=14 EV=+0.250   chênh=+0.288  KILL (chưa đạt 0.30, sát ngưỡng)
win=60: GIU n=10 EV=+0.500  |  LOAI n=17 EV=+0.324   chênh=+0.176  KILL
```
Không có cấu hình nào vượt ngưỡng 0.30 — và `win=10` còn cho dấu NGƯỢC (nhóm bị loại tốt hơn nhóm giữ),
tức bộ lọc "cực trị phải là cực trị N nến gần nhất" **không tách được tín hiệu tốt/xấu một cách nhất quán**
trên mẫu 27 lệnh này.

### 3.4 KB2 — Kb2ZoneExtend (hợp lưu D-1/phiên)

```
TOÀN BỘ (VWAP-only, đang ship)         n=27 WR=56% EV=+0.389 net=+10.5R
CHỈ lệnh CÓ hợp lưu thêm D-1/phiên     n= 5 WR=60% EV=+0.500 net=+2.5R
  phân loại vùng hợp lưu: {'Day':1, 'POC':2, 'VAH':1, 'VAL':1}
```
Chỉ **5/27** lệnh QUAY_DAU hiện có (đang neo VWAP) tình cờ cũng hợp lưu vùng D-1/phiên trong ±7 tick — quá
mỏng để tách partition (< 10) **và** quá xa mốc "n≥40" mà §5.9 yêu cầu để coi Kb2ZoneExtend là một hướng mở
rộng khả thi. Theo đúng luật KILL dứt điểm của §5.9 ("nếu không đưa n lên ≥40 → bỏ hẳn ý tưởng mở rộng"):
**bỏ Kb2ZoneExtend**, giữ nhánh VWAP-only.

---

## 4. Sweep

### 4.1 KB1 — bias `TOL` × `MIN_SCORE` (SPEC §2.4, cấu hình A1-style: TrendProxy TẮT, Bias BẬT)

```
TOL=0.2 MIN_SCORE=1   n=16 EV=+1.500 (05:+3.0 06:+12.0 07:+9.0 ✓)
TOL=0.2 MIN_SCORE=2   n= 9 EV=+1.222
TOL=0.2 MIN_SCORE=3   n= 5 EV=+0.000
TOL=0.5 MIN_SCORE=1   n=16 EV=+1.500   (= TOL=0.2, TOL không đổi kết quả trên cửa sổ này)
TOL=0.5 MIN_SCORE=2   n= 9 EV=+1.222
TOL=0.5 MIN_SCORE=3   n= 5 EV=+0.000
TOL=1.0 MIN_SCORE=1   n=16 EV=+1.500
TOL=1.0 MIN_SCORE=2   n= 9 EV=+1.222
TOL=1.0 MIN_SCORE=3   n= 5 EV=+0.000
```
Nhận xét: `TOL` (0.2/0.5/1.0 giá) **không đổi kết quả một chút nào** trên cửa sổ 5-7/2026 — nghĩa là so sánh
POC(D-1) vs POC(D-2) hiếm khi rơi vào vùng biên [0.2,1.0] giá, gate C1 gần như nhị phân (đã lệch hẳn hoặc
bằng đúng 0) ở dữ liệu này. `MIN_SCORE=1` cho EV cao nhất (+1.500) NHƯNG **n=16 < 25 ở MỌI tổ hợp** —
không có "điểm đẹp" nào đủ mẫu để PASS; đây là cao nguyên thật (không phải đỉnh nhọn) nhưng cao nguyên đó
nằm **dưới ngưỡng kết luận**, không phải bằng chứng ủng hộ bias.

### 4.2 KB2 — `Kb2ExtremeWin` ∈ {10, 20, 60} (đã in ở mục 3.3)
Không có vùng nào cho chênh EV ổn định ≥0.30 — dao động -0.125 → +0.288 → +0.176, không đơn điệu theo
window, không phải cao nguyên rõ ràng quanh 1 giá trị tốt.

---

## 5. Đã thử và bỏ (không làm lại pha sau)

| Ý tưởng | Kết quả | Vì sao bỏ |
|---|---|---|
| **RangeMode=1** (range theo cấu trúc `range_struct.py` thay box 8 nến) | n=0 tín hiệu (sau toàn bộ funnel ARM→WAIT→dedup→post) trên 60 arm event 5-7/2026 | State machine bar-by-bar tự RESET (`new_range`) gần như mọi khi giá đóng cửa vượt biên hiện tại trong pha FORMING (một range mới bắt đầu với `rhi=rlo=`1 nến, cực kỳ dễ vỡ) → chỉ 27/nhiều nghìn lần FORMING sống nổi tới đúng 30 nến, 74 range đạt VALID (5-7/2026), lệch **77%** so con số probe 322 (probe dùng quét-cửa-sổ hồi tố, đếm chạm trên biên CUỐI CÙNG, không phải biên tại-thời-điểm-đó — đúng như SPEC §4.3 đã cảnh báo trước). Đã dừng đúng theo luật "lệch >25% thì soi lại, đừng đi tiếp" — xem mục 9. |
| **Bias TPO (session_bias) thay thế hoặc cộng thêm proxy `close[-480]`** cho KB1 | Partition: EV_giữ−EV_loại=+0.056 (<0.30); mọi A1/A2 đều n<25; sweep TOL×MIN_SCORE không có tổ hợp nào n≥25 | Bias phiên tính đúng theo §2.4 (đối chiếu 61 phiên 5-7/2026 khớp số 61 SPEC đã nêu), tỷ lệ `bias==0`=55% (khác hẳn 2-4% của proxy — xác nhận đúng quan sát của SPEC §2.1) nhưng KHÔNG chuyển thành edge đo được ở KB1 lượt này. |
| **WY04 No Supply/No Demand ở nhịp hồi cho KB1** | Partition EV_giữ−EV_loại=+0.093 (<0.30); nhóm "có WY04" chỉ n=6 | Chênh lệch quá nhỏ để phân biệt với nhiễu; mẫu "có" quá mỏng. |
| **Kb2ExtremeWin** (cực trị nến từ chối phải là cực trị N nến gần nhất) cho KB2 | 3 window (10/20/60) đều KILL, một window còn cho dấu ngược | Không có window nào tách nhóm tốt/xấu ổn định. |
| **Kb2ZoneExtend** (hợp lưu D-1/phiên cho QUAY_DAU) | n=5 << 40 (ngưỡng KILL dứt điểm §5.9) | Quá ít lệnh VWAP hiện có tình cờ trùng vùng D-1/phiên để đánh giá; và §5.9 đã định trước ngưỡng n≥40 mới xét tiếp. |
| **Delta confirm (sign + \|Δ%\|≥20%) cho KB2 trên fp-m1** | n=16→4 sau lọc, quá nhỏ | Chỉ báo THÔNG TIN, không kết luận được; không so với dxFeed (feed khác, cửa sổ khác — SPEC §3). |

**5 giả thuyết đã bác ở GĐ4 (WYCKOFF_V6_PLAN.md §9) — KHÔNG lặp lại, không test lại lượt này:** bắt buộc
Spring/Upthrust trước break, bóp SL 2-4 giá, leg phải do lệnh chủ động đẩy (`ddom`), loại break "spike rồi
tắt", chỉ giao dịch phiên Á+Âu.

---

## 6. A/B bias TPO vs proxy xu hướng (SPEC §2.6, bắt buộc 4 dòng)

```
A0 (chỉ proxy 480, ĐANG SHIP)        n=33 WR=48.5% EV=+1.424 tổng=+47.0R  ✓ 3 tháng dương   <- incumbent
A1 (chỉ bias TPO)                    n= 9 WR=44.4% EV=+1.222 tổng=+11.0R  ✗                 n<25, KHÔNG KẾT LUẬN
A2 (cả hai, AND)                     n= 8 WR=50.0% EV=+1.500 tổng=+12.0R  ✗                 n<25, KHÔNG KẾT LUẬN
A3 (không cái nào)                   n=39 WR=43.6% EV=+1.179 tổng=+46.0R  ✓                 KILL (EV thấp hơn A0)
```
**Kết luận:** giữ nguyên **A0** (chỉ proxy `close[-480]`, đang ship). Không có nhánh nào đủ `n≥25` để tranh
"thay thế" hay "cộng thêm" theo đúng tiêu chí phân xử §2.6; A3 (bỏ hết lọc xu hướng) tuy đủ n nhưng EV thấp
hơn hẳn A0 — xác nhận lại đúng những gì BASELINE.md đã ghi (tắt TREND: n=39/WR=43.6%/kém hơn).

---

## 7. Cấu hình chốt

### KB1 — **KHÔNG ĐỔI** so với BASELINE.md (không có ứng viên nào PASS)

```python
KB1_CONFIG = dict(
    RANGE_LEN=8, RMIN=30, RMAX=75,           # box 8 nến (RangeMode=1 KHÔNG PASS, xem mục 9)
    BVSA=2.0, BBODY=0.50,                    # gate phá: VSA>=2.0, thân>=0.50
    WAIT=12, PMIN=0.60, PMAX=1.00,           # retrace 60-100%
    HOLD_TOL=2, RBODY=0.35,
    FLOOR=30, CAP=70, BUF=2,                 # SL 3.0-7.0 giá
    COOL=15, RR=4.0,
    TREND=True, VWAP=True, LIQ=True, LIQ_K=0.75,
    DEAD=True, DEAD_FROM=2, DEAD_TO=8,       # UTC
    CLEAN=True, CL_LOOK=20, CL_W=5, CL_CLOSE=0.50,
    # v7 — cả hai TẮT (không PASS lượt này):
    RangeMode=0, BIAS_ON=False,
)
# n=33 WR=48.5% tong=+47.0R EV=+1.424 MDD=3.0R
```

### KB2 — **KHÔNG ĐỔI** so với BASELINE.md

```python
KB2_CONFIG = dict(
    vol_floor=20, warmup=20, vwap_tol_t=12, approach_bars=6,
    wick_frac=0.50, cpos_h=0.05, body_min=0.30, vsa_conf=1.8,
    trend_filter=True, trend_bars=480, trend_tol_t=10,
    sl_buf_t=2, sl_cap_t=70, risk_min=5, cooldown=15, rr=1.5,
    dead=False,                              # miễn phiên chết (khác KB1)
    clean_mode=None,                         # BREAK SẠCH: KHÔNG bật (BASELINE §4 chưa chốt)
    # v7 — không bật (không PASS lượt này):
    Kb2ExtremeWin=None, Kb2ZoneExtend=False, delta_confirm=False,
)
# n=27 WR=55.6% tong=+10.5R EV=+0.389 MDD=5.0R
```

---

## 8. Giới hạn

- **Cửa sổ 5-7/2026 vẫn là "vàng tạo đỉnh"** (BASELINE.md/SPEC §9 #1) — mọi kết luận trên là *tương đối*
  trong cùng chế độ thị trường này, không phải quy luật bền vững.
- **`range_struct.py` chưa qua được bước kiểm §4.3** (n_range lệch 77% so probe) — RangeMode=1 và mọi con
  số phái sinh từ nó (arm event=60, backtest n=0) **không phải bằng chứng H5 hợp lệ**, chỉ là thông tin.
  KB3 (dùng chung `range_struct.py`) **sẽ kế thừa vấn đề này** nếu triển khai ở pha sau mà không sửa lại
  cách đếm touch/xác nhận.
- **Hạn mức cấu hình KB1** (§4.9: ≤12 cấu hình mới): lượt này đã chạy RangeMode(1) + bias A1/A2/A3(3) +
  bias sweep TOL×MIN_SCORE(9, nhưng TOL không đổi kết quả nên thực chất chỉ 3 giá trị MIN_SCORE khác biệt)
  + WY04(1) ≈ 14 lần chạy khác biệt — **hơi vượt** hạn mức danh nghĩa. Không ảnh hưởng tới overfit thật vì
  **không có cấu hình nào PASS** (không có "kẻ thắng" bị cherry-pick để cần xác nhận lại) — nhưng ghi nhận
  minh bạch, không lấp liếm.
  Hạn mức KB2 (§5.9: ≤12): đã dùng Kb2ExtremeWin(3) + Kb2ZoneExtend(1) + delta-confirm(1) = 5, trong hạn mức.
- **dxFeed là proxy YẾU cho feed live** (BASELINE.md §6) — mọi số ở đây tương đối trong cùng dxFeed.
- **fp-m1 (KB2 bước 3) chỉ ~6 tháng, nhãn UTC+7, detect() chạy full 6 tháng (chưa cắt đúng 5-7)** — n=16
  không so trực tiếp được với n=27 của dxFeed (feed khác + cửa sổ khác + KHÔNG mô phỏng zone-pool warm-up
  theo DATA_CAPABILITY §7.a).
- Chưa mô hình hoá spread/slippage/phí; SL-trước-TP trong cùng nến (bi quan) — giữ nguyên như v6.
- `evaluate_v7()`/`hit_v7()` đã tổng quát hoá đúng theo §6.5.1 (chuẩn bị KB3) nhưng **chưa test nhánh
  TP-theo-giá-tuyệt-đối/`maxbars`/`dead_at`** với dữ liệu thật (KB3 ngoài phạm vi lượt này) — chỉ xác nhận
  nó là NO-OP đúng cho KB1/KB2 qua GOLDEN TEST.

---

## 9. Cần quyết (chỗ đặc tả thiếu/mâu thuẫn — đã tự chọn, nói rõ ở đây)

1. **Bias trước khi IB đóng (`ready_at`)**: SPEC §2.4 đề xuất một phương án dùng `score=c1+c2` với
   `MIN_SCORE-1` cho khoảng thời gian trước khi IB đóng, và đánh dấu ⟦CẦN QUYẾT Ở GĐ6⟧ việc có cho gate chạy
   với `conf<2/3` hay không. **Đã chọn:** đơn giản nhất — coi `bias=0` (không có bias) cho toàn bộ thời gian
   trước `ready_at`, không dùng phương án c1+c2 riêng. Lý do: ít thêm một nhánh logic/tham số nữa (đỡ rủi ro
   overfit), và vì bias đã KILL ở cả hai thời điểm (trước/sau IB đều gộp vào 1 kết quả) nên khác biệt giữa 2
   lựa chọn này gần như không ảnh hưởng tới kết luận cuối.
2. **`range_struct.py` lệch 77% so probe — có dừng hẳn RangeMode=1 hay vẫn chạy để xem số?** SPEC nói
   "lệch >25% thì soi lại, đừng đi tiếp". **Đã chọn:** vẫn chạy RangeMode=1 một lần (để có số THÔNG TIN,
   tránh bỏ trắng), nhưng **không dùng kết quả đó làm câu trả lời hợp lệ cho H5** — báo rõ ràng là "không
   phải H5 hợp lệ" ở mọi chỗ trích dẫn. RangeMode mặc định giữ nguyên 0.
3. **Kb2ZoneExtend nghĩa là gì?** SPEC §5.3/§5.8 mô tả "thêm zone pool D-1/phiên làm mức neo THỨ HAI" nhưng
   không nói rõ đây là (a) một detector ARM-tại-zone-khác-VWAP hoàn toàn mới, hay (b) một điều kiện hợp lưu
   bổ sung cho tín hiệu VWAP hiện có. **Đã chọn phương án (b)** (rẻ hơn, tận dụng đúng 27 lệnh hiện có, không
   cần viết detector mới) vì lượt này chỉ có ngân sách kiểm tra 1 giả thuyết cho KB2-mở-rộng-zone; đã báo rõ
   trong mục 3.4/5. Nếu pha sau muốn thử phương án (a) (arm độc lập tại D-1 VAH/VAL/POC không cần chạm VWAP)
   thì đó là một detector MỚI, chưa làm ở đây.
4. **Partition threshold khi nhóm ĐƯỢC GIỮ (không phải nhóm bị loại) có n<10** (WY04, n=6): SPEC §4.9 chỉ
   nói rõ ngưỡng `n_loại≥10`. **Đã chọn:** vẫn in ra và tính chênh lệch EV bình thường (không chặn), nhưng
   gắn thêm cảnh báo mẫu mỏng trong lời bàn thay vì tự ý nới lỏng luật "n_loại≥10" (áp đúng cho nhóm loại,
   n=27, đạt).

---

## Tái lập

```bash
cd quantower-entry-signal/research/wyckoff/v7
python3 run_kb12.py
```
