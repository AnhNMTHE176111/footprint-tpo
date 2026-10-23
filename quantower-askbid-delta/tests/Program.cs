// Test lõi nến delta (DeltaCore.cs) — không cần SDK. Chạy: dotnet run
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using AskBidDeltaCore;

static class T
{
    static int ok, fail;
    static void Check(bool c, string name) { if (c) { ok++; Console.WriteLine("  OK   " + name); } else { fail++; Console.WriteLine("  FAIL " + name); } }
    static long Tk(int min) => new DateTime(2026, 9, 14, 6, 0, 0, DateTimeKind.Utc).AddMinutes(min).Ticks;   // 06:00 UTC = 13:00 VN

    static int Main()
    {
        Console.WriteLine("[1] QtRangeReal — nhận diện giá trị mồi");
        Check(!DeltaCore.QtRangeReal(-20, double.MinValue, double.MaxValue, 50), "mồi MinValue/MaxValue -> không thật");
        Check(!DeltaCore.QtRangeReal(-20, -20, -20, 50), "Max=Min=Delta trên nến ≥2 giao dịch -> không thật (kiểu dữ liệu nạp lại)");
        Check(DeltaCore.QtRangeReal(-20, 3, -35, 50), "Max 3 / Min -35 bao Delta -20 -> thật");
        Check(DeltaCore.QtRangeReal(5, 5, 5, 1), "nến 1 giao dịch phẳng -> thật");
        Check(!DeltaCore.QtRangeReal(10, 4, -3, 20), "đỉnh 4 < delta cuối 10 -> không thể -> không thật");
        Check(!DeltaCore.QtRangeReal(double.NaN, 1, -1, 5), "NaN -> không thật");

        Console.WriteLine("[2] ResolveRange — 3 nguồn theo thứ tự ưu tiên");
        var tb = new TickBar { End = -20, Hi = 2, Lo = -33, N = 40 };
        var s1 = DeltaCore.ResolveRange(-20, true, 3, -35, true, tb, out var h1, out var l1);
        Check(s1 == RangeSrc.Quantower && h1 == 3 && l1 == -35, "Quantower thật được ưu tiên hơn tick");
        var s2 = DeltaCore.ResolveRange(-20, false, -20, -20, true, tb, out var h2, out var l2);
        Check(s2 == RangeSrc.Ticks && h2 == 2 && l2 == -33, "không có Quantower -> dùng tick (khớp delta cuối)");
        var s3 = DeltaCore.ResolveRange(-20, false, -20, -20, true, new TickBar { End = -9, Hi = 0, Lo = -12, N = 10 }, out var h3, out var l3);
        Check(s3 == RangeSrc.None && h3 == 0 && l3 == -20, "tick LỆCH delta Quantower -> bỏ tick, không bịa râu");
        var s4 = DeltaCore.ResolveRange(15, false, 15, 15, false, default, out var h4, out var l4);
        Check(s4 == RangeSrc.None && h4 == 15 && l4 == 0, "không có gì -> thân 0..delta, nguồn None");
        var s5 = DeltaCore.ResolveRange(-20, false, 0, 0, true, new TickBar { End = -20, Hi = 0, Lo = -20, N = 0 }, out _, out _);
        Check(s5 == RangeSrc.None, "tick N=0 -> không dùng");

        Console.WriteLine("[3] TickAccumulator — dựng delta chạy từ tick");
        var starts = new[] { Tk(0), Tk(1), Tk(2) };
        var acc = new TickAccumulator(starts);
        acc.Feed(Tk(0) + 10, 5, +1);   // run 5
        acc.Feed(Tk(0) + 20, 8, -1);   // run -3
        acc.Feed(Tk(0) + 30, 4, -1);   // run -7
        acc.Feed(Tk(0) + 40, 9, +1);   // run +2 (đỉnh 5 trước đó)
        acc.Feed(Tk(1) + 5, 3, +1);
        acc.Feed(Tk(1) + 6, 2, 0);     // không rõ bên: không tính
        acc.Flush();
        var b0 = acc.Result[starts[0]];
        Check(b0.End == 2 && b0.Hi == 5 && b0.Lo == -7 && b0.N == 4, $"nến 0: End 2 / Hi 5 / Lo -7 / N 4 (được {b0.End}/{b0.Hi}/{b0.Lo}/{b0.N})");
        var b1 = acc.Result[starts[1]];
        Check(b1.End == 3 && b1.Hi == 3 && b1.Lo == 0 && b1.UnclassVol == 2, "nến 1: tick không rõ bên chỉ vào UnclassVol");
        Check(!acc.Result.ContainsKey(starts[2]), "nến 2 không có tick -> không có kết quả");
        acc.Feed(Tk(0) + 50, 1, +1);   // đi lùi thời gian
        Check(acc.OutOfOrder == 1, "tick đi lùi bị đếm, không làm hỏng nến");
        // nạp theo 2 đợt: cho kết quả giống nạp một lần
        var a1 = new TickAccumulator(starts); var a2 = new TickAccumulator(starts);
        var ticks = new (long, double, int)[] { (Tk(0) + 1, 4, 1), (Tk(0) + 2, 6, -1), (Tk(0) + 3, 1, 1), (Tk(1) + 1, 7, 1) };
        foreach (var t in ticks) a1.Feed(t.Item1, t.Item2, t.Item3);
        a1.Flush();
        a2.Feed(ticks[0].Item1, ticks[0].Item2, ticks[0].Item3); a2.Feed(ticks[1].Item1, ticks[1].Item2, ticks[1].Item3); a2.Flush();
        a2.Feed(ticks[2].Item1, ticks[2].Item2, ticks[2].Item3); a2.Feed(ticks[3].Item1, ticks[3].Item2, ticks[3].Item3); a2.Flush();
        Check(a1.Result[starts[0]].End == a2.Result[starts[0]].End && a1.Result[starts[0]].Lo == a2.Result[starts[0]].Lo
              && a1.Result[starts[0]].Hi == a2.Result[starts[0]].Hi, "nạp 2 đợt (cắt giữa nến) = nạp 1 đợt");

        Console.WriteLine("[4] BuildChain — cộng dồn, đặt lại, từng nến");
        var raw = new List<RawBar>();
        double[] dl = { 10, -30, 25, 5, -8 };
        for (int i = 0; i < dl.Length; i++)
            raw.Add(new RawBar { TimeUtcTicks = Tk(i), HasVa = true, Volume = 100, Trades = 50, Delta = dl[i], QtMax = Math.Max(dl[i], 0) + 3, QtMin = Math.Min(dl[i], 0) - 2 });
        var ch = DeltaCore.BuildChain(raw, null, false, false, 7, 300);
        bool cont = true; for (int i = 1; i < ch.Length; i++) cont &= ch[i].Open == ch[i - 1].Close;
        Check(cont, "Open nến i = Close nến i-1 (nến nối liền)");
        Check(ch[0].Open == 0 && ch[0].Close == 10 && ch[4].Close == 2, "Close = tổng cộng dồn (10,-20,5,10,2)");
        Check(ch[1].High == 10 + 3 && ch[1].Low == 10 - 30 - 2, "High/Low cộng vào Open");
        bool inv = true; foreach (var c in ch) inv &= c.Low <= Math.Min(c.Open, c.Close) && c.High >= Math.Max(c.Open, c.Close);
        Check(inv, "Low ≤ min(O,C) ≤ max(O,C) ≤ High mọi nến");
        var chBar = DeltaCore.BuildChain(raw, null, true, false, 7, 300);
        Check(chBar.All(c => c.Open == 0), "chế độ từng nến: mọi nến mở từ 0");
        Check(chBar[1].Close == -30, "chế độ từng nến: Close = delta của nến");

        // reset hằng ngày tại 05:00 VN (= 22:00 UTC hôm trước)
        var raw2 = new List<RawBar>();
        long day = new DateTime(2026, 9, 14, 0, 0, 0, DateTimeKind.Utc).Ticks;
        long[] ts = { day + 21 * TimeSpan.TicksPerHour + 58 * TimeSpan.TicksPerMinute,    // 04:58 VN 15/09 — vẫn ngày cũ
                      day + 21 * TimeSpan.TicksPerHour + 59 * TimeSpan.TicksPerMinute,    // 04:59 VN
                      day + 22 * TimeSpan.TicksPerHour,                                   // 05:00 VN — sang ngày mới
                      day + 22 * TimeSpan.TicksPerHour + TimeSpan.TicksPerMinute };
        foreach (var t in ts) raw2.Add(new RawBar { TimeUtcTicks = t, HasVa = true, Volume = 10, Trades = 5, Delta = 10, QtMax = 12, QtMin = -1 });
        var ch2 = DeltaCore.BuildChain(raw2, null, false, true, 7, 300);
        Check(ch2[1].Close == 20 && ch2[2].Open == 0 && ch2[2].Close == 10 && ch2[3].Close == 20, "đặt lại về 0 đúng lúc 05:00 giờ VN");
        var ch2n = DeltaCore.BuildChain(raw2, null, false, false, 7, 300);
        Check(ch2n[3].Close == 40, "tắt đặt lại: cộng dồn mãi");
        Check(DeltaCore.DayKey(day + 22 * TimeSpan.TicksPerHour, 7, 300) == DeltaCore.DayKey(day + 22 * TimeSpan.TicksPerHour + 1, 7, 300)
              && DeltaCore.DayKey(day + 22 * TimeSpan.TicksPerHour - 1, 7, 300) != DeltaCore.DayKey(day + 22 * TimeSpan.TicksPerHour, 7, 300), "DayKey đổi đúng tại mốc");

        // nến rỗng / không có VA: không phá chuỗi
        var raw3 = new List<RawBar> { raw[0], new RawBar { TimeUtcTicks = Tk(1) }, raw[2] };
        var ch3 = DeltaCore.BuildChain(raw3, null, false, false, 7, 300);
        Check(ch3[1].Empty && ch3[2].Open == ch3[0].Close, "nến không có VA bị bỏ qua, chuỗi vẫn liền");

        // dùng tick thay mồi
        var rawF = new List<RawBar> { new RawBar { TimeUtcTicks = Tk(0), HasVa = true, Volume = 50, Trades = 30, Delta = -20, QtMax = -20, QtMin = -20 } };
        var tickRes = new Dictionary<long, TickBar> { [Tk(0)] = new TickBar { End = -20, Hi = 2, Lo = -33, N = 30 } };
        var chF = DeltaCore.BuildChain(rawF, tickRes, true, false, 7, 300);
        Check(chF[0].Src == RangeSrc.Ticks && chF[0].High == 2 && chF[0].Low == -33, "nến nạp lại (Max=Min=Delta) được dựng râu từ tick");
        var chN = DeltaCore.BuildChain(rawF, null, true, false, 7, 300);
        Check(chN[0].Src == RangeSrc.None && chN[0].High == 0 && chN[0].Low == -20, "không có tick -> Src=None (không vẽ như nến thật)");

        Console.WriteLine("[5] HỒI QUY trên số liệu THẬT đã xuất (sự cố vạch ngang)");
        string dir = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../../../../data-export/data-footprint"));
        string f1 = Directory.Exists(dir) ? Directory.GetFiles(dir, "fp_GCZ26_XCEC_Time_20260816-20260914_28d18h_bars.csv").FirstOrDefault() : null;
        if (f1 == null) Console.WriteLine("  (bỏ qua: không thấy file xuất mẫu)");
        else
        {
            var lines = File.ReadLines(f1); var hdr = lines.First().Split(',');
            int ix(string n) => Array.IndexOf(hdr, n);
            int iD = ix("delta"), iMx = ix("max_delta"), iMn = ix("min_delta"), iV = ix("volume"), iTr = ix("trades"), iDt = ix("datetime");
            int total = 0, flatMis = 0, real = 0, realMis = 0; var realTimes = new List<string>();
            foreach (var ln in lines.Skip(1))
            {
                var p = ln.Split(',');
                double v = double.Parse(p[iV], CultureInfo.InvariantCulture); if (v <= 0) continue;
                double d = double.Parse(p[iD], CultureInfo.InvariantCulture), mx = double.Parse(p[iMx], CultureInfo.InvariantCulture), mn = double.Parse(p[iMn], CultureInfo.InvariantCulture);
                int tr = (int)double.Parse(p[iTr], CultureInfo.InvariantCulture);
                total++;
                bool isReal = DeltaCore.QtRangeReal(d, mx, mn, tr);
                bool exportFlat = mx == d && mn == d && tr > 1;
                if (exportFlat && isReal) flatMis++;
                if (!exportFlat && mx != mn) { real++; realTimes.Add(p[iDt]); if (!isReal) realMis++; }
            }
            Console.WriteLine($"  file: {Path.GetFileName(f1)} · {total:N0} nến có volume · {real} nến có đỉnh/đáy thật ({realTimes.FirstOrDefault()} → {realTimes.LastOrDefault()})");
            Check(total > 20000, "đọc đủ dữ liệu thật");
            Check(flatMis == 0, "KHÔNG nến phẳng (Max=Min=Delta, ≥2 giao dịch) nào bị coi là thật");
            Check(real > 0 && realMis == 0, "mọi nến có đỉnh/đáy thật đều được nhận là thật");
            Check(real * 100.0 / total < 1.0, $"đúng như đã đo: chỉ {real * 100.0 / total:0.00}% nến có râu thật, còn lại phải dựng từ tick");
        }

        Console.WriteLine($"\n=> {ok} OK, {fail} FAIL");
        return fail == 0 ? 0 : 1;
    }
}
