# Chấm bài #01 — Tích luỹ (ACC) · 2025-12-29 15:22 → 2026-01-05 14:17 (173 nến M1)

**Điểm: 4/10** — Range có lý (SC thật chặn một move 265.6 giá, phá lên thật), nhưng **dải phase sai
gần như hoàn toàn** và range rộng 2.27% thì không còn là vùng cân bằng. Sửa nhãn + vẽ lại phase.

## Lỗi (nặng → nhẹ)

### 1. Dải phase đảo ngược: Phase A dài nhất, Phase B ngắn nhất — luật vi phạm: L9 + L8
- **Thuật toán gắn:** A=73 · B=18+1=19 · C=2+54=56 · D=26 nến.
- **Đúng phải là:** Phase B là phase **dài nhất** (L9), Phase C là phase **ngắn nhất** (L8). Ở đây
  Phase A chiếm 42% range và Phase C dài gấp 3 lần Phase B.
- **Dấu hiệu quyết định trên chart:** Phase C (54 nến) chạy 2025-12-31 06:01 → 2026-01-05 01:04 =
  **4,8 ngày lịch**, bên trong có khe 1520 phút (Tết dương 01-01) và khe **3157 phút** (01-02 18:41 →
  01-04 23:18, cuối tuần). Một Phase C kéo gần 5 ngày thì nó không còn là Phase C.
- **Nghi phạm trong thuật toán:** mọi cửa sổ chờ đếm bằng **SỐ NẾN** (Phase C chờ tối đa 120 nến,
  ST[A] chờ 400 nến) trên dữ liệu **chỉ có nến khi có giao dịch** → dịp lễ 54 nến = 5 ngày. Phải đổi
  sang đếm bằng **thời gian thực** hoặc chặn range bắc qua khe > N phút.

### 2. ST[A] không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] = 4450.2 (2025-12-30 20:07).
- **Đúng phải là:** ST[A] phải quay về **vùng climax** rồi bị chặn lần nữa. 4450.2 nằm **38.8 giá
  trên** SC 4411.4 — tức 39% chiều cao range, giữa range chứ không phải ở biên dưới.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn ST[A] treo lơ lửng giữa hai đường cam, cách hẳn
  đường "bien CHINH duoi 4411.4". Đây đúng là ca giảng viên hay bắt: "một cái ngọ nguậy giữa range".
- **Nghi phạm trong thuật toán:** ngưỡng ST[A] chỉ đòi hồi ≥ **40% chiều cao climax↔AR** — quá lỏng.
  Với range 100 giá thì 40% cho phép ST[A] đứng cách climax 60 giá. Nên đo theo **khoảng cách còn lại
  tới mức climax** (vd ≤ 20-25% chiều cao), không theo phần đã hồi.

### 3. Range 100.3 giá (2.27%) — không phải vùng cân bằng hẹp — luật vi phạm: THEORY §2.3
- **Thuật toán gắn:** biên chính 4411.4 – 4511.7.
- **Đúng phải là:** trung vị 49 range của chính thuật toán là **21.6 giá**; bài này gấp **4.6 lần**,
  và chỉ nằm dưới guard huỷ 3.5% một chút. Với chiều cao đó, "vùng đi ngang" thực chất là cả một
  đoạn dao động lớn — nên hạ khung/tách thành nhiều range con.
- **Nghi phạm trong thuật toán:** guard 3.5% quá rộng (tự đặt, mục 8 tài liệu thuật toán).

### 4. Biên phụ trên là cực trị của chính cây SOS — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4523.6; SOS cũng ở 4523.6.
- **Đúng phải là:** biên phụ = cực trị xa nhất mà một thế lực **đã cố phá và thất bại**. Lấy đỉnh của
  cú phá **thành công** làm biên phụ là vòng tròn logic, và làm điều kiện L3 "SOS phải đóng cửa bứt
  qua biên phụ" thành vô nghĩa.
- **Dấu hiệu quyết định trên chart:** cực trị cao nhất trong khoảng 12-31 06:01 → 01-05 01:04 là
  **4523.6 đúng tại nến SOS** — trước đó không có nến nào lên trên 4511.7. Trên ảnh nét đứt trên đi
  xuyên đúng qua chấm SOS.
- **Nghi phạm trong thuật toán:** biên phụ được "âm thầm nới mỗi nến" (mục 5.0) nên cây SOS tự nới
  biên phụ của nó. Phải **đóng băng biên phụ tại nến trước khi xét cú phá**.

### 5. Effort ↔ result không đọc được vì khối lượng gần bằng 0 — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** climax VSA 3.33x.
- **Đúng phải là:** cả 174 nến trong range chỉ có **374 hợp đồng**, trung vị **1 hợp đồng/nến**; cây
  "climax" có **7 hợp đồng** (7 ÷ TB ~2 = 3.33x). Trên panel khối lượng của ảnh, toàn bộ vùng range
  gần như phẳng — cột vàng chỉ bắt đầu từ 01-02 16:12 trở đi, tức **sau** khi range đã chạy hết.
  VSA là tỷ lệ nên nó nổ ở nơi không có ai giao dịch.
- **Nghi phạm trong thuật toán:** VSA thuần tỷ lệ, **không có sàn khối lượng tuyệt đối**. Cần thêm
  điều kiện `volume ≥ k` (hoặc bỏ qua nến có `vma` dưới ngưỡng) trước khi cho phép mở range.

### 6. Phase B dài 1 nến + 3 dải phase chồng nhãn trong 10 nến — *lỗi trình bày*
- Chuỗi B(18) → C(2) → B(1) → C(54): một "Phase B" một nến không mang nghĩa gì. Trên ảnh 4 hộp nhãn
  phase xếp lên nhau quanh 12-31 03:23, không đọc được. Nên gộp các lần lùi C→B ngắn hơn ~5 nến.

## Đạt
- **L1** — có MOVE thật: 265.6 giá / 64 nến / hiệu suất 0.50; SC 4411.4 đúng là đáy chặn move đó.
- **L4** — SC + phá lên = Tích luỹ, tên đúng; và giá đi tiếp lên **4575.8** (01-06 03:55) nên kết quả
  cũng đúng hướng.
- **L5** — Spring 4383.6 rút vào trong range nhanh, phân loại Spring (không phải Shakeout) hợp lý;
  Spring thất bại 4404.5 trước đó được ghi riêng, đúng tinh thần "B ⇄ C lùi lại được".
- **L7** — Spring / SOS mỗi cái một điểm, không spam.
- **L3 (một nửa)** — biên chính đúng bằng mức SC + mức AR, không bị kéo theo giá; biên phụ dưới
  4383.6 đúng là cực trị xa nhất.

## Cần hỏi người học
- Có nên **chặn hẳn việc mở range trong tuần lễ/Tết** (khối lượng < X hợp đồng/ngày) không? Đây là
  quyết định về **dữ liệu** chứ lý thuyết Wyckoff không phân xử được.
