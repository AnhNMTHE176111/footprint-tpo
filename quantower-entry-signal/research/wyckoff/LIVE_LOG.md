# LIVE_LOG — đối chiếu tín hiệu live ↔ backtest

> Pha GĐ10, **lặp lại** mỗi 1–2 tuần. Mỗi lần chạy **append một mục mới** ở cuối, không ghi đè.
> Đọc trước: [PARITY_V7.md](PARITY_V7.md) · [AUDIT_V7.md](AUDIT_V7.md) · [BASELINE.md](BASELINE.md) §0.

---

## Trạng thái hiện tại (2026-07-29)

| | |
|---|---|
| DLL đã build | ✅ [dist/WyckoffRunner.dll](../../dist/WyckoffRunner.dll) — 83.968 byte, md5 `6e78c447c6edf2db0cc5f63f5f21f301` |
| Parity thuật toán C#↔Python | ✅ **ĐẠT** — 33/33 tín hiệu, 0 lệch |
| Parity DLL-trong-Quantower | ⏳ **CHƯA ĐẠT** — chưa có CSV live |
| Dữ liệu live đã thu | **0 tín hiệu, 0 ngày** — chưa deploy |
| Kết luận về chiến lược từ live | **Chưa có gì.** Không được kết luận |

> ⚠ **Câu quan trọng nhất của cả file này:** cho tới khi có CSV live và `parity_v7.py --live` báo ĐẠT,
> **mọi lệch giữa live và backtest đều CÓ THỂ do port sai**, không phải do chiến lược. Đừng vội kết luận
> "chiến lược không chạy được ngoài thực tế" khi nguyên nhân có thể chỉ là feed khác nến.

---

## 1. Checklist deploy (làm trên máy Windows)

### Bước 1 — Copy DLL
Copy [dist/WyckoffRunner.dll](../../dist/WyckoffRunner.dll) vào thư mục indicator của Quantower:
```
%USERPROFILE%\Documents\Quantower\Settings\Scripts\Indicators\
```
(hoặc thư mục `Indicators` mà bản Quantower của bạn đang dùng). Khởi động lại Quantower, thêm indicator
**WyckoffRunner** vào chart **M1** của hợp đồng vàng.

### Bước 2 — Kiểm cấu hình đóng băng

**Tin tốt: mặc định trong DLL ĐÃ ĐÚNG cấu hình đóng băng** (đã đối chiếu 27/27 tham số, xem
[PARITY_V7.md](PARITY_V7.md) §4). Nên việc cần làm chủ yếu là **không đổi gì**, và đổi đúng **một** input:

| Cần làm | Input | Giá trị |
|---|---|---|
| 🔴 **PHẢI BẬT** | index 120 · "Xuất CSV toàn bộ tín hiệu" | **BẬT** (mặc định TẮT — không bật thì không có gì để đối chiếu) |
| ⚪ tuỳ chọn | index 121 · "Đường dẫn CSV" | để trống = ghi vào thư mục Documents |

**Bảng đối chiếu tay — 22 input LOGIC quan trọng nhất** (nếu một dòng nào lệch → sửa về đúng giá trị này,
đừng "thử điều chỉnh"):

| Index | Input | PHẢI là |
|---:|---|---|
| 50 | Range: số nến trước break | **8** |
| 51 | Range: span TỐI THIỂU (giá) | **3.0** |
| 52 | Range: span TỐI ĐA (giá) | **7.5** |
| 53 | Break: VSA tối thiểu (× TB) | **2.0** |
| 54 | Break: thân mạnh ≥ | **0.50** |
| 55 | Chờ hồi+tiếp diễn trong (số nến) | **12** |
| 56 | Retrace TỐI THIỂU | **0.60** |
| 57 | Retrace TỐI ĐA | **1.00** |
| 58 | Hồi cho phép thủng cạnh (tick) | **2** |
| 59 | Nến tiếp diễn: thân ≥ | **0.35** |
| 60 | SL sàn (giá) | **3.0** |
| 61 | SL trần (giá) | **7.0** |
| 62 | SL đệm (tick) | **2** |
| 63 | **RR mục tiêu** | **4.0** |
| 64 | Cooldown mỗi phía (nến) | **15** |
| 65 | Gộp tín hiệu trùng (nến) | **6** |
| 33 | BREAK SẠCH | **BẬT** |
| 44 | Lọc THUẬN xu hướng | **BẬT** |
| 47 | CBR: vào ĐÚNG phía VWAP | **BẬT** |
| 48 | Lọc thanh khoản | **BẬT** |
| 77 | Lọc phiên chết | **BẬT** |
| 72 | Phiên chết tính theo **UTC** | **BẬT** ← quan trọng, đây là lỗi v5 |
| 66 | **Bật nhánh QUAY ĐẦU** | **TẮT** ← KB2 chưa được cấp vốn |

### Bước 3 — An toàn trước khi chạy thật

| Việc | Input | Giá trị |
|---|---|---|
| Telegram: **để trống token/chat_id** rồi tự điền tay trên máy mình | 141, 142 | repo PUBLIC → **không** commit token |
| Cầu nối MT5: nếu chưa muốn vào lệnh thật thì **bật dry-run** | 131 · "MT5: dry-run (EA chỉ ghi log)" | **BẬT** |
| Hoặc tắt hẳn cầu nối MT5 | 130 · "Cầu nối MT5: BẬT gửi tín hiệu" | **TẮT** |

### Bước 4 — Kiểm múi giờ
Mọi logic tính theo **UTC**. `TzOffset=7` **chỉ** dùng cho hiển thị và dựng vùng phiên, **không** ảnh hưởng
lọc phiên chết (vì `DeadUseUtc=BẬT`). Nếu Quantower hiển thị giờ VN thì tín hiệu lúc 09:44 UTC sẽ hiện là
16:44 — **đây là bình thường**, đừng sửa `TzOffset` để "cho khớp".

### Bước 5 — Chạy và thu dữ liệu
Chạy **ít nhất 1–2 tuần**. Kỳ vọng số lượng: backtest cho ~11 lệnh/tháng ⇒ **2 tuần ≈ 5–6 lệnh**.

---

## 2. Sau khi có CSV live — cách đối chiếu

```bash
cd quantower-entry-signal/research/wyckoff
python3 parity_v7.py "<đường-dẫn-CSV-live>" --live
```

Script tự thu hẹp cửa sổ Python về đúng khoảng thời gian của CSV live rồi so từng tín hiệu.
Ngưỡng phán quyết (theo GĐ9): 0 lệch = ĐẠT · ≤2 lệch và ≤10% = đạt có điều kiện, **phải giải thích từng
cái** · >10% = KHÔNG ĐẠT, không được coi là parity.

⚠ Nếu CSV live có tín hiệu mà Python không có (hoặc ngược lại), **soi từng ca**: ghi thời gian + nguyên nhân
nghi ngờ (nến thiếu? volume khác? warmup chưa đủ? tín hiệu ở nến cuối chuỗi?). Đừng gộp thành "lệch nhẹ".

---

## 3. Ngưỡng cảnh báo — spread & slippage

[AUDIT_V7.md](AUDIT_V7.md) §H đã đo độ nhạy chi phí. Khi có số spread thực tế, so với bảng này:

| Nhánh | Sống tới | Thực tế vàng M1 | Kết luận |
|---|---:|---|---|
| **KB1** (đang cấp vốn) | **>40 tick/lệnh** | 2–3 tick | ✅ biên rất rộng |
| KB2 (đang tắt) | 9 tick | 2–3 tick | ⚠ biên mỏng: EV chỉ +0.294R ở 2 tick |
| KB3 (đã KILL) | **2 tick** | 2–3 tick | ❌ chết ở đúng mức thực tế |

🔴 **Báo động ngay nếu:** spread+slippage thực tế trên vàng ở khung giờ vào lệnh **vượt 40 tick** — lúc đó
edge của KB1 bị ăn hết và phải dừng lại xem xét, không phải "chạy tiếp cho đủ mẫu".

---

## 4. Kỳ vọng dùng để tính vốn — KHÔNG dùng số in-sample

| | |
|---|---|
| EV in-sample KB1 | +1.424R/lệnh |
| **Dùng để tính kích thước vị thế** | **+0.7R** (đầu dưới) |
| Vì sao chiết khấu | kẻ sống sót của ≥94 cấu hình trên **một** cửa sổ 3 tháng; **không có điểm OOS nào** |

WR kỳ vọng ~48,5% với RR 4:1 ⇒ **chuỗi thua 5–6 lệnh liên tiếp là bình thường, không phải dấu hiệu hỏng.**
Backtest có MDD 3.0R trên 33 lệnh; live `n` nhỏ sẽ dao động mạnh hơn thế.

---

## 5. Mẫu mục cho mỗi lượt đối chiếu (copy xuống dưới mỗi lần chạy)

```
## <ngày> — đối chiếu tuần thứ N
- Khoảng dữ liệu live: ...
- Parity live: ĐẠT / CHƯA ĐẠT (khớp x | chỉ live y | chỉ Python z)
- Bảng số live vs backtest: ...
- n = ... → kết luận được / KHÔNG KẾT LUẬN  (n < 25 thì luôn là "không kết luận")
- Ca lệch (live có / backtest không, và ngược lại): từng ca + nguyên nhân nghi ngờ
- Spread/slippage quan sát được: ... (so với ngưỡng 40 tick ở §3)
- Quan sát định tính về feature SPEC §8 (per-level footprint, DOM): ...
- Việc cần làm tiếp: ...
```

---

## 6. Lịch sử đối chiếu

### 2026-07-29 — lượt 0 (chuẩn bị, chưa có dữ liệu live)

- **Khoảng dữ liệu live:** không có — chưa deploy lên máy Windows.
- **Parity live:** CHƯA ĐẠT — chưa có CSV. (Parity *thuật toán* đã ĐẠT 33/33, xem
  [PARITY_V7.md](PARITY_V7.md).)
- **Bảng số live vs backtest:** chưa có số live. Mốc backtest để so sau này:

  ```
  KB1 (in-sample 5-7/2026, dxFeed GCQ26, cấu hình đóng băng)
    n= 33 WR=48.5% tong=+47.0R EV=+1.424 MDD= 3.0R | 05:+5.0 06:+22.0 07:+20.0 ✓
    LONG  n=14 EV=+1.143   |   SHORT n=19 EV=+1.632
    EV sau 2 tick phí: +1.369   |   OOS: KHÔNG CÓ
  ```

- **n = 0** → **KHÔNG KẾT LUẬN**.
- **Ca lệch:** không có (chưa có dữ liệu).
- **Spread/slippage:** chưa đo được — không có trong bất kỳ file export nào (SPEC §8), chỉ live mới thấy.
- **Việc cần làm tiếp:** người dùng deploy theo §1, chạy 1–2 tuần, lấy CSV về, chạy `parity_v7.py --live`.
