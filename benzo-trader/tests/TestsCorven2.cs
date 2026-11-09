// Unit test corven-2 (4 sửa đổi người học 2026-11-09, research/report/VARIANTS-NGUOI-HOC-2026-11-09.md) = setup_corven.cp_live().
// Mỗi luật: bộ mặc định (corven-3) và CorvenCfg.V1() (corven-1) cho kết quả ngược nhau trên cùng một ca.
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
        Check(CorvenParams.LogicVersion == "corven-3", "LogicVersion = corven-3");

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
        Console.WriteLine("[V2-4] Ca thật 09/11 11:26 VN (buy, nhịp hồi không chạm cạnh + trap hồi) — file 3 tháng mới");
        {
            string root = RepoRoot();
            string prefix = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260811-20261109_90d");
            if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Console.WriteLine("  (bỏ qua: không có file 20260811-20261109)"); return; }
            var (b, l) = CorvenData.Load(prefix);
            var (eng, _) = CorvenData.Run(b, l, 0.1);
            var day = eng.Signals.Where(x => x.Time.Date == new DateTime(2026, 11, 9)).ToList();
            var sell = day.FirstOrDefault(x => x.Time == new DateTime(2026, 11, 9, 3, 11, 0, DateTimeKind.Utc));
            Check(sell != null && sell.Side == -1 && Near(sell.Entry, 4126.0, 1e-6) && Near(sell.Sl, 4135.1, 1e-6) && sell.Outcome == "SL"
                  && sell.ExitTime == new DateTime(2026, 11, 9, 4, 30, 0, DateTimeKind.Utc),
                  "corven-3 (= Python cp_live): lệnh B sell 10:11 VN, SL 4135,1 (cạnh 4134,6 + 3 tick), dính SL 11:30 VN", sell == null ? "không có" : $"{sell.Entry} {sell.Sl} {sell.Outcome}");
            Check(!day.Any(x => x.Time == new DateTime(2026, 11, 9, 4, 26, 0, DateTimeKind.Utc)), "⇒ ca 11:26 VN không vào vì đang có lệnh (luật 1 lệnh mở)");
        }
    }
}
