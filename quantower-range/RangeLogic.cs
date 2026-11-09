// ============================================================================
//  RangeLogic — máy trạng thái RANGE theo cụm pivot (logic THUẦN, không phụ thuộc Quantower)
// ============================================================================
//  Đặc tả: BRAINSTORM.md mục 4 (ghi đè bởi mục 7b). Bản mẫu Python: research/range_proto.py —
//  file này PORT 1:1 từ bản đó, phải cho ra ĐÚNG danh sách sự kiện research/events_90d.csv.
//  Tham số mặc định lấy từ research/MEASURE.md (bộ chọn) + research/corven_boxes.csv.
//
//  Mọi giá đổi sang SỐ TICK NGUYÊN khi vào (Math.Round(price/tick), làm tròn chẵn như Python round)
//  để hai bản tính giống hệt nhau; median số nguyên là x.0 / x.5 nên so sánh double không lệch.
//
//  Thứ tự xử lý MỖI NẾN ĐÃ ĐÓNG i:
//   1. mbr = median(high−low) 100 nến gần nhất, tính cả nến i (cuốn chiếu, không nhìn tương lai).
//   2. pivot nến j=i−1: đỉnh nếu H[j] > H[j−1] và H[j] ≥ H[i]; đáy nếu L[j] < L[j−1] và L[j] ≤ L[i].
//   3. mỗi range còn sống: (Active) cập nhật cạnh bằng pivot mới → xét sự kiện của nến i.
//   4. nếu KHÔNG còn range Active/Pending: tìm range ứng viên kết thúc ở i → gộp hoặc sinh mới.
//  Tất định: chạy một mạch = chạy từng nến (Feed lần lượt).
// ============================================================================
namespace RangeBox
{
    using System;
    using System.Collections.Generic;

    public enum RangeState { Active = 0, Pending = 1, Broken = 2, Dead = 3 }

    public enum RangeEventKind { Birth, StopHunt, CloseOutside, FailBreak, BreakConfirmed, ReEntry, Merge }

    public readonly struct RBar
    {
        public readonly double Open, High, Low, Close;
        public RBar(double open, double high, double low, double close) { Open = open; High = high; Low = low; Close = close; }
    }

    /// <summary>Tham số — hằng mặc định, KHÔNG phải ô Settings. Nguồn từng số: research/MEASURE.md.</summary>
    public sealed class RangeParams
    {
        public int MinBars { get; set; } = 8;          // lõi tối thiểu: lõi ngắn nhất CORVEN 8 nến (B17)
        public double HminK { get; set; } = 1.6;       // cao tối thiểu × mbr: tỷ lệ nhỏ nhất CORVEN 1,6 (B04, B08)
        public double HmaxK { get; set; } = 6.0;       // cao tối đa × mbr: max CORVEN 5,9 (B01)
        public double TolK { get; set; } = 0.5;        // dung sai cạnh × mbr: 7b (râu vượt cạnh trung vị 4–10 tick / nến 17 tick)
        public int K { get; set; } = 3;                // nến chờ sau đóng ngoài: fail break CORVEN quay vào sau 2–4 nến
        public int G { get; set; } = 30;               // nến cho phép quay lại sau phá: 16/20 hộp kéo quá nến phá 3–22 nến
        public bool PivotRuleB { get; set; } = false;  // false = mỗi cạnh ≥1, tổng ≥3, ≥1 cạnh ≥2 (3/20 hộp có cạnh 1 chạm)
        public double InsideRatio { get; set; } = 0.0; // tắt: đo không khác (MEASURE.md)
        public int MaxLook { get; set; } = 60;         // cửa sổ pivot: ≥ lõi dài nhất CORVEN 54 nến
        public int MbrLen { get; set; } = 100;         // BRAINSTORM mục 4
        public double MinTolTicks { get; set; } = 2.0; // BRAINSTORM mục 4: tol = max(2 tick, TolK×mbr)
        /// <summary>Số lần ReEntry tối đa; lần phá thật thứ MaxReEntry+1 ⇒ Dead NGAY (không chờ G, Merge không hồi sinh). &lt; 0 = không giới hạn.
        /// Nguồn: CORVEN chỉ nói "confirm lần 2" (B05); hộp CORVEN dài nhất 73 nến; không giới hạn thì 26,5 % hộp máy dài hơn,
        /// có range 21 lần ReEntry (REVIEW-1, tester mục 11).</summary>
        public int MaxReEntry { get; set; } = 2;
        /// <summary>≤ 0 = TẮT (Range Box gốc không đổi). &gt; 0: range đang Broken mà cực trị High/Low kể từ nến phá vượt cạnh vừa phá ≥ DeadRunMult × (top − bottom)
        /// ⇒ Dead NGAY, đánh dấu Exhausted (không ReEntry, Merge không hồi sinh).</summary>
        public double DeadRunMult { get; set; } = 0.0;
    }

    public sealed class RangeInfo
    {
        public int Id, Start, Birth;
        public double Top, Bottom, Top0, Bottom0, Tol, Mbr;   // đơn vị TICK
        public readonly List<long> TopM = new List<long>();
        public readonly List<long> BotM = new List<long>();
        public RangeState State = RangeState.Active;
        public int PendSide, PendStart = -1;
        public int BreakIdx = -1, BreakSide, FirstBreak = -1;
        public int LastIdx = -1;
        public int NHunt, NFail, NBreak;
        public bool Exhausted;   // Dead vì hết lượt ReEntry — không bao giờ sống lại
    }

    public readonly struct RangeEvent
    {
        public readonly int Bar;
        public readonly RangeEventKind Kind;
        public readonly int Side;            // +1 cạnh trên, −1 cạnh dưới, 0
        public readonly double Top, Bottom;  // TICK, lúc phát sự kiện
        public readonly int Start, Ref, RangeId;
        public RangeEvent(int bar, RangeEventKind kind, int side, double top, double bottom, int start, int rf, int rid)
        { Bar = bar; Kind = kind; Side = side; Top = top; Bottom = bottom; Start = start; Ref = rf; RangeId = rid; }
    }

    public sealed class RangeLogic
    {
        public RangeParams P { get; }
        public double Tick { get; }

        private readonly List<long> _h = new List<long>(), _l = new List<long>(), _c = new List<long>();
        private readonly List<(int idx, long p)> _ph = new List<(int, long)>(), _pl = new List<(int, long)>();
        private readonly Queue<long> _win = new Queue<long>();
        private readonly List<long> _sortedWin = new List<long>();
        private double _mbr;
        private readonly List<RangeInfo> _ranges = new List<RangeInfo>();
        private List<RangeInfo> _live = new List<RangeInfo>();
        private readonly List<RangeEvent> _events = new List<RangeEvent>();
        private int _scanStart;

        public RangeLogic(double tick, RangeParams p = null)
        {
            if (!(tick > 0)) throw new ArgumentException("tick phải > 0");
            Tick = tick;
            P = p ?? new RangeParams();
        }

        public int Count => _c.Count;
        public double Mbr => _mbr;
        public IReadOnlyList<RangeInfo> Ranges => _ranges;
        public IReadOnlyList<RangeEvent> Events => _events;
        public long HighTicks(int i) => _h[i];
        public long LowTicks(int i) => _l[i];
        public long CloseTicks(int i) => _c[i];

        public void Process(IList<RBar> bars) { foreach (var b in bars) Feed(b); }

        public void Feed(RBar b) => Feed(b.Open, b.High, b.Low, b.Close);

        /// <summary>Nến có giá NaN/∞ (HistoryItemBar mặc định NaN) KHÔNG được bỏ (chỉ số nến phải khớp chart) mà thay bằng
        /// doji ở close trước — trước đây (long)NaN = 0 ⇒ close 0 ⇒ phá range giả (tester E1, 2026-11-08).</summary>
        public void Feed(double open, double high, double low, double close)
        {
            if (!double.IsFinite(close)) close = _c.Count > 0 ? _c[_c.Count - 1] * Tick : 0.0;
            if (!double.IsFinite(open)) open = close;
            if (!double.IsFinite(high)) high = close;
            if (!double.IsFinite(low)) low = close;
            FeedTicks((long)Math.Round(open / Tick), (long)Math.Round(high / Tick), (long)Math.Round(low / Tick), (long)Math.Round(close / Tick));
        }

        // ------------------------------------------------------------ median
        private static double Median(List<long> vals)
        {
            int n = vals.Count;
            if (n == 0) return 0.0;
            var a = new List<long>(vals); a.Sort();
            return (n % 2 == 1) ? a[n / 2] : (a[n / 2 - 1] + a[n / 2]) / 2.0;
        }

        private void PushRange(long r)
        {
            _win.Enqueue(r);
            int pos = _sortedWin.BinarySearch(r); if (pos < 0) pos = ~pos;
            _sortedWin.Insert(pos, r);
            while (_win.Count > Math.Max(1, P.MbrLen))   // while: MbrLen giảm giữa chừng thì cửa sổ co lại ngay (tester E6)
            {
                long old = _win.Dequeue();
                int k = _sortedWin.BinarySearch(old);
                // BinarySearch có thể trả về bất kỳ phần tử trùng nào — mọi bản trùng đều bằng nhau nên xoá cái nào cũng được
                _sortedWin.RemoveAt(k);
            }
            int n = _sortedWin.Count;
            _mbr = (n % 2 == 1) ? _sortedWin[n / 2] : (_sortedWin[n / 2 - 1] + _sortedWin[n / 2]) / 2.0;
        }

        // ------------------------------------------------------------ nạp 1 nến
        public void FeedTicks(long o, long h, long l, long c)
        {
            // nến hỏng (high < open/close/low …): high = max, low = min của 4 giá. Dữ liệu hợp lệ không đổi gì
            // (90 ngày GC: 0 nến vi phạm ⇒ events_90d.csv giữ nguyên). Tester E1/E2.
            long hh = Math.Max(Math.Max(h, l), Math.Max(o, c)), ll = Math.Min(Math.Min(h, l), Math.Min(o, c));
            h = hh; l = ll;
            int i = _c.Count;
            _h.Add(h); _l.Add(l); _c.Add(c);
            PushRange(h - l);
            (int idx, long p)? newPh = null, newPl = null;
            if (i >= 2)
            {
                int j = i - 1;
                if (_h[j] > _h[j - 1] && _h[j] >= _h[i]) { newPh = (j, _h[j]); _ph.Add(newPh.Value); }
                if (_l[j] < _l[j - 1] && _l[j] <= _l[i]) { newPl = (j, _l[j]); _pl.Add(newPl.Value); }
            }
            int lim = i - P.MaxLook - 2;
            while (_ph.Count > 0 && _ph[0].idx < lim) _ph.RemoveAt(0);
            while (_pl.Count > 0 && _pl[0].idx < lim) _pl.RemoveAt(0);

            bool busy = false, anyDead = false;
            foreach (var r in _live)
            {
                StepRange(r, i, newPh, newPl);
                if (r.State == RangeState.Active || r.State == RangeState.Pending) busy = true;
                if (r.State == RangeState.Dead) anyDead = true;
            }
            if (anyDead) _live = _live.FindAll(r => r.State != RangeState.Dead);
            if (!busy) Scan(i);
        }

        private void Ev(int i, RangeEventKind k, int side, RangeInfo r, int rf = int.MinValue)
            => _events.Add(new RangeEvent(i, k, side, r.Top, r.Bottom, r.Start, rf == int.MinValue ? i : rf, r.Id));

        private static double Clamp(double v, double lo, double hi) => Math.Min(Math.Max(v, lo), hi);

        private void StepRange(RangeInfo r, int i, (int idx, long p)? newPh, (int idx, long p)? newPl)
        {
            long H = _h[i], L = _l[i], C = _c[i];
            if (r.State == RangeState.Active)
            {
                if (newPh.HasValue && Math.Abs(newPh.Value.p - r.Top) <= r.Tol)
                {
                    r.TopM.Add(newPh.Value.p);
                    r.Top = Clamp(Median(r.TopM), r.Top0 - r.Tol, r.Top0 + r.Tol);
                }
                if (newPl.HasValue && Math.Abs(newPl.Value.p - r.Bottom) <= r.Tol)
                {
                    r.BotM.Add(newPl.Value.p);
                    r.Bottom = Clamp(Median(r.BotM), r.Bottom0 - r.Tol, r.Bottom0 + r.Tol);
                }
                if (C > r.Top) { r.State = RangeState.Pending; r.PendSide = +1; r.PendStart = i; Ev(i, RangeEventKind.CloseOutside, +1, r); }
                else if (C < r.Bottom) { r.State = RangeState.Pending; r.PendSide = -1; r.PendStart = i; Ev(i, RangeEventKind.CloseOutside, -1, r); }
                else
                {
                    r.LastIdx = i;
                    if (H - r.Top >= 1) { r.NHunt++; Ev(i, RangeEventKind.StopHunt, +1, r); }
                    if (r.Bottom - L >= 1) { r.NHunt++; Ev(i, RangeEventKind.StopHunt, -1, r); }
                }
            }
            else if (r.State == RangeState.Pending)
            {
                int s = r.PendSide;
                if (r.Bottom <= C && C <= r.Top)
                {
                    r.NFail++;
                    Ev(i, RangeEventKind.FailBreak, s, r, r.PendStart);
                    r.State = RangeState.Active; r.PendSide = 0; r.LastIdx = i;
                }
                else if ((s > 0 && C < r.Bottom) || (s < 0 && C > r.Top))
                {
                    r.NFail++;
                    Ev(i, RangeEventKind.FailBreak, s, r, r.PendStart);
                    r.PendSide = -s; r.PendStart = i;
                    Ev(i, RangeEventKind.CloseOutside, -s, r);
                }
                else if (i - r.PendStart >= P.K)
                {
                    r.NBreak++;
                    r.State = RangeState.Broken; r.BreakIdx = r.PendStart; r.BreakSide = s;
                    if (r.FirstBreak < 0) r.FirstBreak = r.PendStart;
                    Ev(i, RangeEventKind.BreakConfirmed, s, r, r.PendStart);
                    _scanStart = Math.Max(_scanStart, r.PendStart);
                    if (P.MaxReEntry >= 0 && r.NBreak > P.MaxReEntry) { r.State = RangeState.Dead; r.Exhausted = true; }
                    else if (P.G <= 0 || i - r.BreakIdx >= P.G) r.State = RangeState.Dead;
                    else if (DeadRun(r, i)) { r.State = RangeState.Dead; r.Exhausted = true; }
                }
            }
            else if (r.State == RangeState.Broken)
            {
                if (DeadRun(r, i)) { r.State = RangeState.Dead; r.Exhausted = true; }   // chạy xa khỏi cạnh vừa phá ⇒ range kết thúc, không ReEntry
                else if (r.Bottom <= C && C <= r.Top)
                {
                    Ev(i, RangeEventKind.ReEntry, r.BreakSide, r, r.BreakIdx);
                    r.State = RangeState.Active; r.LastIdx = i;
                }
                else if (i - r.BreakIdx >= P.G) r.State = RangeState.Dead;
            }
        }

        private bool DeadRun(RangeInfo r, int i)
        {
            double m = P.DeadRunMult;
            if (!(m > 0) || r.BreakIdx < 0) return false;
            double h = r.Top - r.Bottom;
            if (r.BreakSide > 0) { long mx = long.MinValue; for (int j = r.BreakIdx; j <= i; j++) mx = Math.Max(mx, _h[j]); return mx - r.Top >= m * h - 1e-9; }
            long mn = long.MaxValue; for (int j = r.BreakIdx; j <= i; j++) mn = Math.Min(mn, _l[j]); return r.Bottom - mn >= m * h - 1e-9;
        }

        // ------------------------------------------------------------ tìm range mới
        private static (List<(int idx, long p)> members, double med) BestCluster(List<(int idx, long p)> piv, double tol)
        {
            List<(int idx, long p)> best = null;
            int bCount = -1, bLast = -1;
            var m1 = new List<long>();
            foreach (var seed in piv)
            {
                m1.Clear();
                foreach (var q in piv) if (Math.Abs(q.p - seed.p) <= tol) m1.Add(q.p);
                double med1 = Median(m1);
                var m2 = new List<(int idx, long p)>();
                foreach (var q in piv) if (Math.Abs(q.p - med1) <= tol) m2.Add(q);
                int cnt = m2.Count, last = m2[m2.Count - 1].idx;
                if (best == null || cnt > bCount || (cnt == bCount && last > bLast)) { best = m2; bCount = cnt; bLast = last; }
            }
            var prices = new List<long>(best.Count);
            foreach (var q in best) prices.Add(q.p);
            return (best, Median(prices));
        }

        private sealed class Cand { public int Start; public double Top, Bot, Tol, Mbr; public List<long> Tm, Bm; }

        private Cand Candidate(int i)
        {
            if (i + 1 < P.MbrLen) return null;
            double mbr = _mbr;
            double tol = Math.Max(P.MinTolTicks, P.TolK * mbr);
            int loLim = Math.Max(_scanStart, i - P.MaxLook + 1);
            int lo = loLim;
            List<(int idx, long p)> tm = null, bm = null;
            double top = 0, bot = 0, hiB = 0, loB = 0;
            int first = 0;
            bool settled = false;
            for (int it = 0; it < 3; it++)
            {
                var Hs = _ph.FindAll(x => x.idx >= lo);
                var Ls = _pl.FindAll(x => x.idx >= lo);
                if (Hs.Count == 0 || Ls.Count == 0) return null;
                (tm, top) = BestCluster(Hs, tol);
                (bm, bot) = BestCluster(Ls, tol);
                if (top <= bot) return null;
                first = Math.Min(tm[0].idx, bm[0].idx);
                hiB = top + tol; loB = bot - tol;
                int k = -1;
                for (int j = i; j >= first; j--)
                    if (_c[j] > hiB || _c[j] < loB) { k = j; break; }
                if (k < 0) { settled = true; break; }
                lo = k + 1;
            }
            if (!settled) return null;
            int nt = tm.Count, nb = bm.Count;
            if (P.PivotRuleB) { if (nt < 2 || nb < 2) return null; }
            else if (nt < 1 || nb < 1 || nt + nb < 3 || Math.Max(nt, nb) < 2) return null;
            // đan xen: dãy loại pivot theo thời gian đổi chiều ≥ 2 lần (cùng nến: đáy trước đỉnh, như sorted() Python)
            var seq = new List<(int idx, int t)>(nt + nb);
            foreach (var x in tm) seq.Add((x.idx, 1));
            foreach (var x in bm) seq.Add((x.idx, -1));
            seq.Sort((a, b) => a.idx != b.idx ? a.idx.CompareTo(b.idx) : a.t.CompareTo(b.t));
            int ch = 0;
            for (int q = 1; q < seq.Count; q++) if (seq[q].t != seq[q - 1].t) ch++;
            if (ch < 2) return null;
            double h = top - bot;
            if (h < P.HminK * mbr || h > P.HmaxK * mbr) return null;
            // nến bắt đầu = cây "chạy vào vùng": lùi về trước khi close còn trong dải
            int jj = first - 1;
            while (jj >= loLim && loB <= _c[jj] && _c[jj] <= hiB) jj--;
            int start = jj + 1;
            int core = i - start;
            if (core < P.MinBars) return null;
            if (P.InsideRatio > 0)
            {
                int nIn = 0;
                for (int q = start + 1; q <= i; q++) if (bot <= _c[q] && _c[q] <= top) nIn++;
                if (nIn < P.InsideRatio * core) return null;
            }
            var tmp = new List<long>(); foreach (var x in tm) tmp.Add(x.p);
            var bmp = new List<long>(); foreach (var x in bm) bmp.Add(x.p);
            return new Cand { Start = start, Top = top, Bot = bot, Tol = tol, Mbr = mbr, Tm = tmp, Bm = bmp };
        }

        private void Scan(int i)
        {
            var c = Candidate(i);
            if (c == null) return;
            if (_ranges.Count > 0)
            {
                var r = _ranges[_ranges.Count - 1];
                if ((r.State == RangeState.Broken || r.State == RangeState.Dead) && !r.Exhausted && r.BreakIdx >= 0 && c.Start <= r.BreakIdx + P.G
                    && Math.Abs(c.Top - r.Top) <= r.Tol && Math.Abs(c.Bot - r.Bottom) <= r.Tol)
                {
                    if (r.State == RangeState.Dead) _live.Add(r);
                    r.State = RangeState.Active; r.LastIdx = i;
                    Ev(i, RangeEventKind.Merge, 0, r, r.BreakIdx);
                    return;
                }
            }
            var nr = new RangeInfo
            {
                Id = _ranges.Count, Start = c.Start, Birth = i, Top = c.Top, Bottom = c.Bot, Top0 = c.Top, Bottom0 = c.Bot,
                Tol = c.Tol, Mbr = c.Mbr, LastIdx = i,
            };
            nr.TopM.AddRange(c.Tm); nr.BotM.AddRange(c.Bm);
            _ranges.Add(nr);
            _live.Add(nr);
            Ev(i, RangeEventKind.Birth, 0, nr);
        }
    }
}
