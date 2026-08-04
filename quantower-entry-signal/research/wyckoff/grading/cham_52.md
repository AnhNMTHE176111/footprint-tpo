# Chấm bài #52 — Chưa rõ (BCLX) (DIST?) · 2026-07-24 14:00 → 20:59 (419 nến M1)

**Điểm: 8/10** — **vẽ đúng.** Đây là bài sạch nhất trong lô: Phase A mẫu mực, biên chính đúng chỗ, mỗi bên một biên phụ, và quan trọng nhất là **không ép đặt tên** khi chưa có cú phá thật. Chỉ trừ điểm ở chỉ số SOT không bắt được chuỗi đỉnh giảm dần rất rõ và ở cách ghi trạng thái "completed".

## Lỗi (nặng → nhẹ)

### 1. SOT phía trên báo `none(n=0)` trong khi chart có chuỗi đỉnh rút ngắn kinh điển — luật vi phạm: THEORY §7 (SOT), là **lỗi đo sai bản chất** của chỉ số v6
- **Thuật toán gắn:** `SOT phía TRÊN: trạng thái=none, n=0`.
- **Đúng phải là:** đọc trên ảnh, các đỉnh liên tiếp trong Phase B là **4085.2 → ~4083 → ~4078 → 4073 → ~4066 → ~4062** — sáu nhịp đẩy lên ngắn dần đều, thừa điều kiện "≥3 lần đẩy" của THEORY §7. Đây chính là dấu hiệu #1 của phân phối (§4.4): cung tăng dần, mỗi lần đẩy lên yếu hơn. Chỉ số đáng giá nhất của cả range lại bị bỏ trắng.
- **Dấu hiệu quyết định trên chart:** đỉnh 4085.2 (15:20, cụm volume cao nhất chart tại 15:05) rồi không đỉnh nào chạm lại được 4073 sau 16:33; giá đóng cửa cuối range 4055 — dưới cả biên chính dưới.
- **Nghi phạm trong thuật toán:** bộ dò nhịp SOT nhiều khả năng chỉ đếm các nhịp **vượt biên** hoặc yêu cầu pivot xác nhận quá chặt (cùng cơ chế 5 nến / 1.5× ATR như AR), nên các đỉnh nội bộ range không được ghi. Bằng chứng gián tiếp: SOT báo `none` ở cả 3 bài 51/52/53, chỉ bài 50 có số — chỉ số này đang **im lặng ở đa số ca**, tức ngưỡng phát hiện quá cao.

### 2. Trạng thái ghi "completed" trong khi range bị khe cuối tuần cắt — lỗi TRÌNH BÀY
- **Thuật toán gắn:** `Trạng thái range: completed`, dải phase chỉ A → B.
- **Đúng phải là:** range này không hoàn tất cấu trúc (không có C/D/E); nó **bị cắt** vì khe thời gian > 4 giờ (nến kế tiếp trên trục là 26/07 22:41 — nghỉ cuối tuần). Ghi "completed" khiến người đọc tưởng đây là kết luận cấu trúc, trong khi thực chất là "hết dữ liệu liền mạch".
- **Nghi phạm trong thuật toán:** nhánh cắt range theo khe (lỗi K của v5) dùng chung trạng thái kết thúc với range chạy đủ Phase E. Nên có trạng thái riêng, ví dụ `cut_by_gap`.

### 3. Nhãn mSOS/mSOW không được neo hồi tố vào cây phá thật — lỗi nhẹ, cùng họ với lỗi B của v4
- **Thuật toán gắn:** `mSOS 15:20 @4085.2 VSA 1.56x`.
- **Đúng phải là:** cây phá thật của nhịp đó là cụm 15:05 — thanh volume **cao nhất toàn chart** (nhìn panel dưới). Nhãn nên hồi tố về đó giống cách đã làm cho SOS/SOW.
- **Dấu hiệu quyết định trên chart:** đỉnh cột volume vàng ở 15:05 cao hơn hẳn mọi cột khác; nến mang nhãn chỉ 1.56×.
- **Nghi phạm trong thuật toán:** phép neo hồi tố (v5, lỗi B) chỉ áp cho nhánh SOS/SOW xác nhận, chưa áp cho nhánh hạ cấp mSOS/mSOW.

## Đạt
- **Phase A (L2) mẫu mực:** BCLX @4073.0 (đóng cửa đúng tại đỉnh, VSA 3.09×, thân 0.70) → AR @4058.4 → **ST[A] @4072.3**, cách vùng climax đúng **0.7 giá**. Đây là ST[A] chuẩn nhất trong cả lô 50-53: test lại đúng vùng climax, không thủng qua, không rơi giữa range. Phase A kết thúc đúng tại ST[A], dài 27 nến.
- **Mở range (L1):** MOVE tăng 24.6 giá / 42 nến / hiệu suất 0.42; climax là đỉnh cao nhất cửa sổ và nến +1 đảo chiều ngay với VSA 3.09× — climax thật sự **chặn** move.
- **Biên (L3):** biên chính 4058.4–4073.0 = climax + AR, không bị kéo theo giá; biên phụ đúng **một cái mỗi bên** (4085.2 trên, 4051.3 dưới), đều là cực trị xa nhất. Tỷ lệ 2.32× — biên chính vẫn mô tả được vùng lõi (nhìn ảnh, phần lớn 393 nến Phase B nằm quanh dải này).
- **Phase B (L9)** dài nhất tuyệt đối: 393/419 nến. Đúng tinh thần "B là phase dài nhất".
- **Không ép đặt tên (L4):** cú thọc lên 4085 giữ ngoài biên gần 80 nến rồi thu hẳn vào trong → theo quyết định đã chốt của người học (shock thất bại → mSOS/mSOW, **ở lại Phase B**) thì gọi mSOS là đúng luật, không được nâng thành UTAD. Cú xuống 4051.3 rồi hồi lên đóng cửa trên 4058.4 → cú phá bị vô hiệu → mSOW, cũng đúng. Kết quả: range đóng ở "chưa rõ hướng" — trung thực, không tái phát lỗi F.
- Bias `+0` (test cả hai biên) khớp hình.
- Không có nhãn dư, không spam LPS, không có nhãn sai vai.

## Cần hỏi người học
- Range đóng vì khe cuối tuần trong khi cấu trúc còn dở (mới A→B) và giá đang đóng cửa **dưới** biên chính dưới. Sau khe, muốn xử lý thế nào: bỏ hẳn range này, hay cho phép mở lại range mới lấy 4058.4/4073.0 làm biên tham chiếu?
