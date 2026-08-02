// ============================================================================
//  RunnerSignal  —  Tín hiệu RUNNER CBR (Consolidation→Break→Retest→Resume) M1 (QUANTOWER)
// ============================================================================
//  Mô hình LITERAL của user rút từ 6 setup thật: "phá VÙNG CO, chờ HỒI (giữ trên
//  gốc phá), VÀO nến TIẾP DIỄN". TP 3R (giữ runner). KHÁC con scalp EntrySignal
//  (phá vùng→retest, 1.5R) — đây là chiến lược riêng, chạy song song, DLL riêng.
//
//  Neo = RANGE nội bộ (RangeLen nến trước, span trong [RangeMin..RangeMax] = vùng
//  co hẹp thật, KHÔNG phải zone profile). BREAK = nến đóng vượt cạnh range + VSA
//  climax(≥2.0) + thân mạnh. HOLD = trong WaitBars nến giá hồi nhưng GIỮ (không đóng
//  lại hẳn trong range). RESUME = nến đóng vượt cực trị nhịp hồi → vào tại close.
//  SL = cực trị nhịp hồi ± buf (sàn 3đ, trần 7đ). Chỉ bắn NẾN ĐÃ ĐÓNG (không repaint).
//
//  Logic KHỚP research/entry_cbr.py + optimize_loop.py (backtest thanh khoản 5-7/2026,
//  dxFeed GCQ26). Vùng hợp lưu (co_vung) và TP-vướng-vùng CHỈ là info hiển thị.
//  Build: build-runner.sh (concat ProfileEngine).
//
//  === NÂNG CẤP 2026-07-28 (đối chiếu live CSV 221 lệnh + 9 tháng data + 4 setup đảo chiều) ===
//  Phát hiện: nhánh cũ QUAY ĐẦU LỖ (-6R, WR23%, gate climax/VSA/co_vung VÔ NGHĨA); CBR
//  thắng theo XU HƯỚNG, thua NGƯỢC (thg6 crash -550 → LONG -19R). Bốn cải tiến ĐO ĐƯỢC:
//   1) LỌC THUẬN XU HƯỚNG (proxy TPO bias, close vs close ~8h): thg6 -16R→+5R, net +18→+35R,
//      MỌI THÁNG DƯƠNG. EMA30/120 quá nhanh → dùng lookback chậm.
//   2) RETRACE 60-90% (nâng sàn hồi): WR 30→33% (hồi sâu = runner thật).
//   3) VÀO ĐÚNG PHÍA VWAP + LỌC THANH KHOẢN (vma ≥ 0.75× TB dài): WR 33→37%, giữ net.
//   4) QUAY ĐẦU XÂY LẠI quanh VWAP (4 setup user đều neo VWAP): bỏ gate vô nghĩa, chỉ giữ
//      VWAP + rút râu + đóng mạnh + VSA≥1.8 + THUẬN trend; TP 1.5R (đảo chiều trần ~1.3R,
//      KHÔNG phải 3R). Kết quả: WR 23→56%, -6R→+10R. Absorption footprint = bonus grade LIVE.
//  Portfolio (CBR@3R + Quay đầu@1.5R): WR ~39%, +48R/3 tháng, cả 3 tháng dương.
// ============================================================================
namespace RunnerSignal
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Text;
    using TradingPlatform.BusinessLayer;
    using TpoSuite;   // ProfileEngine + PanelDrag (concat)

    public class RunnerSignal : Indicator, IVolumeAnalysisIndicator
    {
        // ---------- giờ phiên (để dựng vùng hiển thị hợp lưu) ----------
        [InputParameter("Lệch giờ (bar.TimeLeft UTC → local)", 10, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 7;
        [InputParameter("Á bắt đầu (phút/ngày)", 11, 0, 1439, 5, 0)]
        public int AsiaStart { get; set; } = 300;
        [InputParameter("Âu bắt đầu (phút/ngày)", 12, 0, 1439, 5, 0)]
        public int EuropeStart { get; set; } = 750;
        [InputParameter("Mỹ bắt đầu (phút/ngày)", 13, 0, 1439, 5, 0)]
        public int UsStart { get; set; } = 1140;

        // ---------- profile / vùng (chỉ để hiển thị hợp lưu + info TP-vướng-vùng) ----------
        [InputParameter("Số tick / hàng profile", 20, 1, 50, 1, 0)]
        public int RowTicks { get; set; } = 1;
        [InputParameter("Gap tách phiên (phút)", 21, 20, 240, 1, 0)]
        public int SessionGapMin { get; set; } = 40;
        [InputParameter("Gap tách ngày (phút)", 22, 20, 240, 1, 0)]
        public int DayGapMin { get; set; } = 45;
        [InputParameter("Số ngày vùng còn hiệu lực", 24, 1, 10, 1, 0)]
        public int ZoneExpireDays { get; set; } = 3;
        [InputParameter("Dung sai hợp lưu (tick)", 30, 1, 30, 1, 0)]
        public int ConfluenceTol { get; set; } = 7;
        [InputParameter("Số vùng hợp lưu tối thiểu (chỉ để chấm A-grade)", 32, 1, 5, 1, 0)]
        public int MinConfluence { get; set; } = 2;

        // ---------- VSA (khớp VsaVolume: SMA gồm nến hiện tại) ----------
        [InputParameter("VSA period (SMA volume, gồm nến này)", 40, 5, 200, 1, 0)]
        public int VsaPeriod { get; set; } = 20;
        [InputParameter("VSA climax tím (× TB)", 42, 0.5, 8, 0.05, 2)]
        public double VsaClimax { get; set; } = 2.2;

        // ---------- CBR: RANGE ----------
        [InputParameter("Range: số nến trước break", 50, 3, 30, 1, 0)]
        public int RangeLen { get; set; } = 8;
        [InputParameter("Range: span TỐI THIỂU (giá) — loại micro-range nhiễu", 51, 0.5, 10, 0.1, 1)]
        public double RangeMinPts { get; set; } = 3.0;   // sweep: span≥3đ net +40 vs +35 (loại vụ 07/24 19:27)
        [InputParameter("Range: span TỐI ĐA (giá) — vùng co hẹp", 52, 1, 20, 0.1, 1)]
        public double RangeMaxPts { get; set; } = 7.5;   // thử nới 10 → exp 0.29→0.21 (KHÔNG free) → giữ 7.5. Nới tại đây nếu muốn thêm lệnh (chấp nhận loãng edge)

        // ---------- CBR: BREAK ----------
        [InputParameter("Break: VSA tối thiểu (× TB) — climax", 53, 1.0, 5, 0.05, 2)]
        public double BreakVsa { get; set; } = 2.0;
        [InputParameter("Break: thân mạnh ≥ (body/range)", 54, 0.2, 1.0, 0.05, 2)]
        public double BreakBody { get; set; } = 0.50;

        // ---------- CBR: HỒI + TIẾP DIỄN ----------
        [InputParameter("Chờ hồi+tiếp diễn trong (số nến)", 55, 3, 40, 1, 0)]
        public int WaitBars { get; set; } = 12;
        [InputParameter("Retrace TỐI THIỂU (% của leg)", 56, 0.05, 0.9, 0.05, 2)]
        public double PullMin { get; set; } = 0.60;   // nâng 40→60% (2026-07-28): WR 30→33%, giữ net. Hồi SÂU 60-90% = runner thật; hồi nông = đuổi đà kiệt.
        [InputParameter("Retrace TỐI ĐA (% của leg)", 57, 0.3, 1.0, 0.05, 2)]
        public double PullMax { get; set; } = 0.90;   // GIỮ cao: hồi sâu 60-90% chứa nhiều runner lớn. Cap thấp = cắt lãi.
        [InputParameter("Hồi cho phép thủng cạnh vùng (tick)", 58, 0, 10, 1, 0)]
        public int HoldTolTicks { get; set; } = 2;
        [InputParameter("Nến tiếp diễn: thân ≥ (body/range)", 59, 0.2, 1.0, 0.05, 2)]
        public double ResumeBody { get; set; } = 0.35;
        // ⚠ LỖI GỐC (người học phát hiện trên chart 2026-08-02): nến PHÁ bắt buộc VSA≥BreakVsa(2.0),
        // nhưng nến VÀO LỆNH (nến tiếp diễn) TRƯỚC ĐÂY KHÔNG có một điều kiện VSA nào — chỉ cần thân
        // ≥0.35 và vol≥VolFloor. Đo trên dxFeed 5-7/2026 (research/wyckoff/cbr_entry_vsa.py):
        //   VSA nến vào: trung vị 1.04x, p10 0.38x → 56% số lệnh vào nến DƯỚI ngưỡng "high" 1.2x.
        //   Nhóm nến vào VSA<0.8 là nhóm tệ nhất: WR 35% (toàn bộ n=55 là 47%).
        // Gate này CHO PHÉP BỎ QUA nến hồi yếu và CHỜ nến hồi khác trong cùng cửa sổ WaitBars
        // (KHÔNG huỷ leg) — đó là lý do nó không mất tổng R: n 55→42, WR 47.3→54.8%, +49R→+50R,
        // EV +0.891→+1.190. Đối chứng bỏ NGẪU NHIÊN đúng 13 lệnh: trung vị EV +0.905, p95 +1.095
        // ⇒ p=0.037 — gate CHỌN chứ không chỉ làm mỏng. Đối chứng thứ 2: siết ResumeBody để cắt
        // cùng lượng lệnh thì TỆ đi (0.55→EV +0.600) ⇒ thông tin nằm ở VSA, không ở thân nến.
        // Vì sao 0.8 chứ không phải 1.2 ("high")? Vì 1.2 cắt quá tay: +30R (so với +50R) mà EV
        // không hơn (+1.000 vs +1.190). Cái giết lệnh là nến hồi CHẾT, không phải nến hồi thường.
        // Đặt 0 = tắt (về đúng hành vi cũ để A/B).
        [InputParameter("Nến VÀO LỆNH: VSA ≥ (0 = tắt) — nến hồi yếu thì CHỜ nến khác", 61, 0, 4.0, 0.05, 2)]
        public double ResumeVsa { get; set; } = 0.80;

        // ---------- risk / TP ----------
        [InputParameter("SL sàn (giá)", 60, 0.5, 8, 0.1, 1)]
        public double SlFloorPts { get; set; } = 3.0;
        [InputParameter("SL trần (giá) — quá thì bỏ", 61, 1, 12, 0.1, 1)]
        public double SlCapPts { get; set; } = 7.0;
        [InputParameter("SL đệm ngoài cực trị hồi (tick)", 62, 0, 20, 1, 0)]
        public int SlBuf { get; set; } = 2;
        [InputParameter("RR mục tiêu (TP, giữ runner)", 63, 1, 8, 0.5, 1)]
        public double RR { get; set; } = 3.0;
        [InputParameter("Cooldown mỗi phía (số nến)", 64, 0, 60, 1, 0)]
        public int Cooldown { get; set; } = 15;
        [InputParameter("Gộp tín hiệu trùng (số nến)", 65, 1, 20, 1, 0)]
        public int DedupBars { get; set; } = 6;

        // ---------- LỌC THUẬN XU HƯỚNG (proxy TPO bias) + THANH KHOẢN (2026-07-28) ----------
        [InputParameter("Lọc THUẬN xu hướng (proxy TPO bias)", 44)]
        public bool TrendFilter { get; set; } = true;    // thg6 crash: -16R→+5R, MỌI THÁNG DƯƠNG
        [InputParameter("Xu hướng: số nến lookback (~8h)", 45, 60, 2000, 20, 0)]
        public int TrendBars { get; set; } = 480;        // 480≈8h. EMA30/120 quá nhanh → loại nhầm.
        [InputParameter("Xu hướng: ngưỡng đổi hướng (giá)", 46, 0.0, 10, 0.1, 1)]
        public double TrendTolPts { get; set; } = 1.0;
        [InputParameter("CBR: vào ĐÚNG phía VWAP", 47)]
        public bool VwapAlign { get; set; } = true;      // LONG khi entry≥VWAP; SHORT khi ≤VWAP
        [InputParameter("Lọc thanh khoản (vma ≥ k×TB dài)", 48)]
        public bool LiquidityFilter { get; set; } = true; // COMEX/US session > Á mỏng (portable, không hardcode giờ)
        [InputParameter("Thanh khoản: k (× TB dài)", 49, 0.0, 3.0, 0.05, 2)]
        public double LiquidityRatio { get; set; } = 0.75;
        [InputParameter("Thanh khoản: cửa sổ TB (số nến)", 43, 100, 5000, 50, 0)]
        public int LiquidityWindow { get; set; } = 1000;

        // ---------- Lọc PHIÊN CHẾT (research CBR n=140, xem BASELINE.md/WYCKOFF_V6_PLAN.md) ----------
        // ⚠ SỬA LỖI (2026-07-31, phát hiện khi user hỏi vì sao 7-8h sáng VN bị cấm): bar.TimeLeft
        // LÀ GIỜ UTC, KHÔNG phải giờ VN (comment cũ ở đây từng khẳng định nhầm "== giờ VN" —
        // WYCKOFF_V6_PLAN.md §BƯỚC 5 đã chứng minh SAI). Khung xấu thật đo được trên dữ liệu là
        // UTC 02h-08h (CBR WR 9.7%, −19R) — quy đổi ra giờ VN (+7) là **09h-15h chiều**, KHÔNG
        // phải 2h-8h sáng. Bản cũ (DeadUseUtc mặc định false) cộng nhầm TzOffset trước khi so
        // sánh nên lại đi cấm nhầm VN 2h-8h SÁNG (khung này CHƯA HỀ được đo, không phải khung đã
        // validate) — vô tình chặn luôn 7-8h sáng dù dữ liệu không hề nói khung đó xấu.
        // Mặc định BẬT lọc + DeadUseUtc=true để khớp đúng khung đã đo. Tắt ô lọc nếu muốn so A/B.
        [InputParameter("Lọc phiên chết: BỎ lệnh CBR khung giờ chết (mặc định BẬT)", 77)]
        public bool SkipDeadSession { get; set; } = true;
        [InputParameter("Phiên chết: neo theo giờ UTC (tắt = giờ hiển thị VN)", 76)]
        public bool DeadUseUtc { get; set; } = true;
        [InputParameter("Phiên chết: giờ BẮT ĐẦU (UTC nếu DeadUseUtc, ngược lại giờ hiển thị, 0-23)", 78, 0, 23, 1, 0)]
        public int DeadStartHour { get; set; } = 2;
        [InputParameter("Phiên chết: giờ KẾT THÚC (không gồm, UTC nếu DeadUseUtc, 0-24)", 79, 0, 24, 1, 0)]
        public int DeadEndHour { get; set; } = 8;

        // ---------- QUAY ĐẦU v2 — đảo chiều tại VWAP (2026-07-28, khớp reversal_vwap.py) ----------
        [InputParameter("Bật nhánh QUAY ĐẦU (đảo chiều tại VWAP)", 66)]
        public bool EnableReversal { get; set; } = true;
        [InputParameter("Quay đầu: RR mục tiêu (TP) — đảo chiều trần ~1.3R", 67, 1.0, 4.0, 0.25, 2)]
        public double RevRR { get; set; } = 1.5;
        [InputParameter("Quay đầu: VSA xác nhận tối thiểu", 68, 1.0, 4.0, 0.1, 1)]
        public double RevVsaConf { get; set; } = 1.8;
        [InputParameter("Quay đầu: dung sai chạm VWAP (tick)", 74, 2, 40, 1, 0)]
        public int VwapTolTicks { get; set; } = 12;
        [InputParameter("Quay đầu: số nến tiếp cận VWAP", 75, 2, 20, 1, 0)]
        public int RevApproachBars { get; set; } = 6;
        [InputParameter("Quay đầu: rút râu ≥ (rau/range)", 69, 0.3, 1.0, 0.05, 2)]
        public double WickFrac { get; set; } = 0.50;
        [InputParameter("Hấp thụ per-level (footprint LIVE) = nâng grade A", 76, 0.3, 1.0, 0.05, 2)]
        public double AbsDom { get; set; } = 0.60;
        [InputParameter("Quay đầu: climax tím = nâng grade (bonus)", 73)]
        public bool RevClimaxOverride { get; set; } = true;
        // Port luật "NẾN VÀO LỆNH PHẢI THUẬN MÀU" từ EntrySignal (2026-08-02). Nhánh CBR ĐÃ có sẵn luật
        // này (`bj.C > bj.O` / `bj.C < bj.O` trong `resume`); nhánh QUAY ĐẦU thì KHÔNG kiểm thân nến, nên
        // nến TRẮNG vẫn bắn SHORT và nến ĐỎ vẫn bắn LONG.
        // ĐO (research/rev_bodydir_ab*.py, dxFeed 5-7/2026, n=27):
        //   · MFE trung vị: nến thuận màu 3.78R vs nến ngược màu 1.13R  (chênh rất lớn, đo trực tiếp)
        //   · EV thuận màu > ngược màu ở MỌI RR thử (1.0/1.5/2.0/3.0)
        //   · NHƯNG kiểm định hoán vị: p=0.288 ở RR1.5 (RevRR đang ship) — KHÔNG có ý nghĩa;
        //     chỉ p≈0.07 ở RR2-3, vẫn không qua ngưỡng. Ở RR1.5 luật này còn LÀM GIẢM tổng R
        //     (+10.5R → +8.5R) vì cắt mất nửa số lệnh.
        //   · tách theo phía thì mỗi ô chỉ còn n=6-8: SHORT ngược màu lại DƯƠNG (+0.667) ⇒ nhiễu.
        // ⇒ MẶC ĐỊNH TẮT. Không đủ bằng chứng, và AUDIT_V7.md §13 đã phán cả nhánh QUAY ĐẦU là FAIL.
        // (Đối chiếu: gate ResumeVsa của CBR qua được đối chứng ngẫu nhiên p=0.037 nên mới bật mặc định.)
        [InputParameter("Quay đầu: nến vào lệnh phải THUẬN màu — CHƯA qua đối chứng, mặc định TẮT", 77)]
        public bool RevRequireBodyDir { get; set; } = false;

        // ---------- CORVEN: neo vùng HVN/VWAP tuần|ngày (2026-08-01, PLAN_KB_ABC.md v8/runner) ----------
        // ⚠ MẶC ĐỊNH TẮT — bản v5 đang chạy live KHÔNG được đổi hành vi. Khi TẮT, hai nhánh CBR/QUAY_ĐẦU
        // chạy y hệt code cũ (không đụng một dòng nào của Scan()/ScanReversal() gốc). Khi BẬT, PLAY2 (CBR)
        // đổi cạnh neo từ range co hẹp M1 nội bộ sang mép HVN tuần/ngày, PLAY1 (QUAY ĐẦU) đổi vùng fade từ
        // CHỈ VWAP phiên sang HVN tuần/ngày + VWAP tuần/ngày. Backtest offline (v8/runner/RESULTS_RUNNER_ZONES.md):
        // ĐỐI CHỨNG NGẪU NHIÊN KHÔNG QUA cho hầu hết biến thể (vị trí vùng không mang thêm thông tin so với
        // vùng dịch ngẫu nhiên) — cờ này tồn tại để A/B TỰ CHỌN, KHÔNG phải khuyến nghị bật.
        [InputParameter("CORVEN: bật neo vùng HVN/VWAP tuần|ngày — THAY hẳn vùng cũ (mặc định TẮT — xem RESULTS_RUNNER_ZONES.md)", 149)]
        public bool CorvenZoneAnchor { get; set; } = false;
        [InputParameter("CORVEN: tầng vùng khi THAY (0=Tuần/KB-A, 1=Ngày/KB-B)", 150, 0, 1, 1, 0)]
        public int CorvenZoneTier { get; set; } = 0;
        [InputParameter("CORVEN: dung sai chạm vùng HVN (tick)", 151, 4, 40, 1, 0)]
        public int CorvenTolTicks { get; set; } = 12;
        [InputParameter("CORVEN: ngưỡng HVN (× lần TB)", 152, 1.0, 3.0, 0.1, 1)]
        public double CorvenHvnMinRatio { get; set; } = 1.5;
        [InputParameter("CORVEN: số HVN tối đa mỗi tuần/ngày", 153, 1, 5, 1, 0)]
        public int CorvenHvnMaxN { get; set; } = 3;
        // CỘNG THÊM (union) — khác THAY (Anchor) ở chỗ: CBR/QUAY_ĐẦU gốc vẫn chạy y hệt code cũ, vùng
        // CORVEN (HVN+VWAP CẢ tuần LẪN ngày) chỉ là NGUỒN TÍN HIỆU BỔ SUNG, không xoá tín hiệu cũ nào.
        // Kết quả offline (combo_scan.py, 05-07/2026): CBR 54→120 lệnh (WR 46→39%, +46R→+68R), QUAY_ĐẦU
        // 27→40 lệnh (WR 56→58%, +10.5R→+17.5R). Đối chứng ngẫu nhiên: phần lệnh CORVEN thêm vào phần
        // lớn KHÔNG vượt vùng dịch ngẫu nhiên → tăng lệnh/R chủ yếu do có thêm lượt vào (bộ lọc trend/
        // VWAP/thanh khoản vốn đã có edge), KHÔNG chắc do vị trí HVN/VWAP thật sự tốt. Bật để REVIEW
        // TỪNG LỆNH THỦ CÔNG (không phải khuyến nghị bật live). CorvenZoneAnchor=true sẽ ưu tiên hơn
        // (bỏ qua cờ này) vì 2 cờ không nên bật cùng lúc.
        [InputParameter("CORVEN: CỘNG THÊM vùng HVN/VWAP tuần+ngày (giữ nguyên CBR/QUAY_ĐẦU cũ — để review)", 154)]
        public bool CorvenZoneAdd { get; set; } = false;

        // ---------- lọc / warm-up ----------
        [InputParameter("Sàn volume (chống nến mỏng)", 70, 0, 500, 1, 0)]
        public int VolFloor { get; set; } = 20;
        [InputParameter("Warm-up sau gap (số nến)", 71, 0, 60, 1, 0)]
        public int WarmupBars { get; set; } = 20;

        // ---------- hiển thị ----------
        [InputParameter("Hiện tín hiệu", 80)]
        public bool ShowSignals { get; set; } = true;
        [InputParameter("Hiện vùng hợp lưu", 81)]
        public bool ShowZones { get; set; } = true;
        [InputParameter("Hiện bảng", 82)]
        public bool ShowPanel { get; set; } = true;
        [InputParameter("Hiện TOÀN BỘ tín hiệu lịch sử", 83)]
        public bool ShowAllHistory { get; set; } = true;
        [InputParameter("(nếu tắt) số nến hiển thị gần nhất", 87, 50, 20000, 50, 0)]
        public int DisplayBars { get; set; } = 600;
        [InputParameter("Số dòng tối đa trong bảng", 88, 2, 20, 1, 0)]
        public int PanelRows { get; set; } = 4;
        [InputParameter("Góc bảng (0=TL 1=TR 2=BL 3=BR)", 84, 0, 3, 1, 0)]
        public int PanelCorner { get; set; } = 0;
        [InputParameter("Cỡ chữ", 85, 7, 20, 1, 0)]
        public int FontSize { get; set; } = 9;

        [InputParameter("Màu LONG", 90)]
        public Color LongColor { get; set; } = Color.FromArgb(0x26, 0xC6, 0xDA);
        [InputParameter("Màu SHORT", 91)]
        public Color ShortColor { get; set; } = Color.FromArgb(0xEF, 0x53, 0x50);
        [InputParameter("Màu vùng hợp lưu", 92)]
        public Color ConflColor { get; set; } = Color.FromArgb(0xFF, 0xB3, 0x00);
        [InputParameter("Màu SL (đỏ)", 93)]
        public Color SlLineColor { get; set; } = Color.FromArgb(0xE5, 0x39, 0x35);
        [InputParameter("Màu TP (xanh)", 94)]
        public Color TpLineColor { get; set; } = Color.FromArgb(0x00, 0xC8, 0x53);
        [InputParameter("Độ dày đường", 95, 1, 5, 1, 0)]
        public int LineWidth { get; set; } = 2;
        [InputParameter("Tô vùng R:R (lời/lỗ)", 96)]
        public bool ShowRiskBox { get; set; } = true;
        [InputParameter("Vẽ mũi tên", 100)]
        public bool ShowArrows { get; set; } = true;
        [InputParameter("Vẽ đường E/SL/TP", 101)]
        public bool ShowLines { get; set; } = true;
        [InputParameter("Vẽ chip giá (mép phải)", 102)]
        public bool ShowChips { get; set; } = true;
        [InputParameter("Vẽ nhãn setup", 103)]
        public bool ShowLabels { get; set; } = true;
        [InputParameter("Hiện tín hiệu ĐÃ ĐÓNG (mờ)", 104)]
        public bool ShowClosed { get; set; } = true;
        [InputParameter("SL/TP nét đứt (tắt = nét liền)", 105)]
        public bool DashedSlTp { get; set; } = true;
        [InputParameter("Độ mờ vùng R:R (0-120)", 106, 0, 120, 2, 0)]
        public int RiskBoxOpacity { get; set; } = 34;
        [InputParameter("Cỡ mũi tên", 107, 4, 20, 1, 0)]
        public int ArrowSize { get; set; } = 8;
        [InputParameter("Độ dày đường vùng hợp lưu", 108, 1, 6, 1, 0)]
        public int ZoneLineWidth { get; set; } = 2;
        [InputParameter("Độ mờ nền bảng (100-255)", 109, 100, 255, 5, 0)]
        public int PanelOpacity { get; set; } = 215;

        // ---------- xuất CSV (để đối chiếu C# ↔ Python + tách WR 2 nhánh) ----------
        [InputParameter("Xuất CSV toàn bộ tín hiệu", 120)]
        public bool ExportCsv { get; set; } = false;
        [InputParameter("Đường dẫn CSV (trống = thư mục Documents)", 121)]
        public string ExportPath { get; set; } = "";

        // ---------- CẦU NỐI MT5 (gửi tín hiệu sang MetaTrader 5 / Exness) ----------
        // Ghi 1 dòng JSON/lệnh vào <MT5 Common>\Files\runner_cmd.jsonl → EA RunnerBridge.mq5 đọc & vào lệnh.
        // CHỈ gửi KHOẢNG CÁCH SL + RR, KHÔNG gửi giá tuyệt đối: Quantower chạy GC/MGC futures,
        // MT5 chạy XAUUSD spot — lệch basis vài chục USD (và trôi + đảo hợp đồng), nhưng cả hai
        // đều báo giá USD/oz nên KHOẢNG CÁCH chuyển 1:1. EA vào market rồi tự đặt SL/TP theo fill.
        [InputParameter("Cầu nối MT5: BẬT gửi tín hiệu", 130)]
        public bool Mt5Bridge { get; set; } = false;
        [InputParameter("MT5: dry-run (EA chỉ ghi log, KHÔNG vào lệnh)", 131)]
        public bool Mt5DryRun { get; set; } = true;
        [InputParameter("MT5: thư mục Files (trống = Common\\Files của MT5)", 132)]
        public string Mt5Dir { get; set; } = "";
        [InputParameter("MT5: tuổi tín hiệu tối đa (giây) — chống bắn lệnh cũ", 133, 20, 600, 5, 0)]
        public int Mt5MaxAgeSec { get; set; } = 90;
        [InputParameter("MT5: gửi nhánh CBR (3R)", 134)]
        public bool Mt5SendCbr { get; set; } = true;
        [InputParameter("MT5: gửi nhánh QUAY ĐẦU (1.5R)", 135)]
        public bool Mt5SendRev { get; set; } = true;
        [InputParameter("MT5: chỉ gửi grade A (hợp lưu)", 136)]
        public bool Mt5OnlyGradeA { get; set; } = false;
        // ---------- NHỒI LỆNH (nhân lot cho tín hiệu mạnh) ----------
        // Mặc định TẮT (NhoiMult=1). Bridge EA nhân lot cơ sở với "size_mult" trong JSONL.
        //
        // ⚠ KHÁC EntrySignal: bên đó nhồi theo HỢP LƯU (`Cluster`) vì hợp lưu ≥2 là gate lõi đã backtest.
        // Ở runner thì hợp lưu CHỈ LÀ THÔNG TIN HIỂN THỊ, không lọc lệnh nào — và với nhánh QUAY ĐẦU nó
        // còn được đo là NGƯỢC DẤU (0 vùng → WR 33%, 1 → 16%, 2 → 17%, 3 → 0%; xem đầu file
        // research/reversal_vwap.py). Nhồi theo hợp lưu ở runner sẽ nhồi to nhất đúng vào nhóm tệ nhất.
        //
        // Thay vào đó gate theo VSA NẾN VÀO LỆNH — thứ vừa chứng minh được ở RESULTS_ENTRY_VSA.md.
        // Đo trên cấu hình đang ship (đã bật ResumeVsa=0.8), dxFeed 05-07/2026:
        //   RunnerSignal RR3 (n=42): VSA vào [0.8,1.2) EV +1.286 · [1.2,1.8) +0.500 · [2.2,∞) +2.111 (WR 78%)
        //   WyckoffRunner RR4 (n=21): [0.8,1.2) +1.500 · [1.2,1.8) +1.500 · [2.2,∞) +3.000 (WR 80%)
        // Nhồi ×5 theo từng ngưỡng (tổng R / sụt vốn tối đa / tỷ số R trên sụt vốn), RunnerSignal:
        //   không nhồi   +50R  MDD  6.0R   8.3
        //   ≥1.5        +182R  MDD 14.0R  13.0
        //   ≥1.8        +146R  MDD  8.0R  18.3
        //   ≥2.2        +126R  MDD  6.0R  21.0  ← tốt nhất, và KHÔNG làm tăng sụt vốn so với không nhồi
        //   ≥2.5        +118R  MDD  6.0R  19.7
        // Chọn 2.2 vì đó cũng đúng là `VsaClimax` đã có sẵn trong code (nến "tím") — không đẻ thêm
        // một hằng số tinh chỉnh mới.
        // ⚠ TRUNG THỰC: nhóm được nhồi chỉ có n=9 (RunnerSignal) và n=5 (WyckoffRunner) trong 3 tháng.
        // Đây là mẫu quá nhỏ để tin con số; hãy coi ngưỡng 2.2 là mặc định hợp lý, không phải kết luận.
        [InputParameter("MT5: nhồi khi VSA nến vào ≥ (0 = nhồi mọi lệnh)", 137, 0, 5, 0.1, 1)]
        public double NhoiVsaGate { get; set; } = 2.2;
        [InputParameter("MT5: hệ số nhồi (×lot; 1 = tắt)", 138, 1, 10, 0.5, 1)]
        public double NhoiMult { get; set; } = 1.0;

        // ---------- BÁO TELEGRAM (mở lệnh + đóng bởi SL/TP) ----------
        // Bắn 1 tin GỌN khi có tín hiệu MỚI ở nến vừa đóng, và 1 tin khi lệnh đó chạm SL/TP.
        // Chỉ báo ĐÓNG cho lệnh mà bot ĐÃ báo MỞ (không báo đóng lệnh lịch sử). Dùng chung
        // module TeleReport (đã concat từ ProfileEngine) — chỉ mượn hàm gửi + log, không đụng
        // cơ chế tổng-hợp-2-mốc của bộ TPO. Cần bật + điền token/chat_id (điền tay, repo public).
        [InputParameter("Báo Telegram: BẬT (mở/đóng lệnh)", 140)]
        public bool TeleAlerts { get; set; } = false;
        [InputParameter("Telegram: Bot token", 141)]
        public string TeleBotToken { get; set; } = "";
        [InputParameter("Telegram: Chat ID", 142)]
        public string TeleChatId { get; set; } = "";
        [InputParameter("Báo khi MỞ lệnh", 143)]
        public bool TeleAlertOpen { get; set; } = true;
        [InputParameter("Báo khi ĐÓNG (chạm TP/SL)", 144)]
        public bool TeleAlertClose { get; set; } = true;
        [InputParameter("Chỉ báo grade A (hợp lưu)", 145)]
        public bool TeleOnlyGradeA { get; set; } = false;
        [InputParameter("Báo nhánh CBR (3R)", 146)]
        public bool TeleSendCbr { get; set; } = true;
        [InputParameter("Báo nhánh QUAY ĐẦU (1.5R)", 147)]
        public bool TeleSendRev { get; set; } = true;
        [InputParameter("Tuổi tín hiệu tối đa (giây) — chống bắn khi reload", 148, 20, 600, 5, 0)]
        public int TeleMaxAgeSec { get; set; } = 90;
        [InputParameter("TG · Gửi thử ngay", 149)]
        public bool TeleTestNow { get; set; } = false;

        private bool _vaLoaded;
        private string _exportedTo;
        private bool _armed;                                   // false = lần quét đầu (nạp lịch sử) → KHÔNG gửi
        private int _bridgeSent;
        private string _bridgeStatus;
        private readonly HashSet<string> _sentIds = new();
        // ----- Telegram -----
        private readonly TeleReport _tele = new();
        private bool _teleArmed;                               // như _armed nhưng riêng cho Telegram
        private readonly HashSet<string> _teleSeen = new();    // id đã xử lý (chống lặp)
        private readonly HashSet<string> _teleOpenSent = new();// id ĐÃ báo MỞ (điều kiện để báo ĐÓNG)
        private readonly HashSet<string> _teleClosed = new();  // id ĐÃ báo ĐÓNG
        private int _teleSent;
        private string _teleStatus;
        private readonly object _sync = new();
        private readonly object _calc = new();
        private RenderState _render;
        private int _digits = 1;
        private double _tick = 0.1;
        private int _lastN = -1;
        private int _vaCov, _vaTot;
        private DateTime _vaFirst = DateTime.MinValue;
        private readonly PanelDrag _drag = new();

        public RunnerSignal() : base()
        {
            Name = "Runner Signal (CBR M1)";
            Description = "Runner CBR M1: phá vùng co → chờ hồi giữ leg → vào nến tiếp diễn (TP 3R). Bắn nến đóng. Cần Volume Analysis. Add vào chart M1.";
            SeparateWindow = false;
        }

        public bool IsRequirePriceLevelsCalculation => true;
        public void VolumeAnalysisData_Loaded()
        {
            lock (_calc) { _vaLoaded = true; _lastN = -1; }
            try { Process(); }
            catch (Exception ex) { LogErr(ex, "VolumeAnalysisData_Loaded/Process"); }
        }
        protected override void OnClear()
        {
            _drag.Detach();
            lock (_calc)
            {
                _vaLoaded = false; _lastN = -1;
                _armed = false; _sentIds.Clear(); _bridgeSent = 0; _bridgeStatus = null;   // re-attach = nạp lại lịch sử, không bắn lệnh cũ
                _teleArmed = false; _teleSeen.Clear(); _teleOpenSent.Clear(); _teleClosed.Clear(); _teleSent = 0; _teleStatus = null;
                lock (_sync) _render = null;
            }
        }
        protected override void OnUpdate(UpdateArgs args)
        {
            PollTeleTest();                       // nút "gửi thử" chạy ĐỘC LẬP với VA (bấm là gửi ngay)
            var p = HistoricalData?.VolumeAnalysisCalculationProgress;
            if (p == null || p.State != VolumeAnalysisCalculationState.Finished) return;
            // FIX BUG MẤT PANEL: KHÔNG chờ callback VolumeAnalysisData_Loaded(). Quantower chỉ gọi callback
            // đó khi footprint được TÍNH MỚI; nếu VA đã tính xong sẵn (reload chart, attach lại indicator,
            // đổi khung...) callback KHÔNG bắn → _vaLoaded mãi false → Process() và cả panel bị chặn vĩnh
            // viễn, phải xoá & cài lại indicator mới hiện. State==Finished đã đủ điều kiện đọc footprint.
            if (!_vaLoaded) lock (_calc) { _vaLoaded = true; _lastN = -1; }
            // FIX BUG "biến mất khi refresh data": 1 exception không bắt trong Process() có thể khiến
            // Quantower coi indicator lỗi và gỡ khỏi chart (phải cắm lại). Bọc lại để: (a) 1 tick lỗi
            // chỉ bị bỏ qua thay vì crash cả indicator, (b) ghi log để tra được nguyên nhân thật lần sau.
            try { Process(); }
            catch (Exception ex) { LogErr(ex, "OnUpdate/Process"); }
        }

        private void LogErr(Exception ex, string where)
        {
            try
            {
                // cùng thư mục %LOCALAPPDATA%\RunnerSignal với tele_log.txt (xem ConfigTele)
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RunnerSignal");
                Directory.CreateDirectory(dir);
                File.AppendAllText(Path.Combine(dir, "error_log.txt"),
                    $"{DateTime.UtcNow.AddHours(TzOffset):yyyy-MM-dd HH:mm:ss} [{Name}] {where}: {ex}\n");
            }
            catch { }
        }

        private string Fmt(double p) => double.IsNaN(p) ? "—" : Math.Round(p, _digits).ToString("0.0##");
        private string LabelOf(DateTime t)
        {
            int m = (int)(t.AddHours(TzOffset).TimeOfDay.TotalMinutes);
            if (m >= AsiaStart && m < EuropeStart) return "A";
            if (m >= EuropeStart && m < UsStart) return "AU";
            return "MY";
        }
        private static string VN(string lab) => lab == "A" ? "Á" : lab == "AU" ? "Âu" : "Mỹ";

        private sealed class Bar
        {
            public int Idx;
            public int HdIdx;
            public DateTime Time;
            public double O, H, L, C, Vol, Delta, Cum, Vwap, Vma, Vratio;
            public double VwapWeek, VwapDay;   // CORVEN: VWAP neo tuần/ngày (reset rộng hơn Vwap = VWAP phiên)
            public int Bias;      // EMA30 vs EMA120 (hiển thị; KHÔNG gate — bias thật = TPO)
            public int Trend;     // close vs close TrendBars trước (proxy TPO bias — GATE)
            public double LiqRatio;  // vma / TB-vol dài (thanh khoản phiên; GATE)
            public int SinceGap;
            public double Rng => H - L;
            public double Body => Math.Abs(C - O);
            public double UW => H - Math.Max(O, C);
            public double LW => Math.Min(O, C) - L;
            public double Brat => Rng > 0 ? Body / Rng : 0;
            public double Cpos => Rng > 0 ? (C - L) / Rng : 0.5;
            public double Ddom => Vol > 0 ? Delta / Vol : 0;
        }

        private sealed class PZone
        {
            public double Price; public string Kind; public double Strength;
            public DateTime ReadyTime, ExpireTime;
            public bool IsWeek;   // CORVEN: true=HVN tuần, false=HVN ngày (chỉ dùng bởi zone CORVEN)
        }

        private sealed class Sig
        {
            public int Idx; public DateTime Time; public int Side;
            public string Scen; public char Grade; public double Entry, Sl, Tp1, Tp2, RiskT, Rr2, TargetRr;
            public int Cluster;          // số vùng chồng quanh giá vào (info, KHÔNG gate)
            public double BlockR;        // TP-vướng-vùng mạnh: cách entry bao nhiêu R (NaN = không vướng)
            public double Vsa; public bool Climax; public List<string> Why = new();
            public string Outcome = "running";
            public DateTime OutTime;
        }

        private void Process()
        {
            lock (_calc)
            {
                try
                {
                    var hd = HistoricalData;
                    if (hd == null) return;
                    _tick = Symbol?.TickSize ?? 0;
                    if (_tick <= 0) return;
                    _digits = Math.Max(0, (int)Math.Round(-Math.Log10(_tick)));
                    int n = hd.Count;
                    if (n < VsaPeriod + 5) return;
                    if (n == _lastN) return;

                    var B = BuildBars(hd, n);
                    if (B.Count < VsaPeriod + 5) { _lastN = n; return; }

                    var pool = BuildPool(hd, B);
                    var corvenZones = (CorvenZoneAnchor || CorvenZoneAdd) ? BuildCorvenZones(hd) : null;
                    var sigs = Scan(hd, B, pool, corvenZones);
                    foreach (var s in sigs) { Simulate(B, s); Enrich(pool, s); }

                    if (ExportCsv) ExportSignals(sigs);
                    if (Mt5Bridge) EmitLive(sigs, B);
                    if (TeleAlerts) EmitTele(sigs, B);

                    int minIdx = B.Count - 1 - DisplayBars;
                    var show = ShowAllHistory ? sigs : sigs.Where(s => s.Idx >= minIdx || s.Outcome == "running").ToList();

                    double now = B[B.Count - 1].C;
                    var clusters = CurrentClusters(pool, B[B.Count - 1].Time, now);

                    lock (_sync) _render = new RenderState { Sigs = show, Clusters = clusters, Panel = BuildPanel(show), Digits = _digits };
                    _lastN = n;
                }
                catch { /* giữ indicator sống */ }
            }
        }

        // ================= dựng nến + số dẫn xuất (KHỚP entry_month.load_m1) =================
        private List<Bar> BuildBars(HistoricalData hd, int n)
        {
            var B = new List<Bar>(n);
            int cov = 0; DateTime first = DateTime.MinValue;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                var t = b.VolumeAnalysisData?.Total;
                if (t != null) { cov++; if (first == DateTime.MinValue) first = b.TimeLeft; }
                B.Add(new Bar { Idx = B.Count, HdIdx = i, Time = b.TimeLeft, O = b.Open, H = b.High, L = b.Low, C = b.Close,
                    Vol = t?.Volume ?? b.Volume, Delta = t?.Delta ?? 0 });
            }
            _vaCov = cov; _vaTot = B.Count; _vaFirst = first;
            double csPV = 0, csV = 0, cum = 0, rollSum = 0, liqSum = 0;
            double csPvDay = 0, csVDay = 0, csPvWeek = 0, csVWeek = 0;   // CORVEN: VWAP ngày/tuần
            double ef = double.NaN, es = double.NaN, kf = 2.0 / (30 + 1), ks = 2.0 / (120 + 1);
            int liqW = Math.Max(100, LiquidityWindow);
            var q = new Queue<double>();
            var lq = new Queue<double>();       // cửa sổ dài để tính TB-vol thanh khoản (O(1))
            for (int i = 0; i < B.Count; i++)
            {
                var b = B[i];
                bool gap = i > 0 && (b.Time - B[i - 1].Time).TotalMinutes > 30;
                if (gap) { csPV = 0; csV = 0; }
                double tp = (b.H + b.L + b.C) / 3.0; csPV += tp * b.Vol; csV += b.Vol;
                b.Vwap = csV > 0 ? csPV / csV : b.C;
                // CORVEN: VWAP ngày reset tại gap>DayGapMin (khớp ProfileEngine.GroupByGap dùng cho D-1 pool),
                // VWAP tuần reset tại gap>30h (khớp ProfileEngine.WeekSpans / zones_corven.py weekend_gap_hours=30).
                bool gapDay = i > 0 && (b.Time - B[i - 1].Time).TotalMinutes > DayGapMin;
                bool gapWeek = i > 0 && (b.Time - B[i - 1].Time).TotalHours > 30;
                if (gapDay) { csPvDay = 0; csVDay = 0; }
                if (gapWeek) { csPvWeek = 0; csVWeek = 0; }
                csPvDay += tp * b.Vol; csVDay += b.Vol;
                csPvWeek += tp * b.Vol; csVWeek += b.Vol;
                b.VwapDay = csVDay > 0 ? csPvDay / csVDay : b.C;
                b.VwapWeek = csVWeek > 0 ? csPvWeek / csVWeek : b.C;
                cum += b.Delta; b.Cum = cum;
                q.Enqueue(b.Vol); rollSum += b.Vol;
                if (q.Count > VsaPeriod) rollSum -= q.Dequeue();
                b.Vma = q.Count > 0 ? rollSum / q.Count : b.Vol;
                b.Vratio = b.Vma > 1e-9 ? b.Vol / b.Vma : 0;
                // TB-vol dài (KHÔNG gồm nến này) → tỉ lệ thanh khoản portable
                double liqMean = lq.Count > 0 ? liqSum / lq.Count : b.Vol;
                b.LiqRatio = liqMean > 1e-9 ? b.Vma / liqMean : 1.0;
                lq.Enqueue(b.Vol); liqSum += b.Vol;
                if (lq.Count > liqW) liqSum -= lq.Dequeue();
                ef = double.IsNaN(ef) ? b.C : ef + kf * (b.C - ef);
                es = double.IsNaN(es) ? b.C : es + ks * (b.C - es);
                b.Bias = ef > es + 3 * _tick ? 1 : ef < es - 3 * _tick ? -1 : 0;
                // xu hướng chậm (proxy TPO bias): close vs close TrendBars trước
                if (i >= TrendBars) { double d = b.C - B[i - TrendBars].C; b.Trend = d > TrendTolPts ? 1 : d < -TrendTolPts ? -1 : 0; }
                else b.Trend = 0;
                b.SinceGap = gap ? 0 : (i > 0 ? B[i - 1].SinceGap + 1 : 999);
            }
            return B;
        }

        private bool Gate(Bar b) => b.Vol >= VolFloor && b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;
        // Gate MỀM cho nến HỒI trong leg (2026-07-30): hồi vol thấp là DẤU HIỆU TỐT (không có bên
        // đối kháng), không phải nến rác — chỉ đòi cấu trúc (đã qua warm-up + đủ nền TB) để tiếp tục
        // theo dõi leg, KHÔNG đòi sàn volume của riêng nến đó. Nến VÀO (resume) vẫn phải qua Gate() đầy
        // đủ ở điều kiện entry — chỉ nến HỒI ở giữa được nới. Bug cũ: 1 nến hồi vol<sàn → `break` huỷ
        // TOÀN BỘ leg, bỏ sót nến tiếp diễn ngay sau đó dù đạt mọi điều kiện (vd 2026-07-29 23:57 vol=7
        // huỷ leg, bỏ sót entry 00:00 lãi +3R).
        private bool GateSoft(Bar b) => b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;
        // GATE chung (2026-07-28): thuận xu hướng (proxy TPO bias) + đúng phía VWAP + thanh khoản đủ
        private bool TrendOk(Bar b, int side) => !TrendFilter || b.Trend == side;
        private bool VwapOk(Bar b, int side) => !VwapAlign || (side > 0 ? b.C >= b.Vwap : b.C <= b.Vwap);
        private bool LiqOk(Bar b) => !LiquidityFilter || b.LiqRatio >= LiquidityRatio;

        // ================= dựng pool vùng (chỉ để hiển thị hợp lưu + info TP-vướng) =================
        private List<PZone> BuildPool(HistoricalData hd, List<Bar> B)
        {
            var pool = new List<PZone>();
            double rowStep = _tick * Math.Max(1, RowTicks);
            var sBlocks = SplitBlocks(hd, SessionGapMin);
            for (int i = 0; i < sBlocks.Count - 1; i++)
            {
                string lab = LabelOf(GetTime(hd, sBlocks[i].from));
                var sp = ProfileEngine.BuildProfile(hd, sBlocks[i].from, sBlocks[i].to, _tick, rowStep, true, 0, lab);
                if (!sp.Valid) continue;
                DateTime ready = GetTime(hd, sBlocks[i].to), exp = ready.AddDays(ZoneExpireDays);
                Add(pool, sp.Poc, $"POC {VN(lab)}", 70, ready, exp);
                Add(pool, sp.Vah, $"VAH {VN(lab)}", 58, ready, exp);
                Add(pool, sp.Val, $"VAL {VN(lab)}", 58, ready, exp);
                Add(pool, sp.High, $"Đỉnh {VN(lab)}", 52, ready, exp);
                Add(pool, sp.Low, $"Đáy {VN(lab)}", 52, ready, exp);
            }
            var dBlocks = ProfileEngine.GroupByGap(hd, DayGapMin);
            for (int i = 1; i < dBlocks.Count; i++)
            {
                var prev = ProfileEngine.BuildProfile(hd, dBlocks[i - 1].from, dBlocks[i - 1].to, _tick, rowStep, true, 0, "D");
                if (!prev.Valid) continue;
                DateTime ready = GetTime(hd, dBlocks[i].from), exp = ready.AddDays(1).AddHours(6);
                Add(pool, prev.Vah, "D-1 VAH", 66, ready, exp);
                Add(pool, prev.Val, "D-1 VAL", 66, ready, exp);
                Add(pool, prev.Poc, "D-1 POC", 72, ready, exp);
                Add(pool, prev.High, "D-1 Đỉnh", 60, ready, exp);
                Add(pool, prev.Low, "D-1 Đáy", 60, ready, exp);
            }
            return pool;
        }

        // ================= CORVEN: zone HVN tuần/ngày (chỉ dùng khi CorvenZoneAnchor=true) =================
        // W_CLOSED: HVN của tuần/ngày ĐÃ ĐÓNG có hiệu lực cho TOÀN BỘ tuần/ngày kế tiếp (nhân quả tuyệt đối,
        // khớp v8/runner/zones_corven.py::build_zone_series(causal='closed')). Dùng ProfileEngine.WeekSpans/
        // GroupByGap/RowsOver/FindHvn nguyên bản (đã có sẵn, chỉ đọc).
        private List<PZone> BuildCorvenZones(HistoricalData hd)
        {
            var zones = new List<PZone>();
            var wSpans = ProfileEngine.WeekSpans(hd, 30.0);
            for (int k = 1; k < wSpans.Count; k++)
            {
                var (fr, to) = wSpans[k - 1];
                var rows = ProfileEngine.RowsOver(hd, fr, to, _tick, true);
                var hvns = ProfileEngine.FindHvn(rows, _tick, minRatio: CorvenHvnMinRatio);
                DateTime ready = GetTime(hd, wSpans[k].fr), exp = ready.AddDays(8);
                foreach (var (price, ratio) in hvns.Take(Math.Max(1, CorvenHvnMaxN)))
                    zones.Add(new PZone { Price = price, Kind = $"HVN Tuần ×{ratio:0.0}", Strength = 0, ReadyTime = ready, ExpireTime = exp, IsWeek = true });
            }
            var dBlocks = ProfileEngine.GroupByGap(hd, DayGapMin);
            for (int k = 1; k < dBlocks.Count; k++)
            {
                var prev = dBlocks[k - 1];
                var rows = ProfileEngine.RowsOver(hd, prev.from, prev.to, _tick, true);
                var hvns = ProfileEngine.FindHvn(rows, _tick, minRatio: CorvenHvnMinRatio);
                DateTime ready = GetTime(hd, dBlocks[k].from), exp = ready.AddDays(2);
                foreach (var (price, ratio) in hvns.Take(Math.Max(1, CorvenHvnMaxN)))
                    zones.Add(new PZone { Price = price, Kind = $"HVN Ngày ×{ratio:0.0}", Strength = 0, ReadyTime = ready, ExpireTime = exp, IsWeek = false });
            }
            return zones;
        }

        // Danh sách gia CORVEN dang hoat dong tai thoi diem t, dung tang (tuan/ngay theo CorvenZoneTier)
        // + VWAP cua chinh tang do. Dung chung cho ca PLAY1 (cham->dao) va PLAY2 (pha->hoi->tiep).
        private List<double> ActiveCorvenPrices(List<PZone> corvenZones, Bar b, bool wantWeek)
        {
            var res = new List<double>();
            foreach (var z in corvenZones)
                if (z.IsWeek == wantWeek && b.Time >= z.ReadyTime && b.Time <= z.ExpireTime) res.Add(z.Price);
            res.Add(wantWeek ? b.VwapWeek : b.VwapDay);
            return res;
        }

        private static void Add(List<PZone> pool, double price, string kind, double str, DateTime ready, DateTime exp)
        {
            if (double.IsNaN(price) || price <= 0) return;
            pool.Add(new PZone { Price = price, Kind = kind, Strength = str, ReadyTime = ready, ExpireTime = exp });
        }

        private DateTime GetTime(HistoricalData hd, int i) => (hd[i, SeekOriginHistory.Begin] as HistoryItemBar)?.TimeLeft ?? DateTime.MinValue;

        private List<(int from, int to)> SplitBlocks(HistoricalData hd, int gapMin)
        {
            var res = new List<(int, int)>(); int n = hd.Count; if (n == 0) return res;
            int start = 0; DateTime prev = DateTime.MinValue; bool have = false; string curLab = null;
            for (int i = 0; i < n; i++)
            {
                if (hd[i, SeekOriginHistory.Begin] is not HistoryItemBar b) continue;
                string lab = LabelOf(b.TimeLeft);
                bool split = !have || lab != curLab || (b.TimeLeft - prev).TotalMinutes > gapMin;
                if (split) { if (have) res.Add((start, i - 1)); start = i; curLab = lab; }
                prev = b.TimeLeft; have = true;
            }
            if (have) res.Add((start, n - 1));
            return res;
        }

        // CORVEN PLAY2 tại MỘT cạnh (zp) cụ thể — BẢN SAO có chủ ý của logic phá/hồi/tiếp diễn bên dưới,
        // (rhi,rlo) truyền vào thay vì tính từ range co hẹp RangeLen. Duplicate CÓ CHỦ Ý (không refactor
        // dùng chung với Scan()) để KHÔNG chạm vào đường chạy mặc định khi CorvenZoneAnchor=false.
        private void ScanCbrAtEdge(List<Bar> B, List<Sig> raw, int i, Bar b, double rhi, double rlo, double slFloorT, double slCapT)
        {
            int nClosed = B.Count - 1;
            bool up = b.C > rhi + SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C > b.O;
            bool dn = b.C < rlo - SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C < b.O;
            if (!(up || dn)) return;
            int side = up ? +1 : -1;
            double edge = up ? rhi : rlo;
            double peak = up ? b.H : b.L; int since = i;
            int jEnd = Math.Min(nClosed, i + 1 + WaitBars);
            for (int j = i + 1; j < jEnd; j++)
            {
                var bj = B[j];
                if (!GateSoft(bj)) break;
                if (up ? bj.C < edge - HoldTolTicks * _tick : bj.C > edge + HoldTolTicks * _tick) break;
                if (j >= since + 1)
                {
                    double pullExt = up ? double.MaxValue : double.MinValue;
                    for (int k = since + 1; k <= j; k++) { if (up) { if (B[k].L < pullExt) pullExt = B[k].L; } else { if (B[k].H > pullExt) pullExt = B[k].H; } }
                    double leg = up ? (peak - edge) : (edge - peak);
                    double depth = up ? (peak - pullExt) : (pullExt - peak);
                    double retr = leg > 0 ? depth / leg : 0;
                    bool held = up ? pullExt >= edge - HoldTolTicks * _tick : pullExt <= edge + HoldTolTicks * _tick;
                    // ResumeVsa: xem chú thích ở nhánh CBR chuẩn — nến hồi yếu thì CHỜ nến khác, không huỷ leg.
                    bool resume = (up ? (bj.C > B[j - 1].H && bj.C > bj.O) : (bj.C < B[j - 1].L && bj.C < bj.O))
                                  && bj.Brat >= ResumeBody && bj.Vratio >= ResumeVsa;
                    if (j >= since + 2 && retr >= PullMin && retr <= PullMax && held && resume && Gate(bj))
                    {
                        double entry = bj.C, sl, risk;
                        if (up) { sl = pullExt - SlBuf * _tick; risk = (entry - sl) / _tick; }
                        else { sl = pullExt + SlBuf * _tick; risk = (sl - entry) / _tick; }
                        if (risk < slFloorT) { sl = up ? entry - slFloorT * _tick : entry + slFloorT * _tick; risk = slFloorT; }
                        if (risk > slCapT) return;
                        if (TrendOk(bj, side) && VwapOk(bj, side) && LiqOk(bj))
                            AddSig(raw, j, side, entry, sl, risk, RR, bj.Vratio, "CBR phá→hồi→tiếp diễn (CORVEN)",
                                new List<string> { $"mép {edge.ToString("0.0##")}", $"hồi {retr * 100:0}%", $"leg {leg:0.0}giá",
                                                   $"VSA vào {bj.Vratio:0.0}x{(bj.Vratio >= VsaClimax ? " tím" : "")}", $"VSA phá {b.Vratio:0.0}x" });
                        return;
                    }
                }
                if (up ? bj.H > peak : bj.L < peak) { peak = up ? bj.H : bj.L; since = j; }
            }
        }

        // ================= CBR: phá vùng co → hồi giữ leg → tiếp diễn (KHỚP entry_cbr.run_cbr) =================
        // CorvenZoneAnchor=true: THAY nguồn cạnh neo (PLAY2) — mỗi bar i, lặp qua TỪNG zone CORVEN đang
        // hoạt động (HVN tuần|ngày + VWAP tuần|ngày theo CorvenZoneTier) làm (rhi=rlo=zp) thay vì tính
        // range co hẹp RangeLen nến. Phần phá/hồi/tiếp diễn/GATE bên dưới giữ NGUYÊN 1-1 (khớp
        // v8/runner/cbr_hvn.py::run_zone). Khi TẮT (mặc định), nhánh else chạy ĐÚNG code gốc, không đổi.
        private List<Sig> Scan(HistoricalData hd, List<Bar> B, List<PZone> pool, List<PZone> corvenZones)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;                          // BỎ nến đang hình thành → không repaint
            double rangeMinT = RangeMinPts / _tick, rangeMaxT = RangeMaxPts / _tick;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick;
            bool corvenWeek = CorvenZoneTier == 0;

            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i];
                if (!Gate(b)) continue;
                if (CorvenZoneAnchor)
                {
                    if (corvenZones == null) continue;
                    foreach (double zp in ActiveCorvenPrices(corvenZones, b, corvenWeek))
                        ScanCbrAtEdge(B, raw, i, b, zp, zp, slFloorT, slCapT);
                    continue;
                }
                // CorvenZoneAdd: CỘNG THÊM (không continue) — mép HVN/VWAP tuần VÀ ngày là nguồn tín
                // hiệu BỔ SUNG, code range-nội-bộ gốc bên dưới vẫn chạy y hệt cho CÙNG nến i.
                if (CorvenZoneAdd && corvenZones != null)
                {
                    foreach (double zp in ActiveCorvenPrices(corvenZones, b, true))
                        ScanCbrAtEdge(B, raw, i, b, zp, zp, slFloorT, slCapT);
                    foreach (double zp in ActiveCorvenPrices(corvenZones, b, false))
                        ScanCbrAtEdge(B, raw, i, b, zp, zp, slFloorT, slCapT);
                }
                if (i < RangeLen) continue;
                double rhi = double.MinValue, rlo = double.MaxValue;
                for (int k = i - RangeLen; k < i; k++) { if (B[k].H > rhi) rhi = B[k].H; if (B[k].L < rlo) rlo = B[k].L; }
                double span = (rhi - rlo) / _tick;
                if (span > rangeMaxT || span < rangeMinT) continue;

                bool up = b.C > rhi + SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C > b.O;
                bool dn = b.C < rlo - SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C < b.O;
                if (!(up || dn)) continue;
                int side = up ? +1 : -1;
                double edge = up ? rhi : rlo;

                double peak = up ? b.H : b.L; int since = i;
                int jEnd = Math.Min(nClosed, i + 1 + WaitBars);
                for (int j = i + 1; j < jEnd; j++)
                {
                    var bj = B[j];
                    if (!GateSoft(bj)) break;
                    // đóng trở lại HẲN trong range → hủy leg
                    if (up ? bj.C < edge - HoldTolTicks * _tick : bj.C > edge + HoldTolTicks * _tick) break;

                    if (j >= since + 1)
                    {
                        double pullExt = up ? double.MaxValue : double.MinValue;
                        for (int k = since + 1; k <= j; k++) { if (up) { if (B[k].L < pullExt) pullExt = B[k].L; } else { if (B[k].H > pullExt) pullExt = B[k].H; } }
                        double leg = up ? (peak - edge) : (edge - peak);
                        double depth = up ? (peak - pullExt) : (pullExt - peak);
                        double retr = leg > 0 ? depth / leg : 0;
                        bool held = up ? pullExt >= edge - HoldTolTicks * _tick : pullExt <= edge + HoldTolTicks * _tick;
                        // ResumeVsa: gộp THẲNG vào `resume` (không `break`) ⇒ nến hồi yếu bị bỏ qua nhưng
                        // vòng lặp VẪN chạy tiếp → tìm được nến hồi khoẻ hơn trong cùng cửa sổ WaitBars.
                        bool resume = (up ? (bj.C > B[j - 1].H && bj.C > bj.O) : (bj.C < B[j - 1].L && bj.C < bj.O))
                                      && bj.Brat >= ResumeBody && bj.Vratio >= ResumeVsa;
                        if (j >= since + 2 && retr >= PullMin && retr <= PullMax && held && resume && Gate(bj))
                        {
                            double entry = bj.C, sl, risk;
                            if (up) { sl = pullExt - SlBuf * _tick; risk = (entry - sl) / _tick; }
                            else { sl = pullExt + SlBuf * _tick; risk = (sl - entry) / _tick; }
                            if (risk < slFloorT) { sl = up ? entry - slFloorT * _tick : entry + slFloorT * _tick; risk = slFloorT; }
                            if (risk > slCapT) break;
                            // GATE (thuận trend + đúng phía VWAP + thanh khoản) — 1 setup/range, filter-then-break khớp Python
                            if (TrendOk(bj, side) && VwapOk(bj, side) && LiqOk(bj))
                                // ⚠ SỬA 2026-08-02: trước đây truyền `b.Vratio` (VSA nến PHÁ) cho tín hiệu nằm
                                // ở nến j (nến VÀO) ⇒ cột VSA + cờ "tím" trong panel/CSV/Telegram mô tả nến
                                // PHÁ, không phải nến vào lệnh. Nay báo VSA của NẾN VÀO; VSA phá xuống lý do.
                                AddSig(raw, j, side, entry, sl, risk, RR, bj.Vratio, "CBR phá→hồi→tiếp diễn",
                                    new List<string> { $"phá {edge.ToString("0.0##")}", $"hồi {retr * 100:0}%", $"leg {leg:0.0}giá",
                                                       $"VSA vào {bj.Vratio:0.0}x{(bj.Vratio >= VsaClimax ? " tím" : "")}", $"VSA phá {b.Vratio:0.0}x" });
                            break;
                        }
                    }
                    // mở rộng đỉnh leg
                    if (up ? bj.H > peak : bj.L < peak) { peak = up ? bj.H : bj.L; since = j; }
                }
            }
            if (EnableReversal) raw.AddRange(ScanReversal(hd, B, pool, corvenZones));
            // Lọc phiên chết TRƯỚC dedup/cooldown. CHỈ cắt CBR — reversal MIỄN (verify 148 lệnh THẬT:
            // reversal trong khung chết 4/4 THẮNG +6R; cắt cả 2 nhánh +51R, chỉ cắt CBR +57R). Idx = nến vào.
            if (SkipDeadSession && DeadStartHour != DeadEndHour)
                raw.RemoveAll(s => !IsRev(s) && InDeadWindow(B[s.Idx].Time));
            return Cooldown_(Dedup(raw));
        }

        // Giờ rơi vào khung chết? v6: mặc định neo theo UTC (DeadUseUtc=true) vì khung chết là hiện
        // tượng gắn với giờ UTC/CME, không phải giờ địa phương của trader (xem giải thích ở khai báo
        // DeadUseUtc bên trên). Hỗ trợ khung qua nửa đêm (start > end).
        private bool InDeadWindow(DateTime tUtc)
        {
            int h = DeadUseUtc ? tUtc.Hour : tUtc.AddHours(TzOffset).Hour;
            return DeadStartHour <= DeadEndHour
                ? (h >= DeadStartHour && h < DeadEndHour)
                : (h >= DeadStartHour || h < DeadEndHour);
        }

        private void AddSig(List<Sig> raw, int idx, int side, double entry, double sl, double risk, double targetRr, double vsa, string scen, List<string> why)
        {
            raw.Add(new Sig { Idx = idx, Side = side, Scen = scen, Entry = entry, Sl = sl, RiskT = risk,
                Rr2 = RR, TargetRr = targetRr, Vsa = vsa, Climax = vsa >= VsaClimax, Why = why });
        }

        // ===== NHÁNH QUAY ĐẦU v2 — ĐẢO CHIỀU TẠI VWAP (2026-07-28, khớp reversal_vwap.py) =====
        // 4 setup thật của user ĐỀU neo VWAP (3/4) + phá-hụt + 1 nến xác nhận mạnh. Live CSV bác
        // gate cũ (climax/VSA-độ-lớn/co_vung VÔ NGHĨA; delta gate làm TỆ hơn) → BỎ hết, chỉ giữ:
        // VWAP + rút râu + đóng mạnh phía đảo + VSA≥RevVsaConf + đến-từ-đúng-phía + THUẬN trend.
        // TP = RevRR (1.5R — đảo chiều trần MFE ~1.3R, KHÁC runner 3R). SL ngoài cực trị/VWAP.
        // Absorption per-level (footprint LIVE) = BONUS nâng grade, KHÔNG bắt buộc (offline bác delta).
        // PLAY1 tại các zone CORVEN (HVN/VWAP) — dùng chung cho CorvenZoneAnchor (THAY) và CorvenZoneAdd
        // (CỘNG THÊM). BẢN SAO có chủ ý của khối cham→dao gốc, chỉ đổi nguồn vùng (zp thay vw phiên) +
        // thêm gate R2 (vị trí trong "range gần" 50 nến, khớp v8/runner/zone_engine.py::play1_raw).
        private void ScanRevAtZones(HistoricalData hd, List<Bar> B, List<Sig> raw, int i, Bar b, List<double> zps, double slFloorT, double slCapT, double corvenTol)
        {
            double rng = b.Rng; if (rng <= 0) return;
            int loK = Math.Max(0, i - 50);
            if (i - loK < 10) return;
            double locLo = double.MaxValue, locHi = double.MinValue;
            for (int k = loK; k < i; k++) { if (B[k].L < locLo) locLo = B[k].L; if (B[k].H > locHi) locHi = B[k].H; }
            double spanR2 = locHi - locLo;
            if (spanR2 <= 0) return;
            foreach (double zp in zps)
            {
                bool touchUp2 = b.H >= zp - corvenTol;
                bool touchDn2 = b.L <= zp + corvenTol;
                bool rejShort2 = b.UW >= WickFrac * rng && b.Cpos <= 0.45 && b.C < zp && b.Brat >= 0.30 && b.Vratio >= RevVsaConf;
                bool rejLong2 = b.LW >= WickFrac * rng && b.Cpos >= 0.55 && b.C > zp && b.Brat >= 0.30 && b.Vratio >= RevVsaConf;
                bool approUp2 = false, approDn2 = false;
                for (int k = Math.Max(0, i - RevApproachBars); k < i; k++)
                { if (B[k].C < zp) approUp2 = true; if (B[k].C > zp) approDn2 = true; }
                int side2 = 0; double anchor2 = 0;
                if (touchUp2 && rejShort2 && approUp2) { side2 = -1; anchor2 = Math.Max(b.H, zp + corvenTol); }
                else if (touchDn2 && rejLong2 && approDn2) { side2 = +1; anchor2 = Math.Min(b.L, zp - corvenTol); }
                if (side2 == 0) continue;
                double pos = (zp - locLo) / spanR2;
                if (side2 > 0 && pos > 0.25) continue;    // R2: LONG phai gan DAY range gan
                if (side2 < 0 && pos < 0.75) continue;    // R2: SHORT phai gan DINH range gan
                if (!TrendOk(b, side2)) continue;
                bool wall2 = Absorption(HdBar(hd, b.HdIdx), side2 > 0 ? b.L : b.H, side2) || (RevClimaxOverride && b.Vratio >= VsaClimax);
                EmitRev(raw, i, side2, b.C, anchor2, zp, b.Vratio, slFloorT, slCapT, wall2, corven: true);
            }
        }

        private List<Sig> ScanReversal(HistoricalData hd, List<Bar> B, List<PZone> pool, List<PZone> corvenZones)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick, tol = VwapTolTicks * _tick;
            double corvenTol = CorvenTolTicks * _tick;
            bool corvenWeek = CorvenZoneTier == 0;
            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i];
                if (!Gate(b)) continue;
                double rng = b.Rng; if (rng <= 0) continue;
                // CorvenZoneAnchor=true: THAY vung fade tu CHI VWAP phien sang HVN tuan|ngay + VWAP
                // tuan|ngay (PLAY1, khop v8/runner/zone_engine.py::play1_raw, confirm_on=False - ban
                // True cat n qua manh ma khong tang EV, xem RESULTS_RUNNER_ZONES.md). Them gate R2:
                // vung cham phai o cuc tri 25% cua "range gan" (50 nen truoc). Khi TAT, code goc ben
                // duoi chay KHONG DOI.
                if (CorvenZoneAnchor)
                {
                    if (corvenZones == null) continue;
                    var zps = ActiveCorvenPrices(corvenZones, b, corvenWeek);
                    ScanRevAtZones(hd, B, raw, i, b, zps, slFloorT, slCapT, corvenTol);
                    continue;
                }
                // CorvenZoneAdd: CỘNG THÊM (không continue) — vùng HVN/VWAP tuần VÀ ngày là nguồn tín
                // hiệu BỔ SUNG, code VWAP-phiên gốc bên dưới vẫn chạy y hệt cho CÙNG nến i.
                if (CorvenZoneAdd && corvenZones != null)
                {
                    var zpsAll = ActiveCorvenPrices(corvenZones, b, true);
                    zpsAll.AddRange(ActiveCorvenPrices(corvenZones, b, false));
                    ScanRevAtZones(hd, B, raw, i, b, zpsAll, slFloorT, slCapT, corvenTol);
                }
                double vw = b.Vwap;
                // SHORT: VWAP là KHÁNG CỰ — giá đẩy lên chạm VWAP rồi bị từ chối
                bool touchUp = b.H >= vw - tol;
                bool rejShort = b.UW >= WickFrac * rng && b.Cpos <= 0.45 && b.C < vw && b.Brat >= 0.30 && b.Vratio >= RevVsaConf;
                // LONG: VWAP là HỖ TRỢ — giá đạp xuống chạm VWAP rồi bật lên
                bool touchDn = b.L <= vw + tol;
                bool rejLong = b.LW >= WickFrac * rng && b.Cpos >= 0.55 && b.C > vw && b.Brat >= 0.30 && b.Vratio >= RevVsaConf;
                // bối cảnh: đến từ đúng phía (đẩy VÀO VWAP) trong RevApproachBars nến
                bool approUp = false, approDn = false;
                for (int k = Math.Max(0, i - RevApproachBars); k < i; k++)
                { if (B[k].C < vw) approUp = true; if (B[k].C > vw) approDn = true; }

                int side = 0; double anchor = 0;
                if (touchUp && rejShort && approUp) { side = -1; anchor = Math.Max(b.H, vw); }
                else if (touchDn && rejLong && approDn) { side = +1; anchor = Math.Min(b.L, vw); }
                if (side == 0) continue;
                if (RevRequireBodyDir && (side > 0 ? b.C <= b.O : b.C >= b.O)) continue;   // nến vào phải THUẬN màu
                if (!TrendOk(b, side)) continue;   // THUẬN trend (mua nhịp giảm trong uptrend / bán nhịp tăng trong downtrend)

                bool wall = Absorption(HdBar(hd, b.HdIdx), side > 0 ? b.L : b.H, side) || (RevClimaxOverride && b.Vratio >= VsaClimax);
                EmitRev(raw, i, side, b.C, anchor, vw, b.Vratio, slFloorT, slCapT, wall);
            }
            return raw;
        }

        private void EmitRev(List<Sig> raw, int i, int side, double entry, double anchor, double vw, double vsa, double slFloorT, double slCapT, bool wall, bool corven = false)
        {
            // SL TIGHT ở cực trị/VWAP (KHÔNG sàn 3 giá như CBR — user: "SL đặt ở VWAP thì đẹp"), cap slCapT
            double sl, risk;
            if (side > 0) { sl = anchor - SlBuf * _tick; risk = (entry - sl) / _tick; }
            else { sl = anchor + SlBuf * _tick; risk = (sl - entry) / _tick; }
            if (risk <= 5 || risk > slCapT) return;
            _ = slFloorT;
            var why = new List<string> { $"đảo chiều {(corven ? "vùng" : "VWAP")} {vw:0.0##}", side > 0 ? "rút râu dưới" : "rút râu trên", $"VSA {vsa:0.0}x{(vsa >= VsaClimax ? " tím" : "")}" };
            if (wall) why.Add("hấp thụ ✓");
            AddSig(raw, i, side, entry, sl, risk, RevRR, vsa, corven ? "quay đầu VWAP (CORVEN)" : "quay đầu VWAP", why);
        }

        // Tường hấp thụ per-level (footprint LIVE): tại cực trị có mức volume vượt trội + dominance
        // NGƯỢC chiều tiếp cận. side=+1 hấp thụ tại ĐÁY (mua đỡ), -1 tại ĐỈNH (bán đè). (port EntrySignal)
        private bool Absorption(HistoryItemBar bar, double extreme, int side)
        {
            var pl = bar?.VolumeAnalysisData?.PriceLevels;
            if (pl == null || pl.Count == 0) return false;
            double sum = 0; int c = 0;
            foreach (var kv in pl) { sum += kv.Value.Volume; c++; }
            if (c == 0) return false; double meanVol = sum / c;
            foreach (var kv in pl)
            {
                if (Math.Abs(kv.Key - extreme) > 3 * _tick) continue;
                double vol = kv.Value.Volume; if (vol < meanVol * 1.5) continue;
                double dNet = kv.Value.Delta; double dom = vol > 0 ? Math.Abs(dNet) / vol : 0;
                bool dirOk = side > 0 ? dNet < 0 : dNet > 0;
                if (dom >= AbsDom && dirOk) return true;
            }
            return false;
        }

        private HistoryItemBar HdBar(HistoricalData hd, int absIdx)
            => (absIdx >= 0 && absIdx < hd.Count) ? hd[absIdx, SeekOriginHistory.Begin] as HistoryItemBar : null;

        // gộp trùng cùng phía trong DedupBars nến (KHỚP entry_cbr.dedup)
        private List<Sig> Dedup(List<Sig> raw)
        {
            var outp = new List<Sig>();
            foreach (var s in raw.OrderBy(x => x.Idx))
                if (!outp.Any(m => m.Side == s.Side && Math.Abs(s.Idx - m.Idx) <= DedupBars)) outp.Add(s);
            return outp;
        }

        // cooldown mỗi phía (KHỚP entry_cbr.cooldown_filter)
        private List<Sig> Cooldown_(List<Sig> sig)
        {
            var outp = new List<Sig>(); var last = new Dictionary<int, int>();
            foreach (var s in sig.OrderBy(x => x.Idx))
            {
                if (s.Idx - last.GetValueOrDefault(s.Side, -999) < Cooldown) continue;
                outp.Add(s); last[s.Side] = s.Idx;
            }
            return outp;
        }

        private int ClusterCount(List<PZone> pool, DateTime t, double price)
        {
            var seen = new HashSet<long>();
            foreach (var z in pool)
            {
                if (t < z.ReadyTime || t > z.ExpireTime) continue;
                double zp = z.Price; if (double.IsNaN(zp) || zp <= 0) continue;
                if (Math.Abs(zp - price) / _tick > ConfluenceTol) continue;
                seen.Add((long)Math.Round(zp / _tick));
            }
            return seen.Count;
        }

        // vùng MẠNH (strength≥58) chắn đường tới TP → cách entry bao nhiêu R (info, KHÔNG gate)
        private double BlockRToTp(List<PZone> pool, Sig s)
        {
            double r = s.RiskT * _tick, best = double.NaN;
            double trr = s.TargetRr > 0 ? s.TargetRr : RR;
            double tp = s.Side > 0 ? s.Entry + trr * r : s.Entry - trr * r;
            foreach (var z in pool)
            {
                if (s.Time < z.ReadyTime || s.Time > z.ExpireTime || z.Strength < 58) continue;
                double p = z.Price; if (double.IsNaN(p) || p <= 0) continue;
                bool inPath = s.Side > 0 ? (s.Entry < p && p < tp) : (tp < p && p < s.Entry);
                if (!inPath) continue;
                double rr = Math.Abs(p - s.Entry) / r;
                if (double.IsNaN(best) || rr < best) best = rr;
            }
            return best;
        }

        private void Simulate(List<Bar> B, Sig s)
        {
            var b0 = B[s.Idx];
            s.Time = b0.Time;
            double r = s.RiskT * _tick;
            double rr = s.TargetRr > 0 ? s.TargetRr : RR;   // CBR=RR(3), quay đầu VWAP=RevRR(1.5)
            s.Tp1 = s.Side > 0 ? s.Entry + rr * r : s.Entry - rr * r; s.Tp2 = s.Tp1;
            for (int j = s.Idx + 1; j < B.Count; j++)
            {
                var b = B[j];
                bool hitSL = s.Side > 0 ? b.L <= s.Sl : b.H >= s.Sl;
                bool hitTP = s.Side > 0 ? b.H >= s.Tp1 : b.L <= s.Tp1;
                if (hitSL) { s.Outcome = "SL"; s.OutTime = b.Time; return; }
                if (hitTP) { s.Outcome = "TP"; s.OutTime = b.Time; return; }
            }
            s.Outcome = "running"; s.OutTime = B[B.Count - 1].Time;
        }

        // điền Cluster/Block/Grade sau khi có Time (gọi từ Process qua Simulate? — làm gọn: tính ở đây)
        private void Enrich(List<PZone> pool, Sig s)
        {
            s.Cluster = ClusterCount(pool, s.Time, s.Entry);
            s.BlockR = BlockRToTp(pool, s);
            s.Grade = s.Cluster >= MinConfluence ? 'A' : 'B';
            if (s.Cluster >= MinConfluence) s.Why.Add($"hợp lưu ×{s.Cluster}");
            if (!double.IsNaN(s.BlockR)) s.Why.Add($"TP vướng vùng ↧{s.BlockR:0.0}R");
        }

        // ================= CẦU NỐI MT5 =================
        // Process() quét LẠI TOÀN BỘ lịch sử mỗi nến mới → nếu gửi lệnh hồn nhiên ở đây sẽ bắn
        // hàng chục lệnh cũ vào tài khoản thật mỗi lần reload. 4 chốt chống trùng:
        //   1) chỉ xét tín hiệu ở nến VỪA ĐÓNG (Idx == B.Count-2; Scan đã bỏ nến đang hình thành)
        //   2) _armed: lần quét đầu sau attach/reload chỉ NẠP id, không gửi
        //   3) tuổi tín hiệu ≤ Mt5MaxAgeSec so với đồng hồ (bar.TimeLeft = mốc MỞ nến, UTC)
        //   4) id tất định (symbol|phút|hướng|nhánh) → EA lưu id đã xử lý ra file, restart không bắn lại
        private static bool IsRev(Sig s) => s.Scen != null && s.Scen.StartsWith("quay");

        private string SigId(Sig s) =>
            $"{Symbol?.Name ?? "X"}|{s.Time:yyyyMMddHHmm}|{(s.Side > 0 ? "B" : "S")}|{(IsRev(s) ? "R" : "C")}";

        private void EmitLive(List<Sig> sigs, List<Bar> B)
        {
            try
            {
                if (B.Count < 3) return;
                int lastClosed = B.Count - 2;
                double barMin = (B[B.Count - 1].Time - B[B.Count - 2].Time).TotalMinutes;
                if (barMin <= 0 || barMin > 60) barMin = 1;

                if (!_armed)
                {
                    foreach (var s0 in sigs) _sentIds.Add(SigId(s0));
                    _armed = true;
                    double skew = (DateTime.UtcNow - B[B.Count - 1].Time.AddMinutes(barMin)).TotalSeconds;
                    _bridgeStatus = $"nạp {_sentIds.Count} tín hiệu cũ (KHÔNG gửi) · lệch feed↔đồng hồ {skew:0}s";
                    return;
                }

                foreach (var s in sigs.Where(x => x.Idx == lastClosed))
                {
                    bool rev = IsRev(s);
                    string id = SigId(s);
                    if (_sentIds.Contains(id)) continue;
                    if (rev ? !Mt5SendRev : !Mt5SendCbr) { _sentIds.Add(id); continue; }
                    if (Mt5OnlyGradeA && s.Grade != 'A') { _sentIds.Add(id); continue; }

                    var closeUtc = s.Time.AddMinutes(barMin);
                    double age = (DateTime.UtcNow - closeUtc).TotalSeconds;
                    if (age > Mt5MaxAgeSec || age < -Mt5MaxAgeSec)
                    {
                        _sentIds.Add(id);
                        _bridgeStatus = $"BỎ {s.Time.AddHours(TzOffset):dd/MM HH:mm} — lệch đồng hồ {age:0}s (>{Mt5MaxAgeSec}s)";
                        continue;
                    }
                    WriteCmd(s, id, rev, closeUtc);
                    _sentIds.Add(id);
                }
            }
            catch (Exception ex) { _bridgeStatus = "LỖI cầu nối: " + ex.Message; }
        }

        private string Mt5FilesDir()
        {
            string dir = Mt5Dir?.Trim();
            if (!string.IsNullOrEmpty(dir)) return dir;
            return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                                "MetaQuotes", "Terminal", "Common", "Files");
        }

        // Hệ số nhân lot cho 1 tín hiệu. s.Vsa = VSA của NẾN VÀO LỆNH (đã sửa 2026-08-02 — trước đó
        // là VSA nến PHÁ, gate nhồi bằng số cũ sẽ vô nghĩa vì nến phá gần như luôn ≥2.0).
        private double NhoiSize(Sig s) => (NhoiMult > 1.0 && s.Vsa >= NhoiVsaGate) ? NhoiMult : 1.0;

        private void WriteCmd(Sig s, string id, bool rev, DateTime closeUtc)
        {
            var ci = CultureInfo.InvariantCulture;
            string dir = Mt5FilesDir();
            Directory.CreateDirectory(dir);
            string path = Path.Combine(dir, "runner_cmd.jsonl");

            double slDist = s.RiskT * _tick;
            double rr = s.TargetRr > 0 ? s.TargetRr : RR;
            double sizeMult = NhoiSize(s);
            var sb = new StringBuilder();
            sb.Append('{')
              .Append("\"id\":\"").Append(id).Append("\",")
              // ts_utc: GIỮ UTC — EA bên MT5 so với TimeGMT() để tính tuổi tín hiệu, đổi sẽ sai.
              // ts_local: mốc UTC+7 để người đọc/log dùng.
              .Append("\"ts_utc\":\"").Append(closeUtc.ToString("yyyy-MM-dd HH:mm:ss", ci)).Append("\",")
              .Append("\"ts_local\":\"").Append(closeUtc.AddHours(TzOffset).ToString("yyyy-MM-dd HH:mm:ss", ci)).Append("\",")
              .Append("\"tz\":").Append(TzOffset.ToString(ci)).Append(',')
              .Append("\"src\":\"").Append(Symbol?.Name ?? "?").Append("\",")
              .Append("\"branch\":\"").Append(rev ? "REV" : "CBR").Append("\",")
              .Append("\"side\":\"").Append(s.Side > 0 ? "BUY" : "SELL").Append("\",")
              .Append("\"sl_dist\":").Append(slDist.ToString("0.###", ci)).Append(',')
              .Append("\"rr\":").Append(rr.ToString("0.##", ci)).Append(',')
              .Append("\"grade\":\"").Append(s.Grade).Append("\",")
              .Append("\"vsa\":").Append(s.Vsa.ToString("0.00", ci)).Append(',')
              .Append("\"cluster\":").Append(s.Cluster.ToString(ci)).Append(',')
              .Append("\"size_mult\":").Append(sizeMult.ToString("0.##", ci)).Append(',')
              .Append("\"src_entry\":").Append(s.Entry.ToString("0.0##", ci)).Append(',')
              .Append("\"src_sl\":").Append(s.Sl.ToString("0.0##", ci)).Append(',')
              .Append("\"src_tp\":").Append(s.Tp1.ToString("0.0##", ci)).Append(',')
              .Append("\"dry\":").Append(Mt5DryRun ? "true" : "false")
              .Append("}\n");

            using (var fs = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite))
            using (var w = new StreamWriter(fs, new UTF8Encoding(false)))
                w.Write(sb.ToString());

            _bridgeSent++;
            _bridgeStatus = $"gửi {_bridgeSent} · {s.Time.AddHours(TzOffset):dd/MM HH:mm} {(s.Side > 0 ? "BUY" : "SELL")} "
                          + $"{(rev ? "QUAY ĐẦU" : "CBR")} SL {slDist:0.0}đ {rr:0.#}R{(Mt5DryRun ? " [DRY]" : "")}";
        }

        // ================= BÁO TELEGRAM (mở lệnh + đóng bởi SL/TP) =================
        // Cùng khung chống-trùng như cầu nối MT5, nhưng theo dõi CẢ vòng đời lệnh:
        //   • MỞ  : tín hiệu mới ở nến VỪA ĐÓNG + còn tươi (≤ TeleMaxAgeSec) → bắn 1 tin gọn.
        //   • ĐÓNG: khi Simulate() lật Outcome của lệnh ĐÃ báo mở sang TP/SL → bắn tin kết quả.
        // Lần quét đầu sau attach/reload: NẠP toàn bộ id (không bắn) để không spam lịch sử.
        private void ConfigTele()
        {
            _tele.Enabled = TeleAlerts;
            _tele.BotToken = (TeleBotToken ?? "").Trim();
            _tele.ChatId = (TeleChatId ?? "").Trim();
            _tele.TzOffset = TzOffset;
            _tele.TestNow = TeleTestNow;
            // log/telegram riêng của RunnerSignal (tách khỏi %LOCALAPPDATA%\TpoSuite của bộ TPO)
            _tele.ShareDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "RunnerSignal");
        }

        private void PollTeleTest()
        {
            ConfigTele();
            _tele.PollTestRaw($"🔔 TEST — Runner Signal ({Symbol?.Name ?? "?"}) bot chạy OK\n— mẫu tin MỞ: 🟢 MUA · CBR · hạng A · Entry/SL/TP\n— mẫu tin ĐÓNG (chạm TP/SL): ✅ WIN +{RR:0.#}R · giá vào→ra · thời lượng\n(nếu nhận được tin này = đường gửi OK; tin ĐÓNG sẽ tự bắn khi lệnh chạm TP/SL)");
        }

        private bool BranchOn(bool rev) => rev ? TeleSendRev : TeleSendCbr;

        private void EmitTele(List<Sig> sigs, List<Bar> B)
        {
            try
            {
                ConfigTele();
                if (B.Count < 3) return;
                int lastClosed = B.Count - 2;
                double barMin = (B[B.Count - 1].Time - B[B.Count - 2].Time).TotalMinutes;
                if (barMin <= 0 || barMin > 60) barMin = 1;

                if (!_teleArmed)
                {
                    foreach (var s0 in sigs)
                    {
                        string id0 = SigId(s0);
                        _teleSeen.Add(id0);
                        if (s0.Outcome != "running") _teleClosed.Add(id0);   // lệnh cũ đã đóng → không báo
                        else _teleOpenSent.Add(id0);   // FIX: lệnh đang chạy → coi như "đã mở" để CÒN báo ĐÓNG sau recalc (OnClear wipe _teleOpenSent giữa mở↔đóng)
                    }
                    _teleArmed = true;
                    _teleStatus = $"nạp {_teleSeen.Count} lệnh cũ (không báo) · sẵn sàng";
                    return;
                }

                foreach (var s in sigs)
                {
                    string id = SigId(s);
                    bool rev = IsRev(s);
                    bool ok = BranchOn(rev) && (!TeleOnlyGradeA || s.Grade == 'A');

                    // ---- MỞ lệnh ----
                    if (!_teleSeen.Contains(id))
                    {
                        if (TeleAlertOpen && ok && s.Idx == lastClosed)
                        {
                            var closeUtc = s.Time.AddMinutes(barMin);
                            double age = (DateTime.UtcNow - closeUtc).TotalSeconds;
                            if (age <= TeleMaxAgeSec && age >= -TeleMaxAgeSec)
                            {
                                _tele.SendRaw(ComposeOpen(s, rev));
                                _teleOpenSent.Add(id);
                                _teleSent++;
                                _teleStatus = $"MỞ {(s.Side > 0 ? "MUA" : "BÁN")} {(rev ? "quay đầu" : "CBR")} {s.Time.AddHours(TzOffset):HH:mm} · đã gửi {_teleSent}";
                            }
                        }
                        _teleSeen.Add(id);   // đánh dấu đã xử lý dù có bắn hay không → không lặp
                    }

                    // ---- ĐÓNG lệnh (chỉ báo lệnh ta ĐÃ báo mở) ----
                    if (TeleAlertClose && !_teleClosed.Contains(id) && _teleOpenSent.Contains(id)
                        && (s.Outcome == "TP" || s.Outcome == "SL"))
                    {
                        _tele.SendRaw(ComposeClose(s, rev));
                        _teleClosed.Add(id);
                        _teleSent++;
                        _teleStatus = $"ĐÓNG {(s.Outcome == "TP" ? "✓TP" : "✗SL")} {(s.Side > 0 ? "MUA" : "BÁN")} {s.OutTime.AddHours(TzOffset):HH:mm} · đã gửi {_teleSent}";
                    }
                }
            }
            catch (Exception ex) { _teleStatus = "LỖI Telegram: " + ex.Message; }
        }

        private string ComposeOpen(Sig s, bool rev)
        {
            double rr = s.TargetRr > 0 ? s.TargetRr : RR;
            double slPts = s.RiskT * _tick;
            double tpPts = slPts * rr;
            string dirVN = s.Side > 0 ? "🟢 MUA (LONG)" : "🔴 BÁN (SHORT)";
            string branch = rev ? "Quay đầu VWAP" : "CBR";
            string reason = rev ? "quay đầu (đảo chiều) tại VWAP"
                                 : "phá vùng co → hồi giữ gốc → vào nến tiếp diễn";
            var sb = new StringBuilder();
            sb.Append("🔔 LỆNH MỚI\n");
            sb.Append(dirVN).Append(" · Runner ").Append(branch).Append(" · hạng ").Append(s.Grade);
            if (NhoiSize(s) > 1) sb.Append("  ⚡NHỒI ×").Append(NhoiMult.ToString("0.#"));
            sb.Append('\n');
            sb.Append("Vào (Entry): ").Append(Fmt(s.Entry)).Append('\n');
            sb.Append("SL: ").Append(Fmt(s.Sl)).Append("  (").Append(slPts.ToString("0.0")).Append(" giá)\n");
            sb.Append("TP: ").Append(Fmt(s.Tp1)).Append("  (").Append(tpPts.ToString("0.0")).Append(" giá · ").Append(rr.ToString("0.#")).Append("R)\n");
            sb.Append("Lý do: ").Append(reason).Append('\n');
            if (s.Why != null && s.Why.Count > 0) sb.Append("• ").Append(string.Join(" · ", s.Why)).Append('\n');
            sb.Append("⏱ ").Append(s.Time.AddHours(TzOffset).ToString("HH:mm dd/MM"))
              .Append(" · ").Append(Symbol?.Name ?? "?");
            return sb.ToString();
        }

        private string ComposeClose(Sig s, bool rev)
        {
            bool win = s.Outcome == "TP";
            double rr = s.TargetRr > 0 ? s.TargetRr : RR;
            double exit = win ? s.Tp1 : s.Sl;
            string dirVN = s.Side > 0 ? "MUA (LONG)" : "BÁN (SHORT)";
            string branch = rev ? "Quay đầu VWAP" : "CBR";
            string head = win ? "✅ CHỐT LỜI (TP)" : "🛑 DỪNG LỖ (SL)";
            string rRes = win ? "+" + rr.ToString("0.#") + "R" : "-1.0R";
            var sb = new StringBuilder();
            sb.Append(head).Append(" · ").Append(dirVN).Append(" · Runner ").Append(branch).Append('\n');
            sb.Append("Kết quả: ").Append(rRes).Append('\n');
            sb.Append("Vào ").Append(Fmt(s.Entry)).Append(" → ra ").Append(Fmt(exit)).Append('\n');
            sb.Append("Mở ").Append(s.Time.AddHours(TzOffset).ToString("HH:mm"))
              .Append(" → đóng ").Append(s.OutTime.AddHours(TzOffset).ToString("HH:mm dd/MM"))
              .Append("  ·  ").Append(Dur(s.OutTime - s.Time));
            return sb.ToString();
        }

        private static string Dur(TimeSpan t)
        {
            if (t.TotalMinutes < 1) return "<1p";
            int h = (int)t.TotalHours, m = t.Minutes;
            return h > 0 ? $"{h}h{m:00}p" : $"{m}p";
        }

        // ================= XUẤT CSV (đối chiếu C#↔Python + tách WR nhánh CBR vs quay đầu) =================
        // Ghi TOÀN BỘ tín hiệu mỗi khi có nến mới (ghi đè cùng file). Cột nhanh=CBR/QUAY_DAU để soi 2 nhánh.
        // Tên file = tên panel + ngày hiện tại → mỗi ngày một file riêng, không ghi đè chồng ngày cũ.
        private static string SafeFileName(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s;
        }
        // MỌI mốc thời gian ghi ra file đều là UTC+TzOffset (mặc định UTC+7, giờ VN) —
        // KHÔNG dùng DateTime.Now (giờ máy) và KHÔNG ghi giờ UTC thô.
        private string DailyCsvName() => $"{SafeFileName("RUNNER CBR+VWAP (M1)")}_{DateTime.UtcNow.AddHours(TzOffset):yyyy-MM-dd}.csv";

        private void ExportSignals(List<Sig> sigs)
        {
            try
            {
                string path = ExportPath?.Trim();
                if (string.IsNullOrEmpty(path))
                    path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), DailyCsvName());
                else if (Directory.Exists(path))
                    path = Path.Combine(path, DailyCsvName());

                var ci = CultureInfo.InvariantCulture;
                var sb = new StringBuilder();
                // ngay_gio & ket_thuc_luc: giờ UTC+7 (VN)
                sb.Append("ngay_gio,nhanh,huong,entry,SL,risk_gia,TP,RR,VSA,climax,co_vung,grade,tp_vuong_vung,KQ,ket_thuc_luc,chi_tiet\n");
                foreach (var s in sigs.OrderBy(x => x.Idx))
                {
                    string nhanh = s.Scen != null && s.Scen.StartsWith("quay") ? "QUAY_DAU" : "CBR";
                    string huong = s.Side > 0 ? "LONG" : "SHORT";
                    string block = double.IsNaN(s.BlockR) ? "-" : s.BlockR.ToString("0.0", ci) + "R";
                    string kq = s.Outcome == "TP" ? "WIN" : s.Outcome == "SL" ? "LOSS" : "open";
                    string ct = "\"" + string.Join(" · ", s.Why ?? new List<string>()).Replace("\"", "'") + "\"";
                    sb.Append(s.Time.AddHours(TzOffset).ToString("yyyy-MM-dd HH:mm")).Append(',')
                      .Append(nhanh).Append(',').Append(huong).Append(',')
                      .Append(s.Entry.ToString("0.0##", ci)).Append(',')
                      .Append(s.Sl.ToString("0.0##", ci)).Append(',')
                      .Append((s.RiskT * _tick).ToString("0.0", ci)).Append(',')
                      .Append(s.Tp1.ToString("0.0##", ci)).Append(',')
                      .Append((s.TargetRr > 0 ? s.TargetRr : RR).ToString("0.#", ci)).Append(',')
                      .Append(s.Vsa.ToString("0.00", ci)).Append(',')
                      .Append(s.Climax ? "tim" : "-").Append(',')
                      .Append(s.Cluster.ToString(ci)).Append(',')
                      .Append(s.Grade).Append(',')
                      .Append(block).Append(',')
                      .Append(kq).Append(',')
                      .Append(s.OutTime.AddHours(TzOffset).ToString("yyyy-MM-dd HH:mm")).Append(',')
                      .Append(ct).Append('\n');
                }
                File.WriteAllText(path, sb.ToString(), new UTF8Encoding(true));
                _exportedTo = $"{sigs.Count} lệnh → {path}";
            }
            catch (Exception ex) { _exportedTo = "LỖI ghi CSV: " + ex.Message; }
        }

        private List<(double price, double strength, int side)> CurrentClusters(List<PZone> pool, DateTime now, double nowPrice)
        {
            var active = pool.Where(z => now >= z.ReadyTime && now <= z.ExpireTime && !double.IsNaN(z.Price) && z.Price > 0)
                             .Select(z => z.Price).OrderBy(x => x).ToList();
            var res = new List<(double, double, int)>(); int k = 0;
            while (k < active.Count)
            {
                int j = k; var grp = new List<double> { active[k] };
                while (j + 1 < active.Count && (active[j + 1] - grp[0]) / _tick <= ConfluenceTol) { grp.Add(active[j + 1]); j++; }
                if (grp.Count >= MinConfluence) { double c = grp.Average(); res.Add((c, Math.Min(100, 50 + grp.Count * 12), c > nowPrice ? -1 : 1)); }
                k = j + 1;
            }
            return res;
        }

        private List<(string, Color)> BuildPanel(List<Sig> sigs)
        {
            var p = new List<(string, Color)>();
            int running = sigs.Count(s => s.Outcome == "running");
            int tp = sigs.Count(s => s.Outcome == "TP"), sl = sigs.Count(s => s.Outcome == "SL");
            int closed = tp + sl;
            string wr = closed > 0 ? $" · WR {100.0 * tp / closed:0}%" : "";
            int nRev = sigs.Count(s => s.Scen != null && s.Scen.StartsWith("quay"));
            string deadTag = "";
            if (SkipDeadSession && DeadStartHour != DeadEndHour)
            {
                if (DeadUseUtc)
                {
                    int vnFrom = (DeadStartHour + TzOffset) % 24, vnTo = (DeadEndHour + TzOffset) % 24;
                    deadTag = $" · ⛔UTC{DeadStartHour:00}-{DeadEndHour:00}h (VN{vnFrom:00}-{vnTo:00}h)";
                }
                else deadTag = $" · ⛔VN{DeadStartHour:00}-{DeadEndHour:00}h";
            }
            p.Add(($"RUNNER CBR+VWAP (M1)   ▶{sigs.Count - nRev} ↩{nRev} · ✓{tp} ✗{sl} •{running}{wr}{deadTag}  [CBR {RR:0.#}R · quay đầu {RevRR:0.#}R]", Color.White));
            // Thống kê R lời/lỗ (TP=+RR nhánh đó, SL=−1R); + R khi nhồi nếu bật
            double totalR = 0, nhoiR = 0; int nNhoi = 0;
            foreach (var s in sigs)
            {
                double tr = (s.Scen != null && s.Scen.StartsWith("quay")) ? RevRR : RR;
                double dr = s.Outcome == "TP" ? tr : s.Outcome == "SL" ? -1 : 0;
                double m = NhoiSize(s);
                if (m > 1 && s.Outcome != "running") nNhoi++;
                totalR += dr; nhoiR += dr * m;
            }
            string rLine = closed > 0
                ? $"Lời/lỗ: {totalR:+0.0;-0.0}R (1 lot) · TB {totalR / closed:+0.00}R/lệnh ({closed} lệnh đóng)"
                  + (NhoiMult > 1 ? $" · nhồi ×{NhoiMult:0.#} khi VSA≥{NhoiVsaGate:0.#}: {nhoiR:+0.0;-0.0}R ({nNhoi} lệnh)" : "")
                : "Lời/lỗ: — (chưa có lệnh đóng)";
            p.Add((rLine, closed > 0 && totalR < 0 ? Color.FromArgb(240, 140, 140) : Color.FromArgb(120, 230, 150)));
            if (_vaTot > 0 && _vaCov < (int)(_vaTot * 0.98) && _vaFirst != DateTime.MinValue)
                p.Add(($"⚠ footprint chỉ có {_vaCov}/{_vaTot} nến (từ {_vaFirst:dd/MM HH:mm}) — tăng số bar Volume Analysis", Color.FromArgb(255, 190, 120)));
            if (ExportCsv && !string.IsNullOrEmpty(_exportedTo))
                p.Add(($"💾 CSV: {_exportedTo}", Color.FromArgb(150, 220, 150)));
            if (Mt5Bridge)
                p.Add((($"🔗 MT5{(Mt5DryRun ? " (DRY)" : " LIVE")}: " + (_bridgeStatus ?? "chờ nến mới…")),
                       Mt5DryRun ? Color.FromArgb(150, 200, 240) : Color.FromArgb(255, 170, 90)));
            if (TeleAlerts)
                p.Add((("📨 Tele: " + (_teleStatus ?? "chờ tín hiệu…")), Color.FromArgb(150, 210, 255)));
            var recent = sigs.OrderByDescending(s => s.Idx).Take(Math.Max(2, PanelRows)).ToList();
            if (recent.Count == 0) { p.Add(("(chưa có setup CBR)", Color.Gray)); return p; }
            foreach (var s in recent)
            {
                Color col = s.Side > 0 ? LongColor : ShortColor;
                string dir = s.Side > 0 ? "LONG" : "SHORT";
                string oc = s.Outcome == "TP" ? "✓" : s.Outcome == "SL" ? "✗" : "•";
                string tag = s.Scen != null && s.Scen.StartsWith("quay") ? "↩" : "▶";
                double rr = s.TargetRr > 0 ? s.TargetRr : RR;
                p.Add(($"{oc} {tag} {dir} {s.Grade} | E {Fmt(s.Entry)} SL {Fmt(s.Sl)} ({s.RiskT * _tick:0.0}giá) TP {Fmt(s.Tp1)} ({rr:0.#}R)", col));
                p.Add(($"    {string.Join(" · ", s.Why)}", Color.Silver));
            }
            return p;
        }

        // ================= RENDER (tái dùng từ EntrySignal) =================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null) return;   // KHÔNG chặn theo _vaLoaded: _render==null bên dưới đã đủ (xem fix mất panel ở OnUpdate)
            _drag.Attach(CurrentChart);
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;
            RenderState rs; lock (_sync) rs = _render;
            if (rs == null) return;
            var gr = args.Graphics; var conv = win.CoordinatesConverter; var clip = win.ClientRectangle;
            var prevClip = gr.ClipBounds; gr.SetClip(clip);
            try
            {
                gr.SmoothingMode = SmoothingMode.AntiAlias;
                if (ShowZones && rs.Clusters != null && rs.Clusters.Count > 0)
                {
                    using var fZ = new Font("Segoe UI", 8, FontStyle.Bold);
                    using var penZ = new Pen(ConflColor, Math.Max(1, ZoneLineWidth)) { DashStyle = DashStyle.Dash, DashPattern = new[] { 6f, 4f } };
                    foreach (var (price, strength, side) in rs.Clusters)
                    {
                        float y = (float)conv.GetChartY(price);
                        if (y < clip.Top || y > clip.Bottom) continue;
                        gr.DrawLine(penZ, clip.Left, y, clip.Right, y);
                        Chip(gr, fZ, clip.Left + 2, y, "⬥ HỢP LƯU " + price.ToString("0.0##"), ConflColor, false);
                    }
                }
                if (ShowSignals && rs.Sigs != null)
                {
                    using var fLbl = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    using var fChip = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    var dash = DashedSlTp ? DashStyle.Dash : DashStyle.Solid;
                    foreach (var s in rs.Sigs)
                    {
                        bool active = s.Outcome == "running";
                        if (!active && !ShowClosed) continue;
                        float xE = (float)conv.GetChartX(s.Time);
                        float xEnd = active ? clip.Right : (float)conv.GetChartX(s.OutTime);
                        if (xEnd > clip.Right) xEnd = clip.Right;
                        if (xEnd < xE + 10) xEnd = xE + 10;
                        if (xEnd < clip.Left || xE > clip.Right) continue;
                        float yE = (float)conv.GetChartY(s.Entry), ySL = (float)conv.GetChartY(s.Sl), yTP = (float)conv.GetChartY(s.Tp1);
                        float yTop = Math.Min(ySL, yTP), yBot = Math.Max(ySL, yTP);
                        if (yBot < clip.Top || yTop > clip.Bottom) continue;
                        Color dir = s.Side > 0 ? LongColor : ShortColor;
                        float xb = Math.Max(xE, clip.Left); float bw = Math.Max(1, xEnd - xb);
                        int fillA = active ? Math.Max(18, RiskBoxOpacity) : Math.Max(10, RiskBoxOpacity / 2);
                        int lineA = active ? 255 : 150;
                        if (ShowRiskBox)
                        {
                            using (var bt = new SolidBrush(Color.FromArgb(fillA, TpLineColor)))
                                gr.FillRectangle(bt, xb, Math.Min(yE, yTP), bw, Math.Abs(yTP - yE));
                            using (var bs = new SolidBrush(Color.FromArgb(fillA, SlLineColor)))
                                gr.FillRectangle(bs, xb, Math.Min(yE, ySL), bw, Math.Abs(ySL - yE));
                        }
                        if (ShowLines)
                        {
                            using (var pt = new Pen(Color.FromArgb(lineA, TpLineColor), LineWidth) { DashStyle = dash }) gr.DrawLine(pt, xb, yTP, xEnd, yTP);
                            using (var ps = new Pen(Color.FromArgb(lineA, SlLineColor), LineWidth) { DashStyle = dash }) gr.DrawLine(ps, xb, ySL, xEnd, ySL);
                            using (var pe = new Pen(Color.FromArgb(lineA, dir), LineWidth + 0.5f)) gr.DrawLine(pe, xb, yE, xEnd, yE);
                            using (var pv = new Pen(Color.FromArgb(active ? 220 : 110, dir), 1.5f)) gr.DrawLine(pv, xE, yTop, xE, yBot);
                        }
                        if (yE >= clip.Top - 6 && yE <= clip.Bottom + 6)
                        {
                            using (var bd = new SolidBrush(active ? dir : Color.FromArgb(210, dir))) gr.FillEllipse(bd, xE - 4.5f, yE - 4.5f, 9, 9);
                            using (var pw = new Pen(Color.FromArgb(active ? 255 : 190, Color.White), 1.4f)) gr.DrawEllipse(pw, xE - 4.5f, yE - 4.5f, 9, 9);
                        }
                        if (ShowArrows) DrawArrow(gr, xE, yE, s.Side, active ? dir : Color.FromArgb(180, dir), Math.Max(4, active ? ArrowSize : ArrowSize - 2));
                        if (ShowLabels)
                        {
                            string br = s.Scen != null && s.Scen.StartsWith("quay") ? "↩VWAP" : "▶CBR";
                            string lbl = (s.Side > 0 ? "LONG " : "SHORT ") + s.Grade + (s.Cluster >= MinConfluence ? " ×" + s.Cluster : "") + (active ? " · " + br : "");
                            LabelBox(gr, fLbl, xE + 10, s.Side > 0 ? yBot + 4 : yTop - 20, lbl, active ? dir : Color.FromArgb(210, dir));
                        }
                        if (active && ShowChips)
                        {
                            Chip(gr, fChip, clip.Right, yE, "E " + Fmt(s.Entry), dir, true);
                            Chip(gr, fChip, clip.Right, ySL, "SL " + Fmt(s.Sl) + " (" + (s.RiskT * _tick).ToString("0.0") + "giá)", SlLineColor, true);
                            Chip(gr, fChip, clip.Right, yTP, "TP " + Fmt(s.Tp1) + "  " + (s.TargetRr > 0 ? s.TargetRr : RR).ToString("0.#") + "R", TpLineColor, true);
                        }
                        else if (!active)
                        {
                            string mk = s.Outcome == "TP" ? "✓" : "✗";
                            using var bf = new SolidBrush(s.Outcome == "TP" ? TpLineColor : SlLineColor);
                            gr.DrawString(mk, fLbl, bf, xEnd - 3, (s.Outcome == "TP" ? yTP : ySL) - 8);
                        }
                    }
                }
                if (ShowPanel && rs.Panel != null && rs.Panel.Count > 0)
                {
                    using var f = new Font("Consolas", FontSize, FontStyle.Regular);
                    _drag.Draw(gr, f, rs.Panel, Math.Clamp(PanelOpacity, 100, 255), PanelCorner, clip);
                }
            }
            catch { /* nuốt lỗi vẽ */ }
            finally { gr.SetClip(prevClip); }
        }

        private static GraphicsPath Round(float x, float y, float w, float h, float r)
        {
            var p = new GraphicsPath(); float d = r * 2;
            p.AddArc(x, y, d, d, 180, 90); p.AddArc(x + w - d, y, d, d, 270, 90);
            p.AddArc(x + w - d, y + h - d, d, d, 0, 90); p.AddArc(x, y + h - d, d, d, 90, 90);
            p.CloseFigure(); return p;
        }
        private static Color TextOn(Color bg)
            => (0.299 * bg.R + 0.587 * bg.G + 0.114 * bg.B) > 150 ? Color.FromArgb(20, 20, 24) : Color.White;

        private void Chip(Graphics gr, Font f, float x, float yMid, string text, Color bg, bool anchorRight)
        {
            var sz = gr.MeasureString(text, f);
            float pad = 5, h = sz.Height + 3, w = sz.Width + 2 * pad;
            float bx = anchorRight ? x - w : x;
            float by = yMid - h / 2;
            using var path = Round(bx, by, w, h, 4);
            using (var b = new SolidBrush(bg)) gr.FillPath(b, path);
            using var tb = new SolidBrush(TextOn(bg));
            gr.DrawString(text, f, tb, bx + pad, by + 1);
        }

        private void LabelBox(Graphics gr, Font f, float x, float y, string text, Color accent)
        {
            var sz = gr.MeasureString(text, f);
            float pad = 4, w = sz.Width + 2 * pad, h = sz.Height + 2;
            using (var bg = new SolidBrush(Color.FromArgb(210, 18, 18, 22))) { using var p = Round(x, y, w, h, 3); gr.FillPath(bg, p); }
            using (var bd = new Pen(Color.FromArgb(180, accent), 1f)) { using var p = Round(x, y, w, h, 3); gr.DrawPath(bd, p); }
            using var tb = new SolidBrush(accent);
            gr.DrawString(text, f, tb, x + pad, y + 1);
        }

        private void DrawArrow(Graphics gr, float x, float yE, int side, Color col, float sz)
        {
            var tri = side > 0
                ? new[] { new PointF(x, yE + sz + 6), new PointF(x - sz, yE + sz * 2 + 6), new PointF(x + sz, yE + sz * 2 + 6) }
                : new[] { new PointF(x, yE - sz - 6), new PointF(x - sz, yE - sz * 2 - 6), new PointF(x + sz, yE - sz * 2 - 6) };
            using (var b = new SolidBrush(col)) gr.FillPolygon(b, tri);
            using (var pn = new Pen(Color.FromArgb(230, 255, 255, 255), 1.3f)) gr.DrawPolygon(pn, tri);
        }

        private sealed class RenderState
        {
            public List<Sig> Sigs;
            public List<(double price, double strength, int side)> Clusters;
            public List<(string text, Color col)> Panel;
            public int Digits;
        }
    }
}
