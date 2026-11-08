// Test logic thuần RangeLogic — các ca BRAINSTORM mục 7 + đối chiếu events_90d.csv (Python).
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using RangeBox;

/// <summary>Dựng nến tổng hợp theo TICK (tick 0,1). Step(d): o = close trước, c = o+d, râu 2 tick mỗi phía
/// ⇒ |d| = 6 cho biên độ nến 10 tick ⇒ mbr = 10, tol = 5, Hmin = 16, Hmax = 60 tick.</summary>
sealed class Synth
{
    public readonly List<(long o, long h, long l, long c)> B = new();
    public long C;
    public int Scale = 1;
    public Synth(long startClose) { C = startClose; }
    public int Count => B.Count;
    public void Bar(long o, long h, long l, long c) { B.Add((o, h, l, c)); C = c; }
    public void Step(long d) { long o = C, c = C + d; Bar(o, Math.Max(o, c) + 2, Math.Min(o, c) - 2, c); }
    public void Trend(int n, long d) { for (int k = 0; k < n; k++) Step(d); }
    public void MoveTo(long target, long step = 6) { while (C != target) { long d = Math.Clamp(target - C, -step, step); Step(d); } }
    public void Zig(long lo, long hi, int legs) { for (int k = 0; k < legs; k++) MoveTo(k % 2 == 0 ? hi : lo); }
    public List<RBar> Bars(double tick = 0.1)
        => B.Select(x => new RBar(x.o * Scale * tick, x.h * Scale * tick, x.l * Scale * tick, x.c * Scale * tick)).ToList();
    /// <summary>Khởi động 130 nến xu hướng tăng đều (không pivot) kết thúc ở close 1002.</summary>
    public static Synth Warm() { var s = new Synth(1002 - 6 * 130); s.Trend(130, 6); return s; }
}

static class LogicTests
{
    static void Check(bool ok, string n, string d = "") => T.Check(ok, n, d);

    static RangeLogic Run(Synth s, RangeParams p = null) { var lg = new RangeLogic(0.1, p); lg.Process(s.Bars()); return lg; }

    static int CountKind(RangeLogic lg, RangeEventKind k, int side = 0)
        => lg.Events.Count(e => e.Kind == k && (side == 0 || e.Side == side));

    /// <summary>Range sạch [1000,1028]: trend vào 1002 → zig 1002↔1026 (râu 1000/1028).</summary>
    static Synth CleanRange(int legs = 5) { var s = Synth.Warm(); s.Zig(1002, 1026, legs); return s; }

    public static void RunAll()
    {
        Console.WriteLine("[1] Range sạch (2 đỉnh + 1 đáy, đan xen)");
        {
            var s = CleanRange();
            var lg = Run(s);
            Check(lg.Ranges.Count == 1, "đúng 1 range", $"{lg.Ranges.Count}");
            if (lg.Ranges.Count > 0)
            {
                var r = lg.Ranges[0];
                Check(r.Top == 1028 && r.Bottom == 1000, "cạnh = cụm râu lặp lại (1028 / 1000 tick)", $"{r.Top}/{r.Bottom}");
                Check(r.State == RangeState.Active, "đang hiệu lực");
                Check(s.B[r.Start].c >= 995 && s.B[r.Start - 1].c < 995, "nến bắt đầu = cây chạy vào vùng (close đầu tiên trong dải)", $"start={r.Start} c={s.B[r.Start].c}");
                Check(r.Birth - r.Start >= 8, "lõi ≥ MinBars 8", $"{r.Birth - r.Start}");
                Check(CountKind(lg, RangeEventKind.StopHunt) == 0, "không râu quét khi râu đúng bằng cạnh");
            }
        }

        Console.WriteLine("[2] Râu quét không dời cạnh");
        {
            var s = CleanRange();
            int at = s.Count;
            s.Bar(1014, 1040, 1012, 1020);        // râu +12 tick (> tol 5), đóng trong
            s.Zig(1002, 1026, 2);
            var lg = Run(s);
            var r = lg.Ranges.FirstOrDefault();
            Check(r != null && lg.Events.Any(e => e.Kind == RangeEventKind.StopHunt && e.Side == +1 && e.Bar == at), "có StopHunt đỉnh ở nến râu");
            Check(r != null && r.Top == 1028, "cạnh trên giữ nguyên 1028", r == null ? "" : $"{r.Top}");
            Check(r != null && r.State == RangeState.Active && lg.Ranges.Count == 1, "range vẫn hiệu lực, không sinh range mới");
        }

        Console.WriteLine("[3] Fail break (K=3)");
        {
            var s = CleanRange();
            s.MoveTo(1020);
            int b = s.Count; s.Bar(1020, 1034, 1018, 1032);   // đóng ngoài +4
            int f = s.Count; s.Bar(1032, 1034, 1020, 1022);   // đóng lại trong
            s.Zig(1002, 1026, 2);
            var lg = Run(s);
            Check(lg.Events.Any(e => e.Kind == RangeEventKind.CloseOutside && e.Side == +1 && e.Bar == b), "CloseOutside đỉnh");
            Check(lg.Events.Any(e => e.Kind == RangeEventKind.FailBreak && e.Side == +1 && e.Bar == f && e.Ref == b), "FailBreak đỉnh ở nến đóng lại, ref = nến đóng ngoài");
            Check(CountKind(lg, RangeEventKind.BreakConfirmed) == 0 && lg.Ranges[0].State == RangeState.Active, "range tiếp tục hiệu lực");
            // fail sau 3 nến vẫn là fail; sau 4 nến là phá thật
            var s2 = CleanRange(); s2.MoveTo(1020);
            s2.Bar(1020, 1034, 1018, 1032); s2.Bar(1032, 1036, 1030, 1034); s2.Bar(1034, 1036, 1029, 1031); s2.Bar(1031, 1033, 1018, 1020);
            var lg2 = Run(s2);
            Check(CountKind(lg2, RangeEventKind.FailBreak, +1) == 1 && CountKind(lg2, RangeEventKind.BreakConfirmed) == 0, "quay vào ở nến thứ 3 sau = fail");
        }

        Console.WriteLine("[4] Phá thật rồi ReEntry trong G");
        {
            var s = CleanRange();
            s.MoveTo(1020);
            int b = s.Count;
            s.Step(14); s.Step(6); s.Step(6); s.Step(6);        // 1034, 1040, 1046, 1052: K=3 → xác nhận ở b+3
            s.Step(-6); s.Step(-6); s.Step(-6); int re = s.Count; s.Step(-8);   // 1046,1040,1034, 1026 (vào lòng)
            var lg = Run(s);
            Check(lg.Events.Any(e => e.Kind == RangeEventKind.BreakConfirmed && e.Side == +1 && e.Bar == b + 3 && e.Ref == b), "BreakConfirmed lên ở b+3, ref = b");
            Check(lg.Events.Any(e => e.Kind == RangeEventKind.ReEntry && e.Bar == re), "ReEntry ở nến đóng lại trong lòng", $"re={re}");
            Check(lg.Ranges.Count == 1 && lg.Ranges[0].State == RangeState.Active, "range cũ sống lại (không sinh range mới)");
            var s2 = CleanRange(); s2.MoveTo(1020); s2.Step(14); s2.Trend(40, 6); s2.MoveTo(1026, 6);
            var lg2 = Run(s2, new RangeParams());
            Check(!lg2.Events.Any(e => e.Kind == RangeEventKind.ReEntry), "quay lại SAU G=30 nến: không ReEntry");
        }

        Console.WriteLine("[5] Đoạn trend không ra range");
        {
            var s = Synth.Warm();
            for (int k = 0; k < 80; k++) { s.Trend(4, 6); s.Step(-3); }
            var lg = Run(s);
            Check(lg.Ranges.Count == 0, "400 nến bậc thang: 0 range", $"{lg.Ranges.Count}");
        }

        Console.WriteLine("[6] Gộp khi trùng cả 2 cạnh (G=5)");
        {
            var s = CleanRange(); s.MoveTo(1008);
            s.Bar(1008, 1010, 995, 997);                         // đóng dưới đáy 3 tick (trong tol)
            for (int k = 0; k < 6; k++) { s.Bar(998, 1001, 996, 997); s.Bar(997, 1001, 997, 998); }   // lơ lửng dưới đáy > G nến
            s.Zig(1002, 1026, 3);
            var p = new RangeParams { G = 5 };
            var lg = Run(s, p);
            Check(CountKind(lg, RangeEventKind.BreakConfirmed, -1) == 1, "phá xuống được xác nhận");
            Check(CountKind(lg, RangeEventKind.Merge) == 1, "có sự kiện Merge", $"{CountKind(lg, RangeEventKind.Merge)}");
            Check(lg.Ranges.Count == 1, "không sinh range thứ 2", $"{lg.Ranges.Count}");
        }

        Console.WriteLine("[7] Chồng một phần → giữ cả hai");
        {
            var s = CleanRange(); s.MoveTo(1020);
            s.Step(14); s.Trend(20, 6); s.Trend(20, -6);        // phá lên, ở trên > G nến (closes > 1028)
            s.MoveTo(1052); s.Zig(1022, 1052, 5);
            var lg = Run(s);
            Check(lg.Ranges.Count == 2, "2 range", $"{lg.Ranges.Count}");
            if (lg.Ranges.Count == 2)
            {
                var a = lg.Ranges[0]; var b2 = lg.Ranges[1];
                bool overlap = b2.Bottom < a.Top && b2.Top > a.Top;
                Check(overlap, "range 2 chồng một phần range 1", $"A {a.Bottom}-{a.Top}, B {b2.Bottom}-{b2.Top}");
                Check(CountKind(lg, RangeEventKind.Merge) == 0, "không gộp");
            }
        }

        Console.WriteLine("[8] Quá thấp / quá cao bị loại");
        {
            var s = Synth.Warm();
            for (int k = 0; k < 30; k++) { s.Bar(1004, 1010, 1000, 1006); s.Bar(1006, 1008, 998, 1002); }
            var lg = Run(s);
            Check(lg.Ranges.Count == 0, "cao 12 tick < 1,6×mbr (16): 0 range", $"{lg.Ranges.Count}");
            var s2 = Synth.Warm(); s2.Zig(1002, 1122, 8);
            var lg2 = Run(s2);
            Check(lg2.Ranges.Count == 0, "cao 124 tick > 6×mbr (60): 0 range", $"{lg2.Ranges.Count}");
        }

        Console.WriteLine("[9] Nhân giá ×10 ra cùng kết quả");
        {
            var s = CleanRange(); s.MoveTo(1020);
            s.Bar(1020, 1034, 1018, 1032); s.Bar(1032, 1034, 1020, 1022); s.Bar(1014, 1040, 1012, 1020);
            s.Step(14); s.Trend(3, 6); s.MoveTo(1020);
            var a = Run(s);
            s.Scale = 10;
            var b = Run(s);
            bool same = a.Events.Count == b.Events.Count && a.Events.Count > 3;
            for (int k = 0; same && k < a.Events.Count; k++)
            {
                var x = a.Events[k]; var y = b.Events[k];
                same = x.Bar == y.Bar && x.Kind == y.Kind && x.Side == y.Side && x.Start == y.Start && x.Ref == y.Ref
                       && Math.Abs(x.Top * 10 - y.Top) < 1e-9 && Math.Abs(x.Bottom * 10 - y.Bottom) < 1e-9;
            }
            Check(same, "cùng chuỗi sự kiện, cạnh ×10", $"{a.Events.Count} vs {b.Events.Count}");
        }

        Console.WriteLine("[10] Một mạch = từng nến; [11] Đối chiếu Python ↔ C# trên 90 ngày");
        CrossCheck();
    }

    static string DefaultBars() => Path.GetFullPath(Path.Combine(T.Root(), "..", "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv"));

    public static List<(string dt, RBar b)> LoadBars(string path)
    {
        var res = new List<(string, RBar)>();
        using var rd = new StreamReader(path);
        var hdr = rd.ReadLine().TrimStart('﻿').Split(',');
        int io = Array.IndexOf(hdr, "open"), ih = Array.IndexOf(hdr, "high"), il = Array.IndexOf(hdr, "low"), ic = Array.IndexOf(hdr, "close"), it = Array.IndexOf(hdr, "datetime");
        string line;
        var ci = CultureInfo.InvariantCulture;
        while ((line = rd.ReadLine()) != null)
        {
            var f = line.Split(',');
            res.Add((f[it], new RBar(double.Parse(f[io], ci), double.Parse(f[ih], ci), double.Parse(f[il], ci), double.Parse(f[ic], ci))));
        }
        return res;
    }

    static string KindName(RangeEventKind k) => k.ToString();
    static string SideName(int s) => s > 0 ? "top" : s < 0 ? "bottom" : "";

    static void CrossCheck()
    {
        string barsPath = Environment.GetEnvironmentVariable("RANGE_XCHECK_CSV") ?? DefaultBars();
        string evPath = Environment.GetEnvironmentVariable("RANGE_EVENTS_CSV") ?? Path.Combine(T.Root(), "research", "events_90d.csv");
        if (!File.Exists(barsPath) || !File.Exists(evPath)) { Check(false, "thiếu file đối chiếu", barsPath + " | " + evPath); return; }
        var bars = LoadBars(barsPath);
        var all = new RangeLogic(0.1);
        all.Process(bars.Select(x => x.b).ToList());

        // [10] từng nến, xen kẽ đọc trạng thái + dựng cảnh vẽ như indicator live (không được làm lệch kết quả)
        var inc = new RangeLogic(0.1);
        for (int i = 0; i < bars.Count; i++)
        {
            inc.Feed(bars[i].b);
            if (i % 997 == 0) { var _ = RangeRenderer.BuildScene(inc, i + 1, Math.Max(0, i - 300), i + 1, new RenderOptions { MarkStopHunt = true }); var __ = inc.Ranges.Count; }
        }
        bool same = all.Events.Count == inc.Events.Count;
        for (int k = 0; same && k < all.Events.Count; k++)
        {
            var x = all.Events[k]; var y = inc.Events[k];
            same = x.Bar == y.Bar && x.Kind == y.Kind && x.Side == y.Side && x.Top == y.Top && x.Bottom == y.Bottom && x.Start == y.Start && x.Ref == y.Ref && x.RangeId == y.RangeId;
        }
        Check(same, "chạy một mạch = nạp từng nến (90 ngày)", $"{all.Events.Count} sự kiện");

        // [11] Python ↔ C#
        var py = File.ReadAllLines(evPath).Skip(1).Where(l => l.Length > 0).ToList();
        var ci = CultureInfo.InvariantCulture;
        int mism = 0, shown = 0;
        int n = Math.Max(py.Count, all.Events.Count);
        for (int k = 0; k < n; k++)
        {
            string why = null;
            if (k >= py.Count) why = "thiếu bên Python";
            else if (k >= all.Events.Count) why = "thiếu bên C#";
            else
            {
                var f = py[k].Split(',');
                var e = all.Events[k];
                bool ok = int.Parse(f[0]) == e.Bar && f[2] == KindName(e.Kind) && f[3] == SideName(e.Side)
                          && Math.Abs(double.Parse(f[4], ci) - e.Top * 0.1) < 1e-6 && Math.Abs(double.Parse(f[5], ci) - e.Bottom * 0.1) < 1e-6
                          && int.Parse(f[6]) == e.Start && int.Parse(f[7]) == e.Ref && int.Parse(f[8]) == e.RangeId
                          && f[1] == bars[e.Bar].dt;
                if (!ok) why = $"py: {py[k]} | cs: {e.Bar},{KindName(e.Kind)},{SideName(e.Side)},{e.Top * 0.1:F2},{e.Bottom * 0.1:F2},{e.Start},{e.Ref},{e.RangeId}";
            }
            if (why != null) { mism++; if (shown++ < 10) Console.WriteLine("    lệch #" + k + ": " + why); }
        }
        Check(mism == 0, "events_90d.csv Python = C# 100 %", $"{py.Count} dòng Python, {all.Events.Count} sự kiện C#, lệch {mism}");
        // ghi bản C# cạnh bản Python để lưu vết đối chiếu
        try
        {
            using var w = new StreamWriter(Path.Combine(T.Root(), "research", "events_90d_cs.csv"));
            w.WriteLine("bar_idx,datetime,type,side,top,bottom,start_idx,ref_idx,range_id");
            foreach (var e in all.Events)
                w.WriteLine(string.Join(",", e.Bar, bars[e.Bar].dt, KindName(e.Kind), SideName(e.Side), (e.Top * 0.1).ToString("F4", ci), (e.Bottom * 0.1).ToString("F4", ci), e.Start, e.Ref, e.RangeId));
        }
        catch (Exception ex) { Console.WriteLine("    (không ghi được events_90d_cs.csv: " + ex.Message + ")"); }
    }
}
