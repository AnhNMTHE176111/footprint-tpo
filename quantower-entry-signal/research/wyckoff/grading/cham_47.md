# Chấm bài #47 — Tái phân phối (RE-DIST) · 2026-07-14 16:07 → 19:55 (228 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây theo cách này. Biên chính chỉ cao 8.9 giá trong khi giá dao động thật 4051–4073 (22 giá): cái khung được vẽ **không bao được vùng đấu giá**, nên mọi nhãn phía sau đều lệch vai.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới KHÔNG phải cực trị xa nhất — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4061.8** (nét đứt), tỷ lệ 1.18×.
- **Đúng phải là:** **4051.3** — đáy của cú mSOW 18:41. Đó mới là "mức cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra".
- **Dấu hiệu quyết định trên chart:** bảng sự kiện ghi mSOW 18:41 giá 4051.3 (VSA **7.78×**, cây volume cao nhất cả chart — cột vàng cao nhất trên panel dưới). Trên ảnh, chấm mSOW nằm thấp hơn nét đứt biên phụ tới hơn 10 giá — nét đứt đứng nguyên tại 4061.8.
- **Nghi phạm trong thuật toán:** đúng cái lỗi "biên phụ tự nới rồi tự vượt" mà v7 tuyên bố đã vá bằng ngưỡng 30 tick. Ở đây triệu chứng ngược lại: cơ chế đóng băng biên phụ trong `C_pending` (mục 5.0, v6) không mở khoá sau khi cú thăm dò kết thúc, nên cú sâu nhất range **không hề** nới biên phụ.

### 2. Có cú rũ rõ ràng nhất chart mà range vẫn KHÔNG có Phase C — luật vi phạm: L8, L5
- **Thuật toán gắn:** mSOW 18:41, Phase = B. Dải phase: A → B → D → E, **không có C**.
- **Đúng phải là:** cú 18:41 phá xuống 4051.3 (sâu hơn cả chiều cao range 8.9 giá), lùng bùng ngoài biên rồi mới bò về trong range khoảng 19:1x — theo L5 đó là **Shakeout** (một SOW thất bại), tức **Phase C**. Phase D bắt đầu ở SOW 19:30.
- **Dấu hiệu quyết định trên chart:** khoảng cách 18:41 → 19:30 chỉ 49 nến, chưa chạm trần timeout 120 nến của Phase C; và đáy 4051.3 vượt xa mọi mức đã có.
- **Nghi phạm trong thuật toán:** điều kiện "cú rũ phải vượt biên phụ" (mục 5.1 câu hỏi 1) bị chính lỗi #1 làm hỏng — biên phụ không được nới thì phép so sánh ở cú sau lấy sai mốc; cộng thêm cửa sổ gán ngược `min(60, 0.8×len(B))` cũng không cứu vì nhánh gán ngược chỉ chạy khi range *chưa từng* có shock pending.

### 3. SOW "thật" nông hơn mSOW "thất bại" trước đó — mâu thuẫn với chính luật của thuật toán
- **Thuật toán gắn:** SOW 19:30 tại **4055.6** (VSA 5.87×), sau khi mSOW 18:41 đã xuống **4051.3**.
- **Đúng phải là:** theo mục 7 (vá lỗi F) "cú phá lần sau phải vượt qua chính cực trị đã thất bại đó mới được tính" — 4055.6 **cao hơn** 4051.3 tới 4.3 giá, lẽ ra không được công nhận là SOW.
- **Dấu hiệu quyết định trên chart:** hai chấm mSOW và SOW trên ảnh, chấm SOW nằm cao hơn hẳn chấm mSOW.
- **Nghi phạm trong thuật toán:** điều kiện "phải vượt cực trị đã thất bại" chỉ áp cho **cú phá bị vô hiệu** (invalidated), không áp cho cú bị **hạ cấp thành mSOW** ở nhánh Phase B. Hai đường về cùng một trạng thái nhưng chỉ một đường mang theo ràng buộc.

### 4. Phase E dài đúng 1 nến, lại rơi vào nến giá hồi về SÁT BIÊN — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 19:55, **1 nến**.
- **Đúng phải là:** Phase E là giai đoạn giá rời range đi tìm vùng giá mới. Ở nến 19:55 giá đang ở ~4062, tức **quay lại đúng mép biên phụ 4061.8 / biên chính 4063.4** — bằng chứng cú phá chưa dứt điểm, chứ không phải "đã đi tìm vùng giá mới".
- **Dấu hiệu quyết định trên chart:** trên ảnh, vạch tím "Phase E (1n)" nằm ngay tại cụm nến xanh bật lên chạm hai đường ngang cam.
- **Nghi phạm trong thuật toán:** lỗi J của v4 (Phase E luôn dài 1 nến) tuyên bố đã vá ở v5 — ở bài này **vẫn còn**. Điều kiện chấm dứt E "giá đóng cửa lùi hẳn vào trong biên đã phá" bắn ngay ở nến đầu tiên, nên E mở và đóng cùng lúc. Nếu E kết thúc vì giá lùi vào biên thì đó là dấu hiệu **cú phá hỏng**, không phải Phase E hợp lệ — phải quay về hạ cấp mSOW, không phải chốt E.

### 5. Range 8.9 giá / 228 nến — khung không bao được vùng đấu giá — luật vi phạm: L1 (range phải là một vùng đấu giá thật)
- **Thuật toán gắn:** biên chính 4063.4–4072.3 = 8.9 giá (0.22%).
- **Đúng phải là:** nhìn ảnh, cả đoạn 16:07–19:55 giá đi trong dải **4051–4073 (~22 giá)**. Biên chính chỉ phủ **40%** dải đó, và giá nằm ngoài biên rất nhiều nến.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS (mục 5.4) — range con neo climax bằng cực trị của cú phá (4063.4) và AR là swing pivot đầu tiên chỉ 9 nến sau (4072.3). Hai mốc quá gần nhau → range sinh ra đã hẹp hơn nhiễu ngay từ lúc chào đời. Cần một sàn: chiều cao range con ≥ ~1× ATR20 × k, hoặc ≥ 0.3× chiều cao range cha.

### 6. Phase B chiếm 186/228 nến còn Phase A chỉ 17 nến — mất cân đối (nhẹ, hệ quả của #5)
- Phase A 17 nến với ST[A] có thân nến 0.04 (nến doji, VSA 1.68×) — ST[A] hợp lệ về vị trí (4064.9, sát climax 4063.4) nhưng chất lượng rất mỏng. Đây là điểm duy nhất Phase A làm đúng tinh thần L2.

## Đạt
- ST[A] 16:23 tại 4064.9 nằm **sát mức climax 4063.4** — đúng vai "test lại vùng climax" (L2), khác hẳn bài #46/#48.
- Vá #1 chạy đúng: er = 0.38 → ghi "nhịp HIỆU QUẢ, không phải hấp thụ", đúng dấu.
- Tên range: origin SC + phá xuống = **Tái phân phối** — khớp L4, và khớp thực tế giá đi tiếp xuống 4054 sau đó.
- SOW neo đúng cây mạnh (VSA 5.87×, thân 0.87), không rơi vào nến xác nhận yếu.
- Không đặt lung tung nhãn ST[B]/UT[B] rác trong Phase B.

## Nếu là tôi
Không vẽ range con này. Đoạn 16:07–19:55 là **Phase B kéo dài của range #46** (vùng phân phối 4076–4112 đang xả xuống), với cú Shakeout 18:41 và cú phá dứt điểm sau đó. Tách nó thành range riêng chỉ tạo ra một cái khung 8.9 giá vô nghĩa và làm mất tên của range cha.
