# Chấm bài #04 — Phân phối (DIST) · 2026-01-21 06:34 → 2026-01-22 05:50 (127 nến M1)

**Điểm: 6/10** — Bài tốt nhất trong lô. Cấu trúc đọc được: đỉnh sau move tăng 308 giá, phân phối, phá xuống, retest giữ ngoài biên. Phải sửa 2 nhãn (climax neo sai cây, LPSY[C] sai vai) và 1 tỉ lệ phase.

## Lỗi (nặng → nhẹ)

### 1. Climax neo sai cây — BCLX VSA 0,85× trong khi cây thật VSA 13,62× cách đó 3 nến — luật vi phạm: L1 + mục 3(1) tài liệu thuật toán
- **Thuật toán gắn:** BCLX tại 4989,4, nến 06:34, VSA **0,85×**, biên độ **0,0 giá**, volume 2 lot.
- **Đúng phải là:** đọc bảng 12 nến — nến **+3 (06:57)** có volume **111**, **VSA 13,62×**, thân/biên 0,72, và là nến đỏ rơi từ 4961,6 xuống 4954,2. Đó là cây bán tháo thật chặn đợt tăng. Nến **−2 (06:04)** cũng có VSA 4,78×. Cây climax phải là một trong hai, không phải cái tick 2 lot ở 4989,4.
- **Dấu hiệu quyết định trên chart:** thanh volume cao nhất trong toàn bộ vùng Phase A nằm ở panel dưới ngay sau mốc BCLX — cao hơn mọi thanh khác trong range. Chấm BCLX lại ở nến trước đó.
- **Nghi phạm trong thuật toán:** cơ chế "cụm climax" (v5 lỗi A) chọn nến theo **cực trị giá** (High cao nhất) thay vì theo cường độ. Lặp y nguyên ở bài #02, #03, #05 → **lỗi hệ thống của bản v5**, chứ không phải lỗi lẻ. Sửa: chọn cây climax trong cụm theo tích (VSA × biên độ nến), và giữ **giá cực trị** làm mức biên nhưng báo cáo VSA của cây thật.

### 2. LPSY[C] gán sai vai — nó là nhịp hồi SAU mSOW, đúng phải là LPSY[D] hoặc không gán — luật vi phạm: lỗi kinh điển Ca #3 nguồn 4.pdf (gộp nhầm LPSY[C] với LPSY[D]) + L8
- **Thuật toán gắn:** mSOW tại 17:31 (4916,4) → LPSY[C] tại 18:49 (4951,6) → SOW tại 23:17 (4913,0) → LPSY[D] tại 01:21 (4911,9).
- **Đúng phải là:** trật tự này đọc được, nhưng LPSY[C] nằm ở **4951,6 — cao hơn biên chính dưới 4941,5 tới 10,1 giá**, tức nó nằm **trong** range, ở giữa vùng. Một "Last Point of SupplY" phải là đợt phục hồi **yếu, biên hẹp** sau khi đã test biên dưới. Ở đây nó là nhịp hồi mạnh từ 4916,4 lên 4951,6 = **hồi 35,2 giá, tức 74% chiều cao biên chính**. Một nhịp hồi 74% chiều cao range không phải "nguồn cầu cạn kiệt", nó là một cú bật ngược đủ mạnh — đúng hơn nên gọi nó là một **UA/test biên dưới thất bại** và để Phase C bắt đầu muộn hơn, hoặc thừa nhận range này **không có Phase C rõ** (hợp lệ theo THEORY §3.2).
- **Dấu hiệu quyết định trên chart:** chấm LPSY[C] nằm **trên** nét liền "biên CHÍNH dưới 4941,5", còn mSOW và SOW đều nằm quanh nét đứt "biên phụ dưới 4916,4". LPSY[C] là điểm duy nhất trong nhóm này nằm trong range.
- **Nghi phạm trong thuật toán:** nhánh Phase C gán ngược lấy "đỉnh cao nhất trong 60 nến trước cú phá" (mục 6 case KHÓ) mà không kiểm nó có gần biên hay không. Cùng nghi phạm với lỗi #4 bài #03. Cần điều kiện: điểm gán ngược phải nằm trong dải sát biên bị phá.

### 3. Phase B (49 nến) chỉ dài hơn C+D (50 nến) một chút — tỉ lệ phase mỏng — luật vi phạm: L9
- **Thuật toán gắn:** A=18, B=49, C=25, D=25, E=11.
- **Đúng phải là:** B là phase dài nhất — chỗ này ĐẠT (49 > 25). Nhưng B chiếm chỉ 39% range, còn C+D+E chiếm 48%. Trong một cấu trúc phân phối, "xây dựng nguyên nhân" (Phase B) phải chiếm phần lớn thời gian. Với chỉ 49 nến M1 trải 7 giờ lịch, "nguyên nhân" xây được là rất mỏng — theo L Nhân-Quả thì kết quả (đợt giảm sau) cũng chỉ tương ứng.
- **Dấu hiệu quyết định trên chart:** Phase B từ 11:29 tới 18:29 = 7 giờ cho 49 nến, tức ~1 nến/8,5 phút. Dữ liệu thưa, không phải một vùng đấu giá dày.
- **Nghi phạm trong thuật toán:** không phải lỗi logic, là hệ quả của dữ liệu M1 thưa. Ghi nhận để cân nhắc guard mật độ nến.

### 4. Khoảng trống 2 giờ giữa Phase A và Phase B không được xử lý — luật vi phạm: L2 (Phase B bắt đầu ngay sau ST[A])
- **Thuật toán gắn:** Phase A kết thúc 09:31, Phase B bắt đầu **11:29** — hụt gần 2 giờ.
- **Đúng phải là:** Phase B bắt đầu ngay sau ST[A]. Khoảng hụt này là khe dữ liệu (không có nến). Nó không phải lỗi nhãn, nhưng nó cho thấy guard "khe > 4 giờ thì cắt range" (v5 lỗi K) đang để lọt các khe 1-3 giờ liên tiếp, và cộng dồn chúng lại thì range 127 nến này trải **23 giờ lịch**.
- **Dấu hiệu quyết định trên chart:** dải Phase A và dải Phase B trên ảnh có một đoạn hở giữa hai vạch tím.
- **Nghi phạm trong thuật toán:** guard khe chỉ kiểm khe **đơn lẻ**, không kiểm **tổng mật độ**. Đề nghị thêm chỉ số nến/phút cho toàn range.

## Đạt
- **Tên range đúng theo L4:** move tăng 308 giá bị chặn → BCLX; phá thật xuống → Phân phối. Chính xác.
- **Phase A đúng 3 lần đổi hướng (L2):** BCLX 4989,4 → AR 4941,5 → ST[A] 4985,9. ST[A] ở 4985,9 nằm **trong** biên chính, sát mức climax (kém 3,5 giá = 7% chiều cao range) — đây là một cú test lại vùng climax **đúng nghĩa**. So với bài #03 (ST[A] vượt climax 91% chiều cao) thì đây là ca mẫu.
- Phase A kết thúc đúng tại ST[A] — đúng L2.
- **Biên phụ đúng L3:** biên phụ dưới 4916,4 = đúng mức mSOW, cực trị xa nhất; mỗi bên tối đa 1; biên chính không bị kéo theo giá.
- **SOS/SOW đóng cửa bứt qua biên PHỤ (L3):** SOW tại 4913,0 thấp hơn biên phụ 4916,4 — đúng yêu cầu "phải bứt qua biên phụ, không chỉ biên chính". Đây là điểm v4 làm sai và v5 đã vá đúng.
- **mSOW dùng đúng vai (vá lỗi H):** cú thọc xuống 4916,4 lúc 17:31 mạnh nhưng không phá được → gọi mSOW, ở lại Phase B, chỉ nới biên phụ. Đúng như spec. Bản v4 sẽ gọi cái này là "DA test nhẹ" rồi làm hỏng điều kiện xác nhận SOW.
- **Phase D+E là CBR thật (L10):** SOW 23:17 → LPSY[D] 01:21 tại 4911,9 (retest **giữ được** dưới biên) → Phase E 11 nến giá đi tiếp. Đây là lần đầu trong lô thấy CBR đủ hình. Phase E 11 nến, không còn là 1 nến như lỗi J của v4.
- LPSY[C] và LPSY[D] mỗi cái **một điểm** — đúng L7. Và **được tách thành hai vai khác nhau** — đúng bài học Ca #3 nguồn 4.pdf, dù LPSY[C] chọn sai chỗ (lỗi #2).
- Không có nhãn ST[B] — đúng L6.
