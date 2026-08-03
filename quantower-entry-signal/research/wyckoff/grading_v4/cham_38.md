# Chấm bài #38 — Phân phối (DIST) · 2026-07-10 01:00 → 08:49 (469 nến M1)

**Điểm: 4/10** — Khung range, tên range và SOW đều đúng; đây thật sự là một vùng phân phối. Nhưng vùng nhãn ở Phase C bị làm nát: hai nhãn UTAD cùng lúc, cả hai đặt sai vị trí, và một LPSY[C] kẹp giữa chúng. Dải phase bị băm thành B-C-B-C-B với một đoạn B dài 1 nến.

## Lỗi (nặng → nhẹ)

### 1. Hai nhãn UTAD, cả hai sai vị trí — đúng ra là UT trong Phase B — luật vi phạm: lỗi kinh điển Ca #1/#3/#4 nguồn 4.pdf (lặp 3/5 ca) / THEORY §4.1
- **Thuật toán gắn:** UTAD (thất bại) tại 03:00 giá 4141.9, **và** UTAD (thất bại) tại 03:08 giá 4144.6 — cách nhau 8 nến.
- **Đúng phải là:** UTAD là cú test **cuối cùng** phá đỉnh range **ngay trước khi cấu trúc sụp**. Sau 03:08, giá còn dao động trong range thêm **315 nến** (đỉnh 4144.0 lúc 03:09, đáy 4112.8 lúc 08:03) mới sụp ở 08:24. Theo tiêu chí phân biệt của Ca #4 nguồn 4.pdf — "nếu sau đỉnh giá vẫn còn dao động/hồi trong range thì đó là UT thường, chưa phải UTAD" — cả hai đều là **UT**. Và theo L3 mỗi bên chỉ giữ **một** nhãn UT: giữ cái xa nhất (4144.6 ở 03:08), xoá cái 4141.9.
- **Dấu hiệu quyết định trên chart:** hai nhãn "UTAD (thất bại)" chồng đè lên nhau ở mép trên bên trái, còn cú sụp thật (nhãn SOW) nằm tận mép phải chart, cách hơn 5 giờ giao dịch.
- **Nghi phạm trong thuật toán:** mục 5.1 gán UTAD cho **mọi** cú "thăm dò THẬT" ở cạnh climax khi origin là BCLX, không kiểm điều kiện "không còn nhịp hồi giữ được trong range sau đó". Thêm nữa, quy tắc "mỗi bên chỉ giữ 1 nhãn" ở mục 5.0 chỉ áp cho UA/UT/DA mà **không áp cho UTAD**, nên UTAD được phép lặp.

### 2. LPSY[C] gán vào giữa hai cú UT, cao hơn cả biên chính trên — luật vi phạm: L7 / THEORY §4.1 (LPSY = "đợt phục hồi yếu trên biên hẹp")
- **Thuật toán gắn:** LPSY[C] tại 03:06, giá 4142.2 (nến O 4139.6 → C 4142.2, thân 0.87 — nến tăng mạnh).
- **Đúng phải là:** không có nhãn nào ở đây. 4142.2 nằm **cao hơn biên chính trên 4140.8** và cao hơn cả cú UT thứ nhất (4141.9); nó là một nến **trong cùng đợt đẩy lên** dẫn tới đỉnh 4144.6, không phải một đợt phục hồi yếu sau khi test biên dưới.
- **Dấu hiệu quyết định trên chart:** nhãn LPSY[C] (màu xanh, nhóm "hồi test") nằm **trên** đường biên chính trên và **trên** nhãn UTAD thứ nhất — sai cả về giá lẫn về logic thứ tự.
- **Nghi phạm trong thuật toán:** mục 6 nói "trong lúc chờ, giá quay về test đúng vùng điểm rũ → đánh dấu LPSY[C]". Với hai cú rũ liền kề, nến 03:06 nằm trong dung sai của vùng điểm rũ 03:00 nên bị bắt, dù nó là nến của cú đẩy tiếp theo. Cần chặn: nến LPSY[C] không được là nến tạo cực trị mới cùng hướng cú rũ.

### 3. Phase C dài 121 nến, Phase B có đoạn dài 1 nến — luật vi phạm: L8 (C ngắn nhất), L9 (B dài nhất)
- **Thuật toán gắn:** A 58 · B 62 · **C 7** · **B 1** · **C 121** · B 195 · D 25 · E 1.
- **Đúng phải là:** một Phase C duy nhất, ngắn, quanh cú UT cuối cùng. Ở đây Phase C thứ hai (121 nến) dài gấp đôi Phase B đầu (62 nến), và có một đoạn Phase B chỉ **1 nến** (03:07) — vô nghĩa với một phase mà định nghĩa là "giai đoạn xây dựng nguyên nhân, dài nhất".
- **Dấu hiệu quyết định trên chart:** cụm nhãn "Phase C (7n) / Phase B (1n) / Phase C (121n)" xếp thành ba tầng chồng nhau ở một chỗ duy nhất trên trục thời gian.
- **Nghi phạm trong thuật toán:** ngưỡng "Phase C chờ tối đa **120 nến**" quá lỏng — nó cho phép Phase C dài tới 120 nến trước khi bị coi là thất bại, trong khi L8 nói C là phase ngắn nhất. Cộng thêm việc máy trạng thái được phép lùi C→B tự do (mục 2 điểm 1) nên mỗi cú rũ mới lại băm dải phase thêm một lần.

### 4. ST[A] nằm giữa range, không test được vùng climax — luật vi phạm: L2 / THEORY §5
- **Thuật toán gắn:** ST[A] tại 01:57, giá 4130.8, VSA 1.13x.
- **Đúng phải là:** ST[A] phải test lại **vùng climax** (4140.8), không phải "ngọ nguậy giữa range". 4130.8 nằm gần đúng điểm giữa biên chính (4118.3-4140.8, giữa = 4129.6) — cách climax **10 giá = 44% chiều cao range**. Theo THEORY §5, ST ở Phase A chỉ đọc được ý nghĩa khi nằm ở 1/3 nửa trên hoặc 1/3 nửa dưới; nằm giữa thì không nói lên gì. Cú test vùng BCLX thật là đợt lên 4137.6 (02:59) → 4141.9 (03:00).
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm lơ lửng chính giữa hai đường biên chính cam, không chạm đường nào.
- **Nghi phạm trong thuật toán:** ngưỡng "ST[A] phải hồi ≥ **40%** chiều cao climax↔AR". 40% cho phép ST[A] dừng ngay dưới điểm giữa range. Nếu cần ST[A] thật sự test vùng climax thì ngưỡng phải quanh 70-80%.

### 5. Phase E dài 1 nến — lỗi trình bày/mô hình hoá — luật vi phạm: L10
- **Thuật toán gắn:** Phase E = 08:49, đúng 1 nến.
- **Đúng phải là:** Phase E là giai đoạn giá rời range đi tìm vùng giá mới, phải là một đoạn. Giá đi được 4118.3 → 4103.3 = 15.0 giá = 67% chiều cao range trong 25 nến, tức đạt mốc "≥50% khi hết giờ" đúng ở nến cuối cửa sổ, nên E thu về 1 nến.
- **Nghi phạm trong thuật toán:** mốc "hết 25 nến mà đi được ≥50% → chốt Phase E" luôn chốt E tại **nến cuối cửa sổ**, khiến E không bao giờ có độ dài. Nên chốt E tại nến **đầu tiên** vượt mốc 50%, rồi để E chạy tới khi range đóng.

## Đạt
- **Điều kiện mở range (L1):** MOVE tăng 17.3 giá / 26 nến / hiệu suất 0.51; climax 01:00 là đỉnh cửa sổ, volume 321 = VSA 4.75x, biên độ 5.2 giá. Đúng "climax chặn move".
- **Tên range (L4):** origin BCLX + phá xuống thật = Phân phối. Chính xác.
- **Biên (L3):** biên chính 4118.3 + 4140.8 cố định; biên phụ 4117.0 (từ DA) và 4144.6 (từ cú UT), mỗi bên 1. Đúng luật.
- **DA (L3):** DA 05:47 tại 4117.0 đúng là cực trị xa nhất bên dưới và trùng khớp biên phụ dưới — nhất quán.
- **SOW (L3, L10):** SOW 08:24 giá 4114.0 đóng cửa bứt qua **biên phụ** 4117.0 (không chỉ biên chính), VSA 1.97x, thân 0.71. Đúng yêu cầu "SOW mạnh phải bứt qua biên phụ".
- **Range là một vùng đấu giá thật:** 469 nến với biên chính chỉ 22.5 giá (0.54%), hai biên đều được test nhiều lần. Không phải nhiễu.

## Đọc thêm về khối lượng (thuật toán bỏ qua)
Nến AR 01:39 có volume **631 (VSA 9.29x)** — gần **gấp đôi** nến BCLX (321). Nỗ lực bán ở Phase A đã lớn hơn nỗ lực mua ở climax; theo THEORY §4.4 dấu hiệu #1 đây là dấu hiệu phân phối rất sớm, đọc được ngay từ Phase A. Thuật toán chỉ dán nhãn "AR" trung tính, không dùng thông tin này để nghiêng bias — đây là một tín hiệu miễn phí đang bị bỏ.
