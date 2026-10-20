# Review 3 (vòng cuối) — plan "Trạm Đêm Vàng" bản 3 (CHECKLIST-DEM-VANG-plan.md · 20/10/2026)

Người review: Claude (Fable 5.1). Đối chiếu bản 3 với `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (**HT**), `daily-trading/RULES.md` (**RULES**), `so-tay-vang-mgc.html` (**ST**) và với review 2. Chỉ ghi chỗ chưa đạt; xếp nặng → nhẹ.

**Đối chiếu review 2:** 22 mục, **20 mục sửa đúng**. Mục 5 (cửa sổ 20:30) sửa đúng nhưng để lộ mâu thuẫn lớn hơn ở `DIS_BEFORE_2030` (#1). Mục 1 (`pending`) sửa đúng ý nhưng mã `DIS_PENDING_ACCEPT` đặt sai tầng (#2). Mục 21 còn thiếu chữ "ENTRY" (#13). Mục 22 còn sót "Mục 11 và 12" (#18).

---

## A. SAI LUẬT / TEST KHÔNG THỂ XANH

1. **[NẶNG] `DIS_BEFORE_2030` tắt A, B, D trước 20:30 — giết cả 3 ca thật mà plan bắt test phải ra ENTRY/CHỜ.**
   Bảng bật (tầng 2): *"Trước 20:30 (mùa đông 21:30) | `DIS_BEFORE_2030` | `DIS_BEFORE_2030` | bật, ½ | `DIS_BEFORE_2030`"*. Mục 6 test: *"6/10 **20:24** A … ⇒ ENTRY"*, *"13/10 **20:10** B … ⇒ ENTRY ½"*, *"5/10 **19:25** B với B2 lẫn lộn ⇒ CHỜ"*. Cả ba trước 20:30 ⇒ theo bảng bật, A/B không chọn được ở C1 ("chỉ thẻ đang bật"), phán quyết không thể là ENTRY hay CHỜ.
   Gốc là HT tự mâu thuẫn: HT 3.2 *"Trước 20:30 chỉ fade cạnh, cỡ nhỏ"* và HT 5·C *"Trước 20:30 đây là kịch bản duy nhất được bật"* — nhưng HT 0 lại ghi *"Ba lệnh +3R tốt nhất (13/10 20:10 · 6/10 20:24 · 5/10 21:36)"*: hai trong ba là A/B trước 20:30, và HT 3.2 cũng nói *"cú phá đáng tin thường rơi vào 20:20–21:30"*. Plan chưa phân xử.
   **Sửa (tối thiểu):** thêm **QĐ-19**: *"Trước 20:30 (đông 21:30): KHÔNG tắt A/B/D (HT tự mâu thuẫn; ưu tiên 3 ca thật). Thay bằng cảnh báo vàng 'trước 20:30 — mở ảo (HT 3.2)' + **cỡ ½** cho A/B/D (C vốn đã ½). Chưa đo."* Bỏ hàng `DIS_BEFORE_2030` khỏi bảng bật, thay bằng cờ `half` lý do `BEFORE_2030`; sửa test 6/10 thành "ENTRY, **cỡ ½** (QĐ-19)", thêm 3b vào danh sách ½: "trước 20:30". Nếu vẫn muốn giữ luật tắt thì phải đổi cả 3 test thành `DIS_BEFORE_2030` và ghi rõ trong QĐ rằng plan bỏ 2/3 ca ĐÚNG của HT — không được để cả hai như hiện nay.

2. **[NẶNG] `DIS_PENDING_ACCEPT` (và một phần hàng `balanced`) phụ thuộc vùng, nhưng `enabled:{A..D: code|null}` được tính ở tầng 2 trước khi chọn vùng, và thứ tự engine đặt `DIS_*` trước bước vùng.**
   Bảng bật, hàng `pending`: B *"như `balanced`, nhưng **tại cạnh vừa phá** ⇒ `DIS_PENDING_ACCEPT`"*; C *"**tại cạnh vừa phá** ⇒ `DIS_PENDING_ACCEPT`; cạnh khác: bật"*. Mục 5: *"chế độ × kịch bản (`DIS_*`) → hướng vs bias → vùng (…)"*. Mục 6: *"C tại cạnh đó ⇒ `DIS_PENDING_ACCEPT`; C tại cạnh khác ⇒ bật"*. Một mã vừa là lý do mờ thẻ (không có vùng) vừa là lý do KHÔNG VÀO ở C3 (có vùng) ⇒ Sonnet phải tự chọn: tính `enabled` theo vùng (thì tầng 2 chưa có vùng) hay tách thành hai mã.
   **Sửa:** tầng 2 (không vùng): `pending` ⇒ A `DIS_PENDING_ACCEPT`; B, C **bật** (thẻ ghi "trừ cạnh vừa phá"); D `DIS_NO_MOVE`. Tầng 3, bước vùng: `(regime = pending) ∧ (zoneId = breakout.edgeZoneId)` với B hoặc C ⇒ **`NO_PENDING_ACCEPT`** (effect NO). Sửa test mục 6 theo: "C tại cạnh đó ⇒ `NO_PENDING_ACCEPT`". Ghi vào mục 5 nguyên tắc: *"`DIS_*` chỉ phụ thuộc (bias, chế độ, giờ, thẻ); mọi luật cần vùng/hướng là `NO_*`."*

3. **[NẶNG] Ba luật có hiệu lực nhưng không có mã — Sonnet sẽ tự đặt tên, test không so được.**
   (a) Mục 5: *"vùng (…, **hạng cho B**)"* — B tại vùng không đạt hạng theo QĐ-3 (vd B cùng bias tại VAH Âu khi `broken`, B tại poor high) không có mã. Test *"B ngược bias tại VWAP tuần (không cờ) ⇒ NO"* không nói mã.
   (b) Mục 5: *"hướng vs bias (`NO_COUNTER_BIAS_*`)"* — dấu `*`; chỉ `NO_COUNTER_BIAS_SCENARIO` (A, C, D) được đặt tên. B ngược bias không cờ, hoặc cờ `sp`/`tail` **sai phía** (test *"cờ `sp` sai phía ⇒ NO"*) chưa có mã.
   (c) C2 *"Tự điền: A = chiều phá; D = chiều bias; C = theo cạnh … **Sửa được**"* — A sửa thành ngược chiều phá, C sửa thành hướng ra ngoài range, D ngược bias: không mã nào bắt (QĐ-9 chỉ nói A/C/D ngược **bias**).
   **Sửa:** thêm `NO_B_RANK` ("vùng này không đủ hạng cho hấp thụ — QĐ-3") và `NO_COUNTER_BIAS_ZONE` ("ngược bias chỉ tại tail thật / single print đúng phía — HT 2.2"); liệt kê đủ trong mục 5 thay dấu `*`. **Khóa C2** cho A, C, D (chỉ B chọn hướng): hết ca (c), và thao tác A/C/D không đổi. Thêm 2 test cho 2 mã mới.

4. **[NẶNG] Chế độ Trend thin không có hướng trong dữ liệu ⇒ "bật cùng chiều" của A, D và C2 tự điền cho D không kiểm được; `broken` ngược bias chưa có hàng trong bảng bật.**
   Bảng bật: `thin` ⇒ A *"bật ở nhịp hồi, cùng chiều"*, D *"bật cùng chiều"*; C2: *"D = chiều bias"*. Mô hình dữ liệu: `regime: {mode, breakout:{dir,…}}` — `breakout.dir` chỉ có khi Vừa phá; `thin` không có hướng. Trend thin ngược bias (vd bias BUY, trend thin xuống) ⇒ D tự điền buy = cản tàu.
   `broken` ngược bias: A tự điền = chiều phá ⇒ ngược bias ⇒ `NO_COUNTER_BIAS_SCENARIO` ở tầng 3, nhưng thẻ A ở tầng 2 vẫn **sáng** (HT 5·A bối cảnh: *"Bias cùng chiều phá"*).
   **Sửa:** `regime.thinDir: 'up'|'down'` (bắt buộc khi chọn Trend thin). Thêm hàng bảng bật: *"`broken`/`thin` ngược chiều bias ⇒ A, D `DIS_BREAK_AGAINST_BIAS`; B theo QĐ-4/QĐ-9; C `DIS_M5_OUTSIDE`"*. C2 của D = `breakout.dir` (broken) / `thinDir` (thin), không phải bias. Thêm 2 test (broken xuống + bias BUY ⇒ A mờ; thin xuống + bias BUY ⇒ D mờ).

## B. MÂU THUẪN / MƠ HỒ BẮT SONNET TỰ CHỌN

5. **[VỪA] Bảng bật không nói hàng là "khớp đầu tiên thắng" hay "cộng dồn", và thứ tự khác mục 5.**
   Tiêu đề bảng: *"Điều kiện (thứ tự ưu tiên từ trên xuống)"*. Nếu đọc là "khớp đầu tiên thắng": *Bias KHÔNG ⇒ C **bật** 2R ½* dừng tại đó ⇒ bias KHÔNG + `broken` vẫn bật C, trái HT 5·C *"đã sang chế độ vừa phá ⇒ loại bỏ"*; tương tự *Trước 20:30 ⇒ C bật* + thẻ không có cạnh ⇒ không bao giờ tới `DIS_NO_EDGE`.
   Thứ tự: bảng bật = Bias CHỜ → Khóa 3′ → Bias KHÔNG → …; mục 5 = *"`DIS_LONGEST_BAR` → thẻ phiên / `DIS_BIAS_WAIT` → `DIS_BIAS_NONE`"* (khóa 3′ trước CHỜ). Mã hiện trên thẻ sẽ khác nhau tùy Sonnet đọc bảng hay mục 5.
   **Sửa:** ghi dưới bảng: *"Duyệt **mọi** hàng từ trên xuống; ô 'bật' nghĩa là hàng này không tắt, xét tiếp; mã **đầu tiên** tắt là mã hiển thị."* Chọn một thứ tự (đề nghị theo mục 5: khóa 3′ trước bias, vì khóa 3′ là luật cứng HT 7) và sửa bảng cho khớp.

6. **[VỪA] "Vùng loại cạnh" trong QĐ-1 và cờ `edge` ở 1d không trùng nhau ⇒ B cùng bias tại High/Low hôm qua khi Cân bằng: được hay không?**
   QĐ-1: *"Cân bằng ⇒ B chỉ tại **vùng loại cạnh**, hoặc vùng hạng 1–2 trùng cạnh"*. 1d gắn cờ `edge` cho cả hàng *"VAH Âu · VAL Âu · cạnh range · IB high · IB low"* **và** hàng *"High hôm qua · Low hôm qua | cạnh (ngoài) | C, A, D; **B chỉ ngược bias theo QĐ-9**"*. Nếu engine đọc "vùng loại cạnh" = `flags ∋ 'edge'` thì B cùng bias tại High hôm qua được bật (trái 1d); nếu đọc theo hàng thì trái QĐ-1. HT 5·B chỉ nói *"cạnh VA Âu khi đang cân bằng"*.
   **Sửa:** tách cờ: `edge` chỉ cho hàng VAH/VAL Âu · cạnh range · IB; High/Low hôm qua mang cờ `edgeOuter` (C được; A, D được; B chỉ QĐ-9). QĐ-1 viết rõ *"vùng loại cạnh = cờ `edge`"*. Thêm 1 test: B buy cùng bias tại Low hôm qua, `balanced` ⇒ `NO_B_RANK`.

7. **[VỪA] A không bị buộc vào đúng cạnh vừa phá.**
   HT 5·A kiểm tra: *"Hồi hình U về **cạnh vừa phá**"*. Plan 1d cho A tại VWAP tuần, VWAP ngày, HVN tuần, cụm POC, LVN… không điều kiện; C3 không so `zoneId` với `regime.breakout.edgeZoneId`. Ca 6/10 chỉ khớp vì người dùng tự chọn đúng vùng.
   **Sửa:** A ⇒ C3 **tự điền** = `breakout.edgeZoneId`, không sửa (A Canh còn 4 thao tác; cập nhật số đếm A 4/5 ở 3a, mục 10 dòng 15 và e2e). Nếu muốn giữ cho chọn thì thêm `NO_A_NOT_BREAK_EDGE`.

8. **[VỪA] Mô hình dữ liệu: `open` không giữ ảnh chụp của kèo, `trades` không có `id`, lệnh qua đêm không chỉ ra cách tìm.**
   `open:{status, side, scenario, zoneId, entryPlanned, entry, sl, tp, rrPlanned, size, beAt, beDone, outsideZoneBar, openedAt}` — thiếu `tests`, `mode`, `slDist`, `slPos`, `flags`, `ruleCodes`, `counterBiasReason`, `c6`. Dòng sổ chỉ được viết khi đóng (*"Dòng sổ hoàn tất"*), lúc đó `setup` có thể đã bị "Kèo mới" xóa hoặc phán quyết đã đổi theo giờ (cửa sổ cấm, khóa 3′) ⇒ "Tôi vẫn vào" ghi mã nào?
   `trades[]` không có `id` ⇒ *"nhập JSON gộp theo đêm, không trùng"* không có khóa để so trùng. *"Lệnh còn mở qua mốc đêm mới ⇒ vẫn thuộc đêm vào lệnh; đêm mới mở ở tầng 4"* — engine `(night, now)` chỉ nhận một đêm, không thấy `open` của đêm trước.
   **Sửa:** khi bấm "Vào lệnh"/"Tôi vẫn vào" ⇒ tạo ngay dòng `trades` (có `id`, `exit: null`, chụp `tests`, `mode`, `flags`, `ruleCodes`, `counterBiasReason`, `slDist`, `slPos`) và `open = {tradeId, status, beAt, beDone, outsideZoneBar}`. Engine nhận `(nights, nightKey, now, settings)` (cần `settings.dstShift`, `capital`, `riskPct` — chữ ký hiện tại `(night, now)` thiếu). Gộp JSON: khóa `trades.id`; đêm trùng thì giữ bản có `tally.closedAt` mới hơn.

9. **[VỪA] Test "ca thật tái hiện" chưa đủ số để chạy một mình.**
   6/10: không có danh sách vùng trong thẻ ⇒ `NO_TP_PAST_ZONE` (QĐ-16) có kích hay không tùy Sonnet đặt vùng; không có `breakout.at` ⇒ `DIS_EARLY_BREAK` có thể kích; không có Q1/Q5/VWAP ⇒ bias phải "ghi đè". 1/10: *"SL ≈4194,8 đặt ngay tại VWAP tuần"* (HT) ⇒ B5 = "sai chỗ" sẽ ra `NO_SL_POS` **trước** `NO_SL_FLOOR` theo thứ tự mục 5, test lại đòi "một mã". 13/10: HT ghi vùng là *"LVN ngày + POC hôm qua"* (một POC), plan ghi *"cụm POC trùng VAL Âu"* — là ca dựng theo luật, không phải tái hiện; QĐ-3 lại dẫn *"bằng chứng 13/10"* cho định nghĩa cụm ≥ 2 POC.
   **Sửa:** thêm phụ lục "fixtures" cho 5 ca: thẻ (Q1, Q5, VWAP, bias), danh sách vùng đầy đủ (loại · giá · cờ), `regime` (mode, dir, edgeZoneId, at, step1/2), giờ, mọi C/B. 1/10 ghi B5 = "đúng chỗ" (test cô lập sàn nhiễu) hoặc đổi kỳ vọng thành `reasons = [NO_SL_POS, NO_SL_FLOOR]`. 13/10 đổi nhãn "ca dựng từ 13/10"; QĐ-3 sửa "bằng chứng 13/10 (HT ghi 'POC hôm qua', chưa rõ là cụm)".

10. **[VỪA] Lint chữ chưa chạy được như mô tả.**
    Mục 6: *"từ tiếng Anh ngoài danh sách 4.11"* — không nói cách nhận ra một từ là tiếng Anh (tiếng Việt không dấu cũng là chữ Latin: "ban", "con", "kho"). *"Cấm: 'bán'/'mua' **cho hướng lệnh**"* — lint không biết ngữ cảnh. Thanh phán quyết in **"ENTRY"** (mục 3, 3c, 4.2) nhưng "ENTRY" không có trong 4.11 ⇒ đỏ ngay vòng 1. Không nói lint phân biệt hoa/thường ("SELL" trong thanh ENTRY vs "sell").
    **Sửa:** (a) cấm **tuyệt đối** hai từ "bán", "mua" trong `content.js` (dùng "phe sell / phe buy" — đúng quy ước người dùng); (b) định nghĩa phát hiện: token chỉ gồm `[A-Za-z]` dài ≥ 3 **hoặc** toàn chữ hoa ≥ 2, không có trong 4.11 và không có trong `scripts/vi-khong-dau.txt` (danh sách từ Việt không dấu hay gặp, Sonnet tạo và bổ sung khi lint báo sai); so không phân biệt hoa/thường; (c) thêm "ENTRY" vào 4.11.

## C. THIẾU NHỎ / NHẸ

11. **[NHẸ] HVN ngày mang cờ `banned` ⇒ bị gom vào "VÙNG CẤM" của thẻ phiên, trái mẫu HT 8 (*"VÙNG CẤM: (HVN 3 tuần, LVN)"*).** 1e: *"VÙNG CẤM (gom các vùng `banned`)"*; 1d HVN ngày: `banned`. **Sửa:** HVN ngày dùng cờ `noB` (chỉ chặn B), `banned` giữ cho HVN 3 tuần · LVN; thẻ gom `banned`.

12. **[NHẸ] Hai mã lý do mờ sai nghĩa ở chế độ Trend thin.** B ⇒ `DIS_USE_D` ("cùng chiều ở nhịp hồi ⇒ gọi là D") — nhưng B **ngược** chiều trend cũng bị tắt bằng mã này, lý do thật là "cản tàu" (HT chế độ 3). C ⇒ `DIS_M5_OUTSIDE` — ở thin không có "nến M5 đóng ngoài", lý do là *"không fade đỉnh"*. **Sửa:** chữ của `DIS_USE_D` trong `content.js`: "Trend thin: cùng chiều ⇒ dùng D; ngược chiều = cản tàu"; C ở thin ⇒ mã riêng `DIS_THIN_NO_FADE`.

13. **[NHẸ] C2 tự điền cho C cần phía của cạnh, nhưng loại "cạnh range" không có phía; C2 đứng trước C3 trong bảng 3a dù phụ thuộc C3.** `zones[].side` chỉ nói cho single print. **Sửa:** "cạnh range" bắt chọn phía (trên/dưới) như single print; ghi chú ở 3a: "C2 điền sau khi chọn C3".

14. **[NHẸ] Cách đếm lần tại vùng viết lệch một đơn vị.** C3: *"lần thứ n (QĐ-17; n = 3 ⇒ `NO_ZONE_3RD`)"* còn QĐ-17: *"n = số dòng `trades` trong đêm cùng `zoneId`"* (số lần **đã** vào). **Sửa:** "hiện 'lần thứ n+1'; `NO_ZONE_3RD` khi n ≥ 2".

15. **[NHẸ] Phạm vi chuỗi SL, đếm phá luật và trạng thái TẮT MÁY chưa nói là theo đêm.** HT 7: *"Lệnh phá luật **trong phiên** 2 ⇒ tắt máy"*. Plan QĐ-10/QĐ-17 không nói chuỗi SL có reset khi sang `nightKey` mới không, TẮT MÁY kéo dài tới khi nào. **Sửa:** một dòng ở 3c: "Chuỗi SL, đếm phá luật, TẮT MÁY tính trong một `nightKey`; đêm mới về 0."

16. **[NHẸ] Kèo luyện mắt (`paper`) có đi qua tầng 4 không?** 0.1: *"nút thành 'Ghi kèo luyện mắt' (vào sổ với cờ `paper`)"* — không nói có tạo `open`, có khóa tầng 3, có nhập giá thoát để ra R không. **Sửa:** "đi đúng đường tầng 4 như lệnh thật (để có R), chip 'lệnh mở (luyện mắt)', không cộng gì (QĐ-17)".

17. **[NHẸ] Giờ: thiếu mốc London trở lại 28/03/2027; câu `nightKey` viết sai múi; `nth` phá không dùng ở đâu.** Mục 3: *"mốc Globex mở (**05:00 ET** hè / 06:00 đông, giờ VN)"* — 05:00 là giờ VN, mốc gốc là **18:00 ET**. Mục 6 chỉ test 13/03, 14/03/2027. `breakout.nth` (lần 1/2) không có luật nào dùng. **Sửa:** viết "18:00 ET = 05:00 VN hè / 06:00 VN đông"; thêm 27/03, 28/03/2027 vào test; ghi `nth` "chỉ hiển thị, nhắc 'lần 1 chui lại ⇒ không đuổi' (HT 3.2)".

## D. CHỮ

18. **[CHỮ]**
    - Dòng 4: *"Mục 11 và 12 cuối file ghi…"* — các mục đó giờ là **9 và 10**.
    - Sơ đồ mục 3: *"cửa sổ cấm kế: **00:00** (2h46′)"* — không có cửa sổ 00:00 nào trong 0.2 (FOMC 01:00, nhắc 00:45); đổi thành "01:00" hoặc "21:00".
    - 1e: *"Thẻ phiên … **tự điền** đúng mẫu HT 8: … Kế hoạch 1 / Kế hoạch 2 … Hủy kế hoạch khi …"* — ba ô này là chữ người dùng gõ, không tự điền; ghi "(tùy chọn, người dùng gõ)".
    - QĐ-16 chỉ nói 3R (A, B) / 2R (C, D); với B ngược bias (QĐ-9 ép 2R) cần một vế: "B theo QĐ-9: 2R".
    - 4.11 thiếu "ENTRY" (xem #10).
    - Tầng 2 dải giờ: *"19:20–20:30 'mở ảo', 20:20–21:30 'cú phá đáng tin'"* — hai dải chồng 20:20–20:30 trên một thanh trạng thái; chọn một mốc hiển thị (20:20).
    - Mục 6, sổ: cột "V/U" cho kịch bản C (B1 ẩn) in gì — ghi "—" hoặc "cạnh".
    - `content.js` cần trường `htRef` cho mỗi mã (vd `NO_V_PULLBACK` → "4.1") để dòng ⚠ in được *"phạm 4.1, 4.3 và luật SL"* đúng mẫu HT 8 — hiện chưa nói.

---

## Kết luận

- **ĐỦ ĐỂ IMPLEMENT CHƯA: Chưa.** Còn một mâu thuẫn làm 3/5 test ca thật không thể xanh (#1) và ba lỗ hổng bắt Sonnet tự đặt mã/luật (#2, #3, #4); các mục còn lại Sonnet có thể đoán nhưng kết quả sẽ lệch giữa engine, bảng bật và test.
- **Sửa tối thiểu trước khi giao Sonnet:** #1 (QĐ-19 + sửa 3 test) · #2 (`NO_PENDING_ACCEPT` ở bước vùng, nguyên tắc `DIS_*` không phụ thuộc vùng) · #3 (`NO_B_RANK`, `NO_COUNTER_BIAS_ZONE`, khóa C2 cho A/C/D) · #4 (`regime.thinDir`, hàng `DIS_BREAK_AGAINST_BIAS`) · #5 (ngữ nghĩa "cộng dồn" + một thứ tự) · #8 (`trades.id`, tạo dòng sổ lúc vào lệnh, chữ ký engine) · #9 (phụ lục fixtures 5 ca).
- Các mục #6, #7, #10–#18 sửa cùng lượt, mỗi mục một dòng; không cần vòng review 4 nếu 7 mục trên sửa đúng.
