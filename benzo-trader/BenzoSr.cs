// ============================================================================
//  BenzoSr — vùng thêm cho setup B (v2 + v3): HVN/POC/VAH/VAL ngày-tuần, đỉnh/đáy phiên trước (PDH/PDL), vùng Canh Lệnh (VCL)
// ============================================================================
//  Port của research/zones_b_v2.py (12 mức / 8 loại) + research/zones_b_v3.py (PDH/PDL + 14 cạnh VCL), plan B-v2 / B-v3.
//  Mức CỐ ĐỊNH (POC_D, VAH_D, VAL_D, HVN_D1..3, POC_W, HVN_W1..3, PDH, PDL): tính MỘT lần ở nến đầu phiên, chỉ từ phiên/tuần ĐÃ ĐÓNG.
//  Mức VCL: 7 khe theo mã vùng (eid), gán trực tuyến; VCL_Rk = cạnh DƯỚI (lo) của vùng ở khe k — chỉ giá đi LÊN tới nó (sell);
//  VCL_Sk = cạnh TRÊN (hi) — chỉ giá đi XUỐNG tới nó (buy). Khe phải giữ cùng một vùng ≥ 4 nến liên tiếp mới "ấm".
//  Lõi VCL dùng nguyên VclCore.cs của indicator "Vùng Canh Lệnh" (đã parity 100% với Python vcl5.py).
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using VungCanhLenhNs;

    /// <summary>Phiên ĐÃ ĐÓNG (đủ để tính vùng cho phiên sau).</summary>
    public sealed class SessRec
    {
        public int No, Week, Start, N;
        public double Vol, High = double.NegativeInfinity, Low = double.PositiveInfinity;
        public Dictionary<long, double> Prof;
    }

    public sealed class BenzoSr
    {
        // ---- hằng (khớp zones_b_v2/v3 + kernel.CONST) ----
        public const int HvnMax = 3, WeekLookback = 3, MinWeekSessions = 3;
        public const double HvnGate = 2.5, ThinFrac = 0.20;
        public const int VclSlots = 7, VclWarm = 4;
        public static readonly string[] FixedNames =
            { "POC_D", "VAH_D", "VAL_D", "HVN_D1", "HVN_D2", "HVN_D3", "POC_W", "HVN_W1", "HVN_W2", "HVN_W3", "PDH", "PDL" };
        public static int FixedIndex(string name) => Array.IndexOf(FixedNames, name);

        // ---- mức cố định của phiên hiện tại (NaN = không có) ----
        public readonly double[] Fx = new double[FixedNames.Length];

        private readonly List<SessRec> _hist = new();
        private SessRec _lastGood;                          // phiên đã đóng gần nhất có ≥ 300 nến + profile
        private readonly List<double> _goodVols = new();    // volume các phiên ≥ 300 nến (trung vị cho "phiên mỏng")

        public BenzoSr() { for (int k = 0; k < Fx.Length; k++) Fx[k] = double.NaN; InitSlots(); }

        // ================================================================ phiên
        public void CloseSession(SessRec r)
        {
            _hist.Add(r);
            if (r.N >= BenzoKernel.MinBarsProf && r.Prof.Count > 0) { _lastGood = r; _goodVols.Add(r.Vol); }
        }

        /// <summary>Gọi ở nến ĐẦU của phiên mới (week = số thứ tự tuần CME của phiên này). Tính lại 12 mức cố định.</summary>
        public void BeginSession(int week)
        {
            for (int k = 0; k < Fx.Length; k++) Fx[k] = double.NaN;
            // --- phiên hôm qua đủ nến: POC/VAH/VAL ngày, HVN ngày, PDH/PDL ---
            var q = _lastGood;
            if (q != null)
            {
                var (pr, w) = Rows(q.Prof);
                if (BenzoKernel.ValueArea(pr, w, out double poc, out double vah, out double val)) { Fx[0] = poc; Fx[1] = vah; Fx[2] = val; }
                var hd = Gated(FindHvn(pr, w));
                for (int k = 0; k < hd.Count && k < HvnMax; k++) Fx[3 + k] = hd[k];
                Fx[10] = q.High; Fx[11] = q.Low;
            }
            // --- HVN tuần: gộp các phiên ≥ 300 nến của tuần W−3..W−1 ---
            var wk = new List<SessRec>();
            foreach (var s in _hist)
                if (s.Week >= week - WeekLookback && s.Week <= week - 1 && s.N >= BenzoKernel.MinBarsProf && s.Prof.Count > 0) wk.Add(s);
            if (wk.Count > 0)
            {
                var (pr, w) = Rows(Aggregate(wk));
                var hw = Gated(FindHvn(pr, w));
                for (int k = 0; k < hw.Count && k < HvnMax; k++) Fx[7 + k] = hw[k];
            }
            // --- POC tuần: gộp các phiên ≥ 300 nến, không mỏng, của tuần W−1; cần ≥ 3 phiên ---
            double med = Median(_goodVols);
            var w1 = new List<SessRec>();
            foreach (var s in _hist)
                if (s.Week == week - 1 && s.N >= BenzoKernel.MinBarsProf && s.Prof.Count > 0 && !(s.Vol < ThinFrac * med)) w1.Add(s);
            if (w1.Count >= MinWeekSessions)
            {
                var (pr, w) = Rows(Aggregate(w1));
                if (BenzoKernel.ValueArea(pr, w, out double pocW, out _, out _)) Fx[6] = pocW;
            }
            // dọn bớt: chỉ cần các tuần ≥ week−3
            _hist.RemoveAll(s => s.Week < week - WeekLookback);
        }

        private static List<double> Gated(List<(double p, double r)> l)
        {
            var o = new List<double>();
            int take = Math.Min(HvnMax, l.Count);
            for (int k = 0; k < take; k++) if (l[k].r >= HvnGate) o.Add(l[k].p);
            return o;
        }

        private static (double[] pr, double[] w) Rows(Dictionary<long, double> prof)
        {
            var keys = prof.Keys.ToList(); keys.Sort();
            var pr = new double[keys.Count]; var w = new double[keys.Count];
            for (int k = 0; k < keys.Count; k++) { pr[k] = BenzoKernel.RowPrice(keys[k]); w[k] = prof[keys[k]]; }
            return (pr, w);
        }

        private static Dictionary<long, double> Aggregate(List<SessRec> parts)
        {
            var d = new Dictionary<long, double>();
            foreach (var s in parts) foreach (var kv in s.Prof) d[kv.Key] = (d.TryGetValue(kv.Key, out var a) ? a : 0) + kv.Value;
            return d;
        }

        public static double Median(List<double> v)
        {
            if (v.Count == 0) return 0;
            var a = v.OrderBy(x => x).ToArray();
            int n = a.Length;
            return n % 2 == 1 ? a[n / 2] : 0.5 * (a[n / 2 - 1] + a[n / 2]);
        }

        // ================================================================ HVN (port kernel.find_hvn)
        /// <summary>Đỉnh cục bộ của phân bố volume làm mượt ±5 hàng, giữ đỉnh ≥ 1,5 × trung bình, gộp đỉnh quá gần (giữ đỉnh mạnh hơn).
        /// Trả [(giá, tỉ lệ)] mạnh trước. Chạy trên các hàng ĐANG CÓ (không lấp hàng trống), như Python.</summary>
        public static List<(double p, double r)> FindHvn(double[] prices, double[] w)
        {
            const double tick = BenzoKernel.Tick; const int smooth = 5; const double minRatio = 1.5;
            int n = w.Length;
            var res = new List<(double p, double r)>();
            if (n < 3) return res;
            double sum = 0; for (int k = 0; k < n; k++) sum += w[k];
            double avg = sum / n;
            if (avg <= 0) return res;
            double minSep = Math.Min(120.0, Math.Max(20.0, (prices[n - 1] - prices[0]) / tick * 0.08));
            var cs = new double[n + 1];
            for (int k = 0; k < n; k++) cs[k + 1] = cs[k] + w[k];
            var sm = new double[n];
            for (int k = 0; k < n; k++)
            {
                int a = Math.Max(0, k - smooth), z = Math.Min(n - 1, k + smooth);
                sm[k] = (cs[z + 1] - cs[a]) / (z - a + 1);
            }
            var pk = new List<int>();
            for (int k = 1; k < n - 1; k++)
                if (sm[k] >= sm[k - 1] && sm[k] >= sm[k + 1] && sm[k] >= minRatio * avg) pk.Add(k);
            pk.Sort((x, y) => { int c = sm[y].CompareTo(sm[x]); return c != 0 ? c : x.CompareTo(y); });   // mạnh trước, hoà ⇒ hàng thấp trước (sắp ổn định)
            foreach (int j in pk)
            {
                bool ok = true;
                foreach (var e in res) if (!(Math.Abs(prices[j] - e.p) / tick >= minSep)) { ok = false; break; }
                if (ok) res.Add((prices[j], sm[j] / avg));
            }
            return res;
        }

        // ================================================================ VCL: 7 khe theo mã vùng
        /// <summary>Bật lõi VCL (tốn thêm CPU). Phải đặt TRƯỚC khi đẩy nến đầu tiên.</summary>
        public bool UseVcl;
        public VclCore Core;
        private readonly List<double>[] _lo = new List<double>[VclSlots], _hi = new List<double>[VclSlots];
        private readonly List<int>[] _run = new List<int>[VclSlots];
        private readonly int[] _holder = new int[VclSlots], _runNow = new int[VclSlots];
        private readonly Dictionary<int, int> _where = new();
        private int _nBars;

        private void InitSlots()
        {
            for (int k = 0; k < VclSlots; k++) { _lo[k] = new List<double>(); _hi[k] = new List<double>(); _run[k] = new List<int>(); _holder[k] = -1; }
        }

        /// <summary>Đẩy nến idx vào lõi VCL rồi gán khe. Gọi đúng một lần mỗi nến, theo thứ tự.</summary>
        public void PushVcl(int idx, BarData bar, IReadOnlyList<LevelVol> levels, int tzOffset, bool usShift)
        {
            if (!UseVcl || ManualSlots) return;
            if (Core == null) Core = new VclCore { TzOffset = tzOffset, UsShift = usShift };
            if (idx != _nBars) throw new InvalidOperationException($"BenzoSr.PushVcl phải tuần tự: nhận {idx}, mong {_nBars}");
            List<VLevel> lv = null;
            if (levels != null && levels.Count > 0) { lv = new List<VLevel>(levels.Count); foreach (var l in levels) lv.Add(new VLevel(l.Price, l.Vol)); }
            Core.Push(new VBar { Time = bar.Time, O = bar.O, H = bar.H, L = bar.L, C = bar.C, Vol = bar.Vol }, (IReadOnlyList<VLevel>)lv ?? Array.Empty<VLevel>());
            AssignSlots(Core.Display);
            _nBars++;
        }

        /// <summary>CHỈ cho test: tự nạp các khe VCL (không chạy lõi VCL); engine không bật UseVcl khi cờ này bật.</summary>
        internal bool ManualSlots = false;

        internal void AssignSlots(List<VZone> disp)
        {
            var cur = new HashSet<int>(); foreach (var z in disp) cur.Add(z.Id);
            for (int k = 0; k < VclSlots; k++)
                if (_holder[k] != -1 && !cur.Contains(_holder[k])) { _where.Remove(_holder[k]); _holder[k] = -1; _runNow[k] = 0; }
            var order = disp.OrderBy(z => z.Lo).ThenBy(z => z.Id).ToList();     // eid mới nhận khe trống nhỏ nhất theo thứ tự (lo tăng, eid tăng)
            foreach (var z in order)
            {
                if (_where.ContainsKey(z.Id)) continue;
                int k = Array.IndexOf(_holder, -1);
                if (k < 0) continue;                                              // > 7 vùng: bỏ qua (engine không bao giờ hiển thị quá 7)
                _holder[k] = z.Id; _runNow[k] = 0; _where[z.Id] = k;
            }
            var lo = new double[VclSlots]; var hi = new double[VclSlots]; var run = new int[VclSlots];
            for (int k = 0; k < VclSlots; k++) { lo[k] = double.NaN; hi[k] = double.NaN; }
            foreach (var z in disp)
            {
                if (!_where.TryGetValue(z.Id, out int k)) continue;
                _runNow[k]++;
                lo[k] = z.Lo; hi[k] = z.Hi; run[k] = _runNow[k];
            }
            for (int k = 0; k < VclSlots; k++) { _lo[k].Add(lo[k]); _hi[k].Add(hi[k]); _run[k].Add(run[k]); }
        }

        public double SlotLoAt(int slot, int bar) => _lo[slot] != null && bar >= 0 && bar < _lo[slot].Count ? _lo[slot][bar] : double.NaN;
        public double SlotHiAt(int slot, int bar) => _hi[slot] != null && bar >= 0 && bar < _hi[slot].Count ? _hi[slot][bar] : double.NaN;
        public int SlotRunAt(int slot, int bar) => _run[slot] != null && bar >= 0 && bar < _run[slot].Count ? _run[slot][bar] : 0;
    }

    /// <summary>Nhãn tiếng Việt ngắn của vùng B (hiện trên chart, trong lý do và tin Telegram). Tên mã (VWAP_W, VCL_S2...) vẫn ghi ở cột zone của CSV.</summary>
    public static class BenzoZoneNames
    {
        public static string Label(string zone)
        {
            if (string.IsNullOrEmpty(zone)) return "";
            switch (zone)
            {
                case "VWAP_W": return "VWAP tuần";
                case "VWAP_D": return "VWAP ngày";
                case "POC_D": return "POC ngày";
                case "VAH_D": return "VAH ngày";
                case "VAL_D": return "VAL ngày";
                case "POC_W": return "POC tuần";
                case "PDH": return "đỉnh phiên trước";
                case "PDL": return "đáy phiên trước";
            }
            if (zone.StartsWith("HVN_D") && zone.Length == 6) return "HVN ngày " + zone[5];
            if (zone.StartsWith("HVN_W") && zone.Length == 6) return "HVN tuần " + zone[5];
            if (zone.StartsWith("VCL_R")) return "VCL kháng cự (cạnh dưới)";
            if (zone.StartsWith("VCL_S")) return "VCL hỗ trợ (cạnh trên)";
            return zone;
        }
    }
}
