// ============================================================================
//  OrderFlow Bubbles  —  custom footprint / order-flow signal indicator for ATAS
// ============================================================================
//  Thiết kế: xem SPEC.md. Ý tưởng gốc từ một indicator bubble (Sierra Chart) của
//  bạn người dùng; đây là BẢN RIÊNG, ưu tiên tín hiệu LIMIT/HẤP THỤ (passive).
//
//  HỆ MÃ HOÁ 3 KÊNH (giữ chart dễ đọc — KHÔNG dùng màu để mã hoá loại tín hiệu):
//    • MÀU  = phe chủ động ở tín hiệu đó:  CYAN = phe MUA (ở đỉnh) · ĐỎ = phe BÁN (ở đáy).
//             Absorption/BigTrade/Surge: theo aggressor (Ask>Bid=cyan). Các tín hiệu ĐẢO ở
//             cực trị (Exhaustion/Divergence/Sweep): màu = phe vừa đẩy tạo cực trị → HÀNH ĐỘNG
//             NGƯỢC MÀU (cyan ở đỉnh = short, đỏ ở đáy = long). Nhất quán: đỉnh→cyan, đáy→đỏ.
//    • HÌNH = loại tín hiệu:    Ellipse / Triangle / Rectangle / Diamond (ATAS chỉ có 5 hình)
//    • SIZE = độ mạnh:          to = z-score / volume ratio lớn
//  Bubble neo theo PRICE-LEVEL trong footprint (nhiều bubble trên 1 nến).
//
//  AN TOÀN COMPILE: chỉ dùng API ATAS đã kiểm chứng (PriceSelectionValue,
//  GetPriceVolumeInfo, GetCandle, InstrumentInfo.TickSize, DataAnnotations).
//  KHÔNG dùng API tick chưa xác minh (OnNewTrades/CumulativeTrade/MarketDataArg)
//  -> iceberg & stop-hunt là XẤP XỈ từ dữ liệu level+bar. Xem README "Checklist rủi ro".
// ============================================================================

using System;
using System.Collections.Generic;
using System.ComponentModel;                     // DisplayName
using System.ComponentModel.DataAnnotations;     // Display, Range
using System.Windows.Media;                      // Colors  (ATAS color-picker type)
using ATAS.Indicators;
using OFT.Rendering.Context;                     // RenderContext (tham số OnRender)
using OFT.Rendering.Tools;                       // RenderFont + extension DrawString/MeasureString
using Color = System.Windows.Media.Color;        // KHOÁ 'Color' trần = Media.Color -> chống CS0104 khi trộn với System.Drawing.Color lúc vẽ

namespace OrderFlowBubbles
{
    [DisplayName("OrderFlow Bubbles")]
    public class OrderFlowBubbles : Indicator
    {
        // --- render series: mỗi bar chứa 1 danh sách PriceSelectionValue (bubble theo mức giá) ---
        private readonly PriceSelectionDataSeries _render = new("RenderDataSeries", "Price");

        // --- rolling baseline cho z-score (LOGIC CỦA MÌNH, không phải của ATAS) ---
        private int _lastClosedBar = -1;
        private readonly Queue<(decimal sum, decimal sumSq, int count)> _lvlWin = new();
        private decimal _lvlSum, _lvlSumSq;
        private long _lvlCount;
        private readonly Queue<decimal> _adWin = new();      // |bar delta| window
        private decimal _adSum, _adSumSq;

        // --- cumulative delta (dùng cho divergence) ---
        private readonly List<decimal> _cvd = new();

        // ================================================================
        //  SETTINGS
        // ================================================================

        // ---------- Appearance ----------
        [Display(Name = "Màu MUA (buy aggressor)", GroupName = "Appearance", Order = 1)]
        public Color BuyColor { get; set; } = Colors.Cyan;

        [Display(Name = "Màu BÁN (sell aggressor)", GroupName = "Appearance", Order = 2)]
        public Color SellColor { get; set; } = Colors.OrangeRed;

        [Display(Name = "Kích thước nhỏ nhất", GroupName = "Appearance", Order = 3)]
        [Range(2, 60)]
        public int MinBubbleSize { get; set; } = 6;

        [Display(Name = "Kích thước lớn nhất", GroupName = "Appearance", Order = 4)]
        [Range(2, 80)]
        public int MaxBubbleSize { get; set; } = 22;

        [Display(Name = "Độ trong 'halo' hấp thụ (0-100)", GroupName = "Appearance", Order = 5)]
        [Range(0, 100)]
        public int HaloTransparency { get; set; } = 55;

        [Display(Name = "Độ trong bubble đặc (0-100)", GroupName = "Appearance", Order = 6)]
        [Range(0, 100)]
        public int SolidTransparency { get; set; } = 10;

        // ---------- Delta Numbers (số delta dưới đáy nến — DEFAULT ON) ----------
        [Display(Name = "Hiện số Delta dưới nến", GroupName = "Delta Numbers", Order = 1)]
        public bool ShowDeltaNumbers { get; set; } = true;

        [Display(Name = "Cỡ chữ", GroupName = "Delta Numbers", Order = 2)]
        [Range(6, 40)]
        public int DeltaFontSize { get; set; } = 11;

        [Display(Name = "Font", GroupName = "Delta Numbers", Order = 3)]
        public string DeltaFontFamily { get; set; } = "Arial";

        [Display(Name = "Cách đáy nến (px)", GroupName = "Delta Numbers", Order = 4)]
        [Range(0, 60)]
        public int DeltaYOffsetPx { get; set; } = 4;

        [Display(Name = "Chỉ vẽ khi bề rộng nến ≥ (px)", GroupName = "Delta Numbers", Order = 5)]
        [Range(1, 100)]
        public int DeltaMinBarWidthPx { get; set; } = 6;

        [Display(Name = "Nền mờ sau chữ (dễ đọc)", GroupName = "Delta Numbers", Order = 6)]
        public bool DeltaBackground { get; set; } = false;

        [Display(Name = "Màu Delta dương (+)", GroupName = "Delta Numbers", Order = 7)]
        public Color DeltaPosColor { get; set; } = Color.FromRgb(0x3F, 0xB9, 0x50);   // xanh dịu

        [Display(Name = "Màu Delta âm (−)", GroupName = "Delta Numbers", Order = 8)]
        public Color DeltaNegColor { get; set; } = Color.FromRgb(0xF8, 0x51, 0x49);   // đỏ dịu

        // ---------- Baseline ----------
        [Display(Name = "Số nến baseline (rolling)", GroupName = "Baseline", Order = 1)]
        [Range(10, 500)]
        public int BaselineBars { get; set; } = 50;

        [Display(Name = "Mẫu tối thiểu trước khi báo", GroupName = "Baseline", Order = 2)]
        [Range(5, 5000)]
        public int MinSamples { get; set; } = 40;

        // ---------- Absorption (DEFAULT ON) ----------
        [Display(Name = "Bật", GroupName = "1) Absorption", Order = 1)]
        public bool AbsorptionEnabled { get; set; } = true;

        [Display(Name = "Volume z-score ≥", GroupName = "1) Absorption", Order = 2)]
        [Range(0.0, 10.0)]
        public decimal AbsorptionZ { get; set; } = 2.0m;

        [Display(Name = "Tỷ lệ 1 phe áp đảo ≥ (0-1)", GroupName = "1) Absorption", Order = 3)]
        [Range(0.5, 1.0)]
        public decimal AbsorptionImbalancePct { get; set; } = 0.60m;

        [Display(Name = "Giá dịch tối đa (ticks)", GroupName = "1) Absorption", Order = 4)]
        [Range(0, 20)]
        public int AbsorptionMaxDisplaceTicks { get; set; } = 2;

        // ---------- Exhaustion (DEFAULT ON) ----------
        [Display(Name = "Bật", GroupName = "2) Exhaustion", Order = 1)]
        public bool ExhaustionEnabled { get; set; } = true;

        [Display(Name = "Volume nến ≤ x lần nến trước", GroupName = "2) Exhaustion", Order = 2)]
        [Range(0.1, 1.5)]
        public decimal ExhVolFadeRatio { get; set; } = 0.6m;

        [Display(Name = "Delta co lại ≤ x lần đỉnh intrabar", GroupName = "2) Exhaustion", Order = 3)]
        [Range(0.0, 1.0)]
        public decimal ExhDeltaFadeRatio { get; set; } = 0.4m;

        [Display(Name = "Lookback đỉnh/đáy cục bộ", GroupName = "2) Exhaustion", Order = 4)]
        [Range(1, 50)]
        public int ExhSwingLookback { get; set; } = 5;

        // ---------- Stacked Imbalance (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "3) Stacked Imbalance", Order = 1)]
        public bool ImbalanceEnabled { get; set; } = false;

        [Display(Name = "Tỷ lệ chéo % (300 = 3:1)", GroupName = "3) Stacked Imbalance", Order = 2)]
        [Range(100, 2000)]
        public int ImbalanceRatioPct { get; set; } = 300;

        [Display(Name = "Volume tối thiểu mỗi mức", GroupName = "3) Stacked Imbalance", Order = 3)]
        [Range(1, 1000)]
        public int ImbalanceMinVolume { get; set; } = 15;

        [Display(Name = "Số mức liên tiếp (stacked)", GroupName = "3) Stacked Imbalance", Order = 4)]
        [Range(2, 20)]
        public int ImbalanceRun { get; set; } = 3;

        // ---------- Big Trade (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "4) Big Trade", Order = 1)]
        public bool BigTradeEnabled { get; set; } = false;

        [Display(Name = "Volume tối thiểu / mức", GroupName = "4) Big Trade", Order = 2)]
        [Range(1, 100000)]
        public decimal BigTradeMinVolume { get; set; } = 20m;

        [Display(Name = "Hoặc volume z-score ≥", GroupName = "4) Big Trade", Order = 3)]
        [Range(0.0, 10.0)]
        public decimal BigTradeZ { get; set; } = 2.5m;

        // ---------- Delta Surge (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "5) Delta Surge", Order = 1)]
        public bool DeltaSurgeEnabled { get; set; } = false;

        [Display(Name = "|Delta| z-score ≥", GroupName = "5) Delta Surge", Order = 2)]
        [Range(0.0, 10.0)]
        public decimal DeltaSurgeZ { get; set; } = 2.0m;

        // ---------- Delta Divergence (DEFAULT OFF, experimental) ----------
        [Display(Name = "Bật (thử nghiệm)", GroupName = "6) Delta Divergence", Order = 1)]
        public bool DivergenceEnabled { get; set; } = false;

        [Display(Name = "Lookback swing", GroupName = "6) Delta Divergence", Order = 2)]
        [Range(2, 50)]
        public int DivSwingLookback { get; set; } = 6;

        // ---------- Liquidity Sweep (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "7) Liquidity Sweep", Order = 1)]
        public bool SweepEnabled { get; set; } = false;

        [Display(Name = "Lookback swing", GroupName = "7) Liquidity Sweep", Order = 2)]
        [Range(2, 50)]
        public int SweepLookback { get; set; } = 8;

        // ---------- Unfinished Business (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "8) Unfinished Business", Order = 1)]
        public bool UnfinishedEnabled { get; set; } = false;

        // ---------- Iceberg proxy (DEFAULT OFF) ----------
        [Display(Name = "Bật (xấp xỉ)", GroupName = "9) Iceberg (proxy)", Order = 1)]
        public bool IcebergEnabled { get; set; } = false;

        [Display(Name = "Volume z-score ≥", GroupName = "9) Iceberg (proxy)", Order = 2)]
        [Range(0.0, 10.0)]
        public decimal IcebergZ { get; set; } = 2.5m;

        [Display(Name = "Số lần khớp (ticks) tối thiểu", GroupName = "9) Iceberg (proxy)", Order = 3)]
        [Range(1, 5000)]
        public int IcebergMinTicks { get; set; } = 25;

        // ---------- Stop-hunt + Absorption (DEFAULT OFF) ----------
        [Display(Name = "Bật", GroupName = "10) Stop-hunt + Absorption", Order = 1)]
        public bool StopHuntEnabled { get; set; } = false;

        [Display(Name = "Lookback swing", GroupName = "10) Stop-hunt + Absorption", Order = 2)]
        [Range(2, 50)]
        public int StopHuntLookback { get; set; } = 8;

        // ================================================================
        //  CTOR
        // ================================================================
        public OrderFlowBubbles() : base(true)
        {
            _render.IsHidden = true;
            DataSeries[0] = _render;   // thay series mặc định bằng series bubble (giống ClusterSearch)

            // === bật custom drawing để vẽ số Delta dưới nến (OnRender) ===
            EnableCustomDrawing = true;                     // BẮT BUỘC — thiếu dòng này OnRender KHÔNG chạy
            SubscribeToDrawingEvents(DrawingLayouts.Final); // vẽ lại mỗi lần chart render -> mượt khi kéo/zoom
        }

        protected override void OnRecalculate()
        {
            _lastClosedBar = -1;
            _lvlWin.Clear(); _lvlSum = _lvlSumSq = 0; _lvlCount = 0;
            _adWin.Clear(); _adSum = _adSumSq = 0;
            _cvd.Clear();
        }

        // ================================================================
        //  MAIN
        // ================================================================
        protected override void OnCalculate(int bar, decimal value)
        {
            var candle = GetCandle(bar);
            var tick = InstrumentInfo.TickSize;
            if (tick <= 0) return;

            // (1) cập nhật baseline cho MỌI nến vừa đóng (bar-1 trở về trước)
            for (var cb = _lastClosedBar + 1; cb <= bar - 1; cb++)
                AddBarToBaseline(cb, tick);
            if (bar - 1 > _lastClosedBar) _lastClosedBar = bar - 1;

            // (2) cumulative delta (cho divergence)
            EnsureCvd(bar);
            _cvd[bar] = (bar > 0 ? _cvd[bar - 1] : 0m) + candle.Delta;

            // (3) vẽ lại nến hiện tại (idempotent — nến đang hình thành gọi lại mỗi tick)
            _render[bar].Clear();

            var ready = _lvlCount >= MinSamples && LvlStd() > 0;

            // ---- Detector theo TỪNG MỨC GIÁ (1 vòng lặp) ----
            var imbBuyRun = 0;
            var imbSellRun = 0;
            for (var price = candle.Low; price <= candle.High + tick / 2m; price += tick)
            {
                var lvl = candle.GetPriceVolumeInfo(price);
                if (lvl == null) { imbBuyRun = 0; imbSellRun = 0; continue; }

                var total = lvl.Ask + lvl.Bid;
                var volZ = ready ? (lvl.Volume - LvlMean()) / LvlStd() : 0m;

                // 1) ABSORPTION
                if (AbsorptionEnabled && ready && volZ >= AbsorptionZ && total > 0)
                {
                    var buyDom = lvl.Ask / total;
                    var sellDom = lvl.Bid / total;
                    if (buyDom >= AbsorptionImbalancePct &&
                        (candle.High - lvl.Price) / tick <= AbsorptionMaxDisplaceTicks)
                        AddBubble(bar, lvl.Price, ObjectType.Ellipse, BuyColor,
                            SizeFromZ(volZ, AbsorptionZ), HaloTransparency, SelectionType.Ask,
                            $"Buy absorption  vZ={volZ:0.0}");
                    else if (sellDom >= AbsorptionImbalancePct &&
                        (lvl.Price - candle.Low) / tick <= AbsorptionMaxDisplaceTicks)
                        AddBubble(bar, lvl.Price, ObjectType.Ellipse, SellColor,
                            SizeFromZ(volZ, AbsorptionZ), HaloTransparency, SelectionType.Bid,
                            $"Sell absorption  vZ={volZ:0.0}");
                }

                // 3) STACKED IMBALANCE (công thức chéo đã kiểm chứng từ StackedImbalance.cs)
                if (ImbalanceEnabled)
                {
                    var lo = candle.GetPriceVolumeInfo(price - tick);
                    if (lo != null)
                    {
                        // buy imbalance: Ask ở mức trên vs Bid ở mức dưới
                        var askFilter = lo.Bid * ImbalanceRatioPct / 100m;
                        if (lvl.Ask > askFilter && lvl.Ask > ImbalanceMinVolume) imbBuyRun++; else imbBuyRun = 0;
                        if (imbBuyRun >= ImbalanceRun)
                            AddBubble(bar, lvl.Price, ObjectType.Diamond, BuyColor,
                                SizeFromRatio(askFilter > 0 ? lvl.Ask / askFilter : 1m), SolidTransparency,
                                SelectionType.Ask, $"Stacked buy imbalance x{imbBuyRun}");

                        // sell imbalance: Bid ở mức dưới vs Ask ở mức trên (đối xứng)
                        var bidFilter = lvl.Ask * ImbalanceRatioPct / 100m;
                        if (lo.Bid > bidFilter && lo.Bid > ImbalanceMinVolume) imbSellRun++; else imbSellRun = 0;
                        if (imbSellRun >= ImbalanceRun)
                            AddBubble(bar, lo.Price, ObjectType.Diamond, SellColor,
                                SizeFromRatio(bidFilter > 0 ? lo.Bid / bidFilter : 1m), SolidTransparency,
                                SelectionType.Bid, $"Stacked sell imbalance x{imbSellRun}");
                    }
                }

                // 4) BIG TRADE (fallback per-level đã kiểm chứng)
                if (BigTradeEnabled && (lvl.Volume >= BigTradeMinVolume || (ready && volZ >= BigTradeZ)))
                    AddBubble(bar, lvl.Price, ObjectType.Ellipse, AggColor(lvl.Ask, lvl.Bid),
                        SizeFromZ(ready ? volZ : BigTradeZ, 0m), SolidTransparency,
                        SelSide(lvl.Ask, lvl.Bid), $"Big print  vol={lvl.Volume:0}");

                // 9) ICEBERG proxy: volume z cao + nhiều ticks + giá KHÔNG phá qua mức
                if (IcebergEnabled && ready && volZ >= IcebergZ && lvl.Ticks >= IcebergMinTicks
                    && price > candle.Low && price < candle.High)
                    AddBubble(bar, lvl.Price, ObjectType.Rectangle, AggColor(lvl.Ask, lvl.Bid),
                        SizeFromZ(volZ, IcebergZ), SolidTransparency, SelSide(lvl.Ask, lvl.Bid),
                        $"Iceberg proxy  vol={lvl.Volume:0} ticks={lvl.Ticks}");

                // 8) UNFINISHED BUSINESS: chỉ tại đỉnh/đáy nến
                if (UnfinishedEnabled)
                {
                    if (Math.Abs(price - candle.High) < tick / 2m && lvl.Bid > 0)
                        AddBubble(bar, candle.High, ObjectType.Rectangle, SellColor,
                            MinBubbleSize, SolidTransparency, SelectionType.Bid, "Unfinished business (high)");
                    if (Math.Abs(price - candle.Low) < tick / 2m && lvl.Ask > 0)
                        AddBubble(bar, candle.Low, ObjectType.Rectangle, BuyColor,
                            MinBubbleSize, SolidTransparency, SelectionType.Ask, "Unfinished business (low)");
                }
            }

            // ---- Detector theo NẾN (aggregate) ----
            if (ExhaustionEnabled) TryExhaustion(bar, candle);
            if (DeltaSurgeEnabled && ready) TryDeltaSurge(bar, candle);
            if (DivergenceEnabled) TryDivergence(bar);
            if (SweepEnabled) TrySweep(bar, candle);
            if (StopHuntEnabled) TryStopHunt(bar, candle);
        }

        // ================================================================
        //  CUSTOM RENDER — số Delta dưới đáy mỗi nến (dưới râu nến nếu có râu)
        //  Dùng đường vẽ pixel (OnRender) — khác đường bubble (PriceSelectionValue).
        //  DrawString đòi System.Drawing.Color -> phải fully-qualify, KHÔNG 'using System.Drawing;'.
        // ================================================================
        protected override void OnRender(RenderContext context, DrawingLayouts layout)
        {
            if (!ShowDeltaNumbers) return;
            if (ChartInfo == null) return;                       // ChartInfo là IChart? (nullable) -> guard bắt buộc

            var container = ChartInfo.PriceChartContainer;
            if (container == null) return;
            if ((int)container.BarsWidth < DeltaMinBarWidthPx) return;   // nến quá hẹp -> bỏ (tránh rối + đỡ tốn)

            var region = container.Region;                       // System.Drawing.Rectangle (vùng vẽ giá)
            var font = new RenderFont(DeltaFontFamily, DeltaFontSize);

            // chỉ vẽ bar đang hiển thị; clamp phòng biên
            var first = Math.Max(FirstVisibleBarNumber, 0);
            var last = Math.Min(LastVisibleBarNumber, CurrentBar);

            for (var bar = first; bar <= last; bar++)
            {
                var candle = GetCandle(bar);

                var centerX = container.GetXByBar(bar, false);           // false = GIỮA bar
                var lowY = container.GetYByPrice(candle.Low, false);     // false = giữa price-level; LUÔN truyền bool
                var y = lowY + DeltaYOffsetPx;                           // Y tăng xuống dưới => cộng = dưới đáy wick

                var text = candle.Delta.ToString("+0;-0;0");             // dấu rõ (+/−/0)

                var size = context.MeasureString(text, font);           // var: type có thể Size hoặc SizeF -> KHÔNG khai báo cứng
                var w = (int)size.Width;
                var h = (int)size.Height;
                var x = centerX - w / 2;                                 // căn giữa ngang (DrawString neo góc trên-trái)

                // clip: bỏ nếu rơi ngoài vùng vẽ
                if (y > region.Bottom) continue;
                if (x + w < region.Left || x > region.Right) continue;

                if (DeltaBackground)
                    context.FillRectangle(System.Drawing.Color.FromArgb(120, 0, 0, 0),
                        new System.Drawing.Rectangle(x - 1, y, w + 2, h));

                context.DrawString(text, font, DeltaColor(candle.Delta), x, y);
            }
        }

        // Media.Color -> System.Drawing.Color (an toàn 100%, không phụ thuộc extension .Convert())
        private static System.Drawing.Color ToDrawing(Color c)          // Color = Media.Color (alias)
            => System.Drawing.Color.FromArgb(c.A, c.R, c.G, c.B);

        private System.Drawing.Color DeltaColor(decimal d)
        {
            if (d > 0) return ToDrawing(DeltaPosColor);
            if (d < 0) return ToDrawing(DeltaNegColor);
            return System.Drawing.Color.Gray;
        }

        // ================================================================
        //  BAR-LEVEL DETECTORS
        // ================================================================
        private void TryExhaustion(int bar, IndicatorCandle cur)
        {
            if (bar < 1) return;
            var prev = GetCandle(bar - 1);
            if (cur.Volume >= prev.Volume * ExhVolFadeRatio) return;   // volume phải teo lại

            // buy exhaustion tại đỉnh cục bộ: delta rút khỏi đỉnh intrabar
            if (IsLocalHigh(bar, ExhSwingLookback) && cur.MaxDelta > 0
                && cur.Delta < cur.MaxDelta * ExhDeltaFadeRatio)
            {
                var p = cur.MaxPositiveDeltaPriceInfo?.Price ?? cur.High;
                AddBubble(bar, p, ObjectType.Triangle, BuyColor,
                    MidSize(), SolidTransparency, SelectionType.Full, "Buy exhaustion");
            }
            // sell exhaustion tại đáy cục bộ: delta hồi lên khỏi đáy intrabar
            if (IsLocalLow(bar, ExhSwingLookback) && cur.MinDelta < 0
                && cur.Delta > cur.MinDelta * ExhDeltaFadeRatio)
            {
                var p = cur.MaxNegativeDeltaPriceInfo?.Price ?? cur.Low;
                AddBubble(bar, p, ObjectType.Triangle, SellColor,
                    MidSize(), SolidTransparency, SelectionType.Full, "Sell exhaustion");
            }
        }

        private void TryDeltaSurge(int bar, IndicatorCandle cur)
        {
            var std = AdStd();
            if (std <= 0) return;
            var dZ = (Math.Abs(cur.Delta) - AdMean()) / std;
            if (dZ < DeltaSurgeZ) return;
            var p = cur.MaxVolumePriceInfo?.Price ?? cur.Close;
            AddBubble(bar, p, ObjectType.Ellipse, cur.Delta > 0 ? BuyColor : SellColor,
                SizeFromZ(dZ, DeltaSurgeZ), SolidTransparency,
                cur.Delta > 0 ? SelectionType.Ask : SelectionType.Bid, $"Delta surge {cur.Delta:0}");
        }

        private void TryDivergence(int bar)
        {
            var n = DivSwingLookback;
            if (bar < 2 * n) return;
            var c = GetCandle(bar - n);   // pivot 2 phía tại bar-n
            if (IsPivotHigh(bar - n, n))
            {
                var prevPivot = FindPrevPivotHigh(bar - n - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = GetCandle(prevPivot);
                    if (c.High > pc.High && _cvd[bar - n] <= _cvd[prevPivot])   // giá HH, delta LH
                        AddBubble(bar - n, c.High, ObjectType.Triangle, BuyColor,
                            MidSize(), SolidTransparency, SelectionType.Full, "Bearish delta divergence");
                }
            }
            if (IsPivotLow(bar - n, n))
            {
                var prevPivot = FindPrevPivotLow(bar - n - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = GetCandle(prevPivot);
                    if (c.Low < pc.Low && _cvd[bar - n] >= _cvd[prevPivot])     // giá LL, delta HL
                        AddBubble(bar - n, c.Low, ObjectType.Triangle, SellColor,
                            MidSize(), SolidTransparency, SelectionType.Full, "Bullish delta divergence");
                }
            }
        }

        private void TrySweep(int bar, IndicatorCandle cur)
        {
            if (bar < SweepLookback + 1) return;
            var hi = MaxHighPrior(bar, SweepLookback);
            var lo = MinLowPrior(bar, SweepLookback);
            if (cur.High > hi && cur.Close < hi && cur.Delta < 0)
                AddBubble(bar, cur.High, ObjectType.Triangle, BuyColor,
                    MidSize(), SolidTransparency, SelectionType.Full, "Liquidity sweep (highs)");
            if (cur.Low < lo && cur.Close > lo && cur.Delta > 0)
                AddBubble(bar, cur.Low, ObjectType.Triangle, SellColor,
                    MidSize(), SolidTransparency, SelectionType.Full, "Liquidity sweep (lows)");
        }

        private void TryStopHunt(int bar, IndicatorCandle cur)
        {
            if (bar < StopHuntLookback + 1) return;
            if (_lvlCount < MinSamples || LvlStd() <= 0) return;
            var hi = MaxHighPrior(bar, StopHuntLookback);
            var lo = MinLowPrior(bar, StopHuntLookback);

            if (cur.High > hi && cur.Close < hi)   // quét trên rồi đóng cửa lại dưới
            {
                var lvl = cur.GetPriceVolumeInfo(cur.High);
                if (lvl != null && (lvl.Volume - LvlMean()) / LvlStd() >= AbsorptionZ && lvl.Bid > lvl.Ask)
                    AddBubble(bar, cur.High, ObjectType.Ellipse, SellColor,
                        MaxBubbleSize, HaloTransparency, SelectionType.Bid, "Stop-hunt + sell absorption");
            }
            if (cur.Low < lo && cur.Close > lo)
            {
                var lvl = cur.GetPriceVolumeInfo(cur.Low);
                if (lvl != null && (lvl.Volume - LvlMean()) / LvlStd() >= AbsorptionZ && lvl.Ask > lvl.Bid)
                    AddBubble(bar, cur.Low, ObjectType.Ellipse, BuyColor,
                        MaxBubbleSize, HaloTransparency, SelectionType.Ask, "Stop-hunt + buy absorption");
            }
        }

        // ================================================================
        //  HELPERS
        // ================================================================
        private void AddBubble(int bar, decimal price, ObjectType shape,
            Color color, int size, int transparency, SelectionType side, string tooltip)
        {
            _render[bar].Add(new PriceSelectionValue(price)
            {
                VisualObject = shape,
                ObjectColor = color,             // Color -> CrossColor (implicit trong ATAS). Xem README nếu lỗi.
                Size = size,
                ObjectsTransparency = transparency,
                SelectionSide = side,
                MinimumPrice = price,
                MaximumPrice = price,
                Tooltip = tooltip
            });
        }

        private Color AggColor(decimal ask, decimal bid) => ask >= bid ? BuyColor : SellColor;
        private static SelectionType SelSide(decimal ask, decimal bid) => ask >= bid ? SelectionType.Ask : SelectionType.Bid;

        private int MidSize() => (MinBubbleSize + MaxBubbleSize) / 2;

        private int SizeFromZ(decimal z, decimal zMin)
        {
            var t = (double)((z - zMin) / 4m);
            t = Math.Clamp(t, 0, 1);
            return (int)Math.Round(MinBubbleSize + t * (MaxBubbleSize - MinBubbleSize));
        }

        private int SizeFromRatio(decimal ratio)   // ratio quanh 1..5
        {
            var t = Math.Clamp((double)((ratio - 1m) / 4m), 0, 1);
            return (int)Math.Round(MinBubbleSize + t * (MaxBubbleSize - MinBubbleSize));
        }

        // ----- rolling baseline math -----
        private void AddBarToBaseline(int cb, decimal tick)
        {
            if (cb < 0) return;
            var c = GetCandle(cb);

            decimal sum = 0, sumSq = 0; int count = 0;
            for (var price = c.Low; price <= c.High + tick / 2m; price += tick)
            {
                var lvl = c.GetPriceVolumeInfo(price);
                if (lvl == null) continue;
                sum += lvl.Volume; sumSq += lvl.Volume * lvl.Volume; count++;
            }
            _lvlWin.Enqueue((sum, sumSq, count));
            _lvlSum += sum; _lvlSumSq += sumSq; _lvlCount += count;
            while (_lvlWin.Count > BaselineBars)
            {
                var (s, sq, n) = _lvlWin.Dequeue();
                _lvlSum -= s; _lvlSumSq -= sq; _lvlCount -= n;
            }

            var ad = Math.Abs(c.Delta);
            _adWin.Enqueue(ad); _adSum += ad; _adSumSq += ad * ad;
            while (_adWin.Count > BaselineBars)
            {
                var d = _adWin.Dequeue(); _adSum -= d; _adSumSq -= d * d;
            }
        }

        private decimal LvlMean() => _lvlCount > 0 ? _lvlSum / _lvlCount : 0m;
        private decimal LvlStd()
        {
            if (_lvlCount < 2) return 0m;
            var mean = LvlMean();
            var var0 = _lvlSumSq / _lvlCount - mean * mean;
            return var0 > 0 ? (decimal)Math.Sqrt((double)var0) : 0m;
        }
        private decimal AdMean() => _adWin.Count > 0 ? _adSum / _adWin.Count : 0m;
        private decimal AdStd()
        {
            if (_adWin.Count < 2) return 0m;
            var mean = AdMean();
            var var0 = _adSumSq / _adWin.Count - mean * mean;
            return var0 > 0 ? (decimal)Math.Sqrt((double)var0) : 0m;
        }

        private void EnsureCvd(int bar)
        {
            while (_cvd.Count <= bar) _cvd.Add(0m);
        }

        // ----- swing helpers (causal) -----
        private decimal MaxHighPrior(int bar, int n)
        {
            var m = decimal.MinValue;
            for (var i = 1; i <= n && bar - i >= 0; i++) m = Math.Max(m, GetCandle(bar - i).High);
            return m;
        }
        private decimal MinLowPrior(int bar, int n)
        {
            var m = decimal.MaxValue;
            for (var i = 1; i <= n && bar - i >= 0; i++) m = Math.Min(m, GetCandle(bar - i).Low);
            return m;
        }
        private bool IsLocalHigh(int bar, int n) => bar >= n && GetCandle(bar).High >= MaxHighPrior(bar, n);
        private bool IsLocalLow(int bar, int n) => bar >= n && GetCandle(bar).Low <= MinLowPrior(bar, n);

        private bool IsPivotHigh(int bar, int n)
        {
            if (bar - n < 0 || bar + n > CurrentBar) return false;
            var h = GetCandle(bar).High;
            for (var i = 1; i <= n; i++)
                if (GetCandle(bar - i).High > h || GetCandle(bar + i).High > h) return false;
            return true;
        }
        private bool IsPivotLow(int bar, int n)
        {
            if (bar - n < 0 || bar + n > CurrentBar) return false;
            var l = GetCandle(bar).Low;
            for (var i = 1; i <= n; i++)
                if (GetCandle(bar - i).Low < l || GetCandle(bar + i).Low < l) return false;
            return true;
        }
        private int FindPrevPivotHigh(int fromBar, int n)
        {
            for (var b = fromBar; b - n >= 0; b--) if (IsPivotHigh(b, n)) return b;
            return -1;
        }
        private int FindPrevPivotLow(int fromBar, int n)
        {
            for (var b = fromBar; b - n >= 0; b--) if (IsPivotLow(b, n)) return b;
            return -1;
        }
    }
}
