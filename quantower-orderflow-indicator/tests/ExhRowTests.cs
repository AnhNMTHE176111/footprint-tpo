// Test cho ExhRowGrid — kiệt sức theo HÀNG giá như chart CORVEN (2026-11-26, research/exh_2026-11-26/ref_rule.py).
// Hàng: row(tick) = floor((tick - off) / G). Có dấu khi 3 hàng sát cực trị đều <= 0,35 x rowBase, volume nến >= 0,8 x volBase, râu >= 2 hàng.
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class ExhRowTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // Nến theo tick 0..19 (G 1, off 0 cho dễ đọc); vol mỗi tick = bid + ask.
    static List<ExhLevel> Bar(Func<long, (double bid, double ask)> f, long lo = 0, long hi = 19)
    {
        var l = new List<ExhLevel>();
        for (long t = lo; t <= hi; t++) { var (b, a) = f(t); l.Add(new ExhLevel(t, b, a, b + a)); }
        return l;
    }

    public static int Run()
    {
        Console.WriteLine("\n[ExhRow] Kiet suc theo hang gia (CORVEN)");

        // hàng giá
        Check(ExhRowGrid.RowOf(4, 8, 4) == 0 && ExhRowGrid.RowOf(11, 8, 4) == 0 && ExhRowGrid.RowOf(12, 8, 4) == 1 && ExhRowGrid.RowOf(3, 8, 4) == -1,
              "NQ: tick 4..11 = hang 0, 12 = hang 1, 3 = hang -1 (lam tron xuong)");
        Check(ExhRowGrid.RowOf(1, 2, 1) == 0 && ExhRowGrid.RowOf(2, 2, 1) == 0 && ExhRowGrid.RowOf(3, 2, 1) == 1 && ExhRowGrid.RowOf(0, 2, 1) == -1,
              "GC: tick 1-2 = hang 0, 3 = hang 1, 0 = hang -1");
        Check(ExhRowGrid.For("NQZ26") == (8, 4) && ExhRowGrid.For("/MNQ:XCME") == (8, 4), "NQ/MNQ -> (8, 4)");
        Check(ExhRowGrid.For("GCZ26") == (2, 1) && ExhRowGrid.For("/GC:XCEC") == (2, 1) && ExhRowGrid.For("MGCZ6") == (2, 1), "GC/MGC -> (2, 1)");
        Check(ExhRowGrid.For("ESZ26") == (1, 0) && ExhRowGrid.For(null) == (1, 0) && ExhRowGrid.For("GCX") == (1, 0), "ma khac / rong / sai -> (1, 0)");

        // BarStats: 2 hàng có volume (tick 1-2, 3) với G 2 off 1 -> TB mỗi hàng = tổng / 2
        var lv = new List<ExhLevel> { new ExhLevel(1, 1, 1, 2), new ExhLevel(2, 2, 2, 4), new ExhLevel(3, 3, 3, 6), new ExhLevel(5, 0, 0, 0) };
        Check(ExhRowGrid.BarStats(lv, 2, 1, out var m, out var tot) && tot == 12 && m == 6, "BarStats: 3 o -> 2 hang, tong 12, TB 6 (o vol 0 bo qua)", $"{m},{tot}");
        Check(!ExhRowGrid.BarStats(new List<ExhLevel> { new ExhLevel(1, 0, 0, 0) }, 2, 1, out _, out _), "nen khong giao dich -> false");

        // Nến đỉnh 19, đáy 0, thân 5..14 (o 5, c 14): râu trên 5 hàng, râu dưới 5 hàng. Ask 3 tick trên cùng = 1, Bid 3 tick dưới cùng = 1, còn lại 20.
        Func<long, (double, double)> f = t => (t <= 2 ? 1 : 20, t >= 17 ? 1 : 20);
        var bar = Bar(f);
        double rowBase = 10, volBase = 100;   // 0,35 x 10 = 3,5
        var r = ExhRowGrid.Detect(5, 19, 0, 14, bar, 1, 0, true, rowBase, volBase);
        Check(r.top && r.bot, "3 hang sat dinh/day deu 1 <= 3,5 -> co ca hai");
        Check(ExhRowGrid.Detect(5, 19, 0, 14, bar, 1, 0, false, rowBase, volBase) == (false, false), "chua du nen -> khong");
        var big = Bar(t => (t <= 2 ? 1 : 20, t == 18 ? 4 : t >= 17 ? 1 : 20));
        Check(!ExhRowGrid.Detect(5, 19, 0, 14, big, 1, 0, true, rowBase, volBase).top, "mot hang trong 3 hang = 4 > 3,5 -> khong co dinh");
        Check(ExhRowGrid.Detect(5, 19, 0, 14, bar, 1, 0, true, rowBase, 1e9) == (false, false), "volume nen < 0,8 x volBase -> khong");
        Check(!ExhRowGrid.Detect(5, 19, 0, 18, bar, 1, 0, true, rowBase, volBase).top, "rau tren 1 hang (than toi 18) -> khong co dinh");
        Check(ExhRowGrid.Detect(5, 19, 0, 17, bar, 1, 0, true, rowBase, volBase).top, "rau tren dung 2 hang -> co dinh");
        // hàng trống trong 3 hàng sát cực trị = 0 (giá nhảy cóc)
        var gap = bar.Where(x => x.Tick != 18).ToList();
        Check(ExhRowGrid.Detect(5, 19, 0, 14, gap, 1, 0, true, rowBase, volBase).top, "hang trong (nhay coc) tinh 0 -> van co");
        // gom hàng: G 2 off 0 -> 3 hàng sát đỉnh = tick 18-19, 16-17, 14-15; Ask tick 16 = 20 -> hàng 8 = 21 > 3,5
        Check(!ExhRowGrid.Detect(5, 19, 0, 10, bar, 2, 0, true, rowBase, volBase).top, "G 2: hang 16-17 = 21, hang 14-15 = 40 > 3,5 -> khong co dinh");
        Check(ExhRowGrid.Detect(5, 19, 0, 10, bar, 2, 0, true, 120, volBase).top && !ExhRowGrid.Detect(5, 19, 0, 10, bar, 2, 0, true, 100, volBase).top, "G 2: max 3 hang = 40; rowBase 120 (lim 42) -> co, 100 (lim 35) -> khong");
        Check(ExhRowGrid.Detect(5, 5, 5, 5, bar, 1, 0, true, rowBase, volBase) == (false, false), "high = low -> khong");

        // ExhRowBaseline: cần 5 nến, giữ N gần nhất, TB đúng
        var q = new ExhRowBaseline(3);
        for (int i = 1; i <= 4; i++) q.Add(i, 10 * i);
        Check(!q.TryGet(out _, out _), "4 nen < 5 -> chua du nen (N 3 nhung can 5)");
        var q2 = new ExhRowBaseline(20);
        for (int i = 1; i <= 25; i++) q2.Add(i, 10 * i);
        Check(q2.TryGet(out var rb, out var vb) && rb == 15.5 && vb == 155, "N 20: nen 6..25 -> TB 15,5 / 155", $"{rb},{vb}");

        // ---- Big Volume theo hàng (BigVolRows) ----
        // G 2 off 1: hàng 0 = tick 1-2, hàng 1 = tick 3-4. rowBase 10 -> ngưỡng 42,5
        var bv = new List<ExhLevel> { new ExhLevel(1, 10, 20, 30), new ExhLevel(2, 5, 10, 15), new ExhLevel(3, 30, 5, 35), new ExhLevel(4, 2, 1, 3), new ExhLevel(5, 1, 1, 2) };
        var res = BigVolRows.Detect(bv, 2, 1, 5, 1, true, 10);
        Check(res.Count == 1 && res[0].Row == 0 && res[0].Vol == 45 && res[0].Side == 1 && Math.Abs(res[0].Ratio - 4.5) < 1e-12 && res[0].CentreTick == 1.5,
              "hang 0 (45 = 4,5 x nen) -> 1 vong buy (Ask 30 > Bid 15), tam tick 1,5; hang 1 (38) < 42,5 -> khong", res.Count > 0 ? $"{res[0].Row},{res[0].Vol},{res[0].Side},{res[0].CentreTick}" : "rong");
        Check(Math.Abs(res[0].SizeMult - 1.40625) < 1e-12, "co = 4,5 / 3,2 = 1,40625 x cham", $"{res[0].SizeMult}");
        var bvBig = BigVolRows.Detect(new List<ExhLevel> { new ExhLevel(8, 300, 100, 400) }, 8, 4, 8, 8, true, 10);
        Check(bvBig.Count == 1 && bvBig[0].SizeMult == 4.7 && bvBig[0].Side == -1 && bvBig[0].CentreTick == 8, "40 x nen -> co kep 4,7; Bid > Ask -> sell; tam hang 7,5..11 kep vao [low, high] = 8");
        Check(BigVolRows.Detect(bv, 2, 1, 5, 1, false, 10).Count == 0 && BigVolRows.Detect(bv, 2, 1, 5, 1, true, 0).Count == 0, "chua du nen / nen 0 -> khong");
        var eq = BigVolRows.Detect(new List<ExhLevel> { new ExhLevel(1, 25, 25, 50) }, 1, 0, 1, 1, true, 10);
        Check(eq.Count == 1 && eq[0].Side == -1, "Ask = Bid -> sell (nhu Python: buy chi khi Ask > Bid)");
        Check(BigVolRows.Detect(new List<ExhLevel> { new ExhLevel(1, 20, 22.5, 42.5) }, 1, 0, 1, 1, true, 10).Count == 1, "dung 4,25 x nen -> co (>=)");

        Console.WriteLine(_fail == 0 ? "  -> ExhRow PASS" : $"  -> ExhRow {_fail} FAIL");
        return _fail;
    }
}
