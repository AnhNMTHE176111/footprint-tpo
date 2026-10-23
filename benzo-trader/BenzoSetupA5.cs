// ============================================================================
//  BenzoSetupA5 — setup A "Phá hồi v5" (= A-v4 + các vùng hỗ trợ/kháng cự của Vùng Canh Lệnh)
// ============================================================================
//  Port C# của research/setup_a_v5.py::detect5 (logic 'mom', ban=False, after_inside=False, real_break=True,
//  vcl_slfar=True, lock=True, drop_overlap=False) + research/zones_a_v4.py + kernel.find_hvn.
//  Nguồn chân lý = Python: C# phải ra ĐÚNG từng tín hiệu (xem research/parity_a_v5.py, report/PARITY-A5.md).
//
//  ⚠ TRUNG THỰC: A-v5 CHƯA CÓ LỢI THẾ ĐO ĐƯỢC (R trung bình −0,18/lệnh trên 90 ngày; không đạt tiêu chí T1; 6 phép
//  đối chứng đều "không hơn" vào lệnh bừa). Bản này để CHẠY THỬ trên chart và thu số thật, không phải khuyến nghị.
//
//  File MỚI, không sửa BenzoZones/BenzoDetectors/BenzoSr. Mọi trạng thái nằm trong DetectorA5: engine gọi Observe cho
//  MỌI nến đã đóng (kể cả khi có lệnh mở / setup tắt / nến đã niêm phong) nên trạng thái luôn liên tục.
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.Linq;
    using VclNs = VungCanhLenhNs;

    // ---------------------------------------------------------------- hằng số (chỉ trong code, không có trong Settings)
    public static class A5Const
    {
        public const double Rr = 3.0, ZoneHalf = 1.0, DMin = 2.0, CancelDepth = ZoneHalf;
        public const int NMin = 3, LegLookback = 60, THoi = 30, Warm = 30;
        public const int HvnMax = 3, HvnSmooth = 5, WeekLookback = 3, MinBarsProf = 300;
        public const double HvnGate = 2.5, HvnMinRatio = 1.5, HvnBandFrac = 0.90, HvnBandMax = 2.0;
        public const int RankVwapW = 1, RankVwapD = 2, RankHvnW = 3, RankHvnD = 4, RankVahVal = 5, RankVcl = 7;
        /// <summary>10 vùng v4 theo ĐÚNG thứ tự zones_a_v4.build_zones('new').</summary>
        public static readonly string[] V4Names = { "VWAP_W", "VWAP_D", "HVN_W1", "HVN_W2", "HVN_W3", "HVN_D1", "HVN_D2", "HVN_D3", "VAH_D", "VAL_D" };
        public static readonly int[] V4Rank = { RankVwapW, RankVwapD, RankHvnW, RankHvnW, RankHvnW, RankHvnD, RankHvnD, RankHvnD, RankVahVal, RankVahVal };
        public static bool V4Dyn(int order) => order <= 1;
        public static bool V4Band(int order) => order >= 2 && order <= 4;     // chỉ HVN tuần là dải
        public const int VclBase = 1 << 20;                                   // mã vùng khoá: v4 = Order (0..9); VCL = VclBase + eid
    }

    // ---------------------------------------------------------------- toán HVN (port nguyên kernel.py)
    public static class HvnMath
    {
        /// <summary>= np.round(row × 0,2, 6) (làm tròn nửa về chẵn) — giống Profiles.row_price / Vcl.RowPrice.</summary>
        public static double RowPricePy(long row) => Math.Round(row * BenzoKernel.RowStep * 1e6, MidpointRounding.ToEven) / 1e6;

        /// <summary>kernel.find_hvn (tick 0,1 · làm mượt ±5 hàng · tỉ lệ tối thiểu 1,5). Trả [(giá, tỉ lệ)] mạnh trước.
        /// rowsAsc phải tăng dần.</summary>
        public static List<(double price, double ratio)> FindHvn(long[] rowsAsc, double[] vol)
        {
            var res = new List<(double, double)>();
            int n = vol.Length;
            if (n < 3) return res;
            double tot = 0; for (int k = 0; k < n; k++) tot += vol[k];
            double avg = tot / n;
            if (avg <= 0) return res;
            var p = new double[n];
            for (int k = 0; k < n; k++) p[k] = RowPricePy(rowsAsc[k]);
            double tick = BenzoKernel.Tick;
            double minSep = Math.Min(120.0, Math.Max(20.0, (p[n - 1] - p[0]) / tick * 0.08));
            // làm mượt bằng tổng tích luỹ, đúng như kernel._smooth
            var cs = new double[n + 1];
            for (int k = 0; k < n; k++) cs[k + 1] = cs[k] + vol[k];
            var sm = new double[n];
            for (int i = 0; i < n; i++)
            {
                int a = Math.Max(0, i - A5Const.HvnSmooth), z = Math.Min(n - 1, i + A5Const.HvnSmooth);
                sm[i] = (cs[z + 1] - cs[a]) / (z - a + 1);
            }
            var pk = new List<int>();
            for (int i = 1; i <= n - 2; i++)
                if (sm[i] >= sm[i - 1] && sm[i] >= sm[i + 1] && sm[i] >= A5Const.HvnMinRatio * avg) pk.Add(i);
            var ordered = pk.OrderByDescending(j => sm[j]).ToList();      // OrderBy của LINQ ổn định = argsort(kind='stable')
            foreach (int j in ordered)
            {
                bool ok = true;
                foreach (var (pp, _) in res) if (!(Math.Abs(p[j] - pp) / tick >= minSep)) { ok = false; break; }
                if (ok) res.Add((p[j], sm[j] / avg));
            }
            return res;
        }

        /// <summary>FindHvn trên một profile (hàng → volume), rồi cắt 3 đầu RỒI giữ tỉ lệ ≥ 2,5 (thứ tự: cắt trước, lọc sau — như kernel).</summary>
        public static List<(double price, double ratio)> TopHvn(Dictionary<long, double> prof)
        {
            var rows = prof.Keys.OrderBy(x => x).ToArray();
            var vol = new double[rows.Length];
            for (int k = 0; k < rows.Length; k++) vol[k] = prof[rows[k]];
            var all = FindHvn(rows, vol);
            var res = new List<(double, double)>();
            for (int k = 0; k < all.Count && k < A5Const.HvnMax; k++) if (all[k].ratio >= A5Const.HvnGate) res.Add(all[k]);
            return res;
        }

        /// <summary>zones_a_v4.peak_sharpness: từ hàng đỉnh nới lên/xuống chừng nào hàng kề TỒN TẠI và volume ≥ 90% hàng đỉnh.</summary>
        public static (double lo, double hi) PeakSharpness(Dictionary<long, double> prof, double peak)
        {
            long pr = (long)Math.Round(peak / BenzoKernel.RowStep, MidpointRounding.ToEven);
            if (!prof.TryGetValue(pr, out double pv)) return (peak, peak);
            double thr = A5Const.HvnBandFrac * pv;
            long lo = pr, hi = pr;
            while (prof.TryGetValue(lo - 1, out double a) && a >= thr) lo--;
            while (prof.TryGetValue(hi + 1, out double b) && b >= thr) hi++;
            return (Math.Round(lo * BenzoKernel.RowStep * 1e6, MidpointRounding.ToEven) / 1e6,
                    Math.Round(hi * BenzoKernel.RowStep * 1e6, MidpointRounding.ToEven) / 1e6);
        }

        /// <summary>Kẹp dải về rộng ≤ 2,0 giá đối xứng quanh đỉnh.</summary>
        public static (double lo, double hi) ClampBand(double lo, double hi, double peak)
        {
            double h = A5Const.HvnBandMax / 2.0;
            return (Math.Max(lo, peak - h), Math.Min(hi, peak + h));
        }
    }

    // ---------------------------------------------------------------- sổ HVN theo phiên
    /// <summary>Mức của một phiên: HVN tuần (dải đã kẹp) + HVN ngày (điểm) + VAH/VAL hôm qua (lấy từ BenzoZones).</summary>
    public sealed class A5Levels
    {
        public List<(double p, double lo, double hi)> HvnW = new();
        public List<double> HvnD = new();
        public double Vah = double.NaN, Val = double.NaN;
    }

    /// <summary>
    /// Sổ HVN: gom profile volume từng phiên (chỉ từ mức giá, như Python), chốt phiên khi sang phiên mới và tính HVN cho phiên mới
    /// chỉ từ phiên/tuần ĐÃ ĐÓNG (không nhìn trước). HVN ngày = phiên đã đóng gần nhất có ≥ 300 nến; HVN tuần = gộp các phiên đã đóng
    /// của 3 tuần CME trước (tuần W−3..W−1) có ≥ 300 nến. Không xét chỗ nối hợp đồng (file GCZ26 không có).
    /// </summary>
    public sealed class HvnBook
    {
        private sealed class Sess { public int Week, N; public Dictionary<long, double> Prof = new(); }
        private readonly List<Sess> _closed = new();
        private Sess _cur, _q;
        private int _week = -1, _n;
        private DateTime _prevTime;
        public List<double> HvnD = new();
        public List<(double p, double lo, double hi)> HvnW = new();
        public int ClosedCount => _closed.Count;

        public void Step(int i, BarData bar, IReadOnlyList<LevelVol> lv, bool newSession)
        {
            if (_n == 0) _week = 0;
            else if ((bar.Time - _prevTime).TotalMinutes > BenzoKernel.WeekGapMinutes) _week++;
            _prevTime = bar.Time; _n++;
            if (newSession || _cur == null)
            {
                if (_cur != null) _closed.Add(_cur);
                _cur = new Sess { Week = _week };
                Compute(_week);
            }
            if (lv != null)
                for (int k = 0; k < lv.Count; k++)
                {
                    long row = (long)Math.Round(lv[k].Price / BenzoKernel.RowStep, MidpointRounding.ToEven);
                    _cur.Prof[row] = (_cur.Prof.TryGetValue(row, out var a) ? a : 0) + lv[k].Vol;
                }
            _cur.N++;
        }

        private void Compute(int w)
        {
            // HVN ngày: phiên đã đóng gần nhất đủ nến + có profile
            _q = null;
            for (int k = _closed.Count - 1; k >= 0; k--)
                if (_closed[k].N >= A5Const.MinBarsProf && _closed[k].Prof.Count > 0) { _q = _closed[k]; break; }
            HvnD = new List<double>();
            if (_q != null) foreach (var (p, _) in HvnMath.TopHvn(_q.Prof)) HvnD.Add(p);
            // HVN tuần: gộp phiên đã đóng của tuần w−3..w−1
            var agg = new Dictionary<long, double>();
            bool any = false;
            foreach (var s in _closed)
                if (s.Week >= w - A5Const.WeekLookback && s.Week <= w - 1 && s.N >= A5Const.MinBarsProf && s.Prof.Count > 0)
                {
                    any = true;
                    foreach (var kv in s.Prof) agg[kv.Key] = (agg.TryGetValue(kv.Key, out var a) ? a : 0) + kv.Value;
                }
            HvnW = new List<(double, double, double)>();
            if (any)
                foreach (var (p, _) in HvnMath.TopHvn(agg))
                {
                    var (lr, hr) = HvnMath.PeakSharpness(agg, p);
                    var (lo, hi) = HvnMath.ClampBand(lr, hr, p);
                    HvnW.Add((p, lo, hi));
                }
            // tỉa: bỏ phiên quá 3 tuần, nhưng luôn giữ phiên q đang dùng
            _closed.RemoveAll(s => s.Week < w - A5Const.WeekLookback && !ReferenceEquals(s, _q));
        }
    }

    // ---------------------------------------------------------------- nguồn VCL (có thể thay bằng giả trong test)
    public interface IA5VclSource
    {
        /// <summary>Đẩy nến i (tuần tự); sau đó Display = bộ vùng đang hiển thị tại nến i.</summary>
        void Push(int i, BarData b, IReadOnlyList<LevelVol> lv);
        IReadOnlyList<(int Id, double Lo, double Hi)> Display { get; }
    }

    /// <summary>Bọc VclCore.cs của indicator Vùng Canh Lệnh (nối nguồn vào bản build Benzo, không sửa).</summary>
    public sealed class VclCoreSource : IA5VclSource
    {
        public readonly VclNs.VclCore Core;
        private List<(int, double, double)> _disp = new();
        public VclCoreSource(int tzOffset = 7, bool usShift = true) { Core = new VclNs.VclCore { TzOffset = tzOffset, UsShift = usShift }; }
        public IReadOnlyList<(int Id, double Lo, double Hi)> Display => _disp;
        public void Push(int i, BarData b, IReadOnlyList<LevelVol> lv)
        {
            if (i != Core.Bars.Count) throw new InvalidOperationException($"VclCoreSource.Push phải tuần tự: nhận {i}, mong {Core.Bars.Count}");
            List<VclNs.VLevel> vl = null;
            if (lv != null && lv.Count > 0) { vl = new List<VclNs.VLevel>(lv.Count); for (int k = 0; k < lv.Count; k++) vl.Add(new VclNs.VLevel(lv[k].Price, lv[k].Vol)); }
            Core.Push(new VclNs.VBar { Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol },
                      (IReadOnlyList<VclNs.VLevel>)vl ?? Array.Empty<VclNs.VLevel>());
            if (Core.Idx != i) throw new InvalidOperationException($"VclCore.Idx {Core.Idx} khác nến vừa đẩy {i}");
            var d = new List<(int, double, double)>(Core.Display.Count);
            foreach (var z in Core.Display) d.Add((z.Id, z.Lo, z.Hi));
            _disp = d;
        }
    }

    // ---------------------------------------------------------------- dữ liệu ra
    /// <summary>Thông tin của tín hiệu vừa phát (để ReplayCsv/đối chiếu Python). Ghi TRƯỚC khi đặt lại cực trị.</summary>
    public sealed class A5Info
    {
        public int Side, P0, PkPos, Npb, BrkNo, EntNo;
        public double E, ZLo, ZHi, L, Pbmax, PkVal, Dist;
        public string Zone = "";
    }

    /// <summary>Một dòng nhật ký trạng thái kết thúc (đối chiếu states_log của Python).</summary>
    public sealed class A5StateLog
    {
        public string Zone = "", Why = "";
        public int S, P0, PkPos, BrkNo, NEnt;
        public double PkVal, E;
        public bool Armed;
    }

    /// <summary>Ảnh chụp bất biến của một trạng thái "đang canh" (cho vẽ). Lo/Hi/E là giá trị TẠI NẾN CUỐI.</summary>
    public sealed class A5Watch
    {
        public string Name = "";          // tên Python: VWAP_D, HVN_W1, VCL_12...
        public bool IsVcl, IsBand, IsDyn;
        public int Side, P0, PkPos, Npb, Left, BrkNo, NEnt;
        public double E, Lo, Hi, PkVal, L, Pbmax, Dist;
        public bool Near, OkBar, TradeOpen;
        public DateTime P0Time, PkTime;   // giờ mở nến phá (P0) và nến cực trị (PkPos) — để vẽ
        public int Status;                // 1 hồi quá mạnh · 2 đà vừa dừng · 3 chờ giá hồi về vùng · 4 giá đang ở vùng, chờ nến xác nhận
        public string Label = "";
    }

    /// <summary>Ảnh chụp trạng thái để test/gỡ lỗi (không dùng khi vẽ).</summary>
    public sealed class A5StateView
    {
        public string Name = "";
        public int S, P0, PkPos, BrkNo, NEnt, KPos;
        public double E, ZLo, ZHi, L, PkVal, Pbmax;
        public bool Armed;
    }

    // ---------------------------------------------------------------- chữ tiếng Việt (hàm thuần, test được)
    public static class A5Text
    {
        public static string ZoneVn(string name)
        {
            if (name.StartsWith("VCL")) return "vùng S/R";
            switch (name)
            {
                case "VWAP_W": return "VWAP tuần";
                case "VWAP_D": return "VWAP ngày";
                case "VAH_D": return "VAH hôm qua";
                case "VAL_D": return "VAL hôm qua";
            }
            if (name.StartsWith("HVN_W")) return "HVN tuần " + name.Substring(5);
            if (name.StartsWith("HVN_D")) return "HVN ngày " + name.Substring(5);
            return name;
        }

        /// <summary>Điểm ⇒ "4170,4"; dải ⇒ "4168,2–4170,4".</summary>
        public static string Price(bool band, double lo, double hi, double e) =>
            band ? BenzoCore.Num(lo) + "–" + BenzoCore.Num(hi) : BenzoCore.Num(e);

        public static string Dl(double v) => (v >= 0 ? "+" : "−") + BenzoCore.Num(Math.Abs(Math.Round(v)), "0");

        /// <summary>Trạng thái theo thứ tự ưu tiên của plan 4.2: 1 hồi quá mạnh · 2 đà vừa dừng · 3 chờ giá hồi về vùng · 4 giá đang ở vùng.</summary>
        public static int Status(A5Watch w) => w.Pbmax >= w.L ? 1 : w.Npb < 3 ? 2 : !w.Near ? 3 : 4;

        /// <summary>Nhãn 1 dòng của vùng A đang canh (plan mục 4.2).</summary>
        public static string Label(A5Watch w)
        {
            string side = w.Side > 0 ? "MUA" : "BÁN";
            string pk = w.Side > 0 ? "đỉnh" : "đáy";
            int st = Status(w);
            bool strong = st == 1;
            string status = st == 1 ? $"hồi quá mạnh, chờ {pk} mới"
                          : st == 2 ? $"đà vừa dừng, hồi {w.Npb}/3 nến"
                          : st == 3 ? "chờ giá hồi về vùng"
                          : "giá đang ở vùng, chờ nến xác nhận";
            string s = $"A chờ {side} · {ZoneVn(w.Name)} {Price(w.IsBand, w.Lo, w.Hi, w.E)}{(w.IsDyn && w.Name.StartsWith("VWAP") ? " (động)" : "")}"
                     + $" · {pk} {BenzoCore.Num(w.PkVal)} · {status}";
            if (!strong) s += $" · còn {w.Left}′";
            if (!w.OkBar) s += " · đang giờ không vào lệnh";
            if (w.TradeOpen) s += " · đang có lệnh mở";
            return s;
        }
    }

    // ---------------------------------------------------------------- DETECTOR
    public sealed class DetectorA5 : DetectorBase
    {
        public override char Setup => 'A';

        public readonly bool UseVcl;
        /// <summary>true (mặc định, như Python). Chỉ tắt trong test để cô lập các vùng khác khỏi VWAP.</summary>
        public bool UseVwap = true;
        /// <summary>true = bản live (khung 19:20–20:30 VN không tiêu đếm/khoá mức). ReplayCsv đặt false khi so với Python vblock=False.</summary>
        public bool VirtualOpenBlock = true;
        public A5Info LastInfo;                       // chỉ ghi khi có tín hiệu
        public List<A5StateLog> StateLog;             // null = không ghi (live không tốn bộ nhớ)
        public A5Levels CurrentLevels { get; private set; } = new A5Levels();

        private IA5VclSource _vcl;
        private BenzoZones _zref;      // BenzoZones của engine (cùng một đối tượng suốt đời) — để Watch đọc VWAP hiện tại
        private readonly HvnBook _book = new HvnBook();
        private int _lastIdx = -1;
        private bool _okLast;

        private sealed class A5St
        {
            public int Zid, S, P0, PkPos, BrkNo, KPos, NEnt, Order, Eid;
            public bool IsVcl, Armed;
            public string Name = "";
            public double E, ZLo, ZHi, L, PkVal, Pbmax;
        }
        private sealed class EidHist
        {
            public int First;
            public readonly List<double> Lo = new(), Hi = new();
            public int Last => First + Lo.Count - 1;
        }

        private readonly Dictionary<(int zid, int s), A5St> _st = new();
        private readonly Dictionary<(string name, int s), int> _count = new(), _bcount = new();
        private readonly Dictionary<int, List<double>> _sigLog = new();   // chiều → E của các tín hiệu ĐÃ GHI (khoá mức)
        private readonly Dictionary<int, EidHist> _hist = new();

        public DetectorA5(bool useVcl = true, IA5VclSource vcl = null)
        {
            UseVcl = useVcl; _vcl = useVcl ? vcl : null;
        }

        // ------------------------------------------------------------ giá vùng
        private static bool Nan(double v) => double.IsNaN(v);

        /// <summary>(lo, hi) của vùng v4 tại nến k (NaN = không có). Mọi vùng cố định lấy theo phiên HIỆN TẠI (k luôn cùng phiên với nến đang xét).</summary>
        private void V4At(BenzoZones z, int order, int k, out double lo, out double hi)
        {
            lo = hi = double.NaN;
            switch (order)
            {
                case 0: if (UseVwap && z.PosInWeekAt(k) >= A5Const.Warm) lo = hi = z.VwapWAt(k); break;
                case 1: if (UseVwap && z.PosInSessionAt(k) >= A5Const.Warm) lo = hi = z.VwapDAt(k); break;
                case 2: case 3: case 4:
                    {
                        int j = order - 2;
                        if (j < _book.HvnW.Count) { lo = _book.HvnW[j].lo; hi = _book.HvnW[j].hi; }
                        break;
                    }
                case 5: case 6: case 7:
                    {
                        int j = order - 5;
                        if (j < _book.HvnD.Count) lo = hi = _book.HvnD[j];
                        break;
                    }
                case 8: lo = hi = z.YdVah; break;
                case 9: lo = hi = z.YdVal; break;
            }
        }

        /// <summary>Giá "thô" của vùng động tại nến k (VWAP chưa áp Warm) — chỉ dùng để lùi tìm chân cú phá.</summary>
        private static double V4Raw(BenzoZones z, int order, int k) => order == 0 ? z.VwapWAt(k) : z.VwapDAt(k);

        private bool VclAt(int eid, int k, out double lo, out double hi)
        {
            lo = hi = double.NaN;
            if (!_hist.TryGetValue(eid, out var h)) return false;
            int j = k - h.First;
            if (j < 0 || j >= h.Lo.Count) return false;
            lo = h.Lo[j]; hi = h.Hi[j];
            return true;
        }

        private void UpdateHist(int i)
        {
            foreach (var (id, lo, hi) in _vcl.Display)
            {
                if (!_hist.TryGetValue(id, out var h) || h.First + h.Lo.Count != i)
                {
                    h = new EidHist { First = i };      // eid mới (hoặc đứt quãng: coi như vùng mới, lịch sử bắt đầu lại)
                    _hist[id] = h;
                }
                h.Lo.Add(lo); h.Hi.Add(hi);
            }
        }

        private void PruneHist(int i)
        {
            List<int> dead = null;
            foreach (var kv in _hist) if (kv.Value.Last < i - 1) (dead ??= new List<int>()).Add(kv.Key);
            if (dead != null) foreach (int id in dead) _hist.Remove(id);
        }

        private double EAt(BenzoZones z, A5St x, int i)
        {
            if (x.IsVcl) return VclAt(x.Eid, i, out double l, out double h) ? (x.S > 0 ? h : l) : double.NaN;
            if (A5Const.V4Dyn(x.Order)) { V4At(z, x.Order, i, out double l, out double h); return x.S > 0 ? h : l; }
            return x.E;
        }

        // ------------------------------------------------------------ Evaluate
        protected override Signal Evaluate(SetupContext ctx, int i)
        {
            var z = ctx.Zones;
            if (z == null || z.Idx != i) return null;
            if (i <= _lastIdx) return null;                                   // gọi lại cùng nến: không đẩy VCL 2 lần
            if (i != _lastIdx + 1) throw new InvalidOperationException($"DetectorA5 phải nhận nến tuần tự: nhận {i}, mong {_lastIdx + 1}");
            var bar = ctx.Bars[i];
            var lv = ctx.GetLevels(i);
            _zref = z;

            // 0. phiên mới: kết thúc mọi trạng thái, xoá đếm
            if (z.NewSession) { EndAll("end"); _count.Clear(); _bcount.Clear(); _sigLog.Clear(); }
            // 1. sổ HVN
            _book.Step(i, bar, lv, z.NewSession);
            if (z.NewSession || CurrentLevels == null)
            {
                CurrentLevels = new A5Levels { HvnW = new List<(double, double, double)>(_book.HvnW), HvnD = new List<double>(_book.HvnD), Vah = z.YdVah, Val = z.YdVal };
            }
            // 2. nguồn VCL
            if (UseVcl)
            {
                _vcl ??= new VclCoreSource(ctx.TzOffset, z.UsShift);
                _vcl.Push(i, bar, lv);
                UpdateHist(i);
            }
            // 3. sự kiện M5 (k = nến cuối của nến M5; k == i bình thường, k == i−1 khi M5 thiếu phút cuối đóng trễ)
            foreach (var m in z.NewM5) OnM5(ctx, z, m);
            // 4–5. quét nến i + cập nhật đà/hết hạn
            bool okbar = !ctx.IsNewsBlocked(CloseTime(ctx, bar)) && z.Phase != "OFF" && !(z.BarsSinceBig >= 1 && z.BarsSinceBig <= 3)
                         && !(VirtualOpenBlock && BenzoCore.InVirtualOpen(z.Sm));
            _okLast = okbar;
            Signal sig = _st.Count > 0 ? Scan(ctx, z, i, bar, okbar) : null;
            // 6. tỉa lịch sử eid
            PruneHist(i);
            _lastIdx = i;
            return sig;
        }

        // ------------------------------------------------------------ sự kiện M5
        private void OnM5(SetupContext ctx, BenzoZones z, M5Bar m)
        {
            int k = m.LastIdx;
            double C = m.C;
            for (int order = 0; order < A5Const.V4Names.Length; order++)
            {
                V4At(z, order, k, out double lo, out double hi);
                OnZone(ctx, z, order, false, order, 0, k, C, lo, hi);
            }
            if (UseVcl)
            {
                var eids = new SortedSet<int>();
                foreach (var kv in _hist) if (kv.Value.First <= k && k <= kv.Value.Last) eids.Add(kv.Key);
                foreach (var key in _st.Keys) if (key.zid >= A5Const.VclBase) eids.Add(key.zid - A5Const.VclBase);
                foreach (int eid in eids)
                {
                    bool has = VclAt(eid, k, out double lo, out double hi);
                    OnZone(ctx, z, A5Const.VclBase + eid, true, 0, eid, k, C, has ? lo : double.NaN, has ? hi : double.NaN);
                }
            }
        }

        private void OnZone(SetupContext ctx, BenzoZones z, int zid, bool isVcl, int order, int eid, int k, double C, double lo, double hi)
        {
            if (Nan(lo))
            {
                foreach (int S in new[] { 1, -1 })
                    if (_st.Remove((zid, S), out var x)) Finish(x, isVcl ? "roi_bo" : "reset_value");
                return;
            }
            bool dyn = isVcl || A5Const.V4Dyn(order), band = isVcl || A5Const.V4Band(order);
            if (!isVcl && !dyn)
                foreach (int S in new[] { 1, -1 })
                    if (_st.TryGetValue((zid, S), out var x) && (x.ZLo != lo || x.ZHi != hi)) { _st.Remove((zid, S)); Finish(x, "reset_value"); }
            int outv = C > hi ? 1 : (C < lo ? -1 : 0);
            foreach (int S in new[] { 1, -1 })
            {
                if (!_st.TryGetValue((zid, S), out var x)) continue;
                double canh = dyn ? (S > 0 ? hi : lo) : x.E;
                bool deep = S * (C - canh) < -A5Const.CancelDepth;
                bool opp = band && outv == -S;
                if (deep || opp) { _st.Remove((zid, S)); Finish(x, "cancel"); }
            }
            if (outv == 0) return;
            if (_st.ContainsKey((zid, outv))) return;
            if (_st.ContainsKey((zid, -outv))) return;
            var s = OpenState(ctx, z, zid, isVcl, order, eid, outv, k, lo, hi);
            if (s != null) _st[(zid, outv)] = s;
        }

        private A5St OpenState(SetupContext ctx, BenzoZones z, int zid, bool isVcl, int order, int eid, int outv, int ev, double lo, double hi)
        {
            double canh = outv > 0 ? hi : lo;
            int a = z.SessionStartIdx;
            int kk = ev, lim = Math.Max(a, ev - A5Const.LegLookback);
            var bars = ctx.Bars;
            if (isVcl)
            {
                while (kk > lim)
                {
                    if (!VclAt(eid, kk, out double l, out double h)) break;
                    double rv = outv > 0 ? h : l;
                    if (outv > 0 ? bars[kk].C > rv : bars[kk].C < rv) kk--; else break;
                }
                // luật CÚ PHÁ THẬT: tại nến chân cú phá, vùng phải đang hiển thị và giá đóng ở phía TRONG (kể cả khi vòng lùi dừng ở giới hạn)
                if (!VclAt(eid, kk, out double l2, out double h2)) return null;
                bool inside = outv > 0 ? bars[kk].C <= h2 : bars[kk].C >= l2;
                if (!inside) return null;
            }
            else if (A5Const.V4Dyn(order))
            {
                while (kk > lim && (outv > 0 ? bars[kk].C > V4Raw(z, order, kk) : bars[kk].C < V4Raw(z, order, kk))) kk--;
            }
            else
            {
                while (kk > lim && (outv > 0 ? bars[kk].C > canh : bars[kk].C < canh)) kk--;
            }
            int f = kk < ev ? kk + 1 : ev;
            double L = 0; int pk = f;
            double best = outv > 0 ? double.NegativeInfinity : double.PositiveInfinity;
            for (int x = f; x <= ev; x++)
            {
                var b = bars[x];
                L = Math.Max(L, b.H - b.L);
                if (outv > 0 ? b.H > best : b.L < best) { best = outv > 0 ? b.H : b.L; pk = x; }
            }
            double pbmax = 0;
            for (int x = pk + 1; x <= ev; x++) pbmax = Math.Max(pbmax, bars[x].H - bars[x].L);
            string name = isVcl ? "VCL_" + eid : A5Const.V4Names[order];
            var key = (name, outv);
            _bcount[key] = (_bcount.TryGetValue(key, out int bc) ? bc : 0) + 1;
            return new A5St
            {
                Zid = zid, S = outv, P0 = ev, E = canh, ZLo = lo, ZHi = hi, L = L, PkPos = pk, PkVal = best, Pbmax = pbmax, KPos = kk,
                Armed = outv * (best - canh) >= A5Const.DMin, BrkNo = _bcount[key], NEnt = 0,
                IsVcl = isVcl, Order = order, Eid = eid, Name = name
            };
        }

        // ------------------------------------------------------------ quét nến i
        private struct Cand { public double Dist; public int Rank, Zid; public A5St X; public double E; public RiskResult R; public (string, int) CKey; public int Npb; }

        private Signal Scan(SetupContext ctx, BenzoZones z, int i, BarData b, bool okbar)
        {
            double ci = b.C;
            Cand? best = null;
            var ecache = new Dictionary<(int, int), double>();
            var snapshot = _st.Values.ToList();
            foreach (var x in snapshot)
            {
                if (x.P0 >= i) continue;
                double E = EAt(z, x, i);
                ecache[(x.Zid, x.S)] = E;
                bool near = Math.Abs(ci - E) <= A5Const.ZoneHalf || (b.L <= E && E <= b.H);
                if (!(okbar && near)) continue;
                int age = i - x.PkPos;
                if (!(x.Armed && age <= A5Const.THoi)) continue;
                int npb = i - 1 - x.PkPos;
                if (npb < A5Const.NMin || !(x.Pbmax < x.L) || !BenzoKernel.IsConfirmBar(b, x.S, z.Mad)) continue;
                var ckey = (x.Name, x.S);
                if (_count.TryGetValue(ckey, out int c0) && c0 >= 2) continue;
                // SL: HVN tuần và vùng S/R qua MÉP XA của dải; các vùng khác qua E
                bool slFar = x.IsVcl || A5Const.V4Band(x.Order);
                double far;
                if (slFar)
                {
                    double l2, h2;
                    if (x.IsVcl) VclAt(x.Eid, i, out l2, out h2); else V4At(z, x.Order, i, out l2, out h2);
                    far = x.S > 0 ? l2 : h2;
                }
                else far = E;
                double structP = x.S > 0 ? Math.Min(b.L, far - A5Const.ZoneHalf) : Math.Max(b.H, far + A5Const.ZoneHalf);
                var r = BenzoRisk.Calc(ctx.Bars, i, x.S, structP, A5Const.Rr, ctx.Tick);
                if (r == null) continue;
                if (x.IsVcl)
                {
                    // khoá mức: đã có ≥ 2 tín hiệu cùng phiên + chiều trong ±1 giá quanh E
                    if (_sigLog.TryGetValue(x.S, out var olds) && olds.Count(e0 => Math.Abs(e0 - E) <= A5Const.ZoneHalf) >= 2) continue;
                }
                var cand = new Cand { Dist = Math.Abs(ci - E), Rank = x.IsVcl ? A5Const.RankVcl : A5Const.V4Rank[x.Order], Zid = x.Zid, X = x, E = E, R = r, CKey = ckey, Npb = npb };
                if (best == null || Less(cand, best.Value)) best = cand;
            }
            Signal sig = null;
            A5St chosen = null;
            if (best != null)
            {
                var c = best.Value; chosen = c.X;
                var x = c.X;
                double dist = x.S * (x.PkVal - c.E);
                double zl, zh;
                if (x.IsVcl) VclAt(x.Eid, i, out zl, out zh); else V4At(z, x.Order, i, out zl, out zh);
                LastInfo = new A5Info
                {
                    Side = x.S, Zone = x.Name, E = c.E, ZLo = zl, ZHi = zh, P0 = x.P0, PkPos = x.PkPos, PkVal = x.PkVal, L = x.L, Pbmax = x.Pbmax,
                    Npb = c.Npb, BrkNo = x.BrkNo, EntNo = x.NEnt + 1, Dist = dist
                };
                bool band = x.IsVcl || A5Const.V4Band(x.Order);
                string pk = x.S > 0 ? "đỉnh" : "đáy";
                sig = new Signal
                {
                    Side = x.S, Entry = c.R.Entry, Sl = c.R.Sl, Tp = c.R.Tp, Zone = x.Name,
                    Reason = $"phá {(x.S > 0 ? "lên" : "xuống")} {A5Text.ZoneVn(x.Name)} {A5Text.Price(band, zl, zh, c.E)}"
                           + $" (M5 đóng ngoài {Hm(ctx, ctx.Bars[x.P0].Time.AddMinutes(ctx.BarMinutes))}), {pk} cách vùng {N(dist)} giá sau {x.PkPos - x.P0} nến,"
                           + $" hồi {c.Npb} nến, nến xác nhận Δ{Dl(b.Delta)}"
                };
                _count[c.CKey] = (_count.TryGetValue(c.CKey, out int cc) ? cc : 0) + 1;
                if (!_sigLog.TryGetValue(x.S, out var lst)) _sigLog[x.S] = lst = new List<double>();
                lst.Add(c.E);
                x.NEnt++;
                x.PkPos = i; x.PkVal = x.S > 0 ? b.H : b.L; x.Pbmax = 0;
            }
            // bước 3–4: cập nhật đà / hết hạn cho các trạng thái còn lại
            double rng = b.H - b.L;
            foreach (var x in snapshot)
            {
                if (x.P0 >= i || ReferenceEquals(x, chosen)) continue;
                double ext = x.S > 0 ? b.H : b.L;
                if (x.S * (ext - x.PkVal) > 0)
                {
                    x.PkPos = i; x.PkVal = ext; x.Pbmax = 0;
                    x.L = Math.Max(x.L, rng);
                    if (!ecache.TryGetValue((x.Zid, x.S), out double E)) E = EAt(z, x, i);
                    if (!x.Armed && x.S * (x.PkVal - E) >= A5Const.DMin) x.Armed = true;
                }
                else x.Pbmax = Math.Max(x.Pbmax, rng);
                if (i - x.PkPos > A5Const.THoi) { _st.Remove((x.Zid, x.S)); Finish(x, "expire"); }
            }
            return sig;
        }

        private static bool Less(Cand a, Cand b)
        {
            if (a.Dist != b.Dist) return a.Dist < b.Dist;
            if (a.Rank != b.Rank) return a.Rank < b.Rank;
            return a.Zid < b.Zid;
        }

        // ------------------------------------------------------------ nhật ký / kết thúc
        private void Finish(A5St x, string why)
        {
            StateLog?.Add(new A5StateLog { Zone = x.Name, Why = why, S = x.S, P0 = x.P0, PkPos = x.PkPos, BrkNo = x.BrkNo, NEnt = x.NEnt, PkVal = x.PkVal, E = x.E, Armed = x.Armed });
        }

        private void EndAll(string why)
        {
            foreach (var x in _st.Values.OrderBy(v => v.Zid).ThenBy(v => v.S)) Finish(x, why);
            _st.Clear();
        }

        /// <summary>Ghi 'end' cho trạng thái còn sống (cuối dữ liệu) — chỉ dùng khi đối chiếu.</summary>
        public void FlushEnd() => EndAll("end");

        public List<A5StateView> DebugStates() =>
            _st.Values.OrderBy(v => v.Zid).ThenBy(v => v.S).Select(x => new A5StateView
            {
                Name = x.Name, S = x.S, P0 = x.P0, PkPos = x.PkPos, BrkNo = x.BrkNo, NEnt = x.NEnt, KPos = x.KPos,
                E = x.E, ZLo = x.ZLo, ZHi = x.ZHi, L = x.L, PkVal = x.PkVal, Pbmax = x.Pbmax, Armed = x.Armed
            }).ToList();

        // ------------------------------------------------------------ hiển thị: các trạng thái đã trang bị gần giá nhất
        /// <summary>Tối đa 3 trạng thái ĐÃ TRANG BỊ, còn chỗ (đếm &lt; 2), E ở nến cuối khác NaN, còn hạn; gần giá đóng nến cuối nhất trước.
        /// Gọi sau khi engine xử lý xong nến lastIdx. Trả danh sách bất biến (rỗng nếu chưa chạy).</summary>
        public List<A5Watch> Watch(int lastIdx, BarData lastBar, bool tradeOpen)
        {
            var res = new List<A5Watch>();
            if (lastBar == null || lastIdx < 0 || lastIdx != _lastIdx || _zref == null) return res;
            var z = _zref;
            var tmp = new List<(double dist, A5Watch w)>();
            foreach (var x in _st.Values)
            {
                if (!x.Armed) continue;
                if (_count.TryGetValue((x.Name, x.S), out int c) && c >= 2) continue;
                if (lastIdx - x.PkPos > A5Const.THoi) continue;
                double E = EAt(z, x, lastIdx);
                if (Nan(E)) continue;
                double lo, hi;
                if (x.IsVcl) VclAt(x.Eid, lastIdx, out lo, out hi); else V4At(z, x.Order, lastIdx, out lo, out hi);
                bool near = Math.Abs(lastBar.C - E) <= A5Const.ZoneHalf || (lastBar.L <= E && E <= lastBar.H);
                var w = new A5Watch
                {
                    Name = x.Name, IsVcl = x.IsVcl, IsBand = x.IsVcl || A5Const.V4Band(x.Order), IsDyn = x.IsVcl || A5Const.V4Dyn(x.Order),
                    Side = x.S, P0 = x.P0, PkPos = x.PkPos, Npb = lastIdx - x.PkPos, Left = A5Const.THoi - (lastIdx - x.PkPos),
                    BrkNo = x.BrkNo, NEnt = x.NEnt, E = E, Lo = lo, Hi = hi, PkVal = x.PkVal, L = x.L, Pbmax = x.Pbmax,
                    Dist = x.S * (x.PkVal - E), Near = near, OkBar = _okLast, TradeOpen = tradeOpen
                };
                w.Status = A5Text.Status(w);
                w.P0Time = z.Bars[x.P0].Time; w.PkTime = z.Bars[x.PkPos].Time;
                w.Label = A5Text.Label(w);
                tmp.Add((Math.Abs(lastBar.C - E), w));
            }
            foreach (var t in tmp.OrderBy(t => t.dist).Take(3)) res.Add(t.w);
            return res;
        }
    }
}
