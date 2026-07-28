// ============================================================================
//  Test cho FootprintCore — CHẠY THẬT trên Linux (không cần Quantower).
//    cd tests && dotnet run
//  Gồm cả 2 test "chống bug chết người":
//    • số cột header PHẢI khớp số cột dòng dữ liệu (lệch = CSV rác)
//    • tổng theo mức giá PHẢI khớp tổng của nến sau khi gộp tick/hàng
// ============================================================================

namespace FootprintExport
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Text;

    internal static class T
    {
        static int _pass, _fail;
        static readonly List<string> _fails = new();

        static void Ok(bool cond, string name)
        {
            if (cond) { _pass++; }
            else { _fail++; _fails.Add(name); Console.WriteLine("  ✗ FAIL: " + name); }
        }

        static void Eq<TV>(TV actual, TV expect, string name)
            => Ok(EqualityComparer<TV>.Default.Equals(actual, expect), $"{name}  (được '{actual}', mong '{expect}')");

        static void Near(double a, double b, double tol, string name)
            => Ok(Math.Abs(a - b) <= tol, $"{name}  (được {a}, mong {b} ±{tol})");

        static void Section(string s) => Console.WriteLine("\n== " + s);

        static int Main(string[] argv)
        {
            var inv = CultureInfo.InvariantCulture;
            // `dotnet run -- --sample <dir>`: sinh 2 file CSV MẪU bằng CHÍNH code FpCore thật,
            // để verify_export.py kiểm được cả đường ống ghi file (không chỉ logic trong bộ nhớ).
            if (argv.Length >= 2 && argv[0] == "--sample") return WriteSample(argv[1]);

            // ---------------------------------------------------------- digits
            Section("DigitsFromTick");
            Eq(FpCore.DigitsFromTick(0.1), 1, "tick 0.1 (vàng GC/MGC)");
            Eq(FpCore.DigitsFromTick(0.25), 2, "tick 0.25 (ES)");
            Eq(FpCore.DigitsFromTick(1), 0, "tick 1");
            Eq(FpCore.DigitsFromTick(0.01), 2, "tick 0.01");
            Eq(FpCore.DigitsFromTick(0.001), 3, "tick 0.001");
            Eq(FpCore.DigitsFromTick(0.5), 1, "tick 0.5");
            Eq(FpCore.DigitsFromTick(0.00000001), 8, "tick 1e-8 (crypto)");
            Eq(FpCore.DigitsFromTick(0), 2, "tick 0 -> fallback 2");
            Eq(FpCore.DigitsFromTick(-1), 2, "tick âm -> fallback 2");
            Eq(FpCore.DigitsFromTick(double.NaN), 2, "tick NaN -> fallback 2");

            // ------------------------------------------------------- tick index
            Section("ToTick / PriceOf");
            Eq(FpCore.ToTick(4040.3, 0.1), 40403L, "4040.3 / 0.1");
            Eq(FpCore.ToTick(4040.0, 0.1), 40400L, "4040.0 / 0.1");
            Eq(FpCore.ToTick(-1.5, 0.5), -3L, "giá âm");
            Eq(FpCore.ToTick(4040.35, 0.1), 40404L, "nửa tick làm tròn RA XA 0");
            Eq(FpCore.ToTick(100, 0), 0L, "tick 0 -> 0 (không chia cho 0)");
            // round-trip: chuỗi in ra phải bằng chuỗi của giá gốc
            for (double p = 4000.0; p < 4001.0; p += 0.1)
            {
                long t = FpCore.ToTick(p, 0.1);
                Eq(FpCore.FmtPrice(FpCore.PriceOf(t, 0.1), 1), FpCore.FmtPrice(p, 1), $"round-trip {p:0.0}");
            }

            // ------------------------------------------------------------ bucket
            Section("Bucket (gộp tick/hàng)");
            Eq(FpCore.Bucket(40403, 1), 40403L, "per=1 giữ nguyên");
            Eq(FpCore.Bucket(40403, 5), 40400L, "40403 -> 40400 (per 5)");
            Eq(FpCore.Bucket(40405, 5), 40405L, "40405 -> 40405");
            Eq(FpCore.Bucket(40409, 5), 40405L, "40409 -> 40405");
            Eq(FpCore.Bucket(-3, 5), -5L, "âm: -3 -> -5 (floor, KHÔNG truncate về 0)");
            Eq(FpCore.Bucket(-5, 5), -5L, "âm: -5 -> -5");
            Eq(FpCore.Bucket(-6, 5), -10L, "âm: -6 -> -10");
            // mọi tick trong cùng nhóm phải cho cùng bucket
            for (int per = 2; per <= 7; per++)
                for (long t = -20; t <= 20; t++)
                    Ok(FpCore.Bucket(t, per) <= t && t - FpCore.Bucket(t, per) < per,
                       $"bucket({t},{per}) nằm trong [t-per+1, t]");

            // --------------------------------------------------------- FmtPrice
            Section("FmtPrice (không được mất thông tin)");
            Eq(FpCore.FmtPrice(4040.3, 1), "4040.3", "1 chữ số");
            Eq(FpCore.FmtPrice(4040.0, 1), "4040.0", "giữ .0");
            Eq(FpCore.FmtPrice(4040.0, 0), "4040", "0 chữ số");
            Eq(FpCore.FmtPrice(4040.05, 1), "4040.05", "lệch nửa tick -> in ĐỦ, không làm tròn mất số");
            Eq(FpCore.FmtPrice(double.NaN, 1), "", "NaN -> rỗng");
            Ok(!FpCore.FmtPrice(1234567.8, 1).Contains(","), "KHÔNG có dấu phân cách nghìn (phá CSV)");
            Ok(!FpCore.FmtPrice(0.5, 8).Contains(","), "dấu thập phân là '.' bất kể locale");

            // ----------------------------------------------------------- FmtVol
            Section("FmtVol");
            Eq(FpCore.FmtVol(37), "37", "số nguyên in gọn");
            Eq(FpCore.FmtVol(-15), "-15", "delta âm");
            Eq(FpCore.FmtVol(0), "0", "không");
            Eq(FpCore.FmtVol(0.5), "0.5", "phân số (crypto)");
            Eq(FpCore.FmtVol(double.NaN), "0", "NaN -> 0");
            Eq(FpCore.FmtVol(double.PositiveInfinity), "0", "Inf -> 0");
            Ok(!FpCore.FmtVol(1e308).Contains("E"), "số cực lớn không ra dạng E (phá parser)");
            Ok(!FpCore.FmtVol(1234567).Contains(","), "KHÔNG phân cách nghìn");

            // -------------------------------------------------------- FixPrimer
            Section("FixPrimer (dọn giá trị MỒI của MaxDelta/MinDelta ở nến rỗng)");
            Eq(FpCore.FixPrimer(double.MinValue, 0), 0.0, "double.MinValue -> fallback");
            Eq(FpCore.FixPrimer(double.MaxValue, 0), 0.0, "double.MaxValue -> fallback");
            Eq(FpCore.FixPrimer(double.NaN, 7), 7.0, "NaN -> fallback");
            Eq(FpCore.FixPrimer(double.NegativeInfinity, 7), 7.0, "-Inf -> fallback");
            Eq(FpCore.FixPrimer(-42, 0), -42.0, "số thật giữ nguyên (kể cả âm)");
            Ok(!FpCore.FmtVol(FpCore.FixPrimer(double.MinValue, 0)).Contains("E"),
               "nến rỗng KHÔNG ghi -1.79E+308 vào CSV");

            // ---------------------------------------------------------- SepFrom
            Section("SepFrom");
            Eq(FpCore.SepFrom(","), ',', "phẩy");
            Eq(FpCore.SepFrom(";"), ';', "chấm phẩy (Excel VN)");
            Eq(FpCore.SepFrom("|"), '|', "gạch dọc");
            Eq(FpCore.SepFrom("t"), '\t', "t = tab");
            Eq(FpCore.SepFrom("x"), ',', "ký tự lạ -> phẩy");
            Eq(FpCore.SepFrom(""), ',', "rỗng -> phẩy");
            Eq(FpCore.SepFrom(null), ',', "null -> phẩy");

            // ------------------------------------------------ SỐ CỘT header/row
            Section("Số cột: header PHẢI khớp dòng dữ liệu");
            foreach (char sep in new[] { ',', ';', '|', '\t' })
            {
                int hL = FpCore.LevelsHeader(sep).Split(sep).Length;
                var sb = new StringBuilder();
                var lv = new FpLevel { Tick = 40403, BidVol = 3, AskVol = 4, Volume = 7, Delta = 1, Trades = 5, BuyTrades = 2, SellTrades = 3, MaxOneTrade = 2 };
                FpCore.AppendLevelRow(sb, sep, 0, "2026-07-01 10:00:00", 4040.3, lv, 1);
                int rL = sb.ToString().TrimEnd('\n').Split(sep).Length;
                Eq(rL, hL, $"levels: cột dòng == cột header (sep '{(sep == '\t' ? "tab" : sep.ToString())}')");

                int hB = FpCore.BarsHeader(sep).Split(sep).Length;
                var sb2 = new StringBuilder();
                var fb = new FpBar { Idx = 0, Dt = "2026-07-01 10:00:00", Open = 1, High = 2, Low = 0.5, Close = 1.5, Levels = 3, PocPrice = 4040.3 };
                FpCore.AppendBarRow(sb2, sep, fb, 1);
                int rB = sb2.ToString().TrimEnd('\n').Split(sep).Length;
                Eq(rB, hB, $"bars: cột dòng == cột header (sep '{(sep == '\t' ? "tab" : sep.ToString())}')");
            }
            Ok(FpCore.LevelsHeader(',') == "bar_idx,datetime,price,bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade",
               "tên cột levels đúng như tài liệu README");
            Ok(!FpCore.LevelsHeader(',').EndsWith(","), "header không có dấu phẩy đuôi");

            // ------------------------------------------------------- Aggregate
            Section("Aggregate (gộp N tick/hàng)");
            Eq(FpCore.Aggregate(null, 1).Count, 0, "null -> rỗng");
            Eq(FpCore.Aggregate(new List<FpLevel>(), 3).Count, 0, "rỗng -> rỗng");

            var raw = new List<FpLevel>
            {
                L(40402, bid: 5, ask: 3, tr: 4, mot: 2),
                L(40400, bid: 1, ask: 9, tr: 6, mot: 7),
                L(40405, bid: 2, ask: 2, tr: 2, mot: 1),
                L(40404, bid: 0, ask: 8, tr: 3, mot: 5),
            };
            var a1 = FpCore.Aggregate(raw, 1);
            Eq(a1.Count, 4, "per=1 giữ đủ 4 mức");
            Ok(a1.Select(x => x.Tick).SequenceEqual(new long[] { 40400, 40402, 40404, 40405 }), "per=1 SẮP TĂNG theo giá");

            var a5 = FpCore.Aggregate(raw, 5);
            Eq(a5.Count, 2, "per=5 -> 2 nhóm (40400-40404) & (40405-40409)");
            Eq(a5[0].Tick, 40400L, "nhóm 1 neo ở 40400");
            Eq(a5[1].Tick, 40405L, "nhóm 2 neo ở 40405");
            Eq(a5[0].BidVol, 6.0, "nhóm 1 bid = 5+1+0");
            Eq(a5[0].AskVol, 20.0, "nhóm 1 ask = 3+9+8");
            Eq(a5[0].Volume, 26.0, "nhóm 1 volume tổng");
            Eq(a5[0].Delta, 14.0, "nhóm 1 delta = ask-bid = 20-6");
            Eq(a5[0].Trades, 13, "nhóm 1 trades = 4+6+3");
            Eq(a5[0].MaxOneTrade, 7.0, "MaxOneTrade lấy MAX (không cộng)");
            Eq(a5[1].MaxOneTrade, 1.0, "nhóm 2 MaxOneTrade");

            // HỒI QUY: 2 giá khác nhau rơi vào CÙNG tick index (feed mịn hơn TickSize)
            // -> per=1 vẫn PHẢI gộp, không được ra 2 dòng trùng (bar_idx, price).
            var dup = new List<FpLevel> { L(40403, bid: 2, ask: 3, tr: 2, mot: 4), L(40403, bid: 1, ask: 1, tr: 1, mot: 9) };
            var dedup = FpCore.Aggregate(dup, 1);
            Eq(dedup.Count, 1, "per=1: tick trùng -> gộp thành 1 hàng (không ra 2 dòng cùng giá)");
            Eq(dedup[0].BidVol, 3.0, "per=1 trùng: bid cộng dồn");
            Eq(dedup[0].AskVol, 4.0, "per=1 trùng: ask cộng dồn");
            Eq(dedup[0].Trades, 3, "per=1 trùng: trades cộng dồn");
            Eq(dedup[0].MaxOneTrade, 9.0, "per=1 trùng: MaxOneTrade lấy max");

            // BẤT BIẾN: gộp không được làm mất/thêm khối lượng — thử ngẫu nhiên có seed
            Section("Aggregate — bất biến tổng (random, seed cố định)");
            var rnd = new Random(20260728);
            for (int trial = 0; trial < 300; trial++)
            {
                int n = rnd.Next(1, 40);
                var list = new List<FpLevel>(n);
                for (int i = 0; i < n; i++)
                    list.Add(L(rnd.Next(-50, 50), bid: rnd.Next(0, 100), ask: rnd.Next(0, 100),
                              tr: rnd.Next(0, 20), mot: rnd.Next(0, 30)));
                int per = rnd.Next(1, 9);
                var agg = FpCore.Aggregate(list, per);
                Near(agg.Sum(x => x.BidVol), list.Sum(x => x.BidVol), 1e-9, $"[{trial}] tổng bid giữ nguyên");
                Near(agg.Sum(x => x.AskVol), list.Sum(x => x.AskVol), 1e-9, $"[{trial}] tổng ask giữ nguyên");
                Near(agg.Sum(x => x.Volume), list.Sum(x => x.Volume), 1e-9, $"[{trial}] tổng volume giữ nguyên");
                Near(agg.Sum(x => x.Delta), list.Sum(x => x.Delta), 1e-9, $"[{trial}] tổng delta giữ nguyên");
                Eq(agg.Sum(x => x.Trades), list.Sum(x => x.Trades), $"[{trial}] tổng trades giữ nguyên");
                Near(agg.Max(x => x.MaxOneTrade), list.Max(x => x.MaxOneTrade), 1e-9, $"[{trial}] MaxOneTrade lớn nhất giữ nguyên");
                Ok(agg.Count <= list.Count, $"[{trial}] gộp không tăng số hàng");
                Ok(agg.Zip(agg.Skip(1), (x, y) => x.Tick < y.Tick).All(v => v), $"[{trial}] tăng dần & không trùng bucket");
                Ok(agg.All(x => x.Tick % per == 0 || per == 1), $"[{trial}] mọi bucket là bội của per");
            }

            // ------------------------------------------------------------- POC
            Section("PocIndex");
            Eq(FpCore.PocIndex(null), -1, "null -> -1");
            Eq(FpCore.PocIndex(new List<FpLevel>()), -1, "rỗng -> -1");
            var pl = new List<FpLevel> { L(1, bid: 1, ask: 1), L(2, bid: 5, ask: 5), L(3, bid: 2, ask: 2) };
            Eq(FpCore.PocIndex(pl), 1, "chọn mức volume lớn nhất");
            var tie = new List<FpLevel> { L(1, bid: 5, ask: 5), L(2, bid: 5, ask: 5) };
            Eq(FpCore.PocIndex(tie), 0, "bằng nhau -> mức GIÁ THẤP hơn (xác định, không random)");

            // -------------------------------------------------------- lọc ngày
            Section("TryParseDay / InRange");
            Ok(FpCore.TryParseDay("2026-07-01", out var d1) && d1 == new DateTime(2026, 7, 1), "yyyy-MM-dd");
            Ok(FpCore.TryParseDay("2026/07/01", out var d2) && d2 == new DateTime(2026, 7, 1), "yyyy/MM/dd");
            Ok(FpCore.TryParseDay("01/07/2026", out var d3) && d3 == new DateTime(2026, 7, 1), "dd/MM/yyyy (kiểu VN)");
            Ok(FpCore.TryParseDay("20260701", out var d4) && d4 == new DateTime(2026, 7, 1), "yyyyMMdd");
            Ok(!FpCore.TryParseDay("hom nay", out _), "chữ vớ vẩn -> false");
            Ok(!FpCore.TryParseDay("", out _), "rỗng -> false");
            Ok(!FpCore.TryParseDay(null, out _), "null -> false");
            Ok(!FpCore.TryParseDay("2026-13-45", out _), "ngày không tồn tại -> false");

            var from = new DateTime(2026, 7, 1);
            var to = new DateTime(2026, 7, 3);
            Ok(FpCore.InRange(new DateTime(2026, 7, 1, 0, 0, 0), from, to), "đúng đầu khoảng");
            Ok(FpCore.InRange(new DateTime(2026, 7, 3, 23, 59, 59), from, to), "HẾT ngày cuối vẫn trong khoảng");
            Ok(!FpCore.InRange(new DateTime(2026, 7, 4, 0, 0, 0), from, to), "sang ngày 4 -> ngoài");
            Ok(!FpCore.InRange(new DateTime(2026, 6, 30, 23, 59, 0), from, to), "trước from -> ngoài");
            Ok(FpCore.InRange(new DateTime(2020, 1, 1), null, null), "không đặt hạn -> luôn trong");
            Ok(FpCore.InRange(new DateTime(2030, 1, 1), from, null), "chỉ có from");
            Ok(!FpCore.InRange(new DateTime(2030, 1, 1), null, to), "chỉ có to");

            // -------------------------------------------------------- tên file
            Section("SafeName / MakeNames");
            Eq(FpCore.SafeName("GCQ26"), "GCQ26", "tên sạch giữ nguyên");
            Eq(FpCore.SafeName("_GCQ26XCEC dxFeed"), "GCQ26XCEC_dxFeed", "khoảng trắng -> _ , bỏ _ đầu");
            Eq(FpCore.SafeName("a/b\\c:d*e?"), "a_b_c_d_e", "ký tự cấm của Windows bị thay");
            Eq(FpCore.SafeName(""), "unknown", "rỗng -> unknown");
            Eq(FpCore.SafeName(null), "unknown", "null -> unknown");
            Ok(FpCore.SafeName(new string('x', 200)).Length <= 60, "cắt tên quá dài");

            FpCore.MakeNames("", "/def", "MGC", "1m", "20260728_101500", out var lp, out var bp);
            Eq(lp, Path.Combine("/def", "fp_MGC_1m_20260728_101500.csv"), "rỗng -> thư mục mặc định");
            Eq(bp, Path.Combine("/def", "fp_MGC_1m_20260728_101500_bars.csv"), "file nến kèm _bars");

            FpCore.MakeNames("/tmp/out", "/def", "MGC", "1m", "s", out lp, out bp);
            Eq(lp, Path.Combine("/tmp/out", "fp_MGC_1m_s.csv"), "đường dẫn là THƯ MỤC");

            FpCore.MakeNames("/tmp/my.csv", "/def", "MGC", "1m", "s", out lp, out bp);
            Eq(lp, "/tmp/my.csv", "chỉ định .csv -> dùng luôn");
            Eq(bp, Path.Combine("/tmp", "my_bars.csv"), "file nến nằm cạnh, thêm _bars");

            FpCore.MakeNames("  \"/tmp/q.CSV\"  ", "/def", "MGC", "1m", "s", out lp, out bp);
            Eq(lp, Path.Combine("/tmp", "q.csv"), "bỏ dấu ngoặc kép + khoảng trắng khi copy path từ Explorer");
            Eq(bp, Path.Combine("/tmp", "q_bars.csv"), "hoa/thường .CSV vẫn ra file nến đúng chỗ");

            FpCore.MakeNames("abc.csv", "/def", "MGC", "1m", "s", out lp, out bp);
            Eq(lp, Path.Combine("/def", "abc.csv"), "gõ TRƠ tên file -> về thư mục mặc định, không rơi vào CWD Quantower");
            Eq(bp, Path.Combine("/def", "abc_bars.csv"), "file nến cũng vào thư mục mặc định");

            // =============================================================
            //  END-TO-END: sinh CSV giả lập rồi ĐỌC LẠI và đối chiếu
            // =============================================================
            Section("End-to-end: sinh CSV -> parse lại -> đối chiếu");
            {
                double tick = 0.1;
                int digits = FpCore.DigitsFromTick(tick);
                char sep = ',';
                int perRow = 2;                                  // gộp 2 tick/hàng để test cả nhánh gộp
                var rnd2 = new Random(777);

                var sbL = new StringBuilder();
                var sbB = new StringBuilder();
                sbL.Append(FpCore.LevelsHeader(sep)).Append('\n');
                sbB.Append(FpCore.BarsHeader(sep)).Append('\n');

                var expect = new List<(int idx, double bid, double ask, double vol, double delta, int trades, int levels)>();
                for (int b = 0; b < 12; b++)
                {
                    int n = rnd2.Next(1, 15);
                    var lvls = new List<FpLevel>();
                    long baseTick = 40400 + b * 3;
                    for (int i = 0; i < n; i++)
                        lvls.Add(L(baseTick + i, bid: rnd2.Next(0, 60), ask: rnd2.Next(0, 60),
                                   tr: rnd2.Next(1, 9), mot: rnd2.Next(1, 20)));
                    var agg = FpCore.Aggregate(lvls, perRow);
                    string dt = new DateTime(2026, 7, 1, 9, 0, 0).AddMinutes(b).ToString("yyyy-MM-dd HH:mm:ss", inv);
                    foreach (var lv in agg)
                        FpCore.AppendLevelRow(sbL, sep, b, dt, FpCore.PriceOf(lv.Tick, tick), lv, digits);

                    int pi = FpCore.PocIndex(agg);
                    var fb = new FpBar
                    {
                        Idx = b, Dt = dt,
                        Open = 4040.0, High = 4041.0, Low = 4039.0, Close = 4040.5,
                        BidVol = agg.Sum(x => x.BidVol), AskVol = agg.Sum(x => x.AskVol),
                        Volume = agg.Sum(x => x.Volume), Delta = agg.Sum(x => x.Delta),
                        MaxDelta = double.MinValue, MinDelta = double.MaxValue,  // giá trị MỒI — phải bị dọn
                        Trades = agg.Sum(x => x.Trades),
                        Levels = agg.Count,
                        PocPrice = pi >= 0 ? FpCore.PriceOf(agg[pi].Tick, tick) : 0,
                        PocVolume = pi >= 0 ? agg[pi].Volume : 0
                    };
                    fb.MaxDelta = FpCore.FixPrimer(fb.MaxDelta, fb.Delta);
                    fb.MinDelta = FpCore.FixPrimer(fb.MinDelta, fb.Delta);
                    FpCore.AppendBarRow(sbB, sep, fb, digits);
                    expect.Add((b, fb.BidVol, fb.AskVol, fb.Volume, fb.Delta, fb.Trades, fb.Levels));
                }

                // ---- parse lại file mức giá
                var lines = sbL.ToString().TrimEnd('\n').Split('\n');
                var head = lines[0].Split(sep);
                Eq(head.Length, 11, "header levels 11 cột");
                Ok(lines.Skip(1).All(l => l.Split(sep).Length == head.Length), "MỌI dòng levels đủ cột");
                Ok(lines.Skip(1).All(l => !l.Contains("E+") && !l.Contains("E-")), "không có số dạng E trong levels");
                Ok(lines.Skip(1).All(l => !l.EndsWith(sep.ToString())), "không có sep đuôi dòng");

                int ci(string n) => Array.IndexOf(head, n);
                var byBar = lines.Skip(1).Select(l => l.Split(sep))
                                 .GroupBy(f => int.Parse(f[ci("bar_idx")], inv))
                                 .ToDictionary(g => g.Key, g => g.ToList());
                Eq(byBar.Count, 12, "parse lại đúng 12 nến");

                foreach (var e in expect)
                {
                    var rws = byBar[e.idx];
                    Eq(rws.Count, e.levels, $"nến {e.idx}: số hàng mức giá");
                    double bid = rws.Sum(f => double.Parse(f[ci("bid_vol")], inv));
                    double ask = rws.Sum(f => double.Parse(f[ci("ask_vol")], inv));
                    double vol = rws.Sum(f => double.Parse(f[ci("volume")], inv));
                    double del = rws.Sum(f => double.Parse(f[ci("delta")], inv));
                    int trd = rws.Sum(f => int.Parse(f[ci("trades")], inv));
                    Near(bid, e.bid, 1e-9, $"nến {e.idx}: tổng bid_vol == bid của nến");
                    Near(ask, e.ask, 1e-9, $"nến {e.idx}: tổng ask_vol == ask của nến");
                    Near(vol, e.vol, 1e-9, $"nến {e.idx}: tổng volume == volume nến");
                    Near(del, e.delta, 1e-9, $"nến {e.idx}: tổng delta == delta nến");
                    Near(del, ask - bid, 1e-9, $"nến {e.idx}: delta == ask − bid (đúng quy ước order flow)");
                    Eq(trd, e.trades, $"nến {e.idx}: tổng trades");
                    // giá phải tăng dần trong 1 nến & là bội của bước gộp
                    var prices = rws.Select(f => double.Parse(f[ci("price")], inv)).ToList();
                    Ok(prices.Zip(prices.Skip(1), (x, y) => y > x).All(v => v), $"nến {e.idx}: giá tăng dần");
                    Ok(prices.All(p => Math.Abs(FpCore.ToTick(p, tick) % perRow) < 1e-9), $"nến {e.idx}: giá neo theo bước gộp");
                }

                // ---- parse lại file nến + join bằng bar_idx
                var bl = sbB.ToString().TrimEnd('\n').Split('\n');
                var bh = bl[0].Split(sep);
                Eq(bh.Length, 27, "header bars 27 cột");
                Ok(bl.Skip(1).All(l => l.Split(sep).Length == bh.Length), "MỌI dòng bars đủ cột");
                Ok(bl.Skip(1).All(l => !l.Contains("E+") && !l.Contains("E-")),
                   "bars: giá trị MỒI đã bị dọn (không có -1.79E+308)");
                int bi(string n) => Array.IndexOf(bh, n);
                var barRows = bl.Skip(1).Select(l => l.Split(sep)).ToList();
                Eq(barRows.Count, 12, "12 dòng nến");
                Ok(barRows.Select(f => int.Parse(f[bi("bar_idx")], inv)).SequenceEqual(Enumerable.Range(0, 12)),
                   "bar_idx liên tục 0..11 -> join với file levels được");
                foreach (var f in barRows)
                {
                    int idx = int.Parse(f[bi("bar_idx")], inv);
                    var e = expect[idx];
                    Near(double.Parse(f[bi("volume")], inv), e.vol, 1e-9, $"bars {idx}: volume khớp");
                    Near(double.Parse(f[bi("delta")], inv), e.delta, 1e-9, $"bars {idx}: delta khớp");
                    Near(double.Parse(f[bi("max_delta")], inv), e.delta, 1e-9, $"bars {idx}: max_delta mồi -> fallback delta");
                    Eq(int.Parse(f[bi("levels")], inv), e.levels, $"bars {idx}: số mức khớp file levels");
                    double poc = double.Parse(f[bi("poc_price")], inv);
                    var rws = byBar[idx];
                    double maxVol = rws.Max(x => double.Parse(x[ci("volume")], inv));
                    Near(double.Parse(f[bi("poc_volume")], inv), maxVol, 1e-9, $"bars {idx}: poc_volume = volume lớn nhất");
                    Ok(rws.Any(x => Math.Abs(double.Parse(x[ci("price")], inv) - poc) < 1e-9),
                       $"bars {idx}: poc_price tồn tại trong file levels");
                }

                // ---- ghi ra file thật rồi đọc lại bằng đĩa (kiểm encoding + newline)
                string tmp = Path.Combine(Path.GetTempPath(), "fp_selftest.csv");
                File.WriteAllText(tmp, sbL.ToString(), new UTF8Encoding(false));
                var back = File.ReadAllLines(tmp);
                Eq(back.Length, lines.Length, "ghi/đọc đĩa không mất dòng");
                var bytes = File.ReadAllBytes(tmp);
                Ok(!(bytes.Length > 2 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF),
                   "KHÔNG có BOM (pandas đọc cột đầu sạch)");
                File.Delete(tmp);
            }

            // ------------------------------------------------------ tổng kết
            Console.WriteLine();
            Console.WriteLine(new string('=', 60));
            Console.WriteLine($"PASS {_pass}   FAIL {_fail}");
            if (_fail > 0)
            {
                Console.WriteLine("\nCác test hỏng:");
                foreach (var f in _fails.Take(30)) Console.WriteLine("  - " + f);
            }
            Console.WriteLine(new string('=', 60));
            return _fail == 0 ? 0 : 1;
        }

        /// <summary>
        /// Sinh 2 file CSV mẫu GIỐNG THẬT (kể cả ca "volume > bid+ask" do feed không gắn được
        /// phe chủ động — đã kiểm trên 28.071 nến thật của dxFeed: bid+ask ≤ volume, 42% nến lệch).
        /// </summary>
        static int WriteSample(string dir)
        {
            var inv = CultureInfo.InvariantCulture;
            Directory.CreateDirectory(dir);
            double tick = 0.1;
            int digits = FpCore.DigitsFromTick(tick);
            char sep = ',';
            int perRow = 1;
            var rnd = new Random(4242);

            FpCore.MakeNames("", dir, "MGCQ26", "1m", "sample", out var lp, out var bp);
            var sbL = new StringBuilder().Append(FpCore.LevelsHeader(sep)).Append('\n');
            var sbB = new StringBuilder().Append(FpCore.BarsHeader(sep)).Append('\n');

            for (int b = 0; b < 200; b++)
            {
                int n = rnd.Next(1, 22);
                long baseTick = 40400 + rnd.Next(-40, 40);
                var lvls = new List<FpLevel>(n);
                for (int i = 0; i < n; i++)
                {
                    double bid = rnd.Next(0, 80), ask = rnd.Next(0, 80);
                    double unknown = rnd.Next(0, 3) == 0 ? rnd.Next(1, 15) : 0;   // lệnh không rõ phe
                    lvls.Add(new FpLevel
                    {
                        Tick = baseTick + i,
                        BidVol = bid, AskVol = ask,
                        Volume = bid + ask + unknown,          // volume ≥ bid+ask (giống feed thật)
                        Delta = ask - bid,
                        Trades = rnd.Next(1, 12), BuyTrades = rnd.Next(0, 6), SellTrades = rnd.Next(0, 6),
                        MaxOneTrade = rnd.Next(1, 40)
                    });
                }
                var agg = FpCore.Aggregate(lvls, perRow);
                string dt = new DateTime(2026, 7, 1, 9, 0, 0).AddMinutes(b).ToString("yyyy-MM-dd HH:mm:ss", inv);
                foreach (var lv in agg)
                    FpCore.AppendLevelRow(sbL, sep, b, dt, FpCore.PriceOf(lv.Tick, tick), lv, digits);

                int pi = FpCore.PocIndex(agg);
                bool emptyBar = b % 37 == 0;                    // vài nến mồi MaxDelta/MinDelta
                var fb = new FpBar
                {
                    Idx = b, Dt = dt,
                    Open = FpCore.PriceOf(baseTick, tick), High = FpCore.PriceOf(baseTick + n, tick),
                    Low = FpCore.PriceOf(baseTick - 2, tick), Close = FpCore.PriceOf(baseTick + 1, tick),
                    BarVolume = agg.Sum(x => x.Volume), BarTicks = agg.Sum(x => (long)x.Trades),
                    BidVol = agg.Sum(x => x.BidVol), AskVol = agg.Sum(x => x.AskVol),
                    Volume = agg.Sum(x => x.Volume), Delta = agg.Sum(x => x.Delta),
                    Trades = agg.Sum(x => x.Trades),
                    BuyTrades = agg.Sum(x => x.BuyTrades), SellTrades = agg.Sum(x => x.SellTrades),
                    MaxOneTrade = agg.Max(x => x.MaxOneTrade),
                    Levels = agg.Count,
                    PocPrice = pi >= 0 ? FpCore.PriceOf(agg[pi].Tick, tick) : 0,
                    PocVolume = pi >= 0 ? agg[pi].Volume : 0
                };
                fb.DeltaFinish = FpCore.FixPrimer(emptyBar ? double.MaxValue : fb.Delta, fb.Delta);
                fb.MaxDelta = FpCore.FixPrimer(emptyBar ? double.MinValue : fb.Delta + 5, fb.Delta);
                fb.MinDelta = FpCore.FixPrimer(emptyBar ? double.MaxValue : fb.Delta - 5, fb.Delta);
                fb.AvgSize = fb.Trades > 0 ? fb.Volume / fb.Trades : 0;
                FpCore.AppendBarRow(sbB, sep, fb, digits);
            }
            var utf8 = new UTF8Encoding(false);
            File.WriteAllText(lp, sbL.ToString(), utf8);
            File.WriteAllText(bp, sbB.ToString(), utf8);
            Console.WriteLine(lp);
            Console.WriteLine(bp);
            return 0;
        }

        // helper: tạo 1 mức giá; volume/delta luôn nhất quán với bid/ask
        static FpLevel L(long tick, double bid = 0, double ask = 0, int tr = 0, double mot = 0)
            => new FpLevel
            {
                Tick = tick, BidVol = bid, AskVol = ask,
                Volume = bid + ask, Delta = ask - bid,
                Trades = tr, BuyTrades = tr / 2, SellTrades = tr - tr / 2,
                MaxOneTrade = mot
            };
    }
}
