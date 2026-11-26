// ============================================================================
//  BenzoMt5 — LOGIC THUẦN gửi lệnh BenzoTrader sang MT5 (không tham chiếu Quantower SDK)
// ============================================================================
//  Ghi mỗi lệnh MỚI thành 1 dòng JSON vào <MT5 Common>\Files\benzo_cmd.jsonl; EA mt5-runner-bridge/RunnerBridge.mq5 đọc.
//  EA KHÔNG nhận giá tuyệt đối (futures lệch spot): chỉ side + sl_dist (USD/oz) + rr; EA vào market rồi đặt SL/TP quanh giá khớp.
//  4 chốt chống bắn trùng/lệnh cũ (giống RunnerSignal):
//    1) chỉ lệnh có nến vào là nến VỪA ĐÓNG (BarIdx == lastClosed)
//    2) lần quét đầu sau attach/reload/đổi settings chỉ NẠP id, không gửi
//    3) tuổi tín hiệu <= MaxAgeSec so với đồng hồ UTC
//    4) id tất định + tập id đã gửi (EA cũng lưu runner_done.txt)
//  MỌI `using` đặt BÊN TRONG namespace để nối file (concat) hợp lệ.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using System.Globalization;
    using System.IO;
    using System.Text;

    public sealed class Mt5Emitter
    {
        public const string FileName = "benzo_cmd.jsonl";

        public bool DryRun = true;
        public int MaxAgeSec = 90;
        public string Dir = "";                       // trống = %APPDATA%\MetaQuotes\Terminal\Common\Files
        public int Sent { get; private set; }
        public string Status { get; private set; }    // lý do bỏ / lỗi / ghi chú lần nạp đầu (null = không có gì)
        public string LastSent { get; private set; }  // mô tả lệnh gửi cuối
        public Action<string> OnWrite;                // test: bắt dòng thay vì ghi file

        private bool _armed;
        private readonly HashSet<string> _ids = new();

        public void Reset() { _armed = false; _ids.Clear(); Sent = 0; Status = null; LastSent = null; }

        public static string FilesDir(string configured)
        {
            string d = configured?.Trim();
            if (!string.IsNullOrEmpty(d)) return d;
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "MetaQuotes", "Terminal", "Common", "Files");
        }

        public static string BranchOf(Signal s) => s.Setup == 'A' ? "FB" : "BR";

        /// <summary>BENZO|symbol|yyyyMMddHHmm (giờ mở nến xác nhận, UTC)|B/S|FB/BR — tất định.</summary>
        public static string MakeId(string symbol, Signal s) =>
            $"BENZO|{symbol}|{s.Time.ToString("yyyyMMddHHmm", CultureInfo.InvariantCulture)}|{(s.Side > 0 ? "B" : "S")}|{BranchOf(s)}";

        /// <summary>1 dòng JSON (không có '\n'). Số luôn dùng dấu chấm (InvariantCulture). ts_utc = lúc nến xác nhận ĐÓNG (EA so với TimeGMT).</summary>
        public static string BuildLine(string id, string symbol, Signal s, DateTime closeUtc, int tzOffset, double rr, bool dry)
        {
            var ci = CultureInfo.InvariantCulture;
            double slDist = Math.Abs(s.Entry - s.Sl);
            return new StringBuilder()
                .Append("{\"id\":\"").Append(id).Append("\",")
                .Append("\"ts_utc\":\"").Append(closeUtc.ToString("yyyy-MM-dd HH:mm:ss", ci)).Append("\",")
                .Append("\"ts_local\":\"").Append(closeUtc.AddHours(tzOffset).ToString("yyyy-MM-dd HH:mm:ss", ci)).Append("\",")
                .Append("\"tz\":").Append(tzOffset.ToString(ci)).Append(',')
                .Append("\"src\":\"").Append(symbol).Append("\",")
                .Append("\"branch\":\"").Append(BranchOf(s)).Append("\",")
                .Append("\"side\":\"").Append(s.Side > 0 ? "BUY" : "SELL").Append("\",")
                .Append("\"sl_dist\":").Append(slDist.ToString("0.###", ci)).Append(',')
                .Append("\"rr\":").Append(rr.ToString("0.##", ci)).Append(',')
                .Append("\"src_entry\":").Append(s.Entry.ToString("0.0##", ci)).Append(',')
                .Append("\"src_sl\":").Append(s.Sl.ToString("0.0##", ci)).Append(',')
                .Append("\"src_tp\":").Append(s.Tp.ToString("0.0##", ci)).Append(',')
                .Append("\"setup\":\"").Append(BenzoCore.TheName(s.Setup)).Append("\",")
                .Append("\"dry\":").Append(dry ? "true" : "false")
                .Append('}').ToString();
        }

        /// <summary>Gọi sau mỗi lần engine Advance. enabled=false vẫn nạp id (bật giữa chừng không bắn lệnh cũ).
        /// lastBarOpenUtc = giờ mở nến vừa đóng (để báo lệch feed↔đồng hồ lần nạp đầu).</summary>
        public void Process(IReadOnlyList<Signal> all, int lastClosed, string symbol, int tzOffset, int barMinutes,
                            bool enabled, bool enableFailBreak, bool enableBreak, DateTime utcNow, DateTime lastBarOpenUtc)
        {
            try
            {
                if (!_armed)
                {
                    foreach (var s0 in all) _ids.Add(MakeId(symbol, s0));
                    _armed = true;
                    if (enabled)
                    {
                        double skew = (utcNow - lastBarOpenUtc.AddMinutes(barMinutes)).TotalSeconds;
                        Status = $"nạp {_ids.Count} lệnh cũ (không gửi) · lệch feed↔đồng hồ {skew:0} giây";
                    }
                    return;
                }
                foreach (var s in all)
                {
                    if (s.BarIdx != lastClosed) continue;
                    string id = MakeId(symbol, s);
                    if (!_ids.Add(id)) continue;
                    if (!enabled) continue;
                    if (s.Setup == 'A' ? !enableFailBreak : !enableBreak) continue;
                    var closeUtc = s.Time.AddMinutes(barMinutes);
                    double age = (utcNow - closeUtc).TotalSeconds;
                    if (age > MaxAgeSec || age < -MaxAgeSec)
                    {
                        Status = $"bỏ lệnh {s.Time.AddHours(tzOffset):dd/MM HH:mm} vì lệch đồng hồ {age:0} giây (quá {MaxAgeSec} giây)";
                        continue;
                    }
                    double slDist = Math.Abs(s.Entry - s.Sl);
                    if (slDist <= 0) { Status = $"bỏ lệnh {s.Time.AddHours(tzOffset):dd/MM HH:mm} vì SL bằng 0"; continue; }
                    string line = BuildLine(id, symbol, s, closeUtc, tzOffset, 2.0, DryRun);
                    if (!Write(line)) continue;
                    Sent++;
                    LastSent = $"{s.Time.AddHours(tzOffset):dd/MM HH:mm} {BenzoCore.TheName(s.Setup)} {(s.Side > 0 ? "buy" : "sell")} SL {slDist.ToString("0.0", new CultureInfo("vi-VN"))}";
                    Status = null;
                }
            }
            catch (Exception ex) { Status = "lỗi " + ex.Message; }
        }

        private bool Write(string line)
        {
            if (OnWrite != null) { OnWrite(line); return true; }
            try
            {
                string dir = FilesDir(Dir);
                Directory.CreateDirectory(dir);
                using var fs = new FileStream(Path.Combine(dir, FileName), FileMode.Append, FileAccess.Write, FileShare.ReadWrite);
                using var w = new StreamWriter(fs, new UTF8Encoding(false));
                w.Write(line + "\n");
                return true;
            }
            catch (Exception ex) { Status = "không ghi được file — " + ex.Message; return false; }
        }

        /// <summary>Dòng bảng chart: "MT5 (chạy thử): đã gửi N · lệnh cuối … · lý do bỏ".</summary>
        public string TableLine()
        {
            string s = $"MT5{(DryRun ? " (chạy thử)" : "")}: đã gửi {Sent}" + (LastSent != null ? $" · lệnh cuối {LastSent}" : "");
            if (Status != null) s += " · " + Status;
            return s;
        }
    }
}
