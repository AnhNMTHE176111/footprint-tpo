# AUDIT_V7 — phản biện GĐ6/GĐ7

> Viết 2026-07-29. Vai của pha này là **cố bác bỏ**, không phải xây dựng. Mặc định là nghi ngờ: một kết quả
> chỉ PASS khi tôi đã thử bác mà không bác được.
>
> Đối tượng: [RESULTS_KB12.md](RESULTS_KB12.md) (GĐ6) · [RESULTS_KB3.md](RESULTS_KB3.md) (GĐ7).
> Mốc so: [BASELINE.md](BASELINE.md). Luật: [SPEC_V7_3KB.md](../../SPEC_V7_3KB.md) §8/§9 ·
> [WYCKOFF_V6_PLAN.md](../../WYCKOFF_V6_PLAN.md) §9-11 · [DATA_CAPABILITY.md](../DATA_CAPABILITY.md).
>
> **Không sửa một dòng code sản phẩm nào.** Mọi script kiểm nằm riêng ở [audit/](audit/). Mọi con số dưới đây
> là output thật của script trong thư mục đó — không có số nào gõ tay. Tái lập: xem mục cuối.

---

## 0. Bảng phán quyết

| Mục | Phán quyết | Một câu lý do |
|---|---|---|
| **A** Look-ahead | **FAIL** | `calc_volfloor()` là percentile-30 volume của **toàn bộ** dữ liệu ≥2026-05 → dùng ở mọi nến: cắt chuỗi cho 5.0/5.0/6.0/12.0/16.0 thay vì 17.0 ở 5/5 điểm cắt. Thêm 1 look-ahead thứ hai trong phép đo rotation của RESULTS_KB3.md §4 (dùng biên **cuối cùng** của range) làm số đó cao hơn 10.4 điểm. |
| **B** Tái lập độc lập | **PASS** | Tự chạy lại cả 2 script: GOLDEN khớp, và **mọi** dòng số tôi đối chiếu (KB1 33/+47.0R/EV+1.424, KB2 27/+10.5R/+0.389, bias 9-vs-30, WY04 6-vs-27, ExtremeWin 3 window, KB3 n=1 & n=139, portfolio n=60) khớp **tuyệt đối**, không lệch một chữ số. |
| **C** Partition tự tính lại | **PASS** (kèm cảnh báo) | Cả 7 phân hoạch (6 bộ lọc + 1 phép kiểm cơ chế) đều rời-nhau & hợp-đủ đúng pool; **mọi KILL đều đúng**. Cảnh báo: ngưỡng `gap≥0.30` có SE thật 0.28–1.22 → quy tắc này **không có sức phân giải** ở n≈30. |
| **D** Số lần thử | **CẢNH BÁO** | Cấu hình chốt của KB1 là kẻ sống sót của **≥94** cấu hình trên **cùng một** cửa sổ 3 tháng (báo cáo chỉ đếm 14 của GĐ6). KB1 vẫn sống sau hiệu chỉnh Bonferroni (p 0.0003→0.028); **KB2 chết ngay** (0.072→>1). |
| **E** Cao nguyên vs điểm nhọn | **CẢNH BÁO** | KB1 rất tốt: **17/18** trục bằng phẳng theo tiêu chí tự động, trục còn lại (`RR`) là **đơn điệu tăng** chứ không phải đỉnh nhọn ⇒ **18/18 không có điểm nhọn**. KB2: `rr`/`cpos_h` răng cưa, 2 trục NO-OP ⇒ bề mặt EV nằm trong nhiễu. Và `report.sweep()` **đếm cấu hình trùng lặp làm láng giềng** → thổi phồng "có cao nguyên". |
| **F** ⭐ OOS thật | **FAIL** | Cửa sổ 2025-11→2026-04 **không chạy được**: chỉ **171** nến qua gate trên 6 tháng so với **52.160** nến của 3 tháng in-sample (**0,33%**). KB1/KB2/KB3/portfolio đều **n=0**. ⇒ **không có một bằng chứng OOS nào** cho toàn bộ dự án. |
| **G** Đối chứng 2 nguồn | **CẢNH BÁO** | Phát hiện **lỗi dữ liệu mới**: cột Volume của `fp-m1-6-month.csv` **hỏng 74% trong tháng 6/2026** (22.297/30.088 nến có Volume=0 dù OHLC đúng). Sau khi loại tháng 6, 2 nguồn khớp **15/15 lệnh, EV giống nhau tuyệt đối**. |
| **H** Chi phí giao dịch | **PASS** | KB1 sống tới **>40 tick**/lệnh, KB2 tới **9 tick**, portfolio tới **27 tick** — đều xa mức thực tế 2–3 tick của vàng. KB3 **chết ở 2 tick** (củng cố KILL). |
| **I** Giả định trong nến | **PASS** | **0/33, 0/27, 0/139** lệnh có cả SL và TP trong cùng nến. Biên độ bất định = **0.000R** ở cả 3 kịch bản. Giả định vô hại. |
| **J** Portfolio | **PASS** | 0 cặp lệnh chồng thời gian, 0 lệnh đếm 2 lần, tổng R = +57.5R khớp chính xác tổng 2 nhánh. |
| **K** Trung thực báo cáo | **CẢNH BÁO** | 8 khiếm khuyết, nặng nhất: **không có bất kỳ bảng tách LONG/SHORT nào** ở cả 2 báo cáo (SPEC §9 #1a bắt buộc) — và điều đó che mất việc **phía LONG của KB2 gần như bằng 0** (EV +0.154). |

**Phán quyết cuối:** `KB1 = PASS (có điều kiện)` · `KB2 = FAIL` · `KB3 = FAIL (xác nhận KILL của GĐ7)`
**CÓ ĐƯỢC PORT SANG C# KHÔNG: CÓ — nhưng CHỈ KB1, và phải sửa lỗi A trước.** Chi tiết ở §13.

---

## 1. A — Look-ahead

### 1.1 Phép kiểm cắt chuỗi (bắt buộc, 8 feature)

Cách làm: [`audit/_lib.py:derive()`](audit/_lib.py) sao lại **y hệt** vòng lặp dẫn xuất của
[`entry_dxfeed.py:98`](../entry_dxfeed.py) rồi chạy được trên **tiền tố bất kỳ**. Trước khi dùng làm bằng chứng
đã assert `derive(toàn bộ) == E.load_m1()` — **103.857 nến, 0 nến lệch**. Cắt tại 5 điểm rải đều in-sample.

| # | Feature | Cắt chuỗi tại i vs chuỗi đầy đủ tại i | Phán quyết |
|---|---|---|---|
| 1 | **`volfloor`** ([entry_dxfeed.py:399](../entry_dxfeed.py)) | `5.0 / 5.0 / 6.0 / 12.0 / 16.0` vs `17.0` — **5/5 KHÁC** | ❌ **LOOK-AHEAD** |
| 2 | `liqratio` ([cbr_v6.py:79](cbr_v6.py)) | khớp 5/5 (vd 0.515582 = 0.515582) | ✅ nhân-quả |
| 3 | `trend` ([cbr_v6.py:73](cbr_v6.py)) | khớp 5/5 | ✅ |
| 4 | `vwap` | khớp 5/5 (vd 4668.93) | ✅ |
| 5 | `vma` / `vratio` | khớp 5/5 | ✅ |
| 6 | `session_bias` ([features.py:46](v7/features.py)) | khớp 5/5 (−1 / 0 / 0 / 1 / 0) | ✅ |
| 7 | `range_struct_scan` state+biên ([features.py:149](v7/features.py)) | khớp 5/5 cả `state`, `i0`, `rhi`, `rlo` | ✅ |
| 8 | `build_zones` ([entry_dxfeed.py:163](../entry_dxfeed.py)) | mọi zone backtest dùng tại t **đều** tính được từ B[0..t] (thiếu = 0 ở 5/5) | ✅ |

> Ghi chú trung thực về #8: lần chạy đầu báo "lệch 5 zone", nhưng đó là **artifact của chính phép cắt** (block
> đang hình thành bị đóng sớm trên chuỗi cắt nên sinh thêm 5 zone POC/VAH/VAL/Đỉnh/Đáy). Kiểm lại theo hướng
> đúng (`full_ready≤t ⊆ cut`) cho **thiếu = 0** — chuỗi đầy đủ là bản **bảo thủ hơn**.
> Đây là lỗi của tôi ở lần chạy đầu, không phải lỗi của GĐ6.

Ba kiểm bổ sung theo đúng danh sách của brief:

- **Gate ở nến vào hay nến phá?** ✅ đúng nến vào. [`engine.py:102-105`](v7/engine.py) đọc `bj` (nến vào j),
  **0 lần** đọc `b` (nến phá i) trong đoạn gate — khớp [`cbr_v6.py:242`](cbr_v6.py) và `RunnerSignal.cs:570`.
- **TPO/IB của phiên đang chạy?** ✅ không. `session_bias` chỉ đọc `D[s-1]`, `D[s-2]` (phiên đã đóng);
  `bias_at[i]` bị gate bởi `B[i]['dt'] >= ready_at` ([features.py:67](v7/features.py)). IB của phiên hiện tại
  chỉ vào `c3`, và nếu phiên kết thúc trước khi đủ IB thì **không có nến nào** có `dt ≥ ready_at` nên bias
  không bao giờ được đọc → không rò rỉ.
- **Dedup/cooldown dùng lệnh sau để loại lệnh trước?** ✅ không. Cắt `raw` tại 5 mốc rồi dedup+cooldown trên
  tiền tố → kết quả **luôn là tiền tố đúng** của kết quả toàn chuỗi (5/5 `True`).
- **KB3 `dead_at`/`maxbars`:** ✅ nhân-quả. 90/196 lần chạm có `dead_at`, **0 ca** có `dead_at ≤ nến vào`.
  Đây là một **luật thoát** đọc trạng thái tại đúng nến j, triển khai được live.

### 1.2 FAIL #1 — `volfloor` (lỗi cùng họ với `avg_vma` mà BASELINE §5 tưởng đã sửa hết)

```python
# entry_dxfeed.py:399
def calc_volfloor(B):
    liq=[b['v'] for b in B if b['ym']>='2026-05']   # <-- TOÀN BỘ cửa sổ, kể cả tương lai
    liq.sort()
    p30=liq[int(len(liq)*0.30)] if liq else 20
    return max(5.0,p30)
```

Giá trị này (`17.0`) được truyền vào `_gate(b, vf)` ([cbr_v6.py:89](cbr_v6.py)) ở **mọi** nến, kể cả nến tháng
5/2026 — tức ngưỡng lọc thanh khoản của tháng 5 được tính từ volume tháng 6-7. Đúng lớp lỗi mà
[BASELINE.md §5](BASELINE.md) ghi là đã sửa (`avg_vma` toàn chuỗi → `liqratio` cuộn 1000 nến): việc sửa đã bỏ
sót `volfloor`.

**Đo tác động thật (quan trọng — đây là chỗ tôi bác không thành công):**

```
KB1 với volfloor NHÌN TRƯỚC (=17.0, như GĐ6 chạy):
  n= 33 WR=48.5% tổng=+47.0R EV=+1.424 MDD=3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓
KB1 với volfloor = 20 (số CỨNG trong RunnerSignal.cs — KHÔNG look-ahead):
  n= 33 WR=48.5% tổng=+47.0R EV=+1.424 MDD=3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓   <-- GIỐNG HỆT
KB1 với volfloor cuộn nhân-quả (p30 của 1000 nến trước, mỗi nến 1 ngưỡng):
  n= 31 WR=45.2% tổng=+39.0R EV=+1.258 MDD=4.0R | 05:+4.0 06:+18.0 07:+17.0 ✓
```

Kết luận cân bằng: **lỗi là thật và phải sửa**, nhưng nó **không làm sai con số in-sample của KB1** — vì cái
thực sự ship (C# hardcode 20) cho **kết quả y hệt**. Lỗi trở thành **chí tử ở mọi cửa sổ khác**: trong phép
kiểm OOS (§7), `vf=17` được suy ra **100% từ tương lai** của cửa sổ đó.

**Cách sửa:** trong `entry_dxfeed.calc_volfloor`, hoặc (a) trả về hằng `20.0` cho khớp C#, hoặc (b) đổi thành
ngưỡng cuộn nhân-quả như [`audit/a1_truncate.py:scan_causal_vf`](audit/a1_truncate.py). **Số phải chạy lại nếu
chọn (b):** toàn bộ bảng của BASELINE/RESULTS_KB12/RESULTS_KB3 (KB1 đổi 33→31, +47.0→+39.0R). Nếu chọn (a):
không số nào đổi.

### 1.3 FAIL #2 — phép đo rotation của RESULTS_KB3.md §4 dùng biên **cuối cùng** của range

[`kb3_range_report.py:_resolve`](v7/kb3_range_report.py) nhận `rhi/rlo` lấy từ `last[i0]` — tức trạng thái ở
**nến cuối đời** của range, và `end_bar` — nến range chết. Cả hai là thông tin tương lai so với nến chạm `i`.
Tách riêng phần này ([`audit/k_rotation_null.py`](audit/k_rotation_null.py) K.3):

```
dùng biên CUỐI CÙNG (như GĐ7):     n=175 rot=55 brk=58 cen=62 -> xoay/đã phân giải = 48.7%
dùng biên TẠI NẾN CHẠM (nhân-quả): n=218 rot=57 brk=92 cen=69 -> xoay/đã phân giải = 38.3%
chênh do look-ahead biên = +10.4 điểm
```

Không đổi kết luận KILL của KB3 (KILL đến từ backtest, dùng biên nhân-quả) — nhưng **con số 48.7% bị thổi
+10.4 điểm**. Xem thêm §9.

### 1.4 Look-ahead "hợp pháp" cần ghi rõ

Phân hoạch quyết định của KB3 ([`run_kb3.py:146`](v7/run_kb3.py) `find_favorable_break`) **dùng thông tin
tương lai** (range sau này vỡ theo hướng nào) để chia mẫu → **không triển khai được live**. Nhưng vì nó dẫn
tới **KILL**, hướng look-ahead này **làm mạnh** kết luận: phần thực sự giao dịch được (n=117) có EV −0.254R,
còn phần +EV (n=22) **không thể chọn ra ở thời điểm vào lệnh**. Đây là cách dùng look-ahead đúng đắn và
GĐ7 đã diễn giải đúng.

---

## 2. B — Tái lập độc lập

Tự chạy `python3 run_kb12.py` và `python3 run_kb3.py` từ đầu (log đầy đủ, exit 0 cả hai) và đối chiếu **13**
dòng số quan trọng nhất, không tin bảng trong báo cáo:

| Dòng | Báo cáo | Tôi chạy lại | Lệch |
|---|---|---|---|
| GOLDEN cbr_v6 vs engine v7 | n=33 EV+1.424, cùng bộ (i,side) `True` | y hệt, `True` | 0 |
| KB1 incumbent | n=33 WR48.5% +47.0R EV+1.424 MDD3.0 | y hệt | 0 |
| KB2 incumbent | n=27 WR56% EV+0.389 +10.5R | y hệt | 0 |
| `n_range` state machine | 74 (lệch 77% so probe 322) | 74, lệch 77% | 0 |
| ARM event 5-7/2026 | 60 | 60 | 0 |
| RangeMode=1 | n=0 | n=0 | 0 |
| bias A1/A2/A3 | n=9/8/39, EV+1.222/+1.500/+1.179 | y hệt | 0 |
| bias partition | GIỮ 9 EV+1.222 · LOẠI 30 EV+1.167 · gap+0.056 | y hệt | 0 |
| WY04 partition | CÓ 6 EV+1.500 · KHÔNG 27 EV+1.407 · gap+0.093 | y hệt | 0 |
| Kb2ExtremeWin 10/20/60 | gap −0.125 / +0.288 / +0.176 | y hệt | 0 |
| KB3 bản trần | n=1, EV+3.067 | n=1, EV+3.067 | 0 |
| KB3 hình-học-thuần | n=139 WR29.5% +13.1R EV+0.094 MDD27.5 | y hệt | 0 |
| Portfolio KB1+KB2 | n=60 +57.5R EV+0.958 | n=60 +57.5R EV+0.958 | 0 |
| KB3 §4 rotation | 175 chạm, 55/58/62, 48.7%/31.4%, null 3.7% | y hệt | 0 |

**Không lệch một con số nào.** Cả hai báo cáo trung thực về mặt tái lập — điều này đáng ghi nhận rõ ràng, vì
đó là điều kiện cần để mọi phản biện còn lại có nghĩa. `B = PASS`.

---

## 3. C — Partition tự tính lại (kèm sai số chuẩn)

GĐ6/GĐ7 **không tuyên bố bộ lọc nào PASS**, nên việc của mục này là: (a) kiểm toàn vẹn phân hoạch;
(b) tìm bộ lọc bị **KILL oan**; (c) thêm sai số chuẩn — thứ mà cả 2 báo cáo đều không có.

```
                                                                 gap      SE     t      KTC95            rời-nhau
KB1 bias      GIỮ  9 EV+1.222 | LOẠI 30 EV+1.167              +0.056   0.992  +0.06  [-1.888,+1.999]   OK
KB1 WY04      CÓ   6 EV+1.500 | KHÔNG 27 EV+1.407             +0.093   1.221  +0.08  [-2.300,+2.485]   OK
KB2 win=10    GIỮ 15 EV+0.333 | LOẠI 12 EV+0.458              -0.125   0.499  -0.25  [-1.103,+0.853]   OK
KB2 win=20    GIỮ 13 EV+0.538 | LOẠI 14 EV+0.250              +0.288   0.493  +0.58  [-0.679,+1.256]   OK
KB2 win=60    GIỮ 10 EV+0.500 | LOẠI 17 EV+0.324              +0.176   0.514  +0.34  [-0.831,+1.184]   OK
KB3 hợp lưu   CÓ  66 EV+0.223 | KHÔNG 73 EV-0.022             +0.245   0.280  +0.88  [-0.303,+0.793]   OK
KB3 vỡ-thuận  CÓ  22 EV+1.948 | CÒN LẠI 117 EV-0.254          +2.203   0.291  +7.56  [+1.632,+2.773]   OK
```

- **Toàn vẹn: 7/7 phân hoạch rời nhau và hợp lại đúng pool gốc.** Không có lệnh nào lọt hoặc bị đếm 2 lần.
- **Không bộ lọc nào bị KILL oan.** Mọi `t` đều < 1.0 → **không phân biệt được với 0**. KILL là đúng.
- Riêng phân hoạch `vỡ-thuận` có `t=+7.56` — thật và rất mạnh. Đó chính là bằng chứng KILL của KB3, và nó
  vững.

**CẢNH BÁO về chính quy tắc quyết định:** ngưỡng `gap ≥ 0.30` được đặt trong SPEC §4.9/§5.9/§6.9, nhưng SE
thật ở đây là **0.28–1.22**. Tức ngưỡng nằm **trong** nhiễu: dưới giả thuyết "bộ lọc vô dụng" với SE≈0.5, xác
suất một bộ lọc ngẫu nhiên đạt gap ≥0.30 là **P(Z≥0.6) ≈ 27%**. Thử 6 bộ lọc ⇒ kỳ vọng **~1,6 lần PASS giả**.
GĐ6/GĐ7 được **0** — đó là **may**, không phải quy tắc tốt. Quy tắc này cần thay bằng "gap ≥ 2×SE" hoặc phải
nâng n; nếu không, lần sau nó sẽ chứng nhận nhiễu thành bộ lọc thật.

**Hệ quả cho câu chữ báo cáo:** RESULTS_KB12.md §2/§3.3 gọi win=20 là *"chưa đạt 0.30, **sát ngưỡng**"* và
RESULTS_KB3.md §6.3 gọi hợp lưu là *"**khá gần ngưỡng** 0.30"*. Với KTC95 = [−0.679,+1.256] và
[−0.303,+0.793], **không có gì "sát"** — cả hai cách xa 0 đúng 0,58σ và 0,88σ. Cách diễn đạt này gợi ý
"gần thành công" ở nơi chỉ có nhiễu thuần. Xem §12 mục 5.

---

## 4. D — Số lần thử (multiple comparisons)

Đếm từ chính các script (số lời gọi in kết quả — là **cận dưới**, vì sweep trong vòng lặp sinh nhiều dòng hơn
số call site):

| Nguồn | Cấu hình KB1 | Cấu hình KB2 | Cấu hình KB3 |
|---|---:|---:|---:|
| `cbr_v6.py main()` (14 toggle + baseline) | 15 | — | — |
| `stack_v6.py` | 11 | — | — |
| `round3_v6.py` | 17 | — | — |
| `round4_v6.py` | 9 | — | — |
| `final_table.py` | 17 | — | — |
| `parity_fix.py` | 9 | — | — |
| `imp_reversal_sweep.main()` (11 trục × 4-6 giá trị) | — | 52 | — |
| BASELINE §4 BREAK SẠCH | — | 3 | — |
| **GĐ6** `run_kb12.py` (RangeMode 2 + bias 4 + sweep 9 + WY04 1) | ~16 | 6 | — |
| **GĐ7** `run_kb3.py` (tự khai) | — | — | 7 |
| **TỔNG (cận dưới)** | **≥94** | **≥61** | **≥7** |

**Hai điều báo cáo không nói:**
1. RESULTS_KB12.md §8 đếm **14** cấu hình (GĐ6) và kết luận *"không ảnh hưởng tới overfit thật vì không có
   cấu hình nào PASS"*. Đúng **cho riêng GĐ6**. Nhưng cấu hình chốt **không phải** là "không có kẻ thắng" —
   nó là **v6 baseline**, và v6 baseline chính là kẻ thắng của **~78 cấu hình trước đó** trên **cùng cửa sổ
   5-7/2026**. Báo cáo coi baseline là "mốc so" cho sẵn, chứ không phải một cấu hình **đã được chọn**.
2. `n=33` với ≥94 cấu hình ⇒ mức chiết khấu phải rất lớn. Định lượng bằng §6 (Monte Carlo):

| Kịch bản | p đơn lẻ (null vào-lệnh-ngẫu-nhiên) | Số cấu hình | p sau Bonferroni | Kết luận |
|---|---:|---:|---:|---|
| **KB1** | **0.0003** | 94 | **0.028** | vẫn có ý nghĩa ở 5% — **sống** |
| **KB2** | 0.072 | 61 | **>1 (4.4)** | **chết ngay**, không cần tinh vi hơn |
| KB3 | — (đã KILL) | 7 | — | — |

**Mức chiết khấu kỳ vọng phải áp khi trích số:**
- **KB1**: EV bảng +1.424R. Bonferroni còn sống ⇒ chiết khấu **trung bình**, không phải triệt tiêu. Cộng thêm
  bằng chứng cao nguyên (§5: 18/18 trục không có điểm nhọn — bề mặt phẳng nghĩa là ít "phí chọn lọc"), tôi cho
  rằng kỳ vọng thực tế nên lấy **quanh EV null-p95 → observed**, tức **+0.7 đến +1.4R**, và **giả định phần
  dưới** khi tính vốn.
- **KB2**: EV bảng +0.389R ⇒ kỳ vọng thực tế phải giả định **0** cho tới khi có dữ liệu mới.
- Vì `n<40` cho **mọi** quyết định và số cấu hình >20 ở cả KB1 và KB2 → theo đúng luật của brief:
  **ghi CẢNH BÁO OVERFIT CAO** cho cả hai.

---

## 5. E — Vùng bằng phẳng vs điểm nhọn

GĐ6/GĐ7 **không chốt tham số mới nào** (mọi ứng viên đều KILL) ⇒ cái thực sự bị đóng băng để port là **cấu
hình v6**. Vậy phải kiểm cao nguyên ở **chính những tham số đó**, không phải ở các ứng viên đã bị loại.
Sweep 1 tham số một lần, 5 giá trị mỗi trục. Script: [`audit/e_plateau.py`](audit/e_plateau.py).

### 5.1 KB1 — 18 trục (90 lần chạy engine)

```
RR          2.0:EV+0.82(n33)  3.0:EV+1.30(n33)  4.0:EV+1.42(n33)*  5.0:EV+1.73(n33)  6.0:EV+2.18(n33)
PMAX        0.8:EV+1.86(n21)  0.9:EV+1.41(n29)  1.0:EV+1.42(n33)*  1.1:EV+1.22(n36)  1.2:EV+1.22(n36)
PMIN        0.4:EV+1.00(n45)  0.5:EV+1.09(n43)  0.6:EV+1.42(n33)*  0.7:EV+1.04(n27)  0.8:EV+0.25(n16)
RANGE_LEN     6:EV+1.18(n39)    7:EV+1.35(n34)    8:EV+1.42(n33)*    9:EV+1.42(n33)   10:EV+0.60(n25)
RMIN         20:EV+1.22(n36)   25:EV+1.22(n36)   30:EV+1.42(n33)*   35:EV+1.50(n32)   40:EV+1.59(n29)
RMAX         55:EV+1.86(n14)   65:EV+1.50(n22)   75:EV+1.42(n33)*   85:EV+1.18(n39)   95:EV+1.25(n40)
BVSA        1.5:EV+0.98(n48) 1.75:EV+1.18(n39)  2.0:EV+1.42(n33)* 2.25:EV+1.33(n30)  2.5:EV+1.05(n22)
BBODY       0.4:EV+1.16(n37) 0.45:EV+1.29(n35)  0.5:EV+1.42(n33)* 0.55:EV+1.50(n30)  0.6:EV+1.41(n29)
LIQ_K       0.5:EV+1.38(n40) 0.65:EV+1.43(n37) 0.75:EV+1.42(n33)* 0.85:EV+1.33(n30)  1.0:EV+1.04(n27)
COOL          5:EV+1.35(n34)   10:EV+1.35(n34)   15:EV+1.42(n33)*   20:EV+1.42(n33)   30:EV+1.42(n33)
WAIT          8:EV+1.41(n27)   10:EV+1.50(n30)   12:EV+1.42(n33)*   15:EV+1.50(n34)   20:EV+1.20(n41)
RBODY      0.25:EV+1.35(n34)  0.3:EV+1.42(n33) 0.35:EV+1.42(n33)*  0.4:EV+1.42(n31) 0.45:EV+1.50(n30)
HOLD_TOL      0:EV+1.42(n33)    1:EV+1.42(n33)    2:EV+1.42(n33)*    3:EV+1.42(n33)    4:EV+1.42(n33)
FLOOR        20:EV+1.58(n33)   25:EV+1.58(n33)   30:EV+1.42(n33)*   35:EV+1.42(n33)   40:EV+1.42(n33)
CAP          50:EV+1.59(n29)   60:EV+1.50(n32)   70:EV+1.42(n33)*   80:EV+1.42(n33)   90:EV+1.50(n34)
CL_LOOK      10:EV+0.98(n48)   15:EV+1.20(n41)   20:EV+1.42(n33)*   25:EV+1.22(n27)   30:EV+1.50(n20)
CL_W          3:EV+1.17(n23)    4:EV+1.26(n31)    5:EV+1.42(n33)*    6:EV+1.25(n40)    7:EV+1.14(n42)
CL_CLOSE    0.4:EV+1.67(n30) 0.45:EV+1.42(n33)  0.5:EV+1.42(n33)* 0.55:EV+1.50(n36)  0.6:EV+1.43(n37)
                                                (* = giá trị đang chốt)
```

**Kết quả: 17/18 trục cho "BẰNG PHẲNG"** theo tiêu chí (cả hai láng giềng ≥60% EV của điểm tốt nhất trên trục).

Trục duy nhất bị gắn cờ là **`RR`** — nhưng **đây là tiêu chí tự động áp sai**, và tôi phải nói rõ chứ không
lấy nó làm FAIL: `n=33` **không đổi** ở cả 5 giá trị RR (cùng bộ lệnh, chỉ đổi mục tiêu), và EV **đơn điệu
tăng** +0.82 → +1.30 → +1.42 → +1.73 → +2.18. Đó là một **đánh đổi WR/EV/MDD trên đường đơn điệu**, không phải
một đỉnh nhọn được dò ra. `RR=4.0` là lựa chọn **bảo thủ** trên đường đó (BASELINE §3 đã ghi lý do: RR3 cho WR
cao hơn 57,6%). ⇒ về bản chất chống-overfit: **18/18 trục của KB1 không có điểm nhọn nào.**

**Đây là bằng chứng ủng hộ KB1 mạnh thứ hai của audit này** (sau Monte Carlo §6): một bề mặt tham số phẳng
nghĩa là kết quả **không** được tạo ra bằng cách dò tham số. Đặc biệt `RANGE_LEN` 8 vs 9 cho **kết quả y hệt**.

**Phát hiện phụ — 4 input NO-OP hoàn toàn trên cửa sổ này** (mọi giá trị cho n=33/EV+1.42 y hệt):
`HOLD_TOL` (0-4), `COOL` (15/20/30), `FLOOR` (30/35/40), `CAP` (70/80/90). Cộng với `VwapAlign` mà
[BASELINE §3](BASELINE.md) đã ghi ⇒ **5 "lớp lọc" không hề ràng buộc**. Đừng tính chúng là lớp lọc đã chứng
minh, cũng đừng xoá (chúng có thể ràng buộc ở regime khác).

### 5.2 KB2 — 10 trục (50 lần chạy)

```
rr            1.0:EV+0.33(n27)  1.25:EV+0.33(n27)  1.5:EV+0.39(n27)*  2.0:EV+0.22(n27)  2.5:EV+0.43(n27)   RĂNG CƯA
vwap_tol_t      6:EV+0.41(n23)     9:EV+0.41(n23)   12:EV+0.39(n27)*   16:EV+0.25(n30)   20:EV+0.25(n32)   bằng phẳng
vsa_conf      1.4:EV+0.25(n40)   1.6:EV+0.29(n33)  1.8:EV+0.39(n27)*  2.0:EV+0.56(n24)  2.2:EV+0.43(n21)   đơn điệu (chốt KHÔNG ở đỉnh)
approach_bars   3:EV+0.39(n27)     4:EV+0.39(n27)    6:EV+0.39(n27)*    8:EV+0.39(n27)   12:EV+0.39(n27)   NO-OP
wick_frac     0.4:EV+0.17(n32)  0.45:EV+0.34(n28)  0.5:EV+0.39(n27)* 0.55:EV+0.30(n23)  0.6:EV+0.25(n12)   bằng phẳng
body_min      0.2:EV+0.17(n45)  0.25:EV+0.14(n35)  0.3:EV+0.39(n27)* 0.35:EV+0.62(n17)  0.4:EV+0.79(n7)    đơn điệu (n sụp)
cpos_h        0.0:EV+0.32(n38)  0.02:EV+0.43(n35) 0.05:EV+0.39(n27)*  0.1:EV+0.25(n22) 0.15:EV+0.25(n20)   răng cưa
cooldown        5:EV+0.39(n27)    10:EV+0.39(n27)   15:EV+0.39(n27)*   20:EV+0.39(n27)   30:EV+0.39(n27)   NO-OP
trend_tol_t     0:EV+0.38(n29)     5:EV+0.43(n28)   10:EV+0.39(n27)*   20:EV+0.39(n27)   30:EV+0.35(n26)   bằng phẳng
sl_cap_t       40:EV+0.25(n22)    55:EV+0.25(n24)   70:EV+0.39(n27)*   85:EV+0.39(n27)  100:EV+0.39(n27)   bằng phẳng
```

Đọc trung thực: **`rr` và `cpos_h` răng cưa thật** (rr: +0.33 → +0.33 → +0.39 → **+0.22** → +0.43 với **cùng
n=27** — tức đổi RR chỉ **xáo lại** ai thắng ai thua một cách ngẫu nhiên; đó là dấu hiệu kinh điển của mẫu quá
nhỏ, không phải của một tham số có ý nghĩa). `vsa_conf` và `body_min` **đơn điệu tăng** với `n` sụp nhanh
(0.4 → EV+0.79 nhưng chỉ **n=7**) — đáng ghi nhận là GĐ trước **không** chọn điểm tốt nhất mà giữ giá trị LIVE,
tức **không** cherry-pick. 2 trục **NO-OP** (`approach_bars`, `cooldown`) — khớp đúng
[BASELINE §3](BASELINE.md) đã ghi.

⇒ Không phải "KB2 bị overfit tham số" (không ai dò ra đỉnh); mà là **toàn bộ bề mặt EV của KB2 nằm trong
nhiễu** — nhất quán với kết luận §6 (p=0.072).

### 5.3 Lỗi trong chính công cụ kiểm cao nguyên

[`report.sweep()`](v7/report.py) (dòng 75) đếm `neigh_ok` = số **dòng** có `EV ≥ 0.6×best`, trừ 1. Sweep bias
của GĐ6 là 3 `TOL` × 3 `MIN_SCORE` = 9 dòng, **nhưng `TOL` là NO-OP** (log xác nhận: 0.2/0.5/1.0 cho EV y
hệt nhau ở mọi `MIN_SCORE`) ⇒ thực chất chỉ **3 cấu hình khác biệt**, mỗi cái lặp 3 lần. Hàm này đếm:
3 dòng (MS=1, EV+1.500) + 3 dòng (MS=2, EV+1.222) = 6, trừ 1 = **5**, rồi in
*"5 cấu hình khác đạt ≥60% EV của điểm tốt nhất (có cao nguyên)"*.

Nhưng theo **trục tham số thật** (`MIN_SCORE`): 1 → 2 → 3 = +1.500 → +1.222 → **0.000**. Láng giềng phía trên
của điểm tốt nhất **sụp về 0**.

⇒ **`report.sweep()` đếm cấu hình trùng lặp làm láng giềng ⇒ thổi phồng cao nguyên.** Lần này **không gây
hại** (bias đã bị KILL bằng partition, không phải bằng sweep), nhưng hàm này **sẽ** chứng nhận sai một đỉnh
nhọn thành cao nguyên ở bất kỳ sweep nào có trục no-op. **Cách sửa:** dedup theo giá trị EV (hoặc theo tổ hợp
tham số **có tác dụng**) trước khi đếm láng giềng, và đếm theo **khoảng cách trên trục**, không theo số dòng.

---

## 6. Phép kiểm thay thế cho OOS — null vào lệnh ngẫu nhiên

Vì OOS thật không chạy được (§7), đây là phép bác bỏ mạnh nhất còn lại. Script:
[`audit/stat_null.py`](audit/stat_null.py).

**D.1 — binomial so WR hoà vốn** (null yếu: "vào lệnh hoàn toàn vô nghĩa"):

```
KB1 (RR=4.0)  n=33 thắng=16 WR=48.5%  WR hoà vốn=20.0%  P(X>=16|p=0.20) = 2.27e-04  CÓ Ý NGHĨA
KB2 (RR=1.5)  n=27 thắng=15 WR=55.6%  WR hoà vốn=40.0%  P(X>=15|p=0.40) = 7.43e-02  KHÔNG CÓ Ý NGHĨA
```

**D.2 — Monte Carlo, null MẠNH** (giữ nguyên số lệnh, phân bố `side`, phân bố `risk_t`, cùng tập nến hợp lệ,
chỉ **chọn nến vào ngẫu nhiên**; 3000 mô phỏng). Đây là null trả lời đúng câu hỏi *"có phải chỉ cần RR 4:1
trong một thị trường có xu hướng mạnh là đủ?"*:

```
KB1: EV quan sát = +1.424
     EV null: med=+0.061  p05=-0.545  p95=+0.667  max(3000)=+1.576
     p-value = 0.0003   -> QUAN SÁT VƯỢT NULL RÕ RỆT
KB2: EV quan sát = +0.389
     EV null: med=+0.019  p05=-0.352  p95=+0.389  max=+0.759
     p-value = 0.0720   -> KHÔNG phân biệt được với may mắn
```

KB2 quan sát nằm **đúng bằng p95 của null**. Đó là định nghĩa của "không phân biệt được".

**D.3 — null đảo phía** (cùng nến vào, cùng risk, đảo `side`):

```
KB1 đảo phía: n=33 tổng= -3.0R EV=-0.091   (thật: +47.0R EV=+1.424)
KB2 đảo phía: n=27 tổng= -7.0R EV=-0.259   (thật: +10.5R EV=+0.389)
```

**Tôi đã cố bác KB1 bằng null mạnh nhất tôi dựng được và bác không được.** Đây là bằng chứng ủng hộ KB1
mạnh nhất trong toàn dự án và nó **chưa từng tồn tại trước pha audit này**. Ngược lại, KB2 chết.

**D.4 — tách LONG/SHORT** (SPEC §9 #1a bắt buộc, **cả 2 báo cáo đều thiếu hoàn toàn**):

```
KB1 LONG   n=14 WR=42.9% tổng=+16.0R EV=+1.143 MDD=4.0R | 05:-1.0(n1) 06:+7.0(n8) 07:+10.0(n5) ✗
KB1 SHORT  n=19 WR=52.6% tổng=+31.0R EV=+1.632 MDD=3.0R | 05:+6.0(n4) 06:+15.0(n10) 07:+10.0(n5) ✓
KB2 LONG   n=13 WR=46%  EV=+0.154 net=+2.0R   [05:+0R(1/2) 06:+0R(2/5) 07:+2R(3/6)]
KB2 SHORT  n=14 WR=64%  EV=+0.607 net=+8.5R   [05:+2R(1/1) 06:+2R(3/5) 07:+4R(5/8)]
```

- **KB1: cả hai phía đều dương** (+1.143 / +1.632) ⇒ KB1 **không** chỉ là hiện tượng của regime "vàng tạo
  đỉnh". Đây là điểm mạnh thật.
- **KB2: phía LONG gần như bằng 0** (+0.154R, 8/13 = 2.0R trong 3 tháng). Toàn bộ +10.5R của KB2 đến từ
  **8,5R của phía SHORT** trong đúng cửa sổ mà SPEC §9 #1 đã cảnh báo là "SHORT được ưu ái". Rủi ro số 1
  của sổ rủi ro **đã hiện thực hoá ở KB2** — và bảng che nó đi vì không tách phía.

---

## 7. ⭐ F — OOS thật 2025-11 → 2026-04

Đây là mục có giá trị nhất của pha này. Script: [`audit/f_oos.py`](audit/f_oos.py).

### 6.1 Đo độ dày dữ liệu TRƯỚC khi kết luận

```
thang       n_nen  n_ngay  nen/ngay   v>=17   v>=20  _gate OK
2025-11       551      22        25       9       9         0
2025-12       957      25        38       5       5         0
2026-01      2188      26        84      64      61         1
2026-02      2112      24        88      15      13         0
2026-03      6933      27       257     134     105        10
2026-04     15199      25       608     617     458       160
-------------------------------------------------------------
2026-05     20336      26       782    5639    5155      5033
2026-06     30088      26      1157   26498   25537     26165
2026-07     25493      23      1108   21201   20058     20962

nến qua _gate: OOS(6 tháng)=171   IN-SAMPLE(3 tháng)=52.160   tỷ lệ OOS/IS = 0,33%
```

Một ngày giao dịch CME có ~1.380 phút. Tháng 11/2025 có **25 nến/ngày** — tức GCQ26 gần như **không giao
dịch**. Trung vị volume 6 tháng OOS là **1,0–2,0 hợp đồng/nến** so với **43–55** của tháng 6-7/2026.

### 6.2 Bảng OOS đầy đủ theo tháng

| Nhánh | Cấu hình | 2025-11 | 2025-12 | 2026-01 | 2026-02 | 2026-03 | 2026-04 | Tổng OOS | (mốc in-sample) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **KB1** | chốt, vf=17 (nhìn trước) | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=33 +47.0R EV+1.424 |
| **KB1** | chốt, vf=20 (C#, sạch) | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=33 +47.0R EV+1.424 |
| **KB1** | vf cuộn nhân-quả (chẩn đoán) | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=31 +39.0R EV+1.258 |
| **KB2** | chốt LIVE (vol_floor=20) | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=27 +10.5R EV+0.389 |
| **KB2** | vol_floor=2 (**chẩn đoán**, nới gate) | 0 | 0 | 0 | +0.0R (n=2) | 0 | **−2.0R (n=7)** | **n=9 WR33% EV−0.167 net−1.5R** | n=34 +16.0R EV+0.471 |
| **KB3** | bản trần | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=1 |
| **KB3** | hình-học-thuần | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=139 EV+0.094 |
| **Portfolio** | KB1+KB2 (vf=20) | 0 | 0 | 0 | 0 | 0 | 0 | **n=0** | n=60 +57.5R EV+0.958 |

Số range VALID theo tháng: `25-11=0 25-12=0 26-01=0 26-02=0 26-03=0 26-04=0` | `26-05=4 26-06=31 26-07=39`
→ KB3 không có **một** range nào trong 6 tháng OOS (0 lần chạm), nên n=0 không nói gì về KB3.

**Tháng dữ liệu quá mỏng — nói rõ, không gộp im lặng:** cả **6/6 tháng OOS** đều quá mỏng. 2025-11 và 2025-12
gần như không có nến nào qua gate (0 và 0). Chỉ 2026-04 có 160 nến qua gate — vẫn là 0,3% của một tháng
in-sample.

### 6.3 Phán quyết F — và tôi phải nói ngược lại một tiền đề của brief

Brief nêu: *"dxFeed có dữ liệu từ 2025-11-02 … Vậy 2025-11 → 2026-04 là out-of-sample thật sự, chưa bị nhìn."*
**Dữ liệu bác tiền đề này.** Cửa sổ đó có nến (551–15.199/tháng) nhưng **không có thanh khoản**: 171 nến qua
gate trên 6 tháng. Đây **không phải** một cửa sổ OOS — nó là khoảng thời gian trước khi hợp đồng GCQ26 bắt
đầu giao dịch thật. [BASELINE.md §6](BASELINE.md) (*"mở rộng cửa sổ về trước là RÁC, không phải
out-of-sample"*) và [SPEC §9 #1c](../../SPEC_V7_3KB.md) (*"OOS thật phải là front-month/CCPA khác"*) **đúng**, và
tôi xác nhận bằng số của chính mình.

Vì vậy phán quyết **không phải** "OOS âm ⇒ FAIL vì overfit", mà là:

> **F = FAIL** — không phải vì kết quả OOS xấu, mà vì **không tồn tại bằng chứng OOS nào**. 100% số liệu của
> KB1/KB2/KB3 là in-sample trên **một** cửa sổ 3 tháng, **một** chế độ thị trường (vàng tạo đỉnh), **một**
> hợp đồng. Kết hợp với §4 (≥94 cấu hình), đây là rủi ro lớn nhất còn lại của cả dự án.
>
> Điểm dữ liệu OOS **duy nhất** tồn tại trên toàn bộ repo: KB2 với gate nới (`vol_floor=2`) cho
> **n=9, EV −0.167R** trên 2026-02/04. n=9 quá nhỏ để kết luận, nhưng đó là **dấu âm**, và nó là *đúng hướng
> với* mọi kết quả tiêu cực khác của KB2 (§6).

**Cái này là *chế độ thị trường* hay *overfit*?** Không thể phân xử bằng dữ liệu hiện có — và đó chính là vấn
đề. Muốn phân xử phải có **dữ liệu hợp đồng khác** (front-month/CCPA) như SPEC §9 #1c đã ghi. Trong lúc chưa
có: **live log chính là phép OOS đầu tiên**, và phải được đối xử như vậy (§13).

---

## 8. G — Đối chứng 2 nguồn (phát hiện một lỗi dữ liệu mới)

Script: [`audit/g_fpm1.py`](audit/g_fpm1.py), [`audit/g2_volume_diff.py`](audit/g2_volume_diff.py),
[`audit/c_partition_g3.py`](audit/c_partition_g3.py) mục G.7.

Sửa 2 khiếm khuyết của cách GĐ6 làm ([`run_kb12.py:230`](v7/run_kb12.py)): GĐ6 chạy fp-m1 **không quy đổi
UTC+7 → UTC** (SPEC §1.2 bắt buộc) và chạy **cả 6 tháng** rồi so n=16 với n=27 của 3 tháng. Tôi quy đổi −7h
và cắt đúng cùng cửa sổ.

### 7.1 Giá khớp tuyệt đối — nhưng VOLUME thì không

```
nến trùng mốc thời gian = 99.678   chỉ có ở fp-m1 = 0   chỉ có ở dxFeed = 0
max |close_fp - close_dx| = 0.00 tick   số nến lệch close = 0
max |vol_fp  - vol_dx|    = 3655        số nến lệch volume = 22.297   (22,4%)
```

Bóc theo tháng thì lỗi **khu trú hoàn toàn ở tháng 6/2026**:

| tháng | n_nến | n_lệch | %lệch | tổng V fp-m1 | tổng V dxFeed | fp/dx | max lệch | số ca fp>dx |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-01 | 592 | 0 | 0,0% | 1.597 | 1.597 | 1.000 | 0 | 0 |
| 2026-02 | 2.112 | 0 | 0,0% | 4.527 | 4.527 | 1.000 | 0 | 0 |
| 2026-03 | 6.933 | 0 | 0,0% | 20.502 | 20.502 | 1.000 | 0 | 0 |
| 2026-04 | 15.199 | 0 | 0,0% | 61.530 | 61.530 | 1.000 | 0 | 0 |
| 2026-05 | 20.336 | 0 | 0,0% | 530.571 | 530.571 | 1.000 | 0 | 0 |
| **2026-06** | **30.088** | **22.297** | **74,1%** | **594.207** | **2.718.972** | **0,219** | **3.655** | **0** |
| 2026-07 | 24.418 | 0 | 0,0% | 1.790.589 | 1.790.589 | 1.000 | 0 | 0 |

**`fp>dx` = 0 ở mọi ca lệch, và các ca lệch lớn nhất đều là `V_fp = 0` với `V_dx` = 2.000-3.655.** Tức:
**cột Volume của `fp-m1-6-month.csv` bị mất 78% khối lượng tháng 6/2026 — 22.297 nến có Volume = 0 dù OHLC
hoàn toàn đúng.** Đây là **lỗi dữ liệu chưa từng được ghi ở đâu**;
[DATA_CAPABILITY §4.1](../DATA_CAPABILITY.md) chỉ đối chiếu **một ngày (2026-07-10)** — một ngày tháng 7,
khớp hoàn hảo — nên không thể thấy.

**Vì sao nghiêm trọng:** `vratio = v/SMA20(v)` là **gate trung tâm** của cả KB1 (`BVSA=2.0`) và KB2
(`vsa_conf=1.8`); `volfloor` và `liqratio` cũng chỉ từ volume:

```
KB1 BVSA>=2.0      (5-7/2026, 74.842 nến): cả 2 đạt=5.555  chỉ dxFeed=2.083  chỉ fp-m1=  7  -> không nhất quán 27,3%
KB2 vsa_conf>=1.8  (5-7/2026, 74.842 nến): cả 2 đạt=6.903  chỉ dxFeed=2.683  chỉ fp-m1= 10  -> không nhất quán 28,1%
```

### 7.2 Đối chứng SẠCH: loại tháng 6, cùng `volfloor=20`

```
KB1, chỉ tháng 05 + 07/2026, volfloor=20 trên CẢ HAI nguồn:
  KB1 dxFeed        n=15 WR=53.3% tổng=+25.0R EV=+1.667 MDD=3.0R | 05:+5.0(n5) 07:+20.0(n10) ✓
  KB1 fp-m1 (-7h)   n=15 WR=53.3% tổng=+25.0R EV=+1.667 MDD=3.0R | 05:+5.0(n5) 07:+20.0(n10) ✓
  khớp từng lệnh (dt,side): 15/15 — chỉ dx=0, chỉ fp=0            <-- TRÙNG KHỚP TUYỆT ĐỐI
KB2, 05+07:
  KB2 dxFeed  nsig=17 closed=17 WR 59% EV+0.471 net +8.0R
  KB2 fp-m1   nsig=15 closed=15 WR 53% EV+0.333 net +5.0R
  khớp từng lệnh: 15 | chỉ dx=2 chỉ fp=0
```

- **KB1 tái lập 100% trên nguồn thứ hai** (15/15 lệnh y hệt, EV giống hệt) khi dữ liệu còn nguyên. Rất mạnh.
- KB2 còn lệch 2 lệnh, và giải thích được: `vma` (SMA20) và `trend_at` (480 nến) của các nến **đầu tháng 7**
  còn với lùi vào tháng 6 hỏng → `vratio` lệch ở ~20 nến đầu tháng. Tức phần dư cũng do đúng lỗi tháng 6.

### 7.3 Hệ quả cho kết luận cũ về "WR 61% vs 42%"

[DATA_CAPABILITY §4.3](../DATA_CAPABILITY.md) kết luận chênh lệch WR 61% (fp-m1) vs 42% (dxFeed) là do
**zone-pool "lạnh"**, và ghi *"KHÔNG phải hạn chế của dữ liệu thô"*. Cửa sổ điều tra đó là **6/26 → 7/25** —
**bao gồm cuối tháng 6**, đúng chỗ Volume hỏng. Vậy tồn tại một **cơ chế thứ hai mà §4 chưa từng xét**. Kết
luận §4.3 vì thế **chưa được thiết lập**: chưa thể quy toàn bộ chênh lệch cho zone-pool. **Phải chạy lại**
điều tra đó sau khi (a) loại tháng 6 khỏi fp-m1, hoặc (b) xuất lại `fp-m1-6-month.csv`.

**Phán quyết G = CẢNH BÁO.** Đối chứng 2 nguồn **thành công ở nơi dữ liệu còn nguyên** (KB1 khớp 15/15) — đó
là điểm cộng thật cho KB1 — nhưng chỉ phủ **2 tháng**, và một báo cáo trước đó cần sửa.

---

## 9. Kiểm riêng tuyên bố DƯƠNG duy nhất của RESULTS_KB3.md (§4)

RESULTS_KB3.md §4 kết luận: *"48.7% vs null 3.7% → **CÓ edge cấu trúc rõ rệt**"*. KB3 đã KILL, nhưng đây là
tuyên bố dương duy nhất của báo cáo và nếu ai hồi sinh KB3 sẽ dựa vào nó — nên phải kiểm.
Script: [`audit/k_rotation_null.py`](audit/k_rotation_null.py).

**Hai nghi vấn:**
1. Null `p = BUF/(BUF+width) = 0.2/5.2 ≈ 3,7%` là first-passage của bước ngẫu nhiên với **hai rào chắn lệch
   hẳn nhau** (0,2 giá vs 5,0 giá), trong khi biến cố được đếm là "chạm biên đối diện trước khi **close** vượt
   biên gần + BUF", cộng thêm nhóm `censored` chiếm 35%. So 48,7% (**có điều kiện** trên "đã phân giải") với
   3,7% (**không điều kiện**, rào chắn khác) là **so lệch loại**.
2. Nghiêm trọng hơn: bộ phát hiện **chỉ phát ra range khi giá ĐÃ nảy qua lại ≥2 lần mỗi biên trong ≥30 nến**.
   Đo "có nảy tiếp không" rồi so với null bỏ qua chính sự chọn lọc đó là **vòng tròn**.

**Placebo đúng cách:** giữ y nguyên độ rộng + thời lượng + dùng chính `_resolve()`, nhưng neo dải giá ở một
mốc thời gian **ngẫu nhiên** khác (tâm dải = close tại mốc đó), 200 mô phỏng:

```
số lần chạm placebo: med=323   (thật = 175)
tỷ lệ xoay / đã phân giải:  med=17.2%  p05=12.4%  p95=22.9%    (THẬT = 48.7%)
tỷ lệ xoay / toàn bộ:       med=14.6%  p05=10.4%  p95=19.3%    (THẬT = 31.4%)
p-value (placebo đạt >= tỷ lệ thật) = 0.000
```

**Tôi bác không được phần định tính:** 48,7% **thật sự** vượt placebo (p=0,000). Có rotation cấu trúc thật.

**Nhưng độ lớn bị thổi phồng hai lần:**
- Null đúng là **~17%**, không phải 3,7% → báo cáo phóng đại tỷ lệ vượt từ **2,8×** thành **13×** (4,6 lần).
- Bỏ look-ahead biên (§1.3): 48,7% → **38,3%**.
- Con số trung thực: **~38,3% vs null ~17%** — vẫn là edge, nhưng là một câu chuyện khiêm tốn hẳn.

**Phán quyết:** hướng của §4 đúng, **độ lớn sai đáng kể**. Không đổi KILL. Phải sửa câu chữ để lần sau không ai
hồi sinh KB3 bằng lý lẽ "tốt gấp 13 lần ngẫu nhiên".

---

## 10. H — Độ nhạy chi phí

Script: [`audit/hij_cost_inbar_portfolio.py`](audit/hij_cost_inbar_portfolio.py).
Mô hình: chi phí **cố định cả vòng** `cost_ticks`/lệnh, quy về R của **chính lệnh đó**
(`dR = cost_ticks / risk_t`, `risk_t` khác nhau từng lệnh — đây là điểm mấu chốt: nhánh có R nhỏ chịu nặng
hơn hẳn).

| Nhánh | med `risk_t` | EV 0t | EV 1t | **EV 2t** | EV 3t | EV 5t | **Chết ở** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **KB1** (RR4) | 36,0 tick | +1.424 | +1.397 | **+1.369** | +1.341 | +1.286 | **>40 tick** |
| **KB2** QUAY_DAU (RR1.5) | 21,2 tick | +0.389 | +0.341 | **+0.294** | +0.246 | +0.151 | **9 tick** |
| **KB3** hình-học-thuần | 15,0 tick | +0.094 | +0.029 | **−0.036** | −0.102 | −0.233 | **2 tick** |
| **Portfolio** KB1+KB2 | 32,0 tick | +0.958 | +0.922 | **+0.885** | +0.849 | +0.775 | **27 tick** |

Tổng R sau phí (cùng cửa sổ 5-7/2026):

```
KB1        0t: +47.0R   1t: +46.1R   2t: +45.2R   3t: +44.3R   5t: +42.4R
KB2        0t: +10.5R   1t:  +9.2R   2t:  +7.9R   3t:  +6.7R   5t:  +4.1R
KB3        0t: +13.1R   1t:  +4.0R   2t:  -5.1R   3t: -14.2R   5t: -32.3R
Portfolio  0t: +57.5R   1t: +55.3R   2t: +53.1R   3t: +50.9R   5t: +46.5R
```

**Ngưỡng chi phí mà edge còn sống:** KB1 **>40 tick** (4,0 giá — xa mọi mức thực tế), KB2 **9 tick** (0,9 giá),
portfolio **27 tick**. Chi phí thực tế của vàng M1 (spread 1 tick + slippage 1-2 tick cả vòng ≈ **2-3 tick**)
⇒ **KB1 và KB2 đều sống**; đây **không** phải chỗ giết chúng.

**KB3 chết ở 2 tick — đúng ngưỡng mà [SPEC §9 #4](../../SPEC_V7_3KB.md) đã đặt trước** (*"EV sau khi trừ 2
tick/lệnh < +0.15R → KB3 không đáng ship"*): EV(2t) = **−0.036R**. Đây là **lý do KILL thứ 4** cho KB3 mà
RESULTS_KB3.md không nêu vì không có cột này (§12 mục 2).

---

## 11. I & J — Giả định trong nến và Portfolio

### 10.1 I — biên độ bất định trong nến

| Nhánh | n | n có cả SL và TP trong 1 nến | % | EV (SL trước, bi quan) | EV (TP trước, lạc quan) | **Biên độ** |
|---|---:|---:|---:|---:|---:|---:|
| KB1 (RR4) | 33 | **0** | 0,0% | +1.424 | +1.424 | **±0.000** |
| KB2 (RR1.5) | 27 | **0** | 0,0% | +0.389 | +0.389 | **±0.000** |
| KB3 bản trần | 1 | **0** | 0,0% | +3.067 | +3.067 | **±0.000** |
| KB3 hình-học-thuần | 139 | **0** | 0,0% | +0.094 | +0.094 | **±0.000** |

**Phán quyết I = PASS, dứt điểm.** Ngưỡng SPEC §9 #5 là 15%; thực tế **0%**. Kết quả **không phụ thuộc chút
nào** vào giả định "SL trước TP". Hợp lý về cơ chế: KB1 cần một nến M1 chứa cả 3,6 giá ngược và 14,4 giá
thuận (18 giá) — không xảy ra trong 3 tháng. Đây là một trong hai rủi ro của SPEC §9 mà tôi **loại bỏ hẳn**
được (rủi ro #5). Điều đáng nói là **không báo cáo nào đo nó** dù SPEC bắt buộc.

### 10.2 J — Portfolio

```
tổng lệnh 2 nhánh (chưa router) = 60  (KB1 33 + KB2 27)
J.1 số CẶP lệnh CHỒNG THỜI GIAN = 0
    thời gian giữ lệnh (phút): med=9  p90=57  max=203
J.2 router 1-vị-thế: giữ 60, bỏ {}          (báo cáo: n=60, bỏ {} — KHỚP)
    PORTFOLIO sau router  n=60 WR=51.7% tổng=+57.5R EV=+0.958 MDD=5.0R | 05:+7.0(n8) 06:+24.5(n28) 07:+26.0(n24) ✓
    PORTFOLIO cộng gộp không router  n=60 ... +57.5R ... (giống hệt)
J.3 lệnh bị đếm 2 lần (cùng nhánh+dt+side) = 0 ; mốc thời gian có >1 lệnh = 0
J.4 tổng R: KB1=+47.0  KB2=+10.5  cộng=+57.5  = portfolio sau router +57.5   KHỚP
```

**Phán quyết J = PASS trên cả 3 câu hỏi của brief.** Giải thích cơ chế: trung vị giữ lệnh chỉ **9 phút**, và
60 lệnh rải trên 75 ngày giao dịch (26+26+23) ⇒ 0 chồng lấn là hợp lý, không phải lỗi.

**Một điểm suy luận cần chỉnh (không phải lỗi số):** RESULTS_KB3.md §8 viết *"Router đã kiểm: dòng KB1+KB2 tái
lập đúng BASELINE.md (n=60) → **router đúng**"*. Phép kiểm đó **không chứng minh** router đúng — nó chỉ cho
thấy router **chưa bao giờ được kích hoạt** (bỏ 0 lệnh). Kết luận tình cờ đúng (tôi đã kiểm độc lập: thật sự
0 chồng lấn) nhưng lập luận thì không đứng. Hệ quả thực: **logic 1-vị-thế của router vẫn chưa được test bởi
bất kỳ dữ liệu nào** — nó sẽ chạy lần đầu tiên trên live. Ghi vào §13.

---

## 12. K — Trung thực báo cáo

**Đã kiểm và KHÔNG tìm thấy vấn đề** (ghi nhận rõ ràng):
- ✅ **Không** tháng âm nào bị gộp để làm đẹp tổng: mọi dòng đều in `05:/06:/07:` và dấu ✓/✗ đúng.
- ✅ **Không** có `n<25` nào bị gọi là "cải thiện". Cả 2 báo cáo dán nhãn "KHÔNG KẾT LUẬN" đúng chỗ (A1 n=9,
  A2 n=8, KB3 bản trần n=1, delta fp-m1 n=4).
- ✅ **Không** feature nào thuộc SPEC §8 (không kiểm được offline) được bật mặc định: `delta_confirm=False`;
  `Kb3AbsorbBonus`/`AbsDom` chưa được viết dòng nào.
- ✅ Việc lệch 77% của `range_struct_scan` **được nêu bật, không bị chôn** — cả 2 báo cáo tự hạ cấp
  RangeMode=1 xuống "chỉ THÔNG TIN". Đó là hành xử đúng.
- ✅ Mục "Giới hạn" của cả 2 báo cáo thẳng thắn và khá đầy đủ (dxFeed proxy yếu, n nhỏ, chưa mô hình phí,
  SL-trước-TP, cửa sổ 1 regime).

**8 khiếm khuyết tìm được:**

| # | Khiếm khuyết | Ở đâu | Mức |
|---|---|---|---|
| 1 | **Không có một bảng tách LONG/SHORT nào** trong cả 2 báo cáo (grep = 0 lần) dù [SPEC §9 #1a](../../SPEC_V7_3KB.md) bắt buộc *"mỗi lần trích số"*. Che mất việc **KB2 LONG EV chỉ +0.154R** (§6 D.4). | cả 2 báo cáo | **Nặng** |
| 2 | **Thiếu cột "EV sau khi trừ 2 tick/lệnh"** cho **mọi** bảng KB3, dù SPEC §9 #4 bắt buộc. Nếu có, sẽ thấy KB3 EV(2t) = −0.036R = lý do KILL thứ 4. | RESULTS_KB3.md | **Nặng** |
| 3 | **Không đếm** số lệnh có cả SL và TP trong cùng nến cho KB3, dù SPEC §9 #5 bắt buộc. (Thực tế = 0% — tin tốt, nhưng vẫn là mục bắt buộc bị bỏ.) | RESULTS_KB3.md | Trung bình |
| 4 | Trích dẫn **"`range_struct.py`"** như một file, ≥6 lần. **File đó không tồn tại** — logic ở `features.range_struct_scan()`. SPEC §1.3 đặt tên 7 module (`range_struct.py`, `bias_tpo.py`, `force.py`, `s1_breakret.py`, `s2_zonereact.py`, `router.py`); **chỉ `s3_edge2edge.py` được tạo đúng tên**. Người đọc theo báo cáo không tìm được file. Kèm theo: link `[SPEC_V7_3KB.md](../SPEC_V7_3KB.md)` ở đầu **cả 2 báo cáo** sai độ sâu (phải là `../../`) nên **không mở được** — tôi đã mắc đúng lỗi này và đã sửa trong file này. | RESULTS_KB12.md, RESULTS_KB3.md | Trung bình |
| 5 | Gọi gap +0.288 là **"sát ngưỡng"** và gap +0.245 là **"khá gần ngưỡng"**, trong khi KTC95 là [−0.679,+1.256] và [−0.303,+0.793] — cách 0 đúng **0,58σ** và **0,88σ**. Gợi ý "gần thành công" ở nơi chỉ có nhiễu. | KB12 §2/§3.3, KB3 §6.3 | Trung bình |
| 6 | **"48.7% vs 3.7% → CÓ edge cấu trúc rõ rệt"**: null sai loại (đúng là ~17%) và +10.4 điểm là look-ahead. Số trung thực ≈ 38,3% vs 17%. | RESULTS_KB3.md §4 | **Nặng** |
| 7 | *"Router đã kiểm… → router đúng"* suy ra từ một phép kiểm mà router **chưa hề được kích hoạt** (bỏ 0 lệnh). | RESULTS_KB3.md §8 | Nhẹ |
| 8 | Kiểm kê số cấu hình chỉ tính **14 của GĐ6 / 5 của KB2 / 7 của KB3**, bỏ qua **~78 cấu hình trước đó** đã chọn ra chính v6 baseline trên **cùng** cửa sổ (§4). Coi baseline là "mốc cho sẵn" thay vì "cấu hình đã được chọn". | KB12 §8 | **Nặng** |

**Phán quyết K = CẢNH BÁO.** Không có dấu hiệu bịa số hay che tháng âm — mọi số đều tái lập được (§2). Nhưng
**3 mục bắt buộc của SPEC §9 bị bỏ** (#1a, #4, #5), và 3 chỗ diễn đạt làm kết quả trông mạnh hơn thực tế
(#5, #6, #8).

---

## 13. Phán quyết cuối cho từng kịch bản

### KB1 = **PASS (có điều kiện)**

**Đã cố bác bằng 8 hướng và không bác được:**

| Hướng bác | Kết quả |
|---|---|
| Look-ahead làm đẹp số? | Không — `vf=20` (số C# thật, sạch) cho **y hệt** n=33/+47.0R/EV+1.424 |
| Chỉ là RR 4:1 trong thị trường có xu hướng? | Không — Monte Carlo 3000 lần vào-lệnh-ngẫu-nhiên cùng hình học rủi ro: med +0.061, p95 +0.667, max +1.576; quan sát +1.424 ⇒ **p=0.0003** |
| Chỉ là regime SHORT của "vàng tạo đỉnh"? | Không — **cả hai phía dương**: LONG +1.143 (n=14), SHORT +1.632 (n=19); đảo phía cho −0.091 |
| Đỉnh nhọn do tinh chỉnh? | Không — **18/18** trục không có điểm nhọn (17 bằng phẳng + `RR` đơn điệu); `RANGE_LEN` 8 vs 9 cho kết quả **giống hệt**; `HOLD_TOL`/`COOL`/`FLOOR`/`CAP` là NO-OP hoàn toàn |
| Chết vì chi phí? | Không — sống tới **>40 tick**/lệnh (thực tế 2-3 tick) |
| Nhạy với giả định trong nến? | Không — **0/33** lệnh bị ảnh hưởng, biên độ ±0.000R |
| Là artefact của một nguồn dữ liệu? | Không — fp-m1 tái lập **15/15 lệnh y hệt** (05+07, `vf=20`) |
| Là kẻ thắng may mắn của ≥94 cấu hình? | Sống — Bonferroni: p 0.0003 × 94 = **0.028** < 0.05 |

**Nhưng PASS này có điều kiện, và điều kiện là thật:** `n=33`, **một** cửa sổ 3 tháng, **một** regime, **một**
hợp đồng, **không có một điểm dữ liệu OOS nào** (§7). Bằng chứng đủ để **thử bằng vốn nhỏ và ghi log**, không
đủ để coi là hệ thống đã được xác nhận.

### KB2 = **FAIL**

| Bằng chứng | Số |
|---|---|
| Null vào-lệnh-ngẫu-nhiên | EV quan sát +0.389 = **đúng p95 của null** ⇒ p=0.072 |
| Binomial vs WR hoà vốn 40% | p=0.074 (không có ý nghĩa ở 5%) |
| Sau hiệu chỉnh ≥61 cấu hình | p → **>1** |
| Tách phía (chưa từng báo cáo) | **LONG EV +0.154R** (n=13) — gần bằng 0; 8,5R/10,5R đến từ SHORT trong regime tạo đỉnh |
| Điểm dữ liệu OOS duy nhất tồn tại | n=9, WR 33%, **EV −0.167R** |
| Chi phí | chết ở 9 tick (còn sống ở 2-3 tick, nhưng biên mỏng: EV+0.294 ở 2t) |
| n | 27 lệnh / 3 tháng; `LOWcell` ở mọi tháng (tháng 5 chỉ n=3) |

Không phải "KB2 sai" — mà là **KB2 chưa được chứng minh, và mọi phép kiểm độc lập đều cho dấu trung tính đến
âm**. `BASELINE.md §4` đã treo BREAK SẠCH cho nhánh này là "CHƯA CHỐT"; audit này không tháo được nút đó.

### KB3 = **FAIL — xác nhận KILL của GĐ7, và KILL còn vững hơn báo cáo tưởng**

Tôi đã cố **cứu** KB3 (vì brief yêu cầu bác bỏ, kể cả bác bỏ một KILL) và không cứu được:

- §6.9(d) — phần không phải "KB1 sớm": EV **−0.254R**, `t = +7.56` cho phân hoạch ⇒ dứt điểm và có ý nghĩa
  thống kê thật.
- Chi phí: chết ở **2 tick**, EV(2t) = **−0.036R** < ngưỡng +0.15R của SPEC §9 #4 ⇒ **lý do KILL thứ 4**.
- MDD 27,5R ở cấu hình lỏng nhất (trần KILL 10,0R).
- OOS: **0 range VALID** trong 6 tháng ⇒ không có gì để cứu.
- Tuyên bố dương duy nhất (§4) bị thổi phồng 2 lần (§9) — số thật 38,3% vs null 17%, không phải 48,7% vs 3,7%.

**Bổ sung cho GĐ7:** phát hiện "thanh khoản mâu thuẫn cơ chế" (`liqratio` tại chạm med 0.30 vs 0.79 toàn
chuỗi) là một quan sát **thật và có giá trị** — tôi tái lập đúng. Nhưng nó **không phải** lý do KILL: ngay cả
khi bỏ hẳn gate đó, KB3 vẫn chết vì 4 lý do trên.

### **CÓ ĐƯỢC PORT SANG C# KHÔNG: CÓ — nhưng CHỈ KB1, và phải làm 3 việc trước**

| | Port? | Điều kiện |
|---|---|---|
| **KB1** | **CÓ** | 3 điều kiện bắt buộc dưới đây |
| **KB2** | **KHÔNG** như một nhánh ăn vốn thật. Được port ở dạng **bật-log-tắt-vốn** (`EnableReversal=false` mặc định) để thu OOS thật từ live. | — |
| **KB3** | **KHÔNG.** Không có `KB3_CONFIG`. Không viết dòng code nào. | — |

**3 điều kiện bắt buộc trước khi port KB1:**
1. **Sửa lỗi look-ahead `volfloor`** ([entry_dxfeed.py:399](../entry_dxfeed.py)). Cách rẻ nhất và **không đổi
   số nào**: chốt `20.0` cho khớp `RunnerSignal.cs` (đã chứng minh ở §1.2 cho kết quả y hệt). Nếu chọn ngưỡng
   cuộn nhân-quả thì **phải chạy lại toàn bộ BASELINE** (KB1 thành n=31/+39.0R/EV+1.258).
2. **Router 1-vị-thế chưa từng được test bởi dữ liệu nào** (§11.2: bỏ 0 lệnh trong 3 tháng). Phải có unit test
   tổng hợp cho nhánh "bỏ vì đang có vị thế" trước khi tin nó trên live.
3. **Coi live log là phép OOS đầu tiên** và ghi rõ điều đó vào BASELINE: theo §4, kỳ vọng thực tế của KB1 phải
   **chiết khấu về khoảng +0.7…+1.4R/lệnh**, không lấy +1.424R làm dự báo. Kích thước vị thế phải tính theo
   đầu dưới.

---

## 14. Cấu hình ĐÃ ĐÓNG BĂNG cho GĐ9 (không được đổi ở GĐ9)

```python
# ===== KB1 — DUY NHẤT được port ăn vốn. Y HỆT BASELINE.md, không một tham số nào đổi.
KB1_CONFIG = dict(
    RANGE_LEN=8, RMIN=30, RMAX=75,            # tick;  span 3.0-7.5 giá
    BVSA=2.0, BBODY=0.50,
    WAIT=12, PMIN=0.60, PMAX=1.00,
    HOLD_TOL=2, RBODY=0.35,
    FLOOR=30, CAP=70, BUF=2,
    COOL=15, RR=4.0,
    TREND=True, VWAP=True, LIQ=True, LIQ_K=0.75,
    DEAD=True, DEAD_FROM=2, DEAD_TO=8,        # UTC (DeadUseUtc=true)
    CLEAN=True, CL_LOOK=20, CL_W=5, CL_CLOSE=0.50,
    RangeMode=0, BIAS_ON=False,               # v7: cả hai TẮT (không PASS)
    VOL_FLOOR=20.0,                           # <<< ĐÓNG BĂNG SỐ CỨNG — sửa lỗi look-ahead §1.2
)
# In-sample 5-7/2026: n=33 WR=48.5% tổng=+47.0R EV=+1.424 MDD=3.0R  (LONG n=14 EV+1.143 / SHORT n=19 EV+1.632)
# EV sau 2 tick phí: +1.369   |   OOS: KHÔNG CÓ   |   Kỳ vọng dùng để tính vốn: +0.7R (đầu dưới)

# ===== KB2 — port ở dạng TẮT MẶC ĐỊNH, chỉ để thu log OOS. KHÔNG cấp vốn.
KB2_CONFIG = dict(
    vol_floor=20, warmup=20, vwap_tol_t=12, approach_bars=6,
    wick_frac=0.50, cpos_h=0.05, body_min=0.30, vsa_conf=1.8,
    trend_filter=True, trend_bars=480, trend_tol_t=10,
    sl_buf_t=2, sl_cap_t=70, risk_min=5, cooldown=15, rr=1.5,
    dead=False, clean_mode=None,
    Kb2ExtremeWin=None, Kb2ZoneExtend=False, delta_confirm=False,
    ENABLED_DEFAULT=False,                    # <<< AUDIT: p=0.072, LONG EV+0.154 -> chưa cấp vốn
)

# ===== KB3 — KHÔNG CÓ CẤU HÌNH. Không port.
```

**Ba input đã xác nhận là NO-OP trên cửa sổ này** (đừng tính là lớp lọc đã chứng minh, đừng xoá):
`VwapAlign` (BASELINE đã ghi), và bổ sung từ audit này: `HOLD_TOL` (0-4 cho kết quả y hệt), `COOL` (15/20/30
y hệt), `FLOOR` (30/35/40 y hệt), `CAP` (70/80/90 y hệt), KB2 `approach_bars` (3-12 y hệt), KB2 `cooldown`
(5-30 y hệt).

---

## 15. Những gì audit này KHÔNG kiểm được

Trung thực về giới hạn của **chính pha audit**:

1. **Không tạo ra được bằng chứng OOS.** Đây là giới hạn lớn nhất và không thể vượt bằng dữ liệu trong repo.
   Tôi chỉ chứng minh được rằng cửa sổ mà brief chỉ định **không dùng được** (§7) — không thay thế được nó.
   Phép kiểm Monte Carlo (§6) là *thay thế*, không *tương đương*: nó bác được "may mắn thuần trong cùng cửa
   sổ", **không** bác được "edge chỉ tồn tại trong chế độ thị trường vàng-tạo-đỉnh".
2. **Không kiểm được parity Python ↔ C#.** Toàn bộ audit chạy trên `cbr_v6.py`/`imp_reversal_sweep.py`. Nợ hạ
   tầng "Replicator CBR exact" ([BASELINE §7](BASELINE.md)) vẫn còn: `Dedup` gộp 2 nhánh chưa mô phỏng, C# bỏ
   nến cuối còn Python quét hết. Nếu `WyckoffRunner.cs` lệch logic thì mọi số ở đây không áp cho bản ship.
3. **Không kiểm được spread/slippage thật.** §10 dùng **mô hình** chi phí cố định 1-5 tick vì
   [DATA_CAPABILITY §6](../DATA_CAPABILITY.md) xác nhận không export nào có spread. Chi phí thật có thể phụ
   thuộc giờ/biến động (tệ hơn đúng vào lúc KB1 vào lệnh — nến VSA≥2.0 là nến biến động cao). **Chưa đo được
   điều này.**
4. **Không kiểm được `fp-m1` tháng 6 là lỗi export hay lỗi vendor** — chỉ chứng minh được cột Volume bằng 0
   trên 74% nến (§8.1). Muốn biết nguyên nhân phải xuất lại file.
5. **Không chạy lại `data_capability_audit.py`** để kiểm mọi tuyên bố của DATA_CAPABILITY.md — chỉ kiểm đúng
   tuyên bố §4.1 (và tìm ra lỗi ở đó). Các mục khác của file đó **chưa được audit này xác nhận**.
6. **Không kiểm 5 giả thuyết đã bác ở GĐ4** ([WYCKOFF_V6_PLAN §9](../../WYCKOFF_V6_PLAN.md): Spring/Upthrust bắt
   buộc, bóp SL 2-4 giá, `ddom`, loại spike-fade, chỉ phiên Á+Âu). Tôi tin lời GĐ4 ở đây, **chưa tự chạy lại**.
7. **Không kiểm 10 ảnh range** của RESULTS_KB3.md §3 (kiểm chứng bằng mắt). Nhận xét chất lượng bộ phát hiện
   range ở đó **chưa được xác nhận độc lập**.
8. **`report.sweep()` bị lỗi đếm trùng lặp** (§5.3) — tôi chỉ chứng minh nó **có thể** chứng nhận sai; ở lần
   này nó **không** gây hại (bias đã KILL bằng partition). Chưa đo có sweep nào ở các pha **trước** GĐ6 từng
   bị hàm này (hoặc logic tương tự) chứng nhận sai.
9. **Monte Carlo dùng `random.seed(20260729)` cố định** — p-value 0.0003 và 0.072 là của đúng hạt giống đó.
   Với 3000 mô phỏng, sai số Monte Carlo của p≈0.07 là ±0.005; của p=0.0003 thì p thật có thể trong
   khoảng ~[0, 0.002]. Kết luận không đổi, nhưng con số không phải chính xác đến chữ số cuối.
10. **Placebo rotation (§9)** giữ độ rộng + thời lượng nhưng **không** giữ độ biến động cục bộ. Một placebo
    nghiêm hơn (khớp theo ATR) có thể cho null cao hơn 17% ⇒ edge cấu trúc của range còn nhỏ hơn nữa. Tôi
    dừng ở mức này vì KB3 đã KILL bằng 4 lý do khác.

---

## Tái lập

```bash
cd quantower-entry-signal/research/wyckoff/audit
python3 a1_truncate.py            # A: cắt chuỗi 8 feature + tác động volfloor
python3 a2_zones_dedup.py         # A: zones / dedup / dead_at / gate ở nến vào
python3 f_oos.py                  # F: OOS 2025-11 -> 2026-04  (mục KHÔNG được bỏ)
python3 hij_cost_inbar_portfolio.py   # H, I, J
python3 e_plateau.py              # E: 18 sweep KB1 + 10 sweep KB2 + lỗi report.sweep()
python3 stat_null.py              # D: binomial + Monte Carlo + đảo phía + tách LONG/SHORT
python3 g_fpm1.py                 # G: đối chứng 2 nguồn
python3 g2_volume_diff.py         # G: định lượng lỗi Volume tháng 6 của fp-m1
python3 c_partition_g3.py         # C: partition + SE;  G.7: đối chứng sạch (loại tháng 6)
python3 k_rotation_null.py        # kiểm tuyên bố §4 của RESULTS_KB3.md bằng placebo
```

Tái lập đối tượng bị audit (đã chạy lại trong §2, exit 0 cả hai):

```bash
cd quantower-entry-signal/research/wyckoff/v7
python3 run_kb12.py
python3 run_kb3.py
```
