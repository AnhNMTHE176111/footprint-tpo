// ============================================================================
//  EntrySignal  —  Gợi ý điểm vào lệnh (Entry/SL/TP) trên footprint M1 (QUANTOWER)
// ============================================================================
//  Add vào chart M1 có Volume Analysis. Tự dựng VÙNG từ chính M1 (phiên Á/Âu/Mỹ
//  theo giờ + ngày theo gap) → gom HỢP LƯU ≥2 vùng (lõi edge đã validate 28 ngày:
//  confluence≥2 mới có kỳ vọng dương, vùng lẻ = nhiễu). Bắn 2 kịch bản:
//    KB1 phá&hồi (thuận đà, A) · KB2 chạm&đảo (cần tường hấp thụ footprint live, B).
//  Chỉ bắn NẾN ĐÃ ĐÓNG (không repaint). RR 1:3 (nới tới vùng kế), SL ≤6đ (đẹp ~4đ).
//  VSA khớp indicator VsaVolume (SMA20 GỒM nến hiện tại): High=1.2, climax(tím)=2.2.
//  Build: concat ProfileEngine.cs + file này (build-entry.sh). Thiết kế: PLAN.md.
//  Logic tín hiệu KHỚP research/entry_month.py (bộ đã backtest). Vùng: dùng volume
//  per-level LIVE (chính xác hơn TPO offline); tập LOẠI vùng bám bộ đã validate
//  (session POC/VAH/VAL/H-L + D-1 + VWAP; naked/cluster để cho M30SessionZones).
// ============================================================================
namespace EntrySignal
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
    using TpoSuite;   // ProfileEngine (concat) — chứa TeleReport dùng chung

    public class EntrySignal : Indicator, IVolumeAnalysisIndicator
    {
        // ---------- giờ phiên (khớp M30SessionZones) ----------
        [InputParameter("Lệch giờ (bar.TimeLeft UTC → local)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Á bắt đầu (phút/ngày)", 11, 0, 1439, 5, 0)]
        public int AsiaStart { get; set; } = 300;
        [InputParameter("Âu bắt đầu (phút/ngày)", 12, 0, 1439, 5, 0)]
        public int EuropeStart { get; set; } = 750;
        [InputParameter("Mỹ bắt đầu (phút/ngày)", 13, 0, 1439, 5, 0)]
        public int UsStart { get; set; } = 1140;

        // ---------- profile / vùng ----------
        [InputParameter("Số tick / hàng profile", 20, 1, 50, 1, 0)]
        public int RowTicks { get; set; } = 1;      // 0.1 → khớp lưới Python đã validate
        [InputParameter("Gap tách phiên (phút)", 21, 20, 240, 1, 0)]
        public int SessionGapMin { get; set; } = 40;
        [InputParameter("Gap tách ngày (phút)", 22, 20, 240, 1, 0)]
        public int DayGapMin { get; set; } = 45;    // khe bảo trì M1 ~61' > 45 → tách ngày đúng
        [InputParameter("Số phiên xét vùng (0 = TẤT CẢ lịch sử)", 23, 0, 400, 1, 0)]
        public int LookbackSessions { get; set; } = 0;   // 0 = dựng vùng cho MỌI phiên đã load → tín hiệu lịch sử đầy đủ (khớp backtest). >0 chỉ để chặn tải nặng.
        [InputParameter("Số ngày vùng còn hiệu lực", 24, 1, 10, 1, 0)]
        public int ZoneExpireDays { get; set; } = 3;

        // ---------- confluence (lõi edge) ----------
        [InputParameter("Dung sai hợp lưu (tick)", 30, 1, 30, 1, 0)]
        public int ConfluenceTol { get; set; } = 7;
        [InputParameter("Dung sai gộp tín hiệu (tick)", 31, 1, 20, 1, 0)]
        public int DedupTol { get; set; } = 6;      // khớp DEDUP_TICKS Python
        [InputParameter("Số vùng hợp lưu tối thiểu", 32, 1, 5, 1, 0)]
        public int MinConfluence { get; set; } = 2;
        [InputParameter("Khoảng arm vùng (tick)", 33, 5, 60, 1, 0)]
        public int ArmDistTicks { get; set; } = 20;

        // ---------- nến tín hiệu (VSA khớp VsaVolume) ----------
        [InputParameter("VSA period (SMA volume, gồm nến này)", 40, 5, 200, 1, 0)]
        public int VsaPeriod { get; set; } = 20;
        [InputParameter("VSA cổng High (× TB)", 41, 0.5, 5, 0.05, 2)]
        public double VsaGate { get; set; } = 1.2;
        [InputParameter("VSA climax tím (× TB)", 42, 0.5, 8, 0.05, 2)]
        public double VsaClimax { get; set; } = 2.2;
        [InputParameter("Thân mạnh ≥ (body/range)", 43, 0.3, 1.0, 0.05, 2)]
        public double BodyStrong { get; set; } = 0.55;
        [InputParameter("Delta dominance ≥ (|Δ|/vol)", 44, 0.1, 1.0, 0.05, 2)]
        public double DeltaDom { get; set; } = 0.25;
        [InputParameter("|Delta| tối thiểu (thân mạnh)", 45, 0, 300, 1, 0)]
        public int DeltaAbsMin { get; set; } = 15;
        [InputParameter("Rút râu ≥ (rau/range)", 46, 0.3, 1.0, 0.05, 2)]
        public double WickFrac { get; set; } = 0.50;

        // ---------- retest / risk ----------
        [InputParameter("Retest tối đa (số nến)", 50, 2, 40, 1, 0)]
        public int RetestBars { get; set; } = 12;
        [InputParameter("Retest sát mức (tick)", 51, 1, 20, 1, 0)]
        public int RetestTol { get; set; } = 4;
        [InputParameter("Retest phải GIỮ vùng — cho phép chọc qua (tick, 0=chặt)", 58, 0, 10, 1, 0)]
        public int RetestHoldBuf { get; set; } = 0;   // nhịp hồi phải giữ gốc phá (retrace≤100%): low≥vùng-buf. Backtest: 1.5R WR 58→61%, exp +0.45→+0.52R; bỏ đúng ca "bắt dao rơi" (low xuyên thủng vùng), giữ đúng ca retest lành mạnh.
        [InputParameter("SL sàn (giá) — tránh stop 2đ dính nhiễu", 52, 0.5, 8, 0.1, 1)]
        public double SlFloor { get; set; } = 4.0;   // backtest: floor 2đ hay bị noise-stop rồi giá chạy TP; 4đ ⇒ WR 36%→58% (giữ mục tiêu ~6đ)
        [InputParameter("SL trần (giá) — quá thì bỏ", 53, 1, 12, 0.1, 1)]
        public double SlCap { get; set; } = 6.0;
        [InputParameter("SL đệm ngoài nến/vùng (tick)", 54, 0, 20, 1, 0)]
        public int SlBuf { get; set; } = 2;
        [InputParameter("RR mục tiêu (TP1)", 55, 1, 6, 0.5, 1)]
        public double RR { get; set; } = 1.5;   // với SL 4đ ⇒ TP1 ≈ 6đ = điểm ngọt (58% WR). RR to hơn = TP quá xa, hụt.
        [InputParameter("Nới TP tới vùng mạnh kế", 56)]
        public bool ExtendToNextZone { get; set; } = true;
        [InputParameter("RR tối thiểu để nới (TP2 runner)", 57, 1, 8, 0.5, 1)]
        public double NextZoneMinR { get; set; } = 2.0;
        [InputParameter("Cooldown mỗi cụm (số nến)", 58, 0, 60, 1, 0)]
        public int Cooldown { get; set; } = 15;

        // ---------- footprint (KB2) ----------
        [InputParameter("KB2 (chạm&đảo): bắt buộc tường hấp thụ live", 60)]
        public bool RequireWallForS2 { get; set; } = true;
        [InputParameter("Bật Kịch bản 2 (chạm&đảo)", 61)]
        public bool EnableS2 { get; set; } = true;
        [InputParameter("Hấp thụ: dominance mức ≥", 62, 0.3, 1.0, 0.05, 2)]
        public double AbsDom { get; set; } = 0.60;
        [InputParameter("KB2: nến climax tím thay được tường hấp thụ", 63)]
        public bool S2ClimaxOverride { get; set; } = true;   // nến climax (VSA≥tím) tại cụm ≥2 = bằng chứng hấp thụ đủ, không cần per-level wall
        [InputParameter("KB3: climax PHÁ qua cụm (phụ, mặc định TẮT)", 64)]
        public bool EnableS3ClimaxBreak { get; set; } = false;   // nến tím xuyên cụm ≥2 (vd 20:31/4051.8). Edge yếu (~hòa vốn) → grade C, tự bật nếu muốn.
        [InputParameter("KB4: đảo chiều arm→confirm (phụ, mặc định TẮT)", 65)]
        public bool EnableS4ArmConfirm { get; set; } = false;   // rút râu = ARM (không cần vol); nến tăng/giảm mạnh vol≥High trong N cây = CONFIRM. Gate cụm≥2 tự lọc. Edge +0.15R@1.5R.
        [InputParameter("KB4: cửa sổ chờ xác nhận (số nến)", 66, 2, 20, 1, 0)]
        public int ArmConfirmWindow { get; set; } = 6;   // rút râu và nến xác nhận cách nhau ≤ N cây
        // ABSORPTION FILTER (research 6 tháng feed footprint, 4 phân tích hội tụ): delta NGƯỢC phía lệnh
        // (bán bị hấp thụ ở đáy / mua bị hấp thụ ở đỉnh) → WR 52% vs 36% cùng-phía. Bật → WR 45→52%,
        // +15.5→+25.5R, cứu tháng lỗ. MẶC ĐỊNH TẮT (live giữ nguyên): khi BẬT, KB2 bỏ yêu cầu delta
        // cùng-phía (candle-based) và CẢ 2 kịch bản né lệnh có delta 3-nến-chạm-vùng cùng phía. Cần A/B live.
        [InputParameter("Lọc HẤP THỤ (né delta cùng phía) — cần delta live", 67)]
        public bool AbsorptionFilter { get; set; } = false;

        // ---------- lọc / warm-up ----------
        [InputParameter("Sàn volume (chống nến mỏng)", 70, 0, 500, 1, 0)]
        public int VolFloor { get; set; } = 20;
        [InputParameter("Warm-up sau gap (số nến)", 71, 0, 60, 1, 0)]
        public int WarmupBars { get; set; } = 20;

        // ---------- hiển thị ----------
        [InputParameter("Hiện tín hiệu (mũi tên + nhãn)", 80)]
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
        [InputParameter("Chỉ hiện A-grade", 86)]
        public bool OnlyAGrade { get; set; } = false;

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
        // ---- bật/tắt từng thành phần vẽ (tín hiệu ĐANG CHẠY) ----
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
        // ---- tinh chỉnh độ đậm / kích thước ----
        [InputParameter("Độ mờ vùng R:R (0-120)", 106, 0, 120, 2, 0)]
        public int RiskBoxOpacity { get; set; } = 34;
        [InputParameter("Cỡ mũi tên", 107, 4, 20, 1, 0)]
        public int ArrowSize { get; set; } = 8;
        [InputParameter("Độ dày đường vùng hợp lưu", 108, 1, 6, 1, 0)]
        public int ZoneLineWidth { get; set; } = 2;
        [InputParameter("Độ mờ nền bảng (100-255)", 109, 100, 255, 5, 0)]
        public int PanelOpacity { get; set; } = 215;

        // ================= LỌC THUẬN XU HƯỚNG (tuỳ chọn) =================
        [InputParameter("Lọc THUẬN xu hướng (proxy TPO)", 112)]
        public bool TrendFilter { get; set; } = false;   // mặc định TẮT: hại nhánh chạm&đảo ngược-trend đang thắng
        [InputParameter("Xu hướng: số nến so sánh close", 113, 60, 2000, 20, 0)]
        public int TrendLookback { get; set; } = 480;     // ~8h M1 — khớp RUNNER v5

        // ================= CẦU NỐI MT5 (tự vào lệnh) =================
        [InputParameter("Cầu nối MT5: BẬT gửi tín hiệu", 130)]
        public bool Mt5Bridge { get; set; } = false;
        [InputParameter("MT5: dry-run (EA chỉ ghi log, KHÔNG vào lệnh)", 131)]
        public bool Mt5DryRun { get; set; } = true;
        [InputParameter("MT5: thư mục Files (trống = Common\\Files của MT5)", 132)]
        public string Mt5Dir { get; set; } = "";
        [InputParameter("MT5: tên file lệnh (JSONL)", 133)]
        public string Mt5CmdFile { get; set; } = "entry_cmd.jsonl";   // tách khỏi runner_cmd.jsonl; hoặc đổi = runner_cmd.jsonl để chung 1 EA
        [InputParameter("MT5: tuổi tín hiệu tối đa (giây) — chống bắn lệnh cũ", 134, 20, 600, 5, 0)]
        public int Mt5MaxAgeSec { get; set; } = 90;
        [InputParameter("MT5: chỉ gửi grade A (hợp lưu mạnh)", 135)]
        public bool Mt5OnlyGradeA { get; set; } = false;
        // NHỒI theo hợp lưu (research 6 tháng feed footprint: nhồi ×3 khi hợp lưu≥3 → R/MDD 2.05, dương mọi tháng).
        // Mặc định TẮT (mult=1). Bridge EA nhân lot cơ sở với "size_mult" trong JSONL.
        [InputParameter("MT5: nhồi khi hợp lưu ≥ (số vùng)", 136, 2, 6, 1, 0)]
        public int NhoiConflGate { get; set; } = 3;
        [InputParameter("MT5: hệ số nhồi (×lot; 1 = tắt)", 137, 1, 5, 0.5, 1)]
        public double NhoiMult { get; set; } = 1.0;

        // ================= BÁO TELEGRAM (mở/đóng lệnh) =================
        [InputParameter("Báo Telegram: BẬT (mở/đóng lệnh)", 140)]
        public bool TeleAlerts { get; set; } = false;
        [InputParameter("Telegram: Bot token", 141)]
        public string TeleBotToken { get; set; } = "";       // ĐIỀN TAY — repo public, KHÔNG hardcode
        [InputParameter("Telegram: Chat ID", 142)]
        public string TeleChatId { get; set; } = "";
        [InputParameter("Báo khi MỞ lệnh", 143)]
        public bool TeleAlertOpen { get; set; } = true;
        [InputParameter("Báo khi ĐÓNG (chạm TP/SL)", 144)]
        public bool TeleAlertClose { get; set; } = true;
        [InputParameter("Chỉ báo grade A (hợp lưu mạnh)", 145)]
        public bool TeleOnlyGradeA { get; set; } = false;
        [InputParameter("Tuổi tín hiệu tối đa (giây) — chống bắn khi reload", 148, 20, 600, 5, 0)]
        public int TeleMaxAgeSec { get; set; } = 90;
        [InputParameter("TG · Gửi thử ngay", 149)]
        public bool TeleTestNow { get; set; } = false;

        private bool _vaLoaded;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private RenderState _render;
        private int _digits = 1;
        private double _tick = 0.1;
        private int _lastN = -1;
        private int _vaCov, _vaTot;          // số nến có footprint (Δ) / tổng nến → báo vùng quét thực tế
        private DateTime _vaFirst = DateTime.MinValue;
        private readonly PanelDrag _drag = new();

        // ---- cầu nối MT5 ----
        private bool _mt5Armed;                                 // false = lần quét đầu (nạp lịch sử) → KHÔNG gửi
        private readonly HashSet<string> _mt5Sent = new();
        private int _mt5Count;
        private string _mt5Status;
        // ---- Telegram (mở + đóng) ----
        private readonly TeleReport _tele = new();
        private bool _teleArmed;
        private readonly HashSet<string> _teleSeen = new();
        private readonly HashSet<string> _teleOpenSent = new();
        private readonly HashSet<string> _teleClosed = new();
        private int _teleSent;
        private string _teleStatus;

        public EntrySignal() : base()
        {
            Name = "Entry Signal (M1)";
            Description = "Gợi ý entry footprint M1: hợp lưu ≥2 vùng + 2 kịch bản (phá&hồi / chạm&đảo). Bắn nến đóng. Cần Volume Analysis. Add vào chart M1.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded() { lock (_calc) { _vaLoaded = true; _lastN = -1; } Process(); }
        protected override void OnClear()
        {
            _drag.Detach();
            lock (_calc)
            {
                _vaLoaded = false; _lastN = -1; lock (_sync) _render = null;
                // re-attach = nạp lại lịch sử, KHÔNG bắn lệnh/telegram cũ
                _mt5Armed = false; _mt5Sent.Clear(); _mt5Count = 0; _mt5Status = null;
                _teleArmed = false; _teleSeen.Clear(); _teleOpenSent.Clear(); _teleClosed.Clear(); _teleSent = 0; _teleStatus = null;
            }
        }
        protected override void OnUpdate(UpdateArgs args)
        {
            PollTeleTest();   // nút gửi thử chạy độc lập với Volume Analysis
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
            public int Idx;       // vị trí trong list B
            public int HdIdx;     // chỉ số HistoricalData tuyệt đối (đọc footprint)
            public DateTime Time;
            public double O, H, L, C, Vol, Delta, Cum, Vwap, Vma, Vratio;
            public int SinceGap;
            public int Trend;    // proxy bias TPO: dấu (close − close cách TrendLookback nến) — dùng khi bật lọc thuận xu hướng
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
            public DateTime ReadyTime, ExpireTime; public bool IsVwap;
            public string State; public int BrkBar; public int Cool; public string PrevRel;
            public int ArmLBar = -999, ArmSBar = -999; public double ArmLLow, ArmSHigh;   // KB4 arm→confirm
        }

        private sealed class Sig
        {
            public int Idx; public DateTime Time; public int Side;
            public string Scen; public char Grade; public double Entry, Sl, Tp1, Tp2, RiskT, Rr2;
            public int Confl;        // số vùng THỰC SỰ kích hoạt cùng setup (gộp trigger)
            public int Cluster;      // số vùng NẰM TRONG cụm quanh giá vào (confluence "mắt nhìn") — dùng để lọc
            public double Vsa; public bool Climax; public int Trend; public List<string> Why = new();
            public string Outcome = "running";
            public DateTime OutTime; // nến chạm SL/TP (để vẽ khối tới đúng chỗ kết thúc)
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
                    if (n == _lastN) return;          // chỉ chạy khi có nến mới đóng (tránh rescan mỗi tick)

                    var B = BuildBars(hd, n);
                    if (B.Count < VsaPeriod + 5) { _lastN = n; return; }

                    var pool = BuildPool(hd, B);
                    var sigs = Scan(hd, B, pool);
                    foreach (var s in sigs) Simulate(B, s);

                    if (Mt5Bridge) EmitMt5(sigs, B);
                    if (TeleAlerts) EmitTele(sigs, B);

                    // lọc hiển thị NGAY trong Process (paint không đụng HistoricalData).
                    // ShowAllHistory → vẽ MỌI tín hiệu (paint tự cull theo trục X nên không nặng).
                    int minIdx = B.Count - 1 - DisplayBars;
                    var show = ShowAllHistory ? sigs : sigs.Where(s => s.Idx >= minIdx || s.Outcome == "running").ToList();

                    double now = B[B.Count - 1].C;
                    var clusters = CurrentClusters(pool, B[B.Count - 1].Time, now);

                    lock (_sync) _render = new RenderState { Sigs = show, Clusters = clusters, Panel = BuildPanel(show, now), Digits = _digits };
                    _lastN = n;
                }
                catch { /* giữ indicator sống; giữ _render cũ */ }
            }
        }

        // ================= dựng nến + số dẫn xuất =================
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
            _vaCov = cov; _vaTot = B.Count; _vaFirst = first;   // nến cũ hơn _vaFirst chưa có footprint → không thể bắn (Δ=0)
            double csPV = 0, csV = 0, cum = 0, rollSum = 0;
            var q = new Queue<double>();
            for (int i = 0; i < B.Count; i++)
            {
                var b = B[i];
                bool gap = i > 0 && (b.Time - B[i - 1].Time).TotalMinutes > 30;
                if (gap) { csPV = 0; csV = 0; }
                double tp = (b.H + b.L + b.C) / 3.0; csPV += tp * b.Vol; csV += b.Vol;
                b.Vwap = csV > 0 ? csPV / csV : b.C;
                cum += b.Delta; b.Cum = cum;
                // SMA volume rolling (VsaPeriod nến GỒM nến hiện tại) — O(1)/nến
                q.Enqueue(b.Vol); rollSum += b.Vol;
                if (q.Count > VsaPeriod) rollSum -= q.Dequeue();
                b.Vma = q.Count > 0 ? rollSum / q.Count : b.Vol;
                b.Vratio = b.Vma > 1e-9 ? b.Vol / b.Vma : 0;
                b.SinceGap = gap ? 0 : (i > 0 ? B[i - 1].SinceGap + 1 : 999);
            }
            // proxy xu hướng (TPO bias không có trong data → dùng close vs close TrendLookback nến ~8h,
            // KHỚP RUNNER v5; EMA30/120 quá nhanh, ngay sau phá đảo chiều còn chỉ hướng cũ).
            int lb = Math.Max(1, TrendLookback);
            for (int i = 0; i < B.Count; i++)
                B[i].Trend = i >= lb ? Math.Sign(B[i].C - B[i - lb].C) : 0;
            return B;
        }

        // ================= dựng pool vùng từ M1 =================
        private List<PZone> BuildPool(HistoricalData hd, List<Bar> B)
        {
            var pool = new List<PZone>();
            double rowStep = _tick * Math.Max(1, RowTicks);

            // ---- blocks phiên (đổi nhãn Á/Âu/Mỹ hoặc gap>SessionGap) ----
            var sBlocks = SplitBlocks(hd, SessionGapMin);
            // LookbackSessions=0 → dựng vùng cho MỌI phiên (mỗi vùng vẫn tự hết hạn sau ZoneExpireDays,
            // nên scan chỉ bắn nơi vùng còn sống). Đây là fix bug "số entry chững ~4": trước đây chỉ
            // 12 phiên cuối có session-zone → lịch sử bị đói vùng → thiếu hợp lưu. Nay khớp backtest.
            int startBlk = LookbackSessions > 0 ? Math.Max(0, sBlocks.Count - 1 - LookbackSessions) : 0;
            for (int i = startBlk; i < sBlocks.Count - 1; i++)   // bỏ block đang chạy
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

            // ---- ngày (tách bằng gap>DayGap) → mức D-1 ----
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
            // VWAP động (giá cập nhật theo từng bar khi scan)
            pool.Add(new PZone { Price = 0, Kind = "VWAP", Strength = 64, ReadyTime = DateTime.MinValue, ExpireTime = DateTime.MaxValue, IsVwap = true });
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

        // ================= máy trạng thái 2 kịch bản (KHỚP entry_month.py) =================
        private List<Sig> Scan(HistoricalData hd, List<Bar> B, List<PZone> pool)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;                 // BỎ nến đang hình thành → không repaint
            int buf = SlBuf;
            foreach (var z in pool) { z.State = "idle"; z.BrkBar = -999; z.Cool = -999; z.PrevRel = null; z.ArmLBar = -999; z.ArmSBar = -999; }
            var vwapZone = pool.FirstOrDefault(z => z.IsVwap);

            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i]; double px = b.C;
                if (vwapZone != null) vwapZone.Price = b.Vwap;
                bool gated = b.Vol >= VolFloor && b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;

                if (!gated)
                {
                    foreach (var z in pool)
                    {
                        if (b.Time < z.ReadyTime || b.Time > z.ExpireTime) continue;
                        if (double.IsNaN(z.Price) || z.Price <= 0) continue;
                        z.PrevRel = px > z.Price ? "above" : "below";   // nhị phân, khớp Python
                    }
                    continue;
                }

                foreach (var z in pool)
                {
                    if (b.Time < z.ReadyTime || b.Time > z.ExpireTime) continue;
                    double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                    string rel = b.C > zp + buf * _tick ? "above" : b.C < zp - buf * _tick ? "below" : "in";
                    double dist = Math.Abs(px - zp) / _tick;
                    if ((dist > ArmDistTicks && z.State == "idle") || i - z.Cool < Cooldown) { z.PrevRel = rel; continue; }

                    double zlo = zp - buf * _tick, zhi = zp + buf * _tick;
                    bool tagged = b.L <= zhi && b.H >= zlo;
                    bool up = z.PrevRel == "below", dn = z.PrevRel == "above";
                    bool bu = b.C > zhi && b.H > zp && b.Brat >= 0.5 && b.Delta > 0 && b.Vratio >= VsaGate && (z.PrevRel == "below" || z.PrevRel == "in");
                    bool bd = b.C < zlo && b.L < zp && b.Brat >= 0.5 && b.Delta < 0 && b.Vratio >= VsaGate && (z.PrevRel == "above" || z.PrevRel == "in");
                    if (bu) { z.State = "broke_up"; z.BrkBar = i; }
                    else if (bd) { z.State = "broke_dn"; z.BrkBar = i; }

                    bool em = false;
                    if (z.State == "broke_up" && i - z.BrkBar > 0 && i - z.BrkBar <= RetestBars)
                    {
                        if (b.C < zp - buf * _tick) z.State = "idle";
                        else if (b.L <= zp + RetestTol * _tick && b.L >= zp - RetestHoldBuf * _tick && LongSignal(b, out var w) && (!AbsorptionFilter || DeltaOk(B, i, +1)))
                            em = Emit(raw, B, pool, i, +1, "KB1 phá&hồi", Math.Min(b.L, zp), w, 'A', zp);   // b.L≥vùng-buf: hồi GIỮ vùng (không bắt dao rơi)
                        if (em) { z.Cool = i; z.State = "idle"; }
                    }
                    else if (z.State == "broke_dn" && i - z.BrkBar > 0 && i - z.BrkBar <= RetestBars)
                    {
                        if (b.C > zp + buf * _tick) z.State = "idle";
                        else if (b.H >= zp - RetestTol * _tick && b.H <= zp + RetestHoldBuf * _tick && ShortSignal(b, out var w) && (!AbsorptionFilter || DeltaOk(B, i, -1)))
                            em = Emit(raw, B, pool, i, -1, "KB1 phá&hồi", Math.Max(b.H, zp), w, 'A', zp);   // b.H≤vùng+buf: hồi GIỮ vùng (không bắt dao rơi)
                        if (em) { z.Cool = i; z.State = "idle"; }
                    }
                    if (!em && EnableS2 && (z.State == "idle" || z.State == "broke_up" || z.State == "broke_dn"))
                    {
                        if (up && tagged && b.C < zhi && ShortSignal(b, out var w) && (AbsorptionFilter ? DeltaOk(B, i, -1) : b.Delta < 0))
                        {
                            bool wall = !RequireWallForS2 || Absorption(HdBar(hd, b.HdIdx), b.H, -1) || (S2ClimaxOverride && b.Vratio >= VsaClimax);
                            if (wall)
                                if (Emit(raw, B, pool, i, -1, "KB2 chạm&đảo", Math.Max(b.H, zp), Append(w, b.Vratio >= VsaClimax ? "climax" : "hấp thụ"), 'B', zp)) { z.Cool = i; z.State = "idle"; }
                        }
                        else if (dn && tagged && b.C > zlo && LongSignal(b, out var w2) && (AbsorptionFilter ? DeltaOk(B, i, +1) : b.Delta > 0))
                        {
                            bool wall = !RequireWallForS2 || Absorption(HdBar(hd, b.HdIdx), b.L, +1) || (S2ClimaxOverride && b.Vratio >= VsaClimax);
                            if (wall)
                                if (Emit(raw, B, pool, i, +1, "KB2 chạm&đảo", Math.Min(b.L, zp), Append(w2, b.Vratio >= VsaClimax ? "climax" : "hấp thụ"), 'B', zp)) { z.Cool = i; z.State = "idle"; em = true; }
                        }
                    }

                    // KB4 (phụ, tắt mặc định): ĐẢO CHIỀU arm→confirm (đặc tả user). Rút râu = ARM (KHÔNG cần
                    // vol); nến tăng/giảm mạnh vol≥High trong ArmConfirmWindow cây = CONFIRM → vào. Gate cụm≥2
                    // (Dedup) tự lọc → chỉ giữ ca ở hợp lưu. Backtest +0.15R@1.5R (yếu hơn lõi, hơn nhiễu đơn-vùng).
                    if (EnableS4ArmConfirm)
                    {
                        if (b.C < zp - buf * _tick) z.ArmLBar = -999;   // phá xuống → hủy arm mua
                        if (b.C > zp + buf * _tick) z.ArmSBar = -999;   // phá lên → hủy arm bán
                        if (!em && i - z.Cool >= Cooldown)              // CONFIRM (dùng arm từ cây trước; ưu tiên sau KB1/KB2)
                        {
                            if (z.ArmLBar >= 0 && i - z.ArmLBar > 0 && i - z.ArmLBar <= ArmConfirmWindow
                                && b.Brat >= BodyStrong && b.Delta > 0 && b.C > zp && b.Cpos >= 0.6 && b.Vratio >= VsaGate)
                            { if (Emit(raw, B, pool, i, +1, "KB4 đảo chiều", Math.Min(z.ArmLLow, zp), new List<string> { "rút râu→xác nhận", $"Δ{b.Delta:+0;-0}", $"VSA {b.Vratio:0.0}x" }, 'B', zp)) { z.Cool = i; z.ArmLBar = -999; em = true; } }
                            else if (z.ArmSBar >= 0 && i - z.ArmSBar > 0 && i - z.ArmSBar <= ArmConfirmWindow
                                && b.Brat >= BodyStrong && b.Delta < 0 && b.C < zp && b.Cpos <= 0.4 && b.Vratio >= VsaGate)
                            { if (Emit(raw, B, pool, i, -1, "KB4 đảo chiều", Math.Max(z.ArmSHigh, zp), new List<string> { "rút râu→xác nhận", $"Δ{b.Delta:+0;-0}", $"VSA {b.Vratio:0.0}x" }, 'B', zp)) { z.Cool = i; z.ArmSBar = -999; em = true; } }
                        }
                        if (b.Rng > 0)                                 // ARM (đặt cuối → hiệu lực cho cây sau); rút râu KHÔNG cần vol
                        {
                            if (b.L <= zp + RetestTol * _tick && b.L >= zp - 12 * _tick && b.C > zp && b.LW >= WickFrac * b.Rng && b.Cpos >= 0.5)
                            { z.ArmLBar = i; z.ArmLLow = b.L; }
                            if (b.H >= zp - RetestTol * _tick && b.H <= zp + 12 * _tick && b.C < zp && b.UW >= WickFrac * b.Rng && b.Cpos <= 0.5)
                            { z.ArmSBar = i; z.ArmSHigh = b.H; }
                        }
                    }
                    z.PrevRel = rel;
                }

                // KB3 (phụ, tắt mặc định): climax PHÁ qua CỤM ≥2 — bắt nến tím momentum xuyên cụm
                // (vd 20:31 4051.8, đã hụt KB1/KB2). Edge yếu (+0.07..0.11R@2R ~ hòa vốn) → grade C.
                if (EnableS3ClimaxBreak && b.Vratio >= VsaClimax && i > 0)
                {
                    double pc = B[i - 1].C;
                    foreach (var c in ClustersNear(pool, b.Time, b.L, b.H))
                    {
                        if (pc < c - 2 * _tick && b.C > c && b.Cpos >= 0.6 && b.Delta >= 0 && b.Brat >= 0.4)
                        { Emit(raw, B, pool, i, +1, "KB3 climax phá cụm", Math.Min(b.L, c), new List<string> { "phá cụm", $"Δ{b.Delta:+0;-0}", $"VSA {b.Vratio:0.0}x tím" }, 'C', c); break; }
                        if (pc > c + 2 * _tick && b.C < c && b.Cpos <= 0.4 && b.Delta <= 0 && b.Brat >= 0.4)
                        { Emit(raw, B, pool, i, -1, "KB3 climax phá cụm", Math.Max(b.H, c), new List<string> { "phá cụm", $"Δ{b.Delta:+0;-0}", $"VSA {b.Vratio:0.0}x tím" }, 'C', c); break; }
                    }
                }
            }
            return Dedup(raw);
        }

        private HistoryItemBar HdBar(HistoricalData hd, int absIdx)
            => (absIdx >= 0 && absIdx < hd.Count) ? hd[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;
        private static List<string> Append(List<string> w, string s) { var r = new List<string>(w); r.Add(s); return r; }

        // Lọc HẤP THỤ (research feed footprint 6 tháng): giữ lệnh khi delta NHỊP-3-NẾN-chạm-vùng KHÔNG
        // rõ cùng phía lệnh (long giữ khi ddom≤0 = bán bị hấp thụ; short giữ khi ddom≥0 = mua bị hấp thụ).
        // Không có dữ liệu delta → giữ (không loại oan). Ngưỡng 0 = tối ưu backtest.
        private static bool DeltaOk(List<Bar> B, int i, int side)
        {
            double d = 0, v = 0;
            for (int k = Math.Max(0, i - 2); k <= i; k++) { d += B[k].Delta; v += B[k].Vol; }
            if (v <= 0) return true;
            double ddom = d / v;
            return side > 0 ? ddom <= 0 : ddom >= 0;
        }

        // Tường hấp thụ (footprint per-level): tại mức cực trị có 1 mức volume vượt trội +
        // dominance ngược chiều tiếp cận. side=+1 hấp thụ tại ĐÁY (mua), -1 tại ĐỈNH (bán).
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

        private bool LongSignal(Bar b, out List<string> why)
        {
            why = new List<string>();
            bool ur = b.LW >= WickFrac * b.Rng && b.Cpos >= 0.55 && b.Delta >= 0;
            bool su = b.Brat >= BodyStrong && b.Ddom >= DeltaDom && Math.Abs(b.Delta) >= DeltaAbsMin && b.Delta > 0 && b.Cpos >= 0.6;
            if (b.Vratio >= VsaGate && (ur || su))
            {
                if (ur) why.Add("rút râu dưới"); if (su) why.Add("thân mạnh");
                why.Add($"Δ{b.Delta:+0;-0}"); why.Add($"VSA {b.Vratio:0.0}x{(b.Vratio >= VsaClimax ? " tím" : "")}");
                return true;
            }
            return false;
        }
        private bool ShortSignal(Bar b, out List<string> why)
        {
            why = new List<string>();
            bool dr = b.UW >= WickFrac * b.Rng && b.Cpos <= 0.45 && b.Delta <= 0;
            bool sd = b.Brat >= BodyStrong && b.Ddom <= -DeltaDom && Math.Abs(b.Delta) >= DeltaAbsMin && b.Delta < 0 && b.Cpos <= 0.4;
            if (b.Vratio >= VsaGate && (dr || sd))
            {
                if (dr) why.Add("rút râu trên"); if (sd) why.Add("thân mạnh");
                why.Add($"Δ{b.Delta:+0;-0}"); why.Add($"VSA {b.Vratio:0.0}x{(b.Vratio >= VsaClimax ? " tím" : "")}");
                return true;
            }
            return false;
        }

        // Số vùng KHÁC NHAU (theo giá) đang còn hiệu lực nằm trong ConfluenceTol quanh giá vùng kích hoạt.
        // = "hợp lưu mắt nhìn" (cụm ≥2 vùng chồng nhau), gồm cả vùng không tự bắn. Backtest: gate cụm≥2
        // cho edge cao hơn gate theo-trigger (WR 43%→49%, exp +0.30→+0.48).
        private int ClusterCount(List<PZone> pool, DateTime t, double price)
        {
            var seen = new HashSet<long>();
            foreach (var z in pool)
            {
                if (z.IsVwap) continue;   // khớp backtest (pool cụm KHÔNG gồm VWAP) — giữ đúng edge đã validate
                if (t < z.ReadyTime || t > z.ExpireTime) continue;
                double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                if (Math.Abs(zp - price) / _tick > ConfluenceTol) continue;
                seen.Add((long)Math.Round(zp / _tick));
            }
            return seen.Count;
        }

        // Tâm các CỤM ≥MinConfluence vùng (gộp ≤ConfluenceTol) đang sống gần [lo..hi]. Dùng cho KB3.
        private List<double> ClustersNear(List<PZone> pool, DateTime t, double lo, double hi)
        {
            var seen = new HashSet<long>(); var ps = new List<double>();
            foreach (var z in pool)
            {
                if (z.IsVwap) continue;   // khớp backtest cụm
                if (t < z.ReadyTime || t > z.ExpireTime) continue;
                double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                if (zp < lo - 3 || zp > hi + 3) continue;
                if (seen.Add((long)Math.Round(zp / _tick))) ps.Add(Math.Round(zp / _tick) * _tick);
            }
            ps.Sort();
            var res = new List<double>(); int k = 0;
            while (k < ps.Count)
            {
                int j = k; var grp = new List<double> { ps[k] };
                while (j + 1 < ps.Count && (ps[j + 1] - grp[0]) / _tick <= ConfluenceTol) { grp.Add(ps[j + 1]); j++; }
                if (grp.Count >= MinConfluence) res.Add(grp.Average());
                k = j + 1;
            }
            return res;
        }

        private bool Emit(List<Sig> raw, List<Bar> B, List<PZone> pool, int i, int side, string scen, double anchor, List<string> why, char grade, double zonePrice)
        {
            var b = B[i]; double entry = b.C; double sl, risk;
            double slCap = Math.Max(SlCap, SlFloor);       // clamp: tránh SlFloor>SlCap tắt hết tín hiệu
            if (side > 0) { sl = Math.Min(anchor - SlBuf * _tick, entry - SlFloor); risk = (entry - sl) / _tick; }
            else { sl = Math.Max(anchor + SlBuf * _tick, entry + SlFloor); risk = (sl - entry) / _tick; }
            if (risk <= 0 || risk * _tick > slCap) return false;
            double rDollar = risk * _tick;
            double tp1 = side > 0 ? entry + RR * rDollar : entry - RR * rDollar;
            double tp2 = tp1, rr2 = RR;
            if (ExtendToNextZone)
            {
                double? nz = NextZone(pool, b.Time, entry, side);
                if (nz.HasValue)
                {
                    double cand = side > 0 ? nz.Value - 2 * _tick : nz.Value + 2 * _tick;
                    double rrc = Math.Abs(cand - entry) / rDollar;
                    if (rrc >= NextZoneMinR) { tp2 = cand; rr2 = rrc; }
                }
            }
            raw.Add(new Sig { Idx = i, Time = b.Time, Side = side, Scen = scen, Grade = grade, Entry = entry, Sl = sl,
                Tp1 = tp1, Tp2 = tp2, RiskT = risk, Rr2 = rr2, Vsa = b.Vratio, Climax = b.Vratio >= VsaClimax, Trend = b.Trend, Why = why,
                Cluster = ClusterCount(pool, b.Time, zonePrice) });
            return true;
        }

        private double? NextZone(List<PZone> pool, DateTime t, double entry, int side)
        {
            double? best = null;
            foreach (var z in pool)
            {
                if (z.IsVwap || t < z.ReadyTime || t > z.ExpireTime) continue;
                double p = z.Price; if (double.IsNaN(p) || p <= 0) continue;
                if (side > 0 && p > entry + 5 * _tick) best = best.HasValue ? Math.Min(best.Value, p) : p;
                if (side < 0 && p < entry - 5 * _tick) best = best.HasValue ? Math.Max(best.Value, p) : p;
            }
            return best;
        }

        // gộp confluence (KHỚP entry_month.py): tín hiệu cùng phía, ≤6 nến & ≤DedupTol tick = 1 setup;
        // confl = SỐ VÙNG cùng kích hoạt (số raw gộp). Gate confl ≥ MinConfluence.
        private List<Sig> Dedup(List<Sig> raw)
        {
            var outp = new List<Sig>();
            foreach (var s in raw.OrderBy(x => x.Idx))
            {
                var m = outp.FirstOrDefault(k => k.Side == s.Side && Math.Abs(s.Idx - k.Idx) <= 6 && Math.Abs(s.Entry - k.Entry) / _tick <= DedupTol);
                if (m == null) { s.Confl = 1; outp.Add(s); }
                else { m.Confl++; m.Cluster = Math.Max(m.Cluster, s.Cluster); }
            }
            // GATE theo cụm-gần (confluence "mắt nhìn"): giữ setup có ≥MinConfluence vùng chồng quanh giá vào.
            var kept = outp.Where(s => s.Cluster >= MinConfluence);
            // (tuỳ chọn) lọc THUẬN xu hướng: bỏ LONG khi trend xuống / SHORT khi trend lên.
            // Backtest dxFeed 5-7/2026: giúp nhánh cluster≥2 (+0.11→+0.16R, cứu tháng 7); nhưng CẮT bớt
            // nhánh chạm&đảo ngược-trend đang thắng → mặc định TẮT, bật nếu muốn ưu tiên momentum.
            if (TrendFilter)
                kept = kept.Where(s => s.Trend == 0 || (s.Side > 0 ? s.Trend > 0 : s.Trend < 0));
            return kept.ToList();
        }

        private void Simulate(List<Bar> B, Sig s)   // bi quan: SL trước TP (chỉ để hiển thị outcome); ghi OutTime
        {
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

        // ================= CẦU NỐI MT5 + TELEGRAM =================
        // Process() quét LẠI toàn bộ lịch sử mỗi nến → dùng đúng khung chống-trùng của RunnerSignal:
        //   1) chỉ xét tín hiệu ở nến VỪA ĐÓNG (Idx == B.Count-2)
        //   2) _armed: lần quét đầu sau attach/reload chỉ NẠP id, không bắn
        //   3) tuổi tín hiệu ≤ MaxAgeSec so với đồng hồ (bar.Time = mốc MỞ nến, UTC)
        //   4) id tất định (symbol|phút|hướng|kịch bản) → không lặp; EA lưu id đã xử lý ra file
        private static bool IsBreak(Sig s) => s.Scen != null && s.Scen.StartsWith("1");   // "1 pha&hoi" vs "2 cham&dao"
        private string SigId(Sig s) =>
            $"{Symbol?.Name ?? "X"}|{s.Time:yyyyMMddHHmm}|{(s.Side > 0 ? "B" : "S")}|{(IsBreak(s) ? "P" : "D")}";
        private static string ReasonVN(Sig s) =>
            IsBreak(s) ? "phá vùng → hồi giữ gốc → vào nến tiếp diễn"
                       : "chạm vùng hợp lưu → đảo chiều (hấp thụ)";

        private string Mt5FilesDir()
        {
            string dir = Mt5Dir?.Trim();
            if (!string.IsNullOrEmpty(dir)) return dir;
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                                "MetaQuotes", "Terminal", "Common", "Files");
        }

        private void EmitMt5(List<Sig> sigs, List<Bar> B)
        {
            try
            {
                if (B.Count < 3) return;
                int lastClosed = B.Count - 2;
                double barMin = (B[B.Count - 1].Time - B[B.Count - 2].Time).TotalMinutes;
                if (barMin <= 0 || barMin > 60) barMin = 1;

                if (!_mt5Armed)
                {
                    foreach (var s0 in sigs) _mt5Sent.Add(SigId(s0));
                    _mt5Armed = true;
                    double skew = (DateTime.UtcNow - B[B.Count - 1].Time.AddMinutes(barMin)).TotalSeconds;
                    _mt5Status = $"nạp {_mt5Sent.Count} tín hiệu cũ (KHÔNG gửi) · lệch feed↔đồng hồ {skew:0}s";
                    return;
                }

                foreach (var s in sigs.Where(x => x.Idx == lastClosed))
                {
                    string id = SigId(s);
                    if (_mt5Sent.Contains(id)) continue;
                    if (Mt5OnlyGradeA && s.Grade != 'A') { _mt5Sent.Add(id); continue; }
                    var closeUtc = s.Time.AddMinutes(barMin);
                    double age = (DateTime.UtcNow - closeUtc).TotalSeconds;
                    if (age > Mt5MaxAgeSec || age < -Mt5MaxAgeSec)
                    {
                        _mt5Sent.Add(id);
                        _mt5Status = $"BỎ {s.Time:dd/MM HH:mm} — lệch đồng hồ {age:0}s (>{Mt5MaxAgeSec}s)";
                        continue;
                    }
                    WriteCmd(s, id, closeUtc);
                    _mt5Sent.Add(id);
                }
            }
            catch (Exception ex) { _mt5Status = "LỖI cầu nối: " + ex.Message; }
        }

        private void WriteCmd(Sig s, string id, DateTime closeUtc)
        {
            var ci = CultureInfo.InvariantCulture;
            string dir = Mt5FilesDir();
            Directory.CreateDirectory(dir);
            string fname = string.IsNullOrWhiteSpace(Mt5CmdFile) ? "entry_cmd.jsonl" : Mt5CmdFile.Trim();
            string path = Path.Combine(dir, fname);

            double slDist = s.RiskT * _tick;   // KHOẢNG CÁCH (giá futures↔spot lệch basis, chỉ truyền khoảng cách)
            double sizeMult = s.Cluster >= NhoiConflGate ? NhoiMult : 1.0;   // nhồi khi hợp lưu mạnh (mặc định 1 = tắt)
            var sb = new StringBuilder();
            sb.Append('{')
              .Append("\"id\":\"").Append(id).Append("\",")
              .Append("\"ts_utc\":\"").Append(closeUtc.ToString("yyyy-MM-dd HH:mm:ss", ci)).Append("\",")
              .Append("\"src\":\"").Append(Symbol?.Name ?? "?").Append("\",")
              .Append("\"branch\":\"").Append(IsBreak(s) ? "SCALP_BR" : "SCALP_REV").Append("\",")
              .Append("\"side\":\"").Append(s.Side > 0 ? "BUY" : "SELL").Append("\",")
              .Append("\"sl_dist\":").Append(slDist.ToString("0.###", ci)).Append(',')
              .Append("\"rr\":").Append(RR.ToString("0.##", ci)).Append(',')
              .Append("\"grade\":\"").Append(s.Grade).Append("\",")
              .Append("\"vsa\":").Append(s.Vsa.ToString("0.00", ci)).Append(',')
              .Append("\"cluster\":").Append(s.Cluster.ToString(ci)).Append(',')
              .Append("\"size_mult\":").Append(sizeMult.ToString("0.##", ci)).Append(',')
              .Append("\"src_entry\":").Append(s.Entry.ToString("0.0##", ci)).Append(',')
              .Append("\"src_sl\":").Append(s.Sl.ToString("0.0##", ci)).Append(',')
              .Append("\"src_tp\":").Append(s.Tp1.ToString("0.0##", ci)).Append(',')
              .Append("\"dry\":").Append(Mt5DryRun ? "true" : "false")
              .Append("}\n");

            using (var fs = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite))
            using (var w = new StreamWriter(fs, new UTF8Encoding(false)))
                w.Write(sb.ToString());

            _mt5Count++;
            _mt5Status = $"gửi {_mt5Count} · {s.Time:dd/MM HH:mm} {(s.Side > 0 ? "BUY" : "SELL")} "
                       + $"{(IsBreak(s) ? "phá&hồi" : "chạm&đảo")} SL {slDist:0.0}giá {RR:0.#}R{(Mt5DryRun ? " [DRY]" : "")}";
        }

        // ---- Telegram ----
        private void ConfigTele()
        {
            _tele.Enabled = TeleAlerts;
            _tele.BotToken = (TeleBotToken ?? "").Trim();
            _tele.ChatId = (TeleChatId ?? "").Trim();
            _tele.TzOffset = TzOffset;
            _tele.TestNow = TeleTestNow;
            _tele.ShareDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "EntrySignal");
        }
        private void PollTeleTest()
        {
            ConfigTele();
            _tele.PollTestRaw($"🔔 TEST — Entry Signal ({Symbol?.Name ?? "?"}) bot chạy OK\n— mẫu tin MỞ: 🟢 MUA · Phá&Hồi · hạng A · hợp lưu ×3\n— mẫu tin ĐÓNG (chạm TP/SL): ✅ WIN +{RR:0.#}R · giá vào→ra · thời lượng\n(nếu nhận được tin này = đường gửi OK; tin ĐÓNG sẽ tự bắn khi lệnh chạm TP/SL)");
        }

        private void EmitTele(List<Sig> sigs, List<Bar> B)
        {
            try
            {
                ConfigTele();
                if (B.Count < 3) return;
                int lastClosed = B.Count - 2;
                double barMin = (B[B.Count - 1].Time - B[B.Count - 2].Time).TotalMinutes;
                if (barMin <= 0 || barMin > 60) barMin = 1;

                if (!_teleArmed)
                {
                    foreach (var s0 in sigs)
                    {
                        string id0 = SigId(s0);
                        _teleSeen.Add(id0);
                        if (s0.Outcome != "running") _teleClosed.Add(id0);
                        else _teleOpenSent.Add(id0);   // FIX: lệnh đang chạy → coi như "đã mở" để CÒN báo ĐÓNG sau recalc (OnClear wipe _teleOpenSent giữa mở↔đóng)
                    }
                    _teleArmed = true;
                    _teleStatus = $"nạp {_teleSeen.Count} lệnh cũ (không báo) · sẵn sàng";
                    return;
                }

                foreach (var s in sigs)
                {
                    string id = SigId(s);
                    bool ok = !TeleOnlyGradeA || s.Grade == 'A';

                    // MỞ
                    if (!_teleSeen.Contains(id))
                    {
                        if (TeleAlertOpen && ok && s.Idx == lastClosed)
                        {
                            var closeUtc = s.Time.AddMinutes(barMin);
                            double age = (DateTime.UtcNow - closeUtc).TotalSeconds;
                            if (age <= TeleMaxAgeSec && age >= -TeleMaxAgeSec)
                            {
                                _tele.SendRaw(ComposeOpen(s));
                                _teleOpenSent.Add(id);
                                _teleSent++;
                                _teleStatus = $"MỞ {(s.Side > 0 ? "MUA" : "BÁN")} {(IsBreak(s) ? "phá&hồi" : "chạm&đảo")} {s.Time.AddHours(TzOffset):HH:mm} · đã gửi {_teleSent}";
                            }
                        }
                        _teleSeen.Add(id);
                    }

                    // ĐÓNG (chỉ lệnh đã báo mở)
                    if (TeleAlertClose && !_teleClosed.Contains(id) && _teleOpenSent.Contains(id)
                        && (s.Outcome == "TP" || s.Outcome == "SL"))
                    {
                        _tele.SendRaw(ComposeClose(s));
                        _teleClosed.Add(id);
                        _teleSent++;
                        _teleStatus = $"ĐÓNG {(s.Outcome == "TP" ? "✓TP" : "✗SL")} {(s.Side > 0 ? "MUA" : "BÁN")} {s.OutTime.AddHours(TzOffset):HH:mm} · đã gửi {_teleSent}";
                    }
                }
            }
            catch (Exception ex) { _teleStatus = "LỖI Telegram: " + ex.Message; }
        }

        private string ComposeOpen(Sig s)
        {
            double slPts = s.RiskT * _tick;
            double tpPts = slPts * RR;
            string dirVN = s.Side > 0 ? "🟢 MUA (LONG)" : "🔴 BÁN (SHORT)";
            string branch = IsBreak(s) ? "Phá&Hồi" : "Chạm&Đảo";
            var sb = new StringBuilder();
            sb.Append("🔔 LỆNH MỚI (Scalp)\n");
            sb.Append(dirVN).Append(" · ").Append(branch).Append(" · hạng ").Append(s.Grade)
              .Append(" · hợp lưu ×").Append(s.Cluster);
            if (NhoiMult > 1.0 && s.Cluster >= NhoiConflGate)
                sb.Append("  ⚡NHỒI ×").Append(NhoiMult.ToString("0.#"));
            sb.Append('\n');
            sb.Append("Vào (Entry): ").Append(Fmt(s.Entry)).Append('\n');
            sb.Append("SL: ").Append(Fmt(s.Sl)).Append("  (").Append(slPts.ToString("0.0")).Append(" giá)\n");
            sb.Append("TP: ").Append(Fmt(s.Tp1)).Append("  (").Append(tpPts.ToString("0.0")).Append(" giá · ").Append(RR.ToString("0.#")).Append("R)\n");
            if (ExtendToNextZone && s.Rr2 > RR + 0.05)
                sb.Append("TP2 (nới vùng kế): ").Append(Fmt(s.Tp2)).Append("  (").Append(s.Rr2.ToString("0.#")).Append("R)\n");
            sb.Append("Lý do: ").Append(ReasonVN(s)).Append('\n');
            if (s.Why != null && s.Why.Count > 0) sb.Append("• ").Append(string.Join(" · ", s.Why)).Append('\n');
            sb.Append("⏱ ").Append(s.Time.AddHours(TzOffset).ToString("HH:mm dd/MM"))
              .Append(" · ").Append(Symbol?.Name ?? "?");
            return sb.ToString();
        }

        private string ComposeClose(Sig s)
        {
            bool win = s.Outcome == "TP";
            double exit = win ? s.Tp1 : s.Sl;
            string dirVN = s.Side > 0 ? "MUA (LONG)" : "BÁN (SHORT)";
            string branch = IsBreak(s) ? "Phá&Hồi" : "Chạm&Đảo";
            string head = win ? "✅ CHỐT LỜI (TP)" : "🛑 DỪNG LỖ (SL)";
            string rRes = win ? "+" + RR.ToString("0.#") + "R" : "-1.0R";
            var sb = new StringBuilder();
            sb.Append(head).Append(" · ").Append(dirVN).Append(" · ").Append(branch).Append('\n');
            sb.Append("Kết quả: ").Append(rRes).Append('\n');
            sb.Append("Vào ").Append(Fmt(s.Entry)).Append(" → ra ").Append(Fmt(exit)).Append('\n');
            sb.Append("Mở ").Append(s.Time.AddHours(TzOffset).ToString("HH:mm"))
              .Append(" → đóng ").Append(s.OutTime.AddHours(TzOffset).ToString("HH:mm dd/MM"))
              .Append("  ·  ").Append(Dur(s.OutTime - s.Time));
            return sb.ToString();
        }

        private static string Dur(TimeSpan t)
        {
            if (t.TotalMinutes < 1) return "<1p";
            int h = (int)t.TotalHours, m = t.Minutes;
            return h > 0 ? $"{h}h{m:00}p" : $"{m}p";
        }

        private List<(double price, double strength, int side)> CurrentClusters(List<PZone> pool, DateTime now, double nowPrice)
        {
            var active = pool.Where(z => now >= z.ReadyTime && now <= z.ExpireTime && !z.IsVwap && !double.IsNaN(z.Price) && z.Price > 0)
                             .Select(z => z.Price).OrderBy(x => x).ToList();
            var res = new List<(double, double, int)>();
            int k = 0;
            while (k < active.Count)
            {
                int j = k; var grp = new List<double> { active[k] };
                while (j + 1 < active.Count && (active[j + 1] - grp[0]) / _tick <= ConfluenceTol) { grp.Add(active[j + 1]); j++; }
                if (grp.Count >= MinConfluence)
                {
                    double c = grp.Average();
                    res.Add((c, Math.Min(100, 50 + grp.Count * 12), c > nowPrice ? -1 : 1));
                }
                k = j + 1;
            }
            return res;
        }

        private List<(string, Color)> BuildPanel(List<Sig> sigs, double now)
        {
            var p = new List<(string, Color)>();
            var pool = sigs.Where(s => !OnlyAGrade || s.Grade == 'A').ToList();
            int running = pool.Count(s => s.Outcome == "running");
            int tp = pool.Count(s => s.Outcome == "TP"), sl = pool.Count(s => s.Outcome == "SL");
            int closed = tp + sl;
            string wr = closed > 0 ? $" · WR {100.0 * tp / closed:0}%" : "";
            p.Add(($"ENTRY SIGNAL (M1)   {pool.Count} tín hiệu · ✓{tp} ✗{sl} •{running}{wr}", Color.White));
            // Thống kê R lời/lỗ (1 lot: TP=+RR, SL=−1R); + R khi nhồi nếu bật
            double baseR = tp * RR - sl;
            double nhoiR = 0;
            foreach (var s in pool)
            {
                double m = (NhoiMult > 1 && s.Cluster >= NhoiConflGate) ? NhoiMult : 1;
                if (s.Outcome == "TP") nhoiR += m * RR; else if (s.Outcome == "SL") nhoiR -= m;
            }
            string rLine = closed > 0
                ? $"Lời/lỗ: {baseR:+0.0;-0.0}R (1 lot) · TB {baseR / closed:+0.00}R/lệnh" + (NhoiMult > 1 ? $" · nhồi ×{NhoiMult:0.#}≥{NhoiConflGate}: {nhoiR:+0.0;-0.0}R" : "")
                : "Lời/lỗ: — (chưa có lệnh đóng)";
            p.Add((rLine, closed > 0 && baseR < 0 ? Color.FromArgb(240, 140, 140) : Color.FromArgb(120, 230, 150)));
            // cảnh báo vùng quét thực tế: nến cũ hơn _vaFirst chưa có footprint → không bắn được
            if (_vaTot > 0 && _vaCov < (int)(_vaTot * 0.98) && _vaFirst != DateTime.MinValue)
                p.Add(($"⚠ footprint chỉ có {_vaCov}/{_vaTot} nến (từ {_vaFirst:dd/MM HH:mm}) — tăng số bar tính Volume Analysis để thấy lịch sử xa hơn", Color.FromArgb(255, 190, 120)));
            var recent = pool.OrderByDescending(s => s.Idx).Take(Math.Max(2, PanelRows)).ToList();
            if (recent.Count == 0) { p.Add(("(chưa có setup hợp lưu ≥2)", Color.Gray)); return p; }
            foreach (var s in recent)
            {
                Color col = s.Side > 0 ? LongColor : ShortColor;
                string dir = s.Side > 0 ? "LONG" : "SHORT";
                string oc = s.Outcome == "TP" ? "✓" : s.Outcome == "SL" ? "✗" : "•";
                p.Add(($"{oc} {dir} {s.Grade} {s.Scen} | E {Fmt(s.Entry)} SL {Fmt(s.Sl)} ({s.RiskT * _tick:0.0}đ) TP {Fmt(s.Tp1)}→{Fmt(s.Tp2)} ({s.Rr2:0.0}R)", col));
                p.Add(($"    hợp lưu ×{s.Cluster} · {string.Join(" · ", s.Why)}", Color.Silver));
            }
            if (TrendFilter) p.Add(("↕ lọc thuận xu hướng: BẬT", Color.FromArgb(180, 200, 160)));
            if (Mt5Bridge)
                p.Add((("⇄ MT5: " + (_mt5Status ?? "chờ tín hiệu…")), Color.FromArgb(255, 200, 120)));
            if (TeleAlerts)
                p.Add((("📨 Tele: " + (_teleStatus ?? "chờ tín hiệu…")), Color.FromArgb(150, 210, 255)));
            return p;
        }

        // ================= RENDER =================
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
                        if (OnlyAGrade && s.Grade != 'A') continue;
                        bool active = s.Outcome == "running";
                        if (!active && !ShowClosed) continue;

                        // KHỐI kéo từ nến vào → nến kết thúc (đã đóng) hoặc mép phải (đang chạy)
                        float xE = (float)conv.GetChartX(s.Time);
                        float xEnd = active ? clip.Right : (float)conv.GetChartX(s.OutTime);
                        if (xEnd > clip.Right) xEnd = clip.Right;
                        if (xEnd < xE + 10) xEnd = xE + 10;                 // khối tối thiểu để nhìn thấy
                        if (xEnd < clip.Left || xE > clip.Right) continue;   // cull ngoài màn hình
                        float yE = (float)conv.GetChartY(s.Entry), ySL = (float)conv.GetChartY(s.Sl), yTP = (float)conv.GetChartY(s.Tp1);
                        float yTop = Math.Min(ySL, yTP), yBot = Math.Max(ySL, yTP);
                        if (yBot < clip.Top || yTop > clip.Bottom) continue;
                        Color dir = s.Side > 0 ? LongColor : ShortColor;
                        float xb = Math.Max(xE, clip.Left); float bw = Math.Max(1, xEnd - xb);
                        int fillA = active ? Math.Max(18, RiskBoxOpacity) : Math.Max(10, RiskBoxOpacity / 2);
                        int lineA = active ? 255 : 150;

                        // ---- KHỐI position-tool: xanh = LỜI (E→TP), đỏ = LỖ (E→SL) ----
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
                            using (var pv = new Pen(Color.FromArgb(active ? 220 : 110, dir), 1.5f)) gr.DrawLine(pv, xE, yTop, xE, yBot);   // cạnh trái = mốc nến vào
                        }

                        // điểm vào: chấm tròn viền trắng (luôn định vị được entry)
                        if (yE >= clip.Top - 6 && yE <= clip.Bottom + 6)
                        {
                            using (var bd = new SolidBrush(active ? dir : Color.FromArgb(210, dir))) gr.FillEllipse(bd, xE - 4.5f, yE - 4.5f, 9, 9);
                            using (var pw = new Pen(Color.FromArgb(active ? 255 : 190, Color.White), 1.4f)) gr.DrawEllipse(pw, xE - 4.5f, yE - 4.5f, 9, 9);
                        }
                        if (ShowArrows) DrawArrow(gr, xE, yE, s.Side, active ? dir : Color.FromArgb(180, dir), Math.Max(4, active ? ArrowSize : ArrowSize - 2));

                        if (ShowLabels)
                        {
                            string lbl = (s.Side > 0 ? "LONG " : "SHORT ") + s.Grade + " ×" + s.Cluster + (active ? " · " + s.Scen : "");
                            LabelBox(gr, fLbl, xE + 10, s.Side > 0 ? yBot + 4 : yTop - 20, lbl, active ? dir : Color.FromArgb(210, dir));
                        }
                        if (active && ShowChips)
                        {
                            Chip(gr, fChip, clip.Right, yE, "E " + Fmt(s.Entry), dir, true);
                            Chip(gr, fChip, clip.Right, ySL, "SL " + Fmt(s.Sl) + " (" + (s.RiskT * _tick).ToString("0.0") + "đ)", SlLineColor, true);
                            Chip(gr, fChip, clip.Right, yTP, "TP " + Fmt(s.Tp1) + "  " + s.Rr2.ToString("0.0") + "R", TpLineColor, true);
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
            catch { /* nuốt lỗi vẽ, giữ chuỗi paint sống */ }
            finally { gr.SetClip(prevClip); }
        }

        // ---- helper vẽ ----
        private static GraphicsPath Round(float x, float y, float w, float h, float r)
        {
            var p = new GraphicsPath(); float d = r * 2;
            p.AddArc(x, y, d, d, 180, 90); p.AddArc(x + w - d, y, d, d, 270, 90);
            p.AddArc(x + w - d, y + h - d, d, d, 0, 90); p.AddArc(x, y + h - d, d, d, 90, 90);
            p.CloseFigure(); return p;
        }
        private static Color TextOn(Color bg)
            => (0.299 * bg.R + 0.587 * bg.G + 0.114 * bg.B) > 150 ? Color.FromArgb(20, 20, 24) : Color.White;

        // chip bo góc; anchorRight=true → mép phải của chip nằm tại x (mọc sang trái), ngược lại mọc sang phải
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
