# OrderFlow Bubbles — indicator order flow dạng bubble cho ATAS

Indicator **của riêng mình** (cảm hứng từ bản bubble trên Sierra Chart của một người bạn): gom **tất cả tín hiệu order flow** thành bubble/hình trên chart, **bật/tắt từng phần**, default gọn để trade. Thiết kế đầy đủ ở [SPEC.md](SPEC.md); cách build lại DLL ở [BUILD.md](BUILD.md).

> ✅ **Đã build & chạy trong ATAS** (net10.0-windows, bản 8.0.14.392). DLL ở `dist/OrderFlowBubbles.dll`.

## Đọc bubble thế nào — hệ mã hoá 3 kênh
| Kênh | Nghĩa |
|---|---|
| **Màu** | Phe chủ động: **cyan = phe MUA** (thường ở đỉnh) · **đỏ/cam = phe BÁN** (thường ở đáy) |
| **Hình** | Loại tín hiệu: ⬤ Ellipse · ▲ Triangle · ▭ Rectangle · ◆ Diamond |
| **Kích thước** | Độ mạnh (z-score / tỷ lệ volume) — to = mạnh |

**Quy tắc màu (đã làm nhất quán):** mọi tín hiệu ở **ĐỈNH đều cyan**, ở **ĐÁY đều đỏ**.
- Với **Absorption / Big Trade / Delta Surge**: màu = phe aggressor (Ask>Bid → cyan).
- Với **tín hiệu ĐẢO ở cực trị** (Exhaustion / Divergence / Sweep): màu = phe vừa đẩy tạo ra cực trị → **bạn hành động NGƯỢC màu**: cyan ở đỉnh = phe mua sắp hụt hơi → **canh SHORT**; đỏ ở đáy = phe bán sắp hụt hơi → **canh LONG**.

ATAS chỉ có **5 hình** cho ~10 tín hiệu → vài loại **trùng hình**, phân biệt thêm bằng **màu + Tooltip** (rê chuột vào bubble đọc tên tín hiệu).

## Giải nghĩa từng tín hiệu (glossary)

| # | Tín hiệu | Hình | Nó là gì (cơ chế) | Default |
|---|---|---|---|---|
| 1 | **Absorption** (Hấp thụ) | ⬤ halo | Volume LỚN đập 1 phe **nhưng giá đứng yên** (≤2 ticks) → có tường limit hấp thụ hết. Đấm vào tường. | **BẬT** |
| 2 | **Exhaustion** (Kiệt sức) | ▲ | Đợt đẩy cuối **volume teo lại + delta co** → phe chủ động **tự cạn lực**, không phải bị chặn. Xe hết xăng. | **BẬT** |
| 3 | **Stacked Imbalance** (Mất cân bằng chồng) | ◆ | ≥3 **mức giá liên tiếp** có Ask/Bid lệch chéo ≥3:1 → lệnh dồn mạnh 1 phía, thường **động lượng tiếp diễn**. | tắt |
| 4 | **Big Trade** (Lệnh lớn) | ⬤ đặc | 1 mức giá có **volume cực lớn** (≥ ngưỡng hoặc z-score cao) → dấu tay tổ chức. | tắt |
| 5 | **Delta Surge** (Delta bùng nổ) | ⬤ đặc | **Delta ròng cả nến** vọt bất thường (z-score cao) → 1 phe áp đảo đột ngột. | tắt |
| 6 | **Delta Divergence** (Phân kỳ Delta) | ▲ | Giá tạo **đỉnh cao hơn** nhưng CVD/delta tạo **đỉnh thấp hơn** (hoặc ngược ở đáy) → động lượng không xác nhận giá → cảnh báo đảo. | tắt (thử nghiệm) |
| 7 | **Liquidity Sweep** (Quét thanh khoản) | ▲ | Giá **phá đỉnh/đáy cũ rồi đóng cửa ngược lại** + delta ngược → quét stop xong đảo (fakeout). | tắt |
| 8 | **Unfinished Business** (Đấu giá dở dang) | ▭ | Đỉnh/đáy nến **vẫn giao dịch cả 2 phía** (không có phía volume=0) → mức đó "chưa xong", giá hay **quay lại test**. | tắt |
| 9 | **Iceberg** (Lệnh băng trôi, xấp xỉ) | ▭ | 1 mức giá **liên tục nuốt volume lớn** như có limit ẩn tự nạp thêm. | tắt |
| 10 | **Stop-hunt + Absorption** | ⬤ halo | Quét stop tại cực trị **+ hấp thụ ngay tại đó** → bẫy thanh khoản rồi đảo mạnh. | tắt |

> **Absorption vs Exhaustion** (dễ lẫn): Absorption = **volume CAO, bị chặn** (có tường limit). Exhaustion = **volume THẤP dần, tự đuối** (ở cuối 1 con sóng). Cả hai đều báo phe đang thắng sắp hụt hơi → khả năng đảo.

## Nên bật gì trên M1 vs M30

Nguyên tắc: **M1 = bấm nút vào lệnh** (timing), **M30 = đọc bối cảnh/cấu trúc**. Đừng bật hết mọi thứ trên cả hai.

| Tín hiệu | M1 (vào lệnh) | M30 (cấu trúc) | Ghi chú |
|---|:---:|:---:|---|
| Số Delta dưới nến | ✅ Bật | ⬜ Tắt | M1 cần timing; M30 số chồng nhau, tắt cho sạch |
| Absorption | ✅ Bật | ✅ Bật | Hấp thụ ở M30 = vùng đảo mạnh hơn |
| Exhaustion | ✅ Bật | ➖ Tuỳ | |
| **Stacked Imbalance** | ✅ **Bật** | ➖ Tuỳ | Rất hợp M1 (timing lệnh dồn). Min vol MGC → hạ về **10** |
| Big Trade | ⬜ Tắt | ✅ Bật | Lệnh lớn đáng chú ý hơn ở HTF |
| Delta Surge | ⬜ Tắt | ⬜ Tắt | Bật khi muốn soi bùng nổ động lượng |
| Divergence / Sweep | ➖ Thử | ➖ Thử | Thử nghiệm, bật lẻ để quan sát |
| Unfinished / Iceberg / Stop-hunt | ⬜ Tắt | ⬜ Tắt | Nâng cao, bật khi đã quen |

**Native ATAS nên thêm** (indicator này cố ý không làm — ATAS có sẵn tốt hơn):
- **M1:** Cumulative Delta (line), VWAP.
- **M30:** Volume Profile phiên (Value Area + HVN/LVN) để có S/R theo volume.

**Cách phối 2 khung:** M30 thấy vùng đáng chú ý (absorption gần HVN) → xuống M1 chờ **absorption/stacked imbalance cùng chiều** để bấm nút.

## Số Delta dưới nến
In **delta ròng của mỗi nến ngay dưới đáy** (dưới râu nếu có) — khỏi phải đọc cả lưới footprint. Xanh = delta dương (mua ròng) · Đỏ = âm (bán ròng).
- Bật/tắt + cỡ chữ, font, khoảng cách, nền mờ trong nhóm **"Delta Numbers"** (default BẬT).
- **Bị chen số khi zoom xa?** → nâng **"Chỉ vẽ khi bề rộng nến ≥ px"** từ 6 lên **10–12**: zoom xa số tự ẩn, zoom gần mới hiện.

## Bảng cấu hình (Settings)
| Nhóm | Tham số then chốt | Ý nghĩa |
|---|---|---|
| **Baseline** | Số nến baseline (50) | Cửa sổ tính volume/delta trung bình để so z-score |
| | Mẫu tối thiểu (40) | Chưa đủ nến thì chưa báo (tránh nhiễu đầu phiên) |
| **Absorption** | Volume z-score ≥ (2) | Volume cao hơn TB 2 độ lệch chuẩn. Ít bubble → hạ **1.5** |
| | Tỷ lệ 1 phe áp đảo ≥ (0.6) | 60% volume nghiêng 1 phe |
| | Giá dịch tối đa (2 ticks) | Volume lớn mà giá đứng = bị hấp thụ (cốt lõi) |
| **Exhaustion** | Volume ≤ 0.6× nến trước | Đợt đẩy cuối cạn lực |
| | Delta co ≤ 0.4× đỉnh intrabar | Động lượng tụt |
| **Stacked Imb.** | Tỷ lệ chéo 300% (=3:1) · min vol 15 · 3 mức | MGC → hạ min vol về **10** |
| **Big Trade** | Vol/**mức** ≥ 20 **hoặc** z ≥ 2.5 | Lệnh lớn tại **1 mức giá** (không phải cả nến). Xem lưu ý bên dưới |

## Thông số MGC (Micro Gold) — để đặt ngưỡng
- Tick size **0.10**, tick value **$1**, point value **$10**. (Code đọc `InstrumentInfo.TickSize` lúc chạy.)
- Volume MGC nhỏ → **ít bubble thì GIẢM** các ngưỡng (z-score, min volume); **nhiễu thì TĂNG**.

### ⚠️ Lưu ý Big Trade trên MGC M1 (rút từ buổi 2026-07-22)
- Big Trade đo `lvl.Volume` = **volume tại MỘT MỨC GIÁ** (một hàng footprint), **không phải volume cả nến**. Điều kiện bắn: `vol/mức ≥ MinVolume` **HOẶC** `z-score ≥ Z`.
- Trên **MGC M1**, volume mỗi mức rất nhỏ: điển hình **5–15**, đỉnh **~30–32**. → Đặt **"Volume tối thiểu/mức = 70" là VÔ HIỆU** (không mức nào chạm) → mọi vòng tròn khi đó **chỉ đến từ nhánh z-score**, chỉnh số tuyệt đối không có tác dụng.
- Nếu vẫn dùng Big Trade ở M1: đặt **Volume/mức ≈ 25** (bắt đúng mức nổi trội) và **z ≈ 3.0** (hoặc z = 99 để tắt hẳn nhánh z, chỉ dùng ngưỡng tuyệt đối). Vòng tròn sẽ thưa và có nghĩa.
- **Khuyến nghị:** micro gold M1 volume/mức quá nhỏ nên "lệnh lớn" ít ý nghĩa → **TẮT Big Trade ở M1**, để **BẬT ở M30** (mỗi mức gom volume lớn hơn). Ngưỡng M1 **không** áp sang M30 — phải canh lại theo footprint M30.
- Vòng tròn **đặc** (solid) = Big Trade / Delta Surge; vòng tròn **halo** (mờ viền) = Absorption. Cụm vòng to ở các nến delta mạnh thường là **Absorption** (giữ lại), không phải Big Trade.

## Tinh chỉnh & kiểm nghiệm
1. Bật **chỉ Absorption + Exhaustion** trước, chỉnh ngưỡng tới khi bubble khớp các điểm giá đảo thật trên MGC M1.
2. So bubble với **Big Trades / Cluster Search native** của ATAS để canh ngưỡng volume.
3. Chụp "giá SAU khi có bubble" → xác nhận đúng/sai từng loại, gửi lại để cùng canh.
