# KB4 — QUAY ĐẦU TẠI VÙNG MẠNH + ARM→CONFIRM (2026-07-30)

> Yêu cầu người dùng: (1) kịch bản quay đầu **không chỉ ở VWAP** mà ở **các vùng mạnh**;
> (2) nến quay đầu chưa đủ điều kiện thì **chờ nến tín hiệu** rồi vào, nến quay đầu đẹp thì
> **vào luôn**. Câu hỏi: cải thiện bao nhiêu R?
>
> Script: [probe_kb4_zone.py](../probe_kb4_zone.py) · [kb4_validate.py](../kb4_validate.py) ·
> [kb4_null.py](../kb4_null.py). Đặc tả chốt trước khi chạy nằm trong docstring của file đầu.

## 1. Thiết kế

| | |
|---|---|
| **Vùng** | `build_zones()` = đúng pool indicator đang vẽ: POC/VAH/VAL/Đỉnh/Đáy từng phiên (A/ÂU/MỸ) + D-1 VAH/VAL/POC/High/Low. VWAP tính như 1 vùng ⇒ KB4 **bao trùm** KB2. |
| **Chạm** | LONG: `low ≤ Z + 7t` và `low ≥ Z − 20t` (chạm/xuyên nhẹ, không phá sâu) + đến từ trên + đóng lại trên Z. SHORT gương lại. |
| **Nhánh A (vào luôn)** | nến chạm thoả y nguyên gate KB2: râu ≥50%, cpos ≥0.55, thân ≥0.30, VSA ≥1.8 |
| **Nhánh B (arm→confirm)** | nến chạm chỉ cần râu ≥30% + đóng đúng phía ⇒ ARM. Trong ≤8 nến chờ nến tín hiệu: `close > high nến arm`, thân ≥0.45, cùng chiều, VSA ≥1.2. Huỷ nếu đóng xuyên vùng (Z−10t) hoặc hết cửa sổ. |
| **SL** | cực trị cửa sổ arm..confirm − 2t. **Bỏ** cách neo `min(low, vwap)` của bản cũ (chính nó gây risk 153 tick → bị cap loại). |
| **Lọc thêm (vòng 2)** | 1 arm/phía · 1 lệnh/vùng/ngày · nhịp đi vào vùng ≥5 giá trong 15 nến |
| Cửa sổ đo | 2026-05..07 (GCQ26 chỉ thanh khoản từ tháng 5) |

## 2. Kết quả — có cải thiện R, rõ rệt

| Cấu hình | n | WR | EV | net | Theo tháng |
|---|---|---|---|---|---|
| **KB2 VWAP (đang ship)** @1.5R | 27 | 56% | +0.389 | **+10.5R** | 05:+2 06:+2 07:+6 |
| KB4 thô, chưa lọc @1.5R | 1653 | 40% | −0.006 | −9.5R | 05:−6 06:+10 07:−14 |
| **KB4-C3 (trend ON)** @2R | 304 | 38% | +0.135 | **+41.0R** | 05:+14 06:+9 07:+18 |
| **KB4-C3 (trend OFF)** @2R | 579 | 36% | +0.088 | **+51.0R** | 05:+9 06:+8 07:+34 |
| — chỉ nhánh A (vào luôn) @2R | 59 | 42% | +0.271 | +16.0R | 05:+3 06:+2 07:+11 |
| — chỉ nhánh B (chờ confirm) @2R | 281 | 38% | +0.132 | +37.0R | 05:+15 06:+10 07:+12 |

**⇒ Cải thiện thô: +10.5R → +41R (hoặc +51R nếu tắt lọc trend), tức +30…+40R / 3 tháng.**
Sau phí 2 tick/lệnh: KB4-C3 còn **+23.5R**, KB2 còn +7.9R ⇒ cải thiện thực **≈ +16R**.

Cả **hai** ý của người dùng đều đóng góp: nhánh A EV cao nhất (+0.271) nhưng ít lệnh;
nhánh B mang phần lớn tổng R (+37R). "Chờ nến tín hiệu" là ý **đúng và có giá trị đo được**.

### Chi tiết đáng chú ý
- **KB4 thô KHÔNG có edge** (EV −0.006, WR 40% = đúng break-even 1.5R). ~48 vùng active cùng lúc,
  33% số nến chạm vùng ⇒ "chạm vùng mạnh" một mình là **vô nghĩa**. Cả R đến từ 3 bộ lọc chọn lọc.
- Lọc mạnh nhất: **1 lệnh/vùng/ngày** (1653→1111) và **nhịp vào vùng ≥5 giá** (bỏ trường hợp giá bò
  ngang cạ vùng liên tục). Đây là 2 thứ biến nhiễu thành tín hiệu.
- Phân bố theo loại vùng @2R: Đáy phiên +21R · VWAP +19R · VAL +8R · POC +3R · **Đỉnh −3R · VAH −4R**.
  Edge lệch hẳn về phía **đỡ**, phía **kháng cự âm**.
- Lọc trend **không cần** cho KB4 (tắt còn nhiều R hơn) — khác KB1/KB2.
- `mincl ≥ 2` (hợp lưu) làm **TỆ** (−20.5R), khớp bài học cũ trong `reversal_vwap.py`: pool dày ⇒
  "hợp lưu" tự động = nhiễu.

## 3. Kiểm định — CHƯA đủ để bật live

| Test | Kết quả | Đánh giá |
|---|---|---|
| Holdout 3-4/2026 | **n = 0** | Vô hiệu: volume tháng 1–4 chỉ 1–2/nến → chặn ở `Gate()`. **Không có cửa sổ độc lập nào trong data local.** |
| So mô hình ngẫu nhiên (400–500 lần, cùng phía/risk/pool) | trend ON: **percentile 95.5%, z +1.76** · trend OFF: **94.5%, z +1.66** | ~1.7σ. **Không đạt ý nghĩa thống kê.** |
| Đa phép thử | đã thử **~25 cấu hình** | Kỳ vọng max của 25 lần rút ≈ percentile 96% ⇒ kết quả tốt nhất **đúng bằng mức nhiễu sinh ra được**. |
| Độ ổn định tham số | **cao nguyên, không phải đỉnh đơn độc** | ✅ Điểm cộng thật: `leg_min` 2→6 (+35/+26/+48/+41/+37), `w` 4→12 (+44/+52/+41/+32/+30), `ztol` 4→14 (+33…+46), `body_c`/`pen_t`/`cap_t` đều dương. |
| Mọi tháng dương | ✅ ở mọi biến thể | Điểm cộng |
| Phí | 0/1/2/3 tick → +41/+32/+23.5/+14.8R | Chịu được phí, nhưng EV mỏng (+0.135) nên nhạy |
| MDD | **25R** trên net 41R | Cao. 304 lệnh/3 tháng ≈ 3.4 lệnh/ngày |

**Phán quyết:** ý tưởng **đúng hướng và đo được cải thiện**, nhưng bằng chứng ở mức 1.7σ trên
**một** cửa sổ, **một** hợp đồng, sau ~25 lần thử — chưa vượt cổng audit. Điểm cộng duy nhất đáng
tin là **cao nguyên tham số** (không phải trúng số một điểm).

## 4. Bước tiếp — cách lấy bằng chứng thật

1. **Dữ liệu độc lập** (việc còn nợ từ v5): front-month liên tục / CCPA / hoặc test cơ chế trên
   symbol khác. Đây là thứ duy nhất kết luận được overfit hay không bằng backtest.
2. **Chạy song song dạng CHỈ GHI LOG:** port KB4 vào DLL nhưng **không** gửi MT5/Telegram, chỉ
   ghi CSV. Chạy forward 2–4 tuần ⇒ có OOS thật, rủi ro bằng 0. Kỳ vọng ~3.4 lệnh/ngày ⇒ n≈70–90
   sau 4 tuần, đủ để thấy EV có sống sót hay không.
3. Nếu forward giữ EV ≥ +0.10R sau phí ⇒ mới bật gửi lệnh.

**KHÔNG** bật KB4 gửi lệnh thật ngay ở bước này.
