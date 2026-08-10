# Chấm bài #50 — Tích lũy (ACC) · 2026-07-09 04:03 → 05:11 (68 nến M1)

**Điểm: 3/10** — chuỗi Spring → SOS → LPS[D] đọc đúng hướng, nhưng Phase A không tồn tại (AR đứng TRƯỚC climax) và tỉ lệ phase lộn ngược.

## Lỗi (nặng → nhẹ)

### 1. Phase A chỉ 1 nến, AR xảy ra TRƯỚC climax, ST[A] trùng đúng nến climax — luật vi phạm: L2
- **Thuật toán gắn:** AR tại **04:00** (4073.6), SC? tại **04:03** (4068.4), ST[A] tại **04:03** — cùng nến, cùng giá, cùng VSA 2.39x với SC?. Phase A = **1 nến**.
- **Đúng phải là:** L2 đòi đúng 3 lần đổi hướng theo thứ tự climax → AR → ST[A]. Ở đây thứ tự bị đảo (AR trước climax 3 nến) và ST[A] không phải một sự kiện riêng — nó là chính cây climax. Không có CHoCH nào cả → Phase A **chưa hoàn thành**, range không đủ điều kiện mở.
- **Dấu hiệu quyết định trên chart:** ba nhãn AR (yếu) / SC? / ST[A] xếp chồng nhau trong đúng 4 nến, vạch Phase A và vạch Phase B gần như trùng nhau ở bên trái ảnh.
- **Nghi phạm trong thuật toán:** nhánh `WySpawnSidewaysRange` — range con sinh từ cú phá kế thừa pivot AR của range cha rồi mới đặt mốc climax, nên chỉ số AR nhỏ hơn chỉ số climax (đúng đầu mục "Range con sinh từ SIDEWAYS kế thừa sai index Phase A" ghi ở 13.1b, vẫn còn nguyên).

### 2. Phase C (43 nến) dài gấp 3 Phase B (14 nến) — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A 1n · B 14n · **C 43n** · D 8n · E 3n. Phase C chiếm 63% cả range.
- **Đúng phải là:** B phải là phase dài nhất, C ngắn nhất. Ở đây đúng lộn ngược cả hai.
- **Dấu hiệu quyết định:** vạch tím "Phase C (43n)" trải từ 04:18 tới 05:00 — nguyên đoạn giá đi ngang 4066–4074, tức chính là Phase B thật.
- **Nghi phạm:** sau khi bỏ ràng buộc "đúng nửa range" ở v7.1, không còn gì kẹp độ dài Phase C; Spring xảy ra quá sớm (nến thứ 15 của range) nên toàn bộ phần còn lại bị nhét vào C.

### 3. Biên phụ trên 4085.3 do chính cú phá THÀNH CÔNG tạo ra — luật vi phạm: L3
- **Thuật toán gắn:** biên phụ trên 4085.3, tỷ lệ biên phụ/chính **3.62×** (biên chính chỉ 5.2 giá).
- **Đúng phải là:** biên phụ = cực trị xa nhất của một thế lực **đã cố phá range và thất bại**. Mức 4085.3 chỉ đạt được trong Phase E, sau khi SOS đã thắng — nó là kết quả của cú phá, không phải một cú thăm dò thất bại. Range này lẽ ra **không có biên phụ trên**.
- **Dấu hiệu quyết định:** trong toàn bộ Phase A–C giá không lên quá 4074; nét đứt trên 4085.3 lơ lửng trên đầu, không nến nào chạm.
- **Nghi phạm:** nhánh nới `out_edge` vẫn chạy sau khi SOS đã bắn — cần đóng băng biên phụ tại thời điểm chốt SOS/SOW.

### 4. SOS không bứt qua biên phụ — luật vi phạm: L3 (SOS mạnh phải đóng cửa qua biên phụ)
- SOS tại 05:01 giá 4079.1, trong khi biên phụ trên báo 4085.3. Theo đúng luật của chính tài liệu, cú này chưa đủ tư cách "SOS mạnh". Lỗi này là hệ quả trực tiếp của lỗi #3 — sửa #3 thì hết.

### 5. Range không có cao trào thật — luật vi phạm: L1 (điều kiện CẦN)
- Phiếu ghi rõ "SINH TU CU PHA, khong co climax that", nhãn `SC?`. Không có MOVE nào được đo (phiếu không có dòng MOVE). Climax bar VSA 2.39x, biên độ 1.3 giá — nhỏ hơn cả nến -1 (2.01x). Đây là đoạn đi ngang trong đuôi cấu trúc trước, không phải một vùng đấu giá mới.

## Đạt
- Spring tại 04:18 (4066.5) đúng loại theo L5: thò xuống dưới biên chính, quay lại trong range nhanh, và được xác nhận (`confirmed`).
- SOS tại 05:01 neo đúng cây phá thật: **VSA 8.67x**, thân 0.67 — chính là thanh vàng cao nhất panel volume. Đây là chỗ v7.1 làm tốt hơn hẳn bài #49.
- LPS[D] tại 05:04 là một điểm duy nhất (L7), nằm đúng nhịp hồi sau SOS và giữ được trên biên chính trên 4073.6 → L10 thoả.
- Tên range (Tích luỹ) khớp origin SC + phá lên (L4).
