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

    static readonly ExhSettings Def = new ExhSettings();   // mac dinh: 0,10 / 3 muc / 0,25

    static ExhResult Top(long o, long h, long l, long c, List<ExhLevel> lv, ExhSettings s = null)
        => ExhaustionLogic.Detect(true, o, h, l, c, lv, s ?? Def);
    static ExhResult Bot(long o, long h, long l, long c, List<ExhLevel> lv, ExhSettings s = null)
        => ExhaustionLogic.Detect(false, o, h, l, c, lv, s ?? Def);

    public static int Run()
    {
        Console.WriteLine("[E1] Dinh: Ask tai dinh = 0, co rau -> kiet suc buy (Nho)");
        {
            // nen 100..106, than 101-103, rau tren 104-106; Ask o 106 = 0
            var lv = Lv((100, 5, 3), (101, 8, 9), (102, 10, 12), (103, 9, 8), (104, 4, 6), (105, 3, 2), (106, 7, 0));
            var r = Top(101, 106, 100, 103, lv);
            Check(r.Hit && r.Kind == ExhKind.Small && r.Top && r.Tick == 106 && r.ExtremeVol == 0, "dinh 106, Ask=0 -> Small", $"kind={r.Kind}");
        }

        Console.WriteLine("[E2] Dinh soi ASK chu khong soi BID");
        {
            // Bid o dinh rat lon (sell chu dong dap vao) nhung Ask = 0 -> VAN la kiet suc buy
            var a = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 60, 0));
            Check(Top(100, 103, 100, 101, a).Hit, "Bid dinh 60 / Ask dinh 0 -> co kiet suc");
            // nguoc lai: Bid dinh 0 nhung Ask dinh lon -> KHONG
            var b = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 0, 20));
            Check(!Top(100, 103, 100, 101, b).Hit, "Bid dinh 0 / Ask dinh 20 -> khong kiet suc");
        }

        Console.WriteLine("[E3] Day soi BID chu khong soi ASK");
        {
            var a = Lv((100, 0, 40), (101, 6, 6), (102, 6, 6), (103, 6, 6));
            var r = Bot(103, 103, 100, 102, a);
            Check(r.Hit && !r.Top && r.Tick == 100 && r.Kind == ExhKind.Small, "Bid day 0 / Ask day 40 -> kiet suc sell");
            var b = Lv((100, 20, 0), (101, 6, 6), (102, 6, 6), (103, 6, 6));
            Check(!Bot(103, 103, 100, 102, b).Hit, "Bid day 20 / Ask day 0 -> khong kiet suc");
        }

        Console.WriteLine("[E4] Giam dan ve 0 (3 muc rau giam NGAT, muc cuoi <= 0,25 x TB)");
        {
            // TB/muc = (10+10+...)/7; dat sao cho Ask dinh = 2 (khong 'nho' vi > 0,1*TB) nhung giam 9 -> 5 -> 2
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (105, 6, 5), (106, 6, 2));
            double mean = ExhaustionLogic.MeanLevelVolume(lv);
            var r = Top(101, 106, 100, 103, lv);
            Check(r.Hit && r.Kind == ExhKind.Fade, "9 -> 5 -> 2 tai dinh -> Fade", $"kind={r.Kind} mean={mean:0.0}");
            Check(r.Seq.Length == 3 && r.Seq[0] == 9 && r.Seq[2] == 2, "Seq ghi tu trong ra dinh: 9,5,2", string.Join(",", r.Seq));
        }

        Console.WriteLine("[E5] Khong giam NGAT (5 -> 5 -> 2) -> khong Fade");
        {
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 5), (105, 6, 5), (106, 6, 2));
            Check(!Top(101, 106, 100, 103, lv).Hit, "5,5,2 -> khong kiet suc");
        }

        Console.WriteLine("[E6] Giam dan nhung muc cuoi con LON -> khong Fade");
        {
            // TB ~ 30/muc; 40 -> 25 -> 15 giam ngat nhung 15 > 0,25*TB
            var lv = Lv((100, 20, 20), (101, 20, 20), (102, 20, 20), (103, 20, 20), (104, 10, 40), (105, 10, 25), (106, 10, 15));
            var r = Top(101, 106, 100, 103, lv);
            Check(!r.Hit, "40,25,15 voi TB lon -> khong kiet suc", $"mean={ExhaustionLogic.MeanLevelVolume(lv):0.0}");
        }

        Console.WriteLine("[E7] Lay o RAU, khong lay o THAN: nen dong ngay tai dinh -> khong co kiet suc dinh");
        {
            var lv = Lv((100, 5, 5), (101, 5, 5), (102, 5, 5), (103, 4, 0));
            Check(!Top(100, 103, 100, 103, lv).Hit, "close = high (khong rau tren), Ask dinh 0 -> KHONG");
            Check(!Bot(103, 103, 100, 100, Lv((100, 0, 4), (101, 5, 5), (102, 5, 5), (103, 5, 5))).Hit,
                  "close = low (khong rau duoi), Bid day 0 -> KHONG");
            // tat RequireWick (chi de thu nghiem) thi lai bat duoc
            var s = new ExhSettings { RequireWick = false };
            Check(Top(100, 103, 100, 103, lv, s).Hit, "RequireWick=false -> bat duoc (chi thu nghiem)");
        }

        Console.WriteLine("[E8] Giam dan doi DU so muc NAM TRONG RAU");
        {
            // rau tren chi 2 tick (105,106) nhung chuoi giam lay 3 muc (104 la than) -> khong Fade
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (105, 6, 5), (106, 6, 2));
            Check(!Top(101, 106, 100, 104, lv).Hit, "rau 2 tick, chuoi 3 muc lan vao than -> khong");
            // FadeLevels=2 thi 2 muc rau 5 -> 2 du dieu kien
            var s2 = new ExhSettings { FadeLevels = 2 };
            Check(Top(101, 106, 100, 104, lv, s2).Kind == ExhKind.Fade, "FadeLevels=2: 5 -> 2 trong rau -> Fade");
        }

        Console.WriteLine("[E9] Nen 1 muc gia / du lieu rong -> khong co gi");
        {
            var one = Lv((100, 0, 0));
            Check(!Top(100, 100, 100, 100, one).Hit && !Bot(100, 100, 100, 100, one).Hit, "nen 1 muc gia -> khong");
            Check(!Top(100, 102, 100, 101, new List<ExhLevel>()).Hit, "khong co muc gia -> khong");
            Check(!ExhaustionLogic.Detect(true, 100, 102, 100, 101, Lv((100, 1, 1), (102, 0, 0)), null).Hit, "settings null -> khong (khong crash)");
        }

        Console.WriteLine("[E10] 'Nho' la TUONG DOI theo TB/muc cua chinh nen");
        {
            // nen day: TB ~ 60/muc, Ask dinh 5 <= 6 -> Nho
            var heavy = Lv((100, 60, 60), (101, 60, 60), (102, 60, 60), (103, 60, 60), (104, 40, 5));
            Check(Top(101, 104, 100, 102, heavy).Kind == ExhKind.Small, "nen day, Ask dinh 5 -> Nho", $"mean={ExhaustionLogic.MeanLevelVolume(heavy):0.0}");
            // nen mong: TB ~ 4/muc, Ask dinh 1 > 0,4 -> khong
            var thin = Lv((100, 2, 2), (101, 2, 2), (102, 2, 2), (103, 2, 2), (104, 3, 1));
            Check(!Top(101, 104, 100, 102, thin).Hit, "nen mong, Ask dinh 1 -> khong");
            // SmallRel = 0 -> phai dung bang 0
            var s0 = new ExhSettings { SmallRel = 0, FadeLevels = 0 };
            Check(!Top(101, 104, 100, 102, heavy, s0).Hit, "SmallRel=0: Ask dinh 5 -> khong");
            var zero = Lv((100, 60, 60), (101, 60, 60), (102, 60, 60), (103, 60, 60), (104, 40, 0));
            Check(Top(101, 104, 100, 102, zero, s0).Hit, "SmallRel=0: Ask dinh 0 -> co");
        }

        Console.WriteLine("[E11] Muc trong (gia nhay coc) trong rau tinh = 0");
        {
            // khong co dong cho 105; chuoi tu trong ra: 104=9, 105=0, 106=3 -> khong giam ngat (3 < 0 sai)
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (106, 6, 3));
            var r = Top(101, 106, 100, 103, lv);
            Check(!r.Hit, "9, [trong], 3 -> khong Fade, Ask dinh 3 > 0,1*TB", $"kind={r.Kind}");
            // muc trong NGAY tai rau giua, chuoi 9 -> [0] la cuc tri? khong: cuc tri luon co giao dich.
            var lv2 = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (105, 6, 3), (106, 6, 0));
            Check(Top(101, 106, 100, 103, lv2).Kind == ExhKind.Small, "104 trong, Ask dinh 0 -> Small binh thuong");
        }

        Console.WriteLine("[E12] Mot nen co CA kiet suc dinh lan day (nhu nen 22:52 tren chart CORVEN)");
        {
            var lv = Lv((100, 0, 3), (101, 8, 8), (102, 9, 9), (103, 8, 8), (104, 3, 0));
            Check(Top(102, 104, 100, 102, lv).Hit && Bot(102, 104, 100, 102, lv).Hit, "doji 2 rau, Ask dinh 0 & Bid day 0 -> ca 2");
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

        Console.WriteLine("[E15] Tooltip noi thang con so");
        {
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (104, 6, 9), (105, 6, 5), (106, 6, 2));
            string t = ExhaustionLogic.Describe(Top(101, 106, 100, 103, lv));
            Check(t.Contains("Kiệt sức buy") && t.Contains("Ask tại đỉnh = 2") && t.Contains("9 → 5 → 2") && t.Contains("giảm dần về 0"), "tooltip co so Ask + chuoi giam", t);
            string tb = ExhaustionLogic.Describe(Bot(103, 103, 100, 102, Lv((100, 0, 40), (101, 6, 6), (102, 6, 6), (103, 6, 6))));
            Check(tb.Contains("Kiệt sức sell") && tb.Contains("Bid tại đáy = 0"), "tooltip day noi Bid", tb);
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
