# Đặc điểm ca stacked imbalance THÀNH CÔNG vs THẤT BẠI

**Ngày đo:** 2026-09-10 · **Script:** `research/stack-imb-dac-diem.py`
**Log:** `_stack_dacdiem_log.txt` (2,5 tháng) · `_stack_dacdiem_ngoaimau.txt` (22 tháng) · `_stack_combo_log.txt`

Người học hỏi: trong 2,5 tháng gần nhất (1/6 → 19/8/2026), 148 lần mua dồn giá đi lên tiếp và 165 lần
bán dồn giá đi xuống tiếp — **đặc điểm chung của chúng là gì**, để lập combo?

Cách làm: với mỗi ca, trích **16 đặc trưng** (số mức dồn, delta nến, khối lượng so trung vị, biên độ nến,
vị trí đóng cửa trong nến, số nến cùng chiều liên tiếp, giá đã đi được bao nhiêu trong 20 nến, khoảng
cách tới VWAP, vị trí trong biên độ ngày, biên độ ngày, số lệnh, cỡ lệnh trung bình, số mức giá, giờ UTC,
POC nến so close). Chia hai rổ theo trung vị từng đặc trưng, so tỷ lệ đi đúng chiều sau 20 phút; đo riêng
nửa đầu và nửa sau kỳ, đặc trưng nào đổi dấu giữa hai nửa thì loại.

## 1. Đặc điểm rút ra từ 2,5 tháng gần nhất

**Mua dồn** (314 ca, đi theo 148 / ngược 166) — nhóm thành công có:
- giá **chưa chạy xa**: rổ đã đi ≥2,5 giá thắng 41,8%, rổ chưa đi thắng 52,6%;
- nến **không đóng sát đỉnh**: đóng ≥75% biên độ thắng 42,0%, đóng thấp hơn thắng 52,2%;
- ít lệnh hơn, delta nhỏ hơn (cùng chiều với hai điểm trên: càng "nóng" càng kém).

**Bán dồn** (360 ca, đi theo 165 / ngược 195) — nhóm thành công có:
- nến **đóng sát đáy** (≥0,71): thắng 52,2% so với 39,4%;
- **biên độ ngày rộng** (≥52 giá): 49,4% so với 42,2%;
- **sau 9h UTC** (16h giờ Việt Nam): 50,2% so với 40,0%.

Ghép lại thành combo trên chính 2,5 tháng đó:
- **Mua:** chưa chạy xa + không đóng sát đỉnh → 88 ca, **thắng 49 thua 39** (55,7%), nền là 47,1%.
- **Bán:** đóng sát đáy + ngày rộng + sau 9h → 67 ca, **thắng 37 thua 30** (55,2%), nền 45,8%.

## 2. Kiểm hai combo đó trên 22 tháng còn lại (2024-08 → 2026-06) — CẢ HAI SỤP

| Combo | Trên 2,5 tháng (nơi tìm ra) | Trên 22 tháng (ngoài mẫu) | Nền 22 tháng |
|---|---|---|---|
| Mua: chưa chạy xa + không đóng sát đỉnh | 55,7% (88 ca) | **52,6%** (953 ca) | 52,5% → **không hơn gì** |
| Bán: đóng sát đáy + ngày rộng + sau 9h | 55,2% (67 ca) | **42,3%** (168 ca) | 47,9% → **tệ hơn 5,6 điểm** |

## 3. Chiều ngược lại cũng sụp: combo rút từ 22 tháng chết ở 2,5 tháng gần

Trên 22 tháng (n lớn, 3.190 ca mua / 3.076 ca bán) các đặc trưng sống sót lại **ngược hẳn**:
mua dồn **càng nóng càng tốt** (cỡ lệnh trung bình lớn 55,5% vs 49,6%; đóng sát đỉnh 53,8% vs 51,3%;
delta lớn 54,1% vs 51,0%), còn bán dồn **càng nóng càng tệ** (giá đã giảm nhiều 45,0% vs 50,8%;
nhiều lệnh 45,4% vs 50,4%; ngày biên độ rộng 45,5% vs 50,2%).

| Combo rút từ 22 tháng | Trên 22 tháng | Kiểm trên 2,5 tháng gần |
|---|---|---|
| Mua: cỡ lệnh TB ≥1,15 + đóng sát đỉnh | 56,1% (807 ca) | **35,2%** (54 ca) — ngược dấu nặng |
| Mua: chỉ cỡ lệnh TB ≥1,15 | 55,6% (1.587 ca) | **45,1%** (113 ca) |
| Bán: chưa giảm nhiều + ngày yên | 53,0% (837 ca) | 52,4% nhưng chỉ **21 ca** |

## 4. Kết luận

1. **Không có combo nào sống được ở cả hai giai đoạn.** Luật tìm trên giai đoạn nào chỉ đúng ở giai
   đoạn đó — đúng bài học đã ghi ở `DAC-DIEM-CA-DAO-CHIEU.md`.
2. **Nguyên nhân không phải nhiễu thuần: hai giai đoạn hành xử NGƯỢC NHAU.** Trong 22 tháng thị trường
   tăng mạnh, mua dồn kiểu "đuổi giá" (nến đóng sát đỉnh, lệnh to) thắng 56%. Trong 2,5 tháng gần đây,
   đúng kiểu đó chỉ thắng 35%. Nền cũng đổi: mua dồn nói chung từ 52,5% xuống 47,1%.
3. Vì vậy con số đáng giữ lại **không phải combo** mà là: **giai đoạn 6-8/2026 phạt hành vi đuổi giá**.
   Cùng một dấu hiệu, cùng một cách đọc, kết quả đảo chiều khi chế độ thị trường đổi.
4. Việc cần làm trước khi lập bất kỳ combo nào: **có cách nhận ra chế độ thị trường đang là loại nào**
   (xu hướng bền vs đảo liên tục). Chưa có, và đó là lỗ hổng thật.
5. ⛔ Không code combo nào trong tài liệu này thành tín hiệu.
