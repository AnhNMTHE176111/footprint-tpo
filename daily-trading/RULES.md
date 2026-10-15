# Luật giao dịch — chốt 2026-09-29

Rút ra từ nhật ký 16/9 → 25/9 (50 lệnh, +13R). Mọi luật dưới đây đều là câu
chính người học đã tự viết trong nhật ký, chỉ gom lại thành dạng kiểm được.

## A. Trước khi bấm — 4 câu, thiếu 1 câu thì không vào

1. **Gọi tên setup.** Chỉ 4 tên: `phá hồi` · `fade cạnh` · `hấp thụ` · `trap`.
   Không gọi được tên ⇒ không vào.
2. **Bối cảnh của tên đó có đúng không?** (bảng mục B). Tên đúng + bối cảnh sai
   = lệnh hỏng. Đây là lỗi chính của 24/9.
3. **Đang có lệnh mở không?** Có ⇒ không vào. Nhồi lệnh = 0.
4. **Range đã phá chưa?** Chưa phá ⇒ chỉ fade hai cạnh, giữa range không lệnh nào.

## B. Bối cảnh bắt buộc của từng setup

| Setup | Bắt buộc phải có trước đó | Loại bỏ nếu |
|---|---|---|
| **trap buy/sell** | một move giảm (hoặc tăng) rõ + nhịp hồi ngược | bối cảnh sideway — 24/9 hai lệnh, −1R |
| **hấp thụ** | bên chủ động đẩy mạnh tại vùng mà giá không đi (delta giảm dần, thân nến ngắn dần) | cùng lúc đang phá VWAP / cạnh VA ⇒ đó là **phá hồi**, phải follow |
| **fade cạnh** | giá ở đúng cạnh range **chưa phá** + delta ủng hộ hướng vào | thân nến cf ngắn, hoặc râu ngược dài |
| **phá hồi** | đã phá cạnh + hồi về cạnh + nến cf | chưa phá thật, mới chỉ chạm |

## C. Luật xung đột

- **Hấp thụ vs phá hồi cùng lúc ⇒ theo phá hồi.** Không cản tàu.
  (Tự viết 2 lần: 17/9 "cản tàu là đứt tay", 24/9 "ko nên cản tàu, nên flow".)
- **Sau nến tăng/giảm dài mạnh ⇒ không vào ngay.** Chờ hồi về, không hồi thì bỏ.
  Vào ở lưng move là không có điểm tựa đặt SL. Nến dài rất hay là trap.
- **Chạm cạnh VA ⇒ chỉ làm 2 việc:** chờ break thành công, hoặc chờ đảo chiều.
  Không đoán trước.

## D. Sau khi vào lệnh

- **Chưa dời SL về be:** để nguyên, không sờ vào.
- **Đã dời SL về be:** chỉ thoát bằng TP hoặc bằng SL be. **Cấm đóng tay vì sốt
  ruột / thấy râu dài.** Muốn đóng tay thì phải gõ được lý do có tên
  (đúng một lý do hợp lệ: **có hấp thụ ngược chiều đe dọa TP**) vào nhật ký
  *trước* khi bấm đóng.
- Target theo setup: hấp thụ & phá hồi ⇒ 3R · fade cạnh & follow ⇒ 2R.

## E. Ghi sổ (đang là chỗ yếu nhất)

Mỗi lệnh ghi đủ 5 cột: **giờ | hướng | setup | đúng luật? (Đ/S) | R**.
Cuối phiên **cộng tay** rồi mới viết tổng lên tiêu đề ngày.

Hiện có 3 phiên tổng sai: 18/9 ghi +0R (thực +1R) · 24/9 ghi +1R (thực +2R) ·
25/9 ghi +0R (thực −1R). 22/9 còn một lệnh bỏ dở chưa có kết quả.

## F. Ngắt mạch

**Hai lệnh phá luật trong một phiên ⇒ tắt máy.** Chỉ số theo dõi duy nhất là
**số lệnh phá luật/phiên**, không phải lãi lỗ.

---

## G. Bổ sung 2026-10-15 (từ `REVIEW-2026-10-15.md`, đề xuất — người học chốt)

1. **Bài kiểm tra cơ chế trước khi gọi tên** (thay vì chỉ gọi tên):
   - Nhịp hồi hình **V** (bật thẳng, nến dài, delta mạnh) ⇒ phe hồi đang thắng ⇒ **không** gọi là
     "phá hồi" theo chiều cũ.
   - **Bong bóng to** (≥100) ở đáy/đỉnh ⇒ phe đó đang hấp thụ ⇒ **không vào ngược** bong bóng.
   - Thân nến + delta **tăng dần** = đà, **giảm dần** = hấp thụ. Nhầm hai cái này = lệnh hỏng.
2. **Đặt SL:** sau cấu trúc (râu gần nhất / cạnh vùng) **+ đệm**, và **không ngắn hơn chiều cao
   nến M1 lớn nhất trong 5 nến trước**. SL 1 giá khi nến đang cao 3 giá là tự nộp tiền.
3. **Vào lại cùng vùng tối đa 2 lần.** Lần 3 = phá luật = tính vào ngắt mạch F.
4. **Bias trước phiên:** một dòng đầu ngày — "ưu tiên buy/sell vì (TPO ngày/tuần, VWAP tuần)".
   Lệnh ngược bias phải ghi lý do trước khi bấm.
5. **Ghi sổ:** bảng 5 cột (giờ | hướng | setup | Đ/S | R) ngay dưới tiêu đề ngày; tiêu đề ngày
   chỉ được điền sau khi cộng cột R.
