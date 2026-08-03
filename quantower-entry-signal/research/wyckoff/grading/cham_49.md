# Chấm bài #49 — Chưa rõ (SC) (ACC?) · 2026-07-27 12:19 → 15:56 (217 nến M1, đang chạy)

**Điểm: 2/10** — Không nên để range này ở trạng thái hiện tại. **Phase C dài 121 nến** (dài nhất cả cấu trúc, trái thẳng L8), và có một **lỗi logic thật**: giá ở ngoài biên phụ dưới khoảng 90 nến mà máy không bắn SOW, nên range treo "chưa rõ hướng phá" trong khi trên chart nó đã phá xuống rành rành.

## Lỗi (nặng → nhẹ)

### 1. Giá ở ngoài biên phụ dưới ~90 nến mà không bắn SOW — range bị treo — luật vi phạm: L10, mục 5.1 kết cục B của chính thuật toán
- **Thuật toán gắn:** không có SOS/SOW nào; range vẫn `[active]`, tên vẫn "Chưa rõ (SC)", tô xám; phase cuối là Phase B (24 nến).
- **Đúng phải là:** **Tái phân phối** (L4: origin SC + phá xuống thật), với SOW quanh 13:50.
- **Dấu hiệu quyết định trên chart:** biên phụ dưới là 4077.4. Từ ~13:50 tới ~15:20 giá nằm hẳn dưới mức đó, xuống tận **~4067** (10 giá dưới biên phụ, 17 giá dưới biên chính dưới 4083.9). Chính mục 5.1 của thuật toán nói "ở ngoài quá **40 nến** mà không quay lại → phá THẬT" — điều kiện này đã thoả gấp đôi mà không có nhãn nào.
- **Nghi phạm trong thuật toán:** khi máy đang ở **Phase C** nó chỉ chạy đồng hồ đo cú rũ (tiến độ 50% / hạn 120 nến, mục 6) và **không chạy nhánh theo dõi cú phá biên** của mục 5.1. Suốt 121 nến Phase C, không ai xét SOW. Sửa: nhánh kiểm "ở ngoài biên phụ > 40 nến" phải chạy song song ở **mọi** phase, không chỉ ở Phase B.

### 2. Phase C dài 121 nến — dài nhất cấu trúc — luật vi phạm: L8 (và L9)
- **Thuật toán gắn:** A = 52, B = 21, **C = 121**, rồi lùi về B = 24.
- **Đúng phải là:** L8 — "Phase C là phase NGẮN NHẤT", nó chỉ là tín hiệu đầu tiên cho thấy giá sắp phá biên kia. 121 nến thì nó không còn là Phase C. Kéo theo L9 cũng vỡ: Phase B (21 rồi 24 nến) không phải phase dài nhất.
- **Dấu hiệu quyết định trên chart:** dải "Phase C (121n)" trải từ 13:32 tới 15:32, che gần như toàn bộ nửa sau chart — trong đó có cả cú sụp về 4067 và cả nhịp bò lại lên 4080. Không cách nào đó là một cú rũ đang chờ xác nhận.
- **Nghi phạm trong thuật toán:** hạn chờ Phase C = 120 nến (mục 6) quá dài cho một range chỉ cao 7.2 giá. Hạn này nên tỷ lệ với **độ dài Phase A/B** hoặc chiều cao range, không phải một số cố định.

### 3. Gọi "Shakeout (thất bại)" cho một cú rũ đã ĐẠT mục tiêu tối thiểu — luật vi phạm: L5 + THEORY §9 / WY10-WY12
- **Thuật toán gắn:** Shakeout **(thất bại)** @4077.4 lúc 13:32, vẽ xám.
- **Đúng phải là:** cú rũ này **đã xác nhận**, cái thất bại là **cấu trúc**, không phải cú rũ. WY10 (THEORY §5) nói mục tiêu tối thiểu của một cú rũ là "đi đến đầu **đối diện** của cấu trúc": từ 4077.4 giá bật lên **4091.8** lúc ~13:47, tức vượt cả biên chính trên 4091.1 — đạt **>100%** quãng đường, không phải "chưa đi nổi 50%". Việc sau đó không có SOS chính là **cấu trúc thất bại** theo THEORY §9, và theo §9 đó là bằng chứng **thêm chắc chắn** cho kịch bản ngược lại (phá xuống) — thông tin có giá trị, đang bị nhãn "(thất bại)" màu xám vứt đi.
- **Dấu hiệu quyết định trên chart:** đỉnh cụm nến 13:44–13:47 chạm đúng đường đứt biên phụ trên 4091.8; ngay sau đó là cú đổ về 4067.
- **Nghi phạm trong thuật toán:** mục 6 gộp hai kết cục khác nhau vào cùng một nhãn — (a) cú rũ không đến được biên đối diện, và (b) đến được nhưng 120 nến không ra SOS/SOW. Cần tách thành hai nhãn: "cú rũ thất bại" vs "cấu trúc thất bại".

### 4. LPS[C] gắn lên cây có nỗ lực lớn nhất cấu trúc — sai vai — luật vi phạm: mục 8, THEORY §3.3 (LPS)
- **Thuật toán gắn:** LPS[C] @4077.3 lúc 13:56, **VSA 4.91x**.
- **Đúng phải là:** LPS là "điểm hỗ trợ cuối", đặc trưng là **nguồn cung giảm dần**. Cây này có VSA 4.91x — **cao hơn cả cây climax (4.08x)**, và nó nằm giữa cú đổ từ 4091.8 xuống 4067. Đó là cây **cung** (mSOW / cây phá biên phụ), không phải điểm hỗ trợ.
- **Dấu hiệu quyết định trên chart:** thanh vàng cao nhất cả chart nằm ở 13:47–13:56, đúng chỗ nhãn LPS[C]; và sau nhãn này giá **tiếp tục rơi 10 giá**, không hề được "hỗ trợ".
- **Nghi phạm trong thuật toán:** LPS[C] chỉ được chọn theo **vị trí** (giá quay về test đúng vùng điểm rũ, mục 6) mà **không kiểm volume/hướng nến**. Thêm điều kiện volume co lại là loại được ca này.

### 5. Biên chính 7.2 giá nhưng biên phụ 14.4 giá — range gốc vẽ quá hẹp — luật vi phạm: L3, L2 (AR yếu)
- **Thuật toán gắn:** biên chính 4083.9–4091.1 = 7.2 giá (**0.18% giá**); biên phụ 4077.4–4091.8 = 14.4 giá = **gấp đôi biên chính**.
- **Đúng phải là:** vùng làm việc thật là 14.4 giá, tức "range gốc" đã bị đặt hẹp một nửa. Gốc rễ là AR yếu: AR @4091.1 chỉ cách climax 7.2 giá trên một MOVE dài 23.1 giá = **31%**, vừa đủ lọt ngưỡng 30%. Chiều cao range chỉ bằng **1.5 lần biên độ riêng cây climax** (4.8 giá) — đó không phải một vùng cân bằng, đó là cái hộp do chính cây climax vẽ ra.
- **Dấu hiệu quyết định trên chart:** từ 13:21 trở đi **gần như toàn bộ nến nằm dưới** đường liền cam 4083.9; hai đường biên chính không còn liên quan gì tới hành động giá của 150 nến cuối.
- **Nghi phạm trong thuật toán:** ngưỡng "AR phải hồi ≥ 30% độ dài move" (mục 4.1, và mục 12.4 tự nhận là Claude thêm, chưa quét tham số) quá thấp; ở 31% nó cho ra một range không dùng được. Cũng nên chặn khi **biên phụ ≥ 2 × biên chính** — dấu hiệu range gốc sai.

## Đạt
- L1 thoả về hình: MOVE giảm 23.1 giá / 69 nến, hiệu suất 0.37, thấy rõ trên chart (từ ~4108 lúc 11:11 xuống 4083.9); cây climax là nến đỏ 432 lot (VSA 4.08x) chặn đúng đáy move — không phải nến giữa move.
- L3 phần biên phụ: mỗi bên đúng **1** biên phụ (4077.4 dưới, 4091.8 trên), vẽ nét đứt, đúng luật "giữ cái xa nhất".
- L2 có ST[A] (@4082.7, vượt xuống dưới mức climax nên tạo biên phụ dưới) — Phase A đủ 3 lần đổi hướng.
- L7: LPS[C] một điểm duy nhất.
- Không xoá range khi giá đi ngược origin SC — đúng L4.

## Cần hỏi người học
- Khi cú rũ **đã đến được biên đối diện** (đạt mục tiêu tối thiểu WY10) nhưng sau đó không có SOS/SOW trong hạn chờ, nên gọi nó là gì và **vẽ màu gì**? Theo THEORY §9 đó là "cấu trúc thất bại" và là tín hiệu **mạnh** cho hướng ngược lại — nhưng thuật toán hiện tô xám như một nhãn bỏ đi. Cần chốt: có nên biến ca này thành một sự kiện dương (bias ngược hướng cú rũ) thay vì một nhãn thất bại?
