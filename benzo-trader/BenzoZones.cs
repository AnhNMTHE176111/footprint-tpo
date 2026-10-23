// ============================================================================
//  BenzoZones — port C# của kernel.py (vùng, VWAP, chế độ M5, helper) + BenzoRisk
// ============================================================================
//  Chạy THEO DÒNG: engine gọi Push(idx, bar, levels) đúng một lần cho mỗi nến ĐÃ ĐÓNG, theo thứ tự.
//  Mọi giá trị "hiện tại" (VwapD, Yd*, Eu*, Ib*, ModeDef, ...) chỉ dùng dữ liệu của các nến <= idx
//  (cấm nhìn trước). Giờ trong ngày tính theo giờ VN (TzOffset) và "bù giờ Mỹ" như kernel:
//  khi Mỹ dùng giờ mùa đông (EST) mọi mốc neo Mỹ (05:00, 19:00, IB) lùi +1h theo giờ VN.
//  Không phụ thuộc ProfileEngine / Quantower SDK (để unit test + ReplayCsv dùng chung).
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Linq;

    /// <summary>Đỉnh/đáy zigzag (ngưỡng 2 giá, không nhìn trước): chỉ được dùng từ nến ConfirmPos trở đi.</summary>
    public sealed class Pivot
    {
        public int Pos;
        public double Price;
        public bool IsHigh;
        public int ConfirmPos;
    }

    /// <summary>Ảnh chụp các vùng tại một nến (để gắn vào nến M5 vừa đóng).</summary>
    public struct ZoneSnap
    {
        public double EuVah, EuVal, IbHi, IbLo, YdVah, YdVal;
        public int ShKind;                  // hình dạng profile TPO hôm qua: 0 khác/không có · 1 D · 2 P · 3 b (lớp C-v6, BenzoLayers)
        public double TLo, THi;             // vùng dày T của profile TPO hôm qua
        public int Sm;
        public string Phase;
    }

    /// <summary>Nến M5 ghép từ M1 theo mốc phút chia hết cho 5 (UTC), không gộp xuyên phiên.</summary>
    public sealed class M5Bar
    {
        public int SessionNo;
        public DateTime T5Start, T5End;
        public double O, H, L, C, Delta;
        public int FirstIdx, LastIdx;
        public ZoneSnap Snap;
    }

    /// <summary>Chế độ M5 tại một thời điểm (xem kernel.mode_frame).</summary>
    public sealed class ModeState
    {
        public string Mode = "NA";          // BALANCE | BREAK_UP | BREAK_DN | TREND_UP | TREND_DN | NA
        public double BandHi = double.NaN, BandLo = double.NaN;
        public string BandSrc = "";         // "va_eu" | "ib" | ""
        public int BreakSide;               // +1/-1/0 (phía nến M5 ngoài gần nhất, 0 nếu vừa đóng lại trong)
        public int Run;                     // số nến M5 liên tiếp đóng ngoài
        public bool HadBreak;
    }

    /// <summary>Máy trạng thái chế độ M5. Mỗi biến thể chọn band khác nhau (BandSel).</summary>
    public sealed class ModeTracker
    {
        public delegate bool BandSel(ZoneSnap z, out double hi, out double lo, out string src);
        private readonly BandSel _sel;
        private int _run, _prevSide;
        private bool _had;
        public ModeState Cur = new ModeState();
        public ModeTracker(BandSel sel) { _sel = sel; }

        public void Reset() { _run = 0; _prevSide = 0; _had = false; Cur = new ModeState(); }

        public void OnM5(M5Bar m)
        {
            bool has = _sel(m.Snap, out double bh, out double bl, out string src);
            OnM5Raw(m.C, has, bh, bl, src);
        }

        /// <summary>Như OnM5 nhưng band do người gọi đưa vào (các lớp C-v6/v7: band của lớp tại nến M5 vừa đóng).</summary>
        public void OnM5Raw(double close, bool has, double bh, double bl, string src)
        {
            var s = new ModeState();
            if (!has)
            {
                s.Mode = "NA"; _run = 0; _prevSide = 0;
                s.BandHi = double.NaN; s.BandLo = double.NaN; s.BandSrc = "";
            }
            else
            {
                s.BandHi = bh; s.BandLo = bl; s.BandSrc = src;
                int outv = close > bh ? 1 : (close < bl ? -1 : 0);
                double dist = outv > 0 ? close - bh : (outv < 0 ? bl - close : 0.0);
                if (outv == 0) { s.Mode = "BALANCE"; _run = 0; _prevSide = 0; }
                else
                {
                    _run = outv == _prevSide ? _run + 1 : 1;
                    _prevSide = outv; _had = true;
                    string sfx = outv > 0 ? "UP" : "DN";
                    s.Mode = ((_run >= BenzoKernel.TrendRuns && dist >= BenzoKernel.TrendDist) ? "TREND_" : "BREAK_") + sfx;
                }
            }
            s.Run = _run; s.HadBreak = _had; s.BreakSide = _prevSide;
            Cur = s;
        }
    }

    public static class BenzoKernel
    {
        public const double Tick = 0.1;
        public const double RowStep = 0.1 * 2;       // 1 hàng profile = 2 tick
        public const double GapMinutes = 30;          // khoảng trống > 30 phút ⇒ phiên mới
        public const double WeekGapMinutes = 30 * 60; // > 30 giờ ⇒ tuần CME mới
        public const double VaFrac = 0.70;
        public const int MinBarsProf = 300;           // phiên < 300 nến không làm "phiên hôm qua"
        public const int MinEuBars = 60, MinIbBars = 30;
        public const int SmEuStart = 450, SmUsStart = 840, SmOffStart = 1380, SmIbStart = 860, SmIbEnd = 920;
        public const int TrendRuns = 2;
        public const double TrendDist = 3.0;
        public const int MedianN = 50;
        public const double CfBodyFrac = 0.5;
        public const double ZzThreshold = 2.0;

        /// <summary>Mỹ đang dùng giờ mùa hè (EDT): CN thứ 2 tháng 3 07:00 UTC → CN đầu tháng 11 06:00 UTC.</summary>
        public static bool UsDst(DateTime utc)
        {
            int y = utc.Year;
            var m8 = new DateTime(y, 3, 8, 0, 0, 0, DateTimeKind.Utc);
            int d = 8 + (7 - (int)m8.DayOfWeek) % 7;
            var n1 = new DateTime(y, 11, 1, 0, 0, 0, DateTimeKind.Utc);
            int e = 1 + (7 - (int)n1.DayOfWeek) % 7;
            var s = new DateTime(y, 3, d, 7, 0, 0, DateTimeKind.Utc);
            var z = new DateTime(y, 11, e, 6, 0, 0, DateTimeKind.Utc);
            return utc >= s && utc < z;
        }

        public static int Mod(int a, int m) => ((a % m) + m) % m;

        /// <summary>Phút kể từ 05:00 VN (đã bù giờ Mỹ).</summary>
        public static int SmOf(DateTime utc, int tzOffset, bool usShift = true)
        {
            int vm = Mod(utc.Hour * 60 + utc.Minute + tzOffset * 60, 1440);
            int adj = (usShift && !UsDst(utc)) ? Mod(vm - 60, 1440) : vm;
            return Mod(adj - 300, 1440);
        }

        public static string PhaseOf(int sm) => sm < SmEuStart ? "A" : sm < SmUsStart ? "EU" : sm < SmOffStart ? "US" : "OFF";

        /// <summary>Port kernel.value_area: bắt đầu từ POC, mỗi bước mở 2 hàng mỗi bên, chọn bên lớn hơn (hòa ⇒ trên), dừng khi ≥ 70%.</summary>
        public static bool ValueArea(IReadOnlyList<double> prices, IReadOnlyList<double> w, out double poc, out double vah, out double val)
        {
            poc = vah = val = double.NaN;
            int n = w.Count;
            if (n == 0) return false;
            double tot = 0; for (int k = 0; k < n; k++) tot += w[k];
            if (tot <= 0) return false;
            int p = 0;
            for (int k = 1; k < n; k++) if (w[k] > w[p]) p = k;     // hòa ⇒ chỉ số thấp nhất
            double acc = w[p], target = tot * VaFrac;
            int lo = p, hi = p;
            while (acc < target && (lo > 0 || hi < n - 1))
            {
                double up = (hi < n - 1 ? w[hi + 1] : 0) + (hi < n - 2 ? w[hi + 2] : 0);
                double dn = (lo > 0 ? w[lo - 1] : 0) + (lo > 1 ? w[lo - 2] : 0);
                if (hi >= n - 1) { acc += dn; lo = Math.Max(0, lo - 2); }
                else if (lo <= 0) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else if (up >= dn) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else { acc += dn; lo = Math.Max(0, lo - 2); }
            }
            poc = prices[p]; vah = prices[hi]; val = prices[lo];
            return true;
        }

        /// <summary>Giá của hàng profile (làm tròn 6 chữ số như kernel).</summary>
        public static double RowPrice(long row) => Math.Round(row * RowStep, 6);

        /// <summary>VA từ dictionary hàng→volume (sắp theo hàng).</summary>
        public static bool ValueAreaOf(Dictionary<long, double> prof, out double poc, out double vah, out double val)
        {
            var keys = prof.Keys.ToList(); keys.Sort();
            var pr = new double[keys.Count]; var w = new double[keys.Count];
            for (int k = 0; k < keys.Count; k++) { pr[k] = RowPrice(keys[k]); w[k] = prof[keys[k]]; }
            return ValueArea(pr, w, out poc, out vah, out val);
        }

        /// <summary>Trung vị (cửa sổ n nến gần nhất, tính cả nến hiện tại; cần tối thiểu 10).</summary>
        public static double RollingMedian(List<double> src, int n = MedianN, int minPeriods = 10)
        {
            int cnt = Math.Min(n, src.Count);
            if (cnt < minPeriods) return double.NaN;
            var a = new double[cnt];
            for (int k = 0; k < cnt; k++) a[k] = src[src.Count - cnt + k];
            Array.Sort(a);
            return cnt % 2 == 1 ? a[cnt / 2] : 0.5 * (a[cnt / 2 - 1] + a[cnt / 2]);
        }

        /// <summary>Nến xác nhận CF theo chiều side: đóng theo chiều, thân ≥ 50% biên độ, Δ cùng dấu, |Δ| ≥ trung vị |Δ| 50 nến.</summary>
        public static bool IsConfirmBar(BarData b, int side, double medAbsDelta)
        {
            double rng = b.H - b.L;
            if (rng <= 0 || double.IsNaN(medAbsDelta)) return false;
            double body = (b.C - b.O) * side;
            return body > 0 && body >= CfBodyFrac * rng && b.Delta * side > 0 && Math.Abs(b.Delta) >= medAbsDelta;
        }
    }

    // ---------------------------------------------------------------- BenzoRisk
    public sealed class RiskResult
    {
        public double Entry, Sl, Tp, Risk;
        public bool FloorApplied;
    }

    public static class BenzoRisk
    {
        public const double SlBuffer = 0.3;
        public const int SlFloorBars = 5;
        public const double SlCap = 4.0;

        /// <summary>
        /// SL lai: SL = struct ∓ 0,3 giá; SÀN: khoảng SL ≥ biên độ nến cao nhất 5 nến gần nhất (gồm idx); TRẦN: &gt; 4 giá ⇒ null (bỏ lệnh).
        /// Vào ở giá đóng nến idx. TP = entry ± rr × khoảng SL. SL làm tròn ra xa theo tick.
        /// </summary>
        public static RiskResult Calc(IReadOnlyList<BarData> bars, int idx, int side, double structPrice, double rr, double tick = BenzoKernel.Tick)
        {
            if (tick <= 0) tick = BenzoKernel.Tick;
            double ent = bars[idx].C;
            double raw = structPrice - side * SlBuffer;
            double d = (ent - raw) * side;
            double floor = 0;
            for (int k = Math.Max(0, idx - SlFloorBars + 1); k <= idx; k++) floor = Math.Max(floor, bars[k].H - bars[k].L);
            bool fl = false;
            if (d < floor) { d = floor; fl = true; }
            if (d <= 0) return null;
            double sl = ent - side * d;
            sl = (side > 0 ? Math.Floor(sl / tick + 1e-9) : Math.Ceiling(sl / tick - 1e-9)) * tick;
            sl = Math.Round(sl, 6);
            d = (ent - sl) * side;
            if (d > SlCap + 1e-9 || d <= 0) return null;
            return new RiskResult { Entry = ent, Sl = sl, Tp = Math.Round(ent + side * rr * d, 6), Risk = d, FloorApplied = fl };
        }
    }

    // ---------------------------------------------------------------- BenzoZones
    public sealed class BenzoZones
    {
        public int TzOffset = 7;
        public bool UsShift = true;

        // ---- lịch sử theo nến (chỉ số = idx của engine) ----
        public readonly List<BarData> Bars = new();
        private readonly List<int> _sess = new(), _posS = new(), _posW = new(), _sm = new();
        private readonly List<double> _vD = new(), _vW = new(), _mad = new(), _bigSince = new();
        private readonly List<string> _phase = new(), _mode = new();
        private readonly List<bool> _moveClear = new();
        private readonly List<int> _bias = new();
        private readonly List<double> _absDelta = new(), _rangeList = new();

        public int SessionAt(int i) => _sess[i];
        public int PosInSessionAt(int i) => _posS[i];
        public int PosInWeekAt(int i) => _posW[i];
        public int SmAt(int i) => _sm[i];
        public string PhaseAt(int i) => _phase[i];
        public double VwapDAt(int i) => _vD[i];
        public double VwapWAt(int i) => _vW[i];
        public double MadAt(int i) => _mad[i];
        public int BarsSinceBigAt(int i) => (int)_bigSince[i];
        public string ModeAt(int i) => _mode[i];
        public bool MoveClearAt(int i) => _moveClear[i];
        public int BiasAt(int i) => _bias[i];

        // ---- trạng thái nến hiện tại ----
        public int Idx = -1;
        public bool NewSession;
        public int SessionNo = -1, SessionStartIdx, WeekStartIdx;
        public int Sm;
        public string Phase = "OFF";
        public double VwapD = double.NaN, VwapW = double.NaN;
        public bool HasYd; public double YdPoc = double.NaN, YdVah = double.NaN, YdVal = double.NaN;
        public double EuPoc = double.NaN, EuVah = double.NaN, EuVal = double.NaN;
        public double IbHi = double.NaN, IbLo = double.NaN;
        public double U = double.NaN, Mad = double.NaN;
        public int BarsSinceBig;
        public double PrevBigRange = double.NegativeInfinity;   // biên độ lớn nhất của các nến TRƯỚC nến hiện tại trong phiên
        public bool MoveClear;
        public int Bias;
        public readonly List<M5Bar> NewM5 = new();               // nến M5 vừa đóng ở lần Push này (cho setup A)
        public readonly List<Pivot> Pivots = new();
        public ModeState ModeDef => _trkDef.Cur;                 // band = VA Âu, chưa có thì IB (B, D)
        public ModeState ModeC => _trkC.Cur;                     // band = VA hôm qua trước 19:00, sau đó VA Âu / IB (C)

        /// <summary>Vùng thêm cho setup B (HVN/POC/VA ngày-tuần, PDH/PDL, VCL). Mức cố định tính ở nến đầu phiên; VCL chỉ chạy khi Sr.UseVcl.</summary>
        public readonly BenzoSr Sr = new BenzoSr();
        private int _weekNo = -1, _sessWeek = -1;
        private double _sessVol, _sessH = double.NegativeInfinity, _sessL = double.PositiveInfinity;
        /// <summary>Các lớp vùng mới của setup C (v6: hình dạng D/P/b + VA nhỏ CHoCH; v7: hành lang S/R). Chỉ chạy khi được bật (BenzoLayers.Configure).</summary>
        public readonly BenzoLayers Layers;

        private readonly ModeTracker _trkDef, _trkC;
        private readonly Queue<M5Bar> _pending = new();
        private M5Bar _cur;
        private ZoneSnap _lastSnap;

        // ---- phiên ----
        private double _sPV, _sV, _wPV, _wV;
        private int _sessBars, _nEu, _nIb;
        private readonly Dictionary<long, double> _full = new(), _eu = new();
        private bool _euDecided, _ibDecided;
        private double _ibHiAcc = double.NegativeInfinity, _ibLoAcc = double.PositiveInfinity;
        private double _bigRange;
        private int _bigPos;
        private string _groupKey; private int _groupBias;
        // zigzag
        private int _zzState; private double _hv, _lv; private int _hp, _lp;

        public BenzoZones()
        {
            _trkDef = new ModeTracker(SelDefault);
            _trkC = new ModeTracker(SelC);
            Layers = new BenzoLayers(this);
        }

        // ---- chọn band ----
        private static bool Pick(double euV, double euL, double ibH, double ibL, out double hi, out double lo, out string src)
        {
            if (!double.IsNaN(euV)) { hi = euV; lo = euL; src = "va_eu"; return true; }
            if (!double.IsNaN(ibH)) { hi = ibH; lo = ibL; src = "ib"; return true; }
            hi = lo = double.NaN; src = ""; return false;
        }
        public static bool SelDefault(ZoneSnap z, out double hi, out double lo, out string src) =>
            Pick(z.EuVah, z.EuVal, z.IbHi, z.IbLo, out hi, out lo, out src);
        public static bool SelC(ZoneSnap z, out double hi, out double lo, out string src) =>
            z.Sm < BenzoKernel.SmUsStart ? Pick(z.YdVah, z.YdVal, z.IbHi, z.IbLo, out hi, out lo, out src)
                                         : Pick(z.EuVah, z.EuVal, z.IbHi, z.IbLo, out hi, out lo, out src);

        /// <summary>Band của setup A: phase US ⇒ VA Âu (chưa có ⇒ IB); phase khác ⇒ VA hôm qua. src: "EU"|"IB"|"Y"|"".</summary>
        public static bool SelA(ZoneSnap z, out double hi, out double lo, out string src)
        {
            bool us = z.Phase == "US";
            if (us && !double.IsNaN(z.EuVah)) { hi = z.EuVah; lo = z.EuVal; src = "EU"; return true; }
            if (us && double.IsNaN(z.EuVah) && !double.IsNaN(z.IbHi)) { hi = z.IbHi; lo = z.IbLo; src = "IB"; return true; }
            if (!us && !double.IsNaN(z.YdVah)) { hi = z.YdVah; lo = z.YdVal; src = "Y"; return true; }
            hi = lo = double.NaN; src = ""; return false;
        }

        private ZoneSnap Snap() => new ZoneSnap
        {
            EuVah = EuVah, EuVal = EuVal, IbHi = IbHi, IbLo = IbLo, YdVah = YdVah, YdVal = YdVal, Sm = Sm, Phase = Phase,
            ShKind = Layers.ShKind, TLo = Layers.TLo, THi = Layers.THi
        };

        // ---------------------------------------------------------------- Push
        public void Push(int idx, BarData bar, IReadOnlyList<LevelVol> levels)
        {
            if (idx != Bars.Count) throw new InvalidOperationException($"BenzoZones.Push phải tuần tự: nhận {idx}, mong {Bars.Count}");
            Bars.Add(bar);
            NewM5.Clear();
            Idx = idx;
            bool first = idx == 0;
            double gap = first ? 0 : (bar.Time - Bars[idx - 1].Time).TotalMinutes;
            NewSession = first || gap > BenzoKernel.GapMinutes;
            bool newWeek = first || gap > BenzoKernel.WeekGapMinutes;
            if (newWeek) _weekNo++;
            Layers.BeginBar(idx, bar, NewSession);
            if (NewSession) StartSession(idx, first);
            if (newWeek) { WeekStartIdx = idx; _wPV = 0; _wV = 0; }

            // ---- giờ / phase ----
            Sm = BenzoKernel.SmOf(bar.Time, TzOffset, UsShift);
            Phase = BenzoKernel.PhaseOf(Sm);
            bool isEu = Sm >= BenzoKernel.SmEuStart && Sm < BenzoKernel.SmUsStart;
            bool isIb = Sm >= BenzoKernel.SmIbStart && Sm < BenzoKernel.SmIbEnd;

            // ---- M5: đóng nến M5 trước nếu đổi xô/phiên (thiếu nến phút cuối) ----
            DateTime b5 = new DateTime(bar.Time.Year, bar.Time.Month, bar.Time.Day, bar.Time.Hour, bar.Time.Minute - bar.Time.Minute % 5, 0, bar.Time.Kind);
            if (NewSession) { _cur = null; _pending.Clear(); _trkDef.Reset(); _trkC.Reset(); }
            else if (_cur != null && _cur.T5Start != b5) CloseCur(idx - 1, _lastSnap);
            // chế độ chỉ thấy các nến M5 đã đóng TRƯỚC giờ mở nến này
            while (_pending.Count > 0 && _pending.Peek().T5End <= bar.Time)
            {
                var m = _pending.Dequeue();
                _trkDef.OnM5(m); _trkC.OnM5(m);
                Layers.FeedM5(m);
            }

            // ---- VWAP ----
            double tp = (bar.H + bar.L + bar.C) / 3.0;
            _sPV += tp * bar.Vol; _sV += bar.Vol;
            _wPV += tp * bar.Vol; _wV += bar.Vol;
            VwapD = _sV > 0 ? _sPV / _sV : bar.C;
            VwapW = _wV > 0 ? _wPV / _wV : bar.C;

            // ---- VA Âu / IB: chốt ở nến đầu tiên có Sm >= mốc (chỉ dùng nến TRƯỚC nó) ----
            if (!_euDecided && Sm >= BenzoKernel.SmUsStart)
            {
                _euDecided = true;
                if (_nEu >= BenzoKernel.MinEuBars && _eu.Count > 0 &&
                    BenzoKernel.ValueAreaOf(_eu, out double p, out double vh, out double vl)) { EuPoc = p; EuVah = vh; EuVal = vl; }
            }
            if (!_ibDecided && Sm >= BenzoKernel.SmIbEnd)
            {
                _ibDecided = true;
                if (_nIb >= BenzoKernel.MinIbBars) { IbHi = _ibHiAcc; IbLo = _ibLoAcc; }
            }

            // ---- profile volume của phiên ----
            AddProfile(bar, levels, isEu);
            Layers.AddBar(bar);
            _sessBars++;
            _sessVol += bar.Vol; _sessH = Math.Max(_sessH, bar.H); _sessL = Math.Min(_sessL, bar.L);
            if (isEu) _nEu++;
            if (isIb) { _nIb++; _ibHiAcc = Math.Max(_ibHiAcc, bar.H); _ibLoAcc = Math.Min(_ibLoAcc, bar.L); }

            // ---- chỉ số vị trí ----
            _sess.Add(SessionNo); _posS.Add(idx - SessionStartIdx); _posW.Add(idx - WeekStartIdx); _sm.Add(Sm);
            _phase.Add(Phase); _vD.Add(VwapD); _vW.Add(VwapW);

            // ---- nến dài nhất phiên ----
            double rng = bar.H - bar.L;
            PrevBigRange = NewSession ? double.NegativeInfinity : _bigRange;
            if (NewSession || rng > _bigRange) { _bigRange = rng; _bigPos = idx; }
            BarsSinceBig = idx - _bigPos;
            _bigSince.Add(BarsSinceBig);

            // ---- trung vị ----
            _absDelta.Add(Math.Abs(bar.Delta)); _rangeList.Add(rng);
            Mad = BenzoKernel.RollingMedian(_absDelta);
            U = BenzoKernel.RollingMedian(_rangeList);
            _mad.Add(Mad);
            // 'có move rõ': biên độ 60 nến gần nhất >= 2u
            MoveClear = false;
            if (Bars.Count >= 60 && !double.IsNaN(U))
            {
                double mx = double.NegativeInfinity, mn = double.PositiveInfinity;
                for (int k = Bars.Count - 60; k < Bars.Count; k++) { mx = Math.Max(mx, Bars[k].H); mn = Math.Min(mn, Bars[k].L); }
                MoveClear = (mx - mn) >= 2.0 * U;
            }
            _moveClear.Add(MoveClear);

            // ---- bias (dấu close − VWAP tuần ở nến đầu của mỗi (phiên, phase)) ----
            string key = SessionNo + "|" + Phase;
            if (key != _groupKey) { _groupKey = key; _groupBias = Math.Sign(bar.C - VwapW); }
            Bias = _groupBias; _bias.Add(Bias);

            ZigzagStep(idx, bar, NewSession);

            // ---- chế độ hiện tại (sau khi đã đẩy các M5 đóng trước nến này) ----
            _mode.Add(_trkDef.Cur.Mode);

            // ---- M5 gộp nến này; đóng nếu là phút cuối xô ----
            if (_cur == null)
                _cur = new M5Bar { SessionNo = SessionNo, T5Start = b5, T5End = b5.AddMinutes(5), O = bar.O, H = bar.H, L = bar.L, C = bar.C, FirstIdx = idx };
            else { _cur.H = Math.Max(_cur.H, bar.H); _cur.L = Math.Min(_cur.L, bar.L); _cur.C = bar.C; }
            _cur.Delta += bar.Delta; _cur.LastIdx = idx;
            _lastSnap = Snap();
            if (bar.Time.Minute % 5 == 4) CloseCur(idx, _lastSnap);

            // ---- lõi VCL (chỉ khi setup B bật nhóm vùng S/R) ----
            Sr.PushVcl(idx, bar, levels, TzOffset, UsShift);
            // ---- các lớp vùng mới của setup C (chỉ chạy khi được bật) ----
            Layers.EndBar(idx, bar, levels);
        }

        private void CloseCur(int lastIdx, ZoneSnap snap)
        {
            var m = _cur; _cur = null;
            if (m == null) return;
            m.LastIdx = lastIdx; m.Snap = snap;
            NewM5.Add(m); _pending.Enqueue(m);
        }

        private void StartSession(int idx, bool first)
        {
            // lưu phiên vừa đóng cho nhóm vùng thêm của B (HVN/POC ngày-tuần, PDH/PDL)
            if (!first && _sessBars > 0)
                Sr.CloseSession(new SessRec { No = SessionNo, Week = _sessWeek, Start = SessionStartIdx, N = _sessBars, Vol = _sessVol, High = _sessH, Low = _sessL, Prof = new Dictionary<long, double>(_full) });
            // chốt phiên trước thành "phiên hôm qua" nếu đủ nến
            if (!first && _sessBars >= BenzoKernel.MinBarsProf && _full.Count > 0 &&
                BenzoKernel.ValueAreaOf(_full, out double p, out double vh, out double vl))
            {
                HasYd = true; YdPoc = p; YdVah = vh; YdVal = vl;
                Layers.OnSessionStart(true);
            }
            else Layers.OnSessionStart(false);
            SessionNo++;
            SessionStartIdx = idx;
            _sPV = 0; _sV = 0; _sessBars = 0; _nEu = 0; _nIb = 0;
            _full.Clear(); _eu.Clear();
            _euDecided = false; _ibDecided = false;
            EuPoc = EuVah = EuVal = double.NaN; IbHi = IbLo = double.NaN;
            _ibHiAcc = double.NegativeInfinity; _ibLoAcc = double.PositiveInfinity;
            _groupKey = null;
            _sessVol = 0; _sessH = double.NegativeInfinity; _sessL = double.PositiveInfinity;
            _sessWeek = _weekNo;
            Sr.BeginSession(_weekNo);
        }

        private void AddProfile(BarData bar, IReadOnlyList<LevelVol> levels, bool isEu)
        {
            if (levels != null && levels.Count > 0)
            {
                foreach (var lv in levels)
                {
                    long row = (long)Math.Round(lv.Price / BenzoKernel.RowStep);
                    _full[row] = (_full.TryGetValue(row, out var a) ? a : 0) + lv.Vol;
                    if (isEu) _eu[row] = (_eu.TryGetValue(row, out var b) ? b : 0) + lv.Vol;
                }
            }
            else if (bar.Vol > 0)
            {   // không có per-level: rải đều volume nến lên các hàng từ low đến high (xấp xỉ như kernel)
                long lo = (long)Math.Round(bar.L / BenzoKernel.RowStep), hi = (long)Math.Round(bar.H / BenzoKernel.RowStep);
                if (hi < lo) hi = lo;
                double v = bar.Vol / (hi - lo + 1);
                for (long r = lo; r <= hi; r++)
                {
                    _full[r] = (_full.TryGetValue(r, out var a) ? a : 0) + v;
                    if (isEu) _eu[r] = (_eu.TryGetValue(r, out var b) ? b : 0) + v;
                }
            }
        }

        // ---- zigzag ngưỡng 2 giá, không nhìn trước, reset mỗi phiên ----
        private void ZigzagStep(int j, BarData b, bool reset)
        {
            double thr = BenzoKernel.ZzThreshold;
            if (reset)
            {
                _zzState = 0; _hv = b.H; _hp = j; _lv = b.L; _lp = j; return;
            }
            if (_zzState == 0)
            {
                if (b.H > _hv) { _hv = b.H; _hp = j; }
                if (b.L < _lv) { _lv = b.L; _lp = j; }
                if (_hv - _lv >= thr)
                {
                    if (_lp <= _hp)
                    {
                        Pivots.Add(new Pivot { Pos = _lp, Price = _lv, IsHigh = false, ConfirmPos = j });
                        _zzState = 1; _hv = _lp < j ? b.H : double.NegativeInfinity; _hp = j;
                    }
                    else
                    {
                        Pivots.Add(new Pivot { Pos = _hp, Price = _hv, IsHigh = true, ConfirmPos = j });
                        _zzState = -1; _lv = _hp < j ? b.L : double.PositiveInfinity; _lp = j;
                    }
                }
            }
            else if (_zzState == 1)
            {
                if (b.H > _hv) { _hv = b.H; _hp = j; }
                if (_hv - b.L >= thr)
                {
                    Pivots.Add(new Pivot { Pos = _hp, Price = _hv, IsHigh = true, ConfirmPos = j });
                    _zzState = -1; _lv = _hp < j ? b.L : double.PositiveInfinity; _lp = j;
                }
            }
            else
            {
                if (b.L < _lv) { _lv = b.L; _lp = j; }
                if (b.H - _lv >= thr)
                {
                    Pivots.Add(new Pivot { Pos = _lp, Price = _lv, IsHigh = false, ConfirmPos = j });
                    _zzState = 1; _hv = _lp < j ? b.H : double.NegativeInfinity; _hp = j;
                }
            }
        }
    }
}
