# Vẽ sẵn vùng cụm khối lượng → giá chạm thì đảo hay xuyên: 20 vòng (M15, Opus, 2026-11-25)

Chỉ đo **phản ứng của giá**, không giả lập lệnh. Script: `vs.py` (bộ máy đo) và `vong20.py` (các vòng).

Dữ liệu: NQZ26 từ 13/09 đến 25/11 (53 phiên), GCZ26 từ 28/07 đến 18/11 (74 phiên).

**Đơn vị U15** = biên độ trung bình một nến M15 của 5 phiên gần nhất. NQ khoảng 55 điểm, GC khoảng 8,2 giá.

## Cách đo

**1. Vẽ sẵn vùng tại một mốc bất kỳ.** Chỉ dùng dữ liệu trước mốc.
- Lấy profile cố định của từng phiên ngày đã đóng (3 phiên gần nhất).
- Tìm cụm khối lượng: đỉnh của profile đã làm mượt, khối lượng ≥ 1,5 lần trung bình hàng. Lấy 2 cụm nặng nhất mỗi phiên.
- Dải cụm: từ đỉnh nới ra tới khi khối lượng còn < 70 % đỉnh. Bề rộng khoảng 0,7 U15.
- Các cụm chồng nhau giữa các ngày thì gộp thành một vùng hợp lưu.
- Có vòng thử thêm cụm của profile tuần trước, và vùng đi ngang rồi bứt kiểu Trader Dale (tự dò trên M15).

**2. Lần chạm.**
- Giá tới gần mép gần của vùng (trong 0,6 U15), sau khi đã cách vùng ít nhất 1,25 U15.
- Mỗi lần chạm mang theo trạng thái của vùng ngay trước lúc chạm: cú rời đi trước đó mạnh cỡ nào, là lần tới gần thứ mấy, vùng bao nhiêu tuổi, giá lao tới nhanh hay chậm, giá đang thuận hay ngược xu hướng.

**3. Vì sao bảng lần chạm tương đương với cách "chọn mốc bất kỳ".**
- "Chọn mốc bất kỳ, vẽ hết vùng, xem lần chạm đầu tiên sau mốc" cho ra đúng tập lần chạm này, vì vùng không đổi trạng thái giữa mốc và lần chạm.
- Đã kiểm lại đúng nghĩa đen: vòng 1 lấy 400 mốc ngẫu nhiên mỗi mã, vòng 20 lấy 600 mốc. Kết quả khớp.

**4. Kết cục của mỗi lần chạm** (điểm đảo là cực trị khi giá bật ngược ≥ 1 U15):
- **Đảo tại vùng.**
- **Quay đầu sớm**, trước mép gần.
- **Xuyên qua:** vượt quá mép xa, hoặc không bật nổi.

**"Giữ khi đã chạm"** = trong các lần giá thực sự vào tới vùng, bao nhiêu % giá đảo tại vùng.

**5. Đối chứng.** Cùng vùng đó dời đi ±1,5–4 U15, chạy y hệt bộ máy và lọc y hệt luật.
- **Δ** = % đảo tại vùng thật − % ở đối chứng, theo điểm %.
- Khoảng [5–95 %] tính bằng bootstrap theo phiên.
- NQ chia TRAIN (60 % phiên đầu) và TEST (40 % sau). GC là thị trường thứ hai.

## 20 vòng

| Vòng | Giả thuyết | Kết quả (Δ gộp) | Kết luận |
|---|---|---|---|
| 1 | Mọi cụm, mọi lần chạm | +0,5 [−1,7, +2,9]; 400 mốc ngẫu nhiên: +2,3 | cụm chạm bất kỳ lúc nào ≈ ngẫu nhiên |
| 2 | Chỉ vùng giá đã **rời mạnh** (≥ 3 U15 trong 4 nến M15) | **+6,1** [+0,4, +12,8]; rời chậm: −1,0 | điều kiện rời mạnh là bắt buộc |
| 3 | Lần tới gần thứ 1/2/3 | +13,4 / +9,2 / **−13,3** | chỉ dùng lần 1–2; lần 3 vùng hỏng |
| 4 | Cú rời 2/3/4/5 U15 trong 2/4/8 nến | 2 U15: +4; **3 U15 trong 8 nến (2 giờ): +12,8** [+6,9, +19,6], dương cả 3 tập | cú rời ≥ 3 U15 là đủ, cho phép tới 2 giờ |
| 5 | Độ nặng của cụm | **cụm nặng nhất phiên: +15,8** [+8,0, +25,2]; cụm hạng 2: +3,7 | chỉ cụm nặng nhất mới đáng vẽ |
| 6 | Tuổi cụm (cách 1/2/3 ngày; lấy 5 phiên) | +13,3 / +7,5 / +14,0; lấy 5 phiên: +6,2 | 3 phiên là đủ, nhiều hơn thì loãng |
| 7 | Vùng hợp lưu (≥ 2 cụm chồng) | Dale: +5,0 (n 29); mọi lần chạm: +2,9; ≥ 3 cụm: −5,9 | hợp lưu **không** mạnh hơn, chỉ rộng hơn (≈ 1,2 U15) |
| 8 | Thêm cụm tuần trước | vùng có cụm tuần: −3,4 | cụm tuần không giúp cho M15 |
| 9 | Bề rộng dải 55 / 70 / 85 % | −3,3 / **+11,6** / −0,7 | dải 70 % (≈ 0,7 U15) đúng nhất |
| 10 | Nới theo râu 0,1 / 0,2 U15 mỗi mép | +4,9 / +7,5 (gốc +11,6) | **không nới**: râu không giúp |
| 11 | Chỉ vùng đi ngang rồi bứt (tự dò) | +2,8 đến +3,9, NQ TEST âm | vùng tự dò yếu hơn cụm profile ngày |
| 12 | Cụm ngày + vùng đi ngang Dale (gộp) | +11,8; vùng có cả hai: +12,7 | thêm vào không hại, cũng không hơn |
| 13 | Vùng chứa cao/thấp phiên trước | −21,8 (n 13) | quá ít mẫu; gợi ý tránh |
| 14 | Chạm thuận / ngược xu hướng (so với giá TB 1 ngày) | **thuận: +21,9** [+9,5, +33,2]; ngược: +4,2 | đúng ý Dale "vào theo xu hướng" |
| 15 | Giá lao tới nhanh / vừa / chậm | nhanh: +1,0 (n 43); vừa: +17,1; chậm: +11,9 | giá lao tới quá nhanh thì hay xuyên (mẫu ít) |
| 16 | Chạm sau 0–4 / 4–12 / > 12 giờ kể từ khi rời | +8,5 / +20,7 / +10,0 | không rõ quy luật |
| 17 | Giờ Mỹ / ngoài giờ Mỹ | +6,4 / +16,6 | chưa có cơ chế giải thích; không dùng |
| 18 | Ngưỡng bật 0,5 / 1 / 1,5 / 2 U15 | +7,1 / +11,6 / +7,0 / +9,5 | dương ở mọi ngưỡng |
| 19 | **Ghép:** rời ≥ 3 U15 trong 8 nến + lần 1–2 + cụm nặng nhất | **+17,4 [+9,3, +24,7]**: NQ TRAIN +23,8, NQ TEST +18,2, GC +13,7 (n 154) | luật chính |
| 19 | Ghép + chạm thuận xu hướng | **+24,4 [+14,5, +35,3]** (n 70); ngược xu hướng +11,9 | thuận xu hướng mạnh hơn rõ |
| 20 | Kiểm cuối nghĩa đen: 600 mốc ngẫu nhiên mỗi mã, luật ghép | **+24,9 [+10,2, +39,8]**; thêm thuận xu hướng: +22,0 | đúng cả khi đo bằng mốc ngẫu nhiên |

## Luật vẽ rút ra (chưa kiểm định)

1. Mỗi phiên ngày đã đóng, vẽ **1 cụm khối lượng nặng nhất** của profile cố định. Dải gồm các mức giá còn ≥ 70 % đỉnh, khoảng 0,7 U15 (NQ khoảng 40 điểm, GC khoảng 6 giá). **Không** nới theo râu.
2. Giữ cụm của **3 phiên gần nhất**. Cụm chồng nhau thì gộp, nhưng hợp lưu không làm vùng mạnh hơn.
3. Vùng chỉ có hiệu lực khi giá đã **rời dải ≥ 3 U15 trong ≤ 8 nến M15**.
   - Rời lên thì là hỗ trợ, rời xuống thì là kháng cự.
   - Chỉ dùng cho **lần tới gần thứ 1 và 2**; từ lần 3 thì bỏ.
4. Ưu tiên lần chạm **thuận xu hướng**: hỗ trợ khi giá vẫn ở trên giá trung bình 1 ngày, kháng cự khi giá vẫn ở dưới.

## Tỉ lệ theo luật ghép (vòng 19)

Tính trên 100 lần giá tới gần vùng:

| | Vùng theo luật | Mức giá bất kỳ cùng điều kiện |
|---|---|---|
| Đảo tại vùng | **43** | 25 |
| Quay đầu sớm, trước khi chạm | 39 | – |
| Xuyên qua | 18 | – |
| **Đã vào tới vùng thì giữ được** | **70 %** | 50 % |

Cộng thêm điều kiện thuận xu hướng: đảo tại vùng 47 so với 23, và giữ được 73 % khi đã vào tới vùng.

## Giới hạn

- Luật ghép có 154 lần chạm; bản thêm thuận xu hướng chỉ có 70 lần.
- Đã thử khoảng 60 cách lọc, nên có rủi ro chọn trúng may mắn. Bù lại, luật ghép dương ở cả NQ TRAIN, NQ TEST và GC.
- Với ngưỡng bật 1,5–2 U15, NQ TEST của bản thuận xu hướng bị âm.
- Cần NQU26, NQM26, NQH26 để kiểm độc lập.

## Lệnh chạy lại

```bash
VM_CACHE_DIR=$TEMP/vmc python vong20.py          # cả 20 vòng (~3 phút)
VM_CACHE_DIR=$TEMP/vmc python vong20.py 19 20
```

## Đưa vào SessionZones (lớp "Vùng cụm vol", 2026-11-25)

Thuật toán của indicator nằm trong `cz_ref.py` (Python) và `ClusterZones` trong ProfileEngine.cs (C#). Test C# = Python trên 41 thời điểm thật NQ + GC: 83 vùng, trong đó 20 vùng đang bị chạm.

Thuật toán:
- Chỉ lấy **1 cụm nặng nhất** của mỗi phiên ngày.
- Bộ máy trạng thái chạy trên **nến M15**, không phải M1.
- Vùng chỉ hiện khi đủ luật (đã rời mạnh, lần chạm 1–2).

**Đo lại đúng thuật toán này** (1 500 mốc ngẫu nhiên mỗi mã, chấm trên M1, so với vùng dời ngẫu nhiên áp cùng luật):
- Đảo tại vùng: 42,0 % so với 31,9 % ở đối chứng, **Δ +10,1** [+1,0, +19,8].
- Theo từng tập: NQ TRAIN +14,2, **NQ TEST −7,4**, GC +14,1.
- Lợi thế thấp hơn bản nghiên cứu (+14 đến +17), và âm ở NQ TEST.

**Lọc thuận xu hướng không ổn định:** ở bản M15 này, chạm ngược xu hướng lại tốt hơn (+16,1 so với +7,5). Vì vậy indicator **không** dùng điều kiện xu hướng.

**Lỗi đã sửa khi port:** trên M15, giờ nghỉ CME (60 phút) làm hai nến mở cách nhau đúng 75 phút. Ngưỡng tách phiên phải là > 60 phút, không phải > 75 phút như trên M30; để > 75 thì các phiên bị dính vào nhau.

**Báo Telegram:**
- Gửi một tin khi lần chạm hợp lệ bắt đầu trong 30 phút gần nhất.
- Khoá chống trùng = mã + phía + nến M15 bắt đầu lần chạm, lưu bằng file tạo nguyên tử. Nhiều tab hay mở lại chart cũng không gửi lại.
