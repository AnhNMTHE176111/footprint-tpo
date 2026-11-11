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
  chk("ImbalanceRatioPct",250); chk("ImbMinVolume",5.0); chk("ExhSmallRel",0.10); chk("BigTradeAbsFloor",50.0); chk("CellBigRatio",1.3); chk("CellBigBaselineBars",20); chk("CellBigMinSide",3.0); chk("CellBigBalancedPct",0.75); chk("CellBigRowTicks",2); chk("CellBigRowOffset",1); chk("CellBigMergeTicks",0); chk("CellBigTopN",0); chk("AbsScoreMin",4); chk("BigTradeEnabled",true); chk("ExhaustionEnabled",true); chk("ImbalanceEnabled",true);
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
Console.WriteLine(fail==0 ? "=== PASS ===" : $"=== {fail} FAIL ==="); return fail;
