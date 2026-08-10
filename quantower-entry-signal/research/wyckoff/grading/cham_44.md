# Chấm bài #44 — Tích lũy (ACC) · 2026-07-06 00:01 → 01:57 (116 nến M1)

**Điểm: 5/10** — Phase A đẹp nhất trong cả lô; hỏng ở nhóm nhãn phá vỡ (mSOS nến rác, SOS thấp hơn chính mSOS).

## Lỗi (nặng → nhẹ)

### 1. SOS đóng cửa THẤP HƠN đỉnh mSOS trước đó — luật vi phạm: L3 ("SOS mạnh phải bứt qua biên PHỤ")
- **Thuật toán gắn:** mSOS 01:16 tại **4204.8** (= biên phụ trên), rồi SOS 01:32 tại **4203.7** — thấp hơn 1.1 giá.
- **Đúng phải là:** cú phá thật là nhịp 01:33–01:45 đi tới ~4214.5; nhãn SOS phải neo vào cây bùng của nhịp đó, và chỉ được công nhận khi đóng cửa **vượt 4204.8**.
- **Dấu hiệu quyết định:** biên phụ trên ghi rõ 4204.8, do chính mSOS nới ra. Nhãn "phá thật" lại nằm dưới nhãn "phá hụt" — mâu thuẫn nội tại đọc thẳng trên bảng sự kiện.
- **Nghi phạm:** v7.1 đã đổi mốc quyết định decisive/outside sang **biên CHÍNH** (`edge`) để chữa vòng lặp tự thua. Nhưng L3 vẫn đòi biên PHỤ cho việc **xếp hạng mạnh/yếu**. Hai việc này bị gộp làm một → mất luôn ràng buộc L3.

### 2. Nhãn mSOS neo vào nến rác — luật vi phạm: định nghĩa mSOS (mục 5.1 spec: "một cú phá CÓ THẬT")
- **Thuật toán gắn:** mSOS 01:16, **VSA 0.72x**, **thân 0.04** (thân bằng 4% biên độ).
- **Đúng phải là:** một cú phá có thật phải neo vào cây có nỗ lực; nến thân 4% volume dưới trung bình là một cây râu, không phải cú phá.
- **Dấu hiệu quyết định:** nhịp đẩy lên đó, theo phiếu, có `effort` trung bình 2.72x (01:00) — cây mạnh nằm sớm hơn hẳn nến được gắn nhãn.
- **Nghi phạm:** `_demote_shock()` quét lại cây VSA cao nhất, nhưng nhánh hạ cấp này rõ ràng không đi qua bước đó (đúng như 13.1b ghi "ăn không đều").

### 3. Nhãn SOS không thoả chính ngưỡng thân của spec — luật vi phạm: tham số "thân ≥ 45% để công nhận SOS/SOW"
- **Thuật toán gắn:** SOS 01:32, VSA 2.33x, **thân 0.26**.
- **Dấu hiệu quyết định:** 0.26 < 0.45. Bước chốt cú phá có kiểm thân, nhưng bước **đặt nhãn hồi tố** chỉ chọn "VSA cao nhất trong đoạn" mà bỏ kiểm thân.
- **Nghi phạm:** hàm đặt nhãn hồi tố trong `_fire_break` thiếu điều kiện `body_ratio ≥ 0.45` khi chọn cây.

### 4. LPS[D] cao hơn cả điểm phá — luật vi phạm: L10 (retest phải là nhịp HỒI)
- **Thuật toán gắn:** LPS[D] 01:37 tại **4206.6**, cao hơn SOS 4203.7.
- **Đúng phải là:** nhịp retest thật là nhịp lùi về vùng 4204–4205 ở 01:50–01:55 (nhìn trên ảnh, giá lùi về sát nét đứt biên phụ rồi mới rơi).
- **Nghi phạm:** LPS[D] lấy "swing pivot ngược hướng đầu tiên xác nhận" — pivot đầu tiên rơi vào một nhịp thở trong lúc giá còn đang chạy lên, không phải nhịp retest biên.

### 5. Phase E dài đúng 1 nến — luật vi phạm: L10 / lỗi J của vòng v5 tái xuất
- **Dấu hiệu quyết định:** A 26 · B 56 · C 9 · D 25 · **E 1**. Trên ảnh giá đạt đỉnh 01:45 rồi rơi thẳng về 4184 — thực chất cấu trúc **không** đi tìm được vùng giá mới.
- **Đúng phải là:** hoặc kéo Phase E cho đủ, hoặc thừa nhận cú phá không giữ được và đóng range ở trạng thái "chưa rõ hướng" thay vì đặt tên "Tích luỹ".

## Đạt
- **Phase A (L2):** đẹp nhất lô. SC 00:01 VSA 3.72x biên độ 11.1 giá (cây chặn move thật) → AR 00:17 → ST[A] 00:26 tại 4183.0, tức **hồi 95% khoảng AR↔climax**, test đúng vùng climax. Đây là cách ST[A] phải nằm.
- **Mở range (L1):** MOVE giảm 24.3 giá / 33 nến / hiệu suất 0.45, climax là đáy của cả cửa sổ.
- **Biên (L3):** biên chính 4182.4–4193.9 cố định; đúng 1 biên phụ trên 4204.8; tỷ lệ 1.95x hợp lý.
- **Phase B dài nhất (L9)** 56 nến; **Phase C ngắn** 9 nến (L8).
- Chú thích nỗ lực/kết quả đọc đúng dấu (`er=0.46 — nhịp HIỆU QUẢ`), không còn hard-code "hấp thụ nghi vấn".
