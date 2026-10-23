// ============================================================================
//  VclCore — LÕI THUẦN của indicator "Vùng Canh Lệnh" (không tham chiếu Quantower SDK)
// ============================================================================
//  Port 1-1 của research/vcl5.py (engine v4 + độ rộng vùng kẹp theo giá [2, 5]) và research/lan_cham.py
//  (máy trạng thái "một lần chạm" = giá tới vùng, neo vài nến, rồi đi chỗ khác; PLAN-LAN-CHAM.md mục 2.6).
//  Chạy THEO DÒNG: gọi Push(bar, levels) đúng một lần cho mỗi nến M1 ĐÃ ĐÓNG, theo thứ tự thời gian.
//  Bộ vùng sau Push(i) chỉ dùng dữ liệu nến <= i (cấm nhìn trước).
//  Phần lấy từ kernel (giờ VN + bù giờ Mỹ, Value Area 70%, trung vị trượt) copy NGUYÊN logic của
//  benzo-trader/BenzoZones.cs (BenzoKernel) để khớp Python.
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace VungCanhLenhNs
{
    using System;
    using System.Collections.Generic;

    /// <summary>Nến M1 đã đóng. Time = giờ MỞ nến (UTC).</summary>
    public sealed class VBar
    {
        public DateTime Time;
        public double O, H, L, C, Vol;
    }

    /// <summary>Khối lượng của một mức giá trong nến (footprint).</summary>
    public readonly struct VLevel
    {
        public readonly double Price, Vol;
        public VLevel(double price, double vol) { Price = price; Vol = vol; }
    }

    /// <summary>Một vùng đang hiển thị. Side +1 = phía trên giá (kháng cự), −1 = phía dưới (hỗ trợ), 0 = đang chứa giá.
    /// Slot 'K' = đang kiểm tra, 'N' = gần, 'F' = xa vừa phải.</summary>
    public sealed class VZone
    {
        public int Id;
        public double Lo, Hi, Score;
        public int Mask, Conf, NCand, Side;
        public char Slot;
        public bool D10;
        public int FirstBar;
        public DateTime FirstTime;
        // ---- lần chạm (sau Push): đang chạm?, lần thứ k đang chạm, vai lần đang chạm (−1 nếu không), đếm nến thoát,
        //      lịch sử riêng đã chốt (n, đảo, xuyên, chưa rõ, không rõ phía), bin độ rộng 0/1/2 = 2–3 / 3–4 / 4–5 giá
        public bool EpOpen;
        public int EpK, EpVai = -1, DemThoat, N, Dao, Xuyen, ChuaRo, KhongRo, WBin;
        public VZone Clone() => (VZone)MemberwiseClone();
        public string Types()
        {
            var s = new List<string>();
            if ((Mask & Vcl.BitB) != 0) s.Add("B");
            if ((Mask & Vcl.BitB15) != 0) s.Add("B15");
            if ((Mask & Vcl.BitC) != 0) s.Add("C");
            if ((Mask & Vcl.BitD) != 0) s.Add("D");
            return string.Join("+", s);
        }
    }

    /// <summary>Một "đoạn sống" của vùng trên chart: từ lúc vùng vào bộ hiển thị đến lúc rời đi (giá ra khỏi hành lang, vùng bị xuyên
    /// hoặc bị thay). Dùng để vẽ lại lịch sử: mỗi vùng chỉ dài trong khoảng thời gian nó từng có giá trị.</summary>
    public sealed class VSeg
    {
        public int Id, Side;
        public char Slot;
        public double Lo, Hi;
        public DateTime Start, End;
        public bool Live;                 // còn trong bộ hiển thị ở nến mới nhất
        public VSeg Clone() => (VSeg)MemberwiseClone();
    }

    // ---------------------------------------------------------------- hằng số + hàm kernel
    public static class Vcl
    {
        // kernel
        public const double RowStep = 0.1 * 2;          // 1 hàng profile = 2 tick = 0,2 giá
        public const double GapMinutes = 30;            // khoảng trống > 30 phút ⇒ phiên mới
        public const double VaFrac = 0.70;
        public const int MinBarsProf = 300, MinEuBars = 60, MinAsiaBars = 60;
        public const int SmEuStart = 450, SmUsStart = 840;
        public const int UN = 50, UMin = 10;
        public const int SessBars = 1380;
        // gộp (v5: độ rộng vùng kẹp theo GIÁ tuyệt đối [2, 5], không theo u)
        public const double LinkU = 1.0, PadU = 0.5, WminGia = 2.0, WmaxGia = 5.0;
        // lần chạm (PLAN-LAN-CHAM mục 2): dung sai chạm τ, ngưỡng thoát E (giá), số nến yên G để chốt
        public const double EpTau = 0.0, EpExit = 2.0;
        public const int EpGapBars = 5;
        // ứng viên
        public const int SwingM5K = 5, SwingM15K = 3;
        public const double WB = 2, WB15 = 3, WC = 2, WNpoc = 3;
        public const double DWindow = 40.0;
        public const int NakedLookback = 30, NakedMax = 3;
        // điểm / chuyển vai
        public const double TouchK = 0.3; public const int TouchCap = 5;
        public const double FlipMult = 0.7, BreakU = 1.0;
        // chọn bộ
        public const int NearN = 2, KeepNearTop = 3, MinAge = 10;
        public const double FarLoU = 2.0, FarRangeK = 1.5, KeepBonus = 1.5, CorridorPadU = 1.0, CorridorFallbackU = 4.0;
        // loại ứng viên (kind) và bit loại (khớp vcl2.BIT)
        public const int KB = 1, KC = 2, KNpoc = 3, KD = 4, KB15 = 6;
        public const int BitB = 1, BitB15 = 2, BitC = 4, BitD = 8;
        public static int BitOf(int kind) => kind == KB ? BitB : kind == KB15 ? BitB15 : kind == KD ? BitD : BitC;
        public static bool BreakKind(int kind) => kind == KB || kind == KB15 || kind == KC || kind == KNpoc;

        /// <summary>Mỹ đang dùng giờ mùa hè (EDT): CN thứ 2 tháng 3 07:00 UTC → CN đầu tháng 11 06:00 UTC. (copy BenzoKernel.UsDst)</summary>
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

        /// <summary>Phút kể từ 05:00 VN (đã bù giờ Mỹ). (copy BenzoKernel.SmOf)</summary>
        public static int SmOf(DateTime utc, int tzOffset, bool usShift = true)
        {
            int vm = Mod(utc.Hour * 60 + utc.Minute + tzOffset * 60, 1440);
            int adj = (usShift && !UsDst(utc)) ? Mod(vm - 60, 1440) : vm;
            return Mod(adj - 300, 1440);
        }

        /// <summary>0 = Á (sm &lt; 450), 1 = Âu (450 ≤ sm &lt; 840), 2 = Mỹ (sm ≥ 840).</summary>
        public static int PhaseOf(int sm) => sm < SmEuStart ? 0 : sm < SmUsStart ? 1 : 2;
        public static readonly string[] PhaseName = { "Á", "Âu", "Mỹ" };

        /// <summary>Hàng profile của một giá: rint(giá / 0,2) — làm tròn nửa về số chẵn như numpy.</summary>
        public static long RowOf(double price) => (long)Math.Round(price / RowStep, MidpointRounding.ToEven);
        /// <summary>Giá của hàng (như numpy round(x, 6) = rint(x·1e6)/1e6).</summary>
        public static double RowPrice(long row) => Math.Round(row * RowStep * 1e6, MidpointRounding.ToEven) / 1e6;

        /// <summary>Port kernel.value_area (copy BenzoKernel.ValueArea): bắt đầu từ POC, mỗi bước mở 2 hàng mỗi bên, chọn bên lớn hơn
        /// (hòa ⇒ trên), dừng khi ≥ 70%. Chạy trên các hàng ĐANG CÓ (sắp tăng).</summary>
        public static bool ValueArea(IReadOnlyList<double> prices, IReadOnlyList<double> w, out double poc, out double vah, out double val)
        {
            poc = vah = val = double.NaN;
            int n = w.Count;
            if (n == 0) return false;
            double tot = 0; for (int k = 0; k < n; k++) tot += w[k];
            if (tot <= 0) return false;
            int p = 0;
            for (int k = 1; k < n; k++) if (w[k] > w[p]) p = k;
            double acc = w[p], target = tot * VaFrac;
            int lo = p, hi = p;
            while (acc < target && (lo > 0 || hi < n - 1))
            {
                double up = (hi < n - 1 ? w[hi + 1] : 0) + (hi < n - 2 ? w[hi + 2] : 0);
                double dn = (lo > 0 ? w[lo - 1] : 0) + (lo > 1 ? w[lo - 2] : 0);
                if (hi >= n - 1) { acc += dn; lo = Math.Max(0, lo - 2); }
                else if (lo <= 0) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else if (up >= dn) { acc += up; hi = Math.Min(n - 1, hi + 2); }
                else { acc += dn; lo = Math.Max(0, lo - 2); }
            }
            poc = prices[p]; vah = prices[hi]; val = prices[lo];
            return true;
        }

        public static bool ValueAreaOf(Dictionary<long, double> prof, out double poc, out double vah, out double val)
        {
            var keys = new List<long>(prof.Keys); keys.Sort();
            var pr = new double[keys.Count]; var w = new double[keys.Count];
            for (int k = 0; k < keys.Count; k++) { pr[k] = RowPrice(keys[k]); w[k] = prof[keys[k]]; }
            return ValueArea(pr, w, out poc, out vah, out val);
        }

        /// <summary>Trung vị n phần tử cuối (gồm phần tử hiện tại), cần tối thiểu minPeriods.</summary>
        public static double RollingMedian(List<double> src, int n = UN, int minPeriods = UMin)
        {
            int cnt = Math.Min(n, src.Count);
            if (cnt < minPeriods) return double.NaN;
            var a = new double[cnt];
            for (int k = 0; k < cnt; k++) a[k] = src[src.Count - cnt + k];
            Array.Sort(a);
            return cnt % 2 == 1 ? a[cnt / 2] : 0.5 * (a[cnt / 2 - 1] + a[cnt / 2]);
        }

        // ---------------------------------------------------------------- gộp vùng (port vcl5.build_zones)
        /// <summary>Gộp đơn liên kết theo khoảng cách ≤ link·u; biên = min/max ± 0,5u; độ rộng kẹp theo GIÁ [wmin, wmax] (mặc định [2, 5]):
        /// rộng (đã đệm) &gt; wmax ⇒ tách tại khe lớn nhất (đệ quy; dừng nếu 1 mức hoặc mọi mức trùng giá); &lt; wmin ⇒ nới đều quanh tâm;
        /// mảnh không tách được mà vẫn &gt; wmax (chỉ khi u &gt; 5) ⇒ kẹp đều về wmax. Chồng lấn (quét trái → phải): hợp &lt; 2·wmin ⇒ GỘP;
        /// ngược lại cắt ở giữa nhưng dời điểm cắt vào [lo trái + wmin, hi phải − wmin] ⇒ mọi vùng trong [wmin, wmax].
        /// lab[k] = chỉ số vùng (vùng sắp tăng theo giá) của ứng viên k.</summary>
        public static void BuildZones(double[] p, int n, double u, double link, out int[] lab, out double[] lo, out double[] hi,
                                      double wmin = WminGia, double wmax = WmaxGia)
        {
            lab = new int[n];
            if (n == 0) { lo = Array.Empty<double>(); hi = Array.Empty<double>(); return; }
            double pad = PadU * u;
            var o = new int[n];
            for (int k = 0; k < n; k++) o[k] = k;
            Array.Sort(o, (a, b) => { int c = p[a].CompareTo(p[b]); return c != 0 ? c : a.CompareTo(b); });   // = argsort stable
            var ps = new double[n];
            for (int k = 0; k < n; k++) ps[k] = p[o[k]];
            var st = new List<int>(); var en = new List<int>();
            int s0 = 0;
            for (int k = 1; k < n; k++)
                if (ps[k] - ps[k - 1] > link * u) { st.Add(s0); en.Add(k); s0 = k; }
            st.Add(s0); en.Add(n);
            var pst = new List<int>(); var pen = new List<int>();
            for (int g = 0; g < st.Count; g++)
            {
                if ((ps[en[g] - 1] - ps[st[g]]) + 2 * pad > wmax) Split(ps, st[g], en[g], pad, wmax, pst, pen);
                else { pst.Add(st[g]); pen.Add(en[g]); }
            }
            int np = pst.Count;
            var l0 = new double[np]; var h0 = new double[np];
            for (int z = 0; z < np; z++)
            {
                l0[z] = ps[pst[z]] - pad;
                h0[z] = ps[pen[z] - 1] + pad;
                if ((h0[z] - l0[z]) < wmin)
                {
                    double c = (l0[z] + h0[z]) / 2;
                    l0[z] = c - wmin / 2;
                    h0[z] = c + wmin / 2;
                }
                if ((h0[z] - l0[z]) > wmax)
                {
                    double c = (l0[z] + h0[z]) / 2;
                    l0[z] = c - wmax / 2;
                    h0[z] = c + wmax / 2;
                }
            }
            // chồng lấn: quét trái → phải (giữ mọi vùng trong [wmin, wmax])
            var zid = new int[np];
            var zl = new List<double> { l0[0] }; var zh = new List<double> { h0[0] };
            for (int z = 1; z < np; z++)
            {
                int last = zl.Count - 1;
                if (zh[last] > l0[z])
                {
                    if (Math.Max(zh[last], h0[z]) - zl[last] < 2 * wmin)
                    {
                        zh[last] = Math.Max(zh[last], h0[z]);
                        zid[z] = last;
                        continue;
                    }
                    double m = (zh[last] + l0[z]) / 2;
                    m = Math.Min(Math.Max(m, zl[last] + wmin), h0[z] - wmin);
                    zh[last] = m;
                    zl.Add(m); zh.Add(h0[z]);
                }
                else { zl.Add(l0[z]); zh.Add(h0[z]); }
                zid[z] = zl.Count - 1;
            }
            lo = zl.ToArray(); hi = zh.ToArray();
            for (int z = 0; z < np; z++)
                for (int k = pst[z]; k < pen[z]; k++) lab[o[k]] = zid[z];
        }

        private static void Split(double[] ps, int a, int b, double pad, double wmax, List<int> st, List<int> en)
        {
            if (b - a <= 1 || ps[b - 1] - ps[a] + 2 * pad <= wmax || ps[b - 1] == ps[a]) { st.Add(a); en.Add(b); return; }
            int g = a + 1; double best = ps[a + 1] - ps[a];
            for (int k = a + 2; k < b; k++) { double d = ps[k] - ps[k - 1]; if (d > best) { best = d; g = k; } }
            Split(ps, a, g, pad, wmax, st, en);
            Split(ps, g, b, pad, wmax, st, en);
        }

        /// <summary>Bin độ rộng (giá): &lt; 3 → 0 ("2–3"), &lt; 4 → 1 ("3–4"), còn lại → 2 ("4–5"). Khớp lan_cham.wbin.</summary>
        public static int WidthBin(double w) => w < 3 ? 0 : (w < 4 ? 1 : 2);

        /// <summary>Luật chuyển vai cho MỘT ứng viên (port vcl.break_update). side +1 = giá ở trên (hỗ trợ), −1 = giá ở dưới, 0 = chưa rõ.
        /// Đóng xuyên qua CẢ vùng ≥ 1u ⇒ breaks+1, đổi vai. Trả true nếu vừa bị xuyên.</summary>
        public static bool BreakUpdate(ref int side, ref int breaks, double close, double zlo, double zhi, double u)
        {
            if (side == 0)
            {
                if (close > zhi) side = 1;
                else if (close < zlo) side = -1;
            }
            bool brk = (side == 1 && close < zlo - BreakU * u) || (side == -1 && close > zhi + BreakU * u);
            if (brk) { breaks++; side = -side; }
            return brk;
        }
    }

    // ---------------------------------------------------------------- bảng lần chạm (research/report/LAN-CHAM.md, GỘP TRAIN+TEST 61 phiên)
    /// <summary>Tần suất lịch sử của một LẦN CHẠM theo pha phiên × bin độ rộng vùng. % nguyên; −1 = ô có &lt; 100 lần chạm ⇒ dùng EpisodeAll.
    /// Cùng một số cho mọi vùng cùng ô — là MÔ TẢ (vùng giả cùng cỡ cũng cho ≈ chừng ấy), không phải độ mạnh của vùng.</summary>
    public static class VclTables
    {
        public static readonly string[] WBinName = { "2–3", "3–4", "4–5" };
        // Episode[pha 0 Á/1 Âu/2 Mỹ, bin rộng, {đảo chiều, xuyên phá, chưa rõ}]
        public static readonly int[,,] Episode = {
            { { 49, 29, 19 }, { 51, 26, 16 }, { -1, -1, -1 } },
            { { 51, 29, 17 }, { 60, 21, 15 }, { -1, -1, -1 } },
            { { 49, 28, 21 }, { 53, 27, 16 }, { 55, 30, 12 } }
        };
        // EpisodeAll[bin rộng, {đảo, xuyên, chưa rõ}] — mọi pha
        public static readonly int[,] EpisodeAll = { { 50, 28, 19 }, { 54, 25, 16 }, { 55, 30, 11 } };

        /// <summary>% đảo / xuyên / chưa rõ cho (pha, bin rộng); ô thiếu mẫu ⇒ ô "mọi pha" cùng bin; vẫn thiếu ⇒ false.</summary>
        public static bool Lookup(int phase, int wbin, out int dao, out int xuyen, out int chuaRo)
        {
            dao = xuyen = chuaRo = -1;
            if (wbin < 0 || wbin > 2) return false;
            if (phase >= 0 && phase <= 2 && Episode[phase, wbin, 0] >= 0)
            { dao = Episode[phase, wbin, 0]; xuyen = Episode[phase, wbin, 1]; chuaRo = Episode[phase, wbin, 2]; return true; }
            if (EpisodeAll[wbin, 0] >= 0)
            { dao = EpisodeAll[wbin, 0]; xuyen = EpisodeAll[wbin, 1]; chuaRo = EpisodeAll[wbin, 2]; return true; }
            return false;
        }
    }

    // ---------------------------------------------------------------- lần chạm (máy trạng thái PLAN-LAN-CHAM mục 2.6, port lan_cham.episodes)
    /// <summary>Vai của một lần chạm = phía giá TỚI (chốt ở nến bắt đầu). KHÔNG dùng VZone.Side hay side của ứng viên (hai quy ước đó ngược nhau).</summary>
    public enum Vai { KhangCu = 0, HoTro = 1, KhongRo = 2 }
    public enum KetCuc { Dao = 0, Xuyen = 1, ChuaRo = 2, KhongRoPhia = 3 }

    public sealed class EpState { public Vai Vai; public int BatDau, PhiaThoat, DemThoat; }

    /// <summary>Lịch sử riêng của một mã vùng (chỉ sống khi vùng còn hiển thị).</summary>
    public sealed class ZoneHist
    {
        public int N, Dao, Xuyen, ChuaRo, KhongRo;
        public readonly int[] NTheoVai = new int[3], DaoTheoVai = new int[3], XuyenTheoVai = new int[3];
    }

    public readonly struct EpEvent
    {
        public readonly int Id, BatDau, Chot; public readonly Vai Vai; public readonly KetCuc Ket;
        public EpEvent(int id, int batDau, int chot, Vai vai, KetCuc ket) { Id = id; BatDau = batDau; Chot = chot; Vai = vai; Ket = ket; }
    }

    /// <summary>Máy trạng thái "một lần chạm". Gọi Step đúng một lần mỗi nến đóng, SAU khi đã chọn bộ vùng hiển thị của nến đó.
    /// cham = max(C₋,H) ≥ lo−τ và min(C₋,L) ≤ hi+τ; neo = cham hoặc lo−E ≤ C ≤ hi+E; G nến liên tiếp không neo ⇒ chốt theo phía thoát.
    /// Thứ tự trong Step: (1) mã vùng không còn hiển thị ⇒ "rời bộ" (chốt) rồi xoá; (2) nến đầu phiên ⇒ "hết phiên" cho mọi lần chạm đang mở;
    /// (3) máy cho từng vùng đang hiển thị. Chốt khi bị cắt: đã thoát tạm ⇒ theo phía thoát, đang neo ⇒ chưa rõ; vai không rõ ⇒ luôn "không rõ phía".</summary>
    public sealed class EpisodeTracker
    {
        public double Tau = Vcl.EpTau, Exit = Vcl.EpExit;
        public int Gap = Vcl.EpGapBars;
        public bool LogEnabled;
        public readonly List<EpEvent> Log = new();
        private readonly Dictionary<int, EpState> _ep = new();
        private readonly Dictionary<int, ZoneHist> _hist = new();
        private HashSet<int> _live = new();

        public EpState State(int id) => _ep.TryGetValue(id, out var e) ? e : null;
        public ZoneHist Hist(int id) => _hist.TryGetValue(id, out var h) ? h : null;

        public void Step(int t, VBar bar, double cprev, bool newSess, IReadOnlyList<(int id, double lo, double hi)> zones)
        {
            var now = new HashSet<int>();
            foreach (var z in zones) now.Add(z.id);
            foreach (var id in _live)
                if (!now.Contains(id))
                {
                    if (_ep.TryGetValue(id, out var e)) Close(id, e, t);
                    _ep.Remove(id); _hist.Remove(id);
                }
            _live = now;
            if (newSess)
                foreach (var kv in new List<KeyValuePair<int, EpState>>(_ep)) { Close(kv.Key, kv.Value, t); _ep.Remove(kv.Key); }
            foreach (var (id, lo, hi) in zones)
            {
                bool cham = Math.Max(cprev, bar.H) >= lo - Tau && Math.Min(cprev, bar.L) <= hi + Tau;
                bool inl = bar.C >= lo - Exit && bar.C <= hi + Exit;
                if (!_ep.TryGetValue(id, out var e))
                {
                    if (!cham) continue;
                    e = new EpState { Vai = cprev < lo ? Vai.KhangCu : (cprev > hi ? Vai.HoTro : Vai.KhongRo), BatDau = t };
                    _ep[id] = e;
                }
                if (cham || inl) { e.DemThoat = 0; e.PhiaThoat = 0; }
                else
                {
                    e.PhiaThoat = bar.C > hi ? 1 : -1;
                    e.DemThoat++;
                    if (e.DemThoat >= Gap) { Close(id, e, t); _ep.Remove(id); }
                }
            }
        }

        public static KetCuc KetOf(EpState e)
        {
            if (e.Vai == Vai.KhongRo) return KetCuc.KhongRoPhia;
            if (e.DemThoat == 0) return KetCuc.ChuaRo;
            bool dao = (e.Vai == Vai.KhangCu && e.PhiaThoat == -1) || (e.Vai == Vai.HoTro && e.PhiaThoat == 1);
            return dao ? KetCuc.Dao : KetCuc.Xuyen;
        }

        private void Close(int id, EpState e, int chot)
        {
            var k = KetOf(e);
            if (!_hist.TryGetValue(id, out var h)) { h = new ZoneHist(); _hist[id] = h; }
            h.N++; h.NTheoVai[(int)e.Vai]++;
            if (k == KetCuc.Dao) { h.Dao++; h.DaoTheoVai[(int)e.Vai]++; }
            else if (k == KetCuc.Xuyen) { h.Xuyen++; h.XuyenTheoVai[(int)e.Vai]++; }
            else if (k == KetCuc.ChuaRo) h.ChuaRo++;
            else h.KhongRo++;
            if (LogEnabled) Log.Add(new EpEvent(id, e.BatDau, chot, e.Vai, k));
        }
    }


    // ---------------------------------------------------------------- vòng đời lõi khi chạy live (thuần, test được)
    /// <summary>Giữ một VclCore đồng bộ với lịch sử nến của platform. Dựng lại TỪ ĐẦU khi:
    /// (1) chưa có lõi hoặc đổi lệch giờ; (2) lịch sử ngắn đi (platform cắt lịch sử/đổi mã);
    /// (3) footprint (Volume Analysis) vừa sẵn sàng mà lõi đang dựng KHÔNG có footprint — vì ứng viên C (VA/POC hôm qua, VA Âu,
    ///     POC trần) chỉ sinh ở đầu phiên / mốc giờ, đẩy tiếp sẽ không bao giờ có lại; (4) dữ liệu nạp lại khác: giờ nến cuối
    /// đã đẩy không còn khớp nguồn, hoặc nến mới có giờ SỚM hơn nến cuối trong lõi.</summary>
    public sealed class VclFeeder
    {
        public VclCore Core;
        public bool BuiltWithLevels;
        public int Resets;
        public string LastResetReason = "";
        private int _tz = int.MinValue;

        /// <summary>closedCount = số nến ĐÃ ĐÓNG (chỉ số 0..closedCount−1). getBar(i) trả null nếu ô lịch sử không phải nến
        /// (khi đó đẩy nến giả lặp giá trước để giữ chỉ số). levelsReady = footprint đã tính xong. Trả true nếu có đẩy nến mới.</summary>
        public bool Sync(int closedCount, Func<int, VBar> getBar, Func<int, IReadOnlyList<VLevel>> getLevels, bool levelsReady, int tz)
        {
            string why = null;
            if (Core == null) why = "khởi tạo";
            else if (tz != _tz) why = "đổi lệch giờ";
            else if (Core.Bars.Count > closedCount) why = "lịch sử ngắn đi";
            else if (levelsReady && !BuiltWithLevels) why = "footprint vừa sẵn sàng";
            else if (Core.Bars.Count > 0)
            {
                int k = Core.Bars.Count - 1;
                var src = getBar(k);
                if (src != null && src.Time != Core.Bars[k].Time) why = "dữ liệu nạp lại khác (giờ nến cuối không khớp)";
            }
            if (why != null) Reset(why, levelsReady, tz);
            bool pushed = false;
            for (int pass = 0; pass < 2; pass++)
            {
                bool restart = false;
                for (int i = Core.Bars.Count; i < closedCount; i++)
                {
                    var b = getBar(i);
                    var last = Core.Bars.Count > 0 ? Core.Bars[Core.Bars.Count - 1] : null;
                    if (b == null)
                    {
                        double c = last?.C ?? 0;
                        b = new VBar { Time = (last?.Time ?? DateTime.MinValue).AddMinutes(1), O = c, H = c, L = c, C = c };
                    }
                    else if (pass == 0 && last != null && b.Time < last.Time)
                    {
                        Reset("nến mới có giờ sớm hơn nến cuối trong lõi", levelsReady, tz);
                        restart = true;
                        break;
                    }
                    Core.Push(b, levelsReady ? (getLevels(i) ?? Array.Empty<VLevel>()) : Array.Empty<VLevel>());
                    pushed = true;
                }
                if (!restart) break;
            }
            return pushed;
        }

        private void Reset(string why, bool levelsReady, int tz)
        {
            if (Core != null) { Resets++; LastResetReason = why; }
            Core = new VclCore { TzOffset = tz };
            _tz = tz;
            BuiltWithLevels = levelsReady;
        }
    }

    // ---------------------------------------------------------------- engine
    public sealed class VclCore
    {
        public int TzOffset = 7;
        public bool UsShift = true;

        // ---- trạng thái công khai sau mỗi Push ----
        public int Idx = -1;
        public double U = double.NaN, Close = double.NaN;
        public int Sm, Phase;
        public int NRecalc;
        public List<VZone> Display = new();           // bộ vùng đang hiển thị (đã sắp theo thứ tự chọn)
        public readonly List<VBar> Bars = new();
        public readonly EpisodeTracker Episodes = new();   // máy "lần chạm" (PLAN-LAN-CHAM 2.6)
        public readonly List<VSeg> Segs = new();            // lịch sử các đoạn sống của vùng (cũ → mới)
        private readonly Dictionary<int, VSeg> _openSeg = new();

        // ---- ứng viên (mảng song song, chỉ số = thứ tự nạp, giống Python) ----
        private readonly List<double> _price = new(), _w = new();
        private readonly List<int> _kind = new(), _side = new(), _breaks = new(), _touch = new();
        private readonly List<long> _birth = new(), _death = new(), _half = new();
        private readonly List<bool> _alive = new(), _bflag = new();
        private readonly HashSet<long> _dHave = new();
        private readonly List<int> _act = new();

        // ---- phiên ----
        private sealed class SessInfo
        {
            public int Start, End, N;
            public double H = double.NegativeInfinity, L = double.PositiveInfinity, C;
            public bool HasProf; public double Poc = double.NaN, Vah = double.NaN, Val = double.NaN;
            public bool Touched;
            public int NakedCand = -1;             // chỉ số ứng viên POC trần (nếu có) để giết khi bị chạm
            public readonly List<int> NakedCands = new();
        }
        private readonly List<SessInfo> _sess = new();
        private SessInfo _cur;
        private readonly Dictionary<long, double> _full = new(), _eu = new();
        private int _nEu, _nAsia;
        private bool _euDecided, _asiaDecided;
        private double _asiaH = double.NegativeInfinity, _asiaL = double.PositiveInfinity;
        private int _sessNo = -1;
        private readonly List<double> _rng = new();

        // ---- nến gộp M5 / M15 ----
        private sealed class Agg
        {
            public readonly int Minutes, K;
            public readonly List<double> H = new(), L = new();
            public bool Open; public int Sess; public DateTime Bucket; public double CH, CL;
            public Agg(int minutes, int k) { Minutes = minutes; K = k; }
        }
        private readonly Agg _m5 = new Agg(5, Vcl.SwingM5K), _m15 = new Agg(15, Vcl.SwingM15K);

        // ---- chọn bộ ----
        private sealed class Prev { public double Lo, Hi; public int Id; public char Slot; public int Side; }
        private List<Prev> _prev = new();
        private double _anchor;
        private int _nextId;
        private readonly Dictionary<int, (int bar, DateTime t)> _first = new();

        // ================================================================ Push
        public void Push(VBar bar, IReadOnlyList<VLevel> levels)
        {
            int i = Bars.Count;
            Bars.Add(bar);
            Idx = i; Close = bar.C;
            bool newSess = i == 0 || (bar.Time - Bars[i - 1].Time).TotalMinutes > Vcl.GapMinutes;
            Sm = Vcl.SmOf(bar.Time, TzOffset, UsShift);
            Phase = Vcl.PhaseOf(Sm);
            _rng.Add(bar.H - bar.L);
            U = Vcl.RollingMedian(_rng);
            double u = U;

            var newB = new List<(double p, int kind, double w, long death, long half)>();
            var newB15 = new List<(double p, int kind, double w, long death, long half)>();
            var newC = new List<(double p, int kind, double w, long death, long half, SessInfo src)>();

            // ---- phiên mới: chốt phiên cũ, sinh mốc phiên (C) + POC trần ----
            if (newSess)
            {
                CloseAggOnNewBar(_m5, i, newB, true);
                CloseAggOnNewBar(_m15, i, newB15, true);
                if (_cur != null) FinalizeSession();
                _sessNo++;
                _cur = new SessInfo { Start = i };
                _sess.Add(_cur);
                _full.Clear(); _eu.Clear(); _nEu = 0; _nAsia = 0; _euDecided = false; _asiaDecided = false;
                _asiaH = double.NegativeInfinity; _asiaL = double.PositiveInfinity;
                int s = _sessNo;
                if (s >= 1)
                {
                    var ps = _sess[s - 1];
                    newC.Add((ps.H, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((ps.L, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((ps.C, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                }
                // VA hôm qua: phiên trước gần nhất có >= 300 nến và có profile
                for (int q = s - 1; q >= 0; q--)
                {
                    var qs = _sess[q];
                    if (qs.N < Vcl.MinBarsProf || !qs.HasProf) continue;
                    newC.Add((qs.Vah, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((qs.Val, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((qs.Poc, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    break;
                }
                // POC trần: phiên trong 30 phiên trước, >= 300 nến, chưa bị chạm TRƯỚC nến này; giữ 3 cái gần nhất
                var nk = new List<SessInfo>();
                for (int q = Math.Max(s - Vcl.NakedLookback, 0); q < s; q++)
                {
                    var qs = _sess[q];
                    if (qs.N < Vcl.MinBarsProf || !qs.HasProf || qs.Touched) continue;
                    nk.Add(qs);
                }
                for (int k = Math.Max(0, nk.Count - Vcl.NakedMax); k < nk.Count; k++)
                    newC.Add((nk[k].Poc, Vcl.KNpoc, Vcl.WNpoc, long.MaxValue / 4, long.MaxValue / 4, nk[k]));
            }
            else
            {
                CloseAggOnNewBar(_m5, i, newB, false);
                CloseAggOnNewBar(_m15, i, newB15, false);
            }

            // ---- biên Á: chốt ở nến đầu có sm >= 450 ----
            if (!_asiaDecided && Sm >= Vcl.SmEuStart)
            {
                _asiaDecided = true;
                if (_nAsia >= Vcl.MinAsiaBars)
                {
                    newC.Add((_asiaH, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((_asiaL, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                }
            }
            // ---- VA Âu: chốt ở nến đầu có sm >= 840 ----
            if (!_euDecided && Sm >= Vcl.SmUsStart)
            {
                _euDecided = true;
                if (_nEu >= Vcl.MinEuBars && _eu.Count > 0 && Vcl.ValueAreaOf(_eu, out _, out double vh, out double vl))
                {
                    newC.Add((vh, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                    newC.Add((vl, Vcl.KC, Vcl.WC, i + Vcl.SessBars, long.MaxValue / 4, null));
                }
            }
            // ---- cập nhật phiên với nến này ----
            _cur.End = i; _cur.N++; _cur.H = Math.Max(_cur.H, bar.H); _cur.L = Math.Min(_cur.L, bar.L); _cur.C = bar.C;
            bool isEu = Sm >= Vcl.SmEuStart && Sm < Vcl.SmUsStart;
            if (Sm < Vcl.SmEuStart) { _nAsia++; _asiaH = Math.Max(_asiaH, bar.H); _asiaL = Math.Min(_asiaL, bar.L); }
            if (isEu) _nEu++;
            if (levels != null)
                foreach (var lv in levels)
                {
                    long row = Vcl.RowOf(lv.Price);
                    _full[row] = (_full.TryGetValue(row, out var a) ? a : 0) + lv.Vol;
                    if (isEu) _eu[row] = (_eu.TryGetValue(row, out var b2) ? b2 : 0) + lv.Vol;
                }

            // ---- nến gộp: thêm nến này, đóng nếu là phút cuối xô ----
            AddToAgg(_m5, i, bar, newB);
            AddToAgg(_m15, i, bar, newB15);

            // ---- nạp ứng viên sinh tại nến này: B, rồi B15, rồi C (đúng thứ tự Python) ----
            foreach (var c in newB) AddCand(c.p, c.kind, c.w, i, c.death, c.half, bar.C, u);
            foreach (var c in newB15) AddCand(c.p, c.kind, c.w, i, c.death, c.half, bar.C, u);
            foreach (var c in newC)
            {
                int id = AddCand(c.p, c.kind, c.w, i, c.death, c.half, bar.C, u);
                if (c.src != null) c.src.NakedCands.Add(id);
            }
            // ---- D: số tròn bội 10 trong close ± 40, sinh khi lần đầu lọt cửa sổ ----
            long v0 = (long)Math.Ceiling((bar.C - Vcl.DWindow) / 10.0) * 10, v1 = (long)Math.Floor(bar.C + Vcl.DWindow);
            for (long v = v0; v <= v1; v += 10)
            {
                if (!_dHave.Add(v)) continue;
                double w = v % 100 == 0 ? 3.0 : (v % 50 == 0 ? 2.0 : 1.0);
                AddCand(v, Vcl.KD, w, i, long.MaxValue / 4, long.MaxValue / 4, double.NaN, double.NaN, initSide: false);
            }
            // ---- POC trần bị chạm ở nến này ⇒ chết ngay (death = i) ----
            for (int q = 0; q < _sess.Count - 1; q++)
            {
                var qs = _sess[q];
                if (qs.Touched || !qs.HasProf) continue;
                if (bar.L <= qs.Poc && qs.Poc <= bar.H)
                {
                    qs.Touched = true;
                    foreach (var id in qs.NakedCands) _death[id] = Math.Min(_death[id], i);
                }
            }
            // ---- bỏ ứng viên hết tuổi ----
            for (int k = 0; k < _alive.Count; k++) if (_alive[k] && _death[k] <= i) _alive[k] = false;

            double cprev = newSess ? bar.O : Bars[i - 1].C;
            if (double.IsNaN(u) || u <= 0)
            {
                _prev = new List<Prev>(); Display = new List<VZone>();
                UpdateSegs(bar.Time, Display);
                Episodes.Step(i, bar, cprev, newSess, Array.Empty<(int, double, double)>());
                return;
            }

            // ---- gộp lần 1, đếm chạm, chuyển vai ----
            ActiveList();
            int n = _act.Count;
            var pr = new double[n];
            for (int k = 0; k < n; k++) pr[k] = _price[_act[k]];
            Vcl.BuildZones(pr, n, u, Vcl.LinkU, out int[] lab, out double[] zlo, out double[] zhi);
            if (i > 0 && !newSess && n > 0)
            {
                double c0 = Bars[i - 1].C;
                for (int k = 0; k < n; k++)
                {
                    int z = lab[k];
                    if (bar.C >= zlo[z] && bar.C <= zhi[z] && (c0 < zlo[z] || c0 > zhi[z])) _touch[_act[k]]++;
                }
            }
            for (int k = 0; k < _bflag.Count; k++) _bflag[k] = false;
            for (int k = 0; k < n; k++)
            {
                int id = _act[k];
                if (!Vcl.BreakKind(_kind[id])) continue;
                int sd = _side[id], bk = _breaks[id];
                bool x = Vcl.BreakUpdate(ref sd, ref bk, bar.C, zlo[lab[k]], zhi[lab[k]], u);
                _side[id] = sd; _breaks[id] = bk;
                if (x) _bflag[id] = true;
                if (bk >= 2) _alive[id] = false;
            }

            // ---- gộp lần 2 + điểm ----
            ActiveList();
            n = _act.Count;
            pr = new double[n];
            for (int k = 0; k < n; k++) pr[k] = _price[_act[k]];
            Vcl.BuildZones(pr, n, u, Vcl.LinkU, out lab, out zlo, out zhi);
            int nz = zlo.Length;
            var score = new double[nz]; var mask = new int[nz]; var ncand = new int[nz]; var notD10 = new int[nz];
            var brkZ = new bool[nz]; var bestVal = new double[nz]; var bestBirth = new long[nz];
            for (int z = 0; z < nz; z++) { bestVal[z] = double.NegativeInfinity; bestBirth[z] = long.MaxValue; }
            for (int k = 0; k < n; k++)
            {
                int id = _act[k], z = lab[k];
                double val = _w[id] * (i >= _half[id] ? 0.5 : 1.0) * (1 + Vcl.TouchK * Math.Min(_touch[id], Vcl.TouchCap)) * Math.Pow(Vcl.FlipMult, _breaks[id]);
                score[z] += val;
                mask[z] |= Vcl.BitOf(_kind[id]);
                ncand[z]++;
                if (!(_kind[id] == Vcl.KD && _w[id] == 1.0)) notD10[z]++;
                if (_bflag[id]) brkZ[z] = true;
                // ứng viên mạnh nhất (hoà ⇒ sinh sớm nhất)
                if (val > bestVal[z] || (val == bestVal[z] && _birth[id] < bestBirth[z])) { bestVal[z] = val; bestBirth[z] = _birth[id]; }
            }
            var zage = new long[nz];
            for (int z = 0; z < nz; z++) zage[z] = i - bestBirth[z];

            // ---- biên độ phiên trước ----
            double prange;
            if (_sessNo >= 1) { var ps = _sess[_sessNo - 1]; prange = ps.H - ps.L; }
            else prange = Math.Max(_cur.H - _cur.L, 10 * u);
            double maxd = Vcl.FarRangeK * prange;

            // ---- chọn bộ ----
            var sel = CorridorUpdate(zlo, zhi, score, notD10, brkZ, zage, bar.C, u, maxd, out bool rc);
            if (rc) NRecalc++;
            var disp = new List<VZone>();
            var np = new List<Prev>();
            foreach (var (z, slot, id0, sd) in sel)
            {
                int id = id0;
                if (id < 0) id = _nextId++;
                if (!_first.ContainsKey(id)) _first[id] = (i, bar.Time);
                var f = _first[id];
                int conf = 0; for (int bb = mask[z]; bb != 0; bb >>= 1) conf += bb & 1;
                disp.Add(new VZone
                {
                    Id = id, Lo = zlo[z], Hi = zhi[z], Score = score[z], Mask = mask[z], Conf = conf, NCand = ncand[z],
                    Side = sd, Slot = slot, D10 = notD10[z] == 0, FirstBar = f.bar, FirstTime = f.t
                });
                np.Add(new Prev { Lo = zlo[z], Hi = zhi[z], Id = id, Slot = slot, Side = sd });
            }
            _prev = np;
            Display = disp;
            UpdateSegs(bar.Time, disp);

            // ---- lần chạm: chạy SAU khi chốt bộ của nến này, dùng biên hiện tại ----
            var zl = new List<(int, double, double)>(disp.Count);
            foreach (var z in disp) zl.Add((z.Id, z.Lo, z.Hi));
            Episodes.Step(i, bar, cprev, newSess, zl);
            foreach (var z in disp)
            {
                var e = Episodes.State(z.Id); var h = Episodes.Hist(z.Id);
                z.EpOpen = e != null; z.EpVai = e != null ? (int)e.Vai : -1; z.DemThoat = e?.DemThoat ?? 0;
                if (h != null) { z.N = h.N; z.Dao = h.Dao; z.Xuyen = h.Xuyen; z.ChuaRo = h.ChuaRo; z.KhongRo = h.KhongRo; }
                z.EpK = z.EpOpen ? z.N + 1 : 0;
                z.WBin = Vcl.WidthBin(z.Hi - z.Lo);
            }
        }

        private void UpdateSegs(DateTime t, List<VZone> disp)
        {
            var keep = new HashSet<int>();
            foreach (var z in disp)
            {
                keep.Add(z.Id);
                if (_openSeg.TryGetValue(z.Id, out var sg) && sg.Lo == z.Lo && sg.Hi == z.Hi && sg.Side == z.Side) { sg.End = t; sg.Slot = z.Slot; }
                else
                {
                    if (sg != null) sg.Live = false;
                    sg = new VSeg { Id = z.Id, Lo = z.Lo, Hi = z.Hi, Side = z.Side, Slot = z.Slot, Start = t, End = t, Live = true };
                    Segs.Add(sg); _openSeg[z.Id] = sg;
                }
            }
            List<int> gone = null;
            foreach (var kv in _openSeg) if (!keep.Contains(kv.Key)) (gone ??= new List<int>()).Add(kv.Key);
            if (gone != null) foreach (int id in gone) { _openSeg[id].Live = false; _openSeg.Remove(id); }
        }

        /// <summary>Cho test: số ứng viên còn sống của một loại; có ứng viên sống loại kind ở đúng giá p không.</summary>
        public int AliveCount(int kind) { int c = 0; for (int k = 0; k < _alive.Count; k++) if (_alive[k] && _kind[k] == kind) c++; return c; }
        public bool HasAlive(double p, int kind) { for (int k = 0; k < _alive.Count; k++) if (_alive[k] && _kind[k] == kind && _price[k] == p) return true; return false; }

        // ================================================================ chọn bộ (port vcl4.corridor_update / fresh_select)
        private List<int> MatchPrev(double[] lo, double[] hi)
        {
            var js = new List<int>();
            foreach (var p in _prev)
            {
                if (lo.Length == 0) { js.Add(-1); continue; }
                int j = 0; double best = double.NegativeInfinity;
                for (int z = 0; z < lo.Length; z++)
                {
                    double ov = Math.Min(p.Hi, hi[z]) - Math.Max(p.Lo, lo[z]);
                    if (ov > best) { best = ov; j = z; }
                }
                js.Add(best > 0 ? j : -1);
            }
            return js;
        }

        /// <summary>Hành lang = [cạnh dưới vùng gần-1 phía dưới − 1u, cạnh trên vùng gần-1 phía trên + 1u]; thiếu phía nào ⇒ anchor ± 4u.</summary>
        public static void CorridorOf(IList<(int z, char slot, int side)> sel, double[] lo, double[] hi, double anchor, double u, out double bot, out double top)
        {
            int up = -1, dn = -1;
            foreach (var (z, slot, side) in sel)
            {
                if (slot != 'N') continue;
                if (side == 1 && (up < 0 || lo[z] < lo[up])) up = z;
                if (side == -1 && (dn < 0 || hi[z] > hi[dn])) dn = z;
            }
            double pad = Vcl.CorridorPadU * u;
            top = up >= 0 ? hi[up] + pad : anchor + Vcl.CorridorFallbackU * u;
            bot = dn >= 0 ? lo[dn] - pad : anchor - Vcl.CorridorFallbackU * u;
        }

        private List<(int z, char slot, int id, int side)> CorridorUpdate(double[] lo, double[] hi, double[] score, int[] notD10, bool[] brkZ,
                                                                         long[] zage, double c, double u, double maxd, out bool recalc)
        {
            var js = MatchPrev(lo, hi);
            bool trig = _prev.Count == 0;
            if (!trig)
            {
                var seen = new HashSet<int>();
                foreach (var j in js) { if (j < 0 || !seen.Add(j)) { trig = true; break; } }
            }
            if (!trig) foreach (var j in js) if (brkZ[j]) { trig = true; break; }
            if (!trig)
            {
                var cur = new List<(int, char, int)>();
                for (int k = 0; k < _prev.Count; k++) cur.Add((js[k], _prev[k].Slot, _prev[k].Side));
                CorridorOf(cur, lo, hi, _anchor, u, out double bot, out double top);
                trig = c > top || c < bot;
                if (!trig)
                {
                    recalc = false;
                    var keepSel = new List<(int, char, int, int)>();
                    for (int k = 0; k < _prev.Count; k++) keepSel.Add((js[k], _prev[k].Slot, _prev[k].Id, _prev[k].Side));
                    return keepSel;
                }
            }
            recalc = true;
            var emap = new Dictionary<int, int>();
            var keepNear = new HashSet<int>();
            for (int k = 0; k < _prev.Count; k++)
            {
                if (js[k] < 0) continue;
                emap[js[k]] = _prev[k].Id;
                if (_prev[k].Slot == 'N') keepNear.Add(js[k]);
            }
            var eligible = new bool[lo.Length];
            for (int z = 0; z < lo.Length; z++) eligible[z] = zage[z] >= Vcl.MinAge || emap.ContainsKey(z);
            var d10 = new bool[lo.Length];
            for (int z = 0; z < lo.Length; z++) d10[z] = notD10[z] == 0;
            var sel = FreshSelect(lo, hi, score, d10, eligible, c, u, maxd, emap, keepNear);
            _anchor = c;
            var outl = new List<(int, char, int, int)>();
            foreach (var (z, slot, side) in sel) outl.Add((z, slot, emap.TryGetValue(z, out int id) ? id : -1, side));
            return outl;
        }

        /// <summary>Chọn bộ mới: vùng chứa giá (K) + 2 gần (giữ vùng gần cũ nếu còn trong 3 gần nhất) + 1 xa mỗi phía.
        /// Chỉ vùng eligible vào khe gần/xa; vùng chỉ có D-10$ chỉ chiếm khe xa khi không có vùng khác; vùng đang hiển thị ×1,5 điểm ở khe xa.</summary>
        public static List<(int z, char slot, int side)> FreshSelect(double[] lo, double[] hi, double[] score, bool[] d10, bool[] eligible,
                                                                     double c, double u, double maxd, IDictionary<int, int> keep, ISet<int> keepNear)
        {
            var outl = new List<(int, char, int)>();
            int nz = lo.Length;
            int cz = -1;
            for (int z = 0; z < nz; z++) if (lo[z] <= c && c <= hi[z]) { cz = z; break; }
            if (cz >= 0) outl.Add((cz, 'K', 0));
            foreach (int side in new[] { 1, -1 })
            {
                double refp = side > 0 ? (cz >= 0 ? hi[cz] : c) : (cz >= 0 ? lo[cz] : c);
                var idx = new List<int>();
                for (int z = 0; z < nz; z++)
                    if (eligible[z] && (side > 0 ? lo[z] > refp : hi[z] < refp)) idx.Add(z);
                if (side > 0) idx.Sort((a, b) => { int r = lo[a].CompareTo(lo[b]); return r != 0 ? r : a.CompareTo(b); });
                else idx.Sort((a, b) => { int r = (-hi[a]).CompareTo(-hi[b]); return r != 0 ? r : a.CompareTo(b); });
                var top = idx.GetRange(0, Math.Min(Vcl.KeepNearTop, idx.Count));
                var near = new List<int>();
                foreach (var z in top) if (keepNear.Contains(z) && near.Count < Vcl.NearN) near.Add(z);
                foreach (var z in top) if (!near.Contains(z) && near.Count < Vcl.NearN) near.Add(z);
                if (side > 0) near.Sort((a, b) => lo[a].CompareTo(lo[b]));
                else near.Sort((a, b) => (-hi[a]).CompareTo(-hi[b]));
                foreach (var z in near) outl.Add((z, 'N', side));
                double outer = near.Count > 0 ? (side > 0 ? hi[near[near.Count - 1]] : lo[near[near.Count - 1]]) : refp;
                var pool = new List<int>();
                foreach (var z in idx)
                {
                    if (near.Contains(z)) continue;
                    double d = side > 0 ? lo[z] - outer : outer - hi[z];
                    if (Vcl.FarLoU * u <= d && d <= maxd) pool.Add(z);
                }
                if (pool.Count > 0)
                {
                    var nd = pool.FindAll(z => !d10[z]);
                    if (nd.Count > 0) pool = nd;
                    int far = -1; double best = double.NegativeInfinity;
                    foreach (var z in pool)
                    {
                        double sc = score[z] * (keep.ContainsKey(z) ? Vcl.KeepBonus : 1.0);
                        if (sc > best) { best = sc; far = z; }
                    }
                    outl.Add((far, 'F', side));
                }
            }
            return outl;
        }

        // ================================================================ helpers
        private int AddCand(double p, int kind, double w, int birth, long death, long half, double close, double u, bool initSide = true)
        {
            int id = _price.Count;
            _price.Add(p); _kind.Add(kind); _w.Add(w); _birth.Add(birth); _death.Add(death); _half.Add(half);
            int sd = 0;
            if (initSide)
            {
                double dd = close - p;
                double uu = double.IsNaN(u) ? 1.0 : u;
                sd = Math.Abs(dd) < 0.5 * uu ? 0 : (dd > 0 ? 1 : -1);
            }
            _side.Add(sd); _breaks.Add(0); _touch.Add(0); _alive.Add(true); _bflag.Add(false);
            return id;
        }

        private void ActiveList()
        {
            _act.Clear();
            for (int k = 0; k < _alive.Count; k++) if (_alive[k]) _act.Add(k);
        }

        private void FinalizeSession()
        {
            if (_full.Count > 0 && Vcl.ValueAreaOf(_full, out double p, out double vh, out double vl))
            { _cur.HasProf = true; _cur.Poc = p; _cur.Vah = vh; _cur.Val = vl; }
        }

        private static DateTime Floor(DateTime t, int minutes) =>
            new DateTime(t.Year, t.Month, t.Day, t.Hour, t.Minute - t.Minute % minutes, 0, t.Kind);

        /// <summary>Nến M1 mới tới: nếu nến gộp đang mở thuộc xô khác (hoặc phiên khác) ⇒ đóng nó tại nến này (avail = i).</summary>
        private void CloseAggOnNewBar(Agg a, int i, List<(double, int, double, long, long)> outl, bool newSess)
        {
            if (!a.Open) return;
            var b = Floor(Bars[i].Time, a.Minutes);
            if (newSess || b != a.Bucket) CloseAgg(a, i, outl);
        }

        private void AddToAgg(Agg a, int i, VBar bar, List<(double, int, double, long, long)> outl)
        {
            var b = Floor(bar.Time, a.Minutes);
            if (!a.Open) { a.Open = true; a.Bucket = b; a.Sess = _sessNo; a.CH = bar.H; a.CL = bar.L; }
            else { a.CH = Math.Max(a.CH, bar.H); a.CL = Math.Min(a.CL, bar.L); }
            if (bar.Time.AddMinutes(1) >= b.AddMinutes(a.Minutes)) CloseAgg(a, i, outl);   // phút cuối của xô
        }

        private void CloseAgg(Agg a, int birth, List<(double, int, double, long, long)> outl)
        {
            a.Open = false;
            a.H.Add(a.CH); a.L.Add(a.CL);
            int m = a.H.Count - 1, k = a.K, j = m - k;
            if (j < k) return;
            bool isB15 = a.Minutes == 15;
            int kind = isB15 ? Vcl.KB15 : Vcl.KB;
            double w = isB15 ? Vcl.WB15 : Vcl.WB;
            long death = isB15 ? birth + 3L * Vcl.SessBars : birth + 4L * Vcl.SessBars;
            long half = isB15 ? long.MaxValue / 4 : birth + 2L * Vcl.SessBars;
            double hj = a.H[j], lj = a.L[j];
            bool isH = true, isL = true;
            for (int q = j - k; q <= j + k; q++)
            {
                if (a.H[q] > hj) isH = false;
                if (a.L[q] < lj) isL = false;
                if (q < j) { if (!(a.H[q] < hj)) isH = false; if (!(a.L[q] > lj)) isL = false; }
            }
            if (isH) outl.Add((hj, kind, w, death, half));
            if (isL) outl.Add((lj, kind, w, death, half));
        }
    }
}
