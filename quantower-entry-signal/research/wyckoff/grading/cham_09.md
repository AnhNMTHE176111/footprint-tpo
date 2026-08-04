# Chấm bài #09 — Tích luỹ (ACC) · 2026-04-19 23:43 → 2026-04-20 01:12 (59 nến M1)

**Điểm: 2/10** — **không nên vẽ range ở đây.** Đây là một cú capitulation rồi đảo chiều V, không phải một vùng đấu giá. Cả năm phase bị nhồi vào 59 nến / 1,5 giờ, Phase B chỉ 13 nến và Phase A không phải CHoCH.

## Lỗi (nặng → nhẹ)

### 1. Không có vùng đi ngang nào — cấu trúc bị gò cho khớp mô hình — luật vi phạm: L1 (range phải là vùng đấu giá thật), CHART_CASES Ca #20 nguồn 7.pdf ("tái tích luỹ gượng ép")
- **Thuật toán gắn:** Tích luỹ đủ A→E trong 59 nến, biên chính 4793.0-4809.8.
- **Đúng phải là:** ghi nhận **SC + AR** rồi **dừng, chờ cấu trúc**. Đây là hình chữ V: giá giảm 34 giá trong 43 nến, một cây SC biên độ **22 giá / VSA 11.74x / volume 71 so với 1-5 của các nến trước**, rồi bật lên một mạch tới 4868 — tổng cộng **không có 5 nến nào đi ngang liên tiếp**.
- **Dấu hiệu quyết định trên chart:** trên ảnh, từ chấm SC (4793) tới nhãn SOS (4815.9) là một dãy nến xanh leo thang liên tục; sau SOS giá tiếp tục lên 4868 không lùi. Cả khung range vẽ ra chỉ bao đúng đoạn dốc lên. Phase B (13 nến) chiếm 22% range — trong khi L9 nói B là phase **dài nhất**.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Nhưng cần một guard **hình dạng**, không phải guard độ dài: ví dụ Phase B bắt buộc dài hơn Phase A, hoặc yêu cầu ≥N nến có close nằm trong 60% giữa biên chính. Hiện không có guard nào chặn ca V-reversal này.

### 2. Phase A không phải CHoCH — ST[A] là một cái ngọ nguậy giữa range — luật vi phạm: L2
- **Thuật toán gắn:** SC 4793.0 (nến 0) → AR (yếu) 4809.8 (nến 15) → ST[A] 4802.1 (nến 17). Phase A = 17 nến.
- **Đúng phải là:** ST[A] phải là cú **quay lại test vùng climax**. 4802.1 nằm ở **55% chiều cao range tính từ đáy**, còn cách mức SC **9.1 giá**; nó chỉ là một nến hồi 7.7 giá kẹp giữa hai nhịp tăng, VSA **0.15x**, thân **0.00** (nến doji volume 1). Đây không phải một lần "bị chặn", đây là một khoảng trống thanh khoản.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] trên ảnh nằm lơ lửng giữa hai đường cam, cách hẳn đường "biên CHÍNH dưới 4793.0" — mắt nhìn thấy ngay nó không test gì cả. Và nó xuất hiện **chỉ 2 nến sau AR**: 3 lần đổi hướng của L2 bị dồn vào 17 nến, tức không có lần đổi hướng nào là một *nhịp* thật.
- **Nghi phạm trong thuật toán:** ST[A] = "swing pivot đầu tiên về phía climax, 5 nến không cực trị mới + nhịp hồi ≥1.5× biên độ TB". Với biên độ TB ở phiên Á ≈ 1-2 giá, sàn 1.5× ≈ 2-3 giá → một nến doji cũng qua được. Sàn chống nhiễu phải neo theo **chiều cao range** (ví dụ ≥25% chiều cao) chứ không neo theo biên độ TB của phiên chết.

### 3. AR (yếu) được dùng để chốt biên chính dù chính máy đã tự cảnh báo — luật vi phạm: L3
- **Thuật toán gắn:** AR **(yếu)** tại 4809.8, VSA 0.44x, thân 1.00 → dùng luôn làm biên chính trên.
- **Đúng phải là:** máy đã tự dán nhãn "(yếu)" nhưng vẫn để nó chốt một trong hai biên quan trọng nhất, rồi 18 nến sau chính giá phá qua biên đó và không quay lại nữa. Nếu AR yếu thì phải hoặc chờ AR thật, hoặc bỏ ứng viên.
- **Dấu hiệu quyết định trên chart:** biên trên 4809.8 bị phá tại mSOS (4813.0) rồi SOS (4815.9) chỉ 4 nến sau đó, và giá đi tiếp 53 giá lên 4868. Một "biên" chỉ sống được 18 nến không phải biên của vùng đấu giá.
- **Nghi phạm trong thuật toán:** nhãn "AR (yếu)" hiện là **chỉ cảnh báo hiển thị, không đổi logic** (mục 4.1). Ở ca V-reversal, chính nó phải là điều kiện bỏ ứng viên.

### 4. Thiếu hẳn Phase C — luật vi phạm: L8 + mục 6 case khó (bắt buộc gán ngược khi SOS bắn ra mà chưa có C)
- **Thuật toán gắn:** dải phase là A → B → **D** → E, nhảy thẳng từ B sang D.
- **Đúng phải là:** spec nói rõ khi SOS bắn mà range chưa từng có Phase C thì phải nhìn ngược lấy nhịp test cuối làm LPS[C]. Ở đây không có nhãn LPS[C] nào.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = min(60 nến, **1/2 độ dài Phase B**). Phase B = 13 nến → cửa sổ 6 nến, không đủ để có swing pivot xác nhận 5 nến. Công thức min(...) tự khoá chính nó ở mọi range ngắn. Lỗi lặp: xem thêm bài #11 và #12.

### 5. mSOS và SOS là cùng một cú phá, cách nhau 4 nến — nhãn dư — luật vi phạm: mục 5.1 (mSOS = cú phá thất bại, đã thu hẳn vào trong range)
- **Thuật toán gắn:** mSOS 00:16 tại 4813.0 (Phase B) rồi SOS 00:20 tại 4815.9 (Phase D).
- **Đúng phải là:** một nhãn duy nhất. mSOS chỉ đúng khi cú phá **thất bại và giá thu hẳn vào trong range**; ở đây 4 nến sau giá đã phá tiếp và không bao giờ trở lại. 4813.0 chỉ là nến đầu tiên của chính cú phá được gọi SOS.
- **Dấu hiệu quyết định trên chart:** hai chấm mSOS (cam) và SOS (xanh) nằm sát nhau, gần như cùng một cột thời gian, cùng nằm quanh đường biên phụ 4813.0.
- **Nghi phạm trong thuật toán:** điều kiện thu hồi "đóng cửa lùi hẳn vào trong range quá 30 tick" — ở đây có thể một nến lùi 3 giá đủ để bắn mSOS trước khi nhịp phá thật hoàn tất. Nên chặn: không ghi mSOS nếu ≤N nến sau đó lại có cú phá cùng phía sâu hơn.

### 6. Diễn giải chỉ số nỗ lực/kết quả ĐẢO DẤU — lỗi chỉ số
- **Thuật toán gắn:** effort 1.36x, result 13.99, er=0.10 → in "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er=0.10 nghĩa nỗ lực **nhỏ** mà kết quả **rất lớn** — đó là dấu "không còn nguồn cung nổi" (THEORY §6.3: breakout không cần volume cao vẫn hợp lệ), ngược hẳn với "volume nhiều kết quả ít". Ngoài ra result = **13.99 ATR** là con số không dùng được: ATR ở phiên Á gần 0 nên tỷ số phình vô nghĩa.
- **Nghi phạm trong thuật toán:** chuỗi diễn giải in cứng, không phân ngưỡng er; và mẫu số ATR không có sàn tối thiểu.

## Đạt
- **Mục 1 phần climax:** MOVE có thật (34.1 giá / 43 nến, hiệu suất 0.37) và cây SC là cực trị chặn move — biên độ 22 giá, VSA 11.74x. Riêng phép nhận climax làm đúng.
- **Mục 3 phần biên phụ:** biên phụ mỗi bên tối đa 1, tỷ lệ 1.19x, vẽ trung thực.
- **Mục 4 (L4):** SC + phá lên = Tích luỹ. Tên gọi khớp origin + hướng phá.
- **Mục 8 phần SOS:** SOS đặt tại cây VSA **3.88x** — cây phá có volume tăng thật, không rơi vào nến rác. Vá lỗi B của v5 chạy đúng ở bài này.
- **Chỉ số bias = +1** (chạm nổi biên trên, không nổi biên dưới): **đo đúng** — khớp chart, và đúng hướng phá.
- SOT = none cả hai phía: đúng, range không đủ 3 nhịp để SOT có nghĩa (THEORY §7 yêu cầu ≥3 lần đẩy).

## Cần hỏi người học
- Người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Nhưng ca V-reversal như bài này cần một guard **hình dạng** thay cho guard độ dài. Chấp nhận luật nào: (a) Phase B phải dài hơn Phase A, hay (b) yêu cầu ≥N nến có close nằm trong phần giữa biên chính?
