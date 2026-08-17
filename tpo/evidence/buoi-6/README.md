# Buổi 6 — Bằng chứng BALANCE vs SAU BALANCE

Symbol: **GCZ26:XCEC** (dxFeed) · Chart TPO Daily + Volume Analysis. Ảnh: `image.png`.

## Mức 1 — ca "vừa ra khỏi balance" (8/3 → 8/5/2026)

| Phiên | TPO | VAH | VAL | POC | RF | Vai trò |
|---|---|---|---|---|---|---|
| 8/3/2026 | 473 | 4125 | 4102 | 4110 | **-2** | balance, đấu giá dồn cạnh trên (hình P) |
| 8/4/2026 | 524 | 4137 | 4104 | 4117 | **-1** | balance kéo dài — VA **chồng** 8/3 (4104–4125); phá lên ~4155 cuối ngày rồi hồi lại |
| 8/5/2026 | 713 | 4340 | 4221 | 4307 | **+24** | **SAU BALANCE** — VA rời hẳn range cũ (VAL 4221 > VAH 4137 cũ, gap ~84 điểm) |

**Phán đoán của người học (ghi trước):**
1. "TPO này đấu giá ở cạnh trên" (8/3)
2. "Giá phá rồi hồi lại vào cuối ngày — nhìn màu heatmap để biết đc là cuối ngày" (8/4)
3. "Phần bụng này thể hiện TPO tiếp tục duy trì đấu giá từ hôm qua" (8/4)
4. "Giá sau khi hồi thì tăng mạnh" (8/5)

**Chấm: ĐẠT.** Ca hợp lệ và đọc đúng cơ chế. Hai điểm làm tốt hơn yêu cầu đề:
- Nhận ra **balance kéo dài 2 phiên** qua VA chồng nhau (8/3 4102–4125 ∩ 8/4 4104–4137), thay vì chỉ lấy
  1 profile đơn lẻ — đây là cách đọc balance đúng hơn.
- Dùng **màu = bracket/thời gian** (luật vừa chốt ở Buổi 2) để xác định cú phá xảy ra **cuối ngày** rồi hồi
  lại. Đúng công dụng của luật đó.

**Số xác nhận thêm (Claude đọc trên ảnh):** **Rotation Factor** = -2 · -1 · **+24**. RF quanh 0 ở 2 phiên
balance rồi nhảy vọt +24 đúng phiên break = chữ ký "sau balance ⇒ trend" bằng con số, không chỉ bằng mắt.

**⚠️ Ghi chú:** 8/3 là hình **P** (đã chấm ở Buổi 2), không phải D — đề gốc yêu cầu D/chữ nhật. Chấp nhận
được vì cặp 8/3+8/4 hợp thành một vùng balance thật; nhưng nếu tìm được ca D/chữ nhật thuần thì sạch hơn.

## Còn thiếu — nửa sau của bài

Chưa kiểm được vế **delta** (ảnh TPO không hiện delta từng phiên, chỉ có RF):
- Leg đầu của cú break 8/5 có **tăng mà delta âm** không?
- Nếu có, sau đó **có squeeze** (delta bật dương, giá bay tiếp) không?

→ Cần chụp thêm chart **delta/footprint** cho phiên 8/5 để đóng bài.
