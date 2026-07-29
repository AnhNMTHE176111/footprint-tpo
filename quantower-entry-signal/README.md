# quantower-entry-signal — Gợi ý điểm vào lệnh (footprint M1)

Indicator M1 real-time gợi ý Entry/SL/TP cho vàng theo cách người dùng đánh (bias + vùng + footprint,
2 kịch bản phá&hồi / chạm&đảo). **Thiết kế đầy đủ ở [PLAN.md](PLAN.md).** Chưa implement.

## Phát hiện then chốt (backtest 28 ngày dữ liệu thật)
- Tín hiệu cơ học **thô** (bắn ở mọi vùng) **không có edge** — tệ hơn ngẫu nhiên (MFE/MAE 0.86 vs 1.05).
- **HỢP LƯU ≥2 vùng chồng nhau = bộ lọc THẬT:** +0.30R@2R (74 lệnh), đơn điệu theo bậc confluence,
  **giữ ở cả 2 nửa tháng** (chống overfit). ~3 lệnh/ngày.
- Phá&hồi > chạm&đảo. SL 2–4đ > 6đ. VSA/climax/VWAP-đơn-lẻ **không** tự tạo edge → chỉ là thành phần hợp lưu.
- Lớp **footprint theo mức giá (hấp thụ/imbalance)** chỉ có **LIVE** → validate bằng log, không backtest được.

## Research (tái lập số)
```bash
python3 research/entry_month.py   # backtest chính 28 ngày (4 cấu hình + soi 2 ví dụ 7/24)
python3 research/research.py      # MFE/MAE vs baseline + subset + SL sweep
python3 research/research2.py     # chống overfit: đơn điệu confluence + chia đôi 28 ngày
python3 research/profile_data.py  # mổ cột dữ liệu (cột sống/chết)
```

## Đã implement (P0–P2) + verify offline
`EntrySignal.cs` — indicator M1 hoàn chỉnh lõi: dựng vùng từ M1, **confluence-gate ≥2**, KB1 phá&hồi,
KB2 chạm&đảo (gate tường hấp thụ `PriceLevels` live), nến-đóng-only, VSA khớp `VsaVolume`, SL≤6đ,
TP nới vùng kế, render mũi tên/nhãn/bảng. Build: `./build-entry.sh` → `dist/EntrySignal.dll` (0 warning).

**Verify offline đã làm:**
- Build sạch Linux (net10.0-windows, concat ProfileEngine).
- **3 agent review đối kháng**: (1) parity từng-dòng vs `research/entry_month.py`, (2) thread-safety/vòng đời,
  (3) C# correctness/GDI/hiệu năng. Đã fix mọi phát hiện thật (lệch index→vùng theo thời gian; rescan mỗi
  tick→1 lần/nến-đóng; try/catch+SetClip; |Δ|≥15, dedup 6t, prev_rel nhị phân; clamp SlCap; risk theo tick).
- Logic scan KHỚP bộ đã backtest (`entry_month.py`); khác biệt còn lại là **cố ý**: vùng volume-based live
  (chính xác hơn TPO offline), gate confl≥2, KB2 cần tường hấp thụ live.

**CHƯA test được offline (bản chất — cần LIVE Windows):**
- Phần glue Quantower (kéo `HistoricalData`, `PriceLevels`, render GDI).
- Tường hấp thụ / imbalance per-level (data export không có ladder).

## Verify LIVE (bước quyết định — cần máy Windows)
1. Copy `dist/EntrySignal.dll` vào `...\Settings\Scripts\Indicators\EntrySignal\`, add vào **chart M1** có Volume Analysis.
2. Kiểm: vùng HỢP LƯU vẽ đúng chỗ, tín hiệu chỉ hiện trên nến ĐÃ ĐÓNG (không nhấp nháy), không lag khi tick nhanh.
3. **Log 1–2 tuần**: đối chiếu tín hiệu A/B với kết quả thật + với lệnh tay của bạn (vd Entry-1 mẫu:
   LONG tại VWAP+VAH Á+VAL Âu, climax tím — indicator phải gắn cờ đúng).
4. Chỉnh input theo feed: `TzOffset`, mốc giờ phiên, `VolFloor`, ngưỡng hấp thụ.
```

## EntrySignal (scalp 1.5R) — Test data mới + tự vào MT5 + Telegram (2026-07-28)

### Test lại trên data mới `data-export/27-7/` (dxFeed GCQ26 9 tháng, `research/entry_dxfeed.py`)
Data dxFeed **chỉ OHLCV, KHÔNG có delta** → backtest phải chạy **delta-free** (thay gate delta bằng
hướng nến `close>open`; edge thật = **hợp lưu + retest-giữ-vùng + VSA**, delta chỉ cộng hưởng nhỏ).
- **Cross-check (`research/entry_xcheck.py`):** trên cùng fp-m1 (có delta), delta-free **KHÔNG tệ hơn**
  delta-ful (WR 61% vs 55%) → bỏ delta là proxy hợp lệ. NHƯNG **hai feed lệch nhau lớn**: cùng kỳ
  6-7/2026, fp-m1 cho WR **61%** còn dxFeed **42%** → scalp **nhạy feed**; dxFeed là proxy YẾU cho live.
- **Baseline (cluster≥2, SL4, RR1.5) trên dxFeed 5-7/2026:** WR 44%, exp **+0.11R**; **tháng 5 (OOS) 65%**,
  tháng 6 45%, tháng 7 **39%** (nhạt dần — đúng lúc chạy live).
- **Vòng lặp cải tiến (`research/entry_round2.py`):** **cluster≥3 là đòn bẩy mạnh nhất** — exp
  **+0.36R**, WR 55%, **cả 3 tháng dương**, và **rải đều nhiều kịch bản** (không do 1 lệnh may). RR **1.5
  là tối ưu** (RR1.0→+0.09, RR2.0→+0.09). **VWAP-align & lọc thanh khoản LÀM HẠI** scalp (ngược với
  RUNNER). **Lọc thuận xu hướng** giúp cluster≥2 (+0.16) nhưng **cắt nhánh chạm&đảo ngược-trend đang
  thắng** → không stack với cluster≥3.
- **Trung thực:** n=33 (cluster≥3) trên 3 tháng xu-hướng-tăng = mẫu nhỏ; memory cũ từng thấy ≥3 âm trên
  mẫu LỚN TRỘN kỳ mỏng. Phía SHORT gánh cửa sổ này (vàng tạo đỉnh tháng 7) = **regime, không phải cấu
  trúc** → KHÔNG hard-bias short. Vì dxFeed ≠ feed live, **không đổi mặc định lõi**; chỉ thêm **đòn bẩy
  tuỳ chọn** + để user A/B live.

### Thêm vào EntrySignal.cs
- **Lọc thuận xu hướng (toggle, mặc định TẮT):** proxy TPO = `close` vs `close` cách `TrendLookback`
  nến (mặc định 480 ~8h, khớp RUNNER v5). Bật nếu muốn ưu tiên momentum; TẮT để giữ nhánh đảo chiều.
  → Muốn theo phát hiện mạnh nhất: **đặt `Số vùng hợp lưu tối thiểu`=3** (đòn bẩy chính, ~0.4 lệnh/ngày).
- **Cầu nối MT5 (tự vào lệnh):** cùng cơ chế RunnerSignal — ghi JSONL `entry_cmd.jsonl` (chỉ `side +
  sl_dist + rr`, KHÔNG giá tuyệt đối vì futures↔spot lệch basis). Chống trùng: arm lần đầu chỉ nạp id,
  chỉ nến vừa đóng, tuổi ≤90s, id tất định. Mặc định **dry-run BẬT** + `Mt5Bridge` TẮT.
  - **EA:** dùng lại `mt5-runner-bridge/RunnerBridge.mq5`. Chạy **1 instance EA riêng** trỏ
    `InpCmdFile=entry_cmd.jsonl` + `InpDoneFile=entry_done.txt` (tránh đụng runner). Hoặc đổi input
    `MT5: tên file lệnh` = `runner_cmd.jsonl` để **chung 1 EA** (id khác nhau nên không trùng; nhưng
    `InpMaxPositions=1` sẽ khiến Runner & Entry tranh 1 slot). Branch ghi `SCALP_BR/SCALP_REV` — EA
    không chặn (chỉ chặn CBR/REV) nên vào lệnh bình thường.
- **Telegram (mở + đóng):** giống RunnerSignal — 🔔 mở (MUA/BÁN, phá&hồi/chạm&đảo, hạng, hợp lưu×N,
  Entry/SL(giá)/TP(giá·R), TP2 nếu nới, lý do), ✅/🛑 đóng (+RR/−1R, vào→ra, giờ + thời lượng). Log riêng
  `%LOCALAPPDATA%\EntrySignal\tele_log.txt`. Điền token/chat_id **bằng tay** (repo public). Nút "TG · Gửi
  thử ngay". Build 0/0. **CHƯA test live Windows.**

## WyckoffRunner v7 (2026-07-29) — sau cổng audit chống overfit

**Trạng thái hiện tại của DLL.** Đọc [research/wyckoff/AUDIT_V7.md](research/wyckoff/AUDIT_V7.md) (cổng
chặn) + [research/wyckoff/PARITY_V7.md](research/wyckoff/PARITY_V7.md) (đối chiếu C#↔Python) trước khi sửa
bất cứ gì.

| Kịch bản | Trạng thái | Trong DLL |
|---|---|---|
| **KB1** — CBR: co cụm → phá → hồi → tiếp diễn | ✅ PASS **có điều kiện** | **BẬT**, kịch bản duy nhất được cấp vốn |
| **KB2** — quay đầu tại VWAP | ❌ FAIL (p=0.072; LONG EV chỉ +0.154R) | Có code, **`EnableReversal=false`** — bật chỉ để thu log OOS |
| **KB3** — scalp biên↔biên trong range | ❌ KILL (chết ở 2 tick phí; 0 range VALID trong 6 tháng OOS) | **Không có dòng code nào** |

- Parity thuật toán C#↔Python: **33/33 tín hiệu khớp, 0 lệch** (entry & SL khớp tới 0,0 tick).
  Parity DLL-trong-Quantower: **chưa đo** — cần CSV live từ máy Windows.
- Sửa 1 lỗi parity thật ở GĐ9: `liqbase` (C# lấy mean `Vol` không gồm nến hiện tại; Python lấy mean `Vma`
  có gồm) — 363/103.857 nến ra quyết định khác nhau, nhưng 0 tín hiệu đổi trên cửa sổ này. Đã sửa.
- ⚠ **Không có một điểm dữ liệu OOS nào** cho toàn dự án. Kỳ vọng dùng để tính vốn là **+0,7R/lệnh**
  (đầu dưới), không phải +1,424R của in-sample. Log live = phép OOS đầu tiên.

### v6 (nền của v7) — nâng cấp CBR theo lời pro trader CORVEN

`WyckoffRunner.cs` = clone của `RunnerSignal.cs` (v5 đang chạy live) để thử nâng cấp mà không đụng bản
đang ship. Toàn bộ kế hoạch, số liệu và giới hạn: **[WYCKOFF_V6_PLAN.md](WYCKOFF_V6_PLAN.md)** +
**[research/wyckoff/BASELINE.md](research/wyckoff/BASELINE.md)** (baseline đã đóng băng, kèm lệnh tái lập).

Thay đổi chính so với v5:
- **Sửa lỗi khung giờ chết**: bản v5 neo khung theo giờ HIỂN THỊ (`TzOffset`) nên vô tình cắt nhầm khung
  UTC 19–01 (vốn đã rỗng vì lọc thanh khoản) thay vì khung UTC 02–08 (khối lỗ thật). v6 thêm input
  `DeadUseUtc` (mặc định BẬT) neo trực tiếp theo UTC.
- **BREAK SẠCH** (`CleanBreak`): bỏ cú phá ngay sau một cú quét hụt cạnh đối diện (thị trường còn đang
  xoay 2 chiều — Wyckoff Phase B, chưa sang Phase D).
- `PullMax` 0.90→1.00, `RR` 3.0→4.0 (mặc định mới, có input để A/B).
- Build riêng: `./build-wyckoff.sh` → `dist/WyckoffRunner.dll` (0 warning).
- Nhánh QUAY_DAU (đảo chiều VWAP) giữ nguyên logic v2, chỉ dọn lại comment/label sai (`RevApproachBars`,
  `Cooldown`, `SlCapPts` không thực sự ràng buộc nhánh reversal trên mẫu hiện có; `AbsDom`/
  `RevClimaxOverride` chỉ là bonus hiển thị "hấp thụ ✓", KHÔNG nâng grade).

**Giới hạn** (xem đầy đủ ở BASELINE.md §giới hạn): dxFeed là proxy yếu so với feed live (scalp WR 61%
fp-m1 vs 42% dxFeed cùng kỳ); n=33 lệnh CBR/3 tháng; cửa sổ 5–7/2026 là regime vàng tạo đỉnh, chưa phải
out-of-sample thật; backtest không mô hình spread/slippage/phí.

## RunnerSignal — Báo Telegram (mở lệnh + đóng bởi SL/TP)
`RunnerSignal.cs` tự bắn Telegram **2 sự kiện mỗi lệnh**:
- **🔔 Mở lệnh** khi có tín hiệu MỚI ở nến vừa đóng — nội dung gọn: hướng (MUA/BÁN), nhánh (CBR hay
  Quay đầu VWAP), hạng A/B, giá **Entry / SL (kèm số giá) / TP (kèm RR)**, **lý do** (phá→hồi→tiếp diễn
  hoặc quay đầu tại VWAP) + các bullet chi tiết (hồi %, leg, VSA, hợp lưu…).
- **✅/🛑 Đóng lệnh** khi lệnh đó chạm TP/SL — kết quả (+RR / −1R), giá vào→ra, giờ mở→đóng + thời lượng.

**Cơ chế chống trùng (dùng lại khung cầu nối MT5):**
- Lần quét đầu sau khi add/reload chỉ **nạp** id lệnh cũ, **không bắn** (khỏi spam lịch sử).
- Tín hiệu mở phải ở **nến vừa đóng** + còn tươi (≤ `Tuổi tín hiệu tối đa`, mặc định 90s) → chống bắn lệnh cũ khi reload.
- **Chỉ báo ĐÓNG cho lệnh mà bot ĐÃ báo MỞ** (không báo đóng cho lệnh lịch sử/đang chạy lúc mới add).

**Cài đặt:** bật **"Báo Telegram: BẬT"**, điền **Bot token + Chat ID** (điền tay — repo public, KHÔNG hardcode).
Tùy chọn: tắt/bật báo mở, báo đóng, chỉ grade A, lọc nhánh CBR/Quay đầu. Nút **"TG · Gửi thử ngay"** để test
(bật→tắt; chạy độc lập với Volume Analysis). Log chẩn đoán: `%LOCALAPPDATA%\RunnerSignal\tele_log.txt`.
Chỉ chạy khi Quantower đang mở + dữ liệu live. Lưu ý DST: `TzOffset` dùng chung cho giờ hiển thị.
