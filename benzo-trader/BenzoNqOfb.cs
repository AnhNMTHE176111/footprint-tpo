// ============================================================================
//  BenzoNqOfb — cầu nối lõi OrderFlowBubbles (chạy qua khe TEST) → NqSig + NqMachine, chạy TĂNG DẦN từng nến đã đóng.
//  Dùng chung cho indicator (BenzoTrader.cs) và tools/ReplayNq. build.sh đổi `OrderFlowBubbles.OrderFlowBubbles` → `BenzoOfLib.OfbCore`.
// ============================================================================
namespace BenzoTraderNs
{
    using System;
    using System.Collections.Generic;
    using TradingPlatform.BusinessLayer;
    using OfbCore = OrderFlowBubbles.OrderFlowBubbles;

    public sealed class NqRunner
    {
        readonly OfbCore _ofb;
        readonly Func<int, HistoryItemBar> _src;
        public readonly int StartAbs;    // nến tuyệt đối đầu tiên của máy setup (trước đó chỉ chạy OFB để có nền)
        public readonly List<NqBar> Bars = new();   // chỉ số máy = tuyệt đối − StartAbs
        public readonly NqSig Sig = new();
        public readonly NqMachine M;
        int _ofbCount;                   // TestBarCount hiện tại của lõi OFB (nến 0.._ofbCount-2 đã đóng)
        int _read;                       // nến tuyệt đối kế tiếp cần đọc dấu
        bool _loaded;

        /// <param name="src">nến tuyệt đối, 0 = cũ nhất</param>
        public NqRunner(Func<int, HistoryItemBar> src, double tick, string symbol, string cacheFile, int startAbs = 0, NqCfg cfg = null)
        {
            _src = src; StartAbs = startAbs;
            _ofb = new OfbCore
            {
                TestBarSource = src, TestTickSize = tick, TestSymbolName = symbol, TestBarMinutes = 1, TestCacheFile = cacheFile
            };
            M = new NqMachine(Bars, Sig, cfg);
        }

        /// <summary>total = số nến hiện có (gồm nến đang chạy). cold = lần đầu nạp NGUỘI cả lịch sử (indicator);
        /// false = lõi OFB chạy TĂNG DẦN từng nến như live (replay/parity).</summary>
        public void Advance(int total, bool cold)
        {
            if (total < 2) return;
            if (!_loaded)
            {
                _loaded = true;
                _ofbCount = cold ? total : 2;
                _ofb.TestBarCount = _ofbCount;
                _ofb.VolumeAnalysisData_Loaded();
            }
            while (true)
            {
                while (_read <= _ofbCount - 2)
                {
                    int k = _read++;
                    ReadBar(k, full: true);
                    for (int m = Math.Max(0, k - 2); m < k; m++) ReadBar(m, full: false);   // stop hunt đặt ở nến fail break (≤ 2 nến sau nến quét)
                    if (k < StartAbs) continue;
                    int rel = k - StartAbs;
                    Put(rel, _src(k)); Put(rel + 1, _src(k + 1));
                    M.Step(rel);
                }
                if (_ofbCount >= total) break;
                _ofbCount++; _ofb.TestBarCount = _ofbCount; _ofb.RunProcess();
            }
            RefreshForming(total);
        }

        /// <summary>Nến đang chạy: chỉ cập nhật OHLC để vẽ (máy setup không đọc nến chưa đóng).</summary>
        public void RefreshForming(int total)
        {
            if (total - 1 - StartAbs >= 0) Put(total - 1 - StartAbs, _src(total - 1));
        }

        void Put(int rel, HistoryItemBar b)
        {
            if (b == null) return;
            var nb = ToBar(b);
            if (rel < Bars.Count) Bars[rel] = nb; else if (rel == Bars.Count) Bars.Add(nb);
        }

        static NqBar ToBar(HistoryItemBar b)
        {
            var t = b.VolumeAnalysisData?.Total;
            return new NqBar { T = b.TimeLeft, O = b.Open, H = b.High, L = b.Low, C = b.Close, D = t?.Delta ?? 0.0, V = t?.Volume ?? 0.0 };
        }

        void ReadBar(int k, bool full)
        {
            int r = k - StartAbs;
            foreach (var x in _ofb.ExportBar(k))
            {
                switch (x.Kind)
                {
                    case OfbCore.ExportKind.StopHunt: Sig.AddSh(r, x.Side, x.Price); break;
                    case OfbCore.ExportKind.DotB: if (full) Sig.AddDot(r, 1, x.Price); break;
                    case OfbCore.ExportKind.DotS: if (full) Sig.AddDot(r, -1, x.Price); break;
                    case OfbCore.ExportKind.BigTrade: if (full) Sig.AddBt(r, x.Price, x.Side > 0 ? 1 : -1); break;
                    case OfbCore.ExportKind.ExhTop: if (full) Sig.ExhT.Add(r); break;
                    case OfbCore.ExportKind.ExhBottom: if (full) Sig.ExhB.Add(r); break;
                    case OfbCore.ExportKind.Zone: if (full) Sig.AddZone(r, x.Side, x.Price, x.PriceHi); break;
                }
            }
        }
    }
}
