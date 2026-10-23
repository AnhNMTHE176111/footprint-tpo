// ============================================================================
//  DeltaCore — lõi THUẦN (không phụ thuộc SDK Quantower) cho nến delta Ask/Bid
// ============================================================================
//  VÌ SAO CÓ FILE NÀY (sự cố 2026-10-23: "nến delta ở quá khứ chỉ còn vạch ngang"):
//  Đã đo trên 31 file xuất footprint (hơn 1,2 triệu nến): với mọi nến NẠP LẠI TỪ LỊCH SỬ,
//  Quantower trả MaxDelta/MinDelta = giá trị "mồi" (hoặc = đúng Delta) — tức là
//  KHÔNG có đỉnh/đáy delta chạy trong nến. Chỉ nến hình thành TRỰC TIẾP lúc indicator
//  đang gắn (vd 60 nến 29/07 16:33–17:35, 56 nến 14/09 15:09–16:04) mới có số thật.
//  Delta cuối nến (Total.Delta) thì luôn đủ. Mã cũ coi Max<Min là "nến phẳng" nên vẽ
//  O=H=L=C = một vạch ngang, và KHÔNG báo gì.
//
//  CÁCH FIX (3 nguồn, ưu tiên từ trên xuống, nến luôn ghi rõ lấy từ nguồn nào):
//    1. Quantower  — chỉ khi MaxDelta/MinDelta là số THẬT (không phải mồi).
//    2. Tick       — dựng lại delta chạy từ tick lịch sử (AggressorFlag), CHỈ nhận khi
//                    delta cuối nến dựng lại KHỚP Total.Delta của Quantower (kiểm chéo).
//    3. Không có   — vẽ thân (0 → delta) không râu, đánh dấu viền rỗng + đếm trên màn hình.
//  Không bao giờ tự bịa râu.
// ============================================================================
namespace AskBidDeltaCore
{
    using System;
    using System.Collections.Generic;

    public enum RangeSrc : byte { None = 0, Quantower = 1, Ticks = 2 }

    /// <summary>Đường delta chạy của MỘT nến dựng từ tick, tính từ 0 ở đầu nến (Hi ≥ 0 ≥ Lo).</summary>
    public struct TickBar
    {
        public double End, Hi, Lo;
        public int N;
        public double UnclassVol;   // khối lượng tick không biết bên chủ động (không tính vào delta)
    }

    /// <summary>Dữ liệu thô của một nến do indicator đọc từ Quantower.</summary>
    public struct RawBar
    {
        public long TimeUtcTicks;
        public bool HasVa;          // có VolumeAnalysisData.Total
        public double Volume;
        public int Trades;
        public double Delta, QtMax, QtMin;
    }

    /// <summary>Một nến delta đã dựng (Open/High/Low/Close theo trục delta; cộng dồn hoặc từng nến).</summary>
    public struct CumBar
    {
        public long TimeUtcTicks;
        public double Open, High, Low, Close, Delta;
        public RangeSrc Src;
        public bool Empty;          // không có dữ liệu (không vẽ)
    }

    public static class DeltaCore
    {
        public const double PrimerGuard = 1e12;

        /// <summary>
        /// MaxDelta/MinDelta của Quantower có phải số THẬT không? Mồi = double.MinValue/MaxValue
        /// hoặc (sau khi export vá) Max = Min = Delta trên nến có ≥ 2 giao dịch.
        /// </summary>
        public static bool QtRangeReal(double delta, double max, double min, int trades)
        {
            if (!double.IsFinite(max) || !double.IsFinite(min) || !double.IsFinite(delta)) return false;
            if (Math.Abs(max) >= PrimerGuard || Math.Abs(min) >= PrimerGuard) return false;
            if (max < min) return false;
            const double eps = 1e-9;
            if (max < delta - eps || min > delta + eps) return false;       // đỉnh/đáy phải bao được delta cuối
            if (trades > 1 && max == delta && min == delta) return false;   // phẳng bất khả thi khi ≥ 2 giao dịch
            return true;
        }

        /// <summary>Chọn đỉnh/đáy delta chạy cho một nến (tương đối so với Open). Trả nguồn đã dùng.</summary>
        public static RangeSrc ResolveRange(double delta, bool qtReal, double qtMax, double qtMin,
                                            bool hasTick, TickBar tick, out double hi, out double lo)
        {
            if (qtReal)
            {
                hi = Math.Max(qtMax, Math.Max(0.0, delta));
                lo = Math.Min(qtMin, Math.Min(0.0, delta));
                return RangeSrc.Quantower;
            }
            if (hasTick && tick.N > 0 && Math.Abs(tick.End - delta) <= Math.Max(1.0, Math.Abs(delta) * 0.005))
            {
                hi = Math.Max(tick.Hi, Math.Max(0.0, delta));
                lo = Math.Min(tick.Lo, Math.Min(0.0, delta));
                return RangeSrc.Ticks;
            }
            hi = Math.Max(0.0, delta);
            lo = Math.Min(0.0, delta);
            return RangeSrc.None;
        }

        /// <summary>Khoá "ngày giao dịch": đổi giá trị khi qua mốc reset (phút trong ngày, giờ local = UTC + tz).</summary>
        public static long DayKey(long utcTicks, int tzHours, int resetMinutes)
        {
            long local = utcTicks + tzHours * TimeSpan.TicksPerHour - resetMinutes * TimeSpan.TicksPerMinute;
            long d = local / TimeSpan.TicksPerDay;
            if (local < 0 && local % TimeSpan.TicksPerDay != 0) d--;
            return d;
        }

        /// <summary>
        /// Dựng chuỗi nến delta. perBar=true: mỗi nến mở từ 0 (kiểu "Ask/Bid Volume Difference Bars");
        /// perBar=false: Open nến này = Close nến trước, đặt lại về 0 khi qua mốc reset hằng ngày
        /// (resetDaily=false: không bao giờ đặt lại).
        /// </summary>
        public static CumBar[] BuildChain(IList<RawBar> raw, IDictionary<long, TickBar> ticks, bool perBar,
                                          bool resetDaily, int tzHours, int resetMinutes)
        {
            var res = new CumBar[raw.Count];
            double cum = 0; long prevKey = long.MinValue;
            for (int i = 0; i < raw.Count; i++)
            {
                var r = raw[i];
                long key = resetDaily ? DayKey(r.TimeUtcTicks, tzHours, resetMinutes) : 0;
                if (perBar || key != prevKey) cum = 0;
                prevKey = key;
                var c = new CumBar { TimeUtcTicks = r.TimeUtcTicks };
                if (!r.HasVa || r.Volume <= 0)
                {
                    c.Empty = true; c.Open = c.High = c.Low = c.Close = cum;
                    res[i] = c; continue;
                }
                bool qtReal = QtRangeReal(r.Delta, r.QtMax, r.QtMin, r.Trades);
                TickBar tb = default; bool hasTick = ticks != null && ticks.TryGetValue(r.TimeUtcTicks, out tb);
                c.Src = ResolveRange(r.Delta, qtReal, r.QtMax, r.QtMin, hasTick, tb, out double hi, out double lo);
                c.Delta = r.Delta;
                c.Open = cum; c.Close = cum + r.Delta;
                c.High = cum + hi; c.Low = cum + lo;
                cum = c.Close;
                res[i] = c;
            }
            return res;
        }
    }

    /// <summary>
    /// Dựng delta chạy của từng nến từ tick sắp theo thời gian. Có thể nạp theo nhiều đợt liên tiếp:
    /// trạng thái nến đang dở được giữ qua đợt.
    /// </summary>
    public sealed class TickAccumulator
    {
        private readonly long[] _starts;          // thời điểm bắt đầu từng nến, tăng dần
        private int _bi = -1;
        private double _run, _hi, _lo, _unclass;
        private int _n;
        public readonly Dictionary<long, TickBar> Result = new Dictionary<long, TickBar>();
        public long Fed, OutOfOrder, Unclassified;

        public TickAccumulator(long[] barStarts) { _starts = barStarts; }

        /// <param name="sign">+1 buy chủ động, −1 sell chủ động, 0 không biết.</param>
        public void Feed(long timeTicks, double volume, int sign)
        {
            if (_starts.Length == 0 || timeTicks < _starts[0]) return;
            int nb = _bi < 0 ? 0 : _bi;
            if (_bi >= 0 && timeTicks < _starts[_bi]) { OutOfOrder++; return; }
            while (nb + 1 < _starts.Length && _starts[nb + 1] <= timeTicks) nb++;
            if (nb != _bi)
            {
                Flush();
                _bi = nb; _run = _hi = _lo = _unclass = 0; _n = 0;
            }
            Fed++;
            if (sign == 0) { _unclass += volume; Unclassified++; }
            else
            {
                _run += sign * volume;
                if (_run > _hi) _hi = _run;
                if (_run < _lo) _lo = _run;
            }
            _n++;
        }

        /// <summary>Ghi trạng thái nến hiện tại vào Result (không đặt lại; gọi nhiều lần được).</summary>
        public void Flush()
        {
            if (_bi >= 0 && _n > 0)
                Result[_starts[_bi]] = new TickBar { End = _run, Hi = _hi, Lo = _lo, N = _n, UnclassVol = _unclass };
        }
    }
}
