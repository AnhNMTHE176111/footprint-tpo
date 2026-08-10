# Chấm bài #49 — Tái phân phối (RE-DIST) · 2026-07-16 01:24 → 03:49 (145 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây. Một cái khung cao 9.9 giá, không có cao trào thật, Phase B chỉ 22 nến còn Phase E 69 nến, và cú SOW được gắn tên "Tái phân phối" trong khi giá **quay ngược về đúng biên** ngay trong Phase E.

## Lỗi (nặng → nhẹ)

### 1. Phase B là phase NGẮN NHẤT (22 nến) — luật vi phạm: L9
- **Thuật toán gắn:** A 30 · B **22** · D 25 · E 69.
- **Đúng phải là:** Phase B là giai đoạn xây nguyên nhân, phải dài nhất. Ở đây nó ngắn hơn cả Phase A và bằng 1/3 Phase E.
- **Dấu hiệu quyết định trên chart:** trên ảnh, dải "Phase B (22n)" chỉ rộng bằng khoảng 6 phút đồng hồ trục thời gian, kẹp giữa hai vạch tím sát nhau.
- **Nghi phạm trong thuật toán:** không có sàn tối thiểu cho Phase B trước khi cho phép bắn SOS/SOW. Người học đã chốt "không đặt sàn độ dài cho **range**", nhưng đó không có nghĩa cho phép **tỉ lệ phase** đảo ngược. Nên có guard: SOS/SOW bắn khi Phase B < Phase A thì hạ cấp / chờ thêm.

### 2. Thiếu hẳn Phase C — vá #3 KHÔNG cứu được ca này — luật vi phạm: L8
- **Thuật toán gắn:** A → B → D → E, không có C.
- **Đúng phải là:** phải gán ngược LPSY[C] từ SOW.
- **Dấu hiệu quyết định trên chart:** Phase B = 22 nến → cửa sổ gán ngược = min(60, 0.8×22) = **17 nến**. Đúng cái triệu chứng mục 13.1 đã ghi: "cửa sổ vẫn co gần về 0 khi Phase B ngắn". Nới hệ số 0.5→0.8 chỉ đổi 11 nến thành 17 nến — không đủ.
- **Nghi phạm trong thuật toán:** công thức `min(60, k×len(B))`. Cửa sổ gán ngược nên đo từ **mốc bắt đầu Phase B** (tức được phép quét toàn bộ Phase B), có sàn tuyệt đối ~20 nến, thay vì tỉ lệ theo độ dài B.

### 3. Phase E là bằng chứng cú phá THẤT BẠI, không phải giá đi tìm vùng giá mới — luật vi phạm: L10
- **Thuật toán gắn:** Phase E 02:41 → 03:49 (69 nến), range `completed`, tên "Tái phân phối".
- **Đúng phải là:** nhìn ảnh, sau SOW giá xuống đáy ~4030 lúc 02:38 rồi **bò ngược lên suốt 69 nến** và kết thúc Phase E ở đúng **4041** — tức trở lại chạm biên chính dưới 4041.7 / biên phụ 4041.2. Cấu trúc quay về vùng cân bằng cũ = cú SOW bị vô hiệu, range phải đóng ở trạng thái "chưa rõ hướng", không được mang tên Tái phân phối.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nến cuối Phase E nằm ngay trên hai đường ngang cam; cả nửa phải ảnh là một nhịp hồi liên tục hướng lên.
- **Nghi phạm trong thuật toán:** điều kiện chấm dứt Phase E "giá đóng cửa lùi hẳn vào trong biên đã phá" được xử lý như **kết thúc bình thường**, trong khi nó chính là tín hiệu cú phá hỏng. Ba lối thoát của Phase E (lùi vào biên / đi xa 2× / hết 120 nến) phải cho ra **kết luận khác nhau**, hiện đang gộp làm một.

### 4. Climax VSA 1.53× — dưới cả ngưỡng climax của chính thuật toán — luật vi phạm: L1
- **Thuật toán gắn:** SC? tại 4041.7, VSA **1.53×**, biên độ nến 2.7 giá.
- **Đúng phải là:** ngưỡng mở range là biên độ ≥1.4× ATR và VSA ≥2.2×. Cây này không đạt cả hai (biên độ 2.7 giá là nến thường của phiên Á). Nó được miễn trừ vì là range `SINH TU CU PHA`.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS (mục 5.4) cho phép neo range mới **không cần cao trào thật**. Miễn trừ này đang sinh ra hàng loạt range rác trên phiên Á — trong lô này nó sinh ra cả bài #47 lẫn #49, cả hai đều 2/10.

### 5. Range 9.9 giá / 145 nến với đủ A→E = nhiễu, không phải vùng đấu giá
- Chiều cao 0.24% giá, trong khi cú SOW một mình đi 6 giá = 60% chiều cao range. Theo chuẩn đã chốt (TR M1 ngắn mà đủ Phase A→E thì phải nghi là nhiễu), đây đúng là nhiễu phiên Á 01:24–03:49 UTC.

## Đạt
- **Phase A (L2) ĐẠT rất tốt** — đây là điểm sáng duy nhất: ST[A] 01:53 tại **4042.5**, chỉ cách mức climax 4041.7 đúng **0.8 giá**; hồi từ AR bằng **0.92×** khoảng AR↔climax. Đủ đúng 3 lần đổi hướng, và Phase A kết thúc đúng tại ST[A].
- **Biên (L3) ĐẠT:** biên phụ dưới 4041.2 đúng là cực trị xa nhất, mỗi bên 1 cái, tỷ lệ 1.05×.
- Vá #1 chạy đúng: er = 0.16 → ghi "nhịp HIỆU QUẢ, không phải hấp thụ", đúng dấu (không còn hard-code).
- SOW neo đúng cây (VSA 2.76×) và LPSY[D] 02:22 là nhịp retest có thật.
- SOT ghi `none` trung thực thay vì bịa ra chuỗi rút ngắn từ 22 nến dữ liệu.

## Nếu là tôi
Không vẽ range ở đây. Đoạn 01:24–03:49 là phần **đuôi giảm của range #48** (Phân phối 4055–4089) rồi giá tìm đáy quanh 4030 và hồi. Nếu buộc phải vẽ thì range là 4030–4051 (21 giá, bao trọn cả nhịp sụp và nhịp hồi), và kết luận phải là **cú phá bị vô hiệu — chưa rõ hướng**, không phải Tái phân phối hoàn tất.
