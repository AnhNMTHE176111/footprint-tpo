// ============================================================================
//  BenzoCore — LOGIC THUẦN của Benzo Trader (không tham chiếu Quantower SDK)
// ============================================================================
//  Tách riêng khỏi lớp Indicator để unit test được (benzo-trader/tests biên dịch chính file này).
//  Gồm: Signal, BarData, ISetupDetector + SetupContext, mô phỏng kết quả lệnh (StepBar/Simulate, MFE/MAE),
//  thống kê theo thế A/B, nhãn trung thực (plan BENZO-CORVEN 10.3), niêm phong tín hiệu
//  (SignalCache + guard khớp nến), engine xử lý nến đã đóng (BenzoEngine: 1 lệnh mở, huỷ lệnh ở nến cuối phiên,
//  đóng TIME qua khoảng trống > 30′), caption Telegram, CSV lệnh + CSV ứng viên bị loại, client Telegram.
//  GĐ3 (2026-11-09): chỉ còn MỘT setup — CORVEN (BenzoCorven.cs); 4 setup A/B/C/D cũ đã xoá (git giữ lịch sử).
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
    /// <summary>Một lệnh CORVEN. Setup = thế 'A' (fail break) / 'B' (phá giữ được). Side +1 = buy, −1 = sell.
    /// Time = THỜI GIAN MỞ của nến vào (nến xác nhận CF, UTC).</summary>
    public sealed class Signal
    {
        public string Id { get; set; } = "";
        public DateTime Time { get; set; }
        public char Setup { get; set; }
        public int Side { get; set; }
        public double Entry { get; set; }
        public double Sl { get; set; }
        public double Tp { get; set; }
        public string Reason { get; set; } = "";          // dấu hiệu nối " · " (caption)
        public string Zone { get; set; } = "";            // mốc dùng đặt SL: "canh" | "stacked lo–hi"
        public string Outcome { get; set; } = "OPEN";     // OPEN | TP | SL | TIME
        public DateTime ExitTime { get; set; }            // thời gian MỞ của nến thoát (UTC); MinValue khi còn mở
        public double R { get; set; }                     // R thực (đã trừ chi phí) khi đã đóng; 0 khi còn mở
        // ---- CORVEN (plan 10.4) ----
        public string Signs { get; set; } = "";           // = cột dau_hieu Python: "Δ: … (nến N) | bóng: …"
        public int NSigns { get; set; }
        public string SignTypes { get; set; } = "";       // "Δ+bóng"
        public string Short { get; set; } = "";           // nhãn chart "Fail Break sell · Δ ngược + bóng đỏ 18"
        public double RangeLo { get; set; }
        public double RangeHi { get; set; }
        public double Edge { get; set; }                  // cạnh range của thế (A: cạnh fail break; B: cạnh vừa phá)
        public int RangeId { get; set; }
        public bool BFromExhausted { get; set; }
        public double RAvail { get; set; }
        public double CfH { get; set; }                   // guard cache: H/L nến CF lúc niêm phong
        public double CfL { get; set; }
        public double CfBody { get; set; }
        public string Phien { get; set; } = "";           // Á / Âu / Mỹ theo neo Mỹ
        public string InstKey { get; set; } = "";         // khoá 4d (1 lệnh/thế)
        public string LockKey { get; set; } = "";         // khoá 4d (1 lệnh/(range, cạnh, thế))
        public long RangeT0 { get; set; }                 // ticks UTC: giờ mở nến bắt đầu range (0 = dòng cache cũ ⇒ không vẽ hộp)
        public long RangeT1 { get; set; }                 // ticks UTC: giờ mở nến CF
        public double MfeR { get; set; }                  // chạy xa nhất thuận chiều (R) từ vào tới đóng
        public double MaeR { get; set; }                  // chạy xa nhất ngược chiều (R)
        [JsonIgnore] public int BarIdx { get; set; } = -1; // chỉ số nến vào trong engine (không lưu file)

        public double Risk => Math.Abs(Entry - Sl);
        public double Reward => Math.Abs(Tp - Entry);
        public bool IsClosed => Outcome == "TP" || Outcome == "SL" || Outcome == "TIME";
        public Signal Clone() => (Signal)MemberwiseClone();
    }

    /// <summary>Nến M1 đã đóng. Time = thời gian MỞ nến (UTC).</summary>
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
        public IReadOnlyList<Signal> Signals;     // mọi tín hiệu đã mở TRƯỚC nến này
        public Func<int, IReadOnlyList<LevelVol>> GetLevels = _ => Array.Empty<LevelVol>(); // footprint từng mức giá của nến idx
        public Func<DateTime, bool> IsNewsBlocked = _ => false;  // utc → trong ±15' tin USD mức cao
        public BenzoZones Zones;                  // tách phiên / giờ neo Mỹ — engine đẩy mỗi nến đóng TRƯỚC khi gọi detector
        public DateTime ToVn(DateTime utc) => utc.AddHours(TzOffset);
    }

    /// <summary>Bộ dò một setup. TryDetect chạy MỘT lần cho mỗi nến đã đóng (chỉ khi KHÔNG có lệnh đang mở). Trả null nếu không có tín hiệu.
    /// Detector điền Setup, Side, Entry, Sl, Tp, Reason, Zone (+ trường CORVEN) — Time/Id/Outcome do engine gán.</summary>
    public interface ISetupDetector
    {
        char Setup { get; }
        Signal TryDetect(SetupContext ctx, int closedIdx);
    }

    /// <summary>Detector có trạng thái: engine gọi Observe cho MỌI nến đã đóng (kể cả khi đang có lệnh mở / setup tắt / nến đã niêm phong).</summary>
    public interface IObservingDetector : ISetupDetector
    {
        void Observe(SetupContext ctx, int closedIdx);
    }

    /// <summary>Detector giữ khoá "1 lệnh/thế": engine báo lệnh lấy từ cache (Taken) và lệnh bị huỷ (Cancelled).</summary>
    public interface ITakeAware
    {
        void NotifyTaken(Signal s);
        void NotifyCancelled(Signal s);
    }

    // ---------------------------------------------------------------- lõi tính toán
    public static class BenzoCore
    {
        /// <summary>Đổi số này mỗi khi logic detector đổi → cache niêm phong cũ bị bỏ.</summary>
        public const string LogicVersion = CorvenParams.LogicVersion;
        /// <summary>Chi phí mỗi lệnh (giá): spread + trượt, GC tick 0,1 (= kernel.CONST['cost']).</summary>
        public const double CostPrice = 0.2;
        public const int NewsBlockMinutes = 15;
        /// <summary>"Mở ảo": 19:20-20:30 VN theo mốc neo Mỹ (sm 860..929) — luật 4d của CORVEN (công tắc Settings).</summary>
        public static bool InVirtualOpen(int sm) => sm >= 860 && sm < 930;
        public const int TeleMaxAgeSec = 90;

        /// <summary>Khoá cache theo cấu hình ảnh hưởng tín hiệu: phiên bản logic + SL tối đa (giá) + 2 công tắc Fail Break / Break (đổi một trong ba ⇒ tính lại).</summary>
        public static string CacheVersion(double slMaxGia = CorvenParams.SlMaxGia, bool failBreak = true, bool brk = true, bool slKieuCu = false) =>
            LogicVersion + "-sl" + slMaxGia.ToString("0.0", CultureInfo.InvariantCulture) + "-f" + (failBreak ? 1 : 0) + "-b" + (brk ? 1 : 0) + "-old" + (slKieuCu ? 1 : 0);

        /// <summary>Tên file cache/CSV có KHUNG (plan 10.5): cache_&lt;sym&gt;_&lt;aggName&gt;_&lt;minutes&gt;m.jsonl.</summary>
        public static string CacheFileName(string symbol, string aggName, int minutes) =>
            $"cache_{Sanitize(symbol)}_{Sanitize(aggName)}_{minutes}m.jsonl";
        public static string SignalsCsvName(string symbol, int minutes) => $"signals_{Sanitize(symbol)}_{minutes}m_{LogicVersion}.csv";
        public static string CandidatesCsvName(string symbol, int minutes) => $"candidates_{Sanitize(symbol)}_{minutes}m_{LogicVersion}.csv";

        /// <summary>Chọn cửa sổ con chứa vùng chart: nhỏ nhất mà vẫn ≥ kích thước chart (trừ 2px), và không quá 2,5× diện tích chart.</summary>
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

        /// <summary>Tên HIỂN THỊ của setup (một chỗ duy nhất): A = "Fail Break", B = "Break". Mã nội bộ 'A'/'B' (cache, CSV, khoá) giữ nguyên.</summary>
        public static string TheName(char s) => s == 'A' ? "Fail Break" : s == 'B' ? "Break" : "?";
        /// <summary>Nhãn chart để vẽ: cache cũ lưu "A buy · …"/"B buy · …" ⇒ đổi tiền tố sang tên hiển thị hiện hành.</summary>
        public static string ShortDisplay(Signal s)
        {
            if (string.IsNullOrEmpty(s.Short)) return $"{TheName(s.Setup)} {(s.Side > 0 ? "buy" : "sell")}";
            if (s.Short.Length > 2 && (s.Short[0] == 'A' || s.Short[0] == 'B') && s.Short[1] == ' ') return TheName(s.Short[0]) + s.Short.Substring(1);
            return s.Short;
        }

        public static string MakeId(string symbol, DateTime barOpenUtc, char setup, int side) =>
            $"{symbol}|{barOpenUtc:yyyyMMddHHmm}|{setup}|{(side > 0 ? 'B' : 'S')}";

        /// <summary>Gán Time/Id/Outcome cho tín hiệu mới từ detector.</summary>
        public static void Finalize(Signal s, string symbol, DateTime barOpenUtc)
        {
            s.Time = barOpenUtc;
            s.Id = MakeId(symbol, barOpenUtc, s.Setup, s.Side);
            s.Outcome = "OPEN";
            s.ExitTime = DateTime.MinValue;
            s.R = 0; s.MfeR = 0; s.MaeR = 0;
        }

        // ---- mô phỏng (= kernel.simulate) ----
        /// <summary>Áp MỘT nến đã đóng lên lệnh đang mở. Chạm cả SL lẫn TP cùng nến ⇒ SL (bi quan). Trả true nếu lệnh đóng.
        /// R đã trừ chi phí: TP = (lời − chi phí)/rủi ro, SL = −(rủi ro + chi phí)/rủi ro. Cập nhật MFE/MAE (theo R) ở mọi nến xét.</summary>
        public static bool StepBar(Signal s, BarData b)
        {
            if (s.IsClosed) return true;
            double risk = s.Risk;
            if (risk <= 1e-9) risk = 1e-9;
            double fav = s.Side > 0 ? b.H - s.Entry : s.Entry - b.L;
            double adv = s.Side > 0 ? s.Entry - b.L : b.H - s.Entry;
            s.MfeR = Math.Max(s.MfeR, fav / risk);
            s.MaeR = Math.Max(s.MaeR, adv / risk);
            bool hitSl = s.Side > 0 ? b.L <= s.Sl : b.H >= s.Sl;
            bool hitTp = s.Side > 0 ? b.H >= s.Tp : b.L <= s.Tp;
            if (!hitSl && !hitTp) return false;
            if (hitSl) { s.Outcome = "SL"; s.R = (-risk - CostPrice) / risk; }
            else { s.Outcome = "TP"; s.R = (s.Reward - CostPrice) / risk; }
            s.ExitTime = b.Time;
            return true;
        }

        /// <summary>Đóng TIME tại giá đóng của nến cuối phiên (lệnh còn mở qua khoảng trống > 30′, plan 4d).</summary>
        public static void CloseTime(Signal s, BarData last)
        {
            if (s.IsClosed) return;
            double risk = Math.Max(1e-9, s.Risk);
            s.Outcome = "TIME";
            s.R = (s.Side * (last.C - s.Entry) - CostPrice) / risk;
            s.ExitTime = last.Time;
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
            public char Setup;              // 'A' | 'B' | '*' = tổng
            public int Wins, Losses, Open;
            public double SumR;
            public int N => Wins + Losses;  // số lệnh ĐÃ ĐÓNG (TIME: thắng nếu R > 0)
            public double WinRate => N > 0 ? 100.0 * Wins / N : 0;
        }

        public sealed class StatsResult
        {
            public SetupStat Total = new SetupStat { Setup = '*' };
            public SetupStat A = new SetupStat { Setup = 'A' };
            public SetupStat B = new SetupStat { Setup = 'B' };
        }

        /// <summary>Thống kê toàn bộ lệnh đang có (tính lại mỗi lần nạp dữ liệu).</summary>
        public static StatsResult ComputeStats(IEnumerable<Signal> sigs)
        {
            var r = new StatsResult();
            foreach (var s in sigs)
            {
                var by = s.Setup == 'A' ? r.A : s.Setup == 'B' ? r.B : null;
                foreach (var st in by == null ? new[] { r.Total } : new[] { by, r.Total })
                {
                    if (s.IsClosed) { if (s.R > 0) st.Wins++; else st.Losses++; st.SumR += s.R; }
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

        /// <summary>Bảng chart 4 dòng (plan 10.3) — dòng 4 LUÔN hiện:
        /// "BENZO CORVEN corven-7 · N lệnh · WR x % · ΣR" / "Fail Break · n · WR · ΣR" / "Break · n · WR · ΣR" / nhãn backtest.</summary>
        public static List<string> TableLines(StatsResult st, bool slKieuCu = false)
        {
            string open = st.Total.Open > 0 ? $" · {st.Total.Open} đang mở" : "";
            return new List<string>
            {
                $"BENZO CORVEN {LogicVersion} · {st.Total.N} lệnh · WR {Num(st.Total.WinRate, "0")} % · {SignedR(st.Total.SumR)}{open}",
                $"{TheName('A')} · {st.A.N} · WR {Num(st.A.WinRate, "0")} % · {SignedR(st.A.SumR)}",
                $"{TheName('B')} · {st.B.N} · WR {Num(st.B.WinRate, "0")} % · {SignedR(st.B.SumR)}",
                CorvenParams.Backtest(slKieuCu),
            };
        }

        // ---- Telegram caption ----
        public static string FmtPrice(double p, int digits) => Num(p, digits <= 0 ? "0" : "0." + new string('0', digits));

        /// <summary>Dòng mốc: "Mốc: cạnh dưới 4127,4 vừa phá (range 4127,3–4132,5)".</summary>
        public static string MocLine(Signal s, int digits)
        {
            string range = $"(range {FmtPrice(s.RangeLo, digits)}–{FmtPrice(s.RangeHi, digits)})";
            bool upper = Math.Abs(s.Edge - s.RangeHi) < Math.Abs(s.Edge - s.RangeLo);
            string edge = $"cạnh {(upper ? "trên" : "dưới")} {FmtPrice(s.Edge, digits)}";
            if (s.Setup == 'A') return $"Mốc: {edge} fail break {range}";
            if (!string.IsNullOrEmpty(s.Zone) && s.Zone.StartsWith("stacked"))
                return $"Mốc: vùng {s.Zone} trong cú phá {edge} {range}";
            return $"Mốc: {edge} vừa phá {range}";
        }

        /// <summary>Caption tin MỞ lệnh (plan mục 2 + 10.3): 4 dòng + cảnh báo chưa có lợi thế.</summary>
        public static string ComposeOpen(Signal s, string symbol, int tzOffset, int barMinutes, int digits, bool slKieuCu = false)
        {
            double risk = s.Risk;
            string icon = s.Side > 0 ? "🟢 BUY" : "🔴 SELL";
            // giờ MỞ nến CF (= time_vn CSV = t_vn Python = nhãn nến trên Quantower) — plan 12.1 #6; barMinutes giữ chữ ký cũ, không dùng
            string tVn = s.Time.AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            var sb = new StringBuilder();
            sb.Append(icon).Append(" · CORVEN ").Append(TheName(s.Setup)).Append(" · ").Append(symbol).Append(" · ").Append(tVn).Append(" VN\n");
            sb.Append(MocLine(s, digits)).Append('\n');
            sb.Append("Dấu hiệu (").Append(s.NSigns).Append("): ").Append(s.Reason).Append('\n');
            sb.Append("CF ").Append(tVn).Append(" thân ").Append(Num(s.CfBody, "0.0#")).Append(" giá · Vào ").Append(FmtPrice(s.Entry, digits))
              .Append(" · SL ").Append(FmtPrice(s.Sl, digits)).Append(" (").Append(Num(risk, "0.0")).Append(')')
              .Append(" · TP ").Append(FmtPrice(s.Tp, digits)).Append(" (2R, R sẵn ").Append(Num(s.RAvail, "0.0")).Append(")\n");
            sb.Append(CorvenParams.Warn(slKieuCu));
            return Truncate(sb.ToString(), 1000);   // giới hạn caption ảnh Telegram = 1024
        }

        /// <summary>Tin ĐÓNG lệnh: "✅ CORVEN Fail Break +1,9R · 20:24→20:51" (TIME ghi thêm "hết phiên").</summary>
        public static string ComposeClose(Signal s, int tzOffset, int barMinutes)
        {
            bool win = s.R > 0;
            string t0 = s.Time.AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            string t1 = s.ExitTime.AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            return $"{(win ? "✅" : "🛑")} CORVEN {TheName(s.Setup)} {SignedR(s.R)} · {t0}→{t1}" + (s.Outcome == "TIME" ? " (hết phiên)" : "");
        }

        /// <summary>Tin HUỶ: lệnh vào ở nến cuối phiên (không có nến nào để vào thật).</summary>
        public static string ComposeCancel(Signal s, int tzOffset, int barMinutes)
        {
            string t0 = s.Time.AddHours(tzOffset).ToString("HH:mm", CultureInfo.InvariantCulture);
            return $"⚪ CORVEN {TheName(s.Setup)} {t0} huỷ — nến xác nhận là nến cuối phiên";
        }

        /// <summary>x của nhãn lệnh (plan 12.1 #3): mặc định xE + 8; tràn mép phải ⇒ lật sang trái xE − 8 − w; vẫn lọt mép trái ⇒ kẹp clipLeft + 2.</summary>
        public static float LabelX(float xE, float w, float clipLeft, float clipRight)
        {
            float x = xE + 8;
            if (x + w > clipRight) x = xE - 8 - w;
            if (x < clipLeft) x = clipLeft + 2;
            return x;
        }

        public static string Truncate(string s, int max) => s.Length <= max ? s : s.Substring(0, max - 1) + "…";

        public static string Sanitize(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s;
        }
    }

    // ---------------------------------------------------------------- niêm phong
    //  Mỗi nến đã đóng chỉ được dò tín hiệu MỘT LẦN trong đời; kết quả (có/không có tín hiệu) được niêm phong theo THỜI GIAN
    //  MỞ NẾN, sống qua reload. Dòng "rng" = khoảng [first,last] đã dò xong ⇒ nến trong khoảng mà KHÔNG có dòng sig =
    //  "đã dò, không có tín hiệu". `ver` khác ⇒ bỏ toàn bộ cache cũ. Guard khớp nến (plan 10.5) do BenzoEngine kiểm.
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
        /// <summary>Các khoảng [F,L] đã dò xong (rời nhau, sắp tăng). Nhiều khoảng vì nến lúc setup TẮT không được niêm phong (plan 12.1 #2).</summary>
        private readonly List<(long F, long L)> _iv = new();
        public string FilePath { get; }
        public string Version { get; }

        public SignalCache(string filePath, string version = BenzoCore.LogicVersion) { FilePath = filePath; Version = version; }
        public int Count => _byTime.Count;
        public IEnumerable<Signal> All => _byTime.Values;
        public bool Covers(long timeTicks) { foreach (var x in _iv) if (timeTicks >= x.F && timeTicks <= x.L) return true; return false; }
        public IReadOnlyList<(long F, long L)> Intervals => _iv;

        /// <summary>Thêm khoảng [f,l], gộp với mọi khoảng chồng lên nó. Trả khoảng sau gộp.</summary>
        private (long F, long L) AddInterval(long f, long l)
        {
            for (int k = _iv.Count - 1; k >= 0; k--)
                if (_iv[k].F <= l && f <= _iv[k].L) { f = Math.Min(f, _iv[k].F); l = Math.Max(l, _iv[k].L); _iv.RemoveAt(k); }
            int pos = 0; while (pos < _iv.Count && _iv[pos].F < f) pos++;
            _iv.Insert(pos, (f, l));
            return (f, l);
        }
        public bool TryGet(long timeTicks, out Signal s) => _byTime.TryGetValue(timeTicks, out s);

        public void Load()
        {
            _byTime.Clear(); _iv.Clear();
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
                        _byTime.Clear(); _iv.Clear(); dirty = true; continue;
                    }
                    AddInterval(d.F, d.L);
                }
                else if (d.K == "sig" && d.S != null) _byTime[d.S.Time.Ticks] = d.S;
            }
            if (dirty || rngLines > 50) Compact();
        }

        /// <summary>Bỏ TOÀN BỘ cache (guard khớp nến trượt): xoá file, quên mọi khoảng đã dò.</summary>
        public void Reset()
        {
            _byTime.Clear(); _iv.Clear();
            try { lock (_fileLock) if (!string.IsNullOrEmpty(FilePath) && File.Exists(FilePath)) File.Delete(FilePath); } catch { }
        }

        private void Compact()
        {
            try
            {
                var sb = new StringBuilder();
                foreach (var s in _byTime.Values.OrderBy(x => x.Time))
                    sb.Append(JsonSerializer.Serialize(new Line { K = "sig", S = s })).Append('\n');
                foreach (var x in _iv)
                    sb.Append(JsonSerializer.Serialize(new Line { K = "rng", V = Version, F = x.F, L = x.L })).Append('\n');
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

        /// <summary>Niêm phong tín hiệu (dòng sau thắng khi đọc lại).</summary>
        public void PutSignal(Signal s)
        {
            _byTime[s.Time.Ticks] = s.Clone();
            Append(new Line { K = "sig", S = s });
        }

        /// <summary>Đánh dấu khoảng nến [first,last] đã dò xong.</summary>
        public void MarkRange(long firstTicks, long lastTicks)
        {
            foreach (var x in _iv) if (firstTicks >= x.F && lastTicks <= x.L) return;
            var m = AddInterval(firstTicks, lastTicks);
            Append(new Line { K = "rng", V = Version, F = m.F, L = m.L });
        }

        /// <summary>Guard (plan 10.5): tín hiệu niêm phong có thuộc ĐÚNG nến này không — giá vào lệch > nửa tick so với close,
        /// hoặc H/L lệch > 1 tick ⇒ không khớp (cache của khung/lịch sử khác) ⇒ phải bỏ toàn bộ cache.</summary>
        public static bool FitsBar(Signal s, BarData b, double tick) =>
            Math.Abs(s.Entry - b.C) <= tick / 2 + 1e-9 && Math.Abs(s.CfH - b.H) <= tick + 1e-9 && Math.Abs(s.CfL - b.L) <= tick + 1e-9;
    }

    // ---------------------------------------------------------------- engine
    /// <summary>
    /// Xử lý tuần tự nến ĐÃ ĐÓNG: cho detector quan sát → (phiên mới) đóng TIME / huỷ lệnh nến cuối phiên → cập nhật lệnh mở →
    /// (nếu không còn lệnh mở) dò → niêm phong. 1 lệnh mở cùng lúc. Bars chỉ gồm nến đã đóng.
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
        public readonly List<ISetupDetector> Detectors;
        public Func<char, bool> IsEnabled = _ => true;
        public Func<DateTime, bool> IsNewsBlocked = _ => false;
        public Func<int, IReadOnlyList<LevelVol>> GetLevels = _ => Array.Empty<LevelVol>();
        private readonly SignalCache _cache;
        private readonly ClosedBars _view;
        private readonly SetupContext _ctx;
        public readonly BenzoZones Zones = new BenzoZones();
        private long? _segStart;      // đầu đoạn nến liên tiếp đang BẬT (để niêm phong); nến lúc TẮT ngắt đoạn — plan 12.1 #2
        private long _segLast;

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
            public List<Signal> Cancelled = new();
            /// <summary>Guard cache trượt: engine DỪNG; người gọi phải bỏ cache và dựng lại engine từ đầu.</summary>
            public bool CacheInvalid;
            public string CacheWhy = "";
        }

        /// <summary>Kết thúc phiên tại nến last: lệnh vào ĐÚNG nến last bị huỷ (Python: nến cuối phiên không vào), lệnh khác đóng TIME.</summary>
        private void EndSession(int last, AdvanceResult res)
        {
            if (Open == null) return;
            if (Open.BarIdx >= last)
            {
                Signals.Remove(Open);
                foreach (var d in Detectors) if (d is ITakeAware ta) ta.NotifyCancelled(Open);
                res.Cancelled.Add(Open);
            }
            else
            {
                BenzoCore.CloseTime(Open, Bars[last]);
                res.Closed.Add(Open);
            }
            Open = null;
        }

        /// <summary>Hết dữ liệu (chỉ dùng khi chạy lại file — ReplayCorven/test): coi nến cuối là nến cuối phiên.</summary>
        public AdvanceResult FinishSession()
        {
            var res = new AdvanceResult();
            if (Processed > 0) EndSession(Processed - 1, res);
            return res;
        }

        /// <summary>Xử lý mọi nến chưa xử lý tới closedIdx (gồm cả nó). Trả về lệnh vừa mở / đóng / huỷ trong lượt này.</summary>
        public AdvanceResult Advance(int closedIdx)
        {
            var res = new AdvanceResult();
            closedIdx = Math.Min(closedIdx, Bars.Count - 1);
            if (closedIdx < Processed) return res;
            _ctx.TzOffset = TzOffset; _ctx.BarMinutes = BarMinutes; Zones.TzOffset = TzOffset;
            _ctx.GetLevels = GetLevels; _ctx.IsNewsBlocked = IsNewsBlocked;
            for (int i = Processed; i <= closedIdx; i++)
            {
                var bar = Bars[i];
                bool enabled = Detectors.Any(d => IsEnabled(d.Setup));
                // 0) phiên + detector quan sát nến này (chỉ nhìn tới nến i)
                _view.Limit = i + 1;
                Zones.Push(i, bar);
                foreach (var d in Detectors) if (d is IObservingDetector od) od.Observe(_ctx, i);
                _view.Limit = Bars.Count;
                // 1) phiên mới: lệnh còn mở qua khoảng trống > 30′
                if (Zones.NewSession && i > 0) EndSession(i - 1, res);
                // 2) lệnh đang mở gặp nến này (nến SAU nến vào)
                if (Open != null && i > Open.BarIdx && BenzoCore.StepBar(Open, bar)) { res.Closed.Add(Open); Open = null; }
                // 3) không còn lệnh mở → dò
                if (enabled) { _segStart ??= bar.Time.Ticks; _segLast = bar.Time.Ticks; }
                else if (_segStart.HasValue) { _cache?.MarkRange(_segStart.Value, _segLast); _segStart = null; }   // TẮT: không niêm phong nến này
                if (Open != null) { Processed = i + 1; continue; }
                Signal s = null;
                if (_cache != null && _cache.Covers(bar.Time.Ticks))
                {
                    if (_cache.TryGet(bar.Time.Ticks, out var sealedSig))
                    {
                        if (!SignalCache.FitsBar(sealedSig, bar, Tick))
                        {
                            res.CacheInvalid = true;
                            res.CacheWhy = $"cache lệch nến {bar.Time:yyyy-MM-dd HH:mm}: vào {sealedSig.Entry} / H {sealedSig.CfH} / L {sealedSig.CfL} so với nến C {bar.C} H {bar.H} L {bar.L}";
                            Processed = i;
                            return res;
                        }
                        // lệnh đã niêm phong luôn được lấy lại, BẤT KỂ công tắc (tắt chỉ chặn dò mới — không xoá lịch sử, plan 12.1 #2)
                        s = sealedSig.Clone();
                        s.Outcome = "OPEN"; s.ExitTime = DateTime.MinValue; s.R = 0; s.MfeR = 0; s.MaeR = 0;   // kết quả luôn tính lại từ nến
                        foreach (var d in Detectors) if (d is ITakeAware ta) ta.NotifyTaken(s);
                    }
                }
                else if (enabled)
                {
                    _view.Limit = i + 1;
                    foreach (var d in Detectors)
                    {
                        if (!IsEnabled(d.Setup)) continue;
                        s = d.TryDetect(_ctx, i);
                        if (s != null) break;
                    }
                    _view.Limit = Bars.Count;
                    if (s != null)
                    {
                        BenzoCore.Finalize(s, Symbol, bar.Time);
                        s.Phien = BenzoKernel.PhienVn(Zones.Sm);
                        _cache?.PutSignal(s);
                    }
                }
                if (s != null)
                {
                    s.BarIdx = i;
                    Signals.Add(s); Open = s; res.Opened.Add(s);
                }
                Processed = i + 1;
            }
            Processed = closedIdx + 1;
            _view.Limit = Bars.Count;
            if (_segStart.HasValue) _cache?.MarkRange(_segStart.Value, _segLast);
            return res;
        }
    }

    // ---------------------------------------------------------------- CSV log
    public static class SignalCsv
    {
        public const string Header = "time_utc,time_vn,the,side,range_lo,range_hi,b_from_exhausted,moc,n_signs,signs,entry,sl,tp,risk,r_avail,outcome,exit_time,r,mfe_r,mae_r,phien";
        public const string CandHeader = "time_utc,the,side,moc,gate,detail";
        public static string Q(string s)
        {
            s = (s ?? "").Replace("\r", " ").Replace("\n", " ");
            return s.IndexOfAny(new[] { ',', '"' }) >= 0 ? "\"" + s.Replace("\"", "\"\"") + "\"" : s;
        }
        private static string D(double v) => v.ToString("0.0###", CultureInfo.InvariantCulture);

        public static string Key(Signal s, int tz) => $"{s.Time:yyyy-MM-dd HH:mm},{s.Time.AddHours(tz):yyyy-MM-dd HH:mm},{s.Setup}";

        public static string ToLine(Signal s, int tz)
        {
            string exit = s.IsClosed ? s.ExitTime.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) : "";
            string side = s.Side > 0 ? "buy" : "sell";
            string moc = s.Zone == "canh" ? "canh" : s.Zone;
            return string.Join(",", Key(s, tz), side, D(s.RangeLo), D(s.RangeHi), s.BFromExhausted ? "1" : "0", Q(moc), s.NSigns.ToString(CultureInfo.InvariantCulture),
                Q(s.Signs), D(s.Entry), D(s.Sl), D(s.Tp), D(s.Risk), s.RAvail.ToString("0.00", CultureInfo.InvariantCulture), s.Outcome, exit,
                s.IsClosed ? s.R.ToString("0.000", CultureInfo.InvariantCulture) : "", s.MfeR.ToString("0.00", CultureInfo.InvariantCulture),
                s.MaeR.ToString("0.00", CultureInfo.InvariantCulture), s.Phien);
        }

        /// <summary>Trộn: dòng sẵn có trong file giữ lại (nếu không bị ghi đè), tín hiệu trong bộ nhớ ghi đè theo khoá. Ghi nguyên tử.</summary>
        public static void Merge(string path, IEnumerable<Signal> sigs, int tz = 7, IEnumerable<Signal> removed = null)
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
            if (removed != null) foreach (var s in removed) rows.Remove(Key(s, tz));
            foreach (var s in sigs) rows[Key(s, tz)] = ToLine(s, tz);
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            var sb = new StringBuilder(Header).Append('\n');
            foreach (var l in rows.Values) sb.Append(l).Append('\n');
            string tmp = path + ".tmp";
            File.WriteAllText(tmp, sb.ToString(), new UTF8Encoding(false));
            if (File.Exists(path)) File.Delete(path);
            File.Move(tmp, path);
        }

        /// <summary>Ghi thêm 1 dòng CSV ứng viên bị loại (chỉ live, plan 10.4).</summary>
        public static void AppendCandidate(string path, DateTime utc, char the, int side, string moc, string gate, string detail)
        {
            if (string.IsNullOrEmpty(path)) return;
            string dir = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
            bool head = !File.Exists(path);
            var line = string.Join(",", utc.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture), the.ToString(), side > 0 ? "buy" : "sell", Q(moc), Q(gate), Q(detail));
            File.AppendAllText(path, (head ? CandHeader + "\n" : "") + line + "\n", new UTF8Encoding(false));
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
