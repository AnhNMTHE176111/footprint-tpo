# PARITY_V7 — đối chiếu `WyckoffRunner.cs` v7 ↔ engine Python

> Viết 2026-07-29 (GĐ9). Đối tượng: [WyckoffRunner.cs](../../WyckoffRunner.cs) v7 vs
> [cbr_v6.py](cbr_v6.py) + [entry_dxfeed.py](../entry_dxfeed.py).
> Cấu hình: **đóng băng** theo [AUDIT_V7.md](AUDIT_V7.md) §14 — không tinh chỉnh gì ở pha này.
> Mọi con số dưới đây là **output thật** của lệnh ghi kèm, không có số nào gõ tay.

## 0. Phán quyết

| | |
|---|---|
| **Parity thuật toán (C# ↔ Python, offline)** | ✅ **ĐẠT** — 33/33 tín hiệu khớp, **0 lệch**, entry & SL khớp tới **0,0 tick** |
| **Parity DLL-trong-Quantower (live)** | ⏳ **CHƯA ĐẠT — chưa có dữ liệu.** Cần CSV tín hiệu từ máy Windows (GĐ10) |
| **Build** | ✅ 0 warning / 0 error |
| **Trùng index `InputParameter`** | ✅ rỗng (97 input) |

⚠ **Phân biệt hai loại parity** — chỗ này dễ tự lừa mình:
- Cái đã ĐẠT là **thuật toán C# viết đúng như thuật toán Python**. Tôi trích nguyên văn các hàm tính
  của `WyckoffRunner.cs` vào một chương trình console ([ParityHarness.cs](parity/ParityHarness.cs)), cho
  ăn **đúng file CSV** mà Python đọc, rồi so từng tín hiệu.
- Cái **CHƯA** kiểm được là **DLL chạy trong Quantower** có ra cùng tín hiệu không. Quantower có thể lọc
  nến rác, thiếu nến, lấy volume từ `VolumeAnalysis` khác dxFeed, hoặc khác múi giờ feed. Không có cách
  nào kiểm việc đó trên Linux → là việc của GĐ10.

---

## 1. Bảng so sánh từng tín hiệu

Tái lập:
```bash
cd quantower-entry-signal/research/wyckoff/parity
dotnet build -c Release
dotnet bin/Release/net10.0/ParityHarness.dll \
  "../../../../data-export/27-7/_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv" \
  cs_signals.csv
cd .. && python3 parity_v7.py parity/cs_signals.csv
```

Output thật (rút gọn — bảng đầy đủ 33 dòng in ra khi chạy lệnh trên):

```
PARITY V7 — OFFLINE (thuat toan C# harness) vs Python cbr_v6
Python :  33 tin hieu | 2026-05-26 09:44:00 -> 2026-07-23 12:20:00
C#     :  33 tin hieu | 2026-05-26 09:44:00 -> 2026-07-23 12:20:00

thoi gian (Python)   phia     entry py   entry C#     SL py     SL C#  d entry    d SL  ket qua
2026-05-26 09:44:00  SHORT     4545.80    4545.80   4548.80   4548.80     0.0t    0.0t  KHOP
2026-05-26 11:25:00  SHORT     4558.00    4558.00   4561.00   4561.00     0.0t    0.0t  KHOP
...  (31 dòng còn lại, tất cả KHOP 0.0t/0.0t)
2026-07-23 12:20:00  SHORT     4077.80    4077.80   4082.00   4082.00     0.0t    0.0t  KHOP

TONG KET: khop 33  |  chi Python 0  |  chi C# 0  |  lech gia tri 0  |  tong lech 0/33 = 0.0%
PHAN QUYET (tieu chi GD9): DAT — 0 tin hieu lech, 0 lech gia tri
```

Tiêu chí GĐ9: mục tiêu 0 lệch → **đạt mức cao nhất**, không cần dùng tới hạn mức "≤2 lệch được phép".

---

## 2. Chín chỗ dễ lệch — kiểm riêng từng cái

| # | Chỗ | Python làm gì | C# làm gì | Khớp? |
|---|---|---|---|---|
| 1 | **Múi giờ** | `dt` = UTC thô từ cột `Time left`, không đổi giờ | `InDeadWindow()` dùng `tUtc.Hour` vì `DeadUseUtc=true` (mặc định) | ✅ **KHỚP** — đúng chỗ v5 từng sai (neo giờ hiển thị → lọc thành no-op) |
| 2 | **Warmup** | vòng quét từ `VSA_MA+2` = 22; `WARMUP_AFTER_GAP=20`; trend cần `i>=480`; liq cuộn 1000 | `VsaPeriod+2` = 22; `WarmupBars=20`; `i>=TrendBars`; `liqW=1000` | ✅ **KHỚP** |
| 3 | **Reset VWAP theo phiên** | `gap = (dt - dt[-1]).total_seconds()/60 > 30` → reset `csum_pv/csum_v` | `gap = (Time - B[i-1].Time).TotalMinutes > 30` → reset `csPV/csV` | ✅ **KHỚP** |
| 4 | **TB trượt thanh khoản** | `add_liqbase`: mean của **`vma`**, **GỒM** nến hiện tại | trước GĐ9: mean của **`Vol`**, **KHÔNG** gồm nến hiện tại → **ĐÃ SỬA** ở GĐ9 thành mean `Vma` có gồm nến hiện tại | ✅ **KHỚP sau khi sửa** — xem §3 |
| 5 | **VSA ratio** | `win = B[max(0,i-19) .. i]` → SMA20 **có** nến hiện tại | `q.Enqueue(b.Vol)` **trước** khi chia → SMA20 **có** nến hiện tại | ✅ **KHỚP** (cả hai đều "tự pha loãng" như SPEC §9 #7 ghi) |
| 6 | **Làm tròn tick / đơn vị giá** | tham số lưu bằng **tick** (`RMIN=30`), `TICK=0.1` | tham số lưu bằng **giá** (`RangeMinPts=3.0`), chia `_tick` khi dùng | ✅ **KHỚP** — quy đổi 27/27 tham số đúng, xem §4 |
| 7 | **Nến-đóng-only** | quét tới `N` (hết chuỗi, dữ liệu lịch sử nên nến cuối đã đóng) | quét tới `N-1` (**bỏ** nến đang hình thành để không repaint) | ⚠ **KHÁC CÓ CHỦ Ý** — xem §5 "khác biệt đã biết" |
| 8 | **Dedup / cooldown** | `dedup` (cùng phía, ≤6 nến) → `cooldown` (15 nến/phía), áp **sau** lọc phiên chết | `Cooldown_(Dedup(raw))` sau `RemoveAll(InDeadWindow)` — **cùng thứ tự** | ✅ **KHỚP** |
| 9 | **Nguồn nến** | CSV dxFeed GCQ26 (103.857 nến) | trong harness: **cùng CSV đó**. Trong Quantower thật: nến từ feed của user | ⚠ **RỦI RO CÒN LẠI** — không kiểm được offline, xem §0 |

---

## 3. ⭐ Lỗi parity phát hiện & sửa ở GĐ9 — trung bình trượt thanh khoản

Đây là phát hiện thật của pha này, đúng loại "lỗi im lặng" mà GĐ9 tồn tại để bắt.

**Sai chỗ nào:** hai bên tính `liqbase` (mốc so thanh khoản) khác nhau ở **hai** điểm cùng lúc:

| | Python `add_liqbase()` | C# (trước khi sửa) |
|---|---|---|
| Lấy trung bình của | **`vma`** (đã là SMA20 của volume) | **`Vol`** (khối lượng thô) |
| Nến hiện tại | **CÓ** gồm (`dq.append` rồi mới chia) | **KHÔNG** gồm (enqueue *sau* khi chia) |

**Đo mức ảnh hưởng trước khi kết luận** (không suy đoán):

```
So nen: 103857
Quyet dinh LIQ giong nhau: 103494 (99.650%)
Quyet dinh LIQ KHAC nhau : 363 (0.350%)
Lech tuong doi base: med=0.4115% p95=2.4481% max=84.72%
```

**Nhưng có đổi tín hiệu không?** Chạy engine Python với **cả hai** cách tính `liqbase`:

```
Python (liqbase = mean VMA, GOM nen hien tai): n=33 WR=48.5% tong=+47.0R EV=+1.424
C#     (liqbase = mean VOL, KHONG gom       ): n=33 WR=48.5% tong=+47.0R EV=+1.424
Tin hieu chi co o Python: 0
Tin hieu chi co o C#    : 0
Khop: 33
```

→ Trên cửa sổ 5–7/2026 lỗi này **không đổi một tín hiệu nào**. Vẫn sửa, vì hai lý do:
1. "Không đổi trên cửa sổ này" **không** có nghĩa "không đổi trên live" — 363 nến đã ra quyết định khác
   nhau; chỉ là chúng không trùng nến vào lệnh. Đây là bom hẹn giờ, không phải chuyện vô hại.
2. Parity phải **đúng từng dòng** để mọi lệch trong tương lai còn quy được về nguyên nhân.

Đã sửa tại [WyckoffRunner.cs](../../WyckoffRunner.cs) (khối `BuildBars`, comment `v7/GĐ9 SỬA PARITY`).

---

## 4. Bảng đối chiếu 27 tham số cấu hình đóng băng

Output thật của script đối chiếu (Python `KB1_CONFIG` ↔ C# default, có quy đổi tick↔giá):

```
Python (KB1_CONFIG)      quy doi    C#                   C# default KHOP?
RANGE_LEN=8              8          RangeLen             8          OK
RMIN=30                  3.0        RangeMinPts          3.0        OK
RMAX=75                  7.5        RangeMaxPts          7.5        OK
BVSA=2.0                 2.0        BreakVsa             2.0        OK
BBODY=0.5                0.5        BreakBody            0.5        OK
WAIT=12                  12         WaitBars             12         OK
PMIN=0.6                 0.6        PullMin              0.6        OK
PMAX=1.0                 1.0        PullMax              1.0        OK
HOLD_TOL=2               2          HoldTolTicks         2          OK
RBODY=0.35               0.35       ResumeBody           0.35       OK
FLOOR=30                 3.0        SlFloorPts           3.0        OK
CAP=70                   7.0        SlCapPts             7.0        OK
BUF=2                    2          SlBuf                2          OK
COOL=15                  15         Cooldown             15         OK
RR=4.0                   4.0        RR                   4.0        OK
TREND=True               True       TrendFilter          True       OK
VWAP=True                True       VwapAlign            True       OK
LIQ=True                 True       LiquidityFilter      True       OK
LIQ_K=0.75               0.75       LiquidityRatio       0.75       OK
DEAD=True                True       SkipDeadSession      True       OK
DEAD_FROM=2              2          DeadStartHour        2          OK
DEAD_TO=8                8          DeadEndHour          8          OK
CLEAN=True               True       CleanBreak           True       OK
CL_LOOK=20               20         CleanLook            20         OK
CL_W=5                   5          CleanWin             5          OK
CL_CLOSE=0.5             0.5        CleanClosePos        0.5        OK
VOL_FLOOR=20.0           20.0       VolFloor             20         OK
So tham so LECH: 0
```

### 4.1 Input **thay đổi** ở v7 (chỉ 1)

| Input | Index | Cũ | v7 | Vì sao |
|---|---:|---|---|---|
| `EnableReversal` | 66 | `true` | **`false`** | AUDIT_V7 §13: KB2 = FAIL (p=0.072; LONG EV chỉ +0.154R; OOS duy nhất EV −0.167R). Port ở dạng **tắt**, bật lại chỉ để thu log OOS, **không cấp vốn** |

### 4.2 Input **không** thêm mới — và vì sao

SPEC §10 dự kiến thêm khối index 150–179 (`RangeMode`, `RangeFormBars`, `RangeTouchMin`, …) cho 2 feature v7.
**Không thêm cái nào**, vì cấu hình đóng băng của audit là `RangeMode=0, BIAS_ON=False` — **cả hai feature
đều KHÔNG PASS**:
- `RangeMode=1` (range cấu trúc): `n_range` lệch **77%** so probe (ngưỡng SPEC §4.3 là 25%) → dừng theo spec;
  và khi vẫn chạy để xem thì ra **n=0 lệnh**.
- `BIAS_ON` (bias phiên TPO): A1 `n=9`, A2 `n=8` — dưới ngưỡng 25 → **không kết luận**, baseline A0 giữ nguyên.

Thêm input chết vào UI chỉ tạo ảo giác "đã có tính năng". Khi nào có bằng chứng thì thêm.

**KB3: không có dòng code nào.** Audit KILL bằng 4 lý do độc lập (EV −0.254R ở phần không phải "KB1 sớm";
chết ở 2 tick phí; MDD 27,5R; 0 range VALID trong 6 tháng OOS).

---

## 5. Khác biệt đã biết và **chấp nhận** (không che)

| # | Khác biệt | Ảnh hưởng | Vì sao chấp nhận |
|---|---|---|---|
| 1 | **Nến cuối chuỗi**: Python quét tới `N`, C# tới `N-1` | Trên dữ liệu này: **0 tín hiệu** khác nhau (tín hiệu cuối 2026-07-23, cách cuối chuỗi 4 ngày) | C# **buộc** phải bỏ nến đang hình thành, nếu không sẽ repaint — vẽ tín hiệu rồi xoá khi nến đóng khác đi. Đây là đúng, không phải lỗi. Chênh lệch tối đa có thể có: 1 tín hiệu ở nến cuối cùng |
| 2 | **Nguồn nến**: harness dùng CSV dxFeed; Quantower thật dùng feed của user | **Chưa đo được** | Không kiểm được offline. Là rủi ro **mở**, phải đo ở GĐ10. Nếu feed live lọc nến khác dxFeed thì `Vma`/`Vratio`/`vwap` lệch theo và tín hiệu sẽ khác |
| 3 | **`liqbase` ở đầu chuỗi** lệch tới 84,7% khi cửa sổ 1000 nến còn chưa đầy | 0 tín hiệu (vùng đó nằm trước 2026-05, ngoài cửa sổ tính số) | Cả hai bên đều chia cho `len(dq)` thực tế thay vì 1000 cố định → hành vi giống nhau, chỉ là giá trị nhỏ khi cửa sổ ngắn |
| 4 | **Nhánh KB2 chưa được kiểm parity** | Không ảnh hưởng số KB1 | `EnableReversal=false` ⇒ không chạy. Khi nào bật để thu log OOS thì **phải kiểm parity riêng cho nó trước** |
| 5 | **`ParityHarness.cs` là bản COPY**, không phải chính file production | Rủi ro trôi lệch nếu sửa 1 bên | Mỗi khối trong harness có dấu `<<< COPY tu WyckoffRunner.cs` + số dòng gốc. Sửa `WyckoffRunner.cs` **phải** sửa harness rồi chạy lại parity |

---

## 6. Build & kiểm trùng index — output thật

```
$ ./build-wyckoff.sh
Build succeeded.
    0 Warning(s)
    0 Error(s)
==> /home/asl86/Documents/footprint-tpo/quantower-entry-signal/dist/WyckoffRunner.dll

$ grep -oP 'InputParameter\("[^"]*",\s*\K\d+' WyckoffRunner.cs | sort -n | uniq -d
(rỗng — không trùng)

$ grep -c "InputParameter" WyckoffRunner.cs
97
```

---

## 7. Việc còn lại (GĐ10)

1. Copy [dist/WyckoffRunner.dll](../../dist/WyckoffRunner.dll) sang Quantower máy Windows.
2. Đặt input **đúng bảng §4** (mặc định đã đúng — chỉ cần **không** đổi gì; `EnableReversal` phải là **tắt**).
3. Bật `Xuất CSV toàn bộ tín hiệu`, chạy ≥1–2 tuần, lấy CSV về.
4. Chạy `python3 parity_v7.py <csv-live> --live` → cập nhật mục §0 dòng "parity live".
5. **Cho tới khi bước 4 xong: mọi lệch giữa live và backtest đều CÓ THỂ do port sai**, không được coi tín
   hiệu live là bằng chứng về chiến lược. Đây là câu quan trọng nhất của cả file.
