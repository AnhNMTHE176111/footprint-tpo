// Unit test corven-2 (4 sửa đổi người học 2026-11-09, research/report/VARIANTS-NGUOI-HOC-2026-11-09.md) = setup_corven.cp_live().
// Mỗi luật: bộ mặc định (corven-7) và CorvenCfg.V1() (corven-1) cho kết quả ngược nhau trên cùng một ca.
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
        Check(CorvenParams.LogicVersion == "corven-7", "LogicVersion = corven-7");

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
            var c3 = Eval(Mk(), f, new CorvenCfg { SlBCanh3Tick = false });
            Check(c3.Sl == 41287 && c3.MocUsed == "canh", "corven-3/4/5: SL = max(4128,4; 4128,0) + 3 tick = 4128,7", c3.Sl.ToString());
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
        Console.WriteLine("[V6-1] corven-6: SL Break mốc cạnh = cạnh vừa phá ∓ 3 tick; râu nhịp hồi vượt cạnh không làm SL xa thêm");
        {
            var (f, _) = World(Ex2Rows());
            CorvenCand Mk() => Ex2Cand(new List<CorvenMoc> { Canh(41280) });     // sell, cạnh 4128,0; râu nhịp hồi lên 4128,4 (nến 14); CF đóng 4126,6
            var c6 = Eval(Mk(), f);
            Check(c6.Sl == 41283 && c6.Risk == 17 && c6.MocUsed == "canh", "corven-6: SL = 4128,0 + 3 tick = 4128,3 (không theo râu 4128,4)", $"{c6.Sl} {c6.Risk}");
            var c5 = Eval(Mk(), f, new CorvenCfg { SlBCanh3Tick = false });
            Check(c5.Sl == 41287, "cờ tắt (corven-3…5): SL = râu 4128,4 + 3 tick = 4128,7 — xa hơn", c5.Sl.ToString());
            // sàn 1 biên độ vẫn giữ: mbr 30 ⇒ rủi ro tối thiểu 30 tick
            var (fb, _) = World(Ex2Rows(), mbr: 30);
            var cf = Eval(Mk(), fb);
            Check(cf.Risk >= 30 && cf.Sl == 41296, "sàn 1 biên độ giữ: mbr 30 ⇒ SL dời ra 30 tick = 4129,6", $"{cf.Sl} {cf.Risk}");
        }
        Console.WriteLine("[V6-2] corven-6: trần SL theo GIÁ (mặc định 5,0): rủi ro 5,0 nhận · 5,1 bỏ · đặt 3,0 ⇒ bỏ ca 3,7");
        {
            var (f50, _) = GeoWorld(41403, mbr: 15); var (f51, _) = GeoWorld(41404, mbr: 15); var (f37, _) = GeoWorld(41390, mbr: 15);
            var c50 = Eval(GeoCand(41000), f50); var c51 = Eval(GeoCand(41000), f51); var c37 = Eval(GeoCand(41000), f37);
            Check(c50.Risk == 50 && !c50.Gates.Contains("tran_sl"), "rủi ro 5,0 giá ⇒ nhận", $"{c50.Risk} {string.Join(";", c50.Gates)}");
            Check(c51.Risk == 51 && c51.Gates.Contains("tran_sl"), "rủi ro 5,1 giá ⇒ bỏ (cổng tran_sl)", $"{c51.Risk} {string.Join(";", c51.Gates)}");
            Check(c37.Risk == 37 && !c37.Gates.Contains("tran_sl") && Eval(GeoCand(41000), f37, new CorvenCfg { SlMaxGia = 3.0 }).Gates.Contains("tran_sl"), "rủi ro 3,7 giá: nhận ở 5,0, bỏ khi SlMaxGia = 3,0");
            Check(!Eval(GeoCand(41000), f51, new CorvenCfg { SlMaxGia = 6.0 }).Gates.Contains("tran_sl"), "SlMaxGia = 6,0 ⇒ rủi ro 5,1 nhận (trần theo giá, không theo biên độ)");
            Check(CorvenRules.GateVn("tran_sl", 5.0) == "SL > 5,0 giá" && CorvenRules.GateVn("tran_sl", 3.5) == "SL > 3,5 giá", "nhãn cổng hiển thị 'SL > X giá'");
        }
        Console.WriteLine("[V6-3] corven-6: công tắc Fail Break / Break — tắt một kiểu ⇒ kiểu đó không vào và không chiếm chỗ lệnh mở (TRAIN, = Python bat_break / bat_fail_break)");
        {
            string root = RepoRoot();
            string prefix = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
            if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Console.WriteLine("  (bỏ qua: không có file TRAIN 90d)"); }
            else
            {
                var (tb, tl) = CorvenData.Load(prefix, 51318);
                var (eNo, _) = CorvenData.Run(tb, tl, 0.1, 3697, cfg: new CorvenCfg { BatBreak = false });
                Check(eNo.Signals.Count == 44 && eNo.Signals.All(x => x.Setup == 'A') && eNo.Signals.Count(x => x.Outcome == "TP") == 11 && eNo.Signals.Count(x => x.Outcome == "SL") == 33,
                      "tắt Break: 44 lệnh, toàn Fail Break (= Python; mặc định có 43 Fail Break ⇒ thêm 1 vì không còn bị lệnh Break chiếm chỗ)", $"{eNo.Signals.Count}");
                var (eKc, _) = CorvenData.Run(tb, tl, 0.1, 3697, cfg: CorvenCfg.KieuCu_(true, new CorvenCfg()));
                Check(eKc.Signals.Count == 267 && eKc.Signals.Count(x => x.Setup == 'A') == 41 && eKc.Signals.Count(x => x.Setup == 'B') == 226 && eKc.Signals.Count(x => x.Outcome == "TP") == 98 && eKc.Signals.Count(x => x.Outcome == "SL") == 167,
                      "SL kiểu cũ BẬT: 267 lệnh (41/226, 98 TP · 167 SL) = Python cp_live(sl_kieu_cu=True)", $"{eKc.Signals.Count}");
                var (eNoF, _) = CorvenData.Run(tb, tl, 0.1, 3697, cfg: new CorvenCfg { BatFailBreak = false });
                Check(eNoF.Signals.Count == 187 && eNoF.Signals.All(x => x.Setup == 'B') && eNoF.Signals.Count(x => x.Outcome == "TP") == 65 && eNoF.Signals.Count(x => x.Outcome == "SL") == 120,
                      "tắt Fail Break: 187 lệnh, toàn Break (= Python; mặc định có 186 Break ⇒ thêm 1)", $"{eNoF.Signals.Count}");
            }
        }
        Console.WriteLine("[V6-4] corven-6: Settings \"SL kiểu cũ\" — bật ⇒ SL Break + trần SL như corven-5, bỏ qua SL tối đa");
        {
            var (f, _) = World(Ex2Rows());
            CorvenCand Mk() => Ex2Cand(new List<CorvenMoc> { Canh(41280) });
            var cOld = Eval(Mk(), f, CorvenCfg.KieuCu_(true, new CorvenCfg()));
            Check(cOld.Sl == 41287, "kiểu cũ: SL Break = râu 4128,4 + 3 tick = 4128,7 (corven-5)", cOld.Sl.ToString());
            Check(Eval(Mk(), f, CorvenCfg.KieuCu_(false, new CorvenCfg())).Sl == 41283, "tắt: SL = cạnh + 3 tick = 4128,3 (corven-6)");
            var (f51, _) = GeoWorld(41404, mbr: 15);          // rủi ro 5,1 giá ≤ 4 × 15 tick = 6,0 giá
            Check(Eval(GeoCand(41000), f51).Gates.Contains("tran_sl") && !Eval(GeoCand(41000), f51, CorvenCfg.KieuCu_(true, new CorvenCfg { SlMaxGia = 3.0 })).Gates.Contains("tran_sl"),
                  "rủi ro 5,1 giá: bỏ ở chế độ mặc định, vào ở kiểu cũ (trần 4 biên độ) dù SL tối đa đặt 3,0");
            var (f77, _) = GeoWorld(41430, mbr: 15);          // rủi ro 7,7 giá > 6,0 giá
            Check(Eval(GeoCand(41000), f77, CorvenCfg.KieuCu_(true, new CorvenCfg())).Gates.Contains("tran_sl"), "kiểu cũ: rủi ro 7,7 giá > 4 biên độ ⇒ vẫn bỏ");
        }
        Console.WriteLine("[V2-4] Ca thật 09/11 11:26 VN (buy, nhịp hồi không chạm cạnh + trap hồi) — file 3 tháng mới");
        {
            string root = RepoRoot();
            string prefix = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260811-20261109_90d");
            if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Console.WriteLine("  (bỏ qua: không có file 20260811-20261109)"); return; }
            var (b, l) = CorvenData.Load(prefix);
            bool liveAt0211 = true, liveAt0230 = true; int idxR = -1;
            bool IsR(RangeBox.RangeInfo r) => r.Top0 == 40685 && r.Bottom0 == 40647 && b[r.Start].Time == new DateTime(2026, 10, 29, 1, 35, 0, DateTimeKind.Utc);
            var (eng, detX) = CorvenData.Run(b, l, 0.1, onBar: (i, d) =>
            {
                var t = b[i].Time;
                if (t == new DateTime(2026, 10, 29, 2, 11, 0, DateTimeKind.Utc)) liveAt0211 = d.M.LiveRanges().Any(IsR);
                if (t == new DateTime(2026, 10, 29, 2, 30, 0, DateTimeKind.Utc)) { liveAt0230 = d.M.LiveRanges().Any(IsR); var rr = d.M.Eng.Ranges.FirstOrDefault(IsR); idxR = rr == null ? -1 : rr.Id; }
            });
            Check(idxR >= 0, "tìm thấy range 29/10 4064,7–4068,5 (bắt đầu 08:35 VN)");
            if (idxR >= 0)
            {
                var rr = detX.M.Eng.Ranges[idxR];
                var evR = detX.M.Eng.Events.Where(e => e.Start == rr.Start).ToList();
                Check(rr.State == RangeBox.RangeState.Dead && rr.Exhausted, "corven-7: range 29/10 chuyển Dead (giá chạy lên 4078,0 = 2,3 × chiều cao) — không sống lại", $"{rr.State} {rr.Exhausted}");
                int bcBar = evR.First(q => q.Kind == RangeBox.RangeEventKind.BreakConfirmed).Bar;
                Check(!evR.Any(e => e.Kind == RangeBox.RangeEventKind.ReEntry) && !evR.Any(e => e.Kind == RangeBox.RangeEventKind.Merge) && evR.Count(e => e.Kind == RangeBox.RangeEventKind.BreakConfirmed) == 1 && evR.All(e => e.Bar <= bcBar),
                      "không ReEntry 09:10 VN, không Merge, không sự kiện nào sau BreakConfirmed 08:53 VN", string.Join(",", evR.Select(e => e.Kind)));
                Check(!liveAt0211 && !liveAt0230, "LiveRanges (hộp 'Hiện range') không còn range đó sau lúc chết (09:11 và 09:30 VN)");
            }
            var s0910 = eng.Signals.FirstOrDefault(x => x.Time == new DateTime(2026, 10, 29, 2, 10, 0, DateTimeKind.Utc));
            Check(s0910 != null && s0910.Setup == 'B' && s0910.Side == -1 && Near(s0910.Entry, 4067.8, 1e-6) && s0910.Outcome == "TP", "lệnh Break sell 09:10 VN 29/10 (4067,8) vẫn còn, kết cục TP", s0910 == null ? "không có" : $"{s0910.Entry} {s0910.Outcome}");
            var s63 = eng.Signals.FirstOrDefault(x => x.Time == new DateTime(2026, 11, 6, 3, 33, 0, DateTimeKind.Utc));
            Check(s63 != null && s63.Setup == 'B' && s63.Side == -1 && Near(s63.Entry, 4055.3, 1e-6) && Near(s63.Sl, 4058.8, 1e-6) && Near(s63.Tp, 4048.3, 1e-6) && s63.Outcome == "TP",
                  "corven-6 (= Python): 06/11 10:33 VN Break sell 4055,3 · SL 4058,8 · TP 4048,3 ⇒ TP", s63 == null ? "không có" : $"{s63.Entry} {s63.Sl} {s63.Tp} {s63.Outcome}");
            var (engOld, _) = CorvenData.Run(b, l, 0.1, cfg: CorvenCfg.KieuCu_(true, new CorvenCfg()));
            var s63o = engOld.Signals.FirstOrDefault(x => x.Time == new DateTime(2026, 11, 6, 3, 33, 0, DateTimeKind.Utc));
            Check(s63o != null && Near(s63o.Sl, 4060.3, 1e-6) && Near(s63o.Entry, 4055.3, 1e-6) && s63o.Outcome == "SL", "SL kiểu cũ BẬT: 06/11 03:33 UTC sell SL 4060,3 (= corven-5) ⇒ SL", s63o == null ? "không có" : $"{s63o.Sl} {s63o.Outcome}");
            var s65 = eng.Signals.FirstOrDefault(x => x.Time == new DateTime(2026, 11, 6, 5, 7, 0, DateTimeKind.Utc));
            Check(s65 != null && s65.Setup == 'B' && s65.Side == 1 && Near(s65.Entry, 4058.6, 1e-6) && Near(s65.Sl, 4055.5, 1e-6), "06/11 12:07 VN Break buy 4058,6 · SL 4055,5", s65 == null ? "không có" : $"{s65.Entry} {s65.Sl}");
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
