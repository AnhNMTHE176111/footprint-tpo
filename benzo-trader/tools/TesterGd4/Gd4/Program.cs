// GĐ4 — tester độc lập cho Benzo CORVEN (cập nhật corven-2 2026-11-09) (plan BENZO-CORVEN mục 4 + 10.6). KHÔNG sửa mã sản phẩm.
// Nạp dist/BenzoTrader.dll đã build. Chạy:  dotnet run --project benzo-trader/tools/TesterGd4/Gd4 -c Release -- <reflect|ui|caption|cache|all>
// CHỈ dùng phần TRAIN của file 90d (bar_idx ≤ 51318) — không nạp TEST.
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.Json.Nodes;
using BenzoTraderNs;
using TradingPlatform.BusinessLayer;
using TradingPlatform.BusinessLayer.Chart;

static class Program
{
    const int Cut = 51318, Deny = 3697;
    static int _ok, _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        if (ok) { _ok++; Console.WriteLine($"  PASS {name}"); } else { _fail++; Console.WriteLine($"  FAIL {name} {detail}"); }
    }
    static string Root()
    {
        var d = new DirectoryInfo(AppContext.BaseDirectory);
        while (d != null && !Directory.Exists(Path.Combine(d.FullName, "data-export"))) d = d.Parent;
        return d.FullName;
    }
    static string Prefix => Path.Combine(Root(), "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
    static string UiOut => Path.Combine(Root(), "benzo-trader", "tests", "ui-out");

    static int Main(string[] a)
    {
        string what = a.Length > 0 ? a[0] : "all";
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        if (what is "reflect" or "all") Reflect();
        if (what is "caption" or "all") Caption();
        if (what is "cache" or "all") Cache();
        if (what is "ui" or "all") Ui();
        if (what is "fix12" or "all") Fix12();
        Console.WriteLine($"== {_ok} PASS, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }

    // ================================================================ (c) phản chiếu DLL
    static void Reflect()
    {
        Console.WriteLine("[c] Phản chiếu dist/BenzoTrader.dll");
        var asm = typeof(BenzoTrader).Assembly;
        Console.WriteLine($"  DLL: {asm.Location} · {new FileInfo(asm.Location).LastWriteTime:yyyy-MM-dd HH:mm}");
        Type[] types;
        try { types = asm.GetTypes(); } catch (ReflectionTypeLoadException e) { types = e.Types.Where(x => x != null).ToArray(); }
        var names = types.Select(t => t.FullName).OrderBy(x => x).ToList();
        string[] banned = { "DetectorA", "DetectorB", "DetectorC", "DetectorD", "SetupA5", "BenzoLayers", "BenzoSr", "VclCore", "Vcl", "DemoDetector", "BenzoRisk", "ZigZag", "Layer" };
        var hit = names.Where(n => { var s = n.Split('.', '+').Last(); return s != "DetectorCorven" && banned.Any(b => s.StartsWith(b)); }).ToList();
        Check(hit.Count == 0, "không còn kiểu của A/B/C/D/A5/VCL/Layers/Sr trong DLL", string.Join(", ", hit));
        Console.WriteLine("  kiểu public trong BenzoTraderNs: " + string.Join(", ", types.Where(t => t.IsPublic && t.Namespace == "BenzoTraderNs").Select(t => t.Name).OrderBy(x => x)));
        Check(types.Any(t => t.Name == "DetectorCorven") && types.Any(t => t.Name == "CorvenParams"), "có DetectorCorven + CorvenParams");

        var props = typeof(BenzoTrader).GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Select(p => (p, att: p.GetCustomAttributesData().FirstOrDefault(x => x.AttributeType.Name == "InputParameterAttribute")))
            .Where(x => x.att != null)
            .Select(x => (x.p, name: (string)x.att.ConstructorArguments[0].Value, order: (int)x.att.ConstructorArguments[1].Value))
            .OrderBy(x => x.order).ToList();
        BenzoTrader inst = null;
        try { inst = new BenzoTrader(); } catch (Exception ex) { Console.WriteLine("  (không tạo được instance: " + ex.GetType().Name + " " + ex.Message + ")"); }
        Console.WriteLine("  Settings (thứ tự · nhãn · kiểu · mặc định):");
        foreach (var (p, name, order) in props)
            Console.WriteLine($"    {order,3} · {name} · {p.PropertyType.Name} · {(inst == null ? "?" : FormatVal(p.GetValue(inst)))}");
        var expect = new (string name, string type, object def)[]
        {
            ("Lệch giờ (UTC → VN)", "Int32", 7),
            ("Telegram: bật", "Boolean", false),
            ("Telegram: bot token", "String", ""),
            ("Telegram: chat id", "String", ""),
            ("Telegram: gửi thử (bật lên để gửi)", "Boolean", false),
            ("Bật setup CORVEN (chạy thử — backtest −0,07R/lệnh, ngang vào ngẫu nhiên)", "Boolean", true),
            ("Chặn 19:20–20:30 VN (mốc neo Mỹ)", "Boolean", true),
            ("Hiện range", "Boolean", true),
            ("Hiện dấu hiệu đã đếm", "Boolean", true),
            ("Đặt lại thống kê (bật lên để đặt)", "Boolean", false),
            ("Hiện lại toàn bộ thống kê (bật lên để xoá mốc đặt lại)", "Boolean", false),
            ("Hiện bảng", "Boolean", true),
        };
        Check(props.Count == expect.Length, $"đúng {expect.Length} mục Settings (plan 10.2)", props.Count.ToString());
        for (int i = 0; i < Math.Min(props.Count, expect.Length); i++)
        {
            var (p, name, _) = props[i];
            bool okName = name == expect[i].name, okType = p.PropertyType.Name == expect[i].type;
            bool okDef = inst == null || Equals(p.GetValue(inst), expect[i].def);
            Check(okName && okType && okDef, $"Settings #{i + 1}: {expect[i].name} = {FormatVal(expect[i].def)}", $"thấy: {name} / {p.PropertyType.Name} / {(inst == null ? "?" : FormatVal(p.GetValue(inst)))}");
        }
        var numeric = props.Where(x => x.p.PropertyType != typeof(bool) && x.p.PropertyType != typeof(string) && x.name != "Lệch giờ (UTC → VN)").ToList();
        Check(numeric.Count == 0, "không có ngưỡng số nào trong Settings (ngoài Lệch giờ)", string.Join(", ", numeric.Select(x => x.name)));
        // tham số đóng cứng = bộ gốc vòng 1 (plan 10.1)
        var cp = typeof(CorvenParams);
        object V(string f) => cp.GetField(f).GetRawConstantValue();
        var want = new Dictionary<string, object>
        {
            ["LogicVersion"] = "corven-2", ["NearMbr"] = 1.0, ["WinB"] = 3, ["WinAMax"] = 5, ["CfAfterFb"] = 2, ["AgeB"] = 30, ["SiRatio"] = 250.0,
            ["SiRun"] = 3, ["SiMinVol"] = 1.0, ["BFromExhausted"] = true, ["SameSession"] = true, ["DeltaMult"] = 2.0, ["BubbleMult"] = 3.0,
            ["BubbleMin"] = 10.0, ["DivMinLen"] = 2, ["DivMaxLen"] = 8, ["NeedSigns"] = 2, ["CfBody"] = 0.4, ["CfCloseExt"] = 0.3, ["CfMinRngMbr"] = 0.5,
            ["CfMinDelta"] = 0.5, ["SlBufTicks"] = 3.0, ["SlBufMbr"] = 0.2, ["SlFloorMbr"] = 1.0, ["SlCapMbr"] = 4.0, ["RMin"] = 1.7, ["TpR"] = 2.0,
            ["DeadLook"] = 300, ["BlockFirstBars"] = 15, ["VetoWindow"] = 5, ["StopRunK"] = 3, ["OverlapBars"] = 30, ["OverlapFrac"] = 0.5,
            ["HoiKhongCham"] = true, ["BoQuetStop"] = true, ["BBoRMin"] = true, ["TrapHoi"] = true,
        };
        var bad = want.Where(kv => !Equals(V(kv.Key), kv.Value)).Select(kv => $"{kv.Key}={V(kv.Key)}≠{kv.Value}").ToList();
        Check(bad.Count == 0, $"CorvenParams trong DLL = bộ gốc vòng 1 + 4 cờ corven-2 ({want.Count} hằng)", string.Join("; ", bad));
        var extra = cp.GetFields().Where(f => f.IsLiteral && !want.ContainsKey(f.Name)).Select(f => $"{f.Name}={f.GetRawConstantValue()}");
        Console.WriteLine("  hằng khác trong CorvenParams: " + string.Join(" · ", extra));
        Check(!cp.GetFields().Any(f => f.Name.StartsWith("A2") || f.Name.Contains("Pivot") || f.Name.Contains("OverlapMaxDrop") || f.Name.Contains("ExcMaxAge")),
              "không port A2 / neo pivot / overlap_max_drop / exc_max_age");
    }
    static string FormatVal(object v) => v is string s ? $"\"{s}\"" : v?.ToString() ?? "null";

    // ================================================================ (f) caption Telegram (KHÔNG gửi thật)
    static (List<BarData> b, List<LevelVol>[] l) _train;
    static (List<BarData> b, List<LevelVol>[] l) Train() => _train.b != null ? _train : (_train = CorvenData.Load(Prefix, Cut));

    static void Caption()
    {
        Console.WriteLine("[f] Caption Telegram mẫu (không gửi — không có token)");
        var (tb, tl) = Train();
        var (eng, _) = CorvenData.Run(tb.Take(9000).ToList(), tl.Take(9000).ToArray(), 0.1, Deny);
        var sigs = eng.Signals;
        Check(sigs.Count > 0, "có lệnh TRAIN để làm mẫu", sigs.Count.ToString());
        foreach (var s in new[] { sigs.First(x => x.Setup == 'A'), sigs.FirstOrDefault(x => x.Setup == 'B') ?? sigs[0], sigs.FirstOrDefault(x => x.Zone.StartsWith("stacked")) }.Where(x => x != null).Distinct())
        {
            string cap = BenzoCore.ComposeOpen(s, "GCZ26", 7, 1, 1);
            Console.WriteLine("  ---- caption " + s.Id);
            foreach (var ln in cap.Split('\n')) Console.WriteLine("  | " + ln);
            var lines = cap.Split('\n');
            Check(lines.Length == 5, "5 dòng (4 dòng mục 2 + dòng ⚠)", lines.Length.ToString());
            Check(lines[0].StartsWith(s.Side > 0 ? "🟢 BUY · CORVEN thế " : "🔴 SELL · CORVEN thế ") && lines[0].EndsWith(" VN"), "dòng 1: icon BUY/SELL · CORVEN thế X · mã · giờ VN");
            Check(lines[1].StartsWith("Mốc: "), "dòng 2: Mốc");
            Check(lines[2].StartsWith($"Dấu hiệu ({s.NSigns}): ") && s.NSigns >= 2 && lines[2].Split(" · ").Length == s.NSigns, "dòng 3: Dấu hiệu (N) liệt kê đủ N dấu hiệu, có số", lines[2]);
            Check(lines[3].StartsWith("CF ") && lines[3].Contains(" · Vào ") && lines[3].Contains(" · SL ") && lines[3].Contains(" · TP ") && lines[3].Contains("(2R, R sẵn "), "dòng 4: CF · Vào · SL · TP (2R, R sẵn)");
            Check(lines[4] == "⚠ Chưa có lợi thế đo được (−0,07R/lệnh, 35 phiên)", "dòng 5 = nhãn ⚠ đúng chữ plan 10.3");
            Check(cap.Length <= 1024, "≤ 1024 ký tự (giới hạn caption ảnh)", cap.Length.ToString());
            // dòng 4: giờ CF hiển thị = giờ MỞ nến theo VN (plan 12.1 #6: = time_vn CSV = nhãn nến Quantower) — kiểm khớp dòng 1
            string tVn = s.Time.AddHours(7).ToString("HH:mm");
            Check(lines[0].Contains(tVn) && lines[3].StartsWith("CF " + tVn), "giờ ở dòng 1 và dòng 4 = giờ MỞ nến CF (VN)", tVn);
            Check(lines[3].Contains("Vào " + BenzoCore.FmtPrice(s.Entry, 1)) && lines[3].Contains("SL " + BenzoCore.FmtPrice(s.Sl, 1)) && lines[3].Contains("TP " + BenzoCore.FmtPrice(s.Tp, 1)), "giá vào/SL/TP trong caption = giá lệnh");
        }
        var c = sigs.First(x => x.IsClosed);
        Console.WriteLine("  ---- tin đóng: " + BenzoCore.ComposeClose(c, 7, 1));
        Check(BenzoCore.ComposeClose(c, 7, 1).StartsWith(c.R > 0 ? "✅ CORVEN thế " : "🛑 CORVEN thế "), "tin đóng dạng ✅/🛑 CORVEN thế X ±R · giờ→giờ");
        Console.WriteLine("  ---- tin huỷ: " + BenzoCore.ComposeCancel(c, 7, 1));
        // nút gửi thử: chuỗi trong DLL (đọc IL string) có dòng ⚠
        Check(CorvenParams.TeleWarn.StartsWith("⚠"), "nút 'gửi thử' nối CorvenParams.TeleWarn (xem nguồn SendTest)");
        // Telegram không có token ⇒ không gửi, báo lỗi rõ
        var tc = new TeleClient();
        bool sent = tc.SendMessageAsync("x", default).GetAwaiter().GetResult();
        Check(!sent && tc.LastError == "thiếu bot token / chat id", "không token ⇒ không gửi, LastError rõ ràng", tc.LastError);
        var mp = TeleClient.BuildPhoto("123", new byte[] { 1, 2, 3 }, BenzoCore.ComposeOpen(sigs[0], "GCZ26", 7, 1, 1));
        Check(mp.Count() == 3, "multipart sendPhoto: chat_id + caption + photo");
    }

    // ================================================================ (h) cache theo khung (thư mục KHÁC)
    static void Cache()
    {
        Console.WriteLine("[h] Cache theo khung (plan 10.5) — thư mục riêng của tester");
        string dir = Path.Combine(Path.GetTempPath(), "benzo_tester_gd4_" + Guid.NewGuid().ToString("N").Substring(0, 8), "thư mục có dấu & cách");
        Directory.CreateDirectory(dir);
        Console.WriteLine("  thư mục: " + dir);
        Check(BenzoCore.CacheFileName("GCZ26", "Time", 1) == "cache_GCZ26_Time_1m.jsonl", "tên cache gồm khung: cache_GCZ26_Time_1m.jsonl");
        Check(BenzoCore.CacheFileName("GCZ26", "Time", 1) != BenzoCore.CacheFileName("GCZ26", "Time", 5), "M1 và M5 ra 2 file khác nhau");
        Check(BenzoCore.SignalsCsvName("MGCZ6", 1) == "signals_MGCZ6_1m_corven-2.csv" && BenzoCore.CandidatesCsvName("MGCZ6", 1) == "candidates_MGCZ6_1m_corven-2.csv", "2 CSV có khung + phiên bản");
        Check(BenzoCore.CacheFileName("GC/Z26:XCEC", "Time", 1).IndexOfAny(Path.GetInvalidFileNameChars()) < 0, "mã có ký tự lạ (/ :) được làm sạch");
        Check(BenzoCore.CacheVersion(true) == "corven-2-us1" && BenzoCore.CacheVersion(false) == "corven-2-us0", "khoá cache = corven-2-us{0|1}");

        var (tb, tl) = Train();
        int n = 24000;
        var b = tb.Take(n).ToList(); var l = tl.Take(n).ToArray();
        string cp = Path.Combine(dir, BenzoCore.CacheFileName("GCZ26", "Time", 1));
        var (e0, _) = CorvenData.Run(b, l, 0.1, Deny);                                          // không cache = chuẩn
        var c1 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c1.Load();
        var (e1, _) = CorvenData.Run(b, l, 0.1, Deny, cache: c1);
        Check(Sig(e0).SequenceEqual(Sig(e1)), "chạy có cache (lần đầu, ghi) = không cache", $"{e0.Signals.Count}/{e1.Signals.Count}");
        var c2 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c2.Load();
        Check(c2.Count == e1.Signals.Count(x => true) || c2.Count >= e1.Signals.Count, "nạp lại cache: đủ tín hiệu niêm phong", $"{c2.Count}/{e1.Signals.Count}");
        var (e2, _) = CorvenData.Run(b, l, 0.1, Deny, cache: c2);
        Check(Sig(e0).SequenceEqual(Sig(e2)), "chạy lại từ cache (reload) = chuẩn, kể cả kết cục tính lại", $"{e2.Signals.Count}");
        // (i) History range ngắn hơn: bắt đầu từ nến 9000
        int from = 9000;
        var b3 = b.Skip(from).Select((x, i) => new BarData { Idx = i, Time = x.Time, O = x.O, H = x.H, L = x.L, C = x.C, Delta = x.Delta, Vol = x.Vol }).ToList();
        var c3 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c3.Load();
        var (e3, _) = CorvenData.Run(b3, l.Skip(from).ToArray(), 0.1, 0, cache: c3);
        var full = e0.Signals.Select(x => (x.Time, x.Side, x.Entry, x.Sl, x.Tp)).ToHashSet();
        var strange = e3.Signals.Where(x => !full.Contains((x.Time, x.Side, x.Entry, x.Sl, x.Tp))).ToList();
        Check(e3.Signals.Count > 5 && strange.Count == 0, "History range ngắn hơn: không có tín hiệu lạ", $"{e3.Signals.Count} lệnh, lạ {strange.Count}: {string.Join(",", strange.Take(3).Select(x => x.Id))}");
        var expected = e0.Signals.Where(x => x.Time >= b3[0].Time).Select(x => (x.Time, x.Side, x.Entry)).ToList();
        var got = e3.Signals.Select(x => (x.Time, x.Side, x.Entry)).ToList();
        int missing = expected.Count(x => !got.Contains(x));
        Console.WriteLine($"  lịch sử ngắn: chuẩn {expected.Count} lệnh trong khoảng, lấy lại {got.Count}, thiếu {missing} (thiếu được phép khi 1 lệnh mở lâu chặn nến niêm phong sau — chỉ cấm tín hiệu LẠ)");
        // (ii) cache của khung KHÁC (giả lập: file cache M1 của một lịch sử khác — dịch giá 1 tick) ⇒ guard phải bắt
        var bShift = b.Select(x => new BarData { Idx = x.Idx, Time = x.Time, O = x.O + 0.1, H = x.H + 0.1, L = x.L + 0.1, C = x.C + 0.1, Delta = x.Delta, Vol = x.Vol }).ToList();
        var c4 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c4.Load();
        var det4 = new DetectorCorven { AllowBar = i => i >= Deny };
        var eng4 = new BenzoEngine("GCZ26", 0.1, c4, new ISetupDetector[] { det4 }) { GetLevels = i => l[i] };
        eng4.Bars.AddRange(bShift);
        var r4 = eng4.Advance(bShift.Count - 1);
        Check(r4.CacheInvalid, "nến lệch 1 tick so với cache (Entry ≠ C) ⇒ guard bắt", r4.CacheWhy);
        // (iii) sửa tay L của một dòng ⇒ bỏ cache
        foreach (var field in new[] { "CfL", "CfH", "Entry" })
        {
            var cA = new SignalCache(cp, BenzoCore.CacheVersion(true)); cA.Load();
            CorvenData.Run(b, l, 0.1, Deny, cache: cA);   // đảm bảo file đủ
            var lines = File.ReadAllLines(cp).ToList();
            int idx = lines.FindLastIndex(x => x.Contains("\"K\":\"sig\""));
            var node = JsonNode.Parse(lines[idx]);
            node["S"][field] = node["S"][field].GetValue<double>() + (field == "Entry" ? 0.1 : 0.2);
            lines[idx] = node.ToJsonString(); File.WriteAllLines(cp, lines);
            var cB = new SignalCache(cp, BenzoCore.CacheVersion(true)); cB.Load();
            var eng = new BenzoEngine("GCZ26", 0.1, cB, new ISetupDetector[] { new DetectorCorven { AllowBar = i => i >= Deny } }) { GetLevels = i => l[i] };
            eng.Bars.AddRange(b);
            var rr = eng.Advance(b.Count - 1);
            Check(rr.CacheInvalid, $"sửa {field} của 1 dòng sig ⇒ guard bắt, engine dừng", rr.CacheWhy);
            cB.Reset();
            Check(!File.Exists(cp), "Reset xoá file cache");
        }
        // (iv) đổi công tắc chặn giờ Mỹ ⇒ khoá khác ⇒ cache cũ bỏ
        {
            var cA = new SignalCache(cp, BenzoCore.CacheVersion(true)); cA.Load();
            CorvenData.Run(b, l, 0.1, Deny, cache: cA);
            var cB = new SignalCache(cp, BenzoCore.CacheVersion(false)); cB.Load();
            Check(cB.Count == 0 && !cB.Covers(b[5000].Time.Ticks), "đổi 'Chặn 19:20–20:30' ⇒ khoá cache khác ⇒ bỏ cache cũ");
            var (eOff, _) = CorvenData.Run(b, l, 0.1, Deny, blockUs: false, cache: cB);
            var (eOff0, _) = CorvenData.Run(b, l, 0.1, Deny, blockUs: false);
            Check(Sig(eOff).SequenceEqual(Sig(eOff0)), "sau khi đổi khoá: kết quả = chạy mới với công tắc tắt");
        }
        // (v) TẮT setup rồi BẬT lại (Settings "Bật setup CORVEN" KHÔNG nằm trong khoá cache) — nến chạy lúc tắt có bị niêm phong "không tín hiệu"?
        {
            File.Delete(cp);
            int mid = 15000;
            var cA = new SignalCache(cp, BenzoCore.CacheVersion(true)); cA.Load();
            var detA = new DetectorCorven { AllowBar = i => i >= Deny };
            var engA = new BenzoEngine("GCZ26", 0.1, cA, new ISetupDetector[] { detA }) { GetLevels = i => l[i], IsEnabled = _ => false };
            engA.Bars.AddRange(b.Take(mid));
            for (int i = 0; i < mid; i++) engA.Advance(i);           // người dùng để TẮT tới nến mid
            var cB = new SignalCache(cp, BenzoCore.CacheVersion(true)); cB.Load();   // bật lại ⇒ indicator dựng lại, nạp cache
            var (eOn, _) = CorvenData.Run(b, l, 0.1, Deny, cache: cB);
            int lostBefore = e0.Signals.Count(x => x.BarIdx < mid) - eOn.Signals.Count(x => x.BarIdx < mid);
            Console.WriteLine($"  tắt setup tới nến {mid} rồi bật: chuẩn {e0.Signals.Count(x => x.BarIdx < mid)} lệnh trước nến {mid}, sau khi bật hiện {eOn.Signals.Count(x => x.BarIdx < mid)}");
            Check(lostBefore == 0, "tắt rồi bật setup: lịch sử lệnh trong lúc tắt KHÔNG bị mất vĩnh viễn (khoá cache không gồm công tắc setup)", $"mất {lostBefore} lệnh");
        }
        // (vi) Settings "Lệch giờ" đổi sm ⇒ đổi cổng chặn giờ/phiên — nhưng KHÔNG nằm trong khoá cache
        {
            var det8 = new DetectorCorven { AllowBar = i => i >= Deny };
            var eng8 = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det8 }) { GetLevels = i => l[i], TzOffset = 8 };
            eng8.Bars.AddRange(b);
            for (int i = 0; i < b.Count; i++) eng8.Advance(i);
            int diff = e0.Signals.Select(x => x.Id).Except(eng8.Signals.Select(x => x.Id)).Count() + eng8.Signals.Select(x => x.Id).Except(e0.Signals.Select(x => x.Id)).Count();
            Console.WriteLine($"  Lệch giờ 7 → 8: {diff} lệnh khác nhau (trên {e0.Signals.Count}); khoá cache = {BenzoCore.CacheVersion(true)} cho cả hai");
            Check(diff == 0, "đổi 'Lệch giờ' không đổi tín hiệu (nếu đổi thì phải nằm trong khoá cache)", $"{diff} lệnh khác");
        }
        try { Directory.Delete(Path.GetDirectoryName(dir), true); } catch { }
    }
    static IEnumerable<(string, double, double, double, string, double)> Sig(BenzoEngine e) =>
        e.Signals.Select(x => (x.Id, x.Entry, x.Sl, x.Tp, x.Outcome, Math.Round(x.R, 6)));

    // ================================================================ (d)/(i) render UI thật
    public sealed class FakeConv : IChartWindowCoordinatesConverter
    {
        public DateTime T0; public double Bw, PTop, PBot; public Rectangle Rc;
        public DateTime GetTime(double x) => T0.AddMinutes((x - Rc.Left) / Bw);
        public double GetPrice(double y) => PTop - (y - Rc.Top) / Rc.Height * (PTop - PBot);
        public double GetChartX(DateTime t) => Rc.Left + (t - T0).TotalMinutes * Bw;      // = mép TRÁI nến (quy ước Quantower: tâm = + BarsWidth/2)
        public double GetChartY(double p) => Rc.Top + (PTop - p) / (PTop - PBot) * Rc.Height;
        public double GetBarIndex(DateTime t) => (t - T0).TotalMinutes;
    }
    public sealed class FakeWin : IChartWindow
    {
        public Rectangle ClientRectangle { get; set; }
        public bool IsMainWindow => true;
        public int WindowNumber => 0;
        public IChartWindowCoordinatesConverter CoordinatesConverter { get; set; }
        public double YScaleFactor => 1;
    }
    /// <summary>IChart giả bằng DispatchProxy (interface có nhiều event chuột — không cần cho OnPaintChart).</summary>
    public class ChartProxy : DispatchProxy
    {
        public FakeWin W; public int Bw;
        protected override object Invoke(MethodInfo m, object[] args) => m.Name switch
        {
            "get_Windows" => new IChartWindow[] { W },
            "get_MainWindow" => W,
            "get_BarsWidth" => Bw,
            "get_TickSize" => 0.1,
            "get_ID" => "fake",
            "get_RightOffset" => 0,
            _ => m.ReturnType.IsValueType && m.ReturnType != typeof(void) ? Activator.CreateInstance(m.ReturnType) : null,
        };
    }
    static IChart FakeChart(FakeWin w, int bw)
    {
        var c = DispatchProxy.Create<IChart, ChartProxy>();
        var p = (ChartProxy)(object)c; p.W = w; p.Bw = bw;
        return c;
    }

    static readonly BindingFlags NP = BindingFlags.NonPublic | BindingFlags.Instance;

    /// <summary>Dựng indicator thật với engine đã chạy tới nến `upto`, render vùng [first, upto + rightPad] ra PNG.</summary>
    static (Bitmap bmp, FakeConv conv, BenzoTrader ind, BenzoEngine eng) Render(string file, List<BarData> b, List<LevelVol>[] l, int upto, int first, int rightPad,
        int bw = 9, Action<BenzoTrader, BenzoEngine> tweak = null, int W = 1400, int Hh = 760, bool candles = true)
    {
        var det = new DetectorCorven { AllowBar = i => i >= Deny };
        var eng = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det }) { GetLevels = i => l[i] };
        eng.Bars.AddRange(b.Take(upto + 1));
        for (int i = 0; i <= upto; i++) eng.Advance(i);
        var ind = new BenzoTrader();
        typeof(BenzoTrader).GetField("_engine", NP).SetValue(ind, eng);
        typeof(BenzoTrader).GetField("_det", NP).SetValue(ind, det);
        typeof(BenzoTrader).GetField("_digits", NP).SetValue(ind, 1);
        tweak?.Invoke(ind, eng);
        typeof(BenzoTrader).GetMethod("BuildRender", NP).Invoke(ind, null);
        var rc = new Rectangle(0, 0, W, Hh);
        int nBars = upto - first + 1 + rightPad;
        double bwD = Math.Max(1, Math.Floor((double)W / nBars));   // như Quantower: khoảng nến = BarsWidth nguyên (sửa harness theo 12.1 #4)
        var vis = b.Skip(first).Take(upto - first + 1).ToList();
        double hi = vis.Max(x => x.H), lo = vis.Min(x => x.L);
        foreach (var s in eng.Signals.Where(s => s.BarIdx >= first)) { hi = Math.Max(hi, Math.Max(s.Sl, s.Tp)); lo = Math.Min(lo, Math.Min(s.Sl, s.Tp)); }
        double pad = (hi - lo) * 0.08;
        var conv = new FakeConv { T0 = b[first].Time, Bw = bwD, PTop = hi + pad, PBot = lo - pad, Rc = rc };
        ind.CurrentChart = FakeChart(new FakeWin { ClientRectangle = rc, CoordinatesConverter = conv }, (int)bwD);
        var bmp = new Bitmap(W, Hh, PixelFormat.Format24bppRgb);
        using (var g = Graphics.FromImage(bmp))
        {
            g.Clear(Color.FromArgb(18, 20, 26));
            // nến (do harness vẽ thay chart Quantower — tâm nến = GetChartX + bw/2)
            for (int i = first; i <= (candles ? upto : first - 1); i++)
            {
                var x = b[i];
                float xc = (float)(conv.GetChartX(x.Time) + bwD / 2);
                var col = x.C >= x.O ? Color.FromArgb(70, 160, 110) : Color.FromArgb(190, 80, 80);
                using var pen = new Pen(col, 1);
                g.DrawLine(pen, xc, (float)conv.GetChartY(x.H), xc, (float)conv.GetChartY(x.L));
                float y0 = (float)conv.GetChartY(Math.Max(x.O, x.C)), y1 = (float)conv.GetChartY(Math.Min(x.O, x.C));
                using var br = new SolidBrush(col);
                g.FillRectangle(br, xc - (float)bwD * 0.35f, y0, (float)bwD * 0.7f, Math.Max(1, y1 - y0));
            }
            // thang giá (harness) mỗi 1,0
            using var fAx = new Font("Consolas", 7);
            for (double p = Math.Ceiling(conv.PBot); p <= conv.PTop; p += 1)
                g.DrawString(BenzoCore.Num(p), fAx, Brushes.Gray, W - 44, (float)conv.GetChartY(p) - 6);
            var args = new PaintChartEventArgs(g, rc, new Point(-1, -1), 0);
            ind.OnPaintChart(args);
        }
        Directory.CreateDirectory(UiOut);
        bmp.Save(Path.Combine(UiOut, file), ImageFormat.Png);
        Console.WriteLine("  → " + Path.Combine(UiOut, file));
        return (bmp, conv, ind, eng);
    }

    static bool Reddish(Color c) => c.R > c.G + 40 && c.R > c.B + 30;
    static bool Greenish(Color c) => c.G > c.R + 30 && c.G > c.B;
    static bool ColNear(Color c, Color want, int tol = 60) => Math.Abs(c.R - want.R) + Math.Abs(c.G - want.G) + Math.Abs(c.B - want.B) < tol;

    static void Ui()
    {
        Console.WriteLine("[d][i] Render UI thật (BenzoTrader.OnPaintChart trong DLL) với chart giả");
        var (tb, tl) = Train();
        var (e0, _) = CorvenData.Run(tb.Take(30000).ToList(), tl.Take(30000).ToArray(), 0.1, Deny);
        // ca 1: lệnh TP (đã đóng) — xem hộp SL/TP, mũi tên, nhãn
        foreach (var (s, tag) in new[] { (e0.Signals.First(x => x.Outcome == "TP" && x.Setup == 'B'), "B-TP"), (e0.Signals.First(x => x.Outcome == "SL" && x.Setup == 'A'), "A-SL") })
        {
            int exit = tb.FindIndex(x => x.Time == s.ExitTime);
            var (bmp, conv, _, eng) = Render($"corven-{tag}-{s.Time:MMdd-HHmm}.png", tb, tl, exit + 8, s.BarIdx - 70, 6);
            var sig = eng.Signals.First(x => x.Id == s.Id);
            Console.WriteLine($"  lệnh {sig.Id}: vào {sig.Entry} SL {sig.Sl} TP {sig.Tp} · {sig.Outcome} · nhãn \"{sig.Short}\"");
            int xE = (int)conv.GetChartX(sig.Time), xX = (int)conv.GetChartX(sig.ExitTime);
            int ySl = (int)Math.Round(conv.GetChartY(sig.Sl)), yTp = (int)Math.Round(conv.GetChartY(sig.Tp));
            int xm = (xE + xX) / 2;
            Check(Enumerable.Range(-1, 3).Any(d => Reddish(bmp.GetPixel(xm, ySl + d))), $"đường SL đỏ đúng giá {sig.Sl} (y={ySl})", bmp.GetPixel(xm, ySl).ToString());
            Check(Enumerable.Range(-1, 3).Any(d => Greenish(bmp.GetPixel(xm, yTp + d))), $"đường TP xanh đúng giá {sig.Tp} (y={yTp})", bmp.GetPixel(xm, yTp).ToString());
            // mũi tên: tam giác đặc màu hướng ngay trên (sell) / dưới (buy) giá vào, tại x của nến CF
            int yE = (int)conv.GetChartY(sig.Entry);
            int yA = sig.Side > 0 ? yE + 6 + 4 + 3 : yE - 6 - 4 - 3;
            var colA = bmp.GetPixel((int)Math.Round(conv.GetChartX(sig.Time) + conv.Bw / 2), yA);   // tại TÂM nến CF
            Check(sig.Side > 0 ? Greenish(colA) : Reddish(colA), $"mũi tên {(sig.Side > 0 ? "buy" : "sell")} vẽ tại x nến CF", colA.ToString());
            double cfCenter = conv.GetChartX(sig.Time) + conv.Bw / 2;
            // đỉnh mũi tên đo bằng PIXEL (sửa 12.1 #4): hàng ngay dưới/trên đỉnh tam giác, lấy tâm đoạn pixel màu hướng quanh nến CF
            int yApex = sig.Side > 0 ? yE + 6 + 4 + 2 : yE - 6 - 4 - 2;
            var xs = Enumerable.Range((int)Math.Round(cfCenter) - 5, 11)   // ±5 px: nửa rộng tam giác ở hàng này = 2 px; nhãn bắt đầu từ xE + 6
                     .Where(x => x >= 0 && x < bmp.Width && (sig.Side > 0 ? Greenish(bmp.GetPixel(x, yApex)) : Reddish(bmp.GetPixel(x, yApex)))).ToList();
            double xApex = xs.Count > 0 ? (xs.Min() + xs.Max()) / 2.0 : double.NaN;
            Check(xs.Count > 0 && Math.Abs(xApex - cfCenter) <= 1.0, "mũi tên ở TÂM nến CF (đo pixel, lệch ≤ 1 px)", $"đỉnh mũi tên x={xApex:0.0}, tâm nến CF x={cfCenter:0.0}"); 
            Check(sig.Entry == tb[sig.BarIdx].C, "giá vào = giá đóng nến CF");
        }
        // ca 2: lệnh ĐANG MỞ ở mép phải (live: CF = nến vừa đóng) — nhãn có tràn ra ngoài khung không?
        {
            var s = e0.Signals.OrderByDescending(x => x.Short.Length).First();
            var (bmp, conv, _, eng) = Render($"corven-live-mep-phai-{s.Time:MMdd-HHmm}.png", tb, tl, s.BarIdx, s.BarIdx - 90, 4);
            var sig = eng.Signals.Last();
            var f = new Font("Consolas", 8, FontStyle.Bold);
            using var g = Graphics.FromImage(new Bitmap(10, 10));
            float wLbl = g.MeasureString(sig.Short, f).Width;
            float xE = (float)conv.GetChartX(sig.Time) + (float)(conv.Bw / 2);   // tâm nến (12.1 #4)
            float lx = BenzoCore.LabelX(xE, wLbl, conv.Rc.Left, conv.Rc.Right);    // hàm vẽ thật trong DLL (12.1 #3)
            Console.WriteLine($"  nhãn dài nhất: \"{sig.Short}\" rộng {wLbl:0}px, bắt đầu x={lx:0}, khung phải x={conv.Rc.Right}");
            Check(lx >= conv.Rc.Left && lx + wLbl <= conv.Rc.Right, "nhãn lệnh mới nhất (mép phải, như live) nằm trọn trong khung chart", $"x={lx:0}, tràn {lx + wLbl - conv.Rc.Right:0}px");
        }
        // ca 3: bảng 4 dòng — đủ dòng nhãn trung thực (plan 10.3, mục i)
        {
            int upto = 29000;
            var (bmp, conv, ind, eng) = Render("corven-bang-4-dong.png", tb, tl, upto, upto - 110, 10);
            var rs = typeof(BenzoTrader).GetField("_render", NP).GetValue(ind);
            var lines = (List<string>)rs.GetType().GetField("Lines").GetValue(rs);
            foreach (var ln in lines) Console.WriteLine("  | " + ln);
            Check(lines.Count == 4, "bảng 4 dòng", lines.Count.ToString());
            Check(lines[0].StartsWith("BENZO CORVEN corven-2 · ") && lines[0].Contains(" lệnh · WR ") && lines[1].StartsWith("Thế A · ") && lines[2].StartsWith("Thế B · "), "dòng 1–3 đúng mẫu");
            Check(lines[3] == "Backtest 35 phiên: −0,07R/lệnh, ngang vào ngẫu nhiên (−0,08R) · chạy thử, không phải khuyến nghị", "dòng 4 = nhãn trung thực đúng chữ");
            // dòng 4 thật sự hiện trên ảnh: có pixel màu cam (255,170,120) ở vùng đáy trái
            int orange = 0;
            for (int y = conv.Rc.Bottom - 40; y < conv.Rc.Bottom; y++) for (int x = 0; x < 700; x++) if (ColNear(bmp.GetPixel(x, y), Color.FromArgb(255, 170, 120), 90)) orange++;
            Check(orange > 50, "dòng 4 (chữ cam) có trên ảnh", orange.ToString());
        }
        // ca 4: setup TẮT + cảnh báo Telegram + ẩn range/dấu hiệu
        {
            int upto = 29000;
            Render("corven-setup-tat-canh-bao.png", tb, tl, upto, upto - 110, 10, tweak: (ind, eng) =>
            {
                ind.EnableCorven = false; ind.ShowSigns = false; ind.ShowRange = false; ind.TeleEnabled = true;
                var tele = typeof(BenzoTrader).GetField("_tele", NP).GetValue(ind);
                tele.GetType().GetField("LastError").SetValue(tele, "sendPhoto HTTP 401");
            });
        }
        // ca 5: chart không phải M1 — dựng RenderState thủ công như Process() (BarMinutes != 1)
        {
            var ind = new BenzoTrader();
            var rsT = typeof(BenzoTrader).GetNestedType("RenderState", BindingFlags.NonPublic);
            var rs = Activator.CreateInstance(rsT, true);
            rsT.GetField("Lines").SetValue(rs, new List<string> { "Benzo CORVEN chỉ chạy trên chart M1", CorvenParams.BacktestLine });
            typeof(BenzoTrader).GetField("_render", NP).SetValue(ind, rs);
            var rc = new Rectangle(0, 0, 900, 300);
            var conv = new FakeConv { T0 = tb[0].Time, Bw = 9, PTop = 4100, PBot = 4000, Rc = rc };
            ind.CurrentChart = FakeChart(new FakeWin { ClientRectangle = rc, CoordinatesConverter = conv }, 9);
            using var bmp = new Bitmap(900, 300);
            using (var g = Graphics.FromImage(bmp)) { g.Clear(Color.FromArgb(18, 20, 26)); ind.OnPaintChart(new PaintChartEventArgs(g, rc, new Point(-1, -1), 0)); }
            bmp.Save(Path.Combine(UiOut, "corven-khong-phai-M1.png"), ImageFormat.Png);
            Console.WriteLine("  → corven-khong-phai-M1.png");
        }
        // lỗi vẽ (nếu có) được OnPaintChart nuốt và ghi error_log — kiểm file log không có dòng OnPaintChart mới
        string log = Path.Combine(Path.GetTempPath(), "error_log.txt");   // _dir null (OnInit chưa gọi) ⇒ LogErr ghi vào TEMP
        var paintErr = File.Exists(log) ? File.ReadAllLines(log).Where(x => x.Contains("OnPaintChart") && x.StartsWith(DateTime.UtcNow.ToString("yyyy-MM-dd"))).ToList() : new List<string>();
        Check(paintErr.Count == 0, "OnPaintChart không ném lỗi (error_log hôm nay không có dòng OnPaintChart)", paintErr.FirstOrDefault() ?? "");
    }

    // ================================================================ PHỤ LỤC — kiểm lại lượt sửa plan mục 12 (độc lập với kiểm do Opus sửa)
    // viền range mờ (alpha 60 xanh lơ trên nền 18,20,26, nét đứt khử răng cưa): xanh nhạt hơn nền, tối hơn hẳn viền range sống (alpha 200)
    static bool Faint(Color c) => c.B >= 34 && c.B > c.R + 8 && c.B < 110;
    static bool ArrowRed(Color c) => c.R > 130 && c.R > c.G + 60;
    static bool ArrowGreen(Color c) => c.G > 105 && c.G > c.R + 50;
    static (int lo, int hi) Run(Bitmap bmp, int y, int x0, int x1, Func<Color, bool> f)
    {
        int lo = int.MaxValue, hi = int.MinValue;
        for (int x = Math.Max(0, x0); x <= Math.Min(bmp.Width - 1, x1); x++) if (f(bmp.GetPixel(x, y))) { lo = Math.Min(lo, x); hi = Math.Max(hi, x); }
        return (lo, hi);
    }

    static void Fix12()
    {
        Console.WriteLine("[P12] Kiểm độc lập lượt sửa plan 12 (ảnh KHÔNG vẽ nến — tránh thân nến CF trùng màu mũi tên)");
        var (tb, tl) = Train();
        var (e0, _) = CorvenData.Run(tb.Take(30000).ToList(), tl.Take(30000).ToArray(), 0.1, Deny);
        // #4 mũi tên — ảnh không có nến: chỉ còn mũi tên/hộp/nhãn của indicator
        foreach (var (s, tag) in new[] { (e0.Signals.First(x => x.Outcome == "TP" && x.Setup == 'B'), "B-TP"), (e0.Signals.First(x => x.Outcome == "SL" && x.Setup == 'A'), "A-SL") })
        {
            int exit = tb.FindIndex(x => x.Time == s.ExitTime);
            var (bmp, conv, _, eng) = Render($"p12-khong-nen-{tag}.png", tb, tl, exit + 8, s.BarIdx - 70, 6, candles: false);
            var sig = eng.Signals.First(x => x.Id == s.Id);
            double left = conv.GetChartX(sig.Time), center = left + Math.Floor(conv.Bw) / 2.0;
            int yE = (int)Math.Round(conv.GetChartY(sig.Entry));
            Func<Color, bool> f = sig.Side > 0 ? ArrowGreen : ArrowRed;
            // hàng giữa tam giác (đáy cách đỉnh 6 px): rộng ~6 px, đối xứng quanh x đỉnh
            int yMid = sig.Side > 0 ? yE + 4 + 6 + 3 : yE - 4 - 6 - 3;
            var (lo, hi) = Run(bmp, yMid, (int)left - 20, (int)left + 20, f);
            double mid = (lo + hi) / 2.0;
            Console.WriteLine($"  {tag}: mép trái nến {left:0.0}, tâm {center:0.0}, mũi tên đo được [{lo};{hi}] tâm {mid:0.0}");
            Check(lo != int.MaxValue && Math.Abs(mid - center) <= 1.0 && hi - lo <= 10, $"#4 {tag}: mũi tên ở tâm nến CF (ảnh không nến, lệch ≤ 1 px)", $"tâm đo {mid:0.0} vs {center:0.0}");
            // 7c: hộp range mờ của lệnh đã đóng
            Check(sig.RangeT0 > 0 && sig.RangeT1 == sig.Time.Ticks && sig.RangeT0 < sig.RangeT1, "7c: RangeT0 < RangeT1 = giờ CF", $"{sig.RangeT0} {sig.RangeT1}");
            int t0i = tb.FindIndex(x => x.Time.Ticks == sig.RangeT0);
            Check(t0i >= 0 && sig.BarIdx - t0i is > 0 and < 2000, "7c: RangeT0 là giờ một nến có thật, trước CF", $"nến {t0i}, CF {sig.BarIdx}");
            int x0 = (int)conv.GetChartX(new DateTime(sig.RangeT0, DateTimeKind.Utc)) + 2, x1 = (int)left - 2;
            int yHi = (int)Math.Round(conv.GetChartY(sig.RangeHi)), yLo = (int)Math.Round(conv.GetChartY(sig.RangeLo));
            var faint = Color.FromArgb(42, 62, 75);
            int nHi = 0, nLo = 0, nCtl = 0;
            for (int x = Math.Max(0, x0); x <= x1; x++)
            {
                if (Enumerable.Range(-1, 3).Any(d => Faint(bmp.GetPixel(x, yHi + d)))) nHi++;
                if (Enumerable.Range(-1, 3).Any(d => Faint(bmp.GetPixel(x, yLo + d)))) nLo++;
                if (yHi - 6 >= 0 && Faint(bmp.GetPixel(x, yHi - 6))) nCtl++;          // đối chứng: hàng ngay NGOÀI hộp
                if (yLo + 6 < bmp.Height && Faint(bmp.GetPixel(x, yLo + 6))) nCtl++;
            }
            Console.WriteLine($"  7c {tag}: range {sig.RangeLo}–{sig.RangeHi} (nến {t0i}→{sig.BarIdx}), cạnh trên {nHi}/{x1 - x0 + 1} px mờ, cạnh dưới {nLo}/{x1 - x0 + 1} px mờ, đối chứng ngoài hộp {nCtl}/{2 * (x1 - x0 + 1)}");
            Check(nHi > (x1 - x0) / 4 && nLo > (x1 - x0) / 4 && nCtl < (x1 - x0) / 5, $"7c {tag}: thấy hộp range viền đứt mờ đúng giá range_lo/range_hi của lệnh đã đóng");
        }
        // #3 nhãn sát mép phải — kiểm bằng PIXEL nền nhãn, không gọi LabelX
        {
            var s = e0.Signals.OrderByDescending(x => x.Short.Length).First();
            var (bmp, conv, _, eng) = Render($"p12-nhan-mep-phai-khong-nen.png", tb, tl, s.BarIdx, s.BarIdx - 90, 4, candles: false);
            var sig = eng.Signals.Last();
            double center = conv.GetChartX(sig.Time) + Math.Floor(conv.Bw) / 2.0;
            using var g = Graphics.FromImage(new Bitmap(10, 10));
            float w = g.MeasureString(sig.Short, new Font("Consolas", 8, FontStyle.Bold)).Width;
            int yE = (int)Math.Round(conv.GetChartY(sig.Entry));
            int yRow = sig.Side > 0 ? yE + 12 + 8 + 2 : yE - 12 - 22 + 2;      // hàng trong nền nhãn (ly + 2)
            Func<Color, bool> bg = sig.Side > 0 ? (c => c.G > 150 && c.G > c.R + 60) : (c => c.R > 170 && c.R > c.G + 80);
            var (lo, hi) = Run(bmp, yRow, 0, bmp.Width - 1, bg);
            double wantLo = center - 8 - w - 2, wantHi = center - 8 - w - 2 + w + 4;   // công thức plan 12.1 #3 tính tay
            Console.WriteLine($"  #3: nhãn \"{sig.Short}\" w={w:0}; nền nhãn đo [{lo};{hi}], mong [{wantLo:0};{wantHi:0}], khung phải {conv.Rc.Right}, tâm nến {center:0}");
            Check(lo != int.MaxValue && hi <= conv.Rc.Right - 1 && hi < center && Math.Abs(lo - wantLo) <= 3 && Math.Abs(hi - wantHi) <= 3,
                  "#3: nền nhãn nằm TRỌN trong khung, lật sang trái mũi tên, đủ bề rộng chuỗi (đo pixel)", $"[{lo};{hi}]");
        }
        // #6 giờ caption = time_vn CSV, lệnh mẫu của plan
        {
            var s = e0.Signals.First(x => x.Id == "GCZ26|202607291552|A|S");
            string cap = BenzoCore.ComposeOpen(s, "GCZ26", 7, 1, 1);
            string csvVn = SignalCsv.ToLine(s, 7).Split(',')[1];
            Check(cap.Split('\n')[0].EndsWith("· 22:52 VN") && cap.Split('\n')[3].StartsWith("CF 22:52 ") && csvVn == "2026-07-29 22:52",
                  "#6: caption 22:52 VN = time_vn CSV (15:52 UTC + 7)", cap.Split('\n')[0] + " / " + csvVn);
            string cl = BenzoCore.ComposeClose(s, 7, 1);
            Check(cl.EndsWith("· 22:52→" + s.ExitTime.AddHours(7).ToString("HH:mm")), "#6: tin đóng dùng giờ mở nến vào/thoát", cl);
        }
        // #2 kịch bản xen kẽ: BẬT 0–7999, TẮT 8000–14999, BẬT từ 15000 (một engine, đổi công tắc giữa chừng như live)
        {
            string dir = Path.Combine(Path.GetTempPath(), "benzo_tester_p12_" + Guid.NewGuid().ToString("N").Substring(0, 6)); Directory.CreateDirectory(dir);
            string cp = Path.Combine(dir, BenzoCore.CacheFileName("GCZ26", "Time", 1));
            int n = 24000; var b = tb.Take(n).ToList(); var l = tl.Take(n).ToArray();
            var (eStd, _) = CorvenData.Run(b, l, 0.1, Deny);
            bool on = true;
            var c1 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c1.Load();
            var eng = new BenzoEngine("GCZ26", 0.1, c1, new ISetupDetector[] { new DetectorCorven { AllowBar = i => i >= Deny } }) { GetLevels = i => l[i], IsEnabled = _ => on };
            eng.Bars.AddRange(b);
            for (int i = 0; i < n; i++) { on = i < 8000 || i >= 15000; eng.Advance(i); }
            var c2 = new SignalCache(cp, BenzoCore.CacheVersion(true)); c2.Load();
            Console.WriteLine("  #2 khoảng niêm phong: " + string.Join(" ", c2.Intervals.Select(x => $"[{tb.FindIndex(y => y.Time.Ticks == x.F)}..{tb.FindIndex(y => y.Time.Ticks == x.L)}]")));
            Check(c2.Covers(b[100].Time.Ticks) && !c2.Covers(b[8000].Time.Ticks) && !c2.Covers(b[14999].Time.Ticks) && c2.Covers(b[15000].Time.Ticks) && c2.Covers(b[n - 1].Time.Ticks),
                  "#2: niêm phong phủ đoạn BẬT, chừa đúng đoạn TẮT 8000–14999");
            var (eRe, _) = CorvenData.Run(b, l, 0.1, Deny, cache: c2);   // nạp lại chart (bật): dò bù đoạn tắt
            Check(eRe.Signals.Select(x => (x.Id, x.Outcome)).SequenceEqual(eStd.Signals.Select(x => (x.Id, x.Outcome))), "#2: nạp lại sau đoạn tắt = chạy chuẩn (đủ lệnh, đủ kết cục)", $"{eRe.Signals.Count}/{eStd.Signals.Count}");
            int lostLive = eStd.Signals.Count(x => x.BarIdx >= 8000 && x.BarIdx < 15000) - eng.Signals.Count(x => x.BarIdx >= 8000 && x.BarIdx < 15000);
            Console.WriteLine($"  #2 lúc đang chạy (không nạp lại): đoạn tắt thiếu {lostLive} lệnh — đúng ý 'TẮT = tạm ngừng dò'");
            try { Directory.Delete(dir, true); } catch { }
        }
    }
}
