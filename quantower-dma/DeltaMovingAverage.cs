// ============================================================================
//  Delta Moving Average (DMA)  —  cho QUANTOWER / Optimus Flow
// ============================================================================
//  Mô phỏng study "CC Delta Moving Average (DMA)" trên Sierra Chart của bạn:
//  vẽ ĐƯỜNG = trung bình động (SMA) của DELTA từng nến (ask−bid), kèm ĐƯỜNG 0.
//
//    delta(nến)  = BuyVolume − SellVolume  (= VolumeAnalysisData.Total.Delta)
//    DMA(nến i)  = trung bình delta của N nến gần nhất tính đến i  (N mặc định 20)
//
//  Ý nghĩa: đường trên 0 = trong N nến qua phe MUA chủ động chiếm ưu thế (dòng
//  tiền ròng vào); dưới 0 = phe BÁN. Cắt lên/xuống 0 = đảo cán cân order flow.
//  Khác cumulative delta (cộng dồn vô hạn): đây là MA nên DAO ĐỘNG quanh 0, đọc
//  được "gần đây" ai đang thắng — đúng như đường đỏ trong chart tham chiếu.
//
//  Cần Volume Analysis (footprint) để có delta. Đường 1 màu đỏ + mốc 0 (xám).
//  Đổi màu/độ dày đường trong Settings (mục DATA SERIES tự sinh).
// ============================================================================

using System;
using System.Drawing;
using TradingPlatform.BusinessLayer;

namespace DeltaMovingAverage
{
    public class DeltaMovingAverage : Indicator, IVolumeAnalysisIndicator
    {
        [InputParameter("Chu kỳ trung bình delta (số nến)", 10, 1, 2000, 1, 0)]
        public int Length { get; set; } = 20;

        private bool _vaReady;

        public DeltaMovingAverage() : base()
        {
            Name = "Delta Moving Average (DMA)";
            Description = "Trung bình động (SMA) của delta từng nến (ask−bid). Đường quanh mốc 0: >0 = phe mua thắng thế N nến, <0 = phe bán. Cần Volume Analysis.";
            SeparateWindow = true;

            AddLineSeries("DMA", Color.FromArgb(0xCC, 0x00, 0x00), 2, LineStyle.Solid);   // đỏ
            AddLineLevel(0.0, "Zero Line", Color.FromArgb(0x80, 0x80, 0x80), 1, LineStyle.Solid);
        }

        // Cần VA để có delta; true = chắc chắn Total.Delta được tính đầy đủ.
        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            _vaReady = true;
            RecomputeAll();
        }

        protected override void OnClear() { _vaReady = false; }

        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaReady) return;
            var p = HistoricalData.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            SetValue(DmaAt(0), 0, 0);      // cập nhật nến đang hình thành (offset 0)
        }

        // Điền lại toàn bộ lịch sử sau khi VA nạp xong (lúc load ban đầu delta chưa có).
        private void RecomputeAll()
        {
            int n = Count;
            for (int off = 0; off < n; off++)
                SetValue(DmaAt(off), 0, off);
        }

        // SMA của delta cho nến ở 'offset' nến trước nến hiện tại (0 = hiện tại).
        private double DmaAt(int offset)
        {
            int avail = Count - offset;                 // số nến từ offset về quá khứ
            if (avail <= 0) return 0.0;
            int len = Math.Min(Length, avail);
            double sum = 0.0;
            for (int k = 0; k < len; k++) sum += DeltaAt(offset + k);   // offset..offset+len-1 (cũ dần)
            return len > 0 ? sum / len : 0.0;
        }

        private double DeltaAt(int offset)
        {
            if (offset < 0 || offset >= Count) return 0.0;
            var bar = HistoricalData[offset, SeekOriginHistory.End] as HistoryItemBar;   // 0 = mới nhất
            return bar?.VolumeAnalysisData?.Total?.Delta ?? 0.0;
        }
    }
}
