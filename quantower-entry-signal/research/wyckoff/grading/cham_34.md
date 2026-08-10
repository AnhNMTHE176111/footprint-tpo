# Chấm bài #34 — Tích luỹ (ACC) · 2026-06-15 20:44 → 2026-06-16 04:16 (390 nến M1, sinh từ cú phá)

**Điểm: 2/10** — Bài hỏng từ gốc: **Phase A dài âm 7 nến** (AR và ST[A] xảy ra TRƯỚC climax), và hai biên chính cao 5.8 giá nằm lọt thỏm giữa một vùng dao động 20 giá.

## Lỗi (nặng → nhẹ)

### 1. Phase A = **−7 nến**, thứ tự sự kiện đảo ngược — vi phạm L2 tận gốc
- **Thuật toán gắn:** Phase A "bắt đầu 20:44, kết thúc 20:36" → −7 nến. Bảng sự kiện: **AR (yếu) 20:28 → ST[A] 20:36 → SC? 20:44**.
- **Đúng phải là:** L2 quy định đúng 3 lần đổi hướng theo thứ tự climax → AR → ST[A]. Ở đây climax đứng **cuối**. Hai nhãn AR/ST[A] thực chất là **di sản của range cha #33** (AR 20:28 tại 4336.0 chính là LPSY[D] của bài #33, cùng nến, cùng giá, cùng VSA 0.30x).
- **Dấu hiệu quyết định:** VSA của "AR" = **0.30x** và của "ST[A]" = **0.55x** — hai cây chết, không cây nào là phản ứng thật.
- **Nghi phạm trong thuật toán:** `WySpawnSidewaysRange` (mục 5.4) tạo range con neo tại cực trị cú phá nhưng **không reset con trỏ sự kiện/nến bắt đầu**, để máy đi tìm AR/ST[A] trong đoạn nến **trước** nến climax của range con. Phải chặn cứng: mọi sự kiện Phase A của range con phải có index > index climax.

### 2. Biên chính 5.8 giá nằm giữa vùng dao động 20 giá — vi phạm L3
- **Thuật toán gắn:** biên chính 4330.2-4336.0 (**0.13% giá**), biên phụ 4327.4-4346.8 (19.4 giá), tỷ lệ **3.34x**.
- **Đúng phải là:** hai biên chính phải **bao** vùng đấu giá. Nhìn ảnh, hai đường nét liền chạy xuyên **giữa** đám nến; suốt 390 nến giá ra vào hai đường đó liên tục. Vùng đấu giá thật là 4327-4347, tức chính hai đường **nét đứt**.
- **Hệ quả dây chuyền:** chiều cao range 5.8 giá làm mọi ngưỡng tỷ lệ vô nghĩa — đích Phase E ("đi thêm 1× chiều cao") chỉ còn **5.8 giá**, nên một nhịp nhích nhẹ cũng chốt được Phase E (xem lỗi 5).
- **Nghi phạm:** cơ chế SIDEWAYS neo biên chính bằng cực trị cú phá + AR tìm sai (lỗi 1). Guard "tỷ lệ biên phụ/chính ≤ 4.0x" bắt hụt ca 3.34x này — ngưỡng quá lỏng.

### 3. mSOW gán ở **biên TRÊN** — sai bên
- **Thuật toán gắn:** mSOW 23:11 tại **4335.9**, đúng bằng biên chính **trên** 4336.0; trên ảnh chấm nằm phía trên đường nét liền trên.
- **Đúng phải là:** thăm dò phía trên là **UT[B] / mSOS**. mSOW chỉ dành cho cạnh dưới (mục 5.1, v6 đã chốt "chỉ còn phân biệt THEO BÊN").
- **Nghi phạm:** với range con, quan hệ "climax = cạnh dưới, AR = cạnh trên" bị đảo (climax 4330.2 dưới, AR 4336.0 trên) nhưng nhánh chọn bên hình như vẫn suy từ `origin` (SC ⇒ mặc định cạnh climax là cạnh bị phá) thay vì so giá thực với hai mức.

### 4. mSOS nằm trong lòng Phase C nhưng khai là Phase B — timeline tự mâu thuẫn
- **Thuật toán gắn:** Phase C = 02:42 → 03:41; sự kiện **mSOS 03:34 ghi Phase B**.
- **Đúng phải là:** một sự kiện không thể thuộc Phase B khi dải Phase C đang trùm lên nó. Ngoài ra mSOS này có **VSA 1.08x, thân 0.15** — cây rác, không đủ tư cách "cú phá có thật rồi thu vào" theo định nghĩa v6.
- **Nghi phạm:** vá v7 #5 (quét lại cây VSA cao nhất trong đoạn thăm dò) **không chạy** cho nhánh hạ cấp này; và trường `phase` của sự kiện được ghi tại thời điểm phát sinh, không cập nhật lại khi Phase C được gán ngược.

### 5. Phase E không phải "đi tìm vùng giá mới" — vi phạm L10
- **Thuật toán gắn:** SOS 03:42 (4352.7) → Phase E 28 nến, đóng range 04:16 "completed".
- **Đúng phải là:** ngay sau mốc đóng, giá rơi lại về 4343-4345, tức **lùi qua cả biên phụ trên 4346.8** (thấy rõ ở phần bên phải ảnh). Cú phá này là một **UT/mSOS**, không phải SOS hoàn tất.
- **Nghi phạm:** đích Phase E đo bằng chiều cao **biên chính** (5.8 giá) — hệ quả trực tiếp của lỗi 2. Nên đo bằng chiều cao **biên phụ** hoặc đặt sàn tuyệt đối theo ATR.

### 6. Phase C dài 60 nến = đúng trần cửa sổ — vi phạm L8
- Phase C 60 nến trong khi Phase D chỉ 7 và Phase E 28 → C **không** phải phase ngắn nhất.
- **Nghi phạm:** vá v7 #3 nới cửa sổ gán ngược lên 0.8× Phase B; với B = 303 nến thì `min(60, 242) = 60` → LPS[C] luôn bị đẩy về **mép xa nhất** của cửa sổ, Phase C dính trần. Nới cửa sổ đã đổi lỗi "thiếu Phase C" thành lỗi "Phase C dài bằng trần". Phải chọn **nhịp test cuối cùng gần cú phá nhất**, không phải pivot xa nhất trong cửa sổ.

## Đạt
- **Mục 4 (L4):** origin SC? + phá lên = Tích luỹ — đúng bảng L4 (dù climax là giả, đã khai rõ "SINH TỪ CÚ PHÁ, không có cao trào thật").
- **Mục 5 (L9):** Phase B 303/390 nến, dài nhất.
- **Mục 7:** SOS 03:42 đặt đúng cây mạnh (VSA 3.69x, thân 0.77) và có LPS[D] ngay sau — phần đặt nhãn cú phá làm đúng.
- **Mục 8:** chú thích er=0.67 gọi "nhịp HIỆU QUẢ, không phải hấp thụ" — **đúng dấu**, lỗi hard-code v6 đã hết.
- **Mục 9:** LPS[C] và LPS[D] mỗi cái đúng **một điểm**, không vẽ vùng, không spam — đúng L7.
