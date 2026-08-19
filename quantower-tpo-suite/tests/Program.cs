// Test CHAY THAT tren Linux cho ProfileEngine — bien dich chinh file nguon dang
// dung de build DLL (../ProfileEngine.cs), khong phai ban sao. Chay:
//   dotnet run --project quantower-tpo-suite/tests
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using TpoSuite;

static class Tests
{
    static int _fail;

    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // ---- 1. ca dung tay: kiem tung luat mot ------------------------------
    static void UnitCases()
    {
        Console.WriteLine("[1] Cac ca dung tay cho LastSpliceIndex");
        var t0 = new DateTime(2026, 1, 1, 0, 0, 0);

        // khong co khoang nghi nao -> khong co cho noi
        var times = new List<DateTime>(); var op = new List<double>(); var cl = new List<double>();
        for (int i = 0; i < 10; i++) { times.Add(t0.AddMinutes(30 * i)); op.Add(100); cl.Add(100); }
        Check(ProfileEngine.LastSpliceIndex(times, op, cl, 0, 9, 20) == -1,
              "day lien tuc, khong nghi -> -1");

        // nghi 90 phut (nen M30 qua gio nghi CME) + nhay 60 -> bat duoc
        times[5] = times[4].AddMinutes(90);
        for (int i = 5; i < 10; i++) { times[i] = times[4].AddMinutes(90 + 30 * (i - 5)); op[i] = 160; cl[i] = 160; }
        Check(ProfileEngine.LastSpliceIndex(times, op, cl, 0, 9, 20) == 5,
              "nghi 90 phut + nhay 60 gia -> tra chi so 5");

        // cung the nhung nhay chi 8 gia -> duoi nguong, bo qua
        var op2 = new List<double>(op); var cl2 = new List<double>(cl);
        for (int i = 5; i < 10; i++) { op2[i] = 108; cl2[i] = 108; }
        Check(ProfileEngine.LastSpliceIndex(times, op2, cl2, 0, 9, 20) == -1,
              "nhay 8 gia (duoi nguong 20) -> -1");

        // nghi CUOI TUAN 46h + nhay 60 -> PHAI bo qua (khong phai cho noi)
        var tw = new List<DateTime>(times);
        for (int i = 5; i < 10; i++) tw[i] = tw[4].AddMinutes(46 * 60 + 30 * (i - 5));
        Check(ProfileEngine.LastSpliceIndex(tw, op, cl, 0, 9, 20) == -1,
              "nghi cuoi tuan 46h + nhay 60 gia -> -1 (khong cat nham)");

        // hai cho noi -> tra cai GAN NHAT (chi so lon hon)
        var t3 = new List<DateTime>(); var o3 = new List<double>(); var c3 = new List<double>();
        double px = 100;
        for (int i = 0; i < 12; i++)
        {
            var tt = t0.AddMinutes(30 * i);
            if (i == 3 || i == 8) { tt = tt.AddMinutes(60); px += 50; }
            t3.Add(tt); o3.Add(px); c3.Add(px);
        }
        // dung lai moc thoi gian cho dung (cong don do tre)
        for (int i = 1; i < 12; i++)
            if (t3[i] <= t3[i - 1]) t3[i] = t3[i - 1].AddMinutes(30);
        Check(ProfileEngine.LastSpliceIndex(t3, o3, c3, 0, 11, 20) == 8,
              "hai cho noi -> tra cai gan nhat (8)");

        // gioi han [from..to] phai duoc ton trong
        Check(ProfileEngine.LastSpliceIndex(t3, o3, c3, 0, 6, 20) == 3,
              "gioi han to=6 -> chi thay cho noi o 3");
        Check(ProfileEngine.LastSpliceIndex(t3, o3, c3, 9, 11, 20) == -1,
              "gioi han from=9 -> khong con cho noi nao");

        // dau vao rong / nguong 0 (tat chuc nang) -> -1, khong duoc nem loi
        Check(ProfileEngine.LastSpliceIndex(t3, o3, c3, 0, 11, 0) == -1, "nguong 0 (tat) -> -1");
        Check(ProfileEngine.LastSpliceIndex(null, null, null, 0, 5, 20) == -1, "dau vao null -> -1");
        Check(ProfileEngine.LastSpliceIndex(new List<DateTime>(), new List<double>(),
              new List<double>(), 0, 5, 20) == -1, "danh sach rong -> -1");
    }

    // ---- 2. chay tren DU LIEU THAT 2 nam ---------------------------------
    static void RealData()
    {
        Console.WriteLine("\n[2] Chay tren du lieu that /GC:XCEC 2024-08-01..2026-08-19");
        string path = Path.Combine(AppContext.BaseDirectory,
            "../../../../../data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv");
        path = Path.GetFullPath(path);
        if (!File.Exists(path))
        {
            Console.WriteLine("  BO QUA — chua giai nen file bars (" + path + ")");
            return;
        }
        var times = new List<DateTime>(); var op = new List<double>(); var cl = new List<double>();
        using (var r = new StreamReader(path))
        {
            var hdr = r.ReadLine().Split(',');
            int iT = Array.IndexOf(hdr, "datetime"), iO = Array.IndexOf(hdr, "open"), iC = Array.IndexOf(hdr, "close");
            string line;
            while ((line = r.ReadLine()) != null)
            {
                var c = line.Split(',');
                times.Add(DateTime.ParseExact(c[iT], "yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture));
                op.Add(double.Parse(c[iO], CultureInfo.InvariantCulture));
                cl.Add(double.Parse(c[iC], CultureInfo.InvariantCulture));
            }
        }
        Console.WriteLine($"  doc {times.Count:N0} nen M1");

        // quet toan bo, gom tat ca cho noi (khong chi cai cuoi)
        var found = new List<string>();
        for (int i = 1; i < times.Count; i++)
        {
            int k = ProfileEngine.LastSpliceIndex(times, op, cl, i, i, 20);
            if (k == i) found.Add(times[i].ToString("yyyy-MM-dd"));
        }
        found = found.Distinct().ToList();
        Console.WriteLine("  cho noi tim duoc: " + string.Join(", ", found));

        // Danh sach nay do bang Python (dense_prep.py) tren cung file — hai ban
        // doc lap phai ra CUNG ket qua thi moi tin duoc ban C#.
        var expect = new[] { "2025-03-27", "2025-04-22", "2025-05-28", "2025-07-29",
                             "2025-11-25", "2026-01-28", "2026-05-27", "2026-07-29" };
        Check(found.Count == expect.Length && !expect.Except(found).Any(),
              "khop danh sach cho noi do bang Python", $"C#={found.Count} ky vong={expect.Length}");

        // khong duoc bat nham vao nghi cuoi tuan
        int weekendHits = 0;
        for (int i = 1; i < times.Count; i++)
        {
            double gap = (times[i] - times[i - 1]).TotalMinutes;
            if (gap > 150 && Math.Abs(op[i] - cl[i - 1]) >= 20
                && ProfileEngine.LastSpliceIndex(times, op, cl, i, i, 20) == i) weekendHits++;
        }
        Check(weekendHits == 0, "khong bat nham khoang trong cuoi tuan", $"{weekendHits} ca");

        // nguong cang cao thi so cho noi cang it (don dieu) — kiem tinh nhat quan
        int Count(double thr)
        {
            int k = 0;
            for (int i = 1; i < times.Count; i++)
                if (ProfileEngine.LastSpliceIndex(times, op, cl, i, i, thr) == i) k++;
            return k;
        }
        int c10 = Count(10), c20 = Count(20), c40 = Count(40);
        Check(c10 >= c20 && c20 >= c40, "nguong cao hon -> it cho noi hon",
              $"x10={c10} x20={c20} x40={c40}");
    }

    static int Main()
    {
        Console.WriteLine("=== Test ProfileEngine (chay that, khong phai ban sao) ===");
        UnitCases();
        RealData();
        Console.WriteLine(_fail == 0 ? "\n=> TAT CA PASS" : $"\n=> CO {_fail} TEST HONG");
        return _fail == 0 ? 0 : 1;
    }
}
