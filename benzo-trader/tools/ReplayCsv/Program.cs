// ReplayCsv — chạy detector C# (BenzoCore + BenzoZones + BenzoDetectors) trên file footprint export, KHÔNG cần Quantower.
//   dotnet run -c Release --project benzo-trader/tools/ReplayCsv -- <base> [A|B|B2|B3|BSR|C|D|ALL|LEVELS] [out.csv]
//   B = chỉ 2 VWAP (B cũ) · B2 = + vùng v2 (HVN/VA/POC) · B3 = + vùng S/R (VCL, PDH/PDL) · BSR = 2 VWAP + S/R (không v2)
//   LEVELS = xuất các mức cố định + 7 khe VCL của từng nến (đối chiếu mảng với Python zones_b_v3)
//   Biến môi trường BENZO_NO_VOPEN=1: tắt luật "mở ảo" 19:20-20:30 (để so thô với Python).
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
        bool noVopen = Environment.GetEnvironmentVariable("BENZO_NO_VOPEN") == "1";
        if (which == "LEVELS") return DumpLevels(bars, levels, outPath);
        var sets = which == "ALL" ? new[] { "A", "B", "C", "D" } : which.Split(',');
        foreach (var s in sets)
        {
            var list = new List<ISetupDetector>();
            list.Add(Make(s));
            var eng = new BenzoEngine("GCZ26", 0.1, null, list) { GetLevels = i => (IReadOnlyList<LevelVol>)levels[i] ?? Array.Empty<LevelVol>(), VirtualOpenRule = !noVopen };
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

    static ISetupDetector Make(string c) => c switch
    {
        "A" => new DetectorA(), "B" => new DetectorB(), "B2" => new DetectorB(true, false), "B3" => new DetectorB(true, true),
        "BSR" => new DetectorB(false, true), "C" => new DetectorC(), "D" => new DetectorD(),
        _ => throw new ArgumentException("setup?")
    };

    /// <summary>Mỗi nến một dòng: giờ, phiên, 12 mức cố định, rồi 7 khe VCL × (lo, hi, runlen). Đối chiếu mảng với Python (parity_b_v3.py).</summary>
    static int DumpLevels(List<BarData> bars, List<LevelVol>[] levels, string outPath)
    {
        var eng = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { new DetectorB(true, true) })
        { GetLevels = i => (IReadOnlyList<LevelVol>)levels[i] ?? Array.Empty<LevelVol>(), VirtualOpenRule = false };
        foreach (var b in bars) eng.Bars.Add(b);
        var sb = new StringBuilder("pos,datetime,session_no," + string.Join(",", BenzoSr.FixedNames));
        for (int k = 1; k <= BenzoSr.VclSlots; k++) sb.Append($",lo{k},hi{k},run{k}");
        sb.Append('\n');
        for (int i = 0; i < bars.Count; i++)
        {
            eng.Advance(i);
            var z = eng.Zones; var sr = z.Sr;
            sb.Append(i).Append(',').Append(bars[i].Time.ToString("yyyy-MM-dd HH:mm:ss", Inv)).Append(',').Append(z.SessionNo);
            foreach (var v in sr.Fx) sb.Append(',').Append(double.IsNaN(v) ? "" : v.ToString("R", Inv));
            for (int k = 0; k < BenzoSr.VclSlots; k++)
            {
                double lo = sr.SlotLoAt(k, i), hi = sr.SlotHiAt(k, i);
                sb.Append(',').Append(double.IsNaN(lo) ? "" : lo.ToString("R", Inv)).Append(',').Append(double.IsNaN(hi) ? "" : hi.ToString("R", Inv)).Append(',').Append(sr.SlotRunAt(k, i));
            }
            sb.Append('\n');
        }
        File.WriteAllText(outPath, sb.ToString(), new UTF8Encoding(false));
        Console.Error.WriteLine($"LEVELS: {bars.Count} nến -> {outPath}");
        return 0;
    }
    static double D(string s) => double.Parse(s, Inv);
}
