// Test CHẠY THẬT cho VclCore (biên dịch ../VclCore.cs, không cần Quantower). Chạy:
//   dotnet run --project vung-canh-lenh/tests
using System;
using System.Collections.Generic;
using System.Linq;
using VungCanhLenhNs;

static class Tests
{
    static int _fail, _ok;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 && !ok ? "  -> " + detail : ""));
        if (ok) _ok++; else _fail++;
    }
    static bool Near(double a, double b, double eps = 1e-9) => Math.Abs(a - b) < eps;

    // chuỗi nến giả lập: random walk M1, phiên 23h/ngày (nghỉ 60 phút ⇒ phiên mới), footprint 1 mức/nến
    static List<(VBar bar, VLevel[] lv)> Synthetic(int n, int seed = 7)
    {
        var rnd = new Random(seed);
        var outl = new List<(VBar, VLevel[])>();
        var t = new DateTime(2026, 8, 17, 22, 0, 0, DateTimeKind.Utc);
        double c = 4400;
        for (int i = 0; i < n; i++)
        {
            double o = c;
            c = Math.Round(o + (rnd.NextDouble() - 0.5) * 3.0, 1);
            double h = Math.Round(Math.Max(o, c) + rnd.NextDouble() * 1.0, 1), l = Math.Round(Math.Min(o, c) - rnd.NextDouble() * 1.0, 1);
            outl.Add((new VBar { Time = t, O = o, H = h, L = l, C = c, Vol = 100 }, new[] { new VLevel(c, 60), new VLevel(h, 20), new VLevel(l, 20) }));
            t = t.AddMinutes(1);
            if (t.Hour == 21 && t.Minute == 0) t = t.AddMinutes(60);    // nghỉ 21:00–22:00 UTC
        }
        return outl;
    }

    static void TestBuildZones()
    {
        Console.WriteLine("[1] Gộp / kẹp [2, 5] giá / tách khe / chồng lấn");
        Vcl.BuildZones(new[] { 100.0, 100.8, 101.6 }, 3, 1.0, 1.0, out var lab, out var lo, out var hi);
        Check(lo.Length == 1 && Near(lo[0], 99.5) && Near(hi[0], 102.1), "3 mức cách 0,8u, link 1u ⇒ 1 vùng [99,5; 102,1]", $"{lo.Length} {lo[0]} {hi[0]}");
        Vcl.BuildZones(new[] { 50.0 }, 1, 1.0, 1.0, out lab, out lo, out hi);
        Check(Near(hi[0] - lo[0], 2.0), "1 mức, u = 1 ⇒ nới tới đúng 2 giá");
        Vcl.BuildZones(new[] { 50.0 }, 1, 3.1, 1.0, out lab, out lo, out hi);
        Check(Near(hi[0] - lo[0], 3.1), "1 mức, u = 3,1 ⇒ rộng 3,1 (đệm 0,5u mỗi phía, trong [2, 5])");
        Vcl.BuildZones(new[] { 100.0 }, 1, 6.0, 1.0, out lab, out lo, out hi);
        Check(Near(lo[0], 97.5) && Near(hi[0], 102.5), "u = 6 (> 5) ⇒ kẹp trần đều về 5 giá quanh mức");
        Vcl.BuildZones(new[] { 100.0, 100.0, 100.0 }, 3, 6.0, 1.0, out lab, out lo, out hi);
        Check(lo.Length == 1 && Near(hi[0] - lo[0], 5.0) && lab.All(x => x == 0), "mức TRÙNG giá, u = 6 ⇒ không tách, 1 vùng 5 giá");
        Vcl.BuildZones(new[] { 100.0, 101.2 }, 2, 1.0, 1.0, out lab, out lo, out hi);
        Check(lo.Length == 1 && Near(lo[0], 99.0) && Near(hi[0], 102.2) && lab[0] == 0 && lab[1] == 0, "2 vùng 2 giá chồng nhau, hợp 3,2 < 4 ⇒ GỘP");
        var p = new List<double>(); for (double x = 0; x < 5; x += 0.5) p.Add(x); for (double x = 5.9; x < 10.01; x += 0.5) p.Add(x);
        Vcl.BuildZones(p.ToArray(), p.Count, 1.0, 1.0, out lab, out lo, out hi);
        Check(lo.Length >= 2 && Enumerable.Range(0, lo.Length).All(z => hi[z] - lo[z] <= 5.0 + 1e-9 && hi[z] - lo[z] >= 2.0 - 1e-9), "chuỗi dày 10 giá ⇒ tách, mọi vùng trong [2, 5]");
        var rnd = new Random(1); bool ok = true; string why = "";
        foreach (var u in new[] { 1.0, 3.1, 0.6, 4.4 })
            for (int rep = 0; rep < 200; rep++)
            {
                int n = rnd.Next(1, 40);
                var pr = Enumerable.Range(0, n).Select(_ => Math.Round(4400 + (rnd.NextDouble() - 0.5) * 60, 1)).ToArray();
                Vcl.BuildZones(pr, n, u, 1.0, out lab, out lo, out hi);
                for (int z = 0; z < lo.Length; z++)
                {
                    double w = hi[z] - lo[z];
                    if (w < 2 - 1e-9 || w > 5 + 1e-9) { ok = false; why = $"u={u} w={w}"; }
                    if (z > 0 && hi[z - 1] > lo[z] + 1e-9) { ok = false; why = "chồng lấn"; }
                }
            }
        Check(ok, "ngẫu nhiên 800 bộ mức, u = 1 / 3,1 / 0,6 / 4,4 ⇒ mọi vùng trong [2, 5] giá, không chồng", why);
    }

    // ---- lần chạm: chạy EpisodeTracker trên chuỗi nến (O,H,L,C) và một vùng [100, 102] (lân cận [98, 104])
    static (EpisodeTracker tr, List<(bool open, int dem, int n)> trace) RunEp(List<double[]> bars, int[] sessStarts = null, int zoneEnd = int.MaxValue,
                                                                               double lo = 100, double hi = 102, int gap = Vcl.EpGapBars)
    {
        var tr = new EpisodeTracker { LogEnabled = true, Gap = gap };
        var trace = new List<(bool, int, int)>();
        var ss = new HashSet<int>(sessStarts ?? Array.Empty<int>());
        for (int t = 0; t < bars.Count; t++)
        {
            var b = new VBar { O = bars[t][0], H = bars[t][1], L = bars[t][2], C = bars[t][3] };
            bool ns = t == 0 || ss.Contains(t);
            double cp = ns ? b.O : bars[t - 1][3];
            var zs = t <= zoneEnd ? new List<(int, double, double)> { (7, lo, hi) } : new List<(int, double, double)>();
            tr.Step(t, b, cp, ns, zs);
            var e = tr.State(7); var h = tr.Hist(7);
            trace.Add((e != null, e?.DemThoat ?? 0, h?.N ?? 0));
        }
        return (tr, trace);
    }
    static double[] Fl(double c) => new[] { c, c + 0.3, c - 0.3, c };
    static double[] B(double o, double h, double l, double c) => new[] { o, h, l, c };
    static List<double[]> Seq(params object[] xs)
    {
        var l = new List<double[]>();
        foreach (var x in xs) { if (x is double[] a) l.Add(a); else if (x is List<double[]> m) l.AddRange(m); }
        return l;
    }
    static List<double[]> Rep(double[] b, int k) => Enumerable.Repeat(b, k).ToList();

    static void TestEpisodes()
    {
        Console.WriteLine("[7] Lần chạm: máy trạng thái từng ca (khớp test_lan_cham.py)");
        var (t1, tr1) = RunEp(Seq(Fl(96), Fl(97), B(97, 100.3, 96.8, 99.5), Rep(Fl(100.5), 7), B(100.5, 101, 97, 97.5), Rep(Fl(97), 6)));
        var e1 = t1.Log;
        Check(e1.Count == 1 && e1[0].Vai == Vai.KhangCu && e1[0].Ket == KetCuc.Dao && e1[0].BatDau == 2 && e1[0].Chot == 15,
              "neo 8 nến rồi rơi xuống ⇒ 1 lần, kháng cự, ĐẢO, chốt nến 15 (5 nến yên)", $"{e1.Count}");
        Check(new[] { 10, 11, 12, 13, 14 }.Select(k => tr1[k].dem).SequenceEqual(new[] { 0, 1, 2, 3, 4 }) && tr1[14].open && !tr1[15].open && tr1[15].n == 1,
              "đếm thoát 0,1,2,3,4 rồi chốt ở nến thứ 5 (nến đi từ trong vùng ra vẫn là 'chạm' nhờ cầu C₋)");
        var (t2, _) = RunEp(Seq(Fl(96), B(96, 100.2, 95.8, 96.5), Rep(B(96.5, 97, 96, 96.2), 5)));
        Check(t2.Log.Count == 1 && t2.Log[0].Ket == KetCuc.Dao && t2.Log[0].Chot == 6, "râu chạm rồi đóng xa 2 giá ⇒ 1 lần ĐẢO");
        var (t3, _) = RunEp(Seq(Fl(96), B(96, 100.5, 96, 100.5), Rep(Fl(101), 3), Rep(Fl(105), 3), Rep(Fl(101), 2), B(101, 101.5, 97, 97.4), Rep(Fl(97), 6)));
        Check(t3.Log.Count == 1 && t3.Log[0].Ket == KetCuc.Dao, "phá giả (đóng trên 104 ba nến rồi quay về, rơi xuống) ⇒ 1 lần ĐẢO");
        var (t4, tr4) = RunEp(Seq(Fl(96), B(96, 100.5, 96, 100.5), Fl(101), B(101, 101, 97, 97.5), Fl(97), Fl(97), B(97, 100.1, 96.9, 97.2), Rep(Fl(97), 6)));
        Check(t4.Log.Count == 1 && tr4[5].dem == 2 && tr4[6].dem == 0, "thoát 2 nến rồi râu chạm lại nến thứ 3 ⇒ gộp vào lần cũ");
        var (t5, _) = RunEp(Seq(Fl(96), B(96, 100.2, 95.8, 96.5), Rep(Fl(96.2), 4)));
        Check(t5.Log.Count == 0 && t5.State(7) != null, "mới 4 nến yên ⇒ chưa chốt (đang chạm)");
        var (t5b, _) = RunEp(Seq(Fl(96), B(96, 100.2, 95.8, 96.5), Rep(Fl(96.2), 9)), gap: 10);
        Check(t5b.Log.Count == 0, "G = 10 ⇒ 9 nến yên chưa chốt");
        var (t6, _) = RunEp(Seq(Fl(96), B(96, 100.5, 96, 100.5), Fl(101), Fl(101), Fl(101.2)), new[] { 4 });
        Check(t6.Log.Count == 1 && t6.Log[0].Ket == KetCuc.ChuaRo && t6.Log[0].Chot == 4, "hết phiên khi đang neo ⇒ CHƯA RÕ");
        var (t6b, _) = RunEp(Seq(Fl(96), B(96, 100.5, 96, 100.5), Fl(101), B(101, 105, 101, 105), Fl(105.5), Fl(105.5), Fl(105.0)), new[] { 6 });
        Check(t6b.Log.Count == 1 && t6b.Log[0].Ket == KetCuc.Xuyen, "hết phiên khi đã thoát 2 nến lên trên ⇒ chốt theo phía thoát = XUYÊN");
        var (t6c, _) = RunEp(Seq(Fl(96), Fl(96), Fl(96), B(101, 101.5, 100.5, 101)), new[] { 3 });
        Check(t6c.State(7) != null && t6c.State(7).Vai == Vai.KhongRo, "nến đầu phiên: C₋ = O của chính nó (101 trong vùng ⇒ không rõ phía)");
        var bars7 = Seq(Fl(96), B(96, 100.5, 96, 100.5), Fl(101), B(101, 101, 97, 97.4), Fl(97), Fl(97), Fl(97), Fl(97));
        var (t7, _) = RunEp(bars7, zoneEnd: 5);
        Check(t7.Log.Count == 1 && t7.Log[0].Ket == KetCuc.Dao && t7.Log[0].Chot == 6 && t7.Hist(7) == null, "vùng rời bộ khi đã thoát ⇒ chốt theo phía; lịch sử mã đó bị xoá");
        var (t7b, _) = RunEp(bars7, zoneEnd: 2);
        Check(t7b.Log.Count == 1 && t7b.Log[0].Ket == KetCuc.ChuaRo && t7b.Log[0].Chot == 3, "vùng rời bộ khi đang neo ⇒ CHƯA RÕ");
        var (t8, _) = RunEp(Seq(Fl(101), Fl(101.2), Fl(101.1), Rep(Fl(110), 6)));
        Check(t8.Log.Count == 1 && t8.Log[0].Vai == Vai.KhongRo && t8.Log[0].Ket == KetCuc.KhongRoPhia, "vùng hiện ra trùm giá ⇒ KHÔNG RÕ PHÍA");
        var (t8b, _) = RunEp(Seq(Fl(101), Fl(101), Fl(101), Fl(90)), new[] { 3 });
        Check(t8b.Log.Count == 1 && t8b.Log[0].Ket == KetCuc.KhongRoPhia, "vai không rõ + hết phiên khi neo ⇒ vẫn KHÔNG RÕ PHÍA");
        var (t9, _) = RunEp(Seq(Fl(106), B(106, 106, 101.5, 101.5), Fl(101), B(101, 101, 97, 97.4), Rep(Fl(97), 6), B(97, 100.4, 97, 99.8), Rep(Fl(99.5), 2), Rep(Fl(95), 6)));
        Check(t9.Log.Count == 2 && t9.Log[0].Vai == Vai.HoTro && t9.Log[0].Ket == KetCuc.Xuyen && t9.Log[1].Vai == Vai.KhangCu && t9.Log[1].Ket == KetCuc.Dao
              && t9.Hist(7).N == 2 && t9.Hist(7).Dao == 1 && t9.Hist(7).Xuyen == 1,
              "hỗ trợ bị XUYÊN ⇒ lần sau tới từ dưới thành kháng cự (đổi vai), lịch sử 2 lần (đảo 1 · xuyên 1)");
        var (t10, _) = RunEp(Seq(Fl(97), B(97, 106.5, 96.9, 106), Rep(Fl(107), 5)));
        Check(t10.Log.Count == 1 && t10.Log[0].Vai == Vai.KhangCu && t10.Log[0].Ket == KetCuc.Xuyen && t10.Log[0].Chot == 6, "nến nhảy qua vùng (cầu C₋) ⇒ 1 lần XUYÊN");
    }

    static void TestTables()
    {
        Console.WriteLine("[8] Bảng lần chạm + bin rộng + pha");
        Check(Vcl.WidthBin(2.0) == 0 && Vcl.WidthBin(2.999) == 0 && Vcl.WidthBin(3.0) == 1 && Vcl.WidthBin(4.0) == 2 && Vcl.WidthBin(5.0) == 2, "bin rộng 2–3 / 3–4 / 4–5");
        Check(VclTables.Episode.GetLength(0) == 3 && VclTables.Episode.GetLength(1) == 3 && VclTables.Episode.GetLength(2) == 3 && VclTables.EpisodeAll.GetLength(0) == 3, "kích thước 3×3×3 và 3×3");
        bool sum = true;
        for (int ph = 0; ph < 3; ph++) for (int b = 0; b < 3; b++) if (VclTables.Episode[ph, b, 0] >= 0) sum &= VclTables.Episode[ph, b, 0] + VclTables.Episode[ph, b, 1] + VclTables.Episode[ph, b, 2] <= 101;
        Check(sum, "đảo + xuyên + chưa rõ ≤ 100 (phần còn lại = không rõ phía)");
        Check(VclTables.Lookup(0, 2, out int d0, out _, out _) && d0 == VclTables.EpisodeAll[2, 0], "ô thiếu mẫu (Á, 4–5) ⇒ dùng ô mọi pha");
        Check(VclTables.Lookup(2, 0, out int d1, out _, out _) && d1 == VclTables.Episode[2, 0, 0], "ô đủ mẫu dùng số của chính ô");
        Check(Vcl.PhaseOf(Vcl.SmOf(new DateTime(2026, 9, 8, 13, 35, 0, DateTimeKind.Utc), 7)) == 2, "20:35 VN (mùa hè Mỹ) ⇒ pha Mỹ");
        Check(Vcl.PhaseOf(Vcl.SmOf(new DateTime(2026, 9, 8, 3, 0, 0, DateTimeKind.Utc), 7)) == 0, "10:00 VN ⇒ pha Á");
    }

    static void TestBreak()
    {
        Console.WriteLine("[2] Chuyển vai & chết");
        int side = 1, br = 0;
        bool x = Vcl.BreakUpdate(ref side, ref br, 99.5, 100, 102, 1.0);
        Check(!x && side == 1 && br == 0, "đóng 99,5 (chưa xuyên đủ 1u dưới biên 100) ⇒ giữ vai hỗ trợ");
        x = Vcl.BreakUpdate(ref side, ref br, 98.9, 100, 102, 1.0);
        Check(x && side == -1 && br == 1, "đóng 98,9 ⇒ xuyên lần 1, hỗ trợ → kháng cự");
        x = Vcl.BreakUpdate(ref side, ref br, 103.1, 100, 102, 1.0);
        Check(x && side == 1 && br == 2, "đóng 103,1 ⇒ xuyên lần 2 (engine sẽ cho chết vì breaks ≥ 2)");
        side = 0; br = 0;
        x = Vcl.BreakUpdate(ref side, ref br, 103.5, 100, 102, 1.0);
        Check(!x && side == 1 && br == 0, "vai chưa rõ + đóng trên vùng ⇒ gán hỗ trợ, không tính là xuyên");
    }

    static void TestDNeverDies()
    {
        Console.WriteLine("[3] D (số tròn) không chết");
        var core = new VclCore();
        var t = new DateTime(2026, 8, 18, 1, 0, 0, DateTimeKind.Utc);
        for (int i = 0; i < 400; i++)
        {   // giá dao động 4395 ↔ 4425, xuyên 4410 nhiều lần
            double c = 4410 + 15 * Math.Sin(i / 7.0);
            core.Push(new VBar { Time = t.AddMinutes(i), O = c, H = c + 0.5, L = c - 0.5, C = c, Vol = 10 }, Array.Empty<VLevel>());
        }
        Check(core.HasAlive(4410, Vcl.KD) && core.HasAlive(4400, Vcl.KD) && core.HasAlive(4420, Vcl.KD), "4400/4410/4420 vẫn sống sau hàng chục lần bị xuyên");
        Check(core.AliveCount(Vcl.KB) >= 0, "engine chạy hết 400 nến không lỗi");
    }

    static void TestCorridor()
    {
        Console.WriteLine("[4] Hành lang nới 1u");
        var lo = new[] { 90.0, 94.0, 103.0, 106.0 }; var hi = lo.Select(v => v + 1.0).ToArray();
        var sel = new List<(int, char, int)> { (2, 'N', 1), (3, 'N', 1), (1, 'N', -1), (0, 'N', -1) };
        VclCore.CorridorOf(sel, lo, hi, 100, 1.0, out double bot, out double top);
        Check(Near(top, 105.0) && Near(bot, 93.0), "hành lang = [lo gần-1 dưới − 1u, hi gần-1 trên + 1u] = [93; 105]", $"{bot} {top}");
        VclCore.CorridorOf(new List<(int, char, int)> { (2, 'N', 1) }, lo, hi, 100, 1.0, out bot, out top);
        Check(Near(bot, 96.0), "thiếu vùng gần phía dưới ⇒ anchor − 4u", bot.ToString());
        // engine: giá dao động trong hành lang ⇒ không tính lại bộ
        var data = Synthetic(3000);
        var core = new VclCore();
        foreach (var (b, l) in data.Take(2000)) core.Push(b, l);
        int r0 = core.NRecalc;
        var ids0 = core.Display.Select(z => z.Id).ToList();
        double topC = double.PositiveInfinity, botC = double.NegativeInfinity;
        foreach (var z in core.Display.Where(z => z.Slot == 'N'))
        {
            if (z.Side > 0) topC = Math.Min(topC, z.Hi + core.U); else botC = Math.Max(botC, z.Lo - core.U);
        }
        var last = core.Bars[core.Bars.Count - 1];
        double mid = Math.Min(Math.Max(last.C, botC + 0.2), topC - 0.2);
        for (int k = 1; k <= 5; k++)
            core.Push(new VBar { Time = last.Time.AddMinutes(k), O = mid, H = mid + 0.05, L = mid - 0.05, C = mid, Vol = 10 }, Array.Empty<VLevel>());
        Check(core.NRecalc == r0 && core.Display.Select(z => z.Id).SequenceEqual(ids0), "5 nến đứng trong hành lang ⇒ không tính lại, bộ vùng giữ nguyên mã");
    }

    static void TestKeepNearAndAge()
    {
        Console.WriteLine("[5] KEEP khe gần + [6] tuổi tối thiểu");
        var lo = new[] { 90.0, 94.0, 103.0, 104.5, 106.0, 112.0 }; var hi = lo.Select(v => v + 1.0).ToArray();
        var sc = Enumerable.Repeat(1.0, 6).ToArray(); var d10 = new bool[6]; var el = Enumerable.Repeat(true, 6).ToArray();
        var none = new Dictionary<int, int>();
        var s1 = VclCore.FreshSelect(lo, hi, sc, d10, el, 100, 1.0, 30, none, new HashSet<int>());
        Check(s1.Where(x => x.slot == 'N' && x.side == 1).Select(x => lo[x.z]).SequenceEqual(new[] { 103.0, 104.5 }), "không KEEP ⇒ 2 gần nhất 103 / 104,5");
        var s2 = VclCore.FreshSelect(lo, hi, sc, d10, el, 100, 1.0, 30, none, new HashSet<int> { 4 });
        Check(s2.Where(x => x.slot == 'N' && x.side == 1).Select(x => lo[x.z]).OrderBy(v => v).SequenceEqual(new[] { 103.0, 106.0 }),
              "vùng cũ 106 (thứ 3 gần nhất) được giữ thay 104,5");
        var s3 = VclCore.FreshSelect(lo, hi, sc, d10, el, 100, 1.0, 30, none, new HashSet<int> { 5 });
        Check(!s3.Any(x => x.slot == 'N' && lo[x.z] == 112.0), "vùng cũ 112 ngoài top-3 ⇒ KHÔNG giữ ở khe gần");
        var el2 = (bool[])el.Clone(); el2[2] = false;
        var s4 = VclCore.FreshSelect(lo, hi, sc, d10, el2, 100, 1.0, 30, none, new HashSet<int>());
        Check(s4.Where(x => x.slot == 'N' && x.side == 1).Select(x => lo[x.z]).SequenceEqual(new[] { 104.5, 106.0 }), "vùng chưa đủ 10 nến tuổi bị bỏ qua");
        var lo5 = new[] { 99.0 }; var hi5 = new[] { 101.0 };
        var s5 = VclCore.FreshSelect(lo5, hi5, new[] { 1.0 }, new bool[1], new[] { false }, 100, 1.0, 30, none, new HashSet<int>());
        Check(s5.Count == 1 && s5[0].slot == 'K', "vùng CHỨA giá hiện ngay dù chưa đủ tuổi");
        var lo6 = new[] { 103.0, 106.0, 112.0, 115.0 }; var hi6 = lo6.Select(v => v + 2).ToArray();
        var s6 = VclCore.FreshSelect(lo6, hi6, new[] { 1, 1, 9, 1.0 }, new[] { false, false, true, false }, Enumerable.Repeat(true, 4).ToArray(), 100, 1.0, 30, none, new HashSet<int>());
        Check(s6.Any(x => x.slot == 'F' && lo6[x.z] == 115.0), "vùng chỉ có D-10$ không chiếm khe xa khi có vùng khác");
    }

    static void TestNoLookahead()
    {
        Console.WriteLine("[9] Không nhìn trước: chạy tới i rồi chạy lại từ đầu tới i ⇒ cùng bộ");
        var data = Synthetic(4200, 11);
        var full = new VclCore();
        var snap = new Dictionary<int, List<VZone>>();
        var cuts = new HashSet<int> { 900, 1381, 2777, 4100 };
        for (int i = 0; i < data.Count; i++)
        {
            full.Push(data[i].bar, data[i].lv);
            if (cuts.Contains(i)) snap[i] = full.Display.Select(z => z.Clone()).ToList();
        }
        foreach (var c in cuts)
        {
            var part = new VclCore();
            for (int i = 0; i <= c; i++) part.Push(data[i].bar, data[i].lv);
            var a = snap[c]; var b = part.Display;
            bool same = a.Count == b.Count && a.Zip(b, (x, y) => x.Id == y.Id && x.Lo == y.Lo && x.Hi == y.Hi && x.Slot == y.Slot && x.Side == y.Side
                && x.EpOpen == y.EpOpen && x.DemThoat == y.DemThoat && x.N == y.N && x.Dao == y.Dao && x.Xuyen == y.Xuyen && x.ChuaRo == y.ChuaRo).All(v => v);
            Check(same && a.Count > 0, $"nến {c}: {a.Count} vùng giống hệt (cả trạng thái lần chạm + lịch sử riêng)");
        }
    }

    static void TestValueArea()
    {
        Console.WriteLine("[10] Value Area 70% (copy kernel)");
        var pr = new[] { 1.0, 1.2, 1.4, 1.6, 1.8 }; var w = new[] { 1.0, 2, 10, 2, 1 };
        Vcl.ValueArea(pr, w, out double poc, out double vah, out double val);
        Check(Near(poc, 1.4) && Near(vah, 1.8) && Near(val, 1.4), "POC 1,4; mở 2 hàng lên trên trước khi hòa", $"{poc} {vah} {val}");
        Check(Vcl.RowOf(4430.1) == (long)Math.Round(4430.1 / 0.2, MidpointRounding.ToEven) && Near(Vcl.RowPrice(22150), 4430.0), "hàng 0,2 giá");
    }


    static bool SameSet(List<VZone> a, List<VZone> b) =>
        a.Count == b.Count && a.Zip(b, (x, y) => x.Id == y.Id && x.Lo == y.Lo && x.Hi == y.Hi && x.Slot == y.Slot && x.Side == y.Side).All(v => v);

    static void TestFeederVolumeAnalysis()
    {
        Console.WriteLine("[11] Volume Analysis tới muộn ⇒ dựng lại từ đầu có footprint");
        var data = Synthetic(3200, 5);                         // > 2 phiên (phiên nghỉ 21:00–22:00 UTC)
        int n1 = 2900;
        var f = new VclFeeder();
        f.Sync(n1, i => data[i].bar, i => data[i].lv, false, 7);       // chưa có VA: đẩy KHÔNG footprint
        Check(!f.BuiltWithLevels && f.Core.Bars.Count == n1, "chưa có VA vẫn chạy (không footprint)");
        var noLv = f.Core.Display.Select(z => z.Clone()).ToList();
        f.Sync(n1, i => data[i].bar, i => data[i].lv, true, 7);        // VA vừa xong
        Check(f.BuiltWithLevels && f.Resets == 1 && f.LastResetReason.Contains("footprint"), "VA xong ⇒ reset 1 lần, dựng lại có footprint", f.LastResetReason);
        var direct = new VclCore();
        for (int i = 0; i < n1; i++) direct.Push(data[i].bar, data[i].lv);
        Check(SameSet(f.Core.Display, direct.Display), "bộ vùng sau dựng lại = chạy thẳng có footprint từ đầu");
        var noLvCore = new VclCore(); var lvCore = new VclCore(); int diff = 0;
        for (int i = 0; i < n1; i++)
        {
            noLvCore.Push(data[i].bar, Array.Empty<VLevel>()); lvCore.Push(data[i].bar, data[i].lv);
            if (!SameSet(noLvCore.Display, lvCore.Display)) diff++;
        }
        Check(diff > 0, $"không footprint thì bộ vùng khác ở {diff}/{n1} nến (nên phải dựng lại, không đẩy tiếp được)");
        f.Sync(3100, i => data[i].bar, i => data[i].lv, true, 7);
        for (int i = n1; i < 3100; i++) direct.Push(data[i].bar, data[i].lv);
        Check(f.Resets == 1 && SameSet(f.Core.Display, direct.Display), "đẩy tiếp nến mới: không reset thêm, vẫn khớp");
    }

    static void TestFeederTimeRegression()
    {
        Console.WriteLine("[12] Dữ liệu nạp lại khác ⇒ reset");
        var a = Synthetic(2000, 3);
        var f = new VclFeeder();
        f.Sync(1500, i => a[i].bar, i => a[i].lv, true, 7);
        // nguồn mới (platform nạp lại lịch sử khác): từ nến 1490 mọi nến dời +10 phút (vẫn tăng dần theo giờ)
        var b = a.Select((x, i) => i < 1490 ? x : (bar: new VBar { Time = x.bar.Time.AddMinutes(10), O = x.bar.O, H = x.bar.H, L = x.bar.L, C = x.bar.C, Vol = x.bar.Vol }, lv: x.lv)).ToList();
        f.Sync(1700, i => b[i].bar, i => b[i].lv, true, 7);
        var fresh = new VclCore();
        for (int i = 0; i < 1700; i++) fresh.Push(b[i].bar, b[i].lv);
        Check(f.Resets == 1 && SameSet(f.Core.Display, fresh.Display), "giờ nến cuối không khớp nguồn ⇒ reset, kết quả = chạy lại từ đầu", f.LastResetReason);
        // nến mới có giờ SỚM hơn nến cuối trong lõi
        var c = a.Take(1700).Select(x => x).ToList();
        var f2 = new VclFeeder();
        f2.Sync(1600, i => c[i].bar, i => c[i].lv, true, 7);
        var early = new VBar { Time = c[1599].bar.Time.AddMinutes(-30), O = 4400, H = 4401, L = 4399, C = 4400, Vol = 1 };
        var c2 = c.Take(1600).ToList(); c2.Add((bar: early, lv: c[1600].lv));
        f2.Sync(1601, i => c2[i].bar, i => c2[i].lv, true, 7);
        Check(f2.Resets == 1 && f2.LastResetReason.Contains("sớm hơn") && f2.Core.Bars.Count == 1601, "nến mới sớm hơn nến cuối ⇒ reset và đẩy lại từ đầu", f2.LastResetReason);
        // lịch sử ngắn đi
        f2.Sync(1000, i => c[i].bar, i => c[i].lv, true, 7);
        Check(f2.Resets == 2 && f2.Core.Bars.Count == 1000, "lịch sử ngắn đi ⇒ reset");
    }

    static int Main()
    {
        TestBuildZones(); TestBreak(); TestDNeverDies(); TestCorridor(); TestKeepNearAndAge(); TestEpisodes(); TestTables(); TestNoLookahead(); TestValueArea(); TestFeederVolumeAnalysis(); TestFeederTimeRegression();
        Console.WriteLine($"\n{_ok} OK, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }
}
