// ============================================================================
//  Benzo Trader — chuẩn setup CORVEN cho NQ M1 (làm lại từ đầu 2026-11-26, bản 3: Break + Follow trend, không bias)
// ============================================================================
//  Add vào chart NQ / MNQ khung M1 có Volume Analysis. Tín hiệu order flow lấy từ lõi OrderFlowBubbles THẬT (nối nguồn lúc build,
//  chạy qua khe TEST, tham số mặc định "Theo CORVEN") — đúng bộ chấm / Big Trade / kiệt sức / vùng stacked / stop hunt đã khớp chart CORVEN.
//  Luật: research/nq_setup_2026-11-26/SPEC-SETUP-NQ.md · lõi thuần: BenzoNq.cs · cầu nối: BenzoNqOfb.cs.
//  Chỉ xử lý nến ĐÃ ĐÓNG; vào lệnh ở giá mở nến kế. Lịch sử đổi (nạp thêm nến cũ) ⇒ tính lại từ đầu.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using TradingPlatform.BusinessLayer;
    using RangeBox;

    public class BenzoTrader : Indicator, IVolumeAnalysisIndicator
    {
        [InputParameter("Hiện entry", 10)]
        public bool ShowEntries { get; set; } = true;
        [InputParameter("Hiện range", 11)]
        public bool ShowRange { get; set; } = true;
        [InputParameter("Hiện bảng thống kê", 12)]
        public bool ShowTable { get; set; } = true;

        public const string BacktestLine = "Backtest bản 3: NQ 26/10–25/11 179 lệnh +0,09R/lệnh, nhưng 14/09–23/10 111 lệnh −0,15R/lệnh · chạy thử, không phải khuyến nghị";

        private sealed class BoxV { public DateTime T0, T1; public double Top, Bot; public RangeState St; }
        private sealed class RenderState
        {
            public List<NqTrade> Trades = new();
            public List<BoxV> Boxes = new();
            public List<string> Lines = new();
            public string Warn;
        }

        private readonly object _calc = new(), _sync = new();
        private RenderState _render;
        private bool _vaLoaded;
        private NqRunner _run;
        private DateTime _firstBar;
        private int _lastCount;
        private string _dir;

        public BenzoTrader() : base()
        {
            Name = "Benzo Trader";
            Description = "Benzo Trader — chuẩn setup CORVEN cho NQ M1: Break (retest cạnh range vừa phá) + Follow trend (nhịp hồi nông của move đang đi), "
                        + "xác nhận bằng bóng + delta + một tín hiệu order flow nữa, SL sau mốc, TP 2R. Cần Volume Analysis. " + BacktestLine;
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            lock (_calc) _vaLoaded = true;
            SafeProcess("VolumeAnalysisData_Loaded");
        }

        protected override void OnInit()
        {
            base.OnInit();
            _dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "BenzoTrader");
            try { Directory.CreateDirectory(_dir); } catch { }
        }

        protected override void OnClear()
        {
            lock (_calc) { _vaLoaded = false; _run = null; _lastCount = 0; lock (_sync) _render = null; }
        }

        protected override void OnUpdate(UpdateArgs args)
        {
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            if (!_vaLoaded) lock (_calc) _vaLoaded = true;
            SafeProcess("OnUpdate");
        }

        private void SafeProcess(string where)
        {
            try { Process(); }
            catch (Exception ex)
            {
                LogErr(ex.ToString(), where);
                lock (_sync) _render = new RenderState { Warn = "LỖI: " + ex.Message };
            }
        }

        private void LogErr(string text, string where)
        {
            try { File.AppendAllText(Path.Combine(_dir ?? Path.GetTempPath(), "error_log.txt"), $"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}Z [{Name}] {where}: {text}\n"); }
            catch { }
        }

        private static bool IsNasdaq(string s)
        {
            if (string.IsNullOrEmpty(s)) return false;
            var u = s.ToUpperInvariant().TrimStart('/');
            return u.StartsWith("NQ") || u.StartsWith("MNQ");
        }

        private void Process()
        {
            lock (_calc)
            {
                if (!_vaLoaded || HistoricalData == null || Symbol == null) return;
                var at = HistoricalData.Aggregation as HistoryAggregationTime;
                bool m1 = at != null && at.Period.BasePeriod == BasePeriod.Minute && at.Period.PeriodMultiplier == 1;
                if (!m1 || !IsNasdaq(Symbol.Name))
                {
                    lock (_sync) _render = new RenderState { Warn = "Benzo Trader chỉ chạy trên chart NQ / MNQ khung M1" };
                    return;
                }
                int n = HistoricalData.Count;
                if (n < 3) return;
                var b0 = HistoricalData[0, SeekOriginHistory.Begin] as HistoryItemBar;
                if (b0 == null) return;
                if (_run == null || b0.TimeLeft != _firstBar || n < _lastCount)
                {
                    string safe = string.Concat(Symbol.Name.Select(c => char.IsLetterOrDigit(c) ? c : '_'));
                    string cache = Path.Combine(_dir ?? Path.GetTempPath(), "ofb_" + safe + "_m1.jsonl");
                    var hd = HistoricalData;
                    _run = new NqRunner(i => (i >= 0 && i < hd.Count) ? hd[i, SeekOriginHistory.Begin] as HistoryItemBar : null,
                                        Symbol.TickSize, Symbol.Name, cache, 0, new NqCfg { Tick = Symbol.TickSize });
                    _firstBar = b0.TimeLeft;
                    _run.Advance(n, cold: true);
                }
                else if (n != _lastCount) _run.Advance(n, cold: false);
                else _run.RefreshForming(n);
                _lastCount = n;
                Publish();
            }
        }

        private void Publish()
        {
            var m = _run.M;
            var rs = new RenderState { Trades = m.Trades.ToList() };
            var now = m.Processed > 0 ? m.B[m.Processed - 1].T : DateTime.MinValue;
            foreach (var r in m.Eng.Ranges)
            {
                if (r.State == RangeState.Dead || r.Start < 0 || r.Start >= m.B.Count) continue;
                rs.Boxes.Add(new BoxV { T0 = m.B[r.Start].T, T1 = now, Top = r.Top * m.Cfg.Tick, Bot = r.Bottom * m.Cfg.Tick, St = r.State });
            }
            var closed = m.Trades.Where(t => t.Closed).ToList();
            string Row(string name, List<NqTrade> l) => l.Count == 0 ? $"{name} · 0 lệnh"
                : $"{name} · {l.Count} lệnh · WR {100.0 * l.Count(t => t.R > 0) / l.Count:0} % · ΣR {l.Sum(t => t.R).ToString("+0.0;-0.0;0", CultureInfo.InvariantCulture)}";
            rs.Lines.Add("BENZO NQ CORVEN (" + NqCfg.Version + ") · " + Row("tất cả", closed) + (m.Open != null ? " · đang có 1 lệnh mở" : ""));
            rs.Lines.Add(Row("Break", closed.Where(t => t.Kind == "Break").ToList()));
            rs.Lines.Add(Row("Follow trend", closed.Where(t => t.Kind == "Follow trend").ToList()));
            rs.Lines.Add(BacktestLine);
            lock (_sync) _render = rs;
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
                gr.SmoothingMode = SmoothingMode.AntiAlias;
                var up = Color.FromArgb(38, 190, 120); var dn = Color.FromArgb(235, 80, 80);
                var act = Color.FromArgb(120, 200, 235); var brk = Color.FromArgb(150, 150, 150);
                float bw2 = 0;
                try { bw2 = (float)(CurrentChart.BarsWidth / 2.0); } catch { }
                if (ShowRange)
                    foreach (var b in rs.Boxes)
                    {
                        float x0 = (float)conv.GetChartX(b.T0), x1 = Math.Min((float)conv.GetChartX(b.T1) + 2 * bw2, clip.Right);
                        if (x1 < clip.Left || x0 > clip.Right) continue;
                        float y0 = (float)conv.GetChartY(b.Top), y1 = (float)conv.GetChartY(b.Bot);
                        var rect = new RectangleF(Math.Max(x0, clip.Left), Math.Min(y0, y1), Math.Max(2f, x1 - Math.Max(x0, clip.Left)), Math.Max(1f, Math.Abs(y1 - y0)));
                        if (b.St == RangeState.Broken)
                        {
                            using var pen = new Pen(Color.FromArgb(170, brk), 1f) { DashStyle = DashStyle.Dash };
                            gr.DrawRectangle(pen, rect.X, rect.Y, rect.Width, rect.Height);
                        }
                        else
                        {
                            using (var fill = new SolidBrush(Color.FromArgb(b.St == RangeState.Pending ? 18 : 28, act))) gr.FillRectangle(fill, rect);
                            using var pen = new Pen(Color.FromArgb(200, act), 1f) { DashStyle = b.St == RangeState.Pending ? DashStyle.Dot : DashStyle.Solid };
                            gr.DrawRectangle(pen, rect.X, rect.Y, rect.Width, rect.Height);
                        }
                    }
                if (ShowEntries)
                {
                    using var fLbl = new Font("Consolas", 8, FontStyle.Bold);
                    foreach (var s in rs.Trades)
                    {
                        bool open = !s.Closed;
                        float xE = (float)conv.GetChartX(s.EntryTime) + bw2;
                        float xEnd = open ? clip.Right : (float)conv.GetChartX(s.ExitTime) + 2 * bw2;
                        if (xEnd > clip.Right) xEnd = clip.Right;
                        if (xEnd < xE + 6) xEnd = xE + 6;
                        if (xEnd < clip.Left || xE > clip.Right) continue;
                        float yE = (float)conv.GetChartY(s.Entry), ySl = (float)conv.GetChartY(s.Sl), yTp = (float)conv.GetChartY(s.Tp);
                        if (Math.Max(ySl, yTp) < clip.Top || Math.Min(ySl, yTp) > clip.Bottom) continue;
                        Color dir = s.Side > 0 ? up : dn;
                        int a = open ? 255 : 150;
                        float xb = Math.Max(xE, clip.Left), wBox = xEnd - xb;
                        int aTp = open ? 55 : (s.R > 0 ? 95 : 28), aSl = open ? 55 : (s.R > 0 ? 28 : 95);
                        if (wBox > 0)
                        {
                            using (var bTp = new SolidBrush(Color.FromArgb(aTp, up))) gr.FillRectangle(bTp, xb, Math.Min(yE, yTp), wBox, Math.Max(1f, Math.Abs(yTp - yE)));
                            using (var bSl = new SolidBrush(Color.FromArgb(aSl, dn))) gr.FillRectangle(bSl, xb, Math.Min(yE, ySl), wBox, Math.Max(1f, Math.Abs(ySl - yE)));
                        }
                        using (var pTp = new Pen(Color.FromArgb(a, up), 1.6f)) gr.DrawLine(pTp, xb, yTp, xEnd, yTp);
                        using (var pSl = new Pen(Color.FromArgb(a, dn), 1.6f)) gr.DrawLine(pSl, xb, ySl, xEnd, ySl);
                        using (var pE = new Pen(Color.FromArgb(a, dir), 1.2f) { DashStyle = DashStyle.Dash }) gr.DrawLine(pE, xb, yE, xEnd, yE);
                        float sz = 6f;
                        var tri = s.Side > 0
                            ? new[] { new PointF(xE, yE + sz + 4), new PointF(xE - sz, yE + sz * 2 + 4), new PointF(xE + sz, yE + sz * 2 + 4) }
                            : new[] { new PointF(xE, yE - sz - 4), new PointF(xE - sz, yE - sz * 2 - 4), new PointF(xE + sz, yE - sz * 2 - 4) };
                        using (var br = new SolidBrush(Color.FromArgb(a, dir))) gr.FillPolygon(br, tri);
                        string lbl = $"{s.Kind} {s.SideText} · {s.Second}" + (s.Closed ? (s.R > 0 ? " ✓" : " ✗") : "");
                        float ly = s.Side > 0 ? yE + sz * 2 + 8 : yE - sz * 2 - 22;
                        var szL = gr.MeasureString(lbl, fLbl);
                        float lx = xE + szL.Width + 4 > clip.Right ? xE - szL.Width : xE;
                        using (var bg = new SolidBrush(Color.FromArgb(open ? 215 : 150, dir))) gr.FillRectangle(bg, lx - 2, ly - 1, szL.Width + 4, szL.Height + 1);
                        using (var br = new SolidBrush(Color.White)) gr.DrawString(lbl, fLbl, br, lx, ly);
                    }
                }
                if (ShowTable || !string.IsNullOrEmpty(rs.Warn))
                {
                    using var fTab = new Font("Consolas", 8, FontStyle.Regular);
                    var lines = ShowTable ? new List<string>(rs.Lines) : new List<string>();
                    if (!string.IsNullOrEmpty(rs.Warn)) lines.Add("⚠ " + rs.Warn);
                    float lh = fTab.GetHeight(gr) + 1, w = 0;
                    foreach (var ln in lines) w = Math.Max(w, gr.MeasureString(ln, fTab).Width);
                    float x0 = clip.Left + 6, y0 = clip.Bottom - lh * lines.Count - 8;
                    using (var bg = new SolidBrush(Color.FromArgb(170, 14, 16, 22))) gr.FillRectangle(bg, x0 - 3, y0 - 2, w + 8, lh * lines.Count + 4);
                    for (int i = 0; i < lines.Count; i++)
                    {
                        string ln = lines[i];
                        Color col = ln.StartsWith("BENZO") ? Color.White
                                  : ln.StartsWith("Backtest") || ln.StartsWith("⚠") ? Color.FromArgb(255, 170, 120) : Color.FromArgb(200, 205, 215);
                        using var br = new SolidBrush(col);
                        gr.DrawString(ln, fTab, br, x0, y0 + i * lh);
                    }
                }
            }
            catch (Exception ex) { LogErr(ex.ToString(), "OnPaintChart"); }
            finally { gr.SetClip(prevClip); }
        }
    }
}
