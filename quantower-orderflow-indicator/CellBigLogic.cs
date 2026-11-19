// ============================================================================
//  Ô Bid/Ask lớn (CellBig) — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN, fit trên chart M5 ngày 18/11/2026 (research/corven_m5_2026-11-18/, rules.py + final_eval.py là bản Python gốc).
//  KHÔNG phải lợi thế đã kiểm định. TẤT CẢ xét THEO TỪNG TICK (không gom hàng), bóng đặt đúng giá khớp của ô.
//
//  Ký hiệu mỗi ô giá có giao dịch (volume > 0) của một nến: bid, ask, side = max(bid, ask) (bên trội), weak = min(bid, ask) (bên yếu),
//  trades = số lệnh khớp. Màu: Ask > Bid -> xanh (buy), ngược lại -> đỏ (sell).
//  Hai mức nền, tính CHỈ từ các nến ĐÃ ĐÓNG trước (cuốn 20 nến, cần >= 5 nến), đúng như feats.py:
//    - mức trung bình volume mỗi ô = trung bình, trên 20 nến trước, của (volume trung bình mỗi ô có giao dịch của nến đó);
//    - bên trội lớn nhất trung bình = trung bình, trên 20 nến trước, của (bên trội lớn nhất trong các ô của nến đó).
//  1) VÒNG TRÒN LỚN MỜ (Big): side >= CellBigMaxSideRatio (0,5) x bên trội lớn nhất trung bình, VÀ side LỚN HƠN HẲN side của mọi tick khác trong
//     ±CellBigLocalTicks (5) tick cùng nến (tick vắng = 0; bằng nhau không tính là lớn hơn), VÀ side >= CellBigMinImbalance (4) x max(weak, 1).
//  2) CHẤM ĐẶC NHỎ (Dot): trades >= CellDotTradesRatio (2,4) x mức trung bình volume mỗi ô, VÀ side lớn hơn hẳn side của mọi tick khác trong ±CellDotLocalTicks (3) tick.
//  Một ô có thể vừa là Big vừa là Dot -> cả hai cùng được trả về (Dot vẽ trên cùng). Sàn CellBigMinSide (9) áp cho cả hai (đo trên 26 nến mẫu: không đổi kết quả).
//  Chế độ ngưỡng cố định (UseFixedThreshold): Big dùng side >= ngưỡng cố định thay cho 0,5 x bên trội lớn nhất trung bình (vẫn cần lớn hơn hẳn trong ±5 tick, mất cân bằng, sàn);
//  Dot dùng side >= ngưỡng cố định thay cho điều kiện số lệnh (vẫn cần lớn hơn hẳn trong ±3 tick và sàn). Không cần nến nền.
//  Cỡ Big to dần theo side / bên trội lớn nhất trung bình (nén căn bậc hai): 1,0 x bề ngang nến ở 0,5 lần -> 2,5 x ở >= 2 lần.
//  Bóng TÍM chỉ còn nghĩa stop hunt, do OrderFlowBubbles.cs tô.
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    /// <summary>Một ô giá có giao dịch của nến. Buy = ask (BuyVolume), Sell = bid (SellVolume).</summary>
    public readonly struct CellLevel
    {
        public readonly long Tick;
        public readonly double Buy, Sell, Vol;
        public readonly int Trades;
        public CellLevel(long tick, double buy, double sell, double vol, int trades) { Tick = tick; Buy = buy; Sell = sell; Vol = vol; Trades = trades; }
    }

    public sealed class CellBigSettings
    {
        public double MaxSideRatio = 0.5;     // Big: side >= số này x bên trội lớn nhất trung bình của 20 nến trước
        public int LocalTicks = 5;            // Big: side phải lớn hơn hẳn mọi tick khác trong ± số tick này
        public double MinImbalance = 4.0;     // Big: side >= số này x max(weak, 1); <= 0 tắt điều kiện
        public bool DotEnabled = true;
        public double DotTradesRatio = 2.4;   // Dot: trades >= số này x volume trung bình mỗi ô của 20 nến trước
        public int DotLocalTicks = 3;         // Dot: side phải lớn hơn hẳn mọi tick khác trong ± số tick này
        public double MinSide = 9;            // sàn tuyệt đối cho side (cả Big và Dot)
        public bool FixedMode;                // true: dùng FixedThreshold thay cho các mức nền
        public double FixedThreshold = 10;
    }

    public struct CellMark
    {
        public long Tick;
        public int Tier;        // CellBigLogic.TierBig / TierDot
        public int Side;        // +1 = buy (Ask trội), -1 = sell
        public double Buy, Sell, Trades;
        public double Mult;     // Big: side / bên trội lớn nhất trung bình (0 nếu chế độ cố định); Dot: trades / volume trung bình mỗi ô
        public double SizeFrac; // Big: 1,0..2,5; Dot: DotSizeFrac
        public double Threshold;// ngưỡng thực đã vượt (Big: side; Dot: trades, hoặc side ở chế độ cố định) — dùng cho tooltip
    }

    public static class CellBigLogic
    {
        public const int MinHistoryBars = 5;
        public const double SizeMinFrac = 1.0;    // cỡ Big ở ngưỡng (= 1,0 x bề ngang nến)
        public const double SizeMaxFrac = 2.5;    // cỡ Big tối đa (= 2,5 x bề ngang nến; vòng mờ được phép lớn hơn nến)
        public const double DotSizeFrac = 0.45;   // cỡ chấm Dot (tỉ lệ bề ngang nến, kẹp [5,10] px khi vẽ)
        public const double SizeFullMult = 2.0;   // từ side >= 2 lần bên trội lớn nhất trung bình trở lên = cỡ tối đa
        public const int TierNone = 0, TierBig = 1, TierDot = 2;

        // floor division đúng cho số âm (StopHuntLogic dùng)
        public static long FloorDiv(long a, long b)
        {
            long q = a / b;
            if ((a % b != 0) && ((a < 0) != (b < 0))) q--;
            return q;
        }

        /// <summary>Thống kê một nến cho mức nền: volume TB mỗi ô có giao dịch + bên trội lớn nhất. false nếu nến rỗng.</summary>
        public static bool BarStats(IEnumerable<CellLevel> levels, out double meanLevelVol, out double maxSide)
        {
            double tot = 0, mx = 0; int n = 0;
            if (levels != null)
                foreach (var l in levels)
                    if (l.Vol > 0) { tot += l.Vol; n++; double s = Math.Max(l.Buy, l.Sell); if (s > mx) mx = s; }
            meanLevelVol = n > 0 ? tot / n : 0; maxSide = mx;
            return n > 0 && tot > 0;
        }

        // cỡ Big to dần theo mult (nén sqrt): SizeMinFrac (1,0) ở mult = ratio → SizeMaxFrac (2,5) ở mult >= SizeFullMult; đơn vị = bề ngang nến
        public static double Size(double mult, double ratio)
        {
            if (mult <= 0) return 1.5;   // chế độ ngưỡng cố định không có tỉ lệ → cỡ giữa (1,5 x bề ngang nến)
            double lo = Math.Sqrt(Math.Max(ratio, 1e-9)), hi = Math.Sqrt(Math.Max(SizeFullMult, ratio + 1e-6));
            double t = (Math.Sqrt(mult) - lo) / (hi - lo);
            t = Math.Min(1.0, Math.Max(0.0, t));
            return SizeMinFrac + (SizeMaxFrac - SizeMinFrac) * t;
        }

        /// <summary>
        /// Xét từng ô của một nến. avgLevelVol / avgMaxSide = mức nền từ các nến đã đóng trước (hasBaseline false = chưa đủ 5 nến -> chỉ chế độ cố định chạy).
        /// Trả các dấu theo tick tăng dần; một ô vừa Big vừa Dot cho hai dấu (Big trước, Dot sau).
        /// </summary>
        public static List<CellMark> Evaluate(IReadOnlyList<CellLevel> levels, bool hasBaseline, double avgLevelVol, double avgMaxSide, CellBigSettings s)
        {
            var res = new List<CellMark>();
            if (levels == null || levels.Count == 0 || s == null) return res;
            var side = new Dictionary<long, double>(levels.Count);
            var sorted = new List<CellLevel>(levels.Count);
            foreach (var l in levels) if (l.Vol > 0) { side[l.Tick] = Math.Max(l.Buy, l.Sell); sorted.Add(l); }
            sorted.Sort((a, b) => a.Tick.CompareTo(b.Tick));

            double bigThr = s.FixedMode ? s.FixedThreshold : s.MaxSideRatio * avgMaxSide;
            bool canBig = s.FixedMode || (hasBaseline && avgMaxSide > 0);
            bool canDot = s.DotEnabled && (s.FixedMode || (hasBaseline && avgLevelVol > 0));
            double dotThr = s.FixedMode ? s.FixedThreshold : s.DotTradesRatio * avgLevelVol;

            foreach (var l in sorted)
            {
                double sd = Math.Max(l.Buy, l.Sell), weak = Math.Min(l.Buy, l.Sell);
                if (sd < s.MinSide) continue;
                int dir = l.Buy > l.Sell ? 1 : -1;
                if (canBig && sd >= bigThr && LocalMax(side, l.Tick, sd, s.LocalTicks)
                    && (s.MinImbalance <= 0 || sd >= s.MinImbalance * Math.Max(weak, 1)))
                {
                    double mult = s.FixedMode || avgMaxSide <= 0 ? 0 : sd / avgMaxSide;
                    res.Add(new CellMark { Tick = l.Tick, Tier = TierBig, Side = dir, Buy = l.Buy, Sell = l.Sell, Trades = l.Trades, Mult = mult,
                        SizeFrac = Size(mult, s.MaxSideRatio), Threshold = Math.Max(bigThr, s.MinSide) });
                }
                if (canDot && (s.FixedMode ? sd >= dotThr : l.Trades >= dotThr) && LocalMax(side, l.Tick, sd, s.DotLocalTicks))
                {
                    res.Add(new CellMark { Tick = l.Tick, Tier = TierDot, Side = dir, Buy = l.Buy, Sell = l.Sell, Trades = l.Trades,
                        Mult = s.FixedMode || avgLevelVol <= 0 ? 0 : l.Trades / avgLevelVol, SizeFrac = DotSizeFrac,
                        Threshold = s.FixedMode ? Math.Max(dotThr, s.MinSide) : dotThr });
                }
            }
            return res;
        }

        // true khi sd LỚN HƠN HẲN side của mọi tick khác trong ±w tick (tick vắng = 0)
        public static bool LocalMax(Dictionary<long, double> side, long tick, double sd, int w)
        {
            for (int o = 1; o <= w; o++)
            {
                if (side.TryGetValue(tick - o, out double a) && a >= sd) return false;
                if (side.TryGetValue(tick + o, out double b) && b >= sd) return false;
            }
            return true;
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
    }

    // Mức nền: trung bình cuốn của N nến ĐÃ ĐÓNG. Người gọi chỉ Add mỗi nến đóng ĐÚNG 1 lần.
    // Hai chuỗi: volume TB mỗi ô có giao dịch, và bên trội lớn nhất của nến. Cần >= 5 nến.
    public sealed class CellBigBaseline
    {
        private readonly int _n;
        private readonly Queue<double> _mean = new Queue<double>(), _max = new Queue<double>();
        public CellBigBaseline(int n) { _n = Math.Max(CellBigLogic.MinHistoryBars, n); }
        public int Count => _mean.Count;
        public void Add(double barMeanLevelVol, double barMaxSide)
        {
            _mean.Enqueue(barMeanLevelVol); _max.Enqueue(barMaxSide);
            while (_mean.Count > _n) { _mean.Dequeue(); _max.Dequeue(); }
        }
        /// <summary>Volume TB mỗi ô có giao dịch (trung bình 20 nến trước).</summary>
        public bool TryGet(out double avgLevelVol) => Avg(_mean, out avgLevelVol);
        /// <summary>Bên trội lớn nhất trung bình (trung bình 20 nến trước).</summary>
        public bool TryGetMaxSide(out double avgMaxSide) => Avg(_max, out avgMaxSide);
        private static bool Avg(Queue<double> q, out double b)
        {
            b = 0;
            if (q.Count < CellBigLogic.MinHistoryBars) return false;
            double s = 0; foreach (var v in q) s += v;
            b = s / q.Count;
            return b > 0;
        }
    }
}
