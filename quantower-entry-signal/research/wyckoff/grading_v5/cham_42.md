# Chấm bài #42 — Phân phối (DIST) · 2026-07-16 11:48 → 13:22 (94 nến M1)

**Điểm: 1/10** — Không nên vẽ range ở đây. Đây là một đoạn xu hướng giảm bị cắt ngang rồi dán nhãn Wyckoff lên, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Không có vùng đấu giá nào — luật vi phạm: L1 (điều kiện mở range) + THEORY §2.3 "giai đoạn đi ngang"
- **Thuật toán gắn:** một TR 94 nến với đủ Phase A→E.
- **Đúng phải là:** **không vẽ range**. Nhìn ảnh: từ BCLX 4048.4 (11:48) giá đi **một mạch xuống** 3983 (13:02) — 65 giá trong 74 nến, gần như không có một đoạn đi ngang nào. Không có vùng cân bằng thì không có TR.
- **Dấu hiệu quyết định trên chart:** biên chính cao 15.6 giá, nhưng **biên phụ 31.3 giá** — biên phụ gấp **đôi** biên chính. Và giá cuối cùng đi tới 3983, tức **thấp hơn biên chính dưới 50 giá = hơn 3 lần chiều cao range**. Một cấu trúc mà cú phá lớn gấp 3 lần cả cái range thì cái "range" đó chỉ là 15 nến đầu của một cú sụp.
- **Nghi phạm trong thuật toán:** đây đúng là cảnh báo trong đề bài — "một TR M1 chỉ dài 60-100 nến với đủ Phase A→E thì phải nghi ngay đó là nhiễu". Cần một guard: nếu **biên phụ > 1.5× biên chính ngay trong Phase B**, hoặc nếu ST[A] tới SOW chỉ cách nhau vài chục nến, thì huỷ range chứ không đặt tên.

### 2. Climax không đạt ngưỡng và không chặn được gì — luật vi phạm: L1 + mục 3 (1) "VSA ≥ 2.2×"
- **Thuật toán gắn:** BCLX tại 11:48, VSA **1.38×**.
- **Đúng phải là:** 1.38× **dưới hẳn ngưỡng climax 2.2×** trong chính bảng tham số của thuật toán. Cây thật sự có volume là cây **+1 (11:49, VSA 5.10×, 632 lot)** — nhưng đó là cây **giảm** 15 giá, tức là cây bán, không phải cây mua cạn kiệt. Cấu trúc đúng ở đây: cây 11:49 là **cây phá**, không phải "AR".
- **Dấu hiệu quyết định trên chart:** VSA 1.38× ghi thẳng trên tiêu đề ảnh (`climax UP VSA=1.38x`). Một climax dưới ngưỡng lẽ ra không được mở range.
- **Nghi phạm trong thuật toán:** cụm climax dời mốc trong 8 nến đầu (mục 4.0) hình như cho phép mốc dời sang một nến **không** thoả VSA, hoặc ngưỡng 2.2× chỉ kiểm ở nến ứng viên gốc rồi mốc dời làm mất kiểm tra. Phải kiểm lại VSA **sau khi** dời mốc.

### 3. AR (yếu) là cây phá thật bị gọi thành AR — luật vi phạm: L2
- **Thuật toán gắn:** AR (yếu) tại 11:49 — **ngay nến kế** climax, VSA 5.10×, biên độ 15 giá.
- **Đúng phải là:** AR là "sóng mua/bán phản ứng sau climax", phải là một **nhịp** có thời gian. Ở đây nó là **một cây duy nhất, liền kề climax** — chính thuật toán cũng tự dán chữ "(yếu)". Phase A dài **8 nến**: climax nến 1, AR nến 2, ST[A] nến 8. Đó không phải một CHoCH, đó là một cây nến rơi rồi một cây nến hồi.
- **Dấu hiệu quyết định trên chart:** Phase A = 8 nến trong khi range 94 nến. AR cách climax đúng 1 nến.
- **Nghi phạm trong thuật toán:** sàn chống nhiễu "nhịp bật ngược ≥ 1.5× biên độ TB" quá dễ thoả khi chính cây climax làm biên độ TB thấp. Nên yêu cầu AR cách climax **tối thiểu N nến** (đúng như nhãn "(yếu)" đang cảnh báo mà không chặn), hoặc trực tiếp **loại** ứng viên khi AR bị gắn cờ yếu.

### 4. Phase C dài 32 nến ≈ Phase B 34 nến — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A=8, B=34, **C=32**, D=19, E=2.
- **Đúng phải là:** Phase B phải là phase dài nhất và Phase C ngắn nhất. Ở đây B và C gần bằng nhau, và C dài gấp 4 lần A. Đây là hệ quả trực tiếp của lỗi #1: không có cấu trúc thật nên các mốc phase chia bừa.
- **Dấu hiệu quyết định trên chart:** dải phase trên ảnh — vạch tím Phase C ở 12:30 nằm giữa một đoạn giá đang **rơi liên tục**, không phải một cú test.

### 5. LPSY[C] nằm đúng trên biên chính dưới trong lúc giá đang rơi — luật vi phạm: L8
LPSY[C] tại 4034.5 (12:30) là một nhịp hồi giữa cú sụp, không phải "test cuối trước khi cấu trúc sụp" — cấu trúc đã sụp từ 12:16 (mSOW xuống 4017.4, VSA 8.14×). Đúng thứ tự Wyckoff thì cây VSA 8.14× phá 15 giá dưới biên chính **chính là SOW**, không phải "mSOW".

### 6. SOW neo sai cây (lặp lỗi bài #41) — luật vi phạm: mục 5.1 lỗi B
SOW gắn tại 13:02, giá 3983.0 — thấp hơn biên phụ 4017.4 tới **34 giá**. Cây phá thật là cây 12:16 VSA 8.14×.

## Đạt
- MOVE trước climax có hiệu suất 0.71 (cao, đi thẳng) — phép đo MOVE hoạt động đúng, chỉ là nó nghiệm thu một move quá ngắn (16.8 giá / 23 nến).
- Tên range DIST khớp origin BCLX + phá xuống (L4) — đúng về mặt logic đặt tên, dù cả range không đáng vẽ.

## Cần hỏi người học
- Có nên đặt guard cứng: **cú phá đi xa hơn K lần chiều cao biên chính thì range bị hạ cấp / không đặt tên**? Ở bài này K ≈ 3.2. Đây là cách rẻ nhất để chặn kiểu "range 94 nến giữa một cú sụp 65 giá" mà không cần đặt sàn độ dài range (thứ người học đã bác).
