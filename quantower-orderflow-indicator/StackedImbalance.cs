// ============================================================================
//  StackedImbalance — logic THUẦN của Stacked Imbalance (2026-11-08)
// ============================================================================
//  Viết lại theo cách mentor CORVEN dùng và mô tả trong buổi Meet 2026-11-07
//  (corven-meet/2026-11-07/transcript.md mục 1, 3, 7, 8, 24):
//    · "nó là MỘT VÙNG chứ không phải một điểm"            → vẽ hình chữ nhật, không vẽ thoi từng mức
//    · "so CHÉO Ask với Bid, người ta hay để gấp 3, đang để 250%"
//    · "tạo ra một cái zone, zone liên tiếp"                → ≥ N mức liên tiếp cùng phía
//    · "xem vị trí của nó ở đâu trong cây nến ... giữa thân nến thì mới khỏe ... ở đỉnh nến
//       xong bị rút râu xuống thì không đẹp lắm"           → phân loại vị trí (thân / râu)
//    · "không giữ được giá, đâm thủng ngược lên → đảo chiều" → vùng kết thúc khi bị xuyên
//    · "dùng gần thôi, đừng dùng xa"                       → giới hạn độ dài kéo sang phải
//  Trên chart Sierra của CORVEN, vùng là hình chữ nhật xanh lơ (buy) / hồng (sell) bắt đầu
//  từ nến tạo ra nó, kéo sang phải tới đúng NẾN ĐẦU TIÊN có giá chạm lại vùng thì dừng
//  (đã soi khung hình video 0:03–0:05, 0:19–0:20, 1:05).
//
//  ĐỊNH NGHĨA THUẦN (không cổng thống kê nào khác):
//    Buy imbalance ở mức i : Ask[i] ≥ Tỷ lệ% × Bid[i−1]   (mua chủ động áp đảo bán chủ động ở mức NGAY DƯỚI)
//    Sell imbalance ở mức i: Bid[i] ≥ Tỷ lệ% × Ask[i+1]   (bán chủ động áp đảo mua chủ động ở mức NGAY TRÊN)
//    Mức trong khoảng High–Low không có giao dịch = 0. Bên đối diện = 0 vẫn tính là imbalance,
//    nhưng bên áp đảo phải ≥ "Volume tối thiểu" (mặc định 1 = chỉ cần có giao dịch; tăng lên nếu
//    muốn bỏ ca 1-vs-0 — xem số đo trong báo cáo commit).
//    Stacked = ≥ N mức imbalance CÙNG PHÍA LIÊN TIẾP trong một nến. Vùng = [giá mức thấp nhất,
//    giá mức cao nhất] của chuỗi.
//
//  Class này KHÔNG tham chiếu TradingPlatform.BusinessLayer → test độc lập được (xem tests/).
//  ⚠️ Đây là công cụ ĐÁNH DẤU để đọc chart theo lời giảng, CHƯA phải lợi thế đã kiểm định.
// ============================================================================

using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    public enum SiPosition { Body = 0, UpperWick = 1, LowerWick = 2 }

    // Lý do vùng dừng kéo dài sang phải
    public enum SiEnd { Active = 0, Touched = 1, ClosedThrough = 2, Expired = 3 }

    // Chế độ kết thúc vùng
    public enum SiEndMode
    {
        Touch = 0,          // như chart Sierra của CORVEN: dừng ở nến đầu tiên chạm lại vùng
        CloseThrough = 1    // giữ vùng qua các lần test, chỉ dừng khi một nến ĐÓNG CỬA xuyên qua mép xa
    }

    public sealed class SiZone
    {
        public int Side;            // +1 = buy (xanh lơ), −1 = sell (hồng)
        public int LoIdx, HiIdx;    // chỉ số mức trong mảng của nến (0 = mức thấp nhất)
        public double Lo, Hi;       // giá mức imbalance thấp nhất / cao nhất của chuỗi
        public int Levels;          // số mức liên tiếp
        public double MinRatio;     // tỷ lệ chéo YẾU nhất trong chuỗi (∞ nếu mọi mức bên kia = 0)
        public double DomVolume;    // tổng volume bên áp đảo trong chuỗi
        public double OppVolume;    // tổng volume bên đối diện (chéo) trong chuỗi
        public SiPosition Position;
        public bool Weak;           // buy nằm ở râu TRÊN / sell nằm ở râu DƯỚI = "bị rút râu" (CORVEN: không đẹp)
    }

    public static class StackedImbalanceCalc
    {
        private const double Eps = 1e-9;

        // ask[i], bid[i]: volume mua chủ động (khớp Ask) / bán chủ động (khớp Bid) ở mức thứ i,
        // các mức LIÊN TIẾP từng tick từ Low lên High (mức không giao dịch = 0).
        public static List<SiZone> Detect(double lowPrice, double tick, double[] ask, double[] bid,
                                          double ratioPct, int minRun, double minVolume)
        {
            var res = new List<SiZone>();
            if (ask == null || bid == null) return res;
            int n = Math.Min(ask.Length, bid.Length);
            if (n < 2 || tick <= 0) return res;
            double r = ratioPct / 100.0;
            int run = Math.Max(1, minRun);
            double mv = Math.Max(minVolume, 0);

            var buy = new bool[n];
            var sell = new bool[n];
            for (int i = 1; i < n; i++)
                buy[i] = IsImb(ask[i], bid[i - 1], r, mv);
            for (int i = 0; i < n - 1; i++)
                sell[i] = IsImb(bid[i], ask[i + 1], r, mv);

            Collect(res, buy, +1, run, lowPrice, tick, ask, bid);
            Collect(res, sell, -1, run, lowPrice, tick, ask, bid);
            return res;
        }

        // Một mức là imbalance khi bên áp đảo > 0, ≥ volume tối thiểu, và ≥ tỷ lệ × bên chéo.
        public static bool IsImb(double dominant, double opposite, double ratio, double minVolume)
            => dominant > 0 && dominant >= minVolume && dominant >= ratio * opposite - Eps;

        private static void Collect(List<SiZone> res, bool[] f, int side, int run, double lowPrice, double tick,
                                    double[] ask, double[] bid)
        {
            int n = f.Length, s = -1;
            for (int i = 0; i <= n; i++)
            {
                bool on = i < n && f[i];
                if (on && s < 0) s = i;
                if (!on && s >= 0)
                {
                    int e = i - 1;
                    if (e - s + 1 >= run) res.Add(MakeZone(side, s, e, lowPrice, tick, ask, bid));
                    s = -1;
                }
            }
        }

        private static SiZone MakeZone(int side, int s, int e, double lowPrice, double tick, double[] ask, double[] bid)
        {
            double minR = double.PositiveInfinity, dom = 0, opp = 0;
            for (int i = s; i <= e; i++)
            {
                double d = side > 0 ? ask[i] : bid[i];
                double o = side > 0 ? bid[i - 1] : ask[i + 1];
                dom += d; opp += o;
                if (o > 0) minR = Math.Min(minR, d / o);
            }
            return new SiZone
            {
                Side = side, LoIdx = s, HiIdx = e,
                Lo = Math.Round((lowPrice + s * tick) / tick) * tick,
                Hi = Math.Round((lowPrice + e * tick) / tick) * tick,
                Levels = e - s + 1, MinRatio = minR, DomVolume = dom, OppVolume = opp
            };
        }

        // Vị trí vùng trong nến tạo ra nó (theo điểm giữa vùng so với thân nến).
        public static SiPosition Locate(double lo, double hi, double open, double close)
        {
            double mid = (lo + hi) / 2.0;
            double top = Math.Max(open, close), bot = Math.Min(open, close);
            if (mid > top + Eps) return SiPosition.UpperWick;
            if (mid < bot - Eps) return SiPosition.LowerWick;
            return SiPosition.Body;
        }

        // Gán vị trí + cờ "yếu" (buy ở râu trên / sell ở râu dưới = lực đẩy bị rút râu ngược lại).
        public static void Classify(SiZone z, double open, double close)
        {
            z.Position = Locate(z.Lo, z.Hi, open, close);
            z.Weak = (z.Side > 0 && z.Position == SiPosition.UpperWick)
                  || (z.Side < 0 && z.Position == SiPosition.LowerWick);
        }

        // Kiểm một nến SAU nến tạo vùng: vùng có dừng ở nến này không.
        //  · Touch       : nến chạm vùng (High ≥ Lo và Low ≤ Hi) → Touched. Đóng cửa vượt hẳn mép xa
        //                  (trường hợp nhảy giá qua vùng) cũng tính là kết thúc → ClosedThrough.
        //  · CloseThrough: chỉ dừng khi nến ĐÓNG CỬA xuyên qua mép xa (buy: close < Lo; sell: close > Hi)
        //                  — CORVEN: "không giữ được giá, đâm thủng" (phá cấu trúc dùng nến đóng cửa).
        public static SiEnd CheckEnd(int side, double lo, double hi, double high, double low, double close, SiEndMode mode)
        {
            bool through = side > 0 ? close < lo - Eps : close > hi + Eps;
            if (mode == SiEndMode.Touch)
            {
                if (through) return SiEnd.ClosedThrough;
                if (high >= lo - Eps && low <= hi + Eps) return SiEnd.Touched;
                return SiEnd.Active;
            }
            return through ? SiEnd.ClosedThrough : SiEnd.Active;
        }

        // Theo dõi 1 vùng qua chuỗi nến sau nó (dùng cho test + nạp lại lịch sử).
        // Trả về (chỉ số nến kết thúc tính từ 1 = nến ngay sau nến tạo vùng, lý do). maxBars ≤ 0 = không giới hạn.
        public static (int endOffset, SiEnd reason) Follow(int side, double lo, double hi,
            IReadOnlyList<(double high, double low, double close)> after, SiEndMode mode, int maxBars)
        {
            for (int j = 0; j < after.Count; j++)
            {
                int off = j + 1;
                var e = CheckEnd(side, lo, hi, after[j].high, after[j].low, after[j].close, mode);
                if (e != SiEnd.Active) return (off, e);
                if (maxBars > 0 && off >= maxBars) return (off, SiEnd.Expired);
            }
            return (-1, SiEnd.Active);
        }

        public static string PositionText(SiPosition p) => p switch
        {
            SiPosition.Body => "giữa thân nến",
            SiPosition.UpperWick => "ở râu trên",
            _ => "ở râu dưới"
        };
    }
}
