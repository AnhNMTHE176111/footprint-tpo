// Test CHẠY THẬT cho BenzoCore (biên dịch chính ../BenzoCore.cs). Chạy:
//   dotnet run --project benzo-trader/tests
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using BenzoTraderNs;

static class Tests
{
    static int _fail, _ok;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 && !ok ? "  -> " + detail : ""));
        if (ok) _ok++; else _fail++;
    }
    static bool Near(double a, double b, double eps = 1e-9) => Math.Abs(a - b) < eps;

    static readonly DateTime T0 = new DateTime(2026, 10, 21, 3, 0, 0, DateTimeKind.Utc);   // 10:00 VN: ngoài khung mở ảo
    static BarData Bar(int i, double o, double h, double l, double c) =>
        new BarData { Idx = i, Time = T0.AddMinutes(i), O = o, H = h, L = l, C = c, Vol = 100, Delta = 10 };
    static Signal Buy(double e = 100, double sl = 98, double tp = 104, char setup = 'A') =>
        new Signal { Setup = setup, Side = 1, Entry = e, Sl = sl, Tp = tp, Reason = "thử" };
    static Signal Sell(double e = 100, double sl = 102, double tp = 96) =>
        new Signal { Setup = 'B', Side = -1, Entry = e, Sl = sl, Tp = tp, Reason = "thử" };
    static string Tmp(string name)
    {
        string d = Path.Combine(Path.GetTempPath(), "benzo_test_" + Guid.NewGuid().ToString("N").Substring(0, 8));
        Directory.CreateDirectory(d);
        return Path.Combine(d, name);
    }

    static void TestSimulate()
    {
        Console.WriteLine("[1] Simulate (SL/TP/cùng nến/chi phí)");
        var s = Buy(); var bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 101, 99.5, 100.5), Bar(2, 100.5, 104.2, 100, 104) };
        Check(BenzoCore.Simulate(s, bars, 0) && s.Outcome == "TP", "BUY chạm TP", s.Outcome);
        Check(Near(s.R, (4 - 0.2) / 2.0), "R TP đã trừ chi phí 0,2", s.R.ToString());
        Check(s.ExitTime == bars[2].Time, "ExitTime = giờ mở nến chạm");

        s = Buy(); bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 100.5, 97.9, 98) };
        BenzoCore.Simulate(s, bars, 0);
        Check(s.Outcome == "SL" && Near(s.R, -(2 + 0.2) / 2.0), "BUY chạm SL: R = -(rủi ro+chi phí)/rủi ro", s.R.ToString());

        s = Buy(); bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 104.5, 97.5, 101) };
        BenzoCore.Simulate(s, bars, 0);
        Check(s.Outcome == "SL", "cùng nến chạm cả SL và TP => SL", s.Outcome);

        s = Sell(); bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 100.5, 95.9, 96) };
        BenzoCore.Simulate(s, bars, 0);
        Check(s.Outcome == "TP" && Near(s.R, (4 - 0.2) / 2.0), "SELL chạm TP", s.R.ToString());
        s = Sell(); bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 102, 99, 101) };
        BenzoCore.Simulate(s, bars, 0);
        Check(s.Outcome == "SL", "SELL: H chạm đúng SL => SL (biên bằng)");

        s = Buy(); bars = new[] { Bar(0, 100, 100, 100, 100), Bar(1, 100, 101, 99, 100) };
        bool done = BenzoCore.Simulate(s, bars, 0);
        Check(!done && s.Outcome == "OPEN" && s.R == 0, "không chạm gì => OPEN");

        s = Buy(); bars = new[] { Bar(0, 100, 105, 90, 100), Bar(1, 100, 101, 99, 100) };
        BenzoCore.Simulate(s, bars, 0);
        Check(s.Outcome == "OPEN", "nến vào KHÔNG được tính (mô phỏng từ nến sau)");
    }

    static void TestStats()
    {
        Console.WriteLine("[2] Thống kê theo setup + mốc reset");
        DateTime t(int m) => T0.AddMinutes(m);
        var list = new List<Signal>
        {
            new Signal { Setup='A', Side=1, Time=t(0),  Outcome="TP", R=2.8 },
            new Signal { Setup='A', Side=1, Time=t(10), Outcome="TP", R=2.8 },
            new Signal { Setup='A', Side=1, Time=t(20), Outcome="SL", R=-1.1 },
            new Signal { Setup='B', Side=-1, Time=t(30), Outcome="SL", R=-1.1 },
            new Signal { Setup='D', Side=1, Time=t(40), Outcome="TP", R=1.9 },
            new Signal { Setup='C', Side=1, Time=t(50), Outcome="OPEN" },
        };
        var st = BenzoCore.ComputeStats(list, null);
        Check(st.Total.N == 5 && st.Total.Wins == 3 && st.Total.Losses == 2 && st.Total.Open == 1, "tổng n/thắng/thua/mở");
        Check(Near(st.Total.SumR, 2.8 + 2.8 - 1.1 - 1.1 + 1.9), "tổng R", st.Total.SumR.ToString());
        Check(st.By[0].N == 3 && st.By[0].Wins == 2 && Near(st.By[0].WinRate, 66.6666666, 1e-4), "A: 3 lệnh, 2 thắng, WR 66,7%");
        Check(st.By[1].N == 1 && st.By[1].Losses == 1, "B: 1 thua");
        Check(st.By[2].N == 0 && st.By[2].Open == 1, "C: chưa đóng lệnh nào, 1 mở");
        var lines = BenzoCore.TableLines(st, new[] { true, true, false, true });
        Check(lines.Count == 5, "bảng đúng 5 dòng", lines.Count.ToString());
        Check(lines[0].StartsWith("BENZO · Tổng 5 lệnh · 3 thắng · 2 thua · 60,0% · +5,3R"), "dòng tổng đúng mẫu", lines[0]);
        Check(lines[1].StartsWith("A Phá hồi") && lines[1].Contains("3 · 2/1 · 67% · +4,5R"), "dòng A", lines[1]);
        Check(lines[3].Contains("(tắt)"), "setup tắt có nhãn (tắt)", lines[3]);

        var st2 = BenzoCore.ComputeStats(list, t(25));
        Check(st2.Total.N == 2 && st2.By[0].N == 0, "mốc reset: chỉ đếm lệnh sau mốc", st2.Total.N.ToString());
        Check(st2.Total.Open == 1, "mốc reset: lệnh mở sau mốc vẫn được đếm là mở");
    }

    static void TestResetMark()
    {
        Console.WriteLine("[3] Lưu / đọc mốc đặt lại thống kê");
        string p = Tmp("reset_X.txt");
        Check(BenzoCore.LoadResetMark(p) == null, "chưa có file => null");
        var now = new DateTime(2026, 10, 21, 15, 30, 12, DateTimeKind.Utc);
        BenzoCore.SaveResetMark(p, now);
        var back = BenzoCore.LoadResetMark(p);
        Check(back.HasValue && back.Value.Ticks == now.Ticks, "round-trip đúng tick", back?.ToString());
        File.WriteAllText(p, "rác");
        Check(BenzoCore.LoadResetMark(p) == null, "file rác => null (không chết)");
    }

    static void TestCaption()
    {
        Console.WriteLine("[4] Caption Telegram");
        var s = new Signal
        {
            Setup = 'A', Side = 1, Entry = 4193.1, Sl = 4190.6, Tp = 4200.6,
            Reason = "phá VAH Âu 4192,0 lúc 20:10 (M5 đóng ngoài), hồi hình U 4 nến",
            Time = new DateTime(2026, 10, 21, 13, 23, 0, DateTimeKind.Utc),   // mở 13:23 UTC => đóng 13:24 => 20:24 VN
        };
        string c = BenzoCore.ComposeOpen(s, "GCZ26", 7, 1, 1);
        var ls = c.Split('\n');
        Check(ls[0] == "🟢 BUY · A Phá hồi · GCZ26 · 20:24 VN", "dòng 1", ls[0]);
        Check(ls[1].StartsWith("Lý do: phá VAH Âu"), "dòng 2 có lý do", ls[1]);
        Check(ls[2] == "Vào 4193,1 · SL 4190,6 (2,5 giá) · TP 4200,6 (3R)", "dòng 3 đúng mẫu plan", ls[2]);
        var sell = new Signal { Setup = 'C', Side = -1, Entry = 100, Sl = 102, Tp = 96, Reason = "x", Time = s.Time };
        Check(BenzoCore.ComposeOpen(sell, "GCZ26", 7, 1, 1).StartsWith("🔴 SELL · C Fade cạnh"), "SELL dùng 🔴 SELL");
        var longReason = new Signal { Setup = 'D', Side = 1, Entry = 1, Sl = 0, Tp = 2, Reason = new string('x', 3000), Time = s.Time };
        Check(BenzoCore.ComposeOpen(longReason, "G", 7, 1, 1).Length <= 1024, "caption không vượt 1024 ký tự");

        s.Outcome = "TP"; s.R = 2.8; s.ExitTime = new DateTime(2026, 10, 21, 13, 50, 0, DateTimeKind.Utc);
        Check(BenzoCore.ComposeClose(s, 7, 1) == "✅ A Phá hồi +2,8R · 20:24→20:51", "tin đóng thắng", BenzoCore.ComposeClose(s, 7, 1));
        s.Outcome = "SL"; s.R = -1.1;
        Check(BenzoCore.ComposeClose(s, 7, 1).StartsWith("🛑 A Phá hồi −1,1R"), "tin đóng thua", BenzoCore.ComposeClose(s, 7, 1));

        using var mp = TeleClient.BuildPhoto("123", new byte[] { 137, 80, 78, 71 }, "chú thích");
        string body = mp.ReadAsStringAsync().Result;
        Check(body.Contains("name=chat_id") && body.Contains("name=caption") && body.Contains("name=photo") && body.Contains("image/png"),
              "multipart có chat_id + caption + photo(png)");
        var tc = new TeleClient { Token = "SECRET123:abc" };
        Check(!tc.Redact("lỗi tại https://api.telegram.org/botSECRET123:abc/sendPhoto").Contains("SECRET123"), "log che token");
    }

    static void TestCache()
    {
        Console.WriteLine("[5] SignalCache round-trip");
        string p = Tmp("cache.jsonl");
        var c = new SignalCache(p, "v1");
        var s = Buy(); BenzoCore.Finalize(s, "GCZ26", T0.AddMinutes(5));
        c.PutSignal(s);
        c.MarkRange(T0.Ticks, T0.AddMinutes(9).Ticks);
        c.MarkRange(T0.AddMinutes(10).Ticks, T0.AddMinutes(19).Ticks);   // mở rộng
        var c2 = new SignalCache(p, "v1"); c2.Load();
        Check(c2.Count == 1 && c2.TryGet(T0.AddMinutes(5).Ticks, out var r) && r.Id == s.Id && Near(r.Entry, 100) && r.Reason == "thử", "nạp lại đúng tín hiệu");
        Check(c2.Covers(T0.AddMinutes(7).Ticks) && c2.Covers(T0.AddMinutes(19).Ticks) && !c2.Covers(T0.AddMinutes(20).Ticks) && !c2.Covers(T0.AddMinutes(-1).Ticks), "khoảng đã dò [first,last]");
        File.AppendAllText(p, "{hỏng chưa ghi xong\n");
        var c3 = new SignalCache(p, "v1"); c3.Load();
        Check(c3.Count == 1 && c3.Covers(T0.AddMinutes(12).Ticks), "dòng hỏng bị bỏ qua, không chết file");
        var c4 = new SignalCache(p, "v2"); c4.Load();
        Check(c4.Count == 0 && !c4.Covers(T0.AddMinutes(5).Ticks), "đổi LogicVersion => bỏ cache cũ");
        Check(s.Id == $"GCZ26|{T0.AddMinutes(5):yyyyMMddHHmm}|A|B", "Id tất định theo giờ mở nến+setup+side", s.Id);
    }

    sealed class CountDet : ISetupDetector
    {
        public char Setup => 'B'; public int Calls; public Func<int, Signal> F;
        public Signal TryDetect(SetupContext ctx, int i) { Calls++; return F(i); }
    }

    sealed class PeekDet : ISetupDetector
    {
        public static bool Threw; public char Setup => 'A';
        public Signal TryDetect(SetupContext ctx, int i)
        {
            try { var x = ctx.Bars[i + 1]; } catch (IndexOutOfRangeException) { Threw = true; }
            if (ctx.Bars.Count != i + 1) throw new Exception("Bars.Count phải = closedIdx+1");
            return null;
        }
    }

    static BenzoEngine NewEngine(SignalCache cache, params ISetupDetector[] d)
    {
        var e = new BenzoEngine("GCZ26", 0.1, cache, d);
        for (int i = 0; i < 100; i++) e.Bars.Add(Bar(i, 100, 100.5, 99.5, 100));   // phẳng: không chạm gì
        return e;
    }

    static void TestEngine()
    {
        Console.WriteLine("[6] Engine: 1 lệnh mở, niêm phong, chống nhìn trước");
        string p = Tmp("cache_eng.jsonl");
        var cache = new SignalCache(p); cache.Load();
        var det = new CountDet { F = i => i == 10 || i == 12 || i == 40 ? new Signal { Side = 1, Entry = 100, Sl = 98, Tp = 104, Reason = "t" } : null };
        var eng = NewEngine(cache, det);
        eng.Bars[15] = Bar(15, 100, 104.5, 100, 104);   // chạm TP lệnh nến 10
        eng.Bars[45] = Bar(45, 100, 100, 97.5, 98);     // chạm SL lệnh nến 40
        var res = eng.Advance(99);
        Check(eng.Signals.Count == 2, "2 lệnh (nến 12 bị bỏ vì lệnh 10 còn mở)", eng.Signals.Count.ToString());
        Check(eng.Signals[0].Outcome == "TP" && eng.Signals[1].Outcome == "SL", "kết quả TP rồi SL", string.Join(",", eng.Signals.Select(x => x.Outcome)));
        Check(res.Opened.Count == 2 && res.Closed.Count == 2, "Advance trả đúng số mở/đóng");
        Check(eng.Signals[0].Setup == 'B' && eng.Signals[0].Id.Contains("|B|B"), "Setup lấy từ detector, Id gắn setup+side", eng.Signals[0].Id);
        Check(eng.Signals[0].BarIdx == 10 && eng.Signals[0].Time == T0.AddMinutes(10), "Time = giờ mở nến vào");

        // reload: engine mới + cache nạp lại => KHÔNG gọi detector, kết quả giữ nguyên
        var cache2 = new SignalCache(p); cache2.Load();
        var det2 = new CountDet { F = i => throw new Exception("không được dò lại nến đã niêm phong") };
        var eng2 = NewEngine(cache2, det2);
        eng2.Bars[15] = eng.Bars[15]; eng2.Bars[45] = eng.Bars[45];
        eng2.Advance(99);
        Check(det2.Calls == 0, "sau reload nến đã niêm phong KHÔNG dò lại", det2.Calls.ToString());
        Check(eng2.Signals.Count == 2 && eng2.Signals.Select(x => x.Id).SequenceEqual(eng.Signals.Select(x => x.Id)), "tín hiệu giống hệt sau reload");
        Check(eng2.Signals[0].Outcome == "TP" && eng2.Signals[1].Outcome == "SL", "kết quả tính lại từ nến khớp");

        // nến mới (ngoài khoảng đã dò) vẫn được dò
        var det3 = new CountDet { F = i => null };
        var cache3 = new SignalCache(p); cache3.Load();
        var eng3 = NewEngine(cache3, det3);
        eng3.Bars[15] = eng.Bars[15]; eng3.Bars[45] = eng.Bars[45];   // để các lệnh cũ đóng lại như trước
        eng3.Bars.Add(Bar(100, 100, 100.5, 99.5, 100)); eng3.Bars.Add(Bar(101, 100, 100.5, 99.5, 100));
        eng3.Advance(101);
        Check(det3.Calls == 2, "chỉ 2 nến mới (100,101) bị dò", det3.Calls.ToString());

        // công tắc tắt: detector không được gọi
        var det4 = new CountDet { F = i => new Signal { Side = 1, Entry = 100, Sl = 98, Tp = 104 } };
        var eng4 = NewEngine(null, det4); eng4.IsEnabled = c => false;
        eng4.Advance(99);
        Check(det4.Calls == 0 && eng4.Signals.Count == 0, "setup tắt => không dò");

        // chống nhìn trước
        var eng5 = NewEngine(null, new PeekDet());
        eng5.Advance(20);
        Check(PeekDet.Threw, "detector không nhìn được nến sau closedIdx (ClosedBars ném lỗi)");
        Check(eng5.Processed == 21, "Processed đúng", eng5.Processed.ToString());
    }

#if DEBUG
    static void TestDemo()
    {
        Console.WriteLine("[7] DemoDetector (chỉ DEBUG) + CSV log");
        var eng = NewEngine(null, new DemoDetector());
        eng.Bars[40] = Bar(40, 100, 104.5, 100, 104);   // lệnh nến 30 chạm TP
        eng.Advance(99);
        Check(eng.Signals.Count >= 2 && eng.Signals[0].BarIdx == 30 && eng.Signals[0].Outcome == "TP", "demo bắn mỗi 30 nến, TP ở nến 40", eng.Signals.Count.ToString());
        string csv = Tmp("signals_GCZ26.csv");
        var open = eng.Signals.Last();
        SignalCsv.Merge(csv, new[] { eng.Signals[0], open });
        var lines = File.ReadAllLines(csv);
        Check(lines[0] == "time_utc,setup,side,entry,sl,tp,zone,reason,outcome,exit_time,r", "CSV header đúng");
        Check(lines.Length == 3 && lines[1].Contains(",TP,") && lines[1].EndsWith("1.9"), "dòng đã đóng có outcome+r", lines.Length > 1 ? lines[1] : "");
        // cập nhật: lệnh mở nay đóng => dòng được thay, không nhân đôi
        var s = open.Clone(); BenzoCore.StepBar(s, Bar(99, 100, 110, 90, 100));
        int before = File.ReadAllLines(csv).Length;
        SignalCsv.Merge(csv, new[] { s });
        var after = File.ReadAllLines(csv);
        Check(after.Length == before && after.Any(l => l.StartsWith(SignalCsv.Key(s)) && l.Contains(",SL,")), "Merge cập nhật dòng khi đóng, không trùng", string.Join("|", after));
        Check(SignalCsv.ToLine(new Signal { Setup = 'A', Side = 1, Time = T0, Reason = "a, \"b\"", Zone = "z", Entry = 1, Sl = 0, Tp = 2 }).Contains("\"a, \"\"b\"\"\""), "CSV escape dấu phẩy + ngoặc kép");
    }
#endif

    // ---------------------------------------------------------------- kernel / vùng / detector
    static void TestKernel()
    {
        Console.WriteLine("[8] BenzoKernel: giờ Mỹ, SmOf, ValueArea, Risk, CF");
        Check(BenzoKernel.UsDst(new DateTime(2026, 10, 21, 0, 0, 0, DateTimeKind.Utc)), "21/10/2026 Mỹ còn giờ mùa hè");
        Check(!BenzoKernel.UsDst(new DateTime(2026, 11, 2, 0, 0, 0, DateTimeKind.Utc)), "02/11/2026 Mỹ đã giờ mùa đông");
        Check(!BenzoKernel.UsDst(new DateTime(2026, 3, 8, 6, 59, 0, DateTimeKind.Utc)) && BenzoKernel.UsDst(new DateTime(2026, 3, 8, 7, 0, 0, DateTimeKind.Utc)), "mốc CN thứ 2 tháng 3 07:00 UTC");
        Check(BenzoKernel.SmOf(new DateTime(2026, 10, 21, 22, 0, 0, DateTimeKind.Utc), 7) == 0, "22:00 UTC = 05:00 VN ⇒ sm 0 (mùa hè)");
        Check(BenzoKernel.SmOf(new DateTime(2026, 10, 21, 12, 0, 0, DateTimeKind.Utc), 7) == 840, "12:00 UTC = 19:00 VN ⇒ sm 840 (mùa hè)");
        Check(BenzoKernel.SmOf(new DateTime(2026, 12, 21, 13, 0, 0, DateTimeKind.Utc), 7) == 840, "13:00 UTC = 20:00 VN ⇒ sm 840 (mùa đông, neo giờ Mỹ lùi +1h)");
        Check(BenzoKernel.PhaseOf(0) == "A" && BenzoKernel.PhaseOf(449) == "A" && BenzoKernel.PhaseOf(450) == "EU" && BenzoKernel.PhaseOf(840) == "US" && BenzoKernel.PhaseOf(1380) == "OFF", "phase A/EU/US/OFF");
        var pr = new double[] { 1, 2, 3, 4, 5, 6, 7, 8, 9 };
        var w = new double[] { 1, 2, 4, 8, 20, 8, 4, 2, 1 };
        Check(BenzoKernel.ValueArea(pr, w, out double poc, out double vah, out double val) && poc == 5 && vah == 7 && val == 3, "ValueArea 70% (POC 5, 3..7)", $"{poc} {vah} {val}");
        Check(!BenzoKernel.ValueArea(new double[0], new double[0], out _, out _, out _), "ValueArea rỗng ⇒ false");
        var bars = new List<BarData>();
        for (int i = 0; i < 6; i++) bars.Add(new BarData { Idx = i, Time = T0.AddMinutes(i), O = 100, H = 100.5, L = 99.5, C = 100 });
        var r = BenzoRisk.Calc(bars, 5, 1, 99.0, 2.0);
        Check(r != null && Near(r.Sl, 98.7) && Near(r.Tp, 102.6) && Near(r.Risk, 1.3), "Risk BUY: SL = struct − 0,3, TP 2R", r == null ? "null" : $"{r.Sl} {r.Tp}");
        var r2 = BenzoRisk.Calc(bars, 5, 1, 99.9, 2.0);
        Check(r2 != null && r2.FloorApplied && Near(r2.Risk, 1.0), "Risk: sàn = biên độ nến cao nhất 5 nến (1,0)", r2 == null ? "null" : r2.Risk.ToString());
        Check(BenzoRisk.Calc(bars, 5, 1, 95.0, 2.0) == null, "Risk: SL > 4 giá ⇒ bỏ lệnh");
        var r3 = BenzoRisk.Calc(bars, 5, -1, 101.0, 3.0);
        Check(r3 != null && Near(r3.Sl, 101.3) && Near(r3.Tp, 96.1), "Risk SELL: SL = struct + 0,3, TP 3R", r3 == null ? "null" : $"{r3.Sl} {r3.Tp}");
        var cf = new BarData { O = 100, H = 101, L = 99.9, C = 100.8, Delta = 20 };
        Check(BenzoKernel.IsConfirmBar(cf, 1, 15) && !BenzoKernel.IsConfirmBar(cf, -1, 15) && !BenzoKernel.IsConfirmBar(cf, 1, 25) && !BenzoKernel.IsConfirmBar(cf, 1, double.NaN),
            "IsConfirmBar: đúng chiều, |Δ| ≥ trung vị, NaN ⇒ false");
    }

    /// <summary>Phiên 1 (400 nến, giá tuần hoàn 100..110) rồi phiên 2: nến benign quanh 105 + một nến "phá hụt" cạnh VAH hôm qua.</summary>
    static BenzoEngine BuildDay2(Func<double, BarData> poke, bool news = false)
    {
        var det = new DetectorC();
        var eng = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det });
        if (news) eng.IsNewsBlocked = _ => true;
        var lv = new Dictionary<int, List<LevelVol>>();
        eng.GetLevels = i => lv.TryGetValue(i, out var l) ? (IReadOnlyList<LevelVol>)l : Array.Empty<LevelVol>();
        DateTime d1 = new DateTime(2026, 10, 19, 22, 0, 0, DateTimeKind.Utc);
        int idx = 0;
        for (int k = 0; k < 400; k++, idx++)
        {
            double c = 100.0 + (k % 100) * 0.1;
            eng.Bars.Add(new BarData { Idx = idx, Time = d1.AddMinutes(k), O = c, H = c + 0.1, L = c - 0.1, C = c, Vol = 10, Delta = 1 });
            lv[idx] = new List<LevelVol> { new LevelVol(Math.Round(c, 1), 5, 5) };
        }
        DateTime d2 = new DateTime(2026, 10, 20, 22, 0, 0, DateTimeKind.Utc);
        for (int k = 0; k < 20; k++, idx++)
        {
            double c = 105 + (k % 2 == 0 ? 0.1 : -0.1);
            double hi = k == 3 ? c + 1.5 : c + 0.2, lo = k == 3 ? c - 1.5 : c - 0.2;   // nến 3 là nến dài nhất phiên
            eng.Bars.Add(new BarData { Idx = idx, Time = d2.AddMinutes(k), O = c, H = hi, L = lo, C = c, Vol = 10, Delta = 2 });
        }
        eng.Advance(idx - 1);
        var pk = poke(eng.Zones.YdVah);
        pk.Idx = idx; pk.Time = d2.AddMinutes(20);
        eng.Bars.Add(pk);
        eng.Advance(idx);
        return eng;
    }

    static void TestZonesAndC()
    {
        Console.WriteLine("[9] BenzoZones (phiên, VA hôm qua, VWAP, chế độ) + DetectorC trên dữ liệu tổng hợp");
        var eng = BuildDay2(vah => new BarData { O = vah - 0.1, H = vah + 0.4, L = vah - 0.55, C = vah - 0.5, Vol = 10, Delta = -9 });
        var z = eng.Zones;
        Check(z.SessionNo == 1 && z.SessionStartIdx == 400, "tách phiên theo khoảng trống > 30 phút", $"{z.SessionNo} {z.SessionStartIdx}");
        Check(z.HasYd && z.YdVah >= z.YdPoc && z.YdPoc >= z.YdVal && z.YdVah - z.YdVal >= 6.0 && z.YdVah <= 110.0 && z.YdVal >= 100.0, "VA phiên hôm qua có POC/VAH/VAL hợp lý", $"{z.YdVal} {z.YdPoc} {z.YdVah}");
        Check(Math.Abs(z.VwapD - 105) < 0.5 && z.VwapW > 100 && z.VwapW < 110, "VWAP ngày reset ở phiên mới (quanh 105)", z.VwapD.ToString());
        Check(z.ModeC.Mode == "BALANCE" && z.ModeDef.Mode == "NA", "chế độ: C (band hôm qua) = BALANCE, mặc định (chưa có VA Âu/IB) = NA", $"{z.ModeC.Mode}/{z.ModeDef.Mode}");
        Check(eng.Signals.Count == 1 && eng.Signals[0].Side == -1 && eng.Signals[0].Setup == 'C', "C: râu xuyên VAH ≥ 2 tick, đóng lại trong, Δ âm ⇒ SELL", eng.Signals.Count.ToString());
        if (eng.Signals.Count == 1)
        {
            var s = eng.Signals[0];
            Check(Near(s.Tp - s.Entry, -2 * (s.Sl - s.Entry)) && s.Sl > s.Entry, "C: TP = 2R cố định, SL trên râu", $"{s.Entry} {s.Sl} {s.Tp}");
            Check(s.Reason.Contains("VAH hôm qua") && s.Reason.Contains("tick"), "Reason tiếng Việt có số thật", s.Reason);
        }
        var e2 = BuildDay2(vah => new BarData { O = vah - 0.1, H = vah + 0.4, L = vah - 0.55, C = vah - 0.5, Vol = 10, Delta = +9 });
        Check(e2.Signals.Count == 0, "C: Δ dương (không ủng hộ chiều vào) ⇒ không có tín hiệu");
        var e3 = BuildDay2(vah => new BarData { O = vah - 0.1, H = vah + 0.2, L = vah - 0.2, C = vah - 0.05, Vol = 10, Delta = -9 });
        Check(e3.Signals.Count == 0, "C: râu xuyên chỉ 1 tick (< 2 tick) ⇒ không có tín hiệu");
        var e4 = BuildDay2(vah => new BarData { O = vah - 0.1, H = vah + 2.0, L = vah - 1.8, C = vah - 1.7, Vol = 10, Delta = -9 });
        Check(e4.Signals.Count == 0, "C: nến xuyên là nến dài nhất phiên ⇒ loại");
        var e5 = BuildDay2(vah => new BarData { O = vah - 0.1, H = vah + 0.4, L = vah - 0.55, C = vah - 0.5, Vol = 10, Delta = -9 }, news: true);
        Check(e5.Signals.Count == 0, "tin USD mức cao ±15′ ⇒ không phát tín hiệu");
    }

    sealed class ObserveCount : IObservingDetector
    {
        public char Setup => 'A';
        public int Observed, Tried, OpenAt = -1;
        public void Observe(SetupContext ctx, int i) { Observed++; }
        public Signal TryDetect(SetupContext ctx, int i)
        {
            Tried++;
            return i == OpenAt ? new Signal { Side = 1, Entry = 100, Sl = 50, Tp = 150 } : null;
        }
    }

    static void TestObserve()
    {
        Console.WriteLine("[10] Engine: Observe chạy mọi nến, TryDetect chỉ khi không có lệnh mở");
        DateTime d2 = new DateTime(2026, 10, 20, 22, 0, 0, DateTimeKind.Utc);
        var cnt2 = new ObserveCount { OpenAt = 2 };
        var e3 = new BenzoEngine("X", 0.1, null, new ISetupDetector[] { cnt2 });
        for (int k = 0; k < 10; k++) e3.Bars.Add(new BarData { Idx = k, Time = d2.AddMinutes(k), O = 100, H = 100.2, L = 99.8, C = 100, Vol = 10 });
        e3.Advance(9);
        Check(cnt2.Observed == 10 && cnt2.Tried == 3 && e3.Signals.Count == 1, "có lệnh mở: vẫn Observe 10 nến, chỉ TryDetect 3 nến (0..2)", $"{cnt2.Observed}/{cnt2.Tried}");
        Check(e3.Zones.NewM5.Count <= 1 && e3.Zones.Idx == 9, "Zones theo kịp nến cuối");
    }

    /// <summary>Hồi quy trên dữ liệu thật (nếu có file 90d trong repo): số tín hiệu từng setup phải đúng như đã đối chiếu Python (parity).</summary>
    static void TestRealData()
    {
        Console.WriteLine("[11] Hồi quy trên file 90d GCZ26 (bỏ qua nếu không có file)");
        string root = null;
        for (var d = new DirectoryInfo(AppContext.BaseDirectory); d != null; d = d.Parent)
            if (Directory.Exists(Path.Combine(d.FullName, "data-export", "data-footprint"))) { root = d.FullName; break; }
        string bs = root == null ? null : Path.Combine(root, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
        if (bs == null || !File.Exists(bs + "_bars.csv") || !File.Exists(bs + ".csv")) { Console.WriteLine("  (không có file 90d — bỏ qua)"); return; }
        var inv = System.Globalization.CultureInfo.InvariantCulture;
        var bars = new List<BarData>(); var pos = new Dictionary<int, int>();
        foreach (var line in File.ReadLines(bs + "_bars.csv").Skip(1))
        {
            var f = line.Split(',');
            pos[int.Parse(f[0], inv)] = bars.Count;
            bars.Add(new BarData { Idx = bars.Count, Time = DateTime.ParseExact(f[1], "yyyy-MM-dd HH:mm:ss", inv), O = double.Parse(f[2], inv), H = double.Parse(f[3], inv), L = double.Parse(f[4], inv), C = double.Parse(f[5], inv), Vol = double.Parse(f[10], inv), Delta = double.Parse(f[11], inv) });
        }
        var levels = new List<LevelVol>[bars.Count];
        foreach (var line in File.ReadLines(bs + ".csv").Skip(1))
        {
            var f = line.Split(',');
            if (!pos.TryGetValue(int.Parse(f[0], inv), out int p)) continue;
            (levels[p] ??= new List<LevelVol>()).Add(new LevelVol(double.Parse(f[2], inv), double.Parse(f[3], inv), double.Parse(f[4], inv), double.Parse(f[5], inv)));
        }
        var exp = new Dictionary<char, int> { ['A'] = 18, ['B'] = 12, ['C'] = 101, ['D'] = 32 };
        foreach (var kv in exp)
        {
            ISetupDetector d = kv.Key switch { 'A' => new DetectorA(), 'B' => new DetectorB(), 'C' => new DetectorC(), _ => new DetectorD() };
            var e = new BenzoEngine("GCZ26", 0.1, null, new[] { d }) { GetLevels = i => (IReadOnlyList<LevelVol>)levels[i] ?? Array.Empty<LevelVol>() };
            foreach (var b in bars) e.Bars.Add(b);
            e.Advance(bars.Count - 1);
            Check(e.Signals.Count == kv.Value, $"setup {kv.Key}: {kv.Value} tín hiệu (= Python trừ các lệnh trong 19:20-20:30)", e.Signals.Count.ToString());
        }
    }

    static void TestVirtualOpen()
    {
        Console.WriteLine("[12] Luật mở ảo 19:20-20:30 VN (engine, trước TryDetect)");
        Check(BenzoCore.InVirtualOpen(860) && BenzoCore.InVirtualOpen(929) && !BenzoCore.InVirtualOpen(859) && !BenzoCore.InVirtualOpen(930), "mốc sm 860..929");
        // 12:30 UTC = 19:30 VN (trong khung) ; 03:00 UTC = 10:00 VN (ngoài khung)
        foreach (var (start, expect, name) in new[] { (new DateTime(2026, 10, 21, 12, 30, 0, DateTimeKind.Utc), 0, "trong 19:20-20:30 ⇒ không phát"),
                                                     (new DateTime(2026, 10, 21, 3, 0, 0, DateTimeKind.Utc), 1, "ngoài khung ⇒ vẫn phát") })
        {
            var det = new ObserveCount { OpenAt = 3 };
            var e = new BenzoEngine("X", 0.1, null, new ISetupDetector[] { det });
            for (int k = 0; k < 6; k++) e.Bars.Add(new BarData { Idx = k, Time = start.AddMinutes(k), O = 100, H = 100.2, L = 99.8, C = 100, Vol = 10 });
            e.Advance(5);
            Check(e.Signals.Count == expect, name, e.Signals.Count.ToString());
        }
    }

    static int Main()
    {
        TestSimulate(); TestStats(); TestResetMark(); TestCaption(); TestCache(); TestEngine();
        TestKernel(); TestZonesAndC(); TestObserve(); TestVirtualOpen(); TestRealData();
#if DEBUG
        TestDemo();
#endif
        Console.WriteLine($"\n{_ok} OK, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }
}
