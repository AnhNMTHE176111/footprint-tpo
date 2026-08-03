// ============================================================================
//  UiKit — BẢNG TƯƠNG TÁC + NHẢY CHART + KÍNH LÚP  (dùng chung 3 indicator)
// ============================================================================
//  Tách ra từ WyckoffRunner v3 (commit 31b1d9d) để EntrySignal và RunnerSignal
//  dùng CHUNG một bản cài đặt — trước đây mỗi indicator một kiểu bảng (PanelDrag
//  chỉ là danh sách chữ tĩnh, không cuộn/không bấm được).
//
//  Gồm 4 mảnh:
//    UiPanel   — bảng kéo-thả: khối header (thống kê) + N DANH SÁCH cuộn được;
//                hover đổi nền, bấm chọn dòng, nháy đúp = hành động phụ.
//    ChartNav  — dò (reflection) thành viên cuộn/zoom của chart Quantower.
//    UiNav     — vòng lặp kín canh chart tới đúng mốc thời gian sau khi bấm dòng.
//    UiMiniChart — khung "kính lúp": vẽ nến trong 1 hộp trên chart + trả về 2 hàm
//                ánh xạ toạ độ để nơi gọi vẽ chồng lớp riêng (lệnh, sơ đồ Wyckoff…).
//
//  ĐƯỢC CONCAT vào đầu mỗi file indicator khi build → MỌI `using` nằm BÊN TRONG
//  namespace (không có using top-level) để nối file hợp lệ.
// ============================================================================
namespace TpoSuite
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Linq;
    using System.Reflection;
    using System.Text;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;
    using TradingPlatform.BusinessLayer.Native;

    // Một dòng trong danh sách: 1 dòng chính + 1 dòng phụ (vì sao / chi tiết).
    internal sealed class UiRow
    {
        public string Key = "", L1 = "", L2;
        public Color C1 = Color.White, C2 = Color.Silver;
        public int NavIdx = -1;          // chỉ số HistoricalData để nhảy tới (-1 = không nhảy được)
        public int NavSpan;              // độ rộng (nến) của đối tượng — để zoom vừa khung
        public double NavPrice = double.NaN;
    }

    internal sealed class UiSection
    {
        public string Title = "", Hint = "";
        public List<UiRow> Rows = new();
        public string Empty = "(chưa có gì)";
        public int Vis = 6;          // số dòng người dùng đặt trong input
        public int VisEff = 6;       // số dòng THỰC vẽ (bị bóp lại nếu bảng cao quá chart)
        public int Scroll;
        public bool Collapsed;
        public string SelKey = "";
        public RectangleF TitleBox, View, Track, Thumb;
        public float RowH = 30;
        public int MaxScroll => Math.Max(0, Rows.Count - VisEff);
    }

    //  Chỉ UI thread đụng tới lớp này; vẫn khoá _lk vì Quantower gọi chuột và vẽ ở 2 điểm vào khác nhau.
    internal sealed class UiPanel
    {
        public const float Toggle = 15f;
        private readonly object _lk = new object();
        private IChart _chart;
        private bool _drag; private float _gx, _gy;
        private float? _px, _py;
        private bool _collapsed;
        private RectangleF _pan, _head, _toggle;
        private readonly UiSection[] _sec;
        private int _hovSec = -1, _hovRow = -1;
        private int _thSec = -1; private float _thGrab;

        public RectangleF CloseBox;                    // nút ✕ của kính lúp (Empty = không có)
        public Action OnClose;
        public Action<int, UiRow, bool> OnActivate;    // (mục, dòng, nháy-đúp)

        public UiPanel(int sections = 2)
        {
            _sec = new UiSection[Math.Max(1, sections)];
            for (int i = 0; i < _sec.Length; i++) _sec[i] = new UiSection();
        }

        public int SectionCount => _sec.Length;
        public UiSection Sec(int i) => _sec[i];
        public string SelKeyOf(int i) { lock (_lk) return _sec[i].SelKey; }

        public void Attach(IChart chart)
        {
            if (chart == null || ReferenceEquals(_chart, chart)) return;
            Detach();
            _chart = chart;
            _chart.MouseDown += OnDown; _chart.MouseMove += OnMove;
            _chart.MouseUp += OnUp; _chart.MouseWheel += OnWheel;
        }
        public void Detach()
        {
            if (_chart == null) return;
            try { _chart.MouseDown -= OnDown; _chart.MouseMove -= OnMove; _chart.MouseUp -= OnUp; _chart.MouseWheel -= OnWheel; } catch { }
            _chart = null; _drag = false; _thSec = -1;
        }

        // Bảng đang TẮT (hoặc chưa có dữ liệu) → xoá hình học, nếu không chuột vẫn bị bảng vô hình nuốt.
        public void Hide()
        {
            lock (_lk)
            {
                _pan = _head = _toggle = RectangleF.Empty;
                foreach (var s in _sec) { s.TitleBox = s.View = s.Track = s.Thumb = RectangleF.Empty; }
                _hovSec = _hovRow = -1; _drag = false; _thSec = -1;
            }
        }

        private static string Fit(Graphics gr, Font f, string t, float maxW)
        {
            if (string.IsNullOrEmpty(t) || maxW <= 8) return t;
            if (gr.MeasureString(t, f).Width <= maxW) return t;
            int lo = 0, hi = t.Length;
            while (lo < hi)
            {
                int mid = (lo + hi + 1) / 2;
                if (gr.MeasureString(t.Substring(0, mid) + "…", f).Width <= maxW) lo = mid; else hi = mid - 1;
            }
            return t.Substring(0, Math.Max(0, lo)) + "…";
        }

        public void Draw(Graphics gr, Font f, Font fb, IReadOnlyList<(string text, Color col)> header,
                         int bgAlpha, int corner, Rectangle clip, float width)
        {
            lock (_lk)
            {
                float pad = 6f, lineH = f.Height + 2f, rowH = 2f * lineH + 3f, titleH = lineH + 6f;
                float bw = Math.Max(300f, Math.Min(width, clip.Width - 16f));
                int nHead = header == null ? 0 : (_collapsed ? Math.Min(1, header.Count) : header.Count);
                float headH = pad + nHead * lineH;
                float bh = headH;
                foreach (var s in _sec) { s.RowH = rowH; s.VisEff = Math.Max(1, Math.Min(s.Vis, s.Rows.Count == 0 ? 1 : s.Rows.Count)); }
                if (!_collapsed)
                {
                    // Bóp số dòng lại nếu bảng cao hơn khung chart — thà cuộn nhiều hơn là tràn ra ngoài.
                    for (int guard = 0; guard < 60; guard++)
                    {
                        float h = headH + pad;
                        foreach (var s in _sec) h += titleH + (s.Collapsed ? 0 : s.VisEff * rowH + 4f);
                        if (h <= clip.Height - 16 || _sec.All(z => z.Collapsed || z.VisEff <= 2)) { bh = h; break; }
                        var big = _sec.Where(z => !z.Collapsed && z.VisEff > 2).OrderByDescending(z => z.VisEff).First();
                        big.VisEff--;
                        bh = h;
                    }
                    float fin = headH + pad;
                    foreach (var s in _sec) fin += titleH + (s.Collapsed ? 0 : s.VisEff * rowH + 4f);
                    bh = fin;
                }
                else bh = headH + pad;

                float defX = (corner == 1 || corner == 3) ? clip.Right - bw - 8f : clip.Left + 8f;
                float defY = (corner >= 2) ? clip.Bottom - bh - 8f : clip.Top + 8f;
                float x = _px ?? defX, y = _py ?? defY;
                x = Math.Max(clip.Left, Math.Min(x, clip.Right - bw));
                y = Math.Max(clip.Top, Math.Min(y, clip.Bottom - Math.Min(bh, clip.Height)));
                _pan = new RectangleF(x, y, bw, bh);
                _head = new RectangleF(x, y, bw, headH);

                using (var bg = new SolidBrush(Color.FromArgb(bgAlpha, 18, 18, 22))) gr.FillRectangle(bg, _pan);
                using (var bd = new Pen(Color.FromArgb(110, 255, 255, 255))) gr.DrawRectangle(bd, x, y, bw, bh);

                float ty = y + pad;
                for (int k = 0; k < nHead; k++)
                {
                    using var br = new SolidBrush(header[k].col);
                    gr.DrawString(Fit(gr, f, header[k].text, bw - 2 * pad - Toggle - 4), f, br, x + pad, ty);
                    ty += lineH;
                }
                _toggle = new RectangleF(x + bw - Toggle - 3f, y + 3f, Toggle, Toggle);
                DrawToggle(gr, _toggle, _collapsed);
                // Thu gọn → XOÁ hình học các mục, nếu không chuột vẫn bấm trúng dòng vô hình của khung trước.
                if (_collapsed)
                {
                    foreach (var s0 in _sec) { s0.TitleBox = RectangleF.Empty; s0.View = RectangleF.Empty; s0.Track = RectangleF.Empty; s0.Thumb = RectangleF.Empty; }
                    return;
                }

                for (int si = 0; si < _sec.Length; si++)
                {
                    var s = _sec[si];
                    s.TitleBox = new RectangleF(x + 1, ty, bw - 2, titleH);
                    using (var tb = new SolidBrush(Color.FromArgb(46, 255, 255, 255))) gr.FillRectangle(tb, s.TitleBox);
                    using (var ln = new Pen(Color.FromArgb(70, 255, 255, 255))) gr.DrawLine(ln, x + 1, ty, x + bw - 1, ty);
                    string t = (s.Collapsed ? "▸ " : "▾ ") + s.Title + $"  ({s.Rows.Count})" +
                               (s.Rows.Count > s.VisEff ? $"   cuộn {s.Scroll + 1}-{Math.Min(s.Rows.Count, s.Scroll + s.VisEff)}" : "");
                    using (var br = new SolidBrush(Color.FromArgb(235, 235, 245)))
                        gr.DrawString(Fit(gr, fb, t, bw * 0.62f), fb, br, x + 6, ty + 2);
                    if (!string.IsNullOrEmpty(s.Hint))
                        using (var br2 = new SolidBrush(Color.FromArgb(140, 150, 165)))
                            gr.DrawString(Fit(gr, f, s.Hint, bw * 0.36f - 10), f, br2, x + bw * 0.64f, ty + 2);
                    ty += titleH;
                    if (s.Collapsed) { s.View = RectangleF.Empty; s.Track = RectangleF.Empty; s.Thumb = RectangleF.Empty; continue; }

                    int vis = s.VisEff;
                    s.Scroll = Math.Max(0, Math.Min(s.Scroll, s.MaxScroll));
                    s.View = new RectangleF(x + 2, ty, bw - 4, vis * rowH);
                    bool bar = s.Rows.Count > vis;
                    float listW = s.View.Width - (bar ? 11f : 4f);

                    gr.SetClip(s.View);
                    if (s.Rows.Count == 0)
                        using (var br = new SolidBrush(Color.Gray))
                            gr.DrawString(s.Empty, f, br, s.View.X + 8, s.View.Y + 4);
                    for (int k = 0; k < vis; k++)
                    {
                        int ri = s.Scroll + k; if (ri >= s.Rows.Count) break;
                        var r = s.Rows[ri];
                        var rr = new RectangleF(s.View.X, ty + k * rowH, listW, rowH);
                        bool hov = _hovSec == si && _hovRow == ri;
                        bool sel = !string.IsNullOrEmpty(s.SelKey) && s.SelKey == r.Key;
                        if (sel)
                        {
                            using (var b = new SolidBrush(Color.FromArgb(70, r.C1))) gr.FillRectangle(b, rr);
                            using (var b = new SolidBrush(r.C1)) gr.FillRectangle(b, rr.X, rr.Y, 3f, rr.Height);
                        }
                        else if (hov)
                            using (var b = new SolidBrush(Color.FromArgb(52, 255, 255, 255))) gr.FillRectangle(b, rr);
                        if (hov && !sel)
                            using (var b = new SolidBrush(Color.FromArgb(150, r.C1))) gr.FillRectangle(b, rr.X, rr.Y, 3f, rr.Height);
                        using (var b1 = new SolidBrush(r.C1))
                            gr.DrawString(Fit(gr, f, r.L1, rr.Width - 14), f, b1, rr.X + 8, rr.Y + 2);
                        if (r.L2 != null)
                            using (var b2 = new SolidBrush(hov || sel ? Color.FromArgb(220, 220, 220) : r.C2))
                                gr.DrawString(Fit(gr, f, r.L2, rr.Width - 14), f, b2, rr.X + 8, rr.Y + 2 + lineH);
                        using (var ln = new Pen(Color.FromArgb(28, 255, 255, 255)))
                            gr.DrawLine(ln, rr.X + 4, rr.Bottom - 1, rr.Right - 4, rr.Bottom - 1);
                    }
                    gr.SetClip(clip);

                    if (bar)
                    {
                        s.Track = new RectangleF(s.View.Right - 9f, s.View.Y + 1, 7f, s.View.Height - 2);
                        float th = Math.Max(20f, s.Track.Height * vis / s.Rows.Count);
                        float pos = s.MaxScroll > 0 ? (float)s.Scroll / s.MaxScroll : 0f;
                        s.Thumb = new RectangleF(s.Track.X, s.Track.Y + (s.Track.Height - th) * pos, s.Track.Width, th);
                        using (var b = new SolidBrush(Color.FromArgb(40, 255, 255, 255))) gr.FillRectangle(b, s.Track);
                        using (var b = new SolidBrush(Color.FromArgb(_thSec == si ? 220 : 150, 200, 210, 230))) gr.FillRectangle(b, s.Thumb);
                    }
                    else { s.Track = RectangleF.Empty; s.Thumb = RectangleF.Empty; }
                    ty += vis * rowH + 4f;
                }
            }
        }

        private static void DrawToggle(Graphics gr, RectangleF r, bool collapsed)
        {
            using (var b = new SolidBrush(Color.FromArgb(55, 255, 255, 255))) gr.FillRectangle(b, r);
            using (var bd = new Pen(Color.FromArgb(120, 255, 255, 255), 1f)) gr.DrawRectangle(bd, r.X, r.Y, r.Width, r.Height);
            float cx = r.X + r.Width / 2f, cy = r.Y + r.Height / 2f;
            using var pen = new Pen(Color.FromArgb(220, 255, 255, 255), 1.6f);
            if (collapsed) gr.DrawLines(pen, new[] { new PointF(cx - 2.5f, cy - 4f), new PointF(cx + 3f, cy), new PointF(cx - 2.5f, cy + 4f) });
            else gr.DrawLines(pen, new[] { new PointF(cx - 4f, cy - 2.5f), new PointF(cx, cy + 3f), new PointF(cx + 4f, cy - 2.5f) });
        }

        private int RowAt(UiSection s, float mx, float my)
        {
            if (s.View.Width <= 0 || !s.View.Contains(mx, my)) return -1;
            int k = (int)((my - s.View.Y) / Math.Max(1f, s.RowH));
            int ri = s.Scroll + k;
            return (ri >= 0 && ri < s.Rows.Count) ? ri : -1;
        }

        private void OnDown(object sender, ChartMouseNativeEventArgs e)
        {
            if (e.Button != NativeMouseButtons.Left) return;
            Action after = null; bool redraw = false;
            lock (_lk)
            {
                if (CloseBox.Width > 0 && CloseBox.Contains(e.X, e.Y))
                { var cb = OnClose; after = () => cb?.Invoke(); redraw = true; goto done; }
                if (!_pan.Contains(e.X, e.Y)) return;
                if (_toggle.Contains(e.X, e.Y)) { _collapsed = !_collapsed; redraw = true; goto done; }
                for (int si = 0; si < _sec.Length; si++)
                {
                    var s = _sec[si];
                    if (s.TitleBox.Width > 0 && s.TitleBox.Contains(e.X, e.Y)) { s.Collapsed = !s.Collapsed; redraw = true; goto done; }
                    if (s.Thumb.Width > 0 && s.Thumb.Contains(e.X, e.Y)) { _thSec = si; _thGrab = e.Y - s.Thumb.Y; redraw = true; goto done; }
                    if (s.Track.Width > 0 && s.Track.Contains(e.X, e.Y))
                    { s.Scroll = Math.Max(0, Math.Min(s.MaxScroll, s.Scroll + (e.Y < s.Thumb.Y ? -s.VisEff : s.VisEff))); redraw = true; goto done; }
                    int ri = RowAt(s, e.X, e.Y);
                    if (ri >= 0)
                    {
                        var row = s.Rows[ri];
                        s.SelKey = row.Key;
                        bool dbl = e.Clicks >= 2;
                        var cb = OnActivate; int sic = si;
                        after = () => cb?.Invoke(sic, row, dbl);
                        redraw = true; goto done;
                    }
                }
                if (_head.Contains(e.X, e.Y) || _pan.Contains(e.X, e.Y))
                { _drag = true; _gx = e.X - _pan.X; _gy = e.Y - _pan.Y; e.Handled = true; e.NeedMouseCapture = true; return; }
                done: ;
            }
            e.Handled = true;
            if (redraw) e.NeedRedraw = true;
            after?.Invoke();
        }

        private void OnMove(object sender, ChartMouseNativeEventArgs e)
        {
            bool redraw = false, handled = false;
            lock (_lk)
            {
                if (_drag)
                {
                    _px = e.X - _gx; _py = e.Y - _gy; redraw = true; handled = true;
                }
                else if (_thSec >= 0)
                {
                    var s = _sec[_thSec];
                    float span = Math.Max(1f, s.Track.Height - s.Thumb.Height);
                    float pos = Math.Max(0f, Math.Min(1f, (e.Y - _thGrab - s.Track.Y) / span));
                    s.Scroll = (int)Math.Round(pos * s.MaxScroll);
                    redraw = true; handled = true;
                }
                else
                {
                    int hs = -1, hr = -1;
                    for (int si = 0; si < _sec.Length && hr < 0; si++) { int ri = RowAt(_sec[si], e.X, e.Y); if (ri >= 0) { hs = si; hr = ri; } }
                    if (hs != _hovSec || hr != _hovRow) { _hovSec = hs; _hovRow = hr; redraw = true; }
                    handled = _pan.Contains(e.X, e.Y);
                }
            }
            if (handled) e.Handled = true;
            if (redraw) e.NeedRedraw = true;
        }

        private void OnUp(object sender, ChartMouseNativeEventArgs e)
        {
            lock (_lk) { if (!_drag && _thSec < 0) return; _drag = false; _thSec = -1; }
            e.Handled = true; e.NeedRedraw = true;
        }

        private void OnWheel(object sender, ChartMouseNativeEventArgs e)
        {
            bool hit = false;
            lock (_lk)
            {
                foreach (var s in _sec)
                {
                    if (s.View.Width <= 0 || !s.View.Contains(e.X, e.Y)) continue;
                    s.Scroll = Math.Max(0, Math.Min(s.MaxScroll, s.Scroll - Math.Sign(e.Delta) * 3));
                    hit = true; break;
                }
            }
            if (hit) { e.Handled = true; e.NeedRedraw = true; }
        }
    }

    // ================================================================================================
    //  ĐIỀU HƯỚNG CHART (nhảy tới 1 mốc thời gian)
    //  Quantower KHÔNG công bố API cuộn chart: IChart chỉ cho ĐỌC RightOffset/BarsWidth. Nên ở đây
    //  dò bằng reflection trên đối tượng chart THẬT (lớp cài đặt nằm trong assembly giao diện) xem có
    //  thành viên int ghi được tên RightOffset/BarsWidth không. KHÔNG gọi bừa phương thức lạ.
    //  Không dò được → nơi gọi báo "KHÔNG hỗ trợ" và mở KÍNH LÚP thay thế.
    // ================================================================================================
    internal static class ChartNav
    {
        private static readonly object _lk = new object();
        private static Type _t;
        private static MemberInfo _off, _bw;
        private static string _status = "nhảy chart: chưa dò";
        public static string Status { get { lock (_lk) return _status; } }
        public static bool CanScroll { get { lock (_lk) return _off != null; } }
        public static bool CanZoom { get { lock (_lk) return _bw != null; } }

        private const BindingFlags BF = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.FlattenHierarchy;

        private static MemberInfo Find(Type t, string[] names)
        {
            foreach (var n in names)
            {
                try { var p = t.GetProperty(n, BF); if (p != null && p.CanRead && p.CanWrite && p.PropertyType == typeof(int)) return p; } catch { }
            }
            foreach (var n in names)
            {
                try { var fi = t.GetField(n, BF); if (fi != null && fi.FieldType == typeof(int)) return fi; } catch { }
            }
            return null;
        }
        private static int GetI(object o, MemberInfo m) => m is PropertyInfo p ? (int)p.GetValue(o) : (int)((FieldInfo)m).GetValue(o);
        private static void SetI(object o, MemberInfo m, int v) { if (m is PropertyInfo p) p.SetValue(o, v); else ((FieldInfo)m).SetValue(o, v); }

        public static void Discover(IChart chart, Action<string> dump)
        {
            if (chart == null) return;
            lock (_lk)
            {
                var t = chart.GetType();
                if (_t == t) return;
                _t = t;
                _off = Find(t, new[] { "RightOffset", "rightOffset", "_rightOffset" });
                _bw = Find(t, new[] { "BarsWidth", "barsWidth", "_barsWidth" });
                _status = "nhảy chart: " + (_off != null ? "OK (" + _off.Name + ")" : "KHÔNG hỗ trợ → dùng kính lúp");
                try { dump?.Invoke(DumpMembers(t)); } catch { }
            }
        }

        public static int Offset(IChart c) { lock (_lk) { try { return _off == null ? 0 : GetI(c, _off); } catch { return 0; } } }
        public static bool SetOffset(IChart c, int v)
        {
            lock (_lk)
            {
                if (_off == null) return false;
                try { SetI(c, _off, v); return true; }
                catch { _status = "nhảy chart: lỗi ghi " + _off.Name; _off = null; return false; }
            }
        }
        public static bool SetBarsWidth(IChart c, int v)
        {
            lock (_lk)
            {
                if (_bw == null) return false;
                try { SetI(c, _bw, Math.Max(1, Math.Min(64, v))); return true; }
                catch { _bw = null; return false; }
            }
        }

        // Liệt kê thành viên khả nghi (chỉ ĐỌC tên, không gọi) để còn cải tiến nếu bản này chưa nhảy được.
        private static string DumpMembers(Type t)
        {
            var sb = new StringBuilder();
            sb.Append("Chart type: ").Append(t.FullName).Append('\n');
            string[] keys = { "offset", "scroll", "zoom", "barswidth", "visible", "first", "last", "navigate", "goto", "moveto" };
            try
            {
                foreach (var m in t.GetMembers(BF))
                {
                    string n = m.Name.ToLowerInvariant();
                    if (!keys.Any(k => n.Contains(k))) continue;
                    sb.Append("  ").Append(m.MemberType).Append(' ').Append(m).Append('\n');
                }
            }
            catch { }
            return sb.ToString();
        }
    }

    // ================================================================================================
    //  VÒNG LẶP KÍN CANH VỊ TRÍ CHART
    //  Không chắc đơn vị của RightOffset (nến hay px) → mỗi khung hình đo lại x của mốc đích, tự ước
    //  lượng "bao nhiêu px cho 1 đơn vị offset" từ chính bước trước rồi hiệu chỉnh; dừng khi sai số
    //  ≤8px hoặc quá 10 bước. Có cờ chống đệ quy vì RedrawBuffer có thể vẽ ngay trong lời gọi.
    // ================================================================================================
    internal sealed class UiNav
    {
        private DateTime _time = DateTime.MinValue;
        private int _iters, _lastOff; private float _lastX = float.NaN;
        private bool _busy;

        public void Cancel() => _time = DateTime.MinValue;

        // Đặt yêu cầu nhảy tới mốc thời gian (thường là nến giữa đối tượng được bấm).
        public void Request(IChart chart, DateTime target)
        {
            _time = target; _iters = 0; _lastX = float.NaN; _lastOff = ChartNav.Offset(chart);
        }

        public void Step(IChart chart, IChartWindowCoordinatesConverter conv, Rectangle clip, Action<Exception> onErr = null)
        {
            if (_time == DateTime.MinValue || _busy) return;
            _busy = true;
            try
            {
                if (chart == null || _iters++ > 10) { _time = DateTime.MinValue; return; }
                float cur = (float)conv.GetChartX(_time);
                float want = clip.Left + clip.Width * 0.5f;
                float err = cur - want;
                if (Math.Abs(err) <= 8f) { _time = DateTime.MinValue; return; }
                int off = ChartNav.Offset(chart);
                float k = Math.Max(1, chart.BarsWidth);              // ước lượng mặc định: 1 đơn vị = 1 nến
                if (!float.IsNaN(_lastX) && off != _lastOff)
                {
                    float measured = Math.Abs((cur - _lastX) / (off - _lastOff));
                    if (measured > 0.05f && measured < 500f) k = measured;
                }
                int step = (int)Math.Round(err / k);
                if (step == 0) step = err > 0 ? 1 : -1;
                _lastX = cur; _lastOff = off;
                if (!ChartNav.SetOffset(chart, Math.Max(0, off + step))) { _time = DateTime.MinValue; return; }
                chart.RedrawBuffer();
            }
            catch (Exception ex) { _time = DateTime.MinValue; onErr?.Invoke(ex); }
            finally { _busy = false; }
        }
    }

    // ================================================================================================
    //  KÍNH LÚP — hộp vẽ lại một đoạn nến ngay trên chart (không cần cuộn chart).
    //  Lý do tồn tại: Quantower không công bố API cuộn chart; nếu ChartNav không dò được thành viên
    //  ghi được thì đây là cách DUY NHẤT chắc chắn xem lại quá khứ mà không phải kéo tay.
    //  Lớp này CHỈ lo khung + nến + lưới giá + trục thời gian, rồi trả 2 hàm ánh xạ toạ độ để nơi gọi
    //  vẽ chồng phần riêng của mình (đường E/SL/TP, sơ đồ Wyckoff…).
    // ================================================================================================
    internal sealed class UiMiniChart
    {
        private int _from = -1, _to = -1; private string _key;
        private double[] _o, _h, _l, _c; private DateTime[] _t;

        public RectangleF Box, Plot, CloseBox;
        public int From => _from;
        public int Count => _h?.Length ?? 0;

        // Nạp (và nhớ) đoạn nến [from..to] của HistoricalData. Trả false nếu không đủ dữ liệu.
        public bool Load(HistoricalData hd, string key, int from, int to)
        {
            if (hd == null || to - from < 2) return false;
            if (_key == key && _from == from && _to == to) return true;
            int n = to - from + 1;
            var o = new double[n]; var h = new double[n]; var l = new double[n]; var c = new double[n]; var t = new DateTime[n];
            for (int i = 0; i < n; i++)
            {
                if (hd[from + i, SeekOriginHistory.Begin] is not HistoryItemBar b) { h[i] = double.NaN; continue; }
                o[i] = b.Open; h[i] = b.High; l[i] = b.Low; c[i] = b.Close; t[i] = b.TimeLeft;
            }
            _o = o; _h = h; _l = l; _c = c; _t = t; _key = key; _from = from; _to = to;
            return true;
        }

        public void PriceRange(ref double lo, ref double hi)
        {
            for (int i = 0; i < Count; i++) { if (double.IsNaN(_h[i])) continue; if (_h[i] > hi) hi = _h[i]; if (_l[i] < lo) lo = _l[i]; }
        }

        // Vẽ khung + nến; đặt Box/Plot/CloseBox và trả 2 hàm ánh xạ. Nơi gọi vẽ tiếp rồi tự SetClip lại.
        public bool Draw(Graphics gr, Rectangle clip, double lo, double hi, string title, Color accent,
                         Font fTitle, Font fSmall, int tzOffset, Func<double, string> fmt,
                         out Func<int, float> X, out Func<double, float> Y)
        {
            X = null; Y = null;
            int cnt = Count;
            if (cnt < 2 || hi <= lo) return false;
            double padP = (hi - lo) * 0.06; lo -= padP; hi += padP;

            Box = new RectangleF(clip.Left + 28, clip.Top + 26, Math.Max(460, clip.Width - 56), Math.Max(260, clip.Height - 96));
            if (Box.Bottom > clip.Bottom - 12) Box.Height = Math.Max(200, clip.Bottom - 12 - Box.Y);
            if (Box.Right > clip.Right - 12) Box.Width = Math.Max(400, clip.Right - 12 - Box.X);
            Plot = new RectangleF(Box.X + 10, Box.Y + 30, Box.Width - 82, Box.Height - 54);

            using (var bg = new SolidBrush(Color.FromArgb(246, 14, 14, 17))) gr.FillRectangle(bg, Box);
            using (var bd = new Pen(accent, 2f)) gr.DrawRectangle(bd, Box.X, Box.Y, Box.Width, Box.Height);
            using (var hb = new SolidBrush(Color.FromArgb(60, accent))) gr.FillRectangle(hb, Box.X + 1, Box.Y + 1, Box.Width - 2, 26);
            using (var tb = new SolidBrush(Color.White)) gr.DrawString(title, fTitle, tb, Box.X + 8, Box.Y + 4);

            CloseBox = new RectangleF(Box.Right - 24, Box.Y + 4, 18, 18);
            using (var b = new SolidBrush(Color.FromArgb(70, 255, 255, 255))) gr.FillRectangle(b, CloseBox);
            using (var p = new Pen(Color.White, 1.6f))
            {
                gr.DrawLine(p, CloseBox.X + 5, CloseBox.Y + 5, CloseBox.Right - 5, CloseBox.Bottom - 5);
                gr.DrawLine(p, CloseBox.Right - 5, CloseBox.Y + 5, CloseBox.X + 5, CloseBox.Bottom - 5);
            }

            var plot = Plot; int from = _from;
            float XI(int hdIdx) => plot.X + (hdIdx - from + 0.5f) * plot.Width / cnt;
            float YI(double p) => plot.Bottom - (float)((p - lo) / (hi - lo)) * plot.Height;
            X = XI; Y = YI;

            gr.SetClip(new RectangleF(Box.X + 1, Box.Y + 27, Box.Width - 2, Box.Height - 28));
            using (var gp = new Pen(Color.FromArgb(38, 255, 255, 255)))
            using (var gb = new SolidBrush(Color.FromArgb(170, 180, 190)))
                for (int k = 0; k <= 4; k++)
                {
                    double pr = lo + (hi - lo) * k / 4.0; float yy = YI(pr);
                    gr.DrawLine(gp, plot.X, yy, plot.Right, yy);
                    gr.DrawString(fmt(pr), fSmall, gb, plot.Right + 4, yy - 7);
                }
            // nến (gộp theo cột khi quá dày để không vẽ chồng thành mảng đặc)
            float bw = plot.Width / cnt;
            int stepBars = bw >= 1.2f ? 1 : (int)Math.Ceiling(1.2f / Math.Max(0.01f, bw));
            using (var pUp = new Pen(Color.FromArgb(200, 90, 200, 130), 1f))
            using (var pDn = new Pen(Color.FromArgb(200, 220, 100, 100), 1f))
            using (var bUp = new SolidBrush(Color.FromArgb(190, 90, 200, 130)))
            using (var bDn = new SolidBrush(Color.FromArgb(190, 220, 100, 100)))
                for (int i = 0; i < cnt; i += stepBars)
                {
                    int j2 = Math.Min(cnt - 1, i + stepBars - 1);
                    double oo = _o[i], cc2 = _c[j2], hh = double.MinValue, ll = double.MaxValue;
                    for (int k = i; k <= j2; k++) { if (double.IsNaN(_h[k])) continue; if (_h[k] > hh) hh = _h[k]; if (_l[k] < ll) ll = _l[k]; }
                    if (hh == double.MinValue) continue;
                    float xx = plot.X + (i + stepBars * 0.5f) * bw;
                    bool up = cc2 >= oo;
                    gr.DrawLine(up ? pUp : pDn, xx, YI(hh), xx, YI(ll));
                    float bodyW = Math.Max(1f, bw * stepBars * 0.7f);
                    float yA = YI(Math.Max(oo, cc2)), yB = YI(Math.Min(oo, cc2));
                    gr.FillRectangle(up ? bUp : bDn, xx - bodyW / 2, yA, bodyW, Math.Max(1f, yB - yA));
                }
            return true;
        }

        // Trục thời gian + dòng hướng dẫn (gọi SAU khi nơi gọi đã vẽ xong lớp riêng và trả clip về chart).
        public void DrawTimeAxis(Graphics gr, Font fSmall, int tzOffset, string hint)
        {
            int cnt = Count; if (cnt < 2) return;
            using var tb = new SolidBrush(Color.FromArgb(160, 170, 185));
            gr.DrawString(_t[0].AddHours(tzOffset).ToString("dd/MM HH:mm"), fSmall, tb, Plot.X, Box.Bottom - 18);
            gr.DrawString(_t[cnt - 1].AddHours(tzOffset).ToString("dd/MM HH:mm"), fSmall, tb, Plot.Right - 78, Box.Bottom - 18);
            if (!string.IsNullOrEmpty(hint)) gr.DrawString(hint, fSmall, tb, Plot.X + Plot.Width * 0.36f, Box.Bottom - 18);
        }
    }
}
