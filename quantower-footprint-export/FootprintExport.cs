// ============================================================================
//  Footprint Export (CSV)  —  indicator XUẤT DỮ LIỆU cho QUANTOWER / Optimus Flow
// ============================================================================
//  Quantower/Optimus Flow KHÔNG có nút "export footprint": History Exporter chỉ
//  ra OHLCV, còn export của chart chỉ ra TỔNG HỢP THEO NẾN (Buy/Sell volume,
//  delta của cả nến) — MẤT phân bố theo từng mức giá. Indicator này lấy đúng
//  cái đang thiếu: bid/ask/delta/trades TỪNG MỨC GIÁ × TỪNG NẾN → CSV.
//
//  ---- CÁCH DÙNG (tóm tắt, chi tiết ở README.md) ------------------------------
//   1. Mở chart symbol + timeframe + khoảng lịch sử MUỐN XUẤT (chart nạp bao
//      nhiêu thì xuất được bấy nhiêu — platform chỉ tính Volume Analysis cho
//      phần đã nạp).
//   2. Add indicator → chờ Volume Analysis nạp xong 100%.
//   3. Bật "XUẤT NGAY" → OK. Xuất chạy ở THREAD RIÊNG (không đứng máy).
//      Trạng thái hiện góc trên-trái chart. Xong thì tắt lại công tắc đó.
//
//  ---- 2 FILE RA ---------------------------------------------------------------
//   fp_<symbol>_<period>_<stamp>.csv       ← 1 dòng / (nến × mức giá)  [footprint]
//   fp_..._bars.csv                        ← 1 dòng / nến (OHLC + tổng VA + POC)
//   Ghép 2 file bằng cột bar_idx (KHÔNG dùng datetime: chart theo tick/volume có
//   thể trùng TimeLeft).
//
//  ---- AN TOÀN THREAD ---------------------------------------------------------
//  Mảng tham chiếu nến được CHỤP trên thread của platform (tránh race khi
//  HistoricalData nới mảng nội bộ), rồi mới bàn cho thread xuất. Chỉ xuất nến ĐÃ
//  ĐÓNG (nến đang chạy phải bật riêng) vì nến đã đóng không còn bị ghi thêm.
//  _status là volatile: thread xuất ghi, thread vẽ đọc.
//
//  ---- API ĐÃ KIỂM CHỨNG trên TradingPlatform.BusinessLayer.dll v1.146.16 -----
//  bar.VolumeAnalysisData.PriceLevels : Dictionary<double, VolumeAnalysisItem>
//  bar.VolumeAnalysisData.Total       : VolumeAnalysisItem
//  VolumeAnalysisItem: BuyVolume/SellVolume/Volume/Delta/DeltaFinish/MaxDelta/
//    MinDelta/CumulativeDelta/Trades/BuyTrades/SellTrades/MaxOneTradeVolume/
//    AverageSize/AverageBuySize/AverageSellSize
//  HistoricalData.VolumeAnalysisCalculationProgress.State == Finished  (guard)
// ============================================================================

namespace FootprintExport
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Globalization;
    using System.IO;
    using System.Text;
    using System.Threading;
    using TradingPlatform.BusinessLayer;

    public class FootprintExport : Indicator, IVolumeAnalysisIndicator
    {
        // ==================== INPUT ====================
        [InputParameter("Đường dẫn xuất (file .csv HOẶC thư mục; rỗng = Documents\\FootprintExport)", 10)]
        public string ExportPath { get; set; } = "";

        [InputParameter("Gộp mấy tick / hàng (1 = từng tick, như footprint gốc)", 20, 1, 100, 1, 0)]
        public int TicksPerRow { get; set; } = 1;

        [InputParameter("Chỉ xuất N nến gần nhất (0 = tất cả nến đã nạp)", 21, 0, 2000000, 100, 0)]
        public int MaxBars { get; set; } = 0;

        [InputParameter("Từ ngày (yyyy-MM-dd, rỗng = không giới hạn)", 22)]
        public string FromDay { get; set; } = "";

        [InputParameter("Đến ngày (yyyy-MM-dd, tính hết ngày; rỗng = không giới hạn)", 23)]
        public string ToDay { get; set; } = "";

        [InputParameter("Lệch giờ ghi vào CSV (UTC → local, giờ)", 24, -12, 14, 1, 0)]
        public int TzOffset { get; set; } = 0;

        [InputParameter("Ký tự phân cách ( ,  ;  |  t=tab )", 25)]
        public string SepText { get; set; } = ",";

        [InputParameter("Xuất thêm file tổng hợp theo NẾN (_bars.csv)", 26)]
        public bool ExportBarsFile { get; set; } = true;

        [InputParameter("Gồm cả nến ĐANG CHẠY (chưa đóng)", 27)]
        public bool IncludeLiveBar { get; set; } = false;

        [InputParameter("Tự xuất ngay khi nạp xong Volume Analysis", 30)]
        public bool AutoExport { get; set; } = false;

        [InputParameter("XUẤT NGAY (bật → OK; xong thì tắt lại)", 31)]
        public bool ExportNow { get; set; } = false;

        [InputParameter("Hiện trạng thái trên chart", 40)]
        public bool ShowStatus { get; set; } = true;

        // ==================== trạng thái ====================
        private volatile string _status = "chờ Volume Analysis…";
        private int _busy;                  // 0/1 — Interlocked, chống chạy 2 lần chồng nhau
        // Cấu hình đã xuất xong. Đặt trên thread platform, có thể bị thread xuất đặt lại null khi
        // lỗi (để cho phép thử lại) → volatile. Đổi BẤT KỲ setting nào = key khác = xuất lại.
        private volatile string _doneCfg;

        public FootprintExport() : base()
        {
            Name = "Footprint Export (CSV)";
            Description = "Xuất footprint (bid/ask/delta/trades THEO TỪNG MỨC GIÁ và từng nến) ra CSV. "
                        + "Cần Volume Analysis. Bật 'XUẤT NGAY' để chạy.";
            SeparateWindow = false;
        }

        // ==================== Volume Analysis ====================
        public bool IsRequirePriceLevelsCalculation => true;

        public void VolumeAnalysisData_Loaded()
        {
            _status = "Volume Analysis đã nạp — bật 'XUẤT NGAY' để xuất.";
            if (AutoExport) TryStart();
        }

        protected override void OnClear()
        {
            _status = "chờ Volume Analysis…";
            // KHÔNG xoá _doneCfg: tránh xuất lại y nguyên khi platform recalc.
        }

        protected override void OnUpdate(UpdateArgs args)
        {
            // CỐ Ý không đòi _vaLoaded: cờ đó bị OnClear xoá mỗi lần platform recalc, và nếu
            // sự kiện VolumeAnalysisData_Loaded không bắn lại (VA đã cache) thì indicator sẽ
            // treo ở "chờ Volume Analysis" vĩnh viễn. Điều kiện THẬT là
            // VolumeAnalysisCalculationProgress.State == Finished — TryStart tự kiểm.
            if (!ExportNow) return;
            TryStart();
        }

        // ==================== khởi động xuất ====================
        private sealed class Cfg
        {
            public string Path, Symbol, Period, Sep, From, To;
            public int TicksPerRow, MaxBars, Tz;
            public bool Bars, Live;
            public double Tick;
            public string Key() =>
                $"{Symbol}|{Period}|{Path}|{TicksPerRow}|{MaxBars}|{Tz}|{Sep}|{Bars}|{Live}|{From}|{To}";
        }

        private void TryStart()
        {
            if (HistoricalData == null || Symbol == null) return;
            var prog = HistoricalData.VolumeAnalysisCalculationProgress;
            if (prog == null || prog.State != VolumeAnalysisCalculationState.Finished)
            {
                _status = prog == null ? "chưa có Volume Analysis" : $"đang nạp Volume Analysis {prog.ProgressPercent}%…";
                return;
            }

            var cfg = new Cfg
            {
                Path = (ExportPath ?? "").Trim(),
                Symbol = Symbol.Name,
                Period = HistoricalData.Aggregation?.Title ?? HistoricalData.Aggregation?.Name ?? "period",
                Sep = SepText ?? ",",
                From = (FromDay ?? "").Trim(),
                To = (ToDay ?? "").Trim(),
                TicksPerRow = Math.Max(1, TicksPerRow),
                MaxBars = Math.Max(0, MaxBars),
                Tz = TzOffset,
                Bars = ExportBarsFile,
                Live = IncludeLiveBar,
                Tick = Symbol.TickSize
            };
            if (cfg.Key() == _doneCfg) return;                      // đã xuất đúng cấu hình này
            if (Interlocked.CompareExchange(ref _busy, 1, 0) != 0) return;

            HistoryItemBar[] snap;
            try
            {
                snap = Snapshot(cfg);
            }
            catch (Exception ex)
            {
                _status = "LỖI chụp dữ liệu: " + ex.Message;
                Interlocked.Exchange(ref _busy, 0);
                return;
            }

            _doneCfg = cfg.Key();                                   // chặn tái kích hoạt mỗi tick
            if (cfg.Tick <= 0 || !double.IsFinite(cfg.Tick)) cfg.Tick = InferTick(snap);

            var th = new Thread(() => RunExport(snap, cfg)) { IsBackground = true, Name = "FootprintExport" };
            th.Start();
        }

        /// <summary>Chụp MẢNG THAM CHIẾU nến trên thread platform (chỉ nến đã đóng, trừ khi bật Live).</summary>
        private HistoryItemBar[] Snapshot(Cfg cfg)
        {
            int total = HistoricalData.Count;
            int end = cfg.Live ? total : total - 1;                 // exclusive
            if (end < 0) end = 0;
            int start = (cfg.MaxBars > 0 && end - cfg.MaxBars > 0) ? end - cfg.MaxBars : 0;
            var arr = new HistoryItemBar[Math.Max(0, end - start)];
            for (int i = start; i < end; i++)
                arr[i - start] = HistoricalData[i, SeekOriginHistory.Begin] as HistoryItemBar;
            return arr;
        }

        /// <summary>TickSize không có (vài feed) → suy ra từ khoảng cách nhỏ nhất giữa 2 mức giá liền kề.</summary>
        private static double InferTick(HistoryItemBar[] bars)
        {
            double best = double.MaxValue;
            int scanned = 0;
            foreach (var b in bars)
            {
                var pl = b?.VolumeAnalysisData?.PriceLevels;
                if (pl == null || pl.Count < 2) continue;
                var prices = new List<double>(pl.Keys);
                prices.Sort();
                for (int i = 1; i < prices.Count; i++)
                {
                    double g = prices[i] - prices[i - 1];
                    if (g > 1e-10 && g < best) best = g;
                }
                if (++scanned >= 50) break;
            }
            return (best < double.MaxValue) ? best : 0.01;
        }

        // ==================== thread xuất ====================
        private void RunExport(HistoryItemBar[] bars, Cfg cfg)
        {
            string levelsPath = null, barsPath = null;
            var t0 = DateTime.UtcNow;
            try
            {
                if (bars.Length == 0)
                {
                    _doneCfg = null;                                 // trạng thái tạm — cho thử lại
                    _status = "không có nến ĐÃ ĐÓNG để xuất";
                    return;
                }

                char sep = FpCore.SepFrom(cfg.Sep);
                int digits = FpCore.DigitsFromTick(cfg.Tick);
                DateTime? from = FpCore.TryParseDay(cfg.From, out var fd) ? fd : (DateTime?)null;
                DateTime? to = FpCore.TryParseDay(cfg.To, out var td) ? td : (DateTime?)null;
                bool badFrom = cfg.From.Length > 0 && !from.HasValue;
                bool badTo = cfg.To.Length > 0 && !to.HasValue;

                string defDir = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "FootprintExport");
                string stamp = DateTime.Now.ToString("yyyyMMdd_HHmmss", CultureInfo.InvariantCulture);
                FpCore.MakeNames(cfg.Path, defDir, cfg.Symbol, cfg.Period, stamp, out levelsPath, out barsPath);
                string dir = Path.GetDirectoryName(levelsPath);
                if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

                long rows = 0, barsOut = 0, skippedNoVa = 0, skippedRange = 0, skippedUnstable = 0;
                bool capped = false;
                var utf8 = new UTF8Encoding(false);                  // KHÔNG BOM: pandas/numpy đọc sạch
                var sbL = new StringBuilder(1 << 16);                // buffer file MỨC GIÁ
                var sbB = new StringBuilder(1 << 14);                // buffer file NẾN (riêng — không lẫn)
                var raw = new List<FpLevel>(64);

                using (var wl = new StreamWriter(new FileStream(levelsPath, FileMode.Create, FileAccess.Write,
                                                                FileShare.Read, 1 << 20), utf8))
                using (var wb = cfg.Bars
                        ? new StreamWriter(new FileStream(barsPath, FileMode.Create, FileAccess.Write,
                                                          FileShare.Read, 1 << 18), utf8)
                        : null)
                {
                    wl.Write(FpCore.LevelsHeader(sep)); wl.Write('\n');
                    wb?.Write(FpCore.BarsHeader(sep)); wb?.Write('\n');

                    for (int i = 0; i < bars.Length; i++)
                    {
                        var bar = bars[i];
                        if (bar == null) { skippedNoVa++; continue; }

                        DateTime tLocal = bar.TimeLeft.AddHours(cfg.Tz);
                        if (!FpCore.InRange(tLocal, from, to)) { skippedRange++; continue; }

                        var va = bar.VolumeAnalysisData;
                        var pl = va?.PriceLevels;
                        if (pl == null || pl.Count == 0) { skippedNoVa++; continue; }

                        // PriceLevels là Dictionary do platform giữ. Nếu người dùng cuộn chart /
                        // nạp thêm lịch sử GIỮA lúc xuất, platform có thể tính lại VA → foreach
                        // ném "Collection was modified". Thà BỎ nến đó (và báo số lượng) hơn là
                        // huỷ cả lần xuất. Thử lại 1 lần trước khi bỏ.
                        if (!TryReadLevels(pl, cfg.Tick, raw) && !TryReadLevels(pl, cfg.Tick, raw))
                        { skippedUnstable++; continue; }
                        if (raw.Count == 0) { skippedNoVa++; continue; }

                        var levels = FpCore.Aggregate(raw, cfg.TicksPerRow);
                        string dt = FpCore.FmtTime(tLocal);
                        int barIdx = (int)barsOut;

                        foreach (var lv in levels)
                        {
                            FpCore.AppendLevelRow(sbL, sep, barIdx, dt,
                                                  FpCore.PriceOf(lv.Tick, cfg.Tick), lv, digits);
                            rows++;
                        }

                        if (wb != null)
                        {
                            int pi = FpCore.PocIndex(levels);
                            var tot = va.Total;
                            var fb = new FpBar
                            {
                                Idx = barIdx,
                                Dt = dt,
                                Open = bar.Open, High = bar.High, Low = bar.Low, Close = bar.Close,
                                BarVolume = bar.Volume, BarTicks = bar.Ticks,
                                OpenInterest = FpCore.FixPrimer(bar.OpenInterest, 0),
                                Levels = levels.Count,
                                PocPrice = pi >= 0 ? FpCore.PriceOf(levels[pi].Tick, cfg.Tick) : 0,
                                PocVolume = pi >= 0 ? levels[pi].Volume : 0
                            };
                            if (tot != null)
                            {
                                fb.BidVol = tot.SellVolume;
                                fb.AskVol = tot.BuyVolume;
                                fb.Volume = tot.Volume;
                                fb.Delta = tot.Delta;
                                fb.DeltaFinish = FpCore.FixPrimer(tot.DeltaFinish, tot.Delta);
                                fb.MaxDelta = FpCore.FixPrimer(tot.MaxDelta, tot.Delta);
                                fb.MinDelta = FpCore.FixPrimer(tot.MinDelta, tot.Delta);
                                fb.CumDelta = FpCore.FixPrimer(tot.CumulativeDelta, 0);
                                fb.Trades = tot.Trades;
                                fb.BuyTrades = tot.BuyTrades;
                                fb.SellTrades = tot.SellTrades;
                                fb.MaxOneTrade = FpCore.FixPrimer(tot.MaxOneTradeVolume, 0);
                                fb.AvgSize = FpCore.FixPrimer(tot.AverageSize, 0);
                                fb.AvgBuySize = FpCore.FixPrimer(tot.AverageBuySize, 0);
                                fb.AvgSellSize = FpCore.FixPrimer(tot.AverageSellSize, 0);
                            }
                            FpCore.AppendBarRow(sbB, sep, fb, digits);
                        }
                        barsOut++;

                        if (sbL.Length > 1 << 18) Flush(sbL, wl);
                        if (sbB.Length > 1 << 16) Flush(sbB, wb);
                        if ((i & 1023) == 0)
                            _status = $"đang xuất… {i * 100L / bars.Length}%  ({rows:N0} dòng)";
                        if (rows >= FpCore.MaxRowsHardCap) { capped = true; break; }
                    }
                    Flush(sbL, wl);
                    Flush(sbB, wb);
                }

                double sec = (DateTime.UtcNow - t0).TotalSeconds;
                double mb = SafeMb(levelsPath);
                var msg = new StringBuilder();
                // 0 dòng KHÔNG được báo "XONG" màu xanh — dễ tưởng xuất thành công rồi đi phân tích file rỗng.
                bool empty = rows == 0;
                msg.Append(empty
                    ? "LỖI: KHÔNG XUẤT ĐƯỢC DÒNG NÀO — kiểm lại lọc ngày / lệch giờ / feed có volume thật?"
                    : $"XONG: {barsOut:N0} nến · {rows:N0} dòng · {mb:0.0} MB · {sec:0.0}s");
                if (capped) msg.Append($" · ⚠ ĐÃ CẮT ở trần {FpCore.MaxRowsHardCap:N0} dòng — thu hẹp khoảng / tăng tick/hàng");
                if (skippedNoVa > 0) msg.Append($" · bỏ {skippedNoVa:N0} nến không có VA");
                if (skippedRange > 0) msg.Append($" · lọc ngày bỏ {skippedRange:N0} nến");
                if (skippedUnstable > 0) msg.Append($" · ⚠ bỏ {skippedUnstable:N0} nến vì VA bị tính lại giữa lúc xuất (đừng cuộn chart khi đang xuất) — nên xuất lại");
                if (badFrom) msg.Append(" · ⚠ 'Từ ngày' sai định dạng → BỎ QUA");
                if (badTo) msg.Append(" · ⚠ 'Đến ngày' sai định dạng → BỎ QUA");
                Log(msg + " → " + levelsPath, cfg, digits);
                // Banner chỉ hiện TÊN file (đường dẫn đầy đủ nằm trong export_log.txt) cho gọn.
                _status = msg + " → " + Path.GetFileName(levelsPath);
            }
            catch (Exception ex)
            {
                _doneCfg = null;                                     // cho phép thử lại
                // File đã ghi dở PHẢI bị đổi tên: một CSV cắt giữa dòng trông y như file hoàn chỉnh,
                // đem đi phân tích là hỏng cả nghiên cứu mà không ai biết.
                string marked = MarkIncomplete(levelsPath) + " / " + MarkIncomplete(barsPath);
                _status = "LỖI xuất CSV: " + ex.Message + " · file ghi dở đã đổi tên .INCOMPLETE";
                Log("LỖI: " + ex + " | file dở: " + marked, cfg, 0);
            }
            finally
            {
                Interlocked.Exchange(ref _busy, 0);
            }
        }

        /// <summary>Đẩy buffer ra đĩa. Mỗi file 1 buffer RIÊNG → không thể lẫn dòng giữa 2 file.</summary>
        private static void Flush(StringBuilder sb, StreamWriter w)
        {
            if (w == null || sb.Length == 0) return;
            w.Write(sb);                    // overload StringBuilder: không copy ra string trung gian
            sb.Clear();
        }

        /// <summary>Đọc PriceLevels của 1 nến vào 'raw'. false = dictionary bị sửa giữa lúc đọc.</summary>
        private static bool TryReadLevels(Dictionary<double, VolumeAnalysisItem> pl, double tick, List<FpLevel> raw)
        {
            raw.Clear();
            try
            {
                foreach (var kv in pl)
                {
                    var it = kv.Value;
                    if (it == null) continue;
                    raw.Add(new FpLevel
                    {
                        Tick = FpCore.ToTick(kv.Key, tick),
                        BidVol = it.SellVolume,             // khớp ở BID = bán chủ động
                        AskVol = it.BuyVolume,              // khớp ở ASK = mua chủ động
                        Volume = it.Volume,
                        Delta = it.Delta,
                        Trades = it.Trades,
                        BuyTrades = it.BuyTrades,
                        SellTrades = it.SellTrades,
                        MaxOneTrade = FpCore.FixPrimer(it.MaxOneTradeVolume, 0)
                    });
                }
                return true;
            }
            catch (InvalidOperationException) { raw.Clear(); return false; }   // collection modified
            catch (NullReferenceException) { raw.Clear(); return false; }      // bar bị thay giữa lúc đọc
        }

        private static double SafeMb(string path)
        {
            try { return new FileInfo(path).Length / 1048576.0; } catch { return 0; }
        }

        /// <summary>Đổi tên file ghi dở thành *.INCOMPLETE để không bị dùng lẫn như file hoàn chỉnh.</summary>
        private static string MarkIncomplete(string path)
        {
            try
            {
                if (string.IsNullOrEmpty(path) || !File.Exists(path)) return "-";
                string dst = path + ".INCOMPLETE";
                if (File.Exists(dst)) File.Delete(dst);
                File.Move(path, dst);
                return Path.GetFileName(dst);
            }
            catch { return Path.GetFileName(path ?? "-") + " (không đổi tên được)"; }
        }

        private void Log(string msg, Cfg cfg, int digits)
        {
            try
            {
                string dir = Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "FootprintExport");
                Directory.CreateDirectory(dir);
                string line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss}\t{cfg.Symbol}\t{cfg.Period}"
                            + $"\ttick={cfg.Tick.ToString(CultureInfo.InvariantCulture)}\tdigits={digits}"
                            + $"\ttpr={cfg.TicksPerRow}\ttz={cfg.Tz}\t{msg}\n";
                File.AppendAllText(Path.Combine(dir, "export_log.txt"), line, new UTF8Encoding(false));
            }
            catch { }
        }

        // ==================== trạng thái trên chart ====================
        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (!ShowStatus || CurrentChart == null) return;
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;

            string txt = "Footprint Export · " + (_status ?? "");
            var gr = args.Graphics;
            using var font = new Font("Arial", 9, FontStyle.Bold);
            var sz = gr.MeasureString(txt, font);
            var rect = win.ClientRectangle;
            float x = rect.Left + 8, y = rect.Top + 6;
            using var bg = new SolidBrush(Color.FromArgb(180, 0, 0, 0));
            gr.FillRectangle(bg, x - 4, y - 2, sz.Width + 8, sz.Height + 4);
            bool ok = _status != null && _status.StartsWith("XONG");
            bool err = _status != null && _status.StartsWith("LỖI");
            using var fg = new SolidBrush(err ? Color.OrangeRed : ok ? Color.LightGreen : Color.Gainsboro);
            gr.DrawString(txt, font, fg, x, y);
        }
    }
}
