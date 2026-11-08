// Test phá hoại (tester độc lập, REVIEW-1 mục 5–13 + ca tự nghĩ E1…E9).
// Mục 11 chỉ IN số liệu (không đổi logic). Mục 12 render PNG 8-…, 9-… vào tests/ui-out/.
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using RangeBox;

static class AdversarialTests
{
    static void Check(bool ok, string n, string d = "") => T.Check(ok, n, d);

    static Synth CleanRange(int legs = 5) { var s = Synth.Warm(); s.Zig(1002, 1026, legs); return s; }

    static RangeLogic Run(IList<RBar> bars, double tick = 0.1, RangeParams p = null)
    { var lg = new RangeLogic(tick, p); lg.Process(bars); return lg; }

    /// <summary>So 2 chuỗi sự kiện (đơn vị tick). shiftTicks = độ lệch cạnh mong đợi (b = a + shift).</summary>
    static bool SameEvents(RangeLogic a, RangeLogic b, out string why, double shiftTicks = 0)
    {
        why = $"{a.Events.Count} vs {b.Events.Count}";
        if (a.Events.Count != b.Events.Count) return false;
        for (int k = 0; k < a.Events.Count; k++)
        {
            var x = a.Events[k]; var y = b.Events[k];
            if (x.Bar != y.Bar || x.Kind != y.Kind || x.Side != y.Side || x.Start != y.Start || x.Ref != y.Ref || x.RangeId != y.RangeId
                || Math.Abs(x.Top + shiftTicks - y.Top) > 1e-9 || Math.Abs(x.Bottom + shiftTicks - y.Bottom) > 1e-9)
            { why = $"lệch ở sự kiện #{k}: {x.Bar},{x.Kind},{x.Side},{x.Top} vs {y.Bar},{y.Kind},{y.Side},{y.Top}"; return false; }
        }
        return true;
    }

    static List<RBar> Real90()
    {
        string path = Path.GetFullPath(Path.Combine(T.Root(), "..", "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv"));
        return File.Exists(path) ? LogicTests.LoadBars(path).Select(x => x.b).ToList() : null;
    }

    static double Pct(List<int> v, double q)
    {
        if (v.Count == 0) return double.NaN;
        var a = v.OrderBy(x => x).ToList();
        double pos = q * (a.Count - 1); int lo = (int)Math.Floor(pos), hi = (int)Math.Ceiling(pos);
        return a[lo] + (a[hi] - a[lo]) * (pos - lo);
    }

    /// <summary>Chuỗi ngẫu nhiên có đoạn đi ngang (hồi về tâm) xen đoạn trend, đơn vị tick.</summary>
    static List<(long o, long h, long l, long c)> RandomTicks(int seed, int n)
    {
        var rng = new Random(seed);
        var res = new List<(long, long, long, long)>(n);
        long c = 40000, center = c;
        int mode = 0, left = 0;
        for (int i = 0; i < n; i++)
        {
            if (left-- <= 0) { mode = rng.Next(3); left = rng.Next(20, 80); center = c; }
            long d = mode == 0 ? (long)Math.Round((center - c) * 0.3) + rng.Next(-7, 8) : (mode == 1 ? rng.Next(-3, 9) : rng.Next(-8, 4));
            long o = c; c = o + d;
            long h = Math.Max(o, c) + rng.Next(0, 6), l = Math.Min(o, c) - rng.Next(0, 6);
            res.Add((o, h, l, c));
        }
        return res;
    }

    // ------------------------------------------------------------------ tooltip có hiện không (so pixel có/không chuột)
    static bool TipShown(RenderScene sc, FakeMap map, RenderOptions opt, Point mouse, int w, int h)
    {
        using var a = new Bitmap(w, h); using var b = new Bitmap(w, h);
        using (var g = Graphics.FromImage(a)) { g.Clear(Color.Black); g.SetClip(map.Area); RangeRenderer.Draw(g, map, sc, opt, mouse); }
        using (var g = Graphics.FromImage(b)) { g.Clear(Color.Black); g.SetClip(map.Area); RangeRenderer.Draw(g, map, sc, opt, null); }
        var ra = a.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
        var rb = b.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
        try
        {
            int n = ra.Stride * h;
            var pa = new byte[n]; var pb = new byte[n];
            System.Runtime.InteropServices.Marshal.Copy(ra.Scan0, pa, 0, n);
            System.Runtime.InteropServices.Marshal.Copy(rb.Scan0, pb, 0, n);
            int diff = 0; for (int k = 0; k < n; k++) if (pa[k] != pb[k]) diff++;
            return diff > 50;
        }
        finally { a.UnlockBits(ra); b.UnlockBits(rb); }
    }

    static FakeMap MapFor(IList<RBar> bars, int from, int to, float bw, int w, int h)
    {
        double lo = double.MaxValue, hi = double.MinValue;
        for (int i = from; i <= to && i < bars.Count; i++) { lo = Math.Min(lo, bars[i].Low); hi = Math.Max(hi, bars[i].High); }
        double pad = (hi - lo) * 0.08 + 0.2;
        return new FakeMap { First = from, Bw = bw, Area = new RectangleF(10, 10, w - 70, h - 20), PMin = lo - pad, PMax = hi + pad };
    }

    public static void RunAll()
    {
        Console.WriteLine("[A1] REVIEW mục 1 — tooltip hộp chỉ bắt ở cạnh ±5 px");
        {
            var s = CleanRange(); s.MoveTo(1014); s.Zig(1002, 1026, 2);
            var bars = s.Bars(); var lg = Run(bars);
            int from = 110, to = bars.Count - 1, W = 600, H = 400;
            var map = MapFor(bars, from, to, 10, W, H);
            var sc = RangeRenderer.BuildScene(lg, to, from, to, new RenderOptions());
            var opt = new RenderOptions();
            var bx = sc.Boxes.Single();
            int xm = (int)map.X((bx.Start + bx.End) / 2);
            float yTop = map.Y(bx.Top), yBot = map.Y(bx.Bottom);
            Check(yBot - yTop > 20, "hộp đủ cao để có 'giữa lòng' cách cạnh > 5 px", $"{yBot - yTop:F0} px");
            Check(!TipShown(sc, map, opt, new Point(xm, (int)((yTop + yBot) / 2)), W, H), "chuột GIỮA lòng hộp: KHÔNG tooltip");
            Check(!TipShown(sc, map, opt, new Point(xm, (int)Math.Round(yTop) + 9), W, H), "chuột trong hộp cách cạnh trên 9 px: KHÔNG tooltip");
            Check(TipShown(sc, map, opt, new Point(xm, (int)Math.Round(yTop) + 3), W, H), "chuột cách cạnh trên 3 px (trong hộp): CÓ tooltip");
            Check(TipShown(sc, map, opt, new Point(xm, (int)Math.Round(yTop) - 4), W, H), "chuột cách cạnh trên 4 px (ngoài hộp): CÓ tooltip");
            Check(TipShown(sc, map, opt, new Point(xm, (int)Math.Round(yBot) + 2), W, H), "chuột sát cạnh dưới: CÓ tooltip");
            Check(!TipShown(sc, map, opt, new Point((int)(map.X(bx.Start) - 5 - 8), (int)Math.Round(yTop)), W, H), "chuột trên đường cạnh nhưng NGOÀI khoảng x của hộp: KHÔNG tooltip");
            // hộp đã phá: nét chấm retest cũng bắt
            var s2 = Synth.Warm(); s2.Zig(1002, 1026, 5); s2.MoveTo(1008); s2.Trend(5, -6); s2.Trend(4, 3); s2.Trend(10, -6);
            var b2 = s2.Bars(); var lg2 = Run(b2);
            var map2 = MapFor(b2, 110, b2.Count - 1, 10, 700, H);
            var sc2 = RangeRenderer.BuildScene(lg2, b2.Count - 1, 110, b2.Count - 1, opt);
            var bb = sc2.Boxes.FirstOrDefault(x => x.Broken);
            Check(bb != null, "có hộp đã phá để thử nét chấm");
            if (bb != null)
            {
                double edge = bb.BreakSide > 0 ? bb.Top : bb.Bottom;
                int xe = (int)map2.X(bb.BreakIdx + 10), ye = (int)Math.Round(map2.Y(edge));
                Check(TipShown(sc2, map2, opt, new Point(xe, ye + 2), 700, H), "chuột trên nét chấm retest (sau nến phá): CÓ tooltip");
                Check(!TipShown(sc2, map2, opt, new Point(xe, ye + 12), 700, H), "chuột cách nét chấm 12 px: KHÔNG tooltip");
            }
        }

        Console.WriteLine("[A5] mbr = 0 (doji H==L)");
        {
            var ex = Catch(() =>
            {
                var flat = Enumerable.Range(0, 300).Select(_ => new RBar(100, 100, 100, 100)).ToList();
                var lg = Run(flat);
                Check(lg.Ranges.Count == 0 && lg.Mbr == 0, "300 doji cùng giá: 0 range, mbr = 0", $"{lg.Ranges.Count} range, mbr {lg.Mbr}");
                var zz = new Synth(1000); for (int k = 0; k < 300; k++) { long p = 1000 + (k % 12 < 6 ? k % 6 : 6 - k % 6) * 4; zz.Bar(p, p, p, p); }
                var lg2 = Run(zz.Bars());
                Check(lg2.Ranges.Count == 0, "300 doji H==L đi zigzag (có pivot, mbr=0 ⇒ Hmax=0): 0 range", $"{lg2.Ranges.Count}");
            });
            Check(ex == null, "mbr = 0: không ngoại lệ / chia 0", ex?.Message ?? "");
        }

        Console.WriteLine("[A6] Nến gap xuyên cả hộp");
        {
            var s = CleanRange();                         // kết thúc close 1026 (sát cạnh trên)
            int g1 = s.Count; s.Bar(1026, 1027, 984, 985); // từ Active đóng DƯỚI đáy 15 tick (xuyên cả hộp)
            int g2 = s.Count; s.Bar(985, 1045, 984, 1043); // đang Pending xuống, đóng TRÊN đỉnh
            s.Step(4); s.Step(4); s.Step(4);
            RangeLogic lg = null;
            var ex = Catch(() => lg = Run(s.Bars()));
            Check(ex == null, "không ngoại lệ", ex?.Message ?? "");
            if (lg != null)
            {
                Check(lg.Events.Any(e => e.Kind == RangeEventKind.Birth && e.Bar < g1), "range đã sinh trước nến gap");
                Check(lg.Events.Any(e => e.Bar == g1 && e.Kind == RangeEventKind.CloseOutside && e.Side == -1), "Active → gap xuống: CloseOutside cạnh dưới");
                Check(lg.Events.Any(e => e.Bar == g2 && e.Kind == RangeEventKind.FailBreak && e.Side == -1 && e.Ref == g1), "Pending xuống → gap lên: FailBreak đáy (ref = nến gap 1)");
                Check(lg.Events.Any(e => e.Bar == g2 && e.Kind == RangeEventKind.CloseOutside && e.Side == +1), "… và CloseOutside cạnh trên cùng nến");
                Check(lg.Events.Any(e => e.Bar == g2 + 3 && e.Kind == RangeEventKind.BreakConfirmed && e.Side == +1 && e.Ref == g2), "3 nến sau: BreakConfirmed lên, ref = nến gap 2");
                Check(lg.Ranges.Count == 1, "không sinh range rác", $"{lg.Ranges.Count}");
            }
        }

        Console.WriteLine("[A7] Đỉnh bằng nhau (plateau)");
        {
            // (a) mọi nến vùng ngang cùng high 1028, đáy zigzag
            var s = Synth.Warm();
            long c = 1002;
            for (int k = 0; k < 90; k++) { long nc = 1002 + (k % 8 < 4 ? k % 4 : 4 - k % 4) * 6; s.Bar(c, 1028, Math.Min(c, nc) - 2, nc); c = nc; }
            var lg = Run(s.Bars());
            int nTopPiv = 0; for (int j = 131; j < s.Count - 1; j++) if (s.B[j].h > s.B[j - 1].h && s.B[j].h >= s.B[j + 1].h) nTopPiv++;
            Console.WriteLine($"    (a) toàn đỉnh 1028: pivot đỉnh trong vùng ngang = {nTopPiv + 1} (chỉ nến đầu vùng), range = {lg.Ranges.Count}");
            Check(lg.Ranges.Count == 0, "(a) toàn đỉnh bằng nhau: 0 range — GIỚI HẠN đã biết của luật pivot `>` (báo cáo, không sửa)", $"{lg.Ranges.Count}");
            // (b) mỗi đỉnh là plateau 2 nến bằng nhau → nến đầu plateau vẫn là pivot
            var s2 = Synth.Warm();
            for (int leg = 0; leg < 5; leg++)
            {
                s2.MoveTo(1020); s2.Bar(1020, 1028, 1018, 1024); s2.Bar(1024, 1028, 1020, 1022);  // 2 nến high 1028
                s2.MoveTo(1002);
            }
            var lg2 = Run(s2.Bars());
            Check(lg2.Ranges.Count >= 1 && lg2.Ranges[0].Top == 1028, "(b) đỉnh plateau 2 nến: vẫn sinh range, cạnh trên = 1028",
                  lg2.Ranges.Count == 0 ? "0 range" : $"{lg2.Ranges.Count} range, top {lg2.Ranges[0].Top}");
        }

        Console.WriteLine("[A8] Ít hơn / đúng 100 nến");
        {
            var s = new Synth(1002); s.Zig(1002, 1026, 40);
            var all = s.Bars();
            var lg99 = Run(all.Take(99).ToList());
            Check(lg99.Ranges.Count == 0, "99 nến: 0 range", $"{lg99.Ranges.Count}");
            var lg100 = Run(all.Take(100).ToList());
            var first = lg100.Events.FirstOrDefault(e => e.Kind == RangeEventKind.Birth);
            Check(lg100.Ranges.Count == 1 && first.Bar == 99, "đúng 100 nến: range sinh ngay ở nến chỉ số 99 (nến thứ 100)", lg100.Ranges.Count == 0 ? "0 range" : $"birth {first.Bar}");
            var lgAll = Run(all);
            Check(lgAll.Events.All(e => e.Bar >= 99), "không sự kiện nào trước nến 99");
        }

        var real = Real90();
        RangeLogic baseLg = null;
        if (real == null) Check(false, "thiếu dữ liệu 90 ngày (mục 9, 11)");
        else baseLg = Run(real);

        Console.WriteLine("[A9] Tick 0,25 / 0,01 / ×10 — cùng sự kiện tính theo tick");
        {
            var s = CleanRange(); s.MoveTo(1020);
            s.Bar(1020, 1034, 1018, 1032); s.Bar(1032, 1034, 1020, 1022); s.Bar(1014, 1040, 1012, 1020);
            s.Step(14); s.Trend(3, 6); s.MoveTo(1020);
            var a = Run(s.Bars(0.1), 0.1);
            foreach (var tk in new[] { 0.25, 0.01, 1.0, 0.0001 })
            {
                var b = Run(s.Bars(tk), tk);
                Check(SameEvents(a, b, out var why) && a.Events.Count > 3, $"tổng hợp: tick {tk} = tick 0,1", why);
            }
            if (baseLg != null)
            {
                foreach (var tk in new[] { 0.25, 0.01 })
                {
                    var conv = real.Select(x => new RBar(Math.Round(x.Open / 0.1) * tk, Math.Round(x.High / 0.1) * tk, Math.Round(x.Low / 0.1) * tk, Math.Round(x.Close / 0.1) * tk)).ToList();
                    var b = Run(conv, tk);
                    Check(SameEvents(baseLg, b, out var why), $"GC 90 ngày đổi thang sang tick {tk}: cùng {baseLg.Events.Count} sự kiện", why);
                }
            }
        }

        Console.WriteLine("[A10] 500 nến ngẫu nhiên × 20 seed: một mạch = từng nến");
        {
            int bad = 0, totalEv = 0, totalRanges = 0; string firstBad = "";
            for (int seed = 1; seed <= 20; seed++)
            {
                var tk = RandomTicks(seed, 500);
                var bars = tk.Select(x => new RBar(x.o * 0.1, x.h * 0.1, x.l * 0.1, x.c * 0.1)).ToList();
                try
                {
                    var a = Run(bars);
                    var b = new RangeLogic(0.1);
                    for (int i = 0; i < bars.Count; i++)
                    {
                        b.Feed(bars[i]);
                        if (i % 7 == 0) RangeRenderer.BuildScene(b, i + 1, Math.Max(0, i - 200), i + 1, new RenderOptions { MarkStopHunt = true });
                    }
                    var c2 = new RangeLogic(0.1); foreach (var x in tk) c2.FeedTicks(x.o, x.h, x.l, x.c);
                    if (!SameEvents(a, b, out var why) || !SameEvents(a, c2, out why)) { bad++; if (firstBad == "") firstBad = $"seed {seed}: {why}"; }
                    totalEv += a.Events.Count; totalRanges += a.Ranges.Count;
                }
                catch (Exception e) { bad++; if (firstBad == "") firstBad = $"seed {seed}: {e.GetType().Name} {e.Message}"; }
            }
            Check(bad == 0, "20 seed: Feed từng nến = Process = FeedTicks, không ngoại lệ", bad == 0 ? $"{totalRanges} range, {totalEv} sự kiện" : firstBad);
            Check(totalRanges > 20, "chuỗi ngẫu nhiên có sinh range (test có nghĩa)", $"{totalRanges}");
        }

        Console.WriteLine("[A11] Tuổi thọ range trên 90 ngày (CHỈ BÁO CÁO)");
        if (real != null) Lifetime(real);

        Console.WriteLine("[A12] Render: 3 fail break liên tiếp + 2 râu quét; hộp tràn mép trái");
        Render12();

        Console.WriteLine("[A13] Nạp 300 → Clear → nạp lại 300");
        {
            var s = CleanRange(); s.MoveTo(1020); s.Bar(1020, 1034, 1018, 1032); s.Bar(1032, 1034, 1020, 1022); s.Zig(1002, 1026, 4); s.Step(14); s.Trend(6, 6);
            while (s.Count < 300) s.Step(s.Count % 2 == 0 ? 3 : -3);
            var bars = s.Bars().Take(300).ToList();
            var fresh = Run(bars);
            // mô phỏng vòng đời RangeBox: logic cũ nạp dở 170 nến → OnClear (logic = null) → nạp lại từ đầu
            var lg = new RangeLogic(0.1);
            for (int i = 0; i < 170; i++) lg.Feed(bars[i]);
            lg = null;
            lg = new RangeLogic(0.1); lg.Process(bars);
            Check(SameEvents(fresh, lg, out var why) && fresh.Events.Count > 3, "sau Clear nạp lại 300 nến = chạy mới", why);
            // logic không giữ trạng thái tĩnh: 2 instance chạy xen kẽ cho cùng kết quả
            var x1 = new RangeLogic(0.1); var x2 = new RangeLogic(0.1);
            for (int i = 0; i < bars.Count; i++) { x1.Feed(bars[i]); x2.Feed(bars[i]); }
            Check(SameEvents(fresh, x1, out why) && SameEvents(fresh, x2, out why), "2 instance chạy xen kẽ không ảnh hưởng nhau", why);
            Console.WriteLine("    (vòng đời thật của RangeBox.cs OnClear→OnUpdate test bằng HistoricalData giả ở tests-dll)");
        }

        MaxReEntryTests();
        Extra(real, baseLg);
    }

    // ------------------------------------------------------------------ MaxReEntry = 2 (quyết định mục 11)
    static List<int> BreakUpAndBack(Synth s, bool back = true)
    {   // từ trong lòng [1000,1028]: phá lên (đóng 1034, rồi 3 nến ngoài ⇒ BreakConfirmed), rồi quay về đóng 1026 trong lòng
        s.MoveTo(1020); int b = s.Count; s.Step(14); s.Step(6); s.Step(6); s.Step(6);
        if (back) { s.Step(-6); s.Step(-6); s.Step(-6); s.Step(-8); s.MoveTo(1008); }
        return new List<int> { b, b + 3 };
    }

    static void MaxReEntryTests()
    {
        Console.WriteLine("[A14] MaxReEntry = 2: phá lần 3 ⇒ Dead ngay");
        Check(new RangeParams().MaxReEntry == 2, "RangeParams.MaxReEntry mặc định = 2");
        // (a) phá → ReEntry → phá → ReEntry → phá lần 3 → quay lại trong hộp (trong G) rồi đi ngang đúng cạnh cũ
        var s = CleanRange();
        var b1 = BreakUpAndBack(s); var b2 = BreakUpAndBack(s); var b3 = BreakUpAndBack(s, back: false);
        int back = s.Count; s.Step(-6); s.Step(-6); s.Step(-6); s.Step(-8);       // đóng 1026 trong hộp, chỉ 4–7 nến sau phá (< G)
        s.Zig(1002, 1026, 5);                                                       // đi ngang lại đúng cạnh cũ ⇒ trước đây Merge hồi sinh
        var lg = Run(s.Bars());
        var r0 = lg.Ranges[0];
        int nRe = lg.Events.Count(e => e.RangeId == 0 && e.Kind == RangeEventKind.ReEntry);
        int nBk = lg.Events.Count(e => e.RangeId == 0 && e.Kind == RangeEventKind.BreakConfirmed);
        Check(nBk == 3 && nRe == 2, "range 0: 3 lần BreakConfirmed, đúng 2 lần ReEntry", $"{nBk} phá, {nRe} ReEntry");
        Check(lg.Events.Any(e => e.RangeId == 0 && e.Kind == RangeEventKind.BreakConfirmed && e.Bar == b3[1] && e.Ref == b3[0]), "phá lần 3 xác nhận ở nến b+3, ref = nến phá");
        Check(r0.State == RangeState.Dead && r0.Exhausted, "range 0 Dead (hết lượt) ngay, không chờ G", $"{r0.State}, exhausted={r0.Exhausted}");
        Check(!lg.Events.Any(e => e.RangeId == 0 && e.Bar > b3[1]), "đóng lại trong hộp sau đó: KHÔNG ReEntry / Merge / sự kiện nào của range 0",
              string.Join(" ", lg.Events.Where(e => e.RangeId == 0 && e.Bar > b3[1]).Select(e => $"{e.Bar}:{e.Kind}")));
        var r1 = lg.Ranges.Count > 1 ? lg.Ranges[1] : null;
        Check(r1 != null && lg.Events.Any(e => e.RangeId == 1 && e.Kind == RangeEventKind.Birth), "đi ngang lại đúng cạnh cũ ⇒ SINH range mới (id 1), không hồi sinh range 0",
              $"{lg.Ranges.Count} range, Merge {lg.Events.Count(e => e.Kind == RangeEventKind.Merge)}");
        Check(r1 != null && r1.Start >= b3[0], "range mới bắt đầu không sớm hơn nến phá lần 3 (_scanStart = nến phá)", r1 == null ? "" : $"start {r1.Start}, nến phá {b3[0]}");
        // (b) range mới có thể bắt đầu ĐÚNG từ vùng nến phá: sau phá lần 3 đi ngang phía trên
        var s2 = CleanRange();
        BreakUpAndBack(s2); BreakUpAndBack(s2); var c3 = BreakUpAndBack(s2, back: false);
        s2.Zig(1046, 1070, 6);
        var lg2 = Run(s2.Bars());
        var nr = lg2.Ranges.Skip(1).FirstOrDefault();
        Check(lg2.Ranges[0].Exhausted && nr != null && nr.Start >= c3[0] && nr.Start <= c3[1] + 2 && nr.Bottom > 1028,
              "sau phá lần 3, range mới phía trên sinh được, bắt đầu từ vùng nến phá", nr == null ? $"{lg2.Ranges.Count} range" : $"start {nr.Start} (phá {c3[0]}…{c3[1]}), {nr.Bottom}-{nr.Top}");
        // (c) MaxReEntry < 0 = không giới hạn ⇒ hành vi cũ (lần phá 3 vẫn chờ G, quay lại thì ReEntry)
        var lg3 = Run(s.Bars(), 0.1, new RangeParams { MaxReEntry = -1 });
        Check(lg3.Events.Count(e => e.RangeId == 0 && e.Kind == RangeEventKind.ReEntry) >= 3, "MaxReEntry = −1: ReEntry lần 3 vẫn xảy ra (không giới hạn)",
              $"{lg3.Events.Count(e => e.RangeId == 0 && e.Kind == RangeEventKind.ReEntry)}");
        // (d) một mạch = từng nến vẫn đúng
        var inc = new RangeLogic(0.1); foreach (var x in s.Bars()) inc.Feed(x);
        Check(SameEvents(lg, inc, out var why), "MaxReEntry: một mạch = từng nến", why);
    }

    static Exception Catch(Action a) { try { a(); return null; } catch (Exception e) { return e; } }

    // ------------------------------------------------------------------ mục 11
    static void Lifetime(List<RBar> real)
    {
        var lg = new RangeLogic(0.1);
        var deadAt = new Dictionary<int, int>();
        var alive = new HashSet<int>();
        int evSeen = 0;
        for (int i = 0; i < real.Count; i++)
        {
            lg.Feed(real[i]);
            for (; evSeen < lg.Events.Count; evSeen++)
            {
                var e = lg.Events[evSeen];
                if (e.Kind == RangeEventKind.Birth || e.Kind == RangeEventKind.Merge) { alive.Add(e.RangeId); deadAt.Remove(e.RangeId); }
            }
            if (alive.Count > 0)
            {
                List<int> died = null;
                foreach (var id in alive) if (lg.Ranges[id].State == RangeState.Dead) (died ??= new List<int>()).Add(id);
                if (died != null) foreach (var id in died) { alive.Remove(id); deadAt[id] = i; }
            }
        }
        var life = new List<int>(); var boxLen = new List<int>();
        int censored = 0;
        foreach (var r in lg.Ranges)
        {
            if (deadAt.TryGetValue(r.Id, out int d)) life.Add(d - r.Start); else censored++;
            if (r.State == RangeState.Broken || r.State == RangeState.Dead) boxLen.Add(r.BreakIdx - r.Start + 1);
        }
        var reCnt = lg.Ranges.Select(r => lg.Events.Count(e => e.RangeId == r.Id && e.Kind == RangeEventKind.ReEntry)).ToList();
        int n = lg.Ranges.Count;
        int re1 = reCnt.Count(x => x >= 1), re2 = reCnt.Count(x => x >= 2);
        int over73 = boxLen.Count(x => x > 73);
        string s1 = $"range: {n} (chết {life.Count}, còn sống cuối dữ liệu {censored})";
        string s2 = $"tuổi thọ Start→Dead (nến): p50 {Pct(life, 0.5):F0} · p90 {Pct(life, 0.9):F0} · max {(life.Count > 0 ? life.Max() : 0)}";
        string s3 = $"độ dài hộp vẽ Start→nến phá cuối (nến): p50 {Pct(boxLen, 0.5):F0} · p90 {Pct(boxLen, 0.9):F0} · max {(boxLen.Count > 0 ? boxLen.Max() : 0)} · >73 nến: {over73} ({100.0 * over73 / Math.Max(1, boxLen.Count):F1} %)";
        string s4 = $"ReEntry: ≥1 lần {re1} range ({100.0 * re1 / n:F1} %) · ≥2 lần {re2} range ({100.0 * re2 / n:F1} %) · nhiều nhất {reCnt.Max()} lần";
        foreach (var x in new[] { s1, s2, s3, s4 }) Console.WriteLine("    " + x);
        try { File.WriteAllLines(Path.Combine(T.Root(), "tests", "ui-out", "a11-tuoi-tho.txt"), new[] { s1, s2, s3, s4 }); } catch { }
        Check(n > 0 && life.Count > 0, "đo được tuổi thọ (chỉ báo cáo)");
    }

    // ------------------------------------------------------------------ mục 12
    static void Render12()
    {
        var s = CleanRange(); s.MoveTo(1020);
        var fbBars = new List<int>();
        for (int k = 0; k < 3; k++)
        {
            s.Bar(1020, 1034, 1018, 1032);                // đóng ngoài cạnh trên
            fbBars.Add(s.Count); s.Bar(1032, 1034, 1018, 1020);   // đóng lại trong
        }
        int h1 = s.Count; s.Bar(1020, 1033, 1018, 1022); // râu quét đỉnh
        int h2 = s.Count; s.Bar(1022, 1034, 1016, 1018); // râu quét đỉnh tiếp
        s.Zig(1002, 1026, 2);
        var bars = s.Bars(); var lg = Run(bars);
        var all = new RenderOptions { MarkStopHunt = true };
        int fbn = lg.Events.Count(e => e.Kind == RangeEventKind.FailBreak && e.Side > 0);
        int hn = lg.Events.Count(e => e.Kind == RangeEventKind.StopHunt && (e.Bar == h1 || e.Bar == h2));
        Check(fbn == 3 && hn == 2, "kịch bản đúng: 3 fail break đỉnh + 2 râu quét đỉnh", $"{fbn} FB, {hn} râu");
        var dir = Path.Combine(T.Root(), "tests", "ui-out"); Directory.CreateDirectory(dir);
        foreach (var bw in new[] { 10f, 3f, 1f })
        {
            int from = 115, to = bars.Count - 1;
            int W = (int)Math.Max(320, (to - from + 1) * bw + 70), H = 360;
            var map = MapFor(bars, from, to, bw, W, H);
            var sc = RangeRenderer.BuildScene(lg, to, from, to, all);
            // hình bao thật của từng dấu (theo công thức RangeRenderer.Draw)
            float tri = Math.Clamp(Math.Max(1f, bw) * 0.9f, 4f, 9f), dot = Math.Clamp(Math.Max(1f, bw) * 0.35f, 1f, 4f);
            var rects = sc.Marks.Select(m =>
            {
                float cx = map.X(m.Bar), y = map.Y(m.Price);
                if (m.Kind == RangeEventKind.FailBreak)
                    return m.Side > 0 ? new RectangleF(cx - tri / 2, y - 3 - tri, tri, tri) : new RectangleF(cx - tri / 2, y + 3, tri, tri);
                return new RectangleF(cx - dot, y - dot, dot * 2, dot * 2);
            }).ToList();
            int ov = 0; string ovWho = "";
            for (int a = 0; a < rects.Count; a++) for (int b = a + 1; b < rects.Count; b++)
                {
                    var r = RectangleF.Intersect(rects[a], rects[b]);
                    if (r.Width > 0.5f && r.Height > 0.5f) { ov++; ovWho += $" [{sc.Marks[a].Kind}@{sc.Marks[a].Bar} × {sc.Marks[b].Kind}@{sc.Marks[b].Bar}]"; }
                }
            string file = $"8-fail-break-lien-tiep-{bw:F0}px.png";
            using (var bmp = new Bitmap(W, H)) using (var g = Graphics.FromImage(bmp))
            {
                g.Clear(Color.FromArgb(18, 20, 26));
                DrawBars(g, map, bars, from, to);
                g.SetClip(map.Area); RangeRenderer.Draw(g, map, sc, all, null); g.ResetClip();
                bmp.Save(Path.Combine(dir, file), ImageFormat.Png);
            }
            bool expectOk = bw >= 2f;
            if (expectOk) Check(ov == 0, $"bw {bw} px: {sc.Marks.Count} dấu không đè nhau ({file})", $"{ov} cặp đè{ovWho}");
            else Console.WriteLine($"    bw {bw} px: {ov} cặp dấu đè nhau{ovWho} ({file}) — dấu tối thiểu 4 px > khoảng cách 1–2 px giữa nến: chấp nhận khi zoom cực xa");
        }
        // hộp hiệu lực bắt đầu NGOÀI mép trái (Start < li)
        {
            var s2 = CleanRange(8);
            var b2 = s2.Bars(); var lg2 = Run(b2);
            var r = lg2.Ranges[0];
            int from = r.Start + 15, to = b2.Count - 1, W = (int)((to - from + 1) * 10 + 70), H = 360;
            var map = MapFor(b2, from, to, 10, W, H);
            var sc = RangeRenderer.BuildScene(lg2, to, from - 1, to + 1, new RenderOptions());
            Check(sc.Boxes.Count == 1 && sc.Boxes[0].Start < from, "hộp Start < li vẫn vào cảnh", $"start {r.Start}, li {from}");
            string file = "9-hop-tran-mep-trai.png";
            Color px;
            using (var bmp = new Bitmap(W, H)) using (var g = Graphics.FromImage(bmp))
            {
                g.Clear(Color.FromArgb(18, 20, 26));
                DrawBars(g, map, b2, from, to);
                g.SetClip(map.Area); RangeRenderer.Draw(g, map, sc, new RenderOptions(), null); g.ResetClip();
                px = bmp.GetPixel((int)map.Area.Left + 2, (int)Math.Round(map.Y(sc.Boxes[0].Top)));
                var outside = bmp.GetPixel((int)map.Area.Left - 3, (int)Math.Round(map.Y(sc.Boxes[0].Top)));
                Check(outside.B < 40, "không vẽ lố ra ngoài mép trái vùng chart (x < clip.Left)", $"pixel {outside}");
                bmp.Save(Path.Combine(dir, file), ImageFormat.Png);
            }
            Check(px.B > 100 && px.G > 100, "cạnh trên vẫn vẽ ở sát mép trái (phần nhìn thấy)", $"pixel {px}");
        }
    }

    static void DrawBars(Graphics g, FakeMap map, IList<RBar> bars, int from, int to)
    {
        for (int i = from; i <= to; i++)
        {
            var b = bars[i]; float x = map.X(i);
            var col = b.Close >= b.Open ? Color.FromArgb(70, 170, 120) : Color.FromArgb(200, 80, 80);
            using var pen = new Pen(col, 1f);
            g.DrawLine(pen, x, map.Y(b.High), x, map.Y(b.Low));
            float y0 = map.Y(Math.Max(b.Open, b.Close)), y1 = map.Y(Math.Min(b.Open, b.Close));
            using var br = new SolidBrush(col);
            g.FillRectangle(br, x - Math.Max(1f, map.Bw * 0.7f) / 2f, y0, Math.Max(1f, map.Bw * 0.7f), Math.Max(1f, y1 - y0));
        }
    }

    // ------------------------------------------------------------------ ca phá hoại tự nghĩ
    sealed class FuncMap : IChartMap
    {
        public Func<int, float> FX; public Func<double, float> FY; public float Bw = 10; public RectangleF Area = new RectangleF(0, 0, 400, 300);
        public float X(int i) => FX(i); public float Y(double p) => FY(p); public float BarWidth => Bw; public RectangleF Clip => Area;
    }

    static void Extra(List<RBar> real, RangeLogic baseLg)
    {
        Console.WriteLine("[E1] Nến NaN / vô cực giữa chuỗi");
        {
            var s = CleanRange(); var bars = s.Bars();
            var good = Run(bars);
            var bad = new List<RBar>(bars) { new RBar(double.NaN, double.NaN, double.NaN, double.NaN) };
            var s2 = CleanRange(); s2.Zig(1002, 1026, 2); var tail = s2.Bars().Skip(bars.Count).ToList();
            bad.AddRange(tail);
            RangeLogic lg = null;
            var ex = Catch(() => lg = Run(bad));
            Check(ex == null, "nến NaN: không ngoại lệ", ex?.Message ?? "");
            if (lg != null)
            {
                bool brokeByNaN = lg.Events.Any(e => e.Bar == bars.Count && (e.Kind == RangeEventKind.CloseOutside || e.Kind == RangeEventKind.StopHunt));
                Check(!brokeByNaN && lg.Ranges.Count >= 1 && lg.Ranges[0].State == RangeState.Active, "nến NaN không làm phá / quét range đang hiệu lực",
                      string.Join(" ", lg.Events.Where(e => e.Bar >= bars.Count && e.Bar <= bars.Count + 1).Select(e => $"{e.Bar}:{e.Kind}{e.Side}")));
                Check(lg.Count == bad.Count, "chỉ số nến vẫn khớp chart (nến NaN vẫn chiếm 1 chỉ số)", $"{lg.Count} vs {bad.Count}");
            }
            var inf = new List<RBar>(bars) { new RBar(102, double.PositiveInfinity, 100, 101) };
            inf.AddRange(tail);
            RangeLogic lgi = null;
            ex = Catch(() => lgi = Run(inf));
            Check(ex == null && lgi != null && !lgi.Events.Any(e => e.Bar == bars.Count && e.Kind != RangeEventKind.Birth), "high = +∞: không ngoại lệ, không sự kiện rác", ex?.Message ?? "");
        }

        Console.WriteLine("[E2] Nến hỏng high < low / high < close");
        {
            var s = CleanRange(); var bars = s.Bars();
            var b = new List<RBar>(bars) { new RBar(101.4, 100.8, 102.2, 101.5) };   // high < low (đảo)
            var s2 = CleanRange(); s2.Zig(1002, 1026, 2); b.AddRange(s2.Bars().Skip(bars.Count));
            var fixedB = new List<RBar>(b); fixedB[bars.Count] = new RBar(101.4, 102.2, 100.8, 101.5);
            RangeLogic lg = null; var ex = Catch(() => lg = Run(b));
            Check(ex == null, "high < low: không ngoại lệ", ex?.Message ?? "");
            var lgFix = Run(fixedB);
            string why = "logic null";
            Check(lg != null && SameEvents(lgFix, lg, out why), "high<low được hiểu như nến đã đổi chỗ high/low", why);
        }

        Console.WriteLine("[E3] Giá âm / dời cả chuỗi một số tick nguyên");
        if (baseLg != null)
        {
            foreach (long sh in new long[] { -60000, -43000 * 2, 12345 })
            {
                var sb = real.Select(x => new RBar(Math.Round(x.Open / 0.1) * 0.1 + sh * 0.1, Math.Round(x.High / 0.1) * 0.1 + sh * 0.1, Math.Round(x.Low / 0.1) * 0.1 + sh * 0.1, Math.Round(x.Close / 0.1) * 0.1 + sh * 0.1)).ToList();
                var lg = Run(sb);
                Check(SameEvents(baseLg, lg, out var why, sh), $"dời {sh} tick (giá {(sh < -43000 ? "ÂM" : "dương")}): cùng sự kiện, cạnh dời đúng {sh} tick", why);
            }
        }

        Console.WriteLine("[E4] Giá không chia hết tick");
        if (baseLg != null)
        {
            var off = real.Select(x => new RBar(x.Open + 0.03, x.High + 0.03, x.Low + 0.03, x.Close + 0.03)).ToList();
            Check(SameEvents(baseLg, Run(off), out var why), "lệch +0,03 (0,3 tick): làm tròn về cùng tick ⇒ cùng sự kiện", why);
            var off2 = real.Select(x => new RBar(x.Open - 0.04, x.High - 0.04, x.Low - 0.04, x.Close - 0.04)).ToList();
            Check(SameEvents(baseLg, Run(off2), out why), "lệch −0,04: cùng sự kiện", why);
        }

        Console.WriteLine("[E5] 1 triệu nến — hiệu năng");
        {
            var tk = RandomTicks(7, 1_000_000);
            var sw = Stopwatch.StartNew();
            var lg = new RangeLogic(0.1);
            foreach (var x in tk) lg.FeedTicks(x.o, x.h, x.l, x.c);
            sw.Stop();
            long ms = sw.ElapsedMilliseconds;
            var sw2 = Stopwatch.StartNew();
            for (int k = 0; k < 20; k++) RangeRenderer.BuildScene(lg, lg.Count - 1, lg.Count - 300, lg.Count - 1, new RenderOptions { MarkStopHunt = true });
            sw2.Stop();
            double paint = sw2.Elapsed.TotalMilliseconds / 20;
            Console.WriteLine($"    nạp 1.000.000 nến: {ms} ms · {lg.Ranges.Count} range · {lg.Events.Count} sự kiện · BuildScene mỗi khung vẽ {paint:F2} ms");
            Check(ms < 20000, "1 triệu nến nạp < 20 s", $"{ms} ms");
            Check(paint < 8, "BuildScene (mỗi lần vẽ) < 8 ms dù có hàng chục nghìn range", $"{paint:F2} ms");
        }

        Console.WriteLine("[E6] Đổi tham số giữa chừng (RangeParams là object sửa được)");
        {
            var tk = RandomTicks(3, 400);
            var p = new RangeParams();
            var lg = new RangeLogic(0.1, p);
            for (int i = 0; i < 300; i++) lg.FeedTicks(tk[i].o, tk[i].h, tk[i].l, tk[i].c);
            p.MbrLen = 50;
            for (int i = 300; i < 400; i++) lg.FeedTicks(tk[i].o, tk[i].h, tk[i].l, tk[i].c);
            var rng = tk.Skip(350).Select(x => x.h - x.l).OrderBy(x => x).ToList();
            double expect = (rng[24] + rng[25]) / 2.0;
            Check(lg.Mbr == expect, "giảm MbrLen 100→50 giữa chừng: cửa sổ median co về 50 nến", $"mbr {lg.Mbr}, mong đợi {expect}");
            Console.WriteLine("    (RangeBox.cs không đổi tham số lúc chạy — đổi Settings ⇒ OnClear tạo logic mới; ca này chỉ để logic tự vệ)");
        }

        Console.WriteLine("[E7] Vẽ với toạ độ hỏng: Y = NaN/∞, x = −1e9 (hộp rất dài ngoài mép trái)");
        {
            var s = CleanRange(); var bars = s.Bars(); var lg = Run(bars);
            var sc = RangeRenderer.BuildScene(lg, bars.Count - 1, 0, bars.Count - 1, new RenderOptions { MarkStopHunt = true });
            sc.Marks.Add(new MarkView { Bar = bars.Count - 2, Kind = RangeEventKind.FailBreak, Side = 1, Price = 102.8 });
            var maps = new (string name, FuncMap m)[]
            {
                ("Y = NaN", new FuncMap { FX = i => (i - 100) * 10f, FY = p => float.NaN }),
                ("Y = +∞", new FuncMap { FX = i => (i - 100) * 10f, FY = p => float.PositiveInfinity }),
                ("x = −1e9 ở nến bắt đầu", new FuncMap { FX = i => i < bars.Count - 20 ? -1e9f : (i - (bars.Count - 40)) * 10f, FY = p => (float)((103 - p) * 100) }),
                ("x = +1e12 bên phải", new FuncMap { FX = i => i > bars.Count - 5 ? 1e12f : (i - 100) * 10f, FY = p => (float)((103 - p) * 100) }),
            };
            foreach (var (name, m) in maps)
            {
                var ex = Catch(() =>
                {
                    using var bmp = new Bitmap(400, 300); using var g = Graphics.FromImage(bmp);
                    g.SetClip(m.Area);
                    RangeRenderer.Draw(g, m, sc, new RenderOptions { MarkStopHunt = true }, new Point(200, 150));
                });
                Check(ex == null, $"Draw không ngoại lệ khi {name}", ex == null ? "" : ex.GetType().Name + ": " + ex.Message);
            }
        }

        Console.WriteLine("[E8] Chuột trúng cả dấu ▼ lẫn cạnh hộp ⇒ dấu được ưu tiên");
        {
            var s = CleanRange(); s.MoveTo(1020); s.Bar(1020, 1029, 1018, 1029); int fb = s.Count; s.Bar(1029, 1029, 1018, 1020); s.Zig(1002, 1026, 2);
            var bars = s.Bars(); var lg = Run(bars);
            int from = 110, to = bars.Count - 1, W = 600, H = 400;
            var map = MapFor(bars, from, to, 10, W, H);
            map.PMin -= 20; map.PMax += 20;   // nén trục giá (~0,85 px/tick) ⇒ tam giác ▼ nằm trong vùng ±5 px của cạnh trên
            var sc = RangeRenderer.BuildScene(lg, to, from, to, new RenderOptions());
            var mk = sc.Marks.FirstOrDefault(m => m.Bar == fb);
            Check(mk != null, "có ▼ ở nến fail break sát cạnh");
            if (mk != null)
            {
                float tri = 9f, y = map.Y(mk.Price);
                float edgeY = map.Y(sc.Boxes[0].Top);
                var pt = new Point((int)map.X(fb), (int)Math.Ceiling(edgeY - 4));   // trong vùng bắt của ▼ (tới y−1) VÀ cách cạnh hộp ≤ 5 px
                bool nearEdge = Math.Abs(pt.Y - map.Y(sc.Boxes[0].Top)) <= 5;
                // ảnh có chuột vs ảnh chỉ vẽ tooltip "Fail break đỉnh" phải giống nhau ở vùng chữ ⇒ so chiều rộng chữ khác nhau
                Check(nearEdge, "điểm thử nằm trong ±5 px của cạnh trên", $"dy {pt.Y - map.Y(sc.Boxes[0].Top):F1}, tri {tri}");
                string tip = WhichTip(sc, map, pt, W, H);
                Check(tip == "mark", "tooltip là của dấu fail break (không phải hộp)", tip);
            }
        }

        Console.WriteLine("[E9] Mép: K=1, G=0, MaxLook nhỏ, MbrLen=1 — không ngoại lệ");
        {
            var tk = RandomTicks(11, 3000);
            var bars = tk.Select(x => new RBar(x.o * 0.1, x.h * 0.1, x.l * 0.1, x.c * 0.1)).ToList();
            foreach (var (name, p) in new (string, RangeParams)[]
            {
                ("K=1 G=0", new RangeParams { K = 1, G = 0 }), ("K=0", new RangeParams { K = 0 }),
                ("MaxLook=3", new RangeParams { MaxLook = 3 }), ("MbrLen=1", new RangeParams { MbrLen = 1 }),
                ("luật B + InsideRatio 0,9", new RangeParams { PivotRuleB = true, InsideRatio = 0.9 }),
            })
            {
                var ex = Catch(() => Run(bars, 0.1, p));
                Check(ex == null, $"tham số biên {name}: không ngoại lệ", ex == null ? "" : ex.GetType().Name + ": " + ex.Message);
            }
        }
    }

    /// <summary>Tooltip nào hiện: so ảnh có chuột với ảnh "chỉ dấu" và "chỉ hộp" (bỏ phần còn lại của cảnh).</summary>
    static string WhichTip(RenderScene sc, FakeMap map, Point pt, int w, int h)
    {
        var onlyBoxes = new RenderScene { PriceDecimals = sc.PriceDecimals }; onlyBoxes.Boxes.AddRange(sc.Boxes);
        bool boxTip = TipShown(onlyBoxes, map, new RenderOptions(), pt, w, h);
        if (!boxTip) return "hộp không bắt được ở điểm này";
        // cảnh đầy đủ: nếu tooltip là của hộp thì điểm ảnh chữ trắng giống hệt ảnh "chỉ hộp"
        return Snapshot(sc, map, pt, w, h) == Snapshot(onlyBoxes, map, pt, w, h) ? "box" : "mark";
    }

    /// <summary>Tập điểm ảnh chữ trắng (chỉ tooltip vẽ chữ trắng) để so chữ nào được vẽ — tooltip có thể lật sang trái chuột.</summary>
    static string Snapshot(RenderScene sc, FakeMap map, Point pt, int w, int h)
    {
        using var bmp = new Bitmap(w, h); using var g = Graphics.FromImage(bmp);
        g.Clear(Color.Black); g.SetClip(map.Area); RangeRenderer.Draw(g, map, sc, new RenderOptions(), pt);
        var sb = new System.Text.StringBuilder();
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            { var c = bmp.GetPixel(x, y); if (c.R == 255 && c.G == 255 && c.B == 255) sb.Append(x).Append(',').Append(y).Append(';'); }
        return sb.ToString();
    }
}
