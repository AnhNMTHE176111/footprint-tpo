# Benzo Trader v2 — MỘT setup "follow theo footprint" của CORVEN (Fable, 2026-11-09)

> Bỏ hẳn 4 setup A/B/C/D (đo 65 phiên: không setup nào có lợi thế, `research/report/TONG-KET-VONG-1-2.md`).
> Thay bằng **một** setup = checklist 4 bước ①②③④ + ⛔ của `plans/CUU-AM-CHAN-KINH-plan.md` mục 2b, cơ khí hoá
> theo đúng giải thích ở `cuu-am-chan-kinh/chi-tiet.html`. Fable quyết mọi con số; Opus làm Python → đo → port C# → test.
> **Nguyên tắc trung thực:** chỗ nào CORVEN nói bằng mắt mà không đo được thì ghi "không code", không nặn số cho có.

## 0. Căn cứ số (đo 2026-11-09 trên `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, 62 phiên dày, 82.390 nến M1)
| Đại lượng | Số đo | Dùng để chốt |
|---|---|---|
| mbr = trung vị (high−low) 100 nến | **1,5 giá** (biên độ nến p25/50/75/90 = 1,0/1,6/2,4/3,5) | mọi ngưỡng khoảng cách tính theo mbr, như Range Box |
| thân/biên độ nến | p25/50/75 = 0,27/0,50/0,74 | nến xác nhận: thân ≥ 0,4 biên độ (≈ p40) |
| nến tăng: (high−close)/biên độ | p50 0,20 · p75 0,39 | "đóng sát cực trị" = ≤ 0,3 biên độ |
| \|Δ\| / trung vị \|Δ\| 50 nến | ≥ 2× ở 26 % nến · ≥ 3× ở 14 % | delta "to" = ≥ 2× |
| ô Bid/Ask lớn nhất nến / nền (trung vị của "trung vị 3 ô to nhất mỗi nến", 100 nến) | ≥ 3× ở 17 % nến · ≥ 4× ở 10 % · ô p90 = 9 hợp đồng | "bóng" = ≥ 3× nền VÀ ≥ 10 hợp đồng |
| stacked ≥ 3 mức, 250 % (định nghĩa CORVEN) | có ở **32 %** nến (≥ 4 mức: 16 %) | stacked quá phổ biến ⇒ chỉ tính khi "mới + giữa thân + giá đi tiếp" (mục 1.③d) |
| kiệt sức "nhỏ" có râu (ExhaustionLogic mặc định) | ≈ 9 % nến mỗi phía | giữ nguyên định nghĩa đã có |
| `max_one_trade` | = 0 ở 100 % nến | **không** có dấu hiệu nào dựa lệnh đơn |
| Range Box (MEASURE.md) | 19–20 range/ngày; cao trung vị 36–38 tick ≈ 2,1 mbr; fail break ≈ 2/range; vào máy móc ngay fail break = −0,2R sau phí | thế A phải thêm ③ mới có cơ hội khác 0 |
| Hộp CORVEN (`corven_boxes.csv`) | retest sau phá: râu vào hộp 3–11 tick (B09/B13/B16/B17) ≈ 0,2–0,7 mbr; cú thủng fail break 8–13 tick | "gần" = 1,0 mbr; đệm SL 3 tick |

## 1. ĐỊNH NGHĨA MÁY MÓC

Ký hiệu: `tick` = 0,1 (GC/MGC); `mbr` như trên; `tol` = max(2 tick, 0,5 mbr) (= Range Box); `medΔ` = trung vị |Δ| 50 nến;
`nền_ô` = trung vị 100 nến của (trung vị 3 ô side-volume lớn nhất mỗi nến), side-volume = max(bid, ask) của ô. Mọi thứ chỉ xét **nến đã đóng**.

### ① Bối cảnh
**1a. Range** = `RangeLogic.cs` / `range_proto.py` nguyên trạng (MinBars 8 · Hmin 1,6 mbr · Hmax 6 mbr · tol 0,5 mbr · K 3 · G 30 · PivotRule A · MaxReEntry 2). Không đổi tham số nào (đã quét, MEASURE.md).
- **Trong range** = range ở trạng thái ACTIVE (hoặc PENDING chưa đủ K nến).
- **Đã phá, giữ được** = sự kiện `BreakConfirmed` (đóng ngoài rồi K=3 nến không đóng lại trong) — đúng câu "chờ 1–2 cây xem giữ được không" (0:08:46) và "phá thì phải giữ được" (0:43:53). Range ở BROKEN tối đa G=30 nến.
- **Range M15 "rối thì lên M15": KHÔNG làm ở v1.** Lý do: (i) CORVEN nói trong range lớn vẫn đánh theo range M1 (1:08:40) và range lớn "chỉ để đánh dài" (1:08:57) — setup scalp M1 này dùng range M1; (ii) ngưỡng theo mbr đã kiểm là dùng chung được M1/M5/M15 (MEASURE.md kết luận 4) nên khi cần chỉ việc chạy cùng engine trên nến M15 gộp từ M1 — để v2, sau khi v1 có số. Ghi 1 dòng trong README.

**1b. Hai thế** (chỉ hai, không có thế thứ ba):
- **Thế A** — range ACTIVE, vừa có `FailBreak` ở cạnh E (đóng ngoài rồi đóng lại trong trong ≤ K nến). Hướng = vào lòng range, mục tiêu cạnh đối diện.
- **Thế B** — range BROKEN theo hướng D (`BreakConfirmed`), chưa `ReEntry`, tuổi ≤ 30 nến kể từ nến đóng ngoài. Hướng = D. Mốc = cạnh vừa phá hoặc stacked mới cùng hướng D hình thành trong cú đẩy.
- Không có range ACTIVE/BROKEN ⇒ không có tín hiệu (= "không follow giữa lòng range", và "trend không có range thì không vẽ" BRAINSTORM #12). **Không code "phá cấu trúc không có range"** — không có mốc/mục tiêu đo được, và cả 3 ví dụ có số của CORVEN đều dựa range.

**1c. Cấu trúc gần nhất chưa gãy ngược** (0:18:39, 0:42:23 "một nến là đủ"):
- Thế B hướng D: kể từ nến đóng ngoài, lấy pivot 1 nến (luật Range Box) ngược hướng D gần nhất (sell: pivot đỉnh gần nhất sau khi phá). Nếu có nến **đóng** vượt pivot đó ngược hướng D ⇒ thế B huỷ cho tới khi có cú đẩy mới lập cực trị mới. (ReEntry đã huỷ thế B rồi; luật này bắt thêm ca cấu trúc gãy mà chưa đóng vào range.)
- Thế A: cấu trúc = chính range; fail break không phải gãy (chi-tiet 1.3 ngoại lệ). Không xét thêm.

### ② Mốc — "gần" và "không quá sâu"
**2a. Mốc hợp lệ và "gần":**
| Thế | Mốc | Điều kiện "gần" (giá đang ở mốc) |
|---|---|---|
| A | cạnh E vừa fail break | nến xác nhận (CF) đóng **trong** [bottom, top] và cách E ≤ **1,0 mbr** (ví dụ 1: vào ≈ cạnh trên). Đóng sâu hơn vào lòng range ⇒ không vào (R:R tự giảm, và "giữa lòng range không có chỗ đặt SL"). |
| B | cạnh vừa phá | trong cửa sổ test (mục 2c) có nến mà râu chạm dải [E − tol, E + tol] **và** CF đóng cách E ≤ 1,0 mbr về phía D (ví dụ 2: vào 4126,6 với cạnh 4127,4 = 0,5 mbr). |
| B | stacked mới cùng hướng D | vùng stacked (250 %, ≥ 3 mức) hình thành **sau** nến đóng ngoài, tuổi ≤ 30 nến, vị trí Body hoặc râu phía đẩy, **chưa từng bị chạm** trước nhịp test này (CORVEN 0:20:12 "chạm một mớ → vứt"; chế độ `SiEndMode.Touch` của StackedImbalance.cs chính là đếm lần chạm đầu), và chưa `ClosedThrough`. "Gần" = râu nến trong cửa sổ test chạm [Lo − tol, Hi + tol]. |
- Mốc "xa" = không thoả tuổi/khoảng cách trên ⇒ bỏ (0:06:54 "dùng gần thôi"). Không có mốc "đỉnh/đáy vừa gãy" riêng ở v1 (chỉ tồn tại khi có range phá — đã là cạnh vừa phá).
- **Stacked cũ làm mốc KHÔNG tính dấu hiệu** (chi-tiet ③ cách đếm) — code bằng id vùng: vùng dùng làm mốc bị loại khỏi danh sách ③d.

**2b. Test không quá sâu:**
- Thế B: không nến nào trong cửa sổ test đóng lại trong range (= engine không phát `ReEntry`; nếu phát ⇒ thế B chết, range sống lại) và không nến nào đóng xuyên mép xa của vùng stacked làm mốc (`CheckEnd` CloseThrough). Râu xuyên **được phép** (ví dụ 2 râu chạm lại cạnh).
- Thế A: CF phải đóng **trong** range (1:00:02 "phải vào lòng range"). **Ngoại lệ "xác nhận lần 2"** (ví dụ 3, 1:00:09): range đang PENDING/BROKEN hướng −D, nến mới có râu quét qua (≥ 1 tick) cực trị của cú thủng trước rồi đóng cao hơn (sell: thấp hơn) cực trị đó ≥ tol, cùng ≥ 2 dấu hiệu ⇒ cho vào dù chưa đóng trong range; SL sau râu mới. Chỉ 1 lần mỗi cú thủng.

**2c. Cửa sổ test (cũng là cửa sổ "cùng lúc" của ③):**
- Thế A: từ nến đóng ngoài (ref của FailBreak) tới CF, **tối đa 5 nến** (K=3 + 2 nến chờ).
- Thế B: **3 nến** kết thúc tại CF (CF và 2 nến trước), đồng thời phải nằm trong tuổi 30 nến của BROKEN.
- Lý do 3 nến: ví dụ 2 (00:22–00:23 mang phân kỳ + bóng, CF 00:23), ví dụ 3 (trap + kiệt sức cùng 1 nến); CORVEN "những đoạn có nhiều tín hiệu cùng lúc" (1:05:57). Tham số được quét {2,3,4} — mục 3.

### ③ Dấu hiệu — mỗi dấu hiệu có **nến neo**; tính nếu nến neo nằm trong cửa sổ test và cùng phe với hướng vào. Cần **≥ 2 dấu hiệu khác loại**.
Hướng vào S (+1 buy / −1 sell).

**③a. Delta** (một trong hai dạng, tính tối đa 1):
- *Đồng thuận, to-thẳng* (0:35:55 "dương to lên, thẳng lên"): nến neo = CF hoặc nến ngay trước CF, với Δ·S > 0, |Δ| ≥ **2 × medΔ**, và "thẳng" = Δ không đảo trong nến: buy `delta ≥ 0,8 × max_delta`, sell `delta ≤ 0,8 × min_delta` (cột `max_delta/min_delta` có sẵn trong `_bars.csv`; live lấy từ Volume Analysis). Lý do 2×: p75 của tỷ lệ (26 % nến) — "to" phải hiếm hơn một nửa; 3× (14 %) để quét.
- *Ngược giá* (0:31:42; ví dụ 1 và 2): nhịp test = chuỗi 2–8 nến liền đi ngược S tới mốc (sell: giá lên), biên độ nhịp ≥ 1,0 mbr; **tổng Δ của nhịp có dấu ngược chiều giá** (sell: giá lên mà ΣΔ ≤ 0). Nến neo = nến cực trị của nhịp. Không đòi ngưỡng độ lớn (ví dụ 2: −30, −32 là đủ) — chỉ đòi dấu.

**③b. Bóng đúng phe tại mốc** (0:46:03–0:46:13): ô có side-volume phía S (buy: ask, sell: bid) ≥ **3 × nền_ô** và ≥ **10 hợp đồng**, nằm ở **nửa nến phía S** (buy: ô ≤ trung điểm nến) hoặc trong dải mốc ± tol. Nến neo = nến chứa ô. Nền_ô lấy cách tính của OrderFlowBubbles (median trên top-3 ô/nến, 100 nến) nhưng **bỏ MAD/z** — chỉ dùng bội số để Python/C# khớp dễ và người đọc hiểu ("gấp 3 lần ô bình thường"). Lý do 3×: 17 % nến — bóng là "đại diện chính" trên chart CORVEN nên không được quá hiếm; 10 hợp đồng = p90 ô, chặn nến đêm mỏng. Quét {3,4}.

**③c. Phe ngược kiệt sức ở râu** = `ExhaustionLogic.Detect` mặc định (SmallRel 0,10 · Fade 3 mức/0,25 · bắt buộc râu ≥ 1 tick): sell cần kiệt sức **đỉnh** (Ask), buy cần kiệt sức **đáy** (Bid), ở nến trong cửa sổ test, và mức đó **chưa bị râu quét qua** (`IsSwept`, sweepTicks 1) tính tới CF. Nến neo = nến kiệt sức.

**③d. Stacked mới cùng hướng S**: vùng `StackedImbalanceCalc.Detect(250 %, run 3, minVol 1)` phía S, hình thành ở nến trong cửa sổ test, `Position == Body` hoặc râu phía S mà **nến tạo vùng đóng ở phía S của vùng** (buy: close ≥ Hi; CORVEN 0:03:40 "ở đỉnh cũng được nhưng sau đó giá phải đi tiếp"), `Weak == false`. Không tính vùng đang làm mốc (id loại). Nến neo = nến tạo vùng. Vì 32 % nến có stacked, nếu sau GĐ1 dấu hiệu này chiếm > 50 % số lệnh thì nâng run lên 4 (quét {3,4}).

**③e. Trap / stop hunt phe ngược** (0:23:45 "quét qua đỉnh mà nổ bóng thì là stop hunt"; 0:24:34 SL = bóng ngược màu): một nến có râu quét qua **mốc quan trọng** ≥ 1 tick và đóng lại phía S của mốc; mốc quan trọng = cạnh range (thế A: chính cú thủng; thế B: cực trị của cú đẩy hoặc pivot gần nhất ngược S), **và** trong phần râu có ô side-volume phía −S ≥ 3 × nền_ô (bóng ngược màu = SL khớp). Nến neo = nến quét. Trap và kiệt sức trên cùng nến = **2 dấu hiệu** (chi-tiet); trap và ③b khác màu nên không trùng.

Đếm: số loại dấu hiệu ≥ 2 ⇒ qua ③. Reason phải liệt kê từng dấu hiệu kèm số (mục 2 kiến trúc).

### ④ Lệnh
**4a. Nến xác nhận CF** theo S: đóng theo S (close·S > open·S); thân ≥ **0,4** biên độ; khoảng đóng–cực trị phía S ≤ **0,3** biên độ (= "đóng sát cực trị, không rút râu"); biên độ ≥ 0,5 mbr (loại doji); Δ·S ≥ 0 và |Δ| ≥ 0,5 medΔ (⛔ "delta nhỏ" — không đòi to, to là ③a). Thế A: CF phải là nến FailBreak hoặc 1–2 nến sau nó, đều đóng trong range (0:08:46). Vào ở **giá đóng CF**.

**4b. SL** (0:50:25 "đặt dưới cái đáy mới quét", "đặt gần dễ bị quét"):
- Thế A: sau cực trị râu của cú thủng (max/min từ nến đóng ngoài tới CF) ∓ **đệm 3 tick** (= max(3 tick, 0,2 mbr)).
- Thế B mốc cạnh: sau max(cực trị nhịp test, E ± tol) ∓ đệm. Mốc stacked: sau mép xa vùng ∓ đệm (ví dụ 2: SL trên vùng đỏ).
- Sàn rủi ro **1,0 mbr** (nhỏ hơn ⇒ dời SL ra cho đủ, vì "không đặt sát"); trần **4,0 mbr** (≈ 6 giá) ⇒ bỏ lệnh ("SL xa quá thì thôi" 0:51:16).

**4c. Mục tiêu / R:R** (0:58:13–0:58:49):
- Thế A: mục tiêu = cạnh đối diện. Thế B: mục tiêu = xa hơn trong hai: E ∓ 1,0 × chiều cao range ("phá range này thì về range dưới" 0:40:00) hoặc cạnh gần nhất của range **đã chết** gần nhất nằm phía D (nếu có trong 300 nến).
- R_sẵn = (mục tiêu − entry)/rủi ro. R_sẵn < **1,7** ⇒ không vào. **TP luôn đặt 2R** (kể cả khi R_sẵn ∈ [1,7; 2)). Ngoại lệ ví dụ 3 (mục tiêu lấy vùng giá cũ xa hơn cạnh) **không code**.

**4d. Giới hạn:** 1 lệnh mở; mỗi (range, cạnh E, thế) tối đa **1 lệnh** ("không nhồi"); mỗi cú FailBreak / mỗi BreakConfirmed chỉ 1 lệnh; không vào trong **19:20–20:30 VN** theo mốc neo Mỹ (luật duy nhất có số từ vòng 1–2; giữ công tắc, đo cả bật và tắt); không vào trong 15 nến đầu phiên (mbr/nền chưa ổn) và khi `IsNewsBlocked`. Không giữ qua phiên: lệnh còn OPEN khi khoảng trống > 30′ ⇒ đóng tại giá đóng nến cuối (`TIME`). Không cap số lệnh/ngày — báo phân bố rồi quyết.

### ⛔ Không vào — code được / bỏ
| Mục ⛔ | Cách code | Trạng thái |
|---|---|---|
| Delta nhỏ, không có bóng | CF đòi Δ cùng dấu và ≥ 0,5 medΔ (4a); "không bóng" không veto riêng (ví dụ 3 CORVEN cho vào với trap + kiệt sức, không bóng) | code gần đúng |
| Kiệt sức chống hướng đánh | trong 5 nến tới CF có kiệt sức phía S (sell mà đáy kiệt sức sell) mà mức chưa bị râu quét qua tới CF ⇒ veto (0:53:35–0:54:43) | code đúng |
| Ngoài range mới 1 dấu hiệu | thế A đòi CF đóng trong range; ngoại lệ lần 2 đòi ≥ 2 dấu hiệu (2b) | code đúng |
| Nhịp đẩy do quét stop | thế B: cú đẩy (nến đóng ngoài → cực trị) phải có ΣΔ cùng dấu D; và nếu cực trị cú đẩy có bóng **ngược** D (SL khớp) mà trong K nến sau giá không lập cực trị mới ⇒ coi là quét stop, không follow | gần đúng — đo tỷ lệ bị loại |
| Range chồng range, đoạn xấu | range mới sinh trong ≤ 30 nến sau khi range trước chết và chồng ≥ 50 % chiều cao ⇒ không đánh thế A trên range mới cho tới FailBreak thứ 2 của nó | gần đúng — nếu loại > 30 % thế A thì bỏ luật, báo lại |
| Đấu giá vừa xong (profile nhọn) | cần TPO profile, định nghĩa "nhọn" chưa đo | **bỏ**, ghi README |

## 2. KIẾN TRÚC
**Python trước (`benzo-trader/research/`):**
- `of_signals.py` — port thuần từ C#: `stacked_zones(levels, ratio=250, run=3)` (= `StackedImbalanceCalc.Detect` + `Locate/Classify/CheckEnd`), `exhaustion(bar, levels)` (= `ExhaustionLogic.Detect/IsSwept`), `cell_baseline` + `bubbles` (3× nền, 10 hợp đồng), `delta_shapes`, `trap`. Có test so với C#: chạy `quantower-orderflow-indicator/tests` xuất danh sách stacked/kiệt sức 12.000 nến ⇒ Python phải khớp 100 %.
- `setup_corven.py` — import `quantower-range/research/range_proto.py` (sys.path, không copy), `kernel.load_bars/simulate/metrics` giữ nguyên; máy trạng thái theo sự kiện range → thế → cửa sổ → ③ → ④ → `entries` → `simulate`. Xuất `report/RESULTS-CORVEN.md` + `report/_corven_trades.csv` (mỗi lệnh: idx, giờ UTC, thế, mốc, danh sách dấu hiệu, entry/SL/TP, kết cục).
- `controls_corven.py` — 3 đối chứng (mục 3).

**C# sau (`benzo-trader/`):**
| File | Việc |
|---|---|
| `BenzoCorven.cs` (mới) | `DetectorCorven : IObservingDetector` — port y chữ `setup_corven.py`; `Observe` nuôi RangeLogic + sổ stacked/kiệt sức/nền mỗi nến; `TryDetect` trả `Signal` |
| `RangeLogic.cs` | **nối nguồn** từ `quantower-range/RangeLogic.cs` lúc build (như VclCore trước đây), đổi namespace bằng sed — một nguồn, không copy tay |
| `StackedImbalance.cs`, `ExhaustionLogic.cs` | nối nguồn từ `quantower-orderflow-indicator/` cùng cách |
| `BenzoOrderFlow.cs` (mới) | nền_ô, bóng, trap, delta shapes (phần chưa có trong hai file trên) |
| `BenzoCore.cs` | giữ (Signal, Simulate, cache, Telegram, CSV); `LogicVersion = "corven-1"` ⇒ cache cũ tự bỏ; thêm `Signal.Signs` (danh sách dấu hiệu) |
| `BenzoZones.cs` | **cắt** còn: tách phiên, `sm`/phase, giờ Mỹ, medΔ, mbr. Bỏ VA/IB/VWAP/chế độ M5 |
| `BenzoTrader.cs` | Settings còn: Lệch giờ · Telegram 4 ô · **Bật setup CORVEN** · **Chặn 19:20–20:30** (bật) · **Hiện range** (bật) · **Hiện dấu hiệu đã đếm** (bật) · Đặt lại thống kê · Hiện bảng. Vẽ: hộp range (mượn cách vẽ `RangeRenderer.cs`), mũi tên + hộp SL/TP, nhãn ngắn tại CF: `A sell · Δ ngược + bóng đỏ` |
| **Xoá** | `BenzoDetectors.cs`, `BenzoSetupA5.cs`, `BenzoLayers.cs`, `BenzoSr.cs`, tham chiếu `VclCore.cs`, `tools/ReplayA5`, `tests/TestsA5.cs`, các `setup_*.py`/`parity_*` cũ chuyển vào `research/_old/` (giữ lịch sử, không build) |
| `tools/ReplayCorven` | console chạy detector trên file export → CSV cho parity |
- Bảng trên chart: `BENZO CORVEN · N lệnh · WR · ΣR` + 2 dòng `Thế A` / `Thế B` + đuôi "chưa có lợi thế đo được" nếu T1 không đạt.
- **Reason / caption Telegram** (bắt buộc liệt kê dấu hiệu đã đếm, số thật):
  `🔴 SELL · CORVEN thế B · GCZ26 · 00:23 VN` / `Mốc: cạnh dưới 4127,4 vừa phá (range 4127,3–4132,5)` / `Dấu hiệu (2): Δ ngược giá ΣΔ −62/2 nến · bóng đỏ 18 @4127,3` / `CF 00:23 thân 0,6 giá · Vào 4126,6 · SL 4129,1 (2,5) · TP 4121,6 (2R, R sẵn 1,9)`.
- CSV log thêm cột `the,moc,signs`.

## 3. GIAO THỨC ĐO (chống khớp quá tay)
1. **Dữ liệu:** chỉ `fp_GCZ26_..._90d` (QĐ-6). Bỏ 4 phiên thưa đầu file và phiên `thin`. **TRAIN ≤ 2026-09-15 (≈ 40 phiên) / TEST ≥ 2026-09-16 (≈ 25 phiên)** — giữ đúng mốc chia của vòng 1–2 để so được. TEST **chỉ mở một lần**, ở GĐ2 sau khi đã chốt bộ tham số trên TRAIN; mở rồi không sửa gì nữa (sửa = ghi "đã nhìn TEST", kết quả mất giá trị).
2. **Mô phỏng:** `kernel.simulate` — chi phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào ở giá đóng CF, 1 lệnh mở.
3. **Tham số ĐƯỢC quét (và chỉ những cái này):** cửa sổ test thế B {2,3,4}; bội bóng {3,4}; run stacked {3,4}; bội delta {2,3}; "gần" {0,5; 1,0; 1,5} mbr; đệm SL {2,3,5} tick. Quét **từng tham số một** quanh bộ mặc định (như MEASURE.md), không quét lưới đầy đủ. **Tối đa 3 vòng** tinh chỉnh trên TRAIN; mỗi vòng ghi bảng đầy đủ, không chỉ ô tốt. Range, kiệt sức, 250 %, K/G, 1,7R/2R, thân 0,4/0,3: **đóng băng**.
4. **Đối chứng (bắt buộc, cùng SL/TP/chi phí):** (C1) *bỏ ③* — vào ở mọi CF hợp lệ tại mốc mà không đòi dấu hiệu; (C2) *ngẫu nhiên cùng giờ cùng hướng* — với mỗi lệnh thật, chọn 20 nến ngẫu nhiên trong cùng phiên, cùng giờ ±30′, cùng hướng, SL/TP cùng khoảng (rủi ro tính bằng mbr), lấy trung bình; (C3) *từng dấu hiệu đơn lẻ* — chỉ đòi 1 dấu hiệu, báo R theo từng loại.
5. **Bảng phải báo** (TRAIN, TEST, cả hai): n, lệnh/ngày, WR, R TB + KTC 95 % (bootstrap), ΣR, max DD (R), chuỗi thua dài nhất; tách **thế A / thế B**; theo **tổ hợp dấu hiệu** (Δ+bóng, trap+kiệt sức…); theo **giờ VN** (từng giờ) và phiên Á/Âu/Mỹ; theo tháng; tỷ lệ bị loại bởi từng cổng (R < 1,7, trần SL, ⛔ từng mục); 5 lệnh thắng + 5 thua kèm giờ UTC để soi chart.
6. **Tiêu chí "có lợi thế" (chốt trước):**
   - **T1 (có lợi thế):** n ≥ 60 lệnh trên cả 90 ngày; R TB sau phí **> 0 ở cả TRAIN và TEST**; R TB toàn bộ ≥ **+0,15** và cận dưới KTC 95 % > −0,05; hơn C1 và C2 ít nhất **+0,15R**; không ô nào trong bảng theo thế đổi dấu mạnh giữa TRAIN/TEST.
   - **T0 (port để forward test):** parity Python↔C# 100 % và R TB không kém C1/C2 quá 0,05R. **Dù chỉ đạt T0 vẫn port** (người học đã quyết thay A/B/C/D), README/bảng ghi "chưa có lợi thế đo được".
   - Không đạt cả T0 ⇒ dừng, báo lại trước khi port.

## 4. KIỂM THỬ
**Unit test Python (`research/test_setup_corven.py`) và C# (`tests/TestsCorven.cs`) — cùng danh sách ca, dữ liệu tổng hợp (dữ liệu 05–06/11 chưa có trong export; khi người học xuất GCZ26 M1 03→07/11 thì thêm ca thật):**
1. Tái hiện **ví dụ 1** (thế A sell): range 4130,9–4135,8; nến chọc 4138 có bóng đỏ ở râu; nhịp lên 7 nến ΣΔ < 0; CF đóng trong ⇒ tín hiệu sell, SL 4138,3, R_sẵn ≈ 1,7 ⇒ vào, TP 2R; mô phỏng chạm SL (giá vọt 4142).
2. **Ví dụ 2** (thế B sell): phá cạnh 4127,4 + stacked sell 4128,5 trong cú phá (làm mốc, không tính dấu hiệu); hồi 2 nến Δ −30/−32 + bóng đỏ ⇒ 2 dấu hiệu; SL 4129,1; TP 2R chạm.
3. **Ví dụ 3** (xác nhận lần 2): range 4123,2–4126,3, thủng xuống, lần 1 chỉ 1 dấu hiệu ⇒ không; lần 2 trap + kiệt sức đáy ⇒ vào buy dù ngoài range; R tới cạnh trên 1,3 ⇒ **bị loại** (đúng theo luật v1 — ghi rõ test này chứng minh ngoại lệ mục tiêu không code).
4. Stacked cũ làm mốc không được đếm; cùng nến trap + kiệt sức = 2; delta đồng thuận + delta ngược giá = 1.
5. Kiệt sức phía S chưa quét ⇒ veto; bị râu quét ⇒ hết veto.
6. R_sẵn 1,69 ⇒ bỏ; 1,7 ⇒ vào với TP 2R.
7. SL sàn 1 mbr, trần 4 mbr; đệm 3 tick; làm tròn tick.
8. ReEntry huỷ thế B; CloseThrough stacked huỷ mốc; tuổi 31 nến ⇒ hết.
9. Cửa sổ test: dấu hiệu ở nến thứ 4 trước CF (W=3) không tính.
10. Chặn 19:20–20:30 VN; 15 nến đầu phiên; lệnh OPEN qua khoảng trống > 30′ đóng TIME.
11. Nhân giá ×10 (MGC↔GC) ra cùng tín hiệu; **chạy một mạch = chạy từng nến** (cache).
12. Hồi quy: số lệnh/thế trên file 90d = số Python (mục [11] kiểu cũ).

**Parity Python↔C#:** `research/parity_corven.py` chạy `tools/ReplayCorven` trên 90d → so từng lệnh (giờ, thế, mốc, danh sách dấu hiệu, entry/SL/TP, kết cục, R) và danh sách sự kiện range (= `events_90d.csv`) + danh sách stacked/kiệt sức/bóng từng nến. Yêu cầu **100 %**; lệch có chủ đích chỉ ở luật tin USD (không có trong Python). Ghi `report/PARITY-CORVEN.md`, commit file đối chiếu.

**Tester độc lập (agent khác, không phải người port):** (a) chạy lại Python từ đầu, số phải trùng RESULTS; (b) kiểm TEST chỉ được mở 1 lần (git log: tham số không đổi sau commit "mở TEST"); (c) DLL bằng phản chiếu: đúng danh sách Settings mục 2, mặc định đúng; (d) UI render kịch bản tổng hợp ra PNG (`tests/ui-out/`): hộp range, mũi tên đúng nến CF, hộp SL/TP đúng giá, nhãn tiếng Việt không tràn, bảng 3 dòng; (e) lint thuật ngữ trong nhãn/caption (buy/sell/limit/market giữ Anh, không "mua/bán", không "volatility"); (f) Telegram gửi thử 1 tin mẫu có đủ dòng dấu hiệu.

## 5. THỨ TỰ VIỆC CHO OPUS (mỗi giai đoạn dừng, Fable review rồi mới đi tiếp)
- **GĐ0 — Khung + port dấu hiệu (Python):** `of_signals.py` + test khớp C# trên 12.000 nến; `setup_corven.py` chạy được tới bước ② (danh sách thế A/B + mốc) trên TRAIN. **Báo:** tần suất từng dấu hiệu trên TRAIN (so với mục 0 — lệch > 1,5× phải giải thích), số thế A / thế B / ngày, tỷ lệ bị loại bởi 2a/2b. *Dừng.*
- **GĐ1 — Đủ ①–④ + ⛔ trên TRAIN, bộ mặc định, chưa tinh chỉnh:** RESULTS-CORVEN.md đủ các bảng mục 3.5 + 3 đối chứng. *Dừng — Fable đọc 5 thắng/5 thua trên chart.*
- **GĐ2 — ≤ 3 vòng tinh chỉnh trên TRAIN (mục 3.3) → chốt → mở TEST một lần** → kết luận T1/T0. *Dừng.*
- **GĐ3 — Port C#:** nối nguồn RangeLogic/StackedImbalance/ExhaustionLogic, viết BenzoCorven/BenzoOrderFlow, xoá A/B/C/D, Settings, vẽ, caption, LogicVersion `corven-1`, unit test, build 0 cảnh báo, ReplayCorven + parity 100 %, deploy `qw-deploy.sh`, README viết lại. *Dừng.*
- **GĐ4 — Tester độc lập** mục 4 → `report/TEST-CORVEN.md` + ảnh. Fable review → sửa → commit/push.

Việc cần người học (1 dòng, không chặn): xuất GCZ26 M1 03→07/11/2026 bằng Footprint Export để thay 3 ca tổng hợp bằng ca thật và so hộp máy với 20 hộp CORVEN.
