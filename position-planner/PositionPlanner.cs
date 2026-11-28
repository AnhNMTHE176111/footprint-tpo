// ============================================================================
//  PositionPlanner — indicator "Position Planner" cho Optimus Flow (lớp dán Quantower)
// ============================================================================
//  Thanh nút góc dưới-trái: ▲ Long · ▼ Short · Xoá hết. Bấm Long/Short rồi bấm 3 lần trên chart: giá vào → SL → TP.
//  Bấm vào hộp để chọn (hiện nhãn, 4 điểm kéo, ✕), bấm ra ngoài thì nhãn ẩn. Nét đứt = giá chạy theo lệnh tới khi chạm SL/TP.
//  Lệnh được lưu theo mã ở %LOCALAPPDATA%\PositionPlanner\<mã>.txt (tự chép từ thư mục VeLenh cũ nếu có).
//  Không có ô Settings nào.
// ============================================================================
namespace PositionPlannerNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.IO;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;
    using TradingPlatform.BusinessLayer.Native;

    /// <summary>Ánh xạ toạ độ theo cửa sổ chính của chart; thời gian sau nến cuối thì tự ngoại suy theo bề rộng nến.</summary>
    internal sealed class QwMap : IVlMap
    {
        private readonly IChartWindowCoordinatesConverter _c;
        private readonly DateTime _last; private readonly float _xLast, _px;
        private readonly double _p0; private readonly float _y0, _y1;
        public TimeSpan Bar { get; }

        public QwMap(IChartWindowCoordinatesConverter c, DateTime lastBar, TimeSpan bar, float pxPerBar, double priceRef)
        {
            _c = c; _last = lastBar; Bar = bar.Ticks > 0 ? bar : TimeSpan.FromMinutes(1);
            _xLast = (float)c.GetChartX(lastBar);
            _px = pxPerBar > 0.5f ? pxPerBar : 1f;
            _p0 = Math.Max(1, Math.Abs(priceRef));
            _y0 = (float)c.GetChartY(_p0); _y1 = (float)c.GetChartY(_p0 + 1);
        }

        public float X(DateTime t)
        {
            if (t <= _last) return (float)_c.GetChartX(t);
            return _xLast + (float)((t - _last).Ticks / (double)Bar.Ticks) * _px;
        }
        public float Y(double price) => (float)_c.GetChartY(price);
        public double Price(float y) => Math.Abs(_y1 - _y0) < 1e-6 ? _p0 : _p0 + (y - _y0) / (_y1 - _y0);
        public DateTime Time(float x)
        {
            if (x > _xLast) return _last + TimeSpan.FromTicks((long)Math.Round((x - _xLast) / _px) * Bar.Ticks);
            var t = _c.GetTime(x);
            return new DateTime(t.Ticks - t.Ticks % Bar.Ticks, DateTimeKind.Utc);
        }
    }

    public class PositionPlanner : Indicator
    {
        private readonly object _lk = new();
        private readonly VlEditor _ed = new();
        private IChart _chart;
        private string _file;

        private static readonly Color CTp = Color.FromArgb(0, 150, 120), CSl = Color.FromArgb(225, 40, 40), CHandle = Color.FromArgb(100, 100, 255);

        public PositionPlanner() : base()
        {
            Name = "Position Planner";
            Description = "Công cụ vẽ lệnh Long/Short: SL, TP tính bằng điểm (1 điểm = 1,0 giá) và R:R. Bấm nút góc dưới-trái để vẽ, kéo 4 điểm để chỉnh, ✕ để xoá.";
            SeparateWindow = false;
        }

        protected override void OnInit()
        {
            lock (_lk)
            {
                _ed.Tick = Symbol?.TickSize > 0 ? Symbol.TickSize : 0.25;
                string sym = Symbol?.Name ?? "chart";
                foreach (var ch in Path.GetInvalidFileNameChars()) sym = sym.Replace(ch, '_');
                var dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PositionPlanner");
                _file = Path.Combine(dir, sym + ".txt");
                var old = Path.Combine(Path.GetDirectoryName(dir), "VeLenh", sym + ".txt");
                try { if (!File.Exists(_file) && File.Exists(old)) { Directory.CreateDirectory(dir); File.Copy(old, _file); } } catch { }
                try { if (File.Exists(_file)) _ed.SetItems(VlFmt.Load(File.ReadAllText(_file))); } catch { }
            }
        }

        protected override void OnUpdate(UpdateArgs args) { }

        protected override void OnClear() => Detach();
        public override void Dispose() { Detach(); base.Dispose(); }

        private void Attach()
        {
            var ch = CurrentChart;
            if (ch == null || ReferenceEquals(ch, _chart)) return;
            Detach();
            _chart = ch;
            ch.MouseDown += OnDown; ch.MouseMove += OnMove; ch.MouseUp += OnUp;
        }
        private void Detach()
        {
            var ch = _chart; _chart = null;
            if (ch != null) try { ch.MouseDown -= OnDown; ch.MouseMove -= OnMove; ch.MouseUp -= OnUp; } catch { }
        }

        private void SaveIfDirty()
        {
            if (!_ed.Dirty || _file == null || _ed.Mode == VlMode.Drag) return;
            _ed.Dirty = false;
            try { Directory.CreateDirectory(Path.GetDirectoryName(_file)); File.WriteAllText(_file, VlFmt.Save(_ed.Items)); } catch { }
        }

        private QwMap MakeMap()
        {
            var ch = CurrentChart;
            if (ch?.MainWindow == null || HistoricalData == null || Count < 2) return null;
            DateTime t0 = Time(0), t1 = Time(1);
            var bar = t0 - t1;
            for (int k = 1; k < Math.Min(Count - 1, 6); k++) { var d = Time(k) - Time(k + 1); if (d.Ticks > 0 && d < bar) bar = d; }
            var conv = ch.MainWindow.CoordinatesConverter;
            float px = (float)(conv.GetChartX(t0) - conv.GetChartX(t1));
            if (px <= 0.5f) px = Math.Max(1, ch.BarsWidth);
            return new QwMap(conv, t0, bar, px, Close(0));
        }

        private void OnDown(object sender, ChartMouseNativeEventArgs e)
        {
            try
            {
                if (e.Window == null || !e.Window.IsMainWindow) return;
                var m = MakeMap(); if (m == null) return;
                bool used, cap;
                lock (_lk) { used = _ed.Down(e.X, e.Y, e.Button == NativeMouseButtons.Left, m, out cap); SaveIfDirty(); }
                bool rd; lock (_lk) { rd = _ed.Redraw; _ed.Redraw = false; }
                if (rd) e.NeedRedraw = true;
                if (!used) return;
                e.Handled = true; e.NeedRedraw = true;
                if (cap) e.NeedMouseCapture = true;
            }
            catch { }
        }

        private void OnMove(object sender, ChartMouseNativeEventArgs e)
        {
            try
            {
                var m = MakeMap(); if (m == null) return;
                (bool handled, bool redraw) r;
                lock (_lk) r = _ed.Move(e.X, e.Y, m);
                if (r.handled) e.Handled = true;
                if (r.redraw) e.NeedRedraw = true;
            }
            catch { }
        }

        private void OnUp(object sender, ChartMouseNativeEventArgs e)
        {
            try
            {
                bool used;
                lock (_lk) { used = _ed.Up(); SaveIfDirty(); }
                if (used) { e.Handled = true; e.NeedRedraw = true; }
            }
            catch { }
        }

        // ------------------------------------------------------------------ vẽ
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            try
            {
                if (CurrentChart == null) return;
                var win = CurrentChart.Windows[args.WindowIndex];
                if (!win.IsMainWindow) return;
                Attach();
                var m = MakeMap(); if (m == null) return;
                var gr = args.Graphics; var clip = win.ClientRectangle;
                var prev = gr.Clip; gr.SetClip(clip);
                gr.SmoothingMode = SmoothingMode.AntiAlias;
                using var fLbl = new Font("Segoe UI", 11f, FontStyle.Bold);
                using var fBtn = new Font("Segoe UI", 9.5f, FontStyle.Bold);
                lock (_lk)
                {
                    var bars = BarsFrom(_ed.Items);
                    foreach (var p in _ed.Items) DrawPos(gr, m, p, fLbl, false, bars);
                    if (_ed.Draft != null) DrawPos(gr, m, _ed.Draft, fLbl, true, null);
                    _ed.LayoutButtons(clip.Left + 8, clip.Bottom - 34);
                    DrawButtons(gr, fBtn);
                }
                gr.Clip = prev;
            }
            catch { }
        }

        private void DrawPos(Graphics gr, IVlMap m, VlPos p, Font f, bool draft, List<VlBar> bars)
        {
            var g = VlEditor.Geo(p, m);
            float w = Math.Max(2, g.X1 - g.X0);
            using (var b = new SolidBrush(Color.FromArgb(55, CTp))) gr.FillRectangle(b, g.X0, Math.Min(g.YE, g.YTp), w, Math.Abs(g.YTp - g.YE));
            using (var b = new SolidBrush(Color.FromArgb(55, CSl))) gr.FillRectangle(b, g.X0, Math.Min(g.YE, g.YSl), w, Math.Abs(g.YSl - g.YE));
            using (var pe = new Pen(Color.FromArgb(200, CTp), 1.5f)) gr.DrawLine(pe, g.X0, g.YTp, g.X1, g.YTp);
            using (var pe = new Pen(Color.FromArgb(200, CSl), 1.5f)) gr.DrawLine(pe, g.X0, g.YSl, g.X1, g.YSl);
            using (var pe = new Pen(Color.FromArgb(220, 120, 120, 120), 1.5f)) gr.DrawLine(pe, g.X0, g.YE, g.X1, g.YE);

            if (bars != null)
            {
                var path = VlTrack.Run(p, bars);
                if (path.Ok)
                {
                    // tô đậm vùng giá đã chạy (như TradingView): từ giá vào tới giá cuối, từ T0 tới nến cuối/nến chạm
                    int ps = path.Side(p);
                    if (ps != 0)
                    {
                        float xe = Math.Min(m.X(path.EndT), g.X1), ye = m.Y(path.EndPrice);
                        using var bf = new SolidBrush(Color.FromArgb(90, ps > 0 ? CTp : CSl));
                        gr.FillRectangle(bf, g.X0, Math.Min(g.YE, ye), Math.Max(1, xe - g.X0), Math.Abs(ye - g.YE));
                    }
                    using var pe = new Pen(Color.FromArgb(200, 110, 110, 120), 1.5f) { DashStyle = DashStyle.Dash };
                    gr.DrawLine(pe, g.X0, g.YE, m.X(path.EndT), m.Y(path.EndPrice));
                }
            }

            bool sel = !draft && _ed.SelectedId == p.Id;
            if (!draft && !_ed.ShowLabels(p)) return;
            float cx = g.X0 + w / 2f;
            bool tpUp = g.YTp < g.YE;
            Label(gr, f, VlFmt.TpText(p), CTp, cx, tpUp ? g.YTp - 4 : g.YTp + 4, tpUp);
            Label(gr, f, VlFmt.SlText(p), CSl, cx, tpUp ? g.YSl + 4 : g.YSl - 4, !tpUp);
            Label(gr, f, VlFmt.RrText(p), Color.FromArgb(235, 45, 45, 55), cx, g.YE, null);

            if (!sel) return;
            bool hov = _ed.HoverId == p.Id;
            Handle(gr, g.HTp, hov && _ed.HoverPart == VlPart.Tp);
            Handle(gr, g.HSl, hov && _ed.HoverPart == VlPart.Sl);
            Handle(gr, g.HEntry, hov && _ed.HoverPart == VlPart.Entry);
            Handle(gr, g.HRight, hov && _ed.HoverPart == VlPart.Right);
            var c = g.Close;
            using (var b = new SolidBrush(Color.FromArgb(hov && _ed.HoverPart == VlPart.Close ? 230 : 150, 60, 60, 70))) gr.FillRectangle(b, c);
            using (var pe = new Pen(Color.White, 1.6f))
            {
                gr.DrawLine(pe, c.X + 4, c.Y + 4, c.Right - 4, c.Bottom - 4);
                gr.DrawLine(pe, c.Right - 4, c.Y + 4, c.X + 4, c.Bottom - 4);
            }
        }

        /// <summary>Nến (tăng dần) từ T0 sớm nhất của các lệnh tới nến cuối.</summary>
        private List<VlBar> BarsFrom(List<VlPos> items)
        {
            var list = new List<VlBar>();
            if (items.Count == 0 || Count < 1) return list;
            var t0 = DateTime.MaxValue;
            foreach (var p in items) if (p.T0 < t0) t0 = p.T0;
            for (int k = 0; k < Count; k++)
            {
                var t = Time(k);
                if (t < t0) break;
                list.Add(new VlBar(t, High(k), Low(k), Close(k)));
            }
            list.Reverse();
            return list;
        }

        /// <summary>Nhãn nền đặc, chữ trắng, căn giữa theo cx. above: true = nằm trên y, false = dưới y, null = giữa y.</summary>
        private static void Label(Graphics gr, Font f, string text, Color bg, float cx, float y, bool? above)
        {
            var sz = gr.MeasureString(text, f);
            float w = sz.Width + 10, h = sz.Height + 4;
            float top = above == true ? y - h : above == false ? y : y - h / 2f;
            var r = new RectangleF(cx - w / 2f, top, w, h);
            using (var b = new SolidBrush(bg)) gr.FillRectangle(b, r);
            using (var tb = new SolidBrush(Color.White)) gr.DrawString(text, f, tb, r.X + 5, r.Y + 2);
        }

        private static void Handle(Graphics gr, PointF h, bool hover)
        {
            float r = hover ? VlEditor.HandleR + 2 : VlEditor.HandleR;
            using var b = new SolidBrush(CHandle);
            gr.FillEllipse(b, h.X - r, h.Y - r, 2 * r, 2 * r);
            if (hover) using (var pe = new Pen(Color.White, 1.5f)) gr.DrawEllipse(pe, h.X - r, h.Y - r, 2 * r, 2 * r);
        }

        private void DrawButtons(Graphics gr, Font f)
        {
            foreach (var bt in _ed.Buttons)
            {
                bool on = (bt.Key == "long" && _ed.PendingSide == 1) || (bt.Key == "short" && _ed.PendingSide == -1);
                Color bg = bt.Key == "long" ? CTp : bt.Key == "short" ? CSl : Color.FromArgb(70, 70, 80);
                using (var b = new SolidBrush(Color.FromArgb(on ? 255 : 190, bg))) gr.FillRectangle(b, bt.Box);
                if (on) using (var pe = new Pen(Color.White, 2f)) gr.DrawRectangle(pe, bt.Box.X, bt.Box.Y, bt.Box.Width, bt.Box.Height);
                var sz = gr.MeasureString(bt.Text, f);
                using var tb = new SolidBrush(Color.White);
                gr.DrawString(bt.Text, f, tb, bt.Box.X + (bt.Box.Width - sz.Width) / 2f, bt.Box.Y + (bt.Box.Height - sz.Height) / 2f);
            }
            var hint = _ed.Hint;
            if (hint == null || _ed.Buttons.Count == 0) return;
            var last = _ed.Buttons[_ed.Buttons.Count - 1].Box;
            var hs = gr.MeasureString(hint, f);
            var r = new RectangleF(last.Right + 10, last.Y, hs.Width + 10, last.Height);
            using (var b = new SolidBrush(Color.FromArgb(220, 30, 30, 38))) gr.FillRectangle(b, r);
            using (var tb = new SolidBrush(Color.FromArgb(255, 230, 200)))
                gr.DrawString(hint, f, tb, r.X + 5, r.Y + (r.Height - hs.Height) / 2f);
        }
    }
}
