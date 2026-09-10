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
