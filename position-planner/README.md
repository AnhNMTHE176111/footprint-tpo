# Position Planner — công cụ vẽ lệnh cho Optimus Flow

1. Mở lại Optimus Flow → Add indicator **"Position Planner"** vào chart (mọi mã, mọi khung). Không có ô Settings.
2. Góc dưới-trái có 3 nút: **▲ Long · ▼ Short · Xoá hết**.
3. Bấm Long/Short rồi bấm 3 lần trên chart: **giá vào → SL → TP**. Chuột phải để huỷ khi đang đặt.
4. Nhãn `TP 35,25 điểm`, `SL 15 điểm`, `R:R 1 : 2,35` (1 điểm = 1,0 giá; NQ 1 điểm = 4 tick) chỉ hiện khi lệnh **đang chọn** hoặc rê chuột lên hộp.
   Bấm vào hộp để chọn; bấm ra ngoài thì nhãn, điểm kéo, ✕ ẩn đi.
5. **Nét đứt + vùng tô đậm** = giá chạy theo lệnh (tô đậm từ giá vào tới giá cuối, phía TP nếu đang lãi/chạm TP, phía SL nếu đang lỗ/chạm SL): từ giá vào tới nến chạm SL/TP; chưa chạm thì tới giá đóng nến cuối trong hộp. Cùng nến chạm cả SL và TP tính SL.
6. 4 điểm kéo (khi đang chọn):
   - giữa-trái (giá vào): kéo cao thấp + ngang (SL, TP đứng yên, giữ bề ngang);
   - trên-trái, dưới-trái (TP / SL): chỉ kéo cao thấp;
   - giữa-phải: chỉ kéo ngang.
7. ✕ cạnh góc trên-phải hộp để xoá. Lệnh tự lưu theo mã ở `%LOCALAPPDATA%\PositionPlanner\<mã>.txt`.

Code: `PlannerCore.cs` (lõi, test `dotnet run --project position-planner/tests`), `PositionPlanner.cs` (lớp dán Quantower), `bash position-planner/build.sh` (test → build → deploy).
