# quantower-tpo-suite — 2 indicator TPO cho Quantower

Bộ 2 indicator (add vào **chart M30**), dùng chung `ProfileEngine`. Xem thiết kế đầy đủ ở **[PLAN.md](PLAN.md)**.

| File | Vai trò |
|---|---|
| `ProfileEngine.cs` | Lõi dùng chung: dựng profile phiên, POC/VA (rule 2 hàng 70%), IB, gom phiên theo gap, cụm POC, naked POC, thống kê. **Không build riêng** — được concat vào đầu mỗi indicator. |
| `DailyTpoBias.cs` | **Bias ngày real-time**: value relationship + POC migration + IB/range-extension + delta → nhãn Tăng/Giảm + độ tin + bảng chữ VN; vẽ VAH/VAL/POC/IB (nay + hôm qua). |
| `M30SessionZones.cs` | **Phiên + vùng**: gộp Á/Âu/Mỹ, tường thuật "phiên nào làm gì" + gợi ý "Mỹ ưu tiên gì"; vẽ vùng (naked POC, cụm POC, biên VA, đỉnh/đáy) + gợi ý target. |
| `build-tpo.sh` | Build Linux: concat `ProfileEngine.cs` + từng indicator → `dist/*.dll`. |
| `prototype_test.py` | Prototype Python đã test thuật toán trên `../data-export/` (POC khớp nền tảng 90%@5t). |

## Build
```bash
./build-tpo.sh          # cả 2
./build-tpo.sh daily    # chỉ DailyTpoBias
./build-tpo.sh m30      # chỉ M30SessionZones
```
Ra `dist/DailyTpoBias.dll` và `dist/M30SessionZones.dll` (đã build sạch 0 warning).

## Deploy (Windows / Optimus Flow)
Chép mỗi DLL vào `...\Settings\Scripts\Indicators\<tên>\`, mở chart **M30** có Volume Analysis, add indicator.

## Cần kiểm khi chạy live (xem PLAN.md §8)
- `bar.TimeLeft` là UTC hay local → chỉnh input **Lệch giờ** của M30SessionZones cho khớp (mặc định +7 VN).
- `GapMinutes` tách ngày/phiên đúng chưa (mặc định 75').
- Feed có điền `PriceLevels` (volume theo giá) không — nếu không, tự fallback về TPO.
- Ranh giới phiên Á/Âu/Mỹ khớp đỉnh khối lượng thật chưa (chỉnh 3 mốc phút).

> **Trạng thái: v1 — build sạch trên Linux, CHƯA test trên feed live.** Cần deploy Windows + chụp lại để hiệu chỉnh ngưỡng.
