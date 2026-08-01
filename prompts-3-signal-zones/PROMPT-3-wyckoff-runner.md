# SESSION 3 — WyckoffRunner (v7): dựng KB-A / KB-B trên đúng bộ vùng CORVEN

Bạn đang làm việc trong repo `/home/asl86/Documents/footprint-tpo`. Đây là một **phiên nghiên cứu +
code**, không phải phiên dạy học. Trả lời tiếng Việt, ngắn gọn theo CLAUDE.md.

**Có 2 session Claude khác đang chạy song song trong CÙNG thư mục này** (một lo `EntrySignal.cs`, một lo
`RunnerSignal.cs`). Quyền ghi ở PHẦN 2 là **bắt buộc** — cùng thư mục nghĩa là bạn sửa file dùng chung
thì số liệu của session khác đổi ngay giữa lúc họ đang đo.

> `WyckoffRunner.cs` là **cỗ xe được chỉ định** cho việc này (`PLAN_KB_ABC.md §8`: chỉ sửa file này, không
> đụng `RunnerSignal.cs` đang chạy live). Bạn **được** đổi mặc định của file này — nhưng phải ghi rõ mọi
> mặc định đã đổi vào RESULTS, vì nó đang được forward-test và log tín hiệu live.

---

## PHẦN 0 — Đọc trước, im lặng (đừng vừa đọc vừa giảng)

Đọc hết bằng tool call liên tiếp, chỉ báo ngắn "đang đọc tài liệu", **chưa** kết luận gì:

1. `CLAUDE.md` — luật trả lời ngắn + luật commit/push
2. `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md` — **BẢN CHỐT**. Đọc kỹ §1, §2, §3, §4, §6.
3. `data-export/messages-with-pro-trader/CAU_HOI_CAN_THONG_NHAT.md` — câu trả lời gốc của người học
   (mục A, B, C). Đây là nguồn của SPEC, đọc để không diễn giải lệch.
4. `quantower-entry-signal/PLAN_KB_ABC.md` — **plan của chính việc bạn đang làm. Đọc TOÀN BỘ.**
   Đặc biệt §2 (bốn chặn), §3 (tầng vùng), §4 (đặc tả 3 kịch bản), §5 (các pha), §6 (PASS/KILL + kiểm
   chứng đặc tả), §7 (không đo được offline).
5. `quantower-entry-signal/research/wyckoff/BASELINE.md` — §0, §1 (bảng số chuẩn), §3 (cấu hình chốt), §6.
6. `quantower-entry-signal/research/wyckoff/AUDIT_V7.md` — kỷ luật đo. Đọc kỹ §7 và §13.
7. `quantower-entry-signal/SPEC_V7_3KB.md` — đặc tả v7 hiện tại (dài; đọc §1.2 mốc phiên, §5.5 MFE đảo chiều).
8. `quantower-entry-signal/research/DATA_CAPABILITY.md` — múi giờ từng nguồn, giới hạn per-level.
9. `quantower-tpo-suite/BACKTEST-ZONES-V2.md` — bài học: bộ vùng "cải tiến" đo ra **không hơn ngẫu nhiên**.
10. `quantower-entry-signal/WyckoffRunner.cs` — file bạn sở hữu.
11. `quantower-entry-signal/research/wyckoff/v8/zones_corven.py` — zone provider CORVEN đã có (P1 đã khởi
    động; **vẫn READ-ONLY** — xem PHẦN 2 để biết vì sao).
12. `quantower-entry-signal/research/wyckoff/v7/` — `engine.py`, `report.py`, `loaders.py`, `run_kb12.py`.

---

## PHẦN 1 — Bối cảnh: bạn đang thực thi phần chính của PLAN_KB_ABC

CORVEN chỉ dùng **HVN tuần, HVN ngày, VWAP tuần (neo đầu tuần), VWAP ngày**. Không POC/VAH/VAL, tuyệt
đối không vùng theo từng phiên Á-Âu-Mỹ (*"tất nhiên là không rồi"*).

Phát hiện then chốt của plan (§0): **hai engine đang có đã chính là hai play của CORVEN, chỉ neo sai vùng.**

| Đang có trong v7 | Là play nào | Sai ở đâu |
|---|---|---|
| **KB1 / CBR** — phá range co hẹp → hồi → tiếp diễn. `n=33 WR=48.5% +47.0R EV=+1.424 MDD=3R @RR4` | **PLAY2 — phá vùng → hồi → đánh tiếp** | neo **range co hẹp M1 nội bộ**, không phải **HVN** |
| **KB2 / QUAY_DAU** — chạm → fade. `n=27 WR=55.6% +10.5R EV=+0.389 @RR1.5`, **mặc định TẮT** (FAIL, p=0.072) | **PLAY1 — chạm vùng → đảo chiều** | neo **chỉ VWAP phiên**; thiếu HVN tuần/ngày, thiếu VWAP tuần |
| KB3 (biên↔biên) | không thuộc hệ CORVEN | giữ nguyên trạng KILL, **không hồi sinh** |

⇒ Việc chính **không phải viết engine mới**, mà là **đổi tầng neo vùng** + **thêm nến xác nhận M1** +
**thống nhất RR**, rồi cho **cùng một cặp play** chạy trên **hai tầng vùng**: tuần (**KB-A**) và ngày
(**KB-B**).

**Chống trùng tên (plan §1):** `KB-A/KB-B/KB-C` (có gạch) = kịch bản CORVEN, chia theo *tầng vùng*.
`PLAY1/PLAY2` = cách đánh tại vùng. `KB1/KB2/KB3` (không gạch) = tên **cũ**, chỉ dùng khi trích số lịch
sử — **không đặt tên module mới bằng nó**.

**KB-C (follow order flow trong move) NGOÀI phạm vi session này** — nó cần dữ liệu per-level chỉ có
25-46/60 ngày và `max_one_trade = 0` ở mọi file (không đo được "big trade" thật, chỉ có proxy). Plan §2.4
đã quyết: làm sau cùng, **không cấp vốn dựa trên backtest**. Đừng làm nó ở đây.

Cấu hình v7 đang ship (đọc lại từ code): `CleanBreak=true` (`CleanLook/Win/ClosePos = 20/5/0.50`),
`PullMax=1.00`, `RR=4.0`, `LiquidityFilter=true` (`0.75`), `TrendFilter=true`, `VwapAlign=true` (đã xác
nhận **NO-OP** trên cửa sổ này — đừng tính là một lớp lọc đã chứng minh), `EnableReversal=false`,
`SkipDeadSession=true` + `DeadUseUtc=true` + `2/8` **giờ UTC**.

---

## PHẦN 2 — Quyền ghi (BẮT BUỘC)

**Được ghi:**
- `quantower-entry-signal/WyckoffRunner.cs`
- `quantower-entry-signal/dist/WyckoffRunner.dll` (do `./build-wyckoff.sh` sinh ra)
- `quantower-entry-signal/research/wyckoff/v8/wyckoff/**` (thư mục mới, của riêng bạn)
- `quantower-entry-signal/research/wyckoff/v8/wyckoff/RESULTS_KB_AB.md` (báo cáo của bạn)

**READ-ONLY tuyệt đối:**
- `quantower-entry-signal/EntrySignal.cs`, `RunnerSignal.cs`
- `quantower-tpo-suite/**` (kể cả `ProfileEngine.cs`, `SessionZones.cs`)
- `research/wyckoff/cbr_v6.py`, `research/wyckoff/v7/**`, `research/entry_dxfeed.py`,
  `research/imp_reversal_sweep.py`, `research/entry_month.py`
- **`research/wyckoff/v8/zones_corven.py`** — bạn là chủ danh nghĩa của file này, **nhưng 2 session khác
  đang import nó từ cùng một thư mục làm việc.** Sửa nó = đổi số của họ giữa lúc họ đang đo. ⇒ **Đóng
  băng.** Cần sửa/mở rộng thì copy sang `v8/wyckoff/zones_ab.py` rồi sửa bản copy.
- mọi file `.md` ngoài RESULTS của bạn (kể cả `PLAN_KB_ABC.md` — plan nói rõ: kết quả ghi vào file RESULTS
  riêng, **không sửa ngược vào plan**)

Cách làm đúng khi cần đổi module dùng chung: **copy → chứng minh bản copy tái lập đúng số gốc (GOLDEN) →
rồi mới sửa bản copy.** Phát hiện bug thật ở file dùng chung thì ghi vào RESULTS mục "bug ở file dùng
chung" để người học xử lý sau, đừng tự sửa.

**Git — 3 session dùng chung một thư mục và chung nhánh `main`:**
- Chỉ `git add` **đúng những file của bạn**. **Tuyệt đối không `git add -A` / `git add .`** (sẽ nuốt việc
  đang dở của session khác).
- Trước khi push: `git pull --rebase --autostash origin main` rồi `git push origin main`.
  (`--autostash` để không fail vì session khác đang có file dở dang.)
- Gặp `index.lock` hoặc push bị từ chối → **chờ vài giây, thử lại một lần**. Vẫn lỗi thì báo người học,
  đừng dùng `--force`, đừng `git reset`.
- Cuối **mỗi lượt có sửa file**: `git status` → add (chọn lọc) → commit (message tiếng Việt) → pull
  --rebase --autostash → push → **báo hash + kết quả push**.

---

## PHẦN 3 — Các pha, mỗi pha có ĐIỂM DỪNG (theo `PLAN_KB_ABC.md §5`)

Sau mỗi pha: in bảng số → **dừng, báo người học, chờ xác nhận** → mới đi pha sau. Không gộp pha.

### P0 — GOLDEN + đo cột "TRƯỚC"
1. **GOLDEN:** chạy `v7/run_kb12.py`, phải tái lập **đúng** `BASELINE.md §1`: KB1 `n=33 WR=48.5% +47.0R
   EV=+1.424 MDD=3R`, KB2 `n=27 EV=+0.389`. Không khớp → dừng, truy nguyên nhân, báo. Chưa khớp thì
   chưa được đo gì tiếp.
2. Đo cột **TRƯỚC** cho KB1 và KB2 riêng, bằng chính harness sẽ dùng để đo cột SAU. Nếu harness của bạn
   ra số khác `run_kb12.py` thì **truy tới khớp**, đừng ghi hai bộ số song song.
3. **Nguồn dữ liệu:** dxFeed qua `entry_dxfeed.load_m1()` (3 tháng thanh khoản 5-7/2026). **Không** dùng
   `fp-m1-6-month.csv` cho bất cứ thứ gì liên quan volume/HVN — cột Volume **hỏng 04/06→26/06**
   (BASELINE §8). Ghi rõ nguồn + cửa sổ.
4. `volfloor`: dùng hằng **`VOLFLOOR_FROZEN=20.0`**, **không** gọi `calc_volfloor()` (look-ahead, đã sửa
   2026-07-29 — đừng tái phát).
5. ⚠ **Múi giờ:** `b['dt']` của dxFeed là **UTC**, không phải giờ VN. Bẫy này đã làm sai một lần
   (lọc khung chết v5 vô hiệu). Mọi lọc theo giờ phải nói rõ neo múi giờ nào.

### P1 — Tầng vùng: kiểm trước khi tin (plan §3)
`v8/zones_corven.py` đã có `group_days`, `group_weeks`, `vwap_series`, `hvn_of`, `build_zone_series(B,
mode='week'|'day', causal='closed'|'running')`, `zone_lookup_series`. Việc của bạn là **kiểm chứng**, chưa
phải tin:

- Chạy `python3 quantower-entry-signal/research/wyckoff/v8/zones_corven.py`, xem output.
- **In 13 mốc tuần** của 5-7/2026 và tự kiểm bằng mắt. Mốc tuần = phiên đầu tiên có start ≥ **CN 21:00
  UTC**; DST của Mỹ làm giờ nghỉ CME dịch **21h↔22h UTC** → mốc dễ lệch 1 giờ. Plan §3.1 yêu cầu bước
  này tường minh, đừng bỏ.
- **HVN tuần** = một profile cho **cả tuần** dựng từ M1, rồi `find_hvn`. **Chỉ HVN**, không POC/VAH/VAL.
  In số vùng/tuần và số vùng/ngày; sweep `min_ratio ∈ {1.3, 1.5, 1.8}`, chọn theo **cao nguyên**.
- **Nhân quả (plan §3.2) — A/B cả hai chế độ, không chọn sẵn:**
  - `W_CLOSED`: chỉ dùng HVN của tuần **đã đóng** (N-1) cho toàn tuần N. An toàn tuyệt đối.
  - `W_RUNNING`: HVN tuần đang chạy, tính lại tại **mỗi lần đóng phiên**, chỉ từ dữ liệu đã đóng.
  - Tương tự `D_CLOSED` / `D_RUNNING` cho vùng ngày.
- **Kiểm look-ahead bằng số:** cắt chuỗi ở t, tính lại vùng, so với vùng tính từ chuỗi đầy đủ — phải
  trùng khít. Không trùng = có nhìn tương lai → dừng, báo, không đo tiếp.

### P2 — Probe MFE cho PLAY1 (plan §2.2 — chặn, phải làm trước khi chốt RR)
Người học chốt RR 1:3 cho mọi kịch bản. Nhưng repo đã đo **MFE trần của lệnh đảo chiều ≈ 1.3R**
(SPEC §5.5) → đó là lý do KB2 dùng RR1.5. **Không tranh luận — đo.**

- Với tập tín hiệu PLAY1 neo **HVN tuần/ngày** (không phải VWAP phiên như lần đo cũ), in phân phối MFE
  theo R: `P(MFE≥1.5R)`, `P(≥2R)`, `P(≥3R)`, `P(≥4R)`.
- `P(MFE≥3R) ≥ 35%` → RR3 khả thi, đi tiếp theo spec.
- `< 20%` → **báo lại người học kèm số**, đề xuất RR3 cho PLAY2 / RR1.5-2 cho PLAY1. **Không tự đổi spec.**

### P3 — KB-A: PLAY1 + PLAY2 trên vùng TUẦN
Module mới trong `v8/wyckoff/`, tên **không** chứa `kb1/kb2/kb3`:
- `zones_ab.py` (nếu cần mở rộng zone provider — bản copy, xem PHẦN 2)
- `confirm_m1.py` — nến xác nhận M1, dùng chung 2 play
- `play_touch.py` — PLAY1 chạm→đảo (giữ parity: gọi lại logic `imp_reversal_sweep.detect`, đừng viết lại
  từ đầu)
- `play_breakret.py` — PLAY2 phá→hồi→tiếp (giữ parity: gọi lại `cbr_v6`, `edge` = **mép HVN** thay vì
  mép range co hẹp)
- `run_ab.py` — chạy tất cả + in bảng + đối chứng ngẫu nhiên

Đặc tả (plan §4):
- **Bất biến:** `RR=3.0` (chờ P2 xác nhận) · TP theo R cố định · **đóng trong ngày**, không qua đêm · SL
  neo **dưới/trên cây M1 vào lệnh** + buffer 2 tick, sàn/trần **2.0 / 4.0 giá** · **bắt buộc nến xác nhận
  M1** · router 1 vị thế (dùng `v7/engine.route_one_position`, đã có 15/15 test PASS).
- **PLAY1:** giá tới vùng (tol đề xuất 12 tick, sweep `{8,12,20}`) → nến xác nhận M1 **ngược** hướng chạm
  → vào. Giữ gate **R2** (vùng bị chạm phải ở 25% biên của range gần) và **R10** (phải có nến từ chối
  **CÓ** volume — cấm dùng "volume thấp" làm tín hiệu đảo).
- **PLAY2:** nến đóng vượt qua vùng → trong `WaitBars` giá hồi về mép vùng nhưng **giữ** → nến xác nhận
  M1 **thuận** hướng phá → vào.
- **Nến xác nhận M1** ⟦định nghĩa đề xuất, CẦN KIỂM⟧, LONG (SHORT gương lại): `close > open` **và**
  `cpos ≥ 0.60` **và** thân ≥ 30% range **và** râu ngược ≤ 35% range. **Bắt buộc A/B
  `ConfirmOn ∈ {false,true}`** — bật mà EV không tăng thì nó chỉ là bộ lọc giảm n, phải biết bằng số chứ
  không giữ vì "pro trader nói vậy".
- In bảng: PLAY1 riêng / PLAY2 riêng / gộp KB-A. Rất có thể một play sống một play chết.

### P4 — Đối chứng ngẫu nhiên KB-A (plan §5 P4: **cổng chặn cả plan**)
Dịch mọi vùng **±3 giá**, giữ nguyên toàn bộ logic còn lại, **5 seed**.
- `EV(thật) − EV(ngẫu nhiên) ≥ +0.25R` → đi tiếp.
- `< +0.10R` → **KB-A KILL, dừng cả plan**. Báo người học. Đây là kết quả hợp lệ, không phải thất bại của
  bạn — bài học `BACKTEST-ZONES-V2.md` cho thấy bộ vùng nghe rất hợp lý vẫn có thể không hơn ngẫu nhiên.

### P5 — KB-B: cùng bộ logic trên vùng NGÀY, rồi so A vs B
**Kiểm chứng đặc tả (plan §6.3) — dùng chính lời CORVEN làm phép thử định nghĩa vùng:**
1. **Tần suất:** KB-A ≈ **10 lệnh/tuần** ⇒ 13 tuần nên ra **~130 lệnh**. Ra `<30` hoặc `>400` thì **định
   nghĩa vùng/trigger của bạn lệch khỏi hệ anh ấy** → sửa định nghĩa **trước** khi đọc EV. Đây là kiểm
   *conformance*, độc lập với chuyện có lãi hay không.
2. **Thứ tự WR:** phải có `WR(KB-A) > WR(KB-B)` (người học xác nhận). Đo ra **ngược** thì hoặc vùng tuần
   dựng sai, hoặc lời anh ấy không đúng trên cửa sổ này — **cả hai đều phải báo**, không im lặng chọn cái
   tốt hơn.

### P6 — Chi phí giao dịch
Quét phí `0 → 8 tick/lượt`. EV phải còn dương ở **≥ 4 tick**. Chết ở ≤2 tick = KILL.

### P7 — Port sang C# `WyckoffRunner.cs` v8 (chỉ làm nếu P4, P5, P6 qua)
- Thêm input tầng vùng (`CorvenTier`: tuần / ngày / tắt) + `ConfirmOn` + `CleanBreak` giữ nguyên nghĩa cũ.
  Bạn **được** đổi mặc định của file này, nhưng **liệt kê mọi mặc định đã đổi** trong RESULTS.
- **Không** hồi sinh KB3. **Không** xoá code/pool cũ (còn cần đối chiếu lịch sử).
- Dùng `ProfileEngine.FindHvn` / `RowsOver` / `VwapAt` / `WeekSpans` (đã có, chỉ **đọc**).
- Build: `cd quantower-entry-signal && ./build-wyckoff.sh` — phải **0 warning 0 error**.
- **Parity harness (plan §5 P8): ≥95% lệnh khớp** giữa C# và Python trên cùng cửa sổ. Lệch thì truy tới
  khớp, đừng "gần đúng là được". Nhớ hai nguồn lệch đã biết: `cbr_v6.py` chưa mô phỏng `Dedup` gộp
  CBR+reversal, và C# bỏ nến cuối còn Python quét hết (BASELINE §7).

---

## PHẦN 4 — Vòng loop test → cải thiện (luật của vòng lặp)

Lặp: **đo → đổi ĐÚNG MỘT thứ → đo lại → giữ/bỏ**.

- **Hạn mức 10 cấu hình MỖI KỊCH BẢN** (plan §6.2). Đếm và báo. Bonferroni: p phải < 0.005 mới coi là
  thật. Vượt hạn mức = đang dò tìm, không được ship.
- **Cao nguyên, không mũi nhọn:** tham số thắng phải có láng giềng cũng thắng.
- **Không nới gate để tăng số lệnh** (plan §8). Bài học 2026-07-31: n tăng ×2.4 mà EV về 0 là **thất bại**.
- Mỗi vòng ghi 1 dòng vào bảng lịch sử trong RESULTS: đổi gì → n/WR/EV/MDD → giữ hay bỏ → vì sao.
- Ngưỡng (plan §6.2): `n≥25` PASS-able; `n<15` KILL; `15≤n<24` = **"không kết luận"**, không ship.
  WR@RR3 ≥35% PASS / <28% KILL. EV ≥+0.40R PASS / <+0.20R KILL. MDD ≤8R PASS / >15R KILL.
  Theo tháng: ≤1 tháng âm, |R|≤2R, **và tháng 7 không được âm**. Hai nửa kỳ: cả hai >0.
- **Quy tắc DỪNG:** WR nhảy >10 điểm **hoặc** n tụt >40% → dừng soi cơ chế trước khi giữ. Đây là luật đã
  từng được áp đúng (BASELINE §4) — tôn trọng nó, đừng tự chốt qua đầu nó.

---

## PHẦN 5 — Bảng cuối (deliverable chính)

Kết thúc, in **trong chat** và lưu vào `v8/wyckoff/RESULTS_KB_AB.md`. Làm **4 bảng** cùng khuôn:
`KB-A/PLAY1`, `KB-A/PLAY2`, `KB-B (gộp 2 play)`, `portfolio gộp` — và một bảng **so KB-A vs KB-B**.

```
| Thông số | TRƯỚC (v7, tự đo P0) | SAU (vùng CORVEN) | Δ |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ |  |  | (phải giống nhau) |
| Neo vùng | range co hẹp M1 / VWAP phiên | HVN tuần / HVN ngày / VWAP tuần-ngày |  |
| Chế độ nhân quả | — | W_CLOSED / W_RUNNING |  |
| n (số lệnh) |  |  |  |
| n / tuần | | | (đối chiếu mốc ~10 của CORVEN) |
| WR % |  |  |  |
| Tổng R |  |  |  |
| EV / lệnh (R) |  |  |  |
| MDD (R) |  |  |  |
| Tháng 5 (R) |  |  |  |
| Tháng 6 (R) |  |  |  |
| Tháng 7 (R) |  |  |  |
| Nửa kỳ 1 (R, n) |  |  |  |
| Nửa kỳ 2 (R, n) |  |  |  |
| LONG: n / WR / EV |  |  |  |
| SHORT: n / WR / EV |  |  |  |
| EV − EV(ngẫu nhiên, 5 seed) |  |  |  |
| EV @ phí 2 tick |  |  |  |
| EV @ phí 4 tick |  |  |  |
| RR đang dùng |  |  |  |
| P(MFE≥3R) (chỉ PLAY1) | — |  |  |
| ConfirmOn: EV tắt → bật | — |  |  |
| Số cấu hình đã thử |  |  | /10 |
| KẾT LUẬN | — | PASS / KILL / không kết luận |  |
```

Cột Δ: ghi dấu (`+`/`−`) và **thêm mũi tên nghĩa** khi dấu không tự nói (MDD giảm là **tốt** → `−2.0R ↑`).
Ô nào không đo được thì ghi `—` kèm lý do một dòng, **không bỏ trống, không bịa**.

Kèm sau bảng, ngắn gọn:
1. Bảng lịch sử vòng lặp (đổi gì → kết quả → giữ/bỏ).
2. **Hai phép kiểm conformance** của §6.3: tần suất ~10 lệnh/tuần có đạt không, và `WR(KB-A) > WR(KB-B)`
   đúng hay sai. Đây là phép thử xem *định nghĩa vùng của mình có đúng ý CORVEN không* — báo kể cả khi sai.
3. Mọi **mặc định C# đã đổi** so với v7.
4. Cái gì **không** đo được và vì sao (plan §7).
5. Một câu trả lời thẳng: **vùng CORVEN có làm KB-A/KB-B tốt hơn v7 không, hay chưa chứng minh được?**

---

## PHẦN 6 — Luật trung thực (đọc lại trước khi viết bảng cuối)

- **Không tuyên bố cải thiện khi chưa có đối chứng ngẫu nhiên.** "Đúng ý pro trader hơn" ≠ "tốt hơn".
- **Không có một điểm out-of-sample nào.** `AUDIT_V7 §7`: 100% số liệu từ **một** cửa sổ 3 tháng, **một**
  regime (vàng tạo đỉnh), **một** hợp đồng. Cửa sổ OOS 2025-11→2026-04 không chạy được (chỉ 171 nến qua
  gate = 0,33%). GCQ26 vừa qua First Notice Day 31/07 → cần GCZ26/continuous mới có OOS thật. Nhắc **1
  câu** trong báo cáo, không diễn giải dài.
- **Kỳ vọng dùng để tính vốn là +0.7R, không phải EV in-sample.** `AUDIT_V7 §13` / `BASELINE §0`: KB1
  là kẻ sống sót của ≥94 cấu hình trên cùng một cửa sổ; Bonferroni đưa p 0.0003 → 0.028. Nếu bạn báo một
  EV mới, phải kèm chiết khấu tương tự, đừng báo số thô như thành tích.
- **Kết quả âm là kết quả tốt.** KB-A KILL ở P4 là một câu trả lời có giá trị. Đừng đi tìm cấu hình thứ
  11 để cứu một kết luận.
- Đọc số thật trước, giải thích sau. Không in giả thuyết kèm bảng.
- Tách LONG/SHORT ở mọi bảng (thiếu sót cố hữu — `AUDIT` mục K).
- Không sửa số cũ trong `BASELINE.md`/`PLAN_KB_ABC.md` cho khớp số mới của bạn — ghi vào RESULTS của bạn.
