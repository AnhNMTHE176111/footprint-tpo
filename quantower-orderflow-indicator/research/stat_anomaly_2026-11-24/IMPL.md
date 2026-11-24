# IMPL — triển khai chế độ "Không theo CORVEN (thống kê)" (Opus, 2026-11-25)

Theo đúng `SPEC.md` (Fable). Đây là **định nghĩa hiển thị** "ô lớn bất thường", **không phải lợi thế giao dịch đã kiểm định**.

## 1. Đã làm

| File | Nội dung |
|---|---|
| `StatThreshold.cs` (mới) | `StatRank` (ngưỡng = giá trị lớn thứ K + 1 trên mảng đếm 4096 ô), `StatClock` (giờ Chicago luật cố định, ngày giao dịch bắt đầu 17:00 Chicago, khung giờ, khung lân cận), `StatDots` (chấm: ngưỡng chính theo (ngày, khung) có nhớ, dự phòng 120 phút cuốn, cửa sổ gộp w), `StatBigTrade` (Big Trade: hàng đợi n nến có lệnh đơn, mảng đếm cuốn, g) |
| `CellBigLogic.cs` | `BigTradeAdaptive.Select(..., bool strict)` mới (strict = lớn hơn hẳn); hàm cũ gọi strict = false, chế độ cũ không đổi |
| `OrderFlowBubbles.cs` | ô `ThresholdMode` (22, "Theo CORVEN" 0 / "Không theo CORVEN (thống kê)" 1, mặc định 0), ô `StatRarePbp` (23, 200/100/50, ẩn/hiện bằng `SettingItemRelationVisibility(nameof(ThresholdMode), new SelectItem("", 1))`), 6 thuộc tính ẩn; `StatMinutes/StatModeNow/StatKey`; `BaseKey` và dấu vân tay chỉ thêm phần mới khi chế độ mới bật; `InitBaselines` tạo `_statDots/_statBt` chỉ khi bật; `ComputeBar` khối chấm và khối Big Trade; `AddToBaseline` nộp đúng chỗ `_cellBigBase.Add` / `_btAdapt.AddClosedBar`; tooltip đúng mục 5 |
| `tests/StatThresholdTests.cs` (mới, nối `tests/Program.cs`) | toàn bộ ví dụ mục 8.1–8.5 + nến rỗng, hàng đợi dự phòng M1 |
| `tests-dll/Program.cs` | 27 ô; mặc định 8 thuộc tính mới; số lựa chọn 2 và 3; dấu vân tay mục 8.6 (so chuỗi với bản cũ lấy từ DLL commit 674e744); `BaseKey` |
| `tests/tests.csproj`, `perf/Golden/Golden.csproj`, `perf/build-dll.sh`, `BUILD.md` | thêm file nguồn thứ 8 |
| `README.md` | mục "Chế độ ngưỡng Không theo CORVEN (thống kê)" (mục 11 của spec + danh sách ô bị bỏ qua) |
| `sa4_cmp.py`, `sa4_parity.py` | so từng dấu và chạy cả bảng; kết quả `out_sa4_parity.csv` |

## 2. Bảng so C# = Python từng dấu (`sa4_parity.py`, C# `Golden.dll stophunt --zeromot --set ThresholdMode=1 ...`)

Mọi dòng: **0 dấu chỉ có ở Python, 0 dấu chỉ có ở C#**. Chấm đỏ / xanh:

| Cấu hình | GC M1 | GC M5 | GC M15 | GC H1 | NQ M1 | NQ M5 | NQ M15 | NQ H1 |
|---|---|---|---|---|---|---|---|---|
| Mặc định | 16.767 / 16.505 | 8.332 / 8.260 | 4.342 / 4.425 | 1.646 / 1.662 | 30.421 / 30.168 | 11.988 / 11.808 | 5.512 / 5.494 | 1.727 / 1.720 |
| 1% | 9.587 / 9.441 | 4.984 / 5.040 | 2.801 / 2.816 | 1.148 / 1.158 | 18.782 / 18.230 | 7.977 / 7.813 | 3.855 / 3.841 | 1.295 / 1.329 |
| Không lân cận | 17.553 / 17.305 | 8.902 / 8.776 | 4.681 / 4.687 | 1.771 / 1.805 | 32.243 / 31.975 | 12.907 / 12.736 | 5.949 / 5.905 | 1.904 / 1.940 |

| Dòng riêng | Chấm đỏ / xanh | Big Trade |
|---|---|---|
| Nổ ở mọi mức giá GC M5 | 15.050 / 14.965 | |
| Nổ ở mọi mức giá NQ M15 | 21.087 / 20.699 | |
| Nạp 8 ngày GC M5 | 956 / 959 | |
| Nạp 8 ngày NQ M15 | 1.097 / 1.028 | |
| 0,5% GC M5 (Python mới chạy: ngưỡng chính 17.053 / dự phòng 496 / chưa có 74 nến) | 2.958 / 2.965 | |
| 0,5% NQ M15 (Python: 4.551 / 176 / 10) | 2.636 / 2.624 | |
| Big Trade NQ M1 | 30.421 / 30.168 | 3.330 |
| Big Trade NQ M15 | 5.512 / 5.494 | 864 |
| Big Trade GC M5 | 8.332 / 8.260 | 1.913 |
| Big Trade GC M30 | 2.770 / 2.829 | 788 |

Tất cả trùng số chuẩn `SPEC.md` mục 9; sha1 file footprint / nhật ký kiểm với `out_r3_chuan.csv` trước khi so.

## 3. Các kiểm khác

- `dotnet run --project tests`: **TẤT CẢ PASS** (gồm `[Stat]` mục 8).
- `Golden.dll inccheck --set ThresholdMode=1`: KHỚP cả 7 lần — GC M5 (6.000 nến; và cả 17.623 nến có nhật ký, 1.913 vòng), NQ M1 (6.000 nến; và 45.000 nến có nhật ký, 3.330 vòng), NQ M15 (có/không nhật ký, 864 vòng), GC M30 có nhật ký (788 vòng). Lưu ý: 6.000 nến cuối của GC M5 và NQ M1 nằm ngoài khoảng ngày của nhật ký lệnh đơn nên phải tăng `--sub` mới thử được đường Big Trade.
- `Golden.dll golden`: **KHỚP HẾT** (không `--write-expected`).
- Chế độ cũ, `stophunt` không có `ThresholdMode=1`: file dấu GC M5 (đỏ 15.178 / xanh 11.158), NQ M15 (5.906 / 5.155), GC M5 + nhật ký (Big 4.120) **giống từng byte** bản trước khi sửa. `--minutes 0 --set ThresholdMode=1` cũng giống từng byte chế độ cũ.
- `perf/build-dll.sh` + `tests-dll`: PASS, 27 ô; dấu vân tay `ThresholdMode = 0` y hệt bản cũ, `ThresholdMode = 1, m = 5` kết thúc bằng `|stat-v1:5/200/5/True/2/120/240/100`.

## 4. Tốc độ (`Golden.dll bench`, mục A nạp nguội chỉ tính, lần 1 / lần 2)

| Trường hợp | Trước | Sau |
|---|---|---|
| GC 90 ngày M1 mặc định | 2.459 / 1.453 ms | 2.347 / 1.442 ms |
| NQ M1 71.047 nến, chế độ cũ | 3.072 / 2.122 ms | 3.107 / 2.131 ms |
| NQ M1, chế độ mới | — | 3.449 / 2.094 ms |
| NQ M1, chế độ mới + nhật ký lệnh đơn | — | 4.233 / 2.775 ms |

## 5. Điểm cần Fable xem

1. Big Trade: `sa3_ref.py` nộp mọi lệnh đơn > 0 vào ô `int(v)`, kể cả 0 < v < 1 (ô 0); spec mục 1.9 nói giá trị có phần nguyên 0 không nộp. C# theo Python để trùng từng dấu (lệnh đơn thực tế là số nguyên nên không ảnh hưởng).
2. `SettingItemRelationVisibility(..., new SelectItem("", 1))` biên dịch được nhưng không kiểm được ngoài Quantower (tests-dll bỏ qua phần Settings, như ô sàn cũ). Cần mở Optimus Flow xem ô "Mức hiếm" có ẩn/hiện đúng.
3. Stop hunt (bóng tím) lấy chấm làm đầu vào, nên khi bật chế độ mới số stop hunt cũng đổi (GC M5: 139 → 103 dấu). Spec không nhắc; chưa đo.
4. Python xét Big Trade cả nến không có ô footprint (nếu nhật ký có lệnh của nến đó); C# `ComputeBar` bỏ nến không có ô. Trên dữ liệu chuẩn không gặp (0 dấu lệch).
