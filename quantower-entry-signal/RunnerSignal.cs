// ============================================================================
//  RunnerSignal  —  Tín hiệu RUNNER CBR (Consolidation→Break→Retest→Resume) M1 (QUANTOWER)
// ============================================================================
//  Mô hình LITERAL của user rút từ 6 setup thật: "phá VÙNG CO, chờ HỒI (giữ trên
//  gốc phá), VÀO nến TIẾP DIỄN". TP 3R (giữ runner). KHÁC con scalp EntrySignal
//  (phá vùng→retest, 1.5R) — đây là chiến lược riêng, chạy song song, DLL riêng.
//
//  Neo = RANGE nội bộ (RangeLen nến trước, span trong [RangeMin..RangeMax] = vùng
//  co hẹp thật, KHÔNG phải zone profile). BREAK = nến đóng vượt cạnh range + VSA
//  climax(≥2.0) + thân mạnh. HOLD = trong WaitBars nến giá hồi nhưng GIỮ (không đóng
//  lại hẳn trong range). RESUME = nến đóng vượt cực trị nhịp hồi → vào tại close.
//  SL = cực trị nhịp hồi ± buf (sàn 3đ, trần 7đ). Chỉ bắn NẾN ĐÃ ĐÓNG (không repaint).
//
//  Logic KHỚP research/entry_cbr.py (backtest 28 ngày: net +37R@3R, WR 32%, 127 lệnh,
//  bắt 4/6 GT). Bias EMA TẮT (lọc nhầm → dùng TPO bias khi vào lệnh thật). Vùng hợp
//  lưu (co_vung) và TP-vướng-vùng CHỈ là thông tin hiển thị — KHÔNG lọc bỏ tín hiệu
//  (test cho thấy hard-loại đều GIẢM net). Build: build-runner.sh (concat ProfileEngine).
// ============================================================================
namespace RunnerSignal
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Text;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;   // ProfileEngine + PanelDrag (concat)

    public class RunnerSignal : Indicator, IVolumeAnalysisIndicator
    {
        // ---------- giờ phiên (để dựng vùng hiển thị hợp lưu) ----------
        [InputParameter("Lệch giờ (bar.TimeLeft UTC → local)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Á bắt đầu (phút/ngày)", 11, 0, 1439, 5, 0)]
        public int AsiaStart { get; set; } = 300;
        [InputParameter("Âu bắt đầu (phút/ngày)", 12, 0, 1439, 5, 0)]
        public int EuropeStart { get; set; } = 750;
        [InputParameter("Mỹ bắt đầu (phút/ngày)", 13, 0, 1439, 5, 0)]
        public int UsStart { get; set; } = 1140;

        // ---------- profile / vùng (chỉ để hiển thị hợp lưu + info TP-vướng-vùng) ----------
        [InputParameter("Số tick / hàng profile", 20, 1, 50, 1, 0)]
        public int RowTicks { get; set; } = 1;
        [InputParameter("Gap tách phiên (phút)", 21, 20, 240, 1, 0)]
        public int SessionGapMin { get; set; } = 40;
        [InputParameter("Gap tách ngày (phút)", 22, 20, 240, 1, 0)]
        public int DayGapMin { get; set; } = 45;
        [InputParameter("Số ngày vùng còn hiệu lực", 24, 1, 10, 1, 0)]
        public int ZoneExpireDays { get; set; } = 3;
        [InputParameter("Dung sai hợp lưu (tick)", 30, 1, 30, 1, 0)]
        public int ConfluenceTol { get; set; } = 7;
        [InputParameter("Số vùng hợp lưu tối thiểu (chỉ để chấm A-grade)", 32, 1, 5, 1, 0)]
        public int MinConfluence { get; set; } = 2;

        // ---------- VSA (khớp VsaVolume: SMA gồm nến hiện tại) ----------
        [InputParameter("VSA period (SMA volume, gồm nến này)", 40, 5, 200, 1, 0)]
        public int VsaPeriod { get; set; } = 20;
        [InputParameter("VSA climax tím (× TB)", 42, 0.5, 8, 0.05, 2)]
        public double VsaClimax { get; set; } = 2.2;

        // ---------- CBR: RANGE ----------
        [InputParameter("Range: số nến trước break", 50, 3, 30, 1, 0)]
        public int RangeLen { get; set; } = 8;
        [InputParameter("Range: span TỐI THIỂU (giá) — loại micro-range nhiễu", 51, 0.5, 10, 0.1, 1)]
        public double RangeMinPts { get; set; } = 3.0;   // sweep: span≥3đ net +40 vs +35 (loại vụ 07/24 19:27)
        [InputParameter("Range: span TỐI ĐA (giá) — vùng co hẹp", 52, 1, 20, 0.1, 1)]
        public double RangeMaxPts { get; set; } = 7.5;   // thử nới 10 → exp 0.29→0.21 (KHÔNG free) → giữ 7.5. Nới tại đây nếu muốn thêm lệnh (chấp nhận loãng edge)

        // ---------- CBR: BREAK ----------
        [InputParameter("Break: VSA tối thiểu (× TB) — climax", 53, 1.0, 5, 0.05, 2)]
        public double BreakVsa { get; set; } = 2.0;
        [InputParameter("Break: thân mạnh ≥ (body/range)", 54, 0.2, 1.0, 0.05, 2)]
        public double BreakBody { get; set; } = 0.50;

        // ---------- CBR: HỒI + TIẾP DIỄN ----------
        [InputParameter("Chờ hồi+tiếp diễn trong (số nến)", 55, 3, 40, 1, 0)]
        public int WaitBars { get; set; } = 12;
        [InputParameter("Retrace TỐI THIỂU (% của leg)", 56, 0.05, 0.9, 0.05, 2)]
        public double PullMin { get; set; } = 0.40;   // sweep: nâng sàn 10→40% net +28→+35. Hồi nông = đuổi đà kiệt (07/24 09:54).
        [InputParameter("Retrace TỐI ĐA (% của leg)", 57, 0.3, 1.0, 0.05, 2)]
        public double PullMax { get; set; } = 0.90;   // GIỮ cao: hồi sâu 60-90% chứa nhiều runner lớn. Cap thấp = cắt lãi.
        [InputParameter("Hồi cho phép thủng cạnh vùng (tick)", 58, 0, 10, 1, 0)]
        public int HoldTolTicks { get; set; } = 2;
        [InputParameter("Nến tiếp diễn: thân ≥ (body/range)", 59, 0.2, 1.0, 0.05, 2)]
        public double ResumeBody { get; set; } = 0.35;

        // ---------- risk / TP ----------
        [InputParameter("SL sàn (giá)", 60, 0.5, 8, 0.1, 1)]
        public double SlFloorPts { get; set; } = 3.0;
        [InputParameter("SL trần (giá) — quá thì bỏ", 61, 1, 12, 0.1, 1)]
        public double SlCapPts { get; set; } = 7.0;
        [InputParameter("SL đệm ngoài cực trị hồi (tick)", 62, 0, 20, 1, 0)]
        public int SlBuf { get; set; } = 2;
        [InputParameter("RR mục tiêu (TP, giữ runner)", 63, 1, 8, 0.5, 1)]
        public double RR { get; set; } = 3.0;
        [InputParameter("Cooldown mỗi phía (số nến)", 64, 0, 60, 1, 0)]
        public int Cooldown { get; set; } = 15;
        [InputParameter("Gộp tín hiệu trùng (số nến)", 65, 1, 20, 1, 0)]
        public int DedupBars { get; set; } = 6;

        // ---------- QUAY ĐẦU (reversal tại vùng — dùng HẤP THỤ footprint LIVE) ----------
        [InputParameter("Bật nhánh QUAY ĐẦU (chạm vùng + hấp thụ)", 66)]
        public bool EnableReversal { get; set; } = true;
        [InputParameter("Quay đầu: khoảng arm tới vùng (tick)", 67, 5, 60, 1, 0)]
        public int ArmDistTicks { get; set; } = 20;
        [InputParameter("Hấp thụ: dominance mức ≥ (|Δ|/vol per-level)", 68, 0.3, 1.0, 0.05, 2)]
        public double AbsDom { get; set; } = 0.60;
        [InputParameter("Quay đầu: rút râu ≥ (rau/range)", 69, 0.3, 1.0, 0.05, 2)]
        public double WickFrac { get; set; } = 0.50;
        [InputParameter("Quay đầu: hoặc thân mạnh ≥ (body/range)", 72, 0.3, 1.0, 0.05, 2)]
        public double BodyStrong { get; set; } = 0.55;
        [InputParameter("Quay đầu: climax tím thay được tường hấp thụ", 73)]
        public bool RevClimaxOverride { get; set; } = true;

        // ---------- lọc / warm-up ----------
        [InputParameter("Sàn volume (chống nến mỏng)", 70, 0, 500, 1, 0)]
        public int VolFloor { get; set; } = 20;
        [InputParameter("Warm-up sau gap (số nến)", 71, 0, 60, 1, 0)]
        public int WarmupBars { get; set; } = 20;

        // ---------- hiển thị ----------
        [InputParameter("Hiện tín hiệu", 80)]
        public bool ShowSignals { get; set; } = true;
        [InputParameter("Hiện vùng hợp lưu", 81)]
        public bool ShowZones { get; set; } = true;
        [InputParameter("Hiện bảng", 82)]
        public bool ShowPanel { get; set; } = true;
        [InputParameter("Hiện TOÀN BỘ tín hiệu lịch sử", 83)]
        public bool ShowAllHistory { get; set; } = true;
        [InputParameter("(nếu tắt) số nến hiển thị gần nhất", 87, 50, 20000, 50, 0)]
        public int DisplayBars { get; set; } = 600;
        [InputParameter("Số dòng tối đa trong bảng", 88, 2, 20, 1, 0)]
        public int PanelRows { get; set; } = 4;
        [InputParameter("Góc bảng (0=TL 1=TR 2=BL 3=BR)", 84, 0, 3, 1, 0)]
        public int PanelCorner { get; set; } = 0;
        [InputParameter("Cỡ chữ", 85, 7, 20, 1, 0)]
        public int FontSize { get; set; } = 9;

        [InputParameter("Màu LONG", 90)]
        public Color LongColor { get; set; } = Color.FromArgb(0x26, 0xC6, 0xDA);
        [InputParameter("Màu SHORT", 91)]
        public Color ShortColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);
        [InputParameter("Màu vùng hợp lưu", 92)]
        public Color ConflColor { get; set; } = Color.FromArgb(0xFF, 0xB3, 0x00);
        [InputParameter("Màu SL (đỏ)", 93)]
        public Color SlLineColor { get; set; } = Color.FromArgb(0xE5, 0x39, 0x35);
        [InputParameter("Màu TP (xanh)", 94)]
        public Color TpLineColor { get; set; } = Color.FromArgb(0x00, 0xC8, 0x53);
        [InputParameter("Độ dày đường", 95, 1, 5, 1, 0)]
        public int LineWidth { get; set; } = 2;
        [InputParameter("Tô vùng R:R (lời/lỗ)", 96)]
        public bool ShowRiskBox { get; set; } = true;
        [InputParameter("Vẽ mũi tên", 100)]
        public bool ShowArrows { get; set; } = true;
        [InputParameter("Vẽ đường E/SL/TP", 101)]
        public bool ShowLines { get; set; } = true;
        [InputParameter("Vẽ chip giá (mép phải)", 102)]
        public bool ShowChips { get; set; } = true;
        [InputParameter("Vẽ nhãn setup", 103)]
        public bool ShowLabels { get; set; } = true;
        [InputParameter("Hiện tín hiệu ĐÃ ĐÓNG (mờ)", 104)]
        public bool ShowClosed { get; set; } = true;
        [InputParameter("SL/TP nét đứt (tắt = nét liền)", 105)]
        public bool DashedSlTp { get; set; } = true;
        [InputParameter("Độ mờ vùng R:R (0-120)", 106, 0, 120, 2, 0)]
        public int RiskBoxOpacity { get; set; } = 34;
        [InputParameter("Cỡ mũi tên", 107, 4, 20, 1, 0)]
        public int ArrowSize { get; set; } = 8;
        [InputParameter("Độ dày đường vùng hợp lưu", 108, 1, 6, 1, 0)]
        public int ZoneLineWidth { get; set; } = 2;
        [InputParameter("Độ mờ nền bảng (100-255)", 109, 100, 255, 5, 0)]
        public int PanelOpacity { get; set; } = 215;

        // ---------- xuất CSV (để đối chiếu C# ↔ Python + tách WR 2 nhánh) ----------
        [InputParameter("Xuất CSV toàn bộ tín hiệu", 120)]
        public bool ExportCsv { get; set; } = false;
        [InputParameter("Đường dẫn CSV (trống = thư mục Documents)", 121)]
        public string ExportPath { get; set; } = "";

        private bool _vaLoaded;
        private string _exportedTo;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private RenderState _render;
        private int _digits = 1;
        private double _tick = 0.1;
        private int _lastN = -1;
        private int _vaCov, _vaTot;
        private DateTime _vaFirst = DateTime.MinValue;
        private readonly PanelDrag _drag = new();

        public RunnerSignal() : base()
        {
            Name = "Runner Signal (CBR M1)";
            Description = "Runner CBR M1: phá vùng co → chờ hồi giữ leg → vào nến tiếp diễn (TP 3R). Bắn nến đóng. Cần Volume Analysis. Add vào chart M1.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded() { lock (_calc) { _vaLoaded = true; _lastN = -1; } Process(); }
        protected override void OnClear() { _drag.Detach(); lock (_calc) { _vaLoaded = false; _lastN = -1; lock (_sync) _render = null; } }
        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaLoaded) return;
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            Process();
        }

        private string Fmt(double p) => double.IsNaN(p) ? "—" : Math.Round(p, _digits).ToString("0.0##");
        private string LabelOf(DateTime t)
        {
            int m = (int)(t.AddHours(TzOffset).TimeOfDay.TotalMinutes);
            if (m >= AsiaStart && m < EuropeStart) return "A";
            if (m >= EuropeStart && m < UsStart) return "AU";
            return "MY";
        }
        private static string VN(string lab) => lab == "A" ? "Á" : lab == "AU" ? "Âu" : "Mỹ";

        private sealed class Bar
        {
            public int Idx;
            public int HdIdx;
            public DateTime Time;
            public double O, H, L, C, Vol, Delta, Cum, Vwap, Vma, Vratio;
            public int Bias;      // EMA30 vs EMA120 (hiển thị; KHÔNG gate — bias thật = TPO)
            public int SinceGap;
            public double Rng => H - L;
            public double Body => Math.Abs(C - O);
            public double UW => H - Math.Max(O, C);
            public double LW => Math.Min(O, C) - L;
            public double Brat => Rng > 0 ? Body / Rng : 0;
            public double Cpos => Rng > 0 ? (C - L) / Rng : 0.5;
            public double Ddom => Vol > 0 ? Delta / Vol : 0;
        }

        private sealed class PZone
        {
            public double Price; public string Kind; public double Strength;
            public DateTime ReadyTime, ExpireTime;
            public string PrevRel;   // above/below/in — hướng tiếp cận vùng (nhánh quay đầu)
        }

        private sealed class Sig
        {
            public int Idx; public DateTime Time; public int Side;
            public string Scen; public char Grade; public double Entry, Sl, Tp1, Tp2, RiskT, Rr2;
            public int Cluster;          // số vùng chồng quanh giá vào (info, KHÔNG gate)
            public double BlockR;        // TP-vướng-vùng mạnh: cách entry bao nhiêu R (NaN = không vướng)
            public double Vsa; public bool Climax; public List<string> Why = new();
            public string Outcome = "running";
            public DateTime OutTime;
        }

        private void Process()
        {
            lock (_calc)
            {
                try
                {
                    var hd = HistoricalData;
                    if (hd == null) return;
                    _tick = Symbol?.TickSize ?? 0;
                    if (_tick <= 0) return;
                    _digits = Math.Max(0, (int)Math.Round(-Math.Log10(_tick)));
                    int n = hd.Count;
                    if (n < VsaPeriod + 5) return;
                    if (n == _lastN) return;

                    var B = BuildBars(hd, n);
                    if (B.Count < VsaPeriod + 5) { _lastN = n; return; }

                    var pool = BuildPool(hd, B);
                    var sigs = Scan(hd, B, pool);
                    foreach (var s in sigs) { Simulate(B, s); Enrich(pool, s); }

                    if (ExportCsv) ExportSignals(sigs);

                    int minIdx = B.Count - 1 - DisplayBars;
                    var show = ShowAllHistory ? sigs : sigs.Where(s => s.Idx >= minIdx || s.Outcome == "running").ToList();

                    double now = B[B.Count - 1].C;
                    var clusters = CurrentClusters(pool, B[B.Count - 1].Time, now);

                    lock (_sync) _render = new RenderState { Sigs = show, Clusters = clusters, Panel = BuildPanel(show), Digits = _digits };
                    _lastN = n;
                }
                catch { /* giữ indicator sống */ }
            }
        }

        // ================= dựng nến + số dẫn xuất (KHỚP entry_month.load_m1) =================
        private List<Bar> BuildBars(HistoricalData hd, int n)
        {
            var B = new List<Bar>(n);
            int cov = 0; DateTime first = DateTime.MinValue;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                var t = b.VolumeAnalysisData?.Total;
                if (t != null) { cov++; if (first == DateTime.MinValue) first = b.TimeLeft; }
                B.Add(new Bar { Idx = B.Count, HdIdx = i, Time = b.TimeLeft, O = b.Open, H = b.High, L = b.Low, C = b.Close,
                    Vol = t?.Volume ?? b.Volume, Delta = t?.Delta ?? 0 });
            }
            _vaCov = cov; _vaTot = B.Count; _vaFirst = first;
            double csPV = 0, csV = 0, cum = 0, rollSum = 0;
            double ef = double.NaN, es = double.NaN, kf = 2.0 / (30 + 1), ks = 2.0 / (120 + 1);
            var q = new Queue<double>();
            for (int i = 0; i < B.Count; i++)
            {
                var b = B[i];
                bool gap = i > 0 && (b.Time - B[i - 1].Time).TotalMinutes > 30;
                if (gap) { csPV = 0; csV = 0; }
                double tp = (b.H + b.L + b.C) / 3.0; csPV += tp * b.Vol; csV += b.Vol;
                b.Vwap = csV > 0 ? csPV / csV : b.C;
                cum += b.Delta; b.Cum = cum;
                q.Enqueue(b.Vol); rollSum += b.Vol;
                if (q.Count > VsaPeriod) rollSum -= q.Dequeue();
                b.Vma = q.Count > 0 ? rollSum / q.Count : b.Vol;
                b.Vratio = b.Vma > 1e-9 ? b.Vol / b.Vma : 0;
                ef = double.IsNaN(ef) ? b.C : ef + kf * (b.C - ef);
                es = double.IsNaN(es) ? b.C : es + ks * (b.C - es);
                b.Bias = ef > es + 3 * _tick ? 1 : ef < es - 3 * _tick ? -1 : 0;
                b.SinceGap = gap ? 0 : (i > 0 ? B[i - 1].SinceGap + 1 : 999);
            }
            return B;
        }

        private bool Gate(Bar b) => b.Vol >= VolFloor && b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;

        // ================= dựng pool vùng (chỉ để hiển thị hợp lưu + info TP-vướng) =================
        private List<PZone> BuildPool(HistoricalData hd, List<Bar> B)
        {
            var pool = new List<PZone>();
            double rowStep = _tick * Math.Max(1, RowTicks);
            var sBlocks = SplitBlocks(hd, SessionGapMin);
            for (int i = 0; i < sBlocks.Count - 1; i++)
            {
                string lab = LabelOf(GetTime(hd, sBlocks[i].from));
                var sp = ProfileEngine.BuildProfile(hd, sBlocks[i].from, sBlocks[i].to, _tick, rowStep, true, 0, lab);
                if (!sp.Valid) continue;
                DateTime ready = GetTime(hd, sBlocks[i].to), exp = ready.AddDays(ZoneExpireDays);
                Add(pool, sp.Poc, $"POC {VN(lab)}", 70, ready, exp);
                Add(pool, sp.Vah, $"VAH {VN(lab)}", 58, ready, exp);
                Add(pool, sp.Val, $"VAL {VN(lab)}", 58, ready, exp);
                Add(pool, sp.High, $"Đỉnh {VN(lab)}", 52, ready, exp);
                Add(pool, sp.Low, $"Đáy {VN(lab)}", 52, ready, exp);
            }
            var dBlocks = ProfileEngine.GroupByGap(hd, DayGapMin);
            for (int i = 1; i < dBlocks.Count; i++)
            {
                var prev = ProfileEngine.BuildProfile(hd, dBlocks[i - 1].from, dBlocks[i - 1].to, _tick, rowStep, true, 0, "D");
                if (!prev.Valid) continue;
                DateTime ready = GetTime(hd, dBlocks[i].from), exp = ready.AddDays(1).AddHours(6);
                Add(pool, prev.Vah, "D-1 VAH", 66, ready, exp);
                Add(pool, prev.Val, "D-1 VAL", 66, ready, exp);
                Add(pool, prev.Poc, "D-1 POC", 72, ready, exp);
                Add(pool, prev.High, "D-1 Đỉnh", 60, ready, exp);
                Add(pool, prev.Low, "D-1 Đáy", 60, ready, exp);
            }
            return pool;
        }

        private static void Add(List<PZone> pool, double price, string kind, double str, DateTime ready, DateTime exp)
        {
            if (double.IsNaN(price) || price <= 0) return;
            pool.Add(new PZone { Price = price, Kind = kind, Strength = str, ReadyTime = ready, ExpireTime = exp });
        }

        private DateTime GetTime(HistoricalData hd, int i) => (hd[i, SeekOriginHistory.Begin] as HistoryItemBar)?.TimeLeft ?? DateTime.MinValue;

        private List<(int from, int to)> SplitBlocks(HistoricalData hd, int gapMin)
        {
            var res = new List<(int, int)>(); int n = hd.Count; if (n == 0) return res;
            int start = 0; DateTime prev = DateTime.MinValue; bool have = false; string curLab = null;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                string lab = LabelOf(b.TimeLeft);
                bool split = !have || lab != curLab || (b.TimeLeft - prev).TotalMinutes > gapMin;
                if (split) { if (have) res.Add((start, i - 1)); start = i; curLab = lab; }
                prev = b.TimeLeft; have = true;
            }
            if (have) res.Add((start, n - 1));
            return res;
        }

        // ================= CBR: phá vùng co → hồi giữ leg → tiếp diễn (KHỚP entry_cbr.run_cbr) =================
        private List<Sig> Scan(HistoricalData hd, List<Bar> B, List<PZone> pool)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;                          // BỎ nến đang hình thành → không repaint
            double rangeMinT = RangeMinPts / _tick, rangeMaxT = RangeMaxPts / _tick;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick;

            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i];
                if (!Gate(b)) continue;
                if (i < RangeLen) continue;
                double rhi = double.MinValue, rlo = double.MaxValue;
                for (int k = i - RangeLen; k < i; k++) { if (B[k].H > rhi) rhi = B[k].H; if (B[k].L < rlo) rlo = B[k].L; }
                double span = (rhi - rlo) / _tick;
                if (span > rangeMaxT || span < rangeMinT) continue;

                bool up = b.C > rhi + SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C > b.O;
                bool dn = b.C < rlo - SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C < b.O;
                if (!(up || dn)) continue;
                int side = up ? +1 : -1;
                double edge = up ? rhi : rlo;

                double peak = up ? b.H : b.L; int since = i;
                int jEnd = Math.Min(nClosed, i + 1 + WaitBars);
                for (int j = i + 1; j < jEnd; j++)
                {
                    var bj = B[j];
                    if (!Gate(bj)) break;
                    // đóng trở lại HẲN trong range → hủy leg
                    if (up ? bj.C < edge - HoldTolTicks * _tick : bj.C > edge + HoldTolTicks * _tick) break;

                    if (j >= since + 1)
                    {
                        double pullExt = up ? double.MaxValue : double.MinValue;
                        for (int k = since + 1; k <= j; k++) { if (up) { if (B[k].L < pullExt) pullExt = B[k].L; } else { if (B[k].H > pullExt) pullExt = B[k].H; } }
                        double leg = up ? (peak - edge) : (edge - peak);
                        double depth = up ? (peak - pullExt) : (pullExt - peak);
                        double retr = leg > 0 ? depth / leg : 0;
                        bool held = up ? pullExt >= edge - HoldTolTicks * _tick : pullExt <= edge + HoldTolTicks * _tick;
                        bool resume = (up ? (bj.C > B[j - 1].H && bj.C > bj.O) : (bj.C < B[j - 1].L && bj.C < bj.O)) && bj.Brat >= ResumeBody;
                        if (j >= since + 2 && retr >= PullMin && retr <= PullMax && held && resume)
                        {
                            double entry = bj.C, sl, risk;
                            if (up) { sl = pullExt - SlBuf * _tick; risk = (entry - sl) / _tick; }
                            else { sl = pullExt + SlBuf * _tick; risk = (sl - entry) / _tick; }
                            if (risk < slFloorT) { sl = up ? entry - slFloorT * _tick : entry + slFloorT * _tick; risk = slFloorT; }
                            if (risk > slCapT) break;
                            AddSig(raw, j, side, entry, sl, risk, b.Vratio, "CBR phá→hồi→tiếp diễn",
                                new List<string> { $"phá {edge.ToString("0.0##")}", $"hồi {retr * 100:0}%", $"leg {leg:0.0}giá", $"VSA {b.Vratio:0.0}x{(b.Vratio >= VsaClimax ? " tím" : "")}" });
                            break;
                        }
                    }
                    // mở rộng đỉnh leg
                    if (up ? bj.H > peak : bj.L < peak) { peak = up ? bj.H : bj.L; since = j; }
                }
            }
            if (EnableReversal) raw.AddRange(ScanReversal(hd, B, pool));
            return Cooldown_(Dedup(raw));
        }

        private void AddSig(List<Sig> raw, int idx, int side, double entry, double sl, double risk, double vsa, string scen, List<string> why)
        {
            raw.Add(new Sig { Idx = idx, Side = side, Scen = scen, Entry = entry, Sl = sl, RiskT = risk,
                Rr2 = RR, Vsa = vsa, Climax = vsa >= VsaClimax, Why = why });
        }

        // ===== NHÁNH QUAY ĐẦU: chạm vùng + HẤP THỤ per-level (footprint LIVE) → đảo chiều, TP 3R =====
        // KHÔNG backtest offline được (CSV không có footprint per-level) → validate LIVE. Cổng chặt:
        // giá tiếp cận vùng (arm), tag vùng, đóng bật lại đúng phía, + tường hấp thụ (Absorption) HOẶC
        // nến climax tím. SL ngoài cực trị ±buf (sàn/trần như CBR).
        private List<Sig> ScanReversal(HistoricalData hd, List<Bar> B, List<PZone> pool)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1; int buf = SlBuf;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick;
            foreach (var z in pool) z.PrevRel = null;
            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i]; double px = b.C;
                bool gated = Gate(b);
                foreach (var z in pool)
                {
                    if (b.Time < z.ReadyTime || b.Time > z.ExpireTime) continue;
                    double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                    string rel = b.C > zp + buf * _tick ? "above" : b.C < zp - buf * _tick ? "below" : "in";
                    if (!gated) { z.PrevRel = px > zp ? "above" : "below"; continue; }
                    double dist = Math.Abs(px - zp) / _tick;
                    if (dist > ArmDistTicks) { z.PrevRel = rel; continue; }
                    double zlo = zp - buf * _tick, zhi = zp + buf * _tick;
                    bool tagged = b.L <= zhi && b.H >= zlo;
                    bool up = z.PrevRel == "below", dn = z.PrevRel == "above";
                    if (tagged)
                    {
                        // tới vùng từ DƯỚI, bị đẩy xuống lại (kháng cự) → SHORT
                        if (up && b.C < zhi && b.Delta < 0 && RejDown(b))
                        {
                            bool wall = Absorption(HdBar(hd, b.HdIdx), b.H, -1) || (RevClimaxOverride && b.Vratio >= VsaClimax);
                            if (wall) EmitRev(raw, i, -1, b.C, Math.Max(b.H, zp), zp, b.Vratio, slFloorT, slCapT);
                        }
                        // tới vùng từ TRÊN, bị đỡ lên lại (hỗ trợ) → LONG
                        else if (dn && b.C > zlo && b.Delta > 0 && RejUp(b))
                        {
                            bool wall = Absorption(HdBar(hd, b.HdIdx), b.L, +1) || (RevClimaxOverride && b.Vratio >= VsaClimax);
                            if (wall) EmitRev(raw, i, +1, b.C, Math.Min(b.L, zp), zp, b.Vratio, slFloorT, slCapT);
                        }
                    }
                    z.PrevRel = rel;
                }
            }
            return raw;
        }

        private bool RejUp(Bar b) => (b.LW >= WickFrac * b.Rng && b.Cpos >= 0.55) || (b.Brat >= BodyStrong && b.Ddom >= 0.25 && b.Cpos >= 0.6);
        private bool RejDown(Bar b) => (b.UW >= WickFrac * b.Rng && b.Cpos <= 0.45) || (b.Brat >= BodyStrong && b.Ddom <= -0.25 && b.Cpos <= 0.4);

        private void EmitRev(List<Sig> raw, int i, int side, double entry, double anchor, double zp, double vsa, double slFloorT, double slCapT)
        {
            double sl, risk;
            if (side > 0) { sl = anchor - SlBuf * _tick; risk = (entry - sl) / _tick; }
            else { sl = anchor + SlBuf * _tick; risk = (sl - entry) / _tick; }
            if (risk < slFloorT) { sl = side > 0 ? entry - slFloorT * _tick : entry + slFloorT * _tick; risk = slFloorT; }
            if (risk <= 0 || risk > slCapT) return;
            AddSig(raw, i, side, entry, sl, risk, vsa, "quay đầu (hấp thụ)",
                new List<string> { $"chạm {zp:0.0##}", vsa >= VsaClimax ? "climax tím" : "hấp thụ", $"VSA {vsa:0.0}x" });
        }

        // Tường hấp thụ per-level (footprint LIVE): tại cực trị có mức volume vượt trội + dominance
        // NGƯỢC chiều tiếp cận. side=+1 hấp thụ tại ĐÁY (mua đỡ), -1 tại ĐỈNH (bán đè). (port EntrySignal)
        private bool Absorption(HistoryItemBar bar, double extreme, int side)
        {
            var pl = bar?.VolumeAnalysisData?.PriceLevels;
            if (pl == null || pl.Count == 0) return false;
            double sum = 0; int c = 0;
            foreach (var kv in pl) { sum += kv.Value.Volume; c++; }
            if (c == 0) return false; double meanVol = sum / c;
            foreach (var kv in pl)
            {
                if (Math.Abs(kv.Key - extreme) > 3 * _tick) continue;
                double vol = kv.Value.Volume; if (vol < meanVol * 1.5) continue;
                double dNet = kv.Value.Delta; double dom = vol > 0 ? Math.Abs(dNet) / vol : 0;
                bool dirOk = side > 0 ? dNet < 0 : dNet > 0;
                if (dom >= AbsDom && dirOk) return true;
            }
            return false;
        }

        private HistoryItemBar HdBar(HistoricalData hd, int absIdx)
            => (absIdx >= 0 && absIdx < hd.Count) ? hd[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;

        // gộp trùng cùng phía trong DedupBars nến (KHỚP entry_cbr.dedup)
        private List<Sig> Dedup(List<Sig> raw)
        {
            var outp = new List<Sig>();
            foreach (var s in raw.OrderBy(x => x.Idx))
                if (!outp.Any(m => m.Side == s.Side && Math.Abs(s.Idx - m.Idx) <= DedupBars)) outp.Add(s);
            return outp;
        }

        // cooldown mỗi phía (KHỚP entry_cbr.cooldown_filter)
        private List<Sig> Cooldown_(List<Sig> sig)
        {
            var outp = new List<Sig>(); var last = new Dictionary<int, int>();
            foreach (var s in sig.OrderBy(x => x.Idx))
            {
                if (s.Idx - last.GetValueOrDefault(s.Side, -999) < Cooldown) continue;
                outp.Add(s); last[s.Side] = s.Idx;
            }
            return outp;
        }

        private int ClusterCount(List<PZone> pool, DateTime t, double price)
        {
            var seen = new HashSet<long>();
            foreach (var z in pool)
            {
                if (t < z.ReadyTime || t > z.ExpireTime) continue;
                double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                if (Math.Abs(zp - price) / _tick > ConfluenceTol) continue;
                seen.Add((long)Math.Round(zp / _tick));
            }
            return seen.Count;
        }

        // vùng MẠNH (strength≥58) chắn đường tới TP → cách entry bao nhiêu R (info, KHÔNG gate)
        private double BlockRToTp(List<PZone> pool, Sig s)
        {
            double r = s.RiskT * _tick, best = double.NaN;
            double tp = s.Side > 0 ? s.Entry + RR * r : s.Entry - RR * r;
            foreach (var z in pool)
            {
                if (s.Time < z.ReadyTime || s.Time > z.ExpireTime || z.Strength < 58) continue;
                double p = z.Price; if (double.IsNaN(p) || p <= 0) continue;
                bool inPath = s.Side > 0 ? (s.Entry < p && p < tp) : (tp < p && p < s.Entry);
                if (!inPath) continue;
                double rr = Math.Abs(p - s.Entry) / r;
                if (double.IsNaN(best) || rr < best) best = rr;
            }
            return best;
        }

        private void Simulate(List<Bar> B, Sig s)
        {
            var b0 = B[s.Idx];
            s.Time = b0.Time;
            double r = s.RiskT * _tick;
            s.Tp1 = s.Side > 0 ? s.Entry + RR * r : s.Entry - RR * r; s.Tp2 = s.Tp1;
            for (int j = s.Idx + 1; j < B.Count; j++)
            {
                var b = B[j];
                bool hitSL = s.Side > 0 ? b.L <= s.Sl : b.H >= s.Sl;
                bool hitTP = s.Side > 0 ? b.H >= s.Tp1 : b.L <= s.Tp1;
                if (hitSL) { s.Outcome = "SL"; s.OutTime = b.Time; return; }
                if (hitTP) { s.Outcome = "TP"; s.OutTime = b.Time; return; }
            }
            s.Outcome = "running"; s.OutTime = B[B.Count - 1].Time;
        }

        // điền Cluster/Block/Grade sau khi có Time (gọi từ Process qua Simulate? — làm gọn: tính ở đây)
        private void Enrich(List<PZone> pool, Sig s)
        {
            s.Cluster = ClusterCount(pool, s.Time, s.Entry);
            s.BlockR = BlockRToTp(pool, s);
            s.Grade = s.Cluster >= MinConfluence ? 'A' : 'B';
            if (s.Cluster >= MinConfluence) s.Why.Add($"hợp lưu ×{s.Cluster}");
            if (!double.IsNaN(s.BlockR)) s.Why.Add($"TP vướng vùng ↧{s.BlockR:0.0}R");
        }

        // ================= XUẤT CSV (đối chiếu C#↔Python + tách WR nhánh CBR vs quay đầu) =================
        // Ghi TOÀN BỘ tín hiệu mỗi khi có nến mới (ghi đè cùng file). Cột nhanh=CBR/QUAY_DAU để soi 2 nhánh.
        private void ExportSignals(List<Sig> sigs)
        {
            try
            {
                string path = ExportPath?.Trim();
                if (string.IsNullOrEmpty(path))
                    path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "RunnerSignal_signals.csv");
                else if (Directory.Exists(path))
                    path = Path.Combine(path, "RunnerSignal_signals.csv");

                var ci = CultureInfo.InvariantCulture;
                var sb = new StringBuilder();
                sb.Append("ngay_gio,nhanh,huong,entry,SL,risk_gia,TP,RR,VSA,climax,co_vung,grade,tp_vuong_vung,KQ,ket_thuc_luc,chi_tiet\n");
                foreach (var s in sigs.OrderBy(x => x.Idx))
                {
                    string nhanh = s.Scen != null && s.Scen.StartsWith("quay") ? "QUAY_DAU" : "CBR";
                    string huong = s.Side > 0 ? "LONG" : "SHORT";
                    string block = double.IsNaN(s.BlockR) ? "-" : s.BlockR.ToString("0.0", ci) + "R";
                    string kq = s.Outcome == "TP" ? "WIN" : s.Outcome == "SL" ? "LOSS" : "open";
                    string ct = "\"" + string.Join(" · ", s.Why ?? new List<string>()).Replace("\"", "'") + "\"";
                    sb.Append(s.Time.ToString("yyyy-MM-dd HH:mm")).Append(',')
                      .Append(nhanh).Append(',').Append(huong).Append(',')
                      .Append(s.Entry.ToString("0.0##", ci)).Append(',')
                      .Append(s.Sl.ToString("0.0##", ci)).Append(',')
                      .Append((s.RiskT * _tick).ToString("0.0", ci)).Append(',')
                      .Append(s.Tp1.ToString("0.0##", ci)).Append(',')
                      .Append(RR.ToString("0.#", ci)).Append(',')
                      .Append(s.Vsa.ToString("0.00", ci)).Append(',')
                      .Append(s.Climax ? "tim" : "-").Append(',')
                      .Append(s.Cluster.ToString(ci)).Append(',')
                      .Append(s.Grade).Append(',')
                      .Append(block).Append(',')
                      .Append(kq).Append(',')
                      .Append(s.OutTime.ToString("yyyy-MM-dd HH:mm")).Append(',')
                      .Append(ct).Append('\n');
                }
                File.WriteAllText(path, sb.ToString(), new UTF8Encoding(true));
                _exportedTo = $"{sigs.Count} lệnh → {path}";
            }
            catch (Exception ex) { _exportedTo = "LỖI ghi CSV: " + ex.Message; }
        }

        private List<(double price, double strength, int side)> CurrentClusters(List<PZone> pool, DateTime now, double nowPrice)
        {
            var active = pool.Where(z => now >= z.ReadyTime && now <= z.ExpireTime && !double.IsNaN(z.Price) && z.Price > 0)
                             .Select(z => z.Price).OrderBy(x => x).ToList();
            var res = new List<(double, double, int)>(); int k = 0;
            while (k < active.Count)
            {
                int j = k; var grp = new List<double> { active[k] };
                while (j + 1 < active.Count && (active[j + 1] - grp[0]) / _tick <= ConfluenceTol) { grp.Add(active[j + 1]); j++; }
                if (grp.Count >= MinConfluence) { double c = grp.Average(); res.Add((c, Math.Min(100, 50 + grp.Count * 12), c > nowPrice ? -1 : 1)); }
                k = j + 1;
            }
            return res;
        }

        private List<(string, Color)> BuildPanel(List<Sig> sigs)
        {
            var p = new List<(string, Color)>();
            int running = sigs.Count(s => s.Outcome == "running");
            int tp = sigs.Count(s => s.Outcome == "TP"), sl = sigs.Count(s => s.Outcome == "SL");
            int closed = tp + sl;
            string wr = closed > 0 ? $" · WR {100.0 * tp / closed:0}%" : "";
            p.Add(($"RUNNER CBR (M1)   {sigs.Count} tín hiệu · ✓{tp} ✗{sl} •{running}{wr}  [TP {RR:0.#}R]", Color.White));
            if (_vaTot > 0 && _vaCov < (int)(_vaTot * 0.98) && _vaFirst != DateTime.MinValue)
                p.Add(($"⚠ footprint chỉ có {_vaCov}/{_vaTot} nến (từ {_vaFirst:dd/MM HH:mm}) — tăng số bar Volume Analysis", Color.FromArgb(255, 190, 120)));
            if (ExportCsv && !string.IsNullOrEmpty(_exportedTo))
                p.Add(($"💾 CSV: {_exportedTo}", Color.FromArgb(150, 220, 150)));
            var recent = sigs.OrderByDescending(s => s.Idx).Take(Math.Max(2, PanelRows)).ToList();
            if (recent.Count == 0) { p.Add(("(chưa có setup CBR)", Color.Gray)); return p; }
            foreach (var s in recent)
            {
                Color col = s.Side > 0 ? LongColor : ShortColor;
                string dir = s.Side > 0 ? "LONG" : "SHORT";
                string oc = s.Outcome == "TP" ? "✓" : s.Outcome == "SL" ? "✗" : "•";
                p.Add(($"{oc} {dir} {s.Grade} | E {Fmt(s.Entry)} SL {Fmt(s.Sl)} ({s.RiskT * _tick:0.0}đ) TP {Fmt(s.Tp1)} ({RR:0.#}R)", col));
                p.Add(($"    {string.Join(" · ", s.Why)}", Color.Silver));
            }
            return p;
        }

        // ================= RENDER (tái dùng từ EntrySignal) =================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || !_vaLoaded) return;
            _drag.Attach(CurrentChart);
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;
            RenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;
            var gr = args.Graphics; var conv = win.CoordinatesConverter; var clip = win.ClientRectangle;
            var prevClip = gr.ClipBounds; gr.SetClip(clip);
            try
            {
                gr.SmoothingMode = SmoothingMode.AntiAlias;
                if (ShowZones && rs.Clusters != null && rs.Clusters.Count > 0)
                {
                    using var fZ = new Font("Segoe UI", 8, FontStyle.Bold);
                    using var penZ = new Pen(ConflColor, Math.Max(1, ZoneLineWidth)) { DashStyle = DashStyle.Dash, DashPattern = new[] { 6f, 4f } };
                    foreach (var (price, strength, side) in rs.Clusters)
                    {
                        float y = (float)conv.GetChartY(price);
                        if (y < clip.Top || y > clip.Bottom) continue;
                        gr.DrawLine(penZ, clip.Left, y, clip.Right, y);
                        Chip(gr, fZ, clip.Left + 2, y, "⬥ HỢP LƯU " + price.ToString("0.0##"), ConflColor, false);
                    }
                }
                if (ShowSignals && rs.Sigs != null)
                {
                    using var fLbl = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    using var fChip = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    var dash = DashedSlTp ? DashStyle.Dash : DashStyle.Solid;
                    foreach (var s in rs.Sigs)
                    {
                        bool active = s.Outcome == "running";
                        if (!active && !ShowClosed) continue;
                        float xE = (float)conv.GetChartX(s.Time);
                        float xEnd = active ? clip.Right : (float)conv.GetChartX(s.OutTime);
                        if (xEnd > clip.Right) xEnd = clip.Right;
                        if (xEnd < xE + 10) xEnd = xE + 10;
                        if (xEnd < clip.Left || xE > clip.Right) continue;
                        float yE = (float)conv.GetChartY(s.Entry), ySL = (float)conv.GetChartY(s.Sl), yTP = (float)conv.GetChartY(s.Tp1);
                        float yTop = Math.Min(ySL, yTP), yBot = Math.Max(ySL, yTP);
                        if (yBot < clip.Top || yTop > clip.Bottom) continue;
                        Color dir = s.Side > 0 ? LongColor : ShortColor;
                        float xb = Math.Max(xE, clip.Left); float bw = Math.Max(1, xEnd - xb);
                        int fillA = active ? Math.Max(18, RiskBoxOpacity) : Math.Max(10, RiskBoxOpacity / 2);
                        int lineA = active ? 255 : 150;
                        if (ShowRiskBox)
                        {
                            using (var bt = new SolidBrush(Color.FromArgb(fillA, TpLineColor)))
                                gr.FillRectangle(bt, xb, Math.Min(yE, yTP), bw, Math.Abs(yTP - yE));
                            using (var bs = new SolidBrush(Color.FromArgb(fillA, SlLineColor)))
                                gr.FillRectangle(bs, xb, Math.Min(yE, ySL), bw, Math.Abs(ySL - yE));
                        }
                        if (ShowLines)
                        {
                            using (var pt = new Pen(Color.FromArgb(lineA, TpLineColor), LineWidth) { DashStyle = dash }) gr.DrawLine(pt, xb, yTP, xEnd, yTP);
                            using (var ps = new Pen(Color.FromArgb(lineA, SlLineColor), LineWidth) { DashStyle = dash }) gr.DrawLine(ps, xb, ySL, xEnd, ySL);
                            using (var pe = new Pen(Color.FromArgb(lineA, dir), LineWidth + 0.5f)) gr.DrawLine(pe, xb, yE, xEnd, yE);
                            using (var pv = new Pen(Color.FromArgb(active ? 220 : 110, dir), 1.5f)) gr.DrawLine(pv, xE, yTop, xE, yBot);
                        }
                        if (yE >= clip.Top - 6 && yE <= clip.Bottom + 6)
                        {
                            using (var bd = new SolidBrush(active ? dir : Color.FromArgb(210, dir))) gr.FillEllipse(bd, xE - 4.5f, yE - 4.5f, 9, 9);
                            using (var pw = new Pen(Color.FromArgb(active ? 255 : 190, Color.White), 1.4f)) gr.DrawEllipse(pw, xE - 4.5f, yE - 4.5f, 9, 9);
                        }
                        if (ShowArrows) DrawArrow(gr, xE, yE, s.Side, active ? dir : Color.FromArgb(180, dir), Math.Max(4, active ? ArrowSize : ArrowSize - 2));
                        if (ShowLabels)
                        {
                            string lbl = (s.Side > 0 ? "LONG " : "SHORT ") + s.Grade + (s.Cluster >= MinConfluence ? " ×" + s.Cluster : "") + (active ? " · CBR" : "");
                            LabelBox(gr, fLbl, xE + 10, s.Side > 0 ? yBot + 4 : yTop - 20, lbl, active ? dir : Color.FromArgb(210, dir));
                        }
                        if (active && ShowChips)
                        {
                            Chip(gr, fChip, clip.Right, yE, "E " + Fmt(s.Entry), dir, true);
                            Chip(gr, fChip, clip.Right, ySL, "SL " + Fmt(s.Sl) + " (" + (s.RiskT * _tick).ToString("0.0") + "đ)", SlLineColor, true);
                            Chip(gr, fChip, clip.Right, yTP, "TP " + Fmt(s.Tp1) + "  " + RR.ToString("0.#") + "R", TpLineColor, true);
                        }
                        else if (!active)
                        {
                            string mk = s.Outcome == "TP" ? "✓" : "✗";
                            using var bf = new SolidBrush(s.Outcome == "TP" ? TpLineColor : SlLineColor);
                            gr.DrawString(mk, fLbl, bf, xEnd - 3, (s.Outcome == "TP" ? yTP : ySL) - 8);
                        }
                    }
                }
                if (ShowPanel && rs.Panel != null && rs.Panel.Count > 0)
                {
                    using var f = new Font("Consolas", FontSize, FontStyle.Regular);
                    float pad = 6, lineH = f.Height + 2, w = 0;
                    foreach (var (t, _) in rs.Panel) w = Math.Max(w, gr.MeasureString(t, f).Width);
                    float bw = w + 2 * pad, bh = rs.Panel.Count * lineH + 2 * pad;
                    float defX = (PanelCorner == 1 || PanelCorner == 3) ? clip.Right - bw - 8 : clip.Left + 8;
                    float defY = (PanelCorner >= 2) ? clip.Bottom - bh - 8 : clip.Top + 8;
                    var (x, y) = _drag.Origin(defX, defY, bw, bh, clip);
                    using (var bg = new SolidBrush(Color.FromArgb(Math.Clamp(PanelOpacity, 100, 255), 18, 18, 22))) gr.FillRectangle(bg, x, y, bw, bh);
                    using (var bd = new Pen(Color.FromArgb(90, 255, 255, 255))) gr.DrawRectangle(bd, x, y, bw, bh);
                    float ty = y + pad;
                    foreach (var (t, col) in rs.Panel) { using var br = new SolidBrush(col); gr.DrawString(t, f, br, x + pad, ty); ty += lineH; }
                    _drag.SetBounds(x, y, bw, bh);
                }
            }
            catch { /* nuốt lỗi vẽ */ }
            finally { gr.SetClip(prevClip); }
        }

        private static GraphicsPath Round(float x, float y, float w, float h, float r)
        {
            var p = new GraphicsPath(); float d = r * 2;
            p.AddArc(x, y, d, d, 180, 90); p.AddArc(x + w - d, y, d, d, 270, 90);
            p.AddArc(x + w - d, y + h - d, d, d, 0, 90); p.AddArc(x, y + h - d, d, d, 90, 90);
            p.CloseFigure(); return p;
        }
        private static Color TextOn(Color bg)
            => (0.299 * bg.R + 0.587 * bg.G + 0.114 * bg.B) > 150 ? Color.FromArgb(20, 20, 24) : Color.White;

        private void Chip(Graphics gr, Font f, float x, float yMid, string text, Color bg, bool anchorRight)
        {
            var sz = gr.MeasureString(text, f);
            float pad = 5, h = sz.Height + 3, w = sz.Width + 2 * pad;
            float bx = anchorRight ? x - w : x;
            float by = yMid - h / 2;
            using var path = Round(bx, by, w, h, 4);
            using (var b = new SolidBrush(bg)) gr.FillPath(b, path);
            using var tb = new SolidBrush(TextOn(bg));
            gr.DrawString(text, f, tb, bx + pad, by + 1);
        }

        private void LabelBox(Graphics gr, Font f, float x, float y, string text, Color accent)
        {
            var sz = gr.MeasureString(text, f);
            float pad = 4, w = sz.Width + 2 * pad, h = sz.Height + 2;
            using (var bg = new SolidBrush(Color.FromArgb(210, 18, 18, 22))) { using var p = Round(x, y, w, h, 3); gr.FillPath(bg, p); }
            using (var bd = new Pen(Color.FromArgb(180, accent), 1f)) { using var p = Round(x, y, w, h, 3); gr.DrawPath(bd, p); }
            using var tb = new SolidBrush(accent);
            gr.DrawString(text, f, tb, x + pad, y + 1);
        }

        private void DrawArrow(Graphics gr, float x, float yE, int side, Color col, float sz)
        {
            var tri = side > 0
                ? new[] { new PointF(x, yE + sz + 6), new PointF(x - sz, yE + sz * 2 + 6), new PointF(x + sz, yE + sz * 2 + 6) }
                : new[] { new PointF(x, yE - sz - 6), new PointF(x - sz, yE - sz * 2 - 6), new PointF(x + sz, yE - sz * 2 - 6) };
            using (var b = new SolidBrush(col)) gr.FillPolygon(b, tri);
            using (var pn = new Pen(Color.FromArgb(230, 255, 255, 255), 1.3f)) gr.DrawPolygon(pn, tri);
        }

        private sealed class RenderState
        {
            public List<Sig> Sigs;
            public List<(double price, double strength, int side)> Clusters;
            public List<(string text, Color col)> Panel;
            public int Digits;
        }
    }
}
