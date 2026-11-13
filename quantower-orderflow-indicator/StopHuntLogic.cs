// ============================================================================
//  Stop hunt theo định nghĩa của CORVEN — logic THUẦN (không phụ thuộc Quantower) để unit test.
//  Nguồn: research/RESEARCH-stophunt-corven-2026-11-12.md, bản mẫu research/stophunt_corven.py (chạy --spec).
//
//  stop hunt = giá QUÉT qua cạnh range quan trọng (>= 1 tick) + có bóng Ô Bid/Ask lớn (bất kỳ màu) trong chính nến quét
//              + FAIL BREAK (nến quét hoặc 1-2 nến kế đóng cửa quay lại trong mức). Dấu đặt ở nến fail break (lúc nến ĐÓNG).
//  Mốc = cạnh hộp range của HAI hộp (hợp): 20 và 60 nến đóng trước nến đang xét. Hộp hợp lệ khi: liên tục
//  (tt[i] - tt[i-N] <= 1,5 x N x chu kỳ nến), cao <= X x trung vị(high-low) của 100 nến đóng trước, mỗi cạnh có >= 2 lần chạm
//  (cụm nến chạm vùng 25% chiều cao hộp, hai cụm cách nhau >= 3 nến).
//  Cooldown 5 nến mỗi phía. Một mã cho cả hai phía: đáy = lật dấu giá (hi' = -low, lo' = -high, cl' = -close).
//  ⚠ ĐÂY LÀ DẤU ĐỂ ĐỌC CHART, KHÔNG PHẢI TÍN HIỆU VÀO LỆNH: sau phí 1 tick chưa có lợi thế (xem file research).
//  Chỉ dùng nến ĐÃ ĐÓNG: gọi OnBarClosed đúng 1 lần cho mỗi nến, theo thứ tự thời gian.
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    /// <summary>Một bóng Ô Bid/Ask lớn của nến (đã qua luật CellBigLogic).</summary>
    public struct ShCell
    {
        public double Centre;    // giá tâm bóng
        public double Bid, Ask;  // Bid = sell chủ động, Ask = buy chủ động trong hàng
        public int Side;         // +1 xanh (Ask trội), -1 đỏ (Bid trội), 0 tím
    }

    public sealed class StopHuntSettings
    {
        public int BoxSmall = 20;
        public int BoxLarge = 60;
        public double BoxMaxMult = 8;
        public int TolTicks = 3;
        public int ConfirmBars = 2;
        public int Cooldown = 5;
        public int MedianBars = 100;
        public double TouchZone = 0.25;
        public int MinTouches = 2;
        public double BarMinutes = 0;   // chu kỳ nến (phút); 0 = tự ước = khoảng cách dương nhỏ nhất giữa hai nến liền nhau đã thấy (chưa có -> 1)
    }

    public struct StopHuntSignal
    {
        public int SweepIdx;     // chỉ số (do người gọi cấp) của nến quét
        public int FailIdx;      // nến fail break = nến đang đóng
        public bool Top;         // true = quét đỉnh (sell kỳ vọng), false = quét đáy
        public double Level;     // mức bị quét (giá thật, không lật dấu)
        public int Colour;       // màu bóng mạnh nhất tại chỗ quét: +1 xanh, -1 đỏ, 0 tím
        public double Bid, Ask;  // Bid/Ask của bóng mạnh nhất
    }

    public sealed class StopHuntDetector
    {
        public const double Eps = 1e-9;
        private readonly StopHuntSettings _s;
        private readonly double _tick;

        private sealed class SideData
        {
            public readonly List<double> Hi = new List<double>(), Lo = new List<double>(), Cl = new List<double>();
            public readonly List<Pend> Pending = new List<Pend>();
            public long LastSignalPos = -1000000000L;
        }
        private sealed class Pend { public long Pos; public int Idx; public List<double> Levels; public ShCell[] Cells; }

        private readonly SideData _top = new SideData(), _bot = new SideData();
        private readonly List<long> _tt = new List<long>();   // phút (UTC) của từng nến đóng
        private long _estPeriod = long.MaxValue;               // ước chu kỳ nến (phút) khi BarMinutes = 0
        private long _pos;                                    // vị trí tuyệt đối của nến sắp thêm

        public StopHuntDetector(StopHuntSettings s, double tick) { _s = s ?? new StopHuntSettings(); _tick = tick; }

        public void Reset()
        {
            foreach (var sd in new[] { _top, _bot }) { sd.Hi.Clear(); sd.Lo.Clear(); sd.Cl.Clear(); sd.Pending.Clear(); sd.LastSignalPos = -1000000000L; }
            _tt.Clear(); _pos = 0; _estPeriod = long.MaxValue;
        }

        public static long ToMinutes(long ticks) => CellBigLogic.FloorDiv(ticks, TimeSpan.TicksPerMinute);

        /// <summary>Nạp 1 nến vừa ĐÓNG. cells = các bóng Ô lớn của nến (có thể null). Trả về các dấu stop hunt đặt tại nến này.</summary>
        public List<StopHuntSignal> OnBarClosed(int idx, double high, double low, double close, long timeMinutes, IList<ShCell> cells)
        {
            var res = new List<StopHuntSignal>();
            var cellArr = new ShCell[cells?.Count ?? 0];
            for (int k = 0; k < cellArr.Length; k++) cellArr[k] = cells[k];
            Side(true, _top, idx, high, low, close, timeMinutes, cellArr, res);
            Side(false, _bot, idx, -low, -high, -close, timeMinutes, cellArr, res);
            if (_tt.Count > 0) { long d = timeMinutes - _tt[_tt.Count - 1]; if (d > 0 && d < _estPeriod) _estPeriod = d; }
            _tt.Add(timeMinutes);
            _pos++;
            const int keep = 600;
            if (_tt.Count > 2 * keep)
            {
                int drop = _tt.Count - keep;
                _tt.RemoveRange(0, drop);
                foreach (var sd in new[] { _top, _bot }) { sd.Hi.RemoveRange(0, drop); sd.Lo.RemoveRange(0, drop); sd.Cl.RemoveRange(0, drop); }
            }
            return res;
        }

        private void Side(bool top, SideData sd, int idx, double hiS, double loS, double clS, long t, ShCell[] cells, List<StopHuntSignal> res)
        {
            double sgn = top ? 1.0 : -1.0;
            // 1) nến này có quét mốc nào không (chỉ dùng nến TRƯỚC nến này để dựng hộp)
            var levels = new List<double>();
            AddBoxLevel(sd, _s.BoxSmall, hiS, t, levels);
            if (_s.BoxLarge != _s.BoxSmall) AddBoxLevel(sd, _s.BoxLarge, hiS, t, levels);
            if (levels.Count > 0)
            {
                levels.Sort((a, b) => b.CompareTo(a));   // cao trước
                var uniq = new List<double>();
                foreach (var l in levels) if (uniq.Count == 0 || uniq[uniq.Count - 1] != l) uniq.Add(l);
                var ok = new List<double>();
                foreach (var l in uniq)
                    foreach (var c in cells)
                        if (sgn * c.Centre >= l - _s.TolTicks * _tick - Eps) { ok.Add(l); break; }
                if (ok.Count > 0) sd.Pending.Add(new Pend { Pos = _pos, Idx = idx, Levels = ok, Cells = cells });
            }
            // 2) thêm nến vào lịch sử rồi xét fail break
            sd.Hi.Add(hiS); sd.Lo.Add(loS); sd.Cl.Add(clS);
            for (int pi = 0; pi < sd.Pending.Count; pi++)
            {
                var p = sd.Pending[pi];
                double L = double.NaN;
                foreach (var l in p.Levels) if (clS <= l + Eps) { L = l; break; }   // mức CAO nhất đạt fail break
                if (double.IsNaN(L)) continue;
                sd.Pending.RemoveAt(pi); pi--;
                if (_pos - sd.LastSignalPos <= _s.Cooldown) continue;
                sd.LastSignalPos = _pos;
                // bóng mạnh nhất: cạnh >= mốc - tol, mạnh = max(Bid, Ask), hòa -> gần cực trị hơn
                bool have = false; ShCell best = default;
                foreach (var c in p.Cells)
                {
                    if (!(sgn * c.Centre >= L - _s.TolTicks * _tick - Eps)) continue;
                    double m = Math.Max(c.Bid, c.Ask);
                    if (!have || m > Math.Max(best.Bid, best.Ask) || (m == Math.Max(best.Bid, best.Ask) && sgn * c.Centre > sgn * best.Centre)) { best = c; have = true; }
                }
                res.Add(new StopHuntSignal { SweepIdx = p.Idx, FailIdx = idx, Top = top, Level = sgn * L, Colour = best.Side, Bid = best.Bid, Ask = best.Ask });
            }
            // hết hạn: nến quét + ConfirmBars đã qua
            sd.Pending.RemoveAll(p => _pos - p.Pos >= _s.ConfirmBars);
        }

        // hộp N nến đóng trước: nếu hợp lệ và nến hiện tại quét qua cạnh trên (>= 1 tick) thì thêm mức vào levels
        private void AddBoxLevel(SideData sd, int N, double curHi, long t, List<double> levels)
        {
            int n = sd.Hi.Count;
            if (n < N || n < _s.MedianBars) return;
            double top = double.NegativeInfinity;
            for (int k = n - N; k < n; k++) if (sd.Hi[k] > top) top = sd.Hi[k];
            if (!(curHi >= top + _tick - Eps)) return;
            double per = _s.BarMinutes > 0 ? _s.BarMinutes : (_estPeriod == long.MaxValue ? 1.0 : _estPeriod);
            if (!(t - _tt[n - N] <= N * per * 1.5)) return;
            double bot = double.PositiveInfinity;
            for (int k = n - N; k < n; k++) if (sd.Lo[k] < bot) bot = sd.Lo[k];
            double h = top - bot;
            var rg = new double[_s.MedianBars];
            for (int k = 0; k < rg.Length; k++) rg[k] = sd.Hi[n - rg.Length + k] - sd.Lo[n - rg.Length + k];
            Array.Sort(rg);
            double med = (rg.Length % 2 == 1) ? rg[rg.Length / 2] : (rg[rg.Length / 2 - 1] + rg[rg.Length / 2]) / 2.0;
            if (!(h <= _s.BoxMaxMult * med)) return;
            double zone = _s.TouchZone * h;
            if (Touches(sd.Hi, n - N, N, top - zone, true) < _s.MinTouches) return;
            if (Touches(sd.Lo, n - N, N, bot + zone, false) < _s.MinTouches) return;
            levels.Add(top);
        }

        // số cụm chạm: nến chạm (hi >= thr / lo <= thr), cụm mới khi 2 nến liền trước KHÔNG chạm
        private static int Touches(List<double> a, int from, int N, double thr, bool ge)
        {
            int cnt = 0; bool p1 = false, p2 = false;
            for (int k = 0; k < N; k++)
            {
                bool c = ge ? a[from + k] >= thr : a[from + k] <= thr;
                if (c && !p1 && !p2) cnt++;
                p2 = p1; p1 = c;
            }
            return cnt;
        }
    }
}
