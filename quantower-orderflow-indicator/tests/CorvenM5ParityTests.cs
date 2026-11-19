// Đối chiếu C# (CellBigLogic.Evaluate + ExhaustionLogic.Detect) với script Python research/corven_m5_2026-11-18/ (rules.py + final_eval.py)
// trên 26 nến M5 THẬT (12:15-14:20 UTC ngày 18/11/2026, file data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h*.csv).
// Mức nền (20 nến đã đóng trước) được làm nóng từ MỌI nến trước đó trong file, giống Python.
// Python xuất dấu ra research/corven_m5_2026-11-18/marks_python_26bars.csv (export_marks.py); test đòi TẬP (nến, tick, loại, màu) giống HỆT.
// Mong đợi: Dot 33 (10 xanh + 23 đỏ sau luật che), kiệt sức 13 (không so vòng mờ nữa: nay là Big Trade từ lệnh đơn, lịch sử không có số liệu). Không có file dữ liệu (chưa commit / máy khác) thì bỏ qua, không tính là lỗi.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using OrderFlowBubbles;

static class CorvenM5ParityTests
{
    static int _fail;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    static string FindUp(string rel)
    {
        for (var d = new DirectoryInfo(AppContext.BaseDirectory); d != null; d = d.Parent)
            if (File.Exists(Path.Combine(d.FullName, rel))) return Path.Combine(d.FullName, rel);
        return null;
    }

    static double P(string s) => double.Parse(s, CultureInfo.InvariantCulture);

    public static int Run()
    {
        string levelsCsv = FindUp("data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h.csv");
        string barsCsv = FindUp("data-export/data-footprint/fp_GCZ26_XCEC_Time_20261108-20261118_9d16h_bars.csv");
        string pyCsv = FindUp("quantower-orderflow-indicator/research/corven_m5_2026-11-18/marks_python_26bars.csv");
        if (levelsCsv == null || barsCsv == null || pyCsv == null) { Console.WriteLine("[M5] (bo qua doi chieu CORVEN M5: thieu file fp_..._9d16h.csv hoac marks_python_26bars.csv)"); return 0; }
        Console.WriteLine("[M5] Doi chieu C# voi Python tren 26 nen M5 that (CORVEN 18/11)");

        // per-level theo nến (đúng thứ tự file), tick = round(price x 10); Python: D = D[volume > 0]
        var lv = new Dictionary<string, List<CellLevel>>();
        var order = new List<string>();
        bool first = true;
        foreach (var line in File.ReadLines(levelsCsv))
        {
            if (first) { first = false; continue; }
            var f = line.Split(',');
            double vol = P(f[5]); if (vol <= 0) continue;
            string key = f[1].Substring(0, 16);
            if (!lv.TryGetValue(key, out var l)) { l = new List<CellLevel>(); lv[key] = l; order.Add(key); }
            l.Add(new CellLevel((long)Math.Round(P(f[2]) * 10), P(f[4]), P(f[3]), vol, (int)P(f[7])));   // buy = ask_vol (f[4]), sell = bid_vol (f[3])
        }
        var ohlc = new Dictionary<string, (long o, long h, long l, long c)>();
        first = true;
        foreach (var line in File.ReadLines(barsCsv))
        {
            if (first) { first = false; continue; }
            var f = line.Split(',');
            ohlc[f[1].Substring(0, 16)] = ((long)Math.Round(P(f[2]) * 10), (long)Math.Round(P(f[3]) * 10), (long)Math.Round(P(f[4]) * 10), (long)Math.Round(P(f[5]) * 10));
        }

        var sample = new HashSet<string>();
        for (int k = 0; k < 26; k++) sample.Add($"2026-11-18 {12 + (15 + 5 * k) / 60:00}:{(15 + 5 * k) % 60:00}");

        var bl = new CellBigBaseline(20);
        var set = new CellBigSettings();   // mặc định: 2,8 x trung vị / ±4 tick / che 6 / sàn 9
        var ex = new ExhSettings();         // mặc định: râu 3 / 6 mức / 1,1
        var cs = new HashSet<string>();
        int nDot = 0, nExh = 0, seen = 0;
        foreach (var key in order)
        {
            bool hasB = bl.TryGet(out double mean);
            bl.TryGetMedian(out double median);
            if (sample.Contains(key))
            {
                seen++;
                string t = key.Substring(11);
                foreach (var m in CellBigLogic.Evaluate(lv[key], bl.TryGetMedian(out double medB), medB, set))
                {
                    string col = m.Side > 0 ? "B" : "S";
                    nDot++; cs.Add($"{t},{m.Tick},dot,{col}");
                }
                if (ohlc.TryGetValue(key, out var b))
                {
                    var el = lv[key].Select(x => new ExhLevel(x.Tick, x.Sell, x.Buy, x.Vol)).ToList();
                    foreach (bool top in new[] { true, false })
                    {
                        var r = ExhaustionLogic.Detect(top, b.o, b.h, b.l, b.c, el, ex, hasB, mean);
                        if (r.Hit) { nExh++; cs.Add($"{t},{r.Tick},exh,{(top ? "T" : "B")}"); }
                    }
                }
            }
            if (CellBigLogic.BarStats(lv[key], out double bm, out double bmd)) bl.Add(bm, bmd);
        }

        var py = new HashSet<string>();
        first = true;
        foreach (var line in File.ReadLines(pyCsv))
        {
            if (first) { first = false; continue; }
            if (line.Trim().Length > 0) py.Add(line.Trim());
        }

        Check(seen == 26, "26 nen mau co trong file", seen.ToString());
        Check(nDot == 33, "Dot: 33 (nhu Python)", nDot.ToString());
        Check(cs.Count(x => x.Contains(",dot,B")) == 10 && cs.Count(x => x.Contains(",dot,S")) == 23, "10 xanh + 23 do", "");
        Check(nExh == 13, "kiet suc: 13 (nhu Python)", nExh.ToString());
        var onlyCs = cs.Except(py).OrderBy(x => x).ToList();
        var onlyPy = py.Except(cs).OrderBy(x => x).ToList();
        Check(onlyCs.Count == 0 && onlyPy.Count == 0, $"tap (nen, tick, loai, mau) C# == Python ({cs.Count} / {py.Count})",
              $"chi C#: [{string.Join(" ; ", onlyCs)}] chi Python: [{string.Join(" ; ", onlyPy)}]");
        Console.WriteLine(_fail == 0 ? "  -> M5: tat ca PASS" : $"  -> M5: {_fail} FAIL");
        return _fail;
    }
}
