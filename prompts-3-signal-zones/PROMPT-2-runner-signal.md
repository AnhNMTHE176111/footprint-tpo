# SESSION 2 — RunnerSignal (CBR M1, v5 ĐANG CHẠY LIVE): đổi tầng vùng sang bộ vùng CORVEN

Bạn đang làm việc trong repo `/home/asl86/Documents/footprint-tpo`. Đây là một **phiên nghiên cứu +
code**, không phải phiên dạy học. Trả lời tiếng Việt, ngắn gọn theo CLAUDE.md.

**Có 2 session Claude khác đang chạy song song trên cùng repo này** (một lo `EntrySignal.cs`, một lo
`WyckoffRunner.cs`). Quyền ghi ở PHẦN 2 là **bắt buộc**, vượt quyền là phá việc của session khác.

> ⚠️ **`RunnerSignal.cs` là bản v5 người học ĐANG CHẠY LIVE.** Mặc định của nó là tài sản đang hoạt động.
> Mọi thay đổi phải nằm sau một cờ **mặc định TẮT**. Không được đổi hành vi mặc định của file này, kể cả
> khi bạn đo được rằng cách mới tốt hơn — việc quyết định chuyển live là của người học.

---

## PHẦN 0 — Đọc trước, im lặng (đừng vừa đọc vừa giảng)

Đọc hết bằng tool call liên tiếp, chỉ báo ngắn "đang đọc tài liệu", **chưa** kết luận gì:

1. `CLAUDE.md` — luật trả lời ngắn + luật commit/push
2. `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md` — **BẢN CHỐT** về vùng. Đọc kỹ §2 và §3.
3. `quantower-entry-signal/PLAN_KB_ABC.md` — plan tổng. Đọc kỹ **§0** (bảng "engine nào là play nào"),
   §2 (bốn chặn), §6 (PASS/KILL), và **§8** (ghi rõ: không đụng RunnerSignal — xem PHẦN 1 bên dưới về
   cách hoà giải điều này với việc người học đã yêu cầu làm cả 3 signal).
4. `quantower-entry-signal/research/wyckoff/BASELINE.md` — §0, §3 (cấu hình đã chốt), §6 (giới hạn).
5. `quantower-entry-signal/research/wyckoff/AUDIT_V7.md` — kỷ luật đo, luật "n<25 = không kết luận".
6. `quantower-entry-signal/research/DATA_CAPABILITY.md` — §1.1/§1.2 (múi giờ từng nguồn), §4.
7. `quantower-tpo-suite/BACKTEST-ZONES-V2.md` — bài học: bộ vùng "cải tiến" đo ra **không hơn ngẫu nhiên**.
8. `quantower-entry-signal/RunnerSignal.cs` — file bạn sở hữu.
9. `quantower-entry-signal/research/wyckoff/cbr_v6.py` — replicator CBR (READ-ONLY, xem P0).
10. `quantower-entry-signal/research/wyckoff/v8/zones_corven.py` — zone provider CORVEN đã có (READ-ONLY).

---

## PHẦN 1 — Bối cảnh: vì sao phải đổi, và ranh giới với bản live

CORVEN chỉ dùng **HVN tuần, HVN ngày, VWAP tuần (neo đầu tuần), VWAP ngày**. Không POC/VAH/VAL, và
tuyệt đối không vùng theo từng phiên Á-Âu-Mỹ.

`RunnerSignal.cs` v5 có **hai nhánh**, và theo `PLAN_KB_ABC.md §0` thì **cả hai đã là đúng hai play của
CORVEN, chỉ neo sai vùng**:

| Nhánh v5 | Là play nào của CORVEN | Neo hiện tại | Neo đúng theo CORVEN |
|---|---|---|---|
| **CBR** (phá range co hẹp → hồi 60-90% → nến tiếp diễn, RR 3.0) | **PLAY2 — phá vùng → hồi → đánh tiếp** | `RangeLen=8` nến, span ≤ `RangeMaxPts=7.5` giá = **vùng co hẹp M1 nội bộ** | **mép HVN** (tuần/ngày) |
| **QUAY ĐẦU** (chạm VWAP phiên → rút râu → đảo, RR 1.5) | **PLAY1 — chạm vùng → đảo chiều** | **chỉ VWAP phiên** (`VwapTolTicks=12`) | **HVN tuần/ngày + VWAP tuần/ngày** |

Còn `BuildPool` (POC/VAH/VAL theo phiên + D-1) trong file này **chỉ để hiển thị hợp lưu và chấm grade
A/B**, không gate tín hiệu — nhưng nó có ảnh hưởng thật qua `MT5: chỉ gửi grade A` và `NhoiConflGate`.
Vậy có **hai** việc: đổi neo của 2 nhánh (quan trọng) và đổi pool hiển thị/grade (phụ).

**Hoà giải với `PLAN_KB_ABC.md §8`:** plan đó viết "không đụng RunnerSignal (v5 đang chạy live)". Người
học nay yêu cầu làm cả 3 signal. Cách hoà giải: **bạn được sửa file, nhưng mọi thứ mới nằm sau cờ mặc
định TẮT** → bản live không đổi một hành vi nào khi người học cập nhật DLL. Nếu bạn thấy không thể giữ
mặc định nguyên vẹn cho một thay đổi nào đó, **dừng và hỏi**, đừng tự quyết.

Cấu hình v5 đang ship (đọc lại từ code, đừng tin số ở đây nếu lệch): `RangeLen=8`, `RangeMaxPts=7.5`,
`PullMin=0.60`, `PullMax=0.90`, `RR=3.0`, `Cooldown=15`, `DedupBars=6`, `TrendFilter=true`,
`LiquidityFilter=true` (`LiquidityRatio=0.75`), `VwapAlign=true`, `RevRR=1.5`, `VwapTolTicks=12`,
`SkipDeadSession=true` + `DeadUseUtc=true` + `DeadStartHour/EndHour = 2/8` **giờ UTC**
(⚠ neo UTC, không phải giờ VN — lỗi này vừa được sửa 2026-07-31, đừng vô tình đổi lại).

---

## PHẦN 2 — Quyền ghi (BẮT BUỘC)

**Được ghi:**
- `quantower-entry-signal/RunnerSignal.cs`
- `quantower-entry-signal/dist/RunnerSignal.dll` (do `./build-runner.sh` sinh ra)
- `quantower-entry-signal/research/wyckoff/v8/runner/**` (thư mục mới, của riêng bạn)
- `quantower-entry-signal/research/wyckoff/v8/runner/RESULTS_RUNNER_ZONES.md` (báo cáo của bạn)

**READ-ONLY tuyệt đối:**
- `quantower-entry-signal/EntrySignal.cs`, `WyckoffRunner.cs`
- `quantower-tpo-suite/**` (kể cả `ProfileEngine.cs`, `SessionZones.cs`)
- `research/wyckoff/cbr_v6.py`, `research/wyckoff/v8/zones_corven.py`, `research/entry_dxfeed.py`,
  `research/imp_reversal_sweep.py`, `research/entry_month.py`, `research/wyckoff/v7/**`
- mọi file `.md` ngoài RESULTS của bạn

`cbr_v6.py` là nền chung với session 3 → **không sửa**. Cách làm đúng: **copy** sang
`v8/runner/cbr_hvn.py`, chứng minh bản copy tái lập **đúng** số gốc (xem P0 GOLDEN), **rồi mới** sửa bản
copy. Phát hiện bug trong file dùng chung thì ghi vào RESULTS mục "bug ở file dùng chung", đừng tự sửa.

**Git — 3 session dùng chung MỘT thư mục làm việc và chung nhánh `main`:**
- **Không** tạo nhánh, **không** `git checkout` sang nhánh khác. Cả 3 session chia sẻ cùng một working
  tree — đổi nhánh là đổi file dưới chân 2 session kia.
- Chỉ `git add` **đúng những file của bạn**. **Tuyệt đối không `git add -A` / `git add .`** (sẽ nuốt việc
  đang dở của session khác).
- Trước khi push: `git pull --rebase --autostash origin main` rồi `git push origin main`.
  (`--autostash` để không fail vì session khác đang có file dở dang.)
- Gặp `index.lock` hoặc push bị từ chối → **chờ vài giây, thử lại một lần**. Vẫn lỗi thì báo người học,
  đừng dùng `--force`, đừng `git reset`.
- Cuối **mỗi lượt có sửa file**: `git status` → add (chọn lọc) → commit (message tiếng Việt) → pull
  --rebase --autostash → push → **báo hash + kết quả push**.

---

## PHẦN 3 — Việc phải làm, chia pha có ĐIỂM DỪNG

Sau mỗi pha: in bảng số → **dừng, báo người học, chờ xác nhận** → mới đi pha sau. Không gộp pha.

### P0 — GOLDEN + đo cột "TRƯỚC"
1. **GOLDEN:** chạy `cbr_v6.py` ở cấu hình v5 và tái lập số tham chiếu trong `BASELINE.md §1`. Copy sang
   `v8/runner/cbr_hvn.py`, chạy lại, **phải ra y hệt từng con số**. Chưa khớp thì chưa được sửa gì.
2. Đo cột **TRƯỚC** cho **cả hai nhánh riêng** (CBR và QUAY ĐẦU) + gộp, bằng chính harness sẽ dùng để
   đo cột SAU. **Không** lấy số trong BASELINE.md / memory / chat cũ làm cột TRƯỚC — số cũ đo bằng
   pipeline khác, cột Δ sẽ vô nghĩa.
3. **Nguồn dữ liệu:** dùng `dxFeed` (bộ chính, `entry_dxfeed.load_m1()`, 3 tháng thanh khoản 5-7/2026).
   Không dùng `fp-m1-6-month.csv` cho bất cứ thứ gì liên quan volume/HVN: cột Volume **hỏng 04/06→26/06**
   (BASELINE §8). Ghi rõ nguồn + cửa sổ vào bảng.
4. ⚠ **Múi giờ:** `b['dt']` của dxFeed là **UTC**. Đây là cái bẫy đã làm sai một lần rồi (lọc khung chết
   v5 vô hiệu vì đem giờ UTC so với giờ VN). Mọi lọc theo giờ phải nói rõ đang neo múi giờ nào.
5. `volfloor`: dùng hằng **`VOLFLOOR_FROZEN=20.0`**, **không** gọi `calc_volfloor()` (percentile-30 nhìn
   trước = look-ahead, đã sửa 2026-07-29 — đừng tái phát).

### P1 — Kiểm zone provider CORVEN trước khi tin nó
`v8/zones_corven.py` đã có `group_days`, `group_weeks`, `vwap_series`, `hvn_of`, `build_zone_series(B,
mode='week'|'day', causal='closed'|'running')`, `zone_lookup_series`.

- Chạy nó, xem output. **In 13 mốc tuần** của 5-7/2026, tự kiểm bằng mắt (DST Mỹ làm giờ nghỉ CME dịch
  21h↔22h UTC — mốc tuần dễ lệch 1 giờ).
- In số vùng/tuần, số vùng/ngày. Quá nhiều (>6/khung) hay quá ít (<1) = ngưỡng `min_ratio` sai → sweep
  `{1.3, 1.5, 1.8}`, chọn theo **cao nguyên** không theo mũi nhọn.
- **Kiểm nhân quả:** cắt chuỗi ở thời điểm t, tính lại vùng, so với vùng tính từ chuỗi đầy đủ — phải
  trùng khít. Không trùng = look-ahead → dừng, báo, không đo tiếp.

### P2 — PLAY2: đổi neo của CBR từ range co hẹp sang mép HVN
Đây là thay đổi cơ chế lớn nhất của session này.

- Trong `v8/runner/cbr_hvn.py`: thay điều kiện "range = `RangeLen` nến trước có span ≤ `RangeMaxPts`"
  bằng "**cạnh = mép HVN**" (tuần cho tầng KB-A, ngày cho tầng KB-B), giữ **nguyên** phần còn lại của
  chuỗi phá → hồi `PullMin..PullMax` → nến tiếp diễn → SL/TP.
- Đo **3 biến thể riêng**, đừng gộp: `HVN tuần` · `HVN ngày` · `range nội bộ (TRƯỚC)`.
- Bề rộng vùng HVN: HVN là **một dải**, không phải một mức. Định nghĩa mép rõ ràng và sweep dung sai
  `{8, 12, 20}` tick. Ghi định nghĩa vào RESULTS — người đọc sau phải tái lập được.
- Giả thuyết kiểm được của người học: **tầng tuần cho WR cao hơn tầng ngày**. Nếu đo ra **ngược** thì
  báo thẳng, đừng im lặng chọn cái đẹp hơn.

### P3 — PLAY1: nhánh QUAY ĐẦU thêm HVN tuần/ngày + VWAP tuần
- Hiện chỉ fade tại **VWAP phiên**. Thêm các vùng CORVEN vào tập vùng được fade, đo **từng loại vùng
  riêng** (VWAP phiên / VWAP ngày / VWAP tuần / HVN ngày / HVN tuần) rồi mới gộp.
- ⚠ Đã có kết quả đo trước (2026-07-31): gắn nhánh quay đầu vào vùng của `M30SessionZones` làm **n tăng
  ×2.4 nhưng EV sụp về 0**, và đối chứng ngẫu nhiên **bác bỏ** — vị trí vùng không mang thông tin cho
  lệnh quay đầu. Lần này khác ở chỗ **đổi loại vùng** (HVN/VWAP tuần thay vì vùng theo phiên), nên đáng
  đo lại; nhưng **kỳ vọng tiên nghiệm là xấu**. Nếu lại ra kết quả tương tự thì đó là **xác nhận độc
  lập**, không phải thất bại — báo và đóng nhánh.
- Giữ gate **R2** (vùng bị chạm phải ở 25% biên của range gần) và **R10** (phải có nến từ chối **có**
  volume; cấm dùng "volume thấp" làm tín hiệu đảo).
- **RR:** người học chốt RR 1:3 cho mọi kịch bản, nhưng repo đã đo **MFE trần của lệnh đảo chiều ≈ 1.3R**
  → RR1.5 mới được chọn. **Không tranh luận — đo:** in phân phối MFE theo R cho tập PLAY1 neo HVN
  (`P(MFE≥1.5R)`, `≥2R`, `≥3R`, `≥4R`). `P(≥3R) ≥ 35%` → RR3 khả thi. `< 20%` → **báo lại kèm số**,
  đề xuất giữ RR1.5 cho PLAY1, **không tự đổi spec**.

### P4 — Nến xác nhận M1 (CORVEN_SPEC §1: bắt buộc, không vào khi giá vừa chạm)
Định nghĩa đề xuất cho LONG (SHORT gương lại): `close > open` **và** `cpos ≥ 0.60` **và** thân ≥ 30%
range **và** râu ngược ≤ 35% range. **A/B `ConfirmOn ∈ {false, true}`** — bật mà EV không tăng thì nó chỉ
là bộ lọc giảm n, phải biết bằng số chứ không giữ vì "pro trader nói vậy".

### P5 — Đối chứng ngẫu nhiên (BẮT BUỘC, không có thì mọi kết luận vô giá trị)
Dịch mọi vùng **±3 giá**, giữ nguyên toàn bộ logic còn lại, **5 seed**, in EV trung bình bản ngẫu nhiên.
- `EV(thật) − EV(ngẫu nhiên) ≥ +0.25R` → đi tiếp.
- `< +0.10R` → **KILL** nhánh đó: vị trí vùng không mang thông tin. Báo và dừng. Đây là kết quả hợp lệ.

### P6 — Chi phí giao dịch
Quét phí `0 → 8 tick/lượt`. EV phải còn dương ở **≥ 4 tick**. Chết ở ≤2 tick = KILL.

### P7 — Port sang C# `RunnerSignal.cs` (chỉ làm nếu P5 và P6 qua)
- Thêm input `CorvenZoneAnchor` (bool, **mặc định `false`**) và `CorvenZoneTier` (tuần / ngày). Tắt =
  hành vi v5 y nguyên, **không lệch một tín hiệu nào**.
- **Không xoá** `BuildPool` cũ, không đổi mặc định nào đang chạy live, không đổi `DeadUseUtc=true`.
- Dùng `ProfileEngine.FindHvn` / `RowsOver` / `VwapAt` / `WeekSpans` (đã có, chỉ **đọc**).
- Build: `cd quantower-entry-signal && ./build-runner.sh` — phải **0 warning 0 error**.
- **Parity 2 chiều:** (a) cờ TẮT → C# ra đúng danh sách tín hiệu như v5 hiện tại (chứng minh không hồi
  quy); (b) cờ BẬT → khớp ≥95% với Python. Lệch thì truy tới khớp.

---

## PHẦN 4 — Vòng loop test → cải thiện (luật của vòng lặp)

Lặp: **đo → đổi ĐÚNG MỘT thứ → đo lại → giữ/bỏ**.

- **Hạn mức 10 cấu hình** cho signal này. Đếm và báo. Vượt = đang dò tìm, không phải nghiên cứu.
- **Cao nguyên, không mũi nhọn:** tham số thắng phải có láng giềng cũng thắng.
- **Không nới gate để tăng số lệnh.** Bài học 2026-07-31: n tăng ×2.4 mà EV về 0 là **thất bại**.
- Mỗi vòng ghi 1 dòng vào bảng lịch sử trong RESULTS: đổi gì → n/WR/EV/MDD → giữ hay bỏ → vì sao.
- Ngưỡng đọc (PLAN §6.2): `n≥25` mới nói được gì; `n<15` KILL; `15≤n<24` = **"không kết luận"**, không
  ship. Đọc WR theo đúng RR đang dùng (RR3 hoà vốn ở 25%; RR1.5 hoà vốn ở 40%).
- **Quy tắc DỪNG:** WR nhảy >10 điểm **hoặc** n tụt >40% → dừng soi cơ chế trước khi giữ. Nhảy vọt trên
  n nhỏ gần như luôn là nhiễu.

---

## PHẦN 5 — Bảng cuối (deliverable chính)

Kết thúc, in bảng này **trong chat** và lưu vào `v8/runner/RESULTS_RUNNER_ZONES.md`. Làm **3 bảng**:
`CBR/PLAY2`, `QUAY ĐẦU/PLAY1`, `gộp portfolio` — cùng khuôn:

```
| Thông số | TRƯỚC (tự đo P0) | SAU (vùng CORVEN) | Δ |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ |  |  | (phải giống nhau) |
| Neo vùng |  range co hẹp M1 | HVN tuần / ngày |  |
| n (số lệnh) |  |  |  |
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
| Số cấu hình đã thử |  |  | /10 |
| KẾT LUẬN | — | PASS / KILL / không kết luận |  |
```

Cột Δ: ghi dấu (`+`/`−`) và **thêm mũi tên nghĩa** khi dấu không tự nói (MDD giảm là **tốt** → `−2.0R ↑`).
Ô nào không đo được thì ghi `—` kèm lý do một dòng, **không bỏ trống, không bịa**.

Kèm sau bảng, ngắn gọn:
1. Bảng lịch sử vòng lặp (đổi gì → kết quả → giữ/bỏ).
2. So sánh **tầng tuần vs tầng ngày** (giả thuyết "tuần WR cao hơn" đúng hay sai trên dữ liệu này).
3. Cái gì **không** đo được và vì sao.
4. Một câu trả lời thẳng: **có nên chuyển bản live sang neo vùng CORVEN không, hay chưa đủ bằng chứng?**
   Kèm 1 câu về việc mặc định live đã được giữ nguyên.

---

## PHẦN 6 — Luật trung thực (đọc lại trước khi viết bảng cuối)

- **Không tuyên bố cải thiện khi chưa có đối chứng ngẫu nhiên.** "Đúng ý pro trader hơn" ≠ "tốt hơn".
- **n nhỏ thì nói n nhỏ.** Cửa sổ 5-7/2026 là **một** regime (vàng tạo đỉnh), **một** hợp đồng, **không
  có điểm out-of-sample nào** (BASELINE §0). GCQ26 vừa qua First Notice Day 31/07 → dữ liệu đang xấu dần,
  OOS thật cần GCZ26/continuous. Nhắc 1 câu, không diễn giải dài.
- **Kết quả âm là kết quả tốt.** Nếu vùng CORVEN làm signal tệ hơn, báo thẳng kèm số. Đừng đi tìm cấu
  hình thứ 11 để cứu một kết luận.
- Đọc số thật trước, giải thích sau. Không in giả thuyết kèm bảng.
- Tách LONG/SHORT ở mọi bảng.
- **Bản live là bất khả xâm phạm về mặc định.** Nếu cuối cùng bạn tin cách mới tốt hơn, hãy **đề xuất**
  kèm số, để người học tự bật cờ.
