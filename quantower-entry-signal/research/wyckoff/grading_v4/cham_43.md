# Chấm bài #43 — Tái phân phối (RE-DIST) · 2026-07-16 13:04 → 2026-07-17 13:48 (1423 nến M1)

**Điểm: 3/10** — Range mở **rất chuẩn** và đây đúng là một vùng đấu giá thật, nhưng **tên range sai** (cú phá xuống bị phủ định ngay trong Phase D) và **2 trong 3 cú Shakeout không được phép gọi tên** vì không phá đáy cũ. Phải vẽ lại phần cuối, không phải bỏ range.

## Lỗi (nặng → nhẹ)

### 1. Tên range SAI — gán RE-DIST cho một cú phá xuống bị bác bỏ ngay — luật vi phạm: L4 (hướng phá THẬT quyết định tên) + L10 + THEORY §9 (cấu trúc thất bại)
- **Thuật toán gắn:** SOW @17/07 13:23 tại 3972.1 → range = **Tái phân phối**, đóng ở Phase D.
- **Đúng phải là:** cú xuống này **thất bại**. Đáy thật của cả TR là **3963.0 @13:01** — đó là một **Terminal Shakeout / Spring #3** (THEORY §3.5); chỉ 38 nến sau, nến **13:39 VSA 4.61x** đóng cửa **3997.4**, tức **sâu 18.3 giá trong range** và cách biên trên chỉ 15 giá. Theo chính mục 7 Câu 1 ("một nến đóng cửa lùi hẳn vào trong range quá 30 tick → cú phá hỏng") thì cú phá đã hỏng, nên **không được giữ tên RE-DIST**. Đọc đúng: đây là **tích luỹ / tái tích luỹ**, cú rũ đáy 3963 là Phase C, và SOS thật là cú bứt lên xảy ra ngay sau đó (mà máy lại tách thành range #44).
- **Dấu hiệu quyết định trên chart:** nhìn ảnh, ngay sau nhãn SOW là một nến xanh dài vọt từ ~3970 lên 4008 — giá **quay hẳn vào trong range** rồi đi lên. Phase D 26 nến kết thúc bằng giá CAO hơn lúc bắt đầu.
- **Nghi phạm trong thuật toán:** mục 2 — "SOS/SOW đã xác nhận thì range ĐÓNG luôn, không lùi lại nữa". Kiểm tra "phá hỏng" ở mục 7 Câu 1 hoặc không được áp, hoặc có áp nhưng **không huỷ tên đã gán**.

### 2. Nhãn SOW đặt trên một nến chết (volume 62 = 0.47x) — luật vi phạm: THEORY §4.1/§4.2 (SOW = spread + volume TĂNG) + mục 8 chấm (Effort vs Result)
- **Thuật toán gắn:** SOW 13:23, giá 3972.1, VSA **0.47x**, thân 0.52 — volume 62 so với trung bình ~132.
- **Đúng phải là:** không có SOW nào ở đây. Cú phá xuống có nỗ lực thật là cụm **12:19–13:01** (đáy 3963.0, các thanh volume vàng lớn trên panel), và nó **không đi tiếp** — nỗ lực lớn, kết quả nhỏ = dấu hiệu đảo chiều, đúng cơ chế Spring #3 ("volume vẫn cao nhưng range co lại dần").
- **Dấu hiệu quyết định trên chart:** SOW được vẽ ở nến nằm **7.0 giá dưới** biên chính 3979.1 nhưng chỉ **1.3 giá (13 tick)** dưới biên phụ 3973.4 — vừa đủ lách qua ngưỡng, với volume bằng nửa trung bình.
- **Nghi phạm trong thuật toán:** điều kiện phá thật (3 nến đóng vượt biên phụ ≥30 tick, thân ≥45%) **không có điều kiện khối lượng nào**. Với L3 ("SOS/SOW mạnh phải bứt qua biên phụ") thì nên thêm: nến phá phải có VSA ≥ 1 (tối thiểu ngang trung bình).

### 3. Hai cú "Shakeout" không phá đáy cũ — luật vi phạm: lỗi kinh điển #6 CHART_CASES (2.pdf, 4/22 ca — lỗi phổ biến nhất của cả nguồn) + L3
- **Thuật toán gắn:** Spring (thất bại) @19:38 = 3973.4 · Shakeout (thất bại) @22:44 = **3976.8** · Shakeout (thất bại) @17/07 02:38 = **3974.1**.
- **Đúng phải là:** chỉ cú đầu (3973.4) đủ điều kiện — nó là đáy thấp nhất TR tại thời điểm đó. Hai cú sau **cao hơn 3973.4** nên theo phát biểu tường minh của giảng viên ở Ca #19 (2.pdf): "Spring bắt buộc phải là điểm giá **thấp nhất trong suốt Trading Range**"; đáy không phá được đáy cũ thì chỉ là **ST/test thường**, không được mang tên Spring/Shakeout. Nó cũng khớp L3: cú thăm dò nông hơn cú cũ thì **không ghi gì cả**.
- **Dấu hiệu quyết định trên chart:** biên phụ dưới đứng nguyên ở 3973.4 suốt cả 3 lần rũ — chính đường nét đứt đó tự tố rằng 2 cú sau không tạo được cực trị mới.
- **Nghi phạm trong thuật toán:** nhánh nhận Spring/Shakeout so với **biên chính** (3979.1) chứ không so với **đáy thấp nhất đã có của TR / biên phụ**. Sửa: yêu cầu `low < min(low toàn range trước đó)`.

### 4. Dải phase B/C xen kẽ 7 lần, ba Phase C dài **đúng 121 nến** — luật vi phạm: L8 (Phase C là phase NGẮN NHẤT) + L9 (Phase B là phase DÀI NHẤT)
- **Thuật toán gắn:** A 42 · B 352 · C 121 · **B 5** · C 121 · B 112 · C 121 · B 524 · D 26.
- **Đúng phải là:** một Phase B duy nhất từ 13:46 (16/07) đến ~13:00 (17/07) chứa các cú test đáy thất bại, rồi Phase C = **nhịp rũ cuối cùng ngay trước cú phá**. Ba khối "Phase C" đều dài chính xác 121 nến = **artefact của ngưỡng timeout 120 nến**, không phải kết quả đọc cấu trúc; một "Phase B 5 nến" thì tự phủ định L9.
- **Dấu hiệu quyết định trên chart:** dải phase ở đầu ảnh nhảy B→C→B→C→B→C→B trong khi giá vẫn dao động y như nhau giữa 2 biên — mắt người không đọc ra ranh giới nào ở những chỗ đó.
- **Nghi phạm trong thuật toán:** cơ chế "Phase C thất bại → lùi về Phase B" (mục 6) **ghi lại vào dải phase** thay vì chỉ xoá nhãn. Cú rũ thất bại nên để nguyên trong Phase B, không cắt phase.

### 5. Climax lệch 1 nến + ST[A] lệch 1 nến (nhẹ) — luật vi phạm: L3 (biên chính = mức climax), L2
- **Thuật toán gắn:** SC 3979.1 @13:04 · ST[A] 3990.0 @13:45.
- **Đúng phải là:** đáy cụm climax = **3977.1 (13:05)** → biên chính dưới nên là 3977.1. ST[A]: đáy nhịp là **3989.6 (13:44)**, không phải 3990.0 (13:45).
- **Dấu hiệu quyết định trên chart:** cả hai lệch nhỏ (2.0 giá và 0.4 giá) nên không đổi kết luận, nhưng cùng một gốc lỗi với bài #41/#42/#45: mốc luôn lấy **nến đầu tiên thoả điều kiện**, không phải **cực trị của cụm**.

## Đạt
- **L1 điều kiện mở range:** xuất sắc — MOVE giảm 69.6 giá / 60 nến, hiệu suất 0.45, cây SC biên độ 10.6 giá VSA 2.34x chặn đúng đáy đợt rơi. Nhìn ảnh là ca rõ nhất trong 5 bài.
- **L2:** đủ 3 lần đổi hướng; AR bật 33.5 giá = **48% độ dài move** (rất mạnh); ST[A] nằm ở **32.5% chiều cao** tính từ SC — tức trong 1/3 phía climax, đúng ô "lực bán nhất định" của THEORY §5.
- **L3 biên phụ:** làm đúng — mỗi bên đúng 1 biên phụ (trên 4021.8 từ UA, dưới 3973.4 từ Spring), biên phụ cũ bị thay khi có điểm xa hơn, biên chính không bị kéo theo giá.
- **L9:** tổng Phase B (993 nến) vẫn là phần dài nhất — đúng bản chất.
- Range 1423 nến với giá quay lại **cả hai biên nhiều lần** — đây thật sự là một vùng đấu giá, khác hẳn bài #42/#45.

## Cần hỏi người học
1. Cú **UA @15:25** vượt biên trên (biên AR) tới **9.2 giá = 92 tick, VSA 4.02x**, và **đóng cửa ngoài biên 6 nến liên tiếp** trước khi rút vào. Theo bảng mục 5.1 thì cạnh AR luôn chỉ ghi UA/DA "không quyết định", nhưng theo L5 thì "phá ra, lùng bùng ngoài một lúc rồi mới quay lại" = **một SOS thất bại**. Ca này nên gọi **UA**, hay **UT / SOS thất bại**? L3+L6 hiện không phân xử được.
2. Khi cú phá bị phủ định ngay trong cửa sổ Phase D (bài này), range có được **đổi tên** theo hướng ngược lại không, hay giữ tên theo cú phá đã xác nhận? L4 nói "hướng phá thật quyết định tên" nhưng không định nghĩa "thật" cho ca bị bác sau 20-30 nến.
