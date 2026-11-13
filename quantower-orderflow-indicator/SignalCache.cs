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
using System.Text.Json.Serialization;

namespace OrderFlowBubbles
{
    // Bộ (de)serialize SINH SẴN lúc biên dịch (System.Text.Json source generator): không phản chiếu, không JIT
    // ở lần đọc đầu (đo 1,65 s -> ~0,4 s). Cùng JSON với JsonSerializer.Serialize<CachedBarData> mặc định.
    [JsonSerializable(typeof(CachedBarData))]
    internal partial class SignalCacheJson : JsonSerializerContext { }

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
        public double SizeFrac { get; set; }  // Ô lớn: tỉ lệ cỡ 0..1 (bản ghi cũ = 0 = đầy đủ)
        public string Tooltip { get; set; }
        public int Confirm { get; set; }      // 0=đang chờ, +1=giữ mức, -1=vỡ mức
        public bool Confirmable { get; set; } // true = bubble này thuộc luồng Absorption (được theo dõi Confirm)
        public double PriceHi { get; set; }   // vùng Stacked Imbalance: mép trên (Price = mép dưới); bản ghi cũ = 0
        public int ZoneSide { get; set; }     // vùng Stacked Imbalance: +1 buy / −1 sell; 0 = không phải vùng
        public bool ZoneWeak { get; set; }    // vùng Stacked Imbalance: nằm ở râu ngược chiều (bị rút râu)
        public bool CellBig { get; set; }     // Ô Bid/Ask lớn (bản ghi cũ = false)
        public double CellBid { get; set; }
        public double CellAsk { get; set; }
        public int CellSide { get; set; }     // +1 xanh / -1 đỏ / 0 tím
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

        /// <summary>Mọi bản ghi đang giữ (dùng cho golden test perf/Golden để băm nội dung cache).</summary>
        internal IEnumerable<CachedBarData> Values => _byTime.Values;

        public bool TryGet(long timeTicks, out CachedBarData data) => _byTime.TryGetValue(timeTicks, out data);

        /// <summary>Quá file lớn hơn mức này thì đọc kiểu cũ (từng dòng) thay vì nạp cả file vào bộ nhớ.</summary>
        private const long MaxFastLoadBytes = 1_000_000_000L;

        /// <summary>Đọc file niêm phong: mỗi nến giữ bản ghi thắng cuối (dòng hỏng bị bỏ qua).
        /// <paramref name="compact"/> = true: nếu số dòng &gt; 1,2 × số nến duy nhất thì viết lại file chỉ còn bản ghi thắng
        /// (ghi file tạm rồi thay thế; chỉ khi file không đổi từ lúc đọc).</summary>
        public void Load(bool compact = false)
        {
            _byTime.Clear();
            if (string.IsNullOrEmpty(FilePath) || !File.Exists(FilePath)) return;
            bool ok = false;
            try
            {
                if (new FileInfo(FilePath).Length <= MaxFastLoadBytes) ok = TryLoadFast(compact);
            }
            catch { ok = false; }
            if (!ok) { _byTime.Clear(); LoadSlow(); }
        }

        // Đường chậm = bản gốc: ReadLines + Deserialize từng dòng (dòng sau thắng).
        private void LoadSlow()
        {
            foreach (var line in File.ReadLines(FilePath))
            {
                if (string.IsNullOrWhiteSpace(line)) continue;
                CachedBarData d;
                try { d = JsonSerializer.Deserialize<CachedBarData>(line); }
                catch { continue; }   // dòng hỏng (vd ghi dở khi crash) -> bỏ qua, không chết cả file
                if (d != null) _byTime[d.TimeTicks] = d;
            }
        }

        // Đường nhanh: đọc cả file 1 lần, chỉ lập chỉ mục theo "TimeTicks" (khoá nằm ngay đầu mỗi dòng do chính mình ghi),
        // rồi giải mã CHỈ dòng thắng bằng bộ sinh sẵn. Gặp BẤT KỲ dòng không đúng dạng chuẩn -> trả false để dùng đường
        // chậm (kết quả luôn như bản gốc). Dòng thắng giải mã hỏng (ghi dở) -> lùi về dòng trước cùng khoá, đúng như
        // bản gốc (dòng hỏng không đè dòng tốt).
        private bool TryLoadFast(bool compact)
        {
            var writeTime = new FileInfo(FilePath).LastWriteTimeUtc;
            byte[] all = File.ReadAllBytes(FilePath);
            var span = all.AsSpan();
            int pos = (span.Length >= 3 && span[0] == 0xEF && span[1] == 0xBB && span[2] == 0xBF) ? 3 : 0;
            ReadOnlySpan<byte> keyPrefix = "{\"TimeTicks\":"u8;
            var st = new List<int>(); var en = new List<int>(); var prev = new List<int>();
            var last = new Dictionary<long, int>();
            int garbage = 0;   // dòng không giải mã được (ghi dở/rác): bị bỏ qua như bản gốc, và bị loại khi nén
            while (pos < all.Length)
            {
                int nl = span.Slice(pos).IndexOf((byte)'\n');
                int end = nl < 0 ? all.Length : pos + nl;
                int next = nl < 0 ? all.Length : end + 1;
                if (end > pos && all[end - 1] == (byte)'\r') end--;
                var line = span.Slice(pos, end - pos);
                pos = next;
                if (IsBlank(line)) continue;
                if (line.IndexOf((byte)'\r') >= 0) return false;   // \r lẻ giữa dòng: ReadLines sẽ tách khác -> đường chậm
                int p = keyPrefix.Length, digits = 0; long t = 0;
                bool standard = line.StartsWith(keyPrefix);
                if (standard)
                {
                    while (p < line.Length && line[p] >= (byte)'0' && line[p] <= (byte)'9') { if (++digits > 18) { standard = false; break; } t = t * 10 + (line[p] - (byte)'0'); p++; }
                    if (standard && (digits == 0 || p >= line.Length || (line[p] != (byte)',' && line[p] != (byte)'}'))) standard = false;
                }
                if (!standard)
                {
                    // dòng lạ: nếu cũng KHÔNG giải mã được (rác/ghi dở) thì bản gốc cũng bỏ qua -> bỏ qua luôn;
                    // còn nếu giải mã được (JSON dạng khác thường) -> nhường cho đường chậm để giữ đúng thứ tự "dòng sau thắng".
                    try { if (JsonSerializer.Deserialize(line, SignalCacheJson.Default.CachedBarData) != null) return false; }
                    catch { }
                    garbage++;
                    continue;
                }
                int li = st.Count;
                st.Add(end - line.Length); en.Add(end);
                prev.Add(last.TryGetValue(t, out int pj) ? pj : -1);
                last[t] = li;
            }
            int lines = st.Count + garbage;
            var winners = new List<int>(last.Count);
            foreach (var kv in last)
            {
                for (int j = kv.Value; j >= 0; j = prev[j])
                {
                    CachedBarData d;
                    try { d = JsonSerializer.Deserialize(span.Slice(st[j], en[j] - st[j]), SignalCacheJson.Default.CachedBarData); }
                    catch { continue; }   // dòng hỏng -> thử dòng cũ hơn cùng khoá
                    if (d == null) continue;
                    if (d.TimeTicks != kv.Key) return false;   // khác thường -> dùng đường chậm cho chắc
                    _byTime[kv.Key] = d; winners.Add(j);
                    break;
                }
            }
            if (compact && lines > 1.2 * last.Count && winners.Count < lines) { winners.Sort(); Compact(all, st, en, winners, writeTime); }
            return true;
        }

        private static bool IsBlank(ReadOnlySpan<byte> line)
        {
            foreach (byte b in line) if (b != (byte)' ' && b != (byte)'\t' && b != (byte)'\r') return false;
            return true;
        }

        // Viết lại file chỉ còn bản ghi thắng (NGUYÊN VĂN từng dòng, không serialize lại). Tạo file tạm rồi thay thế;
        // bỏ qua nếu file đã đổi từ lúc đọc (instance khác đang ghi) hoặc bị khoá. KHÔNG bao giờ ném lỗi.
        private void Compact(byte[] all, List<int> st, List<int> en, List<int> winners, DateTime readWriteTime)
        {
            string tmp = FilePath + ".tmp";
            try
            {
                byte[] nl = System.Text.Encoding.UTF8.GetBytes(Environment.NewLine);
                using (var fs = new FileStream(tmp, FileMode.Create, FileAccess.Write, FileShare.None, 1 << 16))
                    foreach (int j in winners) { fs.Write(all, st[j], en[j] - st[j]); fs.Write(nl, 0, nl.Length); }
                var fi = new FileInfo(FilePath);
                if (fi.Length != all.Length || fi.LastWriteTimeUtc != readWriteTime) { File.Delete(tmp); return; }
                File.Move(tmp, FilePath, true);
            }
            catch { try { File.Delete(tmp); } catch { } }
        }

        // ---- GHI THEO LÔ (perf 2026-11-11) ----
        //  Bản cũ: mỗi Put = serialize + CreateDirectory + File.AppendAllText (mở-ghi-đóng file) ~180-230 µs;
        //  nạp nguội 87k nến ghi 108k lần = 25 s. Giờ Put chỉ cập nhật bộ nhớ + hàng đợi; mỗi nến CHỈ giữ bản
        //  cuối (Confirm giữ/vỡ ghi đè nhiều lần trong 1 lượt chỉ tốn 1 dòng). Flush() ghi 1 lần: cuối Process,
        //  OnClear, Dispose, và tự động mỗi FlushEvery bản ghi chờ (crash giữa chừng chỉ mất ≤ 1 lô;
        //  dòng ghi dở đã được Load bỏ qua). Kết quả Load() giống hệt cách ghi từng dòng (dòng sau thắng).
        public const int FlushEvery = 4096;
        private readonly Dictionary<long, int> _pendingIdx = new();
        private readonly List<CachedBarData> _pending = new();

        /// <summary>Số bản ghi đang chờ ghi xuống file.</summary>
        public int PendingCount { get { lock (_fileLock) return _pending.Count; } }

        // Ghi/đè bản ghi trong bộ nhớ + xếp hàng ghi file (xem Flush).
        public void Put(CachedBarData data)
        {
            _byTime[data.TimeTicks] = data;
            if (string.IsNullOrEmpty(FilePath)) return;
            bool flushNow;
            lock (_fileLock)
            {
                if (_pendingIdx.TryGetValue(data.TimeTicks, out int i)) _pending[i] = data;
                else { _pendingIdx[data.TimeTicks] = _pending.Count; _pending.Add(data); }
                flushNow = _pending.Count >= FlushEvery;
            }
            if (flushNow) Flush();
        }

        /// <summary>Ghi mọi bản ghi đang chờ xuống file (append, 1 lần mở file). Không ném lỗi I/O: lỗi thì giữ hàng đợi, thử lại lần sau.</summary>
        public void Flush()
        {
            lock (_fileLock)
            {
                if (_pending.Count == 0 || string.IsNullOrEmpty(FilePath)) return;
                try
                {
                    string dir = Path.GetDirectoryName(FilePath);
                    if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                    bool needNewline = false;   // file kết thúc dở (crash) -> xuống dòng trước, kẻo dính vào dòng hỏng
                    if (File.Exists(FilePath))
                        using (var rf = new FileStream(FilePath, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
                            if (rf.Length > 0) { rf.Seek(-1, SeekOrigin.End); needNewline = rf.ReadByte() != 10; }
                    using (var fs = new FileStream(FilePath, FileMode.Append, FileAccess.Write, FileShare.Read, 1 << 16))
                    using (var w = new StreamWriter(fs, new System.Text.UTF8Encoding(false), 1 << 16))
                    {
                        if (needNewline) w.Write(Environment.NewLine);
                        foreach (var d in _pending) { w.Write(JsonSerializer.Serialize(d, SignalCacheJson.Default.CachedBarData)); w.Write(Environment.NewLine); }
                    }
                    _pending.Clear(); _pendingIdx.Clear();
                }
                catch (IOException) { }
                catch (UnauthorizedAccessException) { }
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
