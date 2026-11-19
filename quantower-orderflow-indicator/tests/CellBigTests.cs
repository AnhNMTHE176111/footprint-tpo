// Test cho CellBigLogic — Ô Bid/Ask lớn theo TỪNG TICK (luật fit chart M5 của CORVEN, 2026-11-19).
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class CellBigTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // ô: (tick, buy = ask, sell = bid, trades); vol = buy + sell
    static CellLevel L(long tick, double buy, double sell, int trades = 1) => new CellLevel(tick, buy, sell, buy + sell, trades);

    static CellBigSettings S(Action<CellBigSettings> f = null) { var s = new CellBigSettings { MinSide = 0 }; f?.Invoke(s); return s; }

    static List<CellMark> Ev(CellBigSettings s, double avgLevelVol, double avgMaxSide, params CellLevel[] lv)
        => CellBigLogic.Evaluate(lv, true, avgLevelVol, avgMaxSide, s);

    static int Count(List<CellMark> m, long tick, int tier) => m.Count(x => x.Tick == tick && x.Tier == tier);

    public static int Run()
    {
        Console.WriteLine("[CellBig] mac dinh (CellBigSettings)");
        var d = new CellBigSettings();
        Check(d.MaxSideRatio == 0.5 && d.LocalTicks == 5 && d.MinImbalance == 4.0 && d.DotTradesRatio == 2.4 && d.DotLocalTicks == 3 && d.MinSide == 9 && d.DotEnabled && !d.FixedMode, "mac dinh: 0,5 / +-5 / 4 / 2,4 / +-3 / san 9");

        Console.WriteLine("[CellBig] Big: bien ty le bien tren side >= 0,5 x ben troi lon nhat trung binh (avgMaxSide 40 -> 20)");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 20)), 100, CellBigLogic.TierBig) == 1, "side 20 = 0,5 x 40 -> Big (bien dung)");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 19)), 100, CellBigLogic.TierBig) == 0, "side 19 < 20 -> khong");
        Check(Count(Ev(S(), 100, 40, L(100, 21, 0)), 100, CellBigLogic.TierBig) == 1, "buy 21 -> Big (xet ben troi, ben yeu 0)");
        Check(Ev(S(), 100, 40, L(100, 8, 8)).Count == 0, "8 x 8 (tong 16) khong no: xet ben troi, khong xet tong");

        Console.WriteLine("[CellBig] Big: lon hon HAN moi tick khac trong +-5 tick cung nen");
        // neighbour side 20 (khong tu thanh Big vi 19.. dung avgMaxSide lon de neighbour khong no): avgMaxSide 40 -> nguong 20; dung neighbour 19 de khong no
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(105, 0, 19)), 100, CellBigLogic.TierBig) == 1, "tick lang gieng cach 5 co side 19 < 25 -> Big");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(105, 0, 25)), 100, CellBigLogic.TierBig) == 0, "tick cach 5 bang 25 (hoa) -> KHONG Big (phai lon hon han)");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(95, 0, 26)), 100, CellBigLogic.TierBig) == 0, "tick cach 5 phia duoi lon hon (26) -> khong Big");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(106, 0, 25)), 100, CellBigLogic.TierBig) == 1, "tick bang cach 6 (ngoai cua so +-5) -> van Big");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(101, 0, 26)), 100, CellBigLogic.TierBig) == 0, "tick ke ben lon hon -> khong Big");
        var tie = Ev(S(), 100, 40, L(100, 0, 25), L(103, 0, 25));
        Check(tie.Count(x => x.Tier == CellBigLogic.TierBig) == 0, "hai tick bang nhau trong cua so -> khong tick nao Big");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), L(104, 30, 0)), 100, CellBigLogic.TierBig) == 0, "tick gieng lon hon o BEN KIA (buy 30 vs sell 25) van chan: so side voi side");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25)), 100, CellBigLogic.TierBig) == 1, "tick vang (khong co gieng) tinh 0 -> Big");
        // o gieng volume 0 bi bo (khong lam chan)
        Check(Count(Ev(S(), 100, 40, L(100, 0, 25), new CellLevel(101, 99, 99, 0, 0)), 100, CellBigLogic.TierBig) == 1, "o co volume 0 bi bo qua, khong chan");

        Console.WriteLine("[CellBig] Big: mat can bang side >= 4 x max(weak, 1)");
        Check(Count(Ev(S(), 100, 40, L(100, 5, 20)), 100, CellBigLogic.TierBig) == 1, "20 x 5: 20 = 4 x 5 -> Big (bien dung)");
        Check(Count(Ev(S(), 100, 40, L(100, 5.1, 20)), 100, CellBigLogic.TierBig) == 0, "20 x 5,1: 20 < 20,4 -> khong");
        Check(Count(Ev(S(), 100, 40, L(100, 0, 20)), 100, CellBigLogic.TierBig) == 1, "20 x 0: weak 0 qua");
        // weak 0 duoc tinh la 1: side 3 < 4 x 1 -> khong; side 4 -> co (nguong ratio thap)
        Check(Count(Ev(S(), 100, 2, L(100, 0, 3)), 100, CellBigLogic.TierBig) == 0, "weak 0 tinh la 1: side 3 < 4 -> khong");
        Check(Count(Ev(S(), 100, 2, L(100, 0, 4)), 100, CellBigLogic.TierBig) == 1, "weak 0 tinh la 1: side 4 = 4 -> Big");
        Check(Count(Ev(S(s => s.MinImbalance = 0), 100, 2, L(100, 0, 1)), 100, CellBigLogic.TierBig) == 1, "MinImbalance 0 = tat dieu kien");
        Check(Count(Ev(S(), 100, 40, L(100, 100, 101)), 100, CellBigLogic.TierBig) == 0, "100 x 101 can bang -> khong Big");

        Console.WriteLine("[CellBig] san MinSide 9 ap cho ca Big va Dot");
        Check(Count(Ev(S(s => s.MinSide = 9), 100, 4, L(100, 0, 8)), 100, CellBigLogic.TierBig) == 0, "side 8 < san 9 -> khong Big (du >= 0,5 x 4)");
        Check(Count(Ev(S(s => s.MinSide = 9), 100, 4, L(100, 0, 9)), 100, CellBigLogic.TierBig) == 1, "side 9 = san -> Big");
        Check(Count(Ev(S(s => s.MinSide = 9), 2, 100, L(100, 0, 8, 50)), 100, CellBigLogic.TierDot) == 0, "san 9 cho Dot: side 8 khong du dieu kien lenh van khong Dot");
        Check(Count(Ev(S(s => s.MinSide = 9), 2, 100, L(100, 0, 9, 50)), 100, CellBigLogic.TierDot) == 1, "san 9 cho Dot: side 9 -> Dot");

        Console.WriteLine("[CellBig] Dot: so lenh >= 2,4 x volume TB moi o (avgLevelVol 10 -> 24)");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 24)), 100, CellBigLogic.TierDot) == 1, "24 lenh = 2,4 x 10 -> Dot (bien dung)");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 23)), 100, CellBigLogic.TierDot) == 0, "23 lenh < 24 -> khong");
        Check(Count(Ev(S(), 10, 1000, L(100, 30, 29, 24)), 100, CellBigLogic.TierDot) == 1, "Dot KHONG doi mat can bang (30 x 29)");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 24), L(103, 5, 5, 5)), 100, CellBigLogic.TierDot) == 0, "gieng cach 3 co side bang 5 (hoa) -> khong Dot");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 24), L(104, 5, 5, 5)), 100, CellBigLogic.TierDot) == 1, "gieng bang cach 4 (ngoai +-3) -> Dot");
        Check(Count(Ev(S(), 10, 1000, L(100, 6, 5, 24), L(103, 5, 5, 5)), 100, CellBigLogic.TierDot) == 1, "side 6 > gieng cach 3 co side 5 -> Dot");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 24), L(98, 6, 5, 1)), 100, CellBigLogic.TierDot) == 0, "gieng cach 2 co side 6 > 5 -> khong Dot");
        Check(Count(Ev(S(), 10, 1000, L(100, 5, 5, 24), L(98, 5, 5, 24)), 100, CellBigLogic.TierDot) == 0 && Count(Ev(S(), 10, 1000, L(100, 5, 5, 24), L(98, 5, 5, 24)), 98, CellBigLogic.TierDot) == 0, "hai o hoa side va deu du lenh -> khong o nao Dot");
        Check(Ev(S(s => s.DotEnabled = false), 10, 1000, L(100, 5, 5, 24)).Count == 0, "DotEnabled = false -> khong Dot");

        Console.WriteLine("[CellBig] mot o vua Big vua Dot -> hai dau (Big truoc, Dot sau); mau theo ben troi");
        var both = Ev(S(), 10, 20, L(100, 0, 30, 30));
        Check(both.Count == 2 && both[0].Tier == CellBigLogic.TierBig && both[1].Tier == CellBigLogic.TierDot && both.All(x => x.Tick == 100 && x.Side == -1), "30 sell, 30 lenh: Big roi Dot, cung tick 100, Side -1");
        Check(Ev(S(), 10, 20, L(100, 30, 0, 30))[0].Side == 1, "buy trội -> Side +1");
        Check(Ev(S(), 10, 1000, L(100, 5, 5, 30))[0].Side == -1, "hoa buy = sell -> Side -1 (nhu Python: ask > bid moi xanh)");
        var sz = Ev(S(), 10, 20, L(100, 0, 30, 30));
        Check(sz[1].SizeFrac == CellBigLogic.DotSizeFrac && sz[0].SizeFrac >= 1.0 && sz[0].SizeFrac <= 2.5, "SizeFrac: Dot 0,45; Big 1,0..2,5");

        Console.WriteLine("[CellBig] chua du lich su / chua co muc nen");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500, 500) }, false, 0, 0, S()).Count == 0, "chua du 5 nen -> khong co gi");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500, 500) }, true, 0, 0, S()).Count == 0, "muc nen 0 -> khong co gi");

        Console.WriteLine("[CellBig] che do nguong co dinh");
        var fx = S(s => { s.FixedMode = true; s.FixedThreshold = 10; });
        Check(Count(CellBigLogic.Evaluate(new[] { L(100, 0, 10) }, false, 0, 0, fx), 100, CellBigLogic.TierBig) == 1, "fixed: 10 >= 10 -> Big khong can nen nen");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, 0, fx).Count == 0, "fixed: 9 < 10 -> khong");
        Check(Count(CellBigLogic.Evaluate(new[] { L(100, 0, 10) }, false, 0, 0, fx), 100, CellBigLogic.TierDot) == 1, "fixed: Dot dung side >= nguong co dinh");
        Check(CellBigLogic.Evaluate(new[] { L(100, 15, 14) }, false, 0, 0, fx).All(x => x.Tier == CellBigLogic.TierDot), "fixed: 15 x 14 can bang -> chi Dot (Big can mat can bang)");
        Check(Math.Abs(CellBigLogic.Evaluate(new[] { L(100, 0, 20) }, false, 0, 0, fx)[0].SizeFrac - 1.5) < 1e-9, "fixed: Big co cỡ giua 1,5");
        var fx9 = S(s => { s.FixedMode = true; s.FixedThreshold = 5; s.MinSide = 9; });
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 8) }, false, 0, 0, fx9).Count == 0 && CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, 0, fx9).Count == 2, "fixed + san: dung max(nguong, san 9)");

        Console.WriteLine("[CellBig] cỡ Big (Size) theo side / ben troi lon nhat TB");
        Check(Math.Abs(CellBigLogic.Size(0.5, 0.5) - 1.0) < 1e-9, "o nguong 0,5: 1,0 x be ngang nen");
        Check(Math.Abs(CellBigLogic.Size(2, 0.5) - 2.5) < 1e-9 && CellBigLogic.Size(10, 0.5) == 2.5, "tu 2 lan tro len: 2,5 x be ngang nen");
        bool mono = true; double prev = 0;
        for (double m = 0.5; m <= 4; m += 0.05) { double v = CellBigLogic.Size(m, 0.5); if (v < prev - 1e-12) mono = false; prev = v; }
        Check(mono, "Size don dieu khong giam");
        Check(CellBigLogic.Size(1, 0.5) > 1.0 && CellBigLogic.Size(1, 0.5) < 2.5, "mult 1: o giua");
        var m1 = Ev(S(), 100, 40, L(100, 0, 40));
        Check(Math.Abs(m1[0].Mult - 1.0) < 1e-9 && Math.Abs(m1[0].SizeFrac - CellBigLogic.Size(1, 0.5)) < 1e-9, "Mark.Mult = side / avgMaxSide, SizeFrac theo Size");

        Console.WriteLine("[CellBig] BarStats (volume TB moi o co giao dich + ben troi lon nhat)");
        Check(CellBigLogic.BarStats(new[] { L(1, 3, 4), L(2, 10, 0), L(3, 0, 7) }, out double mean, out double mx) && Math.Abs(mean - 24.0 / 3) < 1e-9 && mx == 10, "mean = 24/3, maxSide 10", $"{mean} {mx}");
        Check(CellBigLogic.BarStats(new[] { L(1, 10, 10), new CellLevel(2, 0, 0, 0, 0) }, out double m2, out _) && Math.Abs(m2 - 20) < 1e-9, "o volume 0 khong tinh");
        Check(!CellBigLogic.BarStats(new CellLevel[0], out _, out _), "nen rong -> khong nap");

        Console.WriteLine("[CellBig] baseline: 20 nen DA DONG truoc, can >= 5 nen (hai chuoi)");
        var bl = new CellBigBaseline(20);
        for (int i = 0; i < 4; i++) bl.Add(10, 30);
        Check(!bl.TryGet(out _) && !bl.TryGetMaxSide(out _), "4 nen -> chua co muc nen");
        bl.Add(10, 30);
        Check(bl.TryGet(out double b5) && Math.Abs(b5 - 10) < 1e-9 && bl.TryGetMaxSide(out double x5) && Math.Abs(x5 - 30) < 1e-9, "5 nen -> co (10, 30)");
        bl.Add(1000, 5000);
        bl.TryGet(out double after); bl.TryGetMaxSide(out double afterMx);
        Check(after > 10 && afterMx > 30, "nen vua dong moi vao muc nen cua nen SAU");
        var b2 = new CellBigBaseline(20);
        for (int i = 0; i < 20; i++) b2.Add(0, 0);
        for (int i = 0; i < 20; i++) b2.Add(8, 16);
        b2.TryGet(out double b20); b2.TryGetMaxSide(out double x20);
        Check(b2.Count == 20 && Math.Abs(b20 - 8) < 1e-9 && Math.Abs(x20 - 16) < 1e-9, "cuon dung 20 nen (ca hai chuoi)");
        var b3 = new CellBigBaseline(20);
        for (int i = 0; i < 6; i++) b3.Add(5 + i, 10 + i);
        b3.TryGet(out double y1); b3.TryGetMaxSide(out double z1);
        for (int r = 0; r < 50; r++) CellBigLogic.Evaluate(new[] { L(100, 0, 20) }, true, y1, z1, S());
        b3.TryGet(out double y2);
        Check(y1 == y2 && b3.Count == 6, "nen live tinh lai nhieu lan khong nap trung muc nen");

        Console.WriteLine("[CellBig] SignalCache: ban ghi cu khong co CellDot nap ra Big; Dot ghi doc lai dung");
        var oldRec = System.Text.Json.JsonSerializer.Deserialize("{\"TimeTicks\":1,\"Bubbles\":[{\"Price\":1.5,\"CellBig\":true,\"CellSide\":1}]}", SignalCacheJson.Default.CachedBarData);
        Check(oldRec != null && oldRec.Bubbles[0].CellBig && !oldRec.Bubbles[0].CellDot, "ban ghi cu khong co CellDot -> nap ra Big");
        var dotRec = new CachedBarData { TimeTicks = 2 }; dotRec.Bubbles.Add(new CachedBubbleData { CellBig = true, CellDot = true });
        var back = System.Text.Json.JsonSerializer.Deserialize(System.Text.Json.JsonSerializer.Serialize(dotRec, SignalCacheJson.Default.CachedBarData), SignalCacheJson.Default.CachedBarData);
        Check(back.Bubbles[0].CellDot, "CellDot ghi roi doc lai van true");

        // MergeAdjacent (gop o lien ke)
        static string K(List<int> l) { l.Sort(); return string.Join(",", l); }
        var c3 = new List<(long, double)> { (10, 20), (11, 50), (12, 30) };
        Check(K(CellBigLogic.MergeAdjacent(c3, 1)) == "1", "cum 3 o lien nhau -> giu o lon nhat", K(CellBigLogic.MergeAdjacent(c3, 1)));
        var c2 = new List<(long, double)> { (10, 20), (12, 30) };
        Check(K(CellBigLogic.MergeAdjacent(c2, 1)) == "0,1", "2 o cach 2 tick, gap 1 -> giu ca hai");
        Check(K(CellBigLogic.MergeAdjacent(c3, 0)) == "0,1,2", "gap 0 -> giu het");
        var c5 = new List<(long, double)> { (1, 10), (2, 20), (3, 30), (4, 40), (5, 50) };
        Check(K(CellBigLogic.MergeAdjacent(c5, 1)) == "0,2,4", "chuoi 5 o side tang: NMS giu 5,3,1", K(CellBigLogic.MergeAdjacent(c5, 1)));
        Check(K(CellBigLogic.MergeAdjacent(c5, 2)) == "1,4", "chuoi 5 o gap 2: giu o 5 va o 2", K(CellBigLogic.MergeAdjacent(c5, 2)));
        var tie1 = new List<(long, double)> { (11, 30), (10, 30) };
        Check(K(CellBigLogic.MergeAdjacent(tie1, 1)) == "1", "hoa side: giu o tick thap hon (tat dinh)");
        var tie2 = new List<(long, double)> { (10, 30), (11, 30) };
        Check(K(CellBigLogic.MergeAdjacent(tie2, 1)) == "0", "hoa side (thu tu dao): van giu tick thap hon");
        Check(CellBigLogic.MergeAdjacent(new List<(long, double)>(), 1).Count == 0, "rong -> rong");

        Console.WriteLine("[CellBig] FloorDiv (StopHuntLogic dung)");
        Check(CellBigLogic.FloorDiv(7, 2) == 3 && CellBigLogic.FloorDiv(-1, 2) == -1 && CellBigLogic.FloorDiv(-4, 2) == -2, "floor chia dung voi so am");
        return _fail;
    }
}
