// ============================================================================
//  Golden test + benchmark cho lõi tính toán THẬT của OrderFlow Bubbles (2026-11-11)
// ============================================================================
//  Biên dịch THẲNG các file nguồn của indicator (không qua DLL) rồi chạy đúng class OrderFlowBubbles với
//  các đối tượng Quantower THẬT (HistoryItemBar / VolumeAnalysisData / VolumeAnalysisItem — dựng từ CSV
//  data-export/data-footprint/fp_GCZ26_XCEC_Time_*.csv). Phần duy nhất "giả lập" là nguồn nến: khe test
//  TestBarSource/TestBarCount/TestTickSize/TestCacheFile trong OrderFlowBubbles.cs (khi null = chạy như cũ).
//
//  Mỗi kịch bản xuất 2 dấu vân tay SHA-256:
//    state = mọi bóng (_bubbles: giá, hình, màu, cỡ, SizeFrac, tooltip, Confirm, PriceHi...), _barTint, vùng stacked
//            (_zones: Idx/EndIdx/End), _absRecs, _exhRecs, _cvd
//    cache = nội dung file niêm phong SAU KHI nạp lại (mỗi nến bản ghi thắng cuối, sắp theo thời gian, serialize lại)
//  So với perf/golden-expected.txt. Dùng:
//    dotnet run -c Release --project perf/Golden -- golden [--work DIR] [--baseline DIR] [--write-expected] [--dump]
//    dotnet run -c Release --project perf/Golden -- bench  [--work DIR] [--baseline DIR]
// ============================================================================
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using TradingPlatform.BusinessLayer;
using Ind = OrderFlowBubbles.OrderFlowBubbles;
using SC = OrderFlowBubbles.SignalCache;

namespace GoldenPerf
{
    static class Program
    {
        static readonly CultureInfo Inv = CultureInfo.InvariantCulture;
        const BindingFlags NP = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance;

        static string RepoRoot()
        {
            var d = new DirectoryInfo(AppContext.BaseDirectory);
            while (d != null && !Directory.Exists(Path.Combine(d.FullName, "data-export"))) d = d.Parent;
            return d?.FullName ?? throw new Exception("khong tim thay data-export");
        }

        static string Arg(string[] a, string name, string def)
        { int i = Array.IndexOf(a, name); return i >= 0 && i + 1 < a.Length ? a[i + 1] : def; }

        static int Main(string[] args)
        {
            string mode = args.Length > 0 ? args[0] : "golden";
            string root = RepoRoot();
            string perfDir = Path.Combine(root, "quantower-orderflow-indicator", "perf");
            string lvl = Arg(args, "--levels", Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv"));
            string barsCsv = lvl.Replace(".csv", "_bars.csv");
            string work = Arg(args, "--work", Path.Combine(Path.GetTempPath(), "ofb-golden"));
            string baseline = Arg(args, "--baseline", Path.Combine(work, "baseline"));
            Directory.CreateDirectory(work);
            if (mode == "realcache") return RealCache(work);
            Console.WriteLine($"data: {lvl}\nwork: {work}");
            var sw = Stopwatch.StartNew();
            var bars = LoadBars(lvl, barsCsv);
            Console.WriteLine($"da nap {bars.Count} nen trong {sw.ElapsedMilliseconds} ms");
            return mode == "bench" ? Bench(bars, work, baseline) : Golden(args, bars, work, baseline, perfDir);
        }

        // ---------------------------------------------------------------- nạp dữ liệu
        static List<HistoryItemBar> LoadBars(string lvlCsv, string barsCsv)
        {
            var bars = new List<HistoryItemBar>(); var byIdx = new Dictionary<int, HistoryItemBar>();
            bool first = true;
            foreach (var line in File.ReadLines(barsCsv))
            {
                if (first) { first = false; continue; }
                var p = line.Split(',');
                var t = DateTime.Parse(p[1], Inv);
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
            // kiểm tra nhanh: Delta của Quantower = buy - sell phải khớp cột delta
            var chk = bars[bars.Count / 2].VolumeAnalysisData.PriceLevels.Values.First();
            if (Math.Abs(chk.Delta - (chk.BuyVolume - chk.SellVolume)) > 1e-9) throw new Exception("Delta khong = buy - sell");
            return bars;
        }
        static double D(string s) => double.Parse(s, Inv);

        // ---------------------------------------------------------------- dựng indicator
        sealed class Run
        {
            public Ind Ind; public Action Process;
        }

        static Run Make(List<HistoryItemBar> bars, int off, int count, string cacheFile, Dictionary<string, object> cfg)
        {
            var ind = new Ind();
            if (cfg != null)
                foreach (var kv in cfg)
                {
                    var pi = typeof(Ind).GetProperty(kv.Key) ?? throw new Exception("khong co tham so " + kv.Key);
                    pi.SetValue(ind, Convert.ChangeType(kv.Value, pi.PropertyType, Inv));
                }
            ind.TestBarSource = i => bars[off + i];
            ind.TestBarCount = count;
            ind.TestTickSize = 0.1;
            ind.TestCacheFile = cacheFile;
            var m = typeof(Ind).GetMethod("Process", NP);
            return new Run { Ind = ind, Process = (Action)Delegate.CreateDelegate(typeof(Action), ind, m) };
        }

        // ---------------------------------------------------------------- dấu vân tay
        sealed class Dig
        {
            readonly IncrementalHash _h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
            public StreamWriter Dump; public List<string> Sample; public int SampleMax = 0; public long Lines;
            public void Line(string s)
            {
                _h.AppendData(Encoding.UTF8.GetBytes(s + "\n")); Lines++;
                Dump?.WriteLine(s);
                if (Sample != null && Sample.Count < SampleMax) Sample.Add(s.Replace("\n", "\\n").Replace("\r", "\\r"));
            }
            public string Final() => Convert.ToHexString(_h.GetHashAndReset());
        }

        static string V(object o)
        {
            switch (o)
            {
                case null: return "null";
                case Enum e: return e.ToString();
                case double d: return d.ToString("R", Inv);
                case bool b: return b ? "T" : "F";
                case string s: return "\"" + s + "\"";
                case Color c: return c.ToArgb().ToString(Inv);
                case IFormattable f: return f.ToString(null, Inv);
            }
            var sb = new StringBuilder("{");
            foreach (var f in o.GetType().GetFields(NP)) sb.Append(f.Name).Append('=').Append(V(f.GetValue(o))).Append(';');
            return sb.Append('}').ToString();
        }

        static string StateHash(Ind ind, Dig d)
        {
            object F(string n) => typeof(Ind).GetField(n, NP).GetValue(ind);
            var bubbles = (IDictionary)F("_bubbles");
            foreach (int k in bubbles.Keys.Cast<int>().OrderBy(x => x))
            {
                d.Line("B " + k);
                foreach (var b in (IEnumerable)bubbles[k]) d.Line(" " + V(b));
            }
            var tint = (IDictionary)F("_barTint");
            foreach (int k in tint.Keys.Cast<int>().OrderBy(x => x)) d.Line($"T {k} {tint[k]}");
            foreach (var z in (IEnumerable)F("_zones")) d.Line("Z " + V(z));
            foreach (var z in (IEnumerable)F("_absRecs")) d.Line("A " + V(z));
            foreach (var z in (IEnumerable)F("_exhRecs")) d.Line("E " + V(z));
            int ci = 0; foreach (var c in (IEnumerable)F("_cvd")) d.Line($"C {ci++} {V(c)}");
            return d.Final();
        }

        static string CacheHash(string path, out int n)
        {
            n = 0; if (string.IsNullOrEmpty(path) || !File.Exists(path)) return "nofile";
            var c = new SC(path); c.Load();
            var h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
            foreach (var x in c.Values.OrderBy(x => x.TimeTicks)) { h.AppendData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(x) + "\n")); n++; }
            return Convert.ToHexString(h.GetHashAndReset());
        }

        // ---------------------------------------------------------------- golden
        static int Golden(string[] args, List<HistoryItemBar> bars, string work, string baseline, string perfDir)
        {
            bool writeExpected = args.Contains("--write-expected"), dump = args.Contains("--dump");
            int N = bars.Count; var results = new List<string>(); var sample = new List<string>();

            void Report(string name, Run r, string cacheFile, bool wantSample = false)
            {
                var d = new Dig();
                if (dump) d.Dump = new StreamWriter(Path.Combine(work, name + ".digest.txt"));
                if (wantSample) { d.Sample = sample; d.SampleMax = 150; }
                string state = StateHash(r.Ind, d); d.Dump?.Dispose();
                string cache = CacheHash(cacheFile, out int keys);
                string line = $"{name} state={state} cache={cache} keys={keys} digestLines={d.Lines}";
                Console.WriteLine(line); results.Add(line);
            }
            string Fresh(string name) { string p = Path.Combine(work, name + ".jsonl"); if (File.Exists(p)) File.Delete(p); return p; }
            string CopyOf(string src, string name) { string p = Fresh(name); File.Copy(src, p); return p; }
            var sw = Stopwatch.StartNew();

            // S1: nạp NGUỘI toàn bộ 90 ngày, cấu hình mặc định, file cache mới
            string c1 = Fresh("S1");
            var r1 = Make(bars, 0, N, c1, null); r1.Ind.VolumeAnalysisData_Loaded();
            Console.WriteLine($"  (S1 nguoi: {sw.ElapsedMilliseconds} ms)"); sw.Restart();
            Report("S1-cold-default", r1, c1, wantSample: true);

            // S2: nạp ẤM từ file S1 (khôi phục)
            string c2 = CopyOf(c1, "S2");
            var r2 = Make(bars, 0, N, c2, null); r2.Ind.VolumeAnalysisData_Loaded();
            Report("S2-warm-from-S1", r2, c2);

            // S3: nạp ấm từ file cache do BẢN CŨ ghi (baseline/S1.jsonl) -> phải giống S2
            string old = Path.Combine(baseline, "S1.jsonl");
            if (File.Exists(old))
            {
                string c3 = CopyOf(old, "S3");
                var r3 = Make(bars, 0, N, c3, null); r3.Ind.VolumeAnalysisData_Loaded();
                Report("S3-warm-from-OLDfile", r3, c3);
            }
            else Console.WriteLine($"  (bo qua S3: chua co {old})");

            // S4: tăng dần — nạp 29.200 nến rồi thêm từng nến, mỗi nến gọi Process 3 lần (như nhiều tick)
            int sub = 30000, off = N - sub; string c4 = Fresh("S4");
            var r4 = Make(bars, off, sub - 800, c4, null); r4.Ind.VolumeAnalysisData_Loaded();
            for (int k = sub - 799; k <= sub; k++) { r4.Ind.TestBarCount = k; r4.Process(); r4.Process(); r4.Process(); }
            Report("S4-incremental", r4, c4);

            // S5: mọi tính năng bật (DLine/Divergence/Sweep/Unfinished/StopHunt), BaselineTopLevels=0 — 40.000 nến cuối
            int sub5 = 40000, off5 = N - sub5;
            var cfgB = new Dictionary<string, object> { ["DLineEnabled"] = true, ["DivergenceEnabled"] = true, ["SweepEnabled"] = true, ["UnfinishedEnabled"] = true, ["StopHuntEnabled"] = true, ["BaselineTopLevels"] = 0 };
            string c5 = Fresh("S5");
            var r5 = Make(bars, off5, sub5, c5, cfgB); r5.Ind.VolumeAnalysisData_Loaded();
            Report("S5-allfeatures", r5, c5);

            // S6: ấm của S5 (khôi phục khi bật hết)
            string c6 = CopyOf(c5, "S6");
            var r6 = Make(bars, off5, sub5, c6, cfgB); r6.Ind.VolumeAnalysisData_Loaded();
            Report("S6-warm-allfeatures", r6, c6);

            // S7: ngưỡng cố định + cửa sổ baseline 50 + DLine
            var cfgC = new Dictionary<string, object> { ["UseFixedThreshold"] = true, ["BaselineBars"] = 50, ["DLineEnabled"] = true };
            string c7 = Fresh("S7");
            var r7 = Make(bars, off5, sub5, c7, cfgC); r7.Ind.VolumeAnalysisData_Loaded();
            Report("S7-fixed-thr-dline", r7, c7);

            string resPath = Path.Combine(work, "golden-result.txt");
            File.WriteAllLines(resPath, results);
            string expPath = Path.Combine(perfDir, "golden-expected.txt");
            if (writeExpected)
            {
                File.WriteAllLines(expPath, results);
                File.WriteAllLines(Path.Combine(perfDir, "golden-sample.txt"), sample);
                Console.WriteLine($"da ghi {expPath}");
                return 0;
            }
            if (!File.Exists(expPath)) { Console.WriteLine("chua co golden-expected.txt"); return 2; }
            var exp = File.ReadAllLines(expPath).Where(l => l.Length > 0).ToDictionary(l => l.Split(' ')[0], l => l);
            int bad = 0;
            foreach (var l in results)
            {
                string key = l.Split(' ')[0];
                if (!exp.TryGetValue(key, out var e)) { Console.WriteLine("THIEU expected: " + key); bad++; continue; }
                var a = l.Split(' ').Take(3); var b = e.Split(' ').Take(3);
                if (!a.SequenceEqual(b)) { Console.WriteLine("LECH  " + key + "\n   hien tai: " + l + "\n   chuan   : " + e); bad++; }
            }
            Console.WriteLine(bad == 0 ? "=== GOLDEN: KHOP HET (hash == chuan) ===" : $"=== GOLDEN: {bad} LECH ===");
            return bad == 0 ? 0 : 1;
        }

        // ---------------------------------------------------------------- bench
        static int Bench(List<HistoryItemBar> bars, string work, string baseline)
        {
            int N = bars.Count;
            string old = Path.Combine(baseline, "S1.jsonl");
            long Time(Action a) { var s = Stopwatch.StartNew(); a(); return s.ElapsedMilliseconds; }
            string Fresh(string n) { string p = Path.Combine(work, n + ".jsonl"); if (File.Exists(p)) File.Delete(p); if (File.Exists(p + ".tmp")) File.Delete(p + ".tmp"); return p; }

            Console.WriteLine("--- A) NGUOI, KHONG ghi file (chi tinh) ---");
            for (int rep = 0; rep < 2; rep++)
            { GC.Collect(); var r = Make(bars, 0, N, "", null); Console.WriteLine($"  lan {rep + 1}: {Time(() => r.Ind.VolumeAnalysisData_Loaded())} ms"); }

            Console.WriteLine("--- B) NGUOI, CO ghi file niem phong ---");
            string cb = null;
            for (int rep = 0; rep < 2; rep++)
            {
                GC.Collect(); cb = Fresh("B"); var r = Make(bars, 0, N, cb, null);
                long ms = Time(() => r.Ind.VolumeAnalysisData_Loaded());
                Console.WriteLine($"  lan {rep + 1}: {ms} ms  | file {new FileInfo(cb).Length / 1048576} MB, {File.ReadLines(cb).Count()} dong");
            }

            Console.WriteLine("--- C) AM: khoi phuc tu file vua ghi (bar + Load + Process) ---");
            for (int rep = 0; rep < 3; rep++)
            {
                string cc = Path.Combine(work, "C.jsonl"); File.Copy(cb, cc, true); GC.Collect();
                long[] parts = new long[2]; Run r = null;
                var sw = Stopwatch.StartNew();
                r = Make(bars, 0, N, cc, null); r.Ind.VolumeAnalysisData_Loaded();
                Console.WriteLine($"  lan {rep + 1}: {sw.ElapsedMilliseconds} ms (gom doc cache + khoi phuc)");
            }

            Console.WriteLine("--- D) DOC CACHE rieng (SignalCache.Load) tren file do BAN CU ghi (baseline/S1.jsonl) ---");
            if (File.Exists(old))
            {
                Console.WriteLine($"  baseline: {new FileInfo(old).Length / 1048576} MB, {File.ReadLines(old).Count()} dong");
                string cd = Path.Combine(work, "D.jsonl"); File.Copy(old, cd, true);
                for (int rep = 0; rep < 4; rep++)
                {
                    GC.Collect(); var c = new SC(cd);
                    var s = Stopwatch.StartNew(); Load(c, true); long ms = s.ElapsedMilliseconds;
                    Console.WriteLine($"  Load lan {rep + 1}: {ms} ms, {c.Count} nen, file nay: {new FileInfo(cd).Length / 1048576} MB, {File.ReadLines(cd).Count()} dong");
                }
            }
            else Console.WriteLine($"  (chua co {old})");
            return 0;
        }

        // ---------------------------------------------------------------- đọc cache THẬT của người dùng (bản sao)
        static int RealCache(string work)
        {
            string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "OrderFlowBubbles", "signal-cache");
            int bad = 0;
            foreach (var f in Directory.GetFiles(dir, "*.jsonl").OrderBy(x => new FileInfo(x).Length))
            {
                long len = new FileInfo(f).Length; if (len > 200_000_000) { Console.WriteLine($"bo qua {Path.GetFileName(f)} ({len / 1048576} MB > 200 MB)"); continue; }
                string cp = Path.Combine(work, "real.jsonl"); File.Copy(f, cp, true);
                // tham chiếu = cách đọc CỦA BẢN GỐC
                var sw = Stopwatch.StartNew();
                var map = new Dictionary<long, OrderFlowBubbles.CachedBarData>(); int lines = 0;
                foreach (var line in File.ReadLines(cp))
                {
                    if (string.IsNullOrWhiteSpace(line)) continue; lines++;
                    OrderFlowBubbles.CachedBarData d; try { d = JsonSerializer.Deserialize<OrderFlowBubbles.CachedBarData>(line); } catch { continue; }
                    if (d != null) map[d.TimeTicks] = d;
                }
                long tOld = sw.ElapsedMilliseconds;
                string H(IEnumerable<OrderFlowBubbles.CachedBarData> all) { var h = IncrementalHash.CreateHash(HashAlgorithmName.SHA256); foreach (var x in all.OrderBy(x => x.TimeTicks)) h.AppendData(Encoding.UTF8.GetBytes(JsonSerializer.Serialize(x) + (char)10)); return Convert.ToHexString(h.GetHashAndReset())[..16]; }
                string hOld = H(map.Values);
                sw.Restart(); var c = new SC(cp); Load(c, false); long tNew = sw.ElapsedMilliseconds; string hNew = H(c.Values);
                sw.Restart(); var c2 = new SC(cp); Load(c2, true); long tCmp = sw.ElapsedMilliseconds;
                var c3 = new SC(cp); Load(c3, false); string hCmp = H(c3.Values);
                int linesAfter = File.ReadLines(cp).Count(l => !string.IsNullOrWhiteSpace(l));
                bool ok = hOld == hNew && hOld == hCmp;
                if (!ok) bad++;
                Console.WriteLine($"{(ok ? "OK  " : "LECH")} {Path.GetFileName(f)} {len / 1048576} MB: {lines} dong -> {map.Count} nen | doc cu {tOld} ms, moi {tNew} ms, moi+nen {tCmp} ms | sau nen {linesAfter} dong | hash {hOld} {hNew} {hCmp}");
            }
            Console.WriteLine(bad == 0 ? "=== REAL CACHE: KHOP ===" : $"=== REAL CACHE: {bad} LECH ===");
            return bad == 0 ? 0 : 1;
        }

        // Load(compact:true) nếu bản mới có tham số này, còn không (bản cũ) gọi Load() thường.
        static void Load(SC c, bool compact)
        {
            var m = typeof(SC).GetMethod("Load", new[] { typeof(bool) });
            if (m != null) m.Invoke(c, new object[] { compact }); else c.Load();
        }
    }
}
