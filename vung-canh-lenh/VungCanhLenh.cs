// ============================================================================
//  VungCanhLenh — indicator "Vùng Canh Lệnh" cho Quantower / Optimus Flow (lớp dán SDK)
// ============================================================================
//  Add vào chart M1 (nên bật Volume Analysis). Chỉ xử lý nến ĐÃ ĐÓNG (tới Count−2), đúng 1 lần/nến, theo thứ tự.
//  Chưa có Volume Analysis vẫn vẽ (swing + số tròn) và ghi chú; khi footprint sẵn sàng thì dựng lại từ đầu (VclFeeder).
//  Toàn bộ logic ở VclCore.cs (test được trên Linux, khớp research/vcl4.py 100%). File này chỉ: Settings,
//  đọc nến + footprint từng mức giá, vẽ vùng + nhãn + bảng tra.
//  Build: build.sh (concat VclCore.cs + file này). MỌI `using` nằm trong namespace.
// ============================================================================
namespace VungCanhLenhNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Globalization;
    using System.IO;
    using TradingPlatform.BusinessLayer;

    public class VungCanhLenh : Indicator, IVolumeAnalysisIndicator
    {
        // ======= Settings (QĐ-1: không có ngưỡng số) =======
        [InputParameter("Lệch giờ (UTC → VN)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Hiện bảng tra", 20)]
        public bool ShowTable { get; set; } = true;
        [InputParameter("Hiện nhãn cạnh vùng", 21)]
        public bool ShowLabels { get; set; } = true;
        [InputParameter("Hiện vùng xa", 22)]
        public bool ShowFar { get; set; } = true;
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
            public double Close, U;
            public int Phase;
            public string Warn;      // lỗi (hiện thay bảng)
            public string Note;      // cảnh báo nhẹ (dòng trong bảng), vd thiếu Volume Analysis
        }

        private readonly object _calc = new();
        private readonly object _sync = new();
        private RenderState _render;
        private VclFeeder _feeder = new VclFeeder();
        private int _lastN = -1;
        private bool _lastVa;
        private const string NoVaNote = "Chưa có Volume Analysis: thiếu VA/POC hôm qua, VA Âu, POC trần (chỉ còn swing + số tròn)";
        private static readonly CultureInfo Vi = CultureInfo.GetCultureInfo("vi-VN");

        public VungCanhLenh() : base()
        {
            Name = "Vùng Canh Lệnh";
            Description = "Vùng hỗ trợ/kháng cự ổn định (swing M5/M15, mốc phiên, số tròn) + bảng tra xác suất chạm/bị quét theo khoảng cách. " +
                          "MÔ TẢ tần suất lịch sử, KHÔNG phải tín hiệu. Cần Volume Analysis. Add vào chart M1.";
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
            lock (_calc) { _feeder = new VclFeeder(); _lastN = -1; _lastVa = false; _vaLoaded = false; lock (_sync) _render = null; }
        }

        /// <summary>KHÔNG chờ Volume Analysis: chưa có footprint vẫn vẽ (chỉ swing + số tròn) và ghi chú trong bảng;
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
                var rs = new RenderState { Close = core.Close, U = core.U, Phase = core.Phase, Note = _feeder.BuiltWithLevels ? null : NoVaNote };
                foreach (var z in core.Display) rs.Zones.Add(z.Clone());
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
        private static string Pct(int v) => v < 0 ? "—" : v + "%";

        /// <summary>Khoảng cách tới cạnh gần (giá, ≥ 0); vùng chứa giá = 0.</summary>
        private static double Dist(VZone z, double c) => z.Slot == 'K' ? 0 : (z.Side > 0 ? Math.Max(0, z.Lo - c) : Math.Max(0, c - z.Hi));

        private static string RoleName(VZone z) => z.Slot == 'K' ? "đang kiểm tra" : (z.Side > 0 ? "kháng cự" : "hỗ trợ") + (z.Slot == 'F' ? " (xa)" : "");

        private static string Label(VZone z, RenderState rs)
        {
            string head = z.Types() + " · " + F(z.Score, "0");
            if (z.Slot == 'K')
                return head + " · đang kiểm tra · quét ≥0,5u≈" + Pct(VclTables.Sweep[rs.Phase, 1]);
            double du = Dist(z, rs.Close) / rs.U;
            int bin = VclTables.Bin(du);
            if (bin < 0) return head + " · " + F(du) + "u";
            return head + " · " + F(du) + "u · chạm 30′≈" + Pct(VclTables.Reach[rs.Phase][bin, 1]) + " · quay ≥2u≈" + Pct(VclTables.Revert2u[bin]);
        }

        private static List<string> TableLines(RenderState rs, bool showFar)
        {
            var lines = new List<string>
            {
                $"Vùng Canh Lệnh · pha {Vcl.PhaseName[rs.Phase]} · u = {F(rs.U, "0.00")} · SL quét ≥0,25/0,5/1,0u: " +
                $"{Pct(VclTables.Sweep[rs.Phase, 0])}/{Pct(VclTables.Sweep[rs.Phase, 1])}/{Pct(VclTables.Sweep[rs.Phase, 2])}",
                "vai          lo – hi              d (u · USD)    chạm 15/30/60/120 nến",
            };
            var zs = new List<VZone>(rs.Zones);
            zs.Sort((a, b) => -(a.Lo + a.Hi).CompareTo(b.Lo + b.Hi));   // trên → dưới
            foreach (var z in zs)
            {
                if (z.Slot == 'F' && !showFar) continue;
                double d = Dist(z, rs.Close), du = d / rs.U;
                int bin = z.Slot == 'K' ? -1 : VclTables.Bin(du);
                string reach = z.Slot == 'K' ? "giá đang trong vùng"
                             : bin < 0 ? "xa > 12u"
                             : $"{Pct(VclTables.Reach[rs.Phase][bin, 0])}/{Pct(VclTables.Reach[rs.Phase][bin, 1])}/{Pct(VclTables.Reach[rs.Phase][bin, 2])}/{Pct(VclTables.Reach[rs.Phase][bin, 3])}";
                lines.Add($"{RoleName(z),-13}{F(z.Lo)} – {F(z.Hi),-10}{F(du) + "u · " + F(d) + "$",-15}{reach}");
            }
            if (!string.IsNullOrEmpty(rs.Note)) lines.Add("⚠ " + rs.Note);
            lines.Add("Tần suất lịch sử 20 phiên GCZ26 — không phải tín hiệu.");
            return lines;
        }

        // ---------------------------------------------------------------- vẽ
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
                if (!double.IsNaN(rs.U) && rs.U > 0)
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
                            string s = Label(z, rs);
                            var sz = gr.MeasureString(s, fLbl);
                            float lx = clip.Right - sz.Width - 6, ly = top + h / 2 - sz.Height / 2;
                            using (var bg = new SolidBrush(Color.FromArgb(150, 14, 16, 22))) gr.FillRectangle(bg, lx - 2, ly, sz.Width + 4, sz.Height);
                            using (var br = new SolidBrush(Color.FromArgb(235, Color.White))) gr.DrawString(s, fLbl, br, lx, ly);
                        }
                    }
                }
                if (ShowTable || !string.IsNullOrEmpty(rs.Warn) || !string.IsNullOrEmpty(rs.Note))
                {
                    var lines = !string.IsNullOrEmpty(rs.Warn) ? new List<string> { "⚠ " + rs.Warn }
                              : double.IsNaN(rs.U) ? new List<string> { "Vùng Canh Lệnh: chưa đủ 10 nến để tính u" }
                              : ShowTable ? TableLines(rs, ShowFar) : new List<string> { "⚠ " + rs.Note };
                    using var fTab = new Font("Consolas", 8, FontStyle.Regular);
                    float lh = fTab.GetHeight(gr) + 1, w = 0;
                    foreach (var l in lines) w = Math.Max(w, gr.MeasureString(l, fTab).Width);
                    float x0 = clip.Right - w - 12, y0 = clip.Top + 6;            // góc trên-phải
                    using (var bg = new SolidBrush(Color.FromArgb(185, 14, 16, 22))) gr.FillRectangle(bg, x0 - 4, y0 - 2, w + 8, lh * lines.Count + 4);
                    for (int i = 0; i < lines.Count; i++)
                    {
                        Color c = lines[i].StartsWith("⚠") ? Color.FromArgb(255, 170, 120)
                                : i == 0 ? Color.White : (i == lines.Count - 1 ? Color.FromArgb(160, 165, 175) : Color.FromArgb(205, 210, 220));
                        using var br = new SolidBrush(c);
                        gr.DrawString(lines[i], fTab, br, x0, y0 + i * lh);
                    }
                }
            }
            catch (Exception ex) { LogErr(ex, "OnPaintChart"); }
            finally { gr.SetClip(prevClip); }
        }
    }
}
