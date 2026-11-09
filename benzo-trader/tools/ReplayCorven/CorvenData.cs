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
        /// <summary>Số lệnh bị engine HUỶ (vào ở nến cuối phiên) trong lần Run gần nhất.</summary>
        public static int LastCancelled;

        public const string TradesHeader = "idx,t_utc,the,side,range_id,b_from_exhausted,moc,so_dau_hieu,loai,dau_hieu,entry,sl,tp,r_san,ket_cuc,r,exit_idx";

        /// <summary>CSV lệnh cho parity. Lệnh có nến vào &gt; hideAfter (phần TEST) ghi TRỐNG 3 cột ket_cuc / r / exit_idx —
        /// kết cục TEST không bao giờ rời tiến trình (plan 10.6, sửa lỗi tester #1).</summary>
        public static string TradesCsv(IEnumerable<Signal> sigs, IReadOnlyDictionary<long, int> timeIdx, int hideAfter = int.MaxValue)
        {
            var ts = new System.Text.StringBuilder(TradesHeader).Append('\n');
            foreach (var s in sigs)
            {
                int ex = s.IsClosed && timeIdx != null && timeIdx.TryGetValue(s.ExitTime.Ticks, out int e) ? e : -1;
                bool hide = s.BarIdx > hideAfter;
                string outc = hide ? "" : s.Outcome;
                string rr = hide || !s.IsClosed ? "" : Math.Round(s.R, 3).ToString("R", Ci);
                string exs = hide ? "" : ex.ToString(Ci);
                ts.Append(s.BarIdx).Append(',').Append(s.Time.ToString("yyyy-MM-dd HH:mm", Ci)).Append(',').Append(s.Setup).Append(',')
                  .Append(s.Side > 0 ? "buy" : "sell").Append(',').Append(s.RangeId).Append(',').Append(s.BFromExhausted ? 1 : 0).Append(',')
                  .Append(SignalCsv.Q(s.Zone)).Append(',').Append(s.NSigns).Append(',').Append(SignalCsv.Q(s.SignTypes)).Append(',').Append(SignalCsv.Q(s.Signs)).Append(',')
                  .Append(s.Entry.ToString("R", Ci)).Append(',').Append(s.Sl.ToString("R", Ci)).Append(',').Append(s.Tp.ToString("R", Ci)).Append(',')
                  .Append(Math.Round(s.RAvail, 2).ToString("R", Ci)).Append(',')
                  .Append(outc).Append(',').Append(rr).Append(',').Append(exs).Append('\n');
            }
            return ts.ToString();
        }

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
                                                              Action<int, DetectorCorven> onBar = null, bool oneShot = false, CorvenCfg cfg = null)
        {
            var det = new DetectorCorven(cfg) { BlockUsOpen = blockUs, AllowBar = i => i >= denyBelow };
            var eng = new BenzoEngine("GCZ26", tick, cache, new ISetupDetector[] { det }) { GetLevels = i => levels[i] };
            eng.Bars.AddRange(bars);
            LastCancelled = 0;
            if (oneShot) LastCancelled += eng.Advance(bars.Count - 1).Cancelled.Count;
            else
                for (int i = 0; i < bars.Count; i++)
                {
                    var r = eng.Advance(i);
                    if (r.CacheInvalid) throw new Exception(r.CacheWhy);
                    LastCancelled += r.Cancelled.Count;
                    onBar?.Invoke(i, det);
                }
            LastCancelled += eng.FinishSession().Cancelled.Count;
            return (eng, det);
        }
    }
}
