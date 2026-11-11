// Test cho các tối ưu hiệu năng 2026-11-11 (xem research/PERF-RESEARCH-2026-11-11.md, perf/README.md):
//  - RollingRobust mới (mảng sắp xếp cuốn + MAD merge-walk) phải TRÙNG TỪNG BIT với bản gốc
//  - SignalCache ghi theo lô phải cho cùng kết quả Load() như ghi từng dòng (dòng sau thắng)
//  - Load đường nhanh (chỉ mục byte + bộ sinh sẵn) == đọc từng dòng kiểu cũ, kể cả dòng hỏng/CRLF/BOM
//  - Nén file giữ nguyên bản ghi thắng
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using OrderFlowBubbles;

static class PerfTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // ---- bản gốc RollingRobust (sao NGUYÊN VĂN từ OrderFlowBubbles.cs trước perf) ----
    sealed class LegacyRollingRobust
    {
        private readonly Queue<double[]> _bars = new();
        private readonly int _window;
        private double _median, _mad;
        private bool _dirty = true;
        private int _valueCount;
        public LegacyRollingRobust(int window) { _window = Math.Max(1, window); }
        public int BarCount => _bars.Count;
        public void AddBar(double[] vals)
        {
            if (vals == null) vals = Array.Empty<double>();
            _bars.Enqueue(vals);
            _valueCount += vals.Length;
            while (_bars.Count > _window) { var d = _bars.Dequeue(); _valueCount -= d.Length; }
            _dirty = true;
        }
        private void Recompute()
        {
            _dirty = false;
            if (_valueCount == 0) { _median = 0; _mad = 0; return; }
            var all = new double[_valueCount];
            int k = 0;
            foreach (var arr in _bars) { Array.Copy(arr, 0, all, k, arr.Length); k += arr.Length; }
            Array.Sort(all);
            _median = Med(all);
            var dev = new double[all.Length];
            for (int i = 0; i < all.Length; i++) dev[i] = Math.Abs(all[i] - _median);
            Array.Sort(dev);
            _mad = Med(dev);
        }
        private static double Med(double[] s)
        {
            int len = s.Length;
            if (len <= 0) return 0;
            int mid = len / 2;
            return (len % 2 == 1) ? s[mid] : 0.5 * (s[mid - 1] + s[mid]);
        }
        public double Median { get { if (_dirty) Recompute(); return _median; } }
        public double ModZ(double x)
        {
            if (_dirty) Recompute();
            if (_mad > 1e-9) return 0.6745 * (x - _median) / _mad;
            if (_median > 1e-9) return (x - _median) / _median;
            return 0;
        }
    }

    static long Bits(double d) => BitConverter.DoubleToInt64Bits(d);
    static double Gauss(Random r) { double u1 = 1 - r.NextDouble(), u2 = r.NextDouble(); return Math.Sqrt(-2 * Math.Log(u1)) * Math.Cos(2 * Math.PI * u2); }

    static void RobustBitExact()
    {
        Console.WriteLine("[P1] RollingRobust moi == ban goc TUNG BIT (Median + ModZ)");
        var rnd = new Random(12345);
        // (ten, so gia tri/nen toi da, kieu du lieu, cua so)
        var kinds = new (string name, int per, int kind, int window)[] {
            ("int top3", 3, 0, 100), ("int ~18/nen", 18, 0, 100), ("int ~50/nen", 50, 0, 100), ("double", 12, 1, 100),
            ("per-bar 1 gia tri", 1, 1, 100), ("nhieu trung lap (0/1/2)", 20, 2, 100), ("cua so nho 3", 5, 0, 3), ("cua so 1", 4, 1, 1), ("rong xen ke", 6, 3, 50)
        };
        foreach (var (name, per, kind, window) in kinds)
        {
            var a = new LegacyRollingRobust(window); var b = new RollingRobust(window);
            long diff = 0, n = 0;
            for (int i = 0; i < 4000; i++)
            {
                int len = kind == 3 ? (i % 3 == 0 ? 0 : rnd.Next(1, per + 1)) : (per == 1 ? 1 : rnd.Next(1, per + 1));
                var v = new double[len];
                for (int j = 0; j < len; j++)
                    v[j] = kind switch { 0 => Math.Floor(Math.Abs(Gauss(rnd)) * 30), 1 => Math.Abs(Gauss(rnd) * 17.3 + 4), 2 => rnd.Next(0, 3), _ => rnd.Next(0, 100) / 4.0 };
                a.AddBar((double[])v.Clone()); b.AddBar(v);
                if (a.BarCount != b.BarCount) diff++;
                // hỏi vài lần (có lúc bỏ qua để _dirty tích luỹ nhiều AddBar)
                if (i % 7 == 3) continue;
                foreach (double q in new[] { 0.0, 1.0, 5.0, 17.3, 123.0, -2.0 })
                {
                    n++;
                    if (Bits(a.Median) != Bits(b.Median)) diff++;
                    if (Bits(a.ModZ(q)) != Bits(b.ModZ(q))) diff++;
                }
            }
            Check(diff == 0, $"{name} (cua so {window}): {n} cau hoi, 0 lech bit", $"diff={diff}");
        }
    }

    static CachedBarData Rand(Random r, long t)
    {
        var d = new CachedBarData { TimeTicks = t, Tint = r.Next(-1, 2), SettingsFingerprint = "fp" + r.Next(0, 3) };
        int nb = r.Next(0, 4);
        for (int i = 0; i < nb; i++)
            d.Bubbles.Add(new CachedBubbleData { Price = 4000 + r.Next(0, 5000) / 10.0, Shape = r.Next(0, 8), ColorArgb = r.Next(), Size = r.Next(8, 26), Transparency = 10, UseBarWidth = r.Next(2) == 0,
                SizeFrac = r.NextDouble(), Tooltip = "Hàng lớn · gấp " + r.NextDouble() + " lần ✓", Confirm = r.Next(-1, 2), Confirmable = r.Next(2) == 0, PriceHi = r.Next(0, 5000) / 10.0, ZoneSide = r.Next(-1, 2) });
        return d;
    }

    static string Norm(IEnumerable<CachedBarData> all) => string.Join("\n", all.OrderBy(x => x.TimeTicks).Select(x => JsonSerializer.Serialize(x)));

    // Đọc kiểu BẢN GỐC (tham chiếu)
    static Dictionary<long, CachedBarData> ReferenceLoad(string path)
    {
        var map = new Dictionary<long, CachedBarData>();
        foreach (var line in File.ReadLines(path))
        {
            if (string.IsNullOrWhiteSpace(line)) continue;
            CachedBarData d;
            try { d = JsonSerializer.Deserialize<CachedBarData>(line); } catch { continue; }
            if (d != null) map[d.TimeTicks] = d;
        }
        return map;
    }

    static void BatchEqualsPerLine()
    {
        Console.WriteLine("[P2] Ghi theo lo == ghi tung dong (Load ra cung du lieu), co ghi de + Flush giua chung");
        var rnd = new Random(7);
        string pa = Path.Combine(Path.GetTempPath(), "pt_batch_" + Guid.NewGuid() + ".jsonl");
        string pb = Path.Combine(Path.GetTempPath(), "pt_line_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var batch = new SignalCache(pa);
            var puts = new List<CachedBarData>();
            for (int i = 0; i < 12000; i++) puts.Add(Rand(rnd, rnd.Next(0, 3000)));   // nhiều lần ghi đè cùng nến
            for (int i = 0; i < puts.Count; i++)
            {
                batch.Put(puts[i]);
                if (rnd.Next(0, 900) == 0) batch.Flush();
            }
            batch.Flush();
            // tham chiếu: ghi từng dòng đúng kiểu cũ
            foreach (var d in puts) File.AppendAllText(pb, JsonSerializer.Serialize(d) + Environment.NewLine);
            var ca = new SignalCache(pa); ca.Load();
            var cb = new SignalCache(pb); cb.Load();
            Check(Norm(ca.Values) == Norm(cb.Values), $"Load() batch == Load() tung dong ({ca.Count} nen)", $"{ca.Count} vs {cb.Count}");
            Check(Norm(batch.Values) == Norm(ca.Values), "bo nho instance ghi == file doc lai");
            Check(new FileInfo(pa).Length < new FileInfo(pb).Length, "file batch nho hon (it dong ghi de)", $"{new FileInfo(pa).Length} < {new FileInfo(pb).Length}");
            Check(batch.PendingCount == 0, "het hang doi sau Flush");
            // định dạng dòng giống hệt bản cũ (bộ sinh sẵn == phản chiếu)
            string first = File.ReadLines(pa).First();
            var parsed = JsonSerializer.Deserialize<CachedBarData>(first);
            Check(first == JsonSerializer.Serialize(parsed), "dong ghi (bo sinh san) == JsonSerializer.Serialize phan chieu");
            // Put trùng liên tiếp chỉ ra 1 dòng
            string pc = Path.Combine(Path.GetTempPath(), "pt_dup_" + Guid.NewGuid() + ".jsonl");
            var dup = new SignalCache(pc);
            for (int i = 0; i < 5; i++) dup.Put(Rand(rnd, 42));
            dup.Flush();
            Check(File.ReadLines(pc).Count() == 1, "5 lan Put cung nen -> 1 dong");
            File.Delete(pc);
            // tự flush khi đủ FlushEvery
            string pd = Path.Combine(Path.GetTempPath(), "pt_auto_" + Guid.NewGuid() + ".jsonl");
            var auto = new SignalCache(pd);
            for (int i = 0; i < SignalCache.FlushEvery + 10; i++) auto.Put(Rand(rnd, 100000 + i));
            Check(File.Exists(pd) && auto.PendingCount == 10, "tu flush khi du FlushEvery", $"pending={auto.PendingCount}");
            File.Delete(pd);
        }
        finally { File.Delete(pa); File.Delete(pb); }
    }

    static void FastLoadEqualsReference()
    {
        Console.WriteLine("[P3] Load duong nhanh == doc kieu cu (dong hong, ghi do, CRLF, BOM, dong trang, dong la)");
        var rnd = new Random(99);
        var cases = new List<(string name, Func<string> make)>();
        string Lines(IEnumerable<string> ls, string nl) => string.Join(nl, ls) + nl;
        var good = Enumerable.Range(0, 500).Select(i => JsonSerializer.Serialize(Rand(rnd, rnd.Next(0, 200)))).ToList();
        cases.Add(("sach LF", () => Lines(good, "\n")));
        cases.Add(("sach CRLF", () => Lines(good, "\r\n")));
        cases.Add(("khong dong cuoi", () => string.Join("\n", good)));
        cases.Add(("BOM", () => "﻿" + Lines(good, "\r\n")));
        cases.Add(("dong trang xen ke", () => Lines(good.SelectMany(g => new[] { g, "", "   " }), "\n")));
        cases.Add(("dong hong giua (khong phai json)", () => Lines(good.Take(100).Concat(new[] { "{ghi do dang crash" }).Concat(good.Skip(100)), "\n")));
        // dòng cuối ghi dở nhưng cùng khoá với 1 dòng tốt trước đó: dòng hỏng KHÔNG được đè dòng tốt
        cases.Add(("ghi do cuoi cung khoa voi dong tot", () => Lines(good, "\n") + good[3].Substring(0, good[3].Length / 2)));
        cases.Add(("ghi do giua + khoa trung", () => Lines(good.Take(50).Concat(new[] { good[10].Substring(0, 40) }).Concat(good.Skip(50)), "\n")));
        cases.Add(("dong la (khong bat dau TimeTicks)", () => Lines(good.Take(20).Concat(new[] { "{\"Tint\":1,\"TimeTicks\":77777,\"Bubbles\":[]}" }).Concat(good.Skip(20)), "\n")));
        cases.Add(("dong 'null'", () => Lines(good.Take(20).Concat(new[] { "null" }).Concat(good.Skip(20)), "\n")));
        cases.Add(("rong", () => ""));
        foreach (var (name, make) in cases)
        {
            string path = Path.Combine(Path.GetTempPath(), "pt_load_" + Guid.NewGuid() + ".jsonl");
            try
            {
                File.WriteAllBytes(path, new UTF8Encoding(false).GetBytes(make()));
                var refMap = ReferenceLoad(path);
                var c = new SignalCache(path); c.Load();
                bool eq = Norm(refMap.Values) == Norm(c.Values);
                Check(eq, $"{name}: {refMap.Count} nen", eq ? "" : $"ref={refMap.Count} fast={c.Count}");
            }
            finally { File.Delete(path); }
        }
        // file không tồn tại -> rỗng, không lỗi
        var none = new SignalCache(Path.Combine(Path.GetTempPath(), "khong-co-" + Guid.NewGuid())); none.Load(compact: true);
        Check(none.Count == 0, "file khong ton tai -> rong");
    }

    static void CompactWorks()
    {
        Console.WriteLine("[P4] Nen file: giu nguyen ban ghi thang, chi khi nhieu dong thua");
        var rnd = new Random(5);
        string path = Path.Combine(Path.GetTempPath(), "pt_compact_" + Guid.NewGuid() + ".jsonl");
        try
        {
            // 600 nến, mỗi nến ghi 3 lần (dòng thừa = 200% > 20%) + 1 dòng hỏng
            var sb = new StringBuilder();
            for (int rep = 0; rep < 3; rep++)
                for (int t = 0; t < 600; t++) sb.Append(JsonSerializer.Serialize(Rand(rnd, t))).Append(Environment.NewLine);
            sb.Append("{hong\n");
            File.WriteAllText(path, sb.ToString());
            long sizeBefore = new FileInfo(path).Length;
            var refMap = ReferenceLoad(path);
            var c0 = new SignalCache(path); c0.Load();   // không nén -> file giữ nguyên
            Check(new FileInfo(path).Length == sizeBefore, "Load() thuong khong dong vao file");
            var c = new SignalCache(path); c.Load(compact: true);
            Check(Norm(c.Values) == Norm(refMap.Values), "du lieu trong bo nho khong doi sau khi nen");
            Check(File.ReadLines(path).Count() == 600, "file con dung 600 dong", "dong=" + File.ReadLines(path).Count());
            Check(new FileInfo(path).Length < sizeBefore / 2, "file nho di > 1/2", $"{sizeBefore} -> {new FileInfo(path).Length}");
            var c2 = new SignalCache(path); c2.Load();
            Check(Norm(c2.Values) == Norm(refMap.Values), "doc lai file da nen == ban goc");
            Check(!File.Exists(path + ".tmp"), "khong de lai file .tmp");
            // sau nén: Put + Flush vẫn append được
            c2.Put(Rand(rnd, 9999)); c2.Flush();
            var c3 = new SignalCache(path); c3.Load();
            Check(c3.Count == 601, "ghi tiep sau khi nen");
            // ít dòng thừa (< 1.2x) -> không nén
            string p2 = path + "2";
            File.WriteAllText(p2, string.Join(Environment.NewLine, Enumerable.Range(0, 100).Select(i => JsonSerializer.Serialize(Rand(rnd, i)))) + Environment.NewLine + JsonSerializer.Serialize(Rand(rnd, 5)) + Environment.NewLine);
            long s2 = new FileInfo(p2).Length;
            new SignalCache(p2).Load(compact: true);
            Check(new FileInfo(p2).Length == s2, "101 dong / 100 nen (< 1.2x) -> khong nen");
            File.Delete(p2);
        }
        finally { File.Delete(path); if (File.Exists(path + ".tmp")) File.Delete(path + ".tmp"); }
    }

    static void TornTailThenFlush()
    {
        Console.WriteLine("[P5] File ket thuc do (crash) -> Flush xuong dong truoc khi them, khong dinh vao dong hong");
        string path = Path.Combine(Path.GetTempPath(), "pt_torn_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var rnd = new Random(3);
            File.WriteAllText(path, JsonSerializer.Serialize(Rand(rnd, 1)) + Environment.NewLine + "{\"TimeTicks\":2,\"Tin");
            var c = new SignalCache(path); c.Load();
            c.Put(Rand(rnd, 3)); c.Flush();
            var c2 = new SignalCache(path); c2.Load();
            Check(c2.Count == 2 && c2.TryGet(1, out _) && c2.TryGet(3, out _), "doc duoc ca nen 1 va nen 3 moi ghi", "count=" + c2.Count);
        }
        finally { File.Delete(path); }
    }

    public static int Run()
    {
        _fail = 0;
        RobustBitExact();
        BatchEqualsPerLine();
        FastLoadEqualsReference();
        CompactWorks();
        TornTailThenFlush();
        return _fail;
    }
}
