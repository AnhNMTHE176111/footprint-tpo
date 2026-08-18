// ============================================================================
//  SessionZones  —  Phiên Á/Âu/Mỹ + Vùng cần quan tâm cho QUANTOWER
// ============================================================================
//  Add vào chart bất kỳ (M1, M5, M30...) — TỰ LẤY dữ liệu M30 của cùng symbol
//  qua Symbol.GetHistory() nếu chart hiện tại không phải M30 (xem ResolveHd()).
//  Gộp nến 30' thành khối phiên Á/Âu/Mỹ (theo giờ-trong-ngày + gap tách cuối
//  tuần/bảo trì). Sinh tường thuật "phiên nào làm gì" + gợi ý "Mỹ ưu tiên gì"
//  (tiếp diễn/phá/đảo/fade), và vẽ VÙNG: naked POC (nam châm), cụm POC, biên VA
//  phiên, đỉnh/đáy phiên + gợi ý target cho lệnh đang chạy.
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
        // ---------- giờ phiên (phút trong ngày, giờ local) ----------
        [InputParameter("Lệch giờ (bar.TimeLeft UTC → local)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Á bắt đầu (phút/ngày)", 11, 0, 1439, 5, 0)]
        public int AsiaStart { get; set; } = 300;    // 05:00
        [InputParameter("Âu bắt đầu (phút/ngày)", 12, 0, 1439, 5, 0)]
        public int EuropeStart { get; set; } = 750;  // 12:30
        [InputParameter("Mỹ bắt đầu (phút/ngày)", 13, 0, 1439, 5, 0)]
        public int UsStart { get; set; } = 1140;     // 19:00

        // ---------- profile ----------
        [InputParameter("Số tick / hàng profile", 20, 1, 50, 1, 0)]
        public int RowTicks { get; set; } = 2;
        [InputParameter("Gap tách phiên (phút)", 21, 30, 240, 1, 0)]
        public int GapMinutes { get; set; } = 75;
        [InputParameter("Dùng volume theo giá (tắt = TPO)", 22)]
        public bool UseVolume { get; set; } = true;
        [InputParameter("Số phiên gần nhất xét vùng", 23, 2, 40, 1, 0)]
        public int ZoneLookbackSessions { get; set; } = 10;
        [InputParameter("Hiện HVN tuần/ngày (nút khối lượng)", 24)]
        public bool ShowHvn { get; set; } = true;
        [InputParameter("Số HVN tối đa mỗi khung", 25, 1, 8, 1, 0)]
        public int MaxHvn { get; set; } = 3;
        [InputParameter("Hiện LVN (nơi giá xuyên nhanh)", 26)]
        public bool ShowLvn { get; set; } = true;
        [InputParameter("Số LVN tối đa", 27, 1, 4, 1, 0)]
        public int MaxLvn { get; set; } = 2;
        // ---- D1: lọc vùng theo TẦM VỚI, không phải theo độ mạnh lý thuyết ----
        //  Vùng mạnh nhất về cấu trúc (vd HVN tuần) có thể cách giá 70-80 giá —
        //  ngoài tầm giao dịch trong ngày. Bán kính co giãn theo ATR20(M30) vì
        //  biến động vàng khác nhau rất nhiều theo giai đoạn (tháng 6 crash vs
        //  tháng 7 êm) — hằng số tick cứng sẽ sai ở giai đoạn còn lại.
        [InputParameter("Bán kính lọc vùng (×ATR20)", 28, 1, 10, 0.5, 1)]
        public double ZoneRangeAtr { get; set; } = 3.0;
        // ---- B1 (PLAN-MOC-PHAN-UNG.md): bán kính ×ATR20(M30) ra ~50 giá — với
        //  người dừng lỗ 3 giá thì mức cách xa vậy là chuyện tuần sau, không phải
        //  hôm nay. Ưu tiên bán kính CỐ ĐỊNH theo "giá" (đơn vị người dùng nghĩ
        //  bằng, không phải tick); 0 = quay lại cách cũ ×ATR.
        [InputParameter("Bán kính lọc vùng (giá, 0=dùng ×ATR)", 38, 0, 60, 1, 0)]
        public double ZoneRadiusPrices { get; set; } = 12.0;
        // ---- D5: trần số vùng hiển thị — tài liệu khuyến nghị 3-5 vùng/chart ----
        [InputParameter("Số vùng tối đa hiển thị", 29, 3, 12, 1, 0)]
        public int MaxZones { get; set; } = 5;
        // HVN tuần: dùng lại nguyên tuần CME đã ĐÓNG (Sun mở -> T6 đóng), không phải
        // cửa sổ trượt ZoneLookbackSessions — CORVEN chốt "neo đầu tuần, 1 lần/tuần"
        // (CAU_HOI_CAN_THONG_NHAT.md §A1). Ranh giới tuần = khoảng trống > ngưỡng này
        // giữa 2 nến M30 liên tiếp (cuối tuần CME nghỉ ~46h).
        [InputParameter("Gap tách TUẦN cho HVN tuần (giờ)", 34, 20, 60, 1, 0)]
        public int WeekGapHours { get; set; } = 30;
        // ---- B3/B4 (PLAN-MOC-PHAN-UNG.md) — đo 2026-08-18: 84% phiên có đỉnh
        //  volume tách hẳn (nền 90% rộng <=4 giá), nhưng HVN tuần trên chart lại
        //  hiện ra như "cái bướu 50 giá" — vì Optimus Flow gom hàng 10 giá, KHÔNG
        //  phải vì HVN thật sự rộng. Sửa: HVN tuần lấy Lo/Hi THẬT (lớp nền, để
        //  đọc chế độ sideway/trend), HVN ngày vẫn là MỐC 1 giá (để canh lệnh),
        //  và mốc nào bẹt hơn MaxLevelThicknessPrices thì tự hạ xuống lớp nền.
        [InputParameter("Hiện dải nền HVN tuần (Lo/Hi thật)", 35)]
        public bool ShowContextBands { get; set; } = true;
        // ⚠️ Đo A3 (MEASURE-LEVELS-RESULTS.md, 2026-08-18): mẫu 128 phiên KHÔNG đủ
        //  để kết luận "mốc nhọn phản ứng tốt hơn mốc bẹt" (84% phiên đã nhọn sẵn
        //  nên rổ "vừa/bẹt" gần trống). MẶC ĐỊNH TẮT — chỉ hiện con số độ nhọn
        //  trên nhãn, KHÔNG tự hạ cấp mốc, cho tới khi có bằng chứng đủ mạnh.
        [InputParameter("Bật cổng độ nhọn (hạ mốc bẹt xuống lớp nền)", 36)]
        public bool SharpnessGate { get; set; } = false;
        [InputParameter("Độ dày tối đa của MỐC (giá) — bằng SL của bạn", 37, 1, 20, 0.5, 1)]
        public double MaxLevelThicknessPrices { get; set; } = 4.0;

        // ---------- hiển thị ----------
        [InputParameter("Hiện bảng phiên", 30)]
        public bool ShowPanel { get; set; } = true;
        [InputParameter("Hiện vùng", 31)]
        public bool ShowZones { get; set; } = true;
        [InputParameter("Góc bảng (0=TL 1=TR 2=BL 3=BR)", 32, 0, 3, 1, 0)]
        public int PanelCorner { get; set; } = 1;
        [InputParameter("Cỡ chữ bảng", 33, 7, 20, 1, 0)]
        public int PanelFontSize { get; set; } = 10;

        [InputParameter("Màu hỗ trợ", 40)]
        public Color SupColor { get; set; } = Color.FromArgb(0x26, 0xA6, 0x9A);
        [InputParameter("Màu kháng cự", 41)]
        public Color ResColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);
        [InputParameter("Màu naked POC", 42)]
        public Color NakedColor { get; set; } = Color.Gold;
        // Sách dùng VÀNG cho "Nhiều nút" (HVN), nhưng vàng đã dành cho naked POC
        // → HVN dùng CAM để phân biệt được trên chart.
        [InputParameter("Màu HVN", 43)]
        public Color HvnColor { get; set; } = Color.FromArgb(0xFF, 0x8F, 0x00);

        // ---------- Telegram (tổng hợp: đầu ngày + buổi chiều + trước phiên Mỹ) ----------
        [InputParameter("Gửi Telegram", 50)]
        public bool TeleEnabled { get; set; } = false;
        [InputParameter("TG · Bot token", 51)]
        public string TeleBotToken { get; set; } = "";
        [InputParameter("TG · Chat ID", 52)]
        public string TeleChatId { get; set; } = "";
        [InputParameter("TG · Phiên Mỹ mở (phút/ngày; 19:20=1160)", 54, 0, 1439, 5, 0)]
        public int TeleUsStartMin { get; set; } = 1160;
        [InputParameter("TG · Báo trước phiên Mỹ (phút)", 55, 5, 120, 5, 0)]
        public int TelePreUsMin { get; set; } = 30;
        [InputParameter("TG · Cửa sổ báo sáng sau IB (nến)", 56, 1, 20, 1, 0)]
        public int TeleMorningGrace { get; set; } = 6;
        [InputParameter("TG · Báo chiều (phút/ngày; 14:00=840; 0=tắt)", 57, 0, 1439, 5, 0)]
        public int TeleAfternoonMin { get; set; } = 840;
        [InputParameter("TG · Thư mục chung (trống=mặc định)", 58)]
        public string TeleShareDir { get; set; } = "";
        [InputParameter("TG · Gửi thử ngay (bật rồi tắt)", 59)]
        public bool TeleTestNow { get; set; } = false;
        // Bạn add indicator này trên NHIỀU tab/chart cùng symbol (M30 + 2 tab M1) →
        // nếu bật ở cả 3, mỗi tab tự kiểm mốc + có thể bắn Telegram riêng, dễ ra 3 tin
        // cùng lúc (nhất là khi 3 tab lệch "Lệch giờ" nhau). CHỈ bật "true" ở ĐÚNG 1 tab
        // (khuyên: tab M1 tôi trade) — các tab còn lại để false, chart vẫn hiện panel
        // bình thường, chỉ không tự gửi tin.
        [InputParameter("TG · Tab này ĐƯỢC gửi (chỉ bật 1 tab/chart)", 60)]
        public bool TeleIsSender { get; set; } = false;
        [InputParameter("TG · Kèm lịch tin Forex Factory", 61)]
        public bool TeleShowNews { get; set; } = true;

        private bool _vaLoaded;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private ZoneRenderState _render;
        private int _digits = 1;
        private readonly PanelDrag _drag = new();   // kéo-thả bảng bằng chuột
        private readonly TeleReport _tele = new();  // gửi tổng hợp lên Telegram

        // ---- Tự nhận diện timeframe chart: nếu KHÔNG phải M30, tự lấy history
        // M30 phụ của cùng symbol qua Symbol.GetHistory() thay vì bắt người dùng
        // add đúng chart M30 (dễ nhầm khi muốn xem vùng trên chart M1 để vào lệnh).
        private HistoricalData _hd30;         // history M30 dùng để tính — của chart chính hoặc phụ
        private bool _ownHd30;                // true nếu _hd30 là history PHỤ (tự lấy, phải tự Dispose)
        private static readonly Period Period30 = new Period(BasePeriod.Minute, 30);

        public SessionZones() : base()
        {
            Name = "Session Zones";
            Description = "Gộp phiên Á/Âu/Mỹ + tường thuật + gợi ý bias Mỹ + vẽ vùng (naked POC, cụm POC, biên VA, HVN/LVN). Cần Volume Analysis. Add vào chart bất kỳ — tự lấy dữ liệu M30.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;

        protected override void OnInit()
        {
            base.OnInit();
            bool isM30 = HistoricalData?.Aggregation is HistoryAggregationTime t && t.Period.Equals(Period30);
            if (isM30)
            {
                _hd30 = HistoricalData;
                _ownHd30 = false;
            }
            else
            {
                var srcAgg = HistoricalData?.Aggregation as HistoryAggregationTime;
                var histType = srcAgg?.HistoryType ?? HistoryType.Last;
                _hd30 = Symbol.GetHistory(Period30, histType, DateTime.UtcNow.AddDays(-45));
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
            _drag.Detach();
            if (_ownHd30 && _hd30 != null) { _hd30.NewHistoryItem -= OnHd30NewBar; _hd30.Dispose(); }
            lock (_calc) { _vaLoaded = false; lock (_sync) _render = null; }
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
        private static string VN(string lab) => lab == "A" ? "Á" : lab == "AU" ? "Âu" : "Mỹ";

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
                var hd = _hd30;
                if (hd == null) return;
                int n = hd.Count; if (n == 0) return;
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

                var panel = new List<(string, Color)>();
                panel.Add(("PHIÊN HÔM NAY", Color.White));
                AddSentence(panel, asia, null, tick);
                AddSentence(panel, europe, asia, tick);
                AddSentence(panel, us, europe, tick, devTag: last.Label == "MY");
                panel.Add(($"VWAP ngày {Fmt(vwapDay)} ({(nowPrice >= vwapDay ? "giá trên" : "giá dưới")}) · VWAP tuần {Fmt(vwapWeek)} ({(nowPrice >= vwapWeek ? "giá trên" : "giá dưới")})",
                    Color.Gainsboro));

                // gợi ý bias Mỹ
                var (decision, lean, conf, reasons) = UsBias(hd, asia, europe, us, last, tick, rowStep);
                Color lc = lean > 0 ? SupColor : lean < 0 ? ResColor : Color.Gainsboro;
                panel.Add(($"→ MỸ ưu tiên: {decision} — {(lean > 0 ? "MUA" : lean < 0 ? "BÁN" : "TRUNG TÍNH")} ({conf}/100)", lc));
                for (int i = 0; i < reasons.Count && i < 3; i++) panel.Add(($"   {i + 1}. {reasons[i]}", Color.Silver));

                // ---- D6: panel phân tầng — "TPO m30 là scalp" (trader pro) ----
                //  VÙNG CANH = HVN/naked/cụm POC (tầng tuần-ngày, để chờ giá tới).
                //  BỐI CẢNH PHIÊN = biên VA/đỉnh-đáy phiên hiện tại (chỉ tham khảo,
                //  KHÔNG canh lệnh — trader pro: "k quan tâm lắm"). LVN riêng vì
                //  khác loại (chỗ tránh kỳ vọng phản ứng, không phải vùng vào lệnh).
                var zones = FindZones(hd, blocks, tick, rowStep, nowPrice);
                // CORVEN chốt "CHỈ quan tâm HVN thôi. Không dùng POC/VAH/VAL của tuần"
                // (CAU_HOI_CAN_THONG_NHAT.md §A2/§C3) → naked POC/cụm POC/băng giá trị/
                // biên VA/đỉnh-đáy phiên đều lùi về bối cảnh, TRỪ KHI đã hợp lưu (merge)
                // với một HVN — khi đó z.Label còn giữ chữ "HVN" sau MergeZones.
                bool IsHvn(Zone z) => z.Label.Contains("HVN");
                // B3/B4: chỉ zone còn là MỐC (IsMarker) mới vào "VÙNG CANH" — HVN tuần
                // (luôn là nền) và HVN ngày bị B4 hạ cấp vì bẹt đều rơi xuống nenList.
                var canhLenh = zones.Where(z => z.IsMarker && z.Type != "lvn" && IsHvn(z)).ToList();
                var boiCanh = zones.Where(z => z.IsMarker && z.Type != "lvn" && !IsHvn(z)).ToList();
                var lvnList = zones.Where(z => z.Type == "lvn").ToList();
                var nenList = zones.Where(z => !z.IsMarker && z.Type != "lvn").ToList();
                if (canhLenh.Count > 0)
                {
                    // B2: sắp theo KHOẢNG CÁCH gần→xa (không theo điểm mạnh) — người
                    // dừng lỗ 3 giá cần biết mốc GẦN NHẤT trước, mốc mạnh mà xa cả
                    // trăm giá không giúp được gì hôm nay.
                    panel.Add(("VÙNG CANH (gần→xa):", Color.Silver));
                    foreach (var z in canhLenh.OrderBy(z => Math.Abs(z.Center - nowPrice)).Take(MaxZones))
                    {
                        string sd = z.Side > 0 ? "S " : z.Side < 0 ? "R " : "· ";
                        string pr = Math.Abs(z.Hi - z.Lo) < tick ? Fmt(z.Center) : $"{Fmt(z.Lo)}–{Fmt(z.Hi)}";
                        Color zc = z.Side > 0 ? SupColor : z.Side < 0 ? ResColor : Color.Gainsboro;
                        double distGia = Math.Abs(z.Center - nowPrice) / (10.0 * tick);
                        panel.Add(($"  {sd}{pr}  {z.Label} · cách {distGia:0.0} giá [{z.Strength:0}]", zc));
                    }
                    var above = canhLenh.Where(z => z.Center > nowPrice).OrderBy(z => z.Center).Take(2).ToList();
                    var below = canhLenh.Where(z => z.Center < nowPrice).OrderByDescending(z => z.Center).Take(2).ToList();
                    if (above.Count > 0) panel.Add(($"  Nếu LONG → T: {string.Join(", ", above.Select(z => Fmt(z.Center - 2 * tick)))}", Color.DimGray));
                    if (below.Count > 0) panel.Add(($"  Nếu SHORT → T: {string.Join(", ", below.Select(z => Fmt(z.Center + 2 * tick)))}", Color.DimGray));
                }
                if (boiCanh.Count > 0)
                    panel.Add(($"Bối cảnh phiên (chỉ tham khảo): {string.Join(" · ", boiCanh.Select(z => $"{z.Label} {Fmt(z.Center)}"))}", Color.Gray));
                // B3: lớp NỀN — HVN tuần (Lo/Hi thật, gộp nhiều phiên, trôi ~20 giá/tuần
                // nên KHÔNG dùng làm điểm vào) + mốc bị B4 hạ cấp vì bẹt hơn dừng lỗ.
                if (nenList.Count > 0)
                    panel.Add(($"Nền/bối cảnh (KHÔNG đặt lệnh): {string.Join(" · ", nenList.Select(z => $"{z.Label} {Fmt(z.Lo)}–{Fmt(z.Hi)}"))}", Color.FromArgb(0x90, 0x90, 0x90)));
                if (lvnList.Count > 0)
                    panel.Add(($"LVN (xuyên nhanh, đặt SL sau): {string.Join(" · ", lvnList.Select(z => Fmt(z.Center)))}", Color.FromArgb(0x90, 0x90, 0x90)));

                lock (_sync) _render = new ZoneRenderState { Zones = zones, Panel = panel, NowPrice = nowPrice, Tick = tick };

                // ---- tổng hợp GỌN cho Telegram ----
                var tele = new List<string>();
                tele.Add($"🇺🇸 Phiên Mỹ: {decision} — {(lean > 0 ? "MUA" : lean < 0 ? "BÁN" : "TRUNG TÍNH")} ({conf}/100)");
                if (reasons.Count > 0) tele.Add($"Lý do: {reasons[0]}");
                tele.Add($"Giá hiện tại: {Fmt(nowPrice)} · VWAP ngày {Fmt(vwapDay)} ({(nowPrice >= vwapDay ? "trên" : "dưới")}) · VWAP tuần {Fmt(vwapWeek)} ({(nowPrice >= vwapWeek ? "trên" : "dưới")})");
                if (canhLenh.Count > 0)
                {
                    tele.Add("Vùng quan trọng:");
                    foreach (var z in canhLenh.Take(4))
                    {
                        string sd = z.Side > 0 ? "S" : z.Side < 0 ? "R" : "·";
                        string pr = Math.Abs(z.Hi - z.Lo) < tick ? Fmt(z.Center) : $"{Fmt(z.Lo)}–{Fmt(z.Hi)}";
                        tele.Add($"• {sd} {pr} · {z.Label} [{z.Strength:0}]");
                    }
                }
                if (boiCanh.Count > 0)
                    tele.Add($"Bối cảnh (tham khảo): {string.Join(" · ", boiCanh.Take(3).Select(z => $"{z.Label} {Fmt(z.Center)}"))}");
                ConfigTele();
                _tele.Run(hd, Symbol?.Name, "zone", tele);
            }
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

        private void AddSentence(List<(string, Color)> panel, SessionProfile s, SessionProfile prior, double tick, bool devTag = false)
        {
            if (s == null || !s.Valid) return;
            string dir = s.Direction > 0 ? "đi lên" : s.Direction < 0 ? "đi xuống" : "đi ngang";
            string cs = s.CloseState == "MẠNH" ? "đóng nửa trên (mạnh)" : s.CloseState == "YẾU" ? "đóng nửa dưới (yếu)" : "đóng giữa";
            string bal = s.Balance == "TREND" ? "có xu hướng" : s.Balance == "ROT" ? "xoay vòng" : "trung gian";
            bool thuan = (s.Delta >= 0) == (s.Direction >= 0);
            string vs = "";
            if (prior != null && prior.Valid)
            {
                var (tag, mig) = AcceptReject(s, prior, tick);
                vs = $" — {tag} (POC {mig:+0;-0}t)";
            }
            string tag2 = devTag ? " (đang chạy)" : "";
            string txt = $"{VN(s.Label)}{tag2}: {dir} {s.RangeTicks:0}t, {cs}, VA {Fmt(s.Val)}-{Fmt(s.Vah)} POC {Fmt(s.Poc)}, {bal}, Δ{s.Delta:+0;-0}({(thuan ? "thuận" : "NGHỊCH")}){vs}";
            panel.Add((txt, thuan ? Color.Gainsboro : Color.Khaki));
        }

        private (string tag, double migTicks) AcceptReject(SessionProfile b, SessionProfile a, double tick)
        {
            double ovl = Math.Max(0, Math.Min(a.Vah, b.Vah) - Math.Max(a.Val, b.Val));
            double uni = Math.Max(a.Vah, b.Vah) - Math.Min(a.Val, b.Val);
            double frac = uni > 0 ? ovl / uni : 0;
            double mig = (b.Poc - a.Poc) / tick;
            string tag = frac >= 0.5 ? "chấp nhận giá trị cũ" : frac < 0.2 ? "từ chối & dời đi" : "chồng một phần";
            return (tag, mig);
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

        private List<Zone> FindZones(HistoricalData hd, List<(string lab, int from, int to)> blocks,
                                     double tick, double rowStep, double nowPrice)
        {
            var zones = new List<Zone>();
            var lvnZones = new List<Zone>();
            int last = hd.Count - 1;
            double atr = ProfileEngine.Atr(hd, last);
            int startBlk = Math.Max(0, blocks.Count - 1 - ZoneLookbackSessions);
            var completed = new List<SessionProfile>();
            for (int i = startBlk; i < blocks.Count - 1; i++)   // bỏ block đang chạy
            {
                var sp = ProfileEngine.BuildProfile(hd, blocks[i].from, blocks[i].to, tick, rowStep, UseVolume, 0, blocks[i].lab);
                if (sp.Valid) completed.Add(sp);
            }
            int SideOf(double p) => p > nowPrice ? -1 : p < nowPrice ? 1 : 0;

            // ---- HVN/LVN gộp nhiều phiên (TUẦN + NGÀY) ----------------------
            //  Trader chuyên nghiệp canh giá ở HVN của TPO tuần/ngày, KHÔNG ở
            //  biên VA từng phiên (xem HVN-VA-TRADER-PRO.md). Nên đây là nhóm
            //  vùng mạnh nhất, đặt điểm cao hơn biên VA phiên.
            SortedDictionary<double, double> wkRows = null, dyRows = null;
            if ((ShowHvn || ShowLvn) && completed.Count > 0)
            {
                // "tuần" = TUẦN CME ĐÃ ĐÓNG gần nhất (không phải ZoneLookbackSessions
                // trượt) — xem WeekGapHours ở trên. Cần ít nhất 2 tuần trong hd mới có
                // 1 tuần đã đóng để dùng; nếu chưa đủ thì tạm dùng tuần đang chạy.
                var weekSpans = ProfileEngine.WeekSpans(hd, WeekGapHours);
                if (weekSpans.Count >= 2)
                {
                    var pw = weekSpans[weekSpans.Count - 2];
                    wkRows = ProfileEngine.RowsOver(hd, pw.fr, pw.to, rowStep, UseVolume);
                }
                else if (weekSpans.Count == 1)
                {
                    var pw = weekSpans[0];
                    wkRows = ProfileEngine.RowsOver(hd, pw.fr, pw.to, rowStep, UseVolume);
                }
                // "ngày" = 24h cuối (xấp xỉ ngày đang phát triển)
                var dayStart = completed[completed.Count - 1].End.AddHours(-24);
                int dFrom = -1;
                for (int i = startBlk; i < blocks.Count - 1; i++)
                    if (hd[blocks[i].from, SeekOriginHistory.Begin] is HistoryItemBar bb
                        && bb.TimeLeft >= dayStart) { dFrom = blocks[i].from; break; }
                if (dFrom >= 0)
                    dyRows = ProfileEngine.RowsOver(hd, dFrom, blocks[blocks.Count - 2].to, rowStep, UseVolume);
            }
            // B3: HVN tuần = LỚP NỀN — Lo/Hi THẬT (nới từ đỉnh tới khi volume tụt
            // dưới 90% đỉnh), không phải điểm. Đây là chỗ DUY NHẤT trong nhóm HVN
            // cần vùng thật; nó gộp nhiều phiên nên vốn dĩ là bối cảnh, không phải
            // mốc vào lệnh chính xác (PLAN §0.4: mốc 3 tuần trôi ~20 giá/tuần).
            if (ShowHvn && wkRows != null)
                foreach (var (p, ratio) in ProfileEngine.FindHvn(wkRows, tick).Take(MaxHvn))
                {
                    var (lo, hi) = ShowContextBands ? ProfileEngine.PeakSharpness(wkRows, p, rowStep) : (p, p);
                    zones.Add(new Zone { Center = p, Lo = lo, Hi = hi, Type = "hvn_week",
                        Side = SideOf(p), Strength = Math.Min(95, 70 + ratio * 6), IsMarker = false,
                        Label = $"HVN tuần ×{ratio:0.0}" });
                }
            // B4: HVN ngày = MỐC — giữ Lo=Hi=đỉnh (điểm, để canh lệnh chính xác),
            // nhưng đo kèm độ nhọn (nền 90%) để (a) ghi lên nhãn, (b) hạ cấp xuống
            // lớp nền nếu bẹt hơn dừng lỗ của người dùng VÀ đã bật SharpnessGate.
            if (ShowHvn && dyRows != null)
                foreach (var (p, ratio) in ProfileEngine.FindHvn(dyRows, tick).Take(MaxHvn))
                {
                    var (lo, hi) = ProfileEngine.PeakSharpness(dyRows, p, rowStep);
                    double widthGia = (hi - lo) / (10.0 * tick);
                    bool tooFlat = SharpnessGate && widthGia > MaxLevelThicknessPrices;
                    zones.Add(new Zone
                    {
                        Center = p,
                        Lo = tooFlat ? lo : p, Hi = tooFlat ? hi : p,
                        Type = "hvn_day", Side = SideOf(p),
                        Strength = Math.Min(88, 64 + ratio * 6),
                        IsMarker = !tooFlat,
                        Label = tooFlat
                            ? $"HVN ngày ×{ratio:0.0} · nền {widthGia:0} giá (bẹt, xem là bối cảnh)"
                            : $"HVN ngày ×{ratio:0.0} · nền {widthGia:0} giá",
                    });
                }
            // LVN: KHÔNG phải vùng canh lệnh — nơi giá xuyên nhanh, dùng để đặt SL /
            // biết chỗ không nên kỳ vọng phản ứng. Xét riêng khỏi trần MaxZones (D3).
            if (ShowLvn && wkRows != null)
                foreach (var (p, ratio) in ProfileEngine.FindLvn(wkRows, tick).Take(MaxLvn))
                    lvnZones.Add(new Zone { Center = p, Lo = p, Hi = p, Type = "lvn", IsMarker = false,
                        Side = SideOf(p), Strength = 30, Label = $"LVN tuần ×{ratio:0.0} (xuyên nhanh)" });

            // naked POC
            foreach (var sp in completed)
            {
                if (ProfileEngine.IsNaked(hd, sp, last))
                    zones.Add(new Zone { Center = sp.Poc, Lo = sp.Poc, Hi = sp.Poc, Type = "naked_poc",
                        Side = SideOf(sp.Poc), Strength = 72, Label = $"naked POC {VN(sp.Label)} (nam châm)" });
            }
            // cụm POC chặt (<=7t) và băng tích luỹ (<=25t)
            var pocs = completed.Select(x => x.Poc).ToList();
            foreach (var (lo, hi, c) in ProfileEngine.ClusterPocs(pocs, 7, tick, 2))
                zones.Add(new Zone { Lo = lo, Hi = hi, Center = (lo + hi) / 2, Type = "poc_cluster",
                    Side = SideOf((lo + hi) / 2), Strength = 78, Label = $"cụm POC ×{c}" });
            foreach (var (lo, hi, c) in ProfileEngine.ClusterPocs(pocs, 25, tick, 3))
                zones.Add(new Zone { Lo = lo, Hi = hi, Center = (lo + hi) / 2, Type = "value_band",
                    Side = SideOf((lo + hi) / 2), Strength = 55, Label = $"băng giá trị ×{c}" });
            // ---- D4: hạ cấp nhóm vùng trader pro nói "k quan tâm lắm" -------
            //  Trước đây lấy biên VA + đỉnh/đáy của 2 PHIÊN gần nhất (8 vùng, điểm
            //  60/45) — đúng thứ trader pro không dùng, và chiếm nhiều khe nhất.
            //  Giảm còn 1 phiên (4 vùng) + hạ điểm; vẫn giữ (không xoá hẳn) để làm
            //  mốc hợp lưu ở D2 — khi trùng HVN thì nâng điểm HVN, bản thân chúng
            //  không đủ điểm để được vẽ riêng khi đã có HVN trong tầm với.
            foreach (var sp in completed.AsEnumerable().Reverse().Take(1))
            {
                zones.Add(new Zone { Center = sp.Vah, Lo = sp.Vah, Hi = sp.Vah, Type = "va_edge", Side = SideOf(sp.Vah), Strength = 50, Label = $"VAH {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.Val, Lo = sp.Val, Hi = sp.Val, Type = "va_edge", Side = SideOf(sp.Val), Strength = 50, Label = $"VAL {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.High, Lo = sp.High, Hi = sp.High, Type = "priorhl", Side = SideOf(sp.High), Strength = 38, Label = $"Đỉnh {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.Low, Lo = sp.Low, Hi = sp.Low, Type = "priorhl", Side = SideOf(sp.Low), Strength = 38, Label = $"Đáy {VN(sp.Label)}" });
            }

            // ---- D2: gộp hợp lưu đa khung — dung sai co giãn theo ATR --------
            //  7 tick cứng quá chặt với profile tuần (range hàng nghìn tick): HVN
            //  tuần và HVN ngày cách nhau 0.3-0.8 giá KHÔNG gộp dù rõ ràng là MỘT
            //  vùng (đã đo: 87% HVN tuần có HVN ngày xác nhận trong ±1 giá — xem
            //  HVN-VA-TRADER-PRO.md). Mỗi khung đồng ý cộng thêm +8 điểm.
            double mergeTol = Math.Clamp(atr * 0.15, 0.7, 3.0);
            zones = MergeZones(zones, mergeTol);

            // ---- D1/B1: lọc theo TẦM VỚI trước khi xếp hạng -------------------
            //  Vùng mạnh nhất về cấu trúc có thể cách giá 70-80 giá (đã đo: HVN
            //  tuần #1 cách 777 tick = 78 giá khi ATR20 ≈ 16.7 giá) — ngoài tầm
            //  giao dịch trong ngày. "Mạnh" phải kết hợp "gần" mới đáng vẽ.
            //  B1: mặc định dùng bán kính CỐ ĐỊNH theo giá (ZoneRadiusPrices), vì
            //  ×ATR20 ra ~50 giá — quá xa so với dừng lỗ 3-4 giá của người dùng.
            double radius = ZoneRadiusPrices > 0
                ? ZoneRadiusPrices * 10.0 * tick
                : ZoneRangeAtr * Math.Max(atr, tick);
            zones = zones.Where(z => Math.Abs(z.Center - nowPrice) <= radius).ToList();

            // ---- D5: trần số vùng + cân đối 2 phía ---------------------------
            //  Tài liệu: đánh dấu mọi mức làm chart thành "cây thông Noel"; mật độ
            //  đúng cho chart trong ngày là 3-5 vùng.
            zones = LimitAndBalance(zones, MaxZones);

            // LVN xét riêng: không cạnh tranh khe với vùng canh lệnh, giữ nguyên
            // (đã giới hạn MaxLvn ở trên), nhưng vẫn áp lọc tầm với.
            zones.AddRange(lvnZones.Where(z => Math.Abs(z.Center - nowPrice) <= radius));
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
                var near = res.FirstOrDefault(r => Math.Abs(r.Center - z.Center) <= tolDollars);
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
            _drag.Attach(CurrentChart);
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;

            ZoneRenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;
            var gr = args.Graphics;
            var conv = win.CoordinatesConverter;
            var clip = win.ClientRectangle;

            if (ShowZones && rs.Zones != null)
            {
                // B3 (PLAN-MOC-PHAN-UNG.md): vẽ LỚP NỀN trước (dải mờ, không phải
                // chỗ đặt lệnh — HVN tuần gộp nhiều phiên + LVN + mốc bị B4 hạ
                // cấp vì quá bẹt), rồi vẽ LỚP MỐC sau đè lên (đường mảnh + nhãn +
                // khoảng cách tới giá — đây mới là chỗ đặt lệnh).
                foreach (var z in rs.Zones.Where(z => !z.IsMarker).OrderBy(z => z.Strength))
                {
                    bool isLvn = z.Type == "lvn";
                    Color col = isLvn ? Color.FromArgb(0x90, 0x90, 0x90) : HvnColor;
                    float yLo = (float)conv.GetChartY(z.Lo), yHi = (float)conv.GetChartY(z.Hi);
                    float yTop = Math.Min(yLo, yHi), yBot = Math.Max(yLo, yHi);
                    // nền mờ hơn hẳn mốc — đây chỉ là bối cảnh, không phải điểm bấm nút
                    if (!isLvn && yBot - yTop >= 1)
                    {
                        using var fill = new SolidBrush(Color.FromArgb(28, col));
                        gr.FillRectangle(fill, clip.Left, yTop, clip.Width, Math.Max(1, yBot - yTop));
                    }
                    float ym = (yTop + yBot) / 2;
                    if (ym < clip.Top || ym > clip.Bottom) continue;
                    using var pen = new Pen(Color.FromArgb(140, col), 1f) { DashStyle = DashStyle.Dash };
                    gr.DrawLine(pen, clip.Left, ym, clip.Right, ym);
                    // nhãn nhạt, không kèm khoảng cách — đây là bối cảnh, không phải mốc vào lệnh
                    using var f = new Font("Arial", 7, FontStyle.Italic);
                    using var br = new SolidBrush(Color.FromArgb(170, col));
                    gr.DrawString(z.Label, f, br, clip.Right - 190, ym - 10);
                }
                foreach (var z in rs.Zones.Where(z => z.IsMarker).OrderBy(z => z.Strength))   // yếu vẽ trước
                {
                    Color col = z.Type == "naked_poc" ? NakedColor
                              : z.Type == "hvn_day" ? HvnColor
                              : z.Side > 0 ? SupColor : z.Side < 0 ? ResColor : Color.Gray;
                    float ym = (float)conv.GetChartY(z.Center);
                    if (ym < clip.Top || ym > clip.Bottom) continue;
                    // HVN ngày đậm nhất trong nhóm mốc, naked POC nét đứt, còn lại nét mảnh.
                    float pw = z.Type == "hvn_day" ? 2f : z.Type == "naked_poc" ? 2f : 1.2f;
                    using var pen = new Pen(col, pw)
                    { DashStyle = z.Type == "naked_poc" ? DashStyle.Dash : DashStyle.Solid };
                    gr.DrawLine(pen, clip.Left, ym, clip.Right, ym);
                    // B2: nhãn LUÔN kèm khoảng cách tới giá hiện tại (giá, không phải tick) —
                    // người dừng lỗ 3 giá cần biết ngay có với tới trong ngày không.
                    double distGia = Math.Abs(z.Center - rs.NowPrice) / (10.0 * rs.Tick);
                    using var f = new Font("Arial", 8, FontStyle.Bold);
                    using var br = new SolidBrush(col);
                    gr.DrawString($"{z.Label} · cách {distGia:0.0} giá", f, br, clip.Right - 190, ym - 12);
                }
            }
            if (ShowPanel && rs.Panel != null && rs.Panel.Count > 0)
            {
                using var f = new Font("Consolas", PanelFontSize, FontStyle.Regular);
                _drag.Draw(gr, f, rs.Panel, 215, PanelCorner, clip);
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
        // B3/B4 (PLAN-MOC-PHAN-UNG.md): true = lớp MỐC (đường mảnh, đặt lệnh được),
        // false = lớp NỀN/bối cảnh (dải mờ, KHÔNG đặt lệnh — hoặc vì bản chất là
        // vùng gộp nhiều phiên [hvn_week], hoặc vì bị B4 hạ cấp do quá bẹt).
        public bool IsMarker = true;
    }

    internal sealed class ZoneRenderState
    {
        public List<Zone> Zones;
        public List<(string text, Color col)> Panel;
        public double NowPrice;
        public double Tick;   // B2: cần để quy đổi khoảng cách ra "giá" khi vẽ nhãn
    }
}
