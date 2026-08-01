# SESSION 1 — EntrySignal (M1): đổi tầng vùng sang bộ vùng CORVEN

Bạn đang làm việc trong repo `/home/asl86/Documents/footprint-tpo`. Đây là một **phiên nghiên cứu +
code**, không phải phiên dạy học. Trả lời tiếng Việt, ngắn gọn theo CLAUDE.md.

**Có 2 session Claude khác đang chạy song song trên cùng repo này** (một lo `RunnerSignal.cs`, một lo
`WyckoffRunner.cs`). Quyền ghi ở PHẦN 2 là **bắt buộc**, vượt quyền là phá việc của session khác.

---

## PHẦN 0 — Đọc trước, im lặng (đừng vừa đọc vừa giảng)

Đọc hết những file này bằng tool call liên tiếp, chỉ báo ngắn "đang đọc tài liệu", **chưa** kết luận gì:

1. `CLAUDE.md` — luật trả lời ngắn + luật commit/push
2. `data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md` — **BẢN CHỐT** về vùng. Đọc kỹ §2 và §3.
3. `quantower-entry-signal/PLAN_KB_ABC.md` — plan tổng. Đọc kỹ §2 (bốn chặn), §4, §6 (PASS/KILL).
4. `quantower-entry-signal/research/wyckoff/BASELINE.md` — §0 (cảnh báo không có OOS) và §6 (giới hạn).
5. `quantower-entry-signal/research/wyckoff/AUDIT_V7.md` — kỷ luật đo, đặc biệt luật "n<25 = không kết luận".
6. `quantower-entry-signal/research/DATA_CAPABILITY.md` — **§4 là bắt buộc**: giải thích vì sao cùng một
   chuỗi giá mà WR ra 61% ở `fp-m1` và 42% ở `dxFeed` (nguyên nhân là **zone-pool "lạnh" ở đầu kỳ**,
   không phải dữ liệu khác nhau). Bạn sắp đổi đúng cái zone-pool đó → cái bẫy này áp trực tiếp vào bạn.
7. `quantower-tpo-suite/BACKTEST-ZONES-V2.md` — bài học 2026-07-31: bộ vùng "cải tiến" đo ra **không hơn
   ngẫu nhiên**. Đọc để biết mức bằng chứng cần có trước khi tuyên bố cải thiện.
8. `quantower-entry-signal/EntrySignal.cs` — file bạn sở hữu.
9. `quantower-entry-signal/research/entry_month.py` — harness backtest của signal này.
10. `quantower-entry-signal/research/wyckoff/v8/zones_corven.py` — zone provider CORVEN đã có (READ-ONLY).

---

## PHẦN 1 — Bối cảnh: vì sao phải đổi

CORVEN (pro trader người học nói chuyện trực tiếp) đã chốt: anh ấy **chỉ** dùng **HVN tuần, HVN ngày,
VWAP tuần (neo đầu tuần), VWAP ngày**. Và **không** dùng POC / VAH / VAL — càng không dùng
VAH/VAL/POC **theo từng phiên Á-Âu-Mỹ** (nguyên văn: *"tất nhiên là không rồi"*).

`EntrySignal.cs` hiện dựng pool vùng gồm:

| Vùng đang dùng | Điểm | CORVEN có dùng? |
|---|---:|---|
| POC theo phiên Á/Âu/Mỹ | 70 | ❌ |
| VAH theo phiên | 58 | ❌ |
| VAL theo phiên | 58 | ❌ |
| D-1 POC | 72 | ❌ |
| D-1 VAH / VAL | 66 | ❌ |
| VWAP (phiên, động) | 64 | ✅ (nhưng CORVEN dùng VWAP **ngày** và **tuần**) |
| HVN tuần / HVN ngày | — | ✅ **đang thiếu hoàn toàn** |

⇒ Signal này đang **gate cứng** (`MinConfluence = 2`) trên đúng những vùng CORVEN nói không dùng. Đây là
signal bị ảnh hưởng **nặng nhất** trong 3 signal, vì với nó vùng không phải hiển thị — vùng **là** edge.

Cấu hình đang ship (đọc lại từ code, đừng tin số ở đây nếu lệch): `MinConfluence=2`, `ConfluenceTol=7`
tick, `ZoneExpireDays=3`, `ArmDistTicks=20`, `RetestBars=12`, `SlFloor=4.0`, `SlCap=6.0`, `RR=1.5`,
`LookbackSessions=0`.

---

## PHẦN 2 — Quyền ghi (BẮT BUỘC)

**Được ghi:**
- `quantower-entry-signal/EntrySignal.cs`
- `quantower-entry-signal/dist/EntrySignal.dll` (do `./build-entry.sh` sinh ra)
- `quantower-entry-signal/research/wyckoff/v8/entry/**` (thư mục mới, của riêng bạn)
- `quantower-entry-signal/research/wyckoff/v8/entry/RESULTS_ENTRY_ZONES.md` (báo cáo của bạn)

**READ-ONLY tuyệt đối** (session khác đang dùng, hoặc là nền chung):
- `quantower-entry-signal/RunnerSignal.cs`, `WyckoffRunner.cs`
- `quantower-tpo-suite/**` (kể cả `ProfileEngine.cs`, `SessionZones.cs`)
- `research/wyckoff/v8/zones_corven.py`, `research/wyckoff/cbr_v6.py`, `research/entry_month.py`,
  `research/entry_dxfeed.py`, `research/imp_reversal_sweep.py`, `research/wyckoff/v7/**`
- mọi file `.md` ngoài RESULTS của bạn

Cần sửa một file READ-ONLY? **Không sửa.** Viết wrapper/bản sao trong `v8/entry/` và ghi lý do vào
RESULTS. Nếu phát hiện **bug thật** trong file dùng chung thì ghi vào RESULTS mục "bug phát hiện ở file
dùng chung" để người học xử lý sau, đừng tự sửa.

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

### P0 — Đo cột "TRƯỚC" bằng chính harness sẽ dùng để đo "SAU"
Đây là pha quan trọng nhất và dễ làm sai nhất.

- Viết `v8/entry/harness.py`: gọi `entry_month.load_m1()` → `build_zones(B)` → `run(B, pool)` →
  `dedup` → đánh giá, in đủ các dòng của bảng ở PHẦN 5.
- **Chạy trên đúng một nguồn dữ liệu và ghi rõ nguồn nào.** Đề xuất `dxFeed` (bộ chính, 3 tháng thanh
  khoản 5-7/2026) vì `fp-m1-6-month.csv` có **cột Volume hỏng 04/06→26/06** (BASELINE §8) — mọi feature
  volume, kể cả HVN, sai trong khoảng đó. Nếu bạn chọn `fp-m1` thì **phải** lọc bỏ vùng hỏng và nói rõ.
- ⚠ **Warm-up zone-pool:** DATA_CAPABILITY §4 chỉ ra pool "lạnh" ở đầu kỳ tạo WR ảo. Bỏ N ngày đầu
  (đề xuất 5 ngày, ghi rõ số đã bỏ) và áp **cùng** một quy tắc warm-up cho cả TRƯỚC và SAU.
- Kết quả P0 = cột TRƯỚC. **Không** lấy số trong BASELINE.md / memory / chat cũ làm cột TRƯỚC.
- Đối chiếu: số bạn đo có gần con số đã ghi ở tài liệu cũ không? Lệch nhiều thì **truy nguyên nhân và
  báo**, đừng lặng lẽ đi tiếp.

### P1 — Kiểm zone provider CORVEN trước khi tin nó
`v8/zones_corven.py` đã có `group_days`, `group_weeks`, `vwap_series`, `hvn_of`,
`build_zone_series(B, mode='week'|'day', causal='closed'|'running')`, `zone_lookup_series`.

- Chạy `python3 quantower-entry-signal/research/wyckoff/v8/zones_corven.py` xem output hiện có.
- **In 13 mốc tuần** của 5-7/2026 và tự kiểm bằng mắt (DST của Mỹ làm giờ nghỉ CME dịch 21h↔22h UTC).
- In số vùng/tuần và số vùng/ngày. Vùng quá nhiều (>6/khung) hay quá ít (<1) đều là dấu hiệu ngưỡng
  `min_ratio` của `hvn_of` sai — sweep `{1.3, 1.5, 1.8}` và chọn theo **cao nguyên**, không theo mũi nhọn.
- **Kiểm nhân quả:** chứng minh vùng tại thời điểm t không dùng dữ liệu sau t. Cách kiểm: cắt chuỗi ở t,
  tính lại, so vùng — phải trùng khít. Nếu không trùng thì có look-ahead → dừng, báo, không đo tiếp.

### P2 — Thay pool trong harness Python (chưa đụng C#)
- `v8/entry/pool_corven.py`: xuất pool chỉ gồm **HVN tuần · HVN ngày · VWAP tuần · VWAP ngày**, đúng
  interface mà `entry_month.run(B, pool)` mong đợi (`price`, `kind`, `ready`, `expire`, `strength`).
- **Vấn đề cấu trúc phải xử lý, không được lờ:** `MinConfluence=2` sinh ra từ pool 7 loại vùng. Pool mới
  chỉ có 4 loại → số vùng chồng nhau ít hơn nhiều → tín hiệu có thể sụt gần hết. Cách xử lý:
  - Định nghĩa lại "hợp lưu" = **các khung đồng ý** (HVN tuần + HVN ngày + VWAP trong `ConfluenceTol`),
    đúng tinh thần "hợp lưu đa khung" đã làm ở `SessionZones` v2.
  - **A/B `MinConfluence ∈ {1, 2}`** và báo cả hai. Nếu phải hạ về 1 mới có lệnh thì **nói thẳng** rằng
    lớp gate hợp lưu đã mất, đó là mất mát chứ không phải đơn giản hoá.
- Chạy lại harness → ra cột SAU (bản v0).

### P3 — Hai play tại vùng (CORVEN_SPEC §3)
EntrySignal đã có 2 kịch bản "phá&hồi" và "chạm&đảo" — đúng là PLAY2 và PLAY1 của CORVEN, chỉ **neo sai
vùng**. Sau P2 chúng đã neo đúng. Việc ở pha này:
- Thêm **nến xác nhận M1** (CORVEN_SPEC §1: bắt buộc, không vào khi giá vừa chạm). Định nghĩa đề xuất
  cho LONG (SHORT gương lại): `close > open` **và** `cpos ≥ 0.60` **và** thân ≥ 30% range **và** râu
  ngược ≤ 35% range. **A/B `ConfirmOn ∈ {false, true}`** — bật mà EV không tăng thì nó chỉ là bộ lọc
  giảm n, phải biết bằng số.
- Tách bảng **PLAY1 riêng / PLAY2 riêng / gộp**. Rất có thể một play sống một play chết.
- A/B `causal ∈ {closed, running}` cho cả vùng tuần và vùng ngày.

### P4 — Đối chứng ngẫu nhiên (BẮT BUỘC, không có thì mọi kết luận vô giá trị)
Dịch mọi vùng đi **±3 giá** (giữ nguyên toàn bộ logic còn lại), chạy **5 seed**, in EV trung bình của
bản ngẫu nhiên. Bài học `BACKTEST-ZONES-V2.md`: bộ vùng nghe rất hợp lý mà đo ra không hơn ngẫu nhiên.
- `EV(thật) − EV(ngẫu nhiên) ≥ +0.25R` → đi tiếp.
- `< +0.10R` → **KILL**: kết luận là vị trí vùng không mang thông tin cho signal này. Báo và dừng, không
  đi P5. Đây là kết quả hợp lệ, không phải thất bại của bạn.

### P5 — Chi phí giao dịch
Quét phí `0 → 8 tick/lượt`. EV phải còn dương ở **≥ 4 tick**. Chết ở ≤2 tick = KILL.

### P6 — Port sang C# `EntrySignal.cs` (chỉ làm nếu P4 và P5 qua)
- Thêm input `CorvenZones` (bool, **mặc định `false`**) — bật thì dùng pool CORVEN, tắt thì y nguyên hành
  vi hiện tại. **Không xoá code pool cũ** (còn cần để đối chiếu, và bản live đang chạy trên nó).
- HVN tuần/ngày trong C#: dùng `ProfileEngine.FindHvn` / `RowsOver` / `VwapAt` / `WeekSpans` (đã có, chỉ
  **đọc**, không sửa `ProfileEngine.cs`).
- Build: `cd quantower-entry-signal && ./build-entry.sh` — phải **0 warning 0 error**.
- **Parity harness:** so danh sách tín hiệu C# vs Python trên cùng cửa sổ, mục tiêu ≥95% lệnh khớp. Lệch
  thì truy tới khớp, đừng "gần đúng là được".

---

## PHẦN 4 — Vòng loop test → cải thiện (luật của vòng lặp)

Sau khi có bản v0 chạy được, lặp: **đo → đổi ĐÚNG MỘT thứ → đo lại → giữ/bỏ**.

- **Hạn mức 10 cấu hình** cho signal này. Đếm và báo số đã dùng. Vượt 10 thì đang dò tìm chứ không phải
  nghiên cứu — theo Bonferroni, p phải < 0.005 mới coi là thật.
- **Cao nguyên, không mũi nhọn:** tham số thắng phải có láng giềng cũng thắng. Thắng đơn độc = nhiễu.
- **Không nới gate để tăng số lệnh.** Bài học 2026-07-31: n tăng ×2.4 mà EV về 0 là **thất bại**.
- Mỗi vòng ghi 1 dòng vào bảng lịch sử trong RESULTS: đổi gì → n/WR/EV/MDD → giữ hay bỏ → vì sao.
- Ngưỡng đọc kết quả (PLAN §6.2): `n≥25` mới nói được gì; `n<15` KILL; `15≤n<24` = **"không kết luận"**,
  không được ship. WR@RR1.5 và EV phải đọc theo RR thật bạn dùng, đừng so với ngưỡng của RR3.
- **Quy tắc DỪNG:** nếu một thay đổi làm WR nhảy >10 điểm **hoặc** n tụt >40%, dừng lại soi cơ chế trước
  khi giữ nó. Nhảy vọt trên n nhỏ gần như luôn là nhiễu.

---

## PHẦN 5 — Bảng cuối (deliverable chính)

Kết thúc, in bảng này **trong chat** và lưu vào `v8/entry/RESULTS_ENTRY_ZONES.md`:

```
| Thông số | TRƯỚC (tự đo P0) | SAU (vùng CORVEN) | Δ |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ |  |  | (phải giống nhau) |
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
| PLAY1 chạm-đảo: n / EV |  |  |  |
| PLAY2 phá-hồi: n / EV |  |  |  |
| EV − EV(ngẫu nhiên, 5 seed) |  |  |  |
| EV @ phí 2 tick |  |  |  |
| EV @ phí 4 tick |  |  |  |
| Số cấu hình đã thử |  |  | /10 |
| KẾT LUẬN | — | PASS / KILL / không kết luận |  |
```

Cột Δ: ghi dấu (`+`/`−`) và **thêm mũi tên nghĩa** khi dấu không tự nói (MDD giảm là **tốt** → `−2.0R ↑`).
Ô nào không đo được thì ghi `—` kèm lý do một dòng, **không bỏ trống, không bịa**.

Kèm sau bảng, ngắn gọn:
1. Bảng lịch sử vòng lặp (đổi gì → kết quả → giữ/bỏ).
2. Cái gì **không** đo được và vì sao.
3. Một câu trả lời thẳng: **bộ vùng CORVEN có làm signal này tốt hơn không, hay chưa chứng minh được?**

---

## PHẦN 6 — Luật trung thực (đọc lại trước khi viết bảng cuối)

- **Không tuyên bố cải thiện khi chưa có đối chứng ngẫu nhiên.** "Đúng ý pro trader hơn" ≠ "tốt hơn".
- **n nhỏ thì nói n nhỏ.** Cửa sổ 5-7/2026 là **một** regime (vàng tạo đỉnh), **một** hợp đồng, **không
  có điểm out-of-sample nào** (BASELINE §0). Mọi kết luận phải kèm cảnh báo đó — 1 câu là đủ.
- **Kết quả âm là kết quả tốt.** Nếu vùng CORVEN làm signal tệ hơn, báo thẳng kèm số. Đừng đi tìm cấu
  hình thứ 11 để cứu một kết luận.
- Đọc số thật trước, giải thích sau. Không in giả thuyết kèm bảng.
- Tách LONG/SHORT ở mọi bảng (thiếu sót cố hữu của các báo cáo trước).
- Không sửa số cũ trong tài liệu khác cho khớp số mới của bạn — ghi vào RESULTS của bạn.
