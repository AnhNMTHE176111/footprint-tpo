// Test cho Big Trade "lệnh cá mập" (2026-11-25, research/bigtrade_whale_2026-11-25/SPEC.md mục 8 — mọi ví dụ đã chạy trên bw2_ref.Whale).
// Luật: hàng đợi 5 ngày nến (1380 phút nến có số liệu = 1 ngày nến), K = max(1, làm tròn(8 x phút / 1380)), ngưỡng = lệnh lớn thứ K,
// chưa đủ 1380 phút -> chưa có ngưỡng; vòng = lệnh lớn hơn hẳn ngưỡng, gộp trong g tick.
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class BigTradeWhaleTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // một nến có các ô lệnh đơn vals (tick khác nhau: 0, 1, 2, ...)
    static List<(long tick, double mot)> Bar(params double[] vals) => vals.Select((v, i) => ((long)i, v)).ToList();
    static List<(long tick, double mot)> Same(int n, double v) => Enumerable.Range(0, n).Select(i => ((long)i, v)).ToList();

    static string Thr(BigTradeWhale w) => w.TryThreshold(out int t) ? t.ToString() : "chua";

    // ô có lệnh mot có nổ không với ngưỡng thr (Select strict như OrderFlowBubbles)
    static bool Fires(double mot, int thr) => BigTradeAdaptive.Select(new List<(long, double)> { (0, mot) }, thr, 2, 0, true).Count == 1;

    public static int Run()
    {
        Console.WriteLine("[Whale] 1. so nen hang doi = max(1, lam tron(5 x 1380 / m))");
        {
            var ms = new double[] { 1, 5, 15, 30, 60, 240, 1440, 0 };
            var exp = new[] { 6900, 1380, 460, 230, 115, 29, 5, 6900 };
            var got = ms.Select(m => new BigTradeWhale(m).WindowBars).ToArray();
            Check(got.SequenceEqual(exp), "m = 1, 5, 15, 30, 60, 240, 1440, 0", string.Join(",", got));
            Check(new BigTradeWhale(-3).WindowBars == 6900 && new BigTradeWhale(double.NaN).WindowBars == 6900, "m am / NaN -> nhu m = 1");
        }

        Console.WriteLine("[Whale] 2. khoi dong (m = 60)");
        {
            var w = new BigTradeWhale(60);
            for (int i = 0; i < 22; i++) w.AddClosedBar(Bar(10));
            Check(!w.TryThreshold(out _) && w.K == 0, "22 nen [10] (1320 phut) -> chua co nguong", Thr(w));
            w.AddClosedBar(Bar(10));
            bool ok = w.TryThreshold(out int t);
            Check(ok && w.K == 8 && t == 10, "nen thu 23 -> K 8, nguong 10", $"K {w.K}, {Thr(w)}");
            Check(!Fires(10, t) && Fires(11, t), "o 10 khong no, o 11 no");
        }

        Console.WriteLine("[Whale] 3. hang theo thoi gian (m = 30)");
        {
            var w = new BigTradeWhale(30);
            for (int i = 1; i <= 45; i++) w.AddClosedBar(Bar(i));
            Check(!w.TryThreshold(out _), "45 nen [1]..[45] -> chua co nguong", Thr(w));
            w.AddClosedBar(Bar(46));
            Check(w.TryThreshold(out int t1) && t1 == 39 && w.K == 8, "them [46] -> nguong 39 (K 8)", $"K {w.K}, {Thr(w)}");
            for (int i = 0; i < 23; i++) w.AddClosedBar(Bar(100));
            bool ok = w.TryThreshold(out int t2);
            Check(ok && w.Count == 69 && w.Minutes == 2070 && w.K == 12 && t2 == 100, "them 23 nen [100] -> 69 nen, 2070 phut, K 12, nguong 100", $"{w.Count} nen, {w.Minutes} phut, K {w.K}, {Thr(w)}");
            Check(!Fires(100, t2) && Fires(101, t2), "o 100 khong no, o 101 no");
        }

        Console.WriteLine("[Whale] 4. lam tron K (m = 15)");
        {
            var w = new BigTradeWhale(15);
            var want = new Dictionary<int, int> { { 92, 8 }, { 93, 8 }, { 95, 8 }, { 98, 9 }, { 100, 9 } };
            var got = new List<string>();
            bool all = true;
            for (int i = 1; i <= 100; i++)
            {
                w.AddClosedBar(Bar(i));
                if (want.TryGetValue(i, out int k)) { got.Add($"{i}:{w.K}"); if (w.K != k) all = false; }
            }
            Check(all, "92, 93, 95, 98, 100 nen -> K 8, 8, 8, 9, 9", string.Join(" ", got));
        }

        Console.WriteLine("[Whale] 5. chua du mau (m = 1440)");
        {
            var w = new BigTradeWhale(1440);
            w.AddClosedBar(Bar(5, 6, 7));
            Check(!w.TryThreshold(out _) && w.K == 8 && w.Samples == 3, "1 nen [5, 6, 7]: du phut nhung K 8 > 3 mau -> chua co nguong", $"K {w.K}, {Thr(w)}");
            w.AddClosedBar(Same(20, 1));
            Check(w.TryThreshold(out int t) && w.K == 17 && t == 1, "them 1 nen 20 o gia tri 1 -> K 17, nguong 1", $"K {w.K}, {Thr(w)}");
        }

        Console.WriteLine("[Whale] 6. truot cua so (m = 1440, n = 5)");
        {
            var w = new BigTradeWhale(1440);
            for (int i = 0; i < 5; i++) w.AddClosedBar(Same(10, 200));
            Check(w.TryThreshold(out int t0) && w.K == 42 && t0 == 200, "5 nen x 10 o 200 -> K 42, nguong 200", $"K {w.K}, {Thr(w)}");
            for (int i = 0; i < 4; i++) w.AddClosedBar(Same(10, 20));
            Check(w.Count == 5 && w.TryThreshold(out int t1) && t1 == 20, "them 4 nen x 10 o 20 -> Count 5, nguong 20", $"{w.Count} nen, {Thr(w)}");
            w.AddClosedBar(Same(10, 20));
            Check(w.TryThreshold(out int t2) && t2 == 20 && w.Samples == 50 && w.Count == 5, "nen thu 5 nhu vay -> nguong 20, Samples 50", $"{w.Samples} mau, {Thr(w)}");
        }

        Console.WriteLine("[Whale] 7. m = 240");
        {
            var w = new BigTradeWhale(240);
            for (int i = 0; i < 5; i++) w.AddClosedBar(Bar(50, 40));
            Check(!w.TryThreshold(out _), "5 nen [50, 40] (1200 phut) -> chua co nguong", Thr(w));
            w.AddClosedBar(Bar(50, 40));
            Check(w.TryThreshold(out int t) && w.K == 8 && t == 40, "nen thu 6 -> K 8, nguong 40", $"K {w.K}, {Thr(w)}");
        }

        Console.WriteLine("[Whale] 8. don o cuoi (lenh > 4095)");
        {
            var w = new BigTradeWhale(1440);
            w.AddClosedBar(Same(8, 5000));
            Check(w.TryThreshold(out int t) && t == 4095, "1 nen 8 o 5000 -> nguong 4095", Thr(w));
            Check(Fires(5000, 4095) && !Fires(4095, 4095), "o 5000 no (so bang gia tri that), o 4095 khong");
        }

        Console.WriteLine("[Whale] 9. nen khong co so lieu");
        {
            var w = new BigTradeWhale(1);
            w.AddClosedBar(Bar(3));
            w.AddClosedBar(new List<(long, double)>());
            w.AddClosedBar(null);
            w.AddClosedBar(Bar(0, 0, -1));
            Check(w.Count == 1 && w.Samples == 1, "rong / null / toan mot <= 0 -> Count khong doi", $"{w.Count} nen, {w.Samples} mau");
        }

        Console.WriteLine("[Whale] 10. gop vong");
        {
            var cells = new List<(long tick, double mot)> { (100, 60), (101, 80), (103, 60), (110, 45), (111, 44) };
            string Kept(int thr) => string.Join(",", BigTradeAdaptive.Select(cells, thr, 2, 0, true).Select(i => cells[i].tick).OrderBy(x => x));
            Check(Kept(44) == "101,110", "nguong 44, g 2 -> giu tick 101 va 110", Kept(44));
            Check(Kept(60) == "101", "nguong 60 -> chi giu 101", Kept(60));
        }

        Console.WriteLine("[Whale] 11. khoang gop g");
        {
            var w = new BigTradeWhale(5);
            for (int i = 0; i < 4; i++) w.AddClosedBar(new List<(long, double)> { (0, 3), (40, 2) });
            Check(w.MergeTicks() == 2, "duoi 5 nen -> 2", $"{w.MergeTicks()}");
            w.AddClosedBar(new List<(long, double)> { (0, 3), (40, 2) });
            Check(w.MergeTicks() == 5, "5 nen bien do 40 -> lam tron(40 / 8) = 5", $"{w.MergeTicks()}");
            var w0 = new BigTradeWhale(5);
            for (int i = 0; i < 5; i++) w0.AddClosedBar(new List<(long, double)> { (7, 3) });
            Check(w0.MergeTicks() == 2, "bien do 0 -> 2", $"{w0.MergeTicks()}");
        }

        Console.WriteLine("[Whale] 12. khong nhin truoc (m = 60, 200 nen ngau nhien)");
        {
            List<List<(long, double)>> Gen(int seed)
            {
                var r = new Random(seed);
                var bars = new List<List<(long, double)>>();
                for (int i = 0; i < 200; i++)
                {
                    int n = r.Next(0, 6);   // 0 ô = nến không có số liệu
                    var b = new List<(long, double)>();
                    for (int j = 0; j < n; j++) b.Add((j * 3, r.Next(0, 120)));
                    bars.Add(b);
                }
                return bars;
            }
            List<string> Thrs(List<List<(long, double)>> bars)
            {
                var w = new BigTradeWhale(60); var res = new List<string>();
                foreach (var b in bars) { res.Add(Thr(w) + "/" + w.MergeTicks()); w.AddClosedBar(b); }
                return res;
            }
            var a = Gen(12345);
            var b2 = a.Take(150).ToList(); b2.AddRange(Gen(999).Skip(150));
            var ta = Thrs(a); var tb = Thrs(b2);
            bool same = ta.Take(151).SequenceEqual(tb.Take(151));
            bool differs = !a.Skip(150).Select(x => string.Join(";", x)).SequenceEqual(b2.Skip(150).Select(x => string.Join(";", x)));
            Check(same && differs, "doi noi dung nen 150-199 -> nguong nen 0-150 khong doi", $"co nguong {ta.Count(x => !x.StartsWith("chua"))} nen");
        }

        Console.WriteLine(_fail == 0 ? "[Whale] TAT CA PASS" : $"[Whale] {_fail} FAIL");
        return _fail;
    }
}
