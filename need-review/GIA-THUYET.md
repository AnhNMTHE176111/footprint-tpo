# GIẢ THUYẾT rút từ review — chưa được kiểm, CHƯA sửa cấu hình

> Mọi thứ rút ra từ review lệnh đi vào đây trước. **Không** sửa `WyckoffRunner.cs` hay cấu hình đóng băng
> cho tới khi giả thuyết được kiểm trên dữ liệu **forward** (tháng 8/2026 trở đi).
>
> Lý do: cấu hình v7 chỉ *vừa* sống sau Bonferroni (p 0.028/0.05) trên ≥94 lần thử. Thêm lần thử lên cùng
> cửa sổ 5–7/2026 là nó chết mà bảng số vẫn đẹp. Xem [00-DOC-TRUOC-KHI-REVIEW.md](00-DOC-TRUOC-KHI-REVIEW.md).

---

## Mẫu ghi một giả thuyết

```
### GT-01 — <tên ngắn>
- **Quan sát:** (từ file nào, những lệnh stt nào, con số cụ thể)
- **Cơ chế đề xuất:** vì sao thị trường lại xử sự như vậy — phải giải thích được, không chỉ tương quan
- **Quy tắc kiểm được:** phát biểu dạng máy chạy được, vd "bỏ tín hiệu nếu leg_gia > 8.0"
- **Áp lên in-sample:** n bị ảnh hưởng = ? · EV trước/sau = ? (tôi chạy, chỉ để biết, KHÔNG phải bằng chứng)
- **Cần dữ liệu gì để kiểm:** vd "tháng 8, ≥10 lệnh có leg_gia > 8"
- **Trạng thái:** CHỜ KIỂM / ĐANG KIỂM / ĐẠT / BÁC
```

---

## Giả thuyết đã có

*(chưa có — chờ review của người dùng)*

---

## Quan sát sẵn từ số liệu (tôi ghi, chưa phải giả thuyết đủ mạnh)

### QS-01 — v7 có thể chặt quá khi thị trường êm

Nhóm 89 lệnh v7 loại, tách theo tháng:

| Tháng | n bị loại | WIN | R của nhóm bị loại |
|---|---:|---:|---:|
| 2026-05 | 14 | 4 | +2.0R |
| **2026-06** (vàng crash) | 27 | 3 | **−15.0R** ← lọc cứu đúng tháng xấu |
| 2026-07 | 48 | 13 | **+4.0R** ← lọc hơi thừa tay |

**Đọc:** bộ lọc BREAK SẠCH đáng giá nhất ở tháng biến động, nhưng ở tháng êm (T7) nó loại đi một nhóm hơi
dương. Chưa đủ mạnh để làm gì — +4.0R trên 48 lệnh là EV +0.083, vẫn kém xa +1.353. Và chia theo tháng
tức n mỗi ô rất nhỏ.

**Cần gì để thành giả thuyết thật:** một định nghĩa "thị trường êm" đo được **trước** khi vào lệnh (vd ATR
hoặc độ rộng range phiên), không phải "nhìn lại thấy tháng 7 êm".
