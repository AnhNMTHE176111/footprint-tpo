# SPEC — chế độ ngưỡng "Không theo CORVEN (thống kê)" cho OrderFlowBubbles (C#)

> Fable viết 2026-11-25 sau ba vòng đo (`PLAN.md`, `r1_review.md`, `r2_review.md`, `r3_review.md`). Opus viết code và test theo đúng tài liệu này; chỗ nào chưa nói thì hỏi lại, không tự đoán.
> Bản Python tham chiếu từng nến: **`sa3_ref.py`** (mặc định của nó chính là cấu hình chốt ở đây). C# phải ra **đúng từng dấu** như `sa3_ref.py`.
> Đây là **định nghĩa hiển thị**: bóng = volume lớn bất thường so với chính quá khứ của nó. **Không phải lợi thế giao dịch đã kiểm định**; không viết như lợi thế ở bất cứ đâu (tên ô, tooltip, README). Không bước nào dùng giá chạy sau, không bước nào dùng chart CORVEN.

## 0. Tóm tắt

| | Chấm Bid/Ask | Big Trade |
|---|---|---|
| Giá trị xét | Bid và Ask của từng ô giá, xét riêng từng bên | lệnh đơn lớn nhất của ô giá |
| Tập tham chiếu | Bid và Ask > 0 của **cùng khung giờ trong ngày (giờ Chicago)**, 5 ngày giao dịch trước, gộp thêm hai khung giờ liền kề | lệnh đơn > 0 của 240 phút nến có số liệu gần nhất |
| Khi chưa đủ | dùng 120 phút nến đóng gần nhất; vẫn chưa đủ thì không vẽ | không vẽ |
| Nổ khi | giá trị **lớn hơn hẳn** ngưỡng; ngưỡng đặt sao cho tập tham chiếu có nhiều nhất 2% (chọn được 1% / 0,5%) số mẫu vượt | như bên, mức 1% cố định |
| Gộp ô sát nhau | chọn tham lam trong ±w tick, `w = max(4, làm tròn(biên độ TB / 6))` | chọn tham lam trong ±g tick, `g = max(2, làm tròn(biên độ TB / 8))` |
| Không có | sàn, luật che xanh gần đỏ, bộ số theo mã | sàn, giới hạn số vòng mỗi nến |

Mặc định của indicator **vẫn là "Theo CORVEN"** (mục 6). Chế độ cũ không đổi một dấu nào; `Golden.dll golden` phải giữ nguyên, không `--write-expected`.

## 1. Quy ước chung

1. **Làm tròn:** `rhu(x) = (int)Math.Floor(x + 0.5)` (`BaselineWindow.RoundHalfUp`). Không dùng `Math.Round`.
2. **Phút một nến** `m`: số nguyên ≥ 1. Chế độ mới chỉ chạy khi `BarMinutesNow ≥ 1` và là số nguyên (lệch dưới 1e-9); ngược lại indicator chạy **chế độ theo CORVEN** như thể ô chọn đang ở "Theo CORVEN" (chưa đo thì không vẽ như đã đo).
3. **Số nến nền** `N = BaselineWindow.BarsFor(m)` = `min(20, max(5, rhu(120 / m)))`, **luôn** theo công thức này trong chế độ mới, không phụ thuộc ô "Nền tự co theo khung".
4. **Giờ nến** = `bar.TimeLeft` (UTC).
5. **Giờ Chicago theo luật cố định** (không dùng `TimeZoneInfo`): từ **08:00 UTC chủ nhật thứ hai của tháng 3** tới trước **07:00 UTC chủ nhật đầu tiên của tháng 11** lệch −5 giờ; ngoài khoảng đó −6 giờ. `giờ Chicago = UTC + lệch`.
6. **Ngày giao dịch** của một nến = phần ngày của `(giờ Chicago + 7 giờ)` (ngày bắt đầu 17:00 Chicago). Lưu thành số nguyên (`Date.Ticks / TimeSpan.TicksPerDay`).
7. **Khung giờ:** `W = max(30, m)` phút; `số khung = ceil(1440 / W)`; `khung = (giờ Chicago × 60 + phút Chicago) / W` (chia nguyên).
8. **Khung lân cận** của khung `s`: `(s − 1 + số khung) % số khung` rồi `(s + 1) % số khung`, bỏ cái nào trùng `s` hoặc trùng nhau. Ví dụ: (5, 48) → 4, 6; (0, 48) → 47, 1; (0, 2) → 1; (0, 1) → không có.
9. **Mảng đếm:** chỉ số = `min((int)Math.Floor(v), 4095)` — chấm: chỉ nộp khi `Floor(v) > 0`; Big Trade: mọi lệnh đơn `v > 0` đều nộp (kể cả 0 < v < 1, rơi vào ô 0 — khớp `sa3_ref.py`; lệnh đơn thật là số nguyên nên không ảnh hưởng). So sánh "lớn hơn hẳn ngưỡng" dùng `Math.Floor(v)` thật, không dùng giá trị đã chặn.
10. **Hàm ngưỡng** `Ngưỡng(mảng đếm, n, p)` với `n` = tổng số mẫu, `p` = mức hiếm tính bằng **phần vạn** (200 = 2%):
    - nếu `n × p < 50000` (tức `n × tỉ lệ < 5`) → **chưa có ngưỡng**;
    - `K = (p × n) / 10000` (chia nguyên, dùng `long`);
    - ngưỡng = **giá trị lớn thứ K + 1**: quét mảng đếm từ 4095 xuống, cộng dồn, trả chỉ số đầu tiên có tổng dồn ≥ K + 1.
    - Ô nổ khi giá trị **> ngưỡng**. Như vậy trong tập tham chiếu có nhiều nhất K mẫu vượt; giá trị bằng nhau không gây vượt mức.

## 2. Chấm Bid/Ask

Tham số (tên thuộc tính C# ở mục 6): `K_ngày = 5`, `lân cận = bật`, `ngày tối thiểu = 2`, `T_dự phòng = 120`, `p = 200` (chọn được 100, 50).

**Trạng thái giữ trong C#** (lớp `StatDots`, một đối tượng cho cả chart):
- `khung → danh sách (ngày giao dịch, mảng đếm)` theo thứ tự thời gian. Mỗi phần tử là tổng các giá trị bên > 0 của mọi nến đã đóng thuộc (ngày, khung) đó. Mỗi khung chỉ cần giữ `K_ngày + 1` phần tử cuối. Mảng đếm của một phần tử nên cắt ngắn tới giá trị lớn nhất + 1 để tiết kiệm bộ nhớ.
- Dự phòng: hàng đợi `n_dp = max(5, rhu(T_dự phòng / m))` nến đóng gần nhất (mỗi nến = mảng giá trị bên > 0) + một mảng đếm 4096 ô cộng vào / trừ ra + tổng số mẫu.
- Biên độ: hàng đợi `N` số (biên độ theo tick của nến đóng = tick cao nhất − tick thấp nhất trong các ô volume > 0, đúng `CellBigLogic.BarRangeTicks`).

**Ngưỡng của một nến** (nến đóng hay nến đang chạy đều tính như nhau, chỉ từ nến đã đóng trước):
1. Tính (ngày D, khung s) của nến.
2. *Ngưỡng chính:* lấy các phần tử của khung s có **ngày < D**, giữ `K_ngày` phần tử cuối. Nếu có ít hơn `ngày tối thiểu` phần tử → không có ngưỡng chính. Ngược lại cộng mảng đếm của chúng; nếu bật lân cận, cộng thêm với từng khung lân cận các phần tử ngày < D, `K_ngày` phần tử cuối (khung lân cận không cần đủ ngày tối thiểu, không có cũng được). `Ngưỡng(tổng, n, p)`.
3. *Dự phòng* (chỉ khi bước 2 không ra ngưỡng): `Ngưỡng(mảng đếm dự phòng, số mẫu dự phòng, p)`.
4. Cả hai không có → nến này **không có chấm**.

Ngưỡng chính chỉ phụ thuộc (D, s) và các ngày trước D nên được phép nhớ lại theo khóa (D, s); ngưỡng dự phòng đổi sau mỗi lần nộp nến đóng nên phải tính lại (hoặc nhớ và xóa nhớ khi nộp).

**Chọn chấm** (hàm thuần, riêng từng bên; bên Bid ra chấm đỏ `Side = −1`, bên Ask ra chấm xanh `Side = +1`):
1. `w = 4`; nếu hàng đợi biên độ có ≥ 5 số và trung bình > 0 thì `w = max(4, rhu(trung bình / 6))`.
2. Ứng viên = mọi ô có `Math.Floor(giá trị bên) > ngưỡng`.
3. Ô "Nổ ở mọi mức giá" **tắt** (mặc định): chọn tham lam = `CellBigLogic.MergeAdjacent(ứng viên, w)` (giá trị giảm dần, bằng nhau thì tick thấp trước, giữ ô nếu chưa có ô đã giữ nào cách ≤ w tick). **Bật**: giữ mọi ứng viên.
4. Kết quả trả về: chấm xanh (tick tăng dần) rồi chấm đỏ (tick tăng dần), như `CellBigLogic.Evaluate`. `CellMark.Threshold = ngưỡng`, `Mult = 0`, `SizeFrac = DotSizeFrac`.
5. Không áp luật che, không áp sàn, không dùng `LocalMax`.

**Nộp nến đóng** (đúng một lần mỗi nến, trong `AddToBaseline`, cùng chỗ `_cellBigBase.Add`, tức chỉ khi `BarStats` trả true = nến có ít nhất một ô volume > 0):
1. Giá trị = mọi `Math.Floor(Bid) > 0` và mọi `Math.Floor(Ask) > 0` của mọi ô (Bid và Ask gộp chung).
2. Cộng vào phần tử (D, s): nếu phần tử cuối của khung s có ngày = D thì cộng dồn, ngược lại thêm phần tử mới (kể cả khi nến không có giá trị nào > 0: vẫn thêm phần tử rỗng) rồi cắt còn `K_ngày + 1` phần tử.
3. Đẩy vào hàng đợi dự phòng, nến cũ nhất rời hàng đợi thì trừ khỏi mảng đếm.
4. Đẩy biên độ vào hàng đợi biên độ, cắt còn `N`.

Nến không có ô nào volume > 0: **bỏ hẳn** (không xét, không nộp gì).

## 3. Big Trade

Tham số: `T = 240` phút, `p = 100` (1%, cố định).

**Trạng thái** (lớp `StatBigTrade`): hàng đợi `n = max(5, rhu(T / m))` **nến có số liệu lệnh đơn** gần nhất (mỗi nến = mảng lệnh đơn > 0 của các ô) + mảng đếm 4096 ô + tổng số mẫu; hàng đợi biên độ `N` số (tick cao nhất − thấp nhất trong các ô có lệnh đơn > 0).

**Xét một nến có số liệu** (danh sách ô lấy như hiện nay: từ feed, nếu không có thì từ nhật ký `BigTradeLog.CellsOf`):
1. `Ngưỡng(mảng đếm, số mẫu, 100)`. Chưa có (dưới 500 mẫu) → **không vẽ vòng nào** (không quay về ngưỡng cố định 10).
2. `g = 2`; nếu hàng đợi biên độ có ≥ 5 số và trung bình > 0 thì `g = max(2, rhu(trung bình / 8))`.
3. Chọn = các ô có `lệnh đơn > ngưỡng` (**lớn hơn hẳn**), duyệt lệnh đơn giảm dần (bằng nhau thì tick thấp trước, rồi chỉ số), bỏ ô cách ô đã giữ ≤ g tick; **không giới hạn** số vòng. Thêm tham số `strict` cho `BigTradeAdaptive.Select` (mặc định false = `>=` như cũ) hoặc viết hàm riêng; chế độ cũ không đổi.
4. Cỡ vòng: `BigTradeLogic.SizeFrac(lệnh đơn, max(1, ngưỡng))`.

**Nộp nến đóng** (trong `AddToBaseline`, cùng chỗ `_btAdapt.AddClosedBar`): nến không có ô nào lệnh đơn > 0 → không nộp, không tính là một nến của hàng đợi. Ngược lại nộp mọi lệnh đơn > 0 và biên độ.

## 4. Lớp C# mới (file mới `StatThreshold.cs`, thuần, không phụ thuộc Quantower; nhớ thêm vào project test và project Golden nếu chúng liệt kê file nguồn)

```csharp
public static class StatRank {
    public const int Cap = 4095;
    public static int Threshold(int[] hist, long n, int pbp);      // -1 = chưa có ngưỡng
}
public static class StatClock {
    public static int ChicagoOffsetHours(DateTime utc);            // -5 hoặc -6
    public static (int day, int slot, int slots) DaySlot(DateTime utc, int minutes);
    public static List<int> Neighbors(int slot, int slots);        // không gồm chính nó
}
public sealed class StatDots {
    public StatDots(int minutes, int pbp, int days = 5, bool neighbors = true, int minDays = 2, int fallbackMinutes = 120);
    public bool TryThreshold(DateTime barUtc, out int thr, out bool fallback);
    public int Window();                                           // w
    public List<CellMark> Evaluate(DateTime barUtc, IReadOnlyList<CellLevel> levels, bool allLevels, out int thr, out bool fallback);
    public static List<CellMark> Select(IReadOnlyList<CellLevel> levels, int thr, int w, bool allLevels);
    public void AddClosedBar(DateTime barUtc, IReadOnlyList<CellLevel> levels);
}
public sealed class StatBigTrade {
    public StatBigTrade(int minutes, int pbp = 100, int windowMinutes = 240);
    public bool TryThreshold(out int thr);
    public int MergeTicks();                                       // g
    public void AddClosedBar(IReadOnlyList<(long tick, double mot)> cells);
}
```

Chi phí: mỗi nến đóng cộng / trừ vài chục đến vài trăm số; ngưỡng chính tính một lần mỗi (ngày, khung) (cộng tối đa 15 mảng đếm); ngưỡng dự phòng và Big Trade quét 4096 ô. Nạp 90 ngày M1 không được chậm thấy rõ so với hiện tại (đo bằng `Golden.dll bench` trước và sau, ghi số).

## 5. Ghép vào `OrderFlowBubbles.cs`

- `StatModeNow` = `ThresholdMode == 1` và `m` hợp lệ (mục 1.2).
- `InitBaselines()`: khi `StatModeNow` thì tạo `_statDots`, `_statBt`; ngược lại để `null` (chế độ cũ không tốn gì thêm).
- `BaseKey()`: nối thêm `"|stat:" + StatKey()` **chỉ khi** `StatModeNow`, để đổi khung hoặc đổi tham số thì `ResetState()`. `StatKey()` = `m/StatRarePbp/StatDotDays/StatDotNeighbors/StatDotMinDays/StatDotFallbackMinutes/StatBtMinutes/StatBtRarePbp` (văn hóa bất biến).
- `ComputeSettingsFingerprint()`: nối thêm `"|stat-v1:" + StatKey()` **chỉ khi** `StatModeNow`. Tắt chế độ mới thì dấu vân tay y như hiện nay.
- `ComputeBar`, khối chấm: khi `StatModeNow` thì thay lời gọi `CellBigLogic.Evaluate(...)` bằng `_statDots.Evaluate(bar.TimeLeft, cellLevels, CellDotAllLevels, ...)` (vẫn tôn trọng `CellBigEnabled` và `CellDotEnabled`; `UseFixedThreshold` bị bỏ qua). Phần sau đó (dựng bóng, `CellBigMergeTicks`, `CellBigTopN`, thứ tự vẽ) giữ nguyên.
- `ComputeBar`, khối Big Trade: khi `StatModeNow` thì dùng `_statBt` theo mục 3; không có ngưỡng → không vẽ.
- `AddToBaseline`: nộp theo mục 2 và 3. Các nền cũ vẫn nộp như hiện nay (kiệt sức và stop hunt còn dùng).
- Nến khôi phục từ bản niêm phong vẫn đi qua `AddToBaseline`, nên nền không bị thiếu.
- Tooltip chấm: `Sell - 53 Bid (Ask 39) | ngưỡng > 31 (2% lớn nhất cùng khung giờ, 5 ngày trước)`; khi dùng dự phòng: `... | ngưỡng > 31 (2% lớn nhất 120 phút gần nhất, chưa đủ ngày)`. Bên buy: `Buy - 40 Ask (Bid 12) | ...`. Số phần trăm in từ `StatRarePbp / 100` với định dạng `0.#`.
- Tooltip Big Trade: `Big trade: 1 lệnh 25 hợp đồng (ngưỡng > 12, 1% lớn nhất 240 phút gần nhất) | ô 3 Bid 30 Ask`.

## 6. Ô cài đặt

| Thuộc tính | Ô hiện cho người dùng | Mặc định |
|---|---|---|
| `int ThresholdMode` | `[InputParameter("Chế độ ngưỡng (chấm Bid/Ask + Big Trade)", 22, variants: new object[] { "Theo CORVEN", 0, "Không theo CORVEN (thống kê)", 1 })]` | **0** |
| `int StatRarePbp` | `[InputParameter("Không theo CORVEN · Mức hiếm của chấm", 23, variants: new object[] { "2% lớn nhất (đã đo: không sót)", 200, "1% lớn nhất (thưa hơn, có sót)", 100, "0,5% lớn nhất (rất thưa, sót nhiều)", 50 })]` | **200** |
| `int StatDotDays` | không hiện | 5 |
| `bool StatDotNeighbors` | không hiện | true |
| `int StatDotMinDays` | không hiện | 2 |
| `int StatDotFallbackMinutes` | không hiện | 120 |
| `int StatBtMinutes` | không hiện | 240 |
| `int StatBtRarePbp` | không hiện | 100 |

- **Vì sao mặc định "Theo CORVEN":** bản niêm phong và chuẩn golden cũ giữ nguyên; ở M1 chế độ mới thưa hơn khoảng 3 lần so với chấm đang thấy nên phải do người học tự bật; Big Trade NQ mới có 6 phiên nhật ký.
- Ô "Mức hiếm" chỉ hiện khi chế độ mới bật: `SettingItemRelationVisibility(nameof(ThresholdMode), new SelectItem("", 1))`. Nếu cách này không biên dịch hoặc không kiểm được ngoài nền tảng thì bỏ quan hệ ẩn / hiện (ô luôn hiện); không được vì thế mà đổi ô chọn thành ô đánh dấu.
- **Quan hệ với ô cũ khi chế độ mới bật:**
  - Vẫn có tác dụng: "Ô Bid/Ask lớn · Bật", "Chấm Bid/Ask nhỏ · Bật", "Big Trade · Bật", **"Nổ ở mọi mức giá"** (vẽ mọi ô vượt ngưỡng, không gộp).
  - Bị bỏ qua: "Dùng sàn tối thiểu", "Sàn tối thiểu", "Tự co dãn theo khung", "Bộ số", "Mã NQ/MNQ tự dùng bộ số Nasdaq", "Big Trade · Ngưỡng tự thích nghi", "Mật độ đích", "Sàn", "Tối đa vòng mỗi nến". Không đổi tên các ô này; ghi điều này vào README.
  - "Nền tự co theo khung" vẫn điều khiển kiệt sức; chế độ mới không đọc nó.
- `tests-dll`: số `InputParameter` 25 → **27**; thêm kiểm mặc định `ThresholdMode = 0`, `StatRarePbp = 200`, số lựa chọn 2 và 3.

## 7. Ca biên (hành vi phải đúng như sau)

| Ca | Hành vi |
|---|---|
| Nến đầu chart | Chưa đủ 250 mẫu (mức 2%) trong 120 phút nến đóng → không chấm. Thực đo: 1–10 nến đầu |
| Hai ngày đầu của chart | Khung giờ chưa có 2 ngày trước → ngưỡng dự phòng 120 phút. Từ ngày giao dịch thứ 6, chấm không còn phụ thuộc lượng lịch sử đã nạp |
| Sau nghỉ cuối tuần, ngày lễ, khung giờ thưa | Khung giờ lấy 5 **lần xuất hiện** gần nhất trước hôm nay, không cần liền ngày. Ngày giao dịch tính theo 17:00 Chicago nên tối chủ nhật thuộc ngày thứ hai |
| Đổi giờ mùa | Khung giờ theo giờ Chicago nên giờ mở cửa Mỹ giữ nguyên khung. Tuần châu Âu đã đổi giờ mà Mỹ chưa đổi: phiên Âu lệch một giờ, khung lân cận đỡ một phần |
| Nến đang chạy | Dùng ngưỡng và w của nến đã đóng; không nộp gì. Khi nến đóng, ngưỡng không đổi |
| Nến rỗng (không ô nào volume > 0) | Bỏ hẳn |
| Nến có volume nhưng mọi Bid = Ask = 0 | Vẫn là một nến: tính vào hàng đợi dự phòng với 0 mẫu, đánh dấu (ngày, khung) có xuất hiện, nộp biên độ |
| Giá trị > 4095 | Dồn vào ô 4095 của mảng đếm; so sánh vẫn dùng giá trị thật. Dữ liệu đã đo lớn nhất 2.299 |
| Big Trade trên lịch sử không có lệnh đơn và không có nhật ký | Không có vòng (như hiện nay) |
| Big Trade khi mới mở chart sống | Chưa đủ 500 lệnh đơn trong cửa sổ → chưa có vòng |
| Khung không theo thời gian, số phút không nguyên hoặc < 1 | Chạy chế độ theo CORVEN |
| Đổi khung, đổi mức hiếm | `BaseKey` đổi → `ResetState()` → tính lại từ đầu |
| Nạp nguội so với nạp tăng dần | Phải giống hệt (`Golden.dll inccheck`) |

## 8. Ví dụ cho unit test (file mới `tests/StatThresholdTests.cs`, nối vào `tests/Program.cs`)

**8.1 Hàm ngưỡng**
- 250 mẫu là 1, 2, …, 250 (mỗi số một lần), p = 200 → K = 5 → ngưỡng **245**; đúng 5 giá trị (246…250) vượt.
- 249 mẫu, p = 200 → chưa có ngưỡng (−1).
- 240 mẫu giá trị 3 và 10 mẫu giá trị 9, p = 200 → K = 5, ngưỡng **9**; không mẫu nào vượt.
- 500 mẫu 1…500, p = 100 → K = 5 → ngưỡng **495**; 499 mẫu → −1.
- 1.000 mẫu 1…1000, p = 50 → K = 5 → ngưỡng **995**; 999 mẫu → −1.
- Giá trị 5000 nộp vào ô 4095; 250 mẫu gồm 244 số 1 và 6 số 5000, p = 200 → ngưỡng 4095; ô 5000 vượt, ô 4095 không vượt.

**8.2 Giờ Chicago, ngày, khung**
| Giờ UTC | m | Lệch | Ngày giao dịch | Khung / số khung |
|---|---|---|---|---|
| 2026-10-30 13:30 | 30 | −5 | 2026-10-30 | 17 / 48 |
| 2026-11-01 06:59 | 1 | −5 | 2026-11-01 | 3 / 48 |
| 2026-11-01 07:00 | 1 | −6 | 2026-11-01 | 2 / 48 |
| 2026-11-01 23:00 | 30 | −6 | **2026-11-02** | 34 / 48 |
| 2026-11-02 14:30 | 30 | −6 | 2026-11-02 | 17 / 48 |
| 2026-11-02 14:00 | 60 | −6 | 2026-11-02 | 8 / 24 |
| 2027-03-14 07:59 | 1 | −6 | 2027-03-14 | 3 / 48 |
| 2027-03-14 08:00 | 1 | −5 | 2027-03-14 | 6 / 48 |
| 2026-11-02 14:00 | 240 | −6 | 2026-11-02 | 2 / 6 |

Khung lân cận: (5, 48) → [4, 6]; (0, 48) → [47, 1]; (0, 2) → [1]; (1, 2) → [0]; (0, 1) → [].

**8.3 Chọn chấm** (một bên, w = 4)
- 12 ở tick 10 và 12 ở tick 11 → giữ tick **10**.
- 20 / 15 / 12 ở tick 0 / 3 / 6 → giữ tick **0 và 6**; bật "Nổ ở mọi mức giá" → cả ba.
- Ngưỡng 12, ô có giá trị đúng 12 → không phải ứng viên (phải lớn hơn hẳn).

**8.4 Chuỗi 4 nến M30, tick 0,1** (đã chạy `sa3_ref.py`, ra đúng như dưới; p = 200, mặc định)
| Nến (UTC) | Ô (tick: Bid / Ask) | Kết quả |
|---|---|---|
| 2026-11-02 14:30 | tick 10001…10125: Bid = 1…125, Ask = 0 | không chấm (chưa có ngưỡng: 0 ngày trước, dự phòng 0 mẫu) |
| 2026-11-03 14:30 | như nến trên | không chấm (1 ngày trước < 2; dự phòng 125 mẫu < 250) |
| 2026-11-04 14:30 | 20000: 124 / 0 · 20010: 123 / 0 · 20020: 0 / 125 · 20021: 0 / 124 · 20030: 0 / 124 | ngưỡng chính **123** (250 mẫu, K = 5; w = 4 vì mới 2 biên độ) → chấm đỏ tick **20000**; chấm xanh tick **20020, 20030** (20021 bị gộp). Bật "Nổ ở mọi mức giá": xanh thêm 20021 |
| 2026-11-05 14:30 (nến đang chạy) | 30000: 125 / 124 · 30010: 124 / 125 | ngưỡng chính **124** (255 mẫu, K = 5) → chấm đỏ tick **30000**, chấm xanh tick **30010** |

Kiểm thêm trên chuỗi này: gọi lại `Evaluate` cho nến 4 nhiều lần không đổi kết quả (nến đang chạy không nộp); nộp nến 3 hai lần là lỗi của người gọi, không cần chặn.

**8.5 Big Trade**
- Hàng đợi có đúng 500 lệnh đơn 1…500 (chia vào ≥ 5 nến) → ngưỡng **495**; ô lệnh đơn 496 nổ, 495 không nổ. 499 lệnh đơn → không vòng nào.
- M5: cửa sổ `max(5, rhu(240 / 5))` = 48 nến; nến thứ 49 nộp vào thì nến đầu rời hàng đợi (mảng đếm phải trừ đúng).
- Gộp: lệnh đơn 600 / 550 / 520 ở tick 0 / 2 / 5, ngưỡng 495, g = 2 → giữ tick 0 và 5.
- Nến không có lệnh đơn > 0 nộp vào: số nến và số mẫu của hàng đợi không đổi.

**8.6 Dấu vân tay và mặc định**
- `ThresholdMode = 0`: dấu vân tay y hệt bản hiện tại (so chuỗi với bản trước khi sửa).
- `ThresholdMode = 1`, `m = 5`: dấu vân tay kết thúc bằng `|stat-v1:5/200/5/True/2/120/240/100`. Đổi `StatRarePbp` thì dấu vân tay đổi.
- `ThresholdMode = 1`, `m = 0`: dấu vân tay và kết quả y hệt `ThresholdMode = 0`.

## 9. Số chuẩn Python để so C#

Đặt `T` = thư mục tạm `C:\Users\anhla\AppData\Local\Temp\claude\39bcbe610c8d657f\ce3fca11-3030-4b09-9b13-33a6dd7ee683\scratchpad`, `G` = `dotnet quantower-orderflow-indicator/perf/Golden/bin/Release/net10.0-windows/Golden.dll`. Nếu file trong `T` đã mất: dựng lại `tf/*.csv` bằng `research/nq_calib_2026-11-24/tf_csv.py`, file nạp 8 ngày và file dấu bằng `python sa3_numbers.py`. sha1 từng file ở `out_r3_chuan.csv`; số theo ngày ở `out_r3_chuan_ngay.csv`.

Lệnh C# (thay mã, khung, tick; NQ thêm `--symbol NQZ26`, tick 0,25; GC tick 0,1):
```
$G stophunt --tick 0.1 --minutes 5 --levels $T/tf/fp_GC_m5.csv --work $T/w_stat --zeromot --marks $T/cs_GC_m5_nen_moi.csv --set ThresholdMode=1
```
Lệnh Python tương ứng: `python sa3_ref.py $T/tf/fp_GC_m5.csv 5 0.1 --set bt=0 --marks $T/marks_r3_GC_m5_nen_moi.csv`.
Golden in `Dot N = do A + xanh B` và `Big C`; so A, B, C với bảng. Sau đó so **từng dấu**: viết `sa4_cmp.py <dấu Python> <dấu C#> <tick>` so hai tập (giờ nến, loại `dotS` / `dotB` / `bt`, `làm tròn(giá / tick)`), bỏ các loại dấu khác, in số dấu chỉ có ở một bên và 10 dấu lệch đầu tiên.

**Chấm đỏ (Bid) / chấm xanh (Ask):**

| Cấu hình | `--set` thêm cho C# | `--set` Python | GC M1 | GC M5 | GC M15 | GC H1 | NQ M1 | NQ M5 | NQ M15 | NQ H1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mặc định của chế độ mới | (không) | (không) | 16.767 / 16.505 | 8.332 / 8.260 | 4.342 / 4.425 | 1.646 / 1.662 | 30.421 / 30.168 | 11.988 / 11.808 | 5.512 / 5.494 | 1.727 / 1.720 |
| Mức 1% | `StatRarePbp=100` | `pbp=100` | 9.587 / 9.441 | 4.984 / 5.040 | 2.801 / 2.816 | 1.148 / 1.158 | 18.782 / 18.230 | 7.977 / 7.813 | 3.855 / 3.841 | 1.295 / 1.329 |
| Không lân cận | `StatDotNeighbors=false` | `lc=0` | 17.553 / 17.305 | 8.902 / 8.776 | 4.681 / 4.687 | 1.771 / 1.805 | 32.243 / 31.975 | 12.907 / 12.736 | 5.949 / 5.905 | 1.904 / 1.940 |

| Dòng riêng | File và `--set` | Chấm đỏ / xanh |
|---|---|---|
| Nổ ở mọi mức giá, GC M5 | `fp_GC_m5.csv`, C# `CellDotAllLevels=true`, Python `sel=all` | 15.050 / 14.965 |
| Nổ ở mọi mức giá, NQ M15 | `fp_NQ_m15.csv`, như trên | 21.087 / 20.699 |
| Nạp 8 ngày, GC M5 | `fp_GC_m5_nap8.csv` (2.041 nến, từ 2026-10-28 22:00 UTC) | 956 / 959 |
| Nạp 8 ngày, NQ M15 | `fp_NQ_m15_nap8.csv` (697 nến, từ 2026-11-12 23:00 UTC) | 1.097 / 1.028 |
| Mức 0,5% (chưa có số) | C# `StatRarePbp=50`, Python `pbp=50`, trên GC M5 và NQ M15 | Opus chạy `sa3_ref.py` lấy số rồi so |

Số nến ngưỡng chính / dự phòng / chưa có của cấu hình mặc định (để dò lệch): GC M5 17.071 / 548 / 4; NQ M15 4.553 / 183 / 1; GC M5 nạp 8 ngày 1.489 / 547 / 5.

**Big Trade** (thêm `--btlog $T/btlog_<mã>_M<khung>.csv --zeromot`; Python thêm `--btlog ... --zeromot`):

| Mã, khung | File footprint | Vòng Big Trade | Chấm đỏ / xanh cùng lần chạy | Nến Big Trade có ngưỡng / chưa có |
|---|---|---|---|---|
| NQ M1 | `fp_NQ_m1.csv` | **3.330** | 30.421 / 30.168 | 8.331 / 9 |
| NQ M15 | `fp_NQ_m15.csv` | **864** | 5.512 / 5.494 | 553 / 3 |
| GC M5 | `fp_GC_m5.csv` | **1.913** | 8.332 / 8.260 | 4.573 / 21 |
| GC M30 | `fp_GC_m30.csv` | **788** | 2.770 / 2.829 | 755 / 11 |

Các số ở bảng mặc định, hai dòng nạp 8 ngày, dòng 1% của NQ H1, dòng không lân cận của GC H1 và ba dòng Big Trade (GC M30, NQ M15, GC M5) đã được Fable cài lại độc lập và ra trùng (`rv3_chk1.py`).

## 10. Điều kiện xong (Opus báo từng dòng kèm số)

1. `dotnet run --project quantower-orderflow-indicator/tests`: mọi test đạt, gồm mục 8.
2. `Golden.dll stophunt` với `ThresholdMode=1`: 8 ô mặc định, 8 ô mức 1%, 8 ô không lân cận, 2 dòng nổ mọi mức giá, 2 dòng nạp 8 ngày, 2 dòng 0,5%, 4 dòng Big Trade — **trùng từng dấu** với `sa3_ref.py` (0 dấu lệch).
3. `Golden.dll inccheck --minutes <phút> --set ThresholdMode=1` (có và không có `--btlog`) trên GC M5, NQ M1, NQ M15: KHOP.
4. `Golden.dll golden`: không đổi so với `perf/golden-expected.txt` (không `--write-expected`).
5. `Golden.dll stophunt` **không** có `ThresholdMode=1` trên GC M5 và NQ M15: số dấu y như trước khi sửa.
6. `bash quantower-orderflow-indicator/perf/build-dll.sh` rồi `dotnet run --project quantower-orderflow-indicator/tests-dll`: đạt, 27 ô.
7. `Golden.dll bench` trước và sau: ghi thời gian; bật chế độ mới trên NQ M1 71.047 nến ghi thêm thời gian nạp nguội.
8. Không commit, không push (agent chính làm).

## 11. Đoạn cho README của indicator (viết cho người học)

> **Chế độ ngưỡng "Không theo CORVEN (thống kê)"** — bật ở ô "Chế độ ngưỡng". Mặc định vẫn là "Theo CORVEN".
> - **Chấm Bid/Ask:** một ô nổ chấm khi Bid (hoặc Ask) của nó lớn hơn 98% các ô **cùng khung giờ trong 5 ngày giao dịch trước**. 9 giờ tối giờ Việt Nam được so với 9 giờ tối các ngày trước, không so với phiên Á, nên ngưỡng tự co theo phiên và theo khung. Ví dụ đo được: NQ M1 ngưỡng khoảng 10 hợp đồng ở phiên Á, 31 ở phiên Mỹ; GC M5 khoảng 18 và 27.
> - **Big Trade:** một lệnh đơn nổ vòng khi nó lớn hơn 99% các lệnh đơn của 4 giờ gần nhất.
> - Các ô sát nhau gộp thành một bóng (giữ ô lớn nhất). Không có sàn, không có luật che chấm xanh gần chấm đỏ.
> - Ô "Mức hiếm": 2% (mặc định), 1%, 0,5%. Chỉ mức 2% qua được bài kiểm "không sót ô lớn nhất ngày".
> - Khi bật chế độ này, các ô sàn, bộ số, bộ Nasdaq, mật độ và giới hạn vòng Big Trade không còn tác dụng. Ô "Nổ ở mọi mức giá" vẫn dùng được.
> - **Giới hạn phải biết:** (1) đây là cách định nghĩa "ô lớn bất thường", **chưa hề đo là có lợi thế giao dịch**; (2) ở M1 thưa hơn chế độ theo CORVEN khoảng 3 lần (GC M1 khoảng 0,3–0,4 chấm mỗi nến); (3) chart cần nạp ít nhất 6 ngày giao dịch, hai ngày đầu của chart dùng ngưỡng tạm 120 phút; (4) NQ từ M15 trở lên: nửa giờ trước giờ mở cửa cổ phiếu Mỹ ngưỡng bị cao, dễ thiếu chấm; (5) Big Trade mới đo trên 16 phiên vàng và 6 phiên NQ, và cần chart chạy sống để có lệnh đơn; (6) chưa đo trên MGC, MNQ, khung trên H1.
