// ReplayNq — chạy NqRunner (lõi OFB thật + NqMachine) trên file Footprint Export NQ → CSV lệnh cho parity với nq_setup.py.
//   dotnet run -c Release --project tools/ReplayNq -- --levels <fp_..._293d16h.csv> --out trades_cs.csv [--start 2026-09-14] [--cold] [--ver 1|2|3]
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using BenzoTraderNs;
using TradingPlatform.BusinessLayer;

static class Program
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static string Arg(string[] a, string k, string d) { int i = Array.IndexOf(a, k); return i >= 0 && i + 1 < a.Length ? a[i + 1] : d; }

    static int Main(string[] args)
    {
        string lvl = Arg(args, "--levels", null), outF = Arg(args, "--out", "trades_cs.csv");
        var start = DateTime.SpecifyKind(DateTime.Parse(Arg(args, "--start", "2026-09-14"), Inv), DateTimeKind.Utc);
        bool cold = args.Contains("--cold");
        var cfg = NqCfg.ForVersion(Arg(args, "--ver", "3"));   // 1 / 2 / 3
        var bars = LoadBars(lvl, lvl.Replace(".csv", "_bars.csv"));
        int startAbs = bars.FindIndex(b => b.TimeLeft >= start);
        string cache = "";   // "" = lõi OFB không niêm phong ra file (SignalCache bỏ qua khi đường dẫn rỗng) — nhanh, kết quả như file mới
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var run = new NqRunner(i => bars[i], 0.25, "NQZ26", cache, startAbs, cfg);
        run.M.CountFrom = start;
        run.Advance(bars.Count, cold);
        var T = run.M.Trades;
        using (var w = new StreamWriter(outF))
        {
            w.WriteLine("signal_utc,kind,side,entry,sl,tp,sl_pts,second,bias,big,big_levels,session,exit_utc,exit,how,r");
            foreach (var t in T.Where(t => t.Closed))
                w.WriteLine(string.Join(",", t.SigTime.ToString("yyyy-MM-dd HH:mm", Inv), t.Kind, t.SideText, F(t.Entry), F(t.Sl), F(t.Tp), F(t.Dist),
                    t.Second, t.Bias, t.Big, t.BigLv, t.Session, t.ExitTime.ToString("yyyy-MM-dd HH:mm", Inv), F(t.ExitPx), t.How, t.R.ToString("0.000000", Inv)));
        }
        Console.WriteLine($"{bars.Count} nến (máy từ {startAbs}), {T.Count} lệnh ({T.Count(t => t.Closed)} đã đóng), {(cold ? "nguội" : "tăng dần")}, {sw.Elapsed.TotalSeconds:0.0}s -> {outF}");
        return 0;
    }

    static string F(double v) => Math.Round(v, 6).ToString("0.######", Inv);

    // giống quantower-orderflow-indicator/perf/Golden LoadBars
    static List<HistoryItemBar> LoadBars(string lvlCsv, string barsCsv)
    {
        var bars = new List<HistoryItemBar>(); var byIdx = new Dictionary<int, HistoryItemBar>();
        bool first = true;
        foreach (var line in File.ReadLines(barsCsv))
        {
            if (first) { first = false; continue; }
            var p = line.Split(',');
            var t = DateTime.SpecifyKind(DateTime.Parse(p[1], Inv), DateTimeKind.Utc);
            var total = new VolumeAnalysisItem
            {
                Volume = D(p[10]), BuyVolume = D(p[9]), SellVolume = D(p[8]), MaxDelta = D(p[13]), MinDelta = D(p[14]),
                MaxOneTradeVolume = D(p[19]), Trades = (int)D(p[16]), BuyTrades = (int)D(p[17]), SellTrades = (int)D(p[18])
            };
            var b = new HistoryItemBar
            {
                TicksLeft = t.Ticks, Open = D(p[2]), High = D(p[3]), Low = D(p[4]), Close = D(p[5]), Volume = D(p[6]),
                VolumeAnalysisData = new VolumeAnalysisData { TimeLeft = t, Total = total, PriceLevels = new Dictionary<double, VolumeAnalysisItem>() }
            };
            byIdx[int.Parse(p[0], Inv)] = b; bars.Add(b);
        }
        first = true;
        foreach (var line in File.ReadLines(lvlCsv))
        {
            if (first) { first = false; continue; }
            var p = line.Split(',');
            if (!byIdx.TryGetValue(int.Parse(p[0], Inv), out var b)) continue;
            b.VolumeAnalysisData.PriceLevels[D(p[2])] = new VolumeAnalysisItem
            {
                SellVolume = D(p[3]), BuyVolume = D(p[4]), Volume = D(p[5]), Trades = (int)D(p[7]), BuyTrades = (int)D(p[8]), SellTrades = (int)D(p[9]), MaxOneTradeVolume = D(p[10])
            };
        }
        return bars;
    }
    static double D(string s) => double.Parse(s, Inv);
}
