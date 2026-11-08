// Render kịch bản ra PNG (tests/ui-out/) để xem bằng mắt: hộp không đè sai, tam giác đúng phía, chữ không tràn mép.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using RangeBox;

sealed class FakeMap : IChartMap
{
    public int First; public float Bw; public RectangleF Area; public double PMin, PMax;
    public float BarWidth => Bw;
    public RectangleF Clip => Area;
    public float X(int idx) => Area.Left + (idx - First + 0.5f) * Bw;
    public float Y(double p) => (float)(Area.Top + (PMax - p) / (PMax - PMin) * Area.Height);
}

static class UiTests
{
    static void Check(bool ok, string n, string d = "") => T.Check(ok, n, d);
    static readonly Color Bg = Color.FromArgb(18, 20, 26);

    /// <summary>Vẽ nến + cảnh range vào PNG. bars = OHLC giá; [from, to] = khoảng nến hiển thị.</summary>
    static RenderScene Render(string file, RangeLogic lg, IList<RBar> bars, int from, int to, float bw, RenderOptions opt,
                              Func<FakeMap, RenderScene, Point?> mouseFn = null, int width = 0, int height = 420, bool forming = false)
    {
        int nVis = to - from + 1;
        int w = width > 0 ? width : (int)Math.Max(320, nVis * bw + 70);
        var area = new RectangleF(10, 10, w - 70, height - 20);
        double lo = double.MaxValue, hi = double.MinValue;
        for (int i = from; i <= to && i < bars.Count; i++) { lo = Math.Min(lo, bars[i].Low); hi = Math.Max(hi, bars[i].High); }
        double pad = (hi - lo) * 0.08 + 0.2;
        var map = new FakeMap { First = from, Bw = bw, Area = area, PMin = lo - pad, PMax = hi + pad };
        int lastIdx = Math.Min(to, bars.Count - 1);
        var scene = RangeRenderer.BuildScene(lg, forming ? lastIdx : lastIdx, from, to, opt);
        using var bmp = new Bitmap(w, height);
        using var g = Graphics.FromImage(bmp);
        g.Clear(Bg);
        g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.AntiAlias;
        // trục giá
        using (var f = new Font("Arial", 8))
        using (var gp = new Pen(Color.FromArgb(40, 255, 255, 255)))
        {
            double stepP = Math.Max(0.1, Math.Round((map.PMax - map.PMin) / 6, 1));
            for (double p = Math.Ceiling(map.PMin / stepP) * stepP; p < map.PMax; p += stepP)
            {
                float y = map.Y(p);
                g.DrawLine(gp, area.Left, y, area.Right, y);
                g.DrawString(RangeRenderer.Fmt(p, 1), f, Brushes.Gray, area.Right + 4, y - 6);
            }
        }
        // nến
        for (int i = from; i <= lastIdx; i++)
        {
            var b = bars[i];
            float x = map.X(i);
            bool up = b.Close >= b.Open;
            var col = (forming && i == lastIdx) ? Color.FromArgb(200, 200, 120) : up ? Color.FromArgb(70, 170, 120) : Color.FromArgb(200, 80, 80);
            using var pen = new Pen(col, 1f);
            g.DrawLine(pen, x, map.Y(b.High), x, map.Y(b.Low));
            float y0 = map.Y(Math.Max(b.Open, b.Close)), y1 = map.Y(Math.Min(b.Open, b.Close));
            float bodyW = Math.Max(1f, bw * 0.7f);
            using var br = new SolidBrush(col);
            g.FillRectangle(br, x - bodyW / 2f, y0, bodyW, Math.Max(1f, y1 - y0));
        }
        Point? mouse = mouseFn?.Invoke(map, scene);
        g.SetClip(area);
        RangeRenderer.Draw(g, map, scene, opt, mouse);
        g.ResetClip();
        if (mouse.HasValue) using (var mp = new Pen(Color.White, 1f)) { g.DrawLine(mp, mouse.Value.X - 5, mouse.Value.Y, mouse.Value.X + 5, mouse.Value.Y); g.DrawLine(mp, mouse.Value.X, mouse.Value.Y - 5, mouse.Value.X, mouse.Value.Y + 5); }
        string dir = Path.Combine(T.Root(), "tests", "ui-out");
        Directory.CreateDirectory(dir);
        string path = Path.Combine(dir, file);
        bmp.Save(path, ImageFormat.Png);
        Check(File.Exists(path) && new FileInfo(path).Length > 1000, "PNG " + file);
        return scene;
    }

    static Point MarkPoint(FakeMap m, MarkView mk)
    {
        float tri = Math.Clamp(m.Bw * 0.9f, 4f, 9f);
        float y = m.Y(mk.Price);
        return new Point((int)m.X(mk.Bar), (int)(mk.Side > 0 ? y - 3 - tri / 2 : y + 3 + tri / 2));
    }

    public static void RunAll()
    {
        Console.WriteLine("[12] Render PNG (tests/ui-out/)");
        var all = new RenderOptions { MarkStopHunt = true };

        // 1) range hiệu lực, có nến đang chạy kéo hộp; chuột trên hộp
        {
            var s = Synth.Warm(); s.Zig(1002, 1026, 6); s.Bar(1014, 1036, 1012, 1018); s.Zig(1002, 1026, 2); s.Step(4);
            var bars = s.Bars(); var lg = new RangeLogic(0.1); lg.Process(bars.Take(bars.Count - 1).ToList());   // nến cuối = đang chạy, chưa nạp
            var sc = Render("1-range-hieu-luc.png", lg, bars, 110, bars.Count - 1, 10, all,
                (m, scn) => new Point((int)m.X(bars.Count - 6), (int)m.Y(101.4)), forming: true);
            Check(sc.Boxes.Count == 1 && !sc.Boxes[0].Broken && sc.Boxes[0].End == bars.Count - 1, "hộp hiệu lực kéo tới nến đang chạy");
        }
        // 2) range đã phá xuống + retest cạnh dưới; chuột trên hộp đã phá
        {
            var s = Synth.Warm(); s.Zig(1002, 1026, 5); s.MoveTo(1008);
            s.Trend(5, -6); s.Step(6); s.Step(6); s.Bar(990, 1003, 988, 992); s.Trend(12, -6); s.Trend(8, 3); s.Trend(6, -6);
            var bars = s.Bars(); var lg = new RangeLogic(0.1); lg.Process(bars);
            var sc = Render("2-range-da-pha-retest.png", lg, bars, 110, bars.Count - 1, 10, all,
                (m, scn) => new Point((int)m.X(scn.Boxes[0].Start + 3), (int)m.Y(101.2)));
            Check(sc.Boxes.Any(b => b.Broken && b.BreakSide < 0), "có hộp đã phá xuống (xám đứt + chấm retest)");
        }
        // 3) fail break 2 phía; chuột trên ▼
        {
            var s = Synth.Warm(); s.Zig(1002, 1026, 5); s.MoveTo(1020);
            s.Bar(1020, 1036, 1018, 1033); s.Bar(1033, 1035, 1023, 1024); s.MoveTo(1008);
            s.Bar(1008, 1010, 993, 995); s.Bar(995, 997, 992, 996); s.Bar(996, 1009, 994, 1007); s.Zig(1002, 1026, 2);
            var bars = s.Bars(); var lg = new RangeLogic(0.1); lg.Process(bars);
            var sc = Render("3-fail-break-2-phia.png", lg, bars, 110, bars.Count - 1, 10, all,
                (m, scn) => { var mk = scn.Marks.FirstOrDefault(x => x.Kind == RangeEventKind.FailBreak && x.Side > 0); return mk == null ? (Point?)null : MarkPoint(m, mk); });
            var top = sc.Marks.FirstOrDefault(x => x.Kind == RangeEventKind.FailBreak && x.Side > 0);
            var bot = sc.Marks.FirstOrDefault(x => x.Kind == RangeEventKind.FailBreak && x.Side < 0);
            Check(top != null && bot != null, "có ▼ fail đỉnh và ▲ fail đáy");
            Check(top != null && top.Price >= sc.Boxes[0].Top && bot != null && bot.Price <= sc.Boxes[0].Bottom, "tam giác nằm NGOÀI cạnh, chỉ vào lòng range");
        }
        // 4) hai range chồng một phần
        {
            var s = Synth.Warm(); s.Zig(1002, 1026, 5); s.MoveTo(1020);
            s.Step(14); s.Trend(20, 6); s.Trend(20, -6); s.MoveTo(1052); s.Zig(1022, 1052, 5);
            var bars = s.Bars(); var lg = new RangeLogic(0.1); lg.Process(bars);
            var sc = Render("4-hai-range-chong.png", lg, bars, 110, bars.Count - 1, 6, all, height: 520);
            Check(sc.Boxes.Count == 2, "vẽ cả 2 hộp", $"{sc.Boxes.Count}");
        }
        // 5) + 6) dữ liệu thật 90 ngày: zoom hẹp 3 px/nến và zoom thường
        {
            string path = Path.GetFullPath(Path.Combine(T.Root(), "..", "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv"));
            if (!File.Exists(path)) { Check(false, "thiếu dữ liệu 90 ngày cho PNG 5/6"); return; }
            var bars = LogicTests.LoadBars(path).Select(x => x.b).ToList();
            var lg = new RangeLogic(0.1); lg.Process(bars);
            var fb = lg.Events.First(e => e.Kind == RangeEventKind.FailBreak && e.Bar > 20000);
            Render("5-zoom-hep-3px.png", lg, bars, fb.Bar - 260, fb.Bar + 120, 3, all, height: 460);
            var sc = Render("6-du-lieu-that.png", lg, bars, fb.Bar - 90, fb.Bar + 50, 9, new RenderOptions(),
                (m, scn) => { var mk = scn.Marks.FirstOrDefault(x => x.Bar == fb.Bar); return mk == null ? (Point?)null : MarkPoint(m, mk); }, height: 460);
            Check(sc.Marks.Count > 0 && sc.Marks.All(x => x.Kind == RangeEventKind.FailBreak), "mặc định: chỉ dấu fail break, không chấm râu quét");
            // tooltip sát mép phải không tràn: chuột ở mép phải, ĐẶT TRÊN CẠNH TRÊN hộp (tooltip hộp chỉ bắt ở cạnh ±5 px — REVIEW-1 mục 1)
            Render("7-tooltip-mep-phai.png", lg, bars, fb.Bar - 60, fb.Bar + 10, 9, new RenderOptions(),
                (m, scn) => scn.Boxes.Count == 0 ? (Point?)null : new Point((int)(m.Area.Right - 4), (int)Math.Round(m.Y(scn.Boxes[^1].Top)) + 2), height: 360);
            // chuột GIỮA lòng hộp ⇒ KHÔNG có tooltip (khỏi che nến)
            Render("7b-chuot-giua-hop-khong-tooltip.png", lg, bars, fb.Bar - 60, fb.Bar + 10, 9, new RenderOptions(),
                (m, scn) => scn.Boxes.Count == 0 ? (Point?)null : new Point((int)(m.Area.Right - 40), (int)m.Y((scn.Boxes[^1].Top + scn.Boxes[^1].Bottom) / 2)), height: 360);
        }
    }
}
