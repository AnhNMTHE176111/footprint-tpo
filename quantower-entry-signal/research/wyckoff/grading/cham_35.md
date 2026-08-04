# Chấm bài #35 — Phân phối (DIST) · 2026-06-21 23:10 → 2026-06-22 00:11 (61 nến M1)

**Điểm: 2/10** — không nên vẽ range ở đây: 61 nến, biên chính 11.1 giá (0.27%), Phase B ngắn hơn cả Phase A, thiếu hẳn Phase C, và "Phân phối" bị chính giá phủ định ngay sau khi range đóng.

## Lỗi (nặng → nhẹ)

### 1. Phase B là phase NGẮN NHẤT của cấu trúc — luật vi phạm: L9 (và L2)
- **Thuật toán gắn:** A = 15 nến · **B = 10 nến** · D = 18 nến · E = 19 nến.
- **Đúng phải là:** Phase B phải là phase dài nhất — đây là chỗ xây "nguyên nhân". B = 10 nến thì không có nguyên nhân nào được xây; 10 nến M1 ở phiên Á là một cái ngọ nguậy, không phải một giai đoạn đấu giá.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu, bảng Phase: B (23:25→23:34) đúng 10 nến, ngắn hơn A, D và E. Trên ảnh, dải "Phase B (10n)" hẹp bằng khoảng 1/2 dải Phase A.
- **Nghi phạm trong thuật toán:** không có luật kiểm tỉ lệ phase sau khi range hoàn tất. Phase A chốt tại ST[A] "swing pivot đầu tiên" nên A phình ra, còn B bị nuốt vì cú phá xuống đến quá nhanh. Nên có guard: `len(B) < len(A)` → range chưa chín, không đóng, hoặc bỏ.

### 2. Thiếu hoàn toàn Phase C — luật vi phạm: L8, mục 6 "case khó" của spec
- **Thuật toán gắn:** timeline A → B → **D** → E, nhảy hẳn qua C.
- **Đúng phải là:** SOW bắn ra ở 23:35 mà range chưa từng có Phase C thì phải nhìn ngược ≤60 nến, lấy nhịp test cuối (đỉnh cao nhất trước cú rơi) làm **LPSY[C]** và mở Phase C từ đó. Trên ảnh, nhịp đỉnh 23:27–23:30 quanh 4176–4177 (ngay trước khi giá xuyên biên dưới) chính là LPSY[C].
- **Dấu hiệu quyết định trên chart:** Phase B kết thúc 23:34, SOW tại 23:35 — không có một nến nào được gán cho Phase C. Bảng sự kiện chỉ có 5 nhãn: BCLX, AR, ST[A], SOW, LPSY[D].
- **Nghi phạm trong thuật toán:** nhánh gán ngược Phase C (spec mục 6, cửa sổ 60 nến) không chạy. Lỗi này lặp ở 4/5 bài lô này (#35, #36, #37, #39) — nghi vá v6 "xoá LPS[C] mồ côi" hoặc "Phase C kẹp trong range" đang xoá luôn cả LPSY[C] gán ngược hợp lệ.

### 3. Chân MOVE là râu nến mở phiên Chủ nhật, MOVE thực chất là đi ngang — luật vi phạm: L1
- **Thuật toán gắn:** MOVE tăng 24.6 giá, 70 nến, hiệu suất 0.39 → coi là "MOVE xu hướng rõ ràng".
- **Đúng phải là:** đo lại chân MOVE bỏ nến mở phiên. 70 nến trước climax rơi đúng vào 06-21 22:00 — nến khai phiên sau khe cuối tuần 53 giờ, có râu thọc xuống ~4157 kèm cột volume vàng cao nhất vùng, trong khi giá xung quanh nằm 4165–4175. Trừ râu đó ra, 50/70 nến của "MOVE" là đi ngang 4165–4175, chỉ 10 nến cuối mới bò lên 4181.5.
- **Dấu hiệu quyết định trên chart:** trục thời gian nhảy từ `06-19 16:51` sang `06-21 22:07` — khe cuối tuần; cây spike + thanh volume vàng ngay tại mép khe. Hiệu suất 0.39 chỉ vượt ngưỡng 0.35 nhờ chính cái râu đó.
- **Nghi phạm trong thuật toán:** cửa sổ MOVE 240 nến (mục 3.2) đo bằng `low/high` và **không loại nến khai phiên/nến sát khe thời gian**. Luật khe > 4 giờ (lỗi K) chỉ áp cho range đang chạy, chưa áp cho đoạn đo MOVE. Sửa: đo chân MOVE bằng close, và cắt cửa sổ MOVE tại khe > 4 giờ giống như cắt range.

### 4. ST[A] rơi giữa range, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 23:24, giá 4175.7.
- **Đúng phải là:** ST[A] phải quay về **phía climax và bị chặn lần nữa tại vùng climax**. 4175.7 nằm ở (4175.7−4170.4)/11.1 = **48% chiều cao range** — đúng giữa. Đó là một nhịp nhấp nhô, không phải cú test lại 4181.5.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn ST[A] nằm lửng giữa hai đường cam, cách biên trên gần 6 giá — bằng nửa cả range.
- **Nghi phạm trong thuật toán:** mục 4.2 đã bỏ hết ngưỡng %, chỉ còn "swing pivot 5 nến + sàn 1.5× biên độ TB" → luôn bắt nhịp lùi **đầu tiên** sau AR. Lỗi này lặp ở 4/5 bài (48% · 68% · 62% · 43%). Cần thêm điều kiện tiệm cận: nhịp hồi phải vào được 1/3 gần climax, chưa đạt thì Phase A chưa xong và chờ nhịp sau.

### 5. Nhãn BCLX đặt ngoài range, không ở cực trị chặn move — luật vi phạm: L1 (điều kiện climax chặn move)
- **Thuật toán gắn:** nhãn BCLX tại 23:04, giá 4176.9, VSA 4.48x; còn **mức** biên chính trên = 4181.5 tại nến 23:10.
- **Đúng phải là:** cây chặn move là nến 23:10 (đỉnh 4181.5, VSA 2.69x). Nến 23:04 nằm **giữa** move — sau nó giá còn đi thêm 4.6 giá. Cơ chế tách nhãn/mức là hợp lệ theo v6, nhưng hệ quả ở đây là nhãn climax nằm **trước mốc bắt đầu range 6 nến** và ở ngoài khung chữ nhật (thấy rõ trên ảnh).
- **Nghi phạm trong thuật toán:** "cây volume cao nhất trong cụm" không bị ràng buộc phải là cây tạo cực trị, cũng không bị kẹp trong `[bắt đầu range, +8 nến]`. Tối thiểu nên kẹp nhãn vào trong range.

### 6. Range 61 nến / 11.1 giá — nhiễu, không phải vùng đấu giá; và cấu trúc bị phủ định ngay — L1, THEORY §9
- **Dấu hiệu quyết định trên chart:** SOW đi được 11.1 giá (đúng 1× chiều cao) rồi range đóng lúc 00:11; ngay sau đó giá bật thẳng từ 4156 lên **4213** — vượt hẳn biên trên của "vùng phân phối" 32 giá. Theo THEORY §9 đây là cấu trúc thất bại, chuyện xảy ra thật là tăng, không phải phân phối.
- **Ghi rõ:** luật hiện hành cho phép đóng range khi đi đủ 1× chiều cao, nên đây không phải lỗi code trực tiếp — nhưng nó là bằng chứng số cho việc range có chiều cao 0.27% giá thì mọi mốc đo đều bé tới mức vô nghĩa.

### 7. Chú giải nhịp nỗ lực/kết quả in cứng, không phân loại — lỗi trình bày chỉ số (v6)
- **Thuật toán gắn:** er = 0.13 → in "vung hap thu NGHI VAN (volume nhieu, ket qua it)".
- **Đúng phải là:** ở bài này effort = 0.87x mà result = 6.84 → **ít nỗ lực, kết quả rất lớn**, tức nghèo cung/nghèo cầu chứ không phải hấp thụ. Câu chú giải là một chuỗi cố định, in y hệt ở cả 5 bài lô này với er từ 0.13 tới 0.94 → không mang thông tin.
- **Nghi phạm trong thuật toán:** chuỗi mô tả hardcode, thiếu ngưỡng phân loại theo er (và thiếu định nghĩa er theo hướng nào là "nỗ lực nhiều kết quả ít").

## Đạt
- Tên range đúng theo L4: origin BCLX + phá xuống thật = Phân phối.
- SOW neo đúng cây phá thật: 23:35, VSA 2.92x, thân 0.75 — không còn rơi vào nến xác nhận thứ 3 như v4/v5.
- SOW đóng cửa vượt biên phụ dưới (4159.8 < 4170.3) → thoả L3.
- Phase D có LPSY[D] một điểm duy nhất (L7), giữ được ngoài biên → đúng khung CBR của L10.
- Biên chính = climax + AR, không bị kéo theo giá về sau (L3).
- Bias = −1 khớp chart: trong range giá chỉ với tới biên dưới, không chạm nổi biên trên.

## Cần hỏi người học
- Có nên đặt guard tỉ lệ phase (ví dụ Phase B phải ≥ Phase A, Phase C phải ngắn nhất) làm **điều kiện đóng range** hay chỉ hiển thị cảnh báo? Người học đã chốt "không đặt sàn độ dài tối thiểu cho range", nhưng L9/L8 nói về **tỉ lệ giữa các phase** — hai điều này chưa được phân xử với nhau.
