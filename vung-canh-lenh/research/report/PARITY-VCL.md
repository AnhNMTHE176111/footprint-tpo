# Parity Vùng Canh Lệnh: C# (VclCore) ↔ Python (vcl4.py)

File: `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (28856 nến). So từng nến có vùng hiển thị ở ít nhất một bên: **28846 nến**.
Khớp (cùng số vùng, lo/hi lệch ≤ 0.05 giá, cùng vai): **28846 / 28846 = 100.000%** (yêu cầu ≥ 99%).
Lệch lo/hi lớn nhất trong các nến khớp: 0.00e+00 giá. Mã vùng (ID) cũng được so: trùng hết ở các nến khớp.

Không có nến nào lệch.

<!-- NGUYEN-NHAN -->
## Ghi chú
- **Cách chạy:** `cd vung-canh-lenh/research && python3 parity_vcl.py`. Script tự build và chạy `tools/ReplayCsv` (C#), rồi so với `report/vcl4_records.csv.gz` (Python v4). Nếu thiếu file Python thì tự chạy lại `vcl4.run_engine`.
- **Kết quả:** khớp tuyệt đối. Lệch lo/hi lớn nhất là 0 (không phải chỉ ≤ 0,05). Mã vùng trùng từng nến. Số lần tính lại bộ cũng trùng: 1014 ở cả hai bên.
  Lý do khớp tuyệt đối: C# giữ đúng thứ tự nạp ứng viên của Python (B → B15 → C trong cùng một nến, D sau cùng), cùng cách sắp ổn định, cùng thứ tự cộng điểm và cùng phép làm tròn hàng profile (làm tròn nửa về số chẵn).
- **10 nến không có vùng ở cả hai bên** (nến 0–9):
  - nến 0–8: u chưa tính được (cần ≥ 10 nến);
  - nến 9: chỉ có ứng viên D mới sinh (< 10 nến tuổi, luật c) và không có vùng nào chứa giá.
- **Phần chưa port (không ảnh hưởng file này):**
  - Kernel Python có loại "phiên dính chỗ nối hợp đồng" (splice) khỏi VA hôm qua và POC trần. File 0816–0915 không có chỗ nối, nên C# chưa port luật này.
  - Khi chạy trên mã liên tục nối thô (vd `/GC:XCEC` qua kỳ đáo hạn), mốc C quanh chỗ nối có thể sai.
- **Khác biệt có thể có khi chạy live trên Optimus Flow (không đo được ở đây):**
  - Footprint từng mức giá lấy từ Volume Analysis của platform. Nếu bước giá hoặc dữ liệu khác file export, VA/POC hôm qua và VA Âu (loại C) có thể lệch vài tick.
  - Swing B/B15 và số tròn D chỉ dùng OHLC nên không bị ảnh hưởng.
