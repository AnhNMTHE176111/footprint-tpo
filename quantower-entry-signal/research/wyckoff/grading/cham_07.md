# Chấm bài #07 — Tái tích lũy (RE-ACC) · 2026-04-13 16:47 → 04-14 06:26 (265 nến M1)

**Điểm: 7/10** — Vẽ đúng về cấu trúc, tên range đúng; sửa vài nhãn (ST[A], LPS[C], nhãn SOS neo sai cây, thiếu LPS[D]).

## Lỗi (nặng → nhẹ)

### 1. SOS không đóng cửa bứt qua biên phụ, và nhãn neo sai cây — luật vi phạm: L3 (SOS mạnh phải qua biên PHỤ) + lỗi B của v4
- **Thuật toán gắn:** SOS tại 23:30, giá **4817.3**, VSA **1.88x**, thân 0.80.
- **Đúng phải là:** biên phụ trên là **4810.9** (do chính ST[A] tạo ra). 4817.3 > 4810.9 nên về mức giá thì có qua — chỗ này ĐẠT. Nhưng VSA 1.88x là **dưới ngưỡng climax 2.2x**, trong khi nhìn panel volume ở đoạn 04-14 05:48–06:48 có một loạt cột vàng cao vượt trội (VSA rõ ràng ≥ 2.2x). Cây phá thật mang lực nằm ở đó, không phải cây 23:30. Logic "neo hồi tố vào cây VSA cao nhất trong đoạn" (v5, lỗi B) chỉ quét trong cửa sổ xác nhận 3 nến nên bỏ sót.
- **Dấu hiệu quyết định trên chart:** nhãn SOS đặt tại một cụm nến nhỏ li ti (biên độ hẹp) ở 23:30, còn thân nến lớn kèm volume nổ thì ở tận 04-14 05:48 trở đi.
- **Nghi phạm trong thuật toán:** cửa sổ tìm "cây phá thật" quá hẹp. Nên mở rộng ra toàn bộ đoạn từ nến thò ra tới nến xác nhận thứ 3, và ưu tiên nến vừa VSA cao vừa thân ≥ 45%.

### 2. ST[A] vượt hẳn qua mức climax, không còn là "test" — luật vi phạm: L2 + L3
- **Thuật toán gắn:** ST[A] tại 17:27, giá **4810.9**, tức **cao hơn mức climax 4806.7 là 4.2 giá**, VSA 0.58x, thân 1.00.
- **Đúng phải là:** L2 định nghĩa ST[A] = "quay lại phía climax rồi **bị chặn** lần nữa". Ở đây giá không bị chặn tại climax mà **vượt qua** nó. Đúng luật L3 thì cú này tạo biên phụ trên (máy có làm: 4810.9) — nhưng nó nên mang tên **UT** (thăm dò nhẹ trên đỉnh, origin BCLX, VSA 0.58x là rất nhẹ), rồi ST[A] thật phải là cú test **trước đó** hoặc Phase A còn chưa xong.
- **Dấu hiệu quyết định trên chart:** chấm ST[A] nằm **trên** đường liền cam "bien CHINH tren 4806.7", nằm đúng trên đường đứt "bien phu tren 4810.9" mà nó tự tạo.
- **Nghi phạm trong thuật toán:** mục 4.2 chỉ đặt **trần** "vượt quá 1 lần chiều cao range thì bỏ ứng viên" (21.0 giá) — vượt 4.2 giá thì lọt. Nhưng không có luật nào nói ST[A] được phép vượt climax rồi vẫn là ST[A]. Nên: nếu nhịp hồi đóng cửa vượt mức climax → gán UT/DA, tiếp tục chờ ST[A] thật.

### 3. Phase E (121 nến) dài hơn Phase B (69 nến) — luật vi phạm: L9 (Phase B là phase dài nhất)
- **Thuật toán gắn:** A 36 · B 69 · C 19 · D 21 · **E 121**.
- **Đúng phải là:** Phase B phải là phase dài nhất trong cấu trúc. Ở đây E dài gần gấp đôi B. Về bản chất thì Phase E là "giá đã rời range đi tìm vùng giá mới" — nó không còn thuộc vùng đấu giá nữa, nên kéo dài 121 nến chỉ nói lên rằng **range đã hết vai trò từ lâu mà máy vẫn giữ**. Nhìn ảnh: từ 04-14 00:41 trở đi giá chạy hẳn lên vùng 4826–4855, cách biên trên 20–45 giá. Nên đóng range sớm hơn.
- **Nghi phạm trong thuật toán:** mục 7 — "Phase E kéo tới khi giá đi xa 2× chiều cao / hết 120 nến" (v5, vá lỗi J). Vá xong thì E chạm đúng trần 120 → cùng bệnh với Phase C chạm trần 121 ở v4. Trần đang là thứ quyết định, không phải cấu trúc.

### 4. Thiếu LPS[D] — luật vi phạm: L10 (Phase D+E = CBR: phá → retest giữ ngoài biên → đi tiếp)
- **Thuật toán gắn:** Phase D dài 21 nến nhưng **không có nhãn nào** trong D ngoài chính SOS.
- **Đúng phải là:** CBR bắt buộc có nhịp hồi retest. Nhìn ảnh đoạn 04-14 00:41–01:46 giá có lùi về quanh 4826–4830 rồi mới đi tiếp — đó là nhịp retest, nhưng nó lùi về **cách biên trên 4806.7 tới ~20 giá**, tức không chạm biên. Vậy đây là ca "phá xong chạy thẳng, không retest biên" — hợp lệ, giống Ca #21 nguồn 7.pdf (không phải TR nào cũng có BU ở Phase D). **Không tính là lỗi cấu trúc**, nhưng nếu không có LPS[D] thì Phase D 21 nến chỉ là khoảng trống — nên gộp vào E hoặc ghi rõ "D không có retest".
- **Nghi phạm trong thuật toán:** dung sai gom LPS[D] = 20 tick (2.0 giá) quanh biên vừa phá — quá chặt cho một cú phá đi xa.

### 5. LPS[C] gán ngược, đặt ở đỉnh chứ không phải đáy nhịp test — luật vi phạm: L8 (case khó, gán ngược từ SOS)
- **Thuật toán gắn:** LPS[C] tại 20:38, giá 4799.5.
- **Đúng phải là:** đây là ca gán ngược (range không có Spring/Shakeout/UTAD). Máy nhìn lùi 60 nến trước cú phá và lấy "đáy sâu nhất". Nhưng nhìn ảnh, chấm LPS[C] nằm ở **sườn xuống của một nhịp đang giảm** (giá vừa từ ~4804 xuống), không phải điểm quay đầu. Đáy thật của nhịp test cuối nằm thấp hơn một chút, ngay sau đó. Sai lệch nhỏ, chấp nhận được nhưng chưa trùng chỗ mắt người chọn.
- **Nghi phạm trong thuật toán:** mục 6 case khó — chọn "cực trị trong 60 nến" thay vì "swing pivot cuối cùng được xác nhận". Chính tài liệu đã tự nghi ngờ (mục 12.8).

## Đạt
- **Tên range đúng:** BCLX chặn move tăng, sau đó phá **lên** → **Tái tích luỹ**. Đúng bảng L4, và đúng chỗ mà bản v2/v3 từng xoá oan range.
- Điều kiện mở range chuẩn: climax VSA **2.72x**, biên độ 5.5 giá, MOVE 42.4 giá / 60 nến / hiệu suất 0.36 — trên chart đợt tăng từ ~4760 lên 4806 là move thật, cây climax nằm đúng đỉnh chặn move (L1 ĐẠT cả cần lẫn đủ).
- Biên chính 4785.7–4806.7 cố định suốt range, không kéo theo giá (L3).
- Biên phụ đúng luật: mỗi bên **đúng 1** cái (trên 4810.9, dưới 4783.2), đều là cực trị xa nhất thật (L3).
- DA gán đúng vai: cú thọc xuống 4783.2 VSA 0.70x — thăm dò nhẹ dưới biên AR, ở lại Phase B, chỉ nới biên phụ. Đúng mục 5.1.
- Phase C 19 nến — ngắn hơn B (69n), đúng L8. Không còn bệnh Phase C 121 nến của v4.
- Đọc effort↔result đúng: nhìn panel volume, nửa đầu range (16:47–20:37) volume lèo tèo, sang 04-14 05:00 trở đi cột vàng dày đặc — cầu vào thật ở cuối, hợp với tái tích luỹ.
