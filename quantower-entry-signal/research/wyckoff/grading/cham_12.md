# Chấm bài #12 — Tái phân phối (RE-DIST) · 2026-04-26 23:41 → 2026-04-28 08:54 (853 nến M1)

**Điểm: 4/10** — Tên range và Phase B/C/E đúng, nhưng gốc range dựng trên một cây "climax" 3 lot giữa phiên chết, AR trễ 5 tiếng và ST[A] rơi đúng giữa range.

## Lỗi (nặng → nhẹ)

### 1. Climax giả — nến 3 lot, biên độ 0.6 giá, trong vùng thanh khoản chết — luật vi phạm: L1 + THEORY §2.2 (Effort vs Result)
- **Thuật toán gắn:** climax mở range `04-26 23:41 · 4724.5 · VSA 1.94x · biên độ nến **0.6 giá**`, volume = **3**.
- **Đúng phải là:** cả cụm 12 nến quanh climax có volume 1–6 lot và nhiều nến doji volume=1 (23:06, 23:17, 23:27, 23:29, 23:30 đều 1 lot, biên độ 0). VSA "cao" ở đây chỉ là ảo giác do trung bình 20 nến rơi xuống ~1.5 lot trong giờ nghỉ. Một cây 0.6 giá biên độ **không chặn được** một move 39 giá. Không đủ điều kiện mở range.
- **Dấu hiệu quyết định trên chart:** so với bài #09 (SC volume 71, biên độ 22 giá) thì cây này nhỏ hơn 20 lần về khối lượng và 35 lần về biên độ, mà vẫn được coi là climax.
- **Nghi phạm trong thuật toán:** VSA là tỷ lệ thuần với TB20 nến, không có **ngưỡng sàn tuyệt đối** (volume tối thiểu, biên độ tối thiểu theo ATR). Cần gate: `range_nen >= k*ATR` và `volume >= sàn` mới cho phép là climax.

### 2. AR trễ 5 giờ → Phase A 282 nến — luật vi phạm: L2, L3
- **Thuật toán gắn:** `SC 23:40` → `AR 04-27 04:33 · 4780.0`, Phase A = 282 nến.
- **Đúng phải là:** AR là cú bật ngược **đầu tiên** bị chặn. Trên ảnh, ngay sau SC giá bật lên vùng ~4752 (quanh 04-27 00:30–01:00) rồi bị chặn và lùi lại; mức 4780.0 lúc 03:25–04:33 là **đỉnh của đợt sóng thứ hai**, cách climax gần 5 tiếng. Lấy nó làm AR = kéo biên chính trên chạy theo giá. Đây là **lặp lại nguyên lỗi #1 của bài #09** — cùng một nhánh code.
- **Nghi phạm trong thuật toán:** AR lấy cực trị ngược hướng trong cửa sổ dài thay vì swing đầu tiên; cần đóng cửa sổ AR theo số nến hoặc theo lần đảo chiều đầu tiên đủ biên độ.

### 3. ST[A] rơi đúng giữa range — luật vi phạm: L2 (ngưỡng 55% mới vẫn không chặn được)
- **Thuật toán gắn:** `ST[A] 04-27 11:37 · 4749.2`.
- **Đúng phải là:** climax 4724.5, AR 4780.0 → 4749.2 nằm cách climax **24.7 giá trên tổng 55.5 = 44.5% chiều cao range**, tức gần như chính giữa. Nó lọt qua vì hồi được **55.5%** khoảng AR↔climax — sát mép ngưỡng `STA_MIN_AR_FRAC = 0.55`. Đây là bằng chứng ngưỡng đo-từ-phía-AR chưa đủ: phải thêm điều kiện đo **từ phía climax**.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] trên ảnh nằm lơ lửng ở khoảng giữa hai đường biên cam, không chạm vùng nào.

### 4. LPSY[D] sai vai — không phải nhịp hồi retest — luật vi phạm: L10
- **Thuật toán gắn:** `SOW 04-28 05:03 · 4710.9` → `LPSY[D] 05:06 · 4709.6 · VSA 12.38x`.
- **Đúng phải là:** LPSY[D] là **đỉnh của nhịp hồi** về retest biên rồi giữ được ở ngoài. Ở đây LPSY[D] nằm **thấp hơn** SOW 1.3 giá và chỉ cách 3 nến — nó là một cây trong chính đà rơi, không phải cú hồi. VSA 12.38x càng khẳng định đó là cây bán tiếp, không phải nhịp hồi cạn cầu.
- **Nghi phạm trong thuật toán:** điều kiện LPSY[D] không kiểm `price(LPSY[D]) > price(SOW)` (với DIST) và không đòi có ít nhất một swing ngược hướng giữa hai nhãn.

### 5. Nhãn SC nằm trước nến mở range (lỗi cụm climax, đã biết) — ghi nhận
- Range bắt đầu **23:41** nhưng nhãn `SC` gắn ở **23:40 · 4724.7 · VSA 4.14x`. Nhãn đứng ngoài range của chính nó. Không phải trọng tâm vòng này nhưng vẫn là lỗi trình bày + dữ liệu.

### 6. LPSY[C] sát đáy chứ không phải hồi lên kháng cự — nhẹ
- `LPSY[C] 04-28 02:16 · 4728.5` chỉ cao hơn biên chính dưới 4724.5 đúng **4 giá** (7% chiều cao range). "Last Point of **Supply**" phải là nhịp hồi yếu lên gặp cung; một cái nảy 4 giá ngay trên đáy thì đúng về vị trí "gần biên" nhưng mỏng về bằng chứng. Chấp nhận được nhưng nên đòi biên độ hồi tối thiểu.

## Đạt
- **L4:** move giảm 39 giá / 28 nến → SC; phá **xuống** thật → **RE-DIST**. Tên đúng theo bảng 4 pattern.
- **L9/L8:** Phase B 377 nến dài nhất, Phase C 49 nến < B, Phase D 25 nến — trật tự độ dài hợp lý.
- **L3:** biên chính cố định = climax + AR; đúng 1 biên phụ dưới 4715.0 (do mSOW 04-28 02:02) là cực trị xa nhất; tỷ lệ phụ/chính 1.17x.
- **L10 (phần SOW/E):** SOW 4710.9 đóng cửa **dưới cả biên phụ 4715.0** — đúng chuẩn "SOW thật sự mạnh"; Phase E 121 nến giá đi tiếp xuống ~4645, đúng là rời range tìm vùng giá mới.
- **L6:** không còn ST[B]. **L7:** LPSY[C]/LPSY[D] đều đánh 1 điểm.
