// Test cho StackedImbalance.cs — Stacked Imbalance THUẦN + vùng kéo sang phải (2026-11-08).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text.Json;
using OrderFlowBubbles;

static class StackedImbalanceTests
{
    public static int Fail;
    const double T = 0.1;

    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) Fail++;
    }

    static bool Near(double a, double b) => Math.Abs(a - b) < 1e-6;

    static List<SiZone> D(double[] ask, double[] bid, double pct = 250, int run = 3, double minVol = 1)
        => StackedImbalanceCalc.Detect(100.0, T, ask, bid, pct, run, minVol);

    // [SI-1] ca thuần: 3 mức buy liên tiếp, đúng biên 250% (10 vs 4) vẫn tính
    static void PureBuy()
    {
        Console.WriteLine("[SI-1] Buy thuan 3 muc, dung bien 250%");
        var z = D(new double[] { 0, 10, 10, 10, 1 }, new double[] { 4, 4, 4, 9, 9 });
        Check(z.Count == 1, "dung 1 vung", $"count={z.Count}");
        if (z.Count != 1) return;
        Check(z[0].Side == 1, "phia buy");
        Check(Near(z[0].Lo, 100.1) && Near(z[0].Hi, 100.3), "vung 100.1-100.3", $"{z[0].Lo}-{z[0].Hi}");
        Check(z[0].Levels == 3, "3 muc");
        Check(Near(z[0].MinRatio, 2.5), "ty le yeu nhat 2.5", $"{z[0].MinRatio}");
        Check(Near(z[0].DomVolume, 30) && Near(z[0].OppVolume, 12), "tong buy 30 / sell cheo 12");
    }

    // [SI-2] ngưỡng tỷ lệ: 9.9 vs 4 (247.5%) KHÔNG đạt 250%; 250% nhận cái mà 300% loại
    static void RatioThreshold()
    {
        Console.WriteLine("[SI-2] Nguong ty le 250% / 300%");
        Check(D(new double[] { 0, 9.9, 10, 10 }, new double[] { 4, 4, 4, 0 }).Count == 0, "247.5% o 1 muc lam dut chuoi -> khong vung");
        var a = new double[] { 0, 11, 11, 11 }; var b = new double[] { 4, 4, 4, 0 };   // 275%
        Check(D(a, b, 250).Count == 1, "275% dat nguong 250%");
        Check(D(a, b, 300).Count == 0, "275% KHONG dat nguong 300%");
    }

    // [SI-3] ca biên 1-vs-0: bên kia = 0 vẫn là imbalance, chỉ volume tối thiểu chặn
    static void OneVsZero()
    {
        Console.WriteLine("[SI-3] Ca bien 1-vs-0 + volume toi thieu");
        var zeros = new double[] { 0, 0, 0, 0 };
        var z1 = D(new double[] { 0, 1, 1, 1 }, zeros, minVol: 1);
        Check(z1.Count == 1, "1 vs 0 voi san 1 -> co vung");
        Check(z1.Count == 1 && double.IsPositiveInfinity(z1[0].MinRatio), "ty le = vo cuc khi ben kia 0");
        Check(D(new double[] { 0, 1, 1, 1 }, zeros, minVol: 5).Count == 0, "1 vs 0 voi san 5 -> khong");
        Check(D(new double[] { 0, 5, 5, 5 }, zeros, minVol: 5).Count == 1, "5 vs 0 voi san 5 -> co (dung bang san)");
        Check(D(new double[] { 0, 5, 4, 5 }, zeros, minVol: 5).Count == 0, "1 muc duoi san lam dut chuoi");
        Check(D(zeros, zeros, minVol: 0).Count == 0, "0 vs 0 KHONG bao gio la imbalance (ke ca san 0)");
    }

    // [SI-4] chuỗi đứt: 2 + (đứt) + 3 → N=3 chỉ 1 vùng; N=2 ra 2 vùng
    static void BrokenChain()
    {
        Console.WriteLine("[SI-4] Chuoi dut");
        var a = new double[] { 0, 10, 10, 0, 10, 10, 10 };
        var b = new double[] { 2, 2, 2, 2, 2, 2, 2 };
        var z3 = D(a, b, run: 3);
        Check(z3.Count == 1 && Near(z3[0].Lo, 100.4) && Near(z3[0].Hi, 100.6), "N=3: 1 vung 100.4-100.6");
        var z2 = D(a, b, run: 2);
        Check(z2.Count == 2, "N=2: 2 vung tach rieng", $"count={z2.Count}");
    }

    // [SI-5] sell: Bid[i] ≥ 250% × Ask[i+1] — vùng đặt ở các mức BID (phía dưới đường chéo)
    static void PureSell()
    {
        Console.WriteLine("[SI-5] Sell thuan");
        var z = D(new double[] { 0, 4, 4, 4 }, new double[] { 10, 10, 10, 0 });
        Check(z.Count == 1 && z[0].Side == -1, "1 vung sell");
        Check(z.Count == 1 && Near(z[0].Lo, 100.0) && Near(z[0].Hi, 100.2), "vung 100.0-100.2");
        Check(z.Count == 1 && Near(z[0].MinRatio, 2.5), "ty le yeu nhat 2.5");
        Check(D(new double[] { 0, 4, 4, 4 }, new double[] { 10, 10, 10, 0 }, pct: 300).Count == 0, "300% loai");
    }

    // [SI-6] cùng nến có cả vùng buy (trên) và vùng sell (dưới); không so mức NGANG
    static void BothSidesAndNoHorizontal()
    {
        Console.WriteLine("[SI-6] Ca buy lan sell trong 1 nen; khong so ngang");
        // dưới: sell áp đảo (bid 10 vs ask mức trên 1); trên: buy áp đảo (ask 10 vs bid mức dưới 1)
        var ask = new double[] { 0, 1, 1, 1, 10, 10, 10 };
        var bid = new double[] { 10, 10, 10, 1, 1, 1, 0 };
        var z = D(ask, bid);
        Check(z.Exists(q => q.Side == 1 && Near(q.Lo, 100.4) && Near(q.Hi, 100.6)), "vung buy 100.4-100.6");
        Check(z.Exists(q => q.Side == -1 && Near(q.Lo, 100.0) && Near(q.Hi, 100.2)), "vung sell 100.0-100.2");
        // so NGANG (ask[i] vs bid[i]) sẽ thấy imbalance, so CHÉO thì không: ask[i]=10 vs bid[i-1]=10
        var z2 = D(new double[] { 0, 10, 10, 10 }, new double[] { 10, 1, 1, 1 });
        Check(!z2.Exists(q => q.Side == 1), "so cheo: ask 10 / bid duoi 10,1,1 -> chuoi buy chi 2 muc, khong vung");
    }

    // [SI-7] vị trí trong nến + cờ "bị rút râu"
    static void PositionAndWeak()
    {
        Console.WriteLine("[SI-7] Vi tri trong nen");
        Check(StackedImbalanceCalc.Locate(100.1, 100.3, 100.0, 100.5) == SiPosition.Body, "giua than");
        Check(StackedImbalanceCalc.Locate(100.6, 100.8, 100.0, 100.5) == SiPosition.UpperWick, "rau tren");
        Check(StackedImbalanceCalc.Locate(99.6, 99.8, 100.5, 100.0) == SiPosition.LowerWick, "rau duoi (nen do)");
        var buyTop = new SiZone { Side = 1, Lo = 100.6, Hi = 100.8 };
        StackedImbalanceCalc.Classify(buyTop, 100.0, 100.5);
        Check(buyTop.Weak, "buy o rau tren = bi rut rau (yeu)");
        var sellTop = new SiZone { Side = -1, Lo = 100.6, Hi = 100.8 };
        StackedImbalanceCalc.Classify(sellTop, 100.0, 100.5);
        Check(!sellTop.Weak, "sell o rau tren KHONG yeu (sell tu choi dinh)");
        var sellBot = new SiZone { Side = -1, Lo = 99.6, Hi = 99.8 };
        StackedImbalanceCalc.Classify(sellBot, 100.5, 100.0);
        Check(sellBot.Weak, "sell o rau duoi = bi rut rau (yeu)");
        var buyBody = new SiZone { Side = 1, Lo = 100.1, Hi = 100.3 };
        StackedImbalanceCalc.Classify(buyBody, 100.0, 100.5);
        Check(!buyBody.Weak && buyBody.Position == SiPosition.Body, "buy giua than = khoe");
    }

    // [SI-8] kết thúc vùng: chạm / đóng xuyên / hết hạn, cả buy và sell
    static void EndRules()
    {
        Console.WriteLine("[SI-8] Ket thuc vung");
        var M = SiEndMode.Touch; var C = SiEndMode.CloseThrough;
        // vùng buy 100.1-100.3
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 100.35, 100.5, M) == SiEnd.Active, "buy: nen o tren, chua cham -> con");
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 100.3, 100.5, M) == SiEnd.Touched, "buy: low = mep tren -> cham");
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 99.9, 100.0, M) == SiEnd.ClosedThrough, "buy: dong duoi mep duoi -> xuyen");
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 100.2, 100.5, C) == SiEnd.Active, "buy che do dong-xuyen: cham ma dong tren -> con");
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 99.9, 100.1, C) == SiEnd.Active, "buy che do dong-xuyen: dong DUNG mep duoi -> con");
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.6, 99.9, 100.0, C) == SiEnd.ClosedThrough, "buy che do dong-xuyen: dong duoi -> xuyen");
        // vùng sell 100.1-100.3
        Check(StackedImbalanceCalc.CheckEnd(-1, 100.1, 100.3, 100.05, 99.8, 99.9, M) == SiEnd.Active, "sell: nen o duoi, chua cham -> con");
        Check(StackedImbalanceCalc.CheckEnd(-1, 100.1, 100.3, 100.1, 99.8, 99.9, M) == SiEnd.Touched, "sell: high = mep duoi -> cham");
        Check(StackedImbalanceCalc.CheckEnd(-1, 100.1, 100.3, 100.6, 99.8, 100.4, C) == SiEnd.ClosedThrough, "sell: dong tren mep tren -> xuyen");
        // nhảy giá qua vùng mà không giao nhau (khoảng trống giữa 2 phiên) vẫn kết thúc
        Check(StackedImbalanceCalc.CheckEnd(1, 100.1, 100.3, 100.0, 99.5, 99.6, M) == SiEnd.ClosedThrough, "buy: gap xuong qua vung -> ket thuc");

        var after = new List<(double, double, double)>
        {
            (100.8, 100.5, 100.7), (100.9, 100.6, 100.8), (100.9, 100.4, 100.5), (100.6, 100.25, 100.4), (100.5, 99.8, 99.9)
        };
        var f1 = StackedImbalanceCalc.Follow(1, 100.1, 100.3, after, M, 0);
        Check(f1.endOffset == 4 && f1.reason == SiEnd.Touched, "Follow cham: nen thu 4", $"{f1.endOffset},{f1.reason}");
        var f2 = StackedImbalanceCalc.Follow(1, 100.1, 100.3, after, C, 0);
        Check(f2.endOffset == 5 && f2.reason == SiEnd.ClosedThrough, "Follow dong-xuyen: qua lan test, ket thuc nen 5", $"{f2.endOffset},{f2.reason}");
        var f3 = StackedImbalanceCalc.Follow(1, 100.1, 100.3, after, M, 2);
        Check(f3.endOffset == 2 && f3.reason == SiEnd.Expired, "Follow het han sau 2 nen", $"{f3.endOffset},{f3.reason}");
        var f4 = StackedImbalanceCalc.Follow(1, 100.1, 100.3, after.GetRange(0, 3), M, 0);
        Check(f4.endOffset == -1 && f4.reason == SiEnd.Active, "Follow chua cham -> con hieu luc");
    }

    // [SI-9] niêm phong: trường vùng đi qua JSON; bản ghi CŨ (không có trường) vẫn đọc được
    static void CacheFields()
    {
        Console.WriteLine("[SI-9] Niem phong truong vung");
        var d = new CachedBubbleData { Price = 100.1, PriceHi = 100.3, ZoneSide = -1, ZoneWeak = true, Shape = 5 };
        var back = JsonSerializer.Deserialize<CachedBubbleData>(JsonSerializer.Serialize(d));
        Check(Near(back.PriceHi, 100.3) && back.ZoneSide == -1 && back.ZoneWeak, "PriceHi/ZoneSide/ZoneWeak giu nguyen");
        var old = JsonSerializer.Deserialize<CachedBubbleData>("{\"Price\":4327.0,\"Shape\":0,\"Tooltip\":\"x\"}");
        Check(old.ZoneSide == 0 && old.PriceHi == 0 && !old.ZoneWeak, "ban ghi cu -> mac dinh 0 (khong phai vung)");
    }

    // [SI-10] đối chiếu với Python trên dữ liệu thật GCZ26 M1 (bỏ qua nếu máy không có file)
    //  Python (si_measure.py, R=250 N=3 M=5, từ 2026-08-03) đếm được 9731 vùng.
    static void RealDataCrossCheck()
    {
        Console.WriteLine("[SI-10] Doi chieu Python tren GCZ26 M1 that");
        string dir = @"C:\Users\anhla\OneDrive\Documents\footprint-tpo\data-export\data-footprint\";
        string f = dir + "fp_GCZ26_XCEC_Time_20260723-20261021_90d.csv", fb = dir + "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv";
        if (!File.Exists(f) || !File.Exists(fb)) { Console.WriteLine("  SKIP (khong co file du lieu)"); return; }
        var ci = CultureInfo.InvariantCulture;
        var hl = new Dictionary<int, (double h, double l)>();
        int first = int.MaxValue;
        foreach (var line in File.ReadLines(fb))
        {
            if (line.StartsWith("bar_idx")) continue;
            var p = line.Split(',');
            if (string.CompareOrdinal(p[1], "2026-08-03") < 0) continue;
            int bi = int.Parse(p[0]);
            first = Math.Min(first, bi);
            hl[bi] = (double.Parse(p[3], ci), double.Parse(p[4], ci));
        }
        var lv = new Dictionary<int, List<(long k, double bid, double ask)>>();
        foreach (var line in File.ReadLines(f))
        {
            if (line.StartsWith("bar_idx")) continue;
            int c1 = line.IndexOf(','); int bi = int.Parse(line.AsSpan(0, c1));
            if (bi < first) continue;
            var p = line.Split(',');
            long k = (long)Math.Round(double.Parse(p[2], ci) / T);
            if (!lv.TryGetValue(bi, out var l)) lv[bi] = l = new List<(long, double, double)>();
            l.Add((k, double.Parse(p[3], ci), double.Parse(p[4], ci)));
        }
        int zones = 0;
        foreach (var kv in hl)
        {
            long lo = (long)Math.Round(kv.Value.l / T), hi = (long)Math.Round(kv.Value.h / T);
            int n = (int)(hi - lo + 1);
            if (n < 2) continue;
            var ask = new double[n]; var bid = new double[n];
            if (lv.TryGetValue(kv.Key, out var l))
                foreach (var (k, b, a) in l) if (k >= lo && k <= hi) { ask[k - lo] += a; bid[k - lo] += b; }
            zones += StackedImbalanceCalc.Detect(lo * T, T, ask, bid, 250, 3, 5).Count;
        }
        Check(zones == 9731, "C# dem dung bang Python (9731 vung)", $"C#={zones}");
    }

    public static void RunAll()
    {
        PureBuy(); RatioThreshold(); OneVsZero(); BrokenChain(); PureSell();
        BothSidesAndNoHorizontal(); PositionAndWeak(); EndRules(); CacheFields(); RealDataCrossCheck();
    }
}
