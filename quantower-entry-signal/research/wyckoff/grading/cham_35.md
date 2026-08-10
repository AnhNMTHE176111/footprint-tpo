# Chấm bài #35 — Phân phối (DIST) · 2026-06-21 23:10 → 2026-06-22 00:11 (61 nến M1)

**Điểm: 2/10** — Không nên vẽ range ở đây. Đủ A→E trong **61 nến** với Phase B chỉ **10 nến**, và ngay sau khi range đóng, giá quay đầu ăn hết cấu trúc lên tận 4210.

## Lỗi (nặng → nhẹ)

### 1. Đây là nhiễu, không phải một vùng đấu giá — vi phạm L9 và tiêu chí "range quá vụn"
- **Thuật toán gắn:** A=15 · B=**10** · D=18 · E=19 nến, tổng 61 nến, tên "Phân phối".
- **Đúng phải là:** L9 — Phase B là phase **dài nhất**, là nơi xây "nguyên nhân". Ở đây B là phase **ngắn nhất**, ngắn hơn cả Phase A. Một cấu trúc phân phối hoàn chỉnh xây xong trong 10 phút đi ngang thì không có "nguyên nhân" nào để tạo "kết quả" (THEORY §2.2 Luật Nhân-Quả).
- **Dấu hiệu quyết định trên chart:** cả khung range chỉ rộng **11.1 giá** và vỏn vẹn ~25 nến từ BCLX tới cú SOW; phần còn lại của ảnh (trước và sau) là hai đợt trend dài gấp nhiều lần.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Quyết định đó đang đẻ ra chính loại rác này — cần ít nhất một sàn **tương đối**: Phase B phải dài hơn Phase A, nếu không thì không đóng range/không đặt tên.

### 2. Kết luận cấu trúc bị chính dữ liệu bác bỏ ngay sau đó — THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** SOW 23:35 (4159.8) → Phase D → Phase E → đóng "Phân phối" lúc 00:11.
- **Đúng phải là:** nhìn tiếp 40 nến sau mốc đóng, giá bật từ 4157 lên **4210**, xuyên qua cả range lẫn đỉnh BCLX. Cú "SOW" đó thực chất là một **shakeout/spring của một cấu trúc lớn hơn** — nó tìm thanh khoản dưới đáy rồi đảo chiều, đúng nguyên tắc "ưu tiên đọc theo lần rung chuyển cuối cùng" (THEORY §9).
- **Nghi phạm:** Phase E chốt bằng "đi thêm 1× chiều cao range" = **11.1 giá** — quá dễ với vàng M1. Range càng hẹp thì càng dễ tự phong Phase E. Cần sàn tuyệt đối theo ATR hoặc đo bằng chiều cao biên phụ.

### 3. Thiếu Phase C — vi phạm L8, và vá v7 #3 không cứu được ca này
- **Thuật toán gắn:** A → B → D → E, không có C.
- **Nghi phạm:** cửa sổ gán ngược = `min(60, 0.8 × len(B))`. Phase B chỉ 10 nến → cửa sổ **8 nến** → gần như chắc chắn không tìm được pivot hợp lệ. Nới hệ số từ 0.5 lên 0.8 **không sửa được lỗi gốc**: lỗi là ở chỗ cửa sổ bị buộc vào độ dài Phase B. Cửa sổ nên tính từ **mốc cú phá lùi lại một số nến cố định**, không nhân với len(B).

### 4. Nhãn BCLX rơi ngoài khung range, cách biên nó tạo ra 4.6 giá — vá v7 #4 chưa ăn (lần thứ 3)
- **Thuật toán gắn:** BCLX tại **23:04**, giá **4176.9**; range mở tại nến **23:10**, biên chính trên **4181.5**.
- **Đúng phải là:** chấm climax phải nằm trong khung, tại đỉnh 4181.5. Trên ảnh chấm BCLX nằm lửng giữa range, thấp hơn hẳn đường nét liền trên.
- **Nghi phạm:** giống bài #31/#32 — kẹp nhãn chỉ chặn hướng trượt về sau, không chặn nhãn nằm trước nến mở range. Ba trên năm bài của lô này dính cùng lỗi.

### 5. ST[A] ở 48% chiều cao range (L2) — cùng lỗi lặp với #32/#33
- ST[A] 23:24 tại 4175.7, cách mức climax 4181.5 tới 5.8 giá trên range cao 11.1 giá. Tỷ lệ hồi từ AR = 0.48, vừa qua ngưỡng mới 0.4. Ngưỡng đo sai chiều: phải ràng buộc **khoảng cách còn lại tới climax**, không phải tỷ lệ hồi từ AR.

### 6. MOVE trước climax ở sát mép điều kiện (L1)
- MOVE 24.6 giá / 70 nến / hiệu suất **0.39** (sàn 0.35). Nhìn ảnh, đoạn 22:07-23:04 là giá bò ngang nhích dần, không phải một move xu hướng bị chặn dứt khoát. Đây là ca cho thấy sàn hiệu suất 0.35 còn lỏng — nên soi lại phân bố hiệu suất của các range bị chê "vụn".
- Ghi nhận **đúng**: cửa sổ MOVE 70 nến nằm trọn sau khe cuối tuần (phiên mở lại ~22:00 ngày 06-21), không bắc qua khe — vá v6 #7 hoạt động.

### 7. Chỉ số bias tính trên 10 nến
- `bias = −1` được rút ra từ một Phase B dài 10 nến. Vô nghĩa về mặt thống kê. Nên chặn không xuất chỉ số Phase B khi B ngắn hơn một sàn nào đó (trình bày/diễn giải, không phải lỗi cấu trúc).

## Đạt
- **Mục 2 (L2):** đủ 3 lần đổi hướng, Phase A kết thúc đúng tại ST[A].
- **Mục 3 (L3):** biên chính = climax + AR, cố định; biên phụ 1.01x — không phình bậy.
- **Mục 4 (L4):** origin BCLX + phá xuống = Phân phối — đúng bảng L4 (dù bản thân cú phá sau đó thất bại, xem lỗi 2).
- **Mục 7:** SOW đặt đúng cây VSA 2.92x thân 0.75, có LPSY[D] một điểm duy nhất — đúng L7.
- **Mục 8:** chú thích er=0.13 gọi "nhịp HIỆU QUẢ, không phải hấp thụ" — **đúng dấu**, lỗi hard-code v6 đã hết.
