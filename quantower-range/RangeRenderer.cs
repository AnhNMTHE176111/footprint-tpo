// ============================================================================
//  RangeRenderer — vẽ hộp range + dấu fail break / râu quét bằng GDI+ (không phụ thuộc Quantower)
// ============================================================================
//  Tách khỏi RangeBox.cs để test render ra PNG bằng IChartMap giả (tests/ui-out/*.png).
//  Quy ước hình (BRAINSTORM mục 6 + 7b):
//    • hộp đang hiệu lực: viền 1 px xanh lơ nhạt, nền alpha ~25, kéo tới nến hiện tại (cả nến đang chạy)
//    • hộp đã phá: viền xám đứt tới nến phá + cạnh bị phá kẻ chấm thêm G nến (mốc retest)
//    • fail break: tam giác chỉ VÀO LÒNG range (▼ cạnh trên = tìm sell, ▲ cạnh dưới = tìm buy)
//    • râu quét cạnh: chấm rỗng nhỏ ở đầu râu
//    • tooltip ngắn, nền đặc + viền màu (kiểu Order Flow Bubbles)
// ============================================================================
namespace RangeBox
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Globalization;

    public interface IChartMap
    {
        float X(int barIdx);          // tâm nến (px), kể cả chỉ số vượt nến cuối (ngoại suy)
        float Y(double price);
        float BarWidth { get; }       // px mỗi nến
        RectangleF Clip { get; }
    }

    public sealed class RenderOptions
    {
        public bool ShowBroken = true;
        public bool MarkFailBreak = true;
        public bool MarkStopHunt = false;
        public int RetestBars = 30;   // = RangeParams.G
    }

    public sealed class BoxView
    {
        public int Start, End;        // chỉ số nến
        public double Top, Bottom;    // giá
        public bool Broken;
        public int BreakSide;         // +1 lên, −1 xuống (khi Broken)
        public int BreakIdx = -1;
    }

    public sealed class MarkView
    {
        public int Bar;
        public RangeEventKind Kind;   // FailBreak / StopHunt
        public int Side;              // +1 cạnh trên, −1 cạnh dưới
        public double Price;          // giá neo: FailBreak = cực của nến ở phía cạnh; StopHunt = đầu râu
    }

    public sealed class RenderScene
    {
        public readonly List<BoxView> Boxes = new List<BoxView>();
        public readonly List<MarkView> Marks = new List<MarkView>();
        public int PriceDecimals = 1;
    }

    public static class RangeRenderer
    {
        public static readonly Color ActiveColor = Color.FromArgb(120, 200, 235);
        public static readonly Color BrokenColor = Color.FromArgb(150, 150, 150);
        public static readonly Color SellColor = Color.FromArgb(240, 90, 110);
        public static readonly Color BuyColor = Color.FromArgb(60, 200, 120);
        public static readonly Color HuntColor = Color.FromArgb(235, 190, 80);
        public const int FillAlpha = 25;
        /// <summary>Tooltip hộp chỉ bật khi chuột cách cạnh trên/dưới (hoặc nét chấm retest) ≤ ngần này px (REVIEW-1 mục 1).</summary>
        public const float EdgeHitPx = 5f;

        /// <summary>Vùng bắt chuột của một hộp: 2 cạnh ngang trong [X0, X1]; hộp đã phá thêm nét chấm [X1, XR] ở YE.</summary>
        public readonly struct BoxHit
        {
            public readonly float X0, X1, YTop, YBot, XR, YE;
            public readonly bool HasExt;
            public BoxHit(float x0, float x1, float yTop, float yBot, bool hasExt, float xr, float ye)
            { X0 = x0; X1 = x1; YTop = yTop; YBot = yBot; HasExt = hasExt; XR = xr; YE = ye; }
            public bool Contains(float mx, float my)
            {
                if (mx >= X0 && mx <= X1 && (Math.Abs(my - YTop) <= EdgeHitPx || Math.Abs(my - YBot) <= EdgeHitPx)) return true;
                return HasExt && mx >= X1 && mx <= XR && Math.Abs(my - YE) <= EdgeHitPx;
            }
        }

        /// <summary>Dựng cảnh từ logic. lastBarIdx = nến cuối trên chart (kể cả nến đang chạy) để hộp hiệu lực kéo tới đó.
        /// li/ri = khoảng nến nhìn thấy (lọc bớt). Gọi trong lock của logic.</summary>
        public static RenderScene BuildScene(RangeLogic logic, int lastBarIdx, int li, int ri, RenderOptions opt)
        {
            var sc = new RenderScene();
            double t = logic.Tick;
            sc.PriceDecimals = Math.Max(0, (int)Math.Ceiling(-Math.Log10(t) - 1e-9));
            foreach (var r in logic.Ranges)
            {
                bool broken = r.State == RangeState.Broken || r.State == RangeState.Dead;
                if (broken && !opt.ShowBroken) continue;
                int end = broken ? r.BreakIdx : lastBarIdx;
                int visEnd = broken ? r.BreakIdx + opt.RetestBars : end;
                if (r.Start > ri || visEnd < li) continue;
                sc.Boxes.Add(new BoxView { Start = r.Start, End = end, Top = r.Top * t, Bottom = r.Bottom * t, Broken = broken, BreakSide = r.BreakSide, BreakIdx = r.BreakIdx });
            }
            if (opt.MarkFailBreak || opt.MarkStopHunt)
            {
                var ev = logic.Events;
                // sự kiện xếp theo nến tăng dần → tìm nhị phân sự kiện đầu tiên có Bar ≥ li
                int a = 0, z = ev.Count;
                while (a < z) { int mid = (a + z) >> 1; if (ev[mid].Bar < li) a = mid + 1; else z = mid; }
                for (int k = a; k < ev.Count; k++)
                {
                    var e = ev[k];
                    if (e.Bar > ri) break;
                    if (e.Kind == RangeEventKind.FailBreak && opt.MarkFailBreak)
                    {
                        double p = e.Side > 0 ? Math.Max(e.Top, logic.HighTicks(e.Bar)) : Math.Min(e.Bottom, logic.LowTicks(e.Bar));
                        sc.Marks.Add(new MarkView { Bar = e.Bar, Kind = e.Kind, Side = e.Side, Price = p * t });
                    }
                    else if (e.Kind == RangeEventKind.StopHunt && opt.MarkStopHunt)
                    {
                        double p = e.Side > 0 ? logic.HighTicks(e.Bar) : logic.LowTicks(e.Bar);
                        sc.Marks.Add(new MarkView { Bar = e.Bar, Kind = e.Kind, Side = e.Side, Price = p * t });
                    }
                }
            }
            return sc;
        }

        public static string Fmt(double price, int dec)
            => price.ToString("F" + dec, CultureInfo.InvariantCulture).Replace('.', ',');

        public static string BoxTip(BoxView b, int dec)
        {
            int n = b.End - b.Start + 1;
            string s = $"Range {Fmt(b.Bottom, dec)}–{Fmt(b.Top, dec)} · {n} nến";
            if (b.Broken) s += b.BreakSide > 0 ? " · Phá lên" : " · Phá xuống";
            return s;
        }

        public static string MarkTip(MarkView m)
            => m.Kind == RangeEventKind.FailBreak ? (m.Side > 0 ? "Fail break đỉnh" : "Fail break đáy")
                                                  : (m.Side > 0 ? "Râu quét đỉnh" : "Râu quét đáy");

        /// <summary>Vẽ cảnh. mouse = vị trí chuột (null nếu không có) để hiện tooltip.</summary>
        public static void Draw(Graphics g, IChartMap map, RenderScene sc, RenderOptions opt, Point? mouse)
        {
            var clip = map.Clip;
            float bw = Math.Max(1f, map.BarWidth);
            float half = bw / 2f;
            var oldSmooth = g.SmoothingMode;
            string tip = null; Color tipCol = Color.White; float tipX = 0, tipY = 0;
            var boxHits = new List<(BoxHit h, string t, Color c)>();
            try
            {
                // 1) hộp đã phá trước (nằm dưới), rồi hộp hiệu lực
                for (int pass = 0; pass < 2; pass++)
                {
                    foreach (var b in sc.Boxes)
                    {
                        if (b.Broken != (pass == 0)) continue;
                        // kẹp x vào quanh vùng nhìn thấy: hộp rất dài/toạ độ ngoại suy lớn làm GDI+ ném OverflowException (tester E7)
                        float x0 = ClampX(map.X(b.Start) - half, clip), x1 = ClampX(map.X(b.End) + half, clip);
                        float y0 = map.Y(b.Top), y1 = map.Y(b.Bottom);
                        if (y1 < y0) { var tt = y0; y0 = y1; y1 = tt; }
                        var rect = new RectangleF(x0, y0, Math.Max(1f, x1 - x0), Math.Max(1f, y1 - y0));
                        g.SmoothingMode = SmoothingMode.None;
                        if (!b.Broken)
                        {
                            using (var fill = new SolidBrush(Color.FromArgb(FillAlpha, ActiveColor))) g.FillRectangle(fill, rect);
                            using (var pen = new Pen(Color.FromArgb(200, ActiveColor), 1f)) g.DrawRectangle(pen, rect.X, rect.Y, rect.Width, rect.Height);
                            boxHits.Add((new BoxHit(x0, x1, y0, y1, false, 0, 0), BoxTip(b, sc.PriceDecimals), ActiveColor));
                        }
                        else
                        {
                            using (var pen = new Pen(Color.FromArgb(170, BrokenColor), 1f) { DashStyle = DashStyle.Dash })
                                g.DrawRectangle(pen, rect.X, rect.Y, rect.Width, rect.Height);
                            // cạnh bị phá: kẻ chấm thêm RetestBars nến về bên phải (mốc retest)
                            double edge = b.BreakSide > 0 ? b.Top : b.Bottom;
                            float ye = map.Y(edge);
                            float xr = ClampX(map.X(b.BreakIdx + opt.RetestBars) + half, clip);
                            using (var dp = new Pen(Color.FromArgb(150, BrokenColor), 1f) { DashStyle = DashStyle.Dot })
                                g.DrawLine(dp, x1, ye, xr, ye);
                            boxHits.Add((new BoxHit(x0, x1, y0, y1, true, xr, ye), BoxTip(b, sc.PriceDecimals), BrokenColor));
                        }
                    }
                }

                // 2) dấu sự kiện
                g.SmoothingMode = SmoothingMode.AntiAlias;
                float tri = Math.Clamp(bw * 0.9f, 4f, 9f);
                float dot = Math.Clamp(bw * 0.35f, 1f, 4f);   // tối thiểu 1 (cũ 2): zoom 3 px/nến 2 chấm râu quét liền nhau không dính (tester A12)
                foreach (var m in sc.Marks)
                {
                    float cx = map.X(m.Bar), y = map.Y(m.Price);
                    if (!(cx >= clip.Left - 20 && cx <= clip.Right + 20) || !float.IsFinite(y)) continue;
                    RectangleF hit;
                    Color col;
                    if (m.Kind == RangeEventKind.FailBreak)
                    {
                        PointF[] pts;
                        if (m.Side > 0)
                        {   // ▼ phía trên nến, mũi chỉ xuống vào lòng range
                            float tipY0 = y - 3f;
                            pts = new[] { new PointF(cx - tri / 2f, tipY0 - tri), new PointF(cx + tri / 2f, tipY0 - tri), new PointF(cx, tipY0) };
                            col = SellColor;
                            hit = new RectangleF(cx - tri / 2f - 2, tipY0 - tri - 2, tri + 4, tri + 4);
                        }
                        else
                        {   // ▲ phía dưới nến, mũi chỉ lên vào lòng range
                            float tipY0 = y + 3f;
                            pts = new[] { new PointF(cx - tri / 2f, tipY0 + tri), new PointF(cx + tri / 2f, tipY0 + tri), new PointF(cx, tipY0) };
                            col = BuyColor;
                            hit = new RectangleF(cx - tri / 2f - 2, tipY0 - 2, tri + 4, tri + 4);
                        }
                        using (var br = new SolidBrush(col)) g.FillPolygon(br, pts);
                    }
                    else
                    {
                        col = HuntColor;
                        using (var pen = new Pen(col, 1.2f)) g.DrawEllipse(pen, cx - dot, y - dot, dot * 2, dot * 2);
                        hit = new RectangleF(cx - dot - 2, y - dot - 2, dot * 2 + 4, dot * 2 + 4);
                    }
                    if (tip == null && mouse.HasValue && hit.Contains(mouse.Value.X, mouse.Value.Y))
                    { tip = MarkTip(m); tipCol = col; tipX = mouse.Value.X; tipY = mouse.Value.Y; }
                }

                // 3) tooltip: dấu ưu tiên; không trúng dấu thì xét CẠNH hộp ±EdgeHitPx (hộp hiệu lực vẽ sau = trên cùng).
                //    Chuột ở giữa lòng hộp KHÔNG hiện chữ (khỏi che nến).
                if (tip == null && mouse.HasValue)
                    for (int k = boxHits.Count - 1; k >= 0; k--)
                        if (boxHits[k].h.Contains(mouse.Value.X, mouse.Value.Y)) { tip = boxHits[k].t; tipCol = boxHits[k].c; tipX = mouse.Value.X; tipY = mouse.Value.Y; break; }
                if (tip != null) DrawTip(g, clip, tip, tipCol, tipX, tipY);
            }
            finally { g.SmoothingMode = oldSmooth; }
        }

        static float ClampX(float x, RectangleF clip)
            => float.IsNaN(x) ? clip.Left - 50 : Math.Clamp(x, clip.Left - 50, clip.Right + 50);

        /// <summary>Khung chữ nền ĐẶC + dải màu trái + viền màu — chép kiểu Order Flow Bubbles (2026-11-08).</summary>
        public static void DrawTip(Graphics g, RectangleF clip, string text, Color col, float mx, float my)
        {
            using var font = new Font("Arial", 10, FontStyle.Bold);
            var sz = g.MeasureString(text, font);
            float w = sz.Width + 12, h = sz.Height + 6;
            float bx = mx + 12, by = my - h - 4;
            if (bx + w > clip.Right) bx = Math.Max(clip.Left, mx - 12 - w);
            if (by < clip.Top) by = my + 12;
            if (by + h > clip.Bottom) by = Math.Max(clip.Top, clip.Bottom - h);
            using (var bg = new SolidBrush(Color.FromArgb(255, 24, 26, 32))) g.FillRectangle(bg, bx, by, w, h);
            using (var strip = new SolidBrush(Color.FromArgb(255, col))) g.FillRectangle(strip, bx, by, 4, h);
            using (var bp = new Pen(Color.FromArgb(255, col), 1.5f)) g.DrawRectangle(bp, bx, by, w, h);
            g.DrawString(text, font, Brushes.White, bx + 8, by + 3);
        }
    }
}
