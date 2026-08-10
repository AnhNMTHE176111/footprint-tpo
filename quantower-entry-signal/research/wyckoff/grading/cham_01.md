# Chấm bài #01 — Chưa rõ (SC) (ACC?) · 2025-12-29 15:22 → 2025-12-31 21:55 (118 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Đây là phiên lễ cuối năm gần như không có giao dịch, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Vẽ range trên vùng không có thanh khoản — luật vi phạm: L1 + mục "khung quá thô / range quá vụn"
- **Thuật toán gắn:** một TR đủ Phase A→C, biên chính 4411.4–4511.7.
- **Đúng phải là:** không mở range. 118 nến trải **2,5 ngày lịch** (29/12 → 31/12) = trung bình một nến mỗi 30 phút; bảng 12 nến quanh climax cho volume **1–7 hợp đồng/nến**, cây climax 7 lot, AR 1.00x (1–2 lot), Spring 0.50x. Không có hai phe nào đang đàm phán ở đây — chỉ là khe giá trong kỳ nghỉ.
- **Dấu hiệu quyết định trên chart:** cả nửa trái panel volume gần như phẳng sát 0; cột volume thật chỉ xuất hiện lại từ 01-02 16:41, tức là **sau khi range đã đóng**.
- **Nghi phạm trong thuật toán:** VSA là tỷ lệ tương đối nên 7 lot / TB 2 lot = 3.33x vẫn qua cửa. Người học đã chốt "không dùng sàn khối lượng tuyệt đối" — nhưng ca này cho thấy cần ít nhất một guard **mật độ nến theo thời gian** (số nến/giờ), không phải sàn lot: 118 nến/54 giờ tự nó đã đủ để loại.

### 2. Nhãn SC nằm giữa move, cách biên chính nó tạo ra 134 giá — luật vi phạm: L3 (biên chính = mức climax)
- **Thuật toán gắn:** SC tại 2025-12-29 13:42, giá **4545.6**, VSA 3.64x — **trước** nến mở range 1h40.
- **Đúng phải là:** SC phải nằm tại 4411.4 (mức đang được vẽ làm biên chính dưới), hoặc nếu 4545.6 mới là cây cao trào thật thì cây đó **không chặn được move** (giá đi tiếp xuống 134 giá nữa) → huỷ ứng viên.
- **Dấu hiệu quyết định trên chart:** chấm SC nằm lơ lửng giữa đoạn dốc trắng "chân MOVE", còn xa phía trên khung range; đường "biên CHINH duoi 4411.4" không có nhãn climax nào bám vào.
- **Nghi phạm trong thuật toán:** lỗi cụm climax đã biết (mục 13.1c — thử sửa rồi revert). Ở ca này nó lộ nặng nhất vì hai cửa sổ (giá trượt tự do / nhãn kẹp) trôi ngược chiều nhau **134 giá**.

### 3. Phase A dài nhất, Phase C dài hơn Phase B — luật vi phạm: L9 và L8
- **Thuật toán gắn:** A = **73** nến · B = **21** nến · C = **25** nến.
- **Đúng phải là:** B phải là phase dài nhất, C phải ngắn nhất. Ở đây A gấp 3,5 lần B và C vẫn phình hơn B.
- **Dấu hiệu quyết định trên chart:** vạch tím Phase B và Phase C nằm sát nhau ở mép phải khung, còn Phase A chiếm gần trọn khung.
- **Nghi phạm trong thuật toán:** ST[A] chốt tại 4450.2 = hồi **61%** khoảng AR↔climax (đã qua ngưỡng 0.55 mới) nhưng vẫn còn cách mức climax 39 giá; nó rơi vào nhịp lùi ngày 30/12 chứ không phải cú test lại vùng climax. Vẫn chưa có **trần tuyệt đối** `len(C) ≤ min(len(B), len(D))`.

### 4. Range đóng "completed" với một Spring còn treo `pending` — luật vi phạm: L8 / mục 6 tài liệu thuật toán
- **Thuật toán gắn:** Spring 2025-12-31 06:01 tại 4383.6, trạng thái `pending`, và Phase C kéo tới hết range.
- **Đúng phải là:** shock hết hạn phải hạ cấp thành mSOW/ST[B] và **xoá đoạn C** (đúng cách vá lỗi C ở v5). Ở đây đoạn C 25 nến vẫn nằm lại, range vẫn ghi `completed` dù không có SOS/SOW nào.
- **Dấu hiệu quyết định trên chart:** cột Spring VSA **0.50x** (1 hợp đồng) — một cú "rũ" bằng một lệnh lẻ.

### 5. Biên chính cao 100.3 giá (2.27%) cho một "vùng cân bằng" — luật vi phạm: THEORY §2.3 (vùng cân bằng hẹp)
- Guard 3.5% không bắn, nhưng 100 giá là cả một chân xu hướng, không phải TR. Guard nên đo theo **ATR của chính đoạn đó**, không theo % giá tuyệt đối.

## Đạt
- Tên range để "Chưa rõ (SC)" thay vì ép đặt tên khi chưa có cú phá — đúng L4.
- Biên phụ dưới 4383.6 đúng là cực trị xa nhất, chỉ một cái mỗi bên — đúng L3.
- ST[B] tại 4404.5 nằm đúng dưới biên chính dưới, không bị gọi nhầm thành Spring — đúng L5/L6.
