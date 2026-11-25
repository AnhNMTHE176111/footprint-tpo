# quantower-tpo-suite — 2 indicator TPO cho Quantower

Bộ 2 indicator, dùng chung `ProfileEngine`. Xem thiết kế đầy đủ ở **[PLAN.md](PLAN.md)**.

| File | Vai trò |
|---|---|
| `ProfileEngine.cs` | Lõi dùng chung: dựng profile phiên, POC/VA (rule 2 hàng 70%), IB, gom phiên theo gap, cụm POC, naked POC, HVN/LVN, thống kê. **Không build riêng** — được concat vào đầu mỗi indicator. |
| `DailyTpoBias.cs` | **Bias ngày real-time**: value relationship + POC migration + IB/range-extension + delta → nhãn Tăng/Giảm + độ tin + bảng chữ VN; vẽ VAH/VAL/POC/IB (nay + hôm qua). |
| `SessionZones.cs` | **Phiên + vùng**: gộp Á/Âu/Mỹ, gợi ý "Mỹ ưu tiên gì" cho Telegram; vẽ **vùng mạnh** và **hộp HVN** (dưới). Lớp phụ tắt mặc định: LVN ngày, VAH/VAL hôm nay, đường VWAP tuần/ngày. HVN kiểu cũ (đỉnh nhọn), mục tiêu chốt lời và các lớp "Đo ·" đã **bỏ hẳn** (2026-11-25). Add vào chart bất kỳ (M1, M5...) — **tự lấy dữ liệu M30** của cùng symbol nếu chart không phải M30. |
| `SessionZones` · **vùng mạnh** (2026-11-25) | Cụm ≥ 3 đỉnh/đáy M30 bật lại ≥ 1 U (U = biên độ TB nến M30 của 5 phiên đã đóng) trong 5 phiên gần nhất, **hợp lưu** với mức của phiên/tuần **đã đóng**: VWAP/±1σ và VAH/VAL hôm qua + tuần trước, hộp HVN ngày/tuần (giá đã rời mép hộp ≥ 2 U). **Xanh** = hỗ trợ, **đỏ** = kháng cự, **vàng** = ≥ 3 nhóm hợp lưu có HVN. Chỉ tính từ history M30 ⇒ **không đổi khi đổi khung M1/M5/M15/M30**. **Chưa kiểm định** — không phải tín hiệu vào lệnh. Spec: [PLAN-VUNG-MANH.md](PLAN-VUNG-MANH.md); logic `StrongZones` trong `ProfileEngine.cs`; ảnh mẫu `research/vung_manh_2026-11-25/ui/`. |
| `SessionZones` · **hộp HVN** (2026-11-25) | HVN = **cụm khối lượng lớn và đều** (thân chữ D, đấu giá xong) của 5 phiên đã đóng + tuần trước + tuần này tới hôm qua: mọi mức giá trong hộp ≥ 80 % đỉnh hộp (khối lượng làm mượt), hộp chứa ≥ 10 % khối lượng ngày (tuần ≥ 8 %), rộng ≥ 0,20 × biên độ M30, tối đa 2 hộp/profile. Vẽ hộp cam nhạt viền rõ, nhãn "HVN ngày"/"HVN tuần", khi giá đã từng rời mép hộp ≥ 2 U và mép gần trong 4 U. Giá quay lại: canh phản ứng đảo chiều **hoặc** phá vỡ — chưa kiểm định. Spec §10–11; test C# = Python 11 profile + 689 ca (`fixture/hvn_cum_cases.json`, `expected_cum.json`). |
| `SessionZones` · **settings** (19 ô) | Hiển thị: Hiện vùng mạnh · Hiện hộp HVN · Hiện LVN · Hiện VAH/VAL hôm nay · Vẽ đường VWAP tuần và ngày · Hiện các lớp phụ đã bật ở trên. Màu: hỗ trợ · kháng cự · vùng rất mạnh · hộp HVN · VWAP tuần · VWAP ngày. Giờ: Lệch giờ so với UTC (Việt Nam = 7). Telegram: Gửi Telegram · Bot token · Chat ID · Tab này được gửi · Gửi thử ngay · Kèm lịch tin Forex Factory. Mọi con số khác là hằng (giờ phiên 05:00/12:30/19:00 VN, mốc Mỹ 19:20, báo chiều 14:00…). Bộ chặn chỗ nối hợp đồng **tự tắt** khi symbol là một hợp đồng (GCZ26, NQZ26…; `ZonePolicy.IsSingleContract`), tự bật với mã liên tục (`/GC:XCEC`). |
| `build-tpo.sh` | Build Linux: concat `ProfileEngine.cs` + từng indicator → `dist/*.dll`. |
| `prototype_test.py` | Prototype Python đã test thuật toán trên `../data-export/` (POC khớp nền tảng 90%@5t). |

## Build
```bash
./build-tpo.sh          # cả 2
./build-tpo.sh daily    # chỉ DailyTpoBias
./build-tpo.sh zones    # chỉ SessionZones
```
Ra `dist/DailyTpoBias.dll` và `dist/SessionZones.dll` (đã build sạch 0 warning).

## Test (chạy trước khi build)
```bash
dotnet run --project tests   # ProfileEngine + vùng mạnh (C# = Python trên fixture, bất biến khung, UI → PNG)
```

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
3. Bấm **"Gửi thử ngay"** (bật rồi tắt) để test — nếu nhận được tin là xong.

**Lịch tin Forex Factory** (ô `Kèm lịch tin Forex Factory`, mặc định BẬT): tin **đầu ngày** liệt kê toàn bộ tin của ngày (giờ VN), tin **trước phiên Mỹ** chỉ nhắc những tin **còn lại** từ giờ đó trở đi; mốc buổi chiều không kèm cho gọn. Lọc: USD mức cao + trung bình, EUR/GBP mức cao; 🔴🔴 = nhóm giật mạnh nhất (CPI, NFP, FOMC). Feed tải nền, cache 1 giờ ra `news_cache.json` (feed trả 429 nếu gọi dày) → mất mạng vẫn dùng bản cache. Bản Python đối chiếu/chạy tay: [news-calendar/ff_news.py](../news-calendar/ff_news.py).

**Lưu ý:** mốc "trước phiên Mỹ" dùng giờ tường (wall-clock) + `Lệch giờ` (giả định `bar.TimeLeft` là UTC). Mùa đông Mỹ (EST) mốc thật là 20:20 VN nhưng từ 2026-11-25 mốc này là **hằng 19:20** (ô "Phiên Mỹ mở" của SessionZones đã gỡ) ⇒ mùa đông tin "trước phiên Mỹ" do SessionZones gửi tới sớm 1 giờ. Mốc "đầu ngày" tính theo số nến sau IB nên KHÔNG lệ thuộc DST.

## Cần kiểm khi chạy live (xem PLAN.md §8)
- `bar.TimeLeft` là UTC hay local → chỉnh input **Lệch giờ** của SessionZones cho khớp (mặc định +7 VN).
- Tách ngày/phiên theo khoảng nghỉ > 75 phút (hằng) đúng chưa.
- Feed có điền `PriceLevels` (volume theo giá) không — nếu không, tự fallback về TPO.
- Ranh giới phiên Á/Âu/Mỹ (hằng 05:00 / 12:30 / 19:00 giờ VN) khớp đỉnh khối lượng thật chưa.

> **Trạng thái: v1 — build sạch trên Linux, CHƯA test trên feed live.** Cần deploy Windows + chụp lại để hiệu chỉnh ngưỡng.
