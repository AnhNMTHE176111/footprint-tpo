// Test cầu nối MT5 (BenzoMt5.cs): định dạng dòng JSON, id, nạp lần đầu, tuổi, trùng, nến vừa đóng, công tắc setup.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.Json;
using BenzoTraderNs;

static partial class Program
{
    static Signal Mt5Sig(int barIdx, int side = 1, char setup = 'B', double entry = 4127.4, double sl = 4124.2, double tp = 4133.8)
        => new Signal { Setup = setup, Side = side, Entry = entry, Sl = sl, Tp = tp, BarIdx = barIdx, Time = T0.AddMinutes(barIdx) };

    static void TestsMt5()
    {
        Console.WriteLine("[MT5] Cầu nối benzo_cmd.jsonl");
        var old = CultureInfo.CurrentCulture;
        CultureInfo.CurrentCulture = new CultureInfo("vi-VN");   // dấu phẩy thập phân: dòng JSON vẫn phải dùng dấu chấm
        try
        {
            var s = Mt5Sig(10);
            string id = Mt5Emitter.MakeId("GCZ26", s);
            Check(id == "BENZO|GCZ26|202610210310|B|BR", "id tất định, prefix BENZO", id);
            Check(Mt5Emitter.MakeId("GCZ26", Mt5Sig(10, -1, 'A')) == "BENZO|GCZ26|202610210310|S|FB", "id sell Fail Break");
            Check(Mt5Emitter.MakeId("GCZ26", s) == id, "id lặp lại giống hệt");

            var close = s.Time.AddMinutes(1);
            string line = Mt5Emitter.BuildLine(id, "GCZ26", s, close, 7, 2.0, true);
            using var doc = JsonDocument.Parse(line);
            var r = doc.RootElement;
            Check(r.GetProperty("id").GetString() == id, "JSON: id");
            Check(r.GetProperty("side").GetString() == "BUY", "JSON: side BUY");
            Check(Near(r.GetProperty("sl_dist").GetDouble(), 3.2, 1e-9), "JSON: sl_dist = |entry − SL| = 3,2", r.GetProperty("sl_dist").ToString());
            Check(Near(r.GetProperty("rr").GetDouble(), 2.0), "JSON: rr = 2");
            Check(r.GetProperty("ts_utc").GetString() == "2026-10-21 03:11:00", "JSON: ts_utc = giờ ĐÓNG nến xác nhận (UTC)", r.GetProperty("ts_utc").GetString());
            Check(r.GetProperty("dry").GetBoolean() && r.GetProperty("branch").GetString() == "BR", "JSON: dry + branch");
            Check(Near(r.GetProperty("src_entry").GetDouble(), 4127.4) && r.GetProperty("setup").GetString() == "Break", "JSON: src_entry + setup (chỉ để log)");
            Check(line.Contains("\"sl_dist\":3.2,") && !line.Contains("3,2"), "dấu thập phân là dấu chấm dù culture vi-VN", line);
            Check(Mt5Emitter.BuildLine(id, "GCZ26", s, close, 7, 2.0, false).EndsWith("\"dry\":false}"), "dry=false");
            // khớp parser EA (JStr/JNum/JBool tìm theo "key": liền nhau, không khoảng trắng)
            foreach (var k in new[] { "\"id\":\"", "\"side\":\"BUY\"", "\"ts_utc\":\"", "\"sl_dist\":", "\"rr\":", "\"dry\":true", "\"branch\":\"" })
                Check(line.Contains(k), "EA đọc được trường " + k);

            // ---- Process
            var T = T0.AddMinutes(11);                      // "bây giờ" = vừa đóng nến idx 10
            var sent = new List<string>();
            Mt5Emitter Make() => new Mt5Emitter { OnWrite = l => sent.Add(l), MaxAgeSec = 90 };
            void Run(Mt5Emitter e, List<Signal> all, int lastClosed, bool on = true, bool fb = true, bool br = true, DateTime? now = null)
                => e.Process(all, lastClosed, "GCZ26", 7, 1, on, fb, br, now ?? T, T0.AddMinutes(lastClosed));

            var e1 = Make();
            Run(e1, new List<Signal> { Mt5Sig(10) }, 10);
            Check(sent.Count == 0 && e1.Sent == 0, "lần quét đầu chỉ nạp id, không gửi (kể cả lệnh nến vừa đóng)");
            Run(e1, new List<Signal> { Mt5Sig(10) }, 10);
            Check(sent.Count == 0, "quét lại cùng lệnh sau khi nạp: vẫn không gửi");
            var all2 = new List<Signal> { Mt5Sig(10), Mt5Sig(11, -1, 'A', 4130, 4133) };
            Run(e1, all2, 11, now: T0.AddMinutes(12));
            Check(sent.Count == 1 && sent[0].Contains("\"branch\":\"FB\"") && sent[0].Contains("\"side\":\"SELL\""), "lệnh mới ở nến vừa đóng được gửi", sent.Count.ToString());
            Check(Near(JsonDocument.Parse(sent[0]).RootElement.GetProperty("sl_dist").GetDouble(), 3.0), "sl_dist sell = 3,0");
            Run(e1, all2, 11, now: T0.AddMinutes(12));
            Check(sent.Count == 1 && e1.Sent == 1, "không gửi trùng");
            Check(e1.TableLine().StartsWith("MT5 (chạy thử): đã gửi 1 · lệnh cuối") && e1.TableLine().Contains("Fail Break sell SL 3,0"), "dòng bảng", e1.TableLine());

            // lệnh cũ: nến vào không phải nến vừa đóng
            sent.Clear(); var e2 = Make();
            Run(e2, new List<Signal>(), 10);
            Run(e2, new List<Signal> { Mt5Sig(9) }, 10);
            Check(sent.Count == 0, "chỉ nến vừa đóng: lệnh nến cũ (idx 9, lastClosed 10) không gửi");

            // quá tuổi
            sent.Clear(); var e3 = Make();
            Run(e3, new List<Signal>(), 10);
            Run(e3, new List<Signal> { Mt5Sig(10) }, 10, now: T0.AddMinutes(11).AddSeconds(200));
            Check(sent.Count == 0 && e3.TableLine().Contains("lệch đồng hồ 200"), "tuổi > 90 giây bị bỏ + báo lý do", e3.TableLine());
            Run(e3, new List<Signal> { Mt5Sig(10) }, 10);
            Check(sent.Count == 0, "lệnh đã bỏ vì tuổi không được thử lại");
            sent.Clear(); var e3b = Make();
            Run(e3b, new List<Signal>(), 10);
            Run(e3b, new List<Signal> { Mt5Sig(10) }, 10, now: T0.AddMinutes(11).AddSeconds(-200));
            Check(sent.Count == 0, "đồng hồ lệch về phía trước (tuổi âm quá ngưỡng) cũng bị bỏ");
            sent.Clear(); var e3c = Make();
            Run(e3c, new List<Signal>(), 10);
            Run(e3c, new List<Signal> { Mt5Sig(10) }, 10, now: T0.AddMinutes(11).AddSeconds(89));
            Check(sent.Count == 1, "tuổi 89 giây vẫn gửi");

            // công tắc
            sent.Clear(); var e4 = Make();
            Run(e4, new List<Signal>(), 10);
            Run(e4, new List<Signal> { Mt5Sig(10, 1, 'A') }, 10, fb: false);
            Run(e4, new List<Signal> { Mt5Sig(10, 1, 'B') }, 10, br: false);
            Check(sent.Count == 0, "setup bị tắt ở Settings không gửi");

            // tắt gửi rồi bật: không bắn lệnh sinh ra lúc tắt
            sent.Clear(); var e5 = Make();
            Run(e5, new List<Signal>(), 10, on: false);
            Run(e5, new List<Signal> { Mt5Sig(10) }, 10, on: false);
            Run(e5, new List<Signal> { Mt5Sig(10) }, 10, on: true);
            Check(sent.Count == 0, "lệnh sinh ra lúc tắt gửi, bật sau đó: không bắn bù");
            Run(e5, new List<Signal> { Mt5Sig(10), Mt5Sig(11) }, 11, now: T0.AddMinutes(12));
            Check(sent.Count == 1, "bật gửi rồi: lệnh mới được gửi");

            // Reset (engine dựng lại) => nạp lại, không bắn
            sent.Clear(); e1.Reset();
            Run(e1, all2, 11, now: T0.AddMinutes(12));
            Check(sent.Count == 0 && e1.Sent == 0, "Reset: lần quét sau đó chỉ nạp id");

            // ghi file thật
            string dir = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "benzo_mt5_test");
            if (System.IO.Directory.Exists(dir)) System.IO.Directory.Delete(dir, true);
            var e6 = new Mt5Emitter { Dir = dir };
            e6.Process(new List<Signal>(), 10, "GCZ26", 7, 1, true, true, true, T, T0.AddMinutes(10));
            e6.Process(new List<Signal> { Mt5Sig(10) }, 10, "GCZ26", 7, 1, true, true, true, T, T0.AddMinutes(10));
            var lines = System.IO.File.ReadAllLines(System.IO.Path.Combine(dir, "benzo_cmd.jsonl"));
            Check(lines.Length == 1 && JsonDocument.Parse(lines[0]).RootElement.GetProperty("id").GetString() == id, "ghi file benzo_cmd.jsonl 1 dòng/lệnh, parse lại được");
            Check(Mt5Emitter.FilesDir("").EndsWith(System.IO.Path.Combine("Terminal", "Common", "Files")) && Mt5Emitter.FilesDir(" X ") == "X", "thư mục mặc định/tuỳ chỉnh");
        }
        finally { CultureInfo.CurrentCulture = old; }
    }
}
