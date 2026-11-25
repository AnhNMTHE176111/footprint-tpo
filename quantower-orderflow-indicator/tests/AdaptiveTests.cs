// Test cho ngưỡng TỰ THÍCH NGHI (2026-11-24, research/adaptive_2026-11-24/README.md mục 6.1 — cùng ví dụ đã chạy đạt trong bt_selftest.py,
// dot_selftest.py, exh_selftest.py): cửa sổ nền theo khung, hàm chọn vòng Big Trade, chấm công thức chung, kiệt sức thêm điều kiện đuôi.
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

        // 2026-11-25: trạng thái "lớn thứ K trong N nến" (mật độ / sàn / trần / tối đa vòng) đã thay bằng BigTradeWhale (BigTradeWhaleTests.cs); chỉ còn hàm chọn vòng.
        Console.WriteLine("[Adaptive] Big Trade: chon vong (gop, gioi han)");
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

        Console.WriteLine("[Adaptive] cham: cong thuc chung (nguong, w, che)");
        (double thr, int w, int h) U(int preset, double B, double R)
        {
            var s = new CellBigSettings(); UnifiedDots.Apply(s, preset, R, false, true, preset == 2 ? 9 : 5);   // sàn như bộ số trong README 6.1
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
        var sAll = new CellBigSettings(); UnifiedDots.Apply(sAll, 0, 183, true, false, 9);
        Check(sAll.DotLocalTicks == 0 && sAll.MinSide == 0, "che do no moi muc gia giu w = 0; tat san -> san 0");
        // LỖI người học 24/11: sàn 9 mà vẫn nổ "Sell - 6 Bid | ngưỡng 5.5" (bộ số ghi đè sàn thành 5)
        var sFl = new CellBigSettings(); UnifiedDots.Apply(sFl, 0, 40, true, true, 9);
        Check(sFl.MinSide == 9, "san lay tu o nguoi dung (9), bo so khong ghi de", sFl.MinSide.ToString());
        var eFl = CellBigLogic.Evaluate(new List<CellLevel> { new CellLevel(100, 1, 6, 7, 1) }, true, 2.75, sFl);
        Check(eFl.Count == 0, "6 Bid, nguong 2,0 x 2,75 = 5,5 nhung san 9 -> KHONG no");
        var eFl2 = CellBigLogic.Evaluate(new List<CellLevel> { new CellLevel(100, 1, 9, 10, 1) }, true, 2.75, sFl);
        Check(eFl2.Count == 1 && eFl2[0].Threshold == 9, "9 Bid -> no, nguong hien 9", eFl2.Count > 0 ? eFl2[0].Threshold.ToString() : "-");

        Console.WriteLine("[Adaptive] san tuyet doi (research/dot_floor_2026-11-24, floor_selftest.py)");
        (double thr, int w, int h) UF(int preset, double B, double R, double floor)
        {
            var s = new CellBigSettings(); UnifiedDots.Apply(s, preset, R, false, true, floor);
            return (Math.Max(s.DotMedianRatio * B, s.MinSide), s.DotLocalTicks, s.DotHideBuyNearSellTicks);
        }
        Check(Eq(UF(0, 2.75, 88, 7), 7, 15, 2) && Eq(UF(0, 2.75, 88, 9), 9, 15, 2) && Eq(UF(0, 2.75, 88, 5), 5.5, 15, 2), "B 2,75 R 88: san 7 -> 7/15/2, san 9 -> 9, san 5 -> 5,5");
        Check(Eq(UF(0, 3.5, 30, 7), 7, 5, 2) && Eq(UF(2, 3.0, 16, 7), 8.4, 4, 6), "(3,5; 30; san 7) -> 7/5/2; it nhieu (3; 16; san 7) -> 8,4/4/6");
        var fb = new (long t, double bid, double ask)[] { (100, 6, 1), (101, 1, 2), (106, 2, 7), (112, 9, 0), (113, 3, 8), (120, 1, 6) };
        CellBigSettings FS(double thr, int w) => new CellBigSettings { DotMedianRatio = 1, MinSide = 0, DotLocalTicks = w, DotHideBuyNearSellTicks = 2 };
        string BR(List<CellMark> m) => Ticks(m, 1) + " / " + Ticks(m, -1);
        Check(BR(Ev(FS(0, 4), 5.5, fb)) == "106,120 / 100,112", "nguong 5,5 -> xanh 106,120 / do 100,112", BR(Ev(FS(0, 4), 5.5, fb)));
        Check(BR(Ev(FS(0, 4), 7, fb)) == "106 / 112", "nguong 7 -> xanh 106 / do 112", BR(Ev(FS(0, 4), 7, fb)));
        Check(BR(Ev(FS(0, 4), 9, fb)) == " / 112", "nguong 9 -> do 112", BR(Ev(FS(0, 4), 9, fb)));
        var fa = new (long t, double bid, double ask)[] { (100, 8, 0), (102, 9, 0), (103, 7, 0), (110, 0, 7) };
        Check(BR(Ev(FS(0, 4), 7, fa)) == "110 / 102" && BR(Ev(FS(0, 0), 7, fa)) == "110 / 100,102,103", "no moi muc gia (w 0): do 100,102,103; w 4: do 102", BR(Ev(FS(0, 0), 7, fa)));

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
        var sq = new CellBigSettings(); UnifiedDots.Apply(sq, 2, R12, false, true, 9);
        var eq = Ev(sq, B4, test);
        Check(Ticks(eq, 1) == "112" && Ticks(eq, -1) == "100" && Math.Abs(eq[0].Threshold - 11.2) < 1e-9, "it nhieu: nguong 11,2 / w 4 / che 6 -> xanh {112}, do {100}", $"{Ticks(eq, 1)} / {Ticks(eq, -1)} nguong {eq[0].Threshold}");
        var sn = new CellBigSettings(); UnifiedDots.Apply(sn, 0, R12, false, true, 5);
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
