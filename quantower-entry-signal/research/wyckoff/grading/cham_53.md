# Chấm bài #53 — Tái tích luỹ (RE-ACC) · 2026-07-22 12:30 → 15:56 (206 nến M1)

**Điểm: 3/10** — Đây không phải một vùng đấu giá, mà là một nhịp điều chỉnh chữ V trong xu hướng tăng bị nhét đủ 5 phase. Phase B **6 nến** — ngắn nhất trong toàn bộ range — là bằng chứng tự tố.

## Lỗi (nặng → nhẹ)

### 1. Phase B là phase NGẮN NHẤT (6 nến) — luật vi phạm: L9, và L8
- **Thuật toán gắn:** A 32n · **B 6n** · C 23n · D 25n · E 121n.
- **Đúng phải là:** L9 — B là phase dài nhất (giai đoạn xây nguyên nhân, đo cung ↔ cầu). L8 — C là phase ngắn nhất. Ở đây **C dài gấp 4 lần B**. Cả hai luật đều bị đảo.
- **Dấu hiệu quyết định trên chart:** ST[A] 13:01 giá 4124.6 và LPS[C] 13:08 giá 4122.0 — cách nhau **7 nến và 2.6 giá**. Toàn bộ "Phase B" là 6 cây nến trên một đoạn dốc đứng đi lên. Không có một lần đàm phán nào giữa hai biên.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược Phase C. Fix #3 nới lên `0.8 × len(B)` = 0.8 × 6 ≈ 5 nến, nhưng LPS[C] được chọn cách SOS **23 nến** — tức clamp không được áp dụng thật, hoặc áp lên đại lượng khác. Dù áp đúng thì luật vẫn sai hướng: khi B quá ngắn, thứ cần làm là **nghi ngờ range**, không phải nới cửa sổ để moi cho ra Phase C.

### 2. Nhãn BCLX rơi giữa move, trước cả nến mở range 10 nến — luật vi phạm: L1/L3 (nhãn climax phải là mức chặn move)
- **Thuật toán gắn:** BCLX tại **12:20**, giá **4134.9**, VSA 2.80x.
- **Đúng phải là:** climax mở range là 12:30 tại **4139.5** (phiếu ghi rõ), và Phase A cũng bắt đầu 12:30. Nhãn phải nằm tại/sát nến đó.
- **Dấu hiệu quyết định trên chart:** vạch dọc tím Phase A đứng ở 12:30, chấm BCLX đứng **bên trái** vạch đó, thấp hơn đỉnh 4.6 giá, nằm trên thân đoạn dốc đang còn đi lên. Nhãn không rơi vào cửa sổ 12 nến quanh climax mà phiếu in ra (-6..+5) — tức đã trượt hẳn ra ngoài.
- **Nghi phạm trong thuật toán:** fix #4 ("kẹp theo nến mở range cố định") **chưa chạy** cho nhánh này. Cửa sổ quét cụm climax vẫn quét lùi quá xa; phải kẹp cứng `idx_label ∈ [idx_open − k, idx_open + k]` với k nhỏ (≤ 3) và cấm `idx_label < idx_range_start`.

### 3. Không đủ tư cách một range — luật vi phạm: L1 (điều kiện CẦN) + ghi chú "range quá vụn"
- **Thuật toán gắn:** MOVE trước climax 15.6 giá / 47 nến, hiệu suất **0.50** — móm; toàn range 206 nến trong đó E chiếm 121.
- **Đúng phải là:** một range M1 chỉ 85 nến (A+B+C+D) mà đủ Phase A→E thì phải nghi ngay là nhiễu. Hình thật trên chart: giá tăng từ 4118 lên 4139, thụt về 4110, rồi đi thẳng lên 4170. Đó là một nhịp pullback, phần "đi ngang" gần như không tồn tại.
- **Nghi phạm trong thuật toán:** không có sàn nào cho hiệu suất hướng của MOVE, và không có kiểm tra "Phase B có thật sự đi ngang không" (vd yêu cầu B chạm được cả hai biên hoặc dài tối thiểu so với A).

### 4. AR mạnh hơn climax nhiều lần — cảnh báo neo sai vai
- AR VSA **5.03x**, climax VSA 1.79x (nhãn 2.80x). Cú xuống 4110.4 mới là cây nổ khối lượng thật của cấu trúc. Khi "phản ứng tự động" nổ gấp 3 lần "cao trào" thì phải xét lại: có khi cấu trúc thật bắt đầu từ chính cây 4110.4 (một SC của một range khác), không phải từ 4139.5.

## Đạt
- **Mục 4 (L4):** origin BCLX (move tăng bị chặn) + phá thật **lên** → **Tái tích luỹ**. Áp bảng L4 đúng.
- **Mục 7 (L10):** SOS 4145.7 (VSA 4.83x) đóng cửa vượt **biên phụ trên** 4139.8; LPS[D] 4143.2 giữ được ngoài biên; Phase E 121 nến chạy tới ~4170 tìm vùng giá mới. Đoạn D→E là CBR sạch, đúng tinh thần L10.
- **Mục 8:** chú thích er = 0.10 → "nhịp HIỆU QUẢ (kết quả nhiều hơn nỗ lực, không phải hấp thụ)" — **đúng dấu**. Fix #1 chạy đúng.
- **L7:** LPS[C]/LPS[D] mỗi cái 1 điểm.
