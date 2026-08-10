# Chấm bài #48 — Chưa rõ (BCLX) (DIST?) · 2026-07-15 18:31 → 2026-07-16 01:24 (353 nến M1)

**Điểm: 4/10** — bài khá nhất trong lô. Điều kiện mở range làm đúng bài bản (move thật, climax chặn move, nhãn climax rơi đúng cây mạnh nhất). Hỏng ở nửa sau: không có ST[A] thật, thiếu hẳn Phase C, và cấu trúc đã phá xuống rõ mà vẫn không được đặt tên.

## Lỗi (nặng → nhẹ)

### 1. Range KHÔNG có ST[A] thật — Phase A chưa đóng — luật vi phạm: L2; vá #2 CHƯA đủ
- **Thuật toán gắn:** ST[A] 20:26 tại 4069.0.
- **Đúng phải là:** ST[A] phải là cú quay lại **phía climax** và bị chặn ở đó. 4069.0 cách climax 4089.1 tới **20.1 giá = 59% chiều cao range** — nó nằm giữa range, đúng cái "ngọ nguậy giữa range" mà giảng viên đã chê nhiều lần.
- **Dấu hiệu quyết định trên chart:** biên chính 4055.2–4089.1 (33.9 giá); ST[A] hồi từ AR đúng 13.8 giá = **0.41×**, vừa lọt ngưỡng mới 0.40. Nhìn ảnh: sau ST[A], suốt 212 nến Phase B giá **chưa một lần** với lại vùng 4080–4089 — chỉ số bias của chính thuật toán ghi `-1` ("không với nổi biên trên") xác nhận điều đó.
- **Kết luận đúng phải là:** cấu trúc này thực ra **chưa hoàn tất Phase A** (không có cú test lại vùng BCLX) → chưa đủ điều kiện chốt hai biên chính.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC` nâng 0.2→0.4 không chạm được lỗi vì đo từ AR. Cần ràng buộc thứ hai: ST[A] phải cách **mức climax** ≤ ~0.35× chiều cao range.

### 2. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** A (116) → B (212) → D (26). Không có C.
- **Đúng phải là:** phải gán ngược Phase C từ SOS/SOW. Trong 60 nến trước SOW 00:59 có một nhịp hồi lên rõ (đỉnh ~4068 quanh 00:39, thấy rõ trên ảnh là cụm nến xanh nhô lên cuối Phase B) rồi rơi thẳng — đó là **LPSY[C]**.
- **Nghi phạm trong thuật toán:** ràng buộc v6 "pivot phải nằm **đúng nửa range**" (LPSY[C] nửa trên). Trung điểm range = 4072.15; đỉnh 4068 nằm **dưới** trung điểm nên bị loại. Nhưng nửa trên của range này là **vùng chết** (giá không bao giờ về lại sau Phase A), nên điều kiện "nửa trên" bảo đảm không bao giờ tìm được LPSY[C]. Vá #3 (nới cửa sổ 0.5×→0.8× Phase B) **không chạm** lỗi này — nút thắt là ràng buộc nửa range, không phải độ dài cửa sổ. Đề xuất: đo nửa range theo **dải giá thực tế của Phase B**, không theo biên chính.

### 3. Đã có SOW + LPSY[D] mà range không được đặt tên — luật vi phạm: L4
- **Thuật toán gắn:** "Chưa rõ (BCLX) (DIST?)", `superseded`.
- **Đúng phải là:** origin BCLX + phá xuống thật = **Phân phối**. SOW 00:59 VSA 4.46× thân 0.81, LPSY[D] 01:10 hồi lên 4055.1 rồi tiếp tục rơi tới 4034 — chuỗi CBR hoàn chỉnh (L10).
- **Nghi phạm trong thuật toán:** mục 5.4 cấm đặt tên vô điều kiện cho range `superseded`. Range cha đã có SOW xác nhận + retest giữ được thì phải được đặt tên.

### 4. Nhãn climax lệch mức biên 2.5 giá (nhẹ)
- **Thuật toán gắn:** nhãn BCLX tại 18:30 giá 4086.6 (VSA 4.52×); mức biên chính trên lấy 4089.1 (high nến 18:31, VSA 2.00×).
- **Ý kiến:** ở đây việc tách "mức" và "nhãn" là **chấp nhận được** — cây 18:30 đúng là cây mạnh nhất cụm và đúng màu (xanh, thân 0.81, chặn move tăng). Chỉ ghi nhận: trên ảnh chấm BCLX nằm thấp hơn nét liền biên trên, người đọc dễ tưởng vẽ sai. Đây là lỗi **trình bày**, không phải cấu trúc.

### 5. Chú thích "hấp thụ nghi vấn" đúng dấu nhưng effort chỉ 1.01× (trình bày/diễn giải)
- er = 5.25 với effort **1.01×** (volume trung bình) và result 0.19. Volume trung bình + giá đứng yên = phiên Á vắng khách, không phải hấp thụ. Vá #1 đã đúng dấu er; còn thiếu **sàn effort** (gợi ý ≥ 1.5×) trước khi được phép dùng chữ "hấp thụ".

## Đạt
- **Điều kiện mở range (L1) ĐẠT thật:** MOVE 49.8 giá / 107 nến / hiệu suất 0.35 — nhìn ảnh là một nhịp tăng liên tục 4036 → 4089 có cấu trúc đỉnh-đáy cao dần, không phải một cây tin. Climax là cực trị của cửa sổ và thực sự chặn move.
- **Nhãn climax rơi đúng cây mạnh nhất cụm** (4.52× so với 2.00× của nến mở range) và **đúng màu nến** — vá #4 hoạt động ở bài này.
- **Biên (L3) ĐẠT:** biên phụ = biên chính (tỷ lệ 1.00×) vì Phase B chưa từng thủng ra ngoài — trung thực, không bịa biên phụ.
- **Bias = −1 đo đúng** và khớp hướng phá thật (xuống).
- **Phase B (212 nến) là phase dài nhất** — L9 đạt.
- SOW neo đúng cây phá (4.46×, thân 0.81, đóng cửa dưới biên chính); LPSY[D] là nhịp retest giữ được ngoài biên → đúng CBR.

## Nếu là tôi
Vẽ range này, nhưng: chờ **ST[A] thật** (nếu 212 nến không có cú nào với lại 4080+ thì đây là cấu trúc **dốc xuống**, phải hạ biên trên làm việc xuống ~4072 thay vì giữ 4089.1 — một cái đỉnh râu không ai chạm lại); thêm LPSY[C] ở nhịp hồi ~00:39; và đặt tên **Phân phối**.
