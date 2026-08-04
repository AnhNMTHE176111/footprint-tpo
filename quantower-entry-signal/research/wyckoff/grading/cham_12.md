# Chấm bài #12 — Tái tích luỹ (RE-ACC) · 2026-05-06 03:20 → 08:58 (187 nến M1)

**Điểm: 1/10** — **Không được vẽ range ở đây.** Cây "climax" VSA 0.58x với 3 hợp đồng, biên chính 7.5 giá; toàn bộ cấu trúc là một xu hướng tăng liên tục bị cắt ngang một cách tuỳ tiện.

## Lỗi (nặng → nhẹ)

### 1. Không có climax — cây mở range VSA 0.58x, volume 3 hợp đồng, biên độ 1.0 giá — luật vi phạm: L1 (climax là điều kiện ĐỦ) + §3.3 THEORY (BCLX)
- **Thuật toán gắn:** BCLX tại 03:20, giá 4695.2, VSA **0.58x**, biên độ nến **1.0 giá**, volume **3**.
- **Đúng phải là:** BCLX theo định nghĩa gốc là "volume + spread tăng rõ rệt, lực mua đạt đỉnh". Cây này có volume **dưới trung bình** và biên độ 1.0 giá. Không có cao trào nào cả. Đây là một cây bình thường trong phiên Á giờ chết, được chọn chỉ vì nó là đỉnh cục bộ.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax — volume các cây là 2, 8, 1, 6, 2, 3, **3**, 1, 2, 1, 1, 2. Cả cụm không có nổi 10 hợp đồng ở cây nào ngoài cây -5.
- **Nghi phạm trong thuật toán:** bảng tham số mục 11 ghi "VSA climax ≥ 2.2x" và "biên độ ≥ 1.4× TB 20 nến". **Cây này không thoả cả hai** mà vẫn mở được range. Đây là lỗi parity/bug thật, không phải lỗi ngưỡng: hoặc mốc climax bị dời bởi cụm (mục 4.0) sang một cây không kiểm lại điều kiện climax, hoặc điều kiện chỉ kiểm ở cây ứng viên gốc rồi bỏ. **Sau khi dời mốc cụm, phải kiểm lại VSA/biên độ ở cây mới.**

### 2. Biên chính 7.5 giá = 0.16% — không phải một vùng đấu giá — luật vi phạm: L1 (vùng đấu giá thật) + "khung quá thô / range quá vụn" (CHART_CASES)
- **Thuật toán gắn:** biên chính 4687.7–4695.2 = **7.5 giá**; biên phụ 4687.7–4723.2 = 35.5 giá.
- **Đúng phải là:** biên phụ **rộng gấp 4.7 lần** biên chính. Khi tỉ lệ này xảy ra, nghĩa là "vùng cân bằng" mà máy tìm ra chỉ là một khoảnh khắc dừng chân 12 nến trong một đợt tăng, còn phần lớn hoạt động giá nằm hoàn toàn bên ngoài nó. Không có cân bằng nào ở đây.
- **Dấu hiệu quyết định trên chart:** hai đường liền cam sát nhau như một đường đôi; toàn bộ nửa phải chart nằm trên chúng.

### 3. Move trước climax hiệu suất 0.36 — sát sàn 0.35 và bản chất là move đi xuyên qua climax — luật vi phạm: L1
- **Thuật toán gắn:** move tăng 91.7 giá, 137 nến, hiệu suất **0.36**.
- **Đúng phải là:** climax phải **chặn** move. Ở đây giá vượt qua mức "BCLX" 4695.2 lên tới 4723.2 (biên phụ) rồi 4742.3 — tức **vượt 47 giá**, gấp hơn 6 lần chiều cao biên chính. Theo mục 4.0 chính tài liệu thuật toán: "giá còn vượt mức climax quá 3× biên độ TB → climax không chặn được move, **bỏ range**". Điều kiện này đã không bắn.
- **Dấu hiệu quyết định trên chart:** đường xám "chân MOVE" chạy thẳng một mạch từ 4581 lên tới climax, rồi giá tiếp tục thẳng lên 4760 — một đường xu hướng liên tục, chỉ bị máy cắt làm đôi ở giữa.
- **Nghi phạm trong thuật toán:** guard "vượt 3× biên độ TB" ở mục 4.0 chỉ áp trong **cửa sổ cụm 8 nến**, sau đó tắt. Nên áp cho cả Phase A và Phase B.

### 4. LPS[C] và SOS đều là cây volume nổ nhưng nằm ngoài range 23–47 giá — luật vi phạm: L8 (Phase C là tín hiệu đầu tiên phá biên kia)
- **Thuật toán gắn:** LPS[C] 08:36 giá **4718.1** (VSA 4.89x), SOS 08:50 giá **4742.3** (VSA 10.29x).
- **Đúng phải là:** LPS[C] ở 4718.1 nằm **cao hơn biên chính trên 22.9 giá**. Một "test cuối trước cú phá" không thể nằm cách vùng đấu giá 3 lần chiều cao của chính vùng đó. Đây là một nhịp nghỉ giữa xu hướng, không phải LPS.
- **Nghi phạm trong thuật toán:** Phase C gán ngược (mục 6, case khó) lấy "đáy sâu nhất trong 60 nến trước cú phá" mà **không kiểm nó có nằm trong/gần range hay không**. Cần chặn: LPS[C] phải nằm trong khoảng biên chính ± một nửa chiều cao range.

### 5. Phase E dài 2 nến, Phase D 7 nến — luật vi phạm: L10
- **Thuật toán gắn:** D = 7 nến, E = 2 nến.
- **Đúng phải là:** Phase E là "giá rời range đi tìm vùng giá mới". 2 nến không phải một phase. Đây là dấu hiệu range bị đóng cưỡng bức chứ không phải chu trình hoàn tất.

## Đạt
- Không có mục nào đạt về mặt cấu trúc. Nhãn duy nhất định danh đúng vai là ST[A] (03:44, 4692.4) nằm giữa BCLX và AR — nhưng nó vô nghĩa khi cả range không hợp lệ.

## Cần hỏi người học
- Có nên đặt **sàn tuyệt đối cho tỉ lệ biên phụ / biên chính** (ví dụ biên phụ > 3× biên chính thì huỷ range) không? Người học đã chốt không dùng sàn volume tuyệt đối, nhưng đây là sàn **cấu trúc**, đúng tinh thần "lọc bằng cấu trúc". Bài này biên phụ/biên chính = 4.7×.
