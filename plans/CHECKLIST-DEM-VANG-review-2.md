# Review 2 — plan "Trạm Đêm Vàng" bản 2 (CHECKLIST-DEM-VANG-plan.md · 20/10/2026)

Người review: Claude (Fable 5.1). Đối chiếu bản 2 với `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (**HT**), `daily-trading/RULES.md` (**RULES**), `so-tay-vang-mgc.html` (**ST**) và với review 1. Chỉ ghi chỗ chưa đạt; mục review 1 đã sửa đúng không nhắc lại. Xếp nặng → nhẹ.

Tóm tắt đối chiếu review 1: 39 mục, **33 mục sửa đúng**. Chưa đạt hoặc sửa làm phát sinh mâu thuẫn mới: mục 2 (xem #3, #4), mục 6 (#2), mục 7 (#5), mục 14 (#1), mục 23 (#13, #14), mục 36 (#7). Mục 19 sửa thiếu `size` và lý do ngược bias (#17).

---

## A. SAI LUẬT

1. **[SAI LUẬT] Acceptance thiếu bước 2 ⇒ plan coi là Cân bằng ⇒ C (fade) bật lại ngay tại cạnh vừa có nến M5 đóng ngoài.**
   Plan tầng 2: *"Thiếu bước 2 ⇒ hiện 'chạm, chưa phá' và engine coi là Cân bằng."* Bảng bật, hàng Cân bằng: C **bật**.
   HT "Xung đột giữa các tên": *"Fade cạnh vs vừa phá: có 1 nến M5 đóng ngoài là tắt fade, chờ công nhận cú phá (3.1)."* HT 5·C bối cảnh: *"chưa có nến M5 đóng ngoài."*
   **Sửa:** thêm trạng thái thứ tư của chế độ: **"Chờ công nhận"** (bước 1 có, bước 2 chưa). Ở trạng thái này: C tắt tại cạnh đó ("đã có nến M5 đóng ngoài — chờ công nhận"), A tắt ("chưa đủ 2 bước"), B/D như Cân bằng. Chỉ về Cân bằng khi người dùng chọn "chui lại trong" (phá lần 1 thất bại). Thêm test: bước 1 có + bước 2 chưa + C tại cạnh đó ⇒ không bật.

2. **[SAI LUẬT] "POC hôm qua" chưa bị chạm chính là naked POC — HT đã đo và kết luận "không bắt đảo chiều", nhưng QĐ-3 mở B tại đó và gọi là "chưa đo".**
   QĐ-3: *"POC hôm qua / cụm POC — hai loại này chưa đo"*; 1d có hai hàng riêng: *"POC hôm qua · cụm POC | hạng 2 … B (½), A, D"* và *"naked POC | chỉ mục tiêu | TP"*.
   HT 2.3: *"naked POC | 103 | 46,5% | 53,9% | Trái dấu, số ca nhỏ; chỉ làm nam châm mục tiêu, không bắt đảo chiều."* Một POC hôm qua chưa bị giá hôm nay chạm **là** naked POC ⇒ cùng một mức giá, người dùng chọn loại "POC hôm qua" thì B được bật, chọn "naked POC" thì không — lỗ hổng.
   **Sửa:** (a) gộp "POC hôm qua" vào hàng naked POC (chỉ TP; A, D theo chiều được vì ca 6/10 là A phá cụm POC); (b) giữ "cụm POC" (≥ 2 POC trùng nhau ≤ 1 giá — ghi định nghĩa) là hạng 2 cho B(½) với chữ "chưa đo, bằng chứng 13/10"; (c) sửa QĐ-3: naked POC **đã đo** (46,5 %), không viết "chưa đo". Test 13/10 đổi loại vùng thành "cụm POC" hoặc ghi rõ là ngoại lệ.

3. **[SAI LUẬT] Cờ `tail/sp` gán cho cả poor high/low ⇒ B ngược bias được mở tại poor high.**
   Plan 1d: *"single print · poor high/low | nợ, mục tiêu ưa thích | TP; B ngược bias theo QĐ-9 | `tail/sp`"*.
   HT 2.2: ngược bias chỉ *"tại đỉnh có tail thật hoặc single print cũ phía trên"*. HT Q2: *"Poor high/low (≥2 TPO) = nợ, sẽ bị test lại"* — là chỗ giá đi xuyên, không phải chỗ từ chối.
   **Sửa:** tách hàng: "single print" mang cờ `sp`; "poor high/low" không cờ, chỉ TP. Cờ `tail` chỉ đến từ Q2a/Q2b = "tail thật".

## B. MÂU THUẪN

4. **[MÂU THUẪN] QĐ-9 không bao giờ chạy được: vùng có tail thật là "High/Low hôm qua" (hàng cạnh ngoài) — 1d không cho B ở đó, và chấm 2 / C3 đòi B phải ở hạng 1–2.**
   1d: *"High hôm qua · Low hôm qua | cạnh (ngoài) | C, A, D"* (không có B). QĐ-3: *"Riêng B: vùng phải là hạng 1 … hạng 2 … hoặc cạnh VA Âu khi cân bằng."* Thứ tự engine (mục 5): *"vùng (lần 3, cấm, giữa range, cạnh vừa phá) → … hướng vs bias"* — luật vùng chặn trước, QĐ-9 đứng sau.
   Test mục 6 *"B ngược bias … có cờ ⇒ ENTRY 2R ½"* không nói loại vùng nên người implement sẽ viết test qua được bằng VWAP tuần + cờ, trong khi VWAP tuần không bao giờ mang cờ tail.
   **Sửa:** ghi thành luật: *"B ngược bias được miễn điều kiện hạng khi vùng mang cờ `tail` (High/Low hôm qua, Q2 = tail thật) hoặc `sp` đúng phía."* Thêm B vào hàng High/Low hôm qua với chú "chỉ ngược bias theo QĐ-9". Test ghi rõ: zone = High hôm qua, cờ tail, bias BUY, B sell ⇒ ENTRY 2R ½.

5. **[MÂU THUẪN] Cửa sổ cấm 20:30 ±5′ (QĐ-6) chặn đúng lệnh +3R mẫu của HT và trái HT 3.2.**
   Plan 0.2: *"Mặc định bật: 20:30 ±5′"* = 20:25–20:35. HT ca ĐÚNG 6/10 **20:24** nến xác nhận, sổ mẫu HT 8 ghi lệnh lúc **20:25** ("20:25 | sell | phá hồi … +3"). HT 3.2: *"cú phá đáng tin thường rơi vào 20:20–21:30."* Test mục 6 *"6/10 20:24 ⇒ ENTRY"* đi qua được chỉ vì đặt đúng 1 phút trước cửa sổ; bấm "Vào lệnh" lúc 20:25 là vào trong cửa sổ.
   HT 7 ghi *"Đánh tin 19:30 / 20:30 / 21:00 · 0"* — là cấm **đánh tin**, không phải cấm 10 phút.
   **Sửa:** 20:30 mặc định **cảnh báo** (thanh vàng "NYSE mở — không đánh tin"), không phải NO; hoặc cửa sổ hẹp 20:30 → 20:33 (3 nến) và ghi "chưa đo". Thêm test: 20:25 không bị chặn. Giữ 21:00 ±5′ (ca SAI 1/10 bị râu 21:00 quét ủng hộ).

6. **[MÂU THUẪN] QĐ-4 mở B ngược chiều phá trong chế độ Vừa phá, trái câu định nghĩa chế độ 2 của HT; con số "≥ 3 giá" không ghi "chưa đo"; ô C7b của B trùng với `NO_FIGHT_BREAK`.**
   QĐ-4: *"B ngược chiều phá: chỉ khi vùng chọn không phải cạnh vừa phá (cách ≥ 3 giá)…"*. HT 3 chế độ 2: *"Phá hồi · hấp thụ **theo chiều**."* HT xung đột: *"Hấp thụ vs phá hồi cùng lúc ⇒ theo phá hồi."*
   C7 cho B: *"giá đang phá VWAP / cạnh theo chiều move? … có ⇒ `NO_B_IS_BREAK`"* — khi chế độ = Vừa phá và vùng = cạnh vừa phá thì engine đã biết, hỏi lại là hỏi trùng (đúng lỗi review 1 #23).
   **Sửa:** thu hẹp QĐ-4: B ngược chiều phá chỉ khi **cùng chiều bias** và vùng **hạng 1** (VWAP tuần); ghi "≥ 3 giá là ngưỡng của plan, chưa đo". Bỏ C7b, suy `NO_B_IS_BREAK` từ (chế độ = Vừa phá) ∧ (vùng = cạnh vừa phá) ∧ (hướng ngược chiều phá) — giữ C7b chỉ cho chế độ Cân bằng/Trend thin nếu muốn.

7. **[MÂU THUẪN / THIẾU] Bảng bật kịch bản không có mã lý do; test lại đòi "mã lý do mờ".**
   Mục 5: effect `'DISABLE'` có trong danh sách luật nhưng bảng bật chỉ cho chữ (*"tắt 'chưa phá'"*, *"tắt 'không cản tàu'"*). Mục 6: *"≥ 20 ca, mỗi ca kiểm `enabled` và **mã** lý do mờ."* Review 1 #1 yêu cầu `NO_SCENARIO_BIAS_NONE` — không có trong bản 2.
   **Sửa:** đặt mã cho từng ô tắt: `DIS_BIAS_WAIT`, `DIS_BIAS_NONE`, `DIS_BEFORE_2030`, `DIS_NOT_BROKEN` (A/Cân bằng), `DIS_NO_MOVE` (D/Cân bằng), `DIS_M5_OUTSIDE` (C/Vừa phá), `DIS_DONT_FIGHT` (B/Trend thin), `DIS_EARLY_BREAK` (A/phá 18:00–19:20), `DIS_PENDING_ACCEPT` (#1), `DIS_LONGEST_BAR`. Chữ hiển thị tra trong `content.js` theo mã.

8. **[MÂU THUẬN] Ví dụ thanh ENTRY ở 3c tự trái QĐ-9.**
   3c: *"`ENTRY SELL 4193,0 · SL 4195,4 (2,4 giá) · TP 4185,0 · 1:3,3 · cỡ ½ · ngược bias`"* — ngược bias ép 2R (QĐ-9) thì TP phải là 4188,2 và R:R 1:2. Người implement sẽ lấy chuỗi này làm chuẩn so sánh.
   **Sửa:** đổi ví dụ thành ca 6/10 cùng chiều bias (bỏ "ngược bias"), hoặc sửa số cho đúng 2R.

9. **[MÂU THUẪN] Nhãn B1 / B3 / B5 dài 15–30 từ, trái luật "mỗi ô ≤ 9 từ" (4.3) và lint sẽ đỏ.**
   B3 nhãn A: *"đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu; tại cạnh có delta cùng chiều phá hoặc hấp thụ phe ngược"* (≈ 25 từ). B5 nhãn A ≈ 15 từ. Mục 4.3: *"Mỗi ô ≤ 9 từ nhãn chính."*
   **Sửa:** tách: nhãn chính ≤ 9 từ ("Nến xác nhận đạt chuẩn A?"), tiêu chí hiện thành **danh sách 2–4 dòng ngay dưới nút** (trường `criteria[]` trong `content.js`, lint bỏ qua trường này). Danh sách dòng cũng chống tick bừa hơn một câu dài.

## C. THIẾU

10. **[THIẾU] B2 và B3 có đáp án "không rõ" nhưng không ghi hệ quả; C4 không có "không rõ".**
    B2: *"giảm ⇒ qua; lẫn ⇒ CHỜ; tăng ⇒ `NO_MOMENTUM`"* — "không rõ" bỏ trống. B3: chỉ *"'chưa' ⇒ CHỜ"*. HT 9: *"Câu nào 'không' hoặc 'không rõ' thì không vào."* B1 đã có `NO_UNCLEAR`, hai ô kia thì không.
    **Sửa:** B2/B3 "không rõ" ⇒ `NO_UNCLEAR` (cùng mã B1, scope ghi tên ô). C4 thêm "không rõ" ⇒ `NO_UNCLEAR`. Ghi luôn: chấm 5 với "không có / ở giữa move" cho A, C, D **sáng** (HT 4.3 "bỏ qua"), với B **không sáng**.

11. **[THIẾU] Ba quyết định của plan không được gắn mã QĐ, người implement không biết đó là chọn lựa hay luật HT.**
    (a) 1c hàng 4: *"trên, Q1 = b · dưới, Q1 = P ⇒ KHÔNG"* — HT 2.2 chỉ nói "profile không phải b" là điều kiện BUY, không nói b thì sao. (b) Bảng bật, Trend thin: *"B tắt 'không cản tàu'"* — B **cùng chiều** trend ở nhịp hồi không phải cản tàu (HT chế độ 3: *"Chỉ vào theo chiều ở nhịp hồi"*); nếu chủ ý coi ca đó là D thì phải ghi. (c) Cỡ ½ "vùng hạng 2" ở 3b áp cho mọi kịch bản, nhưng 1d viết *"B (½), A, D"* (chỉ B ½) và HT 5·B chỉ nói cỡ nhỏ cho hấp thụ; test ca 6/10 (A tại cụm POC) không nói cỡ.
    **Sửa:** thêm QĐ-12 (b/P ⇒ KHÔNG, chưa đo), QĐ-13 (Trend thin: B cùng chiều gọi là D, lý do mờ "cùng chiều ⇒ dùng D"), QĐ-14 (½ hạng 2 chỉ cho B; A, D cỡ chuẩn) và sửa dòng gập cỡ lệnh + test 6/10 ghi "cỡ chuẩn".

12. **[THIẾU] Loại vùng "HVN ngày" (thường) không có hàng trong 1d; "HVN ngày ngay sau phá cực trị" là trạng thái lúc vào lệnh, không phải loại vùng lúc 18:30.**
    1a mục 4 bắt kẻ *"HVN / LVN ngày và 3 tuần"*; 1d chỉ có *"HVN ngày ngay sau phá cực trị"* trong hàng cấm. HT Q4: *"Vào HVN ⇒ đi ngang"*; HT 2.3 không xếp hạng HVN ngày thường.
    **Sửa:** thêm hàng "HVN ngày | trung tính (chưa đo) | A, D; B chặn" và đổi "ngay sau phá cực trị" thành cờ do engine suy: (chế độ = Vừa phá) ∧ (vùng loại HVN ngày) ∧ (vùng nằm ngoài cạnh vừa phá theo chiều phá) ⇒ `banned` cho B.

13. **[THIẾU] TP gợi ý cho A/B thiếu "vùng kế tiếp nếu gần hơn".**
    B4: *"TP gợi ý sẵn = vào ± 3R (A, B) / 2R (C, D); C: gợi ý thêm 'cạnh đối diện / POC gần hơn'"*. HT 6: Phá hồi · Hấp thụ *"3R, hoặc vùng kế tiếp nếu gần hơn (tính trước; dưới 1:2 thì bỏ)"*. Ca 6/10 TP là cạnh VAL Âu, không phải 3R tròn.
    **Sửa:** A/B: gợi ý = min(3R, vùng kế tiếp theo hướng lệnh lấy từ thẻ); nếu vùng kế tiếp cho R:R < 1:2 ⇒ `NO_RR` kèm chữ "vùng kế tiếp quá gần".

14. **[THIẾU] "Lần thứ n tại vùng", chuỗi SL và ngắt mạch không nói đếm từ loại dòng nào.**
    C3 hiện *"lần thứ n"*; tầng 4 chỉ nói limit hủy *"không tăng đếm vùng"*. Không nói: kèo `paper` (chỉ xem) có tính lần không, có tính SL liên tiếp không; "Tôi vẫn vào" có tính lần không; đếm theo `zoneId` hay theo giá (hai vùng trùng giá).
    **Sửa:** ghi luật: n = số dòng `trades` trong đêm có cùng `zoneId`, trạng thái đã khớp, **kể cả** phá luật, **không kể** `paper`; `paper` không cộng chuỗi SL, không cộng phá luật, có cộng vào sổ với cờ. Thêm 3 test.

## D. UX

15. **[UX] Tầng 3 không đạt "≤ 7 + ≤ 6" cho B và D; plan không định nghĩa "thao tác".**
    Đếm theo bảng 3a/3b (1 click hoặc 1 ô số = 1 thao tác; ô tùy chọn và hộp lý do ngược bias không tính):
    - **A — Canh:** C1 kịch bản · C2 hướng · C3 vùng · C4 bong bóng · C5 cách vùng · C6 số = **6** ✓. **Bấm:** B1 U/V · B3 đạt · B4 giá vào · B4 SL · (TP gợi ý sẵn = 0) · B5 tick = **5** ✓ (6 nếu sửa TP).
    - **B — Canh:** C1–C6 = 6 + C7a DMA + C7b "đang phá?" = **8** ✗. **Bấm:** B1 · B2 · B3 · giá vào · SL · B5 = **6** ✓ chỉ khi nhận TP gợi ý; sửa TP ⇒ 7 ✗.
    - **D — Canh:** C1–C6 + C7 "move ≥ 5 giá" + C7 "hồi > 70 %" = **8** ✗.
    - **C — Canh:** 6 ✓; Bấm: B3 · vào · SL · B5 = 4 ✓.
    **Sửa:** (a) định nghĩa "thao tác" như trên và ghi vào mục 3; (b) **C2 hướng tự điền** cho A (theo hướng phá), D (theo bias), C (theo loại cạnh: VAH ⇒ sell, VAL ⇒ buy), sửa được ⇒ A/C/D còn 5; (c) bỏ C7b của B (xem #6) ⇒ B Canh = 7; (d) D: C7 "move ≥ 5 giá" thay bằng một ô số "move vừa rồi: __ giá" (engine tự so 5) — vẫn 1 thao tác nhưng chống tick bừa; D Canh = 7 sau khi hướng tự điền; (e) e2e (1) đếm cho **B**, không chỉ A.

16. **[UX] Hai ô dễ tick bừa hoặc cũ: B5 là checkbox tự khai; C6 nhập ở Canh nhưng luật tính tại lúc Bấm.**
    B5: *"tick"* — trái 4.5 *"không dùng checkbox cho câu có đáp án xấu"*; người muốn thấy ENTRY sẽ tick. C6 *"biên độ nến M1 cao nhất trong 5 nến"* điền trước nến xác nhận; HT 6: *"5 nến gần nhất"* tính lúc đặt SL — nếu Canh 4–5 phút thì cửa sổ 5 nến đã trượt.
    **Sửa:** B5 thành 3 nút "đúng chỗ / chưa chắc / sai chỗ" (chưa chắc ⇒ CHỜ, sai ⇒ `NO_SL_POS`). C6 giữ ở Canh, nhưng khi sang Bấm hiện lại số với nút "còn đúng" / sửa — hoặc chấp nhận cũ và ghi rõ trong plan là chọn lựa có chủ đích.

17. **[UX nhẹ] QĐ-1 chưa nói hai ca thường gặp:** (a) Q6 = "chưa" hoặc thẻ không có vùng loại cạnh ⇒ ở chế độ Cân bằng mọi vùng là "giữa range"? (b) vùng nhập dạng khoảng *"4181–4183"* thì "trùng cạnh ≤ 1 giá" so với mép nào. (c) HVN tuần / cụm POC trùng cạnh có được như VWAP không (QĐ-1 chỉ nêu VWAP).
    **Sửa:** (a) không có vùng cạnh ⇒ B/C đều tắt "chưa có cạnh range"; (b) so với mép gần nhất; (c) mọi vùng hạng 1–2 trùng cạnh ≤ 1 giá đều được.

## E. KỸ THUẬT

18. **[KỸ THUẬT] Mô hình dữ liệu thiếu trường mà UI/sổ cần.**
    `trades.tests:{b1,c4,c4num,b2,c5}` không có `b3` ⇒ cột "Δ" trong sổ 7 cột cho A/D in gì? (HT 9 câu 6: *"phá hồi/trap: nến xác nhận mạnh"*). `trades` không có `size` (số hợp đồng — review 1 #19 yêu cầu, mục 11 ghi "đã sửa" nhưng thiếu) và không có `counterBiasReason` (HT luật cứng bắt ghi lý do; `setup.counterBiasReason` bị xóa khi "Kèo mới"). `t0.windows:[{id, kind, at, on, offAt?}]` không có hạng và độ rộng dù 0.2 cho "tin tùy chỉnh (giờ + hạng)".
    **Sửa:** `tests` thêm `b3`; cột Δ in "giảm" (B) / "nến mạnh" (A, D, C) / "—"; `trades` thêm `size`, `counterBiasReason`, `slPos` (#16); `windows` thêm `rank`, `minutesBefore`, `minutesAfter`.

19. **[KỸ THUẬT] "Mọi mốc khai theo giờ ET" (QĐ-7) sai cho mốc không thuộc Mỹ.**
    "London đóng" 22:30 đổi từ 25/10 (giờ London, đúng như plan nói) nhưng cùng câu lại ghi *"tự +1h mùa đông"*; "Lõi giao thoa 21:00–22:30": đầu 21:00 theo Mỹ (dịch 01/11), cuối 22:30 theo London (dịch 25/10) ⇒ tuần 25/10–31/10 là 21:00–23:30. Globex bảo trì 04:00–05:00 và `nightKey` 05:00: mùa đông Globex mở 06:00 VN, lệnh mở lúc 05:30 bị gán sang đêm mới dù sàn còn đóng.
    **Sửa:** mỗi mốc trong `rules.js` mang múi gốc (`ET` | `LONDON` | `VN`); `nightKey` dùng mốc Globex mở theo ET (05:00 hè / 06:00 đông) và test thêm 05:30 ngày 02/11.

20. **[KỸ THUẬT] Ba chỗ test sẽ làm người implement đoán.**
    (a) *"12/10 21:27 V + bong bóng ngược còn giữ ⇒ NO với 2 mã đúng thứ tự"* — không ghi thứ tự; theo engine mục 5 (C4 trước B1) là `NO_BUBBLE_AGAINST` rồi `NO_V_PULLBACK`, ngược với cách sổ in "V · bb" — ghi rõ. (b) *"5/10 19:25 B lẫn lộn ⇒ CHỜ"*: cửa sổ 19:30 ±15′ mặc định bật khi *"người dùng chưa chạm vào tầng 0"* ⇒ test phải đặt `t0` đã chạm, nếu không ra NO cửa sổ cấm. (c) `tests/*.test.mjs` là ES module nhưng mục 5 nói *"nạp qua `require`"*: `.mjs` không có `require`; đổi sang `.test.cjs` hoặc ghi "import mặc định của CJS".

## F. CHỮ

21. **[CHỮ] Danh sách từ tiếng Anh cho phép (4.11) vẫn thiếu từ plan đang dùng trên màn hình:** "flat" (tầng 4 *"flat trước hh:mm"*), "Trend" (*"Trend thin"* — chỉ "thin" được phép), "Settlement" (thanh trạng thái), "Markdown", "JSON", "CSV" (nút xuất), "Esc", "Enter" (gợi ý phím), "Jobless Claims", "paper" nếu hiện cờ. Lint sẽ đỏ ngay vòng 1.
    **Sửa:** bổ sung, hoặc đổi: "flat" → "đóng sạch", "Settlement" → "chốt giá ngày (settlement)".

22. **[CHỮ] Lỗi câu chữ cụ thể:**
    - 1c hàng 3: *"trên | dưới · hoặc dưới / trên | — | KHÔNG"* — không đọc được; viết: "trên | dưới" và "dưới | trên" thành hai hàng, hoặc "ngược phía VWAP tuần".
    - C5: *"1–3 giá, chưa về"* và *"≥ 3 giá, ở lưng"* chồng nhau tại 3; viết "hơn 1, chưa tới 3" và "từ 3".
    - 3b dòng *"Gập: cỡ lệnh MGC"* — "Gập" khó hiểu; viết "Thu gọn được:".
    - Đánh số mục nhảy từ 8 sang 11 (không có 9, 10).
    - 3c ví dụ ENTRY (xem #8).

---

## Kết luận

- **Chưa đủ để implement**: còn 3 chỗ sai luật (#1 fade bật lại sau nến M5 đóng ngoài, #2 naked POC được gọi là hạng 2, #3 poor high mang cờ tail) và 2 mâu thuẫn làm luật HT không chạy được (#4 ngoại lệ ngược bias bị chặn trước, #5 cửa sổ 20:30 chặn lệnh mẫu 6/10).
- **Phải sửa trước khi giao Sonnet:** #1–#8 (luật và QĐ), #7 + #10 (mã DISABLE và hệ quả "không rõ" — nếu thiếu, agent tự đặt mã và test không so được), #15 (định nghĩa thao tác, hướng tự điền, bỏ C7b).
- Các mục còn lại (#9, #11–#14, #16–#22) sửa được trong cùng lần sửa plan, mỗi mục một dòng; không cần vòng review 3 nếu #1–#8 sửa đúng.
