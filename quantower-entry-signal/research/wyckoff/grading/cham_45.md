# Chấm bài #45 — Tái tích luỹ (RE-ACC) · 2026-07-22 12:20 → 14:01 (101 nến M1)

**Điểm: 2/10** — **Không nên vẽ range ở đây.** Cây được gọi BCLX nổ ra khi giá **đang đi ngang** và bản thân nó là một nến **bứt lên** (thân 0.81) — nó không chặn move nào cả. Toàn bộ hình này là một nhịp điều chỉnh trong xu hướng tăng, giá đi qua "range" đúng một lượt xuống-rồi-lên và tiếp tục tăng lên 4170.

## Lỗi (nặng → nhẹ)

### 1. Mở range trong lúc giá đi ngang — vi phạm trực tiếp điều kiện CẦN — luật vi phạm: **L1** + điều kiện (3) mục 3 của chính spec ("nến xanh **chặn** một move tăng")
- **Thuật toán gắn:** BCLX 12:20 tại 4134.9, VSA 2.80x, biên độ 4.7 giá; MOVE trước = 17.7 giá / 37 nến, hiệu suất 0.50.
- **Đúng phải là:** không mở range. Move tăng thật kết thúc quanh 11:55–12:00; **12 nến liền trước climax (12:08–12:19) đi ngang trong dải 4128.2–4132.8 = 4.6 giá**. L1 nói thẳng: "Giá đang đi ngang mà xuất hiện nến volume cao thì **không** được mở range."
- **Dấu hiệu quyết định trên chart:** nến climax **open 4130.8 → close 4134.6, thân/biên độ 0.81** — đó là một nến **breakout tăng**, không phải nến bị chặn; 5 nến sau nó vẫn đi ngang 4132–4135.5 rồi giá còn lên tiếp **4139.5 @12:30**. Không hề có cú đảo chiều tại 4134.9.
- **Nghi phạm trong thuật toán:** phép đo MOVE (mục 3 nhóm 2) tính trên **240 nến nhìn lại** nên vẫn "nhìn thấy" đợt tăng từ đáy 4118.3 @11:43, trong khi 20 nến gần nhất đã đi ngang hẳn. Cần thêm điều kiện: **đoạn sát climax** (ví dụ 10-20 nến cuối) cũng phải còn hướng, và cây climax phải là **cực trị của cả cụm** — cả hai đều thiếu.

### 2. Climax neo sai nến, lệch 4.6 giá — luật vi phạm: L1 + L3
- **Thuật toán gắn:** biên chính trên = 4134.9; biên phụ trên = 4139.5.
- **Đúng phải là:** đỉnh thật là **4139.5 @12:30** (10 nến sau) — nếu vẫn vẽ range thì biên chính trên phải là 4139.5 và **không có biên phụ trên**.
- **Dấu hiệu quyết định trên chart:** cả cụm nến 12:24–12:36 nằm phía trên đường liền 4134.9; nét đứt 4139.5 chính là đỉnh của cụm climax chứ không phải "cực trị do một thế lực cố phá range" như định nghĩa biên phụ ở L3.

### 3. AR to hơn cả MOVE — bằng chứng cấu trúc bị đọc ngược — luật vi phạm: L2 (AR là **phản ứng** của move, không thể lớn hơn move)
- **Thuật toán gắn:** AR 4110.4 @12:56 → khoảng cách climax↔AR = **24.5 giá**, trong khi MOVE trước climax chỉ **17.7 giá**.
- **Đúng phải là:** khi nhịp "phản ứng" dài hơn 138% cái move mà nó phản ứng lại, thì cái được coi là move là sai. Đoạn 12:36→12:56 (rơi 29 giá kèm VSA 5.03x) mới là **move** thật của khung này, và nó vẫn chỉ là một nhịp điều chỉnh của xu hướng tăng lớn hơn.
- **Nghi phạm trong thuật toán:** điều kiện duy nhất về AR là "hồi ≥30% độ dài move" (mục 4.1) — có **chặn dưới** nhưng **không có chặn trên**. Nên thêm: AR > ~100% độ dài move ⇒ loại ứng viên.

### 4. ST[A] chỉ là một chỗ nghỉ 5 nến giữa range — luật vi phạm: L2 + THEORY §5
- **Thuật toán gắn:** ST[A] 4124.6 @13:01 (5 nến sau AR), VSA 1.11x → chốt Phase A.
- **Đúng phải là:** 4124.6 = **58% chiều cao range**, cách biên trên 10.3 giá → 1/3 giữa, không có vai theo THEORY §5. Và nó **không phải một cú đổi hướng**: 13:02–13:06 chỉ lình xình (volume rơi xuống 27–117), rồi **13:09–13:10 giá lập đỉnh mới ngay (4125.6 → 4126.9)** và đi thẳng lên. Điều kiện "5 nến không tạo cực trị mới" bị thoả bởi một khoảng lặng vi mô, không phải bởi một test.
- **Nghi phạm trong thuật toán:** ngưỡng ST[A] hồi ≥40% chiều cao + xác nhận 5 nến (mục 4.2). Lặp lại y nguyên ở bài #41 (50%) và #42 (61%) → đây là **lỗi hệ thống**, không phải ngẫu nhiên.

### 5. LPS[C] đặt **trên** biên chính, ngay giữa cú bứt biên — luật vi phạm: L8 (Phase C là tín hiệu TRƯỚC cú phá) + Ca #3 (4.pdf: LPS[C] vs LPS[D])
- **Thuật toán gắn:** LPS[C] 4135.8 @13:29 (VSA 0.84x).
- **Đúng phải là:** 4135.8 **cao hơn biên chính trên 4134.9** — lúc đó giá đã đóng cửa ngoài biên từ **13:19 (close 4135.1, VSA 2.4x)** và 13:23–13:24 (4138.2 / 4138.1). Không còn là test trong range, nên vai đúng là LPS[D] (hoặc không có nhãn nào).

### 6. SOS trễ 14 nến, gán trên nến volume 0.52x — luật vi phạm: L10 + mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOS 13:45 tại 4151.3, **VSA 0.52x** — cách biên chính trên **16.4 giá (67% chiều cao range)**.
- **Đúng phải là:** cây phá thật là **13:31: VSA 4.83x**, high 4149.4, close 4145.7 — thanh volume cao nhất cả chart (nhìn panel dưới, cụm vàng ở 13:29–13:31).
- **Nghi phạm trong thuật toán:** giống bài #41/#42/#44 — chuỗi xác nhận 3 nến + 30 tick, nhãn lấy nến cuối chuỗi thay vì hồi tố về nến phá đầu tiên.

### 7. Biên dưới chỉ được chạm 1 lần — luật vi phạm: THEORY §3.1 (TR = nơi cung cầu cân bằng tương đối) + CHART_CASES mục "Cách xác định biên range"
- **Thuật toán gắn:** biên chính dưới 4110.4 (= AR).
- **Đúng phải là:** 4110.4 được chạm **đúng một lần** (chính cây AR) và giá không bao giờ trở lại. Theo quan sát trong CHART_CASES, biên dưới thường cần **2-3 lần chạm** mới được giảng viên công nhận. Cộng với 101 nến / 5 phase (B 27 nến < A 42 nến → vi phạm L9; C 16 = D 16 → vi phạm L8), đây là "range quá vụn" đúng như lỗi kinh điển đã ghi.

## Đạt
- **L3 phần cố định biên:** biên chính không bị kéo theo giá về sau; mỗi bên tối đa 1 biên phụ — làm đúng cơ chế (dù mức neo sai).
- **L4:** nếu buộc phải đặt tên thì origin BCLX + phá lên = Tái tích luỹ — đúng logic 4 pattern.
- **L7:** LPS[C] chỉ 1 điểm, không spam.
- Không nhầm UT ↔ UTAD, không gán SC trong tái tích luỹ, không gọi Spring cho đáy không phá đáy cũ.

## Cần hỏi người học
- L1 hiện đo MOVE trên cửa sổ 240 nến. Có nên bổ sung điều kiện "**N nến sát trước climax phải chưa đi ngang**" (ví dụ biên độ 15 nến cuối ≥ 40% độ dài move) để chặn đúng ca này? Đây là ca duy nhất trong lô mà cây climax nằm giữa một đoạn đi ngang.
