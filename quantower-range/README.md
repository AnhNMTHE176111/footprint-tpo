# Range Box — tự kẻ range như CORVEN (Optimus Flow / Quantower)

## Range là gì (theo CORVEN, buổi Meet 2026-11-07)
- Range = **một cụm nến đi ngang** (0:12:56). Cạnh range đặt ở **chỗ giá phản ứng nhiều lần**, không đặt ở râu cao/thấp nhất (0:14:50).
- Râu thò ra ngoài cạnh rồi đóng lại trong = **quét stop** (stop hunt), chuyện bình thường của range (1:04:25).
- **Phá range = nến ĐÓNG ngoài cạnh**, râu không tính (1:04:00). Đóng ngoài rồi 1–3 nến sau đóng lại trong lòng = **fail break** — chỗ CORVEN tìm lệnh ngược (0:56:49).
- Range là **bối cảnh**, không phải tín hiệu: "Cần range, chỉ là xác nhận thôi" (0:16:25).

## Đọc hình trên chart
| Hình | Nghĩa |
|---|---|
| Hộp viền xanh lơ, nền mờ | Range **đang hiệu lực**, kéo tới nến hiện tại |
| Hộp viền xám nét đứt | Range **đã phá** (kết thúc ở nến đóng ngoài đầu tiên); nét chấm kéo tiếp 30 nến ở cạnh bị phá = mốc giá hay quay lại test |
| ▼ đỏ trên nến | **Fail break đỉnh**: đóng trên cạnh trên rồi đóng lại vào trong → để ý tìm lệnh sell |
| ▲ xanh dưới nến | **Fail break đáy**: đóng dưới cạnh dưới rồi đóng lại vào trong → để ý tìm lệnh buy |
| Chấm tròn rỗng vàng | Râu quét cạnh (mặc định tắt) |

Rê chuột lên **cạnh trên/dưới** của hộp (hoặc nét chấm retest) hay lên dấu ▼/▲ để xem chữ ngắn — chuột ở giữa lòng hộp không hiện chữ, khỏi che nến, vd `Range 4369,9–4377,3 · 118 nến · Phá lên` hoặc `Fail break đáy`.
Nếu range đã phá mà trong 30 nến giá **đóng lại** trong hộp, hộp sống lại (CORVEN gọi là "confirm lần 2") — **tối đa 2 lần**; phá lần thứ 3 thì hộp kết thúc hẳn.

## 3 ô Settings
- **Hiện range đã phá** (bật): tắt đi nếu chỉ muốn thấy range đang hiệu lực.
- **Đánh dấu fail break** (bật): tam giác ▼/▲.
- **Đánh dấu râu quét cạnh** (tắt): chấm rỗng ở đầu râu quét.

Mọi con số khác là hằng trong code, lấy từ đo đạc ([research/MEASURE.md](research/MEASURE.md)) và 20 hộp CORVEN vẽ tay ([research/corven_boxes.csv](research/corven_boxes.csv)).

## Muốn range to → mở khung M15
Indicator dùng nến của chart đang mở: M1 cho range M1, **M15 cho range M15** (CORVEN 0:13:58: "range dùng khung 15").
Ngưỡng tính theo biên độ nến của chính khung đó nên cùng một code chạy đúng mọi khung: trên dữ liệu thật, lõi range trung vị ~20 nến ở cả M1, M5, M15.

## Con số đo được (GC, 90 ngày + kiểm chéo 748 ngày)
- ~19 range/ngày trên M1, cao trung vị 36–38 tick, lõi ~20 nến (hộp CORVEN: 45 tick, 20,5 nến).
- Sau fail break: ~50–52 % lần giá chạm cạnh đối diện trước khi phá thật. Nhưng vào lệnh ngay ở nến fail break (SL ngoài râu + 1 tick, TP cạnh đối diện)
  thì tỷ lệ thắng **chỉ đúng bằng mức hoà vốn** ⇒ **trừ phí còn khoảng −0,2R mỗi lệnh**.
- ⚠️ **Nói thật: chưa đo thấy lợi thế giao dịch nào từ riêng hộp range hay tam giác fail break.** Dùng nó để **đọc bối cảnh** như CORVEN
  (giá đang trong range hay đang trend, cạnh nào đáng chú ý), còn điểm vào phải có thêm xác nhận order flow — đừng vào lệnh chỉ vì thấy ▼/▲.

## Cài
Xem [BUILD.md](BUILD.md).
