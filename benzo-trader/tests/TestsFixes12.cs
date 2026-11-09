// Test cho lượt sửa lỗi tester GĐ4 (plans/BENZO-CORVEN-plan.md mục 12, việc 12.4).
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using BenzoTraderNs;

static partial class Program
{
    static void TestFixes12()
    {
        Console.WriteLine("[F1] ReplayCorven --hide-after: 2 lệnh sau cut ghi trống ket_cuc/r/exit_idx, lệnh trước cut có số (12.1 #1)");
        {
            Signal Mk(int idx, string outc, double r)
            {
                var s = new Signal { Setup = 'A', Side = 1, Entry = 100, Sl = 98, Tp = 104, Outcome = outc, R = r, Zone = "canh", Signs = "x", SignTypes = "Δ+bóng", NSigns = 2 };
                BenzoCore.Finalize(s, "GCZ26", T0.AddMinutes(idx)); s.Outcome = outc; s.R = r; s.ExitTime = T0.AddMinutes(idx + 3); s.BarIdx = idx;
                return s;
            }
            var sigs = new[] { Mk(10, "SL", -1.1), Mk(60, "TP", 1.9), Mk(70, "SL", -1.1) };
            var tIdx = new Dictionary<long, int> { [T0.AddMinutes(13).Ticks] = 13, [T0.AddMinutes(63).Ticks] = 63, [T0.AddMinutes(73).Ticks] = 73 };
            var lines = CorvenData.TradesCsv(sigs, tIdx, 50).TrimEnd('\n').Split('\n');
            string[] Tail(string l) { var p = l.Split(','); return p.Skip(p.Length - 3).ToArray(); }
            Check(lines.Length == 4 && lines[0] == CorvenData.TradesHeader, "header + 3 dòng");
            Check(Tail(lines[1]).SequenceEqual(new[] { "SL", "-1.1", "13" }), "lệnh trước cut: có kết cục, R, nến thoát", lines[1]);
            Check(Tail(lines[2]).All(x => x == "") && Tail(lines[3]).All(x => x == ""), "2 lệnh sau cut: 3 ô rỗng", lines[2] + " | " + lines[3]);
            Check(Tail(CorvenData.TradesCsv(sigs, tIdx).TrimEnd('\n').Split('\n')[3])[0] == "SL", "không --hide-after: ghi đủ (dùng cho TRAIN)");
        }

        Console.WriteLine("[F2] Cổng: danh sách chính thức = GateVn + ③ + 3 cổng detector/engine; README liệt kê đúng tập đó (12.1-7a, Q1, Q2)");
        {
            var mapped = CorvenRules.GateCodes.Select(g => CorvenRules.GateVn(g)).Distinct().ToList();
            Check(mapped.All(x => CorvenRules.AllGateLabels.Contains(x)), "mọi giá trị GateVn nằm trong danh sách", string.Join(";", mapped));
            Check(CorvenRules.GateVn("cuoi_phien") == "cuối phiên" && !CorvenRules.AllGateLabels.Contains("setup tắt"), "có 'cuối phiên', bỏ 'setup tắt'");
            string root = RepoRoot();
            string readme = root == null ? "" : File.ReadAllText(Path.Combine(root, "benzo-trader", "README.md"));
            int at = readme.IndexOf("`gate` ∈", StringComparison.Ordinal);
            var listed = new List<string>();
            if (at >= 0)
            {
                string seg = readme.Substring(at + 9, Math.Min(600, readme.Length - at - 9));
                seg = seg.Substring(0, seg.IndexOf('.') >= 0 ? seg.IndexOf('.') : seg.Length);
                foreach (Match m in Regex.Matches(seg, "`([^`]+)`")) listed.Add(m.Groups[1].Value);
            }
            Check(listed.Count > 0 && new HashSet<string>(listed).SetEquals(CorvenRules.AllGateLabels), "README = đúng danh sách cổng", string.Join(" | ", listed));
        }

        Console.WriteLine("[F3] Cổng cuối phiên: CF ở sm 1379 có cổng, sm 1378 không (12.2-Q2)");
        {
            var (f1, _) = World(Ex1Rows(), start: new DateTime(2026, 9, 1, 20, 41, 0, DateTimeKind.Utc));   // nến 18 mở 20:59 UTC = 16:59 ET
            var c1 = Eval(Ex1Cand(), f1);
            var (f0, _) = World(Ex1Rows(), start: new DateTime(2026, 9, 1, 20, 40, 0, DateTimeKind.Utc));
            var c0 = Eval(Ex1Cand(), f0);
            Check(f1.Sm[18] == 1379 && c1.Gates.Contains("cuoi_phien") && new DetectorCorven().FirstGate(c1, false) == "cuối phiên", "sm 1379 ⇒ cổng 'cuối phiên'", f1.Sm[18] + " " + string.Join(";", c1.Gates));
            Check(f0.Sm[18] == 1378 && !c0.Gates.Contains("cuoi_phien"), "sm 1378 ⇒ không", f0.Sm[18].ToString());
        }

        Console.WriteLine("[F4] sm chỉ phụ thuộc UTC (12.1 #5)");
        {
            var t = new DateTime(2026, 9, 1, 12, 25, 0, DateTimeKind.Utc);
            var z7 = new BenzoZones { TzOffset = 7 }; var z8 = new BenzoZones { TzOffset = 8 };
            z7.Push(0, new BarData { Time = t }); z8.Push(0, new BarData { Time = t });
            Check(z7.Sm == z8.Sm && z7.Sm == BenzoKernel.SmOf(t) && z7.Sm == 865, "Lệch giờ 7 hay 8: cùng sm 865 (19:25 VN giờ hè Mỹ)", $"{z7.Sm}/{z8.Sm}");
        }

        Console.WriteLine("[F5] Nhãn lệnh lật sang trái khi tràn mép phải (12.1 #3)");
        {
            Check(BenzoCore.LabelX(100, 50, 0, 400) == 108, "vừa: xE + 8");
            Check(BenzoCore.LabelX(380, 50, 0, 400) == 322, "tràn phải: lật sang trái xE − 8 − w");
            Check(BenzoCore.LabelX(40, 300, 0, 200) == 2, "chart hẹp: kẹp mép trái + 2");
        }

        string root2 = RepoRoot();
        string prefix = root2 == null ? null : Path.Combine(root2, "data-export", "data-footprint", "fp_GCZ26_XCEC_Time_20260723-20261021_90d");
        if (prefix == null || !File.Exists(prefix + "_bars.csv")) { Check(false, "không thấy file 90d cho [F6]–[F8]"); return; }
        const int Deny = 3697;
        var (b, l) = CorvenData.Load(prefix, 23999);      // 24.000 nến đầu, toàn TRAIN

        Console.WriteLine("[F6] Lệch giờ 7 → 8: 0 lệnh khác trên 24.000 nến (12.1 #5)");
        {
            var (e7, _) = CorvenData.Run(b, l, 0.1, Deny);
            var det8 = new DetectorCorven { AllowBar = i => i >= Deny };
            var e8 = new BenzoEngine("GCZ26", 0.1, null, new ISetupDetector[] { det8 }) { GetLevels = i => l[i], TzOffset = 8 };
            e8.Bars.AddRange(b);
            for (int i = 0; i < b.Count; i++) e8.Advance(i);
            e8.FinishSession();
            int diff = e7.Signals.Select(x => x.Id).Except(e8.Signals.Select(x => x.Id)).Count() + e8.Signals.Select(x => x.Id).Except(e7.Signals.Select(x => x.Id)).Count();
            Check(e7.Signals.Count > 20 && diff == 0, "0 lệnh khác", $"{diff} khác / {e7.Signals.Count}");
        }

        Console.WriteLine("[F7] Công tắc setup: TẮT tới nến 15000 rồi BẬT — lịch sử không mất; rng không phủ đoạn tắt (12.1 #2)");
        {
            string cp = Tmp("cache_toggle.jsonl");
            var (e0, _) = CorvenData.Run(b, l, 0.1, Deny);
            int mid = 15000;
            var cA = new SignalCache(cp, BenzoCore.CacheVersion()); cA.Load();
            var detA = new DetectorCorven { AllowBar = i => i >= Deny };
            var engA = new BenzoEngine("GCZ26", 0.1, cA, new ISetupDetector[] { detA }) { GetLevels = i => l[i], IsEnabled = _ => false };
            engA.Bars.AddRange(b.Take(mid));
            for (int i = 0; i < mid; i++) engA.Advance(i);
            var cChk = new SignalCache(cp, BenzoCore.CacheVersion()); cChk.Load();
            Check(!cChk.Covers(b[100].Time.Ticks) && !cChk.Covers(b[mid - 1].Time.Ticks), "nến chạy lúc TẮT không được niêm phong");
            var cB = new SignalCache(cp, BenzoCore.CacheVersion()); cB.Load();
            var (eOn, _) = CorvenData.Run(b, l, 0.1, Deny, cache: cB);
            int want = e0.Signals.Count(x => x.BarIdx < mid), got = eOn.Signals.Count(x => x.BarIdx < mid);
            Check(want == 58 && got == 58 && eOn.Signals.Select(x => x.Id).SequenceEqual(e0.Signals.Select(x => x.Id)), "bật lại: 58/58 lệnh trước nến 15000 có lại, toàn bộ = chạy chuẩn", $"{got}/{want}");

            // đang TẮT nhưng cache đã có lệnh ⇒ lệnh vẫn hiện (bảng đếm được), không dò mới
            var cC = new SignalCache(cp, BenzoCore.CacheVersion()); cC.Load();
            var detC = new DetectorCorven { AllowBar = i => i >= Deny };
            var engC = new BenzoEngine("GCZ26", 0.1, cC, new ISetupDetector[] { detC }) { GetLevels = i => l[i], IsEnabled = _ => false };
            engC.Bars.AddRange(b);
            var rC = engC.Advance(b.Count - 1);
            var st = BenzoCore.ComputeStats(engC.Signals);
            Check(!rC.CacheInvalid && engC.Signals.Count == eOn.Signals.Count && st.Total.N + st.Total.Open == eOn.Signals.Count,
                  "đang TẮT: mọi lệnh đã niêm phong vẫn hiện và được đếm", $"{engC.Signals.Count}/{eOn.Signals.Count}");
        }
    }
}
