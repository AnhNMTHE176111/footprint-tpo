# Chấm bài #09 — Tích lũy (ACC) · 2026-04-19 23:43 → 2026-04-20 01:12 (59 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** 59 nến mà nhét đủ A→E, Phase B chỉ 13 nến, không có Phase C: đây là một cú đảo chiều chữ V, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — 59 nến M1 với "đủ" 4 phase — luật vi phạm: THEORY §2.3 (TR = giai đoạn đi ngang, đàm phán), lỗi kinh điển "range quá vụn"
- **Thuật toán gắn:** A=17 · B=13 · D=18 · E=12, tổng 59 nến, gọi là Tích luỹ hoàn chỉnh.
- **Đúng phải là:** không có "giai đoạn đàm phán" nào ở đây. Đọc lại chuỗi: SC nổ 22 giá xuống 4793 lúc 23:43, giá bật lên liên tục và tới 00:20 đã phá lên trên rồi chạy thẳng tới 4868. Toàn bộ "range" chỉ là **nhịp nghỉ 30 phút giữa một cú V-reversal**. Giá dành rất ít thời gian ở đây — theo THEORY §2.3 đó là dấu hiệu vùng **không cân bằng**, tức không phải TR.
- **Dấu hiệu quyết định:** chiều cao biên chính 16.8 giá / 59 nến, trong khi ngay sau Phase E giá đi tiếp 55 giá lên 4868 mà không hề dừng.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range" (quyết định 1, mục 0b) — nhưng ca này cho thấy cần một điều kiện **cấu trúc** thay thế: ví dụ Phase B phải có ≥2 lượt chạm biên (ở đây bias=+1, chỉ chạm được biên trên).

### 2. THIẾU HẲN Phase C — luật vi phạm: L8
- **Thuật toán gắn:** timeline nhảy thẳng A → B → **D** → E.
- **Đúng phải là:** L8 nói rõ, khi không có Spring/UTAD thì phải **chờ SOS rồi quay lại gán ngược Phase C**. Không có Phase C = không có "tín hiệu đầu tiên cho thấy giá sắp phá biên kia", cấu trúc đọc không ra chuyện gì.
- **Dấu hiệu quyết định:** Phase B chỉ 13 nến ⇒ cửa sổ gán ngược = min(60, 0.8×13) = **10 nến**. Nới từ 0.5x lên 0.8x **không cứu được ca này**, vì vấn đề là mẫu số (Phase B) quá ngắn chứ không phải hệ số.
- **Nghi phạm trong thuật toán:** công thức `min(60, k×len(B))`. Đề xuất: bỏ hẳn phụ thuộc vào len(B), dùng sàn cứng (ví dụ tối thiểu 15–20 nến hoặc tới mốc bắt đầu Phase B, lấy cái nào gần hơn).

### 3. Phase B (13 nến) ngắn hơn cả Phase A (17) và Phase D (18) — luật vi phạm: L9
- **Thuật toán gắn:** B là phase **ngắn nhì** toàn range.
- **Đúng phải là:** B dài nhất. Ở đây "xây dựng nguyên nhân" chỉ diễn ra trong 13 nến — theo luật Nhân-Quả (THEORY §2.2), nguyên nhân bằng 0 thì không có cơ sở gọi đây là tích luỹ.

### 4. ST[A] là một nến doji volume 1 lot nằm giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 00:01, giá 4802.1, **VSA 0.15x**, thân 0.00.
- **Đúng phải là:** ST[A] phải là cú quay lại **vùng climax** rồi bị chặn. 4802.1 cách SC 4793.0 tới 9.1 giá = **54% chiều cao range** — giữa range, không phải test biên. Và một nến doji 1 hợp đồng thì không "bị chặn" bởi ai cả.
- **Dấu hiệu quyết định:** phiếu số liệu: `ST[A] … 4802.1 … VSA 0.15x … thân 0.00`; biên chính 4793.0–4809.8.
- **Nghi phạm trong thuật toán:** giống bài #08 — ngưỡng mới 0.4× khoảng AR↔climax đo **độ hồi từ AR**, ở đây đạt 0.46 nên lọt, nhưng không đo **khoảng cách còn lại tới climax**. Cần thêm ràng buộc này; đồng thời nên loại ứng viên ST[A] có VSA quá thấp (0.15x là nhiễu thuần).

### 5. mSOS rồi SOS cách nhau 4 nến, cùng một cú phá — luật vi phạm: mục 5.1 spec (nhãn dư)
- **Thuật toán gắn:** mSOS 00:16 (4813.0, VSA 1.67x, Phase B) → SOS 00:20 (4815.9, VSA 3.88x, Phase D).
- **Đúng phải là:** một nhãn duy nhất. mSOS theo định nghĩa v6 là cú phá **thu hẳn vào trong range rồi hướng sang biên đối diện** — ở đây giá không hề thu vào, nó đi thẳng lên và 4 nến sau thành SOS. Nhãn mSOS phải bị xoá hồi tố khi SOS cùng hướng xác nhận ngay sau đó.
- **Nghi phạm trong thuật toán:** bản vá #5 (quét lại lấy nến VSA cao nhất trong đoạn thăm dò) chọn 1.67x trong khi cây thật 3.88x nằm chỉ 4 nến sau, ngoài cửa sổ quét. Cửa sổ hạ cấp mSOS/mSOW đang đóng quá sớm.

### 6. AR gắn cờ "(yếu)" nhưng nó lại là AR hợp lệ nhất trong range
- AR 23:58 giá 4809.8 (VSA 0.44x) là đỉnh nhịp bật ngược thật, cách climax 16.8 giá. Cờ "(yếu)" ở đây gây hiểu nhầm; trong khi ST[A] (0.15x) đáng bị cảnh báo hơn thì lại không có cờ nào.

## Đạt
- **Mục 1 (L1):** SC 23:43 là climax mẫu mực — biên độ nến **22.0 giá**, **VSA 11.74x**, đúng đáy của move giảm 34.1 giá / 43 nến (hiệu suất 0.37). Cây climax chặn move, không nằm giữa move. Nhãn neo đúng cây, đúng đáy 4793.0.
- **Mục 3 (L3):** biên chính = climax + AR, cố định; một biên phụ trên 4813.0 do mSOS tạo, tỷ lệ 1.19x — sạch.
- **Mục 8 một phần:** SOS neo đúng cây VSA 3.88x (cao nhất đoạn phá) — bản vá "nhãn hồi tố về cây phá thật" chạy đúng ở đây.
- **Chú thích nỗ lực/kết quả đúng dấu:** er=0.10 ghi "nhịp HIỆU QUẢ" — không còn hard-code "hấp thụ NGHI VẤN".
