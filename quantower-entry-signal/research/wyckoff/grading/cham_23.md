# Chấm bài #23 — Tích luỹ (ACC) · 2026-06-03 05:31 → 06-04 05:06 (1354 nến M1)

**Điểm: 1/10** — không nên vẽ range ở đây. Biên chính 9.9 giá cố mô tả một vùng giá mà thực tế giá đi lang thang trong 54 giá suốt 22 tiếng; đây là hai biên vô nghĩa dán lên một ngày giao dịch.

## Lỗi (nặng → nhẹ)

### 1. Biên chính 9.9 giá không bao được gì — giá sống ngoài nó gần như cả range — luật vi phạm: L3 + L1
- **Thuật toán gắn:** biên chính 4486.9–4496.8 = **9.9 giá (0.22%)**; biên phụ 4450.1–4504.2 = **54.1 giá**. Tỉ lệ phụ/chính = **5.5 lần**.
- **Đúng phải là:** biên chính phải là biên **quan trọng nhất**, mô tả vùng cân bằng. Ở đây nó chỉ bao 18% chiều cao thực tế giá đã đi. Nhìn ảnh: hai đường cam liền nằm ở nửa trên khung, còn phần lớn thân chart — cả vùng 4450–4487 nơi giá sống hàng trăm nến — nằm **dưới** biên chính dưới. Một biên bị vi phạm liên tục 22 tiếng thì không phải biên.
- **Dấu hiệu quyết định trên chart:** mSOW tại 4450.1 sâu hơn biên chính dưới **36.8 giá** = **3.7 lần chiều cao biên chính**. Một "cú phá thất bại" mà sâu gấp 3.7 lần cả cái range thì cái range đó sai, không phải cú phá sai.
- **Nghi phạm trong thuật toán:** thiếu **điều kiện huỷ range khi biên phụ vượt quá N lần biên chính**. Hiện chỉ có guard "biên chính > 3.5% giá" (mục 8) — guard đó đo cái không phình, nên không bao giờ bắn. Đề xuất: biên phụ > 2.5× biên chính → huỷ range, vì lúc đó cấu trúc Phase A đã bị phủ định hoàn toàn.

### 2. Climax bắt sai cây — cây thật là 05:30 với VSA 11.08×, thuật toán lấy cây sau nó VSA 2.09× — luật vi phạm: L1 (climax phải là cây chặn move) + mục 8 Effort vs Result
- **Thuật toán gắn:** SC tại 05:31, VSA **2.09×**, biên độ 3.2 giá.
- **Đúng phải là:** đọc bảng 12 nến — nến **05:30** có volume **715**, VSA **11.08×**, biên độ 8.2 giá (4496.8→4488.6), thân 0.78. Đó là cây climax. Cây 05:31 chỉ là cây theo sau với volume 147, biên độ 3.2. Cơ chế "cụm climax" (v5, vá lỗi A) được thiết kế để **dời mốc sang cực trị mới** — nó đã dời đúng về đáy 4486.9, nhưng kéo theo cả nhãn VSA sang cây yếu.
- **Dấu hiệu quyết định trên chart:** 11.08× vs 2.09× — chênh hơn 5 lần. Trên panel volume, thanh vàng cao vọt ở đầu range chính là cây 05:30 chứ không phải cây mang nhãn SC.
- **Nghi phạm trong thuật toán:** mục 4.0 "cụm climax" dời mốc theo **cực trị giá** mà không giữ lại **cây VSA cao nhất trong cụm** làm cây được báo cáo. Nên tách: *mức* climax = cực trị của cụm; *cây* climax (để đọc VSA/biên độ) = cây VSA cao nhất trong cụm.

### 3. Phase B 1278 nến — 94% cả range là "Phase B" — luật vi phạm: L9 (bị lạm dụng) + lỗi kinh điển "range quá vụn / khung quá thô"
- **Thuật toán gắn:** A=15, B=**1278**, C=32, D=25, E=5.
- **Đúng phải là:** Phase B đúng là dài nhất, nhưng 1278 nến = **21 tiếng** trên M1 với biên chính 9.9 giá không phải "xây dựng nguyên nhân" — đó là thuật toán treo một range chết suốt một ngày rồi chộp lấy cú phá đầu tiên nó thấy. Giảng viên trong CHART_CASES nhiều lần bắt lỗi này ở chiều ngược lại (khung quá thô); ở đây là **khung quá mịn**: cấu trúc này phải nhìn ở M15/M30 mới ra hình, và khi đó nó gần như chắc chắn là 2–3 range riêng biệt chứ không phải một.
- **Dấu hiệu quyết định trên chart:** trong 1278 nến đó có **cả một cú sụp về 4450 rồi hồi lại toàn bộ** — đó là một chu kỳ giá hoàn chỉnh, đủ tư cách làm range riêng, bị nuốt thành "một nến ngọ nguậy trong Phase B".
- **Nghi phạm trong thuật toán:** mục 13.3 đã tự thừa nhận — "vẫn chỉ theo dõi ĐÚNG MỘT range một lúc". Range này chiếm chỗ suốt 22 tiếng, mọi climax mới trong đó (kể cả cây gây ra mSOW 3.56×) đều bị bỏ. Đây là hệ quả trực tiếp của giới hạn 1-range.

### 4. SOS gắn lên nến VSA 0.46× — luật vi phạm: mục 8 (Effort vs Result) + WY05
- **Thuật toán gắn:** SOS tại 04:37, giá 4508.3, VSA **0.46×**, thân 1.00 (nến marubozu nhưng volume dưới nửa trung bình).
- **Đúng phải là:** SOS là "spread mở rộng + volume tăng". Cây phá thật của đợt này là cụm 04:30–04:35 (trên panel volume có thanh vàng rõ ngay trước mốc SOS). Lỗi B của v4 (nhãn neo nến xác nhận yếu) — **ở bài này CHƯA vá được**: 0.46× nằm đúng dải 0.30–0.69× mà v4 bị bắt.
- **Dấu hiệu quyết định trên chart:** so sánh nội bộ — cùng range, mSOS ở 4504.2 có VSA 2.78×, mSOW có 3.56×; cây được gọi là SOS *thật* lại chỉ 0.46×. Nhãn quan trọng nhất rơi vào cây yếu nhất trong ba.
- **Nghi phạm trong thuật toán:** cơ chế hồi tố nhãn SOS (mục 5.1) yêu cầu cây đó phải "đóng cửa vượt **biên phụ**". Biên phụ trên ở đây là 4504.2 — rất cao — nên cửa sổ hồi tố chỉ còn vài nến cuối, và trong đó cây to nhất tình cờ chỉ 0.46×. **Điều kiện "vượt biên phụ" đang làm hỏng cơ chế hồi tố khi biên phụ bị thổi phồng.**

### 5. Phase E 5 nến — luật vi phạm: L10 (nhẹ, nhưng là bằng chứng cú phá không đi tới đâu)
- **Thuật toán gắn:** E = 5 nến, range đóng lúc 05:06.
- **Đúng phải là:** nhìn ảnh, ngay sau SOS giá quay đầu rơi lại — nến cuối chart đã đỏ và về sát 4495. Đây là **cấu trúc thất bại** (THEORY §9), không phải "Tích luỹ hoàn tất". Đặt tên "Tích luỹ" cho cấu trúc này là gán nhãn thắng cho một cú phá chưa đi được đâu.

## Đạt
- MOVE trước climax có thật: 22.2 giá / 76 nến / hiệu suất 0.37 (sát ngưỡng nhưng qua).
- Phase A đủ 3 lần đổi hướng và kết thúc đúng tại ST[A]; ST[A] 4489.3 **nằm trong** biên chính, đúng là test lại vùng climax — không còn lỗi "ST[A] rơi ngoài range" của v4.
- mSOW / mSOS gán đúng vai: hai cú phá thất bại, giữ ở Phase B, nới biên phụ. L6 đạt (không có ST[B]).
- LPS[C] 4489.1 lần này **nằm đúng trên biên chính dưới** (4486.9) — chọn hợp lý hơn hẳn bài #21 và #22.
- LPS[D] một điểm duy nhất (L7 đạt).

## Cần hỏi người học
- Có chấp nhận **huỷ range khi biên phụ vượt K lần biên chính** không, và K bằng bao nhiêu? Đây là guard duy nhất bắt được cả bài #23 lẫn #24 mà không đụng tới các bài đúng. L3 nói biên phụ "nới ra tự do", nên luật hiện tại không cấm được ca này.
