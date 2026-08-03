// ============================================================================
//  WyckoffRunner  —  Tín hiệu RUNNER CBR (Consolidation→Break→Retest→Resume) M1 (QUANTOWER)
// ============================================================================
//  Clone của RunnerSignal.cs (v5 đang chạy live) để nâng cấp theo lời pro trader CORVEN mà
//  không đụng bản đang ship. Mô hình LITERAL rút từ 6 setup thật: "phá VÙNG CO, chờ HỒI (giữ
//  trên gốc phá), VÀO nến TIẾP DIỄN". TP giữ runner. KHÁC con scalp EntrySignal (phá vùng→
//  retest, 1.5R) — đây là chiến lược riêng, chạy song song, DLL riêng.
//
//  Neo = RANGE nội bộ (RangeLen nến trước, span trong [RangeMin..RangeMax] = vùng
//  co hẹp thật, KHÔNG phải zone profile). BREAK = nến đóng vượt cạnh range + VSA
//  climax(≥2.0) + thân mạnh + nền SẠCH (không vừa quét hụt ngược — xem BREAK SẠCH v6).
//  HOLD = trong WaitBars nến giá hồi nhưng GIỮ (không đóng lại hẳn trong range). RESUME =
//  nến đóng vượt cực trị nhịp hồi → vào tại close. SL = cực trị nhịp hồi ± buf (sàn 3đ,
//  trần 7đ). Chỉ bắn NẾN ĐÃ ĐÓNG (không repaint).
//
//  Logic KHỚP research/wyckoff/cbr_v6.py (backtest thanh khoản 5-7/2026, dxFeed GCQ26; số
//  chuẩn = research/wyckoff/final_table.py). Vùng hợp lưu (co_vung) và TP-vướng-vùng CHỈ là
//  info hiển thị. Build: build-wyckoff.sh (concat ProfileEngine).
//
//  === NÂNG CẤP 2026-07-28 (đối chiếu live CSV 140 lệnh + 9 tháng data + 4 setup đảo chiều) ===
//  Phát hiện: nhánh cũ QUAY ĐẦU LỖ (-6R, WR23%, gate climax/VSA/co_vung VÔ NGHĨA); CBR
//  thắng theo XU HƯỚNG, thua NGƯỢC (thg6 crash -550 → LONG -19R). Bốn cải tiến ĐO ĐƯỢC:
//   1) LỌC THUẬN XU HƯỚNG (proxy TPO bias, close vs close ~8h): thg6 -16R→+5R, net +18→+35R,
//      MỌI THÁNG DƯƠNG. EMA30/120 quá nhanh → dùng lookback chậm.
//   2) RETRACE 60-90% (nâng sàn hồi): WR 30→33% (hồi sâu = runner thật).
//   3) VÀO ĐÚNG PHÍA VWAP + LỌC THANH KHOẢN (vma ≥ 0.75× TB dài): WR 33→37%, giữ net.
//   4) QUAY ĐẦU XÂY LẠI quanh VWAP (4 setup user đều neo VWAP): bỏ gate vô nghĩa, chỉ giữ
//      VWAP + rút râu + đóng mạnh + VSA≥1.8 + THUẬN trend; TP 1.5R (đảo chiều trần ~1.3R,
//      KHÔNG phải 3R). Kết quả: WR 23→56%, -6R→+10R. Absorption footprint = bonus HIỂN THỊ
//      "hấp thụ ✓" (KHÔNG nâng grade — grade chỉ do Cluster>=MinConfluence quyết định).
//  Portfolio (CBR@3R + Quay đầu@1.5R): WR ~39%, +48R/3 tháng, cả 3 tháng dương. (Số v5, xem
//  BASELINE.md cho số v6 đã sửa parity — đừng trộn 2 bộ số.)
//
//  === v6 (2026-07-29, xem WYCKOFF_V6_PLAN.md + research/wyckoff/BASELINE.md) ===
//  Sửa lỗi khung giờ chết cắt NHẦM (neo giờ hiển thị → no-op tuyệt đối; sửa neo UTC —
//  DeadUseUtc). Thêm BREAK SẠCH (CleanBreak/NoCounterSweep): bỏ cú phá ngay sau quét hụt
//  cạnh đối diện (Wyckoff Phase B chưa qua D). PullMax 0.90→1.00. RR 3.0→4.0. Trên nền v6
//  (sạch, dxFeed GCQ26 5-7/2026, chỉ nhánh CBR): n 77→33, WR 37.7%→48.5% (hoặc 57.6% ở RR3),
//  MDD 11R→3R. Nhánh QUAY_DAU giữ nguyên logic v2 (2026-07-28), chỉ dọn comment/label sai
//  (RevApproachBars/Cooldown/SlCapPts không ràng buộc reversal — xem input tương ứng).
//
//  === v7 (2026-07-29) — SAU CỔNG AUDIT GĐ8. Đọc research/wyckoff/AUDIT_V7.md trước khi sửa. ===
//  Cổng audit (Opus xhigh, 12 hướng phản biện) phán quyết:
//    · KB1 (CBR phá→hồi→tiếp diễn) = PASS CÓ ĐIỀU KIỆN → nhánh DUY NHẤT được cấp vốn.
//      Cố bác bằng 8 hướng không bác được: Monte Carlo 3000 lần vào-lệnh-ngẫu-nhiên cùng hình học
//      rủi ro cho p=0.0003; sống sau Bonferroni ×94 cấu hình (p=0.028); 18/18 trục tham số không có
//      "đỉnh nhọn"; cả hai phía dương (LONG EV+1.143 / SHORT +1.632); sống tới >40 tick phí/lệnh.
//    · KB2 (QUAY ĐẦU tại VWAP) = FAIL → EnableReversal MẶC ĐỊNH TẮT (xem comment tại input 66).
//    · KB3 (scalp biên↔biên trong range) = FAIL/KILL → KHÔNG CÓ DÒNG CODE NÀO trong file này.
//      Chết ở 2 tick phí (EV −0.036R), 0 range VALID trong 6 tháng OOS. Đừng "thêm lại cho đủ 3".
//  Hai feature v7 từng thiết kế (RangeMode=1 range cấu trúc, BIAS_ON bias phiên TPO) đều KHÔNG PASS
//  ⟹ KHÔNG port vào đây. Cấu hình đóng băng = AUDIT_V7.md §14, khớp 27/27 tham số với file này.
//
//  ⚠⚠ GIỚI HẠN BẰNG CHỨNG — đọc trước khi cấp vốn (AUDIT_V7 §7, BASELINE.md §0):
//  KHÔNG có MỘT điểm dữ liệu out-of-sample nào cho toàn bộ dự án. Cửa sổ OOS 2025-11→2026-04 chỉ có
//  171 nến qua gate trên 6 tháng (0,33% so với 52.160 nến của 3 tháng in-sample) ⟹ n=0. 100% số liệu
//  đến từ MỘT cửa sổ 3 tháng, MỘT regime (vàng tạo đỉnh), MỘT hợp đồng (GCQ26).
//  ⟹ Kỳ vọng dùng để TÍNH VỐN là +0.7R/lệnh (đầu dưới), KHÔNG phải +1.424R của in-sample.
//  ⟹ Log live là phép OOS ĐẦU TIÊN. Trước khi có nó: "đủ để thử vốn nhỏ + ghi log", KHÔNG phải
//     "hệ thống đã được xác nhận".
// ============================================================================
namespace WyckoffRunner
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Drawing.Drawing2D;
    using System.Globalization;
    using System.IO;
    using System.Linq;
    using System.Reflection;
    using System.Text;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;
    using TradingPlatform.BusinessLayer.Native;
    using TpoSuite;   // ProfileEngine + PanelDrag (concat)

    public class WyckoffRunner : Indicator, IVolumeAnalysisIndicator
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
        public double PullMax { get; set; } = 1.00;   // v6: nới 0.90→1.00 (hồi về sát gốc phá vẫn hợp lệ, miễn
                                                      // GIỮ vùng). dxFeed 5-7/26: n 30→36, WR 53→56%, +34→+44R.
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
        public double SlCapPts { get; set; } = 7.0;   // v6: tự kiểm sweep 6.0→99.9 giá trên nhánh QUAY_DAU
                                                       // (n=27 mọi mức từ 6.0 trở lên) — không ràng buộc cho
                                                       // reversal (SL reversal luôn ngắn, neo VWAP/cực trị).
                                                       // Có tác dụng thật cho CBR.
        [InputParameter("SL đệm ngoài cực trị hồi (tick)", 62, 0, 20, 1, 0)]
        public int SlBuf { get; set; } = 2;
        [InputParameter("RR mục tiêu (TP, giữ runner)", 63, 1, 8, 0.5, 1)]
        public double RR { get; set; } = 4.0;   // v6: 3.0→4.0. "Sl càng ngắn thì tỉ lệ lệnh tp 5-6R càng nhiều"
                                                // (CORVEN). Sweep dxFeed 5-7/26 đơn điệu tăng tới 8R; chọn 4.0 vì
                                                // giữ WR 50% + MDD 3R. RR5 = +66R nhưng WR 47%, MDD 5R.
        [InputParameter("Cooldown mỗi phía (số nến)", 64, 0, 60, 1, 0)]
        public int Cooldown { get; set; } = 15;   // v6: tự kiểm sweep 5→30 trên nhánh QUAY_DAU (n=27) — ra
                                                   // ĐÚNG cùng 27 lệnh mọi giá trị → không ràng buộc cho
                                                   // reversal (mẫu quá thưa để chạm ngưỡng). Có tác dụng thật
                                                   // cho CBR (chưa sweep riêng).
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
                                                          // v6: NO-OP trên dxFeed 5-7/2026 (0 lệnh khác biệt
                                                          // bật/tắt) — "phá lên+thuận trend" gần như luôn ở
                                                          // trên VWAP phiên. Giữ bật (có thể khác trên live/
                                                          // cửa sổ khác), nhưng ĐỪNG tính đây là 1 lớp lọc
                                                          // đã chứng minh — xem BASELINE.md §4.
        [InputParameter("Lọc thanh khoản (vma ≥ k×TB dài)", 48)]
        public bool LiquidityFilter { get; set; } = true; // COMEX/US session > Á mỏng (portable, không hardcode giờ)
        [InputParameter("Thanh khoản: k (× TB dài)", 49, 0.0, 3.0, 0.05, 2)]
        public double LiquidityRatio { get; set; } = 0.75;
        [InputParameter("Thanh khoản: cửa sổ TB (số nến)", 43, 100, 5000, 50, 0)]
        public int LiquidityWindow { get; set; } = 1000;

        // ---------- BREAK SẠCH (v6 — luật W3/W5 của CORVEN: "đừng đánh UT sớm, sang D mới đánh") ----------
        // Cơ chế: nếu ngay TRƯỚC cú phá, thị trường vừa có một cú QUÉT HỤT cạnh ĐỐI DIỆN (đâm thủng cực trị
        // cục bộ rồi đóng ngược lại vào trong) thì giá đang XOAY 2 CHIỀU (Wyckoff Phase B) → cú phá kế tiếp
        // phần lớn là bẫy. Chỉ nhận cú phá từ nền SẠCH (một chiều) = đã sang Phase D.
        // Bằng chứng (dxFeed 5-7/2026, chia đôi CÙNG 58 lệnh baseline thành 2 nhóm rời nhau):
        //   nhóm SẠCH           n=30  WR 53.3%  +34R  EV +1.13  MDD 3R  — dương cả 3 tháng
        //   nhóm CÓ QUÉT NGƯỢC  n=28  WR 32.1%   +8R  EV +0.29  MDD 9R  — tháng 6 ÂM
        // Ổn định theo tham số: look 15–25 & w 4–6 đều cho +44..+56R. Không phải điểm cực trị lẻ.
        [InputParameter("BREAK SẠCH: bỏ cú phá ngay sau quét hụt ngược (v6)", 33)]
        public bool CleanBreak { get; set; } = true;
        [InputParameter("Sạch: số nến soi ngược lại", 34, 5, 60, 1, 0)]
        public int CleanLook { get; set; } = 20;
        [InputParameter("Sạch: cửa sổ cực trị cục bộ", 35, 2, 15, 1, 0)]
        public int CleanWin { get; set; } = 5;
        [InputParameter("Sạch: nến quét phải đóng lại ≥ (vị trí đóng)", 36, 0.2, 0.9, 0.05, 2)]
        public double CleanClosePos { get; set; } = 0.50;

        // ---------- Lọc PHIÊN CHẾT (research 140 lệnh THẬT 2026-07-28, v6 sửa lại 2026-07-29) ----------
        // Khung UTC 02–08 (≈ giờ CME nghỉ/settlement quanh 17-18h ET, KHÔNG phải giờ hiển thị): CBR ở khung
        // này WR 9.7%, −19R, XẤU cả 3 tháng. CHỈ cắt CBR (reversal khung này 4/4 THẮNG +6R trong UTC 02–08
        // → MIỄN): WR 37.7→47.3%, +39→+49R.
        // v6 FIX: bản trước neo khung theo giờ HIỂN THỊ (tUtc + TzOffset) — với TzOffset=7 mặc định, việc
        // này cắt nhầm UTC [19:00,01:00) thay vì [02:00,08:00), một khung đã bị lọc thanh khoản làm rỗng sẵn
        // → bộ lọc là NO-OP tuyệt đối trên baseline, khối lỗ thật ở UTC 02–08 KHÔNG bị chặn. DeadUseUtc=true
        // neo trực tiếp theo UTC — bền với TzOffset và DST vì khung chết là hiện tượng THỊ TRƯỜNG (giờ sàn),
        // không phải giờ người dùng nhìn thấy trên chart.
        // Mặc định BẬT — đã validate trên CSV LIVE C# (cùng engine, không phải proxy), robust cả 3 tháng.
        // Tắt ô này nếu muốn so A/B với bản không lọc.
        [InputParameter("Lọc phiên chết: BỎ lệnh CBR khung giờ chết (mặc định BẬT)", 77)]
        public bool SkipDeadSession { get; set; } = true;
        [InputParameter("Phiên chết: tính theo giờ UTC (v6 — bền TzOffset/DST, khuyến nghị BẬT)", 72)]
        public bool DeadUseUtc { get; set; } = true;
        [InputParameter("Phiên chết: giờ BẮT ĐẦU (UTC nếu DeadUseUtc, ngược lại giờ hiển thị, 0-23)", 78, 0, 23, 1, 0)]
        public int DeadStartHour { get; set; } = 2;
        [InputParameter("Phiên chết: giờ KẾT THÚC (không gồm, UTC nếu DeadUseUtc, 0-24)", 79, 0, 24, 1, 0)]
        public int DeadEndHour { get; set; } = 8;

        // ---------- QUAY ĐẦU v2 — đảo chiều tại VWAP (2026-07-28, khớp reversal_vwap.py) ----------
        // ⚠ v7/GĐ8: MẶC ĐỊNH TẮT. AUDIT_V7.md §13 phán quyết nhánh này = FAIL, KHÔNG cấp vốn:
        //   · null vào-lệnh-ngẫu-nhiên: EV quan sát +0.389 = đúng p95 của null ⟹ p=0.072 (không có ý nghĩa)
        //   · sau hiệu chỉnh ≥61 cấu hình: p → >1
        //   · tách phía (chưa từng báo cáo ở GĐ6): LONG EV chỉ +0.154R (n=13) — gần bằng 0. Toàn bộ
        //     8.5R/10.5R đến từ SHORT trong regime "vàng tạo đỉnh" ⟹ rất có thể là regime, không phải edge.
        //   · điểm dữ liệu OOS duy nhất tồn tại: n=9, WR 33%, EV −0.167R
        // BẬT LẠI CHỈ ĐỂ THU LOG OOS (không cấp vốn thật) — xem BASELINE.md §0.
        [InputParameter("Bật nhánh QUAY ĐẦU (đảo chiều tại VWAP) — v7: TẮT, chưa được cấp vốn", 66)]
        public bool EnableReversal { get; set; } = false;
        [InputParameter("Quay đầu: RR mục tiêu (TP) — đảo chiều trần ~1.3R", 67, 1.0, 4.0, 0.25, 2)]
        public double RevRR { get; set; } = 1.5;
        [InputParameter("Quay đầu: VSA xác nhận tối thiểu", 68, 1.0, 4.0, 0.1, 1)]
        public double RevVsaConf { get; set; } = 1.8;
        [InputParameter("Quay đầu: dung sai chạm VWAP (tick)", 74, 2, 40, 1, 0)]
        public int VwapTolTicks { get; set; } = 12;
        [InputParameter("Quay đầu: số nến tiếp cận VWAP", 75, 2, 20, 1, 0)]
        public int RevApproachBars { get; set; } = 6;   // v6: tự kiểm sweep 1→999 nến — ra ĐÚNG cùng 27 lệnh
                                                         // mọi giá trị = TAUTOLOGY, KHÔNG lọc gì. Lý do: gate
                                                         // rejShort/rejLong đã ép C so VWAP, mà VWAP là TB
                                                         // tích luỹ chậm → "tiếp cận đúng phía" trong appro
                                                         // nến gần như luôn tự thoả. Giữ input để không đổi
                                                         // hành vi ngoài phạm vi plan; muốn thật sự lọc phải
                                                         // THIẾT KẾ LẠI điều kiện bối cảnh, không chỉnh số nến.
        [InputParameter("Quay đầu: rút râu ≥ (rau/range)", 69, 0.3, 1.0, 0.05, 2)]
        public double WickFrac { get; set; } = 0.50;
        // v6 FIX comment: AbsDom/RevClimaxOverride KHÔNG nâng Grade (đã lầm tưởng). Grade thật chỉ do
        // `s.Grade = s.Cluster >= MinConfluence ? 'A' : 'B'` (xem Enrich) — `wall` chỉ được Why.Add("hấp
        // thụ ✓") làm bonus HIỂN THỊ, không đọc vào Grade. Đối chiếu CSV live: 21/28 lệnh QUAY_DAU có tag
        // "hấp thụ ✓" nhưng grade = 27 B / 1 A. Vì per-level không backtest offline được nên KHÔNG biến
        // đây thành gate quyết định grade — giữ nguyên là bonus hiển thị.
        [InputParameter("Hấp thụ per-level (footprint LIVE) = bonus hiển thị 'hấp thụ ✓'", 76, 0.3, 1.0, 0.05, 2)]
        public double AbsDom { get; set; } = 0.60;
        [InputParameter("Quay đầu: climax tím = bonus hiển thị 'hấp thụ ✓' (KHÔNG nâng grade)", 73)]
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

        // ---------- lọc / warm-up ----------
        [InputParameter("Sàn volume (chống nến mỏng)", 70, 0, 500, 1, 0)]
        public int VolFloor { get; set; } = 20;
        [InputParameter("Warm-up sau gap (số nến)", 71, 0, 60, 1, 0)]
        public int WarmupBars { get; set; } = 20;

        // ---------- SƠ ĐỒ WYCKOFF (Range + Phase A-E + sự kiện SC/AR/ST/Spring/SOS/LPS...) ----------
        // Tu dong nhan dien Trading Range (tich luy/phan phoi) + Phase A-E + su kien chuan Wyckoff
        // (PS/SC/AR/ST/Spring/Shakeout/Test/SOS/LPS cho tich luy; PSY/BCLX/AR/ST/UT/UTAD/SOW/LPSY cho
        // phan phoi). CHI hien thi/giao duc — KHONG gate bat ky tin hieu CBR/QUAY DAU nao o tren.
        // Nguon quy tac: data-export/wyckoff/THEORY.md (dinh nghia goc) + CHART_CASES.md (9 loi gan
        // nhan hay gap tu bai chua hoc vien that, dung lam rang buoc thiet ke — vd Spring BAT BUOC la
        // day THAP NHAT toan bo Trading Range, SOS/SOW phai pha canh TUYET DOI cua range chu khong phai
        // dinh cuc bo, ranh gioi Phase neo theo GIA DONG). Prototype + kiem tra truc quan tren du lieu
        // that: research/wyckoff/v8/wyckoff/wyckoff_schematic.py + render_schematic_preview.py.
        // ⚠ Day la HEURISTIC (nguong CLIMAX_RANGE_MULT/ST_TOL_TICKS/... tu dat, tai lieu goc khong cho
        // so) — dung de HOC/doi chieu chart, KHONG dung lam gate vao lenh (giong bai hoc W3 da bi bac bo).
        [InputParameter("Wyckoff: hiện sơ đồ Range + Phase A-E + sự kiện", 150)]
        public bool ShowWyckoffSchematic { get; set; } = true;
        // 2026-08-03: TRƯỚC ĐÂY mặc định 6 → người dùng "chỉ thấy range mới nhất", không soi lại được
        // các range quá khứ để tự chấm. Nay mặc định 40 (trần 300) + có DANH SÁCH RANGE bấm để nhảy chart.
        [InputParameter("Wyckoff: số Range gần nhất hiển thị", 151, 1, 300, 1, 0)]
        public int WyckoffMaxRanges { get; set; } = 40;
        [InputParameter("Wyckoff: mở KÍNH LÚP khi nháy đúp range (xem tách khỏi chart)", 155)]
        public bool WyInspector { get; set; } = true;
        [InputParameter("Wyckoff: màu Range Tích luỹ", 152)]
        public Color WyAccColor { get; set; } = Color.FromArgb(0x4C, 0xAF, 0x50);
        [InputParameter("Wyckoff: màu Range Phân phối", 153)]
        public Color WyDistColor { get; set; } = Color.FromArgb(0xE5, 0x39, 0x35);
        [InputParameter("Wyckoff: màu vạch chia Phase", 154)]
        public Color WyPhaseColor { get; set; } = Color.FromArgb(150, 150, 220);

        /// <summary>v4: đủ 4 pattern. Tái tích luỹ / tái phân phối dùng cùng gam nhưng nhạt hơn;
        /// range chưa biết hướng phá (còn ở Phase A-C) tô xám.</summary>
        private Color WyKindColor(WyRangeR r) => r.Kind switch
        {
            "ACC" => WyAccColor,
            "DIST" => WyDistColor,
            "RE-ACC" => Color.FromArgb(0x8B, 0xC3, 0x4A),
            "RE-DIST" => Color.FromArgb(0xFF, 0x70, 0x43),
            _ => Color.FromArgb(0x78, 0x90, 0x9C),
        };

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
        [InputParameter("Bảng: số dòng THẤY của danh sách LỆNH (cuộn được)", 88, 2, 30, 1, 0)]
        public int PanelRows { get; set; } = 4;
        [InputParameter("Bảng: số dòng THẤY của danh sách WYCKOFF RANGE (cuộn được)", 89, 2, 30, 1, 0)]
        public int RangeListRows { get; set; } = 5;
        [InputParameter("Bảng: bề ngang (px)", 86, 360, 1400, 10, 0)]
        public int PanelWidth { get; set; } = 700;
        [InputParameter("Bảng: bấm vào dòng → nhảy chart tới vị trí đó", 97)]
        public bool ClickToNavigate { get; set; } = true;
        [InputParameter("Bảng: nhảy chart kèm chỉnh zoom cho vừa range", 98)]
        public bool NavZoomFit { get; set; } = true;
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
        // Đo trên cấu hình đang ship (đã bật ResumeVsa=0.8), dxFeed 05-07/2026, WyckoffRunner RR4+sạch:
        //   VSA vào [0.8,1.2) EV +1.500 · [1.2,1.8) +1.500 · [1.8,2.2) +1.500 · [2.2,∞) +3.000 (WR 80%)
        // Nhồi ×5 theo từng ngưỡng (tổng R / sụt vốn tối đa / tỷ số R trên sụt vốn):
        //   không nhồi   +39R  MDD 2.0R
        //   ≥1.5        +155R  MDD 6.0R  25.8
        //   ≥1.8        +111R  MDD 6.0R  18.5
        //   ≥2.2         +99R  MDD 5.0R  19.8  ← chọn (trùng `VsaClimax` sẵn có, không đẻ hằng số mới)
        //   ≥2.5         +83R  MDD 5.0R  16.6
        // ⚠ TRUNG THỰC: nhóm được nhồi chỉ có n=5 trong 3 tháng. Mẫu quá nhỏ để tin con số — coi 2.2 là
        // mặc định hợp lý, không phải kết luận. (Ngưỡng 1.5 cho tổng R cao nhất nhưng nhồi hơn nửa số
        // lệnh, tức gần như nhồi phẳng — không còn là "chọn lệnh mạnh".)
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
        private readonly UiPanel _ui = new();
        // --- yêu cầu nhảy chart đang chạy (vòng lặp kín qua nhiều khung hình, xem UiNav) ---
        private readonly UiNav _nav = new();
        private string _inspectKey;                 // range đang mở kính lúp (null = đóng)
        private bool _apiDumped;

        public WyckoffRunner() : base()
        {
            Name = "Wyckoff Runner (CBR M1, v6)";
            Description = "Runner CBR M1 v6: phá vùng co (nền SẠCH) → chờ hồi giữ leg → vào nến tiếp diễn (TP mặc định 4R). Bắn nến đóng. Cần Volume Analysis. Add vào chart M1.";
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
            _ui.Detach();
            _nav.Cancel(); _inspectKey = null;
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
                // cùng thư mục %LOCALAPPDATA%\WyckoffRunner với tele_log.txt (xem ConfigTele)
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WyckoffRunner");
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
        }

        private sealed class Sig
        {
            public int Idx; public DateTime Time; public int Side;
            public int HdIdx = -1;       // chi so trong HistoricalData (de bang bam-nhay-chart dinh vi)
            public string Scen; public char Grade; public double Entry, Sl, Tp1, Tp2, RiskT, Rr2, TargetRr;
            public int Cluster;          // số vùng chồng quanh giá vào (info, KHÔNG gate)
            public double BlockR;        // TP-vướng-vùng mạnh: cách entry bao nhiêu R (NaN = không vướng)
            public double Vsa; public bool Climax; public List<string> Why = new();
            public string Outcome = "running";
            public DateTime OutTime;
        }

        // ================= SƠ ĐỒ WYCKOFF — kiểu dữ liệu (xem input ShowWyckoffSchematic) =================
        // Noi bo (dung Idx de tinh toan trong ScanWyckoff — B la ephemeral, khong luu giua cac lan Process)
        // v2 (2026-08-03, theo WYCKOFF_DRAW_SPEC.md): them WyShockStatus/WyPendingShock cho co che CR-I
        // (xac nhan/that bai shock Spring/Shakeout/UT/UTAD) va Status tren WyEvent de renderer ve marker
        // theo trang thai (dac=Confirmed, dut net=Pending, rong xam=Failed).
        private enum WyShockStatus { None, Pending, Confirmed, Failed }
        private sealed class WyEvent { public int Idx; public string Label; public double Price; public WyShockStatus Status = WyShockStatus.None; }
        private sealed class WyPendingShock
        {
            public double Price; public double TargetEdge; public double Peak; public WyEvent Ev;
            public int Dir;            // v4: +1 = shock huong len (Spring/Shakeout) | -1 = xuong (UTAD)
            public double OutEdge;     // bien PHU doi dien — SOS/SOW phai but qua moi tinh la manh
            public bool LpsDone;       // v4: LPS[C]/LPSY[C] chi danh dau DUNG 1 diem
            public int StartIdx;
        }
        // v4: theo doi mot cu pha bien dang dien ra (state "B_brk") de biet no la Spring/Shakeout
        // (quay lai trong range) hay la SOS/SOW that (dong cua han o ngoai).
        private sealed class WyBreak
        {
            public int Side;           // -1 = pha canh duoi | +1 = pha canh tren
            public int StartIdx; public double Ext; public int ExtIdx;
            public int Hold; public double VMax; public double Out0;
        }
        private sealed class WyPhaseSeg { public char Phase; public int StartIdx; public int EndIdx = -1; }
        private sealed class WyRange
        {
            public int StartIdx; public int EndIdx = -1;   // -1 = dang chay (active)
            // v4 (review muc 5): huong MOVE truoc climax chi quyet dinh LOAI CLIMAX, KHONG quyet dinh
            // range se pha ve huong nao -> tach lam 2 truong. Xem WyKind() cho du 4 pattern.
            public bool OriginDown;                          // true = move GIAM bi SC chan | false = move TANG bi BCLX chan
            public int Dir;                                  // 0 chua biet | +1 pha LEN | -1 pha XUONG
            public double Low, High;                         // bien PHU (net dut) — cuc tri xa nhat
            public double SolidLow, SolidHigh;               // bien CHINH (net lien) — CO DINH sau Phase A
            public bool SolidSet;
            public string State = "A";                       // A|A_st|B|B_brk|C_pending|END
            public bool Completed;
            public List<WyEvent> Events = new();
            public List<WyPhaseSeg> Phases = new();
            public WyPendingShock Pending;                    // != null chi khi State=="C_pending"
            public WyBreak Brk;                               // != null chi khi State=="B_brk"
            // v3 (review nguoi hoc 2026-08-03): cac MUC CO DINH de VE — bien chinh la muc climax va
            // muc AR (net lien); bien lam viec rong hon ve net dut.
            public double ClimaxPrice;
            public int ArIdx = -1; public double ArPrice;
            public int StaIdx = -1; public double StaPrice;   // ST[A] = lan doi huong thu 3
            public int MoveIdx = -1; public double MoveLen, MoveEff;
            public double StExt; public int StExtIdx = -1;    // cuc tri tam trong luc cho ST[A]
        }
        /// <summary>v4: ten range theo DU 4 pattern — chi chot duoc khi da biet huong pha (Dir).</summary>
        private static string WyKind(bool originDown, int dir)
        {
            if (dir > 0) return originDown ? "ACC" : "RE-ACC";
            if (dir < 0) return originDown ? "RE-DIST" : "DIST";
            return originDown ? "ACC?" : "DIST?";
        }
        private static string WyKindVn(string k) => k switch
        {
            "ACC" => "Tích luỹ",
            "RE-ACC" => "Tái tích luỹ",
            "DIST" => "Phân phối",
            "RE-DIST" => "Tái phân phối",
            _ => "Chưa rõ",
        };
        // Render DTO (B[idx].Time/gia da chot san — dung duoc trong OnPaintChart du B khac lan).
        // v3 (2026-08-03): moi phan tu mang THEM chi so HistoricalData (HdIdx) — can cho (a) bang danh
        // sach bam-de-nhay-chart, (b) KINH LUP tu ve lai range bang chi so nen (khong qua CoordinatesConverter).
        private sealed class WyEventR { public DateTime Time; public int HdIdx; public double Price; public string Label; public WyShockStatus Status; }
        private sealed class WyPhaseSegR { public char Phase; public DateTime StartTime; public DateTime EndTime; public int StartHd, EndHd; }
        private sealed class WyRangeR
        {
            public DateTime StartTime, EndTime; public double Low, High;
            public string Kind = "ACC?";                      // v4: ACC | RE-ACC | DIST | RE-DIST | ACC? | DIST?
            public bool Up;                                   // huong pha (hoac gia thuyet ban dau) — dung chon mau
            public double SolidLow, SolidHigh;                // v3: bien chinh (climax + AR) — ve net lien
            public int StartHd, EndHd;
            public bool Completed;
            public string Key = "";
            public List<WyEventR> Events = new();
            public List<WyPhaseSegR> Phases = new();
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
                    var sigs = Scan(hd, B, pool);
                    foreach (var s in sigs) { Simulate(B, s); Enrich(pool, s); s.HdIdx = B[s.Idx].HdIdx; }

                    if (ExportCsv) ExportSignals(sigs);
                    if (Mt5Bridge) EmitLive(sigs, B);
                    if (TeleAlerts) EmitTele(sigs, B);

                    int minIdx = B.Count - 1 - DisplayBars;
                    var show = ShowAllHistory ? sigs : sigs.Where(s => s.Idx >= minIdx || s.Outcome == "running").ToList();

                    double now = B[B.Count - 1].C;
                    var clusters = CurrentClusters(pool, B[B.Count - 1].Time, now);

                    List<WyRangeR> wyRanges = null;
                    if (ShowWyckoffSchematic)
                    {
                        var wyRaw = ScanWyckoff(B);
                        wyRaw.Sort((x, y) => x.StartIdx.CompareTo(y.StartIdx));
                        if (wyRaw.Count > WyckoffMaxRanges) wyRaw = wyRaw.GetRange(wyRaw.Count - WyckoffMaxRanges, WyckoffMaxRanges);
                        wyRanges = wyRaw.Select(x => WyToRender(B, x)).ToList();
                    }

                    lock (_sync) _render = new RenderState
                    {
                        Sigs = show, Clusters = clusters, Panel = BuildPanel(show), Digits = _digits, WyRanges = wyRanges,
                        EntryRows = BuildEntryRows(show), RangeRows = BuildRangeRows(wyRanges), TotalBars = n,
                    };
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
                cum += b.Delta; b.Cum = cum;
                q.Enqueue(b.Vol); rollSum += b.Vol;
                if (q.Count > VsaPeriod) rollSum -= q.Dequeue();
                b.Vma = q.Count > 0 ? rollSum / q.Count : b.Vol;
                b.Vratio = b.Vma > 1e-9 ? b.Vol / b.Vma : 0;
                // TB-vol dài → tỉ lệ thanh khoản portable.
                // v7/GĐ9 SỬA PARITY: trước đây C# lấy trung bình của Vol (khối lượng thô) và KHÔNG gồm nến
                // hiện tại; Python `add_liqbase()` (entry_dxfeed.py) lấy trung bình của VMA và CÓ gồm nến
                // hiện tại. Đã đo trên 103.857 nến: 363 nến (0,35%) ra quyết định LIQ khác nhau, lệch tương
                // đối trung vị 0,41% (max 84,7% ở đầu chuỗi khi cửa sổ còn ngắn). Trên 5–7/2026 việc này
                // KHÔNG đổi tín hiệu nào (33/33 khớp cả hai cách) — nhưng vẫn sửa cho khớp Python từng dòng,
                // vì "không đổi trên cửa sổ này" không có nghĩa là không đổi trên dữ liệu live.
                lq.Enqueue(b.Vma); liqSum += b.Vma;
                if (lq.Count > liqW) liqSum -= lq.Dequeue();
                double liqMean = lq.Count > 0 ? liqSum / lq.Count : b.Vol;
                b.LiqRatio = liqMean > 1e-9 ? b.Vma / liqMean : 1.0;
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
        // Gate MỀM cho nến HỒI trong leg (2026-07-30, khớp fix RunnerSignal.cs): hồi vol thấp là DẤU
        // HIỆU TỐT, không phải nến rác — chỉ đòi cấu trúc, KHÔNG đòi sàn volume riêng nến đó. Nến VÀO
        // (resume) vẫn qua Gate() đầy đủ ở điều kiện entry. Bug cũ: 1 nến hồi vol thấp → break huỷ leg.
        private bool GateSoft(Bar b) => b.SinceGap >= WarmupBars && b.Vma >= VolFloor * 0.6;
        // GATE chung (2026-07-28): thuận xu hướng (proxy TPO bias) + đúng phía VWAP + thanh khoản đủ
        private bool TrendOk(Bar b, int side) => !TrendFilter || b.Trend == side;

        /// <summary>
        /// BREAK SẠCH (v6). Trả về true nếu trong <see cref="CleanLook"/> nến TRƯỚC nến phá (chỉ số i)
        /// KHÔNG có cú quét hụt cạnh ĐỐI DIỆN — tức nền một chiều, cú phá đáng tin.
        /// "Quét hụt" cho cú phá LÊN = có nến đâm thủng đáy cục bộ (thấp nhất <see cref="CleanWin"/> nến
        /// ngay trước nó) rồi ĐÓNG lại trên đáy đó và đóng ở nửa trên thân nến. Gương lại cho phá XUỐNG.
        /// Chỉ dùng nến ĐÃ ĐÓNG trước i → không nhìn trộm tương lai.
        /// </summary>
        private bool NoCounterSweep(List<Bar> B, int i, bool up)
        {
            if (!CleanBreak) return true;
            int from = Math.Max(VsaPeriod, i - CleanLook) + CleanWin;
            for (int k = from; k < i; k++)
            {
                var b = B[k];
                if (b.Rng <= 0) continue;
                if (k - CleanWin < 0) continue;
                if (up)
                {
                    double loc = double.MaxValue;
                    for (int m = k - CleanWin; m < k; m++) if (B[m].L < loc) loc = B[m].L;
                    if (b.L < loc - _tick && b.C > loc && b.Cpos >= CleanClosePos) return false;
                }
                else
                {
                    double loc = double.MinValue;
                    for (int m = k - CleanWin; m < k; m++) if (B[m].H > loc) loc = B[m].H;
                    if (b.H > loc + _tick && b.C < loc && b.Cpos <= 1.0 - CleanClosePos) return false;
                }
            }
            return true;
        }
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

        // ================= CBR: phá vùng co → hồi giữ leg → tiếp diễn (KHỚP entry_cbr.run_cbr) =================
        private List<Sig> Scan(HistoricalData hd, List<Bar> B, List<PZone> pool)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;                          // BỎ nến đang hình thành → không repaint
            double rangeMinT = RangeMinPts / _tick, rangeMaxT = RangeMaxPts / _tick;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick;

            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i];
                if (!Gate(b)) continue;
                if (i < RangeLen) continue;
                double rhi = double.MinValue, rlo = double.MaxValue;
                for (int k = i - RangeLen; k < i; k++) { if (B[k].H > rhi) rhi = B[k].H; if (B[k].L < rlo) rlo = B[k].L; }
                double span = (rhi - rlo) / _tick;
                if (span > rangeMaxT || span < rangeMinT) continue;

                bool up = b.C > rhi + SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C > b.O;
                bool dn = b.C < rlo - SlBuf * _tick && b.Vratio >= BreakVsa && b.Brat >= BreakBody && b.C < b.O;
                if (!(up || dn)) continue;
                if (!NoCounterSweep(B, i, up)) continue;   // v6: nền phải SẠCH (không vừa quét hụt ngược)
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
                            // ⚠ SỬA 2026-08-02: TRƯỚC ĐÂY truyền `b.Vratio` (VSA của nến PHÁ) cho tín hiệu
                            // nằm ở nến j (nến VÀO). Hệ quả: cột VSA + cờ "tím" trong panel/CSV/Telegram
                            // mô tả NẾN PHÁ chứ không phải nến vào lệnh — nên log toàn 2.2-5.6x "tím" trong
                            // khi nến vào trên chart lại nhỏ (trung vị thật 1.04x). Nay báo VSA của NẾN VÀO,
                            // VSA nến phá chuyển xuống dòng lý do.
                            if (TrendOk(bj, side) && VwapOk(bj, side) && LiqOk(bj))
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
            if (EnableReversal) raw.AddRange(ScanReversal(hd, B, pool));
            // Lọc phiên chết TRƯỚC dedup/cooldown. CHỈ cắt CBR — reversal MIỄN: trong khung UTC 02–08 (khung
            // ĐÚNG sau fix v6), reversal là 4 THẮNG/0 THUA +6R — miễn trừ có cơ sở. (Trước fix, khung C# cắt
            // nhầm UTC 19–01 khiến reversal trong khung đó ra 4W/4L +2R — tệ hơn phần ngoài khung — nên lúc
            // đó luận cứ "miễn vì reversal thắng" chưa đúng; nay đã đúng vì khung cắt đã đổi sang UTC 02–08.)
            // Idx = nến vào.
            if (SkipDeadSession && DeadStartHour != DeadEndHour)
                raw.RemoveAll(s => !IsRev(s) && InDeadWindow(B[s.Idx].Time));
            return Cooldown_(Dedup(raw));
        }

        // Giờ rơi vào khung chết? v6: mặc định neo theo UTC (DeadUseUtc=true) vì khung chết là hiện tượng
        // THỊ TRƯỜNG (CME nghỉ/settlement), không phải giờ hiển thị của user — neo theo giờ hiển thị sẽ sai
        // ngay khi đổi TzOffset hoặc vào DST (xem comment ở khối input phía trên). Hỗ trợ khung qua nửa đêm.
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
        private List<Sig> ScanReversal(HistoricalData hd, List<Bar> B, List<PZone> pool)
        {
            var raw = new List<Sig>();
            int nClosed = B.Count - 1;
            double slFloorT = SlFloorPts / _tick, slCapT = SlCapPts / _tick, tol = VwapTolTicks * _tick;
            for (int i = VsaPeriod + 2; i < nClosed; i++)
            {
                var b = B[i];
                if (!Gate(b)) continue;
                double rng = b.Rng; if (rng <= 0) continue;
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

        private void EmitRev(List<Sig> raw, int i, int side, double entry, double anchor, double vw, double vsa, double slFloorT, double slCapT, bool wall)
        {
            // SL TIGHT ở cực trị/VWAP (KHÔNG sàn 3 giá như CBR — user: "SL đặt ở VWAP thì đẹp"), cap slCapT
            double sl, risk;
            if (side > 0) { sl = anchor - SlBuf * _tick; risk = (entry - sl) / _tick; }
            else { sl = anchor + SlBuf * _tick; risk = (sl - entry) / _tick; }
            if (risk <= 5 || risk > slCapT) return;
            _ = slFloorT;
            var why = new List<string> { $"đảo chiều VWAP {vw:0.0##}", side > 0 ? "rút râu dưới" : "rút râu trên", $"VSA {vsa:0.0}x{(vsa >= VsaClimax ? " tím" : "")}" };
            if (wall) why.Add("hấp thụ ✓");
            AddSig(raw, i, side, entry, sl, risk, RevRR, vsa, "quay đầu VWAP", why);
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

        // ================= SƠ ĐỒ WYCKOFF — engine nhận diện (khớp research/wyckoff/v8/wyckoff/
        // wyckoff_schematic.py — Python chạy TRƯỚC trên dxFeed GCQ26 M1 để kiểm logic bằng ảnh trước
        // khi port; xem WYCKOFF_DRAW_SPEC.md). CHỈ hiển thị, KHÔNG gate tín hiệu nào.
        // v2 (2026-08-03): port đầy đủ CR-H/CR-I/CR-K/CR-Y/CR-M theo spec, cộng 4 lỗi tự phát hiện qua
        // vòng chấm bằng agent (giống giảng viên chữa bài CHART_CASES.md) + tự kiểm bằng số liệu thật:
        //   - Phase B trước đây chỉ theo dõi 1 cạnh của range → breakout quyết định ở cạnh "kia" (chưa
        //     từng có Spring/UTAD) bị bỏ sót tới khi hết guard thời lượng. Nay theo dõi ĐỘC LẬP cả 2 cạnh,
        //     cho phép SOS/SOW bắn TRỰC TIẾP từ Phase B (bỏ qua Phase C nếu không có Spring/UTAD thật).
        //   - Sau Spring/Shakeout/UTAD: thêm PendingShock theo dõi tiến độ mỗi nến tới khi XÁC NHẬN
        //     (≥50% quãng đường tới biên đối diện) hoặc THẤT BẠI (đóng cửa phá lại qua cực trị shock
        //     trước khi đạt 50%) — trước đây không có cơ chế này (chính là WY10/WY12 chưa từng code hoá).
        //   - Phase E không còn ép buộc VÔ ĐIỀU KIỆN khi hết WY_LPS_WAIT_BARS — cần ≥50%×WY_PHASE_E_MULT
        //     tiến độ, không thì lùi Phase B.
        //   - Mọi nhánh lùi state về "B" đều gọi WySetPhase(...,'B') (trước đây có nhánh chỉ đổi biến nội
        //     bộ State, khiến timeline Phase hiển thị sai — tự phát hiện, không có trong spec gốc).
        //   - Tách nhãn LPS[C]/LPSY[C] (test lúc chờ xác nhận shock, thuộc Phase C) khỏi LPS[D]/LPSY[D]
        //     (pullback sau SOS/SOW, thuộc Phase D — giữ nguyên logic điểm/vùng cũ).
        //   - Thêm nhãn UA (test cạnh trên không quyết định của ACC) / DA (test cạnh dưới không quyết
        //     định của DIST), đối xứng nhau.
        //   - Tự phát hiện qua vòng chấm: trong Phase A (chờ AR), biên KHÔNG cùng phía với climax (r.High
        //     cho DIST, r.Low cho ACC) trước đây không hề được cập nhật suốt cả cửa sổ WY_AR_LOOKBACK —
        //     nếu giá vượt xa hơn chính nến climax trước khi đảo chiều thật, phần vượt đó bị bỏ sót hoàn
        //     toàn. Nay cập nhật thụ động mỗi nến, giống cách Phase B/C/D đã làm.
        //   - Tự phát hiện: mốc bắt đầu Phase B trước đây neo vào `i` (luôn CỐ ĐỊNH climax+40+1), trong
        //     khi AR thật (ar_i) thường xảy ra sớm hơn nhiều trong cửa sổ 40 nến — khiến Phase A hiển thị
        //     vẽ dài tới tận cuối cửa sổ cố định thay vì đúng kết thúc tại AR. Nay neo Phase B tại ar_i+1.
        //   - Tự phát hiện: end_i/EndIdx của cả range trước đây dùng `i` (nến đang xử lý) thay vì bar thật
        //     nơi Phase E được xác nhận (WyTryLpsAndPhaseE nhìn-trước tới WY_LPS_WAIT_BARS nến) — khiến
        //     Range High/Low vẽ ngắn hơn hẳn Phase D/E thật. Nay dùng đúng bar Phase E bắt đầu.
        //   - Nhãn LPS[D] vùng trước đây ghi CHỈ SỐ NẾN vào text (vd "(vùng 47637-47648)") thay vì giá —
        //     gây hiểu lầm nghiêm trọng; nay chỉ ghi "(vùng)", giá thật đã có sẵn ở toạ độ điểm vẽ.
        private const double WY_CLIMAX_RANGE_MULT = 1.4;
        private const int WY_CLIMAX_LOOKBACK = 20;
        private const int WY_AR_LOOKBACK = 40;
        private const int WY_ST_TOL_TICKS = 10;
        private const int WY_ST_MIN_GAP_BARS = 5;
        private const double WY_SOS_BODY_MIN = 0.45;
        private const int WY_LPS_WAIT_BARS = 25;
        private const int WY_LPS_AREA_MIN_BARS = 3;
        private const double WY_PHASE_E_MULT = 1.0;
        private const double WY_SHOCK_PROGRESS_MULT = 0.5;         // [MỚI, spec §1.15/§3.5]
        private const double WY_PHASE_E_MIN_PROGRESS_MULT = 0.5;   // [MỚI, CR-K]
        private const double WY_MAX_HEIGHT_PCT = 0.035;   // guard tu dat (KHONG co trong tai lieu goc):
        private const int WY_MAX_BARS_AB = 2500;          // TR Wyckoff that la vung CAN BANG hep, khong
        private const int WY_MAX_BARS_D = 2000;           // phai the hien ca mot xu huong dai — bo neu vuot.

        // ============================================================================================
        // v3 — nguoi hoc review 2026-08-03, vá 2 lỗi NỀN TẢNG (khớp wyckoff_schematic.py cùng ngày)
        // ============================================================================================
        // LỖI 1 — climax MỘT MÌNH không đủ để mở range. Phải có một MOVE XU HƯỚNG RÕ RÀNG ngay trước
        //   đó bị cây climax chặn lại. Trước đây chỉ dùng b.Trend (close vs close 480 nến, tol 1.0 giá)
        //   — quá yếu, giá đang đi ngang vẫn thoả -> vẽ range tùm lum. Nay đo MOVE thật: độ dài
        //   chân->climax, số nến, và HIỆU SUẤT HƯỚNG (đi thẳng ~1.0, đi ngang ~0.05) để loại đi ngang.
        private const int WY_MOVE_LOOKBACK = 240;
        private const int WY_MOVE_MIN_BARS = 20;
        private const double WY_MOVE_MIN_ATR = 8.0;
        private const double WY_MOVE_MIN_EFF = 0.35;
        // Hệ quả tự phát hiện khi soi lại chart sau khi vá (KHÔNG có trong review): AR chỉ ngọ nguậy
        //   vài giá sau một move 35 giá thì "đổi hướng lần 2" không có thật, và ngưỡng 40% của ST[A]
        //   thành vô nghĩa. Buộc AR phải hồi ≥30% độ dài MOVE.
        private const double WY_AR_MIN_RETRACE_OF_MOVE = 0.30;
        private const int WY_AR_MAX_WAIT = 300;
        // LỖI 2 — Phase A thiếu ST[A]. Phase A là một CHoCH = ĐÚNG 3 lần đổi hướng: (1) move bị climax
        //   chặn, (2) hồi ngược tới AR, (3) quay lại phía climax rồi bị chặn lần nữa = ST[A]. Lúc đó
        //   Phase A mới xong. Không có ST[A] thì chưa thành vùng đi ngang -> BỎ ứng viên.
        private const int WY_STA_MAX_WAIT = 400;
        private const double WY_STA_MIN_RETRACE = 0.40;
        private const int WY_STA_CONFIRM_BARS = 5;

        // ===== v4 — người học review mục 5, 5.1, 5.2, 6, 7 (2026-08-03) =====
        // LỖI 3 (mục 5): thiếu TÁI TÍCH LUỸ / TÁI PHÂN PHỐI. Hướng MOVE trước climax chỉ quyết định
        //   LOẠI CLIMAX (move giảm → SC, move tăng → BCLX), KHÔNG quyết định range phá về hướng nào.
        //   Đủ 4 pattern: SC→phá lên = Tích luỹ · SC→phá xuống = Tái phân phối ·
        //                 BCLX→phá xuống = Phân phối · BCLX→phá lên = Tái tích luỹ.
        //   Trước đây phá "sai hướng" bị coi là giả thuyết SAI và BỎ CẢ RANGE. Nay chỉ ĐỔI TÊN range.
        // LỖI 4 (mục 5): 2 biên chính CỐ ĐỊNH sau Phase A; thăm dò ra ngoài chỉ nới BIÊN PHỤ (nét đứt),
        //   mỗi bên nhiều nhất 1 biên phụ. SOS/SOW muốn mạnh phải đóng cửa BỨT QUA biên phụ.
        // LỖI 5 (mục 5.1): Spring vs Shakeout phân biệt bằng THỜI GIAN quay lại, không phải độ sâu.
        // LỖI 6 (mục 5): bỏ hẳn nhãn ST[B]; LPS[C]/LPSY[C] và LPS[D]/LPSY[D] chỉ đánh dấu 1 điểm.
        // LỖI 7 (mục 6): Phase C case KHÓ → gán NGƯỢC từ LPS[C]/LPSY[C] khi SOS/SOW thật sự bắn ra.
        private const int WY_SPRING_MAX_BARS = 4;
        private const int WY_BREAK_HOLD_BARS = 3;
        private const int WY_BREAK_MAX_WAIT = 40;
        private const int WY_MINOR_POKE_TICKS = 15;
        private const int WY_RETRO_C_LOOKBACK = 60;
        private const int WY_SHOCK_MAX_WAIT = 120;   // mục 6: "Phase C là phase NGẮN NHẤT"

        /// <summary>
        /// Trước nến climax i có một MOVE xu hướng thật không? acc=true cần move GIẢM (SC chặn đáy),
        /// acc=false cần move TĂNG (BCLX chặn đỉnh). Trả về false nếu không đạt.
        /// </summary>
        private bool WyFindMove(List<Bar> B, int i, bool acc, out int footIdx, out double len, out double eff)
        {
            footIdx = -1; len = 0; eff = 0;
            int lo = Math.Max(0, i - WY_MOVE_LOOKBACK);
            if (i - lo < WY_MOVE_MIN_BARS) return false;
            // climax phải là CỰC TRỊ của cả cửa sổ — nó đang CHẶN move, không nằm giữa move
            if (acc)
            {
                for (int k = lo; k < i; k++) if (B[k].L < B[i].L) return false;
                double best = double.MinValue;
                for (int k = lo; k < i; k++) if (B[k].H > best) { best = B[k].H; footIdx = k; }
                len = best - B[i].L;
            }
            else
            {
                for (int k = lo; k < i; k++) if (B[k].H > B[i].H) return false;
                double best = double.MaxValue;
                for (int k = lo; k < i; k++) if (B[k].L < best) { best = B[k].L; footIdx = k; }
                len = B[i].H - best;
            }
            if (footIdx < 0 || i - footIdx < WY_MOVE_MIN_BARS) return false;
            double avgr = WyAvgRange(B, i, WY_CLIMAX_LOOKBACK);
            if (avgr <= 0 || len < WY_MOVE_MIN_ATR * avgr) return false;
            double path = 0;
            for (int k = footIdx + 1; k <= i; k++) path += Math.Abs(B[k].C - B[k - 1].C);
            eff = path > 1e-9 ? len / path : 0;
            return eff >= WY_MOVE_MIN_EFF;
        }

        private double WyAvgRange(List<Bar> B, int i, int lookback)
        {
            int lo = Math.Max(0, i - lookback);
            double sum = 0; int n = 0;
            for (int k = lo; k < i; k++) { sum += B[k].Rng; n++; }
            return n > 0 ? sum / n : B[i].Rng;
        }

        private WyEvent WyAddEvent(WyRange r, int i, string label, double price, WyShockStatus status = WyShockStatus.None)
        {
            var ev = new WyEvent { Idx = i, Label = label, Price = price, Status = status };
            r.Events.Add(ev);
            return ev;
        }

        private void WySetPhase(WyRange r, int i, char phase)
        {
            if (r.Phases.Count > 0 && r.Phases[r.Phases.Count - 1].Phase == phase) return;
            if (r.Phases.Count > 0) r.Phases[r.Phases.Count - 1].EndIdx = i - 1;
            r.Phases.Add(new WyPhaseSeg { Phase = phase, StartIdx = i, EndIdx = -1 });
        }

        /// <summary>
        /// v4 mục 5: mỗi bên chỉ có MỘT biên phụ — "biên phụ cũ biến mất, biên phụ mới tiếp tục nới ra".
        /// Nhãn UA/DA/UT vì vậy cũng chỉ giữ DUY NHẤT một cái ở cực trị xa nhất của bên đó.
        /// </summary>
        private void WyMarkOuter(WyRange r, int i, string label, double price, bool upSide)
        {
            for (int k = r.Events.Count - 1; k >= 0; k--)
            {
                var e = r.Events[k];
                if (e.Label != "UA" && e.Label != "DA" && e.Label != "UT") continue;
                bool sameSide = upSide ? e.Price > r.SolidHigh : e.Price < r.SolidLow;
                if (!sameSide) continue;
                if (upSide ? price <= e.Price : price >= e.Price) return;   // chua vuot bien phu cu
                r.Events.RemoveAt(k);
            }
            WyAddEvent(r, i, label, price);
        }

        /// <summary>
        /// v4 mục 5.1/5.2: một cú phá biên đã được XÁC NHẬN. Không còn chuyện "giả thuyết sai → bỏ
        /// range" — hướng phá chỉ quyết định range thuộc pattern nào trong 4 pattern. Nếu range chưa
        /// từng có Phase C (case KHÓ của mục 6) thì gán NGƯỢC Phase C tại đây. Cú phá đã xác nhận thì
        /// vùng đấu giá KẾT THÚC (State = "END") — trước đây lùi về Phase B gây vòng lặp D→B→D vô tận.
        /// </summary>
        private void WyFireBreak(List<Bar> B, WyRange r, int i, bool up, double outEdge)
        {
            r.Dir = up ? 1 : -1;
            r.Brk = null;
            r.Pending = null;
            bool hasC = false;
            foreach (var p in r.Phases) if (p.Phase == 'C') { hasC = true; break; }
            if (!hasC) WyRetroPhaseC(B, r, i, up);
            WyAddEvent(r, i, up ? "SOS" : "SOW", B[i].C);
            WySetPhase(r, i, 'D');
            WyTryLpsAndPhaseE(B, r, i, up, outEdge);
            r.State = "END";
        }

        /// <summary>
        /// v4 mục 6, case KHÓ: không có Spring/Shakeout/UTAD nào để nhận ra Phase C ngay lúc đó. Đợi
        /// đến khi SOS/SOW thật sự bắn ra rồi NHÌN NGƯỢC lại — nhịp test cuối cùng trước cú phá chính
        /// là LPS[C] (phá lên) / LPSY[C] (phá xuống), Phase C bắt đầu từ đó.
        /// </summary>
        private void WyRetroPhaseC(List<Bar> B, WyRange r, int sosI, bool up)
        {
            // Cửa sổ nhìn lại bị chặn bởi CẢ HAI: WY_RETRO_C_LOOKBACK và MỘT NỬA độ dài Phase B
            // hiện tại. Lý do (tự phát hiện khi soi chart, không có trong review): lấy cực trị của cả
            // 60 nến thì ngay sau ST[A] cực trị thường CHÍNH LÀ vùng ST[A] -> Phase C ăn gần hết range,
            // Phase B chỉ còn 2 nến, trái với cả hai mục của người học ("Phase B dài nhất", "C ngắn nhất").
            int bStart = r.Phases.Count > 0 ? r.Phases[r.Phases.Count - 1].StartIdx : r.StartIdx;
            int win = Math.Min(WY_RETRO_C_LOOKBACK, Math.Max(1, (sosI - bStart) / 2));
            int lo = Math.Max(bStart + 1, sosI - win);
            if (sosI - lo < 3) return;
            int piv = lo; double best = up ? double.MaxValue : double.MinValue;
            for (int k = lo; k < sosI; k++)
            {
                if (up) { if (B[k].L < best) { best = B[k].L; piv = k; } }
                else { if (B[k].H > best) { best = B[k].H; piv = k; } }
            }
            WySetPhase(r, piv, 'C');
            WyAddEvent(r, piv, up ? "LPS[C]" : "LPSY[C]", best);
        }

        /// <summary>
        /// v4 mục 7: Phase D + E chính là CBR — PHÁ biên, HỒI về retest nhưng GIỮ được bên ngoài biên
        /// (nhịp hồi đó = LPS[D]/LPSY[D]), rồi giá THUẬN LỰC đi tiếp tìm vùng giá mới (Phase E).
        /// `level` = biên vừa bị phá (biên PHỤ nếu có, vì SOS/SOW phải bứt qua nó).
        /// FIX CR-K: hết WY_LPS_WAIT_BARS mà chưa đi đủ xa thì chỉ ép Phase E nếu đã đạt
        /// ≥ WY_PHASE_E_MIN_PROGRESS_MULT×WY_PHASE_E_MULT tiến độ. Trả true nếu đã chốt Phase E.
        /// </summary>
        private bool WyTryLpsAndPhaseE(List<Bar> B, WyRange r, int sosI, bool acc, double level)
        {
            int end = Math.Min(B.Count - 1, sosI + WY_LPS_WAIT_BARS);
            double failTol = 3.0 * WY_ST_TOL_TICKS * _tick;
            var pullBars = new List<int>();
            double peak = acc ? B[sosI].H : B[sosI].L;
            double rangeHeight = Math.Max(1e-9, r.SolidSet ? r.SolidHigh - r.SolidLow : r.High - r.Low);
            for (int j = sosI + 1; j <= end; j++)
            {
                var bj = B[j];
                bool failed;
                if (acc) { if (bj.H > peak) peak = bj.H; failed = bj.C < level - failTol; }
                else { if (bj.L < peak) peak = bj.L; failed = bj.C > level + failTol; }
                if (failed) return false;
                if (Math.Abs(bj.C - level) <= 2.0 * WY_ST_TOL_TICKS * _tick) pullBars.Add(j);
                double movedFar = acc ? (peak - level) : (level - peak);
                if (movedFar >= WY_PHASE_E_MULT * rangeHeight)
                {
                    if (pullBars.Count > 0) WyEmitLps(B, r, pullBars, acc);
                    WySetPhase(r, j, 'E');
                    return true;
                }
            }
            if (pullBars.Count > 0) WyEmitLps(B, r, pullBars, acc);
            if ((end - sosI) >= WY_LPS_WAIT_BARS)
            {
                double finalMovedFar = acc ? (peak - level) : (level - peak);
                if (finalMovedFar >= WY_PHASE_E_MIN_PROGRESS_MULT * WY_PHASE_E_MULT * rangeHeight)
                {
                    WySetPhase(r, end, 'E');
                    return true;
                }
                return false;   // FIX CR-K: SOS/SOW qua yeu (chua di du xa) -> lui Phase B, khong ep E
            }
            return false;
        }

        /// <summary>
        /// v4 (người học 2026-08-03): LPS[D]/LPSY[D] CHỈ đánh dấu 1 ĐIỂM duy nhất — bỏ hẳn kiểu vẽ
        /// "(vùng)" cũ. Điểm chọn = đáy sâu nhất (phá lên) / đỉnh cao nhất (phá xuống) của nhịp hồi.
        /// </summary>
        private void WyEmitLps(List<Bar> B, WyRange r, List<int> pullBars, bool acc)
        {
            if (pullBars.Count == 0) return;
            int k = pullBars[0]; double best = acc ? B[k].L : B[k].H;
            foreach (var j in pullBars)
            {
                if (acc) { if (B[j].L < best) { best = B[j].L; k = j; } }
                else { if (B[j].H > best) { best = B[j].H; k = j; } }
            }
            WyAddEvent(r, k, acc ? "LPS[D]" : "LPSY[D]", best);
        }

        private List<WyRange> ScanWyckoff(List<Bar> B)
        {
            var ranges = new List<WyRange>();
            WyRange active = null;
            int nClosed = B.Count - 1;   // bỏ nến đang hình thành, khớp Scan()
            for (int i = WY_CLIMAX_LOOKBACK + 5; i < nClosed; i++)
            {
                var b = B[i];

                if (active == null)
                {
                    double avgr = WyAvgRange(B, i, WY_CLIMAX_LOOKBACK);
                    if (avgr <= 0) continue;
                    bool wide = b.Rng >= WY_CLIMAX_RANGE_MULT * avgr;
                    bool climaxVol = b.Vratio >= VsaClimax;
                    if (!(wide && climaxVol)) continue;
                    // v3: điều kiện CẦN là một MOVE XU HƯỚNG THẬT bị cây climax này chặn lại
                    // (thay hoàn toàn cho b.Trend cũ — xem chú thích WyFindMove).
                    if (b.C < b.O)
                    {
                        if (!WyFindMove(B, i, true, out int fi, out double ln, out double ef)) continue;
                        active = new WyRange
                        {
                            StartIdx = i, OriginDown = true, Low = b.L, High = b.H, ClimaxPrice = b.L,
                            MoveIdx = fi, MoveLen = ln, MoveEff = ef,
                        };
                        WyAddEvent(active, i, "SC", b.L);
                        WySetPhase(active, i, 'A');
                    }
                    else if (b.C > b.O)
                    {
                        if (!WyFindMove(B, i, false, out int fi, out double ln, out double ef)) continue;
                        active = new WyRange
                        {
                            StartIdx = i, OriginDown = false, Low = b.L, High = b.H, ClimaxPrice = b.H,
                            MoveIdx = fi, MoveLen = ln, MoveEff = ef,
                        };
                        WyAddEvent(active, i, "BCLX", b.H);
                        WySetPhase(active, i, 'A');
                    }
                    continue;
                }

                var r = active;
                int climaxI = r.StartIdx;
                int lastEvtI = r.Events.Count > 0 ? r.Events[r.Events.Count - 1].Idx : climaxI;
                bool gapOk = (i - lastEvtI) >= WY_ST_MIN_GAP_BARS;
                double tol = WY_ST_TOL_TICKS * _tick;
                double failTol = 3.0 * WY_ST_TOL_TICKS * _tick;

                // v4: đo bằng biên CHÍNH (cố định) — biên phụ nới ra ngoài không làm range "quá cao".
                double height = r.SolidSet ? r.SolidHigh - r.SolidLow : r.High - r.Low;
                bool tooTall = height > WY_MAX_HEIGHT_PCT * b.C;
                bool tooLongAB = (i - climaxI) > WY_MAX_BARS_AB;
                if (tooTall || tooLongAB) { active = null; continue; }

                if (r.State == "A")
                {
                    // Tu phat hien (giang vien-agent + tu kiem chung so lieu that): AR chi cap nhat canh
                    // DOI DIEN voi climax; canh CUNG PHIA (r.High cho DIST, r.Low cho ACC) truoc day
                    // khong duoc cap nhat gi ca trong suot cua so WY_AR_LOOKBACK.
                    if (r.OriginDown) { if (b.L < r.Low) r.Low = b.L; }
                    else { if (b.H > r.High) r.High = b.H; }

                    if (i - climaxI > WY_AR_LOOKBACK)
                    {
                        int arI = climaxI + 1;
                        double arPrice;
                        if (r.OriginDown)
                        {
                            double bestHi = double.MinValue;
                            for (int k = climaxI + 1; k <= i; k++) if (B[k].H > bestHi) { bestHi = B[k].H; arI = k; }
                            r.High = bestHi; arPrice = r.High;
                        }
                        else
                        {
                            double bestLo = double.MaxValue;
                            for (int k = climaxI + 1; k <= i; k++) if (B[k].L < bestLo) { bestLo = B[k].L; arI = k; }
                            r.Low = bestLo; arPrice = r.Low;
                        }
                        // v3: AR phải là cú bật ngược THẬT (≥30% độ dài move), không phải cái ngọ nguậy
                        if (Math.Abs(arPrice - r.ClimaxPrice) < WY_AR_MIN_RETRACE_OF_MOVE * Math.Max(1e-9, r.MoveLen))
                        {
                            if ((i - climaxI) > WY_AR_MAX_WAIT) active = null;
                            continue;
                        }
                        // CR-U (ưu tiên THẤP, chỉ hiển thị): AR quá sát climax -> co the chi la 1 cay
                        // bấc nhiễu, không giống 1 cú Automatic Rally thật. KHÔNG đổi ngưỡng/luồng xử lý.
                        string arLabel = (arI - climaxI) <= 2 ? "AR (yếu)" : "AR";
                        WyAddEvent(r, arI, arLabel, arPrice);
                        r.ArIdx = arI; r.ArPrice = arPrice;
                        // v3: CHƯA được sang Phase B. Phase A chỉ xong khi có ST[A] (lần đổi hướng thứ 3).
                        r.State = "A_st";
                        r.StExt = r.OriginDown ? B[i].L : B[i].H;
                        r.StExtIdx = i;
                    }
                    continue;
                }

                // ===== state A_st: chờ ST[A] = lần đổi hướng thứ 3, mốc KẾT THÚC Phase A =====
                // Sau AR, giá phải quay lại phía climax đủ sâu (≥40% chiều cao) rồi BỊ CHẶN lần nữa.
                // Không có ST[A] -> chưa thành vùng đi ngang -> bỏ ứng viên (đúng lý thuyết CHoCH).
                if (r.State == "A_st")
                {
                    double retrace;
                    if (r.OriginDown)
                    {
                        if (b.H > r.High) { r.High = b.H; r.ArIdx = i; r.ArPrice = b.H; r.StExt = b.L; r.StExtIdx = i; }
                        if (b.L < r.StExt) { r.StExt = b.L; r.StExtIdx = i; }
                        retrace = (r.ArPrice - r.StExt) / Math.Max(1e-9, r.ArPrice - r.ClimaxPrice);
                    }
                    else
                    {
                        if (b.L < r.Low) { r.Low = b.L; r.ArIdx = i; r.ArPrice = b.L; r.StExt = b.H; r.StExtIdx = i; }
                        if (b.H > r.StExt) { r.StExt = b.H; r.StExtIdx = i; }
                        retrace = (r.StExt - r.ArPrice) / Math.Max(1e-9, r.ClimaxPrice - r.ArPrice);
                    }

                    if (retrace >= WY_STA_MIN_RETRACE && (i - r.StExtIdx) >= WY_STA_CONFIRM_BARS)
                    {
                        r.StaIdx = r.StExtIdx; r.StaPrice = r.StExt;
                        WyAddEvent(r, r.StaIdx, "ST[A]", r.StaPrice);
                        // v4: ĐÓNG BĂNG 2 biên CHÍNH (nét liền) tại đây = mức climax + mức AR.
                        r.SolidLow = Math.Min(r.ClimaxPrice, r.ArPrice);
                        r.SolidHigh = Math.Max(r.ClimaxPrice, r.ArPrice);
                        r.SolidSet = true;
                        // ST[A] vượt QUA climax -> tạo BIÊN PHỤ (nét đứt) rộng hơn
                        if (r.OriginDown) r.Low = Math.Min(r.Low, r.StaPrice);
                        else r.High = Math.Max(r.High, r.StaPrice);
                        r.Low = Math.Min(r.Low, r.SolidLow);
                        r.High = Math.Max(r.High, r.SolidHigh);
                        WySetPhase(r, r.StaIdx + 1, 'B');
                        r.State = "B";
                    }
                    else if ((i - r.ArIdx) > WY_STA_MAX_WAIT) active = null;
                    continue;
                }

                // ===== state B (v4): 2 biên CHÍNH đã cố định. Mỗi nến chỉ hỏi một câu: giá có
                // thăm dò RA NGOÀI biên chính không? Nếu có -> chuyển sang theo dõi cú phá đó =====
                if (r.State == "B")
                {
                    double penLo = (r.SolidLow - b.L) / _tick;
                    double penHi = (b.H - r.SolidHigh) / _tick;
                    int side = 0;
                    if (Math.Max(penLo, penHi) > WY_ST_TOL_TICKS) side = penLo >= penHi ? -1 : 1;
                    // Biên PHỤ chỉ nới rộng bằng cú thăm dò THẤT BẠI (giá rút về trong range). Nếu đây
                    // là khởi đầu một cú phá thật thì đoạn giá đi ra ngoài thuộc XU HƯỚNG MỚI, không
                    // phải biên của vùng cân bằng -> chưa nới ở đây, đợi kết cục trong state B_brk.
                    if (side != -1 && b.L < r.Low) r.Low = b.L;
                    if (side != 1 && b.H > r.High) r.High = b.H;
                    if (side != 0)
                    {
                        r.Brk = new WyBreak
                        {
                            Side = side, StartIdx = i, Hold = 0, VMax = b.Vratio,
                            Ext = side < 0 ? b.L : b.H, ExtIdx = i,
                            Out0 = side < 0 ? r.Low : r.High,
                        };
                        r.State = "B_brk";
                    }
                    // KHÔNG continue: vừa mở B_brk thì xử lý luôn chính cây nến này ở dưới
                }

                // ===== state B_brk (v4 mục 5.1): theo dõi cú phá biên đến khi rõ kết cục =====
                if (r.State == "B_brk")
                {
                    var k = r.Brk;
                    bool upSide = k.Side > 0;
                    double edge = upSide ? r.SolidHigh : r.SolidLow;
                    double outEdge = upSide ? Math.Max(k.Out0, edge) : Math.Min(k.Out0, edge);
                    if (b.Vratio > k.VMax) k.VMax = b.Vratio;
                    bool backIn, decisive;
                    if (upSide)
                    {
                        if (b.H > k.Ext) { k.Ext = b.H; k.ExtIdx = i; }
                        backIn = b.C < edge - 1e-9;
                        decisive = b.C > outEdge + failTol && b.Brat >= WY_SOS_BODY_MIN;
                    }
                    else
                    {
                        if (b.L < k.Ext) { k.Ext = b.L; k.ExtIdx = i; }
                        backIn = b.C > edge + 1e-9;
                        decisive = b.C < outEdge - failTol && b.Brat >= WY_SOS_BODY_MIN;
                    }
                    int barsOut = i - k.StartIdx;

                    if (backIn)
                    {
                        // cú phá THẤT BẠI — giá đã rút về trong range. Giờ mới nới BIÊN PHỤ bằng
                        // cực trị của cú thăm dò này (xem chú thích ở state B).
                        if (upSide) r.High = Math.Max(r.High, k.Ext); else r.Low = Math.Min(r.Low, k.Ext);
                        double depthT = Math.Abs(k.Ext - edge) / _tick;
                        bool minor = depthT < WY_MINOR_POKE_TICKS && k.VMax < 1.5 * VsaClimax;
                        bool climaxSide = upSide == !r.OriginDown;
                        r.Brk = null;
                        r.State = "B";
                        if (!climaxSide)
                        {
                            // thăm dò cạnh AR: luôn là sự kiện Phase B (không quyết định), chỉ nới biên phụ
                            WyMarkOuter(r, k.ExtIdx, upSide ? "UA" : "DA", k.Ext, upSide);
                        }
                        else if (minor)
                        {
                            // thăm dò NHẸ cạnh climax. origin UP -> UT. origin DOWN -> đó chính là ST[B],
                            // người học yêu cầu BỎ hẳn nhãn này -> chỉ nới biên phụ, không ghi sự kiện.
                            if (!r.OriginDown) WyMarkOuter(r, k.ExtIdx, "UT", k.Ext, upSide);
                        }
                        else
                        {
                            // cú shock THẬT ở cạnh climax -> Phase C
                            string label; double tgt; int sdir;
                            if (upSide) { label = "UTAD"; tgt = r.SolidLow; sdir = -1; }
                            else
                            {
                                // mục 5.1: phân biệt bằng THỜI GIAN quay lại, không phải độ sâu
                                label = barsOut <= WY_SPRING_MAX_BARS ? "Spring" : "Shakeout";
                                tgt = r.SolidHigh; sdir = 1;
                            }
                            var ev = WyAddEvent(r, k.ExtIdx, label, k.Ext, WyShockStatus.Pending);
                            r.Pending = new WyPendingShock
                            {
                                Price = k.Ext, TargetEdge = tgt, Peak = k.Ext, Ev = ev, Dir = sdir,
                                OutEdge = sdir < 0 ? r.Low : r.High, LpsDone = false, StartIdx = k.ExtIdx,
                            };
                            WySetPhase(r, k.ExtIdx, 'C');
                            r.State = "C_pending";
                        }
                        continue;
                    }

                    k.Hold = decisive ? k.Hold + 1 : 0;
                    if (k.Hold >= WY_BREAK_HOLD_BARS || barsOut > WY_BREAK_MAX_WAIT)
                    {
                        // mục 5.1/5.2: đóng cửa hẳn ngoài biên + các nến sau đủ mạnh giữ nó ở ngoài =
                        // phá THẬT. KHÔNG bỏ range nữa — chỉ chốt xem nó thuộc pattern nào trong 4.
                        WyFireBreak(B, r, i, upSide, outEdge);
                    }
                    else continue;
                }

                // ===== state C_pending: xác nhận/thất bại shock (FIX CR-I) =====
                if (r.State == "C_pending")
                {
                    var shock = r.Pending;
                    double span = Math.Max(1e-9, Math.Abs(shock.TargetEdge - shock.Price));
                    bool up = shock.Dir > 0;
                    double progress; bool failedNow;
                    if (up)
                    {
                        if (b.H > shock.Peak) shock.Peak = b.H;
                        if (b.H > r.High) r.High = b.H;
                        progress = (shock.Peak - shock.Price) / span;
                        failedNow = b.C < shock.Price - tol;
                    }
                    else
                    {
                        if (b.L < shock.Peak) shock.Peak = b.L;
                        if (b.L < r.Low) r.Low = b.L;
                        progress = (shock.Price - shock.Peak) / span;
                        failedNow = b.C > shock.Price + tol;
                    }

                    // mục 6: Phase C là phase NGẮN NHẤT — chờ quá lâu không ra SOS/SOW thì shock đã chết
                    if ((i - shock.StartIdx) > WY_SHOCK_MAX_WAIT)
                    {
                        shock.Ev.Status = WyShockStatus.Failed;
                        shock.Ev.Label += " (thất bại)";
                        r.Pending = null;
                        WySetPhase(r, i, 'B');
                        r.State = "B";
                    }
                    else if (failedNow && progress < WY_SHOCK_PROGRESS_MULT)
                    {
                        // "ngã rẽ trước khi tới khu vực đối diện" = cấu trúc thất bại (THEORY §9) —
                        // lùi về Phase B (không huỷ range), tiếp tục dò Spring/UT mới.
                        shock.Ev.Status = WyShockStatus.Failed;
                        shock.Ev.Label += " (thất bại)";
                        r.Pending = null;
                        if (up) r.Low = Math.Min(r.Low, b.L); else r.High = Math.Max(r.High, b.H);
                        WySetPhase(r, i, 'B');
                        r.State = "B";
                    }
                    else
                    {
                        if (progress >= WY_SHOCK_PROGRESS_MULT && shock.Ev.Status == WyShockStatus.Pending)
                            shock.Ev.Status = WyShockStatus.Confirmed;

                        // mục 5: SOS/SOW phải bứt qua BIÊN PHỤ mới tính là mạnh
                        double oe = shock.OutEdge;
                        bool broke = up ? b.C > oe + tol : b.C < oe - tol;
                        if (broke && b.Brat >= WY_SOS_BODY_MIN && gapOk)
                        {
                            r.Pending = null;
                            WyFireBreak(B, r, i, up, oe);
                        }
                        else if (gapOk && !shock.LpsDone && Math.Abs(b.C - shock.Price) <= 2.0 * tol)
                        {
                            // CR-M: test trong lúc CHỜ xác nhận shock = LPS[C]/LPSY[C].
                            // v4: CHỈ đánh dấu 1 điểm duy nhất.
                            WyAddEvent(r, i, up ? "LPS[C]" : "LPSY[C]", b.C);
                            shock.LpsDone = true;
                        }
                    }
                }

                // ===== đã phá xong -> đóng range =====
                if (r.State == "END")
                {
                    var last = r.Phases[r.Phases.Count - 1];
                    int eEnd = last.Phase == 'E'
                        ? Math.Max(last.StartIdx, Math.Min(B.Count - 1, i))
                        : Math.Max(last.StartIdx, Math.Min(B.Count - 1, i + WY_LPS_WAIT_BARS));
                    last.EndIdx = eEnd;
                    r.EndIdx = eEnd;
                    r.Completed = true;
                    ranges.Add(r);
                    active = null;
                    continue;
                }

            }
            if (active != null)
            {
                if (active.Phases.Count > 0) active.Phases[active.Phases.Count - 1].EndIdx = B.Count - 1;
                ranges.Add(active);
            }
            return ranges;
        }

        private WyRangeR WyToRender(List<Bar> B, WyRange r)
        {
            int endIdx = r.EndIdx >= 0 ? r.EndIdx : B.Count - 1;
            var rr = new WyRangeR
            {
                StartTime = B[r.StartIdx].Time, EndTime = B[endIdx].Time, Low = r.Low, High = r.High,
                Kind = WyKind(r.OriginDown, r.Dir),
                Up = r.Dir != 0 ? r.Dir > 0 : r.OriginDown,
                StartHd = B[r.StartIdx].HdIdx, EndHd = B[endIdx].HdIdx, Completed = r.Completed,
                Key = (r.OriginDown ? "A" : "D") + B[r.StartIdx].HdIdx,
                // v3: biên CHÍNH = mức climax + mức AR (nét liền). Chưa có AR thì tạm dùng biên làm việc.
                SolidLow = r.SolidSet ? r.SolidLow : (r.ArIdx >= 0 ? Math.Min(r.ClimaxPrice, r.ArPrice) : r.Low),
                SolidHigh = r.SolidSet ? r.SolidHigh : (r.ArIdx >= 0 ? Math.Max(r.ClimaxPrice, r.ArPrice) : r.High),
            };
            foreach (var e in r.Events) rr.Events.Add(new WyEventR { Time = B[e.Idx].Time, HdIdx = B[e.Idx].HdIdx, Price = e.Price, Label = e.Label, Status = e.Status });
            foreach (var p in r.Phases)
            {
                int pe = p.EndIdx >= 0 ? p.EndIdx : endIdx;
                rr.Phases.Add(new WyPhaseSegR { Phase = p.Phase, StartTime = B[p.StartIdx].Time, EndTime = B[pe].Time, StartHd = B[p.StartIdx].HdIdx, EndHd = B[pe].HdIdx });
            }
            return rr;
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
              .Append("\"size_mult\":").Append(NhoiSize(s).ToString("0.##", ci)).Append(',')
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
            // log/telegram riêng của WyckoffRunner (tách khỏi %LOCALAPPDATA%\TpoSuite của bộ TPO)
            _tele.ShareDir = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WyckoffRunner");
        }

        private void PollTeleTest()
        {
            ConfigTele();
            _tele.PollTestRaw($"🔔 TEST — Wyckoff Runner ({Symbol?.Name ?? "?"}) bot chạy OK\n— mẫu tin MỞ: 🟢 MUA · CBR · hạng A · Entry/SL/TP\n— mẫu tin ĐÓNG (chạm TP/SL): ✅ WIN +{RR:0.#}R · giá vào→ra · thời lượng\n(nếu nhận được tin này = đường gửi OK; tin ĐÓNG sẽ tự bắn khi lệnh chạm TP/SL)");
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
            sb.Append(dirVN).Append(" · Wyckoff Runner ").Append(branch).Append(" · hạng ").Append(s.Grade);
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
            sb.Append(head).Append(" · ").Append(dirVN).Append(" · Wyckoff Runner ").Append(branch).Append('\n');
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
        private string DailyCsvName() => $"{SafeFileName("WYCKOFF RUNNER CBR+VWAP v6 (M1)")}_{DateTime.UtcNow.AddHours(TzOffset):yyyy-MM-dd}.csv";

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

        // BẢNG TƯƠNG TÁC (UiPanel) + NHẢY CHART (ChartNav/UiNav) + KÍNH LÚP (UiMiniChart) nay nằm ở
        // UiKit.cs — DÙNG CHUNG với EntrySignal và RunnerSignal (concat lúc build, xem build-*.sh).

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
            p.Add(($"WYCKOFF RUNNER CBR+VWAP v6 (M1)   ▶{sigs.Count - nRev} ↩{nRev} · ✓{tp} ✗{sl} •{running}{wr}{deadTag}  [CBR {RR:0.#}R · quay đầu {RevRR:0.#}R]", Color.White));
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
            if (ClickToNavigate)
                p.Add(("🧭 Bấm 1 dòng = nhảy chart tới đó · nháy đúp dòng Range = kính lúp · " + ChartNav.Status,
                       Color.FromArgb(170, 195, 225)));
            return p;
        }

        // ---- danh sách LỆNH (mỗi lệnh = 1 dòng chính + 1 dòng phụ "vì sao") ----
        private List<UiRow> BuildEntryRows(List<Sig> sigs)
        {
            var rows = new List<UiRow>();
            if (sigs == null) return rows;
            foreach (var s in sigs.OrderByDescending(s => s.Idx))
            {
                Color col = s.Side > 0 ? LongColor : ShortColor;
                string dir = s.Side > 0 ? "LONG" : "SHORT";
                string oc = s.Outcome == "TP" ? "✓" : s.Outcome == "SL" ? "✗" : "•";
                string tag = s.Scen != null && s.Scen.StartsWith("quay") ? "↩" : "▶";
                double rr = s.TargetRr > 0 ? s.TargetRr : RR;
                rows.Add(new UiRow
                {
                    Key = "S" + s.HdIdx + (s.Side > 0 ? "L" : "S"),
                    L1 = $"{oc} {tag} {s.Time.AddHours(TzOffset):dd/MM HH:mm} {dir} {s.Grade} · E {Fmt(s.Entry)} SL {Fmt(s.Sl)} ({s.RiskT * _tick:0.0}giá) TP {Fmt(s.Tp1)} ({rr:0.#}R)",
                    L2 = "     " + string.Join(" · ", s.Why),
                    C1 = col, C2 = Color.Silver,
                    NavIdx = s.HdIdx, NavPrice = s.Entry,
                });
            }
            return rows;
        }

        // ---- danh sách WYCKOFF RANGE (để soi lại quá khứ, tự chấm bản vẽ) ----
        private List<UiRow> BuildRangeRows(List<WyRangeR> ranges)
        {
            var rows = new List<UiRow>();
            if (ranges == null) return rows;
            for (int k = ranges.Count - 1; k >= 0; k--)   // mới nhất lên đầu
            {
                var r = ranges[k];
                Color col = WyKindColor(r);
                string kind = (r.Up ? "▲ " : "▼ ") + WyKindVn(r.Kind).ToUpperInvariant();
                string phases = r.Phases.Count > 0 ? string.Join("→", r.Phases.Select(x => x.Phase.ToString()).Distinct()) : "—";
                var evs = r.Events.Select(e => e.Label).ToList();
                string evTxt = string.Join(" ", evs.Take(8)) + (evs.Count > 8 ? " …" : "");
                int bars = Math.Max(1, r.EndHd - r.StartHd + 1);
                rows.Add(new UiRow
                {
                    Key = r.Key,
                    L1 = $"{kind} · {r.StartTime.AddHours(TzOffset):dd/MM HH:mm} → {r.EndTime.AddHours(TzOffset):dd/MM HH:mm} ({bars} nến){(r.Completed ? "" : "  (đang chạy)")}",
                    L2 = $"     {Fmt(r.Low)}–{Fmt(r.High)} ({(r.High - r.Low):0.0} giá) · Phase {phases} · {evs.Count} mốc: {evTxt}",
                    C1 = col, C2 = Color.FromArgb(190, 190, 190),
                    NavIdx = r.StartHd, NavSpan = bars, NavPrice = (r.Low + r.High) / 2,
                });
            }
            return rows;
        }

        // ================= RENDER (tái dùng từ EntrySignal) =================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null) return;   // KHÔNG chặn theo _vaLoaded: _render==null bên dưới đã đủ (xem fix mất panel ở OnUpdate)
            if (_ui.OnActivate == null)
            {
                _ui.OnActivate = OnRowActivate;
                _ui.OnClose = () => { _inspectKey = null; CurrentChart?.RedrawBuffer(); };
            }
            _ui.Attach(CurrentChart);
            ChartNav.Discover(CurrentChart, DumpChartApi);
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
                if (ShowWyckoffSchematic && rs.WyRanges != null && rs.WyRanges.Count > 0)
                {
                    using var fPhase = new Font("Segoe UI", 9, FontStyle.Bold);
                    using var fEvt = new Font("Consolas", 9, FontStyle.Bold);
                    DrawWyckoff(gr, rs.WyRanges, (t, hd) => (float)conv.GetChartX(t), pp => (float)conv.GetChartY(pp),
                                new RectangleF(clip.X, clip.Y, clip.Width, clip.Height), fPhase, fEvt, _ui.SelKeyOf(1), true);
                }

                if (ShowSignals && rs.Sigs != null)
                {
                    using var fLbl = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    using var fChip = new Font("Consolas", Math.Max(8, FontSize), FontStyle.Bold);
                    var dash = DashedSlTp ? DashStyle.Dash : DashStyle.Solid;
                    string selSig = _ui.SelKeyOf(0);
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
                        // lệnh ĐANG CHỌN trong bảng: vạch dọc + vòng tròn to để tìm thấy ngay sau khi nhảy chart
                        if (selSig != null && selSig == "S" + s.HdIdx + (s.Side > 0 ? "L" : "S"))
                        {
                            using (var pSel = new Pen(Color.FromArgb(220, 255, 235, 130), 1.4f) { DashStyle = DashStyle.Dot })
                                gr.DrawLine(pSel, xE, clip.Top, xE, clip.Bottom);
                            using (var pSel2 = new Pen(Color.FromArgb(235, 255, 235, 130), 2f))
                                gr.DrawEllipse(pSel2, xE - 10f, yE - 10f, 20, 20);
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
                // KÍNH LÚP vẽ TRƯỚC bảng để bảng luôn nằm trên cùng (bảng là thứ đang thao tác).
                _ui.CloseBox = RectangleF.Empty;
                if (_inspectKey != null && rs.WyRanges != null)
                {
                    var rIns = rs.WyRanges.FirstOrDefault(z => z.Key == _inspectKey);
                    if (rIns == null) _inspectKey = null; else DrawInspector(gr, rIns, clip);
                }
                if (ShowPanel && rs.Panel != null)
                {
                    using var f = new Font("Consolas", FontSize, FontStyle.Regular);
                    using var fb = new Font("Consolas", FontSize, FontStyle.Bold);
                    var se = _ui.Sec(0); se.Title = "LỆNH"; se.Vis = Math.Max(2, PanelRows); se.Empty = "(chưa có lệnh nào)";
                    se.Hint = ClickToNavigate ? "bấm = nhảy chart" : "";
                    se.Rows = rs.EntryRows ?? new List<UiRow>();
                    var sr = _ui.Sec(1); sr.Title = "WYCKOFF RANGE"; sr.Vis = Math.Max(2, RangeListRows); sr.Empty = "(chưa nhận diện được range nào)";
                    sr.Hint = WyInspector ? "bấm = nhảy · nháy đúp = kính lúp" : (ClickToNavigate ? "bấm = nhảy chart" : "");
                    sr.Rows = rs.RangeRows ?? new List<UiRow>();
                    _ui.Draw(gr, f, fb, rs.Panel, Math.Clamp(PanelOpacity, 100, 255), PanelCorner, clip, PanelWidth);
                }
                else _ui.Hide();
                _nav.Step(CurrentChart, conv, clip, ex => LogErr(ex, "UiNav.Step"));   // vòng lặp kín canh vị trí sau khi bấm dòng
            }
            catch { /* nuốt lỗi vẽ */ }
            finally { gr.SetClip(prevClip); }
        }

        // ================= BẤM 1 DÒNG → NHẢY CHART =================
        // Gọi từ UiPanel (UI thread). Chỉ ĐẶT yêu cầu; việc canh chính xác do UiNav.Step làm dần qua các
        // khung hình vẽ (xem ChartNav: không biết chắc đơn vị RightOffset nên phải đo–hiệu chỉnh).
        private void OnRowActivate(int section, UiRow row, bool dbl)
        {
            try
            {
                if (row == null) return;
                if (section == 1 && dbl && WyInspector)
                {
                    _inspectKey = _inspectKey == row.Key ? null : row.Key;
                    CurrentChart?.RedrawBuffer();
                    return;
                }
                if (!ClickToNavigate || row.NavIdx < 0) return;
                var hd = HistoricalData; var chart = CurrentChart;
                if (hd == null || chart == null) return;
                ChartNav.Discover(chart, DumpChartApi);
                if (!ChartNav.CanScroll)
                {
                    // Không cuộn được chart → mở luôn kính lúp để vẫn soi được range quá khứ.
                    if (section == 1 && WyInspector) _inspectKey = row.Key;
                    chart.RedrawBuffer();
                    return;
                }
                if (NavZoomFit && row.NavSpan > 5 && ChartNav.CanZoom)
                {
                    int wpx = Math.Max(200, chart.MainWindow.ClientRectangle.Width);
                    ChartNav.SetBarsWidth(chart, (int)Math.Floor(wpx / (row.NavSpan * 1.35)));
                }
                int center = row.NavIdx + row.NavSpan / 2;
                center = Math.Max(0, Math.Min(hd.Count - 1, center));
                if (hd[center, SeekOriginHistory.Begin] is not HistoryItemBar hb) return;
                _nav.Request(chart, hb.TimeLeft);
                chart.RedrawBuffer();
            }
            catch (Exception ex) { LogErr(ex, "OnRowActivate"); }
        }

        private void DumpChartApi(string text)
        {
            if (_apiDumped || string.IsNullOrEmpty(text)) return;
            _apiDumped = true;
            try
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "WyckoffRunner");
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "chart_api.txt"), text);
            }
            catch { }
        }

        // ================================================================================================
        //  VẼ SƠ ĐỒ WYCKOFF — dùng chung cho CHART CHÍNH và KÍNH LÚP
        //  Toạ độ đi qua 2 hàm ánh xạ: X(thời gian, chỉ số nến) và Y(giá). Chart chính dùng thời gian
        //  (CoordinatesConverter), kính lúp dùng chỉ số nến (tự chia đều trong khung) → cùng MỘT mã vẽ,
        //  không sợ 2 nơi vẽ lệch nhau.
        // ================================================================================================
        private void DrawWyckoff(Graphics gr, List<WyRangeR> ranges, Func<DateTime, int, float> X, Func<double, float> Y,
                                 RectangleF area, Font fPhase, Font fEvt, string selKey, bool legend)
        {
            var placedBoxes = new List<RectangleF>();
            // UI/UX: nhãn LUÔN vẽ trong hộp bo góc nền tối (không chữ trần đè lên nến), né chồng lấp theo
            // CẢ x lẫn y — "show chữ rõ ràng" (2026-08-02).
            void WyLabelBox(float x, float y, string text, Color color, Font f, bool anchorLeft)
            {
                var sz = gr.MeasureString(text, f);
                float pad = 3, w = sz.Width + 2 * pad, h = sz.Height + 2;
                float bx = anchorLeft ? x : x - w, by = y;
                int guard = 0;
                while (guard < 40 && placedBoxes.Exists(bb => bb.IntersectsWith(new RectangleF(bx, by, w, h)))) { by -= h + 2; guard++; }
                placedBoxes.Add(new RectangleF(bx, by, w, h));
                using (var path = Round(bx, by, w, h, 4))
                {
                    using (var bgb = new SolidBrush(Color.FromArgb(230, 20, 20, 24))) gr.FillPath(bgb, path);
                    using (var bd = new Pen(color, 1f)) gr.DrawPath(bd, path);
                }
                using var tb = new SolidBrush(color);
                gr.DrawString(text, f, tb, bx + pad, by + 1);
            }
            // Mỗi HỌ sự kiện 1 màu riêng để đọc nhanh trên chart bận nến — khớp bảng màu bên Python
            // (render_schematic_preview.py) dùng để kiểm bằng mắt trước khi port.
            string WyCat(string label)
            {
                string b = label.Length > 0 && label[label.Length - 1] == ')' ? label.Substring(0, label.IndexOf('(')).TrimEnd() : label;
                switch (b)
                {
                    case "SC": case "BCLX": return "climax";
                    case "AR": return "ar";
                    case "ST[A]": return "ar";      // v3: ST[A] thuộc Phase A, đọc chung màu với AR
                    case "ST": case "UA": case "DA": case "UT": return "st";   // v4: UT = test nhẹ Phase B
                    case "Spring": case "Shakeout": case "UTAD": return "shake";
                    case "SOS": case "SOW": return "break";
                    case "LPS[C]": case "LPSY[C]": return "lpsc";
                    case "LPS[D]": case "LPSY[D]": return "lpsd";
                    default: return "st";
                }
            }
            Color WyCatColor(string cat)
            {
                switch (cat)
                {
                    case "climax": return Color.FromArgb(255, 82, 82);
                    case "ar": return Color.FromArgb(129, 199, 132);
                    case "st": return Color.FromArgb(176, 190, 197);
                    case "shake": return Color.FromArgb(255, 202, 40);
                    case "break": return Color.FromArgb(66, 165, 245);
                    case "lpsc": return Color.FromArgb(38, 198, 168);
                    case "lpsd": return Color.FromArgb(186, 104, 200);
                    default: return Color.FromArgb(255, 230, 150);
                }
            }
            if (legend)
            {
                var items = new (string cat, string desc)[] {
                    ("climax", "SC / BCLX — Climax"), ("ar", "AR / ST[A] — chốt Phase A"),
                    ("st", "UA/UT/DA — test, nới biên phụ"),
                    ("shake", "Spring/Shakeout/UTAD — Phase C"), ("break", "SOS/SOW — phá vỡ"),
                    ("lpsc", "LPS[C] — test chờ xác nhận"), ("lpsd", "LPS[D] — vào lại sau phá"),
                };
                float ly = area.Top + 4, lh = 17 * items.Length + 6;
                using (var bgL = new SolidBrush(Color.FromArgb(235, 16, 16, 19)))
                    gr.FillRectangle(bgL, area.Right - 264, ly - 4, 264, lh);
                using var brL = new SolidBrush(Color.FromArgb(220, 220, 220));
                foreach (var (cat, desc) in items)
                {
                    using (var b = new SolidBrush(WyCatColor(cat))) gr.FillEllipse(b, area.Right - 258, ly + 3, 8, 8);
                    gr.DrawString(desc, fPhase, brL, area.Right - 246, ly);
                    ly += 17;
                }
                placedBoxes.Add(new RectangleF(area.Right - 264, area.Top, 264, lh));
            }

            foreach (var r in ranges)
            {
                Color col = WyKindColor(r);
                bool sel = !string.IsNullOrEmpty(selKey) && selKey == r.Key;
                float x0 = X(r.StartTime, r.StartHd), x1 = X(r.EndTime, r.EndHd);
                if (x1 < area.Left || x0 > area.Right) continue;   // cả range ngoài khung
                float xa = Math.Max(x0, area.Left), xb = Math.Min(x1, area.Right);
                float yLow = Y(r.Low), yHigh = Y(r.High);
                // range ĐANG CHỌN trong bảng: tô nền mờ + viền dày để tìm thấy ngay bằng mắt
                if (sel)
                    using (var bsel = new SolidBrush(Color.FromArgb(34, col)))
                        gr.FillRectangle(bsel, xa, Math.Min(yHigh, yLow), Math.Max(1, xb - xa), Math.Abs(yLow - yHigh));
                // v3: BIÊN CHÍNH (nét liền) = mức climax và mức AR — biên quan trọng nhất.
                // BIÊN NỚI RỘNG (nét đứt) = biên làm việc khi ST[A]/Spring/UT đã đẩy ra ngoài mức climax.
                float ySolidLo = Y(r.SolidLow), ySolidHi = Y(r.SolidHigh);
                using (var penR = new Pen(col, sel ? 3.2f : 2f))
                {
                    gr.DrawLine(penR, xa, ySolidLo, xb, ySolidLo);
                    gr.DrawLine(penR, xa, ySolidHi, xb, ySolidHi);
                }
                using (var penO = new Pen(col, sel ? 2f : 1.4f) { DashStyle = DashStyle.Dash })
                {
                    if (r.Low < r.SolidLow - _tick / 2) gr.DrawLine(penO, xa, yLow, xb, yLow);
                    if (r.High > r.SolidHigh + _tick / 2) gr.DrawLine(penO, xa, yHigh, xb, yHigh);
                }
                using (var bk = new SolidBrush(col))
                    gr.DrawString(WyKindVn(r.Kind), fPhase, bk, xb + 4, yHigh - 8);

                // vạch dọc chia PHASE — nét đứt, CHỈ trong phạm vi giá [Low..High] CỦA range này
                // (KHÔNG kéo hết chiều cao chart — đúng yêu cầu cũ của người học).
                using (var penP = new Pen(WyPhaseColor, 1.6f) { DashStyle = DashStyle.Dash, DashPattern = new[] { 5f, 4f } })
                {
                    foreach (var ph in r.Phases)
                    {
                        float xp = X(ph.StartTime, ph.StartHd);
                        if (xp < area.Left || xp > area.Right) continue;
                        gr.DrawLine(penP, xp, yHigh, xp, yLow);
                        WyLabelBox(xp + 3, yHigh - 24, $"Phase {ph.Phase}", WyPhaseColor, fPhase, true);
                    }
                }

                // nhãn sự kiện (SC/AR/ST/UA/DA/Spring/Shakeout/SOS/BCLX/UT/UTAD/SOW/LPS[C]/LPS[D])
                foreach (var ev in r.Events.OrderBy(e => e.Time))
                {
                    float xe = X(ev.Time, ev.HdIdx);
                    if (xe < area.Left - 20 || xe > area.Right + 20) continue;
                    float ye = Y(ev.Price);
                    string cat = WyCat(ev.Label);
                    bool above = cat == "ar" || cat == "st" || cat == "break";
                    float ty = above ? ye - 22 : ye + 8;
                    var cc = WyCatColor(cat);
                    // marker theo trạng thái shock: đặc/viền dày = Confirmed, viền đứt = Pending, xám = Failed.
                    var mcolor = ev.Status == WyShockStatus.Failed ? Color.FromArgb(140, 140, 140) : cc;
                    using (var bm = new SolidBrush(mcolor)) gr.FillEllipse(bm, xe - 3f, ye - 3f, 6, 6);
                    using (var pw = new Pen(Color.White, ev.Status == WyShockStatus.Confirmed ? 2f : 1f)
                           { DashStyle = ev.Status == WyShockStatus.Pending ? DashStyle.Dash : DashStyle.Solid })
                        gr.DrawEllipse(pw, xe - 3f, ye - 3f, 6, 6);
                    WyLabelBox(xe - 9, ty, ev.Label, mcolor, fEvt, true);
                }
            }
        }

        // ================================================================================================
        //  KÍNH LÚP — tự vẽ lại range đã chọn (nến + sơ đồ) trong 1 cửa sổ trên chart.
        //  Lý do tồn tại: Quantower không công bố API cuộn chart; nếu ChartNav không dò được thành viên
        //  ghi được thì đây là cách DUY NHẤT chắc chắn xem lại được range quá khứ mà không phải kéo tay.
        // ================================================================================================
        private readonly UiMiniChart _ins = new();

        private void DrawInspector(Graphics gr, WyRangeR r, Rectangle clip)
        {
            var hd = HistoricalData;
            if (hd == null || hd.Count < 2) return;
            int span = Math.Max(1, r.EndHd - r.StartHd + 1);
            int padB = Math.Max(5, span / 10);
            int from = Math.Max(0, r.StartHd - padB), to = Math.Min(hd.Count - 1, r.EndHd + padB);
            if (!_ins.Load(hd, r.Key, from, to)) return;
            double lo = r.Low, hi = r.High;
            _ins.PriceRange(ref lo, ref hi);
            if (hi <= lo) return;

            Color col = WyKindColor(r);
            using var fTitle = new Font("Segoe UI", 10, FontStyle.Bold);
            using var fSmall = new Font("Segoe UI", 8, FontStyle.Regular);
            using var fPhase = new Font("Segoe UI", 9, FontStyle.Bold);
            using var fEvt = new Font("Consolas", 9, FontStyle.Bold);
            string title = $"🔍 {WyKindVn(r.Kind).ToUpperInvariant()} · {r.StartTime.AddHours(TzOffset):dd/MM HH:mm} → {r.EndTime.AddHours(TzOffset):dd/MM HH:mm}" +
                           $" · {Fmt(r.Low)}–{Fmt(r.High)} · {r.Events.Count} mốc · {span} nến";
            if (!_ins.Draw(gr, clip, lo, hi, title, col, fTitle, fSmall, TzOffset, Fmt, out var XI, out var YI)) return;
            _ui.CloseBox = _ins.CloseBox;
            // sơ đồ Wyckoff — CÙNG mã vẽ với chart chính (X nhận chỉ số nến thay vì thời gian)
            DrawWyckoff(gr, new List<WyRangeR> { r }, (t, hdIdx) => XI(hdIdx), YI, _ins.Plot, fPhase, fEvt, r.Key, false);
            gr.SetClip(clip);
            _ins.DrawTimeAxis(gr, fSmall, TzOffset, "nháy đúp lại dòng trong bảng (hoặc ✕) để đóng");
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
            public List<WyRangeR> WyRanges;
            public List<UiRow> EntryRows, RangeRows;
            public int TotalBars;
        }
    }
}
