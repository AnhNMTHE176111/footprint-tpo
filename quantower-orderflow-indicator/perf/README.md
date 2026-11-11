# perf/ — golden test + benchmark cho OrderFlow Bubbles

Mục đích: **mọi tối ưu tốc độ phải KHÔNG đổi dữ liệu** (bóng/vùng/tam giác: giá, hình, màu, cỡ, SizeFrac, tooltip,
Confirm, kết thúc vùng; và nội dung file niêm phong). `Golden` chạy lõi tính toán THẬT của indicator
(`OrderFlowBubbles.Process()` → `ComputeBar`…) trên 87.362 nến M1 thật rồi băm kết quả.

## Cách chạy

```bash
# (cần .NET SDK + $HOME/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common}.dll — xem ../BUILD.md)
cd quantower-orderflow-indicator
dotnet build -c Release perf/Golden
dotnet perf/Golden/bin/Release/net10.0-windows/Golden.dll golden     # ~30 s; in "GOLDEN: KHOP HET" nếu hash == chuẩn
dotnet perf/Golden/bin/Release/net10.0-windows/Golden.dll bench      # đo thời gian nguội / ấm / đọc cache
```

Tuỳ chọn: `--levels <file fp_*.csv>` (mặc định `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260811-20261109_90d.csv`,
cần cả file `_bars.csv` cùng tên), `--work DIR` (mặc định `%TEMP%\ofb-golden`), `--baseline DIR` (chứa `S1.jsonl` = file
cache do BẢN CŨ ghi, để kiểm kịch bản S3 "bản mới đọc file của bản cũ"), `--dump` (ghi mọi dòng digest ra `--work` để diff khi lệch),
`--write-expected` (ghi lại `golden-expected.txt` — CHỈ khi cố ý đổi luật tính toán, kèm giải thích trong commit).

## Golden gồm gì

| Kịch bản | Nội dung |
|---|---|
| S1 | nạp NGUỘI 87.362 nến, cấu hình mặc định, file cache mới |
| S2 | nạp ẤM: khôi phục từ file S1 |
| S3 | nạp ấm từ file cache do **bản cũ** ghi (`--baseline`/S1.jsonl) — kiểm tương thích đọc + nén file |
| S4 | tăng dần: nạp 29.200 nến rồi thêm từng nến, mỗi nến gọi `Process()` 3 lần (như nhiều tick) |
| S5/S6 | bật hết DLine/Divergence/Sweep/Unfinished/StopHunt + BaselineTopLevels=0 (40.000 nến cuối), nguội và ấm |
| S7 | ngưỡng cố định + BaselineBars=50 + DLine (40.000 nến cuối) |

Mỗi kịch bản in `state=<SHA-256>` (mọi bóng, `_barTint`, vùng stacked `_zones` Idx/EndIdx/End, `_absRecs`, `_exhRecs`, `_cvd`)
và `cache=<SHA-256>` (nội dung file niêm phong sau khi nạp lại: mỗi nến bản ghi thắng cuối, serialize lại, sắp theo thời gian).
`golden-expected.txt` = hash chuẩn **lấy từ code TRƯỚC khi tối ưu** (2026-11-11, commit bd675db + khe test).
`golden-sample.txt` = 150 dòng đầu của digest S1 (đọc bằng mắt cho biết digest chứa gì; file đầy đủ ~48 MB, dùng `--dump`).

## Khe test trong `OrderFlowBubbles.cs`

`TestBarSource / TestBarCount / TestTickSize / TestCacheFile` (internal): khi `TestBarSource == null` (luôn như vậy trong
Quantower) mọi hàm trả đúng biểu thức cũ (`HistoricalData.Count`, `Symbol.TickSize`, `HistoricalData[i, Begin]`).
Harness gắn nguồn nến dựng từ CSV bằng đối tượng Quantower thật (`HistoryItemBar`/`VolumeAnalysisData`/`VolumeAnalysisItem`).
**Không giả lập được:** thread/khoá của Quantower, `OnUpdate` thật, `HistoricalData[i, Begin]` có đắt hay không, vẽ GDI+.

## Test nhỏ (không cần dữ liệu thật)

`dotnet run -c Release --project tests` — gồm `tests/PerfTests.cs`: RollingRobust mới trùng từng bit bản gốc, ghi theo lô == ghi
từng dòng, Load đường nhanh == đọc kiểu cũ (dòng hỏng/ghi dở/CRLF/BOM), nén file.
`dotnet run -c Release --project tests-dll` — kiểm DLL đã build (gồm SignalCache trong DLL).

## Build DLL

`./perf/build-dll.sh` → `dist/OrderFlowBubbles.dll` (6 file nguồn, csproj tạm). Deploy: copy vào
`C:\OptimusFLOW\Settings\Scripts\Indicators\OrderFlowBubbles\` (đóng Optimus Flow trước nếu file bị khoá).

## Kết quả đo trước/sau (2026-11-11, 20 lõi, .NET 10.0.12, 87.362 nến M1 GCZ26, lõi THẬT qua `Golden bench`)

| Kịch bản | Trước | Sau |
|---|---|---|
| Nguội, không ghi file (chỉ tính) | 6,5 – 7,5 s | 2,1 – 2,9 s |
| **Nguội, có ghi niêm phong** (đổi tham số / DLL mới) | **37,2 s** (108.636 dòng, 107 MB) | **2,4 – 2,5 s** (87.718 dòng, 78 MB) |
| Ấm: đọc cache + khôi phục | 2,07 – 2,6 s | 1,2 – 1,9 s (lần 1 gồm JIT) |
| `SignalCache.Load` riêng (file 107 MB / 108.636 dòng) | 0,93 – 0,96 s | 0,58 – 0,70 s (lần đầu gồm nén file) |
| File cache thật `_GC_XCEC_Time_1Minute` 29 MB / 67.472 dòng | 568 ms | 193 ms (sau nén 45.128 dòng) |

Golden: `S1…S7` hash == chuẩn (xem `golden-expected.txt`). Đọc thử trên bản sao các file cache thật của người dùng
(`Golden realcache`): bản cũ và bản mới ra cùng dữ liệu (hash từng file), kể cả sau khi nén.
