// OfSignalsDump — chạy StackedImbalanceCalc + ExhaustionLogic (mã C# sản phẩm, không sửa) trên file export
// per-level, xuất từng vùng stacked / từng kiệt sức ra CSV để đối chiếu với benzo-trader/research/of_signals.py.
//
// Dùng:  dotnet run --project benzo-trader/tools/OfSignalsDump -c Release -- <levels.csv> <bars.csv> <maxBarIdx> <out.csv>
//   maxBarIdx: chỉ xét nến có bar_idx ≤ giá trị này (GĐ0: chỉ TRAIN, không đụng TEST).
//
// Dòng ra (giá đổi tick = round(giá/0,1); số thực in "R" = round-trip):
//   Z,cfg,bar,side,loIdx,hiIdx,lo,hi,levels,minRatio,dom,opp,pos,weak,touchOff,touchEnd,closeOff,closeEnd
//   E,bar,top,kind,tick,extVol,mean,seq(;),sweptOff
// touchOff/closeOff: Follow() trên tối đa 300 nến sau (maxBars 0 = không hết hạn), -1 = chưa kết thúc.
// sweptOff: nến sau đầu tiên (≤ 300) có IsSwept(sweepTicks 1), -1 = chưa bị quét.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using OrderFlowBubbles;

static class Program
{
    const double T = 0.1;
    const int Horizon = 300;
    static readonly CultureInfo Ci = CultureInfo.InvariantCulture;
    static string R(double x) => double.IsPositiveInfinity(x) ? "inf" : x.ToString("R", Ci);

    static int Main(string[] a)
    {
        if (a.Length < 4) { Console.Error.WriteLine("args: levels.csv bars.csv maxBarIdx out.csv"); return 2; }
        string fl = a[0], fb = a[1], fo = a[3];
        int maxBar = int.Parse(a[2]);

        var o = new List<long>(); var h = new List<long>(); var l = new List<long>(); var c = new List<long>();
        var oP = new List<double>(); var hP = new List<double>(); var lP = new List<double>(); var cP = new List<double>();
        foreach (var line in File.ReadLines(fb))
        {
            if (line.StartsWith("bar_idx")) continue;
            var p = line.Split(',');
            int bi = int.Parse(p[0]);
            if (bi > maxBar) break;
            if (bi != o.Count) throw new Exception("bar_idx khong lien tuc tai " + bi);
            double po = double.Parse(p[2], Ci), ph = double.Parse(p[3], Ci), pl = double.Parse(p[4], Ci), pc = double.Parse(p[5], Ci);
            oP.Add(po); hP.Add(ph); lP.Add(pl); cP.Add(pc);
            o.Add((long)Math.Round(po / T)); h.Add((long)Math.Round(ph / T)); l.Add((long)Math.Round(pl / T)); c.Add((long)Math.Round(pc / T));
        }
        int n = o.Count;
        var lv = new List<ExhLevel>[n];
        for (int i = 0; i < n; i++) lv[i] = new List<ExhLevel>();
        foreach (var line in File.ReadLines(fl))
        {
            if (line.StartsWith("bar_idx")) continue;
            int c1 = line.IndexOf(',');
            int bi = int.Parse(line.AsSpan(0, c1));
            if (bi > maxBar) break;
            var p = line.Split(',');   // bar_idx,datetime,price,bid_vol,ask_vol,volume,...
            long k = (long)Math.Round(double.Parse(p[2], Ci) / T);
            lv[bi].Add(new ExhLevel(k, double.Parse(p[3], Ci), double.Parse(p[4], Ci), double.Parse(p[5], Ci)));
        }

        var cfgs = new (string name, double pct, int run, double mv)[] { ("250_3_1", 250, 3, 1), ("250_4_5", 250, 4, 5), ("300_3_1", 300, 3, 1) };
        var ex = new ExhSettings();
        var sb = new StringBuilder();
        int nz = 0, ne = 0;
        for (int i = 0; i < n; i++)
        {
            // ---- stacked: mảng liên tiếp Low..High như OrderFlowBubbles ----
            if (h[i] > l[i])
            {
                int m = (int)(h[i] - l[i] + 1);
                var ask = new double[m]; var bid = new double[m];
                foreach (var x in lv[i]) if (x.Tick >= l[i] && x.Tick <= h[i]) { ask[x.Tick - l[i]] += x.Ask; bid[x.Tick - l[i]] += x.Bid; }
                var after = new List<(double, double, double)>();
                for (int j = i + 1; j < n && j <= i + Horizon; j++) after.Add((hP[j], lP[j], cP[j]));
                foreach (var cf in cfgs)
                {
                    foreach (var z in StackedImbalanceCalc.Detect(l[i] * T, T, ask, bid, cf.pct, cf.run, cf.mv))
                    {
                        StackedImbalanceCalc.Classify(z, oP[i], cP[i]);
                        var ft = StackedImbalanceCalc.Follow(z.Side, z.Lo, z.Hi, after, SiEndMode.Touch, 0);
                        var fc = StackedImbalanceCalc.Follow(z.Side, z.Lo, z.Hi, after, SiEndMode.CloseThrough, 0);
                        sb.Append("Z,").Append(cf.name).Append(',').Append(i).Append(',').Append(z.Side).Append(',')
                          .Append(z.LoIdx).Append(',').Append(z.HiIdx).Append(',').Append(R(z.Lo)).Append(',').Append(R(z.Hi)).Append(',')
                          .Append(z.Levels).Append(',').Append(R(z.MinRatio)).Append(',').Append(R(z.DomVolume)).Append(',').Append(R(z.OppVolume)).Append(',')
                          .Append((int)z.Position).Append(',').Append(z.Weak ? 1 : 0).Append(',')
                          .Append(ft.endOffset).Append(',').Append((int)ft.reason).Append(',').Append(fc.endOffset).Append(',').Append((int)fc.reason).Append('\n');
                        nz++;
                    }
                }
            }
            // ---- kiệt sức ----
            foreach (bool top in new[] { true, false })
            {
                var r = ExhaustionLogic.Detect(top, o[i], h[i], l[i], c[i], lv[i], ex);
                if (!r.Hit) continue;
                int swept = -1;
                for (int j = i + 1; j < n && j <= i + Horizon; j++)
                    if (ExhaustionLogic.IsSwept(r.Top, r.Tick, h[j], l[j], 1)) { swept = j - i; break; }
                sb.Append("E,").Append(i).Append(',').Append(top ? 1 : 0).Append(',').Append((int)r.Kind).Append(',').Append(r.Tick).Append(',')
                  .Append(R(r.ExtremeVol)).Append(',').Append(R(r.MeanLevelVol)).Append(',')
                  .Append(string.Join(";", r.Seq.Select(R))).Append(',').Append(swept).Append('\n');
                ne++;
            }
        }
        File.WriteAllText(fo, sb.ToString());
        Console.WriteLine($"{n} nen; {nz} dong vung stacked (3 cau hinh); {ne} dong kiet suc -> {fo}");
        return 0;
    }
}
