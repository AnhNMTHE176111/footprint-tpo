# Chấm bài #41 — Chưa rõ (SC) (ACC?) · 2026-07-06 12:43 → 19:00 (377 nến M1)

**Điểm: 2/10** — range mở đúng chỗ nhưng đọc sai toàn bộ đoạn cuối: giá đã rời hẳn biên trên từ 16:40 mà máy vẫn để Phase B chạy thêm 120 nến, Phase C mất hẳn, ST[A] rơi giữa range. Phải sửa nhãn và sửa cơ chế xác nhận phá vỡ.

## Lỗi (nặng → nhẹ)

### 1. Giá ở ngoài biên chính 120 nến liên tiếp mà vẫn là Phase B — luật vi phạm: L5 (phá THẬT), L10
- **Thuật toán gắn:** Phase B kéo tới 18:34, SOS mãi 18:35; đoạn 16:40–18:34 không có nhãn phá vỡ nào ngoài một cái mSOS lẻ ở 18:00.
- **Đúng phải là:** SOS phải bắn quanh 16:45–16:50. Từ đó Phase D (retest 4166–4170 lúc 17:00) rồi Phase E.
- **Dấu hiệu quyết định trên chart:** đếm trên dữ liệu gốc, **120/120 nến từ 16:40 đến 18:40 đóng cửa TRÊN biên chính trên 4160.7**. Không một nến nào lùi lại trong range. Theo chính spec ("ở ngoài quá 40 nến **và** ≥60% nến đóng ngoài biên") điều kiện đã thoả từ lâu.
- **Nghi phạm trong thuật toán:** điều kiện phá thật đo bằng **biên phụ**, mà biên phụ trên lại được nới liên tục theo từng đỉnh mới của chính cú phá đang xét → không bao giờ vượt được chính nó. Đây đúng là lỗi "biên phụ tự nới rồi tự vượt" mà v7 tuyên bố đã vá bằng ngưỡng 30 tick — **chưa hết**: ngưỡng tick không chạm tới cơ chế nới biên. Phải khoá biên phụ phía đang bị test ngay từ nến đầu thò ra, hoặc chuyển nhánh "40 nến + 60%" sang đo bằng **biên chính**.

### 2. Mất hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase chỉ có A → B → D. Không có Phase C.
- **Đúng phải là:** phải có LPS[C]. Nhịp lùi 17:05–17:20 (về ~4166, ngay trên biên chính trên) chính là test cuối trước khi giá bung — đó là LPS[C] gán ngược.
- **Dấu hiệu quyết định trên chart:** trên ảnh thấy rõ một nhịp thụt về sát đường liền 4160.7 rồi bật lên, ngay trước đoạn tăng cuối.
- **Nghi phạm trong thuật toán:** ràng buộc v6 "pivot gán ngược phải nằm **trong range** và đúng **nửa range**". Ở đây SOS bắn quá muộn (18:35) nên toàn bộ 60 nến nhìn lại đều nằm **ngoài** range → không tìm được pivot nào hợp lệ → bỏ luôn Phase C. Việc nới cửa sổ 0.5x→0.8x Phase B không cứu được ca này; gốc bệnh là lỗi #1.

### 3. ST[A] không test vùng climax, nằm giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:15 tại **4150.7**.
- **Đúng phải là:** một cú test quay về vùng 4143–4146 (vùng SC). Nếu không có thì Phase A **chưa xong**, chưa được chốt biên.
- **Dấu hiệu quyết định trên chart:** biên chính 4143.3–4160.7 (17.4 giá); ST[A] ở 4150.7 = **cách climax 7.4 giá = 43% chiều cao range**, đúng giữa vùng. Nó chỉ hồi 0.57 khoảng AR↔climax nên lọt qua ngưỡng mới 0.4.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC` nâng 0.2→0.4 đo **nhịp hồi từ AR**, không đo **khoảng cách còn lại tới climax**. Hai đại lượng này khác nhau. Cần thêm trần: ST[A] phải nằm trong ~35% chiều cao range tính từ biên climax.

### 4. mSOS 18:00 sai vai — luật vi phạm: mục 5.1 (định nghĩa mSOS ở v6)
- **Thuật toán gắn:** mSOS tại 4173.8 (18:00), tức "phá được nhưng thu hẳn vào trong range rồi hướng sang biên đối diện".
- **Đúng phải là:** giá **không hề** thu vào trong range sau 18:00 — nhịp lùi sâu nhất chỉ về ~4170, vẫn trên biên chính 9 giá. Đây chỉ là một nến trong lòng cú phá đang chạy, không phải cú phá thất bại.
- **Dấu hiệu quyết định trên chart:** SOS 18:35 ở 4178.3 chỉ cách mSOS 4.5 giá và 35 nến, cùng một đoạn tăng liên tục trên ảnh.
- **Nghi phạm trong thuật toán:** nhánh hạ cấp mSOS chạy trước khi biết kết cục thật của cú phá; phải yêu cầu **đóng cửa lùi hẳn qua biên chính** mới được hạ cấp.

### 5. Range `superseded` nhưng vẫn vẽ SOS + Phase D — lỗi trình bày/nhất quán
- Tiêu đề ghi "Chưa rõ (SC) (ACC?) [superseded]" (không đặt tên vì Phase E chưa xong), nhưng bên dưới vẫn có SOS, LPS[D] và dải Phase D 26 nến. Người đọc không biết cuối cùng range này kết luận gì. Nếu đã có SOS + Phase D thì phải gọi thẳng **Tái tích luỹ** (SC + phá lên = L4), hoặc đừng vẽ Phase D.

## Đạt
- L1: MOVE giảm 21.8 giá / 76 nến, hiệu suất 0.36 — có move thật, climax 12:43 là đáy cửa sổ, chặn đúng move (nhìn ảnh mũi xám trùng khớp).
- Nhãn climax neo đúng cây: nhãn SC ở nến VSA 3.27x (12:41) thay vì cây 1.28x mở range — sửa v5 vẫn giữ được.
- L9: Phase B 319/377 nến — dài nhất, đúng.
- Chú thích nỗ lực/kết quả er=0.84 ghi "nhịp HIỆU QUẢ, không phải hấp thụ" — **đúng dấu**, lỗi hard-code "vùng hấp thụ NGHI VẤN" đã hết.
- Biên phụ mỗi bên đúng 1 cái (4140.6 / 4173.8), tỷ lệ 1.91x — hợp L3.
