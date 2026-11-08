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
        Check(ch2n[2].Open == ch2n[1].Close && ch2n[2].Open == 20, "tắt đặt lại: nến đầu ngày mới mở đúng bằng Close nến cuối ngày cũ");
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

        Console.WriteLine("[4b] Nạp lại nến dựng từ tick chưa khớp (sự cố viền chấm 2026-11-03)");
        Check(DeltaCore.TickMatches(-20, new TickBar { End = -20, N = 5 }) && !DeltaCore.TickMatches(-20, new TickBar { End = -12, N = 5 })
              && !DeltaCore.TickMatches(0, new TickBar { End = 0, N = 0 }), "TickMatches: khớp / lệch / không có tick");
        var rs = new long[8]; for (int i = 0; i < 8; i++) rs[i] = Tk(i);
        var rn = new[] { true, true, true, false, true, true, true, true };
        var rd = new double[] { 10, 20, 30, 0, 40, 50, 60, 70 };
        var rr = new Dictionary<long, TickBar>
        {
            [Tk(0)] = new TickBar { End = 10, N = 3 },     // khớp
            [Tk(1)] = new TickBar { End = 5, N = 3 },      // lệch → nạp lại
                                                           // Tk(2) thiếu → nạp lại
            [Tk(4)] = new TickBar { End = 40, N = 3 },     // khớp
                                                           // Tk(5..7) thiếu → nạp lại
        };
        var gr1 = DeltaCore.RetryGroups(rs, rn, rd, rr, 15);
        Check(gr1.Count == 2 && gr1[0][0] == 1 && gr1[0][1] == 2 && gr1[1][0] == 5 && gr1[1][1] == 7, "nhóm nến chưa khớp: [1-2] và [5-7]; bỏ nến không cần (3) và nến đã khớp");
        var gr2 = DeltaCore.RetryGroups(rs, rn, rd, rr, 2);
        Check(gr2.Count == 3 && gr2[1][0] == 5 && gr2[1][1] == 6 && gr2[2][0] == 7 && gr2[2][1] == 7, "nhóm dài bị cắt theo maxBars");
        rr[Tk(1)] = new TickBar { End = 20, N = 3 }; rr[Tk(2)] = new TickBar { End = 30, N = 3 };
        for (int i = 5; i < 8; i++) rr[Tk(i)] = new TickBar { End = rd[i], N = 3 };
        Check(DeltaCore.RetryGroups(rs, rn, rd, rr, 15).Count == 0, "nạp lại khớp hết → không còn nhóm nào");

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

        StrengthTests(dir);

        Console.WriteLine($"\n=> {ok} OK, {fail} FAIL");
        return fail == 0 ? 0 : 1;
    }

    // nến từng-nến (Open = 0) có sẵn đỉnh/đáy
    static CumBar Bar(int min, double close, double hi, double lo, RangeSrc src = RangeSrc.Quantower)
        => new CumBar { TimeUtcTicks = Tk(min), Open = 0, Close = close, Delta = close,
                        High = Math.Max(Math.Max(hi, 0), close), Low = Math.Min(Math.Min(lo, 0), close), Src = src };
    // nến không có râu (lịch sử không dựng được từ tick): High/Low = 0..delta
    static CumBar Flat(int min, double close) => Bar(min, close, 0, 0, RangeSrc.None);
    // n nến nền có |delta| = v (xen kẽ dấu, không râu) rồi nối thêm các nến cần xét
    static CumBar[] Chain(int n, double v, params CumBar[] tail)
    {
        var l = new List<CumBar>();
        for (int i = 0; i < n; i++) l.Add(Flat(i, i % 2 == 0 ? v : -v));
        for (int j = 0; j < tail.Length; j++) { var c = tail[j]; c.TimeUtcTicks = Tk(n + j); l.Add(c); }
        return l.ToArray();
    }

    static void StrengthTests(string dir)
    {
        Console.WriteLine("[6] Lực áp đảo trong nến — Push / ToneOf");
        // ca của người học: đầu nến sell đè xuống −30, sau đó buy vào +50 → đóng +20 (thân ngắn, râu dưới dài)
        DeltaCore.Push(20, 20, -30, out var b1, out var s1);
        Check(b1 == 50 && s1 == 0, $"−30 rồi +50 → đóng +20: buy = Close−Low = 50, sell = High−Close = 0 (được {b1}/{s1})");
        Check(DeltaCore.ToneOf(b1, s1, 25) == 1, "ca −30 → +20 với ngưỡng 25: XANH (delta cuối 20 < 25 nhưng quãng buy đẩy lên 50 ≥ 25)");
        Check(DeltaCore.ToneOf(Math.Max(20, 0), 0, 25) == 0, "cùng delta cuối +20 mà KHÔNG có râu dưới: xám (chỉ 20 < 25)");
        DeltaCore.Push(-10, 0, -45, out var b2, out var s2);
        Check(b2 == 35 && s2 == 10 && DeltaCore.ToneOf(b2, s2, 20) == 1, "delta cuối ÂM −10 nhưng đáy −45: buy 35 > sell 10 → XANH (như cột 06:04 trên chart CORVEN)");
        DeltaCore.Push(-10, 60, -12, out var b3, out var s3);
        Check(s3 == 70 && b3 == 2 && DeltaCore.ToneOf(b3, s3, 20) == -1, "lên +60 rồi sập về −10: sell 70 → ĐỎ");
        DeltaCore.Push(5, 40, -40, out var b4, out var s4);
        Check(DeltaCore.ToneOf(b4, s4, 20) == 1 && b4 == 45 && s4 == 35, "giằng co hai chiều +40/−40 đóng +5: buy 45 > sell 35 → xanh (bên thắng quãng lớn hơn)");
        DeltaCore.Push(0, 40, -40, out var b5, out var s5);
        Check(DeltaCore.ToneOf(b5, s5, 20) == 0, "giằng co đều +40/−40 đóng 0: buy = sell = 40 → XÁM (không bên nào áp đảo)");
        Check(DeltaCore.ToneOf(25, 0, 25) == 1 && DeltaCore.ToneOf(0, 25, 25) == -1, "ca biên: quãng ĐÚNG BẰNG ngưỡng → có màu (≥)");
        Check(DeltaCore.ToneOf(24.99, 0, 25) == 0, "ca biên: dưới ngưỡng một chút → xám");
        DeltaCore.Push(0, 0, 0, out var b6, out var s6);
        Check(b6 == 0 && s6 == 0 && DeltaCore.ToneOf(b6, s6, 5) == 0, "nến delta 0 phẳng → xám");
        Check(DeltaCore.ToneOf(10, 0, 0) == 0 && DeltaCore.ToneOf(10, 0, double.NaN) == 0, "ngưỡng 0/NaN (chưa có nền) → xám, không tô bừa");
        DeltaCore.Push(-20, 7, 3, out var b7, out var s7);
        Check(b7 == 0 && s7 == 27, "High/Low sai phía (hi < delta? lo > 0) vẫn được kẹp quanh Open=0 và Close");

        Console.WriteLine("[7] StrengthTones — ngưỡng thích nghi theo N nến trước");
        // nền 15 nến |delta| = 10 → ngưỡng = 1,25 × 10 = 12,5
        var t1 = DeltaCore.StrengthTones(Chain(15, 10, Flat(0, 11), Flat(0, 13), Flat(0, -40)), 15, 1.25, 5);
        Check(t1[15] == 0, "delta NHỎ: +11 < 12,5 → xám (CORVEN: 'delta dương nhưng nhỏ thì không đánh được')");
        Check(t1[16] == 1, "delta TO: +13 ≥ 12,5 → xanh");
        Check(t1[17] == -1, "−40 → đỏ");
        // cùng +30 nhưng bối cảnh khác nhau
        var quiet = DeltaCore.StrengthTones(Chain(15, 10, Flat(0, 30)), 15, 1.25, 5);
        var busy = DeltaCore.StrengthTones(Chain(15, 50, Flat(0, 30)), 15, 1.25, 5);
        Check(quiet[15] == 1 && busy[15] == 0, "THÍCH NGHI: +30 sau đoạn vắng (TB 10) → xanh; sau đoạn sôi (TB 50) → xám");
        // ca người học trong chuỗi: nền TB 20 → ngưỡng 25; đóng +20 có râu dưới −30
        var uc = DeltaCore.StrengthTones(Chain(15, 20, Bar(0, 20, 20, -30), Flat(0, 20)), 15, 1.25, 5);
        Check(uc[15] == 1, "chuỗi: −30 → +20 (râu dưới dài) → XANH");
        Check(uc[16] == 0, "chuỗi: +20 không râu, cùng nền → xám");
        // nến lịch sử thiếu đỉnh/đáy: rơi về quy tắc theo delta cuối
        var hist = DeltaCore.StrengthTones(Chain(15, 20, Flat(0, -26), Flat(0, -24)), 15, 1.25, 5);
        Check(hist[15] == -1 && hist[16] == 0, "nến THIẾU râu (Src None): chỉ xét |delta cuối| — −26 đỏ, −24 xám");
        // dựng bằng BuildChain thật: cùng nến, có/không có tick → màu khác
        var raw = new List<RawBar>();
        for (int i = 0; i < 15; i++) raw.Add(new RawBar { TimeUtcTicks = Tk(i), HasVa = true, Volume = 100, Trades = 40, Delta = i % 2 == 0 ? 20 : -20, QtMax = 20, QtMin = 20 });
        raw.Add(new RawBar { TimeUtcTicks = Tk(15), HasVa = true, Volume = 120, Trades = 60, Delta = 20, QtMax = 20, QtMin = 20 });   // Quantower: mồi (Max=Min=Delta)
        var noTick = DeltaCore.BuildChain(raw, null, true, false, 7, 300);
        var withTick = DeltaCore.BuildChain(raw, new Dictionary<long, TickBar> { [Tk(15)] = new TickBar { End = 20, Hi = 21, Lo = -30, N = 60 } }, true, false, 7, 300);
        Check(DeltaCore.StrengthTones(noTick, 15, 1.25, 5)[15] == 0, "BuildChain không tick: nến +20 thiếu râu → xám (không bịa râu)");
        Check(withTick[15].Src == RangeSrc.Ticks && DeltaCore.StrengthTones(withTick, 15, 1.25, 5)[15] == 1, "BuildChain có tick (đáy −30): cùng nến → xanh");
        // khởi động: chưa đủ 5 nến nền → xám
        var warm = DeltaCore.StrengthTones(Chain(4, 10, Flat(0, 200)), 15, 1.25, 5);
        Check(warm[4] == 0, "khởi động: mới 4 nến nền (< 5) → xám dù delta 200");
        var warm5 = DeltaCore.StrengthTones(Chain(5, 10, Flat(0, 200)), 15, 1.25, 5);
        Check(warm5[5] == 1, "đủ 5 nến nền → bắt đầu tô (nền = TB các nến đang có)");
        // nến rỗng không vào nền, không có màu
        var em = Chain(15, 10, Flat(0, 12)).ToList();   // nền đúng 10 → ngưỡng 12,5; nếu nến rỗng tính là 0 thì ngưỡng 11,7 → 12 sẽ bị tô sai
        em.Insert(10, new CumBar { TimeUtcTicks = Tk(100), Empty = true });
        var emT = DeltaCore.StrengthTones(em.ToArray(), 15, 1.25, 5);
        Check(emT[10] == 0 && emT[16] == 0, "nến rỗng (không VA): màu 0, không làm loãng nền (+12 vẫn xám)");
        // sàn tối thiểu lúc thị trường vắng
        var fl = DeltaCore.StrengthTones(Chain(15, 2, Flat(0, 4), Flat(0, 6)), 15, 1.25, 5);
        Check(fl[15] == 0 && fl[16] == 1, "sàn tối thiểu 5 hợp đồng: TB 2 → ngưỡng 5 (không phải 2,5): 4 xám, 6 xanh");
        // cửa sổ trượt: nến to cũ ra khỏi cửa sổ
        var roll = new List<CumBar> { Flat(0, 300) };
        for (int i = 1; i <= 15; i++) roll.Add(Flat(i, i % 2 == 0 ? 10 : -10));
        roll.Add(Flat(16, 13));
        var rT = DeltaCore.StrengthTones(roll.ToArray(), 15, 1.25, 5);
        Check(rT[16] == 1, "cửa sổ trượt 15 nến: nến 300 đã ra khỏi nền → +13 xanh");
        var rT2 = DeltaCore.StrengthTones(roll.ToArray(), 16, 1.25, 5);
        Check(rT2[16] == 0, "cùng chuỗi, nền 16 nến (còn nến 300) → +13 xám");
        // nến đang xét không tự nâng ngưỡng của mình
        var self = DeltaCore.StrengthTones(Chain(15, 10, Flat(0, 1000)), 15, 1.25, 5);
        Check(self[15] == 1, "nến cực to không tự đưa mình vào nền (nền chỉ gồm nến TRƯỚC)");
        // cộng dồn: High/Low/Close tính tương đối Open → màu giống chế độ từng nến
        var rawC = new List<RawBar>();
        double[] dd = { 10, -10, 10, -10, 10, -10, 12, -9, 30, -40, 5, 20 };
        for (int i = 0; i < dd.Length; i++) rawC.Add(new RawBar { TimeUtcTicks = Tk(i), HasVa = true, Volume = 100, Trades = 50, Delta = dd[i], QtMax = Math.Max(dd[i], 0) + (i == 11 ? 1 : 3), QtMin = Math.Min(dd[i], 0) - (i == 11 ? 30 : 2) });
        var tp = DeltaCore.StrengthTones(DeltaCore.BuildChain(rawC, null, true, false, 7, 300), 15, 1.25, 5);
        var tc = DeltaCore.StrengthTones(DeltaCore.BuildChain(rawC, null, false, false, 7, 300), 15, 1.25, 5);
        Check(tp.SequenceEqual(tc), "chuỗi cộng dồn cho cùng màu với chuỗi từng nến (tính tương đối Open)");
        Check(DeltaCore.StrengthTones(new CumBar[0], 15, 1.25, 5).Length == 0 && DeltaCore.StrengthTones(null, 15, 1.25, 5).Length == 0, "chuỗi rỗng/null → mảng rỗng, không lỗi");

        Console.WriteLine("[8] Số liệu THẬT: tỷ lệ xanh/đỏ/xám mỗi phiên phải hợp lý (xám là đa số 'yếu')");
        string f2 = Directory.Exists(dir) ? Directory.GetFiles(dir, "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv").FirstOrDefault() : null;
        if (f2 == null) { Console.WriteLine("  (bỏ qua: không thấy file xuất 90 ngày)"); return; }
        var lines = File.ReadLines(f2); var hdr = lines.First().Split(',');
        int ix(string n) => Array.IndexOf(hdr, n);
        int iD = ix("delta"), iV = ix("volume"), iDt = ix("datetime");
        var rawR = new List<RawBar>();
        foreach (var ln in lines.Skip(1))
        {
            var p = ln.Split(',');
            var dt = DateTime.Parse(p[iDt], CultureInfo.InvariantCulture);
            if (dt < new DateTime(2026, 8, 25)) continue;     // GCZ26 đã là hợp đồng chính (dày)
            double v = double.Parse(p[iV], CultureInfo.InvariantCulture);
            double d = double.Parse(p[iD], CultureInfo.InvariantCulture);
            rawR.Add(new RawBar { TimeUtcTicks = DateTime.SpecifyKind(dt, DateTimeKind.Utc).Ticks, HasVa = true, Volume = v, Trades = 2, Delta = d, QtMax = d, QtMin = d });
        }
        var chR = DeltaCore.BuildChain(rawR, null, true, false, 7, 300);
        var tR = DeltaCore.StrengthTones(chR, 15, 1.25, 5);
        int nR = 0, gR = 0, rR = 0; var perDay = new Dictionary<long, int[]>();
        for (int i = 0; i < chR.Length; i++)
        {
            if (chR[i].Empty) continue;
            nR++; if (tR[i] > 0) gR++; else if (tR[i] < 0) rR++;
            long dk = DeltaCore.DayKey(chR[i].TimeUtcTicks, 7, 300);
            if (!perDay.TryGetValue(dk, out var a)) perDay[dk] = a = new int[2];
            a[0]++; if (tR[i] == 0) a[1]++;
        }
        var shares = perDay.Values.Where(a => a[0] >= 300).Select(a => a[1] * 100.0 / a[0]).ToList();
        double gray = 100.0 * (nR - gR - rR) / nR;
        Console.WriteLine($"  {nR:N0} nến · xanh {100.0 * gR / nR:0.0}% · đỏ {100.0 * rR / nR:0.0}% · xám {gray:0.0}% · xám/phiên {shares.Min():0}%–{shares.Max():0}% ({shares.Count} phiên)");
        Check(nR > 40000, "đọc đủ dữ liệu thật");
        Check(gray > 55 && gray < 85, "xám là đa số nhưng không áp đảo tuyệt đối (55–85%)");
        Check(shares.Min() > 50 && shares.Max() < 90, "mọi phiên: xám 50–90% (ngưỡng thích nghi giữ tỷ lệ ổn định qua phiên vắng/sôi)");
        Check(Math.Abs(gR - rR) < 0.15 * (gR + rR), "xanh ≈ đỏ (không lệch hệ thống về một phía)");
    }
}
