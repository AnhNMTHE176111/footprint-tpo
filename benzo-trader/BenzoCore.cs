// ============================================================================
//  BenzoCore — LOGIC THUẦN của Benzo Trader (không tham chiếu Quantower SDK)
// ============================================================================
//  Tách riêng khỏi lớp Indicator để unit test được (benzo-trader/tests biên dịch
//  chính file này). Gồm: Signal, BarData, ISetupDetector + SetupContext, mô phỏng
//  kết quả lệnh (Simulate), thống kê theo setup, mốc "Đặt lại thống kê", niêm phong
//  tín hiệu (SignalCache), engine xử lý nến đã đóng (BenzoEngine), caption Telegram,
//  CSV log, client Telegram (sendMessage / sendPhoto multipart).
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections;
    using System.Collections.Generic;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Net.Http;
    using System.Net.Http.Headers;
    using System.Text;
    using System.Text.Json;
    using System.Text.Json.Serialization;
    using System.Threading;
    using System.Threading.Tasks;

    // ---------------------------------------------------------------- dữ liệu
    /// <summary>Một tín hiệu. Setup 'A'..'D'. Side +1 = BUY, -1 = SELL. Time = THỜI GIAN MỞ của nến vào (UTC).</summary>
    public sealed class Signal
    {
        public string Id { get; set; } = "";
        public DateTime Time { get; set; }
        public char Setup { get; set; }
        public int Side { get; set; }
        public double Entry { get; set; }
        public double Sl { get; set; }
        public double Tp { get; set; }
        public string Reason { get; set; } = "";
        public string Zone { get; set; } = "";
        public string Outcome { get; set; } = "OPEN";     // OPEN | TP | SL
        public DateTime ExitTime { get; set; }            // thời gian MỞ của nến chạm TP/SL (UTC); mặc định = MinValue khi còn mở
        public double R { get; set; }                     // R thực (đã trừ chi phí) khi đã đóng; 0 khi còn mở
        [JsonIgnore] public int BarIdx { get; set; } = -1; // chỉ số nến vào trong engine (không lưu file)

        public double Risk => Math.Abs(Entry - Sl);
        public double Reward => Math.Abs(Tp - Entry);
        public bool IsClosed => Outcome == "TP" || Outcome == "SL";
        public Signal Clone() => (Signal)MemberwiseClone();
    }

    /// <summary>Nến M1 đã đóng, đủ dữ liệu cho detector. Time = thời gian MỞ nến (UTC).</summary>
    public sealed class BarData
    {
        public int Idx;
        public DateTime Time;
        public double O, H, L, C;
        public double Vol, BuyVol, SellVol, Delta;
        public double Range => H - L;
        public double Body => Math.Abs(C - O);
    }

    /// <summary>Một mức giá của footprint. Bid = khớp ở Bid (sell chủ động), Ask = khớp ở Ask (buy chủ động).</summary>
    public struct LevelVol
    {
        public double Price, Bid, Ask;
        /// <summary>Tổng volume mức giá (có thể lớn hơn Bid+Ask khi có lệnh không phân loại được bên).</summary>
        public double Vol;
        public LevelVol(double price, double bid, double ask) { Price = price; Bid = bid; Ask = ask; Vol = bid + ask; }
        public LevelVol(double price, double bid, double ask, double vol) { Price = price; Bid = bid; Ask = ask; Vol = vol; }
    }

    /// <summary>Danh sách nến CHỈ ĐỌC được tới nến đã đóng đang xét — chống nhìn trước (look-ahead) bằng cấu trúc.</summary>
    public sealed class ClosedBars : IReadOnlyList<BarData>
    {
        private readonly List<BarData> _src;
        public int Limit;   // số nến nhìn thấy = chỉ số nến đang xét + 1
        public ClosedBars(List<BarData> src) { _src = src; Limit = src.Count; }
        public int Count => Limit;
        public BarData this[int i]
        {
            get
            {
                if (i < 0 || i >= Limit) throw new IndexOutOfRangeException($"nến {i} ngoài vùng đã đóng (0..{Limit - 1}) — cấm nhìn trước");
                return _src[i];
            }
        }
        public IEnumerator<BarData> GetEnumerator() { for (int i = 0; i < Limit; i++) yield return _src[i]; }
        IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
    }

    /// <summary>Bối cảnh đưa cho detector mỗi nến đóng.</summary>
    public sealed class SetupContext
    {
        public string Symbol = "";
        public double Tick = 0.1;                 // bước giá tối thiểu
        public int TzOffset = 7;                  // UTC → giờ VN
        public int BarMinutes = 1;                // độ dài nến (phút)
        public ClosedBars Bars;                   // chỉ thấy 0..closedIdx
        public IReadOnlyList<Signal> Signals;     // mọi tín hiệu đã mở TRƯỚC nến này (đếm lệnh/vùng, ngắt mạch 3 SL...)
        public Func<int, IReadOnlyList<LevelVol>> GetLevels = _ => Array.Empty<LevelVol>(); // footprint từng mức giá của nến idx
        public Func<DateTime, bool> IsNewsBlocked = _ => false;  // utc → trong ±15' tin USD mức cao
        public BenzoZones Zones;                  // vùng/VWAP/chế độ M5/helper — engine đẩy mỗi nến đóng TRƯỚC khi gọi detector
        public DateTime ToVn(DateTime utc) => utc.AddHours(TzOffset);
    }

    /// <summary>
    /// Bộ dò một setup. TryDetect chạy MỘT lần cho mỗi nến đã đóng (closedIdx = chỉ số nến vừa đóng, nhìn được
    /// ctx.Bars[0..closedIdx]). Trả null nếu không có tín hiệu. Chỉ cần điền Setup, Side, Entry, Sl, Tp, Reason, Zone —
    /// Time/Id/Outcome do engine gán. Chỉ gọi khi KHÔNG có lệnh đang mở (1 lệnh mở cùng lúc) và setup đang bật.
    /// </summary>
    public interface ISetupDetector
    {
        char Setup { get; }
        Signal TryDetect(SetupContext ctx, int closedIdx);
    }

    /// <summary>
    /// Detector có trạng thái: engine gọi Observe cho MỌI nến đã đóng (kể cả khi đang có lệnh mở / setup đang tắt / nến đã niêm phong)
    /// để trạng thái nội bộ (nhịp hồi, đếm lệnh/vùng...) liên tục; TryDetect chỉ trả kết quả đã tính ở Observe của chính nến đó.
    /// </summary>
    public interface IObservingDetector : ISetupDetector
    {
        void Observe(SetupContext ctx, int closedIdx);
    }

    // ---------------------------------------------------------------- lõi tính toán
    public static class BenzoCore
    {
        /// <summary>Đổi số này mỗi khi logic detector đổi → cache niêm phong cũ bị bỏ (không giữ kết quả của logic cũ).</summary>
        public const string LogicVersion = "port-2";
        /// <summary>Chi phí mỗi lệnh (giá): spread + trượt, GC tick 0,1.</summary>
        public const double CostPrice = 0.2;
        public const int NewsBlockMinutes = 15;
        /// <summary>"Mở ảo" (Hệ thống 3.2): 19:20-20:30 VN theo mốc neo Mỹ (sm 860..929) — không phát tín hiệu mới.</summary>
        public static bool InVirtualOpen(int sm) => sm >= 860 && sm < 930;

        /// <summary>Chọn cửa sổ con chứa vùng chart: nhỏ nhất mà vẫn ≥ kích thước chart (trừ 2px), và không quá 2,5× diện tích chart
        /// (loại panel bao cả workspace). Trả chỉ số trong danh sách hoặc −1.</summary>
        public static int PickChartRect(IList<int[]> rects, int chartW, int chartH)
        {
            if (rects == null || chartW < 50 || chartH < 50) return -1;
            int best = -1; long bestArea = long.MaxValue;
            for (int i = 0; i < rects.Count; i++)
            {
                int w = rects[i][2] - rects[i][0], h = rects[i][3] - rects[i][1];
                if (w < chartW - 2 || h < chartH - 2) continue;
                long area = (long)w * h;
                if (area > 2.5 * chartW * chartH) continue;
                if (area < bestArea) { bestArea = area; best = i; }
            }
            return best;
        }
        public const int TeleMaxAgeSec = 90;

        public static readonly char[] Setups = { 'A', 'B', 'C', 'D' };

        public static string SetupName(char s) => s switch
        {
            'A' => "Phá hồi",
            'B' => "Hấp thụ",
            'C' => "Fade cạnh",
            'D' => "Trap",
            _ => "?"
        };

        public static string MakeId(string symbol, DateTime barOpenUtc, char setup, int side) =>
            $"{symbol}|{barOpenUtc:yyyyMMddHHmm}|{setup}|{(side > 0 ? 'B' : 'S')}";

        /// <summary>Gán Time/Id/Outcome cho tín hiệu mới từ detector.</summary>
        public static void Finalize(Signal s, string symbol, DateTime barOpenUtc)
        {
            s.Time = barOpenUtc;
            s.Id = MakeId(symbol, barOpenUtc, s.Setup, s.Side);
            s.Outcome = "OPEN";
            s.ExitTime = DateTime.MinValue;
            s.R = 0;
        }

        // ---- mô phỏng ----
        /// <summary>
        /// Áp MỘT nến đã đóng lên lệnh đang mở. Chạm cả SL lẫn TP cùng nến ⇒ tính SL (bi quan). Trả true nếu lệnh đóng.
        /// R đã trừ chi phí CostPrice: TP = (lời − chi phí)/rủi ro, SL = −(rủi ro + chi phí)/rủi ro.
        /// </summary>
        public static bool StepBar(Signal s, BarData b)
        {
            if (s.IsClosed) return true;
            bool hitSl = s.Side > 0 ? b.L <= s.Sl : b.H >= s.Sl;
            bool hitTp = s.Side > 0 ? b.H >= s.Tp : b.L <= s.Tp;
            if (!hitSl && !hitTp) return false;
            double risk = s.Risk;
            if (risk <= 1e-9) risk = 1e-9;
            if (hitSl)
            {
                s.Outcome = "SL";
                s.R = (-risk - CostPrice) / risk;
            }
            else
            {
                s.Outcome = "TP";
                s.R = (s.Reward - CostPrice) / risk;
            }
            s.ExitTime = b.Time;
            return true;
        }

        /// <summary>Mô phỏng từ nến SAU nến vào tới hết danh sách (dùng cho test / tính lại).</summary>
        public static bool Simulate(Signal s, IReadOnlyList<BarData> bars, int entryIdx)
        {
            for (int j = entryIdx + 1; j < bars.Count; j++)
                if (StepBar(s, bars[j])) return true;
            return false;
        }

        // ---- thống kê ----
        public sealed class SetupStat
        {
            public char Setup;              // 'A'..'D', hoặc '*' = tổng
            public int Wins, Losses, Open;
            public double SumR;
            public int N => Wins + Losses;  // số lệnh ĐÃ ĐÓNG
            public double WinRate => N > 0 ? 100.0 * Wins / N : 0;
        }

        public sealed class StatsResult
        {
            public SetupStat Total = new SetupStat { Setup = '*' };
            public SetupStat[] By = Setups.Select(c => new SetupStat { Setup = c }).ToArray();
        }

        /// <summary>Chỉ đếm lệnh có Time ≥ resetUtc (null = đếm hết lịch sử).</summary>
        public static StatsResult ComputeStats(IEnumerable<Signal> sigs, DateTime? resetUtc)
        {
            var r = new StatsResult();
            foreach (var s in sigs)
            {
                if (resetUtc.HasValue && s.Time < resetUtc.Value) continue;
                int k = Array.IndexOf(Setups, s.Setup);
                if (k < 0) continue;
                foreach (var st in new[] { r.By[k], r.Total })
                {
                    if (s.Outcome == "TP") { st.Wins++; st.SumR += s.R; }
                    else if (s.Outcome == "SL") { st.Losses++; st.SumR += s.R; }
                    else st.Open++;
                }
            }
            return r;
        }

        /// <summary>Dạng số kiểu Việt (dấu phẩy thập phân).</summary>
        public static string Num(double v, string fmt = "0.0")
        {
            if (Math.Abs(v) < 1e-12) v = 0;
            return v.ToString(fmt, CultureInfo.InvariantCulture).Replace('.', ',');
        }
        public static string SignedR(double r)
        {
            string t = Num(Math.Abs(r), "0.0") + "R";
            return r < -0.05 ? "−" + t : (r > 0.05 ? "+" + t : t);
        }

        /// <summary>Đúng 5 dòng bảng: dòng tổng + 4 setup (plan 2.2). enabled: công tắc bật của A..D.</summary>
        public static List<string> TableLines(StatsResult st, bool[] enabled)
        {
            var lines = new List<string>(5);
            string open = st.Total.Open > 0 ? $" · {st.Total.Open} đang mở" : "";
            lines.Add($"BENZO · Tổng {st.Total.N} lệnh · {st.Total.Wins} thắng · {st.Total.Losses} thua · "
                    + $"{Num(st.Total.WinRate)}% · {SignedR(st.Total.SumR)}{open}");
            for (int i = 0; i < Setups.Length; i++)
            {
                var s = st.By[i];
                string name = (Setups[i] + " " + SetupName(Setups[i])).PadRight(13);
                string off = enabled != null && i < enabled.Length && !enabled[i] ? "   (tắt)" : "";
                lines.Add($"{name}{s.N} · {s.Wins}/{s.Losses} · {Num(s.WinRate, "0")}% · {SignedR(s.SumR)}{off}");
            }
            return lines;
        }

        // ---- mốc đặt lại thống kê ----
        public static DateTime? LoadResetMark(string path)
        {
            try
            {
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) return null;
                string t = File.ReadAllText(path).Trim();
                if (DateTime.TryParse(t, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out var d)) return d;
            }
            catch { }
            return null;
        }
        public static void SaveResetMark(string path, DateTime utc)
        {
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            File.WriteAllText(path, utc.ToString("o", CultureInfo.InvariantCulture));
        }

        // ---- Telegram caption ----
        public static string FmtPrice(double p, int digits) => Num(p, digits <= 0 ? "0" : "0." + new string('0', digits));

        /// <summary>Caption tin MỞ lệnh theo mẫu plan 2.2. barMinutes: để ra giờ ĐÓNG nến vào (= giờ vào lệnh).</summary>
        public static string ComposeOpen(Signal s, string symbol, int tzOffset, int barMinutes, int digits)
        {
            double risk = s.Risk, rr = risk > 1e-9 ? s.Reward / risk : 0;
            string icon = s.Side > 0 ? "🟢 BUY" : "🔴 SELL";
            string tVn = s.Time.AddMinutes(barMinutes).AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            var sb = new StringBuilder();
            sb.Append(icon).Append(" · ").Append(s.Setup).Append(' ').Append(SetupName(s.Setup))
              .Append(" · ").Append(symbol).Append(" · ").Append(tVn).Append(" VN\n");
            sb.Append("Lý do: ").Append(s.Reason).Append('\n');
            sb.Append("Vào ").Append(FmtPrice(s.Entry, digits))
              .Append(" · SL ").Append(FmtPrice(s.Sl, digits)).Append(" (").Append(Num(risk, "0.0")).Append(" giá)")
              .Append(" · TP ").Append(FmtPrice(s.Tp, digits)).Append(" (").Append(Num(rr, "0.#")).Append("R)");
            return Truncate(sb.ToString(), 1000);   // giới hạn caption ảnh Telegram = 1024
        }

        /// <summary>Tin ĐÓNG lệnh: "✅ A Phá hồi +3,0R · 20:24→20:51" hoặc "🛑 A Phá hồi −1,0R · ...".</summary>
        public static string ComposeClose(Signal s, int tzOffset, int barMinutes)
        {
            bool win = s.Outcome == "TP";
            string t0 = s.Time.AddMinutes(barMinutes).AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            string t1 = s.ExitTime.AddMinutes(barMinutes).AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            return $"{(win ? "✅" : "🛑")} {s.Setup} {SetupName(s.Setup)} {SignedR(s.R)} · {t0}→{t1}";
        }

        public static string Truncate(string s, int max) => s.Length <= max ? s : s.Substring(0, max - 1) + "…";

        public static string Sanitize(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s;
        }
    }

    // ---------------------------------------------------------------- niêm phong
    //  Mỗi nến đã đóng chỉ được dò tín hiệu MỘT LẦN trong đời; kết quả (có/không có tín hiệu) được niêm phong
    //  theo THỜI GIAN MỞ NẾN (không theo idx), sống qua reload. Khác SignalCache của OrderFlowBubbles ở chỗ:
    //  ngoài các dòng "sig" còn có dòng "rng" = khoảng thời gian [first,last] đã dò xong ⇒ nến trong khoảng mà
    //  KHÔNG có dòng sig = "đã dò, không có tín hiệu", không dò lại (dữ liệu per-level quá khứ do feed cấp lại
    //  có thể mỏng hơn lúc live → dò lại sẽ ra kết quả khác). `ver` khác LogicVersion ⇒ bỏ toàn bộ cache cũ.
    public sealed class SignalCache
    {
        private sealed class Line
        {
            public string K { get; set; }       // "sig" | "rng"
            public Signal S { get; set; }
            public string V { get; set; }
            public long F { get; set; }
            public long L { get; set; }
        }

        private readonly Dictionary<long, Signal> _byTime = new();
        private readonly object _fileLock = new();
        private long _first = long.MaxValue, _last = long.MinValue;
        public string FilePath { get; }
        public string Version { get; }

        public SignalCache(string filePath, string version = BenzoCore.LogicVersion) { FilePath = filePath; Version = version; }
        public int Count => _byTime.Count;
        public IEnumerable<Signal> All => _byTime.Values;
        public bool Covers(long timeTicks) => timeTicks >= _first && timeTicks <= _last;
        public bool TryGet(long timeTicks, out Signal s) => _byTime.TryGetValue(timeTicks, out s);

        public void Load()
        {
            _byTime.Clear(); _first = long.MaxValue; _last = long.MinValue;
            if (string.IsNullOrEmpty(FilePath) || !File.Exists(FilePath)) return;
            int rngLines = 0; bool dirty = false;
            foreach (var raw in File.ReadLines(FilePath))
            {
                if (string.IsNullOrWhiteSpace(raw)) continue;
                Line d;
                try { d = JsonSerializer.Deserialize<Line>(raw); } catch { dirty = true; continue; }   // dòng hỏng (ghi dở) → bỏ
                if (d == null) continue;
                if (d.K == "rng")
                {
                    rngLines++;
                    if (d.V != Version)
                    {   // logic đã đổi: mọi thứ trước đó là của logic cũ
                        _byTime.Clear(); _first = long.MaxValue; _last = long.MinValue; dirty = true; continue;
                    }
                    _first = Math.Min(_first, d.F); _last = Math.Max(_last, d.L);
                }
                else if (d.K == "sig" && d.S != null) _byTime[d.S.Time.Ticks] = d.S;
            }
            if (dirty || rngLines > 50) Compact();
        }

        private void Compact()
        {
            try
            {
                var sb = new StringBuilder();
                foreach (var s in _byTime.Values.OrderBy(x => x.Time))
                    sb.Append(JsonSerializer.Serialize(new Line { K = "sig", S = s })).Append('\n');
                if (_first <= _last)
                    sb.Append(JsonSerializer.Serialize(new Line { K = "rng", V = Version, F = _first, L = _last })).Append('\n');
                lock (_fileLock) File.WriteAllText(FilePath, sb.ToString());
            }
            catch { }
        }

        private void Append(Line l)
        {
            if (string.IsNullOrEmpty(FilePath)) return;
            string json = JsonSerializer.Serialize(l);
            lock (_fileLock)
            {
                string dir = Path.GetDirectoryName(FilePath);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                File.AppendAllText(FilePath, json + "\n");
            }
        }

        /// <summary>Niêm phong tín hiệu (ghi đè bản cũ cùng thời gian khi đọc lại: dòng sau thắng).</summary>
        public void PutSignal(Signal s)
        {
            _byTime[s.Time.Ticks] = s.Clone();
            Append(new Line { K = "sig", S = s });
        }

        /// <summary>Đánh dấu khoảng nến [first,last] đã dò xong.</summary>
        public void MarkRange(long firstTicks, long lastTicks)
        {
            if (firstTicks >= _first && lastTicks <= _last) return;
            _first = Math.Min(_first, firstTicks); _last = Math.Max(_last, lastTicks);
            Append(new Line { K = "rng", V = Version, F = _first, L = _last });
        }
    }

    // ---------------------------------------------------------------- engine
    /// <summary>
    /// Xử lý tuần tự nến ĐÃ ĐÓNG: cập nhật lệnh mở → (nếu không còn lệnh mở) dò setup theo thứ tự ưu tiên →
    /// niêm phong. 1 lệnh mở cùng lúc. Bars chỉ gồm nến đã đóng (indicator thêm tới Count−2).
    /// </summary>
    public sealed class BenzoEngine
    {
        public readonly string Symbol;
        public readonly double Tick;
        public int TzOffset = 7;
        public int BarMinutes = 1;
        public readonly List<BarData> Bars = new();
        public readonly List<Signal> Signals = new();
        public Signal Open;                                   // lệnh đang mở (hoặc null)
        public int Processed;                                 // số nến đã xử lý (= chỉ số nến kế tiếp cần xử lý)
        public readonly List<ISetupDetector> Detectors;       // theo thứ tự ƯU TIÊN (A > B > D > C)
        public Func<char, bool> IsEnabled = _ => true;
        public Func<DateTime, bool> IsNewsBlocked = _ => false;
        public Func<int, IReadOnlyList<LevelVol>> GetLevels = _ => Array.Empty<LevelVol>();
        private readonly SignalCache _cache;
        private readonly ClosedBars _view;
        private readonly SetupContext _ctx;
        public readonly BenzoZones Zones = new BenzoZones();

        public BenzoEngine(string symbol, double tick, SignalCache cache, IEnumerable<ISetupDetector> detectors)
        {
            Symbol = symbol; Tick = tick; _cache = cache;
            Detectors = detectors?.ToList() ?? new List<ISetupDetector>();
            _view = new ClosedBars(Bars);
            _ctx = new SetupContext { Symbol = symbol, Tick = tick, Bars = _view, Signals = Signals, Zones = Zones };
        }

        public sealed class AdvanceResult
        {
            public List<Signal> Opened = new();
            public List<Signal> Closed = new();
        }

        /// <summary>Xử lý mọi nến chưa xử lý tới closedIdx (gồm cả nó). Trả về lệnh vừa mở / vừa đóng trong lượt này.</summary>
        public AdvanceResult Advance(int closedIdx)
        {
            var res = new AdvanceResult();
            closedIdx = Math.Min(closedIdx, Bars.Count - 1);
            if (closedIdx < Processed) return res;
            _ctx.TzOffset = TzOffset; _ctx.BarMinutes = BarMinutes; Zones.TzOffset = TzOffset;
            _ctx.GetLevels = GetLevels; _ctx.IsNewsBlocked = IsNewsBlocked;
            long firstTicks = Bars[Processed].Time.Ticks;
            for (int i = Processed; i <= closedIdx; i++)
            {
                var bar = Bars[i];
                // 0) cập nhật vùng + cho mọi detector có trạng thái quan sát nến này (chỉ nhìn tới nến i)
                _view.Limit = i + 1;
                Zones.Push(i, bar, GetLevels(i));
                foreach (var d in Detectors) if (d is IObservingDetector od) od.Observe(_ctx, i);
                _view.Limit = Bars.Count;
                // 1) lệnh đang mở gặp nến này (nến SAU nến vào)
                if (Open != null && i > Open.BarIdx && BenzoCore.StepBar(Open, bar))
                {
                    res.Closed.Add(Open); Open = null;
                }
                // 2) không còn lệnh mở → dò
                if (Open != null) continue;
                Signal s = null;
                if (_cache != null && _cache.Covers(bar.Time.Ticks))
                {
                    if (_cache.TryGet(bar.Time.Ticks, out var sealedSig) && IsEnabled(sealedSig.Setup))
                    {
                        s = sealedSig.Clone();
                        s.Outcome = "OPEN"; s.ExitTime = DateTime.MinValue; s.R = 0;   // kết quả luôn tính lại từ nến, không tin file
                    }
                }
                else
                {
                    _view.Limit = i + 1;
                    bool virtualOpen = BenzoCore.InVirtualOpen(Zones.Sm);   // luật chung: không phát tín hiệu trong 19:20-20:30 (giờ neo Mỹ)
                    foreach (var d in Detectors)
                    {
                        if (virtualOpen) break;
                        if (!IsEnabled(d.Setup)) continue;
                        s = d.TryDetect(_ctx, i);
                        if (s != null) { s.Setup = d.Setup; break; }
                    }
                    _view.Limit = Bars.Count;
                    if (s != null)
                    {
                        BenzoCore.Finalize(s, Symbol, bar.Time);
                        _cache?.PutSignal(s);
                    }
                }
                if (s != null)
                {
                    s.BarIdx = i;
                    Signals.Add(s); Open = s; res.Opened.Add(s);
                }
            }
            Processed = closedIdx + 1;
            _view.Limit = Bars.Count;
            _cache?.MarkRange(firstTicks, Bars[closedIdx].Time.Ticks);
            return res;
        }
    }

#if DEBUG
    /// <summary>CHỈ biên dịch bản DEBUG để thử đường ống (vẽ, Telegram, CSV): cứ mỗi 30 nến đóng bắn 1 BUY giả
    /// (SL 2 giá, TP 4 giá = 2R). KHÔNG có trong bản ship (Release).</summary>
    public sealed class DemoDetector : ISetupDetector
    {
        public char Setup => 'A';
        public int Every = 30;
        public Signal TryDetect(SetupContext ctx, int closedIdx)
        {
            if (closedIdx < Every || closedIdx % Every != 0) return null;
            var b = ctx.Bars[closedIdx];
            return new Signal
            {
                Setup = 'A', Side = 1, Entry = b.C, Sl = b.C - 2, Tp = b.C + 4,
                Reason = "[DEMO] tín hiệu giả để thử đường ống", Zone = "demo"
            };
        }
    }
#endif

    // ---------------------------------------------------------------- CSV log
    public static class SignalCsv
    {
        public const string Header = "time_utc,setup,side,entry,sl,tp,zone,reason,outcome,exit_time,r";
        private static string Q(string s)
        {
            s = (s ?? "").Replace("\r", " ").Replace("\n", " ");
            return s.IndexOfAny(new[] { ',', '"' }) >= 0 ? "\"" + s.Replace("\"", "\"\"") + "\"" : s;
        }
        private static string D(double v) => v.ToString("0.0###", CultureInfo.InvariantCulture);

        public static string Key(Signal s) => $"{s.Time:yyyy-MM-dd HH:mm:ss},{s.Setup},{(s.Side > 0 ? "BUY" : "SELL")}";

        public static string ToLine(Signal s)
        {
            string exit = s.IsClosed ? s.ExitTime.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture) : "";
            return $"{Key(s)},{D(s.Entry)},{D(s.Sl)},{D(s.Tp)},{Q(s.Zone)},{Q(s.Reason)},{s.Outcome},{exit},{(s.IsClosed ? D(s.R) : "")}";
        }

        /// <summary>Trộn: dòng sẵn có trong file giữ lại (nếu không bị ghi đè), tín hiệu trong bộ nhớ ghi đè theo khoá. Ghi nguyên tử.</summary>
        public static void Merge(string path, IEnumerable<Signal> sigs)
        {
            if (string.IsNullOrEmpty(path)) return;
            var rows = new SortedDictionary<string, string>(StringComparer.Ordinal);
            if (File.Exists(path))
            {
                bool first = true;
                foreach (var l in File.ReadLines(path))
                {
                    if (first) { first = false; continue; }
                    if (string.IsNullOrWhiteSpace(l)) continue;
                    int c1 = l.IndexOf(','); if (c1 < 0) continue;
                    int c2 = l.IndexOf(',', c1 + 1); if (c2 < 0) continue;
                    int c3 = l.IndexOf(',', c2 + 1); if (c3 < 0) continue;
                    rows[l.Substring(0, c3)] = l;
                }
            }
            foreach (var s in sigs) rows[Key(s)] = ToLine(s);
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var sb = new StringBuilder(Header).Append('\n');
            foreach (var l in rows.Values) sb.Append(l).Append('\n');
            string tmp = path + ".tmp";
            File.WriteAllText(tmp, sb.ToString(), new UTF8Encoding(false));
            if (File.Exists(path)) File.Delete(path);
            File.Move(tmp, path);
        }
    }

    // ---------------------------------------------------------------- log + Telegram
    public static class BenzoLog
    {
        private static readonly object Gate = new();
        public static void Write(string path, string text)
        {
            try
            {
                lock (Gate)
                {
                    string dir = Path.GetDirectoryName(path);
                    if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                    File.AppendAllText(path, $"{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}Z {text}\n");
                }
            }
            catch { }
        }
    }

    public sealed class TeleClient
    {
        private static readonly HttpClient Http = new HttpClient { Timeout = Timeout.InfiniteTimeSpan };   // thời hạn do CancellationToken
        public string Token = "", ChatId = "", LogPath = "";
        public string LastError = "";

        public bool Ready => !string.IsNullOrWhiteSpace(Token) && !string.IsNullOrWhiteSpace(ChatId);

        /// <summary>Xoá token khỏi chuỗi lỗi (URL của HttpClient chứa token) trước khi ghi log.</summary>
        public string Redact(string s) =>
            string.IsNullOrEmpty(Token) || string.IsNullOrEmpty(s) ? s : s.Replace(Token.Trim(), "***");

        public static MultipartFormDataContent BuildPhoto(string chatId, byte[] png, string caption)
        {
            var mp = new MultipartFormDataContent();
            mp.Add(new StringContent(chatId, Encoding.UTF8), "chat_id");
            mp.Add(new StringContent(BenzoCore.Truncate(caption ?? "", 1024), Encoding.UTF8), "caption");
            var img = new ByteArrayContent(png);
            img.Headers.ContentType = new MediaTypeHeaderValue("image/png");
            mp.Add(img, "photo", "benzo.png");
            return mp;
        }

        public async Task<bool> SendMessageAsync(string text, CancellationToken ct)
        {
            if (!Ready) { LastError = "thiếu bot token / chat id"; return false; }
            try
            {
                var form = new FormUrlEncodedContent(new[]
                {
                    new KeyValuePair<string, string>("chat_id", ChatId.Trim()),
                    new KeyValuePair<string, string>("text", text),
                });
                using var resp = await Http.PostAsync($"https://api.telegram.org/bot{Token.Trim()}/sendMessage", form, ct).ConfigureAwait(false);
                return await Finish(resp, "sendMessage").ConfigureAwait(false);
            }
            catch (Exception ex) { return Fail("sendMessage", ex); }
        }

        public async Task<bool> SendPhotoAsync(byte[] png, string caption, CancellationToken ct)
        {
            if (!Ready) { LastError = "thiếu bot token / chat id"; return false; }
            try
            {
                using var mp = BuildPhoto(ChatId.Trim(), png, caption);
                using var resp = await Http.PostAsync($"https://api.telegram.org/bot{Token.Trim()}/sendPhoto", mp, ct).ConfigureAwait(false);
                return await Finish(resp, "sendPhoto").ConfigureAwait(false);
            }
            catch (Exception ex) { return Fail("sendPhoto", ex); }
        }

        private async Task<bool> Finish(HttpResponseMessage resp, string what)
        {
            string body = await resp.Content.ReadAsStringAsync().ConfigureAwait(false);
            if (resp.IsSuccessStatusCode) { LastError = ""; Log($"{what} OK"); return true; }
            LastError = $"{what} HTTP {(int)resp.StatusCode}";
            Log($"{what} LỖI HTTP {(int)resp.StatusCode}: {BenzoCore.Truncate(Redact(body), 300)}");
            return false;
        }
        private bool Fail(string what, Exception ex)
        {
            LastError = $"{what}: {(ex is OperationCanceledException ? "quá thời hạn" : ex.GetType().Name)}";
            Log($"{what} LỖI: {Redact(ex.Message)}");
            return false;
        }
        public void Log(string t) { if (!string.IsNullOrEmpty(LogPath)) BenzoLog.Write(LogPath, t); }
    }
}
