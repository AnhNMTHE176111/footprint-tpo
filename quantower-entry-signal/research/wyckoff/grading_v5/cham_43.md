# Chấm bài #43 — Chưa rõ (SC) · 2026-07-16 13:05 → 2026-07-17 20:59 (1853 nến M1)

**Điểm: 5/10** — Range này là một vùng đấu giá THẬT, biên vẽ rất đẹp; nhưng thuật toán chết đứng ở Phase B suốt 1819 nến và bỏ lỡ cú phá lên rõ ràng cuối ngày 17/07.

## Lỗi (nặng → nhẹ)

### 1. Bỏ lỡ hẳn Phase C→D→E — luật vi phạm: L10 + mục 5.1 kết cục B
- **Thuật toán gắn:** mSOS tại 17/07 16:24, giá 4028.9, VSA 2.41×, **thân 0.90** — rồi thôi. Range đóng ở trạng thái "Chưa rõ".
- **Đúng phải là:** nhìn ảnh, từ 13:25 ngày 17/07 giá bật từ đáy 3963 lên thẳng 4028.9 — **65.9 giá trong khoảng 3 giờ**, xuyên qua biên chính trên 4012.6, và sau đó **giá không quay lại dưới biên chính nữa** cho tới hết range (đoạn cuối chart dao động 4012-4025, tức là quanh và trên biên chính trên). Đó là SOS thật. Range này là **Tái phân phối… không, là Tích luỹ (ACC)**: origin SC + phá lên thật.
- **Dấu hiệu quyết định trên chart:** cây mSOS có **thân 0.90 và VSA 2.41×** — thân dày, volume cao, đóng cửa trên biên phụ. Chính bảng tham số của thuật toán nói "thân ≥ 45%" là đủ công nhận SOS. Ngoài ra sau mSOS giá đi ngang **quanh mức 4012-4025** chứ không lùi vào giữa range — đó chính là CBR (L10): phá → retest → giữ được ngoài biên.
- **Nghi phạm trong thuật toán:** điều kiện SOS đòi **3 nến liên tiếp đóng cửa vượt BIÊN PHỤ thêm ≥ 30 tick**. Biên phụ trên ở đây là 4028.9 — mà 4028.9 **chính là do cú phá này tạo ra**. Đây là bẫy logic vòng tròn: cú phá tự nới biên phụ lên đúng đỉnh của nó, rồi bị chấm là "chưa vượt biên phụ". Phải so với biên phụ **tại thời điểm trước cú phá**, không phải biên phụ đã bị chính nó nới.

### 2. Climax VSA 0.92× — dưới ngưỡng, và không phải cây climax thật — luật vi phạm: L1 + mục 3 (1)
- **Thuật toán gắn:** SC tại 13:05, giá 3977.1, **VSA 0.92×**.
- **Đúng phải là:** climax thật là cây **−3 (13:02): VSA 2.91×, 1463 lot, thân 0.77, rơi 13.4 giá**, hoặc cây −1 (13:04): VSA 2.34×, 1202 lot. Cây +0 chỉ có 457 lot và **đóng cửa xanh** (3982.1 → 3987.0) — đó là cây bật lại, không phải cây cao trào bán.
- **Dấu hiệu quyết định trên chart:** volume của climax được gán (457) chỉ bằng **1/3** volume cây 13:02 (1463). Trên panel volume, thanh vàng cao nhất của cả cụm nằm ở nến trước.
- **Nghi phạm trong thuật toán:** lại là cụm climax mục 4.0 dời mốc **về đáy thấp nhất** trong 8 nến mà không kiểm lại VSA của nến đích. Mức giá 3977.1 đúng là đáy thật, nhưng nhãn nên nằm ở cây nỗ lực. Đề xuất: dời mốc theo cực trị nhưng **báo VSA của cả cụm**, và bắt buộc cụm phải chứa ít nhất một nến ≥ 2.2×.

### 3. Phase A quá ngắn so với thân range, ST[A] chỉ 9 nến sau AR — luật vi phạm: L2 (mức nhẹ)
Phase A = 35 nến trên tổng 1853 (1.9%). AR ở 13:30, ST[A] ở 13:39 — 9 nến. Về mặt cấu trúc thì vẫn đủ 3 lần đổi hướng và ST[A] (3985.5) nằm trong range, sát vùng SC → **chấp nhận được**. Nhưng nhìn ảnh, có một nhịp bật lớn hơn nhiều ở 14:24 lên 4022 — mắt người sẽ đặt AR ở đó chứ không ở 4012.6. Ghi nhận là điểm gờn gợn, không tính lỗi nặng.

### 4. Hai mSOW cùng phía cùng tồn tại — luật vi phạm: L3 ("mỗi bên nhiều nhất 1 biên phụ")
- **Thuật toán gắn:** mSOW 16/07 19:38 (3973.4) **và** mSOW 17/07 13:01 (3963.0).
- **Đúng phải là:** biên phụ dưới chỉ giữ cực trị xa nhất = 3963.0. Nhãn mSOW cũ ở 3973.4 lẽ ra **biến mất** khi cú sâu hơn xuất hiện — đúng như quy tắc "cú thăm dò mới nông hơn thì không ghi gì, cú sâu hơn hạ cấp cú trước". Thuật toán áp quy tắc này cho Spring/UTAD nhưng **không áp cho mSOS/mSOW**.
- **Dấu hiệu quyết định trên chart:** hai nhãn mSOW cùng nằm dưới biên chính dưới, biên phụ nét đứt chỉ vẽ một đường ở 3963.0 — tức là chính bản vẽ đã tự mâu thuẫn với nhãn.
- **Nghi phạm trong thuật toán:** nhánh gắn mSOS/mSOW thiếu bước "xoá nhãn cũ cùng phía nông hơn" mà nhánh Spring/UTAD có.

## Đạt
- **Mở range (L1):** MOVE giảm 67.7 giá / 61 nến, hiệu suất 0.45, climax là đáy của cửa sổ. Đạt.
- **Biên (L3):** biên chính 3977.1-4012.6 cố định suốt 1853 nến, **và nhìn ảnh thì hai đường cam liền này bám giá cực đẹp** — hầu hết dao động 30 giờ nằm gọn giữa hai mức đó, các lần thò ra đều bị đẩy về. Đây là biên chính đúng nghĩa "vùng cân bằng". Bài này chứng minh cơ chế biên cố định của v5 hoạt động.
- **Phase B là phase dài nhất (L9):** 1819/1853. Đọc effort↔result: phe bán hai lần cố phá xuống (3973.4 rồi 3963.0) đều bị kéo ngược lên trong vòng vài chục nến, còn phe mua thì cuối cùng đi được tới 4028.9 và **ở lại đó**. Cung cạn dần, cầu thắng — đúng khuôn tích luỹ.
- **Không đặt tên bừa:** range để "Chưa rõ (SC)" thay vì gán đại một tên. Đúng tinh thần L4 và đúng vá lỗi F.
- Cắt range đúng, không bắc qua khe cuối tuần.

## Cần hỏi người học
- Bài này là ca thử tốt nhất cho **bẫy biên phụ tự nới**: cú phá vừa tạo biên phụ vừa bị đo bằng chính biên phụ đó. Có nên chốt luật "biên phụ dùng để xét SOS/SOW là biên phụ **đóng băng tại thời điểm nến đầu tiên thò ra**"?
