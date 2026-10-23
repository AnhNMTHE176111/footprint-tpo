// ============================================================================
//  VungCanhLenh — indicator "Vùng Canh Lệnh" cho Quantower / Optimus Flow (lớp dán SDK)
// ============================================================================
//  Add vào chart M1 (nên bật Volume Analysis). Chỉ xử lý nến ĐÃ ĐÓNG (tới Count−2), đúng 1 lần/nến, theo thứ tự.
//  Chưa có Volume Analysis vẫn vẽ (swing + số tròn) và ghi chú; khi footprint sẵn sàng thì dựng lại từ đầu (VclFeeder).
//  Toàn bộ logic ở VclCore.cs (test được trên Linux, khớp research/vcl5.py + lan_cham.py). File này chỉ: Settings,
//  đọc nến + footprint từng mức giá, vẽ vùng + nhãn.
//  Build: build.sh (concat VclCore.cs + file này). MỌI `using` nằm trong namespace.
// ============================================================================
namespace VungCanhLenhNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;

    public class VungCanhLenh : Indicator, IVolumeAnalysisIndicator
    {
        // ======= Settings (QĐ-1: không có ngưỡng số) =======
        [InputParameter("Lệch giờ (UTC → VN)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Hiện nhãn cạnh vùng", 21)]
        public bool ShowLabels { get; set; } = true;
        [InputParameter("Hiện lịch sử riêng của vùng", 23)]
        public bool ShowHistory { get; set; } = true;
        [InputParameter("Hiện vùng xa", 22)]
        public bool ShowFar { get; set; } = true;
        [InputParameter("Hiện TẤT CẢ vùng trong lịch sử (để xem lại signal)", 24)]
        public bool ShowAllHistory { get; set; } = false;
        [InputParameter("Màu kháng cự", 30)]
        public Color ResColor { get; set; } = Color.FromArgb(220, 70, 60);
        [InputParameter("Màu hỗ trợ", 31)]
        public Color SupColor { get; set; } = Color.FromArgb(40, 170, 100);
        [InputParameter("Màu đang kiểm tra", 32)]
        public Color TestColor { get; set; } = Color.FromArgb(230, 150, 30);

        // ======= trạng thái =======
        private sealed class RenderState
        {
            public List<VZone> Zones = new();
            public List<VLichSu> LichSu = new(); // vùng lịch sử (chỉ khi bật "tất cả vùng"), cũ → mới
            public List<VZone> BiChan = new();   // vùng Display không có vùng lịch sử sống đại diện (vẽ viền đứt)
            public DateTime LastTime;            // giờ mở nến đã đóng mới nhất
            public double Close, U;
            public int Phase;
            public string Warn;      // lỗi (hiện 1 dòng nhỏ góc dưới-phải)
            public string Note;      // cảnh báo nhẹ (dòng nhỏ góc dưới-phải), vd thiếu Volume Analysis
        }

        private readonly object _calc = new();
        private readonly object _sync = new();
        private RenderState _render;
        private VclFeeder _feeder = new VclFeeder();
        private int _lastN = -1;
        private bool _lastVa;
        private const string NoVaNote = "Chưa có Volume Analysis: thiếu VA/POC hôm qua, VA Âu, POC trần (chỉ còn swing + số tròn)";
        private static readonly CultureInfo Vi = CultureInfo.GetCultureInfo("vi-VN");
        // tiêu điểm theo chuột (chế độ lịch sử): giờ nến dưới con trỏ; null ⇒ nến ở mép phải màn hình. Đọc/ghi dưới _sync.
        private DateTime? _focus;
        private IChart _mouseChart;

        public VungCanhLenh() : base()
        {
            Name = "Vùng Canh Lệnh";
            Description = "Vùng hỗ trợ/kháng cự ổn định, rộng 2–5 giá (swing M5/M15, mốc phiên, số tròn). Nhãn: biên vùng, điểm, % lần chạm " +
                          "đảo chiều / xuyên phá (tần suất lịch sử chung theo pha và độ rộng, KHÔNG phải độ mạnh của vùng), lịch sử chạm của riêng vùng. " +
                          "Cần Volume Analysis. Add vào chart M1.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded()
        {
            _vaLoaded = true;                        // footprint đã tính xong ⇒ lần Process này VclFeeder dựng lại lõi CÓ footprint
            SafeProcess("VolumeAnalysisData_Loaded");
        }
        private volatile bool _vaLoaded;

        protected override void OnClear()
        {
            DetachMouse();
            lock (_calc) { _feeder = new VclFeeder(); _lastN = -1; _lastVa = false; _vaLoaded = false; lock (_sync) { _render = null; _focus = null; } }
        }

        public override void Dispose()
        {
            DetachMouse();
            base.Dispose();
        }

        // ---------------------------------------------------------------- chuột (chỉ khi bật chế độ lịch sử)
        /// <summary>Gắn sự kiện chuột khi bật "tất cả vùng", gỡ khi tắt. Gọi từ OnPaintChart (luồng UI).</summary>
        private void SyncMouse()
        {
            var ch = ShowAllHistory ? CurrentChart : null;
            if (ReferenceEquals(ch, _mouseChart)) return;
            DetachMouse();
            if (ch == null) return;
            ch.MouseMove += OnMouseMove;
            ch.MouseLeave += OnMouseLeave;
            _mouseChart = ch;
        }

        private void DetachMouse()
        {
            var ch = _mouseChart;
            _mouseChart = null;
            if (ch != null) try { ch.MouseMove -= OnMouseMove; ch.MouseLeave -= OnMouseLeave; } catch { }
            lock (_sync) _focus = null;
        }

        private static DateTime FloorMin(DateTime t) => new DateTime(t.Year, t.Month, t.Day, t.Hour, t.Minute, 0, t.Kind);

        /// <summary>Không đặt Handled (không nuốt chuột của chart); chỉ NeedRedraw khi nến tiêu điểm đổi.</summary>
        private void OnMouseMove(object sender, ChartMouseNativeEventArgs e)
        {
            try
            {
                var w = e.Window;
                if (w == null) return;
                var clip = w.ClientRectangle;
                DateTime? f = null;
                if (e.X >= clip.Left && e.X <= clip.Right) f = FloorMin(w.CoordinatesConverter.GetTime(e.X));
                bool changed;
                lock (_sync) { changed = _focus != f; _focus = f; }
                if (changed) e.NeedRedraw = true;
            }
            catch (Exception ex) { LogErr(ex, "OnMouseMove"); }
        }

        private void OnMouseLeave(object sender, ChartMouseNativeEventArgs e)
        {
            bool changed;
            lock (_sync) { changed = _focus != null; _focus = null; }
            if (changed) e.NeedRedraw = true;
        }

        /// <summary>KHÔNG chờ Volume Analysis: chưa có footprint vẫn vẽ (chỉ swing + số tròn) và ghi chú một dòng nhỏ;
        /// khi footprint sẵn sàng thì VclFeeder dựng lại lõi từ đầu để có đủ mốc phiên (C).</summary>
        protected override void OnUpdate(UpdateArgs args) => SafeProcess("OnUpdate");

        private bool VaReady()
        {
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            return _vaLoaded || (p != null && p.State == VolumeAnalysisCalculationState.Finished);
        }

        private void SafeProcess(string where)
        {
            try { Process(); }
            catch (Exception ex)
            {
                LogErr(ex, where);
                lock (_sync) _render ??= new RenderState { Warn = "LỖI: " + ex.Message };
            }
        }

        private void LogErr(Exception ex, string where)
        {
            try
            {
                string d = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "VungCanhLenh");
                Directory.CreateDirectory(d);
                File.AppendAllText(Path.Combine(d, "error_log.txt"), $"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}Z [{Name}] {where}: {ex}\n");
            }
            catch { }
        }

        // ---------------------------------------------------------------- xử lý nến đã đóng
        private void Process()
        {
            lock (_calc)
            {
                var hd = HistoricalData;
                if (hd == null) return;
                int n = hd.Count;
                bool va = VaReady();
                if (n < 3 || (n == _lastN && va == _lastVa)) return;
                // nến cuối đang chạy ⇒ số nến ĐÃ ĐÓNG = Count − 1 (chỉ số 0..Count−2)
                _feeder.Sync(n - 1,
                    i => hd[i, SeekOriginHistory.Begin] is HistoryItemBar b
                        ? new VBar { Time = b.TimeLeft, O = b.Open, H = b.High, L = b.Low, C = b.Close, Vol = b.Volume } : null,
                    i => hd[i, SeekOriginHistory.Begin] is HistoryItemBar b ? ReadLevels(b) : Array.Empty<VLevel>(),
                    va, TzOffset);
                var core = _feeder.Core;
                var rs = new RenderState { Close = core.Close, U = core.U, Phase = core.Phase, Note = _feeder.BuiltWithLevels ? null : NoVaNote,
                                           LastTime = core.Bars.Count > 0 ? core.Bars[core.Bars.Count - 1].Time : DateTime.MinValue };
                foreach (var z in core.Display) rs.Zones.Add(z.Clone());
                if (ShowAllHistory)
                {
                    rs.LichSu = new List<VLichSu>(core.LichSu.Count);
                    foreach (var h in core.LichSu) rs.LichSu.Add(h.Clone());
                    foreach (var z in rs.Zones) if (core.Ls.BiChan.Contains(z.Id)) rs.BiChan.Add(z);
                }
                lock (_sync) _render = rs;
                _lastN = n; _lastVa = va;
            }
            CurrentChart?.RedrawBuffer();
        }

        /// <summary>Footprint từng mức giá (dictionary do platform giữ ⇒ thử lại nếu bị sửa giữa chừng).</summary>
        private static IReadOnlyList<VLevel> ReadLevels(HistoryItemBar b)
        {
            for (int attempt = 0; attempt < 3; attempt++)
            {
                try
                {
                    var pl = b.VolumeAnalysisData?.PriceLevels;
                    if (pl == null) return Array.Empty<VLevel>();
                    var list = new List<VLevel>(pl.Count);
                    foreach (var kv in pl) list.Add(new VLevel(kv.Key, kv.Value.Volume));
                    return list;
                }
                catch (InvalidOperationException) { }
            }
            return Array.Empty<VLevel>();
        }

        // ---------------------------------------------------------------- văn bản
        private static string F(double v, string fmt = "0.0") => v.ToString(fmt, Vi);

        /// <summary>Nhãn theo thứ tự ưu tiên khi chật: độ rộng vùng &gt; % đảo/xuyên &gt; điểm &gt; lịch sử riêng.
        /// mức 0 = đủ; 1 = lịch sử rút gọn; 2 = bỏ lịch sử; 3 = bỏ cả điểm.</summary>
        private string Label(VZone z, RenderState rs, int level)
        {
            var parts = new List<string> { F(z.Hi - z.Lo) + " giá" };
            if (level < 3) parts.Add(F(z.Score, "0") + " điểm");
            if (VclTables.Lookup(rs.Phase, z.WBin, out int dao, out int xuyen, out int chuaRo))
            {
                parts.Add("đảo chiều ≈" + dao + "%");
                parts.Add("xuyên phá ≈" + xuyen + "%");
                if (chuaRo >= 10) parts.Add("chưa rõ ≈" + chuaRo + "%");
            }
            else parts.Add("đảo/xuyên: —");
            if (ShowHistory && level < 2)
            {
                if (z.EpOpen) parts.Add(level == 0 ? "đang chạm (lần " + z.EpK + ")" : "đang chạm");
                else if (z.N == 0) parts.Add("chưa chạm");
                else parts.Add(level == 0 ? "đã chạm " + z.N + " lần (đảo " + z.Dao + " · xuyên " + z.Xuyen + ")"
                                          : z.N + " lần (" + z.Dao + " đảo)");
            }
            return string.Join(" · ", parts) + (z.Slot == 'F' ? " (xa)" : "");
        }

        // ---------------------------------------------------------------- vẽ
        /// <summary>Nhãn live (cùng nội dung chế độ gọn) ở mép phải, rút gọn khi chật.</summary>
        private void DrawLiveLabel(Graphics gr, VZone z, RenderState rs, Font fLbl, float x0, float top, float h, Rectangle clip)
        {
            float maxW = Math.Max(40f, (clip.Right - x0) * 0.9f);
            string s = Label(z, rs, 0);
            var sz = gr.MeasureString(s, fLbl);
            for (int lvl = 1; lvl <= 3 && sz.Width > maxW; lvl++) { s = Label(z, rs, lvl); sz = gr.MeasureString(s, fLbl); }
            float lx = clip.Right - sz.Width - 6, ly = top + h / 2 - sz.Height / 2;
            using (var bg = new SolidBrush(Color.FromArgb(150, 14, 16, 22))) gr.FillRectangle(bg, lx - 2, ly, sz.Width + 4, sz.Height);
            using (var br = new SolidBrush(Color.FromArgb(235, Color.White))) gr.DrawString(s, fLbl, br, lx, ly);
        }

        /// <summary>Chế độ "tất cả vùng" (PLAN-LICH-SU 2.5–2.7): mỗi vùng lịch sử một hình chữ nhật từ StartTime tới EndTime (vùng còn sống ⇒ mép phải),
        /// màu theo vai (đỏ kháng cự / xanh hỗ trợ / xám chưa rõ). Vùng sống tại tF (nến dưới chuột, hoặc mép phải) vẽ đậm + nhãn lo–hi; còn lại mờ, không nhãn.
        /// Không vẽ Display từ FirstTime nữa: vùng live = vùng lịch sử còn sống (nhãn live của vùng Display nó đang khớp); vùng Display bị chặn ⇒ viền đứt.</summary>
        private void PaintLichSu(Graphics gr, Func<DateTime, double> chartX, Func<double, double> chartY, Func<double, DateTime> timeAt,
                                 Rectangle clip, RenderState rs, Font fLbl)
        {
            DateTime? mf; lock (_sync) mf = _focus;
            DateTime tF = mf ?? FloorMin(timeAt(clip.Right));
            var zoneOf = new Dictionary<int, VZone>();
            foreach (var z in rs.Zones) zoneOf[z.Id] = z;
            float xF = float.NaN;
            try { xF = (float)chartX(tF); } catch { }
            foreach (var g in rs.LichSu)
            {
                if (!g.TungGan && !ShowFar) continue;
                bool live = g.End < 0;
                float x0, x1;
                try { x0 = (float)chartX(g.StartTime); x1 = live ? clip.Right : (float)chartX(g.EndTime.AddMinutes(1)); } catch { continue; }
                if (x1 < clip.Left || x0 > clip.Right) continue;
                float yHi = (float)chartY(g.Hi), yLo = (float)chartY(g.Lo);
                float top = Math.Min(yHi, yLo), h = Math.Max(1f, Math.Abs(yLo - yHi));
                if (top > clip.Bottom || top + h < clip.Top) continue;
                float cx0 = Math.Max(clip.Left, x0), cx1 = Math.Min(clip.Right, Math.Max(x1, x0 + 2));
                bool focus = g.StartTime <= tF && (live || tF <= g.EndTime);
                Color baseC = g.Vai > 0 ? ResColor : (g.Vai < 0 ? SupColor : Color.FromArgb(140, 140, 140));
                using (var br = new SolidBrush(Color.FromArgb(focus ? 55 : 18, baseC))) gr.FillRectangle(br, cx0, top, cx1 - cx0, h);
                using (var pen = new Pen(Color.FromArgb(focus ? 150 : 60, baseC), 1f))
                {
                    gr.DrawLine(pen, cx0, top, cx1, top);
                    gr.DrawLine(pen, cx0, top + h, cx1, top + h);
                    if (x0 >= clip.Left) gr.DrawLine(pen, x0, top, x0, top + h);
                    if (!live && x1 <= clip.Right) gr.DrawLine(pen, x1, top, x1, top + h);
                }
                double life = ((live ? rs.LastTime : g.EndTime) - g.StartTime).TotalMinutes;
                if (focus && ShowLabels && life >= Vcl.LsLabelMin)
                {
                    string s = F(g.Lo) + "–" + F(g.Hi);
                    var sz = gr.MeasureString(s, fLbl);
                    if (sz.Height <= h + 2)
                        using (var br = new SolidBrush(Color.FromArgb(220, Color.White)))
                        {
                            float ly = top + h / 2 - sz.Height / 2;
                            bool left = x0 >= clip.Left && sz.Width + 4 <= cx1 - cx0;
                            if (left) gr.DrawString(s, fLbl, br, x0 + 2, ly);
                            // khối dài: thêm một nhãn ở x của tF (nếu nhãn mép trái không thấy hoặc ở xa tF)
                            if (!float.IsNaN(xF) && xF + 4 + sz.Width <= cx1 && xF >= cx0 && (!left || xF - x0 > 3 * sz.Width))
                                gr.DrawString(s, fLbl, br, xF + 4, ly);
                        }
                }
                if (live && g.MatchedId >= 0 && zoneOf.TryGetValue(g.MatchedId, out var zl) && (zl.Slot != 'F' || ShowFar))
                    DrawLiveLabel(gr, zl, rs, fLbl, cx0, top, h, clip);
            }
            // vùng Display bị chặn (chồng một phần với vùng lịch sử đang sống): viền đứt, không tô, từ nến hiện tại tới mép phải + nhãn live
            float xNow = clip.Left;
            try { xNow = Math.Max(clip.Left, (float)chartX(rs.LastTime)); } catch { }
            foreach (var z in rs.BiChan)
            {
                if (z.Slot == 'F' && !ShowFar) continue;
                if (xNow > clip.Right) break;
                float yHi = (float)chartY(z.Hi), yLo = (float)chartY(z.Lo);
                float top = Math.Min(yHi, yLo), h = Math.Max(1f, Math.Abs(yLo - yHi));
                if (top > clip.Bottom || top + h < clip.Top) continue;
                Color baseC = z.Slot == 'K' ? TestColor : (z.Side > 0 ? ResColor : SupColor);
                using (var pen = new Pen(Color.FromArgb(150, baseC), 1f) { DashStyle = System.Drawing.Drawing2D.DashStyle.Dash })
                    gr.DrawRectangle(pen, xNow, top, clip.Right - xNow, h);
                DrawLiveLabel(gr, z, rs, fLbl, xNow, top, h, clip);
            }
            // đường dọc mảnh tại nến tiêu điểm
            if (!float.IsNaN(xF) && xF >= clip.Left && xF <= clip.Right)
                using (var pen = new Pen(Color.FromArgb(60, Color.White), 1f)) gr.DrawLine(pen, xF, clip.Top, xF, clip.Bottom);
        }

        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null) return;
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;
            RenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;
            var gr = args.Graphics; var conv = win.CoordinatesConverter; var clip = win.ClientRectangle;
            var prevClip = gr.ClipBounds; gr.SetClip(clip);
            try
            {
                using var fLbl = new Font("Consolas", 8, FontStyle.Regular);
                SyncMouse();
                if (ShowAllHistory && !double.IsNaN(rs.U) && rs.U > 0)
                    PaintLichSu(gr, t => conv.GetChartX(t), p => conv.GetChartY(p), x => conv.GetTime(x), clip, rs, fLbl);
                else if (!double.IsNaN(rs.U) && rs.U > 0)
                {
                    foreach (var z in rs.Zones)
                    {
                        if (z.Slot == 'F' && !ShowFar) continue;
                        Color baseC = z.Slot == 'K' ? TestColor : (z.Side > 0 ? ResColor : SupColor);
                        int a = z.Slot == 'F' ? 28 : (z.Slot == 'K' ? 70 : 55);
                        float x0 = clip.Left;
                        try { x0 = Math.Max(clip.Left, (float)conv.GetChartX(z.FirstTime)); } catch { }
                        float yHi = (float)conv.GetChartY(z.Hi), yLo = (float)conv.GetChartY(z.Lo);
                        float top = Math.Min(yHi, yLo), h = Math.Max(1f, Math.Abs(yLo - yHi));
                        if (top > clip.Bottom || top + h < clip.Top || x0 > clip.Right) continue;
                        using (var br = new SolidBrush(Color.FromArgb(a, baseC))) gr.FillRectangle(br, x0, top, clip.Right - x0, h);
                        using (var pen = new Pen(Color.FromArgb(z.Slot == 'F' ? 90 : 150, baseC), 1f)
                               { DashStyle = z.Slot == 'F' ? System.Drawing.Drawing2D.DashStyle.Dash : System.Drawing.Drawing2D.DashStyle.Solid })
                        {
                            gr.DrawLine(pen, x0, top, clip.Right, top);
                            gr.DrawLine(pen, x0, top + h, clip.Right, top + h);
                        }
                        if (ShowLabels)
                        {
                            float maxW = (clip.Right - x0) * 0.9f;
                            string s = Label(z, rs, 0);
                            var sz = gr.MeasureString(s, fLbl);
                            for (int lvl = 1; lvl <= 3 && sz.Width > maxW; lvl++) { s = Label(z, rs, lvl); sz = gr.MeasureString(s, fLbl); }
                            float lx = clip.Right - sz.Width - 6, ly = top + h / 2 - sz.Height / 2;
                            using (var bg = new SolidBrush(Color.FromArgb(150, 14, 16, 22))) gr.FillRectangle(bg, lx - 2, ly, sz.Width + 4, sz.Height);
                            using (var br = new SolidBrush(Color.FromArgb(235, Color.White))) gr.DrawString(s, fLbl, br, lx, ly);
                        }
                    }
                }
                string msg = !string.IsNullOrEmpty(rs.Warn) ? "⚠ " + rs.Warn
                           : double.IsNaN(rs.U) ? "Vùng Canh Lệnh: chưa đủ 10 nến để tính u"
                           : !string.IsNullOrEmpty(rs.Note) ? "⚠ " + rs.Note : null;
                if (msg != null)
                {
                    using var fNote = new Font("Consolas", 7, FontStyle.Regular);
                    var sz = gr.MeasureString(msg, fNote);
                    float nx = clip.Right - sz.Width - 8, ny = clip.Bottom - sz.Height - 4;   // góc dưới-phải
                    using var br = new SolidBrush(msg.StartsWith("⚠") ? Color.FromArgb(255, 170, 120) : Color.FromArgb(160, 165, 175));
                    gr.DrawString(msg, fNote, br, nx, ny);
                }
            }
            catch (Exception ex) { LogErr(ex, "OnPaintChart"); }
            finally { gr.SetClip(prevClip); }
        }
    }
}
