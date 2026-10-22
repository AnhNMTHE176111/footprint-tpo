## Đánh giá viết tay (Opus, 2026-10-22) — theo đúng tiêu chí T0/T1/T2 đã khai báo

**Kết luận: KHÔNG đạt T0, T1, T2 ⇒ C vẫn TẮT, KHÔNG port C#, không mở thêm vòng tinh chỉnh trên D90.** Chưa chứng minh được gì.

1. **Mục tiêu người dùng ("tăng lệnh, WR không giảm") đạt về hình thức, không đạt về tiền.** C4 tăng lệnh/ngày 1,69 → 3,13 (+85%), WR giữ
   12,6%, R TB bớt âm (−0,43 → −0,31) — nhưng tổng R lỗ sâu hơn (−44,7 → −58,8) vì thêm nhiều lệnh vẫn âm. Đúng điều plan đã cảnh báo:
   ở WR 10–17% với TP ≥ 2R, tăng lệnh = tăng lỗ. T0 trượt ở TEST: −0,15 (C4) < −0,12 (C0).
2. **Cổng hình dạng D (phần 1).** Lệnh A/EU giảm 63 → 14. Ngày D: R TB −0,31 so với −0,54 ngày khác — hướng đúng, nhưng hoán vị nhãn
   cho p = 0,30 (cần ≤ 0,10) và n = 14 ⇒ **không phân biệt được với may rủi**. Ngày P/b chỉ có 6 phiên / 10 lệnh ⇒ không đánh giá được.
3. **VA nhỏ CHoCH (phần 2).** 240 VA sinh, 129 lệnh (2,11/ngày), WR 10,1%, R TB −0,33; TRAIN −0,41 / TEST −0,25. **Không vượt đối chứng
   nào** (dời vùng, vào ngẫu nhiên tại vùng, VA giả dời thời gian, khớp khoảng cách) ⇒ vị trí VA_C không mang thông tin đo được — cùng kết luận
   các vòng VCL/HVN trước. Ô "DN, cạnh phía AR" dương (+0,12, n 36) là ô chia nhỏ SAU khi xem số ⇒ không được coi là phát hiện.
4. **Máy chưa giống ý trader — nói thẳng 2 chỗ:** (a) zigzag 2 giá của kernel quá dày với biên độ M1 hiện tại (pivot gần như mỗi 2 nến), nên
   "đổi hành vi" xảy ra liên tục; (b) luật nới 0,25·h cho VA **leo theo xu hướng** từng bậc (VA #13 nới 8 lần, có VA nới 44 lần) ⇒ nhiều VA_C
   không còn là vùng cân bằng; 152/240 VA chết vì phá biên. Đây là giới hạn của định nghĩa đã duyệt (R5), không sửa sau khi xem số.
5. **Lệch mắt ↔ máy cần người học chấm:** ảnh "P" đầu tiên (`img/c_v6_shape_P.png`) nhìn bằng mắt giống HAI vòm hơn là P — luật "hai đỉnh"
   dùng `find_hvn` (≥ 1,5×TB) bỏ sót. Phải làm bài săn bằng chứng (gắn nhãn 15 phiên + tìm 5 VA_C trên Optimus Flow) TRƯỚC khi tin bảng nhãn.
6. **Độ nhạy:** hai dòng nhìn đẹp hơn (bỏ điều kiện "bị chặn": C3 −0,16; ngày D dùng VA TPO: C1 TEST +0,25) — **không được chọn** vì đã
   xem số (mục 3.5). Muốn thử thì phải đăng ký trước và đo trên dữ liệu MỚI (forward), không phải D90.
7. **Rủi ro còn mở:** R6 — người dùng chưa xác nhận "indicator VWAP có CHoCH" là WyckoffRunner; R1 — neo phiên Globex 05:00 VN (Bài số 0 chưa
   sửa) quyết định nhãn hình dạng.
