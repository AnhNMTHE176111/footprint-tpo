# quantower-tpo-suite — 2 indicator TPO cho Quantower

Bộ 2 indicator, dùng chung `ProfileEngine`. Xem thiết kế đầy đủ ở **[PLAN.md](PLAN.md)**.

| File | Vai trò |
|---|---|
| `ProfileEngine.cs` | Lõi dùng chung: dựng profile phiên, POC/VA (rule 2 hàng 70%), IB, gom phiên theo gap, cụm POC, naked POC, HVN/LVN, thống kê. **Không build riêng** — được concat vào đầu mỗi indicator. |
| `DailyTpoBias.cs` | **Bias ngày real-time**: value relationship + POC migration + IB/range-extension + delta → nhãn Tăng/Giảm + độ tin + bảng chữ VN; vẽ VAH/VAL/POC/IB (nay + hôm qua). |
| `SessionZones.cs` | **Phiên + vùng**: gộp Á/Âu/Mỹ, tường thuật "phiên nào làm gì" + gợi ý "Mỹ ưu tiên gì"; vẽ vùng canh lệnh (HVN tuần/ngày, naked POC, cụm POC) + bối cảnh phiên (VAH/VAL/đỉnh-đáy) + LVN. Add vào chart bất kỳ (M1, M5...) — **tự lấy dữ liệu M30** của cùng symbol nếu chart không phải M30 (xem `OnInit()`). |
| `build-tpo.sh` | Build Linux: concat `ProfileEngine.cs` + từng indicator → `dist/*.dll`. |
| `prototype_test.py` | Prototype Python đã test thuật toán trên `../data-export/` (POC khớp nền tảng 90%@5t). |

## Build
```bash
./build-tpo.sh          # cả 2
./build-tpo.sh daily    # chỉ DailyTpoBias
./build-tpo.sh zones    # chỉ SessionZones
```
Ra `dist/DailyTpoBias.dll` và `dist/SessionZones.dll` (đã build sạch 0 warning).

## Deploy (Windows / Optimus Flow)
Chép mỗi DLL vào `...\Settings\Scripts\Indicators\<tên>\`, mở chart có Volume Analysis, add indicator. `SessionZones` add được vào chart bất kỳ (kể cả M1 để canh entry) — nó tự lấy M30 phía sau; `DailyTpoBias` vẫn cần chart ngày/phù hợp như cũ.

## Báo Telegram (tổng hợp đầu ngày + trước phiên Mỹ)
Hai indicator tự **gộp bias + vùng thành 1 tin** và bắn về Telegram tại 2 mốc/ngày:
- **☀️ Đầu ngày** — ngay khi ngày mới đủ nến qua IB (bias vừa "đủ").
- **🇺🇸 Trước phiên Mỹ 30'** — mặc định mốc 19:20 VN (COMEX vàng mở pit) → bắn ~18:50.

**Cơ chế:** mỗi indicator ghi phần của mình ra file chung (`%LOCALAPPDATA%\TpoSuite\sec_<symbol>_<bias|zone>.txt`); indicator nào có token sẽ đọc CẢ 2 phần, gộp rồi gửi. **Khoá nguyên tử** (`sent_<symbol>_<ngày>_<mốc>.lock`) đảm bảo **1 tin/mốc/ngày** kể cả khi cả 2 indicator cùng cầm token. Chỉ chạy khi Quantower đang mở + dữ liệu live.

**Cài đặt:**
1. Telegram → **@BotFather** → `/newbot` lấy **bot token**; nhắn 1 câu cho bot rồi mở `https://api.telegram.org/bot<TOKEN>/getUpdates` lấy **chat_id**.
2. Trên chart: bật **"Gửi Telegram"** ở CẢ HAI indicator; điền **Bot token + Chat ID** vào MỘT indicator (khuyến nghị SessionZones — giàu dữ liệu vùng hơn). Cái còn lại chỉ cần bật để ghi phần của nó.
3. Bấm **"TG · Gửi thử ngay"** (bật rồi tắt) để test — nếu nhận được tin là xong.

**Lưu ý:** mốc "trước phiên Mỹ" dùng giờ tường (wall-clock) + `Lệch giờ` (giả định `bar.TimeLeft` là UTC). Mùa đông Mỹ (EST) mốc 19:20 lùi thành 20:20 VN → chỉnh lại ô **"TG · Phiên Mỹ mở"** (=1220) khi đổi mùa. Mốc "đầu ngày" tính theo số nến sau IB nên KHÔNG lệ thuộc DST.

## Cần kiểm khi chạy live (xem PLAN.md §8)
- `bar.TimeLeft` là UTC hay local → chỉnh input **Lệch giờ** của SessionZones cho khớp (mặc định +7 VN).
- `GapMinutes` tách ngày/phiên đúng chưa (mặc định 75').
- Feed có điền `PriceLevels` (volume theo giá) không — nếu không, tự fallback về TPO.
- Ranh giới phiên Á/Âu/Mỹ khớp đỉnh khối lượng thật chưa (chỉnh 3 mốc phút).

> **Trạng thái: v1 — build sạch trên Linux, CHƯA test trên feed live.** Cần deploy Windows + chụp lại để hiệu chỉnh ngưỡng.
