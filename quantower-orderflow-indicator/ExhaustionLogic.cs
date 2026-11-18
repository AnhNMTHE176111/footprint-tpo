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
//  LUẬT HIỆN TẠI (2026-11-18, fit trên chart M5 của CORVEN ngày 18/11, xem research/corven_m5_2026-11-18/README.md):
//   • RÂU nến ở phía đang xét phải dài >= MinWickTicks (3) tick (CORVEN dặn không lấy ở thân nến).
//   • TỔNG volume của bên đang soi (Ask ở đỉnh, Bid ở đáy) trên SumLevels (3) tick tính từ cực trị đi vào trong
//     phải <= SumRel (0,5) x volume trung bình mỗi mức giá có giao dịch của nến. Mức giá trống (giá nhảy cóc) tính 0;
//     nến có ít mức hơn SumLevels thì dùng số mức hiện có.
//   Đo trên 27 nến M5 (12:15-14:25 UTC 18/11): CORVEN đánh 11 dấu; luật cũ (cực trị <= 0,10 x trung bình mỗi mức, hoặc 3 mức giảm dần,
//   râu >= 1 tick) ra 30 dấu, 6 trùng, F1 0,29; luật mới 23 dấu, 9 trùng, F1 0,53. Mật độ: M1 ngày 05/11 0,28 dấu/nến, M5 ngày 17/11 0,48 dấu/nến.
//   ⚠️ Chỉ MỘT biểu đồ, 27 nến, nguồn dữ liệu của CORVEN khác nguồn mình. Đây là ĐÁNH DẤU để đọc chart, KHÔNG phải tín hiệu đã kiểm định lợi thế:
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
        public int SumLevels = 3;         // số mức giá xét, tính từ cực trị đi vào trong
        public double SumRel = 0.5;       // tổng bên soi trên SumLevels mức <= SumRel x TB volume/mức của nến
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
        public readonly double MeanLevelVol; // volume trung bình mỗi mức giá của nến
        public readonly double[] Seq;        // giá trị bên soi trên SumLevels mức, từ TRONG ra CỰC TRỊ
        public bool Hit => Kind != ExhKind.None;
        public ExhResult(ExhKind kind, bool top, long tick, double ext, double mean, double[] seq)
        { Kind = kind; Top = top; Tick = tick; ExtremeVol = ext; MeanLevelVol = mean; Seq = seq; }
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
        public static ExhResult Detect(bool top, long openTick, long highTick, long lowTick, long closeTick,
                                       IReadOnlyList<ExhLevel> levels, ExhSettings s)
        {
            long ext = top ? highTick : lowTick;
            var none = new ExhResult(ExhKind.None, top, ext, 0, 0, Array.Empty<double>());
            if (s == null || levels == null || levels.Count == 0 || highTick <= lowTick) return none;

            long bodyEdge = top ? Math.Max(openTick, closeTick) : Math.Min(openTick, closeTick);
            long wick = top ? highTick - bodyEdge : bodyEdge - lowTick;   // số tick râu ở phía này
            if (s.MinWickTicks > 0 && wick < s.MinWickTicks) return none;

            var byTick = new Dictionary<long, ExhLevel>(levels.Count);
            foreach (var l in levels) byTick[l.Tick] = l;
            double mean = MeanLevelVolume(levels);

            int step = top ? -1 : 1;                  // đi từ cực trị VÀO trong nến
            int span = (int)(highTick - lowTick) + 1; // số mức của cả nến
            int want = Math.Min(Math.Max(1, s.SumLevels), span);
            var fromExt = new double[want];           // [0] = cực trị
            double sum = 0;
            for (int j = 0; j < want; j++)
            {
                byTick.TryGetValue(ext + step * j, out var l);   // mức trống (giá nhảy cóc) = 0
                fromExt[j] = top ? l.Ask : l.Bid;
                sum += fromExt[j];
            }
            if (!(sum <= s.SumRel * mean + 1e-9)) return none;

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
