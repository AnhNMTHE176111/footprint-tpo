// ============================================================================
//  BenzoDetectors — 4 setup A/B/C/D (port từ research/setup_*.py, ô chính)
// ============================================================================
//  A Phá hồi (V3: hết hạn 30 nến, TP 3R) · B Hấp thụ (BASE θ0,5 N3, TP 3R)
//  C Fade cạnh (xuyên 2 tick, TP 2R cố định) · D Trap (V3 bỏ vùng Z, TP 2R)
//  Mỗi detector chạy THEO DÒNG: Observe(nến i) tính tín hiệu của nến i và cập nhật trạng thái,
//  TryDetect trả đúng kết quả đó. Chỉ dùng dữ liệu nến <= i (ClosedBars chặn nhìn trước).
//  Điều kiện chung (ngoài Python): không phát tín hiệu trong ±15' tin USD mức cao (ctx.IsNewsBlocked).
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;

    public abstract class DetectorBase : IObservingDetector
    {
        public abstract char Setup { get; }
        private Signal _pending;
        private int _pendingIdx = -1;

        protected abstract Signal Evaluate(SetupContext ctx, int i);

        public void Observe(SetupContext ctx, int closedIdx)
        {
            _pending = Evaluate(ctx, closedIdx);
            _pendingIdx = closedIdx;
        }

        public Signal TryDetect(SetupContext ctx, int closedIdx)
        {
            if (_pendingIdx == closedIdx) { var s = _pending; _pending = null; return s; }
            return Evaluate(ctx, closedIdx);   // dùng độc lập (không qua engine.Observe)
        }

        // ---- tiện ích định dạng ----
        protected static string N(double v, string fmt = "0.0") => BenzoCore.Num(v, fmt);
        protected static string Dl(double v) => (v >= 0 ? "+" : "−") + BenzoCore.Num(Math.Abs(Math.Round(v)), "0");
        protected static string Hm(SetupContext ctx, DateTime utc) => ctx.ToVn(utc).ToString("HH:mm", CultureInfo.InvariantCulture);
        /// <summary>Giờ ĐÓNG nến (= giờ vào lệnh), dùng cho kiểm tra tin.</summary>
        protected static DateTime CloseTime(SetupContext ctx, BarData b) => b.Time.AddMinutes(ctx.BarMinutes);
    }

    // ===================================================================== A · Phá hồi
    public sealed class DetectorA : DetectorBase
    {
        public override char Setup => 'A';
        private const int NMin = 3;            // số nến hồi tối thiểu
        private const double Rr = 3.0;
        private const int Expire = 30;         // CF phải nằm trong 30 nến M1 sau nến M5 phá
        private const double ZoneHalf = 1.0;   // mép xa vùng E = E ± 1
        private const int LegLookback = 60;
        private const int SmNoBreakFrom = 780, SmNoBreakTo = 860;   // 18:00–19:20 VN

        private sealed class St
        {
            public int S, P0, PkPos, Sess; public double E, L, PkVal, Pbmax; public string Src;
            public DateTime BrkClose;
        }
        private St _st;
        private readonly Dictionary<string, int> _count = new();

        protected override Signal Evaluate(SetupContext ctx, int i)
        {
            var z = ctx.Zones;
            if (z == null || z.Idx != i) return null;
            if (z.NewSession) { _st = null; _count.Clear(); }
            foreach (var m in z.NewM5) OnM5(ctx, z, m);
            if (_st == null || i <= _st.P0 || i > _st.P0 + Expire) return null;
            return Scan(ctx, z, i);
        }

        private void OnM5(SetupContext ctx, BenzoZones z, M5Bar m)
        {
            if (!BenzoZones.SelA(m.Snap, out double bh, out double bl, out string src)) { _st = null; return; }
            if (_st != null && _st.Src != src) _st = null;
            int outv = m.C > bh ? 1 : (m.C < bl ? -1 : 0);
            if (outv == 0) { _st = null; return; }
            if (_st != null && _st.S == outv) return;           // cùng phía: vẫn là cú phá cũ
            _st = null;
            if (m.Snap.Sm >= SmNoBreakFrom && m.Snap.Sm < SmNoBreakTo) return;
            double e = outv > 0 ? bh : bl;
            _st = MakeState(ctx, z, outv, e, m.LastIdx, src, m.T5End);
        }

        private St MakeState(SetupContext ctx, BenzoZones z, int outv, double e, int lp, string src, DateTime brkClose)
        {
            int a = z.SessionStartIdx;
            int k = lp, lim = Math.Max(a, lp - LegLookback);
            while (k > lim && (outv > 0 ? ctx.Bars[k].C > e : ctx.Bars[k].C < e)) k--;
            int from = k < lp ? k + 1 : lp;
            double L = 0; int pk = from;
            double best = outv > 0 ? double.NegativeInfinity : double.PositiveInfinity;
            for (int x = from; x <= lp; x++)
            {
                var b = ctx.Bars[x];
                L = Math.Max(L, b.H - b.L);
                if (outv > 0 ? b.H > best : b.L < best) { best = outv > 0 ? b.H : b.L; pk = x; }
            }
            double pbmax = 0;
            for (int x = pk + 1; x <= lp; x++) pbmax = Math.Max(pbmax, ctx.Bars[x].H - ctx.Bars[x].L);
            return new St
            {
                S = outv, E = e, P0 = lp, L = L, Src = src, Sess = z.SessionNo, PkPos = pk,
                PkVal = outv > 0 ? ctx.Bars[pk].H : ctx.Bars[pk].L, Pbmax = pbmax, BrkClose = brkClose
            };
        }

        private Signal Scan(SetupContext ctx, BenzoZones z, int i)
        {
            var st = _st; int S = st.S; double E = st.E;
            var b = ctx.Bars[i];
            double rng = b.H - b.L;
            int sb = z.BarsSinceBig;
            bool ok = z.Phase != "OFF" && !(sb >= 1 && sb <= 3);
            bool near = Math.Abs(b.C - E) <= 1.0 || (b.L <= E && E <= b.H);
            if (ok && near)
            {
                int npb = i - 1 - st.PkPos;
                string key = st.Sess + "|" + st.Src + "|" + S + "|" + Math.Round(E, 1).ToString("0.0", CultureInfo.InvariantCulture);
                _count.TryGetValue(key, out int cnt);
                if (npb >= NMin && st.Pbmax < st.L && BenzoKernel.IsConfirmBar(b, S, z.Mad) && cnt < 2
                    && !ctx.IsNewsBlocked(CloseTime(ctx, b)))
                {
                    double structP = S > 0 ? Math.Min(b.L, E - ZoneHalf) : Math.Max(b.H, E + ZoneHalf);
                    var r = BenzoRisk.Calc(ctx.Bars, i, S, structP, Rr, ctx.Tick);
                    if (r != null)
                    {
                        _count[key] = cnt + 1;
                        string edge = EdgeName(st.Src, S);
                        var sig = new Signal
                        {
                            Side = S, Entry = r.Entry, Sl = r.Sl, Tp = r.Tp, Zone = ZoneName(st.Src, S),
                            Reason = $"phá {edge} {N(E)} (M5 đóng ngoài {Hm(ctx, st.BrkClose)}), hồi U {npb} nến, CF Δ{Dl(b.Delta)}"
                        };
                        st.PkPos = i; st.PkVal = S > 0 ? b.H : b.L; st.Pbmax = 0;
                        return sig;
                    }
                }
            }
            if ((S > 0 && b.H > st.PkVal) || (S < 0 && b.L < st.PkVal)) { st.PkPos = i; st.PkVal = S > 0 ? b.H : b.L; st.Pbmax = 0; }
            else st.Pbmax = Math.Max(st.Pbmax, rng);
            return null;
        }

        private static string EdgeName(string src, int S) => src switch
        {
            "IB" => S > 0 ? "cạnh trên IB" : "cạnh dưới IB",
            "Y" => S > 0 ? "VAH hôm qua" : "VAL hôm qua",
            _ => S > 0 ? "VAH Âu" : "VAL Âu"
        };
        private static string ZoneName(string src, int S) => src == "IB" ? (S > 0 ? "IB_H" : "IB_L") : (S > 0 ? "VAH" : "VAL") + (src == "Y" ? "_Y" : "_EU");
    }

    // ===================================================================== B · Hấp thụ
    /// <summary>Một vùng B canh: tên, loại (để đếm trần 2 lệnh/(loại, phiên)), cách lấy giá, chiều move được phép (0 = cả hai).</summary>
    public sealed class BZone
    {
        public string Name, ZType;
        public int Kind;       // 0 VWAP tuần · 1 VWAP ngày · 2 mức cố định (BenzoSr.Fx) · 3 VCL cạnh dưới (R) · 4 VCL cạnh trên (S)
        public int Slot, Fi;   // khe VCL / chỉ số trong Fx
        public int Mdir;       // +1 chỉ giá đi LÊN tới vùng (sell) · −1 chỉ giá đi XUỐNG (buy) · 0 cả hai
    }

    public sealed class DetectorB : DetectorBase
    {
        public override char Setup => 'B';
        private const int NCluster = 3;
        private const double Theta = 0.5, MoveMin = 3.0, TouchTol = 1.0, ExtTol = 0.5, Rr = 3.0;
        private const int Lookback = 20, Warm = 30, BigExcl = 3, MaxPerZoneSession = 2;
        private readonly Dictionary<string, int> _cnt = new();
        private readonly List<BZone> _zones;

        /// <summary>Nhóm v2 (HVN/VA/POC ngày-tuần).</summary>
        public readonly bool UseV2;
        /// <summary>Nhóm S/R (đỉnh/đáy phiên trước + vùng Canh Lệnh VCL).</summary>
        public readonly bool UseSr;
        public IReadOnlyList<BZone> Zones => _zones;

        /// <summary>Mặc định chỉ 2 VWAP (B cũ: 11 lệnh/90 ngày). v2 = thêm 10 mức ngày/tuần (25 lệnh); sr = thêm PDH/PDL + 14 cạnh VCL (58 lệnh khi bật cả hai).</summary>
        public DetectorB(bool v2 = false, bool sr = false)
        {
            UseV2 = v2; UseSr = sr;
            _zones = BuildZones(v2, sr);
        }

        public static List<BZone> BuildZones(bool v2, bool sr)
        {
            var l = new List<BZone>
            {
                new BZone { Name = "VWAP_W", ZType = "VWAP_W", Kind = 0 },
                new BZone { Name = "VWAP_D", ZType = "VWAP_D", Kind = 1 },
            };
            void Fixed(string nm)
            {
                string zt = nm.StartsWith("HVN_D") ? "HVN_D" : nm.StartsWith("HVN_W") ? "HVN_W" : nm.StartsWith("PD") ? "PDHL" : nm;
                l.Add(new BZone { Name = nm, ZType = zt, Kind = 2, Fi = BenzoSr.FixedIndex(nm) });
            }
            if (v2) foreach (var nm in new[] { "POC_D", "VAH_D", "VAL_D", "HVN_D1", "HVN_D2", "HVN_D3", "POC_W", "HVN_W1", "HVN_W2", "HVN_W3" }) Fixed(nm);
            if (sr)
            {
                Fixed("PDH"); Fixed("PDL");
                for (int k = 0; k < BenzoSr.VclSlots; k++) l.Add(new BZone { Name = "VCL_R" + (k + 1), ZType = "VCL", Kind = 3, Slot = k, Mdir = 1 });
                for (int k = 0; k < BenzoSr.VclSlots; k++) l.Add(new BZone { Name = "VCL_S" + (k + 1), ZType = "VCL", Kind = 4, Slot = k, Mdir = -1 });
            }
            return l;
        }

        private static double ZAt(BZone zn, BenzoZones z, int k) => zn.Kind switch
        {
            0 => z.VwapWAt(k),
            1 => z.VwapDAt(k),
            2 => z.Sr.Fx[zn.Fi],                       // mức cố định của phiên (các nến k đã được kiểm cùng phiên với nến i)
            3 => z.Sr.SlotLoAt(zn.Slot, k),
            _ => z.Sr.SlotHiAt(zn.Slot, k),
        };

        private static bool WarmAt(BZone zn, BenzoZones z, int k) => zn.Kind switch
        {
            0 => z.PosInWeekAt(k) >= Warm,
            1 => z.PosInSessionAt(k) >= Warm,
            2 => true,
            _ => z.Sr.SlotRunAt(zn.Slot, k) >= BenzoSr.VclWarm,   // khe giữ CÙNG một vùng ≥ 4 nến liên tiếp
        };

        protected override Signal Evaluate(SetupContext ctx, int i)
        {
            var z = ctx.Zones;
            if (z == null || z.Idx != i) return null;
            if (z.NewSession) _cnt.Clear();
            if (i < NCluster + 1 || z.Phase == "OFF") return null;
            var b = ctx.Bars[i];
            double rng = b.H - b.L;
            for (int M = 1; M >= -1; M -= 2)
            {
                int s = -M;
                double cs = (b.C - b.O) * s;
                if (!(cs > 0 && cs >= BenzoKernel.CfBodyFrac * rng && b.Delta * s > 0)) continue;
                foreach (var zn in _zones)         // thứ tự ưu tiên: vùng đứng trước thắng khi trùng nến
                {
                    if (zn.Mdir != 0 && zn.Mdir != M) continue;
                    var sig = Try(ctx, z, i, b, zn, M, s);
                    if (sig == null) continue;
                    // trần 2 lệnh / (loại vùng, phiên) — tính sau khi đã chọn vùng ưu tiên của nến này
                    string key = zn.ZType + "|" + z.SessionNo;
                    _cnt.TryGetValue(key, out int c);
                    if (c >= MaxPerZoneSession) return null;
                    if (ctx.IsNewsBlocked(CloseTime(ctx, b))) return null;
                    _cnt[key] = c + 1;
                    return sig;
                }
            }
            return null;
        }

        private Signal Try(SetupContext ctx, BenzoZones z, int i, BarData b, BZone zn, int M, int s)
        {
            int nc = NCluster;
            // cụm N nến trước CF: mỗi nến chạm Z, cùng phiên, vùng "ấm", không phase OFF
            for (int j = 1; j <= nc; j++)
            {
                int k = i - j;
                if (z.SessionAt(k) != z.SessionNo || z.PhaseAt(k) == "OFF") return null;
                if (!WarmAt(zn, z, k)) return null;
                var bk = ctx.Bars[k]; double zk = ZAt(zn, z, k);
                bool touch = Math.Abs(bk.C - zk) <= TouchTol || (bk.L <= zk && zk <= bk.H);
                if (!touch) return null;           // z NaN ⇒ mọi so sánh false ⇒ loại
            }
            // thân và |Δ| giảm: nến cuối cụm < nến đầu cụm
            var first = ctx.Bars[i - nc]; var last = ctx.Bars[i - 1];
            if (!(first.Body > last.Body && Math.Abs(first.Delta) > Math.Abs(last.Delta))) return null;
            // cực trị cụm không vượt Z + 0,5
            double ext = M > 0 ? double.NegativeInfinity : double.PositiveInfinity;
            for (int k = i - nc; k <= i - 1; k++) ext = M > 0 ? Math.Max(ext, ctx.Bars[k].H) : Math.Min(ext, ctx.Bars[k].L);
            double zlast = ZAt(zn, z, i - 1);
            if (M > 0 ? !(ext <= zlast + ExtTol) : !(ext >= zlast - ExtTol)) return null;
            // loại: TREND cùng chiều M · đang phá VA Âu/IB theo chiều M · nến lớn nhất phiên trong 3 nến cuối
            var md = z.ModeDef;
            if (md.Mode == (M > 0 ? "TREND_UP" : "TREND_DN")) return null;
            double prevC = ctx.Bars[i - 1].C;
            if (md.BreakSide == M) return null;
            if (M > 0 && prevC > md.BandHi) return null;
            if (M < 0 && prevC < md.BandLo) return null;
            if (!(z.BarsSinceBig > BigExcl)) return null;
            // move ≥ 3 giá tới Z
            int a = i - nc;
            double zz = zlast;
            int s0 = Math.Max(a - Lookback, z.SessionStartIdx);
            if (s0 >= a) return null;
            int e = s0; double ev = M > 0 ? double.PositiveInfinity : double.NegativeInfinity;
            for (int k = s0; k < a; k++)
            {
                if (M > 0 ? ctx.Bars[k].L < ev : ctx.Bars[k].H > ev) { ev = M > 0 ? ctx.Bars[k].L : ctx.Bars[k].H; e = k; }
            }
            double move = M > 0 ? zz - ev : ev - zz;
            if (move < MoveMin) return null;
            // |Δ_CF| ≥ θ × |Δ| lớn nhất của move
            double mad = 0, madAll = 0; bool any = false;
            for (int k = e; k < a; k++)
            {
                double ad = Math.Abs(ctx.Bars[k].Delta);
                madAll = Math.Max(madAll, ad);
                if (ctx.Bars[k].Delta * M > 0) { any = true; mad = Math.Max(mad, ad); }
            }
            if (!any) mad = madAll;
            if (mad <= 0 || Math.Abs(b.Delta) < Theta * mad) return null;
            double structP = M > 0 ? double.NegativeInfinity : double.PositiveInfinity;
            for (int k = a; k < i; k++) structP = M > 0 ? Math.Max(structP, ctx.Bars[k].H) : Math.Min(structP, ctx.Bars[k].L);
            var r = BenzoRisk.Calc(ctx.Bars, i, s, structP, Rr, ctx.Tick);
            if (r == null) return null;
            string nm = BenzoZoneNames.Label(zn.Name);
            return new Signal
            {
                Side = s, Entry = r.Entry, Sl = r.Sl, Tp = r.Tp, Zone = zn.Name,
                Reason = $"hấp thụ tại {nm} {N0(zz)}: move {N0(move)} giá {(M > 0 ? "lên" : "xuống")}, {nc} nến chạm có thân/Δ giảm, "
                       + $"CF Δ{Dl(b.Delta)} (≥50% Δ lớn nhất {N0(mad, "0")})"
            };
        }
        private static string N0(double v, string f = "0.0") => BenzoCore.Num(v, f);
    }

    // ===================================================================== C · Fade cạnh
    /// <summary>
    /// C Fade cạnh: râu chọc qua cạnh band cân bằng ≥ 2 tick rồi đóng lại trong, Δ cùng chiều vào lệnh.
    /// C0 (mặc định, Opt = Legacy): band = VA hôm qua (Á/Âu) · VA Âu/IB (Mỹ), TP 2R cố định.
    /// Lớp mới (CLayerOptions): cổng hình D / vùng dày P-b (hình dạng profile TPO hôm qua), VA nhỏ CHoCH, hành lang S/R (VCL).
    /// Mỗi lớp có bộ đếm "≤ 2 lệnh / (phiên, cạnh)" riêng; cùng nến nhiều lớp cùng bắn: L(D, P/b) vs CHoCH ⇒ cạnh gần giá đóng hơn
    /// (hoà ⇒ CHoCH); S/R chỉ thêm khi các lớp kia không bắn (merge_add của Python). TpToEdge: TP về cạnh đối diện / POC (≥ 2R), không đủ ⇒ bỏ.
    /// </summary>
    public sealed class DetectorC : DetectorBase, IZoneConsumer
    {
        public override char Setup => 'C';
        private const int PenTicks = 2;
        private const double MinWidth = 6.0, Rr = 2.0;
        private const int SmNoFrom = 780, SmNoTo = 860;     // 18:00–19:20 VN
        private readonly Dictionary<string, int> _cBase = new(), _cChoch = new(), _cSr = new();
        public readonly CLayerOptions Opt;

        public DetectorC() : this(CLayerOptions.Legacy) { }
        public DetectorC(CLayerOptions opt) { Opt = opt ?? CLayerOptions.Legacy; }

        public void ConfigureZones(BenzoZones z, bool enabled)
        {
            z.Layers.Configure(Opt, enabled);
            if (z.Layers.UseSr)
            {   // dùng chung MỘT lõi VCL với setup B (BenzoSr.Core) — không chạy hai bản
                z.Sr.UseVcl = true;
                z.Layers.SharedCore = () => z.Sr.Core;
            }
        }

        private sealed class Cand { public Signal Sig; public double Edge; }

        protected override Signal Evaluate(SetupContext ctx, int i)
        {
            var z = ctx.Zones;
            if (z == null || z.Idx != i) return null;
            if (z.NewSession) { _cBase.Clear(); _cChoch.Clear(); _cSr.Clear(); }
            var L = z.Layers;
            // ---- lớp nền: C0 hoặc lớp D / P-b
            Cand c0;
            if (L.UseShape)
            {
                L.LabelsL(out string hn, out string ln, out string sl);
                c0 = Layer(ctx, z, i, L.TrkL.Cur, L.PocL(), hn, ln, sl, _cBase);
            }
            else c0 = Layer(ctx, z, i, z.ModeC, z.Sm < BenzoKernel.SmUsStart ? z.YdPoc : z.EuPoc, "", "", "", _cBase);
            Cand res = c0;
            // ---- VA nhỏ CHoCH
            if (L.UseChoch)
            {
                string src = L.Choch.Src[i];
                string hn = src != "" ? src + "_HI" : "", ln = src != "" ? src + "_LO" : "";
                var c3 = Layer(ctx, z, i, L.Choch.Mode, double.NaN, hn, ln, "VA nhỏ " + (src == "CHOCH_UP" ? "CHoCH-UP" : "CHoCH-DN") + " (3 lần đổi hành vi)", _cChoch);
                if (c0 != null && c3 != null)
                {
                    double cl = ctx.Bars[i].C;
                    res = Math.Abs(cl - c0.Edge) < Math.Abs(cl - c3.Edge) - 1e-12 ? c0 : c3;
                }
                else res = c0 ?? c3;
            }
            // ---- hành lang S/R: chỉ thêm khi lớp trên không bắn (counter vẫn tăng như Python)
            if (L.UseSr)
            {
                var m4 = L.Sr.Mode;
                var c4 = Layer(ctx, z, i, m4, double.NaN, m4.BandSrc != "" ? "SR_HI" : "", m4.BandSrc != "" ? "SR_LO" : "", "hành lang S/R giữa hai vùng Canh Lệnh (VCL)", _cSr);
                if (res == null) res = c4;
            }
            return res?.Sig;
        }

        /// <summary>Một lớp: dò râu chọc qua cạnh band `md` (band + chế độ của lớp). poc: POC cho TP (NaN = không có).</summary>
        private Cand Layer(SetupContext ctx, BenzoZones z, int i, ModeState md, double poc, string hiName, string loName, string srcLabel, Dictionary<string, int> cnt)
        {
            if (md.Mode != "BALANCE" || z.Phase == "OFF") return null;
            if (z.Sm >= SmNoFrom && z.Sm < SmNoTo) return null;
            double bh = md.BandHi, bl = md.BandLo;
            if (!(bh - bl >= MinWidth - 1e-9)) return null;
            var b = ctx.Bars[i];
            double rng = b.H - b.L;
            if (!(rng < z.PrevBigRange)) return null;                  // nến xuyên là nến dài nhất phiên ⇒ loại
            double pen = PenTicks * BenzoKernel.Tick - 1e-9;
            double body = b.Body;
            bool sell = b.H >= bh + pen && b.C < bh && b.Delta < 0 && (Math.Min(b.O, b.C) - b.L) <= body;
            bool buy = b.L <= bl - pen && b.C > bl && b.Delta > 0 && (b.H - Math.Max(b.O, b.C)) <= body;
            if (!sell && !buy) return null;
            int side = sell ? -1 : 1;
            double E = side < 0 ? bh : bl;
            string key = z.SessionNo + "|" + Math.Round(E, 1).ToString("0.0", CultureInfo.InvariantCulture);
            cnt.TryGetValue(key, out int c);
            if (c >= 2) return null;
            double structP = side < 0 ? b.H : b.L;
            var r = BenzoRisk.Calc(ctx.Bars, i, side, structP, Rr, ctx.Tick);
            if (r == null) return null;
            double tp = r.Tp; string tpTxt = "";
            if (Opt.TpToEdge)
            {
                double opp = side < 0 ? bl : bh;
                double best = double.NaN;
                bool okOpp = (opp - r.Entry) * side > 0;
                bool okPoc = !double.IsNaN(poc) && (poc - r.Entry) * side > 0;
                if (!okOpp && !okPoc) return null;
                if (okOpp && okPoc) best = side < 0 ? Math.Max(opp, poc) : Math.Min(opp, poc);
                else best = okOpp ? opp : poc;
                if (Math.Abs(best - r.Entry) < 2.0 * r.Risk - 1e-9) return null;
                tp = Math.Round(best, 6);
                tpTxt = $" · TP về {N(tp)}";
            }
            if (ctx.IsNewsBlocked(CloseTime(ctx, b))) return null;
            cnt[key] = c + 1;
            string edge;
            if (srcLabel != "") edge = (side < 0 ? "cạnh trên " : "cạnh dưới ") + srcLabel;
            else if (z.Phase == "US") edge = md.BandSrc == "ib" ? (side < 0 ? "cạnh trên IB" : "cạnh dưới IB") : (side < 0 ? "VAH Âu" : "VAL Âu");
            else edge = side < 0 ? "VAH hôm qua" : "VAL hôm qua";
            string zone = z.Phase == "US" ? (md.BandSrc == "ib" ? (side < 0 ? "IB_H" : "IB_L") : (side < 0 ? "VAH_EU" : "VAL_EU")) : (side < 0 ? "VAH_Y" : "VAL_Y");
            string zn = side < 0 ? hiName : loName;
            if (zn != "") zone = zn;
            double pokeTicks = side < 0 ? (b.H - E) / BenzoKernel.Tick : (E - b.L) / BenzoKernel.Tick;
            return new Cand
            {
                Edge = E,
                Sig = new Signal
                {
                    Side = side, Entry = r.Entry, Sl = r.Sl, Tp = tp, Zone = zone,
                    Reason = $"phá hụt {edge} {BenzoCore.Num(E)}: râu xuyên {BenzoCore.Num(pokeTicks, "0")} tick, đóng lại trong range (rộng {BenzoCore.Num(bh - bl)} giá), Δ{Dl(b.Delta)}{tpTxt}"
                }
            };
        }
    }

    // ===================================================================== D · Trap
    public sealed class DetectorD : DetectorBase
    {
        public override char Setup => 'D';
        private const double MinMove = 5.0, MaxRetr = 0.7, Rr = 2.0, PullMinDepth = 1.0;
        private const int LegMaxBars = 30, PullMaxBars = 30, CfWindow = 3;

        private sealed class Pair { public Pivot A, B; public int S; public bool Done; }
        private readonly List<Pair> _active = new();
        private int _pivSeen;

        protected override Signal Evaluate(SetupContext ctx, int i)
        {
            var z = ctx.Zones;
            if (z == null || z.Idx != i) return null;
            // cặp (đáy, đỉnh) / (đỉnh, đáy) zigzag liên tiếp mới xác nhận
            while (_pivSeen < z.Pivots.Count)
            {
                int k = _pivSeen++;
                if (k < 1) continue;
                var a = z.Pivots[k - 1]; var bp = z.Pivots[k];
                if (a.IsHigh == bp.IsHigh) continue;
                if (z.SessionAt(a.Pos) != z.SessionAt(bp.Pos)) continue;
                if (Math.Abs(bp.Price - a.Price) < MinMove || bp.Pos - a.Pos > LegMaxBars) continue;
                _active.Add(new Pair { A = a, B = bp, S = (!a.IsHigh && bp.IsHigh) ? 1 : -1 });
            }
            _active.RemoveAll(p => p.Done || z.SessionAt(p.B.Pos) != z.SessionNo || i > p.B.Pos + PullMaxBars + CfWindow + 1);
            foreach (var p in _active)
            {
                var sig = EvalPair(ctx, z, p, i);
                if (sig != null || p.Done) { p.Done = true; return sig; }
            }
            return null;
        }

        /// <summary>Tái hiện vòng j / CF của Python với dữ liệu tới nến i; trả tín hiệu nếu entry rơi đúng nến i.</summary>
        private Signal EvalPair(SetupContext ctx, BenzoZones z, Pair p, int i)
        {
            int S = p.S; double top = p.B.Price; int p2 = p.B.Pos;
            double move = Math.Abs(p.B.Price - p.A.Price);
            int jmax = Math.Min(i - 1, p2 + PullMaxBars);
            double ext = S > 0 ? double.PositiveInfinity : double.NegativeInfinity;
            int j = p2;
            int sessP2 = z.SessionAt(p2);
            while (j < jmax)
            {
                j++;
                if (z.SessionAt(j) != sessP2) break;
                var bj = ctx.Bars[j];
                if ((S > 0 && bj.H > top) || (S < 0 && bj.L < top)) break;
                if (!((S > 0 && bj.L <= ext) || (S < 0 && bj.H >= ext))) continue;
                ext = S > 0 ? bj.L : bj.H;
                double depth = (top - ext) * S;
                if (depth / move > MaxRetr) break;
                if (depth < PullMinDepth) continue;
                double rng = bj.H - bj.L;
                bool okDelta = rng > 0 && (-S * bj.Delta > 0) && S * (bj.C - (bj.H + bj.L) / 2.0) > 0;
                if (!okDelta) continue;
                // CF theo S trong CfWindow nến sau j
                int iiMax = Math.Min(i, j + CfWindow);
                for (int ii = j + 1; ii <= iiMax; ii++)
                {
                    if (z.SessionAt(ii) != z.SessionAt(j)) break;
                    var bi = ctx.Bars[ii];
                    if ((S > 0 && bi.L < ext) || (S < 0 && bi.H > ext)) break;
                    if ((S > 0 && bi.H > top) || (S < 0 && bi.L < top)) break;
                    if (ii < p.B.ConfirmPos) continue;
                    if (!BenzoKernel.IsConfirmBar(bi, S, z.MadAt(ii))) continue;
                    string ph = z.PhaseAt(ii);
                    if (ph == "OFF") break;
                    if (z.ModeAt(ii) == "BALANCE") break;
                    int sb = z.BarsSinceBigAt(ii);
                    if (sb >= 1 && sb <= 3) break;
                    if ((ph == "A" || ph == "EU") && !z.MoveClearAt(ii)) break;       // lọc sideway (A/Âu)
                    if (z.BiasAt(ii) != S) break;
                    var r = BenzoRisk.Calc(ctx.Bars, ii, S, ext, Rr, ctx.Tick);
                    if (r == null) break;
                    if (ii < i) { p.Done = true; return null; }                       // entry đã đáng ra phát ở nến trước
                    if (ctx.IsNewsBlocked(CloseTime(ctx, bi))) { p.Done = true; return null; }
                    return new Signal
                    {
                        Side = S, Entry = r.Entry, Sl = r.Sl, Tp = r.Tp, Zone = "-",
                        Reason = $"bẫy phe hồi: move {BenzoCore.Num(move)} giá {(S > 0 ? "lên" : "xuống")}, hồi {BenzoCore.Num(100 * depth / move, "0")}% tới {BenzoCore.Num(ext)}, "
                               + $"nến cực trị Δ{Dl(bj.Delta)} đóng {(S > 0 ? "nửa trên" : "nửa dưới")}, CF Δ{Dl(bi.Delta)}"
                    };
                }
            }
            return null;
        }
    }
}
