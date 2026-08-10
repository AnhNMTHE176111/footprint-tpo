# Chấm bài #13 — Chưa rõ (SC) (ACC?) · 2026-05-04 15:22 → 2026-05-05 08:10 (398 nến M1)

**Điểm: 5/10** — Khung range vẽ ĐÚNG (mở range chuẩn, Phase A đẹp), nhưng phần đuôi hỏng: không chịu đặt tên dù đã có SOS + Phase D, và Phase C phình dài hơn Phase D.

## Lỗi (nặng → nhẹ)

### 1. Đã có SOS + Phase D mà vẫn để "Chưa rõ (SC)" — luật vi phạm: L4
- **Thuật toán gắn:** tiêu đề "Chưa rõ (SC) (ACC?)", trạng thái `superseded`, không đặt tên 4 mẫu hình.
- **Đúng phải là:** **Tích luỹ (ACC)**. Origin = SC (move giảm 52.1 giá bị chặn) + hướng phá thật = LÊN (SOS 4599.6 đóng cửa trên cả biên phụ 4596.1, giá sau đó ở lại 4599-4603).
- **Dấu hiệu quyết định trên chart:** phiếu ghi đủ SOS (07:13, VSA 4.31x, thân 1.00) và LPS[D] (07:56, 4588.2 — retest đúng biên chính trên rồi giữ được). Đủ cả cặp CBR của L10 mà vẫn không dám gọi tên.
- **Nghi phạm trong thuật toán:** nhánh `superseded` chặn việc đặt tên. Trạng thái `superseded` chỉ nên chặn tên khi Phase E CHƯA hoàn tất; ở đây Phase D đã trọn vẹn nên phải đặt tên rồi mới nhường chỗ cho range con.

### 2. Phase C (59 nến) dài hơn Phase D (26 nến) — luật vi phạm: L8
- **Thuật toán gắn:** C = 04:55 → 07:08 (59 nến), D = 07:13 → 08:10 (26 nến).
- **Đúng phải là:** Phase C là phase NGẮN NHẤT. Ở đây điểm chuyển thật là cú mSOS 06:01 (4596.1, VSA 4.00x) — Phase C nên co lại quanh nhịp test cuối trước cú đó, khoảng 10-15 nến.
- **Dấu hiệu quyết định:** LPS[C] đặt tại 4575.3 = **55% chiều cao biên chính** (4559.8-4588.3) — chính giữa range, không gần biên nào. Trên ảnh nó nằm lơ lửng giữa khung.
- **Nghi phạm:** đây là tác dụng phụ của việc **bỏ ràng buộc "đúng nửa range"** (13.1c). Ràng buộc nửa range bị gỡ hẳn nên pivot gán ngược rơi vào giữa. Cần thay bằng: pivot phải nằm ở nửa ĐỐI DIỆN hướng phá + trần tuyệt đối `len(C) ≤ min(len(B), len(D))`.

### 3. Phase B 287 nến chỉ có đúng 1 nhãn — luật vi phạm: L9
- **Thuật toán gắn:** một mSOW duy nhất ở 20:20.
- **Đúng phải là:** trên ảnh Phase B chạm biên dưới ~4556 ít nhất 4 lần (16:35, 17:29, 18:43, 20:08) và chạm biên trên một lần quanh 4588 (02:05). Tối thiểu phải có 1 ST[B] và 1 UT[B].
- **Dấu hiệu quyết định:** phiếu ghi SOT-dn = SOT thật (n=4, thrust cuối/đầu 0.09, volume 0.86 = cạn kiệt) — máy ĐÃ đo được chuỗi 4 nhịp đẩy xuống rút ngắn dần nhưng không gắn nhãn nào cho chúng.
- **Nghi phạm:** nhãn UT[B]/ST[B] chỉ sinh ra từ nhánh "thò ra ngoài biên chính rồi rút về"; các nhịp chạm biên mà không thò ra thì không được ghi gì.

### 4. Nhãn SC nằm trước nến mở range — luật vi phạm: mục 3(3) THEORY / lỗi cụm climax
- **Thuật toán gắn:** nhãn SC ở 15:21 (giá 4560.8, VSA 2.70x); nến mở range là 15:22 (giá 4559.8, VSA 1.51x).
- **Đúng phải là:** nhãn và mốc mở range phải trùng nến, hoặc ít nhất nhãn không được nằm TRƯỚC nến mở range.
- **Ghi nhận:** lệch 1 nến / 1.0 giá — nhẹ nhất trong lô, chấp nhận được về mặt đọc chart. Lỗi đã biết, chưa sửa.

### 5. Range bị cắt vụn với bài #14 (trình bày + cấu trúc)
- Bài #14 mở lúc 07:36 trong khi bài này còn chạy tới 08:10 — hai range chồng lấn 34 nến, cùng mô tả một cú bứt lên. Cơ chế SIDEWAYS tách một cấu trúc thành hai.

## Đạt
- **Mở range (L1): ĐẠT tốt.** MOVE giảm 52.1 giá / 32 nến / hiệu suất 0.70 — move xu hướng rõ, climax chặn đúng đáy.
- **Phase A (L2): ĐẠT.** SC → AR (4588.3) → ST[A] (4556.0) đủ 3 lần đổi hướng; ST[A] hồi **113%** khoảng AR↔climax, tức test đúng vùng climax (thủng nhẹ 3.8 giá = 13% chiều cao) chứ không lửng giữa range. Ngưỡng `STA_MIN_AR_FRAC=0.55` chạy đúng ở ca này.
- **Biên chính (L3): ĐẠT.** 4559.8 (climax) + 4588.3 (AR), cố định suốt range, không bị kéo theo giá.
- **Biên phụ + thứ tự SOS (L3): ĐẠT — điểm sửa v7.1 ăn đúng ở đây.** mSOS 06:01 thất bại nới biên phụ lên 4596.1; SOS 07:13 sau đó phải vượt qua đúng mức đó (4599.6, +35 tick). Không còn cảnh "tự nới rồi tự vượt".
- **Tỉ lệ phase (L9): ĐẠT.** B = 287 nến, dài nhất tuyệt đối.
- **Khối lượng:** SOS VSA 4.31x thân 1.00, LPS[D] VSA 0.47x (test co lại) — đọc đúng effort↔result ở đoạn phá.
