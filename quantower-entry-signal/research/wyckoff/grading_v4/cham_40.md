# Chấm bài #40 — Phân phối (DIST) · 2026-07-14 12:30 → 16:32 (242 nến M1)

**Điểm: 2/10** — Bài sai nặng nhất trong lô. Điều kiện mở range không thoả (80% "độ dài MOVE" nằm trong đúng nến climax — một cú spike tin tức, không phải move xu hướng). Mức climax lấy 1 nến trong khi climax là một cụm 5-6 nến, làm biên chính trên sai 14 giá. AR trượt vì thiếu **1.3 giá** nên bị đẩy muộn 166 nến, khiến Phase A chiếm 198/242 nến và cú UTAD thật bị bỏ trắng nhãn. Nếu là tôi: có vùng đấu giá ở đây, nhưng phải vẽ lại từ Phase A — bản này không dùng được.

## Lỗi (nặng → nhẹ)

### 1. Không đủ điều kiện mở range — "MOVE" là số ảo do cây climax tự tạo ra cho chính nó — luật vi phạm: L1
- **Thuật toán gắn:** mở range tại 12:30, MOVE tăng 78.3 giá / 176 nến / hiệu suất hướng 0.36 (ngưỡng 0.35).
- **Đúng phải là:** không mở range ở đây theo L1. Nến climax 12:30 tự nó đi từ L 4036.0 lên H 4098.4 = **62.4 giá**, tức **80% của "MOVE 78.3 giá" nằm trong đúng 1 nến**. 175 nến trước đó chỉ đi 15.9 giá và trên chart là một đoạn lình xình 4019-4038. Đây chính xác là ca L1 nói phải loại: "Giá đang đi ngang mà xuất hiện nến volume cao thì **không** được mở range."
- **Dấu hiệu quyết định trên chart:** nửa trái chart là một dải nến bé xíu đi ngang dưới 4038, rồi một cây xanh dựng đứng cao bằng cả nửa khung giá (volume 4597 = VSA 14.64x, biên độ 62.4 giá) — đường "chân MOVE" mà máy vẽ nối thẳng từ vùng đi ngang lên đỉnh cây spike.
- **Nghi phạm trong thuật toán:** phép đo MOVE **tính cả nến climax vào độ dài move**. Một cây spike đơn lẻ vì thế tự nâng cả độ dài move (≥8× ATR) lẫn hiệu suất hướng (≥0.35) lên trên ngưỡng. Sửa: đo move tới **mức mở cửa của nến climax** (hoặc tới nến climax−1), rồi mới tính hiệu suất.

### 2. Mức climax lấy đúng 1 nến trong khi climax là một cụm — biên chính trên sai 14.1 giá — luật vi phạm: L3 (biên chính = mức climax) / THEORY §3.5 (Spring/climax có thể là 1 nến hoặc nhiều nến)
- **Thuật toán gắn:** mức climax = H nến 12:30 = 4098.4 → biên chính trên 4098.4.
- **Đúng phải là:** cụm climax kéo 4 nến kế tiếp với khối lượng vẫn khổng lồ: 12:31 H 4104.7 (v 3372), 12:32 H 4110.7 (v 2372), **12:33 H 4112.5 (v 1307)**, 12:35 H 4108.9. Đỉnh của cú climax là **4112.5**, đó phải là biên chính trên.
- **Dấu hiệu quyết định trên chart:** bốn nến ngay sau nến climax nằm **hẳn phía trên** đường "biên chính trên 4098.4" — cái gọi là biên chính bị đâm xuyên ngay từ nến thứ hai của range. Máy phải dùng biên phụ 4112.5 để mô tả chính cú climax của mình.
- **Nghi phạm trong thuật toán:** mở range chỉ nhận **một nến** làm climax (mục 3), không có bước gộp cụm nến climax liền kề khi các nến sau vẫn còn VSA ≥ 2.2x. Với news spike thì cụm mới là climax.

### 3. AR trượt vì thiếu 1.3 giá → Phase A chiếm 198/242 nến — luật vi phạm: L2, L9
- **Thuật toán gắn:** AR tại 15:42 (192 nến sau climax), giá 4073.5; Phase A = 12:30 → 15:47, **198 nến (82% cả range)**; Phase B chỉ 10 nến.
- **Đúng phải là:** AR = cực trị phía đối diện trong cửa sổ 40 nến = **4076.2 lúc 12:56**. Điều kiện "AR phải hồi ≥30% độ dài move" đòi 78.3 × 0.3 = 23.5 giá; cú bật thật cho 4098.4 − 4076.2 = **22.2 giá** — **thiếu đúng 1.3 giá**. Vì 1.3 giá đó, máy bỏ AR thật và chờ thêm 166 nến tới khi vùng cân bằng **đã sụp**.
- **Dấu hiệu quyết định trên chart:** nhãn AR nằm ở mép phải chart, sau khi giá đã rơi từ 4101 xuống 4073; toàn bộ vùng đi ngang 12:35-15:00 (146 nến, dao động 4076.2-4108.9) bị dán là "Phase A". Một Phase A đúng nghĩa (3 lần đổi hướng) không thể chứa 146 nến dao động qua lại.
- **Đúng phải là (cả cấu trúc):** BCLX = cụm 12:30-12:35 (đỉnh 4112.5) · AR = 4076.2 @12:56 · ST[A] = cú test lại vùng climax quanh 13:00-13:30 · **Phase B = 13:30 → 15:03 (~90 nến, phase dài nhất)** · Phase C = đỉnh 4101.3 @15:06 · Phase D = cú rơi 15:06 → 15:42 + retest · Phase E = từ 16:07.
- **Nghi phạm trong thuật toán:** cùng ngưỡng "AR ≥ 30% độ dài move" như bài #39, nhưng ở đây nó độc hơn vì **độ dài move đã bị cây spike làm phồng** (lỗi 1) — 30% của một move phồng gần bằng cả chiều cao vùng cân bằng thật (4076-4100 = 24 giá), nên trong vùng cân bằng đó không tồn tại điểm nào thoả. Hai lỗi cộng hưởng nhau.

### 4. Bỏ trắng UTAD thật — cú test cuối phá đỉnh range ngay trước khi cấu trúc sụp — luật vi phạm: L8 / THEORY §4.1 / Ca #1 nguồn 4.pdf
- **Thuật toán gắn:** không có nhãn nào trong khoảng 15:04-15:06. Nhãn Phase C được gán cho LPSY[C] tại 15:58, giá 4075.0, VSA **0.25x**, thân 0.33.
- **Đúng phải là:** **UTAD tại 15:04-15:06** — nến 15:04 bật từ 4087.4 lên H 4100.9 với volume 930 (**VSA 6.01x**), 15:06 đóng cửa 4101.1 với H 4101.3, tức **vượt biên chính trên 4098.4 rồi sụp thẳng xuống 4065 không hồi lại**. Đây đúng từng chữ định nghĩa UTAD: cú test cuối cùng phá đỉnh range ngay trước khi cấu trúc sụp. LPSY[C] hiện tại (một nến volume 0.25× ở đáy range, sau khi đã sụp) là nhãn vô nghĩa.
- **Dấu hiệu quyết định trên chart:** ngay bên phải khoảng giữa chart có một nến nhọn vọt lên trên đường biên chính trên rồi giá đổ liên tục xuống mép dưới khung — không có nhãn nào ở đỉnh đó.
- **Nghi phạm trong thuật toán:** máy vẫn ở **Phase A chờ AR** lúc 15:04, và cơ chế theo dõi cú phá biên chỉ bật từ Phase B (spec mục 5). Cùng gốc với lỗi #1 của bài #37: mọi sự kiện xảy ra trước khi Phase A chốt đều bị bỏ nhãn.

### 5. Cả 5 nhãn nội bộ range dồn vào 50 nến cuối, sau khi cấu trúc đã sụp — luật vi phạm: L8, L9, L10
- **Thuật toán gắn:** ST[A] 15:47 · DA 15:55 · LPSY[C] 15:58 · SOW 16:07 · LPSY[D] 16:16 — B 10 nến, C 9 nến, D 26 nến.
- **Đúng phải là:** các nhãn này phải phân bố trên cả 242 nến, với Phase B chiếm phần lớn. Ở đây bốn phase B/C/D nén vào 45 nến cuối, trong khi 82% range là "Phase A".
- **Nghi phạm trong thuật toán:** hệ quả cơ học của lỗi 3.

## Đạt
- **Tên range (L4):** origin BCLX + phá xuống thật = Phân phối. Đúng — và đúng cả về bản chất: sau 16:07 giá rời hẳn vùng, đóng dưới 4066.
- **Vùng đấu giá có thật:** khoảng 4076-4112 sau cú spike, 146 nến dao động, hai biên đều được test nhiều lần — có một range đáng vẽ ở đây. Kết luận không phải "đừng vẽ", mà là "vẽ lại từ đầu".
- **LPSY[D] (L7):** một điểm duy nhất tại 16:16, giá 4072.3 — đúng cách vẽ (không vẽ vùng, không lặp).
- **Biên phụ (L3):** mỗi bên đúng 1 (4072.2 dưới từ DA, 4112.5 trên), giữ cái xa nhất. Đúng luật — dù về nội dung 4112.5 lẽ ra phải là biên **chính** (lỗi 2).

## Cần hỏi người học
Với một cây news spike (12:30: biên độ 62.4 giá = 2.5 lần chiều cao vùng cân bằng sau đó, volume 14.6× trung bình), nên xử lý thế nào?
1. **Không mở range** — coi cả cây là gap, chờ vùng cân bằng sau đó tự sinh climax riêng; hoặc
2. **Mở range nhưng gộp cụm** — lấy cả cụm 12:30-12:35 làm một "climax nhiều nến", biên chính trên = 4112.5, và đo MOVE **không tính cụm climax**.

Cách 2 giữ được range (và range này có thật), nhưng cần người học chốt cách gộp cụm: gộp tới khi nào — hết chuỗi VSA ≥ 2.2x, hay hết N nến cố định?
