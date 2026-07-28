// ============================================================================
//  FootprintCore.cs — LÕI THUẦN của Footprint Export (KHÔNG phụ thuộc Quantower)
// ============================================================================
//  Mọi thứ dễ sai (làm tròn giá, gộp tick/hàng, POC, dọn giá trị "mồi" của
//  MaxDelta/MinDelta, escape CSV, đặt tên file, lọc ngày) nằm ở đây — không
//  tham chiếu TradingPlatform.* nên BUILD + CHẠY TEST được ngay trên Linux
//  (xem tests/). Phần indicator (FootprintExport.cs) chỉ còn việc lấy dữ liệu
//  từ platform rồi gọi xuống đây.
//
//  QUY ƯỚC TÊN (bám thuật ngữ order flow, không bám tên API):
//    bid_vol = VolumeAnalysisItem.SellVolume  → khớp ở BID = BÁN chủ động
//    ask_vol = VolumeAnalysisItem.BuyVolume   → khớp ở ASK = MUA chủ động
//    delta   = ask_vol − bid_vol (lấy nguyên số của platform, không tự tính lại)
// ============================================================================

namespace FootprintExport
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.IO;
    using System.Text;

    /// <summary>Một MỨC GIÁ trong footprint của một nến (dữ liệu thuần).</summary>
    internal struct FpLevel
    {
        public long Tick;           // chỉ số tick = round(price / tickSize) — tránh so sánh double
        public double BidVol;       // bán chủ động (khớp ở BID)
        public double AskVol;       // mua chủ động (khớp ở ASK)
        public double Volume;
        public double Delta;
        public int Trades;
        public int BuyTrades;
        public int SellTrades;
        public double MaxOneTrade;  // lệnh ĐƠN lớn nhất tại mức giá đó
    }

    /// <summary>Tổng hợp mức NẾN (cho file phụ *_bars.csv).</summary>
    internal struct FpBar
    {
        public int Idx;
        public string Dt;
        public double Open, High, Low, Close, BarVolume;
        public long BarTicks;
        public double BidVol, AskVol, Volume, Delta, DeltaFinish, MaxDelta, MinDelta, CumDelta;
        public int Trades, BuyTrades, SellTrades;
        public double MaxOneTrade, AvgSize, AvgBuySize, AvgSellSize;
        public int Levels;
        public double PocPrice, PocVolume, OpenInterest;
    }

    internal static class FpCore
    {
        private static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

        // Giá trị "mồi" của MaxDelta/MinDelta ở nến rỗng là double.MinValue/MaxValue
        // (đã gặp thật ở AskBidDeltaBars). Nếu để lọt sẽ ra ±1.8e308 trong CSV.
        private const double PrimerGuard = 1e12;

        public const int MaxRowsHardCap = 25_000_000;   // trần an toàn, KHÔNG cắt âm thầm — báo rõ ở status/log

        // ---------------------------------------------------------------- giá
        /// <summary>Số chữ số thập phân suy ra từ tick size (0.1 → 1; 0.25 → 2; 1 → 0).</summary>
        public static int DigitsFromTick(double tick)
        {
            if (!(tick > 0) || !double.IsFinite(tick)) return 2;
            int d = 0;
            double t = tick;
            while (d < 10 && Math.Abs(t - Math.Round(t)) > 1e-10) { t *= 10; d++; }
            return d;
        }

        public static long ToTick(double price, double tick)
            => (tick > 0 && double.IsFinite(tick)) ? (long)Math.Round(price / tick, MidpointRounding.AwayFromZero) : 0L;

        public static double PriceOf(long tickIdx, double tick) => tickIdx * tick;

        /// <summary>Gộp về đáy nhóm (floor-division, đúng cả với tick âm).</summary>
        public static long Bucket(long tickIdx, int ticksPerRow)
        {
            if (ticksPerRow <= 1) return tickIdx;
            long q = tickIdx / ticksPerRow;
            if (tickIdx % ticksPerRow != 0 && tickIdx < 0) q--;
            return q * ticksPerRow;
        }

        /// <summary>Format giá KHÔNG mất thông tin: nếu làm tròn theo tick bị lệch → in đủ chữ số.</summary>
        public static string FmtPrice(double price, int digits)
        {
            if (!double.IsFinite(price)) return "";
            int d = Math.Max(0, Math.Min(digits, 15));
            double r = Math.Round(price, d, MidpointRounding.AwayFromZero);
            if (Math.Abs(price - r) > 1e-9) return price.ToString("0.##########", Inv);
            return r.ToString("F" + d.ToString(Inv), Inv);
        }

        /// <summary>Số lượng: in nguyên nếu là số nguyên (đỡ rác ".0"), không thì tối đa 8 chữ số.</summary>
        public static string FmtVol(double v)
        {
            if (!double.IsFinite(v)) return "0";
            if (Math.Abs(v) < 1e15 && v == Math.Floor(v)) return ((long)v).ToString(Inv);
            return v.ToString("0.########", Inv);
        }

        /// <summary>Dọn giá trị mồi (±1.8e308 / NaN) về fallback.</summary>
        public static double FixPrimer(double v, double fallback)
            => (double.IsFinite(v) && Math.Abs(v) < PrimerGuard) ? v : fallback;

        // ------------------------------------------------------------ gộp mức
        private static int CmpTick(FpLevel a, FpLevel b) => a.Tick.CompareTo(b.Tick);

        /// <summary>
        /// Gộp footprint theo N tick/hàng. Trả về danh sách SẮP TĂNG theo giá, MỖI GIÁ ĐÚNG 1 HÀNG.
        /// LƯU Ý: gộp cả khi ticksPerRow = 1. Không phải dư — PriceLevels khoá theo double, nếu feed
        /// báo giá mịn hơn TickSize (hoặc TickSize suy ra bị to hơn thật) thì 2 giá khác nhau có thể
        /// rơi vào cùng tick index; bỏ bước gộp sẽ sinh 2 dòng trùng (bar_idx, price) trong CSV
        /// → pivot/group-by phía Python sai. Test random đã bắt đúng ca này.
        /// </summary>
        public static List<FpLevel> Aggregate(List<FpLevel> raw, int ticksPerRow)
        {
            if (raw == null || raw.Count == 0) return new List<FpLevel>();
            var map = new Dictionary<long, FpLevel>(raw.Count);
            foreach (var lv in raw)
            {
                long b = Bucket(lv.Tick, ticksPerRow);
                if (map.TryGetValue(b, out var acc))
                {
                    acc.BidVol += lv.BidVol;
                    acc.AskVol += lv.AskVol;
                    acc.Volume += lv.Volume;
                    acc.Delta += lv.Delta;
                    acc.Trades += lv.Trades;
                    acc.BuyTrades += lv.BuyTrades;
                    acc.SellTrades += lv.SellTrades;
                    acc.MaxOneTrade = Math.Max(acc.MaxOneTrade, lv.MaxOneTrade);
                    map[b] = acc;
                }
                else
                {
                    var n = lv;
                    n.Tick = b;
                    map[b] = n;
                }
            }
            var res = new List<FpLevel>(map.Values);
            res.Sort(CmpTick);
            return res;
        }

        /// <summary>Chỉ số POC (volume lớn nhất). Bằng nhau → mức GIÁ THẤP hơn (list đã sắp tăng). -1 nếu rỗng.</summary>
        public static int PocIndex(List<FpLevel> levels)
        {
            if (levels == null || levels.Count == 0) return -1;
            int best = 0;
            for (int i = 1; i < levels.Count; i++)
                if (levels[i].Volume > levels[best].Volume) best = i;
            return best;
        }

        // ---------------------------------------------------------------- CSV
        public static char SepFrom(string text)
        {
            if (string.IsNullOrEmpty(text)) return ',';
            char c = text.Trim().Length > 0 ? text.Trim()[0] : ',';
            if (c == 't') return '\t';                       // cho phép gõ "tab"
            return (c == ',' || c == ';' || c == '|' || c == '\t') ? c : ',';
        }

        public static string LevelsHeader(char sep) => string.Join(sep.ToString(), new[]
        {
            "bar_idx", "datetime", "price", "bid_vol", "ask_vol", "volume",
            "delta", "trades", "buy_trades", "sell_trades", "max_one_trade"
        });

        public static string BarsHeader(char sep) => string.Join(sep.ToString(), new[]
        {
            "bar_idx", "datetime", "open", "high", "low", "close", "bar_volume", "bar_ticks",
            "bid_vol", "ask_vol", "volume", "delta", "delta_finish", "max_delta", "min_delta",
            "cum_delta", "trades", "buy_trades", "sell_trades", "max_one_trade",
            "avg_size", "avg_buy_size", "avg_sell_size", "levels", "poc_price", "poc_volume",
            "open_interest"
        });

        public static void AppendLevelRow(StringBuilder sb, char sep, int barIdx, string dt,
                                          double price, in FpLevel lv, int digits)
        {
            sb.Append(barIdx.ToString(Inv)).Append(sep)
              .Append(dt).Append(sep)
              .Append(FmtPrice(price, digits)).Append(sep)
              .Append(FmtVol(lv.BidVol)).Append(sep)
              .Append(FmtVol(lv.AskVol)).Append(sep)
              .Append(FmtVol(lv.Volume)).Append(sep)
              .Append(FmtVol(lv.Delta)).Append(sep)
              .Append(lv.Trades.ToString(Inv)).Append(sep)
              .Append(lv.BuyTrades.ToString(Inv)).Append(sep)
              .Append(lv.SellTrades.ToString(Inv)).Append(sep)
              .Append(FmtVol(lv.MaxOneTrade)).Append('\n');
        }

        public static void AppendBarRow(StringBuilder sb, char sep, in FpBar b, int digits)
        {
            sb.Append(b.Idx.ToString(Inv)).Append(sep)
              .Append(b.Dt).Append(sep)
              .Append(FmtPrice(b.Open, digits)).Append(sep)
              .Append(FmtPrice(b.High, digits)).Append(sep)
              .Append(FmtPrice(b.Low, digits)).Append(sep)
              .Append(FmtPrice(b.Close, digits)).Append(sep)
              .Append(FmtVol(b.BarVolume)).Append(sep)
              .Append(b.BarTicks.ToString(Inv)).Append(sep)
              .Append(FmtVol(b.BidVol)).Append(sep)
              .Append(FmtVol(b.AskVol)).Append(sep)
              .Append(FmtVol(b.Volume)).Append(sep)
              .Append(FmtVol(b.Delta)).Append(sep)
              .Append(FmtVol(b.DeltaFinish)).Append(sep)
              .Append(FmtVol(b.MaxDelta)).Append(sep)
              .Append(FmtVol(b.MinDelta)).Append(sep)
              .Append(FmtVol(b.CumDelta)).Append(sep)
              .Append(b.Trades.ToString(Inv)).Append(sep)
              .Append(b.BuyTrades.ToString(Inv)).Append(sep)
              .Append(b.SellTrades.ToString(Inv)).Append(sep)
              .Append(FmtVol(b.MaxOneTrade)).Append(sep)
              .Append(b.AvgSize.ToString("0.####", Inv)).Append(sep)
              .Append(b.AvgBuySize.ToString("0.####", Inv)).Append(sep)
              .Append(b.AvgSellSize.ToString("0.####", Inv)).Append(sep)
              .Append(b.Levels.ToString(Inv)).Append(sep)
              .Append(b.PocPrice > 0 ? FmtPrice(b.PocPrice, digits) : "").Append(sep)
              .Append(FmtVol(b.PocVolume)).Append(sep)
              .Append(FmtVol(b.OpenInterest)).Append('\n');
        }

        public static string FmtTime(DateTime t) => t.ToString("yyyy-MM-dd HH:mm:ss", Inv);

        // ---------------------------------------------------------- lọc ngày
        /// <summary>Nhận "yyyy-MM-dd" hoặc "yyyy/MM/dd" hoặc "dd/MM/yyyy". Rỗng/sai → false.</summary>
        public static bool TryParseDay(string s, out DateTime day)
        {
            day = default;
            if (string.IsNullOrWhiteSpace(s)) return false;
            string[] fmt = { "yyyy-MM-dd", "yyyy/MM/dd", "dd/MM/yyyy", "d/M/yyyy", "yyyyMMdd" };
            if (DateTime.TryParseExact(s.Trim(), fmt, Inv, DateTimeStyles.None, out var d))
            { day = d.Date; return true; }
            return false;
        }

        /// <summary>true = nến nằm trong khoảng [from, to] (to tính HẾT ngày). from/to null = bỏ qua cạnh đó.</summary>
        public static bool InRange(DateTime barTimeLocal, DateTime? from, DateTime? to)
        {
            if (from.HasValue && barTimeLocal < from.Value) return false;
            if (to.HasValue && barTimeLocal >= to.Value.Date.AddDays(1)) return false;
            return true;
        }

        // ------------------------------------------------------- tên file
        public static string SafeName(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return "unknown";
            var sb = new StringBuilder(s.Length);
            foreach (char c in s.Trim())
                sb.Append(char.IsLetterOrDigit(c) || c == '-' || c == '_' || c == '.' ? c : '_');
            string r = sb.ToString().Trim('_', '.');
            return r.Length == 0 ? "unknown" : (r.Length > 60 ? r.Substring(0, 60) : r);
        }

        /// <summary>
        /// Quyết định 2 đường dẫn xuất.
        ///   userPath rỗng            → defaultDir + tên tự sinh
        ///   userPath là .csv         → dùng luôn; file nến = "&lt;tên&gt;_bars.csv"
        ///   ngược lại (thư mục)      → thư mục đó + tên tự sinh
        /// </summary>
        public static void MakeNames(string userPath, string defaultDir, string symbol, string period,
                                     string stamp, out string levelsPath, out string barsPath)
        {
            string p = (userPath ?? "").Trim().Trim('"');
            if (p.Length > 0 && p.EndsWith(".csv", StringComparison.OrdinalIgnoreCase))
            {
                string dir = Path.GetDirectoryName(p);
                string baseName = Path.GetFileNameWithoutExtension(p);
                levelsPath = p;
                barsPath = string.IsNullOrEmpty(dir) ? baseName + "_bars.csv"
                                                     : Path.Combine(dir, baseName + "_bars.csv");
                return;
            }
            string outDir = p.Length > 0 ? p : defaultDir;
            string stem = $"fp_{SafeName(symbol)}_{SafeName(period)}_{SafeName(stamp)}";
            levelsPath = Path.Combine(outDir, stem + ".csv");
            barsPath = Path.Combine(outDir, stem + "_bars.csv");
        }
    }
}
