# Review code vòng 1 — chế độ "Không theo CORVEN (thống kê)" (Fable, 2026-11-25)

Đối tượng: `StatThreshold.cs` (mới), `tests/StatThresholdTests.cs` (mới), diff của `OrderFlowBubbles.cs`, `CellBigLogic.cs`, `tests-dll/Program.cs`, các file project, `README.md`, `BUILD.md`, `IMPL.md`. Đối chiếu với `SPEC.md`.

**Kết luận: DUYỆT.** Không tìm thấy lỗi logic. Còn 2 việc nhỏ về tài liệu nên làm trước khi commit (mục 4, việc 1 và 2), không đụng code tính toán.

## 1. Tự chạy lại (không dựa vào số Opus báo)

| Kiểm | Kết quả |
|---|---|
| `dotnet run --project tests` | TẤT CẢ PASS, gồm nhóm `[Stat]` 8.1–8.5 |
| Build lại `perf/Golden` rồi `Golden.dll golden` | KHỚP HẾT, không `--write-expected` |
| Parity từng dấu, NQ M15 + nhật ký lệnh đơn: chạy **mới** `sa3_ref.py` và `Golden.dll stophunt --set ThresholdMode=1`, so bằng `sa4_cmp.py` | đỏ 5.512 / xanh 5.494 / Big Trade 864 hai bên; 0 dấu lệch |
| Parity một tổ hợp **Opus chưa chạy**: GC M5 nạp 8 ngày + mức 1% + không lân cận | đỏ 612 / xanh 638 hai bên; 0 dấu lệch (ngưỡng chính 1.489 nến, dự phòng 542, chưa có 10) |
| `Golden.dll inccheck` NQ M15 + nhật ký, `ThresholdMode=1` | nạp nguội = nạp tăng dần, 864 vòng: KHỚP |
| `tests-dll` trên `dist/OrderFlowBubbles.dll` (DLL mới hơn mọi file nguồn) | PASS, 27 ô, dấu vân tay chế độ cũ y hệt chuỗi của bản 674e744 |
| Quan hệ ẩn / hiện ô "Mức hiếm" (Opus báo không kiểm được) | Tôi gọi thẳng `SettingItemRelation.CheckRelation` của `TradingPlatform.BusinessLayer.dll`: chọn "Theo CORVEN" → ô con `Visible = False`; chọn "Không theo CORVEN" → `Visible = True`. `SelectItem.Equals` so theo `Value` (1 = 1 đúng, 1 = 0 sai). Vẫn nên nhìn lại một lần trong Optimus Flow, nhưng rủi ro thấp |

## 2. Đối chiếu spec

| Mục spec | Chỗ code | Nhận xét |
|---|---|---|
| 1.1 làm tròn | `BaselineWindow.RoundHalfUp` ở mọi chỗ | đúng, không có `Math.Round` trong file mới |
| 1.2 khung hợp lệ | `StatMinutes()` `OrderFlowBubbles.cs:566` | đúng; m = 0 và m = 2,5 ra dấu vân tay cũ (tests-dll) |
| 1.5–1.8 giờ Chicago, ngày, khung, lân cận | `StatClock` | đúng 9 dòng bảng 8.2 và 5 ca lân cận |
| 1.9–1.10 mảng đếm, hàm ngưỡng | `StatRank` | đúng; `n * pbp` tính bằng `long`; so "lớn hơn hẳn" dùng `Floor` thật |
| 2 ngưỡng chính / dự phòng | `StatDots.MainThreshold`, `TryThreshold` | đúng. Bộ nhớ ngưỡng chính theo (ngày, khung) an toàn: chỉ phụ thuộc ngày < D, và bị xóa khi nộp nến của ngày khác |
| 2 chọn chấm | `StatDots.Select` | đúng thứ tự xanh rồi đỏ, `MergeAdjacent`, không sàn, không che |
| 2 nộp nến đóng | `AddClosedBar` + `OrderFlowBubbles.cs:1535` | đúng một lần, cùng nhánh `BarStats` trả true với `_cellBigBase.Add`; nến rỗng bỏ hẳn; nến có volume mà Bid = Ask = 0 vẫn thêm phần tử rỗng |
| 3 Big Trade | `StatBigTrade`, `OrderFlowBubbles.cs:864–888`, `:1554` | đúng; không ngưỡng thì không vẽ, không quay về số 10; không giới hạn vòng |
| 5 chỉ dùng nến đã đóng | `Process()` gọi `ComputeBar` rồi mới `AddToBaseline`; nến đang chạy chỉ `ComputeBar` | đúng; `Evaluate` không ghi trạng thái nào ngoài bộ nhớ ngưỡng |
| 5 `BaseKey`, dấu vân tay | `:561`, `:579` | chỉ nối khi `StatModeNow`; đổi chế độ / khung / mức hiếm → `ResetState()` |
| 5 chế độ cũ không tốn gì | `_statDots`, `_statBt` = null | đúng; golden và file dấu chế độ cũ giống từng byte |
| 6 ô cài đặt | thứ tự 22, 23, không trùng số ô nào | đúng tên, mặc định, số lựa chọn |
| 11 README | mục mới trong `README.md` | đủ; không câu nào nói như lợi thế |

## 3. Chốt các điểm Opus hỏi

1. **Lệnh đơn 0 < v < 1 (spec 1.9 lệch `sa3_ref.py`):** giữ code như hiện nay (theo `sa3_ref.py`, là bản chuẩn từng dấu). Lệnh đơn và Bid / Ask luôn là số nguyên nên không có ca thật. Sửa câu chữ spec, không sửa code.
2. **Ẩn / hiện ô "Mức hiếm":** đã kiểm bằng logic của chính nền tảng (mục 1). Giữ.
3. **Stop hunt đổi theo chế độ:** đúng thiết kế sẵn có (`ApplyStopHunt` lấy đúng các bóng đang hiển thị). Không sửa code, nhưng **phải ghi vào README** (việc 1 dưới đây).
4. **Nến không có ô footprint nhưng nhật ký có lệnh:** không xảy ra được (nhật ký ghi từ chính ô footprint). Không sửa.
5. **`inccheck --sub` mặc định nằm ngoài khoảng nhật ký:** chấp nhận; Opus đã chạy thêm bản đủ dài.

## 4. Việc còn lại (không chặn duyệt)

1. `README.md`, mục "Chế độ ngưỡng Không theo CORVEN", dòng "Giới hạn phải biết": thêm ý (8) — *stop hunt (bóng tím) lấy các bóng đang hiển thị làm đầu vào, nên bật chế độ này thì dấu stop hunt cũng đổi (GC M5: 139 → 103 dấu); stop hunt là setup của CORVEN, số đã đo của nó chỉ đúng với chế độ "Theo CORVEN".*
2. `SPEC.md` mục 1.9: sửa "giá trị có phần nguyên bằng 0 không nộp" thành "chấm: `Floor(v) > 0` mới nộp; Big Trade: `v > 0` là nộp, vào ô `Floor(v)`" cho khớp `sa3_ref.py` và code.
3. `README.md`, giới hạn (3): thêm nửa câu — *nến đã tính khi chart mới nạp ít ngày được niêm phong với ngưỡng tạm; sau đó nạp sâu hơn thì các nến ấy vẫn giữ chấm cũ cho tới khi đổi một tham số.* (Hành vi niêm phong sẵn có; chế độ mới làm nó kéo dài từ 5 nến lên 5 ngày.)
4. `tests/StatThresholdTests.cs`: thêm 3 ca nhỏ mà hiện chỉ parity 90 ngày che — (a) cùng khung giờ, sang ngày mới thì ngưỡng chính đổi (bộ nhớ ngưỡng bị xóa); (b) khung lân cận được cộng vào (bật / tắt `neighbors` ra ngưỡng khác nhau); (c) khung có 7 ngày thì chỉ 5 ngày cuối được dùng. Vòng sau làm cũng được.
5. Người học mở Optimus Flow nhìn một lần: ô "Mức hiếm" hiện khi chọn "Không theo CORVEN", ẩn khi chọn "Theo CORVEN".

## 5. Điều chưa kiểm

- Chưa chạy trong Optimus Flow thật (chart sống, lệnh đơn từ feed). Mọi kiểm ở trên là qua khe test `Golden.dll` và file footprint.
- Tôi chạy lại 2 trong 36 dòng parity và 1 trong 7 lần `inccheck`; các dòng còn lại lấy theo `out_sa4_parity.csv` của Opus.
- Không chạy lại `bench`.
