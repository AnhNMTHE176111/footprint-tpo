// ============================================================================
//  RollingRobust — median + MAD cuốn theo N nến (tách khỏi OrderFlowBubbles.cs, perf 2026-11-11)
// ============================================================================
//  Cửa sổ = N NẾN gần nhất; mỗi nến đóng góp 1 mảng giá trị (per-level) hoặc 1 giá trị (per-bar).
//  Bản cũ: mỗi nến mới gom TOÀN BỘ cửa sổ vào mảng mới, Array.Sort, tạo mảng |x - median|, Array.Sort lần 2
//  (≈ 55-60 µs/nến cho 5 đối tượng = 4,3 s / 87k nến). Bản này giữ MỘT mảng đã sắp xếp: nến mới được trộn vào,
//  nến cũ bị gỡ ra (O(n) không sort); median lấy thẳng từ mảng; MAD = phần tử giữa của phép trộn 2 dãy tăng
//  (độ lệch của nửa trái đi ngược, nửa phải đi xuôi — không sort). Dùng ĐÚNG Math.Abs(x - median) và
//  0.5 * (a + b) như cũ nên KẾT QUẢ TRÙNG TỪNG BIT (tests/RollingRobustTests.cs so với bản cũ).
//  Class này KHÔNG tham chiếu TradingPlatform.BusinessLayer -> test độc lập được.
// ============================================================================
using System;
using System.Collections.Generic;

namespace OrderFlowBubbles
{
    internal sealed class RollingRobust
    {
        private readonly Queue<double[]> _bars = new();   // mỗi nến: bản sao ĐÃ SẮP XẾP của các giá trị nạp vào
        private readonly int _window;
        private double[] _sorted = new double[128];
        private int _n;
        private double _median, _mad;
        private bool _dirty = true;

        public RollingRobust(int window) { _window = Math.Max(1, window); }

        public int BarCount => _bars.Count;

        public void AddBar(double[] vals)
        {
            var mine = vals == null || vals.Length == 0 ? Array.Empty<double>() : (double[])vals.Clone();
            if (mine.Length > 1) Array.Sort(mine);
            _bars.Enqueue(mine);
            InsertSorted(mine);
            while (_bars.Count > _window) RemoveSorted(_bars.Dequeue());
            _dirty = true;
        }

        // trộn mảng đã sắp xếp b vào _sorted (từ cuối về đầu, tại chỗ)
        private void InsertSorted(double[] b)
        {
            int k = b.Length;
            if (k == 0) return;
            if (_n + k > _sorted.Length) Array.Resize(ref _sorted, Math.Max(_sorted.Length * 2, _n + k));
            int i = _n - 1, j = k - 1, w = _n + k - 1;
            while (j >= 0)
            {
                if (i >= 0 && _sorted[i].CompareTo(b[j]) > 0) _sorted[w--] = _sorted[i--];
                else _sorted[w--] = b[j--];
            }
            _n += k;
        }

        // gỡ mảng đã sắp xếp b (b là tập con của _sorted) khỏi _sorted (nén tại chỗ)
        private void RemoveSorted(double[] b)
        {
            int k = b.Length;
            if (k == 0) return;
            int j = 0, w = 0;
            for (int i = 0; i < _n; i++)
            {
                if (j < k && _sorted[i].CompareTo(b[j]) == 0) { j++; continue; }
                _sorted[w++] = _sorted[i];
            }
            _n = w;
        }

        private void Recompute()
        {
            _dirty = false;
            if (_n == 0) { _median = 0; _mad = 0; return; }
            var s = _sorted; int n = _n;
            _median = Med(s, n);
            double m = _median;
            // c = số phần tử <= median; trái: độ lệch m - s[c-1-j] (tăng dần); phải: s[c+j] - m (tăng dần)
            int lo = 0, hi = n;
            while (lo < hi) { int mid = (lo + hi) >> 1; if (s[mid].CompareTo(m) <= 0) lo = mid + 1; else hi = mid; }
            int c = lo, li = 0, ri = 0, rc = n - c;
            int target = n / 2;              // dev đã sắp xếp: lấy dev[target] (và dev[target-1] nếu n chẵn)
            double prev = 0, cur = 0;
            for (int t = 0; t <= target; t++)
            {
                prev = cur;
                if (li < c && (ri >= rc || (m - s[c - 1 - li]) <= (s[c + ri] - m))) cur = Math.Abs(s[c - 1 - li++] - m);
                else cur = Math.Abs(s[c + ri++] - m);
            }
            _mad = (n % 2 == 1) ? cur : 0.5 * (prev + cur);
        }

        private static double Med(double[] s, int len)
        {
            if (len <= 0) return 0;
            int mid = len / 2;
            return (len % 2 == 1) ? s[mid] : 0.5 * (s[mid - 1] + s[mid]);
        }

        public double Median { get { if (_dirty) Recompute(); return _median; } }

        public double ModZ(double x)
        {
            if (_dirty) Recompute();
            if (_mad > 1e-9) return 0.6745 * (x - _median) / _mad;   // modified z (robust)
            if (_median > 1e-9) return (x - _median) / _median;      // fallback khi MAD=0
            return 0;
        }
    }
}
