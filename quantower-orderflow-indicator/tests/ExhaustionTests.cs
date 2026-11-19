// Test cho ExhaustionLogic — kiệt sức theo CORVEN, luật fit chart M5 (2026-11-19):
// râu >= 3 tick VÀ tổng bên soi (Ask ở đỉnh, Bid ở đáy) trên 6 tick từ cực trị <= 1,1 x volume TB mỗi ô của 20 nến đã đóng trước (mức nền lịch sử).
// Quy ước tick: giá = tick x 0,1.
using System;
using System.Collections.Generic;
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

    static readonly ExhSettings Def = new ExhSettings();
    const double Hist = 10.0;   // volume TB mỗi ô của 20 nến trước (mức nền lịch sử) dùng chung trong test

    // levels: (tick, bid, ask)
    static List<ExhLevel> Lv(params (long t, double bid, double ask)[] xs)
        => xs.Select(x => new ExhLevel(x.t, x.bid, x.ask)).ToList();

    // Nến 100..106: đỉnh 106. asks[j] = Ask ở tick 106 - j (j = 0..5, tức 106..101); tick 100: Ask 50; Bid 10 mọi mức.
    static List<ExhLevel> TopBar(params double[] asks)
    {
        var l = new List<ExhLevel> { new ExhLevel(100, 10, 50) };
        for (int j = 5; j >= 0; j--) l.Add(new ExhLevel(106 - j, 10, asks[j]));
        return l;
    }
    // Đối xứng: đáy 100. bids[j] = Bid ở tick 100 + j; tick 106: Bid 50; Ask 10 mọi mức.
    static List<ExhLevel> BotBar(params double[] bids)
    {
        var l = new List<ExhLevel> { new ExhLevel(106, 50, 10) };
        for (int j = 5; j >= 0; j--) l.Add(new ExhLevel(100 + j, bids[j], 10));
        return l;
    }

    // thân 101-103 -> râu trên 3 tick (106 - 103), râu dưới 1 tick
    static ExhResult Top(List<ExhLevel> lv, ExhSettings s = null, double hist = Hist, bool has = true, long close = 103)
        => ExhaustionLogic.Detect(true, 101, 106, 100, close, lv, s ?? Def, has, hist);
    // thân 103-105 -> râu dưới 3 tick (103 - 100), râu trên 1 tick
    static ExhResult Bot(List<ExhLevel> lv, ExhSettings s = null, double hist = Hist, bool has = true, long open = 105)
        => ExhaustionLogic.Detect(false, open, 106, 100, 103, lv, s ?? Def, has, hist);

    public static int Run()
    {
        Console.WriteLine("[E0] Mac dinh: MinWickTicks 3, SumLevels 6, SumHistRatio 1,1");
        Check(Def.MinWickTicks == 3 && Def.SumLevels == 6 && Math.Abs(Def.SumHistRatio - 1.1) < 1e-12, "mac dinh dung");

        Console.WriteLine("[E1] Dinh: tong Ask 6 muc tu cuc tri <= 1,1 x muc nen -> kiet suc buy");
        {
            var r = Top(TopBar(0, 1, 2, 2, 2, 2));   // tong 9 <= 11
            Check(r.Hit && r.Kind == ExhKind.Small && r.Top && r.Tick == 106 && r.ExtremeVol == 0, "dinh 106 -> co", $"kind={r.Kind}");
            Check(r.Seq.Length == 6 && r.Seq[0] == 2 && r.Seq[3] == 2 && r.Seq[4] == 1 && r.Seq[5] == 0, "Seq tu trong ra cuc tri", string.Join(",", r.Seq));
            Check(Math.Abs(r.MeanLevelVol - Hist) < 1e-9, "MeanLevelVol = muc nen lich su");
        }

        Console.WriteLine("[E2] Bien tong: sum <= 1,1 x muc nen (muc nen 10 -> 11)");
        {
            Check(Top(TopBar(2, 2, 2, 2, 2, 1)).Hit, "tong 11 = 1,1 x 10 -> co (bien dung)");
            Check(!Top(TopBar(2, 2, 2, 2, 2, 2)).Hit, "tong 12 > 11 -> khong");
        }
        {
            Check(!Top(TopBar(2, 2, 2, 2, 2, 1.5)).Hit, "tong 11,5 > 11 -> khong");
            var s1 = new ExhSettings { SumHistRatio = 1.0 };
            Check(Top(TopBar(2, 2, 2, 2, 2, 1), s1, hist: 11).Hit, "ty le 1,0 x muc nen 11: tong 11 -> co (bien dung)");
            Check(!Top(TopBar(2, 2, 2, 2, 2, 1.01), s1, hist: 11).Hit, "tong 11,01 > 11 -> khong");
        }

        Console.WriteLine("[E3] Dung muc nen LICH SU, khong dung trung binh cua chinh nen");
        {
            Check(!Top(TopBar(2, 2, 2, 2, 2, 2), hist: 10).Hit && Top(TopBar(2, 2, 2, 2, 2, 2), hist: 11).Hit, "muc nen 10 -> tong 12 khong; muc nen 11 -> 12 <= 12,1 co");
            var own = TopBar(3, 3, 3, 3, 3, 3);   // tong 18; TB cua chinh nen ~ 18 => theo nen nay thi 18 <= 1,1 x 18 la co
            Check(!Top(own, hist: 10).Hit, "tong 18 > 1,1 x 10 (lich su) -> khong, du so voi TB chinh nen thi nho");
            Check(Top(own, hist: 17).Hit, "muc nen lich su 17 -> 18 <= 18,7 -> co");
        }

        Console.WriteLine("[E4] Chua co muc nen lich su -> khong danh dau");
        {
            Check(!Top(TopBar(0, 0, 0, 0, 0, 0), has: false).Hit, "hasHist = false -> khong");
            Check(!Top(TopBar(0, 0, 0, 0, 0, 0), hist: 0).Hit, "muc nen 0 -> khong");
        }

        Console.WriteLine("[E5] Dinh soi ASK, khong soi BID");
        {
            var a = Lv((100, 5, 5), (101, 60, 0), (102, 60, 0), (103, 60, 0), (104, 60, 0), (105, 60, 0), (106, 60, 0));
            Check(Top(a).Hit, "Bid 60 / Ask 0 o 6 muc tren cung -> co kiet suc buy");
            var b = Lv((100, 5, 5), (101, 0, 20), (102, 0, 20), (103, 0, 20), (104, 0, 20), (105, 0, 20), (106, 0, 20));
            Check(!Top(b).Hit, "Bid 0 / Ask 20 -> khong");
        }

        Console.WriteLine("[E6] Day soi BID, khong soi ASK");
        {
            var r = Bot(BotBar(0, 1, 2, 2, 2, 2));
            Check(r.Hit && !r.Top && r.Tick == 100 && r.Kind == ExhKind.Small, "Bid day nho -> kiet suc sell");
            Check(r.Seq.Length == 6 && r.Seq[5] == 0 && r.Seq[4] == 1, "Seq day: cuoi = Bid o day", string.Join(",", r.Seq));
            Check(Bot(BotBar(2, 2, 2, 2, 2, 1)).Hit && !Bot(BotBar(2, 2, 2, 2, 2, 2)).Hit, "day: tong 11 co, tong 12 khong (bien 1,1 x 10)");
            Check(!Bot(Lv((100, 40, 0), (101, 40, 0), (102, 40, 0), (103, 40, 0), (104, 40, 0), (105, 40, 0), (106, 6, 6))).Hit, "Bid day 40 / Ask 0 -> khong");
        }

        Console.WriteLine("[E7] Rau: 2 tick khong du, 3 tick du (cung tong bang 0)");
        {
            var lv = TopBar(0, 0, 0, 0, 0, 0);
            Check(!Top(lv, close: 104).Hit, "rau tren 2 tick (than toi 104, high 106) -> khong");
            Check(Top(lv, close: 103).Hit, "rau tren 3 tick (than toi 103) -> co");
            Check(Top(lv, new ExhSettings { MinWickTicks = 2 }, close: 104).Hit, "MinWickTicks = 2 thi rau 2 tick duoc");
            Check(!Top(lv, close: 106).Hit && Top(lv, new ExhSettings { MinWickTicks = 0 }, close: 106).Hit, "close = high: khong rau -> khong; MinWickTicks 0 -> bo dieu kien rau");
            var lb = BotBar(0, 0, 0, 0, 0, 0);
            Check(!ExhaustionLogic.Detect(false, 105, 106, 100, 102, lb, Def, true, Hist).Hit, "rau duoi 2 tick (than tu 102) -> khong");
            Check(ExhaustionLogic.Detect(false, 105, 106, 100, 103, lb, Def, true, Hist).Hit, "rau duoi 3 tick (than tu 103) -> co");
            // rau tinh theo min(open, close) o day
            Check(ExhaustionLogic.Detect(false, 103, 106, 100, 105, lb, Def, true, Hist).Hit, "nen tang: than tu 103 (open) -> rau duoi 3 tick -> co");
        }

        Console.WriteLine("[E8] Chi tinh SumLevels = 6 muc tu cuc tri; muc thu 7 tro di khong tinh");
        {
            // asks[5] la tick 101 (muc thu 6), tick 100 la muc thu 7 (Ask 50 trong TopBar)
            Check(Top(TopBar(0, 0, 0, 0, 0, 0)).Hit, "muc thu 7 (tick 100, Ask 50) khong anh huong -> co");
            Check(!Top(TopBar(0, 0, 0, 0, 0, 50)).Hit, "muc thu 6 (tick 101) Ask 50 vao tong -> khong");
            Check(!Top(TopBar(0, 0, 0, 0, 0, 0), new ExhSettings { SumLevels = 7 }).Hit, "SumLevels = 7 -> tick 100 (50) vao tong -> khong");
            var s3 = new ExhSettings { SumLevels = 3 };
            Check(Top(TopBar(2, 2, 2, 50, 50, 50), s3).Hit, "SumLevels = 3: chi 3 muc tren cung (tong 6) -> co");
            Check(!Top(TopBar(2, 2, 2, 50, 50, 50)).Hit, "SumLevels = 6 mac dinh: tong 156 -> khong");
        }

        Console.WriteLine("[E9] Muc thieu (gia nhay coc) tinh = 0");
        {
            var lv = Lv((100, 10, 10), (101, 10, 10), (102, 10, 10), (103, 10, 10), (106, 6, 3));   // thieu 104, 105
            // 106: 3; 105: 0; 104: 0; 103: 10; 102: 10; 101: 10 -> tong 33 > 11 -> khong
            Check(!Top(lv).Hit, "tong 33 -> khong (muc 103..101 co Ask 10)");
            var lv2 = Lv((100, 10, 10), (103, 10, 0), (106, 6, 3));   // 106: 3, 105/104 vang, 103: 0, 102/101 vang -> tong 3
            Check(Top(lv2).Hit, "muc vang tinh 0: tong 3 <= 11 -> co");
            Check(Top(Lv((100, 10, 10), (104, 5, 4), (106, 6, 5)), hist: 10).Hit, "thieu 105: tong 5 + 0 + 4 = 9 -> co");
        }

        Console.WriteLine("[E10] Nen 1 muc gia / du lieu rong / settings null -> khong co gi");
        {
            var one = Lv((100, 0, 0));
            Check(!ExhaustionLogic.Detect(true, 100, 100, 100, 100, one, Def, true, Hist).Hit && !ExhaustionLogic.Detect(false, 100, 100, 100, 100, one, Def, true, Hist).Hit, "nen 1 muc gia -> khong");
            Check(!Top(new List<ExhLevel>()).Hit, "khong co muc gia -> khong");
            Check(!ExhaustionLogic.Detect(true, 100, 102, 100, 101, Lv((100, 1, 1), (102, 0, 0)), null, true, Hist).Hit, "settings null -> khong (khong crash)");
        }

        Console.WriteLine("[E11] Mot nen co CA kiet suc dinh lan day");
        {
            var lv = Lv((99, 0, 3), (100, 0, 3), (101, 0, 3), (102, 8, 8), (103, 9, 9), (104, 3, 0), (105, 3, 0), (106, 3, 0));
            // dinh 106 (than 102..103, rau tren 3), day 99 (rau duoi 3); SumLevels 3: Ask 106..104 = 0 va Bid 99..101 = 0
            var s = new ExhSettings { SumLevels = 3 };
            Check(ExhaustionLogic.Detect(true, 102, 106, 99, 103, lv, s, true, Hist).Hit && ExhaustionLogic.Detect(false, 102, 106, 99, 103, lv, s, true, Hist).Hit, "nen 2 rau 3 tick, Ask dinh 0 & Bid day 0 (SumLevels 3) -> ca 2");
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
            long[] highs = { 105, 106, 104, 107, 103 };
            int killedAt = -1;
            for (int i = 0; i < highs.Length; i++)
                if (ExhaustionLogic.IsSwept(true, 106, highs[i], 90, 1)) { killedAt = i; break; }
            Check(killedAt == 3, "vo hieu dung nen co high 107", $"killedAt={killedAt}");
        }

        Console.WriteLine("[E15] Tooltip ngan: Kiet suc buy/sell");
        {
            string t = ExhaustionLogic.Describe(Top(TopBar(0, 1, 2, 2, 2, 2)));
            Check(t == "Kiệt sức buy", "tooltip dinh ngan gon", t);
            string tb = ExhaustionLogic.Describe(Bot(BotBar(0, 1, 2, 2, 2, 2)));
            Check(tb == "Kiệt sức sell", "tooltip day ngan gon", tb);
            Check(ExhaustionLogic.Describe(default) == "", "khong kiet suc -> tooltip rong");
        }

        Console.WriteLine(_fail == 0 ? "  -> kiet suc: tat ca PASS" : $"  -> kiet suc: {_fail} FAIL");
        return _fail;
    }
}
