# quantower-entry-signal — Gợi ý điểm vào lệnh (footprint M1)

Indicator M1 real-time gợi ý Entry/SL/TP cho vàng theo cách người dùng đánh (bias + vùng + footprint,
2 kịch bản phá&hồi / chạm&đảo). **Thiết kế đầy đủ ở [PLAN.md](PLAN.md).** Chưa implement.

## Phát hiện then chốt (backtest 28 ngày dữ liệu thật)
- Tín hiệu cơ học **thô** (bắn ở mọi vùng) **không có edge** — tệ hơn ngẫu nhiên (MFE/MAE 0.86 vs 1.05).
- **HỢP LƯU ≥2 vùng chồng nhau = bộ lọc THẬT:** +0.30R@2R (74 lệnh), đơn điệu theo bậc confluence,
  **giữ ở cả 2 nửa tháng** (chống overfit). ~3 lệnh/ngày.
- Phá&hồi > chạm&đảo. SL 2–4đ > 6đ. VSA/climax/VWAP-đơn-lẻ **không** tự tạo edge → chỉ là thành phần hợp lưu.
- Lớp **footprint theo mức giá (hấp thụ/imbalance)** chỉ có **LIVE** → validate bằng log, không backtest được.

## Research (tái lập số)
```bash
python3 research/entry_month.py   # backtest chính 28 ngày (4 cấu hình + soi 2 ví dụ 7/24)
python3 research/research.py      # MFE/MAE vs baseline + subset + SL sweep
python3 research/research2.py     # chống overfit: đơn điệu confluence + chia đôi 28 ngày
python3 research/profile_data.py  # mổ cột dữ liệu (cột sống/chết)
```

## Đã implement (P0–P2) + verify offline
`EntrySignal.cs` — indicator M1 hoàn chỉnh lõi: dựng vùng từ M1, **confluence-gate ≥2**, KB1 phá&hồi,
KB2 chạm&đảo (gate tường hấp thụ `PriceLevels` live), nến-đóng-only, VSA khớp `VsaVolume`, SL≤6đ,
TP nới vùng kế, render mũi tên/nhãn/bảng. Build: `./build-entry.sh` → `dist/EntrySignal.dll` (0 warning).

**Verify offline đã làm:**
- Build sạch Linux (net10.0-windows, concat ProfileEngine).
- **3 agent review đối kháng**: (1) parity từng-dòng vs `research/entry_month.py`, (2) thread-safety/vòng đời,
  (3) C# correctness/GDI/hiệu năng. Đã fix mọi phát hiện thật (lệch index→vùng theo thời gian; rescan mỗi
  tick→1 lần/nến-đóng; try/catch+SetClip; |Δ|≥15, dedup 6t, prev_rel nhị phân; clamp SlCap; risk theo tick).
- Logic scan KHỚP bộ đã backtest (`entry_month.py`); khác biệt còn lại là **cố ý**: vùng volume-based live
  (chính xác hơn TPO offline), gate confl≥2, KB2 cần tường hấp thụ live.

**CHƯA test được offline (bản chất — cần LIVE Windows):**
- Phần glue Quantower (kéo `HistoricalData`, `PriceLevels`, render GDI).
- Tường hấp thụ / imbalance per-level (data export không có ladder).

## Verify LIVE (bước quyết định — cần máy Windows)
1. Copy `dist/EntrySignal.dll` vào `...\Settings\Scripts\Indicators\EntrySignal\`, add vào **chart M1** có Volume Analysis.
2. Kiểm: vùng HỢP LƯU vẽ đúng chỗ, tín hiệu chỉ hiện trên nến ĐÃ ĐÓNG (không nhấp nháy), không lag khi tick nhanh.
3. **Log 1–2 tuần**: đối chiếu tín hiệu A/B với kết quả thật + với lệnh tay của bạn (vd Entry-1 mẫu:
   LONG tại VWAP+VAH Á+VAL Âu, climax tím — indicator phải gắn cờ đúng).
4. Chỉnh input theo feed: `TzOffset`, mốc giờ phiên, `VolFloor`, ngưỡng hấp thụ.
```
