# Chấm bài #54 — Chưa rõ (SC) / ACC? · 2026-07-20 12:02 → 22:50 (587 nến M1)

**Điểm: 1/10** — không nên vẽ range như thế này. Một phiên 11 tiếng bị mô tả bằng hai nét liền cách nhau 5.4 giá nằm chính giữa vùng dao động; Phase B chiếm 97% range, không có Phase C, Phase D mồ côi không có nhãn phá vỡ nào.

## Lỗi (nặng → nhẹ)

### 1. Biên chính vô nghĩa — climax không chặn nổi move, AR quá nông — luật vi phạm: L1 + L3
- **Thuật toán gắn:** biên chính 4016.5 – **4021.9 = 5.4 giá (0.13%)**; biên phụ 4004.1 – 4023.9 = 19.8 giá, tỷ lệ **3.67×** (lách sát guard 4.0×).
- **Đúng phải là:** vùng đấu giá thật trên ảnh là **~4004 – 4024**. Nhìn chart: nến cắt qua hai nét liền hàng trăm lần, giá xuống 4004 lúc 14:00 (thấp hơn "biên dưới" 12.4 giá = **2.3× cả chiều cao biên chính**) rồi vẫn quay lại. Cây climax 12:02 rõ ràng **không chặn được move**.
- **Dấu hiệu quyết định trên chart:** AR tại 12:06 chỉ hồi 5.4 giá sau một move giảm 22.9 giá = **24% retrace**, VSA 0.69x. Một nhịp hồi 4 nến volume dưới trung bình không đủ tư cách dựng biên trên của cả cấu trúc.
- **Nghi phạm trong thuật toán:** (a) guard "climax không chặn được move" (4× biên độ TB) chỉ chạy trong Phase A/A_st, tắt hẳn ở Phase B — cả 568 nến sau đó không ai kiểm lại; (b) sàn tương đối của AR (≥0.5× nhịp hồi lớn nhất trong lòng move) quá dễ khi move đi thẳng một mạch (hiệu suất 0.67) nên gần như không có nhịp hồi nào để so.

### 2. Phase D tồn tại nhưng không có SOS/SOW nào — luật vi phạm: L10 + lỗi F (v5) tái phát
- **Thuật toán gắn:** dải phase A (14n) → B (568n) → **D (6n)**; bảng sự kiện **không có nhãn SOS hay SOW nào**, chỉ có 1 mSOS và 3 mSOW.
- **Đúng phải là:** cú phá bị hạ cấp thành mSOW thì dải phase phải **trả về B** và Phase D phải biến mất khỏi timeline. Ở đây đoạn Phase D nằm lại mồ côi, đúng kiểu lỗi C/F của v5.
- **Dấu hiệu quyết định:** vạch tím "Phase D (6n)" ở 22:45 trùng đúng nến mSOW cuối (VSA 1.39x, thân 0.06 — một cây gần như không có thân).

### 3. Không có Phase C, Phase B chiếm 97% range — luật vi phạm: L8 + L9
- B = 568/587 nến. Không có Spring/Shakeout/UTAD nào, cũng không có LPS[C]/LPSY[C] gán ngược (vì không có SOS/SOW để gán ngược từ đó). Cấu trúc chỉ còn A → B → D, không đọc được gì.

### 4. Nhãn mSOW spam 3 lần — luật vi phạm: mục 9 (nhãn dư) + tinh thần L3 (mỗi bên một biên phụ)
- **Thuật toán gắn:** mSOW 16:41 (4005.2, VSA 11.39x), mSOW 20:58 (4011.8, VSA 9.95x, `provisional`), mSOW 22:45 (4007.9, VSA 1.39x, `provisional`).
- **Đúng phải là:** giữ đúng một cú sâu nhất (16:41 tại 4005.2) như quy tắc "mỗi bên chỉ một" đang áp cho UT[B]/ST[B]. Riêng cây 22:45 VSA 1.39x nông hơn cả hai cú trước mà vẫn được ghi nhãn — vi phạm cả quy tắc "cú mới nông hơn thì không ghi gì".
- **Nghi phạm:** nhánh mSOS/mSOW không đi qua bộ lọc "chỉ giữ cực trị xa nhất" mà UT[B]/ST[B] đang dùng.

### 5. ST[A] xuyên qua climax 3.7 giá — luật vi phạm: L2
- ST[A] 12:15 tại **4012.8**, thấp hơn mức climax 4016.5 **3.7 giá** = 68% chiều cao range. Đó không phải "bị chặn nhẹ lần nữa" mà là giá đi tiếp. Trần "ST[A] ≤ 1.0× chiều cao range" vô dụng khi range chỉ cao 5.4 giá — trần tự co theo cái sai của chính nó.

### 6. Cây VSA 11.39x bị bỏ lửng — luật vi phạm: mục 8 (Effort vs Result)
- mSOW 16:41 có VSA **11.39x** đẩy giá xuống 4005.2 rồi giá quay lại — nỗ lực cực lớn, kết quả bằng 0. Đây là dấu hiệu hấp thụ mạnh nhất cả phiên. Chỉ số "nhịp nỗ lực/kết quả cao nhất" lại chỉ về 14:19 với er=1.21 — bỏ sót đúng cây quan trọng nhất (cùng lỗi với bài #49: er tính theo nhịp giữa pivot, không quét từng nến).

## Đạt
- Điều kiện cây climax (mục 3.1): nến 12:02 VSA 4.88x, biên độ 9.0 giá, là đáy cửa sổ — đúng chuẩn.
- MOVE trước climax đo sạch: 22.9 giá / 28 nến / hiệu suất **0.67** — move thật, không phải đi ngang. Đây là ca hiếm trong lô có hiệu suất cao hẳn trên ngưỡng.
- Nhãn SC nằm đúng nến mở range (12:02), không lệch như #49/#52.
- Chỉ số SOT đo được và đọc đúng chiều: SOT-dn n=4 với tỷ lệ volume nhịp cuối/đầu 1.55 → gắn nhãn "HẤP THU (cạnh giữ vùng)" — mô tả đúng những gì thấy trên chart (giá bị đỡ nhiều lần quanh 4005–4008).

## Cần hỏi người học
- Với ca thế này, muốn máy **bỏ hẳn range** (guard "climax không chặn được move" chạy suốt cả Phase B) hay muốn nó **vẽ lại biên chính** theo cực trị mới? Hai hướng mâu thuẫn với L3 ("biên chính cố định sau Phase A") nên cần anh phân xử.
