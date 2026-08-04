# Chấm bài #33 — Tái phân phối (RE-DIST) · 2026-06-23 00:22 → 03:18 (176 nến M1)

**Điểm: 6/10** — bài tốt nhất trong lô. Cấu trúc và tên range đúng, mSOS/mSOW dùng đúng chỗ; lỗi còn lại là SOW neo sai cây và Phase C bị kéo dài quá vai.

## Lỗi (nặng → nhẹ)

### 1. SOW neo vào nến VSA 0.81× nằm SÂU 17 giá dưới biên — luật vi phạm: mục 8 (Effort vs Result) + lỗi B
- **Thuật toán gắn:** SOW tại 01:49, giá **4168.0**, **VSA 0.81×**, thân 0.64.
- **Đúng phải là:** biên phụ dưới = 4185.5. Cây được gọi SOW nằm ở 4168.0 — tức **thấp hơn biên phụ 17.5 giá**, giá đã rơi xong từ lâu. Cây phá thật phải là cây đóng cửa **bứt qua 4185.5** lần đầu. Đọc panel volume: cụm thanh vàng cao nhất của cả range nằm ở **~01:37** (thanh vàng vọt hẳn lên, cao nhất chart). Đó là cây SOW thật; nó xảy ra **12 phút trước** nhãn hiện tại.
- **Dấu hiệu quyết định trên chart:** VSA 0.81× = khối lượng dưới trung bình. Một cú "Sign of Weakness" mà nỗ lực dưới trung bình thì không thoả định nghĩa gốc SOW ("chênh lệch/khối lượng tăng", THEORY §4.1).
- **Nghi phạm trong thuật toán:** cùng nghi phạm bài #31 — logic hồi tố lỗi B tìm cây VSA cao nhất chỉ trong **đoạn 3 nến xác nhận**, không mở ngược tới nến thò biên đầu tiên. Đây là lỗi tái xuất, cần sửa ở một chỗ duy nhất và sẽ vá được cả 2 bài.

### 2. Phase C dài 22 nến > Phase D 16 nến — luật vi phạm: L8
- **Thuật toán gắn:** A=29, B=36, C=22, D=16, E=74.
- **Đúng phải là:** Phase C phải là phase **ngắn nhất**. Ở đây C dài hơn D. Nguyên nhân trực tiếp: LPSY[C] chốt ở 01:27 nhưng SOW bị neo trễ tới 01:49 (lỗi #1), nên đoạn C phình ra 22 nến. Nếu SOW neo đúng cây ~01:37 thì C còn ~10 nến và trật tự phase tự đúng.
- **Dấu hiệu quyết định trên chart:** khoảng cách LPSY[C] (01:27) → SOW (01:49) = 22 nến, trong khi cú rơi thật đã bắt đầu từ ~01:30 theo hình nến trên ảnh.
- **Nghi phạm trong thuật toán:** hệ quả kéo theo của lỗi #1, không phải lỗi độc lập.

### 3. Phase A 29 nến gần bằng Phase B 36 nến — luật vi phạm: L9
- **Thuật toán gắn:** A=29, B=36. Tỉ lệ B/A = 1.2.
- **Đúng phải là:** Phase B là "giai đoạn dài nhất", nơi diễn ra quan hệ nỗ lực↔kết quả. Dài hơn A đúng 20% thì chưa ra dáng phase dài nhất, dù về mặt thứ tự thì vẫn đúng.
- **Dấu hiệu quyết định trên chart:** AR chốt ở 00:45 = 23 nến sau climax, kéo Phase A dài ra. Nhìn ảnh, cú bật từ SC 4196.0 lên AR 4212.7 là một chân tăng gần như liên tục.
- **Nghi phạm trong thuật toán:** giống bài #31 — AR là swing pivot đầu tiên xác nhận sau 5 nến, nên với một chân tăng dài không có pivot trung gian thì AR bị đẩy xa. Lỗi nhẹ, ghi nhận là xu hướng hệ thống chứ không phải sai nhãn.

### 4. ST[A] có VSA 0.48× nhưng chỉ lùi 5.4 giá / 32% chiều cao — luật vi phạm: L2 + THEORY §5
- **Thuật toán gắn:** ST[A] tại 00:50, giá 4207.3, VSA 0.48×.
- **Đúng phải là:** climax 4196.0, AR 4212.7, chiều cao 16.7. ST[A] ở 4207.3 lùi 5.4 giá từ AR = **32% chiều cao**, còn cách climax 11.3 giá. Đây là test ở **1/3 trên** range — theo THEORY §5 bảng vị trí ST, đó là dấu hiệu "phe mua rất mạnh", chứ chưa phải một cú quay về test vùng climax như L2 yêu cầu.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm sát ngay dưới nhãn AR trên ảnh, cách xa đường "biên CHINH duoi 4196.0".
- **Nghi phạm trong thuật toán:** giống bài #31 — mục 4.2 bỏ hết ngưỡng %, chỉ còn swing-pivot 5 nến. Cần thêm ràng buộc hướng: ST[A] phải nằm ở nửa range phía climax.
- *Điểm giảm nhẹ:* VSA 0.48× (volume co lại khi test) là **đúng** tinh thần ST — "spread/volume thường giảm khi giá quay lại tiệm cận SC". Máy bắt đúng tính chất volume, chỉ sai vị trí.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 17.6 giá / 44 nến / hiệu suất 0.43; climax 00:22 VSA 2.48× là đáy chặn đúng move đó, và 6 nến trước đều VSA thấp (0.19-0.88×) rồi nổ lên 2.48× — đúng dạng một cây chặn move. Mở range hợp lệ.
- **Tên range đúng L4:** origin SC (move giảm) + phá xuống thật = **Tái phân phối**. Đúng bảng 4 pattern; và cú phá này *giữ được* — giá kết thúc ở ~4157, thấp hơn biên phụ dưới 4185.5 gần 30 giá. Đây là Phase D/E thật, khác hẳn #31 và #32.
- **mSOS / mSOW dùng đúng vai (L3 + lỗi H):** mSOS ở 01:00 (4216.0, VSA **5.23×**) — một cú thọc lên rất mạnh nhưng không giữ được, đúng là "cú phá thất bại", và nó nới biên phụ trên lên 4216.0. mSOW ở 01:21 (4188.0) tương tự phía dưới. Đây chính là lỗi H mà v4 gán bừa thành "test nhẹ" — v5 xử lý đúng.
- **Biên phụ đúng L3:** 2 biên phụ, mỗi bên 1 cái (4185.5 dưới / 4216.0 trên), sinh từ chính mSOW/mSOS. Biên chính 4196.0-4212.7 giữ cố định. Chuẩn.
- Phase E 74 nến là đoạn giá thật sự rời range đi tìm vùng giá mới (rơi về 4144-4157). Đúng L10.
- LPSY[C] và LPSY[D] mỗi cái 1 điểm, đúng vai trước/sau SOW. Đúng L7.
- Không có Spring/Shakeout/UTAD nào bị gán bừa — đây là case khó (chỉ có LPSY[C]), máy gán ngược từ SOW, hợp lý theo L8.

## Kết luận cấu trúc
Nếu là tôi: **vẽ đúng như vậy, chỉ dời nhãn SOW về cây volume cao nhất quanh 01:37**. Dời chỗ đó xong thì Phase C co lại và trật tự phase C < D tự đúng luôn. Cấu trúc, tên range, cách dùng mSOS/mSOW và biên phụ đều đọc bài tốt. Đây là mẫu nên dùng để đối chiếu khi sửa các bài khác.
