// ReplayCsv — chạy detector C# (BenzoCore + BenzoZones + BenzoDetectors) trên file footprint export, KHÔNG cần Quantower.
//   dotnet run -c Release --project benzo-trader/tools/ReplayCsv -- <base> [A|B|C|D|ALL] [out.csv]
//   <base> = đường dẫn bỏ đuôi (đọc <base>_bars.csv và <base>.csv).
// Mỗi setup chạy ĐỘC LẬP (1 lệnh mở/setup, giống K.simulate của Python); ALL = engine ưu tiên A > B > D > C.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using BenzoTraderNs;

static class Program
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static int Main(string[] args)
    {
        if (args.Length < 1) { Console.Error.WriteLine("cách dùng: ReplayCsv <base> [A|B|C|D|ALL] [out.csv]"); return 2; }
        string basePath = args[0];
        string which = args.Length > 1 ? args[1].ToUpperInvariant() : "ALL";
        string outPath = args.Length > 2 ? args[2] : null;

        var bars = new List<BarData>();
        var barIdxOf = new List<int>();
        using (var rd = new StreamReader(basePath + "_bars.csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cT = Array.IndexOf(h, "datetime"), cO = Array.IndexOf(h, "open"), cH = Array.IndexOf(h, "high"),
                cL = Array.IndexOf(h, "low"), cC = Array.IndexOf(h, "close"), cV = Array.IndexOf(h, "volume"), cD = Array.IndexOf(h, "delta"),
                cB = Array.IndexOf(h, "bid_vol"), cA = Array.IndexOf(h, "ask_vol");
            string line; int n = 0;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                var t = DateTime.ParseExact(f[cT], "yyyy-MM-dd HH:mm:ss", Inv, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal);
                bars.Add(new BarData
                {
                    Idx = n, Time = t, O = D(f[cO]), H = D(f[cH]), L = D(f[cL]), C = D(f[cC]), Vol = D(f[cV]), Delta = D(f[cD]),
                    SellVol = D(f[cB]), BuyVol = D(f[cA])
                });
                barIdxOf.Add(int.Parse(f[cI], Inv)); n++;
            }
        }
        var posOfBarIdx = new Dictionary<int, int>();
        for (int k = 0; k < barIdxOf.Count; k++) posOfBarIdx[barIdxOf[k]] = k;
        var levels = new List<LevelVol>[bars.Count];
        using (var rd = new StreamReader(basePath + ".csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cP = Array.IndexOf(h, "price"), cB = Array.IndexOf(h, "bid_vol"), cA = Array.IndexOf(h, "ask_vol"), cV = Array.IndexOf(h, "volume");
            string line;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                if (!posOfBarIdx.TryGetValue(int.Parse(f[cI], Inv), out int pos)) continue;
                (levels[pos] ??= new List<LevelVol>()).Add(new LevelVol(D(f[cP]), D(f[cB]), D(f[cA]), D(f[cV])));
            }
        }
        Console.Error.WriteLine($"nạp {bars.Count} nến M1, {levels.Count(l => l != null)} nến có per-level");

        var sb = new StringBuilder("setup,time_utc,side,entry,sl,tp,outcome,exit_utc,r,zone,reason\n");
        var sets = which == "ALL" ? new[] { "A", "B", "C", "D" } : new[] { which };
        foreach (var s in sets)
        {
            var list = new List<ISetupDetector>();
            foreach (var c in (s == "ALL" ? "ABDC" : s)) list.Add(Make(c));
            var eng = new BenzoEngine("GCZ26", 0.1, null, list) { GetLevels = i => (IReadOnlyList<LevelVol>)levels[i] ?? Array.Empty<LevelVol>() };
            foreach (var b in bars) eng.Bars.Add(b);
            var sw = System.Diagnostics.Stopwatch.StartNew();
            eng.Advance(bars.Count - 1);
            Console.Error.WriteLine($"setup {s}: {eng.Signals.Count} tín hiệu ({sw.Elapsed.TotalSeconds:0.0}s)");
            foreach (var g in eng.Signals)
                sb.Append(s).Append(',').Append(g.Time.ToString("yyyy-MM-dd HH:mm:ss", Inv)).Append(',').Append(g.Side).Append(',')
                  .Append(g.Entry.ToString("0.0###", Inv)).Append(',').Append(g.Sl.ToString("0.0###", Inv)).Append(',').Append(g.Tp.ToString("0.0###", Inv)).Append(',')
                  .Append(g.Outcome).Append(',').Append(g.IsClosed ? g.ExitTime.ToString("yyyy-MM-dd HH:mm:ss", Inv) : "").Append(',')
                  .Append(g.IsClosed ? g.R.ToString("0.####", Inv) : "").Append(',').Append(g.Zone).Append(",\"").Append(g.Reason.Replace("\"", "'")).Append("\"\n");
        }
        if (outPath != null) File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false)); else Console.Write(sb.ToString());
        return 0;
    }

    static ISetupDetector Make(char c) => c switch
    {
        'A' => new DetectorA(), 'B' => new DetectorB(), 'C' => new DetectorC(), 'D' => new DetectorD(),
        _ => throw new ArgumentException("setup?")
    };
    static double D(string s) => double.Parse(s, Inv);
}
