// ============================================================================
//  Ô Bid/Ask lớn (CellBig) — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN (Sierra), fit trên 885 bóng / 11.796 ô, 2 phiên 5-6/11/2026
//  (GCZ26 M1): F1 0,83, recall 87%, precision 80%. KHÔNG phải lợi thế đã kiểm định.
//    bên áp đảo = max(buy, sell) >= Ratio x B  (và >= sàn nhỏ)
//    sau đó GỘP Ô LIỀN KỀ ±1 tick trong cùng nến (giữ ô lớn nhất, non-maximum suppression) — CORVEN gần như
//    không bao giờ có 2 bóng cách nhau 1 tick. Ghép 1-1 lệch ±1 tick với 885 bóng CORVEN 5-6/11:
//    trước 1.245 bóng (thừa 39%, sót 14%) -> sau ~925 bóng (thừa ~24%, sót ~21%).
//    B = trung bình của N nến TRƯỚC (không tính nến hiện tại) của "volume TB mỗi ô giá có giao dịch"
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    public struct CellBigDecision
    {
        public bool Hit;
        public int Side;        // +1 = buy (Ask) trội, -1 = sell (Bid) trội, 0 = hai bên cân (tím)
        public double Mult;     // sideVol / B (0 nếu chưa có B)
        public double SizeFrac; // 0..1 (tỉ lệ so với bề ngang nến)
    }

    public static class CellBigLogic
    {
        public const int MinHistoryBars = 5;
        public const double SizeMinFrac = 0.45;   // cỡ ở ngưỡng
        public const double SizeFullMult = 6.0;   // từ tỉ lệ này trở lên = 100% bề ngang nến

        public static CellBigDecision Decide(double buy, double sell, double baseline, bool hasBaseline,
            double ratio, double minSide, double balancedPct, bool fixedMode, double fixedThreshold)
        {
            var d = new CellBigDecision();
            double side = Math.Max(buy, sell), weak = Math.Min(buy, sell);
            if (side <= 0) return d;
            d.Mult = hasBaseline && baseline > 0 ? side / baseline : 0;
            if (fixedMode) d.Hit = side >= fixedThreshold;
            else d.Hit = hasBaseline && baseline > 0 && side >= ratio * baseline;
            if (side < minSide) d.Hit = false;
            if (!d.Hit) return d;
            d.Side = (weak / side >= balancedPct) ? 0 : (buy >= sell ? 1 : -1);
            d.SizeFrac = Size(d.Mult, ratio);
            return d;
        }

        // Gộp ô liền kề trong MỘT nến (non-maximum suppression). cells = (chỉ số tick, bên áp đảo).
        // Duyệt theo side giảm dần (hòa -> tick thấp hơn trước, tất định); giữ ô nếu không ô đã giữ nào
        // cách nó <= gapTicks. gapTicks <= 0 = tắt gộp (giữ hết). Trả về CHỈ SỐ trong cells của ô được giữ.
        public static List<int> MergeAdjacent(IList<(long tick, double side)> cells, int gapTicks)
        {
            var kept = new List<int>();
            if (cells == null || cells.Count == 0) return kept;
            if (gapTicks <= 0) { for (int i = 0; i < cells.Count; i++) kept.Add(i); return kept; }
            var order = new List<int>();
            for (int i = 0; i < cells.Count; i++) order.Add(i);
            order.Sort((a, b) =>
            {
                int c = cells[b].side.CompareTo(cells[a].side);
                if (c != 0) return c;
                c = cells[a].tick.CompareTo(cells[b].tick);
                return c != 0 ? c : a.CompareTo(b);
            });
            foreach (int i in order)
            {
                bool clash = false;
                foreach (int j in kept)
                    if (Math.Abs(cells[i].tick - cells[j].tick) <= gapTicks) { clash = true; break; }
                if (!clash) kept.Add(i);
            }
            return kept;
        }

        // cỡ to dần theo mult (nén sqrt): SizeMinFrac ở mult = ratio → 1,0 ở mult >= SizeFullMult
        public static double Size(double mult, double ratio)
        {
            if (mult <= 0) return 1.0;   // chế độ ngưỡng cố định không có tỉ lệ → cỡ đầy đủ
            double lo = Math.Sqrt(Math.Max(ratio, 1e-9)), hi = Math.Sqrt(Math.Max(SizeFullMult, ratio + 1e-6));
            double t = (Math.Sqrt(mult) - lo) / (hi - lo);
            t = Math.Min(1.0, Math.Max(0.0, t));
            return SizeMinFrac + (1.0 - SizeMinFrac) * t;
        }

        // volume trung bình mỗi ô giá CÓ giao dịch trong nến; trả false nếu nến rỗng
        public static bool BarMean(double totalVolume, int levelsWithVolume, out double mean)
        {
            mean = levelsWithVolume > 0 ? totalVolume / levelsWithVolume : 0;
            return levelsWithVolume > 0 && totalVolume > 0;
        }
    }

    // Baseline B: trung bình cuốn của N nến ĐÃ ĐÓNG. Người gọi chỉ Add mỗi nến đóng ĐÚNG 1 lần.
    public sealed class CellBigBaseline
    {
        private readonly int _n;
        private readonly Queue<double> _q = new Queue<double>();
        public CellBigBaseline(int n) { _n = Math.Max(CellBigLogic.MinHistoryBars, n); }
        public int Count => _q.Count;
        public void Add(double barMean)
        {
            _q.Enqueue(barMean);
            while (_q.Count > _n) _q.Dequeue();
        }
        public bool TryGet(out double b)
        {
            b = 0;
            if (_q.Count < CellBigLogic.MinHistoryBars) return false;
            double s = 0; foreach (var v in _q) s += v;
            b = s / _q.Count;
            return b > 0;
        }
    }
}
