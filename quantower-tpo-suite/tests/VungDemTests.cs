// Test VÙNG ĐỆM của hộp HVN (PLAN-VUNG-MANH.md §14.5) — biên dịch đúng ../ProfileEngine.cs đang dùng build DLL.
//   [3c] ca dựng tay (§14.5b)   [3d] HvnBoxes: phần đệm được vẽ theo phía giá + dòng Telegram
//   [8] C# = Python trên 19 profile thật (vung_dem_cases.json, §14.5a)
//   [9] NQZ26 tới 25/11 — cả bộ máy (nq25_expected.json, §14.5c), ca người dùng 25/11 07:30, hợp lưu không đổi, render PNG
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text.Json;
using TpoSuite;

static partial class Tests
{
    // ------------------------------------------------------------------ [3c] ca dựng tay (§14.5b)
    // Số kỳ vọng chép từ hvn_cum2.clusters + vung_dem.add_buffers (Python) chạy trên đúng các dãy này:
    // tick 0,1, up = 10,0 (100 bước giá) ⇒ cap = 45 bước, tối thiểu 5 bước. Số là chỉ số trong dãy (bước giá 40000 + i).
    static void HvnBufferHandCases(StrongZoneParams p)
    {
        const double tick = 0.1, up = 10.0;
        List<SzHvnBox> Run(double[] w)
            => StrongZones.HvnClusters(Enumerable.Range(0, w.Length).Select(i => 40000L + i).ToArray(), w, tick, up, 10, 0.12, p);
        double Px(int i) => (40000 + i) / 10.0;
        bool One(List<SzHvnBox> r, int lo, int hi, int blo, int bhi)
            => r.Count == 1 && Near(r[0].Lo, Px(lo), 1e-9) && Near(r[0].Hi, Px(hi), 1e-9) && Near(r[0].BufLo, Px(blo), 1e-9) && Near(r[0].BufHi, Px(bhi), 1e-9);
        string Show(List<SzHvnBox> r) => string.Join(" ; ", r.Select(b => $"{b.Lo:0.0}-{b.Hi:0.0} dem {b.BufLo:0.0}-{b.BufHi:0.0}"));
        double[] Ones(int n) => Enumerable.Repeat(1.0, n).ToArray();

        Console.WriteLine("\n[3c] Vung dem hop HVN - ca dung tay (PLAN 14.5b)");
        Check(p.HvnBufFloor == 0.50 && p.HvnBufCap == 0.45 && p.HvnBufMin == 0.05 && StrongZones.HvnBufCapTicks(100, p) == 45,
              "vung dem: 3 hang 0,50 / 0,45 / 0,05; up 100 buoc -> cap 45 buoc");
        // sườn thoải đều: đệm dừng đúng ở ô cuối còn ≥ 50 % đỉnh (S[134] = 542 ≥ 528,5 > S[135] = 525; phía dưới S[62] = 539 > S[61] = 524)
        var r = Run(Cat(Ones(40), Ramp(20, 100, 61), Ramp(100, 10, 61).Skip(1).ToArray(), Ones(40)));
        Check(One(r, 76, 121, 62, 134), "vung dem: suon thoai deu -> dung o o cuoi con >= 50 % dinh (14 buoc duoi, 13 buoc tren)", Show(r));
        // sườn: thân 100 → đáy 55 (8 bước) → bướu phụ 70 (20 bước) → tụt. Hộp nới dừng ở đáy (luật không leo), đệm ôm cả bướu phụ.
        r = Run(Cat(Ones(40), Seg((30, 100), (8, 55), (20, 70)), Ones(40)));
        Check(One(r, 40, 78, 40, 95), "vung dem: day 55 % roi buou phu 70 % -> hop dung o day (hi 78), dem om ca buou phu (toi 95)", Show(r));
        // sườn phẳng dài ở 60 % đỉnh ⇒ đệm chạm trần đúng 45 bước
        r = Run(Cat(Ones(40), Seg((30, 100), (120, 60)), Ones(40)));
        Check(One(r, 41, 86, 41, 131) && Near(r[0].BufHi - r[0].Hi, 4.5, 1e-9), "vung dem: suon phang dai 60 % -> dung o tran cap = 45 buoc", Show(r));
        // sườn dốc đứng: chỉ 3 bước (do làm mượt) còn ≥ 50 % < tối thiểu 5 ⇒ không có đệm cả hai phía
        r = Run(Seg((40, 1), (60, 100), (40, 1)));
        Check(One(r, 43, 96, 43, 96), "vung dem: suon doc dung -> BufLo = Lo, BufHi = Hi", Show(r));
        // kệ 52 % sau thân rộng: đệm thô 4 bước (0,04 up) ⇒ bỏ; 5 bước (đúng 0,05 up) ⇒ giữ; 6 bước (0,06 up) ⇒ giữ
        r = Run(Seg((40, 1), (60, 100), (3, 52), (40, 1)));
        Check(One(r, 43, 97, 43, 97), "vung dem: dem 0,04 up -> bo", Show(r));
        r = Run(Seg((40, 1), (60, 100), (7, 52), (40, 1)));
        Check(One(r, 43, 98, 43, 103), "vung dem: dem dung 0,05 up -> giu (>=)", Show(r));
        r = Run(Seg((40, 1), (60, 100), (9, 52), (40, 1)));
        Check(One(r, 43, 98, 43, 104), "vung dem: dem 0,06 up -> giu", Show(r));
        // hộp sát mép trên của profile (hi = n − 1): không tràn mảng, BufHi = Hi
        var we = Cat(Ones(40), Seg((60, 100), (3, 300)));
        r = Run(we);
        Check(One(r, 57, 102, 43, 102) && we.Length - 1 == 102, "vung dem: hop sat mep profile (hi = n-1) -> khong tran mang, BufHi = Hi", Show(r));
        // không đổi việc tìm hộp: Lo/Hi/Peak/CoreLo/CoreHi/Mass như khi tắt vùng đệm (cap → 0 ⇒ trần max(1,·) = 1 bước < tối thiểu)
        var p0 = p.Clone(); p0.HvnBufCap = 0;
        var w2 = Cat(Ones(40), Seg((30, 100), (8, 55), (20, 70)), Ones(40));
        var a = Run(w2); var b0 = StrongZones.HvnClusters(Enumerable.Range(0, w2.Length).Select(i => 40000L + i).ToArray(), w2, tick, up, 10, 0.12, p0);
        Check(a.Count == 1 && b0.Count == 1 && a[0].Lo == b0[0].Lo && a[0].Hi == b0[0].Hi && a[0].Peak == b0[0].Peak && a[0].CoreLo == b0[0].CoreLo && a[0].Mass == b0[0].Mass
              && b0[0].BufLo == b0[0].Lo && b0[0].BufHi == b0[0].Hi, "vung dem: chay sau khi tim hop -> hop khong doi; cap 0 -> khong co dem", Show(b0));
    }

    // ------------------------------------------------------------------ [3d] HvnBoxes: phần đệm được vẽ (§14.3) + chữ Telegram (§14.4)
    static void HvnBufferDisplayCases(StrongZoneParams p)
    {
        Console.WriteLine("\n[3d] Vung dem - phan duoc ve theo phia gia + dong Telegram (PLAN 14.3-14.4)");
        int n = 30;
        SzResult R()
        {
            var r = new SzResult { J = 20, U = 1.0, Highs = Enumerable.Repeat(100.5, n).ToArray(), Lows = Enumerable.Repeat(99.5, n).ToArray() };
            r.Highs[15] = 120; r.Lows[16] = 80;   // hộp End ≤ 14 đều "đã rời xa"
            r.Levels.Add(new SzLevel { Name = "hvn_d", IsHvn = true, Lo = 99, Hi = 101, Peak = 100, End = 10, Mass = 0.2, BufLo = 98, BufHi = 102.5 });
            return r;
        }
        string F(double x) => x.ToString("0.0", IC);
        string Show(List<SzHvnShown> b) => string.Join(" ; ", b.Select(x => $"{x.Lo}-{x.Hi} dem {x.BufLo}-{x.BufHi} d{x.Dist}"));
        var bx = StrongZones.HvnBoxes(R(), 105, p);
        Check(bx.Count == 1 && bx[0].BufHi == 102.5 && bx[0].BufLo == 99 && bx[0].Dist == 4, "vung dem: gia tren hop -> chi ve dem tren (BufLo = Lo); Dist van tinh tu Hi", Show(bx));
        Check(StrongZones.HvnSummaryLine(bx, F) == "Hộp HVN (cụm khối lượng, chưa kiểm định): 99.0–101.0 (HVN ngày, đệm tới 102.5)",
              "vung dem: dong Telegram 'dem toi <mep ngoai tren>'", StrongZones.HvnSummaryLine(bx, F));
        bx = StrongZones.HvnBoxes(R(), 95, p);
        Check(bx.Count == 1 && bx[0].BufLo == 98 && bx[0].BufHi == 101, "vung dem: gia duoi hop -> chi ve dem duoi", Show(bx));
        Check(StrongZones.HvnSummaryLine(bx, F).EndsWith("(HVN ngày, đệm tới 98.0)"), "vung dem: Telegram 'dem toi <mep ngoai duoi>'", StrongZones.HvnSummaryLine(bx, F));
        bx = StrongZones.HvnBoxes(R(), 100, p);
        Check(bx.Count == 1 && bx[0].BufLo == 98 && bx[0].BufHi == 102.5, "vung dem: gia trong hop -> ve ca hai phia", Show(bx));
        Check(StrongZones.HvnSummaryLine(bx, F).EndsWith("(HVN ngày, đệm 98.0–102.5)"), "vung dem: Telegram ca hai phia 'dem <duoi>-<tren>'", StrongZones.HvnSummaryLine(bx, F));
        bx = StrongZones.HvnBoxes(R(), 102, p);
        Check(bx.Count == 1 && bx[0].BufHi == 102.5 && bx[0].BufLo == 99 && bx[0].Dist == 1, "vung dem: gia nam trong dem tren -> chi dem tren, Dist = 1 (tu Hi)", Show(bx));
        bx = StrongZones.HvnBoxes(R(), 101, p);
        Check(bx.Count == 1 && bx[0].BufHi == 102.5 && bx[0].BufLo == 98, "vung dem: gia dung bang Hi -> ca hai (giá trong hop)", Show(bx));
        // bán kính vẫn đo từ Hi/Lo, không từ mép đệm: mép đệm cách 6,55 U nhưng Hi cách 8,05 U ⇒ không vẽ
        bx = StrongZones.HvnBoxes(R(), 109.05, p);
        Check(bx.Count == 0, "vung dem: ban kinh 8 U tinh tu Hi, khong tu mep dem -> khong ve", Show(bx));
        // hộp trùng (ngày + tuần): hộp được giữ dùng vùng đệm của chính nó
        var r2 = R();
        r2.Levels.Add(new SzLevel { Name = "hvn_w", IsHvn = true, Lo = 99.1, Hi = 100.9, Peak = 100, End = 9, Mass = 0.05, BufLo = 90, BufHi = 110 });
        bx = StrongZones.HvnBoxes(r2, 105, p);
        Check(bx.Count == 1 && bx[0].Name == "hvn_d" && bx[0].Label == "HVN ngày + tuần" && bx[0].BufHi == 102.5, "vung dem: hop trung ngay + tuan -> dung dem cua hop duoc giu", Show(bx));
        // mức không có đệm (NaN mặc định) ⇒ coi như = Lo/Hi, chữ Telegram như cũ
        var r3 = R(); r3.Levels[0].BufLo = double.NaN; r3.Levels[0].BufHi = double.NaN;
        bx = StrongZones.HvnBoxes(r3, 105, p);
        Check(bx.Count == 1 && bx[0].BufLo == 99 && bx[0].BufHi == 101 && StrongZones.HvnSummaryLine(bx, F).EndsWith("(HVN ngày)"),
              "vung dem: muc khong co dem -> Buf = Lo/Hi, Telegram khong them chu", Show(bx));
        // vẽ: đệm tô trước hộp, cùng màu, nửa độ đậm (14 vs 30), nét đứt mép ngoài
        Check(StrongZonePainter.HvnBufFillAlpha == 14 && StrongZonePainter.HvnFillAlpha == 30 && StrongZonePainter.HvnBufEdgeAlpha == 110,
              "vung dem: nen alpha 14 (hop 30), net dut mep ngoai alpha 110");
        try
        {
            using var bmp = new Bitmap(200, 200);
            using var g = Graphics.FromImage(bmp);
            g.Clear(Color.Black);
            using var fnt = new Font("Arial", 8);
            var box = StrongZones.HvnBoxes(R(), 105, p);
            float Y(double pr) => (float)((110 - pr) * 20);   // 110 → 0 px, 100 → 200 px
            StrongZonePainter.Paint(g, new Rectangle(0, 0, 200, 200), Y, new List<SzZone>(), Color.Green, Color.Red, Color.Gold, 0.1, fnt, box, Color.FromArgb(0xFF, 0x8F, 0x00));
            var cBuf = bmp.GetPixel(5, (int)Y(101.8));   // giữa dải đệm trên (101 → 102,5)
            var cOut = bmp.GetPixel(5, (int)Y(104));     // ngoài
            var cBox = bmp.GetPixel(5, (int)Y(100.5));   // trong hộp
            Check(cOut.R == 0 && cBuf.R > 0 && cBox.R > cBuf.R, "vung dem: render - dai dem nhat hon hop, ngoai dem khong to", $"ngoai {cOut} dem {cBuf} hop {cBox}");
        }
        catch (Exception ex) { Check(false, "vung dem: render", ex.GetType().Name + ": " + ex.Message); }
    }

    // ------------------------------------------------------------------ [8] 19 profile thật (§14.5a)
    static void VungDemFixture()
    {
        Console.WriteLine("\n[8] Vung dem - C# = Python tren 19 profile that (vung_dem_cases.json + hvn_cum2_cases.json)");
        string pc = Path.Combine(FxDir(), "hvn_cum2_cases.json"), pd = Path.Combine(FxDir(), "vung_dem_cases.json");
        if (!File.Exists(pc) || !File.Exists(pd)) { Check(false, "doc vung_dem_cases.json / hvn_cum2_cases.json", FxDir()); return; }
        var p = new StrongZoneParams();
        using var dc = JsonDocument.Parse(File.ReadAllText(pc));
        using var dd = JsonDocument.Parse(File.ReadAllText(pd));
        var pr = dd.RootElement.GetProperty("params");
        Check(Near(pr.GetProperty("BF").GetDouble(), p.HvnBufFloor, 1e-12) && Near(pr.GetProperty("BCAP").GetDouble(), p.HvnBufCap, 1e-12)
              && Near(pr.GetProperty("BMIN").GetDouble(), p.HvnBufMin, 1e-12), "thong so vung dem C# = Python (PLAN 14.1)");
        var cc = dc.RootElement.GetProperty("cases").EnumerateArray().ToList();
        var cd = dd.RootElement.GetProperty("cases").EnumerateArray().ToList();
        Check(cc.Count == 19 && cd.Count == 19, "19 ca o ca hai file", $"{cc.Count} / {cd.Count}");
        int bad = 0, nBox = 0, nUp = 0, nDn = 0; double maxPx = 0;
        var got = new Dictionary<string, List<SzHvnBox>>();
        for (int q = 0; q < Math.Min(cc.Count, cd.Count); q++)
        {
            var c = cc[q]; var e = cd[q];
            string ten = c.GetProperty("ten").GetString();
            double tick = c.GetProperty("tick").GetDouble(), up = c.GetProperty("up").GetDouble(), y = c.GetProperty("mass_min").GetDouble();
            int nb = c.GetProperty("so_nen_m30").GetInt32();
            var lv = c.GetProperty("levels").EnumerateArray().Select(a => new KeyValuePair<double, double>(a[0].GetDouble(), a[1].GetDouble())).ToList();
            var g = StrongZones.HvnClusters(lv, tick, up, nb, y, p);
            got[ten] = g;
            int cap = StrongZones.HvnBufCapTicks(up / tick, p);
            var want = e.GetProperty("clusters").EnumerateArray().ToList();
            bool ok = ten == e.GetProperty("ten").GetString() && cap == e.GetProperty("cap").GetInt32()
                      && Math.Abs(p.HvnBufMin * up / tick - e.GetProperty("min_ticks").GetDouble()) <= 1e-5 && g.Count == want.Count;
            for (int k = 0; k < want.Count && ok; k++)
            {
                var w = want[k]; var b = g[k];
                double d = new[] { Math.Abs(b.Lo - w.GetProperty("lo").GetDouble()), Math.Abs(b.Hi - w.GetProperty("hi").GetDouble()), Math.Abs(b.Peak - w.GetProperty("peak").GetDouble()),
                                   Math.Abs(b.BufLo - w.GetProperty("buf_lo").GetDouble()), Math.Abs(b.BufHi - w.GetProperty("buf_hi").GetDouble()) }.Max();
                maxPx = Math.Max(maxPx, d);
                ok &= d < tick / 2;
                nBox++; if (b.BufHi > b.Hi) nUp++; if (b.BufLo < b.Lo) nDn++;
            }
            if (!ok) bad++;
            string fmt = Math.Abs(tick - 0.1) < 1e-12 ? "0.0" : "0.00";
            Console.WriteLine($"       {ten,-28} cap {cap,3}  " + (g.Count == 0 ? "khong co hop" : string.Join(" ; ", g.Select(b =>
                $"{b.Lo.ToString(fmt, IC)}-{b.Hi.ToString(fmt, IC)} dem {(b.BufLo < b.Lo ? b.BufLo.ToString(fmt, IC) : "khong")} / {(b.BufHi > b.Hi ? b.BufHi.ToString(fmt, IC) : "khong")}")))
                + (ok ? "" : "   <-- LECH"));
        }
        Check(bad == 0 && cc.Count == 19, $"19 profile: ten, cap, min_ticks, so hop, lo/hi/peak/buf_lo/buf_hi (< tick/2; lech lon nhat {maxPx:E1})",
              $"lech {bad}; {nBox} hop, {nDn} co dem duoi, {nUp} co dem tren");
        bool Has(string ten, double lo, double hi, double blo, double bhi)
            => got.TryGetValue(ten, out var g) && g.Any(b => Near(b.Lo, lo, 1e-9) && Near(b.Hi, hi, 1e-9) && Near(b.BufLo, blo, 1e-9) && Near(b.BufHi, bhi, 1e-9));
        Check(Has("NQZ26 phiên 2026-11-20", 25538.50, 25609.75, 25538.50, 25652.25),
              "NQZ26 phien 20/11 (ca nguoi dung): hop 25538,50-25609,75 -> khong dem duoi, dem tren toi 25652,25");
        Check(Has("NQZ26 tuần 2026-11-20", 27239.25, 27299.00, 27179.50, 27316.25) && Has("NQZ26 tuần 2026-11-20", 25544.25, 25604.00, 25534.25, 25611.25),
              "NQZ26 tuan 15->20/11: 27179,50 / 27316,25 va 25534,25 / 25611,25");
        Check(Has("GCZ26 phiên 2026-10-29", 4034.5, 4040.6, 4031.4, 4043.1), "GCZ26 phien 29/10: 4034,5-4040,6 -> 4031,4 / 4043,1");
    }

    // ------------------------------------------------------------------ [9] NQZ26 tới 25/11 (§14.5c)
    static void Nq25Tests()
    {
        Console.WriteLine("\n[9] NQZ26 toi 25/11 - hop HVN + vung dem + vung manh (nq25_expected.json, gia that, tick 0,25)");
        var f = LoadFixture("nq25_", "nq25_expected.json", 0.25);
        if (f == null) { Check(false, "doc fixture nq25", FxDir()); return; }
        var root = f.Exp.RootElement;
        var p = new StrongZoneParams { SpliceJump = ZonePolicy.IsSingleContract("NQZ26") ? 0 : 20.0 * 10 * f.Tick };
        Check(p.SpliceJump == 0 && root.GetProperty("splice_jump").GetDouble() == 0 && Near(root.GetProperty("params").GetProperty("BF").GetDouble(), p.HvnBufFloor, 1e-12),
              "NQZ26 -> bo chan cho noi tat (C# va fixture Python); thong so vung dem khop");
        int n = 0, bad = 0, nHvn = 0, nShown = 0, nDrawn = 0, nBufDrawn = 0;
        var errs = new List<string>();
        var res = new Dictionary<DateTime, (int j, SzResult r, List<SzZone> sh, List<SzHvnShown> bx)>();
        foreach (var cs in root.GetProperty("cases").EnumerateArray())
        {
            n++;
            int j = cs.GetProperty("j").GetInt32();
            var r = StrongZones.Compute(Series(f, 0, j + 1, p), p);
            var sh = StrongZones.Display(r, f.C[j], p);
            var bx = StrongZones.HvnBoxes(r, f.C[j], p);
            res[f.T[j]] = (j, r, sh, bx);
            bool ok = Near(r.U, cs.GetProperty("U").GetDouble(), 1e-6) && Near(f.C[j], cs.GetProperty("now").GetDouble(), 1e-9)
                      && f.T[j] == DateTime.Parse(cs.GetProperty("time_utc").GetString(), IC);
            var hv = r.Levels.Where(x => x.IsHvn).OrderBy(x => x.Name, StringComparer.Ordinal).ThenBy(x => x.Lo).ToList();
            var he = cs.GetProperty("hvn").EnumerateArray().OrderBy(e => e.GetProperty("name").GetString(), StringComparer.Ordinal).ThenBy(e => e.GetProperty("lo").GetDouble()).ToList();
            ok &= hv.Count == he.Count;
            for (int k = 0; k < he.Count && ok; k++)
            {
                var e = he[k]; var x = hv[k]; nHvn++;
                ok &= x.Name == e.GetProperty("name").GetString() && Near(x.Lo, e.GetProperty("lo").GetDouble(), 1e-6) && Near(x.Hi, e.GetProperty("hi").GetDouble(), 1e-6)
                      && Near(x.Peak, e.GetProperty("peak").GetDouble(), 1e-6) && Math.Abs(x.Mass - e.GetProperty("mass").GetDouble()) <= 1e-6
                      && x.Src == e.GetProperty("src").GetInt32() && StrongZones.HvnOk(x, r.Highs, r.Lows, r.J, r.U, p) == e.GetProperty("ok").GetBoolean()
                      && Near(x.BufLo, e.GetProperty("buf_lo").GetDouble(), 1e-6) && Near(x.BufHi, e.GetProperty("buf_hi").GetDouble(), 1e-6);
            }
            var se = cs.GetProperty("shown").EnumerateArray().ToList();
            nShown += se.Count;
            ok &= se.Count == sh.Count;
            for (int k = 0; k < se.Count && ok; k++)
                ok &= Near(sh[k].Lo, se[k].GetProperty("lo").GetDouble(), 1e-6) && Near(sh[k].Hi, se[k].GetProperty("hi").GetDouble(), 1e-6)
                      && sh[k].Side == se[k].GetProperty("side").GetInt32() && sh[k].Color == se[k].GetProperty("color").GetString() && sh[k].Label == se[k].GetProperty("label").GetString();
            var be = cs.GetProperty("hvn_boxes").EnumerateArray().ToList();
            nDrawn += be.Count;
            ok &= be.Count == bx.Count;
            for (int k = 0; k < be.Count && ok; k++)
            {
                ok &= bx[k].Name == be[k].GetProperty("name").GetString() && Near(bx[k].Lo, be[k].GetProperty("lo").GetDouble(), 1e-6) && Near(bx[k].Hi, be[k].GetProperty("hi").GetDouble(), 1e-6)
                      && Near(bx[k].Peak, be[k].GetProperty("peak").GetDouble(), 1e-6) && Math.Abs(bx[k].Mass - be[k].GetProperty("mass").GetDouble()) <= 1e-6
                      && bx[k].Label == be[k].GetProperty("label").GetString()
                      && Near(bx[k].BufLo, be[k].GetProperty("buf_lo").GetDouble(), 1e-6) && Near(bx[k].BufHi, be[k].GetProperty("buf_hi").GetDouble(), 1e-6);
                if (bx[k].BufLo < bx[k].Lo || bx[k].BufHi > bx[k].Hi) nBufDrawn++;
            }
            if (!ok) { bad++; if (errs.Count < 5) errs.Add($"j={j} {f.T[j]:MM-dd HH:mm} U {r.U} hvn {string.Join(",", hv.Select(x => $"{x.Name} {x.Lo}-{x.Hi} [{x.BufLo}-{x.BufHi}]"))} hop {string.Join(" | ", bx.Select(b => $"{b.Lo}-{b.Hi} [{b.BufLo}-{b.BufHi}] {b.Label}"))}"); }
        }
        foreach (var e in errs) Console.WriteLine("       " + e);
        Check(n == 19 && bad == 0, $"NQ 25/11: 19 ca C# = Python (U <= 1e-6; {nHvn} muc HVN lo/hi/peak/buf_lo/buf_hi <= 1e-6, mass <= 1e-6, src/ok; {nShown} vung ve; {nDrawn} hop ve + nhan + phan dem duoc ve, {nBufDrawn} hop co ve dem)",
              $"lech {bad}/{n}");

        // ba ca ghi số (§14.5c): 07:00, 07:30, 08:00 ngày 25/11, U = 146,775
        foreach (var (hh, mm, px) in new[] { (7, 0, 25725.25), (7, 30, 25780.25), (8, 0, 25831.75) })
        {
            var t = new DateTime(2026, 11, 25, hh, mm, 0);
            if (!res.TryGetValue(t, out var c)) { Check(false, $"NQ 25/11 {hh:00}:{mm:00}: co ca trong fixture"); continue; }
            var b = c.bx;
            bool ok = Near(f.C[c.j], px, 1e-9) && Near(c.r.U, 146.775, 5e-4) && b.Count == 3
                      && Near(b[0].Lo, 25538.50, 1e-9) && Near(b[0].Hi, 25609.75, 1e-9) && b[0].Label == "HVN ngày + tuần" && Near(b[0].BufHi, 25652.25, 1e-9) && b[0].BufLo == b[0].Lo
                      && Near(b[1].Lo, 26249.50, 1e-9) && Near(b[1].Hi, 26312.75, 1e-9) && b[1].Label == "HVN ngày + tuần" && Near(b[1].BufLo, 26227.50, 1e-9) && b[1].BufHi == b[1].Hi
                      && Near(b[2].Lo, 26804.25, 1e-9) && Near(b[2].Hi, 26873.50, 1e-9) && b[2].Label == "HVN ngày + tuần" && Near(b[2].BufLo, 26767.25, 1e-9) && b[2].BufHi == b[2].Hi;
            Check(ok, $"NQ 25/11 {hh:00}:{mm:00} gia {px:0.00}: hop 25538,50-25609,75 dem tren toi 25652,25 ; 26249,50-26312,75 dem duoi tu 26227,50 ; 26804,25-26873,50 dem duoi tu 26767,25",
                  $"gia {f.C[c.j]:0.00} U {c.r.U:0.000} " + string.Join(" | ", b.Select(x => $"{x.Lo:0.00}-{x.Hi:0.00} [{x.BufLo:0.00}-{x.BufHi:0.00}] {x.Label}")));
        }
        // ca người dùng: đáy 25637,25 của nến 07:30 nằm trong vùng đệm trên, ngoài hộp
        if (res.TryGetValue(new DateTime(2026, 11, 25, 7, 30, 0), out var u))
        {
            var box = u.bx.FirstOrDefault(x => Near(x.Lo, 25538.50, 1e-9));
            double low = f.L[u.j];
            Check(box != null && Near(low, 25637.25, 1e-9) && box.Hi < low && low <= box.BufHi,
                  "NQ 25/11 07:30 (ca nguoi dung): Hi 25609,75 < day nen 25637,25 <= BufHi 25652,25", $"day {low:0.00}, hop {box?.Hi:0.00}, dem toi {box?.BufHi:0.00}");
            var line = StrongZones.HvnSummaryLine(u.bx, x => x.ToString("0.00", IC));
            Check(line != null && line.Contains("25538.50–25609.75 (HVN ngày + tuần, đệm tới 25652.25)"),
                  "NQ 25/11 07:30: dong Telegram '25538,50-25609,75 (HVN ngay + tuan, dem toi 25652,25)'", line);
        }

        // Hợp lưu KHÔNG dùng vùng đệm (§14.3): (a) sửa vùng đệm của mức trong bộ đệm thành cực rộng ⇒ cụm/nhãn/màu không đổi;
        // (b) trên dữ liệu thật: mọi cụm có tên HVN đều giao HỘP ± dung sai; có cụm chỉ giao vùng đệm ⇒ không mang tên HVN đó.
        int diff = 0, onlyBuf = 0, onlyBufNamed = 0, named = 0, namedBad = 0;
        foreach (var kv in res)
        {
            var (j, r0, _, _) = kv.Value;
            var cache = new Dictionary<string, (List<SzLevel> lv, bool apx)>();
            var rA = StrongZones.Compute(Series(f, 0, j + 1, p), p, cache);
            foreach (var c in cache.Values) foreach (var L in c.lv) if (L.IsHvn) { L.BufLo = L.Lo - 5000; L.BufHi = L.Hi + 5000; }
            var rB = StrongZones.Compute(Series(f, 0, j + 1, p), p, cache);
            bool same = ReferenceEquals(rA.Levels, rB.Levels) && rA.Clusters.Count == rB.Clusters.Count
                        && rA.Clusters.Zip(rB.Clusters, (x, y) => x.Lo == y.Lo && x.Hi == y.Hi && x.NGroup == y.NGroup && x.Gold == y.Gold && x.Hvn == y.Hvn && string.Join(",", x.Names) == string.Join(",", y.Names)).All(z => z);
            if (!same) diff++;
            double tol = p.Tol * r0.U;
            foreach (var z in r0.Clusters)
                foreach (var L in r0.Levels.Where(L => L.IsHvn && StrongZones.HvnOk(L, r0.Highs, r0.Lows, r0.J, r0.U, p)))
                {
                    bool hitBox = L.Lo <= z.Hi + tol && L.Hi >= z.Lo - tol;
                    bool hitBuf = L.BufLo <= z.Hi + tol && L.BufHi >= z.Lo - tol;
                    if (hitBox) { named++; if (!z.Names.Contains(L.Name)) namedBad++; }
                    else if (hitBuf)
                    {
                        onlyBuf++;
                        bool otherSame = r0.Levels.Any(M => M != L && M.IsHvn && M.Name == L.Name && M.Lo <= z.Hi + tol && M.Hi >= z.Lo - tol && StrongZones.HvnOk(M, r0.Highs, r0.Lows, r0.J, r0.U, p));
                        if (z.Names.Contains(L.Name) && !otherSame) onlyBufNamed++;
                    }
                }
        }
        Check(diff == 0, "hop luu khong dung vung dem: noi rong vung dem 5000 diem trong bo dem muc -> cum / nhom / vang / ten khong doi (19 ca)", $"{diff} ca doi");
        Check(namedBad == 0 && onlyBufNamed == 0, $"du lieu that: cum giao hop +- dung sai -> co ten HVN ({named} cap); cum chi giao vung dem -> khong mang ten HVN do ({onlyBuf} cap)",
              $"thieu ten {namedBad}, sai ten {onlyBufNamed}");

        // render PNG: 07:00 (trước), 07:30 (nến chạm đệm), 08:00 (bật lên), cuối dữ liệu 08:30 (nến đang chạy)
        Color sup = Color.FromArgb(0x26, 0xA6, 0x9A), rs = Color.FromArgb(0xEF, 0x53, 0x50), gold = Color.FromArgb(0xFF, 0xD6, 0x00);
        int nPng = 0;
        try
        {
            string outDir = UiDir();
            Directory.CreateDirectory(outDir);
            foreach (var (hh, mm) in new[] { (7, 0), (7, 30), (8, 0) })
            {
                if (!res.TryGetValue(new DateTime(2026, 11, 25, hh, mm, 0), out var c)) continue;
                RenderPng(f, c.j, c.sh, c.bx, Path.Combine(outDir, $"ca_NQ_2026-11-25_{hh:00}{mm:00}_vung_dem.png"), sup, rs, gold,
                          $"NQZ26 · nến đóng {f.T[c.j]:yyyy-MM-dd HH:mm} UTC · giá {f.C[c.j]:0.00} · đáy nến {f.L[c.j]:0.00} · U {c.r.U:0.0}");
                nPng++;
            }
            {
                int jl = f.N - 2; double nowL = f.C[f.N - 1];
                var r = StrongZones.Compute(Series(f, 0, jl + 1, p), p);
                var sh = StrongZones.Display(r, nowL, p); var bx = StrongZones.HvnBoxes(r, nowL, p);
                Console.WriteLine($"       NQ cuoi du lieu {f.T[f.N - 1]:yyyy-MM-dd HH:mm} gia {nowL:0.00}: {StrongZones.HvnSummaryLine(bx, x => x.ToString("0.00", IC))}");
                RenderPng(f, jl, sh, bx, Path.Combine(outDir, "ca_NQ_2026-11-25_0830_cuoi_du_lieu_vung_dem.png"), sup, rs, gold,
                          $"NQZ26 · cuối dữ liệu {f.T[f.N - 1]:yyyy-MM-dd HH:mm} UTC (nến đang chạy) · giá {nowL:0.00} · U {r.U:0.0}", nowL);
                nPng++;
                Check(f.T[f.N - 1] == new DateTime(2026, 11, 25, 8, 30, 0) && bx.Any(b => Near(b.Lo, 25538.50, 1e-9) && Near(b.BufHi, 25652.25, 1e-9)),
                      "NQ cuoi du lieu 25/11 08:30: van ve hop 25538,50-25609,75 + dem tren toi 25652,25");
            }
        }
        catch (Exception ex) { Check(false, "render PNG NQ 25/11", ex.GetType().Name + ": " + ex.Message); }
        Check(nPng == 4, "render PNG NQ 25/11 (hop + vung dem) bang chinh StrongZonePainter.Paint", $"{nPng} anh -> {UiDir()}");
    }
}
