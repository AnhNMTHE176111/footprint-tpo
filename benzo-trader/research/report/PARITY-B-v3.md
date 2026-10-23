# PARITY B (cũ / v2 / v3): C# ↔ Python — file 90d GCZ26

Ô chính: θ 0,5 · N 3 · TP 3R. C# chạy THÔ (`BENZO_NO_VOPEN=1`, không luật mở ảo 19:20-20:30) nên so được với `kernel.simulate` của Python. So từ phiên 2026-07-29 (4 phiên đầu file là "thin": Python loại, C# không biết).

## 1. Mảng vùng (từng nến, 86333 nến)

- 12 mức cố định (POC/VAH/VAL ngày, HVN ngày 1-3, POC tuần, HVN tuần 1-3, PDH, PDL): ô có giá trị 738334 · **lệch 0 ô**.
- 7 khe VCL × (cạnh dưới, cạnh trên, số nến liên tiếp): **lệch 0 ô**.

## 2. Lệnh

| cấu hình | Python | C# | khớp hoàn toàn | khớp giờ+chiều nhưng khác giá/vùng | chỉ Python | chỉ C# |
|---|---|---|---|---|---|---|
| B cũ (kỳ vọng 11) | 11 | 11 | **11** | 0 | 0 | 0 |
| B v2 (kỳ vọng 25) | 25 | 25 | **25** | 0 | 0 | 0 |
| B v3 (kỳ vọng 58) | 58 | 58 | **58** | 0 | 0 | 0 |

## 3. Bản chạy thật (C# có luật mở ảo 19:20-20:30) so với Python bỏ các lệnh trong khung đó

| cấu hình | Python (trừ khung mở ảo) | C# chạy thật | khớp hoàn toàn |
|---|---|---|---|
| B cũ | 10 | 10 | **10** |
| B v2 | 24 | 24 | **24** |
| B v3 | 57 | 57 | **57** |

**KẾT LUẬN: KHỚP HOÀN TOÀN — C# ra đúng 11 / 25 / 58 lệnh của Python, từng lệnh trùng giờ, chiều, entry, SL, TP, tên vùng.**

## Ghi chú

- Luật mở ảo 19:20-20:30 (chỉ có ở C#) bị tắt khi đối chiếu; khi chạy thật nó loại thêm các lệnh nằm trong khung đó (số lệnh live nhỏ hơn).
- Chưa port (không ảnh hưởng file 90d, một hợp đồng): luật loại phiên dính chỗ nối hợp đồng (splice); "phiên mỏng" của POC tuần dùng trung vị volume các phiên đã biết tới lúc đó (Python dùng trung vị cả file) — trên file này cho cùng kết quả.
- Footprint live từ Volume Analysis có thể lệch vài tick so với file export ⇒ HVN/VA/POC và vùng VCL loại VA có thể lệch nhẹ.
