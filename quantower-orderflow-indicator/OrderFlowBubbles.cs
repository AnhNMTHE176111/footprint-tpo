// ============================================================================
//  OrderFlow Bubbles  —  custom footprint / order-flow signal indicator for QUANTOWER
// ============================================================================
//  Đọc footprint (Volume Analysis) theo TỪNG MỨC GIÁ, gom tín hiệu order-flow thành
//  hình vẽ trên chart. Bật/tắt từng phần. TẬP TRUNG VÀNG (GC/MGC).
//
//  ---- NGUYÊN TẮC PORTABLE (cốt lõi, xem plan) --------------------------------
//  Số delta/volume KHÁC NHAU theo feed/sàn (single vs double count, GC 100oz vs
//  MGC 10oz, cách gộp lệnh...) → ngưỡng tuyệt đối vô nghĩa. TẤT CẢ trigger dùng
//  thống kê TƯƠNG ĐỐI + ROBUST: modified z-score theo median + MAD trên baseline
//  động, hoặc tỷ lệ (deltaPct = Delta/Volume). Knob tuyệt đối DUY NHẤT còn lại là
//  MinActivityFloor (chống nhiễu nến đêm mỏng). Dùng median+MAD (KHÔNG mean+std) vì
//  volume đuôi nặng: std bị thổi phồng bởi chính cú spike ta muốn bắt.
//
//  ---- API QUANTOWER (đã kiểm chứng trên TradingPlatform.BusinessLayer.dll) -----
//  VolumeAnalysisItem (per-level VÀ Total per-bar) có:
//    BuyVolume (khớp ở ASK = mua chủ động ~ ATAS lvl.Ask)
//    SellVolume(khớp ở BID = bán chủ động ~ ATAS lvl.Bid)
//    Volume, Delta, DeltaFinish, Trades, BuyTrades, SellTrades,
//    MaxDelta / MinDelta      = delta chạy TRONG nến (intrabar) — CÓ THẬT, khác ghi chú cũ!
//    MaxOneTradeVolume        = lệnh ĐƠN lớn nhất — dùng cho Big Trade thật
//    AverageBuySize / AverageSellSize = cỡ lệnh trung bình
//  Truy cập: bar.VolumeAnalysisData.PriceLevels[price] và .Total.
//  Guard: HistoricalData.VolumeAnalysisCalculationProgress.State == Finished.
//
//  ---- HỆ MÃ HOÁ HÌNH (mới) ---------------------------------------------------
//    • Absorption      = TRÒN ĐẶC, cố định = bề rộng nến (không scale).  cyan(đỉnh)/đỏ(đáy)
//    • Big Trade       = TRÒN MỜ (halo), to dần theo MaxOneTradeVolume.  cyan/đỏ = aggressor
//    • Big Delta line  = GẠCH NGANG (rộng = nến), xanh(buy)/đỏ(sell).
//    • Nến delta lớn   = TÔ THÂN NẾN xanh(+delta)/đỏ(−delta).
//    • Số delta        = chữ dưới đáy nến, xanh/đỏ theo dấu.
//    • Exhaustion/Divergence/Sweep = tam giác;  Stacked Imbalance = thoi;  Unfinished = ngoặc.
//  Vẽ tay bằng GDI+ trong OnPaintChart (Quantower không có PriceSelectionValue).
//  _bubbles/_barTint bị GHI ở thread tính (Process) và ĐỌC ở thread vẽ → mọi truy cập
//  trong lock(_sync); thread vẽ copy snapshot rồi vẽ ngoài lock.
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
        // ===================== hình + bubble =====================
        private enum Shape { Ellipse, Triangle, Rectangle, Diamond, HLine }

        private sealed class Bubble
        {
            public double Price;
            public Shape Shape;
            public Color Color;
            public int Size;            // px (Big Trade...) HOẶC độ dày (HLine)
            public int Transparency;    // 0..100 (0 = đặc)
            public bool Halo;           // true = viền + fill mờ (Big Trade)
            public bool UseBarWidth;    // true = đường kính/độ dài = bề rộng nến (Absorption, HLine)
            public string Tooltip;
        }

        // key = chỉ số nến tuyệt đối (SeekOriginHistory.Begin, 0 = cũ nhất)
        private readonly Dictionary<int, List<Bubble>> _bubbles = new();
        private readonly Dictionary<int, int> _barTint = new();  // idx -> +1 (xanh) / -1 (đỏ)
        private readonly object _sync = new();       // bảo vệ _bubbles/_barTint (calc ghi, paint đọc)
        private readonly object _calcLock = new();   // serialize thread tính (OnUpdate vs VA_Loaded)

        // ===================== baseline ROBUST (median + MAD) =====================
        private RollingRobust _rLvlVol;       // per-level Volume
        private RollingRobust _rLvlAbsDelta;  // per-level |Delta|
        private RollingRobust _rLvlMot;       // per-level MaxOneTradeVolume (chỉ khi feed điền)
        private RollingRobust _rBarVol;       // per-bar Total.Volume
        private RollingRobust _rBarAbsDelta;  // per-bar |Total.Delta|

        private readonly List<double> _cvd = new();  // cumulative delta theo chỉ số tuyệt đối
        private int _processedClosedCount;
        private bool _vaLoaded;
        private int _lastDivPivot = int.MinValue;     // cooldown divergence

        // ================================================================
        //  INPUT PARAMETERS
        // ================================================================

        // ---------- Appearance ----------
        [InputParameter("Màu MUA (aggressor) – bubble", 1)]
        public Color BuyColor { get; set; } = Color.Cyan;

        [InputParameter("Màu BÁN (aggressor) – bubble", 2)]
        public Color SellColor { get; set; } = Color.OrangeRed;

        [InputParameter("Màu delta + (xanh)", 3)]
        public Color DeltaUpColor { get; set; } = Color.FromArgb(0x26, 0xA6, 0x9A);

        [InputParameter("Màu delta − (đỏ)", 4)]
        public Color DeltaDownColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);

        [InputParameter("Bubble nhỏ nhất (px)", 5, 2, 80, 1, 0)]
        public int MinBubbleSize { get; set; } = 8;

        [InputParameter("Bubble lớn nhất (px)", 6, 2, 120, 1, 0)]
        public int MaxBubbleSize { get; set; } = 26;

        [InputParameter("Độ trong halo Big Trade (0-100)", 7, 0, 100, 1, 0)]
        public int HaloTransparency { get; set; } = 55;

        [InputParameter("Độ trong bubble đặc (0-100)", 8, 0, 100, 1, 0)]
        public int SolidTransparency { get; set; } = 10;

        // ---------- Baseline (robust) ----------
        [InputParameter("Baseline · Số nến (rolling)", 10, 20, 500, 1, 0)]
        public int BaselineBars { get; set; } = 100;

        [InputParameter("Baseline · Số nến tối thiểu (warm-up)", 11, 5, 500, 1, 0)]
        public int MinBars { get; set; } = 40;

        [InputParameter("Baseline · Sàn volume/mức (absolute, chống nhiễu)", 12, 0, 1000000, 1, 0)]
        public double MinLevelVolFloor { get; set; } = 5;

        [InputParameter("Baseline · Sàn volume/nến (absolute, chống nhiễu)", 13, 0, 1000000, 1, 0)]
        public double MinBarVolFloor { get; set; } = 20;

        // ---------- Nến delta lớn (dominant-delta candle) ----------
        [InputParameter("Nến delta · Bật (tô thân nến)", 20)]
        public bool DeltaBarEnabled { get; set; } = true;

        [InputParameter("Nến delta · deltaPct tối thiểu (|Δ|/Vol)", 21, 0.0, 1.0, 0.01, 2)]
        public double DeltaPctFloor { get; set; } = 0.30;

        [InputParameter("Nến delta · |Δ| z-score ≥", 22, 0.0, 10.0, 0.1, 1)]
        public double DeltaBarSigZ { get; set; } = 3.0;

        [InputParameter("Nến delta · cổng volume (× median nến)", 23, 0.0, 5.0, 0.05, 2)]
        public double DeltaBarVolGate { get; set; } = 0.8;

        [InputParameter("Nến delta · độ đậm tô (0-100)", 24, 0, 100, 1, 0)]
        public int DeltaBarTintPct { get; set; } = 85;

        // ---------- Số Delta ----------
        [InputParameter("Số Delta · Hiện dưới nến", 30)]
        public bool ShowDeltaNumbers { get; set; } = true;

        [InputParameter("Số Delta · Cỡ chữ", 31, 6, 40, 1, 0)]
        public int DeltaFontSize { get; set; } = 11;

        [InputParameter("Số Delta · cách đáy nến (px)", 32, 0, 60, 1, 0)]
        public int DeltaYOffsetPx { get; set; } = 6;

        [InputParameter("Số Delta · chỉ vẽ khi bề rộng nến ≥ (px)", 33, 1, 100, 1, 0)]
        public int DeltaMinBarWidthPx { get; set; } = 6;

        [InputParameter("Số Delta · nền mờ sau chữ", 34)]
        public bool DeltaBackground { get; set; } = false;

        // ---------- 1) Absorption ----------
        [InputParameter("Absorption · Bật", 40)]
        public bool AbsorptionEnabled { get; set; } = true;

        [InputParameter("Absorption · Volume/mức z-score ≥", 41, 0.0, 12.0, 0.1, 1)]
        public double AbsZ { get; set; } = 4.0;

        [InputParameter("Absorption · Tỷ lệ 1 phe áp đảo ≥", 42, 0.5, 1.0, 0.05, 2)]
        public double AbsDom { get; set; } = 0.60;

        [InputParameter("Absorption · Cách cực trị tối đa (ticks)", 43, 0, 20, 1, 0)]
        public int AbsMaxDisplaceTicks { get; set; } = 2;

        [InputParameter("Absorption · số bubble mạnh nhất / nến", 44, 1, 10, 1, 0)]
        public int AbsorptionTopN { get; set; } = 1;

        // ---------- 2) Big Trade ----------
        [InputParameter("Big Trade · Bật", 50)]
        public bool BigTradeEnabled { get; set; } = true;

        [InputParameter("Big Trade · z-score ≥ (lệnh đơn / volume mức)", 51, 0.0, 12.0, 0.1, 1)]
        public double BigZ { get; set; } = 4.5;

        [InputParameter("Big Trade · số bubble mạnh nhất / nến", 52, 1, 10, 1, 0)]
        public int BigTradeTopN { get; set; } = 1;

        // ---------- 3) Big Delta profile (gạch ngang) ----------
        [InputParameter("Big Delta line · Bật", 60)]
        public bool DLineEnabled { get; set; } = true;

        [InputParameter("Big Delta line · deltaPct tối thiểu", 61, 0.0, 1.0, 0.01, 2)]
        public double DLineFloor { get; set; } = 0.35;

        [InputParameter("Big Delta line · |Δ mức| z-score ≥", 62, 0.0, 12.0, 0.1, 1)]
        public double DLineZ { get; set; } = 4.0;

        [InputParameter("Big Delta line · số mức mạnh nhất / nến", 63, 1, 10, 1, 0)]
        public int DLineTopN { get; set; } = 1;

        // ---------- 4) Exhaustion ----------
        [InputParameter("Exhaustion · Bật", 70)]
        public bool ExhaustionEnabled { get; set; } = false;

        [InputParameter("Exhaustion · Volume nến ≤ × nến trước", 71, 0.1, 1.5, 0.05, 2)]
        public double ExhVolFadeRatio { get; set; } = 0.65;

        [InputParameter("Exhaustion · Delta co ≤ × đỉnh intrabar", 72, 0.0, 1.0, 0.05, 2)]
        public double ExhDeltaFadeRatio { get; set; } = 0.40;

        [InputParameter("Exhaustion · Lookback đỉnh/đáy", 73, 1, 50, 1, 0)]
        public int ExhSwingLookback { get; set; } = 3;

        // ---------- 5) Stacked Imbalance ----------
        [InputParameter("Stacked Imbalance · Bật", 80)]
        public bool ImbalanceEnabled { get; set; } = false;

        [InputParameter("Stacked Imbalance · Tỷ lệ chéo % (300 = 3:1)", 81, 100, 2000, 10, 0)]
        public int ImbalanceRatioPct { get; set; } = 300;

        [InputParameter("Stacked Imbalance · Số mức liên tiếp", 82, 2, 20, 1, 0)]
        public int ImbalanceRun { get; set; } = 3;

        // ---------- 6) Delta Divergence ----------
        [InputParameter("Divergence · Bật", 90)]
        public bool DivergenceEnabled { get; set; } = false;

        [InputParameter("Divergence · Lookback swing", 91, 2, 50, 1, 0)]
        public int DivSwingLookback { get; set; } = 3;

        [InputParameter("Divergence · Volume pivot ≥ × median", 92, 0.5, 5.0, 0.1, 1)]
        public double DivVolPartic { get; set; } = 1.5;

        [InputParameter("Divergence · Cooldown (nến)", 93, 0, 50, 1, 0)]
        public int DivCooldown { get; set; } = 3;

        // ---------- 7) Liquidity Sweep ----------
        [InputParameter("Sweep · Bật", 100)]
        public bool SweepEnabled { get; set; } = false;

        [InputParameter("Sweep · Lookback swing", 101, 2, 50, 1, 0)]
        public int SweepLookback { get; set; } = 8;

        // ---------- 8) Unfinished Business ----------
        [InputParameter("Unfinished · Bật", 110)]
        public bool UnfinishedEnabled { get; set; } = false;

        // ---------- 9) Stop-hunt + Absorption ----------
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
            Description = "Footprint / order-flow signals (bubble). Ngưỡng tương đối (median+MAD) → portable mọi feed. Cần Volume Analysis.";
            SeparateWindow = false;
            InitBaselines();   // tránh null nếu OnUpdate chạy sớm
        }

        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            lock (_calcLock) { ResetState(); _vaLoaded = true; }   // khởi tạo baseline XONG mới bật cờ
            Process();
        }

        protected override void OnInit() { }

        protected override void OnClear()
        {
            lock (_calcLock) { _vaLoaded = false; ResetState(); }
        }

        private void InitBaselines()
        {
            _rLvlVol = new RollingRobust(BaselineBars);
            _rLvlAbsDelta = new RollingRobust(BaselineBars);
            _rLvlMot = new RollingRobust(BaselineBars);
            _rBarVol = new RollingRobust(BaselineBars);
            _rBarAbsDelta = new RollingRobust(BaselineBars);
        }

        private void ResetState()
        {
            lock (_sync) { _bubbles.Clear(); _barTint.Clear(); }
            InitBaselines();
            _cvd.Clear();
            _processedClosedCount = 0;
            _lastDivPivot = int.MinValue;
        }

        // ================================================================
        //  MAIN
        // ================================================================
        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaLoaded) return;
            var progress = HistoricalData.VolumeAnalysisCalculationProgress;
            if (progress == null || progress.State != VolumeAnalysisCalculationState.Finished) return;
            Process();
        }

        private void Process()
        {
            lock (_calcLock)
            {
                if (_rBarVol == null) return;
                double tick = Symbol?.TickSize ?? 0;
                if (tick <= 0) return;

                int total = HistoricalData.Count;
                if (total == 0) return;

                int closedCount = total - 1;               // trừ nến đang hình thành
                EnsureCvd(total);

                // (1) nến đóng chưa xử lý: tính tín hiệu (baseline TRƯỚC bar) rồi nạp baseline
                for (int i = _processedClosedCount; i < closedCount; i++)
                {
                    var bar = Bar(i);
                    if (bar == null) continue;
                    _cvd[i] = (i > 0 ? _cvd[i - 1] : 0.0) + BarDelta(bar);
                    bool ready = _rBarVol.BarCount >= MinBars;
                    ComputeBar(i, bar, tick, ready, isClosed: true);
                    AddToBaseline(bar);
                }
                if (closedCount > _processedClosedCount) _processedClosedCount = closedCount;

                // (2) nến đang hình thành — tính lại mỗi tick (idempotent)
                int cur = total - 1;
                var curBar = Bar(cur);
                if (curBar != null)
                {
                    _cvd[cur] = (cur > 0 ? _cvd[cur - 1] : 0.0) + BarDelta(curBar);
                    bool ready = _rBarVol.BarCount >= MinBars;
                    ComputeBar(cur, curBar, tick, ready, isClosed: false);
                }
            }
        }

        // ================================================================
        //  TÍNH TÍN HIỆU CHO 1 NẾN
        // ================================================================
        private void ComputeBar(int idx, HistoryItemBar bar, double tick, bool ready, bool isClosed)
        {
            var va = bar.VolumeAnalysisData;
            if (va == null || va.PriceLevels == null || va.PriceLevels.Count == 0)
            {
                lock (_sync) { _bubbles.Remove(idx); _barTint.Remove(idx); }
                return;
            }

            var list = new List<Bubble>();
            int tintSign = 0;

            double barVol = va.Total.Volume;
            double barDelta = va.Total.Delta;
            double barMaxDelta = va.Total.MaxDelta;   // delta chạy trong nến (đỉnh)
            double barMinDelta = va.Total.MinDelta;   // (đáy)

            // ---- (4) NẾN DELTA LỚN ----
            if (DeltaBarEnabled && ready)
            {
                double deltaPct = barVol > 0 ? barDelta / barVol : 0;
                double sig = _rBarAbsDelta.ModZ(Math.Abs(barDelta));
                if (barVol >= MinBarVolFloor && barVol >= _rBarVol.Median * DeltaBarVolGate
                    && Math.Abs(deltaPct) >= DeltaPctFloor && sig >= DeltaBarSigZ)
                    tintSign = barDelta > 0 ? 1 : -1;
            }

            // gom mức giá theo chỉ số tick + cực trị
            var byTick = new Dictionary<long, (double price, VolumeAnalysisItem it)>();
            double maxPosDelta = 0, maxPosPrice = bar.High;
            double minNegDelta = 0, minNegPrice = bar.Low;
            foreach (var kv in va.PriceLevels)
            {
                long k = (long)Math.Round(kv.Key / tick);
                byTick[k] = (kv.Key, kv.Value);
                var it = kv.Value;
                if (it.Delta > maxPosDelta) { maxPosDelta = it.Delta; maxPosPrice = kv.Key; }
                if (it.Delta < minNegDelta) { minNegDelta = it.Delta; minNegPrice = kv.Key; }
            }

            long loIdx = (long)Math.Round(bar.Low / tick);
            long hiIdx = (long)Math.Round(bar.High / tick);

            bool motReady = ready && _rLvlMot.BarCount > 0 && _rLvlMot.Median > 0;
            var dLineCands = new List<(double price, double z, int sign)>();
            var bigTradeCands = new List<(Bubble b, double z)>();
            var absCands = new List<(Bubble b, double z)>();
            int imbBuyRun = 0, imbSellRun = 0;
            double imbMinVol = Math.Max(MinLevelVolFloor, _rLvlVol.Median);

            for (long k = loIdx; k <= hiIdx; k++)
            {
                if (!byTick.TryGetValue(k, out var lvl)) { imbBuyRun = 0; imbSellRun = 0; continue; }
                double price = lvl.price;
                var it = lvl.it;
                double buy = it.BuyVolume, sell = it.SellVolume, vol = it.Volume;
                double dNet = buy - sell, sum = buy + sell;

                // 1) ABSORPTION — tròn ĐẶC cố định = nến, tại cực trị + bị chặn. Giữ TOP-N sau vòng lặp.
                if (AbsorptionEnabled && ready && vol >= MinLevelVolFloor && sum > 0)
                {
                    double volZ = _rLvlVol.ModZ(vol);
                    if (volZ >= AbsZ)
                    {
                        double buyDom = buy / sum, sellDom = sell / sum;
                        // buyDom sát ĐỈNH: mua chủ động nhưng bị nuốt (đóng cửa dưới đỉnh) → cyan, canh short
                        if (buyDom >= AbsDom && (bar.High - price) / tick <= AbsMaxDisplaceTicks
                            && (bar.High - bar.Close) >= tick)
                            absCands.Add((Solid(price, Shape.Ellipse, BuyColor, true,
                                $"Absorption đỉnh  vZ={volZ:0.0} buy={buyDom:P0}"), volZ));
                        // sellDom sát ĐÁY: bán chủ động bị nuốt (đóng cửa trên đáy) → đỏ, canh long
                        else if (sellDom >= AbsDom && (price - bar.Low) / tick <= AbsMaxDisplaceTicks
                            && (bar.Close - bar.Low) >= tick)
                            absCands.Add((Solid(price, Shape.Ellipse, SellColor, true,
                                $"Absorption đáy  vZ={volZ:0.0} sell={sellDom:P0}"), volZ));
                    }
                }

                // 2) BIG TRADE — tròn MỜ, scale theo lệnh ĐƠN lớn nhất (fallback volume/mức)
                if (BigTradeEnabled && ready)
                {
                    double metric; RollingRobust rr; string src;
                    if (motReady)
                    {
                        double mot = it.MaxOneTradeVolume;
                        if (mot > 0) { metric = mot; rr = _rLvlMot; src = "lệnh đơn"; }
                        else { metric = -1; rr = null; src = null; }
                    }
                    else { metric = vol; rr = _rLvlVol; src = "vol/mức"; }

                    if (rr != null && metric >= MinLevelVolFloor)
                    {
                        double z = rr.ModZ(metric);
                        if (z >= BigZ || metric >= 3 * rr.Median)
                            bigTradeCands.Add((new Bubble
                            {
                                Price = price, Shape = Shape.Ellipse, Color = AggColor(buy, sell),
                                Size = SizeFromMagnitude(z, BigZ), Transparency = HaloTransparency,
                                Halo = true, UseBarWidth = false,
                                Tooltip = $"Big trade ({src}) {metric:0}  z={z:0.0}"
                            }, z));
                    }
                }

                // 3) BIG DELTA line — ứng viên (giữ TOP-N sau vòng lặp)
                if (DLineEnabled && ready && vol >= MinLevelVolFloor)
                {
                    double dPct = vol > 0 ? dNet / vol : 0;
                    double z = _rLvlAbsDelta.ModZ(Math.Abs(dNet));
                    if (Math.Abs(dPct) >= DLineFloor && (z >= DLineZ || Math.Abs(dNet) >= 2 * _rLvlAbsDelta.Median))
                        dLineCands.Add((price, z, dNet > 0 ? 1 : -1));
                }

                // 5) STACKED IMBALANCE — chéo (buy[k] vs sell[k-1]), min-vol RELATIVE
                if (ImbalanceEnabled && ready && byTick.TryGetValue(k - 1, out var lo))
                {
                    double askFilter = lo.it.SellVolume * ImbalanceRatioPct / 100.0;
                    if (buy > askFilter && buy > imbMinVol) imbBuyRun++; else imbBuyRun = 0;
                    if (imbBuyRun >= ImbalanceRun)
                        list.Add(new Bubble
                        {
                            Price = price, Shape = Shape.Diamond, Color = BuyColor,
                            Size = SizeFromMagnitude(askFilter > 0 ? buy / askFilter : 1, 1),
                            Transparency = SolidTransparency, Tooltip = $"Stacked buy imbalance x{imbBuyRun}"
                        });

                    double bidFilter = buy * ImbalanceRatioPct / 100.0;
                    if (lo.it.SellVolume > bidFilter && lo.it.SellVolume > imbMinVol) imbSellRun++; else imbSellRun = 0;
                    if (imbSellRun >= ImbalanceRun)
                        list.Add(new Bubble
                        {
                            Price = lo.price, Shape = Shape.Diamond, Color = SellColor,
                            Size = SizeFromMagnitude(bidFilter > 0 ? lo.it.SellVolume / bidFilter : 1, 1),
                            Transparency = SolidTransparency, Tooltip = $"Stacked sell imbalance x{imbSellRun}"
                        });
                }

                // 8) UNFINISHED — đỉnh/đáy còn cả 2 phía (min-vol relative)
                if (UnfinishedEnabled)
                {
                    if (k == hiIdx && buy > MinLevelVolFloor && sell > MinLevelVolFloor)
                        list.Add(new Bubble { Price = bar.High, Shape = Shape.Rectangle, Color = SellColor, Size = MinBubbleSize, Transparency = SolidTransparency, Tooltip = "Unfinished (đỉnh)" });
                    if (k == loIdx && buy > MinLevelVolFloor && sell > MinLevelVolFloor)
                        list.Add(new Bubble { Price = bar.Low, Shape = Shape.Rectangle, Color = BuyColor, Size = MinBubbleSize, Transparency = SolidTransparency, Tooltip = "Unfinished (đáy)" });
                }
            }

            // Absorption: giữ TOP-N theo volume z (mỗi nến chỉ 1 bubble mạnh nhất → chart sạch)
            if (absCands.Count > 0)
                foreach (var c in absCands.OrderByDescending(x => x.z).Take(Math.Max(1, AbsorptionTopN)))
                    list.Add(c.b);

            // Big Trade: giữ TOP-N theo z (mỗi nến chỉ 1 bubble mạnh nhất → chart sạch)
            if (bigTradeCands.Count > 0)
                foreach (var c in bigTradeCands.OrderByDescending(x => x.z).Take(Math.Max(1, BigTradeTopN)))
                    list.Add(c.b);

            // Big Delta line: giữ TOP-N theo z
            if (dLineCands.Count > 0)
                foreach (var c in dLineCands.OrderByDescending(x => x.z).Take(Math.Max(1, DLineTopN)))
                    list.Add(new Bubble
                    {
                        Price = c.price, Shape = Shape.HLine,
                        Color = c.sign > 0 ? DeltaUpColor : DeltaDownColor,
                        Size = 2 + (int)Math.Clamp(c.z - DLineZ, 0, 4), Transparency = SolidTransparency,
                        UseBarWidth = true, Tooltip = $"Big delta {(c.sign > 0 ? "+" : "−")}  z={c.z:0.0}"
                    });

            // ---- detector theo NẾN ----
            if (ExhaustionEnabled) TryExhaustion(idx, bar, barVol, barDelta, barMaxDelta, barMinDelta, maxPosPrice, minNegPrice, list);
            if (SweepEnabled) TrySweep(idx, bar, barDelta, list);
            if (StopHuntEnabled && ready) TryStopHunt(idx, bar, tick, list);
            if (DivergenceEnabled && isClosed) TryDivergence(idx);

            lock (_sync)
            {
                if (list.Count > 0) _bubbles[idx] = list; else _bubbles.Remove(idx);
                if (tintSign != 0) _barTint[idx] = tintSign; else _barTint.Remove(idx);
            }
        }

        // ================================================================
        //  BAR-LEVEL DETECTORS
        // ================================================================

        // Exhaustion — dùng delta intrabar THẬT (Total.MaxDelta/MinDelta).
        private void TryExhaustion(int idx, HistoryItemBar cur, double curVol, double curDelta,
            double maxDelta, double minDelta, double maxPosPrice, double minNegPrice, List<Bubble> list)
        {
            if (idx < 1) return;
            var prev = Bar(idx - 1);
            if (prev == null) return;
            if (curVol >= PrevVol(prev) * ExhVolFadeRatio) return;   // volume phải teo lại

            int n = ExhSwingLookback;
            // buy exhaustion tại đỉnh: delta rút khỏi đỉnh intrabar
            if (IsLocalHigh(idx, n) && maxDelta > 0 && curDelta < maxDelta * ExhDeltaFadeRatio)
                list.Add(new Bubble { Price = maxPosPrice, Shape = Shape.Triangle, Color = BuyColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Buy exhaustion (đỉnh)" });
            // sell exhaustion tại đáy: delta hồi lên khỏi đáy intrabar
            if (IsLocalLow(idx, n) && minDelta < 0 && curDelta > minDelta * ExhDeltaFadeRatio)
                list.Add(new Bubble { Price = minNegPrice, Shape = Shape.Triangle, Color = SellColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Sell exhaustion (đáy)" });
        }

        // Divergence neo vào nến PIVOT = idx-n. Idempotent + cooldown + volume participation.
        private void TryDivergence(int idx)
        {
            int n = DivSwingLookback;
            if (idx < 2 * n) return;
            int pivot = idx - n;
            var c = Bar(pivot);
            if (c == null) return;
            if (pivot - _lastDivPivot < DivCooldown) return;

            double medVol = _rBarVol.Median;
            var divs = new List<Bubble>();
            if (IsPivotHigh(pivot, n) && ParticOk(pivot, medVol))
            {
                int prevPivot = FindPrevPivotHigh(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.High > pc.High && _cvd[pivot] <= _cvd[prevPivot])   // giá HH, delta LH
                        divs.Add(new Bubble { Price = c.High, Shape = Shape.Triangle, Color = BuyColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Bearish delta divergence" });
                }
            }
            if (IsPivotLow(pivot, n) && ParticOk(pivot, medVol))
            {
                int prevPivot = FindPrevPivotLow(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.Low < pc.Low && _cvd[pivot] >= _cvd[prevPivot])     // giá LL, delta HL
                        divs.Add(new Bubble { Price = c.Low, Shape = Shape.Triangle, Color = SellColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Bullish delta divergence" });
                }
            }

            if (divs.Count > 0) _lastDivPivot = pivot;

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

        private bool ParticOk(int idx, double medVol)
        {
            var b = Bar(idx);
            double v = b?.VolumeAnalysisData?.Total.Volume ?? 0;
            return medVol <= 0 || v >= DivVolPartic * medVol;
        }

        private void TrySweep(int idx, HistoryItemBar cur, double barDelta, List<Bubble> list)
        {
            if (idx < SweepLookback + 1) return;
            double hi = MaxHighPrior(idx, SweepLookback);
            double lo = MinLowPrior(idx, SweepLookback);
            if (cur.High > hi && cur.Close < hi && barDelta < 0)
                list.Add(new Bubble { Price = cur.High, Shape = Shape.Triangle, Color = BuyColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Liquidity sweep (đỉnh)" });
            if (cur.Low < lo && cur.Close > lo && barDelta > 0)
                list.Add(new Bubble { Price = cur.Low, Shape = Shape.Triangle, Color = SellColor, Size = MidSize(), Transparency = SolidTransparency, Tooltip = "Liquidity sweep (đáy)" });
        }

        private void TryStopHunt(int idx, HistoryItemBar cur, double tick, List<Bubble> list)
        {
            if (idx < StopHuntLookback + 1) return;
            var va = cur.VolumeAnalysisData;
            if (va == null || va.PriceLevels == null) return;

            double hi = MaxHighPrior(idx, StopHuntLookback);
            double lo = MinLowPrior(idx, StopHuntLookback);

            if (cur.High > hi && cur.Close < hi && TryLevel(va, cur.High, tick, out var itH))
            {
                double vz = _rLvlVol.ModZ(itH.Volume);
                if (vz >= AbsZ && itH.BuyVolume > itH.SellVolume)
                    list.Add(Solid(cur.High, Shape.Ellipse, SellColor, true, "Stop-hunt + absorption (đỉnh)"));
            }
            if (cur.Low < lo && cur.Close > lo && TryLevel(va, cur.Low, tick, out var itL))
            {
                double vz = _rLvlVol.ModZ(itL.Volume);
                if (vz >= AbsZ && itL.SellVolume > itL.BuyVolume)
                    list.Add(Solid(cur.Low, Shape.Ellipse, BuyColor, true, "Stop-hunt + absorption (đáy)"));
            }
        }

        // ================================================================
        //  RENDER
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
                int tintAlpha = (int)Math.Round(255 * Math.Clamp(DeltaBarTintPct, 0, 100) / 100.0);

                for (int i = li; i <= ri; i++)
                {
                    if (i < 0 || i >= HistoricalData.Count) continue;
                    if (HistoricalData[i, SeekOriginHistory.Begin] is not HistoryItemBar bar) continue;

                    float cx = (float)(conv.GetChartX(bar.TimeLeft) + barsW / 2.0);

                    // snapshot trong lock
                    List<Bubble> bubbles = null; int tint = 0;
                    lock (_sync)
                    {
                        if (_bubbles.TryGetValue(i, out var l)) bubbles = new List<Bubble>(l);
                        _barTint.TryGetValue(i, out tint);
                    }

                    // --- tô thân nến delta (nền, vẽ trước) ---
                    if (DeltaBarEnabled && tint != 0)
                    {
                        float yTop = (float)conv.GetChartY(Math.Max(bar.Open, bar.Close));
                        float yBot = (float)conv.GetChartY(Math.Min(bar.Open, bar.Close));
                        float h = Math.Max(1f, yBot - yTop);
                        float w = (float)Math.Max(1.0, barsW - 1);
                        using var tb = new SolidBrush(Color.FromArgb(tintAlpha, tint > 0 ? DeltaUpColor : DeltaDownColor));
                        gr.FillRectangle(tb, cx - w / 2f, yTop, w, h);
                    }

                    // --- bubbles ---
                    if (bubbles != null)
                    {
                        foreach (var b in bubbles)
                        {
                            float y = (float)conv.GetChartY(b.Price);
                            int drawSize = b.UseBarWidth ? Math.Clamp((int)Math.Round(barsW), MinBubbleSize, 400) : b.Size;
                            DrawShape(gr, b, cx, y, drawSize, (float)barsW);

                            if (hoverTip == null)
                            {
                                float dx = mouse.X - cx, dy = mouse.Y - y;
                                float r = Math.Max(drawSize / 2f, 6f);
                                if (dx * dx + dy * dy <= r * r) { hoverTip = b.Tooltip; hoverX = (int)cx; hoverY = (int)y; }
                            }
                        }
                    }

                    // --- số delta ---
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
                            using var db = new SolidBrush(d > 0 ? DeltaUpColor : d < 0 ? DeltaDownColor : Color.Gray);
                            gr.DrawString(text, deltaFont, db, cx, y, centerFmt);
                        }
                    }
                }

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

        private void DrawShape(Graphics gr, Bubble b, float cx, float cy, int size, float barsW)
        {
            int alpha = (int)Math.Round(255 * (100 - b.Transparency) / 100.0);
            alpha = Math.Clamp(alpha, 0, 255);

            if (b.Shape == Shape.HLine)
            {
                float len = Math.Max(6f, barsW - 1);
                using var pen = new Pen(Color.FromArgb(alpha, b.Color), Math.Max(2, b.Size));
                gr.DrawLine(pen, cx - len / 2f, cy, cx + len / 2f, cy);
                return;
            }

            var fillColor = Color.FromArgb(b.Halo ? Math.Min(alpha, 110) : alpha, b.Color);
            float r = size / 2f;
            using var fill = new SolidBrush(fillColor);
            switch (b.Shape)
            {
                case Shape.Ellipse: gr.FillEllipse(fill, cx - r, cy - r, size, size); break;
                case Shape.Rectangle: gr.FillRectangle(fill, cx - r, cy - r, size, size); break;
                case Shape.Triangle:
                    gr.FillPolygon(fill, new[] { new PointF(cx, cy - r), new PointF(cx - r, cy + r), new PointF(cx + r, cy + r) });
                    break;
                case Shape.Diamond:
                    gr.FillPolygon(fill, new[] { new PointF(cx, cy - r), new PointF(cx + r, cy), new PointF(cx, cy + r), new PointF(cx - r, cy) });
                    break;
            }

            if (b.Halo)
            {
                using var pen = new Pen(Color.FromArgb(alpha, b.Color), 2f);
                if (b.Shape == Shape.Ellipse) gr.DrawEllipse(pen, cx - r, cy - r, size, size);
                else if (b.Shape == Shape.Rectangle) gr.DrawRectangle(pen, cx - r, cy - r, size, size);
            }
        }

        // ================================================================
        //  HELPERS
        // ================================================================
        private Bubble Solid(double price, Shape shape, Color color, bool useBarWidth, string tip)
            => new Bubble { Price = price, Shape = shape, Color = color, Size = MidSize(), Transparency = SolidTransparency, Halo = false, UseBarWidth = useBarWidth, Tooltip = tip };

        private HistoryItemBar Bar(int absIdx)
            => (absIdx >= 0 && absIdx < HistoricalData.Count)
                ? HistoricalData[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;

        private static double BarDelta(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total.Delta ?? 0.0;
        private static double PrevVol(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total.Volume ?? 0.0;

        private Color AggColor(double buy, double sell) => buy >= sell ? BuyColor : SellColor;
        private int MidSize() => (MinBubbleSize + MaxBubbleSize) / 2;

        // nén sqrt (volume đuôi nặng): z từ zMin..zMin+6 → Min..Max px
        private int SizeFromMagnitude(double z, double zMin)
        {
            double t = Math.Sqrt(Math.Clamp((z - zMin) / 6.0, 0, 1));
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

        private void AddToBaseline(HistoryItemBar bar)
        {
            var va = bar.VolumeAnalysisData;
            if (va?.PriceLevels == null) return;

            var vols = new List<double>(); var ads = new List<double>(); var mots = new List<double>();
            foreach (var it in va.PriceLevels.Values)
            {
                vols.Add(it.Volume);
                ads.Add(Math.Abs(it.Delta));
                double m = it.MaxOneTradeVolume;
                if (m > 0) mots.Add(m);
            }
            _rLvlVol.AddBar(vols.ToArray());
            _rLvlAbsDelta.AddBar(ads.ToArray());
            if (mots.Count > 0) _rLvlMot.AddBar(mots.ToArray());
            _rBarVol.AddBar(new[] { va.Total.Volume });
            _rBarAbsDelta.AddBar(new[] { Math.Abs(va.Total.Delta) });
        }

        private void EnsureCvd(int total) { while (_cvd.Count < total) _cvd.Add(0.0); }

        // ----- swing helpers (causal, chỉ số tuyệt đối) -----
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

        // ================================================================
        //  ROLLING ROBUST BASELINE (median + MAD)
        //  Cửa sổ = N NẾN gần nhất; mỗi nến đóng góp 1 mảng giá trị (per-level) hoặc 1 giá trị
        //  (per-bar). median/MAD tính lười (cache) — chỉ tính lại khi có nến mới.
        // ================================================================
        private sealed class RollingRobust
        {
            private readonly Queue<double[]> _bars = new();
            private readonly int _window;
            private double _median, _mad;
            private bool _dirty = true;
            private int _valueCount;

            public RollingRobust(int window) { _window = Math.Max(1, window); }

            public int BarCount => _bars.Count;

            public void AddBar(double[] vals)
            {
                if (vals == null) vals = Array.Empty<double>();
                _bars.Enqueue(vals);
                _valueCount += vals.Length;
                while (_bars.Count > _window) { var d = _bars.Dequeue(); _valueCount -= d.Length; }
                _dirty = true;
            }

            private void Recompute()
            {
                _dirty = false;
                if (_valueCount == 0) { _median = 0; _mad = 0; return; }
                var all = new double[_valueCount];
                int k = 0;
                foreach (var arr in _bars) { Array.Copy(arr, 0, all, k, arr.Length); k += arr.Length; }
                Array.Sort(all);
                _median = Med(all);
                var dev = new double[all.Length];
                for (int i = 0; i < all.Length; i++) dev[i] = Math.Abs(all[i] - _median);
                Array.Sort(dev);
                _mad = Med(dev);
            }

            private static double Med(double[] s)
            {
                int len = s.Length;
                if (len <= 0) return 0;
                int mid = len / 2;
                return (len % 2 == 1) ? s[mid] : 0.5 * (s[mid - 1] + s[mid]);
            }

            public double Median { get { if (_dirty) Recompute(); return _median; } }

            public double ModZ(double x)
            {
                if (_dirty) Recompute();
                if (_mad > 1e-9) return 0.6745 * (x - _median) / _mad;   // modified z (robust)
                if (_median > 1e-9) return (x - _median) / _median;      // fallback khi MAD=0
                return 0;
            }
        }
    }
}
