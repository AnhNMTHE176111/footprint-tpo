// ============================================================================
//  BenzoZones — phần còn dùng của kernel.py cho setup CORVEN: tách phiên, giờ "neo Mỹ" (sm), phase, trung vị cuốn chiếu.
// ============================================================================
//  GĐ3 (plan 10.7): cắt bỏ VA/IB/VWAP/chế độ M5/zigzag/BenzoRisk của 4 setup A/B/C/D cũ (git giữ lịch sử).
//  mbr do RangeLogic tính (trong CorvenMachine), medΔ do CorvenFeat tính — cùng quy ước kernel.
//  Chạy THEO DÒNG: engine gọi Push(idx, bar) đúng một lần cho mỗi nến ĐÃ ĐÓNG, theo thứ tự (cấm nhìn trước).
//  Giờ theo giờ VN (TzOffset) và "bù giờ Mỹ": khi Mỹ dùng giờ mùa đông (EST) mọi mốc neo Mỹ lùi +1h theo giờ VN.
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;

    public static class BenzoKernel
    {
        public const double Tick = 0.1;
        public const double GapMinutes = 30;          // khoảng trống > 30 phút ⇒ phiên mới
        public const int SmEuStart = 450, SmUsStart = 840, SmOffStart = 1380;

        /// <summary>Mỹ đang dùng giờ mùa hè (EDT): CN thứ 2 tháng 3 07:00 UTC → CN đầu tháng 11 06:00 UTC.</summary>
        public static bool UsDst(DateTime utc)
        {
            int y = utc.Year;
            var m8 = new DateTime(y, 3, 8, 0, 0, 0, DateTimeKind.Utc);
            int d = 8 + (7 - (int)m8.DayOfWeek) % 7;
            var n1 = new DateTime(y, 11, 1, 0, 0, 0, DateTimeKind.Utc);
            int e = 1 + (7 - (int)n1.DayOfWeek) % 7;
            var s = new DateTime(y, 3, d, 7, 0, 0, DateTimeKind.Utc);
            var z = new DateTime(y, 11, e, 6, 0, 0, DateTimeKind.Utc);
            return utc >= s && utc < z;
        }

        public static int Mod(int a, int m) => ((a % m) + m) % m;

        /// <summary>Phút kể từ 05:00 VN (đã bù giờ Mỹ).</summary>
        public static int SmOf(DateTime utc, int tzOffset, bool usShift = true)
        {
            int vm = Mod(utc.Hour * 60 + utc.Minute + tzOffset * 60, 1440);
            int adj = (usShift && !UsDst(utc)) ? Mod(vm - 60, 1440) : vm;
            return Mod(adj - 300, 1440);
        }

        public static string PhaseOf(int sm) => sm < SmEuStart ? "A" : sm < SmUsStart ? "EU" : sm < SmOffStart ? "US" : "OFF";

        /// <summary>Tên phiên tiếng Việt cho CSV/bảng: Á / Âu / Mỹ (04:00–05:00 VN tính Mỹ).</summary>
        public static string PhienVn(int sm) => sm < SmEuStart ? "Á" : sm < SmUsStart ? "Âu" : "Mỹ";

        /// <summary>Trung vị (cửa sổ n phần tử gần nhất, tính cả phần tử hiện tại; cần tối thiểu minPeriods) — = pandas rolling().median().</summary>
        public static double RollingMedian(List<double> src, int n = 50, int minPeriods = 10)
        {
            int cnt = Math.Min(n, src.Count);
            if (cnt < minPeriods) return double.NaN;
            var a = new double[cnt];
            for (int k = 0; k < cnt; k++) a[k] = src[src.Count - cnt + k];
            Array.Sort(a);
            return cnt % 2 == 1 ? a[cnt / 2] : 0.5 * (a[cnt / 2 - 1] + a[cnt / 2]);
        }
    }

    /// <summary>Tách phiên + giờ neo Mỹ theo dòng nến đã đóng.</summary>
    public sealed class BenzoZones
    {
        public int TzOffset = 7;
        public bool UsShift = true;

        public readonly List<BarData> Bars = new();
        private readonly List<int> _sess = new(), _posS = new(), _sm = new();

        public int SessionAt(int i) => _sess[i];
        public int PosInSessionAt(int i) => _posS[i];
        public int SmAt(int i) => _sm[i];

        public int Idx = -1;
        public bool NewSession;
        public int SessionNo = -1, SessionStartIdx;
        public int Sm;
        public string Phase = "OFF";

        public void Push(int idx, BarData bar)
        {
            if (idx != Bars.Count) throw new InvalidOperationException($"BenzoZones.Push phải tuần tự: nhận {idx}, mong {Bars.Count}");
            Bars.Add(bar);
            Idx = idx;
            bool first = idx == 0;
            double gap = first ? 0 : (bar.Time - Bars[idx - 1].Time).TotalMinutes;
            NewSession = first || gap > BenzoKernel.GapMinutes;
            if (NewSession) { SessionNo++; SessionStartIdx = idx; }
            Sm = BenzoKernel.SmOf(bar.Time, TzOffset, UsShift);
            Phase = BenzoKernel.PhaseOf(Sm);
            _sess.Add(SessionNo); _posS.Add(idx - SessionStartIdx); _sm.Add(Sm);
        }
    }
}
