# Parity Vùng Canh Lệnh: C# (VclCore) ↔ Python (vcl5.py + lan_cham.py)

Yêu cầu: bộ vùng khớp ≥ 99% số nến VÀ lần chạm khớp (trạng thái từng nến + danh sách lần chạm đã chốt + đếm theo từng mã vùng).

## `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (86333 nến)

- **Bộ vùng:** khớp 86081 / 86081 nến = **100.000%** (lo/hi lệch ≤ 0.05 giá, cùng vai). Lệch lớn nhất 4.55e-13 giá. Mã vùng trùng hết.
- **Trạng thái lần chạm từng vùng × nến:** 554102 / 554102 dòng = **100.000%** (dòng chỉ có ở một bên: 0).
- **Danh sách lần chạm đã chốt** (mã vùng, nến bắt đầu, nến chốt, vai, kết cục): Python 4915, C# 4915, trùng **4915** (100.000%).
- **Theo từng mã vùng** (số lần chạm / đảo / xuyên): khớp 2377 / 2377 mã = **100.000%**.
- Thời gian 72s.

## `fp_GCZ26_XCEC_Time_20260816-20260915_29d2h` (28856 nến)

- **Bộ vùng:** khớp 28846 / 28846 nến = **100.000%** (lo/hi lệch ≤ 0.05 giá, cùng vai). Lệch lớn nhất 0.00e+00 giá. Mã vùng trùng hết.
- **Trạng thái lần chạm từng vùng × nến:** 185846 / 185846 dòng = **100.000%** (dòng chỉ có ở một bên: 0).
- **Danh sách lần chạm đã chốt** (mã vùng, nến bắt đầu, nến chốt, vai, kết cục): Python 1728, C# 1728, trùng **1728** (100.000%).
- **Theo từng mã vùng** (số lần chạm / đảo / xuyên): khớp 821 / 821 mã = **100.000%**.
- Thời gian 24s.

<!-- NGUYEN-NHAN -->
## Ghi chú
- **Cách chạy:** `cd vung-canh-lenh/research && python3 parity_vcl.py`. Script tự build + chạy `tools/ReplayCsv` (C#) trên cả hai file, rồi so với
  engine Python v5 (`report/cache_lc/*.pkl` do `lan_cham.py` tạo; thiếu thì tự chạy `vcl5.run_engine`) và máy `lan_cham.episodes(trace=True)`.
- **Kết quả:** khớp tuyệt đối cả bộ vùng lẫn lần chạm. Lệch lo/hi lớn nhất 4,6e-13 giá (sai số dấu phẩy động, không đổi vùng nào).
- **Lỗi tìm được nhờ parity (đã sửa, phía Python):** máy Python để sót bộ đếm thoát cũ sau khi chốt do hết phiên (19 dòng trạng thái lệch); kết cục
  không đổi vì bộ đếm được đặt lại khi mở lần chạm mới — `LAN-CHAM.md` chạy lại giống hệt từng số.
- **Chưa port (không ảnh hưởng 2 file này):** luật loại phiên dính chỗ nối hợp đồng (splice) của kernel; file GCZ26 không có chỗ nối.
- **Khác biệt có thể có khi chạy live:** footprint từ Volume Analysis của platform có thể lệch vài tick so với file export ⇒ mốc VA/POC (loại C) có thể lệch;
  swing và số tròn chỉ dùng OHLC nên không bị ảnh hưởng. Lịch sử riêng của vùng chỉ tính từ lúc vùng hiện trên chart (mất khi vùng rời bộ).
