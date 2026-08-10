# Chấm bài #10 — Tái phân phối (RE-DIST) · 2026-04-21 16:54 → 17:45 (48 nến M1)

**Điểm: 1/10** — Không được vẽ range ở đây. Chính phiếu số liệu tự khai "SINH TU CU PHA, khong co cao trao that" mà vẫn vẽ đủ 5 phase trên 48 nến.

## Lỗi (nặng → nhẹ)

### 1. Mở range không có climax thật, range đẻ ra từ cú phá của range #09 — luật vi phạm: L1
- **Thuật toán gắn:** `SC? 16:54 · 4762.2 · VSA 2.86x · biên độ nến 2.4 giá`, ghi chú của chính nó: "SINH TU CU PHA, khong co cao trao that".
- **Đúng phải là:** L1 đòi một MOVE xu hướng rõ ràng **bị cây climax chặn lại**. Ở đây không có: cây 16:54 nằm **giữa** đợt rơi, và hai cây liền trước nó còn dữ hơn nó (16:51 VSA 2.97x, 16:53 VSA **4.95x**, thân 0.59). Một cây 2.4 giá biên độ, volume 15, đứng giữa dòng chảy — không chặn được gì. Phiếu cũng **không có dòng "MOVE truoc climax"** (các bài khác đều có) → chính thuật toán cũng không dựng được move.
- **Dấu hiệu quyết định trên chart:** trên ảnh, sau "SC?" giá vẫn tiếp tục rơi tới 4753.7 rồi mới nảy — climax mà không chặn được move thì không phải climax.
- **Nghi phạm trong thuật toán:** nhánh sinh range nối tiếp sau breakout đang bỏ qua kiểm tra L1. Range `superseded` (#09) đẻ range con mà không phải thoả lại điều kiện mở.

### 2. AR xảy ra TRƯỚC climax, SC và ST[A] trùng đúng một cây — luật vi phạm: L2
- **Thuật toán gắn:** `AR (yếu) 16:40 · 4780.5` (14 nến **trước** SC), `SC? 16:54 · 4762.2` và `ST[A] 16:54 · 4762.2` — cùng thời điểm, cùng giá, cùng VSA 2.86x.
- **Đúng phải là:** trình tự bắt buộc là climax → AR → ST[A], đúng 3 lần đổi hướng. Ở đây có **0** lần đổi hướng: AR đứng trước climax là phản trình tự, còn ST[A] trùng climax nghĩa là không tồn tại cú test nào. Phase A = **1 nến** đã tự tố cáo điều đó.
- **Nghi phạm trong thuật toán:** khi range kế thừa biên/AR từ range mẹ, code gán AR bằng mốc cũ mà không ép `t(AR) > t(climax)`; và nhánh fallback ST[A] cho phép trùng chỉ số nến với climax.

### 3. Trật tự độ dài phase đảo ngược hoàn toàn — luật vi phạm: L8, L9
- **Thuật toán gắn:** A=1, B=**6**, C=**16**, D=25, E=1 nến.
- **Đúng phải là:** B dài nhất (L9), C ngắn nhất (L8). Ở đây C dài gấp gần 3 lần B, còn D mới là phase dài nhất. Phase E = 1 nến thì không phải "giá rời range đi tìm vùng giá mới" (L10), chỉ là chỗ cắt.
- **Nghi phạm trong thuật toán:** không có sanity-check quan hệ độ dài phase trước khi xuất range. Một guard đơn giản (`len(B) >= len(C)` và `len(B) = max`) sẽ loại ngay ca này.

### 4. Phase D/E không có retest giữ ngoài biên — luật vi phạm: L10, L5
- **Thuật toán gắn:** `SOW 17:18 · 4755.3`, Phase E bắt đầu 17:45.
- **Đúng phải là:** sau SOW giá **không** giữ được ngoài biên — trên ảnh nó bật thẳng từ ~4753 lên **4778** vào đúng 17:45 (gần chạm lại biên chính trên 4780.5). Đó là một SOW **thất bại** (theo L5 là shakeout xuống), không phải Phase D. Không có LPSY[D] nào giữ được dưới biên.
- **Dấu hiệu quyết định trên chart:** cây tăng biên độ lớn ngay tại mốc Phase E trên ảnh, đỉnh ~4778 — cao hơn cả LPSY[C] 4773.0.

### 5. 48 nến mà đủ Phase A→E — cảnh báo khung/nhiễu
- Chuẩn đã chốt: TR M1 chỉ 60–100 nến với đủ A→E thì phải nghi là nhiễu. Bài này **48 nến**, biên chính 18.3 giá. Đây là nhiễu, không phải vùng đấu giá.

## Đạt
- **L3 (kỹ thuật):** biên chính = climax 4762.2 + AR 4780.5, không kéo theo giá; mỗi bên tối đa 1 biên phụ; tỷ lệ 1.01x.
- **L7:** LPSY[C] đánh 1 điểm.
- **L6:** không còn ST[B].
- Thuật toán **có tự dán cảnh báo** "SINH TU CU PHA, khong co cao trao that" — thông tin đúng, chỉ thiếu bước dùng nó để **huỷ** range.

## Cần hỏi người học
- Range sinh ra ngay sau cú phá của một range trước (trường hợp #09 → #10): có nên cho phép mở range mới **miễn trừ** L1 không, hay phải bắt buộc chờ một climax thật mới? Tôi nghiêng về bắt buộc chờ, nhưng đây là chỗ luật hiện chưa phân xử.
