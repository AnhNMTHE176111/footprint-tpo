// ============================================================================
//  ParityHarness — chay LOGIC C# CBR (KB1) HEADLESS tren Linux de kiem parity voi Python.
// ============================================================================
//  VI SAO CAN FILE NAY: GD9 cam "tuyen bo parity dua tren doc code". Quantower chi chay tren
//  Windows, nen khong the chay WyckoffRunner.dll o day. Giai phap: copy NGUYEN VAN cac ham
//  tinh toan cua WyckoffRunner.cs (BuildBars/Gate/TrendOk/VwapOk/LiqOk/NoCounterSweep/Scan/
//  Dedup/Cooldown_/InDeadWindow) vao mot chuong trinh console, cho an CUNG file CSV ma Python
//  doc, roi so tung tin hieu.
//
//  ⚠ GIOI HAN PHAI NOI RO: day la parity giua *THUAT TOAN C#* va *THUAT TOAN PYTHON*, KHONG
//  phai parity giua *DLL chay trong Quantower* va Python. Nhung khac biet do Quantower gay ra
//  (loc nen rac, nen thieu, volume tu VolumeAnalysis khac dxFeed, timezone cua feed) KHONG
//  duoc kiem o day — phai kiem o GD10 bang CSV live thuc. Xem PARITY_V7.md muc "chua kiem duoc".
//
//  Cach dong bo: neu sua logic trong WyckoffRunner.cs thi PHAI sua o day. Cac khoi duoi day
//  duoc danh dau "<<< COPY tu WyckoffRunner.cs" kem so dong goc de doi chieu.
//
//  Chay: dotnet run --project . -- <duong-dan-csv>
// ============================================================================
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

class Bar
{
    public int Idx;
    public DateTime Time;
    public double O, H, L, C, Vol, Vwap, Vma, Vratio, LiqRatio, Rng, Body, Brat, Cpos;
    public int Trend, SinceGap;
}

class Sig
{
    public int Idx; public int Side; public double Entry, Sl, Risk; public DateTime Time;
}

static class Parity
{
    // ---------- cau hinh DONG BANG (AUDIT_V7 §14). Doi o day = doi ket qua. ----------
    const double _tick = 0.1;          // vang: 1 tick = 0.1 ; 1 "gia" = 10 tick
    const int VsaPeriod = 20;
    const int RangeLen = 8;
    const double RangeMinPts = 3.0, RangeMaxPts = 7.5;
    const double BreakVsa = 2.0, BreakBody = 0.50;
    const int WaitBars = 12;
    const double PullMin = 0.60, PullMax = 1.00;
    const int HoldTolTicks = 2;
    const double ResumeBody = 0.35;
    const double SlFloorPts = 3.0, SlCapPts = 7.0;
    const int SlBuf = 2;
    const int Cooldown = 15, DedupBars = 6;
    const double RR = 4.0;
    const bool TrendFilter = true; const int TrendBars = 480; const double TrendTolPts = 1.0;
    const bool VwapAlign = true;
    const bool LiquidityFilter = true; const double LiquidityRatio = 0.75; const int LiquidityWindow = 1000;
    const bool CleanBreak = true; const int CleanLook = 20, CleanWin = 5; const double CleanClosePos = 0.50;
    const bool SkipDeadSession = true; const bool DeadUseUtc = true;
    const int DeadStartHour = 2, DeadEndHour = 8;
    const double VolFloor = 20.0;      // v7: so cung, sua look-ahead (AUDIT_V7 §1.2)
    const int WarmupBars = 20;
    const bool EnableReversal = false; // v7: KB2 TAT (AUDIT_V7 §13)

    // ---------- <<< COPY tu WyckoffRunner.cs BuildBars() (dong ~496-520) ----------
    static List<Bar> BuildBars(List<(DateTime t, double o, double h, double l, double c, double v)> rows)
    {
        var B = new List<Bar>();
        double csPV = 0, csV = 0, rollSum = 0, liqSum = 0;
        var q = new Queue<double>();
        var lq = new Queue<double>();
        for (int i = 0; i < rows.Count; i++)
        {
            var r = rows[i];
            var b = new Bar { Idx = i, Time = r.t, O = r.o, H = r.h, L = r.l, C = r.c, Vol = r.v };
            B.Add(b);
            bool gap = i > 0 && (b.Time - B[i - 1].Time).TotalMinutes > 30;
            if (gap) { csPV = 0; csV = 0; }
            double tp = (b.H + b.L + b.C) / 3.0; csPV += tp * b.Vol; csV += b.Vol;
            b.Vwap = csV > 0 ? csPV / csV : b.C;
            q.Enqueue(b.Vol); rollSum += b.Vol;
            if (q.Count > VsaPeriod) rollSum -= q.Dequeue();
            b.Vma = q.Count > 0 ? rollSum / q.Count : b.Vol;
            b.Vratio = b.Vma > 1e-9 ? b.Vol / b.Vma : 0;
            // v7 SUA PARITY: mean cua VMA va CO gom nen hien tai (khop Python add_liqbase)
            lq.Enqueue(b.Vma); liqSum += b.Vma;
            if (lq.Count > LiquidityWindow) liqSum -= lq.Dequeue();
            double liqMean = lq.Count > 0 ? liqSum / lq.Count : b.Vol;
            b.LiqRatio = liqMean > 1e-9 ? b.Vma / liqMean : 1.0;
            if (i >= TrendBars) { double d = b.C - B[i - TrendBars].C; b.Trend = d > TrendTolPts ? 1 : d < -TrendTolPts ? -1 : 0; }
            else b.Trend = 0;
            b.SinceGap = gap ? 0 : (i > 0 ? B[i - 1].SinceGap + 1 : 999);
            b.Rng = b.H - b.L; b.Body = Math.Abs(b.C - b.O);
            b.Brat = b.Rng > 0 ? b.Body / b.Rng : 0.0;
            b.Cpos = b.Rng > 0 ? (b.C - b.L) / b.Rng : 0.5;
        }
        return B;
    }

    // ---------- <<< COPY cac gate (dong ~519-530) ----------
    static bool Gate(Bar b) => b.Vol >= VolFloor && b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;
    static bool TrendOk(Bar b, int side) => !TrendFilter || b.Trend == side;
    static bool VwapOk(Bar b, int side) => !VwapAlign || (side > 0 ? b.C >= b.Vwap : b.C <= b.Vwap);
    static bool LiqOk(Bar b) => !LiquidityFilter || b.LiqRatio >= LiquidityRatio;

    static bool InDeadWindow(DateTime tUtc)
    {
        // DeadUseUtc = true trong cau hinh dong bang => dung truc tiep gio UTC.
        // (Ban C# goc: h = DeadUseUtc ? tUtc.Hour : tUtc.AddHours(TzOffset).Hour)
        int h = tUtc.Hour;
        // Khung 02-08 khong vat qua nua dem; nhanh else giu de khop nguyen van ban goc.
        return DeadStartHour <= DeadEndHour
            ? (h >= DeadStartHour && h < DeadEndHour)
            : (h >= DeadStartHour || h < DeadEndHour);
    }

    // ---------- <<< COPY NoCounterSweep() (dong ~745-770) ----------
    static bool NoCounterSweep(List<Bar> B, int i, bool up)
    {
        if (!CleanBreak) return true;
        int from = Math.Max(VsaPeriod, i - CleanLook) + CleanWin;
        for (int k = from; k < i; k++)
        {
            var b = B[k];
            if (b.Rng <= 0) continue;
            if (k - CleanWin < 0) continue;
            if (up)
            {
                double loc = double.MaxValue;
                for (int m = k - CleanWin; m < k; m++) if (B[m].L < loc) loc = B[m].L;
                if (b.L < loc - _tick && b.C > loc && b.Cpos >= CleanClosePos) return false;
            }
            else
            {
                double loc = double.MinValue;
                for (int m = k - CleanWin; m < k; m++) if (B[m].H > loc) loc = B[m].H;
                if (b.H > loc + _tick && b.C < loc && b.Cpos <= 1.0 - CleanClosePos) return false;
            }
        }
        return true;
    }

    // ---------- <<< COPY Scan() nhanh CBR (dong ~647-717) ----------
    static List<Sig> Scan(List<Bar> B)
    {
        var raw = new List<Sig>();
        int nClosed = B.Count - 1;
        double rangeMinT = RangeMinPts / _tick, rangeMaxT = RangeMaxPts / _tick;
        double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick;

        for (int i = VsaPeriod + 2; i < nClosed; i++)
        {
            var b = B[i];
            if (!Gate(b)) continue;
            if (i < RangeLen) continue;
            double rhi = double.MinValue, rlo = double.MaxValue;
            for (int k = i - RangeLen; k < i; k++) { if (B[k].H > rhi) rhi = B[k].H; if (B[k].L < rlo) rlo = B[k].L; }
            double span = (rhi - rlo) / _tick;
            if (span > rangeMaxT || span < rangeMinT) continue;

            bool up = b.C > rhi + SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C > b.O;
            bool dn = b.C < rlo - SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C < b.O;
            if (!(up || dn)) continue;
            if (!NoCounterSweep(B, i, up)) continue;
            int side = up ? +1 : -1;
            double edge = up ? rhi : rlo;

            double peak = up ? b.H : b.L; int since = i;
            int jEnd = Math.Min(nClosed, i + 1 + WaitBars);
            for (int j = i + 1; j < jEnd; j++)
            {
                var bj = B[j];
                if (!Gate(bj)) break;
                if (up ? bj.C < edge - HoldTolTicks * _tick : bj.C > edge + HoldTolTicks * _tick) break;

                if (j >= since + 1)
                {
                    double pullExt = up ? double.MaxValue : double.MinValue;
                    for (int k = since + 1; k <= j; k++) { if (up) { if (B[k].L < pullExt) pullExt = B[k].L; } else { if (B[k].H > pullExt) pullExt = B[k].H; } }
                    double leg = up ? (peak - edge) : (edge - peak);
                    double depth = up ? (peak - pullExt) : (pullExt - peak);
                    double retr = leg > 0 ? depth / leg : 0;
                    bool held = up ? pullExt >= edge - HoldTolTicks * _tick : pullExt <= edge + HoldTolTicks * _tick;
                    bool resume = (up ? (bj.C > B[j - 1].H && bj.C > bj.O) : (bj.C < B[j - 1].L && bj.C < bj.O)) && bj.Brat >= ResumeBody;
                    if (j >= since + 2 && retr >= PullMin && retr <= PullMax && held && resume)
                    {
                        double entry = bj.C, sl, risk;
                        if (up) { sl = pullExt - SlBuf * _tick; risk = (entry - sl) / _tick; }
                        else { sl = pullExt + SlBuf * _tick; risk = (sl - entry) / _tick; }
                        if (risk < slFloorT) { sl = up ? entry - slFloorT * _tick : entry + slFloorT * _tick; risk = slFloorT; }
                        if (risk > slCapT) break;
                        if (TrendOk(bj, side) && VwapOk(bj, side) && LiqOk(bj))
                            raw.Add(new Sig { Idx = j, Side = side, Entry = entry, Sl = sl, Risk = risk, Time = bj.Time });
                        break;
                    }
                }
                if (up ? bj.H > peak : bj.L < peak) { peak = up ? bj.H : bj.L; since = j; }
            }
        }
        // EnableReversal = false (v7) -> khong them nhanh KB2
        if (SkipDeadSession && DeadStartHour != DeadEndHour)
            raw.RemoveAll(s => InDeadWindow(B[s.Idx].Time));
        return Cooldown_(Dedup(raw));
    }

    // ---------- <<< COPY Dedup + Cooldown_ (dong ~813-833) ----------
    static List<Sig> Dedup(List<Sig> raw)
    {
        var outp = new List<Sig>();
        foreach (var s in raw.OrderBy(x => x.Idx))
            if (!outp.Any(m => m.Side == s.Side && Math.Abs(s.Idx - m.Idx) <= DedupBars)) outp.Add(s);
        return outp;
    }

    static List<Sig> Cooldown_(List<Sig> sig)
    {
        var outp = new List<Sig>(); var last = new Dictionary<int, int>();
        foreach (var s in sig.OrderBy(x => x.Idx))
        {
            if (s.Idx - last.GetValueOrDefault(s.Side, -999) < Cooldown) continue;
            outp.Add(s); last[s.Side] = s.Idx;
        }
        return outp;
    }

    // ---------- doc CSV dxFeed — PHAI khop entry_dxfeed.load_m1(): sep=';', cot 'Time left',
    //            ngay dang '2025-11-02 23:22:00.000' (lay 19 ky tu dau, KHONG doi mui gio) ----------
    static List<(DateTime, double, double, double, double, double)> LoadCsv(string path)
    {
        var res = new List<(DateTime, double, double, double, double, double)>();
        var lines = File.ReadAllLines(path);
        var hdr = lines[0].TrimStart('﻿').Split(';');
        int Find(string name) => Array.FindIndex(hdr, h => h.Trim().Equals(name, StringComparison.OrdinalIgnoreCase));
        int iT = Find("Time left"), iO = Find("Open"), iH = Find("High"),
            iL = Find("Low"), iC = Find("Close"), iV = Find("Volume");
        if (iT < 0 || iO < 0 || iH < 0 || iL < 0 || iC < 0 || iV < 0)
            throw new Exception("CSV thieu cot. Header doc duoc: " + string.Join(" | ", hdr));
        for (int i = 1; i < lines.Length; i++)
        {
            if (string.IsNullOrWhiteSpace(lines[i])) continue;
            var x = lines[i].Split(';');
            if (x.Length <= iV) continue;
            var ts = x[iT].Trim();
            if (ts.Length < 19) continue;
            if (!DateTime.TryParseExact(ts.Substring(0, 19), "yyyy-MM-dd HH:mm:ss",
                    CultureInfo.InvariantCulture, DateTimeStyles.None, out var t)) continue;
            res.Add((t, D(x[iO]), D(x[iH]), D(x[iL]), D(x[iC]), D(x[iV])));
        }
        res.Sort((a, b) => a.Item1.CompareTo(b.Item1));
        return res;
    }

    static double D(string s) => double.TryParse(s, NumberStyles.Any, CultureInfo.InvariantCulture, out var v) ? v : 0.0;

    static int Main(string[] args)
    {
        if (args.Length < 1) { Console.Error.WriteLine("Dung: ParityHarness <csv> [out.csv]"); return 2; }
        var rows = LoadCsv(args[0]);
        var B = BuildBars(rows);
        Console.Error.WriteLine($"[C# harness] doc {rows.Count} nen | {B[0].Time:yyyy-MM-dd HH:mm} -> {B[^1].Time:yyyy-MM-dd HH:mm} (UTC)");
        var sigs = Scan(B);
        // in ra stdout dang CSV de Python doi chieu
        var w = args.Length > 1 ? new StreamWriter(args[1]) : null;
        void P(string s) { if (w != null) w.WriteLine(s); else Console.WriteLine(s); }
        P("time,side,entry,sl,risk_t,idx");
        foreach (var s in sigs)
            P($"{s.Time:yyyy-MM-dd HH:mm:ss},{(s.Side > 0 ? "LONG" : "SHORT")},"
              + $"{s.Entry.ToString("0.####", CultureInfo.InvariantCulture)},"
              + $"{s.Sl.ToString("0.####", CultureInfo.InvariantCulture)},"
              + $"{s.Risk.ToString("0.##", CultureInfo.InvariantCulture)},{s.Idx}");
        w?.Flush(); w?.Dispose();
        Console.Error.WriteLine($"[C# harness] {sigs.Count} tin hieu CBR (KB2 tat, phien chet cat, dedup+cooldown da ap)");
        return 0;
    }
}
