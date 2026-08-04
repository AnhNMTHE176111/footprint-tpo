# Chấm bài #53 — Chưa rõ (BCLX) (DIST?) · 2026-07-27 00:14 → 15:56 (941 nến M1, đang chạy)

**Điểm: 3/10** — sửa nhãn nặng. Range mở ở chỗ tạm được, nhưng **bỏ sót hẳn một cú SOW đã hoàn tất**: giá đóng cửa dưới biên chính dưới suốt hơn 200 nến và đi xa đúng 1× chiều cao range, thế mà range vẫn để trạng thái "chưa rõ hướng" và chỉ chấm một điểm mSOW. Cộng thêm nhãn BCLX lệch 14.7 giá khỏi đỉnh.

## Lỗi (nặng → nhẹ)

### 1. Bỏ sót SOW → mất cả Phase C/D/E, range đáng ra là PHÂN PHỐI — luật vi phạm: L4, L10, và mục 5.1 "kết cục B" của chính spec
- **Thuật toán gắn:** dải phase chỉ A(25) → B(917); một nhãn `mSOW 14:43 @4067.1`; tên range để "Chưa rõ (BCLX) (DIST?)".
- **Đúng phải là:** **SOW** + Phase D + Phase E, tên range = **Phân phối**. Từ khoảng 12:00 trở đi giá đóng cửa hẳn dưới biên chính dưới 4093.2 và **không hề thu lại vào trong range** cho tới hết dữ liệu (đỉnh hồi cuối chỉ tới ~4084, vẫn dưới 4093.2 gần 9 giá).
- **Dấu hiệu quyết định trên chart:** điều kiện phá thật của spec — "ở ngoài quá **40 nến** và ≥60% số nến đóng ngoài biên" — được thoả thừa: khoảng **230 nến** liên tiếp đóng ngoài biên. Biên độ đi được: 4093.2 → 4067.1 = **26.1 giá = đúng 1.0× chiều cao biên chính**, tức đạt cả đích Phase E.
- **Nghi phạm trong thuật toán:** hai chỗ khả nghi. (a) Đếm "cú phá bị vô hiệu" (v5 lỗi F) có thể đã cộng dồn từ các nhịp thọc trước đó trong 917 nến Phase B rồi khoá luôn nhánh SOS/SOW; (b) điều kiện "3 nến liên tiếp đóng vượt **biên phụ** thêm ≥30 tick" — biên phụ dưới bị chính cú phá này nới ra tới 4067.1, nên cú phá phải vượt qua *chính nó* mới được công nhận. Cần: khi biên phụ do **chính nhịp đang theo dõi** tạo ra thì phải so với biên phụ **trước nhịp đó**, không so với mức vừa cập nhật.

### 2. Nhãn mSOW neo vào nến VSA 0.57× trong khi cây phá thật có volume cao nhất chart — luật vi phạm: lỗi B của vòng chấm v4 (tái phát ở nhánh mSOS/mSOW)
- **Thuật toán gắn:** `mSOW 14:43 @4067.1, VSA 0.57x`.
- **Đúng phải là:** neo hồi tố vào cụm 13:40–14:20 — trên panel volume đây là **các cột vàng cao nhất toàn bộ 941 nến**, đúng hướng, đóng cửa dưới biên.
- **Dấu hiệu quyết định trên chart:** nến mang nhãn có VSA **0.57×** (dưới trung bình) — đúng dạng lỗi mà vòng v4 đã bắt (nhãn rơi vào nến 0.30–0.69× trong khi cây phá thật 4×+).
- **Nghi phạm trong thuật toán:** phép neo hồi tố chỉ áp cho SOS/SOW xác nhận, chưa áp cho nhãn hạ cấp.

### 3. Nhãn BCLX đặt cách đỉnh 14.7 giá và cách mốc climax 14 nến — luật vi phạm: L1/L3 (climax là cây **chặn** move, phải là cực trị)
- **Thuật toán gắn:** mức climax 4119.3 @00:14; **nhãn** BCLX tại **00:00 @4104.6, VSA 6.36×**.
- **Đúng phải là:** nhãn phải nằm ở đỉnh 4119.3, hoặc trong cụm 00:11–00:12 (4116.0–4118.9, VSA 2.90×/2.83×). Cây 00:00 VSA 6.36× thân 0.84 **tăng** là cây ĐẨY giữa move, không phải cây chặn move — gắn BCLX ở đó là mô tả sai cơ chế.
- **Dấu hiệu quyết định trên chart:** 14.7 giá lệch = **56% chiều cao biên chính**; trên ảnh chấm BCLX nằm lửng giữa đoạn tăng, dưới đỉnh hẳn một khoảng lớn. Ngoài ra 00:00 → 00:14 là **14 nến**, vượt cửa sổ cụm climax 8 nến của chính spec → khả năng là bug quét ra ngoài cụm.
- **Nghi phạm trong thuật toán:** hàm chọn "cây volume cao nhất trong cụm" không kẹp chỉ số trong `[climax_idx, climax_idx+8]`, và cho phép quét về quá khứ.

### 4. ST[A] test đúng mức **nhãn** climax chứ không phải mức **biên** climax — luật vi phạm: L2 (ST[A] test lại vùng climax)
- **Thuật toán gắn:** `ST[A] @4104.9`, tức chỉ hồi được **45%** chiều cao range (4093.2–4119.3), cách mức climax 14.4 giá — giữa range.
- **Đúng phải là:** ST[A] phải bị chặn tại vùng 4119.3. Điều đáng nghi: 4104.9 trùng gần khít **nhãn** BCLX 4104.6 (lệch 0.3 giá) → thuật toán đang đo ST[A] theo **giá của nhãn** trong khi biên chính lấy theo **mức cực trị**. Tách nhãn/mức đang bị dùng không nhất quán giữa các nhánh.
- **Dấu hiệu quyết định trên chart:** nến ST[A] VSA **0.22×**, thân 0.74 — quá mỏng để coi là một lần "bị chặn"; sau đó giá còn lên 4113 nhiều lần mà không ai gọi tên.
- **Nghi phạm trong thuật toán:** dùng `climaxLabelPrice` thay vì `climaxLevel` trong điều kiện ST[A] (và có thể cả trần "ST[A] vượt climax ≤ 1.0× chiều cao").

### 5. SOT phía trên báo `none(n=0)` dù đỉnh giảm dần rõ — lỗi ĐO SAI BẢN CHẤT của chỉ số v6
- **Thuật toán gắn:** `SOT-up=none(n=0)`, `SOT-dn=none(n=0)`.
- **Đúng phải là:** chuỗi đỉnh đọc trên ảnh: **4119.3 → ~4113 → ~4110 → ~4107 → ~4104** rồi sụp — đủ ≥3 nhịp rút ngắn theo THEORY §7, đúng khuôn phân phối dốc xuống (§4.3). Đây là chỉ số duy nhất có thể cảnh báo trước cú sụp 26 giá, mà nó im lặng.
- **Nghi phạm trong thuật toán:** giống bài #52 — bộ dò nhịp SOT trả `none` ở 3/4 bài trong lô, ngưỡng xác nhận pivot quá chặt so với nhịp nội bộ range.

### 6. Climax mở range yếu và MOVE ngắn hơn chính chiều cao range nó tạo ra — luật vi phạm: L1 (mức nhẹ)
- **Thuật toán gắn:** MOVE 13.2 giá / 50 nến / hiệu suất 0.54; nến mốc climax 00:14 có **biên độ 1.8 giá, VSA 1.98×**.
- **Đúng phải là:** cây mang mức climax không đạt cả hai ngưỡng mở range (biên độ ≥1.4× ATR, VSA ≥2.2×); nó chỉ là nến cuối của đoạn tăng. Chấp nhận được nếu đọc theo THEORY §6.2 (climax kiệt sức, không cần nổ volume) — nhưng khi đó phải ghi rõ là dạng kiệt sức. Đáng chú ý hơn: MOVE **13.2 giá** nhỏ hơn chiều cao range **26.1 giá** — nguyên nhân bị chặn nhỏ hơn hệ quả, ngược luật Nhân–Quả (THEORY §2.2).
- **Dấu hiệu quyết định trên chart:** phiên Á giờ chết — nến -6 chỉ **37 hợp đồng**; VSA vọt lên vì mẫu số bé, không vì có tay lớn tham gia. Người học đã chốt không dùng sàn lot tuyệt đối nên đây là đánh đổi đã biết, ghi nhận ở mức lỗi nhẹ.

## Đạt
- Phase A đủ **3 lần đổi hướng** (L2 về mặt cấu trúc): climax → AR 4093.2 (đáy nhịp rơi 26 giá, là cú bật ngược thật) → ST[A]; Phase A kết thúc đúng tại ST[A], dài 25 nến.
- Biên chính = climax + AR, **không** bị kéo theo giá suốt 917 nến sau đó (L3) — đây là cải thiện thật so với v4.
- Biên phụ: đúng **một** cái, ở đúng cực trị xa nhất (4067.1); phía trên không có biên phụ vì giá chưa bao giờ vượt 4119.3 — trung thực với L3 ("có thể có 1, có thể không có").
- Phase B là phase dài nhất (L9), tuyệt đối 917/941 nến.
- Bias `+0` đo đúng: giá test cả hai biên trong 15 giờ.
- Trạng thái `active` / "(đang chạy)" đúng vì dữ liệu dừng ở 27/07 15:56.
