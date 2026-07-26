# PLAN — Bộ 2 indicator TPO cho Quantower: **Bias ngày real-time** + **Phiên & Vùng (M30)**

> Trạng thái: **CHỈ LÀ PLAN — chưa implement.** Đã research 4 mảng (mổ dữ liệu, lý thuyết bias, phiên+vùng, kiến trúc Quantower) + đã viết prototype Python **test trên dữ liệu thật** (`prototype_test.py`, chạy `python3 prototype_test.py`). Người implement ở phiên sau chỉ việc bám plan này. Mọi công thức/ngưỡng ở đây đã calibrate theo **GC vàng ~4050–4100, tick 0.1**.

---

## 0. Tóm tắt & phạm vi

Hai indicator C# Quantower, **đều add vào chart M30**, **vẽ đè lên khung giá chính** (main window):

| # | Tên (assembly) | Việc |
|---|---|---|
| 1 | **DailyTpoBias** | Dựng profile NGÀY đang phát triển + các ngày trước → chấm **bias ngày real-time** (mở cửa so vùng giá trị hôm qua, kiểu mở cửa, quan hệ giá trị, mở rộng IB một chiều, di trú POC, xác nhận delta), phân loại **kiểu ngày**, hiện **bảng chữ** + đường VAH/VAL/POC/IB. |
| 2 | **M30SessionZones** | Gộp profile 30′ thành khối **phiên Á/Âu/Mỹ**, sinh **tường thuật "phiên nào làm gì"** + **gợi ý bias phiên Mỹ**, và vẽ **các vùng cần quan tâm** (naked POC, cụm POC, biên vùng giá trị, hấp thụ, + **vùng target** cho lệnh đang chạy). |

Hai indicator **dùng chung `ProfileEngine`** (build profile, POC/VA, IB, zones). Build bằng bước **concat** (xem §2.6). Không đụng tới 4 indicator cũ (VSA, DMA, Ask/Bid, Bubbles).

**Nguyên tắc vàng đã rút ra:** file CSV export chỉ có **tổng theo NẾN** (không có volume-theo-giá) nên prototype offline phải xấp xỉ; nhưng **indicator LIVE đọc `bar.VolumeAnalysisData.PriceLevels` = có volume/bid/ask THẬT theo từng mức giá** → live chính xác hơn test offline. Đây là điểm mấu chốt khi đọc phần "giới hạn" (§6).

---

## 1. Nền dữ liệu & hằng số calibrate (từ agent mổ dữ liệu — số THẬT)

### 1.1 Giờ phiên (giờ VN, +07:00) — suy từ đường cong khối lượng thật
| Phiên | Khung giờ VN | Ghi chú |
|---|---|---|
| **Á (Asia)** | **05:00 – 12:30** | ramp 07:00, đỉnh 08:00–10:00, lull 10:30–12:00 |
| **Âu (Europe)** | **12:30 – 19:00** | London 14:00, cao đều 13:00–16:30 |
| **Mỹ (US)** | **19:00 – 04:00 (+1 ngày)** | bùng nổ 19:00, **đỉnh cả ngày 20:30–21:00** (COMEX pit 08:20 ET=19:20 VN; đóng pit 13:30 ET=00:30 VN) |

US mạnh nhất (đỉnh vol ~3.2× phiên Âu). **Ba mốc này là INPUT PARAMETER** (TimeSpan) để chỉnh sau, không hard-code.

### 1.2 Ngưỡng calibrate (dùng làm mặc định; live thì tự thích nghi bằng trung vị trượt 20 ngày)
- **RangeTypical ≈ 900 tick** (biên độ ngày, trung vị). p25 740 / p75 1120.
- **IBTypical ≈ 100 tick** (IB = 60′ đầu = 2 nến M30 đầu). IB chỉ ~**10.6%** biên độ ngày.
- **DeltaTypical ≈ 936** (|delta ngày| trung vị). Có **sell-skew nhẹ**: Delta/Volume trung vị −0.7%.
- **ATR_M30 ≈ 84 tick** (biên độ 30′ trung vị) — đơn vị đo cho mọi băng/merge vùng.
- POC dịch **trung vị 360 tick/ngày** (nhanh). Vùng giá trị 2 ngày liên tiếp chỉ chồng ~19% (giá trị di chuyển nhanh, nhưng 76% số ngày vẫn có chạm).

### 1.3 "Gotcha" bắt buộc phòng khi code (đã xác nhận trên dữ liệu)
1. **Thứ Hai mở cửa 07:00** (không phải 05:00) — dùng API session, đừng hard-code mốc mở.
2. **Cumulative delta (cột feed) reset lúc 00:00**, KHÔNG theo phiên → tự dựng CVD theo phiên từ delta từng nến.
3. **Hai lưới giá:** TPO ngày làm tròn **$1 (10 tick)**, M30 lưới **$0.1 (1 tick)** — đừng trộn.
4. **17 cột toàn 0** (Buy/Sell trades, Max/Min delta, **Max one trade Vol.**, Filt.*, Average buy/sell size…) → không xây tín hiệu trên chúng. **Max one trade Vol = 0 khắp nơi** → **không dò được iceberg/lệnh đơn lớn** từ feed này.
5. Nhiều phút không có nến (phút không khớp lệnh bị bỏ) → **đừng giả định đúng 30 nến/profile M30** hay index phút liên tục.
6. Profile đầu tiên của mỗi export thường **cụt** (thiếu dữ liệu) → bỏ/flag.
7. **Tên cột trùng** (`Volume`/`Delta`/`Trades`/`Open interest` xuất hiện 2 lần) — nếu có code đọc CSV: **truy cập theo index, không theo tên** (đọc `dict(zip(header,row))` sẽ nuốt mất bản trùng). *(Chỉ liên quan test offline; live đọc API nên không dính.)*

---

## 2. Kiến trúc Quantower (đã VERIFY bằng dịch ngược `TradingPlatform.BusinessLayer.dll`)

### 2.1 Sự thật cốt lõi
- **KHÔNG có type sẵn** cho VAH/VAL/POC/IB/TPO/ValueArea → **tự tính hết** từ histogram giá→volume.
- Có sẵn 2 primitive để dựng profile phiên: **`VolumeAnalysisData.Combine(other)`** (gộp footprint nhiều nến thành 1) và **`VolumeAnalysisData.CreateAggregatedSnapshot(step)`** (gộp mức giá về lưới thô hơn = hàng TPO).
- Per-level THẬT: `bar.VolumeAnalysisData.PriceLevels : Dictionary<double, VolumeAnalysisItem>`; mỗi item có `Volume, BuyVolume, SellVolume, Delta, MaxDelta, MinDelta, Trades, MaxOneTradeVolume,…`. Và `.Total` (per-bar).
- **Ranh giới ngày có sẵn (robust)** — dùng, đừng tự tính lịch: `Symbol.CurrentSessionsInfo` (SessionsContainer, có `.TimeZone`) + `SessionsExtensions.EnumerateSessionTimeFrames(container, from, to)` → `IEnumerable<Interval<DateTime>>` (mỗi phần tử = 1 ngày giao dịch, có `.From/.To`).
- Ranh giới **Á/Âu/Mỹ KHÔNG phải session sàn** → tự chia theo giờ-trong-ngày (dùng `TimeUtils.ConvertFromUTCToTimeZone(bar.TimeLeft, tz)` rồi so với 3 khung ở §1.1).
- **Cả 2 indicator vẽ ở main window, map theo giá thật** qua `win.CoordinatesConverter.GetChartY(price)` → **KHÔNG cần trò line-series ẩn auto-scale** (trò đó chỉ cho cửa sổ phụ như VSA/Ask-Bid).
- **Không có panel chữ nhiều dòng native** → tự vẽ **hộp chữ trong `OnPaintChart`** (tái dùng đúng mẫu hộp tooltip đã có trong `OrderFlowBubbles`).

### 2.2 Đọc profile phiên từ nến chart (không mở subscription thứ 2)
```csharp
// Gộp footprint các nến [fromIdx..toIdx] (Begin index) thành 1 profile phiên.
static VolumeAnalysisData BuildSessionVA(HistoricalData hd, int fromIdx, int toIdx) {
    var acc = new VolumeAnalysisData();
    for (int i = fromIdx; i <= toIdx; i++) {
        if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
        var va = b.VolumeAnalysisData;
        if (va?.PriceLevels == null || va.PriceLevels.Count == 0) continue;
        acc.Combine(va);
    }
    return acc;
}
// Hàng TPO thô hơn tick (khuyến nghị gom 2–3 tick/hàng cho vàng ~4100):
// var rows = acc.CreateAggregatedSnapshot(tick * rowTicks);  // đọc rows.PriceLevels
```
⚠ **Chỉ dùng `Volume`/`BuyVolume`/`SellVolume` per-level** (cộng được) từ object đã Combine. **KHÔNG tin `MaxDelta`/`MaxOneTradeVolume` trên object đã Combine** (không cộng dồn được) — cần thì đọc từng nến gốc.

### 2.3 POC + Value Area (rule 2 hàng, 70%) — VALIDATE 90%@5tick
```csharp
// rows: price->weight (weight = Volume per hàng, HOẶC số TPO letter). Trả POC, VAH, VAL.
static (double poc,double vah,double val) ComputeValueArea(SortedDictionary<double,double> rows, double frac=0.70){
    if (rows.Count==0) return (double.NaN,double.NaN,double.NaN);
    var prices=rows.Keys.ToArray(); var w=rows.Values.ToArray(); double tot=w.Sum();
    int poc=0; for(int i=1;i<w.Length;i++) if(w[i]>w[poc]) poc=i;
    double acc=w[poc], target=tot*frac; int lo=poc, hi=poc;
    while(acc<target && (lo>0||hi<w.Length-1)){
        double up  =(hi<w.Length-1?w[hi+1]:0)+(hi<w.Length-2?w[hi+2]:0);
        double down=(lo>0?w[lo-1]:0)+(lo>1?w[lo-2]:0);
        if(hi>=w.Length-1){acc+=down; lo=Math.Max(0,lo-2);}
        else if(lo<=0)    {acc+=up;   hi=Math.Min(w.Length-1,hi+2);}
        else if(up>=down) {acc+=up;   hi=Math.Min(w.Length-1,hi+2);}
        else              {acc+=down; lo=Math.Max(0,lo-2);}
    }
    return (prices[poc], prices[hi], prices[lo]);
}
```
Build `rows` bằng cách snap mỗi key `PriceLevels` về hàng `(long)Math.Round(price/rowStep)` rồi cộng weight (giống snap tick trong `OrderFlowBubbles.ComputeBar`).

### 2.4 IB + TPO letters
```csharp
static (double ibHigh,double ibLow) ComputeIB(HistoricalData hd,int sessFrom,int barsInIB){ // M30: barsInIB=2
    double h=double.MinValue,l=double.MaxValue;
    for(int k=0;k<barsInIB;k++) if(hd[sessFrom+k,SeekOriginHistory.Begin] is HistoryItemBar b){h=Math.Max(h,b.High);l=Math.Min(l,b.Low);}
    return (h,l);
}
// TPO letters: mỗi nến M30 = 1 "letter"; đánh dấu mọi hàng giá mà [Low,High] của nến phủ; đếm số letter/hàng → chạy ComputeValueArea trên số đếm đó.
static SortedDictionary<double,double> BuildTpoCounts(IEnumerable<(double lo,double hi)> periods,double rowStep){
    var c=new SortedDictionary<double,double>();
    foreach(var(lo,hi) in periods){ long a=(long)Math.Round(lo/rowStep),b=(long)Math.Round(hi/rowStep);
        for(long r=a;r<=b;r++){double p=r*rowStep; c[p]=c.TryGetValue(p,out var v)?v+1:1;}}
    return c;
}
```
> Dùng **volume-rows** cho DailyTpoBias (khớp "Volume Profile"), **TPO-letters** cho M30SessionZones (khớp Market Profile cổ điển). Cả 2 chung `ComputeValueArea`.

### 2.5 Session bounds (verified)
```csharp
var sc = Symbol.CurrentSessionsInfo;                 // CÓ THỂ null → guard, fallback RTH input
var frames = SessionsExtensions.EnumerateSessionTimeFrames(sc, chartStart, chartEnd).ToList();
var current = frames[frames.Count-1];                 // ngày đang chạy
var prior   = frames[frames.Count-2];                 // hôm qua
// Interval<DateTime>.From/.To = mốc mở/đóng (đã áp timezone của container).
```
Á/Âu/Mỹ: tự bucket theo `TimeUtils.ConvertFromUTCToTimeZone(bar.TimeLeft, tz).TimeOfDay` so 3 khung §1.1. (Nâng cấp sau: dựng `CustomSessionsContainer` từ 3 `CustomSession`.)

### 2.6 Render + panel + threading + build
- **Vẽ vùng/đường:** `OnPaintChart` trong main window (`if(!win.IsMainWindow) return;`), map giá bằng `GetChartY`, x span từ `GetChartX(sessionStart)`→`clip.Right` (kéo dài phải). Vùng = `FillRectangle` bán trong suốt + viền + nhãn phải. Vẽ vùng theo **thứ tự yếu→mạnh**, mã hoá độ mạnh bằng alpha/độ dày viền.
- **Panel chữ:** vẽ hộp cố định góc màn hình trong `OnPaintChart` (tái dùng mẫu hộp tooltip của `OrderFlowBubbles`): `MeasureString` → `FillRectangle` nền mờ → `DrawString` từng dòng. Góc panel = InputParameter (mặc định: DailyTpoBias **trên-trái**, M30SessionZones **trên-phải**), có toggle bật/tắt.
- **Threading:** publish 1 object `RenderState` bất biến (thay nguyên khối, không sửa tại chỗ). Calc thread ghi dưới `lock(_sync)`, paint đọc snapshot dưới `lock(_sync)` rồi vẽ ngoài lock. Serialize `Process()` bằng `_calcLock` (giống `OrderFlowBubbles`).
```csharp
sealed class RenderState { public SessionProfile Developing; public List<SessionProfile> Priors;
    public List<Zone> Zones; public List<(string text,Color col)> PanelLines; }
readonly object _sync=new(); RenderState _render;
```
- **VA gating:** implement `IVolumeAnalysisIndicator`, `IsRequirePriceLevelsCalculation=>true`; chỉ chạy sau `VolumeAnalysisData_Loaded()`; trong `OnUpdate` bail nếu `HistoricalData.VolumeAnalysisCalculationProgress?.State != Finished`. `OnClear()` xoá cache.
- **Cache phiên đã đóng:** `Dictionary<sessionKey, SessionProfile>`; chỉ tính lại **phiên đang phát triển** mỗi update (giống `_processedClosedCount`), phiên đóng đóng băng 1 lần.
- **Build (concat, 1 nguồn dùng chung):** giữ `ProfileEngine.cs` (thuần, không phụ thuộc Indicator/GDI). Script `build-tpo.sh`:
  ```sh
  cat ProfileEngine.cs DailyTpoBias.cs   > _tmp1.cs && ~/quantower-libs/qw-build.sh _tmp1.cs DailyTpoBias
  cat ProfileEngine.cs M30SessionZones.cs> _tmp2.cs && ~/quantower-libs/qw-build.sh _tmp2.cs M30SessionZones
  ```
  (mỗi indicator vẫn ra 1 DLL riêng, deploy `...\Settings\Scripts\Indicators\<tên>\`.)

---

## 3. INDICATOR 1 — DailyTpoBias (bias ngày real-time)

### 3.1 Input có sẵn (live)
Per nến 30′: `Open/High/Low/Close`, `bar.Total.Delta/Volume/MaxDelta/MinDelta`. **Developing profile** (tự tính mỗi tick từ nến trong ngày): `devVAH/devVAL/devPOC/devMid/devRange/devVArange/devTPOup/devTPOdn`. **IB** đóng băng sau 60′. **Ngày trước** `pVAH/pVAL/pPOC/pHigh/pLow/pClose` (và D-2). `Open0`=giá mở phiên, `bracket`=số nến 30′ đã đóng từ mở cửa.

### 3.2 Bộ chấm điểm (8 tín hiệu → nhãn + độ tin cậy)
`contribution_i = s_i · w_i · validityRamp_i`; `S = Σ contribution` (≈[−100,+100]); `a = alignedWeight/firedWeight`.

| Nhãn | S |
|---|---|
| Tăng mạnh | ≥ +45 |
| Tăng | +18…+45 |
| Trung tính | −18…+18 |
| Giảm | −45…−18 |
| Giảm mạnh | ≤ −45 |

`confidence = round( min(Cp,100·min(1,|S|/40)) · (0.4+0.6·a) )`, `Cp` = trần theo pha (§3.4).

**Trọng số (tổng 100):** A value-relationship **25** · B POC-migration **15** · C IB+RE **15** · D open-type **12** · E delta **10** · F single-print/poor **10** · G open-location **8** · H TPO-skew **5**.

Adaptive: `RangeTypical/IBTypical/DeltaTypical = median(20 ngày gần nhất)` (mặc định 900/100/936).

**A — Value relationship (w=25, CAO — mạnh nhất):** phân loại `[devVAL,devVAH]` so `[pVAL,pVAH]`, đòi cách nhau > `0.03·RangeTypical` (~27t):
`devVAL>pVAH`→cao hơn s=+1 · `devVAH<pVAL`→thấp hơn s=−1 · chồng cao +0.5 · chồng thấp −0.5 · nằm trong 0 · bao trùm ±0.15. validityRamp: 0.3 (br1–2), 0.6 (br3–4), 1.0 (br5+).

**B — POC migration (w=15):** `s = 0.6·clamp((devPOC−pPOC)/(RangeTypical·tick)/0.10,±1) + 0.4·clamp(driftPOC60′/(RangeTypical·tick)/0.05,±1)`; bỏ qua |shift|<~9t; xác nhận thêm bằng `devMid−pMid` cùng dấu. Ramp 0.5(br2)→1.0(br4+).

**C — IB width + range extension MỘT CHIỀU (w=15; hướng RE một chiều = CAO):**
`RE_up=High−IBHigh; RE_dn=IBLow−Low; oneSided = (RE_up>0.5·IB) XOR (RE_dn>0.5·IB)`.
`oneSided & RE_up>RE_dn → s=+min(1,RE_up/IB)` · ngược lại `s=−min(1,RE_dn/IB)` · cả 2 chiều → s=0.2·sign(Now−devMid). IB rộng >1.4·IBTypical = ngày cân bằng (fade biên); hẹp <0.7 = dễ trend. **Chỉ bật sau khi IB đóng (br2).** ⚠ "vượt IB" 2 chiều là chuyện thường (81% ngày) → chỉ XOR mới có tín hiệu.

**D — Open type Dalton (w=12):** trên nến 1–2, `R1=High1−Low1`. Open-Drive (mở ở biên, chạy ≥0.5·R1, không quay lại qua Open1, delta mạnh) s=±1 → **mốc phủ định ngày** (bull→Low1, bear→High1; thủng thì zero tín hiệu này). Open-Test-Drive ±0.7 · Open-Rejection-Reverse ±0.6 (chiều đảo) · Open-Auction 0.

**E — Delta xác nhận (w=10, YẾU, chỉ xác nhận + soi phân kỳ):** `s=0.35·clamp((100·devDelta/devVol−(−0.7))/1.5,±1) + 0.25·clamp(slope4(CumDelta)/…,±1) + 0.40·E3`. **E3 phân kỳ (phần quý):** giá tạo đỉnh phiên mới nhưng CumDelta không xác nhận → s_E3=−0.7 (cảnh báo đảo ở đỉnh); đáy mới mà CumDelta không xác nhận → +0.7. *(delta thô chỉ 57% khớp hướng + có sell-skew → đừng để dẫn.)*

**F — Single print / poor high-low (w=10, MONG MANH):** nếu đọc được mảng TPO-count/hàng thì dùng luật chuẩn (count==1 ở biên = excess/đuôi → chặn biên đó; count≥2 phẳng = poor/unfinished = nam châm sẽ bị phá). Không thì proxy theo cấu trúc nến (≥2 nến High trong 2 tick của đỉnh & đóng ở 25% trên = poor high…). *Live có PriceLevels nên có thể tính poor-high/low bằng TPO thật (đỉnh/đáy ≥2 TPO).*

**G — Open location vs VA hôm qua (w=8, THẤP):** Open0>pVAH → +0.4; <pVAL → −0.4; trong → 0. Nếu gap>0.08·RangeTypical (~72t) → rủi ro fade, giảm nửa. *(lý thuyết bảo mạnh, nhưng trên vàng 23h thực đo yếu → giữ nhẹ.)*

**H — TPO up/down skew (w=5, THẤP):** `s=clamp((devTPOup−devTPOdn)/237,±1)`; bỏ qua |skew|<60. *(Cần verify định nghĩa TPO Up/Down của Quantower trước khi tin.)*

### 3.3 Phân loại KIỂU NGÀY (cảnh báo sớm)
Trend (IB hẹp + RE một chiều + POC dịch cùng chiều + value mỏng `devVArange/devRange<0.40` + mỗi nến đóng về phía trend) → theo, mốc phủ định = IB-origin. · Normal (IB rộng >1.4·IBTypical + RE mỗi bên <0.5·IB) → fade biên. · Normal-Variation (IB vừa + RE 1 bên 0.5–1.5·IB rồi đứng) → theo tới target rồi fade. · Neutral (RE **cả 2** bên nhưng mỗi bên <1.0·IB **và** đóng gần giữa |Close−devMid|<0.15·devRange) → đứng ngoài. · Double-Distribution (POC dời ≥0.15·RangeTypical + có nến single-print tách 2 cụm) — **mong manh, chỉ gợi ý**.
> Cảnh báo: "2 chiều RE ⇒ Neutral" **over-fire** trên vàng → bắt buộc thêm điều kiện mỗi-bên-<1·IB + đóng-gần-giữa.

### 3.4 State machine (tính lại lúc nào)
PRE_OPEN (Cp60, chỉ ngày trước → kịch bản mở cửa) → OPEN br1 (Cp65: G full, A 0.3, D 0.5, E) → IB_FORMING br2 (Cp75: +D 1.0, A 0.6, B1, H; **đóng băng IB cuối 60′**) → IB_DONE br3+ (Cp90: bật C, B2, F; **cửa sổ quyết định chính**; chạy day-type) → MIDDAY (Cp95, mọi tín hiệu full) → CLOSE (Cp88; chốt value-relationship gần cuối; sinh mức cho ngày mai). Recompute mỗi tick đóng; mỗi mốc 30′ chạy lại open-type/IB-freeze/day-type + cuộn snapshot POC-60′-trước cho B2.

### 3.5 Output
**Trên chart:** đường `pVAH/pVAL/pPOC` (nét đứt), `devVAH/devVAL/devPOC` (liền), `IBHigh/IBLow` (chấm, sau 60′), `Open0` (mảnh); vùng VA đang phát triển (shade); marker excess/poor-high/single-print + mốc phủ định Open-Drive.
**Panel (VN, góc trên-trái):**
```
BIAS: <Tăng mạnh|…|Giảm mạnh>     Độ tin cậy: NN/100
Kiểu ngày (dự đoán): <…>   ⟨xác nhận: nến k⟩
Pha: <Trước mở|Mở cửa|Đang tạo IB|IB xong|Giữa phiên|Cuối phiên>
Top 3 lý do:  1. …  2. …  3. …        (mỗi lý do KÈM SỐ THẬT đã kích hoạt nó)
Mức hôm qua: VAH .. | POC .. | VAL .. | H .. | L ..
IB hôm nay: [IBLow–IBHigh]  (rộng/hẹp so trung vị 100t)
Cảnh báo: <phân kỳ / poor-high nam châm / thủng mốc Open-Drive>
```
Lý do = sort tín hiệu theo |contribution|, lấy top 3, render kèm con số thật (không bao giờ câu chữ chung chung — theo đúng luật "đọc số thật trên chart").

---

## 4. INDICATOR 2 — M30SessionZones (phiên + vùng)

### 4.1 Gộp phiên & tham số
Gán mỗi nến M30 vào Á/Âu/Mỹ theo giờ-trong-ngày (§1.1, là INPUT). Nến cùng nhãn liên tiếp → 1 **block phiên**; **cắt block khi đổi nhãn HOẶC gap thời gian >40′** (qua nghỉ bảo trì/cuối tuần). Params: 3 khung giờ + tz, VA_PCT=0.70, close mạnh/yếu 0.70/0.30, balance ROT≥0.55/TREND≤0.35 (VAwidth/range), overlap ACCEPT≥0.5/REJECT<0.2, band width, merge N, decay λ.

### 4.2 Profile phiên & object tóm tắt
`build_session_profile`: cộng TPO-count (và volume proxy live = per-level Volume thật) qua các nến → `poc_va()`. Object mỗi phiên:
`{label,start,end,open,close,high,low,range_t, poc,vah,val,va_width_t,vpoc, delta,volume, direction(UP/DOWN/FLAT), close_pos=(close−low)/(high−low), close_state(MẠNH≥.7/YẾU≤.3/TB), balance(ROT/TREND/INT), ib_high,ib_low, vs_prior}`.

### 4.3 Tường thuật "phiên nào làm gì" (template VN, điền từ object)
> **{Phiên}** hôm nay **{đi lên/xuống/ngang}** ({range_t} tick), đóng ở **{nửa trên/giữa/nửa dưới}** (**{mạnh/yếu/TB}**). Vùng giá trị **{val}–{vah}**, POC **{poc}**. Đấu giá **{có xu hướng/xoay vòng}**, Delta **{+N/−N}** (**{thuận/NGHỊCH}** hướng giá). So phiên trước: **{chấp nhận giá trị cũ / từ chối & dời / nằm trong}**.

`Delta thuận/NGHỊCH`: `sign(delta)==sign(direction)`? thuận : **NGHỊCH** (cờ phân kỳ — nêu ra, đây là tín hiệu đảo/hấp thụ).

### 4.4 Accept/Reject + quan hệ
`ovl=max(0,min(vah)−max(val)); frac=ovl/union`. frac≥.5 ACCEPT · <.2 REJECT · giữa PARTIAL; kèm `POC dời ±Nt`.
`relationship(B,A)`: INSIDE (B nằm trong A) · EXTEND_UP (VAH cao & VAL không thấp hơn) · EXTEND_DN · REVERSAL · OVERLAP. Tag di trú đa phiên (3 POC gần nhất): VA nâng→MUA · hạ→BÁN · chồng→chờ · thu hẹp→chờ break.

### 4.5 "Phiên Mỹ sẽ ưu tiên gì" (luật quyết định)
`AE_val/AE_vah` = VA gộp Á+Âu; `US_open`; order-flow = delta/CVD phiên Mỹ tới hiện tại. Xét theo thứ tự, khớp cái đầu:
1. **TIẾP DIỄN TREND ÂU:** Âu balance=TREND & hướng rõ & close cùng chiều & relationship(Âu,Á)=EXTEND cùng chiều & US_open không ngược → xác nhận CVD cùng dấu → lean = hướng Âu.
2. **PHÁ CÂN BẰNG Á-ÂU {LÊN/XUỐNG}:** relationship(Âu,Á)=INSIDE & US_open phá biên AE → xác nhận Δ cùng phía & giữ ngoài biên ≥2 nến → lean = phía phá.
3. **ĐẢO VỀ VÙNG GIÁ TRỊ:** phiên trước REJECT/quá đà (|leg|≥1.5·ATR_M30) & US_open quay vào lại AE VA → xác nhận CVD phân kỳ ở cực trị (hấp thụ) → lean = về AE_POC.
4. **FADE QUÁ ĐÀ:** Âu giãn mạnh (range≥p75 & close_state mạnh ở biên xa) & US_open gap tiếp cùng chiều → xác nhận hấp thụ (fp-m1) hoặc CVD phân kỳ → lean = NGƯỢC.
Mặc định: neutral, "chờ US_open định hướng vs AE value".
**Output:** `{lean(MUA/BÁN/TRUNG TÍNH), confidence= 40(luật)+20(order-flow xác nhận)+20(di trú giá trị hợp)+10(close mạnh phía lean)+10(cụm POC ủng hộ), reasons[VN]}`.

### 4.6 Vùng cần quan tâm (rank + band)
`Zone {center|band[lo,hi], type, side(S/R/either), strength 0-100, source, fresh, label_vn}`. Band = `clamp(round(0.06·ATR_M30),3,10)` tick; mức điểm đơn (POC/edge) = ±max(3t,0.04·ATR).
**Merge hợp lưu:** 2 vùng cách ≤ `max(5t,0.08·ATR)`≈7t → gộp, strength = max+0.5·min (cap 100).
**Decay:** `freshness=exp(−λ·số_phiên_kể_từ_khi_tạo)`, λ=0.25. **Retest** bật lại (giá quay đầu) ×1.15; xuyên qua & chấp nhận → ×0.4 và có thể đảo vai S↔R.

| Loại | Cách tính | Độ mạnh (mặc định) | Độ tin |
|---|---|---|---|
| **NAKED/VIRGIN POC** | POC phiên cũ mà **không nến phiên SAU (sau khi phiên đó kết thúc) phủ giá đó** | 70 + tuổi + volume | **CAO** (nam châm + S/R) |
| **Cụm POC chặt** | ≥2 POC phiên trong ≤7t | boost | **CAO** |
| **Băng tích luỹ giá trị** | ≥3 POC phiên trong ≤25t (nhìn "cụm" trực quan) | trung bình | MED |
| **Biên VAH/VAL phiên trước** | edge VA phiên | 60 | CAO |
| **Hấp thụ (Absorption)** | *(cần fp-m1 / live per-level)* nến vol≥p85 & range≤p40 & ở cực trị & Δ ngược chiều tiếp cận | 58 | MED |
| **HVN (nút KL cao)** | đỉnh volume-theo-giá (live PriceLevels) ≥1.5·mean | 62 | CAO (live) / xấp xỉ (offline) |
| **Single-print / LVN edge** | hàng TPO=1 ở biên (đuôi ≥2 TPO mới đáng) | 50 | MED |
| **IB extreme / prior H-L / Midpoint** | như tên | 48 / 45 / 30 | MED / MED / YẾU |
| **LVN (vùng đi nhanh)** | dải TPO≤max(1,0.15·TPO_POC) | (không phải S/R — là "đường băng") | — |

### 4.7 Vùng TARGET cho lệnh đang chạy
Cho **LONG** (short đối xứng), target tăng dần theo cấu trúc gần nhất phía trên:
`T1 = min(biên VA đối diện gần nhất phía trên, HVN gần nhất)` · `T2 = HVN kế / biên xa của LVN-gap` · `T3 = đỉnh phiên trước / naked-POC trên / measured move (IB-projection: biên IB ± IB_width; hoặc VA-width projection)`. **Chốt trước vùng KL lớn 2–3 tick** (luật sách: phản ứng thường xảy ra NGAY TRƯỚC vùng nặng). Trình bày: *"Nếu LONG @X → T1 …, T2 …, T3 …; huỷ nếu đóng M30 dưới {inval}"*, `inval(LONG)=hỗ trợ mạnh gần nhất dưới entry (VAL/naked-POC/IB_low) − 3..5t`.

### 4.8 Output
**Trên chart:** vẽ vùng (rectangle theo band + nhãn phải), naked-POC (đường + nhãn "nam châm"), cụm POC (band đậm), biên VA phiên. Xếp alpha/viền theo strength.
**Panel (VN, góc trên-phải):**
```
PHIÊN HÔM NAY
Á : <câu tường thuật>
Âu: <câu tường thuật>
→ MỸ ưu tiên: <TIẾP DIỄN/PHÁ/ĐẢO/FADE> — lean <MUA|BÁN|TRUNG TÍNH> (NN/100)
   lý do: 1… 2… 3…
VÙNG (mạnh→yếu):
  R  4094.2  naked POC (nam châm)        [strength]
  S  4051.5–4051.7  cụm POC              [strength]
  …
Nếu LONG → T1/T2/T3 …  | inval < …
```

---

## 5. Kết quả TEST (prototype trên dữ liệu thật — `prototype_test.py`)

**Part 1 — dựng lại POC/VA (M30) vs đáp án nền tảng (101 profile):** POC exact **59%**, ≤3t **80%**, ≤5t **90%**; VAH ≤3t **94%**; VAL ≤3t **87%**. → **Công thức POC/VA đúng.** (Live sẽ chính xác hơn vì đọc per-level thật thay vì xấp xỉ TPO từ OHLC.)

**Part 2 — engine bias ngày (21 ngày, giá trị chốt):** nhãn hợp lý — 7/21–7/22 "vùng giá trị cao hơn"→**Tăng mạnh (+54/+53)**; 7/16–7/17 "chồng thấp hơn"→**Giảm**. Check logic (không phải backtest): bias có hướng khớp dấu POC ngày kế tiếp **9/13 = 69%**.

**Part 3 — gộp phiên + vùng (7 block phiên 7/22–7/24):** bảng phiên + delta thuận/NGHỊCH + accept/reject chạy đúng; bắt đúng **US 7/24 Δ=+911 NGHỊCH hướng giá giảm = hấp thụ mua ở đáy**. Vùng: **NAKED POC 4094.2** (kháng cự/nam châm trên), **cụm POC chặt 4051.5–4051.7** (hỗ trợ mạnh). → khớp cấu trúc thị trường thật.

---

## 6. Giới hạn TRUNG THỰC (ghi rõ để không ảo tưởng)

- **Test OFFLINE bị thiếu volume-theo-giá** (CSV chỉ có tổng/nến) → prototype xấp xỉ POC bằng TPO từ OHLC. **LIVE KHÔNG bị:** đọc `PriceLevels` = volume/bid/ask THẬT từng mức → VPOC/HVN/absorption/per-level delta đều làm được **live**. (Cần verify feed có điền per-level — xem §9.)
- **Không dò được iceberg / lệnh đơn lớn:** `Max one trade Vol.`=0 khắp feed này.
- **Stacked Imbalance THẬT (Bid×Ask chéo từng mức):** live có `BuyVolume/SellVolume` per-level nên **làm được ở M1 footprint** (đúng như OrderFlowBubbles đang làm) — nhưng ở tầng M30-session này chỉ cần proxy delta-skew; không nhét stacked-imbalance vào 2 indicator này (để cho Bubbles).
- **`MaxDelta/MinDelta` per-nến = 0 trong export này** → tín hiệu Exhaustion/Open-Drive-delta cần verify feed live có điền không; không thì hạ cấp.
- **Signal G (open location), F (single-print proxy), day-type Double-Distribution, TPO Up/Down** = **mong manh** → giữ trọng số thấp / gắn nhãn độ tin thấp trong panel.
- **`CreateAggregatedSnapshot` & `Combine` field-semantics**: đã VERIFY tồn tại, chưa verify số học khi live → §9.

---

## 7. Thứ tự triển khai (cho phiên effort thấp)

- **Phase 0 — `ProfileEngine.cs` + `build-tpo.sh`:** viết engine thuần (BuildSessionVA, ToRows, BuildTpoCounts, ComputeValueArea, ComputeIB, poc_va, FindZones, SessionBounds) + struct `SessionProfile`/`Zone`. Build thử rỗng (1 indicator vỏ) cho sạch 0 warning.
- **Phase 1 — DailyTpoBias khung:** VA gating + session bounds + dựng developing daily profile + prior day → **vẽ VAH/VAL/POC/IB + mức hôm qua**. Deploy Windows, verify số khớp TPO chart nền tảng. (Chưa cần bias.)
- **Phase 2 — DailyTpoBias bias:** thêm 8 tín hiệu + scoring + state machine + panel VN + marker. Calibrate ngưỡng theo feed thật.
- **Phase 3 — M30SessionZones khung + phiên:** gộp Á/Âu/Mỹ + object tóm tắt + tường thuật + luật US + panel VN.
- **Phase 4 — M30SessionZones vùng:** naked POC, cụm POC, biên VA, HVN/absorption (live per-level), targets. Vẽ vùng + rank.
- **Phase 5 — polish:** calibrate band/decay/strength trên GC/MGC thật, chỉnh góc panel tránh đè 4 indicator cũ, cập nhật memory (sửa nhận định cũ nếu có, ghi API đã verify).

Mỗi phase: build Linux sạch → deploy Windows → chụp lại → chỉnh. **Commit + push sau mỗi phase.**

---

## 8. Rủi ro phải VERIFY trên Windows (feed live)

1. **`bar.TimeLeft` là UTC hay local?** (quyết định bucket Á/Âu/Mỹ). Log `bar.TimeLeft` vs `IChart.CurrentTimeZone`; dùng `TimeUtils.ConvertFromUTCToTimeZone`. Ngày thì né bằng `EnumerateSessionTimeFrames` (tự áp tz).
2. **`Symbol.CurrentSessionsInfo` có null/thiếu không** trên feed dxFeed/Rithmic/Ironbeam → fallback khung RTH input.
3. **`Combine` cộng đúng `Volume/BuyVolume/SellVolume`?** So tổng session Combine vs Σ `Total.Volume` từng nến.
4. **`CreateAggregatedSnapshot(step)` canh lưới đúng?** (lệch 1 hàng → lệch VAH/VAL 1 hàng). Đối chiếu snap tay.
5. **Feed có điền per-level `PriceLevels` + `MaxDelta` không**, và **độ sâu lịch sử ngày trước** (demo dxFeed/Rithmic mỏng → prior-day profile có thể rỗng cho tới khi có gói data đủ history).
6. **Panel/vùng không đè** 4 indicator cũ (VSA/DMA/Ask-Bid ở cửa sổ phụ; Bubbles overlay main) → guard `IsMainWindow`, góc panel input.

---

## 9. Nguồn
- Dữ liệu: `data-export/{TPO-chart-daily,tpo-chart-m30,fp-m1}.csv`. Prototype: `quantower-tpo-suite/prototype_test.py`.
- Lý thuyết: `ebook/text/orderflow-full.md` (Volume Profile, HVN/LVN, Value Area, Unfinished Business, Cumulative Delta, 5+4 setup, chốt lời), `glossary.md`, `course/text/bai-*.md`.
- API Quantower verify từ `~/quantower-libs/TradingPlatform.BusinessLayer.dll`; mẫu code từ 4 indicator hiện có (`quantower-orderflow-indicator`, `quantower-askbid-delta`, `quantower-vsa-volume`, `quantower-dma`).
