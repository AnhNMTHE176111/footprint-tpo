// Test cho CellBigLogic — Ô Bid/Ask lớn (luật mô phỏng CORVEN, 2026-11-11).
using System;
using OrderFlowBubbles;

static class CellBigTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    static CellBigDecision D(double buy, double sell, double B = 10, bool has = true)
        => CellBigLogic.Decide(buy, sell, B, has, 1.5, 3, false, 0);

    public static int Run()
    {
        Console.WriteLine("[CellBig] luat o lon");
        // ngưỡng 1,5 x B = 15
        Check(D(15, 0).Hit, "bien tren: side = 1,5 x B -> no");
        Check(!D(14, 0).Hit, "bien duoi: side = 1,4 x B -> khong no");
        Check(!D(0, 14.9).Hit, "sell 14,9 < 15 -> khong no");
        Check(D(0, 15).Hit, "sell 15 -> no (xet ben ap dao, khong xet tong)");
        Check(!D(7, 7).Hit, "buy 7 / sell 7 (tong 14) khong no");
        // sàn 3
        Check(!CellBigLogic.Decide(2, 0, 1, true, 1.5, 3, false, 0).Hit, "side 2 < san 3 -> khong no du >= 1,5 B");
        Check(CellBigLogic.Decide(3, 0, 1, true, 1.5, 3, false, 0).Hit, "side 3 >= san 3 -> no");
        // chưa đủ lịch sử
        Check(!D(1000, 0, 10, false).Hit, "chua co B (<5 nen) -> khong no");
        Check(!CellBigLogic.Decide(1000, 0, 0, true, 1.5, 3, false, 0).Hit, "B = 0 -> khong no");
        // màu
        Check(D(30, 0).Side == 1, "buy troi -> xanh (+1)");
        Check(D(0, 30).Side == -1, "sell troi -> do (-1)");
        Check(D(30, 18).Side == 0, "ben yeu 18 >= 15 -> tim (0)");
        Check(D(30, 14).Side == 1, "ben yeu 14 < 15 -> van xanh");
        Check(D(14, 30).Side == -1, "sell troi, ben yeu 14 < 15 -> do");
        Check(D(25, 25).Side == 0, "hai ben bang nhau -> tim");
        // ngưỡng cố định
        Check(CellBigLogic.Decide(12, 0, 0, false, 1.5, 3, true, 10).Hit, "fixed: 12 >= 10 -> no du khong co B");
        // cỡ đơn điệu
        double prev = -1; bool mono = true;
        for (double m = 1.5; m <= 10; m += 0.25) { double s = CellBigLogic.Size(m, 1.5); if (s < prev - 1e-12) mono = false; prev = s; }
        Check(mono, "co don dieu khong giam theo ty le");
        Check(Math.Abs(CellBigLogic.Size(1.5, 1.5) - 0.45) < 1e-9, "o nguong: 45% be ngang nen");
        Check(Math.Abs(CellBigLogic.Size(6, 1.5) - 1.0) < 1e-9 && CellBigLogic.Size(20, 1.5) == 1.0, "ty le >= 6: 100%");
        Check(CellBigLogic.Size(3, 1.5) > 0.45 && CellBigLogic.Size(3, 1.5) < 1.0, "ty le 3: o giua 45%..100%");
        Check(Math.Abs(D(15, 0).SizeFrac - 0.45) < 1e-9, "Decide tra SizeFrac 0,45 o nguong");
        // MergeAdjacent (gop o lien ke)
        static string K(System.Collections.Generic.List<int> l) { l.Sort(); return string.Join(",", l); }
        var c3 = new System.Collections.Generic.List<(long, double)> { (10, 20), (11, 50), (12, 30) };
        Check(K(CellBigLogic.MergeAdjacent(c3, 1)) == "1", "cum 3 o lien nhau -> giu o lon nhat", K(CellBigLogic.MergeAdjacent(c3, 1)));
        var c2 = new System.Collections.Generic.List<(long, double)> { (10, 20), (12, 30) };
        Check(K(CellBigLogic.MergeAdjacent(c2, 1)) == "0,1", "2 o cach 2 tick, gap 1 -> giu ca hai");
        Check(K(CellBigLogic.MergeAdjacent(c3, 0)) == "0,1,2", "gap 0 -> giu het");
        var c5 = new System.Collections.Generic.List<(long, double)> { (1, 10), (2, 20), (3, 30), (4, 40), (5, 50) };
        Check(K(CellBigLogic.MergeAdjacent(c5, 1)) == "0,2,4", "chuoi 5 o side tang: NMS giu 5,3,1", K(CellBigLogic.MergeAdjacent(c5, 1)));
        Check(K(CellBigLogic.MergeAdjacent(c5, 2)) == "1,4", "chuoi 5 o gap 2: giu o 5 va o 2", K(CellBigLogic.MergeAdjacent(c5, 2)));
        var tie = new System.Collections.Generic.List<(long, double)> { (11, 30), (10, 30) };
        Check(K(CellBigLogic.MergeAdjacent(tie, 1)) == "1", "hoa side: giu o tick thap hon (tat dinh)");
        var tie2 = new System.Collections.Generic.List<(long, double)> { (10, 30), (11, 30) };
        Check(K(CellBigLogic.MergeAdjacent(tie2, 1)) == "0", "hoa side (thu tu dao): van giu tick thap hon");
        Check(CellBigLogic.MergeAdjacent(new System.Collections.Generic.List<(long, double)>(), 1).Count == 0, "rong -> rong");
        Console.WriteLine("[CellBig] gom hang (RowTicks/RowOffset)");
        // RowOf: offset 1, 2 tick/hang -> (1,2)=0, (3,4)=1, (41241,41242)=20620 ; so am: (-1,0)=-1, (-3,-2)=-2
        Check(CellBigLogic.RowOf(41241, 2, 1) == CellBigLogic.RowOf(41242, 2, 1), "offset 1: tick le 41241 + chan 41242 cung hang");
        Check(CellBigLogic.RowOf(41242, 2, 1) != CellBigLogic.RowOf(41243, 2, 1), "offset 1: 41242 va 41243 khac hang");
        Check(CellBigLogic.RowOf(1, 2, 1) == 0 && CellBigLogic.RowOf(2, 2, 1) == 0 && CellBigLogic.RowOf(3, 2, 1) == 1, "offset 1: (1,2)=0, 3=1");
        Check(CellBigLogic.RowOf(-1, 2, 1) == -1 && CellBigLogic.RowOf(0, 2, 1) == -1 && CellBigLogic.RowOf(-2, 2, 1) == -2 && CellBigLogic.RowOf(-3, 2, 1) == -2, "so am: floor chia dung", $"{CellBigLogic.RowOf(-1,2,1)},{CellBigLogic.RowOf(0,2,1)},{CellBigLogic.RowOf(-2,2,1)},{CellBigLogic.RowOf(-3,2,1)}");
        Check(CellBigLogic.RowOf(41240, 2, 0) == CellBigLogic.RowOf(41241, 2, 0) && CellBigLogic.RowOf(41241, 2, 0) != CellBigLogic.RowOf(41242, 2, 0), "offset 0: (41240,41241) cung hang");
        Check(CellBigLogic.RowOf(-1, 2, 0) == -1 && CellBigLogic.RowOf(-2, 2, 0) == -1 && CellBigLogic.RowOf(-3, 2, 0) == -2, "offset 0 so am");
        Check(CellBigLogic.RowOf(41241, 1, 0) == 41241 && CellBigLogic.RowOf(41241, 1, 1) == 41241 && CellBigLogic.RowOf(-5, 1, 1) == -5, "RowTicks 1: hang = tick, offset khong anh huong");
        Check(CellBigLogic.RowOf(10, 3, 1) == 3 && CellBigLogic.RowOf(9, 3, 1) == 2, "RowTicks 3");
        // tâm hàng
        Check(Math.Abs(CellBigLogic.RowCenterTick(CellBigLogic.RowOf(41241, 2, 1), 2, 1) - 41241.5) < 1e-9, "tam hang (41241,41242) = 41241,5 tick");
        Check(Math.Abs(CellBigLogic.RowCenterPrice(CellBigLogic.RowOf(41241, 2, 1), 2, 1, 0.1) - 4124.15) < 1e-9, "gia ve = 4124,15 cho hang 4124.1-4124.2");
        Check(Math.Abs(CellBigLogic.RowCenterTick(CellBigLogic.RowOf(-3, 2, 1), 2, 1) - (-2.5)) < 1e-9, "tam hang so am (-3,-2) = -2,5");
        Check(Math.Abs(CellBigLogic.RowCenterTick(CellBigLogic.RowOf(41241, 1, 1), 1, 1) - 41241) < 1e-9, "RowTicks 1: tam = chinh tick");
        // gom mức
        var lv = new System.Collections.Generic.List<(long, double, double, double)>
            { (41241, 3, 4, 7), (41242, 5, 1, 6), (41243, 2, 2, 4), (41245, 9, 0, 9) };
        var rws = CellBigLogic.GroupRows(lv, 2, 1);
        Check(rws.Count == 3, "gom 4 muc -> 3 hang (41241+41242, 41243, 41245)", rws.Count.ToString());
        Check(rws[0].Buy == 8 && rws[0].Sell == 5 && rws[0].Vol == 13 && rws[0].LoTick == 41241 && rws[0].HiTick == 41242, "hang 1: buy 8 sell 5 vol 13");
        Check(rws[1].Buy == 2 && rws[1].Vol == 4 && rws[2].Buy == 9, "hang 2, 3 dung tong");
        Check(rws[0].RowId < rws[1].RowId && rws[1].RowId < rws[2].RowId, "hang xep theo RowId tang");
        var rws1 = CellBigLogic.GroupRows(lv, 1, 1);
        Check(rws1.Count == 4 && rws1[0].Buy == 3 && rws1[0].Sell == 4, "RowTicks 1: moi tick 1 hang");
        // BarRowMean
        Check(CellBigLogic.BarRowMean(rws, out double rm) && Math.Abs(rm - 26.0 / 3) < 1e-9, "BarRowMean = tong vol / so hang co vol", rm.ToString());
        var withZero = new System.Collections.Generic.List<CellBigLogic.Row> { new CellBigLogic.Row { Vol = 10 }, new CellBigLogic.Row { Vol = 0 } };
        Check(CellBigLogic.BarRowMean(withZero, out double rm2) && Math.Abs(rm2 - 10) < 1e-9, "hang vol 0 khong tinh");
        Check(!CellBigLogic.BarRowMean(new System.Collections.Generic.List<CellBigLogic.Row>(), out _), "khong hang -> khong nap");
        // ngưỡng 1,3 x B; tím khi bên yếu cũng >= 1,3 x B và >= sàn
        static CellBigDecision N(double buy, double sell, double B = 10) => CellBigLogic.Decide(buy, sell, B, true, 1.3, 3, false, 0);
        Check(N(13, 0).Hit && !N(12.9, 0).Hit, "bien 1,3 x B = 13: 13 no, 12,9 khong");
        Check(N(0, 13).Hit && N(0, 13).Side == -1, "sell 13 no, do");
        Check(!CellBigLogic.Decide(2, 0, 1, true, 1.3, 3, false, 0).Hit && CellBigLogic.Decide(3, 0, 1, true, 1.3, 3, false, 0).Hit, "san 3 van giu");
        Check(N(20, 15).Side == 0 && N(15, 20).Side == 0, "bid 20 ask 15, B=10 -> tim (ca hai >= 13)");
        Check(N(20, 12).Side == 1 && N(12, 20).Side == -1, "ben yeu 12 < 13 -> xanh/do");
        Check(N(13, 13).Side == 0 && N(13, 12.9).Side == 1, "bien ben yeu = 13 -> tim");
        Check(CellBigLogic.Decide(20, 15, 0, false, 1.3, 3, true, 15).Side == 0 && CellBigLogic.Decide(20, 14, 0, false, 1.3, 3, true, 15).Side == 1, "fixed mode: yeu >= nguong co dinh -> tim");
        Check(CellBigLogic.Decide(20, 2, 1, true, 1.3, 3, false, 0).Side == 1, "ben yeu 2 < san 3 -> khong tim (du 2 >= 1,3 x B)");
        Check(CellBigLogic.Decide(20, 2, 0, false, 1.3, 3, true, 1).Side == 1, "fixed: ben yeu < minSide -> khong tim");
        // RowTicks=1: luật theo hàng = luật theo tick (Decide trên từng mức)
        bool same = true;
        foreach (var l in lv)
        {
            var r1 = CellBigLogic.GroupRows(new[] { l }, 1, 1)[0];
            var d1 = N(r1.Buy, r1.Sell, 3); var d2 = N(l.Item2, l.Item3, 3);
            if (d1.Hit != d2.Hit || d1.Side != d2.Side) same = false;
        }
        Check(same, "RowTicks 1 cho ket qua nhu luat theo tick");

        // BarMean
        Check(CellBigLogic.BarMean(100, 20, out double m1) && Math.Abs(m1 - 5) < 1e-9, "BarMean = tong / so muc gia");
        Check(!CellBigLogic.BarMean(0, 0, out _), "nen rong -> khong nap");

        Console.WriteLine("[CellBig] baseline B");
        var bl = new CellBigBaseline(20);
        for (int i = 0; i < 4; i++) bl.Add(10);
        Check(!bl.TryGet(out _), "4 nen -> chua co B");
        bl.Add(10);
        Check(bl.TryGet(out double b5) && Math.Abs(b5 - 10) < 1e-9, "5 nen -> co B = 10");
        // nến hiện tại KHÔNG nằm trong B: B xét trước khi Add nến hiện tại
        bl.TryGet(out double before);
        bl.Add(1000);   // nen vua dong
        bl.TryGet(out double after);
        Check(Math.Abs(before - 10) < 1e-9 && after > before, "B xet nen idx chi gom cac nen truoc idx");
        // cuốn 20 nến
        var b2 = new CellBigBaseline(20);
        for (int i = 0; i < 20; i++) b2.Add(0);   // se bi day ra
        for (int i = 0; i < 20; i++) b2.Add(8);
        b2.TryGet(out double b20);
        Check(b2.Count == 20 && Math.Abs(b20 - 8) < 1e-9, "cuon dung 20 nen");
        // nến live: tính lại nhiều lần mà không Add -> B không đổi
        var b3 = new CellBigBaseline(20);
        for (int i = 0; i < 6; i++) b3.Add(5 + i);
        b3.TryGet(out double x1); for (int r = 0; r < 50; r++) CellBigLogic.Decide(20, 0, x1, true, 1.5, 3, false, 0);
        b3.TryGet(out double x2);
        Check(x1 == x2 && b3.Count == 6, "nen live tinh lai nhieu lan khong nap trung baseline");
        return _fail;
    }
}
