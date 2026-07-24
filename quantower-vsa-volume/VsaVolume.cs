// ============================================================================
//  VSA Volume  —  histogram volume TÔ MÀU THEO BẬC (VSA / Wyckoff) cho QUANTOWER
// ============================================================================
//  Mô phỏng 1:1 indicator "VSA Wyckoff Volume" trên TradingView: mỗi cột volume
//  được tô màu theo TỈ LỆ volume nến đó so với TRUNG BÌNH N nến gần nhất (SMA,
//  gồm cả nến hiện tại — giống ta.sma(volume, length)). Nhìn phát ra ngay
//  climax / rất cao / cao / bình thường / thấp / rất thấp.
//
//  Chỉ dùng bar.Volume → KHÔNG cần Volume Analysis (footprint) → chạy được cả
//  khi feed thiếu tick lịch sử.
//
//  RENDER: tự vẽ cột bằng GDI+ trong cửa sổ phụ (giống Ask/Bid Bars) → cột GIÃN
//  NGANG theo bề rộng nến khi zoom, thay vì cột cố định 4 px của LineStyle.
//  Histogramm. 2 line-series TRONG SUỐT (scale/baseline) chỉ để cửa sổ tự canh
//  trục Y đúng dải [0 … max volume]; cột vẽ tay bám trục đó qua GetChartY.
//
//  BẬC (mặc định = đúng config user gửi từ TradingView, × trung bình 20 nến):
//     ≥ 2.2  Ultra High (climax)  → magenta/fuchsia
//     ≥ 1.8  Very High            → đỏ
//     ≥ 1.2  High                 → cam
//     ≥ 0.8  Normal               → xanh lá
//     ≥ 0.4  Low                  → xanh dương (sky)
//     < 0.4  Very Low             → xám
//  Màu từng bậc + độ rộng cột chỉnh trực tiếp trong Settings (không cần build lại).
// ============================================================================

using System;
using System.Drawing;
using TradingPlatform.BusinessLayer;

namespace VsaVolume
{
    public class VsaVolume : Indicator
    {
        private const int TIERS = 6;

        // ------- Inputs: ngưỡng (khớp nhãn + mặc định TradingView) -------
        [InputParameter("Chu kỳ trung bình volume (số nến)", 10, 2, 2000, 1, 0)]
        public int Period { get; set; } = 20;

        [InputParameter("Ultra High (climax) ≥ (× TB)", 20, 0.05, 50, 0.05, 2)]
        public double RUltraHigh { get; set; } = 2.2;

        [InputParameter("Very High ≥ (× TB)", 21, 0.05, 50, 0.05, 2)]
        public double RVeryHigh { get; set; } = 1.8;

        [InputParameter("High ≥ (× TB)", 22, 0.05, 50, 0.05, 2)]
        public double RHigh { get; set; } = 1.2;

        [InputParameter("Normal ≥ (× TB)", 23, 0.05, 50, 0.05, 2)]
        public double RNormal { get; set; } = 0.8;

        [InputParameter("Low ≥ (× TB)  (dưới mốc này = Very Low)", 24, 0.05, 50, 0.05, 2)]
        public double RLow { get; set; } = 0.4;

        // ------- Inputs: độ rộng cột + màu 6 bậc (đổi ngay trong Settings) -------
        [InputParameter("Độ rộng cột (× bề rộng nến)", 30, 0.1, 1.0, 0.05, 2)]
        public double BarWidthFrac { get; set; } = 0.7;

        [InputParameter("Màu · Ultra High (climax)", 40)]
        public Color CUltraHigh { get; set; } = Color.FromArgb(0xD5, 0x00, 0xF9); // magenta/fuchsia

        [InputParameter("Màu · Very High", 41)]
        public Color CVeryHigh { get; set; } = Color.FromArgb(0xF4, 0x43, 0x36); // đỏ

        [InputParameter("Màu · High", 42)]
        public Color CHigh { get; set; } = Color.FromArgb(0xFF, 0x98, 0x00); // cam

        [InputParameter("Màu · Normal", 43)]
        public Color CNormal { get; set; } = Color.FromArgb(0x4C, 0xAF, 0x50); // xanh lá

        [InputParameter("Màu · Low", 44)]
        public Color CLow { get; set; } = Color.FromArgb(0x42, 0xA5, 0xF5); // xanh dương (sky)

        [InputParameter("Màu · Very Low", 45)]
        public Color CVeryLow { get; set; } = Color.FromArgb(0xB0, 0xBE, 0xC5); // xám

        private const int SCALE_MAX = 0;   // series ẩn: mang volume nến → kéo trục Y tới max
        private const int SCALE_ZERO = 1;  // series ẩn: mang 0        → ép baseline 0 vào trục

        public VsaVolume() : base()
        {
            Name = "VSA Volume";
            Description = "Volume tô màu theo bậc (VSA/Wyckoff): tỉ lệ volume nến / SMA N nến. 6 bậc màu, cột tự vẽ giãn ngang theo nến. Không cần Volume Analysis.";
            SeparateWindow = true;

            // 2 series trong suốt (alpha 0): KHÔNG hiện, chỉ để auto-scale trục Y = [0..maxVol].
            AddLineSeries("scale (ẩn)",    Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
            AddLineSeries("baseline (ẩn)", Color.FromArgb(0, 0, 0, 0), 1, LineStyle.Solid);
        }

        protected override void OnUpdate(UpdateArgs args)
        {
            if (Count == 0) return;
            double vol = Volume(0);                     // volume nến hiện tại (offset 0)
            SetValue(vol, SCALE_MAX, 0);                // đẩy trục Y tới đỉnh volume
            SetValue(0.0, SCALE_ZERO, 0);               // giữ baseline 0 trong trục
        }

        // Trả về index bậc (0..5): 0 = ultra high … 5 = very low.
        private int Tier(double r)
        {
            if (r >= RUltraHigh) return 0;
            if (r >= RVeryHigh)  return 1;
            if (r >= RHigh)      return 2;
            if (r >= RNormal)    return 3;
            if (r >= RLow)       return 4;
            return 5;
        }

        private Color TierColor(int tier) => tier switch
        {
            0 => CUltraHigh,
            1 => CVeryHigh,
            2 => CHigh,
            3 => CNormal,
            4 => CLow,
            _ => CVeryLow,
        };

        // Volume tại nến index theo Begin (0 = cũ nhất). An toàn ngoài biên.
        private double VolAtBegin(int beginIndex)
        {
            if (beginIndex < 0 || beginIndex >= HistoricalData.Count) return 0.0;
            return (HistoricalData[beginIndex, SeekOriginHistory.Begin] as HistoryItemBar)?.Volume ?? 0.0;
        }

        // SMA volume N nến kết thúc tại beginIndex (gồm chính nó) — giống ta.sma.
        private double SmaAtBegin(int beginIndex)
        {
            int len = Math.Min(Period, beginIndex + 1);
            if (len <= 0) return 0.0;
            double sum = 0.0;
            for (int k = 0; k < len; k++) sum += VolAtBegin(beginIndex - k);
            return sum / len;
        }

        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null) return;

            var win = CurrentChart.Windows[args.WindowIndex];
            if (win.IsMainWindow) return;                 // chỉ vẽ trong cửa sổ phụ của indicator
            var conv = win.CoordinatesConverter;
            var gr = args.Graphics;
            var clip = win.ClientRectangle;
            double barsW = CurrentChart.BarsWidth;
            float barW = (float)Math.Max(1.0, barsW * BarWidthFrac);
            float y0 = (float)conv.GetChartY(0.0);        // đường baseline (volume = 0)

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
                    double vol = bar.Volume;
                    if (vol <= 0) continue;

                    double sma = SmaAtBegin(i);
                    double ratio = sma > 1e-9 ? vol / sma : 0.0;
                    Color col = TierColor(Tier(ratio));

                    float cx = (float)(conv.GetChartX(bar.TimeLeft) + barsW / 2.0);
                    float yv = (float)conv.GetChartY(vol);
                    float top = Math.Min(y0, yv);
                    float h = Math.Max(1f, Math.Abs(y0 - yv));

                    using var br = new SolidBrush(col);
                    gr.FillRectangle(br, cx - barW / 2f, top, barW, h);
                }
            }
            finally { gr.SetClip(prevClip); }
        }
    }
}
