# Chấm bài #29 — Tái tích lũy (RE-ACC) · 2026-06-25 12:30 → 16:30 (240 nến M1)

**Điểm: 2/10** — hai biên chính (4004.8–4027.4) được lấy từ **thân một cây tin 29.1 giá**, còn giá thật thì đấu giá ở 4024–4051 suốt 200 nến **phía trên** biên trên. ST[A] bị đặt cách mức climax 22.2 giá (98% chiều cao range) — đó là một cú phá vỡ, không phải cú test. Phase C dài 121 nến, thành phase dài nhất chart. Phải vẽ lại range ở vùng khác, không sửa nhãn được.

## Lỗi (nặng → nhẹ)

### 1. ST[A] đặt ngoài range, xa bằng cả chiều cao range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 13:13, giá **4049.6** — cao hơn mức climax 4027.4 tới **22.2 giá**, tức **98% chiều cao biên chính (22.6 giá)**.
- **Đúng phải là:** ST[A] là "giá quay về phía climax rồi **bị chặn nhẹ lần nữa**". Bị chặn ở mức cao hơn climax gần đúng một lần chiều cao range thì đó là **SOS/phá vỡ**, không phải ST[A] — Phase A phải bị coi là chưa hoàn thành và ứng viên range phải **bỏ**.
- **Dấu hiệu quyết định trên chart:** từ 13:05 tới 13:13 giá dao động 4040–4049.6, **hoàn toàn ở trên** đường liền "bien CHINH tren 4027.4". Cả nhãn ST[A] lẫn nhãn UTAD đều nằm cao hơn biên trên trên hình.
- **Nghi phạm trong thuật toán:** dòng 375–395 — `retrace` không có **giới hạn trên** (ở đây retrace ≈ 2.0) và dòng 391–395 chỉ lặng lẽ nới biên phụ khi "ST[A] vượt qua climax". Cần chặn: nếu ST[A] vượt mức climax quá ~50% chiều cao biên chính thì huỷ ứng viên (giá đã bỏ vùng cân bằng đi rồi).

### 2. Hai biên chính lấy từ một cây tin, không phải từ vùng đấu giá — luật vi phạm: L1 + L3
- **Thuật toán gắn:** climax = nến 12:30 (H=4027.4, L=3998.3, **biên độ 29.1 giá**, volume 1809 = 10.34×); AR = 4004.8 tại 12:35, chỉ 5 nến sau.
- **Đúng phải là:** 12:30 UTC là nến tin (8:30 giờ New York). Cả "biên trên" và "biên dưới" đều nằm **trong biên độ của đúng một nến** — AR 4004.8 chỉ là đáy nhịp giật lại của chính cây tin đó, không phải một Automatic Rally đàm phán được với thị trường. Vùng đấu giá thật sau cú tin là **4024–4051** (giá ở đó 200 nến), tức range nên mở **sau** cây tin với biên trên ≈ 4049.9 và biên dưới ≈ 4024.
- **Dấu hiệu quyết định trên chart:** đường liền "bien CHINH tren 4027.4" chạy **xuyên qua đáy** của vùng dao động chính; đường liền dưới 4004.8 gần như **không được giá chạm lại lần nào** trong suốt 240 nến. Một biên mà giá không quay lại test thì không phải biên.
- **Nghi phạm trong thuật toán:** cửa sổ tìm AR 40 nến cho phép AR rơi vào 1–5 nến ngay sát climax (chỉ gắn nhãn cảnh báo "AR (yếu)" khi ≤2 nến, không đổi logic — mục 4.1 tài liệu). Với nến climax biên độ 29 giá thì AR trong 5 nến gần như chắc chắn là nhịp giật của chính nó.

### 3. Phase C = 121 nến, thành phase DÀI NHẤT — luật vi phạm: L8 (Phase C ngắn nhất)
- **Thuật toán gắn:** A=44 · B=8 · **C=121** · B=42 · D=26. Dải "Phase C (121n)" chiếm nửa chart.
- **Đúng phải là:** cú rũ thất bại thì đoạn sau nó phải là **Phase B**, không được giữ nhãn C. Phase C chỉ nên là mấy nến quanh cú rũ.
- **Dấu hiệu quyết định trên chart:** ngưỡng chờ Phase C của chính thuật toán là 120 nến; ở đây nó chạy **đúng 121 nến rồi mới** lùi về B — nghĩa là nhãn C được hiển thị cho toàn bộ thời gian chờ, kể cả khi kết luận cuối là "thất bại".
- **Nghi phạm trong thuật toán:** khi `shock` bị đánh `failed` (dòng 525–536) code mới `set_phase(i,'B')` **từ nến hiện tại**, không **thu hồi** đoạn C đã vẽ. Phải vẽ lại đoạn đó thành B (hoặc chỉ vẽ C sau khi cú rũ được xác nhận).

### 4. Nhãn UTAD sai chỗ, sai loại, và đúng ra không được ghi — luật vi phạm: Ca #1/#4 nguồn 4.pdf + Ca #8 nguồn 7.pdf + L3
- **Thuật toán gắn:** UTAD (thất bại) tại 13:22, giá 4046.2.
- **Đúng phải là:** **không ghi gì cả.** Ba lý do độc lập: (a) 4046.2 **nông hơn** cực trị đã có 4049.6 (ST[A], 9 nến trước) và nông hơn cả biên phụ 4049.9 → theo L3 "cú thăm dò mới nông hơn cú cũ thì không ghi gì"; (b) UTAD là sự kiện **Phase C của phân phối, đứng ngay trước khi cấu trúc sụp** — ở đây cấu trúc phá **lên** (range chốt tên Tái tích luỹ), nên đây đúng là lỗi kinh điển "gọi UTAD cho một cú vượt đỉnh trong Phase B"; (c) nến 13:22 chỉ có VSA 0.91× — không có nỗ lực nào để gọi là cú rũ.
- **Nghi phạm trong thuật toán:** `_mark_outer()` dòng 584 chỉ lọc trùng cho **`UA/DA/UT`**, không lọc cho `UTAD/Spring/Shakeout` — nên một cú thăm dò nông hơn cực trị cũ vẫn được ghi nếu nó rơi vào nhánh "thăm dò THẬT". Ngoài ra tên `UT` vs `UTAD` chọn theo origin (mục 12.7 tài liệu tự nhận "cần xác nhận") — phải đổi lại theo `r.dir` khi đóng range.

### 5. SOS gắn lên một nến doji, volume 0.31× — luật vi phạm: mục 8 THEORY + WY05
- **Thuật toán gắn:** SOS tại 16:05, giá 4053.5 — nến O=4053.5 H=4055.4 L=4053.1 **C=4053.5**, thân **0.00**, volume **70 = 0.31×**.
- **Đúng phải là:** đoạn thể hiện sức mạnh thật là **15:55–15:58** (volume 268 / 334 / 212, VSA 1.55× / 1.78× / 1.09×, giá 4052 → 4058.5), và trước đó là cây bứt 15:11 (thanh volume vàng cao nhất nửa sau chart).
- **Dấu hiệu quyết định trên chart:** nhãn SOS nằm ở 16:05 trong khi giá đã ở trên biên phụ 4049.9 liên tục từ khoảng 15:55; panel volume tại 16:05 gần như phẳng.
- **Nghi phạm trong thuật toán:** giống bài #28 — chuỗi xác nhận (3 nến, thân ≥45%) đẩy nhãn tới nến thoả cuối cùng, và không kiểm tra nến được gắn nhãn có nỗ lực hay không. Nên yêu cầu nến mang nhãn SOS/SOW có VSA ≥ 1 (tối thiểu bằng trung bình), hoặc gắn hồi tố vào nến VSA cao nhất của đoạn phá.

### 6. Phase A = 44 nến > Phase B đợt đầu 8 nến — luật vi phạm: L9
- Tổng B = 8 + 42 = 50 nến, chỉ nhiều hơn A một chút, và bị Phase C 121 nến chiếm mất chỗ. Cùng lỗi hệ thống của lô (Phase A ≥ `AR_LOOKBACK + 1` = 41 nến).

## Đạt
- **Mục 1 (một phần):** MOVE trước climax có thật — 38.8 giá / 54 nến, hiệu suất 0.37; nến 12:30 là đỉnh cao nhất cửa sổ và có nỗ lực khổng lồ (1809 lot, 10.34×). Việc **nhận ra** đây là climax là đúng; sai ở chỗ dùng chính nến đó để dựng cả hai biên.
- **Mục 4 (L4):** tên range đúng — origin BCLX + phá lên = **Tái tích luỹ**.
- **L7:** LPS[D] chỉ 1 điểm (16:09, 4049.3), hồi về đúng vùng biên phụ vừa phá — đúng vai.
