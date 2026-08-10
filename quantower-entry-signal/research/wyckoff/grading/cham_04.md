# Chấm bài #04 — Phân phối (DIST) · 2026-01-28 23:41 → 2026-01-29 17:05 (183 nến M1)

**Điểm: 5/10** — Cấu trúc đỉnh đọc đúng và tỉ lệ phase đẹp nhất lô, nhưng biên trên neo vào một cây spike 3 lot và nhãn BCLX lệch 100 giá.

## Lỗi (nặng → nhẹ)

### 1. Nhãn BCLX nằm giữa chân move, cách biên trên 100 giá — luật vi phạm: L3
- **Thuật toán gắn:** BCLX tại 23:23, giá **5595.8** (VSA 6.53x) — trước nến mở range 18 phút, thấp hơn biên chính trên (5696.0) **100.2 giá**.
- **Đúng phải là:** nhãn climax phải nằm tại đỉnh 5696 (hoặc range không được mở, xem lỗi 2). Trên ảnh, chấm BCLX nằm **thấp hơn cả biên chính dưới 5560** một chút — nghĩa là "cao trào mua" đang được đánh dấu ở giữa đợt tăng, sai hoàn toàn về vai.
- **Dấu hiệu quyết định trên chart:** chấm đỏ BCLX nằm bên ngoài khung range, dưới đường "bien CHINH duoi 5560.0".
- **Nghi phạm trong thuật toán:** lỗi cụm climax (13.1c, revert). Đây là ca lệch lớn thứ hai trong lô.

### 2. Biên chính TRÊN = một cây spike 3 hợp đồng — luật vi phạm: L1 + L3
- **Thuật toán gắn:** nến mở range 23:41: O 5689 / H **5696** / L 5675.4 / C 5696, **3 lot, VSA 1.13x**.
- **Đúng phải là:** một nến 3 lot nhảy 20.6 giá là **khe thanh khoản** trong phiên đêm, không phải cao trào mua. Đỉnh đấu giá thật (nơi giá thực sự dừng lại nhiều lần) là vùng **5665–5680**, thấy rõ trên ảnh qua cụm đỉnh phẳng suốt Phase B.
- **Hệ quả:** biên chính cao 136.0 giá (2.39%) — gần chạm guard 3.5%, và cả Phase B không lần nào chạm nổi biên trên thật sự (UT[B] 5700 cũng chỉ là một nến VSA 0.19x).
- **Nghi phạm trong thuật toán:** cụm climax dời `climax_price` theo cực trị giá thuần tuý; không có điều kiện "cây được dời tới phải còn thoả tính chất climax".

### 3. UT[B] gán cho một nến 1 lot — luật vi phạm: mục 8 (Effort vs Result) + L3 (biên phụ)
- **Thuật toán gắn:** UT[B] tại 06:06, 5700.0, **VSA 0.19x**, thân 0.00 — và chính nó nới biên phụ trên lên 5700.
- **Đúng phải là:** một cú thăm dò biên trên bằng một hợp đồng lẻ, thân 0, không đáng có tên. Không có nỗ lực thì không có kết quả để đọc; nên bỏ nhãn và **không** nới biên phụ vì nó.
- **Đề nghị:** yêu cầu tối thiểu cho nhãn test biên: VSA ≥ 0.8x **hoặc** thân ≥ 45%.

### 4. Phase E dài 2 nến trong khi giá rơi tiếp 200 giá — luật vi phạm: L10
- **Thuật toán gắn:** E = 2 nến (17:01 → 17:05).
- **Đúng phải là:** sau SOW giá rơi từ 5560 xuống tận **~5230** rồi mới bật — đó mới là Phase E. Cắt ở mốc "2× chiều cao" khiến E gần như không tồn tại.

### 5. (nhỏ) SOW neo tại 5410 — đúng cây mạnh nhất (VSA 3.67x, thân 1.00) nhưng đã cách biên chính 150 giá
- Nhãn hồi tố chọn cây mạnh nhất trong đoạn là đúng chủ trương, nhưng ở đây nó nhảy quá sâu; nến **đóng cửa xuyên biên đầu tiên** mới là mốc đọc được cho người vào lệnh. Cân nhắc vẽ cả hai (mốc phá + cây mạnh nhất).

## Đạt
- Điều kiện mở range: MOVE 418.3 giá / 182 nến / hiệu suất 0.35 — một đợt tăng thật bị chặn, đúng L1.
- Phase A đủ 3 lần đổi hướng; ST[A] 5660.0 = hồi **73.5%** khoảng AR↔climax — không còn rơi lửng giữa range, đúng L2.
- Tỉ lệ phase **tốt nhất lô**: A 34 · B **116** · C **10** · D 22 · E 2 → B dài nhất (L9), C ngắn nhất (L8) — đạt cả hai luật tỉ lệ.
- SOT phía dưới đo được n=4 nhịp rút ngắn, tỷ lệ volume 0.77 (cạn kiệt) — đọc đúng tinh thần mục 8/THEORY §7, và khớp với việc sau đó phe bán thắng.
- Tên **Phân phối**: origin BCLX + phá thật xuống = đúng L4.
- CBR đúng: SOW → LPSY[D] 5417.0 giữ **dưới** biên chính 5560 → giá đi tiếp — đúng L10.
- Chỉ một LPSY[C] và một LPSY[D], không gộp vai — đúng L7, tránh lỗi Ca #3 nguồn 4.pdf.
