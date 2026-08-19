# 🎬 Hướng dẫn Phát lại thị trường (Market Replay) trên Optimus Flow

> Soạn 2026-08-19 sau khi người học báo "trước làm backtest không được".
> Optimus Flow là bản đặt tên riêng của Quantower ⇒ tài liệu Quantower dùng được nguyên vẹn.

## 0. Trước hết: phân biệt 3 công cụ hoàn toàn khác nhau

| Công cụ | Tên trong phần mềm | Dùng cho | Có cần viết mã không |
|---|---|---|---|
| **Phát lại thị trường** | *Market Replay* (tên cũ *History Player*) | Tua lại lịch sử, tự đọc chart và tự bấm lệnh — **luyện mắt, luyện tay** | Không |
| **Mô phỏng giao dịch** | *Trading Simulator* | Đặt lệnh giả trên **dữ liệu đang chạy thật**, kể cả khi kết nối chỉ có dữ liệu (dxFeed) | Không |
| **Kiểm định tự động** | *Backtest & Optimize* | Chạy **mã chiến lược** tự động trên lịch sử, tối ưu tham số | **Có — bắt buộc là lớp `Strategy`** |

## 1. ⛔ Vì sao "trước làm không được" — 5 nguyên nhân thường gặp

1. **Nhầm sang panel *Backtest & Optimize*.** Panel này **chỉ nhận lớp `Strategy`**. Toàn bộ mã C# trong
   repo này (`RunnerSignal.cs`, `SessionZones.cs`, `DailyTpoBias.cs`, …) đều là lớp **`Indicator`** —
   panel sẽ **không thấy gì để chọn**. Đây là nguyên nhân số một.
2. **Chọn sai loại dữ liệu.** Trong Market Replay phải chọn **Tick**. Chọn *1 minute* thì bid/ask từng
   mức giá không có ⇒ footprint, delta, DOM đều trống ⇒ trông như phần mềm hỏng.
3. **Mở panel sai chỗ.** Chart/DOM phải mở bằng nút **"Open panel" nằm TRONG panel Market Replay**.
   Mở chart từ ngoài thì nó hiển thị dữ liệu đang chạy thật, không phải dữ liệu đang tua.
4. **Tốc độ 100%.** Nhân viên Optimus xác nhận 100% chạy nhanh hơn thực tế; nến đóng không đều.
   Dùng khoảng **40%**.
5. **Bấm Stop giữa chừng** ⇒ **mất sạch tiến trình** phiên test (tài liệu ghi rõ). Cần nghỉ thì tạm dừng.

## 2. Các bước chạy Phát lại thị trường

1. Mở menu chính (Control Center) → chọn panel **Market Replay**.
2. Thêm mã cần tập, ví dụ **GCZ26:XCEC** (dxFeed).
3. **Loại dữ liệu = Tick** · **Loại khớp lệnh = Bid/Ask/Last** (sát thực tế hơn *Last*).
4. Đặt **số dư ban đầu**, **phí** mỗi hợp đồng, **kiểu gộp lệnh** = *One Position* (mỗi chiều một lệnh —
   giống cách giao dịch thật nhất).
5. **Sơ đồ mô phỏng:** *OHLC* nhanh nhưng ít điểm kiểm soát; *Open*/*Close* nhanh nhất nhưng khớp lệnh
   giả định thô. Với order flow thì chọn Tick ở bước 3 mới là thứ quyết định.
6. Bấm **Start** → dùng **"Open panel"** mở: Chart (TPO/footprint), Time & Sales, DOM.
7. Chỉnh tốc độ ~40%, tua tới ngày muốn tập.

## 3. Nếu chỉ muốn tập trên dữ liệu đang chạy thật (không tua lịch sử)

Dùng **Trading Simulator**: Control Center → nhóm *Trading* → thêm mã → đặt số dư, độ trễ khớp lệnh
(Range/Fix/None), kiểu gộp lệnh → **Start**. Panel nào tham gia sẽ hiện nhãn **"Simulator"** trên tiêu đề.
Chạy được với **mọi kết nối, kể cả kết nối không cho giao dịch** như dxFeed. Bấm Stop = huỷ toàn bộ
lệnh và vị thế mô phỏng.

## 4. Về dữ liệu lịch sử

- dxFeed gói trả phí cho Quantower: **tick 2 năm**, nến 1 phút và 1 giờ tới **5 năm**, nến ngày toàn bộ.
- Bản **demo** mỏng hơn nhiều. Nếu Market Replay ở chế độ Tick báo thiếu dữ liệu ⇒ kiểm tra gói dxFeed.
- Diễn đàn Optimus có ca tick bị thiếu so với nguồn khác; nhân viên trả lời **Rithmic có lịch sử tick
  nhiều nhất** trong các nguồn họ cấp. Chart lỗi thì bấm **Reload History**.
- Cách khác: panel **Historical Symbols** cho **nhập CSV** (chọn dấu phân cách, định dạng ngày giờ,
  ánh xạ cột OHLC + khối lượng, chọn mức gộp Tick/Minute/Day, chọn Ask/Bid/Last, khai *tick size* và
  loại tài sản). Symbol nhập vào **dùng lại được cho Market Replay**. Hữu ích để tua lại đúng đoạn dữ
  liệu đã lưu trong `data-export/`. ⚠️ CSV M1 nhập vào **không** dựng lại được footprint từng mức giá.

## 5. Muốn kiểm định tự động trong phần mềm thì phải làm gì

Panel **Backtest & Optimize**: chọn mã chiến lược → đặt khoảng ngày (có tuỳ chọn *"start replaying from"*
để nạp dữ liệu mồi trước khi bắt đầu tính) → chọn sơ đồ mô phỏng → chạy ở chế độ *Speed control*,
*Step by step* hoặc *Background* → xem kết quả ở mục *Metrics/Logs* hoặc bấm **Visualizer** để xem lệnh
vẽ trên chart. Chế độ *Optimization* có Brute Force, Monte-Carlo, Las-Vegas, Particle Swarm.

**Điều kiện bắt buộc:** phải có một lớp **`Strategy`** — hiện repo chưa có cái nào. Muốn dùng thì viết một
lớp `Strategy` mỏng gọi lại logic của `RunnerSignal`.

> **Khuyến nghị:** chưa nên làm việc này. Kiểm định bằng Python trên CSV (`research/`) hiện mạnh hơn hẳn:
> đo được nền ngẫu nhiên, khoảng tin cậy, kiểm định hoán vị — panel Backtest & Optimize không có.
> Phần mềm chỉ nên dùng cho **phát lại để luyện mắt và luyện tay**.

## Nguồn
- [Market Replay (History Player) — OptimusFLOW](https://help.optimusflow.app/trading-panels/history-player)
- [Trading Simulator — OptimusFLOW](https://help.optimusflow.app/trading-panels/trading-simulator)
- [Backtest & Optimize — Quantower](https://help.quantower.com/quantower/quantower-algo/backtest-and-optimize)
- [Historical Symbols — Quantower](https://help.quantower.com/quantower/portfolio-panels/historical-symbols)
- [Question about Market Replay — diễn đàn Optimus (tốc độ 40%)](https://community.optimusfutures.com/t/question-about-market-replay/5036)
- [Backtesting data is very limited — diễn đàn Optimus (tick mỏng, Rithmic nhiều nhất)](https://community.optimusfutures.com/t/backtesting-data-is-very-limited/5642)
- [dxFeed mở rộng độ sâu dữ liệu lịch sử cho Quantower (tick 2 năm)](https://dxfeed.com/dxfeed-has-expanded-historical-market-data-depth-for-quantower-retail-users/)
