# WyckoffRunner v6 — PLAN thực thi

> Viết 2026-07-29. Mục đích: **người sau (hoặc Claude ở effort thấp) implement được mà KHÔNG phải suy luận lại.**
> Mọi con số trong file này tái lập được bằng `research/wyckoff/final_table.py`.
> Nguồn luật: [`../data-export/messages-with-pro-trader/RULES.md`](../data-export/messages-with-pro-trader/RULES.md)
> · Transcript gốc: [`../data-export/messages-with-pro-trader/TRANSCRIPT.md`](../data-export/messages-with-pro-trader/TRANSCRIPT.md)

---

## 0. Bối cảnh 30 giây

`WyckoffRunner.cs` = clone của `RunnerSignal.cs` (v5 đang chạy live), để nâng cấp theo lời pro trader CORVEN mà không đụng bản đang chạy. Chỉ nhánh **CBR** (phá→hồi→tiếp diễn) được đo trong plan này; nhánh **QUAY_DAU** giữ nguyên (xem Bước 5–7).

**Bàn cân đo (dxFeed GCQ26, 5–7/2026, nhánh CBR):**

| Cấu hình | n | WR | tổng R | EV/lệnh | MDD | 3 tháng |
|---|---:|---:|---:|---:|---:|:--:|
| v5 **như đang ship** (cắt sai khung giờ) | 77 | 37.7% | +39.0R | +0.506 | 11.0R | ✓ |
| + **B1** sửa khung giờ chết | 55 | 47.3% | +49.0R | +0.891 | 6.0R | ✓ |
| + **B2** BREAK SẠCH | 29 | **58.6%** | +39.0R | +1.345 | 2.0R | ✓ |
| + **B3** retrace 60–100% | 33 | 57.6% | +43.0R | +1.303 | 2.0R | ✓ |
| + **B4** RR 4.0 (thay 3.0) | 33 | 48.5% | +47.0R | **+1.424** | 3.0R | ✓ |

**Đọc bảng cho đúng:** tiền *không* tăng nhiều (+39R → +47R). Cái tăng là **chất lượng**: EV/lệnh ×2.8, **MDD 11R → 3R**, số lệnh giảm hơn nửa. Winrate tăng **+19.9 điểm** (37.7%→57.6%) nếu giữ RR3; nếu đẩy RR lên 4 thì WR chỉ +10.8 điểm nhưng EV cao nhất. **Chọn RR là quyết định của bạn — xem Bước 3.**

---

## 1. ĐÃ LÀM (đã build sạch, 0 warning)

| # | Thay đổi | File | Trạng thái |
|---|---|---|---|
| 1 | Clone `RunnerSignal.cs` → `WyckoffRunner.cs` (đổi namespace/class/đường log/CSV) + `build-wyckoff.sh` | `WyckoffRunner.cs` | ✅ build OK → `dist/WyckoffRunner.dll` |
| 2 | **BREAK SẠCH**: input `CleanBreak/CleanLook/CleanWin/CleanClosePos` + hàm `NoCounterSweep()` + chèn vào `Scan()` | `WyckoffRunner.cs` | ✅ |
| 3 | `PullMax` 0.90 → **1.00** | `WyckoffRunner.cs` | ✅ |
| 4 | `RR` 3.0 → **4.0** | `WyckoffRunner.cs` | ✅ (xem lại ở Bước 3) |
| 5 | Trích xuất 36 ảnh chat → `TRANSCRIPT.md` + `RULES.md` | `data-export/messages-with-pro-trader/` | ✅ |
| 6 | Engine backtest v6 + sửa **3 lỗi parity** của chính nó | `research/wyckoff/cbr_v6.py` | ✅ |

**3 lỗi parity đã sửa trong `cbr_v6.py`** (ghi lại vì rất dễ tái phạm):
1. `entry_dxfeed.load_m1` tính `b['trend']` với **tol = 0**, C# dùng `TrendTolPts = 1.0` giá → `prepare()` tính lại.
2. Dùng `avg_vma` trung bình **toàn chuỗi** = **look-ahead**. C# dùng TB volume **cuộn 1000 nến trước**, không gồm nến hiện tại → `prepare()` tính `b['liqratio']` cuộn.
3. Gate trend/VWAP/thanh khoản áp ở **nến phá**, C# áp ở **nến VÀO** (`RunnerSignal.cs:570`) → đã dời.

> Sửa 3 lỗi này làm baseline đổi từ n=58/WR43.1% thành **n=55/WR47.3%**. Kết luận không đổi dấu, nhưng **đừng dùng lại số cũ trong lịch sử chat.**

---

## 2. BƯỚC 1 — SỬA LỖI KHUNG GIỜ CHẾT ⚠️ **ƯU TIÊN CAO NHẤT**

### Lỗi
Bộ lọc phiên chết đang **vô hiệu hoàn toàn** cho CBR, và khối lỗ mà research nhắm tới **vẫn còn nguyên**.

**Bằng chứng cột giờ là UTC, không phải giờ VN** (tự kiểm, không tin docstring):
- Giờ **21 có đúng 0 nến** trong dxFeed 5–7/2026 (mọi giờ khác 2.879–3.628 nến) = phiên nghỉ CME 17:00 ET = 21:00 UTC.
- Volume trung vị đỉnh ở giờ **13–14** (102/107 vs nền ~30) = mở COMEX/NY 08:20–09:30 ET = 12:20–13:30 UTC.
- Tên file export ghi `...7_27_2026 105600 PM` (22:56) nhưng dòng cuối là `2026-07-27 15:56:00` — lệch **đúng 7h**.
- Trong `RunnerSignal_signals.csv`: CBR có **đúng 0 lệnh** ở giờ 19,20,21,22,23,00 và có lệnh ở mọi giờ khác → khớp chính xác khung C# đang cắt = **UTC [19:00, 01:00)**. Nhánh REV (được miễn) VẪN có lệnh ở 19,20,22,23.

**Hệ quả:** `InDeadWindow` làm `tUtc.AddHours(TzOffset=7)` rồi cắt `[2,8)` → thực tế cắt **UTC 19–01**. Nhưng khối lỗ nằm ở **UTC 02–08**: trên CSV live, 31 lệnh CBR ở UTC 02–07 có **WR 9.7%, −19R** và không bị filter đụng tới.

**Đo bằng Python (engine đã sửa parity):**

| Khung cắt | n | WR | tổng R | EV | MDD |
|---|---:|---:|---:|---:|---:|
| không cắt | 77 | 37.7% | +39.0R | +0.506 | 11.0 |
| **UTC 19–01** (C# đang làm) | 77 | 37.7% | +39.0R | +0.506 | 11.0 | ← **no-op tuyệt đối** |
| **UTC 02–08** (đúng) | 55 | **47.3%** | **+49.0R** | **+0.891** | **6.0** |

Nó là no-op vì lọc **thanh khoản** đã làm rỗng khung UTC 19–01 từ trước (volume trung vị ở đó chỉ 16–33).

### Cách sửa (chọn 1 trong 2 — khuyến nghị A)

**A. Neo khung theo UTC (bền với DST & TzOffset).** Thêm input + sửa `InDeadWindow`:

```csharp
[InputParameter("Phiên chết: tính theo giờ UTC (thay vì giờ hiển thị)", 37)]
public bool DeadUseUtc { get; set; } = true;   // v6: khung là khung THỊ TRƯỜNG (lull Á/pre-London),
                                               // phải neo giờ sàn, không neo giờ hiển thị của user.

// InDeadWindow — sửa 1 dòng:
int h = DeadUseUtc ? tUtc.Hour : tUtc.AddHours(TzOffset).Hour;
```
Giữ `DeadStartHour = 2`, `DeadEndHour = 8` (nay là **giờ UTC**). Cập nhật lại comment ở `WyckoffRunner.cs` (khối "Lọc PHIÊN CHẾT") vì con số 02–08 trong đó đang được hiểu là giờ hiển thị.

**B. Chỉ đổi số mặc định:** `DeadStartHour = 9`, `DeadEndHour = 15` (vì UTC 02–08 = VN 09–15 khi TzOffset=7). Nhanh hơn nhưng **sai ngay khi user đổi TzOffset hoặc vào DST** → không khuyến nghị.

### PASS / KILL
- **PASS** nếu sau khi sửa, `python3 research/wyckoff/final_table.py` mục 1 cho dòng "B1" ra **n=55, WR 47.3%, +49.0R** (đã có sẵn — đây là kiểm hồi quy).
- Trên **live**: bật `Xuất CSV`, chạy lại lịch sử, xác nhận CSV **không còn lệnh CBR nào** ở giờ UTC 02–07 (tức giờ hiển thị 09–14 nếu TzOffset=7).
- **KILL** nếu trên máy Windows của bạn, `Bar.Time` hoá ra **không** phải UTC → khi đó toàn bộ suy luận này đổi. **Kiểm trước bằng 1 dòng:** thêm tạm vào log `B[i].Time.ToString("u")` cho nến quanh 21:00 UTC và xem có phải giờ nghỉ CME (không có nến) hay không.

### Việc kèm theo (đừng bỏ)
Comment ở `WyckoffRunner.cs` (khối phiên chết) biện luận *"reversal trong khung chết 4/4 THẮNG +6R → MIỄN"*. Con số đó tính trên khung **UTC 02–08**. Sau khi sửa, luận cứ này **mới thành đúng** (trong khung UTC 02–08 reversal là 4W/0L +6R; còn trong khung C# đang cắt thì reversal là 4W/4L +2R, tệ hơn phần ngoài khung). → Giữ miễn trừ, nhưng **sửa comment** cho khỏi lừa người sau.

---

## 3. BƯỚC 2 — CHỐT RR

Trên nền v6 (sạch + retrace 60–100%), cùng 33 lệnh:

| RR | WR | tổng R | EV | MDD | Ghi chú |
|---:|---:|---:|---:|---:|---|
| 2.0 | 60.6% | +27.0R | +0.818 | 2.0 | WR cao nhất, tiền ít nhất |
| **3.0** | **57.6%** | +43.0R | +1.303 | **2.0** | WR ~ mức CORVEN nói (65–70%), MDD nhỏ nhất |
| **4.0** | 48.5% | +47.0R | +1.424 | 3.0 | **đang set trong C#** |
| 5.0 | 45.5% | +57.0R | +1.727 | 4.0 | |
| 6.0 | 45.5% | +72.0R | +2.182 | 4.0 | EV cao nhất |

Đơn điệu tăng theo RR — **đúng lời CORVEN**: *"Sl càng ngắn thì tỉ lệ lệnh tp 5-6R càng nhiều"*, *"bóp sl thì mới có cơ sở gồng dài"*.

**Khuyến nghị:** giữ **RR 4.0** làm mặc định (cân bằng WR/EV/MDD), phơi input để A/B live. **Không** đặt RR 6 làm mặc định vì:
- SL trung vị 3.7 giá → RR6 = mục tiêu **22 giá**; backtest **không mô hình hoá spread/slippage/phí**, mà lệnh chạy 22 giá thì phải sống qua nhiều nhịp hồi.
- Toàn bộ tiền của RR cao đến từ ít lệnh; `nửa1/nửa2` ở RR6 là +19/+53 → lệch nặng về nửa sau (tháng 7 chạy trend mạnh).

**KILL:** nếu live 1 tháng cho tỉ lệ chạm ≥4R thấp hơn ~35% số lệnh thắng → hạ về RR3.

---

## 4. BƯỚC 3 — QUYẾT ĐỊNH LỌC THANH KHOẢN (A/B)

Trên nền v6 RR4:

| Cấu hình | n | WR | tổng R | EV | MDD |
|---|---:|---:|---:|---:|---:|
| v6 RR4 (giữ lọc thanh khoản) | 33 | **48.5%** | +47.0R | **+1.424** | 3.0 |
| **TẮT** lọc thanh khoản | 45 | 46.7% | **+60.0R** | +1.333 | 4.0 |
| TẮT lọc giờ chết | 43 | 37.2% | +37.0R | +0.860 | 5.0 |
| TẮT lọc trend | 39 | 43.6% | +46.0R | +1.179 | 4.0 |
| TẮT VWAP-align | 33 | 48.5% | +47.0R | +1.424 | 3.0 | ← **no-op hoàn toàn** |

**Việc cần làm:**
1. **VWAP-align là no-op** trên cửa sổ này (0 lệnh khác biệt) — hợp lý vì "phá lên + thuận trend" gần như luôn ở trên VWAP phiên. Không xoá (live có thể khác), nhưng **ghi comment** là hiện chưa chứng minh được đóng góp, đừng tính nó là một "lớp lọc".
2. **Lọc thanh khoản:** giữ = WR/EV/MDD tốt hơn; tắt = +13R và +12 lệnh. Sau khi B1 cắt đúng khung UTC 02–08, phần việc của lọc thanh khoản đã bị trùng một phần. → **Đề xuất: giữ mặc định BẬT, phơi input, A/B live 1 tháng.** KILL lựa chọn "tắt" nếu MDD live > 6R.
3. **Lọc trend và lọc giờ chết đều còn đóng góp thật** → giữ nguyên.

---

## 5. BƯỚC 4 — CÁC ĐÒN BẨY PHỤ (tuỳ chọn, đừng đặt mặc định)

| Ý tưởng | Luật | Kết quả (nền v6 RR4) | Kết luận |
|---|---|---|---|
| **R9** chất lượng nến trong leg ≥50% | "cây giảm vol có ngon k / đóng có đẹp k / râu dưới vẫn rút kìa" | n=30, WR 46.7%, +40R, EV 1.333 | Trên nền v6 **không thêm gì** (đã có sẵn trong `cbr_v6.py`, `LEGQ`). Nhưng **riêng lẻ trên baseline thì có**: n=47, WR **51.1%**, +49R, EV 1.043 (vs 47.3%/0.891). → Cân nhắc nếu quyết định **không** dùng BREAK SẠCH. |
| **span range ≤ 6.0 giá** | "Biên của chú to thế =))" (TR 15 giá là quá rộng) | n=15, WR 60.0%, +30R, EV **2.000** | Hướng đúng nhưng **n=15 — quá nhỏ để ship**. Phơi input `RangeMaxPts`, để user tự siết. |
| **R6** chỉ phiên Mỹ | "RR theo entrytime" | n=9, WR 77.8%, EV 2.111 | n=9. **Không dùng.** |

---

## 6. BƯỚC 5 — DỌN CODE CHẾT & COMMENT SAI Ở NHÁNH QUAY_DAU

Đây là **nợ kỹ thuật đã được chứng minh bằng sweep**, không phải phỏng đoán. Sửa để người sau không bị lừa:

| Vấn đề | Bằng chứng | Việc cần làm |
|---|---|---|
| `RevApproachBars` ("đến từ đúng phía") **không lọc gì** | sweep 1→999 đều ra **đúng 27 lệnh**. Vì `rejShort` đã ép `C < VWAP`, mà VWAP là TB tích luỹ chậm → điều kiện "tiếp cận" tự thoả (tautology) | Xoá input, hoặc thiết kế lại điều kiện bối cảnh (không phải chỉnh số nến) |
| `Cooldown` và `SlCapPts` **không tác dụng** cho nhánh reversal | sweep Cooldown 5→30 và SlCap 60→999 đều ra kết quả y hệt | Ghi comment `// không ràng buộc cho reversal` |
| Comment nói `AbsDom`/`RevClimaxOverride` **"nâng grade A"** — **SAI** | `wall` chỉ được dùng để `why.Add("hấp thụ ✓")`; grade gán bằng `s.Grade = s.Cluster >= MinConfluence ? 'A' : 'B'`, không đọc `wall`. CSV live: 21/28 lệnh có tag "hấp thụ ✓" nhưng grade = 27 B / 1 A | **Chọn:** (a) sửa comment cho đúng sự thật, hoặc (b) thực sự cho `wall` nâng grade. Khuyến nghị (a) — vì per-level không backtest được, đừng biến nó thành gate |
| `reversal_vwap.py` **KHÔNG** phải replicator bản đang ship | lệch 4 hằng số (WICK 0.45 vs 0.50; SL cap 60 vs 70 tick; RR 3.0 vs 1.5) + **thiếu hẳn gate trend** | Thêm chú thích đầu file: *"prototype CŨ, chỉ dùng làm loader"*. Replicator thật = `imp_reversal_sweep.py::detect`. **Lưu ý `optimize_loop.py` đang import `reversal_vwap`** → kết quả tối ưu của nó nói về tham số cũ |
| Docstring ghi **"148 lệnh"** | CSV thực có **140 lệnh** (CBR 112 / QUAY_DAU 28), trải 2026-05-22 → 07-28 | Sửa `review_runner.py:3`, `review_export.py:4`, `runner_stack.py:4` |
| `imp_reversal_sweep.py:7-8` khẳng định *"'Time left' == giờ VN"* | **SAI** — đã chứng minh là UTC ở Bước 1 | Sửa docstring. `imp_entry_lift.py:8` (coi là UTC) mới là đúng |

---

## 7. BƯỚC 6 — ÁP BREAK SẠCH CHO NHÁNH QUAY_DAU? (chưa test)

Chưa đo. Nhưng **về cơ chế thì có thể ngược dấu**: reversal là *fade*, sống nhờ thị trường xoay 2 chiều — đúng cái mà "sạch" loại bỏ.
- **Cách đo:** thêm toggle trong `imp_reversal_sweep.py::detect`, gọi `cbr_v6.counter_sweep()`, sweep look/w.
- **PASS** nếu WR tăng ≥5 điểm **và** dương cả 3 tháng. **KILL** nếu n tụt dưới 15 (mẫu reversal chỉ có 28 lệnh — rất mỏng).
- **Nếu ngược dấu (có quét ngược thì reversal TỐT hơn)** → đó là phát hiện giá trị: dùng cùng một chỉ báo để **định tuyến** nhánh (nền sạch → CBR; nền xoay → reversal). Đây là ứng viên mạnh nhất cho vòng sau.

---

## 8. BƯỚC 7 — REPLICATOR CBR EXACT (nợ hạ tầng)

`cbr_v6.py` đã sát v5 nhưng **chưa phải exact-replica**. Còn lệch:
- Chưa mô phỏng `Dedup` **gộp chung CBR + reversal** (C# dedup trên danh sách gộp → một lệnh reversal cùng phía có thể nuốt lệnh CBR trong 6 nến). Thực nghiệm 5–7/2026 chưa thấy nổ, nhưng đừng coi là an toàn vĩnh viễn.
- `volfloor`: `cbr_v6` dùng `E.calc_volfloor` (percentile) = **17.0**, C# dùng `VolFloor = 20` cứng.
- C# bỏ nến cuối (`i < B.Count-1`); Python quét hết.

**Việc cần làm:** theo đúng khuôn `imp_reversal_sweep.py` — tách một `dict LIVE` ghi rõ tên biến C# tương ứng cho từng hằng số, rồi reconcile với CSV live theo **entry time + side**. Mục tiêu ≥95% khớp như nhánh reversal (27/28).
**PASS:** ≥95% lệnh CBR trong CSV live được tái tạo, 0 lệnh offline thừa.

---

## 9. ĐÃ THỬ VÀ THẤT BẠI — ĐỪNG LÀM LẠI

| Ý tưởng | Luật | Kết quả | Vì sao thất bại |
|---|---|---|---|
| **Bắt buộc có SPRING/UPTHRUST trước break** (Phase C → D theo nghĩa chữ) | W3 | n=26, WR 34.6%, +10R, EV 0.385, **tháng 6 ÂM** | **Ngược dấu.** Giả thuyết ban đầu của tôi SAI. Cú quét hụt gần đó = thị trường đang xoay 2 chiều (Phase B) → break kế tiếp là bẫy. Luật đúng là **đảo lại** = BREAK SẠCH (Bước đã làm #2). Code còn trong `cbr_v6.py` dưới cờ `PHASE_C` để đối chiếu. |
| **Bóp SL 2–4 giá, neo dưới cây M1 vào lệnh** | R7 | n=52, WR 38.5%, +28R, EV 0.538 (vs 47.3%/+49R/0.891) | SL 2.4 giá bị quét sạch. CORVEN bóp SL **kèm khả năng đọc data xác nhận** ("t check data xác nhận t mới vào") — cái đó không mô phỏng được. Trên entry cơ học, SL chặt là **âm**. Phần "gồng dài" của lời khuyên thì ĐÚNG (xem RR sweep). |
| **Leg phải do lệnh CHỦ ĐỘNG đẩy** (ddom leg ≥ ngưỡng) | R1 | n 34→17, +51R→+18R, WR 50%→41% | Nửa số leg có delta âm và **nhóm đó lại tốt hơn**. Cell n=17 → không kết luận được. Xem mục 10. |
| **Loại break "spike rồi tắt"** | R3 | Không loại lệnh nào (0 khác biệt) | Ngưỡng `VSA≥3.0 + cpos<0.55` không bao giờ đồng thời xảy ra sau khi `BreakBody≥0.50` đã lọc. Cần định nghĩa khác nếu muốn thử lại. |
| **Chỉ giao dịch phiên Á+Âu (08–19h)** | R6 | n=46, WR 41.3%, +30R (kém baseline) | Giờ đẹp thật nằm ở phiên Mỹ, nhưng n=9 → không ship được. |

---

## 10. KHÔNG KIỂM ĐƯỢC OFFLINE (đừng hứa với chính mình)

1. **Luật lõi R1 "buy limit vs buy market"** — kiểm định độc lập cho kết quả:
   - *"leg buy-limit đi tiếp NGẮN hơn"* → **SAI**. MFE hai nhóm bằng nhau ở 10/20/30 nến; test đua ±2 USD là null (49.7% vs 48.8%).
   - *"leg buy-limit dễ bị trả hết / MAE lớn hơn"* → **có tín hiệu nhưng yếu và không ổn định theo tháng**; **tháng 5/2026 ngược dấu có ý nghĩa** (p=0.0147).
   - Nếu dùng, đây là tín hiệu về **rủi ro pullback / độ tin cậy của retest**, KHÔNG phải tín hiệu hướng hay mục tiêu chốt lời.
2. **Bẫy khi tự đo lại:** `|ddom|` **không so được** giữa các bar khác volume — 47.9% bar có vol<10, trong nhóm đó 27.4% có `|ddom| = 1.0` chỉ vì bar có 2–3 lot cùng phía. **Bắt buộc gate volume trước khi gate ddom.**
3. `max_one_trade` trong `sample.csv` **toàn bằng 0** → gate "big trade" (thứ CORVEN tích hợp trong Sierra Chart) **không thể** backtest với data này.
4. `perlevel_m1_clean.pkl` **không** phải 2 tháng liên tục: chỉ **25 phiên rời rạc** (tháng 6 chỉ 6 ngày, thủng 06-04→06-25).
5. **Stacked imbalance / hấp thụ từng mức giá / iceberg** — chỉ có LIVE. Giữ ở dạng *bonus hiển thị*, đừng biến thành gate (nếu biến thành gate thì replicator mù ngay).
6. **Cửa sổ trượt 5 nến làm leg chồng lấn nặng** → p-value hoán vị thường **lạc quan giả** (p=0.0002 trên 3.922 leg chồng lấn → p=0.067 trên mẫu độc lập n=231/188). Luôn báo kèm mẫu không chồng lấn.

---

## 11. GIỚI HẠN PHẢI NÓI RA MỖI KHI TRÍCH SỐ

- **dxFeed là proxy YẾU cho feed live.** Cùng kỳ 6–7/2026, nhánh scalp cho WR **61%** trên `fp-m1` nhưng **42%** trên dxFeed. Số v6 ở đây là *tương đối* (v5 vs v6 cùng feed), không phải dự báo WR live.
- **n = 33 lệnh / 3 tháng.** Tháng 5 chỉ góp +5R. GCQ26 chỉ có thanh khoản từ ~tháng 5/2026 → mở rộng cửa sổ về trước ra rác, **không** phải out-of-sample. Muốn OOS thật cần **front-month/CCPA khác**.
- Backtest **không** mô hình hoá spread, slippage, phí, và kiểm **SL trước TP** trong cùng nến (bi quan).
- Cửa sổ 5–7/2026 là **vàng tạo đỉnh** → phía SHORT được ưu ái. Là **regime**, không phải cấu trúc.

---

## 12. TÁI LẬP SỐ

```bash
cd quantower-entry-signal/research/wyckoff
python3 final_table.py     # BẢNG CHỐT — mọi số trong plan này (~3 phút)
python3 cbr_v6.py          # baseline + từng luật riêng lẻ
python3 stack_v6.py        # sweep RR / retrace / span / LEGQ  (số CŨ, trước khi sửa parity)
python3 round4_v6.py       # lớp delta trên merged feed (R1)
```

`build-wyckoff.sh` → `dist/WyckoffRunner.dll`.

**Cạm bẫy khi viết script mới:**
- `entry_cbr.run_cbr` đọc `b['bias']` → **KeyError** với bar của `entry_dxfeed.load_m1`. Dùng `reversal_vwap.load_dxfeed()` hoặc `optimize_loop.bars()`.
- `entry_cbr.py` là **v4**, lệch bản ship: `PULL_MIN=0.40` (C# 0.60), **thiếu** TrendOk/VwapOk/LiqOk, **thiếu** lọc phiên chết.
- Import `entry_dxfeed` như thư viện: phải tự set `E.VOLFLOOR_AUTO = E.calc_volfloor(B)` trước, nếu không `NameError`.
- **Luôn gọi `V.prepare(B)`** trước khi `V.scan(...)` — nếu không sẽ `KeyError: 'liqratio'`.
- `entry_cbr.hit` kiểm SL trước TP không có trạng thái `'amb'`; `reversal_vwap.hit` có `'amb'` → trộn 2 bộ eval ra tổng R khác nhau.

---

## 13. THỨ TỰ THỰC THI ĐỀ XUẤT

1. **Bước 1** (khung giờ chết) — lỗi thật, tác động lớn nhất, 3 dòng code. Kiểm hồi quy bằng `final_table.py`.
2. **Bước 5** (dọn code chết + comment sai) — rẻ, ngăn hiểu sai về sau.
3. **Bước 2 + 3** (chốt RR, A/B thanh khoản) — chỉ là đổi mặc định + phơi input.
4. **Cập nhật header `WyckoffRunner.cs`** thành mô tả v6 (hiện vẫn là văn bản v5) + viết `README` mục WyckoffRunner.
5. **Bước 6** (BREAK SẠCH cho reversal / định tuyến nhánh) — đòn bẩy lớn nhất còn lại.
6. **Bước 7** (replicator exact) — làm khi cần độ tin cậy cao hơn cho vòng sau.
7. Deploy Windows, log 2–4 tuần, đối chiếu CSV với bảng ở mục 0.
