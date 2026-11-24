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
    // Ba chuỗi: volume TB mỗi ô có giao dịch (kiệt sức dùng, luôn nMean = 20 nến), TRUNG VỊ volume mỗi ô và BIÊN ĐỘ nến (chấm dùng,
    // nMedian nến — tự co theo khung từ 2026-11-24, xem BaselineWindow). Cần >= 5 nến.
    public sealed class CellBigBaseline
    {
        private readonly int _nMean, _nMed;
        private readonly Queue<double> _mean = new Queue<double>();
        private readonly Queue<double> _median = new Queue<double>();
        private readonly Queue<double> _range = new Queue<double>();
        public CellBigBaseline(int n) : this(n, n) { }
        public CellBigBaseline(int nMean, int nMedian)
        {
            _nMean = Math.Max(CellBigLogic.MinHistoryBars, nMean);
            _nMed = Math.Max(CellBigLogic.MinHistoryBars, nMedian);
        }
        public int Count => _mean.Count;
        public int MedianBars => _nMed;
        public void Add(double barMeanLevelVol, double barMedianLevelVol, double barRangeTicks = 0)
        {
            _mean.Enqueue(barMeanLevelVol); _median.Enqueue(barMedianLevelVol); _range.Enqueue(barRangeTicks);
            while (_mean.Count > _nMean) _mean.Dequeue();
            while (_median.Count > _nMed) { _median.Dequeue(); _range.Dequeue(); }
        }
        /// <summary>Biên độ nến tính theo tick (tick cao nhất - thấp nhất có giao dịch), trung bình nMedian nến trước.</summary>
        public bool TryGetRange(out double avgRangeTicks) => Avg(_range, out avgRangeTicks);
        /// <summary>Volume TB mỗi ô có giao dịch (trung bình nMean = 20 nến trước).</summary>
        public bool TryGet(out double avgLevelVol) => Avg(_mean, out avgLevelVol);
        /// <summary>Trung vị volume mỗi ô có giao dịch, lấy trung bình của nMedian nến trước.</summary>
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

    // ========================================================================
    //  NGƯỠNG TỰ THÍCH NGHI THEO KHUNG + TÌNH TRẠNG (2026-11-24, research/adaptive_2026-11-24/, Fable đo + đề xuất)
    //  Mọi luật là KHỚP MẬT ĐỘ HIỂN THỊ với chart CORVEN, KHÔNG phải lợi thế đã kiểm định.
    //  Làm tròn: Floor(x + 0,5) (khớp Python), KHÔNG dùng Math.Round (làm tròn về số chẵn).
    // ========================================================================
    public static class BaselineWindow
    {
        public const double DefaultWindowMinutes = 120;
        public static int RoundHalfUp(double x) => (int)Math.Floor(x + 0.5);
        /// <summary>Số nến ĐÃ ĐÓNG làm nền = min(20, max(5, làm tròn(120 phút / phút một nến))): M1 20 · M5 20 · M15 8 · M30 5 · H1 5.
        /// Không phải nến thời gian (minutes &lt;= 0) -> 20. Lý do đo được: 20 nến M30 = 10 giờ nên nền lấy từ phiên trước
        /// (NQ M30 phiên Á 0,09 chấm/nến, phiên Mỹ 3,77).</summary>
        public static int BarsFor(double minutesPerBar, double windowMinutes = DefaultWindowMinutes)
            => minutesPerBar > 0 ? Math.Min(20, Math.Max(5, (int)Math.Floor(windowMinutes / minutesPerBar + 0.5))) : 20;
    }

    // CHẤM — một công thức cho mọi mã, mọi khung (thay bộ số theo mã khi bật):
    //   w = max(4, làm tròn(biên độ TB / 6)); ngưỡng = max(k x B, sàn); che h = max(che tối thiểu, làm tròn(tỉ lệ che x w)).
    //   B (trung vị mỗi ô) và biên độ TB lấy trên N nến trước (BaselineWindow).
    //   Bộ số (đo với sàn của bộ trong research/adaptive_2026-11-24): 0 = Không sót (k 2,0 · che 2) — recall chấm CORVEN GC M1 0,70 (precision 0,85, sàn 5);
    //          1 = Trung gian (k 2,4 · che 2) — recall 0,61 (0,92, sàn 5); 2 = Ít nhiễu (k 2,8 · che max(6; 0,75 x w)) — recall 0,46 (0,98, sàn 9).
    //   SÀN luôn lấy từ ô "Sàn tối thiểu" của người dùng (sửa 2026-11-24: bản trước để bộ số ghi đè sàn thành 5 dù người dùng đặt 9).
    public static class UnifiedDots
    {
        public const double RangePerWindow = 6.0;
        public const int WindowMin = 4;
        public const int PresetNoMiss = 0, PresetMiddle = 1, PresetQuiet = 2;

        public static (double k, double hideRatio, int hideMin) Preset(int preset) => preset switch
        {
            PresetMiddle => (2.4, 0.0, 2),
            PresetQuiet => (2.8, 0.75, 6),
            _ => (2.0, 0.0, 2),
        };

        public static int Window(double avgRangeTicks)
            => avgRangeTicks > 0 ? Math.Max(WindowMin, BaselineWindow.RoundHalfUp(avgRangeTicks / RangePerWindow)) : WindowMin;

        public static int Hide(int w, double hideRatio, int hideMin) => Math.Max(hideMin, BaselineWindow.RoundHalfUp(hideRatio * w));

        /// <summary>Đặt k / cửa sổ / che theo bộ số; sàn = sàn của người dùng (floorEnabled false = bỏ sàn). allLevels: giữ chế độ "nổ mọi mức giá" (w = 0).</summary>
        public static void Apply(CellBigSettings s, int preset, double avgRangeTicks, bool allLevels, bool floorEnabled, double userFloor)
        {
            if (s == null) return;
            var p = Preset(preset);
            int w = Window(avgRangeTicks);
            s.DotMedianRatio = p.k;
            s.MinSide = floorEnabled ? userFloor : 0;
            s.DotLocalTicks = allLevels ? 0 : w;
            s.DotHideBuyNearSellTicks = Hide(w, p.hideRatio, p.hideMin);
        }
    }

    // BIG TRADE thích nghi — "lớn thứ K trong N nến trước" (Bookmap cùng họ: ngưỡng cuốn theo phân phối gần đây; dùng thứ hạng vì lệnh đơn có đuôi rất dài).
    //   Mỗi nến ĐÃ ĐÓNG có số liệu lệnh đơn (ít nhất một ô > 0) nộp K lệnh đơn lớn nhất của nó; K = max(1, làm tròn(mật độ x N)).
    //   Ngưỡng dùng = max(sàn, giá trị lớn thứ K trong gộp hàng đợi) (trần > 0 thì kẹp); chưa đủ 5 nến có số liệu -> ngưỡng cố định.
    //   Gộp vòng cách nhau <= g = max(gộp tối thiểu, làm tròn(biên độ TB các nến trước / chia)) tick (giữ lệnh lớn hơn), tối đa cap vòng/nến.
    //   Đo (nhật ký lệnh đơn, vòng/nến Á/Âu/Mỹ): NQ M15 cố định 10 = 2,04 / 3,09 / 15,05 -> thích nghi 0,77 / 1,12 / 0,96.
    public sealed class BigTradeAdaptive
    {
        public const int MinBars = 5;
        private readonly int _n, _k;
        private readonly Queue<double[]> _tops = new Queue<double[]>();
        private readonly Queue<double> _ranges = new Queue<double>();

        public BigTradeAdaptive(int n, double density)
        {
            _n = Math.Max(1, n);
            _k = Math.Max(1, BaselineWindow.RoundHalfUp(density * _n));
        }
        public int Count => _tops.Count;
        public int K => _k;

        /// <summary>Giá trị lớn thứ K trong gộp các mảng (0 nếu chưa đủ K giá trị).</summary>
        public static double KthLargest(IEnumerable<double[]> tops, int k)
        {
            var v = new List<double>();
            foreach (var a in tops) v.AddRange(a);
            if (k < 1 || v.Count < k) return 0;
            v.Sort((a, b) => b.CompareTo(a));
            return v[k - 1];
        }

        /// <summary>Ngưỡng dùng cho nến đang xét (chỉ từ các nến ĐÃ ĐÓNG trước).</summary>
        public double Threshold(double fixedMin, double floor, double ceil)
        {
            if (_tops.Count < MinBars) return fixedMin;
            double thr = Math.Max(floor, KthLargest(_tops, _k));
            if (ceil > 0) thr = Math.Min(thr, ceil);
            return thr;
        }

        /// <summary>Khoảng gộp (tick) theo biên độ TB của các nến trước.</summary>
        public int MergeTicks(double div, int gmin)
        {
            if (_ranges.Count < MinBars || div <= 0) return gmin;
            double s = 0; foreach (var r in _ranges) s += r;
            double avg = s / _ranges.Count;
            return avg > 0 ? Math.Max(gmin, BaselineWindow.RoundHalfUp(avg / div)) : gmin;
        }

        /// <summary>Nộp nến vừa đóng (ĐÚNG 1 lần, SAU khi đã xét nến đó). Nến không có ô nào lệnh đơn &gt; 0 -> bỏ qua (không nộp số 0).</summary>
        public void AddClosedBar(IReadOnlyList<(long tick, double mot)> cells)
        {
            if (cells == null) return;
            var vals = new List<double>(); long lo = long.MaxValue, hi = long.MinValue;
            foreach (var c in cells)
                if (c.mot > 0) { vals.Add(c.mot); if (c.tick < lo) lo = c.tick; if (c.tick > hi) hi = c.tick; }
            if (vals.Count == 0) return;
            vals.Sort((a, b) => b.CompareTo(a));
            if (vals.Count > _k) vals.RemoveRange(_k, vals.Count - _k);
            _tops.Enqueue(vals.ToArray()); _ranges.Enqueue(hi - lo);
            while (_tops.Count > _n) { _tops.Dequeue(); _ranges.Dequeue(); }
        }

        /// <summary>Chọn vòng: ô đạt (mot &gt; 0 và &gt;= thr), duyệt mot giảm dần (bằng nhau: tick thấp trước), bỏ ô cách ô đã giữ &lt;= g tick
        /// (g &lt;= 0: không gộp), dừng khi đủ cap vòng (cap &lt;= 0: không giới hạn). Trả CHỈ SỐ trong cells, theo thứ tự giữ.</summary>
        public static List<int> Select(IReadOnlyList<(long tick, double mot)> cells, double thr, int g, int cap) => Select(cells, thr, g, cap, false);

        /// <summary>Như trên; strict = true: ô phải LỚN HƠN HẲN ngưỡng (mot &gt; thr) — chế độ "Không theo CORVEN (thống kê)".</summary>
        public static List<int> Select(IReadOnlyList<(long tick, double mot)> cells, double thr, int g, int cap, bool strict)
        {
            var kept = new List<int>();
            if (cells == null) return kept;
            var order = new List<int>();
            for (int i = 0; i < cells.Count; i++) if (cells[i].mot > 0 && (strict ? cells[i].mot > thr : cells[i].mot >= thr)) order.Add(i);
            order.Sort((a, b) =>
            {
                int c = cells[b].mot.CompareTo(cells[a].mot);
                if (c != 0) return c;
                c = cells[a].tick.CompareTo(cells[b].tick);
                return c != 0 ? c : a.CompareTo(b);
            });
            foreach (int i in order)
            {
                if (cap > 0 && kept.Count >= cap) break;
                bool clash = false;
                if (g > 0) foreach (int j in kept) if (Math.Abs(cells[i].tick - cells[j].tick) <= g) { clash = true; break; }
                if (!clash) kept.Add(i);
            }
            return kept;
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
