// ============================================================================
//  M30SessionZones  —  Phiên Á/Âu/Mỹ + Vùng cần quan tâm cho QUANTOWER
// ============================================================================
//  Add vào chart M30. Gộp nến 30' thành khối phiên Á/Âu/Mỹ (theo giờ-trong-ngày
//  + gap tách cuối tuần/bảo trì). Sinh tường thuật "phiên nào làm gì" + gợi ý
//  "Mỹ ưu tiên gì" (tiếp diễn/phá/đảo/fade), và vẽ VÙNG: naked POC (nam châm),
//  cụm POC, biên VA phiên, đỉnh/đáy phiên + gợi ý target cho lệnh đang chạy.
//
//  Giờ phiên = phút-trong-ngày, giờ local = bar.TimeLeft + TzOffset (giả định
//  TimeLeft là UTC; nếu feed trả local, đặt TzOffset=0). Mặc định VN (+7):
//  Á 05:00–12:30, Âu 12:30–19:00, Mỹ 19:00–04:00. Cần Volume Analysis.
//  Build: concat ProfileEngine.cs + file này. Chi tiết: PLAN.md.
// ============================================================================
namespace M30SessionZones
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Linq;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;

    public class M30SessionZones : Indicator, IVolumeAnalysisIndicator
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

        // ---------- Telegram (tổng hợp đầu ngày + trước phiên Mỹ) ----------
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
        [InputParameter("TG · Thư mục chung (trống=mặc định)", 57)]
        public string TeleShareDir { get; set; } = "";
        [InputParameter("TG · Gửi thử ngay (bật rồi tắt)", 58)]
        public bool TeleTestNow { get; set; } = false;

        private bool _vaLoaded;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private ZoneRenderState _render;
        private int _digits = 1;
        private readonly PanelDrag _drag = new();   // kéo-thả bảng bằng chuột
        private readonly TeleReport _tele = new();  // gửi tổng hợp lên Telegram

        public M30SessionZones() : base()
        {
            Name = "M30 Session Zones";
            Description = "Gộp phiên Á/Âu/Mỹ + tường thuật + gợi ý bias Mỹ + vẽ vùng (naked POC, cụm POC, biên VA). Cần Volume Analysis. Add vào chart M30.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded() { lock (_calc) { _vaLoaded = true; } Process(); }
        protected override void OnClear() { _drag.Detach(); lock (_calc) { _vaLoaded = false; lock (_sync) _render = null; } }
        protected override void OnUpdate(UpdateArgs args)
        {
            if (!_vaLoaded) return;
            var p = HistoricalData.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
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
                var hd = HistoricalData;
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
                var panel = new List<(string, Color)>();
                panel.Add(("PHIÊN HÔM NAY", Color.White));
                AddSentence(panel, asia, null, tick);
                AddSentence(panel, europe, asia, tick);
                AddSentence(panel, us, europe, tick, devTag: last.Label == "MY");

                // gợi ý bias Mỹ
                var (decision, lean, conf, reasons) = UsBias(hd, asia, europe, us, last, tick, rowStep);
                Color lc = lean > 0 ? SupColor : lean < 0 ? ResColor : Color.Gainsboro;
                panel.Add(($"→ MỸ ưu tiên: {decision} — {(lean > 0 ? "MUA" : lean < 0 ? "BÁN" : "TRUNG TÍNH")} ({conf}/100)", lc));
                for (int i = 0; i < reasons.Count && i < 3; i++) panel.Add(($"   {i + 1}. {reasons[i]}", Color.Silver));

                // vùng
                var zones = FindZones(hd, blocks, tick, rowStep, nowPrice);
                if (zones.Count > 0)
                {
                    panel.Add(("VÙNG (mạnh→yếu):", Color.Silver));
                    foreach (var z in zones.Take(6))
                    {
                        string sd = z.Side > 0 ? "S " : z.Side < 0 ? "R " : "· ";
                        string pr = Math.Abs(z.Hi - z.Lo) < tick ? Fmt(z.Center) : $"{Fmt(z.Lo)}–{Fmt(z.Hi)}";
                        Color zc = z.Side > 0 ? SupColor : z.Side < 0 ? ResColor : Color.Gainsboro;
                        panel.Add(($"  {sd}{pr}  {z.Label} [{z.Strength:0}]", zc));
                    }
                    // gợi ý target đơn giản
                    var above = zones.Where(z => z.Center > nowPrice).OrderBy(z => z.Center).Take(2).ToList();
                    var below = zones.Where(z => z.Center < nowPrice).OrderByDescending(z => z.Center).Take(2).ToList();
                    if (above.Count > 0) panel.Add(($"  Nếu LONG → T: {string.Join(", ", above.Select(z => Fmt(z.Center - 2 * tick)))}", Color.DimGray));
                    if (below.Count > 0) panel.Add(($"  Nếu SHORT → T: {string.Join(", ", below.Select(z => Fmt(z.Center + 2 * tick)))}", Color.DimGray));
                }

                lock (_sync) _render = new ZoneRenderState { Zones = zones, Panel = panel, NowPrice = nowPrice };

                // ---- tổng hợp GỌN cho Telegram ----
                var tele = new List<string>();
                tele.Add($"🇺🇸 Phiên Mỹ: {decision} — {(lean > 0 ? "MUA" : lean < 0 ? "BÁN" : "TRUNG TÍNH")} ({conf}/100)");
                if (reasons.Count > 0) tele.Add($"Lý do: {reasons[0]}");
                tele.Add($"Giá hiện tại: {Fmt(nowPrice)}");
                if (zones.Count > 0)
                {
                    tele.Add("Vùng quan trọng:");
                    foreach (var z in zones.Take(4))
                    {
                        string sd = z.Side > 0 ? "S" : z.Side < 0 ? "R" : "·";
                        string pr = Math.Abs(z.Hi - z.Lo) < tick ? Fmt(z.Center) : $"{Fmt(z.Lo)}–{Fmt(z.Hi)}";
                        tele.Add($"• {sd} {pr} · {z.Label} [{z.Strength:0}]");
                    }
                }
                ConfigTele();
                _tele.Run(hd, Symbol?.Name, "zone", tele);
            }
        }

        private void ConfigTele()
        {
            _tele.Enabled = TeleEnabled;
            _tele.TestNow = TeleTestNow;
            _tele.BotToken = TeleBotToken?.Trim() ?? "";
            _tele.ChatId = TeleChatId?.Trim() ?? "";
            _tele.ShareDir = TeleShareDir ?? "";
            _tele.TzOffset = TzOffset;          // dùng lệch giờ sẵn có của M30
            _tele.UsStartMin = TeleUsStartMin;
            _tele.PreUsMin = TelePreUsMin;
            _tele.MorningGraceBars = TeleMorningGrace;
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
            int last = hd.Count - 1;
            int startBlk = Math.Max(0, blocks.Count - 1 - ZoneLookbackSessions);
            var completed = new List<SessionProfile>();
            for (int i = startBlk; i < blocks.Count - 1; i++)   // bỏ block đang chạy
            {
                var sp = ProfileEngine.BuildProfile(hd, blocks[i].from, blocks[i].to, tick, rowStep, UseVolume, 0, blocks[i].lab);
                if (sp.Valid) completed.Add(sp);
            }
            int SideOf(double p) => p > nowPrice ? -1 : p < nowPrice ? 1 : 0;

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
            // biên VA + đỉnh/đáy của 2 phiên gần nhất đã đóng
            foreach (var sp in completed.AsEnumerable().Reverse().Take(2))
            {
                zones.Add(new Zone { Center = sp.Vah, Lo = sp.Vah, Hi = sp.Vah, Type = "va_edge", Side = SideOf(sp.Vah), Strength = 60, Label = $"VAH {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.Val, Lo = sp.Val, Hi = sp.Val, Type = "va_edge", Side = SideOf(sp.Val), Strength = 60, Label = $"VAL {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.High, Lo = sp.High, Hi = sp.High, Type = "priorhl", Side = SideOf(sp.High), Strength = 45, Label = $"Đỉnh {VN(sp.Label)}" });
                zones.Add(new Zone { Center = sp.Low, Lo = sp.Low, Hi = sp.Low, Type = "priorhl", Side = SideOf(sp.Low), Strength = 45, Label = $"Đáy {VN(sp.Label)}" });
            }
            // gộp hợp lưu <=7t
            zones = MergeZones(zones, 7 * tick);
            return zones.OrderByDescending(z => z.Strength).ToList();
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
                    near.Strength = Math.Min(100, Math.Max(near.Strength, z.Strength) + 0.5 * Math.Min(near.Strength, z.Strength));
                    if (!near.Label.Contains(z.Label.Split(' ')[0])) near.Label += " + " + z.Label;
                }
                else res.Add(z);
            }
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
                foreach (var z in rs.Zones.OrderBy(z => z.Strength))   // yếu vẽ trước
                {
                    Color col = z.Type == "naked_poc" ? NakedColor : z.Side > 0 ? SupColor : z.Side < 0 ? ResColor : Color.Gray;
                    float yLo = (float)conv.GetChartY(z.Lo), yHi = (float)conv.GetChartY(z.Hi);
                    float yTop = Math.Min(yLo, yHi), yBot = Math.Max(yLo, yHi);
                    int alpha = (int)Math.Clamp(30 + z.Strength * 0.8, 30, 120);
                    if (yBot - yTop >= 2)
                    {
                        using var fill = new SolidBrush(Color.FromArgb(alpha / 3, col));
                        gr.FillRectangle(fill, clip.Left, yTop, clip.Width, yBot - yTop);
                    }
                    float ym = (yTop + yBot) / 2;
                    if (ym < clip.Top || ym > clip.Bottom) continue;
                    using var pen = new Pen(col, z.Type == "naked_poc" ? 2f : 1.2f)
                    { DashStyle = z.Type == "naked_poc" ? DashStyle.Dash : DashStyle.Solid };
                    gr.DrawLine(pen, clip.Left, ym, clip.Right, ym);
                    using var f = new Font("Arial", 8, FontStyle.Bold);
                    using var br = new SolidBrush(col);
                    gr.DrawString(z.Label, f, br, clip.Right - 160, ym - 12);
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
    }

    internal sealed class ZoneRenderState
    {
        public List<Zone> Zones;
        public List<(string text, Color col)> Panel;
        public double NowPrice;
    }
}
