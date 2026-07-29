# LIVE_LOG — đối chiếu tín hiệu live ↔ backtest

> Pha GĐ10, **lặp lại** mỗi 1–2 tuần. Mỗi lần chạy **append một mục mới** ở cuối, không ghi đè.
> Đọc trước: [PARITY_V7.md](PARITY_V7.md) · [AUDIT_V7.md](AUDIT_V7.md) · [BASELINE.md](BASELINE.md) §0.

---

## Trạng thái hiện tại (2026-07-29, sau lượt 1)

| | |
|---|---|
| DLL đã build | ✅ [dist/WyckoffRunner.dll](../../dist/WyckoffRunner.dll) — 83.968 byte, md5 `6e78c447c6edf2db0cc5f63f5f21f301` |
| Parity thuật toán C#↔Python | ✅ **ĐẠT** — 33/33 tín hiệu, 0 lệch |
| Parity **DLL-trong-Quantower** | ✅ **ĐẠT** — 33/33 CBR khớp, 0 lệch giá trị (0.0 tick), 2 tín hiệu "chỉ C#" đã giải thích = ngoài cửa sổ dữ liệu Python |
| Cấu hình đóng băng | ✅ **ĐÚNG** (từ lượt 2) — chỉ còn CBR, nhánh QUAY ĐẦU đã tắt |
| Dữ liệu live đã thu | **35 tín hiệu CBR**, 2026-05-26 → 2026-07-29 — nhưng là **REPLAY lịch sử**, không phải forward |
| Kết luận về chiến lược từ live | **Chưa có gì.** Replay ≠ OOS. Điểm thật sự ngoài mẫu: **n=2** → KHÔNG KẾT LUẬN |

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

---

### 2026-07-29 — lượt 1: PARITY DLL ĐẠT, nhưng dữ liệu là REPLAY (không phải forward test)

File: `data-export/28-7/WyckoffRunner_signals.csv` — 63 tín hiệu, 2026-05-22 07:10 → 2026-07-29 14:00.

#### 1. Parity live: ✅ **ĐẠT**

```
Python :  33 tin hieu | 2026-05-26 09:44 -> 2026-07-23 12:20
C#     :  35 tin hieu | 2026-05-26 09:44 -> 2026-07-29 14:00
TONG KET: khop 33 | chi Python 0 | chi C# 2 | lech gia tri 0 | tong lech 2/35 = 5.7%
```

**33/33 tín hiệu CBR khớp, mọi entry và SL lệch 0.0 tick.** Đây là kết quả quan trọng nhất của lượt này:
DLL chạy trong Quantower, ăn feed của Quantower (VolumeAnalysis, bộ lọc nến của Quantower), vẫn ra **đúng
từng tín hiệu** như engine Python ăn CSV dxFeed. 9 điểm nghi lệch ở [PARITY_V7.md](PARITY_V7.md) §2
(timezone, warmup, VWAP reset, liqbase, VSA, làm tròn tick, nến-đã-đóng, dedup, nguồn nến) **không cái nào
phát tác trên cửa sổ này**.

**Giải thích 2 tín hiệu "chỉ có ở C#"** (bắt buộc theo tiêu chí GĐ9, không được gộp thành "lệch nhẹ"):

| Tín hiệu | Nguyên nhân | Có phải lệch thật? |
|---|---|---|
| 2026-07-28 13:47 SHORT | CSV dxFeed của Python **hết dữ liệu ở 2026-07-27 15:56** | ❌ Không — Python không có nến để mà quét |
| 2026-07-29 14:00 SHORT | cùng lý do | ❌ Không |

Trong đúng khoảng hai bên **đều có dữ liệu** (≤ 2026-07-27 15:56): CBR live = 33, Python = 33, **khớp 33,
lệch 0**. Vậy lệch thực tế = **0/33 = 0.0%** → **ĐẠT** theo ngưỡng GĐ9, không phải "đạt có điều kiện".
(Script in ra "ĐẠT CÓ ĐIỀU KIỆN" vì nó chỉ so mốc đầu–cuối của CSV live, không biết Python hết dữ liệu sớm hơn.)

#### 2. ⚠ Dữ liệu này KHÔNG phải forward test — nó là REPLAY lịch sử

Bằng chứng: tín hiệu đầu tiên là **2026-05-22**, tức indicator đã tính lại toàn bộ lịch sử có trên chart, chứ
không phải chạy tiến từ ngày deploy. `ExportSignals()` ghi đè toàn bộ danh sách mỗi nến mới, nên file này là
**backtest do Quantower chạy**, không phải log lệnh phát sinh theo thời gian thực.

⇒ **Không được cộng 63 lệnh này vào bằng chứng OOS.** 60/63 tín hiệu nằm trong đúng cửa sổ 5–7/2026 đã dùng
để chọn cấu hình. Đó vẫn là in-sample, chỉ là chạy qua đường ống khác.

**Phần thật sự ngoài mẫu** = tín hiệu sau khi dữ liệu research kết thúc (2026-07-27 15:56):

```
CBR ngoai-mau      n= 2 WR=  0.0% tong= -2.0R   (07-28 13:47 LOSS, 07-29 14:00 LOSS)
TAT CA ngoai-mau   n= 3 WR= 33.3% tong= -0.7R
```

**n=3 → KHÔNG KẾT LUẬN.** Hai lệnh CBR thua liên tiếp là hoàn toàn bình thường với WR ~46%/RR 4:1 (xác suất
2 thua liên tiếp ≈ 29%); **không** phải dấu hiệu chiến lược hỏng, và cũng **không** phải xác nhận nó chạy được.

#### 3. Số liệu replay (in-sample, chỉ để đối chiếu — KHÔNG phải kết quả live)

```
TAT CA        n= 63 WR= 50.8% tong=+57.0R EV=+0.905 | 05: +7.0( 8) 06:+24.5(28) 07:+25.5(27) ✓ thang am=0
CBR (KB1)     n= 35 WR= 45.7% tong=+45.0R EV=+1.286 | 05: +5.0( 5) 06:+22.0(18) 07:+18.0(12) ✓ thang am=0
QUAY_DAU(KB2) n= 28 WR= 57.1% tong=+12.0R EV=+0.429 | 05: +2.0( 3) 06: +2.5(10) 07: +7.5(15) ✓ thang am=0
```

Mốc backtest Python để so: CBR `n=33 WR=48.5% +47.0R EV=+1.424`. Live replay `n=35 WR=45.7% +45.0R EV=+1.286`
— chênh **đúng bằng 2 lệnh thua ngoài mẫu** đã nói ở trên, không có sai lệch nào khác.

#### 4. 🔴 Phát hiện cấu hình: nhánh QUAY_ĐẦU (KB2) ĐANG BẬT — trái cấu hình đóng băng

28/63 tín hiệu là `QUAY_DAU`. Nhưng [AUDIT_V7.md](AUDIT_V7.md) phán quyết **KB2 = FAIL** (p=0.072, OOS n=9
EV −0.167R) và §1 bảng input của file này ghi rõ **index 66 "Bật nhánh QUAY ĐẦU" = TẮT**. Mặc định trong DLL
đã là `false`.

⇒ Người dùng đã **bật tay** input 66, hoặc dùng chart có preset cũ lưu sẵn giá trị `true`. Quantower lưu giá
trị input theo template chart, nên **DLL mới không tự ghi đè preset cũ**.

**Việc cần làm:** tắt index 66 về **TẮT**. KB2 chưa qua cổng audit — chạy nó thật là giao dịch bằng nhánh đã
bị FAIL. (Replay cho KB2 EV +0.429R nhìn có vẻ ổn, nhưng đó chính là in-sample của cái đã bị bác; số đẹp trên
cửa sổ đã dùng để chọn tham số không phải bằng chứng.)

#### 5. Chưa đo được

- **Spread/slippage thực tế** — replay không có; phải có lệnh forward thật mới thấy (§3 ngưỡng báo động 40 tick).
- **Parity trên nến đang chạy** — mọi so sánh ở trên là nến đã đóng.
- **Độ trễ Quantower→MT5** — cầu nối chưa chạy thật.

#### 6. Việc cần làm tiếp

1. **Tắt input 66** (QUAY ĐẦU) → chỉ chạy CBR.
2. Chạy **forward** ≥2 tuần **không xoá file CSV**, rồi gửi lại. Kỳ vọng ~5–6 lệnh CBR/2 tuần.
3. Lượt sau chỉ tính điểm ngoài mẫu (sau 2026-07-27), tích luỹ tới n≥25 mới được kết luận.

---

### 2026-07-29 — lượt 2: đã tắt QUAY ĐẦU, cấu hình giờ ĐÚNG. Parity vẫn ĐẠT. Vẫn là replay.

Cùng đường dẫn file, người dùng xuất lại sau khi tắt input 66. File 11.291 → 5.911 byte, 63 → **35 tín hiệu,
100% CBR**.

#### 1. ✅ Việc cần làm ở lượt 1 đã xong

`nhanh` chỉ còn `CBR` (35/35), không còn dòng `QUAY_DAU` nào. Cấu hình đóng băng của
[AUDIT_V7.md](AUDIT_V7.md) §14 giờ được tôn trọng: **chỉ KB1 chạy**.

#### 2. ✅ Parity live: vẫn **ĐẠT**, kết quả không đổi

```
TONG KET: khop 33 | chi Python 0 | chi C# 2 | lech gia tri 0 | tong lech 2/35 = 5.7%
```

Hai tín hiệu "chỉ C#" vẫn là 07-28 và 07-29, vẫn cùng nguyên nhân đã ghi ở lượt 1 (dxFeed CSV của Python hết
ở 2026-07-27 15:56). Trong khoảng hai bên đều có dữ liệu: **33/33 khớp, lệch 0.0 tick → 0.0%**.

**Kiểm tra chéo quan trọng:** so từng ô của 35 dòng CBR ở lượt 2 với 35 dòng CBR ở lượt 1 → **0 ô lệch**.
Nghĩa là tắt input 66 **không** làm xê dịch nhánh CBR: không có tín hiệu CBR nào trước đây bị router 1-vị-thế
gạt vì trùng giờ với một lệnh QUAY_DAU. Đây là điều cần kiểm chứ không được giả định — nếu có lệch, con số
in-sample của KB1 sẽ khác.

#### 3. Số liệu (in-sample replay — KHÔNG phải kết quả live)

```
CBR (KB1)  n= 35 WR= 45.7% tong=+45.0R EV=+1.286 | 05: +5.0( 5) 06:+22.0(18) 07:+18.0(12) ✓ thang am=0
  LONG     n= 14 WR= 42.9% tong=+16.0R EV=+1.143 | 05: -1.0( 1) 06: +7.0( 8) 07:+10.0( 5)   thang am=1
  SHORT    n= 21 WR= 47.6% tong=+29.0R EV=+1.381 | 05: +6.0( 4) 06:+15.0(10) 07: +8.0( 7) ✓ thang am=0
```

So mốc Python `n=33 WR=48.5% +47.0R EV=+1.424`: chênh **đúng bằng 2 lệnh thua ngoài mẫu**, không sai lệch khác.

#### 4. Điều KHÔNG đổi so với lượt 1 — vẫn chưa có forward test

Tín hiệu đầu vẫn là **2026-05-26**, tức vẫn là replay toàn bộ lịch sử trên chart, không phải log tiến theo
thời gian thực. Phần ngoài mẫu vẫn chỉ là 2 lệnh (07-28, 07-29), **cả hai LOSS, −2.0R, n=2 → KHÔNG KẾT LUẬN**.

Tắt input 66 sửa được **cấu hình**, không tạo thêm **dữ liệu**. Muốn có bằng chứng OOS thì chỉ có một cách:
để nó chạy tiếp về phía trước.

#### 5. Việc cần làm tiếp

1. Cứ để chart chạy, **≥2 tuần**, không đổi input nào nữa.
2. Trước khi xuất lần sau: **đổi tên file CSV cũ** (vd `..._2026-07-29.csv`) rồi mới lấy file mới, để giữ
   lịch sử — `ExportSignals()` ghi đè cùng đường dẫn.
3. Lượt 3 chỉ tính tín hiệu sau 2026-07-27 15:56. Tích luỹ tới **n≥25** mới được nói bất cứ điều gì về
   việc chiến lược có chạy ngoài thực tế hay không.
