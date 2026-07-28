# Footprint Export (CSV) — Quantower / Optimus Flow

Xuất **footprint thật**: bid / ask / delta / trades **theo TỪNG MỨC GIÁ × TỪNG NẾN** ra CSV.

## Vì sao cần indicator này
| Cách sẵn có | Ra được gì | Thiếu gì |
|---|---|---|
| History Exporter | OHLCV, tick | không có bid/ask theo giá |
| Export của Chart (chuột phải → export) | **tổng hợp theo NẾN**: Buy(Ask) volume, Sell(Bid) volume, Delta, POC, VAH/VAL… | **mất phân bố theo từng mức giá** — tức mất chính footprint |
| **Indicator này** | 1 dòng / (nến × mức giá) | — |

Đúng cái đang thiếu trong các file `data-export/*.csv` hiện có của repo: chúng chỉ có delta **cả nến**, không biết delta nằm ở giá nào trong nến.

---

## Dùng thế nào (máy Windows chạy Quantower / Optimus Flow)

1. **Nạp DLL**: bỏ `dist/FootprintExport.dll` vào thư mục **con** riêng:
   ```
   <Quantower>\Settings\Scripts\Indicators\FootprintExport\FootprintExport.dll
   ```
   Tải nhanh từ GitHub:
   ```powershell
   [Net.ServicePointManager]::SecurityProtocol='Tls12'
   $d="$env:USERPROFILE\Documents\Quantower\Settings\Scripts\Indicators\FootprintExport"
   New-Item -ItemType Directory -Force $d | Out-Null
   iwr "https://raw.githubusercontent.com/AnhNMTHE176111/footprint-tpo/main/quantower-footprint-export/dist/FootprintExport.dll" -OutFile "$d\FootprintExport.dll"
   ```
   → **khởi động lại Quantower** (không hot-reload DLL ngoài).

2. **Mở chart đúng khoảng muốn xuất.** Xuất được **đúng phần chart đã nạp** — platform chỉ tính Volume Analysis cho phần đó. Muốn 6 tháng M1 thì phải để chart nạp 6 tháng M1 trước.

3. Chuột phải → **Indicators → Custom → Footprint Export (CSV)**.

4. **Chờ Volume Analysis nạp xong 100%** (có % ở chart). Góc trên-trái sẽ hiện
   `Footprint Export · Volume Analysis đã nạp — bật 'XUẤT NGAY' để xuất.`

5. Mở settings indicator → bật **XUẤT NGAY** → OK.
   Chạy ở **thread riêng** nên không đứng máy; trạng thái + % hiện trên chart.
   Xong sẽ báo: `XONG: 28.071 nến · 331.204 dòng · 24,6 MB · 3,1s → <đường dẫn>`
   → **tắt lại công tắc XUẤT NGAY**.

Mặc định file nằm ở `Documents\FootprintExport\`. Log mỗi lần xuất: `Documents\FootprintExport\export_log.txt`.

---

## 2 file ra

**`fp_<symbol>_<period>_<stamp>.csv`** — 1 dòng / (nến × mức giá):

| cột | nghĩa |
|---|---|
| `bar_idx` | số thứ tự nến trong lần xuất (0 = nến cũ nhất) — **khoá để ghép 2 file** |
| `datetime` | `TimeLeft` của nến, đã cộng "Lệch giờ" |
| `price` | mức giá (đã gộp theo "tick/hàng" nếu đặt > 1) |
| `bid_vol` | khớp ở **BID** = **bán chủ động** (API: `SellVolume`) |
| `ask_vol` | khớp ở **ASK** = **mua chủ động** (API: `BuyVolume`) |
| `volume` | tổng khối lượng tại mức giá đó |
| `delta` | `ask_vol − bid_vol` |
| `trades` / `buy_trades` / `sell_trades` | số lệnh |
| `max_one_trade` | **lệnh đơn lớn nhất** tại mức giá đó (bắt Big Trade) |

**`fp_..._bars.csv`** — 1 dòng / nến: `bar_idx, datetime, open, high, low, close, bar_volume, bar_ticks, bid_vol, ask_vol, volume, delta, delta_finish, max_delta, min_delta, cum_delta, trades, buy_trades, sell_trades, max_one_trade, avg_size, avg_buy_size, avg_sell_size, levels, poc_price, poc_volume, open_interest`

Ghép bằng **`bar_idx`**, KHÔNG dùng `datetime`: chart theo tick/volume/range có thể trùng `TimeLeft`.

### ⚠ Hai điều dễ tính sai
1. **`volume` ≥ `bid_vol + ask_vol`, không bằng.** Phần chênh là khối lượng feed **không gắn được phe chủ động**. Đã kiểm trên **28.071 nến M1 GCQ26 dxFeed thật** (`data-export/fp-m1-1-month-data.csv`): `bid+ask ≤ volume` đúng 28.071/28.071 nến, và **42% nến có chênh**. → Tính `delta%` thì chia cho **`volume`**, đừng chia `bid+ask`. Đừng tự dựng lại `volume = bid+ask`.
2. `max_delta` / `min_delta` là delta **chạy trong nến** (intrabar), không phải max của các mức giá. Nến rỗng, platform trả giá trị "mồi" `±1.8e308` — indicator đã dọn về `delta` của nến (nếu bạn thấy `E+308` trong file thì báo lại, đó là bug).

---

## Cài đặt (settings)

| Tham số | Mặc định | Ghi chú |
|---|---|---|
| Đường dẫn xuất | rỗng | rỗng = `Documents\FootprintExport`. Gõ **thư mục** → tên tự sinh. Gõ **`...\ten.csv`** → dùng luôn, file nến thành `ten_bars.csv` |
| Gộp mấy tick / hàng | 1 | 1 = từng tick (footprint gốc). Đặt 5 với vàng = 0,5 giá/hàng — file nhỏ đi ~5 lần |
| Chỉ xuất N nến gần nhất | 0 | 0 = tất cả |
| Từ ngày / Đến ngày | rỗng | `yyyy-MM-dd` (nhận cả `dd/MM/yyyy`). Sai định dạng → **bỏ qua + báo trên chart**, không tự đoán |
| Lệch giờ (UTC → local) | 0 | VN đặt **7** để khớp các file `data-export` cũ (`+07:00`) |
| Ký tự phân cách | `,` | `,` `;` `\|` hoặc `t` = tab |
| Xuất thêm file theo NẾN | bật | |
| Gồm cả nến ĐANG CHẠY | tắt | nên để tắt: nến chưa đóng còn thay đổi |
| Tự xuất khi nạp xong VA | tắt | bật nếu muốn xuất tự động, khỏi bấm |
| XUẤT NGAY | tắt | **bật → OK** để chạy; xong tắt lại |

**Xuất lại**: chỉ cần đổi **bất kỳ** tham số nào (kể cả đường dẫn) là chạy lại. Giữ nguyên y hệt cấu hình cũ thì indicator **không xuất trùng** (nếu không, mỗi tick sẽ ghi lại cả file).

**Cỡ file (ước lượng)**: M1 vàng ~12 mức giá/nến → 1 tháng M1 ≈ 28k nến ≈ **330k dòng ≈ 25 MB**. 6 tháng ≈ 150 MB. Trần an toàn **25 triệu dòng** — nếu chạm, indicator **báo rõ "ĐÃ CẮT"** trên chart (không cắt âm thầm).

---

## Kiểm file sau khi xuất

```bash
python3 verify_export.py /đường/dẫn/fp_MGCQ26_1m_20260728_101500.csv
```
Kiểm 8 điều: đủ cột · không lọt `E+308` · `(bar_idx, price)` không trùng · giá tăng dần trong nến · `delta == ask−bid` · `bid+ask ≤ volume` · **tổng theo mức giá == tổng của nến** · `poc_price` đúng là mức volume lớn nhất.

Mục **7a/7b/7c** là quan trọng nhất: nó đối chiếu `PriceLevels` với `Total` của platform. Nếu lệch thì **không được tự suy diễn** — báo lại để xem lại.

---

## Build lại từ source (Linux)

```bash
./build.sh          # -> dist/FootprintExport.dll  (net10.0-windows, Quantower 1.146.x)
cd tests && dotnet run     # 3.259 assertion, phải PASS hết, FAIL 0
cd tests && dotnet run -- --sample /tmp/x && python3 ../verify_export.py /tmp/x/fp_MGCQ26_1m_sample.csv
```

Cần `~/quantower-libs/` (2 DLL tham chiếu trích từ installer Quantower — cách lấy xem `../quantower-orderflow-indicator/BUILD.md`).

**Bố cục source** — tách có mục đích:
- `FootprintCore.cs` — **lõi thuần**, không tham chiếu Quantower: làm tròn giá, gộp tick/hàng, POC, dọn giá trị mồi, escape CSV, đặt tên file, lọc ngày. Vì thế **test được thật trên Linux**.
- `FootprintExport.cs` — phần indicator: lấy dữ liệu từ platform, chụp snapshot nến, ghi file ở thread riêng.
- `tests/` — 3.259 assertion chạy trên Linux, gồm test random có seed cho **bất biến tổng** khi gộp và test **số cột header phải khớp số cột dòng**.

### Đã test tới đâu (nói đúng, không thổi)
- ✅ Lõi: 3.259 assertion PASS trên Linux, gồm property-test 300 vòng random có seed.
- ✅ Sinh CSV mẫu bằng **chính code C# thật** → ghi ra đĩa → `verify_export.py` đọc lại: **8/8 mục đạt**.
- ✅ Quy ước `delta = ask − bid` và `bid+ask ≤ volume` **đối chiếu với 31k nến dữ liệu dxFeed thật** trong `data-export/`.
- ✅ Build DLL sạch, 0 warning.
- ❌ **CHƯA chạy trong Quantower thật** (Quantower là app Windows, máy dev này là Linux). Phần chưa được kiểm bằng dữ liệu sống: đọc `PriceLevels` từ feed thật, thời gian xuất với lịch sử lớn, `TickSize` của symbol lạ. Lần đầu chạy trên Windows → **chạy `verify_export.py` ngay** để xác nhận.
- ❌ Chưa kiểm bằng `pandas` (máy dev không có) — chỉ kiểm bằng `csv` chuẩn của Python. Format đã chọn để pandas đọc thẳng: không BOM, thập phân `.`, không phân cách nghìn, không ký hiệu `E`.

### Bug đã bắt được trong lúc làm (để không tái phạm)
1. **Ghi lẫn 2 file**: ban đầu dòng-mức-giá và dòng-nến dùng chung 1 buffer → dòng nến rơi vào file mức giá. Sửa: mỗi file 1 buffer riêng.
2. **`(bar_idx, price)` trùng**: khi "tick/hàng = 1" tôi bỏ qua bước gộp. Nếu feed báo giá **mịn hơn `TickSize`**, hai giá khác nhau rơi vào cùng tick index → 2 dòng cùng giá trong 1 nến → pivot phía Python sai. **Test random bắt được**. Sửa: luôn gộp qua dictionary, kể cả tick/hàng = 1.
