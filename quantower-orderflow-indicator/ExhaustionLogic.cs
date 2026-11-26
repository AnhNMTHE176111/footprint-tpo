// ============================================================================
//  ExhaustionLogic — KIỆT SỨC (exhaustion) thuần theo định nghĩa CORVEN (Meet 2026-11-07)
// ============================================================================
//  Lớp THUẦN (không phụ thuộc TradingPlatform.BusinessLayer) để test được bằng tests/.
//
//  Lời CORVEN (corven-meet/2026-11-07/transcript.md, mục 5, 12, 18):
//   • "Kiệt sức: ở ĐỈNH thì xem bên ASK, ở ĐÁY thì xem bên BID."
//   • "Thấy nó NHỎ là được — nhỏ, hoặc GIẢM DẦN VỀ 0."
//   • "Lấy ở RÂU NẾN thôi, đừng lấy ở thân nến."
//   • "Đỉnh = không còn người mua (kiệt sức buy), đáy = không còn người bán (kiệt sức sell)."
//   • "Giá phải QUÉT QUA được mức đó thì kiệt sức mới bị VÔ HIỆU — quét qua là được, không cần đóng nến."
//
//  LUẬT HIỆN TẠI (2026-11-18, fit lại trên chart M5 của CORVEN ngày 18/11, xem research/corven_m5_2026-11-18/README.md; bản Python gốc: rules.py exh_rule):
//   • RÂU nến ở phía đang xét phải dài >= MinWickTicks (3) tick (CORVEN dặn không lấy ở thân nến).
//   • TỔNG volume của bên đang soi (Ask ở đỉnh, Bid ở đáy) trên SumLevels (6) tick tính từ cực trị đi vào trong
//     phải <= SumHistRatio (1,1) x volume trung bình mỗi mức giá có giao dịch của 20 nến ĐÃ ĐÓNG TRƯỚC (mức nền lịch sử, KHÔNG phải trung bình
//     của chính nến này; cần >= 5 nến lịch sử, chưa đủ thì không đánh dấu). Mức giá trống (giá nhảy cóc) tính 0.
//   Đo trên 26 nến M5 (12:15-14:20 UTC 18/11): CORVEN đánh 11 dấu; luật này ra 13 dấu, trùng 11, thừa 2, sót 0 (F1 0,917).
//   ⚠️ Chỉ MỘT biểu đồ, 26 nến, nguồn dữ liệu của CORVEN khác nguồn mình. Đây là ĐÁNH DẤU để đọc chart, KHÔNG phải tín hiệu đã kiểm định lợi thế:
//   mức kiệt sức bị quét qua với tỷ lệ gần như nến bất kỳ (44%/70%/84% sau 1/5/20 nến, nến bất kỳ 46/72/85%).
// ============================================================================

using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    // Small = có dấu kiệt sức (tên giữ lại cho tương thích; nhánh "giảm dần" cũ đã bỏ 2026-11-18)
    public enum ExhKind { None = 0, Small = 1 }

    public sealed class ExhSettings
    {
        public int MinWickTicks = 3;      // râu >= số tick này (<= 0: không đòi râu)
        public int SumLevels = 6;         // số mức giá xét, tính từ cực trị đi vào trong
        public double SumHistRatio = 1.1; // tổng bên soi trên SumLevels mức <= số này x TB volume/mức của 20 nến đã đóng trước (mức nền lịch sử)
        // 2026-11-24 (research/adaptive_2026-11-24, mục 4): thêm điều kiện tổng bên soi <= số này x TRUNG VỊ của chính đại lượng đó (đuôi đỉnh theo Ask
        // + đuôi đáy theo Bid) trên N nến đã đóng trước. <= 0 = tắt (đúng luật cũ). Lý do đo được: đuôi 6 tick gần như không tăng theo khung
        // (trung vị 11 -> 29) còn TB mỗi ô tăng mạnh (5 -> 65) nên khung lớn gần như nến nào cũng nổ (NQ H1 1,77 dấu/nến -> 0,75).
        // CORVEN GC M5: 11/11 dấu vẫn trùng, thừa 2 -> 1. ⚠ 0,8 chọn trên chính 11 dấu của một chart (dấu CORVEN "dày" nhất có tỉ số 0,76).
        public double TailMedianRatio = 0;
    }

    // Nền đuôi: mỗi nến ĐÃ ĐÓNG có giao dịch và high > low nộp HAI số (đuôi đỉnh theo Ask, đuôi đáy theo Bid), không phụ thuộc râu.
    // Giữ N nến; trung vị của 2 x số nến giá trị, cần >= 5 nến.
    public sealed class ExhTailBaseline
    {
        public const int MinBars = 5;
        private readonly int _n;
        private readonly Queue<(double top, double bot)> _q = new Queue<(double, double)>();
        public ExhTailBaseline(int n) { _n = Math.Max(1, n); }
        public int Count => _q.Count;
        public void Add(double topTail, double botTail)
        {
            _q.Enqueue((topTail, botTail));
            while (_q.Count > _n) _q.Dequeue();
        }
        public bool TryGetMedian(out double median)
        {
            median = 0;
            if (_q.Count < MinBars) return false;
            var v = new List<double>(_q.Count * 2);
            foreach (var p in _q) { v.Add(p.top); v.Add(p.bot); }
            v.Sort();
            int n = v.Count;
            median = n % 2 == 1 ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2.0;
            return true;
        }
    }

    public readonly struct ExhLevel
    {
        public readonly long Tick;     // chỉ số tick của mức giá (price / tickSize, đã làm tròn)
        public readonly double Bid;    // volume khớp ở Bid (sell chủ động)
        public readonly double Ask;    // volume khớp ở Ask (buy chủ động)
        public readonly double Volume; // tổng volume mức (có thể > Bid+Ask nếu feed có lệnh không phân loại)
        public ExhLevel(long tick, double bid, double ask, double volume) { Tick = tick; Bid = bid; Ask = ask; Volume = volume; }
        public ExhLevel(long tick, double bid, double ask) : this(tick, bid, ask, bid + ask) { }
    }

    public readonly struct ExhResult
    {
        public readonly ExhKind Kind;
        public readonly bool Top;            // true = đỉnh (kiệt sức buy), false = đáy (kiệt sức sell)
        public readonly long Tick;           // mức cực trị (đỉnh/đáy nến)
        public readonly double ExtremeVol;   // Ask ở đỉnh / Bid ở đáy
        public readonly double MeanLevelVol; // mức nền: volume trung bình mỗi mức giá của 20 nến đã đóng trước
        public readonly double[] Seq;        // giá trị bên soi trên SumLevels mức, từ TRONG ra CỰC TRỊ
        public bool Hit => Kind != ExhKind.None;
        public ExhResult(ExhKind kind, bool top, long tick, double ext, double mean, double[] seq)
        { Kind = kind; Top = top; Tick = tick; ExtremeVol = ext; MeanLevelVol = mean; Seq = seq; }
    }

    // ========================================================================
    //  LUẬT KIỆT SỨC THEO HÀNG GIÁ (2026-11-26, research/exh_2026-11-26/README.md mục 5; bản Python chuẩn: ref_rule.py)
    //  Thay luật theo từng tick ở trên trong indicator. So 95 dấu CORVEN (NQ M1 06/11, GC M1 05–06/11, GC M5 18/11):
    //  luật cũ trùng 64 / thừa 209 / sót 31; luật này trùng 82 / thừa 35 / sót 13.
    //   • Hàng giá như chart CORVEN: row(tick) = floor((tick - off) / G). NQ/MNQ G 8 off 4; GC/MGC G 2 off 1; mã khác G 1 off 0.
    //   • Đỉnh soi Ask của 3 hàng từ hàng chứa High đi xuống; đáy soi Bid của 3 hàng từ hàng chứa Low đi lên (hàng trống / ngoài nến = 0).
    //   • Có dấu khi: cả 3 hàng <= 0,35 x rowBase; tổng volume nến >= 0,8 x volBase; râu >= 2 hàng.
    //   • rowBase = TB (tổng volume ÷ số hàng có volume) của N nến ĐÃ ĐÓNG trước; volBase = TB tổng volume nến; cần >= 5 nến.
    // ========================================================================
    public static class ExhRowGrid
    {
        public const int Rows = 3, MinWickRows = 2;
        public const double SmallRatio = 0.35, MinBarVolRatio = 0.80;
        public static string Key(int g, int off) => $"exh-rows-v1:{g}/{off}/{Rows}/{SmallRatio}/{MinBarVolRatio}/{MinWickRows}";

        /// <summary>(G, off) của mã: NQ/MNQ (8, 4), GC/MGC (2, 1), mã khác (1, 0).</summary>
        public static (int g, int off) For(string symbolName)
        {
            if (SymbolPreset.IsNasdaq(symbolName)) return (8, 4);
            if (IsGold(symbolName)) return (2, 1);
            return (1, 0);
        }

        /// <summary>GC / MGC (mã liên tục hoặc mã tháng: GCZ26, /GC:XCEC, MGCZ6).</summary>
        public static bool IsGold(string symbolName)
        {
            if (string.IsNullOrWhiteSpace(symbolName)) return false;
            var s = symbolName.Trim().TrimStart('/').ToUpperInvariant();
            int colon = s.IndexOf(':'); if (colon >= 0) s = s.Substring(0, colon);
            string rest = s.StartsWith("MGC") ? s.Substring(3) : s.StartsWith("GC") ? s.Substring(2) : null;
            if (rest == null) return false;
            if (rest.Length == 0) return true;
            if ("FGHJKMNQUVXZ".IndexOf(rest[0]) < 0) return false;
            string y = rest.Substring(1);
            if (y.Length < 1 || y.Length > 2) return false;
            foreach (char c in y) if (c < '0' || c > '9') return false;
            return true;
        }

        public static long RowOf(long tick, int g, int off)
        {
            long x = tick - off;
            return x >= 0 ? x / g : -((-x + g - 1) / g);   // chia làm tròn XUỐNG (đúng cả số âm)
        }

        /// <summary>Volume TB mỗi hàng có giao dịch + tổng volume của nến (chỉ ô volume > 0). false = nến không có giao dịch.</summary>
        public static bool BarStats(IReadOnlyList<ExhLevel> levels, int g, int off, out double rowMean, out double total)
        {
            rowMean = 0; total = 0;
            if (levels == null) return false;
            var rows = new HashSet<long>();
            foreach (var l in levels)
                if (l.Volume > 0) { rows.Add(RowOf(l.Tick, g, off)); total += l.Volume; }
            if (rows.Count == 0) return false;
            rowMean = total / rows.Count;
            return true;
        }

        /// <summary>Dò kiệt sức đỉnh + đáy của một nến (o/h/l/c theo tick). hasBase = đã đủ nền.</summary>
        public static (bool top, bool bot) Detect(long o, long h, long l, long c, IReadOnlyList<ExhLevel> levels, int g, int off,
                                                  bool hasBase, double rowBase, double volBase)
        {
            if (levels == null || h <= l || !hasBase || !(rowBase > 0)) return (false, false);
            var ask = new Dictionary<long, double>(); var bid = new Dictionary<long, double>();
            double tot = 0;
            foreach (var lv in levels)
            {
                if (!(lv.Volume > 0)) continue;
                long r = RowOf(lv.Tick, g, off);
                ask[r] = (ask.TryGetValue(r, out var a) ? a : 0) + lv.Ask;
                bid[r] = (bid.TryGetValue(r, out var b) ? b : 0) + lv.Bid;
                tot += lv.Volume;
            }
            if (ask.Count == 0) return (false, false);
            long rH = RowOf(h, g, off), rL = RowOf(l, g, off);
            double lim = SmallRatio * rowBase;
            double maxT = 0, maxB = 0;
            for (int j = 0; j < Rows; j++)
            {
                if (rH - j >= rL && ask.TryGetValue(rH - j, out var a)) maxT = Math.Max(maxT, a);
                if (rL + j <= rH && bid.TryGetValue(rL + j, out var b)) maxB = Math.Max(maxB, b);
            }
            long wT = rH - RowOf(Math.Max(o, c), g, off), wB = RowOf(Math.Min(o, c), g, off) - rL;
            bool volOk = tot >= MinBarVolRatio * volBase;
            return (volOk && wT >= MinWickRows && maxT <= lim, volOk && wB >= MinWickRows && maxB <= lim);
        }
    }

    // ========================================================================
    //  BIG TRADE = "BIG VOLUME THEO HÀNG" như chart M1 của CORVEN (2026-11-26, research/bigtrade_corven_2026-11-26/SPEC.md; Python chuẩn: ref_rule.py)
    //  Cùng lưới hàng với kiệt sức (ExhRowGrid). Hàng có volume >= 4,25 x rowBase (TB volume mỗi hàng của N nến đóng trước) -> một vòng
    //  tại tâm hàng (kẹp trong [low, high]); phía = Ask > Bid ? buy : sell; cỡ = clamp(ratio / 3,2; 1,33; 4,7) x chấm thường.
    //  Không cần lệnh đơn (lịch sử không có) -> lịch sử và live ra như nhau. 3 mẫu M1 CORVEN: trùng 112 / thừa 66 / sót 32 (luật lệnh đơn cũ 0 / 0 / 144).
    // ========================================================================
    public readonly struct BigVolRow
    {
        public readonly long Row; public readonly double CentreTick; public readonly int Side; public readonly double Ratio, SizeMult, Bid, Ask, Vol;
        public BigVolRow(long row, double centreTick, int side, double ratio, double sizeMult, double bid, double ask, double vol)
        { Row = row; CentreTick = centreTick; Side = side; Ratio = ratio; SizeMult = sizeMult; Bid = bid; Ask = ask; Vol = vol; }
    }

    public static class BigVolRows
    {
        public const double K = 4.25, SizeDiv = 3.2, SizeMin = 1.33, SizeMax = 4.7;
        public static string Key(int g, int off) => $"bigvol-rows-v2:{g}/{off}/{K}/{SizeDiv}/{SizeMin}/{SizeMax}";

        /// <summary>Các hàng Big Volume của nến (hàng tăng dần). hasBase = đã đủ nền (>= 5 nến).</summary>
        public static List<BigVolRow> Detect(IReadOnlyList<ExhLevel> levels, int g, int off, long highTick, long lowTick, bool hasBase, double rowBase)
        {
            var res = new List<BigVolRow>();
            if (levels == null || !hasBase || !(rowBase > 0)) return res;
            var acc = new SortedDictionary<long, (double bid, double ask, double vol)>();
            foreach (var l in levels)
            {
                if (!(l.Volume > 0)) continue;
                long r = ExhRowGrid.RowOf(l.Tick, g, off);
                acc.TryGetValue(r, out var a);
                acc[r] = (a.bid + l.Bid, a.ask + l.Ask, a.vol + l.Volume);
            }
            foreach (var kv in acc)
            {
                double ratio = kv.Value.vol / rowBase;
                if (!(ratio >= K)) continue;
                double c = Math.Min((double)highTick, Math.Max((double)lowTick, kv.Key * g + off + (g - 1) / 2.0));
                double size = Math.Min(SizeMax, Math.Max(SizeMin, ratio / SizeDiv));
                res.Add(new BigVolRow(kv.Key, c, kv.Value.ask > kv.Value.bid ? 1 : -1, ratio, size, kv.Value.bid, kv.Value.ask, kv.Value.vol));
            }
            return res;
        }
    }

    /// <summary>Nền của luật theo hàng: N nến đóng gần nhất có giao dịch, mỗi nến (volume TB mỗi hàng, tổng volume); cần >= 5 nến.</summary>
    public sealed class ExhRowBaseline
    {
        public const int MinBars = 5;
        private readonly int _n;
        private readonly Queue<(double rowMean, double total)> _q = new Queue<(double, double)>();
        public ExhRowBaseline(int n) { _n = Math.Max(1, n); }
        public int Count => _q.Count;
        public void Add(double rowMean, double total)
        {
            _q.Enqueue((rowMean, total));
            while (_q.Count > _n) _q.Dequeue();
        }
        public bool TryGet(out double rowBase, out double volBase)
        {
            rowBase = volBase = 0;
            if (_q.Count < MinBars) return false;
            // cộng theo thứ tự hàng đợi (khớp Python sum(list) từng bit)
            double m = 0, t = 0; foreach (var p in _q) { m += p.rowMean; t += p.total; }
            rowBase = m / _q.Count; volBase = t / _q.Count;
            return true;
        }
    }

    public static class ExhaustionLogic
    {
        // Trung bình volume mỗi mức giá CÓ giao dịch của nến.
        public static double MeanLevelVolume(IReadOnlyList<ExhLevel> levels)
        {
            double sum = 0; int cnt = 0;
            if (levels != null)
                foreach (var l in levels)
                    if (l.Volume > 0) { sum += l.Volume; cnt++; }
            return cnt > 0 ? sum / cnt : 0;
        }

        // Dò kiệt sức ở MỘT phía của nến. highTick/lowTick/openTick/closeTick là chỉ số tick.
        // Tổng bên soi (Ask ở đỉnh, Bid ở đáy) trên sumLevels tick từ cực trị extTick đi vào trong; tick trống = 0.
        public static double TailSum(bool top, long extTick, IReadOnlyList<ExhLevel> levels, int sumLevels)
        {
            var byTick = new Dictionary<long, ExhLevel>(levels?.Count ?? 0);
            if (levels != null) foreach (var l in levels) byTick[l.Tick] = l;
            return TailSum(top, extTick, byTick, sumLevels);
        }
        private static double TailSum(bool top, long extTick, Dictionary<long, ExhLevel> byTick, int sumLevels)
        {
            int step = top ? -1 : 1, want = Math.Max(1, sumLevels);
            double sum = 0;
            for (int j = 0; j < want; j++)
            {
                byTick.TryGetValue(extTick + step * j, out var l);
                sum += top ? l.Ask : l.Bid;
            }
            return sum;
        }

        public static ExhResult Detect(bool top, long openTick, long highTick, long lowTick, long closeTick,
                                       IReadOnlyList<ExhLevel> levels, ExhSettings s,
                                       bool hasHist, double histMeanLevelVol, bool hasTail = false, double tailMedian = 0)
        {
            long ext = top ? highTick : lowTick;
            var none = new ExhResult(ExhKind.None, top, ext, 0, 0, Array.Empty<double>());
            if (s == null || levels == null || levels.Count == 0 || highTick <= lowTick) return none;
            if (!hasHist || !(histMeanLevelVol > 0)) return none;   // chưa đủ nến lịch sử để có mức nền

            long bodyEdge = top ? Math.Max(openTick, closeTick) : Math.Min(openTick, closeTick);
            long wick = top ? highTick - bodyEdge : bodyEdge - lowTick;   // số tick râu ở phía này
            if (s.MinWickTicks > 0 && wick < s.MinWickTicks) return none;

            var byTick = new Dictionary<long, ExhLevel>(levels.Count);
            foreach (var l in levels) byTick[l.Tick] = l;
            double mean = histMeanLevelVol;

            int step = top ? -1 : 1;                  // đi từ cực trị VÀO trong nến
            int want = Math.Max(1, s.SumLevels);
            var fromExt = new double[want];           // [0] = cực trị
            double sum = 0;
            for (int j = 0; j < want; j++)
            {
                byTick.TryGetValue(ext + step * j, out var l);   // mức trống (giá nhảy cóc) = 0
                fromExt[j] = top ? l.Ask : l.Bid;
                sum += fromExt[j];
            }
            if (!(sum <= s.SumHistRatio * mean)) return none;
            // điều kiện đuôi (tắt khi TailMedianRatio <= 0; chưa đủ nền đuôi thì chỉ áp luật cũ)
            if (s.TailMedianRatio > 0 && hasTail && !(sum <= s.TailMedianRatio * tailMedian)) return none;

            // tooltip/Seq: chuỗi giá trị bên soi từ TRONG ra CỰC TRỊ
            var seq = new double[want];
            for (int j = 0; j < want; j++) seq[j] = fromExt[want - 1 - j];
            return new ExhResult(ExhKind.Small, top, ext, fromExt[0], mean, seq);
        }

        // VÔ HIỆU (CORVEN 0:54): một nến SAU đó chỉ cần RÂU quét qua mức kiệt sức là đủ, không cần đóng nến.
        // sweepTicks = phải vượt bao nhiêu tick (1 = vượt qua; 0 = chạm lại đúng mức cũng tính).
        public static bool IsSwept(bool top, long levelTick, long laterHighTick, long laterLowTick, int sweepTicks)
        {
            int t = Math.Max(0, sweepTicks);
            return top ? laterHighTick >= levelTick + t : laterLowTick <= levelTick - t;
        }

        // Tooltip NGẮN (người học chốt 2026-11-08: "ghi là kiệt sức buy/sell thôi").
        public static string Describe(ExhResult r)
        {
            if (!r.Hit) return "";
            return r.Top ? "Kiệt sức buy" : "Kiệt sức sell";
        }
    }
}
