# Cầu nối Quantower RunnerSignal → MT5 (Exness)

Mỗi khi RunnerSignal bắn tín hiệu trên Quantower, MT5 tự vào lệnh cùng hướng.

```
Quantower / RunnerSignal.cs          %APPDATA%\MetaQuotes\Terminal\Common\Files\
  nến M1 vừa đóng có tín hiệu  ──►     runner_cmd.jsonl   (1 dòng JSON = 1 lệnh)
                                              │
                                       RunnerBridge.mq5 (EA trên chart vàng, OnTimer 250ms)
                                              ├──► OrderSend market + SL/TP theo giá KHỚP
                                              ├──► runner_ack.csv   (fill, slippage, spread, lý do bỏ)
                                              └──► runner_done.txt  (id đã xử lý — chống bắn trùng)
```

## Nguyên tắc thiết kế quan trọng

**Không truyền giá tuyệt đối.** Quantower chạy GC/MGC futures, MT5 chạy XAUUSD spot — lệch
basis vài chục USD, còn trôi theo thời gian và nhảy khi đảo hợp đồng. Nhưng cả hai đều báo giá
**USD/oz** nên **khoảng cách chuyển 1:1**. Tín hiệu vì vậy chỉ mang `side + sl_dist + rr`;
EA vào **market** rồi đặt `SL = fill ∓ sl_dist`, `TP = fill ± rr × sl_dist`. Các trường `src_*`
trong file chỉ để ghi log đối chiếu, **không** dùng để đặt lệnh.

**Không cần lệnh quản lý sau khi vào.** Backtest của runner chỉ dùng SL/TP tĩnh (không trailing,
không break-even) nên SL/TP native của MT5 tái tạo đúng logic thoát. Thậm chí `Simulate()` ưu tiên
SL khi một nến chạm cả hai → backtest **bi quan hơn** thực tế ở điểm này.

## Chống bắn lệnh trùng (rủi ro lớn nhất)

`Process()` trong RunnerSignal quét **lại toàn bộ lịch sử mỗi nến mới**. Nếu nối order một cách
hồn nhiên, mỗi lần reload indicator sẽ bắn hàng chục lệnh cũ. Bốn chốt:

| Chốt | Ở đâu |
|---|---|
| Chỉ xét tín hiệu ở nến **vừa đóng** (`Idx == B.Count-2`) | Quantower |
| Lần quét đầu sau attach/reload chỉ **nạp id, không gửi** (`_armed`) | Quantower |
| Tuổi tín hiệu ≤ `Mt5MaxAgeSec` (mặc định 90s) | Quantower **và** EA (kiểm độc lập) |
| `id` tất định `symbol\|phút\|hướng\|nhánh`, EA lưu `runner_done.txt` | EA (bền qua restart) |

## Ba lớp an toàn độc lập

1. **Quantower**: `MT5: dry-run` = true (mặc định) → mỗi dòng có `"dry":true` → EA chỉ ghi log.
2. **EA**: `InpEnableTrading` = false (mặc định) → chỉ ghi log.
3. **EA**: trần cứng `InpMaxRiskPct` (3%) — **bỏ lệnh** nếu ngay cả lot nhỏ nhất cũng vượt trần;
   cộng thêm chặn spread rộng, số vị thế, lỗ ngày, tín hiệu cũ, thiếu margin.

## Nhồi lệnh (`size_mult`) — thêm 2026-08-02

> ⚠ **Trước ngày này EA KHÔNG đọc `size_mult`.** EntrySignal đã ghi trường đó ra JSONL từ lâu, nhưng EA
> bỏ qua — nên "nhồi ×5" chỉ là **con số thống kê trên panel**, lot thật chưa bao giờ được nhân. Nay đã sửa.

Indicator quyết định hệ số, EA nhân lot cơ sở với nó:

| Bên | Input | Mặc định | Ý nghĩa |
|---|---|---|---|
| EntrySignal | `NhoiConflGate` / `NhoiMult` | 3 / 1.0 (tắt) | nhồi khi **hợp lưu** ≥ N |
| RunnerSignal · WyckoffRunner | `NhoiVsaGate` / `NhoiMult` | 2.2 / 1.0 (tắt) | nhồi khi **VSA nến vào lệnh** ≥ ngưỡng |
| EA | `InpUseSizeMult` | true | đọc `size_mult`; đặt false = bỏ qua, luôn dùng lot cơ sở |
| EA | `InpMaxSizeMult` | 5.0 | trần hệ số — chặn trường hợp indicator báo số vô lý |

Runner gate theo **VSA nến vào** chứ không theo hợp lưu như EntrySignal, vì ở runner hợp lưu chỉ là thông
tin hiển thị và với nhánh QUAY ĐẦU nó còn **ngược dấu** (0 vùng → WR 33%, 3 vùng → WR 0%). Chi tiết:
[`RESULTS_ENTRY_VSA.md`](../quantower-entry-signal/research/wyckoff/RESULTS_ENTRY_VSA.md) §8.

**Trần cứng vẫn thắng, nhưng cách xử lý được tách làm hai:** nếu phần nhồi làm rủi ro vượt
`InpMaxRiskPct` thì EA **hạ lot về vừa trần** (ghi vào Experts log) chứ không bỏ lệnh — vì lệnh gốc vẫn
hợp lệ, chỉ là phần nhồi không đủ chỗ. Chỉ khi lot **nhỏ nhất** vẫn vượt trần thì mới bỏ lệnh như cũ.
Nghĩa là bật nhồi **không thể** đẩy rủi ro mỗi lệnh vượt quá `InpMaxRiskPct` — hãy đặt input đó cho đúng
trước, rồi mới bật nhồi.

## Cài đặt

**1. Chép EA vào MT5**

Trong MT5: `File → Open Data Folder` → `MQL5\Experts\` → chép `RunnerBridge.mq5` vào →
mở MetaEditor (F4) → chọn file → **Compile** (F7). Phải 0 error.

**2. Kiểm đặc tả symbol — bước BẮT BUỘC trước khi bật tiền thật**

Mở chart **vàng của chính tài khoản cent** (Market Watch → tên có thể là `XAUUSD`, `XAUUSDm`,
`XAUUSD.c`… — EA dùng `_Symbol` của chart nên không hardcode). Kéo EA vào chart, để
`InpEnableTrading = false`. Xem tab **Experts**, EA in ra:

```
RunnerBridge XAUUSDm | contract ... | tick ... | tickValue ... | lot min ... | digits ... | stops ...
RunnerBridge equity 1000.00 USC | LOT MIN: SL 3.0 -> mat X (Y%), SL 7.0 -> mat Z (W%)
```

SL của runner nằm trong **3.0–7.0 USD/oz**, nên dòng thứ hai cho biết ngay lot nhỏ nhất có
dùng được với số dư hiện tại hay không:

- Tài khoản **cent** (1 lot = 1 oz, số dư tính bằng cent): lot min 0.01 → mất ~3–7 cent/lệnh.
  Với 1000 cent (~$10) = **0.3–0.7% mỗi lệnh** → đúng khoảng cần, dùng `RISK_MIN_LOT` là chuẩn.
- Tài khoản **standard** (1 lot = 100 oz): lot min 0.01 → mất **$3–7/lệnh** = 30–70% của $10
  → EA sẽ **bỏ toàn bộ lệnh** (đúng như thiết kế). Trường hợp này phải dùng cent hoặc nạp thêm.

Nếu Experts in `CANH BAO: lot NHO NHAT da vuot tran rui ro` → **đừng bật trading**, xử lý số dư
hoặc loại tài khoản trước.

**3. Bật cầu nối phía Quantower**

Trong properties của indicator *Runner Signal (CBR M1)*:

| Input | Giá trị |
|---|---|
| Cầu nối MT5: BẬT gửi tín hiệu | ✔ |
| MT5: dry-run | ✔ (giữ nguyên giai đoạn 1) |
| MT5: thư mục Files | để trống = `%APPDATA%\MetaQuotes\Terminal\Common\Files` |

Bảng trên chart sẽ hiện dòng `🔗 MT5 (DRY): …`. Ngay lần quét đầu nó báo **lệch feed↔đồng hồ Xs** —
phải gần 0. Nếu lệch hàng giờ thì `bar.TimeLeft` không phải UTC như giả định, nói tôi sửa chứ
đừng nâng `Mt5MaxAgeSec` để lách (sẽ mở cửa cho bắn lệnh cũ).

**4. Trong MT5, cho phép thư mục Common**

Không cần bật *Allow DLL imports*. Chỉ cần *Allow Algo Trading* (`Ctrl+O → Expert Advisors`) khi
sang giai đoạn vào lệnh thật.

## Ba giai đoạn chạy

| GĐ | Quantower dry-run | EA EnableTrading | Kiểm gì |
|---|---|---|---|
| 1 | ✔ | ✘ | `runner_cmd.jsonl` có dòng mới đúng lúc tín hiệu nổ trên chart; `runner_ack.csv` ghi `LOG`. Reload indicator vài lần → **không** sinh dòng trùng. |
| 2 | ✘ | ✔ | Lệnh thật lot min. Đối chiếu `runner_ack.csv`: `truot` (slippage) và `spread` thực tế. |
| 3 | ✘ | ✔ + `RISK_PERCENT` | Chạy theo % equity sau khi số liệu GĐ2 sạch. |

## Đối chiếu sau đó

- `RunnerSignal_signals.csv` (bật `Xuất CSV`) = tín hiệu theo giá futures.
- `runner_ack.csv` = fill thật trên spot.

So hai file để đo **spread + slippage ăn bao nhiêu R**.

### Spread ăn bao nhiêu edge — đo trên data thật (GCQ26, 5–7/2026, config shipped)

Mô phỏng đúng cơ chế spot: vào ở ask/bid nên **SL hiệu dụng bị thịt bớt đúng 1 spread** và
**TP hiệu dụng xa thêm 1 spread**.

| spread (USD/oz) | CBR 3R (n=75) | QUAY ĐẦU 1.5R (n=55) | portfolio |
|---:|---|---|---|
| 0.00 (backtest gốc) | WR 37% · **+37.0R** | WR 47% · **+10.0R** | **+47.0R** |
| 0.10 | WR 35% · +29.0R | WR 47% · +10.0R | +39.0R |
| 0.20 | WR 35% · +29.0R | WR 44% · +5.0R | +34.0R |
| 0.30 | WR 33% · +25.0R | WR 42% · +2.5R | +27.5R |
| 0.50 | WR 32% · +21.0R | WR 40% · +0.0R | +21.0R |

Kết luận:

- **CBR bền** với spread (SL 3.0–6.8 USD nên spread chỉ ~6% của R): 0.20 → mất 22% net.
- **QUAY ĐẦU là mắt yếu** (SL median chỉ 2.4 USD, p25 1.7, min 1.1): 0.20 → net **rơi một nửa**;
  từ 0.50 là hết edge. Vì vậy EA có chốt `InpMaxSpreadPctOfR` (mặc định 15%) — bỏ lệnh khi
  spread quá lớn so với SL của chính tín hiệu đó, thay vì chặn theo ngưỡng tuyệt đối.
- Đã thử lọc theo SL tối thiểu (≥1.5 / ≥2.0 USD): **không** cải thiện net (cắt cả lệnh thắng)
  → không lọc, chỉ chặn theo spread tương đối.
- Portfolio ở spread 0.20 còn +34R/3 tháng → cầu nối đáng chạy, nhưng **chọn tài khoản
  spread thấp** là biến quan trọng nhất, hơn mọi tinh chỉnh param.

## Ghi chú vận hành

- Cả hai app phải chạy trên **cùng máy Windows** (dùng thư mục Common). Khác máy → phải đổi
  sang shared folder hoặc TCP.
- Feed Quantower chết → không có tín hiệu (cổng tuổi tín hiệu chặn hàng cũ). MT5 vẫn giữ SL/TP
  cho vị thế đang mở nên lệnh đã vào không bị bỏ rơi.
- `Reject` **đánh dấu đã xử lý** (không thử lại): tín hiệu là lệnh vào market tại nến đóng, vào
  muộn = vào giá tệ hơn, thà bỏ.
- Không có lệnh đóng từ Quantower: mọi lệnh thoát bằng SL/TP tại broker. Muốn can thiệp thì đóng
  tay trong MT5.
