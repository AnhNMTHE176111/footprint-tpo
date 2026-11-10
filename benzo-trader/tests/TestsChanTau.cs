// Unit test corven-8 "không cản tàu": CorvenFeat.StructState (= setup_corven.struct_states) — N = 2 cho ngắn.
using System;
using System.Collections.Generic;
using System.Linq;
using BenzoTraderNs;

static partial class Program
{
    // (cao, thấp) — đỉnh 110 (nến 2), đáy 90 (nến 5), đỉnh 106 (nến 8), đáy 85 (nến 11) ⇒ GIẢM, xác nhận ở nến 13
    static readonly (long h, long l)[] CtBase =
    {
        (100, 95), (102, 97), (110, 105), (104, 99), (101, 96), (100, 90), (103, 94), (105, 98),
        (106, 100), (102, 96), (99, 92), (98, 85), (97, 88), (96, 89),
    };
    static CorvenFeat CtWorld(List<(long h, long l, long c)> bars, List<DateTime> times = null)
    {
        var rows = bars.Select(b => R_((b.h + b.l) / 2, b.h, b.l, b.c)).ToList();
        return World(rows, times: times).f;
    }
    static List<(long h, long l, long c)> CtSeries(params (long h, long l, long c)[] extra)
    {
        var s = CtBase.Select(b => (b.h, b.l, c: (b.h + b.l) / 2)).ToList();
        s.AddRange(extra);
        return s;
    }

    static void TestsChanTau()
    {
        Console.WriteLine("[CT] Không cản tàu: trạng thái cấu trúc (pivot N = 2)");
        Check(CorvenParams.ChanTauN == 5 && new CorvenCfg().ChanTauN == 5 && CorvenCfg.V1().ChanTauN == 0, "ChanTauN = 5 mặc định, V1 = 0 (tắt)");
        Check(CorvenRules.GateVn("v_can_tau") == "không cản tàu" && CorvenRules.AllGateLabels.Contains("không cản tàu") && CorvenRules.GateCodes.Contains("v_can_tau"), "nhãn cổng 'không cản tàu'");

        var f = CtWorld(CtSeries());
        Check(f.StructState(2, 13) == -1, "đỉnh 110→106, đáy 90→85 hạ dần, đã xác nhận ⇒ GIẢM (chặn Fail Break buy)", f.StructState(2, 13).ToString());
        Check(f.StructState(2, 12) == 0, "đáy 85 (nến 11) chưa xác nhận ở nến 12 ⇒ chưa dùng, TRUNG TÍNH", f.StructState(2, 12).ToString());
        Check(f.StructState(0, 13) == 0, "N = 0 ⇒ luôn TRUNG TÍNH");

        var fw = CtWorld(CtSeries((107, 95, 105)));
        Check(fw.StructState(2, 14) == -1, "râu vượt đỉnh 106 (cao 107) mà ĐÓNG 105 dưới ⇒ vẫn GIẢM (vẫn chặn)", fw.StructState(2, 14).ToString());

        var fb = CtWorld(CtSeries((108, 100, 107)));
        Check(fb.StructState(2, 14) == 0, "đóng cửa 107 trên đỉnh 106 ⇒ GÃY, TRUNG TÍNH (không chặn)", fb.StructState(2, 14).ToString());
        var fb2 = CtWorld(CtSeries((108, 100, 107), (107, 99, 100)));
        Check(fb2.StructState(2, 15) == 0, "sau khi gãy vẫn TRUNG TÍNH cho tới khi có đỉnh mới xác nhận");

        var rows = CtSeries();
        rows[12] = (97, 85, 91);     // đáy nến 12 = 85 bằng nến 11 ⇒ không nến nào là pivot đáy
        var fe = CtWorld(rows);
        Check(fe.StructState(2, 13) == 0, "đáy bằng nhau (85 = 85) không là pivot ⇒ chỉ 1 pivot đáy ⇒ TRUNG TÍNH", fe.StructState(2, 13).ToString());

        var times = new List<DateTime>();
        for (int i = 0; i < 14; i++) times.Add(W0.AddMinutes(i));
        for (int i = 14; i < 17; i++) times.Add(W0.AddHours(3).AddMinutes(i));
        var fs = CtWorld(CtSeries((97, 90, 93), (96, 89, 92), (95, 88, 91)), times);
        Check(fs.StructState(2, 13) == -1 && fs.StructState(2, 14) == 0 && fs.StructState(2, 16) == 0, "sang phiên mới ⇒ xoá pivot, TRUNG TÍNH", $"{fs.StructState(2, 14)}/{fs.StructState(2, 16)}");

        // đối xứng: lật giá ⇒ TĂNG (+1) (chặn Fail Break sell)
        var up = CtBase.Select(b => (h: 200 - b.l, l: 200 - b.h)).Select(b => (b.h, b.l, c: (b.h + b.l) / 2)).ToList();
        Check(CtWorld(up).StructState(2, 13) == 1, "cấu trúc lật ngược ⇒ TĂNG (+1)");
    }
}
