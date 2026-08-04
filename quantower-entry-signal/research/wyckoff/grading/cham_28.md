# Chấm bài #28 — Tái phân phối (RE-DIST) · 2026-06-10 14:58 → 22:03 (365 nến M1)

**Điểm: 5/10** — Cấu trúc lớn đọc đúng và tên range đúng, nhưng cây SC bị dời sang một nến VSA 1.57x (không phải climax), và cả Phase C lẫn LPSY[C] nằm NGOÀI biên chính — hai lỗi neo làm hỏng phần giữa bài.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC neo vào nến KHÔNG phải climax (VSA 1.57x) — luật vi phạm: L1, §3.3 THEORY (SC = volume tăng mạnh + spread mở rộng)
- **Thuật toán gắn:** SC tại 4139.7 lúc 14:58, VSA **1.57x**, biên độ 5.3 giá, thân/biên **0.17**.
- **Đúng phải là:** cao trào bán thật là cụm **14:56 (VSA 3.83x, 969 lot, thân 0.73, rơi 9.4 giá)** và **14:57 (VSA 3.09x, 893 lot, thân 0.85)**. Nến 14:58 chỉ là cây dừng lại sau cao trào — volume đã tụt còn 486, biên độ co lại còn 5.3 giá, thân 0.17. Đó là nến *kết thúc* cao trào, không phải nến cao trào.
- **Dấu hiệu quyết định trên chart:** volume 969 → 893 → **486**; VSA 3.83x → 3.09x → **1.57x**. Panel volume cho thấy hai thanh vàng cao rồi tụt hẳn đúng tại nến được gắn SC. Ngưỡng mở range của chính thuật toán là VSA ≥ 2.2x — nến mang nhãn SC **không đạt ngưỡng đó**.
- **Nghi phạm trong thuật toán:** mục 4.0 "cụm climax" — trong 8 nến đầu, có cực trị mới cùng phía thì **dời mốc climax** sang đó. Luật này chỉ nhìn giá (đáy thấp nhất), không kiểm lại nến đích còn giữ tính chất climax không. Cần thêm điều kiện: chỉ dời mốc nếu nến đích vẫn đạt VSA ≥ 2.2x, hoặc giữ nhãn ở nến climax gốc và chỉ dời **mức giá biên** xuống đáy cụm.

### 2. LPSY[C] ở 4126.6 — nằm DƯỚI biên chính dưới 4139.7 — luật vi phạm: L3 + L8
- **Thuật toán gắn:** LPSY[C] tại 4126.6 lúc 18:57, mở Phase C 26 nến.
- **Đúng phải là:** một LPSY[C] phải là nhịp hồi yếu ở **kháng cự** trước khi cung áp đảo. Điểm này thấp hơn biên chính dưới **13.1 giá** — tức khi thuật toán còn đang gọi Phase C thì giá đã ở hẳn ngoài range rồi. Trên thực tế cú phá đã xảy ra ở **mSOW 18:50 (4120.2, VSA 7.75x, thân 0.88)**; LPSY[C] chỉ là nhịp hồi *sau* cú phá đó, tức nó là **LPSY[D]**, không phải [C].
- **Dấu hiệu quyết định trên chart:** 4139.7 − 4126.6 = **13.1 giá dưới biên**. Trên ảnh, chấm LPSY[C] xanh nằm rõ dưới đường liền cam 4139.7.
- **Nghi phạm trong thuật toán:** mục 6 case KHÓ nhìn ngược 60 nến lấy "đỉnh cao nhất" — không ràng buộc điểm đó phải nằm **trong** range. Cần chặn: điểm gán ngược cho Phase C bắt buộc nằm trong biên chính.

### 3. mSOW 7.75x bị hạ cấp trong khi SOW được gắn cho cây 3.90x sau đó — nhãn sai vai — luật vi phạm: L3 (SOS/SOW mạnh phải bứt biên phụ), CHART_CASES "SOW neo sai cây"
- **Thuật toán gắn:** mSOW 18:50 tại 4120.2 (VSA **7.75x**) rồi SOW 19:23 tại 4107.3 (VSA 3.90x).
- **Đúng phải là:** cây 18:50 là cây phá thật — VSA 7.75x, thân 0.88, đóng cửa xuyên thủng biên chính dưới 19.5 giá. Nó *chính là* cây tạo ra biên phụ 4120.2, nên theo luật "phải bứt qua biên phụ" nó tự loại chính nó. Đây là vòng lặp logic: cây phá mạnh nhất luôn là cây tạo biên phụ, nên không bao giờ được công nhận là SOW.
- **Dấu hiệu quyết định trên chart:** VSA 7.75x là thanh volume cao nhất trong toàn bộ 365 nến của range (nhìn panel volume, thanh vàng tại 18:50). Một cây như thế bị gọi là "minor".
- **Nghi phạm trong thuật toán:** mục 5.0 — biên phụ được nới **bởi chính cú phá đang xét**, rồi mục 5.1 kết cục B lại đòi "đóng cửa vượt **biên phụ**". Phải chốt biên phụ **trước** khi xét cú phá hiện tại, không cho cú phá tự nâng chuẩn của nó.

### 4. Biên phụ dưới 4120.2 rộng gấp đôi biên chính — range làm việc phình 39.5 giá — luật vi phạm: L3 (trình bày/hệ quả)
- **Thuật toán gắn:** biên chính 19.5 giá, biên phụ 39.5 giá.
- **Đúng phải là:** khi phần "ngoài biên" rộng bằng đúng phần "trong biên", đó là dấu hiệu cấu trúc đã vỡ chứ không phải range được nới. Đúng ra range nên đóng tại 18:50.
- **Dấu hiệu quyết định trên chart:** 39.5 ÷ 19.5 = **2.03 lần**.
- **Nghi phạm trong thuật toán:** guard huỷ range (mục 8) chỉ đo **biên chính** (3.5% giá) nên không bao giờ bắt được ca này. Nên thêm guard theo tỉ lệ biên phụ / biên chính.

## Đạt
- Mục 1 phần MOVE (L1): MOVE giảm 53.1 giá / 65 nến / hiệu suất 0.37, có cao trào bán thật (3.83x + 3.09x) chặn move. Điều kiện mở range **đúng** — chỉ sai chỗ neo nhãn.
- Mục 2 (L2): đủ 3 lần đổi hướng; AR 4159.2 là cú bật ngược thật (bật 19.5 giá trong 4 nến); ST[A] 4135.9 quay lại test vùng SC và thủng nhẹ 3.8 giá — đúng vai test lại vùng climax. Phase A chốt tại ST[A], 22 nến.
- Mục 3 phần biên chính (L3): biên chính 4139.7/4159.2 cố định suốt 365 nến, không kéo theo giá. Mỗi bên đúng 1 biên phụ.
- Mục 4 (L4): origin SC + phá xuống thật (giá về 4050) = **Tái phân phối**. Tên đúng, và đây đúng là ca L4 muốn nói — SC không bắt buộc dẫn tới tích luỹ.
- Mục 5 (L9): Phase B **217/365 nến** = phase dài nhất. Đúng tỉ lệ.
- Mục 6 (L8): Phase C 26 nến là phase ngắn nhất (cùng Phase D 25). Đúng tỉ lệ, dù điểm neo sai.
- Mục 7 (L10): sau SOW giá giữ được ngoài biên và chạy tiếp xuống 4050 trong Phase E 76 nến — CBR hoàn chỉnh, hướng đúng.

## Kết luận cấu trúc
Vẽ range ở đây **hợp lý**, hướng đọc đúng. Nếu là tôi: dời nhãn SC về cụm 14:56–14:57 (giữ mức biên 4139.7), gọi cây **18:50 là SOW thật** thay vì mSOW, chuyển LPSY[C] hiện tại thành **LPSY[D]**, và đóng Phase C vào nhịp chạm biên trên cuối cùng quanh 18:1x (giá còn trong range). Range kết thúc sớm hơn, sạch hơn.
