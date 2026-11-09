// Unit test setup CORVEN (plan BENZO-CORVEN mục 4 — 12 ca, mục 10.5 — 2 test cache, mục 10.3 — nhãn ở Program.cs).
// Ca 1–7, 10 dựng "thế giới" tổng hợp y như research/test_setup_corven_gd1.py (mbr 15 tick, medΔ 20, nền_ô 5,
// mọi mức bid = ask = 5 trừ khi ghi rõ) rồi gọi CorvenRules.FindSigns/EvalOrder — cùng con số kỳ vọng với test Python.
// Ca 8, 9 chạy CorvenMachine thật trên 120 nến hộp đều (như research/test_setup_corven.py).
// Ca 11, 12 + cache chạy trên file 90d thật (data-export/data-footprint/fp_GCZ26_..._90d) — CHỈ phần TRAIN.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Nodes;
using BenzoTraderNs;
using OrderFlowBubbles;

static partial class Program
{
    // ================================================================ thế giới tổng hợp (= world() Python)
    sealed class Row { public long o, h, l, c; public double d; public List<ExhLevel> lv; }
    static Row R_(long o, long h, long l, long c, double d = 0, List<ExhLevel> lv = null) => new Row { o = o, h = h, l = l, c = c, d = d, lv = lv };
    static List<ExhLevel> Uni(long l, long h, double v = 5.0)
    {
        var x = new List<ExhLevel>();
        for (long k = l; k <= h; k++) x.Add(new ExhLevel(k, v, v, 2 * v));
        return x;
    }
    static List<ExhLevel> SetLv(List<ExhLevel> lv, long tick, double? bid = null, double? ask = null)
    {
        var o = new List<ExhLevel>();
        foreach (var x in lv)
        {
            if (x.Tick == tick) { double b = bid ?? x.Bid, a = ask ?? x.Ask; o.Add(new ExhLevel(x.Tick, b, a, b + a)); }
            else o.Add(x);
        }
        return o;
    }

    static readonly DateTime W0 = new DateTime(2026, 9, 1, 2, 0, 0, DateTimeKind.Utc);
    static (CorvenFeat f, List<BarData> bars) World(List<Row> rows, DateTime? start = null, double mbr = 15, double medd = 20, double baseV = 5, List<DateTime> times = null)
    {
        var f = new CorvenFeat { Tick = 0.1 };
        var bars = new List<BarData>();
        int sess = 0, sstart = 0;
        for (int i = 0; i < rows.Count; i++)
        {
            var r = rows[i];
            var t = times != null ? times[i] : (start ?? W0).AddMinutes(i);
            if (i > 0 && (t - bars[i - 1].Time).TotalMinutes > 30) { sess++; sstart = i; }
            var b = new CorvenBar { Idx = i, Time = t, O = r.o, H = r.h, L = r.l, C = r.c, Delta = r.d, Levels = r.lv ?? Uni(r.l, r.h) };
            var ex = Of.Exhaustion(b);
            f.AddRaw(b, mbr, medd, baseV, BenzoKernel.SmOf(t), sstart, sess, ex.top, ex.bot, Of.StackedZones(b, 0.1, 250, 3, 1));
            bars.Add(new BarData { Idx = i, Time = t, O = r.o * 0.1, H = r.h * 0.1, L = r.l * 0.1, C = r.c * 0.1, Delta = r.d });
        }
        return (f, bars);
    }

    static CorvenCand Eval(CorvenCand c, CorvenFeat f, CorvenCfg cp = null)
    {
        cp ??= new CorvenCfg();
        c.Signs = CorvenRules.FindSigns(c, f, cp);
        CorvenRules.EvalOrder(c, f, cp, null);
        return c;
    }
    static CorvenMoc Canh(double lvl, double tol = 7.5) => new CorvenMoc { Kind = "canh", Level = lvl, Tol = tol, BandLo = lvl - tol, BandHi = lvl + tol };
    static Signal ToSig(CorvenCand c) => new Signal { Side = c.S, Entry = Math.Round(c.Entry * 0.1, 6), Sl = Math.Round(c.Sl * 0.1, 6), Tp = Math.Round(c.Tp * 0.1, 6) };
    static string Types(CorvenCand c) => string.Join(",", c.Signs.Select(s => s.Type));

    // ---------------------------------------------------------------- ví dụ 1 — thế A sell
    const long T1 = 41358, B1 = 41309;          // range 4130,9–4135,8
    static List<Row> Ex1Rows(double cfDelta = -15, Action<List<Row>> extra = null)
    {
        var rows = new List<Row>();
        for (int k = 0; k < 10; k++) rows.Add(R_(41335, 41340, 41328, 41333));
        rows.Add(R_(41325, 41327, 41318, 41322, -5));                                        // 10 = s (đáy nhịp)
        long p = 41322;
        for (int k = 0; k < 6; k++) { rows.Add(R_(p, p + 7, p - 1, p + 5, -3)); p += 5; }    // 11..16: nhịp lên, Δ âm
        rows.Add(R_(41352, 41380, 41350, 41362, -10, SetLv(Uni(41350, 41380), 41375, bid: 30)));   // 17 = chọc 4138,0, bóng đỏ 30 ở râu trên
        rows.Add(R_(41362, 41364, 41354, 41356, cfDelta));                                   // 18 = CF (FailBreak) đóng trong, gần cạnh
        rows.Add(R_(41356, 41420, 41355, 41415, 40));                                        // 19: vọt 4142 ⇒ chạm SL
        rows.Add(R_(41415, 41418, 41410, 41412));
        extra?.Invoke(rows);
        return rows;
    }
    static CorvenCand Ex1Cand(int cf = 18) => new CorvenCand
    {
        Cf = cf, The = 'A', S = -1, Rid = 0, Ref = 17, W0 = 17, InstTop = T1, InstBottom = B1, InstE = T1, InstFb = 18,
        InstKey = "A|0|18", LockKey = "0|1|A", Mocs = new List<CorvenMoc> { Canh(T1) }, TrapLevels = new List<double> { T1 },
    };

    // ---------------------------------------------------------------- ví dụ 2 — thế B sell, mốc stacked
    const long E2 = 41274, TOP2 = 41325;
    static List<Row> Ex2Rows(bool cfZone = false)
    {
        var rows = new List<Row>();
        for (int k = 0; k < 10; k++) rows.Add(R_(41300, 41305, 41295, 41300));
        var lv = Uni(41268, 41292);
        foreach (long k in new long[] { 41286, 41287, 41288 }) lv = SetLv(lv, k, bid: 20);      // stacked sell 4128,6–4128,8 trong cú phá
        rows.Add(R_(41290, 41292, 41268, 41270, -40, lv));                                   // 10 = nến đóng ngoài
        rows.Add(R_(41270, 41272, 41255, 41258, -30));
        rows.Add(R_(41258, 41262, 41250, 41255, -20));                                       // 12 = đáy cú đẩy (s)
        rows.Add(R_(41255, 41270, 41253, 41268, -30));                                       // 13 hồi, Δ −30
        rows.Add(R_(41268, 41284, 41266, 41280, -32, SetLv(Uni(41266, 41284), 41283, bid: 25)));   // 14 hồi, Δ −32, bóng đỏ 25
        var lv15 = Uni(41264, 41281);
        if (cfZone) foreach (long k in new long[] { 41270, 41271, 41272 }) lv15 = SetLv(lv15, k, bid: 20);
        rows.Add(R_(41279, 41281, 41264, 41266, -25, lv15));                                 // 15 = CF
        rows.Add(R_(41266, 41268, 41240, 41242, -30));
        rows.Add(R_(41242, 41244, 41200, 41205, -50));                                       // chạm TP
        return rows;
    }
    static CorvenMoc Zone(int zb, long lo, long hi, double tz = 7.5) =>
        new CorvenMoc { Kind = "stacked", Level = lo, Tol = tz, BandLo = lo - tz, BandHi = hi + tz, IsZone = true, ZBar = zb, ZLo = lo, ZHi = hi };
    static CorvenCand Ex2Cand(List<CorvenMoc> mocs = null, int cf = 15) => new CorvenCand
    {
        Cf = cf, The = 'B', S = -1, Rid = 0, Ref = 10, W0 = Math.Max(cf - 2, 11), InstTop = TOP2, InstBottom = E2, InstE = E2, InstFb = 13,
        Mocs = mocs ?? new List<CorvenMoc> { Zone(10, 41286, 41288) }, TrapLevels = new List<double> { E2 },
    };

    // ---------------------------------------------------------------- ví dụ 3 — "lần 2" (A2 KHÔNG port: chỉ kiểm bị loại)
    static (CorvenFeat f, List<BarData> bars) Ex3World()
    {
        var rows = new List<Row>();
        for (int k = 0; k < 16; k++) rows.Add(R_(41240, 41245, 41235, 41240));
        rows.Add(R_(41230, 41231, 41222, 41224, -20));                                       // 16 đóng ngoài cạnh dưới 4123,2
        rows.Add(R_(41224, 41224, 41208, 41218, 5, SetLv(Uni(41208, 41224), 41208, bid: 0, ask: 3)));   // 17 = LẦN 1: chỉ kiệt sức đáy
        var lv = Uni(41206, 41230);
        lv = SetLv(lv, 41206, bid: 0, ask: 3);                                              // kiệt sức đáy (Bid 0)
        lv = SetLv(lv, 41207, bid: 25);                                                     // bóng đỏ 25 ở râu dưới = SL phe sell khớp
        rows.Add(R_(41215, 41230, 41206, 41229, 15, lv));                                   // 18 = LẦN 2 (x)
        rows.Add(R_(41229, 41232, 41225, 41230));
        return World(rows);
    }
    static CorvenCand Ex3Cand(int cf, long ext = 41208, int w0 = -1) => new CorvenCand
    {
        Cf = cf, The = 'A', S = +1, Rid = 0, Ref = 16, W0 = w0 >= 0 ? w0 : Math.Max(16, cf - 4), InstTop = 41263, InstBottom = 41232, InstE = 41232, InstFb = cf,
        Mocs = new List<CorvenMoc> { Canh(ext) }, TrapLevels = new List<double> { ext },
    };

    // ---------------------------------------------------------------- hình học R/SL
    static (CorvenFeat f, List<BarData> bars) GeoWorld(long refHigh, double mbr = 15, int cf = 19)
    {
        var rows = new List<Row>();
        for (int k = 0; k < cf - 1; k++) rows.Add(R_(41300, 41305, 41295, 41300));
        rows.Add(R_(41340, refHigh, 41338, 41362));
        rows.Add(R_(41362, 41364, 41354, 41356, -15));
        rows.Add(R_(41356, 41357, 41350, 41351));
        return World(rows, mbr: mbr);
    }
    static CorvenCand GeoCand(long bottom, int cf = 19, long top = 41358) => new CorvenCand
    {
        Cf = cf, The = 'A', S = -1, Rid = 0, Ref = cf - 1, W0 = cf - 1, InstTop = top, InstBottom = bottom, InstE = top, InstFb = cf,
        Mocs = new List<CorvenMoc> { Canh(top) }, TrapLevels = new List<double> { top },
    };

    // ================================================================ máy thật trên hộp đều (= test_setup_corven.py)
    const long BB = 41000, TT = 41049;
    static CorvenBar Mk(int i, long o, long h, long l, long c, List<ExhLevel> lv = null)
    {
        var b = new CorvenBar { Idx = i, Time = W0.AddMinutes(i), O = o, H = h, L = l, C = c, Levels = lv };
        if (lv == null) { b.Levels = new List<ExhLevel>(); for (long k = l; k <= h; k++) b.Levels.Add(new ExhLevel(k, 1, 1, 2)); }
        return b;
    }
    static List<CorvenBar> BaseBars(int n = 120)
    {
        var cyc = new (long, long, long, long)[] { (BB + 20, BB + 25, BB, BB + 15), (BB + 15, BB + 35, BB + 10, BB + 30), (BB + 30, TT, BB + 28, TT - 8), (TT - 8, TT - 3, BB + 18, BB + 22) };
        var x = new List<CorvenBar>();
        for (int i = 0; i < n; i++) { var c = cyc[i % 4]; x.Add(Mk(i, c.Item1, c.Item2, c.Item3, c.Item4)); }
        return x;
    }
    static int Add(List<CorvenBar> bars, long o, long h, long l, long c, List<ExhLevel> lv = null) { bars.Add(Mk(bars.Count, o, h, l, c, lv)); return bars.Count - 1; }
    static (int rf, int bc) BreakUp(List<CorvenBar> bars)
    {
        int rf = Add(bars, TT - 8, TT + 12, TT - 10, TT + 8);
        Add(bars, TT + 8, TT + 30, TT + 6, TT + 25);
        Add(bars, TT + 25, TT + 45, TT + 20, TT + 40);
        int bc = Add(bars, TT + 40, TT + 60, TT + 35, TT + 55);
        return (rf, bc);
    }
    static List<ExhLevel> PushLevels(long lo, long hi, long z0)
    {
        var lv = new List<ExhLevel>();
        for (long k = lo; k <= hi; k++) { double a = z0 <= k && k <= z0 + 2 ? 10 : 1; lv.Add(new ExhLevel(k, 1, a, 1 + a)); }
        return lv;
    }
    static (CorvenMachine m, List<CorvenCand> cands) RunM(List<CorvenBar> bars, CorvenCfg cfg = null)
    {
        var m = new CorvenMachine(0.1, cfg);
        var all = new List<CorvenCand>();
        foreach (var b in bars) all.AddRange(m.Feed(b, 0, 300));
        return (m, all);
    }
    static bool HasB(List<CorvenCand> cs, int bc, int cf, string kind = "canh", int zbar = -1) =>
        cs.Any(c => c.The == 'B' && c.InstFb == bc && c.Cf == cf && c.Mocs.Any(mo => mo.Kind == kind && (zbar < 0 || mo.ZBar == zbar)));

    static string RepoRoot()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d != null && !Directory.Exists(Path.Combine(d.FullName, "data-export"))) d = d.Parent;
        return d?.FullName;
    }

    static void TestsCorven()
    {
        Console.WriteLine("[C1] Ví dụ 1 — thế A sell (range 4130,9–4135,8, bóng đỏ râu, nhịp lên ΣΔ < 0)");
        {
            var (f, bars) = World(Ex1Rows());
            var c = Eval(Ex1Cand(), f);
            Check(Types(c) == "delta,bong", "2 dấu hiệu: Δ + bóng", Types(c));
            Check(c.Signs[0].Desc.Contains("ngược giá") && c.Signs[0].Bar == 17, "Δ ngược giá neo nến 17", c.Signs[0].Desc);
            Check(c.Gates.Count == 0, "qua mọi cổng", string.Join(";", c.Gates));
            Check(c.Entry == 41356 && c.Sl == 41383, "SL 4138,3 = đỉnh 4138,0 + đệm 3 tick", $"{c.Entry} {c.Sl}");
            Check(Near(c.RAvail, 47.0 / 27) && c.RAvail >= 1.7 && c.RAvail < 1.8, "R sẵn ≈ 1,74 ⇒ vào", c.RAvail.ToString());
            Check(Near(c.Tp, 41356 - 2 * 27), "TP 2R");
            var s = ToSig(c);
            BenzoCore.Simulate(s, bars, 18);
            Check(s.Outcome == "SL" && s.ExitTime == bars[19].Time && s.R < -1, "mô phỏng: giá vọt 4142 ⇒ chạm SL ở nến 19", s.Outcome);
        }
        Console.WriteLine("[C2] Ví dụ 2 — thế B sell, mốc stacked trong cú phá");
        {
            var (f, bars) = World(Ex2Rows());
            var c = Eval(Ex2Cand(), f);
            Check(Types(c) == "delta,bong", "2 dấu hiệu: Δ ngược giá + bóng đỏ", Types(c));
            Check(c.Signs[0].Desc.Contains("ΣΔ -62/2 nến"), "ΣΔ −62 / 2 nến hồi", c.Signs[0].Desc);
            Check(c.Gates.Count == 0, "qua mọi cổng", string.Join(";", c.Gates));
            Check(c.Sl == 41291 && c.Entry == 41266, "SL 4129,1 = mép xa vùng 4128,8 + 3 tick", $"{c.Entry} {c.Sl}");
            Check(Near(c.RAvail, (41266 - (E2 - 51)) / 25.0) && c.RAvail >= 1.7, "R sẵn tới E − chiều cao range", c.RAvail.ToString());
            Check(c.MocUsed == "stacked 4128,6–4128,8", "mốc dùng = vùng stacked", c.MocUsed);
            var s = ToSig(c);
            BenzoCore.Simulate(s, bars, 15);
            Check(s.Outcome == "TP" && s.R > 1.9, "mô phỏng chạm TP", s.Outcome);
        }
        Console.WriteLine("[C3] Ví dụ 3 — trap + kiệt sức đáy nhưng R tới cạnh trên 1,3 ⇒ bị loại (A2 \"lần 2\" KHÔNG port)");
        {
            var (f, _) = Ex3World();
            var first = Eval(Ex3Cand(17, 41222, 16), f);
            Check(first.NTypes == 1, "lần 1 chỉ 1 dấu hiệu ⇒ không", Types(first));
            var c = Eval(Ex3Cand(18), f);
            Check(c.Has("trap") && c.Has("kiet_suc"), "lần 2: trap + kiệt sức", Types(c));
            Check(c.Sl == 41206 - 3 && c.Entry == 41229, "SL sau râu x + 3 tick");
            Check(Near(c.RAvail, 34.0 / 26), "R tới cạnh trên ≈ 1,3", c.RAvail.ToString());
            Check(c.Gates.SequenceEqual(new[] { "r_nho" }), "⇒ bị loại vì R < 1,7 (ngoại lệ mục tiêu không code)", string.Join(";", c.Gates));
        }
        Console.WriteLine("[C4] Cách đếm dấu hiệu");
        {
            var (f, _) = World(Ex2Rows(cfZone: true));
            Check(Eval(Ex2Cand(), f).Has("stacked"), "vùng sell MỚI giữa thân CF đóng dưới Lo ⇒ đếm");
            Check(!Eval(Ex2Cand(new List<CorvenMoc> { Zone(15, 41270, 41272) }), f).Has("stacked"), "cùng vùng đó đang làm mốc ⇒ KHÔNG đếm");
            var (f3, _) = Ex3World();
            var c3 = Eval(Ex3Cand(18), f3);
            Check(c3.Signs.First(s => s.Type == "trap").Bar == 18 && c3.Signs.First(s => s.Type == "kiet_suc").Bar == 18 && c3.NTypes >= 2, "trap + kiệt sức cùng nến = 2");
            var (f1, _) = World(Ex1Rows(cfDelta: -45));
            var c1 = Eval(Ex1Cand(), f1);
            var dv = Of.DeltaDivergence(f1.H, f1.L, f1.Dl, 17, -1, 15);
            Check(c1.Signs[0].Desc.StartsWith("Δ to") && dv.ok && Types(c1) == "delta,bong", "Δ to + Δ ngược giá cùng có ⇒ chỉ tính 1 loại Δ", Types(c1));
        }
        Console.WriteLine("[C5] ⛔ kiệt sức chống hướng: veto tới khi bị râu quét");
        {
            Action<List<Row>> Exh(long low16, long? low17)
            {
                return rows =>
                {
                    var r = rows[16];
                    rows[16] = R_(r.o, r.h, low16, r.c, r.d, SetLv(Uni(low16, r.h), low16, bid: 0, ask: 3));
                    if (low17.HasValue) { var q = rows[17]; rows[17] = R_(q.o, q.h, low17.Value, q.c, q.d, SetLv(Uni(low17.Value, q.h), 41375, bid: 30)); }
                };
            }
            var (f, _) = World(Ex1Rows(extra: Exh(41340, null)));
            Check(f.ExhBot[16].Hit && Eval(Ex1Cand(), f).Gates.Contains("v_kiet_suc_chong"), "đáy 4134,0 kiệt sức sell, chưa bị quét ⇒ veto");
            var (g, _) = World(Ex1Rows(extra: Exh(41346, 41345)));
            Check(g.ExhBot[16].Hit && !Eval(Ex1Cand(), g).Gates.Contains("v_kiet_suc_chong"), "nến 17 râu quét qua đáy ⇒ hết veto");
        }
        Console.WriteLine("[C6] R sẵn 1,69 bỏ · 1,70 vào · TP luôn 2R");
        {
            var (f, _) = GeoWorld(41377);
            var c = Eval(GeoCand(41356 - 40), f);
            Check(c.Risk == 24 && c.Gates.Contains("r_nho"), "40/24 = 1,667 < 1,7 ⇒ bỏ", string.Join(";", c.Gates));
            c = Eval(GeoCand(41356 - 41), f);
            Check(!c.Gates.Contains("r_nho") && Near(c.Tp, 41356 - 48), "41/24 = 1,708 ⇒ vào, TP 2R dù R sẵn < 2");
            var (g, _) = GeoWorld(41373);
            c = Eval(GeoCand(41356 - 34), g);
            Check(c.Risk == 20 && Near(c.RAvail, 1.7, 1e-12) && !c.Gates.Contains("r_nho"), "biên đúng 1,70 ⇒ vào");
        }
        Console.WriteLine("[C7] SL: sàn 1 mbr, trần 4 mbr, đệm max(3 tick, 0,2 mbr), làm tròn tick ra xa");
        {
            var (f, _) = GeoWorld(41364, mbr: 15.5);
            var c = Eval(GeoCand(41200), f);
            Check(c.Sl == 41372 && c.Risk == 16, "rủi ro 11,1 < 15,5 ⇒ dời ra rồi làm tròn lên 16", $"{c.Sl} {c.Risk}");
            (f, _) = GeoWorld(41380, mbr: 20);
            c = Eval(GeoCand(41200), f);
            Check(c.Sl == 41384 && c.Risk == 28, "đệm = max(3, 0,2 × 20) = 4", $"{c.Sl} {c.Risk}");
            (f, _) = GeoWorld(41430, mbr: 15);
            Check(Eval(GeoCand(41000), f).Gates.Contains("tran_sl"), "rủi ro 77 > 60 ⇒ trần SL");
            (f, _) = GeoWorld(41410, mbr: 15);
            Check(!Eval(GeoCand(41000), f).Gates.Contains("tran_sl"), "rủi ro 57 ≤ 60 ⇒ giữ");
        }
        Console.WriteLine("[C7b] Nến xác nhận 4a: thân, đóng sát cực trị, Δ, biên độ");
        {
            var bad = new (Func<Row, Row> mod, string why)[]
            {
                (r => R_(41362, 41364, 41354, 41360, -15), "thân 0,2 < 0,4"),
                (r => R_(41363, 41364, 41350, 41358, -15), "đóng cách đáy 0,57 > 0,3"),
                (r => R_(41362, 41364, 41354, 41356, 5), "Δ ngược dấu"),
                (r => R_(41362, 41364, 41354, 41356, -9), "Δ < 0,5 medΔ"),
                (r => R_(41359, 41359, 41354, 41355, -15), "biên độ 5 < 0,5 mbr"),
            };
            foreach (var (mod, why) in bad)
            {
                var rows = Ex1Rows(); rows[18] = mod(rows[18]);
                var (f, _) = World(rows);
                Check(Eval(Ex1Cand(), f).Gates.Contains("g4a_cf"), "CF hỏng: " + why);
            }
        }
        Console.WriteLine("[C8] Máy ①②: ReEntry huỷ thế B · CloseThrough huỷ mốc stacked · tuổi 31 nến hết");
        {
            var bars = BaseBars();
            var (rf, bc) = BreakUp(bars);
            int re = Add(bars, TT + 55, TT + 56, TT - 10, TT - 5);         // đóng lại TRONG range = ReEntry
            int after = Add(bars, TT - 5, TT + 14, TT - 6, TT + 10);       // chạm cạnh, đóng gần — sẽ là ứng viên nếu thế còn sống
            var (m, cs) = RunM(bars);
            Check(m.Eng.Ranges.Count > 0 && Near(m.Eng.Ranges[m.Eng.Ranges.Count - 1].Top, TT) && Near(m.Eng.Ranges[m.Eng.Ranges.Count - 1].Bottom, BB), "range hộp đều sinh đúng 4100,0–4104,9");
            Check(!cs.Any(c => c.The == 'B' && c.InstFb == bc && c.Cf >= re), "sau ReEntry không còn ứng viên của thế B đó");

            bars = BaseBars(); (rf, bc) = BreakUp(bars);
            long p = TT + 55;
            while (bars.Count - 1 - rf < 30) { p += 3; Add(bars, p, p + 12, p - 8, p + 5); }
            int lastOk = bars.Count - 1;
            int late = Add(bars, p, p + 2, TT + 5, TT + 14);              // tuổi 31: chạm cạnh nhưng thế đã hết
            (m, cs) = RunM(bars);
            Check(lastOk - rf == 30 && !HasB(cs, bc, late), "tuổi 31 nến: chạm cạnh nhưng thế B đã hết");

            bars = BaseBars();
            rf = Add(bars, TT - 8, TT + 12, TT - 10, TT + 8);
            int z = Add(bars, TT + 8, TT + 40, TT + 6, TT + 38, PushLevels(TT + 6, TT + 40, TT + 20));
            Add(bars, TT + 38, TT + 60, TT + 36, TT + 58);
            bc = Add(bars, TT + 58, TT + 75, TT + 55, TT + 70);
            Add(bars, TT + 70, TT + 72, TT + 45, TT + 50);
            int t = Add(bars, TT + 50, TT + 52, TT + 28, TT + 33);         // râu chạm vùng ± tol lần đầu ⇒ mốc stacked hợp lệ
            int ct = Add(bars, TT + 33, TT + 35, TT + 15, TT + 17);        // đóng dưới mép dưới vùng ⇒ CloseThrough
            int af = Add(bars, TT + 17, TT + 26, TT + 16, TT + 24);
            (m, cs) = RunM(bars);
            Check(HasB(cs, bc, t, "stacked", z), "vùng stacked trong cú đẩy làm mốc khi test lần đầu");
            Check(!HasB(cs, bc, ct, "stacked", z) && !HasB(cs, bc, af, "stacked", z), "đóng xuyên mép xa ⇒ vùng hết làm mốc");

            bars = BaseBars();
            rf = Add(bars, TT - 8, TT + 12, TT - 10, TT + 8);
            z = Add(bars, TT + 8, TT + 40, TT + 6, TT + 38, PushLevels(TT + 6, TT + 40, TT + 20));
            Add(bars, TT + 38, TT + 39, TT + 21, TT + 30);                 // chạm ĐÚNG vùng ngay
            bc = Add(bars, TT + 30, TT + 60, TT + 30, TT + 58);
            Add(bars, TT + 58, TT + 75, TT + 55, TT + 70); Add(bars, TT + 70, TT + 85, TT + 66, TT + 80); Add(bars, TT + 80, TT + 82, TT + 60, TT + 65);
            t = Add(bars, TT + 65, TT + 66, TT + 30, TT + 36);
            (m, cs) = RunM(bars);
            Check(!HasB(cs, bc, t, "stacked", z), "vùng đã bị chạm trước nhịp test ⇒ vứt (CORVEN 0:20:12)");
        }
        Console.WriteLine("[C9] Cửa sổ test W = 3: chạm ở nến thứ 4 trước CF không tính");
        {
            var bars = BaseBars();
            var (rf, bc) = BreakUp(bars);
            int k = Add(bars, TT + 55, TT + 56, TT + 8, TT + 20);
            int a1 = Add(bars, TT + 20, TT + 30, TT + 14, TT + 22);
            int a2 = Add(bars, TT + 22, TT + 30, TT + 15, TT + 21);
            int a3 = Add(bars, TT + 21, TT + 30, TT + 16, TT + 20);
            var (_, cs) = RunM(bars);
            Check(HasB(cs, bc, k) && HasB(cs, bc, a1) && HasB(cs, bc, a2) && !HasB(cs, bc, a3), "W=3: k, k+1, k+2 qua; k+3 không");
            var (_, cs4) = RunM(bars, new CorvenCfg { WinB = 4 });
            Check(HasB(cs4, bc, a3), "W=4 thì k+3 qua (đối chứng)");
            // dấu hiệu: bóng ở nến 13 (thứ 3 trước CF 15 với w0 = 13) được tính; dời w0 = 14 ⇒ không còn bóng
            var (f, _) = World(Ex2Rows());
            var c = Ex2Cand(); c.W0 = 15; Eval(c, f);
            Check(!c.Has("bong"), "bóng ở nến 14 nằm ngoài cửa sổ [15, 15] ⇒ không tính");
        }
        Console.WriteLine("[C10] Chặn 19:20–20:30 VN (công tắc) · 15 nến đầu phiên · TIME qua khoảng trống");
        {
            var (f, _) = World(Ex1Rows(), start: new DateTime(2026, 9, 1, 12, 7, 0, DateTimeKind.Utc));
            var c = Eval(Ex1Cand(), f);
            Check(f.Sm[18] >= 860 && f.Sm[18] < 930 && c.Gates.SequenceEqual(new[] { "chan_1920" }), "CF 19:25 VN ⇒ chỉ vướng chặn giờ", string.Join(";", c.Gates));
            var on = new DetectorCorven(); var off = new DetectorCorven { BlockUsOpen = false };
            Check(on.FirstGate(c, false) == "chặn giờ" && off.FirstGate(c, false) == null, "tắt công tắc ⇒ vào được");
            var times = Enumerable.Range(0, 5).Select(i => new DateTime(2026, 9, 1, 1, i, 0, DateTimeKind.Utc))
                        .Concat(Enumerable.Range(0, 16).Select(i => new DateTime(2026, 9, 1, 2, i, 0, DateTimeKind.Utc))).ToList();
            (f, _) = World(Ex1Rows(), times: times);
            Check(f.SStart[18] == 5 && Eval(Ex1Cand(), f).Gates.Contains("dau_phien"), "nến 18 là nến thứ 14 của phiên ⇒ chặn 15 nến đầu");
            Check(on.FirstGate(Eval(Ex1Cand(), World(Ex1Rows()).f), true) == "tin USD", "tin USD (lệch có chủ đích, chỉ C#) chặn");
            // TIME: lệnh ví dụ 1 không chạm gì tới hết phiên ⇒ đóng TIME tại giá đóng nến cuối (nến 21)
            var rows = Ex1Rows();
            rows[19] = R_(41356, 41358, 41350, 41352); rows[20] = R_(41352, 41354, 41348, 41349);
            for (int i = 0; i < 5; i++) rows.Add(R_(41349, 41351, 41345, 41347));
            var tt = Enumerable.Range(0, 22).Select(i => W0.AddMinutes(i)).Concat(Enumerable.Range(0, rows.Count - 22).Select(i => W0.AddMinutes(60 + i))).ToList();
            var (f2, bars2) = World(rows, times: tt);
            var c2 = Eval(Ex1Cand(), f2);
            var det = new CountDet { F = i => i == 18 ? new Signal { Setup = 'A', Side = c2.S, Entry = c2.Entry * 0.1, Sl = c2.Sl * 0.1, Tp = c2.Tp * 0.1 } : null };
            var eng = new BenzoEngine("GCZ26", 0.1, null, new[] { det });
            eng.Bars.AddRange(bars2);
            eng.Advance(bars2.Count - 1);
            var s = eng.Signals[0];
            Check(s.Outcome == "TIME" && s.ExitTime == bars2[21].Time && Near(bars2[21].C, 4134.7, 1e-9), "TIME ở nến 21 (cuối phiên), giá 4134,7", s.Outcome);
        }

        string root = RepoRoot();
        string prefix = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
        if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Check(false, "không thấy file 90d để chạy ca 11/12 + cache", prefix ?? "(không có data-export)"); return; }
        const int Cut = 51318, Deny = 3697;    // nến cuối TRAIN (2026-09-15) · 4 phiên mỏng đầu file (Python `good`)
        var (tb, tl) = CorvenData.Load(prefix, Cut);

        Console.WriteLine("[C12] Hồi quy TRAIN trên file 90d (corven-4): 374 lệnh = Python cp_live (thế A 38, thế B 336)");
        var (engT, _) = CorvenData.Run(tb, tl, 0.1, Deny);
        var sg = engT.Signals;
        Check(sg.Count == 374, "374 lệnh TRAIN", sg.Count.ToString());
        Check(sg.Count(x => x.Setup == 'A') == 38 && sg.Count(x => x.Setup == 'B') == 336, "thế A 38 · thế B 336", $"{sg.Count(x => x.Setup == 'A')}/{sg.Count(x => x.Setup == 'B')}");
        Check(sg.Count(x => x.Outcome == "TP") == 130 && sg.Count(x => x.Outcome == "SL") == 241, "130 TP · 241 SL · 3 TIME (= Python cp_live)", $"{sg.Count(x => x.Outcome == "TP")}/{sg.Count(x => x.Outcome == "SL")}");
        Check(sg[0].BarIdx == 4050 && sg[0].Signs == "kiệt sức: kiệt sức đỉnh (Ask 0) @4084,2 (nến 4048) | stacked: stacked sell 3 mức 4083,2–4083,4 (nến 4050)", "lệnh đầu: nến 4050, chuỗi dấu hiệu đúng định dạng Python", sg[0].Signs);

        Console.WriteLine("[C11] Chạy một mạch = chạy từng nến · giá ×10 (bước giá ×10) ra cùng tín hiệu");
        {
            int n = 20000;
            var b = tb.Take(n).ToList(); var l = tl.Take(n).ToArray();
            var (e1, _) = CorvenData.Run(b, l, 0.1, Deny);
            var (e2, _) = CorvenData.Run(b, l, 0.1, Deny, oneShot: true);
            Check(e1.Signals.Count > 5 && e1.Signals.Select(x => (x.Id, x.Entry, x.Outcome, x.Signs)).SequenceEqual(e2.Signals.Select(x => (x.Id, x.Entry, x.Outcome, x.Signs))),
                  "Advance từng nến = Advance một lần", $"{e1.Signals.Count}/{e2.Signals.Count}");
            var b10 = b.Select(x => new BarData { Idx = x.Idx, Time = x.Time, O = x.O * 10, H = x.H * 10, L = x.L * 10, C = x.C * 10, Delta = x.Delta, Vol = x.Vol }).ToList();
            var l10 = l.Select(x => x.Select(y => new LevelVol(y.Price * 10, y.Bid, y.Ask, y.Vol)).ToList()).ToArray();
            var (e10, _) = CorvenData.Run(b10, l10, 1.0, Deny);
            Check(e10.Signals.Select(x => (x.BarIdx, x.Setup, x.Side, x.SignTypes, Math.Round(x.Entry, 3), x.ExitTime)).SequenceEqual(
                  e1.Signals.Select(x => (x.BarIdx, x.Setup, x.Side, x.SignTypes, Math.Round(x.Entry * 10, 3), x.ExitTime))), "giá ×10 + tick ×10 ⇒ cùng nến, thế, hướng, dấu hiệu, giá vào ×10, nến thoát",
                  $"{e10.Signals.Count}/{e1.Signals.Count}");
        }

        Console.WriteLine("[C13] Cache (plan 10.5): lịch sử ngắn hơn không sinh tín hiệu lạ · sửa H một dòng ⇒ bỏ cache");
        {
            string cp = Tmp("cache_GCZ26_Time_1m.jsonl");
            var cache = new SignalCache(cp, BenzoCore.CacheVersion(true)); cache.Load();
            var (e1, _) = CorvenData.Run(tb, tl, 0.1, Deny, cache: cache);
            int from = 20000;
            var b2 = tb.Skip(from).Select((x, i) => new BarData { Idx = i, Time = x.Time, O = x.O, H = x.H, L = x.L, C = x.C, Delta = x.Delta, Vol = x.Vol }).ToList();
            var l2 = tl.Skip(from).ToArray();
            var c2 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c2.Load();
            var (e2, _) = CorvenData.Run(b2, l2, 0.1, 0, cache: c2);
            var set1 = e1.Signals.Where(x => x.Time >= b2[0].Time).Select(x => (x.Time, x.Side, x.Entry, x.Sl)).ToList();
            var set2 = e2.Signals.Select(x => (x.Time, x.Side, x.Entry, x.Sl)).ToList();
            Check(set2.Count > 10 && set2.All(x => e1.Signals.Any(y => (y.Time, y.Side, y.Entry, y.Sl) == x)), "lịch sử ngắn hơn: không có tín hiệu lạ", $"{set2.Count}");
            Check(set2.SequenceEqual(set1.Where(x => set2.Count == 0 || x.Time >= set2[0].Time)), "tập tín hiệu chung trùng khớp", $"{set1.Count}/{set2.Count}");
            // sửa tay H của 1 dòng sig ⇒ nạp lại phải bỏ cache
            var lines = File.ReadAllLines(cp).ToList();
            int idx = lines.FindIndex(x => x.Contains("\"K\":\"sig\""));
            var node = JsonNode.Parse(lines[idx]);
            node["S"]["CfH"] = node["S"]["CfH"].GetValue<double>() + 1.0;
            lines[idx] = node.ToJsonString();
            File.WriteAllLines(cp, lines);
            var c3 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c3.Load();
            var det = new DetectorCorven { AllowBar = i => i >= Deny };
            var eng = new BenzoEngine("GCZ26", 0.1, c3, new ISetupDetector[] { det }) { GetLevels = i => tl[i] };
            eng.Bars.AddRange(tb);
            var res = eng.Advance(tb.Count - 1);
            Check(res.CacheInvalid && res.CacheWhy.Contains("cache lệch nến"), "guard khớp nến bắt dòng bị sửa ⇒ engine dừng, báo bỏ cache", res.CacheWhy);
            c3.Reset();
            Check(!File.Exists(cp) && c3.Count == 0, "Reset xoá file cache (dò lại từ đầu)");
        }
    }
}
