# IMPL — Big Trade "lệnh cá mập" (Opus, 2026-11-25)

Làm theo `SPEC.md` (Fable). Đây là **định nghĩa hiển thị**, không phải lợi thế giao dịch đã kiểm định. Chưa commit, chưa push, chưa chép DLL.

## Đã sửa

| File | Thay đổi |
|---|---|
| `CellBigLogic.cs` | Lớp mới `BigTradeWhale` (D = 5, R = 8, W = 1380, gộp g = max(2, rhu(biên độ TB / 8)), hàng đợi biên độ `BaselineWindow.BarsFor(m)`). `BigTradeAdaptive` chỉ còn hai overload tĩnh `Select`. Xóa `BigTradeLogic.Hit` (giữ `SizeFrac`). Sửa comment đầu file. |
| `StatThreshold.cs` | Xóa `StatBigTrade`; comment đầu file ghi Big Trade không còn thuộc chế độ thống kê. |
| `OrderFlowBubbles.cs` | `_btWhale` thay `_btAdapt` + `_statBt`, tạo ở mọi chế độ (`new BigTradeWhale(BarMinutesNow)`). Khối Big Trade của `ComputeBar` còn một nhánh (`TryThreshold` → `MergeTicks` → `Select(strict: true)`). `AddToBaseline` gọi `_btWhale.AddClosedBar(bt)`. Tooltip mới (mục 4 spec; hàng đợi chưa đầy thì "tính trên 2.3 ngày"). `BaseKey` = `DesiredBaseBars() + "\|bw:" + m` (+ `\|stat:` khi chế độ thống kê). Gỡ 4 ô + 6 property ẩn (mục 5 spec), bỏ 3 dòng `Rel(...)`. Đổi chữ "Chế độ ngưỡng chấm Bid/Ask", "Nền tự co theo khung (chấm, kiệt sức)"; viết lại comment khối Big Trade và chế độ ngưỡng. |
| Dấu vân tay | `BigTradeEnabled, "bigtrade-whale-v1:5/8/1380/<m>"` (m sau khi quy ≤ 0 → 1, `InvariantCulture`); bỏ `\|bta-v1:…`; chế độ thống kê `\|stat-v2:5/200/5/True/2/120`. Ví dụ M1 mặc định: `…\|True\|bigtrade-whale-v1:5/8/1380/1\|False\|0.35…\|dotu-v2:0\|exhtail-v1:0.8`. |
| `tests/BigTradeWhaleTests.cs` (mới) + `tests/Program.cs` | 12 ví dụ mục 8 spec. |
| `tests/AdaptiveTests.cs`, `tests/StatThresholdTests.cs`, `tests/CellBigTests.cs` | Bỏ test của phần đã xóa (trạng thái `BigTradeAdaptive`, `StatBigTrade`, `Hit`); giữ test `Select`. |
| `tests-dll/Program.cs` | 27 → 23 ô; bỏ `chk` 10 property đã xóa và thêm vào danh sách "đã bỏ"; dòng dấu vân tay / `BaseKey` theo mục 6. |
| `perf/golden-expected.txt` | Ghi lại (chỉ cột `cache` đổi, xem bước 6). |
| `dist/OrderFlowBubbles.dll` | Build lại. |
| `README.md`, `BUILD.md` | Thêm mục "Big Trade = lệnh cá mập" (nguyên văn mục 11 spec + một dòng nguồn); sửa các dòng còn nói ngưỡng 10 / "Ngưỡng tự thích nghi" / "1% 240 phút". |

## Điều kiện xong (mục 10 spec)

Dữ liệu: bản cố định trong scratchpad (`tf/fp_*.csv`, `btlog_*.csv`); sha1 bốn nhật ký trùng sha1 trong spec. Python `bw2_ref.py` chạy lại ra đúng 4 sha1 file dấu của spec (56 / 50 / 111 / 105 vòng).

**0. Chụp "trước"** (code HEAD a6cd6b1): 8 file dấu `before_*` lưu trong `scratchpad/bwimpl/`. Big Trade chế độ thống kê 3.330 / 864 / 1.913 / 788 vòng = đúng số "trước" trong spec.

**1. Unit test** `dotnet run --project tests`: `=== TAT CA PASS ===`, gồm `[Whale] TAT CA PASS` (12 ví dụ).

**2. C# = Python từng vòng** (`sa4_cmp.py … --kinds bt`), 8 lần chạy:

| Mã, khung | Python | C# mặc định | C# `ThresholdMode=1` | Lệch |
|---|---|---|---|---|
| NQ M1 | 56 | 56 | 56 | 0 / 0 |
| NQ M15 | 50 | 50 | 50 | 0 / 0 |
| GC M5 | 111 | 111 | 111 | 0 / 0 |
| GC M30 | 105 | 105 | 105 | 0 / 0 |

Hai chế độ ra cùng tập vòng (cả hai trùng Python từng dấu).

**3. Chấm và kiệt sức không đổi** (`sa4_cmp.py <trước> <sau> --kinds dotS,dotB`): 0 lệch ở cả 8 lần chạy (vd NQ M1 mặc định 42.541 đỏ + 35.120 xanh; GC M5 thống kê 8.332 + 8.260). Dòng `exhT` / `exhB` trùng từng dòng (NQ M1 11.174 / 11.306; NQ M15 1.570 / 1.653; GC M5 3.157 / 3.090; GC M30 993 / 933).

**4. Stop hunt** (dấu / bóng tím / tím là vòng Big Trade), trước → sau. Chỉ báo số, không diễn giải:

| | Mặc định | `ThresholdMode=1` |
|---|---|---|
| NQ M1 | 647 / 1.100 / 50 → 639 / 1.051 / 0 | 530 / 957 / 33 → 528 / 925 / 0 |
| NQ M15 | 40 / 116 / 11 → 39 / 105 / 0 | 43 / 138 / 31 → 41 / 107 / 0 |
| GC M5 | 140 / 327 / 40 → 139 / 289 / 2 | 103 / 236 / 23 → 103 / 215 / 2 |
| GC M30 | 21 / 68 / 3 → 21 / 66 / 1 | 19 / 76 / 8 → 19 / 69 / 1 |

Tổng vòng Big Trade trước → sau: mặc định 5.096 / 516 / 4.120 / 711 → 56 / 50 / 111 / 105; thống kê 3.330 / 864 / 1.913 / 788 → 56 / 50 / 111 / 105.

**5. `inccheck`** (có `--btlog`), hai chế độ, **toàn bộ chuỗi** (`--sub` = số nến; với `--sub 6000` mặc định NQ M1 và GC M5 không có vòng nào trong đoạn cuối nên kiểm suông, vì vậy chạy cả chuỗi): NQ M1 71.047 nến 56 vòng KHOP / KHOP; NQ M15 4.737 nến 50 vòng KHOP / KHOP; GC M5 17.623 nến 111 vòng KHOP / KHOP. (`--sub 6000` cũng KHOP cả 6.)

**6. Golden.** Chạy bản HEAD (dựng từ `git archive` trong scratchpad) và bản mới với `--dump`: cột `state` của S1–S7 **giữ nguyên từng byte**, file digest trùng, nội dung file niêm phong trùng hết khi bỏ trường `SettingsFingerprint` — dữ liệu golden (GC 90 ngày, lệnh đơn gần như 0, không nhật ký) không có vòng Big Trade ở cả hai bản. Chỉ cột `cache` đổi do dấu vân tay. Sau khi bước 2–5 đạt mới chạy `--write-expected` (kèm `--baseline` = file S1 do bản cũ ghi, để giữ dòng S3). Dòng đổi: `cache` của S1, S2, S3, S4, S5, S6, S7 (`C9119BFF…` → `48D8FE16…`, `BB601CAA…` → `A116B6D7…`, `EC26A640…` → `4937D370…`, `099E74E7…` → `833D0411…`). Chạy lại `golden`: KHOP HET.

**7. DLL:** `bash perf/build-dll.sh` → `dist/OrderFlowBubbles.dll`; `dotnet run --project tests-dll`: `=== PASS ===`, 23 ô.

**8. Bench** NQ M1 71.047 nến (`--zeromot --btlog`), nạp nguội không ghi file lần 2: 2.873 ms → 2.753 ms; có ghi niêm phong: 3.180 ms → 3.005 ms (file 68 → 66 MB, do tooltip / dấu vân tay ngắn hơn).

**9.** Không commit, không push, không chép DLL.

## Ghi chú

- Ô "Chế độ ngưỡng" vẫn có trong dấu vân tay qua `|stat-v2:` (chấm), nên đổi chế độ vẫn tính lại chấm; Big Trade ra giống hệt ở hai chế độ.
- Đổi khung (m khác) làm `BaseKey` và dấu vân tay đổi → `ResetState` dựng `_btWhale` rỗng và nạp lại từ nến đầu.
- Tooltip khi hàng đợi chưa đầy dùng `Minutes / 1380` một chữ số thập phân (`InvariantCulture`, vd "2.3").
