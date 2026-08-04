# Chấm bài #06 — Chưa rõ (BCLX) / DIST? · 2026-04-02 14:43 → 2026-04-02 20:59 (223 nến M1)

**Điểm: 3/10** — vị trí range là chỗ hợp lý nhất trong cả lô (dữ liệu dày, đây là phiên Mỹ thật, biên chính hẹp 0.89%), nhưng **Phase A chưa hoàn thành**: ST[A] chỉ là một nhịp bật 3 nến giữa range, và cây mở range chỉ 2 hợp đồng. Sửa 2 chỗ đó là bài này lên khá.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không test được vùng climax → Phase A chốt sớm — luật vi phạm: L2
- **Thuật toán gắn:** AR = 4720.0 (15:25), `ST[A]` = **4737.6** (15:28) — **cách nhau 3 nến** — rồi Phase A đóng, Phase B chạy 179 nến.
- **Đúng phải là:** ST[A] là "giá quay lại phía climax rồi **bị chặn nhẹ lần nữa**". Climax 4762.2, AR 4720.0, chiều cao 42.2 giá → 4737.6 chỉ hồi được **42%** đường về climax, còn cách mức climax **24.6 giá**. Một nhịp bật 17.6 giá trong 3 nến ngay sau đáy AR là **phần cuối của chính cú AR**, không phải một lần đổi hướng thứ ba. Và điều quan trọng: suốt 179 nến Phase B sau đó giá **chưa bao giờ** lên lại quá 4745 — tức range này **không có ST[A]**. Đúng bài là bỏ ứng viên (Phase A chưa xong, đúng như CHART_CASES Ca #2 nguồn 7.pdf "Thiếu ST[A]") hoặc chờ tới đỉnh hồi cao nhất về sau (~4745 quanh 19:04) mới chốt Phase A.
- **Dấu hiệu quyết định trên chart:** chấm `AR` và chấm `ST[A]` nằm sát nhau theo trục thời gian (hai vạch phase tím cách nhau đúng một khe), và cả hai đều ở nửa dưới khung; đỉnh khung 4762.2 sau Phase A không có nến nào chạm tới nữa.
- **Nghi phạm trong thuật toán:** đúng chỗ v5 vá lỗi D — bỏ mọi ngưỡng %, ST[A] = swing pivot đầu tiên (5 nến không cực trị mới + nhịp ≥ 1.5× biên độ TB). Với biên độ TB nhỏ, nhịp 17.6 giá vượt sàn dễ dàng, nên pivot đầu tiên nào cũng thành ST[A]. **Cùng một lỗi với bài #01.** Người học đã chốt "ST[A] đo bằng cấu trúc, không đo %" — nhưng "cấu trúc" ở đây phải bao gồm điều kiện *đã chạm được vùng climax*, chứ không chỉ là "có pivot"; nếu không thì cấu trúc bị đọc thiếu một lần đổi hướng.

### 2. Cây mở range VSA 0.24× / 2 hợp đồng — vi phạm nặng nhất trong lô về điều kiện climax
- **Thuật toán gắn:** "Climax mở range: BCLX tại 4762.2, **VSA = 0.24×**, biên độ 3.7 giá" (nến 14:43, volume **2**).
- **Đúng phải là:** ngưỡng của chính thuật toán là VSA ≥ 2.2× và biên độ ≥ 1.4× TB — nến này thấp hơn cả khối lượng trung bình 4 lần. Cụm cao trào thật nằm ngay cạnh: **14:37 (20 hợp đồng, VSA 2.99×, biên độ 12.4 giá)**, **14:38 (17, 2.27×)**, **14:44 (22, 2.38×)**. Biên chính trên nên neo theo cụm đó — đỉnh giao dịch thật là **4757.6–4760.4**, không phải 4762.2 (một print 2 hợp đồng cao hơn 1.8–4.6 giá).
- **Dấu hiệu quyết định trên chart:** panel khối lượng — cụm thanh vàng cao nhất của cả ảnh nằm đúng ở 04-02 14:33–14:44; nến mở range là một vạch mảnh nằm trong cụm đó.
- **Nghi phạm trong thuật toán:** giống #03/#04/#05 — mốc **giá** climax dời sang cực trị cụm nhưng không kiểm lại điều kiện climax trên nến đã dời tới. Đây là lỗi lặp 4/6 bài của lô này, vá một chỗ là hết.

### 3. Ba chỉ số Phase B đọc `none` trên Phase B 179 nến — lỗi ĐO
- **Thuật toán gắn:** `SOT phía TRÊN = none (n=0)`, `SOT phía DƯỚI = none (n=0)`, và **không có** dòng "nhịp nỗ lực/kết quả cao nhất".
- **Đúng phải là:** Phase B ở đây có ít nhất 4 nhịp lên–xuống nhìn thấy bằng mắt (4737 → 4704 mSOW → 4740 → 4712 → 4745 → 4712 → 4740). Không dò được **một** nhịp nào trên 179 nến là bộ dò nhịp thrust bị chết, không phải "thị trường không có SOT". Đây là bài chứng minh chỉ số mới chưa đo đúng: nó im lặng ở chính chỗ dữ liệu dày nhất, đầy đủ nhất của cả lô.
- **Nghi phạm trong thuật toán:** ngưỡng nhận một "nhịp thrust" (có lẽ dùng cùng sàn 1.5× biên độ TB / swing 5 nến) quá chặt, hoặc chỉ số được tính trên đoạn Phase B **trước** cú phá đầu tiên nên bị cắt ngắn ở mSOW (16:20). Cần kiểm lại: bài #01 (Phase B 68 nến) cũng đọc `none` cả hai phía.

### 4. Nhãn BCLX lệch 6.2 giá xuống dưới biên chính trên (nhẹ)
- Nhãn `BCLX` tại 4756.0 trong khi biên chính trên là 4762.2. Cùng loại lỗi tách nhãn/mức nhưng ở đây chỉ 6.2 giá nên vẫn đọc được trên chart — ghi nhận để vá chung, không trừ điểm nặng.

### 5. Nhãn `bien phu duoi 4704.8` bị nến đè, chỉ đọc được "4704.8" (trình bày)

## Đạt
- **Điều kiện mở range (L1):** có MOVE tăng thật 95.5 giá / 78 nến, hiệu suất 0.36; climax là cực trị của cả cửa sổ, tức nó đang **chặn** move chứ không nằm giữa move. Chart xác nhận rõ: đợt tăng dốc 4645 → 4762 rồi dừng hẳn.
- **Đây là dữ liệu thật, không phải nhiễu phiên chết** — khối lượng 2–22 hợp đồng/nến, nến có thân, có râu, biên độ vài giá. Khác hẳn bài #01/#02/#03/#05. Range cao **42.2 giá = 0.89%** trên 223 nến: đúng tỉ lệ một vùng cân bằng hẹp, đúng tinh thần THEORY §2.3 ("giá dành thời gian lớn hơn cho khu vực cân bằng").
- **Biên (L3):** biên chính = mức climax 4762.2 + mức AR 4720.0, **giữ cố định** suốt 223 nến dù giá thò ra ngoài — đúng L3, không bị kéo theo giá. Đúng **một** biên phụ dưới 4704.8 = cực trị xa nhất; phía trên không có biên phụ vì giá không lần nào vượt 4762.2 — hợp lệ ("có thể có 2, có 1, hoặc không có").
- **mSOW giữ ở lại Phase B:** cú thọc 4704.8 (sâu 15.2 giá = 36% chiều cao, thân 0.73) phá biên chính rồi thu hẳn về trong range được gọi **mSOW** và ở lại Phase B, không bị nâng thành Shakeout và không mở Phase C. Đúng L5 + đúng Ca #10 nguồn 2.pdf (Failed SOS/SOW vẫn thuộc Phase B). Vá lỗi H chạy đúng.
- **Tên range (L4):** không đặt tên, để **"Chưa rõ (BCLX)"** vì chưa có cú phá thật. Trung thực, đúng L4 — và chart xác nhận là đúng: sau mSOW giá quay vào trong range và dao động 4704–4745 tới hết phiên, không bên nào thắng.
- **Phase B (L9):** 179/223 nến = dài nhất, áp đảo. Bias test biên `+0` (test cả hai biên) — đọc đúng: giá chạm 4745 phía trên và 4704 phía dưới.
- Không có nhãn dư, không spam, không nhãn nào sai vai.

## Cần hỏi người học
- ST[A] "đo bằng cấu trúc, không đo %" — nhưng ở ca này pivot đầu tiên chỉ hồi 42% và range **không bao giờ** test lại climax nữa. Anh muốn xử lý thế nào: (a) bỏ ứng viên vì Phase A không hoàn thành, (b) chờ tiếp và lấy đỉnh hồi cao nhất trong N nến làm ST[A], hay (c) chấp nhận ST[A] yếu nhưng gắn nhãn cảnh báo "ST[A] (yếu)" giống cách đang làm với "AR (yếu)"?
