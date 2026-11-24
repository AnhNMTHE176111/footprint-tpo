// ============================================================================
//  Ô Bid/Ask lớn (CellBig) + Big Trade — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN, fit trên chart M5 ngày 18/11/2026 (research/corven_m5_2026-11-18/, rules.py + final_eval.py là bản Python gốc).
//  KHÔNG phải lợi thế đã kiểm định. TẤT CẢ xét THEO TỪNG TICK (không gộp hàng), bóng đặt đúng giá khớp của ô.
//
//  1) CHẤM ĐẶC NHỎ (Dot), xét RIÊNG TỪNG BÊN (chốt 2026-11-19, research/corven_m5_2026-11-18/perside_dots.py): Bid và Ask được xét độc lập tại mọi tick.
//     Mức nền = trung bình, trên 20 nến ĐÃ ĐÓNG trước (cần >= 5 nến), của TRUNG VỊ volume mỗi ô có giao dịch của nến đó (ô volume > 0).
//     Chấm ĐỎ (sell) tại tick p nổ khi bid(p) >= CellDotMedianRatio (2,8) x mức nền VÀ bid(p) lớn hơn hẳn bid của mọi tick khác trong ±CellDotLocalTicks (4) tick
//     cùng nến (tick vắng = 0; bằng nhau không tính là lớn hơn) VÀ bid(p) >= sàn CellBigMinSide (9). Chấm XANH (buy) tương tự với ask. Một tick có thể có cả hai.
//     Luật che (CORVEN vẽ đỏ đè xanh): chấm xanh bị bỏ nếu cùng nến có chấm đỏ cách <= CellDotHideBuyNearSellTicks (6) tick. Danh sách trả về: xanh trước, đỏ sau (đỏ vẽ sau = nằm trên).
//     Chế độ ngưỡng cố định (UseFixedThreshold): giá trị của bên >= max(ngưỡng cố định, sàn), vẫn cần lớn hơn hẳn trong ±4 tick và áp luật che.
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
        public double DotMedianRatio = 2.8;   // Dot: bid (hoặc ask) >= số này x trung vị volume mỗi ô của 20 nến trước
        public int DotLocalTicks = 4;         // Dot: bên đang xét phải lớn hơn hẳn cùng bên của mọi tick khác trong ± số tick này
        public int DotHideBuyNearSellTicks = 6; // chấm xanh bị che (bỏ) nếu cùng nến có chấm đỏ cách <= số tick này (< 0 = tắt che)
        public double MinSide = 9;            // sàn tuyệt đối cho giá trị của bên đang xét (Dot)
        public bool FixedMode;                // true: dùng FixedThreshold thay cho các mức nền
        public double FixedThreshold = 10;
    }

    public struct CellMark
    {
        public long Tick;
        public int Tier;        // CellBigLogic.TierDot
        public int Side;        // +1 = chấm xanh buy (xét Ask), -1 = chấm đỏ sell (xét Bid)
        public double Buy, Sell;// Ask và Bid của ô (bên đang xét = Buy nếu Side > 0, Sell nếu Side < 0)
        public double Mult;     // giá trị bên đang xét / trung vị mức nền (0 nếu chế độ cố định)
        public double SizeFrac; // DotSizeFrac
        public double Threshold;// ngưỡng thực đã vượt (2,8 x mức nền, ít nhất sàn; hoặc max(ngưỡng cố định, sàn)) — dùng cho tooltip
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

        /// <summary>Thống kê một nến cho mức nền: volume TB và TRUNG VỊ mỗi ô có giao dịch (ô volume > 0). false nếu nến rỗng.</summary>
        public static bool BarStats(IEnumerable<CellLevel> levels, out double meanLevelVol, out double medianLevelVol)
        {
            var vols = new List<double>();
            double tot = 0;
            if (levels != null)
                foreach (var l in levels)
                    if (l.Vol > 0) { tot += l.Vol; vols.Add(l.Vol); }
            int n = vols.Count;
            meanLevelVol = n > 0 ? tot / n : 0;
            medianLevelVol = 0;
            if (n > 0)
            {
                vols.Sort();
                medianLevelVol = (n % 2 == 1) ? vols[n / 2] : (vols[n / 2 - 1] + vols[n / 2]) / 2.0;
            }
            return n > 0 && tot > 0;
        }

        /// <summary>Biên độ nến theo tick: tick cao nhất - tick thấp nhất trong các ô có giao dịch (0 nếu rỗng).</summary>
        public static double BarRangeTicks(IEnumerable<CellLevel> levels)
        {
            long lo = long.MaxValue, hi = long.MinValue;
            if (levels != null)
                foreach (var l in levels)
                    if (l.Vol > 0) { if (l.Tick < lo) lo = l.Tick; if (l.Tick > hi) hi = l.Tick; }
            return hi >= lo ? hi - lo : 0;
        }

        /// <summary>
        /// Xét từng ô của một nến, chỉ ra các chấm Dot THEO TỪNG BÊN. medianBaseline = mức nền (trung vị) từ các nến đã đóng trước (hasBaseline false = chưa đủ 5 nến -> chỉ chế độ cố định chạy).
        /// Trả xanh (tick tăng dần) rồi tới đỏ (tick tăng dần): thứ tự vẽ, đỏ nằm trên.
        /// </summary>
        public static List<CellMark> Evaluate(IReadOnlyList<CellLevel> levels, bool hasBaseline, double medianBaseline, CellBigSettings s)
        {
            var res = new List<CellMark>();
            if (levels == null || levels.Count == 0 || s == null) return res;
            var askAt = new Dictionary<long, double>(levels.Count);
            var bidAt = new Dictionary<long, double>(levels.Count);
            var sorted = new List<CellLevel>(levels.Count);
            foreach (var l in levels) if (l.Vol > 0) { askAt[l.Tick] = l.Buy; bidAt[l.Tick] = l.Sell; sorted.Add(l); }
            sorted.Sort((a, b) => a.Tick.CompareTo(b.Tick));

            bool canDot = s.DotEnabled && (s.FixedMode || (hasBaseline && medianBaseline > 0));
            if (!canDot) return res;
            double thr = Math.Max(s.FixedMode ? s.FixedThreshold : s.DotMedianRatio * medianBaseline, s.MinSide);

            var reds = new List<CellMark>();
            var blues = new List<CellMark>();
            foreach (var l in sorted)
            {
                if (l.Sell > 0 && l.Sell >= thr && LocalMax(bidAt, l.Tick, l.Sell, s.DotLocalTicks))
                    reds.Add(Mark(l, -1, l.Sell, medianBaseline, thr, s));
                if (l.Buy > 0 && l.Buy >= thr && LocalMax(askAt, l.Tick, l.Buy, s.DotLocalTicks))
                    blues.Add(Mark(l, 1, l.Buy, medianBaseline, thr, s));   // luật che áp sau, khi đã biết hết chấm đỏ
            }
            if (s.DotHideBuyNearSellTicks >= 0)
                blues.RemoveAll(bm => reds.Exists(rm => Math.Abs(rm.Tick - bm.Tick) <= s.DotHideBuyNearSellTicks));
            res.AddRange(blues);
            res.AddRange(reds);
            return res;
        }

        static CellMark Mark(CellLevel l, int dir, double sideVal, double medianBaseline, double thr, CellBigSettings s)
            => new CellMark { Tick = l.Tick, Tier = TierDot, Side = dir, Buy = l.Buy, Sell = l.Sell,
                              Mult = s.FixedMode || medianBaseline <= 0 ? 0 : sideVal / medianBaseline, SizeFrac = DotSizeFrac, Threshold = thr };

        // true khi sd LỚN HƠN HẲN giá trị cùng bên của mọi tick khác trong ±w tick (tick vắng = 0)
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
    // Hai chuỗi: volume TB mỗi ô có giao dịch (kiệt sức dùng) và TRUNG VỊ volume mỗi ô (chấm dùng). Cần >= 5 nến.
    public sealed class CellBigBaseline
    {
        private readonly int _n;
        private readonly Queue<double> _mean = new Queue<double>();
        private readonly Queue<double> _median = new Queue<double>();
        private readonly Queue<double> _range = new Queue<double>();
        public CellBigBaseline(int n) { _n = Math.Max(CellBigLogic.MinHistoryBars, n); }
        public int Count => _mean.Count;
        public void Add(double barMeanLevelVol, double barMedianLevelVol, double barRangeTicks = 0)
        {
            _mean.Enqueue(barMeanLevelVol); _median.Enqueue(barMedianLevelVol); _range.Enqueue(barRangeTicks);
            while (_mean.Count > _n) { _mean.Dequeue(); _median.Dequeue(); _range.Dequeue(); }
        }
        /// <summary>Biên độ nến tính theo tick (tick cao nhất - thấp nhất có giao dịch), trung bình 20 nến trước. Bộ NQ dùng để nới cửa sổ theo khung.</summary>
        public bool TryGetRange(out double avgRangeTicks) => Avg(_range, out avgRangeTicks);
        /// <summary>Volume TB mỗi ô có giao dịch (trung bình 20 nến trước).</summary>
        public bool TryGet(out double avgLevelVol) => Avg(_mean, out avgLevelVol);
        /// <summary>Trung vị volume mỗi ô có giao dịch, lấy trung bình của 20 nến trước.</summary>
        public bool TryGetMedian(out double avgMedianLevelVol) => Avg(_median, out avgMedianLevelVol);
        private static bool Avg(Queue<double> q, out double v)
        {
            v = 0;
            if (q.Count < CellBigLogic.MinHistoryBars) return false;
            double s = 0; foreach (var x in q) s += x;
            v = s / q.Count;
            return v > 0;
        }
    }

    // BỘ SỐ CHẤM THEO MÃ (2026-11-24, research/nq_calib_2026-11-24/). Bộ mặc định (2,8 / ±4 / che 6) fit trên vàng GC.
    // NQ: nến M5 rộng gấp ~2,7 lần GC tính theo tick (trung vị 104 so với 39 tick) còn volume mỗi ô gần bằng (trung vị 8 so với 7,5),
    // nên giữ bộ GC thì NQ ra 1,61 chấm/nến M5, gần gấp đôi GC (0,84). Bộ Nasdaq 3,5 / ±8 / che 12 cho 0,82 chấm/nến M5 (đỏ 0,51, xanh 0,31;
    // GC 0,53 / 0,31) và 0,47 chấm/nến M1 (GC 0,46). Sàn 9 giữ nguyên. Đây là khớp MẬT ĐỘ hiển thị với GC, không phải lợi thế đã kiểm định.
    public static class SymbolPreset
    {
        public const double NqDotMedianRatio = 2.8 * 1.25;   // 3,5
        public const int NqDotLocalTicks = 8;           // cửa sổ tối thiểu (M1, M5)
        public const int NqDotHideBuyNearSellTicks = 12;
        // TỰ NỚI THEO KHUNG (2026-11-24, tf_scale.py): cửa sổ ±w = max(8, làm tròn(biên độ TB 20 nến trước / 14)), che giữ 12.
        // Nến càng rộng (M15, M30, H1…) cửa sổ càng to, nên số chấm mỗi nến bám theo vàng GC cùng khung:
        // chấm/nến NQ (GC): M1 0,47 (0,46) · M5 0,78 (0,84) · M15 1,19 (1,11) · M30 1,67 (1,34) · H1 1,54 (1,54).
        // Cửa sổ cố định 8 thì M15 1,45 · M30 2,40 · H1 2,66 (dày gấp 1,3-1,8 lần GC). Khớp mật độ, không phải lợi thế đã kiểm định.
        public const double NqRangePerWindowTick = 14;
        public static int NqLocalTicksFor(double avgRangeTicks)
            => avgRangeTicks > 0 ? Math.Max(NqDotLocalTicks, (int)Math.Round(avgRangeTicks / NqRangePerWindowTick)) : NqDotLocalTicks;

        /// <summary>true nếu tên mã là NQ hoặc MNQ (vd "/NQZ26:XCME", "NQZ26", "/NQ:XCME", "MNQH27"). Không bắt NQLT, NQMLF…</summary>
        public static bool IsNasdaq(string symbolName)
        {
            if (string.IsNullOrWhiteSpace(symbolName)) return false;
            var s = symbolName.Trim().TrimStart('/').ToUpperInvariant();
            int colon = s.IndexOf(':'); if (colon >= 0) s = s.Substring(0, colon);
            string rest = s.StartsWith("MNQ") ? s.Substring(3) : s.StartsWith("NQ") ? s.Substring(2) : null;
            if (rest == null) return false;
            if (rest.Length == 0) return true;                                        // mã liên tục /NQ, /MNQ
            // phần còn lại phải là mã tháng + năm: 1 chữ tháng (F G H J K M N Q U V X Z) + 1-2 chữ số
            if ("FGHJKMNQUVXZ".IndexOf(rest[0]) < 0) return false;
            string y = rest.Substring(1);
            if (y.Length < 1 || y.Length > 2) return false;
            foreach (char c in y) if (c < '0' || c > '9') return false;
            return true;
        }

        /// <summary>Đổi bộ số chấm sang bộ Nasdaq (giữ sàn, chế độ cố định, cờ bật/tắt). DotLocalTicks = 0 (chế độ nổ mọi mức giá) giữ 0.</summary>
        public static void ApplyNasdaq(CellBigSettings s, double avgRangeTicks = 0)
        {
            if (s == null) return;
            s.DotMedianRatio = NqDotMedianRatio;
            if (s.DotLocalTicks > 0) s.DotLocalTicks = NqLocalTicksFor(avgRangeTicks);
            if (s.DotHideBuyNearSellTicks >= 0) s.DotHideBuyNearSellTicks = NqDotHideBuyNearSellTicks;
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
