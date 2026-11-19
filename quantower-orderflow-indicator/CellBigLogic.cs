// ============================================================================
//  Ô Bid/Ask lớn (CellBig) + Big Trade — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN, fit trên chart M5 ngày 18/11/2026 (research/corven_m5_2026-11-18/, rules.py + final_eval.py là bản Python gốc).
//  KHÔNG phải lợi thế đã kiểm định. TẤT CẢ xét THEO TỪNG TICK (không gộp hàng), bóng đặt đúng giá khớp của ô.
//
//  1) CHẤM ĐẶC NHỎ (Dot): ô giá có giao dịch của một nến, bid, ask, side = max(bid, ask) (bên trội), trades = số lệnh khớp.
//     Mức nền = trung bình, trên 20 nến ĐÃ ĐÓNG trước (cần >= 5 nến), của (volume trung bình mỗi ô có giao dịch của nến đó).
//     Dot nổ khi trades >= CellDotTradesRatio (2,4) x mức nền, VÀ side lớn hơn hẳn side của mọi tick khác trong ±CellDotLocalTicks (3) tick
//     cùng nến (tick vắng = 0; bằng nhau không tính là lớn hơn), VÀ side >= sàn CellBigMinSide (9). Màu: Ask > Bid -> xanh (buy), ngược lại -> đỏ (sell).
//     Chế độ ngưỡng cố định (UseFixedThreshold): Dot dùng side >= ngưỡng cố định thay cho điều kiện số lệnh (vẫn cần lớn hơn hẳn trong ±3 tick và sàn).
//  2) BIG TRADE (vòng tròn mờ) — KHÔNG còn suy từ volume của ô (bản 07efb1f đã bỏ): đó là MỘT lệnh đơn chủ động rất lớn
//     (MaxOneTradeVolume của mức giá, chỉ feed SỐNG mới cấp). Nổ khi MaxOneTradeVolume >= BigTradeMinContracts (mặc định 10). Xem BigTradeLogic.
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
        public bool DotEnabled = true;
        public double DotTradesRatio = 2.4;   // Dot: trades >= số này x volume trung bình mỗi ô của 20 nến trước
        public int DotLocalTicks = 3;         // Dot: side phải lớn hơn hẳn mọi tick khác trong ± số tick này
        public double MinSide = 9;            // sàn tuyệt đối cho side (Dot)
        public bool FixedMode;                // true: dùng FixedThreshold thay cho các mức nền
        public double FixedThreshold = 10;
    }

    public struct CellMark
    {
        public long Tick;
        public int Tier;        // CellBigLogic.TierDot
        public int Side;        // +1 = buy (Ask trội), -1 = sell
        public double Buy, Sell, Trades;
        public double Mult;     // trades / volume trung bình mỗi ô (0 nếu chế độ cố định)
        public double SizeFrac; // DotSizeFrac
        public double Threshold;// ngưỡng thực đã vượt (trades, hoặc side ở chế độ cố định) — dùng cho tooltip
    }

    public static class CellBigLogic
    {
        public const int MinHistoryBars = 5;
        public const double DotSizeFrac = 0.45;   // cỡ chấm Dot (tỉ lệ bề ngang nến, kẹp [5,10] px khi vẽ)
        public const int TierNone = 0, TierDot = 2;

        // floor division đúng cho số âm (StopHuntLogic dùng)
        public static long FloorDiv(long a, long b)
        {
            long q = a / b;
            if ((a % b != 0) && ((a < 0) != (b < 0))) q--;
            return q;
        }

        /// <summary>Thống kê một nến cho mức nền: volume TB mỗi ô có giao dịch. false nếu nến rỗng.</summary>
        public static bool BarStats(IEnumerable<CellLevel> levels, out double meanLevelVol)
        {
            double tot = 0; int n = 0;
            if (levels != null)
                foreach (var l in levels)
                    if (l.Vol > 0) { tot += l.Vol; n++; }
            meanLevelVol = n > 0 ? tot / n : 0;
            return n > 0 && tot > 0;
        }

        /// <summary>
        /// Xét từng ô của một nến, chỉ ra các chấm Dot. avgLevelVol = mức nền từ các nến đã đóng trước (hasBaseline false = chưa đủ 5 nến -> chỉ chế độ cố định chạy).
        /// Trả các dấu theo tick tăng dần.
        /// </summary>
        public static List<CellMark> Evaluate(IReadOnlyList<CellLevel> levels, bool hasBaseline, double avgLevelVol, CellBigSettings s)
        {
            var res = new List<CellMark>();
            if (levels == null || levels.Count == 0 || s == null) return res;
            var side = new Dictionary<long, double>(levels.Count);
            var sorted = new List<CellLevel>(levels.Count);
            foreach (var l in levels) if (l.Vol > 0) { side[l.Tick] = Math.Max(l.Buy, l.Sell); sorted.Add(l); }
            sorted.Sort((a, b) => a.Tick.CompareTo(b.Tick));

            bool canDot = s.DotEnabled && (s.FixedMode || (hasBaseline && avgLevelVol > 0));
            double dotThr = s.FixedMode ? s.FixedThreshold : s.DotTradesRatio * avgLevelVol;

            foreach (var l in sorted)
            {
                double sd = Math.Max(l.Buy, l.Sell);
                if (sd < s.MinSide) continue;
                int dir = l.Buy > l.Sell ? 1 : -1;
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
    // Chuỗi: volume TB mỗi ô có giao dịch của nến. Cần >= 5 nến.
    public sealed class CellBigBaseline
    {
        private readonly int _n;
        private readonly Queue<double> _mean = new Queue<double>();
        public CellBigBaseline(int n) { _n = Math.Max(CellBigLogic.MinHistoryBars, n); }
        public int Count => _mean.Count;
        public void Add(double barMeanLevelVol)
        {
            _mean.Enqueue(barMeanLevelVol);
            while (_mean.Count > _n) _mean.Dequeue();
        }
        /// <summary>Volume TB mỗi ô có giao dịch (trung bình 20 nến trước).</summary>
        public bool TryGet(out double avgLevelVol)
        {
            avgLevelVol = 0;
            if (_mean.Count < CellBigLogic.MinHistoryBars) return false;
            double s = 0; foreach (var v in _mean) s += v;
            avgLevelVol = s / _mean.Count;
            return avgLevelVol > 0;
        }
    }

    // BIG TRADE: một lệnh đơn chủ động lớn tại một mức giá (VolumeAnalysisItem.MaxOneTradeVolume).
    public static class BigTradeLogic
    {
        public const double SizeMinFrac = 1.0;    // cỡ ở ngưỡng (x bề ngang nến)
        public const double SizeMaxFrac = 2.5;    // cỡ tối đa
        public const double SizeFullMult = 6.0;   // từ lệnh >= 6 x ngưỡng trở lên = cỡ tối đa

        /// <summary>Nổ khi lệnh đơn >= ngưỡng (0 / âm = không có số liệu lệnh đơn -> không nổ).</summary>
        public static bool Hit(double maxOneTrade, double minContracts) => maxOneTrade > 0 && maxOneTrade >= minContracts;

        /// <summary>Cỡ (x bề ngang nến): 1,0 ở ngưỡng, 2,5 từ 6 x ngưỡng trở lên, đường cong căn bậc hai.</summary>
        public static double SizeFrac(double maxOneTrade, double minContracts)
        {
            if (minContracts <= 0) return SizeMinFrac;
            double t = (Math.Sqrt(maxOneTrade / minContracts) - 1.0) / (Math.Sqrt(SizeFullMult) - 1.0);
            t = Math.Min(1.0, Math.Max(0.0, t));
            return SizeMinFrac + (SizeMaxFrac - SizeMinFrac) * t;
        }
    }
}
