// ============================================================================
//  BenzoLayers — các LỚP VÙNG MỚI của setup C "Fade cạnh" (port C# của research/zones_c_v6.py + zones_c_v7.py)
// ============================================================================
//  Plan: research/PLAN-C-v2.md (v6) và PLAN-C-v3.md (v7). Mỗi lớp = một nguồn "band" cân bằng cho detector C:
//    · Cổng hình D / vùng dày P-b  — hình dạng profile TPO phiên hôm qua (30′): D ⇒ fade VA hôm qua; P/b ⇒ fade cạnh vùng dày T.
//    · VA nhỏ CHoCH               — climax → AR → ST (3 lần đổi hành vi) sinh VA nhỏ [min(L1,L2), H1]; nới tối đa 25% rồi chết.
//    · Hành lang S/R              — khoảng giữa kháng cự gần nhất (mặt dưới) và hỗ trợ gần nhất (mặt trên) của bộ vùng VCL v5.
//  Mọi thứ chạy THEO DÒNG, chỉ dùng nến <= idx (cấm nhìn trước). Chỉ chạy khi được bật qua Configure (tắt = không tốn CPU,
//  không đổi hành vi C0). Hằng số khớp đăng ký trước của Python (ghi ở từng chỗ).
//  Python "đóng băng" mode_kills bằng lặp đến hội tụ; ở đây chạy một lượt nhân quả cho cùng kết quả (xem ChochFrame.Step).
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using VungCanhLenhNs;

    /// <summary>Cấu hình các lớp của setup C. Mặc định (Legacy) = C0 cũ: không lớp mới, TP 2R cố định.</summary>
    public sealed class CLayerOptions
    {
        public bool GateD;      // cổng hình D: chỉ fade VA hôm qua (pha Á/Âu) khi profile TPO hôm qua có hình D
        public bool ThickPb;    // vùng dày P/b: ngày hình P hoặc b fade cạnh vùng dày T của profile TPO hôm qua
        public bool Choch;      // VA nhỏ từ 3 lần đổi hành vi (CHoCH)
        public bool Sr;         // hành lang hỗ trợ/kháng cự từ vùng Canh Lệnh (VCL)
        public bool TpToEdge;   // TP về cạnh đối diện / POC (≥ 2R) — ô chính đo trên D90; false = 2R cố định (C0 cũ)

        public static CLayerOptions Legacy => new CLayerOptions();
        public bool NeedShape => GateD || ThickPb;
        public bool AnyNew => GateD || ThickPb || Choch || Sr;
        public string Key => (GateD ? "1" : "0") + (ThickPb ? "1" : "0") + (Choch ? "1" : "0") + (Sr ? "1" : "0") + (TpToEdge ? "e" : "f");
    }

    /// <summary>Detector cần các lớp vùng của BenzoZones: engine gọi trước nến đầu tiên (biết setup đó đang bật hay không).</summary>
    public interface IZoneConsumer
    {
        void ConfigureZones(BenzoZones z, bool enabled);
    }

    // ================================================================= hình dạng profile TPO
    public sealed class ShapeInfo
    {
        public string Label = "";      // D | P | b | KHÁC-B | KHÁC-thin | KHÁC-close
        public double Poc, Vah, Val, TLo, THi, Asym, Bulge, L, H, Close;
        public bool CloseIn, TwoPeaks;
    }

    /// <summary>Port zones_c_v6.classify_shape (hằng số đăng ký trước: asym 0,25 · bulge 0,20 · vùng dày = hàng kề ≥ 50% POC).</summary>
    public static class TpoShape
    {
        public const double Step = 0.1 * 2;                 // 0,2 giá / hàng
        public const double AsymThr = 0.25, BulgeThr = 0.20, BulgeFrac = 0.5;
        private const double Tick = 0.1;
        private const int Smooth = 5;
        private const double HvnMinRatio = 1.5, LvnMaxRatio = 0.5;

        public static ShapeInfo Classify(long[] rows, double[] cnt, double L, double H, double close)
        {
            int n = rows.Length;
            var prices = new double[n];
            for (int k = 0; k < n; k++) prices[k] = Math.Round(rows[k] * Step, 6);
            BenzoKernel.ValueArea(prices, cnt, out double poc, out double vah, out double val);
            PeakSharpness(rows, cnt, poc, BulgeFrac, out double tLo, out double tHi);
            double R = H - L;
            var hv = Peaks(prices, cnt, true);
            var lv = Peaks(prices, cnt, false);
            bool two = false;
            for (int a = 0; a < hv.Count; a++)
                for (int b = a + 1; b < hv.Count; b++)
                {
                    double lo_ = Math.Min(hv[a], hv[b]), hi_ = Math.Max(hv[a], hv[b]);
                    foreach (double p in lv) if (lo_ < p && p < hi_) two = true;
                }
            bool closeIn = val - 1e-9 <= close && close <= vah + 1e-9;
            double bulge = 0, asym = 0;
            if (R > 0) { bulge = (tHi - tLo) / R; asym = ((tLo - L) - (H - tHi)) / R; }
            string lab;
            if (two) lab = "KHÁC-B";
            else if (bulge < BulgeThr) lab = "KHÁC-thin";
            else if (!closeIn) lab = "KHÁC-close";
            else if (Math.Abs(asym) <= AsymThr) lab = "D";
            else if (asym > 0) lab = "P";
            else lab = "b";
            return new ShapeInfo { Label = lab, Poc = poc, Vah = vah, Val = val, TLo = tLo, THi = tHi, Asym = asym, Bulge = bulge, L = L, H = H, Close = close, CloseIn = closeIn, TwoPeaks = two };
        }

        /// <summary>Port zones_a_v4.peak_sharpness: từ hàng POC nới lên/xuống chừng nào hàng kề TỒN TẠI và ≥ frac × TPO của POC.</summary>
        public static void PeakSharpness(long[] rows, double[] cnt, double peakPrice, double frac, out double lo, out double hi)
        {
            var d = new Dictionary<long, double>();
            for (int k = 0; k < rows.Length; k++) d[rows[k]] = cnt[k];
            long pr = (long)Math.Round(peakPrice / Step, MidpointRounding.ToEven);
            if (!d.TryGetValue(pr, out double pv)) { lo = peakPrice; hi = peakPrice; return; }
            double thr = frac * pv;
            long a = pr, b = pr;
            while (d.TryGetValue(a - 1, out double x) && x >= thr) a--;
            while (d.TryGetValue(b + 1, out double y) && y >= thr) b++;
            lo = Math.Round(a * Step, 6); hi = Math.Round(b * Step, 6);
        }

        /// <summary>Port kernel.find_hvn (peak=true) / find_lvn (peak=false): giá các đỉnh/đáy cục bộ của phân bố làm mượt ±5 hàng, mạnh trước, gộp theo khoảng cách tối thiểu.</summary>
        private static List<double> Peaks(double[] prices, double[] w, bool peak)
        {
            var res = new List<double>();
            int n = w.Length;
            if (n < 3) return res;
            double sum = 0; for (int k = 0; k < n; k++) sum += w[k];
            double avg = sum / n;
            if (avg <= 0) return res;
            double minSep = Math.Min(120.0, Math.Max(20.0, (prices[n - 1] - prices[0]) / Tick * 0.08));
            var cs = new double[n + 1];
            for (int k = 0; k < n; k++) cs[k + 1] = cs[k] + w[k];
            var sm = new double[n];
            for (int k = 0; k < n; k++)
            {
                int a = Math.Max(0, k - Smooth), z = Math.Min(n - 1, k + Smooth);
                sm[k] = (cs[z + 1] - cs[a]) / (z - a + 1);
            }
            var pk = new List<int>();
            for (int k = 1; k < n - 1; k++)
            {
                bool ok = peak ? (sm[k] >= sm[k - 1] && sm[k] >= sm[k + 1] && sm[k] >= HvnMinRatio * avg)
                               : (sm[k] <= sm[k - 1] && sm[k] <= sm[k + 1] && sm[k] <= LvnMaxRatio * avg);
                if (ok) pk.Add(k);
            }
            pk.Sort((x, y) => { int c = peak ? sm[y].CompareTo(sm[x]) : sm[x].CompareTo(sm[y]); return c != 0 ? c : x.CompareTo(y); });
            var kept = new List<double>();
            foreach (int j in pk)
            {
                bool ok = true;
                foreach (double p in kept) if (!(Math.Abs(prices[j] - p) / Tick >= minSep)) { ok = false; break; }
                if (ok) kept.Add(prices[j]);
            }
            return kept;
        }
    }

    /// <summary>Gom nến M1 của một phiên thành profile TPO (bracket 30′ UTC, hàng 0,2 giá) — port zones_c_v6.tpo_profile.</summary>
    public sealed class TpoAcc
    {
        private const long T30 = 30L * TimeSpan.TicksPerMinute;
        private readonly SortedDictionary<long, (double hi, double lo)> _br = new();
        private double _hi = double.NegativeInfinity, _lo = double.PositiveInfinity, _close;
        private int _n;

        public void Reset() { _br.Clear(); _hi = double.NegativeInfinity; _lo = double.PositiveInfinity; _n = 0; }

        public void Add(BarData b)
        {
            long k = b.Time.Ticks / T30;
            if (_br.TryGetValue(k, out var v)) _br[k] = (Math.Max(v.hi, b.H), Math.Min(v.lo, b.L));
            else _br[k] = (b.H, b.L);
            _hi = Math.Max(_hi, b.H); _lo = Math.Min(_lo, b.L); _close = b.C; _n++;
        }

        public ShapeInfo Build()
        {
            if (_n == 0) return null;
            long r0 = long.MaxValue, r1 = long.MinValue;
            var span = new List<(long a, long b)>();
            foreach (var v in _br.Values)
            {
                long bl = (long)Math.Round(v.lo / TpoShape.Step, MidpointRounding.ToEven);
                long bh = (long)Math.Round(v.hi / TpoShape.Step, MidpointRounding.ToEven);
                span.Add((bl, bh)); r0 = Math.Min(r0, bl); r1 = Math.Max(r1, bh);
            }
            var cnt = new double[r1 - r0 + 1];
            foreach (var (a, b) in span) for (long r = a; r <= b; r++) cnt[r - r0] += 1;
            var rows = new List<long>(); var cc = new List<double>();
            for (int k = 0; k < cnt.Length; k++) if (cnt[k] > 0) { rows.Add(r0 + k); cc.Add(cnt[k]); }
            return TpoShape.Classify(rows.ToArray(), cc.ToArray(), _lo, _hi, _close);
        }
    }

    // ================================================================= VA nhỏ CHoCH
    /// <summary>Một VA nhỏ CHoCH. Giá lưu theo KHUNG của máy (chiều UP lưu giá âm); Real* trả giá thật.</summary>
    public sealed class ChochVa
    {
        public int Id, Dir;                 // Dir +1 = DN (climax bán ở đáy), −1 = UP (gương)
        public int Birth, End = int.MaxValue;
        public double Lo, Hi;               // trong khung máy
        public int NExt;
        public bool ModeKilled;
        public double RealLo => Dir > 0 ? Lo : -Hi;
        public double RealHi => Dir > 0 ? Hi : -Lo;
        public string Src => Dir > 0 ? "CHOCH_DN" : "CHOCH_UP";
    }

    /// <summary>Máy một chiều của VA nhỏ CHoCH (port zones_c_v6._one_dir). d=+1: climax bán ở đáy (giá thật); d=−1: gương (giá âm).</summary>
    internal sealed class ChochDir
    {
        // ---- hằng số đăng ký trước (zones_c_v6.py)
        const double MoveU = 6.0, MoveMinEff = 0.35, VsaClimax = 2.2, ClimaxRangeMult = 1.4, BlockFrac = 0.4, ArMin = 2.0, ArRetraceMult = 0.5,
                     UndercutU = 1.0, StaMinArFrac = 0.55, MinHeight = 6.0, ExtFrac = 0.25;
        const int MoveLookback = 240, ClimaxExtBars = 8, ArWaitBars = 300, StWaitBars = 400;

        enum S { Ngu, Cand, WaitAr, WaitSt }
        private sealed class Cd
        {
            public int Anchor, C; public double Low, Cmin, Mp; public int Blk;   // Blk: 1 true · 0 false · −1 chưa biết (None)
            public double L1, H1; public int TH1;
        }

        public readonly int D;
        private readonly BenzoZones _z;
        private readonly Func<int, double> _vma, _avgr;
        private S _st = S.Ngu;
        private Cd _cd;
        private bool _hasLastH; private int _lastHPos; private double _lastHPrice;
        private int _s0;
        public ChochVa Live;

        public ChochDir(BenzoZones z, int d, Func<int, double> vma, Func<int, double> avgr)
        { _z = z; D = d; _vma = vma; _avgr = avgr; }

        private double Xl(int k) => D > 0 ? _z.Bars[k].L : -_z.Bars[k].H;
        private double Xh(int k) => D > 0 ? _z.Bars[k].H : -_z.Bars[k].L;
        private double Xc(int k) => D > 0 ? _z.Bars[k].C : -_z.Bars[k].C;
        private double Rng(int k) => _z.Bars[k].H - _z.Bars[k].L;

        private void KillLive(int i) { if (Live != null) { Live.End = i; Live = null; } }

        private bool ClimaxOk(int c, out double mp)
        {
            mp = 0;
            double vm = _vma(c), ar = _avgr(c);
            bool cond = (!double.IsNaN(vm) && _z.Bars[c].Vol >= VsaClimax * vm) || (!double.IsNaN(ar) && Rng(c) >= ClimaxRangeMult * ar);
            if (!cond) return false;
            int ch; double top;
            if (_hasLastH && _lastHPos < c) { ch = _lastHPos; top = _lastHPrice; }
            else
            {
                int a = Math.Max(_s0, c - MoveLookback);
                if (c - a < 1) return false;
                ch = a; double best = Xh(a);
                for (int k = a + 1; k < c; k++) if (Xh(k) > best) { best = Xh(k); ch = k; }     // argmax: nến đầu tiên khi hoà
                top = best;
            }
            double mn = double.PositiveInfinity;
            for (int k = ch; k < c; k++) mn = Math.Min(mn, Xl(k));
            if (Xl(c) > mn + 1e-12) return false;
            double length = top - Xl(c);
            double uc = _z.U;
            if (double.IsNaN(uc) || length < MoveU * uc) return false;
            double path = 0;
            for (int k = ch + 1; k <= c; k++) path += Math.Abs(Xc(k) - Xc(k - 1));
            double eff = path > 1e-9 ? length / path : 0.0;
            if (eff < MoveMinEff) return false;
            double runMin = double.PositiveInfinity; mp = 0;
            for (int k = ch; k < c; k++) { runMin = Math.Min(runMin, Xl(k)); mp = Math.Max(mp, Xh(k) - runMin); }
            return true;
        }

        private bool BlockedNow(int c) => Xc(c) >= Xl(c) + BlockFrac * Rng(c) - 1e-12;

        /// <summary>Một bước tại nến i. pv: pivot zigzag được xác nhận ĐÚNG ở nến i (đã đổi sang khung máy), hoặc null.</summary>
        public void Step(int i, bool newSession, bool hasPv, int pvPos, double pvPrice, bool pvIsH, Func<ChochVa> mk)
        {
            if (newSession) { KillLive(i); _st = S.Ngu; _cd = null; _hasLastH = false; _s0 = i; }
            if (hasPv && pvIsH) { _hasLastH = true; _lastHPos = pvPos; _lastHPrice = pvPrice; }
            double ui = _z.U;
            // ---- VA đang sống: nới / chết theo pivot
            if (Live != null && hasPv)
            {
                double h = Live.Hi - Live.Lo;
                if (!pvIsH && pvPrice < Live.Lo - 1e-9)
                {
                    double dd = Live.Lo - pvPrice;
                    if (dd > ExtFrac * h + 1e-9) KillLive(i);
                    else { Live.Lo = pvPrice; Live.NExt++; }
                }
                else if (pvIsH && pvPrice > Live.Hi + 1e-9)
                {
                    double dd = pvPrice - Live.Hi;
                    if (dd > ExtFrac * h + 1e-9) KillLive(i);
                    else { Live.Hi = pvPrice; Live.NExt++; }
                }
            }
            for (int attempt = 0; attempt < 2; attempt++)
            {
                bool fresh = false;
                if (_st == S.Ngu)
                {
                    if (!ClimaxOk(i, out double mp)) break;
                    _cd = new Cd { Anchor = i, C = i, Low = Xl(i), Cmin = Xl(i), Mp = mp, Blk = BlockedNow(i) ? 1 : -1 };
                    _st = S.Cand; fresh = true;
                }
                bool fail = false;
                if (_st == S.Cand)
                {
                    if (i <= _cd.Anchor + ClimaxExtBars)
                    {
                        if (Xl(i) < _cd.Low - 1e-12 && ClimaxOk(i, out double mp2))
                        { _cd.C = i; _cd.Low = Xl(i); _cd.Mp = mp2; _cd.Blk = BlockedNow(i) ? 1 : -1; }
                        _cd.Cmin = Math.Min(_cd.Cmin, Xl(i));
                    }
                    else if (Xl(i) < _cd.Cmin - 1e-12) fail = true;
                    if (!fail && _cd.Blk == -1 && i == _cd.C + 1)
                    {
                        _cd.Blk = Xc(i) > (Xh(_cd.C) + Xl(_cd.C)) / 2.0 + 1e-12 ? 1 : 0;
                        if (_cd.Blk == 0) fail = true;
                    }
                    if (!fail && hasPv && !pvIsH)
                    {
                        if (pvPos <= _cd.Anchor + ClimaxExtBars && _cd.Blk != 0) { _cd.L1 = Math.Min(pvPrice, _cd.Cmin); _st = S.WaitAr; }
                        else fail = true;
                    }
                }
                else if (_st == S.WaitAr)
                {
                    if (_cd.Blk == -1 && i == _cd.C + 1)
                    {
                        _cd.Blk = Xc(i) > (Xh(_cd.C) + Xl(_cd.C)) / 2.0 + 1e-12 ? 1 : 0;
                        if (_cd.Blk == 0) fail = true;
                    }
                    if (!fail && ((!double.IsNaN(ui) && Xl(i) < _cd.L1 - UndercutU * ui - 1e-12) || i - _cd.C > ArWaitBars)) fail = true;
                    if (!fail && hasPv && pvIsH)
                    {
                        if (pvPrice - _cd.L1 >= Math.Max(ArMin, ArRetraceMult * _cd.Mp) - 1e-9) { _cd.H1 = pvPrice; _cd.TH1 = i; _st = S.WaitSt; }
                    }
                }
                else if (_st == S.WaitSt)
                {
                    if (!double.IsNaN(ui) && Xl(i) < _cd.L1 - UndercutU * ui - 1e-12) fail = true;
                    else if (i - _cd.TH1 > StWaitBars) fail = true;
                    else if (hasPv && pvIsH && pvPrice > _cd.H1 + 1e-9) { _cd.H1 = pvPrice; _cd.TH1 = i; }
                    else if (hasPv && !pvIsH)
                    {
                        double span = _cd.H1 - _cd.L1;
                        if (pvPrice <= _cd.H1 - StaMinArFrac * span + 1e-9)
                        {
                            double lo = Math.Min(_cd.L1, pvPrice), hi = _cd.H1;
                            if (hi - lo >= MinHeight - 1e-9)
                            {
                                KillLive(i);
                                var va = mk();
                                va.Dir = D; va.Birth = i; va.Lo = lo; va.Hi = hi;
                                Live = va;
                            }
                            _st = S.Ngu; _cd = null;
                        }
                    }
                }
                if (fail)
                {
                    _st = S.Ngu; _cd = null;
                    if (attempt == 0 && !fresh) continue;
                }
                break;
            }
        }
    }

    /// <summary>Khung VA nhỏ CHoCH theo nến: máy giá hai chiều + luật chết khi chế độ M5 trên band VA đó là TREND (port choch_va + mode_kills).</summary>
    public sealed class ChochFrame
    {
        private readonly BenzoZones _z;
        private readonly ChochDir _dn, _up;
        private int _nid, _pivSeen;
        public readonly ModeTracker Trk = new ModeTracker((ZoneSnap zz, out double hi, out double lo, out string src) => { hi = lo = double.NaN; src = ""; return false; });
        private int _modeId = -1;
        // mảng theo nến: band VA đang hiện (giá thật), mã, nguồn
        public readonly List<double> Lo = new(), Hi = new();
        public readonly List<int> Id = new();
        public readonly List<string> Src = new();

        public ModeState Mode => Trk.Cur;
        public int Born => _nid;

        public ChochFrame(BenzoZones z)
        {
            _z = z;
            _dn = new ChochDir(z, +1, Vma, Avgr);
            _up = new ChochDir(z, -1, Vma, Avgr);
        }

        // SMA volume 20 nến GỒM nến i (đủ 20 nến mới có giá trị); TB biên độ 20 nến TRƯỚC nến i
        private double Vma(int c)
        {
            if (c < 19) return double.NaN;
            double s = 0; for (int k = c - 19; k <= c; k++) s += _z.Bars[k].Vol;
            return s / 20.0;
        }
        private double Avgr(int c)
        {
            if (c < 20) return double.NaN;
            double s = 0; for (int k = c - 20; k < c; k++) s += _z.Bars[k].H - _z.Bars[k].L;
            return s / 20.0;
        }

        public void OnNewSession() { Trk.Reset(); _modeId = -1; }

        /// <summary>M5 vừa "hiện" (đã đóng trước giờ mở nến hiện tại): đưa band VA tại nến cuối M5 vào máy chế độ.</summary>
        public void FeedM5(M5Bar m)
        {
            int k = m.LastIdx;
            bool has = k < Id.Count && Id[k] >= 0;
            Trk.OnM5Raw(m.C, has, has ? Hi[k] : double.NaN, has ? Lo[k] : double.NaN, has ? "va_eu" : "");
            _modeId = has ? Id[k] : -1;
        }

        public void Step(int i)
        {
            bool ns = _z.NewSession;
            // pivot zigzag được xác nhận ĐÚNG ở nến i (tối đa 1)
            bool has = false; Pivot pv = null;
            while (_pivSeen < _z.Pivots.Count)
            {
                var p = _z.Pivots[_pivSeen++];
                if (p.ConfirmPos == i) { has = true; pv = p; }
            }
            Func<ChochVa> mk = () => new ChochVa { Id = _nid++ };
            _dn.Step(i, ns, has, has ? pv.Pos : 0, has ? pv.Price : 0, has && pv.IsHigh, mk);
            _up.Step(i, ns, has, has ? pv.Pos : 0, has ? -pv.Price : 0, has && !pv.IsHigh, mk);   // gương: giá âm, H↔L
            // ứng viên được vẽ: VA còn sống chưa bị chế độ giết; mới sinh sau thắng, hoà thì UP (id lớn hơn) thắng
            ChochVa top = Pick();
            // luật chết (mode_kills): chế độ M5 hiện hành là TREND trên band của ĐÚNG VA đang được vẽ ⇒ VA chết từ nến này
            if (top != null && _modeId == top.Id && Trk.Cur.Mode.StartsWith("TREND", StringComparison.Ordinal))
            {
                top.ModeKilled = true;
                top = Pick();
            }
            if (top == null) { Lo.Add(double.NaN); Hi.Add(double.NaN); Id.Add(-1); Src.Add(""); }
            else { Lo.Add(top.RealLo); Hi.Add(top.RealHi); Id.Add(top.Id); Src.Add(top.Src); }
        }

        private ChochVa Pick()
        {
            ChochVa best = null;
            foreach (var v in new[] { _dn.Live, _up.Live })
            {
                if (v == null || v.ModeKilled) continue;
                if (best == null || v.Birth > best.Birth || (v.Birth == best.Birth && v.Dir < best.Dir)) best = v;   // UP (Dir −1) thắng khi hoà ngày sinh
            }
            return best;
        }
    }

    // ================================================================= hành lang S/R (VCL)
    /// <summary>Máy hành lang S/R (port zones_c_v7.sr_corridors, face='near', rộng ≥ 6). Bước của nến j chạy khi nến j+1 đến (cần biết j có phải nến cuối M5 hay không).</summary>
    public sealed class SrFrame
    {
        const double MinW = 6.0;
        private sealed class Cor { public double Lo, Hi; public int EidS, EidR; }
        private readonly BenzoZones _z;
        public readonly ModeTracker Trk = new ModeTracker((ZoneSnap zz, out double hi, out double lo, out string src) => { hi = lo = double.NaN; src = ""; return false; });
        private Cor _cur;
        private double[] _pLo = Array.Empty<double>(), _pHi = Array.Empty<double>();
        private int[] _pId = Array.Empty<int>();
        private bool _pFirst;
        public int Born, DiedTrend, DiedGone;
        public VclCore OwnCore;

        public ModeState Mode => Trk.Cur;
        /// <summary>Hành lang đang sống (sau bước gần nhất); NaN nếu không có.</summary>
        public double CurLo => _cur?.Lo ?? double.NaN;
        public double CurHi => _cur?.Hi ?? double.NaN;
        public SrFrame(BenzoZones z) { _z = z; }

        /// <summary>Chạy bước của nến j = idx−1 (display lưu ở lần EndBar trước). Gọi ở ĐẦU Push(idx), trước khi đặt lại máy chế độ của phiên mới.</summary>
        public void StepPrev(int idx, bool newSessionNow, DateTime timeNow)
        {
            if (idx < 1) return;
            int j = idx - 1;
            var bj = _z.Bars[j];
            const long T5 = 5L * TimeSpan.TicksPerMinute;
            bool isLast = newSessionNow || (timeNow.Ticks / T5 != bj.Time.Ticks / T5);
            if (_pFirst) _cur = null;                                    // sang phiên: hành lang chết
            if (isLast)                                                  // nến M5 đóng ở j (band đang vẽ = _cur tại j)
            {
                bool has = _cur != null;
                Trk.OnM5Raw(bj.C, has, has ? _cur.Hi : double.NaN, has ? _cur.Lo : double.NaN, has ? "va_eu" : "");
                if (has && Trk.Cur.Mode.StartsWith("TREND", StringComparison.Ordinal)) { _cur = null; DiedTrend++; }
            }
            int n = _pId.Length;
            if (_cur != null)                                            // mất vùng
            {
                bool s = false, r = false;
                for (int k = 0; k < n; k++) { if (_pId[k] == _cur.EidS) s = true; if (_pId[k] == _cur.EidR) r = true; }
                if (!s || !r) { _cur = null; DiedGone++; }
            }
            if (_cur == null && n > 0)                                   // thử sinh
            {
                double c = bj.C;
                bool inside = false;
                for (int k = 0; k < n; k++) if (_pLo[k] <= c && c <= _pHi[k]) { inside = true; break; }
                if (!inside)
                {
                    int a = -1, b = -1;                                  // R = vùng có lo > c nhỏ nhất · S = vùng có hi < c lớn nhất (hoà ⇒ eid nhỏ)
                    for (int k = 0; k < n; k++)
                    {
                        if (_pLo[k] > c && (a < 0 || _pLo[k] < _pLo[a] || (_pLo[k] == _pLo[a] && _pId[k] < _pId[a]))) a = k;
                        if (_pHi[k] < c && (b < 0 || _pHi[k] > _pHi[b] || (_pHi[k] == _pHi[b] && _pId[k] < _pId[b]))) b = k;
                    }
                    if (a >= 0 && b >= 0)
                    {
                        double lof = _pHi[b], hif = _pLo[a];
                        if (hif - lof >= MinW - 1e-9) { _cur = new Cor { Lo = lof, Hi = hif, EidS = _pId[b], EidR = _pId[a] }; Born++; }
                    }
                }
            }
        }

        /// <summary>Lưu bộ vùng hiển thị của nến vừa đẩy (dùng ở bước kế tiếp).</summary>
        public void Store(IReadOnlyList<VZone> disp, bool newSession)
        {
            int n = disp.Count;
            if (_pLo.Length != n) { _pLo = new double[n]; _pHi = new double[n]; _pId = new int[n]; }
            for (int k = 0; k < n; k++) { _pLo[k] = disp[k].Lo; _pHi[k] = disp[k].Hi; _pId[k] = disp[k].Id; }
            _pFirst = newSession;
        }

        public void OnNewSession() { Trk.Reset(); }
    }

    // ================================================================= hub
    /// <summary>Tất cả lớp vùng mới của C, gắn vào BenzoZones. Mọi hàm là no-op khi lớp tương ứng không bật.</summary>
    public sealed class BenzoLayers
    {
        private readonly BenzoZones _z;
        public CLayerOptions Opt = CLayerOptions.Legacy;
        public bool Active;

        // ---- hình dạng profile TPO hôm qua + vùng dày
        public bool UseShape, UseChoch, UseSr;
        private readonly TpoAcc _acc = new();
        public ShapeInfo Shape;
        public int ShKind => Shape == null ? 0 : Shape.Label == "D" ? 1 : Shape.Label == "P" ? 2 : Shape.Label == "b" ? 3 : 0;
        public double TLo => Shape == null ? double.NaN : Shape.TLo;
        public double THi => Shape == null ? double.NaN : Shape.THi;
        public ModeTracker TrkL;                         // band lớp D / P-b (A/EU theo hình dạng; US như C0)

        // ---- VA nhỏ CHoCH + hành lang S/R
        public ChochFrame Choch;
        public SrFrame Sr;
        /// <summary>Nguồn bộ vùng VCL: BenzoSr.Core khi có (dùng chung với setup B), nếu không thì lõi riêng.</summary>
        public Func<VclCore> SharedCore;
        /// <summary>Chỉ để test: thay bộ vùng hiển thị VCL bằng bộ tổng hợp.</summary>
        public Func<int, IReadOnlyList<VZone>> DisplayOverride;

        public BenzoLayers(BenzoZones z) { _z = z; }

        public void Configure(CLayerOptions o, bool enabled)
        {
            Opt = o ?? CLayerOptions.Legacy;
            Active = enabled && Opt.AnyNew;
            UseShape = Active && Opt.NeedShape;
            UseChoch = Active && Opt.Choch;
            UseSr = Active && Opt.Sr;
            if (UseShape) TrkL = new ModeTracker(SelL);
            if (UseChoch) Choch = new ChochFrame(_z);
            if (UseSr) Sr = new SrFrame(_z);
        }

        // ---- band lớp D / P-b: A/EU = theo hình dạng; US = như C0 (VA Âu, chưa có thì IB)
        private bool SelL(ZoneSnap z, out double hi, out double lo, out string src)
        {
            if (z.Sm < BenzoKernel.SmUsStart)
            {
                double eh = double.NaN, el = double.NaN;
                switch (z.ShKind)
                {
                    case 1: eh = z.YdVah; el = z.YdVal; break;                                  // D: VA hôm qua
                    case 2: case 3:
                        if (Opt.ThickPb) { eh = z.THi; el = z.TLo; }                             // P/b: vùng dày T
                        else if (!Opt.GateD) { eh = z.YdVah; el = z.YdVal; }                     // chưa gate ⇒ như C0
                        break;
                    default: if (!Opt.GateD) { eh = z.YdVah; el = z.YdVal; } break;             // khác/không có: gate ⇒ không band
                }
                if (!double.IsNaN(eh)) { hi = eh; lo = el; src = "va_eu"; return true; }
                if (!double.IsNaN(z.IbHi)) { hi = z.IbHi; lo = z.IbLo; src = "ib"; return true; }
                hi = lo = double.NaN; src = ""; return false;
            }
            return BenzoZones.SelC(z, out hi, out lo, out src);
        }

        /// <summary>Tên cạnh và POC (cho TP) của lớp D / P-b tại nến hiện tại (A/EU); ngoài A/EU trả null/POC của C0.</summary>
        public void LabelsL(out string hiName, out string loName, out string srcLabel)
        {
            hiName = loName = ""; srcLabel = "";
            if (_z.Sm >= BenzoKernel.SmUsStart) return;
            if (ShKind == 1 && Opt.GateD) { hiName = "VAH_Y_D"; loName = "VAL_Y_D"; srcLabel = "VA hôm qua (ngày hình D)"; }
            else if ((ShKind == 2 || ShKind == 3) && Opt.ThickPb)
            {
                string sfx = ShKind == 2 ? "P" : "B";
                hiName = "T_HI_" + sfx; loName = "T_LO_" + sfx;
                srcLabel = "vùng dày TPO hôm qua (ngày hình " + (ShKind == 2 ? "P" : "b") + ")";
            }
        }

        /// <summary>POC dùng làm mục tiêu TP của lớp D / P-b tại nến hiện tại (NaN nếu không có).</summary>
        public double PocL()
        {
            if (_z.Sm >= BenzoKernel.SmUsStart) return _z.EuPoc;
            if ((ShKind == 2 || ShKind == 3) && Opt.ThickPb) return Shape.Poc;           // POC của profile TPO
            return _z.YdPoc;
        }

        // ---- hook từ BenzoZones.Push ----
        public void BeginBar(int idx, BarData bar, bool newSession)
        {
            if (!Active) return;
            Fed.Clear();
            if (UseSr) Sr.StepPrev(idx, newSession, bar.Time);
            if (newSession)
            {
                TrkL?.Reset();
                Choch?.OnNewSession();
                Sr?.OnNewSession();
            }
        }

        public readonly List<M5Bar> Fed = new();

        public void FeedM5(M5Bar m)
        {
            if (!Active) return;
            Fed.Add(m);
            TrkL?.OnM5(m);
            Choch?.FeedM5(m);
        }

        public void OnSessionStart(bool becameYd)
        {
            if (!UseShape) return;
            if (becameYd) Shape = _acc.Build();
            _acc.Reset();
        }

        public void AddBar(BarData bar) { if (UseShape) _acc.Add(bar); }

        public void EndBar(int idx, BarData bar, IReadOnlyList<LevelVol> levels)
        {
            if (!Active) return;
            if (UseChoch) Choch.Step(idx);
            if (UseSr)
            {
                var core = DisplayOverride == null ? SharedCore?.Invoke() : null;
                if (DisplayOverride != null) Sr.Store(DisplayOverride(idx), _z.NewSession);
                else if (core == null)
                {
                    Sr.OwnCore ??= new VclCore { TzOffset = _z.TzOffset, UsShift = _z.UsShift };
                    List<VLevel> lv = null;
                    if (levels != null && levels.Count > 0) { lv = new List<VLevel>(levels.Count); foreach (var l in levels) lv.Add(new VLevel(l.Price, l.Vol)); }
                    Sr.OwnCore.Push(new VBar { Time = bar.Time, O = bar.O, H = bar.H, L = bar.L, C = bar.C, Vol = bar.Vol }, (IReadOnlyList<VLevel>)lv ?? Array.Empty<VLevel>());
                    core = Sr.OwnCore;
                }
                if (DisplayOverride == null) Sr.Store(core.Display, _z.NewSession);
            }
        }
    }
}
