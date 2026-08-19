# Hiệu chỉnh lại cổng HVN trên dữ liệu DÀY (2026-08-19)

Chạy `calib_hvn_dense.py`. Nguồn: `data-export/data-footprint/fp_GC_XCEC_Time_20260720-20260819_30d.csv`
(27 phiên, ~101k hợp đồng/phiên) so với file mỏng đã dùng ở B8
(`Data_Footprint_Export.csv`, 127 phiên, **657** hợp đồng/phiên).

## 1. Dữ liệu dày làm bướu NHỌN hẳn lên

| | file MỎNG | file DÀY |
|---|---|---|
| bề rộng nền quanh bướu — trung vị | 0,5 giá | **0,3 giá** |
| bề rộng nền — phân vị 75 | **8,3 giá** | **0,7 giá** |
| bướu có nền ≤ 1 giá | 66% | **82%** |

Trên file mỏng, 1/4 số "bướu" rộng hơn 8 giá — tức không phải bướu, chỉ là mặt phẳng bị
thuật toán gọi tên. Có khối lượng thật thì hiện tượng đó gần như biến mất.

⇒ **Giữ `SharpnessGate` TẮT là đúng.** Cổng đó sinh ra để dọn rác của dữ liệu mỏng;
với nguồn dày thì không còn rác để dọn.

## 2. Nhưng dữ liệu dày cũng tìm ra NHIỀU bướu hơn → phải siết cổng

| | file MỎNG | file DÀY |
|---|---|---|
| mốc/phiên trước cổng | 2,12 | **2,93** |
| mốc/phiên sau cổng ×2,0 | 1,31 | **2,11** ⚠️ |
| tỉ lệ HVN/trung bình — trung vị | ×2,23 | ×2,36 |

Giữ nguyên ×2,0 thì số mốc vẽ lên chart tăng từ 1,31 lên 2,11 mỗi phiên — rối đúng cái
người học muốn tránh. Quét thử các ngưỡng trên dữ liệu dày:

| cổng | mốc/phiên | % phiên có ít nhất 1 mốc |
|---|---|---|
| ×2,0 | 2,11 | 100% |
| ×2,2 | 1,70 | 96% |
| ×2,4 | 1,44 | 89% |
| **×2,5** | **1,30** | **78%** |
| ×2,6 | 1,04 | 63% |
| ×3,0 | 0,56 | 44% |

**Chốt B9:** `MinHvnRatio` 2,0 → **2,5** (giữ nguyên mật độ 1,3 mốc/phiên như thiết kế B8),
`TargetMinRatio` 2,5 → **3,0** (để lớp MỤC TIÊU không trùng luôn với lớp mốc; ×3,0 cho
0,56 mục tiêu/phiên — thưa, đúng vai trò vùng chốt lời xa).

⚠️ Đây là chọn ngưỡng cho **đỡ rối mắt**, hiệu chỉnh trên **27 phiên**.
KHÔNG phải bằng chứng rằng mốc tỉ lệ cao thì ăn tiền hơn — điều đó vẫn chưa đo được.

## 3. Chỗ nối hợp đồng của `/GC:XCEC` — bẫy thật, đã đo

So bướu HVN mạnh nhất mỗi ngày giữa `/GC:XCEC` và `GCZ26` trong cùng 26 ngày:
**chỉ 18/26 ngày (69%) trùng nhau**. 8 ngày lệch đều nằm gọn trong 07-20 → 07-29 và
lệch đều đặn khoảng **+59 giá**.

Nguyên nhân: mã liên tục nối thô, không bù chênh lệch. Bước nhảy nằm đúng tại
**2026-07-29, 20:59 → 22:00: +61,2 giá** (giờ nghỉ CME). Từ 07-29 trở đi hai mã khớp
tuyệt đối. Phiên 07-29 vì thế có biên độ giả 163 giá.

**Hệ quả cho SessionZones:** profile TUẦN gộp nhiều phiên, nếu cửa sổ vắt qua chỗ nối thì
HVN tuần dựng trên hai thang giá cách nhau 59 giá ⇒ vô nghĩa. Vàng đổi hợp đồng ~2 tháng/lần.

Chưa tự động chặn trong code, vì khoảng trống cuối tuần thật đo được tới 41,8 giá — quá gần
59 giá để tách bằng ngưỡng mà không cắt nhầm. **Xử lý bằng cách lọc dữ liệu trước khi đo**
(chi tiết ở `data-export/README.md`), và khi đọc chart thì nhớ bỏ qua vùng quanh ngày đổi hợp đồng.

## 4. Việc còn treo
- Chạy lại toàn bộ `MEASURE-LEVELS-RESULTS.md` (21 rổ) trên nguồn dày — kết luận
  "không mốc nào vượt nền 40%" đang dựa trên 657 hợp đồng/phiên nên chưa đáng tin.
- Cần export dày 748 ngày (đang kẹt ở bước đẩy lên GitHub) để đủ n.
- Deploy `dist/SessionZones.dll` (bản B9) lên máy Windows.
