// ============================================================================
//  Ask/Bid Volume Difference Bars  —  cho QUANTOWER / Optimus Flow
// ============================================================================
//  Mô phỏng study "Ask/Bid Volume Difference Bars" (delta OHLC) trên Sierra
//  Chart của bạn: mỗi NẾN gốc → một NẾN DELTA trong cửa sổ phụ, dựng từ diễn
//  biến delta CHẠY TRONG nến (ask−bid tích luỹ nội bộ nến, reset đầu mỗi nến):
//
//     Open  ≈ 0            (delta chạy xuất phát từ 0 đầu nến)
//     High  = MaxDelta     (đỉnh delta chạy đạt được trong nến)
//     Low   = MinDelta     (đáy delta chạy)
//     Close = Delta        (delta cuối nến)
//
//  Vì delta chạy khởi điểm 0 nên Open = kẹp 0 vào [Low, High]:
//     • nến straddle 0        → Open = 0
//     • nến toàn âm (chưa hề dương) → Open = High (mép gần 0 nhất)   → nến ĐEN
//     • nến toàn dương             → Open = Low                      → nến TÍM
//  Đã đối chiếu số thật trong ảnh: NQ O0 H96 L-7 C57 (tím) & GC O-1 H-1 L-21
//  C-20 (đen) — công thức tái tạo đúng cả hai.
//
//  Màu: Close ≥ Open → TÍM (#7200FF, mua thắng);  Close < Open → ĐEN (bán thắng).
//  Cần Volume Analysis (footprint) để có Delta / MaxDelta / MinDelta.
//
//  Quantower KHÔNG có line-style "nến" → tự vẽ OHLC bằng GDI+ trong cửa sổ phụ.
//  Hai line-series TRONG SUỐT (scale-hi/lo) chỉ để cửa sổ tự canh trục Y đúng
//  theo dải High/Low của delta (nến vẽ tay bám đúng trục đó qua GetChartY).
// ============================================================================

using System;
using System.Drawing;
using TradingPlatform.BusinessLayer;

namespace AskBidDeltaBars
{
    public class AskBidDeltaBars : Indicator, IVolumeAnalysisIndicator
    {
        [InputParameter("Màu nến delta + (mua thắng)", 1)]
        public Color UpColor { get; set; } = Color.FromArgb(0x72, 0x00, 0xFF);   // tím

        [InputParameter("Màu nến delta − (bán thắng)", 2)]
        public Color DownColor { get; set; } = Color.FromArgb(0x1A, 0x1A, 0x1A); // đen

        [InputParameter("Độ rộng thân (× bề rộng nến)", 3, 0.1, 1.0, 0.05, 2)]
        public double BodyWidthFrac { get; set; } = 0.6;

        [InputParameter("Độ dày râu (px)", 4, 1, 6, 1, 0)]
        public int WickWidth { get; set; } = 1;

        private const int SCALE_HI = 0;
        private const int SCALE_LO = 1;
        private bool _vaReady;

        public AskBidDeltaBars() : base()
        {
            Name = "Ask/Bid Volume Difference Bars";
            Description = "Delta (ask−bid) dạng nến OHLC mỗi nến: Open≈0, High=đỉnh delta chạy, Low=đáy delta, Close=delta cuối. Tím=mua thắng, đen=bán thắng. Cần Volume Analysis.";
            SeparateWindow = true;

            // 2 series trong suốt (alpha 0): KHÔNG hiện, chỉ để auto-scale + trục Y đúng.
            AddLineSeries("scale-hi (ẩn)", Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
            AddLineSeries("scale-lo (ẩn)", Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
            AddLineLevel(0.0, "Zero Line", Color.FromArgb(0x80, 0x80, 0x80), 1, LineStyle.Solid);
        }

        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            _vaReady = true;
            for (int off = 0; off < Count; off++) SetScale(off);
        }

        protected override void OnClear() { _vaReady = false; }

        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaReady) return;
            var p = HistoricalData.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            SetScale(0);
        }

        private void SetScale(int offset)
        {
            if (TryOhlc(offset, out _, out double h, out double l, out _))
            {
                SetValue(h, SCALE_HI, offset);
                SetValue(l, SCALE_LO, offset);
            }
            else
            {
                SetValue(0.0, SCALE_HI, offset);
                SetValue(0.0, SCALE_LO, offset);
            }
        }

        // OHLC của delta cho nến ở 'offset' (0 = hiện tại). Dùng SeekOriginHistory.End.
        private bool TryOhlc(int offset, out double open, out double high, out double low, out double close)
        {
            open = high = low = close = 0.0;
            if (offset < 0 || offset >= Count) return false;
            var bar = HistoricalData[offset, SeekOriginHistory.End] as HistoryItemBar;
            var va = bar?.VolumeAnalysisData?.Total;
            if (va == null) return false;
            BuildOhlc(va.Delta, va.MaxDelta, va.MinDelta, out open, out high, out low, out close);
            return true;
        }

        // Tách riêng để dùng chung ở paint (đọc theo Begin).
        private static void BuildOhlc(double delta, double maxDelta, double minDelta,
                                      out double open, out double high, out double low, out double close)
        {
            close = delta;
            high = maxDelta;
            low = minDelta;
            if (high < low) { double t = high; high = low; low = t; }     // guard
            open = Math.Min(Math.Max(0.0, low), high);                    // kẹp 0 vào [low,high]
            high = Math.Max(high, Math.Max(open, close));                 // nến hợp lệ
            low = Math.Min(low, Math.Min(open, close));
        }

        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || !_vaReady) return;

            var win = CurrentChart.Windows[args.WindowIndex];
            if (win.IsMainWindow) return;                    // chỉ vẽ trong cửa sổ phụ của indicator
            var conv = win.CoordinatesConverter;
            var gr = args.Graphics;
            var clip = win.ClientRectangle;
            double barsW = CurrentChart.BarsWidth;
            float bodyW = (float)Math.Max(1.0, barsW * BodyWidthFrac);

            DateTime leftTime = conv.GetTime(clip.Left);
            DateTime rightTime = conv.GetTime(clip.Right);
            int li = (int)conv.GetBarIndex(leftTime);
            int ri = (int)Math.Ceiling(conv.GetBarIndex(rightTime));

            var prevClip = gr.ClipBounds;
            gr.SetClip(clip);
            try
            {
                for (int i = li; i <= ri; i++)
                {
                    if (i < 0 || i >= HistoricalData.Count) continue;
                    if (HistoricalData[i, SeekOriginHistory.Begin] is not HistoryItemBar bar) continue;
                    var va = bar.VolumeAnalysisData?.Total;
                    if (va == null) continue;

                    BuildOhlc(va.Delta, va.MaxDelta, va.MinDelta,
                              out double open, out double high, out double low, out double close);

                    float cx = (float)(conv.GetChartX(bar.TimeLeft) + barsW / 2.0);
                    float yO = (float)conv.GetChartY(open);
                    float yC = (float)conv.GetChartY(close);
                    float yH = (float)conv.GetChartY(high);
                    float yL = (float)conv.GetChartY(low);

                    bool up = close >= open;
                    Color col = up ? UpColor : DownColor;

                    using var pen = new Pen(col, Math.Max(1, WickWidth));
                    using var br = new SolidBrush(col);

                    gr.DrawLine(pen, cx, yH, cx, yL);        // râu (High↔Low)
                    float top = Math.Min(yO, yC);
                    float bot = Math.Max(yO, yC);
                    float h = Math.Max(1f, bot - top);
                    gr.FillRectangle(br, cx - bodyW / 2f, top, bodyW, h);   // thân (Open↔Close)
                }
            }
            finally { gr.SetClip(prevClip); }
        }
    }
}
