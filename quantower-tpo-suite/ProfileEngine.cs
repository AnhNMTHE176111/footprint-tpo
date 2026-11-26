// ============================================================================
//  ProfileEngine  —  lõi dùng chung cho DailyTpoBias + M30SessionZones (Quantower)
// ============================================================================
//  Thuần logic (không phụ thuộc Indicator/GDI). Dựng profile phiên từ footprint
//  (VolumeAnalysisData.PriceLevels) hoặc TPO (High/Low nến), tính POC/VA (rule 2
//  hàng 70%), IB, và các vùng (naked POC, cụm POC, biên VA, HVN — xem FindHvn).
//
//  ĐƯỢC CONCAT vào đầu mỗi file indicator khi build (xem build-tpo.sh). Vì vậy
//  MỌI `using` đặt BÊN TRONG namespace (không có using top-level) để nối file hợp lệ.
//  Đã validate offline: POC khớp đáp án nền tảng 90% trong 5 tick (prototype_test.py).
// ============================================================================
namespace TpoSuite
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.IO;
    using System.Linq;
    using System.Net.Http;
    using System.Text;
    using System.Threading.Tasks;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;
    using TradingPlatform.BusinessLayer.Native;

    // ---- Kéo-thả bảng bằng chuột (dùng chung cho 2 indicator) ----------------
    //  Bắt sự kiện chuột của chart (CurrentChart.MouseDown/Move/Up). Khi bấm trái
    //  vào trong vùng bảng → kéo theo chuột. Lưu vị trí bằng offset px; nếu chưa
    //  kéo bao giờ thì dùng vị trí góc mặc định. Chỉ UI thread đụng tới lớp này.
    internal sealed class PanelDrag
    {
        private readonly object _lk = new object();
        private IChart _chart;
        private bool _dragging;
        private float _grabDX, _grabDY;
        private float _bx, _by, _bw, _bh;   // vùng bảng lần vẽ gần nhất (hit-test)
        private float? _x, _y;              // vị trí người dùng đã kéo (null = mặc định)
        private bool _collapsed;            // đang thu gọn (chỉ hiện tiêu đề)

        public const float ToggleSize = 15f;   // cạnh nút thu gọn/mở rộng (px)
        public bool Collapsed { get { lock (_lk) return _collapsed; } }

        // Vùng nút thu gọn ở góc trên-phải của bảng — DÙNG CHUNG cho cả vẽ ↔ bắt chuột
        // (một nguồn sự thật để glyph và hit-test luôn khớp nhau).
        public static RectangleF ToggleBox(float x, float y, float bw)
            => new RectangleF(x + bw - ToggleSize - 3f, y + 3f, ToggleSize, ToggleSize);

        public void Attach(IChart chart)
        {
            if (chart == null || ReferenceEquals(_chart, chart)) return;
            Detach();
            _chart = chart;
            _chart.MouseDown += OnDown;
            _chart.MouseMove += OnMove;
            _chart.MouseUp += OnUp;
        }

        public void Detach()
        {
            if (_chart == null) return;
            try { _chart.MouseDown -= OnDown; _chart.MouseMove -= OnMove; _chart.MouseUp -= OnUp; } catch { }
            _chart = null; _dragging = false;
        }

        // Vị trí gốc bảng để vẽ: nếu đã kéo dùng vị trí đó, chưa thì dùng defX/defY;
        // luôn kẹp trong vùng chart để bảng không biến mất khỏi màn hình.
        public (float x, float y) Origin(float defX, float defY, float bw, float bh, Rectangle clip)
        {
            lock (_lk)
            {
                float x = _x ?? defX, y = _y ?? defY;
                x = Math.Max(clip.Left, Math.Min(x, clip.Right - bw));
                y = Math.Max(clip.Top, Math.Min(y, clip.Bottom - bh));
                return (x, y);
            }
        }

        // Gọi CUỐI OnPaintChart sau khi biết vị trí + kích thước bảng thực vẽ.
        public void SetBounds(float x, float y, float bw, float bh)
        { lock (_lk) { _bx = x; _by = y; _bw = bw; _bh = bh; } }

        private void OnDown(object s, ChartMouseNativeEventArgs e)
        {
            if (e.Button != NativeMouseButtons.Left) return;
            bool toggled = false;
            lock (_lk)
            {
                if (!(e.X >= _bx && e.X <= _bx + _bw && e.Y >= _by && e.Y <= _by + _bh)) return;
                // Bấm vào nút góc trên-phải → thu gọn/mở rộng (KHÔNG bắt đầu kéo).
                var tr = ToggleBox(_bx, _by, _bw);
                if (e.X >= tr.X && e.X <= tr.Right && e.Y >= tr.Y && e.Y <= tr.Bottom)
                {
                    _collapsed = !_collapsed; toggled = true;
                }
                else { _dragging = true; _grabDX = e.X - _bx; _grabDY = e.Y - _by; }
            }
            e.Handled = true;
            if (toggled) e.NeedRedraw = true; else e.NeedMouseCapture = true;
        }

        // Vẽ nút thu gọn/mở rộng: ▸ khi đang thu gọn (bấm để mở), ▾ khi đang mở (bấm để thu).
        public static void DrawToggle(Graphics gr, float x, float y, float bw, bool collapsed)
        {
            var r = ToggleBox(x, y, bw);
            using (var b = new SolidBrush(Color.FromArgb(55, 255, 255, 255))) gr.FillRectangle(b, r.X, r.Y, r.Width, r.Height);
            using (var bd = new Pen(Color.FromArgb(120, 255, 255, 255), 1f)) gr.DrawRectangle(bd, r.X, r.Y, r.Width, r.Height);
            float cx = r.X + r.Width / 2f, cy = r.Y + r.Height / 2f;
            using var pen = new Pen(Color.FromArgb(220, 255, 255, 255), 1.6f);
            if (collapsed)
                gr.DrawLines(pen, new[] { new PointF(cx - 2.5f, cy - 4f), new PointF(cx + 3f, cy), new PointF(cx - 2.5f, cy + 4f) }); // ▸
            else
                gr.DrawLines(pen, new[] { new PointF(cx - 4f, cy - 2.5f), new PointF(cx, cy + 3f), new PointF(cx + 4f, cy - 2.5f) }); // ▾
        }

        // Vẽ TRỌN bảng (nền + viền + chữ + nút thu gọn) rồi lưu hit-test. Khi thu gọn
        // chỉ vẽ dòng đầu (tiêu đề). Dùng chung cho cả 3 indicator để logic thu gọn ở 1 chỗ.
        public void Draw(Graphics gr, Font f, IReadOnlyList<(string text, Color col)> lines,
                         int bgAlpha, int corner, Rectangle clip)
        {
            if (lines == null || lines.Count == 0) return;
            bool col = Collapsed;
            int nShow = col ? 1 : lines.Count;
            float pad = 6f, lineH = f.Height + 2f, w = 0f;
            for (int k = 0; k < nShow; k++) w = Math.Max(w, gr.MeasureString(lines[k].text, f).Width);
            float bw = w + 2f * pad + ToggleSize + 6f;   // chừa chỗ nút thu gọn góc phải
            float bh = nShow * lineH + 2f * pad;
            float defX = (corner == 1 || corner == 3) ? clip.Right - bw - 8f : clip.Left + 8f;
            float defY = (corner >= 2) ? clip.Bottom - bh - 8f : clip.Top + 8f;
            var (x, y) = Origin(defX, defY, bw, bh, clip);
            using (var bg = new SolidBrush(Color.FromArgb(bgAlpha, 18, 18, 22))) gr.FillRectangle(bg, x, y, bw, bh);
            using (var bd = new Pen(Color.FromArgb(90, 255, 255, 255))) gr.DrawRectangle(bd, x, y, bw, bh);
            float ty = y + pad;
            for (int k = 0; k < nShow; k++) { using var br = new SolidBrush(lines[k].col); gr.DrawString(lines[k].text, f, br, x + pad, ty); ty += lineH; }
            DrawToggle(gr, x, y, bw, col);
            SetBounds(x, y, bw, bh);
        }

        private void OnMove(object s, ChartMouseNativeEventArgs e)
        {
            lock (_lk)
            {
                if (!_dragging) return;
                _x = e.X - _grabDX; _y = e.Y - _grabDY;
            }
            e.Handled = true; e.NeedRedraw = true;
        }

        private void OnUp(object s, ChartMouseNativeEventArgs e)
        {
            lock (_lk) { if (!_dragging) return; _dragging = false; }
            e.Handled = true; e.NeedRedraw = true;
        }
    }

    // ---- Kết quả profile 1 phiên (ngày, hoặc khối Á/Âu/Mỹ, hoặc 1 profile 30') ----
    internal sealed class SessionProfile
    {
        public string Label = "";
        public DateTime Start, End;
        public int FromIdx = -1, ToIdx = -1;
        public int Bars;
        public double Tick = 0.1;
        public double Open, Close;
        public double High = double.MinValue, Low = double.MaxValue;
        public double Poc = double.NaN, Vah = double.NaN, Val = double.NaN, Mid = double.NaN;
        public double IbHigh = double.NaN, IbLow = double.NaN;
        public double Volume, Delta;

        public bool Valid => High > Low && !double.IsNaN(Poc);
        public double RangeTicks => (High > Low) ? (High - Low) / Tick : 0;
        public double VaWidthTicks => (!double.IsNaN(Vah) && !double.IsNaN(Val)) ? (Vah - Val) / Tick : 0;
        public double IbRangeTicks => (!double.IsNaN(IbHigh) && !double.IsNaN(IbLow)) ? (IbHigh - IbLow) / Tick : 0;
        public double ClosePos => (High > Low) ? (Close - Low) / (High - Low) : 0.5;
        public int Direction => Close > Open ? 1 : Close < Open ? -1 : 0;
        // balance: ROT (>=0.55) / TREND (<=0.35) / INT theo VAwidth/Range
        public string Balance
        {
            get { double r = RangeTicks > 0 ? VaWidthTicks / RangeTicks : 1;
                  return r >= 0.55 ? "ROT" : r <= 0.35 ? "TREND" : "INT"; }
        }
        public string CloseState => ClosePos >= 0.70 ? "MẠNH" : ClosePos <= 0.30 ? "YẾU" : "TB";
    }

    internal static class ProfileEngine
    {
        public static double Snap(double price, double step) => Math.Round(price / step) * step;

        // Volume rows (giá->volume) từ PriceLevels trên [from..to], snap về rowStep.
        public static SortedDictionary<double, double> VolumeRows(HistoricalData hd, int from, int to, double rowStep)
        {
            var rows = new SortedDictionary<double, double>();
            for (int i = from; i <= to; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                var pl = b.VolumeAnalysisData?.PriceLevels;
                if (pl == null) continue;
                foreach (var kv in pl)
                {
                    double p = Snap(kv.Key, rowStep);
                    double v = kv.Value.Volume;
                    rows[p] = rows.TryGetValue(p, out var c) ? c + v : v;
                }
            }
            return rows;
        }

        // ATR đơn giản (trung bình High-Low, không EMA) của n nến kết thúc tại idx.
        // Dùng để co giãn bán kính lọc vùng / dung sai gộp theo biến động hiện tại —
        // KHÔNG dùng hằng số tick cứng vì range vàng khác nhau rất nhiều theo giai đoạn
        // (đối chiếu prototype: tháng 6 crash biến động gấp nhiều lần tháng 7 êm).
        public static double Atr(HistoricalData hd, int idx, int n = 20)
        {
            int from = Math.Max(0, idx - n + 1);
            double sum = 0; int cnt = 0;
            for (int i = from; i <= idx; i++)
                if (hd[i, SeekOriginHistory.Begin] is HistoryItemBar b) { sum += b.High - b.Low; cnt++; }
            return cnt > 0 ? sum / cnt : 0;
        }

        // TPO rows (giá->số nến phủ) từ High/Low trên [from..to].
        public static SortedDictionary<double, double> TpoRows(HistoricalData hd, int from, int to, double rowStep)
        {
            var rows = new SortedDictionary<double, double>();
            for (int i = from; i <= to; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                long a = (long)Math.Round(b.Low / rowStep), z = (long)Math.Round(b.High / rowStep);
                for (long r = a; r <= z; r++)
                {
                    double p = r * rowStep;
                    rows[p] = rows.TryGetValue(p, out var c) ? c + 1 : 1;
                }
            }
            return rows;
        }

        // POC + Value Area (rule 2 hàng, 70%).
        public static (double poc, double vah, double val) ValueArea(SortedDictionary<double, double> rows, double frac = 0.70)
        {
            if (rows == null || rows.Count == 0) return (double.NaN, double.NaN, double.NaN);
            var prices = rows.Keys.ToArray();
            var w = rows.Values.ToArray();
            double tot = 0; for (int i = 0; i < w.Length; i++) tot += w[i];
            if (tot <= 0) return (double.NaN, double.NaN, double.NaN);
            int poc = 0; for (int i = 1; i < w.Length; i++) if (w[i] > w[poc]) poc = i;
            double acc = w[poc], target = tot * frac; int lo = poc, hi = poc;
            while (acc < target && (lo > 0 || hi < w.Length - 1))
            {
                double up = (hi < w.Length - 1 ? w[hi + 1] : 0) + (hi < w.Length - 2 ? w[hi + 2] : 0);
                double dn = (lo > 0 ? w[lo - 1] : 0) + (lo > 1 ? w[lo - 2] : 0);
                if (hi >= w.Length - 1) { acc += dn; lo = Math.Max(0, lo - 2); }
                else if (lo <= 0) { acc += up; hi = Math.Min(w.Length - 1, hi + 2); }
                else if (up >= dn) { acc += up; hi = Math.Min(w.Length - 1, hi + 2); }
                else { acc += dn; lo = Math.Max(0, lo - 2); }
            }
            return (prices[poc], prices[hi], prices[lo]);
        }

        // Dựng 1 SessionProfile từ nến [from..to]. useVolume=true → volume rows (fallback TPO nếu rỗng).
        public static SessionProfile BuildProfile(HistoricalData hd, int from, int to, double tick,
                                                  double rowStep, bool useVolume, int ibBars, string label)
        {
            var sp = new SessionProfile { Label = label, FromIdx = from, ToIdx = to, Tick = tick };
            if (from < 0 || to < from) return sp;
            for (int i = from; i <= to; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                if (i == from) { sp.Open = b.Open; sp.Start = b.TimeLeft; }
                sp.High = Math.Max(sp.High, b.High);
                sp.Low = Math.Min(sp.Low, b.Low);
                sp.Close = b.Close; sp.End = b.TimeLeft; sp.Bars++;
                var t = b.VolumeAnalysisData?.Total;
                if (t != null) { sp.Volume += t.Volume; sp.Delta += t.Delta; }
            }
            var rows = useVolume ? VolumeRows(hd, from, to, rowStep) : null;
            if (rows == null || rows.Count == 0) rows = TpoRows(hd, from, to, rowStep);
            var (poc, vah, val) = ValueArea(rows);
            sp.Poc = poc; sp.Vah = vah; sp.Val = val;
            if (sp.High > sp.Low) sp.Mid = (sp.High + sp.Low) / 2;
            if (ibBars > 0)
            {
                double ih = double.MinValue, il = double.MaxValue; int cnt = 0;
                for (int k = 0; k < ibBars && from + k <= to; k++)
                    if (hd[from + k, SeekOriginHistory.Begin] is HistoryItemBar bb)
                    { ih = Math.Max(ih, bb.High); il = Math.Min(il, bb.Low); cnt++; }
                if (cnt > 0) { sp.IbHigh = ih; sp.IbLow = il; }
            }
            return sp;
        }

        // Nhóm toàn bộ nến thành các phiên theo GAP thời gian (không cần timezone).
        // gapMinutes: gap giữa 2 nến liên tiếp lớn hơn ngưỡng → phiên mới (nghỉ bảo trì/cuối tuần).
        public static List<(int from, int to)> GroupByGap(HistoricalData hd, double gapMinutes)
        {
            var res = new List<(int, int)>();
            int n = hd.Count; if (n == 0) return res;
            int start = 0; DateTime prev = DateTime.MinValue; bool have = false;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                if (have && (b.TimeLeft - prev).TotalMinutes > gapMinutes)
                { res.Add((start, i - 1)); start = i; }
                prev = b.TimeLeft; have = true;
            }
            res.Add((start, n - 1));
            return res;
        }

        // ---- thống kê ----
        public static double Median(List<double> xs)
        {
            if (xs == null || xs.Count == 0) return 0;
            var s = xs.ToList(); s.Sort(); int m = s.Count / 2;
            return (s.Count % 2 == 1) ? s[m] : 0.5 * (s[m - 1] + s[m]);
        }
        public static double Percentile(List<double> xs, double p)
        {
            if (xs == null || xs.Count == 0) return 0;
            var s = xs.ToList(); s.Sort();
            double idx = Math.Clamp(p, 0, 1) * (s.Count - 1);
            int lo = (int)Math.Floor(idx), hi = (int)Math.Ceiling(idx);
            if (lo == hi) return s[lo];
            return s[lo] + (idx - lo) * (s[hi] - s[lo]);
        }
        public static double Clamp(double x, double a, double b) => Math.Max(a, Math.Min(b, x));

        // Phân loại quan hệ vùng giá trị d(hôm nay/dev) vs p(hôm qua). Trả (nhãn, điểm[-1..1]).
        public static (string label, double s) ValueRelation(double dVah, double dVal, double dClose,
                                                             double pVah, double pVal, double pPoc, double gapDollars)
        {
            if (dVal > pVah + gapDollars) return ("vùng giá trị cao hơn", +1.0);
            if (dVah < pVal - gapDollars) return ("vùng giá trị thấp hơn", -1.0);
            if (dVah > pVah && dVal > pVal) return ("chồng lên cao hơn", +0.5);
            if (dVah < pVah && dVal < pVal) return ("chồng lên thấp hơn", -0.5);
            if (dVah <= pVah && dVal >= pVal) return ("nằm trong giá trị cũ", 0.0);
            return ("bao trùm giá trị cũ", 0.15 * (dClose > pPoc ? 1 : -1));
        }

        // Naked/virgin POC: POC của phiên đã đóng, chưa nến nào SAU khi phiên đó kết thúc phủ lại.
        public static bool IsNaked(HistoricalData hd, SessionProfile sp, int lastIdx)
        {
            for (int i = sp.ToIdx + 1; i <= lastIdx; i++)
                if (hd[i, SeekOriginHistory.Begin] is HistoryItemBar b && b.Low <= sp.Poc && sp.Poc <= b.High)
                    return false;
            return true;
        }

        // Gom các POC gần nhau (<= tolTicks) thành cụm; trả (lo,hi,count) cho cụm có >=minCount.
        public static List<(double lo, double hi, int n)> ClusterPocs(List<double> pocs, double tolTicks, double tick, int minCount)
        {
            var res = new List<(double, double, int)>();
            if (pocs == null || pocs.Count == 0) return res;
            var s = pocs.Where(x => !double.IsNaN(x)).ToList(); s.Sort();
            if (s.Count == 0) return res;
            var cur = new List<double> { s[0] };
            void flush() { if (cur.Count >= minCount) res.Add((cur[0], cur[cur.Count - 1], cur.Count)); }
            for (int i = 1; i < s.Count; i++)
            {
                if ((s[i] - cur[cur.Count - 1]) / tick <= tolTicks) cur.Add(s[i]);
                else { flush(); cur = new List<double> { s[i] }; }
            }
            flush();
            return res;
        }

        // Hàng giá gộp trên [from..to] — dùng cho profile nhiều phiên (tuần/ngày).
        // Ưu tiên volume thật (footprint); rỗng thì rơi về TPO (đếm nến phủ).
        public static SortedDictionary<double, double> RowsOver(
            HistoricalData hd, int from, int to, double rowStep, bool useVolume)
        {
            var rows = useVolume ? VolumeRows(hd, from, to, rowStep) : null;
            if (rows == null || rows.Count == 0) rows = TpoRows(hd, from, to, rowStep);
            return rows;
        }

        // Ranh giới TUẦN trong hd (M30 hoặc khung khác): khoảng trống > gapHours giữa 2
        // nến liên tiếp (cuối tuần CME đóng T6 tối -> mở lại CN tối, ~46h). Span cuối =
        // tuần ĐANG CHẠY; span áp chót = tuần ĐÃ ĐÓNG gần nhất. Dùng chung cho SessionZones
        // (nguồn HVN tuần) và DailyTpoBias (neo VWAP tuần) — xem CAU_HOI_CAN_THONG_NHAT.md §A1.
        public static List<(int fr, int to)> WeekSpans(HistoricalData hd, double gapHours)
        {
            var spans = new List<(int fr, int to)>();
            int n = hd.Count, fr = 0; DateTime prev = DateTime.MinValue; bool have = false;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                if (have && (b.TimeLeft - prev).TotalHours > gapHours) { spans.Add((fr, i - 1)); fr = i; }
                prev = b.TimeLeft; have = true;
            }
            if (have) spans.Add((fr, n - 1));
            return spans;
        }

        // ---- Chỗ NỐI HỢP ĐỒNG của mã liên tục (B10) --------------------------
        //  Mã liên tục (/GC:XCEC, GC1!, GC=F…) khi hợp đồng cũ hết vòng đời thì NHẢY
        //  sang hợp đồng mới mà KHÔNG bù chênh lệch giá. Đo trên 2 năm GC (529 phiên,
        //  ~143k hợp đồng/phiên): 8 chỗ nối, bước nhảy tới +61,2 giá, và LUÔN rơi
        //  đúng vào GIỜ NGHỈ 1 TIẾNG của sàn — trong khi bước nhảy bình thường tại
        //  giờ nghỉ đó có trung vị 0,7 giá, phân vị 90 là 8,4 giá.
        //  Vì sao phải chặn: profile gộp nhiều phiên mà vắt qua chỗ nối thì dựng trên
        //  HAI thang giá cách nhau ~60 giá ⇒ HVN sinh ra từ đó vô nghĩa. Vàng đổi hợp
        //  đồng ~2 tháng/lần nên chuyện này lặp lại đều đặn.
        //  Chỉ xét khoảng nghỉ trong [minGapMin, maxGapMin] để LOẠI nghỉ cuối tuần
        //  (~46h): khoảng trống cuối tuần thật có thể tới 41,8 giá, to gần bằng chỗ
        //  nối, nên gộp chung sẽ cắt nhầm tuần lành.
        //  Trả CHỈ SỐ nến đầu tiên NGAY SAU chỗ nối gần nhất trong [from..to]; -1 = sạch.
        public static int LastSpliceIndex(
            IList<DateTime> times, IList<double> opens, IList<double> closes,
            int from, int to, double minJump, double minGapMin = 30, double maxGapMin = 150)
        {
            if (times == null || opens == null || closes == null) return -1;
            int n = Math.Min(times.Count, Math.Min(opens.Count, closes.Count));
            if (n == 0 || minJump <= 0) return -1;
            int lo = Math.Max(1, from), hi = Math.Min(to, n - 1);
            int res = -1;
            for (int i = lo; i <= hi; i++)
            {
                double gap = (times[i] - times[i - 1]).TotalMinutes;
                if (gap < minGapMin || gap > maxGapMin) continue;
                if (Math.Abs(opens[i] - closes[i - 1]) >= minJump) res = i;
            }
            return res;
        }

        // Bản dùng thẳng trên HistoricalData của Quantower.
        public static int LastSpliceIndex(HistoricalData hd, int from, int to, double minJump,
                                          double minGapMin = 30, double maxGapMin = 150)
        {
            if (hd == null || minJump <= 0) return -1;
            int lo = Math.Max(1, from), hi = Math.Min(to, hd.Count - 1);
            int res = -1;
            for (int i = lo; i <= hi; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                if (hd[i - 1, SeekOriginHistory.Begin] is not HistoryItemBar a) continue;
                double gap = (b.TimeLeft - a.TimeLeft).TotalMinutes;
                if (gap < minGapMin || gap > maxGapMin) continue;
                if (Math.Abs(b.Open - a.Close) >= minJump) res = i;
            }
            return res;
        }

        // VWAP neo từ nến `from`, cộng dồn tới nến `to`, trả giá trị TẠI `to` (giống
        // vwap_series trong zones_corven.py, đã kiểm chứng offline — §2). Dùng typical
        // price (H+L+C)/3 × volume; fallback = Close nếu chưa có volume.
        public static double VwapAt(HistoricalData hd, int from, int to)
        {
            if (from < 0 || to < from) return double.NaN;
            double sumPv = 0, sumV = 0, lastClose = double.NaN;
            for (int i = from; i <= to; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                double v = b.VolumeAnalysisData?.Total?.Volume ?? 0;
                double tp = (b.High + b.Low + b.Close) / 3.0;
                sumPv += tp * v; sumV += v;
                lastClose = b.Close;
            }
            return sumV > 0 ? sumPv / sumV : lastClose;
        }

        // ---- Độ nhọn của một đỉnh khối lượng — PLAN-MOC-PHAN-UNG.md §A3/B4 ----
        //  Nới từ đỉnh ra 2 bên, LIÊN TỤC (dừng ngay khi gặp mức dưới ngưỡng —
        //  không nhảy qua khe trống), tới khi khối lượng tụt dưới frac*đỉnh.
        //  Trả (lo, hi) bằng GIÁ THẬT (không phải tick) — dùng để:
        //   (a) B3: Lo/Hi thật cho lớp NỀN (HVN tuần/LVN — đây là chỗ DUY NHẤT
        //       cần vùng thật, khác lớp MỐC vẫn giữ Lo=Hi=đỉnh);
        //   (b) B4: đo "nền rộng bao nhiêu giá" để quyết định có cho làm mốc
        //       (mỏng) hay phải hạ xuống lớp nền (bẹt).
        //  Đối chiếu Python: measure_levels.py::sharpness_width (cùng công thức).
        //  `rows` khoá theo rowStep (KHÔNG PHẢI tick — xem RowsOver/rowStep trong
        //  SessionZones), nên bước nới cũng phải đi theo rowStep.
        public static (double lo, double hi) PeakSharpness(
            SortedDictionary<double, double> rows, double peakPrice, double rowStep, double frac = 0.90)
        {
            if (rows == null || !rows.ContainsKey(peakPrice)) return (peakPrice, peakPrice);
            double thr = frac * rows[peakPrice];
            double lo = peakPrice, hi = peakPrice;
            while (rows.TryGetValue(Math.Round((lo - rowStep) / rowStep) * rowStep, out var vLo) && vLo >= thr)
                lo -= rowStep;
            while (rows.TryGetValue(Math.Round((hi + rowStep) / rowStep) * rowStep, out var vHi) && vHi >= thr)
                hi += rowStep;
            return (lo, hi);
        }

        // ---- HVN (High Volume Node) — nút khối lượng cao ---------------------
        //  KHÁC POC: POC chỉ có MỘT (đỉnh cao nhất của phân bố). HVN có thể có
        //  NHIỀU — mỗi nơi khối lượng tụ thành "nút". Sách (ebook §HVN, §Setup 2
        //  "Nhiều nút") coi đây là vùng S/R mạnh nhất và dùng khung 30 phút.
        //
        //  Cách tìm: làm mượt phân bố → lấy đỉnh cực bộ → giữ đỉnh đủ cao so với
        //  trung bình → gộp đỉnh quá gần nhau (giữ cái mạnh hơn).
        //  Trả (giá, tỉ lệ so với trung bình), mạnh trước.
        //  Đã đối chiếu bản Python trên dữ liệu thật (hvn_research.py).
        //  minSepTicks<=0 → tự co giãn theo độ rộng profile (xem ghi chú bên dưới).
        public static List<(double price, double ratio)> FindHvn(
            SortedDictionary<double, double> rows, double tick,
            int smoothTicks = 5, double minRatio = 1.5, double minSepTicks = 0)
        {
            var res = new List<(double, double)>();
            if (rows == null || rows.Count < 3) return res;
            var prices = rows.Keys.ToArray();
            var w = rows.Values.ToArray();
            int n = w.Length;
            double avg = w.Average();
            if (avg <= 0) return res;

            // Khoảng cách tối thiểu giữa 2 HVN phải CO GIÃN theo độ rộng profile.
            // Cố định 20 tick thì với profile tuần (range ~700 tick) một nút duy
            // nhất bị tách thành 3 HVN sát nhau (4085/4089/4095) — phí cả 3 khe.
            // Lấy 8% độ rộng, kẹp trong [20, 120] tick.
            if (minSepTicks <= 0)
            {
                double widthTicks = (prices[n - 1] - prices[0]) / tick;
                minSepTicks = Math.Clamp(widthTicks * 0.08, 20, 120);
            }

            // làm mượt bằng cửa sổ ±smoothTicks (khử răng cưa tick lẻ)
            var sm = new double[n];
            for (int i = 0; i < n; i++)
            {
                int a = Math.Max(0, i - smoothTicks), z = Math.Min(n - 1, i + smoothTicks);
                double s = 0; for (int k = a; k <= z; k++) s += w[k];
                sm[i] = s / (z - a + 1);
            }

            var peaks = new List<(double price, double weight, double ratio)>();
            for (int i = 1; i < n - 1; i++)
                if (sm[i] >= sm[i - 1] && sm[i] >= sm[i + 1] && sm[i] >= minRatio * avg)
                    peaks.Add((prices[i], sm[i], sm[i] / avg));

            foreach (var p in peaks.OrderByDescending(x => x.weight))
                if (res.All(k => Math.Abs(p.price - k.Item1) / tick >= minSepTicks))
                    res.Add((p.price, p.ratio));
            return res;
        }

        // ---- LVN (Low Volume Node) — nghịch đảo HVN ---------------------------
        //  Nơi giá XUYÊN QUA NHANH vì không có gì đỡ (ít volume). KHÔNG phải vùng
        //  canh vào lệnh — dùng để (a) biết chỗ không nên kỳ vọng phản ứng,
        //  (b) đặt SL phía sau. Tìm ĐÁY cực bộ, giữ đáy đủ thấp so với trung bình.
        // Vùng LVN quanh một đáy (HVN đã là vùng, LVN cũng phải là vùng): nới liên tục từ đáy
        // sang hai bên cho tới khi khối lượng (đã làm mượt) vượt maxRatio × trung bình. Mỗi
        // bên chặn tối đa nửa khoảng cách tối thiểu giữa hai LVN (8% độ rộng profile, kẹp
        // [20,120] tick) để dải của hai đáy khác nhau không chồng nhau và không lan hết
        // đuôi profile (đuôi vốn luôn mỏng). Đáy không có trong rows → (giá, giá).
        public static (double lo, double hi) TroughBand(
            SortedDictionary<double, double> rows, double tick, double troughPrice,
            int smoothTicks = 5, double maxRatio = 0.5)
        {
            if (rows == null || rows.Count < 3 || !rows.ContainsKey(troughPrice)) return (troughPrice, troughPrice);
            var prices = rows.Keys.ToArray();
            var w = rows.Values.ToArray();
            int n = w.Length;
            double avg = w.Average();
            if (avg <= 0) return (troughPrice, troughPrice);
            var sm = new double[n];
            for (int i = 0; i < n; i++)
            {
                int a = Math.Max(0, i - smoothTicks), z = Math.Min(n - 1, i + smoothTicks);
                double sum = 0; for (int k = a; k <= z; k++) sum += w[k];
                sm[i] = sum / (z - a + 1);
            }
            double halfCap = Math.Clamp((prices[n - 1] - prices[0]) / tick * 0.08, 20, 120) * tick / 2;
            int c = Array.IndexOf(prices, troughPrice);
            int lo = c, hi = c;
            while (lo > 0 && sm[lo - 1] <= maxRatio * avg && troughPrice - prices[lo - 1] <= halfCap) lo--;
            while (hi < n - 1 && sm[hi + 1] <= maxRatio * avg && prices[hi + 1] - troughPrice <= halfCap) hi++;
            return (prices[lo], prices[hi]);
        }

        public static List<(double price, double ratio)> FindLvn(
            SortedDictionary<double, double> rows, double tick,
            int smoothTicks = 5, double maxRatio = 0.5, double minSepTicks = 0)
        {
            var res = new List<(double, double)>();
            if (rows == null || rows.Count < 3) return res;
            var prices = rows.Keys.ToArray();
            var w = rows.Values.ToArray();
            int n = w.Length;
            double avg = w.Average();
            if (avg <= 0) return res;
            if (minSepTicks <= 0)
                minSepTicks = Math.Clamp((prices[n - 1] - prices[0]) / tick * 0.08, 20, 120);

            var sm = new double[n];
            for (int i = 0; i < n; i++)
            {
                int a = Math.Max(0, i - smoothTicks), z = Math.Min(n - 1, i + smoothTicks);
                double s = 0; for (int k = a; k <= z; k++) s += w[k];
                sm[i] = s / (z - a + 1);
            }

            var troughs = new List<(double price, double weight, double ratio)>();
            for (int i = 1; i < n - 1; i++)
                if (sm[i] <= sm[i - 1] && sm[i] <= sm[i + 1] && sm[i] <= maxRatio * avg)
                    troughs.Add((prices[i], sm[i], sm[i] / avg));

            foreach (var p in troughs.OrderBy(x => x.weight))     // yếu nhất trước = LVN rõ nhất
                if (res.All(k => Math.Abs(p.price - k.Item1) / tick >= minSepTicks))
                    res.Add((p.price, p.ratio));
            return res;
        }
    }

    // ---- Lịch tin Forex Factory (né tin khi trade vàng) ------------------------------------
    //  Tải feed JSON công khai của Forex Factory (lịch tuần), lọc tin USD (High+Medium) và tin
    //  đỏ EUR/GBP, quy về giờ VN. Tải NỀN + cache ra đĩa (1 giờ) vì feed trả 429 nếu gọi dày;
    //  Compose() chỉ ĐỌC cache nên không bao giờ chặn luồng vẽ chart. Bản Python đối chiếu:
    //  news-calendar/ff_news.py (cùng nguồn, cùng bộ lọc).
    internal static class NewsCalendar
    {
        private const string Url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json";
        private static readonly HttpClient Http = new HttpClient { Timeout = TimeSpan.FromSeconds(20) };
        private static readonly object Gate = new object();
        private static List<Ev> _cache;
        private static DateTime _cacheUtc = DateTime.MinValue;
        private static bool _loading;

        internal sealed class Ev
        {
            public string Title = "", Ccy = "", Impact = "", Forecast = "", Previous = "";
            public DateTime WhenVn;      // giờ Việt Nam
            public DateTime Utc;         // giờ tuyệt đối (từ chuỗi giờ + độ lệch của feed)
            public int OffMin = int.MinValue;   // độ lệch feed ghi kèm (phút so với UTC; giờ New York: −300 mùa đông, −240 mùa hè)
            public bool AllDay;
        }

        // Tin nào cũng "đỏ" nhưng mức nguy hiểm khác nhau → tách riêng nhóm giật mạnh nhất.
        private static readonly string[] TopTier =
        {
            "non-farm", "federal funds", "fomc statement", "core cpi", "cpi m/m", "cpi y/y",
            "fomc press conference", "fed chair"
        };

        // Gọi mỗi vòng Process — trả về ngay, chỉ tải khi cache quá hạn.
        public static void Refresh(string dir, int tzOffset, Action<string> log)
        {
            lock (Gate)
            {
                if (_loading) return;
                // cache còn hạn 60' — trừ khi là lịch TUẦN CŨ (tin cuối cùng đã qua > 12 giờ, vd sáng thứ Hai) thì 10' thử lại
                if (_cache != null && (DateTime.UtcNow - _cacheUtc).TotalMinutes < (CoversNow(_cache, DateTime.UtcNow) ? 60 : 10)) return;
                if (_cache == null && TryLoadDisk(dir, tzOffset)) return;   // khởi động: dùng file cũ trước
                _loading = true;
            }
            Task.Run(async () =>
            {
                try
                {
                    var req = new HttpRequestMessage(HttpMethod.Get, Url);
                    req.Headers.TryAddWithoutValidation("User-Agent", "Mozilla/5.0");
                    var resp = await Http.SendAsync(req).ConfigureAwait(false);
                    string body = await resp.Content.ReadAsStringAsync().ConfigureAwait(false);
                    if (!resp.IsSuccessStatusCode) { log?.Invoke($"lịch tin HTTP {(int)resp.StatusCode} — giữ cache cũ"); return; }
                    var evs = Parse(body, tzOffset);
                    if (evs.Count == 0) { log?.Invoke("lịch tin: feed rỗng — giữ cache cũ"); return; }
                    lock (Gate) { _cache = evs; _cacheUtc = DateTime.UtcNow; }
                    try { File.WriteAllText(Path.Combine(dir, "news_cache.json"), body); } catch { }
                    log?.Invoke($"lịch tin: tải OK, {evs.Count} tin liên quan");
                }
                catch (Exception ex) { log?.Invoke("lịch tin LỖI: " + ex.Message); }
                finally { lock (Gate) { _loading = false; } }
            });
        }

        private static bool TryLoadDisk(string dir, int tzOffset)
        {
            try
            {
                string p = Path.Combine(dir, "news_cache.json");
                if (!File.Exists(p)) return false;
                var evs = Parse(File.ReadAllText(p), tzOffset);
                if (evs.Count == 0) return false;
                _cache = evs;
                _cacheUtc = File.GetLastWriteTimeUtc(p);   // vẫn quá hạn thì vòng sau tự tải mới
                return (DateTime.UtcNow - _cacheUtc).TotalMinutes < 60;
            }
            catch { return false; }
        }

        // Lịch có phải của tuần đang chạy không: tin muộn nhất chưa qua quá 12 giờ.
        public static bool CoversNow(IList<Ev> evs, DateTime nowUtc)
            => evs != null && evs.Count > 0 && evs.Max(e => e.Utc) >= nowUtc.AddHours(-12);

        public static bool Ready(DateTime nowUtc) { lock (Gate) return CoversNow(_cache, nowUtc); }

        // Múi giờ New York (Windows: "Eastern Standard Time", Linux: "America/New_York"); null nếu máy không có.
        public static TimeZoneInfo NewYork()
        {
            foreach (var id in new[] { "Eastern Standard Time", "America/New_York" })
                try { return TimeZoneInfo.FindSystemTimeZoneById(id); } catch { }
            return null;
        }

        // ---- Parser JSON tối giản: feed là mảng object, mọi giá trị đều là chuỗi ----
        public static List<Ev> Parse(string json, int tzOffset)
        {
            var res = new List<Ev>();
            if (string.IsNullOrEmpty(json)) return res;
            int i = 0;
            while (true)
            {
                int s = json.IndexOf('{', i);
                if (s < 0) break;
                int e = json.IndexOf('}', s);
                if (e < 0) break;
                var fields = ReadFields(json.Substring(s + 1, e - s - 1));
                i = e + 1;
                string ccy = Get(fields, "country"), imp = Get(fields, "impact");
                bool keep = (ccy == "USD" && (imp == "High" || imp == "Medium" || imp == "Holiday"))
                         || ((ccy == "EUR" || ccy == "GBP") && imp == "High");
                if (!keep) continue;
                string date = Get(fields, "date");
                var ev = new Ev
                {
                    Title = Get(fields, "title"), Ccy = ccy, Impact = imp,
                    Forecast = Get(fields, "forecast"), Previous = Get(fields, "previous")
                };
                // Feed ghi giờ New York KÈM độ lệch (vd 2026-11-25T08:30:00-05:00) ⇒ đổi sang UTC bằng chính độ lệch đó,
                // không tự cộng trừ giờ mùa hè/đông. Ngày nghỉ (Holiday) coi là cả ngày.
                if (DateTimeOffset.TryParse(date, System.Globalization.CultureInfo.InvariantCulture,
                                            System.Globalization.DateTimeStyles.None, out var dto))
                {
                    ev.Utc = dto.UtcDateTime; ev.OffMin = (int)Math.Round(dto.Offset.TotalMinutes);
                    ev.WhenVn = ev.Utc.AddHours(tzOffset); ev.AllDay = imp == "Holiday";
                }
                else continue;
                res.Add(ev);
            }
            res.Sort((a, b) => a.WhenVn.CompareTo(b.WhenVn));
            return res;
        }

        private static Dictionary<string, string> ReadFields(string obj)
        {
            var d = new Dictionary<string, string>();
            int i = 0;
            while (i < obj.Length)
            {
                string k = NextString(obj, ref i); if (k == null) break;
                int c = obj.IndexOf(':', i); if (c < 0) break;
                i = c + 1;
                string v = NextString(obj, ref i);
                d[k] = v ?? "";
                if (v == null) break;
            }
            return d;
        }

        // Đọc chuỗi JSON kế tiếp (bỏ qua escape \" và \/ mà feed hay dùng).
        private static string NextString(string s, ref int i)
        {
            while (i < s.Length && s[i] != '"') i++;
            if (i >= s.Length) return null;
            i++;
            var sb = new StringBuilder();
            while (i < s.Length && s[i] != '"')
            {
                if (s[i] == '\\' && i + 1 < s.Length)
                {
                    char n = s[++i];
                    sb.Append(n == 'n' ? '\n' : n == 't' ? '\t' : n);
                }
                else sb.Append(s[i]);
                i++;
            }
            i++;
            return sb.ToString();
        }

        private static string Get(Dictionary<string, string> d, string k) => d.TryGetValue(k, out var v) ? v : "";

        private static string Label(Ev e)
        {
            if (e.Impact == "High")
            {
                if (e.Ccy == "USD")
                {
                    string t = e.Title.ToLowerInvariant();
                    foreach (var k in TopTier) if (t.Contains(k)) return "🔴🔴";
                    return "🔴";
                }
                return "🔴(" + e.Ccy + ")";
            }
            return "🟠";
        }

        // Né tin: true nếu utcNow nằm trong ±minutes phút quanh tin USD mức CAO (không tính tin cả ngày).
        // tzOffset PHẢI trùng giá trị đã truyền cho Refresh (cache lưu giờ VN theo tzOffset đó).
        // Chỉ biết tin của TUẦN hiện tại (feed ff_calendar_thisweek) → với nến cũ hơn tuần này trả false.
        public static bool IsBlocked(DateTime utcNow, int tzOffset, int minutes)
        {
            List<Ev> src;
            lock (Gate) src = _cache;
            if (src == null) return false;
            var vn = utcNow.AddHours(tzOffset);
            foreach (var e in src)
            {
                if (e.Ccy != "USD" || e.Impact != "High" || e.AllDay) continue;
                if (Math.Abs((e.WhenVn - vn).TotalMinutes) <= minutes) return true;
            }
            return false;
        }

        // TIN BUỔI SÁNG (2026-11-26): chỉ báo hôm nay có tin hay không và tin lúc mấy giờ (giờ VN), cho 24 giờ tới.
        // Giờ VN tính từ giờ UTC tuyệt đối của feed. Kiểm chéo: độ lệch feed ghi kèm phải đúng độ lệch New York tại
        // giờ đó (theo luật giờ mùa hè Mỹ của máy) — lệch ⇒ thêm dòng cảnh báo. ny = null ⇒ bỏ kiểm chéo.
        public static List<string> MorningLines(IList<Ev> evs, DateTime nowUtc, int tzOffset, TimeZoneInfo ny, out bool tzMismatch)
        {
            tzMismatch = false;
            var outp = new List<string>();
            var nowVn = nowUtc.AddHours(tzOffset);
            outp.Add($"☀️ LỊCH TIN {nowVn:dd/MM} (giờ VN, 24 giờ tới)");
            if (ny != null)
            {
                var off = ny.GetUtcOffset(nowUtc);
                bool dst = ny.IsDaylightSavingTime(nowUtc);
                var t830 = new DateTime(2000, 1, 1, 8, 30, 0).Add(-off).AddHours(tzOffset);
                outp.Add($"Giờ New York đang UTC{(off < TimeSpan.Zero ? "−" : "+")}{Math.Abs(off.TotalHours):0} ({(dst ? "giờ mùa hè" : "giờ mùa đông")}): tin 8:30 sáng Mỹ = {t830:HH:mm} VN.");
            }
            var sel = new List<Ev>(); var hol = new List<Ev>();
            foreach (var e in evs ?? new List<Ev>())
            {
                if (e.AllDay) { if (e.Ccy == "USD" && e.Utc >= nowUtc.AddHours(-12) && e.Utc < nowUtc.AddHours(24)) hol.Add(e); continue; }
                if (e.Utc >= nowUtc && e.Utc < nowUtc.AddHours(24)) sel.Add(e);
                if (ny != null && e.OffMin != int.MinValue && e.OffMin != (int)Math.Round(ny.GetUtcOffset(e.Utc).TotalMinutes)) tzMismatch = true;
            }
            foreach (var h in hol) outp.Add($"🇺🇸 Mỹ nghỉ lễ ({h.Title}) — thanh khoản mỏng.");
            if (sel.Count == 0) outp.Add("Không có tin USD / EUR / GBP đáng kể.");
            foreach (var e in sel.OrderBy(x => x.Utc))
            {
                var vn = e.Utc.AddHours(tzOffset);
                string when = vn.Date == nowVn.Date ? vn.ToString("HH:mm") : vn.ToString("HH:mm") + $" (rạng sáng {vn:dd/MM})";
                string fc = string.IsNullOrEmpty(e.Forecast) ? "-" : e.Forecast;
                string pv = string.IsNullOrEmpty(e.Previous) ? "-" : e.Previous;
                outp.Add($"• {when} {Label(e)} {e.Title} (dự báo {fc} / trước {pv})");
            }
            if (tzMismatch) outp.Add("⚠ Giờ trong lịch tin không khớp múi giờ New York — kiểm lại trên forexfactory.com.");
            return outp;
        }

        public static List<string> MorningLines(DateTime nowUtc, int tzOffset, out bool tzMismatch)
        {
            List<Ev> src; lock (Gate) src = _cache;
            return MorningLines(src, nowUtc, tzOffset, NewYork(), out tzMismatch);
        }
    }

    // ---- Telegram (dùng chung cho DailyTpoBias + SessionZones) — 2026-11-26 -----------------------------------
    //  Bỏ 3 tin tổng hợp (sáng / chiều / trước phiên Mỹ). Chỉ còn:
    //    • TIN BUỔI SÁNG (07:00–11:00 VN, thứ Hai–thứ Sáu): hôm nay có tin không, tin lúc mấy giờ (NewsCalendar.MorningLines).
    //    • BÁO CHẠM VÙNG (SendOnce, gọi từ SessionZones).
    //  Chống gửi trùng bằng FILE KHOÁ tạo NGUYÊN TỬ (FileMode.CreateNew) → nhiều chart / 2 indicator cùng cầm token cũng chỉ
    //  1 tin. HTTP chạy nền (Task).
    internal sealed class TeleReport
    {
        public bool Enabled, TestNow;
        // Chỉ 1 instance (bật IsSender=true) mới thực sự gửi.
        public bool IsSender = true;
        public string BotToken = "", ChatId = "", ShareDir = "";
        public int TzOffset = 7;
        public bool ShowNews = true;       // tin buổi sáng
        public int MorningFromMin = 420, MorningToMin = 660;   // 07:00–11:00 VN; 10:45 chưa tải được lịch ⇒ báo lỗi

        private static readonly HttpClient Http = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
        private long _lastCheckTicks;
        private bool _lastTest;

        // Gọi 1 lần cuối mỗi Process(): kiểm mốc tin buổi sáng. (hd, symbol, kind, lines giữ cho tương thích, không dùng.)
        public void Run(HistoricalData hd, string symbol, string kind, IReadOnlyList<string> lines)
        {
            if (!Enabled) return;
            try
            {
                if (!IsSender) return;
                if (ShowNews) NewsCalendar.Refresh(Dir(), TzOffset, Log);   // tải nền, có cache 1h
                if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId)) return;

                long now = DateTime.UtcNow.Ticks;
                if (now - _lastCheckTicks < 15 * TimeSpan.TicksPerSecond) return;   // ~15s/lần
                _lastCheckTicks = now;
                CheckMorningNews();
            }
            catch (Exception ex) { Log("LỖI Run: " + ex.Message); }
        }

        // Xử lý RIÊNG nút "gửi thử" — gọi từ OnUpdate (mỗi tick / lúc đổi cấu hình), KHÔNG lệ
        // thuộc VA/Process đã sẵn sàng → bấm là gửi ngay + ghi log để soi lỗi.
        public void PollTest(string symbol)
        {
            bool edge = TestNow && !_lastTest;
            _lastTest = TestNow;
            if (!edge) return;
            Log($"nút TEST bật — enabled={Enabled}, có token={!string.IsNullOrWhiteSpace(BotToken)}, có chat_id={!string.IsNullOrWhiteSpace(ChatId)}");
            if (!Enabled) { Log("BỎ QUA: chưa bật 'Gửi Telegram'"); return; }
            if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId)) { Log("BỎ QUA: thiếu token hoặc chat_id"); return; }
            Log("TEST → đang gửi HTTP...");
            SendAsync("🔔 TEST — bot TPO chạy OK · " + (symbol ?? ""), null);
        }

        // ===== Dùng cho indicator KHÁC (vd RunnerSignal): gửi 1 tin THÔ, KHÔNG đụng section/lock TPO =====
        // Chỉ tái dùng HttpClient + đường log chung. Không có Compose/CheckTriggers ở đây.
        public void SendRaw(string text)
        {
            if (!Enabled) return;
            SendAsync(text, null);
        }

        // Gửi 1 tin MỘT LẦN DUY NHẤT theo khoá (vd báo chạm vùng): khoá = FILE tạo nguyên tử (CreateNew) trong thư mục chung
        // ⇒ nhiều tab / mở lại chart cũng không gửi lại. Chỉ instance được phép gửi (IsSender). Trả true nếu đã gửi.
        public bool SendOnce(string key, string text)
        {
            if (!Enabled || !IsSender || string.IsNullOrEmpty(key)) return false;
            if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId)) return false;
            try
            {
                string path = Path.Combine(Dir(), "touch_" + Safe(key) + ".lock");
                using (new FileStream(path, FileMode.CreateNew, FileAccess.Write)) { }
            }
            catch (IOException) { return false; }          // đã có khoá ⇒ đã gửi
            catch (Exception ex) { Log("LỖI khoá chạm: " + ex.Message); return false; }
            Log("Báo chạm vùng: " + key);
            SendAsync(text, null);
            return true;
        }

        // Nút "gửi thử" bản THÔ: gửi đúng testText của indicator gọi (không dùng Compose TPO).
        public void PollTestRaw(string testText)
        {
            bool edge = TestNow && !_lastTest;
            _lastTest = TestNow;
            if (!edge) return;
            Log($"nút TEST bật — enabled={Enabled}, có token={!string.IsNullOrWhiteSpace(BotToken)}, có chat_id={!string.IsNullOrWhiteSpace(ChatId)}");
            if (!Enabled) { Log("BỎ QUA: chưa bật báo Telegram"); return; }
            if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId)) { Log("BỎ QUA: thiếu token hoặc chat_id"); return; }
            Log("TEST → đang gửi HTTP...");
            SendAsync(testText, null);
        }

        private void Log(string msg)
        {
            try
            {
                string line = DateTime.UtcNow.AddHours(TzOffset).ToString("yyyy-MM-dd HH:mm:ss") + "  " + msg + "\n";
                File.AppendAllText(Path.Combine(Dir(), "tele_log.txt"), line);
            }
            catch { }
        }

        private string Dir()
        {
            string d = string.IsNullOrWhiteSpace(ShareDir)
                ? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TpoSuite")
                : ShareDir;
            Directory.CreateDirectory(d);
            return d;
        }

        private static string Safe(string s)
        {
            if (string.IsNullOrEmpty(s)) return "sym";
            var sb = new StringBuilder();
            foreach (char c in s) sb.Append(char.IsLetterOrDigit(c) ? c : '_');
            return sb.ToString();
        }

        // Tin buổi sáng: một lần mỗi ngày (khoá file theo ngày VN), thứ Hai–thứ Sáu, trong khung MorningFromMin–MorningToMin.
        // Chưa có lịch của tuần đang chạy thì chờ; tới 10:45 vẫn chưa có ⇒ gửi báo không tải được.
        private void CheckMorningNews()
        {
            if (!ShowNews) return;
            var nowUtc = DateTime.UtcNow;
            var vn = nowUtc.AddHours(TzOffset);
            if (vn.DayOfWeek == DayOfWeek.Saturday || vn.DayOfWeek == DayOfWeek.Sunday) return;
            int m = (int)vn.TimeOfDay.TotalMinutes;
            if (m < MorningFromMin || m > MorningToMin) return;
            bool ready = NewsCalendar.Ready(nowUtc);
            if (!ready && m < MorningToMin - 15) return;
            string lockPath = Path.Combine(Dir(), $"sent_news_{vn:yyyyMMdd}.lock");
            if (File.Exists(lockPath)) return;
            try { using (new FileStream(lockPath, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { } }
            catch { return; }
            string text;
            if (ready)
            {
                var lines = NewsCalendar.MorningLines(nowUtc, TzOffset, out bool mis);
                if (mis) Log("lịch tin: độ lệch giờ feed không khớp múi giờ New York");
                text = string.Join("\n", lines);
            }
            else text = $"☀️ LỊCH TIN {vn:dd/MM}: chưa tải được lịch tuần này từ Forex Factory — tự kiểm tra trên forexfactory.com.";
            Log("TIN SÁNG → đang gửi");
            SendAsync(text, lockPath);
        }

        private void SendAsync(string text, string lockPathOnFail)
        {
            if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId) || string.IsNullOrEmpty(text)) return;
            string url = $"https://api.telegram.org/bot{BotToken}/sendMessage";
            var form = new FormUrlEncodedContent(new Dictionary<string, string>
            {
                ["chat_id"] = ChatId, ["text"] = text, ["disable_web_page_preview"] = "true"
            });
            Task.Run(async () =>
            {
                try
                {
                    var resp = await Http.PostAsync(url, form).ConfigureAwait(false);
                    string body = "";
                    try { body = await resp.Content.ReadAsStringAsync().ConfigureAwait(false); } catch { }
                    Log($"HTTP {(int)resp.StatusCode} {(resp.IsSuccessStatusCode ? "OK" : "FAIL")}: {(body.Length > 200 ? body.Substring(0, 200) : body)}");
                    if (!resp.IsSuccessStatusCode && lockPathOnFail != null)
                        try { File.Delete(lockPathOnFail); } catch { }
                }
                catch (Exception ex)
                {
                    Log("HTTP LỖI: " + ex.Message);
                    if (lockPathOnFail != null) try { File.Delete(lockPathOnFail); } catch { }
                }
            });
        }
    }
    // ========================================================================
    //  ZonePolicy — LOẠI VÙNG NÀO ĐƯỢC VẼ, VẼ Ở LỚP NÀO (chốt 2026-10-17)
    // ========================================================================
    //  Tách khỏi SessionZones thành lớp thuần để test được không cần Quantower.
    //  Căn cứ (đều có đối chứng ngẫu nhiên, nguồn dày 474–724k nến M1):
    //   • VWAP tuần: đảo chiều 53,8% / 53,3% / 53,6% — ô duy nhất dương ở MỌI
    //     phép đo (research/HAP-THU-TAI-VUNG-KET-QUA.md, DAC-DIEM-CA-DAO-CHIEU.md).
    //   • VWAP ngày: 52,9% / 51,6%; hấp thụ đúng nghĩa xảy ra gần VWAP ngày nhiều
    //     hơn ngẫu nhiên +29% (z=+3,6).
    //   • HVN ngày/tuần: KHÔNG phải mốc phản ứng (5 cách đo, MEASURE-DENSE-RESULTS.md);
    //     sau cú phá thì nghiêng ĐI TIẾP 56% ⇒ chỉ làm NỀN / mục tiêu, không canh fade.
    //   • VAH/VAL: tự thân 50,4% (trung tính) nhưng là CẠNH range để gọi chế độ
    //     cân bằng / vừa phá ⇒ giữ. Từ 2026-10-23 (người học chốt): chỉ của NGÀY HÔM NAY
    //     đang hình thành (từ đầu phiên Á tới nay), không lấy riêng phiên Á/Âu/Mỹ.
    //   • BỎ mặc định: đỉnh/đáy phiên (backtest v2 −0,68, tệ nhất), naked POC phiên
    //     (hai phép đo trái dấu 46,5% vs 53,9%), cụm POC / băng giá trị (n=10 / n=2,
    //     bản chất là HVN), LVN tuần (chưa đo, trôi theo cửa sổ).
    public sealed class ZoneFilter
    {
        public bool SessionHighLow = false;
        public bool NakedPoc = false;
        public bool PocClusters = false;   // gồm cả "cụm POC" và "băng giá trị"
        public bool WeekLvn = false;
    }

    public static class ZonePolicy
    {
        // Loại vùng có được SINH ra không.
        public static bool KeepType(string type, ZoneFilter f)
        {
            if (f == null) f = new ZoneFilter();
            switch (type)
            {
                case "priorhl": return f.SessionHighLow;
                case "naked_poc": return f.NakedPoc;
                case "poc_cluster":
                case "value_band": return f.PocClusters;
                case "lvn_week": return f.WeekLvn;
                default: return true;   // vwap_*, va_edge, hvn_box, lvn (ngày)
            }
        }

        // true = lớp MỐC (đường đậm, có thể canh lệnh); false = lớp NỀN (dải mờ).
        public static bool IsMarkerType(string type)
        {
            switch (type)
            {
                case "hvn_box":                // hộp HVN dạng cụm (PLAN-VUNG-MANH.md §10–11), vẽ riêng
                case "lvn":
                case "lvn_week":
                case "strong": return false;   // vùng mạnh: dải tô màu, vẽ riêng (StrongZonePainter)
                default: return true;
            }
        }

        // Vai trò trên bảng: "canh" = vùng canh đảo chiều/hấp thụ (chỉ VWAP),
        // "canh_range" = cạnh range Âu, "nen" = hộp HVN (cụm khối lượng; đo cũ: đi tiếp/mục tiêu), "lvn",
        // "khac" = loại cũ chỉ hiện khi người dùng tự bật lại.
        public static string Role(string type)
        {
            switch (type)
            {
                case "vwap_week":
                case "vwap_day": return "canh";
                case "va_edge": return "canh_range";
                case "hvn_box": return "nen";
                case "lvn":
                case "lvn_week": return "lvn";
                case "strong": return "manh";   // vùng va đập nhiều + hợp lưu (PLAN-VUNG-MANH.md) — chưa kiểm định
                default: return "khac";
            }
        }

        // Thứ hạng để sắp xếp/giành khe: VWAP tuần > VWAP ngày > cạnh range > còn lại.
        public static double BaseStrength(string type)
        {
            switch (type)
            {
                case "vwap_week": return 95;
                case "vwap_day": return 85;
                case "va_edge": return 60;
                case "strong": return 90;
                default: return 40;
            }
        }
        // Vùng mạnh: 90, vùng vàng (≥3 nhóm hợp lưu + có HVN) 98. Chỉ để xếp thứ tự, không phải xác suất.
        public static double StrongStrength(bool gold) => gold ? 98 : 90;

        // Chỉ gộp hai vùng cùng lớp: không để dải nền HVN "nuốt" một mốc VWAP/cạnh
        // range rồi kéo giãn Lo/Hi của mốc đó. Vùng mạnh KHÔNG gộp với loại nào —
        // biên của nó chỉ do các điểm va đập quyết định (PLAN-VUNG-MANH.md §4.5).
        // Hộp HVN cũng không gộp với loại nào (biên = thân cụm khối lượng).
        public static bool CanMerge(string typeA, string typeB)
            => typeA != "strong" && typeB != "strong" && typeA != "hvn_box" && typeB != "hvn_box"
               && IsMarkerType(typeA) == IsMarkerType(typeB);

        // Symbol là MỘT hợp đồng cụ thể (GCZ26, NQZ26, MGCZ26…) ⇒ không có chỗ nối ⇒ tắt bộ chặn chỗ nối
        // (PLAN-VUNG-MANH.md §12.3: trên NQZ26 bộ chặn bắt nhầm khoảng trống giá thật qua giờ nghỉ).
        // isContinuous = Symbol.FutureContractType của Quantower (Continuous ⇒ true, Contract/Spread ⇒ false)
        // khi nền tảng có điền; null ⇒ đoán theo tên:
        //   bỏ khoảng trắng, chữ hoa; bắt đầu bằng "/" (mã liên tục "/GC:XCEC") ⇒ false; cắt từ ":", ".", "@",
        //   khoảng trắng đầu tiên; còn lại khớp gốc + mã tháng + năm (^[A-Z0-9]{1,4}[FGHJKMNQUVXZ][0-9]{1,2}$) ⇒ true.
        public static bool IsSingleContract(string symbolName, bool? isContinuous = null)
        {
            if (isContinuous.HasValue) return !isContinuous.Value;
            if (string.IsNullOrWhiteSpace(symbolName)) return false;
            string s = symbolName.Trim().ToUpperInvariant();
            if (s.StartsWith("/")) return false;
            int cut = s.IndexOfAny(new[] { ':', '.', '@', ' ' });
            if (cut >= 0) s = s.Substring(0, cut);
            return System.Text.RegularExpressions.Regex.IsMatch(s, "^[A-Z0-9]{1,4}[FGHJKMNQUVXZ][0-9]{1,2}$");
        }

        // Số nến M30 tối thiểu của "ngày hôm nay" để VAH/VAL có nghĩa (4 nến = 2 giờ);
        // ít hơn thì profile quá mỏng, không vẽ.
        public const int TodayVaMinBars = 4;

        // "Ngày hôm nay" = từ đầu phiên Á gần nhất tới nến mới nhất. labels = nhãn các
        // khối phiên theo thứ tự thời gian (khối cuối là khối đang chạy). Trả chỉ số khối
        // đầu tiên của cụm khối "A" cuối cùng (Á có thể bị tách đôi bởi khoảng trống dữ liệu);
        // -1 nếu chưa có khối Á nào.
        public static int TodayStartBlock(IList<string> labels)
        {
            if (labels == null) return -1;
            int i = labels.Count - 1;
            while (i >= 0 && labels[i] != "A") i--;
            if (i < 0) return -1;
            while (i > 0 && labels[i - 1] == "A") i--;
            return i;
        }

        // Mốc bắt đầu xin history M30 phụ. Neo vào NẾN MỚI NHẤT CỦA CHART, không neo
        // vào đồng hồ thật: ở Market Replay, chart đang ở quá khứ (vd 5/8) nên
        // "UtcNow − 45 ngày" rơi sau toàn bộ dữ liệu replay ⇒ 0 nến (sự cố 2026-10-17).
        // Không có nến chart (null) ⇒ dùng đồng hồ thật như cũ.
        public static DateTime AuxHistoryFrom(DateTime? lastChartBarUtc, DateTime nowUtc, int days)
        {
            DateTime anchor = lastChartBarUtc.HasValue && lastChartBarUtc.Value < nowUtc ? lastChartBarUtc.Value : nowUtc;
            return anchor.AddDays(-Math.Abs(days));
        }

        public static int VaEdgeSessionIndex(IList<string> labels, bool europeOnly)
        {
            if (labels == null || labels.Count == 0) return -1;
            if (europeOnly)
                for (int i = labels.Count - 1; i >= 0; i--)
                    if (labels[i] == "AU") return i;
            return labels.Count - 1;
        }
    }

    // ========================================================================
    //  StrongZones — VÙNG VA ĐẬP NHIỀU + HỢP LƯU (PLAN-VUNG-MANH.md, 2026-11-25)
    // ========================================================================
    //  ⚠ CHƯA KIỂM ĐỊNH: trên 589 phiên GC vùng này cho kết quả ngang vùng dời ngẫu
    //  nhiên (thắng 1:1 48,8 % / 47,2 % so với đối chứng 47,9 % / 47,5 %). Không sinh
    //  signal vào lệnh từ đây; không viết "vùng đảo chiều", "xác suất cao".
    //
    //  Chỉ nhận MẢNG THUẦN (nến M30 + khối lượng từng mức giá) ⇒ test được không cần
    //  Quantower, và không nhận tham số nào của khung chart ⇒ cùng history M30 thì cùng
    //  vùng dù chart là M1, M5 hay M30. Nến CUỐI luôn coi là nến đang chạy: j = n − 2.
    //  Bản tham chiếu Python (nguồn sự thật): research/vung_manh_2026-11-25/vung_manh.py
    //  + vm.py + hvn_cum2.py; bộ đối chiếu fixture/expected_cum2.json (689 ca, 357 điểm va đập),
    //  fixture/hvn_cum2_cases.json (19 profile) và fixture/nq_expected2.json (13 ca NQZ26) — tests/StrongZonesTests.cs.
    //
    //  HVN = HỘP cụm khối lượng lớn và đều (thân chữ D) của phiên/tuần đã đóng (§10, v2 §13, HvnClusters),
    //  không còn là từng đỉnh nhọn. Giá quay lại hộp: canh phản ứng đảo chiều HOẶC phá vỡ.
    //  Ghi chú mâu thuẫn (giữ cả hai ý): đo cũ trên HVN đỉnh nhọn coi HVN là "nền — đi tiếp /
    //  mục tiêu, không fade"; ở đây HVN là một mức HỢP LƯU cho vùng canh đảo chiều và làm vùng
    //  thành vàng (yêu cầu người học). Phép đo chưa phân xử (HVN-CUM.md: vàng chưa hơn vùng thường).
    public sealed class StrongZoneParams
    {
        public int K = 2;                 // đỉnh/đáy cục bộ: so với K nến mỗi bên
        public int M = 6;                 // cửa sổ "đi tới" và "bật lại" (nến M30)
        public double R = 1.0;            // bật lại tối thiểu (×U)
        public int LB = 5;                // số phiên ĐÃ ĐÓNG nhìn lại (cộng phiên đang chạy)
        public double WC = 0.30;          // bề rộng cụm tối đa (×U)
        public int NMin = 3;              // số lần va đập tối thiểu
        public double Pad = 0.05;         // nới mỗi mép vùng (×U)
        public double WMin = 0.20;        // bề rộng vùng tối thiểu (×U)
        public double Tol = 0.10;         // dung sai hợp lưu (×U)
        public int HvnDays = 5;           // HVN ngày lấy từ bao nhiêu phiên đã đóng
        public double HvnAway = 2.0;      // "đã rời xa" (×U), đo từ MÉP hộp; 0 = bỏ điều kiện
        // HVN dạng cụm v2 (PLAN-VUNG-MANH.md §13.1) — cụm khối lượng lớn và đều của một profile đã đóng;
        // tiêu chí không phụ thuộc biên độ profile. Mọi số là hằng (không có input).
        public double HvnSmooth = 0.05;     // nửa cửa sổ làm mượt (×up, up = TB High−Low nến M30 của chính profile)
        public double HvnBody = 0.80;       // lõi: khối lượng mượt ≥ 80 % đỉnh
        public double HvnWidth = 0.45;      // bề rộng đích của hộp (×up): lõi hẹp hơn thì nới về phía dày hơn
        public double HvnWidenFloor = 0.50; // khi nới không lấy mức có khối lượng mượt < 50 % đỉnh
        public double HvnWidenClimb = 0.05; // khi nới không leo cao hơn (đáy đã qua ở phía đó + 5 % đỉnh) — không sang bướu bên cạnh
        public double HvnAround = 3.0;      // "vùng xung quanh" = ± 3 × up (luật đỉnh cục bộ + luật nổi bật)
        public double HvnContrast = 2.0;    // nổi bật: mật độ hộp ≥ 2 × mật độ phần profile trong vùng xung quanh, ngoài hộp
        public double HvnBars = 4.5;        // nổi bật: khối lượng hộp ≥ 4,5 lần khối lượng TB một nến M30 của profile
        public double HvnMassDay = 0.12;    // HOẶC hộp chứa ≥ 12 % khối lượng profile ngày
        public double HvnMassWeek = 0.08;   // … profile tuần
        public double HvnMinWidth = 0.20;   // hộp sau khi nới vẫn hẹp hơn 0,20 × up ⇒ bỏ
        public int HvnMaxPerProfile = 2;    // số hộp tối đa khi profile hẹp
        public double HvnMaxStep = 6.0;     // số hộp tối đa = min(HvnMaxCap, max(HvnMaxPerProfile, floor(biên độ / (6 × up))))
        public int HvnMaxCap = 4;
        public double HvnFloor = 0.10;      // dừng khi đỉnh còn lại < 10 % đỉnh lớn nhất (chặn vòng lặp)
        public double HvnRadius = 8.0;      // hiển thị hộp HVN: mép gần cách giá ≤ 8 U (vùng mạnh vẫn Radius)
        public int HvnMaxSide = 2;          // hiển thị hộp HVN: tối đa 2 hộp gần nhất mỗi phía giá
        // Vùng đệm của hộp HVN (§14.1) — chỉ là lớp VẼ: sườn cụm sát ngoài mép hộp; không dùng trong hợp lưu / "rời xa".
        public double HvnBufFloor = 0.50;   // vùng đệm: khối lượng mượt ≥ 50 % đỉnh cụm (= HvnWidenFloor, khai riêng cho rõ)
        public double HvnBufCap = 0.45;     // bề rộng tối đa mỗi phía (×up) (= HvnWidth)
        public double HvnBufMin = 0.05;     // phía nào hẹp hơn 0,05 × up thì không có vùng đệm
        public int GoldMin = 3;           // vàng: ≥ 3 nhóm mức và có HVN
        public bool GroupEdges = true;    // gộp VAH/VAL với VWAP ±1σ cùng kỳ thành một nhóm
        public int MinGroup = 1;          // hiển thị: số nhóm mức hợp lưu tối thiểu
        public double Radius = 4.0;       // hiển thị: mép gần cách giá tối đa (×U)
        public int MaxSide = 3;           // hiển thị: số vùng tối đa mỗi phía
        public double Sep = 0.15;         // hiển thị: hai vùng cách nhau dưới bấy nhiêu (×U) chỉ giữ vùng mạnh hơn
        public int MinDayBars = 20;       // phiên ngắn hơn (lễ) không làm "hôm qua", không đếm vào HVN ngày
        public int UnitDays = 5;          // U = TB (High − Low) nến M30 của 5 phiên đã đóng
        public int MinWeekBars = 60;
        public double GapMinutes = 75;    // phiên mới khi nghỉ > 75 phút (GroupByGap)
        public double WeekGapHours = 30;  // tuần mới khi nghỉ > 30 giờ (WeekSpans)
        public double SpliceJump = 20;    // chỗ nối hợp đồng: nhảy ≥ bấy nhiêu (đơn vị giá); 0 = tắt
        public double SpliceMinGapMin = 30, SpliceMaxGapMin = 150;
        public int SideLookback = 400;    // giá trong vùng: lùi tối đa bấy nhiêu nến tìm phía đi vào
        public double VaFrac = 0.70;
        public int HistoryDays = 35;      // cửa sổ history chuẩn hoá (bất biến theo khung chart)

        public StrongZoneParams Clone() => (StrongZoneParams)MemberwiseClone();
        // Dấu vân tay của MỌI thông số — đổi input thì bộ đệm tự tính lại.
        public string Fingerprint()
            => string.Join("|", GetType().GetFields().Select(f => f.Name + "=" + Convert.ToString(f.GetValue(this), System.Globalization.CultureInfo.InvariantCulture)));
    }

    public sealed class SzPivot { public int I, Conf, Kind; public double Price; }   // Kind: +1 đỉnh, −1 đáy

    public sealed class SzLevel
    {
        public string Name = "";
        public double Lo, Hi;
        public bool IsHvn;
        public double Peak = double.NaN, Mass;   // HVN: đỉnh (khối lượng mượt) + tỉ trọng khối lượng của hộp
        public int End = -1, Src;   // End = nến cuối của profile nguồn; Src = số phiên/tuần lùi lại
        public double BufLo = double.NaN, BufHi = double.NaN;   // HVN: mép ngoài vùng đệm (§14.3); mức khác: NaN ⇒ coi như = Lo/Hi
    }

    // Một hộp HVN dạng cụm (StrongZones.HvnClusters, §13.2). Lo/Hi/Peak/CoreLo/CoreHi là giá (CoreLo–CoreHi = lõi ≥ 80 % đỉnh,
    // Lo–Hi = hộp sau khi nới); Rel = đỉnh hộp / đỉnh lớn nhất profile; Bars = khối lượng hộp tính bằng số nến M30 TB;
    // Con = mật độ hộp / mật độ xung quanh (≤ 999); Lon = qua nhờ ≥ massMin; Noi = qua nhờ nổi bật tại chỗ.
    public sealed class SzHvnBox
    {
        public double Lo, Hi, Peak, CoreLo, CoreHi, Mass, Rel, Bars, Con;
        public bool Lon, Noi;
        public double BufLo, BufHi;   // vùng đệm (§14.2): mép ngoài dưới/trên; = Lo/Hi khi phía đó không có đệm
    }

    // Hộp HVN ĐƯỢC VẼ (StrongZones.HvnBoxes): đã đủ điều kiện "đã rời xa" và trong bán kính hiển thị.
    public sealed class SzHvnShown
    {
        public string Name = "";    // "hvn_d" / "hvn_w"
        public double Lo, Hi, Peak, Mass, Dist;
        public int End, Src;
        public string Label = "";   // "HVN ngày" / "HVN tuần"
        // Vùng đệm ĐƯỢC VẼ (§14.3): chỉ phía giá đang đứng (giá trong hộp ⇒ cả hai). = Lo/Hi khi không vẽ phía đó.
        // Mặc định NaN (dựng tay không gán) ⇒ không vẽ đệm.
        public double BufLo = double.NaN, BufHi = double.NaN;
    }

    public sealed class SzZone
    {
        public double Lo, Hi, Pmin, Pmax, U;
        public int N, NHigh, Newest, Oldest;
        public List<string> Names = new List<string>();
        public int NGroup;
        public bool Hvn, Gold;
        // ---- hiển thị (Display) ----
        public int Side;            // +1 hỗ trợ, −1 kháng cự, 0 chưa rõ
        public double Dist;         // khoảng cách mép gần tới giá (0 khi giá trong vùng)
        public bool Inside;
        public string Color = "";   // "xanh" / "do" / "vang" / "xam"
        public string Label = "";
        public SzZone CloneZone() { var z = (SzZone)MemberwiseClone(); z.Names = new List<string>(Names); return z; }
    }

    public sealed class SzProfile
    {
        public double[] Pr, W;
        public double Poc, Vah, Val, Vwap, Sigma, PocPos, VaFrac;
        public bool Approx;          // thiếu khối lượng theo giá ⇒ TPO + giá điển hình
    }

    // Chuỗi nến M30 + ranh giới phiên / tuần / chỗ nối + đơn vị U từng phiên.
    public sealed class SzSeries
    {
        public readonly int N;
        public readonly DateTime[] T;
        public readonly double[] O, H, L, C, V;
        public readonly double Tick, RowStep;
        public readonly List<(int a, int b)> Days = new List<(int a, int b)>();
        public readonly List<(int a, int b)> Weeks = new List<(int a, int b)>();
        public readonly int[] DayOf, WeekOf, Seg;
        public readonly List<int> Splices = new List<int>();
        public readonly double[] UnitDay;
        private readonly Func<int, IEnumerable<KeyValuePair<double, double>>> _levelsOf;
        private readonly long[][] _lvTick;
        private readonly double[][] _lvVol;
        private readonly double _invTick;
        private readonly bool _intInv;

        public SzSeries(IList<DateTime> t, IList<double> o, IList<double> h, IList<double> l, IList<double> c,
                        IList<double> vol, Func<int, IEnumerable<KeyValuePair<double, double>>> levelsOf,
                        double tick, double rowStep, StrongZoneParams p)
        {
            p ??= new StrongZoneParams();
            N = t?.Count ?? 0;
            T = t?.ToArray() ?? new DateTime[0];
            O = o?.ToArray() ?? new double[N]; H = h?.ToArray() ?? new double[N];
            L = l?.ToArray() ?? new double[N]; C = c?.ToArray() ?? new double[N];
            V = vol?.ToArray() ?? new double[N];
            Tick = tick; RowStep = rowStep;
            _levelsOf = levelsOf;
            _lvTick = new long[N][]; _lvVol = new double[N][];
            double inv = 1.0 / tick;
            _intInv = Math.Abs(inv - Math.Round(inv)) < 1e-9;
            _invTick = _intInv ? Math.Round(inv) : inv;
            DayOf = new int[N]; WeekOf = new int[N]; Seg = new int[N];
            UnitDay = new double[0];
            if (N == 0) return;

            // phiên (GroupByGap) + tuần (WeekSpans)
            int ds = 0, ws = 0;
            for (int i = 1; i < N; i++)
            {
                double gm = (T[i] - T[i - 1]).TotalMinutes;
                if (gm > p.GapMinutes) { Days.Add((ds, i - 1)); ds = i; }
                if (gm > p.WeekGapHours * 60) { Weeks.Add((ws, i - 1)); ws = i; }
            }
            Days.Add((ds, N - 1)); Weeks.Add((ws, N - 1));
            for (int k = 0; k < Days.Count; k++) for (int i = Days[k].a; i <= Days[k].b; i++) DayOf[i] = k;
            for (int k = 0; k < Weeks.Count; k++) for (int i = Weeks[k].a; i <= Weeks[k].b; i++) WeekOf[i] = k;
            // chỗ nối hợp đồng (LastSpliceIndex): nghỉ 30–150 phút + nhảy ≥ SpliceJump
            int sg = 0;
            for (int i = 0; i < N; i++)
            {
                if (i >= 1 && p.SpliceJump > 0)
                {
                    double gm = (T[i] - T[i - 1]).TotalMinutes;
                    if (gm >= p.SpliceMinGapMin && gm <= p.SpliceMaxGapMin && Math.Abs(O[i] - C[i - 1]) >= p.SpliceJump)
                    { Splices.Add(i); sg++; }
                }
                Seg[i] = sg;
            }
            // U(k) = TB (High − Low) mọi nến từ phiên max(0, k−5) tới phiên k−1; cần ≥ 2 phiên
            UnitDay = new double[Days.Count];
            for (int k = 0; k < Days.Count; k++)
            {
                int lo = Math.Max(0, k - p.UnitDays);
                if (k - lo < 2) { UnitDay[k] = double.NaN; continue; }
                int a = Days[lo].a, b = Days[k - 1].b;
                double s = 0; for (int i = a; i <= b; i++) s += H[i] - L[i];
                UnitDay[k] = s / (b - a + 1);
            }
        }

        public double U(int i) => UnitDay[DayOf[i]];
        public long TickOf(double price) => (long)Math.Round(price / Tick);
        // Giá chuẩn của một tick: k / (1/tick) khi 1/tick nguyên (0,1 → /10) — trùng tk/10.0 của Python.
        public double PriceOfTick(long k) => _intInv ? k / _invTick : k * Tick;

        private void LoadLevels(int i)
        {
            if (_lvTick[i] != null) return;
            var acc = new Dictionary<long, double>();
            var src = _levelsOf?.Invoke(i);
            if (src != null)
                foreach (var kv in src)
                {
                    long k = TickOf(kv.Key);
                    acc[k] = acc.TryGetValue(k, out var c0) ? c0 + kv.Value : kv.Value;
                }
            var ks = acc.Keys.ToArray(); Array.Sort(ks);
            _lvTick[i] = ks; _lvVol[i] = ks.Select(k => acc[k]).ToArray();
        }

        // (tick, khối lượng) cộng dồn trên nến [a..b], theo tick tăng dần.
        public (long[] tk, double[] v) TicksOver(int a, int b)
        {
            var acc = new Dictionary<long, double>();
            for (int i = Math.Max(0, a); i <= b && i < N; i++)
            {
                LoadLevels(i);
                var kk = _lvTick[i]; var vv = _lvVol[i];
                for (int q = 0; q < kk.Length; q++) acc[kk[q]] = acc.TryGetValue(kk[q], out var c0) ? c0 + vv[q] : vv[q];
            }
            var ks = acc.Keys.ToArray(); Array.Sort(ks);
            return (ks, ks.Select(k => acc[k]).ToArray());
        }
    }

    public sealed class SzResult
    {
        public int J = -1, D = -1;
        public double U = double.NaN;
        public List<SzPivot> Pivots = new List<SzPivot>();     // mọi điểm va đập tìm được (cả conf > j)
        public List<SzLevel> Levels = new List<SzLevel>();     // mức hợp lưu của hôm nay
        public List<SzZone> Clusters = new List<SzZone>();     // cụm ≥ NMin điểm, kèm hợp lưu
        public bool Approx;                                     // có mức tính gần đúng (thiếu PriceLevels)
        public double[] Closes = new double[0];
        public double[] Highs = new double[0], Lows = new double[0];
    }

    public static class StrongZones
    {
        // nhóm mức độc lập: VAH và VWAP+1σ của cùng một kỳ gần như trùng nhau (VA 70 % ≈ ±1σ) ⇒ tính MỘT
        public static readonly Dictionary<string, string> Group = new Dictionary<string, string>
        {
            ["vwap_d"] = "giua_d", ["vah_d"] = "tren_d", ["vwap_d_tren"] = "tren_d", ["val_d"] = "duoi_d", ["vwap_d_duoi"] = "duoi_d",
            ["vwap_w"] = "giua_w", ["vah_w"] = "tren_w", ["vwap_w_tren"] = "tren_w", ["val_w"] = "duoi_w", ["vwap_w_duoi"] = "duoi_w",
            ["hvn_d"] = "hvn_d", ["hvn_w"] = "hvn_w",
        };
        public static readonly Dictionary<string, string> Ten = new Dictionary<string, string>
        {
            ["vwap_d"] = "VWAP hôm qua", ["vwap_d_tren"] = "VWAP hôm qua +1σ", ["vwap_d_duoi"] = "VWAP hôm qua −1σ",
            ["vah_d"] = "VAH hôm qua", ["val_d"] = "VAL hôm qua",
            ["vwap_w"] = "VWAP tuần trước", ["vwap_w_tren"] = "VWAP tuần trước +1σ", ["vwap_w_duoi"] = "VWAP tuần trước −1σ",
            ["vah_w"] = "VAH tuần trước", ["val_w"] = "VAL tuần trước", ["hvn_d"] = "HVN ngày", ["hvn_w"] = "HVN tuần",
        };
        public static readonly string[] ThuTu =
            { "hvn_w", "hvn_d", "vah_w", "val_w", "vwap_w", "vwap_w_tren", "vwap_w_duoi", "vah_d", "val_d", "vwap_d", "vwap_d_tren", "vwap_d_duoi" };

        // ---------------------------------------------------------------- profile
        // POC + VA (luật 2 hàng) trên mảng đã sắp theo giá. Trả chỉ số hàng.
        public static (int poc, int hi, int lo) ValueAreaIdx(double[] w, double frac = 0.70)
        {
            int n = w.Length;
            if (n == 0) return (-1, -1, -1);
            double tot = 0; for (int i = 0; i < n; i++) tot += w[i];
            if (tot <= 0) return (-1, -1, -1);
            int poc = 0; for (int i = 1; i < n; i++) if (w[i] > w[poc]) poc = i;
            double acc = w[poc], target = tot * frac; int lo = poc, hi = poc;
            while (acc < target && (lo > 0 || hi < n - 1))
            {
                double up = (hi < n - 1 ? w[hi + 1] : 0) + (hi < n - 2 ? w[hi + 2] : 0);
                double dn = (lo > 0 ? w[lo - 1] : 0) + (lo > 1 ? w[lo - 2] : 0);
                if (hi >= n - 1) { acc += dn; lo = Math.Max(0, lo - 2); }
                else if (lo <= 0) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else if (up >= dn) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else { acc += dn; lo = Math.Max(0, lo - 2); }
            }
            return (poc, hi, lo);
        }

        // ---------------------------------------------------------------- HVN dạng cụm v2 (§13.2)
        // Giá chuẩn của bước giá k: k / (1/tick) khi 1/tick nguyên (0,1 → /10) — trùng tk × 0,1 của Python.
        public static double PriceOfTick(long k, double tick)
        {
            double inv = 1.0 / tick;
            return Math.Abs(inv - Math.Round(inv)) < 1e-9 ? k / Math.Round(inv) : k * tick;
        }

        // Nửa cửa sổ làm mượt (số bước giá): h = max(1, floor(SM × up / tick + 0,5)).
        public static int HvnHalfWindow(double up, double tick, StrongZoneParams p)
            => Math.Max(1, (int)Math.Floor(p.HvnSmooth * up / tick + 0.5));

        // "Vùng xung quanh" (số bước giá): dn = max(1, floor(HvnAround × up / tick + 0,5)).
        public static int HvnAroundTicks(double up, double tick, StrongZoneParams p)
            => Math.Max(1, (int)Math.Floor(Math.Min(p.HvnAround * up / tick, 1e9) + 0.5));

        // Bề rộng tối đa vùng đệm mỗi phía (số bước giá, §14.2): cap = max(1, floor(HvnBufCap × upTicks + 0,5)).
        public static int HvnBufCapTicks(double upTicks, StrongZoneParams p)
            => Math.Max(1, (int)Math.Floor(Math.Min(p.HvnBufCap * upTicks, 1e9) + 0.5));

        // Số hộp tối đa của một profile: span = bước giá cao nhất − thấp nhất, upTicks = up / tick.
        public static int HvnMaxBoxes(long span, double upTicks, StrongZoneParams p)
        {
            double f = Math.Floor(span / (p.HvnMaxStep * upTicks));
            if (double.IsNaN(f)) f = 0;
            return (int)Math.Min(p.HvnMaxCap, Math.Max(p.HvnMaxPerProfile, f));
        }

        // Bản (giá, khối lượng) — cộng dồn theo bước giá rồi gọi bản số nguyên.
        public static List<SzHvnBox> HvnClusters(IEnumerable<KeyValuePair<double, double>> levels, double tick, double up, int nBars, double massMin, StrongZoneParams p)
        {
            var acc = new SortedDictionary<long, double>();
            if (levels != null)
                foreach (var kv in levels)
                {
                    long k = (long)Math.Round(kv.Key / tick);
                    acc[k] = acc.TryGetValue(k, out var c0) ? c0 + kv.Value : kv.Value;
                }
            return HvnClusters(acc.Keys.ToArray(), acc.Values.ToArray(), tick, up, nBars, massMin, p);
        }

        // tk: bước giá (số nguyên, tăng dần, không trùng); v: khối lượng THÔ từng bước giá của cả profile;
        // nBars = số nến M30 của profile. Trả các hộp theo thứ tự tìm thấy (đỉnh cao trước).
        // Bản tham chiếu: hvn_cum2.py clusters(). Mọi phép so là tích số nguyên × hằng bằng double, không chia.
        public static List<SzHvnBox> HvnClusters(long[] tk, double[] v, double tick, double up, int nBars, double massMin, StrongZoneParams p)
        {
            var outp = new List<SzHvnBox>();
            if (tk == null || tk.Length == 0 || tick <= 0 || double.IsNaN(up) || up <= 0) return outp;
            long t0 = tk[0];
            long nl = tk[tk.Length - 1] - t0 + 1;
            if (nl < 3 || nl > 50_000_000) return outp;
            int n = (int)nl;
            var w = new double[n];
            double tot = 0;
            for (int q = 0; q < tk.Length; q++) w[tk[q] - t0] += v[q];
            for (int i = 0; i < n; i++) tot += w[i];
            if (tot <= 0) return outp;
            double upT = up / tick;
            int h = HvnHalfWindow(up, tick, p);
            int dn = HvnAroundTicks(up, tick, p);
            double wt = p.HvnWidth * upT;
            int maxBoxes = HvnMaxBoxes(n - 1, upT, p);
            // S[i] = Σ w[max(0, i−h) .. min(n−1, i+h)] qua mảng cộng dồn (giống np.cumsum)
            var cs = new double[n + 1];
            for (int i = 0; i < n; i++) cs[i + 1] = cs[i] + w[i];
            var S = new double[n];
            double p1 = double.MinValue;
            for (int i = 0; i < n; i++) { S[i] = cs[Math.Min(n, i + h + 1)] - cs[Math.Max(0, i - h)]; if (S[i] > p1) p1 = S[i]; }
            double Sum(int a, int b) { double m = 0; for (int i = a; i <= b; i++) m += w[i]; return m; }
            var used = new bool[n];
            var idx = new List<(int lo, int hi, int pk)>();
            void Mark(int a, int b) { for (int i = a; i <= b; i++) used[i] = true; }
            for (int it = 0; it < 2000; it++)
            {
                // 1. đỉnh còn lại cao nhất (hoà ⇒ chỉ số nhỏ nhất)
                int ib = -1; double P = double.NegativeInfinity;
                for (int i = 0; i < n; i++) { double c = used[i] ? -1.0 : S[i]; if (c > P) { P = c; ib = i; } }
                if (ib < 0 || P <= 0 || P < p.HvnFloor * p1) break;
                // 2. lõi ≥ HvnBody × đỉnh
                double thr = p.HvnBody * P;
                int lo = ib, hi = ib;
                while (lo > 0 && !used[lo - 1] && S[lo - 1] >= thr) lo--;
                while (hi < n - 1 && !used[hi + 1] && S[hi + 1] >= thr) hi++;
                bool vai = (lo > 0 && used[lo - 1] && S[lo - 1] >= thr) || (hi < n - 1 && used[hi + 1] && S[hi + 1] >= thr);
                if (vai) { Mark(lo, hi); continue; }                 // vai của khối cao hơn, không có đáy tách
                // 3. phải là đỉnh cao nhất trong ± dn (xét mọi ô, kể cả đã dùng); bằng nhau thì qua
                double mxAround = double.MinValue;
                for (int i = Math.Max(0, ib - dn), e = Math.Min(n - 1, ib + dn); i <= e; i++) if (S[i] > mxAround) mxAround = S[i];
                if (P < mxAround) { Mark(lo, hi); continue; }
                // 4. nới tới bề rộng đích, về phía dày hơn; không dưới sàn, không leo sang bướu bên cạnh
                int coreLo = lo, coreHi = hi;
                double fl = p.HvnWidenFloor * P, vd = p.HvnWidenClimb * P;
                double mL = double.MaxValue, mR = double.MaxValue;
                for (int i = lo; i <= ib; i++) mL = Math.Min(mL, S[i]);
                for (int i = ib; i <= hi; i++) mR = Math.Min(mR, S[i]);
                while ((hi - lo) < wt)
                {
                    bool okL = lo > 0 && !used[lo - 1] && S[lo - 1] >= fl && S[lo - 1] <= mL + vd;
                    bool okR = hi < n - 1 && !used[hi + 1] && S[hi + 1] >= fl && S[hi + 1] <= mR + vd;
                    if (!okL && !okR) break;
                    if (okL && (!okR || S[lo - 1] >= S[hi + 1])) { lo--; mL = Math.Min(mL, S[lo]); }
                    else { hi++; mR = Math.Min(mR, S[hi]); }
                }
                // 5. đánh dấu (kể cả khi bị loại dưới đây)
                Mark(lo, hi);
                // 6. vẫn hẹp ⇒ đỉnh nhọn
                if ((hi - lo) < p.HvnMinWidth * upT) continue;
                // 7. đủ lớn: lớn so với cả profile HOẶC nổi bật tại chỗ
                double vIn = Sum(lo, hi);
                int nIn = hi - lo + 1;
                int A = Math.Max(0, lo - dn), Z = Math.Min(n - 1, hi + dn);
                int nOut = (lo - A) + (Z - hi);
                double vOut = Sum(A, lo - 1) + Sum(hi + 1, Z);
                bool lon = vIn >= massMin * tot;
                bool noi = vIn * nBars >= p.HvnBars * tot && vIn * nOut >= p.HvnContrast * vOut * nIn;
                if (!(lon || noi)) continue;
                double mass = vIn / tot;
                // 8. ghi hộp
                outp.Add(new SzHvnBox
                {
                    Lo = PriceOfTick(t0 + lo, tick), Hi = PriceOfTick(t0 + hi, tick), Peak = PriceOfTick(t0 + ib, tick),
                    CoreLo = PriceOfTick(t0 + coreLo, tick), CoreHi = PriceOfTick(t0 + coreHi, tick),
                    Mass = mass, Rel = P / p1, Bars = mass * nBars,
                    Con = vOut > 0 ? Math.Min((vIn * nOut) / (vOut * nIn), 999.0) : 999.0,
                    Lon = lon, Noi = noi,
                });
                idx.Add((lo, hi, ib));
                if (outp.Count >= maxBoxes) break;
            }
            // 9. vùng đệm (§14.2) — chạy SAU khi đã tìm xong mọi hộp ⇒ không ảnh hưởng việc tìm hộp.
            //    Nới từ mép hộp ra ngoài chừng nào S ≥ HvnBufFloor × đỉnh cụm, tối đa cap bước; hẹp hơn mn thì bỏ.
            //    Không xét used[], không có luật "không leo". Bản tham chiếu: vung_dem.py add_buffers().
            int cap = HvnBufCapTicks(upT, p);
            double mn = p.HvnBufMin * upT;
            for (int q = 0; q < outp.Count; q++)
            {
                var (lo, hi, pk) = idx[q];
                double thr = p.HvnBufFloor * S[pk];
                int i = hi;
                while (i < n - 1 && (i - hi) < cap && S[i + 1] >= thr) i++;
                int k = lo;
                while (k > 0 && (lo - k) < cap && S[k - 1] >= thr) k--;
                outp[q].BufHi = PriceOfTick(t0 + ((i - hi) >= mn ? i : hi), tick);
                outp[q].BufLo = PriceOfTick(t0 + ((lo - k) >= mn ? k : lo), tick);
            }
            return outp;
        }

        public static (double vwap, double sigma) VwapSigma(IList<double> prices, IList<double> vols)
        {
            double sv = 0, spv = 0;
            for (int i = 0; i < prices.Count; i++) { sv += vols[i]; spv += prices[i] * vols[i]; }
            if (prices.Count == 0 || sv <= 0) return (double.NaN, double.NaN);
            double m = spv / sv, s2 = 0;
            for (int i = 0; i < prices.Count; i++) { double d = prices[i] - m; s2 += d * d * vols[i]; }
            return (m, Math.Sqrt(s2 / sv));
        }

        public static SzProfile ProfileStats(SzSeries s, int a, int b, StrongZoneParams p)
        {
            if (a < 0 || b < a) return null;
            var (tk, tv) = s.TicksOver(a, b);
            double[] pr, w; double vwap, sigma; bool approx = false;
            if (tk.Length > 0)
            {
                var rows = new SortedDictionary<long, double>();
                var px = new double[tk.Length];
                for (int q = 0; q < tk.Length; q++)
                {
                    px[q] = s.PriceOfTick(tk[q]);
                    long rid = (long)Math.Round(px[q] / s.RowStep);
                    rows[rid] = rows.TryGetValue(rid, out var c0) ? c0 + tv[q] : tv[q];
                }
                pr = rows.Keys.Select(r => r * s.RowStep).ToArray(); w = rows.Values.ToArray();
                (vwap, sigma) = VwapSigma(px, tv);
            }
            else
            {
                // Thiếu PriceLevels: hàng = TPO (đếm nến phủ), VWAP = giá điển hình × khối lượng nến (0 ⇒ trọng số 1)
                approx = true;
                var rows = new SortedDictionary<long, double>();
                var px = new List<double>(); var vv = new List<double>();
                for (int i = a; i <= b; i++)
                {
                    long r0 = (long)Math.Round(s.L[i] / s.RowStep), r1 = (long)Math.Round(s.H[i] / s.RowStep);
                    for (long r = r0; r <= r1; r++) rows[r] = rows.TryGetValue(r, out var c0) ? c0 + 1 : 1;
                    px.Add((s.H[i] + s.L[i] + s.C[i]) / 3.0); vv.Add(s.V[i] > 0 ? s.V[i] : 1);
                }
                pr = rows.Keys.Select(r => r * s.RowStep).ToArray(); w = rows.Values.ToArray();
                (vwap, sigma) = VwapSigma(px, vv);
            }
            if (w.Length < 3) return null;
            var (poc, vh, vl) = ValueAreaIdx(w, p.VaFrac);
            if (poc < 0) return null;
            double rng = Math.Max(pr[pr.Length - 1] - pr[0], 1e-9);
            return new SzProfile
            {
                Pr = pr, W = w, Poc = pr[poc], Vah = pr[vh], Val = pr[vl], Vwap = vwap, Sigma = sigma,
                PocPos = (pr[poc] - pr[0]) / rng, VaFrac = (pr[vh] - pr[vl]) / rng, Approx = approx,
            };
        }

        // ---------------------------------------------------------------- mức hợp lưu
        // Mức của phiên d — chỉ từ phiên/tuần ĐÃ ĐÓNG trước d; HVN tuần này tính tới hết hôm qua.
        public static List<SzLevel> DayLevels(SzSeries s, int d, StrongZoneParams p, out bool approx)
        {
            var outp = new List<SzLevel>();
            bool apx = false;
            int a0 = s.Days[d].a;
            int seg = s.Seg[a0];
            int lastSp = 0; foreach (var sp in s.Splices) if (sp <= a0 && sp > lastSp) lastSp = sp;

            void AddPoints(SzProfile st, string pre)
            {
                apx |= st.Approx;
                void Add(string nm, double v) { if (!double.IsNaN(v)) outp.Add(new SzLevel { Name = nm, Lo = v, Hi = v }); }
                Add("vwap_" + pre, st.Vwap); Add("vwap_" + pre + "_tren", st.Vwap + st.Sigma); Add("vwap_" + pre + "_duoi", st.Vwap - st.Sigma);
                Add("vah_" + pre, st.Vah); Add("val_" + pre, st.Val);
            }
            void AddHvn(int a, int b, string name, int src)
            {
                var st = ProfileStats(s, a, b, p);
                if (st == null) return;
                apx |= st.Approx;
                // HVN dạng cụm (§10.3, v2 §13.3): khối lượng THÔ từng bước giá (không qua hàng 2 tick), up của chính profile.
                // Thiếu khối lượng theo giá ⇒ không có hộp (không đoán bằng TPO).
                var (tk, tv) = s.TicksOver(a, b);
                double up = 0; for (int i = a; i <= b; i++) up += s.H[i] - s.L[i];
                up /= (b - a + 1);
                foreach (var c in HvnClusters(tk, tv, s.Tick, up, b - a + 1, name == "hvn_w" ? p.HvnMassWeek : p.HvnMassDay, p))
                    outp.Add(new SzLevel { Name = name, Lo = c.Lo, Hi = c.Hi, IsHvn = true, Peak = c.Peak, Mass = c.Mass, End = b, Src = src,
                                           BufLo = c.BufLo, BufHi = c.BufHi });
            }

            // hôm qua = phiên đã đóng gần nhất có ≥ MinDayBars nến
            int y = d - 1;
            while (y >= 0 && (s.Days[y].b - s.Days[y].a + 1) < p.MinDayBars) y--;
            if (y >= 0 && s.Seg[s.Days[y].a] == seg)
            {
                var st = ProfileStats(s, s.Days[y].a, s.Days[y].b, p);
                if (st != null) AddPoints(st, "d");
            }
            // HVN ngày: 5 phiên đã đóng gần nhất (cùng hợp đồng, bỏ phiên ngắn)
            int cnt = 0, yy = d - 1;
            while (yy >= 0 && cnt < p.HvnDays)
            {
                var (a, b) = s.Days[yy];
                if (s.Seg[a] != seg) break;
                if (b - a + 1 >= p.MinDayBars) { AddHvn(a, b, "hvn_d", d - yy); cnt++; }
                yy--;
            }
            // tuần trước (cắt ở chỗ nối gần nhất ≤ a0)
            int w = s.WeekOf[a0];
            if (w >= 1)
            {
                var (a, b) = s.Weeks[w - 1];
                a = Math.Max(a, lastSp);
                if (b - a + 1 >= p.MinWeekBars)
                {
                    var st = ProfileStats(s, a, b, p);
                    if (st != null) AddPoints(st, "w");
                    AddHvn(a, b, "hvn_w", 1);
                }
            }
            // tuần này tính tới hết hôm qua — chỉ sinh HVN
            {
                int a = Math.Max(s.Weeks[w].a, lastSp), b = a0 - 1;
                if (b - a + 1 >= p.MinWeekBars) AddHvn(a, b, "hvn_w", 0);
            }
            approx = apx;
            return outp;
        }

        // Hộp HVN đủ điều kiện tại nến j: sau khi profile chốt, giá đã từng cách MÉP hộp ≥ HvnAway × U (§10.4).
        public static bool HvnOk(SzLevel lv, IList<double> h, IList<double> l, int j, double u, StrongZoneParams p)
        {
            int a = lv.End + 1;
            if (a > j) return false;
            double mx = double.MinValue, mn = double.MaxValue;
            for (int i = a; i <= j; i++) { if (h[i] > mx) mx = h[i]; if (l[i] < mn) mn = l[i]; }
            return Math.Max(mx - lv.Hi, lv.Lo - mn) >= p.HvnAway * u;
        }

        // ---------------------------------------------------------------- điểm va đập
        public static List<SzPivot> Pivots(SzSeries s, StrongZoneParams p)
        {
            var res = new List<SzPivot>();
            int n = s.N, k = p.K, m = p.M;
            var h = s.H; var l = s.L; var seg = s.Seg;
            for (int i = m; i < n - 1; i++)
            {
                double u = s.U(i);
                if (double.IsNaN(u)) continue;
                if (seg[i - m] != seg[i]) continue;
                if (i + k >= n) continue;
                int e = Math.Min(n - 1, i + m);
                // đỉnh
                {
                    bool ok = true;
                    for (int q = i - k; q < i; q++) if (!(h[i] > h[q])) { ok = false; break; }
                    if (ok) for (int q = i + 1; q <= i + k; q++) if (!(h[i] >= h[q])) { ok = false; break; }
                    if (ok)
                    {
                        double mn = double.MaxValue; for (int q = i - m; q <= i; q++) mn = Math.Min(mn, l[q]);
                        ok = h[i] - mn >= p.R * u;
                    }
                    if (ok)
                        for (int q = i + 1; q <= e; q++)
                        {
                            if (h[q] > h[i] || seg[q] != seg[i]) break;
                            if (h[i] - l[q] >= p.R * u) { res.Add(new SzPivot { I = i, Conf = Math.Max(i + k, q), Price = h[i], Kind = 1 }); break; }
                        }
                }
                // đáy
                {
                    bool ok = true;
                    for (int q = i - k; q < i; q++) if (!(l[i] < l[q])) { ok = false; break; }
                    if (ok) for (int q = i + 1; q <= i + k; q++) if (!(l[i] <= l[q])) { ok = false; break; }
                    if (ok)
                    {
                        double mx = double.MinValue; for (int q = i - m; q <= i; q++) mx = Math.Max(mx, h[q]);
                        ok = mx - l[i] >= p.R * u;
                    }
                    if (ok)
                        for (int q = i + 1; q <= e; q++)
                        {
                            if (l[q] < l[i] || seg[q] != seg[i]) break;
                            if (h[q] - l[i] >= p.R * u) { res.Add(new SzPivot { I = i, Conf = Math.Max(i + k, q), Price = l[i], Kind = -1 }); break; }
                        }
                }
            }
            return res;
        }

        // ---------------------------------------------------------------- gom cụm
        // prices TĂNG DẦN. Lặp: neo có nhiều điểm nhất trong [p, p + wc] (hoà → neo giá thấp hơn) → lấy nhóm → bỏ ra.
        // Trả danh sách nhóm, mỗi nhóm là danh sách chỉ số vào prices.
        public static List<List<int>> Cluster(IList<double> prices, double wc)
        {
            var alive = Enumerable.Range(0, prices.Count).ToList();
            var res = new List<List<int>>();
            while (alive.Count > 0)
            {
                int bestA = 0, bestC = -1, z = 0;
                for (int a = 0; a < alive.Count; a++)
                {
                    double lim = prices[alive[a]] + wc + 1e-9;
                    if (z < a) z = a;
                    while (z < alive.Count && prices[alive[z]] <= lim) z++;
                    int c = z - a;
                    if (c > bestC) { bestC = c; bestA = a; }
                }
                var mem = alive.GetRange(bestA, bestC);
                res.Add(mem);
                alive.RemoveRange(bestA, bestC);
            }
            return res;
        }

        // Biên vùng từ giá thấp/cao nhất trong cụm (nới PAD, tối thiểu WMIN, ra mép tick).
        public static (double lo, double hi) Bounds(double pmin, double pmax, double u, double tick, StrongZoneParams p)
        {
            double lo = pmin - p.Pad * u, hi = pmax + p.Pad * u;
            if (hi - lo < p.WMin * u) { double mid = (pmin + pmax) / 2; lo = mid - p.WMin * u / 2; hi = mid + p.WMin * u / 2; }
            lo = Math.Floor(lo / tick + 1e-6) * tick;
            hi = Math.Ceiling(hi / tick - 1e-6) * tick;
            return (lo, hi);
        }

        // Tên mức (đã khử lặp, đúng thứ tự cố định) ⇒ số nhóm, có HVN, vàng.
        public static (List<string> names, int ngroup, bool hvn, bool gold) Grade(IEnumerable<string> hit, StrongZoneParams p)
        {
            var set = new HashSet<string>(hit);
            var names = ThuTu.Where(set.Contains).ToList();
            int ng = names.Select(nm => p.GroupEdges ? Group[nm] : nm).Distinct().Count();
            bool hv = names.Any(nm => nm.StartsWith("hvn"));
            return (names, ng, hv, ng >= p.GoldMin && hv);
        }

        // ---------------------------------------------------------------- tính toàn bộ cấu trúc tại j = n − 2
        public static SzResult Compute(SzSeries s, StrongZoneParams p, Dictionary<string, (List<SzLevel> lv, bool apx)> levelCache = null)
        {
            p ??= new StrongZoneParams();
            var res = new SzResult { Closes = s.C, Highs = s.H, Lows = s.L };
            if (s.N < 3) return res;
            int j = s.N - 2, jn = s.N - 1;
            int d = s.DayOf[jn];
            res.J = j; res.D = d;
            res.Pivots = Pivots(s, p);
            double u = s.UnitDay[d];
            res.U = u;
            if (double.IsNaN(u)) return res;

            // mức hợp lưu của hôm nay — cố định suốt phiên (cache theo nến đầu phiên + độ dài phần trước nó)
            int a0 = s.Days[d].a;
            string lkey = s.T[0].Ticks + ":" + a0 + ":" + s.T[a0].Ticks + ":" + p.Fingerprint();
            List<SzLevel> levels; bool apx;
            if (levelCache != null && levelCache.TryGetValue(lkey, out var hitc)) { levels = hitc.lv; apx = hitc.apx; }
            else
            {
                levels = DayLevels(s, d, p, out apx);
                if (levelCache != null) { if (levelCache.Count > 4) levelCache.Clear(); levelCache[lkey] = (levels, apx); }
            }
            res.Levels = levels; res.Approx = apx;

            int lbStart = s.Days[Math.Max(0, d - p.LB)].a;
            int segNow = s.Seg[jn];
            var act = res.Pivots.Where(q => q.Conf <= j && q.I >= lbStart && s.Seg[q.I] == segNow)
                                .OrderBy(q => q.Conf).ToList();   // ổn định như Python: theo conf rồi theo giá
            act = act.OrderBy(q => q.Price).ToList();
            if (act.Count == 0) return res;
            var groups = Cluster(act.Select(q => q.Price).ToList(), p.WC * u);
            foreach (var g in groups)
            {
                if (g.Count < p.NMin) continue;
                var pts = g.Select(ix => act[ix]).ToList();
                double pmin = pts.Min(q => q.Price), pmax = pts.Max(q => q.Price);
                var (lo, hi) = Bounds(pmin, pmax, u, s.Tick, p);
                var hit = new List<string>();
                foreach (var L in levels)
                {
                    if (L.Lo <= hi + p.Tol * u && L.Hi >= lo - p.Tol * u)
                    {
                        if (L.IsHvn && !HvnOk(L, s.H, s.L, j, u, p)) continue;
                        hit.Add(L.Name);
                    }
                }
                var (names, ng, hv, gold) = Grade(hit, p);
                res.Clusters.Add(new SzZone
                {
                    Lo = lo, Hi = hi, N = pts.Count, NHigh = pts.Count(q => q.Kind > 0), Pmin = pmin, Pmax = pmax,
                    Newest = pts.Max(q => q.I), Oldest = pts.Min(q => q.I), Names = names, NGroup = ng, Hvn = hv, Gold = gold, U = u,
                });
            }
            return res;
        }

        // ---------------------------------------------------------------- hiển thị
        // +1 = hỗ trợ (giá ở trên vùng), −1 = kháng cự; giá đang trong vùng → lùi về nến gần nhất đóng NGOÀI vùng.
        public static int SideOf(IList<double> closes, double lo, double hi, int j, int back)
        {
            for (int i = j; i > Math.Max(j - back, -1); i--)
            {
                if (closes[i] > hi) return 1;
                if (closes[i] < lo) return -1;
            }
            return 0;
        }

        public static string LabelOf(SzZone z, int side)
        {
            string head = side > 0 ? "Hỗ trợ" : side < 0 ? "Kháng cự" : "Vùng";
            if (z.Gold) head = "★ " + head + " rất mạnh";
            var parts = new List<string>();
            foreach (var nm in z.Names) { var t = Ten[nm]; if (!parts.Contains(t)) parts.Add(t); }
            return parts.Count > 0 ? $"{head} · {z.N} lần · {string.Join(" + ", parts)}" : $"{head} · {z.N} lần";
        }

        public static string ColorOf(bool gold, int side) => gold ? "vang" : side > 0 ? "xanh" : side < 0 ? "do" : "xam";

        // Lọc hiển thị + gán phía/màu/nhãn. Rẻ — chạy lại mỗi khi giá đổi. Trả vùng ĐƯỢC VẼ, sắp theo Lo.
        public static List<SzZone> Display(SzResult r, double now, StrongZoneParams p)
        {
            var outp = new List<SzZone>();
            if (r == null || r.Clusters.Count == 0 || double.IsNaN(now)) return outp;
            var pool = r.Clusters.Where(z => z.NGroup >= p.MinGroup).Select(z => z.CloneZone())
                        .OrderBy(z => z.Gold ? 0 : 1).ThenBy(z => -z.NGroup).ThenBy(z => -z.N).ThenBy(z => -z.Newest).ThenBy(z => z.Lo).ToList();
            var kept = new List<SzZone>();
            foreach (var z in pool)
                if (kept.All(k => Math.Max(z.Lo, k.Lo) - Math.Min(z.Hi, k.Hi) >= p.Sep * z.U)) kept.Add(z);
            var cand = new List<SzZone>();
            foreach (var z in kept)
            {
                if (now > z.Hi) { z.Side = 1; z.Dist = now - z.Hi; z.Inside = false; }
                else if (now < z.Lo) { z.Side = -1; z.Dist = z.Lo - now; z.Inside = false; }
                else { z.Side = SideOf(r.Closes, z.Lo, z.Hi, r.J, p.SideLookback); z.Dist = 0; z.Inside = true; }
                if (z.Dist > p.Radius * z.U) continue;
                z.Color = ColorOf(z.Gold, z.Side);
                z.Label = LabelOf(z, z.Side) + (z.Inside ? " (giá đang trong vùng)" : "");
                cand.Add(z);
            }
            outp.AddRange(cand.Where(z => z.Inside));
            foreach (int sd in new[] { 1, -1 })
                outp.AddRange(cand.Where(z => !z.Inside && z.Side == sd).OrderBy(z => z.Gold ? 0 : 1).ThenBy(z => z.Dist).Take(p.MaxSide));
            return outp.OrderBy(z => z.Lo).ToList();
        }

        // Dòng tóm tắt cho Telegram: tối đa 4 vùng, gần giá trước, vùng vàng thêm ★.
        public static string SummaryLine(IList<SzZone> shown, Func<double, string> fmt, int max = 4)
        {
            if (shown == null || shown.Count == 0) return null;
            var parts = shown.OrderBy(z => z.Dist).Take(max)
                .Select(z => $"{(z.Gold ? "★" : "")}{(z.Side > 0 ? "S" : z.Side < 0 ? "R" : "·")} {fmt(z.Lo)}–{fmt(z.Hi)}");
            return "Vùng mạnh (va đập + hợp lưu, chưa kiểm định): " + string.Join(" · ", parts);
        }

        // ---------------------------------------------------------------- hộp HVN (PLAN-VUNG-MANH.md §11, v2 §13.4)
        // Lấy ĐÚNG các hộp hvn_d / hvn_w mà Compute đã tính (không tính lần hai). Bản tham chiếu: vung_manh.hvn_boxes().
        // 1. Ứng viên: đủ "đã rời xa" (HvnOk tại nến j) và mép gần cách giá ≤ HvnRadius × U (giá trong hộp ⇒ 0).
        // 2. Hộp của các profile khác nhau chồng nhau: giữ hộp MỚI hơn (End lớn hơn; cùng End ⇒ hộp ngày trước
        //    hộp tuần, rồi tỉ trọng lớn hơn, rồi Lo nhỏ hơn), bỏ hộp sau nếu phần giao > 50 % bề rộng hộp nhỏ hơn;
        //    hộp bị bỏ khác loại (ngày ↔ tuần) ⇒ nhãn hộp giữ lại thành "HVN ngày + tuần".
        // 3. Giữ mọi hộp đang chứa giá; mỗi phía giá chỉ giữ HvnMaxSide hộp gần nhất ("dưới giá" ⇔ Hi < now).
        // Trả theo Lo tăng dần. Rẻ — chạy lại mỗi khi giá đổi.
        public const string HvnLabelBoth = "HVN ngày + tuần";

        public static List<SzHvnShown> HvnBoxes(SzResult r, double now, StrongZoneParams p)
        {
            var outp = new List<SzHvnShown>();
            if (r == null || r.Levels == null || r.J < 0 || double.IsNaN(r.U) || double.IsNaN(now)) return outp;
            var cand = new List<SzHvnShown>();
            foreach (var lv in r.Levels)
            {
                if (!lv.IsHvn || !HvnOk(lv, r.Highs, r.Lows, r.J, r.U, p)) continue;
                double dist = now > lv.Hi ? now - lv.Hi : now < lv.Lo ? lv.Lo - now : 0;
                if (dist > p.HvnRadius * r.U) continue;
                // vùng đệm được vẽ (§14.3): giá trên/trong hộp ⇒ đệm trên; giá dưới/trong hộp ⇒ đệm dưới. Lọc vẫn theo Lo/Hi.
                double bLo = double.IsNaN(lv.BufLo) ? lv.Lo : lv.BufLo, bHi = double.IsNaN(lv.BufHi) ? lv.Hi : lv.BufHi;
                cand.Add(new SzHvnShown
                {
                    Name = lv.Name, Lo = lv.Lo, Hi = lv.Hi, Peak = lv.Peak, Mass = lv.Mass, Dist = dist, End = lv.End, Src = lv.Src,
                    Label = lv.Name == "hvn_w" ? "HVN tuần" : "HVN ngày",
                    BufLo = now <= lv.Hi ? bLo : lv.Lo,
                    BufHi = now >= lv.Lo ? bHi : lv.Hi,
                });
            }
            foreach (var c in cand.OrderByDescending(x => x.End).ThenBy(x => x.Name == "hvn_d" ? 0 : 1).ThenByDescending(x => x.Mass).ThenBy(x => x.Lo))
            {
                var dup = outp.FirstOrDefault(k =>
                {
                    double inter = Math.Min(k.Hi, c.Hi) - Math.Max(k.Lo, c.Lo);
                    double small = Math.Min(k.Hi - k.Lo, c.Hi - c.Lo);
                    return inter > 0 && inter > 0.5 * small;
                });
                if (dup == null) outp.Add(c);
                else if (dup.Name != c.Name) dup.Label = HvnLabelBoth;   // cùng một cụm thấy ở cả profile ngày lẫn tuần
            }
            var keep = outp.Where(c => c.Dist == 0).ToList();
            foreach (bool below in new[] { true, false })
                keep.AddRange(outp.Where(c => c.Dist > 0 && (c.Hi < now) == below).OrderBy(c => c.Dist).ThenBy(c => c.Lo).Take(Math.Max(0, p.HvnMaxSide)));
            return keep.OrderBy(x => x.Lo).ToList();
        }

        // Chữ trên chart của một hộp HVN: "HVN ngày + tuần · 11 % khối lượng" (tỉ trọng của hộp được giữ).
        public static string HvnBoxText(SzHvnShown b)
            => b == null ? "" : $"{b.Label} · {Math.Round(b.Mass * 100, MidpointRounding.AwayFromZero):0} % khối lượng";

        // Dòng Telegram: tối đa 3 hộp, gần giá trước.
        public static string HvnSummaryLine(IList<SzHvnShown> boxes, Func<double, string> fmt, int max = 3)
        {
            if (boxes == null || boxes.Count == 0) return null;
            return "Hộp HVN (cụm khối lượng, chưa kiểm định): "
                   + string.Join(" · ", boxes.OrderBy(b => b.Dist).Take(max).Select(b => $"{fmt(b.Lo)}–{fmt(b.Hi)} ({b.Label}{BufText(b, fmt)})"));
        }

        // Chữ vùng đệm trong dòng Telegram (§14.4): ", đệm tới <mép ngoài>" (một phía) hoặc ", đệm <dưới>–<trên>" (cả hai phía).
        public static string BufText(SzHvnShown b, Func<double, string> fmt)
        {
            if (b == null) return "";
            bool up = b.BufHi > b.Hi, dn = b.BufLo < b.Lo;
            if (up && dn) return $", đệm {fmt(b.BufLo)}–{fmt(b.BufHi)}";
            if (up) return $", đệm tới {fmt(b.BufHi)}";
            if (dn) return $", đệm tới {fmt(b.BufLo)}";
            return "";
        }

        // Cửa sổ history chuẩn hoá: chỉ dùng nến có TimeLeft ≥ (nến cuối − days ngày). M30 chính và M30 phụ
        // có độ dài history khác nhau; cắt về cùng cửa sổ ⇒ cùng đầu vào ⇒ cùng vùng.
        public static int CanonicalStart(IList<DateTime> t, int days)
        {
            if (t == null || t.Count == 0) return 0;
            var from = t[t.Count - 1].AddDays(-Math.Abs(days));
            for (int i = 0; i < t.Count; i++) if (t[i] >= from) return i;
            return t.Count - 1;
        }
    }

    // Bộ đệm: cấu trúc vùng chỉ tính lại khi có nến M30 mới (khoá = số nến + giờ nến đầu, nến j, nến cuối
    // + mọi thông số). Mỗi tick chỉ chạy Display với giá mới.
    public sealed class StrongZoneEngine
    {
        public int Recomputes { get; private set; }
        private string _key;
        private SzResult _res;
        private readonly Dictionary<string, (List<SzLevel> lv, bool apx)> _lvCache = new Dictionary<string, (List<SzLevel> lv, bool apx)>();

        public static string KeyOf(int n, DateTime first, DateTime barJ, DateTime last, StrongZoneParams p)
            => n + "|" + first.Ticks + "|" + barJ.Ticks + "|" + last.Ticks + "|" + p.Fingerprint();

        public SzResult Structure(string key, Func<SzSeries> build, StrongZoneParams p)
        {
            if (key == _key && _res != null) return _res;
            var s = build();
            _res = s == null ? new SzResult() : StrongZones.Compute(s, p, _lvCache);
            _key = key; Recomputes++;
            return _res;
        }

        public void Reset() { _key = null; _res = null; _lvCache.Clear(); }
    }

    // Vẽ vùng mạnh — dùng chung cho OnPaintChart (Quantower) và test render ra PNG.
    public static class StrongZonePainter
    {
        public static Color ColorOf(SzZone z, Color sup, Color res, Color gold)
            => z.Color == "vang" ? gold : z.Color == "xanh" ? sup : z.Color == "do" ? res : Color.FromArgb(0x9E, 0x9E, 0x9E);

        public static int FillAlpha(SzZone z) => z.Gold ? 70 : 40;

        // Chỉ nhãn — bỏ phần "cách n giá" theo yêu cầu người dùng (2026-11-25).
        public static string TextOf(SzZone z, double tick) => z.Label;

        // Vị trí Y của nhãn (góc trên chữ). Ưu tiên nằm giữa dải; dải mỏng hơn chữ thì đặt ngay TRÊN dải.
        // Sau đó đẩy cho các nhãn không đè nhau (cách nhau ≥ textH) và kẹp trong [clipTop, clipBot].
        public static float[] LayoutLabels(IList<(float top, float bot)> bands, float textH, float clipTop, float clipBot)
        {
            int n = bands?.Count ?? 0;
            var y = new float[n];
            if (n == 0) return y;
            var pref = new float[n];
            for (int i = 0; i < n; i++)
            {
                float t = Math.Min(bands[i].top, bands[i].bot), b = Math.Max(bands[i].top, bands[i].bot);
                pref[i] = (b - t >= textH) ? t + (b - t - textH) / 2f : t - textH - 1f;
            }
            var order = Enumerable.Range(0, n).OrderBy(i => pref[i]).ToArray();
            float prev = float.NegativeInfinity;
            foreach (int i in order) { y[i] = Math.Max(Math.Max(pref[i], clipTop), prev + textH); prev = y[i]; }
            float limit = clipBot;
            for (int k = order.Length - 1; k >= 0; k--)
            {
                int i = order[k];
                if (y[i] + textH > limit) y[i] = limit - textH;
                limit = y[i];
            }
            return y;
        }

        // Hộp HVN: nền rất nhạt (cam nhạt trên nền tối) + viền liền rõ, để nhìn ra "thân" mà không lấn vùng mạnh.
        public const int HvnFillAlpha = 30, HvnEdgeAlpha = 220;
        // Vùng đệm (§14.4): cùng màu hộp, nền bằng nửa độ đậm hộp, không viền, nét đứt 1 px ở mép ngoài.
        public const int HvnBufFillAlpha = 14, HvnBufEdgeAlpha = 110;

        // Vẽ hộp HVN (dưới) rồi vùng mạnh (trên); nhãn của CẢ HAI xếp chung bằng LayoutLabels ⇒ không đè nhau.
        public static void Paint(Graphics g, Rectangle clip, Func<double, float> toY, IList<SzZone> zones,
                                 Color sup, Color res, Color gold, double tick, Font font,
                                 IList<SzHvnShown> hvnBoxes = null, Color hvnColor = default)
        {
            if (g == null) return;
            zones ??= new List<SzZone>();
            var boxes = new List<(SzHvnShown b, float top, float bot)>();
            if (hvnBoxes != null)
                foreach (var b in hvnBoxes)
                {
                    float y1 = toY(b.Lo), y2 = toY(b.Hi);
                    float top = Math.Min(y1, y2), bot = Math.Max(y1, y2);
                    if (bot < clip.Top || top > clip.Bottom) continue;
                    boxes.Add((b, top, bot));
                }
            var vis = new List<(SzZone z, float top, float bot, Color col)>();
            foreach (var z in zones)
            {
                float y1 = toY(z.Lo), y2 = toY(z.Hi);
                float top = Math.Min(y1, y2), bot = Math.Max(y1, y2);
                if (bot < clip.Top || top > clip.Bottom) continue;
                vis.Add((z, top, bot, ColorOf(z, sup, res, gold)));
            }
            // vùng đệm vẽ TRƯỚC hộp (nằm dưới cùng); không nhãn, không tham gia LayoutLabels

            if (hvnBoxes != null)
                using (var bfill = new SolidBrush(Color.FromArgb(HvnBufFillAlpha, hvnColor)))
                using (var dash = new Pen(Color.FromArgb(HvnBufEdgeAlpha, hvnColor), 1f) { DashStyle = System.Drawing.Drawing2D.DashStyle.Dash })
                    foreach (var b in hvnBoxes)
                    {
                        if (b.BufHi > b.Hi) PaintBuf(g, clip, bfill, dash, toY(b.Hi), toY(b.BufHi));
                        if (b.BufLo < b.Lo) PaintBuf(g, clip, bfill, dash, toY(b.Lo), toY(b.BufLo));
                    }
            if (vis.Count == 0 && boxes.Count == 0) return;
            foreach (var b in boxes)
            {
                float h = Math.Max(1f, b.bot - b.top);
                using (var fill = new SolidBrush(Color.FromArgb(HvnFillAlpha, hvnColor)))
                    g.FillRectangle(fill, clip.Left, b.top, clip.Width, h);
                using (var pen = new Pen(Color.FromArgb(HvnEdgeAlpha, hvnColor), 1f))
                    g.DrawRectangle(pen, clip.Left, b.top, clip.Width - 1, h);
            }
            foreach (var v in vis)
            {
                float h = Math.Max(1f, v.bot - v.top);
                using (var fill = new SolidBrush(Color.FromArgb(FillAlpha(v.z), v.col)))
                    g.FillRectangle(fill, clip.Left, v.top, clip.Width, h);
                using (var pen = new Pen(Color.FromArgb(160, v.col), 1f))
                {
                    g.DrawLine(pen, clip.Left, v.top, clip.Right, v.top);
                    g.DrawLine(pen, clip.Left, v.top + h, clip.Right, v.top + h);
                }
            }
            float textH = font.GetHeight(g) + 1f;
            var labels = vis.Select(v => (txt: TextOf(v.z, tick), v.top, v.bot, col: v.col))
                            .Concat(boxes.Select(b => (txt: StrongZones.HvnBoxText(b.b), b.top, b.bot, col: hvnColor))).ToList();
            var ys = LayoutLabels(labels.Select(v => (v.top, v.bot)).ToList(), textH, clip.Top, clip.Bottom);
            for (int i = 0; i < labels.Count; i++)
            {
                string txt = labels[i].txt;
                var sz = g.MeasureString(txt, font);
                float x = clip.Right - sz.Width - 6f;
                using (var bg = new SolidBrush(Color.FromArgb(215, 16, 16, 20)))
                    g.FillRectangle(bg, x - 2f, ys[i], sz.Width + 4f, textH);
                using (var br = new SolidBrush(labels[i].col))
                    g.DrawString(txt, font, br, x, ys[i]);
            }
        }

        // Một dải đệm: tô từ mép hộp (yEdge) tới mép ngoài (yOuter), nét đứt ở mép ngoài. Trả true nếu có vẽ.
        static bool PaintBuf(Graphics g, Rectangle clip, Brush fill, Pen dash, float yEdge, float yOuter)
        {
            float top = Math.Min(yEdge, yOuter), bot = Math.Max(yEdge, yOuter);
            if (bot < clip.Top || top > clip.Bottom) return false;
            g.FillRectangle(fill, clip.Left, top, clip.Width, Math.Max(1f, bot - top));
            if (yOuter >= clip.Top && yOuter <= clip.Bottom) g.DrawLine(dash, clip.Left, yOuter, clip.Right, yOuter);
            return true;
        }
    }

    // ============================================================================
    //  VÙNG CỤM VOL (2026-11-25, research/vung_quan_trong_2026-11-25/KET-QUA-20-VONG-VE-SAN.md, cz_ref.py) — CHƯA KIỂM ĐỊNH
    //  Mỗi phiên ngày đã đóng (3 phiên gần nhất, ≥ 20 nến M30): 1 cụm khối lượng nặng nhất của profile cố định
    //  (làm mượt ± 0,1 U15, đỉnh ≥ 1,5 × TB hàng, dải = hàng liên tục còn ≥ 70 % đỉnh). Dải chồng/sát (≤ 0,1 U15) ⇒ gộp.
    //  Trạng thái chạy trên nến M15 từ đầu phiên nguồn: chỉ HIỆN khi giá đã rời dải ≥ 3 U15 trong ≤ 8 nến M15 và mới tới gần
    //  ≤ 1 lần (lần sắp tới là lần 1 hoặc 2); hoặc đang trong một lần chạm hợp lệ (hết khi giá cách dải ≥ 1 U15).
    //  Rời lên = hỗ trợ, rời xuống = kháng cự. U15 = TB (H − L) nến M15 của 5 phiên trước. Port 1:1 từ cz_ref.py (test C# = Python).
    // ============================================================================
    public sealed class CzParams
    {
        public double Sm = 0.10, Ratio = 1.5, Frac = 0.70, GapM = 0.10, Imp = 3.0, Trig = 0.6, Away = 1.25, Rearm = 1.0;
        public int NDays = 3, MinBars30 = 20, SessGapMin = 60, UDays = 5, KBars = 8, MaxTouch = 2;
    }

    public sealed class CzBar { public DateTime T; public double H, L, C; }

    public sealed class CzDay
    {
        public DateTime T0; public int N30;
        public double[] Prices, Vols;      // hàng profile (giá thật, bội số rowStep)
    }

    public sealed class CzZone
    {
        public double Lo, Hi, Imp;
        public int Side, Touch, Nm;        // Side +1 hỗ trợ / −1 kháng cự; Touch = lần chạm (sắp tới hoặc đang chạm)
        public bool Live;                  // đang trong lần chạm
        public DateTime? EpT;              // nến M15 bắt đầu lần chạm đang diễn ra
        public List<DateTime> Days = new List<DateTime>();
        public string Desc;                // thành phần vùng, vd "HVN ngày 24/11 + HVN tuần + VWAP tuần" (Describe)
    }

    public static class ClusterZones
    {
        public static int[] Sessions(IList<CzBar> b, int gapMin)
        {
            var s = new int[b.Count];
            for (int i = 1; i < b.Count; i++) s[i] = s[i - 1] + ((b[i].T - b[i - 1].T).TotalMinutes > gapMin ? 1 : 0);
            return s;
        }

        public static double U15(IList<CzBar> b, int[] sess, int k, int nd)
        {
            int lo = Math.Max(0, k - nd);
            if (k - lo < 2) return double.NaN;
            double sum = 0; int n = 0;
            for (int i = 0; i < b.Count; i++) if (sess[i] >= lo && sess[i] < k) { sum += b[i].H - b[i].L; n++; }
            return n > 0 ? sum / n : double.NaN;
        }

        // 1 cụm nặng nhất: (lo, hi, peak, ratio) hoặc null.
        public static (double lo, double hi, double peak, double ratio)? Cluster(double[] prices, double[] vols, double u, double row, CzParams p)
        {
            if (prices == null || prices.Length < 5 || double.IsNaN(u) || u <= 0) return null;
            var idx = new long[prices.Length];
            long mn = long.MaxValue, mx = long.MinValue;
            for (int i = 0; i < prices.Length; i++) { idx[i] = (long)Math.Round(prices[i] / row); mn = Math.Min(mn, idx[i]); mx = Math.Max(mx, idx[i]); }
            int n = (int)(mx - mn + 1);
            var W = new double[n];
            for (int i = 0; i < prices.Length; i++) W[idx[i] - mn] += vols[i];
            int kk = Math.Max(1, (int)Math.Floor(p.Sm * u / row + 0.5));
            var cs = new double[n + 1];
            for (int i = 0; i < n; i++) cs[i + 1] = cs[i] + W[i];
            var sm = new double[n];
            for (int i = 0; i < n; i++) { int a = Math.Max(0, i - kk), z = Math.Min(n - 1, i + kk); sm[i] = (cs[z + 1] - cs[a]) / (z - a + 1); }
            double tot = 0; int nz = 0;
            for (int i = 0; i < n; i++) if (W[i] > 0) { tot += W[i]; nz++; }
            if (nz == 0) return null;
            double avg = tot / nz;
            int best = -1;
            for (int i = 1; i < n - 1; i++)
                if (sm[i] >= sm[i - 1] && sm[i] >= sm[i + 1] && sm[i] >= p.Ratio * avg)
                    if (best < 0 || sm[i] > sm[best]) best = i;
            if (best < 0) return null;
            double thr = p.Frac * sm[best]; int l2 = best, h2 = best;
            while (l2 > 0 && sm[l2 - 1] >= thr) l2--;
            while (h2 < n - 1 && sm[h2 + 1] >= thr) h2++;
            int ipk = l2;
            for (int i = l2; i <= h2; i++) if (W[i] > W[ipk]) ipk = i;
            return ((mn + l2) * row, (mn + h2) * row, (mn + ipk) * row, sm[best] / avg);
        }

        public sealed class State { public int Side, Nt, Ep, EpNt, EpI = -1, LastIn = -1; public double Imp; public bool Armed; }

        // Bộ máy trạng thái trên nến M15 [s0..e] — đúng cz_ref.run_state.
        public static State Run(IList<CzBar> b, double lo, double hi, int s0, int e, double u, CzParams p)
        {
            int lastIn = -1, side = 0, nt = 0, ep = 0, epNt = 0, epI = -1; double imp = 0, aw = 0; bool ready = false;
            for (int i = s0; i <= e; i++)
            {
                double h = b[i].H, l = b[i].L;
                if (l <= hi && h >= lo) { lastIn = i; side = 0; imp = 0; nt = 0; aw = 0; ready = false; continue; }
                int cs = l > hi ? 1 : -1;
                if (side != cs) { if (side != 0) lastIn = i; side = cs; imp = 0; nt = 0; aw = 0; ready = false; }
                double near = cs > 0 ? l - hi : lo - h;
                double far = cs > 0 ? h - hi : lo - l;
                if (ep != 0 && far >= p.Rearm * u) ep = 0;
                if (near <= p.Trig * u)
                {
                    if (ready)
                    {
                        if (lastIn >= 0 && imp >= p.Imp * u && nt < p.MaxTouch) { ep = cs; epNt = nt + 1; epI = i; }
                        nt++;
                    }
                    ready = false; aw = 0;
                    continue;
                }
                aw = Math.Max(aw, far);
                if (lastIn >= 0 && i - lastIn <= p.KBars) imp = Math.Max(imp, far);
                if (!ready && aw >= (nt == 0 ? p.Away : p.Rearm) * u) ready = true;
            }
            return new State { Side = side, Imp = imp / u, Nt = nt, Ep = ep, EpNt = epNt, EpI = ep != 0 ? epI : -1, LastIn = lastIn,
                               Armed = lastIn >= 0 && side != 0 && imp >= p.Imp * u && nt < p.MaxTouch };
        }

        // Vùng hiện tại nến cuối của bars. days: profile phiên ngày theo thời gian (có thể gồm phiên đang chạy — tự bỏ).
        public static List<CzZone> Compute(IList<CzBar> bars, IList<CzDay> days, double row, CzParams p, out double u)
        {
            u = double.NaN;
            var res = new List<CzZone>();
            int e = (bars?.Count ?? 0) - 1;
            if (e < 1 || days == null) return res;
            var sess = Sessions(bars, p.SessGapMin);
            int k = sess[e];
            u = U15(bars, sess, k, p.UDays);
            if (double.IsNaN(u) || u <= 0) return res;
            DateTime curT0 = bars[e].T;
            for (int i = 0; i <= e; i++) if (sess[i] == k) { curT0 = bars[i].T; break; }
            var src = new List<(double lo, double hi, int s0, List<DateTime> days)>();
            int got = 0;
            for (int di = days.Count - 1; di >= 0; di--)
            {
                var d = days[di];
                if (d.T0 >= curT0 || d.N30 < p.MinBars30) continue;
                got++;
                var cl = Cluster(d.Prices, d.Vols, u, row, p);
                int s0 = LowerBound(bars, d.T0);
                if (cl.HasValue && s0 <= e) src.Add((cl.Value.lo, cl.Value.hi, s0, new List<DateTime> { d.T0 }));
                if (got >= p.NDays) break;
            }
            var sorted = src.Select((z, i) => (z, i)).OrderBy(x => x.z.lo).ThenBy(x => x.z.hi).ThenBy(x => x.i).Select(x => x.z).ToList();
            var mg = new List<(double lo, double hi, int s0, List<DateTime> days, int nm)>();
            foreach (var z in sorted)
            {
                if (mg.Count > 0 && z.lo <= mg[mg.Count - 1].hi + p.GapM * u)
                {
                    var m = mg[mg.Count - 1];
                    m.days.AddRange(z.days);
                    mg[mg.Count - 1] = (m.lo, Math.Max(m.hi, z.hi), Math.Min(m.s0, z.s0), m.days, m.nm + 1);
                }
                else mg.Add((z.lo, z.hi, z.s0, new List<DateTime>(z.days), 1));
            }
            foreach (var z in mg)
            {
                var st = Run(bars, z.lo, z.hi, z.s0, e, u, p);
                int side, touch; bool live;
                if (st.Ep != 0) { side = st.Ep; touch = st.EpNt; live = true; }
                else if (st.Armed) { side = st.Side; touch = st.Nt + 1; live = false; }
                else continue;
                res.Add(new CzZone { Lo = z.lo, Hi = z.hi, Side = side, Touch = touch, Live = live, Nm = z.nm, Imp = st.Imp,
                                     Days = z.days.OrderBy(x => x).ToList(), EpT = live ? bars[st.EpI].T : (DateTime?)null });
            }
            return res;
        }

        static int LowerBound(IList<CzBar> b, DateTime t)
        {
            int lo = 0, hi = b.Count;
            while (lo < hi) { int m = (lo + hi) / 2; if (b[m].T < t) lo = m + 1; else hi = m; }
            return lo;
        }

        public static string SideText(int side) => side > 0 ? "hỗ trợ" : "kháng cự";

        // Thành phần vùng: "HVN ngày 24/11 + 23/11", cộng các mức khác nằm trong vùng (± 0,1 U15), theo thứ tự extras
        // (vd HVN tuần, VWAP tuần, VWAP ngày). Mức dạng đường: lo = hi.
        public static string Describe(CzZone z, IList<(string name, double lo, double hi)> extras, double u, int tzOffset)
        {
            var parts = new List<string> { "HVN ngày " + string.Join(" + ", z.Days.Select(d => d.AddHours(tzOffset).ToString("dd/MM"))) };
            double tol = double.IsNaN(u) ? 0 : 0.1 * u;
            if (extras != null)
                foreach (var x in extras)
                    if (!double.IsNaN(x.lo) && !double.IsNaN(x.hi) && x.lo <= z.Hi + tol && x.hi >= z.Lo - tol && !parts.Contains(x.name)) parts.Add(x.name);
            return string.Join(" + ", parts);
        }

        // Nhãn trên chart: "HVN ngày 24/11 + VWAP tuần · hỗ trợ · chờ chạm lần 1" (đang chạm: "đang chạm lần 1").
        public static string Label(CzZone z, int tzOffset)
        {
            string desc = z.Desc ?? Describe(z, null, double.NaN, tzOffset);
            return $"{desc} · {SideText(z.Side)} · {(z.Live ? "đang chạm" : "chờ chạm")} lần {z.Touch}";
        }

        // Khoá chống gửi trùng cho một lần chạm: symbol + phía + nến M15 bắt đầu lần chạm.
        public static string TouchKey(string symbol, CzZone z)
            => z.EpT.HasValue ? $"{symbol}|{z.Side}|{z.EpT.Value.Ticks}" : null;

        // Có nên báo Telegram: đang chạm, nến bắt đầu lần chạm còn mới (≤ freshMin phút so với giờ thật), khoá chưa gửi.
        public static bool ShouldAlert(CzZone z, DateTime utcNow, int freshMin, ISet<string> sent, string symbol)
        {
            if (z == null || !z.Live || !z.EpT.HasValue) return false;
            if ((utcNow - z.EpT.Value).TotalMinutes > freshMin) return false;
            var key = TouchKey(symbol, z);
            return key != null && (sent == null || !sent.Contains(key));
        }

        // Tin chạm vùng (mẫu người dùng 2026-11-26): "NQZ26: giá chạm vùng kháng cự 25540–25610 – HVN tuần + VWAP tuần, canh sell".
        public static string AlertText(string symbol, CzZone z, Func<double, string> fmt, int tzOffset)
        {
            string desc = z.Desc ?? Describe(z, null, double.NaN, tzOffset);
            return $"{symbol}: giá chạm vùng {SideText(z.Side)} {fmt(z.Lo)}–{fmt(z.Hi)} – {desc}, canh {(z.Side > 0 ? "buy" : "sell")}";
        }
    }
}
