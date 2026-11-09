# GĐ4 — Tester độc lập: Benzo CORVEN corven-1

> Tester độc lập (không phải người port), 2026-11-09. Kiểm theo `plans/BENZO-CORVEN-plan.md` mục 4 (a–f) và mục 10.6 (g, h, i).
> Bản được kiểm: commit `5aebd47` (port `8fa530d`, plan `ee8b252`). DLL kiểm = `benzo-trader/dist/BenzoTrader.dll` **đúng bản đã commit**
> (sha1 `b42f4d0d…`). Mọi số dưới đây do tester **tự chạy lại**, không chép từ báo cáo của người port.
> **TEST chưa bị đọc:** tester chỉ nạp phần TRAIN (bar_idx ≤ 51318). Riêng mục (g) phải chạy ReplayCorven trên toàn file để kiểm cờ
> `--hide-after`; script chỉ **đếm số ô có dữ liệu**, không in giá trị nào, rồi xoá file ngay.
> Không sửa mã sản phẩm. Công cụ của tester nằm ở `benzo-trader/tools/TesterGd4/`.

## Kết quả tổng

| Mục | Nội dung | Kết quả |
|---|---|---|
| (a) | Chạy lại Python từ đầu, số TRAIN trùng RESULTS | **PASS** |
| (b) | TEST chỉ được mở một lần, tham số không đổi sau khi mở | **PASS** (TEST chưa từng mở) |
| (c) | Phản chiếu DLL: Settings, mặc định, không còn A/B/C/D | **PASS** |
| (d) | Render UI: hộp range, mũi tên đúng nến CF, hộp SL/TP đúng giá, nhãn không tràn | **FAIL một phần** — SL/TP và range đúng; mũi tên lệch nửa nến; nhãn lệnh mới nhất bị cắt ở mép phải |
| (e) | Lint thuật ngữ (buy/sell/limit/market, không "mua/bán", không "volatility") | **PASS** |
| (f) | Caption Telegram đủ dòng dấu hiệu + dòng ⚠ (không gửi thật) | **PASS** |
| (g) | Không script nào đọc R của phần TEST | **FAIL** — `ReplayCorven --hide-after` không ẩn gì cả (chưa ai đọc TEST, nhưng ranh giới trong mã bị hỏng) |
| (h) | Test cache 10.5 ở thư mục khác | **PASS** cho 2 test của plan; tester tìm thêm **2 lỗi cache** ngoài plan |
| (i) | Ảnh bảng chart có đủ dòng 4 (nhãn trung thực) | **PASS** |
| — | `dotnet run --project benzo-trader/tests` | **115 OK / 0 FAIL** |
| — | pytest 5 file test Python | **83 passed** |
| — | `bash benzo-trader/build.sh` | **0 lỗi / 0 cảnh báo**, deploy OK |
| — | Chạy lại `parity_corven.py` | **100 %**: TRAIN 97/97 lệnh, 10094/10094 ứng viên; TEST 66/66 định danh, 7302/7302 ứng viên (file báo cáo không đổi) |

## Lỗi tìm được (theo mức nghiêm trọng)

| # | Mức | Lỗi | Bằng chứng | Gợi ý sửa |
|---|---|---|---|---|
| 1 | **CAO** | `tools/ReplayCorven/Program.cs`: cờ `--hide-after` **không có tác dụng**. Ba biến `outc`, `rr`, `exs` được tính rồi bỏ; dòng `Append` vẫn ghi `s.Outcome`, `s.R`, `ex`. ⇒ `cs_trades.csv` chứa kết cục + R + nến thoát của **toàn bộ 66 lệnh TEST**. | Chạy `--hide-after 51318` trên file 90d: phần TEST có 66 dòng, **66/66 ô `ket_cuc`, `r`, `exit_idx` có dữ liệu** (chỉ đếm, không xem). README dòng 33 và 117, docstring ReplayCorven, ghi chú trong `parity_corven.py` dòng 142 và 147 đều nói "C# ghi trống kết cục" — **sai**. | Dùng `outc / rr / exs` ở dòng `Append`; thêm test: chạy `--hide-after` rồi khẳng định cột trống. Hiện `parity_corven.py` vẫn an toàn **chỉ nhờ** thư mục tạm + `drop(columns=OUT_COLS)`. |
| 2 | TRUNG BÌNH | **Tắt rồi bật lại "Bật setup CORVEN" làm mất vĩnh viễn lịch sử lệnh** của mọi nến chạy lúc tắt. Engine vẫn `MarkRange` (niêm phong "đã dò, không có tín hiệu") khi `IsEnabled = false`, mà khoá cache (`corven-1-us0/1`) không gồm công tắc setup. | Harness: tắt setup tới nến 15000 rồi bật lại ⇒ chuẩn có **27 lệnh** trước nến 15000, sau khi bật còn **0**. Bảng thống kê và CSV lệnh mất theo. | Không `MarkRange` cho nến xử lý khi setup tắt, hoặc đưa công tắc setup vào khoá cache. |
| 3 | TRUNG BÌNH | **Nhãn dấu hiệu của lệnh mới nhất bị cắt ở mép phải.** Nhãn vẽ từ `xE + 8` sang phải, không lật. Khi chạy thật, lệnh mới luôn nằm ở nến vừa đóng sát mép phải ⇒ đúng lệnh cần đọc nhất lại không đọc được. | [corven-live-mep-phai-0730-0233.png](../../tests/ui-out/corven-live-mep-phai-0730-0233.png): nhãn "B sell · Δ to + bóng đỏ 14 + kiệt sức đỉnh + stacked 4 mức" rộng 354px, chỉ hiện "B sell · Δ", **tràn 288px**. | Nếu `xE + 8 + w > clip.Right` thì vẽ nhãn sang trái mũi tên. |
| 4 | THẤP | **Mũi tên và mép trái hộp SL/TP đặt ở mép TRÁI nến CF**, không ở tâm: `GetChartX(s.Time)` thiếu `+ BarsWidth/2`. Các indicator khác trong repo (RangeBox, OrderFlowBubbles, VsaVolume) đều cộng nửa bề rộng nến. | Đo trên ảnh: đỉnh mũi tên lệch **7px = nửa nến** (bề rộng nến 14px). Với chart footprint nến rộng 60–100px, mũi tên rơi vào ranh giới giữa CF và nến trước nên dễ đọc nhầm nến. | Cộng `CurrentChart.BarsWidth / 2` cho `xE` (giữ `xEnd`). |
| 5 | THẤP | **"Lệch giờ (UTC → VN)" làm đổi tín hiệu nhưng không nằm trong khoá cache.** `sm` (giờ neo Mỹ) tính bằng `TzOffset` ⇒ cổng chặn 19:20–20:30, 15 nến đầu phiên và cột `phien` đổi theo. Đổi Settings này thì cache cũ (tính theo lệch giờ cũ) vẫn được dùng. | 24.000 nến TRAIN: lệch giờ 7 → 8 cho **1 lệnh khác** (trên 44). Việt Nam không có giờ mùa hè nên người học hiếm khi đổi ⇒ mức thấp. | Hoặc tính `sm` theo UTC cố định (+7), hoặc đưa `TzOffset` vào khoá cache. |
| 6 | THẤP | **Giờ trong caption Telegram lệch 1 phút so với CSV.** Caption ghi giờ ĐÓNG nến CF ("CF 22:53"), còn `time_vn` trong CSV lệnh (và `t_vn` của Python) ghi giờ MỞ nến (22:52). Đối chiếu Telegram với CSV sẽ lệch 1 phút. | Lệnh `GCZ26\|202607291552\|A\|S`: caption "22:53 VN", CSV 22:52. | Ghi rõ "đóng 22:53" trong caption, hoặc thống nhất một mốc giờ. |
| 7 | GHI CHÚ | (a) Có cổng `thế đã có lệnh` ngoài danh sách cổng của plan 10.4 (README đã ghi). (b) "Δ to -36" dùng dấu trừ ASCII, còn các chỗ khác dùng "−" (chỉ là hiển thị). (c) Chỉ vẽ hộp của range còn sống, nên lệnh cũ không còn hộp range bên cạnh. Đúng chữ plan, nhưng soi lại lệnh cũ trên chart sẽ không thấy range của lệnh. (d) Python test hiện có 83 ca (plan cũ ghi 65; có thêm test `of_signals`/`kernel`). | — | Không bắt buộc. |

---

## (a) Chạy lại Python từ đầu — PASS
Script `tools/TesterGd4/a_rerun_train.py` gọi `setup_corven.run_gd1` trên TRAIN (cut 51318, 35 phiên dày) **không ghi đè báo cáo nào**
(không gọi `results_corven.main`), xuất bảng lệnh ra thư mục tạm rồi so với `report/_corven_trades.csv` từng ô.
```
n=97 A=43 B=54 per_day=2.77 WR=26.8% avg=-0.294 CI=[-0.55; -0.02] sum=-28.5 dd=28.5 streak=13
TP=26 SL=71 TIME=0
C1 avg=-0.237 (n 194) · C2 avg=-0.083 (theo cặp: -0.211)
so với _corven_trades.csv: shape (97, 23) vs (97, 23) · ô lệch = 0
```
Khớp RESULTS-CORVEN.md (bộ gốc vòng 1): 97 lệnh · 2,77/ngày · WR 26,8 % · R TB −0,29 [−0,55; −0,02] · ΣR −28,5 · max DD 28,5 · chuỗi thua 13 ·
C1 −0,24 (n 194) · C2 −0,08 (theo cặp −0,21). Nhãn trung thực "−0,29R/lệnh, kém vào ngẫu nhiên (−0,08R)" đúng với số chạy lại.

## (b) TEST chỉ mở một lần — PASS (chưa từng mở)
- `git log --grep "mở TEST"`: không có commit nào mở TEST. Commit `c89d7a7` kết luận GĐ2 ghi rõ "không mở TEST".
- `git log c89d7a7..HEAD -- setup_corven.py BenzoCorven.cs`: chỉ có 2 commit port (`8fa530d`, `5aebd47`), không đổi tham số.
  Phản chiếu DLL (mục c) xác nhận 33 hằng = bộ gốc vòng 1. Parity TRAIN 97/97 xác nhận tham số C# = Python.
- Báo cáo: `RESULTS-CORVEN.md`, `KET-LUAN-CORVEN.md`, `CORVEN-GD0.md`, `PARITY-CORVEN.md`, `README.md` **không có** R/WR/kết cục của phần TEST.
  `PARITY-CORVEN.md` chỉ in số đếm khớp định danh (66/66, 7302/7302). `_parity_corven_train.csv` đã commit có idx lớn nhất 51254 (≤ cut).

## (c) Phản chiếu DLL — PASS
`tools/TesterGd4/Gd4` nạp `dist/BenzoTrader.dll` (bản commit), đọc `InputParameterAttribute` và tạo instance để đọc giá trị mặc định:

| # | Settings | Kiểu | Mặc định |
|---|---|---|---|
| 10 | Lệch giờ (UTC → VN) | int | 7 |
| 20–23 | Telegram: bật / bot token / chat id / gửi thử (bật lên để gửi) | bool/string/string/bool | tắt / "" / "" / tắt |
| 30 | Bật setup CORVEN (chạy thử — backtest −0,29R/lệnh, kém vào ngẫu nhiên) | bool | **BẬT** |
| 31 | Chặn 19:20–20:30 VN (mốc neo Mỹ) | bool | **BẬT** |
| 32 · 33 | Hiện range · Hiện dấu hiệu đã đếm | bool | **BẬT** · **BẬT** |
| 40 · 41 | Đặt lại thống kê · Hiện lại toàn bộ thống kê | bool | tắt |
| 50 | Hiện bảng | bool | **BẬT** |

Đúng 12 mục, đúng nhãn và thứ tự của plan 10.2, không có ngưỡng số nào. Kiểu trong DLL: không còn `Detector A/B/C/D`, `SetupA5`, `BenzoLayers`, `BenzoSr`,
`VclCore`, `DemoDetector`, `BenzoRisk`. `CorvenParams` = 33 hằng đúng 10.1. Không có hằng A2 / pivot / `overlap_max_drop` / `exc_max_age`.

## (d) Render UI thật — FAIL một phần
Harness gọi **`BenzoTrader.OnPaintChart` thật trong DLL**, với `IChart` giả (DispatchProxy) và bộ đổi toạ độ giả theo quy ước Quantower:
`GetChartX` = mép trái nến. Engine chạy trên dữ liệu TRAIN thật; nến và thang giá do harness vẽ. Các ảnh trong `tests/ui-out/`:

- [corven-B-TP-0731-1434.png](../../tests/ui-out/corven-B-TP-0731-1434.png) — lệnh thế B buy, đã chạm TP. Vào 4096,8 · SL 4093,9 · TP 4102,6.
  Đo pixel: đường SL đỏ đúng y của 4093,9 ✅, đường TP xanh đúng y của 4102,6 ✅, giá vào = giá đóng nến CF ✅, nhãn "B buy · Δ ngược + kiệt sức đáy + stacked 5 mức ✓" đọc được ✅.
- [corven-A-SL-0729-1552.png](../../tests/ui-out/corven-A-SL-0729-1552.png) — lệnh thế A sell, chạm SL: SL 4072,6 / TP 4065,7 đúng giá ✅, có hộp range ACTIVE xanh lơ ✅.
- [corven-live-mep-phai-0730-0233.png](../../tests/ui-out/corven-live-mep-phai-0730-0233.png) — lệnh đang mở ở nến vừa đóng, giống lúc chạy thật:
  hộp range BROKEN viền xám đứt ✅, đường đứt đỏ tại cạnh vừa phá 4142,1 của thế B ✅, **nhãn bị cắt còn "B sell · Δ"** ❌ (lỗi #3).
- Mũi tên: tam giác đúng màu, đúng phía giá vào, ở cột nến CF ✅ — nhưng lệch nửa nến sang trái ❌ (lỗi #4).
- Chữ tiếng Việt có dấu, Δ, ✓, ✗ hiển thị đúng bằng Consolas, không ra ô vuông. OnPaintChart không ném lỗi.
- [corven-setup-tat-canh-bao.png](../../tests/ui-out/corven-setup-tat-canh-bao.png) — setup TẮT: thêm dòng "(setup CORVEN đang TẮT — không phát tín hiệu mới)"
  và dòng "⚠ Telegram: sendPhoto HTTP 401". Ẩn range và ẩn dấu hiệu đều có tác dụng. Dòng 4 vẫn hiện ✅.
- [corven-khong-phai-M1.png](../../tests/ui-out/corven-khong-phai-M1.png) — chart không phải M1: "Benzo CORVEN chỉ chạy trên chart M1" + dòng backtest ✅.

## (e) Lint thuật ngữ — PASS
`tools/TesterGd4/e_lint.py` quét mọi chuỗi hiển thị trong 5 file C# và phần chữ của README.
**0 vi phạm**: không có "mua/bán", "lệnh chờ/giới hạn", "lệnh thị trường/đập giá", "giá chào", "volatility", "aggressive/passive".
Nhãn dùng đúng `buy/sell` (`A sell · …`, `🔴 SELL`, `stacked sell`). Các từ tiếng Anh còn lại đều là chữ plan quy định hoặc thuật ngữ CORVEN đã dạy:
`stacked`, `trap`, `range`, `fail break`, `CF`, `medΔ`, `WR`, `Backtest`, `setup`, `veto`, `stop`. Từ lạ duy nhất người học có thể thấy là
`fallback`/`foreground`/`handle`, nhưng chỉ nằm trong `tele_log.txt` (log kỹ thuật).

## (f) Telegram — PASS (không gửi thật, không có token)
Caption dựng từ lệnh TRAIN thật bằng `BenzoCore.ComposeOpen` trong DLL:
```
🔴 SELL · CORVEN thế B · GCZ26 · 09:34 VN
Mốc: vùng stacked 4133,8–4134,0 trong cú phá cạnh dưới 4142,1 (range 4142,1–4147,5)
Dấu hiệu (4): Δ to -29 = 4,1× medΔ · bóng đỏ 14 @4133,0 (3,5× nền) · kiệt sức đỉnh (Ask 0) @4134,1 · stacked sell 4 mức 4136,0–4136,3
CF 09:34 thân 0,6 giá · Vào 4133,3 · SL 4135,3 (2,0) · TP 4129,3 (2R, R sẵn 3,9)
⚠ Chưa có lợi thế đo được (−0,29R/lệnh, 35 phiên)
```
Với 2 caption mẫu (thế A, thế B mốc stacked), kiểm: đủ 5 dòng; dòng dấu hiệu liệt kê đủ N dấu hiệu, có số; dòng ⚠ đúng chữ 10.3;
giá vào/SL/TP trùng giá lệnh; ≤ 1024 ký tự. Tin đóng ra dạng "🛑 CORVEN thế A −1,1R · 22:53→23:09". Không có token thì không gửi và báo
"thiếu bot token / chat id". Multipart sendPhoto có đủ 3 phần. Nút "gửi thử" (nguồn `SendTest`) có nối `TeleWarn`.

## (g) Không script nào đọc R của phần TEST — FAIL (lỗi #1)
- `git grep` trên `research/*.py` (trừ `_old/`), `tools/`, `tests/`: chỉ `parity_corven.py` chạm toàn file.
  Python toàn file bị đặt `Rf['trades'] = None` và lấy định danh bằng `py_rows(..., with_outcome=False)`. Phía C#, phần TEST bị `drop(OUT_COLS)`.
  Không in, không ghi R/WR của phần TEST. `kernel_check.py` / `test_kernel.py` có nạp toàn file nhưng là kiểm kernel cũ, không mô phỏng lệnh CORVEN.
- **Nhưng `ReplayCorven --hide-after` hỏng**: 66/66 lệnh TEST vẫn ghi đủ `ket_cuc / r / exit_idx` ra CSV. Ranh giới TEST hiện chỉ dựa vào việc
  parity_corven.py tự bỏ cột. Ai chạy tay ReplayCorven với `--hide-after` (README nói là an toàn) sẽ ghi kết cục TEST ra đĩa.

## (h) Cache theo khung, ở thư mục khác — PASS (thêm 2 lỗi ngoài plan)
- Test chính thức C13 chạy với `TEMP`/`TMP` = thư mục mới có dấu và dấu cách, cwd khác repo: 4/4 OK (lịch sử ngắn hơn không sinh tín hiệu lạ ·
  tập chung trùng khớp · sửa H ⇒ guard bắt · Reset xoá file).
- Harness của tester (thư mục `…\thư mục có dấu & cách`, 24.000 nến TRAIN): tên cache `cache_GCZ26_Time_1m.jsonl`, M1 và M5 ra 2 file khác nhau,
  2 CSV có khung + phiên bản, mã có `/ :` được làm sạch, khoá `corven-1-us1/us0` ✅. Chạy có cache = không cache, nạp lại cache = chuẩn
  (kết cục tính lại) ✅. Lịch sử bắt đầu từ nến 9000: 30/30 lệnh trùng, 0 lệnh lạ ✅. Nến lệch 1 tick so với cache ⇒ guard bắt ✅.
  Sửa tay `CfL` / `CfH` / `Entry` một dòng ⇒ guard bắt, `Reset` xoá file ✅. Đổi "Chặn 19:20–20:30" ⇒ khoá khác, bỏ cache cũ, kết quả = chạy mới ✅.
- ❌ Tắt rồi bật setup ⇒ mất 27/27 lệnh lịch sử (lỗi #2). ❌ Đổi lệch giờ ⇒ 1 lệnh khác nhưng cùng khoá cache (lỗi #5).

## (i) Ảnh bảng chart đủ dòng 4 — PASS
[corven-bang-4-dong.png](../../tests/ui-out/corven-bang-4-dong.png) (TRAIN tới nến 29000):
```
BENZO CORVEN corven-1 · 53 lệnh · WR 26 % · −16,3R
Thế A · 25 · WR 20 % · −12,5R
Thế B · 28 · WR 32 % · −3,8R
Backtest 35 phiên: −0,29R/lệnh, kém vào ngẫu nhiên (−0,08R) · chạy thử, không phải khuyến nghị
```
Đúng 4 dòng. Dòng 4 đúng chữ plan 10.3, màu cam, có trên ảnh (đo pixel). Dòng 4 cũng hiện ở mọi ảnh khác, kể cả khi setup tắt và khi chart không phải M1.

## Cách chạy lại
```bash
PYTHONIOENCODING=utf-8 python benzo-trader/tools/TesterGd4/a_rerun_train.py           # (a)
PYTHONIOENCODING=utf-8 python benzo-trader/tools/TesterGd4/e_lint.py                  # (e)
dotnet run --project benzo-trader/tools/TesterGd4/Gd4 -c Release -- all              # (c)(d)(f)(h)(i) → tests/ui-out/*.png; hiện 72 PASS / 5 FAIL (= lỗi #2–#5)
dotnet run --project benzo-trader/tests -c Release                                    # 115 OK
```

---

# PHỤ LỤC — Kiểm lại lượt sửa theo plan mục 12 (commit `437d21a`)

> Tester độc lập, 2026-11-09, theo plan 12.3. DLL kiểm = `dist/BenzoTrader.dll` của `437d21a` (git sạch). Chỉ dùng TRAIN. Riêng phép kiểm
> `--hide-after` phải chạy toàn file: script chỉ **đếm ô rỗng / không rỗng**, không in giá trị, xoá file ngay. **TEST vẫn chưa bị đọc.**

## Kết quả

| Mục | Kết quả | Bằng chứng |
|---|---|---|
| #1 `--hide-after` (g) | **PASS** | ReplayCorven toàn file `--hide-after 51318`: 66 lệnh TEST, ô không rỗng `ket_cuc/r/exit_idx` = **0/0/0**. Đối chứng: 97 lệnh TRAIN có dữ liệu **97/97/97** (không ẩn quá tay). Lớp 2: `parity_corven.py` có `assert_test_hidden`, pytest `test_parity_corven.py` xanh. |
| #2 tắt/bật setup (h) | **PASS** | Kịch bản cũ: tắt tới nến 15000 rồi bật ⇒ **27/27** lệnh có lại. Kịch bản mới của tester (một engine, công tắc đổi giữa chừng: BẬT 0–7999, TẮT 8000–14999, BẬT từ 15000): khoảng niêm phong đúng `[0..7999] [15000..23999]`; nạp lại ⇒ toàn bộ lệnh + kết cục = chạy chuẩn. Lúc đang chạy, đoạn tắt thiếu 16 lệnh, đúng nghĩa "TẮT = tạm ngừng dò"; nạp lại chart thì dò bù. |
| #3 nhãn mép phải (d) | **PASS** | Đo **pixel nền nhãn** trên ảnh không vẽ nến, không gọi `LabelX`: nền nhãn nằm ở [904; 1260], mong theo công thức plan tính tay [903; 1261]; khung phải 1400; tâm nến 1267 ⇒ nhãn lật sang trái, trọn khung, đủ 354px. Mở ảnh xem: [corven-live-mep-phai-0730-0233.png](../../tests/ui-out/corven-live-mep-phai-0730-0233.png) đọc đủ "B sell · Δ to + bóng đỏ 14 + kiệt sức đỉnh + stacked 4 mức". |
| #4 mũi tên tâm nến (d) | **PASS** | Trên ảnh **không vẽ nến** ([p12-khong-nen-A-SL.png](../../tests/ui-out/p12-khong-nen-A-SL.png), [p12-khong-nen-B-TP.png](../../tests/ui-out/p12-khong-nen-B-TP.png)), hàng giữa tam giác có tâm trùng tâm nến CF, lệch ≤ 1px, ở cả lệnh buy và sell. |
| #5 lệch giờ (h) | **PASS** | Lệch giờ 7 → 8: **0** lệnh khác trên 24.000 nến TRAIN (trước sửa: 1). |
| #6 giờ caption | **PASS** | Lệnh `GCZ26 / 2026-07-29 15:52 UTC / thế A sell`: caption "· 22:52 VN" và "CF 22:52"; `time_vn` CSV = "2026-07-29 22:52"; tin đóng "22:52→23:08" (giờ mở nến thoát). |
| 7c hộp range lệnh cũ | **PASS** | `RangeT0` là giờ một nến có thật trước CF, `RangeT1` = giờ CF. Trên ảnh không nến, đếm pixel viền mờ đúng y của `range_lo/range_hi`: A-SL cạnh trên 231/231, cạnh dưới 173/231; B-TP cạnh trên 686/686, cạnh dưới 514/686 (nét đứt). Hàng đối chứng ngay ngoài hộp: **0** pixel (A-SL 0/462, B-TP 0/1372). Mở ảnh: hộp đứt mờ 4065,55–4070,5 cạnh lệnh A-SL, 4078,1–4083,7 cạnh lệnh B-TP. |
| `dotnet run --project tests` | **139 OK / 0 FAIL** | |
| pytest (`--ignore=_old`) | **106 passed** | 83 CORVEN + 6 parity + 17 FOLLOW. Chạy `pytest` trần sẽ gom cả `research/_old/` (34 FAIL do file cũ không còn) — `_old` theo plan 10.7 là không build, không test, nên đây không phải lỗi. |
| `parity_corven.py` | **100 %** | TRAIN 97/97 lệnh, 10094/10094 ứng viên; TEST 66/66 định danh, 7302/7302 ứng viên; chong_rate TRAIN 0,018, toàn file 0,025. `PARITY-CORVEN.md` và `_parity_corven_train.csv` không đổi khi chạy lại; không có R/WR của TEST. ReplayCorven báo huỷ (nến cuối phiên) = 0. |
| `Gd4 -- all` | **90 PASS / 0 FAIL** | 77 kiểm cũ + 13 kiểm độc lập mới (mục `fix12`). |
| Lint (e) | **PASS** | 0 vi phạm. |

## Đánh giá 3 kiểm Opus đã sửa trong `tools/TesterGd4/Gd4/Program.cs`

1. **Giờ caption (#6): hợp lệ, không bị nới.** Plan 12.1 #6 đổi đặc tả sang giờ mở nến. Kiểm vẫn tự tính giờ mong đợi từ `s.Time + 7`, không gọi lại hàm caption.
   Tester thêm kiểm khoá cứng theo plan: "22:52" = `time_vn` CSV.
2. **Mũi tên (#4): bị nới — kiểm có thể qua dù mũi tên sai chỗ.** Kiểm mới tìm pixel cùng màu hướng trong ±5px quanh tâm nến, trên ảnh **có vẽ nến**.
   Thân nến CF cùng màu với mũi tên (CF sell là nến đỏ, CF buy là nến xanh), nằm đúng tâm, rộng ~10px. Hàng đo cách giá vào 12px, mà giá vào = giá đóng
   nên hàng đo rơi vào thân nến. Ví dụ lệnh A-SL: thân 0,7 giá ≈ 25px > 12px. ⇒ Kiểm này đo **thân nến**, không đo mũi tên; mũi tên lệch hay mất đều vẫn PASS.
   Sửa harness `bwD` = số nguyên (khớp `BarsWidth` nguyên của Quantower) là đúng. Tester thay bằng kiểm trên ảnh **không vẽ nến** (mục `fix12`) ⇒ PASS thật.
3. **Nhãn (#3): tự so với chính nó.** Kiểm gọi `BenzoCore.LabelX` của DLL rồi khẳng định kết quả nằm trong khung — không chứng minh `OnPaintChart` có dùng
   `LabelX`, cũng không chứng minh nhãn trên ảnh không tràn. Tester thêm kiểm pixel nền nhãn (so với công thức plan tính tay) + mở ảnh xem ⇒ PASS thật.
   Giữ cả hai kiểm của Opus (vô hại), nhưng chỉ coi kiểm của tester là bằng chứng.

## Lỗi mới
Không thấy lỗi mới. Ghi chú nhỏ:
- (a) Khi setup đang TẮT, lệnh đã niêm phong vẫn hiện; tôi kiểm phần này bằng đọc mã (`EmitTele` bỏ qua khi `!EnableCorven`), không chạy được Telegram thật.
- (b) Nhãn lật trái sẽ che vài nến bên trái lệnh mới nhất. Đây là hệ quả của đặc tả, không phải lỗi.

Ảnh mới: `tests/ui-out/p12-khong-nen-A-SL.png`, `p12-khong-nen-B-TP.png`, `p12-nhan-mep-phai-khong-nen.png`. Các ảnh `corven-*.png` được render lại bằng DLL mới.
