# Benzo Trader — setup CORVEN (corven-7) trên nến M1 đã đóng

**Setup là gì:** một setup "follow theo footprint" của CORVEN, cơ khí hoá theo `plans/BENZO-CORVEN-plan.md` — có range (Range Box)
⇒ chờ giá về mốc gần (**Fail Break** = thế A: fail break cạnh range; **Break** = thế B: phá range rồi giữ được) ⇒ cần **≥ 2 loại dấu hiệu** order flow
(Δ, bóng, kiệt sức, stacked, trap) ⇒ vào ở giá đóng nến xác nhận, SL sau cực trị cú thủng/mốc, TP 2R.
**Số backtest (35 phiên TRAIN, file 90 ngày GCZ26) — corven-7:** 229 lệnh (Fail Break 43, Break 186), **−0,07R/lệnh**, WR 33 %, nửa +0,01 / −0,16; vào ngẫu nhiên sau CF −0,12R ⇒ **chưa có lợi thế**. Bật "SL kiểu cũ": 267 lệnh, **+0,05R/lệnh**, vào ngẫu nhiên −0,03R ⇒ hơn nhưng chưa đủ chắc. (corven-6: 232 lệnh −0,07R; (corven-5: 266 lệnh +0,02R; (corven-4: 374 lệnh −0,02R; corven-3: 399 lệnh +0,02R; corven-2: 333 lệnh −0,07R; corven-1: 97 lệnh −0,29R.) Chi tiết: `research/report/VARIANTS-NGUOI-HOC-2026-11-09.md`.

Bốn setup A/B/C/D cũ đã bỏ (không setup nào có lợi thế đo được) — kết quả cũ: `research/report/TONG-KET-VONG-1-2.md`.

## Build / deploy / test
```bash
cd benzo-trader
bash build.sh                      # nối nguồn → qw-build.sh → dist/BenzoTrader.dll → copy vào C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader\
dotnet run -c Release --project tests                  # unit test: 12 ca plan mục 4 + cache 10.5 + nhãn 10.3 + hồi quy 97 lệnh TRAIN
python -m pytest -q research --ignore=research/_old     # pytest: 83 ca CORVEN (kernel 18, of_signals 26, setup_corven 18+18, sweep 3) + 6 ca parity + 17 ca C2'/FOLLOW = 106
PYTHONIOENCODING=utf-8 python research/parity_corven.py   # parity Python ↔ C# (tools/ReplayCorven) → research/report/PARITY-CORVEN.md
```
- `build.sh` **nối nguồn**, không copy tay: `quantower-range/RangeLogic.cs`, `quantower-orderflow-indicator/StackedImbalance.cs` +
  `ExhaustionLogic.cs` (đổi namespace bằng sed để không trùng kiểu với `RangeBox.dll` / `OrderFlowBubbles.dll`), và
  `quantower-tpo-suite/ProfileEngine.cs` **chỉ vì `NewsCalendar`** (lịch tin USD — sẽ tách sau). Báo lỗi nếu có cảnh báo MỚI.
- Cần `~/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common,System.Private.Windows.Core}.dll`.
- Add indicator vào **chart M1 có Volume Analysis**. Khung khác M1 ⇒ không dựng engine, chart hiện 1 dòng "Benzo CORVEN chỉ chạy trên chart M1".

## Cấu trúc file
| File | Vai trò |
|---|---|
| `BenzoCorven.cs` | `CorvenParams` (bộ tham số corven-4, đóng cứng) · `CorvenMachine` (①② range → thế A/B → mốc) · `CorvenRules` (③ dấu hiệu, ④ lệnh + ⛔) · `DetectorCorven` (chọn lệnh 4d) — port y chữ `research/setup_corven.py` |
| `BenzoOrderFlow.cs` | nền_ô, bóng, delta ngược giá, trap, định dạng số kiểu Python — port `research/of_signals.py` |
| `BenzoCore.cs` | `Signal`, mô phỏng SL/TP/TIME + MFE/MAE, thống kê thế A/B, bảng + nhãn trung thực, caption Telegram, cache niêm phong + guard, `BenzoEngine`, CSV |
| `BenzoZones.cs` | tách phiên (khoảng trống > 30′), giờ neo Mỹ (`sm`), phiên Á/Âu/Mỹ |
| `BenzoTrader.cs` | lớp dán Quantower: Settings, vòng đời, vẽ, Telegram + chụp ảnh |
| `tools/ReplayCorven` | chạy DetectorCorven trên file Footprint Export → CSV cho parity; `--hide-after <cut>` ghi trống 3 cột kết cục của mọi lệnh sau cut ngay trong tiến trình (`CorvenData.TradesCsv`, có unit test) |
| `tools/OfSignalsDump` | parity stacked/kiệt sức GĐ0 (giữ) |
| `research/` | Python chuẩn: `setup_corven.py`, `of_signals.py`, `kernel.py`, `results_corven.py`, `controls_corven.py`, `sweep_corven.py`, `parity_corven.py`; file setup cũ ở `research/_old/` (không build, không test) |

## Settings (corven-6)
Lệch giờ · Telegram: bật / bot token / chat id / gửi thử · **Hiện range** [BẬT] · **Hiện bảng thống kê** [BẬT] · **Bật Fail Break** [BẬT] · **Bật Break** [BẬT] ·
**SL tối đa (giá)** [5,0; bước 0,1; tối thiểu 0,5] · **SL kiểu cũ** [TẮT].
- Tắt Fail Break hoặc Break ⇒ ứng viên kiểu đó không được vào và **không chiếm chỗ "1 lệnh mở"** (kiểu còn lại vào được như bình thường).
- **SL tối đa (giá):** lệnh có rủi ro (entry↔SL) lớn hơn mức này bị bỏ (cổng `SL > X giá`), cho cả Fail Break và Break; thay trần 4 biên độ cũ.
- **SL kiểu cũ** (mặc định TẮT): BẬT = SL Break mốc cạnh + trần SL như corven-5 (SL theo râu nhịp hồi + dung sai cạnh + đệm max(3 tick, 0,2 biên độ); trần 4 × biên độ, **bỏ qua** "SL tối đa"). Backtest chế độ này (corven-7): 267 lệnh, +0,05R, vào ngẫu nhiên −0,03R — nhãn bảng + Telegram đổi theo chế độ.
- Đổi **SL tối đa**, **SL kiểu cũ** hoặc một công tắc ⇒ khoá cache đổi ⇒ tính lại toàn bộ. Chặn 19:20–20:30 VN **luôn BẬT**; nhãn dấu hiệu **luôn hiện**; thống kê tính lại mỗi lần nạp dữ liệu (không còn "đặt lại").
- **"Lệch giờ" chỉ đổi cách HIỂN THỊ giờ** (bảng, CSV `time_vn`, caption, lịch tin). Mọi luật giờ (chặn 19:20–20:30, 15 nến đầu phiên,
  cuối phiên, phiên Á/Âu/Mỹ) tính theo `sm` = phút kể từ 05:00 giờ VN cố định UTC+7, bù giờ mùa đông Mỹ — chỉ phụ thuộc UTC.
Không đưa `win_b / bubble_mult / need_signs / đệm SL / "gần" / lọc phiên` ra Settings: đổi tham số sống mà không đo lại = đúng lỗi A/B/C/D,
và mỗi bộ tham số là một chuỗi forward test riêng (n live ≈ 3 lệnh/ngày — chia nhỏ là vô nghĩa).

## Setup corven-4 (tóm tắt — chi tiết và lý do từng con số ở plan mục 1, 6–10)
- **① Bối cảnh:** Range Box nguyên trạng. Thế A = FailBreak về ACTIVE (CF là nến FailBreak hoặc 1–2 nến sau, đóng trong range, cách cạnh ≤ 1 mbr).
  Thế B = BreakConfirmed (gồm cả range hết lượt ReEntry, cờ `b_from_exhausted`), chưa ReEntry, ≤ 30 nến, cấu trúc 1 nến chưa gãy ngược.
- **② Mốc gần:** cạnh vừa phá (râu chạm cạnh ± tol trong cửa sổ 3 nến, CF đóng cách cạnh ≤ 1 mbr) hoặc vùng stacked mới cùng hướng
  (Body, không Weak, chưa từng bị chạm, chưa bị đóng xuyên).
- **③ ≥ 2 loại dấu hiệu** trong cửa sổ test: Δ to (≥ 2× medΔ) hoặc Δ ngược giá · bóng đúng phe (≥ 3× nền_ô và ≥ 10 hợp đồng) ·
  kiệt sức phe ngược chưa bị quét · stacked mới đóng phía hướng vào · trap (quét mốc + bóng ngược màu trong râu). Vùng đang làm mốc không đếm.
- **④ Lệnh:** CF thân ≥ 0,4 biên độ, đóng sát cực trị (≤ 0,3), biên độ ≥ 0,5 mbr, Δ cùng dấu ≥ 0,5 medΔ. SL sau cực trị cú thủng (A) /
  mốc (B) + đệm max(3 tick, 0,2 mbr), sàn 1 mbr, trần SL theo giá (mặc định 5,0). R sẵn tới mục tiêu ≥ 1,7, TP luôn 2R. 1 lệnh mở; 1 lệnh/thế;
  1 lệnh/(range, cạnh, thế); không vào 15 nến đầu phiên, khi có tin USD ±15′, và 19:20–20:30 VN (luôn bật).
- **⛔:** kiệt sức chống hướng chưa bị quét (5 nến) · range chồng range (thế A, chỉ từ FailBreak thứ 2). (corven-3 đã bỏ "nhịp đẩy do quét stop".)
- **corven-3 (người học chốt 2026-11-09):** thế B không cần nhịp hồi chạm cạnh (đủ ≥ 1 nến hồi, mọi nến đóng ngoài range, CF đóng vượt nến hồi) · thế B bỏ luật R sẵn ≥ 1,7 (TP 2R) · thêm dấu hiệu "trap trong nhịp hồi" (ô ngược phe ≥ 3× nền và ≥ 10 ở nến hồi, CF đóng vượt ô đó).
- **corven-3:** SL thế B mốc cạnh = ngay sau cạnh vừa phá: min(đáy cửa sổ, cạnh) − đệm (buy), bỏ phần trừ dung sai cạnh.
- **corven-7 (người học yêu cầu, Opus chọn số 2026-11-09):** range đã bị phá thật mà giá chạy xa cạnh vừa phá ≥ 2 × chiều cao range (đo High/Low từ nến phá) ⇒ range Dead ngay, không ReEntry, không Merge hồi sinh, hộp "Hiện range" không kéo dài (`RangeParams.DeadRunMult = 2`; Range Box gốc mặc định tắt).
- **corven-6 (người học yêu cầu 2026-11-09):** SL Break mốc cạnh = cạnh vừa phá ∓ 3 tick cố định (bỏ râu nhịp hồi và đệm biên độ; sàn 1 biên độ giữ; Fail Break giữ SL cũ) · trần SL theo GIÁ (Settings) thay trần 4 biên độ · Settings rút còn 5 mục + Telegram/lệch giờ.
- **corven-5 (Opus quyết 2026-11-09):** Break bỏ nhánh "vùng stacked làm mốc" (chỉ còn mốc cạnh vừa phá; stacked vẫn là dấu hiệu) · nhiều Break cùng nến xác nhận ⇒ gán range có nến đóng ngoài muộn nhất trước.
- **Tên hiển thị (2026-11-09):** thế A → "Fail Break", thế B → "Break" (bảng chart, nhãn mũi tên, Telegram, caption) — định nghĩa một chỗ `BenzoCore.TheName`. Mã nội bộ 'A'/'B' giữ nguyên trong cache/CSV/khoá (không đổi định dạng ⇒ cache cũ vẫn nạp; nhãn cũ "A buy · …" trong cache được đổi tiền tố lúc vẽ).
- **corven-4 (Opus quyết 2026-11-09):** nhịp hồi không chạm cạnh phải thuộc cú phá — nến hồi đầu tiên cách nến phá (CloseOutside) ≤ 5 nến, nếu không thì không tính là mốc cạnh.
- Lệnh còn mở qua khoảng trống > 30′ đóng `TIME` tại giá đóng nến cuối phiên.

## Quyết định khi port (plan 10)
- Bộ tham số = **bộ gốc vòng 1** (RESULTS-CORVEN.md), `LogicVersion = "corven-4"`. **Không port:** ngoại lệ "xác nhận lần 2" (A2),
  neo SL pivot, `overlap_max_drop`, lọc phiên mỏng/chỗ nối của Python.
- **Nến cuối phiên:** Python biết trước nến cuối nên không vào. C# chặn bằng cổng `cuối phiên` khi `sm ≥ 1379` (nến mở 16:59 ET = nến M1
  cuối của phiên 18:00→17:00 ET — cách nhân quả duy nhất, plan 12.2-Q2), và **giữ** cơ chế huỷ ở `BenzoEngine` làm lưới dự phòng cho ngày
  đóng sớm / thiếu nến (vào rồi huỷ khi nến đầu phiên sau tới, Telegram gửi tin huỷ, khoá 4d được trả lại). Số lệnh bị huỷ của ReplayCorven
  trên TRAIN: **0 trước khi thêm cổng, 0 sau khi thêm cổng** (toàn file 90d cũng 0). Kết quả lệnh giống Python 100 %.
- **Luật chồng range:** C# **luôn bật**. Python có thêm luật báo cáo `overlap_max_drop` (tự tắt luật khi nó loại > 30 % thế A — không port);
  `parity_corven.py` in `chong_rate` (TRAIN 0,018) và **dừng** nếu > 0,30 để không bao giờ "tự khớp" âm thầm khi hai bên tách nhau.
- **Range chồng range / mục tiêu thế B:** Python đọc cạnh range cũ ở cuối file; C# đọc tại lúc xét (không nhìn trước). Không gây lệch trên file 90d.
- **Tin USD** ±15′: lệch có chủ đích duy nhất (Python không có lịch tin). Lịch tin chỉ phủ tuần hiện tại.
- **Chọn lệnh khi bận (G7):** đang có lệnh mở thì mọi CF khác bị bỏ (không xếp hàng); cùng một nến xét thế A trước thế B, rồi theo range.
- Range M15 ("rối thì lên M15") **không làm ở v1** — để v2 sau khi v1 có số. ⛔ "đấu giá vừa xong (profile nhọn)" **bỏ** (chưa đo được).
- Δ "thẳng" (`max_delta`) không dùng ở cả Python lẫn C# (export lịch sử ghi `max_delta = delta`).

## Cách đề xuất sửa tín hiệu (vòng "review → update")
1. Xem `candidates_<mã>_1m_corven-7.csv` (ứng viên bị loại + cổng chặn) và `signals_…csv` (cột `mfe_r/mae_r`) để tìm chỗ "thấy đẹp mà máy không vào" hoặc ngược lại.
2. Viết đề xuất thành **luật có số** (không phải "nhìn thấy"), sửa `research/setup_corven.py` trước.
3. Đo lại trên TRAIN cùng 2 đối chứng C1/C2 (`results_corven.py`, `controls_corven.py`) — đề xuất phải hơn đối chứng, không chỉ hơn số cũ.
4. Đạt mới sửa C#, tăng `LogicVersion` (`corven-4`…) ⇒ cache cũ tự bỏ; chạy unit test + `parity_corven.py` phải 100 %.
5. Không bao giờ đổi tham số bằng nút bấm trên chart.

## Vòng đời, cache, chống tính lại
- Chỉ xử lý nến **đã đóng** (`Count−2`), mỗi nến dò **một lần**; `ClosedBars` chặn nhìn nến sau `closedIdx`.
- **Niêm phong** `%LOCALAPPDATA%\BenzoTrader\cache_<mã>_<aggName>_<phút>m.jsonl` (tên có khung — sửa bug cũ dùng `Aggregation.Title`).
  Khoá phiên bản = `corven-7-sl<SL tối đa>-f<0|1>-b<0|1>-old<0|1>` (SL tối đa + công tắc Fail Break + công tắc Break + SL kiểu cũ); "Hiện range"/"Hiện bảng" chỉ vẽ nên không vào khoá.
  **Guard khớp nến:** mỗi dòng `sig` lưu H/L nến CF; khi gắn lại, giá vào lệch > nửa tick hoặc H/L lệch > 1 tick ⇒ **bỏ toàn bộ cache**,
  dò lại từ đầu, ghi 1 dòng `error_log.txt`. File cache cũ `cache_<mã>_<Title>.jsonl` của A/B/C/D tự xoá khi gặp.
- 1 lệnh mở cùng lúc; chạm cả SL lẫn TP cùng nến ⇒ SL; chi phí 0,2 giá/lệnh.
- Cache giữ **nhiều khoảng** đã dò (dòng `rng` rời nhau): đoạn nến lúc setup TẮT để trống, nạp lại sẽ dò bù đúng đoạn đó.
- Dòng `sig` lưu thêm `RangeT0/RangeT1` (giờ mở nến đầu range / nến CF) để vẽ lại hộp range mờ của lệnh đã đóng; dòng cũ thiếu 2 trường vẫn nạp (không vẽ hộp).

## Bảng trên chart (4 dòng, dòng 4 luôn hiện)
```
BENZO CORVEN corven-7 · N lệnh · WR x % · ΣR
Fail Break · n · WR x % · ΣR
Break · n · WR x % · ΣR
Backtest 35 phiên: +0,02R/lệnh, hơn vào ngẫu nhiên (−0,01R) chưa đủ chắc · chạy thử, không phải khuyến nghị
```
Trên chart: hộp range (xanh lơ = ACTIVE, chấm = PENDING, xám đứt = BROKEN), đường đứt tại cạnh vừa phá của thế B đang sống,
mũi tên + hộp SL/TP tại nến CF, nhãn ngắn `Fail Break sell · Δ ngược + bóng đỏ 18` (luôn hiện).

## Gửi lệnh sang MT5 (Exness) — mặc định TẮT
Settings nhóm riêng: **Gửi lệnh sang MT5** [TẮT] · **MT5: chạy thử (chỉ ghi nhật ký)** [BẬT] · **MT5: thư mục Files** [trống = `%APPDATA%\MetaQuotes\Terminal\Common\Files`].
- Mỗi lệnh MỚI ghi 1 dòng JSON vào `benzo_cmd.jsonl` (file riêng, không dùng chung `runner_cmd`/`entry_cmd`). EA `mt5-runner-bridge/RunnerBridge.mq5` đọc.
  Không gửi giá tuyệt đối (futures lệch spot): chỉ `side` + `sl_dist` (= |entry − SL|, USD/oz) + `rr` = 2; EA vào market rồi đặt SL/TP quanh giá khớp. Trường `src_*` và `setup` chỉ để ghi nhật ký.
- Mẫu dòng: `{"id":"BENZO|GCZ26|202610210310|B|BR","ts_utc":"2026-10-21 03:11:00","ts_local":"2026-10-21 10:11:00","tz":7,"src":"GCZ26","branch":"BR","side":"BUY","sl_dist":3.2,"rr":2,"src_entry":4127.4,"src_sl":4124.2,"src_tp":4133.8,"setup":"Break","dry":true}`
- Chống bắn trùng/lệnh cũ: chỉ lệnh có nến vào là nến **vừa đóng**; lần quét đầu sau attach/reload/dựng lại chỉ nạp id; tuổi ≤ 90 giây so với đồng hồ UTC (lệch hơn thì bỏ + báo lý do trên bảng); id tất định. Bật gửi giữa chừng không bắn bù lệnh sinh ra lúc tắt.
- Bảng chart thêm 1 dòng: `MT5 (chạy thử): đã gửi N · lệnh cuối dd/MM HH:mm Break buy SL 3,2` (hoặc lý do bỏ). Các mục MT5 **không** nằm trong khoá cache tín hiệu.
- Cài EA, ba giai đoạn chạy thử → thật: xem `mt5-runner-bridge/README.md` (mục BenzoTrader). EA phải có `benzo_cmd.jsonl` trong `InpCmdFile`.
- Code: `BenzoMt5.cs` (logic thuần, có unit test `tests/TestsMt5.cs`).

## Telegram
```
🔴 SELL · CORVEN Break · GCZ26 · 00:23 VN
Mốc: cạnh dưới 4127,4 vừa phá (range 4127,3–4132,5)
Dấu hiệu (2): Δ ngược giá ΣΔ -62/2 nến · bóng đỏ 18 @4127,3 (3,6× nền)
CF 00:23 thân 0,6 giá · Vào 4126,6 · SL 4129,1 (2,5) · TP 4121,6 (2R, R sẵn 1,9)
⚠ Chưa có lợi thế đo được (+0,02R/lệnh, 35 phiên)

✅ CORVEN Break +1,9R · 00:23→00:32          (R đã trừ chi phí 0,2; TIME ghi thêm "(hết phiên)")
⚪ CORVEN Fail Break 03:59 huỷ — nến xác nhận là nến cuối phiên
```
**Mọi giờ trong tin = giờ MỞ nến** (nến CF / nến thoát), trùng `time_vn` của CSV, cột `t_vn` Python và nhãn thời gian nến trên Quantower.
Chống trùng: lần quét đầu sau reload chỉ nạp id; chỉ bắn tín hiệu ở nến vừa đóng, tuổi ≤ 90 giây; khoá file `%LOCALAPPDATA%\BenzoTrader\sent\`.
Ảnh chụp vùng chart (cửa sổ Optimus Flow phải đang hiện, không thu nhỏ). Log `tele_log.txt` (che token), lỗi code `error_log.txt`.

## CSV (thư mục `%LOCALAPPDATA%\BenzoTrader\`)
- **Lệnh** `signals_<mã>_1m_corven-7.csv`:
  `time_utc,time_vn,the,side,range_lo,range_hi,b_from_exhausted,moc,n_signs,signs,entry,sl,tp,risk,r_avail,outcome,exit_time,r,mfe_r,mae_r,phien`
  — `signs` đúng **từng byte** cột `dau_hieu` của Python (kể cả dấu trừ ASCII `-` trong "Δ to -36", "ΣΔ -62" — để parity so thẳng chuỗi); `mfe_r/mae_r` = chạy xa nhất thuận/nghịch (theo R) từ vào tới đóng; `phien` = Á/Âu/Mỹ.
- **Ứng viên bị loại** `candidates_<mã>_1m_corven-7.csv` (chỉ live, nến vừa đóng): `time_utc,the,side,moc,gate,detail` —
  `gate` ∈ `③ 0 loại`, `③ 1 loại`, `④ CF`, `④ R<1,7`, `SL > X giá`, `⛔ veto kiệt sức`, `⛔ quét stop`, `⛔ chồng range`, `chặn giờ`,
  `cuối phiên`, `tin USD`, `thế đã có lệnh`, `đang có lệnh`, `Fail Break tắt`, `Break tắt`.
  (`SL > X giá`: X = Settings "SL tối đa (giá)", file CSV ghi số thật, vd `SL > 5,0 giá`; `Fail Break tắt`/`Break tắt` = công tắc Settings.)
  (`thế đã có lệnh` = luật 4d "1 lệnh/thế, 1 lệnh/(range, cạnh, thế)"; `đang có lệnh` = đang có lệnh mở. Danh sách này có unit test so với mã.)

## Parity
`research/parity_corven.py` → `research/report/PARITY-CORVEN.md`: TRAIN 97/97 lệnh khớp cả kết cục/R, mọi CF ứng viên khớp;
phần TEST (sau 2026-09-15) **chỉ so định danh**, khoá 2 lớp: (1) ReplayCorven `--hide-after` ghi trống kết cục TEST ngay trong tiến trình;
(2) `parity_corven.py` kiểm lại — ô kết cục TEST nào không rỗng ⇒ dừng + xoá thư mục tạm (pytest `test_parity_corven.py`). Không in/đọc R hay WR của TEST
(giữ TEST nguyên vẹn cho giả thuyết "chỉ phiên Âu" ở plan mục 9).
