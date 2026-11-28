// Test cho PlannerCore (không cần Quantower). Chạy: dotnet run --project ve-lenh/tests
using System;
using PositionPlannerNs;

sealed class LinMap : IVlMap
{
    // 10 px / nến M1 bắt đầu 2026-11-27 14:00 UTC tại x=0; giá 28200 tại y=500, 4 px / điểm (giá tăng thì y giảm)
    public static readonly DateTime T0 = new DateTime(2026, 11, 27, 14, 0, 0, DateTimeKind.Utc);
    public float X(DateTime t) => (float)((t - T0).TotalMinutes * 10);
    public float Y(double p) => (float)(500 - (p - 28200) * 4);
    public double Price(float y) => 28200 + (500 - y) / 4.0;
    public DateTime Time(float x) => T0.AddMinutes(Math.Round(x / 10.0));
    public TimeSpan Bar => TimeSpan.FromMinutes(1);
}

static class Tests
{
    static int _fail, _ok;
    static void Check(bool ok, string name, string detail = "")
    {
        Console.WriteLine((ok ? "  OK   " : "  FAIL ") + name + (!ok && detail.Length > 0 ? "  -> " + detail : ""));
        if (ok) _ok++; else _fail++;
    }

    static int Main()
    {
        var m = new LinMap();
        var ed = new VlEditor { Tick = 0.25 };
        ed.LayoutButtons(8, 8);
        bool cap;

        // 1) đặt lệnh short giống ảnh người dùng: vào 28220,75, SL 28235,75, TP 28185,5
        Check(ed.Down(90, 20, true, m, out cap), "bấm nút Short được nhận");
        Check(ed.Mode == VlMode.PlaceEntry && ed.PendingSide == -1, "chế độ đặt giá vào, phía short");
        Check(ed.Down(100, m.Y(28220.75), true, m, out cap) && ed.Mode == VlMode.PlaceSl, "bấm đặt giá vào");
        Check(ed.Draft.Entry == 28220.75 && ed.Draft.T0 == LinMap.T0.AddMinutes(10), "giá vào + T0 đúng", $"{ed.Draft.Entry} {ed.Draft.T0}");
        ed.Move(100, m.Y(28235.70), m);
        Check(ed.Draft.Sl == 28235.75, "SL bám tick khi rê", ed.Draft.Sl.ToString());
        Check(ed.Draft.Tp == 28190.75, "TP tạm = 2R khi đang đặt SL", ed.Draft.Tp.ToString());
        ed.Down(100, m.Y(28235.75), true, m, out cap);
        ed.Move(100, m.Y(28185.5), m);
        ed.Down(100, m.Y(28185.5), true, m, out cap);
        Check(ed.Mode == VlMode.Idle && ed.Items.Count == 1 && ed.Dirty, "đặt xong 1 lệnh");
        var p = ed.Items[0];
        Check(VlFmt.SlText(p) == "SL 15 điểm", "nhãn SL", VlFmt.SlText(p));
        Check(VlFmt.TpText(p) == "TP 35,25 điểm", "nhãn TP", VlFmt.TpText(p));
        Check(VlFmt.RrText(p) == "R:R 1 : 2,35", "nhãn R:R", VlFmt.RrText(p));
        Check(p.T1 - p.T0 == TimeSpan.FromMinutes(30), "bề ngang mặc định 30 nến");

        // 2) SL short không được đặt dưới giá vào
        ed.Down(90, 20, true, m, out cap); ed.Down(100, m.Y(28300), true, m, out cap);
        ed.Move(100, m.Y(28290), m);
        Check(ed.Draft.Sl == 28300.25, "SL short bị kẹp trên giá vào ≥ 1 tick", ed.Draft.Sl.ToString());
        ed.Down(100, 300, false, m, out cap);
        Check(ed.Mode == VlMode.Idle && ed.Draft == null && ed.Items.Count == 1, "chuột phải huỷ lệnh đang đặt");

        // 3) kéo điểm trên/dưới: chỉ đổi giá, không đổi thời gian
        var g = VlEditor.Geo(p, m);
        var t0 = p.T0; var t1 = p.T1;
        Check(ed.Down(g.X0, g.YSl, true, m, out cap) && cap, "bấm trúng điểm SL (dưới-trái của short là TP, trên-trái là SL)");
        ed.Move(g.X0 + 80, m.Y(28240), m); ed.Up();
        Check(p.Sl == 28240 && p.T0 == t0 && p.T1 == t1, "điểm SL chỉ kéo cao thấp", $"{p.Sl} {p.T0}");
        g = VlEditor.Geo(p, m);
        ed.Down(g.X0, g.YTp, true, m, out cap); ed.Move(g.X0 - 50, m.Y(28180), m); ed.Up();
        Check(p.Tp == 28180 && p.T0 == t0, "điểm TP chỉ kéo cao thấp");

        // 4) điểm giữa-phải: chỉ kéo ngang
        g = VlEditor.Geo(p, m);
        ed.Down(g.X1, g.YE, true, m, out cap); ed.Move(g.X1 + 100, g.YE + 60, m); ed.Up();
        Check(p.T1 == t1.AddMinutes(10) && p.Entry == 28220.75 && p.T0 == t0, "điểm phải chỉ đổi bề ngang", $"{p.T1}");
        g = VlEditor.Geo(p, m);
        ed.Down(g.X1, g.YE, true, m, out cap); ed.Move(g.X0 - 200, g.YE, m); ed.Up();
        Check(p.T1 == p.T0.AddMinutes(1), "bề ngang tối thiểu 1 nến");
        ed.Down(m.X(p.T1), g.YE, true, m, out cap); ed.Move(m.X(p.T0) + 300, g.YE, m); ed.Up();

        // 5) điểm giữa-trái: kéo cao thấp + ngang, giữ bề ngang, SL/TP đứng yên
        g = VlEditor.Geo(p, m);
        var dur = p.T1 - p.T0;
        ed.Down(g.X0, g.YE, true, m, out cap); ed.Move(g.X0 + 50, m.Y(28210), m); ed.Up();
        Check(p.Entry == 28210 && p.T0 == t0.AddMinutes(5) && p.T1 - p.T0 == dur && p.Sl == 28240 && p.Tp == 28180, "điểm giữa-trái dời giá vào + thời gian", $"{p.Entry} {p.T0}");
        g = VlEditor.Geo(p, m);
        ed.Down(g.X0, g.YE, true, m, out cap); ed.Move(g.X0, m.Y(28300), m); ed.Up();
        Check(p.Entry == 28239.75, "giá vào bị kẹp trong khoảng SL–TP", p.Entry.ToString());

        // 6) bấm chỗ trống không nuốt chuột của chart
        Check(ed.SelectedId == p.Id && ed.ShowLabels(p), "lệnh vừa đặt đang được chọn, hiện nhãn");
        ed.Redraw = false;
        Check(!ed.Down(900, 900, true, m, out cap), "bấm chỗ trống để chart xử lý");
        Check(ed.SelectedId == -1 && ed.Redraw, "bấm ra ngoài bỏ chọn, cần vẽ lại");
        ed.Move(900, 900, m);
        Check(!ed.ShowLabels(p), "bỏ chọn + chuột không rê lên lệnh: ẩn nhãn");
        g = VlEditor.Geo(p, m);
        Check(!ed.Down(g.X0, g.YSl, true, m, out cap) || ed.Mode != VlMode.Drag, "lệnh chưa chọn: điểm kéo không hoạt động (chỉ chọn)");
        ed.Up(); ed.SelectedId = -1;
        ed.Move((g.X0 + g.X1) / 2, (g.YE + g.YTp) / 2, m);
        Check(ed.ShowLabels(p), "rê chuột lên thân hộp: hiện nhãn");
        Check(ed.Down((g.X0 + g.X1) / 2, (g.YE + g.YTp) / 2, true, m, out cap) && ed.SelectedId == p.Id && ed.Mode == VlMode.Idle, "bấm thân hộp = chọn, không kéo");

        // 7) lưu / nạp
        var back = VlFmt.Load(VlFmt.Save(ed.Items));
        Check(back.Count == 1 && back[0].Entry == p.Entry && back[0].Sl == p.Sl && back[0].Tp == p.Tp && back[0].T0 == p.T0 && back[0].T1 == p.T1 && back[0].Side == -1, "lưu rồi nạp lại giống hệt");
        Check(VlFmt.Load("rác;1\n\n").Count == 0, "file hỏng không làm lỗi");

        // 8) nút xoá ✕ và Xoá hết
        g = VlEditor.Geo(p, m);
        Check(ed.Down(g.Close.X + 3, g.Close.Y + 3, true, m, out cap) && ed.Items.Count == 0, "bấm ✕ xoá lệnh");
        ed.SetItems(back);
        Check(ed.SelectedId == -1, "sau ✕ không còn lệnh chọn");
        ed.Down(ed.Buttons[2].Box.X + 2, ed.Buttons[2].Box.Y + 2, true, m, out cap);
        Check(ed.Items.Count == 0, "Xoá hết");

        // 9) long: SL dưới, TP trên
        ed.Down(10, 20, true, m, out cap); ed.Down(100, m.Y(28200), true, m, out cap);
        ed.Move(100, m.Y(28210), m);
        Check(ed.Draft.Sl == 28199.75, "SL long bị kẹp dưới giá vào");
        ed.Down(100, m.Y(28190), true, m, out cap); ed.Down(100, m.Y(28230), true, m, out cap);
        Check(ed.Items.Count == 1 && ed.Items[0].Side == 1 && VlFmt.RrText(ed.Items[0]) == "R:R 1 : 3,00", "long R:R 3");

        Console.WriteLine($"\n{_ok} OK, {_fail} FAIL");
        return _fail == 0 ? 0 : 1;
    }
}
