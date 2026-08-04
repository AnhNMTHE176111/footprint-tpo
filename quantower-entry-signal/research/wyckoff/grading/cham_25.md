# Chấm bài #25 — Chưa rõ (SC) (ACC?) · 2026-06-04 14:53 → 16:35 (102 nến M1)

**Điểm: 6/10** — Range mở đúng chỗ, biên đúng, nhưng thiếu hẳn Phase C và cú SOS được công nhận quá dễ dãi so với kết quả nó tạo ra. Sửa nhãn, không phải bỏ range.

## Lỗi (nặng → nhẹ)

### 1. Có SOS ở Phase D nhưng KHÔNG có Phase C — luật vi phạm: L8
- **Thuật toán gắn:** dải phase A (35n) → B (42n) → **D (26n)**. Bảng phase không có dòng C.
- **Đúng phải là:** L8 nói rõ case khó — không có Spring/Shakeout/UTAD thì **chờ SOS xuất hiện rồi quay lại vẽ Phase C** từ nhịp test cuối trước cú phá. Ở đây nhịp test cuối là đáy quanh 16:04–16:08 (giá bò lại về vùng 4502–4504 sát biên chính trên sau khi UT[B] hụt) — đó là **LPS[C]**, Phase C phải bắt đầu từ đó và kết thúc tại nến SOS 16:10.
- **Dấu hiệu quyết định trên chart:** SOS đã được chốt (16:10, VSA 3.76x, giá 4510.9) mà timeline nhảy thẳng B → D. Mục 6 của tài liệu thuật toán mô tả có cơ chế gán ngược 60 nến, nhưng ở bài này nó không chạy.
- **Nghi phạm trong thuật toán:** nhánh "Phase C gán ngược" (mục 6, case khó) không được gọi khi range chuyển sang trạng thái `superseded`, hoặc cửa sổ `min(60 nến, 1/2 Phase B)` = 21 nến không tìm được swing pivot đủ 1.5× biên độ TB.

### 2. Cú SOS không đi tới đâu mà vẫn được ghi là phá thật — luật vi phạm: L10, THEORY §5 (mục tiêu tối thiểu của cú phá)
- **Thuật toán gắn:** SOS 4510.9 → LPS[D] 4508.3 → đóng range ở Phase D.
- **Đúng phải là:** biên phụ trên 4505.0, chiều cao range 18.6 giá → đích Phase E là 4523.6. Giá cao nhất sau SOS chỉ ~4514 (đi được ~48%), rồi cuối chart **đóng cửa quay lại đúng 4502.4 = biên chính trên**. Theo L5/L10 đây là một cú phá **không giữ được** — đúng vai của nó là **mSOS**, và range đáng lẽ trả về Phase B chứ không phải sang D.
- **Dấu hiệu quyết định trên chart:** 20 nến cuối ảnh (16:45→17:20) đi xuống liên tục từ 4513 về 4502.4, xuyên qua biên phụ 4505.0 rồi ngồi trên biên chính.
- **Nghi phạm trong thuật toán:** guard "cú phá bị vô hiệu" (lỗi F, mục 7) chỉ kiểm trong **cửa sổ 25 nến** sau SOS. Cú lùi hẳn vào trong biên xảy ra sau cửa sổ đó nên không bị bắt; cộng thêm việc `superseded` đóng range sớm nên không ai đo tiếp.

### 3. ST[A] chỉ hồi 30% chiều cao, chưa phải "test lại vùng climax" — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 15:27 tại 4496.9 (VSA 0.50x, thân 0.08).
- **Đúng phải là:** ST[A] phải là nhịp quay về **phía climax** rồi bị chặn. Từ AR 4502.4 xuống 4496.9 chỉ là 5.5 giá / 29.6% chiều cao 18.6 — cách mức climax 4483.8 tới 13.1 giá. THEORY §5 có cho phép ST nằm 1/3 nửa trên (đọc là "phe mua rất mạnh") nên **không sai hẳn**, nhưng đây là một cây doji thân 0.08 giữa range, chứng cứ mỏng.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm ngay dưới đường biên chính trên, cách xa biên dưới cả chiều cao range.
- **Nghi phạm trong thuật toán:** sàn chống nhiễu AR/ST[A] = 1.5× biên độ TB (mục 4.2) quá thấp trên M1 vàng; không có ràng buộc ST[A] phải về nửa dưới range.

### 4. Chỉ số nỗ lực/kết quả in nhãn ngược nghĩa và lấy nến ngoài Phase B — lỗi ĐO, không phải lỗi nhãn Wyckoff (THEORY §2.2)
- **Thuật toán gắn:** "Nhịp nỗ lực/kết quả cao nhất trong **Phase B**: nến 16:10, effort 2.16x, result 5.81, er=0.37 — vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** (a) nến 16:10 chính là nến **SOS thuộc Phase D**, không thuộc Phase B — cửa sổ đo lấn sang phase sau; (b) er = effort/result = 0.37 nghĩa là **kết quả LỚN hơn nỗ lực** (biên độ 5.81 ATR với volume chỉ 2.16x) — đó là nến phá vỡ trơn trên thanh khoản mỏng, **ngược hẳn** với "nỗ lực nhiều kết quả ít". Theo THEORY §2.2, "nỗ lực lớn kết quả nhỏ" là khi er **CAO**.
- **Dấu hiệu quyết định trên chart:** cả 5 bài trong lô này (25/26/27/28/29) đều in đúng một chuỗi "NGHI VẤN" với er trải từ 0.17 đến 0.72 → nhãn được in **cứng**, không so với ngưỡng nào.
- **Nghi phạm trong thuật toán:** chỗ sinh chuỗi mô tả cho chỉ số er thiếu nhánh `if er > ngưỡng`; và biên phải của cửa sổ quét Phase B lấy mốc SOS thay vì mốc kết Phase B.

## Đạt
- **L1 (mở range):** move giảm 50.6 giá / 68 nến, hiệu suất 0.46, climax là đáy thật của cửa sổ và nến 14:53 chặn đứng move — điều kiện CẦN thoả rõ ràng.
- **L3 (biên):** biên chính = climax 4483.8 + AR 4502.4, cố định suốt range; biên phụ trên 4505.0 đúng là cực trị xa nhất do UT[B] tạo ra, mỗi bên tối đa 1. Không bị kéo theo giá.
- **L6:** không còn nhãn ST[B] rác ở biên trên — cú thọc 4505.0 gọi UT[B], đúng vị trí biên trên.
- **L4 (tên range):** không ép đặt tên 4 mẫu hình khi bị `superseded` — trung thực, đúng cơ chế mới.
- **Chỉ số bias = +1** (chỉ nới được biên trên, không nới biên dưới) khớp đúng với hướng phá lên — chỉ số này **đo đúng bản chất**, giữ lại.
- **SOT dưới = "chớm", n=2, thrust cuối/đầu 0.49, volume 0.96:** đọc được là lực bán ngắn dần mà volume không giảm → cung đang bị hấp thụ ở đáy range. Diễn giải này khớp với việc range phá lên. Đo đúng.
