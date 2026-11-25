// ============================================================================
//  SessionZones  —  Phiên Á/Âu/Mỹ + Vùng cần quan tâm cho QUANTOWER
// ============================================================================
//  Add vào chart bất kỳ (M1, M5, M30...) — TỰ LẤY dữ liệu M30 của cùng symbol
//  qua Symbol.GetHistory() nếu chart hiện tại không phải M30 (xem OnInit()).
//  Gộp nến 30' thành khối phiên Á/Âu/Mỹ (theo giờ-trong-ngày + gap tách cuối
//  tuần/bảo trì), gợi ý "Mỹ ưu tiên gì" cho Telegram, và vẽ:
//    VÙNG MẠNH (PLAN-VUNG-MANH.md, CHƯA KIỂM ĐỊNH): cụm ≥3 đỉnh/đáy M30 bật lại ≥1 U +
//      hợp lưu với mức của phiên/tuần ĐÃ ĐÓNG (VWAP/±1σ, VAH/VAL hôm qua & tuần trước,
//      hộp HVN); xanh hỗ trợ / đỏ kháng cự / vàng ≥3 nhóm có HVN.
//    HỘP HVN (2026-11-25, §10–11, v2 §13): cụm khối lượng LỚN và ĐỀU (thân chữ D, đấu giá xong) của
//      5 phiên / tuần trước + tuần này tới hôm qua; vẽ hộp trong 8 U, tối đa 2 hộp mỗi phía giá,
//      hộp ngày trùng hộp tuần ⇒ một hộp "HVN ngày + tuần". Giá quay lại: canh phản ứng đảo chiều HOẶC
//      phá vỡ — chưa kiểm định. (Đo cũ trên HVN đỉnh nhọn: "đi tiếp / mục tiêu, không fade";
//      phép đo chưa phân xử với cách dùng mới.) HVN kiểu cũ (đỉnh nhọn + nền 90 %), mục tiêu
//      chốt lời sinh từ nó, và các lớp "Đo ·" đã BỎ HẲN.
//    Lớp phụ (tắt mặc định): LVN ngày, VAH/VAL hôm nay, đường VWAP tuần/ngày.
//  Logic thuần ở ProfileEngine.cs (StrongZones / ZonePolicy) — test C# = Python ở tests/.
//  Mọi con số là HẰNG (người dùng không chỉnh); settings chỉ còn bật/tắt lớp, màu, Telegram, lệch giờ.
//
//  Giờ phiên = phút-trong-ngày, giờ local = bar.TimeLeft + TzOffset (giả định
//  TimeLeft là UTC; nếu feed trả local, đặt TzOffset=0). Mặc định VN (+7):
//  Á 05:00–12:30, Âu 12:30–19:00, Mỹ 19:00–04:00. Cần Volume Analysis.
//  Build: concat ProfileEngine.cs + file này. Chi tiết: PLAN.md.
// ============================================================================
namespace SessionZonesNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Linq;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;

    public class SessionZones : Indicator, IVolumeAnalysisIndicator
    {
        // ======================= SETTINGS (PLAN-VUNG-MANH.md §12.1) =======================
        //  Quantower bỏ qua giá trị đã lưu của ô không còn tồn tại ⇒ workspace cũ mở được.
        //  Ô hộp HVN dùng tên thuộc tính MỚI (ShowHvnBox) để giá trị "tắt" của ô ShowHvn cũ không dính sang.
        // ---------- Hiển thị ----------
        [InputParameter("Hiện vùng mạnh (va đập nhiều + hợp lưu)", 10)]
        public bool ShowStrongZones { get; set; } = true;
        [InputParameter("Hiện hộp HVN (cụm khối lượng lớn của ngày/tuần trước)", 11)]
        public bool ShowHvnBox { get; set; } = true;
        [InputParameter("Hiện LVN (chỗ khối lượng mỏng, giá hay xuyên nhanh)", 12)]
        public bool ShowLvn { get; set; } = false;
        [InputParameter("Hiện VAH/VAL hôm nay", 13)]
        public bool ShowTodayVa { get; set; } = false;
        [InputParameter("Vẽ đường VWAP tuần và ngày", 14)]
        public bool DrawVwapLines { get; set; } = false;
        // Công tắc chung của 3 lớp phụ ở trên (LVN, VAH/VAL hôm nay, đường VWAP): tắt ô này thì cả ba
        // không vẽ dù đã bật. Không ảnh hưởng vùng mạnh, hộp HVN và tin Telegram.
        [InputParameter("Hiện các lớp phụ đã bật ở trên (LVN, VAH/VAL, VWAP)", 15)]
        public bool ShowZones { get; set; } = true;
        // ---------- Màu ----------
        [InputParameter("Màu hỗ trợ", 20)]
        public Color SupColor { get; set; } = Color.FromArgb(0x26, 0xA6, 0x9A);
        [InputParameter("Màu kháng cự", 21)]
        public Color ResColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);
        [InputParameter("Màu vùng rất mạnh", 22)]
        public Color StrongGoldColor { get; set; } = Color.FromArgb(0xFF, 0xD6, 0x00);
        [InputParameter("Màu hộp HVN", 23)]
        public Color HvnColor { get; set; } = Color.FromArgb(0xFF, 0x8F, 0x00);
        [InputParameter("Màu VWAP tuần", 24)]
        public Color VwapWeekColor { get; set; } = Color.FromArgb(0x1E, 0x88, 0xE5);
        [InputParameter("Màu VWAP ngày", 25)]
        public Color VwapDayColor { get; set; } = Color.FromArgb(0xFD, 0xD8, 0x35);
        // ---------- Giờ ----------
        [InputParameter("Lệch giờ so với UTC (Việt Nam = 7)", 30, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        // ---------- Telegram (tổng hợp: đầu ngày + buổi chiều + trước phiên Mỹ) ----------
        [InputParameter("Gửi Telegram", 40)]
        public bool TeleEnabled { get; set; } = false;
        [InputParameter("Bot token", 41)]
        public string TeleBotToken { get; set; } = "";
        [InputParameter("Chat ID", 42)]
        public string TeleChatId { get; set; } = "";
        // Add indicator này trên NHIỀU tab cùng symbol thì mỗi tab có thể tự bắn tin ⇒ CHỈ bật ở ĐÚNG 1 tab.
        [InputParameter("Tab này được gửi (chỉ bật ở một chart)", 43)]
        public bool TeleIsSender { get; set; } = false;
        [InputParameter("Gửi thử ngay (bật rồi tắt)", 44)]
        public bool TeleTestNow { get; set; } = false;
        [InputParameter("Kèm lịch tin Forex Factory", 45)]
        public bool TeleShowNews { get; set; } = true;

        // ======================= HẰNG SỐ (bằng đúng mặc định cũ của các ô đã gỡ — §12.2) =======================
        private const int AsiaStart = 300;            // 05:00 giờ VN
        private const int EuropeStart = 750;          // 12:30
        private const int UsStart = 1140;             // 19:00
        private const int RowTicks = 2;               // hàng profile = 2 bước giá
        private const int GapMinutes = 75;            // nghỉ > 75 phút ⇒ phiên mới
        private const bool UseVolume = true;          // volume theo giá (thiếu thì tự rơi về TPO)
        private const int ZoneLookbackSessions = 10;
        private const int MaxLvn = 2;
        private const double ZoneRangeAtr = 3.0;      // bán kính lớp phụ ×ATR20 (chỉ dùng khi ZoneRadiusPrices = 0)
        private const double ZoneRadiusPrices = 12.0; // bán kính lớp phụ (VAH/VAL hôm nay, LVN) — "giá" của vàng ≈ 1 U GC
        private const int MaxZones = 5;
        private const int WeekGapHours = 30;          // nghỉ > 30 giờ ⇒ tuần mới
        private const double MinSpliceJumpPrices = 20.0;   // chỗ nối hợp đồng: nhảy ≥ 20 "giá" (× 10 × tick)
        private const int TeleUsStartMin = 1160;      // 19:20
        private const int TelePreUsMin = 30;
        private const int TeleMorningGrace = 6;
        private const int TeleAfternoonMin = 840;     // 14:00
        private const string TeleShareDir = "";       // thư mục mặc định
        private static readonly Color LvnColor = Color.FromArgb(0x90, 0x90, 0x90);

        private bool _daySpliced;                     // profile 24h của LVN vừa bị cắt vì chỗ nối
        private bool _singleContract;                 // symbol là một hợp đồng ⇒ không có chỗ nối ⇒ bộ chặn tắt (§12.3)
        private bool _vaLoaded;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private ZoneRenderState _render;
        private int _digits = 1;
        private readonly TeleReport _tele = new();  // gửi tổng hợp lên Telegram
        private readonly StrongZoneEngine _sz = new();   // vùng mạnh + hộp HVN: bộ đệm theo nến M30 (PLAN-VUNG-MANH.md §2)

        // ---- Tự nhận diện timeframe chart: nếu KHÔNG phải M30, tự lấy history
        // M30 phụ của cùng symbol qua Symbol.GetHistory() thay vì bắt người dùng
        // add đúng chart M30 (dễ nhầm khi muốn xem vùng trên chart M1 để vào lệnh).
        private HistoricalData _hd30;         // history M30 dùng để tính — của chart chính hoặc phụ
        private bool _ownHd30;                // true nếu _hd30 là history PHỤ (tự lấy, phải tự Dispose)
        private static readonly Period Period30 = new Period(BasePeriod.Minute, 30);

        public SessionZones() : base()
        {
            Name = "Session Zones";
            Description = "Vùng mạnh = cụm đỉnh/đáy M30 va đập nhiều lần + hợp lưu với VWAP/±1σ, VAH/VAL hôm qua & tuần trước, hộp HVN (xanh hỗ trợ, đỏ kháng cự, vàng = ≥3 nhóm hợp lưu có HVN). Hộp HVN = cụm khối lượng lớn và đều của phiên/tuần đã đóng; giá quay lại thì canh phản ứng đảo chiều hoặc phá vỡ. Chưa kiểm định; không phải tín hiệu vào lệnh. Add vào chart bất kỳ — tự lấy dữ liệu M30, vùng không đổi khi đổi khung. Cần Volume Analysis.";
            SeparateWindow = false;
        }

        // Bộ chặn chỗ nối: chỉ bật với mã liên tục (/GC:XCEC…). Một hợp đồng (GCZ26, NQZ26…) ⇒ 0 = tắt.
        private double SpliceJump(double tick) => _singleContract ? 0 : MinSpliceJumpPrices * 10.0 * tick;

        private static bool? IsContinuousSymbol(Symbol s)
        {
            try
            {
                var t = s?.FutureContractType;
                if (!t.HasValue) return null;
                return t.Value == FutureContractType.Continuous;
            }
            catch { return null; }
        }

        public bool IsRequirePriceLevelsCalculation => true;

        protected override void OnInit()
        {
            base.OnInit();
            bool isM30 = HistoricalData?.Aggregation is HistoryAggregationTime t && t.Period.Equals(Period30);
            // Vùng mạnh cắt history về cùng cửa sổ (StrongZoneParams.HistoryDays = 35 ngày trước nến cuối) để
            // chart M30 và chart khung khác ra CÙNG vùng. Chart M30 tải ít hơn ~36 ngày thì không đủ cửa sổ đó
            // ⇒ dùng history M30 phụ 45 ngày như các khung khác.
            if (isM30 && HistoricalData.Count > 0)
            {
                var first = HistoricalData[0, SeekOriginHistory.Begin]?.TimeLeft;
                var lastB = HistoricalData[0, SeekOriginHistory.End]?.TimeLeft;
                if (first.HasValue && lastB.HasValue && (lastB.Value - first.Value).TotalDays < new StrongZoneParams().HistoryDays + 1)
                    isM30 = false;
            }
            if (isM30)
            {
                _hd30 = HistoricalData;
                _ownHd30 = false;
            }
            else
            {
                var srcAgg = HistoricalData?.Aggregation as HistoryAggregationTime;
                var histType = srcAgg?.HistoryType ?? HistoryType.Last;
                // Neo theo nến mới nhất của CHART (Market Replay ở quá khứ) — ZonePolicy.AuxHistoryFrom.
                DateTime? lastBar = HistoricalData != null && HistoricalData.Count > 0
                    ? HistoricalData[0, SeekOriginHistory.End]?.TimeLeft : null;
                _hd30 = Symbol.GetHistory(Period30, histType, ZonePolicy.AuxHistoryFrom(lastBar, DateTime.UtcNow, 45));
                _ownHd30 = true;
                _hd30.NewHistoryItem += OnHd30NewBar;
                var prog = _hd30.CalculateVolumeProfile(new VolumeAnalysisCalculationParameters { CalculatePriceLevels = true });
                if (prog != null) prog.StateChanged += OnVaStateChanged; else { lock (_calc) _vaLoaded = true; }
            }
        }

        private void OnVaStateChanged(object sender, VolumeAnalysisTaskEventArgs e)
        {
            if (e?.CalculationState != VolumeAnalysisCalculationState.Finished) return;
            lock (_calc) _vaLoaded = true;
            Process();
        }

        private void OnHd30NewBar(object sender, HistoryEventArgs e) => Process();

        public void VolumeAnalysisData_Loaded() { if (!_ownHd30) { lock (_calc) { _vaLoaded = true; } Process(); } }
        protected override void OnClear()
        {
            if (_ownHd30 && _hd30 != null) { _hd30.NewHistoryItem -= OnHd30NewBar; _hd30.Dispose(); }
            lock (_calc) { _vaLoaded = false; _sz.Reset(); lock (_sync) _render = null; }
        }
        protected override void OnUpdate(UpdateArgs args)
        {
            ConfigTele();
            _tele.PollTest(Symbol?.Name);        // nút gửi thử: xử lý ngay, không đợi VA
            if (!_vaLoaded) return;
            if (!_ownHd30)
            {
                var p = HistoricalData.VolumeAnalysisCalculationProgress;
                if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            }
            Process();
        }

        private string Fmt(double p) => double.IsNaN(p) ? "—" : Math.Round(p, _digits).ToString("0.0##");

        private string LabelOf(DateTime timeLeft)
        {
            int m = (int)((timeLeft.AddHours(TzOffset).TimeOfDay).TotalMinutes);
            if (m >= AsiaStart && m < EuropeStart) return "A";
            if (m >= EuropeStart && m < UsStart) return "AU";
            return "MY";
        }

        private void Process()
        {
            lock (_calc)
            {
                double tick = Symbol?.TickSize ?? 0;
                if (tick <= 0) return;
                _digits = Math.Max(0, (int)Math.Round(-Math.Log10(tick)));
                _singleContract = ZonePolicy.IsSingleContract(Symbol?.Name, IsContinuousSymbol(Symbol));
                var hd = _hd30;
                if (hd == null) return;
                int n = hd.Count;
                if (n == 0)
                {
                    // Không im lặng: báo thẳng trên chart thay vì để trống (sự cố replay 2026-10-17).
                    lock (_sync) _render = new ZoneRenderState { Zones = new List<Zone>(), NowPrice = 0, Tick = tick,
                        Note = "⚠ Chưa có nến M30 nào cho symbol này (Market Replay chưa có dữ liệu trong khoảng 45 ngày trước nến cuối?)." };
                    return;
                }
                double rowStep = tick * Math.Max(1, RowTicks);

                // gộp block phiên: đổi label HOẶC gap > GapMinutes → block mới
                var blocks = new List<(string lab, int from, int to)>();
                string curLab = null; int start = 0; DateTime prev = DateTime.MinValue; bool have = false;
                for (int i = 0; i < n; i++)
                {
                    if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                    string lab = LabelOf(b.TimeLeft);
                    bool split = !have || lab != curLab || (b.TimeLeft - prev).TotalMinutes > GapMinutes;
                    if (split) { if (have) blocks.Add((curLab, start, i - 1)); curLab = lab; start = i; }
                    prev = b.TimeLeft; have = true;
                }
                if (have) blocks.Add((curLab, start, n - 1));
                if (blocks.Count == 0) return;

                SessionProfile P(int idx) => ProfileEngine.BuildProfile(hd, blocks[idx].from, blocks[idx].to, tick, rowStep, UseVolume, 0, blocks[idx].lab);

                var last = P(blocks.Count - 1);
                // tìm phiên Á/Âu/Mỹ gần nhất
                SessionProfile asia = null, europe = null, us = null;
                for (int i = blocks.Count - 1; i >= 0 && (asia == null || europe == null || us == null); i--)
                {
                    var lab = blocks[i].lab;
                    if (lab == "A" && asia == null) asia = P(i);
                    else if (lab == "AU" && europe == null) europe = P(i);
                    else if (lab == "MY" && us == null) us = P(i);
                }

                double nowPrice = last.Close;

                // VWAP neo NGÀY/TUẦN (cộng dồn từ đầu kỳ tới nến hiện tại) — CORVEN dùng
                // "Vwap ngày scalp" (CAU_HOI_CAN_THONG_NHAT.md, ghi chú §W5/§C1), tuần dùng
                // cho KB-A hold dài. Tự tính lại (không đọc indicator VWAP có sẵn của
                // Quantower — API không cho 1 indicator đọc giá trị của indicator khác trên
                // chart) bằng đúng công thức đã kiểm chứng offline (zones_corven.py §2).
                var daySpansV = ProfileEngine.GroupByGap(hd, GapMinutes);
                var weekSpansV = ProfileEngine.WeekSpans(hd, WeekGapHours);
                int dayFrV = daySpansV.Count > 0 ? daySpansV[daySpansV.Count - 1].from : 0;
                int weekFrV = weekSpansV.Count > 0 ? weekSpansV[weekSpansV.Count - 1].fr : 0;
                double vwapDay = ProfileEngine.VwapAt(hd, dayFrV, n - 1);
                double vwapWeek = ProfileEngine.VwapAt(hd, weekFrV, n - 1);

                // gợi ý bias Mỹ
                var (decision, lean, conf, reasons) = UsBias(hd, asia, europe, us, last, tick, rowStep);

                var zones = FindZones(hd, blocks, tick, rowStep, nowPrice, vwapDay, vwapWeek);
                // B10: báo khi vừa cắt profile vì mã liên tục đổi hợp đồng (chỉ xảy ra khi bộ chặn đang bật).
                string note = _daySpliced
                    ? "⚠ Mã liên tục vừa đổi hợp đồng — LVN 24h đã cắt bỏ phần trước chỗ nối."
                    : null;
                // v3 (2026-10-17): phân nhóm theo VAI TRÒ đo được (ZonePolicy.Role).
                string RoleOf(Zone z) => ZonePolicy.Role(z.Type);
                var canhLenh = zones.Where(z => RoleOf(z) == "canh").ToList();
                var canhRange = zones.Where(z => RoleOf(z) == "canh_range").ToList();

                // ---- VÙNG MẠNH + HỘP HVN (chưa kiểm định): cấu trúc chỉ tính lại khi có nến M30 mới, mỗi tick chỉ
                //  lọc hiển thị theo giá. Hộp HVN = đúng các hộp hvn_d / hvn_w mà StrongZones.Compute đã tính.
                //  Không đi qua MergeZones / LimitAndBalance / bán kính cũ.
                List<SzZone> strong = null;
                List<SzHvnShown> hvnBoxes = null;
                if (ShowStrongZones || ShowHvnBox)
                {
                    var szp = SzParams(tick);
                    var szr = StrongStructure(hd, tick, rowStep, szp);
                    if (ShowStrongZones)
                    {
                        strong = StrongZones.Display(szr, nowPrice, szp);
                        foreach (var s in strong)
                            zones.Add(new Zone { Type = "strong", Lo = s.Lo, Hi = s.Hi, Center = (s.Lo + s.Hi) / 2, Side = s.Side,
                                Strength = ZonePolicy.StrongStrength(s.Gold), Label = s.Label, IsMarker = false });
                    }
                    if (ShowHvnBox) hvnBoxes = StrongZones.HvnBoxes(szr, nowPrice, szp);
                    if (szr.Approx)
                        note = (note == null ? "" : note + "\n") + "⚠ Thiếu khối lượng theo giá — mức hợp lưu tính gần đúng, không có hộp HVN";
                }

                lock (_sync) _render = new ZoneRenderState { Zones = zones, Strong = strong, HvnBoxes = hvnBoxes, Note = note, NowPrice = nowPrice, Tick = tick };

                // ---- tổng hợp GỌN cho Telegram ----
                var tele = new List<string>();
                tele.Add($"🇺🇸 Phiên Mỹ: {decision} — {(lean > 0 ? "MUA" : lean < 0 ? "BÁN" : "TRUNG TÍNH")} ({conf}/100)");
                if (reasons.Count > 0) tele.Add($"Lý do: {reasons[0]}");
                tele.Add($"Giá hiện tại: {Fmt(nowPrice)} · VWAP ngày {Fmt(vwapDay)} ({(nowPrice >= vwapDay ? "trên" : "dưới")}) · VWAP tuần {Fmt(vwapWeek)} ({(nowPrice >= vwapWeek ? "trên" : "dưới")})");
                if (canhLenh.Count > 0)
                {
                    tele.Add("Vùng canh (VWAP):");
                    foreach (var z in canhLenh.Take(4))
                    {
                        string sd = z.Side > 0 ? "S" : z.Side < 0 ? "R" : "·";
                        string pr = Math.Abs(z.Hi - z.Lo) < tick ? Fmt(z.Center) : $"{Fmt(z.Lo)}–{Fmt(z.Hi)}";
                        tele.Add($"• {sd} {pr} · {z.Label} [{z.Strength:0}]");
                    }
                }
                if (canhRange.Count > 0)
                    tele.Add($"Cạnh range Âu: {string.Join(" · ", canhRange.Select(z => $"{z.Label} {Fmt(z.Center)}"))}");
                var hvnLine = StrongZones.HvnSummaryLine(hvnBoxes, Fmt);
                if (hvnLine != null) tele.Add(hvnLine);
                var szLine = StrongZones.SummaryLine(strong, Fmt);
                if (szLine != null) tele.Add(szLine);
                ConfigTele();
                _tele.Run(hd, Symbol?.Name, "zone", tele);
            }
        }

        // Mọi thông số vùng mạnh / hộp HVN = mặc định của StrongZoneParams (đã đo, tính theo U nên dùng chung GC và NQ:
        // 3 lần va đập, bật lại 1 U, 5 phiên, cụm 0,30 U, dung sai 0,10 U, ≥1 nhóm, HVN rời xa 2 U, gộp VAH/VAL với ±1σ,
        // bán kính 4 U, 3 vùng mỗi phía). Chỉ bộ chặn chỗ nối phụ thuộc symbol.
        private StrongZoneParams SzParams(double tick) => new StrongZoneParams
        {
            GapMinutes = GapMinutes, WeekGapHours = WeekGapHours, SpliceJump = SpliceJump(tick),
        };

        // Cấu trúc vùng mạnh từ history M30 — chỉ dựng lại mảng + tính lại khi khoá đổi (số nến, nến đầu,
        // nến j = n−2 vừa đóng, nến cuối đang chạy, thông số). Nến cuối luôn coi là nến đang chạy.
        private SzResult StrongStructure(HistoricalData hd, double tick, double rowStep, StrongZoneParams p)
        {
            int n = hd.Count;
            if (n < 3) return new SzResult();
            var first = hd[0, SeekOriginHistory.Begin] as HistoryItemBar;
            var barJ = hd[n - 2, SeekOriginHistory.Begin] as HistoryItemBar;
            var lastB = hd[n - 1, SeekOriginHistory.Begin] as HistoryItemBar;
            if (first == null || barJ == null || lastB == null) return new SzResult();
            string key = StrongZoneEngine.KeyOf(n, first.TimeLeft, barJ.TimeLeft, lastB.TimeLeft, p) + "|" + tick + "|" + rowStep;
            return _sz.Structure(key, () =>
            {
                var bars = new List<HistoryItemBar>(n);
                for (int i = 0; i < n; i++) if (hd[i, SeekOriginHistory.Begin] is HistoryItemBar b) bars.Add(b);
                int st = StrongZones.CanonicalStart(bars.Select(b => b.TimeLeft).ToList(), p.HistoryDays);
                var win = bars.GetRange(st, bars.Count - st);
                return new SzSeries(win.Select(b => b.TimeLeft).ToList(), win.Select(b => b.Open).ToList(),
                    win.Select(b => b.High).ToList(), win.Select(b => b.Low).ToList(), win.Select(b => b.Close).ToList(),
                    win.Select(b => b.VolumeAnalysisData?.Total?.Volume ?? b.Volume).ToList(),
                    i => win[i].VolumeAnalysisData?.PriceLevels?.Select(kv => new KeyValuePair<double, double>(kv.Key, kv.Value.Volume)).ToList(),
                    tick, rowStep, p);
            }, p);
        }

        private void ConfigTele()
        {
            _tele.Enabled = TeleEnabled;
            _tele.TestNow = TeleTestNow;
            _tele.IsSender = TeleIsSender;
            _tele.ShowNews = TeleShowNews;
            _tele.BotToken = TeleBotToken?.Trim() ?? "";
            _tele.ChatId = TeleChatId?.Trim() ?? "";
            _tele.ShareDir = TeleShareDir ?? "";
            _tele.TzOffset = TzOffset;          // dùng lệch giờ sẵn có của M30
            _tele.UsStartMin = TeleUsStartMin;
            _tele.PreUsMin = TelePreUsMin;
            _tele.MorningGraceBars = TeleMorningGrace;
            _tele.AfternoonMin = TeleAfternoonMin;
            _tele.IbBars = 2;                   // M30 không có input IB → coi IB = 2 nến (1h)
            _tele.GapMinutes = GapMinutes;
        }

        // quan hệ B vs A: 1=EXTEND_UP, -1=EXTEND_DN, 0=INSIDE/overlap
        private int Relationship(SessionProfile b, SessionProfile a)
        {
            if (b == null || a == null || !b.Valid || !a.Valid) return 0;
            if (b.Vah <= a.Vah && b.Val >= a.Val) return 0;               // inside
            if (b.Vah > a.Vah && b.Val >= a.Val) return 1;                // extend up
            if (b.Val < a.Val && b.Vah <= a.Vah) return -1;               // extend down
            return b.Poc > a.Poc ? 1 : -1;
        }

        private (string decision, int lean, int conf, List<string> reasons) UsBias(
            HistoricalData hd, SessionProfile asia, SessionProfile europe, SessionProfile us,
            SessionProfile last, double tick, double rowStep)
        {
            var reasons = new List<string>();
            if (europe == null || !europe.Valid)
                return ("chờ dữ liệu phiên Âu", 0, 20, reasons);

            // AE VA gộp Á+Âu (nếu liền mạch)
            double aeVah = europe.Vah, aeVal = europe.Val, aePoc = europe.Poc;
            if (asia != null && asia.Valid && asia.FromIdx <= europe.ToIdx)
            {
                var ae = ProfileEngine.BuildProfile(hd, Math.Min(asia.FromIdx, europe.FromIdx), europe.ToIdx, tick, rowStep, UseVolume, 0, "AE");
                if (ae.Valid) { aeVah = ae.Vah; aeVal = ae.Val; aePoc = ae.Poc; }
            }
            double usOpen = us != null && us.Valid ? us.Open : last.Close;
            double usDelta = us != null ? us.Delta : 0;
            int rel = Relationship(europe, asia);

            // Rule 1 — tiếp diễn trend Âu
            if (europe.Balance == "TREND" && europe.Direction != 0 &&
                ((europe.Direction > 0 && rel >= 0) || (europe.Direction < 0 && rel <= 0)) &&
                !(usOpen < aeVal && europe.Direction > 0) && !(usOpen > aeVah && europe.Direction < 0))
            {
                int lean = europe.Direction;
                bool conf = Math.Sign(usDelta) == lean || usDelta == 0;
                reasons.Add($"Âu có xu hướng {(lean > 0 ? "tăng" : "giảm")}, mở rộng cùng chiều");
                if (conf) reasons.Add("Delta phiên Mỹ xác nhận");
                reasons.Add($"AE value {Fmt(aeVal)}-{Fmt(aeVah)}");
                return ("TIẾP DIỄN TREND ÂU", lean, conf ? 60 : 45, reasons);
            }
            // Rule 2 — phá cân bằng Á-Âu
            if (rel == 0)
            {
                if (usOpen > aeVah) { reasons.Add("Á-Âu cân bằng, Mỹ mở phá LÊN trên AE VAH"); if (usDelta > 0) reasons.Add("Delta đẩy lên"); return ("PHÁ CÂN BẰNG LÊN", 1, usDelta > 0 ? 60 : 45, reasons); }
                if (usOpen < aeVal) { reasons.Add("Á-Âu cân bằng, Mỹ mở phá XUỐNG dưới AE VAL"); if (usDelta < 0) reasons.Add("Delta đẩy xuống"); return ("PHÁ CÂN BẰNG XUỐNG", -1, usDelta < 0 ? 60 : 45, reasons); }
                reasons.Add("Á-Âu cân bằng, Mỹ mở trong value — chờ break");
                return ("CHỜ MỸ ĐỊNH HƯỚNG", 0, 35, reasons);
            }
            // Rule 3 — đảo về giá trị (Âu reject/quá đà, Mỹ quay vào lại AE VA)
            bool insideAE = usOpen <= aeVah && usOpen >= aeVal;
            if (insideAE && europe.Balance != "TREND")
            {
                int lean = usOpen < aePoc ? 1 : -1;   // về phía POC
                reasons.Add("Mỹ mở lại trong vùng giá trị Á-Âu → nghiêng đảo về POC");
                reasons.Add($"AE POC {Fmt(aePoc)}");
                return ("ĐẢO VỀ VÙNG GIÁ TRỊ", lean, 50, reasons);
            }
            // mặc định: theo hướng mở rộng Âu
            reasons.Add($"Theo hướng mở rộng phiên Âu ({(rel > 0 ? "lên" : "xuống")})");
            return ("THEO ĐÀ ÂU", rel, 40, reasons);
        }

        // Lớp PHỤ (không phải vùng mạnh / hộp HVN): LVN ngày, VAH/VAL hôm nay, VWAP tuần/ngày.
        // HVN kiểu cũ (đỉnh nhọn + nền 90 %), mục tiêu chốt lời sinh từ nó, đỉnh/đáy phiên, naked POC, cụm POC,
        // băng giá trị, LVN tuần đã BỎ (PLAN-VUNG-MANH.md §11–12).
        private List<Zone> FindZones(HistoricalData hd, List<(string lab, int from, int to)> blocks,
                                     double tick, double rowStep, double nowPrice,
                                     double vwapDay = double.NaN, double vwapWeek = double.NaN)
        {
            var zones = new List<Zone>();
            var lvnZones = new List<Zone>();
            int last = hd.Count - 1;
            double atr = ProfileEngine.Atr(hd, last);
            int startBlk = Math.Max(0, blocks.Count - 1 - ZoneLookbackSessions);
            int SideOf(double p) => p > nowPrice ? -1 : p < nowPrice ? 1 : 0;
            double spliceJump = SpliceJump(tick);

            // ---- LVN NGÀY: profile 24h cuối của các khối phiên đã đóng. Không phải vùng canh lệnh — nơi giá
            //  xuyên nhanh, dùng để đặt SL / biết chỗ không nên kỳ vọng phản ứng. Xét riêng khỏi trần MaxZones.
            _daySpliced = false;
            if (ShowLvn && blocks.Count >= 2)
            {
                SessionProfile lastDone = null;
                for (int i = blocks.Count - 2; i >= startBlk && lastDone == null; i--)
                {
                    var sp = ProfileEngine.BuildProfile(hd, blocks[i].from, blocks[i].to, tick, rowStep, UseVolume, 0, blocks[i].lab);
                    if (sp.Valid) lastDone = sp;
                }
                if (lastDone != null)
                {
                    var dayStart = lastDone.End.AddHours(-24);
                    int dFrom = -1;
                    for (int i = startBlk; i < blocks.Count - 1; i++)
                        if (hd[blocks[i].from, SeekOriginHistory.Begin] is HistoryItemBar bb
                            && bb.TimeLeft >= dayStart) { dFrom = blocks[i].from; break; }
                    if (dFrom >= 0)
                    {
                        int dTo = blocks[blocks.Count - 2].to;
                        int spD = ProfileEngine.LastSpliceIndex(hd, dFrom, dTo, spliceJump);
                        if (spD > dFrom) { dFrom = spD; _daySpliced = true; }
                        var dyRows = ProfileEngine.RowsOver(hd, dFrom, dTo, rowStep, UseVolume);
                        foreach (var (p, ratio) in ProfileEngine.FindLvn(dyRows, tick).Take(MaxLvn))
                        {
                            var (lo, hi) = ProfileEngine.TroughBand(dyRows, tick, p);
                            lvnZones.Add(new Zone { Center = p, Lo = lo, Hi = hi, Type = "lvn", IsMarker = false,
                                Side = SideOf(p), Strength = 30, Label = $"LVN ngày ×{ratio:0.0} (xuyên nhanh)" });
                        }
                    }
                }
            }

            //  v4 (2026-10-23, người học chốt): VAH/VAL = của NGÀY HÔM NAY đang hình thành —
            //  profile từ đầu phiên Á gần nhất tới nến mới nhất (gồm khối đang chạy), KHÔNG
            //  lấy riêng phiên Á/Âu/Mỹ. Chưa đủ TodayVaMinBars nến M30 thì không vẽ. Cắt ở chỗ nối hợp đồng.
            int todayBlk = ZonePolicy.TodayStartBlock(blocks.Select(x => x.lab).ToList());
            if (ShowTodayVa && todayBlk >= 0)
            {
                int tFrom = blocks[todayBlk].from, tTo = blocks[blocks.Count - 1].to;
                int spT = ProfileEngine.LastSpliceIndex(hd, tFrom, tTo, spliceJump);
                if (spT > tFrom) tFrom = spT;
                if (tTo - tFrom + 1 >= ZonePolicy.TodayVaMinBars)
                {
                    var sp = ProfileEngine.BuildProfile(hd, tFrom, tTo, tick, rowStep, UseVolume, 0, "A");
                    if (sp.Valid)
                    {
                        double vs = ZonePolicy.BaseStrength("va_edge");
                        zones.Add(new Zone { Center = sp.Vah, Lo = sp.Vah, Hi = sp.Vah, Type = "va_edge", Side = SideOf(sp.Vah), Strength = vs, Label = "VAH hôm nay" });
                        zones.Add(new Zone { Center = sp.Val, Lo = sp.Val, Hi = sp.Val, Type = "va_edge", Side = SideOf(sp.Val), Strength = vs, Label = "VAL hôm nay" });
                    }
                }
            }
            //  v3: VWAP tuần/ngày = VÙNG CANH duy nhất có bằng chứng. Không gộp với vùng
            //  khác (giữ nguyên giá trị đường VWAP), không chịu trần MaxZones.
            var vwapZones = new List<Zone>();
            if (!double.IsNaN(vwapWeek) && vwapWeek > 0)
                vwapZones.Add(new Zone { Center = vwapWeek, Lo = vwapWeek, Hi = vwapWeek, Type = "vwap_week", Side = SideOf(vwapWeek),
                    Strength = ZonePolicy.BaseStrength("vwap_week"), Label = "VWAP tuần · hạng 1" });
            if (!double.IsNaN(vwapDay) && vwapDay > 0)
                vwapZones.Add(new Zone { Center = vwapDay, Lo = vwapDay, Hi = vwapDay, Type = "vwap_day", Side = SideOf(vwapDay),
                    Strength = ZonePolicy.BaseStrength("vwap_day"), Label = "VWAP ngày · hạng 2" });

            // ---- D2: gộp hợp lưu — dung sai co giãn theo ATR (chỉ còn VAH/VAL hôm nay đi qua đây)
            double mergeTol = Math.Clamp(atr * 0.15, 0.7, 3.0);
            zones = MergeZones(zones, mergeTol);

            // ---- D1/B1: lọc theo TẦM VỚI — bán kính CỐ ĐỊNH theo "giá" (ZoneRadiusPrices = 12 giá vàng ≈ 1 U GC;
            //  trên NQ hẹp — đổi sang U là thay đổi hành vi, làm riêng, §12.2).
            double radius = ZoneRadiusPrices > 0
                ? ZoneRadiusPrices * 10.0 * tick
                : ZoneRangeAtr * Math.Max(atr, tick);
            zones = zones.Where(z => Math.Abs(z.Center - nowPrice) <= radius).ToList();

            // ---- D5: trần số vùng + cân đối 2 phía
            zones = LimitAndBalance(zones, MaxZones);

            zones.AddRange(lvnZones.Where(z => Math.Abs(z.Center - nowPrice) <= radius));
            zones.AddRange(vwapZones);    // v3: VWAP luôn có mặt, không lọc bán kính
            return zones.OrderByDescending(z => z.Strength).ToList();
        }

        // Xếp theo điểm, đảm bảo tối thiểu 2 vùng mỗi phía (nếu có đủ), rồi cắt còn cap.
        private static List<Zone> LimitAndBalance(List<Zone> zones, int cap)
        {
            if (zones.Count <= cap) return zones;
            var above = zones.Where(z => z.Side < 0).OrderByDescending(z => z.Strength).ToList();
            var below = zones.Where(z => z.Side > 0).OrderByDescending(z => z.Strength).ToList();
            var res = new List<Zone>();
            res.AddRange(above.Take(Math.Min(2, above.Count)));
            res.AddRange(below.Take(Math.Min(2, below.Count)));
            var rest = zones.Except(res).OrderByDescending(z => z.Strength);
            foreach (var z in rest)
            {
                if (res.Count >= cap) break;
                res.Add(z);
            }
            return res;
        }

        private List<Zone> MergeZones(List<Zone> zones, double tolDollars)
        {
            var sorted = zones.OrderBy(z => z.Center).ToList();
            var res = new List<Zone>();
            foreach (var z in sorted)
            {
                var near = res.FirstOrDefault(r => Math.Abs(r.Center - z.Center) <= tolDollars && ZonePolicy.CanMerge(r.Type, z.Type));
                if (near != null)
                {
                    near.Lo = Math.Min(near.Lo, z.Lo); near.Hi = Math.Max(near.Hi, z.Hi);
                    near.Center = (near.Lo + near.Hi) / 2;
                    near.Strength = Math.Min(100, Math.Max(near.Strength, z.Strength) + 0.5 * Math.Min(near.Strength, z.Strength) + 8);
                    near.Frames += z.Frames;
                    near.IsMarker = near.IsMarker || z.IsMarker;   // hợp lưu với 1 mốc thật -> vẫn là mốc
                    if (!near.Label.Contains(z.Label.Split(' ')[0])) near.Label += " + " + z.Label;
                }
                else res.Add(z);
            }
            foreach (var z in res)
                if (z.Frames > 1) z.Label += $" (×{z.Frames} khung)";
            return res;
        }

        // ================================================================
        //  RENDER
        // ================================================================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || !_vaLoaded) return;
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;

            ZoneRenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;
            var gr = args.Graphics;
            var conv = win.CoordinatesConverter;
            var clip = win.ClientRectangle;

            bool oldLayers = ShowZones && rs.Zones != null;
            if (oldLayers)
            {
                // LVN (lớp nền phụ): dải xám mờ + hai viền chấm, nhãn nhạt — bối cảnh, không phải mốc vào lệnh.
                foreach (var z in rs.Zones.Where(z => z.Type == "lvn").OrderBy(z => z.Strength))
                {
                    Color col = LvnColor;
                    float yLo = (float)conv.GetChartY(z.Lo), yHi = (float)conv.GetChartY(z.Hi);
                    float yTop = Math.Min(yLo, yHi), yBot = Math.Max(yLo, yHi);
                    float ym = (yTop + yBot) / 2;
                    if (yBot < clip.Top || yTop > clip.Bottom) continue;
                    if (yBot - yTop >= 3)
                    {
                        using var fill = new SolidBrush(Color.FromArgb(40, col));
                        gr.FillRectangle(fill, clip.Left, yTop, clip.Width, yBot - yTop);
                        using var edge = new Pen(Color.FromArgb(150, col), 1f) { DashStyle = DashStyle.Dot };
                        gr.DrawLine(edge, clip.Left, yTop, clip.Right, yTop);
                        gr.DrawLine(edge, clip.Left, yBot, clip.Right, yBot);
                    }
                    else
                    {
                        using var pen = new Pen(Color.FromArgb(140, col), 1f) { DashStyle = DashStyle.Dash };
                        gr.DrawLine(pen, clip.Left, ym, clip.Right, ym);
                    }
                    using var f = new Font("Arial", 7, FontStyle.Italic);
                    using var br = new SolidBrush(Color.FromArgb(170, col));
                    gr.DrawString(z.Label, f, br, clip.Right - 190, yTop - 10);
                }
            }
            // HỘP HVN + VÙNG MẠNH: dải kéo hết bề ngang; hộp HVN vẽ dưới, vùng mạnh đè lên; nhãn của cả hai
            // sát mép phải, xếp CHUNG bằng StrongZonePainter.LayoutLabels để không đè nhau (có test).
            var strong = ShowStrongZones ? rs.Strong : null;
            var boxes = ShowHvnBox ? rs.HvnBoxes : null;
            if ((strong?.Count ?? 0) + (boxes?.Count ?? 0) > 0)
            {
                using var fs = new Font("Arial", 8, FontStyle.Bold);
                StrongZonePainter.Paint(gr, clip, pr => (float)conv.GetChartY(pr), strong, SupColor, ResColor, StrongGoldColor, rs.Tick, fs,
                                        boxes, HvnColor);
            }
            if (oldLayers)
            {
                // Lớp MỐC phụ: VAH/VAL hôm nay (đường mảnh), VWAP tuần/ngày (chỉ khi bật "Vẽ đường VWAP").
                foreach (var z in rs.Zones.Where(z => z.IsMarker && z.Type != "strong").OrderBy(z => z.Strength))   // yếu vẽ trước
                {
                    bool isVwap = z.Type == "vwap_week" || z.Type == "vwap_day";
                    if (isVwap && !DrawVwapLines) continue;   // dùng đường VWAP của nền tảng
                    Color col = z.Type == "vwap_week" ? VwapWeekColor
                              : z.Type == "vwap_day" ? VwapDayColor
                              : z.Side > 0 ? SupColor : z.Side < 0 ? ResColor : Color.Gray;
                    float ym = (float)conv.GetChartY(z.Center);
                    if (ym < clip.Top || ym > clip.Bottom) continue;
                    using var pen = new Pen(col, 1.2f);
                    gr.DrawLine(pen, clip.Left, ym, clip.Right, ym);
                    using var f = new Font("Arial", 8, FontStyle.Bold);
                    using var br = new SolidBrush(col);
                    gr.DrawString(z.Label, f, br, clip.Right - 190, ym - 12);
                }
            }
            if (!string.IsNullOrEmpty(rs.Note))
            {
                using var fNote = new Font("Consolas", 7, FontStyle.Regular);
                var sz = gr.MeasureString(rs.Note, fNote);
                using var brNote = new SolidBrush(Color.FromArgb(255, 170, 120));
                gr.DrawString(rs.Note, fNote, brNote, clip.Right - sz.Width - 8, clip.Bottom - sz.Height - 4);   // góc dưới-phải
            }
        }
    }

    internal sealed class Zone
    {
        public double Lo, Hi, Center;
        public string Type = "";
        public int Side;
        public double Strength;
        public string Label = "";
        public int Frames = 1;   // số khung thời gian đồng ý (hợp lưu đa khung) — xem D2
        // true = lớp MỐC (đường mảnh: VWAP, VAH/VAL hôm nay); false = lớp NỀN (dải mờ: LVN, vùng mạnh vẽ riêng).
        public bool IsMarker = true;
    }

    internal sealed class ZoneRenderState
    {
        public List<Zone> Zones;
        public List<SzZone> Strong;          // vùng mạnh đã lọc hiển thị (StrongZones.Display) — vẽ bằng StrongZonePainter
        public List<SzHvnShown> HvnBoxes;    // hộp HVN đã lọc hiển thị (StrongZones.HvnBoxes) — vẽ cùng vùng mạnh
        public string Note;  // cảnh báo 1 dòng nhỏ góc dưới-phải (thay cho bảng cũ)
        public double NowPrice;
        public double Tick;
    }
}
