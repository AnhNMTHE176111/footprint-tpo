// ============================================================================
//  DailyTpoBias  —  Bias NGÀY real-time (Market Profile / TPO) cho QUANTOWER
// ============================================================================
//  Add vào chart M30. Dựng profile NGÀY đang phát triển + ngày trước (gom nến
//  theo GAP thời gian — nghỉ bảo trì/cuối tuần tách ngày, không cần timezone).
//  Chấm bias bằng 6 tín hiệu (A value-relationship, B POC migration, C IB+RE
//  một chiều, D open-type, E delta, G open-location) → nhãn Tăng/Giảm + độ tin.
//  Vẽ VAH/VAL/POC/IB (nay + hôm qua) + bảng chữ tiếng Việt. Cần Volume Analysis.
//
//  Build: concat ProfileEngine.cs + file này (xem build-tpo.sh). Mọi `using` nằm
//  TRONG namespace để nối file hợp lệ.
//  Ngưỡng mặc định calibrate GC vàng (Range~900t, IB~100t, Delta~936); tự thích
//  nghi bằng trung vị 20 ngày. Chi tiết: quantower-tpo-suite/PLAN.md.
// ============================================================================
namespace DailyTpoBias
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Linq;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;

    public class DailyTpoBias : Indicator, IVolumeAnalysisIndicator
    {
        // ---------- cấu hình profile ----------
        [InputParameter("Số tick / hàng profile", 10, 1, 50, 1, 0)]
        public int RowTicks { get; set; } = 2;

        [InputParameter("Số nến IB (60' = 2 nến M30)", 11, 1, 20, 1, 0)]
        public int IbBars { get; set; } = 2;

        [InputParameter("Gap tách ngày (phút)", 12, 30, 240, 1, 0)]
        public int GapMinutes { get; set; } = 75;

        [InputParameter("Số ngày baseline (trung vị trượt)", 13, 5, 120, 1, 0)]
        public int BaselineDays { get; set; } = 20;

        [InputParameter("Dùng volume theo giá (tắt = TPO letters)", 14)]
        public bool UseVolume { get; set; } = true;

        // Ranh giới TUẦN cho VWAP tuần — cùng cơ chế với SessionZones.cs (xem
        // ProfileEngine.WeekSpans): gap > ngưỡng này giữa 2 nến M30 = hết 1 tuần CME.
        [InputParameter("Gap tách TUẦN cho VWAP tuần (giờ)", 15, 20, 60, 1, 0)]
        public int WeekGapHours { get; set; } = 30;

        // ---------- hiển thị ----------
        [InputParameter("Hiện bảng bias", 20)]
        public bool ShowPanel { get; set; } = true;

        [InputParameter("Hiện đường VA/POC/IB", 21)]
        public bool ShowLevels { get; set; } = true;

        [InputParameter("Góc bảng (0=TL 1=TR 2=BL 3=BR)", 22, 0, 3, 1, 0)]
        public int PanelCorner { get; set; } = 0;

        [InputParameter("Cỡ chữ bảng", 23, 7, 20, 1, 0)]
        public int PanelFontSize { get; set; } = 10;

        // ---------- màu ----------
        [InputParameter("Màu tăng", 30)]
        public Color BullColor { get; set; } = Color.FromArgb(0x26, 0xA6, 0x9A);
        [InputParameter("Màu giảm", 31)]
        public Color BearColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);
        [InputParameter("Màu POC", 32)]
        public Color PocColor { get; set; } = Color.Orange;
        [InputParameter("Màu VA (hôm nay)", 33)]
        public Color VaColor { get; set; } = Color.SteelBlue;
        [InputParameter("Màu mức hôm qua", 34)]
        public Color PriorColor { get; set; } = Color.FromArgb(0x90, 0x90, 0x90);

        // ---------- Telegram (tổng hợp: đầu ngày + buổi chiều + trước phiên Mỹ) ----------
        [InputParameter("Gửi Telegram", 50)]
        public bool TeleEnabled { get; set; } = false;
        [InputParameter("TG · Bot token", 51)]
        public string TeleBotToken { get; set; } = "";
        [InputParameter("TG · Chat ID", 52)]
        public string TeleChatId { get; set; } = "";
        [InputParameter("TG · Lệch giờ local (bar UTC→local)", 53, -12, 14, 1, 0)]
        public int TeleTzOffset { get; set; } = 7;
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
        // Xem SessionZones.cs: nếu add cả 2 indicator (bias + zone) trên cùng chart,
        // cả hai cùng ghi vào 1 tin Telegram gộp — nhưng chỉ 1 trong số các instance
        // đang chạy (bias/zone, nhiều tab) nên là nơi thực sự BẤM GỬI. Khuyên: bật true
        // ở CÙNG tab với SessionZones đã bật TeleIsSender, hoặc chỉ bật ở 1 trong 2.
        [InputParameter("TG · Tab này ĐƯỢC gửi (chỉ bật 1 tab/chart)", 60)]
        public bool TeleIsSender { get; set; } = false;

        private bool _vaLoaded;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private RenderState _render;
        private int _digits = 1;
        private readonly PanelDrag _drag = new();   // kéo-thả bảng bằng chuột
        private readonly TeleReport _tele = new();  // gửi tổng hợp lên Telegram

        public DailyTpoBias() : base()
        {
            Name = "Daily TPO Bias";
            Description = "Bias ngày real-time từ Market Profile/TPO: value relationship, POC migration, IB+range extension, delta. Cần Volume Analysis. Add vào chart M30.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded() { lock (_calc) { _vaLoaded = true; } Process(); }
        protected override void OnClear() { _drag.Detach(); lock (_calc) { _vaLoaded = false; lock (_sync) _render = null; } }

        protected override void OnUpdate(UpdateArgs args)
        {
            ConfigTele();
            _tele.PollTest(Symbol?.Name);        // nút gửi thử: xử lý ngay, không đợi VA
            if (!_vaLoaded) return;
            var p = HistoricalData.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            Process();
        }

        private string Fmt(double p) => double.IsNaN(p) ? "—" : Math.Round(p, _digits).ToString("0.0##");

        private void Process()
        {
            lock (_calc)
            {
                double tick = Symbol?.TickSize ?? 0;
                if (tick <= 0) return;
                _digits = Math.Max(0, (int)Math.Round(-Math.Log10(tick)));
                var hd = HistoricalData;
                int n = hd.Count; if (n == 0) return;
                double rowStep = tick * Math.Max(1, RowTicks);

                var groups = ProfileEngine.GroupByGap(hd, GapMinutes);
                if (groups.Count == 0) return;

                var dg = groups[groups.Count - 1];                          // ngày đang phát triển
                var dev = ProfileEngine.BuildProfile(hd, dg.from, dg.to, tick, rowStep, UseVolume, IbBars, "dev");
                SessionProfile prior = null;
                if (groups.Count >= 2)
                {
                    var pg = groups[groups.Count - 2];
                    prior = ProfileEngine.BuildProfile(hd, pg.from, pg.to, tick, rowStep, UseVolume, IbBars, "prior");
                }

                // baseline trung vị trượt từ các ngày ĐÃ ĐÓNG (bỏ ngày đang chạy, bỏ ngày cụt)
                var ranges = new List<double>(); var ibs = new List<double>(); var deltas = new List<double>();
                int firstClosed = Math.Max(0, groups.Count - 1 - BaselineDays);
                for (int g = firstClosed; g < groups.Count - 1; g++)
                {
                    var sp = ProfileEngine.BuildProfile(hd, groups[g].from, groups[g].to, tick, rowStep, UseVolume, IbBars, "b");
                    if (sp.Bars < 20) continue;                              // bỏ ngày cụt
                    ranges.Add(sp.RangeTicks); ibs.Add(sp.IbRangeTicks); deltas.Add(Math.Abs(sp.Delta));
                }
                double RangeTypical = ranges.Count > 0 ? ProfileEngine.Median(ranges) : 900;
                double IBTypical = ibs.Count > 0 ? ProfileEngine.Median(ibs) : 100;

                // ---- VWAP neo NGÀY/TUẦN — "vwap ngày scalp" (CORVEN), tuần cho KB-A ----
                double vwapDay = ProfileEngine.VwapAt(hd, dg.from, dg.to);
                var weekSpans = ProfileEngine.WeekSpans(hd, WeekGapHours);
                int weekFr = weekSpans.Count > 0 ? weekSpans[weekSpans.Count - 1].fr : dg.from;
                double vwapWeek = ProfileEngine.VwapAt(hd, weekFr, dg.to);

                // ---- HVN tuần/ngày ĐÃ ĐÓNG — CHỈ để CẢNH BÁO "gần HVN" (không chấm
                // điểm hướng: CORVEN xác nhận cả fade LẪN break-retest đều xảy ra tại
                // HVN — CAU_HOI_CAN_THONG_NHAT.md §C2 — nên không có dấu rõ ràng).
                SortedDictionary<double, double> wkRows = null, dyRows = null;
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
                if (prior != null && prior.Valid) dyRows = ProfileEngine.RowsOver(hd, prior.FromIdx, prior.ToIdx, rowStep, UseVolume);

                (double price, double ratio, string tf)? nearestHvn = null;
                void Consider(SortedDictionary<double, double> rows, string tf)
                {
                    if (rows == null) return;
                    foreach (var (p, ratio) in ProfileEngine.FindHvn(rows, tick).Take(3))
                        if (nearestHvn == null || Math.Abs(p - dev.Close) < Math.Abs(nearestHvn.Value.price - dev.Close))
                            nearestHvn = (p, ratio, tf);
                }
                Consider(wkRows, "tuần");
                Consider(dyRows, "ngày");

                var rs = ComputeBias(dev, prior, tick, RangeTypical, IBTypical, vwapDay, vwapWeek, nearestHvn);
                rs.Dev = dev; rs.Prior = prior;
                lock (_sync) _render = rs;

                ConfigTele();
                _tele.Run(hd, Symbol?.Name, "bias", rs.Tele);
            }
        }

        private void ConfigTele()
        {
            _tele.Enabled = TeleEnabled;
            _tele.TestNow = TeleTestNow;
            _tele.IsSender = TeleIsSender;
            _tele.BotToken = TeleBotToken?.Trim() ?? "";
            _tele.ChatId = TeleChatId?.Trim() ?? "";
            _tele.ShareDir = TeleShareDir ?? "";
            _tele.TzOffset = TeleTzOffset;
            _tele.UsStartMin = TeleUsStartMin;
            _tele.PreUsMin = TelePreUsMin;
            _tele.MorningGraceBars = TeleMorningGrace;
            _tele.AfternoonMin = TeleAfternoonMin;
            _tele.IbBars = IbBars;
            _tele.GapMinutes = GapMinutes;
        }

        private RenderState ComputeBias(SessionProfile dev, SessionProfile prior, double tick,
                                        double RangeTypical, double IBTypical,
                                        double vwapDay, double vwapWeek, (double price, double ratio, string tf)? nearestHvn)
        {
            int bracket = dev.Bars;
            bool priorOk = prior != null && prior.Valid;
            var sig = new List<(double s, double wramp, string reason)>();

            // A — value relationship (w25)
            if (priorOk && dev.Valid)
            {
                double gap = 0.03 * RangeTypical * tick;
                var (lab, s) = ProfileEngine.ValueRelation(dev.Vah, dev.Val, dev.Close, prior.Vah, prior.Val, prior.Poc, gap);
                double ramp = bracket >= 5 ? 1.0 : bracket >= 3 ? 0.6 : 0.3;
                sig.Add((s, 25 * ramp, $"Vùng giá trị {lab}"));
            }
            // B — POC migration (w15)
            if (priorOk && !double.IsNaN(dev.Poc))
            {
                double shift = (dev.Poc - prior.Poc) / (RangeTypical * tick);
                double s = ProfileEngine.Clamp(shift / 0.10, -1, 1);
                double ramp = bracket >= 4 ? 1.0 : bracket >= 2 ? 0.5 : 0.0;
                if (ramp > 0 && Math.Abs((dev.Poc - prior.Poc) / tick) >= 9)
                    sig.Add((s, 15 * ramp, $"POC dịch {(dev.Poc - prior.Poc) / tick:+0;-0}t"));
            }
            // C — IB + range extension một chiều (w15, chỉ sau IB)
            if (bracket >= IbBars && !double.IsNaN(dev.IbHigh))
            {
                double reUp = (dev.High - dev.IbHigh) / tick, reDn = (dev.IbLow - dev.Low) / tick;
                double ib = Math.Max(1, dev.IbRangeTicks);
                bool oneSided = (reUp > 0.5 * ib) ^ (reDn > 0.5 * ib);
                double s = 0;
                if (oneSided && reUp > reDn) s = Math.Min(1, reUp / ib);
                else if (oneSided && reDn > reUp) s = -Math.Min(1, reDn / ib);
                else if (reUp > 0.5 * ib && reDn > 0.5 * ib) s = 0.2 * Math.Sign(dev.Close - (double.IsNaN(dev.Mid) ? dev.Close : dev.Mid));
                if (Math.Abs(s) > 1e-6)
                    sig.Add((s, 15.0, s > 0 ? $"Mở rộng IB lên +{reUp:0}t" : $"Mở rộng IB xuống +{reDn:0}t"));
            }
            // D — open type (w12, đơn giản: chỉ open-drive)
            if (bracket >= 1 && dev.FromIdx >= 0 && HistoricalData[dev.FromIdx, SeekOriginHistory.Begin] is HistoryItemBar b1)
            {
                double r1 = b1.High - b1.Low;
                if (r1 > 0)
                {
                    double s = 0; string why = null;
                    if ((b1.Open - b1.Low) <= 0.15 * r1 && (b1.Close - b1.Open) >= 0.5 * r1) { s = 1; why = "Open-Drive tăng"; }
                    else if ((b1.High - b1.Open) <= 0.15 * r1 && (b1.Open - b1.Close) >= 0.5 * r1) { s = -1; why = "Open-Drive giảm"; }
                    if (s != 0) { double ramp = bracket >= 2 ? 1.0 : 0.5; sig.Add((s, 12 * ramp, why)); }
                }
            }
            // E — delta xác nhận (w10, de-skew -0.7%)
            if (dev.Volume > 0)
            {
                double dpct = 100 * dev.Delta / dev.Volume;
                double s = ProfileEngine.Clamp((dpct - (-0.7)) / 1.5, -1, 1);
                if (Math.Abs(s) > 0.05) sig.Add((s, 10.0, $"Delta {(dev.Delta >= 0 ? "+" : "")}{dpct:0.0}%/vol"));
            }
            // G — open location vs VA hôm qua (w8)
            if (priorOk)
            {
                double s = 0; string why = null;
                if (dev.Open > prior.Vah) { s = 0.4; why = "Mở trên vùng giá trị hôm qua"; }
                else if (dev.Open < prior.Val) { s = -0.4; why = "Mở dưới vùng giá trị hôm qua"; }
                if (s != 0) sig.Add((s, 8.0, why));
            }
            // F — giá vs VWAP ngày (w15). CORVEN: "vwap ngày scalp" — trên/dưới VWAP là
            // dấu hiệu bias trực tiếp, không mơ hồ như HVN (§C1/§C2). Chỉ tính khi VWAP
            // đã đủ nến để có ý nghĩa (không phải ngay nến mở).
            if (!double.IsNaN(vwapDay) && bracket >= 2)
            {
                double distTicks = (dev.Close - vwapDay) / tick;
                double s = ProfileEngine.Clamp(distTicks / (0.15 * RangeTypical), -1, 1);
                if (Math.Abs(s) > 0.05)
                    sig.Add((s, 15.0, $"Giá {(s > 0 ? "trên" : "dưới")} VWAP ngày ({distTicks:+0;-0}t)"));
            }
            // H — giá vs VWAP tuần (w10, nhẹ hơn ngày vì đây là bias NGÀY)
            if (!double.IsNaN(vwapWeek) && bracket >= 2)
            {
                double distTicks = (dev.Close - vwapWeek) / tick;
                double s = ProfileEngine.Clamp(distTicks / (0.5 * RangeTypical), -1, 1);
                if (Math.Abs(s) > 0.05)
                    sig.Add((s, 10.0, $"Giá {(s > 0 ? "trên" : "dưới")} VWAP tuần ({distTicks:+0;-0}t)"));
            }

            // tổng hợp
            double S = 0, fired = 0;
            foreach (var x in sig) { S += x.s * x.wramp; if (x.wramp > 0) fired += Math.Abs(x.wramp); }
            double aligned = 0;
            foreach (var x in sig) if (x.s != 0 && Math.Sign(x.s) == Math.Sign(S)) aligned += Math.Abs(x.wramp);
            double a = fired > 0 ? aligned / fired : 0.5;

            string label = S >= 45 ? "TĂNG MẠNH" : S >= 18 ? "TĂNG" : S > -18 ? "TRUNG TÍNH" : S > -45 ? "GIẢM" : "GIẢM MẠNH";
            int cSign = S >= 18 ? 1 : S <= -18 ? -1 : 0;
            double Cp = bracket < IbBars ? 68 : bracket < IbBars + 3 ? 90 : 95;
            int confidence = (int)Math.Round(Math.Min(Cp, 100 * Math.Min(1, Math.Abs(S) / 40)) * (0.4 + 0.6 * a));

            // HVN gần giá → KHÔNG chấm hướng (§C2: cả fade lẫn break-retest đều xảy ra),
            // chỉ hạ tin cậy + cảnh báo chờ phản ứng rõ ràng trước khi tin bias.
            string hvnNote = null;
            if (nearestHvn != null)
            {
                double distT = Math.Abs(nearestHvn.Value.price - dev.Close) / tick;
                double nearTol = Math.Max(10, 0.02 * RangeTypical);
                if (distT <= nearTol)
                {
                    confidence = (int)Math.Round(confidence * 0.75);
                    hvnNote = $"⚠ Gần HVN {nearestHvn.Value.tf} ×{nearestHvn.Value.ratio:0.0} (cách {distT:0}t) — chờ phản ứng rõ trước khi tin bias";
                }
            }

            string phase = bracket < IbBars ? "Mở cửa / tạo IB" : bracket < IbBars + 3 ? "IB xong (quyết định)" : "Giữa/cuối phiên";
            string dayType = DayTypeGuess(dev, bracket, IBTypical, tick);

            // top 3 lý do theo |đóng góp|
            var reasons = sig.Where(x => Math.Abs(x.s * x.wramp) > 1e-6)
                             .OrderByDescending(x => Math.Abs(x.s * x.wramp))
                             .Take(3).Select(x => x.reason).ToList();

            var panel = new List<(string, Color)>();
            Color cCol = cSign > 0 ? BullColor : cSign < 0 ? BearColor : Color.Gainsboro;
            panel.Add(($"BIAS: {label}   ({(S >= 0 ? "+" : "")}{S:0})   tin cậy {confidence}/100", cCol));
            panel.Add(($"Kiểu ngày (dự đoán): {dayType}", Color.Gainsboro));
            panel.Add(($"Pha: {phase}  |  nến: {bracket}", Color.Gainsboro));
            if (reasons.Count > 0) panel.Add(("Lý do:", Color.Silver));
            for (int i = 0; i < reasons.Count; i++) panel.Add(($"  {i + 1}. {reasons[i]}", Color.Silver));
            if (priorOk)
                panel.Add(($"Hôm qua: VAH {Fmt(prior.Vah)} POC {Fmt(prior.Poc)} VAL {Fmt(prior.Val)}", PriorColor));
            if (!double.IsNaN(dev.IbHigh))
            {
                string wide = dev.IbRangeTicks > 1.4 * IBTypical ? "rộng" : dev.IbRangeTicks < 0.7 * IBTypical ? "hẹp" : "vừa";
                panel.Add(($"IB nay: {Fmt(dev.IbLow)}–{Fmt(dev.IbHigh)} ({wide} vs {IBTypical:0}t)", Color.Gainsboro));
            }
            if (!double.IsNaN(vwapDay))
                panel.Add(($"VWAP ngày {Fmt(vwapDay)} ({(dev.Close >= vwapDay ? "giá trên" : "giá dưới")}) · VWAP tuần {Fmt(vwapWeek)} ({(dev.Close >= vwapWeek ? "giá trên" : "giá dưới")})", Color.Gainsboro));
            if (hvnNote != null) panel.Add((hvnNote, Color.Khaki));

            // ---- tổng hợp GỌN cho Telegram ----
            var tele = new List<string>();
            tele.Add($"📊 Bias NGÀY: {label} ({(S >= 0 ? "+" : "")}{S:0}) · tin {confidence}/100");
            tele.Add($"Kiểu ngày: {dayType} · Pha: {phase}");
            if (reasons.Count > 0) tele.Add($"Lý do: {reasons[0]}");
            if (priorOk) tele.Add($"Hôm qua: VAH {Fmt(prior.Vah)} · POC {Fmt(prior.Poc)} · VAL {Fmt(prior.Val)}");
            if (!double.IsNaN(dev.IbHigh)) tele.Add($"IB nay: {Fmt(dev.IbLow)}–{Fmt(dev.IbHigh)}");
            if (!double.IsNaN(vwapDay)) tele.Add($"VWAP ngày {Fmt(vwapDay)} ({(dev.Close >= vwapDay ? "trên" : "dưới")}) · VWAP tuần {Fmt(vwapWeek)} ({(dev.Close >= vwapWeek ? "trên" : "dưới")})");
            if (hvnNote != null) tele.Add(hvnNote);

            return new RenderState { Panel = panel, Tele = tele };
        }

        private string DayTypeGuess(SessionProfile dev, int bracket, double IBTypical, double tick)
        {
            if (bracket < IbBars || double.IsNaN(dev.IbHigh)) return "Chờ IB";
            double ib = Math.Max(1, dev.IbRangeTicks);
            double reUp = (dev.High - dev.IbHigh) / tick, reDn = (dev.IbLow - dev.Low) / tick;
            bool oneSided = (reUp > 0.5 * ib) ^ (reDn > 0.5 * ib);
            double vaRatio = dev.RangeTicks > 0 ? dev.VaWidthTicks / dev.RangeTicks : 1;
            if (ib < 0.7 * IBTypical && oneSided && vaRatio < 0.40) return "Xu hướng (theo)";
            if (dev.IbRangeTicks > 1.4 * IBTypical && reUp < 0.5 * ib && reDn < 0.5 * ib) return "Bình thường (fade biên)";
            if (reUp > 0.5 * ib && reDn > 0.5 * ib && reUp < ib && reDn < ib) return "Trung tính (đứng ngoài)";
            return "Biến thể / chưa rõ";
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

            RenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;

            var gr = args.Graphics;
            var conv = win.CoordinatesConverter;
            var clip = win.ClientRectangle;

            void DrawLevels(SessionProfile sp, bool isPrior)
            {
                if (sp == null || !sp.Valid) return;
                float xL = clip.Left, xR = clip.Right;
                try { xL = Math.Max(clip.Left, (float)conv.GetChartX(sp.Start)); } catch { }
                void hline(double price, Color col, float w, DashStyle dash, string lbl)
                {
                    if (double.IsNaN(price)) return;
                    float y = (float)conv.GetChartY(price);
                    if (y < clip.Top || y > clip.Bottom) return;
                    using var pen = new Pen(col, w) { DashStyle = dash };
                    gr.DrawLine(pen, xL, y, xR, y);
                    using var f = new Font("Arial", 8, FontStyle.Bold);
                    using var br = new SolidBrush(col);
                    gr.DrawString($"{lbl} {Fmt(price)}", f, br, xR - 92, y - 12);
                }
                if (isPrior)
                {
                    hline(sp.Vah, PriorColor, 1, DashStyle.Dash, "yVAH");
                    hline(sp.Poc, PriorColor, 1, DashStyle.Dash, "yPOC");
                    hline(sp.Val, PriorColor, 1, DashStyle.Dash, "yVAL");
                }
                else
                {
                    hline(sp.Vah, VaColor, 1.5f, DashStyle.Solid, "VAH");
                    hline(sp.Poc, PocColor, 2f, DashStyle.Solid, "POC");
                    hline(sp.Val, VaColor, 1.5f, DashStyle.Solid, "VAL");
                    hline(sp.IbHigh, Color.DimGray, 1, DashStyle.Dot, "IBH");
                    hline(sp.IbLow, Color.DimGray, 1, DashStyle.Dot, "IBL");
                }
            }

            if (ShowLevels) { DrawLevels(rs.Prior, true); DrawLevels(rs.Dev, false); }
            if (ShowPanel && rs.Panel != null && rs.Panel.Count > 0) DrawPanel(gr, clip, rs.Panel);
        }

        private void DrawPanel(Graphics gr, Rectangle clip, List<(string text, Color col)> lines)
        {
            using var f = new Font("Consolas", PanelFontSize, FontStyle.Regular);
            _drag.Draw(gr, f, lines, 215, PanelCorner, clip);
        }
    }

    internal sealed class RenderState
    {
        public SessionProfile Dev, Prior;
        public List<(string text, Color col)> Panel;
        public List<string> Tele;
    }
}
