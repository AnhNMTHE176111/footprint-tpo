# Tính năng MỚI — Sơ đồ Wyckoff tự động (Range + Phase A-E + sự kiện) trên WyckoffRunner.cs

> Toggle mới: **`ShowWyckoffSchematic`** (mặc định **BẬT**). Đây là lớp hiển thị/giáo dục THUẦN
> TUÝ — không gate, không đổi bất kỳ tín hiệu CBR/QUAY ĐẦU nào. Build: `dist/WyckoffRunner.dll`
> (biên dịch sạch, 0 warning/error, dotnet 10 trên Linux qua `build-wyckoff.sh`).

## Vẽ gì

1. **Range** (Trading Range) — 2 đường ngang biên trên/dưới, màu xanh lá (Tích luỹ) / đỏ (Phân
   phối), **CHỈ vẽ trong đúng phạm vi thời gian của range đó** (từ nến bắt đầu tới nến kết thúc/
   hiện tại nếu còn đang chạy) — **KHÔNG kéo dài hết chart**.
2. **Vạch chia Phase A/B/C/D/E** — nét đứt, màu tím nhạt, **CHỈ vẽ trong đúng phạm vi GIÁ của
   range đó** (từ Range Low tới Range High) — **KHÔNG kéo hết chiều cao chart**.
3. **Sự kiện** (chấm tròn + nhãn chữ) tại đúng nến/giá: Tích luỹ dùng `SC, AR, ST, Spring,
   Shakeout, SOS, LPS`; Phân phối dùng `BCLX, AR, ST, UT, UTAD, SOW, LPSY`.
4. Hiển thị tối đa `WyckoffMaxRanges` (mặc định 6) range gần nhất để tránh rối chart.

## Cơ chế nhận diện (tóm tắt — chi tiết xem comment trong `ScanWyckoff()`)

Chưng cất từ 3 nguồn đã có sẵn trong repo (không bịa thêm lý thuyết):
- `data-export/wyckoff/THEORY.md` — định nghĩa gốc Phase A-E + PS/SC/AR/ST/Spring/SOS/LPS
  (đối xứng PSY/BCLX/AR/ST/UT/UTAD/SOW/LPSY).
- `data-export/wyckoff/CHART_CASES.md` — **9 lỗi gán nhãn hay gặp**, chưng cất từ ~50 ca bài chữa
  học viên THẬT (7.pdf/4.pdf/2.pdf/Journal.pptx) — dùng làm **ràng buộc thiết kế trực tiếp**:
  - Spring **bắt buộc** là đáy THẤP NHẤT toàn bộ range tính tới lúc đó (lỗi phổ biến nhất trong
    2.pdf: gọi Spring cho đáy không phá đáy cũ) → code chỉ gắn nhãn Spring/Shakeout khi
    `low < mọi low trước đó trong range`.
  - SOS/SOW **bắt buộc** phá cạnh TUYỆT ĐỐI của range, không phải đỉnh/đáy cục bộ trong Phase B.
  - SC/BCLX chỉ hợp lệ nếu TRƯỚC đó là downtrend/uptrend thật (dùng field `Trend` có sẵn) — tránh
    gán SC trong tái tích luỹ.
  - LPS/LPSY vẽ thành VÙNG (không phải 1 điểm) khi ≥3 nến dao động hẹp quanh vùng test.
  - Phase D không bắt buộc phải có BU/LPS (SOS xong tăng thẳng vẫn hợp lệ).
- `data-export/wyckoff/WYCKOFF_RULES.md` — WY01-WY17, chọn các luật code hoá được trực tiếp.

## ⚠ Giới hạn (đọc trước khi dùng để học/đối chiếu)

- **Heuristic, không phải chuẩn tuyệt đối.** Các ngưỡng (`CLIMAX_RANGE_MULT=1.4`,
  `ST_TOL_TICKS=10`, `SOS_BODY_MIN=0.45`, `MAX_RANGE_HEIGHT_PCT=3.5%`...) là **tự đặt** vì tài
  liệu gốc không cho số cụ thể (xem THEORY.md §10 "mâu thuẫn/mơ hồ") — giống hệt tình huống của
  luật W3 (Phase C) đã từng bị bác bỏ khi dùng làm gate cứng. Ở đây KHÔNG dùng làm gate, chỉ vẽ.
- **"Cấu trúc thất bại" (failed structure, THEORY.md §9) chỉ xử lý một phần**: nếu giá phá NGƯỢC
  hướng giả thuyết (vd đang giả định Phân phối nhưng giá phá thẳng lên không quay đầu) → range bị
  **BỎ** (không cố gán nhãn tiếp), nhưng KHÔNG tự động dựng lại thành cấu trúc ngược chiều — đây là
  phần khó nhất của Wyckoff, để dành cho người đọc chart tự nhận định.
- Chỉ theo dõi **1 range tại một thời điểm** (không xử lý range chồng lấp).
- Đã tự kiểm bằng ảnh (xem `wyckoff-schematic-examples/`), KHÔNG kiểm bằng cách chạy lại đúng
  chart của học viên trong CHART_CASES.md (khác thị trường/khung thời gian, không có dữ liệu giá).

## Đã test thế nào

1. Viết prototype Python trước (`research/wyckoff/v8/wyckoff/wyckoff_schematic.py`), chạy trên dữ
   liệu dxFeed GCQ26 M1 THẬT (8 tháng, 11/2025→7/2026).
2. Vẽ lại bằng Pillow (`render_schematic_preview.py`) để kiểm bằng mắt — đã soát và sửa 2 vòng lỗi
   thuật toán lớn (range "vỡ" chạy vô hạn nhiều tháng, gán lại Spring/SOS lặp trên từng nến) trước
   khi port sang C#. 2 ảnh mẫu cuối cùng: [example-ACC-04-08.png](wyckoff-schematic-examples/example-ACC-04-08.png),
   [example-DIST-04-01.png](wyckoff-schematic-examples/example-DIST-04-01.png) — cả hai đúng trình
   tự chuẩn (SC→AR→ST→Spring→SOS→LPS→Phase E; BCLX→AR→ST→UT→UTAD→SOW→LPSY→Phase E).
3. Kết quả lần chạy cuối trên 8 tháng dữ liệu: **5 range** phát hiện (4 Tích luỹ + 1 Phân phối,
   1 đang chạy), thời lượng 185–2400 nến (vài giờ tới ~1.5 ngày), biên độ vài chục điểm giá — hợp
   lý so với quy mô Wyckoff TR thật (không phải chạy dài hàng tháng).
4. Port logic 1-1 sang C# (`ScanWyckoff`/`WyTryLpsAndPhaseE`/`WyEmitLps` trong `WyckoffRunner.cs`),
   build DLL qua `build-wyckoff.sh` (dotnet 10, Linux) — **biên dịch sạch, 0 lỗi/cảnh báo**.
5. **Chưa test được** trên chart Quantower thật (cần môi trường Windows + Volume Analysis sống) —
   người dùng cần tự kiểm khi attach vào chart M1 thật, đối chiếu range/phase/nhãn với hành vi giá.
