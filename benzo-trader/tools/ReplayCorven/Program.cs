// ReplayCorven — chạy DetectorCorven (mã C# sản phẩm) trên file Footprint Export, ghi CSV để
// benzo-trader/research/parity_corven.py đối chiếu với setup_corven.py (plan BENZO-CORVEN 10.6).
//
// Dùng:  dotnet run --project benzo-trader/tools/ReplayCorven -c Release -- <prefix> <outdir> [--maxbar N] [--deny-below K] [--no-block-us]
//   prefix     : .../fp_GCZ26_XCEC_Time_20260723-20261021_90d   (đọc <prefix>_bars.csv + <prefix>.csv)
//   --maxbar   : chỉ nạp nến bar_idx ≤ N
//   --deny-below: nến < K không được vào lệnh (= phiên mỏng Python lọc bằng `good`)
//   --hide-after: lệnh có nến vào > N ghi TRỐNG cột ket_cuc/r/exit_idx (phần TEST — kết cục không rời tiến trình)
// Ra: <outdir>/cs_trades.csv (mọi lệnh, kể cả kết cục) + <outdir>/cs_cands.csv (mọi CF qua ②: dấu hiệu, cổng, giá).
// ⚠ Tool KHÔNG in thống kê R/WR. Với --hide-after, 3 cột kết cục (ket_cuc/r/exit_idx) của mọi lệnh sau nến cut được ghi TRỐNG ngay
//   trong tiến trình (CorvenData.TradesCsv); parity_corven.py còn kiểm lại và raise nếu thấy ô không rỗng (khoá 2 lớp, plan 12.1 #1).
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
        if (a.Length < 2) { Console.Error.WriteLine("args: prefix outdir [--maxbar N] [--deny-below K] [--no-block-us] [--sl-kieu-cu]"); return 2; }
        string prefix = a[0], outDir = a[1];
        int maxBar = -1, deny = 0, hideAfter = int.MaxValue; bool blockUs = true, slKieuCu = false;
        for (int k = 2; k < a.Length; k++)
        {
            if (a[k] == "--maxbar") maxBar = int.Parse(a[++k], Ci);
            else if (a[k] == "--deny-below") deny = int.Parse(a[++k], Ci);
            else if (a[k] == "--no-block-us") blockUs = false;
            else if (a[k] == "--sl-kieu-cu") slKieuCu = true;       // Settings "SL kiểu cũ" = SL Break + trần SL như corven-5
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
        var (eng, det) = CorvenData.Run(bars, levels, 0.1, deny, blockUs, null, cfg: CorvenCfg.KieuCu_(slKieuCu, new CorvenCfg()), onBar: (i, d) =>
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

        File.WriteAllText(Path.Combine(outDir, "cs_trades.csv"), CorvenData.TradesCsv(eng.Signals, timeIdx, hideAfter), new UTF8Encoding(false));
        Console.WriteLine($"{bars.Count} nến · {nc} ứng viên · {eng.Signals.Count} lệnh · huỷ (nến cuối phiên) {CorvenData.LastCancelled} → {outDir} ({sw.Elapsed.TotalSeconds:0.0}s)");
        return 0;
    }
}
