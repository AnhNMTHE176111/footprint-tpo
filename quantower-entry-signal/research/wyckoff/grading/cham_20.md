# Chấm bài #20 — Phân phối (DIST) · 2026-05-21 01:41 → 02:15 (27 nến M1)

**Điểm: 3/10** — **Không nên vẽ range ở đây.** 27 nến, biên 7.8 giá (0.17%), Phase A dài **1 nến** — đây là nhiễu, không phải một vùng đấu giá. Cơ chế "sinh từ cú phá" hợp lệ, nhưng nó không cho phép hạ chuẩn tới mức này.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn để tồn tại — luật vi phạm: L1 + tiêu chí khung của giảng viên (Ca #4/#6/#19 nguồn 7.pdf)
- **Thuật toán gắn:** một TR "Phân phối" đủ Phase A→E trong **27 nến M1**, biên chính **7.8 giá = 0.17%**.
- **Đúng phải là:** đã có mốc cảnh báo "TR M1 chỉ 60-100 nến với đủ A→E thì phải nghi là nhiễu" — bài này chỉ **27 nến**, tức chưa tới một nửa mức đã bị coi là đáng nghi. Vùng 01:41–02:15 trên chart chỉ là **một chặng nghỉ giữa cú rơi** từ 4605 xuống 4564: giá vào chặng ở 4605, ra ở 4592, và tiếp tục rơi thẳng. Đây là "giai đoạn xu hướng bị cắt ngang" (THEORY §2.3 phân biệt giai đoạn xu hướng vs giai đoạn đi ngang), không phải cân bằng cung-cầu.
- **Dấu hiệu quyết định trên chart:** bảng 12 nến quanh climax có volume 1, 2, 2, 1, 1, 2, 3, 4 — **thanh khoản gần như bằng 0**; nhiều nến thân=0 (than/bien = 0.00). Không có ai đấu giá ở đây cả.
- **Nghi phạm trong thuật toán:** nhánh "range sinh từ cú phá" không kế thừa các guard tối thiểu (số nến tối thiểu, % biên tối thiểu, thanh khoản tối thiểu) đang áp cho range sinh từ climax. Thêm gate: `so_nen >= 60` và `bien_chinh% >= ~0.3%` và `volume TB trong range >= x% TB 20 nến`.

### 2. Biên chính trên lấy theo ST[A] chứ không theo mức climax — luật vi phạm: L3
- **Thuật toán gắn:** biên CHÍNH = 4597.6 (AR) – **4605.4**; nhưng 4605.4 là giá của **ST[A]** (01:41), còn climax BCLX? ở **4603.8** (01:31).
- **Đúng phải là:** biên chính trên = **mức climax 4603.8**. ST[A] vượt qua mức climax thì theo L3 nó tạo **biên PHỤ trên 4605.4** (nét đứt), không được thay chỗ biên chính. Trên ảnh hiện chỉ có biên phụ **dưới** (4595.0); phía trên thiếu hẳn nét đứt.
- **Dấu hiệu quyết định trên chart:** 4605.4 > 4603.8 đọc thẳng từ bảng sự kiện.
- **Nghi phạm trong thuật toán:** khi range sinh từ cú phá, mức biên đang được lấy = `max/min của các nhãn Phase A` thay vì `mức climax` cố định. Đây đúng là lỗi "biên bị kéo theo giá" mà L3 cấm.

### 3. Phase A = 1 nến, không có 3 lần đổi hướng — luật vi phạm: L2
- **Thuật toán gắn:** Phase A = 01:41 → 01:41 (**1 nến**), chứa duy nhất ST[A]; BCLX? (01:31) và AR (01:33) nằm **trước** khi range bắt đầu.
- **Đúng phải là:** Phase A = một CHoCH = 3 lần đổi hướng, phải **bao trọn** climax → AR → ST[A]. Range phải bắt đầu ở nến climax (01:31), Phase A = 01:31→01:41 = 11 nến. Việc mốc bắt đầu range trễ hơn cả 2 sự kiện của chính Phase A khiến biểu đồ tự phủ định mình: hai nhãn nằm ngoài khung vạch tím.
- **Dấu hiệu quyết định trên chart:** trên ảnh, nhãn `BCLX?` và `AR (yếu)` nằm hẳn bên **trái** vạch tím "Phase A (1n)".
- **Nghi phạm trong thuật toán:** `range.start` được đặt bằng thời điểm cú phá / thời điểm ST[A], không đặt bằng thời điểm climax.

### 4. Thiếu hẳn Phase C — luật vi phạm: L8
- **Thuật toán gắn:** A → B → **D** → E, nhảy qua C.
- **Đúng phải là:** đây đúng là "case khó" của L8 (không có UTAD, chỉ có LPSY[C]) → phải **gán ngược từ SOW**. SOW ở 02:03; nhịp hồi cuối cùng trước nó (01:59–02:02, giá bò lại ~4598–4599 sau khi mSOW 01:56 đã chọc 4595.0) chính là **LPSY[C]**. Phase C = 4 nến đó.
- **Dấu hiệu quyết định trên chart:** trên ảnh có rõ 2 nến hồi nhỏ ngay trước nhãn SOW, nằm dưới biên chính dưới 4597.6 — dạng "phục hồi yếu trên biên hẹp" = định nghĩa gốc LPSY (THEORY §4.1).
- **Nghi phạm trong thuật toán:** không có nhánh hồi tố "tìm LPSY[C] = swing-high cuối cùng trước SOW" khi không phát hiện được UTAD/shock.

### 5. Chỉ số nỗ lực/kết quả diễn giải NGƯỢC — luật vi phạm: THEORY §2.2 (lỗi ĐO bản chất)
- **Thuật toán in:** effort (VSA TB) = 1.25x, result (biên độ/ATR) = **6.76**, er = **0.18** → kết luận "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er = 0.18 nghĩa là **kết quả lớn gấp ~5,5 lần nỗ lực** — đây là "nỗ lực ÍT, kết quả NHIỀU", tức thị trường **rỗng thanh khoản** (giá trượt xa với volume tầm thường), hoàn toàn trái với "hấp thụ". Câu diễn giải bị hardcode (bài #21/#23/#24 er < 1 cũng in y hệt).
- **Nghi phạm trong thuật toán:** chuỗi kết luận nằm ngoài `if er > 1`; và tiêu chí chọn "nhịp nỗ lực/kết quả cao nhất" đang chọn nhịp có er **thấp nhất** — chọn sai chiều so sánh.

### 6. Bias test biên = +0 nhưng Phase B chỉ test biên dưới (lỗi ĐO)
- **Thuật toán in:** bias `+0` = "test CẢ HAI biên".
- **Đúng phải là:** trong Phase B (01:42–02:02) giá cao nhất chỉ ~4600 (nhìn cụm nến quanh 01:50), **không chạm lại biên trên 4605.4 lần nào**, còn biên dưới bị chọc (mSOW 4595.0). Bias đúng là **−1** (chỉ với tới biên dưới) — và đó là chỉ số duy nhất ủng hộ tên "Phân phối", nên đo sai ở đây là mất thông tin.
- **Nghi phạm trong thuật toán:** phép "chạm biên trên" đang tính cả nhãn ST[A] của Phase A (chính là cái tạo biên trên), tức đếm trùng một lần chạm thuộc phase khác.

### 7. Climax mang nhãn "BCLX?" với VSA 0.29x / biên độ 0.4 giá (trình bày + ngữ nghĩa)
- Dòng đầu phiếu ghi "climax mở range tại giá 4605.4, VSA=0.29x, biên độ nến=0.4 giá" nhưng dòng dưới lại ghi "nhãn climax mang VSA=1.15x" và bảng sự kiện đặt BCLX? tại 4603.8. **Ba con số cho cùng một sự kiện.** Dấu `?` là đúng (đã tự thú không có cao trào thật), nhưng phiếu cần in một cặp (nhãn, mức) rõ ràng thay vì trộn.

## Đạt
- **L4 — tên range:** move trước là tăng (giá bò từ 4571 lên 4605) + phá **xuống** thật → **Phân phối (DIST)** là đúng theo bảng 4 mẫu hình.
- **L3 (một phần):** biên phụ dưới 4595.0 = mSOW là cực trị xa nhất phía dưới, đúng 1 biên.
- **L10:** SOW 02:03 đóng cửa **dưới** biên phụ 4595.0 (giá 4592.1) và giá không quay lại — Phase E rời range đi tìm vùng giá mới (rơi tới 4564). Cú phá này đọc đúng.
- **Cơ chế BCLX? / "sinh từ cú phá"** được ghi rõ trên chart và trên phiếu — minh bạch, không giả vờ có cao trào.
- **SOT = none(n=0)** đúng: 17 nến Phase B không đủ để nói gì về lực đẩy (khớp THEORY §7 cần ≥3 nhịp).

## Cần hỏi người học
- Range "sinh từ cú phá" có được phép **bỏ** ngưỡng số nến / % biên tối thiểu không? Nếu có, thì mốc sàn là bao nhiêu — vì với 27 nến và volume 1-4 lot/nến thì mọi nhãn Wyckoff ở đây đều là đọc nhiễu.
