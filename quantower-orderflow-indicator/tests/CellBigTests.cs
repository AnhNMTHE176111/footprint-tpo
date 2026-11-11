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
        => CellBigLogic.Decide(buy, sell, B, has, 1.5, 3, 0.6, false, 0);

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
        Check(!CellBigLogic.Decide(2, 0, 1, true, 1.5, 3, 0.6, false, 0).Hit, "side 2 < san 3 -> khong no du >= 1,5 B");
        Check(CellBigLogic.Decide(3, 0, 1, true, 1.5, 3, 0.6, false, 0).Hit, "side 3 >= san 3 -> no");
        // chưa đủ lịch sử
        Check(!D(1000, 0, 10, false).Hit, "chua co B (<5 nen) -> khong no");
        Check(!CellBigLogic.Decide(1000, 0, 0, true, 1.5, 3, 0.6, false, 0).Hit, "B = 0 -> khong no");
        // màu
        Check(D(30, 0).Side == 1, "buy troi -> xanh (+1)");
        Check(D(0, 30).Side == -1, "sell troi -> do (-1)");
        Check(D(30, 18).Side == 0, "yeu/manh = 0,6 -> tim (0)");
        Check(D(30, 17).Side == 1, "yeu/manh = 0,567 -> van xanh");
        Check(D(17, 30).Side == -1, "sell troi, yeu/manh 0,567 -> do");
        Check(D(25, 25).Side == 0, "hai ben bang nhau -> tim");
        // ngưỡng cố định
        Check(CellBigLogic.Decide(12, 0, 0, false, 1.5, 3, 0.6, true, 10).Hit, "fixed: 12 >= 10 -> no du khong co B");
        // cỡ đơn điệu
        double prev = -1; bool mono = true;
        for (double m = 1.5; m <= 10; m += 0.25) { double s = CellBigLogic.Size(m, 1.5); if (s < prev - 1e-12) mono = false; prev = s; }
        Check(mono, "co don dieu khong giam theo ty le");
        Check(Math.Abs(CellBigLogic.Size(1.5, 1.5) - 0.45) < 1e-9, "o nguong: 45% be ngang nen");
        Check(Math.Abs(CellBigLogic.Size(6, 1.5) - 1.0) < 1e-9 && CellBigLogic.Size(20, 1.5) == 1.0, "ty le >= 6: 100%");
        Check(CellBigLogic.Size(3, 1.5) > 0.45 && CellBigLogic.Size(3, 1.5) < 1.0, "ty le 3: o giua 45%..100%");
        Check(Math.Abs(D(15, 0).SizeFrac - 0.45) < 1e-9, "Decide tra SizeFrac 0,45 o nguong");
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
        b3.TryGet(out double x1); for (int r = 0; r < 50; r++) CellBigLogic.Decide(20, 0, x1, true, 1.5, 3, 0.6, false, 0);
        b3.TryGet(out double x2);
        Check(x1 == x2 && b3.Count == 6, "nen live tinh lai nhieu lan khong nap trung baseline");
        return _fail;
    }
}
