# Chấm bài #35 — Tích luỹ (ACC) · 2026-06-30 01:07 → 15:00 (833 nến M1)

**Điểm: 5/10** — range mở đúng chỗ và Phase A đọc rất tốt, nhưng LPS[D] nằm lộn ngược trong Phase B (10 giờ trước SOS) và biên chính bị giá bỏ lại từ giữa Phase B nên toàn bộ nửa sau range mất khung tham chiếu.

## Lỗi (nặng → nhẹ)

### 1. LPS[D] đặt ở 04:48 — nằm TRONG Phase B, 10 giờ TRƯỚC SOS — luật vi phạm: L7 + mục 7 (phân biệt LPS[C]/LPS[D])
- **Thuật toán gắn:** LPS[D] tại **04:48**, giá 3997.2, phase ghi là **D**. Nhưng Phase D thật là 14:15 → 14:39, và SOS ở 14:15.
- **Đúng phải là:** LPS[D] theo định nghĩa là "nhịp hồi retest **sau** SOS/SOW". Nhãn này nằm **9 giờ 27 phút trước** SOS, và theo bảng phase nó rơi vào giữa Phase B (bar 77087-77828). Một điểm không thể vừa thuộc Phase B trên timeline vừa mang nhãn [D].
- **Dấu hiệu quyết định trên chart:** đọc index.json — LPS[D] ở 04:48 nhưng Phase D bắt đầu ở 14:15. Trên ảnh, nhãn LPS[D] nằm ở giữa chart, sát biên chính trên 3994.2, trong khi nhãn SOS/Phase D nằm dồn hết ở góc phải.
- **Nghi phạm trong thuật toán:** logic gom LPS[D] (mục 7: "nhịp hồi về loanh quanh biên vừa phá, trong 20 tick") quét theo **mức giá** mà không chặn theo **thời gian** — bất kỳ nến nào chạm vùng biên ±20 tick đều thành ứng viên, kể cả nến xảy ra trước SOS. Phải chặn cứng: chỉ xét các nến có index > index của SOS.

### 2. Biên chính bị giá bỏ lại từ 05:40 — nửa sau range không còn khung — luật vi phạm: L3 + lỗi A
- **Thuật toán gắn:** biên chính 3955.4 - 3994.2 (38.8 giá), cố định. Biên phụ trên 4051.8.
- **Đúng phải là:** biên chính cố định là **đúng luật** L3 — máy không kéo biên, điểm này ghi nhận. Nhưng hệ quả là: từ khoảng 05:40 trở đi giá **đóng cửa hẳn trên 3994.2 và không bao giờ quay lại**, dao động suốt 8 tiếng trong dải 4020-4060. Nghĩa là 700 nến cuối của "Phase B" diễn ra **hoàn toàn ngoài biên chính**. Một vùng cân bằng mà giá không còn ở trong đó thì nó đã hết vai trò làm range.
- **Dấu hiệu quyết định trên chart:** đường "biên CHINH tren 3994.2" nằm ở khoảng 1/3 dưới chart; toàn bộ hành động giá từ giữa chart sang phải nằm **phía trên** đường đó. Biên phụ trên 4051.8 (nét đứt) mới là cái đang bao giá — nhưng biên phụ theo L3 chỉ là "cực trị xa nhất một thế lực đã cố phá range", không phải biên làm việc.
- **Nghi phạm trong thuật toán:** không có guard "giá đã bỏ hẳn biên chính". Mục 8 chỉ có 2 guard huỷ range (cao > 3.5%, dài > 2500 nến), cả hai đều không bắn. Đề nghị guard mới: nếu N nến liên tiếp (vd 100) đóng cửa ngoài biên chính mà **chưa có SOS/SOW**, thì cú phá đó phải được xử lý (thành SOS thật, hoặc đóng range) — không được để range treo với giá nằm ngoài suốt 700 nến.

### 3. Phase B dài 742 nến / 89% range — mất tỉ lệ — luật vi phạm: L9 (đúng chiều nhưng thái quá) + L8
- **Thuật toán gắn:** A=34, **B=742**, C=12, D=25, E=21. Phase B chiếm 89% range.
- **Đúng phái là:** L9 nói B là phase dài nhất — về thứ tự thì máy đúng. Nhưng 742 nến mà chỉ ghi được **đúng 1 sự kiện** (mSOS ở 08:05) là dấu hiệu máy đã **mù suốt 12 giờ**. Đọc trên ảnh, trong đoạn B đó có ít nhất 2 cấu trúc riêng biệt: một cú sụp về 3970 rồi hồi (03:00-05:00), và một cú bứt dựng đứng từ ~4000 lên 4045 ở **05:40-06:00** (thấy rõ trên ảnh là một chân tăng gần thẳng đứng). Cú bứt đó chính là SOS thật của cấu trúc này — nó đóng cửa vượt biên chính 3994.2 và giữ được vĩnh viễn.
- **Dấu hiệu quyết định trên chart:** chân tăng dựng đứng ở ~05:40 trên ảnh, kèm cụm thanh volume nổi bật trên panel dưới, đưa giá từ ~4000 lên ~4045 và không bao giờ trả lại.
- **Nghi phạm trong thuật toán:** điều kiện SOS đòi **3 nến liên tiếp đóng cửa vượt biên PHỤ thêm ≥30 tick với thân ≥45%**. Biên phụ trên lúc đó đã bị mSOS đẩy lên cao, nên cú bứt thật không "vượt biên phụ" và bị bỏ qua. Đây là tác dụng phụ của L3 ("SOS phải bứt qua biên phụ"): một cú thọc râu sớm nới biên phụ lên cao rồi **khoá luôn** khả năng ghi nhận SOS thật sau đó. Cần cho phép SOS xác nhận qua biên **chính** khi số nến giữ ngoài biên đủ lớn.

### 4. Phase C 12 nến gán ngược vào 14:03 — bỏ qua cấu trúc thật ở 05:40 — luật vi phạm: L8
- **Thuật toán gắn:** LPS[C] tại 14:03 (giá 4039.5), Phase C = 14:03 → 14:14, gán ngược từ SOS ở 14:15.
- **Đúng phải là:** L8 cho phép gán ngược Phase C từ SOS ("có Phase D rồi mới xác định được Phase C") — cơ chế đúng. Nhưng vì SOS bị neo trễ 8 tiếng (lỗi #3), Phase C bị đặt vào một nhịp test ở **4039.5** — mức nằm **45 giá trên** biên chính trên. Gọi một điểm cao hơn biên trên 45 giá là "Last Point of Support" của range 3955-3994 là mất liên hệ với chính cái range đó.
- **Dấu hiệu quyết định trên chart:** LPS[C] 4039.5 vs biên chính trên 3994.2 — lệch 45.3 giá, hơn cả chiều cao biên chính (38.8 giá).
- **Nghi phạm trong thuật toán:** hệ quả kéo theo của lỗi #3 (SOS neo trễ) + thiếu ràng buộc "LPS[C] phải nằm trong hoặc sát biên range". Cửa sổ gán ngược 60 nến lấy cực trị mà không kiểm khoảng cách tới biên.

### 5. SOS neo vào cây VSA 1.23× — luật vi phạm: mục 8 (Effort vs Result)
- **Thuật toán gắn:** SOS tại 14:15, giá 4061.2, **VSA 1.23×**, thân 0.51.
- **Đúng phải là:** VSA 1.23× chỉ nhúc nhích trên trung bình — không thoả "volume tăng đều" của định nghĩa SOS. So sánh: cây climax cùng range có VSA **7.11×**. Trên panel volume, cụm thanh vàng rõ nhất của nửa sau chart nằm ở khoảng **14:10-14:20**; máy nên hồi tố vào cây cao nhất trong cụm đó.
- **Dấu hiệu quyết định trên chart:** 1.23× so với 7.11× của climax cùng range — chênh gần 6 lần nỗ lực.
- **Nghi phạm trong thuật toán:** cùng nghi phạm lỗi B như bài #31 và #33 — cửa sổ hồi tố quá hẹp. Đây là lần tái xuất thứ 3 trong lô.

### 6. mSOS 4051.8 với VSA 1.29× thân 0.12 — nới biên phụ bằng một cây râu — luật vi phạm: L3 + lỗi H
- **Thuật toán gắn:** mSOS tại 08:05, giá 4051.8, VSA **1.29×**, thân **0.12**. Chính điểm này định ra biên phụ trên 4051.8.
- **Đúng phải là:** thân 0.12 = nến gần như toàn râu, VSA 1.29× = volume tầm thường. Lỗi H định nghĩa mSOS là "thăm dò **mạnh** mà không phá được"; cây này không mạnh ở bất kỳ chiều nào. Đúng vai của nó chỉ là **UA** (test nhẹ) — hoặc không ghi gì.
- **Dấu hiệu quyết định trên chart:** thân/biên độ 0.12 với VSA 1.29×. Nếu ngưỡng "thăm dò NHẸ" là "< 15 tick **và** VSA < 3.3×" thì cây này thoả VSA nhưng độ sâu vượt 15 tick nên bị đẩy lên mSOS — tiêu chí "hoặc" đang cho một cây râu leo lên hạng mSOS.
- **Nghi phạm trong thuật toán:** bảng phân loại mục 5.1 dùng "sâu ≥ max(15 tick, 15% chiều cao) **hoặc** VSA ≥ 2.2×". Với chiều cao range 38.8 giá thì 15% = 5.8 giá; cây râu thọc 5.8 giá là chuyện thường. Nên thêm điều kiện thân nến tối thiểu (vd ≥ 0.45 như đã dùng cho SOS/SOW) trước khi cho một cú thăm dò lên hạng mSOS/mSOW — vì chính nó nới biên phụ và khoá SOS thật (lỗi #3).

## Đạt
- **Điều kiện mở range (L1) — tốt nhất cả lô:** MOVE giảm **60.1 giá / 108 nến**, hiệu suất 0.38; climax 01:07 có VSA **7.11×**, biên độ nến **25.6 giá**, thân 0.86, volume 2097 so với nến trước 789. Đây là một Selling Climax thật, không phải cây nhiễu phiên Á. Cây climax là đáy 3955.4 và giá **không bao giờ quay lại dưới mức đó** trong suốt 833 nến — climax chặn move thành công, đúng L1.
- **Phase A đọc đúng L2:** 3 lần đổi hướng rõ — SC 3955.4 (01:07) → AR 3994.2 (01:29) → ST[A] 3979.4 (01:40). Phase A dài 34 nến, kết thúc đúng tại ST[A]. ST[A] ở 3979.4 lùi 14.8 giá từ AR = **38% chiều cao**, nằm ở nửa dưới range, hướng về phía climax — đây là ST[A] **đúng nhất trong cả 5 bài** của lô.
- Biên chính cố định, không bị kéo theo giá suốt 833 nến. Đúng L3 (dù sinh ra hệ quả ở lỗi #2).
- Biên phụ đúng 1 cái mỗi bên, không spam. Đúng L3.
- **Tên "Tích luỹ" đúng L4** và lần này khớp thực tế: origin SC (move giảm 60 giá) + phá lên thật, giá kết thúc ~4045 tức **cao hơn biên trên 50 giá**. Cú phá này giữ được — khác hẳn #31 và #32.
- Phase C (12 nến) ngắn nhất, Phase B dài nhất — đúng thứ tự L8 và L9.
- LPS[C] và LPS[D] mỗi cái đúng 1 điểm, không vẽ vùng. Đúng L7.

## Kết luận cấu trúc
Nếu là tôi: **vẽ range ở đây nhưng kết thúc nó ở ~06:00, không kéo tới 15:00**. Phase A (01:07-01:40) và biên chính 3955.4-3994.2 đúng. Cú bứt dựng đứng ở 05:40 lên 4045 mới là SOS thật; retest nhẹ sau đó là LPS[D]; range đóng khoảng 06:30 với chiều dài ~320 nến. Cả đoạn 06:30 → 15:00 giá dao động 4020-4060 là một **range MỚI** (tái tích luỹ ở mức cao hơn) — đúng như mục 13.3 điểm 1 đã tự nhận: máy chỉ theo dõi một range một lúc nên phải nhét 2 vùng đấu giá vào 1 khung, và cái giá phải trả là Phase B 742 nến cùng 4 nhãn sai vị trí.
