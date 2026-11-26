// ============================================================================
//  OrderFlow Bubbles  —  custom footprint / order-flow signal indicator for QUANTOWER
// ============================================================================
//  Đọc footprint (Volume Analysis) theo TỪNG MỨC GIÁ, gom tín hiệu order-flow thành
//  hình vẽ trên chart. Bật/tắt từng phần. TẬP TRUNG VÀNG (GC/MGC).
//
//  ---- NGUYÊN TẮC PORTABLE (cốt lõi, xem plan) --------------------------------
//  Số delta/volume KHÁC NHAU theo feed/sàn (single vs double count, GC 100oz vs
//  MGC 10oz, cách gộp lệnh...) → ngưỡng tuyệt đối vô nghĩa. TẤT CẢ trigger dùng
//  thống kê TƯƠNG ĐỐI + ROBUST: modified z-score theo median + MAD trên baseline
//  động, hoặc tỷ lệ (deltaPct = Delta/Volume). Knob tuyệt đối DUY NHẤT còn lại là
//  MinActivityFloor (chống nhiễu nến đêm mỏng). Dùng median+MAD (KHÔNG mean+std) vì
//  volume đuôi nặng: std bị thổi phồng bởi chính cú spike ta muốn bắt.
//
//  ---- API QUANTOWER (đã kiểm chứng trên TradingPlatform.BusinessLayer.dll) -----
//  VolumeAnalysisItem (per-level VÀ Total per-bar) có:
//    BuyVolume (khớp ở ASK = mua chủ động ~ ATAS lvl.Ask)
//    SellVolume(khớp ở BID = bán chủ động ~ ATAS lvl.Bid)
//    Volume, Delta, DeltaFinish, Trades, BuyTrades, SellTrades,
//    MaxDelta / MinDelta      = delta chạy TRONG nến (intrabar) — CÓ THẬT, khác ghi chú cũ!
//    MaxOneTradeVolume        = lệnh ĐƠN lớn nhất — dùng cho Big Trade thật
//    AverageBuySize / AverageSellSize = cỡ lệnh trung bình
//  Truy cập: bar.VolumeAnalysisData.PriceLevels[price] và .Total.
//  Guard: HistoricalData.VolumeAnalysisCalculationProgress.State == Finished.
//
//  ---- ABSORPTION (Hấp thụ đỉnh/đáy) ĐÃ GỠ HOÀN TOÀN (2026-11-19): không còn tính, vẽ, niêm phong hay xác nhận giữ/vỡ mức.
//  Bản ghi niêm phong cũ có cờ Confirmable (bóng hấp thụ) bị bỏ khi nạp lại; dấu vân tay đã đổi nên bản ghi cũ cũng không được khôi phục.
//
//  ---- Ô BID/ASK LỚN (mục 1.5, xem CellBigLogic.cs) -------------
//  Luật mô phỏng hiển thị của CORVEN, fit lại 2026-11-19 trên chart M5 ngày 18/11, TẤT CẢ THEO TỪNG TICK (không gom hàng), bóng ở đúng giá khớp.
//  CHẤM ĐẶC NHỎ xét RIÊNG TỪNG BÊN: đỏ khi Bid >= 2,8 x trung vị volume mỗi ô (TB 20 nến trước), lớn hơn hẳn Bid của mọi tick trong ±4 tick, sàn 9; xanh tương tự với Ask; xanh bị che nếu có đỏ cùng nến cách <= 6 tick.
//  VÒNG TRÒN MỜ = BIG TRADE "lệnh cá mập": MỘT lệnh đơn chủ động lớn hơn hẳn nhóm 8 lệnh lớn nhất mỗi ngày, tính trên 5 ngày nến gần nhất
//  (BigTradeWhale trong CellBigLogic.cs; chỉ feed sống cấp lệnh đơn, lịch sử lấy từ nhật ký lệnh đơn). Cả hai chế độ ngưỡng dùng chung luật này.
//  Kiệt sức: râu >= 3 tick và tổng bên soi trên 6 tick từ cực trị <= 1,1 x volume trung bình mỗi ô của 20 nến trước (ExhaustionLogic.cs).
//  Trên 26 nến M5 mẫu: Dot 33 (10 xanh + 23 đỏ sau khi che), kiệt sức 13 (CORVEN: 16 cụm chấm, 11 kiệt sức; vòng mờ của CORVEN = lệnh đơn lớn, lịch sử không có số liệu nên không khớp được). Chỉ một biểu đồ nên chưa phải kiểm định.
//  Chi tiết + bản Python gốc: research/corven_m5_2026-11-18/. KHÔNG phải lợi thế đã kiểm định.
//
//  ---- NIÊM PHONG TÍN HIỆU (2026-09-15, xem SignalCache.cs) --------------------
//  Sự cố: Quantower gọi lại VolumeAnalysisData_Loaded() → ResetState() nhiều lần trong 1 phiên
//  (không chỉ 1 lần lúc mở indicator), mỗi lần xoá sạch _bubbles rồi tính lại TOÀN BỘ lịch sử bằng
//  dữ liệu VA hiện có — mà dữ liệu per-level của nến QUÁ KHỨ do feed cấp lại thường MỎNG hơn lúc
//  live (đã xác nhận: MaxOneTradeVolume luôn về 0 khi tải lại lịch sử) → bóng đã nổ có thể biến mất
//  dù giá/nến không đổi. Đã đo thật trên dữ liệu 2026-09-14: ngưỡng nổ bóng dao động 17-31 hợp đồng
//  trong 1 ngày (KHÔNG phải 1 số n cố định) — bản chất tương đối này ĐÚNG, giữ nguyên không sửa.
//  Sửa: mỗi nến ĐÃ ĐÓNG chỉ tính tín hiệu 1 LẦN TRONG ĐỜI, niêm phong (SignalCache) khoá theo
//  THỜI GIAN mở nến (không khoá theo idx — idx lệch giữa các lần nếu tải nhiều/ít lịch sử khác nhau),
//  lưu cả bộ nhớ lẫn file (%AppData%\OrderFlowBubbles\signal-cache\<symbol>_<khung>.jsonl — file này
//  cũng dùng luôn làm log để backtest). ResetState() sau đó KHÔI PHỤC lại nến đã niêm phong thay vì
//  tính lại. Confirm (kiệt sức bị quét) khi chốt xong sẽ ghi đè niêm phong (RePersistBar).
//
//  ---- HỆ MÃ HOÁ HÌNH ---------------------------------------------------------
//    • Big Trade/HVN   = TRÒN MỜ (halo). Feed KHÔNG cấp MaxOneTradeVolume (đã kiểm 0% trên
//                        6 tháng dxFeed) → tooltip ghi "HVN cell · vol/ô" cho đúng bản chất.
//    • Big Delta line  = GẠCH NGANG (rộng = nến), xanh(buy)/đỏ(sell).
//    • Nến delta lớn   = TÔ THÂN NẾN xanh(+delta)/đỏ(−delta).
//    • Số delta        = chữ dưới đáy nến, xanh/đỏ theo dấu.
//    • Kiệt sức = tam giác vàng chỉ xuống ở đỉnh / xanh chỉ lên ở đáy (nền mờ khi bị râu quét qua);
//    • Divergence/Sweep = tam giác;  Unfinished = ngoặc.
//    • Stacked Imbalance = VÙNG CHỮ NHẬT xanh lơ(buy)/hồng(sell) kéo sang phải (xem StackedImbalance.cs).
//  Vẽ tay bằng GDI+ trong OnPaintChart (Quantower không có PriceSelectionValue).
//  _bubbles/_barTint bị GHI ở thread tính (Process) và ĐỌC ở thread vẽ → mọi truy cập
//  trong lock(_sync); thread vẽ copy snapshot rồi vẽ ngoài lock.
// ============================================================================

using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using TradingPlatform.BusinessLayer;

namespace OrderFlowBubbles
{
    public class OrderFlowBubbles : Indicator, IVolumeAnalysisIndicator
    {
        // ===================== hình + bubble =====================
        private enum Shape { Ellipse, Triangle, Rectangle, Diamond, HLine, ExhTop, ExhBottom, Zone }   // thêm CUỐI để số cũ trong SignalCache không lệch

        private sealed class Bubble
        {
            public double Price;
            public Shape Shape;
            public Color Color;
            public int Size;            // px (Big Trade...) HOẶC độ dày (HLine)
            public int Transparency;    // 0..100 (0 = đặc)
            public bool Halo;           // true = viền + fill mờ (Big Trade)
            public bool UseBarWidth;    // true = đường kính/độ dài = bề rộng nến (Big Trade, chấm, HLine)
            public double SizeFrac;     // 0 = đầy đủ; (0,1] = tỉ lệ bề ngang nến khi UseBarWidth (Ô lớn to dần theo độ lớn)
            public string Tooltip;
            public int Confirm;         // kiệt sức: 0 = còn hiệu lực, -1 = đã bị râu nến sau quét qua
            public bool IsDivergence;   // true = thuộc luồng Divergence (TryDivergence dò lại bằng field này, KHÔNG dò tooltip)
            public double PriceHi;      // Shape.Zone: mép trên vùng (Price = mép dưới)
            public int ZoneSide;        // Shape.Zone: +1 buy / −1 sell
            public bool ZoneWeak;       // Shape.Zone: buy ở râu trên / sell ở râu dưới (bị rút râu)
            public bool CellBig;        // true = bóng Ô Bid/Ask lớn (Price = tâm bóng); stop hunt đọc đúng các bóng này
            public double CellBid, CellAsk;  // Ô lớn: Bid (sell chủ động) / Ask (buy chủ động) của hàng
            public int CellSide;        // Ô lớn: +1 xanh (Ask trội), -1 đỏ (Bid trội); 0 chỉ còn ở bản ghi niêm phong cũ (vàng, đã bỏ). KHÔNG đổi khi thành stop hunt
            public bool CellDot;        // true = bậc Dot (chấm nhỏ đặc); false = bậc Big (vòng mờ lớn). Chỉ có nghĩa khi CellBig
            public bool StopHunt;       // true = bóng thuộc nến quét của một stop hunt đã xác nhận -> vẽ màu tím (Color), tooltip "Stop hunt ..."
        }

        // vùng Stacked Imbalance đang theo dõi (kéo sang phải tới khi kết thúc)
        private sealed class ZoneRec
        {
            public int Idx;             // nến tạo vùng
            public Bubble B;
            public int EndIdx = -1;     // nến kết thúc (-1 = còn hiệu lực)
            public SiEnd End;
        }

        // key = chỉ số nến tuyệt đối (SeekOriginHistory.Begin, 0 = cũ nhất)
        private readonly Dictionary<int, List<Bubble>> _bubbles = new();
        private readonly Dictionary<int, int> _barTint = new();  // idx -> +1 (xanh) / -1 (đỏ)
        private readonly object _sync = new();       // bảo vệ _bubbles/_barTint (calc ghi, paint đọc)
        private readonly object _calcLock = new();   // serialize thread tính (OnUpdate vs VA_Loaded)

        // ===================== baseline ROBUST (median + MAD) =====================
        private StopHuntDetector _stopHunt;     // stop hunt CORVEN (chỉ nạp nến ĐÃ ĐÓNG, đúng 1 lần/nến)
        private BigTradeWhale _btWhale;         // Big Trade "lệnh cá mập": mọi lệnh đơn của 5 ngày nến có số liệu TRƯỚC (2026-11-25), cả hai chế độ
        private StatDots _statDots;             // chế độ "Không theo CORVEN (thống kê)": chấm (null khi chế độ tắt)
        private ExhRowBaseline _exhRowBase;     // kiệt sức theo HÀNG giá (2026-11-26): (volume TB mỗi hàng, tổng volume) của N nến đóng TRƯỚC
        private string _baseKey;                // N nến nền + phút một nến của Big Trade lúc dựng nền; đổi -> ResetState
        private CellBigBaseline _nqRowBase;     // NQ như CORVEN: trung vị volume mỗi HÀNG 8 tick, TB 20 nến đóng trước (chỉ mã NQ/MNQ)
        private CellBigBaseline _cellBigBase;   // mức nền Ô lớn + kiệt sức (volume TB mỗi ô, bên trội lớn nhất): TB 20 nến đóng TRƯỚC
        private RollingRobust _rLvlAbsDelta;  // per-level |Delta| — CHỈ nạp khi DLineEnabled (chỉ Big Delta line đọc nó)
        private bool _trackAbsDelta;          // DLineEnabled tại lúc InitBaselines (ResetState)
        private RollingRobust _rBarVol;       // per-bar Total.Volume
        private RollingRobust _rBarAbsDelta;  // per-bar |Total.Delta|

        private readonly List<double> _cvd = new();  // cumulative delta theo chỉ số tuyệt đối
        private int _processedClosedCount;
        private bool _vaLoaded;
        private int _lastDivPivot = int.MinValue;     // cooldown divergence

        private readonly List<ZoneRec> _zones = new();    // vùng Stacked Imbalance (của nến ĐÃ ĐÓNG), lock(_sync)
        private const int MaxZonesKept = 200000;          // ~ vài MB; đủ cho cả năm NQ M1
        private readonly List<ZoneRec> _activeZones = new();  // tập con của _zones còn hiệu lực (EndIdx < 0), cùng thứ tự — UpdateZones chỉ duyệt cái này (O(Z hoạt động) thay vì O(mọi vùng))

        // kiệt sức còn HIỆU LỰC (chưa bị râu nến sau quét qua) — xem ExhaustionLogic.cs
        private sealed class ExhRec { public int Idx; public long Tick; public bool Top; public Bubble B; }
        private readonly List<ExhRec> _exhRecs = new();

        // ===================== niêm phong tín hiệu (xem SignalCache.cs) =====================
        // Mỗi nến ĐÃ ĐÓNG chỉ tính tín hiệu 1 lần; kết quả khoá theo THỜI GIAN mở nến, sống sót
        // qua ResetState() (Quantower gọi lại khi nạp lại Volume Analysis — không chỉ 1 lần).
        private SignalCache _cache;
        private BigTradeLog _bigTradeLog;
        private string _settingsFingerprint = "";   // đổi khi người dùng đổi tham số -> vô hiệu cache cũ
        private bool _fingerprintValid;             // true = _settingsFingerprint đã tính cho bộ tham số hiện tại (đổi tham số luôn đi qua OnClear -> ResetState)

        // ================================================================
        //  INPUT PARAMETERS
        // ================================================================

        // ---------- Appearance ----------
        // 2026-11-26: bảng màu lấy theo chart Sierra của CORVEN (đo màu điểm ảnh trên khung hình Meet 07/11): chấm buy XANH DƯƠNG,
        // sell ĐỎ, nến delta xanh lá / đỏ. Cũ: Cyan / OrangeRed / xanh ngọc — cyan trên nền xám nhạt gần như không tương phản (khó nhìn).
        public Color BuyColor { get; set; } = Color.FromArgb(0x4A, 0x5A, 0xF5);

        public Color SellColor { get; set; } = Color.FromArgb(0xE0, 0x14, 0x0A);

        public Color DeltaUpColor { get; set; } = Color.FromArgb(0x1E, 0xA8, 0x3C);

        public Color DeltaDownColor { get; set; } = Color.FromArgb(0xE5, 0x39, 0x35);

        public int MinBubbleSize { get; set; } = 8;

        public int MaxBubbleSize { get; set; } = 26;

        public int SolidTransparency { get; set; } = 10;

        // ---------- Baseline (robust) ----------
        public int BaselineBars { get; set; } = 100;

        public int MinBars { get; set; } = 40;

        public double MinLevelVolFloor { get; set; } = 5;

        public double MinBarVolFloor { get; set; } = 20;

        // ---------- Ngưỡng CỐ ĐỊNH (thay cho tương đối) — dùng để soi mắt/thử nghiệm ----------
        // Đo thật trên ~29 ngày GC: ngưỡng tương đối (median+MAD) dao động 12-40 hợp đồng tuỳ giờ
        // (median chung ~20). Bật mục này để ép chấm Bid/Ask dùng THẲNG 1 số
        // hợp đồng cố định thay vì z-score — mất tính "portable" theo biến động/mã, chỉ nên dùng để
        // xem trực quan số lượng bóng nổ ra ở 1 mã/khung cụ thể, KHÔNG bật khi giao dịch thật.
        public bool UseFixedThreshold { get; set; } = false;

        // Đo thật trên 508 đỉnh + 500 đáy đảo chiều thật (29 ngày GC, 2026-09-15): trong khoảng
        // 10-15, điểm tách biệt "đảo chiều thật" vs "nến bất kỳ" cao nhất rơi vào 10 (bắt 24,1% đảo
        // chiều thật, nổ trên 12,0% nến bất kỳ) — xem chi tiết trong hội thoại/README nghiên cứu.
        public double FixedThresholdContracts { get; set; } = 10;

        // ---------- 1.5) Ô BID/ASK LỚN — BÓNG ĐẠI DIỆN CHÍNH (2026-09-15; luật theo TỪNG TICK 2026-11-19) ----------
        // Xem CellBigLogic.cs. Chấm nhỏ đặc xét RIÊNG TỪNG BÊN (vòng tròn mờ giờ là Big Trade, mục 2): chấm đỏ khi Bid >= CellDotMedianRatio x trung vị volume mỗi ô (TB 20 nến trước) và lớn hơn hẳn Bid của mọi tick trong ±CellDotLocalTicks tick; chấm xanh tương tự với Ask; chấm xanh bị che nếu có chấm đỏ cùng nến cách <= CellDotHideBuyNearSellTicks tick.
        // KHÔNG phải lợi thế đã kiểm định; không giới hạn số bóng/nến. Màu: xanh buy, đỏ sell; TÍM = bóng của nến quét trong một stop hunt.
        // ---------- CHẾ ĐỘ NGƯỠNG (2026-11-25, research/stat_anomaly_2026-11-24/SPEC.md; logic ở StatThreshold.cs) ----------
        // CHỈ điều khiển chấm Bid/Ask (từ 2026-11-25 Big Trade dùng chung một luật "lệnh cá mập" cho cả hai chế độ, xem BigTradeWhale).
        // 0 = Theo CORVEN (mọi luật cũ, mặc định). 1 = Không theo CORVEN (thống kê): chấm Bid/Ask nổ khi lớn hơn hẳn 98% (mức hiếm) các Bid/Ask
        // cùng khung giờ (giờ Chicago) của 5 ngày giao dịch trước.
        // Đây là ĐỊNH NGHĨA HIỂN THỊ "ô lớn bất thường", KHÔNG phải lợi thế giao dịch đã kiểm định. Chỉ chạy với nến thời gian có số phút nguyên >= 1;
        // khung khác chạy như "Theo CORVEN". Khi bật: sàn, bộ số, bộ Nasdaq, tự co dãn của chấm bị bỏ qua.
        [InputParameter("Chế độ ngưỡng chấm Bid/Ask", 22, variants: new object[] { "Theo CORVEN", 0, "Không theo CORVEN (thống kê)", 1 })]
        public int ThresholdMode { get; set; } = 0;

        // Mức hiếm của chấm, phần vạn (200 = 2%). Chỉ hiện khi chế độ "Không theo CORVEN" bật (xem Settings).
        [InputParameter("Độ dày chấm (chỉ theo mode \"Không theo CORVEN\")", 23, variants: new object[] { "Dày (2%)", 200, "Vừa (1%)", 100, "Thưa (0,5%)", 50 })]
        public int StatRarePbp { get; set; } = 200;

        public int StatDotDays { get; set; } = 5;               // số ngày giao dịch trước của cùng khung giờ
        public bool StatDotNeighbors { get; set; } = true;      // gộp thêm hai khung giờ liền kề
        public int StatDotMinDays { get; set; } = 2;            // khung giờ cần ít nhất số ngày này, chưa đủ -> dự phòng
        public int StatDotFallbackMinutes { get; set; } = 120;  // dự phòng: nến đóng trong số phút gần nhất

        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public bool CellBigEnabled { get; set; } = true;

        public int CellBigBaselineBars { get; set; } = 20;

        [InputParameter("Chấm Bid/Ask · Bật", 26)]
        public bool CellDotEnabled { get; set; } = true;

        public double CellDotMedianRatio { get; set; } = 2.8;

        public int CellDotLocalTicks { get; set; } = 4;

        // Bật = chấm Bid/Ask nổ ở MỌI mức giá vượt ngưỡng (bỏ điều kiện "lớn nhất trong ±CellDotLocalTicks tick"); tắt = như cũ.
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public bool CellDotAllLevels { get; set; } = false;

        // chấm xanh bị che (không vẽ) nếu cùng nến có chấm đỏ cách <= số tick này (CORVEN vẽ đỏ đè xanh); < 0 = tắt che
        public int CellDotHideBuyNearSellTicks { get; set; } = 6;

        // sàn tuyệt đối cho giá trị của bên đang xét (chấm nhỏ)
        // Bật (mặc định) = chấm chỉ nổ khi bên đang xét >= CellBigMinSide hợp đồng (ngoài điều kiện k x trung vị). Tắt = bỏ sàn, chỉ còn ngưỡng tương đối.
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public bool CellDotFloorEnabled { get; set; } = true;

        // Ô số chỉ hiện khi ô "Dùng sàn tối thiểu" bật (xem Settings bên dưới). Áp cho CẢ chế độ cũ lẫn "Tự co dãn theo khung"
        // (sửa 2026-11-24: bản trước để bộ số ghi đè sàn thành 5).
        // Đo 2026-11-24 (research/dot_floor_2026-11-24): sàn chỉ có tác dụng ở M1 (M5 trở lên k x trung vị đã cao hơn). GC M1 so CORVEN (885 chấm):
        // sàn 7 recall 0,675 / precision 0,87; sàn 9 0,60 / 0,90 (mất chủ yếu phiên Á); sàn 12 0,45 / 0,96; sàn 15 0,31 / 0,98 -> trên 9 sót nhiều.
        // Giữ 9 (người học thấy nhiễu); 7 = ít sót nhất mà gần như không tăng nhiễu theo F1 (Fable đề xuất).
        [InputParameter("Chấm Bid/Ask · Sàn tối thiểu (hợp đồng, 0 = không sàn; chỉ tác dụng ở M1 — 9 thưa, 7 ít sót)", 30, 0, 10000, 1, 0)]
        public double CellBigMinSide { get; set; } = 9;

        // 2026-11-24 (research/adaptive_2026-11-24): MỘT công thức chấm cho mọi mã, mọi khung — w = max(4, biên độ TB / 6),
        // ngưỡng = max(k x trung vị mỗi ô, sàn), nền lấy trên N nến theo khung (xem UnifiedDots / BaselineWindow trong CellBigLogic.cs).
        // Bật = thay bộ số cũ (2,8 / ±4 / che 6) và bộ Nasdaq. Tắt = như cũ.
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public bool CellDotAdaptive { get; set; } = true;

        // Bộ số khi tự co dãn: 0 Không sót (k 2,0 · sàn 5 · che 2), 1 Trung gian (2,4 · 5 · 2), 2 Ít nhiễu (2,8 · 9 · che max(6; 0,75 x w)).
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public int CellDotPreset { get; set; } = 0;

        // Nền (trung vị mỗi ô, biên độ, đuôi kiệt sức) lấy trên N = min(20, max(5, 120 phút / phút một nến)) nến: M1/M5 20, M15 8, M30/H1 5.
        // Tắt = 20 nến như cũ. Volume TB mỗi ô của luật kiệt sức cũ luôn 20 nến. Big Trade không phụ thuộc ô này.
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public bool AdaptiveBaseline { get; set; } = true;

        public double BaselineWindowMinutes { get; set; } = BaselineWindow.DefaultWindowMinutes;

        // màu bóng (chấm / Big Trade) thuộc nến quét của stop hunt đã xác nhận (thay cho tam giác cũ)
        public Color CellBigStopHuntColor { get; set; } = Color.MediumOrchid;

        // 0 = KHÔNG giới hạn số bóng/nến (CORVEN có nến 10+ bóng)
        public int CellBigTopN { get; set; } = 0;

        // Gộp ô liền kề trong cùng nến: giữ ô lớn nhất, bỏ ô cách nó <= số tick này. 0 = tắt gộp.
        public int CellBigMergeTicks { get; set; } = 0;

        // ---------- Nến delta lớn (dominant-delta candle) ----------
        [InputParameter("Nến delta · Bật (tô thân nến)", 20)]
        public bool DeltaBarEnabled { get; set; } = true;

        public double DeltaPctFloor { get; set; } = 0.30;

        public double DeltaBarSigZ { get; set; } = 3.0;

        public double DeltaBarVolGate { get; set; } = 0.8;

        public int DeltaBarTintPct { get; set; } = 85;

        // ---------- Số Delta ----------
        [InputParameter("Số Delta · Hiện dưới nến", 35)]
        public bool ShowDeltaNumbers { get; set; } = true;

        public int DeltaFontSize { get; set; } = 8;

        public int DeltaYOffsetPx { get; set; } = 8;

        public int DeltaMinBarWidthPx { get; set; } = 6;

        public bool DeltaBackground { get; set; } = false;

        // ---------- 2) Big Trade — MỘT LỆNH ĐƠN chủ động THẬT SỰ LỚN: "lệnh cá mập" (2026-11-25, research/bigtrade_whale_2026-11-25/SPEC.md) ----------
        //  Vòng tròn MỜ = một lệnh đơn rất lớn đánh vào một mức giá (VolumeAnalysisItem.MaxOneTradeVolume; lịch sử lấy từ nhật ký lệnh đơn).
        //  Luật (BigTradeWhale, CellBigLogic.cs): nổ khi lệnh đơn LỚN HƠN HẲN lệnh lớn thứ K của mọi lệnh đơn trong 5 ngày nến gần nhất
        //  (1380 phút nến có số liệu = một ngày nến), K = 8 lệnh mỗi ngày nến (đủ 5 ngày: K = 40). Chưa đủ một ngày nến có số liệu -> không vẽ vòng.
        //  Gộp vòng cách nhau <= max(2, biên độ TB / 8) tick, không giới hạn số vòng mỗi nến. Tham số là HẰNG SỐ, không có ô chỉnh dày / thưa,
        //  áp y hệt cho "Theo CORVEN" và "Không theo CORVEN". Đo trên nhật ký: ngưỡng vàng ~34–76 hợp đồng, NQ ~67–82.
        //  Đây là định nghĩa HIỂN THỊ lệnh lớn, KHÔNG phải lợi thế giao dịch đã kiểm định.
        [InputParameter("Big Trade (lệnh đơn) · Bật", 60)]
        public bool BigTradeEnabled { get; set; } = true;

        // Độ đậm của vòng Big Trade, phần trăm (35 = mờ ~35%). Chỉ ảnh hưởng cách vẽ.
        public int BigTradeOpacity { get; set; } = 35;

        // ---------- 3) Big Delta profile (gạch ngang) ----------
        [InputParameter("Big Delta line · Bật", 70)]
        public bool DLineEnabled { get; set; } = false;

        public double DLineFloor { get; set; } = 0.35;

        public double DLineZ { get; set; } = 4.0;

        public int DLineTopN { get; set; } = 1;

        // ---------- 4) Exhaustion — KIỆT SỨC thuần theo CORVEN (Meet 2026-11-07, xem ExhaustionLogic.cs) ----------
        //  Đỉnh soi ASK, đáy soi BID, chỉ lấy ở RÂU nến; "nhỏ, hoặc giảm dần về 0". Vô hiệu khi một nến
        //  sau đó chỉ cần RÂU quét qua mức đó (không cần đóng nến) → tô nền mờ (hoặc ẩn).
        //  Đã BỎ định nghĩa cũ (volume nến ≤ × nến trước, delta co khỏi đỉnh intrabar, lookback swing).
        //  Luật 2026-11-26 (ExhRowGrid, research/exh_2026-11-26): theo HÀNG giá như chart CORVEN (NQ 8 tick, GC 2 tick, mốc lẻ); 3 hàng sát cực trị đều <= 0,35 x
        //  volume TB mỗi hàng của 20 nến trước, volume nến >= 0,8 x TB, râu >= 2 hàng. 95 dấu CORVEN: trùng 82 / thừa 35 / sót 13 (luật cũ 64 / 209 / 31).
        //  ⚠️ Công cụ ĐÁNH DẤU để đọc chart, CHƯA kiểm định lợi thế.
        [InputParameter("Kiệt sức · Bật", 80)]
        public bool ExhaustionEnabled { get; set; } = true;

        // 2026-11-26: luật theo HÀNG giá như chart CORVEN (ExhRowGrid trong ExhaustionLogic.cs) — tham số là HẰNG SỐ, không có ô chỉnh.
        // Bỏ các ô cũ ExhMinWickTicks / ExhSumLevels / ExhSumHistRatio / ExhTailMedianRatio (luật theo từng tick).

        public int ExhSweepTicks { get; set; } = 1;

        public bool ExhHideInvalidated { get; set; } = false;

        // true = vẽ mờ dấu đã bị quét (kiểu cũ). Mặc định false như CORVEN (2026-11-26).
        public bool ExhDimInvalidated { get; set; } = false;

        // độ đậm (%) của tam giác kiệt sức ĐÃ HẾT HIỆU LỰC so với tam giác còn hiệu lực (tô đặc, chỉ mờ đi)
        public int ExhDeadOpacity { get; set; } = 35;

        public Color ExhTopColor { get; set; } = Color.FromArgb(0xE6, 0xB4, 0x1E);

        public Color ExhBottomColor { get; set; } = Color.FromArgb(0x3D, 0xB8, 0xFF);

        // ---------- 5) Stacked Imbalance — THUẦN, vẽ VÙNG như chart CORVEN (2026-11-08) ----------
        // Định nghĩa + lời giảng: xem StackedImbalance.cs. ĐÃ BỎ mọi cổng ngoài định nghĩa của bản cũ:
        // chờ đủ 40 nến thống kê ("ready"), ngưỡng volume TƯƠNG ĐỐI max(5, trung vị 3 ô đậm nhất 100 nến)
        // (đo: ngưỡng trung vị 8 hợp đồng, chỉ còn 17 vùng/phiên so với 141 của bản mới), và tắt mặc định. Chỉ giữ 1 sàn TUYỆT ĐỐI cho bên áp
        // đảo — đo trên GCZ26 M1 69 phiên (08-03 → 10-21): với sàn 1 hợp đồng, 92% vùng chứa ít nhất một
        // mức "x vs 0" và cứ 1,2 nến lại có 1 vùng (ngập chart); sàn 5 → 1 vùng / 7 nến giờ London, gần
        // mật độ đếm trên chart CORVEN (~1 / 9-13 nến). Đây là mật độ hiển thị, KHÔNG phải lợi thế đã kiểm định.
        [InputParameter("Stacked Imbalance · Bật", 90)]
        public bool ImbalanceEnabled { get; set; } = true;

        public int ImbalanceRatioPct { get; set; } = 250;

        public int ImbalanceRun { get; set; } = 3;

        public double ImbMinVolume { get; set; } = 5;

        // Bật (mặc định) = như Sierra của CORVEN: vùng dừng ở nến ĐẦU TIÊN chạm lại vùng (đo: 64% vùng bị chạm
        // ngay nến kế tiếp, trung vị 1 nến, 95% trong 42 nến). Tắt = giữ vùng qua các lần test, chỉ dừng khi
        // một nến ĐÓNG CỬA xuyên qua mép xa ("không giữ được giá, đâm thủng").
        public bool ImbEndOnTouch { get; set; } = true;

        // CORVEN (Meet 07/11, 0:06:54 "dùng gần thôi, đừng dùng xa"; 1:05:32 "xa tít thì không dùng"): vùng còn hiệu lực
        // mà đã kéo đủ N nến thì coi là HẾT HIỆU LỰC — dừng kéo ở nến thứ N (vẽ nhạt như vùng đã kết thúc). 0 = không giới hạn.
        // CORVEN không nêu con số; 20 nến là lựa chọn hiển thị (vùng bị chạm trung vị sau 1 nến, 95% trong 42 nến), chỉnh được.
        // 2026-11-26 rà Settings: ẨN khỏi bảng (giữ giá trị mặc định = bộ đã khớp CORVEN; người dùng không muốn chỉnh tay)
        public int ImbMaxBars { get; set; } = 20;

        // CORVEN: "dùng gần thôi, đừng dùng xa" → vùng còn hiệu lực nhưng đã quá N nến thì KHÔNG vẽ, không hover nữa.
        // 60 nến (~1 giờ M1) > 95% thời gian chờ bị chạm đo được (42 nến).
        public int ImbFarBars { get; set; } = 60;

        // 2026-11-26: màu + độ đậm tính ngược từ màu vùng trên chart CORVEN (xanh lơ ~#A0D8D8, hồng ~#E4C0C0 trên nền #D8D8D8).
        public Color ImbBuyZoneColor { get; set; } = Color.FromArgb(0x7A, 0xD8, 0xD8);

        public Color ImbSellZoneColor { get; set; } = Color.FromArgb(0xEF, 0xAD, 0xAD);

        public int ImbZoneOpacity { get; set; } = 60;

        // Bề dày TỐI THIỂU (px) khi vẽ vùng. Vùng 3–7 mức của NQ (tick 0,25, nến M1 dài 40–100 tick) chỉ còn 2–4 px = một vạch mảnh;
        // trên vàng của CORVEN (nến 10–25 tick) cùng số mức chiếm 1/4–1/2 thân nến nên trông to. Chỉ đổi CÁCH VẼ (giãn đều quanh tâm vùng),
        // giá thật của vùng vẫn hiện trong chữ rê chuột. 0 = vẽ đúng tỉ lệ giá (vẫn tối thiểu 3 px như cũ).
        public int ImbZoneMinPx { get; set; } = 10;

        // ---------- 6) Delta Divergence ----------
        [InputParameter("Divergence · Bật", 100)]
        public bool DivergenceEnabled { get; set; } = false;

        public int DivSwingLookback { get; set; } = 3;

        public double DivVolPartic { get; set; } = 1.5;

        public int DivCooldown { get; set; } = 3;

        // ---------- 7) Liquidity Sweep ----------
        [InputParameter("Sweep · Bật", 110)]
        public bool SweepEnabled { get; set; } = false;

        public int SweepLookback { get; set; } = 8;

        // ---------- 8) Unfinished Business ----------
        [InputParameter("Unfinished · Bật", 120)]
        public bool UnfinishedEnabled { get; set; } = false;

        // ---------- 9) Stop-hunt ----------
        // Stop hunt kiểu CORVEN (2026-11-12, logic ở StopHuntLogic.cs): quét cạnh range 20/60 nến + bóng Ô lớn + fail break.
        // DẤU ĐỂ ĐỌC CHART, không phải tín hiệu vào lệnh (chưa có lợi thế sau phí 1 tick).
        [InputParameter("Stop-hunt · Bật", 130)]
        public bool StopHuntEnabled { get; set; } = true;

        public int StopHuntBoxSmall { get; set; } = 60;      // hộp nhỏ (nến đóng trước); 2026-11-18: chỉ dùng hộp 60 (= hộp lớn thì bộ dò bỏ qua bản trùng)
        public int StopHuntBoxLarge { get; set; } = 60;      // hộp lớn
        public double StopHuntBoxMaxMult { get; set; } = 8;  // hộp hợp lệ khi cao <= k x trung vị biên độ 100 nến trước
        public int StopHuntTolTicks { get; set; } = 3;       // bóng phải có tâm >= mốc - tol x tick
        public int StopHuntConfirmBars { get; set; } = 2;    // fail break trong nến quét + N nến sau
        public int StopHuntCooldown { get; set; } = 5;       // nghỉ giữa 2 dấu cùng phía (nến)

        // ================================================================
        //  CTOR
        // ================================================================
        public OrderFlowBubbles() : base()
        {
            Name = "OrderFlow Bubbles";
            Description = "Footprint / order-flow signals (bubble). Ngưỡng tương đối (median+MAD) → portable mọi feed. Cần Volume Analysis.";
            SeparateWindow = false;
            InitBaselines();   // tránh null nếu OnUpdate chạy sớm
        }

        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            lock (_calcLock) { ResetState(); _vaLoaded = true; }   // khởi tạo baseline XONG mới bật cờ
            Process();
        }

        protected override void OnInit() { }

        protected override void OnClear()
        {
            lock (_calcLock) { _vaLoaded = false; ResetState(); _cache?.Flush(); }
        }

        public override void Dispose()
        {
            try { lock (_calcLock) { _cache?.Flush(); } } catch { }   // không để lỗi ghi file chặn việc tháo indicator
            base.Dispose();
        }

        // Người dùng ĐỔI THAM SỐ trên chart (vd bật "Ngưỡng · Dùng số CỐ ĐỊNH") -> đây là hành động
        // CHỦ Ý, khác hẳn feed nạp lại dữ liệu. Bắt tính lại từ đầu; dấu vân tay tham số mới sẽ tự
        // KHÔNG khớp các bản niêm phong cũ (tính bằng tham số cũ) nên chúng được tính lại, còn niêm
        // phong của phiên trước (nếu mở lại đúng tham số cũ) vẫn được giữ nguyên, không mất.
        //  ⚠️ FIX 2026-11-08 (bật/tắt ô trong Settings là MẤT HẾT bubble, phải refresh trang): đã dịch
        //  ngược TradingPlatform.BusinessLayer — base.OnSettingsUpdated() gọi Refresh() → wrapper chạy
        //  Clear() (→ OnClear: _vaLoaded=false) → Init() → Update(HistoricalBar)×N, nhưng KHÔNG gọi lại
        //  VolumeAnalysisData_Loaded() (chỉ gọi khi VA tính xong lần đầu). Bản cũ vì thế kẹt _vaLoaded=false
        //  vĩnh viễn → OnUpdate return sớm → trắng chart. Giờ OnUpdate tự "mở lại" khi VA đã Finished
        //  (ShouldArmVa). Bỏ luôn dòng đặt _processedClosedCount=0 ở đây: Clear() đã reset, còn đặt lại
        //  SONG SONG với lượt tính lại (chạy trên task khác) dễ làm baseline nạp trùng.
        // Ô "Sàn tối thiểu (hợp đồng)" chỉ hiện khi ô "Dùng sàn tối thiểu" đang bật.
        public override IList<SettingItem> Settings
        {
            get
            {
                var settings = base.Settings;
                // ô "Sàn tối thiểu" chỉ hiện ở chế độ "Theo CORVEN" (chế độ thống kê không dùng sàn)
                var floor = settings?.FirstOrDefault(x => x.Name == nameof(CellBigMinSide));
                if (floor != null) floor.Relation = new SettingItemRelationVisibility(nameof(ThresholdMode), new SelectItem("", 0));
                // ô "Mức hiếm" chỉ hiện khi chọn "Không theo CORVEN (thống kê)"
                var rare = settings?.FirstOrDefault(x => x.Name == nameof(StatRarePbp));
                if (rare != null) rare.Relation = new SettingItemRelationVisibility(nameof(ThresholdMode), new SelectItem("", 1));
                return settings;
            }
            set => base.Settings = value;
        }

        protected override void OnSettingsUpdated()
        {
            _fingerprintValid = false;   // tham số đổi -> tính lại dấu vân tay ở lượt Process kế tiếp
            base.OnSettingsUpdated();
        }

        /// <summary>Có cần "mở" lại cờ VA không: chưa mở, và Volume Analysis đã tính xong.</summary>
        internal static bool ShouldArmVa(bool vaLoaded, VolumeAnalysisCalculationState? state)
            => !vaLoaded && state == VolumeAnalysisCalculationState.Finished;

        private CellBigSettings CellSettings(double avgRangeTicks = 0)
        {
            var s = new CellBigSettings
            {
                DotEnabled = CellDotEnabled, DotMedianRatio = CellDotMedianRatio, DotLocalTicks = CellDotAllLevels ? 0 : CellDotLocalTicks, DotHideBuyNearSellTicks = CellDotHideBuyNearSellTicks,
                MinSide = CellDotFloorEnabled ? CellBigMinSide : 0, FixedMode = UseFixedThreshold, FixedThreshold = FixedThresholdContracts
            };
            if (CellDotAdaptive) UnifiedDots.Apply(s, CellDotPreset, avgRangeTicks, CellDotAllLevels, CellDotFloorEnabled, CellBigMinSide);
            else if (UseNasdaqPresetNow) SymbolPreset.ApplyNasdaq(s, avgRangeTicks);
            return s;
        }

        private string SymbolNameNow => TestBarSource != null ? TestSymbolName : Symbol?.Name;
        private (int g, int off) ExhGridNow => ExhRowGrid.For(SymbolNameNow);
        private string ExhKey() { var (g, off) = ExhGridNow; return ExhRowGrid.Key(g, off); }
        private bool IsNasdaqNow => SymbolPreset.IsNasdaq(TestBarSource != null ? TestSymbolName : Symbol?.Name);
        // 2026-11-26: NQ/MNQ như chart CORVEN (gom 8 tick một hàng) — TỰ BẬT khi chế độ đang chạy "Theo CORVEN" và mã là NQ/MNQ,
        // không có ô riêng (người dùng không muốn thêm ô phải chỉnh tay). Khi bật, thắng "Tự co dãn" và "Nổ ở mọi mức giá" cho NQ/MNQ.
        // Bộ Nasdaq theo từng tick cũ (SymbolPreset) không còn đường chạy.
        private bool NqRowModeNow => !StatModeNow && IsNasdaqNow;
        private bool UseNasdaqPresetNow => false;

        private string ComputeSettingsFingerprint()
        {
            // Chỉ cần liệt kê tham số ẢNH HƯỞNG TỚI QUYẾT ĐỊNH nổ bóng (không cần màu sắc/kích
            // thước hiển thị — đổi màu không cần tính lại). Thêm tham số nào ảnh hưởng quyết định
            // thì thêm vào đây.
            return string.Join("|",
                UseFixedThreshold, FixedThresholdContracts,
                CellBigEnabled, CellBigBaselineBars, CellBigMinSide, CellBigTopN, CellBigMergeTicks, CellDotEnabled, CellDotMedianRatio, CellDotLocalTicks, CellDotAllLevels, CellDotHideBuyNearSellTicks, "cellbig-v18",
                BaselineBars, MinBars, MinLevelVolFloor, MinBarVolFloor, "noabs-v1",
                DeltaBarEnabled, DeltaPctFloor, DeltaBarSigZ, DeltaBarVolGate,
                BigTradeEnabled, BigTradeWhaleKey(),
                DLineEnabled, DLineFloor, DLineZ, DLineTopN,
                ExhaustionEnabled, ExhKey(), ExhSweepTicks,
                ImbalanceEnabled, ImbalanceRatioPct, ImbalanceRun, ImbMinVolume,
                DivergenceEnabled, DivSwingLookback, DivVolPartic, DivCooldown,
                SweepEnabled, SweepLookback, UnfinishedEnabled,
                StopHuntEnabled, StopHuntBoxSmall, StopHuntBoxLarge, StopHuntBoxMaxMult, StopHuntTolTicks, StopHuntConfirmBars, StopHuntCooldown, "stophunt-v8")
                // chỉ thêm khi bộ Nasdaq đang chạy -> dấu vân tay của vàng GC giữ nguyên như cũ (bản niêm phong cũ vẫn dùng được)
                + (CellDotFloorEnabled ? "" : "|nofloor")   // chỉ thêm khi TẮT sàn -> dấu vân tay mặc định giữ nguyên
                + (UseNasdaqPresetNow ? $"|nq-v2:{SymbolPreset.NqDotMedianRatio}/{SymbolPreset.NqDotLocalTicks}/{SymbolPreset.NqRangePerWindowTick}/{SymbolPreset.NqDotHideBuyNearSellTicks}" : "")
                + (NqRowModeNow ? "|" + NqRows.Key : "")
                // 2026-11-24 thích nghi: mỗi phần chỉ thêm khi BẬT -> tắt hết thì dấu vân tay = bản cũ
                + (AdaptiveBaseline ? $"|nbase-v1:{DesiredBaseBars()}" : "")
                + (CellDotAdaptive ? $"|dotu-v2:{CellDotPreset}" : "")
                // 2026-11-25 chế độ "Không theo CORVEN (thống kê)": chỉ thêm khi BẬT -> tắt thì dấu vân tay y như cũ
                + (StatModeNow ? "|stat-v2:" + StatKey() : "");
        }

        // ---- chế độ "Không theo CORVEN (thống kê)" (StatThreshold.cs) ----
        // Phút một nến hợp lệ cho chế độ mới: số nguyên >= 1 (lệch dưới 1e-9); ngược lại 0 = chạy như "Theo CORVEN".
        private int StatMinutes()
        {
            double m = BarMinutesNow;
            if (!(m >= 1)) return 0;
            double r = Math.Floor(m + 0.5);
            return Math.Abs(m - r) < 1e-9 ? (int)r : 0;
        }
        private bool StatModeNow => ThresholdMode == 1 && StatMinutes() > 0;
        private string StatKey() => string.Join("/", new object[] { StatMinutes(), StatRarePbp, StatDotDays, StatDotNeighbors, StatDotMinDays, StatDotFallbackMinutes }
            .Select(x => Convert.ToString(x, System.Globalization.CultureInfo.InvariantCulture)));

        // Số nến nền theo khung (BaselineWindow). Tắt "Nền tự co theo khung" = CellBigBaselineBars (20) như cũ.
        private int DesiredBaseBars() => AdaptiveBaseline ? BaselineWindow.BarsFor(BarMinutesNow, BaselineWindowMinutes) : CellBigBaselineBars;
        private string BaseKey() => DesiredBaseBars() + "|bw:" + WhaleMinutesText()
            + (StatModeNow ? "|stat:" + StatKey() : "");
        // Big Trade "lệnh cá mập": phút một nến sau khi quy (<= 0 -> 1), in InvariantCulture; đổi khung -> dựng lại hàng đợi.
        private string WhaleMinutesText() => BigTradeWhale.NormMinutes(BarMinutesNow).ToString(System.Globalization.CultureInfo.InvariantCulture);
        private string BigTradeWhaleKey() => $"bigtrade-whale-v1:{BigTradeWhale.Days}/{BigTradeWhale.PerDay}/{BigTradeWhale.DayMinutes}/" + WhaleMinutesText();

        private void InitBaselines()
        {
            int nb = DesiredBaseBars();
            _baseKey = BaseKey();
            _cellBigBase = new CellBigBaseline(CellBigBaselineBars, nb);
            _nqRowBase = new CellBigBaseline(CellBigBaselineBars, CellBigBaselineBars);
            _btWhale = new BigTradeWhale(BarMinutesNow);   // mọi chế độ ngưỡng
            if (StatModeNow)
            {
                int sm = StatMinutes();
                _statDots = new StatDots(sm, StatRarePbp, StatDotDays, StatDotNeighbors, StatDotMinDays, StatDotFallbackMinutes);
            }
            else _statDots = null;
            _exhRowBase = new ExhRowBaseline(nb);
            _rLvlAbsDelta = new RollingRobust(BaselineBars);
            _trackAbsDelta = DLineEnabled;
            _rBarVol = new RollingRobust(BaselineBars);
            _rBarAbsDelta = new RollingRobust(BaselineBars);
        }

        private void ResetState()
        {
            lock (_sync) { _bubbles.Clear(); _barTint.Clear(); _zones.Clear(); _activeZones.Clear(); }
            _stopHunt = null;   // dựng lại với tham số hiện tại ở nến đóng kế tiếp
            _fingerprintValid = false;
            InitBaselines();
            _cvd.Clear();
            _processedClosedCount = 0;
            _lastDivPivot = int.MinValue;
                _exhRecs.Clear();
        }

        // ================================================================
        //  MAIN
        // ================================================================
        protected override void OnUpdate(UpdateArgs args)
        {
            var progress = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (progress == null || progress.State != VolumeAnalysisCalculationState.Finished) return;
            if (!_vaLoaded)
            {
                // Sau Refresh (đổi Settings) Quantower không gọi lại VolumeAnalysisData_Loaded → tự mở lại.
                lock (_calcLock) { if (ShouldArmVa(_vaLoaded, progress.State)) { ResetState(); _vaLoaded = true; } }
                if (!_vaLoaded) return;
            }
            Process();
        }

        private void Process()
        {
            lock (_calcLock)
            {
                if (_rBarVol == null) return;
                if (_baseKey != BaseKey()) ResetState();   // khung (số nến nền, phút một nến của Big Trade) hoặc chế độ đổi -> dựng lại nền, tính lại từ đầu
                double tick = TickSizeNow;
                if (tick <= 0) return;

                int total = BarCountNow;
                if (total == 0) return;

                if (DLineEnabled != _trackAbsDelta) ResetState();   // baseline |Delta| chỉ nạp khi DLine bật: đổi cờ mà không qua OnClear -> nạp lại từ đầu
                int closedCount = total - 1;               // trừ nến đang hình thành
                EnsureCvd(total);

                // (1) nến đóng chưa xử lý: tính tín hiệu (baseline TRƯỚC bar) rồi nạp baseline
                //     NIÊM PHONG: nến đã tính (khoá theo thời gian mở nến) thì KHÔI PHỤC lại,
                //     KHÔNG tính lại — dù ResetState() vừa chạy và dữ liệu VA của nến đó bây giờ
                //     có mỏng hơn lúc live cũng mặc kệ (xem SignalCache.cs).
                EnsureCache();
                try   // finally: ghi niêm phong 1 lần cho cả lượt (SignalCache.Put chỉ xếp hàng — xem SignalCache.Flush)
                {
                if (!_fingerprintValid) { _settingsFingerprint = ComputeSettingsFingerprint(); _fingerprintValid = true; }
                if (_processedClosedCount == 0) lock (_sync) { _zones.Clear(); _activeZones.Clear(); }   // tính lại từ đầu (đổi tham số)
                for (int i = _processedClosedCount; i < closedCount; i++)
                {
                    var bar = Bar(i);
                    if (bar == null) continue;
                    _cvd[i] = (i > 0 ? _cvd[i - 1] : 0.0) + BarDelta(bar);
                    bool ready = _rBarVol.BarCount >= MinBars;

                    long timeKey = bar.TimeLeft.Ticks;
                    // Chỉ khôi phục khi CÙNG dấu vân tay tham số — đổi tham số (vd bật ngưỡng cố
                    // định) là hành động CHỦ Ý của người dùng, phải tính lại; khác với feed nạp lại
                    // dữ liệu (tham số không đổi) — trường hợp đó mới cần niêm phong bất di bất dịch.
                    // FitsBar: bản ghi có bóng nằm ngoài biên độ nến = của nến khác → tính lại, ghi đè bản hỏng
                    if (_cache != null && _cache.TryGet(timeKey, out var cached) && cached.SettingsFingerprint == _settingsFingerprint
                        && SignalCache.FitsBar(cached, bar.High, bar.Low, 2 * tick))
                        RestoreFromCache(i, bar, cached);
                    else
                    {
                        ComputeBar(i, bar, tick, ready, isClosed: true);
                        PersistBar(i, bar, timeKey);
                    }

                    ApplyStopHunt(i, bar, tick);           // stop hunt CORVEN: dấu đặt ở nến fail break = nến vừa đóng (TRƯỚC AddToBaseline: B của nến i)
                    UpdateZones(i, bar);                   // vùng stacked imbalance của các nến TRƯỚC có kết thúc ở nến này?
                    RegisterZones(i);                      // rồi mới nhận vùng của chính nến này
                    AddToBaseline(bar);
                    UpdateExhaustionSweeps(i, bar, tick);  // kiệt sức của các nến trước bị râu quét qua chưa?
                }
                if (closedCount > _processedClosedCount) _processedClosedCount = closedCount;

                // (2) nến đang hình thành — tính lại mỗi tick (idempotent)
                int cur = total - 1;
                var curBar = Bar(cur);
                if (curBar != null)
                {
                    _cvd[cur] = (cur > 0 ? _cvd[cur - 1] : 0.0) + BarDelta(curBar);
                    bool ready = _rBarVol.BarCount >= MinBars;
                    ComputeBar(cur, curBar, tick, ready, isClosed: false);
                    // râu nến đang chạy đã quét qua thì KHÔNG rút lại được (high/low chỉ nới ra) → vô hiệu ngay
                    UpdateExhaustionSweeps(cur, curBar, tick);
                }
                }
                finally { _cache?.Flush(); }
            }
        }

        // ================================================================
        //  TÍNH TÍN HIỆU CHO 1 NẾN
        // ================================================================
        private void ComputeBar(int idx, HistoryItemBar bar, double tick, bool ready, bool isClosed)
        {
            var va = bar.VolumeAnalysisData;
            if (va == null || va.Total == null || va.PriceLevels == null || va.PriceLevels.Count == 0)
            {
                lock (_sync) { _bubbles.Remove(idx); _barTint.Remove(idx); }
                return;
            }

            var list = new List<Bubble>();
            int tintSign = 0;

            double barVol = va.Total.Volume;
            double barDelta = va.Total.Delta;
            double barMaxDelta = va.Total.MaxDelta;   // delta chạy trong nến (đỉnh)
            double barMinDelta = va.Total.MinDelta;   // (đáy)

            // ---- (4) NẾN DELTA LỚN ----
            if (DeltaBarEnabled && ready)
            {
                double deltaPct = barVol > 0 ? barDelta / barVol : 0;
                double sig = _rBarAbsDelta.ModZ(Math.Abs(barDelta));
                if (barVol >= MinBarVolFloor && barVol >= _rBarVol.Median * DeltaBarVolGate
                    && Math.Abs(deltaPct) >= DeltaPctFloor && sig >= DeltaBarSigZ)
                    tintSign = barDelta > 0 ? 1 : -1;
            }

            // gom mức giá theo chỉ số tick + cực trị
            var byTick = new Dictionary<long, (double price, VolumeAnalysisItem it)>();
            double maxPosDelta = 0, maxPosPrice = bar.High;
            double minNegDelta = 0, minNegPrice = bar.Low;
            foreach (var kv in va.PriceLevels)
            {
                long k = (long)Math.Round(kv.Key / tick);
                byTick[k] = (kv.Key, kv.Value);
                var it = kv.Value;
                if (it.Delta > maxPosDelta) { maxPosDelta = it.Delta; maxPosPrice = kv.Key; }
                if (it.Delta < minNegDelta) { minNegDelta = it.Delta; minNegPrice = kv.Key; }
            }

            long loIdx = (long)Math.Round(bar.Low / tick);
            long hiIdx = (long)Math.Round(bar.High / tick);

            var dLineCands = new List<(double price, double z, int sign, double buy, double sell)>();
            var bigTradeCands = new List<Bubble>();
            var btCells = new List<(long tick, double mot, double price, double buy, double sell)>();
            var cellBigCands = new List<(Bubble b, double magnitude, long lo, long hi)>();

            for (long k = loIdx; k <= hiIdx; k++)
            {
                if (!byTick.TryGetValue(k, out var lvl)) continue;
                double price = lvl.price;
                var it = lvl.it;
                double buy = it.BuyVolume, sell = it.SellVolume, vol = it.Volume;
                double dNet = buy - sell, sum = buy + sell;

                // 1.5) Ô BID/ASK LỚN: xét theo từng tick, sau vòng ô — xem khối "Ô lớn theo từng tick" bên dưới.

                // 2) BIG TRADE — gom lệnh đơn chủ động lớn nhất của từng mức giá; ngưỡng "lệnh cá mập" xét SAU vòng lặp. Vòng tròn MỜ, to dần theo cỡ lệnh.
                //    Phía của lệnh đơn KHÔNG có trong dữ liệu: màu lấy theo phía TRỘI của ô (Ask > Bid -> buy xanh, ngược lại sell đỏ).
                if (BigTradeEnabled)
                {
                    double mot = it.MaxOneTradeVolume;
                    if (mot > 0)
                    {
                        // Ghi log lệnh đơn thật (mọi giá trị quan sát được, KHÔNG chỉ ca đạt ngưỡng) để đo lại ngưỡng sau này.
                        // Chỉ ghi lúc nến ĐÃ ĐÓNG (isClosed): nến đang chạy có thể còn tăng tiếp.
                        if (isClosed && _bigTradeLog != null)
                            _bigTradeLog.TryAppend(bar.TimeLeft.Ticks, bar.TimeLeft, price, mot, buy, sell);
                        btCells.Add((k, mot, price, buy, sell));   // xét ngưỡng SAU vòng lặp (cần cả nến để gộp / giới hạn)
                    }
                }

                // 3) BIG DELTA line — ứng viên (giữ TOP-N sau vòng lặp)
                if (DLineEnabled && ready && vol >= MinLevelVolFloor)
                {
                    double dPct = vol > 0 ? dNet / vol : 0;
                    double z = _rLvlAbsDelta.ModZ(Math.Abs(dNet));
                    if (Math.Abs(dPct) >= DLineFloor && (z >= DLineZ || Math.Abs(dNet) >= 2 * _rLvlAbsDelta.Median))
                        dLineCands.Add((price, z, dNet > 0 ? 1 : -1, buy, sell));
                }

                // 8) UNFINISHED — đỉnh/đáy còn cả 2 phía (min-vol relative)
                if (UnfinishedEnabled)
                {
                    if (k == hiIdx && buy > MinLevelVolFloor && sell > MinLevelVolFloor)
                        list.Add(new Bubble { Price = bar.High, Shape = Shape.Rectangle, Color = SellColor, Size = MinBubbleSize, Transparency = SolidTransparency, Tooltip = $"Đấu giá chưa xong tại đỉnh: buy {buy:0} / sell {sell:0}" });
                    if (k == loIdx && buy > MinLevelVolFloor && sell > MinLevelVolFloor)
                        list.Add(new Bubble { Price = bar.Low, Shape = Shape.Rectangle, Color = BuyColor, Size = MinBubbleSize, Transparency = SolidTransparency, Tooltip = $"Đấu giá chưa xong tại đáy: buy {buy:0} / sell {sell:0}" });
                }
            }

            // 5) STACKED IMBALANCE — định nghĩa THUẦN (StackedImbalance.cs), vẽ VÙNG. Không cần "ready".
            bool nqRows = NqRowModeNow;
            List<CellLevel> nqRowLevels = null;
            if (nqRows)
            {
                var raw = new List<CellLevel>(byTick.Count);
                foreach (var kv in byTick) raw.Add(new CellLevel(kv.Key, kv.Value.it.BuyVolume, kv.Value.it.SellVolume, kv.Value.it.Volume, kv.Value.it.Trades));
                nqRowLevels = NqRows.Group(raw);
            }
            if (ImbalanceEnabled && nqRows && hiIdx > loIdx)
            {
                // NQ như CORVEN: hàng 8 tick; vùng từ giá đầu hàng thấp nhất tới giá đầu hàng cao nhất của chuỗi (như Sierra vẽ)
                long loRow = NqRows.RowOf(loIdx), hiRow = NqRows.RowOf(hiIdx);
                var (ra, rb) = NqRows.RowArrays(nqRowLevels, loRow, hiRow);
                foreach (var z in StackedImbalanceCalc.Detect(0, 1, ra, rb, ImbalanceRatioPct, ImbalanceRun, NqRows.ImbMinVolume))
                {
                    double zlo = Math.Round(NqRows.RowLowTick(loRow + z.LoIdx) * tick, 6), zhi = Math.Round(NqRows.RowLowTick(loRow + z.HiIdx) * tick, 6);
                    z.Lo = zlo; z.Hi = zhi;
                    StackedImbalanceCalc.Classify(z, bar.Open, bar.Close);
                    list.Add(new Bubble
                    {
                        Price = zlo, PriceHi = zhi, Shape = Shape.Zone, ZoneSide = z.Side, ZoneWeak = z.Weak,
                        Color = z.Side > 0 ? ImbBuyZoneColor : ImbSellZoneColor, Size = 0, Transparency = 0,
                        Tooltip = StackedImbalanceCalc.ZoneTooltip(z.Side, z.Levels)
                    });
                }
            }
            else if (ImbalanceEnabled && hiIdx > loIdx)
            {
                int n = (int)(hiIdx - loIdx + 1);
                var askArr = new double[n]; var bidArr = new double[n];
                for (long k = loIdx; k <= hiIdx; k++)
                    if (byTick.TryGetValue(k, out var lv)) { askArr[k - loIdx] = lv.it.BuyVolume; bidArr[k - loIdx] = lv.it.SellVolume; }
                foreach (var z in StackedImbalanceCalc.Detect(loIdx * tick, tick, askArr, bidArr, ImbalanceRatioPct, ImbalanceRun, ImbMinVolume))
                {
                    StackedImbalanceCalc.Classify(z, bar.Open, bar.Close);
                    string tip = StackedImbalanceCalc.ZoneTooltip(z.Side, z.Levels);
                    list.Add(new Bubble
                    {
                        Price = z.Lo, PriceHi = z.Hi, Shape = Shape.Zone, ZoneSide = z.Side, ZoneWeak = z.Weak,
                        Color = z.Side > 0 ? ImbBuyZoneColor : ImbSellZoneColor, Size = 0, Transparency = 0,
                        Tooltip = tip
                    });
                }
            }

            // ---- Ô LỚN THEO TỪNG TICK (mục 1.5, CellBigLogic.Evaluate): mức nền = TB 20 nến đóng TRƯỚC (nến hiện tại chưa nạp —
            //      AddToBaseline chạy SAU ComputeBar), cần >= 5 nến. Chỉ ra chấm Dot (vẽ trên cùng; đỏ vẽ sau xanh).
            if (CellBigEnabled)
            {
                double cellMedian = 0;
                bool hasCellB = _cellBigBase != null && _cellBigBase.TryGetMedian(out cellMedian);
                var cellLevels = new List<CellLevel>(byTick.Count);
                foreach (var kv in byTick)
                    cellLevels.Add(new CellLevel(kv.Key, kv.Value.it.BuyVolume, kv.Value.it.SellVolume, kv.Value.it.Volume, kv.Value.it.Trades));
                double avgRange = 0;
                if (_cellBigBase != null) _cellBigBase.TryGetRange(out avgRange);   // bộ NQ: cửa sổ nới theo biên độ nến (khung càng lớn càng rộng)
                var inv = System.Globalization.CultureInfo.InvariantCulture;
                bool statDots = _statDots != null;   // chỉ khác null khi chế độ thống kê bật (đổi chế độ / khung -> BaseKey đổi -> ResetState)
                List<CellMark> marks;
                string statTip = null;
                if (nqRows && !statDots)
                {
                    // NQ như CORVEN: chấm xét trên HÀNG 8 tick; mức nền = trung vị volume mỗi hàng, TB 20 nến đóng trước
                    double rowMed = 0; bool hasRowB = _nqRowBase != null && _nqRowBase.TryGetMedian(out rowMed);
                    marks = CellBigLogic.Evaluate(nqRowLevels, hasRowB, rowMed, NqRows.DotSettings(CellDotEnabled, CellDotFloorEnabled ? CellBigMinSide : 0));
                }
                else if (statDots)
                {
                    // "Không theo CORVEN (thống kê)": ngưỡng cùng khung giờ các ngày trước (hoặc dự phòng 120 phút), không sàn, không che
                    int sthr = -1; bool sfb = false;
                    marks = CellDotEnabled ? _statDots.Evaluate(bar.TimeLeft, cellLevels, CellDotAllLevels, out sthr, out sfb) : new List<CellMark>();
                    // "ngưỡng > 31 (2% lớn nhất cùng khung giờ, 5 ngày trước)" / "ngưỡng > 31 (2% lớn nhất 120 phút gần nhất, chưa đủ ngày)"
                    string pct = (StatRarePbp / 100.0).ToString("0.#", inv);
                    statTip = sfb
                        ? $"> {sthr} ({pct}% lớn nhất {StatDotFallbackMinutes} phút gần nhất, chưa đủ ngày)"
                        : $"> {sthr} ({pct}% lớn nhất cùng khung giờ, {StatDotDays} ngày trước)";
                }
                else
                    marks = CellBigLogic.Evaluate(cellLevels, hasCellB, cellMedian, CellSettings(avgRange));
                foreach (var m in marks)
                {
                    var col2 = m.Side > 0 ? BuyColor : SellColor;
                    string side = m.Side > 0 ? "Buy" : "Sell";
                    // Dot theo từng bên: "Sell - 53 Bid (Ask 39) | ngưỡng 31" / "Buy - 40 Ask (Bid 12) | ngưỡng 31" (k = 2,8 x trung vị mỗi ô, ít nhất sàn)
                    string thrTxt = statTip ?? m.Threshold.ToString("0.#", inv);
                    string tip2 = m.Side > 0
                        ? $"{side} - {m.Buy:0} Ask (Bid {m.Sell:0}) | ngưỡng {thrTxt}"
                        : $"{side} - {m.Sell:0} Bid (Ask {m.Buy:0}) | ngưỡng {thrTxt}";
                    bool rowMark = nqRows && !statDots;
                    double mPrice = rowMark ? NqRows.DotPrice(m.Tick, tick, bar.Low, bar.High) : m.Tick * tick;
                    var b2 = Solid(mPrice, Shape.Ellipse, col2, true, tip2);
                    b2.SizeFrac = m.SizeFrac;
                    b2.CellBig = true; b2.CellDot = true; b2.CellBid = m.Sell; b2.CellAsk = m.Buy; b2.CellSide = m.Side;
                    long mLo = rowMark ? NqRows.RowLowTick(m.Tick) : m.Tick, mHi = rowMark ? mLo + NqRows.RowTicks - 1 : m.Tick;
                    cellBigCands.Add((b2, m.Side > 0 ? m.Buy : m.Sell, mLo, mHi));
                }
            }

            // ---- BIG TRADE "lệnh cá mập" (2026-11-25, BigTradeWhale): một luật cho cả hai chế độ ngưỡng ----
            if (BigTradeEnabled)
            {
                // lịch sử không có lệnh đơn (luôn 0) -> lấy từ nhật ký lệnh đơn đã ghi lúc chạy sống (nếu có)
                if (btCells.Count == 0 && _bigTradeLog != null) btCells = _bigTradeLog.CellsOf(bar.TimeLeft.Ticks, tick);
                // lệnh đơn lớn hơn hẳn lệnh lớn thứ K của 5 ngày nến gần nhất; chưa đủ một ngày nến có số liệu -> không vẽ
                if (btCells.Count > 0 && _btWhale != null && _btWhale.TryThreshold(out int wthr))
                {
                    int g = _btWhale.MergeTicks();
                    var sel = BigTradeAdaptive.Select(btCells.Select(c => (c.tick, c.mot)).ToList(), wthr, g, 0, true);
                    sel.Sort((a, b) => btCells[a].tick.CompareTo(btCells[b].tick));   // thứ tự vẽ: tick tăng dần (như bản cũ)
                    var inv0 = System.Globalization.CultureInfo.InvariantCulture;
                    // "tính trên 5 ngày gần nhất"; hàng đợi chưa đầy thì số ngày nến đang có, một chữ số thập phân
                    string days = _btWhale.Count >= _btWhale.WindowBars
                        ? BigTradeWhale.Days.ToString(inv0)
                        : (_btWhale.Minutes / BigTradeWhale.DayMinutes).ToString("0.0", inv0);
                    foreach (int si in sel)
                    {
                        var c = btCells[si];
                        int dir = c.buy > c.sell ? 1 : -1;
                        bigTradeCands.Add(new Bubble
                        {
                            Price = c.price, Shape = Shape.Ellipse, Color = dir > 0 ? BuyColor : SellColor,
                            Size = MidSize(), Transparency = SolidTransparency, Halo = false, UseBarWidth = true,
                            SizeFrac = BigTradeLogic.SizeFrac(c.mot, Math.Max(1, wthr)),
                            Tooltip = $"Big trade: 1 lệnh {c.mot:0} hợp đồng (ngưỡng > {wthr}: nhóm {BigTradeWhale.PerDay} lệnh lớn nhất mỗi ngày, tính trên {days} ngày gần nhất) | ô {c.sell:0} Bid {c.buy:0} Ask",
                            CellBig = true, CellDot = false, CellBid = c.sell, CellAsk = c.buy, CellSide = dir
                        });
                    }
                }
            }

            // ---- chọn TOP-N + thứ tự vẽ ----
            // Big Trade (vòng mờ) add TRƯỚC CÙNG; chấm Bid/Ask add sau (khi vẽ, chấm luôn nằm trên cùng).
            list.AddRange(bigTradeCands);
            if (cellBigCands.Count > 0)
            {
                // gộp ô liền kề (mặc định TẮT), rồi áp TopN
                var cellMerged = new List<(Bubble b, double magnitude, long lo, long hi)>();
                var mergeIn = cellBigCands.Select(x => (x.lo, x.magnitude)).ToList();
                foreach (int mi in CellBigLogic.MergeAdjacent(mergeIn, CellBigMergeTicks)) cellMerged.Add(cellBigCands[mi]);
                IEnumerable<(Bubble b, double magnitude, long lo, long hi)> cellKeep = cellMerged.OrderByDescending(x => x.magnitude).ThenBy(x => x.lo);
                if (CellBigTopN > 0) cellKeep = cellKeep.Take(CellBigTopN);   // 0 = không giới hạn
                // thứ tự vẽ: chấm xanh trước, chấm đỏ sau (đỏ đè lên xanh như CORVEN); OrderBy ổn định nên thứ tự cũ giữ trong từng màu
                cellKeep = cellKeep.OrderBy(x => x.b.CellSide > 0 ? 0 : 1);
                foreach (var c in cellKeep)
                {
                    list.Add(c.b);
                }
            }

            // Big Delta line: giữ TOP-N theo z
            if (dLineCands.Count > 0)
                foreach (var c in dLineCands.OrderByDescending(x => x.z).Take(Math.Max(1, DLineTopN)))
                    list.Add(new Bubble
                    {
                        Price = c.price, Shape = Shape.HLine,
                        Color = c.sign > 0 ? DeltaUpColor : DeltaDownColor,
                        Size = 2 + (int)Math.Clamp(c.z - DLineZ, 0, 4), Transparency = SolidTransparency,
                        UseBarWidth = true,
                        Tooltip = $"Lệch delta mạnh tại mức này: buy {c.buy:0} / sell {c.sell:0}"
                    });

            // ---- detector theo NẾN ----
            if (ExhaustionEnabled) TryExhaustion(idx, bar, va, tick, list, isClosed);
            if (SweepEnabled) TrySweep(idx, bar, barDelta, list);
            if (DivergenceEnabled && isClosed) TryDivergence(idx);

            lock (_sync)
            {
                if (list.Count > 0) _bubbles[idx] = list; else _bubbles.Remove(idx);
                if (tintSign != 0) _barTint[idx] = tintSign; else _barTint.Remove(idx);
            }
        }

        // ================================================================
        //  BAR-LEVEL DETECTORS
        // ================================================================

        // KIỆT SỨC thuần theo CORVEN — logic nằm trong ExhaustionLogic.cs (test được, không cần nền tảng).
        private void TryExhaustion(int idx, HistoryItemBar bar, VolumeAnalysisData va, double tick, List<Bubble> list, bool isClosed)
        {
            var levels = new List<ExhLevel>(va.PriceLevels.Count);
            foreach (var kv in va.PriceLevels)   // Bid = SellVolume (khớp ở Bid), Ask = BuyVolume (khớp ở Ask)
                levels.Add(new ExhLevel((long)Math.Round(kv.Key / tick), kv.Value.SellVolume, kv.Value.BuyVolume, kv.Value.Volume));
            var (g, off) = ExhGridNow;
            double rowBase = 0, volBase = 0;
            bool hasBase = _exhRowBase != null && _exhRowBase.TryGet(out rowBase, out volBase);   // N nến đóng TRƯỚC
            long o = (long)Math.Round(bar.Open / tick), h = (long)Math.Round(bar.High / tick);
            long l = (long)Math.Round(bar.Low / tick), c = (long)Math.Round(bar.Close / tick);
            var (hitT, hitB) = ExhRowGrid.Detect(o, h, l, c, levels, g, off, hasBase, rowBase, volBase);
            foreach (bool top in new[] { true, false })
            {
                if (!(top ? hitT : hitB)) continue;
                var b = new Bubble
                {
                    Price = top ? bar.High : bar.Low, Shape = top ? Shape.ExhTop : Shape.ExhBottom,
                    Color = top ? ExhTopColor : ExhBottomColor, Size = MidSize(), Transparency = SolidTransparency,
                    UseBarWidth = true, Tooltip = top ? "Kiệt sức buy" : "Kiệt sức sell"
                };
                list.Add(b);
                if (isClosed) _exhRecs.Add(new ExhRec { Idx = idx, Tick = top ? h : l, Top = top, B = b });
            }
        }

        // Màu VẼ của bóng Ô lớn / Big Trade theo VAI (tím stop hunt, xanh dương buy, đỏ sell) với bảng màu HIỆN TẠI — bóng khôi phục từ
        // niêm phong cũ còn lưu màu cũ (Cyan / OrangeRed) vẫn vẽ đúng màu mới (2026-11-26). Bản ghi rất cũ CellSide = 0 giữ màu đã lưu.
        private Color CellColor(Bubble b) => b.StopHunt ? CellBigStopHuntColor : b.CellSide > 0 ? BuyColor : b.CellSide < 0 ? SellColor : b.Color;

        private string FmtPrice(double p)
        {
            try { if (Symbol != null) return Symbol.FormatPrice(p); } catch { }
            return p.ToString("0.####", System.Globalization.CultureInfo.InvariantCulture);
        }

        // Kiệt sức luôn hiện chữ NGẮN, kể cả bubble cũ trong SignalCache còn tooltip dài (2026-11-08).
        private static string ShortTip(Bubble b)
        {
            if (b.Shape != Shape.ExhTop && b.Shape != Shape.ExhBottom) return b.Tooltip;
            string t = b.Shape == Shape.ExhTop ? "Kiệt sức buy" : "Kiệt sức sell";
            return b.Confirm < 0 ? t + " · hết hiệu lực" : t;
        }

        // VÔ HIỆU kiệt sức (CORVEN 0:54): nến SAU chỉ cần RÂU quét qua mức là đủ, không cần đóng nến.
        private void UpdateExhaustionSweeps(int idx, HistoryItemBar bar, double tick)
        {
            if (_exhRecs.Count == 0 || bar == null) return;
            long h = (long)Math.Round(bar.High / tick), l = (long)Math.Round(bar.Low / tick);
            List<ExhRec> done = null;
            foreach (var r in _exhRecs)
            {
                if (r.Idx >= idx) continue;
                if (!ExhaustionLogic.IsSwept(r.Top, r.Tick, h, l, ExhSweepTicks)) continue;
                lock (_sync) { r.B.Confirm = -1; }
                r.B.Tooltip += " · hết hiệu lực";
                (done ??= new List<ExhRec>()).Add(r);
                RePersistBar(r.Idx);
            }
            if (done != null) foreach (var r in done) _exhRecs.Remove(r);
            if (_exhRecs.Count > 3000) _exhRecs.RemoveRange(0, _exhRecs.Count - 3000);
        }

        // Divergence neo vào nến PIVOT = idx-n. Idempotent + cooldown + volume participation.
        private void TryDivergence(int idx)
        {
            int n = DivSwingLookback;
            if (idx < 2 * n) return;
            int pivot = idx - n;
            var c = Bar(pivot);
            if (c == null) return;
            if (pivot - _lastDivPivot < DivCooldown) return;

            double medVol = _rBarVol.Median;
            var divs = new List<Bubble>();
            if (IsPivotHigh(pivot, n) && ParticOk(pivot, medVol))
            {
                int prevPivot = FindPrevPivotHigh(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.High > pc.High && _cvd[pivot] <= _cvd[prevPivot])   // giá HH, delta LH
                        divs.Add(new Bubble { Price = c.High, Shape = Shape.Triangle, Color = BuyColor, Size = MidSize(), Transparency = SolidTransparency, IsDivergence = true,
                            Tooltip = $"Giá đỉnh sau cao hơn ({c.High:0.0} > {pc.High:0.0}) nhưng delta cộng dồn lại thấp hơn ({_cvd[pivot]:0} ≤ {_cvd[prevPivot]:0}) — buy yếu dần" });
                }
            }
            if (IsPivotLow(pivot, n) && ParticOk(pivot, medVol))
            {
                int prevPivot = FindPrevPivotLow(pivot - 1, n);
                if (prevPivot >= 0)
                {
                    var pc = Bar(prevPivot);
                    if (pc != null && c.Low < pc.Low && _cvd[pivot] >= _cvd[prevPivot])     // giá LL, delta HL
                        divs.Add(new Bubble { Price = c.Low, Shape = Shape.Triangle, Color = SellColor, Size = MidSize(), Transparency = SolidTransparency, IsDivergence = true,
                            Tooltip = $"Giá đáy sau thấp hơn ({c.Low:0.0} < {pc.Low:0.0}) nhưng delta cộng dồn lại cao hơn ({_cvd[pivot]:0} ≥ {_cvd[prevPivot]:0}) — sell yếu dần" });
                }
            }

            if (divs.Count > 0) _lastDivPivot = pivot;

            lock (_sync)
            {
                if (_bubbles.TryGetValue(pivot, out var existing))
                {
                    existing.RemoveAll(b => b.IsDivergence);
                    existing.AddRange(divs);
                    if (existing.Count == 0) _bubbles.Remove(pivot);
                }
                else if (divs.Count > 0)
                {
                    _bubbles[pivot] = divs;
                }
            }
        }

        private bool ParticOk(int idx, double medVol)
        {
            var b = Bar(idx);
            double v = b?.VolumeAnalysisData?.Total?.Volume ?? 0;
            return medVol <= 0 || v >= DivVolPartic * medVol;
        }

        private void TrySweep(int idx, HistoryItemBar cur, double barDelta, List<Bubble> list)
        {
            if (idx < SweepLookback + 1) return;
            double hi = MaxHighPrior(idx, SweepLookback);
            double lo = MinLowPrior(idx, SweepLookback);
            if (cur.High > hi && cur.Close < hi && barDelta < 0)
                list.Add(new Bubble { Price = cur.High, Shape = Shape.Triangle, Color = BuyColor, Size = MidSize(), Transparency = SolidTransparency,
                    Tooltip = $"Quét đỉnh {SweepLookback} nến rồi bị đẩy lùi: vượt {hi:0.0} nhưng đóng lại {cur.Close:0.0}, delta {barDelta:0}" });
            if (cur.Low < lo && cur.Close > lo && barDelta > 0)
                list.Add(new Bubble { Price = cur.Low, Shape = Shape.Triangle, Color = SellColor, Size = MidSize(), Transparency = SolidTransparency,
                    Tooltip = $"Quét đáy {SweepLookback} nến rồi bị đẩy lùi: xuống dưới {lo:0.0} nhưng đóng lại {cur.Close:0.0}, delta +{barDelta:0}" });
        }

        // ================================================================
        //  RENDER
        // ================================================================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || !_vaLoaded) return;

            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;              // overlay ở chart CHÍNH; không vẽ lộn sang cửa sổ phụ (VSA/Ask-Bid/DMA)
            var conv = win.CoordinatesConverter;
            var gr = args.Graphics;
            var clip = win.ClientRectangle;
            double tick = Symbol?.TickSize ?? 0;
            if (tick <= 0) return;
            double barsW = CurrentChart.BarsWidth;

            DateTime leftTime = conv.GetTime(clip.Left);
            DateTime rightTime = conv.GetTime(clip.Right);
            int li = (int)conv.GetBarIndex(leftTime);
            int ri = (int)Math.Ceiling(conv.GetBarIndex(rightTime));

            var mouse = args.MousePosition;
            string hoverTip = null; int hoverX = 0, hoverY = 0; Color hoverCol = Color.White;
            string dotHoverTip = null; int dotHoverX = 0, dotHoverY = 0; Color dotHoverCol = Color.White;
            var dotDraw = new List<(Bubble b, float cx, float cy, int size)>();

            var prevClip = gr.ClipBounds;
            gr.SetClip(clip);
            try
            {
                using var deltaFont = new Font("Arial", DeltaFontSize, FontStyle.Regular);   // CORVEN: chữ thường, xanh dương / đỏ, không dấu +
                using var centerFmt = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
                int tintAlpha = (int)Math.Round(255 * Math.Clamp(DeltaBarTintPct, 0, 100) / 100.0);

                // --- vùng Stacked Imbalance: hình chữ nhật từ nến tạo vùng kéo sang phải (như Sierra CORVEN) ---
                var zoneHits = new List<(RectangleF r, string tip, Color c)>();
                if (ImbalanceEnabled)
                {
                    int last = HistoricalData.Count - 1;
                    var lastBar = Bar(last);
                    var mode = ImbEndOnTouch ? SiEndMode.Touch : SiEndMode.CloseThrough;
                    var snap = new List<(int idx, Bubble b, int endIdx, SiEnd end)>();
                    lock (_sync)
                    {
                        foreach (var z in _zones)
                            if (z.Idx <= ri && (z.EndIdx < 0 || z.EndIdx >= li)) snap.Add((z.Idx, z.B, z.EndIdx, z.End));
                        if (_bubbles.TryGetValue(last, out var lb))      // nến đang chạy: vùng tạm thời
                            foreach (var b in lb) if (b.Shape == Shape.Zone) snap.Add((last, b, -1, SiEnd.Active));
                    }
                    foreach (var (zIdx, b, endIdx0, end0) in snap)
                    {
                        var src = Bar(zIdx);
                        if (src == null) continue;
                        int endIdx = endIdx0; var end = end0;
                        // còn hiệu lực: nến ĐANG CHẠY đã chạm/xuyên chưa (xem trước, chốt khi nến đóng)
                        if (endIdx < 0 && zIdx < last && lastBar != null)
                        {
                            var e = StackedImbalanceCalc.CheckEnd(b.ZoneSide, b.Price, b.PriceHi, lastBar.High, lastBar.Low, lastBar.Close, mode);
                            if (e != SiEnd.Active) { endIdx = last; end = e; }
                        }
                        // đã kéo đủ ImbMaxBars nến mà nến đóng chưa chốt (nến đang chạy) -> cắt ở nến thứ N như UpdateZones
                        (endIdx, end) = StackedImbalanceCalc.CapLength(zIdx, endIdx, end, ImbMaxBars, last);
                        float x0 = (float)(conv.GetChartX(src.TimeLeft) + barsW / 2.0);
                        float x1;
                        if (endIdx >= 0)
                        {
                            var eb = Bar(endIdx);
                            if (eb == null) continue;
                            x1 = (float)(conv.GetChartX(eb.TimeLeft) + barsW / 2.0);
                        }
                        else   // còn hiệu lực: kéo tới nến đang chạy, KHÔNG kéo hết màn hình bên phải
                        {
                            var lbx = lastBar ?? src;
                            x1 = (float)(conv.GetChartX(lbx.TimeLeft) + barsW / 2.0);
                        }
                        if (x1 < clip.Left || x0 > clip.Right) continue;
                        float yTop = (float)conv.GetChartY(b.PriceHi + tick / 2.0);
                        float yBot = (float)conv.GetChartY(b.Price - tick / 2.0);
                        var (vTop, vH) = StackedImbalanceCalc.VisualSpan(yTop, yBot, Math.Max(3, ImbZoneMinPx));
                        var rect = new RectangleF(x0, vTop, Math.Max((float)barsW / 2f, x1 - x0), vH);

                        int age = (endIdx >= 0 ? endIdx : last) - zIdx;
                        bool far = StackedImbalanceCalc.IsFar(endIdx, ImbFarBars, age);
                        if (far) continue;            // "đừng dùng xa" → không vẽ, không hover
                        double op = Math.Clamp(ImbZoneOpacity, 0, 100) / 100.0;
                        if (b.ZoneWeak) op *= 0.5;    // bị rút râu → nhạt
                        var col = b.ZoneSide > 0 ? ImbBuyZoneColor : ImbSellZoneColor;
                        using (var zb = new SolidBrush(Color.FromArgb((int)Math.Round(255 * op), col)))
                            gr.FillRectangle(zb, rect);   // CORVEN: khối màu phẳng, không viền

                        zoneHits.Add((rect, b.Tooltip + " · " + FmtPrice(b.Price) + " – " + FmtPrice(b.PriceHi), col));
                    }
                }

                double guardTick = TickSizeNow;
                for (int i = li; i <= ri; i++)
                {
                    if (i < 0 || i >= HistoricalData.Count) continue;
                    if (HistoricalData[i, SeekOriginHistory.Begin] is not HistoryItemBar bar) continue;

                    float cx = (float)(conv.GetChartX(bar.TimeLeft) + barsW / 2.0);

                    // snapshot trong lock
                    List<Bubble> bubbles = null; int tint = 0;
                    lock (_sync)
                    {
                        if (_bubbles.TryGetValue(i, out var l)) bubbles = new List<Bubble>(l);
                        _barTint.TryGetValue(i, out tint);
                    }

                    // --- tô thân nến delta (nền, vẽ trước) ---
                    if (DeltaBarEnabled && tint != 0)
                    {
                        float yTop = (float)conv.GetChartY(Math.Max(bar.Open, bar.Close));
                        float yBot = (float)conv.GetChartY(Math.Min(bar.Open, bar.Close));
                        float h = Math.Max(1f, yBot - yTop);
                        float w = (float)Math.Max(1.0, barsW - 1);
                        using var tb = new SolidBrush(Color.FromArgb(tintAlpha, tint > 0 ? DeltaUpColor : DeltaDownColor));
                        gr.FillRectangle(tb, cx - w / 2f, yTop, w, h);
                    }

                    // --- bubbles ---
                    if (bubbles != null)
                    {
                        foreach (var b in bubbles)
                        {
                            if (b.Shape == Shape.Zone) continue;   // vùng stacked imbalance đã vẽ ở trên
                            if (!BubbleFitsBar(b.Price, bar.High, bar.Low, guardTick)) continue;   // chặn bóng lạc ngoài biên độ nến (± 2 tick)
                            float y = (float)conv.GetChartY(b.Price);
                            // UseBarWidth = luôn ĐÚNG BẰNG bề ngang nến, KHÔNG có sàn tối thiểu — trước
                            // đây có sàn 14 px để bóng không biến mất khi zoom bé, nhưng hệ quả
                            // là bóng RỘNG HƠN thân nến lúc zoom bé (đè sang nến bên cạnh). Người dùng
                            // xác nhận ưu tiên "không bao giờ che rộng hơn thân nến" hơn "luôn nhìn thấy
                            // rõ khi zoom bé" (2026-09-15).
                            int drawSize = b.CellBig ? CellDrawSize(b.CellDot, b.SizeFrac, (float)barsW)
                                         : b.UseBarWidth ? Math.Max(1, (int)Math.Round(barsW * (b.SizeFrac > 0 ? b.SizeFrac : 1.0))) : b.Size;
                            if (b.CellBig && b.CellDot)
                            {
                                // chấm Dot vẽ SAU CÙNG (trên mọi vòng mờ, kể cả của nến bên cạnh) và được ưu tiên khi rê chuột
                                dotDraw.Add((b, cx, y, drawSize));
                                // chấm vẽ sau nằm trên (đỏ sau xanh) nên chấm cuối cùng nằm dưới con trỏ được ưu tiên
                                {
                                    float ddx = mouse.X - cx, ddy = mouse.Y - y;
                                    float dr = Math.Max(drawSize / 2f, 6f);
                                    if (ddx * ddx + ddy * ddy <= dr * dr) { dotHoverTip = ShortTip(b); dotHoverX = (int)cx; dotHoverY = (int)y; dotHoverCol = CellColor(b); }
                                }
                                continue;
                            }
                            DrawShape(gr, b, cx, y, drawSize, (float)barsW);

                            if (hoverTip == null)
                            {
                                float dx = mouse.X - cx, dy = mouse.Y - y;
                                float r = Math.Max(drawSize / 2f, 6f);
                                if (dx * dx + dy * dy <= r * r)
                                {
                                    hoverTip = ShortTip(b); hoverX = (int)cx; hoverY = (int)y;
                                    hoverCol = b.Shape == Shape.ExhTop ? ExhTopColor : b.Shape == Shape.ExhBottom ? ExhBottomColor : b.CellBig ? CellColor(b) : b.Color;
                                }
                            }
                        }
                    }

                    // --- số delta ---
                    if (ShowDeltaNumbers && barsW >= DeltaMinBarWidthPx && bar.VolumeAnalysisData?.Total != null)
                    {
                        double d = bar.VolumeAnalysisData.Total.Delta;
                        string text = d.ToString("0;-0;0");
                        float y = (float)conv.GetChartY(bar.Low) + DeltaYOffsetPx + DeltaFontSize / 2f;
                        if (y <= clip.Bottom)
                        {
                            if (DeltaBackground)
                            {
                                var sz = gr.MeasureString(text, deltaFont);
                                using var bg = new SolidBrush(Color.FromArgb(120, 0, 0, 0));
                                gr.FillRectangle(bg, cx - sz.Width / 2 - 1, y - sz.Height / 2, sz.Width + 2, sz.Height);
                            }
                            using var db = new SolidBrush(d > 0 ? BuyColor : d < 0 ? SellColor : Color.Gray);
                            gr.DrawString(text, deltaFont, db, cx, y, centerFmt);
                        }
                    }
                }

                foreach (var dd in dotDraw) DrawShape(gr, dd.b, dd.cx, dd.cy, dd.size, (float)barsW);
                if (dotHoverTip != null) { hoverTip = dotHoverTip; hoverX = dotHoverX; hoverY = dotHoverY; hoverCol = dotHoverCol; }

                if (hoverTip == null)   // bóng được ưu tiên; không trúng bóng thì xét vùng (vùng vẽ sau = trên cùng)
                    for (int zi = zoneHits.Count - 1; zi >= 0; zi--)
                        if (zoneHits[zi].r.Contains(mouse.X, mouse.Y)) { hoverTip = zoneHits[zi].tip; hoverCol = zoneHits[zi].c; hoverX = mouse.X; hoverY = mouse.Y; break; }

                if (hoverTip != null)
                {
                    // Nền ĐẶC (không trong suốt) + viền màu tín hiệu → đọc rõ trên mọi nền chart (2026-11-08).
                    using var tipFont = new Font("Arial", 10, FontStyle.Bold);
                    var sz = gr.MeasureString(hoverTip, tipFont);
                    float w = sz.Width + 12, h = sz.Height + 6;
                    float bx = hoverX + 12, by = hoverY - h - 4;
                    if (bx + w > clip.Right) bx = Math.Max(clip.Left, hoverX - 12 - w);
                    if (by < clip.Top) by = hoverY + 12;
                    using (var bg = new SolidBrush(Color.FromArgb(255, 24, 26, 32)))
                        gr.FillRectangle(bg, bx, by, w, h);
                    using (var strip = new SolidBrush(Color.FromArgb(255, hoverCol)))
                        gr.FillRectangle(strip, bx, by, 4, h);
                    using (var bp = new Pen(Color.FromArgb(255, hoverCol), 1.5f))
                        gr.DrawRectangle(bp, bx, by, w, h);
                    gr.DrawString(hoverTip, tipFont, Brushes.White, bx + 8, by + 3);
                }
            }
            finally { gr.SetClip(prevClip); }
        }

        // Chốt chặn lúc vẽ: bóng có giá ngoài [thấp nhất - 2 tick, cao nhất + 2 tick] của nến là bóng của nến khác (cache cũ/lệch) -> không vẽ.
        internal static bool BubbleFitsBar(double price, double high, double low, double tick)
            => tick <= 0 || (price >= low - 2 * tick && price <= high + 2 * tick);

        // Cỡ (px) của bóng: Big Trade = SizeFrac x bề ngang nến (1,0..2,5), sàn 8 px, trần 80 px; Dot = 45% bề ngang nến kẹp [5, 10] px.
        internal static int CellDrawSize(bool isDot, double sizeFrac, float barsW)
        {
            if (isDot) return Math.Clamp((int)Math.Round(barsW * CellBigLogic.DotSizeFrac), 5, 10);
            double f = sizeFrac > 0 ? sizeFrac : 1.0;
            return Math.Clamp((int)Math.Round(barsW * f), 8, 80);
        }

        private void DrawShape(Graphics gr, Bubble b, float cx, float cy, int size, float barsW)
        {
            int alpha = (int)Math.Round(255 * (100 - b.Transparency) / 100.0);
            alpha = Math.Clamp(alpha, 0, 255);

            if (b.Shape == Shape.HLine)
            {
                float len = Math.Max(6f, barsW - 1);
                using var pen = new Pen(Color.FromArgb(alpha, b.Color), Math.Max(2, b.Size));
                gr.DrawLine(pen, cx - len / 2f, cy, cx + len / 2f, cy);
                return;
            }

            // KIỆT SỨC (kiểu chart CORVEN): đỉnh = tam giác VÀNG mũi chỉ XUỐNG, cạnh đáy nằm ở giá cao nhất;
            // đáy = tam giác XANH mũi chỉ LÊN, cạnh nằm ở giá thấp nhất. Bị râu quét qua → tô nền mờ (hoặc ẩn).
            if (b.Shape == Shape.ExhTop || b.Shape == Shape.ExhBottom)
            {
                // 2026-11-26: CORVEN vẽ dấu đã bị quét GIỐNG HỆT dấu còn hiệu lực -> không làm mờ nữa (chữ rê chuột vẫn ghi "hết hiệu lực")
                bool dead = b.Confirm < 0 && ExhDimInvalidated;
                if (b.Confirm < 0 && ExhHideInvalidated) return;
                var col = b.Shape == Shape.ExhTop ? ExhTopColor : ExhBottomColor;   // màu HIỆN TẠI (đổi màu có hiệu lực ngay)
                float half = Math.Max(1, size) / 2f, th = Math.Max(1, size) * 0.85f;
                float dir = b.Shape == Shape.ExhTop ? 1f : -1f;
                var pts = new[] { new PointF(cx - half, cy), new PointF(cx + half, cy), new PointF(cx, cy + dir * th) };
                if (!dead)
                {
                    using var fb = new SolidBrush(Color.FromArgb(alpha, col));
                    gr.FillPolygon(fb, pts);
                    using var op = new Pen(Color.FromArgb(Math.Min(alpha, 160), Color.Black), 1f);
                    gr.DrawPolygon(op, pts);
                }
                else
                {
                    // hết hiệu lực: vẫn TÔ ĐẶC nhưng nền mờ (người học 2026-11-18: viền rỗng khó nhìn)
                    int fa = Math.Clamp(alpha * ExhDeadOpacity / 100, 25, 255);
                    using var fb = new SolidBrush(Color.FromArgb(fa, col));
                    gr.FillPolygon(fb, pts);
                    using var dp = new Pen(Color.FromArgb(Math.Min(255, fa + 40), col), 1f);
                    gr.DrawPolygon(dp, pts);
                }
                return;
            }

            // Big Trade = vòng tròn MỜ (độ đậm BigTradeOpacity) + viền mảnh đậm hơn một chút; Dot = chấm nhỏ ĐẶC
            if (b.CellBig)
            {
                float cr = size / 2f;
                var cc = CellColor(b);
                if (b.CellDot)
                {
                    using var db = new SolidBrush(Color.FromArgb(255, cc));
                    gr.FillEllipse(db, cx - cr, cy - cr, size, size);
                }
                else
                {
                    int fa = Math.Clamp((int)Math.Round(255 * BigTradeOpacity / 100.0), 10, 255);
                    using var cb = new SolidBrush(Color.FromArgb(fa, cc));
                    gr.FillEllipse(cb, cx - cr, cy - cr, size, size);
                    using var cpn = new Pen(Color.FromArgb(Math.Min(255, fa + 70), cc), 1f);
                    gr.DrawEllipse(cpn, cx - cr, cy - cr, size, size);
                }
                return;
            }

            var fillColor = Color.FromArgb(b.Halo ? Math.Min(alpha, 110) : alpha, b.Color);
            float r = size / 2f;
            using var fill = new SolidBrush(fillColor);
            switch (b.Shape)
            {
                case Shape.Ellipse: gr.FillEllipse(fill, cx - r, cy - r, size, size); break;
                case Shape.Rectangle: gr.FillRectangle(fill, cx - r, cy - r, size, size); break;
                case Shape.Triangle:
                    gr.FillPolygon(fill, new[] { new PointF(cx, cy - r), new PointF(cx - r, cy + r), new PointF(cx + r, cy + r) });
                    break;
                case Shape.Diamond:
                    gr.FillPolygon(fill, new[] { new PointF(cx, cy - r), new PointF(cx + r, cy), new PointF(cx, cy + r), new PointF(cx - r, cy) });
                    break;
            }

            if (b.Halo)
            {
                using var pen = new Pen(Color.FromArgb(alpha, b.Color), 2f);
                if (b.Shape == Shape.Ellipse) gr.DrawEllipse(pen, cx - r, cy - r, size, size);
                else if (b.Shape == Shape.Rectangle) gr.DrawRectangle(pen, cx - r, cy - r, size, size);
            }

        }

        // ================================================================
        //  HELPERS
        // ================================================================
        private const string StopHuntTipTop = "Stop hunt đỉnh", StopHuntTipBot = "Stop hunt đáy";

        // Stop hunt CORVEN: nạp nến i (ĐÃ ĐÓNG) vào bộ dò; nếu có fail break thì gắn dấu vào nến i. Chạy cho cả nến tính mới lẫn nến khôi phục
        // từ niêm phong (bộ dò cần đủ lịch sử); dấu cũ trong niêm phong được thay bằng kết quả tính lại (tất định) và ghi đè niêm phong nếu khác.
        private void ApplyStopHunt(int idx, HistoryItemBar bar, double tick)
        {
            if (!StopHuntEnabled || !(CellBigEnabled || BigTradeEnabled)) return;
            _stopHunt ??= new StopHuntDetector(new StopHuntSettings
            {
                BoxSmall = StopHuntBoxSmall, BoxLarge = StopHuntBoxLarge, BoxMaxMult = StopHuntBoxMaxMult,
                TolTicks = StopHuntTolTicks, ConfirmBars = StopHuntConfirmBars, Cooldown = StopHuntCooldown,
                BarMinutes = ChartBarMinutes(bar)
            }, tick);

            // Bóng đưa vào bộ dò = ĐÚNG các bóng (chấm hoặc Big Trade) đang hiển thị/niêm phong của nến (qua TopN, MergeTicks),
            // cho cả nến tính mới lẫn nến khôi phục từ niêm phong — không dựng lại từ dữ liệu từng mức giá (có thể mỏng hơn lúc nạp lại).
            var cells = new List<ShCell>();
            lock (_sync)
            {
                if (_bubbles.TryGetValue(idx, out var shown))
                    foreach (var b in shown)
                        if (b.CellBig) cells.Add(new ShCell { Centre = b.Price, Bid = b.CellBid, Ask = b.CellAsk, Side = b.CellSide });
            }

            var sigs = _stopHunt.OnBarClosed(idx, bar.High, bar.Low, bar.Close, StopHuntDetector.ToMinutes(bar.TimeLeft.Ticks), cells);
            if (sigs.Count == 0) return;
            // Stop hunt xác nhận (fail break ở nến idx) -> tô TÍM các bóng Ô lớn của NẾN QUÉT (sweepIdx <= idx) nằm ở/vượt mốc bị quét
            // (đúng các bóng đã đủ điều kiện quét: tâm >= mốc - tol x tick, phía đáy lật dấu). CellSide/CellBid/CellAsk giữ nguyên bên gốc.
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            var touched = new HashSet<int>();
            lock (_sync)
            {
                foreach (var sg in sigs)
                {
                    if (!_bubbles.TryGetValue(sg.SweepIdx, out var list)) continue;
                    double sgn = sg.Top ? 1.0 : -1.0;
                    foreach (var b in list)
                    {
                        if (!b.CellBig || b.StopHunt) continue;
                        if (!(sgn * b.Price >= sgn * sg.Level - StopHuntTolTicks * tick - StopHuntDetector.Eps)) continue;
                        b.StopHunt = true;
                        b.Color = CellBigStopHuntColor;
                        b.Tooltip = (sg.Top ? StopHuntTipTop : StopHuntTipBot) + " - quét " + sg.Level.ToString("0.0", inv)
                                  + " | " + b.CellBid.ToString("0", inv) + " Bid " + b.CellAsk.ToString("0", inv) + " Ask → fail break";
                        touched.Add(sg.SweepIdx);
                    }
                }
            }
            foreach (int k in touched) RePersistBar(k);   // ghi đè niêm phong của nến quét để nạp lại vẫn tím
        }

        // Chu kỳ nến (phút) cho kiểm tra liên tục của hộp. Khung thời gian: lấy từ HistoricalData; không rõ: bộ dò ước từ khoảng cách nhỏ nhất
        // giữa hai nến liền nhau đã thấy (chưa có -> 1 phút). Dưới 1 phút / không phải khung thời gian: trả 0 = để bộ dò tự ước.
        private double ChartBarMinutes(HistoryItemBar bar)
        {
            if (HistoricalData?.Aggregation is HistoryAggregationTime at)
            {
                double m = at.Period.BasePeriod switch
                {
                    BasePeriod.Second => at.Period.PeriodMultiplier / 60.0,
                    BasePeriod.Minute => at.Period.PeriodMultiplier,
                    BasePeriod.Hour => at.Period.PeriodMultiplier * 60.0,
                    BasePeriod.Day => at.Period.PeriodMultiplier * 1440.0,
                    _ => 0
                };
                return m >= 1 ? m : 0;
            }
            return 0;   // không rõ -> bộ dò tự ước từ khoảng cách nến
        }

        private Bubble Solid(double price, Shape shape, Color color, bool useBarWidth, string tip)
            => new Bubble { Price = price, Shape = shape, Color = color, Size = MidSize(), Transparency = SolidTransparency, Halo = false, UseBarWidth = useBarWidth, Tooltip = tip };

        // ---- khe TEST (perf/Golden): cho phép chạy lõi tính toán THẬT ngoài Quantower. Khi TestBarSource == null
        //      (luôn luôn trong Quantower) mọi hàm dưới đây trả ĐÚNG như code cũ (HistoricalData.Count / Symbol.TickSize). ----
        internal Func<int, HistoryItemBar> TestBarSource;
        internal int TestBarCount;
        internal double TestTickSize;
        internal string TestCacheFile;
        internal string TestSymbolName;   // null = như vàng GC (golden không đổi)
        internal double TestBarMinutes;   // phút một nến trong khe test (0 = không rõ -> nền 20 nến, như M1)
        internal string TestBigTradeLogFile;   // nhật ký lệnh đơn đọc vào khe test (null = không có)
        private double BarMinutesNow => TestBarSource != null ? TestBarMinutes : ChartBarMinutes(null);
        private int BarCountNow => TestBarSource != null ? TestBarCount : HistoricalData.Count;
        private double TickSizeNow => TestBarSource != null ? TestTickSize : (Symbol?.TickSize ?? 0);

        private HistoryItemBar Bar(int absIdx)
        {
            if (TestBarSource != null) return (absIdx >= 0 && absIdx < TestBarCount) ? TestBarSource(absIdx) : null;
            return (absIdx >= 0 && absIdx < HistoricalData.Count)
                ? HistoricalData[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;
        }

        private static double BarDelta(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total?.Delta ?? 0.0;
        private static double PrevVol(HistoryItemBar bar) => bar.VolumeAnalysisData?.Total?.Volume ?? 0.0;

        private int MidSize() => (MinBubbleSize + MaxBubbleSize) / 2;

        private static bool TryLevel(VolumeAnalysisData va, double price, double tick, out VolumeAnalysisItem it)
        {
            it = null;
            if (va?.PriceLevels == null) return false;
            long want = (long)Math.Round(price / tick);
            foreach (var kv in va.PriceLevels)
                if ((long)Math.Round(kv.Key / tick) == want) { it = kv.Value; return true; }
            return false;
        }

        private void AddToBaseline(HistoryItemBar bar)
        {
            var va = bar.VolumeAnalysisData;
            if (va?.PriceLevels == null) return;

            // perf 2026-11-11: dựng mảng thẳng (không List/LINQ). _rLvlSideVol (max buy/sell) đã BỎ — không nơi nào đọc.
            var levels = va.PriceLevels;
            double[] ads = _trackAbsDelta ? new double[levels.Count] : null;
            if (ads != null)
            {
                int li = 0;
                foreach (var it in levels.Values) ads[li++] = Math.Abs(it.Delta);
            }
            // mức nền chấm + kiệt sức: volume TB mỗi ô giá có giao dịch của nến ĐÃ ĐÓNG (gọi đúng 1 lần/nến đóng)
            double tickSz = TickSizeNow;
            if (tickSz > 0)
            {
                var cbLevels = va.PriceLevels.Select(kv => new CellLevel((long)Math.Round(kv.Key / tickSz), kv.Value.BuyVolume, kv.Value.SellVolume, kv.Value.Volume, kv.Value.Trades)).ToList();
                if (_nqRowBase != null && IsNasdaqNow && CellBigLogic.BarStats(NqRows.Group(cbLevels), out double rmean, out double rmedian))
                    _nqRowBase.Add(rmean, rmedian, 0);
                if (CellBigLogic.BarStats(cbLevels, out double bmean, out double bmedian))
                {
                    _cellBigBase.Add(bmean, bmedian, CellBigLogic.BarRangeTicks(cbLevels));
                    _statDots?.AddClosedBar(bar.TimeLeft, cbLevels);   // chế độ thống kê: nộp Bid/Ask của nến vào (ngày, khung giờ), dự phòng, biên độ
                }
                // nền kiệt sức theo hàng: mọi nến đóng có giao dịch nộp (volume TB mỗi hàng, tổng volume) — kể cả high = low
                if (_exhRowBase != null)
                {
                    var exLv = new List<ExhLevel>(cbLevels.Count);
                    foreach (var c in cbLevels) exLv.Add(new ExhLevel(c.Tick, c.Sell, c.Buy, c.Vol));
                    var (g, off) = ExhGridNow;
                    if (ExhRowGrid.BarStats(exLv, g, off, out double erm, out double etot)) _exhRowBase.Add(erm, etot);
                }
                // Big Trade "lệnh cá mập": nộp MỌI lệnh đơn > 0 của nến (từ feed, hoặc nhật ký nếu lịch sử không có); nến không có số liệu -> không nộp
                if (_btWhale != null)
                {
                    var bt = new List<(long tick, double mot)>();
                    foreach (var kv in va.PriceLevels)
                        if (kv.Value.MaxOneTradeVolume > 0) bt.Add(((long)Math.Round(kv.Key / tickSz), kv.Value.MaxOneTradeVolume));
                    if (bt.Count == 0 && _bigTradeLog != null)
                        foreach (var c in _bigTradeLog.CellsOf(bar.TimeLeft.Ticks, tickSz)) bt.Add((c.tick, c.mot));
                    _btWhale.AddClosedBar(bt);
                }
            }
            if (ads != null) _rLvlAbsDelta.AddBar(ads);
            _rBarVol.AddBar(new[] { va.Total.Volume });
            _rBarAbsDelta.AddBar(new[] { Math.Abs(va.Total.Delta) });
        }

        // ---- vùng Stacked Imbalance: nhận vùng của nến ĐÃ ĐÓNG (tính mới hoặc khôi phục từ niêm phong) ----
        private void RegisterZones(int idx)
        {
            lock (_sync)
            {
                // _zones được thêm theo Idx không giảm -> chỉ khi phần tử cuối có Idx >= idx mới có thể trùng (hiếm: tính lại cùng idx)
                if (_zones.Count > 0 && _zones[_zones.Count - 1].Idx >= idx)
                {
                    _zones.RemoveAll(z => z.Idx == idx);
                    _activeZones.RemoveAll(z => z.Idx == idx);
                }
                if (_bubbles.TryGetValue(idx, out var l))
                    foreach (var b in l)
                        if (b.Shape == Shape.Zone) { var zr = new ZoneRec { Idx = idx, B = b }; _zones.Add(zr); _activeZones.Add(zr); }
                // giữ bộ nhớ gọn: chỉ khi RẤT nhiều mới bỏ vùng đã kết thúc cũ nhất. Lỗi cũ (sửa 2026-11-26): ngưỡng 4000 vùng / 5000 nến
                // làm NQ hàng 8 tick (~4300 vùng mỗi 25 nghìn nến M1) xoá sạch vùng quá 5000 nến (~3,5 ngày) → lúc tính thấy vùng hiện rồi biến mất.
                if (_zones.Count > MaxZonesKept) _zones.RemoveRange(0, _zones.Count - MaxZonesKept + MaxZonesKept / 10);
            }
        }

        // Nến idx vừa đóng: vùng nào (của nến TRƯỚC) dừng kéo dài ở nến này. OHLC không đổi khi Quantower
        // nạp lại → tính lại luôn ra cùng kết quả, không cần niêm phong trạng thái kết thúc.
        private void UpdateZones(int idx, HistoryItemBar bar)
        {
            var mode = ImbEndOnTouch ? SiEndMode.Touch : SiEndMode.CloseThrough;
            lock (_sync)
            {
                int w = 0;
                for (int zi = 0; zi < _activeZones.Count; zi++)
                {
                    var z = _activeZones[zi];
                    if (z.Idx < idx)
                    {
                        var e = StackedImbalanceCalc.CheckEnd(z.B.ZoneSide, z.B.Price, z.B.PriceHi, bar.High, bar.Low, bar.Close, mode);
                        if (e == SiEnd.Active && ImbMaxBars > 0 && idx - z.Idx >= ImbMaxBars) e = SiEnd.Expired;
                        if (e != SiEnd.Active) { z.EndIdx = idx; z.End = e; continue; }   // kết thúc -> rời danh sách hoạt động
                    }
                    _activeZones[w++] = z;
                }
                if (w < _activeZones.Count) _activeZones.RemoveRange(w, _activeZones.Count - w);
            }
        }

        // ================================================================
        //  NIÊM PHONG TÍN HIỆU (xem SignalCache.cs) — sống sót qua ResetState()
        // ================================================================
        private void EnsureCache()
        {
            if (_cache != null) return;
            if (TestCacheFile != null)   // khe test: file cache chỉ định, không đụng %AppData% của người dùng
            {
                _cache = new SignalCache(TestCacheFile); _cache.Load(); _bigTradeLog = new BigTradeLog(TestBigTradeLogFile); _bigTradeLog.Load();
                return;
            }
            string symName = Symbol?.Name ?? "unknown";
            var agg = HistoricalData?.Aggregation;
            string aggName = agg?.Name ?? "unknown";
            // ⚠️ tên file PHẢI có khung (xem SignalCache.CacheName): bản cũ M1/M15/H1 dùng chung 1 file
            var at = agg as HistoryAggregationTime;
            string tf = at != null ? $"{at.Period.PeriodMultiplier}{at.Period.BasePeriod}" : (agg?.ToString() ?? "unknown");
            bool isM1 = at != null && at.Period.BasePeriod == BasePeriod.Minute && at.Period.PeriodMultiplier == 1;
            string safe = SignalCache.CacheName(symName, aggName, tf);
            try
            {
                string dir = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "OrderFlowBubbles", "signal-cache");
                string path = Path.Combine(dir, safe + ".jsonl");
                bool fresh = !File.Exists(path);
                _cache = new SignalCache(path);
                _cache.Load(compact: true);
                // lần đầu chạy bản mới trên M1: giữ niêm phong cũ CHẮC CHẮN của M1 (phút lẻ), phần còn lại tính lại
                if (fresh && isM1)
                    _cache.ImportLegacy(Path.Combine(dir, SignalCache.LegacyCacheName(symName, aggName) + ".jsonl"),
                                        SignalCache.IsSafeLegacyM1);
            }
            catch
            {
                _cache = new SignalCache(null);   // lỗi ghi file (vd không có quyền) -> chạy tiếp KHÔNG niêm phong,
            }                                      // không được để crash cả indicator vì một tính năng phụ

            try
            {
                string dir = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                    "OrderFlowBubbles", "bigtrade-log");
                _bigTradeLog = new BigTradeLog(Path.Combine(dir, safe + ".csv"));
                _bigTradeLog.Load();
            }
            catch
            {
                _bigTradeLog = new BigTradeLog(null);   // tương tự trên: lỗi ghi file không được crash indicator
            }
        }

        private CachedBarData ToCachedBarData(long timeTicks, List<Bubble> list, int tint)
        {
            var d = new CachedBarData { TimeTicks = timeTicks, Tint = tint, SettingsFingerprint = _settingsFingerprint };
            if (list != null)
                foreach (var b in list)
                    d.Bubbles.Add(new CachedBubbleData
                    {
                        Price = b.Price, Shape = (int)b.Shape, ColorArgb = b.Color.ToArgb(), Size = b.Size,
                        Transparency = b.Transparency, Halo = b.Halo, UseBarWidth = b.UseBarWidth, SizeFrac = b.SizeFrac,
                        Tooltip = b.Tooltip, Confirm = b.Confirm,
                        PriceHi = b.PriceHi, ZoneSide = b.ZoneSide, ZoneWeak = b.ZoneWeak,
                        CellBig = b.CellBig, CellDot = b.CellDot, CellBid = b.CellBid, CellAsk = b.CellAsk, CellSide = b.CellSide, StopHunt = b.StopHunt
                    });
            return d;
        }

        private static List<Bubble> FromCachedBarData(CachedBarData d)
        {
            var list = new List<Bubble>();
            foreach (var cb in d.Bubbles)
            {
                if (cb.Confirmable) continue;   // bản ghi niêm phong cũ: bóng Hấp thụ đã gỡ khỏi indicator -> bỏ, không vẽ
                list.Add(new Bubble
                {
                    Price = cb.Price, Shape = (Shape)cb.Shape, Color = Color.FromArgb(cb.ColorArgb), Size = cb.Size,
                    Transparency = cb.Transparency, Halo = cb.Halo, UseBarWidth = cb.UseBarWidth, SizeFrac = cb.SizeFrac,
                    Tooltip = cb.Tooltip, Confirm = cb.Confirm,
                    PriceHi = cb.PriceHi, ZoneSide = cb.ZoneSide, ZoneWeak = cb.ZoneWeak,
                    CellBig = cb.CellBig, CellDot = cb.CellDot, CellBid = cb.CellBid, CellAsk = cb.CellAsk, CellSide = cb.CellSide, StopHunt = cb.StopHunt
                });
            }
            return list;
        }

        // Nến ĐÃ NIÊM PHONG ở lần chạy trước -> khôi phục nguyên trạng, KHÔNG tính lại tín hiệu.
        private void RestoreFromCache(int idx, HistoryItemBar bar, CachedBarData cached)
        {
            var list = FromCachedBarData(cached);
            int tint = cached.Tint;
            lock (_sync)
            {
                if (list.Count > 0) _bubbles[idx] = list; else _bubbles.Remove(idx);
                if (tint != 0) _barTint[idx] = tint; else _barTint.Remove(idx);
            }
            // kiệt sức còn hiệu lực từ phiên trước -> tiếp tục theo dõi bị râu quét qua chưa
            double tk = TickSizeNow;
            if (tk > 0)
                foreach (var b in list)
                    if ((b.Shape == Shape.ExhTop || b.Shape == Shape.ExhBottom) && b.Confirm == 0)
                        _exhRecs.Add(new ExhRec { Idx = idx, Tick = (long)Math.Round(b.Price / tk), Top = b.Shape == Shape.ExhTop, B = b });
        }

        // Nến vừa tính XONG lần đầu -> niêm phong (lưu bộ nhớ + ghi file).
        private void PersistBar(int idx, HistoryItemBar bar, long timeKey)
        {
            if (_cache == null) return;
            List<Bubble> list; int tint;
            lock (_sync) { _bubbles.TryGetValue(idx, out list); _barTint.TryGetValue(idx, out tint); }
            _cache.Put(ToCachedBarData(timeKey, list, tint));
        }

        // Confirm của 1 nến đã niêm phong vừa chốt (giữ/vỡ mức) -> ghi đè niêm phong.
        private void RePersistBar(int idx)
        {
            if (_cache == null) return;
            var bar = Bar(idx);
            if (bar == null) return;
            PersistBar(idx, bar, bar.TimeLeft.Ticks);
        }

        private void EnsureCvd(int total) { while (_cvd.Count < total) _cvd.Add(0.0); }

        // ----- swing helpers (causal, chỉ số tuyệt đối) -----
        private double MaxHighPrior(int idx, int n)
        {
            double m = double.MinValue;
            for (int i = 1; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Max(m, b.High); }
            return m;
        }
        private double MinLowPrior(int idx, int n)
        {
            double m = double.MaxValue;
            for (int i = 1; i <= n && idx - i >= 0; i++) { var b = Bar(idx - i); if (b != null) m = Math.Min(m, b.Low); }
            return m;
        }

        private bool IsPivotHigh(int idx, int n)
        {
            var c = Bar(idx);
            if (c == null || idx - n < 0 || idx + n >= BarCountNow) return false;
            for (int i = 1; i <= n; i++)
            {
                var l = Bar(idx - i); var r = Bar(idx + i);
                if (l == null || r == null || l.High > c.High || r.High > c.High) return false;
            }
            return true;
        }
        private bool IsPivotLow(int idx, int n)
        {
            var c = Bar(idx);
            if (c == null || idx - n < 0 || idx + n >= BarCountNow) return false;
            for (int i = 1; i <= n; i++)
            {
                var l = Bar(idx - i); var r = Bar(idx + i);
                if (l == null || r == null || l.Low < c.Low || r.Low < c.Low) return false;
            }
            return true;
        }
        private int FindPrevPivotHigh(int fromIdx, int n)
        {
            for (int b = fromIdx; b - n >= 0; b--) if (IsPivotHigh(b, n)) return b;
            return -1;
        }
        private int FindPrevPivotLow(int fromIdx, int n)
        {
            for (int b = fromIdx; b - n >= 0; b--) if (IsPivotLow(b, n)) return b;
            return -1;
        }
    }
}
