# Review 1 — plan "Trạm Đêm Vàng" (CHECKLIST-DEM-VANG-plan.md, bản 1 · 20/10/2026)

Người review: Claude (Fable 5.1). Đối chiếu từng ô của plan với `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (gọi tắt **HT**, trích theo số mục), `daily-trading/RULES.md` (**RULES**) và `so-tay-vang-mgc.html` (**ST**). Xếp nặng → nhẹ. Không liệt kê chỗ plan đã đúng.

---

## A. SAI LUẬT (công cụ sẽ cho ENTRY hoặc cấm sai so với trang hệ thống)

1. **[SAI LUẬT] Bias KHÔNG: plan vẫn bật A/B/D, chỉ giảm cỡ ½.**
   Plan: tầng 2 "Bảng bật kịch bản" chỉ phụ thuộc chế độ × giờ; tầng 3d "Tự nhân ½ khi: bias KHÔNG". Bias không hề tắt kịch bản nào.
   HT 2.2, hàng KHÔNG bias: *"Chỉ fade hai cạnh VA Âu, mục tiêu 2R, cỡ lệnh một nửa. Không phá hồi."* Hàng CHỜ: *"Chờ 1 nến M5 đóng rõ một phía rồi mới chốt bias"* (chưa chốt = chưa có gì được bật).
   **Sửa:** thêm trục *bias* vào bảng bật: KHÔNG ⇒ chỉ C (2R, ½), A/B/D mờ với lý do "bias KHÔNG: chỉ fade cạnh"; CHỜ ⇒ cả 4 mờ. Thêm test `NO_SCENARIO_BIAS_NONE`.

2. **[SAI LUẬT] Lệnh ngược bias: plan cho mọi kịch bản, chỉ cần gõ lý do; mục tiêu vẫn 3R.**
   Plan 3a: *"Hướng ngược bias ⇒ bắt buộc ô 'Lý do ngược bias' (… điền ⇒ cho phép, cỡ nhỏ…)"*.
   HT 2.2 hàng BUY: *"Không sell, trừ hấp thụ buy tại đỉnh có tail thật hoặc single print cũ phía trên, cỡ nhỏ, 2R. Không sell tại HVN 3 tuần."* HT 5·A bối cảnh: *"Bias cùng chiều phá"*; HT 5·D bối cảnh: *"Một move rõ (≥ 5 giá) cùng chiều bias"*. ⇒ A và D ngược bias là bối cảnh hỏng theo định nghĩa; chỉ B (và C) mới có thể ngược bias.
   **Sửa:** ngược bias ⇒ (a) A, D ⇒ KHÔNG VÀO mã `NO_COUNTER_BIAS_SCENARIO`; (b) B chỉ khi vùng đã chọn có cờ "tail thật" / "single print" đúng phía (xem mục 20) — nếu không, KHÔNG VÀO; (c) mục tiêu ép về 2R, cỡ ½; (d) lý do vẫn bắt buộc ghi (luật cứng 2.2). Thanh ENTRY in rõ "ngược bias · 2R · ½".

3. **[SAI LUẬT] Vị trí SL dùng một câu chung cho cả 4 kịch bản.**
   Plan 3d tick tay: *"SL đặt sau râu nến xác nhận hoặc mép xa vùng (cái xa hơn) + 0,3 đệm"* — đó là câu của A (HT 5·A) và mục 6.
   HT 5·B SL: *"Sau cực trị của cụm hấp thụ + 0,3 giá. Không đặt SL ở giữa cụm."* HT 5·C SL: *"Sau râu phá hụt + 0,3 giá."* HT 5·D SL: *"Sau đỉnh nhịp hồi + 0,3 giá."*
   **Sửa:** nhãn ô "vị trí SL" đổi theo kịch bản đã chọn (4 chuỗi trong `content.js`), kèm ảnh nhỏ. B thêm ô đỏ "SL đang ở giữa cụm". Sàn nhiễu + trần 4 giá giữ chung.

4. **[SAI LUẬT] B trong chế độ Cân bằng được bật tại "vùng hạng 1–2" dù vùng đó nằm giữa range.**
   Plan tầng 2, hàng Cân bằng: *"B: bật, chỉ tại cạnh VA Âu / vùng hạng 1–2"*.
   HT 3 chế độ 1: *"Chỉ fade hai cạnh, mục tiêu 2R. Giữa range không có lệnh nào."* HT 7: *"Lệnh giữa range (không ở cạnh) · 0"*. HT 5·B bối cảnh: *"…hoặc cạnh VA Âu khi đang cân bằng"* — tức ở chế độ cân bằng, B chỉ ở cạnh.
   **Sửa:** Cân bằng ⇒ B chỉ bật khi vùng chọn là cạnh VA Âu/range, hoặc VWAP tuần/ngày **trùng cạnh** (≤1 giá). VWAP tuần giữa range ⇒ KHÔNG VÀO `NO_MID_RANGE`. Ghi quyết định này vào mục 0 của plan vì HT có hai câu kéo hai phía.

5. **[SAI LUẬT] LVN ngày xếp vào "vùng kẻ" (A, D) trong khi thẻ phiên gọi LVN là VÙNG CẤM.**
   Plan 1d: *"POC hôm qua · cụm POC · LVN ngày | vùng kẻ (ca 13/10, 6/10) | A, D"*.
   HT 0: *"Vùng cấm: LVN, HVN 3 tuần"*; HT 8 thẻ phiên: *"VÙNG CẤM : (HVN 3 tuần, LVN)"*; HT Q4: *"Vào LVN ⇒ chạy nhanh qua."* Ca 13/10 là *"LVN ngày + POC hôm qua"* — vùng để bám là POC, LVN chỉ nói giá sẽ đi nhanh.
   **Sửa:** tách LVN ra hàng "cấm fade" cùng HVN 3 tuần (B chặn, A/D theo chiều được). Trợ giúp "?" nói rõ ca 13/10 là hợp lưu LVN + POC.

6. **[SAI LUẬT / MÂU THUẪN NGUỒN] Chấm 2 (câu 2 checklist) không thoả được cho các vùng POC / cụm POC / HVN tuần, nhưng plan vẫn cho A, D ở đó — và ca ĐÚNG 6/10 chính là phá cụm POC.**
   Plan 3e: *"2 vùng ≤1 giá & hạng"*; HT 9 câu 2: *"vùng đó thuộc hạng 1–2 hoặc là cạnh VA Âu trong chế độ cân bằng?"*; HT 9 mở đầu: *"Câu nào 'không'… thì không vào."* Nhưng HT 5·A ca thật 6/10: *"Nến −20, −75 phá cụm POC"* ⇒ ENTRY hợp lệ tại vùng không phải hạng 1–2.
   **Sửa:** định nghĩa chấm 2 trong plan: "giá ở vùng **đã ghi trong thẻ phiên** ≤1 giá; **riêng B** vùng phải hạng 1–2 hoặc cạnh VA Âu (cân bằng)". Cùng lúc, acceptance bước 1 (plan tầng 2) đang viết cứng *"ngoài cạnh VA Âu (hoặc ngoài IB)"* — thêm "hoặc ngoài một vùng đã kẻ" để ca 6/10 chạy qua được. Thêm test ca 6/10 với mode = vừa phá cụm POC.

7. **[SAI LUẬT] Không có cửa sổ cấm lúc 20:30; cửa sổ 19:30/21:00 chỉ tồn tại nếu người dùng tự khai có tin.**
   Plan 0.2: tin tối nay là lựa chọn "không · hạng 2 (21:00) · hạng 1 (19:30)…"; không có mốc 20:30.
   HT 7: *"Đánh tin 19:30 / 20:30 / 21:00 · 0 · Lệnh +5R ngày 30/9 không lặp lại được"*. ST §1: *"20:30 … cú quét NYSE"*; ST §8: *"Flat trước 19:15 · đứng ngoài ±15′"*.
   **Sửa:** 20:30 (mùa đông 21:30) luôn là cửa sổ cấm mặc định, ±5′ (con số ±5′ là đề xuất của plan, HT không cho số — ghi rõ "chưa đo"). 19:30 mặc định "có tin hạng 1" vào thứ Năm (Jobless Claims, ST §1 *"thứ Năm hằng tuần"*) và khi người dùng chưa khai. Người dùng tắt từng cửa sổ được, mỗi lần tắt ghi vết.

8. **[SAI LUẬT] 4.4 "cạnh/lưng" để hở khoảng 1–3 giá.**
   Plan 3b: *"cạnh (≤1 giá…) · lưng (≥3 giá) · không rõ"* — giá cách vùng 2 giá thì người dùng bấm gì? Dễ bấm "cạnh".
   HT 4.4: *"Entry hợp lệ khi giá cách vùng đã kẻ ≤ 1 giá, hoặc nến xác nhận có râu chạm vùng."* — mọi khoảng >1 giá đều không hợp lệ; "≥3 giá" chỉ là lúc gọi tên "lưng" và bỏ kèo.
   **Sửa:** ba nút: "≤1 giá / râu chạm" · "1–3 giá: chưa về" (⇒ CHỜ, lý do "chờ hồi về cạnh") · "≥3 giá: lưng" (⇒ KHÔNG VÀO, "không hồi thì bỏ").

9. **[SAI LUẬT] B với 4.2 = "lẫn lộn" chưa định nghĩa; chỉ "tăng dần" mới chặn.**
   Plan 3b: *"B cần 'giảm dần'; … 'tăng dần' khi gọi B ⇒ KHÔNG VÀO"*.
   HT 4.2 luật: *"chỉ gọi hấp thụ khi cả thân lẫn |delta| giảm dần qua 3 nến."* ⇒ "lẫn lộn" cũng không phải hấp thụ. (Lưu ý HT tự mâu thuẫn: ca ĐÚNG 5/10 19:25 ghi *"delta lẫn lộn (+25, +22, −27, +11)"* — plan phải chọn luật cứng 4.2 và ghi chú ca 5/10 là ngoại lệ chưa đo.)
   **Sửa:** B: chỉ "giảm dần" cho qua; "lẫn lộn" ⇒ CHỜ với lý do "chưa đủ 3 nến giảm dần"; "tăng dần" ⇒ KHÔNG VÀO.

10. **[SAI LUẬT] B cần bong bóng CÙNG PHE, plan dùng 4.3 chung (cho qua cả "đã vỡ" / "không có").**
    HT 5·B kiểm tra: *"Bong bóng ở cực trị cùng phe với lệnh định vào."* Plan 4.3: chỉ "ngược phe còn giữ ⇒ KHÔNG VÀO".
    **Sửa:** khi kịch bản = B, 4.3 phải là "cùng phe"; "không có" ⇒ CHỜ ("hấp thụ mà không có bong bóng thì lấy gì làm bằng chứng"), "đã vỡ" ⇒ KHÔNG VÀO.

11. **[SAI LUẬT nhẹ] D ghi "mục tiêu 2–3R" (plan 3c) nhưng mục 0 chốt "2R (C, D)".**
    HT 6 bảng TP: *"Fade cạnh · Trap | 2R, hoặc cạnh đối diện / POC | Khi đạt +1R."* Tiêu đề D "2–3R" chỉ là dải.
    **Sửa:** D: TP mặc định 2R, be +1R; bỏ "2–3R" khỏi ô.

12. **[SAI LUẬT nhẹ] Chốt thẻ phiên chỉ cần ≥1 vùng.** HT 0: *"3–5 vùng đã kẻ"*; thẻ phiên *"VÙNG (≤5)"*. **Sửa:** <3 vùng vẫn chốt được nhưng hiện cảnh báo vàng "mới có n/3 vùng" và ghi vết.

## B. THIẾU (luật có trong hệ thống nhưng plan bỏ, hoặc đường đi đứt)

13. **[THIẾU] Giờ mùa đông chỉ dịch thanh trạng thái và mốc 20:30; không dịch neo TPO 19:20, IB, cửa sổ 18:00–19:20, 20:20–21:30 — và không nhắc đổi neo chart.**
    Plan §0 và §8 câu 1 nói "mọi mốc Mỹ +1h" nhưng tầng 1a vẫn *"TPO ngày neo 19:20"*, tầng 2 vẫn *"IB 19:20–20:20"*, *"18:00–19:20 phá giả"*. Từ 01/11 pit COMEX mở 20:20 VN; nếu chart vẫn neo 19:20 thì IB sai (CLAUDE.md đã ghi sự cố này).
    **Sửa:** mọi mốc trong `rules.js` khai theo giờ ET rồi `time.js` đổi sang VN; ngày 01/11 hiện thẻ một lần: "Mỹ sang giờ mùa đông: đổi neo session TPO/SessionZones 19:20 → 20:20, IB = 20:20–21:20". London đổi giờ sớm hơn một tuần (25/10): mốc "London đóng" 22:30 → 23:30 từ 25/10, không phải 01/11.

14. **[THIẾU / THỪA] Acceptance bước 3 hỏi ở tầng 2 nhưng chỉ xảy ra lúc retest (tầng 3), và bị hỏi lại trong A·Kiểm tra.**
    Plan tầng 2: bước 3 *"Tại cú retest trên M1: delta cùng chiều phá, hoặc hấp thụ phe ngược"*; plan 3c A kiểm tra: *"tại cạnh vừa phá có delta cùng chiều phá hoặc bong bóng hấp thụ phe ngược"* — cùng một câu. Lúc gọi tên chế độ, retest chưa có ⇒ người dùng kẹt hoặc tick bừa.
    **Sửa:** chế độ "Vừa phá" = bước 1 + 2; bước 3 là ô A·Kiểm tra (hỏi một lần, tầng 3). Chấm 3 ("chế độ bật kịch bản") không phụ thuộc bước 3.

15. **[THIẾU] Không có trạng thái "lệnh limit chưa khớp" và đường huỷ kèo; giá vào thực tế không nhập được.**
    HT 5·A điểm vào: *"Vào ở giá đóng, hoặc limit tại giữa thân."* ST §7: *"Hủy kịch bản — viết trước, làm đúng."* Plan tầng 4 lấy thẳng số từ máy tính 3d.
    **Sửa:** nút "Vào lệnh" mở hộp: market (giá khớp thật) / limit (giá chờ) ⇒ trạng thái "đang chờ khớp" với nút "Khớp rồi" · "Huỷ (giá bỏ đi)". Huỷ không tính là lệnh. Giá khớp thật ghi vào sổ, R tính theo giá thật.

16. **[THIẾU] Đang có lệnh mở mà tới cửa sổ tin.** ST §8: *"Flat trước 19:15"* (hạng 1), *"Đóng sạch trước 00:45"* (FOMC). Plan chỉ có dòng nhắc FOMC ở 0.2, tầng 4 không biết gì.
    **Sửa:** tầng 4 có đếm ngược "flat trước hh:mm" khi lệnh mở trùng cửa sổ hạng 1/FOMC; đóng vì lý do này là lý do hợp lệ có tên, không phải phá luật.

17. **[THIẾU] Luật "chưa be thì không sờ SL".** RULES D: *"Chưa dời SL về be: để nguyên, không sờ vào."* Plan tầng 4 không nói SL có sửa được không.
    **Sửa:** tầng 4 không có ô sửa SL; chỉ có nút "Đã dời về hoà" (mở khi đạt mốc) và "Đóng lệnh".

18. **[THIẾU] Ba ca biên của ngắt mạch chưa định:** (a) lệnh hoà (be) có reset chuỗi SL liên tiếp không (plan chỉ nói *"TP xen giữa reset đếm"*); (b) "Tôi vẫn vào (phá luật)" bị ẩn khi TẮT MÁY — lệnh vào lúc đó không được ghi sổ, trái mục đích "sổ trung thực"; (c) lệnh còn mở lúc 05:00 (ST: Globex bảo trì 04:00–05:00, *"lệnh ôm qua đêm không thoát được"*).
    **Sửa:** (a) chỉ SL mới cộng chuỗi, TP/hoà đều reset — ghi thành luật có mã; (b) giữ nút ở mọi phán quyết trừ ENTRY; (c) `open` chuyển sang đêm mới, dòng sổ ghi về đêm vào lệnh.

19. **[THIẾU] Dữ liệu để in dòng sổ 7 cột và 4 con số tuần không được thu.**
    HT 8 mẫu: *"U · bb −129 giữ · Δ giảm · cạnh"* cần **số** bong bóng; HT 8 cuối tuần: *"R theo tên kịch bản và theo loại vùng"*, *"SL bị quét rồi giá tới TP"*. Plan `trades:[{time,side,scenario,mode,tests,slDist,r,flags,exit,notes}]` không có `zoneType`, `entry/sl/tp`, `sweptThenTP`, số bong bóng.
    **Sửa:** 4.3 có ô số tuỳ chọn "bong bóng: ±___" (người dùng đọc số này rồi, HT bắt ghi); trade thêm `zoneId, zoneType, entry, sl, tp, rrPlanned, sweptThenTP, counterBias, size`.

20. **[THIẾU] Q2 (tail) một đáp án cho cả đỉnh lẫn đáy.** Một profile có hai cực trị; tail thật ở đỉnh và poor low ở đáy là chuyện thường. Ngoại lệ ngược bias (mục 2) cần biết *"đỉnh có tail thật hoặc single print cũ phía trên"*.
    **Sửa:** Q2 tách "Đỉnh hôm qua: …" và "Đáy hôm qua: …"; vùng kẻ từ đỉnh/đáy tự mang cờ tail thật / poor / mồi.

21. **[THIẾU] Loại vùng "IB high / IB low" không có trong 1d** dù acceptance (HT 3.1) dùng IB và ST neo IB 19:20–20:20. **Sửa:** thêm loại "cạnh IB" cùng hàng với cạnh VA Âu.

22. **[THIẾU] Q1 có đáp án "B" nhưng HT Q1 chỉ định nghĩa D · P · b · Thin · Chữ nhật**; "B" chỉ xuất hiện ở mẫu thẻ phiên. **Sửa:** hoặc định nghĩa "B = hai phân phối (double distribution)" trong "?" và ghi rõ "HT không định nghĩa", hoặc bỏ.

## C. UX (chậm, phải đoán, dễ tick bừa)

23. **[UX] Cùng một sự thật bị hỏi 2–3 lần ở tầng 3** — DMA (B·kiểm tra "DMA đi ngang" + B·loại bỏ "DMA còn dốc"); "chưa có nến M5 đóng ngoài" (A·loại bỏ + acceptance bước 1 + C·bối cảnh); "hồi chỉ 1–2 nến" (A·loại bỏ) = 4.1 U (≥3 nến); "giá ở giữa range" (C·loại bỏ) = 4.4 + C·bối cảnh; "nến dài nhất phiên" (nút 3′ + B·loại bỏ + C·loại bỏ). Hệ quả: ~15 ô tick + 4–6 số mỗi kèo trong khi nến xác nhận M1 chỉ cho 60 giây ⇒ tick bừa hoặc bỏ công cụ.
    **Sửa:** mỗi sự thật một điều khiển 3 trạng thái; ô "loại bỏ" chỉ giữ cái không suy được từ ô khác. Tách tầng 3 thành **Canh** (điền trước khi nến xác nhận: kịch bản, hướng, vùng, bối cảnh, 4.3, 4.4, biên độ nến cao nhất) và **Bấm** (sau nến xác nhận: 4.1, 4.2, 1 ô "nến xác nhận đạt", giá vào/SL/TP). Mục tiêu đo: ≤6 thao tác ở bước Bấm.

24. **[UX] B bắt nhập hai số delta để tính 50 %.** HT 10 ghi luật này *"chưa chứng minh… không coi là lợi thế đã đo"*. Nhập 2 số dưới áp lực 1 phút là chỗ dễ bỏ. **Sửa:** một ô 3 trạng thái "delta nến xác nhận ≥ ½ nến lớn nhất move: có / không / không rõ".

25. **[UX] Q6 và cạnh VA Âu đổi trong lúc 18:30–19:20 sẽ sinh dòng "sửa lúc hh:mm" vô nghĩa.** Âu kết thúc 19:20 (ST §1 *"14:00–19:20 Âu"*), thẻ phiên *"điền trước 19:20"*. **Sửa:** trước 19:20 (mùa đông 20:20) sửa Q6 / vùng VA Âu không ghi vết; sau mốc đó mới coi là "nắn thẻ".

26. **[UX / CHỮ] "KỊCH BẢN A/B" trong thẻ phiên trùng tên với kịch bản A (phá hồi) / B (hấp thụ).** HT 8 dùng A)/B) với nghĩa "kế hoạch 1 / kế hoạch 2". **Sửa:** đặt "Kế hoạch 1 · Kế hoạch 2: nếu … thì …", thêm ô "huỷ kế hoạch khi …" (ST §7).

27. **[UX] Chân bảng "cộng tay cuối phiên: …R" do máy điền thì không còn là cộng tay.** HT 8: *"tổng ngày không khớp cộng tay"* là lỗi đang muốn sửa. **Sửa:** ô "Bạn cộng: __ R" bên cạnh "Máy cộng: x R"; lệch ⇒ tô đỏ. Nút "Kết phiên" chỉ mở khi đã nhập.

28. **[UX] Khi tầng 4 có lệnh, tầng 3 vẫn tính ra KHÔNG VÀO "đang có lệnh mở".** Nên khoá hẳn tầng 3 và nhảy về tầng 4 (RULES A.3 *"Nhồi lệnh = 0"*).

29. **[UX / KỸ THUẬT] Nửa cỡ lệnh chồng nhau.** Plan 3d: ½ khi "bias KHÔNG, fade cạnh, ngược bias, NFP/CPI, hạng 2" — ba điều kiện cùng lúc = ⅛? HT chỉ nói "cỡ nhỏ"/"một nửa". **Sửa:** ½ áp một lần, không nhân chồng; ghi "½ là lượng hoá của plan, HT nói 'cỡ nhỏ'".

30. **[UX] Khoá 3 phút sau nến dài nhất tính theo đồng hồ, không theo nến.** Bấm lúc 21:17:50 thì 3 nến M1 đóng xong lúc 21:21:00, không phải 21:20:50. **Sửa:** khoá tới `ceil(now, 1′) + 3′`, hiện "mở lại 21:21".

31. **[UX] Phím 1–4 / B / S xung đột với ô nhập số và chữ.** Chưa nói phím tắt bị tắt khi focus trong input. **Sửa:** ghi rõ; thêm `Esc` thoát ô nhập.

## D. CHỮ

32. **[CHỮ] Danh sách từ tiếng Anh cho phép (4.11) thiếu chính những từ plan và HT đang dùng** → lint sẽ đỏ ngay trang đầu: *move* ("move rõ"), *retest*, *be* (hoà), *overlap* ("Lõi overlap"), *thin* ("Trend thin"), *setup*, *range*, *bracket*, *session*, *tick*, *DST*, *Globex/COMEX/NYSE/FOMC/NFP/CPI*. **Sửa:** bổ sung vào danh sách hoặc đổi: "Lõi overlap" → "Lõi giao thoa", "DST" → "giờ mùa đông".

33. **[CHỮ] Chính tả không khớp trang HT:** plan viết "hoà", "khoá"; HT viết "hòa" (*"Dời SL về hòa (be)"*), "khóa". Chọn một kiểu (theo HT) để lint không bắt chéo. Plan 3b 4.2 ghi *"(ô 3d)"* cho nến xác nhận — 3d là máy tính SL, đúng phải là 3c "Điểm vào".

34. **[CHỮ / KỸ THUẬT] Ngày đổi giờ sai và tự mâu thuẫn:** §0 nói *"bắt đầu 01/11/2026"* (đúng: CN đầu tháng 11), §6 test lại ghi *"DST (18/10 và 02/11/2026)"*. 18/10 không là mốc nào; EU đổi 25/10, Mỹ 01/11, Mỹ trở lại 14/03/2027. **Sửa:** test 25/10, 01/11/2026, 14/03/2027.

## E. KỸ THUẬT / KIỂM THỬ

35. **[KỸ THUẬT] "App chạy local" sẽ hỏng nếu `js/*.js` là ES module mở bằng file://** (trình duyệt chặn module qua `file:`), và service worker không chạy trên `file:`. Plan hứa "chạy không mạng" + "không bước build". **Sửa:** chọn một trong hai và ghi rõ: (a) script thường (không `type=module`), nối thứ tự trong `index.html`, test bằng node:test qua `vm`/export điều kiện; hoặc (b) local = `npx serve` và chỉ hứa offline qua PWA đã cài. Thêm: trên GitHub Pages dưới đường dẫn con, SW phải có `scope` tương đối, tên cache theo phiên bản + `skipWaiting`/`clients.claim` + thẻ "có bản mới, tải lại" — nếu không, sau mỗi vòng review người dùng vẫn chạy bản cũ nhiều ngày.

36. **[KỸ THUẬT] Thứ tự ưu tiên giữa các luật bật/tắt chưa khai.** Hàng "trước 20:30" × chế độ × bias × cửa sổ tin × khoá 3′ — khi nhiều cái cùng tắt một kịch bản, lý do nào hiện? Agent implement sẽ tự chọn. **Sửa:** `rules.js` là **danh sách luật có thứ tự** `[{code, when(state,now), effect}]`, engine chạy tuần tự, `reasons` giữ thứ tự đó; plan liệt kê thứ tự: OFF → lệnh mở → tin → 3′ → bias → giờ → chế độ → vùng → 4 bài → loại bỏ → SL/R:R.

37. **[KỸ THUẬT] Khoá đêm theo ngày lịch sai khi đêm vắt qua 0:00.** `nights["2026-10-20"]` — lệnh lúc 00:30 ngày 21 thuộc đêm 20. **Sửa:** khoá = ngày của mốc 18:00 bắt đầu; `time.nightKey(now)`; test ranh 05:00 đã có, thêm test 00:30.

38. **[KIỂM THỬ] Ca test thiếu:** bias KHÔNG ⇒ chỉ C; bias CHỜ ⇒ tầng 3 khoá rồi "chốt lại"; ngược bias ⇒ B 2R ½, A/D NO; "Tôi vẫn vào" ×2 ⇒ OFF; đóng tay lý do "khác" ⇒ phá luật; mốc giá be (+1,5R / +1R) tính đúng với SL lẻ 0,1; chuỗi SL reset khi hoà; lệnh mở qua 05:00; sửa thẻ phiên khi đang canh kèo sinh dòng vết; ca 13/10 (B tại POC + LVN) để ép quyết định mục 5–6. Ca 6/10 ghi *"R:R ≈ 1:3,5 tuỳ số nhập"* — test không được "tuỳ": chốt số vào 4193,0 · SL 4195,4 · TP 4185,0 ⇒ 1:3,3 (hoặc chọn bộ số khác, nhưng cố định).

39. **[KIỂM THỬ] Lint "nhãn > 9 từ" đếm bằng khoảng trắng sẽ sai với "|delta|", "4193,5", "sell limit"** — ghi cách đếm (tách theo khoảng trắng, bỏ ký hiệu toán). Lint cấm dấu chấm thập phân trong `content.js` nhưng **ô nhập** phải nhận cả "4193.5" (bàn phím số Windows gõ dấu chấm) — ghi rõ để implement không chặn nhầm.

---

## Kết luận

- **Chưa đủ để implement**: còn 12 chỗ sai luật, trong đó 1, 2, 4 làm công cụ in ENTRY cho lệnh hệ thống cấm; cộng với tầng 3 hỏi trùng quá nhiều để dùng được trong 60 giây.
- **Ba việc phải sửa trước:** (1) thêm trục *bias* và *ngược bias* vào bảng bật kịch bản + mục tiêu/cỡ lệnh (mục 1, 2); (2) viết lại tầng 3 thành Canh/Bấm, mỗi sự thật hỏi một lần, SL theo từng kịch bản (mục 3, 23); (3) chốt bằng văn bản ba quyết định HT để mở: B giữa range, LVN, chấm 2 với vùng POC/cụm POC (mục 4–6) và sửa mô hình dữ liệu + danh sách test theo mục 19, 36–38.
- Sau khi sửa ba việc trên, các mục còn lại (giờ mùa đông, limit/huỷ, tin 20:30, chữ) có thể xử lý trong cùng vòng implement 1.
