# Hấp thụ có thật là hấp thụ không? — kiểm lại chính phép đo của mình

> Câu hỏi của người học 2026-09-08: *"K3 thất bại nhiều như thế, liệu đó có phải hấp thụ không?
> 3 điều kiện xác nhận hấp thụ có còn đúng nữa không?"*

## 1. LỖI CỦA PHÉP ĐO TRƯỚC — điều kiện 3 bị mã hóa NGƯỢC

Ba điều kiện người học nêu: (1) khối lượng cực lớn, (2) delta lệch hẳn một bên,
(3) **nỗ lực có nhưng kết quả không — giá KHÔNG tạo đáy mới**.

Trong `research/kich-ban-hap-thu*.py` tôi lại đòi nến sự kiện **PHẢI là đáy thấp nhất 20 nến**
⇒ tức **bắt buộc giá đã đi tiếp**. Đó là **ngược hẳn** điều kiện 3. Vậy cái đã đo là
**"cụm bán tháo phá đáy" (capitulation), KHÔNG phải hấp thụ.**

Lỗi thứ hai — **thiên lệch hình học**: "K3" định nghĩa là thủng 0,5 biên nến **dưới đáy nến sự kiện**.
Một nến vừa tạo đáy mới thì đang nằm sát mép dưới ⇒ thủng thêm vài tick là chuyện dễ.
Vậy **con số K3 61,9%/65,2% chủ yếu do hình học, không phải bằng chứng "hấp thụ thất bại"**.

## 2. Đo lại bằng thước ĐỐI XỨNG
Từ giá đóng nến sự kiện, đặt hai rào `+u` và `−u` (`u` = trung vị biên độ 50 nến trước),
xem bên nào chạm **trước** trong 60 nến. Nến ngẫu nhiên phải cho ~50/50.
Chạy cả hai chiều bằng cách lật gương dữ liệu (`research/hap-thu-that-hay-khong.py`).

| Họ sự kiện | n | thuận/(thuận+ngược) ±1u | z | ±2u | z |
|---|---|---|---|---|---|
| **A** bán tháo phá đáy (vol≥3×, delta≥4×, đáy mới) | 8.251 | 50,2% | +0,38 | 49,0% | −1,76 |
| **B** HẤP THỤ đúng nghĩa (vol≥3×, delta≥4×, **không** đáy mới, biên độ ≤ trung vị, đóng nửa trên) | 357 | 51,3% | +0,48 | 48,9% | −0,42 |
| **B2** nỗ lực lớn / kết quả nhỏ (biên độ ≤ 0,7× trung vị) | 161 | 51,6% | +0,40 | 48,4% | −0,39 |
| **C** chỉ khối lượng lớn | 23.574 | 50,0% | 0,00 | 50,0% | 0,00 |
| **D** nến ngẫu nhiên (nền chuẩn) | 42.182 | 50,0% | — | 50,0% | — |

⇒ **Tất cả bằng mức bốc ngẫu nhiên.** Hấp thụ đúng nghĩa cũng vậy.

## 3. Nến xác nhận cũng KHÔNG dự báo hướng
Đo từ giá đóng **nến xác nhận** (`research/hap-thu-nen-xac-nhan.py`), thêm nền so sánh **E** =
nến delta dương cực đoan bất kỳ (không cần có cụm hấp thụ trước), để tách phần "đà delta".

| | n | thuận ±1u | z | ±2u | ±3u |
|---|---|---|---|---|---|
| **Ac** bán tháo phá đáy + nến xác nhận | 1.918 | 51,3% | +1,13 | 50,5% | 49,2% |
| **Bc** hấp thụ đúng nghĩa + nến xác nhận | 39 | (n quá ít) | | | |
| **E** nến delta cực đoan bất kỳ | 13.304 | 49,9% | −0,32 | 49,7% | 50,0% |
| **D** nền chuẩn | 42.134 | 50,0% | — | 50,0% | 50,0% |

⇒ **Kết luận trước đó "nến xác nhận đẩy K1 từ 8,1% lên 25,9%" là ẢO GIÁC HÌNH HỌC:** sau nến xác nhận,
giá đã bật xa khỏi đáy nên cái bẫy "thủng đáy" khó nổ hơn — chứ hướng đi thì vẫn 50/50.

## 4. Nhưng có một thứ ĐO ĐƯỢC: nó báo BIÊN ĐỘ, không báo HƯỚNG
`research/hap-thu-bao-bien-dong.py` — biên độ 30 nến kế tiếp chia cho `u`:

| Họ | n | trung vị | so với nền |
|---|---|---|---|
| A bán tháo phá đáy | 8.370 | **7,33** | **+19%** |
| C chỉ khối lượng lớn | 12.076 | 7,05 | +15% |
| B hấp thụ đúng nghĩa | 565 | 6,60 | +7,5% |
| D nền chuẩn | 21.748 | 6,14 | — |

⇒ Cụm khối lượng lớn **thật sự báo trước một đoạn chạy rộng hơn 15–19%** — nhưng **không nói đi đâu**.

## 5. Trả lời câu hỏi
1. **Con số K3 63% phải bỏ** — nó là hình học, không phải bằng chứng hấp thụ thất bại.
2. **Ba điều kiện vẫn nhận đúng một hiện tượng thật** (chỗ chuyển giao hàng, khối lượng lớn), nhưng
   **không sinh ra lợi thế về hướng** ở M1 trong 60 nến. Chúng cho biết **sắp có sóng**, không cho biết
   **sóng đi đâu**.
3. **Điều kiện còn THIẾU, lấy từ `CORVEN_SPEC_V1.md`:** luật **R2 — "hấp thụ chỉ có giá trị ở CỰC TRỊ"**,
   và vùng của CORVEN **chỉ gồm HVN tuần + HVN ngày + VWAP**; POC/VAH/VAL/đáy-đỉnh phiên trước bị loại
   thẳng (Q14: *"Tất nhiên là không rồi"*). Tức phép đo của tôi thiếu đúng điều kiện quan trọng nhất:
   **vị trí phải ở HVN**. ⚠️ Nhưng commit `811a57a` đã đo 474 phiên bằng 5 cách độc lập:
   **HVN không phải mốc phản ứng** (ngang random) ⇒ đừng kỳ vọng nó cứu được, phải đo mới biết.
4. **Hấp thụ đúng nghĩa rất hiếm:** 565 ca / 2 năm ≈ **0,4 lần/phiên**. Cái người ta gặp hằng ngày
   và gọi là "hấp thụ" phần lớn là **bán tháo phá đáy** — hai thứ khác nhau.

## Việc nên làm tiếp
- Đo hấp thụ **tại HVN tuần / HVN ngày** (điều kiện R2 còn thiếu).
- Hoặc đổi cách dùng: coi cụm khối lượng lớn là **bộ lọc "sắp có sóng"** rồi đánh **theo hướng phá**,
  thay vì đánh ngược.
