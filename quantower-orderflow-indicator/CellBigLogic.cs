// ============================================================================
//  Ô Bid/Ask lớn (CellBig) — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Luật MÔ PHỎNG HIỂN THỊ của CORVEN (Sierra). Cơ chế gom hàng fit trên 885 bóng, 2 phiên 5-6/11/2026 (GCZ26 M1, F1 0,83);
//  ngưỡng nổ chỉnh lại 2026-11-18 theo chart M5 (xem bên dưới). KHÔNG phải lợi thế đã kiểm định.
//    GOM MỨC GIÁ THÀNH HÀNG (2026-11-11, reverse-engineer chart Sierra của CORVEN): chart CORVEN gộp 2 tick
//    thành 1 hàng (0,2 giá với GC), hàng = (tick lẻ, tick chẵn kế tiếp): row = floor((tickIndex - 1) / 2).
//    Bóng đặt ở TÂM hàng. Bằng chứng: khoảng cách giữa các bóng kề nhau chủ yếu 2 tick; lệch pha hàng
//    (x.0,x.1) trúng 400/885, pha (x.1,x.2) trúng 784/885. ⚠ Pha hàng đo trên GC (tick 0,1) chart CORVEN;
//    mã khác chưa kiểm.
//    hàng: bid = tổng SellVolume, ask = tổng BuyVolume, vol = tổng Volume các mức trong hàng.
//    LUẬT HIỆN TẠI (2026-11-18, fit trên chart M5 của CORVEN ngày 18/11, xem research/corven_m5_2026-11-18/README.md):
//      bên áp đảo của hàng (bên có volume lớn hơn) phải thoả CẢ BA điều kiện:
//        (1) >= CellBigRatio (1,25) x mức trung bình volume mỗi hàng có giao dịch của 20 nến đã đóng liền trước (cần >= 5 nến);
//        (2) >= sàn nổ 9 hợp đồng;
//        (3) >= CellBigMinImbalance (3) x bên yếu (bên yếu bằng 0 thì qua; đặt 0 để tắt điều kiện này).
//      Điều kiện (3) loại các hàng cân bằng (vd 100 Bid x 101 Ask) mà CORVEN không đánh bóng. Màu: xanh khi Ask trội, đỏ khi Bid trội
//      (Side = +1 nếu ask > bid, ngược lại -1; sau điều kiện (3) hai bên không thể bằng nhau trừ khi tắt điều kiện, khi đó hoà tính là -1).
//      KHÔNG còn bóng vàng "cả hai bên đều lớn" (CORVEN không có). Bóng TÍM chỉ còn nghĩa stop hunt, do OrderFlowBubbles.cs tô.
//    Đo trên 27 nến M5 (12:15-14:25 UTC 18/11): CORVEN 24 bóng; luật cũ (1,3 x, sàn 9, không điều kiện (3)) ra 123 bóng, F1 0,16;
//    luật mới 17 bóng, F1 0,39 theo vị trí, 11/15 nến có bóng của CORVEN trùng. Mật độ 9 ngày M5: 2,87 -> 0,73 bóng/nến (CORVEN ~0,9).
//    Đánh đổi: so với các chấm M1 cũ của CORVEN (Meet 5-6/11), F1 giảm 0,835 -> 0,572. Người học chọn kiểu M5. Chỉ MỘT biểu đồ, 27 nến,
//    nguồn dữ liệu của CORVEN khác nguồn mình (delta lệch) nên khớp vị trí bị chặn trần. KHÔNG phải lợi thế đã kiểm định.
//    B = trung bình của N nến ĐÃ ĐÓNG TRƯỚC của "volume TB mỗi HÀNG có giao dịch" (cần >= 5 nến)
//    (Luật cũ 2026-11-12 có thêm màu tím/vàng khi bên yếu cũng vượt ngưỡng nổ — đã bỏ hẳn.)
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
        public int Side;        // +1 = buy (Ask) trội, -1 = sell (Bid) trội (hoà -> -1). Hit=false thì 0. Không còn bóng vàng/cân bằng.
        public double Mult;     // sideVol / B (0 nếu chưa có B)
        public double SizeFrac; // 0..1 (tỉ lệ so với bề ngang nến)
    }

    public static class CellBigLogic
    {
        public const int MinHistoryBars = 5;
        public const double SizeMinFrac = 0.45;   // cỡ ở ngưỡng
        public const double SizeFullMult = 6.0;   // từ tỉ lệ này trở lên = 100% bề ngang nến

        // minImbalance: bên áp đảo phải >= minImbalance x bên yếu (bên yếu 0 thì qua; <= 0 tắt điều kiện). Áp cho cả chế độ ngưỡng cố định.
        public static CellBigDecision Decide(double buy, double sell, double baseline, bool hasBaseline,
            double ratio, double minSide, double minImbalance, bool fixedMode, double fixedThreshold)
        {
            var d = new CellBigDecision();
            double side = Math.Max(buy, sell), weak = Math.Min(buy, sell);
            if (side <= 0) return d;
            d.Mult = hasBaseline && baseline > 0 ? side / baseline : 0;
            if (fixedMode) d.Hit = side >= fixedThreshold;
            else d.Hit = hasBaseline && baseline > 0 && side >= ratio * baseline;
            if (side < minSide) d.Hit = false;
            if (minImbalance > 0 && side < minImbalance * weak) d.Hit = false;
            if (!d.Hit) return d;
            d.Side = buy > sell ? 1 : -1;
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
