// Unit test Benzo Trader (logic thuần, không cần Quantower chạy). Chạy:  dotnet run --project benzo-trader/tests
// Program.cs: lõi chung (mô phỏng, thống kê + nhãn trung thực, mốc reset, caption Telegram, cache + guard, engine).
// TestsCorven.cs: setup CORVEN — 12 ca plan mục 4 + 2 test cache mục 10.5 + hồi quy 97 lệnh TRAIN.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text.RegularExpressions;
using BenzoTraderNs;

static partial class Program
{
    static int _fail, _ok;
    static void Check(bool ok, string name, string detail = "")
    {
        if (ok) { _ok++; Console.WriteLine($"  OK   {name}"); }
        else { _fail++; Console.WriteLine($"  FAIL {name} {detail}"); }
    }
    static bool Near(double a, double b, double eps = 1e-9) => Math.Abs(a - b) < eps;

    static readonly DateTime T0 = new DateTime(2026, 10, 21, 3, 0, 0, DateTimeKind.Utc);   // 10:00 VN: ngoài khung mở ảo
    static BarData Bar(int i, double o, double h, double l, double c) =>
        new BarData { Idx = i, Time = T0.AddMinutes(i), O = o, H = h, L = l, C = c, Vol = 10 };
    static Signal Buy(double e = 100, double sl = 98, double tp = 104, char setup = 'A') =>
        new Signal { Setup = setup, Side = 1, Entry = e, Sl = sl, Tp = tp, Reason = "thử" };
    static Signal Sell(double e = 100, double sl = 102, double tp = 96) =>
        new Signal { Setup = 'B', Side = -1, Entry = e, Sl = sl, Tp = tp, Reason = "thử" };

    static string Tmp(string name)
    {
        string d = Path.Combine(Path.GetTempPath(), "benzo_tests");
        Directory.CreateDirectory(d);
        string p = Path.Combine(d, name);
        if (File.Exists(p)) File.Delete(p);
        return p;
    }

    static void TestSimulate()
    {
        Console.WriteLine("[1] Mô phỏng lệnh (StepBar/Simulate/TIME, MFE/MAE)");
        var bars = new List<BarData> { Bar(0, 100, 100, 100, 100), Bar(1, 100, 101, 99, 100), Bar(2, 100, 104.5, 100, 104) };
        var s = Buy();
        Check(BenzoCore.Simulate(s, bars, 0) && s.Outcome == "TP", "buy chạm TP", s.Outcome);
        Check(Near(s.R, (4 - 0.2) / 2.0), "R TP đã trừ chi phí 0,2", s.R.ToString());
        Check(s.ExitTime == bars[2].Time, "ExitTime = giờ mở nến chạm");
        Check(Near(s.MfeR, 4.5 / 2) && Near(s.MaeR, 0.5), "MFE/MAE theo R qua mọi nến tới nến thoát", $"{s.MfeR} {s.MaeR}");
        s = Buy();
        BenzoCore.Simulate(s, new List<BarData> { Bar(0, 100, 100, 100, 100), Bar(1, 100, 100, 97.5, 98) }, 0);
        Check(s.Outcome == "SL" && Near(s.R, -(2 + 0.2) / 2.0), "buy chạm SL: R = -(rủi ro+chi phí)/rủi ro", s.R.ToString());
        s = Buy();
        BenzoCore.Simulate(s, new List<BarData> { Bar(0, 100, 100, 100, 100), Bar(1, 100, 105, 97, 100) }, 0);
        Check(s.Outcome == "SL", "cùng nến chạm cả SL và TP => SL", s.Outcome);
        s = Sell();
        BenzoCore.Simulate(s, new List<BarData> { Bar(0, 100, 100, 100, 100), Bar(1, 100, 100, 95, 96) }, 0);
        Check(s.Outcome == "TP" && Near(s.R, (4 - 0.2) / 2.0), "sell chạm TP", s.R.ToString());
        s = Buy();
        bool done = BenzoCore.Simulate(s, new List<BarData> { Bar(0, 100, 100, 100, 100), Bar(1, 100, 101, 99, 100.5) }, 0);
        Check(!done && s.Outcome == "OPEN" && s.R == 0, "không chạm gì => OPEN");
        BenzoCore.CloseTime(s, Bar(1, 100, 101, 99, 100.5));
        Check(s.Outcome == "TIME" && s.IsClosed && Near(s.R, (0.5 - 0.2) / 2.0), "đóng TIME tại giá đóng nến cuối phiên", s.R.ToString());
        s = Buy();
        BenzoCore.Simulate(s, new List<BarData> { Bar(0, 100, 105, 97, 100) }, 0);
        Check(s.Outcome == "OPEN", "nến vào KHÔNG được tính (mô phỏng từ nến sau)");
    }

    static void TestStatsAndLabels()
    {
        Console.WriteLine("[2] Thống kê thế A/B + nhãn trung thực (plan 10.3, so đúng chữ)");
        Signal Closed(char the, string outc, double r, int min) { var x = Buy(setup: the); x.Time = T0.AddMinutes(min); x.Outcome = outc; x.R = r; return x; }
        var sigs = new List<Signal>
        {
            Closed('A', "TP", 1.9, 0), Closed('A', "SL", -1.1, 10), Closed('B', "SL", -1.1, 20), Closed('B', "TIME", 0.4, 30),
            Closed('B', "OPEN", 0, 40),
        };
        var st = BenzoCore.ComputeStats(sigs);
        Check(st.Total.N == 4 && st.Total.Wins == 2 && st.Total.Open == 1, "tổng: 4 đã đóng (TIME R>0 = thắng), 1 mở");
        Check(st.A.N == 2 && st.B.N == 2 && Near(st.B.SumR, -0.7), "theo thế A / B");
        var ls = BenzoCore.TableLines(st);
        Check(ls.Count == 4, "bảng đúng 4 dòng", ls.Count.ToString());
        var rx = new Regex(@"^BENZO CORVEN corven-6 · \d+ lệnh · WR \d+ % · [+−]?\d+,\d+R( · \d+ đang mở)?$");
        Check(rx.IsMatch(ls[0]) && ls[0].EndsWith(" · 1 đang mở"), "dòng 1 khớp mẫu plan 12.2-Q3 (có '· k đang mở' khi k > 0)", ls[0]);
        Check(ls[1] == "Fail Break · 2 · WR 50 % · +0,8R", "dòng thế A", ls[1]);
        Check(ls[2] == "Break · 2 · WR 50 % · −0,7R", "dòng thế B", ls[2]);
        Check(ls[3] == "Backtest 35 phiên: −0,07R/lệnh, chưa có lợi thế (vào ngẫu nhiên −0,09R) · chạy thử, không phải khuyến nghị", "dòng 4 nhãn backtest đúng chữ", ls[3]);
        var empty = BenzoCore.TableLines(BenzoCore.ComputeStats(new Signal[0]));
        Check(empty.Count == 4 && empty[3] == CorvenParams.BacktestLine, "dòng 4 LUÔN hiện kể cả khi chưa có lệnh");
        Check(CorvenParams.TeleWarn == "⚠ Chưa có lợi thế đo được (−0,07R/lệnh, 35 phiên)", "dòng cảnh báo Telegram đúng chữ");
        // lint thuật ngữ (plan 4e): buy/sell giữ tiếng Anh, không "mua/bán", không "volatility"
        var all = new[] { CorvenParams.BacktestLine, CorvenParams.TeleWarn, ls[0], ls[1], ls[2] };
        Check(!all.Any(x => x.Contains(" mua") || x.Contains(" bán") || x.ToLower().Contains("volatility")), "lint thuật ngữ nhãn");
    }

    static void TestCaption()
    {
        Console.WriteLine("[4] Caption Telegram CORVEN (plan mục 2 + 10.3)");
        var s = new Signal
        {
            Setup = 'B', Side = -1, Entry = 4126.6, Sl = 4129.1, Tp = 4121.6, RangeLo = 4127.3, RangeHi = 4132.5, Edge = 4127.4, Zone = "canh",
            NSigns = 2, Reason = "Δ ngược giá ΣΔ -62/2 nến · bóng đỏ 18 @4127,3 (3,6× nền)", RAvail = 1.92, CfBody = 0.6,
        };
        BenzoCore.Finalize(s, "GCZ26", new DateTime(2026, 11, 5, 17, 23, 0, DateTimeKind.Utc));
        var ls = BenzoCore.ComposeOpen(s, "GCZ26", 7, 1, 1).Split('\n');
        Check(ls.Length == 5, "5 dòng (4 dòng plan mục 2 + cảnh báo)", ls.Length.ToString());
        Check(ls[0] == "🔴 SELL · CORVEN Break · GCZ26 · 00:23 VN", "dòng 1", ls[0]);
        Check(ls[1] == "Mốc: cạnh dưới 4127,4 vừa phá (range 4127,3–4132,5)", "dòng 2 mốc", ls[1]);
        Check(ls[2] == "Dấu hiệu (2): Δ ngược giá ΣΔ -62/2 nến · bóng đỏ 18 @4127,3 (3,6× nền)", "dòng 3 dấu hiệu có số", ls[2]);
        Check(ls[3] == "CF 00:23 thân 0,6 giá · Vào 4126,6 · SL 4129,1 (2,5) · TP 4121,6 (2R, R sẵn 1,9)", "dòng 4 lệnh", ls[3]);
        Check(ls[4] == CorvenParams.TeleWarn, "dòng cuối cảnh báo chưa có lợi thế", ls[4]);
        var a = new Signal { Setup = 'A', Side = -1, Entry = 4135.6, Sl = 4138.3, Tp = 4130.2, RangeLo = 4130.9, RangeHi = 4135.8, Edge = 4135.8, Zone = "canh" };
        Check(BenzoCore.TheName('A') == "Fail Break" && BenzoCore.TheName('B') == "Break", "tên hiển thị: A = Fail Break, B = Break");
        Check(BenzoCore.ShortDisplay(new Signal { Setup = 'B', Side = 1, Short = "B buy · stacked 4 mức + trap" }) == "Break buy · stacked 4 mức + trap"
              && BenzoCore.ShortDisplay(new Signal { Setup = 'A', Side = -1, Short = "A sell · Δ ngược" }) == "Fail Break sell · Δ ngược"
              && BenzoCore.ShortDisplay(new Signal { Setup = 'B', Side = 1, Short = "Break buy · trap" }) == "Break buy · trap"
              && BenzoCore.ShortDisplay(new Signal { Setup = 'A', Side = 1, Short = "" }) == "Fail Break buy", "nhãn chart: cache cũ 'B buy …' → 'Break buy …', nhãn mới giữ nguyên");
        Check(BenzoCore.MocLine(a, 1) == "Mốc: cạnh trên 4135,8 fail break (range 4130,9–4135,8)", "mốc thế A", BenzoCore.MocLine(a, 1));
        s.Outcome = "TP"; s.R = 1.9; s.ExitTime = s.Time.AddMinutes(9);
        Check(BenzoCore.ComposeClose(s, 7, 1) == "✅ CORVEN Break +1,9R · 00:23→00:32", "tin đóng thắng: giờ MỞ nến vào → giờ MỞ nến thoát", BenzoCore.ComposeClose(s, 7, 1));
        // plan 12.1 #6: giờ caption = giờ MỞ nến CF = time_vn của CSV (lệnh GCZ26 2026-07-29 15:52 UTC thế A sell ⇒ 22:52 VN)
        var a1 = new Signal { Setup = 'A', Side = -1, Entry = 4070.3, Sl = 4072.6, Tp = 4065.7, RangeLo = 4065.0, RangeHi = 4070.6, Edge = 4070.6, Zone = "canh", NSigns = 2, Reason = "x · y" };
        BenzoCore.Finalize(a1, "GCZ26", new DateTime(2026, 7, 29, 15, 52, 0, DateTimeKind.Utc));
        var capA = BenzoCore.ComposeOpen(a1, "GCZ26", 7, 1, 1).Split('\n');
        string keyVn = SignalCsv.Key(a1, 7).Split(',')[1].Substring(11);
        Check(capA[0].EndsWith(" · 22:52 VN") && capA[3].StartsWith("CF 22:52 ") && keyVn == "22:52", "caption ghi 22:52 VN = time_vn của SignalCsv.Key", capA[0] + " | " + keyVn);
        Check(BenzoCore.ComposeCancel(a1, 7, 1).Contains(" 22:52 huỷ"), "tin huỷ cũng giờ mở nến");
        // plan 12.2-Q5: TIME thắng/thua theo dấu R (trùng Python wr = (r > 0))
        var tW = Buy(); tW.Outcome = "TIME"; tW.R = 0.3; var tL = Buy(); tL.Outcome = "TIME"; tL.R = -0.2;
        var stT = BenzoCore.ComputeStats(new[] { tW, tL });
        Check(stT.Total.Wins == 1 && stT.Total.Losses == 1, "TIME R +0,3 ⇒ thắng, R −0,2 ⇒ thua");
        tW.Time = tW.ExitTime = s.Time; tL.Time = tL.ExitTime = s.Time; tW.Setup = tL.Setup = 'A';
        Check(BenzoCore.ComposeClose(tW, 7, 1).StartsWith("✅") && BenzoCore.ComposeClose(tL, 7, 1).StartsWith("🛑"), "tin đóng TIME ✅/🛑 theo cùng dấu R");
        s.Outcome = "TIME"; s.R = -0.3;
        Check(BenzoCore.ComposeClose(s, 7, 1).StartsWith("🛑 CORVEN Break −0,3R") && BenzoCore.ComposeClose(s, 7, 1).EndsWith("(hết phiên)"), "tin đóng TIME");
        var mp = TeleClient.BuildPhoto("123", new byte[] { 1, 2, 3 }, "cap");
        string body = mp.ReadAsStringAsync().Result;
        Check(body.Contains("name=chat_id") && body.Contains("name=caption") && body.Contains("name=photo") && body.Contains("image/png"), "multipart sendPhoto đủ trường");
        var tc = new TeleClient { Token = "SECRET123:abc" };
        Check(!tc.Redact("lỗi tại https://api.telegram.org/botSECRET123:abc/sendPhoto").Contains("SECRET123"), "log che token");
    }

    static void TestCache()
    {
        Console.WriteLine("[5] SignalCache round-trip + guard khớp nến + tên file có khung");
        string p = Tmp("cache.jsonl");
        var c = new SignalCache(p, "v1");
        var s = Buy(); s.CfH = 101; s.CfL = 99; BenzoCore.Finalize(s, "GCZ26", T0.AddMinutes(5));
        c.PutSignal(s);
        c.MarkRange(T0.Ticks, T0.AddMinutes(9).Ticks);
        c.MarkRange(T0.AddMinutes(10).Ticks, T0.AddMinutes(19).Ticks);
        var c2 = new SignalCache(p, "v1"); c2.Load();
        Check(c2.Count == 1 && c2.TryGet(T0.AddMinutes(5).Ticks, out var r) && r.Id == s.Id && Near(r.Entry, 100) && Near(r.CfH, 101), "nạp lại đúng tín hiệu (có H/L nến CF)");
        Check(c2.Covers(T0.AddMinutes(7).Ticks) && c2.Covers(T0.AddMinutes(19).Ticks) && !c2.Covers(T0.AddMinutes(20).Ticks), "khoảng đã dò [first,last]");
        File.AppendAllText(p, "{hỏng chưa ghi xong\n");
        var c3 = new SignalCache(p, "v1"); c3.Load();
        Check(c3.Count == 1, "dòng hỏng bị bỏ qua, không chết file");
        var c4 = new SignalCache(p, "v2"); c4.Load();
        Check(c4.Count == 0 && !c4.Covers(T0.AddMinutes(5).Ticks), "đổi phiên bản => bỏ cache cũ");
        Check(SignalCache.FitsBar(s, Bar(5, 99.5, 101, 99, 100), 0.1) && !SignalCache.FitsBar(s, Bar(5, 99.5, 101.2, 99, 100), 0.1)
              && !SignalCache.FitsBar(s, Bar(5, 99.5, 101, 99, 100.1), 0.1), "FitsBar: H lệch > 1 tick hoặc giá vào lệch > nửa tick ⇒ không khớp");
        Check(BenzoCore.CacheFileName("GCZ26", "Time", 1) == "cache_GCZ26_Time_1m.jsonl" && BenzoCore.CacheFileName("GCZ26", "Time", 15) != BenzoCore.CacheFileName("GCZ26", "Time", 1),
              "tên cache có số phút (M1 ≠ M15)");
        Check(BenzoCore.CacheVersion() == "corven-6-sl5.0-f1-b1" && BenzoCore.CacheVersion(3.0, false, true) == "corven-6-sl3.0-f0-b1" && BenzoCore.CacheVersion(5.0, true, false) == "corven-6-sl5.0-f1-b0" && BenzoCore.CacheVersion(5.1) != BenzoCore.CacheVersion(), "khoá cache = LogicVersion + SL tối đa + công tắc Fail Break + công tắc Break (không còn hậu tố chặn giờ)");
        // plan 12.1-7c: RangeT0/RangeT1 round-trip; dòng cache cũ thiếu 2 trường vẫn nạp được (= 0 ⇒ không vẽ), guard không đổi
        string p7 = Tmp("cache7c.jsonl");
        var c7 = new SignalCache(p7, "v1");
        var s7 = Buy(); s7.CfH = 101; s7.CfL = 99; s7.RangeT0 = T0.Ticks; s7.RangeT1 = T0.AddMinutes(30).Ticks; BenzoCore.Finalize(s7, "GCZ26", T0.AddMinutes(30));
        c7.PutSignal(s7); c7.MarkRange(T0.Ticks, T0.AddMinutes(40).Ticks);
        var c7b = new SignalCache(p7, "v1"); c7b.Load();
        Check(c7b.TryGet(s7.Time.Ticks, out var r7) && r7.RangeT0 == T0.Ticks && r7.RangeT1 == T0.AddMinutes(30).Ticks, "RangeT0/RangeT1 lưu và nạp lại");
        var lines7 = File.ReadAllLines(p7).Select(x => x.Contains("\"K\":\"sig\"") ? Regex.Replace(x, @",""RangeT[01]"":\d+", "") : x).ToArray();
        File.WriteAllLines(p7, lines7);
        var c7c = new SignalCache(p7, "v1"); c7c.Load();
        Check(c7c.TryGet(s7.Time.Ticks, out var r7c) && r7c.RangeT0 == 0 && SignalCache.FitsBar(r7c, Bar(30, 99.5, 101, 99, 100), 0.1), "dòng cache cũ (không có RangeT0/T1) vẫn nạp, guard vẫn khớp");
        // plan 12.1 #2: nhiều khoảng niêm phong rời nhau
        string p8 = Tmp("cache_iv.jsonl");
        var c8 = new SignalCache(p8, "v1");
        c8.MarkRange(T0.Ticks, T0.AddMinutes(9).Ticks); c8.MarkRange(T0.AddMinutes(20).Ticks, T0.AddMinutes(29).Ticks); c8.MarkRange(T0.AddMinutes(25).Ticks, T0.AddMinutes(35).Ticks);
        var c8b = new SignalCache(p8, "v1"); c8b.Load();
        Check(c8b.Intervals.Count == 2 && !c8b.Covers(T0.AddMinutes(15).Ticks) && c8b.Covers(T0.AddMinutes(33).Ticks), "cache giữ khoảng rời nhau (không phủ đoạn giữa), gộp khoảng chồng nhau");
    }

    sealed class CountDet : ISetupDetector
    {
        public char Setup => 'C'; public int Calls; public Func<int, Signal> F;
        public Signal TryDetect(SetupContext ctx, int i) { Calls++; return F(i); }
    }

    sealed class PeekDet : ISetupDetector
    {
        public static bool Threw; public char Setup => 'C';
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

    static Signal Sig(char the = 'A') => new Signal { Setup = the, Side = 1, Entry = 100, Sl = 98, Tp = 104, Reason = "t", CfH = 100.5, CfL = 99.5 };

    static void TestEngine()
    {
        Console.WriteLine("[6] Engine: 1 lệnh mở, niêm phong, chống nhìn trước, hết phiên");
        string p = Tmp("cache_eng.jsonl");
        var cache = new SignalCache(p); cache.Load();
        var det = new CountDet { F = i => i == 10 || i == 12 || i == 40 ? Sig(i == 40 ? 'B' : 'A') : null };
        var eng = NewEngine(cache, det);
        eng.Bars[15] = Bar(15, 100, 104.5, 100, 104);   // chạm TP lệnh nến 10
        eng.Bars[45] = Bar(45, 100, 100, 97.5, 98);     // chạm SL lệnh nến 40
        var res = eng.Advance(99);
        Check(eng.Signals.Count == 2, "2 lệnh (nến 12 bị bỏ vì lệnh 10 còn mở)", eng.Signals.Count.ToString());
        Check(eng.Signals[0].Outcome == "TP" && eng.Signals[1].Outcome == "SL", "kết quả TP rồi SL");
        Check(res.Opened.Count == 2 && res.Closed.Count == 2, "Advance trả đúng số mở/đóng");
        Check(eng.Signals[1].Setup == 'B' && eng.Signals[1].Id.Contains("|B|B"), "Setup = thế do detector điền, Id gắn thế+hướng", eng.Signals[1].Id);
        Check(eng.Signals[0].BarIdx == 10 && eng.Signals[0].Time == T0.AddMinutes(10) && eng.Signals[0].Phien == "Á", "Time = giờ mở nến vào; phiên Á");

        var cache2 = new SignalCache(p); cache2.Load();
        var det2 = new CountDet { F = i => throw new Exception("không được dò lại nến đã niêm phong") };
        var eng2 = NewEngine(cache2, det2);
        eng2.Bars[15] = eng.Bars[15]; eng2.Bars[45] = eng.Bars[45];
        var r2 = eng2.Advance(99);
        Check(det2.Calls == 0 && !r2.CacheInvalid, "sau reload nến đã niêm phong KHÔNG dò lại", det2.Calls.ToString());
        Check(eng2.Signals.Select(x => x.Id).SequenceEqual(eng.Signals.Select(x => x.Id)) && eng2.Signals[0].Outcome == "TP", "tín hiệu + kết quả giống hệt sau reload");

        var eng5 = NewEngine(null, new PeekDet());
        eng5.Advance(20);
        Check(PeekDet.Threw && eng5.Processed == 21, "detector không nhìn được nến sau closedIdx (ClosedBars ném lỗi)");

        // hết phiên: lệnh còn mở qua khoảng trống > 30′ ⇒ TIME tại giá đóng nến cuối; lệnh vào ĐÚNG nến cuối phiên ⇒ huỷ
        var det6 = new CountDet { F = i => i == 10 || i == 49 ? Sig() : null };
        var eng6 = new BenzoEngine("GCZ26", 0.1, null, new[] { det6 });
        for (int i = 0; i < 30; i++) eng6.Bars.Add(Bar(i, 100, 100.5, 99.5, i == 29 ? 101 : 100));
        for (int i = 30; i < 50; i++) { var b = Bar(i, 100, 100.5, 99.5, 100); b.Time = T0.AddMinutes(i + 60); eng6.Bars.Add(b); }   // khoảng trống 61′
        var r6 = eng6.Advance(49);
        Check(eng6.Signals[0].Outcome == "TIME" && eng6.Signals[0].ExitTime == eng6.Bars[29].Time && Near(eng6.Signals[0].R, (1 - 0.2) / 2), "TIME ở nến cuối phiên", eng6.Signals[0].Outcome);
        var f6 = eng6.FinishSession();
        Check(f6.Cancelled.Count == 1 && eng6.Signals.Count == 1, "lệnh vào ở nến cuối (hết dữ liệu) bị huỷ");
    }

    static int Main()
    {
        TestSimulate(); TestStatsAndLabels(); TestCaption(); TestCache(); TestEngine(); TestFixes12();
        TestsCorven();
        TestsCorven2();
        Console.WriteLine($"\n{_ok} OK, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }
}
