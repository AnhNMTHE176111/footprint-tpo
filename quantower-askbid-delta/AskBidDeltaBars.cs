// ============================================================================
//  Ask/Bid Volume Difference Bars  —  cho QUANTOWER / Optimus Flow
// ============================================================================
//  Mô phỏng study "Ask/Bid Volume Difference Bars" (delta OHLC) trên Sierra
//  Chart: mỗi NẾN gốc → một NẾN DELTA trong cửa sổ phụ, dựng từ delta CHẠY
//  trong nến (ask−bid tích luỹ nội bộ nến, reset đầu mỗi nến):
//     Open ≈ 0 · High = đỉnh delta chạy · Low = đáy delta chạy · Close = delta cuối.
//  Màu: Close ≥ Open → TÍM (buy thắng); Close < Open → ĐEN (sell thắng).
//
//  v2 (2026-10-23) — FIX "nến quá khứ chỉ còn vạch ngang": Quantower không trả
//  MaxDelta/MinDelta cho nến nạp lại từ lịch sử. Giờ râu lấy từ Quantower khi là số
//  thật, nếu không thì dựng từ tick lịch sử (kiểm chéo với delta Quantower), nếu
//  vẫn không có thì vẽ viền rỗng + báo trên màn hình. Chi tiết: DeltaCore.cs.
// ============================================================================
namespace AskBidDeltaBars
{
    using System;
    using System.Drawing;
    using TradingPlatform.BusinessLayer;
    using AskBidDeltaIndicators;

    public class AskBidDeltaBars : DeltaIndicatorBase
    {
        protected override bool PerBar => true;
        protected override bool ResetDailyDefault => false;

        public AskBidDeltaBars() : base()
        {
            Name = "Ask/Bid Volume Difference Bars";
            Description = "Delta (ask−bid) dạng nến OHLC mỗi nến: Open≈0, High=đỉnh delta chạy, Low=đáy delta, Close=delta cuối. Tím=buy thắng, đen=sell thắng. Râu nến cũ dựng từ tick. Cần Volume Analysis.";
            UpColor = Color.FromArgb(0x72, 0x00, 0xFF);
        }
    }
}
