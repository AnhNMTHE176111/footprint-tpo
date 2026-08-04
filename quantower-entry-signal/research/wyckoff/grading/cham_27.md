# Chấm bài #27 — Tái tích luỹ (RE-ACC) · 2026-06-05 06:51 → 09:13 (142 nến M1)

**Điểm: 1/10** — Không được vẽ range ở đây. Cây "climax" không chặn được gì cả, cấu trúc thật chỉ dài 21 nến, còn 121 nến còn lại được dán nhãn "Phase E" trong khi đó mới chính là vùng đấu giá thật.

## Lỗi (nặng → nhẹ)

### 1. Climax không chặn move — nó nằm GIỮA move — luật vi phạm: L1
- **Thuật toán gắn:** BCLX mức 4483.2 (nến 06:51, VSA **0.94x**, biên độ 2.0 giá) chặn move tăng 22.1 giá.
- **Đúng phải là:** không mở range. Sau "climax" đó giá đi tiếp lên **4499** và không bao giờ về lại — cây 4483.2 chỉ là chỗ dừng 20 nến giữa một đợt tăng liên tục 4452 → 4499. L1 đòi climax phải là **cực trị chặn move**; ở đây nó bị vượt qua 16 giá = **2.4 lần chiều cao range** (6.8 giá).
- **Dấu hiệu quyết định trên chart:** toàn bộ nửa phải ảnh nằm **trên** đường "biên CHÍNH trên 4483.2", không có một nến nào quay lại dưới nó trong 121 nến.
- **Nghi phạm trong thuật toán:** guard "climax không chặn được move" (mục 4.0, lỗi A) đo bằng "vượt hẳn quá **3× biên độ TB 20 nến**" và chỉ kiểm **trong cửa sổ cụm 8 nến**. Biên độ TB ở phiên Á ~1 giá nên 3× = 3 giá, nhưng giá vượt tới 16 giá — chỉ vì nó vượt **sau** cửa sổ 8 nến nên guard không bắn. Guard phải chạy suốt Phase A/B, không chỉ 8 nến đầu.

### 2. Nến climax có VSA 0.94x — không đủ điều kiện climax mà range vẫn mở — luật vi phạm: mục 3 tài liệu thuật toán (VSA ≥ 2.2x), THEORY §3.3 (SC/BCLX cần volume tăng mạnh)
- **Thuật toán gắn:** mức climax lấy nến 06:51 (VSA 0.94x, biên độ 2.0 giá) nhưng **nhãn** BCLX lại vẽ ở nến 06:46 (VSA 2.73x, giá 4479.5).
- **Đúng phải là:** cơ chế v6 "tách nhãn/mức" là hợp lệ, nhưng ở đây nó tách ra **3.7 giá = 54% chiều cao range**, tức nhãn BCLX nằm **giữa range** trong khi biên trên do một cây volume tầm thường tạo ra. Người đọc chart không thể biết cao trào nằm đâu. Nếu cây thật ở 06:46 thì mốc climax phải là 4479.5 và range phải mở từ đó.
- **Dấu hiệu quyết định trên chart:** nhãn đỏ "BCLX" nằm thấp hơn đường biên chính trên rõ rệt, gần đường biên dưới hơn.
- **Nghi phạm trong thuật toán:** cụm climax dời mốc theo **cực trị giá** trong 8 nến nhưng giữ nhãn ở **cây volume cao nhất** — hai tiêu chí này không bị buộc phải nằm gần nhau. Cần chặn: nếu khoảng cách nhãn ↔ mức > ~25% chiều cao range thì bỏ ứng viên.

### 3. Phase E dài 121 nến, Phase D dài 1 nến, không có Phase C — luật vi phạm: L9, L8, L10, mục 7 lỗi J
- **Thuật toán gắn:** A 11 · B 10 · **D 1** · **E 121**. Không có C.
- **Đúng phải là:** L9 — B dài nhất (ở đây B là 10 nến, ngắn thứ hai); L8 — có SOS thì phải gán ngược Phase C, ở đây không có; L10 — Phase D phải bao trọn nhịp retest, ở đây D = **đúng 1 nến** (chính nến SOS), tức lỗi J của v5 quay lại nguyên vẹn: không có LPS[D], không có retest nào được ghi.
- **Dấu hiệu quyết định trên chart:** hai vạch tím "Phase D (1n)" và "Phase E (121n)" đứng sát nhau; Phase E chạm đúng trần 121 nến = timeout, tức nó không kết thúc vì cấu trúc mà vì hết hạn đếm.
- **Nghi phạm trong thuật toán:** SOS bắn ngay nến 07:12 sau đúng 10 nến Phase B → cửa sổ retest 25 nến không tìm được swing pivot 1.5× biên độ TB nào (giá chạy thẳng), nên Phase D không nở ra được. Cộng với nhánh gán ngược Phase C lại không chạy khi Phase B < 60 nến.

### 4. Cái được gọi "Phase E" mới chính là range thật — luật vi phạm: L1/mục 1 (đây có phải vùng đấu giá thật không)
- **Thuật toán gắn:** 121 nến từ 07:13 đến 09:13 = Phase E "giá đi tìm vùng giá mới".
- **Đúng phải là:** đọc trên ảnh, 121 nến đó **đi ngang trong dải ~4484–4494 suốt 2 giờ** — đó là một vùng cân bằng thật, rộng ~10 giá, đủ dài để đàm phán. Cấu trúc đúng của đoạn này là: move tăng 4452→4499 bị chặn ở 4499, rồi TR ở 4484–4494. Range mà thuật toán vẽ (6.8 giá, nằm **dưới** cả vùng đó) là một mảnh vụn nằm ở chân move.
- **Dấu hiệu quyết định trên chart:** từ 07:13 tới 09:13 giá tạo 4 lần đỉnh quanh 4492–4494 và 4 lần đáy quanh 4485–4487 — hai biên rõ, chạm nhiều lần. Đó là hình của một TR.
- **Nghi phạm trong thuật toán:** mục 13.3 điểm 1 — "vẫn chỉ theo dõi ĐÚNG MỘT range một lúc". Trong lúc range rác này đang chạy Phase E, mọi climax mới đều bị bỏ, nên TR thật không bao giờ được mở.

### 5. Chỉ số nỗ lực/kết quả in nhãn ngược nghĩa (lỗi ĐO — lặp cả 5 bài trong lô)
- **Thuật toán gắn:** nến 07:12, effort 0.93x, result 5.42, er=0.17 → "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** effort 0.93x = volume **dưới trung bình**, result 5.42 ATR = biên độ rất lớn. Đây là "nỗ lực ÍT, kết quả NHIỀU" — theo THEORY §6.3 là breakout trên thị trường **cạn nguồn cung nổi** (hoặc đơn giản là thanh khoản mỏng phiên Á). Gọi nó "volume nhiều kết quả ít" là **ngược hoàn toàn**.
- **Nghi phạm trong thuật toán:** chuỗi mô tả er được in cứng, không có nhánh so ngưỡng — cả 5 bài trong lô này đều in y hệt dù er trải từ 0.17 đến 0.72.

## Đạt
- **L3:** biên chính cố định đúng bằng climax + AR, không kéo theo giá; không dựng biên phụ giả.
- **L4:** origin BCLX + phá lên → Tái tích luỹ, mapping bảng 4 pattern đúng.
- **L2 (hình thức):** đủ 3 lần đổi hướng climax → AR 4476.4 → ST[A] 4482.8, Phase A kết đúng tại ST[A].
- **Chỉ số bias = +1** khớp hướng phá lên. Đo đúng.
- **SOT hai phía = none:** đúng — Phase B 10 nến không thể có 3 nhịp đẩy. Chỉ số đang tố cáo Phase B quá ngắn, hữu ích.
