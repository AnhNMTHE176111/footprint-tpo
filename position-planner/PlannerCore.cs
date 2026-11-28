// ============================================================================
//  PlannerCore — lõi thuần của công cụ "Position Planner" (không phụ thuộc Quantower, test được bằng tests/)
// ============================================================================
//  Một lệnh = giá vào, SL, TP, thời gian bắt đầu T0 và kết thúc T1 (bề ngang hộp).
//  4 điểm kéo:
//    • giữa-trái  (giá vào): kéo CAO THẤP (đổi giá vào) và NGANG (dời T0, giữ bề ngang)
//    • trên-trái / dưới-trái (TP hoặc SL): chỉ kéo CAO THẤP
//    • giữa-phải: chỉ kéo NGANG (đổi T1 = bề ngang)
//  Nhãn: "SL 15 điểm", "TP 35,25 điểm", "R:R 1 : 2,35". 1 điểm = 1,0 giá.
//  ĐƯỢC CONCAT với PositionPlanner.cs khi build → mọi `using` nằm BÊN TRONG namespace.
// ============================================================================
namespace PositionPlannerNs
{
    using System;
    using System.Collections.Generic;
    using System.Drawing;
    using System.Globalization;
    using System.Text;

    public sealed class VlPos
    {
        public long Id;
        public int Side;            // +1 long, -1 short
        public double Entry, Sl, Tp;
        public DateTime T0, T1;
        public double SlPts => Math.Abs(Entry - Sl);
        public double TpPts => Math.Abs(Tp - Entry);
        public double RR => SlPts > 0 ? TpPts / SlPts : 0;
        public VlPos Clone() => (VlPos)MemberwiseClone();
    }

    /// <summary>Ánh xạ toạ độ của chart (lớp dán cài bằng CoordinatesConverter; test cài tuyến tính).</summary>
    public interface IVlMap
    {
        float X(DateTime t);
        float Y(double price);
        double Price(float y);
        DateTime Time(float x);
        TimeSpan Bar { get; }
    }

    public struct VlBar
    {
        public DateTime T; public double H, L, C;
        public VlBar(DateTime t, double h, double l, double c) { T = t; H = h; L = l; C = c; }
    }

    /// <summary>Đường giá chạy theo lệnh: từ (T0, giá vào) tới nến chạm SL/TP, hoặc nến cuối trong hộp (giá đóng).</summary>
    public struct VlPath
    {
        public bool Ok;
        public DateTime EndT; public double EndPrice;
        public int Hit;              // +1 chạm TP, -1 chạm SL, 0 chưa chạm
        /// <summary>+1 giá cuối đang ở phía lãi (tô đậm vùng TP), -1 phía lỗ (tô đậm vùng SL), 0 đúng giá vào.</summary>
        public int Side(VlPos p) => Math.Sign((EndPrice - p.Entry) * p.Side);
    }

    public static class VlTrack
    {
        /// <summary>bars tăng dần theo thời gian. Xét các nến có T0 ≤ T ≤ T1. Cùng nến chạm cả SL và TP → tính SL (thận trọng).</summary>
        public static VlPath Run(VlPos p, IReadOnlyList<VlBar> bars)
        {
            var r = new VlPath();
            foreach (var b in bars)
            {
                if (b.T < p.T0) continue;
                if (b.T > p.T1) break;
                bool sl = p.Side > 0 ? b.L <= p.Sl : b.H >= p.Sl;
                bool tp = p.Side > 0 ? b.H >= p.Tp : b.L <= p.Tp;
                r.Ok = true; r.EndT = b.T;
                if (sl) { r.Hit = -1; r.EndPrice = p.Sl; return r; }
                if (tp) { r.Hit = 1; r.EndPrice = p.Tp; return r; }
                r.EndPrice = b.C;
            }
            return r;
        }
    }

    public enum VlPart { None, Entry, Sl, Tp, Right, Close, Body }
    public enum VlMode { Idle, PlaceEntry, PlaceSl, PlaceTp, Drag }

    public static class VlFmt
    {
        private static readonly CultureInfo Vi = CultureInfo.GetCultureInfo("vi-VN");
        public static string Pts(double v) => Math.Round(v, 2).ToString("0.##", Vi);
        public static string SlText(VlPos p) => "SL " + Pts(p.SlPts) + " điểm";
        public static string TpText(VlPos p) => "TP " + Pts(p.TpPts) + " điểm";
        public static string RrText(VlPos p) => "R:R 1 : " + Math.Round(p.RR, 2).ToString("0.00", Vi);

        public static string Save(IEnumerable<VlPos> items)
        {
            var sb = new StringBuilder();
            var inv = CultureInfo.InvariantCulture;
            foreach (var p in items)
                sb.Append(p.Id).Append(';').Append(p.Side).Append(';')
                  .Append(p.Entry.ToString("R", inv)).Append(';').Append(p.Sl.ToString("R", inv)).Append(';').Append(p.Tp.ToString("R", inv)).Append(';')
                  .Append(p.T0.Ticks).Append(';').Append(p.T1.Ticks).Append('\n');
            return sb.ToString();
        }

        public static List<VlPos> Load(string text)
        {
            var list = new List<VlPos>();
            if (string.IsNullOrEmpty(text)) return list;
            var inv = CultureInfo.InvariantCulture;
            foreach (var line in text.Split('\n'))
            {
                var a = line.Trim().Split(';');
                if (a.Length != 7) continue;
                try
                {
                    var p = new VlPos
                    {
                        Id = long.Parse(a[0], inv), Side = int.Parse(a[1], inv) >= 0 ? 1 : -1,
                        Entry = double.Parse(a[2], inv), Sl = double.Parse(a[3], inv), Tp = double.Parse(a[4], inv),
                        T0 = new DateTime(long.Parse(a[5], inv), DateTimeKind.Utc), T1 = new DateTime(long.Parse(a[6], inv), DateTimeKind.Utc)
                    };
                    if (p.T1 > p.T0) list.Add(p);
                }
                catch { }
            }
            return list;
        }
    }

    /// <summary>Hình học một lệnh trên màn hình (px). Dùng chung cho vẽ và bắt chuột.</summary>
    public struct VlGeo
    {
        public float X0, X1, YE, YSl, YTp;
        public float Top => Math.Min(YSl, YTp);
        public float Bot => Math.Max(YSl, YTp);
        public PointF HEntry => new PointF(X0, YE);
        public PointF HSl => new PointF(X0, YSl);
        public PointF HTp => new PointF(X0, YTp);
        public PointF HRight => new PointF(X1, YE);
        public RectangleF Close => new RectangleF(X1 + 4, Top - 2, 14, 14);
    }

    public sealed class VlButton
    {
        public string Key, Text;
        public RectangleF Box;
    }

    /// <summary>Máy trạng thái: thanh nút (Long / Short / Xoá hết), đặt lệnh 3 lần bấm, kéo 4 điểm, xoá.</summary>
    public sealed class VlEditor
    {
        public const float HandleR = 5f, HitR = 9f;
        public readonly List<VlPos> Items = new();
        public double Tick = 0.25;
        public VlMode Mode { get; private set; } = VlMode.Idle;
        public int PendingSide { get; private set; }
        public VlPos Draft { get; private set; }
        public long HoverId = -1; public VlPart HoverPart = VlPart.None;
        public bool Dirty;                       // có thay đổi cần lưu
        public readonly List<VlButton> Buttons = new();

        private long _nextId = 1;
        private VlPos _drag; private VlPart _dragPart;
        private TimeSpan _dragDur; private float _grabDx;

        public void SetItems(IEnumerable<VlPos> items)
        {
            Items.Clear(); Items.AddRange(items);
            foreach (var p in Items) if (p.Id >= _nextId) _nextId = p.Id + 1;
        }

        public void LayoutButtons(float left, float top)
        {
            Buttons.Clear();
            float x = left;
            foreach (var (k, t, w) in new[] { ("long", "▲ Long", 70f), ("short", "▼ Short", 74f), ("clear", "Xoá hết", 70f) })
            {
                Buttons.Add(new VlButton { Key = k, Text = t, Box = new RectangleF(x, top, w, 24) });
                x += w + 6;
            }
        }

        public string Hint => Mode switch
        {
            VlMode.PlaceEntry => "Bấm vào chart để đặt giá vào lệnh · chuột phải để huỷ",
            VlMode.PlaceSl => "Bấm để đặt SL · chuột phải để huỷ",
            VlMode.PlaceTp => "Bấm để đặt TP · chuột phải để huỷ",
            _ => null
        };

        public double Snap(double price) => Tick > 0 ? Math.Round(Math.Round(price / Tick) * Tick, 8) : price;

        public static VlGeo Geo(VlPos p, IVlMap m) => new VlGeo
        {
            X0 = m.X(p.T0), X1 = m.X(p.T1), YE = m.Y(p.Entry), YSl = m.Y(p.Sl), YTp = m.Y(p.Tp)
        };

        private static bool Near(PointF h, float x, float y) => (h.X - x) * (h.X - x) + (h.Y - y) * (h.Y - y) <= HitR * HitR;

        /// <summary>selected = lệnh đang chọn (mới có điểm kéo + ✕); lệnh khác chỉ bấm/rê được vào thân hộp.</summary>
        public static VlPart HitTest(VlPos p, IVlMap m, float x, float y, bool selected)
        {
            var g = Geo(p, m);
            if (selected)
            {
                if (g.Close.Contains(x, y)) return VlPart.Close;
                if (Near(g.HEntry, x, y)) return VlPart.Entry;
                if (Near(g.HSl, x, y)) return VlPart.Sl;
                if (Near(g.HTp, x, y)) return VlPart.Tp;
                if (Near(g.HRight, x, y)) return VlPart.Right;
            }
            if (x >= Math.Min(g.X0, g.X1) && x <= Math.Max(g.X0, g.X1) && y >= g.Top && y <= g.Bot) return VlPart.Body;
            return VlPart.None;
        }

        public long SelectedId = -1;
        /// <summary>Hiện nhãn khi lệnh đang chọn hoặc chuột đang rê lên nó.</summary>
        public bool ShowLabels(VlPos p) => p.Id == SelectedId || p.Id == HoverId;

        // giá đặt SL/TP phải nằm đúng phía so với giá vào (cách ít nhất 1 tick)
        private double ClampSl(int side, double entry, double v) => side > 0 ? Math.Min(v, entry - Tick) : Math.Max(v, entry + Tick);
        private double ClampTp(int side, double entry, double v) => side > 0 ? Math.Max(v, entry + Tick) : Math.Min(v, entry - Tick);

        /// <summary>Bấm chuột. Trả true = công cụ đã dùng cú bấm (không cho chart kéo/cuộn).</summary>
        public bool Down(float x, float y, bool left, IVlMap m, out bool capture)
        {
            capture = false;
            if (!left)
            {
                if (Mode == VlMode.PlaceEntry || Mode == VlMode.PlaceSl || Mode == VlMode.PlaceTp) { Cancel(); return true; }
                return false;
            }
            foreach (var b in Buttons)
            {
                if (!b.Box.Contains(x, y)) continue;
                if (b.Key == "clear") { Cancel(); SelectedId = -1; if (Items.Count > 0) { Items.Clear(); Dirty = true; } }
                else { int s = b.Key == "long" ? 1 : -1; if (Mode == VlMode.PlaceEntry && PendingSide == s) Cancel(); else { Cancel(); PendingSide = s; Mode = VlMode.PlaceEntry; } }
                return true;
            }
            switch (Mode)
            {
                case VlMode.PlaceEntry:
                {
                    double e = Snap(m.Price(y));
                    var t0 = m.Time(x);
                    Draft = new VlPos { Id = _nextId++, Side = PendingSide, Entry = e, T0 = t0, T1 = t0 + TimeSpan.FromTicks(m.Bar.Ticks * 30) };
                    Draft.Sl = Snap(ClampSl(PendingSide, e, e - PendingSide * 10 * Tick));
                    Draft.Tp = Snap(ClampTp(PendingSide, e, e + PendingSide * 20 * Tick));
                    Mode = VlMode.PlaceSl;
                    return true;
                }
                case VlMode.PlaceSl:
                    Draft.Sl = Snap(ClampSl(Draft.Side, Draft.Entry, m.Price(y)));
                    Draft.Tp = Snap(Draft.Entry + Draft.Side * 2 * Draft.SlPts);
                    Mode = VlMode.PlaceTp;
                    return true;
                case VlMode.PlaceTp:
                    Draft.Tp = Snap(ClampTp(Draft.Side, Draft.Entry, m.Price(y)));
                    Items.Add(Draft); SelectedId = Draft.Id; Draft = null; Mode = VlMode.Idle; PendingSide = 0; Dirty = true;
                    return true;
            }
            // Idle: lệnh đang chọn xét trước (điểm kéo, ✕), rồi thân hộp các lệnh khác (vẽ sau = trên cùng)
            foreach (int i in HitOrder())
            {
                var p = Items[i];
                var part = HitTest(p, m, x, y, p.Id == SelectedId);
                if (part == VlPart.None) continue;
                if (part == VlPart.Close) { Items.RemoveAt(i); Dirty = true; SelectedId = -1; HoverId = -1; HoverPart = VlPart.None; Redraw = true; return true; }
                if (SelectedId != p.Id) { SelectedId = p.Id; Redraw = true; }
                if (part == VlPart.Body) return true;      // bấm vào thân hộp = chọn lệnh (hiện nhãn + điểm kéo)
                _drag = p; _dragPart = part; _dragDur = p.T1 - p.T0; _grabDx = x - m.X(p.T0);
                Mode = VlMode.Drag; capture = true;
                return true;
            }
            // bấm ra ngoài: bỏ chọn (nhãn ẩn đi) nhưng vẫn để chart xử lý cú bấm
            if (SelectedId != -1) { SelectedId = -1; Redraw = true; }
            return false;
        }

        /// <summary>true khi chọn/bỏ chọn đổi mà Down trả false — lớp dán cần vẽ lại.</summary>
        public bool Redraw;

        private IEnumerable<int> HitOrder()
        {
            int sel = Items.FindIndex(q => q.Id == SelectedId);
            if (sel >= 0) yield return sel;
            for (int i = Items.Count - 1; i >= 0; i--) if (i != sel) yield return i;
        }

        /// <summary>Di chuột. Trả (handled, redraw).</summary>
        public (bool handled, bool redraw) Move(float x, float y, IVlMap m)
        {
            switch (Mode)
            {
                case VlMode.PlaceEntry: return (false, false);
                case VlMode.PlaceSl:
                    Draft.Sl = Snap(ClampSl(Draft.Side, Draft.Entry, m.Price(y)));
                    Draft.Tp = Snap(Draft.Entry + Draft.Side * 2 * Draft.SlPts);
                    return (true, true);
                case VlMode.PlaceTp:
                    Draft.Tp = Snap(ClampTp(Draft.Side, Draft.Entry, m.Price(y)));
                    return (true, true);
                case VlMode.Drag:
                {
                    var p = _drag;
                    double pr = m.Price(y);
                    switch (_dragPart)
                    {
                        case VlPart.Sl: p.Sl = Snap(ClampSl(p.Side, p.Entry, pr)); break;
                        case VlPart.Tp: p.Tp = Snap(ClampTp(p.Side, p.Entry, pr)); break;
                        case VlPart.Entry:
                        {
                            // giá vào nằm giữa SL và TP (cách mỗi bên ≥ 1 tick)
                            double lo = Math.Min(p.Sl, p.Tp) + Tick, hi = Math.Max(p.Sl, p.Tp) - Tick;
                            p.Entry = Snap(Math.Max(lo, Math.Min(hi, pr)));
                            p.T0 = m.Time(x - _grabDx); p.T1 = p.T0 + _dragDur;
                            break;
                        }
                        case VlPart.Right:
                        {
                            var t1 = m.Time(x);
                            var min = p.T0 + m.Bar;
                            p.T1 = t1 < min ? min : t1;
                            break;
                        }
                    }
                    Dirty = true;
                    return (true, true);
                }
            }
            // Idle: hover để tô to điểm kéo
            long hid = -1; var hp = VlPart.None;
            foreach (int i in HitOrder())
            {
                var part = HitTest(Items[i], m, x, y, Items[i].Id == SelectedId);
                if (part != VlPart.None) { hid = Items[i].Id; hp = part; break; }
            }
            bool ch = hid != HoverId || hp != HoverPart;
            HoverId = hid; HoverPart = hp;
            return (false, ch);
        }

        public bool Up()
        {
            if (Mode != VlMode.Drag) return false;
            Mode = VlMode.Idle; _drag = null; _dragPart = VlPart.None;
            return true;
        }

        public void Cancel()
        {
            if (Mode == VlMode.Drag) return;
            Mode = VlMode.Idle; PendingSide = 0; Draft = null;
        }
    }
}
