// Kiểm tra DLL ĐÃ BUILD (dist/OrderFlowBubbles.dll) bằng phản chiếu: số tham số Settings, giá trị mặc định,
// và vòng đời đổi Settings (fix 2026-11-08). Chạy: dotnet run --project quantower-orderflow-indicator/tests-dll
using System; using System.Linq; using System.Reflection;
var t = typeof(OrderFlowBubbles.OrderFlowBubbles);
var props = t.GetProperties(BindingFlags.Public|BindingFlags.Instance).Where(p => p.GetCustomAttributes().Any(a => a.GetType().Name=="InputParameterAttribute")).ToList();
Console.WriteLine($"InputParameter count = {props.Count}");
foreach (var p in props) Console.WriteLine("  " + p.Name);
int fail = props.Count == 14 ? 0 : 1;   // 2026-11-26 ra Settings: an 8 o chinh tay (o lon, no moi muc, dung san, tu co dan, bo so, nen tu co, duoi kiet suc, keo dai vung) 22 -> 14. Truoc do: bo o "Ma NQ/MNQ gom 2 diem" (tu bat khi Theo CORVEN + NQ) 23 -> 22. 2026-11-25: +2 o che do nguong (ThresholdMode, StatRarePbp); Big Trade "lenh ca map": -4 o mat do (27 -> 23)
object o = null; try { o = Activator.CreateInstance(t); } catch (Exception e) { Console.WriteLine("Khong tao duoc instance: " + e.GetType().Name); }
if (o != null) {
  void chk(string n, object exp){ var v=t.GetProperty(n).GetValue(o); bool ok=Equals(v,exp); if(!ok) fail++; Console.WriteLine($"  {(ok?"OK  ":"FAIL")} {n} = {v} (mong doi {exp})"); }
  chk("DeltaFontSize",8); chk("ImbZoneMinPx",10); chk("ImbZoneOpacity",60); chk("BuyColor",System.Drawing.Color.FromArgb(0x4A,0x5A,0xF5)); chk("SellColor",System.Drawing.Color.FromArgb(0xE0,0x14,0x0A)); chk("DeltaYOffsetPx",8); chk("DLineEnabled",false); chk("DeltaMinBarWidthPx",6);
  chk("CellDotAllLevels",false); chk("CellDotFloorEnabled",true); chk("ImbalanceRatioPct",250); chk("ImbMinVolume",5.0); chk("BigTradeOpacity",35); chk("CellBigBaselineBars",20); chk("CellBigMinSide",9.0); chk("CellDotMedianRatio",2.8); chk("CellDotLocalTicks",4); chk("CellDotHideBuyNearSellTicks",6); chk("CellDotEnabled",true); chk("CellBigMergeTicks",0); chk("CellBigTopN",0); chk("BigTradeEnabled",true); chk("ExhaustionEnabled",true); chk("ImbalanceEnabled",true); chk("ImbMaxBars",20); chk("ImbFarBars",60);
  chk("CellDotAdaptive",true); chk("CellDotPreset",0); chk("AdaptiveBaseline",true);
  // 2026-11-26: kiet suc theo hang gia (ExhRowGrid), ve dau da bi quet KHONG mo
  chk("ExhDimInvalidated",false);
  { bool okp = t.GetProperty("ExhMinWickTicks")==null && t.GetProperty("ExhTailMedianRatio")==null; if(!okp) fail++; Console.WriteLine($"  {(okp?"OK  ":"FAIL")} bo tham so kiet suc cu (theo tick)"); }
  // 2026-11-26: cac o chinh tay da AN khoi Settings (giu mac dinh)
  foreach (var hn in new[]{"CellBigEnabled","CellDotAllLevels","CellDotFloorEnabled","CellDotAdaptive","CellDotPreset","AdaptiveBaseline","ImbMaxBars"}) {
    bool okh = !props.Any(p => p.Name == hn); if(!okh) fail++; Console.WriteLine($"  {(okh?"OK  ":"FAIL")} {hn} da an khoi Settings"); }
  // ---- 2026-11-25: che do nguong "Khong theo CORVEN (thong ke)" (research/stat_anomaly_2026-11-24/SPEC.md muc 6, 8.6) ----
  chk("ThresholdMode",0); chk("StatRarePbp",200); chk("StatDotDays",5); chk("StatDotNeighbors",true); chk("StatDotMinDays",2); chk("StatDotFallbackMinutes",120);
  foreach (var (pn, want) in new[] { ("ThresholdMode", 4), ("StatRarePbp", 6) })
  { var pa = t.GetProperty(pn).GetCustomAttributes().First(a => a.GetType().Name=="InputParameterAttribute");
    var vf = pa.GetType().GetProperties().FirstOrDefault(pp => pp.Name.ToLower().Contains("variant"));
    var vv = vf?.GetValue(pa) as System.Collections.IEnumerable; int nv = 0; if (vv != null) foreach (var _ in vv) nv++;
    bool okv = nv == want; if(!okv) fail++; Console.WriteLine($"  {(okv?"OK  ":"FAIL")} {pn} co {want/2} lua chon (variants {nv}/{want})"); }
  {
    const BindingFlags F = BindingFlags.NonPublic|BindingFlags.Instance;
    var fpo = Activator.CreateInstance(t);
    t.GetField("TestBarSource", F).SetValue(fpo, (Func<int, TradingPlatform.BusinessLayer.HistoryItemBar>)(i => null));
    string Fp(double m, int mode, int pbp) { t.GetField("TestBarMinutes", F).SetValue(fpo, m); t.GetProperty("ThresholdMode").SetValue(fpo, mode); t.GetProperty("StatRarePbp").SetValue(fpo, pbp); return (string)t.GetMethod("ComputeSettingsFingerprint", F).Invoke(fpo, null); }
    // dau van tay (2026-11-25, research/bigtrade_whale_2026-11-25/SPEC.md muc 6): Big Trade "lenh ca map" = "bigtrade-whale-v1:5/8/1380/<m>"
    // thay "10|bigtrade-v1" va bo "|bta-v1:..."; che do thong ke "|stat-v2:" bo hai so Big Trade. Moi phan khac giu nguyen tung ky tu.
    string Nw(string m) => "False|10|True|20|9|0|0|True|2.8|4|False|6|cellbig-v18|100|40|5|20|noabs-v1|True|0.3|3|0.8|True|bigvol-rows-v2:1/0/4.25/3.2/1.33/4.7|False|0.35|4|1|True|exh-rows-v1:1/0/3/0.35/0.8/2|1|True|250|3|5|False|3|1.5|3|False|8|False|True|60|60|8|3|2|5|stophunt-v8|nbase-v1:20|dotu-v2:0";
    void fc(bool ok, string name, string got) { if(!ok) fail++; Console.WriteLine($"  {(ok?"OK  ":"FAIL")} {name}" + (ok ? "" : " -> " + got)); }
    string a0 = Fp(5, 0, 200); fc(a0 == Nw("5"), "ThresholdMode = 0, m = 5: bigtrade-whale-v1:5/8/1380/5, khong con bta-v1", a0);
    string a1 = Fp(5, 1, 200); fc(a1 == Nw("5") + "|stat-v2:5/200/5/True/2/120", "ThresholdMode = 1, m = 5: them |stat-v2:5/200/5/True/2/120", a1);
    string a2 = Fp(5, 1, 100); fc(a2 != a1 && a2.EndsWith("|stat-v2:5/100/5/True/2/120"), "doi StatRarePbp -> dau van tay doi", a2);
    string b0 = Fp(0, 0, 200), b1 = Fp(0, 1, 200); fc(b0 == Nw("1") && b1 == b0, "m = 0 (khong phai nen thoi gian): Big Trade nhu m = 1, ThresholdMode = 1 y het che do cu", b1);
    string c1 = Fp(2.5, 1, 200); fc(c1 == Nw("2.5"), "ThresholdMode = 1, m = 2,5 (khong nguyen): cham nhu che do cu, Big Trade m = 2.5", c1);
    t.GetField("TestBarMinutes", F).SetValue(fpo, 5.0); t.GetProperty("ThresholdMode").SetValue(fpo, 0);
    string bkOld = (string)t.GetMethod("BaseKey", F).Invoke(fpo, null);
    t.GetProperty("ThresholdMode").SetValue(fpo, 1);
    string bkNew = (string)t.GetMethod("BaseKey", F).Invoke(fpo, null);
    fc(bkOld == "20" && bkNew == "20|stat:5/200/5/True/2/120", "BaseKey: \"20\" (bo Big Trade ca map), che do thong ke them |stat:...", bkOld + " / " + bkNew);
  }
  chk("StopHuntEnabled",true); chk("StopHuntBoxSmall",60); chk("StopHuntBoxLarge",60); chk("StopHuntBoxMaxMult",8.0); chk("StopHuntTolTicks",3); chk("StopHuntConfirmBars",2); chk("StopHuntCooldown",5);
  chk("CellBigStopHuntColor",System.Drawing.Color.MediumOrchid);
  try {
    var st = (System.Collections.IEnumerable)t.GetProperty("Settings").GetValue(o);
    object floor = null; foreach (var it in st) if ((string)it.GetType().GetProperty("Name").GetValue(it) == "CellBigMinSide") floor = it;
    var rel = floor?.GetType().GetProperty("Relation").GetValue(floor);
    bool ok = rel != null && rel.GetType().Name == "SettingItemRelationVisibility";
    if (!ok) fail++; Console.WriteLine($"  {(ok?"OK  ":"FAIL")} o San toi thieu chi hien khi bat (Relation = {rel?.GetType().Name ?? "null"})");
    object rare = null; foreach (var it in st) if ((string)it.GetType().GetProperty("Name").GetValue(it) == "StatRarePbp") rare = it;
    var rel2 = rare?.GetType().GetProperty("Relation").GetValue(rare);
    bool ok2 = rel2 != null && rel2.GetType().Name == "SettingItemRelationVisibility";
    if (!ok2) fail++; Console.WriteLine($"  {(ok2?"OK  ":"FAIL")} o Muc hiem chi hien khi chon Khong theo CORVEN (Relation = {rel2?.GetType().Name ?? "null"})");
  } catch (Exception e) { Console.WriteLine("  (bo qua kiem Settings ngoai Quantower: " + (e.InnerException ?? e).GetType().Name + ")"); }
  foreach (var gn in new[] { "CellBigRowTicks", "CellBigRowOffset", "CellBigRatio", "CellDotRatio", "ExhSumRel", "CellBigMaxSideRatio", "CellBigLocalTicks", "CellBigMinImbalance", "CellBigOpacity", "BigZ", "BigVolMult", "BigTradeTopN", "BigTradeRequireRealTrades", "BigTradeSkipOnAbsorption", "CellDotTradesRatio", "AbsorptionEnabled", "AbsEffortZ", "AbsScoreMin", "AbsMaxDisplaceTicks", "AbsorptionTopN", "AbsRangeRatio", "AbsImpactZ", "AbsSwingPeriod", "AbsPocProminence", "AbsDivergencePct", "AbsTwoSidedPct", "AbsMultiBarLookback", "AbsConfirmBars", "AbsBreakTicks", "WNoResult", "WProminent", "WDivergence", "WTwoSided", "WMulti", "WSwing", "CellBigSkipOnAbsorption", "BaselineTopLevels", "BigTradeFixedContracts", "BigTradeAbsFloor", "HaloTransparency", "BigTradeMinContracts", "BigTradeAdaptiveEnabled", "BigTradeDensity", "BigTradeFloor", "BigTradeMaxPerBar", "BigTradeCeil", "BigTradeMergeDiv", "BigTradeMergeMin", "StatBtMinutes", "StatBtRarePbp" }) { bool g2 = t.GetProperty(gn) == null; if(!g2) fail++; Console.WriteLine($"  {(g2?"OK  ":"FAIL")} {gn} da bo"); }
  { bool gone = t.GetProperty("StopHuntLookback") == null; if(!gone) fail++; Console.WriteLine($"  {(gone?"OK  ":"FAIL")} StopHuntLookback da bo"); }
}

// ---- Cỡ vẽ (px) của chấm / Big Trade: CellDrawSize(isDot, sizeFrac, barsW) ----
{
  var cds = t.GetMethod("CellDrawSize", BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static);
  if (cds == null) { Console.WriteLine("FAIL khong thay CellDrawSize"); fail++; }
  else {
    void d(bool dot, double fr, float w, int exp){ int v=(int)cds.Invoke(null,new object[]{dot,fr,w}); if(v!=exp) fail++; Console.WriteLine($"  {(v==exp?"OK  ":"FAIL")} CellDrawSize(dot={dot}, {fr}, {w}) = {v} (mong doi {exp})"); }
    d(false,0.6,20f,12); d(false,2.115,20f,42); d(false,2.115,40f,47); d(false,0.6,4f,8); d(false,0.6,60f,13);
    d(true,0.45,40f,10); d(true,0.45,5f,5); d(true,0.45,16f,7);
  }
}


// ---- Bản ghi niêm phong cũ có bóng Hấp thụ (Confirmable = true) phải bị BỎ khi nạp lại, không vẽ ----
{
  var fm = t.GetMethod("FromCachedBarData", BindingFlags.NonPublic|BindingFlags.Static);
  if (fm == null) { Console.WriteLine("FAIL khong thay FromCachedBarData"); fail++; }
  else {
    var cd = new OrderFlowBubbles.CachedBarData { TimeTicks = 1 };
    cd.Bubbles.Add(new OrderFlowBubbles.CachedBubbleData { Price = 1, Shape = 0, Confirmable = true, Confirm = 1, Tooltip = "Hap thu dinh" });
    cd.Bubbles.Add(new OrderFlowBubbles.CachedBubbleData { Price = 2, Shape = 0, CellBig = true, CellDot = true, CellSide = -1 });
    var res = (System.Collections.IList)fm.Invoke(null, new object[]{cd});
    bool ok = res.Count == 1; if(!ok) fail++;
    Console.WriteLine($"  {(ok?"OK  ":"FAIL")} nap ban ghi cu: bong Hap thu (Confirmable) bi bo, con {res.Count}/2 bong");
  }
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
