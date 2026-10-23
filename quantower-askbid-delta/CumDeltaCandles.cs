// ============================================================================
//  Cumulative Delta Candles — nến delta CỘNG DỒN cho QUANTOWER / Optimus Flow
// ============================================================================
//  Mỗi nến của chart gốc → một nến trên trục DELTA CỘNG DỒN (ask − bid):
//     Open  = Close nến trước (đóng cửa nến này = mở cửa nến kế tiếp)
//     Close = Open + delta của nến
//     High/Low = đỉnh/đáy delta CHẠY trong nến (cộng vào Open)
//  Đặt lại về 0 mỗi ngày giao dịch (mặc định 05:00 giờ VN = đầu phiên Á, khớp
//  SessionZones). Màu: Close ≥ Open → xanh (buy thắng); ngược lại → đen (sell thắng).
//  Cần Volume Analysis. Râu nến lịch sử dựng từ tick — xem DeltaCore.cs.
// ============================================================================
namespace CumDeltaCandlesNs
{
    using System;
    using TradingPlatform.BusinessLayer;
    using AskBidDeltaIndicators;

    public class CumDeltaCandles : DeltaIndicatorBase
    {
        [InputParameter("Đặt lại delta cộng dồn mỗi ngày (tắt = không bao giờ đặt lại)", 20)]
        public bool ResetDaily { get; set; } = true;

        [InputParameter("Mốc đặt lại (phút trong ngày, giờ local: 300 = 05:00)", 21, 0, 1439, 5, 0)]
        public int ResetMinutes { get; set; } = 300;

        protected override bool PerBar => false;
        protected override bool ResetDailyDefault => ResetDaily;
        protected override int ResetMinutesValue => ResetMinutes;

        public CumDeltaCandles() : base()
        {
            Name = "Cumulative Delta Candles";
            Description = "Nến delta cộng dồn: Open = Close nến trước, Close = Open + delta nến, râu = đỉnh/đáy delta chạy. Xanh = buy thắng, đen = sell thắng. Đặt lại mỗi ngày. Cần Volume Analysis.";
        }
    }
}
