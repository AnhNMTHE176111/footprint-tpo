# OrderFlow Bubbles — bản QUANTOWER (tập trung VÀNG)

Indicator order-flow dạng **bubble/hình** cho **Quantower**, đọc footprint (Volume Analysis) theo
từng mức giá. Triết lý: gom mọi tín hiệu order-flow thành hình trên chart, **bật/tắt từng phần**,
**ngưỡng tương đối** để cùng một cấu hình chạy đúng trên mọi feed/sàn. Cách build & nạp: [BUILD.md](BUILD.md).

> ✅ **Build sạch** trên Linux → `dist/OrderFlowBubbles.dll` (net10.0, khớp Quantower 1.146.x).
> ⚠️ **Chưa chạy thử trên Quantower thật** (Quantower Windows-only, máy dev Linux) — cần add lên
> chart Windows để xác nhận trực quan + tinh chỉnh ngưỡng theo feed.

## ⚠️ Điều kiện bắt buộc
Đọc footprint qua `IVolumeAnalysisIndicator`. Chỉ hiện tín hiệu khi feed **có trade/volume thật**
(futures CME: AMP/CQG, dxFeed, Rithmic…). Feed CFD không volume thật → không có gì. Lần đầu add phải
chờ Quantower **nạp Volume Analysis** (có % tiến trình).

## 🔑 Vì sao "ngưỡng tương đối" — câu chuyện số delta lệch ~4 lần
Cùng 1 nến GC M1, số delta trên ATAS của bạn lớn ~3–4× số của bạn (Sierra). Đó là **tích của nhiều
hệ số**: single- vs double-count volume (~2×), contract GC 100oz vs MGC 10oz (10×), cách gộp lệnh/
phân loại bid-ask giữa feed, filter [CV]… → **mọi ngưỡng SỐ HỢP ĐỒNG tuyệt đối đều vô nghĩa khi đổi
feed**.

Cách chống (đã áp dụng): mọi trigger dùng **thống kê tương đối & robust** —
**modified z-score theo median + MAD** trên baseline động (không dùng mean+std vì volume đuôi nặng,
std bị spike thổi phồng), hoặc **tỷ lệ** `deltaPct = Δ/Volume`. Nhờ vậy **mọi hệ số thang đo triệt
tiêu** → cùng cấu hình chạy đúng cho GC, MGC, hay feed proxy. Knob **tuyệt đối duy nhất** còn lại là
**sàn chống nhiễu** (`MinLevelVolFloor`/`MinBarVolFloor`) cho nến đêm quá mỏng.

## Đọc hình thế nào — hệ mã hoá mới
| Tín hiệu | HÌNH | Kích thước | Màu |
|---|---|---|---|
| **Absorption (hấp thụ)** | ⬤ **tròn ĐẶC** | **cố định = bề rộng nến** (không to/nhỏ) | cyan (đỉnh) / đỏ (đáy) = phe aggressor bị nuốt |
| **Big Trade** | ⬤ **tròn MỜ (halo)** | **to dần theo lệnh đơn lớn nhất** | cyan/đỏ = phe aggressor |
| **Big Delta profile** | ━ **gạch ngang** (rộng = nến) | dày nhẹ theo độ mạnh | **xanh = buy dồn / đỏ = sell dồn** |
| **Nến delta lớn** | **tô thân nến** | cả thân | **xanh (Δ>0) / đỏ (Δ<0)** |
| **Số Delta** | chữ dưới nến | — | xanh/đỏ theo dấu |
| Exhaustion / Divergence / Sweep | ▲ tam giác | vừa | đỉnh→cyan, đáy→đỏ |
| Stacked Imbalance | ◆ thoi | theo ratio | phe áp đảo |
| Unfinished / Stop-hunt | ▭ / ⬤ halo | nhỏ / lớn | 2 phía / phe hấp thụ |

Rê chuột vào bubble → **tooltip** tên tín hiệu + số liệu (z-score, deltaPct…).

## Giải nghĩa & thuật toán (ngưỡng portable, default vàng M1)
| # | Tín hiệu | Cơ chế + test | Default |
|---|---|---|---|
| 1 | **Absorption** | Volume/mức z **cao** + 1 phe áp đảo **tại cực trị** nến + giá **bị chặn** (đóng cửa lùi khỏi cực trị ≥1 tick). | **BẬT** |
| 2 | **Big Trade** | `MaxOneTradeVolume` (lệnh ĐƠN lớn nhất) z ≥ ngưỡng — hoặc fallback volume/mức nếu feed không điền. Size nén **sqrt**. | **BẬT** |
| 3 | **Big Delta line** | 1 mức có net delta lệch mạnh: `|Δ/Vol| ≥ 0.35` **và** `|Δ|` z cao. Giữ **top-N** mức/nến. | **BẬT** |
| 4/5 | **Nến delta lớn** | `|Δ/Vol| ≥ 0.30` **và** `|Δ|` z ≥ 2 **và** volume ≥ 0.8× median → tô thân **theo DẤU DELTA** (không theo close). | **BẬT** |
| 6 | **Exhaustion** | Cực trị swing mới + volume teo + **delta rút khỏi đỉnh intrabar** (dùng `Total.MaxDelta/MinDelta` THẬT). | tắt |
| 7 | **Stacked Imbalance** | Chéo `buy[i]` vs `sell[i-1]` ≥ 3:1, ≥3 mức liên tiếp; min-vol = **median động** (không cố định). | tắt |
| 8 | **Delta Divergence** | Giá HH nhưng CVD LH (ngược ở đáy) tại pivot + **volume pivot ≥ 1.5× median** + cooldown. | tắt |
| 9 | **Liquidity Sweep** | Wick vượt swing cũ + đóng lại trong range + delta ngược dấu. | tắt |
| 10 | **Unfinished** | Đỉnh/đáy còn cả 2 phía (> sàn nhiễu). | tắt |
| 11 | **Stop-hunt + Absorption** | Quét cực trị + hấp thụ ngay đó. | tắt |

> **Absorption vs Exhaustion:** Absorption = volume CAO, giá bị chặn (tường limit). Exhaustion =
> đẩy tới cực trị mới nhưng lực (volume+delta) **teo dần**. Cả hai báo phe thắng sắp hụt hơi.

## Khác biệt so với bản ATAS
1. **Vẽ tay GDI+** (Quantower không có `PriceSelectionValue`) → tự tính + tự vẽ trong `OnPaintChart`.
2. **Exhaustion = đúng intrabar.** Quantower **CÓ** `Total.MaxDelta/MinDelta` (ghi chú port cũ sai) →
   không còn phải xấp xỉ bằng "delta swing".
3. **Big Trade dùng `MaxOneTradeVolume`** (lệnh đơn lớn nhất) — sát nghĩa "cú đánh lớn" hơn tổng
   volume/mức; tự fallback nếu feed không cấp.
4. **Baseline robust median+MAD** (không mean+std) + ngưỡng z/percentile/ratio → **portable feed**.
5. Field map: `BuyVolume↔Ask`, `SellVolume↔Bid`, `Trades↔Ticks`, `Total.Delta/Volume` = cả nến.

## Nên bật gì trên M1 vs M30
| Tín hiệu | M1 | M30 | Ghi chú |
|---|:---:|:---:|---|
| Số Delta + Nến delta | ✅ | ➖ | M1 cần timing; M30 số chồng nhau |
| Absorption | ✅ | ✅ | Ở M30 vùng đảo mạnh hơn |
| Big Trade | ✅ | ✅ | z tự chuẩn hoá nên chạy được cả hai |
| Big Delta line | ✅ | ➖ | Nhiều mức ở HTF dễ rối |
| Exhaustion / Divergence / Sweep | ➖ | ➖ | Thử nghiệm, bật lẻ quan sát |

**Native Quantower nên thêm:** M1 → Cumulative Delta (line) + VWAP; M30 → Volume Profile phiên (VA + HVN/LVN).

## Bảng cấu hình then chốt (Settings)
| Nhóm | Tham số | Ý nghĩa |
|---|---|---|
| Baseline | Số nến (100) · Warm-up (40) · **Sàn nhiễu** vol/mức (5), vol/nến (20) | Cửa sổ median+MAD; sàn = knob tuyệt đối DUY NHẤT, tinh chỉnh theo feed |
| Nến delta | deltaPct (0.30) · z (2.0) · cổng volume (0.8×) · độ đậm tô (85) | Tô thân xanh/đỏ khi delta lớn & 1 chiều |
| Absorption | z (2.5) · áp đảo (0.60) · cách cực trị (2 tick) | Ít bubble → hạ z |
| Big Trade | z (2.5) | Dùng lệnh đơn lớn nhất; nhiều quá → tăng z |
| Big Delta line | deltaPct (0.35) · z (2.0) · top-N (2) | Số gạch ngang mạnh nhất mỗi nến |

## Thông số MGC/GC (Micro/Full Gold)
Tick 0.10. **Không cần** đổi ngưỡng khi chuyển GC↔MGC hay đổi feed — z/ratio tự chuẩn hoá. Chỉ chỉnh
**sàn nhiễu** (`MinLevelVolFloor`/`MinBarVolFloor`) cho khớp thang volume của feed (MGC nhỏ → để thấp;
GC lớn → có thể nâng). Ít tín hiệu → hạ z; nhiễu → tăng z.
