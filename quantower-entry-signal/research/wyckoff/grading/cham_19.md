# Chấm bài #19 — Chưa rõ (BCLX) (DIST?) · 2026-05-20 15:16 → 2026-05-21 01:56 (421 nến M1)

**Điểm: 3/10** — khung range và Phase A/B đọc được, nhưng ST[A] rơi giữa range, Phase C dài hơn cả A lẫn D, nhãn SOS neo vào cây 0.97× và cuối cùng range bị bỏ tên trong khi thực tế nó là một cấu trúc **Phân phối** rõ.

## Lỗi (nặng → nhẹ)

### 1. ST[A] không test lại vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 15:40 tại 4576.4.
- **Đúng phải là:** ST[A] phải là cú quay về **phía climax 4591.2** rồi bị chặn. 4576.4 nằm ở (4576.4−4565.6)/25.6 = **42% chiều cao range** — đúng giữa vùng, đây là một cái ngọ nguậy, không phải test.
- **Dấu hiệu quyết định trên chart:** khoảng cách từ ST[A] tới climax (14.8 giá) **lớn hơn** khoảng cách tới AR (10.8 giá) — test mà xa mức cần test hơn xa mức xuất phát thì không phải test.
- **Nghi phạm trong thuật toán:** `STA_MIN_AR_FRAC` vừa nâng 0.2 → 0.4 (vá v7 #2) nhưng ca này đo được **0.42** — lọt qua sát ngưỡng. Ngưỡng đặt sai chiều: phải ràng buộc **khoảng cách còn lại tới climax** (vd ≤ 0.35× chiều cao), không phải "hồi được bao nhiêu từ AR".

### 2. Phase C dài 53 nến — dài hơn cả Phase A (25) và Phase D (26) — luật vi phạm: L8
- **Thuật toán gắn:** Phase C 00:27 → 01:24, neo bằng LPS[C] gán ngược.
- **Đúng phải là:** Phase C là phase NGẮN NHẤT. Nếu LPS[C] gán ngược cách cú phá 53 nến thì nó không phải "tín hiệu đầu tiên cho thấy giá sắp phá biên kia" — đó chỉ là một đáy bất kỳ trong Phase B.
- **Dấu hiệu quyết định trên chart:** nhìn dải phase — Phase C (53n) rộng gấp đôi Phase D (26n).
- **Nghi phạm trong thuật toán:** vá v7 #3 nới cửa sổ gán ngược 0.5× → 0.8× độ dài Phase B (318 nến → trần 60 nến) đã **quá tay**: giờ luôn lấy được pivot ở tận đầu cửa sổ 60 nến. Phải thêm trần tuyệt đối kiểu `len(C) ≤ min(len(A), len(D))`.

### 3. Nhãn SOS rơi vào cây VSA 0.97× trong khi cây phá thật 4.29× nằm ngay trước — luật vi phạm: mục 5.1 (nhãn hồi tố)
- **Thuật toán gắn:** SOS 01:25 tại 4600.3, VSA **0.97×**; cây 01:15 VSA **4.29×** lại mang nhãn mSOS.
- **Đúng phải là:** SOS neo hồi tố vào cây 01:15 (4.29×) — đó là cây bứt thật, đúng hướng, đóng cửa vượt biên chính 4591.2.
- **Dấu hiệu quyết định trên chart:** trên panel khối lượng, thanh vàng cao nhất của cả đoạn phá nằm ở 01:15, không phải 01:25.
- **Nghi phạm trong thuật toán:** cửa sổ quét hồi tố bắt đầu **sau** khi cú mSOS trước đó đã bị chốt/hạ cấp, nên cây thật bị "khoá" vào nhãn mSOS và không còn ứng viên cho SOS.

### 4. mSOS ghi Phase = B trong khi mốc thời gian nằm giữa Phase C — lỗi nhất quán bảng
- mSOS 01:15 nằm trong khoảng Phase C (00:27–01:24) nhưng cột Phase ghi `B`. Trường phase của sự kiện không được cập nhật khi dải phase bị vẽ lại.

### 5. Range không được đặt tên (superseded) trong khi cấu trúc thật là Phân phối — luật vi phạm: L4
- **Thuật toán gắn:** `superseded`, tiêu đề "Chưa rõ (BCLX) (DIST?)".
- **Đúng phải là:** BCLX chặn move tăng 81.5 giá → cú vượt lên 4600–4605 chỉ giữ được ~45 nến rồi giá xuyên thẳng cả range xuống 4564 (xem chart bài #20) → đó là **UTAD**, range là **PHÂN PHỐI**. Máy đọc thành SOS + Phase D + LPS[D] (tức tái tích luỹ) rồi né việc đặt tên bằng cách chuyển sang range con.
- **Nghi phạm trong thuật toán:** cơ chế SIDEWAYS (mục 5.4) cắt cấu trúc làm hai, range cha mất tên vĩnh viễn — chính là ca "range con bị chết/không kết luận thì cha treo `superseded`" đã ghi ở mục 5.4 nhưng chưa xử lý.

### 6. Nhãn climax bỏ sót cây nỗ lực lớn nhất — nhẹ
- Cây 15:15 có VSA **7.69×**, biên độ 22.2 giá, thân 0.84 — chính nó mới là cây cao trào; cây 15:16 (4.45×) chỉ là cây làm đỉnh. Cửa sổ cụm climax chỉ quét **tiến**, không quét lùi, nên không thấy cây mạnh hơn liền trước.

## Đạt
- L1: MOVE 81.5 giá / 63 nến, hiệu suất 0.44, climax là đỉnh cao nhất cửa sổ — mở range hợp lệ.
- L3: biên chính 4565.6–4591.2 đúng bằng AR + climax, không trượt theo giá; tỷ lệ biên phụ 1.36× hợp lý.
- L9: Phase B 318/421 nến — đúng là phase dài nhất.
- **Vá v7 #1 chạy đúng:** er=1.32 ≥ 1 → ghi "vùng hấp thụ NGHI VẤN"; không còn hard-code.
- Phase D có LPS[D] một điểm duy nhất (L7).
