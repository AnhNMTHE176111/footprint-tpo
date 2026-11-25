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
        public int N => T.Count;
    }

    static string FxDir() => Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
        "../../../../research/vung_manh_2026-11-25/fixture"));

    static Fx LoadFixture()
    {
        string dir = FxDir();
        if (!File.Exists(Path.Combine(dir, "m30_bars.csv"))) return null;
        var f = new Fx();
        foreach (var line in File.ReadLines(Path.Combine(dir, "m30_bars.csv")).Skip(1))
        {
            var c = line.Split(',');
            f.T.Add(DateTime.ParseExact(c[1], "yyyy-MM-dd HH:mm:ss", IC));
            f.O.Add(double.Parse(c[2], IC)); f.H.Add(double.Parse(c[3], IC)); f.L.Add(double.Parse(c[4], IC));
            f.C.Add(double.Parse(c[5], IC)); f.V.Add(double.Parse(c[6], IC));
        }
        f.Lv = new List<KeyValuePair<double, double>>[f.N];
        for (int i = 0; i < f.N; i++) f.Lv[i] = new List<KeyValuePair<double, double>>();
        using (var gz = new GZipStream(File.OpenRead(Path.Combine(dir, "m30_levels.csv.gz")), CompressionMode.Decompress))
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
        f.Exp = JsonDocument.Parse(File.ReadAllText(Path.Combine(dir, "expected.json")));
        return f;
    }

    // Nến [from..to] của fixture thành một SzSeries (nến cuối = nến đang chạy).
    static SzSeries Series(Fx f, int from, int to, StrongZoneParams p)
    {
        int n = to - from + 1;
        return new SzSeries(f.T.GetRange(from, n), f.O.GetRange(from, n), f.H.GetRange(from, n), f.L.GetRange(from, n),
                            f.C.GetRange(from, n), f.V.GetRange(from, n), i => f.Lv[from + i], 0.1, 0.2, p);
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
        // ---- chữ D
        Check(!StrongZones.IsDShape(0.29, 0.5, p) && StrongZones.IsDShape(0.30, 0.5, p) && !StrongZones.IsDShape(0.5, 0.61, p),
              "chu D: poc 0,29 khong / 0,30 co / va 0,61 khong");
        // ---- HVN đủ điều kiện
        {
            var hh = Enumerable.Repeat(100.5, 20).ToList(); var ll = Enumerable.Repeat(99.5, 20).ToList();
            var lv = new SzLevel { Name = "hvn_d", IsHvn = true, Peak = 100, End = 5, DShape = true };
            Check(!StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: gia chua tung cach dinh 2U -> khong");
            hh[10] = 102.0;
            Check(StrongZones.HvnOk(lv, hh, ll, 15, 1, p), "HVN: vua du 2U -> co");
            Check(!StrongZones.HvnOk(lv, hh, ll, 9, 1, p), "HVN: cu rời xa sau nen j -> khong tinh");
            var lv2 = new SzLevel { Name = "hvn_d", IsHvn = true, Peak = 100, End = 15, DShape = true };
            Check(!StrongZones.HvnOk(lv2, hh, ll, 15, 1, p), "HVN: end >= j -> khong");
            var lv3 = new SzLevel { Name = "hvn_d", IsHvn = true, Peak = 100, End = 5, DShape = false };
            var pn = p.Clone(); pn.DOnly = false;
            Check(!StrongZones.HvnOk(lv3, hh, ll, 15, 1, p) && StrongZones.HvnOk(lv3, hh, ll, 15, 1, pn), "HVN: khong chu D -> chi nhan khi tat SzHvnDOnly");
        }
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
        Check(new[] { "strong", "vwap_week", "vwap_day", "va_edge", "hvn_day", "hvn_week", "lvn", "naked_poc" }.All(x => !ZonePolicy.CanMerge("strong", x) && !ZonePolicy.CanMerge(x, "strong")),
              "ZonePolicy: 'strong' khong gop voi loai nao");
        Check(ZonePolicy.BaseStrength("strong") == 90 && ZonePolicy.StrongStrength(true) == 98 && !ZonePolicy.IsMarkerType("strong"), "ZonePolicy: diem 90 / vang 98, khong phai lop moc");
        Check(ZonePolicy.CanMerge("hvn_day", "hvn_week") && !ZonePolicy.CanMerge("va_edge", "hvn_day"), "ZonePolicy: luat gop cu khong doi");
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
        int nCase = 0, badU = 0, badLv = 0, badCl = 0, badSh = 0, badNg = 0, nCl = 0, nSh = 0, nLv = 0;
        double maxU = 0, maxVw = 0, maxRatio = 0, maxExact = 0;
        var firstErr = new List<string>();
        void Err(string s) { if (firstErr.Count < 12) firstErr.Add(s); }
        var byJ = new Dictionary<int, (SzResult r, List<SzZone> sh)>();
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
                        double er = e.GetProperty("ratio").GetDouble();
                        maxRatio = Math.Max(maxRatio, Math.Abs(x.Ratio - er));
                        bool ok = StrongZones.HvnOk(x, s.H, s.L, j, r.U, p);
                        lvOk &= x.IsHvn && Near(x.Peak, pk.GetDouble(), 1e-9) && Near(x.Ratio, er, 1e-4)
                             && x.DShape == e.GetProperty("dshape").GetBoolean() && x.Src == e.GetProperty("src").GetInt32()
                             && ok == e.GetProperty("ok").GetBoolean();
                    }
                    if (!lvOk) Err($"j={j} muc {nm} C#=({x.Name} {x.Lo:0.####}-{x.Hi:0.####} r{x.Ratio:0.####} D{x.DShape}) Py=({elo}-{ehi})");
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
            if (!shOk) badSh++;
        }
        foreach (var s in firstErr) Console.WriteLine("       " + s);
        Check(nCase == 689, "so ca = 689", $"{nCase}");
        Check(badU == 0, $"U moi ca (<= 1e-6)", $"lech {badU}/{nCase}, sai so lon nhat {maxU:E2}");
        Check(badLv == 0, $"muc hop luu moi ca ({nLv} muc): ten, VWAP/sigma <= 1e-4, VAH/VAL/HVN bang dung, HVN peak/ratio/dshape/ok",
              $"lech {badLv}/{nCase}; sai so lon nhat VWAP {maxVw:E2}, VAH/VAL/HVN {maxExact:E2}, ratio {maxRatio:E2}");
        Check(badCl == 0, $"cum moi ca ({nCl} cum): lo/hi/n/pmin/pmax/names/ngroup/hvn/gold", $"lech {badCl}/{nCase}");
        Check(badNg == 0, "cum khi SzGroupEdges=false: ngroup_khong_gop, gold_khong_gop", $"lech {badNg}/{nCase}");
        Check(badSh == 0, $"vung duoc ve moi ca ({nSh} vung): lo/hi/side/color/label UTF-8 nguyen van", $"lech {badSh}/{nCase}");

        // 8.2: năm ca ghi số
        void CaseShown(string name, int j, double u, params (double lo, double hi, string col, string lab)[] want)
        {
            if (!byJ.TryGetValue(j, out var x)) { Check(false, name, "khong co ca"); return; }
            bool ok = Near(x.r.U, u, 1e-6) && x.sh.Count == want.Length;
            for (int k = 0; k < want.Length && ok; k++)
                ok &= Near(x.sh[k].Lo, want[k].lo, 1e-6) && Near(x.sh[k].Hi, want[k].hi, 1e-6) && x.sh[k].Color == want[k].col && x.sh[k].Label == want[k].lab;
            Check(ok, name, string.Join(" | ", x.sh.Select(z => $"{z.Lo:0.0}-{z.Hi:0.0} {z.Color} {z.Label}")));
        }
        CaseShown("Ca A (j=1342, vung vang)", 1342, 10.028261,
            (4026.4, 4028.6, "do", "Kháng cự · 3 lần · VAL hôm qua + VWAP hôm qua −1σ"),
            (4032.3, 4036.3, "do", "Kháng cự · 6 lần · HVN tuần"),
            (4038.8, 4042.0, "vang", "★ Kháng cự rất mạnh · 3 lần · HVN ngày + VAL tuần trước + VWAP hôm qua"));
        if (byJ.TryGetValue(1342, out var ca))
        {
            var lv = ca.r.Levels;
            double L(string nm) => lv.First(x => x.Name == nm).Lo;
            Check(Near(L("vwap_d"), 4041.8706, 1e-4) && Near(L("vwap_d_tren"), 4054.7866, 1e-4) && Near(L("vwap_d_duoi"), 4028.9546, 1e-4)
                  && Near(L("vah_d"), 4052.8, 1e-9) && Near(L("val_d"), 4029.2, 1e-9) && Near(L("vwap_w"), 4111.5234, 1e-4)
                  && Near(L("vah_w"), 4176.4, 1e-9) && Near(L("val_w"), 4042.8, 1e-9), "Ca A: so tung muc VWAP/sigma/VAH/VAL dung PLAN");
            var hd = lv.First(x => x.Name == "hvn_d");
            Check(Near(hd.Lo, 4038.0, 1e-9) && Near(hd.Hi, 4039.2, 1e-9) && Near(hd.Peak, 4039.0, 1e-9) && Near(hd.Ratio, 3.6734, 1e-4) && hd.DShape,
                  "Ca A: HVN ngay 4038,0-4039,2 dinh 4039,0 ti le 3,6734 chu D");
            var gz = ca.r.Clusters.First(z => z.Gold);
            Check(gz.N == 3 && Near(gz.Pmin, 4039.4, 1e-9) && Near(gz.Pmax, 4041.4, 1e-9), "Ca A: vung vang = 3 diem 4039,4..4041,4");
        }
        CaseShown("Ca B (j=1042, loc chong)", 1042, 10.070435,
            (4145.0, 4148.3, "xanh", "Hỗ trợ · 3 lần · VWAP hôm qua"),
            (4158.4, 4162.2, "do", "Kháng cự · 3 lần · VAL tuần trước + VWAP hôm qua +1σ"),
            (4163.9, 4168.1, "do", "Kháng cự · 4 lần · VAL tuần trước"),
            (4174.3, 4177.7, "do", "Kháng cự · 5 lần · HVN tuần + VWAP tuần trước"));
        CaseShown("Ca C (j=935, gia trong vung)", 935, 9.806087,
            (4180.4, 4184.0, "xanh", "Hỗ trợ · 6 lần · HVN tuần + VAL hôm qua + VWAP hôm qua −1σ"),
            (4192.0, 4194.0, "xanh", "Hỗ trợ · 3 lần · HVN tuần + VWAP hôm qua"),
            (4197.2, 4200.5, "xanh", "Hỗ trợ · 3 lần · HVN tuần"),
            (4202.4, 4206.0, "do", "Kháng cự · 4 lần · VWAP hôm qua +1σ (giá đang trong vùng)"));
        {
            // Ca C với SzGroupEdges = false: vùng 4180,4–4184,0 thành 3 nhóm ⇒ vàng
            var pg = p.Clone(); pg.GroupEdges = false;
            var r = StrongZones.Compute(Series(f, 0, 936, pg), pg);
            var sh = StrongZones.Display(r, f.C[935], pg);
            var z = sh.FirstOrDefault(q => Near(q.Lo, 4180.4, 1e-6));
            Check(z != null && z.Gold && z.Color == "vang" && z.Label == "★ Hỗ trợ rất mạnh · 6 lần · HVN tuần + VAL hôm qua + VWAP hôm qua −1σ",
                  "Ca C khong gop: 4180,4-4184,0 -> 3 nhom, vang", z?.Label ?? "khong thay");
        }
        CaseShown("Ca D (j=1502, mot vung)", 1502, 10.927826, (4059.4, 4062.8, "do", "Kháng cự · 3 lần · HVN ngày"));
        if (byJ.TryGetValue(1502, out var cd))
            Check(cd.r.Clusters.Count == 7 && cd.r.Levels.Any(x => x.Name == "hvn_w" && Near(x.Lo, 4036.4, 1e-9) && !x.DShape),
                  "Ca D: 7 cum; HVN tuan truoc 4036,4 khong chu D");
        CaseShown("Ca E (j=1238, chi ho tro)", 1238, 10.236522,
            (4032.3, 4036.3, "xanh", "Hỗ trợ · 5 lần · VWAP hôm qua +1σ"),
            (4042.4, 4046.3, "xanh", "Hỗ trợ · 4 lần · VAL tuần trước"));
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
        }
        // render PNG
        try
        {
            string outDir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../research/vung_manh_2026-11-25/ui"));
            Directory.CreateDirectory(outDir);
            var p = new StrongZoneParams();
            int nPng = 0;
            foreach (var (j, name) in new[] { (1342, "ca_A_vang_1342"), (1042, "ca_B_loc_chong_1042"), (935, "ca_C_trong_vung_935"), (1238, "ca_E_ho_tro_1238") })
            {
                var r = StrongZones.Compute(Series(f, 0, j + 1, p), p);
                var sh = StrongZones.Display(r, f.C[j], p);
                RenderPng(f, j, sh, Path.Combine(outDir, name + ".png"), sup, res, gold, $"{f.T[j]:yyyy-MM-dd HH:mm} UTC · giá {f.C[j]:0.0} · U {r.U:0.00}");
                nPng++;
            }
            {   // Ca C khi không gộp ⇒ vàng hỗ trợ
                var pg = p.Clone(); pg.GroupEdges = false;
                var r = StrongZones.Compute(Series(f, 0, 936, pg), pg);
                RenderPng(f, 935, StrongZones.Display(r, f.C[935], pg), Path.Combine(outDir, "ca_C_khong_gop_vang_935.png"), sup, res, gold,
                          $"{f.T[935]:yyyy-MM-dd HH:mm} UTC · SzGroupEdges = false");
                nPng++;
            }
            Check(nPng == 5 && Directory.GetFiles(outDir, "*.png").Length >= 5, "render PNG bang chinh StrongZonePainter.Paint", outDir);
        }
        catch (Exception ex) { Check(false, "render PNG", ex.GetType().Name + ": " + ex.Message); }
    }

    static void RenderPng(Fx f, int j, List<SzZone> shown, string path, Color sup, Color res, Color gold, string title)
    {
        int W = 1500, H = 820, padR = 70;
        int from = Math.Max(0, j - 90), to = j + 1;
        double top = double.MinValue, bot = double.MaxValue;
        for (int i = from; i <= to; i++) { top = Math.Max(top, f.H[i]); bot = Math.Min(bot, f.L[i]); }
        foreach (var z in shown) { top = Math.Max(top, z.Hi); bot = Math.Min(bot, z.Lo); }
        double m = (top - bot) * 0.06; top += m; bot -= m;
        var clip = new Rectangle(0, 24, W - padR, H - 24);
        float Y(double pr) => (float)(clip.Top + (top - pr) / (top - bot) * clip.Height);
        using var bmp = new Bitmap(W, H);
        using var g = Graphics.FromImage(bmp);
        g.SmoothingMode = SmoothingMode.None;
        g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.ClearTypeGridFit;
        g.Clear(Color.FromArgb(19, 23, 34));
        using (var grid = new Pen(Color.FromArgb(40, 255, 255, 255)))
        using (var fa = new Font("Arial", 8))
        using (var ba = new SolidBrush(Color.FromArgb(170, 255, 255, 255)))
        {
            double step = 5; for (double pr = Math.Ceiling(bot / step) * step; pr <= top; pr += step)
            { float y = Y(pr); g.DrawLine(grid, clip.Left, y, clip.Right, y); g.DrawString(pr.ToString("0", IC), fa, ba, clip.Right + 6, y - 7); }
        }
        float cw = (float)clip.Width / (to - from + 4);
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
            StrongZonePainter.Paint(g, clip, Y, shown, sup, res, gold, 0.1, fnt);
        double now = f.C[j];
        using (var pn = new Pen(Color.FromArgb(200, 255, 255, 255), 1f) { DashStyle = DashStyle.Dot })
            g.DrawLine(pn, clip.Left, Y(now), clip.Right, Y(now));
        using (var ft = new Font("Arial", 9, FontStyle.Bold))
        using (var bt = new SolidBrush(Color.White))
            g.DrawString("Session Zones · vùng mạnh (chưa kiểm định) · " + title, ft, bt, 6, 4);
        bmp.Save(path, ImageFormat.Png);
    }

    static void StrongZoneTests()
    {
        HandCases();
        var f = LoadFixture();
        if (f == null) { Check(false, "doc fixture vung manh", FxDir()); return; }
        FixtureParity(f);
        InvarianceTests(f);
        UiTests(f);
    }
}
