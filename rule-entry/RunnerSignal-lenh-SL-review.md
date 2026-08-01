# RunnerSignal.cs — Tổng hợp các lệnh SL (thua) để review đối chiếu chart

> Nguồn: `data-export/27-7/RunnerSignal_signals.csv` — đây là **CSV do chính indicator LIVE xuất ra**
> (`ExportCsv=true`), KHÔNG phải backtest Python mô phỏng → khớp 100% với tín hiệu thật đã vẽ trên
> chart Quantower của bạn. Tính đến lúc export (2026-07-30 23:55), toàn bộ lịch sử có **9 lệnh đã
> đóng**: 2 WIN, **7 LOSS** (liệt kê dưới đây). Đây là mẫu còn nhỏ (mới bật export vài ngày) — sẽ cập
> nhật file này khi bạn export CSV mới nhiều lệnh hơn.
>
> **Giờ trong CSV gốc (`ngay_gio`, `ket_thuc_luc`) là giờ UTC** (lấy từ `bar.TimeLeft`, KHÔNG cộng
> lệch múi giờ). Bảng dưới quy đổi sẵn ra **giờ VN (UTC+7)** để bạn dò thẳng trên chart nếu chart bạn
> hiển thị giờ VN. Nếu chart bạn đang hiển thị UTC thì dùng cột UTC.

## Cách review

Với mỗi lệnh: mở đúng nến **giờ vào lệnh** trên chart M1, xem lại đúng chuỗi nến quanh đó, đối chiếu
với **"Lý do hệ thống đưa ra"** — hệ thống có đọc đúng cấu trúc phá/hồi/tiếp diễn (CBR) hay
chạm/từ chối VWAP (QUAY ĐẦU) như bạn thấy trên chart không. Điền vào cột **"Review của bạn"** đúng/sai
và giải thích ngắn — tôi sẽ dùng đúng phần bạn ghi để sửa lại điều kiện trong `RunnerSignal.cs`.

---

## Lệnh SL #1 — CBR SHORT

| | |
|---|---|
| Giờ vào lệnh | **2026-07-28 20:47 VN** (13:47 UTC) |
| Giờ chạm SL | 2026-07-28 20:49 VN (13:49 UTC) — chỉ 2 phút sau khi vào |
| Entry / SL / TP | 4081.9 / 4085.2 / 4072.0 |
| Risk / RR mục tiêu | 3.3 giá / RR 3 |
| VSA lúc phá | 2.34× (climax) |
| Lý do hệ thống đưa ra | phá 4087.0 · hồi 72% · leg 7.2giá · VSA 2.3x tím · **TP vướng vùng ↧1.7R** |
| Ghi chú | "TP vướng vùng ↧1.7R" = có 1 vùng mạnh chắn đường tới TP, cách entry 1.7R — CHỈ LÀ THÔNG TIN HIỂN THỊ, không phải điều kiện chặn lệnh. SL chạm rất nhanh (2 phút) → đáng ngờ giá đã đảo chiều gần như ngay khi vào. |
| **Review của bạn** | _(điền: đúng/sai cấu trúc phá-hồi-tiếp diễn? nếu sai thì sai ở bước nào?)_ |

---

## Lệnh SL #2 — CBR SHORT

| | |
|---|---|
| Giờ vào lệnh | **2026-07-29 08:12 VN** (01:12 UTC) |
| Giờ chạm SL | 2026-07-29 08:28 VN (01:28 UTC) |
| Entry / SL / TP | 4073.1 / 4077.0 / 4061.4 |
| Risk / RR mục tiêu | 3.9 giá / RR 3 |
| VSA lúc phá | 5.58× (climax rất mạnh) |
| Lý do hệ thống đưa ra | phá 4079.5 · hồi 74% · leg 10.3giá · VSA 5.6x tím · **TP vướng vùng ↧0.2R** |
| Ghi chú | Có vùng hợp lưu (`co_vung`=1). "TP vướng vùng ↧0.2R" = vùng mạnh chắn đường CHỈ CÁCH ENTRY 0.2R — rất gần, gần như chắn ngay từ đầu. VSA phá cực lớn (5.58×) nhưng vẫn SL — đáng xem giá phá có phải "phá giả/hút hàng" không. |
| **Review của bạn** | _(điền)_ |

---

## Lệnh SL #3 — QUAY ĐẦU SHORT

| | |
|---|---|
| Giờ vào lệnh | **2026-07-29 11:00 VN** (04:00 UTC) |
| Giờ chạm SL | 2026-07-29 11:25 VN (04:25 UTC) |
| Entry / SL / TP | 4081.1 / 4083.3 / 4077.8 |
| Risk / RR mục tiêu | 2.2 giá / RevRR 1.5 |
| VSA lúc chạm | 1.87× (KHÔNG climax — dưới ngưỡng `VsaClimax`=2.2×) |
| Lý do hệ thống đưa ra | đảo chiều VWAP 4082.175 · rút râu trên · VSA 1.9x |
| Ghi chú | Không có "hấp thụ ✓" trong lý do → không có bonus absorption, VSA cũng không đạt mức climax để override — đây là lệnh "grade B" yếu nhất trong các điều kiện quay đầu (chỉ vừa đủ ngưỡng tối thiểu `RevVsaConf`=1.8×). Xem trên chart nến rút râu này có thực sự là 1 cú từ chối rõ ràng không, hay chỉ là dao động nhiễu quanh VWAP. |
| **Review của bạn** | _(điền)_ |

---

## Lệnh SL #4 — CBR SHORT

| | |
|---|---|
| Giờ vào lệnh | **2026-07-29 17:51 VN** (10:51 UTC) |
| Giờ chạm SL | 2026-07-29 18:15 VN (11:15 UTC) |
| Entry / SL / TP | 4086.0 / 4089.0 / 4077.0 |
| Risk / RR mục tiêu | 3.0 giá / RR 3 |
| VSA lúc phá | 3.72× (climax) |
| Lý do hệ thống đưa ra | phá 4088.7 · hồi 70% · leg 3.3giá · VSA 3.7x tím · **TP vướng vùng ↧0.7R** |
| Ghi chú | Leg (nhịp phá) chỉ 3.3 giá — khá ngắn so với các lệnh khác (7-10 giá) → biên độ dao động của cả đợt phá nhỏ, dễ bị nhiễu nuốt ngược trở lại. Có vùng chắn TP ở 0.7R. |
| **Review của bạn** | _(điền)_ |

---

## Lệnh SL #5 — CBR LONG

| | |
|---|---|
| Giờ vào lệnh | **2026-07-29 18:28 VN** (11:28 UTC) |
| Giờ chạm SL | 2026-07-29 18:35 VN (11:35 UTC) — chỉ 7 phút sau |
| Entry / SL / TP | 4092.7 / 4089.7 / 4101.7 |
| Risk / RR mục tiêu | 3.0 giá / RR 3 |
| VSA lúc phá | 2.75× (climax) |
| Lý do hệ thống đưa ra | phá 4089.3 · hồi 47% · leg 3.2giá · VSA 2.8x tím · **TP vướng vùng ↧0.3R** |
| Ghi chú | ⚠ Hồi chỉ 47% — DƯỚI sàn `PullMin`=60% mà hệ thống đang cấu hình! Cần kiểm tra kỹ vì đây có thể là dấu hiệu **sai lệch giữa số ghi log và điều kiện code** (số 47% ghi trong log có thể là % tính trên cách đo khác, hoặc là lỗi cần soi lại `retr` lúc export). Cách bạn đối chiếu: đo bằng mắt trên chart % hồi thực tế của nhịp giá 4089.3→4092.7 rồi so lại. Lệnh này ưu tiên review trước. Cũng SL rất nhanh (7 phút) + vùng chắn TP chỉ 0.3R. |
| **Review của bạn** | _(điền — ĐẶC BIỆT chú ý số 47% hồi này)_ |

---

## Lệnh SL #6 — CBR SHORT

| | |
|---|---|
| Giờ vào lệnh | **2026-07-29 19:19 VN** (12:19 UTC) |
| Giờ chạm SL | 2026-07-29 19:56 VN (12:56 UTC) |
| Entry / SL / TP | 4077.4 / 4082.2 / 4063.0 |
| Risk / RR mục tiêu | 4.8 giá / RR 3 |
| VSA lúc phá | 5.40× (climax rất mạnh) |
| Lý do hệ thống đưa ra | phá 4084.6 · hồi 61% · leg 6.7giá · VSA 5.4x tím · **TP vướng vùng ↧0.1R** |
| Ghi chú | "TP vướng vùng ↧0.1R" = vùng mạnh chắn đường tới TP gần như NGAY SÁT entry (chỉ 0.1R) — tức về lý thuyết lệnh gần như không có đường thoáng tới TP. Đáng đặt câu hỏi: có nên tự động hạ RR hoặc bỏ qua lệnh khi vùng chắn quá gần (<0.2-0.3R) không? |
| **Review của bạn** | _(điền)_ |

---

## Lệnh SL #7 — QUAY ĐẦU LONG

| | |
|---|---|
| Giờ vào lệnh | **2026-07-30 06:58 VN** (2026-07-29 23:58 UTC) |
| Giờ chạm SL | 2026-07-30 07:01 VN (2026-07-30 00:01 UTC) — chỉ 3 phút sau |
| Entry / SL / TP | 4143.5 / 4141.24 / 4146.891 |
| Risk / RR mục tiêu | 2.3 giá / RevRR 1.5 |
| VSA lúc chạm | 2.45× (climax) |
| Lý do hệ thống đưa ra | đảo chiều VWAP 4141.44 · rút râu dưới · VSA 2.5x tím · **hấp thụ ✓** · TP vướng vùng ↧0.7R |
| Ghi chú | Có "hấp thụ ✓" (bonus, grade cao hơn #3) và VSA climax — về lý thuyết đây là lệnh quay đầu "đẹp" nhất trong 2 lệnh QUAY ĐẦU SL, nhưng vẫn thua chỉ sau 3 phút. Đáng xem kỹ trên chart: giá có thật sự đảo chiều hay chỉ dừng chân tạm rồi đi tiếp xuyên VWAP. |
| **Review của bạn** | _(điền)_ |

---

## Bảng tóm tắt nhanh (để đối chiếu nhanh, không cần đọc lại chi tiết)

| # | Nhánh | Hướng | Giờ vào (VN) | Entry | SL | Risk | VSA | Vùng chắn TP | SL chạm sau |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 1 | CBR | SHORT | 28/07 20:47 | 4081.9 | 4085.2 | 3.3 | 2.34× | 1.7R | 2 phút |
| 2 | CBR | SHORT | 29/07 08:12 | 4073.1 | 4077.0 | 3.9 | 5.58× | 0.2R | 16 phút |
| 3 | QUAY ĐẦU | SHORT | 29/07 11:00 | 4081.1 | 4083.3 | 2.2 | 1.87× | — | 25 phút |
| 4 | CBR | SHORT | 29/07 17:51 | 4086.0 | 4089.0 | 3.0 | 3.72× | 0.7R | 24 phút |
| 5 | CBR | LONG | 29/07 18:28 | 4092.7 | 4089.7 | 3.0 | 2.75× | 0.3R | **7 phút** ⚠ |
| 6 | CBR | SHORT | 29/07 19:19 | 4077.4 | 4082.2 | 4.8 | 5.40× | 0.1R | 37 phút |
| 7 | QUAY ĐẦU | LONG | 30/07 06:58 | 4143.5 | 4141.24 | 2.3 | 2.45× | 0.7R | **3 phút** ⚠ |

**Điểm đáng chú ý tự thấy trước khi bạn review** (không phải kết luận, chỉ để bạn kiểm tra thêm):
- 2 lệnh (#1, #5, #7) chạm SL trong **dưới 10 phút** — SL rất gần, đáng xem có phải entry vào ngay đỉnh/đáy của cú giật hay không.
- Lệnh #5 có số "hồi 47%" thấp hơn sàn cấu hình `PullMin`=60% — **cần soi kỹ nhất**.
- 4/5 lệnh CBR thua đều có "TP vướng vùng" ở khoảng cách rất gần (0.1R–1.7R) — có thể là gợi ý nên thêm điều kiện "không vào nếu vùng mạnh chắn TP quá gần" (hiện tại chỉ là thông tin hiển thị, không phải gate).

---

## Sau khi bạn review xong

Gửi lại theo từng lệnh (số # + đúng/sai + lý do bạn thấy trên chart), tôi sẽ đối chiếu với code
`RunnerSignal.cs` (nhánh CBR ở hàm `Scan()`, nhánh QUAY ĐẦU ở `ScanReversal()`) để sửa đúng điều kiện
bạn chỉ ra, build lại DLL, rồi gửi bạn test tiếp.
