# Vẽ Lệnh — công cụ vẽ lệnh cho Optimus Flow

1. Mở lại Optimus Flow → Add indicator **"Vẽ Lệnh"** vào chart (mọi mã, mọi khung). Không có ô Settings.
2. Góc dưới-trái có 3 nút: **▲ Long · ▼ Short · Xoá hết**.
3. Bấm Long/Short rồi bấm 3 lần trên chart: **giá vào → SL → TP**. Chuột phải để huỷ khi đang đặt.
4. Nhãn: `TP 35,25 điểm`, `SL 15 điểm`, `R:R 1 : 2,35` (1 điểm = 1,0 giá; NQ 1 điểm = 4 tick).
5. 4 điểm kéo:
   - giữa-trái (giá vào): kéo cao thấp + ngang (SL, TP đứng yên, giữ bề ngang);
   - trên-trái, dưới-trái (TP / SL): chỉ kéo cao thấp;
   - giữa-phải: chỉ kéo ngang.
6. ✕ cạnh góc trên-phải hộp để xoá. Lệnh tự lưu theo mã ở `%LOCALAPPDATA%\VeLenh\<mã>.txt`.

Code: `VeLenhCore.cs` (lõi, test `dotnet run --project ve-lenh/tests`), `VeLenh.cs` (lớp dán Quantower), `bash ve-lenh/build.sh` (test → build → deploy).
