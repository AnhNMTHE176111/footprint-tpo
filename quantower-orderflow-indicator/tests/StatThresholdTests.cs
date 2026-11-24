// Test cho chế độ "Không theo CORVEN (thống kê)" (2026-11-25) — đúng các ví dụ của research/stat_anomaly_2026-11-24/SPEC.md mục 8
// (chuỗi 4 nến mục 8.4 đã chạy ra như dưới bằng sa3_ref.py). Phần dấu vân tay (mục 8.6) kiểm trong tests-dll (cần lớp indicator).
using System;
using System.Collections.Generic;
using System.Linq;
using OrderFlowBubbles;

static class StatThresholdTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    static int[] Hist(IEnumerable<double> vals, out long n)
    {
        var h = new int[StatRank.Cap + 1]; n = 0;
        foreach (var v in vals) { h[StatRank.Index(v)]++; n++; }
        return h;
    }
    static IEnumerable<double> Range(int a, int b) { for (int i = a; i <= b; i++) yield return i; }

    static DateTime U(int y, int mo, int d, int h, int mi) => new DateTime(y, mo, d, h, mi, 0);
    static int Day(int y, int mo, int d) => (int)(new DateTime(y, mo, d).Ticks / TimeSpan.TicksPerDay);

    // một bên (Bid) có giá trị, bên kia 0
    static CellLevel Bid(long t, double bid) => new CellLevel(t, 0, bid, bid, 1);
    static CellLevel BA(long t, double bid, double ask) => new CellLevel(t, ask, bid, bid + ask, 1);
    static string Ticks(List<CellMark> m, int side) => string.Join(",", m.Where(x => x.Side == side).Select(x => x.Tick));

    public static int Run()
    {
        // ---------------- 8.1 hàm ngưỡng ----------------
        Console.WriteLine("[Stat] 8.1 ham nguong (gia tri lon thu K + 1, K = p x n / 10000)");
        {
            var h = Hist(Range(1, 250), out long n);
            int thr = StatRank.Threshold(h, n, 200);
            Check(thr == 245, "250 mau 1..250, 2% -> 245", $"{thr}");
            Check(Range(1, 250).Count(v => v > thr) == 5, "dung 5 gia tri vuot (246..250)");
            h = Hist(Range(1, 249), out n);
            Check(StatRank.Threshold(h, n, 200) == -1, "249 mau, 2% -> chua co nguong (-1)");
            h = Hist(Enumerable.Repeat(3.0, 240).Concat(Enumerable.Repeat(9.0, 10)), out n);
            thr = StatRank.Threshold(h, n, 200);
            Check(thr == 9, "240 x 3 + 10 x 9, 2% -> 9 (khong mau nao vuot)", $"{thr}");
            h = Hist(Range(1, 500), out n);
            Check(StatRank.Threshold(h, n, 100) == 495, "500 mau, 1% -> 495", $"{StatRank.Threshold(h, n, 100)}");
            h = Hist(Range(1, 499), out n);
            Check(StatRank.Threshold(h, n, 100) == -1, "499 mau, 1% -> -1");
            h = Hist(Range(1, 1000), out n);
            Check(StatRank.Threshold(h, n, 50) == 995, "1000 mau, 0,5% -> 995", $"{StatRank.Threshold(h, n, 50)}");
            h = Hist(Range(1, 999), out n);
            Check(StatRank.Threshold(h, n, 50) == -1, "999 mau, 0,5% -> -1");
            Check(StatRank.Index(5000) == 4095 && StatRank.Index(12.7) == 12, "chi so mang dem: 5000 -> 4095, 12,7 -> 12");
            h = Hist(Enumerable.Repeat(1.0, 244).Concat(Enumerable.Repeat(5000.0, 6)), out n);
            thr = StatRank.Threshold(h, n, 200);
            Check(thr == 4095 && Math.Floor(5000.0) > thr && !(4095 > thr), "244 x 1 + 6 x 5000 -> 4095; o 5000 vuot, o 4095 khong", $"{thr}");
        }

        // ---------------- 8.2 giờ Chicago, ngày, khung ----------------
        Console.WriteLine("[Stat] 8.2 gio Chicago, ngay giao dich, khung gio");
        var rows = new (DateTime t, int m, int off, int day, int slot, int slots)[]
        {
            (U(2026, 10, 30, 13, 30), 30, -5, Day(2026, 10, 30), 17, 48),
            (U(2026, 11, 1, 6, 59), 1, -5, Day(2026, 11, 1), 3, 48),
            (U(2026, 11, 1, 7, 0), 1, -6, Day(2026, 11, 1), 2, 48),
            (U(2026, 11, 1, 23, 0), 30, -6, Day(2026, 11, 2), 34, 48),
            (U(2026, 11, 2, 14, 30), 30, -6, Day(2026, 11, 2), 17, 48),
            (U(2026, 11, 2, 14, 0), 60, -6, Day(2026, 11, 2), 8, 24),
            (U(2027, 3, 14, 7, 59), 1, -6, Day(2027, 3, 14), 3, 48),
            (U(2027, 3, 14, 8, 0), 1, -5, Day(2027, 3, 14), 6, 48),
            (U(2026, 11, 2, 14, 0), 240, -6, Day(2026, 11, 2), 2, 6),
        };
        foreach (var r in rows)
        {
            int off = StatClock.ChicagoOffsetHours(r.t);
            var ds = StatClock.DaySlot(r.t, r.m);
            Check(off == r.off && ds.day == r.day && ds.slot == r.slot && ds.slots == r.slots,
                  $"{r.t:yyyy-MM-dd HH:mm} m={r.m}: lech {r.off}, ngay {new DateTime((long)r.day * TimeSpan.TicksPerDay):yyyy-MM-dd}, khung {r.slot}/{r.slots}",
                  $"lech {off}, ngay {new DateTime((long)ds.day * TimeSpan.TicksPerDay):yyyy-MM-dd}, khung {ds.slot}/{ds.slots}");
        }
        string Nb(int s, int n) => string.Join(",", StatClock.Neighbors(s, n));
        Check(Nb(5, 48) == "4,6", "lan can (5, 48) -> [4, 6]", Nb(5, 48));
        Check(Nb(0, 48) == "47,1", "lan can (0, 48) -> [47, 1]", Nb(0, 48));
        Check(Nb(0, 2) == "1", "lan can (0, 2) -> [1]", Nb(0, 2));
        Check(Nb(1, 2) == "0", "lan can (1, 2) -> [0]", Nb(1, 2));
        Check(Nb(0, 1) == "", "lan can (0, 1) -> []", Nb(0, 1));

        // ---------------- 8.3 chọn chấm ----------------
        Console.WriteLine("[Stat] 8.3 chon cham (mot ben, w = 4)");
        {
            var m = StatDots.Select(new List<CellLevel> { Bid(10, 12), Bid(11, 12) }, 11, 4, false);
            Check(Ticks(m, -1) == "10", "12 o tick 10 va 11 -> giu tick 10", Ticks(m, -1));
            var lv = new List<CellLevel> { Bid(0, 20), Bid(3, 15), Bid(6, 12) };
            m = StatDots.Select(lv, 11, 4, false);
            Check(Ticks(m, -1) == "0,6", "20/15/12 o tick 0/3/6 -> giu 0 va 6", Ticks(m, -1));
            m = StatDots.Select(lv, 11, 4, true);
            Check(Ticks(m, -1) == "0,3,6", "No o moi muc gia -> ca ba", Ticks(m, -1));
            m = StatDots.Select(new List<CellLevel> { Bid(0, 12) }, 12, 4, false);
            Check(m.Count == 0, "nguong 12, o dung 12 -> khong phai ung vien (phai lon hon han)");
            m = StatDots.Select(new List<CellLevel> { BA(0, 30, 31), BA(10, 0, 40) }, 11, 4, false);
            Check(m.Count == 3 && m[0].Side == 1 && m[1].Side == 1 && m[2].Side == -1 && m.All(x => x.Threshold == 11 && x.Mult == 0 && x.SizeFrac == CellBigLogic.DotSizeFrac),
                  "thu tu tra ve: xanh (tick tang) roi do; Threshold = nguong, Mult = 0");
        }

        // ---------------- 8.4 chuỗi 4 nến M30 ----------------
        Console.WriteLine("[Stat] 8.4 chuoi 4 nen M30, tick 0,1 (p = 200)");
        foreach (bool all in new[] { false, true })
        {
            var sd = new StatDots(30, 200);
            var b1 = Enumerable.Range(1, 125).Select(i => Bid(10000 + i, i)).ToList();
            var m1 = sd.Evaluate(U(2026, 11, 2, 14, 30), b1, all, out int t1, out bool f1);
            if (!all) Check(m1.Count == 0 && t1 == -1, "nen 1 (02/11 14:30): khong cham, chua co nguong", $"{m1.Count} cham, thr {t1}");
            sd.AddClosedBar(U(2026, 11, 2, 14, 30), b1);
            var m2 = sd.Evaluate(U(2026, 11, 3, 14, 30), b1, all, out int t2, out bool f2);
            if (!all) Check(m2.Count == 0 && t2 == -1 && sd.FallbackSamples == 125, "nen 2 (03/11): khong cham (1 ngay < 2; du phong 125 mau < 250)", $"{m2.Count} cham, thr {t2}, du phong {sd.FallbackSamples}");
            sd.AddClosedBar(U(2026, 11, 3, 14, 30), b1);
            var b3 = new List<CellLevel> { BA(20000, 124, 0), BA(20010, 123, 0), BA(20020, 0, 125), BA(20021, 0, 124), BA(20030, 0, 124) };
            var m3 = sd.Evaluate(U(2026, 11, 4, 14, 30), b3, all, out int t3, out bool f3);
            if (!all)
                Check(t3 == 123 && !f3 && sd.Window() == 4 && Ticks(m3, -1) == "20000" && Ticks(m3, 1) == "20020,20030",
                      "nen 3 (04/11): nguong chinh 123 -> do 20000, xanh 20020, 20030 (20021 bi gop)", $"thr {t3} du phong {f3} w {sd.Window()} do {Ticks(m3, -1)} xanh {Ticks(m3, 1)}");
            else
                Check(t3 == 123 && Ticks(m3, -1) == "20000" && Ticks(m3, 1) == "20020,20021,20030", "nen 3 bat No o moi muc gia: xanh them 20021", $"do {Ticks(m3, -1)} xanh {Ticks(m3, 1)}");
            sd.AddClosedBar(U(2026, 11, 4, 14, 30), b3);
            if (all) continue;
            var b4 = new List<CellLevel> { BA(30000, 125, 124), BA(30010, 124, 125) };
            string prev = null; bool same = true;
            for (int rep = 0; rep < 3; rep++)
            {
                var m4 = sd.Evaluate(U(2026, 11, 5, 14, 30), b4, false, out int t4, out bool f4);
                string s = $"thr {t4} du phong {f4} do {Ticks(m4, -1)} xanh {Ticks(m4, 1)}";
                if (rep == 0) Check(t4 == 124 && !f4 && Ticks(m4, -1) == "30000" && Ticks(m4, 1) == "30010", "nen 4 (05/11, dang chay): nguong chinh 124 -> do 30000, xanh 30010", s);
                if (prev != null && prev != s) same = false;
                prev = s;
            }
            Check(same, "goi lai Evaluate cho nen dang chay 3 lan khong doi ket qua (khong nop)");
        }
        {
            // nến rỗng (không ô volume > 0) bị bỏ hẳn; nến có volume nhưng Bid = Ask = 0 vẫn là một nến của hàng đợi dự phòng (0 mẫu)
            var sd = new StatDots(30, 200);
            var empty = new List<CellLevel> { new CellLevel(5, 0, 0, 0, 0) };
            Check(sd.Evaluate(U(2026, 11, 2, 14, 30), empty, false, out int te, out _).Count == 0 && te == -1, "nen rong: khong xet");
            sd.AddClosedBar(U(2026, 11, 2, 14, 30), empty);
            Check(sd.FallbackSamples == 0, "nen rong: khong nop");
        }
        {
            // dự phòng: M1 -> n = max(5, 120) = 120 nến; 250 mẫu trong 120 nến -> có ngưỡng dự phòng
            var sd = new StatDots(1, 200);
            Check(sd.FallbackBars == 120, "M1: hang doi du phong 120 nen", $"{sd.FallbackBars}");
            var t0 = U(2026, 11, 2, 14, 0);
            for (int i = 0; i < 125; i++) sd.AddClosedBar(t0.AddMinutes(i), new List<CellLevel> { BA(100, 1 + (i % 3), 2) });
            Check(sd.FallbackSamples == 240, "125 nen x 2 mau -> giu 120 nen = 240 mau (nen cu roi hang doi bi tru)", $"{sd.FallbackSamples}");
            Check(!sd.TryThreshold(t0.AddMinutes(125), out _, out _), "240 mau < 250 -> chua co nguong");
            sd.AddClosedBar(t0.AddMinutes(125), new List<CellLevel> { BA(100, 1, 2), BA(101, 1, 2), BA(102, 1, 2), BA(103, 1, 2), BA(104, 1, 2), BA(105, 1, 2) });
            bool okfb = sd.TryThreshold(t0.AddMinutes(126), out int tf, out bool ff);
            Check(okfb && ff, "du 250 mau -> nguong du phong", $"thr {tf} du phong {ff}");
        }

        // ---------------- 8.5 Big Trade ----------------
        Console.WriteLine("[Stat] 8.5 Big Trade (1% lon nhat 240 phut nen co so lieu)");
        {
            var bt = new StatBigTrade(1, 100, 240);
            for (int b = 0; b < 5; b++) bt.AddClosedBar(Enumerable.Range(1 + b * 100, 100).Select(v => ((long)v, (double)v)).ToList());
            bool ok = bt.TryThreshold(out int thr);
            Check(ok && thr == 495, "500 lenh don 1..500 trong 5 nen -> nguong 495", $"{thr}");
            var cells = new List<(long tick, double mot)> { (0, 496), (10, 495) };
            var sel = BigTradeAdaptive.Select(cells, thr, 2, 0, true);
            Check(sel.Count == 1 && cells[sel[0]].mot == 496, "o 496 no, o 495 khong (lon hon han)");
            var bt2 = new StatBigTrade(1, 100, 240);
            for (int b = 0; b < 5; b++) bt2.AddClosedBar(Enumerable.Range(1 + b * 100, b == 4 ? 99 : 100).Select(v => ((long)v, (double)v)).ToList());
            Check(!bt2.TryThreshold(out _), "499 lenh don -> khong vong nao");
            Check(BigTradeAdaptive.Select(cells, 495, 2, 0, false).Count == 2, "che do cu (strict = false) giu >= nhu cu");
        }
        {
            var bt = new StatBigTrade(5, 100, 240);
            Check(bt.WindowBars == 48, "M5: cua so max(5, lam tron(240 / 5)) = 48 nen", $"{bt.WindowBars}");
            bt.AddClosedBar(Enumerable.Range(0, 20).Select(i => ((long)i * 10, 4000.0)).ToList());
            for (int b = 1; b < 48; b++) bt.AddClosedBar(Enumerable.Range(1, 11).Select(v => ((long)v * 10, (double)v)).ToList());
            bt.TryThreshold(out int thrA);
            Check(bt.Count == 48 && bt.Samples == 20 + 47 * 11 && thrA == 4000, "48 nen (nen dau 20 lenh 4000) -> nguong 4000", $"{bt.Count} nen, {bt.Samples} mau, thr {thrA}");
            bt.AddClosedBar(Enumerable.Range(1, 11).Select(v => ((long)v * 10, (double)v)).ToList());
            bt.TryThreshold(out int thrB);
            Check(bt.Count == 48 && bt.Samples == 48 * 11 && thrB == 11, "nen thu 49 nop -> nen dau roi hang doi, mang dem tru dung (nguong 11)", $"{bt.Count} nen, {bt.Samples} mau, thr {thrB}");
            bt.AddClosedBar(new List<(long, double)> { (5, 0), (6, 0) });
            Check(bt.Count == 48 && bt.Samples == 48 * 11, "nen khong co lenh don > 0: so nen va so mau khong doi");
        }
        {
            var cells = new List<(long tick, double mot)> { (0, 600), (2, 550), (5, 520) };
            var sel = BigTradeAdaptive.Select(cells, 495, 2, 0, true).Select(i => cells[i].tick).OrderBy(x => x).ToList();
            Check(string.Join(",", sel) == "0,5", "gop: 600 / 550 / 520 o tick 0 / 2 / 5, g = 2 -> giu 0 va 5", string.Join(",", sel));
            var bt = new StatBigTrade(5);
            Check(bt.MergeTicks() == 2, "g = 2 khi chua du 5 nen");
            for (int b = 0; b < 5; b++) bt.AddClosedBar(new List<(long, double)> { (0, 3), (40, 2) });
            Check(bt.MergeTicks() == 5, "bien do TB 40 tick -> g = max(2, lam tron(40 / 8)) = 5", $"{bt.MergeTicks()}");
        }

        Console.WriteLine(_fail == 0 ? "[Stat] TAT CA PASS" : $"[Stat] {_fail} FAIL");
        return _fail;
    }
}
