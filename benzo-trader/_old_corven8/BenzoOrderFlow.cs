// ============================================================================
//  BenzoOrderFlow — các dấu hiệu order flow của setup CORVEN chưa có trong StackedImbalance.cs /
//  ExhaustionLogic.cs: nền_ô, bóng, delta ngược giá, trap; cộng hàm định dạng số kiểu Python.
// ============================================================================
//  PORT Y CHỮ từ benzo-trader/research/of_signals.py (phần (2) "MỚI") — parity: research/parity_corven.py.
//  Mọi giá là SỐ TICK nguyên (long), như Python. Hai file nguồn StackedImbalance.cs + ExhaustionLogic.cs
//  được NỐI lúc build (build.sh), không copy tay.
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.Numerics;
    using OrderFlowBubbles;

    /// <summary>Một nến M1 ĐÃ ĐÓNG cho setup CORVEN: giá theo tick, delta, các mức footprint (tick, bid, ask, volume)
    /// theo đúng thứ tự nguồn cấp (file export / platform: giá tăng dần).</summary>
    public sealed class CorvenBar
    {
        public int Idx;
        public DateTime Time;          // giờ MỞ nến (UTC)
        public long O, H, L, C;        // tick
        public double Delta;
        public List<ExhLevel> Levels = new List<ExhLevel>();
    }

    public static class Of
    {
        public const double Eps = 1e-9;

        // ------------------------------------------------------------ stacked / kiệt sức (gọi mã gốc)
        /// <summary>Mảng ask/bid liên tiếp từ Low lên High (mức trống = 0) — = of_signals.ladder.</summary>
        public static void Ladder(CorvenBar b, out double[] ask, out double[] bid)
        {
            int n = (int)Math.Max(0, b.H - b.L + 1);
            ask = new double[n]; bid = new double[n];
            foreach (var x in b.Levels)
                if (x.Tick >= b.L && x.Tick <= b.H) { ask[x.Tick - b.L] += x.Ask; bid[x.Tick - b.L] += x.Bid; }
        }

        /// <summary>= of_signals.stacked_zones: vùng stacked của nến (đã Classify theo open/close giá thực = tick × bước giá).</summary>
        public static List<SiZone> StackedZones(CorvenBar b, double tick, double ratioPct, int run, double minVol)
        {
            if (b.H <= b.L) return new List<SiZone>();
            Ladder(b, out var ask, out var bid);
            var zs = StackedImbalanceCalc.Detect(b.L * tick, tick, ask, bid, ratioPct, run, minVol);
            foreach (var z in zs) StackedImbalanceCalc.Classify(z, b.O * tick, b.C * tick);
            return zs;
        }

        private static readonly ExhSettings DefaultExh = new ExhSettings();
        /// <summary>(kiệt sức đỉnh, kiệt sức đáy) với cấu hình mặc định ExhaustionLogic.</summary>
        public static (ExhResult top, ExhResult bot) Exhaustion(CorvenBar b) =>
            (ExhaustionLogic.Detect(true, b.O, b.H, b.L, b.C, b.Levels, DefaultExh),
             ExhaustionLogic.Detect(false, b.O, b.H, b.L, b.C, b.Levels, DefaultExh));

        // ------------------------------------------------------------ nền_ô
        public static double Median(List<double> sorted)
        {
            int n = sorted.Count;
            if (n == 0) return 0.0;
            return n % 2 == 1 ? sorted[n / 2] : (sorted[n / 2 - 1] + sorted[n / 2]) / 2.0;
        }

        /// <summary>Trung vị của 3 ô side-volume lớn nhất (side-volume = max(bid, ask)); nến không có ô nào ⇒ null.</summary>
        public static double? CellValue(CorvenBar b, int topN = 3)
        {
            var sv = new List<double>();
            foreach (var x in b.Levels) if (x.Bid > 0 || x.Ask > 0) sv.Add(Math.Max(x.Bid, x.Ask));
            if (sv.Count == 0) return null;
            sv.Sort((p, q) => q.CompareTo(p));
            if (sv.Count > topN) sv.RemoveRange(topN, sv.Count - topN);
            sv.Sort();
            return Median(sv);
        }

        // ------------------------------------------------------------ bóng
        /// <summary>③b — ô phía side (+1: ask, −1: bid) ≥ max(mult × nền, min). Trả [(tick, volume)] theo thứ tự mức của nến.</summary>
        public static List<(long tk, double v)> Bubbles(CorvenBar b, int side, double baseV, double mult = 3.0, double minContracts = 10.0)
        {
            double thr = Math.Max(mult * baseV, minContracts);
            var res = new List<(long, double)>();
            foreach (var x in b.Levels)
            {
                double v = side > 0 ? x.Ask : x.Bid;
                if (v > 0 && v >= thr - Eps) res.Add((x.Tick, v));
            }
            return res;
        }

        /// <summary>Ô ở nửa nến phía side (buy: ≤ trung điểm) HOẶC trong dải [bandLo, bandHi] (tick).</summary>
        public static bool BubbleInPlace(CorvenBar b, int side, long tk, double bandLo = double.NaN, double bandHi = double.NaN)
        {
            double mid = (b.H + b.L) / 2.0;
            bool half = side > 0 ? tk <= mid + Eps : tk >= mid - Eps;
            bool band = !double.IsNaN(bandLo) && bandLo - Eps <= tk && tk <= bandHi + Eps;
            return half || band;
        }

        // ------------------------------------------------------------ delta ngược giá
        /// <summary>= of_signals.delta_divergence. Trả (ok, s, ΣΔ).</summary>
        public static (bool ok, int s, double sd) DeltaDivergence(IReadOnlyList<long> H, IReadOnlyList<long> L, IReadOnlyList<double> D,
                                                                   int x, int side, double mbrTicks, int minLen = 2, int maxLen = 8, double ampMbr = 1.0)
        {
            int lo = x - maxLen, hi = x - minLen;
            if (lo < 0) lo = 0;
            if (hi < lo) return (false, -1, 0.0);
            int s = -1;
            double amp;
            if (side < 0)
            {   // sell: nhịp lên — s = đáy thấp nhất, hoà ⇒ nến MUỘN nhất
                for (int j = lo; j <= hi; j++) if (s < 0 || L[j] < L[s] || (L[j] == L[s] && j > s)) s = j;
                long mx = long.MinValue; for (int j = s; j <= x; j++) mx = Math.Max(mx, H[j]);
                if (mx != H[x]) return (false, -1, 0.0);
                amp = H[x] - L[s];
            }
            else
            {
                for (int j = lo; j <= hi; j++) if (s < 0 || H[j] > H[s] || (H[j] == H[s] && j > s)) s = j;
                long mn = long.MaxValue; for (int j = s; j <= x; j++) mn = Math.Min(mn, L[j]);
                if (mn != L[x]) return (false, -1, 0.0);
                amp = H[s] - L[x];
            }
            if (amp < ampMbr * mbrTicks - Eps) return (false, -1, 0.0);
            double sd = 0.0;
            for (int j = s + 1; j <= x; j++) sd += D[j];
            bool ok = side < 0 ? sd <= 0 : sd >= 0;
            return (ok, s, sd);
        }

        // ------------------------------------------------------------ trap
        /// <summary>= of_signals.trap: râu quét mốc ≥ sweep tick, đóng lại phía side, ô phía −side trong râu ≥ mult × nền và ≥ min.</summary>
        public static (bool ok, long tk, double v) Trap(CorvenBar b, int side, double level, double baseV, double mult = 3.0,
                                                         int sweepTicks = 1, double minContracts = 0.0)
        {
            long edge;
            bool any = false; long bk = 0; double bv = 0;
            if (side < 0)
            {
                if (!(b.H >= level + sweepTicks && b.C < level)) return (false, -1, 0.0);
                edge = Math.Max(b.O, b.C);
                foreach (var x in b.Levels)
                {
                    if (x.Tick <= edge) continue;
                    // max theo (v, −k): v lớn nhất, hoà ⇒ tick nhỏ nhất
                    if (!any || x.Ask > bv || (x.Ask == bv && x.Tick < bk)) { any = true; bk = x.Tick; bv = x.Ask; }
                }
            }
            else
            {
                if (!(b.L <= level - sweepTicks && b.C > level)) return (false, -1, 0.0);
                edge = Math.Min(b.O, b.C);
                foreach (var x in b.Levels)
                {
                    if (x.Tick >= edge) continue;
                    if (!any || x.Bid > bv || (x.Bid == bv && x.Tick > bk)) { any = true; bk = x.Tick; bv = x.Bid; }
                }
            }
            if (!any || baseV <= 0) return (false, -1, 0.0);
            if (bv >= mult * baseV - Eps && bv >= minContracts - Eps && bv > 0) return (true, bk, bv);
            return (false, -1, 0.0);
        }

        // ------------------------------------------------------------ định dạng số kiểu Python
        /// <summary>= format(x, '.{d}f') của Python: làm tròn ĐÚNG giá trị nhị phân, hoà ⇒ chẵn (khác "F" của .NET ở ca hoà).</summary>
        public static string PyFixed(double x, int d)
        {
            if (double.IsNaN(x)) return "nan";
            if (double.IsInfinity(x)) return x > 0 ? "inf" : "-inf";
            bool neg = x < 0 || (x == 0 && double.IsNegative(x));
            long bits = BitConverter.DoubleToInt64Bits(Math.Abs(x));
            int exp = (int)((bits >> 52) & 0x7FF);
            long man = bits & 0xFFFFFFFFFFFFFL;
            if (exp == 0) exp = 1; else man |= 1L << 52;
            exp -= 1075;
            BigInteger num = man, den = BigInteger.One;
            if (exp > 0) num <<= exp; else den <<= -exp;
            num *= BigInteger.Pow(10, d);
            var q = BigInteger.DivRem(num, den, out var r);
            int cmp = (r * 2).CompareTo(den);
            if (cmp > 0 || (cmp == 0 && !q.IsEven)) q += 1;
            string s = q.ToString(CultureInfo.InvariantCulture).PadLeft(d + 1, '0');
            string res = d > 0 ? s.Substring(0, s.Length - d) + "." + s.Substring(s.Length - d) : s;
            return (neg ? "-" : "") + res;
        }

        /// <summary>= format(x, '+.{d}f').</summary>
        public static string PySigned(double x, int d)
        {
            string s = PyFixed(x, d);
            return s.StartsWith("-") ? s : "+" + s;
        }

        /// <summary>Giá kiểu Việt từ số tick: = setup_corven._px (f"{t*TICK:.1f}" đổi '.' → ',').</summary>
        public static string Px(double ticks, double tick, int digits = 1) => PyFixed(ticks * tick, digits).Replace('.', ',');
    }
}
