// ============================================================================
//  DeltaIndicatorBase — khung chung của 2 indicator nến delta (xem DeltaCore.cs)
// ============================================================================
namespace AskBidDeltaIndicators
{
    using System;
    using System.Drawing;
    using AskBidDeltaCore;
    using AskBidDeltaFeed;
    using TradingPlatform.BusinessLayer;

    public abstract class DeltaIndicatorBase : Indicator, IVolumeAnalysisIndicator
    {
        [InputParameter("Màu nến delta + (buy thắng)", 1)]
        public Color UpColor { get; set; } = Color.FromArgb(0x33, 0x33, 0xFF);

        [InputParameter("Màu nến delta − (sell thắng)", 2)]
        public Color DownColor { get; set; } = Color.FromArgb(0x1A, 0x1A, 0x1A);

        [InputParameter("Độ rộng thân (× bề rộng nến)", 3, 0.1, 1.0, 0.05, 2)]
        public double BodyWidthFrac { get; set; } = 0.6;

        [InputParameter("Độ dày râu (px)", 4, 1, 6, 1, 0)]
        public int WickWidth { get; set; } = 1;

        [InputParameter("Hiện số delta trên nến (khi nến đủ rộng)", 5)]
        public bool ShowNumbers { get; set; } = true;

        [InputParameter("Dựng râu nến cũ từ tick lịch sử (vì Quantower không có đỉnh/đáy delta cho nến nạp lại)", 6)]
        public bool UseTicks { get; set; } = true;

        [InputParameter("Chỉ nạp tick cho N ngày gần nhất", 7, 1, 30, 1, 0)]
        public int MaxTickDays { get; set; } = 5;

        [InputParameter("Lệch giờ (UTC → local, giờ)", 9, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;

        protected readonly DeltaFeed Feed = new DeltaFeed();
        protected abstract bool PerBar { get; }
        protected abstract bool ResetDailyDefault { get; }
        protected virtual int ResetMinutesValue => 300;

        private const int SCALE_HI = 0;
        private const int SCALE_LO = 1;

        protected DeltaIndicatorBase() : base()
        {
            SeparateWindow = true;
            // 2 series trong suốt chỉ để cửa sổ tự canh trục Y theo đỉnh/đáy delta
            AddLineSeries("scale-hi (ẩn)", Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
            AddLineSeries("scale-lo (ẩn)", Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
            AddLineLevel(0.0, "Zero Line", Color.FromArgb(0x80, 0x80, 0x80), 1, LineStyle.Solid);
        }

        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            Feed.MarkDirty();
            Refresh(true);
        }

        protected override void OnClear() { Feed.Cancel(); }

        public override void Dispose() { try { Feed.Cancel(); } catch { } base.Dispose(); }

        protected override void OnUpdate(UpdateArgs args)
        {
            Refresh(false);
        }

        private void OnTickProgress()
        {
            try { CurrentChart?.RedrawBuffer(); } catch { }
        }

        private void Refresh(bool force)
        {
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            Feed.PerBar = PerBar;
            Feed.ResetDaily = ResetDailyDefault;
            Feed.ResetMinutes = ResetMinutesValue;
            Feed.TzHours = TzOffset;
            Feed.UseTicks = UseTicks;
            Feed.MaxTickDays = MaxTickDays;
            bool changed = Feed.Update(HistoricalData, Symbol, OnTickProgress, force);
            var chain = Feed.Chain;
            int n = chain.Length;
            int from = changed ? 0 : Math.Max(0, n - 3);
            for (int i = from; i < n; i++)
            {
                int off = Count - 1 - i;
                if (off < 0 || off >= Count) continue;
                var c = chain[i];
                double h = c.Empty ? c.Open : c.High, l = c.Empty ? c.Open : c.Low;
                SetValue(h, SCALE_HI, off);
                SetValue(l, SCALE_LO, off);
            }
        }

        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null) return;
            var win = CurrentChart.Windows[args.WindowIndex];
            if (win.IsMainWindow) return;                    // chỉ vẽ trong cửa sổ phụ của indicator
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            if (Feed.TicksChanged) Refresh(false);           // tick nền vừa nạp thêm → dựng lại chuỗi

            var conv = win.CoordinatesConverter;
            var gr = args.Graphics;
            var clip = win.ClientRectangle;
            double barsW = CurrentChart.BarsWidth;
            DateTime leftTime = conv.GetTime(clip.Left);
            DateTime rightTime = conv.GetTime(clip.Right);
            int li = (int)conv.GetBarIndex(leftTime);
            int ri = (int)Math.Ceiling(conv.GetBarIndex(rightTime));

            var prevClip = gr.ClipBounds;
            gr.SetClip(clip);
            try
            {
                DeltaFeed.Draw(gr, clip, Feed.Chain, li, ri, barsW,
                               t => conv.GetChartX(t), v => conv.GetChartY(v),
                               UpColor, DownColor, BodyWidthFrac, WickWidth, ShowNumbers);
            }
            finally { gr.SetClip(prevClip); }
        }
    }
}
