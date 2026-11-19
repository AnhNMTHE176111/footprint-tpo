// Test cho CellBigLogic (chấm Dot theo TỪNG TICK, luật fit chart M5 của CORVEN) và BigTradeLogic (vòng mờ = một lệnh đơn lớn, chốt 2026-11-19).
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

    static List<CellMark> Ev(CellBigSettings s, double avgLevelVol, params CellLevel[] lv)
        => CellBigLogic.Evaluate(lv, true, avgLevelVol, s);

    static int Count(List<CellMark> m, long tick, int tier) => m.Count(x => x.Tick == tick && x.Tier == tier);

    public static int Run()
    {
        Console.WriteLine("[CellBig] mac dinh (CellBigSettings)");
        var d = new CellBigSettings();
        Check(d.DotTradesRatio == 2.4 && d.DotLocalTicks == 3 && d.MinSide == 9 && d.DotEnabled && !d.FixedMode, "mac dinh: 2,4 / +-3 / san 9");

        Console.WriteLine("[CellBig] khong con Big dua tren volume o: o rat lon van chi ra Dot (hoac khong gi), khong bao gio bac Big");
        var huge = Ev(S(), 10, L(100, 0, 500, 500));
        Check(huge.Count == 1 && huge[0].Tier == CellBigLogic.TierDot, "sell 500 / 500 lenh: chi 1 dau Dot");
        Check(Ev(S(), 10, L(100, 0, 500, 1)).Count == 0, "sell 500 chi 1 lenh: khong Dot (it lenh) va khong con Big theo volume");
        Check(Ev(S(), 10, L(100, 0, 60, 1), L(101, 5, 5, 2)).Count == 0, "60 Bid trong 1 lenh trong DU LIEU O (1 lenh): khong ra gi tu logic o; vong mo di tu MaxOneTradeVolume");
        Check(CellBigLogic.TierDot == 2 && typeof(CellBigLogic).GetField("TierBig") == null && typeof(CellBigSettings).GetField("MaxSideRatio") == null && typeof(CellBigSettings).GetField("LocalTicks") == null && typeof(CellBigSettings).GetField("MinImbalance") == null,
              "bac Big theo volume va 3 tham so cua no da bo khoi API");

        Console.WriteLine("[CellBig] san MinSide 9 ap cho Dot");
        Check(Count(Ev(S(s => s.MinSide = 9), 2, L(100, 0, 8, 50)), 100, CellBigLogic.TierDot) == 0, "san 9 cho Dot: side 8 khong du dieu kien lenh van khong Dot");
        Check(Count(Ev(S(s => s.MinSide = 9), 2, L(100, 0, 9, 50)), 100, CellBigLogic.TierDot) == 1, "san 9 cho Dot: side 9 -> Dot");

        Console.WriteLine("[CellBig] Dot: so lenh >= 2,4 x volume TB moi o (avgLevelVol 10 -> 24)");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 24)), 100, CellBigLogic.TierDot) == 1, "24 lenh = 2,4 x 10 -> Dot (bien dung)");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 23)), 100, CellBigLogic.TierDot) == 0, "23 lenh < 24 -> khong");
        Check(Count(Ev(S(), 10, L(100, 30, 29, 24)), 100, CellBigLogic.TierDot) == 1, "Dot KHONG doi mat can bang (30 x 29)");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 24), L(103, 5, 5, 5)), 100, CellBigLogic.TierDot) == 0, "gieng cach 3 co side bang 5 (hoa) -> khong Dot");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 24), L(104, 5, 5, 5)), 100, CellBigLogic.TierDot) == 1, "gieng bang cach 4 (ngoai +-3) -> Dot");
        Check(Count(Ev(S(), 10, L(100, 6, 5, 24), L(103, 5, 5, 5)), 100, CellBigLogic.TierDot) == 1, "side 6 > gieng cach 3 co side 5 -> Dot");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 24), L(98, 6, 5, 1)), 100, CellBigLogic.TierDot) == 0, "gieng cach 2 co side 6 > 5 -> khong Dot");
        Check(Count(Ev(S(), 10, L(100, 5, 5, 24), L(98, 5, 5, 24)), 100, CellBigLogic.TierDot) == 0 && Count(Ev(S(), 10, L(100, 5, 5, 24), L(98, 5, 5, 24)), 98, CellBigLogic.TierDot) == 0, "hai o hoa side va deu du lenh -> khong o nao Dot");
        Check(Ev(S(s => s.DotEnabled = false), 10, L(100, 5, 5, 24)).Count == 0, "DotEnabled = false -> khong Dot");

        Console.WriteLine("[CellBig] mau theo ben troi, cỡ Dot");
        var one = Ev(S(), 10, L(100, 0, 30, 30));
        Check(one.Count == 1 && one[0].Tier == CellBigLogic.TierDot && one[0].Tick == 100 && one[0].Side == -1, "30 sell, 30 lenh: 1 Dot, Side -1");
        Check(Ev(S(), 10, L(100, 30, 0, 30))[0].Side == 1, "buy trội -> Side +1");
        Check(Ev(S(), 10, L(100, 5, 5, 30))[0].Side == -1, "hoa buy = sell -> Side -1 (nhu Python: ask > bid moi xanh)");
        Check(one[0].SizeFrac == CellBigLogic.DotSizeFrac, "SizeFrac Dot 0,45");

        Console.WriteLine("[CellBig] chua du lich su / chua co muc nen");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500, 500) }, false, 0, S()).Count == 0, "chua du 5 nen -> khong co gi");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500, 500) }, true, 0, S()).Count == 0, "muc nen 0 -> khong co gi");

        Console.WriteLine("[CellBig] che do nguong co dinh");
        var fx = S(s => { s.FixedMode = true; s.FixedThreshold = 10; });
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, fx).Count == 0, "fixed: 9 < 10 -> khong");
        Check(Count(CellBigLogic.Evaluate(new[] { L(100, 0, 10) }, false, 0, fx), 100, CellBigLogic.TierDot) == 1, "fixed: Dot dung side >= nguong co dinh, khong can nen nen");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 10) }, false, 0, fx).All(x => x.Tier == CellBigLogic.TierDot), "fixed: chi con bac Dot");
        var fx9 = S(s => { s.FixedMode = true; s.FixedThreshold = 5; s.MinSide = 9; });
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 8) }, false, 0, fx9).Count == 0 && CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, fx9).Count == 1, "fixed + san: dung max(nguong, san 9)");

        Console.WriteLine("[CellBig] BarStats (volume TB moi o co giao dich)");
        Check(CellBigLogic.BarStats(new[] { L(1, 3, 4), L(2, 10, 0), L(3, 0, 7) }, out double mean) && Math.Abs(mean - 24.0 / 3) < 1e-9, "mean = 24/3", $"{mean}");
        Check(CellBigLogic.BarStats(new[] { L(1, 10, 10), new CellLevel(2, 0, 0, 0, 0) }, out double m2) && Math.Abs(m2 - 20) < 1e-9, "o volume 0 khong tinh");
        Check(!CellBigLogic.BarStats(new CellLevel[0], out _), "nen rong -> khong nap");

        Console.WriteLine("[CellBig] baseline: 20 nen DA DONG truoc, can >= 5 nen");
        var bl = new CellBigBaseline(20);
        for (int i = 0; i < 4; i++) bl.Add(10);
        Check(!bl.TryGet(out _), "4 nen -> chua co muc nen");
        bl.Add(10);
        Check(bl.TryGet(out double b5) && Math.Abs(b5 - 10) < 1e-9, "5 nen -> co 10");
        bl.Add(1000);
        bl.TryGet(out double after);
        Check(after > 10, "nen vua dong moi vao muc nen cua nen SAU");
        var b2 = new CellBigBaseline(20);
        for (int i = 0; i < 20; i++) b2.Add(0);
        for (int i = 0; i < 20; i++) b2.Add(8);
        b2.TryGet(out double b20);
        Check(b2.Count == 20 && Math.Abs(b20 - 8) < 1e-9, "cuon dung 20 nen");
        var b3 = new CellBigBaseline(20);
        for (int i = 0; i < 6; i++) b3.Add(5 + i);
        b3.TryGet(out double y1);
        for (int r = 0; r < 50; r++) CellBigLogic.Evaluate(new[] { L(100, 0, 20) }, true, y1, S());
        b3.TryGet(out double y2);
        Check(y1 == y2 && b3.Count == 6, "nen live tinh lai nhieu lan khong nap trung muc nen");

        Console.WriteLine("[BigTrade] ranh gioi: lenh don >= ngưỡng (mac dinh 10); 0 = khong co so lieu");
        Check(!BigTradeLogic.Hit(9, 10), "9 < 10 -> khong no");
        Check(BigTradeLogic.Hit(10, 10), "10 = ngưỡng -> no");
        Check(BigTradeLogic.Hit(60, 10), "60 -> no");
        Check(!BigTradeLogic.Hit(0, 10), "0 (lich su khong co so lenh don) -> khong no");
        Check(!BigTradeLogic.Hit(-1, 10) && !BigTradeLogic.Hit(0, 0), "am / ngưỡng 0 voi so lieu 0 -> khong no");
        Check(BigTradeLogic.Hit(5, 5) && !BigTradeLogic.Hit(4.9, 5), "ngưỡng tuy chinh 5: 5 no, 4,9 khong");

        Console.WriteLine("[BigTrade] cỡ: 1,0 x be ngang nen o ngưỡng -> 2,5 tu 6 x ngưỡng, can bac hai");
        Check(Math.Abs(BigTradeLogic.SizeFrac(10, 10) - 1.0) < 1e-9, "o ngưỡng: 1,0");
        Check(Math.Abs(BigTradeLogic.SizeFrac(60, 10) - 2.5) < 1e-9 && BigTradeLogic.SizeFrac(186, 10) == 2.5, "tu 6 x ngưỡng: 2,5 va khong vuot");
        Check(BigTradeLogic.SizeFrac(5, 10) == 1.0, "duoi ngưỡng kep 1,0");
        bool mono = true; double prev = 0;
        for (double m = 10; m <= 100; m += 0.5) { double v = BigTradeLogic.SizeFrac(m, 10); if (v < prev - 1e-12) mono = false; prev = v; }
        Check(mono, "cỡ don dieu khong giam");
        double mid = BigTradeLogic.SizeFrac(25, 10);   // sqrt(2,5) = 1,581 -> t = 0,581/1,449 = 0,401 -> 1 + 1,5 x 0,401
        Check(Math.Abs(mid - (1.0 + 1.5 * (Math.Sqrt(2.5) - 1.0) / (Math.Sqrt(6.0) - 1.0))) < 1e-9 && mid > 1.4 && mid < 1.7, "25 hop dong (2,5 x ngưỡng): dung cong thuc can bac hai", mid.ToString("0.000"));
        // sqrt (lom) -> nua duong cua lenh (3,5 x ngưỡng) da qua nua khoang cỡ
        Check(BigTradeLogic.SizeFrac(35, 10) > 1.0 + 0.5 * 1.5, "can bac hai: 3,5 x ngưỡng da qua nua khoang cỡ");

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
