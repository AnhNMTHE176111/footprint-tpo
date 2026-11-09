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
| stacked ≥ 3 mức, 250 % (định nghĩa CORVEN) | có ở **32 % nến theo TỪNG PHÍA** (buy 32 %, sell 33 %; nến có vùng bất kỳ phía 55 %; ≥ 4 mức: 16 %/phía) | stacked quá phổ biến ⇒ chỉ tính khi "mới + giữa thân + đóng phía đẩy" (mục 1.③d) |
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
- **Thế B** — range BROKEN theo hướng D (`BreakConfirmed`), chưa `ReEntry`, tuổi ≤ 30 nến kể từ nến đóng ngoài. Hướng = D. Mốc = cạnh vừa phá hoặc stacked mới cùng hướng D hình thành trong cú đẩy. **Gồm cả** `BreakConfirmed` làm range DEAD ngay vì hết lượt ReEntry (Q4, 19 % số cú phá): cú phá thật lần 3 vẫn là cú phá thật và cạnh vẫn là mốc; gắn cờ `b_from_exhausted` và **báo tách riêng** — GĐ2 được phép bật/tắt nhóm này (tính là 1 tham số quét).
- **1c (Q15):** pivot ngược D được chọn = pivot 1 nến ngược D **gần nhất sau nến đóng ngoài và sau lần gãy trước**; thế B tạm huỷ cho tới khi giá lập cực trị mới theo D (vượt cực trị cú đẩy tính tới lúc đó).
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
| B | stacked mới cùng hướng D | vùng stacked (250 %, ≥ 3 mức) hình thành **từ nến đóng ngoài trở đi** (Q8: ví dụ 2 vùng nằm trong chính cú phá), tuổi ≤ 30 nến, vị trí **Body, không Weak** (Q3: "râu phía đẩy" theo `Classify` luôn là Weak — CORVEN "ở đỉnh rồi rút râu thì không đẹp" ⇒ không làm mốc), **chưa từng bị chạm** trước nhịp test này (chạm = râu vào đúng [Lo, Hi], như `SiEndMode.Touch`; CORVEN 0:20:12 "chạm một mớ → vứt"), và chưa `ClosedThrough`. "Gần" = râu nến trong cửa sổ test chạm [Lo − tol, Hi + tol] (Q6: hai thước khác nhau vì hai mục đích khác nhau — "đã chạm" là chạm thật, "đang test" là đang tới gần) **và** CF đóng cách mép gần của vùng ≤ 1,0 mbr về phía D (Q5: "gần" là tính chất chung của mọi mốc, không riêng cạnh). |
- Mốc "xa" = không thoả tuổi/khoảng cách trên ⇒ bỏ (0:06:54 "dùng gần thôi"). Không có mốc "đỉnh/đáy vừa gãy" riêng ở v1 (chỉ tồn tại khi có range phá — đã là cạnh vừa phá).
- **Stacked cũ làm mốc KHÔNG tính dấu hiệu** (chi-tiet ③ cách đếm) — code bằng id vùng: vùng dùng làm mốc bị loại khỏi danh sách ③d.

**2b. Test không quá sâu:**
- Thế B: không nến nào trong cửa sổ test đóng lại trong range (= engine không phát `ReEntry`; nếu phát ⇒ thế B chết, range sống lại) và không nến nào đóng xuyên mép xa của vùng stacked làm mốc (`CheckEnd` CloseThrough). Râu xuyên **được phép** (ví dụ 2 râu chạm lại cạnh).
- Thế A: CF phải đóng **trong** range (1:00:02 "phải vào lòng range"). **Ngoại lệ "xác nhận lần 2"** (ví dụ 3, 1:00:09): range đang PENDING/BROKEN hướng −S (S = hướng vào lòng range), **phải có "lần 1"** = một nến y trước đó trong cùng cú thủng có râu phía −S và đóng lùi về phía S ≥ tol so với cực trị của nó (phe S đã thử một lần mà chưa vào được lòng range); rồi nến x quét qua cực trị của y ≥ 1 tick, đóng lùi về phía S ≥ tol so với cực trị mới, cùng ≥ 2 dấu hiệu ⇒ cho vào dù chưa đóng trong range; SL sau râu x. Chỉ 1 lần mỗi cú thủng, trong ≤ 30 nến từ nến đóng ngoài (Q12: bản không đòi lần 1 cho 25 ứng viên/ngày — quá lỏng). Báo nhóm này **tách riêng** trong bảng. **Sau GĐ1 (G1): ngoại lệ này TẮT mặc định ở v1** — xem mục 7.
- **FailBreak "whipsaw"** (đóng lại xuyên luôn cạnh đối diện, engine phát FailBreak + CloseOutside cùng nến): **không lập thế A** (Q13) — nến to hơn cả range thì không có mốc để chờ, CORVEN "không đuổi giá".

**2c. Cửa sổ test (cũng là cửa sổ "cùng lúc" của ③):**
- Thế A: từ nến đóng ngoài (ref của FailBreak) tới CF, **tối đa 5 nến** (K=3 + 2 nến chờ).
- Thế B: **3 nến** kết thúc tại CF (CF và 2 nến trước), đồng thời phải nằm trong tuổi 30 nến của BROKEN.
- Lý do 3 nến: ví dụ 2 (00:22–00:23 mang phân kỳ + bóng, CF 00:23), ví dụ 3 (trap + kiệt sức cùng 1 nến); CORVEN "những đoạn có nhiều tín hiệu cùng lúc" (1:05:57). Tham số được quét {2,3,4} — mục 3.

### ③ Dấu hiệu — mỗi dấu hiệu có **nến neo**; tính nếu nến neo nằm trong cửa sổ test và cùng phe với hướng vào. Cần **≥ 2 dấu hiệu khác loại**.
Hướng vào S (+1 buy / −1 sell).

**③a. Delta** (một trong hai dạng, tính tối đa 1):
- *Đồng thuận, to* (0:35:55 "dương to lên, thẳng lên"): nến neo = CF hoặc nến ngay trước CF, với Δ·S > 0, |Δ| ≥ **2 × medΔ**, và nến neo đóng theo S. **Bỏ điều kiện "thẳng" (`0,8 × max_delta`) ở v1 — Q1:** Footprint Export ghi `max_delta = min_delta = delta` ở 100 % nến lịch sử ⇒ điều kiện này không đo được; theo nguyên tắc "chưa đo được thì không code thành signal", C# **cũng không được dùng** `max_delta` (nếu không Python/C# lệch ở live). Việc phụ cho v2: sửa Footprint Export ghi intrabar thật rồi xuất lại. Lý do 2×: p75 của tỷ lệ (26 % nến) — "to" phải hiếm hơn một nửa; 3× (14 %) để quét.
- *Ngược giá* (0:31:42; ví dụ 1 và 2) — định nghĩa máy móc (Q9, chốt theo Opus): nến neo x = nến cực trị của nhịp, râu x chạm dải mốc (sell: H[x] ≥ mốc − tol); điểm xuất phát s = nến có đáy thấp nhất (sell; buy: đỉnh cao nhất) trong [x−8, x−2]; nhịp = s+1…x; biên độ L[s]→H[x] ≥ 1,0 mbr; **ΣΔ(s+1…x) có dấu ngược chiều giá** (sell: giá lên mà ΣΔ ≤ 0). Không đòi ngưỡng độ lớn (ví dụ 2: −30, −32 là đủ) — chỉ đòi dấu.

**③b. Bóng đúng phe tại mốc** (0:46:03–0:46:13): ô có side-volume phía S (buy: ask, sell: bid) ≥ **3 × nền_ô** và ≥ **10 hợp đồng**, nằm ở **nửa nến phía S** (buy: ô ≤ trung điểm nến) hoặc trong dải mốc ± tol. Nến neo = nến chứa ô. Nền_ô = trung vị 100 nến của (trung vị 3 ô side-volume lớn nhất mỗi nến), **tính trên các nến TRƯỚC nến hiện tại** (Q11, như OrderFlowBubbles; mbr và medΔ thì gồm nến hiện tại như Range Box/kernel — giữ hai quy ước này, ghi vào code), **bỏ MAD/z** — chỉ dùng bội số để Python/C# khớp dễ và người đọc hiểu ("gấp 3 lần ô bình thường"). Lý do 3×: 17 % nến — bóng là "đại diện chính" trên chart CORVEN nên không được quá hiếm; 10 hợp đồng = p90 ô, chặn nến đêm mỏng. Quét {3,4}.

**③c. Phe ngược kiệt sức ở râu** = `ExhaustionLogic.Detect` mặc định (SmallRel 0,10 · Fade 3 mức/0,25 · bắt buộc râu ≥ 1 tick): sell cần kiệt sức **đỉnh** (Ask), buy cần kiệt sức **đáy** (Bid), ở nến trong cửa sổ test, và mức đó **chưa bị râu quét qua** (`IsSwept`, sweepTicks 1) tính tới CF. Nến neo = nến kiệt sức.

**③d. Stacked mới cùng hướng S**: vùng `StackedImbalanceCalc.Detect(250 %, run 3, minVol 1)` phía S, hình thành ở nến trong cửa sổ test, **`Position == Body` và `Weak == false` và nến tạo vùng đóng ở phía S của vùng** (buy: close ≥ Hi). Nhánh "râu phía S" **bỏ** (Q3: theo `Classify` vùng ở râu phía S luôn Weak và không thể đóng vượt nó — nhánh này rỗng; câu CORVEN 0:03:40 "ở đỉnh cũng được nếu sau đó giá đi tiếp" cần nhìn nến SAU, không code ở v1). Không tính vùng đang làm mốc (id loại). Nến neo = nến tạo vùng. Vì ~31 % nến có stacked đủ điều kiện này (run 4: 16,5 %), nếu sau GĐ1 dấu hiệu này có mặt trong > 50 % số lệnh thì nâng run lên 4 (quét {3,4}).

**③e. Trap / stop hunt phe ngược** (0:23:45 "quét qua đỉnh mà nổ bóng thì là stop hunt"; 0:24:34 SL = bóng ngược màu): một nến có râu quét qua **mốc quan trọng** ≥ 1 tick và đóng lại phía S của mốc; mốc quan trọng = cạnh range (thế A: chính cú thủng; thế B: cực trị của cú đẩy hoặc pivot gần nhất ngược S), **và** trong phần râu có ô side-volume phía −S ≥ 3 × nền_ô **và ≥ 10 hợp đồng** (Q10: cùng sàn với ③b, cùng lý do nến đêm mỏng) (bóng ngược màu = SL khớp). Nến neo = nến quét. Trap và kiệt sức trên cùng nến = **2 dấu hiệu** (chi-tiet); trap và ③b khác màu nên không trùng.

Đếm: số loại dấu hiệu ≥ 2 ⇒ qua ③. Reason phải liệt kê từng dấu hiệu kèm số (mục 2 kiến trúc).

### ④ Lệnh
**4a. Nến xác nhận CF** theo S: đóng theo S (close·S > open·S); thân ≥ **0,4** biên độ; khoảng đóng–cực trị phía S ≤ **0,3** biên độ (= "đóng sát cực trị, không rút râu"); biên độ ≥ 0,5 mbr (loại doji); Δ·S ≥ 0 và |Δ| ≥ 0,5 medΔ (⛔ "delta nhỏ" — không đòi to, to là ③a). Thế A: CF phải là nến FailBreak hoặc 1–2 nến sau nó, đều đóng trong range (0:08:46). Vào ở **giá đóng CF**.

**4b. SL** (0:50:25 "đặt dưới cái đáy mới quét", "đặt gần dễ bị quét"):
- Thế A: sau cực trị râu của **toàn bộ** cú thủng (max/min từ nến đóng ngoài tới CF, kể cả nến giữa) ∓ **đệm 3 tick** (= max(3 tick, 0,2 mbr)). Biến thể đo ở GĐ2 (mục 7, neo "đáy/đỉnh mới quét" theo CORVEN 0:50:25): sau pivot 1 nến ngược S gần nhất trong [nến đóng ngoài − 10, CF].
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
1. **Dữ liệu:** chỉ `fp_GCZ26_..._90d` (QĐ-6). Bỏ 4 phiên thưa đầu file và phiên `thin`. **TRAIN ≤ 2026-09-15 (= 35 phiên dày, 47.622 nến) / TEST ≥ 2026-09-16 (= 26 phiên)** (Q14) — giữ đúng mốc chia của vòng 1–2 để so được. TEST **chỉ mở một lần**, ở GĐ2 sau khi đã chốt bộ tham số trên TRAIN; mở rồi không sửa gì nữa (sửa = ghi "đã nhìn TEST", kết quả mất giá trị).
2. **Mô phỏng:** `kernel.simulate` — chi phí 0,2 giá/lệnh, chạm SL+TP cùng nến = SL, vào ở giá đóng CF, 1 lệnh mở.
3. **Tham số ĐƯỢC quét (và chỉ những cái này):** cửa sổ test thế B {2,3,4}; bội bóng {3,4}; run stacked {3,4}; bội delta {2,3}; "gần" {0,5; 1,0; 1,5} mbr; đệm SL {2,3,5} tick; nhóm thế B từ range DEAD-ngay {bật, tắt} (Q4). Quét **từng tham số một** quanh bộ mặc định (như MEASURE.md), không quét lưới đầy đủ. **Tối đa 3 vòng** tinh chỉnh trên TRAIN; mỗi vòng ghi bảng đầy đủ, không chỉ ô tốt. Range, kiệt sức, 250 %, K/G, 1,7R/2R, thân 0,4/0,3: **đóng băng**.
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

## 6. QUYẾT ĐỊNH SAU GĐ0 (Fable, 2026-11-09 — trả lời 15 điểm ở `research/report/CORVEN-GD0.md` mục 5)
GĐ0 đạt: parity stacked + kiệt sức Python↔C# 0 lệch trên 51.319 nến; 39/39 test; TEST chưa chạm; tần suất khớp mục 0. Các mục 1–3 ở trên **đã sửa theo bảng này** (tìm "Qn" trong văn bản).
| Q | Quyết định | Lý do |
|---|---|---|
| Q1 Δ "thẳng" | **Bỏ** `0,8 × max_delta` ở v1, cả Python lẫn C#; ③a chỉ còn "to" (≥ 2× medΔ, cùng dấu, nến đóng theo S) | export ghi `max_delta = delta` 100 % ⇒ không đo được; giữ no-op ở lịch sử mà có tác dụng ở live = Python/C# lệch và R đo không đại diện. Việc v2: sửa Footprint Export ghi intrabar |
| Q2 stacked 32 % | Sửa câu mục 0: 32 % là theo từng phía (bất kỳ phía 55 %) | định nghĩa và mã đúng, chỉ khác mẫu số |
| Q3 ③d nhánh râu | ③d = **Body + không Weak + nến tạo vùng đóng phía S**; mốc stacked ở ② cũng **chỉ Body** | nhánh "râu phía S" rỗng theo `Classify`; vùng râu phía đẩy = Weak = "rút râu, không đẹp" ⇒ không làm mốc |
| Q4 range DEAD ngay | **Có lập thế B**, cờ `b_from_exhausted`, báo tách, GĐ2 được bật/tắt | phá thật lần 3 vẫn là phá thật; 19 % mẫu không được vứt mù, nhưng range đã phá 3 lần là "range xấu" nên phải nhìn số riêng |
| Q5 mốc stacked khoảng cách | **Thêm** CF đóng ≤ 1,0 mbr từ mép gần vùng | "gần" là tính chất của mọi mốc; 608 thế B chỉ nhờ stacked là lỗ hổng |
| Q6 hai thước chạm | **Giữ**: đã-chạm = đúng [Lo, Hi]; đang-test = ±tol | hai mục đích khác nhau (đã khớp lệnh ở vùng vs đang tiến về vùng) |
| Q7 tol | **Giữ**: cạnh dùng `r.tol` lúc sinh range; vùng dùng tol hiện tại | nhất quán với engine; vùng mới sinh thì mbr hiện tại là đúng |
| Q8 nến đóng ngoài | **Tính cả** nến đóng ngoài vào cú đẩy (bar ≥ ref) | ví dụ 2: vùng đỏ nằm trong chính nến phá |
| Q9 Δ ngược giá | **Chốt định nghĩa Opus** (s = cực trị đối diện trong [x−8, x−2], nhịp s+1…x, biên độ ≥ 1 mbr, ΣΔ ngược dấu) | máy móc, không nhìn trước, tần suất 25 % trên CF thế A hợp lý |
| Q10 trap sàn | **Thêm** sàn 10 hợp đồng cho bóng ngược màu của trap | cùng lý do ③b (nến đêm mỏng) |
| Q11 nền_ô | **Giữ** cách plan, tính TRƯỚC nến hiện tại; mbr/medΔ gồm nến hiện tại | khớp OFB và Range Box tương ứng; ghi rõ hai quy ước trong code |
| Q12 lần 2 | **Đòi "lần 1"**: nến y trước đó có râu phía −S + đóng lùi ≥ tol; x quét qua cực trị y; ≤ 30 nến; 1 lần/cú thủng; báo tách | 25 ứng viên/ngày là lỏng; CORVEN nói "confirm lại lần 2" = phải có lần 1 chưa vào |
| Q13 whipsaw | **Không lập thế A** | nến to hơn range thì không có mốc để chờ |
| Q14 số phiên | TRAIN 35 / TEST 26 phiên dày; tiêu chí n ≥ 60 giữ nguyên | chỉ là số đếm |
| Q15 1c | **Chốt định nghĩa Opus** | đúng tinh thần "một nến là đủ", không nhìn trước |

Nhận định thêm: ② chỉ lọc 10 % thế A / 3 % thế B là **đúng dự kiến** (fail break vốn đóng sát cạnh), không sửa ②. Toàn bộ sức lọc nằm ở ③④. Mức kỳ vọng sau ③④ (không phải mục tiêu để ép): **1–4 lệnh/ngày**; nếu > 8 lệnh/ngày thì ③ đang quá rẻ — xử lý ở GĐ2 bằng đúng các tham số được phép quét (run 4, bóng 4×), không thêm luật mới.

**Việc GĐ1 (Opus) — ĐÃ XONG (commit 47a531a):** hoàn thiện ③ (5 dấu hiệu có nến neo, đếm loại, Q1/Q3/Q9/Q10) + ④ (CF, SL sàn/trần/đệm, mục tiêu, R ≥ 1,7, TP 2R, giới hạn 4d) + ⛔ 4 mục code được + Q4/Q5/Q12; chạy `kernel.simulate` trên TRAIN với **bộ mặc định, không tinh chỉnh**; ra `report/RESULTS-CORVEN.md` đủ bảng mục 3.5, thêm **phễu** (thế → qua ③ → qua ④ → lệnh, kèm lý do loại từng cổng), nhóm tách riêng (`b_from_exhausted`, "lần 2"), 3 đối chứng C1/C2/C3, `_corven_trades.csv` (mỗi lệnh có danh sách dấu hiệu + số). Test mới cho ③④⛔ theo mục 4 (ca 1–7, 10). **Không chạm TEST, không đổi tham số.** Dừng để Fable soi 5 thắng/5 thua trên chart.

## 7. QUYẾT ĐỊNH SAU GĐ1 (Fable, 2026-11-09 — đọc `research/report/RESULTS-CORVEN.md`, 10 ảnh, và tự đo lại trên `_corven_trades.csv`)

### 7.1 Đọc kết quả thẳng thắn
- TRAIN, bộ mặc định: 159 lệnh (4,5/ngày), WR 27 %, **R TB −0,30 [−0,50; −0,09]**, kém C1 bỏ ③ (−0,24) và C2 ngẫu nhiên (−0,16; theo cặp −0,14). ⇒ **Ở bộ mặc định, ③ không thêm lợi thế**, thậm chí âm. Đây đúng là điều MEASURE.md đã cảnh báo cho fail break máy móc (−0,2R), và ③ chưa cứu được.
- Số tôi tự đo thêm (script trên `_corven_trades.csv` + `_bars.csv`): sau khi dính SL, giá vẫn chạm **TP gốc** trong 30 nến ở **36 %** lệnh SL, trong 60 nến **53 %**; 38 % SL dính trong ≤ 2 nến. **Nhưng** mô phỏng thô nới SL ×1,5 / ×2,0 (TP 2R theo rủi ro mới, bỏ lọc R_sẵn) cho R TB **−0,25 / −0,29** — không cứu. ⇒ Quan sát "hướng đúng, SL sát" của agent chính đúng ở hai ca THUA1/THUA2, nhưng **SL sát không phải nguyên nhân chính**; nguyên nhân chính là điểm vào không có lợi thế. Con số 36 %/53 % chưa có mức nền (giá M1 đi ±3R trong 30–60 nến là chuyện thường) — GĐ2 phải đo nền trước khi diễn giải.
- Phễu: ③ rẻ (33 % CF qua ②), cổng thật là 4a (81 %) và R ≥ 1,7 (61 %). Stacked có ở 86 % lệnh ⇒ theo plan ③d quét run 4.
- Theo số dấu hiệu: 2 loại −0,52 (n=100), 3 loại **+0,13** (n=49), 4 loại −0,20 (n=10). Đây là bảng đã lên kế hoạch báo, nhưng đọc nó rồi mới đổi luật là **hậu kiểm**; tôi cho phép quét `need_signs {2,3}` ở GĐ2 với ghi chú rõ "hậu kiểm, TEST quyết".
- Ảnh THUA1: A2 vào khi CF **đóng ngoài range** (4083,8 > cạnh 4082,7) — đúng theo chữ ngoại lệ Q12, không phải lỗi code, nhưng cho thấy ngoại lệ này đang là 40 % số lệnh (64/159) trong khi nguồn chỉ có **một** ví dụ của CORVEN. SL 4085,3 nằm **dưới** đỉnh cú thử (≈ 4085,8) vì Opus neo theo nến y thay vì toàn bộ cú thủng — sai so với 4b ("max/min từ nến đóng ngoài tới CF").
- Ảnh THUA2: SL 4393,6 bị đẩy ra bởi sàn 1 mbr, dính râu 4392,7 rồi giá đi 10 giá đúng hướng; "đáy mới quét" theo CORVEN là 4392,0 (20 nến trước) — đây là câu hỏi **neo SL ở đâu**, trả lời bằng biến thể 7.3.

### 7.2 Trả lời G1–G12 (RESULTS mục 13)
| G | Quyết định | Lý do |
|---|---|---|
| G1 lần 2 | **TẮT mặc định ở v1** (A2 chỉ còn là nhóm báo cáo trong Python, không port C#). Định nghĩa báo cáo siết lại: y = nến lập cực trị cú thủng; x quét qua cực trị y ≥ 1 tick **và đóng về phía S ≥ tol so với cực trị của y** | ngoại lệ dựa 1 ví dụ mà chiếm 40 % lệnh và 32 ứng viên/ngày = cơ khí hoá sai tinh thần "ngoại lệ"; R −0,29 không cứu gì. Đây là sửa ĐỊNH NGHĨA, không phải tinh chỉnh |
| G2 CF lần 2 | CF = x hoặc 1–2 nến sau x (như thế A) — chỉ cho nhóm báo cáo | nhất quán với 0:08:46 |
| G3 mốc trap thế B | **Giữ** {E, pivot 1c gần nhất ngược S} | cực trị cú đẩy là phía S, không phải chỗ SL phe −S |
| G4 quét stop | **Giữ** cách hiểu Opus | đúng 1 nghĩa khả dĩ, loại 8,8 % hợp lý |
| G5 chồng range cho A2 | không còn áp dụng (A2 tắt) | |
| G6 hai mốc cùng lúc | **SL theo mốc cạnh** (xa hơn) | CORVEN "sau mốc quan trọng" — cạnh quan trọng hơn vùng |
| G7 chọn lệnh khi bận | **Giữ**; C# port y hệt, ghi vào README | |
| G8 khoá chung A/A2 | **Giữ** (A2 tắt nên không còn tác dụng ở live) | |
| G9 ΣΔ = 0 | **Giữ ≤ 0**; mbr tại nến neo | theo chữ |
| G10 đóng trong vùng | **Giữ** là "gần" | chưa xuyên mép xa = mốc còn |
| G11 tin USD | **Giữ** lệch có chủ đích | |
| G12 TIME cuối phiên | **Giữ** | |

### 7.3 Sửa định nghĩa theo nguồn (KHÔNG tính vào 3 vòng tinh chỉnh — là sửa cho đúng plan/CORVEN)
1. **A2 tắt mặc định** (G1).
2. **SL thế A = cực trị toàn bộ cú thủng** (nến đóng ngoài → CF) + đệm — Opus đang neo sai ở nến y/CF (THUA1).
3. **Biến thể neo SL "đáy/đỉnh mới quét"** (CORVEN 0:50:25, 0:51:25): SL sau pivot 1 nến ngược S gần nhất trong [nến đóng ngoài − 10, CF] (thế A) / [nến đóng ngoài − 10, CF] về phía −D (thế B), + đệm; R_sẵn tính lại; trần 4 mbr giữ. **Đo song song** với neo hiện tại, báo cả hai: n, R TB, tỷ lệ bị loại vì R_sẵn, tỷ lệ "SL rồi vẫn chạm TP". Chọn neo **theo nguồn** (cái nào gần lời CORVEN và không tệ hơn), không chọn theo R.
4. **Mức nền cho "SL rồi vẫn chạm TP"**: với mỗi lệnh SL, lấy 20 nến ngẫu nhiên cùng phiên ±30′, hỏi xác suất giá đi được 3R (theo rủi ro lệnh) đúng hướng trong 30/60 nến. Nếu 36 %/53 % ≈ nền ⇒ gác hẳn câu chuyện SL.

### 7.4 GĐ2 — tối đa 3 vòng trên TRAIN, rồi mở TEST MỘT lần
- **Vòng 1:** áp 7.3 (A2 tắt, SL cú thủng đúng, 2 neo SL song song, nền 7.3.4) + chạy lại C1/C2. Báo bảng như GĐ1. *Fable review.*
- **Vòng 2:** quét **từng tham số một** quanh bộ vòng 1: `si_run` {3,4} · `bubble_mult` {3,4} · `delta_mult` {2,3} · `near_mbr` {0,5; 1,0; 1,5} · `win_b` {2,3,4} · `sl_buf_ticks` {2,3,5} · `b_from_exhausted` {bật, tắt} · **`need_signs` {2,3}** (hậu kiểm — ghi rõ trong báo cáo). Báo đủ bảng mọi ô + C1/C2 cho mỗi ô. Không lưới chéo.
- **Vòng 3:** chốt bộ **đơn giản nhất** mà (a) R TB TRAIN ≥ C1 và C2, (b) hàng xóm trong lưới không đổi dấu, (c) n ≥ 35 trên TRAIN. Nếu không ô nào đạt (a) ⇒ **không mở TEST**, dừng, báo người học: setup CORVEN cơ khí hoá ở mức này không hơn vào bừa tại mốc. Nếu đạt ⇒ mở TEST một lần với đúng bộ đó, kết luận T1/T0, commit "mở TEST".
- Không được: thêm dấu hiệu mới, đổi định nghĩa range/kiệt sức/250 %, đổi CF 0,4/0,3, đổi 1,7R/2R, bỏ cổng 4a dù nó loại 81 % (đó là cổng CORVEN: "nến xác nhận đã đóng").

### 7.5 Đánh giá thẳng của Fable
Khả năng cao nhất là **không đạt T1**; đạt **T0** (không kém C1/C2 quá 0,05R) cũng chưa chắc — hiện kém 0,06–0,14R. Nếu vòng 3 không đạt (a) thì theo plan mục 3.6 là **dừng trước khi port** và trình người học hai lựa chọn: (i) vẫn port với nhãn "chưa có lợi thế" để forward test (như A/B/C/D trước đây), hoặc (ii) giữ indicator đọc chart (Range Box + Bubbles) và không bắn tín hiệu. Tôi nghiêng về (ii) nếu còn kém đối chứng, vì bắn tín hiệu kém hơn vào bừa là có hại.

## 8. QUYẾT ĐỊNH SAU GĐ2 VÒNG 1 (Fable, 2026-11-09 — `RESULTS-CORVEN.md` mục GĐ2 v1, 20 ảnh, tự đo thêm trên `_corven_trades.csv`)

### 8.1 Neo SL: **giữ neo cú thủng / mốc (4b)**
Neo "đáy/đỉnh mới quét" gần lời CORVEN hơn nhưng **tệ hơn ở mọi mặt đo được**: n 77 < 97, R TB −0,36 < −0,29, thế B −0,45, 16,7 % chạm trần 4 mbr, loại vì R < 1,7 tăng 67 → 76 %. Luật chọn ở 7.3.3 là "theo nguồn **và không tệ hơn**" ⇒ không đạt vế hai. "SL rồi vẫn chạm TP" chỉ hơn nền 2–7 điểm % (37/51 % so với 31/44 %) ⇒ **gác hẳn giả thuyết "SL sát"**; vấn đề là điểm vào.

### 8.2 Ba ý của agent chính — kiểm bằng số trước khi quyết
| Ý | Số tôi đo trên 97 lệnh | Quyết |
|---|---|---|
| (a) Δ "to" phải so với nhịp gần, không chỉ medΔ 50 nến (THUA3: CF +22 sau các nến −50/−60/−80) | \|Δ_CF\| / max\|Δ\| 5 nến trước **< 0,5 → R TB −0,18 (n 36); ≥ 0,5 → −0,36 (n 61)** — ngược chiều giả thuyết | **Không thêm.** Không có số ủng hộ, và là luật mới (cấm ở 7.4) |
| (b) Thế B cấm CF là nến đẩy rời mốc (THUA5: vào ở đáy nến −93, cách mốc ≈ 0,5 mbr) | THUA5 vẫn trong "gần" 1,0 mbr. R theo biên độ CF/mbr: < 1 → −0,19 (n 56), 1–2 → −0,46 (n 38), ≥ 2 → −0,08 (n 3) — không đơn điệu | **Không thêm luật mới**; "không đuổi giá" đã có đòn bẩy hợp lệ là `near_mbr` {0,5; 1,0; 1,5} ở vòng 2 (0,5 sẽ loại ca này) |
| (c) Phiên Á tệ hơn? | Á **−0,60** (n 36) · Âu **+0,14** (n 29) · Mỹ −0,33 (n 32). Hậu kiểm, n nhỏ | **Không lọc phiên ở v1** (QĐ-2 cũ: bot chạy cả ngày, bảng tách phiên, người học tự tắt phiên khi thấy số live). Vòng 2 phải báo thêm **rủi ro trung vị theo giá** từng phiên: Á có mbr nhỏ ⇒ rủi ro ≈ 1,5–2 giá ⇒ phí 0,2 ăn 10–13 % mỗi R — đó là lý do cơ học có thể giải thích Á âm, không phải "setup sai ở Á" |

### 8.3 V1–V5
V1 giữ (y = nến lập cực trị và là "lần 1") · V2 giữ (nhóm báo cáo, đã tắt) · V3 giữ (pivot gần nhất về thời gian, phía −S của giá vào, sàn 1 mbr) · V4 giữ (nền quanh nến dính SL, 3R theo rủi ro lệnh) · V5 đúng.

### 8.4 Vòng 2 — lưới quét từng tham số quanh bộ vòng 1 (neo cú thủng, A2 tắt)
`si_run` {3,**4**} · `bubble_mult` {3,**4**} · `delta_mult` {2,**3**} · `near_mbr` {**0,5**; 1,0; **1,5**} · `win_b` {**2**,3,**4**} · `sl_buf_ticks` {**2**,3,**5**} · `b_from_exhausted` {bật,**tắt**} · `need_signs` {2,**3**} (hậu kiểm) — **14 ô mới + bộ gốc**, mỗi ô đổi đúng một tham số. Mỗi ô báo: n · lệnh/ngày · WR · R TB + KTC · ΣR · max DD · **C1 và C2 chạy lại cho đúng ô đó** · R theo thế A/B · R theo phiên Á/Âu/Mỹ + rủi ro trung vị (giá) theo phiên · R theo số dấu hiệu. Không lưới chéo, không thêm tham số, không lọc phiên/giờ mới. Kết quả: `RESULTS-CORVEN.md` mục "GĐ2 vòng 2" một bảng 15 dòng + phụ lục theo ô. *Dừng — Fable chọn ô cho vòng 3.*

### 8.5 Điều kiện mở TEST (không đổi so với 7.4) và nhận định
Vòng 3 chốt bộ **đơn giản nhất** thoả (a) R TB TRAIN ≥ C1 **và** ≥ C2 của chính ô đó, (b) hai hàng xóm trong lưới không đổi dấu, (c) n ≥ 35. Lưu ý thẳng: C2 hiện là −0,08 nên (a) đòi ô ≈ ≥ −0,08; `need_signs` = 3 có n 29 < 35 — nếu nó là ô duy nhất qua (a) thì **vẫn không mở TEST** (điều kiện (c) giữ nguyên, không hạ cho vừa). Khả năng cao nhất vẫn là dừng ở vòng 3 và trình người học hai lựa chọn ở 7.5.

## 9. KẾT LUẬN GĐ2 (Fable, 2026-11-09 — sau vòng 2, commit Opus 1500f62)
- Đính chính 8.4: lưới đúng là **11 ô** (tôi đếm nhầm thành 14; danh sách in đậm có 11 giá trị). Opus làm đủ 11, không thiếu ô nào.
- **Không ô nào đạt (a)** (R TB ≥ C1 và ≥ C2 của chính ô). Gần nhất: `sl_buf 5` −0,15 = C1 −0,15 nhưng C2 −0,02; `need_signs 3` +0,01 (n 38) nhưng C2 của nhóm +0,22 ⇒ dương do thời điểm, không do dấu hiệu. C2 dao động −0,17…+0,22 giữa các ô = nhiễu ±0,1R.
- Theo 7.4 vòng 3 và 3.6: **KHÔNG mở TEST, dừng trước khi port.** Không còn bước hợp lệ nào: 3 vòng đã dùng (vòng 1 sửa định nghĩa, vòng 2 quét, vòng 3 = chốt → không có ô), danh sách tham số đã quét hết, luật cấm thêm dấu hiệu/lọc phiên mới. Nới luật lúc này = lặp lỗi A/B/C/D.
- Quan sát hậu kiểm ghi lại (không dùng): Á âm 12/12 ô, Mỹ âm 12/12 ô, Âu ≥ 0 ở 10/12 ô; phí không giải thích (0,03–0,04R). Ví dụ CORVEN đều ở phiên Mỹ — chính phiên máy thua đều ⇒ bằng chứng là cơ khí hoá chưa bắt được cái CORVEN nhìn.
- Bản cho người học: `benzo-trader/research/report/KET-LUAN-CORVEN.md` — 3 lựa chọn (A port gắn nhãn forward test · B không bắn tín hiệu, giữ Range Box + Bubbles · C đăng ký trước giả thuyết "chỉ phiên Âu", chờ ≥ 60 phiên dữ liệu mới rồi chạy một lần). **Khuyến nghị: B ngay + C chạy nền.**
- Việc còn lại tuỳ người học chọn. Nếu chọn A thì GĐ3 làm theo mục 2 với LogicVersion `corven-1`, bảng phải ghi "−0,29R/lệnh trong 35 phiên, kém vào ngẫu nhiên". Nếu chọn C thì giả thuyết đăng ký ở đây: **bộ gốc vòng 1, chỉ nến CF có giờ VN trong 12:30–19:00 theo mốc neo Mỹ, chạy một lần trên dữ liệu từ 22/10/2026 trở đi khi đủ ≥ 60 phiên dày; tiêu chí = T1 mục 3.6.** Không được đổi gì khác trước khi chạy.

## 10. QUYẾT ĐỊNH GĐ3 — PORT (người học chọn A, Fable 2026-11-09)

Người học trả lời nguyên văn: *"cứ thay hẳn đi, rồi dần dần tôi review và update tín hiệu này để dần có lợi thế nhé"* ⇒ **lựa chọn A**:
port vào Benzo, **thay hẳn** A/B/C/D, gắn nhãn chưa có lợi thế, forward test; người học sẽ lặp "review → sửa tín hiệu" dần.
Mục này là lệnh làm việc cho Opus; chỗ nào mâu thuẫn với mục 2 thì **mục 10 thắng**. Opus không hỏi lại — thiếu gì thì chọn cách đơn giản nhất và ghi vào README mục "Quyết định khi port".

### 10.1 Bộ tham số được port = **bộ gốc vòng 1** (RESULTS-CORVEN.md dòng 766), `LogicVersion = "corven-1"`
Giá trị mặc định (đóng cứng trong `BenzoCorven.cs`, một `static class CorvenParams` để test đọc được):
`near_mbr 1,0 · win_b 3 · win_a_max 5 · cf_after_fb 2 · age_b 30 · si_ratio 250 · si_run 3 · si_minvol 1 · b_from_exhausted BẬT ·
same_session BẬT · delta_mult 2 · bubble_mult 3 · bubble_min 10 · div_min_len 2 · div_max_len 8 · need_signs 2 ·
cf_body 0,4 · cf_close_ext 0,3 · cf_min_rng_mbr 0,5 · cf_min_delta 0,5 · sl_buf_ticks 3 (đệm = max(3 tick, 0,2 mbr)) ·
sl_floor_mbr 1,0 · sl_cap_mbr 4,0 · r_min 1,7 · tp_r 2,0 · dead_look 300 · block_first_bars 15 · veto_window 5 · stop_run_k 3 ·
overlap_bars 30 · overlap_frac 0,5 (luật chồng range GIỮ — chỉ loại 1,8 % thế A)`.
**Không port:** ngoại lệ "lần 2" (`a2_on`, `exc_max_age`, `a2_cf_after` — nhóm báo cáo Python, G1), neo SL `pivot`/`piv_back` (8.1 đã bác),
`overlap_max_drop` (là luật báo cáo, không phải luật live), bộ lọc thin/splice của Python. Neo SL duy nhất = `cu_thung` (4b).
`block_us_open` là công tắc Settings (10.2), mặc định BẬT.

### 10.2 Settings: **không đưa tham số số ra Settings**; chỉ công tắc
Danh sách Settings cuối cùng (thay dòng `BenzoTrader.cs` ở mục 2, bỏ hết A/B/C/D):
`Lệch giờ · Telegram: bật / token / chat id / gửi thử · Bật setup CORVEN (chạy thử — backtest −0,29R/lệnh, kém vào ngẫu nhiên) [BẬT] ·
Chặn 19:20–20:30 VN (mốc neo Mỹ) [BẬT] · Hiện range [BẬT] · Hiện dấu hiệu đã đếm [BẬT] · Đặt lại thống kê · Hiện lại toàn bộ thống kê · Hiện bảng [BẬT]`.
- **Lý do không đưa `win_b / bubble_mult / need_signs / sl_buf / near_mbr / lọc phiên` ra Settings:** đổi tham số sống mà không đo lại trên dữ liệu
  = đúng lỗi A/B/C/D; và mỗi bộ tham số là một chuỗi forward test riêng — n live vốn đã nhỏ (≈ 3 lệnh/ngày), chia theo bộ thì vô nghĩa.
  Vòng "review → update" của người học đi qua **Python trước** (`setup_corven.py` sửa → đo TRAIN + đối chứng → sửa C# → `LogicVersion` mới `corven-2`…),
  không qua nút bấm. Ghi quy trình này thành mục "Cách đề xuất sửa tín hiệu" trong README (5 dòng).
- **Cache key** = `LogicVersion + "-us" + (chặn ? 1 : 0)` (thay `BModeKey/CModeKey`). "Hiện range"/"Hiện dấu hiệu" chỉ vẽ ⇒ **không** vào key.
- **Chỉ chạy trên nến 1 phút**: `BarMinutes != 1` ⇒ không dựng engine, chart hiện 1 dòng "Benzo CORVEN chỉ chạy trên chart M1". Bỏ hẳn chế độ M5.
- Bảng trên chart ghi thêm `corven-1` ở dòng đầu để ảnh chụp nào cũng biết đang chạy phiên bản nào.

### 10.3 Nhãn trung thực — chuỗi cố định, test phải so đúng chữ
- **Bảng chart (4 dòng):** `BENZO CORVEN corven-1 · N lệnh · WR x % · ΣR` / `Thế A · n · WR · ΣR` / `Thế B · n · WR · ΣR` /
  `Backtest 35 phiên: −0,29R/lệnh, kém vào ngẫu nhiên (−0,08R) · chạy thử, không phải khuyến nghị`. Dòng 4 **luôn hiện**, không có điều kiện tắt.
- **Telegram tin mở:** caption như mục 2 (4 dòng) + dòng cuối `⚠ Chưa có lợi thế đo được (−0,29R/lệnh, 35 phiên)`.
- **README** khối đầu: 3 câu — setup là gì, số backtest trên (kèm C1/C2), "đang forward test để người học review, không phải khuyến nghị".
  Bảng A/B/C/D cũ **xoá khỏi README**, thay bằng 1 dòng trỏ `research/report/TONG-KET-VONG-1-2.md`.
- Nhãn Settings của công tắc setup như 10.2. Lint thuật ngữ (mục 4e) áp cho mọi chuỗi trên.

### 10.4 Cơ chế để người học review dần (giữ đơn giản: 1 CSV lệnh + 1 CSV ứng viên + nhãn chart + Telegram)
1. **CSV lệnh** `signals_<sym>_<tf>_corven-1.csv`, header mới (thay hẳn header cũ):
   `time_utc,time_vn,the,side,range_lo,range_hi,b_from_exhausted,moc,n_signs,signs,entry,sl,tp,risk,r_avail,outcome,exit_time,r,mfe_r,mae_r,phien`.
   `signs` **đúng định dạng chuỗi của cột `dau_hieu` Python** (`Δ: Δ to -36 = 3,8× medΔ (nến 4769) | bóng: …`) để parity so thẳng chuỗi;
   `the` = A/B; `moc` = `canh` hoặc `stacked lo–hi`; `phien` = Á/Âu/Mỹ theo neo Mỹ; `mfe_r/mae_r` = chạy xa nhất thuận/nghịch (theo R) từ vào tới đóng,
   tính trong `Simulate` (thêm 2 trường vào `Signal`, cache lưu luôn) — đây là số để tự kiểm lại tranh luận "SL sát" trên dữ liệu live.
2. **CSV ứng viên bị loại** `candidates_<sym>_<tf>_corven-1.csv` — **chỉ ghi live** (nến vừa đóng, không ghi lịch sử, không cache):
   `time_utc,the,side,moc,gate,detail` với `gate` ∈ {`③ 0 loại`, `③ 1 loại`, `④ CF`, `④ R<1,7`, `④ trần SL`, `⛔ veto kiệt sức`, `⛔ quét stop`, `⛔ chồng range`, `chặn giờ`, `tin USD`, `đang có lệnh`}
   và `detail` = dấu hiệu đã đếm được (nếu có). Mục đích: người học thấy "chỗ này tôi thấy đẹp mà máy không vào — vì cổng nào". Mỗi CF qua ② một dòng.
3. **Nhãn chart "Hiện dấu hiệu đã đếm":** tại nến CF của mỗi lệnh, 1 dòng ngắn `A sell · Δ ngược + bóng đỏ 18` (loại dấu hiệu + số đắt nhất của mỗi loại);
   **không** vẽ ứng viên bị loại lên chart (tránh rối; đã có CSV 2).
4. **"Hiện range":** hộp range theo trạng thái (PENDING/ACTIVE/BROKEN) mượn cách vẽ `RangeRenderer.cs`; thế B đang sống vẽ thêm đường đứt tại mốc.
5. **Telegram** như 10.3. Tin đóng giữ dạng cũ `✅/🛑 CORVEN thế A ±x,xR · giờ→giờ`.

### 10.5 Bug cache phải sửa khi port (cùng loại bug đã sửa ở `quantower-orderflow-indicator/SignalCache.cs`)
Hiện `BenzoTrader.cs` ~371/396 đặt tên `cache_<symbol>_<Aggregation.Title|Name>.jsonl` — không chắc chứa khung ⇒ đổi khung hoặc đổi History range làm lẫn tín hiệu. Sửa:
- Tên file = `cache_<sym>_<aggName>_<minutes>m.jsonl` (lấy phút từ `Aggregation` như cách tính `BarMinutes` dòng ~425; không dùng `Title`). Cùng quy tắc cho 2 file CSV ở 10.4.
- **Guard khớp nến** khi nạp cache (như `FitsBar`): mỗi dòng `sig` lưu thêm `H,L` của nến CF; khi gắn lại vào nến cùng `Time`, nếu `|Entry − C| > tick/2` hoặc `H/L` lệch > 1 tick ⇒ **bỏ toàn bộ cache**, dò lại từ đầu (ghi 1 dòng `error_log`). Không vá từng dòng.
- Khi `BarMinutes != 1` không tạo cache (10.2). File cache cũ `cache_<sym>_<Title>.jsonl` của logic A/B/C/D: **xoá** khi gặp (version lệch nào cũng vô dụng).
- Test: (i) cùng file 90d chạy M1 rồi chạy M1 với History range ngắn hơn → tập tín hiệu chung phải trùng, không có tín hiệu "lạ"; (ii) sửa tay `H` một dòng cache → nạp phải bỏ cache.

### 10.6 Nghiệm thu GĐ3 + GĐ4 — parity và ranh giới TEST
- **TEST vẫn chưa "mở".** Định nghĩa "mở TEST" (3.1) = đọc **kết quả R/WR** của các lệnh sau 2026-09-15. Parity là kiểm **mã**, không phải kiểm **lợi thế** ⇒
  `ReplayCorven` được chạy **toàn file 90d**, nhưng `parity_corven.py` **chỉ so định danh** trên phần TEST (giờ, thế, mốc, dấu hiệu, entry/SL/TP),
  **so cả kết cục + R chỉ trên TRAIN** (bar_idx ≤ cut 2026-09-15). `PARITY-CORVEN.md` báo hai số: `TRAIN n/n khớp (kể cả kết cục) · TEST m/m khớp định danh`,
  **không in R, WR, ΣR, không liệt kê từng lệnh TEST**. Script phải bỏ cột `ket_cuc,r,exit_idx,giu_nen` của phần TEST trước khi so.
  Test hồi quy C# [12] "số lệnh trên file" **chỉ đếm TRAIN: 97 lệnh (A/B theo RESULTS 2.3)**. Giữ TEST nguyên vẹn cho giả thuyết C (mục 9) nếu sau này dùng.
- **GĐ3 đạt khi:** build 0 cảnh báo mới · unit test C# đủ 12 ca mục 4 (ca 3 ghi rõ A2 không port nên chỉ kiểm "bị loại", ca 11 ×10 + chạy mạch = từng nến) + 2 test cache 10.5 + test chuỗi nhãn 10.3 ·
  parity **100 %** theo định nghĩa trên (lệch có chủ đích duy nhất: tin USD) · deploy `qw-deploy.sh` · README viết lại theo 10.3/10.4.
- **GĐ4 (tester độc lập):** mục 4 (a)–(f) nguyên trạng, thêm (g) `git grep` xác nhận không script nào đọc R của phần TEST; (h) chạy test cache 10.5 trên máy khác thư mục; (i) ảnh bảng chart có đủ dòng 4 của 10.3. Ghi `report/TEST-CORVEN.md`.

### 10.7 File xoá / chuyển — xác nhận mục 2, bổ sung
- **Xoá khỏi build và repo (git giữ lịch sử, không cần `_old` cho C#):** `BenzoDetectors.cs`, `BenzoSetupA5.cs`, `BenzoLayers.cs`, `BenzoSr.cs`, tham chiếu `vung-canh-lenh/VclCore.cs` trong `build.sh`, `tests/TestsA5.cs`, `tools/ReplayA5`, **`tools/ReplayCsv`** (mục 2 quên — nó chạy A/B/C/D).
- **Giữ:** `ProfileEngine.cs` trong chuỗi nối **chỉ vì `NewsCalendar`** (ghi 1 dòng README; tách sau), `tools/OfSignalsDump` (parity stacked/kiệt sức GĐ0 vẫn dùng), `BenzoCore.cs` (cắt `DemoDetector` nếu còn tham chiếu detector cũ), `BenzoZones.cs` cắt theo mục 2 (tách phiên, sm/phase, giờ Mỹ, medΔ, mbr; bỏ VA/IB/VWAP/M5/zigzag/`BenzoRisk`).
- **`research/_old/`** (chuyển, không build/không test): `setup_a_*.py, setup_b_*.py, setup_c_*.py, setup_d_trap.py, zones_*.py, test_setup_a_*.py, test_b_*.py, test_setup_c_*.py, parity_check.py, parity_a_v5.py, parity_b_v3.py, benzo_vcl.py, test_benzo_vcl.py, sr_measure.py, _dissect*.py, _plot_run.py, _plot_sl.py, PLAN-C-v2.md, PLAN-C-v3.md`.
  **Giữ nguyên chỗ:** `kernel.py, kernel_check.py, test_kernel.py, of_signals.py, test_of_signals.py, parity_of_signals.py, setup_corven.py, controls_corven.py, results_corven.py, sweep_corven.py, test_setup_corven*.py, test_sweep_corven.py, plot_corven.py` và toàn bộ `report/` (không xoá báo cáo cũ).
- `tests/Program.cs`: giữ test `BenzoCore/Zones` còn áp dụng, xoá test detector cũ; thêm `tests/TestsCorven.cs`.
- Thứ tự làm: (1) nối nguồn + `BenzoCorven/BenzoOrderFlow` + test xanh → (2) `ReplayCorven` + parity 100 % → (3) mới xoá file cũ, sửa Settings/vẽ/README → (4) build, deploy, commit. Không xoá trước khi parity xong.

## 11. FOLLOW-COMBO — thiết kế đo các combo "Follow sau cú phá" (Fable, 2026-11-09) → `plans/BENZO-FOLLOW-COMBO-plan.md`
Yêu cầu mới của người học (kèm ảnh GCZ26 M1): Follow = **move phá range → nhịp hồi 1–2 nến → dấu hiệu ở nhịp hồi/CF → CF trong ≤ 3 nến**, CF chỉ cần
"tăng · Δ xanh · đóng cao hơn"; mỗi combo (trap nguyên thủy, bóng CF, kiệt sức hồi, …) có tên, đo riêng, rồi mổ lệnh SL để cải tiến.
Khác Thế B đang port: xét **ngay từ `CloseOutside`** (không đợi `BreakConfirmed`), không đòi hồi về cạnh, CF lỏng hơn 4a, TP 2R không cổng mục tiêu.
- File Python **mới** `research/follow_combo.py` + `test_follow_combo.py` + `plot_follow.py` + `mo_sl_follow.py`; **không sửa** `setup_corven.py`/C# (GĐ3 port chạy song song).
- 10 combo đăng ký trước (F1…F10) + F0 = C1; đối chứng C1/C2 **từng combo**; hiệu chỉnh nhiều phép thử bằng **kiểm hoán vị thống kê cực đại** (2.000 lần, phân vị 95);
  ĐẠT = n ≥ 30 · ≥ C1+0,15 · ≥ C2+0,15 · KTC dưới > −0,10 · dương cả 2 nửa TRAIN · qua hoán vị. Mổ SL: danh mục nhãn cố định, nhãn phải ≥ 40 % SL và ≤ 20 % TP, ≤ 1 luật/combo/vòng, ≤ 2 vòng, combo sửa không được mở TEST.
- **TEST 26 phiên dành cho Follow, mở một lần** nếu có combo ĐẠT; **giả thuyết C mục 9 giữ trên dữ liệu mới ≥ 22/10** (10.6 chỉ là dự phòng, mục 9 thắng). Sau khi mở, TEST coi như đã dùng.
- Port C# (`corven-2`) chỉ khi qua TEST với T1 — khác quyết định A của Thế A/B.
- Ý kiến thẳng: hướng hợp lý (Thế B không thể bắt ca ảnh; CORVEN 0:46:13/0:48:07 ủng hộ combo "trap + CF có lực"), nhưng nền F0 nhiều khả năng âm, F1/F4/F5 có thể n < 30, dự đoán ~30 % có combo ĐẠT.

## 12. QUYẾT ĐỊNH SAU GĐ4 (tester) — Fable, 2026-11-09, đọc `research/report/TEST-CORVEN.md` (commit 9f2c71b)

**Trạng thái TEST: vẫn CHƯA mở.** Tester chỉ đếm số ô có dữ liệu trong file tạm rồi xoá, không ai đọc R/kết cục. Nhưng ranh giới trong mã
đã hỏng (lỗi #1) ⇒ phải vá và khoá hai lớp trước khi ai chạy tay ReplayCorven lần nữa.

**Thứ tự và tương thích:** các việc dưới đây làm **SAU** khi Opus làm xong mục 9.3 của `plans/BENZO-FOLLOW-COMBO-plan.md` (đính chính C2,
có thể đổi 4 chuỗi nhãn theo nhánh (a)/(b)), **cùng một lần build + deploy**. Opus sửa lỗi **không chạm** 4 chuỗi nhãn; nếu 9.3 đi nhánh (b)
thì cập nhật chuỗi mong đợi trong `tools/TesterGd4/Gd4/Program.cs` (dòng 77, 406) cho đúng chữ mới của plan — `tests/Program.cs` do Opus 9.3 sửa.
`LogicVersion` **giữ `corven-1`**: không sửa nào dưới đây đổi tập lệnh TRAIN (parity 97/97 phải giữ nguyên). Không đổi khoá cache.
Ưu tiên theo lời người học: **không mất lịch sử, nhãn đọc được** (#2, #3 trước; #1 là an toàn dữ liệu, bắt buộc).

### 12.1 Bảy mục của tester

| # | Quyết | Sửa thế nào | Lý do (1 dòng) | Test bắt buộc |
|---|---|---|---|---|
| 1 CAO | **SỬA + khoá 2 lớp** | `ReplayCorven/Program.cs` dòng ~71: dùng `outc / rr / exs` ở `Append`. `parity_corven.py`: **trước** `drop(OUT_COLS)` kiểm phần TEST của C# — ô nào trong `ket_cuc/r/exit_idx` không rỗng ⇒ `raise` + xoá thư mục tạm, không so tiếp. Sửa README dòng 33/117, docstring ReplayCorven, ghi chú parity dòng 142/147 cho đúng sự thật. | Ranh giới TEST hiện chỉ đứng nhờ một dòng `drop` — một lớp là quá mỏng cho thứ không được phép xảy ra lần hai. | (i) test C# mới trong `tests/`: chạy hàm ghi CSV của ReplayCorven với `hideAfter` trên 3 `Signal` giả (1 ≤ cut, 2 > cut) ⇒ 2 dòng sau cut có 3 ô rỗng, dòng trước có số; (ii) pytest mới: `parity_corven` nhận DataFrame TEST có 1 ô `r` không rỗng ⇒ `raise`; (iii) chạy lại `parity_corven.py` toàn bộ ⇒ 100 % như cũ, báo cáo không đổi. |
| 2 TB | **SỬA — không niêm phong nến lúc setup tắt; lệnh đã niêm phong vẫn hiện khi tắt** | `BenzoEngine.Advance`: (a) nến xử lý khi `!IsEnabled` ⇒ **không** đưa vào `MarkRange` (ngắt khoảng niêm phong tại đó, nến bật lại mới niêm phong tiếp); (b) lệnh **đã có trong cache** vẫn lấy ra dù setup đang tắt (bỏ điều kiện `IsEnabled(sealedSig.Setup)` ở nhánh cache) — tắt chỉ chặn **dò mới**. Không đưa công tắc vào khoá cache. Ghi README: *"TẮT = tạm ngừng dò; lịch sử đã có vẫn hiện; nến lúc tắt được dò bù khi bật lại / nạp lại chart."* | Lịch sử là dữ liệu forward test của người học — công tắc chỉ được ngừng tạo tín hiệu mới, không được xoá quá khứ. Đưa công tắc vào khoá cache cũng xoá lịch sử (khoá khác = bỏ cache). | (i) kịch bản của tester: tắt tới nến 15000, bật ⇒ **27/27** lệnh trước 15000 có lại, bảng và CSV lệnh đủ; (ii) test cache: sau đoạn tắt, dòng `rng` **không phủ** các nến đó; (iii) đang tắt, nạp cache có lệnh ⇒ lệnh vẫn vẽ, bảng vẫn đếm, không gửi Telegram; (iv) Gd4 mục (h) chuyển PASS. |
| 3 TB | **SỬA — lật nhãn sang trái khi tràn** | Tách hàm thuần `static float LabelX(float xE, float w, float clipLeft, float clipRight)`: mặc định `xE + 8`; nếu `xE + 8 + w > clipRight` ⇒ `xE − 8 − w`; nếu vẫn `< clipLeft` ⇒ kẹp `clipLeft + 2`. Nền nhãn đi theo. | Lệnh mới nhất luôn ở mép phải — đúng lệnh cần đọc nhất lại bị cắt. | (i) unit test `LabelX` 3 ca (vừa, tràn phải, chart hẹp); (ii) Gd4 (d) ảnh `corven-live-mep-phai` đọc đủ chuỗi nhãn, không tràn. |
| 4 THẤP | **SỬA cùng lượt** | `xE = GetChartX(s.Time) + BarsWidth / 2` cho mũi tên, nhãn, mép trái hộp SL/TP; `xEnd` giữ nguyên. Hộp range (`b.T0/T1`) không đổi. | Một dòng, cùng quy ước với RangeBox/OrderFlowBubbles trong repo; với nến footprint rộng 60–100 px lệch nửa nến là đọc nhầm nến. | Gd4 (d): đỉnh mũi tên tại tâm nến CF (lệch ≤ 1 px). |
| 5 THẤP | **SỬA gốc — `sm` chỉ phụ thuộc UTC** | `BenzoKernel.SmOf` dùng hằng **+7** (như `kernel.py`: "phút kể từ 05:00 VN"), không dùng `TzOffset`. `TzOffset` chỉ còn cho hiển thị giờ, CSV `time_vn`, caption, `NewsCalendar`. Không đưa vào khoá cache. | Luật chặn giờ là luật về **thị trường Mỹ**, không được đổi theo cách người dùng muốn xem giờ. | (i) unit test `SmOf(utc, 7) == SmOf(utc, 8)` (hoặc chữ ký mới không còn tham số); (ii) kịch bản của tester: lệch giờ 7 → 8 ⇒ **0** lệnh khác trên 24.000 nến; (iii) parity 97/97 không đổi. |
| 6 THẤP | **SỬA — thống nhất giờ MỞ nến** | `ComposeOpen/ComposeClose/ComposeCancel`: bỏ `.AddMinutes(barMinutes)`; giờ trong caption = giờ mở nến CF (= `time_vn` CSV = `t_vn` Python = nhãn thời gian nến trên Quantower). | Người học đối chiếu Telegram ↔ CSV ↔ chart; ba nơi phải cùng một mốc, và chart Quantower ghi nến theo giờ mở. | Unit test: caption lệnh `GCZ26 / 2026-07-29 15:52 UTC / thế A sell` ghi **22:52 VN**, bằng `SignalCsv.Key` cùng lệnh; tin đóng `→` cũng giờ mở nến thoát. |
| 7a | **GIỮ cổng `thế đã có lệnh`** — bổ sung vào plan 10.4.2 | Là luật 4d "mỗi (range, cạnh E, thế) tối đa 1 lệnh / mỗi FailBreak 1 lệnh" — plan liệt kê thiếu, không phải cổng ngoài plan. Danh sách cổng chính thức = 10.4.2 + `thế đã có lệnh`. Xem thêm Q1. | — | Test chuỗi cổng: `GateVn` phủ đủ danh sách mới, không có cổng nào ngoài danh sách. |
| 7b | **GIỮ dấu trừ ASCII** trong `signs` | Chuỗi `signs` phải **đúng byte** cột `dau_hieu` Python để parity so thẳng (10.4.1). Ghi 1 dòng README. | — | — (parity đang là test). |
| 7c | **SỬA nhẹ — vẽ hộp range của lệnh cũ** | Thêm `RangeT0, RangeT1` (ticks UTC) vào `Signal` + dòng `sig` cache (dòng cũ thiếu ⇒ 0 ⇒ không vẽ). Khi "Hiện range" bật: với mỗi lệnh đã đóng vẽ hộp `[range_lo, range_hi] × [T0, T1]` viền đứt mờ (alpha ≈ 60), không nhãn. Range còn sống vẽ như cũ. Không đổi `CacheVersion`. | Soát lại lệnh cũ mà không thấy range là mất ngữ cảnh "mốc" — đúng thứ người học cần khi review. | (i) cache round-trip 2 trường mới + dòng cũ không có trường vẫn nạp được, guard không đổi; (ii) Gd4 ảnh `corven-A-SL-0729-1552` thấy hộp range cạnh lệnh đã đóng. |
| 7d | Sửa số | Plan/README ghi "pytest 83 ca" thay 65. | — | — |

### 12.2 Trả lời Q1–Q5 của Opus port

- **Q1 — GIỮ `thế đã có lệnh` và `đang có lệnh` là hai cổng riêng; BỎ `setup tắt`.** Hai cổng đầu nói hai điều khác nhau cho người học
  (khoá 1 lệnh/thế/range vs đang có lệnh mở). `setup tắt` bỏ vì sau sửa #2 nến lúc tắt **không dò** ⇒ không có ứng viên để ghi; nhánh
  `if (!EnableCorven) gate = "setup tắt"` xoá luôn. Test: danh sách cổng trong README = tập giá trị `GateVn` + 2 cổng engine, so đúng chữ.
- **Q2 — CÓ, thêm cổng `cuoi_phien` khi `sm ≥ 1379`** (nến mở 16:59 ET = nến M1 cuối của phiên 18:00→17:00 ET; `GateVn` → `cuối phiên`).
  Đây **không phải luật mới** mà là cách nhân quả duy nhất để code luật 4d "nến cuối phiên không vào" — Python nhìn trước nến cuối, máy sống
  không thể. **Giữ** cơ chế huỷ ở `BenzoEngine.EndSession` làm lưới dự phòng cho ngày đóng sớm / thiếu nến. Parity: `parity_corven.py` bỏ
  `cuoi_phien` ở **cả hai phía** trước khi so cột `gates` (hiện chỉ bỏ phía Python). Test: (i) unit: CF tại sm 1379 ⇒ có cổng, sm 1378 ⇒ không;
  (ii) parity 97/97 + ứng viên 100 % không đổi; (iii) đếm `Cancelled` của ReplayCorven trên TRAIN trước/sau sửa, ghi vào README (kỳ vọng về ≈ 0).
- **Q3 — ĐƯỢC.** Bảng đúng 4 dòng, không liệt kê từng lệnh; dòng 1 thêm `· k đang mở` **chỉ khi k > 0** (mã hiện đã làm vậy). Sửa 10.3: test
  dòng 1 so bằng mẫu `^BENZO CORVEN corven-1 · \d+ lệnh · WR \d+ % · [+−]\d+,\d+R( · \d+ đang mở)?$`; dòng 2–4 vẫn so đúng chữ.
- **Q4 — XÁC NHẬN C# luôn bật luật chồng range.** `overlap_max_drop` là luật **báo cáo** của Python (10.1 đã nói không port). Để không lệch
  âm thầm về sau: `parity_corven.py` in `chong_rate` và **`raise` nếu > 0,30** (khi đó Python tự tắt luật còn C# thì không — phải quyết lại, không
  được để parity "tự khớp"). Ghi vào README mục "Quyết định khi port".
- **Q5 — ĐỒNG Ý.** TIME tính thắng khi R > 0 — **trùng Python** (`results_corven.py` dòng 49: `wr = (r > 0).mean()` trên TP/SL/TIME). Test:
  1 lệnh TIME R = +0,3 ⇒ `Wins` +1, 1 lệnh TIME R = −0,2 ⇒ `Losses` +1; caption ✅/🛑 theo cùng dấu.

### 12.3 Nghiệm thu lượt sửa
Build `./build.sh` 0 cảnh báo · `dotnet run --project tests` toàn xanh (≥ 115 + test mới) · pytest toàn xanh · `parity_corven.py` 100 % không đổi,
`PARITY-CORVEN.md` không chứa R/WR của TEST · `dotnet run --project tools/TesterGd4/Gd4 -- all` **0 FAIL** (5 FAIL cũ = #2–#5 phải hết) · deploy
`qw-deploy.sh` · README cập nhật (cổng, giờ caption, công tắc, chong_rate, Cancelled) · commit tiếng Việt, chỉ `git add` file của mình, push, báo hash.
Sau đó tester GĐ4 **chạy lại (g)(h)(d)** trên bản mới, ghi phụ lục vào `TEST-CORVEN.md` — chưa chạy lại thì chưa coi là xong.

### 12.4 Việc giao Opus (một lượt, sau khi 9.3 FOLLOW-COMBO xong; thứ tự như đánh số)
1. `tools/ReplayCorven/Program.cs`: `Append` dùng `outc/rr/exs`; test C# mới (3 `Signal` giả, 2 sau cut ⇒ 3 ô rỗng). Sửa docstring.
2. `research/parity_corven.py`: (a) kiểm phần TEST của C# — ô `ket_cuc/r/exit_idx` không rỗng ⇒ `raise` + xoá thư mục tạm; (b) bỏ `cuoi_phien`
   cả hai phía trước khi so `gates`; (c) in `chong_rate`, `raise` nếu > 0,30. Pytest mới cho (a). Sửa ghi chú dòng 142/147.
3. `BenzoCore.cs` `BenzoEngine.Advance`: không `MarkRange` nến xử lý khi `!IsEnabled`; nhánh cache lấy lệnh niêm phong **bất kể** công tắc.
   Test: kịch bản tắt→bật 27/27; `rng` không phủ đoạn tắt; đang tắt vẫn vẽ lệnh cache, không gửi Telegram.
4. `BenzoTrader.cs` `LogCandidates`: xoá nhánh `setup tắt`. `BenzoCorven.GateVn`: thêm `cuoi_phien → "cuối phiên"`. Test chuỗi cổng = danh sách README.
5. `BenzoCorven.cs` cổng 4d: `if (sm >= 1379) g.Add("cuoi_phien")`. Unit test sm 1378/1379. Đếm `Cancelled` ReplayCorven TRAIN trước/sau, ghi README.
6. `BenzoZones.cs`/`BenzoKernel.SmOf`: `sm` theo UTC + 7 cố định, bỏ tham số `TzOffset`. Unit test `SmOf` không đổi theo lệch giờ; kịch bản 7→8 ⇒ 0 lệnh khác.
7. `BenzoCore.cs` `ComposeOpen/Close/Cancel`: giờ mở nến (bỏ `AddMinutes(barMinutes)`). Unit test caption 22:52 = `SignalCsv.Key`.
8. `BenzoTrader.cs` vẽ: `xE += BarsWidth/2`; hàm thuần `LabelX` + lật trái khi tràn; unit test 3 ca; Gd4 (d) nhãn đọc đủ, mũi tên tâm nến.
9. `Signal` + cache: thêm `RangeT0/RangeT1`; vẽ hộp range mờ cho lệnh đã đóng khi "Hiện range" bật; test round-trip + dòng cache cũ nạp được; `CacheVersion` giữ.
10. `tests/Program.cs` dòng 1 bảng so bằng mẫu regex (12.2-Q3); test TIME thắng/thua theo dấu R (12.2-Q5).
11. README: cổng (10.4.2 + `thế đã có lệnh`, bỏ `setup tắt`, thêm `cuối phiên`), công tắc = tạm ngừng dò, giờ caption = giờ mở nến, `chong_rate`,
    số `Cancelled`, dấu trừ ASCII trong `signs`, pytest 83 ca; sửa dòng 33/117 về `--hide-after`. Nếu 9.3 đi nhánh (b): cập nhật chuỗi trong
    `tools/TesterGd4/Gd4/Program.cs` dòng 77/406 — **không** sửa `tests/Program.cs` (của Opus 9.3).
12. `./build.sh` 0 cảnh báo → `dotnet run --project tests` → pytest → `parity_corven.py` → `Gd4 -- all` 0 FAIL → `qw-deploy.sh` → commit tiếng Việt
    (chỉ `git add` file mình sửa) → `git push origin main` → báo hash + số test + số `Cancelled` trước/sau + xác nhận `PARITY-CORVEN.md` không đổi.

## 13. corven-2 (2026-11-09) — 4 sửa đổi người học chốt sau ca bỏ lỡ 11:26 VN 09/11

Người học (chủ setup) chốt sau khi mổ ca buy 11:26: (1) thế B không cần nhịp hồi chạm cạnh — hồi không về được cạnh là phe theo hướng phá mạnh;
(2) bỏ ⛔ "nhịp đẩy do quét stop" — luật do agent diễn giải (mục 3 ghi "gần đúng"), phần ΣΔ ≤ 0 mâu thuẫn trực tiếp với trap (trap sell tạo Δ âm);
(3) thế B (đã phá range) bỏ R sẵn ≥ 1,7, TP 2R; thế A giữ; (4) agent phát hiện thêm: trap sell ở nhịp hồi (bóng đỏ 20 @4131,3, nến 11:24)
không được tính vì định nghĩa trap đòi quét mốc ⇒ thêm dấu hiệu "trap trong nhịp hồi" (thế B).
Đo TRAIN 35 phiên: 97 lệnh −0,29R → 333 lệnh −0,075R; vào ngẫu nhiên sau CF −0,079R ⇒ **ngang ngẫu nhiên, chưa có lợi thế**; 11 tổ hợp thử ⇒ hậu kiểm.
Python: `setup_corven.cp_live()` (cờ `hoi_khong_cham`, `bo_quet_stop`, `b_bo_rmin`, `trap_hoi`; mặc định CP() vẫn = corven-1).
C#: LogicVersion `corven-2`, `CorvenParams.HoiKhongCham/BoQuetStop/BBoRMin/TrapHoi`, `CorvenCfg.V1()` cho test luật cũ.
Kiểm: C# 151/151 (thêm `tests/TestsCorven2.cs`), pytest 114, Gd4 99/99 (đã cập nhật hằng), parity TRAIN 333/333 · ứng viên 14803/14803 · TEST định danh 231/231.
Bước sau: chấm corven-2 trên dữ liệu ≥ 22/10 KHÔNG sửa thêm (tiêu chí như 10.2: R TB > 0 và hơn vào ngẫu nhiên).
Số liệu: `research/report/VARIANTS-NGUOI-HOC-2026-11-09.md`.
