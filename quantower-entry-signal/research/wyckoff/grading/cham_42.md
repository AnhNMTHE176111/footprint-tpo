# Chấm bài #42 — Phân phối (DIST) · 2026-07-06 18:36 → 07-07 00:24 (274 nến M1)

**Điểm: 5/10** — bài khá nhất trong lô: cấu trúc A→E đủ, cú SOW và nhịp retest đọc đúng. Sửa 3 nhãn: vị trí BCLX?, ST[A], và ranh giới Phase C.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX? đặt trên một nến GIẢM, không phải cực trị — luật vi phạm: mục 3 điều kiện (3), L2
- **Thuật toán gắn:** BCLX? tại 18:42, giá 4177.1, VSA 3.29x.
- **Đúng phải là:** đỉnh cụm là nến **18:36** (H=4179.6, xanh) — chính là nến mở range và là mức biên chính trên. Nhãn climax phải nằm đó, hoặc ở nến 18:35 (O=4175.5 C=4178.3, xanh, VSA 2.41x) là cây đẩy cuối.
- **Dấu hiệu quyết định trên chart:** nến 18:42 có **O=4176.8, C=4175.8 → nến đỏ**, và đỉnh của nó (4177.1) thấp hơn biên trên 2.5 giá. Trên ảnh nhãn BCLX? rõ ràng treo lơ lửng dưới đường liền 4179.6. Một cao trào MUA không thể nằm trên nến giảm.
- **Nghi phạm trong thuật toán:** quy tắc "nhãn cụm climax = cây VSA cao nhất trong 8 nến" **không kiểm màu nến và không kiểm hướng**. Vá #4 của v7 (kẹp theo nến mở range) chỉ giới hạn cửa sổ, chưa lọc màu → lỗi còn nguyên. Phải thêm điều kiện: nến mang nhãn BCLX phải là nến **xanh** (hoặc close ≥ mid) và nằm trong 1× ATR của mức climax.

### 2. Phase C dài 56 nến — dài hơn cả Phase D (25) và E (3) — luật vi phạm: L8
- **Thuật toán gắn:** Phase C 22:56 → 23:56.
- **Đúng phải là:** Phase C phải là phase ngắn nhất. Nhịp test cuối trước khi sụp là đỉnh **22:35** chạm biên trên rồi cụm đi ngang 23:30–23:50; LPSY[C] nên lấy ở nhịp 23:40–23:50, Phase C rút xuống ~15–20 nến.
- **Dấu hiệu quyết định trên chart:** từ LPSY[C] (22:56) tới SOW (23:57) giá còn đi ngang cả tiếng trong lòng range, có tới 3 nhịp lên/xuống — đó là hành vi Phase B, không phải Phase C.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược Phase C vừa nới 0.5x→**0.8x** độ dài Phase B = 116 nến; máy lấy pivot **xa nhất** hợp lệ trong cửa sổ thay vì **nhịp test cuối cùng**. Nới cửa sổ đã sửa được ca "thiếu Phase C" nhưng đẻ ra ca "Phase C phình". Nên chốt bằng trần tuyệt đối (vd Phase C ≤ 1/3 Phase B) hoặc luôn lấy pivot **gần SOS/SOW nhất** thoả điều kiện.

### 3. ST[A] không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 19:21 tại 4174.5.
- **Đúng phải là:** test quay về vùng 4178–4179.6.
- **Dấu hiệu quyết định trên chart:** biên chính 4170.5–4179.6 = 9.1 giá; ST[A] ở 4174.5 = **44% chiều cao range**, đúng giữa. Hồi 4.0/9.1 = 0.44 nên vừa lọt ngưỡng 0.4 mới.
- **Nghi phạm trong thuật toán:** cùng gốc với bài #41 — `STA_MIN_AR_FRAC` đo nhịp hồi từ AR, không đo khoảng cách còn lại tới climax.

### 4. Range mở không có cao trào thật — luật vi phạm: L1 (điều kiện CẦN)
- **Thuật toán gắn:** "SINH TỪ CÚ PHÁ, không có cao trào thực sự", climax gắn dấu `?`.
- **Đúng phải là:** ghi nhận trung thực là tốt, nhưng phiếu **không có dòng MOVE** nào — không chứng minh được có move xu hướng bị chặn. Thực tế nhìn ảnh thì có (đợt tăng 4170→4179.6 lúc 18:20–18:36), chỉ là máy không đo. Nên vẫn đo và in MOVE cho cả range sinh từ cú phá, nếu không đạt thì đừng mở.

### 5. Phase E chỉ 3 nến (trình bày)
Giá sau 00:24 còn rơi thẳng từ 4163 xuống 4149 (thấy rõ nửa phải ảnh) nhưng range đã đóng. Không sai luật (đã đi đủ 2× chiều cao 9.1 giá) — nhưng chiều cao range quá mỏng khiến mốc "đi đủ xa" trở nên vô nghĩa. Đây là hệ quả biên chính chỉ 0.22% giá.

## Đạt
- L4: origin BCLX + phá xuống thật = **Phân phối** — tên đúng.
- SOW 23:57 neo đúng cây phá: VSA **4.12x**, thân 0.74, đóng dưới biên chính. Nhãn không còn rơi vào nến xác nhận yếu.
- L10: LPSY[D] 00:05 tại 4169.7 — hồi lên đúng mép biên 4170.5 rồi **giữ được ở ngoài**, sau đó đi tiếp. Đây là CBR sách vở, vẽ chuẩn.
- L3: không có biên phụ (tỷ lệ 1.00x) — trung thực, đúng tinh thần "có thể không có biên phụ nào".
- L9: Phase B 145 nến, dài nhất.
- Chú thích er=0.70 ghi "nhịp HIỆU QUẢ" — đúng dấu.
