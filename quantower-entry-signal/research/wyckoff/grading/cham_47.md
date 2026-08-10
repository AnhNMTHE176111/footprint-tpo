# Chấm bài #47 — Chưa rõ (SC) (ACC?) · 2026-07-07 19:18 → 2026-07-08 03:26 (427 nến M1) · superseded

**Điểm: 5/10** — Cấu trúc tốt nhất trong lô về mặt khung và cú phá, nhưng bị tước tên vô cớ và ST[A] vẫn sai chỗ.

## Lỗi (nặng → nhẹ)

### 1. Range bị đóng `superseded`, mất tên, dù cú phá đã hoàn tất trọn vẹn — luật vi phạm: L4, L10
- **Thuật toán gắn:** "Chưa rõ (SC)", không đặt tên 4 mẫu hình.
- **Đúng phải là:** **Tích luỹ (ACC)**. Đủ cả ba mắt xích của L10: SOS 03:01 VSA **6.30x** thân 0.85 (cây phá mạnh nhất cả range), LPS[D] 03:18 tại 4135.7 **giữ được ngoài biên chính 4128.9**, rồi giá đi tiếp.
- **Dấu hiệu quyết định:** range con #48 sinh tại **03:13** trong khi range này còn chạy tới 03:26 và LPS[D] của nó nằm ở 03:18 — nhãn Phase D của cha nằm lọt trong Phase A của con. Lỗi giống hệt cặp #45/#46.
- **Nghi phạm:** cơ chế SIDEWAYS (mục 5.4) không kiểm "cha đã hoàn tất CBR chưa" trước khi spawn con. Cần chặn spawn khi range cha đang ở Phase D với cú phá chưa bị vô hiệu.

### 2. ST[A] lơ lửng 44% chiều cao, cắt Phase A ngay TRƯỚC cú test thật — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 20:51 tại 4114.2, Phase A đóng tại đó.
- **Dấu hiệu quyết định:** biên chính 4102.7–4128.9 = 26.2 giá; (4114.2−4102.7)/26.2 = **44% chiều cao**. Retrace từ AR = 0.561 — **vừa lọt ngưỡng 0.55**. Trên ảnh, ngay sau mốc đó (20:53) có một cây đỏ dài về ~4106 — đó mới là cú test vùng SC.
- **Nghi phạm:** cùng một nguyên nhân với #43 và #45. Ba bài liên tiếp ST[A] rơi vào dải 42–44% chiều cao với retrace 0.56–0.58. `STA_MIN_AR_FRAC=0.55` **không** chạm gốc rễ — cần ràng buộc theo khoảng cách tới climax (ST[A] phải nằm trong 1/3 phía climax, THEORY §5).

### 3. Nhãn SC nằm trước nến mở range 3 nến và lệch 4.6 giá khỏi biên chính — luật vi phạm: L3
- **Thuật toán gắn:** nhãn SC tại **19:15**, giá 4107.3; range mở 19:18; biên chính dưới **4102.7**.
- **Dấu hiệu quyết định:** trên ảnh chấm SC treo cách hẳn đường liền cam phía dưới. Nến 19:15 (VSA 2.94x) là cây volume lớn nhất cụm, nhưng nến 19:18 (low 4102.7, VSA 1.53x, biên độ 9.7 giá) mới là cây tạo biên.
- **Nghi phạm:** lỗi cụm climax "kẹp một phía", 13.1c ghi rõ đã thử sửa rồi revert vì mất 7 climax thật. Đây là cái giá phải trả — hiện đang trả ở **hầu hết** range.

### 4. mSOS neo vào nến rác — luật vi phạm: định nghĩa mSOS (mục 5.1 spec)
- **Thuật toán gắn:** mSOS 00:44 tại 4137.1, **VSA 0.63x, thân 0.27**.
- **Dấu hiệu quyết định:** trên panel volume, đợt đẩy lên 4137 quanh 00:40–00:46 có mấy thanh vàng rõ, nhưng nhãn rơi đúng vào cây volume dưới trung bình. Cùng lỗi với #44 và #46.

### 5. Phase C (28 nến) dài hơn Phase D (26 nến) — luật vi phạm: L8
- **Dấu hiệu quyết định:** A 94 · B 280 · **C 28** · D 26. Phase C phải là ngắn nhất.
- **Nghi phạm:** thiếu trần tuyệt đối `len(C) ≤ min(len(B), len(D))` — chính điều 13.1b đã đề xuất mà v7.1 chưa làm.

## Đạt
- **Mở range (L1):** MOVE giảm **46.2 giá / 107 nến / hiệu suất 0.41** — move xu hướng mạnh nhất cả lô, climax chặn đúng đáy cửa sổ. Nhìn ảnh thấy rõ một đợt rơi thẳng từ 4157 xuống 4103.
- **Phase B dài nhất (L9):** 280/427 nến, đúng tinh thần "phase xây nguyên nhân".
- **Biên (L3):** biên chính 4102.7–4128.9 cố định suốt 427 nến; đúng 1 biên phụ trên 4137.1; tỷ lệ 1.31x lành mạnh.
- **SOS neo đúng cây:** 03:01, VSA 6.30x, thân 0.85, đóng cửa vượt **cả biên phụ** 4137.1 — đúng yêu cầu L3 về SOS mạnh. Đây là ca thuật toán làm đúng nhất.
- **LPS[D] (L7):** một điểm duy nhất, giữ được ngoài biên chính. Đúng CBR.
- **SOT phía dưới `n=3`** khớp với chuỗi đáy cao dần 01:36 → 02:00 nhìn thấy trên ảnh.
