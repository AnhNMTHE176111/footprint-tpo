// Unit test corven-2 (4 sửa đổi người học 2026-11-09, research/report/VARIANTS-NGUOI-HOC-2026-11-09.md) = setup_corven.cp_live().
// Mỗi luật: bộ mặc định (corven-5) và CorvenCfg.V1() (corven-1) cho kết quả ngược nhau trên cùng một ca.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using BenzoTraderNs;
using OrderFlowBubbles;

static partial class Program
{
    static void TestsCorven2()
    {
        Console.WriteLine("[V2-0] Phiên bản");
        Check(CorvenParams.LogicVersion == "corven-5", "LogicVersion = corven-5");

        Console.WriteLine("[V2-1] Trap trong nhịp hồi (thế B sell): ô Ask 20 ở nến hồi 13 @4126,8, CF đóng 4126,6 dưới ô");
        {
            var rows = Ex2Rows();
            var r = rows[13];
            rows[13] = R_(r.o, r.h, r.l, r.c, r.d, SetLv(Uni(r.l, r.h), 41268, ask: 20));
            var (f, _) = World(rows);
            var c2 = Eval(Ex2Cand(), f);
            var tr = c2.Signs.FirstOrDefault(s => s.Type == "trap");
            Check(tr != null && tr.Desc == "trap hồi, bóng xanh 20 @4126,8" && tr.Bar == 13, "corven-2: có dấu hiệu trap hồi", tr?.Desc ?? Types(c2));
            var c1 = Eval(Ex2Cand(), f, CorvenCfg.V1());
            Check(!c1.Has("trap"), "corven-1: không có", Types(c1));
            rows[13] = R_(r.o, r.h, r.l, r.c, r.d, SetLv(Uni(r.l, r.h), 41268, ask: 14));
            var (g, _) = World(rows);
            Check(!Eval(Ex2Cand(), g).Has("trap"), "ô 14 < 3 × nền 5 ⇒ không tính");
            rows[13] = R_(r.o, r.h, r.l, r.c, r.d, SetLv(Uni(r.l, r.h), 41264, ask: 20));
            var (h, _) = World(rows);
            Check(!Eval(Ex2Cand(), h).Has("trap"), "ô @4126,4 dưới giá đóng CF 4126,6 ⇒ CF chưa vượt qua ⇒ không tính");
        }
        Console.WriteLine("[V2-2] Bỏ ⛔ quét stop: cú đẩy sell nhưng ΣΔ dương");
        {
            var rows = Ex2Rows();
            rows[11] = R_(rows[11].o, rows[11].h, rows[11].l, rows[11].c, 80);
            rows[12] = R_(rows[12].o, rows[12].h, rows[12].l, rows[12].c, 50);
            var (f, _) = World(rows);
            Check(Eval(Ex2Cand(), f, CorvenCfg.V1()).Gates.Contains("v_quet_stop"), "corven-1: bị veto quét stop");
            Check(!Eval(Ex2Cand(), f).Gates.Contains("v_quet_stop"), "corven-2: không còn veto");
        }
        Console.WriteLine("[V2-3] Thế B bỏ R sẵn ≥ 1,7 — TP vẫn 2R; thế A giữ");
        {
            var (f, _) = World(Ex2Rows());
            CorvenCand Mk() { var c = Ex2Cand(); c.InstTop = 41300; return c; }
            var c1 = Eval(Mk(), f, CorvenCfg.V1());
            Check(c1.RAvail < 1.7 && c1.Gates.Contains("r_nho"), "corven-1: R sẵn < 1,7 ⇒ bỏ", c1.RAvail.ToString("0.00"));
            var c2 = Eval(Mk(), f);
            Check(!c2.Gates.Contains("r_nho") && Near(c2.Tp, c2.Entry - 2 * c2.Risk), "corven-2: vào, TP = 2R", string.Join(";", c2.Gates));
            var (g, _) = GeoWorld(41377);
            Check(Eval(GeoCand(41356 - 40), g).Gates.Contains("r_nho"), "thế A vẫn bị luật R ≥ 1,7");
        }
        Console.WriteLine("[V3-1] SL thế B mốc cạnh: ngay dưới cạnh vừa phá − đệm (corven-3), không trừ dung sai (corven-1/2)");
        {
            var (f, _) = World(Ex2Rows());
            CorvenCand Mk() => Ex2Cand(new List<CorvenMoc> { Canh(41280) });     // sell, cạnh 4128,0 ± 0,75; đỉnh cửa sổ 4128,4
            var c3 = Eval(Mk(), f);
            Check(c3.Sl == 41287 && c3.MocUsed == "canh", "corven-3: SL = max(4128,4; 4128,0) + 3 tick = 4128,7", c3.Sl.ToString());
            var c1 = Eval(Mk(), f, CorvenCfg.V1());
            Check(c1.Sl == 41291, "corven-1: SL = max(4128,4; 4128,0 + 0,75) + 3 tick, làm tròn ra xa = 4129,1", c1.Sl.ToString());
        }
        Console.WriteLine("[V4-1] corven-4: nhịp hồi không chạm cạnh phải thuộc cú phá — nến hồi đầu tiên cách nến phá ≤ 5 nến (máy ①② trên hộp đều)");
        {
            // cú phá: rf (đóng ngoài đầu tiên) rồi các nến đẩy lên; nến hồi đầu tiên ở rf+pb; 1 nến lên; CF đóng vượt giá đóng nến hồi. Không nến nào chạm cạnh 4104,9 (± dung sai)
            List<CorvenBar> Seq(int pb, out int bc, out int cf)
            {
                var bars = BaseBars();
                int rf = Add(bars, TT - 8, TT + 12, TT - 10, TT + 8);
                long c = TT + 8;
                for (int k = 1; k < pb; k++) { long n = c + 15; Add(bars, c, n + 5, c - 2, n); c = n; }
                bc = rf + 3;
                Add(bars, c, c + 2, c - 12, c - 8);                  // nến hồi: đóng thấp hơn nến trước, nến đỏ, vẫn đóng ngoài
                long d = c - 8; Add(bars, d, d + 20, d - 2, d + 15); d += 15;
                cf = Add(bars, d, d + 25, d - 2, d + 20);             // đóng vượt giá đóng nến hồi
                return bars;
            }
            foreach (var (pb, ok) in new[] { (3, true), (5, true), (6, false) })
            {
                var bs = Seq(pb, out int bc, out int cf);
                var (_, cs) = RunM(bs);
                Check(HasB(cs, bc, cf) == ok, $"nến hồi đầu tiên cách nến phá {pb} nến ⇒ " + (ok ? "nhận" : "loại"));
                var (_, csOff) = RunM(bs, new CorvenCfg { HoiTrongNNen = false });
                Check(HasB(csOff, bc, cf), $"cờ tắt: ca {pb} nến vẫn nhận (corven-3 cũ)");
                var (_, csV1) = RunM(bs, CorvenCfg.V1());
                Check(!HasB(csV1, bc, cf), $"corven-1: ca {pb} nến không nhận (V1 không có nhánh hồi, không bị ảnh hưởng)");
            }
            var b6 = Seq(6, out int bc6, out int cf6);
            var (_, cs6n) = RunM(b6, new CorvenCfg { HoiMaxNen = 6 });
            Check(HasB(cs6n, bc6, cf6), "ngưỡng 6 nến: ca 6 nến nhận (biên ≤ N)");
        }
        Console.WriteLine("[V2-4] Ca thật 09/11 11:26 VN (buy, nhịp hồi không chạm cạnh + trap hồi) — file 3 tháng mới");
        {
            string root = RepoRoot();
            string prefix = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260811-20261109_90d");
            if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Console.WriteLine("  (bỏ qua: không có file 20260811-20261109)"); return; }
            var (b, l) = CorvenData.Load(prefix);
            var (eng, _) = CorvenData.Run(b, l, 0.1);
            var day = eng.Signals.Where(x => x.Time.Date == new DateTime(2026, 11, 9)).ToList();
            Check(!day.Any(x => x.Time == new DateTime(2026, 11, 9, 0, 43, 0, DateTimeKind.Utc)), "corven-5: lệnh Break buy 07:43 VN 09/11 (mốc vùng stacked, 4107,9) không còn");
            Check(!eng.Signals.Any(x => x.Time == new DateTime(2026, 11, 6, 16, 8, 0, DateTimeKind.Utc)), "corven-5: lệnh Break buy 23:08 VN 06/11 (mốc vùng stacked 4070,8–4071,0, 4072,9) không còn");
            Check(!day.Any(x => x.Time == new DateTime(2026, 11, 9, 3, 11, 0, DateTimeKind.Utc)), "corven-4: lệnh B sell 10:11 VN (nhịp hồi xa cú phá) không còn");
            var s = day.FirstOrDefault(x => x.Time == new DateTime(2026, 11, 9, 4, 26, 0, DateTimeKind.Utc));
            Check(s != null && s.Setup == 'B' && s.Side == 1 && Near(s.Entry, 4132.3, 1e-6) && Near(s.Sl, 4129.1, 1e-6) && Near(s.Tp, 4138.7, 1e-6) && s.Zone == "canh",
                  "có lệnh B buy 11:26 VN: 4132,3 · SL 4129,1 · TP 4138,7 · mốc cạnh", s == null ? "không có" : $"{s.Setup} {s.Side} {s.Entry} {s.Sl} {s.Tp} {s.Zone}");
            Check(s != null && s.Signs.Contains("trap hồi, bóng đỏ 20 @4131,3"), "dấu hiệu gồm trap hồi bóng đỏ 20 @4131,3", s?.Signs);
        }
    }
}
