# Chấm bài #46 — Chưa rõ (BCLX) (DIST?) · 2026-07-14 12:33 → 16:32 (239 nến M1)

**Điểm: 3/10** — vùng đấu giá là có thật, nhưng gần như mọi cái nhãn đều đặt sai chỗ: climax bỏ sót cây nổ thật, chân MOVE bịa ra 3 tiếng xu hướng không tồn tại, ST[A] nằm giữa range, và cái đỉnh cuối cùng trước khi sụp bị gọi là LPSY[C].

## Lỗi (nặng → nhẹ)

### 1. MOVE trước climax là MOVE GIẢ — 176/179 nến của nó là đi ngang — luật vi phạm: L1
- **Thuật toán gắn:** "chân MOVE (78.3 giá, hiệu suất 0.36)", chân đặt ở 09:2x quanh 4034.
- **Đúng phải là:** chân move ở **4036.1 lúc 12:30** — toàn bộ 78.3 giá nằm gọn trong **3 cây** 12:30–12:33.
- **Dấu hiệu quyết định trên chart:** phiếu số liệu, nến 12:30 mở 4036.1 / đóng 4096.3 — tức từ chân move được vẽ (4034.2) tới đầu cây 12:30 giá chỉ nhích **1.9 giá trong 176 nến**. Nhìn ảnh: từ 09:09 tới 12:29 giá lắc phẳng trong dải 4020–4040, rồi một cây tin nhảy 62 giá. Đó không phải "một move xu hướng bị climax chặn lại", đó là một cú gap tin tức.
- **Nghi phạm trong thuật toán:** tham số "MOVE: cửa sổ nhìn lại 240 nến, loại bỏ hẳn **nến** climax" — chỉ loại đúng 1 nến (12:33), trong khi cụm climax ở đây là 12:30–12:33. Ba cây còn lại tự nuôi chỉ số move của chính nó (lỗi I của v4 tái diễn ở dạng cụm). Phải loại **cả cụm climax** khỏi phép đo move, và nên có sàn "hiệu suất tính trên đoạn không chứa nến VSA > 4×".

### 2. Nhãn climax rơi vào cây 7.01× trong khi cây 14.64× nằm ngay cạnh — luật vi phạm: mục 4.0 (cụm climax), vá #4 CHƯA đủ
- **Thuật toán gắn:** BCLX tại 12:31, giá 4104.7, VSA 7.01×.
- **Đúng phải là:** cây 12:30 — VSA **14.64×**, biên độ **62.4 giá**, thân 0.96. Đó là cây chặn move, và là cây to nhất cả chart (nhìn panel volume: cột vàng cao vọt duy nhất).
- **Dấu hiệu quyết định trên chart:** bảng 12 nến — 12:30 = 4597 lot / 14.64×; 12:31 = 3372 lot / 7.01×; nến mở range 12:33 chỉ 1307 lot / **1.98×**, tức còn **dưới ngưỡng climax 2.2×**.
- **Nghi phạm trong thuật toán:** vá #4 kẹp nhãn "theo nến mở range cố định" nên cửa sổ cụm chỉ quét **tiến** từ nến mở range. Cây mạnh nhất nằm **trước** nến mở range 3 nến nên vĩnh viễn không với tới. Cửa sổ cụm phải hai chiều (±8 nến), và nến được chọn làm mốc mở range không được có VSA thấp hơn cây liền trước nó.

### 3. LPSY[C] đặt lên ĐỈNH CAO NHẤT của range — sai vai nhãn — luật vi phạm: THEORY §4.1 (định nghĩa LPSY), L8
- **Thuật toán gắn:** LPSY[C] tại 15:08, giá **4108.7** — đỉnh cao nhất kể từ Phase A, sát biên chính trên 4112.5, VSA 3.02×.
- **Đúng phải là:** **UT[B]/UTAD** — cú test cuối cùng lên đỉnh range ngay trước khi cấu trúc sụp (sau nó là chuỗi giảm liền một mạch 43 giá). LPSY theo định nghĩa là *đợt phục hồi yếu, biên hẹp, ở nửa dưới, sau khi cung đã chiếm ưu thế* — không thể là đỉnh cao nhất cấu trúc.
- **Dấu hiệu quyết định trên chart:** trên ảnh, chấm LPSY[C] nằm cao hơn mọi nến của Phase B và chỉ cách nét liền biên trên vài giá; ngay sau nó là đoạn dốc thẳng xuống mSOW.
- **Nghi phạm trong thuật toán:** nhánh "Phase C gán ngược" (mục 6, case khó) lấy *đỉnh cao nhất trong 60 nến trước cú phá* rồi **mặc định** đặt tên LPSY[C]. Thiếu bước phân loại hình thái: pivot nằm ở ≥80% chiều cao range và là đỉnh cao nhất từ đầu Phase B thì phải gọi UT/UTAD, không phải LPSY.

### 4. ST[A] nằm giữa range, không test lại vùng climax — luật vi phạm: L2; vá #2 CHƯA đủ
- **Thuật toán gắn:** ST[A] 13:02 tại 4091.0.
- **Đúng phải là:** cú hồi phải chạm lại vùng 4104–4112 (vùng climax). 4091.0 cách climax **21.5 giá = 59% chiều cao range**.
- **Dấu hiệu quyết định trên chart:** biên chính 4076.2–4112.5 (36.3 giá); ST[A] hồi từ AR đúng 14.8 giá = **0.41×** — vừa đủ lọt ngưỡng mới 0.40. Ngưỡng nâng từ 0.2 lên 0.4 **không chạm** được lỗi này vì nó đo từ AR, không đo khoảng cách còn lại tới climax.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC`. Cần thêm ràng buộc đối xứng: ST[A] phải nằm trong khoảng ≤ 0.35× chiều cao range tính từ **mức climax** (đúng như mục 13.1 đã tự ghi nhận "ST[A] vẫn thiếu ràng buộc khoảng cách đáy tới climax").

### 5. Phase C dài 59 nến = gần một nửa Phase B — luật vi phạm: L8
- **Thuật toán gắn:** A 30 · B 125 · C **59** · D 26.
- **Đúng phải là:** Phase C phải là phase ngắn nhất. Ở đây nó gấp đôi Phase D và gần bằng nửa Phase B.
- **Dấu hiệu quyết định trên chart:** đoạn Phase C (15:08→16:06) chứa nguyên cả nhịp rơi 4108→4073 và cả nhãn mSOW — tức nó đã nuốt trọn cả đoạn phá vỡ, phần đáng lẽ là Phase D.
- **Nghi phạm trong thuật toán:** Phase C gán ngược neo mốc bắt đầu tại pivot rồi kéo tới tận SOS/SOW; không có trần độ dài Phase C cho nhánh gán ngược (nhánh case dễ có trần 120 nến, nhánh này không có).

### 6. mSOW ghi Phase = B nhưng nằm giữa dải Phase C — mâu thuẫn nội bộ
- **Thuật toán gắn:** mSOW 15:42, cột Phase ghi `B`; trên ảnh nó nằm giữa dải "Phase C (59n)".
- **Đúng phải là:** một sự kiện chỉ thuộc đúng một phase. Ở đây mSOW 4073.5 (VSA 3.40×) chính là cú phá xuống thật đầu tiên, phải mở Phase D chứ không phải nằm lẫn trong C.
- **Nghi phạm trong thuật toán:** phase của event được gán lúc phát sinh, không đồng bộ lại khi dải phase được vẽ ngược về sau.

### 7. Có đủ SOW + Phase D mà range không được đặt tên — luật vi phạm: L4
- **Thuật toán gắn:** "Chưa rõ (BCLX) (DIST?)", trạng thái `superseded`.
- **Đúng phải là:** origin BCLX + phá xuống thật (SOW 16:07, LPSY[D] giữ được dưới biên, giá đi tiếp xuống 4055) = **Phân phối**. Cơ chế SIDEWAYS không được phép xoá tên của một cấu trúc đã hoàn tất chuỗi A→D.
- **Nghi phạm trong thuật toán:** mục 5.4 — range cha bị `superseded` thì cấm đặt tên vô điều kiện. Nên cho phép đặt tên khi range cha đã có SOS/SOW xác nhận + LPS[D]/LPSY[D].

### 8. Chú thích "hấp thụ nghi vấn" đúng dấu nhưng sai chất (trình bày/diễn giải)
- er = 36.67 với **effort chỉ 1.05×** và result 0.03 — volume ở mức **trung bình**, giá đứng yên 16 nến. Đó là "chợ vắng", không phải hấp thụ. Vá #1 đã sửa đúng dấu er, nhưng còn thiếu **sàn effort** (gợi ý: chỉ gọi hấp thụ khi effort ≥ 1.5×).

## Đạt
- Vá #1 chạy đúng: nhãn er bám dấu thật, không còn hard-code.
- Biên phụ: đúng 1 cái mỗi bên tối đa (chỉ có biên phụ dưới 4073.5 = đáy mSOW, đúng cực trị xa nhất) — L3 đạt.
- Tỷ lệ biên phụ/chính 1.07× — không có hiện tượng biên phụ tự phình.
- SOW 16:07 neo đúng cây phá (VSA 2.31×, thân 0.54, đóng cửa dưới cả biên phụ) — không còn lỗi B của v4.
- LPS[D] hợp lệ: LPSY[D] 16:16 tại 4072.3 hồi về sát biên chính rồi vẫn giữ được bên ngoài — đúng tinh thần CBR (L10).
- Phase A kết thúc đúng tại ST[A], không kéo dài thêm (L2, phần hình thức).

## Nếu là tôi
Vẫn vẽ range ở đây — vùng 4076–4104 sau cây tin là một vùng cân bằng thật. Nhưng: climax = cây 12:30, chân move = 4036 lúc 12:30 (không phải 09:20), ST[A] = nhịp chạm lại 4100–4104 (khoảng 13:5x), đỉnh 15:08 = **UTAD**, Phase C = đúng vài nến quanh UTAD đó, Phase D bắt đầu từ mSOW 15:42, và range tên là **Phân phối**.
