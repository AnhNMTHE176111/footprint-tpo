# Hấp thụ TẠI CÁC VÙNG của SessionZones + VWAP ngày/tuần — kết quả đo

**Script:** `research/hap-thu-tai-vung.py` · **Dữ liệu:** `fp_GC_XCEC_Time_20240801-20260819_748d9h`
(724.279 nến M1, 533 phiên; **loại 8 chỗ nối hợp đồng** và mọi cửa sổ 15 phiên chạm chỗ nối
⇒ còn **389 phiên** đủ điều kiện dựng vùng).

## Vùng lấy đúng định nghĩa trong repo, không tự bày ra
| Vùng | Nguồn |
|---|---|
| HVN ngày · HVN tuần (5 phiên) · HVN 3 tuần (15 phiên) | port `ProfileEngine.FindHvn`, cổng `MinHvnRatio = 2,5`, `MaxHvn = 3` |
| POC / VAH / VAL phiên trước | port `ProfileEngine.ValueArea(0.70)` |
| naked POC | POC phiên cũ chưa bị giá chạm lại |
| LVN ngày | đáy rỗng của profile phiên trước |
| VWAP ngày / VWAP tuần | cộng dồn trong phiên / neo đầu tuần |

Mọi vùng chỉ dùng dữ liệu **các phiên TRƯỚC** — không nhìn trước.

## Thước đo
Rào chắn đối xứng ±k×(trung vị biên độ 50 nến) tính từ giá đóng nến sự kiện, xem bên nào chạm trước
trong 60 nến. "Thuận" = đi theo hướng hấp thụ mong đợi. Nền chuẩn (nến ngẫu nhiên) = **49,9–50,0%**.
Ba họ sự kiện: **A** phá cực trị · **B** hấp thụ đúng nghĩa (không phá cực trị, biên độ ≤ trung vị,
đóng nửa trong) · **AB** mọi cụm khối lượng lớn + delta cực đoan.

## Kết quả chính (bán kính vùng ±2 giá, rào chắn ±2×)
| Họ | Vùng | n | thuận | z |
|---|---|---|---|---|
| AB | **VWAP ngày** | 1.784 | **52,9%** | **+2,46** |
| AB | **VWAP tuần** | 774 | **53,8%** | **+2,15** |
| AB | HVN tuần | 427 | 53,7% | +1,53 |
| AB | HVN ngày | 541 | 48,0% | −0,93 |
| AB | POC phiên trước | 664 | 49,1% | −0,44 |
| AB | naked POC | 103 | 46,5% | −0,69 |
| A | **HVN ngày** | 309 | **43,5%** | **−2,27** |
| A | HVN 3 tuần | 217 | 43,5% | −1,89 |
| A | **KHÔNG ở vùng nào** | 3.585 | **47,4%** | **−3,03** |
| B | **ở BẤT KỲ vùng nào** | 126 | **57,6%** | +1,71 |
| B | không ở vùng nào | 141 | 44,7% | −1,25 |

Bán kính ±1 giá, rào chắn ±1×: B ở bất kỳ vùng nào **63,5%** (n=67, z=+2,15); VWAP tuần AB 53,4%
(z=+1,36); VWAP ngày AB 51,7% (z=+1,00); HVN ngày A 46,6%.

## Đọc kết quả
1. **HVN — vùng chính của SessionZones và của hệ CORVEN — KHÔNG giúp hấp thụ đảo chiều.** Ngược lại:
   cụm phá cực trị **ngay tại HVN ngày** thì **đi tiếp** theo hướng phá (thuận chỉ 43,5%, z=−2,27).
   Khớp với kết luận cũ trong commit `811a57a`: HVN không phải mốc phản ứng.
2. **VWAP ngày và VWAP tuần là vùng duy nhất nghiêng ĐÚNG chiều hấp thụ** — 52,9% và 53,8%,
   tức hơn nền **+3 đến +4 điểm phần trăm**, và **cùng dấu ở cả 4 cách cắt**. Nhỏ, nhưng nhất quán.
3. **Hấp thụ đúng nghĩa ở bất kỳ vùng nào cho tỉ lệ cao nhất toàn bộ phép đo (57,6–63,5%)** —
   nhưng **n chỉ 67–126** nên chưa kết luận được. Đây là ô cần thu thêm dữ liệu, không phải ô để tin ngay.
4. **Mặt có bằng chứng mạnh nhất lại là mặt NGƯỢC với hấp thụ:** cụm phá cực trị **không ở vùng nào**
   đi tiếp theo hướng phá 52,6% (thuận 47,4%, n=3.585, z=−3,03).

## ⚠️ Cảnh báo phép so sánh nhiều lần
Bảng này gồm **~120 ô** (3 họ × 10 vùng × 2 bán kính × có/không). Ở mức đó, vài ô có |z| > 2 là
**chuyện bình thường do may mắn**. Không được lấy riêng một ô làm luật giao dịch.
Hai thứ đáng theo tiếp vì **nhất quán qua nhiều cách cắt**, không vì z đẹp:
**VWAP (thuận hấp thụ, nhẹ)** và **phá cực trị ngoài vùng (thuận đà phá, mạnh hơn)**.

## Việc nên làm tiếp
- Tăng n cho họ B tại VWAP: hạ nhẹ ngưỡng khối lượng/delta hoặc dùng thêm mã khác cùng dạng.
- Kiểm định tách đôi thời gian (2 năm chia 2 nửa) — luật nào chết ở nửa sau thì bỏ.
- Nếu muốn dùng ngay: đánh **theo hướng phá** khi cụm phá cực trị xảy ra **xa mọi vùng**, thay vì
  bắt đảo chiều.
