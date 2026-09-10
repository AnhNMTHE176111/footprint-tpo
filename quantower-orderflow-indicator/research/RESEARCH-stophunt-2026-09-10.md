# Stop-hunt + Sweep — đo lần đầu (2026-09-10)

**Kết luận: KHÔNG có lợi thế. Giữ `StopHuntEnabled = false` và `SweepEnabled = false`.**

Đây là lần đầu hai tín hiệu này được đo. Trước đó chúng ship ở trạng thái TẮT và
chưa từng có backtest nào (đã grep toàn repo).

## Dữ liệu
- `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv` (+ `_bars.csv`)
- 724.279 nến M1, 2024-08-01 → 2026-08-19. Loại 48 nến nối hợp đồng (nhảy giá giả)
  và mọi cửa sổ vắt qua chúng.

## Điều kiện tín hiệu (copy đúng từ `TryStopHunt`)
Đỉnh: `high > max(high[-8..-1])` **và** `close < ` mức đó **và** ô giá tại đỉnh có
`ModZ(volume) ≥ 2,5` **và** `BuyVolume > SellVolume`. Đáy đối xứng.

## Kết quả 1 — đảo chiều đúng hướng (rào đối xứng ±1× median range 100 nến, 20 nến)

| | n | đảo chiều trước | |
|---|---|---|---|
| **Stop-hunt đỉnh** | 602 | **52,8%** ±2,0 | +2,7pp so nền, **1,4σ** |
| sweep-only đỉnh | 50.474 | 49,9% ±0,2 | — |
| **Stop-hunt đáy** | 496 | **49,0%** ±2,2 | **dưới** nền |
| sweep-only đáy | 48.915 | 49,4% ±0,2 | — |
| đối chứng mọi nến | 709.283 | 50,1% ±0,1 | — |

Hai phía **ngược dấu nhau** → không phải cơ chế thật. Và bản thân "sweep-only"
(quét qua đỉnh 8 nến rồi đóng lại vào trong) = 49,9%, tức **tiền đề "quét thanh
khoản ⇒ đảo chiều" đã sai ngay từ mức nền**.

## Kết quả 2 — E[R] thật (vào tại close, SL = cực trị nến ±1 tick, TP 2R)

SL trung vị chỉ **9 tick** (đỉnh) / 11 tick (đáy) → phí ăn rất nặng theo tỷ lệ R.

| phí khứ hồi | E[R] đỉnh (bán) | E[R] đáy (mua) |
|---|---|---|
| 0 tick | +0,162 ±0,058 (t=2,8) | +0,040 ±0,061 (t=0,7) |
| 1 tick | +0,036 ±0,058 (t=0,6) | — |
| 2 tick | **−0,091** ±0,058 | **−0,187** ±0,061 |

Chỉ 1 tick phí là xoá sạch. Tách đôi thời gian (phí 2 tick, phía đỉnh):
nửa đầu **−0,295** ±0,082 · nửa sau **+0,085** ±0,081 → **ngược dấu nhau**, đúng
kiểu hỏng đã gặp ở HVN.

## Ghi chú cơ chế
`StopHuntLookback = 8` nghĩa là "đỉnh 8 phút gần nhất" — quá cục bộ. Lệnh dừng lỗ
thật đọng ở đỉnh/đáy PHIÊN, mức ngày, số tròn. Nếu muốn thử lại thì phải neo vào
các mức đó chứ không phải swing 8 nến; nhưng chưa đo thì vẫn không được bật.

Script: `scratchpad/stophunt.py` (chạy lại được, ~4 phút trên file 583MB).

---

# Bổ sung — đi tìm "bối cảnh chung" của các ca ĐẢO CHIỀU ĐÚNG

Câu hỏi: trong số các ca stop-hunt có đảo chiều đúng hướng, chúng có đặc điểm gì chung?

**Kết luận: KHÔNG tìm được đặc điểm nào. Ca đúng và ca sai trông giống hệt nhau.**

## Cách làm (chống tự lừa)
Gộp cả hai phía, n = **1.098** tín hiệu, tỷ lệ đảo chiều chung **51,1%**.
**Tách đôi theo thời gian**: dùng **nửa đầu để TÌM** (chọn nhóm 1/3 tốt hơn của mỗi đặc
điểm), rồi **nửa sau để KIỂM CHỨNG**. Không làm vậy thì thử 8 đặc điểm kiểu gì cũng ra
một cái "đẹp" do ngẫu nhiên.

⚠️ Bẫy quan trọng: nền của **nửa sau tự nó đã là 52,8%** (nửa đầu chỉ 49,1% — tức bản
thân tín hiệu cũng không ổn định). Phải so nhóm chọn ra với **52,8%**, không phải với 50%.

## Kết quả

| đặc điểm | nhóm chọn ở nửa đầu | nửa sau (kiểm chứng) | so nền 52,8% |
|---|---|---|---|
| độ đậm ô cực trị (vZ) | thấp | 53,0% ±3,4 | +0,2 |
| độ rộng nến / median | hẹp | 51,2% ±3,4 | −1,6 |
| khối lượng nến / median | cao | 52,5% ±4,2 | −0,3 |
| close lùi khỏi cực trị | ít | 50,0% ±3,2 | −2,8 |
| vượt qua đỉnh cũ bao nhiêu tick | sâu | 53,6% ±2,5 | +0,8 |
| delta nến ủng hộ đảo chiều | — | 52,9% ±3,8 | +0,1 |
| đã chạy bao nhiêu R trước đó | ít | 51,3% ±4,1 | −1,5 |
| delta % của ô cực trị | cao | 53,0% ±3,3 | +0,2 |

Mọi ô đều nằm trong ±3pp quanh nền, sai số ±3pp. **Không có gì.**

## Theo phiên (giờ UTC, chưa tách đôi nên còn yếu hơn)
Á 00-07: 49,2% (n=427) · Âu 07-13: 52,8% (n=303) · Mỹ 13-20: 52,8% (n=246) · 20-24: 50,0% (n=122).
Chênh ~3,6pp với sai số 2,4-4,5pp → không kết luận được.

## Giới hạn phải nói rõ
n = 1.098 chia thành nhóm chỉ còn 150-400 mỗi nhóm ⇒ sai số ±3-4pp ⇒ phép đo này chỉ
thấy được hiệu ứng **từ ~8pp trở lên**. Một hiệu ứng thật nhưng nhỏ (2-3pp) sẽ vô hình ở
đây. Nhưng hiệu ứng nhỏ như vậy cũng không giao dịch được: phần trên đã đo SL trung vị
chỉ 9 tick nên **1 tick phí đã xoá +0,126R**.

Script: `scratchpad/build_cache.py` + `scratchpad/context.py`.
