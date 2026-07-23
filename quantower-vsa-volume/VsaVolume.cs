// ============================================================================
//  VSA Volume  —  histogram volume TÔ MÀU THEO BẬC (VSA / Wyckoff) cho QUANTOWER
// ============================================================================
//  Mô phỏng 1:1 indicator "VSA Wyckoff Volume" trên TradingView: mỗi cột volume
//  được tô màu theo TỈ LỆ volume nến đó so với TRUNG BÌNH N nến gần nhất (SMA,
//  gồm cả nến hiện tại — giống ta.sma(volume, length)). Nhìn phát ra ngay
//  climax / rất cao / cao / bình thường / thấp / rất thấp.
//
//  Chỉ dùng bar.Volume → KHÔNG cần Volume Analysis (footprint) → chạy được cả
//  khi feed thiếu tick lịch sử. Vẽ bằng 6 line-series kiểu Histogramm, mỗi bậc
//  một màu; mỗi nến chỉ ghi giá trị vào series khớp bậc, các series khác = 0.
//
//  BẬC (mặc định = đúng config user gửi từ TradingView, × trung bình 20 nến):
//     ≥ 2.2  Ultra High (climax)  → Color 0  tím
//     ≥ 1.8  Very High            → Color 1  đỏ
//     ≥ 1.2  High                 → Color 2  cam
//     ≥ 0.8  Normal               → Color 3  xanh lá
//     ≥ 0.4  Low                  → Color 4  xanh dương
//     < 0.4  Very Low             → Color 5  xám
//  Màu / độ rộng / kiểu vẽ từng bậc chỉnh trực tiếp trong Settings (mỗi series
//  tự có mục "DATA SERIES" riêng, giống panel Style của TradingView).
// ============================================================================

using System;
using System.Drawing;
using TradingPlatform.BusinessLayer;

namespace VsaVolume
{
    public class VsaVolume : Indicator
    {
        private const int TIERS = 6;

        // ------- Inputs (khớp nhãn + mặc định TradingView) -------
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

        public VsaVolume() : base()
        {
            Name = "VSA Volume";
            Description = "Volume tô màu theo bậc (VSA/Wyckoff): tỉ lệ volume nến / SMA N nến. 6 bậc màu. Không cần Volume Analysis.";
            SeparateWindow = true;

            // Thứ tự series khớp Color 0..5 của TradingView.
            AddLineSeries("Color 0 · Ultra High (climax)", Color.FromArgb(0x9C, 0x27, 0xB0), 4, LineStyle.Histogramm); // tím
            AddLineSeries("Color 1 · Very High",           Color.FromArgb(0xF4, 0x43, 0x36), 4, LineStyle.Histogramm); // đỏ
            AddLineSeries("Color 2 · High",                Color.FromArgb(0xFF, 0x98, 0x00), 4, LineStyle.Histogramm); // cam
            AddLineSeries("Color 3 · Normal",              Color.FromArgb(0x4C, 0xAF, 0x50), 4, LineStyle.Histogramm); // xanh lá
            AddLineSeries("Color 4 · Low",                 Color.FromArgb(0x5B, 0x8D, 0xEF), 4, LineStyle.Histogramm); // xanh dương
            AddLineSeries("Color 5 · Very Low",            Color.FromArgb(0xB0, 0xBE, 0xC5), 4, LineStyle.Histogramm); // xám
        }

        protected override void OnUpdate(UpdateArgs args)
        {
            if (Count == 0) return;

            double vol = Volume(0);                 // volume nến hiện tại (offset 0)

            // SMA volume N nến (gồm nến hiện tại) — giống ta.sma(volume, length)
            int n = Math.Min(Period, Count);
            double sum = 0;
            for (int k = 0; k < n; k++) sum += Volume(k);
            double sma = n > 0 ? sum / n : 0;
            double ratio = sma > 1e-9 ? vol / sma : 0;

            int tier = Tier(ratio);
            for (int s = 0; s < TIERS; s++)
                SetValue(s == tier ? vol : 0.0, s, 0);   // offset 0 = nến hiện tại
        }

        // Trả về index series (0..5) khớp Color 0..5 của TradingView.
        private int Tier(double r)
        {
            if (r >= RUltraHigh) return 0;   // ultra high
            if (r >= RVeryHigh)  return 1;   // very high
            if (r >= RHigh)      return 2;   // high
            if (r >= RNormal)    return 3;   // normal
            if (r >= RLow)       return 4;   // low
            return 5;                        // very low
        }
    }
}
