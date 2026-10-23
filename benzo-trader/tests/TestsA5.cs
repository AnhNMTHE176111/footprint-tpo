// Test CHẠY THẬT cho BenzoSetupA5 (setup A "Phá hồi v5"). Gọi từ tests/Program.cs: var (o, f) = TestsA5.Run();
// Dữ liệu giả: nến dựng tay + IA5VclSource giả (không dựng VclCore) — trừ test 22 (file 90 ngày) và test 23 (VclCore thật).
// Cảnh quay chuẩn ("Scene"): vùng S/R giả [101;102] có mặt mọi nến; 40 nến phẳng ở 101; nến 44 (M5 đóng) đóng 102,8 ⇒ cú phá lên;
// nến 45 lập đỉnh 104,5 (cách cạnh 2,5 ⇒ đã trang bị); hồi 46–48; nến 49 là nến xác nhận ⇒ tín hiệu MUA.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using BenzoTraderNs;

static class TestsA5
{
    static int _ok, _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 && !ok ? "  -> " + detail : ""));
        if (ok) _ok++; else _fail++;
    }
    static bool Near(double a, double b, double eps = 1e-6) => Math.Abs(a - b) < eps;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    static readonly DateTime T0 = new DateTime(2026, 10, 21, 3, 0, 0, DateTimeKind.Utc);   // 10:00 VN (pha Á, ngoài khung mở ảo)

    // ---------------------------------------------------------------- dụng cụ
    sealed class Seq
    {
        public readonly List<BarData> Bars = new();
        public DateTime T;
        public Seq(DateTime t0) { T = t0; }
        public Seq Add(double o, double h, double l, double c, double delta = 10)
        {
            Bars.Add(new BarData { Idx = Bars.Count, Time = T.AddMinutes(Bars.Count), O = o, H = h, L = l, C = c, Vol = 100, Delta = delta });
            return this;
        }
        public Seq Flat(int n, double p) { for (int k = 0; k < n; k++) Add(p, p, p, p); return this; }
        public int Count => Bars.Count;
    }

    sealed class FakeVcl : IA5VclSource
    {
        public Func<int, IEnumerable<(int, double, double)>> F = _ => Array.Empty<(int, double, double)>();
        private List<(int, double, double)> _d = new();
        public int Pushes;
        public IReadOnlyList<(int Id, double Lo, double Hi)> Display => _d;
        public void Push(int i, BarData b, IReadOnlyList<LevelVol> lv) { Pushes++; _d = F(i).ToList(); }
    }

    static IEnumerable<(int, double, double)> Z1(int i) { yield return (1, 101.0, 102.0); }

    /// <summary>Chạy tay Zones.Push → Observe → TryDetect (như engine nhưng không có luật 1 lệnh mở).</summary>
    sealed class Hx
    {
        public readonly List<BarData> Bars = new();
        public readonly BenzoZones Z = new();
        public readonly ClosedBars View;
        public readonly SetupContext Ctx;
        public readonly DetectorA5 D;
        public Func<int, IReadOnlyList<LevelVol>> Lv = _ => Array.Empty<LevelVol>();
        public readonly List<(int i, Signal s)> Sigs = new();
        public Hx(DetectorA5 d, Func<DateTime, bool> news = null)
        {
            D = d; View = new ClosedBars(Bars);
            Ctx = new SetupContext { Symbol = "GCZ26", Tick = 0.1, Bars = View, Signals = new List<Signal>(), Zones = Z, GetLevels = i => Lv(i), IsNewsBlocked = news ?? (_ => false) };
        }
        public Signal Step(BarData b)
        {
            int i = Bars.Count; Bars.Add(b); View.Limit = i + 1;
            Z.Push(i, b, Lv(i));
            D.Observe(Ctx, i);
            var s = D.TryDetect(Ctx, i);
            if (s != null) Sigs.Add((i, s));
            return s;
        }
        public void Run(IEnumerable<BarData> bars) { foreach (var b in bars) Step(b); }
    }

    static Seq Scene(DateTime? t0 = null)
    {
        var s = new Seq(t0 ?? T0);
        s.Flat(44, 101.0);                         // 0..43
        s.Add(101.0, 103.0, 100.9, 102.8);         // 44 cú phá (M5 đóng)
        s.Add(102.8, 104.5, 102.7, 104.4);         // 45 đỉnh mới 104,5
        s.Add(104.4, 104.4, 103.4, 103.5);         // 46
        s.Add(103.5, 103.6, 102.8, 102.9);         // 47
        s.Add(102.9, 103.0, 102.2, 102.3);         // 48
        s.Add(102.3, 102.9, 102.2, 102.8, 50);     // 49 nến xác nhận (xanh, thân ≥ 50%, Δ+50)
        return s;
    }

    static Hx NewHx(Func<int, IEnumerable<(int, double, double)>> zones = null, bool vblock = false, Func<DateTime, bool> news = null)
    {
        var f = new FakeVcl { F = zones ?? Z1 };
        var d = new DetectorA5(true, f) { VirtualOpenBlock = vblock, StateLog = new List<A5StateLog>(), UseVwap = false };
        return new Hx(d, news);
    }

    static string Fmt(double v) => v.ToString("0.0###", Inv);

    // ---------------------------------------------------------------- 1–2: toán HVN
    static void T01_02()
    {
        Console.WriteLine("[A5-1] HvnMath.FindHvn (số kỳ vọng lấy từ kernel.find_hvn của Python)");
        // python3 -c "import numpy as np,kernel as K; p=K.Profiles.row_price(np.arange(100)); v=np.full(100,10.0); v[20]=200; v[70]=120; print(K.find_hvn(p,v))"
        long[] rows = Enumerable.Range(0, 100).Select(x => (long)x).ToArray();
        var v = Enumerable.Repeat(10.0, 100).ToArray(); v[20] = 200; v[70] = 120;
        var r1 = HvnMath.FindHvn(rows, v);
        Check(r1.Count == 4 && Near(r1[0].price, 3.0) && Near(r1[1].price, 5.0) && Near(r1[2].price, 13.0) && Near(r1[3].price, 15.0)
              && Near(r1[0].ratio, 2.097902098, 1e-8) && Near(r1[2].ratio, 1.538461538, 1e-8),
            "profile 1: 4 đỉnh phẳng (3,0 · 5,0 · 13,0 · 15,0), tỉ lệ 2,0979 / 1,5385 (giống Python)", string.Join(" ", r1.Select(x => $"{x.price}:{x.ratio:0.000000000}")));
        v = Enumerable.Repeat(10.0, 100).ToArray(); v[30] = 200; v[36] = 150; v[80] = 100;
        var r2 = HvnMath.FindHvn(rows, v);
        Check(r2.Count == 1 && Near(r2[0].price, 6.2) && Near(r2[0].ratio, 2.816901408, 1e-8), "profile 2: hai đỉnh gần nhau (< 20 tick) gộp còn 1 đỉnh mạnh hơn (6,2)", string.Join(" ", r2.Select(x => $"{x.price}:{x.ratio:0.000000000}")));
        long[] rows3 = Enumerable.Range(1000, 30).Concat(Enumerable.Range(1040, 30)).Select(x => (long)x).ToArray();
        var v3 = Enumerable.Repeat(5.0, 60).ToArray(); v3[10] = 90; v3[45] = 60;
        var r3 = HvnMath.FindHvn(rows3, v3);
        Check(r3.Count == 2 && Near(r3[0].price, 201.0) && Near(r3[1].price, 203.0) && Near(r3[0].ratio, 1.73553719, 1e-8), "profile 3: hàng không liên tục (nhảy 10 hàng) vẫn khớp Python (201,0 · 203,0)", string.Join(" ", r3.Select(x => $"{x.price}:{x.ratio:0.000000000}")));
        Check(HvnMath.FindHvn(new long[] { 1, 2 }, new double[] { 5, 5 }).Count == 0 && HvnMath.FindHvn(rows, new double[100]).Count == 0, "n < 3 hoặc tổng volume 0 ⇒ rỗng");

        Console.WriteLine("[A5-2] PeakSharpness + ClampBand");
        var prof = new Dictionary<long, double>();
        double[] vv = { 10, 10, 60, 90, 100, 95, 92, 60, 10, 10, 10 };
        for (int k = 0; k < vv.Length; k++) prof[100 + k] = vv[k];
        var (lo, hi) = HvnMath.PeakSharpness(prof, 104 * 0.2);
        Check(Near(lo, 103 * 0.2) && Near(hi, 106 * 0.2), "dải nới tới khi hàng kề < 90% đỉnh: hàng 103–106", $"{lo} {hi}");
        var plateau = new Dictionary<long, double>();
        for (int k = 100; k <= 114; k++) plateau[k] = 100;
        var (l2, h2) = HvnMath.PeakSharpness(plateau, 107 * 0.2);
        Check(Near(l2, 100 * 0.2) && Near(h2, 114 * 0.2), "bậc thang đều ⇒ dải rộng 15 hàng", $"{l2} {h2}");
        var (cl, ch) = HvnMath.ClampBand(l2, h2, 107 * 0.2);
        Check(Near(cl, 107 * 0.2 - 1.0) && Near(ch, 107 * 0.2 + 1.0), "dải rộng 2,8 giá ⇒ kẹp còn 2,0 giá đối xứng quanh đỉnh", $"{cl} {ch}");
        var (pl, ph) = HvnMath.PeakSharpness(plateau, 999.0);
        Check(pl == 999.0 && ph == 999.0, "đỉnh không có trong profile ⇒ (đỉnh, đỉnh)");
        var gap = new Dictionary<long, double> { [100] = 50, [101] = 100, [103] = 100 };   // hàng 102 không tồn tại
        var (gl, gh) = HvnMath.PeakSharpness(gap, 101 * 0.2);
        Check(Near(gl, 101 * 0.2) && Near(gh, 101 * 0.2), "hàng kề KHÔNG tồn tại ⇒ dừng (không nhảy qua lỗ): hàng 100 chỉ 50 < 90%, hàng 102 vắng ⇒ (đỉnh, đỉnh)", $"{gl} {gh}");
    }

    // ---------------------------------------------------------------- 3: HvnBook
    static void T03()
    {
        Console.WriteLine("[A5-3] HvnBook: 5 tuần giả, phiên < 300 nến bị loại, HVN ngày = phiên ≥ 300 nến gần nhất, tỉa vẫn giữ phiên q");
        var book = new HvnBook();
        DateTime t = T0; int idx = 0;
        void Sess(int n, long peakRow)
        {
            for (int k = 0; k < n; k++)
            {
                var b = new BarData { Idx = idx, Time = t, O = 100, H = 100, L = 100, C = 100, Vol = 100 };
                book.Step(idx, b, new[] { new LevelVol(1000 * 0.2 + k * 0.2, 0, 1, 1), new LevelVol(peakRow * 0.2, 0, 3, 3) }, k == 0);
                idx++; t = t.AddMinutes(1);
            }
        }
        long P0 = 1050, P1 = 1100, P2 = 1170, P3 = 1240;
        long[] P = { P0, P1, P2, P3, 1180 };
        for (int w = 0; w < 5; w++)
        {
            if (w > 0) t = t.AddHours(50);                 // > 30 giờ ⇒ tuần mới
            Sess(300, P[w]);
            t = t.AddHours(2);
            if (w == 3) Sess(100, 1200); else if (w < 4) Sess(300, P[w]);   // tuần 3: phiên thứ hai chỉ 100 nến (mỏng, bị loại)
        }
        // tuần 4 mới bắt đầu ở phiên đầu của nó (đã tính lúc Step k==0). Kiểm HVN tuần tại thời điểm đó bằng cách dựng lại tới đó.
        var book2 = new HvnBook();
        t = T0; idx = 0;
        var save = book; book = book2;
        for (int w = 0; w <= 4; w++)
        {
            if (w > 0) t = t.AddHours(50);
            Sess(w == 4 ? 1 : 300, P[w]);                    // tuần 4: chỉ nến đầu để tính mức
            if (w == 4) break;
            t = t.AddHours(2);
            if (w == 3) Sess(100, 1200); else Sess(300, P[w]);
        }
        var pr = book2.HvnW.Select(x => Math.Round(x.p, 6)).OrderBy(x => x).ToList();
        // đỉnh 1 hàng sau khi làm mượt ±5 hàng thành bậc thang 11 hàng; find_hvn lấy hàng THẤP nhất của bậc thang (cùng Python) ⇒ hàng đỉnh − 5
        Check(pr.Count == 3 && Near(pr[0], (P1 - 5) * 0.2) && Near(pr[1], (P2 - 5) * 0.2) && Near(pr[2], (P3 - 5) * 0.2),
            "HVN tuần của tuần 4 chỉ dùng tuần 1–3 (đỉnh tuần 1, 2, 3); không có đỉnh tuần 0 và không có đỉnh phiên mỏng 100 nến", string.Join(" ", pr));
        Check(book2.HvnW.All(x => x.lo >= x.p - 1.0 - 1e-9 && x.hi <= x.p + 1.0 + 1e-9 && x.lo <= x.p && x.hi >= x.p), "dải HVN tuần luôn kẹp trong đỉnh ± 1 giá (rộng ≤ 2,0)");
        Check(book2.HvnD.Count == 1 && Near(book2.HvnD[0], (P3 - 5) * 0.2), "HVN ngày = HVN của phiên ≥ 300 nến gần nhất (tuần 3, phiên 1; phiên 100 nến bị bỏ qua)", string.Join(" ", book2.HvnD));
        // tỉa: 4 tuần liền chỉ có phiên mỏng ⇒ phiên q (tuần 3) vẫn giữ cho HVN ngày, HVN tuần rỗng
        book = new HvnBook(); t = T0; idx = 0;
        Sess(300, P0); t = t.AddHours(2); Sess(300, P0);   // tuần 0 (2 phiên đủ)
        for (int w = 1; w <= 8; w++) { t = t.AddHours(50); Sess(w == 8 ? 1 : 100, 1200); }
        Check(book.HvnW.Count == 0, "chỉ còn phiên mỏng ⇒ HVN tuần rỗng", book.HvnW.Count.ToString());
        Check(book.HvnD.Count == 1 && Near(book.HvnD[0], (P0 - 5) * 0.2), "phiên q (≥ 300 nến) cũ quá 3 tuần vẫn được giữ cho HVN ngày", string.Join(" ", book.HvnD));
        Check(book.ClosedCount == 4, "tỉa bỏ phiên cũ quá 3 tuần: còn đúng 4 phiên đã đóng (q + 3 phiên mỏng của tuần 5, 6, 7)", book.ClosedCount.ToString());
    }

    // ---------------------------------------------------------------- 4: VWAP
    static void T04()
    {
        Console.WriteLine("[A5-4] VWAP: E động; phiên < 30 nến ⇒ không mở VWAP_D");
        var d = new DetectorA5(false) { StateLog = new List<A5StateLog>() };
        var h = new Hx(d);
        var s = new Seq(T0).Flat(29, 100.0);
        s.Add(100, 103, 100, 103);                                   // nến 29 (M5 đóng): posin = 29 < 30
        h.Run(s.Bars);
        Check(!d.DebugStates().Any(x => x.Name.StartsWith("VWAP")), "M5 đóng ngoài VWAP ở nến 29 (phiên mới 29 nến) ⇒ không có trạng thái VWAP");
        d = new DetectorA5(false) { StateLog = new List<A5StateLog>() };
        h = new Hx(d);
        s = new Seq(T0).Flat(34, 100.0);
        s.Add(100, 102.2, 100, 102);                                 // nến 34 (M5 đóng): posin = 34 ≥ 30
        h.Run(s.Bars);
        var st = d.DebugStates().FirstOrDefault(x => x.Name == "VWAP_D");
        Check(st != null && st.S == 1 && Near(st.E, h.Z.VwapDAt(34)) && st.E > 100.0 && st.E < 100.2, "M5 đóng trên VWAP ngày ở nến 34 ⇒ mở trạng thái MUA, E = VWAP tại nến đó", st == null ? "không có" : Fmt(st.E));
        // đi tiếp: đỉnh mới 104,5 ⇒ đã trang bị; E của Watch = VWAP HIỆN TẠI (động), nhãn có "(động)"
        for (int k = 35; k < 38; k++) h.Step(new BarData { Idx = k, Time = T0.AddMinutes(k), O = 102, H = 102.2 + (k - 34), L = 102, C = 102.1 + (k - 34), Vol = 100, Delta = 10 });
        var w = d.Watch(h.Bars.Count - 1, h.Bars.Last(), false);
        var wv = w.FirstOrDefault(x => x.Name == "VWAP_D");
        Check(wv != null && Near(wv.E, h.Z.VwapDAt(h.Bars.Count - 1)) && wv.IsDyn && wv.Label.Contains("(động)") && wv.Label.StartsWith("A chờ MUA · VWAP ngày"), "Watch: E = VWAP hiện tại, nhãn có '(động)'", wv?.Label ?? "không có");
    }

    // ---------------------------------------------------------------- 5–9: trạng thái VCL
    static void T05()
    {
        Console.WriteLine("[A5-5] Mở trạng thái VCL [100;102]: M5 đóng 102,5 ⇒ S=+1, E=102; cực trị 103,5 chưa trang bị; 104,1 ⇒ trang bị");
        var h = NewHx(i => new[] { (1, 100.0, 102.0) });
        var s = new Seq(T0).Flat(44, 101.0);
        s.Add(101, 102.6, 101, 102.5);                               // 44: M5 đóng 102,5
        h.Run(s.Bars);
        var st = h.D.DebugStates();
        Check(st.Count == 1 && st[0].Name == "VCL_1" && st[0].S == 1 && Near(st[0].E, 102.0) && st[0].P0 == 44 && !st[0].Armed && Near(st[0].PkVal, 102.6),
            "mở S=+1, E=102, P0=44, đỉnh 102,6 chưa trang bị", string.Join(";", st.Select(x => $"{x.Name} S{x.S} E{x.E} P{x.P0} armed={x.Armed}")));
        h.Step(new BarData { Idx = 45, Time = T0.AddMinutes(45), O = 102.5, H = 103.5, L = 102.4, C = 103.4, Vol = 100, Delta = 10 });
        st = h.D.DebugStates();
        Check(st.Count == 1 && !st[0].Armed && Near(st[0].PkVal, 103.5), "đỉnh 103,5 (cách cạnh 1,5) ⇒ chưa trang bị", string.Join(";", st.Select(x => $"{x.PkVal} {x.Armed}")));
        h.Step(new BarData { Idx = 46, Time = T0.AddMinutes(46), O = 103.4, H = 104.1, L = 103.3, C = 104.0, Vol = 100, Delta = 10 });
        st = h.D.DebugStates();
        Check(st.Count == 1 && st[0].Armed && Near(st[0].PkVal, 104.1), "đỉnh 104,1 (cách cạnh 2,1 ≥ 2) ⇒ đã trang bị", string.Join(";", st.Select(x => $"{x.PkVal} {x.Armed}")));
    }

    static void T06()
    {
        Console.WriteLine("[A5-6] Luật cú phá thật của VCL (vùng phải đang hiển thị ở chân cú phá)");
        // (a) vùng xuất hiện ngay trong chân cú phá (từ nến 41) ⇒ không mở
        var h = NewHx(i => i >= 41 ? new[] { (1, 101.0, 102.0) } : Array.Empty<(int, double, double)>());
        var s = new Seq(T0).Flat(41, 101.0);
        s.Flat(3, 102.6);                                            // 41..43 đã ngoài vùng
        s.Add(102.6, 103.0, 102.5, 102.8);                           // 44: M5 đóng ngoài
        h.Run(s.Bars);
        Check(h.D.DebugStates().Count == 0, "vùng mới xuất hiện giữa lúc giá đã ngoài ⇒ không phải cú phá thật ⇒ không mở");
        // (b) giá ở DƯỚI vùng > 60 nến rồi M5 đóng dưới ⇒ VCL không mở; cùng tình huống VAL_D (vùng điểm) ⇒ mở
        var d = new DetectorA5(true, new FakeVcl { F = i => new[] { (1, 101.0, 102.0) } }) { StateLog = new List<A5StateLog>(), UseVwap = false };
        var hh = new Hx(d);
        var prev = new Seq(T0.AddDays(-1));
        prev.Flat(400, 98.0);                                        // phiên hôm qua ≥ 300 nến, mọi volume ở giá 98
        var lvPrev = new Func<int, IReadOnlyList<LevelVol>>(i => i < 400 ? new[] { new LevelVol(98.0, 0, 1, 1) } : Array.Empty<LevelVol>());
        hh.Lv = lvPrev;
        hh.Run(prev.Bars);
        var cur = new Seq(T0);
        cur.Bars.AddRange(Enumerable.Range(0, 85).Select(k => new BarData { Idx = 400 + k, Time = T0.AddMinutes(k), O = 96.9, H = 96.9, L = 96.9, C = 96.9, Vol = 100, Delta = 10 }));
        // hiện VAL_D = 98 (điểm) và giá 96,9 dưới vùng suốt 85 nến
        hh.Run(cur.Bars);
        var sts = d.DebugStates();
        Check(!sts.Any(x => x.Name.StartsWith("VCL")), "giá dưới vùng VCL suốt > 60 nến ⇒ chân cú phá không có nến 'trong' ⇒ VCL không mở");
        Check(sts.Any(x => x.Name == "VAL_D" && x.S == -1), "cùng tình huống nhưng VAL_D (vùng điểm) ⇒ vẫn mở (luật cú phá thật chỉ áp cho VCL)", string.Join(";", sts.Select(x => x.Name + x.S)));
    }

    static void T07()
    {
        Console.WriteLine("[A5-7] Huỷ: đóng lại trong 0,5 ⇒ giữ; 1,5 ⇒ huỷ; đóng dưới lo ⇒ huỷ +1 và mở −1 cùng nến");
        var zones = new Func<int, IEnumerable<(int, double, double)>>(i => new[] { (1, 100.0, 102.0) });
        var h = NewHx(zones);
        var s = new Seq(T0).Flat(44, 101.0);
        s.Add(101, 102.6, 101, 102.5);                               // 44: mở +1
        for (int k = 45; k < 49; k++) s.Add(102.5, 102.6, 102.4, 102.5);
        s.Add(102.5, 102.5, 101.5, 101.5);                           // 49 (M5): đóng 101,5 = canh 102 − 0,5 ⇒ giữ
        h.Run(s.Bars);
        Check(h.D.DebugStates().Any(x => x.S == 1), "M5 đóng lại trong 0,5 giá ⇒ giữ trạng thái");
        for (int k = 50; k < 53; k++) h.Step(new BarData { Idx = k, Time = T0.AddMinutes(k), O = 101.5, H = 101.5, L = 101.5, C = 101.5, Vol = 100, Delta = 10 });
        h.Step(new BarData { Idx = 53, Time = T0.AddMinutes(53), O = 101.5, H = 101.5, L = 100.8, C = 100.8, Vol = 100, Delta = 10 });
        h.Step(new BarData { Idx = 54, Time = T0.AddMinutes(54), O = 100.8, H = 100.8, L = 100.8, C = 100.8, Vol = 100, Delta = 10 });   // 54: M5 đóng 100,8 (huỷ sâu 1,2 > 1)
        Check(!h.D.DebugStates().Any(x => x.S == 1) && h.D.StateLog.Any(x => x.Why == "cancel" && x.S == 1), "M5 đóng lại trong 1,2 giá (> 1) ⇒ huỷ", string.Join(";", h.D.DebugStates().Select(x => x.Name + x.S)));
        // đóng dưới lo ⇒ huỷ +1 và mở −1 cùng nến
        var h2 = NewHx(zones);
        var s2 = new Seq(T0).Flat(44, 101.0);
        s2.Add(101, 102.6, 101, 102.5);                              // 44 mở +1
        for (int k = 45; k < 49; k++) s2.Add(101.0, 101.0, 101.0, 101.0);
        s2.Add(101.0, 101.0, 99.4, 99.5);                            // 49: M5 đóng 99,5 < lo 100
        h2.Run(s2.Bars);
        var st = h2.D.DebugStates();
        Check(st.Count == 1 && st[0].S == -1 && Near(st[0].E, 100.0) && h2.D.StateLog.Any(x => x.Why == "cancel" && x.S == 1), "M5 đóng dưới lo ⇒ huỷ +1 và mở −1 (E = lo) cùng nến", string.Join(";", st.Select(x => x.Name + x.S + " E" + x.E)));
    }

    static void T08()
    {
        Console.WriteLine("[A5-8] Hết hạn: 31 nến sau cực trị không có nến xác nhận ⇒ mất trạng thái; M5 ngoài kế tiếp ⇒ mở lại, BrkNo = 2");
        var h = NewHx();
        var s = Scene();
        // thay nến 49 bằng nến KHÔNG xác nhận (đỏ), rồi đi ngang ở 102,5 tới nến 78
        s.Bars.RemoveAt(49);
        s.Add(102.3, 102.9, 102.2, 102.25, 50);
        for (int k = 50; k <= 78; k++) s.Add(102.5, 102.5, 102.5, 102.5);
        for (int k = 0; k <= 75; k++) h.Step(s.Bars[k]);
        Check(h.D.DebugStates().Any(x => x.Name == "VCL_1" && x.BrkNo == 1 && x.PkPos == 45), "nến 75 (cách đỉnh 30 nến): vẫn còn trạng thái");
        h.Step(s.Bars[76]);
        Check(!h.D.DebugStates().Any() && h.D.StateLog.Any(x => x.Why == "expire" && x.P0 == 44), "nến 76 (31 nến sau đỉnh, không có nến xác nhận): mất trạng thái (expire)");
        for (int k = 77; k <= 78; k++) h.Step(s.Bars[k]);
        h.Step(new BarData { Idx = 79, Time = T0.AddMinutes(79), O = 102.5, H = 102.5, L = 102.5, C = 102.5, Vol = 100, Delta = 10 });   // 79: M5 đóng ngoài
        var st = h.D.DebugStates();
        Check(st.Count == 1 && st[0].BrkNo == 2 && st[0].P0 == 79,
            "M5 đóng ngoài kế tiếp (nến 79) ⇒ mở lại với BrkNo = 2", string.Join(";", st.Select(x => $"P0={x.P0} brk={x.BrkNo}")) + " log=" + string.Join(",", h.D.StateLog.Select(x => x.Why)));
    }

    static void T09()
    {
        Console.WriteLine("[A5-9] Đà đi tiếp 40 nến (cực trị liên tục mới) rồi hồi ⇒ vẫn vào được (không cắt hạn tính từ nến phá)");
        var h = NewHx();
        var s = new Seq(T0).Flat(44, 101.0);
        s.Add(101.0, 103.0, 100.9, 102.8);                           // 44
        s.Add(102.8, 104.5, 102.7, 104.4);                           // 45: L = 2,1 từ nến 44
        double top = 104.5;
        for (int k = 46; k <= 85; k++) { top += 0.3; s.Add(top - 0.3, top, top - 0.4, top - 0.1); }   // 40 nến, mỗi nến đỉnh mới, biên độ 0,4
        double tp = top;
        s.Add(tp - 0.1, tp - 0.1, tp - 0.9, tp - 0.9);               // 86 hồi
        s.Add(tp - 0.9, tp - 0.9, tp - 1.5, tp - 1.5);               // 87
        s.Add(tp - 1.5, tp - 1.5, tp - 2.0, tp - 2.0);               // 88
        // hồi về vùng: giá giảm tới ~102
        double c = tp - 2.0;
        int i = 89;
        while (c > 103.3) { double n = Math.Max(103.3, c - 1.5); s.Add(c, c, n, n); c = n; i++; }
        s.Add(c, c, 102.3, 102.4); i++;
        s.Add(102.4, 103.0, 102.35, 102.95, 50);                     // nến xác nhận
        var sig = new List<(int i, Signal s)>();
        h.Run(s.Bars);
        Check(h.Sigs.Count >= 1, "có tín hiệu sau pha đà dài (> 30 nến kể từ nến phá)", "n=" + h.Sigs.Count);
        if (h.Sigs.Count >= 1)
        {
            var first = h.Sigs[0];
            Check(first.i - 44 > 30, "tín hiệu vào sau nến phá > 30 nến (V3 cũ đã hết hạn)", (first.i - 44).ToString());
            var info = h.D.LastInfo;
            Check(info != null && info.PkPos >= 85 && Near(info.L, 2.1), "cực trị cuối ≥ nến 85; L = nến đà lớn nhất (2,1)", info == null ? "null" : $"pk={info.PkPos} L={info.L}");
        }
    }

    // ---------------------------------------------------------------- 10–12: điều kiện vào, SL/TP, rời bộ
    static void T10_11()
    {
        Console.WriteLine("[A5-10] Điều kiện vào: hồi 3 nến ✓; hồi 2 nến ✗; nến hồi ≥ L ✗; không nến xác nhận ✗; chạm bằng râu ✓");
        var h = NewHx(); h.Run(Scene().Bars);
        Check(h.Sigs.Count == 1 && h.Sigs[0].i == 49 && h.Sigs[0].s.Side == 1 && h.Sigs[0].s.Zone == "VCL_1", "cảnh chuẩn: 1 tín hiệu MUA ở nến 49, vùng VCL_1", string.Join(";", h.Sigs.Select(x => x.i + ":" + x.s.Zone)));
        // hồi 2 nến: nến xác nhận ở 48 (npb = 48 − 1 − 45 = 2)
        var s = Scene(); s.Bars.RemoveRange(48, 2);
        s.Add(102.9, 103.4, 102.8, 103.3, 50);                       // 48 (xác nhận nhưng chỉ hồi 2)
        var h2 = NewHx(); h2.Run(s.Bars);
        Check(h2.Sigs.Count == 0, "hồi chỉ 2 nến ⇒ không vào");
        // nến hồi có biên độ ≥ L: nến 47 biên độ 2,2 ≥ 2,1
        s = Scene(); s.Bars[47] = new BarData { Idx = 47, Time = T0.AddMinutes(47), O = 103.5, H = 103.6, L = 101.4, C = 102.9, Vol = 100, Delta = 10 };
        var h3 = NewHx(); h3.Run(s.Bars);
        Check(h3.Sigs.Count == 0, "nến hồi biên độ 2,2 ≥ L 2,1 ⇒ không vào");
        // không nến xác nhận: nến 49 đỏ
        s = Scene(); s.Bars[49] = new BarData { Idx = 49, Time = T0.AddMinutes(49), O = 102.8, H = 102.9, L = 102.2, C = 102.3, Vol = 100, Delta = 50 };
        var h4 = NewHx(); h4.Run(s.Bars);
        Check(h4.Sigs.Count == 0, "thiếu nến xác nhận (nến đỏ) ⇒ không vào");
        // chạm bằng râu: đóng cách E 1,3 nhưng râu dưới chạm E = 102
        s = Scene(); s.Bars[49] = new BarData { Idx = 49, Time = T0.AddMinutes(49), O = 102.1, H = 103.4, L = 101.9, C = 103.3, Vol = 100, Delta = 50 };
        var h5 = NewHx(); h5.Run(s.Bars);
        Check(h5.Sigs.Count == 1 && h5.Sigs[0].i == 49, "đóng cách E 1,3 giá nhưng râu chạm E ⇒ vẫn vào", "n=" + h5.Sigs.Count);

        Console.WriteLine("[A5-11] SL/TP: MUA ở E = hi, SL = ⌊min(L_cf, lo − 1) − 0,3⌋, TP = 3R; vùng rộng ⇒ SL > 4 ⇒ không vào");
        var sg = h.Sigs[0].s;
        Check(Near(sg.Entry, 102.8) && Near(sg.Sl, 99.7) && Near(sg.Tp, 112.1), "Entry 102,8 · SL 99,7 · TP 112,1 (R = 3,1 × 3)", $"{sg.Entry} {sg.Sl} {sg.Tp}");
        string exp = "phá lên vùng S/R 101,0–102,0 (M5 đóng ngoài 10:45), đỉnh cách vùng 2,5 giá sau 1 nến, hồi 3 nến, nến xác nhận Δ+50";
        Check(sg.Reason == exp, "Reason đúng mẫu tiếng Việt", sg.Reason);
        var info = h.D.LastInfo;
        Check(info.P0 == 44 && info.PkPos == 45 && Near(info.PkVal, 104.5) && Near(info.L, 2.1) && info.Npb == 3 && info.BrkNo == 1 && info.EntNo == 1 && Near(info.E, 102.0), "LastInfo: P0 44, đỉnh 45 = 104,5, L 2,1, hồi 3, BrkNo 1, EntNo 1");
        var hw = NewHx(i => new[] { (1, 98.0, 102.0) });
        s = Scene(); hw.Run(s.Bars);
        Check(hw.Sigs.Count == 0, "vùng rộng 4 giá ⇒ SL > 4 ⇒ không vào");
        Check(hw.D.DebugStates().Any(x => x.NEnt == 0), "…và trạng thái KHÔNG bị tiêu (NEnt vẫn 0)");
    }

    static void T12()
    {
        Console.WriteLine("[A5-12] Rời bộ: eid vắng ở nến quét ⇒ không vào; vắng ở M5 kế ⇒ kết thúc 'roi_bo'");
        // nến 49 thành nến đỏ nhỏ; nến 50 là nến xác nhận (hồi 4 nến)
        Func<Seq> mk = () =>
        {
            var s = Scene();
            s.Bars[49] = new BarData { Idx = 49, Time = T0.AddMinutes(49), O = 102.4, H = 102.45, L = 102.3, C = 102.35, Vol = 100, Delta = 10 };
            s.Add(102.4, 103.0, 102.35, 102.95, 50);                 // 50 xác nhận
            return s;
        };
        var hc = NewHx(); hc.Run(mk().Bars);
        Check(hc.Sigs.Count == 1 && hc.Sigs[0].i == 50, "đối chứng: vùng có mặt ⇒ nến 50 ra tín hiệu");
        var h = NewHx(i => i == 50 ? Array.Empty<(int, double, double)>() : new[] { (1, 101.0, 102.0) });
        h.Run(mk().Bars);
        Check(h.Sigs.Count == 0, "vùng vắng đúng ở nến xác nhận (nến 50) ⇒ không vào");
        var h2 = NewHx(i => i == 54 ? Array.Empty<(int, double, double)>() : new[] { (1, 101.0, 102.0) });
        var s2 = mk(); for (int k = 51; k <= 54; k++) s2.Add(102.4, 102.4, 102.4, 102.4);
        h2.Run(s2.Bars);
        Check(h2.D.StateLog.Any(x => x.Why == "roi_bo" && x.P0 == 44) && h2.D.DebugStates().Count == 0, "vùng vắng ở M5 kế (nến 54) ⇒ trạng thái kết thúc 'roi_bo'", string.Join(",", h2.D.StateLog.Select(x => x.Why)));
    }

    // ---------------------------------------------------------------- 13–15: tranh cùng nến, đếm, đặt lại cực trị
    static void T13()
    {
        Console.WriteLine("[A5-13] Cùng nến: cùng khoảng cách ⇒ vùng hạng cao hơn (VAH_D) thắng VCL; khác khoảng cách ⇒ gần hơn thắng");
        // phiên hôm qua: mọi volume ở giá 102,0 ⇒ VAH_D = VAL_D = 102,0 (trùng cạnh trên của VCL [101;102])
        var d = new DetectorA5(true, new FakeVcl { F = Z1 }) { StateLog = new List<A5StateLog>(), UseVwap = false };
        var h = new Hx(d);
        h.Lv = i => i < 400 ? new[] { new LevelVol(102.0, 0, 1, 1) } : Array.Empty<LevelVol>();
        var prev = new Seq(T0.AddDays(-1)).Flat(400, 102.0);
        h.Run(prev.Bars);
        var s = new Seq(T0).Flat(44, 102.0);
        s.Add(102.0, 103.0, 101.9, 102.8);                           // 44
        s.Add(102.8, 104.5, 102.7, 104.4);                           // 45
        s.Add(104.4, 104.4, 103.4, 103.5); s.Add(103.5, 103.6, 102.8, 102.9); s.Add(102.9, 103.0, 102.2, 102.3);
        s.Add(102.3, 102.9, 102.2, 102.8, 50);                       // 49
        foreach (var b in s.Bars) { var b2 = new BarData { Idx = 400 + b.Idx, Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol, Delta = b.Delta }; h.Step(b2); }
        Check(h.Sigs.Count == 1 && h.Sigs[0].s.Zone == "VAH_D", "VAH_D (hạng 5) và VCL (hạng 7) cùng khoảng cách 0,8 ⇒ VAH_D thắng", string.Join(";", h.Sigs.Select(x => x.s.Zone)));
        // khác khoảng cách: VAL_D = 101,6 (hàng 508 × 0,2) ⇒ cách đóng 102,5 là 0,9; VCL cách 0,5 ⇒ VCL thắng dù hạng thấp
        d = new DetectorA5(true, new FakeVcl { F = Z1 }) { StateLog = new List<A5StateLog>(), UseVwap = false };
        h = new Hx(d);
        h.Lv = i => i < 400 ? new[] { new LevelVol(101.6, 0, 1, 1) } : Array.Empty<LevelVol>();
        h.Run(new Seq(T0.AddDays(-1)).Flat(400, 101.6).Bars);
        s = new Seq(T0).Flat(44, 101.6);
        s.Add(101.6, 103.0, 101.5, 102.8); s.Add(102.8, 104.5, 102.7, 104.4);
        s.Add(104.4, 104.4, 103.4, 103.5); s.Add(103.5, 103.6, 102.8, 102.9); s.Add(102.9, 103.0, 102.2, 102.3);
        s.Add(102.3, 102.6, 102.2, 102.5, 50);
        foreach (var b in s.Bars) h.Step(new BarData { Idx = 400 + b.Idx, Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol, Delta = b.Delta });
        Check(h.Sigs.Count >= 1 && h.Sigs[0].i == 449 && h.Sigs[0].s.Zone == "VCL_1", "VCL gần hơn (0,5 so với 0,9) ⇒ VCL thắng dù hạng thấp hơn", string.Join(";", h.Sigs.Select(x => x.i + ":" + x.s.Zone)));
    }

    static IEnumerable<BarData> Cycle(ref int idx, DateTime t0, double top, int pullBars = 3)
    {
        // pullBars nến hồi nhỏ rồi 1 nến xác nhận; đỉnh nến xác nhận = top (không lập cực trị mới nếu top ≤ cực trị hiện tại)
        var l = new List<BarData>();
        for (int k = 0; k < pullBars; k++) { l.Add(new BarData { Idx = idx, Time = t0.AddMinutes(idx), O = top - 0.1, H = top - 0.1, L = top - 0.5, C = top - 0.4, Vol = 100, Delta = 10 }); idx++; }
        l.Add(new BarData { Idx = idx, Time = t0.AddMinutes(idx), O = top - 0.5, H = top, L = top - 0.55, C = top - 0.05, Vol = 100, Delta = 50 }); idx++;
        return l;
    }

    static void T14()
    {
        Console.WriteLine("[A5-14] Đếm ≤ 2 lệnh/(phiên, vùng, chiều); khoá mức cho VCL; v4 không bị khoá mức");
        // (a) cùng 1 eid: tín hiệu 1 ở nến 49, 2 ở 53, thứ 3 (nến 57) bị trần 2
        var h = NewHx(); h.Run(Scene().Bars);
        int idx = 50;
        for (int c = 0; c < 2; c++) h.Run(Cycle(ref idx, T0, 103.0));
        Check(h.Sigs.Count == 2 && h.Sigs[1].i == 53, "cùng 1 vùng: 2 tín hiệu (nến 49, 53); tín hiệu thứ 3 (nến 57) bị trần 2/(phiên, vùng, chiều)", string.Join(";", h.Sigs.Select(x => x.i + ":" + x.s.Zone)));
        // (b) 3 vùng VCL cùng mức: tín hiệu thứ 3 bị khoá mức dù mỗi eid mới có 1 lệnh
        var h3 = NewHx(i => new[] { (1, 101.0, 102.0), (2, 101.0, 102.0), (3, 101.0, 102.0) });
        h3.Run(Scene().Bars);                                         // tín hiệu eid 1 ở nến 49
        // nến 50 đỏ rồi nến 51 xác nhận (eid 2: PkPos vẫn 45), 52 đỏ, 53 xác nhận (eid 3), 54 đỏ, 55 xác nhận (eid 1 hồi ≥ 3?)
        var seq = new List<BarData>();
        BarData Bx(int i, double o, double hgh, double l, double c, double dlt) => new BarData { Idx = i, Time = T0.AddMinutes(i), O = o, H = hgh, L = l, C = c, Vol = 100, Delta = dlt };
        seq.Add(Bx(50, 102.8, 102.9, 102.0, 102.2, 10)); seq.Add(Bx(51, 102.2, 102.9, 102.1, 102.8, 50));
        seq.Add(Bx(52, 102.8, 102.9, 102.0, 102.2, 10)); seq.Add(Bx(53, 102.2, 102.9, 102.1, 102.8, 50));
        h3.Run(seq);
        var z = h3.Sigs.Select(x => x.i + ":" + x.s.Zone).ToList();
        Check(h3.Sigs.Count == 2 && h3.Sigs[0].s.Zone == "VCL_1" && h3.Sigs[1].s.Zone == "VCL_2" && h3.Sigs[1].i == 51, "3 vùng cùng mức: VCL_1 (nến 49), VCL_2 (nến 51); VCL_3 (nến 53) BỊ KHOÁ MỨC (đã có 2 tín hiệu quanh 102)", string.Join(";", z));
        // (c) vùng v4 KHÔNG bị khoá mức: VAH_D và VAL_D cùng giá 102 cho ≥ 3 tín hiệu cùng mức
        var d = new DetectorA5(false) { StateLog = new List<A5StateLog>(), UseVwap = false };
        var hv = new Hx(d);
        hv.Lv = i => i < 400 ? new[] { new LevelVol(102.0, 0, 1, 1) } : Array.Empty<LevelVol>();
        hv.Run(new Seq(T0.AddDays(-1)).Flat(400, 102.0).Bars);
        var s = new Seq(T0).Flat(44, 102.0);
        s.Add(102.0, 103.0, 101.9, 102.8); s.Add(102.8, 104.5, 102.7, 104.4);
        s.Add(104.4, 104.4, 103.4, 103.5); s.Add(103.5, 103.6, 102.8, 102.9); s.Add(102.9, 103.0, 102.2, 102.3);
        s.Add(102.3, 102.9, 102.2, 102.8, 50);
        int off = 400;
        foreach (var b in s.Bars) hv.Step(new BarData { Idx = off + b.Idx, Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol, Delta = b.Delta });
        int ii = 50;
        for (int c = 0; c < 4; c++) foreach (var b in Cycle(ref ii, T0, 103.0)) hv.Step(new BarData { Idx = off + b.Idx, Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol, Delta = b.Delta });
        Check(hv.Sigs.Count >= 3 && hv.Sigs.All(x => x.s.Zone == "VAH_D" || x.s.Zone == "VAL_D"), "vùng v4 (VAH_D/VAL_D cùng 102,0): ≥ 3 tín hiệu cùng mức vẫn vào (khoá mức chỉ áp cho VCL)", string.Join(";", hv.Sigs.Select(x => x.i + ":" + x.s.Zone)));
    }

    static void T15_16()
    {
        Console.WriteLine("[A5-15] Sau khi vào: cực trị đặt lại ⇒ lệnh 2 cần nhịp hồi mới ≥ 3 nến");
        var h = NewHx(); h.Run(Scene().Bars);
        var st = h.D.DebugStates().Single();
        Check(st.PkPos == 49 && Near(st.PkVal, 102.9) && Near(st.Pbmax, 0) && st.NEnt == 1, "sau tín hiệu: PkPos = 49, đỉnh = H nến vào (102,9), Pbmax = 0, NEnt = 1");
        // nến xác nhận ngay nến 51 (hồi 1 nến) ⇒ không vào
        h.Step(new BarData { Idx = 50, Time = T0.AddMinutes(50), O = 102.8, H = 102.9, L = 102.0, C = 102.2, Vol = 100, Delta = 10 });
        var s2 = h.Step(new BarData { Idx = 51, Time = T0.AddMinutes(51), O = 102.2, H = 102.9, L = 102.1, C = 102.8, Vol = 100, Delta = 50 });
        Check(s2 == null, "hồi mới chỉ 1 nến ⇒ nến xác nhận nến 51 không vào");
        Console.WriteLine("[A5-16] Hết phiên: mọi trạng thái/đếm/khoá mức về 0; nhật ký ghi 'end'");
        int before = h.D.StateLog.Count;
        h.Step(new BarData { Idx = 52, Time = T0.AddHours(5), O = 101, H = 101, L = 101, C = 101, Vol = 100, Delta = 10 });   // cách > 30 phút ⇒ phiên mới
        Check(h.D.DebugStates().Count == 0 && h.D.StateLog.Skip(before).Any(x => x.Why == "end" && x.Zone == "VCL_1" && x.NEnt == 1), "phiên mới ⇒ không còn trạng thái; nhật ký 'end' của VCL_1 (NEnt 1)", string.Join(",", h.D.StateLog.Select(x => x.Why)));
    }

    static void T17()
    {
        Console.WriteLine("[A5-17] Mở ảo: VirtualOpenBlock ⇒ không tín hiệu và KHÔNG tiêu đếm trong 19:20–20:30; sau đó có tín hiệu");
        DateTime tv = new DateTime(2026, 10, 21, 12, 40, 0, DateTimeKind.Utc);   // nến 49 = 13:29 UTC = 20:29 VN (sm 929 = còn trong khung), nến 53 = 13:33 (sm 933 > 930)
        Func<Seq> mk = () =>
        {
            var s = Scene(tv);
            s.Add(102.8, 102.9, 102.0, 102.2, 10);                   // 50
            s.Add(102.2, 102.3, 102.1, 102.2, 10);                   // 51
            s.Add(102.2, 102.3, 102.1, 102.2, 10);                   // 52
            s.Add(102.2, 102.9, 102.1, 102.8, 50);                   // 53 nến xác nhận ngoài khung
            return s;
        };
        var h = NewHx(vblock: true); h.Run(mk().Bars);
        Check(h.Z.SmAt(49) < 930 && h.Z.SmAt(49) >= 860 && h.Z.SmAt(53) >= 930, "dựng giờ đúng: nến 49 trong khung (sm " + h.Z.SmAt(49) + "), nến 53 ngoài khung (sm " + h.Z.SmAt(53) + ")");
        Check(h.Sigs.Count == 1 && h.Sigs[0].i == 53, "chặn mở ảo: nến xác nhận trong khung không ra tín hiệu; nến 53 (sau 20:30 VN) có tín hiệu", string.Join(";", h.Sigs.Select(x => x.i + ":" + x.s.Zone)));
        Check(h.D.LastInfo != null && h.D.LastInfo.EntNo == 1, "nến bị chặn KHÔNG tiêu đếm (EntNo của tín hiệu đầu vẫn là 1)", h.D.LastInfo?.EntNo.ToString());
        var h2 = NewHx(vblock: false); h2.Run(mk().Bars);
        Check(h2.Sigs.Count >= 1 && h2.Sigs[0].i == 49, "VirtualOpenBlock = false ⇒ có tín hiệu ngay trong khung (nến 49)", string.Join(";", h2.Sigs.Select(x => x.i + ":" + x.s.Zone)));
    }

    // ---------------------------------------------------------------- 18–21: không nhìn trước, nạp lại, lệnh mở, Watch
    static List<BarData> LongScene()
    {
        var s = Scene();
        for (int k = 50; k < 80; k++) s.Add(102.5, 102.6, 102.4, 102.5);
        return s.Bars;
    }

    static string WatchSig(List<A5Watch> w) => string.Join("|", w.Select(x => $"{x.Name}/{x.Side}/{Fmt(x.E)}/{x.PkPos}/{x.Label}"));

    static void T18()
    {
        Console.WriteLine("[A5-18] Không nhìn trước: chạy tới nến k = chạy cả chuỗi (tín hiệu ≤ k và Watch(k) giống hệt)");
        var all = LongScene();
        var hf = NewHx();
        var watchAt = new Dictionary<int, string>();
        foreach (var b in all)
        {
            hf.Step(b);
            if (b.Idx == 47 || b.Idx == 49 || b.Idx == 60) watchAt[b.Idx] = WatchSig(hf.D.Watch(b.Idx, b, false));
        }
        bool ok = true; string why = "";
        foreach (int k in new[] { 47, 49, 60 })
        {
            var hp = NewHx();
            try { for (int i = 0; i <= k; i++) hp.Step(all[i]); }
            catch (Exception e) { ok = false; why = e.Message; break; }
            string w = WatchSig(hp.D.Watch(k, all[k], false));
            var sp = hp.Sigs.Select(x => x.i + ":" + x.s.Entry + ":" + x.s.Sl + ":" + x.s.Tp).ToList();
            var sf = hf.Sigs.Where(x => x.i <= k).Select(x => x.i + ":" + x.s.Entry + ":" + x.s.Sl + ":" + x.s.Tp).ToList();
            if (w != watchAt[k] || !sp.SequenceEqual(sf)) { ok = false; why = $"k={k}: '{w}' vs '{watchAt[k]}'"; }
        }
        Check(ok, "cắt dữ liệu ở 47, 49, 60 ⇒ tín hiệu + Watch giống chạy cả chuỗi, không ném lỗi ClosedBars", why);
    }

    sealed class BlockerDetector : ISetupDetector
    {
        public char Setup => 'B';
        public Signal TryDetect(SetupContext ctx, int i) => i == 30 ? new Signal { Side = 1, Entry = 101, Sl = 1, Tp = 1000, Reason = "chặn", Zone = "x" } : null;
    }

    static void T19_20()
    {
        Console.WriteLine("[A5-19] Nạp lại: engine 2 cùng cache ⇒ tín hiệu và Watch giống; LogicVersion khác ⇒ bỏ cache cũ");
        string path = Path.Combine(Path.GetTempPath(), "benzo_a5_" + Guid.NewGuid().ToString("N").Substring(0, 8), "cache.jsonl");
        var bars = LongScene();
        (BenzoEngine e, DetectorA5 d) Mk(string ver)
        {
            var d = new DetectorA5(true, new FakeVcl { F = Z1 }) { UseVwap = false };
            var cache = new SignalCache(path, ver); cache.Load();
            var e = new BenzoEngine("GCZ26", 0.1, cache, new ISetupDetector[] { d }) { GetLevels = _ => Array.Empty<LevelVol>() };
            foreach (var b in bars) e.Bars.Add(b);
            e.Advance(bars.Count - 1);
            return (e, d);
        }
        var (e1, d1) = Mk(BenzoCore.LogicVersion);
        var (e2, d2) = Mk(BenzoCore.LogicVersion);
        string s1 = string.Join(";", e1.Signals.Select(x => x.Id + ":" + x.Entry + ":" + x.Sl + ":" + x.Tp));
        string s2 = string.Join(";", e2.Signals.Select(x => x.Id + ":" + x.Entry + ":" + x.Sl + ":" + x.Tp));
        Check(e1.Signals.Count >= 1 && s1 == s2, "engine 2 (cùng cache niêm phong) ra đúng danh sách tín hiệu của engine 1", s1 + " / " + s2);
        Check(WatchSig(d1.Watch(bars.Count - 1, bars.Last(), false)) == WatchSig(d2.Watch(bars.Count - 1, bars.Last(), false)), "Watch giống nhau sau nạp lại");
        var cOld = new SignalCache(path, "logic-khac"); cOld.Load();
        Check(cOld.Count == 0, "LogicVersion khác ⇒ cache cũ bị bỏ", cOld.Count.ToString());
        try { Directory.Delete(Path.GetDirectoryName(path), true); } catch { }

        Console.WriteLine("[A5-20] Có lệnh mở (engine bận): Observe vẫn tiêu đếm/khoá mức/đặt lại cực trị như chạy không engine");
        var dBusy = new DetectorA5(true, new FakeVcl { F = Z1 }) { UseVwap = false };
        var eBusy = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { new BlockerDetector(), dBusy }) { GetLevels = _ => Array.Empty<LevelVol>() };
        foreach (var b in bars) eBusy.Bars.Add(b);
        eBusy.Advance(bars.Count - 1);
        var hFree = NewHx(); hFree.Run(bars);
        string a = string.Join(";", dBusy.DebugStates().Select(x => $"{x.Name}/{x.S}/{x.P0}/{x.PkPos}/{Fmt(x.PkVal)}/{x.NEnt}/{x.Armed}"));
        string b2 = string.Join(";", hFree.D.DebugStates().Select(x => $"{x.Name}/{x.S}/{x.P0}/{x.PkPos}/{Fmt(x.PkVal)}/{x.NEnt}/{x.Armed}"));
        Check(eBusy.Signals.Count == 1 && eBusy.Signals[0].Setup == 'B' && a == b2 && a.Length > 0, "A bị lệnh B chặn (A không ra lệnh) nhưng trạng thái nội bộ (NEnt, cực trị) y hệt chạy tự do", a + " / " + b2);
    }

    static void T21()
    {
        Console.WriteLine("[A5-21] A5Text.Label + Watch: 4 trạng thái + 2 hậu tố, ẩn mục chưa trang bị/đủ 2 lệnh, tối đa 3, gần nhất trước");
        // sau nến 46: đỉnh 45 ⇒ hồi 1 nến
        var h = NewHx(); var sc = Scene();
        for (int i = 0; i <= 46; i++) h.Step(sc.Bars[i]);
        var w = h.D.Watch(46, sc.Bars[46], false);
        Check(w.Count == 1 && w[0].Label == "A chờ MUA · vùng S/R 101,0–102,0 · đỉnh 104,5 · đà vừa dừng, hồi 1/3 nến · còn 29′ · đang giờ không vào lệnh", "trạng thái 2 (hồi 1/3; nến 46 nằm 2 nến sau nến dài nhất phiên ⇒ okbar sai ⇒ có hậu tố): chuỗi mẫu", w.Count > 0 ? w[0].Label : "rỗng");
        h.Step(sc.Bars[47]); h.Step(sc.Bars[48]);
        w = h.D.Watch(48, sc.Bars[48], false);
        // trạng thái 4: near ở nến 48 (đóng 102,3) và npb = 3
        Check(w.Count == 1 && w[0].Label == "A chờ MUA · vùng S/R 101,0–102,0 · đỉnh 104,5 · giá đang ở vùng, chờ nến xác nhận · còn 27′", "trạng thái 4 (đủ vị trí, chờ nến xác nhận): chuỗi mẫu", w.Count > 0 ? w[0].Label : "rỗng");
        // hậu tố
        var w2 = h.D.Watch(48, sc.Bars[48], true);
        Check(w2[0].Label.EndsWith(" · đang có lệnh mở"), "hậu tố 'đang có lệnh mở'");
        // trạng thái 3: giá xa vùng (đỉnh 104,5, hồi chưa về) — dựng riêng: bars 46,47,48 ở trên 104 (cách E > 1, râu không chạm)
        var h3 = NewHx(); var s3 = Scene();
        for (int i = 0; i <= 45; i++) h3.Step(s3.Bars[i]);
        for (int k = 46; k <= 48; k++) h3.Step(new BarData { Idx = k, Time = T0.AddMinutes(k), O = 104.2, H = 104.3, L = 104.0, C = 104.1, Vol = 100, Delta = 10 });
        var w3 = h3.D.Watch(48, h3.Bars[48], false);
        Check(w3.Count == 1 && w3[0].Label == "A chờ MUA · vùng S/R 101,0–102,0 · đỉnh 104,5 · chờ giá hồi về vùng · còn 27′", "trạng thái 3 (chưa hồi về vùng)", w3.Count > 0 ? w3[0].Label : "rỗng");
        // trạng thái 1: nến hồi biên độ ≥ L
        var h4 = NewHx();
        for (int i = 0; i <= 45; i++) h4.Step(s3.Bars[i]);
        h4.Step(new BarData { Idx = 46, Time = T0.AddMinutes(46), O = 104.4, H = 104.4, L = 102.2, C = 102.3, Vol = 100, Delta = 10 });
        var w4 = h4.D.Watch(46, h4.Bars[46], false);
        Check(w4.Count == 1 && w4[0].Label == "A chờ MUA · vùng S/R 101,0–102,0 · đỉnh 104,5 · hồi quá mạnh, chờ đỉnh mới", "trạng thái 1 (hồi quá mạnh): không có phần 'còn …′'", w4.Count > 0 ? w4[0].Label : "rỗng");
        // hậu tố ngoài giờ: chặn mở ảo bật, nến trong khung
        var hv = NewHx(vblock: true); var sv = Scene(new DateTime(2026, 10, 21, 12, 40, 0, DateTimeKind.Utc));
        for (int i = 0; i <= 47; i++) hv.Step(sv.Bars[i]);
        var wv = hv.D.Watch(47, sv.Bars[47], false);
        Check(wv.Count == 1 && wv[0].Label.EndsWith(" · đang giờ không vào lệnh"), "hậu tố 'đang giờ không vào lệnh' khi nến cuối nằm trong khung mở ảo", wv.Count > 0 ? wv[0].Label : "rỗng");
        // chưa trang bị ⇒ ẩn
        var hu = NewHx(); var su = new Seq(T0).Flat(44, 101.0); su.Add(101, 102.6, 101, 102.5);
        hu.Run(su.Bars);
        Check(hu.D.Watch(44, su.Bars[44], false).Count == 0, "trạng thái chưa trang bị ⇒ không hiện");
        // đủ 2 lệnh ⇒ ẩn; nhiều vùng ⇒ tối đa 3, gần giá nhất trước
        var hm = NewHx(i => new[] { (1, 100.5, 101.4), (2, 100.5, 101.6), (3, 100.5, 101.8), (4, 100.5, 102.0) });
        var sm = Scene(); for (int i = 0; i <= 47; i++) hm.Step(sm.Bars[i]);
        var wm = hm.D.Watch(47, sm.Bars[47], false);
        Check(wm.Count == 3 && wm[0].Name == "VCL_4" && wm[1].Name == "VCL_3" && wm[2].Name == "VCL_2", "4 vùng đã trang bị ⇒ chỉ 3, gần giá đóng nhất trước (VCL_4, VCL_3, VCL_2)", string.Join(",", wm.Select(x => x.Name)));
        // trần 2: 2 tín hiệu cùng vùng ⇒ ẩn
        var h2s = NewHx(); h2s.Run(Scene().Bars);
        int idx = 50; h2s.Run(Cycle(ref idx, T0, 103.0));
        Check(h2s.Sigs.Count == 2 && h2s.D.Watch(h2s.Bars.Count - 1, h2s.Bars.Last(), false).Count == 0, "đủ 2 lệnh/(phiên, vùng, chiều) ⇒ không hiện nữa", "n=" + h2s.Sigs.Count);
    }

    // ---------------------------------------------------------------- 23: VclCoreSource
    static void T23()
    {
        Console.WriteLine("[A5-23] VclCoreSource: Display trùng VclCore.Display; đẩy sai thứ tự ⇒ ném lỗi; Evaluate 2 lần cùng nến ⇒ lần 2 null và không đẩy lại");
        var rnd = new Random(12345);
        double p = 4000;
        var src = new VclCoreSource();
        var chk = new VungCanhLenhNs.VclCore();
        int nonEmpty = 0, mism = 0, n = 700;
        var bars = new List<BarData>();
        for (int i = 0; i < n; i++)
        {
            double o = p; p += (rnd.NextDouble() - 0.5) * 3.0 + Math.Sin(i / 40.0) * 0.4;
            var b = new BarData { Idx = i, Time = T0.AddMinutes(i), O = o, H = Math.Max(o, p) + rnd.NextDouble(), L = Math.Min(o, p) - rnd.NextDouble(), C = p, Vol = 100 + rnd.Next(50), Delta = 10 };
            var lv = new List<LevelVol>();
            for (double q = Math.Round(b.L, 1); q <= b.H; q += 0.4) lv.Add(new LevelVol(Math.Round(q, 1), 1, 1, 2 + rnd.Next(5)));
            bars.Add(b);
            src.Push(i, b, lv);
            chk.Push(new VungCanhLenhNs.VBar { Time = b.Time, O = b.O, H = b.H, L = b.L, C = b.C, Vol = b.Vol }, lv.Select(x => new VungCanhLenhNs.VLevel(x.Price, x.Vol)).ToList());
            var a = src.Display.Select(x => (x.Id, x.Lo, x.Hi)).ToList();
            var c = chk.Display.Select(x => (x.Id, x.Lo, x.Hi)).ToList();
            if (a.Count > 0) nonEmpty++;
            if (!a.SequenceEqual(c)) mism++;
        }
        Check(mism == 0 && src.Core.Idx == n - 1, $"Display trùng VclCore.Display ở cả {n} nến ({nonEmpty} nến có vùng)", $"lệch {mism}");
        bool threw = false;
        try { src.Push(n + 5, bars[0], Array.Empty<LevelVol>()); } catch (InvalidOperationException) { threw = true; }
        Check(threw, "đẩy sai thứ tự (bỏ nến) ⇒ InvalidOperationException");
        var det = new DetectorA5(true);
        var hx = new Hx(det);
        hx.Step(new BarData { Idx = 0, Time = T0, O = 4000, H = 4001, L = 3999, C = 4000, Vol = 100, Delta = 10 });
        // gọi Observe lần 2 cùng nến 0 ⇒ Evaluate trả null và không ném lỗi, VclCore không bị đẩy lại
        var core = typeof(DetectorA5).GetField("_vcl", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(det) as VclCoreSource;
        int before = core.Core.Bars.Count;
        det.Observe(hx.Ctx, 0);
        Check(core.Core.Bars.Count == before && before == 1 && det.TryDetect(hx.Ctx, 0) == null, "Observe lần 2 cùng nến ⇒ VclCore không bị đẩy lại, không tín hiệu");
    }

    // ---------------------------------------------------------------- 22: hồi quy file 90 ngày
    static void T22()
    {
        Console.WriteLine("[A5-22] Hồi quy file 90 ngày GCZ26: A-v5 và A-v4 (số từ PARITY-A5.md)");
        string dir = FindUp("data-export/data-footprint");
        string bad = FindUp("benzo-trader/research/report/_a5_bad_bars.csv");
        string basePath = dir == null ? null : Path.Combine(dir, "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
        if (basePath == null || bad == null || !File.Exists(basePath + "_bars.csv") || !File.Exists(basePath + ".csv"))
        { Console.WriteLine("  (bỏ qua: thiếu file 90 ngày hoặc _a5_bad_bars.csv)"); return; }
        var badSet = new HashSet<DateTime>();
        foreach (var l in File.ReadLines(bad))
            if (DateTime.TryParseExact(l.Trim(), "yyyy-MM-dd HH:mm:ss", Inv, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal, out var t)) badSet.Add(t);
        var (bars, lv) = Load(basePath);
        Func<int, IReadOnlyList<LevelVol>> getLv = i => (IReadOnlyList<LevelVol>)lv[i] ?? Array.Empty<LevelVol>();
        foreach (var (tag, useVcl, nSim, nLive) in new[] { ("A-v5", true, 324, 312), ("A-v4", false, 218, 208) })
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            foreach (bool live in new[] { false, true })
            {
                var det = new DetectorA5(useVcl) { VirtualOpenBlock = live };
                var eng = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det }) { GetLevels = getLv, IsNewsBlocked = t => badSet.Contains(t.AddMinutes(-1)), VirtualOpenRule = live };
                foreach (var b in bars) eng.Bars.Add(b);
                eng.Advance(bars.Count - 1);
                int closed = eng.Signals.Count(x => x.IsClosed);
                int want = live ? nLive : nSim;
                Check(closed == want, $"{tag} {(live ? "có chặn mở ảo (bản live)" : "không chặn mở ảo")}: {want} lệnh đã đóng (= Python từng lệnh)", $"{closed}");
            }
            Console.WriteLine($"  ({tag}: {sw.Elapsed.TotalSeconds:0.0}s cho 2 lượt)");
        }
    }

    static string FindUp(string rel)
    {
        string env = Environment.GetEnvironmentVariable("A5_REPO");   // chỉ để chạy test từ ngoài cây thư mục repo
        if (!string.IsNullOrEmpty(env)) { string q = Path.Combine(env, rel); if (Directory.Exists(q) || File.Exists(q)) return q; }
        string d = AppContext.BaseDirectory;
        for (int k = 0; k < 10 && d != null; k++, d = Path.GetDirectoryName(d))
        {
            string p = Path.Combine(d, rel);
            if (Directory.Exists(p) || File.Exists(p)) return p;
        }
        return null;
    }

    static (List<BarData>, List<LevelVol>[]) Load(string basePath)
    {
        var bars = new List<BarData>(); var idxOf = new List<int>();
        using (var rd = new StreamReader(basePath + "_bars.csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cT = Array.IndexOf(h, "datetime"), cO = Array.IndexOf(h, "open"), cH = Array.IndexOf(h, "high"), cL = Array.IndexOf(h, "low"),
                cC = Array.IndexOf(h, "close"), cV = Array.IndexOf(h, "volume"), cD = Array.IndexOf(h, "delta"), cB = Array.IndexOf(h, "bid_vol"), cA = Array.IndexOf(h, "ask_vol");
            string line; int n = 0;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                var t = DateTime.ParseExact(f[cT], "yyyy-MM-dd HH:mm:ss", Inv, DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal);
                bars.Add(new BarData { Idx = n, Time = t, O = D(f[cO]), H = D(f[cH]), L = D(f[cL]), C = D(f[cC]), Vol = D(f[cV]), Delta = D(f[cD]), SellVol = D(f[cB]), BuyVol = D(f[cA]) });
                idxOf.Add(int.Parse(f[cI], Inv)); n++;
            }
        }
        var pos = new Dictionary<int, int>();
        for (int k = 0; k < idxOf.Count; k++) pos[idxOf[k]] = k;
        var lv = new List<LevelVol>[bars.Count];
        using (var rd = new StreamReader(basePath + ".csv"))
        {
            var h = rd.ReadLine().Split(',');
            int cI = Array.IndexOf(h, "bar_idx"), cP = Array.IndexOf(h, "price"), cB = Array.IndexOf(h, "bid_vol"), cA = Array.IndexOf(h, "ask_vol"), cV = Array.IndexOf(h, "volume");
            string line;
            while ((line = rd.ReadLine()) != null)
            {
                if (line.Length == 0) continue;
                var f = line.Split(',');
                if (!pos.TryGetValue(int.Parse(f[cI], Inv), out int p)) continue;
                (lv[p] ??= new List<LevelVol>()).Add(new LevelVol(D(f[cP]), D(f[cB]), D(f[cA]), D(f[cV])));
            }
        }
        return (bars, lv);
    }
    static double D(string s) => double.Parse(s, Inv);

    // ---------------------------------------------------------------- chạy tất cả
    public static (int ok, int fail) Run()
    {
        _ok = 0; _fail = 0;
        Console.WriteLine("\n===== A5: setup A Phá hồi v5 =====");
        T01_02(); T03(); T04(); T05(); T06(); T07(); T08(); T09(); T10_11(); T12(); T13(); T14(); T15_16(); T17(); T18(); T19_20(); T21(); T23(); T22();
        return (_ok, _fail);
    }
}
