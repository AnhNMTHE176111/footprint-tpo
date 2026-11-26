// ============================================================================
//  BenzoNq — lõi THUẦN của chuẩn setup CORVEN cho NQ M1 (bản 3: Break + Follow trend, không bias)
//  Port y chữ benzo-trader/research/nq_setup_2026-11-26/nq_setup.py (SPEC-SETUP-NQ.md). Parity: tools/ReplayNq + parity_nq.py.
//  Chạy TĂNG DẦN: Step(i) khi nến i đã đóng và nến i+1 đã mở (cần Open/thời gian của nến i+1 để vào lệnh / xét khoảng trống).
//  Không phụ thuộc Quantower (test được). Range = RangeLogic.cs (Range Box), tín hiệu order flow = OrderFlowBubbles (NqSig).
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.Linq;
    using RangeBox;

    public sealed class NqCfg
    {
        public int W = 3;                 // cửa sổ phản ứng [i-2, i]
        public int ZoneMaxAge = 30;       // vùng stacked "gần"
        public double ZoneBody = 0.5;     // ≥ 50 % vùng trong thân nến sinh
        public double DeltaK = 1.0;       // |delta| ≥ 1,0 × TB |delta| 20 nến trước
        public int DeltaN = 20;
        public int ExhBlock = 5;          // kiệt sức ngược phe chưa bị quét trong 5 nến → chặn
        public int RetryLook = 30;
        public double ShPokeBub = 0.75;   // bóng trong 0,75 điểm quanh cạnh (stop hunt tại cạnh range)
        public double SlPad = 2.0, SlMin = 5.0, SlMaxMbr = 3.0;
        public double RrTp = 2.0, RrFbRoom = 1.7;
        public int BiasWarm = 30;
        public double BigNear = 10.0;
        public double Cost = 1.0;         // điểm/lệnh khứ hồi (chỉ để tính R)
        public int NoEntryMin = 16 * 60 + 45, CloseMin = 16 * 60 + 59;   // giờ New York
        public bool UseD = true;
        public bool UseBias = false;      // bản 3 (người học): bỏ bias, đánh theo cấu trúc và bối cảnh
        public bool FailBreak = false;    // bản 2 (người học): bỏ Fail Break
        public bool ZoneTest = false;     // bản 3 (người học): follow trend không cần vùng stacked
        public bool Follow = true;        // bản 3: Follow trend = nhịp hồi nông của move đang đi
        public int FollowLook = 30;       //   move tìm trong 30 nến trước nến tín hiệu
        public double FollowMoveMbr = 2.0;//   move ≥ 2 × mbr ("để ý momentum")
        public double FollowDepth = 0.5;  //   hồi không sâu quá 50 % move ("không được test quá sâu")
        public int FollowMaxPb = 10;      //   hồi 1–10 nến
        public double Tick = 0.25;
        public const string Version = "nq-corven-3";

        /// <summary>Bản cũ để đối chiếu parity: 1 = có Fail Break + Test vùng stacked + bias; 2 = bỏ Fail Break; 3 = hiện tại.</summary>
        public static NqCfg ForVersion(string v)
        {
            var c = new NqCfg();
            if (v == "1") { c.FailBreak = true; c.ZoneTest = true; c.Follow = false; c.UseBias = true; }
            else if (v == "2") { c.ZoneTest = true; c.Follow = false; c.UseBias = true; }
            return c;
        }
    }

    public struct NqBar
    {
        public DateTime T;                // UTC, giờ MỞ nến
        public double O, H, L, C, D, V;   // D = delta nến, V = volume
    }

    /// <summary>Tín hiệu OrderFlowBubbles theo chỉ số nến (đúng nghĩa marks.csv / sh.csv / bt_side.csv của Python).</summary>
    public sealed class NqSig
    {
        public readonly Dictionary<int, List<double>> DotB = new(), DotS = new();
        public readonly Dictionary<int, List<(double P, int S)>> Bt = new();
        public readonly HashSet<int> ExhT = new(), ExhB = new();
        public readonly Dictionary<int, List<(int Side, double Lo, double Hi)>> Zones = new();
        public readonly Dictionary<int, HashSet<(int Side, double Level)>> Sh = new();   // Side: +1 quét đỉnh, −1 quét đáy

        static List<T> L<T>(Dictionary<int, List<T>> d, int i) { if (!d.TryGetValue(i, out var l)) d[i] = l = new List<T>(); return l; }
        public void AddDot(int i, int side, double p) => L(side < 0 ? DotS : DotB, i).Add(p);
        public void AddBt(int i, double p, int side) => L(Bt, i).Add((p, side));
        public void AddZone(int i, int side, double lo, double hi) => L(Zones, i).Add((side, lo, hi));
        public void AddSh(int i, int side, double lv) { if (!Sh.TryGetValue(i, out var s)) Sh[i] = s = new HashSet<(int, double)>(); s.Add((side, lv)); }
        public void Clear() { DotB.Clear(); DotS.Clear(); Bt.Clear(); ExhT.Clear(); ExhB.Clear(); Zones.Clear(); Sh.Clear(); }
    }

    public sealed class NqTrade
    {
        public int Sig, Touch, ExitI = -1;
        public string Kind;               // "Break" / "Test vùng stacked" / "Fail Break"
        public int Side;
        public double Entry, Sl, Tp, Dist, Edge, Room, ExitPx, R, RGross;
        public string Second, Bias, Big, BigLv, Session, Note, How = "";
        public DateTime SigTime, EntryTime, ExitTime;
        public bool Closed => How != "";
        public string SideText => Side > 0 ? "buy" : "sell";
    }

    public static class NqTime
    {
        static TimeZoneInfo _ny;
        public static TimeZoneInfo NyZone
        {
            get
            {
                if (_ny != null) return _ny;
                try { _ny = TimeZoneInfo.FindSystemTimeZoneById("Eastern Standard Time"); }
                catch { _ny = TimeZoneInfo.FindSystemTimeZoneById("America/New_York"); }
                return _ny;
            }
        }
        public static DateTime Ny(DateTime utc) => TimeZoneInfo.ConvertTimeFromUtc(DateTime.SpecifyKind(utc, DateTimeKind.Utc), NyZone);
        public static int NyMin(DateTime utc) { var n = Ny(utc); return n.Hour * 60 + n.Minute; }

        /// <summary>Á 18:00–03:00, Âu 03:00–09:30, Mỹ 09:30–17:00 (giờ New York). Trả (tên, khoá phiên).</summary>
        public static (string Name, (DateTime, string) Key) Session(DateTime utc)
        {
            var n = Ny(utc); int m = n.Hour * 60 + n.Minute;
            if (m >= 18 * 60) return ("A", (n.Date.AddDays(1), "A"));
            if (m < 3 * 60) return ("A", (n.Date, "A"));
            if (m < 9 * 60 + 30) return ("E", (n.Date, "E"));
            return ("U", (n.Date, "U"));
        }

        public static DateTime TradeDay(DateTime utc) { var n = Ny(utc); return n.Hour >= 18 ? n.Date.AddDays(1) : n.Date; }
    }

    /// <summary>Mốc lớn (luật 9): chỉ gắn nhãn kịch bản, không lọc.</summary>
    public sealed class NqBigLevels
    {
        const double Row = 2.0;
        DateTime? _day; (int, int)? _week;
        double _vd0, _vd1, _vw0, _vw1;
        Dictionary<int, HashSet<(DateTime, int, int)>> _tpoDay = new(), _tpoWeek = new();
        double? _pocDay, _pocWeek;
        bool _leftDay, _leftWeek;

        static double? Poc(Dictionary<int, HashSet<(DateTime, int, int)>> tpo)
        {
            if (tpo.Count == 0) return null;
            int mx = tpo.Values.Max(p => p.Count);
            var rows = tpo.Keys.OrderBy(r => r).ToList();
            double mid = (rows[0] + rows[rows.Count - 1]) / 2.0;
            int best = rows.Where(r => tpo[r].Count == mx).OrderBy(r => Math.Abs(r - mid)).ThenBy(r => r).First();
            return (best + 0.5) * Row;
        }

        public void Update(DateTime t, double h, double l, double c, double v)
        {
            var td = NqTime.TradeDay(t);
            var wk = (ISOWeek.GetYear(td), ISOWeek.GetWeekOfYear(td));
            if (_day != td)
            {
                if (_day != null) _pocDay = Poc(_tpoDay);
                _day = td; _vd0 = _vd1 = 0; _tpoDay = new(); _leftDay = false;
            }
            if (_week != wk)
            {
                if (_week != null) _pocWeek = Poc(_tpoWeek);
                _week = wk; _vw0 = _vw1 = 0; _tpoWeek = new(); _leftWeek = false;
            }
            double tp = (h + l + c) / 3.0;
            _vd0 += tp * v; _vd1 += v; _vw0 += tp * v; _vw1 += v;
            var n = NqTime.Ny(t);
            var per = (n.Date, n.Hour, n.Minute / 30);
            for (int r = (int)Math.Floor(l / Row); r <= (int)Math.Floor(h / Row); r++)
            {
                if (!_tpoDay.TryGetValue(r, out var a)) _tpoDay[r] = a = new(); a.Add(per);
                if (!_tpoWeek.TryGetValue(r, out var b)) _tpoWeek[r] = b = new(); b.Add(per);
            }
            if (_pocDay != null && !(l <= _pocDay && _pocDay <= h)) _leftDay = true;
            if (_pocWeek != null && !(l <= _pocWeek && _pocWeek <= h)) _leftWeek = true;
        }

        public (string Lab, string Lv) Label(double price, double near)
        {
            var wk = new List<string>(); var dy = new List<string>();
            if (_vw1 > 0 && Math.Abs(price - _vw0 / _vw1) <= near) wk.Add("VWAP tuần");
            if (_pocWeek != null && _leftWeek && Math.Abs(price - _pocWeek.Value) <= near) wk.Add("POC tuần trước");
            if (_vd1 > 0 && Math.Abs(price - _vd0 / _vd1) <= near) dy.Add("VWAP ngày");
            if (_pocDay != null && _leftDay && Math.Abs(price - _pocDay.Value) <= near) dy.Add("POC hôm trước");
            if (wk.Count > 0) return ("kịch bản 1", string.Join("+", wk.Concat(dy)));
            if (dy.Count > 0) return ("kịch bản 2.1", string.Join("+", dy));
            return ("kịch bản 2.2", "");
        }
    }

    public sealed class NqZone
    {
        public int Side; public double Lo, Hi; public int Birth, OkAt = -1, ReadyAt = -1, Touch = -1;
        public bool Dead, Used;
    }

    public sealed class NqMachine
    {
        public readonly NqCfg Cfg;
        public readonly List<NqBar> B;
        public readonly NqSig S;
        public readonly RangeLogic Eng;
        readonly List<double> _ph = new(), _pl = new();
        public readonly List<int> Dir = new();
        public readonly List<int> Bias = new();
        public List<NqZone> Zones = new();
        readonly NqBigLevels _big = new();
        (DateTime, string)? _sessKey; int _sessStart; double _sessOpen, _cumd;
        public readonly List<NqTrade> Trades = new();
        public NqTrade Open;              // lệnh đang mở (chưa đóng)
        public DateTime CountFrom = DateTime.MinValue;
        public int Processed;             // số nến đã Step
        // ảnh range sau nến i: (id, state, top, bot, tol, breakSide) — giá thật
        List<(int Id, RangeState St, double Top, double Bot, double Tol, int BSide)> _snap = new();
        public IReadOnlyList<(int Id, RangeState St, double Top, double Bot, double Tol, int BSide)> Snap => _snap;
        public readonly List<(int I, string Kind, int Side, string Why)> Cands = new();
        readonly HashSet<int> _usedLegs = new();   // bản 3: nến đỉnh/đáy của move đã vào Follow trend
        public bool KeepCands = false;

        public NqMachine(List<NqBar> bars, NqSig sig, NqCfg cfg = null)
        {
            B = bars; S = sig; Cfg = cfg ?? new NqCfg();
            Eng = new RangeLogic(Cfg.Tick, new RangeParams());
        }

        public double MbrPts => Eng.Mbr * Cfg.Tick;

        /// <summary>Nến i đã đóng; B phải có nến i+1 (đang chạy hoặc đã đóng).</summary>
        public void Step(int i)
        {
            if (i != Processed) throw new InvalidOperationException($"Step({i}) sai thứ tự, chờ {Processed}");
            if (i + 1 >= B.Count) throw new InvalidOperationException("thiếu nến i+1");
            var b = B[i];
            Eng.Feed(b.O, b.H, b.L, b.C);
            _snap = new();
            foreach (var r in Eng.Ranges)
                if (r.State != RangeState.Dead)
                    _snap.Add((r.Id, r.State, r.Top * Cfg.Tick, r.Bottom * Cfg.Tick, r.Tol * Cfg.Tick, r.BreakSide));
            Structure(i);
            BiasStep(i);
            ZonesStep(i);
            _big.Update(b.T, b.H, b.L, b.C, b.V);
            Processed = i + 1;
            // lệnh đang mở: xét nến i (trước khi xét tín hiệu mới ở chính nến này)
            if (Open != null && Open.Sig + 1 <= i)
            {
                if (SimStep(Open, i)) Open = null;
            }
            if (b.T < CountFrom) return;
            foreach (var c in CandsAt(i)) Consider(i, c.Kind, c.Side, c.Tb, c.Edge, c.Room, c.Zone, c.Note, c.Leg);
        }

        // ---------- tầng A: cấu trúc
        void Structure(int i)
        {
            int d = Dir.Count > 0 ? Dir[Dir.Count - 1] : 0;
            if (i >= 2)
            {
                int j = i - 1; bool newp = false;
                if (B[j].H > B[j - 1].H && B[j].H >= B[i].H) { _ph.Add(B[j].H); newp = true; }
                if (B[j].L < B[j - 1].L && B[j].L <= B[i].L) { _pl.Add(B[j].L); newp = true; }
                if (newp && _ph.Count >= 2 && _pl.Count >= 2)
                {
                    int a = _ph.Count, c = _pl.Count;
                    if (_ph[a - 1] > _ph[a - 2] && _pl[c - 1] > _pl[c - 2]) d = 1;
                    else if (_ph[a - 1] < _ph[a - 2] && _pl[c - 1] < _pl[c - 2]) d = -1;
                }
                if (_ph.Count > 0 && B[i].C > _ph[_ph.Count - 1]) d = 1;
                else if (_pl.Count > 0 && B[i].C < _pl[_pl.Count - 1]) d = -1;
                if (_ph.Count > 50) _ph.RemoveRange(0, _ph.Count - 10);
                if (_pl.Count > 50) _pl.RemoveRange(0, _pl.Count - 10);
            }
            Dir.Add(d);
        }

        // ---------- bias phiên (luật 8)
        void BiasStep(int i)
        {
            var key = NqTime.Session(B[i].T).Key;
            if (_sessKey == null || !_sessKey.Value.Equals(key) || (i > 0 && (B[i].T - B[i - 1].T) > TimeSpan.FromMinutes(30)))
            {
                _sessKey = key; _sessStart = i; _sessOpen = B[i].O; _cumd = 0;
            }
            _cumd += B[i].D;
            int v = 0;
            if (i - _sessStart + 1 > Cfg.BiasWarm)
            {
                double dp = B[i].C - _sessOpen;
                if (_cumd > 0 && dp > 0) v = 1; else if (_cumd < 0 && dp < 0) v = -1;
            }
            Bias.Add(v);
        }

        // ---------- vùng stacked (7a–7d)
        void ZonesStep(int i)
        {
            var b = B[i];
            if (S.Zones.TryGetValue(i, out var zl))
                foreach (var (sd, lo, hi) in zl)
                {
                    var z = new NqZone { Side = sd, Lo = lo, Hi = hi, Birth = i };
                    double bl = Math.Min(b.O, b.C), bh = Math.Max(b.O, b.C);
                    double ov = Math.Max(0.0, Math.Min(hi, bh) - Math.Max(lo, bl));
                    double hgt = hi - lo;
                    bool inside = hgt > 0 ? ov >= Cfg.ZoneBody * hgt - 1e-9 : (bl <= lo && lo <= bh);
                    if (inside) z.OkAt = i;
                    Zones.Add(z);
                }
            foreach (var z in Zones)
            {
                if (z.Dead || z.Birth == i) continue;
                if (z.OkAt < 0)
                {
                    if (i == z.Birth + 1 && ((z.Side > 0 && b.C > z.Hi) || (z.Side < 0 && b.C < z.Lo))) z.OkAt = i;
                    else { z.Dead = true; continue; }
                }
                if ((z.Side > 0 && b.C < z.Lo) || (z.Side < 0 && b.C > z.Hi)) { z.Dead = true; continue; }
                if (i - z.Birth > Cfg.ZoneMaxAge) { z.Dead = true; continue; }
                if (Dir[i] != z.Side) { z.Dead = true; continue; }
                if (z.ReadyAt < 0)
                {
                    if (i >= z.OkAt && ((z.Side > 0 && b.L > z.Hi) || (z.Side < 0 && b.H < z.Lo))) z.ReadyAt = i;
                }
                else if (z.Touch < 0)
                {
                    if ((z.Side > 0 && b.L <= z.Hi) || (z.Side < 0 && b.H >= z.Lo)) z.Touch = i;
                }
                if (z.Touch >= 0 && i > z.Touch + Cfg.W - 1) z.Dead = true;
            }
            foreach (var z in Zones)
                if (z.Birth == i && Dir[i] != z.Side) z.Dead = true;
            if (Zones.Count > 400) Zones = Zones.Where(z => !z.Dead).ToList();
        }

        // ---------- tín hiệu order flow
        bool BubbleSide(int i, int side)
        {
            if (side > 0) return (S.DotB.TryGetValue(i, out var a) && a.Count > 0) || (S.Bt.TryGetValue(i, out var t) && t.Any(x => x.S > 0));
            return (S.DotS.TryGetValue(i, out var c) && c.Count > 0) || (S.Bt.TryGetValue(i, out var u) && u.Any(x => x.S < 0));
        }

        IEnumerable<double> AnyBubblePrices(int i)
        {
            if (S.DotB.TryGetValue(i, out var a)) foreach (var p in a) yield return p;
            if (S.DotS.TryGetValue(i, out var c)) foreach (var p in c) yield return p;
            if (S.Bt.TryGetValue(i, out var t)) foreach (var x in t) yield return x.P;
        }

        bool ExhValid(int m, int i, int side)
        {
            if (side > 0) { for (int k = m + 1; k <= i; k++) if (B[k].L < B[m].L) return false; return true; }
            for (int k = m + 1; k <= i; k++) if (B[k].H > B[m].H) return false;
            return true;
        }

        bool DeltaOk(int i, int side)
        {
            int n = Cfg.DeltaN;
            if (i < n) return false;
            double sum = 0; for (int k = i - n; k < i; k++) sum += Math.Abs(B[k].D);
            double avg = sum / n;
            return B[i].D * side > 0 && Math.Abs(B[i].D) >= Cfg.DeltaK * avg;
        }

        bool CandleOk(int i, int side)
        {
            var b = B[i]; double rng = b.H - b.L;
            if (rng <= 0) return false;
            if (side > 0) return b.C > b.O && (b.C - b.L) / rng >= 0.5;
            return b.C < b.O && (b.H - b.C) / rng >= 0.5;
        }

        List<string> Second(int i, int side, double? edge, bool zoneTest)
        {
            var o = new List<string>();
            int w0 = Math.Max(0, i - Cfg.W + 1);
            var ex = side > 0 ? S.ExhB : S.ExhT;
            for (int m = w0; m <= i; m++) if (ex.Contains(m) && ExhValid(m, i, side)) { o.Add("kiệt sức"); break; }
            int shs = side > 0 ? -1 : 1;
            bool hit = false;
            for (int m = w0; m <= i; m++)
                if (S.Sh.TryGetValue(m, out var set))
                    foreach (var (sd, lv) in set)
                        if (sd == shs && ((side > 0 && B[i].C > lv) || (side < 0 && B[i].C < lv))) hit = true;
            if (!hit && edge != null)
            {
                double e = edge.Value, tk = Cfg.Tick;
                for (int m = w0; m <= i; m++)
                {
                    if (side > 0 && B[m].L <= e - tk + 1e-9 && AnyBubblePrices(m).Any(p => p <= e + Cfg.ShPokeBub + 1e-9)) hit = true;
                    if (side < 0 && B[m].H >= e + tk - 1e-9 && AnyBubblePrices(m).Any(p => p >= e - Cfg.ShPokeBub - 1e-9)) hit = true;
                }
            }
            if (hit) o.Add("stop hunt");
            foreach (var z in Zones)
                if (z.Side == side && z.Birth >= w0 && z.Birth <= i && z.OkAt >= 0 && z.OkAt <= i) { o.Add("stacked mới"); break; }
            if (zoneTest) o.Add("vùng đang test");
            return o;
        }

        bool ExhBlock(int i, int side)
        {
            var ex = side > 0 ? S.ExhT : S.ExhB;
            for (int m = Math.Max(0, i - Cfg.ExhBlock + 1); m <= i; m++)
                if (ex.Contains(m) && ExhValid(m, i, -side)) return true;
            return false;
        }

        bool Retry2(int i, int side, double top, double bot)
        {
            int w0 = Math.Max(0, i - Cfg.W + 1), lo0 = Math.Max(0, w0 - Cfg.RetryLook);
            double? prev = null;
            for (int m = w0 - 1; m >= lo0; m--)
            {
                if (side > 0 && B[m].L <= bot - Cfg.Tick + 1e-9) { prev = B[m].L; break; }
                if (side < 0 && B[m].H >= top + Cfg.Tick - 1e-9) { prev = B[m].H; break; }
            }
            if (prev == null) return false;
            var ex = side > 0 ? S.ExhB : S.ExhT;
            for (int m = w0; m <= i; m++)
            {
                if (side > 0 && B[m].L < prev && ex.Contains(m) && ExhValid(m, i, side)) return true;
                if (side < 0 && B[m].H > prev && ex.Contains(m) && ExhValid(m, i, side)) return true;
            }
            return false;
        }

        readonly struct Cand
        {
            public readonly string Kind; public readonly int Side, Tb; public readonly double Edge; public readonly double? Room; public readonly NqZone Zone; public readonly string Note;
            public readonly int Leg;     // Follow trend: nến đỉnh/đáy của move (−1 = không)
            public Cand(string k, int s, int tb, double e, double? r, NqZone z, string n, int leg = -1) { Kind = k; Side = s; Tb = tb; Edge = e; Room = r; Zone = z; Note = n; Leg = leg; }
        }

        /// <summary>bản 3 — Follow trend: theo hướng cấu trúc; move trong FollowLook nến ≥ FollowMoveMbr × mbr; hồi 1–FollowMaxPb nến,
        /// không sâu quá FollowDepth move. Mỗi move vào tối đa 1 lần. (port y chữ nq_setup._follow)</summary>
        Cand? FollowAt(int i)
        {
            int side = Dir[i];
            if (side == 0) return null;
            int lo = Math.Max(0, i - Cfg.FollowLook);
            int h = lo, a; double move, p, depth;
            if (side > 0)
            {
                for (int k = lo; k < i; k++) if (B[k].H >= B[h].H) h = k;            // cao nhất, gần nhất nếu bằng
                if (h <= lo) return null;
                a = lo; for (int k = lo; k < h; k++) if (B[k].L < B[a].L) a = k;        // thấp nhất, sớm nhất nếu bằng
                move = B[h].H - B[a].L;
                if (h + 1 > i) return null;
                p = double.MaxValue; for (int k = h + 1; k <= i; k++) p = Math.Min(p, B[k].L);
                depth = B[h].H - p;
            }
            else
            {
                for (int k = lo; k < i; k++) if (B[k].L <= B[h].L) h = k;
                if (h <= lo) return null;
                a = lo; for (int k = lo; k < h; k++) if (B[k].H > B[a].H) a = k;
                move = B[a].H - B[h].L;
                if (h + 1 > i) return null;
                p = double.MinValue; for (int k = h + 1; k <= i; k++) p = Math.Max(p, B[k].H);
                depth = p - B[h].L;
            }
            int npb = i - h - 1;
            if (npb < 1 || npb > Cfg.FollowMaxPb || _usedLegs.Contains(h)) return null;
            if (move < Cfg.FollowMoveMbr * MbrPts - 1e-9) return null;
            if (depth > Cfg.FollowDepth * move + 1e-9) return null;
            return new Cand("Follow trend", side, h + 1, p, null, null, "", h);
        }

        List<Cand> CandsAt(int i)
        {
            var o = new List<Cand>();
            int w0 = Math.Max(0, i - Cfg.W + 1);
            bool busy = _snap.Any(r => r.St == RangeState.Active || r.St == RangeState.Pending);
            foreach (var (id, st, top, bot, tol, bside) in _snap)
            {
                if ((st == RangeState.Active || st == RangeState.Pending) && Cfg.FailBreak)
                {
                    foreach (int side in new[] { 1, -1 })
                    {
                        int tb = -1;
                        for (int m = w0; m <= i; m++)
                            if (side > 0 ? B[m].L <= bot + tol + 1e-9 : B[m].H >= top - tol - 1e-9) { tb = m; break; }
                        if (tb < 0) continue;
                        bool inside = bot < B[i].C && B[i].C < top;
                        bool retry = false;
                        if (!inside) { retry = Retry2(i, side, top, bot); if (!retry) continue; }
                        o.Add(new Cand("Fail Break", side, tb, side > 0 ? bot : top, side > 0 ? top : bot, null, retry ? "xác nhận lần 2" : ""));
                    }
                }
                else if (st == RangeState.Broken && bside != 0)
                {
                    int side = bside; double edge = side > 0 ? top : bot;
                    int tb = -1;
                    for (int m = w0; m <= i; m++)
                        if (side > 0 ? B[m].L <= top + tol + 1e-9 : B[m].H >= bot - tol - 1e-9) { tb = m; break; }
                    bool ok = side > 0 ? B[i].C > top : B[i].C < bot;
                    if (tb >= 0 && ok) o.Add(new Cand("Break", side, tb, edge, null, null, ""));
                }
            }
            if (!busy && Cfg.Follow)
            {
                var fc = FollowAt(i);
                if (fc != null) o.Add(fc.Value);
            }
            if (!busy && Cfg.ZoneTest)
                foreach (var z in Zones)
                {
                    if (z.Dead || z.Touch < 0 || z.Used) continue;
                    if (!(z.Touch <= i && i <= z.Touch + Cfg.W - 1)) continue;
                    if ((z.Side > 0 && B[i].C >= z.Hi) || (z.Side < 0 && B[i].C <= z.Lo))
                        o.Add(new Cand("Test vùng stacked", z.Side, z.Touch, z.Side > 0 ? z.Lo : z.Hi, null, z, ""));
                }
            return o;
        }

        void Consider(int i, string kind, int side, int tb, double edge, double? room, NqZone zone, string note, int leg)
        {
            var why = new List<string>();
            if (Open != null) why.Add("đang có lệnh");
            double mbr = MbrPts;
            if (kind != "Fail Break")
            {
                if (Dir[i] != side) why.Add("ngược cấu trúc");
                if (Cfg.UseBias && Bias[i] == -side) why.Add("ngược bias");
            }
            if (!CandleOk(i, side)) why.Add("nến không đẹp");
            var sec = new List<string>();
            if (Cfg.UseD)
            {
                if (!DeltaOk(i, side)) why.Add("delta nhỏ/ngược");
                if (!BubbleSide(i, side)) why.Add("không bóng cùng phe");
                sec = Second(i, side, kind == "Break" || kind == "Fail Break" ? edge : (double?)null, kind == "Test vùng stacked");
                if (sec.Count == 0) why.Add("thiếu tín hiệu thứ hai");
                if (ExhBlock(i, side)) why.Add("kiệt sức ngược phe");
            }
            if ((B[i + 1].T - B[i].T) > TimeSpan.FromMinutes(5)) why.Add("nến kế sau khoảng trống");
            int hm = NqTime.NyMin(B[i + 1].T);
            if (hm >= Cfg.NoEntryMin && hm < 18 * 60) why.Add("sau 16:45 NY");
            double entry = B[i + 1].O;
            double ext = side > 0 ? double.MaxValue : double.MinValue;
            for (int k = tb; k <= i; k++) ext = side > 0 ? Math.Min(ext, B[k].L) : Math.Max(ext, B[k].H);
            double sl, dist;
            if (side > 0) { sl = Math.Min(ext, edge) - Cfg.SlPad; dist = entry - sl; }
            else { sl = Math.Max(ext, edge) + Cfg.SlPad; dist = sl - entry; }
            if (dist <= 0) why.Add("giá vào đã qua SL");
            else
            {
                if (dist < Cfg.SlMin) { dist = Cfg.SlMin; sl = entry - side * dist; }
                if (dist > Cfg.SlMaxMbr * mbr) why.Add("SL xa quá");
                if (kind == "Fail Break" && room != null && (room.Value - entry) * side < Cfg.RrFbRoom * dist - 1e-9) why.Add("không đủ 1,7R tới cạnh đối diện");
            }
            if (KeepCands) Cands.Add((i, kind, side, string.Join(";", why)));
            if (why.Count > 0) return;
            double tp = entry + side * Cfg.RrTp * dist;
            var (lab, lv) = _big.Label(entry, Cfg.BigNear);
            var t = new NqTrade
            {
                Sig = i, Kind = kind, Side = side, Entry = entry, Sl = sl, Tp = tp, Dist = dist, Second = string.Join("+", sec),
                Bias = Bias[i] == 1 ? "buy" : Bias[i] == -1 ? "sell" : "chưa có", Big = lab, BigLv = lv,
                Session = NqTime.Session(B[i].T).Name, Note = note, Edge = edge, Room = room ?? 0.0, Touch = tb,
                SigTime = B[i].T, EntryTime = B[i + 1].T
            };
            if (zone != null) zone.Used = true;
            if (leg >= 0) _usedLegs.Add(leg);
            Trades.Add(t);
            Open = t;
        }

        /// <summary>Xét lệnh trên nến k (k ≥ nến vào). true = đã đóng. Cùng nến chạm SL và TP → SL; mở nhảy qua SL → khớp Open.
        /// Đóng TIME ở 16:59 NY hoặc trước khoảng trống > 30′ (cần nến k+1).</summary>
        bool SimStep(NqTrade t, int k)
        {
            var b = B[k]; int side = t.Side; int k0 = t.Sig + 1;
            if (k > k0)
            {
                if ((side > 0 && b.O <= t.Sl) || (side < 0 && b.O >= t.Sl)) return Close(t, k, b.O, "SL");
                if ((side > 0 && b.O >= t.Tp) || (side < 0 && b.O <= t.Tp)) return Close(t, k, t.Tp, "TP");
            }
            bool hitSl = side > 0 ? b.L <= t.Sl : b.H >= t.Sl;
            bool hitTp = side > 0 ? b.H >= t.Tp : b.L <= t.Tp;
            if (hitSl) return Close(t, k, t.Sl, "SL");
            if (hitTp) return Close(t, k, t.Tp, "TP");
            if (NqTime.NyMin(b.T) == Cfg.CloseMin || k + 1 >= B.Count || (B[k + 1].T - b.T) > TimeSpan.FromMinutes(30))
                return Close(t, k, b.C, "TIME");
            return false;
        }

        bool Close(NqTrade t, int k, double px, string how)
        {
            t.ExitI = k; t.ExitPx = px; t.How = how; t.ExitTime = B[k].T;
            double pnl = (px - t.Entry) * t.Side;
            t.RGross = pnl / t.Dist; t.R = (pnl - Cfg.Cost) / t.Dist;
            return true;
        }

        public static string Fmt(double v) => v.ToString("0.####", CultureInfo.InvariantCulture);
    }
}
