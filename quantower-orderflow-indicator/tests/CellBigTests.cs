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
        Check(d.DotMedianRatio == 2.8 && d.DotLocalTicks == 4 && d.DotHideBuyNearSellTicks == 6 && d.MinSide == 9 && d.DotEnabled && !d.FixedMode, "mac dinh: 2,8 / +-4 / che 6 / san 9");
        Check(typeof(CellBigSettings).GetField("DotTradesRatio") == null && typeof(CellMark).GetField("Trades") == null, "luat so lenh da bo khoi API");
        Check(CellBigLogic.TierDot == 2 && typeof(CellBigLogic).GetField("TierBig") == null, "chi con bac Dot");

        // mac dinh tu day: san 0, khong che (de thu doc lap), nen trung vi 10 -> nguong 28
        static CellBigSettings P(Action<CellBigSettings> f = null) { var s = new CellBigSettings { MinSide = 0, DotHideBuyNearSellTicks = -1 }; f?.Invoke(s); return s; }
        static int Reds(List<CellMark> m, long t) => m.Count(x => x.Tick == t && x.Side < 0);
        static int Blues(List<CellMark> m, long t) => m.Count(x => x.Tick == t && x.Side > 0);

        Console.WriteLine("[CellBig] tung ben doc lap: Bid xet rieng, Ask xet rieng");
        var rb = Ev(P(), 10, L(100, 40, 50));
        Check(Reds(rb, 100) == 1 && Blues(rb, 100) == 1 && rb.Count == 2, "cung tick: Bid 50 va Ask 40 deu >= 28 -> co CA do va xanh");
        var rr = Ev(P(), 10, L(100, 5, 30));
        Check(rr.Count == 1 && rr[0].Side == -1, "Bid 30, Ask 5: chi do");
        var rbl = Ev(P(), 10, L(100, 30, 5));
        Check(rbl.Count == 1 && rbl[0].Side == 1, "Ask 30, Bid 5: chi xanh");
        var sw = Ev(P(), 10, L(100, 40, 30));
        Check(Reds(sw, 100) == 1 && Blues(sw, 100) == 1, "Ask 40 > Bid 30 van co do vi Bid 30 >= 28 (khong con ben troi)");
        Check(Ev(P(), 10, L(100, 20, 27)).Count == 0, "Bid 27, Ask 20 deu duoi 28 -> khong");
        Check(Ev(P(s => s.DotEnabled = false), 10, L(100, 5, 50)).Count == 0, "DotEnabled = false -> khong Dot");

        Console.WriteLine("[CellBig] ranh gioi ty le 2,8 x trung vi (10 -> 28)");
        Check(Reds(Ev(P(), 10, L(100, 0, 28)), 100) == 1, "Bid 28 = 2,8 x 10 -> do (bien dung)");
        Check(Ev(P(), 10, L(100, 0, 27)).Count == 0, "Bid 27 < 28 -> khong");
        Check(Blues(Ev(P(), 10, L(100, 28, 0)), 100) == 1 && Ev(P(), 10, L(100, 27, 0)).Count == 0, "Ask: 28 xanh, 27 khong");
        var m1 = Ev(P(), 10, L(100, 0, 30));
        Check(Math.Abs(m1[0].Threshold - 28) < 1e-9 && Math.Abs(m1[0].Mult - 3.0) < 1e-9, "Threshold = 28, Mult = 30 / 10 = 3", $"{m1[0].Threshold} {m1[0].Mult}");

        Console.WriteLine("[CellBig] san MinSide 9");
        Check(Ev(P(s => s.MinSide = 9), 2, L(100, 0, 8)).Count == 0, "san 9: Bid 8 (>= 2,8 x 2 = 5,6) khong du");
        Check(Reds(Ev(P(s => s.MinSide = 9), 2, L(100, 0, 9)), 100) == 1, "san 9: Bid 9 -> do");
        Check(Blues(Ev(P(s => s.MinSide = 9), 2, L(100, 9, 0)), 100) == 1 && Ev(P(s => s.MinSide = 9), 2, L(100, 8, 0)).Count == 0, "san 9 cho Ask nhu nhau");
        Check(Math.Abs(Ev(P(s => s.MinSide = 9), 2, L(100, 0, 20))[0].Threshold - 9) < 1e-9, "Threshold = max(2,8 x 2, 9) = 9");

        Console.WriteLine("[CellBig] cuc dai dia phuong +-4 tick: lon hon HAN cung ben, tick vang = 0, bang nhau khong tinh");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(104, 0, 39)), 100) == 1, "gieng cach 4 co Bid 39 < 40 -> do");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(104, 0, 41)), 100) == 0, "gieng cach 4 co Bid 41 > 40 -> khong (4 con trong +-4)");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(105, 0, 90)), 100) == 1, "gieng cach 5 (ngoai +-4) Bid 90 khong ngan");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(96, 0, 41)), 100) == 0, "gieng ben duoi cach 4 lon hon -> khong");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(104, 0, 40)), 100) == 0 && Reds(Ev(P(), 10, L(100, 0, 40), L(104, 0, 40)), 104) == 0, "hoa Bid 40 = 40: khong o nao no");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(101, 0, 0)), 100) == 1, "gieng co Bid 0 khong ngan");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(103, 90, 5)), 100) == 1, "gieng co Ask 90 nhung Bid 5: Ask khong ngan Bid (xet rieng tung ben)");
        Check(Reds(Ev(P(), 10, L(100, 0, 40), L(98, 0, 0), L(102, 0, 20)), 100) == 1, "tick vang va gieng nho hon -> do");
        Check(Blues(Ev(P(), 10, L(100, 40, 0), L(103, 41, 0)), 100) == 0 && Blues(Ev(P(), 10, L(100, 40, 0), L(103, 41, 0)), 103) == 1, "Ask: cuc dai cung tuong tu");
        Check(Blues(Ev(P(), 10, L(100, 40, 0), L(103, 0, 90)), 100) == 1, "Bid cua gieng khong ngan Ask");
        Check(Ev(P(s => s.DotLocalTicks = 0), 10, L(100, 0, 40), L(101, 0, 90)).Count == 2, "DotLocalTicks = 0 -> khong xet gieng");

        Console.WriteLine("[CellBig] nen 5 (nguong 14): mac dinh chi cuc dai +-4 tick; DotLocalTicks = 0 (Nổ ở mọi mức giá) -> moi muc >= 14");
        var ex = new[] { L(1, 9, 5), L(2, 3, 14), L(3, 7, 15), L(4, 12, 16), L(5, 3, 10) };
        var exD = Ev(P(), 5, ex);
        Check(exD.Count == 1 && Reds(exD, 4) == 1, "mac dinh: dung 1 cham do o tick 4", string.Join(",", exD.Select(x => x.Side + "@" + x.Tick)));
        var exA = Ev(P(s => s.DotLocalTicks = 0), 5, ex);
        Check(exA.Count == 3 && Reds(exA, 2) == 1 && Reds(exA, 3) == 1 && Reds(exA, 4) == 1 && exA.All(x => x.Side < 0), "moi muc: do o tick 2,3,4, khong xanh", string.Join(",", exA.Select(x => x.Side + "@" + x.Tick)));

        Console.WriteLine("[CellBig] che: chấm xanh bi bo neu co chấm do cung nen cach <= 6 tick (do khong bi che)");
        static CellBigSettings H(int n) => new CellBigSettings { MinSide = 0, DotHideBuyNearSellTicks = n };
        var h6 = Ev(H(6), 10, L(100, 40, 0), L(106, 0, 40));
        Check(h6.Count == 1 && h6[0].Side == -1 && h6[0].Tick == 106, "cach 6 tick: xanh bi che, do con", string.Join(",", h6.Select(x => x.Side + "@" + x.Tick)));
        var h7 = Ev(H(6), 10, L(100, 40, 0), L(107, 0, 40));
        Check(h7.Count == 2 && h7.Count(x => x.Side > 0) == 1 && h7.Count(x => x.Side < 0) == 1, "cach 7 tick: ca hai con");
        var h6b = Ev(H(6), 10, L(106, 40, 0), L(100, 0, 40));
        Check(h6b.Count == 1 && h6b[0].Side == -1, "xanh o tren do cach 6: van bi che (doi xung)");
        var hs = Ev(H(6), 10, L(100, 40, 50));
        Check(hs.Count == 1 && hs[0].Side == -1, "cung tick: xanh bi che boi do cung tick");
        var h0 = Ev(H(0), 10, L(100, 40, 50), L(110, 40, 0));
        Check(h0.Count == 2 && h0[0].Side > 0 && h0[0].Tick == 110 && h0[1].Side < 0 && h0[1].Tick == 100, "che 0: chi che cung tick; xanh @110 con, xanh @100 bi che");
        Check(Ev(H(-1), 10, L(100, 40, 50)).Count == 2, "che am = tat che");
        var hr = Ev(H(6), 10, L(100, 0, 40), L(105, 0, 40));
        Check(hr.Count == 2 && hr.All(x => x.Side < 0), "do khong bao gio bi do khac che");
        var hb = Ev(H(6), 10, L(100, 40, 0), L(110, 0, 40));
        Check(hb.Count == 2, "xanh cach do 10 tick: giu ca hai");
        var hk = Ev(H(6), 10, L(100, 40, 0), L(103, 0, 40), L(104, 0, 41));
        Check(hk.Count(x => x.Side > 0) == 0 && hk.Count(x => x.Side < 0) == 1 && hk.Single(x => x.Side < 0).Tick == 104, "do @103 bi do @104 nuot; do @104 con va che xanh @100 (cach 4)");
        var hk2 = Ev(H(6), 10, L(100, 40, 0), L(107, 0, 40), L(108, 0, 41));
        Check(hk2.Count(x => x.Side > 0) == 1, "do @107 bi nuot, do @108 cach xanh 8 > 6: xanh con");

        Console.WriteLine("[CellBig] thu tu ve: xanh truoc, do sau (do len tren); moi mau tang dan theo tick");
        var ord = Ev(H(-1), 10, L(100, 40, 40), L(110, 40, 40), L(120, 0, 50), L(130, 50, 0));
        string ordS = string.Join(",", ord.Select(x => (x.Side > 0 ? "B" : "S") + x.Tick));
        Check(ordS == "B100,B110,B130,S100,S110,S120", "thu tu: " + ordS);

        Console.WriteLine("[CellBig] mau, cỡ Dot, du lieu cho Tooltip");
        var one = Ev(P(), 10, L(100, 0, 30));
        Check(one.Count == 1 && one[0].Tier == CellBigLogic.TierDot && one[0].Tick == 100 && one[0].Side == -1 && one[0].Sell == 30 && one[0].Buy == 0, "30 Bid: 1 Dot, Side -1, Sell 30");
        Check(one[0].SizeFrac == CellBigLogic.DotSizeFrac, "SizeFrac Dot 0,45");
        Check(Ev(P(), 10, L(100, 30, 0))[0].Side == 1, "Ask 30 -> Side +1");
        Check(Ev(P(), 10, L(100, 100, 100)).Count == 2, "hoa Bid = Ask = 100: ca do va xanh (khong con luat hoa -> do)");

        Console.WriteLine("[CellBig] chua du lich su / chua co muc nen");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500) }, false, 0, P()).Count == 0, "chua du 5 nen -> khong co gi");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 500) }, true, 0, P()).Count == 0, "muc nen 0 -> khong co gi");

        Console.WriteLine("[CellBig] che do nguong co dinh (max(nguong, san), van +-4 tick va che)");
        var fx = P(s => { s.FixedMode = true; s.FixedThreshold = 10; });
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, fx).Count == 0, "fixed: 9 < 10 -> khong");
        Check(Reds(CellBigLogic.Evaluate(new[] { L(100, 0, 10) }, false, 0, fx), 100) == 1, "fixed: Bid 10 -> do, khong can muc nen");
        Check(Blues(CellBigLogic.Evaluate(new[] { L(100, 10, 0) }, false, 0, fx), 100) == 1, "fixed: Ask 10 -> xanh");
        Check(CellBigLogic.Evaluate(new[] { L(100, 10, 12) }, false, 0, fx).Count == 2, "fixed: tick co ca hai ben >= 10 -> ca hai (che tat)");
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 10), L(103, 0, 11) }, false, 0, fx).Count == 1, "fixed: van loai khi gieng +-4 lon hon");
        var fx9 = P(s => { s.FixedMode = true; s.FixedThreshold = 5; s.MinSide = 9; });
        Check(CellBigLogic.Evaluate(new[] { L(100, 0, 8) }, false, 0, fx9).Count == 0 && CellBigLogic.Evaluate(new[] { L(100, 0, 9) }, false, 0, fx9).Count == 1, "fixed + san: dung max(nguong, san 9)");
        var fxh = CellBigLogic.Evaluate(new[] { L(100, 10, 0), L(103, 0, 10) }, false, 0, new CellBigSettings { MinSide = 0, FixedMode = true, FixedThreshold = 10 });
        Check(fxh.Count == 1 && fxh[0].Side == -1, "fixed: ap luat che 6 mac dinh (xanh @100 bi do @103 che)");

        Console.WriteLine("[CellBig] BarStats (volume TB va TRUNG VI moi o co giao dich)");
        Check(CellBigLogic.BarStats(new[] { L(1, 3, 4), L(2, 10, 0), L(3, 0, 7) }, out double mean, out double med) && Math.Abs(mean - 24.0 / 3) < 1e-9 && med == 7, "mean = 24/3, trung vi 7 (so o le)", $"{mean} {med}");
        Check(CellBigLogic.BarStats(new[] { L(1, 10, 10), L(2, 1, 1), L(3, 4, 0), L(4, 100, 0) }, out double m4, out double d4) && d4 == (4 + 20) / 2.0, "trung vi so o chan = TB hai gia tri giua (4 va 20 -> 12)", $"{d4}");
        Check(CellBigLogic.BarStats(new[] { L(1, 10, 10), new CellLevel(2, 0, 0, 0, 0) }, out double m2, out double d2) && Math.Abs(m2 - 20) < 1e-9 && d2 == 20, "o volume 0 khong tinh (ca TB va trung vi)");
        Check(!CellBigLogic.BarStats(new CellLevel[0], out _, out _), "nen rong -> khong nap");

        Console.WriteLine("[CellBig] baseline: 20 nen DA DONG truoc, can >= 5 nen (TB va trung vi)");
        var bl = new CellBigBaseline(20);
        for (int i = 0; i < 4; i++) bl.Add(10, 3);
        Check(!bl.TryGet(out _) && !bl.TryGetMedian(out _), "4 nen -> chua co muc nen");
        bl.Add(10, 3);
        Check(bl.TryGet(out double b5) && Math.Abs(b5 - 10) < 1e-9 && bl.TryGetMedian(out double q5) && Math.Abs(q5 - 3) < 1e-9, "5 nen -> TB 10, trung vi nen 3");
        bl.Add(1000, 33);
        bl.TryGet(out double after); bl.TryGetMedian(out double afterMed);
        Check(after > 10 && Math.Abs(afterMed - 8) < 1e-9, "nen vua dong moi vao muc nen cua nen SAU (trung vi: (5x3 + 33)/6 = 8)", $"{afterMed}");
        var b2 = new CellBigBaseline(20);
        for (int i = 0; i < 20; i++) b2.Add(0, 0);
        for (int i = 0; i < 20; i++) b2.Add(8, 5);
        b2.TryGet(out double b20); b2.TryGetMedian(out double q20);
        Check(b2.Count == 20 && Math.Abs(b20 - 8) < 1e-9 && Math.Abs(q20 - 5) < 1e-9, "cuon dung 20 nen (ca hai chuoi)");
        var b3 = new CellBigBaseline(20);
        for (int i = 0; i < 6; i++) b3.Add(5 + i, 2 + i);
        b3.TryGetMedian(out double y1);
        for (int r = 0; r < 50; r++) CellBigLogic.Evaluate(new[] { L(100, 0, 20) }, true, y1, P());
        b3.TryGetMedian(out double y2);
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
        Console.WriteLine("[CellBig] bo so theo ma: Nasdaq (NQ/MNQ)");
        foreach (var n in new[] { "/NQZ26:XCME", "NQZ26", "/NQ:XCME", "/NQ", "MNQH27", "/MNQZ26:XCME", "nqz26" })
            Check(SymbolPreset.IsNasdaq(n), "la Nasdaq: " + n);
        foreach (var n in new[] { null, "", "/GCZ26:XCEC", "GC", "MGCZ26", "NQLT", "NQMLF", "/ES:XCME", "NQZ", "NQZ2026", "NQA26" })
            Check(!SymbolPreset.IsNasdaq(n), "khong phai Nasdaq: " + (n ?? "null"));
        var nqs = new CellBigSettings(); SymbolPreset.ApplyNasdaq(nqs);
        Check(nqs.DotMedianRatio == 3.5 && nqs.DotLocalTicks == 8 && nqs.DotHideBuyNearSellTicks == 12 && nqs.MinSide == 9 && nqs.DotEnabled && !nqs.FixedMode, "bo Nasdaq: 3,5 / +-8 / che 12, san 9 giu nguyen");
        var nqAll = new CellBigSettings { DotLocalTicks = 0, DotHideBuyNearSellTicks = -1 }; SymbolPreset.ApplyNasdaq(nqAll);
        Check(nqAll.DotLocalTicks == 0 && nqAll.DotHideBuyNearSellTicks == -1, "bo Nasdaq giu che do no moi muc gia (0) va tat che (-1)");
        // cung mot nen: bid 30 tai tick 100 va bid 34 tai tick 106, nen 10. Bo GC (+-4): ca hai no; bo Nasdaq (+-8, 3,5 x 10 = 35): khong cai nao no (34 < 35)
        var lv = new[] { L(100, 0, 30), L(106, 0, 34) };
        Check(Ev(new CellBigSettings(), 10, lv).Count(m => m.Side < 0) == 2, "bo GC: 2 cham do (cach 6 tick > 4)");
        var nqs2 = new CellBigSettings(); SymbolPreset.ApplyNasdaq(nqs2);
        Check(Ev(nqs2, 10, lv).Count == 0, "bo Nasdaq: nguong 35 -> khong no");
        var lv2 = new[] { L(100, 0, 36), L(106, 0, 40) };
        var r2 = Ev(nqs2, 10, lv2);
        Check(r2.Count == 1 && r2[0].Tick == 106, "bo Nasdaq: 36 va 40 cach 6 tick (< 8) -> chi 40 no");

        Console.WriteLine("[CellBig] bo Nasdaq tu noi cua so theo bien do nen (khung)");
        Check(SymbolPreset.NqLocalTicksFor(0) == 8 && SymbolPreset.NqLocalTicksFor(47) == 8 && SymbolPreset.NqLocalTicksFor(112.6) == 8, "M1 (47 tick), M5 (113 tick), chua co lich su -> +-8");
        Check(SymbolPreset.NqLocalTicksFor(203) == 14 && SymbolPreset.NqLocalTicksFor(303) == 22 && SymbolPreset.NqLocalTicksFor(439) == 31, "M15 203 -> 14, M30 303 -> 22, H1 439 -> 31",
              $"{SymbolPreset.NqLocalTicksFor(203)},{SymbolPreset.NqLocalTicksFor(303)},{SymbolPreset.NqLocalTicksFor(439)}");
        var nq15 = new CellBigSettings(); SymbolPreset.ApplyNasdaq(nq15, 203);
        Check(nq15.DotLocalTicks == 14 && nq15.DotHideBuyNearSellTicks == 12 && nq15.DotMedianRatio == 3.5, "ApplyNasdaq(M15): +-14, che 12, 3,5 x");
        var nq15all = new CellBigSettings { DotLocalTicks = 0 }; SymbolPreset.ApplyNasdaq(nq15all, 203);
        Check(nq15all.DotLocalTicks == 0, "che do no moi muc gia van giu 0");
        // 40 tai tick 100, 38 tai tick 112 (cach 12): +-8 -> ca hai no; +-14 -> chi 40
        var lv3 = new[] { L(100, 0, 40), L(112, 0, 38) };
        Check(Ev(nqs2, 10, lv3).Count == 2 && Ev(nq15, 10, lv3).Count == 1, "cach 12 tick: M5 2 cham, M15 1 cham");
        Check(CellBigLogic.BarRangeTicks(new[] { L(100, 1, 0), L(140, 0, 2), new CellLevel(200, 0, 0, 0, 0) }) == 40 && CellBigLogic.BarRangeTicks(new CellLevel[0]) == 0, "bien do = tick cao - thap cua o co giao dich");
        var br = new CellBigBaseline(20);
        for (int i = 0; i < 4; i++) br.Add(5, 3, 100);
        Check(!br.TryGetRange(out _), "4 nen -> chua co bien do");
        br.Add(5, 3, 200);
        Check(br.TryGetRange(out double rg) && Math.Abs(rg - 120) < 1e-9, "5 nen -> bien do TB 120", $"{rg}");
        for (int i = 0; i < 30; i++) br.Add(5, 3, 50);
        br.TryGetRange(out double rg2);
        Check(Math.Abs(rg2 - 50) < 1e-9 && br.Count == 20, "cuon 20 nen ca bien do");

        return _fail;
    }
}
