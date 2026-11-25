# Code review 1 — Big Trade "lệnh cá mập" (Fable, 2026-11-25)

Đối tượng: diff chưa commit của Opus (`CellBigLogic.cs`, `StatThreshold.cs`, `OrderFlowBubbles.cs`, tests, tests-dll, README, BUILD, golden) so với `SPEC.md`.

**Kết luận: DUYỆT.** Không có lỗi đáng kể. Có 5 ghi chú không chặn (mục 3).

## 1. Fable tự chạy lại

| Bước | Kết quả |
|---|---|
| `dotnet run --project tests` | `=== TAT CA PASS ===`, có `[Whale] TAT CA PASS` |
| sha1 4 nhật ký trong scratchpad | trùng spec |
| `bw2_ref.py` chạy lại NQ M15, GC M5, GC M30 | 50 / 111 / 105 vòng, sha1 file dấu trùng spec |
| C# so Python (`sa4_cmp.py --kinds bt`), 3 cấu hình × 2 chế độ | 6 lần đều "TRUNG TUNG DAU", 0 lệch; hai chế độ cùng tập vòng |
| Dấu không phải Big Trade (chấm, kiệt sức), trước so sau, 6 lần | sha1 trùng cả 6 |
| `Golden.dll golden` | KHOP HET; cột `state` S1–S7 trùng bản trong git, chỉ `cache` đổi |
| `inccheck` NQ M15 toàn chuỗi (`--sub 4737`, có `--btlog`) | KHOP, 50 vòng |
| `tests-dll` | PASS, 23 ô; DLL trong `dist` mới hơn mọi file nguồn |

Chưa chạy lại: NQ M1 (parity, inccheck), bench. Số của Opus cho các phần này chưa được Fable kiểm độc lập.

## 2. Đối chiếu spec

- **Công thức** (`BigTradeWhale`): `n = max(1, rhu(5 × 1380 / m))`, `phút < 1380` → không ngưỡng, `K = max(1, rhu(8 × phút / 1380))`, số mẫu < K → không ngưỡng, quét 4095 → 1 lấy giá trị lớn thứ K. Trùng `bw2_ref.Whale` từng dòng. `m <= 0` và NaN → 1.
- **Lớn hơn hẳn:** `Select(..., strict: true)`, so bằng giá trị thật của `mot` (lệnh 5000 với ngưỡng 4095 vẫn nổ, có test).
- **Chỉ nến đã đóng, nộp 1 lần:** `TryThreshold` chỉ đọc trạng thái; `AddClosedBar` chỉ được gọi trong `AddToBaseline`, sau `ComputeBar`, trong vòng nến đóng. Nến đang chạy không nộp. Nến không có ô `mot > 0` không đổi trạng thái.
- **Gộp:** hàng đợi biên độ dùng `BaselineWindow.BarsFor(m)` cố định 120 phút, không phụ thuộc ô "Nền tự co theo khung". Đúng spec.
- **Dấu vân tay:** `bigtrade-whale-v1:5/8/1380/<m>`, bỏ `|bta-v1`, `|stat-v2:` còn 6 số. `BaseKey` thêm `|bw:<m>`. tests-dll kiểm đúng chuỗi cho m = 5, 0, 2,5.
- **Ô cài đặt:** gỡ 4 ô, xóa 6 property ẩn, bỏ 3 dòng `Rel`, đổi chữ 2 ô. Không thêm ô nào. Không còn tham chiếu tới tên cũ ngoài thư mục `research/`.
- **Phần không sửa:** `StopHuntLogic`, chấm, kiệt sức không đụng; golden `state` giữ nguyên.
- **Chữ:** comment, tooltip, README không viết như lợi thế; có câu "chưa phải lợi thế đã kiểm định".

## 3. Ghi chú không chặn

1. **Số vòng phụ thuộc độ sâu lịch sử chart nạp, và kết quả bị niêm phong.** Nếu chart nạp ít hơn 5 ngày nến có nhật ký thì ngưỡng tính trên ít ngày hơn; nếu ít hơn 1380 phút thì không có vòng. Nến đã tính được niêm phong, nên lần sau nạp sâu hơn cũng không vẽ lại (dấu vân tay không đổi). Spec không quy định; nên thêm một dòng vào README mục "Cần biết".
2. **Khung dưới 1 phút:** `ChartBarMinutes` trả 0 cho khung giây, nên Big Trade chạy như m = 1 (mỗi nến tính 1 phút), không phải "dùng nguyên giá trị" như spec mục 1. Chưa đo, người học không dùng khung giây.
3. **Tắt "Big Trade · Bật" thì nhật ký không được ghi** (lệnh `TryAppend` nằm trong `if (BigTradeEnabled)`, hành vi có từ trước). Trong phiên sống nền vẫn nộp từ feed, nhưng nạp lại sẽ thiếu các nến đó. Spec ghi "như hiện nay" nên không tính là sai.
4. **Nến đang chạy quét mảng 4096 ô mỗi lần cập nhật** khi có ô lệnh đơn. Rẻ (bench của Opus không chậm hơn), có thể nhớ ngưỡng theo nến đóng nếu sau này cần.
5. **Tooltip khi hàng đợi gần đầy** có thể in "5.0 ngày" thay vì "5". Chỉ là chữ.

## 4. Test

12 ví dụ spec có đủ trong `tests/BigTradeWhaleTests.cs`, thêm m âm / NaN. Test của phần đã xóa được gỡ, test `Select` được giữ. Ca tích hợp (nhật ký, hai chế độ, nạp nguội so với tăng dần) do Golden kiểm. Đủ.

## 5. Việc còn lại cho agent chính

Commit, push, chép DLL. Nên chạy lại parity NQ M1 một lần trước khi chép nếu muốn kiểm độc lập đủ 4 cấu hình.
