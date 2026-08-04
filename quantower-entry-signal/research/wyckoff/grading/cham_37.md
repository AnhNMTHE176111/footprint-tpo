# Chấm bài #37 — Tái phân phối (RE-DIST) · 2026-06-30 00:09 → 00:56 (47 nến M1)

**Điểm: 5/10** — Phase A ở đây là Phase A **đúng bài nhất cả lô**, nhưng cả range chỉ 47 nến / 10.4 giá thì đó là một nhịp thở giữa đợt giảm, chưa phải một vùng đấu giá; thiếu Phase C, và Phase E bị chốt ngay lúc cú xả thật mới bắt đầu.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn: 47 nến / 10.4 giá (0.26%) mà đủ Phase A→E — luật vi phạm: L1 (mục 1 tiêu chí chấm)
- **Thuật toán gắn:** một TR hoàn chỉnh 5 phase trong 47 nến M1, phase dài nhất chỉ 18 nến.
- **Đúng phải là:** đây là chỗ giảng viên nhiều lần yêu cầu đổi khung (Ca #4, #6, #19 nguồn 7.pdf: "khung quá thô/quá vụn"). Áp cho lần này: một cấu trúc Wyckoff đủ A→E gói trong 47 nến, mỗi phase 6–18 nến, ở phiên Á với volume 7–140 lot, thì phải nghi ngay đó là dao động vi mô. Cái đáng vẽ là **vùng đấu giá 4007–4027 kéo dài từ 00:09 tới 01:00**, không phải cắt 47 nến rồi tuyên bố xong.
- **Dấu hiệu quyết định trên chart:** chiều cao biên chính 10.4 giá; ngay sau khi range đóng lúc 00:56, giá rơi từ 4007 xuống **3955** (52 giá, gấp 5 lần chiều cao range) trong khoảng 30 nến — cú xả thật nằm **ngoài** range mà thuật toán đã vẽ.
- **Nghi phạm trong thuật toán:** người học đã chốt "không đặt sàn độ dài tối thiểu cho range", nên đây không phải lỗi vi phạm luật đã chốt — nhưng hệ quả thì thấy bằng mắt. Kiến nghị: thay sàn độ dài bằng sàn **chiều cao so với ATR nền** (range 10.4 giá trong khi biên độ nến climax đã 3.2 giá → range chỉ đáng 3 cây nến).

### 2. Thiếu hoàn toàn Phase C — luật vi phạm: L8, mục 6 spec
- **Thuật toán gắn:** timeline A → B → D → E; bảng sự kiện chỉ có SC, AR, ST[A], SOW, LPSY[D].
- **Đúng phải là:** SOW bắn 00:37 mà range chưa có Phase C thì bắt buộc gán ngược: nhìn lại ≤60 nến, lấy nhịp test cuối cùng — trên ảnh là cụm đỉnh 00:31–00:33 quanh 4021–4022 (nhịp hồi cuối cùng trước khi giá xuyên hẳn biên dưới) — làm **LPSY[C]**, và Phase C bắt đầu từ đó.
- **Dấu hiệu quyết định trên chart:** Phase B kết thúc 00:36, SOW ở 00:37; không một nến nào thuộc Phase C.
- **Nghi phạm trong thuật toán:** giống #35/#36/#39 — nhánh gán ngược Phase C (spec mục 6, cửa sổ min(60 nến, ½ Phase B)) không sinh nhãn. Ở bài này Phase B chỉ 18 nến nên cửa sổ gán ngược = 9 nến, có thể quá hẹp để chứa nhịp test → nghi ngưỡng `½ Phase B` là thủ phạm ở các range ngắn.

### 3. Phase E dài 6 nến, chốt ngay lúc move thật bắt đầu — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 00:51 → 00:56 (6 nến) rồi đóng range.
- **Đúng phải là:** Phase E là "giá rời range đi tìm **vùng giá mới**". Ở thời điểm 00:56 giá mới đi được ~10 giá; vùng giá mới thật sự chỉ hình thành quanh 3965–3985 sau đó. Đích Phase E "đi thêm 1× chiều cao range" = 10.4 giá là quá dễ đạt vì chính chiều cao range đã quá nhỏ.
- **Dấu hiệu quyết định trên chart:** trên ảnh, dải Phase E (6n) kết thúc ở khoảng giá 4007 trong khi cây rơi lớn nhất của cả khung (thanh volume vàng cao nhất, ~01:05) nằm **sau** khi range đã đóng.
- **Nghi phạm trong thuật toán:** đích Phase E neo theo chiều cao range (mục 7 câu 3). Với range vụn thì mốc này vô nghĩa; nên kèm sàn tuyệt đối theo ATR.

### 4. Chú giải nhịp nỗ lực/kết quả nói ngược — lỗi trình bày chỉ số (v6)
- **Thuật toán gắn:** nhịp 00:21, effort 0.51x, result 1.64, er = 0.31 → in "vung hap thu NGHI VAN (volume nhieu, ket qua it)".
- **Đúng phải là:** effort 0.51x là volume **thấp**, result 1.64 là kết quả **lớn** — tức "ít nỗ lực nhiều kết quả", dấu hiệu **cạn cung/cạn cầu**, ngược hẳn với chữ "volume nhiều kết quả ít". Chuỗi này in y hệt ở cả 5 bài lô này với er từ 0.13 tới 0.94.
- **Nghi phạm trong thuật toán:** câu chú giải hardcode, không có ngưỡng phân loại theo er; và cần chốt lại chiều của er (er nhỏ = nỗ lực nhiều kết quả ít, hay ngược lại?) vì hiện tại cả er=0.13 và er=0.94 đều ra cùng một câu.

### 5. Nhãn SC lệch mức climax 1.1 giá — lỗi trình bày (hệ quả cơ chế v6)
- **Thuật toán gắn:** nhãn SC ở 00:06 giá 4018.2 (VSA 4.47x), mức biên chính dưới = 4017.1 ở nến 00:09.
- **Ghi rõ:** cơ chế tách nhãn/mức là hợp lệ theo v6 và ở bài này lệch nhỏ (1.1 giá, 3 nến) nên đọc chart vẫn ổn. Chỉ ghi nhận để đối chiếu với #35 và #39, nơi cùng cơ chế gây lỗi thật.

## Đạt
- **Phase A đúng bài nhất cả lô (L2):** SC 4017.1 (đáy chặn move) → AR 4027.5 lên 10.4 giá trong 3 nến, VSA 2.55x → **ST[A] 00:18 tại 4018.3, đúng vào vùng SC (lệch 1.2 giá), VSA 0.82x**. Test lại đúng vùng climax với volume co lại từ 2.66x xuống 0.82x — đây chính là ST kinh điển theo THEORY §3.3. Đủ 3 lần đổi hướng, Phase A kết thúc đúng tại ST[A].
- Điều kiện mở range (L1): MOVE giảm 16.3 giá / 50 nến, hiệu suất 0.39; trên ảnh là chuỗi bậc thang giảm rõ từ 4035 xuống 4018, climax là cây đỏ chặn đáy.
- Biên chính = climax + AR, cố định; biên phụ dưới 4016.1 đúng là cực trị xa nhất, mỗi bên tối đa 1 (L3).
- Tên range đúng L4: origin SC + phá xuống thật = Tái phân phối — và kết cục thực tế (rơi 52 giá tiếp) xác nhận cách gọi này.
- SOW 00:37: VSA **6.90x**, thân 0.55, đóng cửa 4010.1 — vượt cả biên chính (4017.1) và biên phụ (4016.1) → thoả L3.
- LPSY[D] 00:46: một điểm duy nhất (L7), VSA **0.42x** (test volume co), giá 4007.6 vẫn giữ ngoài biên → CBR đúng L10.
- Bias = −1 khớp chart: trong Phase B đỉnh cao nhất chỉ ~4024.5, không với tới biên trên 4027.5, còn biên dưới thì bị chạm liên tục.
