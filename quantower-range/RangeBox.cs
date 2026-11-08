// ============================================================================
//  Range Box — tự kẻ RANGE theo cụm nến như CORVEN kẻ tay (Quantower / Optimus Flow)
// ============================================================================
//  Công cụ BỐI CẢNH, không phải máy bắn tín hiệu (CORVEN 0:16:25: "Cần range, chỉ là xác nhận thôi").
//  Chạy theo nến của chart đang mở: M1 ra range M1, muốn range to thì mở M15 (CORVEN 0:13:58).
//  Chỉ dùng OHLC — KHÔNG cần Volume Analysis.
//
//  Logic thuần: RangeLogic.cs (port 1:1 từ research/range_proto.py, đối chiếu 100 % events_90d.csv).
//  Vẽ: RangeRenderer.cs (test render ra PNG không cần Quantower).
//  Vòng đời: OnClear (đổi Settings / nạp lại lịch sử) → xoá logic, tính lại từ đầu ở OnUpdate kế tiếp.
//  Chỉ nến ĐÃ ĐÓNG đi vào logic; nến đang chạy chỉ kéo dài hộp đang hiệu lực khi vẽ.
// ============================================================================
namespace RangeBox
{
    using System;
    using System.Drawing;
    using TradingPlatform.BusinessLayer;
    using TradingPlatform.BusinessLayer.Chart;

    public class RangeBox : Indicator
    {
        [InputParameter("Hiện range đã phá", 10)]
        public bool ShowBroken { get; set; } = true;

        [InputParameter("Đánh dấu fail break", 20)]
        public bool MarkFailBreak { get; set; } = true;

        [InputParameter("Đánh dấu râu quét cạnh", 30)]
        public bool MarkStopHunt { get; set; } = false;

        private readonly object _lock = new object();
        private RangeLogic _logic;
        private int _fed;                 // số nến đã nạp vào logic (= chỉ số nến kế tiếp)
        private DateTime _firstTime;      // thời gian nến 0 lúc nạp — đổi (tải thêm lịch sử bên trái) thì tính lại

        public RangeBox() : base()
        {
            Name = "Range Box";
            Description = "Tự kẻ range theo cụm đỉnh/đáy (cách CORVEN). Hộp xanh = đang hiệu lực, xám đứt = đã phá; ▼/▲ = fail break.";
            SeparateWindow = false;
            OnBackGround = true;
        }

        protected override void OnInit() { lock (_lock) Reset(); }

        protected override void OnClear() { lock (_lock) Reset(); }

        private void Reset() { _logic = null; _fed = 0; _firstTime = default; }

        private HistoryItemBar Bar(int i)
            => (HistoricalData != null && i >= 0 && i < HistoricalData.Count) ? HistoricalData[i, SeekOriginHistory.Begin] as HistoryItemBar : null;

        protected override void OnUpdate(UpdateArgs args)
        {
            lock (_lock) Process();
        }

        /// <summary>Nạp mọi nến ĐÃ ĐÓNG chưa nạp. Gọi trong _lock.</summary>
        private void Process()
        {
            double tick = Symbol?.TickSize ?? 0;
            if (!(tick > 0) || HistoricalData == null) return;
            int total = HistoricalData.Count;
            if (total == 0) return;
            var b0 = Bar(0);
            if (b0 == null) return;
            if (_logic == null || _logic.Tick != tick || (_fed > 0 && b0.TimeLeft != _firstTime))
            {
                _logic = new RangeLogic(tick);
                _fed = 0;
                _firstTime = b0.TimeLeft;
            }
            int closed = total - 1;      // trừ nến đang chạy
            if (closed < _fed) { _logic = new RangeLogic(tick); _fed = 0; _firstTime = b0.TimeLeft; }
            for (int i = _fed; i < closed; i++)
            {
                var b = Bar(i);
                if (b == null) break;
                _logic.Feed(b.Open, b.High, b.Low, b.Close);
                _fed = i + 1;
            }
        }

        private sealed class QtMap : IChartMap
        {
            private readonly RangeBox _ind; private readonly IChartWindowCoordinatesConverter _conv;
            private readonly int _last; private readonly double _bw;
            public QtMap(RangeBox ind, IChartWindowCoordinatesConverter conv, int last, double bw, Rectangle clip)
            { _ind = ind; _conv = conv; _last = last; _bw = bw; Clip = clip; }
            public float BarWidth => (float)_bw;
            public RectangleF Clip { get; }
            public float X(int idx)
            {
                if (idx > _last)
                {
                    var lb = _ind.Bar(_last);
                    return lb == null ? 0f : (float)(_conv.GetChartX(lb.TimeLeft) + _bw / 2.0 + (idx - _last) * _bw);
                }
                var b = _ind.Bar(Math.Max(0, idx));
                return b == null ? 0f : (float)(_conv.GetChartX(b.TimeLeft) + _bw / 2.0);
            }
            public float Y(double price) => (float)_conv.GetChartY(price);
        }

        public override void OnPaintChart(PaintChartEventArgs args)
        {
            base.OnPaintChart(args);
            if (CurrentChart == null || HistoricalData == null) return;
            var win = CurrentChart.Windows[args.WindowIndex];
            if (!win.IsMainWindow) return;
            var conv = win.CoordinatesConverter;
            var clip = win.ClientRectangle;
            int last = HistoricalData.Count - 1;
            if (last < 0) return;
            int li = (int)conv.GetBarIndex(conv.GetTime(clip.Left));
            int ri = (int)Math.Ceiling(conv.GetBarIndex(conv.GetTime(clip.Right)));
            var opt = new RenderOptions { ShowBroken = ShowBroken, MarkFailBreak = MarkFailBreak, MarkStopHunt = MarkStopHunt };
            RenderScene scene;
            lock (_lock)
            {
                if (_logic == null) return;
                opt.RetestBars = _logic.P.G;
                scene = RangeRenderer.BuildScene(_logic, last, li - 1, ri + 1, opt);
            }
            var gr = args.Graphics;
            var prev = gr.ClipBounds;
            gr.SetClip(clip);
            try
            {
                var map = new QtMap(this, conv, last, CurrentChart.BarsWidth, clip);
                // Quantower truyền Point.Empty khi chưa có sự kiện rê chuột (ChartCustomDrawingRenderer) ⇒ coi như không có chuột
                var mp = args.MousePosition;
                Point? mouse = (mp == Point.Empty || !clip.Contains(mp)) ? (Point?)null : mp;
                RangeRenderer.Draw(gr, map, scene, opt, mouse);
            }
            finally { gr.SetClip(prev); }
        }
    }
}
