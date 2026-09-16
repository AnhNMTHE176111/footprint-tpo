// Test cho SignalCache — cơ chế niêm phong tín hiệu (2026-09-15).
// Chạy: dotnet run --project quantower-orderflow-indicator/tests
using System;
using System.IO;
using OrderFlowBubbles;

static class Tests
{
    static int _fail;

    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (detail.Length > 0 ? "  -> " + detail : ""));
        if (!ok) _fail++;
    }

    static CachedBarData MakeBar(long timeTicks, int tint, params (double price, int confirm, bool confirmable)[] bubbles)
    {
        var d = new CachedBarData { TimeTicks = timeTicks, Tint = tint };
        foreach (var (price, confirm, confirmable) in bubbles)
            d.Bubbles.Add(new CachedBubbleData
            {
                Price = price, Shape = 0, ColorArgb = unchecked((int)0xFFFF8000), Size = 14,
                Transparency = 10, Halo = false, UseBarWidth = true,
                Tooltip = "test", Confirm = confirm, Confirmable = confirmable
            });
        return d;
    }

    // [1] Ghi rồi đọc lại trong CÙNG 1 instance (chưa đụng file) -> phải thấy ngay
    static void InMemoryRoundtrip()
    {
        Console.WriteLine("[1] Put roi TryGet trong cung 1 instance");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var cache = new SignalCache(path);
            cache.Load();   // file chưa tồn tại -> rỗng, không lỗi
            Check(cache.Count == 0, "cache rong luc dau");

            var bar = MakeBar(1000, 1, (4327.0, 0, true));
            cache.Put(bar);
            Check(cache.TryGet(1000, out var got), "TryGet thay ngay sau Put");
            Check(got.Bubbles.Count == 1 && got.Bubbles[0].Price == 4327.0, "du lieu dung");
        }
        finally { File.Delete(path); }
    }

    // [2] NIÊM PHONG sống sót qua "khởi động lại" (instance MỚI đọc lại file cũ)
    //     — đây chính là ca của ResetState(): Process() cũ ghi ra file, Process() MỚI (sau reset)
    //     phải khôi phục đúng, không tự tính lại.
    static void SurvivesRestart()
    {
        Console.WriteLine("[2] Niem phong song sot qua instance moi (mo phong ResetState)");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var cache1 = new SignalCache(path);
            cache1.Load();
            cache1.Put(MakeBar(2000, -1, (4325.5, 0, true)));
            cache1.Put(MakeBar(2060, 0, (4326.0, 0, false)));   // nến khác, không có absorption

            // "khởi động lại" -> instance MỚI, đọc lại từ file
            var cache2 = new SignalCache(path);
            cache2.Load();
            Check(cache2.Count == 2, "doc lai du 2 nen tu file", $"count={cache2.Count}");
            Check(cache2.TryGet(2000, out var b1) && b1.Tint == -1 && b1.Bubbles[0].Price == 4325.5,
                  "nen 2000 khoi phuc dung gia + tint");
            Check(cache2.TryGet(2060, out var b2) && b2.Bubbles.Count == 1 && b2.Bubbles[0].Price == 4326.0,
                  "nen 2060 khoi phuc dung");
        }
        finally { File.Delete(path); }
    }

    // [3] Dòng ghi SAU (Confirm chốt: đang chờ -> giữ/vỡ mức) phải ĐÈ dòng ghi TRƯỚC cùng thời gian
    //     — đây là ca RePersistBar() khi UpdateAbsorptionConfirms() chốt xong.
    static void LaterWriteOverrides()
    {
        Console.WriteLine("[3] Ghi de: Confirm chot sau phai thang ban ghi cho truoc");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var cache1 = new SignalCache(path);
            cache1.Load();
            cache1.Put(MakeBar(3000, 1, (4330.0, 0, true)));    // lần 1: đang chờ xác nhận (Confirm=0)
            cache1.Put(MakeBar(3000, 1, (4330.0, -1, true)));   // lần 2: đã chốt VỠ MỨC (Confirm=-1)

            var cache2 = new SignalCache(path);   // đọc lại từ đầu, như sau khi ResetState()
            cache2.Load();
            Check(cache2.TryGet(3000, out var b) && b.Bubbles[0].Confirm == -1,
                  "doc lai file thay dung ban ghi MOI NHAT (Confirm=-1), khong phai ban dau (Confirm=0)");
        }
        finally { File.Delete(path); }
    }

    // [4] Nến KHÔNG có bóng nào vẫn phải niêm phong được (Bubbles rỗng) — để không bị tính lại vô ích
    //     mỗi lần reset (dù không có gì để vẽ, quyết định "không có bóng" cũng phải cố định).
    static void EmptyBarIsCached()
    {
        Console.WriteLine("[4] Nen khong co bong (Bubbles rong) van niem phong duoc");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var cache = new SignalCache(path);
            cache.Load();
            cache.Put(new CachedBarData { TimeTicks = 4000, Tint = 0 });   // Bubbles để mặc định = rỗng

            var cache2 = new SignalCache(path);
            cache2.Load();
            Check(cache2.TryGet(4000, out var b) && b.Bubbles.Count == 0,
                  "nen rong van co trong cache (khong bi coi la 'chua tung tinh')");
        }
        finally { File.Delete(path); }
    }

    // [5] Dòng file hỏng (vd ghi dở khi crash giữa chừng) không được làm chết cả file
    static void CorruptLineIsSkipped()
    {
        Console.WriteLine("[5] 1 dong JSON hong khong lam hong ca file");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            File.WriteAllText(path,
                "{\"TimeTicks\":5000,\"Tint\":1,\"Bubbles\":[]}\n" +
                "{ghi do dang crash, khong phai json hop le\n" +
                "{\"TimeTicks\":5060,\"Tint\":0,\"Bubbles\":[]}\n");
            var cache = new SignalCache(path);
            cache.Load();
            Check(cache.Count == 2, "bo qua dong hong, van doc duoc 2 dong tot", $"count={cache.Count}");
        }
        finally { File.Delete(path); }
    }

    // [6] Fingerprint tham số KHÁC nhau -> KHÔNG được coi là cache hit (đây là hành vi caller
    //     [OrderFlowBubbles.Process()] tự so sánh SettingsFingerprint, SignalCache chỉ lưu hộ —
    //     test mô phỏng đúng cách caller dùng: TryGet trả về record, caller tự so fingerprint).
    static void FingerprintMismatchMeansMiss()
    {
        Console.WriteLine("[6] Doi tham so (fingerprint khac) -> khong dung nham bong cu");
        string path = Path.Combine(Path.GetTempPath(), "sc_test_" + Guid.NewGuid() + ".jsonl");
        try
        {
            var cache = new SignalCache(path);
            cache.Load();
            var rec = MakeBar(6000, 1, (4327.0, 0, true));
            rec.SettingsFingerprint = "relative-mode|z=2.5";
            cache.Put(rec);

            // nguoi dung bat "nguong co dinh" -> fingerprint moi khac han
            string newFingerprint = "fixed-mode|20";
            bool hit = cache.TryGet(6000, out var got) && got.SettingsFingerprint == newFingerprint;
            Check(!hit, "fingerprint moi khong khop -> phai la CACHE MISS (tinh lai)", $"cached_fp={got?.SettingsFingerprint}");

            // dung fingerprint CU (khong doi tham so) -> van phai la cache HIT
            bool hitOld = cache.TryGet(6000, out var got2) && got2.SettingsFingerprint == "relative-mode|z=2.5";
            Check(hitOld, "fingerprint khop (tham so khong doi) -> van la CACHE HIT");
        }
        finally { File.Delete(path); }
    }

    // [7] BigTradeLog: ghi 1 lan, doc lai (mo phong restart) khong ghi trung du lieu cu
    static void BigTradeLogDedupSurvivesRestart()
    {
        Console.WriteLine("[7] BigTradeLog: khong ghi trung khi mo lai (dedup qua file)");
        string path = Path.Combine(Path.GetTempPath(), "btl_test_" + Guid.NewGuid() + ".csv");
        try
        {
            var log1 = new BigTradeLog(path);
            log1.Load();
            bool wrote1 = log1.TryAppend(1000, DateTime.UtcNow, 4327.0, 55, 40, 10);
            Check(wrote1, "lan dau ghi thanh cong");
            bool wrote2 = log1.TryAppend(1000, DateTime.UtcNow, 4327.0, 55, 40, 10);
            Check(!wrote2, "ghi lai CUNG key (nen+gia) trong CUNG instance -> bi chan (dedup)");

            // "khoi dong lai" -> instance moi doc lai file cu
            var log2 = new BigTradeLog(path);
            log2.Load();
            Check(log2.Count == 1, "doc lai file thay dung 1 dong da ghi", $"count={log2.Count}");
            bool wrote3 = log2.TryAppend(1000, DateTime.UtcNow, 4327.0, 999, 1, 1);
            Check(!wrote3, "instance MOI cung chan ghi trung (da nap key tu file cu)");

            bool wrote4 = log2.TryAppend(2000, DateTime.UtcNow, 4328.0, 60, 50, 5);
            Check(wrote4, "nen/gia KHAC thi ghi duoc binh thuong");
        }
        finally { File.Delete(path); }
    }

    static int Main()
    {
        InMemoryRoundtrip();
        SurvivesRestart();
        LaterWriteOverrides();
        EmptyBarIsCached();
        CorruptLineIsSkipped();
        FingerprintMismatchMeansMiss();
        BigTradeLogDedupSurvivesRestart();
        Console.WriteLine(_fail == 0 ? "\n=== TAT CA PASS ===" : $"\n=== {_fail} FAIL ===");
        return _fail == 0 ? 0 : 1;
    }
}
