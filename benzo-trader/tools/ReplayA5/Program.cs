// ReplayA5 — chạy setup A "Phá hồi v5" (DetectorA5) của C# trên file footprint export, KHÔNG cần Quantower, để đối chiếu với
// research/setup_a_v5.py (xem research/parity_a_v5.py).
//   dotnet run -c Release --project benzo-trader/tools/ReplayA5 -- <base> <outprefix> [--novcl] [--bad <file>]
//   <base>      = đường dẫn bỏ đuôi (đọc <base>_bars.csv và <base>.csv)
//   --novcl     = DetectorA5(useVcl:false) (= A-v4)
//   --bad <f>   = file giờ MỞ nến UTC "xấu" (mỗi dòng yyyy-MM-dd HH:mm:ss; = P.bad của Python: chỗ nối hợp đồng | phiên mỏng);
//                 IsNewsBlocked = bad.Contains(giờ đóng − 1 phút) ⇒ đúng okbar của Python, so được TOÀN file.
// Ghi 5 file: <out>_levels.csv · _raw.csv · _states.csv · _sim.csv (1 lệnh mở, KHÔNG chặn mở ảo) · _live.csv (1 lệnh mở, CÓ chặn mở ảo).
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
    static string R(double v) => double.IsNaN(v) ? "" : v.ToString("R", Inv);
    static string T(DateTime t) => t.ToString("yyyy-MM-dd HH:mm:ss", Inv);
    static double D(string s) => double.Parse(s, Inv);

    static int Main(string[] args)
    {
        if (args.Length < 2) { Console.Error.WriteLine("cách dùng: ReplayA5 <base> <outprefix> [--novcl] [--bad <file>]"); return 2; }
        string basePath = args[0], outPrefix = args[1];
        bool novcl = args.Contains("--novcl");
        HashSet<DateTime> bad = null;
        int bi = Array.IndexOf(args, "--bad");
        if (bi >= 0 && bi + 1 < args.Length)
        {
            bad = new HashSet<DateTime>();
            foreach (var l in File.ReadLines(args[bi + 1]))
                if (DateTime.TryParseExact(l.Trim(), "yyyy-MM-dd HH:mm:ss", Inv, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out var t)) bad.Add(t);
        }
        Func<DateTime, bool> blocked = bad == null ? (_ => false) : (t => bad.Contains(t.AddMinutes(-1)));

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
                bars.Add(new BarData { Idx = n, Time = t, O = D(f[cO]), H = D(f[cH]), L = D(f[cL]), C = D(f[cC]), Vol = D(f[cV]), Delta = D(f[cD]), SellVol = D(f[cB]), BuyVol = D(f[cA]) });
                barIdxOf.Add(int.Parse(f[cI], Inv)); n++;
            }
        }
        var posOf = new Dictionary<int, int>();
        for (int k = 0; k < barIdxOf.Count; k++) posOf[barIdxOf[k]] = k;
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
                if (!posOf.TryGetValue(int.Parse(f[cI], Inv), out int pos)) continue;
                (levels[pos] ??= new List<LevelVol>()).Add(new LevelVol(D(f[cP]), D(f[cB]), D(f[cA]), D(f[cV])));
            }
        }
        Console.Error.WriteLine($"nạp {bars.Count} nến M1, {levels.Count(l => l != null)} nến có per-level; nến xấu: {(bad == null ? 0 : bad.Count)}; {(novcl ? "A-v4 (không VCL)" : "A-v5 (có VCL)")}");
        Func<int, IReadOnlyList<LevelVol>> getLv = i => (IReadOnlyList<LevelVol>)levels[i] ?? Array.Empty<LevelVol>();

        // ---------------- (1) chạy tay: mức theo phiên + tín hiệu raw + nhật ký trạng thái (KHÔNG engine, không chặn mở ảo)
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var det = new DetectorA5(!novcl) { VirtualOpenBlock = false, StateLog = new List<A5StateLog>() };
            var zones = new BenzoZones();
            var view = new ClosedBars(bars);
            var ctx = new SetupContext { Symbol = "GCZ26", Tick = 0.1, Bars = view, Signals = new List<Signal>(), Zones = zones, GetLevels = getLv, IsNewsBlocked = blocked };
            var lv = new StringBuilder("session_start_utc,hvn_w,hvn_d,vah_d,val_d\n");
            var raw = new StringBuilder("time_utc,pos,side,entry,sl,tp,zone,E,p0,pk_pos,pk_val,L,pbmax,npb,brk_no,ent_no,zlo,zhi\n");
            int nsig = 0;
            for (int i = 0; i < bars.Count; i++)
            {
                view.Limit = i + 1;
                zones.Push(i, bars[i], getLv(i));
                det.Observe(ctx, i);
                if (zones.NewSession)
                {
                    var c = det.CurrentLevels;
                    lv.Append(T(bars[i].Time)).Append(',').Append(string.Join(";", c.HvnW.Select(x => $"{R(x.p)}:{R(x.lo)}:{R(x.hi)}"))).Append(',')
                      .Append(string.Join(";", c.HvnD.Select(R))).Append(',').Append(R(c.Vah)).Append(',').Append(R(c.Val)).Append('\n');
                }
                var s = det.TryDetect(ctx, i);
                if (s == null) continue;
                var f = det.LastInfo; nsig++;
                raw.Append(T(bars[i].Time)).Append(',').Append(i).Append(',').Append(s.Side).Append(',').Append(R(s.Entry)).Append(',').Append(R(s.Sl)).Append(',').Append(R(s.Tp)).Append(',')
                   .Append(s.Zone).Append(',').Append(R(f.E)).Append(',').Append(f.P0).Append(',').Append(f.PkPos).Append(',').Append(R(f.PkVal)).Append(',').Append(R(f.L)).Append(',')
                   .Append(R(f.Pbmax)).Append(',').Append(f.Npb).Append(',').Append(f.BrkNo).Append(',').Append(f.EntNo).Append(',').Append(R(f.ZLo)).Append(',').Append(R(f.ZHi)).Append('\n');
            }
            det.FlushEnd();
            var st = new StringBuilder("zone,S,p0,pk_pos,pk_val,E,why,armed,n_ent,brk_no\n");
            foreach (var x in det.StateLog)
                st.Append(x.Zone).Append(',').Append(x.S).Append(',').Append(x.P0).Append(',').Append(x.PkPos).Append(',').Append(R(x.PkVal)).Append(',').Append(R(x.E)).Append(',')
                  .Append(x.Why).Append(',').Append(x.Armed ? 1 : 0).Append(',').Append(x.NEnt).Append(',').Append(x.BrkNo).Append('\n');
            File.WriteAllText(outPrefix + "_levels.csv", lv.ToString(), new UTF8Encoding(false));
            File.WriteAllText(outPrefix + "_raw.csv", raw.ToString(), new UTF8Encoding(false));
            File.WriteAllText(outPrefix + "_states.csv", st.ToString(), new UTF8Encoding(false));
            Console.Error.WriteLine($"raw: {nsig} tín hiệu, {det.StateLog.Count} trạng thái kết thúc ({sw.Elapsed.TotalSeconds:0.0}s)");
        }

        // ---------------- (2) engine thật, 1 lệnh mở: sim (không chặn mở ảo) và live (có chặn mở ảo)
        foreach (var mode in new[] { "sim", "live" })
        {
            bool live = mode == "live";
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var det = new DetectorA5(!novcl) { VirtualOpenBlock = live };
            var eng = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det }) { GetLevels = getLv, IsNewsBlocked = blocked, VirtualOpenRule = live };
            foreach (var b in bars) eng.Bars.Add(b);
            eng.Advance(bars.Count - 1);
            var sb = new StringBuilder("time_utc,side,entry,sl,tp,zone,outcome,exit_utc,r\n");
            int closed = 0;
            foreach (var g in eng.Signals)
            {
                if (g.IsClosed) closed++;
                sb.Append(T(g.Time)).Append(',').Append(g.Side).Append(',').Append(R(g.Entry)).Append(',').Append(R(g.Sl)).Append(',').Append(R(g.Tp)).Append(',').Append(g.Zone).Append(',')
                  .Append(g.Outcome).Append(',').Append(g.IsClosed ? T(g.ExitTime) : "").Append(',').Append(g.IsClosed ? R(g.R) : "").Append('\n');
            }
            File.WriteAllText(outPrefix + "_" + mode + ".csv", sb.ToString(), new UTF8Encoding(false));
            Console.Error.WriteLine($"{mode}: {eng.Signals.Count} lệnh ({closed} đã đóng) ({sw.Elapsed.TotalSeconds:0.0}s)");
        }
        return 0;
    }
}
