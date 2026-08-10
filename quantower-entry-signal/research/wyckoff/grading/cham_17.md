# Chấm bài #17 — Chưa rõ (SC) (ACC?) · 2026-05-12 13:16 → 17:24 (226 nến M1)

**Điểm: 2/10** — Phase A vẽ đẹp nhất cả lô, rồi hỏng hoàn toàn từ Phase B: một cú sụp 42 giá kéo 80 nến ngoài biên bị gọi là "mSOW", biên phụ đứng yên ở 4714.5 trong khi giá đã xuống 4680.

## Lỗi (nặng → nhẹ)

### 1. Biên phụ dưới 4714.5 trong khi cực trị thật là ~4680 — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ dưới **4714.5** (nét đứt), tỉ lệ biên phụ/chính 1.37×.
- **Đúng phải là:** L3 định nghĩa biên phụ = **cực trị xa nhất mà một thế lực đã tạo ra khi cố phá range gốc**. Cú sụp 15:07-15:15 xuống tận **~4680** (đọc từ trục giá trên ảnh, đáy nến nằm dưới mức 4690.2) → biên phụ dưới phải là ~4680, thấp hơn nhãn hiện tại **34 giá**.
- **Dấu hiệu quyết định trên chart:** đường nét đứt 4714.5 nằm **cao hơn cả một khối nến khổng lồ** kéo dài từ 15:00 tới 16:30. Nhìn ảnh là thấy ngay biên phụ vẽ sai.
- **Nghi phạm:** biên phụ bị đóng băng trong lúc một cú thăm dò đang `C_pending` (cơ chế v6, mục 5.0) và chỉ được nới **một lần** sau khi biết kết cục — nhưng ở đây kết cục bị phán sai (thành mSOW) nên mức nới lấy sai điểm.

### 2. Cú sụp 42 giá / ~80 nến ngoài biên bị hạ thành mSOW — luật vi phạm: L5 + mục 5.1
- **Thuật toán gắn:** mSOW 15:10 tại 4712.6, VSA **10.51x** (cây to nhất range).
- **Đúng phải là:** giá thủng biên chính dưới (4722.5) từ 15:07 và **đóng cửa dưới biên liên tục tới ~16:30** — tức khoảng 80 nến ngoài biên, sâu 42 giá = **gấp đôi chiều cao range (21.9 giá)**. Theo L5 đây là **phá THẬT (SOW)**, không phải Spring cũng không phải Shakeout: "đóng cửa hẳn ngoài biên và các nến sau đủ mạnh giữ nó ở ngoài".
- **Dấu hiệu quyết định:** điều kiện "ở ngoài quá 40 nến VÀ ≥60% nến đóng ngoài biên" (mục 5.1) rõ ràng đã thoả, mà nhãn vẫn không lên SOW.
- **Nghi phạm:** đây là ca người dùng hỏi ở mục 3 — bản vá 13.1c (`edge` + `fail_tol` 30 tick) **CHƯA cứu được**. Cần soi lại nhánh nào của `B_brk` đưa cú này về `_demote_shock`.

### 3. Nhãn SOW cuối cùng đặt vào cây VSA 0.39x, cao hơn đáy thật 34 giá — luật vi phạm: mục 5.1 (nhãn hồi tố về cây phá thật)
- **Thuật toán gắn:** SOW 16:59 tại 4714.3, VSA **0.39x**.
- **Đúng phải là:** cây phá thật là 15:10 (VSA 10.51x). Nhãn "phá vỡ" nằm trên một nến volume rác, muộn **109 phút**, và ở mức giá cao hơn đáy đã đi 34 giá.
- **Dấu hiệu quyết định:** đây chính là **lỗi B của vòng v4 tái xuất nguyên vẹn** (nhãn SOS/SOW rơi vào nến VSA 0.30-0.69x trong khi cây phá thật 4-10x).

### 4. Cú "SOW" bị vô hiệu ngay sau đó mà range vẫn đóng như hoàn tất — luật vi phạm: L10 + lỗi F (mục 7)
- **Thuật toán gắn:** LPSY[D] 17:06 tại **4722.2** — cách biên chính dưới (4722.5) đúng **3 tick**.
- **Đúng phải là:** L10 đòi retest phải **GIỮ được ở ngoài biên**. Trên ảnh, ngay sau LPSY[D] giá đi thẳng LÊN, vượt hẳn 4722.5 và leo tới 4740. Cú phá bị vô hiệu → phải hạ cấp mSOW, trả dải phase về B, **không** đóng range ở Phase D.
- **Nghi phạm:** ngưỡng "lùi hẳn qua biên chính 30 tick" — giá lùi qua đúng lúc range đã chuyển sang `superseded` nên nhánh vô hiệu không còn chạy.

### 5. Thiếu hẳn Phase C — luật vi phạm: L8
- Dải phase: A(45) → B(156) → **D(26)**. Không có C. Range có SOW mà không gán ngược được Phase C.

### 6. Không đặt tên dù đã có SOW + Phase D — luật vi phạm: L4
- Tiêu đề "Chưa rõ (SC) (ACC?)". Origin SC + hướng phá xuống → phải là **Tái phân phối**, không phải "(ACC?)". Ghi "(ACC?)" là gợi ý ngược hẳn với cái chart đang thể hiện.

### 7. MOVE mở range chỉ dài bằng chính chiều cao range — L1 (nhẹ)
- MOVE 23.6 giá / 23 nến, biên chính 21.9 giá. "Nguyên nhân" trước range chỉ bằng 108% "kết quả" — mỏng, nhưng vẫn qua ngưỡng 8× ATR. Ghi nhận, không tính lỗi nặng.

## Đạt
- **Nhãn climax: ĐẠT — trường hợp tốt nhất trong lô.** SC đặt **đúng tại nến mở range** (13:16), VSA 6.34x, volume 59 (cao nhất vùng), biên độ 5.2 giá, và đúng là đáy chặn move. Không lệch nến nào.
- **Phase A (L2): ĐẠT tốt.** SC → AR (4744.4) → ST[A] 14:00 tại **4719.1** — thủng nhẹ 3.4 giá dưới climax, VSA **4.71x**, retrace **115%** khoảng AR↔climax. Đây đúng là cú test lại vùng climax, không lửng giữa range. Ngưỡng 0.55 chạy đúng ở ca này.
- **Biên chính (L3): ĐẠT**, cố định 4722.5-4744.4.
- **Tỉ lệ B dài nhất (L9): ĐẠT** (156/226 nến).
- **ST[B] 14:31 tại 4721.2:** đúng vai test nhẹ biên dưới, VSA 0.55x (volume co lại) — nhãn hợp lý.
