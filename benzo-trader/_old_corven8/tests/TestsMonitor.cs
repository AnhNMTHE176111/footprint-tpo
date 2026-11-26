// Chọn màn hình chụp ảnh Telegram: máy thật = ASUS (chính, 0,0) + Dell (phụ, 1920,-261).
using System.Collections.Generic;
using BenzoTraderNs;

static partial class Program
{
    static void TestPickMonitor()
    {
        System.Console.WriteLine("-- PickMonitor");
        var mons = new List<int[]> { new[] { 0, 0, 1920, 1080 }, new[] { 1920, -261, 3840, 819 } };
        Check(BenzoCore.PickMonitor(mons, 0, 0, null) == 1, "tự động, không gợi ý ⇒ Dell (màn hình không chính)");
        Check(BenzoCore.PickMonitor(mons, 0, 0, new[] { 2000, -200, 3800, 800 }) == 1, "tự động, cửa sổ nằm trên Dell ⇒ Dell");
        Check(BenzoCore.PickMonitor(mons, 0, 0, new[] { 100, 100, 1500, 900 }) == 0, "tự động, cửa sổ nằm trên ASUS ⇒ ASUS (chụp theo chart)");
        Check(BenzoCore.PickMonitor(mons, 0, 0, new[] { 1500, 0, 2500, 800 }) == 1, "cửa sổ vắt 2 màn hình (580px trên Dell > 420px trên ASUS) ⇒ Dell");
        Check(BenzoCore.PickMonitor(mons, 0, 1, null) == 0 && BenzoCore.PickMonitor(mons, 0, 2, null) == 1, "chọn tay: 1 = ASUS, 2 = Dell");
        Check(BenzoCore.PickMonitor(mons, 0, 9, null) == 1, "chọn tay quá số màn hình ⇒ kẹp về màn hình cuối");
        var one = new List<int[]> { new[] { 0, 0, 1920, 1080 } };
        Check(BenzoCore.PickMonitor(one, 0, 0, null) == 0, "chỉ 1 màn hình ⇒ màn hình đó");
        Check(BenzoCore.PickMonitor(new List<int[]>(), 0, 0, null) == -1, "không có màn hình ⇒ -1");
        var rev = new List<int[]> { new[] { -1920, 0, 0, 1080 }, new[] { 0, 0, 1920, 1080 } };
        Check(BenzoCore.PickMonitor(rev, 1, 0, null) == 0, "màn hình chính ở vị trí 2 ⇒ chọn màn hình còn lại");
    }
}
