# Chấm bài #22 — Tích luỹ (ACC) · 2026-06-02 01:01 → 06:36 (335 nến M1)

**Điểm: 7/10** — vẽ đúng về căn bản, chỉ sửa hai nhãn: LPS[C] đặt sai phía, và AR bắt quá sớm nên biên chính trên hụt.

## Lỗi (nặng → nhẹ)

### 1. LPS[C] đặt tại 4526.9 — TRÊN biên chính trên, tức trong vùng đã phá — luật vi phạm: L8 + Ca #3 nguồn 4.pdf (nhầm vai LPS[C] / LPS[D])
- **Thuật toán gắn:** LPS[C] tại 03:53, giá **4526.9**, cao hơn biên chính trên (4521.6) **5.3 giá**, chỉ cách biên phụ trên (4530.0) 3.1 giá. VSA 0.40×.
- **Đúng phải là:** LPS[C] là **cú test cuối cùng trước** SOS, và trong tích luỹ nó phải là một điểm **đỡ** — đáy của nhịp hồi. Ở đây điểm được chọn nằm gần đỉnh vùng chứ không phải đáy nhịp hồi. Nhịp test đúng là đáy quanh 03:32–03:38 (nhìn trên ảnh: cú thụt về sát 4514 trước khi loạt nến xanh đẩy lên) — đó mới là "last point of support".
- **Dấu hiệu quyết định trên chart:** LPS mà đặt ở mức **cao hơn** biên trên thì nó không "hỗ trợ" gì cả; hơn nữa VSA 0.40× ở đó chỉ là một nến lặng giữa đợt tăng, không phải một cú test có ý nghĩa cung/cầu.
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #21 — nhánh "Phase C gán ngược nhìn lại 60 nến". Spec (mục 6) nói lấy "**đáy sâu nhất** nếu phá lên", nhưng số đọc được là 4526.9 — cao hơn mọi mức trong 60 nến trước đó theo hình. Hoặc cửa sổ 60 nến bị đo từ sai mốc, hoặc dấu so sánh min/max bị đảo. **Đáng kiểm code trực tiếp** — đây là lỗi có thể bị đảo dấu.

### 2. AR bắt tại nến +13, chốt biên trên 4521.6, trong khi giá sau đó ở lì trên mức này gần hết Phase B — luật vi phạm: L3
- **Thuật toán gắn:** AR (yếu) tại 01:14, 4521.6, VSA 1.88×, **thân 0.04** (gần như doji, một cây râu).
- **Đúng phải là:** chính thuật toán đã tự dán nhãn "(yếu)" — nhưng vẫn dùng đỉnh râu đó làm biên chính. Ca #5 nguồn 4.pdf: **mốc phase và biên phải neo giá đóng cửa, không neo bóng nến**. Neo đóng cửa thì biên trên rơi vào khoảng 4516–4517, và toàn bộ Phase B nằm trong biên gọn hơn nhiều.
- **Dấu hiệu quyết định trên chart:** thân/biên độ = **0.04** — đây là định nghĩa của một cây râu. Ngoài ra trên ảnh, đường "biên CHÍNH trên 4521.6" bị giá xuyên qua và ở lại phía trên suốt đoạn 03:20 → 04:11 mà không có nhãn nào ghi nhận — biên đó không mô tả được cấu trúc.
- **Nghi phạm trong thuật toán:** AR lấy `High` của nến pivot thay vì `Close`. Nhãn "AR (yếu)" hiện chỉ là cảnh báo hiển thị ("không đổi logic" — mục 4.1) — nên **có đổi logic**: AR yếu thì dùng close thay vì extreme.

### 3. Phase E 121 nến, dài gần bằng Phase B 154 nến — luật vi phạm: L9 (nhẹ)
- **Thuật toán gắn:** A=18, B=154, C=18, D=25, E=121.
- **Đúng phải là:** B vẫn là dài nhất — **đạt**. Nhưng E kéo 121 nến là do trần cứng, không do cấu trúc: nhìn ảnh, giá rời range lúc 04:11 và tăng thẳng một mạch tới 4570; Phase E đáng lẽ chốt sớm hơn nhiều khi đã đi đủ 1× chiều cao range (20.6 giá → chạm 4542 vào khoảng 05:10).
- **Nghi phạm trong thuật toán:** điều kiện chốt Phase E "đi thêm 1.0 × chiều cao range" đo bằng **biên chính** — nhưng nếu đo từ mốc SOS 4535.2 thì đích là 4555.8, giá chạm rất muộn. Nên đo từ **biên bị phá** chứ không từ giá cây SOS.

## Đạt
- **Điều kiện mở range (L1) — đạt tốt.** MOVE 18.3 giá / 29 nến / hiệu suất 0.59; climax là đáy tuyệt đối của cửa sổ (4501.0, thấp nhất bảng 12 nến); VSA 5.98×; đây là move giảm thật bị chặn thật.
- **Phase A (L2) — đạt.** Đủ 3 lần đổi hướng SC → AR → ST[A] (4511.4, nằm trong range, đúng là test lại vùng climax), kết thúc đúng tại ST[A]. 18 nến, gọn.
- **Tỉ lệ phase (L9, L8) — đạt.** Phase B 154 nến là dài nhất; Phase C 18 nến là ngắn nhất cùng Phase A. Đây là bài duy nhất trong lô 21–25 làm đúng cả hai luật tỉ lệ.
- **Tên range (L4) — đúng.** Origin SC + phá lên thật = Tích luỹ.
- **mSOW ở Phase B — gán đúng vai.** 01:52, 4492.3, VSA 2.40×: một cú thọc thủng biên chính dưới 8.7 giá rồi thất bại. Đúng là "cú phá thất bại", đúng là ở lại Phase B, đúng là nới biên phụ dưới. Đây chính là chỗ v4 hay gọi nhầm thành "DA test nhẹ" — **lỗi H đã hết**.
- **SOS neo đúng cây phá.** 04:11, VSA **4.32×**, thân 0.77, đóng cửa vượt cả biên phụ trên 4530.0. Đây là cây phá thật — **lỗi B đã hết ở bài này**.
- **Biên phụ đúng quy tắc:** mỗi bên 1 cái (4492.3 dưới từ mSOW, 4530.0 trên), là cực trị xa nhất. L3 đạt.
- **Phase D/E là CBR thật (L10) — đạt.** Phá 4530 → hồi nhẹ → giữ ngoài biên → đi tiếp tới 4570. Đúng khuôn.
