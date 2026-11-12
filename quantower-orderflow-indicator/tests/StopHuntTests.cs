// Test cho StopHuntLogic — stop hunt kiểu CORVEN (2026-11-12): quét cạnh range + bóng Ô lớn + fail break.
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class StopHuntTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    const double Tick = 0.1;

    // Nến mẫu: M = giữa (100,7-101,1), L = chạm đáy (100,0-100,6), T = chạm đỉnh (topLo..top)
    static (double lo, double hi) Pat(int k, double top)
        => k % 8 == 0 ? (top - 0.6, top) : k % 8 == 4 ? (100.0, 100.6) : (100.7, 101.1);

    sealed class Feed
    {
        public StopHuntDetector D;
        public int Idx;
        public long Min = 1_000_000;
        public Feed(StopHuntSettings s = null) { D = new StopHuntDetector(s ?? new StopHuntSettings(), Tick); }
        public List<StopHuntSignal> Bar(double lo, double hi, double close, params ShCell[] cells)
        {
            var r = D.OnBarClosed(Idx, hi, lo, close, Min, cells);
            Idx++; Min++;
            return r;
        }
        // n nến đi ngang mẫu (đỉnh top), bắt đầu ở vị trí k0
        public void Warm(int n, double top = 102.0, int k0 = 0)
        {
            for (int k = k0; k < k0 + n; k++) { var (lo, hi) = Pat(k, top); Bar(lo, hi, (lo + hi) / 2); }
        }
    }

    static ShCell Cell(double centre, double bid, double ask, int side = 1) => new ShCell { Centre = centre, Bid = bid, Ask = ask, Side = side };

    public static int Run()
    {
        _fail = 0;
        Console.WriteLine("[StopHunt] stop hunt CORVEN");

        // --- 1) quét đỉnh + bóng + đóng lại ngay trong nến quét ---
        var f = new Feed(); f.Warm(120);
        var r = f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18, 1));
        Check(r.Count == 1 && r[0].Top && r[0].FailIdx == 120 && r[0].SweepIdx == 120, "quet dinh + bong + dong lai trong nen quet -> 1 dau tai nen quet", r.Count.ToString());
        Check(r.Count == 1 && Math.Abs(r[0].Level - 102.0) < 1e-9 && r[0].Colour == 1 && r[0].Bid == 3 && r[0].Ask == 18, "muc = canh tren hop 102,0; mau xanh; Bid 3 Ask 18");

        // --- 2) không bóng -> không dấu ---
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.2, 101.0).Count == 0, "khong co bong -> khong dau");

        // --- 3) quét chưa đủ 1 tick ---
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.05, 101.0, Cell(102.0, 3, 18)).Count == 0, "high chi vuot 0,05 (< 1 tick) -> khong quet");
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.1, 101.0, Cell(102.0, 3, 18)).Count == 1, "high vuot dung 1 tick -> quet");

        // --- 4) dung sai bóng (tol = 3 tick) ---
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(101.75, 3, 18)).Count == 1, "bong tam 101,75 >= muc - 3 tick (101,7) -> dau");
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(101.65, 3, 18)).Count == 0, "bong tam 101,65 < 101,7 -> khong dau");
        f = new Feed(new StopHuntSettings { TolTicks = 0 }); f.Warm(120);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(101.95, 3, 18)).Count == 0, "tol = 0: bong tam 101,95 duoi muc -> khong dau");

        // --- 5) fail break trong 2 nến sau ---
        f = new Feed(); f.Warm(120);
        var a1 = f.Bar(101.4, 102.2, 102.1, Cell(102.05, 3, 18));     // quét, đóng trên mức
        var a2 = f.Bar(101.9, 102.3, 102.2);                           // vẫn trên
        var a3 = f.Bar(101.2, 102.2, 101.5);                           // đóng lại <= 102,0
        Check(a1.Count == 0 && a2.Count == 0 && a3.Count == 1 && a3[0].FailIdx == 122 && a3[0].SweepIdx == 120, "fail break o nen thu 2 sau nen quet -> dau dat o nen fail break (idx 122)");
        f = new Feed(); f.Warm(120);
        f.Bar(101.4, 102.2, 102.1, Cell(102.05, 3, 18)); f.Bar(101.9, 102.3, 102.2); f.Bar(101.9, 102.3, 102.2);
        Check(f.Bar(101.2, 102.2, 101.5).Count == 0, "fail break o nen thu 3 -> qua han, khong dau");
        f = new Feed(new StopHuntSettings { ConfirmBars = 0 }); f.Warm(120);
        f.Bar(101.4, 102.2, 102.1, Cell(102.05, 3, 18));
        Check(f.Bar(101.2, 102.2, 101.5).Count == 0, "ConfirmBars = 0: chi tinh nen quet");
        // đóng đúng bằng mức vẫn là fail break
        f = new Feed(); f.Warm(120);
        Check(f.Bar(101.4, 102.2, 102.0, Cell(102.05, 3, 18)).Count == 1, "dong cua dung bang muc (<=) -> fail break");

        // --- 6) cooldown 5 nến mỗi phía ---
        f = new Feed(); f.Warm(120);
        var c1 = f.Bar(101.4, 102.2, 101.0, Cell(102.15, 3, 18));      // dấu 1 tại idx 120
        for (int k = 121; k < 123; k++) { var (lo, hi) = Pat(k, 102.0); f.Bar(lo, hi, 101.0); }   // 121,122
        var c2 = f.Bar(101.4, 102.5, 101.0, Cell(102.4, 3, 18));       // idx 123: cách 3 nến -> bị nghỉ
        Check(c1.Count == 1 && c2.Count == 0, "cooldown: dau thu hai cach 3 nen cung phia -> bi chan", $"{c1.Count},{c2.Count}");
        f = new Feed(); f.Warm(120);
        f.Bar(101.4, 102.2, 101.0, Cell(102.15, 3, 18));
        for (int k = 121; k < 126; k++) { var (lo, hi) = Pat(k, 102.0); f.Bar(lo, hi, 101.0); }  // 121..125
        var c3 = f.Bar(101.4, 102.5, 101.0, Cell(102.4, 3, 18));       // idx 126: cách 6 nến -> được
        Check(c3.Count == 1, "cooldown: cach 6 nen -> cho phep dau moi", c3.Count.ToString());

        // --- 7) đáy (đối xứng) ---
        f = new Feed(); f.Warm(120);
        var d1 = f.Bar(99.8, 100.6, 101.0, Cell(99.95, 20, 2, -1));
        Check(d1.Count == 1 && !d1[0].Top && Math.Abs(d1[0].Level - 100.0) < 1e-9 && d1[0].Colour == -1 && d1[0].Bid == 20 && d1[0].Ask == 2, "quet day + bong do + dong lai tren muc -> dau day, muc 100,0");
        f = new Feed(); f.Warm(120);
        Check(f.Bar(99.8, 100.6, 101.0, Cell(100.45, 20, 2, -1)).Count == 0, "day: bong tam 100,45 > muc + 3 tick (100,3) -> khong dau");
        f = new Feed(); f.Warm(120);
        Check(f.Bar(99.8, 100.6, 99.9, Cell(99.95, 20, 2, -1)).Count == 0, "day: dong cua van duoi muc -> chua fail break");

        // --- 8) bóng mạnh nhất + màu tím ---
        f = new Feed(); f.Warm(120);
        var e1 = f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 10, 1), Cell(101.95, 15, 18, 0), Cell(101.85, 4, 12, 1));
        Check(e1.Count == 1 && e1[0].Colour == 0 && e1[0].Bid == 15 && e1[0].Ask == 18, "bong manh nhat (max Bid/Ask = 18) la bong tim 15 Bid 18 Ask", e1.Count > 0 ? $"{e1[0].Colour} {e1[0].Bid}/{e1[0].Ask}" : "");

        // --- 9) hộp không hợp lệ ---
        // 9a) quá cao: một nến đáy rất thấp trong 20 nến cuối -> h > 8 x trung vị
        f = new Feed(); f.Warm(110);
        f.Bar(90.0, 90.4, 90.2);   // 110
        f.Warm(9, 102.0, 111);     // 111..119
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 0, "hop qua cao (h > 8 x trung vi) -> khong co muc");
        // 9b) chỉ 1 lần chạm đỉnh trong hộp 20 nến
        var one = new StopHuntSettings { BoxSmall = 20, BoxLarge = 20 };
        f = new Feed(one);
        for (int k = 0; k < 100; k++) f.Bar(100.7, 101.1, 100.9);                       // 100 nen phang
        for (int k = 0; k < 20; k++) f.Bar(k == 5 ? 101.4 : (k == 12 ? 100.0 : 100.7), k == 5 ? 102.0 : (k == 12 ? 100.4 : 101.1), 100.9);   // 1 cham dinh, 1 cham day
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 0, "chi 1 lan cham canh tren -> khong hop le");
        f = new Feed(one);
        for (int k = 0; k < 100; k++) f.Bar(100.7, 101.1, 100.9);
        for (int k = 0; k < 20; k++) f.Bar(k == 5 || k == 12 ? 101.4 : (k == 8 || k == 16 ? 100.0 : 100.7), k == 5 || k == 12 ? 102.0 : (k == 8 || k == 16 ? 100.4 : 101.1), 100.9);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 1, "2 lan cham moi canh (cach >= 3 nen) -> hop le");
        // 9c) hai nến chạm sát nhau chỉ tính 1 cụm
        f = new Feed(one);
        for (int k = 0; k < 100; k++) f.Bar(100.7, 101.1, 100.9);
        for (int k = 0; k < 20; k++) f.Bar(k == 5 || k == 6 ? 101.4 : (k == 12 ? 100.0 : 100.7), k == 5 || k == 6 ? 102.0 : (k == 12 ? 100.4 : 101.1), 100.9);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 0, "2 nen cham ke nhau = 1 cum -> chua du 2 lan cham");
        // 9d) không liên tục về thời gian (nghỉ giữa hộp)
        f = new Feed(one); f.Warm(110);
        f.Min += 200;   // nghỉ 200 phút
        f.Warm(10, 102.0, 110);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 0, "hop 20 nen tran qua cho nghi 200 phut (> 30 phut) -> khong hop le");
        // 9e) chưa đủ 100 nến cho trung vị
        f = new Feed(); f.Warm(90);
        Check(f.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18)).Count == 0, "chua du 100 nen lich su -> khong dau");

        // --- 10) hợp hai hộp: chọn mức CAO nhất thoả bóng + fail break ---
        // 100 nến đầu: đỉnh 102,0; 20 nến cuối: đỉnh 101,6
        Feed Two() { var g = new Feed(); g.Warm(100, 102.0, 0); g.Warm(20, 101.6, 100); return g; }
        var g1 = Two();
        var u1 = g1.Bar(101.4, 102.2, 101.0, Cell(101.5, 3, 18));     // chỉ đủ cho mức 101,6 (>= 101,3), không đủ cho 102,0 (>= 101,7)
        Check(u1.Count == 1 && Math.Abs(u1[0].Level - 101.6) < 1e-9, "hop 20 (101,6) + hop 60 (102,0): bong tam 101,5 chi thoa muc 101,6", u1.Count > 0 ? u1[0].Level.ToString() : "0");
        var g2 = Two();
        var u2 = g2.Bar(101.4, 102.2, 101.0, Cell(102.05, 3, 18));
        Check(u2.Count == 1 && Math.Abs(u2[0].Level - 102.0) < 1e-9, "bong tam 102,05 thoa ca hai muc -> chi 1 dau, muc cao 102,0", u2.Count.ToString());
        var g3 = Two();
        var u3 = g3.Bar(101.4, 102.2, 101.8, Cell(102.05, 3, 18));    // đóng 101,8: <= 102,0 nhưng > 101,6
        Check(u3.Count == 1 && Math.Abs(u3[0].Level - 102.0) < 1e-9, "dong 101,8: fail break voi muc 102,0 (khong voi 101,6)");

        Console.WriteLine(_fail == 0 ? "  [StopHunt] PASS" : $"  [StopHunt] {_fail} FAIL");
        return _fail;
    }
}
