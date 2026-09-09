# Bóc đặc điểm ca ĐẢO CHIỀU — tìm điều kiện NHẬN DẠNG hấp thụ (chưa bàn vào lệnh)

**Script:** `research/dac-diem-ca-dao-chieu.py` (không lọc vùng) ·
`research/dac-diem-dao-chieu-tai-vung.py` (chỉ xét ca **tại vùng**)

## Cách làm
- Tập sự kiện rộng: `khối lượng ≥ 2,5× trung vị 50 nến` **và** `|delta| ≥ 3× trung vị 50 nến`, hai chiều.
- Nhãn **ĐẢO CHIỀU** = giá chạm `±2u` ngược hướng chủ động trước khi chạm phía thuận (u = trung vị biên độ).
- **15 đặc trưng** ứng viên, chuẩn hoá theo chiều (cao = giống hấp thụ hơn).
- **Tách đôi thời gian:** nửa đầu tìm luật (ngưỡng ngũ phân vị lấy từ nửa đầu), **nửa sau kiểm tra**.
- Neo đo tại **giá đóng nến SAU**, bắt đầu từ nến i+2 ⇒ nến xác nhận **không** nằm trong đường được đo.

## 🔴 Phát hiện phương pháp: "nến sau xác nhận" là VÒNG LẶP LOGIC
| Cách neo phép đo | tỉ lệ đảo chiều Q1 → Q5 | độ lệch |
|---|---|---|
| Neo tại nến sự kiện (nến xác nhận **nằm trong** đường đo) | 29,3% → **68,5%** (nửa sau 29,5% → 70,3%) | **+39,2 / +40,8** |
| Neo tại nến sau (loại nến xác nhận khỏi đường đo) | 52,8% → 50,9% (nửa sau 51,0% → 53,2%) | −1,9 / +2,1 |

⇒ Sức mạnh "khủng" của nến xác nhận **tan hết** khi không cho nó tự chứng minh chính nó.
Đây đúng là cái bẫy đã làm sai kết luận "K1 tăng từ 8,1% lên 25,9%" trước đó.

## Kết quả — CHỈ XÉT CA TẠI VÙNG (n = 4.039 nửa đầu / 2.633 nửa sau)
Nền: đảo chiều **49,5%** (nửa đầu) và **51,6%** (nửa sau).

### Theo loại vùng (gộp 2 nửa)
| Vùng | n | đảo chiều |
|---|---|---|
| naked POC | 180 | 53,9% |
| **VWAP tuần** | 1.241 | **53,3%** |
| VWAP ngày | 2.735 | 50,7% |
| biên VA | 1.703 | 50,4% |
| HVN tuần | 708 | 50,0% |
| HVN ngày | 868 | 49,7% |
| POC phiên trước | 1.045 | 49,8% |
| LVN ngày | 1.071 | 49,4% |
| **HVN 3 tuần** | 608 | **45,7%** (nghiêng đi tiếp) |

### Theo 15 đặc trưng của chính nến — **KHÔNG CÓ CÁI NÀO SỐNG SÓT**
Mọi đặc trưng có độ lệch ≥ 4 điểm ở một nửa đều **đổi dấu** ở nửa kia:

| Đặc trưng | lệch Q5−Q1 nửa đầu | nửa sau |
|---|---|---|
| nỗ lực/kết quả | −3,6 | **+6,0** |
| số mức giá / biên độ | +0,9 | **+8,0** |
| số lần chạm vùng | 0,0 | **+6,1** |
| chân trước đó dài | +0,9 | **−5,3** |
| nến sau xác nhận | +3,2 | **−4,8** |
| đóng ngược phía (%) | −3,6 | −0,7 |
| POC hút (%vol) | −0,9 | +2,4 |
| cỡ lệnh (avg_size) | +0,1 | −0,7 |
| delta phân kỳ | +0,2 | −3,1 |
| cực trị phiên | +0,2 | −1,0 |

⇒ **Không thêm được luật nhận dạng nào từ đặc trưng nến.** Các con số 6–8 điểm ở nửa sau là
**nhiễu**: chúng không có ở nửa đầu, nếu lấy làm luật thì đó chính là tự lừa mình.

## Ý nghĩa
1. Các dấu hiệu sách dạy — đóng cửa ngược phía, delta/khối lượng lớn, POC hút khối lượng, POC sát
   cực trị, cỡ lệnh to, phân kỳ delta, chân giảm dài, ở cực trị phiên — **không tách được** ca đảo
   chiều khỏi ca thất bại, kể cả khi đã lọc "tại vùng".
2. Thứ duy nhất trông mạnh là **vòng lặp logic**.
3. Chỉ còn hai ô đáng theo, và chúng là **loại vùng** chứ không phải đặc trưng nến:
   **VWAP tuần 53,3%** (n=1.241) và **HVN 3 tuần 45,7%** (n=608, nghiêng **đi tiếp**).

## 🎯 Vấn đề PHƯƠNG PHÁP đáng sửa nhất
Toàn bộ nghiên cứu này xấp xỉ hấp thụ **theo NẾN**. Nhưng định nghĩa gốc của order flow là
**theo MỨC GIÁ**: "tại một mức giá, khối lượng lớn khớp mà giá không xuyên qua mức đó".
File `fp_GC_XCEC_Time_*_748d9h.csv` (583 MB) **có bid/ask từng mức giá** ⇒ đo được đúng định nghĩa
gốc, gồm cả imbalance chéo và cụm imbalance xếp tầng. Đó là hướng tiếp theo đáng làm nhất —
đổi **dữ liệu**, không phải đổi **ngưỡng**.
