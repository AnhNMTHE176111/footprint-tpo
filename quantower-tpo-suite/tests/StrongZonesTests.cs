// Test VÙNG MẠNH (PLAN-VUNG-MANH.md §8) — biên dịch đúng ../ProfileEngine.cs đang dùng build DLL.
//   [3] ca dựng tay (§8.3)   [4] C# = Python trên fixture (§8.1 + 5 ca §8.2)
//   [5] bất biến khung chart + bộ đệm   [6] UI: màu / nhãn / vị trí chữ + render PNG
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Globalization;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Text.Json;
using TpoSuite;

static partial class Tests
{
    static readonly CultureInfo IC = CultureInfo.InvariantCulture;

    // ------------------------------------------------------------------ fixture
    sealed class Fx
    {
        public List<DateTime> T = new(); public List<double> O = new(), H = new(), L = new(), C = new(), V = new();
        public List<KeyValuePair<double, double>>[] Lv;
        public JsonDocument Exp;
        public double Tick = 0.1, Row = 0.2;
        public int N => T.Count;
    }

    static string FxDir() => Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
        "../../../../research/vung_manh_2026-11-25/fixture"));

    static Fx LoadFixture(string pre = "", string exp = "expected_cum2.json", double tick = 0.1)
    {
        string dir = FxDir();
        if (!File.Exists(Path.Combine(dir, pre + "m30_bars.csv"))) return null;
        var f = new Fx { Tick = tick, Row = 2 * tick };
        foreach (var line in File.ReadLines(Path.Combine(dir, pre + "m30_bars.csv")).Skip(1))
        {
            var c = line.Split(',');
            f.T.Add(DateTime.ParseExact(c[1], "yyyy-MM-dd HH:mm:ss", IC));
            f.O.Add(double.Parse(c[2], IC)); f.H.Add(double.Parse(c[3], IC)); f.L.Add(double.Parse(c[4], IC));
            f.C.Add(double.Parse(c[5], IC)); f.V.Add(double.Parse(c[6], IC));
        }
        f.Lv = new List<KeyValuePair<double, double>>[f.N];
        for (int i = 0; i < f.N; i++) f.Lv[i] = new List<KeyValuePair<double, double>>();
        using (var gz = new GZipStream(File.OpenRead(Path.Combine(dir, pre + "m30_levels.csv.gz")), CompressionMode.Decompress))
        using (var r = new StreamReader(gz))
        {
            r.ReadLine();
            string line;
            while ((line = r.ReadLine()) != null)
            {
                var c = line.Split(',');
                f.Lv[int.Parse(c[0], IC)].Add(new KeyValuePair<double, double>(double.Parse(c[1], IC), double.Parse(c[2], IC)));
            }
        }
        f.Exp = JsonDocument.Parse(File.ReadAllText(Path.Combine(dir, exp)));   // GC: HVN dạng cụm v2 (PLAN §13.5c)
        return f;
    }

    // Nến [from..to] của fixture thành một SzSeries (nến cuối = nến đang chạy).
    static SzSeries Series(Fx f, int from, int to, StrongZoneParams p)
    {
        int n = to - from + 1;
        return new SzSeries(f.T.GetRange(from, n), f.O.GetRange(from, n), f.H.GetRange(from, n), f.L.GetRange(from, n),
                            f.C.GetRange(from, n), f.V.GetRange(from, n), i => f.Lv[from + i], f.Tick, f.Row, p);
    }

    static bool Near(double a, double b, double tol) => Math.Abs(a - b) <= tol;

    // ------------------------------------------------------------------ [3] ca dựng tay
    // Hai phiên phẳng (range 1 ⇒ U = 1 cho phiên thứ ba) rồi phiên thứ ba để dựng mẫu.
    static (List<DateTime> t, List<double> o, List<double> h, List<double> l, List<double> c) FlatDays(int nDays, int barsPerDay)
    {
        var t = new List<DateTime>(); var o = new List<double>(); var h = new List<double>(); var l = new List<double>(); var c = new List<double>();
        var t0 = new DateTime(2026, 1, 5, 0, 0, 0);
        for (int d = 0; d < nDays; d++)
            for (int k = 0; k < barsPerDay; k++)
            { t.Add(t0.AddHours(24 * d).AddMinutes(30 * k)); o.Add(100); h.Add(100.5); l.Add(99.5); c.Add(100); }
        return (t, o, h, l, c);
    }

    static List<SzPivot> PivotsOf(List<DateTime> t, List<double> o, List<double> h, List<double> l, List<double> c, StrongZoneParams p)
        => StrongZones.Pivots(new SzSeries(t, o, h, l, c, null, null, 0.1, 0.2, p), p);

    static void SetBar(List<double> o, List<double> h, List<double> l, List<double> c, int i, double hi, double lo)
    { h[i] = hi; l[i] = lo; o[i] = (hi + lo) / 2; c[i] = (hi + lo) / 2; }

    static void HandCases()
    {
        Console.WriteLine("\n[3] Vung manh - ca dung tay (PLAN 8.3)");
        var p = new StrongZoneParams();

        // ---- điểm va đập. Phiên 0,1 phẳng range 1 ⇒ U(phiên 2) = 1. Phiên 2 bắt đầu ở nến 40.
        (List<DateTime> t, List<double> o, List<double> h, List<double> l, List<double> c) Base()
        {
            var b = FlatDays(3, 20);
            for (int i = 40; i < 60; i++) SetBar(b.o, b.h, b.l, b.c, i, 100.5, 99.5);
            SetBar(b.o, b.h, b.l, b.c, 46, 101.0, 100.0);
            SetBar(b.o, b.h, b.l, b.c, 47, 101.5, 100.5);   // đỉnh: đi tới 101,5 − 99,5 = 2 ≥ 1 U
            SetBar(b.o, b.h, b.l, b.c, 48, 101.2, 100.8);
            SetBar(b.o, b.h, b.l, b.c, 49, 101.0, 100.6);
            for (int i = 50; i < 60; i++) SetBar(b.o, b.h, b.l, b.c, i, 100.9, 100.6);
            return b;
        }
        {
            var b = Base(); SetBar(b.o, b.h, b.l, b.c, 50, 100.9, 100.4);   // bật 1,1 U ở nến 50
            var pv = PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Where(q => q.I == 47 && q.Kind == 1).ToList();
            Check(pv.Count == 1 && pv[0].Conf == 50 && pv[0].Price == 101.5, "dinh ro: dung i=47, conf=50", pv.Count > 0 ? $"conf={pv[0].Conf}" : "khong thay");
        }
        {
            var b = Base();   // l thấp nhất sau đỉnh 100,6 ⇒ bật 0,9 U
            Check(!PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Any(q => q.I == 47 && q.Kind == 1), "bat lai 0,9 U -> khong co");
        }
        {
            var b = Base(); SetBar(b.o, b.h, b.l, b.c, 54, 100.9, 100.4);   // nến thứ 7 sau đỉnh
            Check(!PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Any(q => q.I == 47 && q.Kind == 1), "bat o nen thu 7 -> khong co");
            SetBar(b.o, b.h, b.l, b.c, 53, 100.9, 100.4);                   // nến thứ 6 ⇒ có
            var pv = PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Where(q => q.I == 47 && q.Kind == 1).ToList();
            Check(pv.Count == 1 && pv[0].Conf == 53, "bat o nen thu 6 -> co, conf=53");
        }
        {
            var b = Base(); SetBar(b.o, b.h, b.l, b.c, 50, 100.9, 100.4);
            SetBar(b.o, b.h, b.l, b.c, 46, 101.5, 100.0);                   // hai nến cùng High
            var pv = PivotsOf(b.t, b.o, b.h, b.l, b.c, p);
            Check(!pv.Any(q => q.I == 47 && q.Kind == 1), "hai nen cung High -> nen sau khong thanh dinh");
        }
        {
            var b = Base(); SetBar(b.o, b.h, b.l, b.c, 48, 101.6, 100.8); SetBar(b.o, b.h, b.l, b.c, 50, 100.9, 100.4);
            Check(!PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Any(q => q.I == 47 && q.Kind == 1), "gia vuot dinh truoc khi bat du -> khong co");
        }
        {
            var b = Base(); SetBar(b.o, b.h, b.l, b.c, 50, 100.9, 100.4);
            // chỗ nối ở nến 44 (nghỉ 60 phút, nhảy 0,5 ≥ ngưỡng 0,3) ⇒ cửa sổ 41..47 vắt qua chỗ nối
            for (int i = 44; i < 60; i++) b.t[i] = b.t[i].AddMinutes(30);
            b.o[44] = b.c[43] + 0.5;
            var ps = p.Clone(); ps.SpliceJump = 0.3;
            Check(!PivotsOf(b.t, b.o, b.h, b.l, b.c, ps).Any(q => q.I == 47 && q.Kind == 1), "cho noi nam giua cua so -> khong co");
            Check(PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Any(q => q.I == 47 && q.Kind == 1), "  (doi chung: nhay 0,5 duoi nguong 20 -> van co)");
        }
        {
            // đáy đối xứng
            var b = FlatDays(3, 20);
            SetBar(b.o, b.h, b.l, b.c, 46, 100.0, 99.0);
            SetBar(b.o, b.h, b.l, b.c, 47, 99.5, 98.5);
            SetBar(b.o, b.h, b.l, b.c, 48, 99.2, 98.8);
            SetBar(b.o, b.h, b.l, b.c, 49, 99.4, 99.0);
            SetBar(b.o, b.h, b.l, b.c, 50, 99.6, 99.1);
            for (int i = 51; i < 60; i++) SetBar(b.o, b.h, b.l, b.c, i, 99.4, 99.1);
            var pv = PivotsOf(b.t, b.o, b.h, b.l, b.c, p).Where(q => q.I == 47 && q.Kind == -1).ToList();
            Check(pv.Count == 1 && pv[0].Conf == 50 && pv[0].Price == 98.5, "day doi xung: i=47, conf=50");
        }

        // ---- gom cụm
        {
            var g = StrongZones.Cluster(new List<double> { 100, 100.2, 100.4, 103, 103.1 }, 0.5);
            Check(g.Count == 2 && g[0].SequenceEqual(new[] { 0, 1, 2 }) && g[1].SequenceEqual(new[] { 3, 4 }), "gom cum {100;100,2;100,4} {103;103,1}");
            var g2 = StrongZones.Cluster(new List<double> { 100, 100.3, 100.6, 100.9 }, 0.3);
            Check(g2.Count == 2 && g2[0].SequenceEqual(new[] { 0, 1 }) && g2[1].SequenceEqual(new[] { 2, 3 }), "hoa -> neo gia thap: {100;100,3} roi {100,6;100,9}");
        }
        // ---- biên
        {
            var (lo, hi) = StrongZones.Bounds(100, 100, 10, 0.1, p);
            Check(Near(lo, 99.0, 1e-9) && Near(hi, 101.0, 1e-9), "bien: 1 diem 100, u=10 -> 99,0-101,0", $"{lo}-{hi}");
            (lo, hi) = StrongZones.Bounds(100, 102, 10, 0.1, p);
            Check(Near(lo, 99.5, 1e-9) && Near(hi, 102.5, 1e-9), "bien: cum 100-102, u=10 -> 99,5-102,5", $"{lo}-{hi}");
            (lo, hi) = StrongZones.Bounds(100, 101, 7.3, 0.1, p);   // 99,635 → 99,6 ; 101,365 → 101,4
            Check(Near(lo, 99.6, 1e-9) && Near(hi, 101.4, 1e-9), "bien: u le -> noi ra mep tick", $"{lo}-{hi}");
        }
        // ---- VWAP / σ
        {
            var (m, s) = StrongZones.VwapSigma(new[] { 100.0, 102.0 }, new[] { 1.0, 3.0 });
            Check(Near(m, 101.5, 1e-12) && Near(s, 0.8660254, 1e-7), "VWAP {100:1, 102:3} = 101,5, sigma 0,8660254", $"{m} {s}");
        }
        // ---- hộp HVN đủ điều kiện: đo từ MÉP hộp (PLAN §10.4 / §10.5b)
        {
            var hh = Enumerable.Repeat(100.5, 20).ToList(); var ll = Enumerable.Repeat(99.5, 20).ToList();
            var lv = new SzLevel { Name = "hvn_d", IsHvn = true, Lo = 99, Hi = 101, Peak = 100, End = 5 };
            Check(!StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: gia chua tung cach mep 2U -> khong");
            hh[10] = 103.0;
            Check(StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: cach MEP TREN dung 2U -> du");
            hh[10] = 102.9;
            Check(!StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: cach dinh 2,9U nhung cach mep 1,9U -> khong du");
            hh[10] = 100.5; ll[12] = 97.0;
            Check(StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: cach MEP DUOI dung 2U -> du");
            Check(!StrongZones.HvnOk(lv, hh, ll, 11, 1, p), "HVN: roi xa sau nen j -> khong tinh");
            var lv2 = new SzLevel { Name = "hvn_d", IsHvn = true, Lo = 99, Hi = 101, Peak = 100, End = 15 };
            Check(!StrongZones.HvnOk(lv2, hh, ll, 15, 1, p), "HVN: end >= j -> khong");
        }
        HvnClusterHandCases(p);
        HvnBoxDisplayCases(p);
        // ---- nhóm / vàng
        {
            var pg = p.Clone(); pg.GroupEdges = false;
            var a = StrongZones.Grade(new[] { "vah_d", "vwap_d_tren", "hvn_d" }, p);
            var b = StrongZones.Grade(new[] { "vah_d", "vwap_d_tren", "hvn_d" }, pg);
            Check(a.ngroup == 2 && !a.gold && b.ngroup == 3 && b.gold, "{vah_d, vwap_d_tren, hvn_d}: gop 2 nhom khong vang / khong gop 3 nhom vang");
            var c = StrongZones.Grade(new[] { "vah_d", "val_w", "vwap_w" }, p);
            Check(c.ngroup == 3 && !c.hvn && !c.gold, "{vah_d, val_w, vwap_w}: 3 nhom, khong HVN -> khong vang");
            var d = StrongZones.Grade(new[] { "vwap_d", "hvn_w", "hvn_d" }, p);
            Check(d.gold && d.names.SequenceEqual(new[] { "hvn_w", "hvn_d", "vwap_d" }), "{hvn_d, hvn_w, vwap_d} -> vang, dung thu tu ten");
        }
        // ---- phía khi giá trong vùng
        {
            Check(StrongZones.SideOf(new[] { 99.0, 105.0, 101.0 }, 100, 102, 2, 400) == 1, "gia trong vung, nen truoc dong tren -> ho tro");
            Check(StrongZones.SideOf(new[] { 105.0, 99.0, 101.0 }, 100, 102, 2, 400) == -1, "nen truoc dong duoi -> khang cu");
            Check(StrongZones.SideOf(new[] { 101.0, 101.5, 101.0 }, 100, 102, 2, 400) == 0, "khong nen nao dong ngoai -> 0");
            var r = new SzResult { J = 2, Closes = new[] { 101.0, 101.5, 101.0 } };
            r.Clusters.Add(new SzZone { Lo = 100, Hi = 102, N = 3, U = 10, Names = new List<string> { "vwap_d" }, NGroup = 1 });
            var sh = StrongZones.Display(r, 101, p);
            Check(sh.Count == 1 && sh[0].Side == 0 && sh[0].Color == "xam" && sh[0].Label.StartsWith("Vùng · 3 lần") && sh[0].Label.EndsWith("(giá đang trong vùng)"),
                  "phia 0 -> mau xam, dau nhan 'Vung'", sh.Count > 0 ? sh[0].Label : "");
        }
        // ---- lọc chồng
        {
            SzZone Z(double lo, double hi, int ng, int n) => new SzZone
            { Lo = lo, Hi = hi, N = n, U = 10, NGroup = ng, Names = Enumerable.Repeat("vwap_d", 1).ToList(), Newest = 1 };
            var r = new SzResult { J = 0, Closes = new[] { 110.0 } };
            r.Clusters.AddRange(new[] { Z(100, 102, 1, 5), Z(103, 105, 2, 3) });
            var sh = StrongZones.Display(r, 110, p);
            Check(sh.Count == 1 && sh[0].Lo == 103, "chong (cach 0,10U) -> giu vung nhieu nhom hon");
            r.Clusters.Clear(); r.Clusters.AddRange(new[] { Z(100, 102, 1, 5), Z(103, 105, 1, 3) });
            sh = StrongZones.Display(r, 110, p);
            Check(sh.Count == 1 && sh[0].Lo == 100, "cung so nhom -> giu vung nhieu lan va dap hon");
            r.Clusters.Clear(); r.Clusters.AddRange(new[] { Z(100, 102, 1, 5), Z(103.5, 105, 1, 3) });
            sh = StrongZones.Display(r, 110, p);
            Check(sh.Count == 2, "cach dung 0,15U -> giu ca hai", $"{sh.Count}");
        }
        // ---- trần mỗi phía + bán kính
        {
            SzZone Z(double lo, bool gold = false) => new SzZone
            { Lo = lo, Hi = lo + 1, N = 3, U = 10, NGroup = gold ? 3 : 1, Gold = gold, Hvn = gold, Names = new List<string> { "vwap_d" } };
            var r = new SzResult { J = 0, Closes = new[] { 100.0 } };
            foreach (var lo in new[] { 96.0, 92.0, 88.0, 84.0, 80.0 }) r.Clusters.Add(Z(lo));
            var sh = StrongZones.Display(r, 100, p);
            Check(sh.Count == 3 && sh.Select(z => z.Lo).SequenceEqual(new[] { 88.0, 92.0, 96.0 }), "5 ho tro, tran 3 -> 3 vung gan nhat");
            r.Clusters[4] = Z(70.0, true);   // vàng xa nhất, mép gần cách 29 ≤ 40
            sh = StrongZones.Display(r, 100, p);
            Check(sh.Count == 3 && sh.Select(z => z.Lo).SequenceEqual(new[] { 70.0, 92.0, 96.0 }) && sh[0].Color == "vang", "co 1 vung vang xa nhat -> vang + 2 vung gan nhat");
            var rr = new SzResult { J = 0, Closes = new[] { 100.0 } };
            rr.Clusters.Add(Z(140.0));
            Check(StrongZones.Display(rr, 100, p).Count == 1, "mep gan cach 4,0U -> ve");
            rr.Clusters[0] = Z(140.1);
            Check(StrongZones.Display(rr, 100, p).Count == 0, "mep gan cach 4,01U -> khong");
        }
        // ---- ZonePolicy
        Check(ZonePolicy.KeepType("strong", new ZoneFilter()) && ZonePolicy.Role("strong") == "manh", "ZonePolicy: giu 'strong', vai tro 'manh'");
        Check(new[] { "strong", "vwap_week", "vwap_day", "va_edge", "hvn_box", "lvn", "naked_poc" }.All(x => !ZonePolicy.CanMerge("strong", x) && !ZonePolicy.CanMerge(x, "strong")),
              "ZonePolicy: 'strong' khong gop voi loai nao");
        Check(new[] { "hvn_box", "vwap_week", "vwap_day", "va_edge", "lvn", "lvn_week", "naked_poc" }.All(x => !ZonePolicy.CanMerge("hvn_box", x) && !ZonePolicy.CanMerge(x, "hvn_box")),
              "ZonePolicy: 'hvn_box' khong gop voi loai nao");
        Check(ZonePolicy.BaseStrength("strong") == 90 && ZonePolicy.StrongStrength(true) == 98 && !ZonePolicy.IsMarkerType("strong"), "ZonePolicy: diem 90 / vang 98, khong phai lop moc");
        Check(ZonePolicy.CanMerge("lvn", "lvn_week") && !ZonePolicy.CanMerge("va_edge", "lvn"), "ZonePolicy: luat gop cu khong doi");
    }

    // ------------------------------------------------------------------ HVN dạng cụm v2 — ca dựng tay (PLAN §13.5b)
    // Số kỳ vọng chép từ hvn_cum2.clusters (Python) chạy trên đúng các dãy này: tick 0,1, up = 10,0 (100 bước giá) ⇒ h = 5,
    // dn = 300, bề rộng đích 45, tối thiểu 20 bước giá. Dãy bắt đầu ở bước giá 40000 (giá 4000,0); số là chỉ số trong dãy.
    static double[] Seg(params (int n, double v)[] parts) => parts.SelectMany(x => Enumerable.Repeat(x.v, x.n)).ToArray();
    // Dốc số nguyên a → b, n điểm: a ± (|b − a| × i) div (n − 1) — y như ramp() trong ca Python.
    static double[] Ramp(int a, int b, int n)
        => Enumerable.Range(0, n).Select(i => (double)(a + Math.Sign(b - a == 0 ? 1 : b - a) * ((Math.Abs(b - a) * i) / (n - 1)))).ToArray();
    static double[] Cat(params double[][] parts) => parts.SelectMany(x => x).ToArray();

    static void HvnClusterHandCases(StrongZoneParams p)
    {
        const double tick = 0.1, up = 10.0;
        List<SzHvnBox> Run(double[] w, int nBars = 10, double massMin = 0.12)
            => StrongZones.HvnClusters(Enumerable.Range(0, w.Length).Select(i => 40000L + i).ToArray(), w, tick, up, nBars, massMin, p);
        bool Box(SzHvnBox b, int lo, int hi, int peak, int clo, int chi, double mass)
            => Near(b.Lo, (40000 + lo) / 10.0, 1e-9) && Near(b.Hi, (40000 + hi) / 10.0, 1e-9) && Near(b.Peak, (40000 + peak) / 10.0, 1e-9)
               && Near(b.CoreLo, (40000 + clo) / 10.0, 1e-9) && Near(b.CoreHi, (40000 + chi) / 10.0, 1e-9) && Near(b.Mass, mass, 1e-12);
        string Show(List<SzHvnBox> r) => string.Join(" ; ", r.Select(b => $"{b.Lo:0.0}-{b.Hi:0.0} pk {b.Peak:0.0} loi {b.CoreLo:0.0}-{b.CoreHi:0.0} m {b.Mass:R} lon {b.Lon} noi {b.Noi}"));
        double[] Ones(int n) => Enumerable.Repeat(1.0, n).ToArray();
        double[] Hump(double h, int width = 30) => Enumerable.Repeat(h, width).ToArray();

        Check(StrongZones.HvnHalfWindow(up, tick, p) == 5 && StrongZones.HvnAroundTicks(up, tick, p) == 300,
              "HVN cum v2: h = floor(0,05 x 100 + 0,5) = 5, vung xung quanh dn = 300");
        var r = Run(Seg((50, 1), (50, 50), (50, 1)));
        Check(r.Count == 1 && Box(r[0], 52, 97, 55, 53, 96, 0.8846153846153846), "HVN cum v2: than phang giua hai duoi mong -> 1 hop om than", Show(r));
        var spike = Ones(150); spike[75] = 100;
        r = Run(spike);
        Check(r.Count == 0, "HVN cum v2: dinh nhon (1 muc x100) -> noi bi chan o san 50 %, hep hon 0,20 up -> khong co hop", Show(r));
        // lõi hẹp, hai sườn thoải: nới đúng tới 45 bước giá; sườn trái dày hơn được lấy trước
        r = Run(Cat(Ones(40), Ramp(20, 100, 61), Ramp(100, 10, 61).Skip(1).ToArray(), Ones(40)));
        Check(r.Count == 1 && Box(r[0], 76, 121, 100, 83, 115, 0.5509298998569385) && r[0].Hi - r[0].Lo > 4.5 - 1e-9 && r[0].Hi - r[0].Lo < 4.5 + 1e-9,
              "HVN cum v2: loi hep, suon thoai -> noi dung 0,45 up, phia day hon (trai) lay truoc", Show(r));
        var up61 = Ramp(20, 100, 61);
        r = Run(Cat(Ones(40), up61, up61.Reverse().Skip(1).ToArray(), Ones(40)));
        Check(r.Count == 1 && Box(r[0], 77, 122, 100, 83, 117, 0.534297520661157), "HVN cum v2: hai suon doi xung (hoa) -> lay phia gia thap truoc", Show(r));
        // sườn tụt dưới 50 % đỉnh trước khi đủ rộng ⇒ dừng, hộp hẹp hơn đích nhưng ≥ 0,20 up
        r = Run(Seg((40, 1), (10, 30), (28, 100), (10, 30), (40, 1)));
        Check(r.Count == 1 && Box(r[0], 48, 79, 55, 52, 75, 0.8390804597701149) && r[0].Hi - r[0].Lo < 4.5,
              "HVN cum v2: suon tut duoi 50 % dinh -> dung noi, hop hep hon dich", Show(r));
        // bướu bên cạnh qua một đáy: nới dừng trước khi leo quá đáy + 5 % đỉnh
        r = Run(Cat(Ones(40), Ramp(90, 60, 20), Ramp(60, 100, 6).Skip(1).ToArray(), Hump(100, 10), Ones(40)));
        Check(r.Count == 1 && Box(r[0], 52, 74, 69, 62, 71, 0.647391159853772), "HVN cum v2: buou ben canh -> noi dung o day, khong leo sang", Show(r));
        // hai bướu cách nhau dưới / trên 3 up
        r = Run(Cat(Ones(40), Hump(100), Enumerable.Repeat(5.0, 200).ToArray(), Hump(70), Ones(40)));
        Check(r.Count == 1 && Box(r[0], 40, 69, 45, 43, 66, 0.4854368932038835), "HVN cum v2: hai buou cach nhau < 3 up -> chi buou cao", Show(r));
        r = Run(Cat(Ones(40), Hump(100), Enumerable.Repeat(5.0, 320).ToArray(), Hump(70), Ones(40)));
        Check(r.Count == 2 && Box(r[0], 40, 69, 45, 43, 66, 0.4424778761061947) && Box(r[1], 390, 419, 395, 393, 416, 0.30973451327433627)
              && r.All(b => b.Lon && !b.Noi), "HVN cum v2: hai buou cach nhau > 3 up -> 2 hop, buou cao truoc", Show(r));
        // bướu nhỏ (30 % đỉnh lớn nhất) nằm xa, xung quanh mỏng ⇒ thành hộp nhờ nổi bật; đặt giữa vùng dày ⇒ không
        r = Run(Cat(Ones(40), Hump(100, 60), Ones(400), Hump(30), Ones(400)), nBars: 40);
        Check(r.Count == 2 && Box(r[0], 43, 96, 45, 43, 96, 0.6976744186046512) && Box(r[1], 500, 529, 505, 503, 526, 0.11627906976744186)
              && !r[1].Lon && r[1].Noi && r[1].Bars >= 4.5, "HVN cum v2: buou nho xa, xung quanh mong, >= 4,5 nen -> hop (nhanh noi bat)", Show(r));
        r = Run(Cat(Ones(40), Hump(100, 60), Ones(400), Enumerable.Repeat(20.0, 150).ToArray(), Hump(30), Enumerable.Repeat(20.0, 150).ToArray(), Ones(100)), nBars: 40);
        Check(r.Count == 1 && Box(r[0], 43, 96, 45, 43, 96, 0.4017857142857143), "HVN cum v2: cung buou do giua vung day -> khong", Show(r));
        // đủ massMin nhưng không nổi bật ⇒ vẫn nhận (nhánh lớn)
        r = Run(Seg((200, 10), (40, 14), (200, 10)), nBars: 40, massMin: 0.08);
        Check(r.Count == 1 && Box(r[0], 197, 242, 205, 198, 241, 0.13596491228070176) && r[0].Lon && !r[0].Noi,
              "HVN cum v2: hop >= massMin nhung khong noi bat -> van nhan", Show(r));
        // số hộp tối đa theo biên độ profile
        Check(StrongZones.HvnMaxBoxes(1300, 100, p) == 2 && StrongZones.HvnMaxBoxes(1900, 100, p) == 3 && StrongZones.HvnMaxBoxes(3000, 100, p) == 4
              && StrongZones.HvnMaxBoxes(10, 100, p) == 2 && StrongZones.HvnMaxBoxes(100000, 100, p) == 4,
              "HVN cum v2: so hop toi da: 13 up -> 2, 19 up -> 3, 30 up -> 4 (tran 4, san 2)");
        double[] Humps(int k, int gap, int tail) { var x = new List<double>(); for (int i = 0; i < k; i++) { x.AddRange(Ones(gap)); x.AddRange(Hump(100 - 5 * i, 40)); } x.AddRange(Ones(tail)); return x.ToArray(); }
        r = Run(Humps(3, 350, 50), nBars: 200, massMin: 0.08);
        Check(r.Count == 2 && Near(r[0].Lo, 4035.0, 1e-9) && Near(r[1].Lo, 4074.0, 1e-9), "HVN cum v2: 3 buou, profile 12 up -> 2 hop", Show(r));
        r = Run(Humps(5, 300, 300), nBars: 200, massMin: 0.08);
        Check(r.Count == 3 && Near(r[0].Lo, 4030.0, 1e-9) && Near(r[1].Lo, 4064.0, 1e-9) && Near(r[2].Lo, 4098.0, 1e-9), "HVN cum v2: 5 buou, profile 20 up -> 3 hop", Show(r));
        r = Run(Humps(6, 400, 0), nBars: 200, massMin: 0.08);
        Check(r.Count == 4 && Near(r[0].Lo, 4040.0, 1e-9) && Near(r[3].Lo, 4172.0, 1e-9) && Near(r[3].Mass, 0.1452991452991453, 1e-12),
              "HVN cum v2: 6 buou, profile 26 up -> 4 hop", Show(r));
        // bản (giá, khối lượng): cộng dồn theo bước giá, thứ tự bất kỳ
        var lv = new List<KeyValuePair<double, double>>();
        var wv = Seg((50, 1), (50, 50), (50, 1));
        for (int i = wv.Length - 1; i >= 0; i--) { lv.Add(new KeyValuePair<double, double>((40000 + i) / 10.0, wv[i] - 0.5)); lv.Add(new KeyValuePair<double, double>((40000 + i) / 10.0 + 1e-9, 0.5)); }
        r = StrongZones.HvnClusters(lv, tick, up, 10, 0.12, p);
        Check(r.Count == 1 && Box(r[0], 52, 97, 55, 53, 96, 0.8846153846153846), "HVN cum v2: ban (gia, khoi luong) chua sap + trung muc -> nhu ban so nguyen", Show(r));
        Check(StrongZones.HvnClusters(new long[0], new double[0], tick, up, 10, 0.12, p).Count == 0
              && StrongZones.HvnClusters(new long[] { 1, 2 }, new double[] { 5, 5 }, tick, up, 10, 0.12, p).Count == 0
              && StrongZones.HvnClusters(new long[] { 1, 2, 3 }, new double[] { 0, 0, 0 }, tick, up, 10, 0.12, p).Count == 0
              && StrongZones.HvnClusters(new long[] { 1, 2, 3 }, new double[] { 1, 2, 1 }, tick, 0, 10, 0.12, p).Count == 0,
              "HVN cum v2: rong / duoi 3 buoc gia / tong 0 / up 0 -> khong co hop");
    }

    // Lớp hộp HVN hiển thị (PLAN §11, v2 §13.4): đã "rời xa", trong bán kính 8 U, chồng > 50 % ⇒ giữ hộp mới hơn
    // (khác loại ⇒ nhãn "HVN ngày + tuần"), mỗi phía giá tối đa 2 hộp gần nhất, hộp chứa giá luôn giữ.
    static void HvnBoxDisplayCases(StrongZoneParams p)
    {
        int n = 30;
        SzResult R() => new SzResult { J = 20, U = 1.0, Highs = Enumerable.Repeat(100.5, n).ToArray(), Lows = Enumerable.Repeat(99.5, n).ToArray() };
        SzLevel H(string nm, double lo, double hi, int end, double mass = 0.2) => new SzLevel { Name = nm, Lo = lo, Hi = hi, Peak = (lo + hi) / 2, IsHvn = true, End = end, Mass = mass };
        string Show(List<SzHvnShown> b) => string.Join(" ; ", b.Select(x => $"{x.Lo}-{x.Hi} {x.Label} d{x.Dist}"));
        Check(p.HvnRadius == 8.0 && p.HvnMaxSide == 2 && p.Radius == 4.0, "hop HVN: ban kinh rieng 8 U (vung manh van 4 U), toi da 2 hop moi phia");

        var r = R();
        r.Highs[15] = 120; r.Lows[16] = 80;   // sau nến 10 giá từng lên 120 và xuống 80 ⇒ hộp End ≤ 14 đều "đã rời xa"
        r.Levels.Add(new SzLevel { Name = "vwap_d", Lo = 100, Hi = 100 });
        r.Levels.Add(H("hvn_d", 99, 101, 10));      // chứa giá
        r.Levels.Add(H("hvn_d", 99.5, 101.5, 8));   // chồng 75 % hộp nhỏ, cùng loại ⇒ bỏ, nhãn giữ "HVN ngày"
        r.Levels.Add(H("hvn_d", 95, 96, 20));       // End = j ⇒ chưa đủ điều kiện ⇒ không vẽ
        r.Levels.Add(H("hvn_d", 107.9, 108.5, 5));  // mép dưới cách giá 7,9 U ⇒ vẽ
        r.Levels.Add(H("hvn_w", 91.9, 92.5, 5));    // mép trên cách 7,5 U ⇒ vẽ
        r.Levels.Add(H("hvn_d", 108.1, 109, 4));    // cách 8,1 U ⇒ không
        r.Levels.Add(H("hvn_w", 91, 91.85, 6));     // cách 8,15 U ⇒ không
        var b = StrongZones.HvnBoxes(r, 100, p);
        Check(b.Count == 3 && Near(b[0].Lo, 91.9, 1e-12) && b[0].Label == "HVN tuần" && Near(b[0].Dist, 7.5, 1e-12)
              && Near(b[1].Lo, 99, 1e-12) && b[1].Label == "HVN ngày" && b[1].Dist == 0
              && Near(b[2].Lo, 107.9, 1e-12) && Near(b[2].Dist, 7.9, 1e-9),
              "hop HVN: ban kinh 8 U (7,9 U ve, 8,1 U khong); chong cung loai giu hop moi, nhan khong doi", Show(b));
        // ba hộp cùng phía (trên giá) ⇒ giữ hai hộp gần; hộp chứa giá không tính vào trần
        var r2 = R(); r2.Highs[15] = 120;
        r2.Levels.Add(H("hvn_d", 99, 101, 10));
        r2.Levels.Add(H("hvn_d", 102, 103, 9)); r2.Levels.Add(H("hvn_d", 104, 105, 8)); r2.Levels.Add(H("hvn_w", 106, 107, 7));
        b = StrongZones.HvnBoxes(r2, 100, p);
        Check(b.Count == 3 && b.Select(x => x.Lo).SequenceEqual(new[] { 99.0, 102.0, 104.0 }), "hop HVN: 3 hop phia tren -> giu 2 hop gan nhat (+ hop chua gia)", Show(b));
        var r2b = R(); r2b.Lows[16] = 80;
        r2b.Levels.Add(H("hvn_d", 97, 98, 9)); r2b.Levels.Add(H("hvn_d", 95, 96, 8)); r2b.Levels.Add(H("hvn_d", 93, 94, 7));
        b = StrongZones.HvnBoxes(r2b, 100, p);
        Check(b.Count == 2 && b.Select(x => x.Lo).SequenceEqual(new[] { 95.0, 97.0 }), "hop HVN: 3 hop phia duoi -> giu 2 hop gan nhat", Show(b));
        // hộp ngày trùng hộp tuần ⇒ một hộp, nhãn "HVN ngày + tuần", số % của hộp được giữ
        var r3 = R(); r3.Highs[15] = 120;
        r3.Levels.Add(H("hvn_w", 102.1, 103.9, 9, 0.026)); r3.Levels.Add(H("hvn_d", 102, 104, 10, 0.111));
        b = StrongZones.HvnBoxes(r3, 100, p);
        Check(b.Count == 1 && b[0].Name == "hvn_d" && b[0].Label == "HVN ngày + tuần" && Near(b[0].Lo, 102, 1e-12) && Near(b[0].Mass, 0.111, 1e-12),
              "hop HVN: hop ngay trung hop tuan -> 1 hop nhan 'HVN ngay + tuan'", Show(b));
        Check(StrongZones.HvnBoxText(b[0]) == "HVN ngày + tuần · 11 % khối lượng", "hop HVN: chu tren chart 'HVN ngay + tuan · 11 % khoi luong'", StrongZones.HvnBoxText(b[0]));
        // cùng End, chồng nhau ⇒ giữ hộp ngày (và gộp nhãn)
        var r4 = R(); r4.Highs[15] = 120;
        r4.Levels.Add(H("hvn_w", 99, 101, 10)); r4.Levels.Add(H("hvn_d", 99.2, 101.2, 10));
        b = StrongZones.HvnBoxes(r4, 100, p);
        Check(b.Count == 1 && b[0].Name == "hvn_d" && b[0].Label == "HVN ngày + tuần", "hop HVN: cung End, chong nhau -> giu hop ngay, nhan gop", Show(b));
        Check(StrongZones.HvnBoxes(new SzResult(), 100, p).Count == 0 && StrongZones.HvnBoxes(r, double.NaN, p).Count == 0, "hop HVN: ket qua rong / gia NaN -> khong ve");
        var line = StrongZones.HvnSummaryLine(StrongZones.HvnBoxes(r, 100, p), x => x.ToString("0.0", IC));
        Check(line == "Hộp HVN (cụm khối lượng, chưa kiểm định): 99.0–101.0 (HVN ngày) · 91.9–92.5 (HVN tuần) · 107.9–108.5 (HVN ngày)",
              "hop HVN: dong Telegram toi da 3 hop, gan gia truoc", line);
    }

    // ------------------------------------------------------------------ HVN dạng cụm v2 — 19 profile thật (PLAN §13.5a)
    static void HvnClusterFixture()
    {
        Console.WriteLine("\n[3b] HVN dang cum v2 - C# = Python tren 19 profile that (hvn_cum2_cases.json)");
        string path = Path.Combine(FxDir(), "hvn_cum2_cases.json");
        if (!File.Exists(path)) { Check(false, "doc hvn_cum2_cases.json", path); return; }
        var p = new StrongZoneParams();
        using var doc = JsonDocument.Parse(File.ReadAllText(path));
        var pr = doc.RootElement.GetProperty("params");
        double P(string k) => pr.GetProperty(k).GetDouble();
        Check(Near(P("SM"), p.HvnSmooth, 1e-12) && Near(P("X"), p.HvnBody, 1e-12) && Near(P("WT"), p.HvnWidth, 1e-12) && Near(P("XMIN"), p.HvnWidenFloor, 1e-12)
              && Near(P("VD"), p.HvnWidenClimb, 1e-12) && Near(P("DOM"), p.HvnAround, 1e-12) && Near(P("CK"), p.HvnContrast, 1e-12) && Near(P("B"), p.HvnBars, 1e-12)
              && Near(P("Y"), p.HvnMassDay, 1e-12) && Near(P("Y_W"), p.HvnMassWeek, 1e-12) && Near(P("WMIN"), p.HvnMinWidth, 1e-12)
              && pr.GetProperty("MAXC").GetInt32() == p.HvnMaxPerProfile && Near(P("MAXC_STEP"), p.HvnMaxStep, 1e-12) && pr.GetProperty("MAXC_CAP").GetInt32() == p.HvnMaxCap
              && Near(P("FLOOR"), p.HvnFloor, 1e-12), "thong so HVN v2 C# = Python (PLAN 13.1)");
        int nCase = 0, bad = 0, nBox = 0; double maxMass = 0, maxPx = 0;
        var got = new Dictionary<string, List<SzHvnBox>>();
        foreach (var cs in doc.RootElement.GetProperty("cases").EnumerateArray())
        {
            nCase++;
            string ten = cs.GetProperty("ten").GetString();
            double tick = cs.GetProperty("tick").GetDouble(), up = cs.GetProperty("up").GetDouble(), y = cs.GetProperty("mass_min").GetDouble();
            int nb = cs.GetProperty("so_nen_m30").GetInt32();
            var lv = cs.GetProperty("levels").EnumerateArray().Select(a => new KeyValuePair<double, double>(a[0].GetDouble(), a[1].GetDouble())).ToList();
            var g = StrongZones.HvnClusters(lv, tick, up, nb, y, p);
            got[ten] = g;
            var want = cs.GetProperty("clusters").EnumerateArray().ToList();
            int h = StrongZones.HvnHalfWindow(up, tick, p), dn = StrongZones.HvnAroundTicks(up, tick, p);
            long span = lv.Count == 0 ? 0 : (long)Math.Round(lv.Max(x => x.Key) / tick) - (long)Math.Round(lv.Min(x => x.Key) / tick);
            int mb = StrongZones.HvnMaxBoxes(span, up / tick, p);
            bool ok = (Near(y, p.HvnMassDay, 1e-12) || Near(y, p.HvnMassWeek, 1e-12)) && h == cs.GetProperty("h").GetInt32() && dn == cs.GetProperty("dn").GetInt32()
                      && mb == cs.GetProperty("max_boxes").GetInt32() && g.Count == want.Count;
            for (int k = 0; k < want.Count && ok; k++)
            {
                var e = want[k]; var b = g[k];
                double dpx = new[] { Math.Abs(b.Lo - e.GetProperty("lo").GetDouble()), Math.Abs(b.Hi - e.GetProperty("hi").GetDouble()), Math.Abs(b.Peak - e.GetProperty("peak").GetDouble()),
                                     Math.Abs(b.CoreLo - e.GetProperty("core_lo").GetDouble()), Math.Abs(b.CoreHi - e.GetProperty("core_hi").GetDouble()) }.Max();
                double dm = Math.Abs(b.Mass - e.GetProperty("mass").GetDouble());
                maxPx = Math.Max(maxPx, dpx); maxMass = Math.Max(maxMass, dm);
                ok &= dpx < tick / 2 && dm <= 1e-6 && b.Lon == e.GetProperty("lon").GetBoolean() && b.Noi == e.GetProperty("noi").GetBoolean()
                      && Math.Abs(b.Bars - e.GetProperty("bars").GetDouble()) <= 1e-4 && Math.Abs(b.Con - e.GetProperty("con").GetDouble()) <= 1e-4;
                nBox++;
            }
            if (!ok) bad++;
            string fmt = Math.Abs(tick - 0.1) < 1e-12 ? "0.0" : "0.00";
            Console.WriteLine($"       {ten,-28} h={h,3} dn={dn,5} toi da {mb}  " + (g.Count == 0 ? "khong co hop" : string.Join(" ; ", g.Select(b => $"{b.Lo.ToString(fmt, IC)}-{b.Hi.ToString(fmt, IC)} pk {b.Peak.ToString(fmt, IC)} {b.Mass:0.000} {(b.Lon ? "L" : "")}{(b.Noi ? "N" : "")}")))
                              + (ok ? "" : "   <-- LECH"));
        }
        Check(nCase == 19 && bad == 0, "19 profile: h, dn, so hop toi da, so hop, lo/hi/peak/core_lo/core_hi (< tick/2), mass (<= 1e-6), lon/noi, bars/con (<= 1e-4)",
              $"lech {bad}/{nCase}; {nBox} hop; sai so gia lon nhat {maxPx:E2}, mass {maxMass:E2}");
        // ca bắt buộc (PLAN §13.5a, ca người dùng báo sót + ca người dùng vẽ)
        bool Has(string ten, params (double lo, double hi)[] want)
            => got.TryGetValue(ten, out var g) && g.Count == want.Length && want.Select((w, k) => Near(g[k].Lo, w.lo, 1e-9) && Near(g[k].Hi, w.hi, 1e-9)).All(x => x);
        string S(string ten) => got.TryGetValue(ten, out var g) ? string.Join(" ; ", g.Select(b => $"{b.Lo:0.00}-{b.Hi:0.00}")) : "khong co ca";
        Check(Has("NQZ26 phiên 2026-11-20", (25538.50, 25609.75)), "NQZ26 phien 20/11 (ca bao sot): 1 hop 25538,50-25609,75", S("NQZ26 phiên 2026-11-20"));
        Check(Has("NQZ26 tuần 2026-11-20", (27239.25, 27299.00), (25544.25, 25604.00)), "NQZ26 tuan 15->20/11 (ca bao sot): 27239,25-27299,00 va 25544,25-25604,00", S("NQZ26 tuần 2026-11-20"));
        Check(Has("NQZ26 phiên 2026-11-23", (26801.50, 26876.50)), "NQZ26 phien 23/11 (ca nguoi dung ve): 1 hop 26801,50-26876,50", S("NQZ26 phiên 2026-11-23"));
        Check(Has("GCZ26 phiên 2026-10-29", (4034.5, 4040.6)), "GCZ26 phien 29/10: 1 hop 4034,5-4040,6 (khong doi so voi v1)", S("GCZ26 phiên 2026-10-29"));
    }

    // ------------------------------------------------------------------ [4] C# = Python
    static void FixtureParity(Fx f)
    {
        Console.WriteLine("\n[4] Vung manh - C# = Python tren fixture (PLAN 8.1/8.2)");
        var root = f.Exp.RootElement;
        var p = new StrongZoneParams();
        var full = Series(f, 0, f.N - 1, p);

        // 1. phiên + U
        var days = root.GetProperty("days").EnumerateArray().ToList();
        int badDay = 0;
        Check(days.Count == full.Days.Count, "so phien", $"C#={full.Days.Count} Py={days.Count}");
        for (int k = 0; k < Math.Min(days.Count, full.Days.Count); k++)
        {
            var e = days[k];
            bool ok = e.GetProperty("start").GetInt32() == full.Days[k].a && e.GetProperty("end").GetInt32() == full.Days[k].b;
            var ue = e.GetProperty("U");
            if (ue.ValueKind == JsonValueKind.Null) ok &= double.IsNaN(full.UnitDay[k]);
            else ok &= Near(full.UnitDay[k], ue.GetDouble(), 1e-6);
            if (!ok) badDay++;
        }
        Check(badDay == 0, $"ranh gioi {days.Count} phien + U tung phien (<= 1e-6)", $"{badDay} lech");
        var weeks = root.GetProperty("weeks").EnumerateArray().ToList();
        Check(weeks.Count == full.Weeks.Count && weeks.Select((w, k) => w.GetProperty("start").GetInt32() == full.Weeks[k].a && w.GetProperty("end").GetInt32() == full.Weeks[k].b).All(x => x),
              "ranh gioi tuan", $"C#={full.Weeks.Count} Py={weeks.Count}");

        // 2. điểm va đập
        var pvE = root.GetProperty("pivots").EnumerateArray()
            .Select(e => (i: e.GetProperty("i").GetInt32(), kind: e.GetProperty("kind").GetInt32(), price: e.GetProperty("price").GetDouble(), conf: e.GetProperty("conf").GetInt32()))
            .OrderBy(x => x.i).ThenBy(x => x.kind).ToList();
        var pvC = StrongZones.Pivots(full, p).OrderBy(x => x.I).ThenBy(x => x.Kind).ToList();
        int pvBad = 0;
        for (int k = 0; k < Math.Min(pvE.Count, pvC.Count); k++)
            if (pvE[k].i != pvC[k].I || pvE[k].kind != pvC[k].Kind || pvE[k].conf != pvC[k].Conf || !Near(pvE[k].price, pvC[k].Price, 1e-9)) pvBad++;
        Check(pvE.Count == pvC.Count && pvBad == 0, $"diem va dap: du {pvE.Count}, dung i/price/kind/conf", $"C#={pvC.Count} lech={pvBad}");

        // 3–5. từng ca
        var pNoGroup = p.Clone(); pNoGroup.GroupEdges = false;
        int nCase = 0, badU = 0, badLv = 0, badCl = 0, badSh = 0, badNg = 0, nCl = 0, nSh = 0, nLv = 0, nHvn = 0, nHvnOk = 0, nGoldCase = 0, nHvnCase = 0;
        double maxU = 0, maxVw = 0, maxRatio = 0, maxExact = 0;
        var firstErr = new List<string>();
        void Err(string s) { if (firstErr.Count < 12) firstErr.Add(s); }
        var byJ = new Dictionary<int, (SzResult r, List<SzZone> sh)>();
        var boxByJ = new Dictionary<int, List<SzHvnShown>>();
        int nBx = 0, maxBx = 0, badBx = 0;
        foreach (var cs in root.GetProperty("cases").EnumerateArray())
        {
            nCase++;
            int j = cs.GetProperty("j").GetInt32();
            double now = cs.GetProperty("now").GetDouble();
            var s = Series(f, 0, j + 1, p);
            var r = StrongZones.Compute(s, p);
            var r2 = StrongZones.Compute(s, pNoGroup);
            var sh = StrongZones.Display(r, now, p);
            byJ[j] = (r, sh);
            if (!Near(now, f.C[j], 1e-9)) Err($"j={j} now khac close[j]");

            double ue = cs.GetProperty("U").GetDouble();
            maxU = Math.Max(maxU, Math.Abs(r.U - ue));
            if (!Near(r.U, ue, 1e-6)) { badU++; Err($"j={j} U C#={r.U} Py={ue}"); }

            // mức hợp lưu: so theo tập (tên, lo)
            var le = cs.GetProperty("levels").EnumerateArray().ToList();
            nLv += le.Count;
            bool lvOk = le.Count == r.Levels.Count;
            if (lvOk)
            {
                var ce = le.OrderBy(e => e.GetProperty("name").GetString(), StringComparer.Ordinal).ThenBy(e => e.GetProperty("lo").GetDouble()).ToList();
                var cc = r.Levels.OrderBy(x => x.Name, StringComparer.Ordinal).ThenBy(x => x.Lo).ToList();
                for (int k = 0; k < ce.Count && lvOk; k++)
                {
                    var e = ce[k]; var x = cc[k];
                    string nm = e.GetProperty("name").GetString();
                    double elo = e.GetProperty("lo").GetDouble(), ehi = e.GetProperty("hi").GetDouble();
                    bool isVw = nm.StartsWith("vwap");
                    double dlo = Math.Abs(Math.Round(x.Lo, 4) - elo), dhi = Math.Abs(Math.Round(x.Hi, 4) - ehi);
                    if (isVw) maxVw = Math.Max(maxVw, Math.Max(Math.Abs(x.Lo - elo), Math.Abs(x.Hi - ehi)));
                    else maxExact = Math.Max(maxExact, Math.Max(dlo, dhi));
                    lvOk &= x.Name == nm && (isVw ? Near(x.Lo, elo, 1e-4) && Near(x.Hi, ehi, 1e-4) : dlo < 1e-9 && dhi < 1e-9);
                    if (e.TryGetProperty("peak", out var pk))
                    {
                        double em = e.GetProperty("mass").GetDouble();
                        maxRatio = Math.Max(maxRatio, Math.Abs(x.Mass - em));
                        bool ok = StrongZones.HvnOk(x, s.H, s.L, j, r.U, p);
                        nHvn++; if (ok) nHvnOk++;
                        lvOk &= x.IsHvn && Math.Abs(Math.Round(x.Peak, 1) - pk.GetDouble()) < 1e-9 && Math.Abs(x.Mass - em) <= 1e-6
                             && x.Src == e.GetProperty("src").GetInt32() && x.End == e.GetProperty("end").GetInt32()
                             && ok == e.GetProperty("ok").GetBoolean();
                    }
                    else lvOk &= !x.IsHvn;
                    if (!lvOk) Err($"j={j} muc {nm} C#=({x.Name} {x.Lo:0.####}-{x.Hi:0.####} pk{x.Peak:0.####} m{x.Mass:0.######} e{x.End}) Py=({elo}-{ehi})");
                }
            }
            else Err($"j={j} so muc C#={r.Levels.Count} Py={le.Count}");
            if (!lvOk) badLv++;

            // cụm
            var cle = cs.GetProperty("clusters").EnumerateArray().ToList();
            nCl += cle.Count;
            var clc = r.Clusters.OrderBy(z => z.Lo).ToList();
            var clc2 = r2.Clusters.OrderBy(z => z.Lo).ToList();
            bool clOk = cle.Count == clc.Count && clc2.Count == clc.Count, ngOk = clOk;
            for (int k = 0; k < cle.Count && clOk; k++)
            {
                var e = cle[k]; var z = clc[k];
                clOk &= Near(z.Lo, e.GetProperty("lo").GetDouble(), 1e-6) && Near(z.Hi, e.GetProperty("hi").GetDouble(), 1e-6)
                     && z.N == e.GetProperty("n").GetInt32() && Near(z.Pmin, e.GetProperty("pmin").GetDouble(), 1e-6) && Near(z.Pmax, e.GetProperty("pmax").GetDouble(), 1e-6)
                     && z.Names.SequenceEqual(e.GetProperty("names").EnumerateArray().Select(x => x.GetString()))
                     && z.NGroup == e.GetProperty("ngroup").GetInt32() && z.Hvn == e.GetProperty("hvn").GetBoolean() && z.Gold == e.GetProperty("gold").GetBoolean();
                ngOk &= clc2[k].NGroup == e.GetProperty("ngroup_khong_gop").GetInt32() && clc2[k].Gold == e.GetProperty("gold_khong_gop").GetBoolean();
                if (!clOk) Err($"j={j} cum {k}: C#=({z.Lo:0.0}-{z.Hi:0.0} n{z.N} [{string.Join(",", z.Names)}] g{z.NGroup}) Py=({e.GetProperty("lo")}-{e.GetProperty("hi")} n{e.GetProperty("n")} {e.GetProperty("names")})");
            }
            if (cle.Count != clc.Count) Err($"j={j} so cum C#={clc.Count} Py={cle.Count}");
            if (!clOk) badCl++;
            if (!ngOk) badNg++;

            // vùng được vẽ
            var she = cs.GetProperty("shown").EnumerateArray().ToList();
            nSh += she.Count;
            bool shOk = she.Count == sh.Count;
            for (int k = 0; k < she.Count && shOk; k++)
            {
                var e = she[k]; var z = sh[k];
                shOk &= Near(z.Lo, e.GetProperty("lo").GetDouble(), 1e-6) && Near(z.Hi, e.GetProperty("hi").GetDouble(), 1e-6)
                     && z.Side == e.GetProperty("side").GetInt32() && z.Color == e.GetProperty("color").GetString()
                     && string.Equals(z.Label, e.GetProperty("label").GetString(), StringComparison.Ordinal);
                if (!shOk) Err($"j={j} ve {k}: C#=({z.Lo:0.0}-{z.Hi:0.0} {z.Color} '{z.Label}') Py=({e.GetProperty("lo")}-{e.GetProperty("hi")} {e.GetProperty("color")} '{e.GetProperty("label").GetString()}')");
            }
            if (she.Count != sh.Count) Err($"j={j} so vung ve C#={sh.Count} Py={she.Count}");
            if (sh.Any(z => z.Gold)) nGoldCase++;
            if (sh.Any(z => z.Hvn)) nHvnCase++;
            if (!shOk) badSh++;

            // hộp HVN được vẽ (PLAN §13.4) — giá = now
            var bxe = cs.GetProperty("hvn_boxes").EnumerateArray().ToList();
            var bxc = StrongZones.HvnBoxes(r, now, p);
            boxByJ[j] = bxc;
            nBx += bxe.Count; maxBx = Math.Max(maxBx, bxe.Count);
            bool bxOk = bxe.Count == bxc.Count;
            for (int k = 0; k < bxe.Count && bxOk; k++)
            {
                var e = bxe[k]; var x = bxc[k];
                bxOk &= x.Name == e.GetProperty("name").GetString() && Math.Abs(Math.Round(x.Lo, 1) - e.GetProperty("lo").GetDouble()) < 1e-9
                        && Math.Abs(Math.Round(x.Hi, 1) - e.GetProperty("hi").GetDouble()) < 1e-9 && Math.Abs(Math.Round(x.Peak, 1) - e.GetProperty("peak").GetDouble()) < 1e-9
                        && Math.Abs(x.Mass - e.GetProperty("mass").GetDouble()) <= 1e-6 && x.Label == e.GetProperty("label").GetString();
            }
            if (!bxOk) { badBx++; Err($"j={j} hop HVN C#=[{string.Join(" ; ", bxc.Select(x => $"{x.Lo:0.0}-{x.Hi:0.0} {x.Label}"))}] Py=[{string.Join(" ; ", bxe.Select(e => $"{e.GetProperty("lo")}-{e.GetProperty("hi")} {e.GetProperty("label").GetString()}"))}]"); }
        }
        foreach (var s in firstErr) Console.WriteLine("       " + s);
        Check(nCase == 689, "so ca = 689", $"{nCase}");
        Check(badU == 0, $"U moi ca (<= 1e-6)", $"lech {badU}/{nCase}, sai so lon nhat {maxU:E2}");
        Check(badLv == 0, $"muc hop luu moi ca ({nLv} muc, {nHvn} hop HVN, {nHvnOk} du dieu kien): ten, VWAP/sigma <= 1e-4, VAH/VAL/hop HVN lo/hi/peak bang dung, mass <= 1e-6, src/end/ok",
              $"lech {badLv}/{nCase}; sai so lon nhat VWAP {maxVw:E2}, VAH/VAL/HVN {maxExact:E2}, mass {maxRatio:E2}");
        Check(nGoldCase == 232 && nHvnCase == 393, "689 ca: 232 ca co vung vang duoc ve, 393 ca co vung dinh HVN (PLAN 13.5c)", $"vang {nGoldCase}, HVN {nHvnCase}");
        Check(badBx == 0 && Math.Abs(nBx / 689.0 - 2.49) < 0.005 && maxBx == 5,
              $"hop HVN duoc ve moi ca ({nBx} hop, TB {nBx / 689.0:0.00}, nhieu nhat {maxBx}): name/lo/hi/peak bang dung, mass <= 1e-6, nhan UTF-8 nguyen van",
              $"lech {badBx}/{nCase}");
        Check(badCl == 0, $"cum moi ca ({nCl} cum): lo/hi/n/pmin/pmax/names/ngroup/hvn/gold", $"lech {badCl}/{nCase}");
        Check(badNg == 0, "cum khi SzGroupEdges=false: ngroup_khong_gop, gold_khong_gop", $"lech {badNg}/{nCase}");
        Check(badSh == 0, $"vung duoc ve moi ca ({nSh} vung): lo/hi/side/color/label UTF-8 nguyen van", $"lech {badSh}/{nCase}");

        // 13.5c: năm ca ghi số (vùng được vẽ + hộp HVN được vẽ)
        void CaseShown(string name, int j, double u, params (double lo, double hi, string col, string lab)[] want)
        {
            if (!byJ.TryGetValue(j, out var x)) { Check(false, name, "khong co ca"); return; }
            bool ok = Near(x.r.U, u, 1e-6) && x.sh.Count == want.Length;
            for (int k = 0; k < want.Length && ok; k++)
                ok &= Near(x.sh[k].Lo, want[k].lo, 1e-6) && Near(x.sh[k].Hi, want[k].hi, 1e-6) && x.sh[k].Color == want[k].col && x.sh[k].Label == want[k].lab;
            Check(ok, name, string.Join(" | ", x.sh.Select(z => $"{z.Lo:0.0}-{z.Hi:0.0} {z.Color} {z.Label}")));
        }
        void CaseBoxes(string name, int j, params (double lo, double hi, string lab)[] want)
        {
            if (!boxByJ.TryGetValue(j, out var b)) { Check(false, name, "khong co ca"); return; }
            bool ok = b.Count == want.Length;
            for (int k = 0; k < want.Length && ok; k++)
                ok &= Math.Abs(Math.Round(b[k].Lo, 1) - want[k].lo) < 1e-9 && Math.Abs(Math.Round(b[k].Hi, 1) - want[k].hi) < 1e-9 && b[k].Label == want[k].lab;
            Check(ok, name, string.Join(" | ", b.Select(z => $"{z.Lo:0.0}-{z.Hi:0.0} {z.Label}")));
        }
        const string HD = "HVN ngày", HW = "HVN tuần", HB = "HVN ngày + tuần";
        CaseShown("Ca A (j=1342, vung vang)", 1342, 10.028261,
            (4020.6, 4024.7, "do", "Kháng cự · 4 lần · HVN ngày"),
            (4026.4, 4028.6, "do", "Kháng cự · 3 lần · HVN ngày + VAL hôm qua + VWAP hôm qua −1σ"),
            (4038.8, 4042.0, "vang", "★ Kháng cự rất mạnh · 3 lần · HVN tuần + HVN ngày + VAL tuần trước + VWAP hôm qua"));
        CaseBoxes("Ca A: hop HVN 4007,6-4012,6 ; 4021,8-4025,9 ; 4028,5-4032,7 (deu HVN ngay)", 1342, (4007.6, 4012.6, HD), (4021.8, 4025.9, HD), (4028.5, 4032.7, HD));
        if (byJ.TryGetValue(1342, out var ca))
        {
            var lv = ca.r.Levels;
            double L(string nm) => lv.First(x => x.Name == nm).Lo;
            Check(Near(L("vwap_d"), 4041.8706, 1e-4) && Near(L("vwap_d_tren"), 4054.7866, 1e-4) && Near(L("vwap_d_duoi"), 4028.9546, 1e-4)
                  && Near(L("vah_d"), 4052.8, 1e-9) && Near(L("val_d"), 4029.2, 1e-9) && Near(L("vwap_w"), 4111.5234, 1e-4)
                  && Near(L("vah_w"), 4176.4, 1e-9) && Near(L("val_w"), 4042.8, 1e-9), "Ca A: so tung muc VWAP/sigma/VAH/VAL dung PLAN");
            var hd = lv.First(x => x.Name == "hvn_d" && x.Src == 1);
            var hw = lv.First(x => x.Name == "hvn_w" && x.Src == 0);
            Check(Near(hd.Lo, 4034.5, 1e-9) && Near(hd.Hi, 4040.6, 1e-9) && Near(hd.Peak, 4037.6, 1e-9) && Near(hd.Mass, 0.30678, 1e-5)
                  && lv.Count(x => x.Name == "hvn_d") == 6 && Near(hw.Lo, 4032.8, 1e-9) && Near(hw.Hi, 4040.3, 1e-9) && Near(hw.Mass, 0.166402, 1e-6),
                  "Ca A: HVN ngay hom qua 4034,5-4040,6 (30,7 %), 6 hop ngay; HVN tuan nay 4032,8-4040,3 (16,6 %)");
            var gz = ca.r.Clusters.First(z => z.Gold && Near(z.Lo, 4038.8, 1e-6));
            Check(gz.N == 3 && Near(gz.Pmin, 4039.4, 1e-9) && Near(gz.Pmax, 4041.4, 1e-9), "Ca A: vung vang = 3 diem 4039,4..4041,4");
        }
        CaseShown("Ca B (j=1042, loc chong)", 1042, 10.070435,
            (4145.0, 4148.3, "xanh", "Hỗ trợ · 3 lần · VWAP hôm qua"),
            (4158.4, 4162.2, "do", "Kháng cự · 3 lần · VAL tuần trước + VWAP hôm qua +1σ"),
            (4163.9, 4168.1, "do", "Kháng cự · 4 lần · HVN ngày + VAL tuần trước"),
            (4174.3, 4177.7, "vang", "★ Kháng cự rất mạnh · 5 lần · HVN tuần + HVN ngày + VWAP tuần trước"));
        CaseBoxes("Ca B: hop HVN 4113,9-4118,4 'HVN ngay + tuan' ; 4165,8-4172,0 ; 4173,6-4177,9", 1042, (4113.9, 4118.4, HB), (4165.8, 4172.0, HD), (4173.6, 4177.9, HD));
        CaseShown("Ca C (j=935, gia trong vung)", 935, 9.806087,
            (4174.8, 4178.6, "vang", "★ Hỗ trợ rất mạnh · 6 lần · HVN tuần + HVN ngày + VWAP tuần trước"),
            (4192.0, 4194.0, "xanh", "Hỗ trợ · 3 lần · HVN ngày + VWAP hôm qua"),
            (4197.2, 4200.5, "xanh", "Hỗ trợ · 3 lần · HVN ngày"),
            (4206.7, 4209.6, "do", "Kháng cự · 4 lần · HVN ngày + VWAP tuần trước +1σ"));
        CaseBoxes("Ca C: hop HVN 4177,7-4182,2 'HVN tuan' ; 4192,6-4196,4 ; 4207,3-4211,4", 935, (4177.7, 4182.2, HW), (4192.6, 4196.4, HD), (4207.3, 4211.4, HD));
        {
            // Ca C với SzGroupEdges = false: cụm 4180,4–4184,0 (HVN tuần + VAL hôm qua + VWAP hôm qua −1σ) từ 2 nhóm thành 3 ⇒ vàng
            var pg = p.Clone(); pg.GroupEdges = false;
            var r = StrongZones.Compute(Series(f, 0, 936, pg), pg);
            var z = r.Clusters.FirstOrDefault(q => Near(q.Lo, 4180.4, 1e-6));
            var z0 = byJ.TryGetValue(935, out var c0) ? c0.r.Clusters.FirstOrDefault(q => Near(q.Lo, 4180.4, 1e-6)) : null;
            Check(z != null && z0 != null && z.Gold && z.NGroup == 3 && !z0.Gold && z0.NGroup == 2 && z.Names.SequenceEqual(new[] { "hvn_w", "val_d", "vwap_d_duoi" }),
                  "Ca C khong gop: cum 4180,4-4184,0 (HVN tuan + VAL hom qua + VWAP hom qua -1sigma) 2 nhom -> 3 nhom, vang",
                  z == null ? "khong thay" : $"{string.Join("+", z.Names)} g{z.NGroup} {z.Gold}");
        }
        CaseShown("Ca D (j=1502, mot vung)", 1502, 10.927826, (4059.4, 4062.8, "do", "Kháng cự · 3 lần · HVN ngày"));
        CaseBoxes("Ca D: hop HVN 3966,5-3971,4 ; 4030,2-4040,3 'HVN ngay + tuan' ; 4058,7-4063,0", 1502, (3966.5, 3971.4, HD), (4030.2, 4040.3, HB), (4058.7, 4063.0, HD));
        if (byJ.TryGetValue(1502, out var cd))
            Check(cd.r.Clusters.Count == 7 && cd.r.Levels.Any(x => x.Name == "hvn_w" && x.Src == 1 && Near(x.Lo, 4030.2, 1e-9) && Near(x.Hi, 4040.3, 1e-9)),
                  "Ca D: 7 cum; HVN tuan truoc 4030,2-4040,3");
        CaseShown("Ca E (j=1238, chi ho tro)", 1238, 10.236522,
            (4032.3, 4036.3, "xanh", "Hỗ trợ · 5 lần · HVN ngày + VWAP hôm qua +1σ"),
            (4042.4, 4046.3, "xanh", "Hỗ trợ · 4 lần · VAL tuần trước"));
        CaseBoxes("Ca E: hop HVN 4007,6-4012,6 ; 4028,5-4032,7 ; 4103,5-4108,8 ; 4140,6-4145,2 'HVN ngay + tuan' (2 moi phia)", 1238,
            (4007.6, 4012.6, HD), (4028.5, 4032.7, HD), (4103.5, 4108.8, HD), (4140.6, 4145.2, HB));
    }

    // ------------------------------------------------------------------ [5] bất biến khung + bộ đệm
    static void InvarianceTests(Fx f)
    {
        Console.WriteLine("\n[5] Vung manh - bat bien khung chart + bo dem");
        var p = new StrongZoneParams();
        string Sig(SzResult r, List<SzZone> sh) =>
            $"U={r.U:R}|" + string.Join(";", r.Clusters.Select(z => $"{z.Lo:R},{z.Hi:R},{z.N},{string.Join("+", z.Names)},{z.NGroup},{z.Gold}"))
            + "||" + string.Join(";", sh.Select(z => $"{z.Lo:R},{z.Hi:R},{z.Color},{z.Label}"));

        // (a) chart M30 chính vs M30 phụ: history dài khác nhau, cùng nến cuối ⇒ cắt về 35 ngày ⇒ y hệt
        int sameTrim = 0, total = 0, sameVsPy = 0;
        foreach (int j in new[] { 1042, 1238, 1342, 1502, 1600 })
        {
            total++;
            string a = null;
            foreach (int from in new[] { 0, 60, 150 })
            {
                var t = f.T.GetRange(from, j + 2 - from);
                int st = from + StrongZones.CanonicalStart(t, p.HistoryDays);
                var s = Series(f, st, j + 1, p);
                var r = StrongZones.Compute(s, p);
                var sig = Sig(r, StrongZones.Display(r, f.C[j], p));
                if (a == null) a = sig; else if (a != sig) { a = "KHAC"; break; }
            }
            if (a != "KHAC") sameTrim++;
            // so với không cắt (đúng như kỳ vọng Python) — cắt 35 ngày không đổi kết quả
            var rf = StrongZones.Compute(Series(f, 0, j + 1, p), p);
            if (Sig(rf, StrongZones.Display(rf, f.C[j], p)) == a) sameVsPy++;
        }
        Check(sameTrim == total, "M30 chinh / M30 phu (history bat dau khac nhau) -> cat 35 ngay -> vung y het", $"{sameTrim}/{total}");
        Check(sameVsPy == total, "cat 35 ngay khong doi ket qua so voi tinh tren toan fixture", $"{sameVsPy}/{total}");

        // (b) cả 689 ca với đầu vào đã cắt 35 ngày vẫn = Python
        var root = f.Exp.RootElement;
        int bad = 0, n = 0;
        foreach (var cs in root.GetProperty("cases").EnumerateArray())
        {
            int j = cs.GetProperty("j").GetInt32(); n++;
            int st = StrongZones.CanonicalStart(f.T.GetRange(0, j + 2), p.HistoryDays);
            var r = StrongZones.Compute(Series(f, st, j + 1, p), p);
            var sh = StrongZones.Display(r, f.C[j], p);
            var she = cs.GetProperty("shown").EnumerateArray().ToList();
            bool ok = she.Count == sh.Count;
            for (int k = 0; k < she.Count && ok; k++)
                ok &= Near(sh[k].Lo, she[k].GetProperty("lo").GetDouble(), 1e-6) && Near(sh[k].Hi, she[k].GetProperty("hi").GetDouble(), 1e-6)
                   && sh[k].Label == she[k].GetProperty("label").GetString() && sh[k].Color == she[k].GetProperty("color").GetString();
            if (!ok) bad++;
        }
        Check(bad == 0, "689 ca voi dau vao cat 35 ngay (nhu indicator) van = Python", $"lech {bad}/{n}");

        // (c) không vẽ lại lùi: điểm có conf ≤ j ở lần tính j còn nguyên ở lần tính j + 5
        int lost = 0, checkedPv = 0;
        foreach (int j in new[] { 900, 1100, 1300, 1500 })
        {
            var r1 = StrongZones.Compute(Series(f, 0, j + 1, p), p);
            var r2 = StrongZones.Compute(Series(f, 0, j + 6, p), p);
            var set2 = new HashSet<string>(r2.Pivots.Select(q => $"{q.I},{q.Kind},{q.Conf},{q.Price:R}"));
            foreach (var q in r1.Pivots.Where(q => q.Conf <= j)) { checkedPv++; if (!set2.Contains($"{q.I},{q.Kind},{q.Conf},{q.Price:R}")) lost++; }
        }
        Check(lost == 0 && checkedPv > 0, "khong ve lai lui: diem conf<=j o lan dau con nguyen o j+5", $"{checkedPv} diem, mat {lost}");

        // (d) bộ đệm: gọi nhiều lần trong cùng nến M30 (giá đổi) ⇒ chỉ tính 1 lần, cụm không đổi, chỉ 'shown' đổi
        {
            var eng = new StrongZoneEngine();
            int j = 1342;
            int builds = 0;
            SzSeries Build() { builds++; return Series(f, 0, j + 1, p); }
            string key = StrongZoneEngine.KeyOf(j + 2, f.T[0], f.T[j], f.T[j + 1], p);
            var r1 = eng.Structure(key, Build, p);
            var sh1 = StrongZones.Display(r1, 4015.3, p);
            var r2 = eng.Structure(key, Build, p);
            var sh2 = StrongZones.Display(r2, 4030.0, p);
            var r3 = eng.Structure(key, Build, p);
            Check(ReferenceEquals(r1, r2) && ReferenceEquals(r2, r3) && eng.Recomputes == 1 && builds == 1,
                  "bo dem: 3 lan goi cung (n, gio nen j) -> tinh 1 lan", $"recompute={eng.Recomputes}");
            Check(Sig(r1, sh1) != Sig(r2, sh2) && r1.Clusters.Count == r2.Clusters.Count, "bo dem: gia khac -> chi 'shown' doi");
            string key2 = StrongZoneEngine.KeyOf(j + 3, f.T[0], f.T[j + 1], f.T[j + 2], p);
            j = 1343;
            eng.Structure(key2, Build, p);
            Check(eng.Recomputes == 2, "bo dem: co nen M30 moi -> tinh lai");
            var p2 = p.Clone(); p2.MinGroup = 2;
            eng.Structure(StrongZoneEngine.KeyOf(j + 2, f.T[0], f.T[j], f.T[j + 1], p2), Build, p2);
            Check(eng.Recomputes == 3, "bo dem: doi input -> tinh lai");
        }
        // (e) giá hiện tại đổi giữa hai nến M30 không làm đổi cấu trúc: tính lại từ đầu với nến đang chạy khác
        //     (High/Low/Close nến j+1 khác) ⇒ cụm y hệt (nến đang chạy không đi vào cấu trúc)
        {
            int j = 1342;
            var t = f.T.GetRange(0, j + 2); var o = f.O.GetRange(0, j + 2); var h = f.H.GetRange(0, j + 2);
            var l = f.L.GetRange(0, j + 2); var c = f.C.GetRange(0, j + 2); var v = f.V.GetRange(0, j + 2);
            var r1 = StrongZones.Compute(new SzSeries(t, o, h, l, c, v, i => f.Lv[i], 0.1, 0.2, p), p);
            h[j + 1] += 25; l[j + 1] -= 25; c[j + 1] += 10;
            var r2 = StrongZones.Compute(new SzSeries(t, o, h, l, c, v, i => i == j + 1 ? new List<KeyValuePair<double, double>>() : f.Lv[i], 0.1, 0.2, p), p);
            Check(Sig(r1, new List<SzZone>()) == Sig(r2, new List<SzZone>()), "nen dang chay (M30 chua dong) doi -> cau truc vung khong doi");
        }
    }

    // ------------------------------------------------------------------ [6] UI
    static void UiTests(Fx f)
    {
        Console.WriteLine("\n[6] Vung manh - UI (mau / nhan / vi tri chu) + render PNG");
        Color sup = Color.FromArgb(0x26, 0xA6, 0x9A), res = Color.FromArgb(0xEF, 0x53, 0x50), gold = Color.FromArgb(0xFF, 0xD6, 0x00);
        Check(StrongZonePainter.ColorOf(new SzZone { Color = "vang" }, sup, res, gold) == gold
              && StrongZonePainter.ColorOf(new SzZone { Color = "xanh" }, sup, res, gold) == sup
              && StrongZonePainter.ColorOf(new SzZone { Color = "do" }, sup, res, gold) == res
              && StrongZonePainter.ColorOf(new SzZone { Color = "xam" }, sup, res, gold).R == 0x9E, "mau: vang/xanh/do/xam dung input");
        Check(StrongZonePainter.FillAlpha(new SzZone { Gold = true }) == 70 && StrongZonePainter.FillAlpha(new SzZone()) == 40, "do dam: vang 70, con lai 40");
        Check(StrongZones.ColorOf(true, -1) == "vang" && StrongZones.ColorOf(false, 1) == "xanh" && StrongZones.ColorOf(false, -1) == "do" && StrongZones.ColorOf(false, 0) == "xam",
              "chon mau theo vang/phia");
        Check(StrongZonePainter.TextOf(new SzZone { Label = "Hỗ trợ · 3 lần", Dist = 4.56 }, 0.1) == "Hỗ trợ · 3 lần"
              && StrongZonePainter.TextOf(new SzZone { Label = "X (giá đang trong vùng)", Inside = true }, 0.1) == "X (giá đang trong vùng)",
              "chu: chi nhan, khong kem khoang cach");
        // vị trí chữ
        {
            float th = 13f;
            var y = StrongZonePainter.LayoutLabels(new List<(float, float)> { (100, 140) }, th, 0, 800);
            Check(y[0] >= 100 && y[0] + th <= 140, "dai day hon chu -> chu nam trong dai");
            y = StrongZonePainter.LayoutLabels(new List<(float, float)> { (100, 105) }, th, 0, 800);
            Check(Near(y[0] + th, 99, 1e-3), "dai mong hon chu -> chu ngay tren dai");
            var rnd = new Random(7);
            int overlapBad = 0, clipBad = 0;
            for (int trial = 0; trial < 500; trial++)
            {
                int n = rnd.Next(1, 8);
                var bands = new List<(float, float)>();
                for (int k = 0; k < n; k++) { float t = rnd.Next(0, 760); bands.Add((t, t + rnd.Next(1, 40))); }
                var ys = StrongZonePainter.LayoutLabels(bands, th, 0, 800);
                for (int a = 0; a < n; a++)
                {
                    if (ys[a] < -1e-3 || ys[a] + th > 800 + 1e-3) clipBad++;
                    for (int b = a + 1; b < n; b++) if (Math.Abs(ys[a] - ys[b]) < th - 1e-3) overlapBad++;
                }
            }
            Check(overlapBad == 0 && clipBad == 0, "500 bo dai ngau nhien: nhan khong de nhau, nam trong khung", $"de={overlapBad} ra ngoai={clipBad}");
            // trên dữ liệu thật: mọi ca của fixture, khung 800 px theo dải giá ±5U quanh giá
            int realBad = 0;
            foreach (var cs in f.Exp.RootElement.GetProperty("cases").EnumerateArray())
            {
                var sh = cs.GetProperty("shown").EnumerateArray().ToList();
                if (sh.Count < 2) continue;
                double now = cs.GetProperty("now").GetDouble(), u = cs.GetProperty("U").GetDouble();
                double top = now + 5 * u, bot = now - 5 * u;
                float Y(double pr) => (float)((top - pr) / (top - bot) * 800);
                var bands = sh.Select(e => (Y(e.GetProperty("hi").GetDouble()), Y(e.GetProperty("lo").GetDouble()))).ToList();
                var ys = StrongZonePainter.LayoutLabels(bands, th, 0, 800);
                for (int a = 0; a < ys.Length; a++) for (int b = a + 1; b < ys.Length; b++) if (Math.Abs(ys[a] - ys[b]) < th - 1e-3) realBad++;
            }
            Check(realBad == 0, "moi ca fixture (khung 800px, +-5U): nhan khong de nhau", $"{realBad}");
            // nhãn vùng mạnh + nhãn hộp HVN xếp CHUNG (như StrongZonePainter.Paint) — C# tính lại mọi ca
            int mixBad = 0, mixCases = 0, nBoxShown = 0;
            var pp = new StrongZoneParams();
            foreach (var cs in f.Exp.RootElement.GetProperty("cases").EnumerateArray())
            {
                int j = cs.GetProperty("j").GetInt32();
                var r = StrongZones.Compute(Series(f, 0, j + 1, pp), pp);
                double now = f.C[j], u = r.U;
                var sh = StrongZones.Display(r, now, pp);
                var bx = StrongZones.HvnBoxes(r, now, pp);
                nBoxShown += bx.Count;
                if (sh.Count + bx.Count < 2) continue;
                mixCases++;
                double top = now + 5 * u, bot = now - 5 * u;
                float Y(double pr) => (float)((top - pr) / (top - bot) * 800);
                var bands = sh.Select(z => (Y(z.Hi), Y(z.Lo))).Concat(bx.Select(z => (Y(z.Hi), Y(z.Lo)))).ToList();
                var ys = StrongZonePainter.LayoutLabels(bands, th, 0, 800);
                for (int a = 0; a < ys.Length; a++)
                {
                    if (ys[a] < -1e-3 || ys[a] + th > 800 + 1e-3) mixBad++;
                    for (int b = a + 1; b < ys.Length; b++) if (Math.Abs(ys[a] - ys[b]) < th - 1e-3) mixBad++;
                }
            }
            Check(mixBad == 0 && mixCases > 0, $"moi ca fixture: nhan vung manh + nhan hop HVN ({nBoxShown} hop) khong de nhau", $"{mixCases} ca, de {mixBad}");
        }
        // render PNG (GC) — vùng mạnh + hộp HVN, đúng thông số indicator (GCZ26 là một hợp đồng ⇒ bộ chặn chỗ nối tắt;
        // fixture không có chỗ nối nên kết quả như Python)
        try
        {
            string outDir = UiDir();
            Directory.CreateDirectory(outDir);
            var p = new StrongZoneParams();
            int nPng = 0;
            foreach (var (j, name) in new[] { (1342, "ca_A_vang_1342"), (1042, "ca_B_loc_chong_1042"), (935, "ca_C_trong_vung_935"), (1238, "ca_E_ho_tro_1238") })
            {
                var r = StrongZones.Compute(Series(f, 0, j + 1, p), p);
                var sh = StrongZones.Display(r, f.C[j], p);
                var bx = StrongZones.HvnBoxes(r, f.C[j], p);
                RenderPng(f, j, sh, bx, Path.Combine(outDir, name + ".png"), sup, res, gold, $"GCZ26 · {f.T[j]:yyyy-MM-dd HH:mm} UTC · giá {f.C[j]:0.0} · U {r.U:0.00}");
                nPng++;
            }
            {   // Ca C khi không gộp ⇒ vàng hỗ trợ
                var pg = p.Clone(); pg.GroupEdges = false;
                var r = StrongZones.Compute(Series(f, 0, 936, pg), pg);
                RenderPng(f, 935, StrongZones.Display(r, f.C[935], pg), StrongZones.HvnBoxes(r, f.C[935], pg), Path.Combine(outDir, "ca_C_khong_gop_vang_935.png"), sup, res, gold,
                          $"GCZ26 · {f.T[935]:yyyy-MM-dd HH:mm} UTC · không gộp VAH/VAL với ±1σ");
                nPng++;
            }
            Check(nPng == 5 && Directory.GetFiles(outDir, "*.png").Length >= 5, "render PNG GC bang chinh StrongZonePainter.Paint (vung manh + hop HVN)", outDir);
        }
        catch (Exception ex) { Check(false, "render PNG", ex.GetType().Name + ": " + ex.Message); }
    }

    static string UiDir() => Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../research/vung_manh_2026-11-25/ui"));
    static readonly Color HvnCol = Color.FromArgb(0xFF, 0x8F, 0x00);   // mặc định HvnColor của SessionZones

    static void RenderPng(Fx f, int j, List<SzZone> shown, List<SzHvnShown> boxes, string path, Color sup, Color res, Color gold, string title, double nowPrice = double.NaN)
    {
        int W = 1500, H = 820, padR = 80;
        int from = Math.Max(0, j - 90), to = j + 1;
        double top = double.MinValue, bot = double.MaxValue;
        for (int i = from; i <= to; i++) { top = Math.Max(top, f.H[i]); bot = Math.Min(bot, f.L[i]); }
        foreach (var z in shown) { top = Math.Max(top, z.Hi); bot = Math.Min(bot, z.Lo); }
        foreach (var z in boxes) { top = Math.Max(top, z.Hi); bot = Math.Min(bot, z.Lo); }
        double m = (top - bot) * 0.06; top += m; bot -= m;
        var clip = new Rectangle(0, 24, W - padR, H - 24);
        float Y(double pr) => (float)(clip.Top + (top - pr) / (top - bot) * clip.Height);
        using var bmp = new Bitmap(W, H);
        using var g = Graphics.FromImage(bmp);
        g.SmoothingMode = SmoothingMode.None;
        g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;
        g.Clear(Color.FromArgb(19, 23, 34));
        double rng = top - bot;
        double step = rng > 600 ? 100 : rng > 250 ? 50 : rng > 120 ? 25 : rng > 50 ? 10 : 5;
        using (var grid = new Pen(Color.FromArgb(40, 255, 255, 255)))
        using (var fa = new Font("Arial", 8))
        using (var ba = new SolidBrush(Color.FromArgb(170, 255, 255, 255)))
        {
            for (double pr = Math.Ceiling(bot / step) * step; pr <= top; pr += step)
            { float y = Y(pr); g.DrawLine(grid, clip.Left, y, clip.Right, y); g.DrawString(pr.ToString("0", IC), fa, ba, clip.Right + 6, y - 7); }
        }
        float cw = (float)clip.Width / (to - from + 4);
        using (var sep = new Pen(Color.FromArgb(60, 255, 255, 255)) { DashStyle = DashStyle.Dash })
        using (var fd = new Font("Arial", 7))
        using (var bd = new SolidBrush(Color.FromArgb(150, 255, 255, 255)))
            for (int i = from + 1; i <= to; i++)
                if ((f.T[i] - f.T[i - 1]).TotalMinutes > 75)
                {   // ranh giới phiên
                    float x = clip.Left + (i - from + 0.5f) * cw;
                    g.DrawLine(sep, x, clip.Top, x, clip.Bottom);
                    g.DrawString($"{f.T[i]:dd/MM HH:mm}", fd, bd, x + 2, clip.Bottom - 14);
                }
        for (int i = from; i <= to; i++)
        {
            float x = clip.Left + (i - from + 1) * cw;
            bool up = f.C[i] >= f.O[i];
            var col = i == to ? Color.FromArgb(150, 200, 200, 200) : up ? Color.FromArgb(0x26, 0xA6, 0x9A) : Color.FromArgb(0xEF, 0x53, 0x50);
            using var pen = new Pen(col, 1f);
            g.DrawLine(pen, x, Y(f.H[i]), x, Y(f.L[i]));
            float y1 = Y(Math.Max(f.O[i], f.C[i])), y2 = Y(Math.Min(f.O[i], f.C[i]));
            using var br = new SolidBrush(col);
            g.FillRectangle(br, x - cw * 0.35f, y1, cw * 0.7f, Math.Max(1, y2 - y1));
        }
        using (var fnt = new Font("Arial", 8, FontStyle.Bold))
            StrongZonePainter.Paint(g, clip, Y, shown, sup, res, gold, f.Tick, fnt, boxes, HvnCol);
        double now = double.IsNaN(nowPrice) ? f.C[j] : nowPrice;
        using (var pn = new Pen(Color.FromArgb(200, 255, 255, 255), 1f) { DashStyle = DashStyle.Dot })
            g.DrawLine(pn, clip.Left, Y(now), clip.Right, Y(now));
        using (var ft = new Font("Arial", 9, FontStyle.Bold))
        using (var bt = new SolidBrush(Color.White))
            g.DrawString("Session Zones · vùng mạnh + hộp HVN (chưa kiểm định) · " + title, ft, bt, 6, 4);
        bmp.Save(path, ImageFormat.Png);
    }

    // ------------------------------------------------------------------ [7] NQZ26 (giá thật, bước giá 0,25)
    // (a) C# = Python ở 13 ca ngày 2026-11-24 (nq_expected2.json; bộ chặn chỗ nối TẮT — đúng như indicator trên NQZ26);
    // (b) ca bắt buộc PLAN §13.5d; (c) render PNG đúng như indicator, có ảnh thời điểm cuối dữ liệu.
    static void NqTests()
    {
        Console.WriteLine("\n[7] NQZ26 23/11-24/11 - hop HVN v2 + vung manh (gia that, tick 0,25)");
        var f = LoadFixture("nq_", "nq_expected2.json", 0.25);
        if (f == null) { Check(false, "doc fixture NQ", FxDir()); return; }
        var root = f.Exp.RootElement;
        // như indicator: NQZ26 là một hợp đồng ⇒ bộ chặn chỗ nối tắt; fixture sinh với splice_jump = 0
        var p = new StrongZoneParams { SpliceJump = ZonePolicy.IsSingleContract("NQZ26") ? 0 : 20.0 * 10 * f.Tick };
        Check(p.SpliceJump == 0 && root.GetProperty("splice_jump").GetDouble() == 0, "NQZ26 -> bo chan cho noi tat (C# va fixture Python)");
        int n = 0, bad = 0, nShown = 0, nBox = 0, nDrawn = 0;
        var errs = new List<string>();
        SzResult rLast = null; List<SzZone> shLast = null; List<SzHvnShown> bxLast = null; int jLast = -1;
        foreach (var cs in root.GetProperty("cases").EnumerateArray())
        {
            n++;
            int j = cs.GetProperty("j").GetInt32();
            var r = StrongZones.Compute(Series(f, 0, j + 1, p), p);
            var sh = StrongZones.Display(r, f.C[j], p);
            var bx = StrongZones.HvnBoxes(r, f.C[j], p);
            bool ok = Near(r.U, cs.GetProperty("U").GetDouble(), 1e-6) && Near(f.C[j], cs.GetProperty("now").GetDouble(), 1e-9);
            var hv = r.Levels.Where(x => x.IsHvn).OrderBy(x => x.Name, StringComparer.Ordinal).ThenBy(x => x.Lo).ToList();
            var he = cs.GetProperty("hvn").EnumerateArray().OrderBy(e => e.GetProperty("name").GetString(), StringComparer.Ordinal).ThenBy(e => e.GetProperty("lo").GetDouble()).ToList();
            ok &= hv.Count == he.Count;
            for (int k = 0; k < he.Count && ok; k++)
            {
                var e = he[k]; var x = hv[k]; nBox++;
                ok &= x.Name == e.GetProperty("name").GetString() && Near(x.Lo, e.GetProperty("lo").GetDouble(), 1e-6) && Near(x.Hi, e.GetProperty("hi").GetDouble(), 1e-6)
                      && Near(x.Peak, e.GetProperty("peak").GetDouble(), 1e-6) && Math.Abs(x.Mass - e.GetProperty("mass").GetDouble()) <= 1e-6
                      && x.Src == e.GetProperty("src").GetInt32() && StrongZones.HvnOk(x, r.Highs, r.Lows, r.J, r.U, p) == e.GetProperty("ok").GetBoolean();
            }
            var se = cs.GetProperty("shown").EnumerateArray().ToList();
            nShown += se.Count;
            ok &= se.Count == sh.Count;
            for (int k = 0; k < se.Count && ok; k++)
                ok &= Near(sh[k].Lo, se[k].GetProperty("lo").GetDouble(), 1e-6) && Near(sh[k].Hi, se[k].GetProperty("hi").GetDouble(), 1e-6)
                      && sh[k].Color == se[k].GetProperty("color").GetString() && sh[k].Label == se[k].GetProperty("label").GetString();
            var be = cs.GetProperty("hvn_boxes").EnumerateArray().ToList();
            nDrawn += be.Count;
            ok &= be.Count == bx.Count;
            for (int k = 0; k < be.Count && ok; k++)
                ok &= bx[k].Name == be[k].GetProperty("name").GetString() && Near(bx[k].Lo, be[k].GetProperty("lo").GetDouble(), 1e-6) && Near(bx[k].Hi, be[k].GetProperty("hi").GetDouble(), 1e-6)
                      && Near(bx[k].Peak, be[k].GetProperty("peak").GetDouble(), 1e-6) && Math.Abs(bx[k].Mass - be[k].GetProperty("mass").GetDouble()) <= 1e-6
                      && bx[k].Label == be[k].GetProperty("label").GetString();
            if (!ok) { bad++; if (errs.Count < 5) errs.Add($"j={j} U {r.U} hvn {string.Join(",", hv.Select(x => $"{x.Name} {x.Lo}-{x.Hi}"))} shown {string.Join(" | ", sh.Select(z => $"{z.Lo}-{z.Hi} {z.Label}"))} hop {string.Join(" | ", bx.Select(b => $"{b.Lo}-{b.Hi} {b.Label}"))}"); }
            if (j > jLast) { jLast = j; rLast = r; shLast = sh; bxLast = bx; }
        }
        foreach (var e in errs) Console.WriteLine("       " + e);
        Check(n == 13 && bad == 0, $"NQ 24/11: 13 ca C# = Python (U <= 1e-6; {nBox} muc HVN lo/hi/peak <= 1e-6, mass <= 1e-6, src/ok; {nShown} vung ve; {nDrawn} hop HVN ve + nhan)", $"lech {bad}/{n}");

        // ca cuối (2026-11-24 11:30, PLAN §13.5d)
        if (rLast != null)
        {
            bool Lv(string nm, double lo, double hi) => rLast.Levels.Any(x => x.IsHvn && x.Name == nm && Near(x.Lo, lo, 1e-9) && Near(x.Hi, hi, 1e-9) && StrongZones.HvnOk(x, rLast.Highs, rLast.Lows, rLast.J, rLast.U, p));
            Check(f.T[jLast] == new DateTime(2026, 11, 24, 11, 30, 0) && Near(f.C[jLast], 26442.75, 1e-9) && Near(rLast.U, 143.467, 5e-4),
                  "NQ ca cuoi: nen 2026-11-24 11:30, gia 26442,75, U 143,467", $"{f.T[jLast]:yyyy-MM-dd HH:mm} {f.C[jLast]} U {rLast.U:0.000}");
            Check(Lv("hvn_d", 26801.50, 26876.50) && Lv("hvn_d", 25538.50, 25609.75) && Lv("hvn_d", 27664.75, 27750.50) && Lv("hvn_d", 27143.00, 27206.25) && Lv("hvn_d", 26946.25, 27002.00)
                  && Lv("hvn_w", 27239.25, 27299.00) && Lv("hvn_w", 25544.25, 25604.00) && rLast.Levels.Count(x => x.IsHvn) == 7,
                  "NQ ca cuoi: HVN ngay 26801,50-26876,50 · 25538,50-25609,75 · 27664,75-27750,50 · 27143,00-27206,25 · 26946,25-27002,00; tuan truoc 27239,25-27299,00 · 25544,25-25604,00; deu da roi xa",
                  string.Join(" ; ", rLast.Levels.Where(x => x.IsHvn).Select(x => $"{x.Name} {x.Lo:0.00}-{x.Hi:0.00}")));
            Check(shLast.Count == 1 && Near(shLast[0].Lo, 26909.00, 1e-9) && Near(shLast[0].Hi, 26959.00, 1e-9) && shLast[0].Color == "do" && shLast[0].Label == "Kháng cự · 5 lần · HVN ngày + VAH hôm qua",
                  "NQ ca cuoi: vung ve 26909,00-26959,00 do 'Khang cu · 5 lan · HVN ngay + VAH hom qua'", string.Join(" | ", shLast.Select(z => $"{z.Lo}-{z.Hi} {z.Label}")));
            Check(bxLast.Count == 3 && Near(bxLast[0].Lo, 25538.50, 1e-9) && Near(bxLast[0].Hi, 25609.75, 1e-9) && bxLast[0].Label == "HVN ngày + tuần"
                  && Near(bxLast[1].Lo, 26801.50, 1e-9) && Near(bxLast[1].Hi, 26876.50, 1e-9) && bxLast[1].Label == "HVN ngày"
                  && Near(bxLast[2].Lo, 26946.25, 1e-9) && Near(bxLast[2].Hi, 27002.00, 1e-9)
                  && bxLast[0].Dist / rLast.U > 4.0 && Near(bxLast[0].Dist / rLast.U, 5.81, 0.005),
                  "NQ ca cuoi: hop ve 25538,50-25609,75 'HVN ngay + tuan' (cach 5,81 U > 4 U cu) ; 26801,50-26876,50 ; 26946,25-27002,00",
                  string.Join(" | ", bxLast.Select(b => $"{b.Lo:0.00}-{b.Hi:0.00} {b.Label} {b.Dist / rLast.U:0.00}U")));
        }
        int jd = -1;   // nến đầu phiên 24/11 (giờ nghỉ CME xong)
        for (int i = 1; i < f.N; i++) if (f.T[i].Date == new DateTime(2026, 11, 23) && f.T[i].Hour == 23 && (f.T[i] - f.T[i - 1]).TotalMinutes > 75) jd = i;
        var r0 = StrongZones.Compute(Series(f, 0, jd + 1, p), p);
        var hd = r0.Levels.Where(x => x.Name == "hvn_d" && x.Src == 1).ToList();
        Check(hd.Count == 1 && Near(hd[0].Lo, 26801.50, 1e-9) && Near(hd[0].Hi, 26876.50, 1e-9),
              "chart NQZ26 dau phien 24/11: hop HVN ngay hom qua = 26801,50-26876,50 (PLAN 13.5a)",
              string.Join(" ; ", hd.Select(x => $"{x.Lo:0.00}-{x.Hi:0.00}")) + $" · tong {r0.Levels.Count(x => x.IsHvn)} hop, chot nen {jd}");

        Color sup = Color.FromArgb(0x26, 0xA6, 0x9A), res = Color.FromArgb(0xEF, 0x53, 0x50), gold = Color.FromArgb(0xFF, 0xD6, 0x00);
        int nPng = 0, nWithBox = 0, nWithStrong = 0;
        try
        {
            string outDir = UiDir();
            foreach (var (h, m) in new[] { (4, 0), (10, 0), (11, 0) })
            {
                int j = f.T.FindIndex(t => t == new DateTime(2026, 11, 24, h, m, 0));
                if (j < 0 || j + 1 >= f.N) continue;
                var r = StrongZones.Compute(Series(f, 0, j + 1, p), p);
                var sh = StrongZones.Display(r, f.C[j], p);
                var bx = StrongZones.HvnBoxes(r, f.C[j], p);
                if (bx.Count > 0) nWithBox++;
                if (sh.Count > 0) nWithStrong++;
                Console.WriteLine($"       NQ {f.T[j]:yyyy-MM-dd HH:mm} gia {f.C[j]:0.00} U {r.U:0.0}: hop HVN [{string.Join(" ; ", bx.Select(b => $"{b.Label} {b.Lo:0.00}-{b.Hi:0.00}"))}] vung [{string.Join(" | ", sh.Select(z => $"{z.Lo:0.00}-{z.Hi:0.00} {z.Label}"))}]");
                RenderPng(f, j, sh, bx, Path.Combine(outDir, $"ca_NQ_2026-11-24_{h:00}{m:00}.png"), sup, res, gold,
                          $"NQZ26 · {f.T[j]:yyyy-MM-dd HH:mm} UTC · giá {f.C[j]:0.00} · U {r.U:0.0}");
                nPng++;
            }
            {   // thời điểm cuối dữ liệu: nến đang chạy 12:00 (nến cuối của fixture), cấu trúc tới nến đã đóng 11:30,
                // giá hiện tại = giá đóng của nến 12:00 — đúng như indicator đang chạy trên chart NQZ26 lúc đó
                int jl = f.N - 2;
                double nowL = f.C[f.N - 1];
                var r = StrongZones.Compute(Series(f, 0, jl + 1, p), p);
                var sh = StrongZones.Display(r, nowL, p);
                var bx = StrongZones.HvnBoxes(r, nowL, p);
                Console.WriteLine($"       NQ cuoi du lieu {f.T[f.N - 1]:yyyy-MM-dd HH:mm} gia {nowL:0.00} U {r.U:0.0}: hop HVN [{string.Join(" ; ", bx.Select(b => $"{StrongZones.HvnBoxText(b)} {b.Lo:0.00}-{b.Hi:0.00}"))}] vung [{string.Join(" | ", sh.Select(z => $"{z.Lo:0.00}-{z.Hi:0.00} {z.Label}"))}]");
                RenderPng(f, jl, sh, bx, Path.Combine(outDir, "ca_NQ_2026-11-24_1200_cuoi_du_lieu.png"), sup, res, gold,
                          $"NQZ26 · cuối dữ liệu {f.T[f.N - 1]:yyyy-MM-dd HH:mm} UTC (nến đang chạy) · giá {nowL:0.00} · U {r.U:0.0}", nowL);
                nPng++;
                Check(f.T[f.N - 1] == new DateTime(2026, 11, 24, 12, 0, 0)
                      && bx.Any(b => b.Label == "HVN ngày + tuần" && Near(b.Lo, 25538.50, 1e-9) && Near(b.Hi, 25609.75, 1e-9)),
                      "anh NQ cuoi du lieu 2026-11-24 12:00: co hop 'HVN ngay + tuan' 25538,50-25609,75",
                      string.Join(" | ", bx.Select(b => $"{b.Lo:0.00}-{b.Hi:0.00} {b.Label}")));
            }
        }
        catch (Exception ex) { Check(false, "render PNG NQ", ex.GetType().Name + ": " + ex.Message); }
        Check(nPng == 4 && nWithBox >= 1 && nWithStrong >= 1, "render PNG NQ 24/11 (co hop HVN va vung manh)", $"{nPng} anh, {nWithBox} co hop HVN, {nWithStrong} co vung manh");
    }

    static void StrongZoneTests()
    {
        HandCases();
        HvnClusterFixture();
        var f = LoadFixture();
        if (f == null) { Check(false, "doc fixture vung manh", FxDir()); return; }
        FixtureParity(f);
        InvarianceTests(f);
        UiTests(f);
        NqTests();
    }
}
