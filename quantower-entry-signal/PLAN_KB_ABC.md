# PLAN — nâng Runner lên 3 kịch bản CORVEN (KB-A / KB-B / KB-C)

> Lập 2026-07-31. Nguồn thiết kế: [CORVEN_SPEC_V1.md](../data-export/messages-with-pro-trader/CORVEN_SPEC_V1.md)
> (đã chốt với người học cùng ngày). Nguồn kỷ luật đo: [SPEC_V7_3KB.md](SPEC_V7_3KB.md) §9 ·
> [AUDIT_V7.md](research/wyckoff/AUDIT_V7.md) · [BASELINE.md](research/wyckoff/BASELINE.md) ·
> [DATA_CAPABILITY.md](research/DATA_CAPABILITY.md).
>
> **Đây là PLAN — không có một con số kết quả nào trong file này.** Mọi số ghi dưới đây là **mốc so**
> (đã đo trước đây, có nguồn) hoặc **ngưỡng PASS/KILL** (quy ước trước khi đo). Khi chạy xong sẽ ghi
> kết quả vào file RESULTS riêng, không sửa ngược vào đây.

---

## §0. Tóm tắt 30 giây

**Phát hiện then chốt khiến việc này rẻ hơn tưởng:** hai engine đang có **đã chính là hai play của
CORVEN**, chỉ **neo sai vùng**.

| Đang có | Là play nào của CORVEN | Sai ở đâu |
|---|---|---|
| **KB1 / CBR** (phá range → hồi → tiếp diễn), n=33 EV+1.424 @RR4 | **Play 2 — phá vùng → hồi → đánh tiếp** | Neo vào **range co hẹp M1 nội bộ**, không phải **HVN** |
| **KB2 / QUAY_DAU** (chạm → fade), n=27 EV+0.389 @RR1.5 | **Play 1 — chạm vùng → đảo chiều** | Neo **chỉ VWAP phiên**; thiếu **HVN tuần/ngày**; thiếu **VWAP tuần** |
| KB3 (biên↔biên trong range) | **Không thuộc hệ CORVEN** | Giữ nguyên trạng KILL |

⇒ Việc chính **không phải viết engine mới**, mà là **đổi tầng neo vùng** (zone provider) + **thêm nến
xác nhận M1** + **thống nhất RR 1:3**, rồi để **cùng một cặp play** chạy trên **ba tầng vùng khác nhau**
(tuần / ngày / không vùng). Đó là lý do plan này chia theo **tầng vùng**, không chia theo engine.

**Kiến trúc đích:**

```
                    ┌─ ZONE PROVIDER (mới) ──────────────────┐
                    │  HVN tuần · VWAP tuần (neo đầu tuần)   │  → KB-A
                    │  HVN ngày · VWAP ngày                  │  → KB-B
                    └────────────────┬───────────────────────┘
                                     │  (không dùng vùng)
   ┌─────────────────────────────────┴──────────┐        ┌──────────────┐
   │ PLAY 1: chạm → đảo chiều  (từ KB2)         │        │ KB-C         │
   │ PLAY 2: phá → hồi → tiếp  (từ KB1)         │        │ push-in-move │
   └────────────────┬───────────────────────────┘        └──────┬───────┘
                    │        NẾN XÁC NHẬN M1 (bắt buộc, mới)    │
                    └──────────────────┬───────────────────────┘
                              RR 1:3 · SL dưới cây M1 · đóng trong ngày
                                   ROUTER 1 vị thế (đã có)
```

---

## §1. ⚠ CHỐNG TRÙNG TÊN — bắt buộc đọc

Repo đã dùng `KB1/KB2/KB3` với nghĩa **khác** (SPEC_V7_3KB.md). CORVEN dùng `KB-A/KB-B/KB-C`. Hai bộ
tên này **không map 1-1**. Quy ước từ nay:

- **`KB-A` / `KB-B` / `KB-C`** (có gạch nối) = **kịch bản CORVEN** — theo *tầng vùng*.
- **`PLAY1` / `PLAY2`** = *cách đánh tại vùng* (chạm-đảo / phá-hồi). Một kịch bản có thể chạy cả 2 play.
- **`KB1/KB2/KB3`** (không gạch) = tên **cũ**, chỉ dùng khi trích dẫn số lịch sử. **Không đặt tên module mới bằng nó.**
- Module mới nằm trong **`research/wyckoff/v8/`**, tên không chứa `kb1/kb2/kb3`.

| Module mới | Vai trò |
|---|---|
| `v8/zones_corven.py` | Zone provider: HVN tuần/ngày + VWAP tuần/ngày, **causal snapshot** |
| `v8/confirm_m1.py` | Nến xác nhận M1 (§4.3) — dùng chung cả 3 kịch bản |
| `v8/play_touch.py` | PLAY1 chạm→đảo chiều (gọi lại `imp_reversal_sweep.detect` để giữ parity) |
| `v8/play_breakret.py` | PLAY2 phá→hồi→tiếp (gọi lại `cbr_v6` để giữ parity) |
| `v8/flow_push.py` | KB-C: nhận diện move + nến đẩy chủ động |
| `v8/run_abc.py` | Chạy toàn bộ + in bảng + đối chứng ngẫu nhiên |

Dùng lại nguyên trạng, **không sửa**: `v7/loaders.py`, `v7/report.py` (`line/partition/sweep/mdd/_half_split`),
`v7/engine.py` (`hit_v7`, `evaluate_v7`, `route_one_position`), `wyckoff/kb2_zones.py` (khung snapshot causal),
`quantower-tpo-suite/verify_zones_v2.py` (`value_area`, `find_peaks`, `find_hvn`).

---

## §2. BỐN CHẶN phải xử lý TRƯỚC khi đo (không làm là mọi số vô nghĩa)

### 2.1 ✅ `volfloor` look-ahead — ĐÃ SỬA (phiên 2026-07-29, trước cả khi viết plan này)
Ghi chú P0 lúc lập plan bị lỗi thời: đã kiểm lại 2026-07-31, `BASELINE.md` §8 ghi rõ việc này **XONG** —
`VOLFLOOR_FROZEN=20.0` (khớp hằng số cứng trong `RunnerSignal.cs`, không look-ahead), 2 nơi gọi trong
`v7/run_kb12.py` / `v7/run_kb3.py` đã chuyển sang dùng hằng này thay vì `calc_volfloor()` percentile-30
nhìn trước. Chạy lại `run_kb12.py` hôm nay xác nhận: **GOLDEN OK**, KB1 vẫn `n=33 WR=48.5% EV=+1.424
MDD=3R`, KB2 vẫn `n=27 EV=+0.389` — khớp tuyệt đối BASELINE, không đổi số. ⇒ **P0 coi như đã xong, không
cần làm lại.** Mốc so ở §6.1 vẫn dùng nguyên, không cần đo lại BASELINE mới.

### 2.2 🟠 RR 1:3 cho PLAY1 xung đột với số đã đo
Người học chốt **RR 1:3 cho mọi kịch bản**. Nhưng repo đã đo **MFE trần của lệnh đảo chiều ≈ 1.3R**
([SPEC §5.5](SPEC_V7_3KB.md)) — nên RR1.5 mới được chọn cho KB2. Ngược lại RR3 **đã** được xác nhận tốt
cho play phá-hồi (KB1 @RR3: WR 57.6%).
**Không tranh luận — đo.** Bước 0 là **probe MFE**: với tập tín hiệu PLAY1 neo **HVN tuần/ngày** (chứ không
phải VWAP phiên như lần đo cũ), in phân phối MFE theo R: `P(MFE≥1.5R)`, `P(≥2R)`, `≥3R`, `≥4R`.
- Nếu `P(MFE≥3R) ≥ 35%` → RR3 khả thi, đi tiếp theo spec.
- Nếu `< 20%` → **báo lại người học kèm số**, đề xuất RR3 cho PLAY2 / RR1.5-2 cho PLAY1. Không tự đổi spec.
Lý do probe này rẻ và phải làm đầu: nó quyết định RR của **hai trong ba** kịch bản.

### 2.3 🟠 "Bubble big trade" của KB-C **không đo được trực tiếp**
[DATA_CAPABILITY](research/DATA_CAPABILITY.md): **`max_one_trade` = 0 ở MỌI file**, kể cả 761.199 dòng
per-level → **không nguồn nào cho biết lệnh đơn lớn nhất trong nến**.
**Cách xử lý (giữ parity live):** dùng đúng **fallback mà indicator đang ship** đã dùng —
[OrderFlowBubbles.cs](../quantower-orderflow-indicator/OrderFlowBubbles.cs) dòng ~620: khi `mot=0` thì
`metric = vol` mỗi mức giá, gắn nhãn *"HVN cell · vol/ô"*, và bubble nổ khi `ModZ(metric) ≥ BigZ`.
⇒ Backtest định nghĩa **big trade = mức giá có volume z-score ≥ BigZ so với phân phối per-level rolling**.
Đây là **proxy**, phải ghi rõ trong mọi báo cáo. Không được viết "đã test tín hiệu big trade của CORVEN".

### 2.4 🟠 Độ phủ dữ liệu per-level cho KB-C
`perlevel_m1_clean.pkl` = **25 phiên** (06-01→07-27); `perlevel_m1.pkl` = 46 ngày (05-01→07-27) nhưng
gồm cả tháng 6 có cột Volume hỏng ở nguồn fp-m1. dxFeed 3 tháng thanh khoản có ~**60 ngày**.
⇒ KB-C chỉ đo được trên **~25-46/60 ngày**, và DATA_CAPABILITY đã cảnh báo: độ phủ thưa khiến **mọi**
thống kê per-level dễ overfit vào đúng những ngày ngẫu nhiên có mặt.
**Quyết định:** KB-C làm **sau cùng**, và kết quả KB-C **không được cấp vốn** dựa trên backtest — chỉ
được phép **log live** để lấy OOS. Ghi rõ điều này ngay khi báo cáo, đừng để người học kỳ vọng sai.

---

## §3. Tầng vùng — cái phải xây mới

### 3.1 Mốc tuần
- **VWAP tuần:** neo **đầu tuần, reset 1 lần/tuần** (A1 — người học xác nhận). Mốc = **start của phiên đầu
  tiên trong tuần**. Phiên trong hệ này bắt đầu ~**22:00 UTC** ([SPEC §1.2](SPEC_V7_3KB.md)), CN có dữ liệu
  và T7 không → mốc tuần = phiên đầu tiên có start ≥ **CN 21:00 UTC**.
  ⚠ Phải **in ra 13 mốc tuần** của 5-7/2026 và mắt thường xác nhận trước khi tin (DST làm giờ nghỉ CME dịch
  21h↔22h UTC — DATA_CAPABILITY §1.1).
- **HVN tuần:** dựng **một** profile cho **cả tuần** từ M1 (volume theo mức giá), rồi `find_hvn` (dùng lại
  hàm đã có trong `verify_zones_v2.py`). **Chỉ HVN** — không POC/VAH/VAL (A2).

### 3.2 Nhân quả (bắt buộc)
Vùng tuần đang-chạy **không được** dùng volume của tương lai. Hai chế độ, **A/B cả hai**:
- **`W_CLOSED`** — chỉ dùng HVN của **tuần đã đóng** (tuần N-1) cho toàn bộ tuần N. An toàn tuyệt đối.
- **`W_RUNNING`** — HVN của tuần đang chạy, tính lại tại **mỗi lần đóng phiên**, chỉ từ dữ liệu đã đóng.
  Giống cách trader nhìn chart thật hơn, nhưng vùng dịch chuyển trong tuần.
Snapshot theo đúng khuôn `build_zone_series` trong [kb2_zones.py](research/wyckoff/kb2_zones.py) (đã kiểm
causal). HVN ngày làm tương tự với `D_CLOSED` / `D_RUNNING`.

### 3.3 Cắt indicator cho khớp
[SessionZones.cs](../quantower-tpo-suite/SessionZones.cs) đang vẽ 7 loại vùng; CORVEN dùng **1** (HVN) và
**không dùng vùng theo phiên Á-Âu-Mỹ** (C4: *"tất nhiên là không rồi"*).
**Việc:** thêm input `CorvenMode` — bật thì chỉ vẽ **HVN tuần + HVN ngày + VWAP tuần/ngày**, tắt hết
naked POC / cụm POC / băng giá trị / prior H/L / va_edge và tắt vùng theo phiên. **Không xoá code cũ**
(vẫn cần để đối chiếu lịch sử), chỉ thêm cờ. Đổi luôn nhãn "VÙNG CANH" → nêu rõ **HVN**.

---

## §4. Ba kịch bản — đặc tả để code

### 4.1 Bất biến (cả 3)
`RR = 3.0` · `TP` theo R cố định · **đóng trong ngày** (cắt tại cuối phiên, không qua đêm) ·
`SL` neo **dưới/trên cây M1 vào lệnh** + buffer 2 tick, sàn/trần đề xuất **2.0 / 4.0 giá**
([R7](../data-export/messages-with-pro-trader/RULES.md)) · **bắt buộc nến xác nhận M1** · router 1 vị thế.

### 4.2 KB-A và KB-B — cùng logic, khác tầng vùng
Chạy **cả PLAY1 và PLAY2** trên vùng của mình.
- **PLAY1 (chạm → đảo chiều):** giá tới vùng (tol đề xuất 12 tick, sweep {8,12,20}) → nến xác nhận M1
  ngược hướng chạm → vào. Giữ gate **R2** (vùng bị chạm phải ở 25% biên của range gần) và **R10** (phải
  có nến từ chối **CÓ** volume — cấm dùng "vol thấp" làm tín hiệu).
- **PLAY2 (phá → hồi → tiếp):** nến đóng vượt qua vùng → trong `WaitBars` giá hồi về mép vùng nhưng
  **giữ** → nến xác nhận M1 thuận hướng phá → vào. Đây là `cbr_v6` với `edge` = **mép HVN** thay vì mép
  range co hẹp.
- Khác biệt duy nhất giữa A và B = **nguồn vùng** (tuần vs ngày). Kỳ vọng: **A có WR cao hơn B** (người học
  xác nhận) — đây là **giả thuyết kiểm được**, xem §6.3.

### 4.3 Nến xác nhận M1 (`confirm_m1.py`) — dùng chung
Định nghĩa đề xuất ⟦CẦN KIỂM⟧, cho LONG (SHORT gương lại): `close > open` **và** `cpos ≥ 0.60`
(đóng ở nửa trên) **và** `brat ≥ 0.30` (thân ≥30% range) **và** râu ngược `≤ 35%` range (R9).
**Bắt buộc A/B `ConfirmOn ∈ {false, true}`** — nếu bật mà EV không tăng thì nó chỉ là bộ lọc giảm n, phải
biết điều đó bằng số chứ không giữ vì "pro trader nói vậy".

### 4.4 KB-C — follow order flow trong move
- **Tiền đề (`in_move`):** `K` nến liên tiếp cùng chiều **và** delta `K` nến liên tiếp cùng dấu.
  `K` đề xuất 3, sweep {2,3,4}. **Không** đòi delta tăng dần (B2).
- **Trigger (`push_bar`):** nến có **big-trade proxy** (§2.3) nằm ở **30% dưới** nến (LONG) / 30% trên
  (SHORT), **và** delta nến cùng dấu hướng move, **và** `brat ≥ 0.30`.
- **Cấm:** vào ngược move ("ko cản tàu") — hard gate, không phải điểm cộng.
- **Không dùng** VSA/volume climax cho nhánh này (B1 nói rõ) → đây là điểm khác biệt cơ chế so với KB1.
- Cần `v8/loader_perlevel.py` (DATA_CAPABILITY §c ghi rõ hiện **chưa có** loader dùng chung cho pkl).

---

## §5. Các pha, mỗi pha có ĐIỂM DỪNG

Mỗi pha: chạy → in bảng (dùng `report.line`) → **dừng, báo người học** → mới đi tiếp. Không gộp pha.

| Pha | Việc | Đầu ra | Cổng để đi tiếp |
|---|---|---|---|
| **P0** | ✅ **Đã xong trước plan này** (§2.1) — chỉ xác nhận lại GOLDEN | GOLDEN OK, số khớp BASELINE cũ | (đã qua) |
| **P1** | `zones_corven.py` + in 13 mốc tuần + đếm vùng/tuần | Bảng vùng + ảnh chart để mắt kiểm | Mốc tuần đúng bằng mắt; HVN tuần trông hợp lý trên chart |
| **P2** | **Probe MFE** cho PLAY1 tại HVN (§2.2) | Phân phối MFE theo R | `P(MFE≥3R)` ≥35% → RR3; <20% → báo lại, chờ quyết |
| **P3** | KB-A: PLAY1 + PLAY2 tại vùng tuần, `ConfirmOn` A/B, `W_CLOSED` vs `W_RUNNING` | Bảng n/WR/EV/MDD + partition | §6 PASS/KILL |
| **P4** | **Đối chứng ngẫu nhiên KB-A** (dịch HVN ±3 giá, 5 seed) | Bảng thật vs ngẫu nhiên | chênh EV ≥ **+0.25R** mới đi tiếp; nếu không → KB-A KILL, dừng cả plan |
| **P5** | KB-B tại vùng ngày, cùng bộ biến thể | Bảng + so A vs B | §6.3 |
| **P6** | Chi phí giao dịch: quét cost 0→8 tick/lượt | Bảng EV theo cost | EV còn dương ở **≥4 tick** |
| **P7** | KB-C (chỉ ngày có per-level), kèm cảnh báo độ phủ | Bảng riêng, **không trộn** số với A/B | Chỉ để log live, không cấp vốn |
| **P8** | Port sang **`WyckoffRunner.cs` v8** (giữ `RunnerSignal.cs` v5 live **không đụng**) | DLL + parity harness | Parity C#↔Python ≥ 95% lệnh khớp |

**Ước lượng:** P0-P2 ~1 lượt · P3-P4 ~1-2 lượt · P5-P6 ~1 lượt · P7 ~1 lượt · P8 ~1-2 lượt.

---

## §6. PASS / KILL — chốt TRƯỚC khi đo

### 6.1 Mốc so
KB1 @RR4: n=33 WR 48.5% EV +1.424 MDD 3R · KB2 @RR1.5: n=27 WR 55.6% EV +0.389 MDD 5R
([BASELINE.md](research/wyckoff/BASELINE.md)) — ✅ đã xác nhận lại 2026-07-31 sau P0, không đổi số.
Mục tiêu người học chốt: **WR 40-50% @ RR3** ⇒ EV thiết kê **+0.60 … +1.00R**. Hoà vốn tại RR3 = **25%**.

### 6.2 Ngưỡng mỗi nhánh
| Tiêu chí | PASS | KILL |
|---|---|---|
| n | ≥ **25** | < 15 → KILL; 15-24 → "không kết luận", không ship |
| WR @RR3 | ≥ **35%** (EV +0.40) | < 28% |
| EV | ≥ **+0.40R** | < +0.20R |
| MDD | ≤ 8R | > 15R |
| Theo tháng (5/6/7) | ≤1 tháng âm, \|R\|≤2R, **và tháng 7 không được âm** | ≥2 tháng âm |
| 2 nửa kỳ | cả hai > 0 | một nửa ≤ 0 |
| Đối chứng ngẫu nhiên | thật − ngẫu nhiên ≥ **+0.25R** | < +0.10R → **KILL** |
| Chi phí | dương ở ≥4 tick/lượt | chết ở ≤2 tick |
| Hạn mức cấu hình | ≤ **10 mỗi kịch bản** (Bonferroni: p phải < 0.005 mới coi là thật) | vượt → coi là dò tìm, không ship |

### 6.3 Kiểm chứng đặc tả (mới — dùng lời CORVEN làm phép thử)
CORVEN cho hai con số **kiểm được**, dùng chúng để test xem *định nghĩa vùng của mình có đúng ý anh ấy không*:
1. **Tần suất:** KB-A ≈ **10 lệnh/tuần** ⇒ 13 tuần (5-7/2026) nên ra **~130 lệnh**. Nếu ra <30 hoặc >400
   thì **định nghĩa vùng/trigger của mình lệch khỏi hệ anh ấy**, phải sửa định nghĩa **trước** khi đọc EV.
   Đây là kiểm tra *conformance*, không phải kiểm tra lợi nhuận — và nó độc lập với chuyện có lãi hay không.
2. **Thứ tự WR:** `WR(KB-A) > WR(KB-B)`. Nếu đo ra ngược thì hoặc vùng tuần dựng sai, hoặc lời anh ấy không
   đúng trên cửa sổ này — cả hai đều phải báo, **không im lặng chọn cái tốt hơn**.

### 6.4 Bắt buộc, không được bỏ
- **LONG/SHORT tách bảng** (AUDIT K vẫn đang thiếu ở mọi báo cáo).
- **Đối chứng ngẫu nhiên** cho mọi kết luận có dính vị trí vùng (bài học KB2×vùng 2026-07-31).
- **Cao nguyên, không mũi nhọn:** tham số thắng phải có láng giềng cũng thắng.
- Khi in bảng, **không** in kèm giả thuyết. Đọc số trước, giải thích sau.

---

## §7. Không đo được offline (nói trước, khỏi hứa)
- **Lệnh đơn lớn (`max_one_trade`)** = 0 ở mọi file → KB-C chỉ có **proxy** (§2.3).
- **OOS thật:** cả 3 kịch bản đo trên **cùng 3 tháng, cùng một chế độ, cùng một hợp đồng**. GCQ26 vừa qua
  First Notice Day 31/07 → cần **GCZ26/continuous** để có OOS độc lập. Đây vẫn là nghẽn lớn nhất của cả
  dự án, plan này **không** giải quyết nó.
- **Sổ lệnh (order book), rút/huỷ limit:** không có → không kiểm được R1 ở mức "limit kê" thật.

---

## §8. Việc KHÔNG làm trong plan này
- Không đụng `RunnerSignal.cs` (v5 đang chạy live) — chỉ sửa `WyckoffRunner.cs`.
- Không hồi sinh KB3 (biên↔biên) — không thuộc hệ CORVEN.
- Không xoá 5 loại vùng khỏi SessionZones — chỉ thêm cờ `CorvenMode`.
- Không tăng số lệnh bằng cách nới gate. Bài học 2026-07-31: n tăng ×2.4 mà EV về 0 là **thất bại**, không
  phải tiến bộ.
