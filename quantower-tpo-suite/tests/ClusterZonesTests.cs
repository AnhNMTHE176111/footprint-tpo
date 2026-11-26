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
        Check(ClusterZones.Label(z, 7) == "HVN ngày 21/11 · hỗ trợ · đang chạm lần 1", "nhan vung", ClusterZones.Label(z, 7));

        // gọi tên vùng: mức khác nằm trong vùng (± 0,1 U15) được ghép tên, mức xa thì không
        var zr = new CzZone { Lo = 25540, Hi = 25610, Side = -1, Touch = 1, Live = true, EpT = now, Days = { t0, t0.AddDays(1) } };
        var ex = new List<(string, double, double)> { ("HVN tuần", 25600, 25650), ("VWAP tuần", 25615, 25615), ("VWAP ngày", 25700, 25700) };
        zr.Desc = ClusterZones.Describe(zr, ex, 100, 7);
        Check(zr.Desc == "HVN ngày 21/11 + 22/11 + HVN tuần + VWAP tuần", "ten vung ghep HVN tuan + VWAP tuan (VWAP ngay xa -> khong ghep)", zr.Desc);
        string msg = ClusterZones.AlertText("NQZ26", zr, x => x.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture), 7);
        Check(msg == "NQZ26: giá chạm vùng kháng cự 25540.00–25610.00 – HVN ngày 21/11 + 22/11 + HVN tuần + VWAP tuần, canh sell", "tin cham vung khang cu -> canh sell", msg);
        z.Desc = null;
        Check(ClusterZones.AlertText("GCZ26", z, x => x.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture), 7).EndsWith(", canh buy"), "tin cham vung ho tro -> canh buy");

        Console.WriteLine("\n[5c] Tin buoi sang - gio VN, gio mua he / mua dong My");
        var ny = NewsCalendar.NewYork();
        Check(ny != null, "may co mui gio New York");
        // feed thật dạng Forex Factory: tuần 23–27/11/2026 (sau khi Mỹ lùi giờ 01/11) + một tin mùa hè để so
        string feed = "[{\"title\":\"Core PCE Price Index m/m\",\"country\":\"USD\",\"date\":\"2026-11-25T08:30:00-05:00\",\"impact\":\"High\",\"forecast\":\"0.2%\",\"previous\":\"0.2%\"},"
                    + "{\"title\":\"Bank Holiday\",\"country\":\"USD\",\"date\":\"2026-11-26T08:00:00-05:00\",\"impact\":\"Holiday\",\"forecast\":\"\",\"previous\":\"\"},"
                    + "{\"title\":\"FOMC Statement\",\"country\":\"USD\",\"date\":\"2026-11-25T14:00:00-05:00\",\"impact\":\"High\",\"forecast\":\"\",\"previous\":\"\"},"
                    + "{\"title\":\"BOJ Core CPI y/y\",\"country\":\"JPY\",\"date\":\"2026-11-25T00:00:00-05:00\",\"impact\":\"Low\",\"forecast\":\"\",\"previous\":\"\"}]";
        var evs = NewsCalendar.Parse(feed, 7);
        Check(evs.Count == 3, "loc tin: giu USD cao/vua + ngay nghi le My, bo JPY thap", evs.Count.ToString());
        var mUtc = new DateTime(2026, 11, 25, 0, 0, 0, DateTimeKind.Utc);        // 07:00 VN thứ Tư 25/11
        var ml = NewsCalendar.MorningLines(evs, mUtc, 7, ny, out bool mis);
        string all = string.Join("\n", ml);
        Check(all.Contains("• 20:30 ") && all.Contains("Core PCE"), "mua dong: 8:30 New York = 20:30 VN", all);
        Check(all.Contains("02:00 (rạng sáng 26/11)") && all.Contains("FOMC"), "14:00 New York = 02:00 VN hom sau, ghi ro rang sang", all);
        Check(all.Contains("UTC−5 (giờ mùa đông)") && all.Contains("= 20:30 VN"), "dong gio New York mua dong", ml.Count > 1 ? ml[1] : "");
        Check(!mis, "do lech feed khop mui gio New York");
        var ml2 = NewsCalendar.MorningLines(evs, new DateTime(2026, 11, 26, 0, 0, 0, DateTimeKind.Utc), 7, ny, out _);
        Check(ml2.Any(x => x.Contains("Mỹ nghỉ lễ")) && ml2.Any(x => x.Contains("Không có tin")), "26/11: bao My nghi le + khong co tin", string.Join(" | ", ml2));
        // mùa hè: 8:30 New York = 19:30 VN
        var evS = NewsCalendar.Parse("[{\"title\":\"CPI m/m\",\"country\":\"USD\",\"date\":\"2026-07-15T08:30:00-04:00\",\"impact\":\"High\",\"forecast\":\"\",\"previous\":\"\"}]", 7);
        var mlS = NewsCalendar.MorningLines(evS, new DateTime(2026, 7, 15, 0, 0, 0, DateTimeKind.Utc), 7, ny, out bool misS);
        Check(string.Join("\n", mlS).Contains("• 19:30 ") && string.Join("\n", mlS).Contains("UTC−4 (giờ mùa hè)") && !misS, "mua he: 8:30 New York = 19:30 VN", string.Join(" | ", mlS));
        // tuần đổi giờ: thứ Hai 02/11/2026 (Mỹ vừa lùi giờ 01/11) — feed ghi −05:00 thì khớp; feed ghi nhầm −04:00 thì cảnh báo
        var evX = NewsCalendar.Parse("[{\"title\":\"ISM Manufacturing PMI\",\"country\":\"USD\",\"date\":\"2026-11-02T10:00:00-04:00\",\"impact\":\"High\",\"forecast\":\"\",\"previous\":\"\"}]", 7);
        NewsCalendar.MorningLines(evX, new DateTime(2026, 11, 2, 0, 0, 0, DateTimeKind.Utc), 7, ny, out bool misX);
        Check(misX, "feed ghi sai do lech gio (−4 sau khi My da lui gio) -> canh bao");
        // lịch tuần cũ (tin cuối đã qua > 12 giờ, vd sáng thứ Hai) ⇒ chưa sẵn sàng, chờ tải lịch mới
        Check(!NewsCalendar.CoversNow(evs, new DateTime(2026, 11, 30, 0, 0, 0, DateTimeKind.Utc)) && NewsCalendar.CoversNow(evs, mUtc),
              "lich tuan cu sang thu Hai -> cho tai lai; giua tuan -> dung duoc");

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
