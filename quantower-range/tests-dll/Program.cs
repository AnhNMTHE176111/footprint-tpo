// Kiểm tra DLL ĐÃ BUILD (dist/RangeBox.dll) bằng phản chiếu: đúng 3 ô Settings, mặc định đúng, kế thừa Indicator,
// OnClear xoá logic (tính lại từ đầu), tham số logic = bộ chọn trong research/MEASURE.md.
// Chạy: dotnet run --project quantower-range/tests-dll   (build dist/RangeBox.dll trước)
using System; using System.Collections.Generic; using System.Linq; using System.Reflection; using TradingPlatform.BusinessLayer;
int fail = 0;
void ok(bool c, string n) { if (!c) fail++; Console.WriteLine($"  {(c ? "OK  " : "FAIL")} {n}"); }
var t = typeof(RangeBox.RangeBox);
ok(typeof(TradingPlatform.BusinessLayer.Indicator).IsAssignableFrom(t), "RangeBox kế thừa Indicator");
ok(!typeof(TradingPlatform.BusinessLayer.IVolumeAnalysisIndicator).IsAssignableFrom(t), "KHÔNG cài IVolumeAnalysisIndicator (chỉ OHLC)");
var props = t.GetProperties(BindingFlags.Public | BindingFlags.Instance)
    .Where(p => p.GetCustomAttributes().Any(a => a.GetType().Name == "InputParameterAttribute")).ToList();
Console.WriteLine($"InputParameter count = {props.Count}");
foreach (var p in props) Console.WriteLine("  " + p.Name);
ok(props.Count == 3, "đúng 3 ô Settings");
object o = null;
try { o = Activator.CreateInstance(t); } catch (Exception e) { Console.WriteLine("Khong tao duoc instance: " + e.GetType().Name); fail++; }
if (o != null)
{
    void chk(string n, object exp) { var v = t.GetProperty(n).GetValue(o); ok(Equals(v, exp), $"{n} = {v} (mong doi {exp})"); }
    chk("ShowBroken", true); chk("MarkFailBreak", true); chk("MarkStopHunt", false);
    var names = props.Select(p => p.GetCustomAttributes().First(a => a.GetType().Name == "InputParameterAttribute"))
                     .Select(a => (string)a.GetType().GetProperty("Name").GetValue(a)).ToList();
    ok(names.SequenceEqual(new[] { "Hiện range đã phá", "Đánh dấu fail break", "Đánh dấu râu quét cạnh" }), "nhãn Settings: " + string.Join(" | ", names));
    ok((string)t.GetProperty("Name").GetValue(o) == "Range Box", "Name = Range Box");
    var fLogic = t.GetField("_logic", BindingFlags.NonPublic | BindingFlags.Instance);
    var fFed = t.GetField("_fed", BindingFlags.NonPublic | BindingFlags.Instance);
    fLogic.SetValue(o, new RangeBox.RangeLogic(0.1)); fFed.SetValue(o, 500);
    t.GetMethod("OnClear", BindingFlags.NonPublic | BindingFlags.Instance).Invoke(o, null);
    ok(fLogic.GetValue(o) == null && (int)fFed.GetValue(o) == 0, "OnClear xoá logic + _fed=0 (tính lại từ đầu)");
}
var pr = new RangeBox.RangeParams();
ok(pr.MinBars == 8 && pr.HminK == 1.6 && pr.HmaxK == 6.0 && pr.TolK == 0.5 && pr.K == 3 && pr.G == 30 && !pr.PivotRuleB && pr.InsideRatio == 0.0 && pr.MaxLook == 60 && pr.MbrLen == 100 && pr.MaxReEntry == 2,
   "RangeParams mặc định = bộ chọn MEASURE.md (8 · 1,6 · 6 · 0,5 · K3 · G30 · luật A · MaxReEntry 2)");
// ---------------- vòng đời THẬT của RangeBox.Process qua HistoricalData giả (tester 2026-11-08, REVIEW-1 mục 3 + 13)
// HistoricalData.Count / indexer là virtual (ilspy) ⇒ lớp con giả lập được; Symbol.TickSize đọc trường double? riêng.
try { Lifecycle(); } catch (Exception e) { Console.WriteLine("  FAIL vòng đời: " + e); fail++; }

void Lifecycle()
{
    string root = AppContext.BaseDirectory; var d = new System.IO.DirectoryInfo(root);
    while (d != null && !System.IO.File.Exists(System.IO.Path.Combine(d.FullName, "RangeLogic.cs"))) d = d.Parent;
    string csv = System.IO.Path.Combine(d.FullName, "..", "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv");
    var lines = System.IO.File.ReadLines(csv).Take(2601).ToList();
    var hdr = lines[0].TrimStart('﻿').Split(',');
    int io_ = Array.IndexOf(hdr, "open"), ih = Array.IndexOf(hdr, "high"), il = Array.IndexOf(hdr, "low"), ic = Array.IndexOf(hdr, "close");
    var ci = System.Globalization.CultureInfo.InvariantCulture;
    var all = lines.Skip(1).Select((l, k) => { var f = l.Split(','); return (k, o: double.Parse(f[io_], ci), h: double.Parse(f[ih], ci), lo: double.Parse(f[il], ci), c: double.Parse(f[ic], ci)); }).ToList();
    HistoryItemBar Mk((int k, double o, double h, double lo, double c) x) => new HistoryItemBar { TicksLeft = new DateTime(2026, 7, 23, 0, 0, 0, DateTimeKind.Utc).AddMinutes(x.k).Ticks, Open = x.o, High = x.h, Low = x.lo, Close = x.c };

    var sym = new FakeSymbol(0.1);
    ok(sym.TickSize == 0.1, $"Symbol giả TickSize = {sym.TickSize}");
    var hd = new FakeHD(new HistoryRequestParameters { Symbol = sym });
    hd.Items.AddRange(all.Skip(100).Take(2000).Select(Mk));          // 2000 nến (nến cuối = đang chạy)
    var ind = new RangeBox.RangeBox();
    var t2 = typeof(RangeBox.RangeBox);
    typeof(Indicator).GetProperty("HistoricalData").GetSetMethod(true).Invoke(ind, new object[] { hd });
    var onUpd = t2.GetMethod("OnUpdate", BindingFlags.NonPublic | BindingFlags.Instance);
    var onClr = t2.GetMethod("OnClear", BindingFlags.NonPublic | BindingFlags.Instance);
    var fL = t2.GetField("_logic", BindingFlags.NonPublic | BindingFlags.Instance);
    RangeBox.RangeLogic Ref(IEnumerable<(int k, double o, double h, double lo, double c)> xs) { var r = new RangeBox.RangeLogic(0.1); foreach (var x in xs) r.Feed(x.o, x.h, x.lo, x.c); return r; }
    bool Same(RangeBox.RangeLogic a, RangeBox.RangeLogic b)
    {
        if (a == null || b == null || a.Events.Count != b.Events.Count || a.Count != b.Count) return false;
        for (int k = 0; k < a.Events.Count; k++) { var x = a.Events[k]; var y = b.Events[k]; if (x.Bar != y.Bar || x.Kind != y.Kind || x.Side != y.Side || x.Top != y.Top || x.Bottom != y.Bottom || x.RangeId != y.RangeId) return false; }
        return true;
    }
    // nạp lịch sử: Quantower gọi OnUpdate(HistoricalBar) Count lần, HistoricalData.Count = TỔNG số nến ngay từ lần đầu (ilspy: Indicator.Update chỉ tăng Indicator.Count)
    for (int k = 0; k < hd.Items.Count; k++) onUpd.Invoke(ind, new object[] { null });
    var lg = (RangeBox.RangeLogic)fL.GetValue(ind);
    var exp1 = Ref(all.Skip(100).Take(1999));
    ok(Same(lg, exp1), $"nạp lịch sử 2000 nến: logic = 1999 nến đã đóng ({exp1.Events.Count} sự kiện)");
    // nến mới (NewBar): nến 2000 vừa đóng phải được nạp, không bỏ sót
    hd.Items.Add(Mk(all[2100])); onUpd.Invoke(ind, new object[] { null });
    lg = (RangeBox.RangeLogic)fL.GetValue(ind);
    ok(lg.Count == 2000 && Same(lg, Ref(all.Skip(100).Take(2000))), $"NewBar: nến vừa đóng được nạp (logic.Count = {lg.Count})");
    // OnClear giữa chừng → OnUpdate lại ⇒ giống chạy mới
    onClr.Invoke(ind, null); onUpd.Invoke(ind, new object[] { null });
    lg = (RangeBox.RangeLogic)fL.GetValue(ind);
    ok(Same(lg, Ref(all.Skip(100).Take(2000))), "OnClear → OnUpdate: tính lại từ đầu, giống chạy mới");
    // tải thêm lịch sử bên trái (nến 0 đổi) ⇒ tính lại toàn bộ
    hd.Items.InsertRange(0, all.Take(100).Select(Mk)); onUpd.Invoke(ind, new object[] { null });
    lg = (RangeBox.RangeLogic)fL.GetValue(ind);
    ok(Same(lg, Ref(all.Take(2100))), $"tải thêm 100 nến bên trái: tính lại, logic.Count = {lg?.Count} (mong đợi 2100)");
    // nến NaN (HistoryItemBar mặc định NaN) giữa chuỗi: không ngoại lệ, chỉ số vẫn khớp
    hd.Items.Add(new HistoryItemBar { TicksLeft = hd.Items[^1].TicksLeft + TimeSpan.TicksPerMinute });
    hd.Items.Add(Mk(all[2101 % all.Count])); hd.Items[^1].TicksLeft = hd.Items[^2].TicksLeft + TimeSpan.TicksPerMinute;
    onUpd.Invoke(ind, new object[] { null });
    lg = (RangeBox.RangeLogic)fL.GetValue(ind);
    ok(lg.Count == hd.Items.Count - 1, $"nến NaN: vẫn nạp, logic.Count = {lg.Count} = số nến đã đóng {hd.Items.Count - 1}");
}

Console.WriteLine(fail == 0 ? "=== PASS ===" : $"=== {fail} FAIL ==="); return fail;

sealed class FakeSymbol : Symbol
{
    public FakeSymbol(double tick) : base()
    {
        foreach (var f in typeof(Symbol).GetFields(BindingFlags.NonPublic | BindingFlags.Instance).Where(f => f.FieldType == typeof(double?)))
        {
            f.SetValue(this, tick);
            if (TickSize == tick) return;
            f.SetValue(this, null);
        }
    }
}

sealed class FakeHD : HistoricalData
{
    public readonly List<HistoryItemBar> Items = new();
    public FakeHD(HistoryRequestParameters p) : base(p) { }
    public override int Count => Items.Count;
    public override IHistoryItem this[int offset, SeekOriginHistory origin = SeekOriginHistory.End]
        => origin == SeekOriginHistory.Begin ? Items[offset] : Items[Items.Count - 1 - offset];
}
