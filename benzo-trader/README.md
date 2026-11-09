# Benzo Trader — setup CORVEN (corven-1) trên nến M1 đã đóng

**Setup là gì:** một setup "follow theo footprint" của CORVEN, cơ khí hoá theo `plans/BENZO-CORVEN-plan.md` — có range (Range Box)
⇒ chờ giá về mốc gần (thế A: fail break cạnh range; thế B: phá range rồi giữ được) ⇒ cần **≥ 2 loại dấu hiệu** order flow
(Δ, bóng, kiệt sức, stacked, trap) ⇒ vào ở giá đóng nến xác nhận, SL sau cực trị cú thủng/mốc, TP 2R.
**Số backtest (35 phiên TRAIN, file 90 ngày GCZ26):** 97 lệnh, **−0,29R/lệnh** [KTC 95 % −0,55; −0,02], kém cả hai đối chứng
— vào mọi nến xác nhận tại mốc không cần dấu hiệu (C1 −0,24R) và vào ngẫu nhiên cùng giờ cùng hướng (C2 −0,08R).
**Đang forward test để người học review và sửa dần, KHÔNG phải khuyến nghị vào lệnh** (người học chọn lựa chọn A, plan mục 10).

Bốn setup A/B/C/D cũ đã bỏ (không setup nào có lợi thế đo được) — kết quả cũ: `research/report/TONG-KET-VONG-1-2.md`.

## Build / deploy / test
```bash
cd benzo-trader
bash build.sh                      # nối nguồn → qw-build.sh → dist/BenzoTrader.dll → copy vào C:\OptimusFLOW\Settings\Scripts\Indicators\BenzoTrader\
dotnet run -c Release --project tests                  # unit test: 12 ca plan mục 4 + cache 10.5 + nhãn 10.3 + hồi quy 97 lệnh TRAIN
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
| `BenzoCorven.cs` | `CorvenParams` (bộ tham số corven-1, đóng cứng) · `CorvenMachine` (①② range → thế A/B → mốc) · `CorvenRules` (③ dấu hiệu, ④ lệnh + ⛔) · `DetectorCorven` (chọn lệnh 4d) — port y chữ `research/setup_corven.py` |
| `BenzoOrderFlow.cs` | nền_ô, bóng, delta ngược giá, trap, định dạng số kiểu Python — port `research/of_signals.py` |
| `BenzoCore.cs` | `Signal`, mô phỏng SL/TP/TIME + MFE/MAE, thống kê thế A/B, bảng + nhãn trung thực, caption Telegram, cache niêm phong + guard, `BenzoEngine`, CSV |
| `BenzoZones.cs` | tách phiên (khoảng trống > 30′), giờ neo Mỹ (`sm`), phiên Á/Âu/Mỹ |
| `BenzoTrader.cs` | lớp dán Quantower: Settings, vòng đời, vẽ, Telegram + chụp ảnh |
| `tools/ReplayCorven` | chạy DetectorCorven trên file Footprint Export → CSV cho parity (phần TEST ghi trống kết cục) |
| `tools/OfSignalsDump` | parity stacked/kiệt sức GĐ0 (giữ) |
| `research/` | Python chuẩn: `setup_corven.py`, `of_signals.py`, `kernel.py`, `results_corven.py`, `controls_corven.py`, `sweep_corven.py`, `parity_corven.py`; file setup cũ ở `research/_old/` (không build, không test) |

## Settings (plan 10.2 — CHỈ công tắc, không có ngưỡng số)
Lệch giờ · Telegram: bật / bot token / chat id / gửi thử · **Bật setup CORVEN (chạy thử — backtest −0,29R/lệnh, kém vào ngẫu nhiên)** [BẬT] ·
**Chặn 19:20–20:30 VN (mốc neo Mỹ)** [BẬT] · **Hiện range** [BẬT] · **Hiện dấu hiệu đã đếm** [BẬT] · Đặt lại thống kê · Hiện lại toàn bộ thống kê · Hiện bảng [BẬT].
Không đưa `win_b / bubble_mult / need_signs / đệm SL / "gần" / lọc phiên` ra Settings: đổi tham số sống mà không đo lại = đúng lỗi A/B/C/D,
và mỗi bộ tham số là một chuỗi forward test riêng (n live ≈ 3 lệnh/ngày — chia nhỏ là vô nghĩa).

## Setup corven-1 (tóm tắt — chi tiết và lý do từng con số ở plan mục 1, 6–10)
- **① Bối cảnh:** Range Box nguyên trạng. Thế A = FailBreak về ACTIVE (CF là nến FailBreak hoặc 1–2 nến sau, đóng trong range, cách cạnh ≤ 1 mbr).
  Thế B = BreakConfirmed (gồm cả range hết lượt ReEntry, cờ `b_from_exhausted`), chưa ReEntry, ≤ 30 nến, cấu trúc 1 nến chưa gãy ngược.
- **② Mốc gần:** cạnh vừa phá (râu chạm cạnh ± tol trong cửa sổ 3 nến, CF đóng cách cạnh ≤ 1 mbr) hoặc vùng stacked mới cùng hướng
  (Body, không Weak, chưa từng bị chạm, chưa bị đóng xuyên).
- **③ ≥ 2 loại dấu hiệu** trong cửa sổ test: Δ to (≥ 2× medΔ) hoặc Δ ngược giá · bóng đúng phe (≥ 3× nền_ô và ≥ 10 hợp đồng) ·
  kiệt sức phe ngược chưa bị quét · stacked mới đóng phía hướng vào · trap (quét mốc + bóng ngược màu trong râu). Vùng đang làm mốc không đếm.
- **④ Lệnh:** CF thân ≥ 0,4 biên độ, đóng sát cực trị (≤ 0,3), biên độ ≥ 0,5 mbr, Δ cùng dấu ≥ 0,5 medΔ. SL sau cực trị cú thủng (A) /
  mốc (B) + đệm max(3 tick, 0,2 mbr), sàn 1 mbr, trần 4 mbr. R sẵn tới mục tiêu ≥ 1,7, TP luôn 2R. 1 lệnh mở; 1 lệnh/thế;
  1 lệnh/(range, cạnh, thế); không vào 15 nến đầu phiên, khi có tin USD ±15′, và (công tắc) 19:20–20:30 VN.
- **⛔:** kiệt sức chống hướng chưa bị quét (5 nến) · nhịp đẩy do quét stop (thế B) · range chồng range (thế A, chỉ từ FailBreak thứ 2).
- Lệnh còn mở qua khoảng trống > 30′ đóng `TIME` tại giá đóng nến cuối phiên.

## Quyết định khi port (plan 10)
- Bộ tham số = **bộ gốc vòng 1** (RESULTS-CORVEN.md), `LogicVersion = "corven-1"`. **Không port:** ngoại lệ "xác nhận lần 2" (A2),
  neo SL pivot, `overlap_max_drop`, lọc phiên mỏng/chỗ nối của Python.
- **Nến cuối phiên:** Python biết trước nến cuối nên không vào; C# không biết trước ⇒ vào rồi **huỷ** khi nến đầu phiên sau tới
  (Telegram gửi tin huỷ, khoá 4d được trả lại). Kết quả lệnh giống Python 100 %.
- **Range chồng range / mục tiêu thế B:** Python đọc cạnh range cũ ở cuối file; C# đọc tại lúc xét (không nhìn trước). Không gây lệch trên file 90d.
- **Tin USD** ±15′: lệch có chủ đích duy nhất (Python không có lịch tin). Lịch tin chỉ phủ tuần hiện tại.
- **Chọn lệnh khi bận (G7):** đang có lệnh mở thì mọi CF khác bị bỏ (không xếp hàng); cùng một nến xét thế A trước thế B, rồi theo range.
- Range M15 ("rối thì lên M15") **không làm ở v1** — để v2 sau khi v1 có số. ⛔ "đấu giá vừa xong (profile nhọn)" **bỏ** (chưa đo được).
- Δ "thẳng" (`max_delta`) không dùng ở cả Python lẫn C# (export lịch sử ghi `max_delta = delta`).

## Cách đề xuất sửa tín hiệu (vòng "review → update")
1. Xem `candidates_<mã>_1m_corven-1.csv` (ứng viên bị loại + cổng chặn) và `signals_…csv` (cột `mfe_r/mae_r`) để tìm chỗ "thấy đẹp mà máy không vào" hoặc ngược lại.
2. Viết đề xuất thành **luật có số** (không phải "nhìn thấy"), sửa `research/setup_corven.py` trước.
3. Đo lại trên TRAIN cùng 2 đối chứng C1/C2 (`results_corven.py`, `controls_corven.py`) — đề xuất phải hơn đối chứng, không chỉ hơn số cũ.
4. Đạt mới sửa C#, tăng `LogicVersion` (`corven-2`…) ⇒ cache cũ tự bỏ; chạy unit test + `parity_corven.py` phải 100 %.
5. Không bao giờ đổi tham số bằng nút bấm trên chart.

## Vòng đời, cache, chống tính lại
- Chỉ xử lý nến **đã đóng** (`Count−2`), mỗi nến dò **một lần**; `ClosedBars` chặn nhìn nến sau `closedIdx`.
- **Niêm phong** `%LOCALAPPDATA%\BenzoTrader\cache_<mã>_<aggName>_<phút>m.jsonl` (tên có khung — sửa bug cũ dùng `Aggregation.Title`).
  Khoá phiên bản = `corven-1-us<0|1>` (theo công tắc chặn giờ); "Hiện range"/"Hiện dấu hiệu" chỉ vẽ nên không vào khoá.
  **Guard khớp nến:** mỗi dòng `sig` lưu H/L nến CF; khi gắn lại, giá vào lệch > nửa tick hoặc H/L lệch > 1 tick ⇒ **bỏ toàn bộ cache**,
  dò lại từ đầu, ghi 1 dòng `error_log.txt`. File cache cũ `cache_<mã>_<Title>.jsonl` của A/B/C/D tự xoá khi gặp.
- 1 lệnh mở cùng lúc; chạm cả SL lẫn TP cùng nến ⇒ SL; chi phí 0,2 giá/lệnh.
- "Đặt lại thống kê" ghi mốc UTC vào `reset_<mã>.txt`; "Hiện lại toàn bộ thống kê" xoá mốc.

## Bảng trên chart (4 dòng, dòng 4 luôn hiện)
```
BENZO CORVEN corven-1 · N lệnh · WR x % · ΣR
Thế A · n · WR x % · ΣR
Thế B · n · WR x % · ΣR
Backtest 35 phiên: −0,29R/lệnh, kém vào ngẫu nhiên (−0,08R) · chạy thử, không phải khuyến nghị
```
Trên chart: hộp range (xanh lơ = ACTIVE, chấm = PENDING, xám đứt = BROKEN), đường đứt tại cạnh vừa phá của thế B đang sống,
mũi tên + hộp SL/TP tại nến CF, nhãn ngắn `A sell · Δ ngược + bóng đỏ 18` (tắt bằng "Hiện dấu hiệu đã đếm").

## Telegram
```
🔴 SELL · CORVEN thế B · GCZ26 · 00:23 VN
Mốc: cạnh dưới 4127,4 vừa phá (range 4127,3–4132,5)
Dấu hiệu (2): Δ ngược giá ΣΔ -62/2 nến · bóng đỏ 18 @4127,3 (3,6× nền)
CF 00:23 thân 0,6 giá · Vào 4126,6 · SL 4129,1 (2,5) · TP 4121,6 (2R, R sẵn 1,9)
⚠ Chưa có lợi thế đo được (−0,29R/lệnh, 35 phiên)

✅ CORVEN thế B +1,9R · 00:23→00:32          (R đã trừ chi phí 0,2; TIME ghi thêm "(hết phiên)")
⚪ CORVEN thế A 03:59 huỷ — nến xác nhận là nến cuối phiên
```
Chống trùng: lần quét đầu sau reload chỉ nạp id; chỉ bắn tín hiệu ở nến vừa đóng, tuổi ≤ 90 giây; khoá file `%LOCALAPPDATA%\BenzoTrader\sent\`.
Ảnh chụp vùng chart (cửa sổ Optimus Flow phải đang hiện, không thu nhỏ). Log `tele_log.txt` (che token), lỗi code `error_log.txt`.

## CSV (thư mục `%LOCALAPPDATA%\BenzoTrader\`)
- **Lệnh** `signals_<mã>_1m_corven-1.csv`:
  `time_utc,time_vn,the,side,range_lo,range_hi,b_from_exhausted,moc,n_signs,signs,entry,sl,tp,risk,r_avail,outcome,exit_time,r,mfe_r,mae_r,phien`
  — `signs` đúng định dạng cột `dau_hieu` của Python; `mfe_r/mae_r` = chạy xa nhất thuận/nghịch (theo R) từ vào tới đóng; `phien` = Á/Âu/Mỹ.
- **Ứng viên bị loại** `candidates_<mã>_1m_corven-1.csv` (chỉ live, nến vừa đóng): `time_utc,the,side,moc,gate,detail` —
  `gate` ∈ `③ 0 loại`, `③ 1 loại`, `④ CF`, `④ R<1,7`, `④ trần SL`, `⛔ veto kiệt sức`, `⛔ quét stop`, `⛔ chồng range`, `chặn giờ`,
  `tin USD`, `đang có lệnh`, `thế đã có lệnh`.

## Parity
`research/parity_corven.py` → `research/report/PARITY-CORVEN.md`: TRAIN 97/97 lệnh khớp cả kết cục/R, mọi CF ứng viên khớp;
phần TEST (sau 2026-09-15) **chỉ so định danh** — ReplayCorven ghi trống kết cục TEST ngay trong tiến trình, không in/đọc R hay WR của TEST
(giữ TEST nguyên vẹn cho giả thuyết "chỉ phiên Âu" ở plan mục 9).
