# Chấm bài #25 — Tái phân phối (RE-DIST) · 2026-06-05 14:06 → 15:05 (59 nến M1)

**Điểm: 1/10** — không được vẽ range ở đây. "Climax" có VSA **0.98×** — dưới trung bình. Cả cấu trúc A→E gói trong 59 nến giữa một đợt giảm đang chạy. Đây là nhiễu bị dán 6 nhãn Wyckoff.

## Lỗi (nặng → nhẹ)

### 1. Climax có VSA 0.98× — thấp hơn trung bình 20 nến, và có tới 3 cây to hơn nó ngay trước đó — luật vi phạm: L1 (climax là điều kiện ĐỦ, phải có volume nổ) + mục 8
- **Thuật toán gắn:** SC tại 14:06, giá 4388.1, **VSA 0.98×**, volume 652.
- **Đúng phải là:** không mở range. Đọc bảng 12 nến: nến −6 (14:00) có volume **1444, VSA 2.58×**; nến −4 (14:02) volume 1194, VSA 1.94×; nến −2 volume 693. Cây được gọi là climax (652) là cây **volume thấp thứ hai** trong cả cụm 12 nến. Đây là định nghĩa ngược của cao trào.
- **Dấu hiệu quyết định trên chart:** tiêu đề chart tự ghi `climax DOWN VSA=0.98x`. Thuật toán tự khai báo mình vi phạm chính ngưỡng 2.2× mà nó đặt ra ở mục 3.
- **Nghi phạm trong thuật toán:** đây là **lỗi A tái phát dưới dạng khác**. Cơ chế "cụm climax" (mục 4.0) cho phép mốc climax **dời** trong 8 nến đầu sang cực trị mới, và khi dời thì **VSA của cây mới không được kiểm lại**. Cây đủ 2.2× là cây 14:00 (2.58×), nhưng đáy sâu nhất lại ở 14:06 → dời mốc sang đó và ngưỡng VSA bị bỏ luôn. Cách sửa giống bài #23: tách **mức** climax (cực trị của cụm) khỏi **cây** climax (cây VSA cao nhất trong cụm), và ngưỡng 2.2× vẫn phải kiểm trên cây, không được mất khi dời mốc.

### 2. Climax không chặn được move — giá đi tiếp 36 giá sau đó — luật vi phạm: L1 (climax phải CHẶN move, không nằm giữa move)
- **Thuật toán gắn:** MOVE 77.6 giá / 106 nến / hiệu suất 0.47 → mở range tại 4388.1.
- **Đúng phải là:** nhìn ảnh — đường xu hướng xám (chân MOVE) đi từ 4500 xuống, cắt xuyên qua toàn bộ khu vực range, và **sau khi range đóng giá tiếp tục xuống 4360**. Move giảm 77.6 giá không bị chặn ở 4388; nó chỉ nghỉ 1 tiếng rồi đi tiếp. Range này là **một cái nghỉ giữa move**, đúng nghĩa "climax nằm giữa move".
- **Dấu hiệu quyết định trên chart:** biên chính chỉ 14.2 giá trong khi move trước 77.6 giá và move sau range còn hơn 30 giá nữa. Vùng nghỉ chiếm 13% một đợt giảm liên tục thì không phải vùng đấu giá.
- **Nghi phạm trong thuật toán:** guard "sau cửa sổ cụm, giá còn vượt mức climax quá 3× biên độ TB → bỏ range" (mục 4.0). Guard này **có** trong spec nhưng ở đây không bắn — giá xuống dưới 4388.1 tới 4371.7 (SOW) = 16.4 giá, chắc chắn hơn 3× biên độ TB của phiên này. **Cần kiểm xem guard chỉ chạy trong cửa sổ 8 nến rồi tắt hẳn hay không** — nếu vậy nó vô dụng với mọi ca phá muộn.

### 3. Biên chính = biên phụ (cùng 14.2 giá) — tức chưa hề có ai cố phá range, nhưng vẫn kết luận SOW xác nhận — luật vi phạm: L3 + L5
- **Thuật toán gắn:** biên chính 4388.1–4402.3; biên phụ **4388.1–4402.3**, y hệt.
- **Đúng phải là:** biên phụ bằng biên chính nghĩa là **suốt Phase B không có nến nào đóng ra ngoài biên**. Theo L3, "SOS/SOW muốn thực sự mạnh phải đóng cửa bứt qua biên PHỤ" — điều kiện này thoả một cách rỗng, vì biên phụ chưa được kiểm nghiệm lần nào. Range chưa từng được test ở bên nào thì chưa đủ "lần chạm" để công nhận cấu trúc (THEORY §9: cấu trúc hợp lệ được xác nhận bởi lần chạm ở 2 khu vực đối lập).
- **Dấu hiệu quyết định trên chart:** Phase B chỉ **14 nến**. Trong 14 nến không thể có "quan hệ nỗ lực ↔ kết quả" nào để đọc.

### 4. SOW gắn lên nến VSA 0.51× — luật vi phạm: mục 8 (Effort vs Result) + WY05
- **Thuật toán gắn:** SOW tại 14:43, 4371.7, VSA **0.51×**, thân 0.58.
- **Đúng phải là:** trên panel volume, cây to nhất cả vùng nằm ở **14:22** (thanh vàng cao vọt, VSA rõ ≥ 2.2×). Nếu có SOW thì nó ở đó. Nhãn 0.51× là nến rỗng. Lỗi B **chưa vá** ở bài này.
- **Nghi phạm trong thuật toán:** cùng nghi phạm ba bài trên — hồi tố nhãn bị giới hạn trong đoạn "đã vượt biên phụ", nên bỏ qua cây nổ volume nằm ngay tại biên.

### 5. Phase E = 1 nến — luật vi phạm: L10 + lỗi J (v4) chưa vá hết
- **Thuật toán gắn:** E = **1 nến** (15:05 → 15:05).
- **Đúng phải là:** Phase E là "giá rời range đi tìm vùng giá mới". Một nến không phải một phase. Lỗi J của v4 ("Phase E luôn dài 1 nến") được ghi là đã vá — bài này chứng minh nó **còn sót đường đi**.
- **Dấu hiệu quyết định trên chart:** đáng nói hơn: LPSY[D] được gán tại **4397.3** — cao hơn SOW 25.6 giá và **nằm hẳn TRONG biên chính**. Tức nhịp "retest" đã lùi vào trong range, theo L10 thì cú phá đã **hỏng**, không được chốt Phase E. Thuật toán vẫn chốt.
- **Nghi phạm trong thuật toán:** điều kiện Câu 1 mục 7 — "một nến đóng cửa lùi hẳn vào trong range quá 30 tick → cú phá hỏng". 4397.3 vào sâu trong range **90 tick**. Điều kiện này rõ ràng **không được kiểm** trước khi chốt E, hoặc chỉ kiểm với biên phụ (trùng biên chính ở đây nên vẫn phải bắn). Đây là lỗi logic đáng soi code trực tiếp.

### 6. Tỉ lệ phase gãy cả hai luật — luật vi phạm: L8 + L9
- A=10, B=**14**, C=13, D=**22**, E=1. Phase B (14) không phải dài nhất — Phase D dài nhất. Phase C (13) gần bằng B (14), không phải ngắn nhất — Phase E (1) mới ngắn nhất. Cả L8 và L9 sai.

## Đạt
- Phase A có đủ 3 lần đổi hướng về mặt hình thức: 4388.1 → AR 4402.3 → ST[A] 4389.4, và ST[A] nằm đúng sát mức climax (lệch 1.3 giá) — đây là ST[A] chọn đẹp nhất trong lô 21–25.
- Phase A kết thúc đúng tại ST[A] (L2 phần này đạt).
- Tên "Tái phân phối" đúng theo L4 nếu đã chấp nhận range: origin SC + phá xuống = RE-DIST. Và cú phá xuống là thật về mặt hướng (giá về 4360).
- Không có nhãn ST[B], không spam nhãn, LPSY[C]/LPSY[D] mỗi cái một điểm (L6, L7 đạt).

## Cần hỏi người học
- Ngưỡng VSA 2.2× có được phép **mất hiệu lực** khi mốc climax dời trong cụm 8 nến không? Nếu không (tôi nghĩ là không), thì bài này đáng lẽ không tồn tại — và cách sửa là kiểm lại VSA sau mỗi lần dời mốc.
