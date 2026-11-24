// ============================================================================
//  CHẾ ĐỘ NGƯỠNG "KHÔNG THEO CORVEN (THỐNG KÊ)" — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Spec: research/stat_anomaly_2026-11-24/SPEC.md (Fable, 2026-11-25); bản Python chuẩn từng nến: sa3_ref.py.
//  Bóng = volume lớn BẤT THƯỜNG so với chính quá khứ của nó, đo tại thời điểm đó (chỉ dùng nến ĐÃ ĐÓNG trước).
//  Không dùng giá chạy sau, không dùng chart CORVEN. Đây là ĐỊNH NGHĨA HIỂN THỊ, KHÔNG phải lợi thế giao dịch đã kiểm định.
//
//  1) CHẤM Bid/Ask: giá trị của từng bên (Bid, Ask) của từng ô so với tập tham chiếu = mọi Bid và Ask > 0 của CÙNG KHUNG GIỜ
//     trong ngày (giờ Chicago) của 5 ngày giao dịch trước (gộp thêm hai khung liền kề). Nổ khi lớn hơn hẳn giá trị lớn thứ K + 1,
//     K = mức hiếm x số mẫu (2% mặc định). Chưa đủ ngày: dùng 120 phút nến đóng gần nhất. Ô sát nhau gộp trong ±w tick.
//  2) BIG TRADE: lệnh đơn lớn nhất của ô so với mọi lệnh đơn > 0 của 240 phút nến có số liệu gần nhất, mức 1%.
//  Làm tròn: Floor(x + 0,5) (khớp Python), KHÔNG dùng Math.Round.
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    /// <summary>Ngưỡng theo thứ hạng trên mảng đếm (chỉ số = phần nguyên của giá trị, chặn ở 4095).</summary>
    public static class StatRank
    {
        public const int Cap = 4095;

        /// <summary>Chỉ số mảng đếm của một giá trị: min(Floor(v), 4095).</summary>
        public static int Index(double v)
        {
            double f = Math.Floor(v);
            return f >= Cap ? Cap : (int)f;
        }

        /// <summary>Ngưỡng = giá trị lớn thứ K + 1 với K = (pbp x n) / 10000 (pbp = phần vạn, 200 = 2%).
        /// -1 = chưa có ngưỡng (n x pbp &lt; 50000, tức chưa đủ 5 mẫu vượt mức). Ô nổ khi giá trị &gt; ngưỡng.</summary>
        public static int Threshold(int[] hist, long n, int pbp)
        {
            if (hist == null || pbp <= 0 || n <= 0) return -1;
            if (n * pbp < 50000) return -1;
            long k = (pbp * n) / 10000;
            long cum = 0;
            for (int i = Math.Min(hist.Length - 1, Cap); i >= 0; i--)
            {
                cum += hist[i];
                if (cum >= k + 1) return i;
            }
            return -1;
        }
    }

    /// <summary>Giờ Chicago theo luật cố định (không dùng TimeZoneInfo), ngày giao dịch (bắt đầu 17:00 Chicago) và khung giờ trong ngày.</summary>
    public static class StatClock
    {
        static DateTime NthSunday(int year, int month, int nth)
        {
            var d = new DateTime(year, month, 1);
            int add = ((int)DayOfWeek.Sunday - (int)d.DayOfWeek + 7) % 7;
            return d.AddDays(add + 7 * (nth - 1));
        }

        /// <summary>-5 từ 08:00 UTC chủ nhật thứ hai tháng 3 tới trước 07:00 UTC chủ nhật đầu tháng 11; ngoài khoảng đó -6.</summary>
        public static int ChicagoOffsetHours(DateTime utc)
        {
            var a = NthSunday(utc.Year, 3, 2).AddHours(8);
            var b = NthSunday(utc.Year, 11, 1).AddHours(7);
            return (utc.Ticks >= a.Ticks && utc.Ticks < b.Ticks) ? -5 : -6;
        }

        /// <summary>(ngày giao dịch = số ngày của (giờ Chicago + 7 giờ), khung = phút Chicago trong ngày / max(30, phút), số khung = ceil(1440 / max(30, phút))).</summary>
        public static (int day, int slot, int slots) DaySlot(DateTime utc, int minutes)
        {
            int w = Math.Max(30, minutes);
            int slots = (1440 + w - 1) / w;
            var loc = new DateTime(utc.Ticks).AddHours(ChicagoOffsetHours(utc));
            int day = (int)(loc.AddHours(7).Date.Ticks / TimeSpan.TicksPerDay);
            int slot = (loc.Hour * 60 + loc.Minute) / w;
            return (day, slot, slots);
        }

        /// <summary>Khung lân cận (s - 1, s + 1, quay vòng), bỏ cái trùng s hoặc trùng nhau.</summary>
        public static List<int> Neighbors(int slot, int slots)
        {
            var res = new List<int>(2);
            if (slots <= 0) return res;
            int a = ((slot - 1) % slots + slots) % slots, b = (slot + 1) % slots;
            if (a != slot) res.Add(a);
            if (b != slot && !res.Contains(b)) res.Add(b);
            return res;
        }
    }

    /// <summary>Chấm Bid/Ask theo thống kê cùng khung giờ các ngày trước (SPEC mục 2). Một đối tượng cho cả chart; nộp mỗi nến đóng ĐÚNG 1 lần.</summary>
    public sealed class StatDots
    {
        public const int WindowMin = 4;
        public const double RangePerWindow = 6.0;

        private sealed class DayHist { public int Day; public int[] Hist; }

        private readonly int _m, _pbp, _days, _minDays, _nfb, _nRange;
        private readonly bool _neighbors;
        private readonly Dictionary<int, List<DayHist>> _slots = new Dictionary<int, List<DayHist>>();
        private readonly Queue<int[]> _fbBars = new Queue<int[]>();
        private readonly int[] _fbHist = new int[StatRank.Cap + 1];
        private long _fbN;
        private readonly Queue<double> _ranges = new Queue<double>();
        // nhớ ngưỡng chính theo (ngày, khung): chỉ phụ thuộc các ngày trước nên không đổi trong ngày; xóa khi nộp nến của ngày khác
        private bool _mainValid; private int _mainDay, _mainSlot, _mainThr;

        public StatDots(int minutes, int pbp, int days = 5, bool neighbors = true, int minDays = 2, int fallbackMinutes = 120)
        {
            _m = Math.Max(1, minutes);
            _pbp = pbp;
            _days = Math.Max(1, days);
            _neighbors = neighbors;
            _minDays = Math.Max(1, minDays);
            _nfb = Math.Max(5, BaselineWindow.RoundHalfUp((double)fallbackMinutes / _m));
            _nRange = BaselineWindow.BarsFor(_m);
        }

        public int FallbackBars => _nfb;
        public long FallbackSamples => _fbN;

        static bool HasVolume(IReadOnlyList<CellLevel> levels)
        {
            if (levels == null) return false;
            foreach (var l in levels) if (l.Vol > 0) return true;
            return false;
        }

        // K_ngày phần tử cuối của khung có ngày < D
        void LastDays(int slot, int day, List<int[]> into, out int count)
        {
            count = 0;
            if (!_slots.TryGetValue(slot, out var lst)) return;
            int end = lst.Count;
            while (end > 0 && lst[end - 1].Day >= day) end--;
            int start = Math.Max(0, end - _days);
            for (int i = start; i < end; i++) { into.Add(lst[i].Hist); count++; }
        }

        int MainThreshold(int day, int slot, int slots)
        {
            if (_mainValid && _mainDay == day && _mainSlot == slot) return _mainThr;
            int thr = -1;
            var parts = new List<int[]>();
            LastDays(slot, day, parts, out int own);
            if (own >= _minDays && own > 0)
            {
                if (_neighbors)
                    foreach (int s in StatClock.Neighbors(slot, slots)) LastDays(s, day, parts, out _);
                int len = 0; foreach (var h in parts) if (h.Length > len) len = h.Length;
                var sum = new int[len]; long n = 0;
                foreach (var h in parts) for (int i = 0; i < h.Length; i++) { sum[i] += h[i]; n += h[i]; }
                thr = StatRank.Threshold(sum, n, _pbp);
            }
            _mainValid = true; _mainDay = day; _mainSlot = slot; _mainThr = thr;
            return thr;
        }

        /// <summary>Ngưỡng cho nến mở lúc barUtc (chỉ từ nến đã đóng). fallback = true khi dùng ngưỡng 120 phút gần nhất.</summary>
        public bool TryThreshold(DateTime barUtc, out int thr, out bool fallback)
        {
            var (day, slot, slots) = StatClock.DaySlot(barUtc, _m);
            thr = MainThreshold(day, slot, slots);
            fallback = false;
            if (thr >= 0) return true;
            thr = StatRank.Threshold(_fbHist, _fbN, _pbp);
            fallback = thr >= 0;
            return thr >= 0;
        }

        /// <summary>Cửa sổ gộp w = max(4, làm tròn(biên độ TB / 6)) khi đã có >= 5 nến; ngược lại 4.</summary>
        public int Window()
        {
            if (_ranges.Count < 5) return WindowMin;
            double s = 0; foreach (var r in _ranges) s += r;
            double avg = s / _ranges.Count;
            return avg > 0 ? Math.Max(WindowMin, BaselineWindow.RoundHalfUp(avg / RangePerWindow)) : WindowMin;
        }

        /// <summary>Xét một nến (đóng hoặc đang chạy). Nến không có ô volume > 0 hoặc chưa có ngưỡng -> rỗng (thr = -1).</summary>
        public List<CellMark> Evaluate(DateTime barUtc, IReadOnlyList<CellLevel> levels, bool allLevels, out int thr, out bool fallback)
        {
            thr = -1; fallback = false;
            if (!HasVolume(levels)) return new List<CellMark>();
            if (!TryThreshold(barUtc, out thr, out fallback)) { thr = -1; return new List<CellMark>(); }
            return Select(levels, thr, Window(), allLevels);
        }

        /// <summary>Chọn chấm của một nến: ứng viên Floor(bên) &gt; thr; tắt allLevels thì chọn tham lam trong ±w tick
        /// (giá trị giảm dần, bằng nhau tick thấp trước). Trả xanh (tick tăng dần) rồi đỏ (tick tăng dần).</summary>
        public static List<CellMark> Select(IReadOnlyList<CellLevel> levels, int thr, int w, bool allLevels)
        {
            var res = new List<CellMark>();
            if (levels == null || thr < 0) return res;
            var blues = SelectSide(levels, thr, w, allLevels, +1);
            var reds = SelectSide(levels, thr, w, allLevels, -1);
            res.AddRange(blues); res.AddRange(reds);
            return res;
        }

        static List<CellMark> SelectSide(IReadOnlyList<CellLevel> levels, int thr, int w, bool allLevels, int side)
        {
            // ô vượt theo tick (trùng tick giữ giá trị lớn hơn)
            var at = new Dictionary<long, int>();
            var cand = new List<(long tick, double side)>();
            var src = new List<CellLevel>();
            foreach (var l in levels)
            {
                double v = Math.Floor(side > 0 ? l.Buy : l.Sell);
                if (!(v > thr)) continue;
                if (at.TryGetValue(l.Tick, out int i))
                {
                    if (v > cand[i].side) { cand[i] = (l.Tick, v); src[i] = l; }
                }
                else { at[l.Tick] = cand.Count; cand.Add((l.Tick, v)); src.Add(l); }
            }
            var kept = allLevels ? null : CellBigLogic.MergeAdjacent(cand, w);
            var outIdx = new List<int>();
            if (kept == null) for (int i = 0; i < cand.Count; i++) outIdx.Add(i); else outIdx.AddRange(kept);
            outIdx.Sort((a, b) => cand[a].tick.CompareTo(cand[b].tick));
            var res = new List<CellMark>(outIdx.Count);
            foreach (int i in outIdx)
            {
                var l = src[i];
                res.Add(new CellMark { Tick = l.Tick, Tier = CellBigLogic.TierDot, Side = side, Buy = l.Buy, Sell = l.Sell, Mult = 0, SizeFrac = CellBigLogic.DotSizeFrac, Threshold = thr });
            }
            return res;
        }

        /// <summary>Nộp nến vừa đóng (ĐÚNG 1 lần, SAU khi đã xét). Nến không có ô volume > 0 bị bỏ hẳn.</summary>
        public void AddClosedBar(DateTime barUtc, IReadOnlyList<CellLevel> levels)
        {
            if (!HasVolume(levels)) return;
            var (day, slot, _) = StatClock.DaySlot(barUtc, _m);
            var vals = new List<int>();
            foreach (var l in levels) { double v = Math.Floor(l.Sell); if (v > 0) vals.Add(StatRank.Index(v)); }
            foreach (var l in levels) { double v = Math.Floor(l.Buy); if (v > 0) vals.Add(StatRank.Index(v)); }
            int mx = 0; foreach (int v in vals) if (v > mx) mx = v;

            // (ngày, khung)
            if (!_slots.TryGetValue(slot, out var lst)) { lst = new List<DayHist>(); _slots[slot] = lst; }
            DayHist e;
            if (lst.Count > 0 && lst[lst.Count - 1].Day == day) e = lst[lst.Count - 1];
            else
            {
                e = new DayHist { Day = day, Hist = new int[1] };
                lst.Add(e);
                while (lst.Count > _days + 1) lst.RemoveAt(0);
            }
            if (mx + 1 > e.Hist.Length) { var h2 = new int[mx + 1]; Array.Copy(e.Hist, h2, e.Hist.Length); e.Hist = h2; }
            foreach (int v in vals) e.Hist[v]++;

            // dự phòng
            var arr = vals.ToArray();
            _fbBars.Enqueue(arr);
            foreach (int v in arr) _fbHist[v]++;
            _fbN += arr.Length;
            while (_fbBars.Count > _nfb)
            {
                var old = _fbBars.Dequeue();
                foreach (int v in old) _fbHist[v]--;
                _fbN -= old.Length;
            }

            // biên độ
            _ranges.Enqueue(CellBigLogic.BarRangeTicks(levels));
            while (_ranges.Count > _nRange) _ranges.Dequeue();

            if (_mainValid && _mainDay != day) _mainValid = false;
        }
    }

    /// <summary>Big Trade theo thống kê (SPEC mục 3): lệnh đơn so với mọi lệnh đơn > 0 của n nến có số liệu gần nhất, n = max(5, làm tròn(240 / phút)).</summary>
    public sealed class StatBigTrade
    {
        public const int MergeMin = 2;
        public const double RangePerMerge = 8.0;

        private readonly int _n, _pbp, _nRange;
        private readonly Queue<int[]> _bars = new Queue<int[]>();
        private readonly int[] _hist = new int[StatRank.Cap + 1];
        private long _count;
        private readonly Queue<double> _ranges = new Queue<double>();

        public StatBigTrade(int minutes, int pbp = 100, int windowMinutes = 240)
        {
            int m = Math.Max(1, minutes);
            _pbp = pbp;
            _n = Math.Max(5, BaselineWindow.RoundHalfUp((double)windowMinutes / m));
            _nRange = BaselineWindow.BarsFor(m);
        }

        public int WindowBars => _n;
        public int Count => _bars.Count;
        public long Samples => _count;

        public bool TryThreshold(out int thr)
        {
            thr = StatRank.Threshold(_hist, _count, _pbp);
            return thr >= 0;
        }

        /// <summary>g = max(2, làm tròn(biên độ TB / 8)) khi đã có >= 5 nến; ngược lại 2.</summary>
        public int MergeTicks()
        {
            if (_ranges.Count < 5) return MergeMin;
            double s = 0; foreach (var r in _ranges) s += r;
            double avg = s / _ranges.Count;
            return avg > 0 ? Math.Max(MergeMin, BaselineWindow.RoundHalfUp(avg / RangePerMerge)) : MergeMin;
        }

        /// <summary>Nộp nến vừa đóng (ĐÚNG 1 lần). Nến không có ô lệnh đơn > 0 -> không nộp, không tính là một nến của hàng đợi.</summary>
        public void AddClosedBar(IReadOnlyList<(long tick, double mot)> cells)
        {
            if (cells == null) return;
            var vals = new List<int>(); long lo = long.MaxValue, hi = long.MinValue;
            foreach (var c in cells)
                if (c.mot > 0) { vals.Add(StatRank.Index(c.mot)); if (c.tick < lo) lo = c.tick; if (c.tick > hi) hi = c.tick; }
            if (vals.Count == 0) return;
            var arr = vals.ToArray();
            _bars.Enqueue(arr);
            foreach (int v in arr) _hist[v]++;
            _count += arr.Length;
            while (_bars.Count > _n)
            {
                var old = _bars.Dequeue();
                foreach (int v in old) _hist[v]--;
                _count -= old.Length;
            }
            _ranges.Enqueue(hi - lo);
            while (_ranges.Count > _nRange) _ranges.Dequeue();
        }
    }
}
