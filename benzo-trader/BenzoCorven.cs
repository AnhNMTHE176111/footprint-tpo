// ============================================================================
//  BenzoCorven — setup "follow theo footprint" của CORVEN (plans/BENZO-CORVEN-plan.md, GĐ3 mục 10)
// ============================================================================
//  PORT Y CHỮ từ benzo-trader/research/setup_corven.py (LogicVersion "corven-2" = corven-1 + 4 sửa đổi người học 2026-11-09, setup_corven.cp_live()):
//    ① bối cảnh = RangeLogic (quantower-range/RangeLogic.cs, nối nguồn lúc build) — thế A (fail break) / thế B (phá giữ được)
//    ② mốc "gần" + test không quá sâu + cửa sổ test          (Step2Machine.on_bar / _a_candidate / _b_step / _b_eval)
//    ③ 5 loại dấu hiệu, cần ≥ 2 loại                          (find_signs)
//    ④ nến xác nhận, SL, mục tiêu/R, giờ + ⛔ 3 luật veto      (eval_order)
//    chọn lệnh 4d: 1 lệnh mở, 1 lệnh/thế, 1 lệnh/(range, cạnh, thế) (select_and_simulate)
//  KHÔNG port (plan 10.1): ngoại lệ "lần 2" (a2_on), neo SL pivot, overlap_max_drop, lọc thin/splice.
//  Lệch có chủ đích DUY NHẤT so với Python: cổng tin USD (IsNewsBlocked) — Python không có lịch tin.
//  "Nến cuối phiên" (Python biết trước nến cuối) xử lý ở BenzoEngine: lệnh vào ở nến cuối phiên bị HUỶ khi nến đầu
//  phiên sau tới (giống Python không vào), lệnh còn mở qua khoảng trống > 30′ đóng TIME tại giá đóng nến cuối.
//  Quy ước (Q11): nền_ô = 100 nến TRƯỚC nến hiện tại; mbr (Range Box) và medΔ (50 nến) GỒM nến hiện tại.
//  Mọi giá trong máy là SỐ TICK (long / double .5 cho cạnh range). MỌI `using` nằm TRONG namespace (nối file).
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using OrderFlowBubbles;
    using RangeBox;

    /// <summary>Bộ tham số corven-1 (bộ gốc vòng 1, RESULTS-CORVEN.md). ĐÓNG CỨNG — không đưa ra Settings (plan 10.2):
    /// muốn đổi phải đo lại bằng Python rồi tăng LogicVersion.</summary>
    public static class CorvenParams
    {
        public const string LogicVersion = "corven-2";
        public const double NearMbr = 1.0;
        public const int WinB = 3;
        public const int WinAMax = 5;
        public const int CfAfterFb = 2;
        public const int AgeB = 30;
        public const double SiRatio = 250.0;
        public const int SiRun = 3;
        public const double SiMinVol = 1.0;
        public const bool BFromExhausted = true;
        public const bool SameSession = true;
        public const double DeltaMult = 2.0;
        public const double BubbleMult = 3.0;
        public const double BubbleMin = 10.0;
        public const double TrapMult = 3.0;          // ③e: bóng ngược màu = 3 × nền_ô cố định (plan ③e)
        public const int DivMinLen = 2;
        public const int DivMaxLen = 8;
        public const int NeedSigns = 2;
        public const double CfBody = 0.4;
        public const double CfCloseExt = 0.3;
        public const double CfMinRngMbr = 0.5;
        public const double CfMinDelta = 0.5;
        public const double SlBufTicks = 3.0;
        public const double SlBufMbr = 0.2;
        public const double SlFloorMbr = 1.0;
        public const double SlCapMbr = 4.0;
        public const double RMin = 1.7;
        public const double TpR = 2.0;
        public const int DeadLook = 300;
        public const int BlockFirstBars = 15;
        public const int VetoWindow = 5;
        public const int StopRunK = 3;
        public const int OverlapBars = 30;
        public const double OverlapFrac = 0.5;
        public const int CellBaseN = 100;
        public const int MedDeltaN = 50;
        public const int MedDeltaMin = 10;
        // ---- corven-2: 4 sửa đổi người học chốt 2026-11-09 (research/report/VARIANTS-NGUOI-HOC-2026-11-09.md) = setup_corven.cp_live() ----
        public const bool HoiKhongCham = true;   // thế B: nhịp hồi không cần chạm cạnh
        public const bool BoQuetStop = true;     // bỏ ⛔ nhịp đẩy do quét stop
        public const bool BBoRMin = true;        // thế B: bỏ R sẵn ≥ 1,7 (TP vẫn 2R)
        public const bool TrapHoi = true;        // thế B: dấu hiệu "trap trong nhịp hồi"

        // ---- nhãn trung thực (plan 10.3) — test so đúng chữ ----
        public const string BacktestLine = "Backtest 35 phiên: −0,07R/lệnh, ngang vào ngẫu nhiên (−0,08R) · chạy thử, không phải khuyến nghị";
        public const string TeleWarn = "⚠ Chưa có lợi thế đo được (−0,07R/lệnh, 35 phiên)";
        public const string SettingLabel = "Bật setup CORVEN (chạy thử — backtest −0,07R/lệnh, ngang vào ngẫu nhiên)";
    }

    /// <summary>Bản sao tham số theo instance — CHỈ để unit test dựng ca biên (vd cửa sổ W=4); live luôn dùng mặc định = CorvenParams.</summary>
    public sealed class CorvenCfg
    {
        public double NearMbr = CorvenParams.NearMbr;
        public int WinB = CorvenParams.WinB, WinAMax = CorvenParams.WinAMax, CfAfterFb = CorvenParams.CfAfterFb, AgeB = CorvenParams.AgeB;
        public double SiRatio = CorvenParams.SiRatio; public int SiRun = CorvenParams.SiRun; public double SiMinVol = CorvenParams.SiMinVol;
        public bool BFromExhausted = CorvenParams.BFromExhausted, SameSession = CorvenParams.SameSession;
        public double DeltaMult = CorvenParams.DeltaMult, BubbleMult = CorvenParams.BubbleMult, BubbleMin = CorvenParams.BubbleMin;
        public int DivMinLen = CorvenParams.DivMinLen, DivMaxLen = CorvenParams.DivMaxLen, NeedSigns = CorvenParams.NeedSigns;
        public double CfBody = CorvenParams.CfBody, CfCloseExt = CorvenParams.CfCloseExt, CfMinRngMbr = CorvenParams.CfMinRngMbr, CfMinDelta = CorvenParams.CfMinDelta;
        public double SlBufTicks = CorvenParams.SlBufTicks, SlBufMbr = CorvenParams.SlBufMbr, SlFloorMbr = CorvenParams.SlFloorMbr, SlCapMbr = CorvenParams.SlCapMbr;
        public double RMin = CorvenParams.RMin, TpR = CorvenParams.TpR;
        public int DeadLook = CorvenParams.DeadLook, BlockFirstBars = CorvenParams.BlockFirstBars, VetoWindow = CorvenParams.VetoWindow, StopRunK = CorvenParams.StopRunK;
        public int OverlapBars = CorvenParams.OverlapBars; public double OverlapFrac = CorvenParams.OverlapFrac;
        public bool HoiKhongCham = CorvenParams.HoiKhongCham, BoQuetStop = CorvenParams.BoQuetStop, BBoRMin = CorvenParams.BBoRMin, TrapHoi = CorvenParams.TrapHoi;
        /// <summary>Bộ corven-1 (4 cờ corven-2 tắt) — cho test cũ dựng ca biên của luật đã bỏ.</summary>
        public static CorvenCfg V1() => new CorvenCfg { HoiKhongCham = false, BoQuetStop = false, BBoRMin = false, TrapHoi = false };
    }

    // ======================================================================== đặc trưng từng nến (Feat)
    /// <summary>Đặc trưng từng nến, tính MỘT lần khi nến đóng, không nhìn trước (= setup_corven.Feat, dạng nối dần).</summary>
    public sealed class CorvenFeat
    {
        public double Tick = 0.1;
        public readonly List<CorvenBar> Bars = new();
        public readonly List<long> H = new(), L = new(), O = new(), C = new();
        public readonly List<double> Dl = new(), Mbr = new(), Medd = new(), Base = new();
        public readonly List<ExhResult> ExhTop = new(), ExhBot = new();
        public readonly List<List<SiZone>> Zones = new();
        public readonly List<int> Sm = new(), SStart = new(), Sess = new();
        private readonly Queue<double> _cbQ = new();
        private readonly List<double> _cbSorted = new();
        private readonly List<double> _absD = new();
        public int Count => C.Count;

        /// <summary>Nạp nến i: nền_ô lấy TRƯỚC khi nạp nến (Q11), medΔ gồm nến hiện tại (rolling 50, tối thiểu 10).</summary>
        public void Add(CorvenBar b, double mbr, int sess, int sm, CorvenCfg cfg)
        {
            double baseV = _cbQ.Count >= CorvenParams.CellBaseN ? Of.Median(_cbSorted) : double.NaN;
            var cv = Of.CellValue(b);
            if (cv.HasValue)
            {
                _cbQ.Enqueue(cv.Value);
                int p = _cbSorted.BinarySearch(cv.Value); if (p < 0) p = ~p; _cbSorted.Insert(p, cv.Value);
                if (_cbQ.Count > CorvenParams.CellBaseN) { double old = _cbQ.Dequeue(); _cbSorted.RemoveAt(_cbSorted.BinarySearch(old)); }
            }
            _absD.Add(Math.Abs(b.Delta));
            double medd = BenzoKernel.RollingMedian(_absD, CorvenParams.MedDeltaN, CorvenParams.MedDeltaMin);
            int i = Count;
            int sstart = i == 0 || sess != Sess[i - 1] ? i : SStart[i - 1];
            var ex = Of.Exhaustion(b);
            AddRaw(b, mbr, medd, baseV, sm, sstart, sess, ex.top, ex.bot, Of.StackedZones(b, Tick, cfg.SiRatio, cfg.SiRun, cfg.SiMinVol));
        }

        /// <summary>Nạp với đặc trưng cho sẵn (unit test dựng "thế giới" mbr/medΔ/nền cố định như test Python).</summary>
        public void AddRaw(CorvenBar b, double mbr, double medd, double baseV, int sm, int sstart, int sess,
                           ExhResult top, ExhResult bot, List<SiZone> zones)
        {
            Bars.Add(b); H.Add(b.H); L.Add(b.L); O.Add(b.O); C.Add(b.C); Dl.Add(b.Delta);
            Mbr.Add(mbr); Medd.Add(medd); Base.Add(baseV); Sm.Add(sm); SStart.Add(sstart); Sess.Add(sess);
            ExhTop.Add(top); ExhBot.Add(bot); Zones.Add(zones);
        }
    }

    // ======================================================================== ứng viên
    public sealed class CorvenMoc
    {
        public string Kind = "canh";         // "canh" | "stacked"
        public double Level, Tol, BandLo, BandHi;
        public bool IsZone; public int ZBar; public long ZLo, ZHi;
    }

    public sealed class CorvenSign
    {
        public string Type;   // delta | bong | kiet_suc | stacked | trap
        public string Desc;   // mô tả có số (đúng chuỗi Python)
        public int Bar;       // nến neo
    }

    /// <summary>Một CF ứng viên đã qua ② (= setup_corven.Cand).</summary>
    public sealed class CorvenCand
    {
        public int Cf; public char The; public int S; public int Rid;
        public string InstKey = "", LockKey = "";
        public int Ref, W0;
        public List<CorvenMoc> Mocs = new();
        public List<double> TrapLevels = new();
        public bool Exhausted;
        public double InstTop, InstBottom, InstE; public int InstFb;
        public List<CorvenSign> Signs = new();
        public List<string> Gates = new();
        public long Entry, Sl; public double Tp, Risk, RAvail, Target;
        public string MocUsed = "";

        public static readonly string[] TypeOrder = { "delta", "bong", "kiet_suc", "stacked", "trap" };
        public static string TypeVn(string t) => t switch { "delta" => "Δ", "bong" => "bóng", "kiet_suc" => "kiệt sức", "stacked" => "stacked", "trap" => "trap", _ => t };
        public bool Has(string t) => Signs.Any(x => x.Type == t);
        public int NTypes => Signs.Count;
        /// <summary>= cột `loai` Python: "Δ+bóng".</summary>
        public string TypesText => string.Join("+", TypeOrder.Where(Has).Select(TypeVn));
        /// <summary>= cột `dau_hieu` Python: "Δ: Δ to -36 = 3,8× medΔ (nến 4769) | bóng: …".</summary>
        public string SignsText => string.Join(" | ", Signs.Select(s => $"{TypeVn(s.Type)}: {s.Desc} (nến {s.Bar})"));
    }

    // ======================================================================== ③ + ④ (hàm thuần)
    public static class CorvenRules
    {
        /// <summary>③ — mọi dấu hiệu có nến neo trong cửa sổ [w0, cf], cùng phe S (= find_signs).</summary>
        public static List<CorvenSign> FindSigns(CorvenCand c, CorvenFeat f, CorvenCfg cp)
        {
            int S = c.S, cf = c.Cf;
            var H = f.H; var L = f.L; var O = f.O; var C = f.C; var Dl = f.Dl;
            double tk = f.Tick;
            var sg = new List<CorvenSign>();
            // ③a delta: to (CF hoặc nến trước CF) hoặc ngược giá — tối đa 1
            foreach (int k in new[] { cf, cf - 1 })
            {
                if (k < c.W0 || !(f.Medd[k] > 0)) continue;
                if (Dl[k] * S > 0 && Math.Abs(Dl[k]) >= cp.DeltaMult * f.Medd[k] - 1e-9 && (C[k] - O[k]) * S > 0)
                {
                    string d = $"Δ to {Of.PySigned(Dl[k], 0)} = {Of.PyFixed(Math.Abs(Dl[k]) / f.Medd[k], 1)}× medΔ".Replace('.', ',');
                    sg.Add(new CorvenSign { Type = "delta", Desc = d, Bar = k });
                    break;
                }
            }
            if (!sg.Any(x => x.Type == "delta"))
            {
                bool found = false;
                for (int x = c.W0; x <= cf && !found; x++)
                {
                    foreach (var mo in c.Mocs)
                    {
                        bool reach = S < 0 ? H[x] >= mo.Level - mo.Tol : L[x] <= mo.Level + mo.Tol;
                        if (!reach) continue;
                        var dv = Of.DeltaDivergence(H, L, Dl, x, S, f.Mbr[x], cp.DivMinLen, cp.DivMaxLen);
                        if (dv.ok)
                        {
                            sg.Add(new CorvenSign { Type = "delta", Desc = $"Δ ngược giá ΣΔ {Of.PySigned(dv.sd, 0)}/{x - dv.s} nến", Bar = x });
                            found = true; break;
                        }
                    }
                }
            }
            // ③b bóng đúng phe: nửa nến phía S hoặc trong dải mốc
            bool hasBest = false; double bv = 0, bbs = 0; int bk = 0; long btk = 0;
            for (int k = c.W0; k <= cf; k++)
            {
                double bs = f.Base[k];
                if (double.IsNaN(bs) || double.IsInfinity(bs) || bs <= 0) continue;
                foreach (var (t, v) in Of.Bubbles(f.Bars[k], S, bs, cp.BubbleMult, cp.BubbleMin))
                {
                    bool inPlace = c.Mocs.Any(mo => Of.BubbleInPlace(f.Bars[k], S, t, mo.BandLo, mo.BandHi)) || Of.BubbleInPlace(f.Bars[k], S, t);
                    if (inPlace && (!hasBest || v > bv)) { hasBest = true; bv = v; bk = k; btk = t; bbs = bs; }
                }
            }
            if (hasBest)
            {
                string d = $"bóng {(S > 0 ? "xanh" : "đỏ")} {Of.PyFixed(bv, 0)} @{Of.Px(btk, tk)} ({Of.PyFixed(bv / bbs, 1)}× nền)".Replace('.', ',');
                sg.Add(new CorvenSign { Type = "bong", Desc = d, Bar = bk });
            }
            // ③c kiệt sức phe ngược ở râu, chưa bị quét tới CF
            for (int k = c.W0; k <= cf; k++)
            {
                var r = S < 0 ? f.ExhTop[k] : f.ExhBot[k];
                if (!r.Hit) continue;
                bool swept = false;
                for (int j = k + 1; j <= cf; j++) if (ExhaustionLogic.IsSwept(r.Top, r.Tick, H[j], L[j], 1)) { swept = true; break; }
                if (swept) continue;
                string side = r.Top ? "đỉnh (Ask" : "đáy (Bid";
                sg.Add(new CorvenSign { Type = "kiet_suc", Desc = $"kiệt sức {side} {Of.PyFixed(r.ExtremeVol, 0)}) @{Of.Px(r.Tick, tk)}", Bar = k });
                break;
            }
            // ③d stacked mới cùng hướng S: Body, không Weak, nến tạo vùng đóng phía S; loại vùng đang làm mốc
            bool stk = false;
            for (int k = c.W0; k <= cf && !stk; k++)
            {
                foreach (var z in f.Zones[k])
                {
                    if (z.Side != S || z.Position != SiPosition.Body || z.Weak) continue;
                    long lo = (long)Math.Round(z.Lo / tk), hi = (long)Math.Round(z.Hi / tk);
                    if (c.Mocs.Any(mo => mo.IsZone && mo.ZBar == k && mo.ZLo == lo && mo.ZHi == hi)) continue;
                    if ((S > 0 && C[k] >= hi) || (S < 0 && C[k] <= lo))
                    {
                        sg.Add(new CorvenSign { Type = "stacked", Desc = $"stacked {(S > 0 ? "buy" : "sell")} {z.Levels} mức {Of.Px(lo, tk)}–{Of.Px(hi, tk)}", Bar = k });
                        stk = true; break;
                    }
                }
            }
            // ③e trap phe ngược: quét mốc quan trọng ≥ 1 tick, đóng lại phía S, ô −S trong râu ≥ 3 × nền_ô và ≥ 10
            bool trp = false;
            for (int k = c.W0; k <= cf && !trp; k++)
            {
                double bs = f.Base[k];
                if (double.IsNaN(bs) || double.IsInfinity(bs) || bs <= 0) continue;
                foreach (double lvl in c.TrapLevels)
                {
                    var t = Of.Trap(f.Bars[k], S, lvl, bs, CorvenParams.TrapMult, 1, cp.BubbleMin);
                    if (t.ok)
                    {
                        sg.Add(new CorvenSign { Type = "trap", Desc = $"trap quét {Of.Px(lvl, tk)}, bóng {(S > 0 ? "đỏ" : "xanh")} {Of.PyFixed(t.v, 0)} @{Of.Px(t.tk, tk)}", Bar = k });
                        trp = true; break;
                    }
                }
            }
            // ③f (corven-2, chỉ thế B) trap trong nhịp hồi: ô −S ≥ 3 × nền_ô và ≥ 10 ở nến trước CF trong cửa sổ, CF đóng vượt giá ô.
            // Ô lớn nhất; hoà ⇒ nến sớm hơn, rồi giá xa hướng S hơn (= find_signs ③f).
            if (cp.TrapHoi && c.The == 'B' && !trp)
            {
                bool hb = false; double hv = 0; int hk = 0; long htk = 0;
                for (int k = c.W0; k < cf; k++)
                {
                    double bs = f.Base[k];
                    if (double.IsNaN(bs) || double.IsInfinity(bs) || bs <= 0) continue;
                    foreach (var lv in f.Bars[k].Levels)
                    {
                        double vol = S > 0 ? lv.Bid : lv.Ask;
                        if (!(vol >= 3.0 * bs - 1e-9 && vol >= cp.BubbleMin - 1e-9 && (C[cf] - lv.Tick) * S > 0)) continue;
                        bool better = !hb || vol > hv || (vol == hv && k < hk) || (vol == hv && k == hk && lv.Tick * S > htk * S);
                        if (better) { hb = true; hv = vol; hk = k; htk = lv.Tick; }
                    }
                }
                if (hb) sg.Add(new CorvenSign { Type = "trap", Desc = $"trap hồi, bóng {(S > 0 ? "đỏ" : "xanh")} {Of.PyFixed(hv, 0)} @{Of.Px(htk, tk)}", Bar = hk });
            }
            return sg;
        }

        /// <summary>④ + ⛔ (= eval_order, neo SL "cu_thung"). Ghi c.Gates (mọi cổng trượt, theo thứ tự) + entry/SL/TP/R.
        /// m = null ⇒ không có range/khoá (test hàm thuần như M0 của Python).</summary>
        public static void EvalOrder(CorvenCand c, CorvenFeat f, CorvenCfg cp, CorvenMachine m)
        {
            int S = c.S, cf = c.Cf;
            var H = f.H; var L = f.L; var O = f.O; var C = f.C; var Dl = f.Dl;
            var g = new List<string>();
            double mbr = f.Mbr[cf];
            // 4a nến xác nhận
            long o = O[cf], h = H[cf], l = L[cf], cc = C[cf];
            long rng = h - l;
            double medd = f.Medd[cf];
            bool ok = rng > 0 && (cc - o) * S > 0 && Math.Abs(cc - o) >= cp.CfBody * rng - 1e-9
                      && (S > 0 ? h - cc : cc - l) <= cp.CfCloseExt * rng + 1e-9
                      && rng >= cp.CfMinRngMbr * mbr - 1e-9
                      && Dl[cf] * S >= 0 && !double.IsNaN(medd) && Math.Abs(Dl[cf]) >= cp.CfMinDelta * medd - 1e-9;
            if (!ok) g.Add("g4a_cf");
            // ⛔ kiệt sức chống hướng: 5 nến tới CF có kiệt sức phía S (sell: đáy) chưa bị quét tới CF
            for (int k = Math.Max(0, cf - cp.VetoWindow + 1); k <= cf; k++)
            {
                var r = S < 0 ? f.ExhBot[k] : f.ExhTop[k];
                if (!r.Hit) continue;
                bool swept = false;
                for (int j = k + 1; j <= cf; j++) if (ExhaustionLogic.IsSwept(r.Top, r.Tick, H[j], L[j], 1)) { swept = true; break; }
                if (!swept) { g.Add("v_kiet_suc_chong"); break; }
            }
            // ⛔ nhịp đẩy do quét stop (thế B)
            if (c.The == 'B' && !cp.BoQuetStop)
            {
                int D = S;
                int e = c.Ref;
                for (int j = c.Ref; j <= cf; j++)
                    if (D > 0 ? H[j] > H[e] : L[j] < L[e]) e = j;      // cực trị cú đẩy, hoà ⇒ nến SỚM nhất
                double sd = 0; for (int j = c.Ref; j <= e; j++) sd += Dl[j];
                bool bad = sd * D <= 0;
                double be = f.Base[e];
                if (!bad && cf >= e + cp.StopRunK && !double.IsNaN(be) && !double.IsInfinity(be) && be > 0)
                {
                    foreach (var (t, _) in Of.Bubbles(f.Bars[e], -D, be, cp.BubbleMult, cp.BubbleMin))
                        if (Of.BubbleInPlace(f.Bars[e], -D, t)) { bad = true; break; }
                }
                if (bad) g.Add("v_quet_stop");
            }
            // ⛔ range chồng range (thế A): chỉ đánh từ FailBreak thứ 2 của range mới
            if (c.The == 'A' && m != null && m.Chong(c.Rid))
            {
                int nfb = m.FbBars.TryGetValue(c.Rid, out var lst) ? lst.Count(x => x <= c.InstFb) : 0;
                if (nfb < 2) g.Add("v_chong_range");
            }
            // 4b SL
            double buf = Math.Max(cp.SlBufTicks, cp.SlBufMbr * mbr);
            double raw;
            if (c.The == 'A')
            {
                if (S > 0) { long mn = long.MaxValue; for (int j = c.Ref; j <= cf; j++) mn = Math.Min(mn, L[j]); raw = mn - buf; }
                else { long mx = long.MinValue; for (int j = c.Ref; j <= cf; j++) mx = Math.Max(mx, H[j]); raw = mx + buf; }
                c.MocUsed = "canh";
            }
            else
            {
                var edge = c.Mocs.FirstOrDefault(x => x.Kind == "canh");
                if (edge != null)
                {
                    if (S > 0) { long mn = long.MaxValue; for (int j = c.W0; j <= cf; j++) mn = Math.Min(mn, L[j]); raw = Math.Min(mn, edge.Level - edge.Tol) - buf; }
                    else { long mx = long.MinValue; for (int j = c.W0; j <= cf; j++) mx = Math.Max(mx, H[j]); raw = Math.Max(mx, edge.Level + edge.Tol) + buf; }
                    c.MocUsed = "canh";
                }
                else
                {
                    CorvenMoc mo = null;
                    foreach (var x in c.Mocs) if (x.Kind == "stacked" && (mo == null || x.ZBar > mo.ZBar)) mo = x;   // vùng mới nhất (hoà ⇒ cái đầu)
                    raw = S > 0 ? mo.ZLo - buf : mo.ZHi + buf;
                    c.MocUsed = $"stacked {Of.Px(mo.ZLo, f.Tick)}–{Of.Px(mo.ZHi, f.Tick)}";
                }
            }
            long ent = C[cf];
            double risk = (ent - raw) * S;
            if (risk < cp.SlFloorMbr * mbr) risk = cp.SlFloorMbr * mbr;
            double slRaw = ent - S * risk;
            long sl = S > 0 ? (long)Math.Floor(slRaw + 1e-9) : (long)Math.Ceiling(slRaw - 1e-9);
            risk = (ent - sl) * S;
            c.Entry = ent; c.Sl = sl; c.Risk = risk;
            if (risk > cp.SlCapMbr * mbr + 1e-9) g.Add("tran_sl");
            // 4c mục tiêu
            double tgt;
            if (c.The == 'A') tgt = S < 0 ? c.InstBottom : c.InstTop;
            else
            {
                double hgt = c.InstTop - c.InstBottom;
                double t1 = c.InstE + S * hgt;
                double? t2 = null; int bestD = -1;
                if (m != null)
                    foreach (var (rid2, d) in m.Deaths)
                    {
                        if (rid2 == c.Rid || d > cf || cf - d > cp.DeadLook) continue;
                        var r2 = m.Eng.Ranges[rid2];
                        if (S > 0 && r2.Bottom > ent && d > bestD) { bestD = d; t2 = r2.Bottom; }
                        if (S < 0 && r2.Top < ent && d > bestD) { bestD = d; t2 = r2.Top; }
                    }
                tgt = t2 == null ? t1 : (S > 0 ? Math.Max(t1, t2.Value) : Math.Min(t1, t2.Value));
            }
            c.Target = tgt;
            c.RAvail = risk > 0 ? (tgt - ent) * S / risk : -1;
            if (c.RAvail < cp.RMin - 1e-9 && !(cp.BBoRMin && c.The == 'B')) g.Add("r_nho");
            c.Tp = ent + S * cp.TpR * risk;
            // 4d giờ (nến cuối phiên: BenzoEngine huỷ lệnh khi thấy khoảng trống)
            int sm = f.Sm[cf];
            if (BenzoCore.InVirtualOpen(sm)) g.Add("chan_1920");
            if (cf - f.SStart[cf] < cp.BlockFirstBars) g.Add("dau_phien");
            // nến cuối phiên (plan 12.2-Q2): nến mở 16:59 ET (sm ≥ 1379) = nến M1 cuối của phiên 18:00→17:00 ET — cách NHÂN QUẢ duy nhất
            // để code luật 4d "nến cuối phiên không vào" (Python nhìn trước). Huỷ ở BenzoEngine.EndSession giữ làm lưới dự phòng.
            if (sm >= LastBarSm) g.Add("cuoi_phien");
            c.Gates = g;
        }

        /// <summary>sm của nến M1 cuối phiên CME (mở 16:59 ET).</summary>
        public const int LastBarSm = 1379;

        /// <summary>Danh sách cổng CHÍNH THỨC của CSV ứng viên (plan 10.4.2 + "thế đã có lệnh" + "cuối phiên", 12.1-7a/12.2-Q1-Q2):
        /// 2 cổng ③ + mọi giá trị GateVn + "tin USD" + "thế đã có lệnh" (DetectorCorven) + "đang có lệnh" (engine). README phải liệt kê đúng tập này.</summary>
        public static readonly string[] AllGateLabels =
        {
            "③ 0 loại", "③ 1 loại", "④ CF", "④ R<1,7", "④ trần SL", "⛔ veto kiệt sức", "⛔ quét stop", "⛔ chồng range",
            "chặn giờ", "cuối phiên", "tin USD", "thế đã có lệnh", "đang có lệnh",
        };
        public static readonly string[] GateCodes = { "g4a_cf", "r_nho", "tran_sl", "v_kiet_suc_chong", "v_quet_stop", "v_chong_range", "chan_1920", "dau_phien", "cuoi_phien", "tin_usd" };

        /// <summary>Nhãn cổng cho CSV ứng viên bị loại (plan 10.4).</summary>
        public static string GateVn(string g) => g switch
        {
            "g4a_cf" => "④ CF",
            "r_nho" => "④ R<1,7",
            "tran_sl" => "④ trần SL",
            "v_kiet_suc_chong" => "⛔ veto kiệt sức",
            "v_quet_stop" => "⛔ quét stop",
            "v_chong_range" => "⛔ chồng range",
            "chan_1920" => "chặn giờ",
            "dau_phien" => "chặn giờ",
            "cuoi_phien" => "cuối phiên",
            "tin_usd" => "tin USD",
            _ => g
        };
    }

    // ======================================================================== máy trạng thái ①② (Step2Machine)
    public sealed class CorvenMachine
    {
        public readonly CorvenCfg Cfg;
        public readonly RangeLogic Eng;
        public readonly CorvenFeat F;

        private sealed class InstA { public int Rid, E, S, Ref, Fb; public double Top, Bottom, Tol; }
        private sealed class ZoneTr { public int Bar, D; public long Lo, Hi; public double LoP, HiP; public int FirstTouch = -1, FirstCt = -1; }
        private sealed class InstB
        {
            public int Rid, D, Ref, Bc; public double E, Top, Bottom, Tol; public bool Exhausted;
            public bool Suspended; public int NSuspend; public long PushExt; public int BrokenAt = -1;
            public List<ZoneTr> Zones = new();
        }

        private readonly List<InstA> _liveA = new();
        private readonly List<InstB> _liveB = new();
        private (int idx, long p)? _lastPh, _lastPl;
        /// <summary>(range, nến chuyển DEAD lần đầu) theo thứ tự ghi nhận (= dict death Python).</summary>
        public readonly List<(int rid, int bar)> Deaths = new();
        private readonly HashSet<int> _deathSet = new();
        public readonly Dictionary<int, int> Birth = new();
        public readonly Dictionary<int, List<int>> FbBars = new();
        private readonly List<RangeState> _prevState = new();

        public CorvenMachine(double tick, CorvenCfg cfg = null)
        {
            Cfg = cfg ?? new CorvenCfg();
            Eng = new RangeLogic(tick);
            F = new CorvenFeat { Tick = tick };
        }

        private bool Same(int a, int b) => !Cfg.SameSession || F.Sess[a] == F.Sess[b];
        public double TolNow(int i) => Math.Max(Eng.P.MinTolTicks, Eng.P.TolK * F.Mbr[i]);

        /// <summary>⛔ range chồng range: range sinh trong ≤ 30 nến sau khi một range khác chết và chồng ≥ 50 % chiều cao (của range mới).
        /// Python tính sau cả file (giá trị cạnh range cũ CUỐI CÙNG); ở đây tính tại lúc xét (không nhìn trước).</summary>
        public bool Chong(int rid)
        {
            if (!Birth.TryGetValue(rid, out int bi)) return false;
            var r = Eng.Ranges[rid];
            double h = r.Top0 - r.Bottom0;
            foreach (var (rid2, d) in Deaths)
            {
                if (rid2 == rid || d > bi || bi - d > Cfg.OverlapBars) continue;
                var r2 = Eng.Ranges[rid2];
                double ov = Math.Min(r.Top0, r2.Top) - Math.Max(r.Bottom0, r2.Bottom);
                if (h > 0 && ov >= Cfg.OverlapFrac * h) return true;
            }
            return false;
        }

        /// <summary>Nạp MỘT nến đã đóng; trả các CF ứng viên của chính nến này (đã qua ②, đã tính ③ ④),
        /// theo thứ tự xét của Python (thế A trước thế B, rồi theo range, rồi theo thứ tự sinh thế).</summary>
        public List<CorvenCand> Feed(CorvenBar bar, int sess, int sm)
        {
            int i = bar.Idx;
            if (i != F.Count) throw new InvalidOperationException($"CorvenMachine.Feed phải tuần tự: nhận {i}, mong {F.Count}");
            _prevState.Clear(); foreach (var r in Eng.Ranges) _prevState.Add(r.State);
            int nEv = Eng.Events.Count;
            Eng.FeedTicks(bar.O, bar.H, bar.L, bar.C);
            for (int k = 0; k < _prevState.Count; k++)
            {
                var r = Eng.Ranges[k];
                if (_prevState[k] != RangeState.Dead && r.State == RangeState.Dead && _deathSet.Add(r.Id)) Deaths.Add((r.Id, i));
            }
            F.Add(bar, Eng.Mbr, sess, sm, Cfg);
            var H = F.H; var L = F.L; var C = F.C;
            if (i >= 2)
            {
                int j = i - 1;
                if (H[j] > H[j - 1] && H[j] >= H[i]) _lastPh = (j, H[j]);
                if (L[j] < L[j - 1] && L[j] <= L[i]) _lastPl = (j, L[j]);
            }
            var evs = new List<RangeEvent>();
            for (int k = nEv; k < Eng.Events.Count; k++) evs.Add(Eng.Events[k]);
            var cands = new List<CorvenCand>();

            // ---------- thế A đang sống (CF = fb+1, fb+2) ----------
            foreach (var a in _liveA.ToList())
            {
                if (i == a.Fb) continue;
                var r = Eng.Ranges[a.Rid];
                bool okSeq = i - a.Fb <= Cfg.CfAfterFb && i - a.Ref <= Cfg.WinAMax - 1 && Same(i, a.Fb)
                             && r.State == RangeState.Active && !evs.Any(x => x.RangeId == a.Rid && x.Kind == RangeEventKind.CloseOutside);
                if (!okSeq) { _liveA.Remove(a); continue; }
                ACand(a, i, r.Top, r.Bottom, cands);
                if (i - a.Fb >= Cfg.CfAfterFb || i - a.Ref >= Cfg.WinAMax - 1) _liveA.Remove(a);
            }
            // ---------- thế B đang sống ----------
            foreach (var b in _liveB.ToList())
            {
                if (i == b.Bc) continue;
                BStep(b, i, evs, cands);
            }
            // ---------- sự kiện mới ----------
            foreach (var ev in evs)
            {
                var r = Eng.Ranges[ev.RangeId];
                if (ev.Kind == RangeEventKind.Birth) Birth[ev.RangeId] = i;
                if (ev.Kind == RangeEventKind.BreakConfirmed && r.State == RangeState.Dead && _deathSet.Add(ev.RangeId)) Deaths.Add((ev.RangeId, i));
                if (ev.Kind == RangeEventKind.FailBreak)
                {
                    if (!FbBars.TryGetValue(ev.RangeId, out var fl)) FbBars[ev.RangeId] = fl = new List<int>();
                    fl.Add(i);
                    bool backActive = r.State == RangeState.Active
                                      && !evs.Any(x => x.RangeId == ev.RangeId && x.Kind == RangeEventKind.CloseOutside && x.Bar == i);
                    if (!backActive) continue;    // whipsaw (Q13): không lập thế A
                    var a = new InstA { Rid = ev.RangeId, E = ev.Side, S = -ev.Side, Ref = ev.Ref, Fb = i, Top = ev.Top, Bottom = ev.Bottom, Tol = r.Tol };
                    ACand(a, i, r.Top, r.Bottom, cands);
                    if (Cfg.CfAfterFb > 0 && i - a.Ref < Cfg.WinAMax - 1) _liveA.Add(a);
                }
                else if (ev.Kind == RangeEventKind.BreakConfirmed)
                {
                    bool exhausted = r.State == RangeState.Dead && r.Exhausted;
                    if (exhausted && !Cfg.BFromExhausted) continue;
                    int D = ev.Side;
                    var b = new InstB { Rid = ev.RangeId, D = D, Ref = ev.Ref, Bc = i, E = D > 0 ? ev.Top : ev.Bottom, Top = ev.Top, Bottom = ev.Bottom, Tol = r.Tol, Exhausted = exhausted };
                    long pe = D > 0 ? long.MinValue : long.MaxValue;
                    for (int k = ev.Ref; k <= i; k++) pe = D > 0 ? Math.Max(pe, H[k]) : Math.Min(pe, L[k]);
                    b.PushExt = pe;
                    for (int z = ev.Ref; z <= i; z++) AddZones(b, z);
                    foreach (var z in b.Zones) for (int k = z.Bar + 1; k <= i; k++) ZoneTrack(z, k);
                    _liveB.Add(b);
                    var piv = D < 0 ? _lastPh : _lastPl;
                    double? pivAt = piv.HasValue && piv.Value.idx >= b.Ref ? piv.Value.p : (double?)null;
                    BEval(b, i, pivAt, cands);
                }
            }
            // thứ tự Python: sort ổn định theo (cf, A < B, range)
            var sorted = cands.Select((c, k) => (c, k)).OrderBy(x => x.c.The == 'A' ? 0 : 2).ThenBy(x => x.c.Rid).ThenBy(x => x.k).Select(x => x.c).ToList();
            foreach (var c in sorted)
            {
                c.Signs = CorvenRules.FindSigns(c, F, Cfg);
                CorvenRules.EvalOrder(c, F, Cfg, this);
            }
            return sorted;
        }

        private void ACand(InstA a, int i, double top, double bottom, List<CorvenCand> cands)
        {
            long c = F.C[i];
            if (!(bottom <= c && c <= top)) return;
            double dist = a.E > 0 ? top - c : c - bottom;
            double m = F.Mbr[i];
            bool ok = m > 0 && dist <= Cfg.NearMbr * m + 1e-9;
            if (!ok) return;
            double E = a.E > 0 ? a.Top : a.Bottom;
            cands.Add(new CorvenCand
            {
                Cf = i, The = 'A', S = a.S, Rid = a.Rid, InstKey = $"A|{a.Rid}|{a.Fb}", LockKey = $"{a.Rid}|{a.E}|A",
                Ref = a.Ref, W0 = a.Ref, InstTop = a.Top, InstBottom = a.Bottom, InstE = E, InstFb = a.Fb,
                Mocs = new List<CorvenMoc> { new CorvenMoc { Kind = "canh", Level = E, Tol = a.Tol, BandLo = E - a.Tol, BandHi = E + a.Tol } },
                TrapLevels = new List<double> { E },
            });
        }

        private void AddZones(InstB b, int z)
        {
            foreach (var zz in F.Zones[z])
            {
                if (zz.Side != b.D) continue;
                if (zz.Position != SiPosition.Body || zz.Weak) continue;      // Q3: mốc stacked chỉ Body, không Weak
                b.Zones.Add(new ZoneTr { Bar = z, D = b.D, Lo = (long)Math.Round(zz.Lo / F.Tick), Hi = (long)Math.Round(zz.Hi / F.Tick), LoP = zz.Lo, HiP = zz.Hi });
            }
        }

        private void ZoneTrack(ZoneTr z, int k)
        {
            if (z.FirstTouch < 0 && F.H[k] >= z.Lo && F.L[k] <= z.Hi) z.FirstTouch = k;
            if (z.FirstCt < 0 && StackedImbalanceCalc.CheckEnd(z.D, z.LoP, z.HiP, F.H[k] * F.Tick, F.L[k] * F.Tick, F.C[k] * F.Tick, SiEndMode.CloseThrough) == SiEnd.ClosedThrough)
                z.FirstCt = k;
        }

        private void BStep(InstB b, int i, List<RangeEvent> evs, List<CorvenCand> cands)
        {
            var H = F.H; var L = F.L; var C = F.C;
            if (evs.Any(x => x.RangeId == b.Rid && x.Kind == RangeEventKind.ReEntry) || (b.Exhausted && b.Bottom <= C[i] && C[i] <= b.Top)) { _liveB.Remove(b); return; }
            if (evs.Any(x => x.RangeId == b.Rid && x.Kind == RangeEventKind.Merge)) { _liveB.Remove(b); return; }
            if (i - b.Ref > Cfg.AgeB) { _liveB.Remove(b); return; }
            if (!Same(i, b.Bc)) { _liveB.Remove(b); return; }
            AddZones(b, i);
            foreach (var z in b.Zones) if (z.Bar < i) ZoneTrack(z, i);
            // 1c cấu trúc gần nhất chưa gãy ngược
            var piv = b.D < 0 ? _lastPh : _lastPl;
            double? lvl = null;
            if (piv.HasValue && !(piv.Value.idx < b.Ref || piv.Value.idx <= b.BrokenAt)) lvl = piv.Value.p;
            if (b.Suspended)
            {
                bool newExt = b.D > 0 ? H[i] > b.PushExt : L[i] < b.PushExt;
                if (newExt) { b.Suspended = false; lvl = null; }
            }
            else if (lvl.HasValue)
            {
                if ((b.D < 0 && C[i] > lvl.Value) || (b.D > 0 && C[i] < lvl.Value)) { b.Suspended = true; b.NSuspend++; b.BrokenAt = i; }
            }
            b.PushExt = b.D > 0 ? Math.Max(b.PushExt, H[i]) : Math.Min(b.PushExt, L[i]);
            if (!b.Suspended) BEval(b, i, lvl, cands);
        }

        /// <summary>corven-2 (= Step2Machine._hoi_ok): nến [w0, j−1] đều đóng ngoài range phía D, có ≥ 1 nến hồi (đóng ngược D so
        /// với nến trước, hoặc nến ngược màu), CF đóng ngoài range và vượt giá đóng cực trị của các nến hồi.</summary>
        private bool HoiOk(InstB b, int j, int w0)
        {
            var C = F.C; var O = F.O; int D = b.D; double E = b.E;
            if (w0 >= j || (C[j] - E) * D <= 0) return false;
            bool any = false; long lim = 0;
            for (int k = w0; k < j; k++)
            {
                if ((C[k] - E) * D <= 0) return false;
                bool pb = (C[k] - C[k - 1]) * D < 0 || (C[k] - O[k]) * D < 0;
                if (!pb) continue;
                if (!any || (D > 0 ? C[k] > lim : C[k] < lim)) lim = C[k];
                any = true;
            }
            return any && (C[j] - lim) * D > 0;
        }

        private void BEval(InstB b, int j, double? piv, List<CorvenCand> cands)
        {
            var H = F.H; var L = F.L; var C = F.C;
            int w0 = Math.Max(j - Cfg.WinB + 1, b.Ref + 1);
            double m = F.Mbr[j];
            double E = b.E, tol = b.Tol;
            bool touch = false;
            for (int k = w0; k <= j; k++) if (H[k] >= E - tol && L[k] <= E + tol) { touch = true; break; }
            bool pe = false;
            if (touch)
            {
                double dist = b.D < 0 ? E - C[j] : C[j] - E;
                if (0 < dist && dist <= Cfg.NearMbr * m + 1e-9) pe = true;
            }
            if (!pe && Cfg.HoiKhongCham && HoiOk(b, j, w0)) pe = true;
            double tz = TolNow(j);
            var zm = new List<CorvenMoc>();
            foreach (var z in b.Zones)
            {
                if (j - z.Bar > Cfg.AgeB || z.Bar >= j) continue;
                if (z.FirstCt >= 0 && z.FirstCt <= j) continue;
                int ws = Math.Max(w0, z.Bar + 1);
                if (z.FirstTouch >= 0 && z.FirstTouch < ws) continue;
                bool near = false;
                for (int k = ws; k <= j; k++) if (H[k] >= z.Lo - tz && L[k] <= z.Hi + tz) { near = true; break; }
                if (!near) continue;
                double dz = b.D > 0 ? C[j] - z.Hi : z.Lo - C[j];
                if (dz <= Cfg.NearMbr * m + 1e-9)
                    zm.Add(new CorvenMoc { Kind = "stacked", Level = b.D < 0 ? z.Lo : z.Hi, Tol = tz, BandLo = z.Lo - tz, BandHi = z.Hi + tz, IsZone = true, ZBar = z.Bar, ZLo = z.Lo, ZHi = z.Hi });
            }
            if (!pe && zm.Count == 0) return;
            var mocs = new List<CorvenMoc>();
            if (pe) mocs.Add(new CorvenMoc { Kind = "canh", Level = E, Tol = tol, BandLo = E - tol, BandHi = E + tol });
            mocs.AddRange(zm);
            var tl = new List<double> { E };
            if (piv.HasValue) tl.Add(piv.Value);
            cands.Add(new CorvenCand
            {
                Cf = j, The = 'B', S = b.D, Rid = b.Rid, InstKey = $"B|{b.Rid}|{b.Bc}", LockKey = $"{b.Rid}|{b.D}|B",
                Ref = b.Ref, W0 = w0, Mocs = mocs, TrapLevels = tl, Exhausted = b.Exhausted,
                InstTop = b.Top, InstBottom = b.Bottom, InstE = E, InstFb = b.Bc,
            });
        }

        /// <summary>Range đang sống để vẽ (ACTIVE/PENDING/BROKEN) — chỉ đọc.</summary>
        public IEnumerable<RangeInfo> LiveRanges() => Eng.Ranges.Where(r => r.State != RangeState.Dead);

        /// <summary>Thế B đang sống (để vẽ đường đứt tại mốc cạnh vừa phá): (cạnh tick, hướng D, nến đóng ngoài, đang tạm huỷ 1c).</summary>
        public IEnumerable<(double edge, int dir, int refBar, bool suspended)> LiveB() => _liveB.Select(b => (b.E, b.D, b.Ref, b.Suspended));
    }

    // ======================================================================== detector (cắm vào BenzoEngine)
    /// <summary>Detector CORVEN: Observe nuôi máy mỗi nến đóng; TryDetect chọn ứng viên đầu tiên qua ③ ④ ⛔ + khoá 4d.</summary>
    public sealed class DetectorCorven : IObservingDetector, ITakeAware
    {
        public char Setup => 'C';
        public bool BlockUsOpen = true;                       // Settings "Chặn 19:20–20:30 VN" (mặc định BẬT)
        /// <summary>Chỉ cho đối chiếu Python (ReplayCorven): nến không được vào lệnh (= phiên mỏng/splice Python lọc). Live: luôn true.</summary>
        public Func<int, bool> AllowBar = _ => true;
        public CorvenMachine M { get; private set; }
        public readonly CorvenCfg Cfg;
        private readonly HashSet<string> _usedInst = new(), _usedKey = new();
        private List<CorvenCand> _last = new();
        private int _lastIdx = -1;

        public DetectorCorven(CorvenCfg cfg = null) { Cfg = cfg ?? new CorvenCfg(); }

        /// <summary>Ứng viên (đã qua ②) của nến vừa Observe — cho CSV ứng viên bị loại.</summary>
        public IReadOnlyList<CorvenCand> LastCandidates => _last;
        public int LastIdx => _lastIdx;

        public void Observe(SetupContext ctx, int closedIdx)
        {
            M ??= new CorvenMachine(ctx.Tick, Cfg);
            var b = ctx.Bars[closedIdx];
            double t = ctx.Tick;
            var cb = new CorvenBar
            {
                Idx = closedIdx, Time = b.Time, Delta = b.Delta,
                O = (long)Math.Round(b.O / t), H = (long)Math.Round(b.H / t), L = (long)Math.Round(b.L / t), C = (long)Math.Round(b.C / t),
            };
            foreach (var lv in ctx.GetLevels(closedIdx)) cb.Levels.Add(new ExhLevel((long)Math.Round(lv.Price / t), lv.Bid, lv.Ask, lv.Vol));
            _last = M.Feed(cb, ctx.Zones.SessionAt(closedIdx), ctx.Zones.SmAt(closedIdx));
            _lastIdx = closedIdx;
        }

        /// <summary>Cổng cuối cùng của ứng viên (null = vào được) — dùng chung cho TryDetect và CSV ứng viên.</summary>
        public string FirstGate(CorvenCand c, bool newsBlocked)
        {
            if (c.NTypes < Cfg.NeedSigns) return c.NTypes == 0 ? "③ 0 loại" : c.NTypes == 1 ? "③ 1 loại" : $"③ {c.NTypes} loại";
            foreach (var g in c.Gates)
            {
                if (g == "chan_1920" && !BlockUsOpen) continue;
                return CorvenRules.GateVn(g);
            }
            if (newsBlocked) return "tin USD";
            if (_usedInst.Contains(c.InstKey) || _usedKey.Contains(c.LockKey)) return "thế đã có lệnh";
            return null;
        }

        public Signal TryDetect(SetupContext ctx, int closedIdx)
        {
            if (closedIdx != _lastIdx || !AllowBar(closedIdx)) return null;
            bool news = ctx.IsNewsBlocked(ctx.Bars[closedIdx].Time.AddMinutes(ctx.BarMinutes));
            foreach (var c in _last)
            {
                if (FirstGate(c, news) != null) continue;
                _usedInst.Add(c.InstKey); _usedKey.Add(c.LockKey);
                return ToSignal(c, ctx.Tick);
            }
            return null;
        }

        /// <summary>Lệnh lấy từ cache niêm phong: ghi khoá 4d như khi tự dò ra.</summary>
        public void NotifyTaken(Signal s) { if (!string.IsNullOrEmpty(s.InstKey)) _usedInst.Add(s.InstKey); if (!string.IsNullOrEmpty(s.LockKey)) _usedKey.Add(s.LockKey); }
        /// <summary>Lệnh bị huỷ (vào ở nến cuối phiên — Python không vào): trả khoá 4d.</summary>
        public void NotifyCancelled(Signal s) { _usedInst.Remove(s.InstKey ?? ""); _usedKey.Remove(s.LockKey ?? ""); }

        public Signal ToSignal(CorvenCand c, double tick)
        {
            var f = M.F;
            return new Signal
            {
                Setup = c.The, Side = c.S,
                Entry = Math.Round(c.Entry * tick, 6), Sl = Math.Round(c.Sl * tick, 6), Tp = Math.Round(c.Tp * tick, 6),
                Zone = c.MocUsed, Reason = string.Join(" · ", c.Signs.Select(s => s.Desc)),
                Signs = c.SignsText, NSigns = c.NTypes, SignTypes = c.TypesText, Short = ShortLabel(c),
                RangeLo = Math.Round(c.InstBottom * tick, 6), RangeHi = Math.Round(c.InstTop * tick, 6), Edge = Math.Round(c.InstE * tick, 6),
                BFromExhausted = c.Exhausted, RAvail = c.RAvail, RangeId = c.Rid,
                InstKey = c.InstKey, LockKey = c.LockKey,
                RangeT0 = RangeStartTicks(c.Rid), RangeT1 = f.Bars[c.Cf].Time.Ticks,
                CfH = f.H[c.Cf] * tick, CfL = f.L[c.Cf] * tick, CfBody = Math.Abs(f.C[c.Cf] - f.O[c.Cf]) * tick,
            };
        }

        /// <summary>Giờ mở nến bắt đầu range (ticks UTC) — để vẽ lại hộp range của lệnh cũ (plan 12.1-7c); 0 nếu không rõ.</summary>
        private long RangeStartTicks(int rid)
        {
            if (M == null || rid < 0 || rid >= M.Eng.Ranges.Count) return 0;
            int st = M.Eng.Ranges[rid].Start;
            return st >= 0 && st < M.F.Bars.Count ? M.F.Bars[st].Time.Ticks : 0;
        }

        /// <summary>Nhãn ngắn trên chart: "A sell · Δ ngược + bóng đỏ 18" (loại + số đắt nhất mỗi loại).</summary>
        public static string ShortLabel(CorvenCand c)
        {
            var parts = new List<string>();
            foreach (var s in c.Signs)
            {
                string d = s.Desc;
                switch (s.Type)
                {
                    case "delta": parts.Add(d.StartsWith("Δ to") ? "Δ to" : "Δ ngược"); break;
                    case "bong": { var w = d.Split(' '); parts.Add(w.Length >= 3 ? $"{w[0]} {w[1]} {w[2]}" : d); break; }
                    case "kiet_suc": parts.Add(d.Contains("đỉnh") ? "kiệt sức đỉnh" : "kiệt sức đáy"); break;
                    case "stacked": { var w = d.Split(' '); parts.Add(w.Length >= 3 ? $"stacked {w[2]} mức" : "stacked"); break; }
                    case "trap": parts.Add("trap"); break;
                }
            }
            return $"{c.The} {(c.S > 0 ? "buy" : "sell")} · {string.Join(" + ", parts)}";
        }
    }
}
