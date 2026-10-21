# Benzo Trader — indicator signal mới cho Quantower / Optimus Flow (bản 1, 2026-10-21)

> Agent chính: Fable 5.1. Agent con: Sonnet 5.5, mỗi agent một setup, làm việc độc lập, báo kết quả về
> agent chính để brainstorm rồi sửa tiếp. File này là trục: mọi quyết định đều ghi ở đây trước khi code.

## 0. Mục tiêu người học đặt ra, và sự thật từ các phép đo cũ

| Người học muốn | Số đo đã có trong repo |
|---|---|
| Winrate tổng 60–70% | EntrySignal live 28 phiên: 42,9%. Hợp lưu ≥2 vùng (backtest 28 ngày): +0,30R@2R, ~3 lệnh/ngày. Nhật ký tay 29/9→15/10: 29%. |
| 10–20 lệnh/ngày | EntrySignal: ~1 lệnh/ngày. Hợp lưu ≥3: 0,4 lệnh/ngày. Nhật ký tay: 3–8 lệnh/ngày. |
| R:R 1:2 hoặc 1:3 | Hệ thống Đêm Vàng: A/B 3R, C/D 2R. SL 2–4 giá (CORVEN). |

Ba kết luận đo trên 724.279 nến M1 (2 năm) mà bot **phải tôn trọng**, không được "quên":
1. **Tín hiệu M1 đứng một mình không có lợi thế** (hấp thụ, bong bóng, stacked imbalance, đặc trưng nến: đều ≈50%).
   Lợi thế chỉ xuất hiện khi **có vùng kẻ từ phiên trước + bối cảnh (VWAP tuần/ngày) + chế độ**.
2. **Vùng có số liệu ủng hộ đảo chiều:** VWAP tuần (53,8%), VWAP ngày (52,9%). **Vùng nghiêng đi tiếp:**
   HVN ngày ngay sau phá cực trị (43,5%), HVN 3 tuần (45,7%), không ở vùng nào (47,4%).
3. **Luật nào cũng phải sống ở cả hai nửa thời gian.** Combo tìm trên 2,5 tháng chết trên 22 tháng và ngược lại.

⇒ Cách làm trung thực: xây bot theo đúng 4 kịch bản của Hệ thống, **đo thật** trên dữ liệu dày, báo con số thật.
Nếu số thật không tới 60–70%, báo thẳng và chỉ ra ô nào gần nhất, **không ép tham số cho đẹp**.
Mục tiêu 10–20 lệnh/ngày chỉ đạt được khi bot chạy **cả ngày** (Á + Âu + Mỹ) chứ không chỉ 19:00–23:00 VN;
phần đo phải tách riêng theo phiên để người học thấy phiên nào ăn, phiên nào lỗ.

## 1. Nguồn đầu vào đã đọc

- Hệ thống Đêm Vàng v1.2 (`daily-trading/HE-THONG-DEM-VANG.html`): tầng vùng → chế độ → 4 kịch bản A/B/C/D
  → luật SL 3 điều kiện → ngắt mạch. `daily-trading/RULES.md`, `REVIEW-2026-10-15.md`.
- Nhật ký 16/9 → 15/10 (106 lệnh): 3 lệnh +3R tốt nhất đều = vùng kẻ trước + phe ngược thử và thất bại + SL ngoài nhiễu.
  Lỗi chính: gọi sai tên (V gọi là U, đà gọi là hấp thụ), SL 2 giá đặt ngay tại đường tham chiếu, vào lại 3–4 lần cùng vùng,
  vào ngay sau nến dài nhất phiên, lệnh giữa range.
- Dữ liệu: `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d{,_bars}.csv` — **65 phiên, trung vị
  133.471 hợp đồng/phiên, 1.379 nến M1/phiên, một hợp đồng (không có chỗ nối)**. Giờ trong file là **UTC**.
  Bộ 2 năm `fp_GC_XCEC_Time_20240801-20260819_748d9h*` (474 phiên sạch sau khi loại chỗ nối) để kiểm độ bền.
- Indicator hiện có: `SessionZones` + `ProfileEngine` (vùng, VWAP tuần, HVN, VA, tin Forex Factory, Telegram),
  `OrderFlowBubbles` (hấp thụ/bong bóng, baseline median+MAD, SignalCache niêm phong tín hiệu), `EntrySignal`
  (khung Telegram mở/đóng, Simulate, bảng). Chỉ **mượn khung kỹ thuật**, không mượn luật.
- Quantower SDK (`TradingPlatform.BusinessLayer.dll` 1.146): **không có API chụp ảnh chart**. Chụp bằng Win32
  (`GetWindowRect` cửa sổ chính Optimus Flow + `Graphics.CopyFromScreen`) rồi gửi `sendPhoto`.

## 2. Kiến trúc Benzo Trader

```
benzo-trader/
  research/            ← Python, backtest. kernel.py dùng chung, setup_a..d.py mỗi agent một file
    kernel.py          data loader · tách phiên · vùng (chỉ từ phiên trước) · chế độ · mô phỏng SL/TP · metrics
    setup_a_pha_hoi.py  setup_b_hap_thu.py  setup_c_fade_canh.py  setup_d_trap.py
    report/            ← mỗi setup một RESULTS-*.md, số thật, hai nửa thời gian, theo phiên Á/Âu/Mỹ
  BenzoTrader.cs       ← indicator Quantower (concat ProfileEngine.cs khi build), port 1:1 từ kernel + setup
  build.sh · tests/    ← build bằng ~/quantower-libs/qw-build.sh, unit test logic thuần
  README.md
```

### 2.1 Năm khối trong indicator
1. **Vùng (Zones)** — tính từ dữ liệu phiên TRƯỚC, cập nhật khi đổi phiên (không nhìn trước):
   VWAP tuần (hạng 1) · VWAP ngày (hạng 2) · VAH/VAL/POC phiên Âu hôm nay (cạnh range) · VAH/VAL/POC hôm qua ·
   HVN ngày/tuần (chỉ làm mục tiêu / vùng phá hồi, **không fade**) · IB (19:20–20:20 VN).
2. **Chế độ (Mode)** — mỗi nến M5 đóng: `CÂN BẰNG` (chưa có nến M5 đóng ngoài VA Âu/IB) · `VỪA PHÁ` (đã đóng
   ngoài, hồi về cạnh giữ được) · `TREND` (≥ 2 nến M5 liên tiếp đóng ngoài và cách cạnh ≥ 3 giá).
3. **Bốn bộ dò setup** (mục 3) — chỉ chạy trên nến M1 **đã đóng**, chỉ khi giá ở vùng (≤ 1 giá) hoặc râu chạm vùng.
4. **Rủi ro (Risk)** — SL lai: `max(sau râu nến xác nhận, mép xa vùng) + 0,3 giá`, **sàn** = biên độ nến M1 cao nhất
   trong 5 nến, **trần 4 giá**; TP theo setup (A/B 3R, C/D 2R). R:R cố định, không nới.
5. **Ngắt mạch (Guard)** — mỗi vùng tối đa 2 lệnh/phiên · 0 lệnh trong 3 nến sau nến dài nhất phiên · 0 lệnh ±15′ tin
   USD mức cao (lịch Forex Factory, mượn `ProfileEngine.FfNews`) · 1 lệnh mở cùng lúc · 3 SL liên tiếp ⇒ nghỉ 60′.

### 2.2 Đầu ra
- **Chart:** mũi tên + nhãn tên setup tại nến vào; đường SL/TP mỏng tới khi đóng lệnh.
- **Bảng (góc trên trái, 5 dòng, chữ nhỏ):**
  ```
  BENZO · Tổng 12 lệnh · 8 thắng · 4 thua · 66,7% · +12,0R
  A Phá hồi   4 · 3/1 · 75% · +8R
  B Hấp thụ   3 · 2/1 · 67% · +5R
  C Fade cạnh 4 · 2/2 · 50% · +2R
  D Trap      1 · 1/0 · 100% · +2R   (tắt từ 20:30? không — luật ở mục 5)
  ```
  Mặc định đếm **từ đầu lịch sử chart đã nạp**; nút bấm 1 lần "Đặt lại thống kê" (xoá bộ đếm từ giờ).
- **Telegram mỗi lệnh (sendPhoto):** ảnh chụp màn hình Optimus Flow + chú thích:
  ```
  🟢 BUY · A Phá hồi · GCZ26 · 20:24 VN
  Lý do: phá VAH Âu 4192,0 lúc 20:10 (M5 đóng ngoài), hồi hình U 4 nến, nến xác nhận Δ+41 thân 0,8 giá
  Vào 4193,1 · SL 4190,6 (2,5 giá) · TP 4200,6 (3R)
  ```
  Và tin đóng: `✅ A Phá hồi +3R · 20:24→20:51` / `🛑 −1R`.
- **CSV log** `%LOCALAPPDATA%\BenzoTrader\signals_<symbol>.csv` để đối chiếu Python ↔ C#.

### 2.3 Cấu hình — tối giản (người học: "những con số đấy tôi chẳng bao giờ set lại")
| # | Input | Mặc định | Vì sao phải có |
|---|---|---|---|
| 1 | Lệch giờ (UTC→VN) | 7 | feed |
| 2 | Telegram: bật | tắt | — |
| 3 | Telegram: bot token | (trống) | repo công khai, điền tay |
| 4 | Telegram: chat id | (trống) | |
| 5 | Telegram: gửi thử | nút | |
| 6 | Bật setup A / B / C / D | 4 công tắc, bật | tắt một setup khi thấy nó lỗ |
| 7 | Đặt lại thống kê | nút | |
| 8 | Hiện bảng | bật | |

**Không có** ngưỡng số nào trong Settings. Mọi ngưỡng là hằng trong code, chốt bằng backtest, ghi ở mục 3.

## 3. Bốn setup — định nghĩa đo được (bản khởi điểm, agent con được sửa SAU khi đo, phải ghi lý do)

Ký hiệu: `giá` = 1 USD = 10 tick. `u` = trung vị biên độ nến M1 50 nến gần nhất. `|Δ|` = delta nến.
Nến xác nhận (`CF`) theo chiều S: đóng theo chiều S, thân ≥ 50% biên độ, Δ cùng dấu, |Δ| ≥ trung vị |Δ| 50 nến.
"Ở vùng Z": |close − Z| ≤ 1 giá, hoặc râu chạm Z trong nến.

### A · Phá hồi (chế độ VỪA PHÁ, mục tiêu 3R)
1. Cú phá được công nhận: 1 nến M5 đóng ngoài cạnh VA Âu / IB (cạnh `E`) theo chiều S; **không** trong 18:00–19:20 VN.
2. Nhịp hồi về `E` hình U: ≥ 3 nến M1, **không nến hồi nào có biên độ ≥ nến dài nhất của move phá**, hồi không đóng
   ngược trở lại trong VA (tức nến M5 không đóng lại trong).
3. Tại `E` (≤ 1 giá): nến `CF` theo chiều S. Vào ở giá đóng `CF`.
4. SL: `max(râu CF, mép xa E) + 0,3`, sàn/trần ở mục 2.1. TP 3R.
5. Loại: hồi hình V (1 nến hồi ≥ nến dài nhất move) · hồi < 3 nến · đã 2 lệnh ở `E` · trong 3 nến sau nến dài nhất phiên.
Tham số tự do: số nến hồi tối thiểu (3), tỉ lệ thân CF (0,5). **Không thêm tham số thứ ba.**

### B · Hấp thụ (giá tới VWAP tuần / VWAP ngày, mục tiêu 3R)
1. Giá tới vùng Z ∈ {VWAP tuần, VWAP ngày} bằng một move ≥ 3 giá theo chiều M (chiều của move).
2. 3 nến cuối chạm Z: **thân và |Δ| giảm dần**, không cực trị mới vượt quá Z + 0,5 giá.
3. Nến `CF` ngược chiều M, |Δ_CF| ≥ 50% |Δ| nến lớn nhất của move. Vào ở giá đóng CF.
4. SL: sau cực trị cụm 3 nến + 0,3. TP 3R.
5. Loại: đang đồng thời phá VA Âu theo chiều M (đó là A) · chế độ TREND cùng chiều M · Z là HVN ngày/3 tuần ·
   nến lớn nhất phiên nằm trong 3 nến cuối.
Lưu ý số đo cũ: hấp thụ "đúng nghĩa ở bất kỳ vùng nào" 57,6% (n=126) — ô hứa hẹn nhất nhưng n nhỏ. Agent B phải
báo n thật; **n < 100 lệnh trên 65 phiên thì chưa kết luận**.

### C · Fade cạnh (chế độ CÂN BẰNG, mục tiêu 2R)
1. Chế độ CÂN BẰNG: chưa có nến M5 đóng ngoài VA Âu (hoặc IB nếu chưa có VA Âu).
2. Phá hụt: râu nến M1 xuyên cạnh `E` ≥ 2 tick, đóng lại **trong** range. Δ nến ủng hộ chiều vào (ngược chiều xuyên).
3. Vào ở giá đóng nến đó. SL sau râu phá hụt + 0,3. TP = min(cạnh đối diện, POC Âu) nhưng ≥ 2R; nếu < 2R ⇒ bỏ.
4. Loại: nến xuyên là nến dài nhất phiên (chờ nến sau) · râu ngược dài hơn thân · đã 2 lệnh ở `E`.
Tham số tự do: độ xuyên tối thiểu (2 tick), khoảng cách cạnh đối diện tối thiểu.

### D · Trap (có move rõ + nhịp hồi, mục tiêu 2R)
1. Move rõ ≥ 5 giá theo chiều S (zigzag ngưỡng 2 giá), **cùng chiều bias phiên** (bias = giá vs VWAP tuần lúc 19:00 VN).
2. Nhịp hồi ngược tới một vùng Z (VWAP ngày, POC/cạnh VA hôm qua, cạnh VA Âu), hồi ≤ 70% move.
3. Ở đỉnh nhịp hồi: nến hồi có Δ thuận chiều hồi nhưng đóng dưới nửa thân (phe hồi thử và thất bại), rồi `CF` theo S.
4. SL sau đỉnh nhịp hồi + 0,3. TP 2R.
5. Loại: không có move ≥ 5 giá trong 30 nến · hồi > 70% · chế độ CÂN BẰNG (24/9: trap trong sideway = lỗi).

## 4. Khung backtest chung — luật bắt buộc cho mọi agent

1. **Không nhìn trước.** Vùng từ phiên trước; VWAP ngày/tuần cộng dồn tới nến hiện tại; chế độ từ nến M5 đã đóng.
2. **Chỉ nến đã đóng.** Vào ở giá đóng nến xác nhận; mô phỏng từ nến kế tiếp; nến chạm cả SL lẫn TP ⇒ tính SL.
3. **Chi phí:** trừ 0,2 giá/lệnh (spread + trượt, GC tick 0,1) khi tính R.
4. **Tách đôi thời gian:** 2026-07-23→09-15 (tìm luật) · 2026-09-16→10-21 (kiểm). Luật phải dương ở cả hai.
   Sau đó chạy thêm trên 2 năm (`fp_GC_XCEC_*`, loại ±2 phiên quanh chỗ nối) — báo cả hai nửa 2024-08→2025-08 và 2025-08→2026-08.
5. **Báo theo phiên:** Á (05:00–12:30 VN), Âu (12:30–19:00), Mỹ (19:00–04:00). Mục tiêu 10–20 lệnh/ngày sẽ được
   đối chiếu bằng tổng cả 3 phiên.
6. **Tối đa 2 tham số tự do mỗi setup**, quét lưới thưa (3×3), báo cả bảng chứ không chỉ ô tốt nhất.
   Ô tốt nhất mà hàng xóm xấu hẳn = khớp quá mức, không chọn.
7. **Đối chứng:** cùng vùng, cùng chế độ, nhưng vào ở nến ngẫu nhiên cùng chiều — để biết setup thêm được gì.
8. Mỗi báo cáo `RESULTS-<setup>.md` phải có: n, lệnh/ngày, WR, R trung bình, kỳ vọng/lệnh, chuỗi thua dài nhất,
   bảng theo tháng, bảng theo phiên, 2 nửa thời gian, 5 ví dụ thắng + 5 thua kèm giờ UTC để soi chart.

## 5. Thứ tự làm việc
1. **Agent Kernel** (Sonnet): viết `kernel.py` + test nhỏ (vùng khớp định nghĩa ProfileEngine; VWAP tuần neo đầu tuần
   CME; tách phiên theo khoảng trống > 30′). Xuất `kernel_check.md` (vài số kiểm: số phiên, VA Âu 3 ngày mẫu).
2. **4 agent setup** chạy song song, mỗi agent một file, báo về agent chính. Agent chính brainstorm → gửi hướng sửa →
   agent sửa → báo lại. Tối đa 3 vòng mỗi setup.
3. Agent chính gộp 4 setup, chạy **tổng hợp** (chồng lệnh: 1 lệnh mở cùng lúc, ưu tiên A > B > D > C), ra bảng tổng.
4. **Agent C#** port `BenzoTrader.cs` 1:1 từ kernel + 4 setup, kèm Telegram ảnh, bảng, CSV log; build + unit test;
   deploy vào Optimus Flow; gửi thử Telegram.
5. Parity: chạy Python trên CSV live do indicator ghi ra ↔ tín hiệu C# ghi ra; lệch ⇒ sửa C#.

## 6. Quyết định đã chốt (QĐ)
- **QĐ-1** Không có ngưỡng số trong Settings; mọi hằng ghi trong code + README.
- **QĐ-2** Bot chạy cả ngày, nhưng bảng thống kê và báo cáo tách phiên; người học quyết định tắt phiên nào sau khi
  thấy số. (Hệ thống Đêm Vàng chỉ nói phiên Mỹ; mục tiêu 10–20 lệnh/ngày buộc phải mở rộng.)
- **QĐ-3** R:R cố định theo setup (A/B 3R, C/D 2R). Không be hòa trong bot (be là việc tay; bot chỉ đo SL/TP cứng).
- **QĐ-4** Ảnh Telegram = chụp cửa sổ Optimus Flow (Win32), không phải vẽ lại chart. Chart phải đang hiện trên màn hình.
- **QĐ-5** Nếu sau 3 vòng một setup vẫn < 50% WR ở 2R hoặc kỳ vọng âm ở cả hai nửa thời gian ⇒ setup đó **tắt mặc định**
  trong indicator (vẫn có công tắc), và báo rõ trong README. Không ép.
- **QĐ-6 (người học chốt 2026-10-21):** **CHỈ đo trên file 90 ngày `fp_GCZ26_XCEC_Time_20260723-20261021_90d*`** (3 tháng
  gần nhất, một hợp đồng GCZ26). **Bỏ hẳn file 2 năm `fp_GC_XCEC_*`** vì dữ liệu footprint trước đó sai mã hợp đồng, lệch
  nhiều. Hệ quả: n nhỏ hơn, TRAIN ≤ 2026-09-15 / TEST từ 2026-09-16 là phép kiểm duy nhất; mọi bảng "2 năm" trong các
  RESULTS vòng 1 chỉ còn giá trị tham khảo, không dùng để quyết định. Khi có export mới cùng mã thì nối thêm vào.
