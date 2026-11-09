// ReplayCorven — chạy DetectorCorven (mã C# sản phẩm) trên file Footprint Export, ghi CSV để
// benzo-trader/research/parity_corven.py đối chiếu với setup_corven.py (plan BENZO-CORVEN 10.6).
//
// Dùng:  dotnet run --project benzo-trader/tools/ReplayCorven -c Release -- <prefix> <outdir> [--maxbar N] [--deny-below K] [--no-block-us]
//   prefix     : .../fp_GCZ26_XCEC_Time_20260723-20261021_90d   (đọc <prefix>_bars.csv + <prefix>.csv)
//   --maxbar   : chỉ nạp nến bar_idx ≤ N
//   --deny-below: nến < K không được vào lệnh (= phiên mỏng Python lọc bằng `good`)
//   --hide-after: lệnh có nến vào > N ghi TRỐNG cột ket_cuc/r/exit_idx (phần TEST — kết cục không rời tiến trình)
// Ra: <outdir>/cs_trades.csv (mọi lệnh, kể cả kết cục) + <outdir>/cs_cands.csv (mọi CF qua ②: dấu hiệu, cổng, giá).
// ⚠ Tool KHÔNG in thống kê R/WR. Cột kết cục của phần TEST do parity_corven.py bỏ trước khi so (giữ TEST nguyên vẹn).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using BenzoTraderNs;

static class Program
{
    static readonly CultureInfo Ci = CultureInfo.InvariantCulture;
    static string R(double x) => x.ToString("R", Ci);
    static string Q(string s) => SignalCsv.Q(s);

    static int Main(string[] a)
    {
        if (a.Length < 2) { Console.Error.WriteLine("args: prefix outdir [--maxbar N] [--deny-below K] [--no-block-us]"); return 2; }
        string prefix = a[0], outDir = a[1];
        int maxBar = -1, deny = 0, hideAfter = int.MaxValue; bool blockUs = true;
        for (int k = 2; k < a.Length; k++)
        {
            if (a[k] == "--maxbar") maxBar = int.Parse(a[++k], Ci);
            else if (a[k] == "--deny-below") deny = int.Parse(a[++k], Ci);
            else if (a[k] == "--no-block-us") blockUs = false;
            else if (a[k] == "--hide-after") hideAfter = int.Parse(a[++k], Ci);
        }
        Directory.CreateDirectory(outDir);
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var (bars, levels) = CorvenData.Load(prefix, maxBar);
        Console.WriteLine($"nạp {bars.Count} nến ({sw.Elapsed.TotalSeconds:0.0}s)");
        var timeIdx = new Dictionary<long, int>();
        for (int i = 0; i < bars.Count; i++) timeIdx[bars[i].Time.Ticks] = i;

        var cs = new StringBuilder("cf,t_utc,the,side,rid,b_from_exhausted,n,loai,dau_hieu,gates,entry,sl,tp,r_san,moc\n");
        int nc = 0;
        var (eng, det) = CorvenData.Run(bars, levels, 0.1, deny, blockUs, null, (i, d) =>
        {
            if (i < deny) return;
            foreach (var c in d.LastCandidates)
            {
                cs.Append(c.Cf).Append(',').Append(bars[c.Cf].Time.ToString("yyyy-MM-dd HH:mm", Ci)).Append(',').Append(c.The).Append(',')
                  .Append(c.S > 0 ? "buy" : "sell").Append(',').Append(c.Rid).Append(',').Append(c.Exhausted ? 1 : 0).Append(',')
                  .Append(c.NTypes).Append(',').Append(Q(c.TypesText)).Append(',').Append(Q(c.SignsText)).Append(',')
                  .Append(string.Join(";", c.Gates)).Append(',').Append(c.Entry).Append(',').Append(c.Sl).Append(',').Append(R(c.Tp)).Append(',')
                  .Append(Math.Round(c.RAvail, 2).ToString("R", Ci)).Append(',').Append(Q(c.MocUsed)).Append('\n');
                nc++;
            }
        });
        File.WriteAllText(Path.Combine(outDir, "cs_cands.csv"), cs.ToString(), new UTF8Encoding(false));

        var ts = new StringBuilder("idx,t_utc,the,side,range_id,b_from_exhausted,moc,so_dau_hieu,loai,dau_hieu,entry,sl,tp,r_san,ket_cuc,r,exit_idx\n");
        foreach (var s in eng.Signals)
        {
            int ex = s.IsClosed && timeIdx.TryGetValue(s.ExitTime.Ticks, out int e) ? e : -1;
            bool hide = s.BarIdx > hideAfter;     // phần TEST: kết cục không bao giờ rời tiến trình
            string outc = hide ? "" : s.Outcome, rr = hide || !s.IsClosed ? "" : Math.Round(s.R, 3).ToString("R", Ci), exs = hide ? "" : ex.ToString(Ci);
            ts.Append(s.BarIdx).Append(',').Append(s.Time.ToString("yyyy-MM-dd HH:mm", Ci)).Append(',').Append(s.Setup).Append(',')
              .Append(s.Side > 0 ? "buy" : "sell").Append(',').Append(s.RangeId).Append(',').Append(s.BFromExhausted ? 1 : 0).Append(',')
              .Append(Q(s.Zone)).Append(',').Append(s.NSigns).Append(',').Append(Q(s.SignTypes)).Append(',').Append(Q(s.Signs)).Append(',')
              .Append(R(s.Entry)).Append(',').Append(R(s.Sl)).Append(',').Append(R(s.Tp)).Append(',').Append(Math.Round(s.RAvail, 2).ToString("R", Ci)).Append(',')
              .Append(s.Outcome).Append(',').Append(s.IsClosed ? Math.Round(s.R, 3).ToString("R", Ci) : "").Append(',').Append(ex).Append('\n');
        }
        File.WriteAllText(Path.Combine(outDir, "cs_trades.csv"), ts.ToString(), new UTF8Encoding(false));
        Console.WriteLine($"{bars.Count} nến · {nc} ứng viên · {eng.Signals.Count} lệnh → {outDir} ({sw.Elapsed.TotalSeconds:0.0}s)");
        return 0;
    }
}
