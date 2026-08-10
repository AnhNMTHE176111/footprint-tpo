# Chấm bài #48 — Phân phối (DIST) · 2026-07-16 11:48 → 12:51 (63 nến M1)

**Điểm: 2/10** — KHÔNG nên vẽ range ở đây. Cả hai biên chính lấy từ **một cây nến duy nhất**, Phase A dài 8 nến, và cái được gọi là range chỉ là một đoạn của đợt giảm 4048 → 3986 bị cắt ngang.

## Lỗi (nặng → nhẹ)

### 1. BCLX và AR nằm trên CÙNG MỘT NẾN — luật vi phạm: L2 (và guard "climax trùng AR" của chính spec)
- **Thuật toán gắn:** BCLX 11:49 tại 4047.8; AR (yếu) 11:49 tại 4032.8. Cùng thời điểm, cùng VSA 5.10x, cùng thân/biên 0.65.
- **Đúng phải là:** L2 đòi **3 lần đổi hướng** để chốt Phase A. Ở đây đỉnh và đáy của một cây nến M1 (O 4047.8 / H 4047.8 / L 4032.8 / C 4038.0, 632 lot) được dùng làm hai biên chính. Đó là 0 lần đổi hướng — không có Phase A, nên không có range.
- **Dấu hiệu quyết định trên chart:** hai nhãn BCLX và AR (yếu) xếp thẳng đứng trên cùng một cột nến; Phase A đo được **8 nến**.
- **Nghi phạm trong thuật toán:** guard "climax trùng AR → bỏ ứng viên" so sánh theo **mốc climax** (nến 11:48) chứ không theo nến sinh ra **mức** climax (nến 11:49, chính là nến AR). Sau khi tách nhãn/mức ở v6, guard này mất hiệu lực. Phải so sánh chỉ số nến của mức climax với chỉ số nến AR, và thêm sàn "AR cách climax ≥ 3 nến".

### 2. Nến mở range không đủ điều kiện climax — luật vi phạm: L1 + mục 3(1) spec (VSA ≥ 2.2x)
- **Thuật toán gắn:** climax mở range = nến 11:48, VSA **1.38x**, biên độ 4.9 giá.
- **Đúng phải là:** 1.38x < ngưỡng 2.2x. Cây thoả ngưỡng là 11:49 (5.10x) — nhưng cây đó là một nến **ĐỎ 15 giá đóng gần đáy**, tức nó vừa là cao trào vừa là cú đạp; nó không "chặn một move rồi để AR bật lên", nó tự đi luôn xuống. Không có climax hợp lệ ở đây.
- **Dấu hiệu quyết định trên chart:** panel volume — cột vàng lớn nằm ở 11:49 và 11:50, không nằm ở nến mở range.
- **Nghi phạm trong thuật toán:** cơ chế "cụm climax dời mốc trong 8 nến" cho phép mức climax và nhãn nhảy sang nến khác, nhưng **không kiểm lại** ngưỡng VSA/biên độ trên nến được chọn làm mốc. Phải hoặc dời hẳn mốc range sang nến climax thật, hoặc bỏ ứng viên.

### 3. SOW đặt muộn 27 nến, cú phá thật bị hạ thành mSOW — luật vi phạm: L5, L10
- **Thuật toán gắn:** mSOW 12:16 tại 4017.4 (VSA **8.14x**, thân 0.54); SOW 12:43 tại 4007.5 (VSA 3.36x).
- **Đúng phải là:** cú 12:16 chính là **SOW thật**. Nó phá biên chính dưới 4032.8, đi tới 4017.4, và sau đó giá **không bao giờ đóng cửa lùi hẳn (>3 giá) trở lại trong range** — nhịp hồi 12:26–12:36 chỉ chạm đúng mép 4032–4033 rồi bị chặn. Nhịp hồi đó là **LPSY[D]** (thiếu hẳn nhãn này trong bài). SOW ở 12:43 chỉ là nhịp tiếp diễn của Phase E.
- **Dấu hiệu quyết định trên chart:** cột volume cao nhất toàn chart là 12:16; nhịp hồi sau đó bị chặn đúng tại đường cam 4032.8 (nhìn thấy rõ hai đỉnh 12:31 và 12:36 dừng ở mép đường).
- **Nghi phạm trong thuật toán:** vòng khoá logic — điều kiện phá thật đòi "3 nến đóng cửa vượt **biên phụ** thêm ≥30 tick", nhưng biên phụ 4017.4 do **chính cây 12:16** tạo ra. Cú phá không thể vượt được biên phụ mà nó tự sinh. Phải so với biên phụ ở trạng thái **trước** cú phá đang xét.

### 4. Range 63 nến mà đủ Phase A→E — luật vi phạm: mục 1 tiêu chí (nhiễu, không phải vùng đấu giá)
- **Thuật toán gắn:** A 8 · B 47 · D 7 · E 2 nến, tổng 63.
- **Đúng phải là:** đây là **một đợt giảm liên tục** 4048 → 3986 (62 giá) trong hơn 1 giờ, bị cắt lấy 15 giá ở đầu để gọi là "range". Nguyên nhân (MOVE trước) chỉ 16.8 giá mà "kết quả" là 62 giá — vi phạm luật Nhân–Quả (THEORY §2.2): nguyên nhân nhỏ không tạo được kết quả gấp 4 lần.
- **Dấu hiệu quyết định trên chart:** từ 11:49 đến 13:00 các nến gần như đơn hướng xuống, không có nhịp đi ngang nào dài quá 10 nến giữa hai biên cam.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range". Nhưng thiếu một guard khác: **Phase A không được ngắn hơn N nến** hoặc **chiều cao biên chính không được nhỏ hơn ½ biên phụ**. Ở đây tỷ lệ biên phụ/chính = 2.01x — nghĩa là phần giá nằm NGOÀI range lớn hơn cả range, dấu hiệu rất rõ rằng biên chính chọn sai.

### 5. Thiếu Phase C — luật vi phạm: L8
Timeline A → B → D → E. Nhánh gán ngược Phase C không kích hoạt (lỗi lặp y hệt bài #46 và #47).

### 6. Phase E dài 2 nến — luật vi phạm: L10 (tàn dư lỗi J)
Phase E = 12:50 → 12:51, trong khi giá sau đó còn đi tiếp tới 3986 (thêm ~20 giá > 1 lần chiều cao range 15.6). Phase E chốt quá sớm nên không mô tả được "giá rời range đi tìm vùng giá mới".

### 7. (trình bày) Nhãn biên chồng nhau không đọc được
Nhãn "biên CHÍNH trên 4048.4" bị nhãn biên phụ trên 4048.7 và nhãn ST[A] đè lên nhau ở góc trên; dòng phụ đề "bias=+0" bị nhãn Phase A cắt ngang. Lỗi trình bày.

## Đạt
- **Mục 1 (một phần):** MOVE trước climax đo đúng — 16.8 giá / 23 nến / **hiệu suất 0.71**, trên ảnh là một đợt tăng thẳng 4026 → 4048. Đây là move thật, không phải đi ngang.
- **Mục 2 (một phần):** ST[A] 11:55 tại 4047.3 — sát mức climax 4048.4, đúng vai "test lại vùng climax", và Phase A kết thúc đúng tại đó.
- **Mục 3 (một phần):** nhãn "AR (yếu)" đã cảnh báo đúng rằng AR rơi vào nến sát climax — máy tự biết mình đang đứng trên nền yếu; chỉ tiếc là cảnh báo này không được nâng thành điều kiện bỏ ứng viên.
- **Mục 4 (tên):** move tăng + phá xuống → Phân phối, đúng bảng L4 về mặt logic đặt tên.
- **Chỉ số:** SOT hai phía đều báo `none(n=0)` — trung thực, đúng: Phase B 47 nến không đủ 3 nhịp để nói về SOT (THEORY §7 đòi ≥3 lần đẩy).

## Cần hỏi người học
- Có nên thêm guard **"AR phải cách mức climax ít nhất 3 nến"**? Bài này AR và mức climax nằm trên cùng một nến M1 mà vẫn qua được mọi guard, và nó là kiểu lỗi sẽ lặp trên mọi cây nến đảo chiều biên độ lớn.
- Chú thích "vùng hấp thụ NGHI VẤN (volume nhiều, kết quả ít)" lại xuất hiện với er=0.27 (effort 1.11x, result 4.09 — tức nỗ lực ít, kết quả nhiều). Cùng lỗi in ngược đã ghi ở bài #46.
