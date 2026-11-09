// CorvenData — nạp file Footprint Export (fp_<mã>_..._bars.csv + .csv per-level) và chạy BenzoEngine + DetectorCorven
// từng nến một. Dùng chung cho tools/ReplayCorven (parity) và tests (hồi quy ca [12]). Không phụ thuộc Quantower SDK.
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.IO;

    public static class CorvenData
    {
        static readonly CultureInfo Ci = CultureInfo.InvariantCulture;

        /// <summary>Nạp nến (bar_idx ≤ maxBar; −1 = hết file) + mức giá theo đúng thứ tự trong file.</summary>
        public static (List<BarData> bars, List<LevelVol>[] levels) Load(string prefix, int maxBar = -1)
        {
            var bars = new List<BarData>();
            string[] hdr = null;
            int iT = 0, iO = 0, iH = 0, iL = 0, iC = 0, iD = 0, iV = 0;
            foreach (var line in File.ReadLines(prefix + "_bars.csv"))
            {
                if (hdr == null)
                {
                    hdr = line.Split(',');
                    iT = Array.IndexOf(hdr, "datetime"); iO = Array.IndexOf(hdr, "open"); iH = Array.IndexOf(hdr, "high");
                    iL = Array.IndexOf(hdr, "low"); iC = Array.IndexOf(hdr, "close"); iD = Array.IndexOf(hdr, "delta"); iV = Array.IndexOf(hdr, "volume");
                    continue;
                }
                var p = line.Split(',');
                int bi = int.Parse(p[0], Ci);
                if (maxBar >= 0 && bi > maxBar) break;
                if (bi != bars.Count) throw new Exception("bar_idx không liên tục tại " + bi);
                bars.Add(new BarData
                {
                    Idx = bi,
                    Time = DateTime.SpecifyKind(DateTime.ParseExact(p[iT], "yyyy-MM-dd HH:mm:ss", Ci), DateTimeKind.Utc),
                    O = double.Parse(p[iO], Ci), H = double.Parse(p[iH], Ci), L = double.Parse(p[iL], Ci), C = double.Parse(p[iC], Ci),
                    Delta = double.Parse(p[iD], Ci), Vol = double.Parse(p[iV], Ci),
                });
            }
            var lv = new List<LevelVol>[bars.Count];
            for (int i = 0; i < lv.Length; i++) lv[i] = new List<LevelVol>();
            bool first = true;
            foreach (var line in File.ReadLines(prefix + ".csv"))
            {
                if (first) { first = false; continue; }
                int c1 = line.IndexOf(',');
                int bi = int.Parse(line.AsSpan(0, c1), NumberStyles.Integer, Ci);
                if (bi >= bars.Count) { if (maxBar >= 0) break; continue; }
                var p = line.Split(',');   // bar_idx,datetime,price,bid_vol,ask_vol,volume,...
                lv[bi].Add(new LevelVol(double.Parse(p[2], Ci), double.Parse(p[3], Ci), double.Parse(p[4], Ci), double.Parse(p[5], Ci)));
            }
            return (bars, lv);
        }

        /// <summary>Chạy engine TỪNG NẾN (Advance(i) lần lượt) rồi FinishSession. onBar(i, det) gọi sau mỗi nến (lấy ứng viên).</summary>
        public static (BenzoEngine eng, DetectorCorven det) Run(List<BarData> bars, List<LevelVol>[] levels, double tick = 0.1,
                                                              int denyBelow = 0, bool blockUs = true, SignalCache cache = null,
                                                              Action<int, DetectorCorven> onBar = null, bool oneShot = false)
        {
            var det = new DetectorCorven { BlockUsOpen = blockUs, AllowBar = i => i >= denyBelow };
            var eng = new BenzoEngine("GCZ26", tick, cache, new ISetupDetector[] { det }) { GetLevels = i => levels[i] };
            eng.Bars.AddRange(bars);
            if (oneShot) eng.Advance(bars.Count - 1);
            else
                for (int i = 0; i < bars.Count; i++)
                {
                    var r = eng.Advance(i);
                    if (r.CacheInvalid) throw new Exception(r.CacheWhy);
                    onBar?.Invoke(i, det);
                }
            eng.FinishSession();
            return (eng, det);
        }
    }
}
