// Test cho ExhaustionLogic — kiệt sức thuần theo CORVEN (2026-11-08).
// Quy ước tick: giá = tick × 0,1; mọi nến dựng bằng hàm Bar(...) bên dưới.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using OrderFlowBubbles;

static class ExhaustionTests
{
    static int _fail;

    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    // levels: (tick, bid, ask) tu THAP len CAO
    static List<ExhLevel> Lv(params (long t, double bid, double ask)[] xs)
        => xs.Select(x => new ExhLevel(x.t, x.bid, x.ask)).ToList();

    static readonly ExhSettings Def = new ExhSettings();   // mac dinh moi (2026-11-18): rau >= 3 tick, tong 3 muc <= 0,5 x TB/muc

    static ExhResult Top(long o, long h, long l, long c, List<ExhLevel> lv, ExhSettings s = null)
        => ExhaustionLogic.Detect(true, o, h, l, c, lv, s ?? Def);
    static ExhResult Bot(long o, long h, long l, long c, List<ExhLevel> lv, ExhSettings s = null)
        => ExhaustionLogic.Detect(false, o, h, l, c, lv, s ?? Def);

    // nen mau: 100..106, than 101-103 (open 101, close 103), rau tren 104-106 (3 tick), rau duoi 100 (1 tick).
    // Cac muc 100-103 = 10/10 (vol 20). Rau tren: Bid 6, Ask = a104/a105/a106.
    static List<ExhLevel> Wick3(double a104, double a105, double a106)
        => Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, a104), (105, 6, a105), (106, 6, a106));

    public static int Run()
    {
        Console.WriteLine("[E0] Mac dinh: MinWickTicks 3, SumLevels 3, SumRel 0,5");
        Check(Def.MinWickTicks == 3 && Def.SumLevels == 3 && Math.Abs(Def.SumRel - 0.5) < 1e-12, "mac dinh dung");

        Console.WriteLine("[E1] Dinh: tong Ask 3 muc tren cung nho, rau 3 tick -> kiet suc buy");
        {
            var lv = Wick3(2, 1, 0);   // tong Ask 3 tick = 3; TB/muc ~ 14,7 -> nguong 7,4
            var r = Top(101, 106, 100, 103, lv);
            Check(r.Hit && r.Kind == ExhKind.Small && r.Top && r.Tick == 106 && r.ExtremeVol == 0, "dinh 106 -> co", $"kind={r.Kind}");
            Check(r.Seq.Length == 3 && r.Seq[0] == 2 && r.Seq[1] == 1 && r.Seq[2] == 0, "Seq tu trong ra cuc tri: 2,1,0", string.Join(",", r.Seq));
        }

        Console.WriteLine("[E2] Dinh soi ASK chu khong soi BID");
        {
            var a = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 5, 5), (104, 60, 0), (105, 60, 0), (106, 60, 0));
            Check(Top(101, 106, 100, 103, a).Hit, "Bid rau tren 60 / Ask 0 -> co kiet suc");
            var b = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 5, 5), (104, 0, 20), (105, 0, 20), (106, 0, 20));
            Check(!Top(101, 106, 100, 103, b).Hit, "Bid 0 / Ask 20 o rau tren -> khong kiet suc");
        }

        Console.WriteLine("[E3] Day soi BID chu khong soi ASK");
        {
            var a = Lv((100, 0, 40), (101, 0, 40), (102, 0, 40), (103, 6, 6), (104, 6, 6), (105, 6, 6), (106, 6, 6));
            var r = Bot(105, 106, 100, 103, a);   // open 105, close 103 -> than tu 103, rau duoi 100-102 = 3 tick
            Check(r.Hit && !r.Top && r.Tick == 100 && r.Kind == ExhKind.Small, "Bid day 0 / Ask day 40 -> kiet suc sell");
            Check(r.Seq.Length == 3 && r.Seq[2] == 0, "Seq day: cuoi = Bid o day", string.Join(",", r.Seq));
            var b = Lv((100, 40, 0), (101, 40, 0), (102, 40, 0), (103, 6, 6), (104, 6, 6), (105, 6, 6), (106, 6, 6));
            Check(!Bot(105, 106, 100, 103, b).Hit, "Bid day 40 / Ask day 0 -> khong kiet suc");
        }

        Console.WriteLine("[E4] Rau 2 tick khong du, 3 tick du (bien MinWickTicks)");
        {
            var lv = Wick3(0, 0, 0);   // tong = 0 -> neu rau du thi chac chan co
            Check(!Top(101, 106, 100, 104, lv).Hit, "rau tren 2 tick (than toi 104, high 106) -> khong");
            Check(Top(101, 106, 100, 103, lv).Hit, "rau tren 3 tick (than toi 103) -> co");
            var s2 = new ExhSettings { MinWickTicks = 2 };
            Check(Top(101, 106, 100, 104, lv, s2).Hit, "MinWickTicks = 2 thi rau 2 tick duoc");
            var s0 = new ExhSettings { MinWickTicks = 0 };
            Check(Top(100, 106, 100, 106, lv, s0).Hit, "MinWickTicks = 0 -> khong doi rau (close = high van co)");
            Check(!Top(100, 106, 100, 106, lv).Hit, "close = high (khong rau) -> khong");
        }

        Console.WriteLine("[E5] Bien tong 3 muc <= 0,5 x TB/muc");
        {
            // Bid rau = 6 -> TB = (4x20 + 3x(6 + a))/7 = (98 + 3a)/7 ; tong = 3a <= (98 + 3a)/14 <=> a <= 2,5128
            Check(Top(101, 106, 100, 103, Wick3(2.5, 2.5, 2.5)).Hit, "a = 2,5 (tong 7,5 <= 0,5 x TB 15,2) -> co");
            Check(!Top(101, 106, 100, 103, Wick3(2.6, 2.6, 2.6)).Hit, "a = 2,6 (tong 7,8 > 0,5 x TB 15,3) -> khong");
            var lv = Wick3(2, 1, 0);   // tong 3
            double m = ExhaustionLogic.MeanLevelVolume(lv);
            var exact = new ExhSettings { SumRel = 3.0 / m };
            Check(Top(101, 106, 100, 103, lv, exact).Hit, "tong == SumRel x TB (bien dung) -> co", $"sum=3 mean={m:0.000}");
            var tighter = new ExhSettings { SumRel = 3.0 / m - 0.001 };
            Check(!Top(101, 106, 100, 103, lv, tighter).Hit, "SumRel nho hon bien -> khong");
        }

        Console.WriteLine("[E6] Chi tinh SumLevels muc tu cuc tri; muc ben trong khong tinh");
        {
            Check(!Top(101, 106, 100, 103, Wick3(50, 0, 0)).Hit, "muc thu 3 tu cuc tri lon (50) -> khong");
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 80), (104, 6, 1), (105, 6, 1), (106, 6, 0));
            Check(Top(101, 106, 100, 103, lv).Hit, "Ask 80 o muc 103 (ngoai 3 muc) -> khong anh huong");
            Check(!Top(101, 106, 100, 103, lv, new ExhSettings { SumLevels = 4 }).Hit, "SumLevels = 4 -> muc 103 (80) vao tong -> khong");
        }

        Console.WriteLine("[E7] Muc thieu (gia nhay coc) tinh = 0; nen it muc hon SumLevels dung so muc co");
        {
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (106, 6, 3));
            Check(Top(101, 106, 100, 103, lv).Hit, "104, 105 trong -> tinh 0, tong Ask = 3 <= 0,5 x TB", $"mean={ExhaustionLogic.MeanLevelVolume(lv):0.0}");
            var s = new ExhSettings { MinWickTicks = 1 };
            var two = Lv((100, 8, 8), (101, 9, 0));   // nen 2 muc; than = 100, rau tren 1 tick; tong Ask 0 + 8 = 8 > 0,5 x 12,5
            Check(!Top(100, 101, 100, 100, two, s).Hit, "span 2 muc: dung 2 muc (tong 8 > 6,25) -> khong");
            var two2 = Lv((100, 8, 2), (101, 9, 0));  // tong 2 <= 0,5 x 9,5
            var r2 = Top(100, 101, 100, 100, two2, s);
            Check(r2.Hit && r2.Seq.Length == 2, "span 2 muc: tong 2 <= 0,5 x TB -> co, Seq 2 phan tu");
        }

        Console.WriteLine("[E8] Nen 1 muc gia / du lieu rong / settings null -> khong co gi");
        {
            var one = Lv((100, 0, 0));
            Check(!Top(100, 100, 100, 100, one).Hit && !Bot(100, 100, 100, 100, one).Hit, "nen 1 muc gia -> khong");
            Check(!Top(100, 102, 100, 101, new List<ExhLevel>()).Hit, "khong co muc gia -> khong");
            Check(!ExhaustionLogic.Detect(true, 100, 102, 100, 101, Lv((100, 1, 1), (102, 0, 0)), null).Hit, "settings null -> khong (khong crash)");
        }

        Console.WriteLine("[E9] Nguong theo TB/muc cua chinh nen (day hon -> nguong cao hon)");
        {
            var heavy = Lv((100, 60, 60), (101, 60, 60), (102, 60, 60), (103, 60, 60), (104, 40, 8), (105, 40, 8), (106, 40, 8));
            Check(Top(101, 106, 100, 103, heavy).Hit, "nen day, tong Ask 24 <= 0,5 x TB 89 -> co");
            var thin = Lv((100, 2, 2), (101, 2, 2), (102, 2, 2), (103, 2, 2), (104, 3, 1), (105, 3, 1), (106, 3, 1));
            Check(!Top(101, 106, 100, 103, thin).Hit, "nen mong, tong Ask 3 > 0,5 x TB 4 -> khong");
        }

        Console.WriteLine("[E10] Mot nen co CA kiet suc dinh lan day");
        {
            var lv = Lv((99, 0, 3), (100, 0, 3), (101, 0, 3), (102, 8, 8), (103, 9, 9), (104, 3, 0), (105, 3, 0), (106, 3, 0));
            Check(Top(102, 106, 99, 103, lv).Hit && Bot(102, 106, 99, 103, lv).Hit, "nen 2 rau 3 tick, Ask dinh 0 & Bid day 0 -> ca 2");
        }

        Console.WriteLine("[E13] VO HIEU: nen sau chi can RAU quet qua (khong can dong nen)");
        {
            Check(!ExhaustionLogic.IsSwept(true, 106, 106, 100, 1), "dinh 106, nen sau high 106 (cham, chua qua) -> con hieu luc");
            Check(ExhaustionLogic.IsSwept(true, 106, 107, 100, 1), "dinh 106, nen sau high 107 -> vo hieu");
            Check(ExhaustionLogic.IsSwept(true, 106, 106, 100, 0), "sweepTicks=0: cham lai dung muc -> vo hieu");
            Check(!ExhaustionLogic.IsSwept(true, 106, 107, 100, 2), "sweepTicks=2: vuot 1 tick chua du");
            Check(!ExhaustionLogic.IsSwept(false, 100, 110, 100, 1), "day 100, nen sau low 100 -> con hieu luc");
            Check(ExhaustionLogic.IsSwept(false, 100, 110, 99, 1), "day 100, nen sau low 99 -> vo hieu");
            Check(!ExhaustionLogic.IsSwept(true, 106, 105, 90, 1), "kiet suc dinh khong bi vo hieu boi gia di XUONG");
        }

        Console.WriteLine("[E14] Chuoi nen: kiet suc song toi khi bi rau quet qua");
        {
            // dinh kiet suc 106; cac nen sau: high 105, 106, 104, 107 -> vo hieu o nen thu 4
            long[] highs = { 105, 106, 104, 107, 103 };
            int killedAt = -1;
            for (int i = 0; i < highs.Length; i++)
                if (ExhaustionLogic.IsSwept(true, 106, highs[i], 90, 1)) { killedAt = i; break; }
            Check(killedAt == 3, "vo hieu dung nen co high 107", $"killedAt={killedAt}");
        }

        Console.WriteLine("[E15] Tooltip ngan: Kiet suc buy/sell");
        {
            var lv = Wick3(2, 1, 0);
            string t = ExhaustionLogic.Describe(Top(101, 106, 100, 103, lv));
            Check(t == "Kiệt sức buy", "tooltip dinh ngan gon", t);
            string tb = ExhaustionLogic.Describe(Bot(105, 106, 100, 103, Lv((100, 0, 40), (101, 0, 40), (102, 0, 40), (103, 6, 6), (104, 6, 6), (105, 6, 6), (106, 6, 6))));
            Check(tb == "Kiệt sức sell", "tooltip day ngan gon", tb);
            Check(ExhaustionLogic.Describe(default) == "", "khong kiet suc -> tooltip rong");
        }

        CrossCheckWithPython();
        Console.WriteLine(_fail == 0 ? "  -> kiet suc: tat ca PASS" : $"  -> kiet suc: {_fail} FAIL");
        return _fail;
    }

    // [E16] Doi chieu voi script Python da dung de do (chi chay khi co bien moi truong EXH_XCHECK_CSV):
    // file CSV: bar_idx,open,high,low,close,price_tick,bid,ask,volume  +  dong cuoi "#expect,top,bottom"
    static void CrossCheckWithPython()
    {
        string path = Environment.GetEnvironmentVariable("EXH_XCHECK_CSV");
        if (string.IsNullOrEmpty(path) || !File.Exists(path)) { Console.WriteLine("[E16] (bo qua doi chieu Python: khong co EXH_XCHECK_CSV)"); return; }
        Console.WriteLine("[E16] Doi chieu so dem kiet suc C# voi Python tren du lieu that");
        var bars = new Dictionary<long, (long o, long h, long l, long c, List<ExhLevel> lv)>();
        int expTop = -1, expBot = -1;
        foreach (var line in File.ReadLines(path))
        {
            var f = line.Split(',');
            if (f[0] == "#expect") { expTop = int.Parse(f[1]); expBot = int.Parse(f[2]); continue; }
            if (f[0] == "bar_idx") continue;
            long bi = long.Parse(f[0]);
            if (!bars.TryGetValue(bi, out var b))
            {
                b = (long.Parse(f[1]), long.Parse(f[2]), long.Parse(f[3]), long.Parse(f[4]), new List<ExhLevel>());
                bars[bi] = b;
            }
            b.lv.Add(new ExhLevel(long.Parse(f[5]), double.Parse(f[6], CultureInfo.InvariantCulture),
                                  double.Parse(f[7], CultureInfo.InvariantCulture), double.Parse(f[8], CultureInfo.InvariantCulture)));
        }
        int top = 0, bot = 0;
        foreach (var b in bars.Values)
        {
            if (ExhaustionLogic.Detect(true, b.o, b.h, b.l, b.c, b.lv, Def).Hit) top++;
            if (ExhaustionLogic.Detect(false, b.o, b.h, b.l, b.c, b.lv, Def).Hit) bot++;
        }
        Check(top == expTop && bot == expBot, $"{bars.Count} nen: C# dinh={top} day={bot}", $"Python dinh={expTop} day={expBot}");
    }
}
