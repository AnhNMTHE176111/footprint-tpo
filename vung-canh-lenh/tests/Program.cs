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
        Console.WriteLine("[1] Gộp / kẹp / tách khe / cắt chồng");
        Vcl.BuildZones(new[] { 100.0, 100.8, 101.6 }, 3, 1.0, 1.0, out var lab, out var lo, out var hi);
        Check(lo.Length == 1 && Near(lo[0], 99.5) && Near(hi[0], 102.1), "3 mức cách 0,8u, link 1u ⇒ 1 vùng [99,5; 102,1]", $"{lo.Length} {lo[0]} {hi[0]}");
        Vcl.BuildZones(new[] { 100.0, 100.8, 101.6 }, 3, 1.0, 0.7, out lab, out lo, out hi);
        Check(lo.Length == 3 && hi[0] <= lo[1] + 1e-12 && hi[1] <= lo[2] + 1e-12, "link 0,7u ⇒ 3 vùng, chồng lấn cắt ở giữa");
        Vcl.BuildZones(new[] { 50.0 }, 1, 1.0, 1.0, out lab, out lo, out hi);
        Check(Near(hi[0] - lo[0], 1.0), "1 mức ⇒ rộng đúng 1u");
        var p = new List<double>(); for (double x = 0; x < 5; x += 0.5) p.Add(x); for (double x = 5.9; x < 10.01; x += 0.5) p.Add(x);
        Vcl.BuildZones(p.ToArray(), p.Count, 1.0, 1.0, out lab, out lo, out hi);
        Check(lo.Length >= 3 && Enumerable.Range(0, lo.Length).All(z => hi[z] - lo[z] <= 4.0 + 1e-9), "chuỗi dày 10u ⇒ tách tại khe lớn nhất, mọi vùng ≤ 4u");
        Check(Enumerable.Range(0, p.Count).All(k => lo[lab[k]] - 1e-9 <= p[k] && p[k] <= hi[lab[k]] + 1e-9), "mọi mức nằm trong vùng của nó");
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

    static void TestTables()
    {
        Console.WriteLine("[7] Bảng tra: bin + kích thước");
        Check(VclTables.Bin(0) == 0 && VclTables.Bin(1.0) == 0 && VclTables.Bin(1.0001) == 1 && VclTables.Bin(4.0) == 3 && VclTables.Bin(4.01) == 4, "bin ≤1, (1,2], …, (3,4], (4,6]");
        Check(VclTables.Bin(12.0) == 6 && VclTables.Bin(12.01) == -1 && VclTables.Bin(-0.1) == -1 && VclTables.Bin(double.NaN) == -1, "bin 8–12 / > 12 / âm / NaN");
        Check(VclTables.Reach.Length == 3 && VclTables.Reach[2].GetLength(0) == 7 && VclTables.Reach[2].GetLength(1) == 4 && VclTables.Sweep.GetLength(0) == 3, "kích thước bảng 3×7×4, quét 3×3");
        bool mono = true;
        for (int ph = 0; ph < 3; ph++) for (int b = 0; b < 7; b++) for (int w = 1; w < 4; w++) mono &= VclTables.Reach[ph][b, w] >= VclTables.Reach[ph][b, w - 1];
        Check(mono, "P(chạm) không giảm theo cửa sổ 15→120");
        Check(Vcl.PhaseOf(Vcl.SmOf(new DateTime(2026, 9, 8, 13, 35, 0, DateTimeKind.Utc), 7)) == 2, "20:35 VN (mùa hè Mỹ) ⇒ pha Mỹ");
        Check(Vcl.PhaseOf(Vcl.SmOf(new DateTime(2026, 9, 8, 3, 0, 0, DateTimeKind.Utc), 7)) == 0, "10:00 VN ⇒ pha Á");
    }

    static void TestNoLookahead()
    {
        Console.WriteLine("[8] Không nhìn trước: chạy tới i rồi chạy lại từ đầu tới i ⇒ cùng bộ");
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
            bool same = a.Count == b.Count && a.Zip(b, (x, y) => x.Id == y.Id && x.Lo == y.Lo && x.Hi == y.Hi && x.Slot == y.Slot && x.Side == y.Side).All(v => v);
            Check(same && a.Count > 0, $"nến {c}: {a.Count} vùng giống hệt");
        }
    }

    static void TestValueArea()
    {
        Console.WriteLine("[9] Value Area 70% (copy kernel)");
        var pr = new[] { 1.0, 1.2, 1.4, 1.6, 1.8 }; var w = new[] { 1.0, 2, 10, 2, 1 };
        Vcl.ValueArea(pr, w, out double poc, out double vah, out double val);
        Check(Near(poc, 1.4) && Near(vah, 1.8) && Near(val, 1.4), "POC 1,4; mở 2 hàng lên trên trước khi hòa", $"{poc} {vah} {val}");
        Check(Vcl.RowOf(4430.1) == (long)Math.Round(4430.1 / 0.2, MidpointRounding.ToEven) && Near(Vcl.RowPrice(22150), 4430.0), "hàng 0,2 giá");
    }

    static int Main()
    {
        TestBuildZones(); TestBreak(); TestDNeverDies(); TestCorridor(); TestKeepNearAndAge(); TestTables(); TestNoLookahead(); TestValueArea();
        Console.WriteLine($"\n{_ok} OK, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }
}
