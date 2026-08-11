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
                if ((DateTime.UtcNow - _cacheUtc).TotalMinutes < 60 && _cache != null) return;
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

        // ---- Parser JSON tối giản: feed là mảng object, mọi giá trị đều là chuỗi ----
        private static List<Ev> Parse(string json, int tzOffset)
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
                bool keep = (ccy == "USD" && (imp == "High" || imp == "Medium"))
                         || ((ccy == "EUR" || ccy == "GBP") && imp == "High");
                if (!keep) continue;
                string date = Get(fields, "date");
                var ev = new Ev
                {
                    Title = Get(fields, "title"), Ccy = ccy, Impact = imp,
                    Forecast = Get(fields, "forecast"), Previous = Get(fields, "previous")
                };
                if (DateTimeOffset.TryParse(date, out var dto))
                    ev.WhenVn = dto.UtcDateTime.AddHours(tzOffset);
                else if (DateTime.TryParse(date.Length >= 10 ? date.Substring(0, 10) : date, out var d0))
                { ev.WhenVn = d0; ev.AllDay = true; }
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

        // Dòng lịch tin chèn vào tin Telegram. preUsOnly = chỉ tin còn LẠI từ giờ trở đi.
        public static List<string> Lines(DateTime nowVn, bool preUsOnly)
        {
            var outp = new List<string>();
            List<Ev> src;
            lock (Gate) src = _cache;
            if (src == null) return outp;
            var day = nowVn.Date;
            var sel = new List<Ev>();
            foreach (var e in src)
            {
                if (e.WhenVn.Date != day) continue;
                if (preUsOnly && !e.AllDay && e.WhenVn < nowVn) continue;
                sel.Add(e);
            }
            if (sel.Count == 0)
            {
                outp.Add(preUsOnly ? "📅 TIN: không còn tin Mỹ nào hôm nay → chạy theo dòng lệnh."
                                   : "📅 TIN HÔM NAY: không có tin USD đáng kể.");
                return outp;
            }
            outp.Add(preUsOnly ? "📅 TIN CÒN LẠI HÔM NAY:" : "📅 TIN HÔM NAY:");
            foreach (var e in sel)
            {
                string hhmm = e.AllDay ? "cả ngày" : e.WhenVn.ToString("HH:mm");
                string fc = string.IsNullOrEmpty(e.Forecast) ? "-" : e.Forecast;
                string pv = string.IsNullOrEmpty(e.Previous) ? "-" : e.Previous;
                outp.Add($"  {hhmm} {Label(e)} {e.Title} (dự báo {fc} / trước {pv})");
            }
            outp.Add("  ⚠ Né 15' trước–sau mốc tin: không vào lệnh mới, siết SL.");
            return outp;
        }
    }

    // ---- Gửi "tổng hợp" lên Telegram (dùng chung cho DailyTpoBias + M30SessionZones) --------
    //  Mỗi indicator GHI phần của mình ra file chung (sec_<symbol>_<kind>.txt). Indicator nào
    //  có bot token + chat id sẽ GỘP các phần (bias + zone) thành 1 tin và bắn tại 3 mốc/ngày:
    //    • MORNING   : ngày phát triển vừa đủ nến qua IB (đủ bias) — cửa sổ vài nến sau IB.
    //    • AFTERNOON : mốc giờ cố định buổi chiều (mặc định 14:00 VN — quanh giờ Âu vào).
    //    • PREUS     : trước giờ phiên Mỹ mở PreUsMin phút.
    //  Chống gửi trùng bằng FILE KHOÁ tạo NGUYÊN TỬ (FileMode.CreateNew) theo ngày+mốc → dù
    //  cả 2 indicator (hoặc 2 chart) cùng cầm token cũng chỉ 1 tin/mốc/ngày. Chỉ chạy khi dữ
    //  liệu LIVE (nến cuối gần giờ thực → chart lịch sử không bắn nhầm). HTTP chạy nền (Task).
    internal sealed class TeleReport
    {
        public bool Enabled, TestNow;
        // Nhiều chart/tab có thể cùng add 1 indicator trên cùng symbol (vd SessionZones
        // gắn cả M30 + 2 tab M1) — mỗi instance đều cố gắng bắn Telegram, dễ ra NHIỀU tin
        // cùng lúc nếu cấu hình (TzOffset/GapMinutes) lệch nhau giữa các tab dù cùng
        // symbol → khoá lock khác nhau. Chỉ 1 instance (bật IsSender=true) mới thực sự
        // kiểm mốc + gửi; các instance khác vẫn ghi section (để Compose gộp) nhưng
        // không tự bắn tin.
        public bool IsSender = true;
        public string BotToken = "", ChatId = "", ShareDir = "";
        public int TzOffset = 7;
        public int UsStartMin = 1160;      // 19:20 VN (COMEX vàng mở pit)
        public int PreUsMin = 30;
        public int AfternoonMin = 840;     // 14:00 VN — tổng hợp giữa ngày (0 = tắt)
        public int MorningGraceBars = 6;   // sau IB còn được bắn "báo sáng" trong bao nhiêu nến
        public int IbBars = 2;
        public int GapMinutes = 75;
        public int FreshMinutes = 15;      // section/nến cũ hơn ngần này coi như KHÔNG live
        public bool ShowNews = true;       // kèm lịch tin Forex Factory (đầu ngày + trước phiên Mỹ)

        private static readonly HttpClient Http = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
        private long _lastPubTicks, _lastCheckTicks;
        private bool _lastTest;

        // Gọi 1 lần cuối mỗi Process(): ghi section của indicator này + kiểm mốc để gửi.
        public void Run(HistoricalData hd, string symbol, string kind, IReadOnlyList<string> lines)
        {
            if (!Enabled || hd == null) return;
            try
            {
                PublishSection(symbol, kind, lines);
                if (!IsSender) return;
                if (ShowNews) NewsCalendar.Refresh(Dir(), TzOffset, Log);   // tải nền, có cache 1h
                if (string.IsNullOrWhiteSpace(BotToken) || string.IsNullOrWhiteSpace(ChatId)) return;

                long now = DateTime.UtcNow.Ticks;
                if (now - _lastCheckTicks < 15 * TimeSpan.TicksPerSecond) return;   // ~15s/lần
                _lastCheckTicks = now;
                CheckTriggers(hd, symbol);
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
            SendAsync(Compose(symbol, "🔔 TEST — bot TPO chạy OK", "MORNING"), null);
        }

        // ===== Dùng cho indicator KHÁC (vd RunnerSignal): gửi 1 tin THÔ, KHÔNG đụng section/lock TPO =====
        // Chỉ tái dùng HttpClient + đường log chung. Không có Compose/CheckTriggers ở đây.
        public void SendRaw(string text)
        {
            if (!Enabled) return;
            SendAsync(text, null);
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

        private void PublishSection(string symbol, string kind, IReadOnlyList<string> lines)
        {
            if (lines == null || lines.Count == 0) return;
            long now = DateTime.UtcNow.Ticks;
            if (now - _lastPubTicks < 30 * TimeSpan.TicksPerSecond) return;   // giảm ghi đĩa
            _lastPubTicks = now;
            var sb = new StringBuilder();
            foreach (var l in lines) sb.Append(l).Append('\n');
            try { File.WriteAllText(Path.Combine(Dir(), $"sec_{Safe(symbol)}_{kind}.txt"), sb.ToString()); } catch { }
        }

        private void CheckTriggers(HistoricalData hd, string symbol)
        {
            int n = hd.Count; if (n == 0) return;
            // Dữ liệu có LIVE không? Nến cuối phải gần giờ thực (nến M30 đang tạo cũ tối đa ~30').
            if (hd[n - 1, SeekOriginHistory.Begin] is not HistoryItemBar lastBar) return;
            if ((DateTime.UtcNow - lastBar.TimeLeft).TotalMinutes > 60) return;

            var groups = ProfileEngine.GroupByGap(hd, GapMinutes);
            if (groups.Count == 0) return;
            var dg = groups[groups.Count - 1];                 // ngày đang phát triển
            int devBars = dg.to - dg.from + 1;
            if (hd[dg.from, SeekOriginHistory.Begin] is not HistoryItemBar firstBar) return;
            string dayKey = firstBar.TimeLeft.AddHours(TzOffset).ToString("yyyyMMdd");
            int nowMin = (int)DateTime.UtcNow.AddHours(TzOffset).TimeOfDay.TotalMinutes;

            // MORNING — IB xong, còn trong cửa sổ vài nến sau IB (mở chart giữa ngày sẽ KHÔNG bắn)
            if (devBars >= IbBars && devBars <= IbBars + MorningGraceBars)
                TrySend(symbol, dayKey, "MORNING", "☀️ TỔNG HỢP ĐẦU NGÀY");

            // AFTERNOON — mốc giờ cố định buổi chiều, cửa sổ 20' (0 = tắt)
            if (AfternoonMin > 0 && nowMin >= AfternoonMin && nowMin <= AfternoonMin + 20)
                TrySend(symbol, dayKey, "AFTERNOON", "🌤 TỔNG HỢP BUỔI CHIỀU");

            // PREUS — trong 20' kể từ mốc (giờ phiên Mỹ − PreUsMin)
            int trig = UsStartMin - PreUsMin;
            if (nowMin >= trig && nowMin <= trig + 20)
                TrySend(symbol, dayKey, "PREUS", "🇺🇸 CHUẨN BỊ PHIÊN MỸ (30')");
        }

        private void TrySend(string symbol, string dayKey, string slot, string header)
        {
            string lockPath = Path.Combine(Dir(), $"sent_{Safe(symbol)}_{dayKey}_{slot}.lock");
            if (File.Exists(lockPath)) return;
            try { using (new FileStream(lockPath, FileMode.CreateNew, FileAccess.Write, FileShare.None)) { } }
            catch { return; }   // ai đó đã chiếm mốc này
            Log($"{slot} → đang gửi (ngày {dayKey})");
            SendAsync(Compose(symbol, header, slot), lockPath);   // gửi lỗi → xoá khoá để lần sau thử lại
        }

        private string Compose(string symbol, string header, string slot)
        {
            var sb = new StringBuilder();
            sb.Append(header).Append(" · ").Append(symbol ?? "").Append(" · ")
              .Append(DateTime.UtcNow.AddHours(TzOffset).ToString("dd/MM HH:mm")).Append('\n');
            sb.Append("————————————\n");
            string dir = Dir();
            bool any = false;
            foreach (var kind in new[] { "bias", "zone" })   // bias trước, zone sau
            {
                string path = Path.Combine(dir, $"sec_{Safe(symbol)}_{kind}.txt");
                if (!File.Exists(path)) continue;
                try
                {
                    if ((DateTime.UtcNow - new FileInfo(path).LastWriteTimeUtc).TotalMinutes > FreshMinutes) continue;
                    string body = File.ReadAllText(path).TrimEnd();
                    if (body.Length == 0) continue;
                    if (any) sb.Append('\n');
                    sb.Append(body).Append('\n');
                    any = true;
                }
                catch { }
            }
            if (!any) sb.Append("(chưa có dữ liệu bias/vùng — mở indicator lên chart)");

            // Lịch tin: đầu ngày liệt kê cả ngày; trước phiên Mỹ chỉ nhắc tin CÒN LẠI.
            // Mốc buổi chiều bỏ qua cho tin gọn.
            if (ShowNews && (slot == "MORNING" || slot == "PREUS"))
            {
                var news = NewsCalendar.Lines(DateTime.UtcNow.AddHours(TzOffset), slot == "PREUS");
                if (news.Count > 0)
                {
                    sb.Append("\n————————————\n");
                    foreach (var l in news) sb.Append(l).Append('\n');
                }
            }
            return sb.ToString().TrimEnd();
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
}
