// VclReplayCsv — chạy VclCore (C#) trên file footprint export, KHÔNG cần Quantower, để đối chiếu với research/vcl4.py.
//   dotnet run -c Release --project vung-canh-lenh/tools/ReplayCsv -- <base> <out.csv>
//   <base> = đường dẫn bỏ đuôi (đọc <base>_bars.csv và <base>.csv).
// Xuất mỗi nến mỗi vùng hiển thị: bar_idx (vị trí 0..n-1), zone_id, lo, hi, role (R/RF/S/SF/K), score.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using VungCanhLenhNs;

static class Program
{
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
    static double D(string s) => double.Parse(s, Inv);

    static int Main(string[] args)
    {
        if (args.Length < 2) { Console.Error.WriteLine("cách dùng: VclReplayCsv <base> <out.csv>"); return 2; }
        string basePath = args[0], outPath = args[1];
        var bars = new List<VBar>();
        var barIdxOf = new List<int>();
        using (var rd = new StreamReader(basePath + "_bars.csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cT = Array.IndexOf(h, "datetime"), cO = Array.IndexOf(h, "open"), cH = Array.IndexOf(h, "high"),
                cL = Array.IndexOf(h, "low"), cC = Array.IndexOf(h, "close"), cV = Array.IndexOf(h, "volume");
            string line;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                var t = DateTime.ParseExact(f[cT], "yyyy-MM-dd HH:mm:ss", Inv, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal);
                bars.Add(new VBar { Time = t, O = D(f[cO]), H = D(f[cH]), L = D(f[cL]), C = D(f[cC]), Vol = D(f[cV]) });
                barIdxOf.Add(int.Parse(f[cI], Inv));
            }
        }
        var posOf = new Dictionary<int, int>();
        for (int k = 0; k < barIdxOf.Count; k++) posOf[barIdxOf[k]] = k;
        var levels = new List<VLevel>[bars.Count];
        using (var rd = new StreamReader(basePath + ".csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cP = Array.IndexOf(h, "price"), cV = Array.IndexOf(h, "volume");
            string line;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                if (!posOf.TryGetValue(int.Parse(f[cI], Inv), out int pos)) continue;
                (levels[pos] ??= new List<VLevel>()).Add(new VLevel(D(f[cP]), D(f[cV])));
            }
        }
        Console.Error.WriteLine($"nạp {bars.Count} nến M1");
        var core = new VclCore();
        var sb = new StringBuilder("bar_idx,zone_id,lo,hi,role,score\n");
        var sw = System.Diagnostics.Stopwatch.StartNew();
        for (int i = 0; i < bars.Count; i++)
        {
            core.Push(bars[i], (IReadOnlyList<VLevel>)levels[i] ?? Array.Empty<VLevel>());
            foreach (var z in core.Display)
            {
                string role = z.Slot == 'K' ? "K" : (z.Side > 0 ? "R" : "S") + (z.Slot == 'F' ? "F" : "");
                sb.Append(i).Append(',').Append(z.Id).Append(',').Append(z.Lo.ToString("R", Inv)).Append(',').Append(z.Hi.ToString("R", Inv))
                  .Append(',').Append(role).Append(',').Append(z.Score.ToString("R", Inv)).Append('\n');
            }
        }
        File.WriteAllText(outPath, sb.ToString());
        Console.Error.WriteLine($"xong {sw.Elapsed.TotalSeconds:0.0}s, tính lại bộ {core.NRecalc} lần → {outPath}");
        return 0;
    }
}
