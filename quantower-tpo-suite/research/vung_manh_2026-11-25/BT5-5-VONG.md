# Backtest SessionZones 5 vòng (Opus, 2026-11-25)

Dữ liệu: **NQZ26** `fp_NQZ26_XCME_Time_20260204-20261125_293d16h` (file "1 năm") và **GCZ26** (2 file 90 ngày, như lần đo trước).
Kết quả: hộp HVN có lợi thế nhỏ nhưng đều so với đường ngẫu nhiên. Vùng mạnh chỉ có lợi thế khi hợp lưu có HVN.
Cả lớp vẫn **chưa kiểm định**: mẫu chỉ hơn 2 tháng NQ và 3,5 tháng GC.

## 1. Kiểm dữ liệu

| Tháng NQZ26 | nến M1 | khối lượng | ghi chú |
|---|---|---|---|
| 02–08/2026 | 1 → 6 918 / tháng | 1 → 18 855 hợp đồng / tháng | hợp đồng phụ (NQU26 mới là hợp đồng chính): lỗ thời gian hàng trăm lần, nến lẻ tẻ ⇒ **không dùng** |
| 09/2026 (từ 13/09 21:30 UTC) | 18 059 | 6,8 triệu | dùng |
| 10/2026 | 30 240 | 14,4 triệu | dùng |
| 11/2026 (tới 25/11) | 24 040 | 15,2 triệu | dùng |

Phần dùng (13/09 → 25/11) không có nến volume 0, không có nến thiếu khối lượng theo giá, không có lỗ 6–55 phút trong phiên.
Nghỉ ngày đúng giờ CME, tổng cộng 53 phiên.
File "1 năm" thực chất chỉ thêm 1 ngày so với file 90 ngày cũ, vì trước 13/09 NQZ26 chưa phải hợp đồng chính.
Muốn có thêm lịch sử thì phải xuất **NQU26, NQM26, NQH26, NQZ25** (mỗi hợp đồng lấy đúng quý nó là hợp đồng chính).

## 2. Cách chấm

Phần chấm nằm ở `bt5.py`. Tại MỖI nến M30 vừa đóng, script chạy đúng bản tham chiếu Python của indicator (C# = Python qua test parity) để lấy vùng mạnh và hộp HVN ĐANG được vẽ.
Trên nến M1 của khoảng thời gian vùng đang hiện:

- **Lần quay lại:** giá vào dải 0,6 U ngoài mép gần, sau khi đã cách mép ≥ 1,25 U (lần sau ≥ 1 U).
- **Điểm đảo:** cực trị tại lúc giá bật ngược 1 U. Đảo **trước** mép (chưa chạm) / **trong** vùng / **phá** (xuyên quá mép xa + 0,25 U).
- **Lệnh:** limit ở mép gần (và nới 0,1–0,3 U), dừng lỗ ở mép xa + 0,15 U, chốt 1R / 2R.
- **Chỉ số chính:** R 1:2 trung bình mỗi lần quay lại (không khớp lệnh thì tính 0).
- **Đối chứng:** cùng vùng dời ± 1,5–4 U (3 bản), cùng thời gian hiển thị và cùng cách chấm.
- **Lý do đảo sớm:** xem điểm đảo có trùng (± 0,1 U) với các mức sau không: đỉnh/đáy M30 cũ, râu M30 bất kỳ trong 5 phiên, vùng/hộp khác đang vẽ, cao/thấp hôm qua, số tròn, VWAP phiên đang chạy.
- **Tập:** NQ chia TRAIN = 60 % phiên đầu, TEST = 40 % phiên sau. GC là thị trường thứ hai để kiểm độc lập.

## 3. Năm vòng

| Vòng | Thấy gì (bước 2) | Sửa (bước 3) | Kết quả (Δ R 1:2 / lần quay lại, thật − đối chứng, NQ + GC [5–95 %]) |
|---|---|---|---|
| 0 (gốc) | Khoảng 50 % lần quay lại đảo TRƯỚC mép gần, nhưng đối chứng cũng 45 % ⇒ phần lớn là nhiễu giá. Phần dư thật nằm sát mép (đảo trong 0,3 U: 22 % so với 17 %). Lý do "râu nến cũ" KHÔNG phân biệt được: râu M30 khớp 95 % ở vùng thật và 90 % ở đối chứng; đỉnh/đáy M30 cũ 31 % ở cả hai. | — | vùng mạnh −0,011 [−0,06, +0,04] · hộp +0,044 [−0,02, +0,10] |
| 1 | Hộp HVN: vào lệnh sớm hơn 0,2 U cho kết quả tốt hơn ở cả NQ TRAIN, NQ TEST lẫn GC. Nới vùng mạnh tới thân nến của các lần va đập (đúng ý "vẽ cả phần râu") không cải thiện gì. Vùng đệm sườn profile (+0,08) kém dải cố định 0,2 U (+0,13). | Hộp HVN thêm **dải chờ 0,2 U** phía giá, thay vùng đệm sườn profile | hộp +0,088 [+0,02, +0,16] |
| 2 | Vùng mạnh có HVN trong hợp lưu: thật hơn đối chứng ở cả NQ và GC. Vùng chỉ có VWAP/VA thì không (GC −0,19). Vùng có mức tuần (VWAP/VA) còn kém hơn đối chứng ở cả hai thị trường. | Vùng mạnh **bắt buộc có HVN** (có ô tắt để quay về luật cũ) | vùng mạnh +0,044 [−0,02, +0,11] |
| 3 | Hộp mới hiện (≤ 12 nến) mà bị test ngay thì kém; hộp cũ, đã xa giá thì tốt hơn ⇒ thử tăng ngưỡng "đã rời xa". | **HVN rời xa 2 U → 4 U** | 3 U +0,108 · **4 U +0,122 [+0,05, +0,19]** · 5 U +0,127 · 6 U +0,149. Chọn 4 U vì vùng mạnh tốt nhất ở 4 U (+0,049) rồi xấu đi ở 5 U, và còn đủ mẫu (899 lần) |
| 4 | HVN tuần mạnh hơn HVN ngày ở cả 3 tập (NQ TRAIN +0,32, TEST +0,17, GC +0,20 so với đối chứng ≤ 0). Thử số phiên lấy HVN ngày: 3 / 5 / 8. | **Không đổi** (3 phiên +0,128 ≈ 5 phiên +0,122; 8 phiên kém hơn: +0,088) | — |
| 5 | Đo độ bền của bản chốt (= vòng 3): ngưỡng đảo 1,5 U, dừng lỗ mép xa + 0,3 U, R 1:1, từng tháng | — | xem mục 4 |

Thêm ở bước 2 của vòng 3: hiện tượng vùng tắt rồi hiện lại (khoảng 53 % vùng/hộp) là do thiết kế. Nguyên nhân là bán kính 4 U / 8 U và trần 2–3 vùng mỗi phía khi giá chạy; phần lớn chỉ tắt dưới 2 giờ. Không lần quay lại nào bị mất vì vùng đang ẩn.
Ở vòng 3, khi vùng mạnh đảo sớm thì điểm đảo nằm trên hộp/dải chờ HVN đang vẽ 73 % (NQ) / 68 % (GC), trong khi đối chứng chỉ 32 % / 39 %. Nghĩa là giá thường bật ở hộp HVN ngay trước vùng mạnh, và chỗ đó đã được vẽ.

## 4. Trước và sau (lệnh limit ở mép gần; sau = mép dải chờ của hộp)

| Tập | Loại | Bản | n | đảo trước mép | đảo trong | phá | R 1:2 thật | đối chứng | Δ |
|---|---|---|---|---|---|---|---|---|---|
| NQ TRAIN | hộp HVN | trước | 262 | 50 % | 27 % | 22 % | −0,027 | −0,028 | +0,002 |
| NQ TRAIN | hộp HVN | sau | 192 | 48 % | 36 % | 15 % | +0,094 | −0,024 | +0,118 |
| NQ TEST | hộp HVN | trước | 248 | 46 % | 26 % | 28 % | −0,012 | −0,019 | +0,007 |
| NQ TEST | hộp HVN | sau | 188 | 43 % | 37 % | 20 % | +0,101 | −0,119 | +0,220 |
| GC | hộp HVN | trước | 688 | 49 % | 27 % | 24 % | +0,033 | −0,041 | +0,075 |
| GC | hộp HVN | sau | 519 | 49 % | 36 % | 15 % | +0,091 | +0,005 | +0,086 |
| NQ + GC | vùng mạnh | trước | 1 244 | 49 % | 24 % | 28 % | +0,002 | +0,013 | −0,011 [−0,06, +0,04] |
| NQ + GC | vùng mạnh | sau | 598 | 48 % | 25 % | 27 % | +0,038 | −0,011 | +0,049 [−0,02, +0,12] |
| NQ + GC | hộp HVN | trước | 1 198 | 49 % | 27 % | 24 % | +0,011 | −0,033 | +0,044 [−0,02, +0,10] |
| NQ + GC | hộp HVN | sau | 899 | 47 % | 37 % | 16 % | +0,093 | −0,029 | **+0,122 [+0,05, +0,19]** |

Độ bền (Δ NQ + GC, hộp HVN sau): ngưỡng đảo 1,5 U cho +0,131, dừng lỗ + 0,3 U cho +0,104.
Theo tháng: NQ 09 +0,17 · 10 +0,12 · 11 +0,23; GC 08 +0,04 · 09 −0,03 · 10 +0,12 · 11 +0,50.
Điểm yếu: ở **R 1:1** cải thiện gần như mất (Δ hộp +0,023, trước là +0,046). Cái lợi chủ yếu nằm ở các lần bật đủ xa để chạm 2R.
Kỳ vọng tuyệt đối khoảng +0,09R mỗi lần quay lại, chưa trừ phí.

Ca người dùng (NQ 25/11 07:25 UTC): giá chạm dải chờ 25 609,75–25 639,25 của hộp 20/11, đáy 25 637,25, rồi bật đủ 2R.
Ở bản trước, lệnh đặt ở mép hộp không khớp.
Đổi lại: hộp 26 801,50–26 876,50 (HVN ngày 23/11) không còn vẽ lúc 24/11 11:30, vì giá chưa từng cách mép hộp 4 U.

## 5. Đã đổi trong indicator

1. `HvnBand = 0,20`: dải cam nhạt nét đứt 0,2 U sát hộp HVN, chỉ phía giá đang đứng, ra mép tick. Dải này thay vùng đệm sườn profile khi vẽ. Telegram ghi `chờ từ <giá>`.
2. `RequireHvn = true`: vùng mạnh chỉ vẽ khi hợp lưu có HVN. Settings có thêm ô **"Vùng mạnh: chỉ vẽ vùng có HVN trong hợp lưu"**; tắt ô này để quay về luật cũ (≥ 1 mức bất kỳ).
3. `HvnAway = 4`: hộp HVN chỉ tính (để vẽ và để hợp lưu) khi giá đã từng rời mép hộp ≥ 4 U.

Bản tham chiếu Python (`vung_manh.P`: `HVN_AWAY`, `REQ_HVN`, `HVN_BAND`) đổi theo; fixture `expected_cum2.json`, `nq_expected2.json`, `nq25_expected.json` được sinh lại.
`bt5.py moi` (mặc định mới) cho ra từng lần quay lại y hệt `v5`.
Lệnh chạy lại toàn bộ: `python prep1.py nqy` (`NQY_TMIN='2026-09-13 21:30:00'`), `python prep1.py gc`, `python bt5.py run nqy|gc v0|v1|v2|v3a..d|v4a|v4b|v5`, `python eval5.py <vòng>`, `python an5.py <sym> <vòng>`, `python final5.py`.
