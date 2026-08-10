# Chấm bài #35 — Tái phân phối (RE-DIST) · 2026-06-10 14:58 → 22:02 (364 nến M1)

**Điểm: 6/10** — cấu trúc lớn đọc đúng và Phase D/E rất thuyết phục; phải sửa nến neo climax, độ dài Phase C và biên phụ trên vô nghĩa.

## Lỗi (nặng → nhẹ)

### 1. Nến neo range không phải nến climax — luật vi phạm: L1
- **Thuật toán gắn:** range mở tại 14:58, "climax SC @4139.7, **VSA=1.57x**"; nhưng dòng dưới lại ghi "nhãn climax mang VSA=3.83x".
- **Đúng phải là:** climax là nến 14:56 (volume 969, VSA **3.83x**, thân/biên 0.73) hoặc 14:57 (893, 3.09x) — đó mới là hai cây chặn đứng move giảm 53.1 giá. Nến 14:58 chỉ có 486 volume và thân/biên 0.17: một nến do dự, không chặn được gì.
- **Dấu hiệu quyết định trên chart:** trên panel volume, hai thanh vàng cao nhất của cụm nằm ngay **trước** vạch mở range; và mức 4139.7 không phải đáy thật của vùng — 21 nến sau, ST[A] xuống 4135.9.
- **Nghi phạm trong thuật toán:** vẫn là nhánh "nhãn climax = cây volume cao nhất trong cụm, không cần trùng cực trị giá" (đã revert, chưa sửa). Hệ quả không chỉ là nhãn lệch mà **biên chính dưới bị đặt sai mức** (4139.7 thay vì ~4135.9-4140.6), kéo theo mọi tính toán phá biên.

### 2. Phase C dài 46 nến, dài hơn cả Phase A và Phase D — luật vi phạm: L8
- **Thuật toán gắn:** A=22n, B=164n, **C=46n**, D=25n, E=108n.
- **Đúng phải là:** C phải là phase ngắn nhất. 46 nến 18:04→18:49 chỉ có duy nhất nhãn LPSY[C] ở nến **đầu tiên** (18:04), rồi 45 nến trôi không nhãn — 45 nến đó thuộc Phase B.
- **Dấu hiệu quyết định trên chart:** vạch tím Phase C và vạch tím Phase D cách nhau gần nửa màn hình, trong khi cả đoạn đó giá chỉ trôi ngang 4134-4150 y hệt Phase B trước đó.
- **Nghi phạm trong thuật toán:** giống bài #34 — Phase C = [LPSY[C] … trước SOW] và LPSY[C] lấy ứng viên đầu tiên. Lấy ứng viên **cuối cùng** trước break sẽ tự động thu gọn Phase C.

### 3. Biên phụ trên chỉ hơn biên chính 5 tick — luật vi phạm: L3
- **Thuật toán gắn:** biên chính trên **4159.2**, biên phụ trên **4159.7**.
- **Đúng phải là:** biên phụ = "mức cực trị xa nhất mà một thế lực đã cố phá range gốc tạo ra". Vượt 0.5 giá là chưa từng có ai cố phá gì — bên trên **không có** biên phụ, chỉ nên vẽ biên chính.
- **Dấu hiệu quyết định trên chart:** hai nhãn "bien CHINH tren 4159.2" và "bien phu tren 4159.7" đè chồng lên nhau, không đọc được — đây vừa là lỗi luật vừa là lỗi trình bày.
- **Nghi phạm trong thuật toán:** khi nới biên phụ không áp đệm tối thiểu. Chỉ tạo/nới biên phụ khi cực trị vượt biên chính ≥ đệm (dùng cùng 30 tick như điều kiện SOS/SOW).

### 4. LPSY[C] ở nửa dưới range trong cấu trúc phân phối — luật vi phạm: L8 (vai trò nhãn)
- **Thuật toán gắn:** LPSY[C] 18:04 @4144.0 (trung điểm range 4149.5).
- **Đúng phải là:** với tái phân phối, tín hiệu Phase C nên là cú hồi thất bại ở **biên trên**, hoặc một UT. Điểm 4144.0 chỉ là một nến trong nhịp trôi xuống — không đọc được vai trò gì.

## Đạt
- Điều kiện mở range (L1) về mặt MOVE: 53.1 giá / 65 nến, bị chặn thật — có vùng đấu giá thật kéo 364 nến, không phải nhiễu.
- ST[A] 15:19 @4135.9 hồi **119%** khoảng AR↔climax, tức xuyên qua mức climax — đúng L2, và tạo biên phụ dưới hợp lệ. Ngưỡng 0.55 hoạt động tốt ở bài này.
- Phase B 164 nến — dài nhất, đúng L9. Đọc effort/result có ích: nhịp 17:28 er=4.79 (volume nhiều, kết quả ít) = vùng hấp thụ nghi vấn, và đúng ~80 nến sau giá vỡ xuống. Đây là ca chỉ số Phase B nói đúng chuyện.
- SOT hai phía đều `chớm` với volume nhịp cuối/đầu 0.22-0.75 (cạn kiệt) — khớp §7 THEORY và khớp kết cục.
- Phase D/E đúng L10: SOW 18:50 @4121.1 với VSA **7.75x** đóng cửa dưới cả biên phụ 4126.6; LPSY[D] 18:53 @4126.6 retest **giữ được ngoài biên**; Phase E 108 nến giá đi thẳng về 4050. Đây là chuỗi CBR sạch nhất trong lô 31-36.
- Tên range đúng L4; biên phụ dưới đúng là cực trị xa nhất, mỗi bên tối đa 1.
