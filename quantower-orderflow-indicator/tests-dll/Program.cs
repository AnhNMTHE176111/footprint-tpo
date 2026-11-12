// Kiểm tra DLL ĐÃ BUILD (dist/OrderFlowBubbles.dll) bằng phản chiếu: số tham số Settings, giá trị mặc định,
// và vòng đời đổi Settings (fix 2026-11-08). Chạy: dotnet run --project quantower-orderflow-indicator/tests-dll
using System; using System.Linq; using System.Reflection;
var t = typeof(OrderFlowBubbles.OrderFlowBubbles);
var props = t.GetProperties(BindingFlags.Public|BindingFlags.Instance).Where(p => p.GetCustomAttributes().Any(a => a.GetType().Name=="InputParameterAttribute")).ToList();
Console.WriteLine($"InputParameter count = {props.Count}");
foreach (var p in props) Console.WriteLine("  " + p.Name);
int fail = props.Count == 12 ? 0 : 1;
object o = null; try { o = Activator.CreateInstance(t); } catch (Exception e) { Console.WriteLine("Khong tao duoc instance: " + e.GetType().Name); }
if (o != null) {
  void chk(string n, object exp){ var v=t.GetProperty(n).GetValue(o); bool ok=Equals(v,exp); if(!ok) fail++; Console.WriteLine($"  {(ok?"OK  ":"FAIL")} {n} = {v} (mong doi {exp})"); }
  chk("DeltaFontSize",7); chk("DeltaYOffsetPx",8); chk("DLineEnabled",false); chk("DeltaMinBarWidthPx",6);
  chk("ImbalanceRatioPct",250); chk("ImbMinVolume",5.0); chk("ExhSmallRel",0.10); chk("BigTradeAbsFloor",50.0); chk("CellBigRatio",1.3); chk("CellBigBaselineBars",20); chk("CellBigMinSide",9.0); chk("CellBigPurpleMinWeak",3.0); chk("CellBigRowTicks",2); chk("CellBigRowOffset",1); chk("CellBigMergeTicks",0); chk("CellBigTopN",0); chk("AbsScoreMin",4); chk("BigTradeEnabled",true); chk("ExhaustionEnabled",true); chk("ImbalanceEnabled",true);
}

// ---- Lifecycle: bat/tat Settings -> Refresh -> OnClear -> phai tu mo lai co VA ----
var arm = t.GetMethod("ShouldArmVa", BindingFlags.NonPublic|BindingFlags.Static);
if (arm == null) { Console.WriteLine("FAIL khong thay ShouldArmVa"); fail++; }
else {
  void a(bool loaded, TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState? st, bool exp){ bool v=(bool)arm.Invoke(null,new object[]{loaded,st}); if(v!=exp) fail++; Console.WriteLine($"  {(v==exp?"OK  ":"FAIL")} ShouldArmVa({loaded},{st?.ToString()??"null"}) = {v}"); }
  a(false, TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState.Finished, true);
  a(true,  TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState.Finished, false);
  a(false, null, false);
  foreach (TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState s in Enum.GetValues(typeof(TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState)))
    if (s != TradingPlatform.BusinessLayer.VolumeAnalysisCalculationState.Finished) a(false, s, false);
}
if (o != null) {
  var f = t.GetField("_vaLoaded", BindingFlags.NonPublic|BindingFlags.Instance);
  f.SetValue(o, true);
  t.GetMethod("OnClear", BindingFlags.NonPublic|BindingFlags.Instance).Invoke(o, null);
  bool after = (bool)f.GetValue(o);
  bool ok = !after; if(!ok) fail++;
  Console.WriteLine($"  {(ok?"OK  ":"FAIL")} OnClear (Refresh khi doi Settings) dat _vaLoaded=false -> {after}");
  var pc = t.GetField("_processedClosedCount", BindingFlags.NonPublic|BindingFlags.Instance);
  pc.SetValue(o, 123);
  try { t.GetMethod("OnSettingsUpdated", BindingFlags.NonPublic|BindingFlags.Instance).Invoke(o, null); } catch (Exception e) { Console.WriteLine("  (base.Refresh ngoai nen tang: " + (e.InnerException?.GetType().Name ?? e.GetType().Name) + ")"); }
  int pcv=(int)pc.GetValue(o); bool ok2 = pcv==123; if(!ok2) fail++;
  Console.WriteLine($"  {(ok2?"OK  ":"FAIL")} OnSettingsUpdated KHONG tu dat lai _processedClosedCount (de Clear() lo) -> {pcv}");
}
// ---- perf 2026-11-11: SignalCache trong DLL (bo sinh san System.Text.Json chay duoc trong DLL, Put/Flush/Load/nen) ----
{
  var sct = typeof(OrderFlowBubbles.SignalCache);
  string tp = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "dll_sc_" + Guid.NewGuid() + ".jsonl");
  try {
    var c = new OrderFlowBubbles.SignalCache(tp);
    for (int r = 0; r < 3; r++) for (int i = 0; i < 20; i++) c.Put(new OrderFlowBubbles.CachedBarData { TimeTicks = 1000 + i, Tint = r, SettingsFingerprint = "fp" });
    c.Flush();
    int nlines = System.IO.File.ReadLines(tp).Count();
    var c2 = new OrderFlowBubbles.SignalCache(tp); c2.Load(true);   // 20 nen / 20 dong -> khong nen
    bool ok1 = nlines == 20 && c2.Count == 20 && c2.TryGet(1005, out var d) && d.Tint == 2;
    if (!ok1) fail++; Console.WriteLine($"  {(ok1?"OK  ":"FAIL")} DLL: Put x60 -> Flush -> {nlines} dong; Load -> {c2.Count} nen, ban ghi cuoi Tint=2");
    System.IO.File.AppendAllText(tp, System.IO.File.ReadAllText(tp));   // nhan doi dong -> 40 dong / 20 nen -> nen
    var c3 = new OrderFlowBubbles.SignalCache(tp); c3.Load(true);
    int after = System.IO.File.ReadLines(tp).Count();
    bool ok2 = c3.Count == 20 && after == 20;
    if (!ok2) fail++; Console.WriteLine($"  {(ok2?"OK  ":"FAIL")} DLL: file 40 dong/20 nen -> nen con {after} dong, {c3.Count} nen");
  } catch (Exception e) { fail++; Console.WriteLine("  FAIL DLL SignalCache: " + e); }
  finally { try { System.IO.File.Delete(tp); } catch { } }
}
Console.WriteLine(fail==0 ? "=== PASS ===" : $"=== {fail} FAIL ==="); return fail;
