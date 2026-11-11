// ============================================================================
//  Ô Bid/Ask lớn (CellBig) — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN (Sierra), fit trên 885 bóng / 11.796 ô, 2 phiên 5-6/11/2026
//  (GCZ26 M1): F1 0,83, recall 87%, precision 80%. KHÔNG phải lợi thế đã kiểm định.
//    GOM MỨC GIÁ THÀNH HÀNG (2026-11-11, reverse-engineer chart Sierra của CORVEN): chart CORVEN gộp 2 tick
//    thành 1 hàng (0,2 giá với GC), hàng = (tick lẻ, tick chẵn kế tiếp): row = floor((tickIndex - 1) / 2).
//    Bóng đặt ở TÂM hàng. Bằng chứng: khoảng cách giữa các bóng kề nhau chủ yếu 2 tick; lệch pha hàng
//    (x.0,x.1) trúng 400/885, pha (x.1,x.2) trúng 784/885. ⚠ Pha hàng đo trên GC (tick 0,1) chart CORVEN;
//    mã khác chưa kiểm.
//    hàng: bid = tổng SellVolume, ask = tổng BuyVolume, vol = tổng Volume các mức trong hàng.
//    bên áp đảo của hàng = max(ask, bid) >= Ratio (1,3) x B  (và >= sàn 3)
//    B = trung bình của N nến ĐÃ ĐÓNG TRƯỚC của "volume TB mỗi HÀNG có giao dịch" (cần >= 5 nến)
//    Màu (luật 2026-11-12, màu đúng 93,6% trên 879 bóng): tím khi BÊN YẾU CŨNG tự vượt ngưỡng nổ (cả cột Bid lẫn
//    cột Ask đều đủ nổ bóng); còn lại xanh = ask trội, đỏ = bid trội.
//    Fit ngày 05/11, kiểm ngày 06/11 — ghép 1-1 ±1 tick với 885 bóng CORVEN (580 nến 5-6/11): mình 972 bóng,
//    trúng 784, thừa 188 (19%), sót 101 (11%), F1 0,844; ngày 06/11: 319 vs 302, F1 0,870; màu đúng 88%.
//    RowTicks = 1 -> hành vi theo từng tick như bản cũ. Gộp ô liền kề ±1 tick (MergeAdjacent) giữ lại nhưng
//    mặc định TẮT (xấp xỉ sai vị trí, đã thay bằng gom hàng).
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    public struct CellBigDecision
    {
        public bool Hit;
        public int Side;        // +1 = buy (Ask) trội, -1 = sell (Bid) trội, 0 = bên yếu cũng đủ nổ (tím)
        public double Mult;     // sideVol / B (0 nếu chưa có B)
        public double SizeFrac; // 0..1 (tỉ lệ so với bề ngang nến)
    }

    public static class CellBigLogic
    {
        public const int MinHistoryBars = 5;
        public const double SizeMinFrac = 0.45;   // cỡ ở ngưỡng
        public const double SizeFullMult = 6.0;   // từ tỉ lệ này trở lên = 100% bề ngang nến

        public static CellBigDecision Decide(double buy, double sell, double baseline, bool hasBaseline,
            double ratio, double minSide, bool fixedMode, double fixedThreshold)
        {
            var d = new CellBigDecision();
            double side = Math.Max(buy, sell), weak = Math.Min(buy, sell);
            if (side <= 0) return d;
            d.Mult = hasBaseline && baseline > 0 ? side / baseline : 0;
            if (fixedMode) d.Hit = side >= fixedThreshold;
            else d.Hit = hasBaseline && baseline > 0 && side >= ratio * baseline;
            if (side < minSide) d.Hit = false;
            if (!d.Hit) return d;
            bool weakBig = fixedMode ? weak >= fixedThreshold : (hasBaseline && baseline > 0 && weak >= ratio * baseline);
            weakBig = weakBig && weak >= minSide;
            d.Side = weakBig ? 0 : (buy >= sell ? 1 : -1);
            d.SizeFrac = Size(d.Mult, ratio);
            return d;
        }

        // Gộp ô liền kề trong MỘT nến (non-maximum suppression). cells = (chỉ số tick, bên áp đảo).
        // Duyệt theo side giảm dần (hòa -> tick thấp hơn trước, tất định); giữ ô nếu không ô đã giữ nào
        // cách nó <= gapTicks. gapTicks <= 0 = tắt gộp (giữ hết). Trả về CHỈ SỐ trong cells của ô được giữ.
        public static List<int> MergeAdjacent(IList<(long tick, double side)> cells, int gapTicks)
        {
            var kept = new List<int>();
            if (cells == null || cells.Count == 0) return kept;
            if (gapTicks <= 0) { for (int i = 0; i < cells.Count; i++) kept.Add(i); return kept; }
            var order = new List<int>();
            for (int i = 0; i < cells.Count; i++) order.Add(i);
            order.Sort((a, b) =>
            {
                int c = cells[b].side.CompareTo(cells[a].side);
                if (c != 0) return c;
                c = cells[a].tick.CompareTo(cells[b].tick);
                return c != 0 ? c : a.CompareTo(b);
            });
            foreach (int i in order)
            {
                bool clash = false;
                foreach (int j in kept)
                    if (Math.Abs(cells[i].tick - cells[j].tick) <= gapTicks) { clash = true; break; }
                if (!clash) kept.Add(i);
            }
            return kept;
        }

        // ---- GOM HÀNG ----
        public struct Row
        {
            public long RowId;
            public double Buy, Sell, Vol;   // Buy = ask (BuyVolume), Sell = bid (SellVolume)
            public long LoTick, HiTick;     // các tick cấu thành hàng (cả khoảng, kể cả tick không có giao dịch)
        }

        // floor division đúng cho số âm
        public static long FloorDiv(long a, long b)
        {
            long q = a / b;
            if ((a % b != 0) && ((a < 0) != (b < 0))) q--;
            return q;
        }

        public static long RowOf(long tickIndex, int rowTicks, int rowOffset)
            => rowTicks <= 1 ? tickIndex : FloorDiv(tickIndex - rowOffset, rowTicks);

        public static long RowLoTick(long row, int rowTicks, int rowOffset)
            => rowTicks <= 1 ? row : row * rowTicks + rowOffset;

        // tâm hàng tính bằng "chỉ số tick" (có thể lẻ nửa tick): vd hàng (tick 41241, 41242) -> 41241,5
        public static double RowCenterTick(long row, int rowTicks, int rowOffset)
            => RowLoTick(row, rowTicks, rowOffset) + (Math.Max(1, rowTicks) - 1) / 2.0;

        public static double RowCenterPrice(long row, int rowTicks, int rowOffset, double tickSize)
            => RowCenterTick(row, rowTicks, rowOffset) * tickSize;

        // gom mức -> hàng. levels = (tickIndex, buy, sell, vol); trả về hàng theo RowId tăng dần.
        public static List<Row> GroupRows(IEnumerable<(long tick, double buy, double sell, double vol)> levels,
            int rowTicks, int rowOffset)
        {
            var map = new SortedDictionary<long, Row>();
            foreach (var l in levels)
            {
                long id = RowOf(l.tick, rowTicks, rowOffset);
                if (!map.TryGetValue(id, out var r))
                {
                    long lo = RowLoTick(id, rowTicks, rowOffset);
                    r = new Row { RowId = id, LoTick = lo, HiTick = lo + Math.Max(1, rowTicks) - 1 };
                }
                r.Buy += l.buy; r.Sell += l.sell; r.Vol += l.vol;
                map[id] = r;
            }
            return new List<Row>(map.Values);
        }

        // volume TB mỗi HÀNG có giao dịch (vol > 0) của nến; false nếu nến rỗng
        public static bool BarRowMean(IList<Row> rows, out double mean)
        {
            double tot = 0; int n = 0;
            if (rows != null) foreach (var r in rows) if (r.Vol > 0) { tot += r.Vol; n++; }
            mean = n > 0 ? tot / n : 0;
            return n > 0 && tot > 0;
        }

        // cỡ to dần theo mult (nén sqrt): SizeMinFrac ở mult = ratio → 1,0 ở mult >= SizeFullMult
        public static double Size(double mult, double ratio)
        {
            if (mult <= 0) return 1.0;   // chế độ ngưỡng cố định không có tỉ lệ → cỡ đầy đủ
            double lo = Math.Sqrt(Math.Max(ratio, 1e-9)), hi = Math.Sqrt(Math.Max(SizeFullMult, ratio + 1e-6));
            double t = (Math.Sqrt(mult) - lo) / (hi - lo);
            t = Math.Min(1.0, Math.Max(0.0, t));
            return SizeMinFrac + (1.0 - SizeMinFrac) * t;
        }

        // volume trung bình mỗi ô giá CÓ giao dịch trong nến; trả false nếu nến rỗng
        public static bool BarMean(double totalVolume, int levelsWithVolume, out double mean)
        {
            mean = levelsWithVolume > 0 ? totalVolume / levelsWithVolume : 0;
            return levelsWithVolume > 0 && totalVolume > 0;
        }
    }

    // Baseline B: trung bình cuốn của N nến ĐÃ ĐÓNG. Người gọi chỉ Add mỗi nến đóng ĐÚNG 1 lần.
    public sealed class CellBigBaseline
    {
        private readonly int _n;
        private readonly Queue<double> _q = new Queue<double>();
        public CellBigBaseline(int n) { _n = Math.Max(CellBigLogic.MinHistoryBars, n); }
        public int Count => _q.Count;
        public void Add(double barMean)
        {
            _q.Enqueue(barMean);
            while (_q.Count > _n) _q.Dequeue();
        }
        public bool TryGet(out double b)
        {
            b = 0;
            if (_q.Count < CellBigLogic.MinHistoryBars) return false;
            double s = 0; foreach (var v in _q) s += v;
            b = s / _q.Count;
            return b > 0;
        }
    }
}
