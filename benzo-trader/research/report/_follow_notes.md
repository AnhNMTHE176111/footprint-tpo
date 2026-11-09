## 6. Cách Opus hiểu các chỗ plan chưa ghi rõ (chọn cách khớp ảnh gốc, cố định TRƯỚC khi nhìn R)

1. **FailBreak sau khi CF đã bắn không huỷ lệnh.** Ca ảnh vào ở nến thứ 2 sau nến đóng ngoài, còn FailBreak/BreakConfirmed chỉ biết ở nến thứ 3 ⇒ "huỷ mọi ứng viên" chỉ áp cho ứng viên **chưa có CF**; huỷ lệnh đã vào = nhìn trước. Lệnh vào rồi mà cú phá thành giả sẽ là nhãn `MOVE_GIA` lúc mổ SL.
2. **Kết thúc cú phá** khi có nến đóng về phía trong cạnh, tức `(close − E)·D ≤ 0` (đóng trong range = FailBreak trong K nến / ReEntry sau đó; đóng xuyên cạnh đối diện cũng tính), hoặc khi range Merge, hết tuổi 30 nến tính từ nến đóng ngoài, hoặc sang phiên mới. Range BROKEN rồi DEAD ngay vì hết lượt ReEntry vẫn bị kết thúc theo cách đóng giá này.
3. **Leg.** Có cực trị mới trước khi xuất hiện CF thì **cùng leg đó kéo dài**: x dời sang nến mới, nhịp hồi tính lại. Leg kết thúc khi gặp một trong ba trường hợp: (a) có CF; (b) tới x + 3 mà chưa có CF (hết hạn); (c) nhịp hồi quá sâu. Có CF mà move chưa hợp lệ (đẩy ra < 1 mbr hoặc ΣΔ ngược hướng) thì **không có F0** nhưng leg vẫn kết thúc (193 leg, xem phễu). Leg 2 được mở khi một nến vượt cực trị của leg trước; nếu chính nến CF đã vượt thì leg 2 bắt đầu ngay tại nến CF. Move của leg 2 vẫn tính từ nến đóng ngoài gốc (ΣΔ tính trên ref…x′, cùng E).
4. **Nhịp hồi và CF.** CF phải đứng ngay sau một chuỗi nến hồi **liền nhau** bắt đầu từ x + 1. Nếu x + 2 chưa đạt CF nhưng vẫn là nến hồi thì chuỗi nối dài, và x + 3 vẫn có thể là CF. Bản thân nến CF được phép cũng thoả điều kiện nến hồi (đóng < close[x]), vì plan chỉ đòi CF đóng cao hơn **nhịp hồi**.
5. **Cú phá kiểu whipsaw** (một nến vừa FailBreak vừa CloseOutside sang cạnh đối diện, khoảng 38 ca trên TRAIN theo GĐ0) vẫn được tính là cú phá mới theo hướng ngược lại.
6. **`b_from_exhausted`** được xác định ngay ở nến đóng ngoài: range đã có ≥ 2 lần phá thật thì lần này, nếu giữ được, sẽ làm range DEAD ngay. Biết được tại thời điểm đó nên không nhìn trước.
7. **Hai dung sai (tol).** Điều kiện "hồi không quá sâu" dùng tol của range (RangeEngine chốt lúc range sinh, giống `setup_corven` thế B). Cờ S dùng tol = max(2 tick, 0,5 mbr của nến CF).
8. **Cờ S** chỉ kiểm hai thứ: nhịp hồi có râu chạm [Lo − tol, Hi + tol], và không nến nào trong nhịp hồi ∪ CF đóng xuyên mép. Opus **không** thêm điều kiện "vùng chưa bị chạm trước đó" hay "nến tạo vùng phải đóng vượt Hi", vì plan không ghi. Hệ quả: S có ở 62 % F0, nên gần như không lọc được gì.
9. **Cờ Mv:** nhánh "nến thân ≥ 0,7 biên độ và |Δ| ≥ 2 medΔ" không đòi nến đó cùng hướng D (plan không ghi). Mv có ở 82 % F0.
10. **Tập F0 dùng để hoán vị** = F0 trên phiên dày, đã qua Vk, trần SL và các cổng giờ, đồng thời mô phỏng đóng được (TP/SL/TIME). Cột "C1 toàn F0" dùng lệnh thật của chính tập này (1 lệnh mở cùng lúc).

## 7. Câu hỏi cho Fable

1. **F0 = 22,1/ngày, vượt ngưỡng 10/ngày của GĐ-F0** (plan: "2a quá lỏng ⇒ báo lại trước khi đổi"). Opus **không đổi định nghĩa**, vì việc của lượt này là chạy F0 + F1. Nguyên nhân gốc: `CloseOutside` = 97/ngày. Số này khớp GĐ0: FailBreak 1.681 + BreakConfirmed 1.727 = 3.408 sự kiện, ứng với 24,7 range/ngày. Sau trần SL và các cổng giờ còn 451 F0; sau khi chọn lệnh còn 340 lệnh (9,7/ngày). Nếu muốn siết 2a thì đây là sửa định nghĩa **sau khi đã nhìn R** ⇒ phải ghi là hậu kiểm.
2. **Ngưỡng hoán vị bị phồng vì các combo n nhỏ.** Làm đúng chữ plan (max trên cả 10 combo, combo nào rỗng ở một lần hoán vị thì bỏ qua) thì ngưỡng P95 ≈ 1,98R (2.000 lần), do F1 (n F0 = 11) và F5 (n = 2) dao động rất mạnh. Nếu chỉ lấy max trên các combo có ≥ 30 F0 thì ngưỡng ≈ 0,31R. Ở lượt này không combo nào vượt **cả hai** ngưỡng, nên kết luận không đổi. Fable có muốn chốt cách thứ hai cho các vòng sau không (combo có n < 30 đằng nào cũng không được chấm)?
3. **C2 dương rõ (+0,28R ở F0) trong khi F0 −0,05R.** Vào ngẫu nhiên cùng hướng cú phá, ±30′ quanh CF, lại có lời. Opus nghi C2 có thiên lệch dương với setup đi theo cú phá: tập nến ngẫu nhiên gồm cả nến **trước** cú phá, mà hướng vào lại lấy theo cú phá đã xảy ra, nên các nến đó "biết trước" cú phá. Plan chính dùng C2 cho Thế A/B (cùng cơ chế). Nếu Fable thấy đúng, có thể cần C2 chỉ lấy nến **sau** CF. Lượt này giữ nguyên C2 theo plan.
4. **S2 khi leg 2 cách xa cạnh:** SL = min(E, đáy nhịp hồi) − đệm, nên rủi ro thường > 4 mbr và lệnh bị trần SL loại (677 → 476 F0 qua trần SL). S1 giữ được nhiều lệnh hơn (487 lệnh so với 340). Đây là đặc điểm của định nghĩa, không phải lỗi.
5. Danh mục mổ SL (mục 5) có hạng `TIN`, nhưng Python chưa có lịch tin ⇒ GĐ-F2 sẽ phải bỏ hạng này (plan đã cho phép), trừ khi Fable muốn port `NewsCalendar` trước.

## 8. Đối chiếu dự đoán đăng ký trước của Fable (mục 8 plan)

- F0 âm (−0,1…−0,3R): thực tế **−0,05R** (KTC [−0,20; 0,10]), tức âm nhẹ hơn dự đoán.
- F1/F5 n < 30: **đúng**; F2 và F4 cũng n < 30 (F4 không có lệnh nào: T và Bc không trùng nhau trên F0 nào qua được cổng).
- "1–2 combo dương nhưng không qua hoán vị": **đúng**. F7 (+0,20, dương cả hai nửa) và F10 (+0,12) dương, nhưng không qua C2 + 0,15 và không qua ngưỡng hoán vị (p cực đại 0,76 / 0,84). F7 có p thô 0,049 (< 0,05) nhưng không qua p cực đại; theo plan mục 8.2, combo như vậy **không** được gọi là có lợi thế. Hai combo này không nằm trong nhóm Fable đoán {F2, F4, F8, F9}.
- Có combo ĐẠT: **không** ⇒ theo 4.7 **không mở TEST**. Theo 4.5 cũng không combo nào lọt vòng trong, vì tất cả đều thua C2 của chính mình ⇒ GĐ-F2 (mổ SL) không có đối tượng hợp lệ. Fable quyết bước tiếp theo.

## 9. Lượt 9.3-A (Opus, 2026-11-09, hậu kiểm — chỉ TRAIN)

- **C2' đã thay C2 làm cột chấm.** Cấu hình chính, số lệnh và R TB của mọi combo **không đổi** (cùng 340 lệnh F0, F7 +0,20, F10 +0,12…); chỉ đối chứng đổi.
  C2 → C2': F0 +0,28 → **−0,02** · F1 +0,84 → +0,51 · F3 +0,31 → −0,06 · F7 +0,33 → **+0,05** · F10 +0,35 → **+0,01**. Dự đoán đăng ký trước của Fable
  (C2' của F0 rơi về −0,10…+0,05): **đúng** (−0,02).
- **Lọt vòng trong theo C2' (n ≥ 30, ≥ C1, ≥ C2'): F3, F7, F10.** Không combo nào ĐẠT: F7 chỉ vướng đúng một điều kiện — Δ 0,201 < ngưỡng hoán vị
  ≥ 30 F0 = 0,314 (p cực đại ≥ 30 = 0,23); F10 vướng < C2'+0,15, KTC dưới ≤ −0,10, hoán vị; F3 vướng mọi tiêu chí trừ n.
- **F3 lọt vòng trong** nhưng plan 9.2/9.3-B chỉ giao mổ F7, F10 (+ F1 xem) ⇒ lượt này **chưa** mổ F3 (R TB +0,00 [−0,29; 0,33], dương nửa 1 / âm nửa 2) — Fable quyết.
- **S3** (leg 2 neo cực trị leg 1): giữ được nhiều lệnh hơn S2 (F0 409 so với 340, vì ít lệnh vượt trần 4 mbr) nhưng R TB F0 như nhau (−0,05); F7 +0,12 (n 112), F10 +0,11 (n 147).
- **move_mbr 1,5**: F0 −0,02 (n 297), F7 +0,16 (n 82), F10 +0,03 (n 105). Cả hai biến thể **không có sức chọn**, chỉ báo.
- C2' bỏ lệnh khi pool < 5 nến sau CF (cuối phiên): F0 còn 6.778/6.800 lệnh giả.
- Mổ SL vòng 1 (F7, F10; F1 chỉ xem): `report/MO-SL-FOLLOW.md`, ảnh `report/follow_shots/`, nhãn máy `report/_mo_sl_follow.csv`.
