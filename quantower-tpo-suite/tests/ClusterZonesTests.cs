// Test lớp "Vùng cụm vol" (ClusterZones) — C# = Python (cz_ref.py) trên ca thật NQZ26 + GCZ26, cộng ca dựng tay
// cho tách phiên M15 và chống gửi Telegram trùng.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using TpoSuite;

static partial class Tests
{
    static string CzDir() => Path.GetFullPath(Path.Combine(AppContext.BaseDirectory,
        "../../../../research/vung_quan_trong_2026-11-25/fixture"));

    static DateTime Unix(long s) => DateTimeOffset.FromUnixTimeSeconds(s).UtcDateTime;

    static void ClusterZoneTests()
    {
        Console.WriteLine("\n[5] Vung cum vol - ca dung tay");
        var p = new CzParams();
        var t0 = new DateTime(2026, 11, 20, 22, 0, 0, DateTimeKind.Utc);
        // tách phiên: M15 liền nhau 15', nghỉ CME 60' (mở cách 75') ⇒ phiên mới; cách đúng 60' ⇒ chưa tách
        var bb = new List<CzBar> { new CzBar { T = t0 }, new CzBar { T = t0.AddMinutes(15) }, new CzBar { T = t0.AddMinutes(75) },
                                   new CzBar { T = t0.AddMinutes(150) }, new CzBar { T = t0.AddMinutes(210) } };
        var ss = ClusterZones.Sessions(bb, p.SessGapMin);
        Check(ss[1] == 0 && ss[2] == 0 && ss[3] == 1 && ss[4] == 1, "tach phien M15: cach > 60' moi tach", string.Join(",", ss));

        // cụm nặng nhất: profile 2 đỉnh, đỉnh dưới nặng hơn ⇒ lấy đỉnh dưới, dải không lan sang đỉnh trên
        var pr = Enumerable.Range(0, 60).Select(i => 100 + i * 0.2).ToArray();
        var vol = pr.Select((x, i) => 10.0 + 100 * Math.Exp(-Math.Pow((i - 15) / 3.0, 2)) + 60 * Math.Exp(-Math.Pow((i - 45) / 3.0, 2))).ToArray();
        var cl = ClusterZones.Cluster(pr, vol, 2.0, 0.2, p);
        Check(cl.HasValue && cl.Value.peak > 102.0 && cl.Value.peak < 104.0 && cl.Value.hi < 106.0, "cum nang nhat = dinh duoi, dai khong lan sang dinh tren",
              cl.HasValue ? $"{cl.Value.lo:0.0}-{cl.Value.hi:0.0} dinh {cl.Value.peak:0.0}" : "null");
        Check(ClusterZones.Cluster(pr.Take(3).ToArray(), vol.Take(3).ToArray(), 2.0, 0.2, p) == null, "it hon 5 hang -> khong co cum");

        // chống gửi trùng: chỉ lần chạm đang diễn ra, còn mới, và khoá chưa gửi
        var now = new DateTime(2026, 11, 25, 15, 0, 0, DateTimeKind.Utc);
        var z = new CzZone { Lo = 1, Hi = 2, Side = 1, Touch = 1, Live = true, EpT = now.AddMinutes(-15), Days = { t0 } };
        var sent = new HashSet<string>();
        bool a1 = ClusterZones.ShouldAlert(z, now, 30, sent, "NQZ26");
        sent.Add(ClusterZones.TouchKey("NQZ26", z));
        bool a2 = ClusterZones.ShouldAlert(z, now.AddMinutes(5), 30, sent, "NQZ26");
        Check(a1 && !a2, "bao Telegram dung 1 lan cho moi lan cham", $"{a1}/{a2}");
        Check(!ClusterZones.ShouldAlert(z, now.AddMinutes(40), 30, new HashSet<string>(), "NQZ26"), "lan cham cu (> 30') -> khong bao (mo chart giua chung)");
        var z2 = new CzZone { Lo = 1, Hi = 2, Side = 1, Touch = 1, Live = false, Days = { t0 } };
        Check(!ClusterZones.ShouldAlert(z2, now, 30, new HashSet<string>(), "NQZ26"), "vung chua cham -> khong bao");
        var z3 = new CzZone { Lo = 1, Hi = 2, Side = 1, Touch = 2, Live = true, EpT = now.AddMinutes(-5), Days = { t0 } };
        Check(ClusterZones.ShouldAlert(z3, now, 30, sent, "NQZ26"), "lan cham thu 2 (nen khac) -> bao rieng");
        Check(ClusterZones.Label(z, 7) == "Cụm vol 21/11 · hỗ trợ · đang chạm lần 1", "nhan vung", ClusterZones.Label(z, 7));

        Console.WriteLine("\n[5b] Vung cum vol - C# = Python (cz_ref.py) tren ca that NQZ26 + GCZ26");
        foreach (var name in new[] { "cz_nqy.json", "cz_gc.json" })
        {
            string path = Path.Combine(CzDir(), name);
            if (!File.Exists(path)) { Check(false, "doc " + name, path); continue; }
            using var doc = JsonDocument.Parse(File.ReadAllText(path));
            var root = doc.RootElement;
            double row = root.GetProperty("row").GetDouble();
            var jb = root.GetProperty("bars");
            var ts = jb.GetProperty("t").EnumerateArray().Select(x => x.GetInt64()).ToArray();
            var hs = jb.GetProperty("h").EnumerateArray().Select(x => x.GetDouble()).ToArray();
            var ls = jb.GetProperty("l").EnumerateArray().Select(x => x.GetDouble()).ToArray();
            var cs = jb.GetProperty("c").EnumerateArray().Select(x => x.GetDouble()).ToArray();
            var bars = Enumerable.Range(0, ts.Length).Select(i => new CzBar { T = Unix(ts[i]), H = hs[i], L = ls[i], C = cs[i] }).ToList();
            var days = root.GetProperty("days").EnumerateArray().Select(d => new CzDay
            {
                T0 = Unix(d.GetProperty("t0").GetInt64()), N30 = d.GetProperty("n30").GetInt32(),
                Prices = d.GetProperty("prices").EnumerateArray().Select(x => x.GetDouble()).ToArray(),
                Vols = d.GetProperty("vols").EnumerateArray().Select(x => x.GetDouble()).ToArray(),
            }).ToList();
            int ok = 0, tot = 0, nz = 0, nlive = 0; string bad = "";
            foreach (var c in root.GetProperty("cases").EnumerateArray())
            {
                tot++;
                int last = c.GetProperty("last").GetInt32();
                var sub = bars.Take(last + 1).ToList();
                var dd = days.Where(d => d.T0 <= sub[sub.Count - 1].T).ToList();
                var got = ClusterZones.Compute(sub, dd, row, p, out double u);
                var exp = c.GetProperty("zones").EnumerateArray().ToList();
                double ue = c.GetProperty("u").GetDouble();
                bool same = Math.Abs(u - ue) <= 1e-9 * Math.Max(1, Math.Abs(ue)) && got.Count == exp.Count;
                for (int i = 0; same && i < exp.Count; i++)
                {
                    var e = exp[i]; var g = got[i];
                    var eDays = e.GetProperty("days").EnumerateArray().Select(x => Unix(x.GetInt64())).ToList();
                    DateTime? eEp = e.GetProperty("ep_t").ValueKind == JsonValueKind.Null ? null : Unix(e.GetProperty("ep_t").GetInt64());
                    same = Math.Abs(g.Lo - e.GetProperty("lo").GetDouble()) < 1e-6 && Math.Abs(g.Hi - e.GetProperty("hi").GetDouble()) < 1e-6
                        && g.Side == e.GetProperty("side").GetInt32() && g.Touch == e.GetProperty("touch").GetInt32()
                        && g.Live == e.GetProperty("live").GetBoolean() && g.Nm == e.GetProperty("nm").GetInt32()
                        && Math.Abs(g.Imp - e.GetProperty("imp").GetDouble()) < 1e-6 && g.Days.SequenceEqual(eDays) && g.EpT == eEp;
                }
                nz += got.Count; nlive += got.Count(z0 => z0.Live);
                if (same) ok++; else if (bad.Length < 300) bad += $" ca {last}: C# {got.Count} vung u={u:0.000} / Py {exp.Count} u={ue:0.000};";
            }
            Check(ok == tot, $"{name}: {tot} thoi diem, {nz} vung ({nlive} dang cham) - C# = Python", $"{ok}/{tot}{bad}");
        }
    }
}
