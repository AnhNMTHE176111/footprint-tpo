// Test cho ngưỡng TỰ THÍCH NGHI (2026-11-24, research/adaptive_2026-11-24/README.md mục 6.1 — cùng ví dụ đã chạy đạt trong bt_selftest.py,
// dot_selftest.py, exh_selftest.py): cửa sổ nền theo khung, Big Trade "lớn thứ K trong N nến trước", chấm công thức chung, kiệt sức thêm điều kiện đuôi.
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class AdaptiveTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    static string Fmt(IEnumerable<(long tick, double mot)> xs) => string.Join(" ", xs.Select(x => $"({x.tick},{x.mot})"));

    static List<(long tick, double mot)> Sel(List<(long tick, double mot)> cells, double thr, int g, int cap)
        => BigTradeAdaptive.Select(cells, thr, g, cap).Select(i => cells[i]).ToList();

    static List<(long, double)> C(params (long, double)[] x) => x.ToList();

    // chuỗi 8 nến của README 6.1 (N = 5, mật độ 0,6 -> K = 3)
    static readonly List<(long, double)>[] Seq =
    {
        C((100, 1), (101, 6), (102, 2)),
        C((100, 3), (104, 8)),
        C((99, 12), (100, 1)),
        C((101, 2), (102, 4)),
        C((100, 7), (103, 5), (110, 1)),
        C((100, 7), (101, 9), (102, 7), (105, 6), (108, 15), (109, 7)),
        C((100, 0), (101, 0)),
        C((100, 9), (103, 9), (106, 9), (109, 30)),
    };

    static List<(double thr, int g, string kept)> RunSeq(double floor, double ceil, double div)
    {
        var a = new BigTradeAdaptive(5, 0.6);
        var res = new List<(double, int, string)>();
        foreach (var cells in Seq)
        {
            double thr = a.Threshold(10, floor, ceil);
            int g = a.MergeTicks(div, 2);
            res.Add((thr, g, Fmt(Sel(cells, thr, g, 3))));
            a.AddClosedBar(cells);
        }
        return res;
    }

    static List<CellMark> Ev(CellBigSettings s, double B, params (long t, double bid, double ask)[] xs)
        => CellBigLogic.Evaluate(xs.Select(x => new CellLevel(x.t, x.ask, x.bid, x.ask + x.bid, 1)).ToList(), true, B, s);
    static string Ticks(List<CellMark> m, int side) => string.Join(",", m.Where(x => x.Side == side).Select(x => x.Tick).OrderBy(x => x));

    public static int Run()
    {
        Console.WriteLine("[Adaptive] cua so nen theo khung: min(20, max(5, lam tron(120 / phut)))");
        var mins = new double[] { 1, 2, 5, 10, 15, 20, 30, 60, 240, 0 };
        var exp = new[] { 20, 20, 20, 12, 8, 6, 5, 5, 5, 20 };
        var got = mins.Select(m => BaselineWindow.BarsFor(m)).ToArray();
        Check(got.SequenceEqual(exp), "M1 M2 M5 M10 M15 M20 M30 H1 H4 / khong ro", string.Join(",", got));
        Check(BaselineWindow.RoundHalfUp(4.5) == 5 && BaselineWindow.RoundHalfUp(2.5) == 3 && BaselineWindow.RoundHalfUp(3.49) == 3, "lam tron nua len (khong ve so chan)");

        Console.WriteLine("[Adaptive] Big Trade: lon thu K, gop, gioi han");
        Check(BigTradeAdaptive.KthLargest(new[] { new double[] { 12, 7, 3 }, new double[] { 9, 2 }, new double[] { 30 } }, 3) == 9, "lon thu 3 cua [[12,7,3],[9,2],[30]] = 9");
        Check(BigTradeAdaptive.KthLargest(new[] { new double[] { 12 }, new double[] { 9 } }, 3) == 0, "chua du 3 gia tri -> 0");
        var cs = C((100, 20), (101, 30), (110, 20), (104, 25));
        Check(Fmt(Sel(cs, 1, 2, 3)) == "(101,30) (104,25) (110,20)", "g 2, toi da 3", Fmt(Sel(cs, 1, 2, 3)));
        Check(Fmt(Sel(cs, 1, 2, 2)) == "(101,30) (104,25)", "g 2, toi da 2", Fmt(Sel(cs, 1, 2, 2)));
        Check(Fmt(Sel(cs, 1, 0, 0)) == "(101,30) (104,25) (100,20) (110,20)", "khong gop, khong gioi han", Fmt(Sel(cs, 1, 0, 0)));
        var cs2 = C((100, 20), (101, 30), (110, 20), (103, 25));
        Check(Fmt(Sel(cs2, 1, 2, 3)) == "(101,30) (110,20)", "103 cach 101 hai tick -> gop", Fmt(Sel(cs2, 1, 2, 3)));
        var cs3 = C((105, 9), (100, 9), (103, 9));
        Check(Fmt(Sel(cs3, 1, 2, 3)) == "(100,9) (103,9)", "bang nhau: tick thap truoc", Fmt(Sel(cs3, 1, 2, 3)));
        Check(Sel(C((100, 0), (101, 0)), 0, 0, 0).Count == 0, "lenh don 0 khong bao gio no (ke ca nguong 0)");
        Check(Fmt(Sel(C((100, 9), (101, 10)), 10, 0, 0)) == "(101,10)", "dung nguong: 10 >= 10 no, 9 khong");

        Console.WriteLine("[Adaptive] Big Trade: khoang gop theo bien do TB");
        foreach (var (rng, div, want) in new[] { (3.6, 8.0, 2), (183.0, 8.0, 23), (20.0, 8.0, 3), (0.0, 8.0, 2), (183.0, 0.0, 2) })
        {
            var a = new BigTradeAdaptive(5, 1);
            // 5 nen co bien do TB = rng: 4 nen bien do 0 + ... -> dung 5 nen cung bien do (lam tron xuong tick khong duoc) -> dung tong bang 5 x rng
            var rs = new double[] { rng, rng, rng, rng, rng };
            foreach (var r in rs) a.AddClosedBar(new List<(long, double)> { (0, 1), ((long)Math.Round(r), 1) });
            if (Math.Abs(rng - Math.Round(rng)) > 1e-9)
            {   // 3,6 = TB của 2,4,1,1,10 (chuỗi README)
                a = new BigTradeAdaptive(5, 1);
                foreach (var r in new long[] { 2, 4, 1, 1, 10 }) a.AddClosedBar(new List<(long, double)> { (0, 1), (r, 1) });
            }
            int gg = a.MergeTicks(div, 2);
            Check(gg == want, $"bien do {rng}, chia {div} -> {want}", gg.ToString());
        }
        Check(new BigTradeAdaptive(5, 1).MergeTicks(8, 2) == 2, "chua du 5 nen -> gop toi thieu");

        Console.WriteLine("[Adaptive] Big Trade: chuoi 8 nen (N 5, mat do 0,6 -> K 3, san 5, co dinh 10, toi da 3, chia 8)");
        var r0 = RunSeq(5, 0, 8);
        var wantThr = new double[] { 10, 10, 10, 10, 10, 7, 9, 9 };
        var wantKept = new[] { "", "", "(99,12)", "", "", "(108,15) (101,9)", "", "(109,30) (100,9) (103,9)" };
        for (int i = 0; i < 8; i++)
            Check(r0[i].thr == wantThr[i] && r0[i].kept == wantKept[i], $"nen {i}: nguong {wantThr[i]}, giu [{wantKept[i]}]", $"{r0[i].thr} [{r0[i].kept}] g={r0[i].g}");
        var a7 = new BigTradeAdaptive(5, 0.6);
        foreach (var c in Seq) a7.AddClosedBar(c);
        Check(a7.Count == 5, "nen 6 (khong co so lieu) khong vao hang doi; hang doi cuon 5", a7.Count.ToString());
        var r1 = RunSeq(5, 0, 2);
        Check(r1[7].g == 3 && r1[7].kept == "(109,30) (100,9)", "chia 2: nen 7 g = 3", $"g={r1[7].g} [{r1[7].kept}]");
        Check(RunSeq(8, 0, 8)[5].thr == 8, "san 8: nguong nen 5 = 8");
        Check(RunSeq(5, 6, 8)[5].thr == 6, "tran 6: nguong nen 5 = 6");
        Check(new BigTradeAdaptive(20, 1.0).K == 20 && new BigTradeAdaptive(8, 1.0).K == 8 && new BigTradeAdaptive(5, 0.5).K == 3 && new BigTradeAdaptive(5, 0.01).K == 1, "K = max(1, lam tron(mat do x N))");

        Console.WriteLine("[Adaptive] cham: cong thuc chung (nguong, w, che)");
        (double thr, int w, int h) U(int preset, double B, double R)
        {
            var s = new CellBigSettings(); UnifiedDots.Apply(s, preset, R, false, true);
            return (Math.Max(s.DotMedianRatio * B, s.MinSide), s.DotLocalTicks, s.DotHideBuyNearSellTicks);
        }
        bool Eq((double thr, int w, int h) a, double thr, int w, int h) => Math.Abs(a.thr - thr) < 1e-9 && a.w == w && a.h == h;
        Check(Eq(U(2, 8, 39), 22.4, 7, 6), "it nhieu (8; 39) -> 22,4 / 7 / 6", U(2, 8, 39).ToString());
        Check(Eq(U(2, 3, 16), 9, 4, 6), "it nhieu (3; 16) -> 9 / 4 / 6", U(2, 3, 16).ToString());
        Check(Eq(U(2, 16.2, 183), 45.36, 31, 23), "it nhieu (16,2; 183) -> 45,36 / 31 / 23", U(2, 16.2, 183).ToString());
        Check(Eq(U(2, 10, 0), 28, 4, 6), "it nhieu (10; chua co bien do) -> 28 / 4 / 6", U(2, 10, 0).ToString());
        Check(Eq(U(0, 8, 39), 16, 7, 2), "khong sot (8; 39) -> 16 / 7 / 2", U(0, 8, 39).ToString());
        Check(Eq(U(0, 2, 16), 5, 4, 2), "khong sot (2; 16) -> 5 / 4 / 2", U(0, 2, 16).ToString());
        Check(Eq(U(1, 8, 39), 19.2, 7, 2), "trung gian (8; 39) -> 19,2 / 7 / 2", U(1, 8, 39).ToString());
        Check(UnifiedDots.Window(27) == 5 && UnifiedDots.Window(21) == 4, "R 27 -> w 5 (4,5 len 5); R 21 -> 4");
        var sAll = new CellBigSettings(); UnifiedDots.Apply(sAll, 0, 183, true, false);
        Check(sAll.DotLocalTicks == 0 && sAll.MinSide == 0, "che do no moi muc gia giu w = 0; tat san -> san 0");

        Console.WriteLine("[Adaptive] cham: mot nen (nguong 22,4)");
        var one = new (long t, double bid, double ask)[] { (100, 5, 30), (101, 2, 3), (104, 25, 1), (108, 40, 26), (112, 3, 24), (120, 1, 23) };
        CellBigSettings W(int w, int h) => new CellBigSettings { DotMedianRatio = 2.8, MinSide = 9, DotLocalTicks = w, DotHideBuyNearSellTicks = h };
        var e1 = Ev(W(7, 6), 8, one); Check(Ticks(e1, 1) == "100,120" && Ticks(e1, -1) == "108", "w 7, che 6 -> xanh {100,120}, do {108}", $"{Ticks(e1, 1)} / {Ticks(e1, -1)}");
        var e2 = Ev(W(7, 8), 8, one); Check(Ticks(e2, 1) == "120" && Ticks(e2, -1) == "108", "w 7, che 8 -> xanh {120}, do {108}", $"{Ticks(e2, 1)} / {Ticks(e2, -1)}");
        var e3 = Ev(W(3, 6), 8, one); Check(Ticks(e3, 1) == "120" && Ticks(e3, -1) == "104,108", "w 3, che 6 -> xanh {120}, do {104,108}", $"{Ticks(e3, 1)} / {Ticks(e3, -1)}");
        Check(Ev(W(4, 2), 1, (100, 30, 0), (102, 30, 0)).Count == 0, "bang nhau khong tinh la lon hon han -> khong cham");

        Console.WriteLine("[Adaptive] cham: chuoi 5 nen nen (B 4, R 12) roi nen xet");
        var bl = new CellBigBaseline(20, 8);
        var baseBar = Enumerable.Range(100, 13).Select(t => new CellLevel(t, 2, 2, 4, 1)).ToList();
        for (int i = 0; i < 5; i++)
        {
            CellBigLogic.BarStats(baseBar, out double mn, out double md);
            bl.Add(mn, md, CellBigLogic.BarRangeTicks(baseBar));
        }
        bl.TryGetMedian(out double B4); bl.TryGetRange(out double R12);
        Check(B4 == 4 && R12 == 12, "B 4, R 12", $"{B4}, {R12}");
        var test = new (long t, double bid, double ask)[] { (100, 12, 1), (103, 11, 0), (105, 2, 15), (112, 0, 20) };
        var sq = new CellBigSettings(); UnifiedDots.Apply(sq, 2, R12, false, true);
        var eq = Ev(sq, B4, test);
        Check(Ticks(eq, 1) == "112" && Ticks(eq, -1) == "100" && Math.Abs(eq[0].Threshold - 11.2) < 1e-9, "it nhieu: nguong 11,2 / w 4 / che 6 -> xanh {112}, do {100}", $"{Ticks(eq, 1)} / {Ticks(eq, -1)} nguong {eq[0].Threshold}");
        var sn = new CellBigSettings(); UnifiedDots.Apply(sn, 0, R12, false, true);
        var en = Ev(sn, B4, test);
        Check(Ticks(en, 1) == "105,112" && Ticks(en, -1) == "100" && en[0].Threshold == 8, "khong sot: nguong 8 / w 4 / che 2 -> xanh {105,112}, do {100}", $"{Ticks(en, 1)} / {Ticks(en, -1)}");
        Check(CellBigLogic.Evaluate(test.Select(x => new CellLevel(x.t, x.ask, x.bid, x.ask + x.bid, 1)).ToList(), false, 0, sn).Count == 0, "chua co nen -> khong cham");

        Console.WriteLine("[Adaptive] nen: TB moi o giu 20 nen, trung vi + bien do N nen");
        var b2 = new CellBigBaseline(20, 5);
        for (int i = 0; i < 20; i++) b2.Add(10, 100, 50);
        for (int i = 0; i < 5; i++) b2.Add(10, 1, 5);
        b2.TryGet(out double m20); b2.TryGetMedian(out double md5); b2.TryGetRange(out double r5);
        Check(m20 == 10 && md5 == 1 && r5 == 5 && b2.Count == 20, "TB 20 nen; trung vi/bien do chi 5 nen gan nhat", $"{m20} {md5} {r5} {b2.Count}");

        Console.WriteLine("[Adaptive] kiet suc: tong duoi + nen duoi");
        var cells = new List<ExhLevel> { new(100, 4, 0), new(101, 3, 1), new(102, 0, 2), new(103, 5, 6), new(104, 2, 9), new(105, 1, 3), new(110, 7, 2), new(111, 0, 1) };
        Check(ExhaustionLogic.TailSum(true, 111, cells, 6) == 3 && ExhaustionLogic.TailSum(false, 100, cells, 6) == 15, "duoi dinh tai 111 = 3; duoi day tai 100 = 15");
        var tb = new ExhTailBaseline(20);
        tb.Add(3, 15); tb.Add(1, 8); tb.Add(2, 2); tb.Add(9, 4);
        Check(!tb.TryGetMedian(out _), "4 nen -> chua co nen duoi");
        tb.Add(6, 7);
        Check(tb.TryGetMedian(out double tm) && tm == 5, "trung vi 10 gia tri (1 2 2 3 4 6 7 8 9 15) = 5", tm.ToString());
        var tb2 = new ExhTailBaseline(2); tb2.Add(100, 100); for (int i = 0; i < 5; i++) tb2.Add(1, 3);
        Check(tb2.Count == 2, "nen duoi cuon N nen");

        // chuỗi: 5 nến nền rồi nến xét — như luồng indicator (Detect với nền TRƯỚC, rồi nộp nến)
        (bool top, bool bot) Exh(List<(long o, long h, long l, long c, List<ExhLevel> lv)> bars, double ratio)
        {
            var mean = new CellBigBaseline(20, 20); var tail = new ExhTailBaseline(20);
            (bool, bool) last = (false, false);
            var s = new ExhSettings { TailMedianRatio = ratio };
            foreach (var b in bars)
            {
                bool hh = mean.TryGet(out double hm); bool ht = tail.TryGetMedian(out double tmed);
                last = (ExhaustionLogic.Detect(true, b.o, b.h, b.l, b.c, b.lv, s, hh, hm, ht, tmed).Hit,
                        ExhaustionLogic.Detect(false, b.o, b.h, b.l, b.c, b.lv, s, hh, hm, ht, tmed).Hit);
                double mn = b.lv.Average(x => x.Volume);
                mean.Add(mn, 0, 0);
                if (b.h > b.l) tail.Add(ExhaustionLogic.TailSum(true, b.h, b.lv, 6), ExhaustionLogic.TailSum(false, b.l, b.lv, 6));
            }
            return last;
        }
        var B0 = (o: 103L, h: 111L, l: 100L, c: 104L, lv: cells);
        var seq1 = Enumerable.Repeat(B0, 6).ToList();
        Check(Exh(seq1, 0.8) == (true, false), "nen y het: dinh CO dau (3 <= 6,325 va 3 <= 7,2), day khong (15 > 6,325)");
        var seq2 = Enumerable.Repeat(B0, 5).ToList(); seq2.Add((109, 111, 100, 108, cells));
        Check(Exh(seq2, 0.8) == (false, false), "mo 109 dong 108: rau dinh 2 tick -> khong dau");
        var thin = new List<ExhLevel> { new(100, 1, 0), new(101, 1, 0), new(106, 9, 9), new(107, 9, 9), new(112, 0, 1), new(113, 0, 1) };
        var seq3 = Enumerable.Repeat((o: 104L, h: 113L, l: 100L, c: 105L, lv: thin), 5).ToList(); seq3.Add(B0);
        Check(Exh(seq3, 0.8) == (false, false), "nen duoi rat mong (trung vi 2): 3 > 1,6 -> khong dau");
        Check(Exh(seq3, 0) == (true, false), "ti le duoi = 0 (tat) -> co dau nhu luat cu");

        Console.WriteLine(_fail == 0 ? "  -> thich nghi: tat ca PASS" : $"  -> thich nghi: {_fail} FAIL");
        return _fail;
    }
}
