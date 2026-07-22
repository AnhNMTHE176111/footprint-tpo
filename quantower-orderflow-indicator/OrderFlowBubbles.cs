// ============================================================================
//  OrderFlow Bubbles  —  custom footprint / order-flow signal indicator for QUANTOWER
// ============================================================================
//  BẢN PORT từ indicator ATAS cùng tên (xem ../atas-orderflow-indicator).
//  Cùng triết lý: gom tín hiệu order flow thành bubble trên chart, bật/tắt từng phần.
//
//  KHÁC BIỆT API ATAS -> QUANTOWER (đọc kỹ trước khi sửa):
//    • ATAS có PriceSelectionValue vẽ sẵn theo price-level. Quantower KHÔNG có ->
//      ta TỰ tính tín hiệu, lưu vào _bubbles[barIndex], rồi TỰ VẼ trong OnPaintChart (GDI+).
//    • Footprint (bid/ask theo từng mức giá) lấy qua interface IVolumeAnalysisIndicator:
//         bar.VolumeAnalysisData.PriceLevels[price] -> VolumeAnalysisItem
//         item.BuyVolume  = volume khớp ở ASK (phe MUA chủ động)   (~ ATAS lvl.Ask)
//         item.SellVolume = volume khớp ở BID (phe BÁN chủ động)   (~ ATAS lvl.Bid)
//         item.Volume     = tổng                                    (~ ATAS lvl.Volume)
//         item.Trades     = số lệnh                                 (~ ATAS lvl.Ticks)
//         Total.Delta / Total.Volume = delta / volume CẢ NẾN.
//    • Quantower KHÔNG có delta chạy trong nến (intrabar MaxDelta/MinDelta của ATAS).
//      -> Exhaustion được ĐIỀU CHỈNH: so delta nến hiện tại với delta LỚN NHẤT của
//         cụm nến gần đây (swing) thay cho "đỉnh delta intrabar". Xem TryExhaustion.
//    • Toạ độ pixel: CurrentChart.Windows[args.WindowIndex].CoordinatesConverter
//         GetChartX(bar.TimeLeft)+BarsWidth/2 = tâm nến; GetChartY(price) = Y của mức giá.
//    • Màu = System.Drawing.Color (không phải Media.Color như ATAS) -> đơn giản hơn.
//    • DEFAULT đã CHỈNH cho MGC (khác code ATAS gốc, theo hiệu chỉnh 2026-07-22):
//         ImbalanceMinVolume=10 (ATAS 15), BigTradeMinVolume=25 (ATAS 20), BigTradeZ=3.0 (ATAS 2.5).
//         -> Big Trade bắn thưa hơn (hợp M30), Stacked Imbalance nhạy hơn cho volume nhỏ của MGC.
//
//  HỆ MÃ HOÁ 3 KÊNH (giữ nguyên như ATAS):
//    • MÀU  = phe chủ động: CYAN = MUA (đỉnh) · ĐỎ/CAM = BÁN (đáy).
//    • HÌNH = loại tín hiệu: Ellipse / Triangle / Rectangle / Diamond.
//    • SIZE = độ mạnh (z-score / tỷ lệ volume) — to = mạnh.
//  Bubble ĐẶC = tín hiệu chủ động (Big Trade/Surge/Imbalance...); Bubble HALO (viền mờ)
//  = Absorption / Stop-hunt.
// ============================================================================

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using TradingPlatform.BusinessLayer;

namespace OrderFlowBubbles
{
    public class OrderFlowBubbles : Indicator, IVolumeAnalysisIndicator
    {
        // ===================== hình bubble =====================
        private enum Shape { Ellipse, Triangle, Rectangle, Diamond }

        private sealed class Bubble
        {
            public double Price;
            public Shape Shape;
            public Color Color;
            public int Size;            // đường kính px
            public int Transparency;    // 0..100 (0 = đặc, 100 = trong suốt) — như ATAS
            public bool Halo;           // true = viền + fill mờ (Absorption); false = fill đặc
            public string Tooltip;
        }

        // bubble theo TỪNG NẾN, key = chỉ số nến tuyệt đối (SeekOriginHistory.Begin, 0 = cũ nhất)
        // _bubbles bị GHI ở thread tính toán (OnUpdate/Process) và ĐỌC ở thread vẽ (OnPaintChart)
        // -> MỌI truy cập phải trong lock (_sync). Thread vẽ copy snapshot ngắn rồi vẽ ngoài lock.
        private readonly Dictionary<int, List<Bubble>> _bubbles = new();
        private readonly object _sync = new();

        // ===================== baseline z-score (giống ATAS) =====================
        private readonly Queue<(double sum, double sumSq, int count)> _lvlWin = new();
        private double _lvlSum, _lvlSumSq;
        private long _lvlCount;
        private readonly Queue<double> _adWin = new();   // |delta nến| window
        private double _adSum, _adSumSq;

        private readonly List<double> _cvd = new();      // cumulative delta theo chỉ số tuyệt đối
        private int _processedClosedCount;               // số nến ĐÃ đóng đã nạp vào baseline
        private bool _vaLoaded;

        // ================================================================
        //  INPUT PARAMETERS  (Quantower xếp theo sortIndex trong Settings)
        // ================================================================

        // ---------- Appearance ----------
        [InputParameter("Màu MUA (buy aggressor)", 1)]
        public Color BuyColor { get; set; } = Color.Cyan;

        [InputParameter("Màu BÁN (sell aggressor)", 2)]
        public Color SellColor { get; set; } = Color.OrangeRed;

        [InputParameter("Kích thước nhỏ nhất", 3, 2, 60, 1, 0)]
        public int MinBubbleSize { get; set; } = 8;

        [InputParameter("Kích thước lớn nhất", 4, 2, 80, 1, 0)]
        public int MaxBubbleSize { get; set; } = 24;

        [InputParameter("Độ trong 'halo' hấp thụ (0-100)", 5, 0, 100, 1, 0)]
        public int HaloTransparency { get; set; } = 55;

        [InputParameter("Độ trong bubble đặc (0-100)", 6, 0, 100, 1, 0)]
        public int SolidTransparency { get; set; } = 10;

        // ---------- Delta Numbers ----------
        [InputParameter("Hiện số Delta dưới nến", 10)]
        public bool ShowDeltaNumbers { get; set; } = true;

        [InputParameter("Cỡ chữ Delta", 11, 6, 40, 1, 0)]
        public int DeltaFontSize { get; set; } = 11;

        [InputParameter("Delta: cách đáy nến (px)", 12, 0, 60, 1, 0)]
        public int DeltaYOffsetPx { get; set; } = 6;

        [InputParameter("Delta: chỉ vẽ khi bề rộng nến ≥ (px)", 13, 1, 100, 1, 0)]
        public int DeltaMinBarWidthPx { get; set; } = 6;

        [InputParameter("Delta: nền mờ sau chữ", 14)]
        public bool DeltaBackground { get; set; } = false;

        // ---------- Baseline ----------
        [InputParameter("Số nến baseline (rolling)", 20, 10, 500, 1, 0)]
        public int BaselineBars { get; set; } = 50;

        [InputParameter("Mẫu tối thiểu trước khi báo", 21, 5, 5000, 1, 0)]
        public int MinSamples { get; set; } = 40;

        // ---------- 1) Absorption ----------
        [InputParameter("Absorption · Bật", 30)]
        public bool AbsorptionEnabled { get; set; } = true;

        [InputParameter("Absorption · Volume z-score ≥", 31, 0.0, 10.0, 0.1, 1)]
        public double AbsorptionZ { get; set; } = 2.0;

        [InputParameter("Absorption · Tỷ lệ 1 phe áp đảo ≥ (0-1)", 32, 0.5, 1.0, 0.05, 2)]
        public double AbsorptionImbalancePct { get; set; } = 0.60;

        [InputParameter("Absorption · Giá dịch tối đa (ticks)", 33, 0, 20, 1, 0)]
        public int AbsorptionMaxDisplaceTicks { get; set; } = 2;

        // ---------- 2) Exhaustion ----------
        [InputParameter("Exhaustion · Bật", 40)]
        public bool ExhaustionEnabled { get; set; } = true;

        [InputParameter("Exhaustion · Volume nến ≤ x lần nến trước", 41, 0.1, 1.5, 0.05, 2)]
        public double ExhVolFadeRatio { get; set; } = 0.6;

        [InputParameter("Exhaustion · Delta co ≤ x lần delta đỉnh swing", 42, 0.0, 1.0, 0.05, 2)]
        public double ExhDeltaFadeRatio { get; set; } = 0.4;

        [InputParameter("Exhaustion · Lookback đỉnh/đáy cục bộ", 43, 1, 50, 1, 0)]
        public int ExhSwingLookback { get; set; } = 5;

        // ---------- 3) Stacked Imbalance ----------
        [InputParameter("Stacked Imbalance · Bật", 50)]
        public bool ImbalanceEnabled { get; set; } = false;

        [InputParameter("Stacked Imbalance · Tỷ lệ chéo % (300 = 3:1)", 51, 100, 2000, 10, 0)]
        public int ImbalanceRatioPct { get; set; } = 300;

        [InputParameter("Stacked Imbalance · Volume tối thiểu mỗi mức", 52, 1, 100000, 1, 0)]
        public int ImbalanceMinVolume { get; set; } = 10;

        [InputParameter("Stacked Imbalance · Số mức liên tiếp", 53, 2, 20, 1, 0)]
        public int ImbalanceRun { get; set; } = 3;

        // ---------- 4) Big Trade ----------
        [InputParameter("Big Trade · Bật", 60)]
        public bool BigTradeEnabled { get; set; } = false;

        [InputParameter("Big Trade · Volume tối thiểu / mức", 61, 1, 1000000, 1, 0)]
        public double BigTradeMinVolume { get; set; } = 25;

        [InputParameter("Big Trade · Hoặc volume z-score ≥", 62, 0.0, 10.0, 0.1, 1)]
        public double BigTradeZ { get; set; } = 3.0;

        // ---------- 5) Delta Surge ----------
        [InputParameter("Delta Surge · Bật", 70)]
        public bool DeltaSurgeEnabled { get; set; } = false;

        [InputParameter("Delta Surge · |Delta| z-score ≥", 71, 0.0, 10.0, 0.1, 1)]
        public double DeltaSurgeZ { get; set; } = 2.0;

        // ---------- 6) Delta Divergence ----------
        [InputParameter("Divergence · Bật (thử nghiệm)", 80)]
        public bool DivergenceEnabled { get; set; } = false;

        [InputParameter("Divergence · Lookback swing", 81, 2, 50, 1, 0)]
        public int DivSwingLookback { get; set; } = 6;

        // ---------- 7) Liquidity Sweep ----------
        [InputParameter("Sweep · Bật", 90)]
        public bool SweepEnabled { get; set; } = false;

        [InputParameter("Sweep · Lookback swing", 91, 2, 50, 1, 0)]
        public int SweepLookback { get; set; } = 8;

        // ---------- 8) Unfinished Business ----------
        [InputParameter("Unfinished Business · Bật", 100)]
        public bool UnfinishedEnabled { get; set; } = false;

        // ---------- 9) Iceberg (proxy) ----------
        [InputParameter("Iceberg · Bật (xấp xỉ)", 110)]
        public bool IcebergEnabled { get; set; } = false;

        [InputParameter("Iceberg · Volume z-score ≥", 111, 0.0, 10.0, 0.1, 1)]
        public double IcebergZ { get; set; } = 2.5;

        [InputParameter("Iceberg · Số lệnh (trades) tối thiểu", 112, 1, 5000, 1, 0)]
        public int IcebergMinTrades { get; set; } = 25;

        // ---------- 10) Stop-hunt + Absorption ----------
        [InputParameter("Stop-hunt · Bật", 120)]
        public bool StopHuntEnabled { get; set; } = false;

        [InputParameter("Stop-hunt · Lookback swing", 121, 2, 50, 1, 0)]
        public int StopHuntLookback { get; set; } = 8;

        // ================================================================
        //  CTOR
        // ================================================================
        public OrderFlowBubbles() : base()
        {
            Name = "OrderFlow Bubbles";
            Description = "Footprint / order-flow signals dạng bubble (port từ ATAS). Cần dữ liệu Volume Analysis.";
            SeparateWindow = false;   // vẽ đè lên chart giá
        }

        // Cần footprint theo TỪNG MỨC GIÁ -> true (bắt buộc, khác example chỉ cần Total)
        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            _vaLoaded = true;
            ResetState();
            Process();
        }

        protected override void OnInit() { }

        protected override void OnClear()
        {
            _vaLoaded = false;
            ResetState();
        }

        private void ResetState()
        {
            lock (_sync) _bubbles.Clear();
            _lvlWin.Clear(); _lvlSum = _lvlSumSq = 0; _lvlCount = 0;
            _adWin.Clear(); _adSum = _adSumSq = 0;
            _cvd.Clear();
            _processedClosedCount = 0;
        }

        // ================================================================
        //  MAIN — chạy mỗi tick; chỉ tính khi Volume Analysis đã nạp xong
        // ================================================================
        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaLoaded) return;
            var progress = HistoricalData.VolumeAnalysisCalculationProgress;
            if (progress == null || progress.State != VolumeAnalysisCalculationState.Finished) return;
            Process();
        }

        // Nạp các nến vừa đóng vào baseline + tính tín hiệu, rồi tính lại nến đang hình thành.
        private void Process()
        {
            double tick = Symbol?.TickSize ?? 0;
            if (tick <= 0) return;

            int total = HistoricalData.Count;
            if (total == 0) return;

            int closedCount = total - 1;               // tất cả trừ nến đang hình thành
            EnsureCvd(total);

            // (1) xử lý các nến đóng chưa nạp: tính tín hiệu (baseline hiện tại) rồi nạp baseline
            for (int i = _processedClosedCount; i < closedCount; i++)
            {
                var bar = Bar(i);
                if (bar == null) continue;

                _cvd[i] = (i > 0 ? _cvd[i - 1] : 0.0) + BarDelta(bar);
                bool ready = _lvlCount >= MinSamples && LvlStd() > 0;
                ComputeBar(i, bar, tick, ready, isClosed: true);
                AddToBaseline(bar);
            }
            if (closedCount > _processedClosedCount) _processedClosedCount = closedCount;

            // (2) tính lại nến đang hình thành (index total-1) mỗi tick — idempotent
            int cur = total - 1;
            var curBar = Bar(cur);
            if (curBar != null)
            {
                _cvd[cur] = (cur > 0 ? _cvd[cur - 1] : 0.0) + BarDelta(curBar);
                bool ready = _lvlCount >= MinSamples && LvlStd() > 0;
                ComputeBar(cur, curBar, tick, ready, isClosed: false);
            }
        }

        // ================================================================
        //  TÍNH TÍN HIỆU CHO 1 NẾN (ghi đè _bubbles[bar])
        // ================================================================
        private void ComputeBar(int idx, HistoryItemBar bar, double tick, bool ready, bool isClosed)
        {
            var va = bar.VolumeAnalysisData;
            if (va == null || va.PriceLevels == null || va.PriceLevels.Count == 0)
            {
                lock (_sync) _bubbles.Remove(idx);
                return;
            }

            var list = new List<Bubble>();

            // gom mức giá theo chỉ số tick (chống lỗi so sánh double) + tính các mức cực trị
            var byTick = new Dictionary<long, (double price, VolumeAnalysisItem it)>();
            double maxVol = double.MinValue, maxVolPrice = bar.Close;
            double maxPosDelta = 0, maxPosPrice = bar.High;
            double minNegDelta = 0, minNegPrice = bar.Low;
            foreach (var kv in va.PriceLevels)
            {
                long k = (long)Math.Round(kv.Key / tick);
                byTick[k] = (kv.Key, kv.Value);
                var it = kv.Value;
                if (it.Volume > maxVol) { maxVol = it.Volume; maxVolPrice = kv.Key; }
                if (it.Delta > maxPosDelta) { maxPosDelta = it.Delta; maxPosPrice = kv.Key; }
                if (it.Delta < minNegDelta) { minNegDelta = it.Delta; minNegPrice = kv.Key; }
            }

            long loIdx = (long)Math.Round(bar.Low / tick);
            long hiIdx = (long)Math.Round(bar.High / tick);

            int imbBuyRun = 0, imbSellRun = 0;
            for (long k = loIdx; k <= hiIdx; k++)
            {
                if (!byTick.TryGetValue(k, out var lvl)) { imbBuyRun = 0; imbSellRun = 0; continue; }
                double price = lvl.price;
                var it = lvl.it;
                double buy = it.BuyVolume, sell = it.SellVolume, vol = it.Volume;
                double sum = buy + sell;
                double volZ = ready ? (vol - LvlMean()) / LvlStd() : 0.0;

                // 1) ABSORPTION — volume lớn 1 phe nhưng giá đứng tại cực trị
                if (AbsorptionEnabled && ready && volZ >= AbsorptionZ && sum > 0)
                {
                    double buyDom = buy / sum, sellDom = sell / sum;
                    if (buyDom >= AbsorptionImbalancePct && (bar.High - price) / tick <= AbsorptionMaxDisplaceTicks)
                        list.Add(MakeBubble(price, Shape.Ellipse, BuyColor, SizeFromZ(volZ, AbsorptionZ),
                            HaloTransparency, true, $"Buy absorption  vZ={volZ:0.0}"));
                    else if (sellDom >= AbsorptionImbalancePct && (price - bar.Low) / tick <= AbsorptionMaxDisplaceTicks)
                        list.Add(MakeBubble(price, Shape.Ellipse, SellColor, SizeFromZ(volZ, AbsorptionZ),
                            HaloTransparency, true, $"Sell absorption  vZ={volZ:0.0}"));
                }

                // 3) STACKED IMBALANCE — chéo mức trên (Ask) vs mức dưới (Bid)
                if (ImbalanceEnabled && byTick.TryGetValue(k - 1, out var lo))
                {
                    double askFilter = lo.it.SellVolume * ImbalanceRatioPct / 100.0;
                    if (buy > askFilter && buy > ImbalanceMinVolume) imbBuyRun++; else imbBuyRun = 0;
                    if (imbBuyRun >= ImbalanceRun)
                        list.Add(MakeBubble(price, Shape.Diamond, BuyColor,
                            SizeFromRatio(askFilter > 0 ? buy / askFilter : 1), SolidTransparency, false,
                            $"Stacked buy imbalance x{imbBuyRun}"));

                    double bidFilter = buy * ImbalanceRatioPct / 100.0;
                    if (lo.it.SellVolume > bidFilter && lo.it.SellVolume > ImbalanceMinVolume) imbSellRun++; else imbSellRun = 0;
                    if (imbSellRun >= ImbalanceRun)
                        list.Add(MakeBubble(lo.price, Shape.Diamond, SellColor,
                            SizeFromRatio(bidFilter > 0 ? lo.it.SellVolume / bidFilter : 1), SolidTransparency, false,
                            $"Stacked sell imbalance x{imbSellRun}"));
                }

                // 4) BIG TRADE — 1 mức volume rất lớn
                if (BigTradeEnabled && (vol >= BigTradeMinVolume || (ready && volZ >= BigTradeZ)))
                    list.Add(MakeBubble(price, Shape.Ellipse, AggColor(buy, sell),
                        SizeFromZ(ready ? volZ : BigTradeZ, 0), SolidTransparency, false,
                        $"Big print  vol={vol:0}"));

                // 9) ICEBERG proxy — volume z cao + nhiều lệnh + giá không phá qua mức
                if (IcebergEnabled && ready && volZ >= IcebergZ && it.Trades >= IcebergMinTrades
                    && price > bar.Low && price < bar.High)
                    list.Add(MakeBubble(price, Shape.Rectangle, AggColor(buy, sell),
                        SizeFromZ(volZ, IcebergZ), SolidTransparency, false,
                        $"Iceberg proxy  vol={vol:0} trades={it.Trades:0}"));

                // 8) UNFINISHED BUSINESS — tại đỉnh/đáy nến còn giao dịch cả 2 phía
                if (UnfinishedEnabled)
                {
                    if (k == hiIdx && sell > 0)
                        list.Add(MakeBubble(bar.High, Shape.Rectangle, SellColor, MinBubbleSize,
                            SolidTransparency, false, "Unfinished business (high)"));
                    if (k == loIdx && buy > 0)
                        list.Add(MakeBubble(bar.Low, Shape.Rectangle, BuyColor, MinBubbleSize,
                            SolidTransparency, false, "Unfinished business (low)"));
                }
            }

            // ---- detector theo NẾN ----
            double barVol = va.Total.Volume;
            double barDelta = va.Total.Delta;

            if (ExhaustionEnabled) TryExhaustion(idx, bar, barVol, barDelta, maxPosPrice, minNegPrice, list);
            if (DeltaSurgeEnabled && ready) TryDeltaSurge(barDelta, maxVolPrice, list);
            // Divergence gắn vào nến PIVOT (idx-n) -> chỉ chạy khi idx là nến ĐÃ ĐÓNG (mỗi pivot xử lý
            // đúng 1 lần khi nến xác nhận đóng). Nếu chạy cho nến đang hình thành sẽ append trùng mỗi tick.
            if (DivergenceEnabled && isClosed) TryDivergence(idx);
            if (SweepEnabled) TrySweep(idx, bar, barDelta, list);
            if (StopHuntEnabled) TryStopHunt(idx, bar, tick, list);

            lock (_sync)
            {
                if (list.Count > 0) _bubbles[idx] = list;
                else _bubbles.Remove(idx);
            }
        }

        // ================================================================
        //  BAR-LEVEL DETECTORS
        // ================================================================

        // Exhaustion — ĐÃ ĐIỀU CHỈNH cho Quantower (không có delta intrabar):
        // so delta nến hiện tại với delta LỚN NHẤT (buy) / NHỎ NHẤT (sell) trong swing gần đây.
        private void TryExhaustion(int idx, HistoryItemBar cur, double curVol, double curDelta,
            double maxPosPrice, double minNegPrice, List<Bubble> list)
        {
            if (idx < 1) return;
            var prev = Bar(idx - 1);
            if (prev == null) return;
            if (curVol >= PrevVol(prev) * ExhVolFadeRatio) return;   // volume phải teo lại

            // Bám ATAS: điều kiện fade là delta nến < ngưỡng * đỉnh delta swing (KHÔNG chặn dấu delta
            // nến hiện tại) — nến net-âm tại đỉnh (sellers xuất hiện) vẫn tính là kiệt sức/đảo.
            int n = ExhSwingLookback;
            if (IsLocalHigh(idx, n))
            {
                double swingMax = MaxBarDeltaPrior(idx, n);          // "đỉnh delta" thay cho intrabar
                if (swingMax > 0 && curDelta < swingMax * ExhDeltaFadeRatio)
                    list.Add(MakeBubble(maxPosPrice, Shape.Triangle, BuyColor, MidSize(),
                        SolidTransparency, false, "Buy exhaustion"));
            }
            if (IsLocalLow(idx, n))
            {
                double swingMin = MinBarDeltaPrior(idx, n);
                if (swingMin < 0 && curDelta > swingMin * ExhDeltaFadeRatio)
                    list.Add(MakeBubble(minNegPrice, Shape.Triangle, SellColor, MidSize(),
                        SolidTransparency, false, "Sell exhaustion"));
            }
        }

        private void TryDeltaSurge(double barDelta, double maxVolPrice, List<Bubble> list)
        {
            double std = AdStd();
            if (std <= 0) return;
            double dZ = (Math.Abs(barDelta) - AdMean()) / std;
            if (dZ < DeltaSurgeZ) return;
            list.Add(MakeBubble(maxVolPrice, Shape.Ellipse, barDelta > 0 ? BuyColor : SellColor,
                SizeFromZ(dZ, DeltaSurgeZ), SolidTransparency, false, $"Delta surge {barDelta:0}"));
        }

        // Divergence neo vào nến PIVOT = idx-n (idx là nến xác nhận, đã đóng). Ghi thẳng vào
        // _bubbles[pivot]. Idempotent: xoá divergence cũ của pivot trước khi thêm lại (phòng gọi lại).
        private void TryDivergence(int idx)
        {
            int n = DivSwingLookback;
            if (idx < 2 * n) return;
            int pivot = idx - n;
            var c = Bar(pivot);
            if (c == null) return;

            var divs = new List<Bubble>();
            if (IsPivotHigh(pivot, n))
            {
                int prevPivot = FindPrevPivotHigh(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.High > pc.High && _cvd[pivot] <= _cvd[prevPivot])   // giá HH, delta LH
                        divs.Add(MakeBubble(c.High, Shape.Triangle, BuyColor, MidSize(),
                            SolidTransparency, false, "Bearish delta divergence"));
                }
            }
            if (IsPivotLow(pivot, n))
            {
                int prevPivot = FindPrevPivotLow(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.Low < pc.Low && _cvd[pivot] >= _cvd[prevPivot])     // giá LL, delta HL
                        divs.Add(MakeBubble(c.Low, Shape.Triangle, SellColor, MidSize(),
                            SolidTransparency, false, "Bullish delta divergence"));
                }
            }

            lock (_sync)
            {
                if (_bubbles.TryGetValue(pivot, out var existing))
                {
                    existing.RemoveAll(b => b.Tooltip != null && b.Tooltip.Contains("divergence"));
                    existing.AddRange(divs);
                    if (existing.Count == 0) _bubbles.Remove(pivot);
                }
                else if (divs.Count > 0)
                {
                    _bubbles[pivot] = divs;
                }
            }
        }

        private void TrySweep(int idx, HistoryItemBar cur, double barDelta, List<Bubble> list)
        {
            if (idx < SweepLookback + 1) return;
            double hi = MaxHighPrior(idx, SweepLookback);
            double lo = MinLowPrior(idx, SweepLookback);
            if (cur.High > hi && cur.Close < hi && barDelta < 0)
                list.Add(MakeBubble(cur.High, Shape.Triangle, BuyColor, MidSize(),
                    SolidTransparency, false, "Liquidity sweep (highs)"));
            if (cur.Low < lo && cur.Close > lo && barDelta > 0)
                list.Add(MakeBubble(cur.Low, Shape.Triangle, SellColor, MidSize(),
                    SolidTransparency, false, "Liquidity sweep (lows)"));
        }

        private void TryStopHunt(int idx, HistoryItemBar cur, double tick, List<Bubble> list)
        {
            if (idx < StopHuntLookback + 1) return;
            if (_lvlCount < MinSamples || LvlStd() <= 0) return;
            var va = cur.VolumeAnalysisData;
            if (va == null || va.PriceLevels == null) return;

            double hi = MaxHighPrior(idx, StopHuntLookback);
            double lo = MinLowPrior(idx, StopHuntLookback);

            if (cur.High > hi && cur.Close < hi && TryLevel(va, cur.High, tick, out var itH))
            {
                double vz = (itH.Volume - LvlMean()) / LvlStd();
                if (vz >= AbsorptionZ && itH.SellVolume > itH.BuyVolume)
                    list.Add(MakeBubble(cur.High, Shape.Ellipse, SellColor, MaxBubbleSize,
                        HaloTransparency, true, "Stop-hunt + sell absorption"));
            }
            if (cur.Low < lo && cur.Close > lo && TryLevel(va, cur.Low, tick, out var itL))
            {
                double vz = (itL.Volume - LvlMean()) / LvlStd();
                if (vz >= AbsorptionZ && itL.BuyVolume > itL.SellVolume)
                    list.Add(MakeBubble(cur.Low, Shape.Ellipse, BuyColor, MaxBubbleSize,
                        HaloTransparency, true, "Stop-hunt + buy absorption"));
            }
        }

        // ================================================================
        //  RENDER — vẽ bubble + số delta, tooltip khi hover
        // ================================================================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || !_vaLoaded) return;

            var win = CurrentChart.Windows[args.WindowIndex];
            var conv = win.CoordinatesConverter;
            var gr = args.Graphics;
            var clip = win.ClientRectangle;
            double tick = Symbol?.TickSize ?? 0;
            if (tick <= 0) return;
            double barsW = CurrentChart.BarsWidth;

            DateTime leftTime = conv.GetTime(clip.Left);
            DateTime rightTime = conv.GetTime(clip.Right);
            int li = (int)conv.GetBarIndex(leftTime);
            int ri = (int)Math.Ceiling(conv.GetBarIndex(rightTime));

            var mouse = args.MousePosition;
            string hoverTip = null; int hoverX = 0, hoverY = 0;

            var prevClip = gr.ClipBounds;
            gr.SetClip(clip);
            try
            {
                using var deltaFont = new Font("Arial", DeltaFontSize, FontStyle.Bold);
                using var centerFmt = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };

                for (int i = li; i <= ri; i++)
                {
                    if (i < 0 || i >= HistoricalData.Count) continue;
                    if (HistoricalData[i, SeekOriginHistory.Begin] is not HistoryItemBar bar) continue;

                    float cx = (float)(conv.GetChartX(bar.TimeLeft) + barsW / 2.0);

                    // --- bubbles --- (copy snapshot ngắn trong lock rồi vẽ NGOÀI lock)
                    List<Bubble> bubbles = null;
                    lock (_sync) { if (_bubbles.TryGetValue(i, out var l)) bubbles = new List<Bubble>(l); }
                    if (bubbles != null)
                    {
                        foreach (var b in bubbles)
                        {
                            float y = (float)conv.GetChartY(b.Price);
                            DrawShape(gr, b, cx, y);

                            // hover tooltip: chuột trong bán kính bubble
                            if (hoverTip == null)
                            {
                                float dx = mouse.X - cx, dy = mouse.Y - y;
                                float r = Math.Max(b.Size / 2f, 6f);
                                if (dx * dx + dy * dy <= r * r)
                                { hoverTip = b.Tooltip; hoverX = (int)cx; hoverY = (int)y; }
                            }
                        }
                    }

                    // --- số delta dưới đáy nến ---
                    if (ShowDeltaNumbers && barsW >= DeltaMinBarWidthPx && bar.VolumeAnalysisData != null)
                    {
                        double d = bar.VolumeAnalysisData.Total.Delta;
                        string text = d.ToString("+0;-0;0");
                        float y = (float)conv.GetChartY(bar.Low) + DeltaYOffsetPx + DeltaFontSize / 2f;
                        if (y <= clip.Bottom)
                        {
                            if (DeltaBackground)
                            {
                                var sz = gr.MeasureString(text, deltaFont);
                                using var bg = new SolidBrush(Color.FromArgb(120, 0, 0, 0));
                                gr.FillRectangle(bg, cx - sz.Width / 2 - 1, y - sz.Height / 2, sz.Width + 2, sz.Height);
                            }
                            using var db = new SolidBrush(d > 0 ? BuyColor : d < 0 ? SellColor : Color.Gray);
                            gr.DrawString(text, deltaFont, db, cx, y, centerFmt);
                        }
                    }
                }

                // --- tooltip nổi cạnh chuột ---
                if (hoverTip != null)
                {
                    using var tipFont = new Font("Arial", 9, FontStyle.Regular);
                    var sz = gr.MeasureString(hoverTip, tipFont);
                    float tx = hoverX + 12, ty = hoverY - sz.Height - 4;
                    using var bg = new SolidBrush(Color.FromArgb(220, 20, 20, 20));
                    gr.FillRectangle(bg, tx - 3, ty - 2, sz.Width + 6, sz.Height + 4);
                    gr.DrawString(hoverTip, tipFont, Brushes.White, tx, ty);
                }
            }
            finally { gr.SetClip(prevClip); }
        }

        private void DrawShape(Graphics gr, Bubble b, float cx, float cy)
        {
            int alpha = (int)Math.Round(255 * (100 - b.Transparency) / 100.0);
            alpha = Math.Clamp(alpha, 0, 255);
            var fillColor = Color.FromArgb(b.Halo ? Math.Min(alpha, 110) : alpha, b.Color);
            float r = b.Size / 2f;

            using var fill = new SolidBrush(fillColor);
            switch (b.Shape)
            {
                case Shape.Ellipse:
                    gr.FillEllipse(fill, cx - r, cy - r, b.Size, b.Size);
                    break;
                case Shape.Rectangle:
                    gr.FillRectangle(fill, cx - r, cy - r, b.Size, b.Size);
                    break;
                case Shape.Triangle:
                {
                    var pts = new[] { new PointF(cx, cy - r), new PointF(cx - r, cy + r), new PointF(cx + r, cy + r) };
                    gr.FillPolygon(fill, pts);
                    break;
                }
                case Shape.Diamond:
                {
                    var pts = new[] { new PointF(cx, cy - r), new PointF(cx + r, cy), new PointF(cx, cy + r), new PointF(cx - r, cy) };
                    gr.FillPolygon(fill, pts);
                    break;
                }
            }

            if (b.Halo)   // viền đậm cho hiệu ứng halo
            {
                using var pen = new Pen(Color.FromArgb(alpha, b.Color), 2f);
                switch (b.Shape)
                {
                    case Shape.Ellipse: gr.DrawEllipse(pen, cx - r, cy - r, b.Size, b.Size); break;
                    case Shape.Rectangle: gr.DrawRectangle(pen, cx - r, cy - r, b.Size, b.Size); break;
                }
            }
        }

        // ================================================================
        //  HELPERS
        // ================================================================
        private static Bubble MakeBubble(double price, Shape shape, Color color, int size,
            int transparency, bool halo, string tooltip)
            => new Bubble { Price = price, Shape = shape, Color = color, Size = size, Transparency = transparency, Halo = halo, Tooltip = tooltip };

        private HistoryItemBar Bar(int absIdx)
            => (absIdx >= 0 && absIdx < HistoricalData.Count)
                ? HistoricalData[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;

        private static double BarDelta(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total.Delta ?? 0.0;
        private static double PrevVol(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total.Volume ?? 0.0;

        private Color AggColor(double buy, double sell) => buy >= sell ? BuyColor : SellColor;

        private int MidSize() => (MinBubbleSize + MaxBubbleSize) / 2;

        private int SizeFromZ(double z, double zMin)
        {
            double t = Math.Clamp((z - zMin) / 4.0, 0, 1);
            return (int)Math.Round(MinBubbleSize + t * (MaxBubbleSize - MinBubbleSize));
        }

        private int SizeFromRatio(double ratio)
        {
            double t = Math.Clamp((ratio - 1.0) / 4.0, 0, 1);
            return (int)Math.Round(MinBubbleSize + t * (MaxBubbleSize - MinBubbleSize));
        }

        private static bool TryLevel(VolumeAnalysisData va, double price, double tick, out VolumeAnalysisItem it)
        {
            it = null;
            if (va?.PriceLevels == null) return false;
            long want = (long)Math.Round(price / tick);
            foreach (var kv in va.PriceLevels)
                if ((long)Math.Round(kv.Key / tick) == want) { it = kv.Value; return true; }
            return false;
        }

        // ----- rolling baseline -----
        private void AddToBaseline(HistoryItemBar bar)
        {
            var va = bar.VolumeAnalysisData;
            if (va?.PriceLevels == null) return;

            double sum = 0, sumSq = 0; int count = 0;
            foreach (var it in va.PriceLevels.Values)
            {
                double v = it.Volume;
                sum += v; sumSq += v * v; count++;
            }
            _lvlWin.Enqueue((sum, sumSq, count));
            _lvlSum += sum; _lvlSumSq += sumSq; _lvlCount += count;
            while (_lvlWin.Count > BaselineBars)
            {
                var (s, sq, n) = _lvlWin.Dequeue();
                _lvlSum -= s; _lvlSumSq -= sq; _lvlCount -= n;
            }

            double ad = Math.Abs(va.Total.Delta);
            _adWin.Enqueue(ad); _adSum += ad; _adSumSq += ad * ad;
            while (_adWin.Count > BaselineBars)
            {
                double d = _adWin.Dequeue(); _adSum -= d; _adSumSq -= d * d;
            }
        }

        private double LvlMean() => _lvlCount > 0 ? _lvlSum / _lvlCount : 0.0;
        private double LvlStd()
        {
            if (_lvlCount < 2) return 0.0;
            double mean = LvlMean();
            double var0 = _lvlSumSq / _lvlCount - mean * mean;
            return var0 > 0 ? Math.Sqrt(var0) : 0.0;
        }
        private double AdMean() => _adWin.Count > 0 ? _adSum / _adWin.Count : 0.0;
        private double AdStd()
        {
            if (_adWin.Count < 2) return 0.0;
            double mean = AdMean();
            double var0 = _adSumSq / _adWin.Count - mean * mean;
            return var0 > 0 ? Math.Sqrt(var0) : 0.0;
        }

        private void EnsureCvd(int total)
        {
            while (_cvd.Count < total) _cvd.Add(0.0);
        }

        // ----- swing helpers (causal, dùng chỉ số tuyệt đối) -----
        private double MaxHighPrior(int idx, int n)
        {
            double m = double.MinValue;
            for (int i = 1; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Max(m, b.High); }
            return m;
        }
        private double MinLowPrior(int idx, int n)
        {
            double m = double.MaxValue;
            for (int i = 1; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Min(m, b.Low); }
            return m;
        }
        private double MaxBarDeltaPrior(int idx, int n)
        {
            double m = double.MinValue;
            for (int i = 0; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Max(m, BarDelta(b)); }
            return m;
        }
        private double MinBarDeltaPrior(int idx, int n)
        {
            double m = double.MaxValue;
            for (int i = 0; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Min(m, BarDelta(b)); }
            return m;
        }
        private bool IsLocalHigh(int idx, int n) { var b = Bar(idx); return b != null && idx >= n && b.High >= MaxHighPrior(idx, n); }
        private bool IsLocalLow(int idx, int n) { var b = Bar(idx); return b != null && idx >= n && b.Low <= MinLowPrior(idx, n); }

        private bool IsPivotHigh(int idx, int n)
        {
            var c = Bar(idx);
            if (c == null || idx - n < 0 || idx + n >= HistoricalData.Count) return false;
            for (int i = 1; i <= n; i++)
            {
                var l = Bar(idx - i); var r = Bar(idx + i);
                if (l == null || r == null || l.High > c.High || r.High > c.High) return false;
            }
            return true;
        }
        private bool IsPivotLow(int idx, int n)
        {
            var c = Bar(idx);
            if (c == null || idx - n < 0 || idx + n >= HistoricalData.Count) return false;
            for (int i = 1; i <= n; i++)
            {
                var l = Bar(idx - i); var r = Bar(idx + i);
                if (l == null || r == null || l.Low < c.Low || r.Low < c.Low) return false;
            }
            return true;
        }
        private int FindPrevPivotHigh(int fromIdx, int n)
        {
            for (int b = fromIdx; b - n >= 0; b--) if (IsPivotHigh(b, n)) return b;
            return -1;
        }
        private int FindPrevPivotLow(int fromIdx, int n)
        {
            for (int b = fromIdx; b - n >= 0; b--) if (IsPivotLow(b, n)) return b;
            return -1;
        }
    }
}
