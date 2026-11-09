## 12. Nhận định (Opus) — số đo, chưa phải kết luận

- **Chưa thấy lợi thế trên TRAIN:** R TB −0,30 [−0,50; −0,09] — KTC nằm hẳn dưới 0. **Kém cả hai đối chứng**: C1 (bỏ ③) −0,24, C2 (ngẫu nhiên cùng giờ/hướng/rủi ro) −0,16; theo cặp R thật − R C2 = −0,14. Như vậy, ở bộ mặc định, ③ không cải thiện so với vào bừa tại mốc. C3: chỉ đòi Δ (−0,10, 99 lệnh) là loại đơn lẻ đỡ tệ nhất; chỉ đòi stacked −0,29.
- **Lệnh rất ngắn, SL sát:** giữ lệnh trung vị 5 nến; rủi ro trung vị 1,29 mbr (≈ 2,2 giá); 18 % lệnh bị sàn 1 mbr đẩy SL ra. WR 27 % so với mức hoà vốn ≈ 36 % ở TP 2R.
- **Phễu:** ③ là cổng rẻ (33 % CF qua ② có ≥ 2 loại dấu hiệu); cổng lọc thật là **4a** (81 % CF qua ③ trượt nến xác nhận) và **R ≥ 1,7** (61 % trượt độc lập). 4,5 lệnh/ngày (trung vị 5, tối đa 8) — trong khoảng kỳ vọng ≤ 8 của plan.
- **Stacked có mặt ở 86 % số lệnh** (> 50 %) ⇒ theo plan ③d, GĐ2 quét run 4. Tổ hợp hay gặp nhất "Δ+stacked" (57 lệnh, −0,36).
- Nhóm `b_from_exhausted` (15 lệnh) +0,31 nhưng KTC [−0,47; 1,10] — mẫu quá nhỏ, không đọc được gì.
- Chặn 19:20–20:30 gần như không đổi gì (bật −0,30 / tắt −0,29; chỉ khác 5 lệnh).

## 13. Điểm vẫn mơ hồ — CẦN FABLE QUYẾT (đang chạy theo lựa chọn in đậm)
1. **G1 — "Lần 2" (Q12) vẫn lỏng và là nhóm đông nhất:** 1.128 ứng viên (32/ngày, còn nhiều hơn bản GĐ0 25/ngày) và **64/159 lệnh (40 %)**. Lý do: "đóng lùi ≥ tol so với cực trị **mới**" (đáy của chính x) dễ hơn bản cũ (so với cực trị cú thủng), và "lần 1" (râu ≥ 1 tick + đóng lùi ≥ tol) xuất hiện ở hầu hết nến trong cú thủng. Plan coi đây là ngoại lệ. Có siết không (vd y phải là nến lập cực trị cú thủng; hoặc x đóng lại ≥ tol so với cực trị của y)? **Đang: theo chữ plan, y = nến thoả gần nhất trước x.**
2. **G2 — CF của "lần 2":** **đang lấy CF = chính nến x** (phải qua 4a), cửa sổ ③ = [max(nến đóng ngoài, x−4), x], mốc (dải ±tol, mức trap, mức "tới mốc" của Δ ngược giá) = cực trị của y. Plan không nói CF có được là 1–2 nến sau x không.
3. **G3 — Mốc trap thế B "cực trị của cú đẩy":** với thế B sell, cực trị cú đẩy là một đáy; quét đáy rồi đóng lên là ngược phe S ⇒ không dùng được làm mốc trap. **Đang dùng {cạnh vừa phá E, pivot 1c gần nhất ngược S}.** Có thể Fable muốn "đỉnh của nến đóng ngoài"?
4. **G4 — ⛔ nhịp quét stop:** "bóng ngược D ở cực trị cú đẩy" **đang hiểu là ô phía −D (≥ 3 × nền, ≥ 10) nằm ở nửa phía D của nến cực trị**; "K nến sau không lập cực trị mới" chỉ xét được khi CF ≥ cực trị + K (trước đó chưa biết ⇒ chưa veto). Cực trị cú đẩy = cực trị từ nến đóng ngoài tới CF. Loại 8,8 % CF qua ③ (độc lập).
5. **G5 — ⛔ range chồng range áp cho "lần 2":** **đang: chỉ cho khi range đã có ≥ 2 FailBreak tính tới x.** Luật chỉ loại 1,8 % thế A (< 30 % ⇒ giữ).
6. **G6 — Thế B có cả mốc cạnh và mốc stacked cùng lúc (16/53 lệnh B):** SL **đang lấy theo mốc cạnh**; chỉ có stacked thì lấy vùng mới nhất. Mốc stacked dùng cho 43/53 lệnh B.
7. **G7 — Chọn lệnh khi đang có lệnh mở:** **đang: ứng viên của một thế bị bỏ vì đang có lệnh thì các CF sau của CÙNG thế vẫn được vào** (nếu còn hợp lệ); một thế đã có lệnh thì hết. C# live phải làm y hệt (ghi để port GĐ3).
8. **G8 — Khoá "mỗi (range, cạnh, thế)":** A và "lần 2" **đang dùng chung nhóm thế A** (cùng cạnh thì chỉ 1 lệnh cho cả hai).
9. **G9 — Δ ngược giá với ΣΔ = 0:** plan viết "ΣΔ ≤ 0" ⇒ **đang tính cả = 0** (2/31 lệnh có dấu hiệu này). Biên độ nhịp so với mbr **tại nến neo x**.
10. **G10 — Q5 đóng TRONG vùng stacked:** **đang coi là "gần"** (khoảng cách âm, chưa xuyên mép xa).
11. **G11 — Tin USD (`IsNewsBlocked`):** Python không có lịch tin ⇒ không chặn (lệch có chủ đích, như plan mục parity).
12. **G12 — Lệnh còn mở qua khoảng trống phiên:** `kernel.simulate` không đổi; đóng `TIME` cuối phiên làm bằng cách gọi `simulate` từng lệnh với `max_hold_bars` = số nến tới hết phiên (`setup_corven.sim_one`). Chỉ 2 lệnh `TIME`.
