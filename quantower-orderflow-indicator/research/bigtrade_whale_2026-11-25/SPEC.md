# SPEC — Big Trade "lệnh cá mập": một thuật toán cho cả hai chế độ ngưỡng (C#)

> Fable chốt 2026-11-25 sau vòng 1 (`r1_review.md`, `R1-KET-QUA.md`). Opus implement + test; Fable review code.
> Đây là **định nghĩa hiển thị**, KHÔNG phải lợi thế giao dịch đã kiểm định: không viết comment, tooltip hay README nào ngụ ý vòng dự báo được giá.
> Bản Python chuẩn từng nến: `bw2_ref.py` (cùng thư mục). C# phải trùng **từng vòng** với nó.

## 0. Tóm tắt

- Vòng Big Trade nổ khi **một lệnh đơn lớn hơn hẳn lệnh lớn thứ K của mọi lệnh đơn trong 5 ngày nến gần nhất**, K = 8 lệnh cho mỗi ngày nến (1380 phút nến). Đủ 5 ngày thì K = 40.
- Tham số là **hằng số trong code**: `D = 5`, `R = 8`, `W = 1380`. **Không có ô chọn mật độ, không sàn, không giới hạn vòng mỗi nến.**
- Áp **y hệt** cho "Theo CORVEN" và "Không theo CORVEN (thống kê)". Ô "Chế độ ngưỡng" từ nay chỉ điều khiển chấm Bid/Ask.
- Chưa đủ 1380 phút nến có số liệu lệnh đơn → **không vẽ vòng nào** (không quay về ngưỡng cố định 10).
- Chấm Bid/Ask, kiệt sức, Stacked Imbalance: **không đổi một dấu nào** ở cả hai chế độ.

## 1. Quy ước

- `rhu(x) = Floor(x + 0,5)` (`BaselineWindow.RoundHalfUp`).
- `m` = phút một nến = `BarMinutesNow` (số thực). `m <= 0` (không phải nến thời gian, hoặc không rõ) → dùng `m = 1`. Khung không nguyên phút (vd 0,5) dùng nguyên giá trị đó. Hai trường hợp này **chưa đo**, chỉ quy định để code không rẽ nhánh.
- **Nến có số liệu** = nến đã đóng có ít nhất một ô lệnh đơn `mot > 0`. Ô lấy như hiện nay: từ feed (`MaxOneTradeVolume`), nếu nến không có ô nào thì từ `BigTradeLog.CellsOf(giờ mở nến, tick)`.
- **Phút nến** của hàng đợi = số nến có số liệu trong hàng đợi × `m`. Một **ngày nến** = 1380 phút nến. Đếm theo nến có số liệu, không theo lịch.
- Chỉ số mảng đếm của một lệnh đơn = `StatRank.Index(mot)` = `min(Floor(mot), 4095)`.

## 2. Luật

Hằng số: `Days = 5`, `PerDay = 8`, `DayMinutes = 1380`, `WarmMinutes = 1380`, `MergeMin = 2`, `RangePerMerge = 8,0`.

**Trạng thái** (lớp mới `BigTradeWhale`, mục 3):
- Hàng đợi `n = max(1, rhu(Days × 1380 / m))` nến có số liệu gần nhất; mỗi phần tử = mảng chỉ số của **mọi** lệnh đơn > 0 của nến đó. (M1 6900 · M5 1380 · M15 460 · M30 230 · H1 115 · H4 29 · D1 5.)
- Mảng đếm 4096 ô + tổng số mẫu, cộng khi nến vào, trừ khi nến ra.
- Hàng đợi biên độ `N = BaselineWindow.BarsFor(m)` số (120 phút, **không** phụ thuộc ô "Nền tự co theo khung"): biên độ = tick cao nhất − tick thấp nhất trong các ô `mot > 0` của nến.

**Ngưỡng của nến đang xét** (chỉ từ nến đã đóng trước):
1. `phút = số nến hàng đợi × m`. Nếu `phút < 1380` → **chưa có ngưỡng**.
2. `K = max(1, rhu(8 × phút / 1380))`.
3. Nếu tổng số mẫu < K → chưa có ngưỡng.
4. `ngưỡng` = chỉ số `v` lớn nhất (quét từ 4095 xuống 1) sao cho số mẫu có chỉ số ≥ `v` đạt ≥ K. Tức giá trị lớn thứ K.

**Chọn vòng** (khi có ngưỡng và nến có ô `mot > 0`):
1. `g = 2`; nếu hàng đợi biên độ có ≥ 5 số và trung bình > 0 thì `g = max(2, rhu(trung bình / 8))`.
2. `BigTradeAdaptive.Select(cells, ngưỡng, g, cap: 0, strict: true)`: ô có `mot > ngưỡng` (**lớn hơn hẳn**), duyệt lệnh giảm dần (bằng nhau: tick thấp trước, rồi chỉ số), bỏ ô cách ô đã giữ ≤ g tick, không giới hạn số vòng. Vẽ theo tick tăng dần như cũ.
3. Cỡ vòng `BigTradeLogic.SizeFrac(mot, max(1, ngưỡng))`. Màu, độ mờ, `CellBig = true`, `CellDot = false`, `CellBid`, `CellAsk`, `CellSide` như cũ.

So sánh dùng **giá trị thật** của `mot` với ngưỡng (ngưỡng tối đa 4095): lệnh 5000 khi ngưỡng 4095 vẫn nổ.

**Nộp nến đóng** (đúng 1 lần mỗi nến đóng, SAU khi đã xét nến đó, trong `AddToBaseline` đúng chỗ đang gọi `_btAdapt.AddClosedBar`): nến không có ô nào `mot > 0` → không nộp, không tính là một nến. Ngược lại nộp mọi lệnh đơn > 0 và biên độ. Nến đang chạy không nộp.

## 3. Lớp C# mới

File `CellBigLogic.cs` (hoặc file mới `BigTradeWhale.cs`; nếu file mới thì thêm vào project `tests` và `perf/Golden` nếu chúng liệt kê file nguồn). Thuần, không phụ thuộc Quantower.

```csharp
public sealed class BigTradeWhale
{
    public const int Days = 5, PerDay = 8, DayMinutes = 1380, WarmMinutes = 1380, MergeMin = 2;
    public const double RangePerMerge = 8.0;
    public BigTradeWhale(double minutesPerBar);
    public int WindowBars { get; }              // n
    public int Count { get; }                   // số nến có số liệu đang giữ
    public long Samples { get; }
    public double Minutes { get; }              // Count x m
    public int K { get; }                       // hạng hiện tại (0 khi chưa đủ WarmMinutes)
    public bool TryThreshold(out int thr);      // false = chưa có ngưỡng
    public int MergeTicks();
    public void AddClosedBar(IReadOnlyList<(long tick, double mot)> cells);
}
```

Chi phí: mỗi nến đóng cộng / trừ vài chục đến vài trăm số; `TryThreshold` quét tối đa 4096 ô (như `StatRank.Threshold` hiện nay). Bộ nhớ M1: 6900 nến × vài chục số.

**Xóa:** lớp `StatBigTrade`; phần trạng thái của `BigTradeAdaptive` (`Threshold`, `MergeTicks`, `AddClosedBar`, `KthLargest`, hàm tạo) — **giữ** hàm tĩnh `Select` (cả hai overload). `BigTradeLogic.Hit` không còn ai gọi thì xóa; giữ `SizeFrac`. Sửa / xóa test tương ứng trong `tests/AdaptiveTests.cs`, `tests/StatThresholdTests.cs`, `tests/CellBigTests.cs`.

## 4. Ghép vào `OrderFlowBubbles.cs`

- Trường mới `private BigTradeWhale _btWhale;` thay `_btAdapt` và `_statBt`. Tạo trong `InitBaselines()` ở **mọi** chế độ: `new BigTradeWhale(BarMinutesNow)`.
- Khối Big Trade của `ComputeBar` (hiện có hai nhánh `_statBt` / `else`) còn **một nhánh**: lấy `btCells` như cũ (kể cả dòng lấy từ nhật ký), `_btWhale.TryThreshold` → `MergeTicks` → `Select(strict: true)` → tạo `Bubble`.
- `AddToBaseline`: `_btWhale.AddClosedBar(bt)` thay hai lời gọi cũ; cách dựng `bt` (feed trước, nhật ký sau) giữ nguyên.
- `BaseKey()`: bỏ `BigTradeDensity`, thêm `m` của Big Trade (để đổi khung thì dựng lại): vd `DesiredBaseBars() + "|bw:" + m`.
- `StatKey()`: bỏ `StatBtMinutes`, `StatBtRarePbp`.
- Ghi nhật ký lệnh đơn (`TryAppend`) giữ nguyên.

**Tooltip** (một dạng cho cả hai chế độ):
`Big trade: 1 lệnh 86 hợp đồng (ngưỡng > 47: nhóm 8 lệnh lớn nhất mỗi ngày, tính trên 5 ngày gần nhất) | ô 12 Bid 90 Ask`
Khi hàng đợi chưa đủ 5 ngày nến, thay "5 ngày" bằng số ngày nến đang có, một chữ số thập phân, dấu phẩy thập phân kiểu Việt không bắt buộc (dùng `InvariantCulture` như các tooltip khác): `tính trên 2.3 ngày gần nhất`.

## 5. Ô cài đặt

**Gỡ khỏi Settings (xóa hẳn property):**
| Ô | Property |
|---|---|
| Big Trade · Ngưỡng tự thích nghi (theo khung + phiên) | `BigTradeAdaptiveEnabled` |
| Big Trade · Mật độ đích (vòng/nến) | `BigTradeDensity` |
| Big Trade · Sàn (hợp đồng) | `BigTradeFloor` |
| Big Trade · Tối đa vòng mỗi nến | `BigTradeMaxPerBar` |

**Xóa property ẩn:** `BigTradeMinContracts`, `BigTradeCeil`, `BigTradeMergeDiv`, `BigTradeMergeMin`, `StatBtMinutes`, `StatBtRarePbp`. Bỏ ba dòng `Rel(nameof(BigTrade…), nameof(BigTradeAdaptiveEnabled))` trong `Settings`.

**Giữ:** "Big Trade (lệnh đơn) · Bật" (`BigTradeEnabled`), `BigTradeOpacity`. **Không thêm ô nào.**

**Đổi chữ** (không đổi property, không đổi giá trị):
- "Chế độ ngưỡng (chấm Bid/Ask + Big Trade)" → "Chế độ ngưỡng chấm Bid/Ask".
- "Nền tự co theo khung (chấm, Big Trade, kiệt sức)" → "Nền tự co theo khung (chấm, kiệt sức)".
- Comment đầu khối Big Trade và khối chế độ ngưỡng: viết lại theo luật mới, bỏ câu "Big Trade nổ khi lệnh đơn lớn hơn hẳn 99% lệnh đơn 240 phút gần nhất" và "ngưỡng 10 cho ~0,73 vòng mỗi nến M5".

**`tests-dll/Program.cs`:** số ô `27 → 23`; bỏ các `chk` của 10 property đã xóa và thêm chúng vào danh sách "đã bỏ"; sửa các dòng so dấu vân tay (mục 6).

## 6. Dấu vân tay

- `BigTradeEnabled, BigTradeMinContracts, "bigtrade-v1"` → `BigTradeEnabled, "bigtrade-whale-v1:5/8/1380/" + m` (`m` in bằng `InvariantCulture`; `m` sau khi quy `<= 0` thành 1).
- Bỏ hẳn đoạn `|bta-v1:…`.
- Chế độ thống kê: `|stat-v1:5/200/5/True/2/120/240/100` → `|stat-v2:5/200/5/True/2/120` (bỏ hai số Big Trade; đổi nhãn để không nhầm với chuỗi cũ).
- Mọi phần khác giữ nguyên từng ký tự. Hệ quả: mọi bản niêm phong cũ được tính lại một lần ở cả hai chế độ (chấm tính lại ra y như cũ).

## 7. Ca biên (hành vi phải đúng như sau)

| Ca | Hành vi |
|---|---|
| Chart mới, chưa có nhật ký | Không vòng nào cho tới khi đủ 1380 phút nến có số liệu (M1 1380 nến, M5 276, M15 92, M30 46, H1 23, H4 6, D1 1) |
| Nhật ký ngắt quãng | Đếm theo nến có số liệu, khoảng trống không tính; ngưỡng dùng tiếp trạng thái cũ |
| Nến không có ô `mot > 0` (lịch sử ngoài nhật ký) | Không xét, không nộp, không đổi trạng thái |
| Đủ phút nhưng số mẫu < K (nến rất ít ô) | Chưa có ngưỡng |
| Ngày vắng | Được phép 0 vòng |
| Ngày cá mập đánh dồn | Không chặn số vòng (đo: vàng 20/11 có 9 vòng, NQ 30/10 có 22) |
| Lệnh bằng đúng ngưỡng | Không nổ |
| `mot` > 4095 | Chỉ số 4095; so sánh bằng giá trị thật |
| `m <= 0` | Như `m = 1` |
| Đổi khung / đổi tham số / feed nạp lại | `ResetState` dựng lại `_btWhale` rỗng rồi nạp lại từ nến đầu |
| Nạp nguội so với nạp tăng dần | Giống hệt (`Golden.dll inccheck`) |
| Tắt "Big Trade · Bật" | Không vẽ; vẫn nộp nền và vẫn ghi nhật ký như hiện nay |

## 8. Ví dụ cho unit test (file mới `tests/BigTradeWhaleTests.cs`, nối vào `tests/Program.cs`)

Mọi ví dụ đã chạy trên `bw2_ref.Whale`. "Nến [a, b]" = một nến có các ô lệnh đơn a, b (tick tùy ý, khác nhau).

1. **Số nến hàng đợi:** `WindowBars` với m = 1, 5, 15, 30, 60, 240, 1440, 0 → 6900, 1380, 460, 230, 115, 29, 5, 6900.
2. **Khởi động (m = 60):** nộp 22 nến [10] → `TryThreshold` false. Nộp nến thứ 23 → true, K = 8, ngưỡng 10. Ô 10 không nổ, ô 11 nổ.
3. **Hạng theo thời gian (m = 30):** nộp 45 nến [1], [2], …, [45] → false. Nộp [46] → ngưỡng **39** (K = 8). Nộp thêm 23 nến [100] → 69 nến, 2070 phút, K = 12, ngưỡng **100**; ô 100 không nổ, ô 101 nổ.
4. **Làm tròn K (m = 15):** số nến 92, 93, 95, 98, 100 → K = 8, 8, 8, 9, 9.
5. **Chưa đủ mẫu (m = 1440):** nộp một nến [5, 6, 7] → đủ phút (1440) nhưng K = 8 > 3 mẫu → false. Nộp thêm một nến 20 ô giá trị 1 → K = 17, ngưỡng **1**.
6. **Trượt cửa sổ (m = 1440, n = 5):** nộp 5 nến, mỗi nến 10 ô giá trị 200 → K = 42, ngưỡng 200. Nộp thêm 4 nến, mỗi nến 10 ô giá trị 20 → `Count` = 5, ngưỡng **20**. Nộp nến thứ 5 như vậy → ngưỡng 20, `Samples` = 50.
7. **m = 240:** 5 nến [50, 40] → false (1200 phút). Nến thứ 6 → K = 8, ngưỡng **40**.
8. **Dồn ô cuối:** m = 1440, một nến 8 ô giá trị 5000 → ngưỡng 4095; ô 5000 nổ (`Select` strict với ngưỡng 4095).
9. **Nến không có số liệu:** `AddClosedBar` với danh sách rỗng, null, hoặc toàn `mot = 0` → `Count` không đổi.
10. **Gộp:** ô (tick, lệnh) = (100, 60), (101, 80), (103, 60), (110, 45), (111, 44), ngưỡng 44, g = 2 → giữ tick 101 và 110. Ngưỡng 60 → chỉ giữ 101.
11. **g:** dưới 5 nến → 2; 5 nến biên độ 40 → `rhu(40 / 8)` = 5; biên độ 0 → 2.
12. **Không nhìn trước:** chạy một dãy 200 nến ngẫu nhiên có hạt giống cố định (m = 60), ghi ngưỡng từng nến; đổi nội dung nến 150–199 rồi chạy lại → ngưỡng của nến 0–150 không đổi.

## 9. Số chuẩn Python để so C#

`T` = `C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad`, `G` = `dotnet quantower-orderflow-indicator/perf/Golden/bin/Release/net10.0-windows/Golden.dll`, `R` = `quantower-orderflow-indicator/research`. Dùng bản nhật ký cố định trong `T` (không dùng nhật ký sống đang ghi thêm). Nếu file trong `T` đã mất: dựng `tf/*.csv` bằng `R/nq_calib_2026-11-24/tf_csv.py`, `btlog_*.csv` bằng `R/adaptive_2026-11-24/bt_cs_log.py`; khi đó số vòng có thể khác bảng nếu nhật ký đã dài hơn — chạy lại Python để lấy số mới, không sửa C# cho khớp bảng.

Lệnh mẫu (NQ M1):
```
python $R/bigtrade_whale_2026-11-25/bw2_ref.py $T/tf/fp_NQ_m1.csv 1 0.25 --btlog $T/btlog_NQ_M1.csv --marks $T/bw2_marks_NQ_M1.csv
$G stophunt --tick 0.25 --symbol NQZ26 --minutes 1 --levels $T/tf/fp_NQ_m1.csv --work $T/w_bw --marks $T/cs_bw_NQ_M1.csv --zeromot --btlog $T/btlog_NQ_M1.csv
python $R/stat_anomaly_2026-11-24/sa4_cmp.py $T/bw2_marks_NQ_M1.csv $T/cs_bw_NQ_M1.csv 0.25 --kinds bt
```
Vàng: `--tick 0.1`, không `--symbol`. Chạy Golden **hai lần** mỗi dòng: mặc định và thêm `--set ThresholdMode=1`; cả hai phải ra cùng tập vòng Big Trade.

| Mã, khung | File footprint · nhật ký | Số nến | **Vòng Big Trade** | Nến có số liệu: có ngưỡng / chưa có | Ngưỡng nhỏ nhất / giữa / lớn nhất | Vòng nhỏ nhất | sha1 nhật ký · sha1 file dấu Python |
|---|---|---|---|---|---|---|---|
| NQ M1 | `fp_NQ_m1.csv` · `btlog_NQ_M1.csv` | 71.047 | **56** | 6.960 / 1.380 | 67 / 75 / 82 | 71 | `ec1fe48e…88ea8` · `b917fc1e…6ea3` |
| NQ M15 | `fp_NQ_m15.csv` · `btlog_NQ_M15.csv` | 4.737 | **50** | 464 / 92 | 68 / 75 / 81 | 71 | `c9152218…be43f` · `b2de2b2f…3215` |
| GC M5 | `fp_GC_m5.csv` · `btlog_GC_M5.csv` | 17.623 | **111** | 4.318 / 276 | 34 / 50 / 76 | 35 | `540f6c2e…1beb3` · `9461d5f8…a03c` |
| GC M30 | `fp_GC_m30.csv` · `btlog_GC_M30.csv` | 2.938 | **105** | 720 / 46 | 34 / 50 / 76 | 36 | `9f90c459…5b38` · `a2b25e2b…aee2` |

sha1 đầy đủ: nhật ký `ec1fe48e1155628179e67adec3399162b5988ea8`, `c91522189a4c0ce68fa2861f52f9814c0fabe43f`, `540f6c2ef0c6674bc127c67d84bb8455291dbeb3`, `9f90c4598ccdcf456799eca1175ac7bd4e605b38`; file dấu `b917fc1e40460dca5b54050e638bcf7adffb6ea3`, `b2de2b2f19ce464a7e9e95e82a973bb6fb4e3215`, `9461d5f814f06c4dd9d1dfafc70f90f89974a03c`, `a2b25e2b59f9e99c75e165948f75f4e7aa70aee2`.

Trước khi sửa (luật cũ, cùng dữ liệu, `research/stat_anomaly_2026-11-24/SPEC.md` mục 9): chế độ thống kê 3.330 / 864 / 1.913 / 788 vòng. Dò lệch: thêm `--trace <file>` cho `bw2_ref.py` để in ngưỡng và số nến hàng đợi của từng nến có số liệu.

## 10. Điều kiện xong (Opus báo từng dòng kèm số)

Thứ tự: **chụp "trước" → sửa → test → build.**

0. **Trước khi sửa code**, chạy `$G stophunt … --marks` trên 4 dòng mục 9, mỗi dòng hai chế độ (mặc định và `--set ThresholdMode=1`), lưu 8 file dấu "trước" và dòng thống kê stop hunt in ra.
1. `dotnet run --project quantower-orderflow-indicator/tests`: mọi test đạt, gồm 12 ví dụ mục 8.
2. Sau khi sửa: 8 lần chạy Golden mục 9 — vòng Big Trade **trùng từng dấu** với `bw2_ref.py` (`sa4_cmp.py … --kinds bt`: 0 lệch), và hai chế độ cho cùng tập vòng.
3. **Chấm không đổi:** 8 file dấu "sau" so với "trước" bằng `sa4_cmp.py <trước> <sau> <tick> --kinds dotS,dotB` → 0 lệch; số dấu `exhT` / `exhB` bằng nhau.
4. **Stop hunt:** báo số stop hunt và bóng tím trước / sau của 8 lần chạy. Stop hunt đọc mọi bóng `CellBig` của nến quét, gồm vòng Big Trade (`OrderFlowBubbles.cs` quanh dòng 1427), nên **được phép đổi** trên nến có nhật ký; không sửa `StopHuntLogic`. Chỉ báo số, không diễn giải thành tốt hơn hay xấu hơn.
5. `$G inccheck` (có `--btlog`) trên NQ M1, NQ M15, GC M5, mỗi cái hai chế độ: KHOP.
6. `$G golden`: so với `perf/golden-expected.txt`. Dấu vân tay đổi nên mã băm `cache` sẽ đổi; `state` chỉ được đổi do vòng Big Trade. Báo dòng nào đổi; sau khi các bước 2–5 đạt mới `--write-expected`, ghi rõ trong báo cáo.
7. `bash quantower-orderflow-indicator/perf/build-dll.sh` rồi `dotnet run --project quantower-orderflow-indicator/tests-dll`: đạt, 23 ô.
8. `$G bench` trước và sau: ghi thời gian nạp nguội NQ M1 71.047 nến.
9. Không commit, không push, không chép DLL (agent chính làm).

## 11. Đoạn cho README của indicator (viết cho người học)

### Big Trade = lệnh cá mập

**Vòng mờ nổ khi nào:** khi **một lệnh đơn chủ động** lớn hơn hẳn nhóm 8 lệnh lớn nhất mỗi ngày, tính trên 5 ngày gần nhất của chính mã đó. Không còn ô chỉnh dày / thưa; hai chế độ ngưỡng dùng chung luật này.

**Ngưỡng thường gặp (hợp đồng, đo trên nhật ký của bạn):**

| | Phiên Á | Phiên Âu | Phiên Mỹ | Vòng nhỏ nhất từng vẽ |
|---|---|---|---|---|
| Vàng GC, tuần sôi động (1–11/9) | 67 | 57 | 67 | 61 |
| Vàng GC, tuần yên (14–22/9) | 44 | 42 | 39 | 36 |
| Vàng GC, tháng 11 | 43 | 42 | 45 | 40 |
| NQ (27/10–2/11) | 73–75 | 72–75 | 72–78 | 71 |

Ngưỡng gần như bằng nhau cả ngày: phiên vắng không được hạ chuẩn.

**Mật độ trước và sau (vòng mỗi ngày, trung vị):**

| | Luật cũ "Không theo CORVEN" | Luật cũ "Theo CORVEN" | **Luật mới** (Á / Âu / Mỹ) |
|---|---|---|---|
| Vàng M1, 1–11/9 | 233 (ngưỡng 7–9) | 664 | **6,5** (1 / 3,5 / 1) |
| Vàng M1, 14–22/9 | 226 | 702 | **6** (1 / 1 / 1) |
| Vàng M1, tháng 11 (ngày ghi không đủ) | 83 | 290 | **5** (1 / 3 / 1) |
| NQ M1, 27–28/10 | 493 (ngưỡng 5–10) | 825 | **6** (0,5 / 1 / 4,5) |
| NQ M1, 29/10–2/11 | 609 | 906 | **14** (3 / 1 / 9) |

Cùng một lệnh cá mập hiện ở mọi khung: M1 và M5 của vàng trùng 92–98% số vòng, M1 và M15 của NQ trùng 89–92%.

**Cần biết:**
- Ngày yên có thể không có vòng nào. Ngày cá mập đánh dồn có thể 15–22 vòng (vàng 20/11: 9 vòng, 7 vòng trong 30 phút; NQ 30/10: 22 vòng).
- **Chart hoặc khung mới chưa có nhật ký lệnh đơn sẽ chưa có vòng** cho tới khi chạy sống đủ 23 giờ nến (nhật ký ghi riêng từng mã, từng khung). Đang đủ: vàng M1, M5; NQ M1, M15.
- Ngưỡng trôi theo thị trường: tuần yên, vàng chỉ cần khoảng 36–40 hợp đồng là nổ.
- Lệnh bằng đúng ngưỡng không nổ (ngưỡng 50 thì lệnh 50 không có vòng).
- Lệnh lớn nhất của một phiên vắng có thể không nổ nếu nó nhỏ hơn chuẩn cả tuần (NQ 28/10: phiên Á 52, phiên Âu 50, ngưỡng 70–75).
- NQ mới đo trên 6 ngày đủ; MGC và MNQ chưa có nhật ký. Sẽ đo lại khi nhật ký dài hơn.
- Đây là cách **hiển thị** lệnh lớn, chưa phải lợi thế giao dịch đã kiểm định.
