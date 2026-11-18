// Đối chiếu C# (CellBigLogic + ExhaustionLogic) với script Python research/corven_m5_2026-11-18/ trên 27 nến M5 THẬT
// (12:15-14:25 UTC ngày 18/11/2026, file data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h*.csv).
// Mong đợi (Python, luật đã chọn): 17 bóng Ô lớn / 8 trùng vị trí CORVEN; 23 dấu kiệt sức / 9 trùng CORVEN.
// Không có file dữ liệu (chưa commit / máy khác) thì bỏ qua, không tính là lỗi.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using OrderFlowBubbles;

static class CorvenM5ParityTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // 24 bóng CORVEN (giờ, giá tâm) — copy từ fit_bubbles_m5.py (cột "P"/"B" là màu CORVEN, không dùng để ghép vị trí)
    static readonly (string t, double price)[] GT =
    {
        ("12:15",3774.65),("12:30",3768.05),("12:35",3760.95),("12:35",3760.15),("12:45",3754.15),("12:45",3752.45),
        ("12:50",3750.75),("12:55",3748.95),("13:00",3757.15),("13:00",3755.4),("13:00",3750.6),("13:00",3749.0),
        ("13:05",3766.3),("13:10",3773.5),("13:10",3770.55),("13:15",3772.15),("13:15",3767.95),("13:20",3770.2),
        ("13:25",3773.85),("13:30",3782.4),("13:30",3779.8),("13:50",3790.75),("13:50",3788.55),("14:20",3777.95)
    };
    // dấu kiệt sức CORVEN (fit_exhaustion_m5.py)
    static readonly HashSet<string> CTop = new() { "12:35", "12:45", "12:50", "13:30", "13:45" };
    static readonly HashSet<string> CBot = new() { "12:15", "13:10", "13:20", "13:40", "13:45", "13:50" };

    static string FindCsv()
    {
        const string name = "data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h";
        for (var d = new DirectoryInfo(AppContext.BaseDirectory); d != null; d = d.Parent)
            if (File.Exists(Path.Combine(d.FullName, name + ".csv"))) return Path.Combine(d.FullName, name);
        return null;
    }

    static double P(string s) => double.Parse(s, CultureInfo.InvariantCulture);

    public static int Run()
    {
        string prefix = FindCsv();
        if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Console.WriteLine("[M5] (bo qua doi chieu CORVEN M5: khong co file fp_..._9d16h.csv)"); return 0; }
        Console.WriteLine("[M5] Doi chieu C# voi Python tren 27 nen M5 that (CORVEN 18/11)");

        // gom per-level theo nến (đúng thứ tự file), tick = round(price x 10)
        var lv = new Dictionary<string, List<(long tick, double bid, double ask, double vol)>>();
        var order = new List<string>();
        bool first = true;
        foreach (var line in File.ReadLines(prefix + ".csv"))
        {
            if (first) { first = false; continue; }
            var f = line.Split(',');
            double vol = P(f[5]); if (vol <= 0) continue;            // Python: D = D[volume > 0]
            string key = f[1].Substring(0, 16);
            if (!lv.TryGetValue(key, out var l)) { l = new(); lv[key] = l; order.Add(key); }
            l.Add(((long)Math.Round(P(f[2]) * 10), P(f[3]), P(f[4]), vol));
        }
        var ohlc = new Dictionary<string, (long o, long h, long l, long c)>();
        first = true;
        foreach (var line in File.ReadLines(prefix + "_bars.csv"))
        {
            if (first) { first = false; continue; }
            var f = line.Split(',');
            ohlc[f[1].Substring(0, 16)] = ((long)Math.Round(P(f[2]) * 10), (long)Math.Round(P(f[3]) * 10), (long)Math.Round(P(f[4]) * 10), (long)Math.Round(P(f[5]) * 10));
        }

        var bl = new CellBigBaseline(20);
        var bubbles = new Dictionary<string, List<(double pos, double bid, double ask)>>();
        var exh = new List<(string t, bool top)>();
        var times = new HashSet<string>();
        for (int h = 12; h <= 14; h++) for (int m = 0; m < 60; m += 5) if (string.CompareOrdinal($"{h:00}:{m:00}", "12:15") >= 0 && string.CompareOrdinal($"{h:00}:{m:00}", "14:25") <= 0) times.Add($"2026-11-18 {h:00}:{m:00}");
        var s = new ExhSettings();
        foreach (var key in order)
        {
            var rows = CellBigLogic.GroupRows(lv[key].Select(x => (x.tick, x.ask, x.bid, x.vol)), 2, 1);   // buy = ask, sell = bid
            bool has = bl.TryGet(out double B);
            if (times.Contains(key))
            {
                foreach (var r in rows)
                {
                    var d = CellBigLogic.Decide(r.Buy, r.Sell, B, has, 1.25, 9, 3.0, false, 0);
                    if (!d.Hit) continue;
                    string t = key.Substring(11);
                    if (!bubbles.TryGetValue(t, out var lst)) bubbles[t] = lst = new();
                    lst.Add((CellBigLogic.RowCenterPrice(r.RowId, 2, 1, 0.1), r.Sell, r.Buy));
                }
                if (ohlc.TryGetValue(key, out var b))
                {
                    var el = lv[key].Select(x => new ExhLevel(x.tick, x.bid, x.ask, x.vol)).ToList();
                    foreach (bool top in new[] { true, false })
                        if (ExhaustionLogic.Detect(top, b.o, b.h, b.l, b.c, el, s).Hit) exh.Add((key.Substring(11), top));
                }
            }
            if (CellBigLogic.BarRowMean(rows, out double mean)) bl.Add(mean);
        }

        int nb = bubbles.Values.Sum(x => x.Count);
        Check(times.Count == 27, "27 nen mau", times.Count.ToString());
        Check(nb == 17, "bong O lon: 17 (nhu Python)", nb.ToString());
        // ghép vị trí kiểu Python: theo từng nến, tham lam theo (khoảng cách, i, j), dung sai 0,5 giá
        int hit = 0, gtBarsWith = 0, bothBars = 0;
        foreach (var grp in GT.GroupBy(g => g.t))
        {
            var gl = grp.ToList(); gtBarsWith++;
            bubbles.TryGetValue(grp.Key, out var al); al ??= new();
            if (al.Count > 0) bothBars++;
            var pairs = new List<(double d, int i, int j)>();
            for (int i = 0; i < al.Count; i++) for (int j = 0; j < gl.Count; j++) { double dd = Math.Abs(al[i].pos - gl[j].price); if (dd <= 0.5) pairs.Add((dd, i, j)); }
            pairs.Sort((x, y) => x.d != y.d ? x.d.CompareTo(y.d) : x.i != y.i ? x.i.CompareTo(y.i) : x.j.CompareTo(y.j));
            var ua = new HashSet<int>(); var ub = new HashSet<int>();
            foreach (var p in pairs) { if (ua.Contains(p.i) || ub.Contains(p.j)) continue; ua.Add(p.i); ub.Add(p.j); hit++; }
        }
        Check(hit == 8, "bong trung vi tri CORVEN: 8", hit.ToString());
        Check(gtBarsWith == 15 && bothBars == 11, "11/15 nen co bong CORVEN cung co bong cua minh", $"{bothBars}/{gtBarsWith}");

        int ne = exh.Count, eh = exh.Count(x => x.top ? CTop.Contains(x.t) : CBot.Contains(x.t));
        Check(ne == 23, "dau kiet suc: 23 (nhu Python)", ne.ToString());
        Check(eh == 9, "dau kiet suc trung CORVEN: 9", eh.ToString());
        Console.WriteLine(_fail == 0 ? "  -> M5: tat ca PASS" : $"  -> M5: {_fail} FAIL");
        return _fail;
    }
}
