// ============================================================================
//  Ask/Bid Volume Difference Bars  —  cho QUANTOWER / Optimus Flow
// ============================================================================
//  Mô phỏng study "Ask/Bid Volume Difference Bars" (delta OHLC) trên Sierra
//  Chart: mỗi NẾN gốc → một NẾN DELTA trong cửa sổ phụ, dựng từ delta CHẠY
//  trong nến (ask−bid tích luỹ nội bộ nến, reset đầu mỗi nến):
//     Open ≈ 0 · High = đỉnh delta chạy · Low = đáy delta chạy · Close = delta cuối.
//
//  v3 (2026-11-08) — TÔ MÀU THEO LỰC ÁP ĐẢO kiểu "CC Delta Bar (Buyer/Seller)" của CORVEN:
//     XANH = buy áp đảo trong nến · ĐỎ = sell áp đảo · XÁM = yếu, không bên nào áp đảo.
//     buy = Close − Low (buy đẩy từ đáy delta lên), sell = High − Close (sell đè từ đỉnh xuống);
//     áp đảo khi quãng đó ≥ hệ số × trung bình |delta| của N nến trước VÀ lớn hơn quãng bên kia.
//     Vd nến đầu đè xuống −30 rồi buy vào +50, đóng +20 → buy 50, sell 0 → XANH dù thân ngắn.
//     Quy tắc + số đo: DeltaCore.StrengthTones. Tắt ô "Tô màu theo lực áp đảo" = màu tím/đen cũ.
//     ⚠️ Đây là công cụ ĐỌC chart, chưa phải tín hiệu đã kiểm định lợi thế.
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
    using AskBidDeltaCore;
    using AskBidDeltaIndicators;

    public class AskBidDeltaBars : DeltaIndicatorBase
    {
        [InputParameter("Tô màu theo lực áp đảo: xanh = buy áp đảo, đỏ = sell áp đảo, xám = yếu (tắt = tím/đen theo delta cuối)", 30)]
        public bool StrengthColors { get; set; } = true;

        [InputParameter("Số nến làm nền so sánh (trung bình |delta| các nến trước)", 31, 3, 200, 1, 0)]
        public int StrengthLookback { get; set; } = 15;

        [InputParameter("Hệ số ngưỡng (× trung bình |delta|): quãng đẩy ≥ ngưỡng mới tô màu", 32, 0.5, 5.0, 0.05, 2)]
        public double StrengthMult { get; set; } = 1.25;

        [InputParameter("Ngưỡng tối thiểu (hợp đồng) — chống tô màu lúc thị trường quá vắng", 33, 0, 1000, 1, 0)]
        public double StrengthMin { get; set; } = 5;

        [InputParameter("Màu cột buy áp đảo", 34)]
        public Color StrongBuyColor { get; set; } = Color.FromArgb(0x00, 0xC8, 0x00);

        [InputParameter("Màu cột sell áp đảo", 35)]
        public Color StrongSellColor { get; set; } = Color.FromArgb(0xE6, 0x1E, 0x1E);

        [InputParameter("Màu cột yếu (không bên nào áp đảo)", 36)]
        public Color WeakColor { get; set; } = Color.FromArgb(0x78, 0x78, 0x78);

        protected override bool PerBar => true;
        protected override bool ResetDailyDefault => false;

        private CumBar[] _toneChain;
        private sbyte[] _tones;
        private string _toneKey = "";

        public AskBidDeltaBars() : base()
        {
            Name = "Ask/Bid Volume Difference Bars";
            Description = "Delta (ask−bid) dạng nến OHLC mỗi nến: Open≈0, High=đỉnh delta chạy, Low=đáy delta, Close=delta cuối. Xanh = buy áp đảo trong nến (đẩy từ đáy delta lên), đỏ = sell áp đảo, xám = yếu (ngưỡng thích nghi theo N nến trước). Râu nến cũ dựng từ tick. Cần Volume Analysis.";
            UpColor = Color.FromArgb(0x72, 0x00, 0xFF);
        }

        protected override sbyte[] ComputeTones(CumBar[] chain, out Color up, out Color down, out Color neutral)
        {
            if (!StrengthColors) return base.ComputeTones(chain, out up, out down, out neutral);
            up = StrongBuyColor; down = StrongSellColor; neutral = WeakColor;
            string key = StrengthLookback + "|" + StrengthMult + "|" + StrengthMin;
            if (!ReferenceEquals(chain, _toneChain) || key != _toneKey || _tones == null)
            {
                _tones = DeltaCore.StrengthTones(chain, StrengthLookback, StrengthMult, StrengthMin);
                _toneChain = chain; _toneKey = key;
            }
            return _tones;
        }
    }
}
