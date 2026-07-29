# SPEC v7 — WyckoffRunner 3 KỊCH BẢN (KB1 / KB2 / KB3)

> Viết 2026-07-29 (GĐ4 — **thiết kế**, không phải kết quả). Mục đích: GĐ6/GĐ7 implement + đo được mà
> **không phải suy luận lại**, và không lặp lại các giả thuyết đã bị bác.
>
> Nguồn đã đọc và bám theo:
> [THEORY.md](../data-export/wyckoff/THEORY.md) · [WYCKOFF_RULES.md](../data-export/wyckoff/WYCKOFF_RULES.md) ·
> [CHART_CASES.md](../data-export/wyckoff/CHART_CASES.md) · [RULES.md (pro trader CORVEN)](../data-export/messages-with-pro-trader/RULES.md) ·
> [TRANSCRIPT.md](../data-export/messages-with-pro-trader/TRANSCRIPT.md) · [DATA_CAPABILITY.md](research/DATA_CAPABILITY.md) ·
> [WYCKOFF_V6_PLAN.md](WYCKOFF_V6_PLAN.md) · [BASELINE.md](research/wyckoff/BASELINE.md) ·
> [cbr_v6.py](research/wyckoff/cbr_v6.py) · [entry_dxfeed.py](research/entry_dxfeed.py) · [WyckoffRunner.cs](WyckoffRunner.cs)
>
> **Quy ước trung thực dùng suốt file:** số nào có nguồn thì ghi nguồn; số nào tôi đề xuất mà chưa có bằng
> chứng thì ghi rõ **`⟦ĐỀ XUẤT — CẦN KIỂM⟧`**; chỗ nào tôi không đủ cơ sở để chốt thì ghi
> **`⟦CẦN QUYẾT Ở GĐ6⟧`** kèm cách quyết. Mọi số đo mới trong file này lấy từ **§11 (log probe thật)**.

---

## §0. Tóm tắt 30 giây

| KB | Là gì | Trạng thái hiện tại |
|---|---|---|
| **KB1** | Phá range → chờ hồi 60–100% → vào (tiếp diễn) | **ĐÃ CÓ, là setup CHÍNH.** v6 CBR: n=33, WR 48.5%, +47R, EV +1.424, MDD 3R ([BASELINE.md §1](research/wyckoff/BASELINE.md)) |
| **KB2** | Giá chạm vùng/VWAP → bị từ chối → fade, TP 1.5R | **ĐÃ CÓ** (nhánh QUAY_DAU): n=27, WR 55.6%, +10.5R, EV +0.389, MDD 5R |
| **KB3** | **MỚI** — scalp biên↔biên trong range đã xác nhận, TP = biên đối diện, **R biến thiên** | Chưa có dòng code nào. Hạ tầng còn thiếu: range-theo-cấu-trúc ([DATA_CAPABILITY §7.d](research/DATA_CAPABILITY.md)) |

**Setup chính vẫn là KB1** — nó là cái duy nhất đã có EV cao (+1.42R/lệnh) và MDD nhỏ (3R).

**Thứ tự implement (chi tiết ở §4.10/§5.10/§6.10):**
1. **Hạ tầng dùng chung**: `range_struct.py` (range theo cấu trúc, state machine) + `bias_tpo.py` (bias phiên).
2. **KB1**: A/B "box 8 nến (v6)" vs "range cấu trúc (v7)"; A/B bias TPO vs proxy `close[-480]`.
3. **KB3**: dùng đúng range vừa xây (dùng 1 lần cho 2 kịch bản — đây là lý do KB3 phải đi **sau** KB1).
4. **KB2**: mở rộng từ chỉ-VWAP sang zone pool. Làm cuối vì rủi ro cao nhất/khó tách nhân quả nhất.

**Rủi ro overfit lớn nhất — một câu:** KB3 có **461 lần chạm biên thô** trong 5–7/2026 (§11.B/§11.D), tức
**dư n để "tìm ra" một tổ hợp lọc thắng bằng tình cờ** — nguy hiểm ngược lại với lo ban đầu ("liệu có đủ n
không"): vấn đề của KB3 là **quá nhiều bậc tự do trên một cửa sổ 3 tháng cùng một chế độ thị trường**, nên §6.9
đặt hạn mức số cấu hình được thử và bắt buộc "thắng phải nằm trên cao nguyên", không phải một đỉnh nhọn.

---

## §1. Từ vựng & quy ước

### 1.1 Đơn vị
- **tick = 0.1** (đã kiểm ở MỌI file dữ liệu — [DATA_CAPABILITY §1](research/DATA_CAPABILITY.md)).
- **"giá" = 10 tick = 1.0 đơn vị giá.** Ví dụ 4058.0 → 4052.0 là **6.0 giá** = 60 tick.
- **Mọi ngưỡng trong file này ghi rõ đơn vị**: `giá` / `tick` / `nến` / `%` / `R`.
- `R` = |entry − SL| tính bằng **giá**. `RR` = |TP − entry| / R (không đơn vị).
- Trong `cbr_v6.py` các hằng số range/SL là **tick** (`RMIN=30` = 3.0 giá). Trong `WyckoffRunner.cs` là **giá**
  (`RangeMinPts = 3.0`). Đây là bẫy quy đổi đã tồn tại — đừng thêm bẫy mới: **module v7 dùng "giá" ở mọi nơi**,
  chỉ quy đổi sang tick ngay tại chỗ gọi engine cũ.

### 1.2 Múi giờ
- **Mọi tính toán bằng UTC.** dxFeed cột `Time left` = **UTC** (đã chứng minh 2 lần độc lập:
  [WYCKOFF_V6_PLAN §2](WYCKOFF_V6_PLAN.md) và [DATA_CAPABILITY §1.1](research/DATA_CAPABILITY.md)).
- `fp-m1-*.csv`, `TPO-chart-daily.csv`, `tpo-chart-m30.csv` mang nhãn **UTC+7** → **trừ 7 giờ trước khi ghép**
  với dxFeed hoặc trước khi cắt khung giờ. Không bao giờ so trực tiếp.
- **Phiên (session) trong hệ này bắt đầu ~22:00 UTC** (đo được ở §11.C: các phiên do
  `daily_levels_from_m1` sinh ra đều start 22:00; khối TPO ví dụ chạy 06-29 22:00 → 06-30 20:30 UTC).
  Khung "phiên chết" đang dùng là **UTC [02, 08)** (`DeadUseUtc=true`) — giữ nguyên.
- Nhắc lại lỗi cũ để không tái phạm: `imp_reversal_sweep.py` từng ghi *"'Time left' == giờ VN"* — **SAI**
  ([WYCKOFF_V6_PLAN §6](WYCKOFF_V6_PLAN.md)).

### 1.3 Mã kịch bản & tên module (⚠ chống trùng tên)
- `KB1` = phá&hồi · `KB2` = chạm&phản ứng · `KB3` = biên↔biên trong range.
  Khớp với chuỗi `scen` đã có trong [entry_dxfeed.py](research/entry_dxfeed.py) (`'1 pha&hoi len'`,
  `'2 cham&dao xuong'`).
- ⚠ **`research/kb3_climax_break.py` (2026-07-27) dùng chữ "KB3" với nghĩa KHÁC** — climax phá cụm. File đó
  **không liên quan** tới KB3 của spec này. **Bắt buộc:** mọi module mới đặt trong **`research/wyckoff/v7/`**
  với tên **không chứa `kb3`**:

| Module mới | Vai trò |
|---|---|
| `research/wyckoff/v7/range_struct.py` | Range theo cấu trúc (state machine) — dùng chung KB1+KB3 |
| `research/wyckoff/v7/bias_tpo.py` | Bias phiên từ TPO/VA/IB (§2) |
| `research/wyckoff/v7/force.py` | Tầng đo lực (§3), 1 hàm/1 feature, không side effect |
| `research/wyckoff/v7/s1_breakret.py` | KB1 (gọi lại `cbr_v6` để giữ parity) |
| `research/wyckoff/v7/s2_zonereact.py` | KB2 (gọi lại `imp_reversal_sweep.detect`) |
| `research/wyckoff/v7/s3_edge2edge.py` | KB3 (mới hoàn toàn) |
| `research/wyckoff/v7/router.py` | Định tuyến 3 nhánh + quy tắc 1 vị thế (§6.7) |
| `research/wyckoff/v7/probe_*.py` | Probe (đã có 2 file, xem §11) |

### 1.4 Nến-đóng-only (áp cho TỪNG feature, không phải khẩu hiệu)

| Nơi dùng | Quy tắc cụ thể |
|---|---|
| Mọi quyết định tại nến `i` | Chỉ đọc `B[0..i]`. `cbr_v6.run` đã đúng; `WyckoffRunner.Scan()` bỏ nến cuối (`i < B.Count-1`) → giữ. |
| Range state machine | Biên/đếm chạm cập nhật **sau khi** nến `i` đóng; nến xác nhận range là `i`, KB3 chỉ được arm từ `i+1`. |
| `vratio` | `vma` = SMA20 volume **có gồm nến hiện tại** (đúng như `load_m1` và label input C# "gồm nến này") — không phải look-ahead, nhưng **tự pha loãng**: một nến climax làm chính mẫu số của nó tăng. Giữ nguyên để parity, ghi nhận ở §9. |
| `liqratio` | TB volume **cuộn 1000 nến TRƯỚC**, không gồm nến hiện tại (`cbr_v6.prepare`). Đây là bản đã sửa look-ahead — **đừng quay về `avg_vma` toàn chuỗi**. |
| Bias TPO | Chỉ dùng **phiên đã đóng**. Xem cảnh báo look-ahead nghiêm trọng ở §2.2. |
| Swing/fractal | Fractal cần `k` nến SAU → **trễ xác nhận k nến**; range state machine ở §2.4/§6.3 **không dùng fractal** chính vì lý do này. |
| Delta/CVD (fp-m1) | Delta của nến `i` chỉ dùng ở nến `i` trở đi; CVD **tự cộng dồn**, không tin cột `Cumulative delta` của vendor (không biết mốc reset — [DATA_CAPABILITY §5 #13](research/DATA_CAPABILITY.md)). |
| Per-level | Chỉ `lvls` của nến đã đóng; và **không được làm gate** (§8). |

---

## §2. Tầng BIAS phiên (dùng chung 3 kịch bản)

### 2.1 Vì sao cần
Luật **R5** (nguyên văn): *"**mỗi phiên sẽ có một bias** … xem bên nào đang kiểm soát thì theo bên đó …
**bias tang thì chỉ canh mua** … xong **vào low tìm entry**"*. v6 đang thay bias bằng **proxy** `close` vs
`close[-480]` với `TrendTolPts = 1.0` giá. Proxy này có một khuyết điểm đo được: **nó gần như không bao giờ
bằng 0** — tại các lần chạm biên range, `trend == 0` chỉ **2–4%** số ca (§11.D). Nghĩa là proxy hiện tại
**không phân biệt được "thị trường đang cân bằng"**, trong khi đó lại chính là điều kiện sống của KB3.

### 2.2 ⚠ Look-ahead nghiêm trọng của `TPO-chart-daily.csv` (đo được, đừng bỏ qua)
Đã kiểm (§11.E): **cả 22/22 khối TPO đều có `VAH/VAL/POC/IB High/IB Low` KHÔNG đổi** suốt mọi dòng 30 phút
trong phiên đó → đây là **giá trị CHỐT của phiên**, được dập lên **mọi** nến kể cả nến đầu phiên.
→ **Dùng các cột này ở bất kỳ nến nào trong chính phiên đó = look-ahead trắng trợn.**

Hệ quả bắt buộc:
- `TPO-chart-daily.csv` chỉ dùng được cho **phiên đã đóng** (D-1 trở về trước), và làm **đối chứng**, không
  làm nguồn chính: file chỉ có **22 phiên** (2026-06-25 → 07-25) → **21 cặp D-1→D**. Quá mỏng cho A/B 3 tháng.
- Cột `IB High/IB Low` của **phiên đang chạy** chỉ được dùng **sau khi cửa sổ IB đã đóng** (mặc định 60 phút
  kể từ 22:00 UTC → dùng được từ 23:00 UTC), và **phải tự tính lại từ M1**, không đọc cột (vì cột đã bị dập
  giá trị chốt từ nến đầu).

### 2.3 Nguồn chính = dựng từ M1 (nhân quả)
Dùng **`daily_levels_from_m1(B)`** đã có trong [entry_dxfeed.py:145](research/entry_dxfeed.py) — gom phiên
theo gap > 45 phút (khớp `DayGapMin = 45` của C#), trả `vah/val/poc/hi/lo` mỗi phiên.
Đo được (§11.C): **160 phiên / 9 tháng**, **61 phiên trong 5–7/2026 → 60 cặp D-1→D**.
(Ít hơn "75 ngày giao dịch" mà [DATA_CAPABILITY §2](research/DATA_CAPABILITY.md) ghi cho cùng cửa sổ, vì hàm
này bỏ phiên < 30 nến và gộp phiên khi gap ≤ 45'. **Nêu ra chứ không lấp**: nếu GĐ6 cần đúng 1 phiên/ngày thì
phải viết bộ gom phiên riêng, đừng lặng lẽ nhận 61 = 75.)

**Còn thiếu, phải viết mới** (khớp [DATA_CAPABILITY §7.e](research/DATA_CAPABILITY.md)):
`ib_from_m1(B, session_start, minutes=60) -> (ib_hi, ib_lo)` — max/min của các nến trong `[start, start+60')`,
**chỉ trả kết quả khi cửa sổ đã đóng**.

### 2.4 Thuật toán bias (đặc tả chính xác)

```python
# bias_tpo.py — tinh 1 LAN moi phien, KHOA lai (R5: "bias khong dao giua phien")
# INPUT: D = daily_levels_from_m1(B)  (phien da dong)
#        s  = chi so phien hien tai trong D  (>=2 de co D-1 va D-2)
# OUTPUT: dict(score=int[-3..3], bias=int[-1,0,1], conf=float, ready_at=datetime)

TOL = 0.5            # gia — dung sai so sanh POC (⟦DE XUAT — CAN KIEM⟧, sweep 0.2/0.5/1.0)
MIN_SCORE = 2        # |score| >= 2 moi coi la co bias (⟦DE XUAT⟧, sweep 1/2/3)

def session_bias(D, s, B, ib_minutes=60):
    d1, d2 = D[s-1], D[s-2]                      # CHI phien DA DONG
    open_px = first_bar_close_of(D[s])           # close nen dau tien cua phien s
    c1 = +1 if d1['poc'] > d2['poc'] + TOL else (-1 if d1['poc'] < d2['poc'] - TOL else 0)
    #    C1 = VALUE MIGRATION: POC phien truoc dich len/xuong so voi phien truoc nua
    c2 = +1 if open_px > d1['vah'] else (-1 if open_px < d1['val'] else 0)
    #    C2 = GIA MO vs VA(D-1): mo NGOAI vung gia tri = mat can bang theo huong do
    ibh, ibl = ib_from_m1(B, D[s]['start'], ib_minutes)     # None neu cua so IB chua dong
    c3 = 0 if ibh is None else (+1 if ibl > d1['poc'] else (-1 if ibh < d1['poc'] else 0))
    #    C3 = IB nam HAN tren/duoi POC(D-1)
    score = c1 + c2 + c3
    return dict(score=score,
                bias=(1 if score >= MIN_SCORE else (-1 if score <= -MIN_SCORE else 0)),
                conf=abs(score) / 3.0,
                ready_at=D[s]['start'] + timedelta(minutes=ib_minutes))
```

- **Trước khi IB đóng** (từ đầu phiên tới `ready_at`): dùng `score = c1 + c2` với `MIN_SCORE` giảm 1 → bias
  vẫn có nhưng `conf ≤ 2/3`. **Không** để nhánh nào chạy trong khoảng này với bias `conf < 2/3` nếu bias đang
  là gate bắt buộc ⟦CẦN QUYẾT Ở GĐ6⟧.
- **Khoá:** sau `ready_at`, bias **không được đổi** tới hết phiên (R5). Kể cả khi giá đi ngược.
- Cơ sở lý thuyết của C2/C3: [THEORY §2.3](../data-export/wyckoff/THEORY.md) — *"Giá sẽ dành rất ít thời gian
  ở khu vực có lợi cho một trong 2 bên, ngược lại giá sẽ dành khoảng thời gian lớn hơn cho một khu vực cân
  bằng"*. Mở ngoài VA D-1 = thị trường đang **không** ở vùng cân bằng cũ.
- ⚠ **Chưa đo:** tần suất `bias == 0` là bao nhiêu %. Đây là số quyết định KB3 có dùng được bias làm điều
  kiện "đang cân bằng" hay không. ⟦CẦN QUYẾT Ở GĐ6⟧ — **probe bắt buộc trước khi code KB3 gate**:
  in phân bố `score` trên 60 phiên của 5–7/2026 và trên 159 phiên của 9 tháng; nếu `bias == 0` < 15% số
  phiên thì bias TPO cũng vô dụng như proxy 480 cho mục đích "phát hiện cân bằng" → khi đó KB3 **không** dùng
  bias làm điều kiện cân bằng, mà dùng chính **trạng thái range HỢP LỆ** (§6.3) làm định nghĩa cân bằng.

### 2.5 Dùng bias ở đâu

| KB | Bias dùng làm gì |
|---|---|
| KB1 | **Thay** (hoặc **cộng thêm**) gate `TrendOk`. Chỉ nhận cú phá cùng phía bias. |
| KB2 | Chọn phía được fade: chỉ fade **ngược** đà ngắn hạn khi **thuận** bias phiên (mua nhịp giảm trong phiên bias tăng) — đúng ý R5 *"bias tang thì chỉ canh mua… vào low tìm entry"*. |
| KB3 | 2 cách, phải A/B: (a) bias **không** dùng, KB3 chỉ cần range HỢP LỆ; (b) bias quyết **thiên vị biên**: chỉ đánh biên **cùng** phía bias (bias +1 → chỉ mua biên dưới). Xem §6.6. |

### 2.6 Thí nghiệm A/B phân xử "thay thế hay cộng thêm"
Chạy trên **chính KB1** (nhánh duy nhất đã có baseline vững), 4 nhánh, cùng bộ tín hiệu thô, cùng cửa sổ
5–7/2026, dxFeed:

| Nhánh | `TrendFilter` (proxy 480) | Bias TPO | Kỳ vọng đọc kết quả |
|---|---|---|---|
| A0 | BẬT | TẮT | = baseline v6 (n=33, EV +1.424) — mốc so |
| A1 | TẮT | BẬT | Nếu EV ≥ A0 và n ≥ 25 → **thay thế** |
| A2 | BẬT | BẬT | Nếu EV > cả A0 và A1 nhưng n ≥ 25 → **cộng thêm** |
| A3 | TẮT | TẮT | Mốc dưới (v6 đo được: n=39, WR 43.6%, +46R — [WYCKOFF_V6_PLAN §4](WYCKOFF_V6_PLAN.md)) |

**Phân xử:** chọn nhánh có EV cao nhất **với n ≥ 25**; nếu A1 và A2 chênh EV < 0.15R thì chọn **A1** (ít tham
số hơn = ít overfit hơn). Bắt buộc kèm **partition test**: in nhóm bị bias loại; nhóm đó phải tệ hơn rõ
(§4.9), nếu không thì bias chỉ là nhiễu → **KILL bias**, giữ proxy 480.

---

## §3. Tầng ĐO LỰC (dùng chung)

Ký hiệu bộ dữ liệu: **dx** = dxFeed 9 tháng (OHLCV, KHÔNG delta) · **fp** = `fp-m1-6-month.csv` (6 tháng, CÓ
delta, nhãn UTC+7) · **pl** = `perlevel_m1_clean.pkl` (25 phiên rời rạc).

| Feature | Công thức chính xác (biến/cột, cửa sổ) | Ngưỡng đề xuất + khoảng sweep | Bộ dữ liệu | Dùng ở KB | Look-ahead? |
|---|---|---|---|---|---|
| `rng` | `hi − lo` (giá) | — (dùng làm mẫu số) | dx, fp | 1,2,3 | Không |
| `brat` (thân/range) | `abs(c−o)/rng` | KB1 phá ≥ **0.50**, tiếp diễn ≥ **0.35**; KB3 nến từ chối ≥ **0.25** (sweep 0.20–0.40) | dx, fp | 1,2,3 | Không |
| `cpos` | `(c−lo)/rng` | KB1 sạch ≥ **0.50**; KB2/KB3 SHORT ≤ **0.45**, LONG ≥ **0.55** (sweep 0.35–0.50) | dx, fp | 1,2,3 | Không |
| râu `uw`/`lw` | `hi−max(o,c)` / `min(o,c)−lo` | KB2 `WickFrac` = **0.50** (đang ship); KB3 ≥ **0.35** (sweep 0.25–0.50) | dx, fp | 2,3 | Không |
| `vratio` (VSA) | `v / SMA20(v)`, **gồm nến hiện tại** | KB1 phá ≥ **2.0**; climax **2.2**; KB2 `RevVsaConf` **1.8**; KB3 nến từ chối ≥ **1.2** (sweep 1.0–2.0) | dx, fp | 1,2,3 | Không (nhưng tự pha loãng — §1.4) |
| `liqratio` | `vma / mean(v, cuộn 1000 nến TRƯỚC)` | ≥ **0.75** (giữ) | dx, fp | 1,(2),3 | Không — bản đã sửa |
| `trend` (proxy) | `sign(c − c[i−480])` với tol **1.0** giá | dùng/không dùng theo §2.6 | dx, fp | 1,2,3 | Không |
| **WY04** `no_supply`/`no_demand` | `(c<o)` (no_supply) `& rng < rng[-1] & rng < rng[-2] & v < v[-1] & v < v[-2]` | nhị phân; biến thể: chỉ cần `v < min(v[-1],v[-2])` | dx, fp | 1 (nhịp hồi), 3 | Không |
| **WY06** SOT | ≥3 đỉnh (hoặc đáy) liên tiếp có `dist(swing_k, swing_{k-1})` giảm đơn điệu | cần ≥3 lần đẩy | dx, fp | 3 (nhận biết biên đang yếu) | **Có trễ** (cần swing xác nhận) → chỉ dùng swing đã đóng |
| **WY14** climax cạn kiệt | ≥3 nến cùng hướng có `rng` và `v` giảm đơn điệu, không mở rộng qua cực trị trước | ⟦ĐỀ XUẤT — CẦN KIỂM⟧ N=3 | dx, fp | 2,3 | Không |
| `delta` nến | cột `Delta` | `sign` phải cùng hướng lệnh | **fp only** | 1,2,3 (xác nhận) | Không |
| `Delta %` | cột `Delta, %` | \|Δ%\| ≥ **20%** (sweep 10/20/30) | **fp only** | 2,3 | Không |
| bid vs ask vol | `Buy (Ask) volume` vs `Sell (Bid) volume` | tỉ lệ ≥ **1.5×** phía thuận (sweep 1.2/1.5/2.0) | **fp only** | 2,3 | Không |
| CVD / phân kỳ | **tự cộng dồn** `CVD_t = CVD_{t-1} + Delta_t`, reset đầu phiên | phân kỳ = giá tạo cực trị mới nhưng CVD **không** | **fp only** | 2,3 | Không nếu tự cộng dồn. **KHÔNG** tin cột `Cumulative delta` |
| **ddom** (leg) | `Σdelta(leg) / Σvolume(leg)` | ⚠ **phải gate volume TRƯỚC** (47.9% nến có vol<10, trong đó 27.4% có \|ddom\|=1.0 chỉ vì 2–3 lot) | **fp only** | — | Không, nhưng **đã bị bác** cho KB1 (§7 H-đã-bác) |
| imbalance/stacked/absorption từng mức giá | `ask_vol[p]` vs `bid_vol[p−1tick]`; stacked = N mức liên tiếp | — | **pl only, 25 phiên rời rạc** | **KHÔNG làm gate** (§8) | Không, nhưng độ phủ 25/49 ngày → mọi thống kê dễ overfit |
| `max_one_trade` ("cá lớn") | — | — | **KHÔNG TỒN TẠI** (toàn 0 ở mọi file) | — | — |

**Hệ quả bắt buộc của cột "Bộ dữ liệu":** mọi feature **fp only** (delta, Δ%, bid/ask, CVD) **phải test trên
fp-m1** và **số KHÔNG so trực tiếp được với số dxFeed** — vì (a) fp-m1 chỉ 6 tháng và nhãn UTC+7, (b) đã
chứng minh chênh lệch WR 61% vs 42% giữa 2 nguồn **do zone-pool "lạnh"**, không do dữ liệu
([DATA_CAPABILITY §4](research/DATA_CAPABILITY.md)). Trước khi so, **phải làm ấm pool** bằng lịch sử dxFeed
trước điểm bắt đầu (hạ tầng còn thiếu — [DATA_CAPABILITY §7.a](research/DATA_CAPABILITY.md)). Nếu chưa có
hạ tầng đó thì chỉ được kết luận **trong nội bộ cùng một feed** (bật/tắt delta trên cùng fp-m1).

---

## §4. KB1 — PHÁ RANGE → HỒI → VÀO (setup CHÍNH)

### 4.1 Định nghĩa bằng cơ chế đấu giá (một câu)
Cú phá là **mất cân bằng**: bên chủ động ăn hết thanh khoản thụ động đang bảo vệ biên; nhịp hồi sau đó **giữ
được** biên vừa phá chứng minh **vai của biên đã đảo** (kháng cự cũ thành hỗ trợ) — tức thị trường đã **chấp
nhận** vùng giá mới — và đó là chỗ duy nhất trong toàn bộ chuyển động mà điểm vô hiệu (SL) nhỏ hơn nhiều so
với quãng đường còn lại.

### 4.2 Neo vào luật nào (trích nguyên văn)
- **W5** — *"**Đánh break thôi chú**"*; *"SL 5 giá ổn"*.
- **W1** — *"**Tìm biên m1 xong et m1 luôn cũng đc**"* → range dựng trên chính M1, không lên M5.
- **W2** — *"Biên của chú **to thế** =))"* (nói về TR 15 giá) → biên phải HẸP.
- **WY05** — *"SOS-bar: thân dài nến tăng mạnh xuất hiện = điểm vào mua; SOW-bar tương tự cho bán"*.
- **WY08** — *"Breakout không có volume tăng cao vẫn hợp lệ nếu nguồn cung nổi thấp"* → **không** loại cú phá
  chỉ vì volume thấp.
- **THEORY §6.5 (chìa khoá phá vỡ, đáng tin cậy nhất)** — *"breakout hiệu quả ra ngoài TR, **thất bại khi cố
  quay lại vùng cân bằng** → xác nhận phong trào được CO hậu thuẫn"* ← đây **chính xác** là điều kiện
  `held` (nhịp hồi không đóng lại trong range) mà v6 đang dùng. Lý thuyết và luật thực nghiệm **khớp nhau**
  ở điểm này.
- **BREAK SẠCH (luật thực nghiệm v6, thắng dữ liệu)**: bỏ cú phá nếu trong 20 nến trước có cú quét hụt cạnh
  **đối diện** rồi đóng lại. Phân hoạch: SẠCH n=29 WR 58.6% MDD 2R **vs** CÓ QUÉT NGƯỢC n=26 WR 34.6% MDD 11R.
- ⚠ **WY03 / THEORY §3.2** — *"Không phải cấu trúc nào cũng có Spring hoặc Shakeout"* → **cấm** biến
  Spring/UT thành gate bắt buộc. Đã bị bác bằng dữ liệu (§7).

### 4.3 Bối cảnh cần có — range (pseudocode chính xác)

**v7 đổi định nghĩa range** từ "box 8 nến trượt" sang **range theo cấu trúc**, dùng chung với KB3.
State machine **bar-by-bar** (không phải quét cửa sổ) để C# và Python port 1:1 được:

```python
# range_struct.py — trang thai: NONE | FORMING | VALID | BREAKING | DEAD
# THU TU CAC BUOC LA MOT PHAN CUA DAC TA. Doi thu tu = doi ket qua.
P = dict(FORM=30,        # so nen toi thieu de range co the HOP LE            (nen)
         TOUCH=2,        # so lan cham toi thieu MOI bien                     (lan)
         SEP=3,          # 2 lan cham phai cach nhau >= SEP nen               (nen)
         TOLF=0.15, TOLMIN=0.3,   # dung sai cham = max(TOLMIN, TOLF*width)   (gia)
         WMIN=2.0, WMAX=6.0,      # do rong hop le                            (gia)
         MAXBARS=120,    # tuoi toi da                                        (nen)
         BUF=0.2)        # close phai vuot bien + BUF moi tinh la pha         (gia)

def step(R, B, i, P):
    b = B[i]
    # (0) gap phien: range KHONG duoc vat qua gap
    if b['since_gap'] == 0: R = new_range(i, b); return R
    if R.state == 'NONE':   R = new_range(i, b); return R
    # (1) KIEM PHA truoc khi mo rong bien  <-- thu tu quan trong
    if b['c'] > R.rhi + P['BUF'] or b['c'] < R.rlo - P['BUF']:
        if R.state == 'VALID':
            R.state, R.brk_dir, R.brk_bar = 'BREAKING', (1 if b['c'] > R.rhi else -1), i
            return R
        R = new_range(i, b); return R          # range CHUA hop le thi cu vuot bien KHONG phai break
    if R.state == 'BREAKING':
        # dong lai TRONG bien trong <=2 nen  => pha THAT BAI (day chinh la quet hut / spring)
        R.state = 'VALID' if (i - R.brk_bar) <= 2 else 'DEAD'
        if R.state == 'DEAD': return R
    # (2) mo rong bien bang WICK (khong bang close)
    nhi, nlo = max(R.rhi, b['hi']), min(R.rlo, b['lo'])
    if nhi - nlo > P['WMAX']: R = new_range(i, b); return R   # loang ra => khong con la vung nen
    R.rhi, R.rlo = nhi, nlo
    if i - R.i0 + 1 > P['MAXBARS']: R.state = 'DEAD'; return R
    # (3) DEM CHAM (theo bien HIEN TAI, khong tinh lai qua khu)
    tol = max(P['TOLMIN'], P['TOLF'] * (R.rhi - R.rlo))
    if b['hi'] >= R.rhi - tol and (not R.tu or i - R.tu[-1] >= P['SEP']): R.tu.append(i)
    if b['lo'] <= R.rlo + tol and (not R.td or i - R.td[-1] >= P['SEP']): R.td.append(i)
    # (4) XAC NHAN
    if (R.state == 'FORMING' and i - R.i0 + 1 >= P['FORM']
            and len(R.tu) >= P['TOUCH'] and len(R.td) >= P['TOUCH']
            and P['WMIN'] <= R.rhi - R.rlo <= P['WMAX']):
        R.state, R.valid_bar = 'VALID', i
    return R
```

⚠ **Chênh lệch đã biết giữa state machine này và probe §11.B:** probe đếm số lần chạm theo **biên cuối cùng**
của range (quét cửa sổ, không phải bar-by-bar), state machine đếm theo **biên tại thời điểm đó**. Hai cách cho
số khác nhau. **Bắt buộc bước kiểm ở GĐ6:** chạy state machine trên cùng cửa sổ và so `n_range` với
322 (§11.B, `FORM=30/TOUCH=2/WMAX=6.0`); nếu lệch > 25% thì **soi lại**, đừng đi tiếp.

**Neo biên vào cực trị hay close?** [CHART_CASES](../data-export/wyckoff/CHART_CASES.md) mục "Cách xác định
biên range": biên **range tổng thể** neo **cực trị nến**, còn ranh giới **phase bên trong** neo **giá đóng
cửa** (Ca #5 của `4.pdf`, giảng viên chủ động sửa). Đặc tả trên **khớp**: biên mở rộng bằng **wick**, còn
phá/vỡ xét bằng **close** — hai chuẩn khác nhau, có chủ đích, đúng tài liệu.

### 4.4 Arm và Entry (tách rời, nến-đóng-only)

**ARM (nến `i`):**
```
range.state == 'BREAKING' và range.brk_bar == i          # cú phá của một range ĐÃ HỢP LỆ
và vratio[i] >= 2.0  và  brat[i] >= 0.50
và (up ? c>o : c<o)
và NoCounterSweep(B, i, up, look=20, win=5, closepos=0.50) == True     # BREAK SẠCH
```
**ENTRY (nến `j`, `i+2 ≤ j ≤ i+WAIT`, `WAIT=12`):**
```
mọi nến từ i+1..j không đóng lại trong range (c > edge − 2tick nếu up)
retr = depth/leg  ∈ [0.60, 1.00]
held  = pullExt >= edge − 2tick        (up)
resume = c[j] > hi[j−1] và c[j]>o[j] và brat[j] >= 0.35
GATE tại NẾN VÀO j (không phải nến phá): trend/bias, VWAP-side, liqratio >= 0.75
```
(Đây là logic v6 nguyên bản — [cbr_v6.run](research/wyckoff/cbr_v6.py) và
[WyckoffRunner.Scan()](WyckoffRunner.cs). **Giữ nguyên**; v7 chỉ đổi *nguồn của `edge`* và *nguồn của bias*.)

### 4.5 SL / TP / R
- `SL = pullExt ∓ 2 tick`; sàn **3.0 giá**, trần **7.0 giá** (quá trần → **bỏ lệnh**).
- `R = |entry − SL|`; `TP = entry ± RR·R`, **RR = 4.0** (mặc định đang ship; RR 3.0 cho WR cao hơn 57.6% —
  bảng sweep ở [WYCKOFF_V6_PLAN §3](WYCKOFF_V6_PLAN.md)).
- ⚠ **Không** bóp SL về 2–4 giá: đã test, **âm** (n=52, WR 38.5%, EV 0.538 vs 0.891) — §7.

### 4.6 Gate ÁP / MIỄN

| Gate | KB1 | Ghi chú |
|---|---|---|
| Phiên chết UTC [02,08) | **ÁP** | Đóng góp thật (tắt: WR 37.2%) |
| Thuận xu hướng / bias | **ÁP** | Nguồn (proxy 480 vs bias TPO) quyết bằng §2.6 |
| VWAP-side | **ÁP nhưng đã biết NO-OP** trên cửa sổ này (0 lệnh khác biệt) | Giữ, **không** tính là một lớp lọc đã chứng minh |
| Thanh khoản `liqratio ≥ 0.75` | **ÁP** | Tắt: +13R nhưng MDD 4R thay 3R |
| BREAK SẠCH | **ÁP** | Đòn bẩy mạnh nhất tìm được |
| Spring/UT bắt buộc trước break | **MIỄN — CẤM BẬT** | Đã bị bác (§7) |

### 4.7 Định tuyến & loại trừ
KB1 chỉ arm khi range ở `BREAKING` (nến phá) của một range **đã** `VALID`. Đây là **thay đổi so với v6**
(v6 nhận cú phá của box 8 nến bất kỳ, không đòi range phải hợp lệ theo cấu trúc) → chính là **giả thuyết H1**
(§7). Khi KB1 đã arm, KB3 trên range đó **dừng arm ngay** (§6.7).

### 4.8 Tham số

| Tên | Mặc định | Sweep | Lý do chọn |
|---|---:|---|---|
| `RangeMode` | **0** (box v6) → đổi sang 1 nếu H1 PASS | {0,1} | Không đổi mặc định trước khi có số |
| `RangeFormBars` | 30 | {30,45} | Probe §11.F: form 30 → 322 range/461 arm; 45 → 118/182; 60 → 48/70 và tháng 5 chỉ 6 range → quá mỏng |
| `RangeTouchMin` | 2 | {2,3} | [CHART_CASES](../data-export/wyckoff/CHART_CASES.md): biên dưới thường test **2–3 lần** trước khi giảng viên chấp nhận; probe: 2→322 range, 3→206 |
| `RangeStructMaxPts` | 6.0 giá | {4,6,8} | Probe §11.A: cửa sổ 30 nến trong 5–7/26 có **p10 = 6.3 giá** → hẹp hơn 6.3 là thuộc decile thấp nhất = nén thật; khớp W2 ("15 giá là to") |
| `RangeStructMinPts` | 2.0 giá | {1.5,2.0,3.0} | Dưới 1.5 giá thì R không đủ chỗ đặt SL (§6.5) |
| `PullMin`/`PullMax` | 0.60 / 1.00 | đã sweep ở v6 | +B3: n 29→33, tổng R +4 |
| `RR` | 4.0 | {3,4,5} | Đơn điệu tăng theo RR nhưng MDD cũng tăng; 4.0 = EV cao nhất với MDD 3R |
| `CleanLook/CleanWin` | 20 / 5 | look {15..25}, win {4..6} | Cao nguyên đã xác nhận ở v6 |

### 4.9 PASS / KILL bằng số

**Mốc so (incumbent, phải đánh bại):** n=33, WR 48.5%, EV **+1.424**, MDD 3.0R, cả 3 tháng dương,
nửa1 +14R (n16) / nửa2 +33R (n17).

| Tiêu chí | PASS | KILL |
|---|---|---|
| n (lệnh đã đóng, sau dedup+cooldown+1-vị-thế) | **≥ 25** | < 25 → ghi **"không kết luận"**, KHÔNG ship |
| EV/lệnh | **≥ +1.42R** (không được thấp hơn incumbent) | < +1.00R |
| WR | ≥ 45% ở RR4 (hoặc ≥ 55% ở RR3) | < 40% |
| MDD | **≤ 4.0R** | > 6.0R |
| 3 tháng | **cả 3 phải dương** (không nhượng bộ — incumbent đã đạt) | bất kỳ tháng ≤ −3R |
| OOS thô | chia đôi cửa sổ theo thời gian → **cả 2 nửa > 0** | một nửa ≤ 0 |
| **Partition test** (bắt buộc mọi bộ lọc mới) | in cả nhóm **bị loại**; cần `EV_giữ − EV_loại ≥ 0.30R` **và** `n_loại ≥ 10` | `n_loại < 10` → "không kết luận"; chênh EV < 0.30R → **bộ lọc là nhiễu, KILL** |
| Hạn mức cấu hình | **≤ 12 cấu hình mới** cho toàn KB1 ở GĐ6 | vượt → mọi kết quả sau đó coi là khám phá, phải test lại trên cửa sổ khác |

**KILL dứt điểm cho một ý tưởng KB1** (bỏ hẳn, không tinh chỉnh thêm): sau khi thử **≤ 3 biến thể tham số**
mà vẫn không đạt PASS ở bất kỳ biến thể nào **và** partition không tách được → ghi vào §7 dưới nhãn "đã bác",
không quay lại.

### 4.10 Thứ tự implement + điểm dừng
1. Viết `range_struct.py` + kiểm đối chiếu với probe (§4.3) → **in bảng**: `n_range`, phân bố width/tuổi,
   phân bố `brk_dir`, số range theo tháng. **Dừng** nếu lệch > 25% so với 322.
2. Nối `RangeMode=1` vào `cbr_v6.run` (giữ `RangeMode=0` là mặc định) → **in bảng** so A0/A1 dạng
   `line()` của `cbr_v6` (n/WR/tổng R/EV/MDD/3 tháng/nửa1-nửa2). **Dừng**, đọc trước khi làm tiếp.
3. A/B bias §2.6 (4 nhánh) → **in bảng 4 dòng + 2 dòng partition**. **Dừng**.
4. WY04 (No Supply ở nhịp hồi) → **in partition**. **Dừng**.
5. Chốt cấu hình KB1, cập nhật `BASELINE.md`, rồi mới sang KB3.

---

## §5. KB2 — CHẠM VÙNG → PHẢN ỨNG (fade)

### 5.1 Định nghĩa bằng cơ chế đấu giá (một câu)
Tại một mức tham chiếu (VWAP phiên, VAH/VAL/POC D-1, POC/đỉnh/đáy phiên) có **thanh khoản thụ động dồn cục**;
khi lệnh chủ động đập vào đó mà **không đẩy được giá qua** (hấp thụ), bên chủ động vừa vào bị mắc kẹt và buộc
phải thoát → giá quay ngược, và điểm vô hiệu chỉ nằm vài tick ngoài cực trị của cú thử đó.

### 5.2 Neo vào luật nào (trích nguyên văn)
- **R2** — *"buy limit ở **chân** con song tang (sau một nhịp giảm) thì **ngon**; ở **đỉnh** là **lỏ**"* →
  chỉ fade **tại cực trị**, không fade giữa xu hướng. Code: `absorb_at_extreme` (25% dưới/trên của range gần).
- **R10** — *"Đi lên **k có ai bán** thì nó vẫn lên mà chú"* → **cấm** dùng "volume thấp" làm tín hiệu fade;
  phải có **nến từ chối CÓ volume**.
- **R8** — *"**t check data xác nhận t mới vào**"; "mọi thứ đề chuẩn chỉ rồi, **thiếu mỗi xác nhận trong m5,
  m1**"*.
- **WY01** (Spring) — *"giá dưới mức thấp nhất TR rồi đảo chiều đóng trong TR"*.
- **WY14** — *"xu hướng **không nhất thiết** kết thúc bằng volume lớn — có thể kết thúc khi mua/bán dần biến
  mất"* → phải bắt cả climax "lặng lẽ", không chỉ spike.
- **CHART_CASES lỗi #6** (lỗi phổ biến nhất của học viên, 4/22 ca) — *"Spring bắt buộc phải là điểm giá
  **THẤP NHẤT trong suốt Trading Range**"* → code hoá trực tiếp: cực trị của nến từ chối phải là cực trị của
  cả range/cửa sổ, không phải một đáy cục bộ bất kỳ.
- Bằng chứng riêng của người học: **4/4 setup thật do người học gửi đều neo VWAP** (ghi trong comment
  [WyckoffRunner.cs](WyckoffRunner.cs) khối `ScanReversal`).

### 5.3 Bối cảnh cần có
Giữ nguyên nhánh QUAY_DAU v2 (đã đo, n=27): neo **VWAP phiên**, `touch = hi ≥ vwap − 12tick` (SHORT) /
`lo ≤ vwap + 12tick` (LONG). **Mở rộng đề xuất (v7, phải A/B riêng):** thêm zone pool đã có
(`build_zones` → D-1 VAH/VAL/POC/Đỉnh/Đáy + POC/VAH/VAL phiên) làm mức neo thứ hai, với dung sai
`ConfluenceTol = 7 tick`.
⚠ `RevApproachBars` ("đến từ đúng phía") **đã tự kiểm là tautology**: sweep 1→999 ra **đúng 27 lệnh**
([WYCKOFF_V6_PLAN §6](WYCKOFF_V6_PLAN.md)) — **không** dùng nó như bằng chứng "đã có bối cảnh"; nếu muốn bối
cảnh thật thì phải thiết kế lại điều kiện (ví dụ: R2 — mức bị chạm phải nằm ở 25% biên của range gần đó).

### 5.4 Arm / Entry
- **ARM (nến `i`)**: `touchUp` (hoặc `touchDn`) tại mức neo; và mức neo đó thoả **R2** (nằm ở 25% trên/dưới
  của range 60 nến gần nhất) ⟦ĐỀ XUẤT — CẦN KIỂM⟧.
- **ENTRY (cùng nến `i`, đã đóng)**: `rejShort = uw ≥ 0.50·rng và cpos ≤ 0.45 và c < vwap và brat ≥ 0.30 và
  vratio ≥ 1.8` (gương lại cho LONG). Thêm ⟦ĐỀ XUẤT⟧: cực trị nến phải là cực trị của 20 nến gần nhất
  (CHART_CASES lỗi #6).
- Xác nhận delta (fp only, **không** làm mặc định): `Delta` cùng dấu hướng lệnh và `|Δ%| ≥ 20%`.

### 5.5 SL / TP / R
`SL = max(hi, vwap) + 2 tick` (SHORT) / `min(lo, vwap) − 2 tick` (LONG); **không có sàn 3 giá** (khác KB1 —
người học: "SL đặt ở VWAP thì đẹp"); bỏ lệnh nếu `R ≤ 0.5 giá` hoặc `R > 7.0 giá`.
`TP = entry ∓ 1.5·R` — **RevRR = 1.5** vì MFE trần của đảo chiều đo được ~1.3R; **đừng** đặt RR 3 cho nhánh này.

### 5.6 Gate ÁP / MIỄN

| Gate | KB2 | Ghi chú |
|---|---|---|
| Phiên chết | **MIỄN** | Trong khung UTC 02–08 reversal 4W/0L +6R — miễn trừ có cơ sở (đã sửa lại luận cứ ở v6) |
| Thuận xu hướng | **ÁP** (đang ship) | Fade nhịp ngược trong xu hướng, không fade cả xu hướng |
| VWAP-side | **có sẵn trong định nghĩa** | Không phải gate riêng |
| Thanh khoản | Chưa ràng buộc cho nhánh này | Sweep `Cooldown`/`SlCap` cho reversal ra **kết quả y hệt** → đừng nhận vơ là "đã lọc" |
| **BREAK SẠCH** | **KHÔNG BẬT** | [BASELINE §4](research/wyckoff/BASELINE.md): sạch cho WR 75% nhưng **n=12 < 25** → *chạm quy tắc dừng, CHƯA CHỐT*. Spec này **tôn trọng** kết luận đó: không bật, không dùng số đó làm căn cứ |

### 5.7 Định tuyến
KB2 độc lập với range, nhưng chịu **quy tắc 1 vị thế** (§6.7). Khi cùng nến có cả KB1 và KB2 → **ưu tiên KB1**
(EV cao hơn 3.7×). Khi KB2 và KB3 cùng nến và cùng mức giá (biên range trùng vùng) → **ưu tiên KB2** (đã có
baseline), và ghi log là ca trùng để đếm.

### 5.8 Tham số

| Tên | Mặc định | Sweep | Lý do |
|---|---:|---|---|
| `RevRR` | 1.5 | {1.25, 1.5, 2.0} | MFE trần đo được ~1.3R |
| `RevVsaConf` | 1.8 | {1.5, 1.8, 2.2} | R10: cần từ chối **có** volume |
| `VwapTolTicks` | 12 | {8, 12, 20} | đang ship |
| `Kb2ZoneExtend` | **false** | {false, true} | Mở rộng sang zone pool = giả thuyết mới, phải A/B |
| `Kb2ExtremeWin` | 20 nến | {10, 20, 60} | CHART_CASES lỗi #6 |

### 5.9 PASS / KILL bằng số
**Mốc so:** n=27, WR 55.6%, EV **+0.389**, MDD 5.0R, 3 tháng dương, nửa1 +4.5R(n13)/nửa2 +6.0R(n14).

| Tiêu chí | PASS | KILL |
|---|---|---|
| n | **≥ 25** | < 15 → **KILL biến thể**; 15 ≤ n < 25 → "không kết luận", không ship |
| EV/lệnh | **≥ +0.55R** (≈ +40% so incumbent — đủ lớn để không phải nhiễu) | < +0.30R |
| WR | ≥ 52% ở RR1.5 | < 45% |
| MDD | ≤ 5.0R | > 8.0R |
| 3 tháng | cho phép **đúng 1** tháng âm với \|R\| ≤ **2.0R** **và** ≤ 10% tổng R dương; **nhưng nếu tháng âm là tháng 7 → KILL** (tháng 7 là nửa OOS gần nhất, và là tháng nhiều lệnh nhất) | ≥ 2 tháng âm |
| OOS thô | cả 2 nửa > 0 | một nửa ≤ 0 |
| Partition | như §4.9 | như §4.9 |
| Hạn mức cấu hình | ≤ 12 | — |

**KILL dứt điểm KB2-mở-rộng-zone:** nếu `Kb2ZoneExtend=true` không đưa n lên ≥ 40 **hoặc** làm EV tụt dưới
+0.30R → bỏ hẳn ý tưởng mở rộng, giữ nhánh VWAP-only.

### 5.10 Thứ tự implement + điểm dừng
1. Chỉ thêm `Kb2ExtremeWin` (R2 + CHART_CASES #6) → **in partition** (nhóm bị loại). **Dừng**.
2. `Kb2ZoneExtend` → **in bảng** n/WR/EV/MDD + partition theo loại vùng (VWAP vs D-1 vs phiên). **Dừng**.
3. Delta confirm trên **fp-m1** (báo riêng, không trộn số dxFeed). **Dừng**.
4. **Không** làm gì với BREAK SẠCH cho KB2 tới khi có kết luận cơ chế cho [BASELINE §4](research/wyckoff/BASELINE.md).

---

## §6. KB3 — SCALP BIÊN ↔ BIÊN TRONG RANGE (mới)

### 6.1 Định nghĩa bằng cơ chế đấu giá (một câu)
Trong một vùng **đã được chấp nhận** (balance), hai biên đang được bên **thụ động** bảo vệ và cuộc đấu giá
**luân chuyển** giữa chúng; fade một biên là bán/mua ở **cực trị của phân bố giá trị hiện tại**, nơi điểm vô
hiệu chỉ nằm ngay ngoài biên (R nhỏ) trong khi mục tiêu là biên đối diện — một cái mốc mà chính cuộc đấu giá
vừa chứng minh là **hút giá** (đã chạm ≥2 lần).

**Số đo hậu thuẫn cơ chế này (probe §11.D, `WMAX=6.0`):** R thô trung vị **1.0 giá**, khoảng chạy tới biên
đối diện trung vị **4.4 giá** → **RR khả dụng trung vị 4.13**; 92% lần chạm có RR ≥ 1.5. Đây là **hình học**,
**không phải** kết quả backtest — nó nói "chỗ này có sẵn tỉ lệ", không nói "vào là thắng".

### 6.2 Neo vào luật nào (trích nguyên văn)
- **THEORY §2.3** — *"Giá sẽ dành rất ít thời gian ở khu vực có lợi cho một trong 2 bên, ngược lại giá sẽ
  dành khoảng thời gian lớn hơn cho một khu vực cân bằng."* ← nền tảng của KB3.
- **WY10 / THEORY §5** — *"Cú sốc là một cuộc tìm kiếm thanh khoản nhưng sau đó cũng phải có khả năng tạo ra
  một chuyển động với động lượng nhất định mà **ít nhất đạt đến phía đối diện của cấu trúc**."* ← đây chính là
  **TP của KB3**: biên đối diện là mục tiêu **tối thiểu** mà lý thuyết đặt ra cho một cú thử biên.
- **WY17 / THEORY §9** — *"cấu trúc hợp lệ được xác nhận bởi **lần chạm** ở 2 khu vực cung/cầu đối lập — càng
  nhiều lần chạm, càng tự tin."*
- **CHART_CASES** — *"biên dưới thường được chạm/test **2–3 lần** (SC → ST[A] → ST[B]/Spring) trước khi giảng
  viên chấp nhận là biên hợp lệ"* → cơ sở cho `RangeTouchMin ∈ {2,3}`.
- Nguyên văn của **người học** (yêu cầu gốc): *"nếu nó va chạm ở 2 cạnh đồng thời xác nhận bằng các delta
  footprint thì ta có thể scalp ngắn từ biên này sang biên còn lại"* + *"giá cũng sẽ chạy lên xuống trong range
  đó 1 thời gian nhất định rồi sẽ phá mạnh ra… tại đây thì lại dùng kịch bản 1"*.

**⚠ XUNG ĐỘT phải nói rõ:** luật pro trader **W5** nói thẳng *"**Đánh break thôi chú**"* — tức **không**
mean-revert trong range. KB3 **đi ngược W5**.
**Phân xử bằng cơ chế + dữ liệu, không bằng cảm tính:**
(a) Về cơ chế, W5 là một **lựa chọn phong cách** (CORVEN chơi momentum với RR 5–6), không phải một phát biểu
về việc rotation trong balance có tồn tại hay không — mà THEORY §2.3/§5 nói nó tồn tại;
(b) Về dữ liệu, hệ này **đã có** một nhánh vi phạm W5 là QUAY_DAU (fade tại VWAP) và nó **dương**: n=27,
WR 55.6%, +10.5R. Nên W5 **không** đủ để giết KB3 trước khi đo;
(c) **Thí nghiệm phân xử:** KB3 phải tự đứng bằng PASS/KILL §6.9 **và** phải kiểm thêm điều kiện W5-thân
thiện: nếu KB3 chỉ dương ở nhóm "range sau đó vỡ theo hướng thuận lệnh scalp" thì thực chất nó **không** phải
rotation mà là bắt đúng đầu cú phá → khi đó **hợp nhất vào KB1**, không giữ thành kịch bản riêng.

### 6.3 Bối cảnh cần có
Dùng **đúng** `range_struct.py` ở §4.3, đúng cùng tham số. KB3 chỉ tồn tại khi `range.state == 'VALID'`.
Định nghĩa "đang cân bằng" của KB3 = **chính trạng thái VALID này**, KHÔNG phải `trend == 0`
(probe §11.D bác cách đó: `trend == 0` chỉ 2–4% → n = 11 (WMAX 6.0) / 36 (WMAX 8.0), dưới ngưỡng kết luận).

### 6.4 Arm / Entry (tách rời, nến-đóng-only)

**ARM (nến `i`):**
```
range.state == 'VALID' và i > range.valid_bar          # chỉ sau nến xác nhận
và (hi[i] >= rhi − tol)  → arm SHORT tại biên trên
   hoặc (lo[i] <= rlo + tol) → arm LONG tại biên dưới
và không đang có vị thế (§6.7)
```
**ENTRY (cùng nến `i`, sau khi nến đã đóng) — nến TỪ CHỐI phải có chất lượng:**
```
SHORT:  c[i] <  rhi            (đóng lại TRONG range, không đóng ngoài biên)
        cpos[i] <= 0.45
        uw[i] >= 0.35 * rng[i]
        brat[i] >= 0.25
        vratio[i] >= 1.2                  # R10: fade phải có volume, không fade vì "vắng người"
        hi[i] == max(hi[i−19..i])          # CHART_CASES #6: cực trị phải là cực trị cửa sổ, không phải đáy/đỉnh cục bộ
LONG:   gương lại
Xác nhận delta (fp only, MẶC ĐỊNH TẮT): sign(Delta[i]) đúng hướng lệnh và |Δ%| >= 20%
```

### 6.5 SL / TP / R — **R BIẾN THIÊN** (mục quan trọng nhất của KB3)

```
SHORT (fade biên trên):
    entry = c[i]
    sl_raw = max(hi[i], rhi) + 2 tick
    R      = max(sl_raw − entry, Kb3SlFloorPts)        # SÀN SL bắt buộc, xem lý do dưới
    sl     = entry + R
    tp     = rlo + Kb3TpBufTicks·tick                  # biên ĐỐI DIỆN trừ đệm
    room   = entry − tp
    BỎ LỆNH nếu  room / R < Kb3MinRr
LONG: gương lại
```

- **Vì sao phải có sàn SL:** R thô trung vị chỉ **1.0 giá**, p10 = **0.5 giá** (§11.D). SL 5 tick sẽ bị nhiễu
  quét sạch. Mặt khác v6 **đã có bằng chứng** bóp SL làm KB1 tệ đi (SL 2.4 giá: WR 38.5% vs 47.3%) — nhưng
  **không suy trực tiếp sang KB3** được, vì KB1 là momentum (vào sau khi giá đã chạy) còn KB3 là fade tại cực
  trị (SL nằm ngoài một cực trị vừa được bảo vệ). Vì thế: đặt sàn **1.5 giá** ⟦ĐỀ XUẤT — CẦN KIỂM⟧ và
  **sweep {1.0, 1.5, 2.0, 2.5}** — đây là tham số quan trọng nhất của KB3.
- ⚠ **Số RR ở §6.1 tính trên R THÔ (chưa áp sàn)**. Sau khi áp sàn 1.5 giá, RR trung vị ước ~2.9 (4.4/1.5)
  nhưng **tỷ lệ lệnh còn RR ≥ 1.5 sẽ giảm** — **CHƯA ĐO**. ⟦CẦN QUYẾT Ở GĐ6⟧: chạy lại `probe_kb3_geometry.py`
  với `Kb3SlFloorPts` áp vào rồi mới chốt `Kb3MinRr`.
- **Thoát khi range vỡ:** vì sàn SL có thể đẩy SL ra **ngoài** biên, giá có thể xác nhận vỡ range **trước khi**
  chạm SL. Khi `range.state → DEAD` theo hướng **ngược** lệnh → **thoát market ở close nến đó**,
  `r = (exit − entry)/R` (âm nhưng nhỏ hơn −1). Cờ `Kb3ExitOnBreak = true` (mặc định).
- **Timeout:** `Kb3MaxHoldBars = 60` nến → thoát market, `r = (exit − entry)/R`. Lý do: tuổi range trung vị
  **37 nến** (§11.B) — giữ quá 60 nến nghĩa là rotation đã không xảy ra.

#### 6.5.1 Phải sửa `evaluate()` của `cbr_v6.py` thế nào (đặc tả chính xác)
Engine hiện tại **hardcode RR cố định**:
```python
# cbr_v6.py — HIEN TAI
def evaluate(B, sig, C):
    for s in sig:
        r = s['risk_t'] * TICK
        tp = s['entry'] + C['RR'] * r if s['side'] == 'LONG' else s['entry'] - C['RR'] * r
        o = hit(B, s['i'], s['side'], s['sl'], tp)
        if o == 'open': continue
        s2 = dict(s); s2['r'] = C['RR'] if o == 'TP' else -1.0
```
**Bản sửa (bắt buộc là NO-OP cho KB1/KB2):**
```python
def evaluate(B, sig, C):
    out = []
    for s in sig:
        r = s['risk_t'] * TICK
        if s.get('tp') is not None:                    # KB3: TP tuyet doi (bien doi dien) => RR bien thien
            tp = s['tp']; rr = abs(tp - s['entry']) / r
        else:                                          # KB1/KB2: y NGUYEN duong cu
            rr = C['RR']
            tp = s['entry'] + rr * r if s['side'] == 'LONG' else s['entry'] - rr * r
        o = hit(B, s['i'], s['side'], s['sl'], tp,
                maxbars=s.get('maxbars'), dead_at=s.get('dead_at'))
        if o[0] == 'open': continue
        s2 = dict(s); s2['rr_real'] = rr
        s2['r'] = rr if o[0] == 'TP' else (-1.0 if o[0] == 'SL' else o[1])   # o[1] = R thuc khi TO/BREAK
        out.append(s2)
    return out
```
và `hit()` mở rộng (giữ nguyên hành vi cũ khi 2 tham số mới = None):
```python
def hit(B, i, side, sl, tp, maxbars=None, dead_at=None):
    for j in range(i + 1, len(B)):
        b = B[j]
        if (b['lo'] <= sl) if side == 'LONG' else (b['hi'] >= sl): return ('SL', -1.0)
        if (b['hi'] >= tp) if side == 'LONG' else (b['lo'] <= tp): return ('TP', None)
        if dead_at is not None and j >= dead_at:        # range vo nguoc huong -> thoat market
            r = (B[j]['c'] - B[i]['entry_px']) if side == 'LONG' else (B[i]['entry_px'] - B[j]['c'])
            return ('BREAK', r / (abs(B[i]['entry_px'] - sl)))
        if maxbars is not None and j - i >= maxbars:
            r = (B[j]['c'] - B[i]['entry_px']) if side == 'LONG' else (B[i]['entry_px'] - B[j]['c'])
            return ('TO', r / (abs(B[i]['entry_px'] - sl)))
    return ('open', 0.0)
```
(`entry_px` phải được truyền vào chứ không đọc từ `B` — chi tiết implement, nhưng **hợp đồng** là: `hit` trả
`(outcome, r_thuc)` và outcome mới `'TO'`/`'BREAK'` **chỉ** xuất hiện khi tham số mới khác None.)

**Kiểm hồi quy BẮT BUỘC ngay sau khi sửa** (nếu lệch → dừng, sửa lại):
`python3 research/wyckoff/final_table.py` phải vẫn in dòng B4 = **n=33, WR 48.5%, +47.0R, EV +1.424, MDD 3.0R**.

Cũng phải sửa `line()` để KB3 báo thêm: **trung vị `rr_real` của lệnh thắng**, số lệnh `TO`, số lệnh `BREAK`
— vì với R biến thiên, "tổng R" có thể bị 2–3 cú rotation dài kéo lên và điều đó phải nhìn thấy được.

### 6.6 Gate ÁP / MIỄN — **điểm dễ sai nhất của KB3**

| Gate | KB3 | Bằng chứng / lý do |
|---|---|---|
| **Thuận xu hướng (proxy 480)** | **MIỄN mặc định** | KB3 nghịch đà **theo bản chất**. Probe §11.D: gate v6 nguyên bản giữ lại 49% (n=224) — không "giết sạch" như lo, nhưng nó **thay đổi bản chất** setup (chỉ còn fade biên ngược đà). Phải A/B 3 chế độ: `Kb3TrendMode` 0=không lọc / 1=chỉ `trend==side` / 2=chỉ `trend==0` |
| ~~`trend == 0`~~ | **BÁC NGAY, không cần test** | Probe §11.D: n = **11** (WMAX 6.0) / **36** (WMAX 8.0) → dưới ngưỡng 25 ở cấu hình mặc định. Ghi vào §7 là "đã bác bằng probe" |
| **VWAP-side** | **MIỄN** | Probe: chỉ 41–46% lần chạm ở "đúng phía VWAP" theo hướng scalp → gate này cắt hơn nửa mẫu và **không có cơ chế** biện minh (KB3 fade biên range, không fade VWAP) |
| Thanh khoản `liqratio ≥ 0.75` | **ÁP** | Portable, không hardcode giờ; range trong phiên mỏng là range rác |
| Phiên chết UTC [02,08) | **ÁP** ⟦ĐỀ XUẤT — CẦN KIỂM⟧ | Chưa đo cho KB3. Nhưng KB1 mất 22 lệnh tệ ở đó; và range trong giờ chết dễ là drift, không phải balance. **Thí nghiệm:** partition trong/ngoài khung |
| BREAK SẠCH | **KHÔNG áp** | Vô nghĩa: KB3 không có "cú phá" để đánh giá |
| Bias TPO | **A/B** (§2.5) | Chỉ sau khi §2.4 probe xong tần suất `bias==0` |
| Hợp lưu biên với vùng D-1/phiên | **A/B, không mặc định** | Probe §11.D: chỉ **18%** biên nằm trong ±0.3 giá của một vùng, **35–38%** trong ±0.7 giá → **cả 2 nhóm đều đủ n** để partition (82 vs 379 / 176 vs 285). Đây là giả thuyết của chính người học ("swing low/high hợp lưu với vùng nào đó thì nó cũng mạnh") → **phải đo, đừng giả định** |

### 6.7 Định tuyến & loại trừ lẫn nhau (state machine + 1 vị thế)

```
range.state:  NONE → FORMING → VALID → BREAKING → (VALID | DEAD) → NONE
KB3 arm:      CHỈ khi VALID và i > valid_bar
KB1 arm:      CHỈ khi BREAKING và brk_bar == i, và range TRƯỚC đó đã VALID
KB2 arm:      độc lập range (neo VWAP/zone)

Chuyển trạng thái ↔ hành vi kịch bản:
  VALID → BREAKING   : KB3 NGỪNG arm ngay tại nến đó. Nếu đang có vị thế KB3 và hướng vỡ NGƯỢC
                       lệnh → chờ xác nhận (2 nến) rồi thoát market (Kb3ExitOnBreak).
  BREAKING → VALID   : (phá thất bại) KB1 đã arm ở nến brk_bar bị HUỶ nếu chưa vào lệnh;
                       KB3 được arm lại. Chính cú phá thất bại này là dữ liệu của counter_sweep/spring.
  BREAKING → DEAD    : range chết. KB1 tiếp tục vòng chờ-hồi của nó (WAIT=12 nến từ brk_bar).
                       KB3 không còn range → không arm.
```
**Quy tắc 1 vị thế tại một thời điểm (cho backtest portfolio):** gộp tín hiệu 3 nhánh, sort theo `dt`; nếu còn
một vị thế **chưa đóng** (chưa TP/SL/TO/BREAK) → **bỏ** mọi tín hiệu mới bất kể nhánh. Trùng cùng nến → ưu
tiên **KB1 > KB2 > KB3**. **Bắt buộc in ra** số tín hiệu bị bỏ vì quy tắc này, tách theo nhánh — nếu KB3 bị
KB1/KB2 "ăn" mất > 40% tín hiệu thì con số KB3 độc lập **không** phản ánh đóng góp thật của nó vào portfolio,
phải báo cả hai (KB3 độc lập và KB3 trong portfolio).
⚠ Nhắc nợ: `Dedup` của C# gộp chung CBR + reversal, `cbr_v6` **chưa** mô phỏng
([WYCKOFF_V6_PLAN §8](WYCKOFF_V6_PLAN.md)) → khi thêm nhánh thứ ba, sai lệch này **tăng lên**. Router v7 phải
mô phỏng dedup **trên danh sách gộp 3 nhánh** ngay từ đầu.

### 6.8 Tham số

| Tên | Mặc định | Sweep | Lý do chọn |
|---|---:|---|---|
| `Kb3SlFloorPts` | **1.5 giá** ⟦ĐỀ XUẤT⟧ | {1.0, 1.5, 2.0, 2.5} | R thô trung vị 1.0 / p10 0.5 giá (§11.D) → không có sàn thì SL = nhiễu; nhưng SL rộng thì mất lợi thế "R nhỏ" |
| `Kb3MinRr` | **1.5** ⟦ĐỀ XUẤT⟧ | {1.2, 1.5, 2.0, 2.5} | Probe (R thô): 92% lần chạm có RR ≥1.5, 85% ≥2.0 → 1.5 giữ gần hết mẫu. **Phải đo lại sau khi áp sàn SL** |
| `Kb3TpBufTicks` | 2 | {0, 2, 5} | Đối xứng với `SlBuf = 2` đang dùng |
| `Kb3MaxHoldBars` | 60 | {30, 60, 90} | Tuổi range trung vị 37 nến (§11.B) |
| `Kb3VsaMin` | 1.2 | {1.0, 1.2, 1.5} | R10 — fade phải có volume; 1.2 là `VSA_GATE` đã dùng ở EntrySignal |
| `Kb3WickFrac` | 0.35 | {0.25, 0.35, 0.50} | Thấp hơn `WickFrac=0.50` của KB2 vì nến từ chối ở biên range thường nhỏ hơn ở VWAP ⟦ĐỀ XUẤT — CẦN KIỂM⟧ |
| `Kb3TrendMode` | 0 (không lọc) | {0, 1} (2 đã bị bác) | §6.6 |
| `Kb3ExtremeWin` | 20 nến | {10, 20} | CHART_CASES lỗi #6 |
| `Kb3RequireConfluence` | false | {false, true} | Probe: 18%/38% → partition được |

### 6.9 PASS / KILL bằng số — **phần quan trọng nhất**

KB3 **không có incumbent** → phải vượt một mốc tuyệt đối, và vì nó cạnh tranh cùng một tài khoản với KB2
(EV +0.389R) thì nó phải **ít nhất ngang KB2**.

| Tiêu chí | PASS | KILL |
|---|---|---|
| **n** (lệnh đã đóng, sau mọi lọc + dedup + 1-vị-thế) | **≥ 40** | < 25 → **"không kết luận"**; nếu ở **mọi** cấu hình trong hạn mức đều < 25 → **KILL dứt điểm** |
| EV/lệnh | **≥ +0.40R** | < +0.15R → KILL dứt điểm |
| WR | ⟦không đặt ngưỡng cứng⟧ — RR biến thiên nên WR không so được. Thay bằng: **trung vị `rr_real` của lệnh thắng ≥ 1.8** | trung vị `rr_real` < 1.2 (nghĩa là đang ăn vụn mà chịu rủi ro đầy) |
| MDD | **≤ 6.0R** | > 10.0R |
| 3 tháng | cho phép **đúng 1** tháng âm, \|R\| ≤ 2.0R và ≤ 10% tổng R dương; **tháng 7 âm → KILL** | ≥ 2 tháng âm |
| OOS thô | chia đôi theo thời gian → **cả 2 nửa > 0** | một nửa ≤ 0 |
| `TO` + `BREAK` | tổng ≤ **35%** số lệnh | > 50% → rotation không xảy ra → cơ chế sai → KILL |
| **Partition bắt buộc** cho MỌI bộ lọc (`Kb3TrendMode`, hợp lưu, phiên chết, delta) | in cả nhóm bị loại; `EV_giữ − EV_loại ≥ 0.30R` và `n_loại ≥ 10` | chênh < 0.30R → bộ lọc là nhiễu → **bỏ bộ lọc** (không bỏ KB3) |
| **Hạn mức cấu hình** | **≤ 24 cấu hình** cho toàn KB3 ở GĐ6, khai báo TRƯỚC khi chạy | vượt hạn mức → kết quả chỉ được coi là *khám phá*, phải xác nhận lại trên cửa sổ 9 tháng dxFeed hoặc trên fp-m1 |
| **Cao nguyên (chống đỉnh nhọn)** | cấu hình thắng phải có **≥2 láng giềng** (±1 bước sweep của tham số chính) đạt EV ≥ **60%** EV của nó | thắng đơn độc, láng giềng âm → coi là **nhiễu**, KILL cấu hình đó |
| Kiểm "có thật là rotation?" (§6.2c) | Nếu bỏ hết các lệnh mà range sau đó vỡ **thuận** hướng scalp, phần còn lại vẫn EV ≥ +0.25R | nếu phần còn lại ≤ 0 → KB3 thực chất là KB1 sớm → **hợp nhất vào KB1**, xoá KB3 |

**KILL dứt điểm KB3** (bỏ hẳn kịch bản): thoả **bất kỳ** điều sau — (a) EV < +0.15R ở mọi cấu hình trong hạn
mức; (b) chỉ 1/3 tháng dương ở mọi cấu hình; (c) `TO+BREAK` > 50%; (d) sau khi lọc bỏ nhóm "vỡ thuận hướng",
phần còn lại ≤ 0.

### 6.10 Thứ tự implement + điểm dừng
1. `range_struct.py` xong và đã đối chiếu probe (§4.10 bước 1). **Không code KB3 trước bước này.**
2. Chạy lại `probe_kb3_geometry.py` **có áp `Kb3SlFloorPts`** → **in bảng** phân bố `rr_real` và % lệnh còn
   RR ≥ {1.2, 1.5, 2.0} → **chốt `Kb3MinRr` bằng số này**. **Dừng.**
3. `s3_edge2edge.py` phiên bản **trần** (không lọc gì ngoài chất lượng nến từ chối + `Kb3MinRr` + thanh khoản)
   → **in bảng** `n/WR/tổng R/EV/MDD/3 tháng/nửa1-nửa2/median rr_real/TO/BREAK`. **Dừng** — đây là điểm quyết
   định KB3 sống hay chết.
4. Nếu bước 3 cho EV ≥ +0.15R: thêm **từng** bộ lọc một, **mỗi cái một bảng partition**, theo thứ tự
   (rẻ→đắt): phiên chết → `Kb3TrendMode=1` → hợp lưu vùng → `RangeTouchMin=3` → bias TPO. **Dừng sau mỗi cái.**
5. Router + 1 vị thế + dedup gộp 3 nhánh → **in bảng portfolio** và số tín hiệu bị bỏ theo nhánh. **Dừng.**
6. Chỉ khi PASS: cập nhật `BASELINE.md`, rồi mới port C# (§10) với `EnableKb3 = false` mặc định.

---

## §7. Danh sách giả thuyết cần test, xếp hạng

Xếp theo **(giá trị kỳ vọng ÷ công sức)**. "Bác nó" = kết quả cụ thể khiến phải bỏ.

| # | Giả thuyết (có thể bác được) | Cách test | n dự kiến | Kết quả nào BÁC nó |
|---|---|---|---:|---|
| **H1** | **KB3 có edge:** fade biên trong range VALID cho EV > 0 sau khi áp sàn SL và `Kb3MinRr` | `s3_edge2edge.py` bản trần, cấu hình mặc định §6.8 | thô 461 lần chạm → sau lọc **⟦chưa biết⟧**, chỉ tiêu ≥40 | EV < +0.15R; hoặc n < 25 ở mọi cấu hình; hoặc `TO+BREAK` > 50% |
| **H2** | **Chỉ fade biên NGƯỢC đà** (`Kb3TrendMode=1`) tốt hơn không lọc | Partition trên chính bộ H1 (miễn phí, cùng lần chạy) | 224 / 237 (probe, trước lọc chất lượng) | `EV_giữ − EV_loại < 0.30R` → gate là nhiễu, bỏ |
| **H3** | **Hợp lưu biên range với vùng D-1/phiên làm KB3 mạnh hơn** (giả thuyết của chính người học) | Partition ±0.3 giá và ±0.7 giá (miễn phí) | 82 vs 379 · 176 vs 285 | chênh EV < 0.30R ở **cả hai** dung sai |
| **H4** | **Range ≥3 chạm mỗi biên** (WY17) mạnh hơn 2 chạm — dùng cho **cả** KB1 và KB3 | `RangeTouchMin` 2 vs 3, partition | KB3: 461 vs 267 lần chạm; KB1: ⟦chưa biết⟧ | chênh EV < 0.30R, hoặc nhóm 3-chạm có n < 25 |
| **H5** | **Range cấu trúc (≥30 nến, ≥2 chạm) tốt hơn box 8 nến** cho KB1 | `RangeMode` 0 vs 1 trên `cbr_v6` | 25–60 ⟦chưa biết⟧ | EV < +1.00R hoặc n < 25 hoặc MDD > 6R |
| **H6** | **Bias TPO (giá mở vs VA D-1 + value migration) tốt hơn proxy `close[-480]`** | A/B 4 nhánh §2.6 trên KB1 | 25–45 | EV(TPO) < EV(proxy) **và** partition không tách |
| **H7** | **WY04 No Supply/No Demand ở nhịp hồi** là bộ lọc thật cho KB1 | Partition trên 33 lệnh v6 | 33 → 2 nhóm nhỏ | `n_loại < 10` → "không kết luận" (rất có thể xảy ra); chênh EV < 0.30R |
| **H8** | **WY10/WY12 "cấu trúc thất bại"** (cú thử biên KHÔNG đến được biên đối diện trong N nến → tăng trọng số hướng ngược) đo được và có giá trị | Feature mới trong `force.py`, sweep X% ∈ {60,80,100}, N ∈ {tuổi range, 2× tuổi} | ⟦chưa biết⟧ | mọi (X,N) trong sweep đều không tách partition ≥ 0.30R |
| **H9** | **Delta/CVD xác nhận tại biên** (fp-m1) cải thiện KB2/KB3 | Chạy trên fp-m1, **báo riêng**, sau khi làm ấm zone pool | nhỏ hơn dx ~40% | không tách partition; hoặc chưa có hạ tầng warm-up → **không được kết luận** |

### 7.1 ĐÃ BỊ BÁC — ĐỪNG LÀM LẠI

| Ý tưởng | Kết quả | Nguồn |
|---|---|---|
| **Bắt buộc có Spring/Upthrust (Phase C) trước cú phá** (W3 hiểu theo nghĩa chữ) | n=26, WR 34.6%, EV 0.385, **tháng 6 ÂM**. Luật đúng là **ngược lại** (BREAK SẠCH) | [WYCKOFF_V6_PLAN §9](WYCKOFF_V6_PLAN.md) |
| **Bóp SL 2–4 giá cho KB1**, neo dưới cây M1 vào lệnh (R7) | n=52, WR 38.5%, EV 0.538 (vs 0.891) | idem |
| **Leg phải do lệnh chủ động đẩy** (`ddom` leg ≥ ngưỡng, R1) | n 34→17, +51R→+18R; nửa số leg có delta âm mà **nhóm đó lại tốt hơn** | idem + [DATA_CAPABILITY §5](research/DATA_CAPABILITY.md) |
| **Loại break "spike rồi tắt"** (R3) | 0 lệnh khác biệt — ngưỡng không bao giờ đồng thời xảy ra | idem |
| **Chỉ giao dịch phiên Á+Âu** (R6) | n=46, WR 41.3% — kém baseline; phiên Mỹ tốt nhưng n=9 | idem |
| **KB3 chỉ chạy khi `trend == 0`** | **Bác bằng probe (§11.D)**: n = 11 (WMAX 6.0) / 36 (WMAX 8.0) — dưới ngưỡng kết luận. Nguyên nhân cơ chế: tol 1.0 giá trên 480 nến gần như không bao giờ = 0 trên vàng | §11.D (lượt này) |
| **`RevApproachBars` là một điều kiện bối cảnh** | Tautology: sweep 1→999 ra đúng 27 lệnh | [WYCKOFF_V6_PLAN §6](WYCKOFF_V6_PLAN.md) |

---

## §8. KHÔNG kiểm được offline

**Quy tắc chung:** không đưa vào mặc định; chỉ để dạng **tham số tắt sẵn** + hiển thị. Nếu biến thành gate thì
replicator offline **mù ngay** và mọi số sau đó không so được.

| Feature | Vì sao | Xử lý trong v7 |
|---|---|---|
| Stacked imbalance / hấp thụ / iceberg **từng mức giá** liên tục | Chỉ có **25–46 phiên rời rạc** (`perlevel_m1_clean.pkl` 25/49 ngày = 51%) | `Kb3AbsorbBonus`, `AbsDom` → **chỉ hiển thị** "hấp thụ ✓", **không** nâng grade, **không** gate |
| DOM/Level 2, vị trí trong hàng đợi | Không tồn tại trong mọi export | Không thiết kế vào |
| **"Cá lớn"** (`max_one_trade`) | Toàn 0 ở **mọi** file, kể cả 761.199 dòng per-level | Không thiết kế vào |
| **Số lệnh** tách phía Buy/Sell | `Buy (Ask) trades`/`Sell (Bid) trades` toàn 0 ở mọi file | Không thiết kế vào |
| Spread / slippage / phí | Không có trong export nào | §9 — chỉ nêu ra khi trích số |
| **R8 "check data xác nhận"** của CORVEN (đọc DOM/footprint sống trước khi vào) | Bản chất là phán đoán người trên dữ liệu sống | Chỉ mô phỏng phần **đo được** (`m5_confirm`, nến xác nhận), nói rõ đây **không** phải R8 đầy đủ |
| Bias theo "vùng va chạm nhiều" tính bằng **volume từng mức** (HVN thật) | HVN thật chỉ có trên per-level 25–46 ngày | Dùng **proxy TPO-count** (`tpo_counts` trên M1, ~9 tháng) và **nói rõ là proxy**, không gọi là HVN |

---

## §9. Sổ rủi ro overfit

| # | Rủi ro | Mức độ | Cách giảm thiểu cụ thể |
|---|---|---|---|
| 1 | **Cửa sổ 5–7/2026 là vàng tạo đỉnh** → đây là **chế độ thị trường**, không phải cấu trúc bền. Phía SHORT được ưu ái | **Cao** | (a) Báo **tách LONG/SHORT** cho cả 3 KB, mỗi lần trích số; (b) mở cửa sổ dxFeed lên **9 tháng** (11/2025→7/2026) cho **mọi giả thuyết về CẤU TRÚC** (range, số lần chạm, hình học KB3) — probe §11.B cho thấy số range 9 tháng chỉ hơn 5–7/26 rất ít (326 vs 322 ở WMAX 6.0) ⟹ **thanh khoản trước tháng 5 quá mỏng, mở rộng ra rác** đúng như [BASELINE §6](research/wyckoff/BASELINE.md) đã cảnh báo → (c) **OOS thật phải là front-month/CCPA khác**, không phải quá khứ của GCQ26 |
| 2 | **dxFeed là proxy YẾU** cho feed live (WR 61% fp-m1 vs 42% dxFeed cùng kỳ) | **Cao** | Nguyên nhân đã xác định là **zone-pool lạnh**, không phải dữ liệu → xây hạ tầng warm-up ([DATA_CAPABILITY §7.a](research/DATA_CAPABILITY.md)) **trước** khi so 2 feed; trong lúc chưa có, chỉ kết luận **trong nội bộ cùng feed** |
| 3 | **KB3 có 461 lần chạm thô** → thừa bậc tự do | **Cao** | Hạn mức **24 cấu hình** khai báo trước; luật **cao nguyên** (≥2 láng giềng ≥60% EV); partition bắt buộc; và **khai báo trước** danh sách bộ lọc sẽ thử (§6.10 bước 4) |
| 4 | **Chưa mô hình spread/slippage/phí**; KB3 có R nhỏ nhất (sàn 1.5 giá = 15 tick) nên **bị ảnh hưởng nặng nhất** | **Cao cho KB3** | Báo thêm một cột **EV sau khi trừ 2 tick/lệnh** (ước lượng bi quan cho spread+slippage vàng M1) cho **mọi** bảng KB3. Nếu EV_sau_phí < +0.15R → KB3 không đáng ship dù PASS thô |
| 5 | Giả định **SL trước TP trong cùng nến** (bi quan) | Trung bình | Giữ (bi quan là an toàn), nhưng với KB3 phải **đếm** số lệnh mà cả SL và TP nằm trong cùng nến và báo riêng — nếu > 15% thì kết quả KB3 rất nhạy với giả định này |
| 6 | **n nhỏ theo tháng** (KB1 ~11 lệnh/tháng, KB2 ~9) | Cao | Ngưỡng "1 tháng âm nhỏ" ở §5.9/§6.9 chỉ áp cho KB2/KB3; KB1 giữ "cả 3 dương" |
| 7 | **`vratio` tự pha loãng** (SMA20 gồm nến hiện tại) | Thấp | Giữ nguyên vì parity với C#; nhưng khi sweep `Kb3VsaMin` phải nhớ ngưỡng 1.2 ở đây "nhẹ" hơn 1.2 của SMA không-gồm-nến-hiện-tại |
| 8 | **Range state machine ≠ probe scan** (§4.3) | Trung bình | Bước kiểm bắt buộc: `n_range` lệch ≤ 25% so 322 mới đi tiếp |
| 9 | **Dedup gộp 3 nhánh chưa mô phỏng** | Trung bình | Router v7 mô phỏng dedup trên danh sách gộp **ngay từ đầu**, đừng để thành nợ như v6 |
| 10 | **Khoá tham số**: mỗi lần sweep là một lần rút thăm | Cao | Sau khi chốt cấu hình ở GĐ6, **đóng băng** vào `BASELINE.md` với ngày; mọi sweep sau đó phải chạy trên dữ liệu **mới** (live log) chứ không phải cùng cửa sổ 5–7/2026 |

---

## §10. Bản đồ port sang C#

**Kiểm trùng index đã chạy** (lệnh trong brief):
```
$ grep -oP 'InputParameter\("[^"]*",\s*\K\d+' WyckoffRunner.cs | sort -n | uniq -d
(không có dòng nào — 97 input, 0 trùng)
```
Index đang dùng: `10-13, 20-22, 24, 30, 32-36, 40, 42-85, 87, 88, 90-96, 100-109, 120, 121, 130-136, 140-149`.
→ **Khối 150–179 hoàn toàn trống** (không có index nào ≥ 150). v7 dùng khối này để không chen vào nhóm chủ đề cũ.

| Input mới (C#) | Index | Tên tiếng Việt hiển thị | Mặc định | Rủi ro parity |
|---|---:|---|---:|---|
| `RangeMode` | 150 | "Range: 0 = box 8 nến (v6) · 1 = theo cấu trúc (v7)" | **0** | — |
| `RangeFormBars` | 151 | "Range cấu trúc: số nến tối thiểu" | 30 | — |
| `RangeTouchMin` | 152 | "Range cấu trúc: số lần chạm tối thiểu mỗi biên" | 2 | **CAO** — cách đếm chạm (theo biên hiện tại, `SEP` nến) phải giống Python từng dòng |
| `RangeTouchSep` | 153 | "Range: 2 lần chạm phải cách nhau (số nến)" | 3 | như trên |
| `RangeTolFrac` | 154 | "Range: dung sai chạm = tỉ lệ × độ rộng" | 0.15 | Làm tròn double khi so `hi >= rhi − tol` |
| `RangeTolMinPts` | 155 | "Range: dung sai chạm tối thiểu (giá)" | 0.3 | — |
| `RangeMaxBars` | 156 | "Range: tuổi tối đa (số nến)" | 120 | — |
| `RangeBreakBufTicks` | 157 | "Range: close phải vượt biên bao nhiêu tick mới tính phá" | 2 | Trùng ý nghĩa với `SlBuf=2` đang dùng — **đừng gộp**, tách riêng để sweep độc lập |
| `RangeStructMinPts` | 158 | "Range cấu trúc: độ rộng TỐI THIỂU (giá)" | 2.0 | — |
| `RangeStructMaxPts` | 159 | "Range cấu trúc: độ rộng TỐI ĐA (giá)" | 6.0 | — |
| `EnableKb3` | 160 | "Bật KB3 (scalp biên↔biên trong range)" | **false** | — |
| `Kb3SlFloorPts` | 161 | "KB3: SL sàn (giá)" | 1.5 | — |
| `Kb3MinRr` | 162 | "KB3: bỏ lệnh nếu (khoảng tới biên đối diện)/R nhỏ hơn" | 1.5 | **CAO** — Python dùng `room/R`; C# phải dùng **cùng** định nghĩa `R` (sau sàn), không dùng R thô |
| `Kb3TpBufTicks` | 163 | "KB3: TP lùi vào trong biên đối diện (tick)" | 2 | — |
| `Kb3MaxHoldBars` | 164 | "KB3: giữ tối đa (số nến) rồi thoát" | 60 | **CAO** — C# thoát theo **nến đã đóng**, Python cũng vậy; nếu C# thoát intrabar thì lệch |
| `Kb3TrendMode` | 165 | "KB3: 0 = không lọc xu hướng · 1 = chỉ thuận" | 0 | — |
| `Kb3RequireConfluence` | 166 | "KB3: biên phải hợp lưu với vùng (D-1/phiên)" | false | Pool vùng C# dựng bằng `ProfileEngine`, Python bằng `tpo_counts` → **giá trị VAH/VAL/POC có thể lệch vài tick** |
| `Kb3ExitOnBreak` | 167 | "KB3: thoát ngay khi range vỡ ngược lệnh" | true | **CAO** — định nghĩa "vỡ" (2 nến xác nhận) phải giống hệt |
| `Kb3VsaMin` | 168 | "KB3: VSA tối thiểu của nến từ chối (× TB)" | 1.2 | `vratio` gồm nến hiện tại ở cả 2 phía → OK |
| `Kb3WickFrac` | 169 | "KB3: râu từ chối ≥ (râu/range)" | 0.35 | — |
| `BiasMode` | 170 | "Bias phiên: 0 = proxy 480 nến (v6) · 1 = TPO/VA · 2 = cả hai" | 0 | **RẤT CAO** — xem ghi chú dưới bảng |
| `BiasIbMinutes` | 171 | "Bias: độ dài Initial Balance (phút)" | 60 | Mốc bắt đầu phiên: C# `DayGapMin=45`, Python 45 → khớp; nhưng C# dùng `ProfileEngine.GroupByGap`, Python dùng `daily_levels_from_m1` → **phải đối chiếu danh sách mốc phiên trước khi tin** |
| `BiasVaTolPts` | 172 | "Bias: dung sai so POC 2 phiên (giá)" | 0.5 | — |
| `BiasMinScore` | 173 | "Bias: điểm tối thiểu để coi là có bias (1-3)" | 2 | — |
| `NoSupplyTest` | 174 | "KB1: nhịp hồi phải có nến test cạn cung (WY04)" | false | So `v < v[-1] && v < v[-2]` — chú ý nến volume 0 |
| `Kb2ZoneExtend` | 175 | "KB2: fade cả tại vùng D-1/phiên (không chỉ VWAP)" | false | Lệch pool như 166 |
| `Kb3DeltaConfirm` | 176 | "KB3: cần delta xác nhận (CHỈ LIVE — offline không kiểm được)" | false | **Không backtest được** → §8 |
| `Kb3AbsorbBonus` | 177 | "KB3: hấp thụ per-level = bonus hiển thị (KHÔNG gate)" | true | §8 |

**Rủi ro parity nghiêm trọng nhất (đọc trước khi code):**
1. **Range state machine.** `WyckoffRunner.Scan()` hiện **dựng lại box mỗi nến** (không có trạng thái). v7 cần
   **một đối tượng range có trạng thái** sống qua nhiều nến. Nếu C# làm state machine mà Python làm quét cửa
   sổ (như probe) → **hai hệ thống khác nhau**, không phải hai bản của một hệ. **Bắt buộc: cả hai làm state
   machine, cùng thứ tự 4 bước ở §4.3**, rồi reconcile bằng `n_range` + danh sách `(i0, valid_bar, brk_bar)`.
2. **Bias TPO.** Profile của C# (`ProfileEngine.BuildProfile`, `RowTicks=1`) và của Python
   (`value_area(tpo_counts(...))`, grid = tick) **cùng ý tưởng nhưng khác cài đặt** → VAH/VAL/POC lệch vài
   tick là bình thường. Với `BiasVaTolPts = 0.5` giá (5 tick) thì lệch 1–2 tick **không** đổi dấu bias, nhưng
   ca biên sẽ lệch. **Cách kiểm:** xuất VAH/VAL/POC của 60 phiên từ cả hai phía, so từng phiên, chấp nhận
   ≤ 2 tick; > 2 tick thì phải sửa.
3. **Thoát theo timeout/break.** Đây là hai outcome **mới** mà C# hiện không có (C# chỉ có TP/SL). Phải thêm
   vào cả `EmitLive`/CSV/Telegram, nếu không thì CSV live sẽ không có gì để reconcile với Python.
4. **`R` sau sàn SL.** Python tính `R = max(sl_raw − entry, floor)` **rồi** mới tính `Kb3MinRr`. Nếu C# tính
   `MinRr` trên `sl_raw` (R thô) thì số lệnh sẽ khác hẳn — đây là loại lỗi đã xảy ra 3 lần ở v6
   ([WYCKOFF_V6_PLAN §1](WYCKOFF_V6_PLAN.md)).
5. **Múi giờ**: `Bar.Time` của C# là UTC (đã kiểm); mọi thứ dính TPO CSV chỉ tồn tại ở Python và phải −7h.

---

## §11. LOG PROBE (số thật, chạy 2026-07-29)

Tái lập:
```bash
cd quantower-entry-signal/research/wyckoff/v7
python3 probe_range_feasibility.py     # A, B, C, F
python3 probe_kb3_geometry.py          # D
```
Script: [probe_range_feasibility.py](research/wyckoff/v7/probe_range_feasibility.py) ·
[probe_kb3_geometry.py](research/wyckoff/v7/probe_kb3_geometry.py)

### 11.A Phân bố độ rộng cửa sổ M1 (chọn ngưỡng width bằng dữ liệu)
```
dxFeed M1 = 103857 nen | 2025-11-02 23:22:00 -> 2026-07-27 15:56:00 (UTC)

A. PHAN BO DO RONG CUA SO M1 (don vi 'gia'; 1 gia = 10 tick)
      L      bo      n    p10    p25    p50    p75    p90
     30  5-7/26   7410    6.3    8.5   11.7   16.6   23.6
     30 9 thang   9509    6.8    9.2   13.2   19.8   30.3
     60  5-7/26   7224    9.3   12.3   17.0   24.1   33.7
     60 9 thang   9124   10.0   13.4   19.1   28.5   42.0
     90  5-7/26   7038   11.7   15.4   21.4   30.2   41.9
     90 9 thang   8797   12.4   16.6   23.9   34.8   51.6
    120  5-7/26   6852   13.8   18.1   25.3   35.0   49.7
    120 9 thang   8487   14.7   19.7   28.1   40.2   58.4
```
→ **Đọc:** một cửa sổ 30 nến hẹp hơn **6.3 giá** đã thuộc **decile thấp nhất** ⟹ `RangeStructMaxPts = 6.0`
là "vùng nén thật", không phải số bốc. Cũng cho thấy `RangeMaxPts = 7.5` của v6 (trên box **8** nến) và
6.0 (trên **30** nến) là hai chuẩn khác nhau — đừng so trực tiếp.

### 11.B Số range hợp lệ (khả thi n cho KB3)
```
B. SO RANGE HOP LE (>=2 cham MOI bien, khong chong lap, cua so 30-120 nen)
    minw  maxw |  5-7/26  05  06  07 cham sau XN |  9thg    w~  nen~  pha up/dn
     1.5   4.0 |      82   9  24  49         121 |    82   3.9    36      17/23
     2.0   6.0 |     322  52 107 163         461 |   326   5.7    37     87/118
     2.0   8.0 |     641 123 234 284         979 |   679   7.5    38    207/245
     3.0   8.0 |     640 123 234 283         976 |   678   7.5    38    207/244
     3.0  12.0 |    1070 276 414 380        1978 |  1215  10.5    41    393/437
     2.0  15.0 |    1158 316 445 397        2433 |  1374  11.6    43    454/495
```
→ **Kết luận về n:** KB3 **KHÔNG** thiếu n. Ở cấu hình mặc định (2.0–6.0 giá): **322 range**, **461 lần chạm
sau nến xác nhận** trong 5–7/2026, chia theo tháng 52/107/163 range. ⚠ **461 là CẬN TRÊN** — chưa qua lọc
chất lượng nến từ chối, `Kb3MinRr`, thanh khoản, phiên chết, dedup, 1-vị-thế. v6 cho thấy mức tụt có thể rất
lớn (hàng nghìn cú phá → 33 lệnh). Nếu sau lọc n < 25 → **"không kết luận"**, và cách mở rộng **không phải**
lùi cửa sổ dxFeed về trước (bảng cột "9thg" chỉ thêm 4 range: 326 vs 322 ⟹ trước tháng 5 GCQ26 quá mỏng,
đúng như [BASELINE §6](research/wyckoff/BASELINE.md)) mà là **front-month/CCPA khác**.

### 11.C Phiên dùng cho bias
```
TPO-daily: n=952  2026-06-25 23:00:00 -> 2026-07-25 03:30:00  ngay-lich=26  gia-tri TPO phan biet=22
  ho so TPO co IB hop le=22 | co VA hop le=22
daily_levels_from_m1: tong phien=160 (9 thang) | 5-7/2026=61 -> so cap D-1->D dung duoc=159/60
  vd 3 phien cuoi: [('07-22 22:00', 4051.7, 4121.9, 4042.5), ('07-23 22:00', 4056.7, 4071.5, 4044.3), ('07-26 22:00', 4093.9, 4106.3, 4085.7)]
```
→ `TPO-chart-daily.csv` = **22 phiên** (không phải 26 ngày lịch — 1 phiên vắt qua 2 ngày lịch), tất cả 22 đều
có IB và VA đọc được → **21 cặp D-1→D**: quá mỏng, chỉ làm **đối chứng**. Nguồn chính = `daily_levels_from_m1`:
**60 cặp** trong 5–7/2026, **159 cặp** trong 9 tháng. Phiên bắt đầu **22:00 UTC**.

### 11.D Hình học KB3 (R biến thiên, gate, hợp lưu)
```
--- range minw=2.0 maxw=6.0: n_range=322  n_lan_cham(sau XN)=461
    theo thang: 05=71 06=134 07=256
    R (gia)        p10=0.50 med=1.00 p90=2.00
    room->bien doi dien (gia) med=4.40
    RR kha dung    p10=1.68 p25=2.67 med=4.13 p75=6.12 p90=9.80
      so lan cham co RR >= 1.0:  448  (97%)
      so lan cham co RR >= 1.5:  424  (92%)
      so lan cham co RR >= 2.0:  392  (85%)
      so lan cham co RR >= 2.5:  358  (78%)
      so lan cham co RR >= 3.0:  318  (69%)
    gate THUAN xu huong v6 tai nen cham: trend=+1:212  trend=0:11  trend=-1:238
      trong do 'thuan huong scalp' (trend==side) = 224 (49%) -> neu ap gate v6 nguyen ban, KB3 con n=224
      neu chi cho KB3 chay khi trend==0: n=11 (2%)
    dung phia VWAP (theo huong scalp): 210 (46%)
    bien range hop luu voi >=1 vung (D-1/session) trong +-0.3 gia: 82 (18%)
    bien range hop luu voi >=1 vung (D-1/session) trong +-0.7 gia: 176 (38%)

--- range minw=2.0 maxw=8.0: n_range=641  n_lan_cham(sau XN)=979   [khoi nay RUT GON dong, so nguyen van]
    R (gia)        p10=0.60 med=1.30 p90=2.40 | room med=5.90 | RR med=4.50
      RR>=1.5: 934 (95%)   RR>=2.0: 880 (90%)
    trend=+1:471  trend=0:36  trend=-1:472 | trend==side 431 (44%) | trend==0: 36 (4%)
    dung phia VWAP: 398 (41%) | hop luu +-0.3: 159 (16%) | +-0.7: 343 (35%)
```
→ 3 kết luận thiết kế: (1) **R thô quá nhỏ** (med 1.0 giá) ⟹ **phải có sàn SL**; (2) **gate `trend==0` BỊ BÁC
NGAY** (n=11); (3) **hợp lưu biên với vùng là thiểu số** (18%/38%) ⟹ đủ mẫu cả 2 nhóm để partition, không
được mặc định bật.
⚠ RR ở đây tính trên **R thô** — sau khi áp sàn SL, các tỷ lệ % sẽ **giảm**; phải chạy lại (§6.10 bước 2).

### 11.E Look-ahead của cột TPO (bằng chứng)
```
khoi TPO: tong=22 | VAH/VAL/POC DOI trong khoi=0 | KHONG doi (gia tri CHOT)=22
vd khoi 688 (6 dong dau, gio la UTC+7):
    06-30 05:00 VAH=4058.0 VAL=3998.0 POC=4041.0 IBH=4037.0 IBL=4024.0
    06-30 05:30 VAH=4058.0 VAL=3998.0 POC=4041.0 IBH=4037.0 IBL=4024.0
    ... 46 dong, dong cuoi 07-01 03:30
```
→ **22/22 khối có VA/POC/IB không đổi suốt phiên** = giá trị **chốt** dập lên mọi nến, kể cả nến đầu phiên.
**Dùng intraday = look-ahead.** Xem §2.2.

### 11.F Độ nhạy định nghĩa range (chọn `FORM`/`TOUCH`)
```
do nhay dinh nghia range (maxw=6.0, minw=2.0)
 form need | n_range 5-7/26   05  06  07 | arms(cham sau XN) | nen~ | pha up/dn/timeout
   30    2 |     322   52 107 163 |               461 |   37 | 87/118/0
   30    3 |     206   34  64 108 |               267 |   40 | 57/71/0
   45    2 |     118   21  36  61 |               182 |   54 | 29/36/0
   45    3 |      87   12  25  50 |               128 |   56 | 26/24/0
   60    2 |      48    6  16  26 |                70 |   69 |  9/11/0
   60    3 |      37    4  10  23 |                59 |   69 |  6/9/0
```
→ `FORM=30, TOUCH=2` làm mặc định (n dồi dào); `FORM=45, TOUCH=3` là biến thể "trung thành Wyckoff" vẫn còn
128 lần chạm; `FORM=60` cho tháng 5 chỉ 4–6 range ⟹ **quá mỏng theo tháng**, không dùng.

### 11.G Giới hạn của chính bộ probe (đọc trước khi trích số §11)
1. Probe dùng **quét cửa sổ greedy không chồng lấn**, **không** phải state machine của §4.3 → số range sẽ
   lệch khi implement thật. Đã đặt bước kiểm ≤ 25% ở §4.10.
2. Probe đếm chạm theo **biên cuối cùng** của range; state machine đếm theo **biên tại thời điểm đó**.
3. Probe **không** áp: lọc chất lượng nến từ chối, sàn SL, `Kb3MinRr`, thanh khoản, phiên chết, dedup,
   cooldown, 1-vị-thế → **461 là cận trên, không phải n dự kiến**.
4. Dung sai chạm (`TOLF=0.15`, `TOLMIN=0.3` giá) và `SEP=3` **chưa được kiểm độ nhạy** (chỉ kiểm `FORM`/
   `TOUCH`) → ⟦CẦN QUYẾT Ở GĐ6⟧: sweep `TOLF ∈ {0.10,0.15,0.20}`, `SEP ∈ {2,3,5}` và báo cả 9 ô.
5. Probe **không có WR nào** — không suy ra được xác suất thắng từ hình học.
