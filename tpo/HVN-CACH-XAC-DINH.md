# Cách xác định HVN — bản tổng hợp từ internet (2026-11-02)

> Không có định nghĩa chuẩn có ngưỡng số. Các bước dưới là **tổng hợp riêng của Claude** ghép từ các nguồn
> ghi ở cuối file. **Chưa kiểm định** trên dữ liệu vàng.

1. **Chọn khung profile:** TPO ngày cho scalp, TPO gộp 3 tuần cho vùng lớn (theo CORVEN). Mỗi dòng 1 giá.
2. **Làm mượt:** mỗi dòng lấy trung bình với 2 dòng sát bên, để bỏ răng cưa nhiễu.
3. **Tìm đỉnh:** dòng có khối lượng cao hơn hai dòng sát bên.
4. **Lọc bằng độ nổi:** độ nổi = khối lượng đỉnh trừ đi thung lũng **cao hơn** trong hai thung lũng hai bên.
   Chỉ giữ đỉnh có độ nổi **≥ 30% POC**. Hai đỉnh không có thung lũng thật ở giữa ⇒ **một** HVN (một "kệ").
5. **Mép vùng:** đi từ đỉnh ra hai phía, dừng khi khối lượng đã rơi **60% quãng** từ đỉnh xuống thung lũng.
6. **Kiểm tra độ bền:** đổi cỡ dòng (1 giá → 2 giá) mà HVN vẫn còn thì mới tin.

## Áp dụng mẫu (ảnh profile 4079 → 3991, chụp 2026-11-02 20:57)
- HVN chính: **4040 → 4018**, đỉnh 4026 (7.904), chứa 57% khối lượng.
- HVN phụ: **4076 → 4070**, đỉnh 4073–4074 (4.651), 11% khối lượng.
- LVN: 4068 → 4042 (khoảng 300–1.100 mỗi dòng).
- Bậc 4017 → 4005 (đỉnh 3.712 ở 4009): độ nổi chỉ 7% ⇒ không đủ chuẩn HVN.
- Giá rơi từ 4060: canh buy ở **mép trên HVN chính 4040 → 4038**, cần bias tăng + nến M1 xác nhận.

## Nguồn
- Ngưỡng 30% độ nổi: [How to Analyze Volume Profiles With Python](https://pycoders.com/link/5581/web)
- Mép 60% quãng + tách đỉnh bằng thung lũng: [TradingView – HVN Zones](https://www.tradingview.com/script/6TPrx1GV-HVN-Zones/)
- Kệ liền = 1 vùng, cỡ dòng thô gộp đỉnh: [LuxAlgo – High/low-volume Nodes](https://www.luxalgo.com/library/concept/high-low-volume-nodes/)
- Vào gần mép HVN: [Trader Profesional – HVN and LVN](https://traderprofesional.com/en/hvn-lvn-volume-nodes/)
