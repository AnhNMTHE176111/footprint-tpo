// ============================================================================
//  SignalCache — niêm phong tín hiệu bóng theo THỜI GIAN MỞ NẾN (2026-09-15)
// ============================================================================
//  Vấn đề gốc: OrderFlowBubbles.ResetState() (gọi mỗi khi Quantower nạp lại
//  Volume Analysis, KHÔNG chỉ 1 lần lúc mở indicator) xoá sạch _bubbles rồi
//  tính lại TOÀN BỘ lịch sử. Dữ liệu per-level của nến QUÁ KHỨ do feed cấp lại
//  thường mỏng hơn lúc nến còn đang chạy live (đã xác nhận: MaxOneTradeVolume
//  luôn về 0 khi tải lại lịch sử) → bóng đã nổ có thể KHÔNG còn đủ điều kiện ở
//  lần tính lại, và biến mất dù giá/nến không đổi.
//
//  Cách sửa: mỗi nến ĐÃ ĐÓNG chỉ được PHÉP TÍNH TÍN HIỆU MỘT LẦN TRONG ĐỜI.
//  Kết quả (nổ bóng gì, ở đâu) được NIÊM PHONG — lưu vào bộ nhớ + ghi ra file —
//  khoá theo THỜI GIAN MỞ NẾN (bar.TimeLeft), KHÔNG khoá theo chỉ số idx (idx có
//  thể lệch giữa các lần nếu Quantower tải nhiều/ít lịch sử hơn). Lần sau nếu
//  ResetState() chạy lại, nến đã niêm phong được KHÔI PHỤC nguyên trạng thay vì
//  tính lại — dù dữ liệu VA của nến đó lúc này có mỏng đi cũng không còn ảnh
//  hưởng. File cũng dùng luôn làm log để backtest (mục đích thứ hai, miễn phí).
//
//  Class này KHÔNG tham chiếu TradingPlatform.BusinessLayer -> build/test độc
//  lập được (xem tests/), không cần SDK Quantower.
// ============================================================================

using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace OrderFlowBubbles
{
    // Bản sao "phẳng" của 1 bubble — đủ dữ liệu để vẽ lại y hệt, không phụ thuộc
    // enum Shape/Color của file chính (dùng int/argb) để tránh vòng phụ thuộc.
    public sealed class CachedBubbleData
    {
        public double Price { get; set; }
        public int Shape { get; set; }
        public int ColorArgb { get; set; }
        public int Size { get; set; }
        public int Transparency { get; set; }
        public bool Halo { get; set; }
        public bool UseBarWidth { get; set; }
        public string Tooltip { get; set; }
        public int Confirm { get; set; }      // 0=đang chờ, +1=giữ mức, -1=vỡ mức
        public bool Confirmable { get; set; } // true = bubble này thuộc luồng Absorption (được theo dõi Confirm)
        public double PriceHi { get; set; }   // vùng Stacked Imbalance: mép trên (Price = mép dưới); bản ghi cũ = 0
        public int ZoneSide { get; set; }     // vùng Stacked Imbalance: +1 buy / −1 sell; 0 = không phải vùng
        public bool ZoneWeak { get; set; }    // vùng Stacked Imbalance: nằm ở râu ngược chiều (bị rút râu)
    }

    public sealed class CachedBarData
    {
        public long TimeTicks { get; set; }
        public int Tint { get; set; }
        public List<CachedBubbleData> Bubbles { get; set; } = new();
        // "Dấu vân tay" tham số đang chạy lúc tính ra bản ghi này (xem ComputeSettingsFingerprint
        // trong OrderFlowBubbles.cs). Khi người dùng ĐỔI THAM SỐ (vd bật mode ngưỡng cố định), dấu
        // vân tay hiện tại sẽ KHÁC bản ghi cũ -> coi là "chưa niêm phong", tính lại theo tham số mới
        // — khác với việc feed nạp lại dữ liệu (tham số KHÔNG đổi, dấu vân tay khớp, vẫn niêm phong).
        public string SettingsFingerprint { get; set; } = "";
    }

    // Niêm phong: mỗi nến (khoá = thời gian mở nến, tick DateTime) giữ ĐÚNG 1 bản
    // ghi mới nhất. File JSON Lines — mỗi dòng 1 nến; ghi thêm dòng CÙNG thời gian
    // (vd khi Absorption chuyển từ "đang chờ" sang "giữ/vỡ mức") sẽ ĐÈ bản cũ khi
    // đọc lại (đọc tuần tự, gán vào Dictionary — dòng sau thắng).
    public sealed class SignalCache
    {
        private readonly Dictionary<long, CachedBarData> _byTime = new();
        private readonly object _fileLock = new();

        public string FilePath { get; }

        public SignalCache(string filePath) { FilePath = filePath; }

        public int Count => _byTime.Count;

        public bool TryGet(long timeTicks, out CachedBarData data) => _byTime.TryGetValue(timeTicks, out data);

        public void Load()
        {
            _byTime.Clear();
            if (string.IsNullOrEmpty(FilePath) || !File.Exists(FilePath)) return;
            foreach (var line in File.ReadLines(FilePath))
            {
                if (string.IsNullOrWhiteSpace(line)) continue;
                CachedBarData d;
                try { d = JsonSerializer.Deserialize<CachedBarData>(line); }
                catch { continue; }   // dòng hỏng (vd ghi dở khi crash) -> bỏ qua, không chết cả file
                if (d != null) _byTime[d.TimeTicks] = d;
            }
        }

        // Ghi/đè bản ghi trong bộ nhớ + append 1 dòng vào file.
        public void Put(CachedBarData data)
        {
            _byTime[data.TimeTicks] = data;
            if (string.IsNullOrEmpty(FilePath)) return;
            string json = JsonSerializer.Serialize(data);
            lock (_fileLock)
            {
                string dir = Path.GetDirectoryName(FilePath);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                File.AppendAllText(FilePath, json + Environment.NewLine);
            }
        }

        public static string SanitizeFileName(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s;
        }

        // ---------------- FIX 2026-11-09: bóng / vùng / tam giác LƠ LỬNG giữa chart ----------------
        //  Bản cũ đặt tên file = mã + Aggregation.Name. Với nến thời gian Name chỉ là "Time" → M1, M15,
        //  M30, H1… DÙNG CHUNG 1 file, mà khoá lại là GIỜ MỞ NẾN. Nến M15 lúc 11:00 ghi sau sẽ ĐÈ bản ghi
        //  của nến M1 lúc 11:00; lần nạp lại kế tiếp (đổi History range, mở lại chart) M1 khôi phục bóng
        //  của nến M15 → vẽ ở giá của cả cây M15, xa thân nến M1. Đo file thật: 1.151 bóng nằm ngoài
        //  biên độ nến, 100 % ở phút :00/:15/:30/:45. Sửa: tên file có khung (vd Time_1Minute).

        /// <summary>Tên file cache THEO KHUNG: mã + kiểu nến + khung (vd "_GCZ26_XCEC_Time_1Minute").</summary>
        public static string CacheName(string symbol, string aggregation, string timeframe)
            => SanitizeFileName($"{symbol}_{aggregation}_{timeframe}");

        /// <summary>Tên file kiểu cũ (không có khung) — chỉ dùng để chuyển dữ liệu sang file mới.</summary>
        public static string LegacyCacheName(string symbol, string aggregation)
            => SanitizeFileName(symbol + "_" + aggregation);

        /// <summary>Mọi bóng của bản ghi có nằm trong biên độ nến (± tol) không. Bóng do chính nến đó sinh ra
        /// luôn nằm trong [Low, High]; nằm ngoài = bản ghi của nến khác (khung khác) → không được khôi phục.</summary>
        public static bool FitsBar(CachedBarData d, double high, double low, double tol)
        {
            if (d?.Bubbles == null) return true;
            foreach (var b in d.Bubbles)
            {
                if (b.Price < low - tol || b.Price > high + tol) return false;
                if (b.ZoneSide != 0 && (b.PriceHi < low - tol || b.PriceHi > high + tol)) return false;
            }
            return true;
        }

        /// <summary>Bản ghi file cũ chắc chắn là của nến M1: phút KHÔNG chia hết cho 5 (M5/M15/M30/H1 không mở ở đó).</summary>
        public static bool IsSafeLegacyM1(long timeTicks) => new DateTime(timeTicks).Minute % 5 != 0;

        /// <summary>Chép từ file cũ các bản ghi thoả <paramref name="keep"/> (chưa có trong cache này) — ghi 1 lần.
        /// Trả về số bản ghi đã chép.</summary>
        public int ImportLegacy(string legacyPath, Func<long, bool> keep)
        {
            if (string.IsNullOrEmpty(legacyPath) || !File.Exists(legacyPath) || keep == null) return 0;
            var old = new SignalCache(legacyPath);
            old.Load();
            var take = new List<CachedBarData>();
            foreach (var d in old._byTime.Values)
                if (keep(d.TimeTicks) && !_byTime.ContainsKey(d.TimeTicks)) take.Add(d);
            if (take.Count == 0) return 0;
            take.Sort((a, b) => a.TimeTicks.CompareTo(b.TimeTicks));
            var sb = new System.Text.StringBuilder();
            foreach (var d in take) { _byTime[d.TimeTicks] = d; sb.Append(JsonSerializer.Serialize(d)).Append(Environment.NewLine); }
            if (!string.IsNullOrEmpty(FilePath))
                lock (_fileLock)
                {
                    string dir = Path.GetDirectoryName(FilePath);
                    if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                    File.AppendAllText(FilePath, sb.ToString());
                }
            return take.Count;
        }
    }

    // ========================================================================
    //  BigTradeLog — ghi lại PHÂN PHỐI THẬT của lệnh đơn (2026-09-16)
    // ========================================================================
    //  Lý do: chưa từng đo được "lệnh đơn bao nhiêu là to" bằng số liệu thật, vì
    //  MỌI file lịch sử export ra đều có MaxOneTradeVolume = 0 (feed chỉ cấp số
    //  này lúc đang chạy SỐNG). Log này ghi lại NGUYÊN VẸN từng lệnh đơn thật
    //  quan sát được trong lúc feed sống, để vài ngày sau có đủ dữ liệu đo lại
    //  con số ngưỡng cho chuẩn (thay vì đoán 35 hay 50).
    //
    //  Chỉ ghi 1 dòng / (nến, mức giá) — dedup bằng key nạp từ file lúc Load(),
    //  để chạy lại (mở lại indicator) không ghi trùng dữ liệu cũ.
    // ========================================================================
    public sealed class BigTradeLog
    {
        private readonly HashSet<string> _seen = new();
        private readonly object _fileLock = new();
        private bool _headerWritten;

        public string FilePath { get; }

        public BigTradeLog(string filePath) { FilePath = filePath; }

        public int Count => _seen.Count;

        public void Load()
        {
            _seen.Clear();
            _headerWritten = false;
            if (string.IsNullOrEmpty(FilePath) || !File.Exists(FilePath)) return;
            bool first = true;
            foreach (var line in File.ReadLines(FilePath))
            {
                if (first) { first = false; _headerWritten = true; continue; } // dòng header
                if (string.IsNullOrWhiteSpace(line)) continue;
                var parts = line.Split(',');
                if (parts.Length < 2) continue;
                _seen.Add(parts[0] + "|" + parts[2]); // time_ticks|price
            }
        }

        // Trả về true nếu vừa ghi mới (false nếu đã có từ trước -> bỏ qua, tránh trùng).
        public bool TryAppend(long timeTicks, DateTime timeUtc, double price, double mot, double buy, double sell)
        {
            string key = timeTicks + "|" + price;
            lock (_fileLock)
            {
                if (_seen.Contains(key)) return false;
                _seen.Add(key);
                if (string.IsNullOrEmpty(FilePath)) return true;
                string dir = Path.GetDirectoryName(FilePath);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                if (!_headerWritten)
                {
                    File.AppendAllText(FilePath, "time_ticks,time_iso,price,mot,buy,sell" + Environment.NewLine);
                    _headerWritten = true;
                }
                string line = string.Join(",", timeTicks, timeUtc.ToString("o"), price, mot, buy, sell);
                File.AppendAllText(FilePath, line + Environment.NewLine);
                return true;
            }
        }
    }
}
