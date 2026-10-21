// ============================================================================
//  BenzoTrader — indicator signal cho Quantower / Optimus Flow (KHUNG, chưa có logic 4 setup)
// ============================================================================
//  Add vào chart M1 có Volume Analysis. Chỉ xử lý nến ĐÃ ĐÓNG, đúng 1 lần/nến, niêm phong theo
//  thời gian mở nến (sống qua reload). Logic thuần nằm ở BenzoCore.cs (test được). File này chỉ
//  là lớp dán: Settings, vòng đời, vẽ (bảng + mũi tên + SL/TP), Telegram + chụp ảnh Win32.
//  4 detector A/B/D/C (BenzoDetectors.cs) được cắm trong CreateDetectors() theo ưu tiên A > B > D > C.
//  Build: concat ProfileEngine.cs + BenzoCore.cs + file này (build.sh). Mọi `using` nằm trong namespace.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Drawing.Imaging;
    using System.IO;
    using System.Linq;
    using System.Runtime.InteropServices;
    using System.Threading;
    using System.Threading.Tasks;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;   // ProfileEngine.cs (concat) — dùng NewsCalendar (lịch tin Forex Factory)

    // ---------------------------------------------------------------- chụp ảnh cửa sổ (Win32)
    internal static class WinShot
    {
        [StructLayout(LayoutKind.Sequential)] private struct RECT { public int Left, Top, Right, Bottom; }
        [DllImport("user32.dll")] private static extern bool GetWindowRect(IntPtr h, out RECT r);
        [DllImport("user32.dll")] private static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")] private static extern bool IsIconic(IntPtr h);
        [DllImport("user32.dll")] private static extern int GetSystemMetrics(int n);
        [DllImport("user32.dll")] private static extern IntPtr WindowFromDC(IntPtr hdc);
        [DllImport("user32.dll")] private static extern IntPtr GetAncestor(IntPtr h, uint flags);
        [DllImport("user32.dll")] private static extern bool IsWindow(IntPtr h);
        [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr h);
        private delegate bool EnumProc(IntPtr h, IntPtr l);
        [DllImport("user32.dll")] private static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
        private static volatile IntPtr _chartHwnd;
        private static int _chartW, _chartH;
        private static long _lastProbe;

        /// <summary>Gọi trong OnPaintChart (trước khi vẽ): nhớ handle cửa sổ chart (WindowFromDC) + kích thước vùng chart,
        /// để chụp ĐÚNG vùng chart thay vì cả cửa sổ Optimus Flow.</summary>
        public static void NoteChart(Graphics gr, int chartW, int chartH)
        {
            _chartW = chartW; _chartH = chartH;
            long now = Environment.TickCount64;
            if (_chartHwnd != IntPtr.Zero && IsWindow(_chartHwnd) && now - _lastProbe < 5000) return;
            _lastProbe = now;
            IntPtr hdc = IntPtr.Zero;
            try
            {
                hdc = gr.GetHdc();
                IntPtr h = WindowFromDC(hdc);
                if (h != IntPtr.Zero && IsWindow(h) && h != GetAncestor(h, 2 /*GA_ROOT*/)) _chartHwnd = h;
            }
            catch { }
            finally { if (hdc != IntPtr.Zero) { try { gr.ReleaseHdc(hdc); } catch { } } }
        }

        private static bool TryChartRect(out RECT r, out string src)
        {
            r = default; src = null;
            try
            {
                IntPtr h = _chartHwnd;
                if (h != IntPtr.Zero && IsWindow(h) && IsWindowVisible(h) && !IsIconic(h) && GetWindowRect(h, out r)
                    && r.Right - r.Left >= 300 && r.Bottom - r.Top >= 200) { src = "vùng chart (handle từ DC vẽ)"; return true; }
                IntPtr main = Process.GetCurrentProcess().MainWindowHandle;
                if (main != IntPtr.Zero && _chartW >= 50 && _chartH >= 50)
                {
                    var list = new List<int[]>();
                    EnumChildWindows(main, (c, l) =>
                    {
                        if (IsWindowVisible(c) && GetWindowRect(c, out var rc)) list.Add(new[] { rc.Left, rc.Top, rc.Right, rc.Bottom });
                        return true;
                    }, IntPtr.Zero);
                    int i = BenzoCore.PickChartRect(list, _chartW, _chartH);
                    if (i >= 0) { r = new RECT { Left = list[i][0], Top = list[i][1], Right = list[i][2], Bottom = list[i][3] }; src = "vùng chart (cửa sổ con khớp kích thước)"; return true; }
                }
            }
            catch { }
            return false;
        }
        private const int SM_CXSCREEN = 0, SM_CYSCREEN = 1, SM_XVIRTUALSCREEN = 76, SM_YVIRTUALSCREEN = 77,
                          SM_CXVIRTUALSCREEN = 78, SM_CYVIRTUALSCREEN = 79;

        /// <summary>Chụp cửa sổ chính của tiến trình (hoặc cửa sổ đang foreground nếu không có), fallback toàn màn hình chính.
        /// Ném exception nếu cả hai đều hỏng. how = mô tả cách chụp (để ghi log).</summary>
        public static byte[] CapturePng(out string how)
        {
            Exception first = null;
            try
            {
                if (TryChartRect(out var cr, out string csrc))
                {
                    int vx0 = GetSystemMetrics(SM_XVIRTUALSCREEN), vy0 = GetSystemMetrics(SM_YVIRTUALSCREEN);
                    int vw0 = GetSystemMetrics(SM_CXVIRTUALSCREEN), vh0 = GetSystemMetrics(SM_CYVIRTUALSCREEN);
                    int l0 = Math.Max(cr.Left, vx0), t0 = Math.Max(cr.Top, vy0);
                    int r0 = Math.Min(cr.Right, vx0 + vw0), b0 = Math.Min(cr.Bottom, vy0 + vh0);
                    if (r0 - l0 >= 300 && b0 - t0 >= 200) { var png0 = Grab(l0, t0, r0 - l0, b0 - t0); how = csrc; return png0; }
                }
            }
            catch (Exception ex0) { first = ex0; }
            try
            {
                IntPtr h = IntPtr.Zero;
                try { h = Process.GetCurrentProcess().MainWindowHandle; } catch { }
                string src = "cửa sổ chính";
                if (h == IntPtr.Zero) { h = GetForegroundWindow(); src = "cửa sổ foreground"; }
                if (h != IntPtr.Zero && !IsIconic(h) && GetWindowRect(h, out var r))
                {
                    // cắt theo màn hình ảo (nhiều màn hình có toạ độ âm); cửa sổ maximize hay lòi ~8px ra ngoài
                    int vx = GetSystemMetrics(SM_XVIRTUALSCREEN), vy = GetSystemMetrics(SM_YVIRTUALSCREEN);
                    int vw = GetSystemMetrics(SM_CXVIRTUALSCREEN), vh = GetSystemMetrics(SM_CYVIRTUALSCREEN);
                    int l = Math.Max(r.Left, vx), t = Math.Max(r.Top, vy);
                    int rr = Math.Min(r.Right, vx + vw), bb = Math.Min(r.Bottom, vy + vh);
                    if (rr - l >= 200 && bb - t >= 150)
                    {
                        var png = Grab(l, t, rr - l, bb - t);
                        how = src; return png;
                    }
                }
                first = new InvalidOperationException("không lấy được khung cửa sổ hợp lệ");
            }
            catch (Exception ex) { first = ex; }

            try
            {   // fallback: toàn màn hình chính (không cần System.Windows.Forms)
                int w = GetSystemMetrics(SM_CXSCREEN), hgt = GetSystemMetrics(SM_CYSCREEN);
                var png = Grab(0, 0, w, hgt);
                how = "toàn màn hình chính (fallback: " + first.Message + ")";
                return png;
            }
            catch (Exception ex2)
            {
                throw new InvalidOperationException("chụp ảnh lỗi: " + first.Message + " / " + ex2.Message);
            }
        }

        private static byte[] Grab(int x, int y, int w, int h)
        {
            if (w <= 0 || h <= 0) throw new InvalidOperationException("kích thước ảnh 0");
            using var bmp = new Bitmap(w, h, PixelFormat.Format24bppRgb);
            using (var g = Graphics.FromImage(bmp)) g.CopyFromScreen(x, y, 0, 0, new Size(w, h), CopyPixelOperation.SourceCopy);
            using var ms = new MemoryStream();
            if (w > 1600)
            {   // thu nhỏ để ảnh Telegram gọn, vẫn đọc được số
                int nw = 1600, nh = (int)Math.Round(h * 1600.0 / w);
                using var small = new Bitmap(nw, nh, PixelFormat.Format24bppRgb);
                using (var g2 = Graphics.FromImage(small)) { g2.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic; g2.DrawImage(bmp, 0, 0, nw, nh); }
                small.Save(ms, ImageFormat.Png);
            }
            else bmp.Save(ms, ImageFormat.Png);
            return ms.ToArray();
        }
    }

    // ---------------------------------------------------------------- indicator
    public class BenzoTrader : Indicator, IVolumeAnalysisIndicator
    {
        // ======= Settings (plan 2.3 — KHÔNG có ngưỡng số nào khác) =======
        [InputParameter("Lệch giờ (UTC → VN)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Telegram: bật", 20)]
        public bool TeleEnabled { get; set; } = false;
        [InputParameter("Telegram: bot token", 21)]
        public string TeleBotToken { get; set; } = "";      // ĐIỀN TAY — repo công khai, KHÔNG hardcode
        [InputParameter("Telegram: chat id", 22)]
        public string TeleChatId { get; set; } = "";
        [InputParameter("Telegram: gửi thử (bật lên để gửi)", 23)]
        public bool TeleTestNow { get; set; } = false;
        [InputParameter("Bật setup A · Phá hồi", 30)]
        public bool EnableA { get; set; } = true;
        [InputParameter("Bật setup B · Hấp thụ", 31)]
        public bool EnableB { get; set; } = true;
        [InputParameter("Bật setup C · Fade cạnh", 32)]
        public bool EnableC { get; set; } = true;
        [InputParameter("Bật setup D · Trap", 33)]
        public bool EnableD { get; set; } = true;
        [InputParameter("Đặt lại thống kê (bật lên để đặt)", 40)]
        public bool ResetStatsNow { get; set; } = false;
        [InputParameter("Hiện bảng", 50)]
        public bool ShowTable { get; set; } = true;

        // ======= trạng thái =======
        private sealed class RenderState
        {
            public List<Signal> Sigs = new();
            public List<string> Lines = new();
            public string Warn;
            public int Digits = 1;
        }

        private readonly object _calc = new();
        private readonly object _sync = new();
        private RenderState _render;
        private bool _vaLoaded;
        private int _lastN = -1;
        private int _digits = 1;
        private BenzoEngine _engine;
        private SignalCache _cache;
        private readonly List<int> _hdOfBar = new();   // chỉ số HistoricalData của từng nến trong engine
        private DateTime? _resetUtc;
        private string _dir, _symbol, _tf, _resetPath, _csvPath, _logPath;
        private readonly TeleClient _tele = new();
        private bool _armed;
        private readonly HashSet<string> _seen = new(), _openSent = new(), _closedSent = new();
        private bool _lastTest, _lastReset;
        private string _teleStatus;

        public BenzoTrader() : base()
        {
            Name = "Benzo Trader";
            Description = "Benzo Trader (khung): 4 setup A/B/C/D trên nến M1 đã đóng, thống kê, Telegram kèm ảnh. Cần Volume Analysis. Add vào chart M1.";
            SeparateWindow = false;
        }

        /// <summary>Danh sách detector THEO THỨ TỰ ƯU TIÊN A > B > D > C. Agent port setup cắm vào đây.</summary>
        private static List<ISetupDetector> CreateDetectors()
        {
            return new List<ISetupDetector> { new DetectorA(), new DetectorB(), new DetectorD(), new DetectorC() };
        }

        /// <summary>Tin USD mức cao trong ±15 phút (expose cho detector; cần lịch tin đã tải — chỉ phủ tuần hiện tại).</summary>
        public bool IsNewsBlocked(DateTime utc) => NewsCalendar.IsBlocked(utc, TzOffset, BenzoCore.NewsBlockMinutes);

        private bool Enabled(char s) => s == 'A' ? EnableA : s == 'B' ? EnableB : s == 'C' ? EnableC : EnableD;

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded()
        {
            lock (_calc) { _vaLoaded = true; }
            SafeProcess("VolumeAnalysisData_Loaded");
        }

        protected override void OnInit()
        {
            base.OnInit();
            _dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "BenzoTrader");
            try { Directory.CreateDirectory(_dir); } catch { }
            _logPath = Path.Combine(_dir, "tele_log.txt");
        }

        protected override void OnClear()
        {
            lock (_calc)
            {
                _vaLoaded = false; _lastN = -1; _engine = null; _cache = null; _hdOfBar.Clear();
                _armed = false; _seen.Clear(); _openSent.Clear(); _closedSent.Clear(); _teleStatus = null;
                lock (_sync) _render = null;
            }
        }

        protected override void OnUpdate(UpdateArgs args)
        {
            PollButtons();
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            if (!_vaLoaded) lock (_calc) { _vaLoaded = true; }   // callback không bắn nếu VA đã tính sẵn (xem EntrySignal)
            SafeProcess("OnUpdate");
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
                Directory.CreateDirectory(_dir ?? Path.GetTempPath());
                File.AppendAllText(Path.Combine(_dir ?? Path.GetTempPath(), "error_log.txt"),
                    $"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}Z [{Name}] {where}: {ex}\n");
            }
            catch { }
        }

        // ---------------------------------------------------------------- nút bấm (bool bật lên = bấm)
        private void PollButtons()
        {
            bool testEdge = TeleTestNow && !_lastTest; _lastTest = TeleTestNow;
            bool resetEdge = ResetStatsNow && !_lastReset; _lastReset = ResetStatsNow;
            if (testEdge) SendTest();
            if (resetEdge)
            {
                try
                {
                    var now = DateTime.UtcNow;
                    lock (_calc)
                    {
                        EnsurePaths();
                        _resetUtc = now;
                        BenzoCore.SaveResetMark(_resetPath, now);
                        BuildRender();
                    }
                    CurrentChart?.RedrawBuffer();
                }
                catch (Exception ex) { LogErr(ex, "reset"); }
            }
        }

        private void ConfigTele()
        {
            _tele.Token = (TeleBotToken ?? "").Trim();
            _tele.ChatId = (TeleChatId ?? "").Trim();
            _tele.LogPath = _logPath ?? Path.Combine(Path.GetTempPath(), "benzo_tele_log.txt");
        }

        private void EnsurePaths()
        {
            if (_dir == null) OnInit();
            _symbol = Symbol?.Name ?? "X";
            if (_tf == null) _tf = BenzoCore.Sanitize(HistoricalData?.Aggregation?.Title ?? HistoricalData?.Aggregation?.Name ?? "tf");
            string sym = BenzoCore.Sanitize(_symbol);
            _resetPath = Path.Combine(_dir, $"reset_{sym}.txt");
            _csvPath = Path.Combine(_dir, $"signals_{sym}.csv");
        }

        // ---------------------------------------------------------------- xử lý nến đóng
        private void Process()
        {
            lock (_calc)
            {
                var hd = HistoricalData;
                if (hd == null) return;
                double tick = Symbol?.TickSize ?? 0;
                if (tick <= 0) return;
                int n = hd.Count;
                if (n < 3 || n == _lastN) return;     // chỉ chạy khi có nến mới
                _digits = Math.Max(0, (int)Math.Round(-Math.Log10(tick)));
                EnsurePaths();
                ConfigTele();
                NewsCalendar.Refresh(_dir, TzOffset, t => BenzoLog.Write(_logPath, t));   // tải nền, cache 1h

                if (_engine == null || _engine.Bars.Count > n - 1)   // lần đầu, hoặc lịch sử bị cắt ngắn → dựng lại
                {
                    _cache = new SignalCache(Path.Combine(_dir, $"cache_{BenzoCore.Sanitize(_symbol)}_{_tf}.jsonl"));
                    _cache.Load();
                    _resetUtc = BenzoCore.LoadResetMark(_resetPath);
                    _engine = new BenzoEngine(_symbol, tick, _cache, CreateDetectors())
                    {
                        IsEnabled = Enabled,
                        IsNewsBlocked = IsNewsBlocked,
                        GetLevels = ReadLevels,
                    };
                    _hdOfBar.Clear();
                    _armed = false; _seen.Clear(); _openSent.Clear(); _closedSent.Clear();
                }
                _engine.TzOffset = TzOffset;

                int closed = n - 2;                     // nến cuối đang chạy → chỉ xử lý tới Count−2
                for (int i = _engine.Bars.Count; i <= closed; i++)
                {
                    if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) { _engine.Bars.Add(PlaceholderBar(i)); _hdOfBar.Add(i); continue; }
                    var t = b.VolumeAnalysisData?.Total;
                    _engine.Bars.Add(new BarData
                    {
                        Idx = i, Time = b.TimeLeft, O = b.Open, H = b.High, L = b.Low, C = b.Close,
                        Vol = t?.Volume ?? b.Volume, BuyVol = t?.BuyVolume ?? 0, SellVol = t?.SellVolume ?? 0, Delta = t?.Delta ?? 0,
                    });
                    _hdOfBar.Add(i);
                }
                if (_engine.Bars.Count >= 2)
                {
                    double bm = (_engine.Bars[_engine.Bars.Count - 1].Time - _engine.Bars[_engine.Bars.Count - 2].Time).TotalMinutes;
                    _engine.BarMinutes = bm > 0 && bm <= 60 ? (int)Math.Round(bm) : 1;
                }

                var res = _engine.Advance(closed);
                bool first = !_armed;
                if (first)
                {
                    // lần quét đầu sau attach/reload: chỉ NẠP id, không bắn
                    foreach (var s in _engine.Signals)
                    {
                        _seen.Add(s.Id);
                        if (s.IsClosed) _closedSent.Add(s.Id); else _openSent.Add(s.Id);   // lệnh đang chạy vẫn được báo ĐÓNG
                    }
                    _armed = true;
                    _teleStatus = $"nạp {_seen.Count} lệnh cũ (không báo) · sẵn sàng";
                }
                else EmitTele(res, closed);

                if (first || res.Opened.Count > 0 || res.Closed.Count > 0)
                {
                    try { SignalCsv.Merge(_csvPath, _engine.Signals); } catch (Exception ex) { LogErr(ex, "csv"); }
                }
                BuildRender();
                _lastN = n;
            }
            CurrentChart?.RedrawBuffer();
        }

        private BarData PlaceholderBar(int i)
        {
            double c = _engine.Bars.Count > 0 ? _engine.Bars[_engine.Bars.Count - 1].C : 0;
            DateTime t = _engine.Bars.Count > 0 ? _engine.Bars[_engine.Bars.Count - 1].Time.AddMinutes(1) : DateTime.UtcNow;
            return new BarData { Idx = i, Time = t, O = c, H = c, L = c, C = c };
        }

        /// <summary>Footprint từng mức giá của nến idx (engine) — dictionary do platform giữ nên thử lại nếu bị sửa giữa chừng.</summary>
        private IReadOnlyList<LevelVol> ReadLevels(int idx)
        {
            try
            {
                var hd = HistoricalData;
                if (hd == null || idx < 0 || idx >= _hdOfBar.Count) return Array.Empty<LevelVol>();
                if (hd[_hdOfBar[idx], SeekOriginHistory.Begin] is not HistoryItemBar b) return Array.Empty<LevelVol>();
                for (int attempt = 0; attempt < 3; attempt++)
                {
                    try
                    {
                        var pl = b.VolumeAnalysisData?.PriceLevels;
                        if (pl == null) return Array.Empty<LevelVol>();
                        var list = new List<LevelVol>(pl.Count);
                        foreach (var kv in pl) list.Add(new LevelVol(kv.Key, kv.Value.SellVolume, kv.Value.BuyVolume, kv.Value.Volume));
                        list.Sort((x, y) => x.Price.CompareTo(y.Price));
                        return list;
                    }
                    catch (InvalidOperationException) { }   // collection modified → thử lại
                }
            }
            catch { }
            return Array.Empty<LevelVol>();
        }

        private void BuildRender()
        {
            if (_engine == null) return;
            var st = BenzoCore.ComputeStats(_engine.Signals, _resetUtc);
            var rs = new RenderState
            {
                Sigs = _engine.Signals.Select(s => s.Clone()).ToList(),
                Lines = BenzoCore.TableLines(st, new[] { EnableA, EnableB, EnableC, EnableD }),
                Digits = _digits,
                Warn = TeleEnabled && !string.IsNullOrEmpty(_tele.LastError) ? "Telegram: " + _tele.LastError : null,
            };
            lock (_sync) _render = rs;
        }

        // ---------------------------------------------------------------- Telegram
        private void EmitTele(BenzoEngine.AdvanceResult res, int lastClosed)
        {
            if (!TeleEnabled || !_tele.Ready) return;
            try
            {
                int bm = _engine.BarMinutes;
                foreach (var s in res.Opened)
                {
                    if (!_seen.Add(s.Id)) continue;
                    if (s.BarIdx != lastClosed) continue;                     // chỉ nến vừa đóng
                    double age = (DateTime.UtcNow - s.Time.AddMinutes(bm)).TotalSeconds;
                    if (age > BenzoCore.TeleMaxAgeSec || age < -BenzoCore.TeleMaxAgeSec) { _teleStatus = $"BỎ {s.Id} — lệch đồng hồ {age:0}s"; continue; }
                    _openSent.Add(s.Id);
                    if (!TryClaim("open", s.Id)) continue;                    // chart/instance khác đã gửi
                    string cap = BenzoCore.ComposeOpen(s, _symbol, TzOffset, bm, _digits);
                    _teleStatus = $"MỞ {s.Id}";
                    SendOpenAsync(cap);
                }
                foreach (var s in res.Closed)
                {
                    if (!_openSent.Contains(s.Id) || !_closedSent.Add(s.Id)) continue;
                    if (!TryClaim("close", s.Id)) continue;
                    string msg = BenzoCore.ComposeClose(s, TzOffset, bm);
                    _teleStatus = $"ĐÓNG {s.Id}";
                    var snapshot = CloneTele();
                    Task.Run(async () =>
                    {
                        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
                        await snapshot.SendMessageAsync(msg, cts.Token).ConfigureAwait(false);
                    });
                }
            }
            catch (Exception ex) { _teleStatus = "LỖI Telegram: " + ex.Message; LogErr(ex, "EmitTele"); }
        }

        private TeleClient CloneTele() => new TeleClient { Token = _tele.Token, ChatId = _tele.ChatId, LogPath = _tele.LogPath };

        /// <summary>Khoá tạo nguyên tử: nhiều chart/instance cùng symbol chỉ 1 cái gửi tin cho mỗi id.</summary>
        private bool TryClaim(string kind, string id)
        {
            try
            {
                string d = Path.Combine(_dir, "sent");
                Directory.CreateDirectory(d);
                using var fs = new FileStream(Path.Combine(d, BenzoCore.Sanitize(kind + "_" + id) + ".lock"), FileMode.CreateNew);
                return true;
            }
            catch (IOException) { return false; }
            catch { return true; }   // không tạo được khoá (quyền...) → vẫn gửi còn hơn mất tín hiệu
        }

        /// <summary>Chụp ảnh ở thread riêng (không chặn nến), gửi sendPhoto (tối đa 10s); lỗi thì gửi text không ảnh.</summary>
        private void SendOpenAsync(string caption)
        {
            var tele = CloneTele();
            Task.Run(async () =>
            {
                try
                {
                    bool ok = false;
                    try
                    {
                        try { CurrentChart?.RedrawBuffer(); } catch { }
                        await Task.Delay(1200).ConfigureAwait(false);          // chờ chart vẽ xong hộp SL/TP của lệnh mới
                        byte[] png = WinShot.CapturePng(out string how);
                        tele.Log("chụp ảnh OK (" + how + ", " + png.Length / 1024 + " KB)");
                        using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10));
                        ok = await tele.SendPhotoAsync(png, caption, cts.Token).ConfigureAwait(false);
                    }
                    catch (Exception ex) { tele.Log("ảnh LỖI: " + tele.Redact(ex.Message)); }
                    if (!ok)
                    {
                        using var cts2 = new CancellationTokenSource(TimeSpan.FromSeconds(10));
                        ok = await tele.SendMessageAsync(caption + "\n(không có ảnh)", cts2.Token).ConfigureAwait(false);
                    }
                    _tele.LastError = ok ? "" : tele.LastError;
                }
                catch (Exception ex) { tele.Log("SendOpenAsync LỖI: " + tele.Redact(ex.Message)); }
            });
        }

        private void SendTest()
        {
            ConfigTele();
            if (!_tele.Ready) { BenzoLog.Write(_logPath ?? Path.Combine(Path.GetTempPath(), "benzo_tele_log.txt"), "gửi thử: thiếu bot token / chat id"); _tele.LastError = "thiếu bot token / chat id"; return; }
            string cap = $"🔔 TEST — Benzo Trader ({Symbol?.Name ?? "?"}) bot chạy OK\n(mẫu: 🟢 BUY · A Phá hồi · ... kèm ảnh chụp Optimus Flow)";
            SendOpenAsync(cap);
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
            try
            {   // kích thước cả vùng chart (mọi cửa sổ con: nến + volume + delta) để chụp đúng vùng chart
                int minL = int.MaxValue, minT = int.MaxValue, maxR = 0, maxB = 0;
                foreach (var w in CurrentChart.Windows) { var rc = w.ClientRectangle; minL = Math.Min(minL, rc.Left); minT = Math.Min(minT, rc.Top); maxR = Math.Max(maxR, rc.Right); maxB = Math.Max(maxB, rc.Bottom); }
                if (maxR > minL && maxB > minT) WinShot.NoteChart(gr, maxR - minL, maxB - minT);
            }
            catch { }
            var prevClip = gr.ClipBounds; gr.SetClip(clip);
            try
            {
                gr.SmoothingMode = SmoothingMode.AntiAlias;
                var up = Color.FromArgb(38, 190, 120); var dn = Color.FromArgb(235, 80, 80);
                using var fLbl = new Font("Consolas", 8, FontStyle.Bold);
                foreach (var s in rs.Sigs)
                {
                    bool open = !s.IsClosed;
                    float xE = (float)conv.GetChartX(s.Time);
                    float xEnd = open ? clip.Right : (float)conv.GetChartX(s.ExitTime);
                    if (xEnd > clip.Right) xEnd = clip.Right;
                    if (xEnd < xE + 6) xEnd = xE + 6;
                    if (xEnd < clip.Left || xE > clip.Right) continue;   // cull ngoài màn hình
                    float yE = (float)conv.GetChartY(s.Entry), ySl = (float)conv.GetChartY(s.Sl), yTp = (float)conv.GetChartY(s.Tp);
                    if (Math.Max(ySl, yTp) < clip.Top || Math.Min(ySl, yTp) > clip.Bottom) continue;
                    Color dir = s.Side > 0 ? up : dn;
                    int a = open ? 255 : 150;
                    float xb = Math.Max(xE, clip.Left);
                    // vùng tô nền: xanh = từ giá vào tới TP, đỏ = từ giá vào tới SL (đậm hơn ở phía đã xảy ra khi lệnh đóng)
                    int aTp = open ? 55 : (s.Outcome == "TP" ? 95 : 28);
                    int aSl = open ? 55 : (s.Outcome == "SL" ? 95 : 28);
                    float wBox = xEnd - xb;
                    if (wBox > 0)
                    {
                        using (var bTp = new SolidBrush(Color.FromArgb(aTp, up)))
                            gr.FillRectangle(bTp, xb, Math.Min(yE, yTp), wBox, Math.Max(1f, Math.Abs(yTp - yE)));
                        using (var bSl = new SolidBrush(Color.FromArgb(aSl, dn)))
                            gr.FillRectangle(bSl, xb, Math.Min(yE, ySl), wBox, Math.Max(1f, Math.Abs(ySl - yE)));
                    }
                    using (var pTp = new Pen(Color.FromArgb(a, up), 1.6f)) gr.DrawLine(pTp, xb, yTp, xEnd, yTp);
                    using (var pSl = new Pen(Color.FromArgb(a, dn), 1.6f)) gr.DrawLine(pSl, xb, ySl, xEnd, ySl);
                    using (var pE = new Pen(Color.FromArgb(Math.Min(255, a), dir), 1.2f) { DashStyle = DashStyle.Dash }) gr.DrawLine(pE, xb, yE, xEnd, yE);
                    // mũi tên tại nến vào (BUY chỉ lên bên dưới giá vào, SELL chỉ xuống bên trên)
                    float sz = 6f;
                    var tri = s.Side > 0
                        ? new[] { new PointF(xE, yE + sz + 4), new PointF(xE - sz, yE + sz * 2 + 4), new PointF(xE + sz, yE + sz * 2 + 4) }
                        : new[] { new PointF(xE, yE - sz - 4), new PointF(xE - sz, yE - sz * 2 - 4), new PointF(xE + sz, yE - sz * 2 - 4) };
                    using (var br = new SolidBrush(Color.FromArgb(a, dir))) gr.FillPolygon(br, tri);
                    string lbl = s.Setup + " " + BenzoCore.SetupName(s.Setup) + (s.IsClosed ? (s.Outcome == "TP" ? " ✓" : " ✗") : "");
                    float ly = s.Side > 0 ? yE + sz * 2 + 8 : yE - sz * 2 - 22;
                    var szLbl = gr.MeasureString(lbl, fLbl);
                    using (var bgLbl = new SolidBrush(Color.FromArgb(open ? 215 : 150, dir)))
                        gr.FillRectangle(bgLbl, xE + 6, ly - 1, szLbl.Width + 4, szLbl.Height + 1);
                    using (var br = new SolidBrush(Color.FromArgb(255, 255, 255, 255))) gr.DrawString(lbl, fLbl, br, xE + 8, ly);
                }

                if (ShowTable)
                {
                    using var fTab = new Font("Consolas", 8, FontStyle.Regular);
                    var lines = new List<string>(rs.Lines);
                    if (!string.IsNullOrEmpty(rs.Warn)) lines.Add("⚠ " + rs.Warn);
                    float lh = fTab.GetHeight(gr) + 1, w = 0;
                    foreach (var l in lines) w = Math.Max(w, gr.MeasureString(l, fTab).Width);
                    float x0 = clip.Left + 6, y0 = clip.Top + 6;
                    using (var bg = new SolidBrush(Color.FromArgb(170, 14, 16, 22)))
                        gr.FillRectangle(bg, x0 - 3, y0 - 2, w + 8, lh * lines.Count + 4);
                    for (int i = 0; i < lines.Count; i++)
                    {
                        Color c = i == 0 ? Color.White : (lines[i].StartsWith("⚠") ? Color.FromArgb(255, 150, 120) : Color.FromArgb(200, 205, 215));
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
