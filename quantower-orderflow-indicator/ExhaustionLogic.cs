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
//  Định lượng (đo trên GCZ26 M1, 90 ngày 2026-07-23 → 10-21, 86.333 nến, xem báo cáo commit):
//   • Ask tại đỉnh / Bid tại đáy có TRUNG VỊ chỉ 1 hợp đồng, 58% nến ≤ 1 → ngưỡng tuyệt đối "≤ 1-2"
//     đánh dấu một nửa số nến, vô nghĩa. Vì vậy "nhỏ" phải TƯƠNG ĐỐI với chính cây nến:
//       NHỎ      : giá trị ở cực trị ≤ SmallRel × (volume trung bình mỗi mức giá của nến)  [mặc định 0,10]
//                  (nến mỏng TB ~4/mức → thực chất đòi = 0; nến dày TB 50/mức → ≤ 5 vẫn là "nhỏ")
//       GIẢM DẦN : FadeLevels mức trên cùng của râu (đều phải nằm trong RÂU) giảm NGẶT về phía cực trị
//                  và mức cuối ≤ FadeEndRel × TB/mức                                [mặc định 3 mức, 0,25]
//   • Bắt buộc có râu ≥ 1 tick ở phía đang xét: nến đóng ngay tại đỉnh/đáy thì mức cực trị là THÂN,
//     CORVEN dặn không lấy ở thân.
//  ⚠️ Đây là ĐÁNH DẤU để đọc chart, KHÔNG phải tín hiệu đã kiểm định lợi thế: đo cho thấy mức kiệt sức
//     bị quét qua với tỷ lệ gần như bằng nến bất kỳ (44%/70%/84% sau 1/5/20 nến, nến bất kỳ 46/72/85%).
// ============================================================================

using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    public enum ExhKind { None = 0, Small = 1, Fade = 2 }

    public sealed class ExhSettings
    {
        public double SmallRel = 0.10;    // "nhỏ": cực trị ≤ SmallRel × TB volume/mức (0 = phải đúng bằng 0)
        public int FadeLevels = 3;        // "giảm dần về 0": số mức râu xét (< 2 = tắt nhánh này)
        public double FadeEndRel = 0.25;  // mức cuối của chuỗi giảm dần ≤ FadeEndRel × TB volume/mức
        public bool RequireWick = true;   // chỉ lấy ở râu nến (CORVEN) — tắt chỉ để thử nghiệm
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
        public readonly double[] Seq;        // giá trị bên soi, từ TRONG râu ra CỰC TRỊ (để ghi tooltip)
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
            if (s.RequireWick && wick < 1) return none;

            var byTick = new Dictionary<long, ExhLevel>(levels.Count);
            foreach (var l in levels) byTick[l.Tick] = l;
            double mean = MeanLevelVolume(levels);

            int step = top ? -1 : 1;                  // đi từ cực trị VÀO trong nến
            int span = (int)(highTick - lowTick) + 1; // số mức của cả nến
            int want = Math.Min(Math.Max(1, s.FadeLevels), span);
            var fromExt = new double[want];           // [0] = cực trị
            for (int j = 0; j < want; j++)
            {
                byTick.TryGetValue(ext + step * j, out var l);   // mức trống (giá nhảy cóc) = 0
                fromExt[j] = top ? l.Ask : l.Bid;
            }
            double extVol = fromExt[0];

            // tooltip: chuỗi từ trong ra cực trị, chỉ lấy phần nằm trong râu (tối đa 'want' mức)
            int inWick = (int)Math.Min(want, s.RequireWick ? wick : want);
            if (inWick < 1) inWick = 1;
            var seq = new double[inWick];
            for (int j = 0; j < inWick; j++) seq[j] = fromExt[inWick - 1 - j];

            if (extVol <= s.SmallRel * mean + 1e-9)
                return new ExhResult(ExhKind.Small, top, ext, extVol, mean, seq);

            int n = s.FadeLevels;
            if (n >= 2 && span >= n && (!s.RequireWick || wick >= n))
            {
                bool strictlyFading = true;
                for (int j = 0; j < n - 1; j++)
                    if (!(fromExt[j] < fromExt[j + 1])) { strictlyFading = false; break; }
                if (strictlyFading && extVol <= s.FadeEndRel * mean + 1e-9)
                    return new ExhResult(ExhKind.Fade, top, ext, extVol, mean, seq);
            }
            return none;
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
