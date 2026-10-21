# Benzo Trader — tổng kết backtest vòng 1–2 (2026-10-21, agent chính)

Dữ liệu dùng để quyết định: **chỉ** `fp_GCZ26_XCEC_Time_20260723-20261021_90d` (65 phiên, QĐ-6).
TRAIN ≤ 2026-09-15 (40 phiên) · TEST từ 2026-09-16 (25 phiên). Chi phí 0,2 giá/lệnh. Nến chạm cả SL lẫn TP tính SL.

## Kết quả từng setup (ô chính, sau 2 vòng, chỉ 90d)

| Setup | Định nghĩa cuối | n | lệnh/ngày | WR | R TB | TEST | Kết luận |
|---|---|---|---|---|---|---|---|
| A Phá hồi | V3: phá M5 ngoài VA Âu/IB, hết hạn 30 nến, hồi U ≥3 nến, CF, TP 3R | 20 | 0,31 | 10% | −0,68 | n=8, −0,08 | **chưa có lợi thế**; hợp lưu (V4) chỉ còn 1 lệnh |
| B Hấp thụ | cụm 3 nến tại VWAP tuần/ngày, CF ≥ 0,5·Δmax, TP 3R | 11 | 0,17 | 27% | 0,00 | n=4 | **n quá nhỏ**, 3 hướng sửa không giúp |
| C Fade cạnh | phá hụt cạnh VA ≥2 tick, đóng lại trong, TP 2R | 121 | 1,9 | 27% | −0,26 | n=58, −0,14 | **thua có ý nghĩa** (KTC 95% [−0,48; −0,01]) |
| D Trap | V3: move ≥5 giá cùng bias VWAP tuần, hồi ≤70%, bẫy + CF, TP 2R | 31 | 0,51 | — | +0,08 | n=15, −0,29 | **không bền**, KTC bao trùm 0 |

Cộng cả 4 setup: khoảng **3 lệnh/ngày**, kỳ vọng ≈ **−0,2R/lệnh**. So với mục tiêu (10–20 lệnh/ngày, WR 60–70%, 1:2–1:3): **chưa đạt ở mọi tiêu chí**.

## Vì sao — ba điều đo được, không phải phỏng đoán
1. **Đối chứng (vào ngẫu nhiên cùng vùng, cùng chế độ, cùng chiều) cũng âm, −0,1 đến −0,2R.** Nghĩa là "ở vùng" + "đúng chế độ"
   tự nó không tạo lợi thế trên M1 với SL 2–4 giá; chi phí 0,2 giá ăn 5–10% mỗi R.
2. **Bộ lọc cơ chế (hình U, giảm dần, CF chặt) đưa kết quả từ âm về ≈0, không lên dương.** Chúng lọc đúng lỗi nhật ký
   (vào ở lưng, V gọi là U) nhưng không thêm lợi thế.
3. **Khớp quá mức xuất hiện ngay:** mọi ô "đẹp" ở TRAIN đều đổi dấu ở TEST; không ô nào trong ~300 ô đã quét sống cả hai nửa.

Kết quả này **khớp** với 8 phép đo cũ trong `research/*.md` (hấp thụ, bong bóng, stacked imbalance, đặc trưng nến ≈ 50%).

## Quyết định
- **QĐ-7:** indicator vẫn port đủ 4 setup, 4 công tắc **bật mặc định** để chạy **forward test** (thu thống kê live trên bảng
  và CSV), README ghi rõ "chưa có lợi thế đo được trong 65 phiên". Người học tắt setup nào sau khi thấy số live.
- Không ép tham số. Không thêm setup thứ 5 cho tới khi có ≥ 3 tháng dữ liệu mới cùng mã hợp đồng.
- Việc có giá trị nhất tiếp theo: **đối chiếu tín hiệu bot với nhật ký tay** (cùng ngày 16/9 → 15/10): bot có bắt được
  3 lệnh +3R tốt nhất của người học không, và bot có tránh được 35 lệnh thua không. Đó là phép kiểm "bot có hiểu hệ thống"
  độc lập với lợi nhuận.

Chi tiết từng setup: `RESULTS-A.md`, `RESULTS-B.md`, `RESULTS-C.md`, `RESULTS-D.md` (bảng 2 năm trong đó chỉ tham khảo).
