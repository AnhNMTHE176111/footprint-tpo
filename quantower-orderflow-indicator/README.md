# OrderFlow Bubbles — bản QUANTOWER (port từ ATAS)

Indicator order flow dạng **bubble** cho **Quantower**, port từ bản ATAS ở [../atas-orderflow-indicator/](../atas-orderflow-indicator/). Cùng triết lý: gom **mọi tín hiệu order flow** thành bubble/hình trên chart, **bật/tắt từng phần**, default gọn để trade. Cách build & nạp: [BUILD.md](BUILD.md).

> ✅ **Build sạch** trên Linux → `dist/OrderFlowBubbles.dll` (net10.0, khớp Quantower 1.146.x).
> ⚠️ **Chưa chạy thử trên Quantower thật** (Quantower là Windows-only, máy dev là Linux) — cần bạn add lên chart Windows để xác nhận trực quan.

## ⚠️ Điều kiện bắt buộc
Indicator đọc **footprint (Volume Analysis)** qua `IVolumeAnalysisIndicator`. Chỉ hiện bubble khi data feed **có trade/volume thật** (futures CME: AMP/CQG, dxFeed, Rithmic…). Feed CFD không volume thật → không có bubble. Lần đầu add phải chờ Quantower **nạp Volume Analysis** (có % tiến trình).

## Đọc bubble thế nào — hệ mã hoá 3 kênh (giống ATAS)
| Kênh | Nghĩa |
|---|---|
| **Màu** | Phe chủ động: **cyan = phe MUA** (thường ở đỉnh) · **đỏ/cam = phe BÁN** (thường ở đáy) |
| **Hình** | Loại tín hiệu: ⬤ Ellipse · ▲ Triangle · ▭ Rectangle · ◆ Diamond |
| **Kích thước** | Độ mạnh (z-score / tỷ lệ volume) — to = mạnh |
| **Kiểu tô** | **Đặc** = tín hiệu chủ động · **Halo (viền + tô mờ)** = Absorption / Stop-hunt |

**Quy tắc màu:** tín hiệu ở **ĐỈNH → cyan**, ở **ĐÁY → đỏ**.
- Absorption / Big Trade / Delta Surge: màu = phe aggressor (BuyVolume>SellVolume → cyan).
- Tín hiệu ĐẢO ở cực trị (Exhaustion / Divergence / Sweep): màu = phe vừa đẩy tạo cực trị → **hành động NGƯỢC màu** (cyan ở đỉnh = canh SHORT; đỏ ở đáy = canh LONG).

Rê chuột vào bubble → hiện **tooltip** tên tín hiệu + số liệu.

## Giải nghĩa từng tín hiệu (glossary)
| # | Tín hiệu | Hình | Cơ chế | Default |
|---|---|---|---|---|
| 1 | **Absorption** | ⬤ halo | Volume LỚN đập 1 phe **nhưng giá đứng** (≤2 ticks) → có tường limit hấp thụ. | **BẬT** |
| 2 | **Exhaustion** | ▲ | Đợt đẩy cuối **volume teo + delta co** → phe chủ động tự cạn lực. *(xem lưu ý port)* | **BẬT** |
| 3 | **Stacked Imbalance** | ◆ | ≥3 **mức giá liên tiếp** Ask/Bid lệch chéo ≥3:1 → lệnh dồn 1 phía, động lượng tiếp diễn. | tắt |
| 4 | **Big Trade** | ⬤ đặc | 1 mức giá volume cực lớn (≥ ngưỡng hoặc z cao) → dấu tay tổ chức. | tắt |
| 5 | **Delta Surge** | ⬤ đặc | Delta ròng cả nến vọt bất thường (z cao) → 1 phe áp đảo đột ngột. | tắt |
| 6 | **Delta Divergence** | ▲ | Giá đỉnh cao hơn nhưng CVD đỉnh thấp hơn (ngược ở đáy) → cảnh báo đảo. | tắt (thử nghiệm) |
| 7 | **Liquidity Sweep** | ▲ | Phá đỉnh/đáy cũ rồi đóng ngược + delta ngược → quét stop xong đảo (fakeout). | tắt |
| 8 | **Unfinished Business** | ▭ | Đỉnh/đáy nến còn giao dịch cả 2 phía → mức "chưa xong", giá hay quay lại test. | tắt |
| 9 | **Iceberg (proxy)** | ▭ | 1 mức liên tục nuốt volume lớn + nhiều lệnh như có limit ẩn tự nạp. | tắt |
| 10 | **Stop-hunt + Absorption** | ⬤ halo | Quét stop tại cực trị + hấp thụ ngay đó → bẫy thanh khoản rồi đảo. | tắt |

> **Absorption vs Exhaustion:** Absorption = volume CAO, bị chặn (tường limit). Exhaustion = volume THẤP dần, tự đuối (cuối 1 con sóng). Cả hai báo phe đang thắng sắp hụt hơi.

## Khác biệt so với bản ATAS (đọc kỹ)
Port bám sát logic ATAS, nhưng Quantower có vài chỗ khác về mặt API nên có **điều chỉnh**:
1. **Vẽ tay bằng GDI+.** ATAS có `PriceSelectionValue` vẽ sẵn theo mức giá; Quantower không có → indicator **tự tính tín hiệu và tự vẽ** trong `OnPaintChart`. Bubble neo theo (thời gian nến, giá mức).
2. **Exhaustion — điều chỉnh.** ATAS dùng **delta chạy trong nến** (MaxDelta/MinDelta intrabar) để đo "delta co lại". Quantower **không cung cấp delta intrabar** → bản này so delta nến hiện tại với **delta lớn nhất/nhỏ nhất của cụm nến gần đây (swing)**. Tinh thần "động lượng cạn ở cực trị" giữ nguyên, nhưng con số **không giống hệt** ATAS.
3. **Footprint field mapping:** `BuyVolume` ↔ ATAS `Ask`, `SellVolume` ↔ ATAS `Bid`, `Trades` ↔ ATAS `Ticks`, `Total.Delta/Total.Volume` ↔ delta/volume cả nến.
4. **Iceberg** dùng `Trades` (số lệnh) thay cho `Ticks` — cùng ý nghĩa "1 mức khớp rất nhiều lần".

## Nên bật gì trên M1 vs M30 (giống ATAS)
Nguyên tắc: **M1 = bấm nút vào lệnh**, **M30 = đọc bối cảnh**. Đừng bật hết trên cả hai.

| Tín hiệu | M1 | M30 | Ghi chú |
|---|:---:|:---:|---|
| Số Delta dưới nến | ✅ | ⬜ | M1 cần timing; M30 số chồng nhau |
| Absorption | ✅ | ✅ | Hấp thụ ở M30 = vùng đảo mạnh hơn |
| Exhaustion | ✅ | ➖ | |
| Stacked Imbalance | ✅ | ➖ | Min vol MGC → hạ về **10** |
| Big Trade | ⬜ | ✅ | Lệnh lớn đáng chú ý hơn ở HTF (M1 volume/mức quá nhỏ) |
| Delta Surge | ⬜ | ⬜ | Bật khi muốn soi bùng nổ động lượng |
| Divergence / Sweep | ➖ | ➖ | Thử nghiệm, bật lẻ để quan sát |
| Unfinished / Iceberg / Stop-hunt | ⬜ | ⬜ | Nâng cao |

**Native Quantower nên thêm:** M1 → Cumulative Delta (line) + VWAP; M30 → Volume Profile phiên (Value Area + HVN/LVN). Quantower có sẵn Footprint/Cluster + Volume Profile rất tốt — indicator này chỉ lo phần **bubble tín hiệu**.

## Bảng cấu hình (Settings)
Tham số xếp theo nhóm tiền tố tên (`Absorption · …`, `Big Trade · …`). Then chốt:
| Nhóm | Tham số | Ý nghĩa |
|---|---|---|
| Baseline | Số nến baseline (50) · Mẫu tối thiểu (40) | Cửa sổ tính volume/delta TB để so z-score |
| Absorption | Volume z-score ≥ (2.0) · Tỷ lệ 1 phe (0.6) · Giá dịch tối đa (2 ticks) | Ít bubble → hạ z về 1.5 |
| Exhaustion | Volume ≤ 0.6× nến trước · Delta co ≤ 0.4× đỉnh swing | |
| Stacked Imb. | Chéo 300% · min vol 10 · 3 mức | MGC volume nhỏ → min vol 10 |
| Big Trade | Vol/mức ≥ 25 **hoặc** z ≥ 3.0 | Lệnh lớn tại **1 mức giá**. MGC M1 volume/mức nhỏ → nên bật ở M30 |

## Thông số MGC (Micro Gold)
Tick 0.10, tick value $1, point value $10. Volume MGC nhỏ → **ít bubble thì GIẢM** ngưỡng, **nhiễu thì TĂNG**. Big Trade trên M1 volume/mức chỉ ~5–15 → nên **tắt ở M1, bật ở M30** (xem README bản ATAS để rõ hơn).
