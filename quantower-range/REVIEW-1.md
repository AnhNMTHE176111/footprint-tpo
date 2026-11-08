# Review vòng 1 (Fable, 2026-11-08) — Range Box sau khi agent triển khai xong

Đã tự chạy lại: tests 42/42 PASS · build 0 cảnh báo · tests-dll PASS · `events_90d.csv` = `events_90d_cs.csv` (md5 khớp).
Đã đọc `RangeLogic.cs`, `RangeBox.cs`, `RangeRenderer.cs`, `MEASURE.md`, `README.md`, 7 PNG.

## Đánh giá chung
- Logic bám đúng BRAINSTORM 4 + 7b. Điểm hay: `_scanStart` = nến phá ⇒ range kế có thể bắt đầu đúng nến phá range trước
  (khớp B13→B14, B10→B11 của CORVEN). Cạnh kẹp trong ±tol quanh giá trị lúc sinh ⇒ hộp không trôi.
- Đo đạc trung thực: không có lợi thế ⇒ README nói thẳng. Đúng yêu cầu.
- Hình: hộp/tam giác/chấm đúng quy ước; tooltip ngắn; zoom 3 px vẫn đọc được.

## PHẢI SỬA trước khi deploy
1. **Tooltip hộp bật quá dễ.** `boxHits` nhận cả diện tích hộp ⇒ chuột ở bất kỳ nến nào trong range cũng hiện khung chữ,
   che chart. Chỉ bắt khi chuột **cách cạnh trên hoặc cạnh dưới ≤ 5 px** (và trong khoảng x của hộp). Với hộp đã phá, áp
   dụng cả đoạn chấm kéo dài. Cập nhật PNG `7-tooltip-mep-phai` + thêm PNG chuột ở giữa hộp (phải KHÔNG có tooltip).

## PHẢI KIỂM (bằng ilspycmd trên `~/quantower-libs/TradingPlatform.BusinessLayer.dll`, như đã làm với IndicatorWrapper)
2. `Indicator.OnBackGround`: có thật, ý nghĩa là vẽ **dưới** nến? Nếu không, bỏ và ghi chú.
3. `HistoricalData[i, SeekOriginHistory.Begin]`: i = 0 là nến **cũ nhất**? Trong lúc nạp lịch sử (`UpdateArgs.Reason == HistoricalBar`)
   `HistoricalData.Count` là tổng số nến hay tăng dần? Ghi kết luận vào BUILD.md (logic tất định nên cả hai đều đúng,
   nhưng phải chắc nến cuối cùng không bị bỏ sót khi chuyển sang live).
4. `IChartWindowCoordinatesConverter.GetBarIndex(time)`: trả chỉ số tính từ nến cũ nhất (khớp `SeekOriginHistory.Begin`)? OrderFlowBubbles
   dùng cùng cách và chạy được, chỉ cần xác nhận lại 1 dòng.

## PHẢI TEST THÊM (adversarial — cố làm hỏng)
5. mbr = 0 (100 nến doji H==L) ⇒ không sinh range, không chia 0, không ngoại lệ.
6. Nến gap: close nhảy xuyên cả hộp (đóng ngoài cạnh đối diện ngay từ Active) ⇒ CloseOutside phía đó, không crash; xuyên hộp lúc Pending ⇒ FailBreak + CloseOutside phía ngược (đã có nhánh, cần test).
7. Đỉnh bằng nhau (plateau H[j]==H[j−1]) ⇒ không pivot (đúng với `>`), nhưng range vẫn sinh được nhờ nến khác; test một chuỗi
   toàn đỉnh bằng nhau để xem có sinh range không và kết quả có hợp lý không.
8. Ít hơn 100 nến ⇒ không range; đúng 100 ⇒ bắt đầu xét.
9. Tick 0,25 (NQ) và 0,01: chạy chuỗi GC nhân/chia thang + đổi tick ⇒ cùng sự kiện (đã có ×10, thêm 0,25 và 0,01).
10. Chuỗi 500 nến sinh ngẫu nhiên (seed cố định) ×20 seed: so Feed từng nến vs Process một mạch ⇒ giống hệt; không ngoại lệ.
11. ReEntry nhiều lần: range sống mãi? Trên 90 ngày, in phân bố **tuổi thọ** (Start→Dead, nến) p50/p90/max và tỷ lệ range có ≥2 ReEntry.
    Chỉ BÁO CÁO, không đổi logic (hộp CORVEN dài nhất 73 nến; tôi sẽ quyết sau khi thấy số).
12. Render: 1 range có 3 fail break liên tiếp cùng phía + 2 râu quét ⇒ dấu không đè lên nhau thành một cục? Render PNG.
    Hộp hiệu lực bắt đầu ngoài mép trái màn hình (Start < li) ⇒ vẫn vẽ phần nhìn thấy, không vẽ x âm lố (đã có `li−1`, chụp PNG xác nhận).
13. `OnClear` giữa chừng rồi `OnUpdate` lại ⇒ kết quả giống chạy mới (test phản chiếu đã có một phần; thêm: nạp 300 nến → Clear → nạp lại 300 ⇒ events giống).

## Không sửa (đã cân nhắc)
- Chỉ một range Active/Pending tại một thời điểm: đúng ý CORVEN "range chồng range thì khó" — không cố vẽ chồng.
- 17 range/ngày trên M1 ≈ CORVEN ~10/ngày (20 hộp/2 phiên): chấp nhận, hộp đã phá vẽ mờ nên không rối.
- Không thêm Settings.

## Kết quả tester (agent độc lập, 2026-11-08)
Chạy cuối: `tests` **111 OK / 0 FAIL** (43 ở file cũ — thêm PNG 7b — + 68 mới trong `tests/AdversarialTests.cs`) · `build.sh` **0 cảnh báo** · `tests-dll` **PASS**
(thêm 6 kiểm vòng đời thật của `RangeBox.Process` bằng `HistoricalData` giả) · `events_90d_cs.csv` = `events_90d.csv` (md5 `71181e84…`, **không đổi**).

| Mục | Kết quả | Ghi chú |
|---|---|---|
| 1 Tooltip hộp | **ĐÃ SỬA** | `RangeRenderer.BoxHit`: chỉ bắt khi chuột cách cạnh trên/dưới ≤ `EdgeHitPx` = 5 px trong khoảng x của hộp; hộp đã phá bắt thêm nét chấm retest. Test pixel A1 (giữa hộp, cách 9 px, ngoài x → không; cách 3–4 px, nét chấm → có). PNG `7-…` (chuột trên cạnh) + `7b-chuot-giua-hop-khong-tooltip.png`. API `Draw` giữ nguyên. |
| 2 `OnBackGround` | PASS | Có thật, = vẽ dưới nến (chi tiết + tên hàm trong BUILD.md "Đã kiểm API"). |
| 3 `HistoricalData` | PASS | `Begin` 0 = cũ nhất; `Count` = tổng (không tăng dần); NewBar không bỏ sót nến — test thật ở tests-dll. |
| 4 `GetBarIndex` | PASS | Tính từ nến cũ nhất, ngoại suy âm/vượt cuối. |
| 5 mbr = 0 | PASS | 300 doji (phẳng và zigzag): 0 range, không ngoại lệ. |
| 6 Gap xuyên hộp | PASS | Active→CloseOutside phía close; Pending→FailBreak + CloseOutside ngược cùng nến; BreakConfirmed ref đúng. |
| 7 Plateau | PASS (có giới hạn) | Đỉnh plateau 2 nến: vẫn sinh range, cạnh đúng. **Toàn bộ vùng cùng một high: 0 range** (chỉ nến đầu vùng là pivot ⇒ không đan xen) — giới hạn của luật pivot `>`, chỉ báo cáo. |
| 8 <100 / =100 nến | PASS | 99 nến: 0 range; 100 nến: range sinh đúng nến chỉ số 99. |
| 9 Tick 0,25 / 0,01 | PASS | Tổng hợp ở tick 0,25 / 0,01 / 1 / 0,0001 và GC 90 ngày đổi thang sang 0,25 / 0,01: cùng sự kiện. |
| 10 Ngẫu nhiên 20 seed | PASS | Process = Feed từng nến (xen BuildScene) = FeedTicks; 20 seed có sinh range. |
| 11 Tuổi thọ | BÁO CÁO | Số liệu bên dưới. |
| 12 Render | **ĐÃ SỬA** một phần | 3 FB + 2 râu quét: 10 px không đè; **3 px: 2 chấm râu quét liền nhau dính nhau** ⇒ hạ bán kính chấm tối thiểu 2→1 px (chỉ đổi hình khi < 5,7 px/nến). 1 px/nến vẫn đè (tam giác tối thiểu 4 px) — chấp nhận. Hộp Start < li: phần nhìn thấy vẫn vẽ, không lố ra ngoài clip. |
| 13 Clear giữa chừng | PASS | Logic: nạp 170 → bỏ → nạp lại 300 = chạy mới; tests-dll: OnClear→OnUpdate trên RangeBox thật = chạy mới. |

### Số liệu mục 11 (GC M1 90 ngày, 86.333 nến, bộ tham số mặc định)
- 1.363 range (1.362 đã chết, 1 còn sống cuối dữ liệu).
- Tuổi thọ Start→Dead: **p50 71 · p90 145 · max 406 nến** (Dead = 30 nến sau lần phá cuối không quay lại, nên luôn ≥ độ dài hộp + 30).
- Độ dài hộp vẽ Start→nến phá cuối: **p50 42 · p90 116 · max 377 nến**; **361 hộp (26,5 %) dài hơn 73 nến** (hộp CORVEN dài nhất).
- ReEntry: ≥1 lần **63,0 %** range · ≥2 lần **38,1 %** (519 range) · nhiều nhất **21 lần** trên một range.
  ⇒ ReEntry làm range "sống dai": hộp p90 gấp ~1,6 lần hộp CORVEN dài nhất. Chưa đổi logic (chờ quyết).

### Lỗi tìm được ngoài danh sách (ca tự nghĩ)
| Ca | Bắt được lỗi? | Xử lý |
|---|---|---|
| E1 Nến NaN / +∞ (HistoryItemBar mặc định NaN) | **CÓ** — `(long)Math.Round(NaN)` = 0 ⇒ close 0 ⇒ CloseOutside + FailBreak giả, range đang hiệu lực bị "phá"; high = +∞ ⇒ StopHunt giả. | `RangeLogic.Feed`: giá không hữu hạn thay bằng close trước (vẫn chiếm 1 chỉ số nến, khớp chart). |
| E2 Nến hỏng high < low | Không (kết quả trùng nến đã đổi chỗ) | Vẫn thêm chuẩn hoá high = max, low = min của OHLC trong `FeedTicks` (90 ngày GC: 0 nến vi phạm ⇒ không đổi events). |
| E3 Giá âm / dời chuỗi ±N tick | Không | — |
| E4 Giá không chia hết tick (±0,3–0,4 tick) | Không | — |
| E5 1 triệu nến | Không | Nạp ~3,7 s, 9.018 range; BuildScene ~0,1 ms/khung. |
| E6 Giảm `MbrLen` giữa chừng | **CÓ** — cửa sổ median không co (mỗi nến vào 1 ra 1). Không xảy ra trong RangeBox (không đổi tham số lúc chạy). | `PushRange`: `if` → `while`. |
| E7 Vẽ với toạ độ hỏng (Y NaN/∞, x −1e9, x +1e12) | **CÓ** — x = +1e12 ⇒ GDI+ `OverflowException`. | Kẹp x hộp/nét chấm vào [clip−50, clip+50]; bỏ dấu có Y không hữu hạn. |
| E8 Chuột trúng cả ▼ lẫn cạnh hộp | Không — dấu được ưu tiên đúng | — |
| E9 Tham số biên (K=0/1, G=0, MaxLook 3, MbrLen 1, luật B) | Không ngoại lệ | — |
| `MousePosition` = `Point.Empty` khi chưa rê chuột (ilspy) | **CÓ** (nhỏ) — trước đây coi như chuột ở (0,0). | `RangeBox.cs` truyền `null` khi `Point.Empty` hoặc chuột ngoài vùng chart. |

PNG mới: `tests/ui-out/7-tooltip-mep-phai.png` (cập nhật), `7b-chuot-giua-hop-khong-tooltip.png`, `8-fail-break-lien-tiep-{10,3,1}px.png`,
`9-hop-tran-mep-trai.png`; số liệu mục 11 cũng ghi ở `tests/ui-out/a11-tuoi-tho.txt`.

### Sau MaxReEntry=2 (quyết định mục 11, 2026-11-08)
Luật: lần BreakConfirmed thứ 3 ⇒ Dead ngay (không chờ G), không ReEntry, Merge không hồi sinh; `_scanStart` vẫn = nến phá.
Sửa giống hệt `research/range_proto.py` + `RangeLogic.cs` (`RangeParams.MaxReEntry = 2`, `< 0` = không giới hạn). Chạy lại `measure.py` (93 job,
thêm quét MaxReEntry {−1, 1, 3}); dòng `MaxReEntry=-1` trùng khớp từng số với bộ chọn cũ ⇒ chỉ luật mới làm đổi kết quả.
`events_90d.csv` = `events_90d_cs.csv` (md5 `9dbcf898…`, 19.921 sự kiện; MEASURE.md cũ ghi 22.474 dòng). Tests cuối: 121 OK / 0 FAIL · build 0 cảnh báo · tests-dll PASS.

5 chỉ số bộ chọn mới (H1 / H2 / G748):
1. range/ngày 19,4 / 19,9 / 18,2 (cũ 17,2 / 17,7 / 15,9); cao trung vị 38 / 36,5 / 27 tick; lõi tới phá đầu 20 / 20 / 20 nến.
2. râu quét · fail · phá mỗi range: 2,8·2,0·2,0 / 3,1·1,9·2,1 / 3,1·2,1·2,1 (cũ 3,5·2,5·2,6 / 3,9·2,5·2,6 / 4,2·2,8·2,8).
3. P chạm cạnh đối diện trước phá 0,50 / 0,52 / 0,51; EV R≥1,7 trước / sau 2 tick phí −0,058/−0,22 · −0,034/−0,20 · −0,036/−0,27 (vẫn không có lợi thế).
4. P đi ≥1× cao sau phá 0,71 / 0,66 / 0,69.
5. Số fail break 1.515 / 1.501 / 26.578.

Tuổi thọ mới (90 ngày, 1.533 range): Start→Dead **p50 60 · p90 93 · max 302 nến** (cũ 71/145/406); hộp vẽ p50 40 · p90 83 · max 300;
**> 73 nến: 240 hộp = 15,7 %** (cũ 26,5 %); ReEntry ≥2 lần **38,9 %** (= đúng 2, tối đa 2; cũ 38,1 %, max 21).
Lưu ý: hộp dài nhất vẫn 300 nến — range sống lâu trong lòng hộp (ít phá) thì MaxReEntry không cắt; muốn chặn phải thêm luật khác.
Test mới A14 (7 kiểm): phá→ReEntry→phá→ReEntry→phá lần 3 ⇒ Dead + Exhausted ngay; đóng lại trong hộp không ReEntry; đi ngang lại đúng cạnh cũ ⇒
sinh range mới (không Merge); range mới phía trên bắt đầu từ vùng nến phá; MaxReEntry=−1 giữ hành vi cũ; một mạch = từng nến. tests-dll kiểm MaxReEntry = 2.
