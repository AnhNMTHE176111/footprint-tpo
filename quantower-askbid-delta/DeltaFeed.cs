// ============================================================================
//  DeltaFeed — lớp nối SDK Quantower ↔ DeltaCore (đọc nến, nạp tick nền, vẽ)
// ============================================================================
//  Dùng chung cho AskBidDeltaBars (từng nến, mở từ 0) và CumDeltaCandles (cộng dồn).
//  Lõi tính toán + lý do fix nằm ở DeltaCore.cs. File này chỉ chứa phần cần SDK.
//
//  Quy ước chống lỗi "vạch ngang âm thầm":
//    • mọi nến có ghi nguồn đỉnh/đáy (Quantower / Tick / Không có);
//    • màn hình luôn hiện 1 dòng trạng thái đếm số nến theo từng nguồn + tiến độ nạp tick;
//    • nến không có râu vẽ VIỀN RỖNG chứ không giả làm nến thật.
// ============================================================================
namespace AskBidDeltaFeed
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Threading;
    using System.Threading.Tasks;
    using AskBidDeltaCore;
    using TradingPlatform.BusinessLayer;

    /// <summary>Nạp tick lịch sử ở luồng nền, dựng delta chạy từng nến, KHÔNG chặn giao diện.</summary>
    public sealed class TickRangeLoader
    {
        private readonly object _lk = new object();
        private Dictionary<long, TickBar> _res = new Dictionary<long, TickBar>();
        private CancellationTokenSource _cts;
        public volatile string Status = "";
        public volatile bool Running;
        public int Version;

        public Dictionary<long, TickBar> Snapshot() { lock (_lk) return new Dictionary<long, TickBar>(_res); }

        public void Cancel()
        {
            try { _cts?.Cancel(); } catch { }
            lock (_lk) _res = new Dictionary<long, TickBar>();
            Running = false;
        }

        /// <param name="starts">thời điểm bắt đầu (UTC ticks) từng nến, tăng dần</param>
        /// <param name="need">nến nào cần dựng từ tick</param>
        public void Start(Symbol sym, long[] starts, bool[] need, int chunkHours, Action onProgress)
        {
            Cancel();
            var cts = new CancellationTokenSource(); _cts = cts;
            var tok = cts.Token;
            Running = true; Status = "đang nạp tick…";
            Task.Run(() =>
            {
                try { Run(sym, starts, need, Math.Max(1, chunkHours), onProgress, tok); }
                catch (Exception ex) { Status = "LỖI nạp tick: " + ex.Message; }
                finally { if (!tok.IsCancellationRequested) Running = false; }
            });
        }

        private void Run(Symbol sym, long[] starts, bool[] need, int chunkHours, Action onProgress, CancellationToken tok)
        {
            int first = -1, last = -1;
            for (int i = 0; i < need.Length; i++) if (need[i]) { if (first < 0) first = i; last = i; }
            if (first < 0) { Status = "không có nến nào cần dựng từ tick"; return; }

            long chunk = chunkHours * TimeSpan.TicksPerHour;
            long w0 = starts[first] - starts[first] % TimeSpan.TicksPerHour;
            long endAll = last + 1 < starts.Length ? starts[last + 1] : starts[last] + TimeSpan.TicksPerHour;
            var acc = new TickAccumulator(starts);
            long totalTicks = 0; int windows = 0, emptyWindows = 0, doneWindows = 0;
            int bi = first;                                   // trỏ nến cần đầu tiên chưa phủ
            for (long a = w0; a < endAll; a += chunk) windows++;
            for (long a = w0; a < endAll && !tok.IsCancellationRequested; a += chunk)
            {
                long b = a + chunk;
                // bỏ cửa sổ không chứa nến cần nào
                bool any = false;
                while (bi < need.Length && starts[bi] < a) bi++;
                for (int k = bi; k < need.Length && starts[k] < b; k++) if (need[k]) { any = true; break; }
                if (!any) { doneWindows++; continue; }

                HistoricalData hd = null; long got = 0;
                try
                {
                    hd = sym.GetTickHistory(HistoryType.Last, new DateTime(a, DateTimeKind.Utc), new DateTime(b, DateTimeKind.Utc));
                    int n = hd?.Count ?? 0;
                    for (int i = 0; i < n && !tok.IsCancellationRequested; i++)
                    {
                        if (hd[i, SeekOriginHistory.Begin] is not HistoryItemLast t) continue;
                        long tt = t.TimeLeft.Ticks;
                        if (tt < a || tt >= b) continue;             // chống trùng tick ở biên cửa sổ
                        int sign = t.AggressorFlag == AggressorFlag.Buy ? 1 : t.AggressorFlag == AggressorFlag.Sell ? -1 : 0;
                        acc.Feed(tt, t.Volume, sign);
                        got++;
                    }
                }
                finally { try { hd?.Dispose(); } catch { } }
                acc.Flush();
                totalTicks += got; doneWindows++;
                if (got == 0) emptyWindows++;
                lock (_lk) { foreach (var kv in acc.Result) _res[kv.Key] = kv.Value; }
                Interlocked.Increment(ref Version);
                Status = $"nạp tick {doneWindows}/{windows} đợt · {totalTicks:N0} tick" + (emptyWindows > 0 ? $" · {emptyWindows} đợt RỖNG" : "");
                try { onProgress?.Invoke(); } catch { }
            }
            if (tok.IsCancellationRequested) return;
            string tail = acc.Unclassified > 0 ? $" · {acc.Unclassified:N0} tick không rõ bên chủ động" : "";
            if (acc.OutOfOrder > 0) tail += $" · {acc.OutOfOrder:N0} tick lệch thứ tự";
            Status = totalTicks == 0
                ? "nhà cung cấp KHÔNG trả tick lịch sử cho khoảng này (nến cũ không có râu)"
                : $"xong · {totalTicks:N0} tick{tail}" + (emptyWindows > 0 ? $" · {emptyWindows}/{windows} đợt RỖNG" : "");
            try { onProgress?.Invoke(); } catch { }
        }
    }

    /// <summary>Đọc nến → dựng chuỗi nến delta; quản lý việc nạp tick; thống kê nguồn.</summary>
    public sealed class DeltaFeed
    {
        public bool PerBar;                 // true = mỗi nến mở từ 0
        public bool ResetDaily = true;
        public int TzHours = 7, ResetMinutes = 300, MaxTickDays = 5, ChunkHours = 2;
        public bool UseTicks = true;

        private readonly object _lk = new object();
        private readonly TickRangeLoader _loader = new TickRangeLoader();
        private RawBar[] _raw = new RawBar[0];
        private CumBar[] _chain = new CumBar[0];
        private int _loadedVer = -1, _count = -1;
        private string _loadKey = "";
        private volatile bool _dirty = true;
        public int NQt, NTick, NNone, NNoVa;

        public CumBar[] Chain { get { lock (_lk) return _chain; } }
        public bool TicksChanged => _loader.Version != _loadedVer;
        public void MarkDirty() { _dirty = true; }
        public void Cancel() { _loader.Cancel(); lock (_lk) { _raw = new RawBar[0]; _chain = new CumBar[0]; _count = -1; _loadKey = ""; } }
        public void ForceReload() { _loadKey = ""; _dirty = true; }

        public string StatusLine()
        {
            string s = $"Nến có râu: Quantower {NQt} · dựng từ tick {NTick} · KHÔNG có râu {NNone}" + (NNoVa > 0 ? $" · chưa có VA {NNoVa}" : "");
            if (UseTicks) s += " | tick: " + (string.IsNullOrEmpty(_loader.Status) ? "chưa cần" : _loader.Status);
            return s;
        }

        private static RawBar ReadBar(HistoricalData hd, int i)
        {
            var r = new RawBar();
            if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar bar) return r;
            r.TimeUtcTicks = bar.TimeLeft.Ticks;
            var t = bar.VolumeAnalysisData?.Total;
            if (t == null) return r;
            r.HasVa = true; r.Volume = t.Volume; r.Trades = t.Trades;
            r.Delta = t.Delta; r.QtMax = t.MaxDelta; r.QtMin = t.MinDelta;
            return r;
        }

        /// <summary>Gọi mỗi OnUpdate (và khi VA nạp xong). Trả true nếu chuỗi nến đã đổi cần đặt lại thang.</summary>
        public bool Update(HistoricalData hd, Symbol sym, Action onProgress, bool forceFull)
        {
            if (hd == null) return false;
            int n = hd.Count;
            bool full = forceFull || _dirty || n != _count && Math.Abs(n - _count) > 1 || _raw.Length != n;
            int ver = _loader.Version;
            bool verChanged = ver != _loadedVer;
            if (!full)
            {
                // nến đang chạy + 2 nến trước: số liệu còn đổi (tick nạp thêm chỉ đổi chuỗi dựng, không cần đọc lại cả lịch sử)
                for (int i = Math.Max(0, n - 3); i < n; i++) _raw[i] = ReadBar(hd, i);
            }
            else
            {
                var raw = new RawBar[n];
                for (int i = 0; i < n; i++) raw[i] = ReadBar(hd, i);
                lock (_lk) _raw = raw;
                _dirty = false;
            }
            _count = n; _loadedVer = ver;
            var ticks = _loader.Snapshot();
            var chain = DeltaCore.BuildChain(_raw, ticks, PerBar, ResetDaily, TzHours, ResetMinutes);
            lock (_lk) _chain = chain;
            int nq = 0, nt = 0, nn = 0, nv = 0;
            for (int i = 0; i < chain.Length; i++)
            {
                if (chain[i].Empty) { if (!_raw[i].HasVa) nv++; continue; }
                if (chain[i].Src == RangeSrc.Quantower) nq++;
                else if (chain[i].Src == RangeSrc.Ticks) nt++;
                else nn++;
            }
            NQt = nq; NTick = nt; NNone = nn; NNoVa = nv;
            if (full) MaybeStartLoader(sym, onProgress);
            return full || verChanged;
        }

        private void MaybeStartLoader(Symbol sym, Action onProgress)
        {
            if (!UseTicks || sym == null || _raw.Length == 0) return;
            long lastT = _raw[_raw.Length - 1].TimeUtcTicks;
            long minT = lastT - MaxTickDays * TimeSpan.TicksPerDay;
            var starts = new long[_raw.Length]; var need = new bool[_raw.Length];
            int cnt = 0; long firstNeed = 0;
            for (int i = 0; i < _raw.Length; i++)
            {
                var r = _raw[i];
                starts[i] = r.TimeUtcTicks;
                if (!r.HasVa || r.Volume <= 0 || r.TimeUtcTicks < minT) continue;
                if (DeltaCore.QtRangeReal(r.Delta, r.QtMax, r.QtMin, r.Trades)) continue;
                need[i] = true; cnt++; if (cnt == 1) firstNeed = r.TimeUtcTicks;
            }
            if (cnt == 0) { if (!_loader.Running) _loader.Status = "không cần (Quantower đã có râu thật)"; return; }
            string key = cnt + "|" + firstNeed;
            if (key == _loadKey) return;           // cùng tập nến cần → không nạp lại (tránh lặp mỗi nến mới)
            _loadKey = key;
            _loader.Start(sym, starts, need, ChunkHours, onProgress);
        }

        // ---------------------------------------------------------------- vẽ
        public static void Draw(Graphics gr, RectangleF clip, CumBar[] chain, int li, int ri, double barsW,
                                Func<DateTime, double> chartX, Func<double, double> chartY,
                                Color up, Color down, double bodyFrac, int wickPx, bool showNumbers)
        {
            float bodyW = (float)Math.Max(1.0, barsW * bodyFrac);
            bool labels = showNumbers && barsW >= 26;
            using var font = new Font("Arial", 8, FontStyle.Regular);
            for (int i = Math.Max(0, li); i <= ri && i < chain.Length; i++)
            {
                var c = chain[i];
                if (c.Empty) continue;
                float cx = (float)(chartX(new DateTime(c.TimeUtcTicks, DateTimeKind.Utc)) + barsW / 2.0);
                float yO = (float)chartY(c.Open), yC = (float)chartY(c.Close);
                float yH = (float)chartY(c.High), yL = (float)chartY(c.Low);
                bool isUp = c.Close >= c.Open;
                Color col = isUp ? up : down;
                float top = Math.Min(yO, yC), bot = Math.Max(yO, yC);
                float h = Math.Max(1f, bot - top);
                if (c.Src == RangeSrc.None)
                {
                    // KHÔNG có đỉnh/đáy thật: viền rỗng, không râu — không giả làm nến đầy đủ
                    using var pen0 = new Pen(col, 1f) { DashStyle = System.Drawing.Drawing2D.DashStyle.Dot };
                    gr.DrawRectangle(pen0, cx - bodyW / 2f, top, bodyW, h);
                }
                else
                {
                    using var pen = new Pen(col, Math.Max(1, wickPx));
                    using var br = new SolidBrush(col);
                    gr.DrawLine(pen, cx, yH, cx, yL);
                    gr.FillRectangle(br, cx - bodyW / 2f, top, bodyW, h);
                }
                if (labels)
                {
                    using var tb = new SolidBrush(col);
                    string txt = ((long)Math.Round(c.Delta)).ToString();
                    var sz = gr.MeasureString(txt, font);
                    float ty = isUp ? Math.Min(yH, top) - sz.Height - 1 : Math.Max(yL, bot) + 1;
                    gr.DrawString(txt, font, tb, cx - sz.Width / 2f, ty);
                }
            }
        }

        public void DrawStatus(Graphics gr, RectangleF clip)
        {
            using var f = new Font("Arial", 8, FontStyle.Regular);
            string s = StatusLine();
            var sz = gr.MeasureString(s, f);
            using var bg = new SolidBrush(Color.FromArgb(150, 255, 255, 255));
            gr.FillRectangle(bg, clip.Left + 4, clip.Top + 3, sz.Width + 4, sz.Height + 2);
            using var br = new SolidBrush(NNone > 0 || NNoVa > 0 ? Color.FromArgb(0xB0, 0x30, 0x00) : Color.FromArgb(0x30, 0x30, 0x30));
            gr.DrawString(s, f, br, clip.Left + 6, clip.Top + 4);
        }
    }
}
