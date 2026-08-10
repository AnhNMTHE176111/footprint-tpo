# Chấm bài #43 — Tích lũy (ACC) · 2026-06-30 12:58 → 15:14 (136 nến M1)

**Điểm: 6/10** — Khung range vẽ đúng, cú phá đọc đúng; phải sửa ST[A] và lấp Phase B đang trống trơn.

## Lỗi (nặng → nhẹ)

### 1. ST[A] lơ lửng giữa range, cắt Phase A trước cú test thật — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:24 tại 4033.0, Phase A đóng tại đó (27 nến).
- **Đúng phải là:** cú test thật vùng SC là nhịp 13:39–13:42 (đáy ~4027, nhìn trên ảnh), chứ không phải 4033.0.
- **Dấu hiệu quyết định:** biên chính 4022.1–4047.5 = 25.4 giá. ST[A] 4033.0 nằm ở **(4033.0−4022.1)/25.4 = 43% chiều cao** — đúng giữa range, không chạm vùng climax. Retrace từ AR đo được 0.57, tức **vừa lọt ngưỡng 0.55 mới** mà vẫn sai vị trí.
- **Nghi phạm:** `STA_MIN_AR_FRAC=0.55` đo "hồi bao nhiêu % từ AR". Với range mà AR nằm thấp, 0.55–0.57 vẫn dừng ở giữa. Cần thêm ràng buộc tuyệt đối theo phía climax, ví dụ ST[A] phải nằm trong **1/3 dưới** chiều cao range (theo THEORY §5, bảng vị trí test Phase A).

### 2. Nhãn SC rơi vào nến XANH, lệch khỏi mức biên — luật vi phạm: mục 3(3) spec (màu nến khớp hướng move)
- **Thuật toán gắn:** nhãn SC tại 13:00, giá 4022.9, VSA 3.33x.
- **Đúng phải là:** nến 12:58 (O 4024.6 / C 4022.7, đỏ, low 4022.1, VSA 2.60x) — đúng cây chặn move giảm và đúng mức biên chính.
- **Dấu hiệu quyết định:** nến 13:00 có O 4023.7 → C 4029.6, **nến xanh tăng 5.9 giá** — đó là cây bật ngược, không phải cây cao trào bán. Nhãn SC cũng cao hơn biên chính dưới 0.8 giá.
- **Nghi phạm:** cửa sổ cụm climax chọn nến VSA cao nhất mà **không kiểm màu nến / không kiểm nến đó có phải cực trị**. Lỗi đã ghi nhận ở 13.1c là chưa sửa (thử rồi revert).

### 3. Phase B 38 nến hoàn toàn trống nhãn — luật vi phạm: L9
- **Thuật toán gắn:** không một nhãn nào giữa ST[A] (13:24) và LPS[C] (14:03).
- **Đúng phải là:** trên ảnh có ít nhất một nhịp xuống ~4027 (13:39) và một nhịp lên ~4046 (13:33) — hai lần test hai biên, phải ra được ST[B] và UT[B].
- **Dấu hiệu quyết định:** bias đo được `+0` = "test CẢ HAI biên", tức chính thuật toán biết Phase B đã chạm hai phía, nhưng không sinh nhãn nào.
- **Nghi phạm:** nhãn UT[B]/ST[B] chỉ sinh khi giá **thò ra ngoài biên chính quá 10 tick**. Test chạm biên từ bên trong không bao giờ được ghi → Phase B trống ở phần lớn bài.

### 4. Phase E (52 nến) dài hơn Phase B (38 nến) — luật vi phạm: L9 (trình bày tỉ lệ phase)
- **Dấu hiệu quyết định:** A 27 · B 38 · C 6 · D 14 · **E 52**. Phase dài nhất phải là B.
- **Nghi phạm:** trần Phase E = 120 nến / 2× chiều cao, không có ràng buộc tương đối `len(E) ≤ len(B)`.

## Đạt
- **Mở range (L1):** MOVE giảm 25.6 giá / 72 nến / hiệu suất 0.37, climax là cực trị chặn move — điều kiện CẦN thoả rõ, thấy được trên ảnh.
- **Biên chính (L3):** 4022.1 (climax) + 4047.5 (AR), cố định, không kéo theo giá; không có biên phụ (tỷ lệ 1.00x) — trung thực.
- **Phase C (L8):** 6 nến, ngắn nhất trong cả 5 phase. Đúng.
- **SOS (L10):** neo đúng cây 14:09 VSA **4.17x**, thân 0.87 — cây phá thật, không phải nến xác nhận thứ ba.
- **Tên range (L4):** origin SC + phá lên thật (giá đi từ 4047.5 lên 4078, quá 1× chiều cao) → Tích luỹ. Đúng.
- **Phase D:** có LPS[D] 14:12 giữ trên biên, đúng mô hình CBR.
