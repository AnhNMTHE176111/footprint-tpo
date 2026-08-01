# RESULTS — đổi tầng vùng EntrySignal (M1) sang bộ vùng CORVEN

> Phiên nghiên cứu 2026-08-01. Đối tượng: `quantower-entry-signal/EntrySignal.cs`. Nguồn dữ liệu:
> **dxFeed** (`research/entry_dxfeed.py`) — không dùng fp-m1 (cột Volume hỏng 04/06→26/06,
> BASELINE.md §8). Toàn bộ script nằm trong `v8/entry/` (P0-P5 Python), chưa đụng C#/EntrySignal.cs.

## Kết luận thẳng (đọc trước khi xem bảng)

**Bộ vùng CORVEN (HVN tuần/ngày + VWAP tuần/ngày) làm EntrySignal (M1) TỆ HƠN, không phải tốt hơn —
và chưa có bằng chứng đủ mạnh để nói vị trí vùng mới mang thông tin thật.** Cụ thể:

1. Với gate gốc `MinConfluence≥2` (đang ship), pool CORVEN chỉ còn 4 loại vùng (so với 7 loại của pool
   cũ) khiến số lệnh **sụp gần hết**: n từ 3 đến 10 trên cả 3 tháng — dưới ngưỡng "không kết luận" (n<15).
2. Hạ `MinConfluence` xuống 1 (mất hẳn lớp gate hợp lưu, không phải đơn giản hoá) mới ra được n=58 —
   cấu hình DUY NHẤT trong 7 cấu hình đã thử đạt n≥25.
3. Cấu hình sống sót đó (SAU-B) có EV chỉ +0.034R/lệnh (gần như hoà vốn), **chết ở phí ≥2 tick** (KILL
   theo đúng ngưỡng đã chốt trước khi đo), và đối chứng ngẫu nhiên cho chênh **+0.173R** — nằm trong
   vùng "không rõ ràng" (0.10–0.25), không đạt +0.25R để PASS.
4. **Không port sang C#** (theo đúng luật đã chốt: P6 chỉ làm nếu P4 và P5 qua — ở đây cả hai đều
   không qua). `EntrySignal.cs` giữ nguyên, không sửa dòng nào.

## 1. Nguồn dữ liệu + quy tắc dùng chung

- dxFeed 9 tháng (`data-export/27-7/..._dxFeed...csv`), 103.857 nến M1, scored 5-7/2026.
- Warm-up: bỏ 5 ngày giao dịch đầu tháng 5/2026 (cutoff quan sát = 2026-05-07) — áp **giống hệt**
  cho TRƯỚC và SAU. Vì dxFeed nạp lịch sử từ 2025-11 nên pool không hề "lạnh" ở đầu kỳ scored
  (DATA_CAPABILITY §4.3) — cả TRƯỚC lẫn SAU đều **0 tín hiệu bị cắt** bởi warm-up này.
- R dùng cho EV/WR/MDD = kết quả tới **RR cố định** (không nới TP tới vùng kế) — khớp CORVEN_SPEC
  "TP theo R cố định, không hết lực thì ra". TRƯỚC dùng RR=1.5 (giá trị đang ship); SAU thử cả 1.5 và 3.0.
- VolFloor dùng hằng số nhân quả `VOLFLOOR_FROZEN=20.0` (khớp `EntrySignal.cs` mặc định), không dùng
  `calc_volfloor()` look-ahead (AUDIT_V7.md §1.2).

## 2. P1 — kiểm zone provider CORVEN

- **13 mốc tuần 5-7/2026**: bám đúng ranh giới CME (~22:00 UTC), có dịch 21h↔22h quanh DST (chuyển
  chính xác từ 8/3/2026). Từ sau DST, mọi tuần trong cửa sổ scored đều đúng 5 ngày Thứ2-Thứ6.
- **Số vùng/tuần**: cố định 3/tuần trong toàn bộ 13 tuần scored, **không đổi** khi sweep
  `min_ratio ∈ {1.3, 1.5, 1.8}` — cao nguyên thật (bị chặn bởi `max_n=3`, không bởi ngưỡng tỷ lệ).
- **Số vùng/ngày**: trung bình chỉ 0.60 HVN/ngày trên toàn lịch sử (578/737 ngày **KHÔNG có** HVN
  ngày nào) — vùng ngày rất thưa, ảnh hưởng trực tiếp tới KB-B/PLAY tại vùng ngày.
- **Nhân quả — W_CLOSED**: cắt chuỗi tại mốc giữa tuần và giữa ngày, tính lại — **trùng khít tuyệt đối**
  cả 2 trường hợp. An toàn, dùng làm mặc định.
- **⚠ Bug phát hiện ở file dùng chung (READ-ONLY, không tự sửa)**: `zones_corven.py`,
  `causal='running'` — khi cắt chuỗi giữa ngày rồi tính lại, kết quả **LỆCH** với bản đầy đủ
  (`4344.2/4355.5/4366.7` vs `4285.3/4341.5/4355.5` tại cùng mốc `2026-06-10 09:32`). Nguyên nhân:
  `group_days()` luôn coi ngày CUỐI CÙNG của dữ liệu đang có là ngày "đã đóng" (`(fr, len(B)-1)`),
  không phân biệt được "hết dữ liệu vì đang chạy live" với "hết ngày vì có gap thật". Khi dùng
  `causal='running'`, điều này khiến snapshot tại một mốc-giữa-ngày bất kỳ vô tình dùng dữ liệu của
  CHÍNH ngày đang hình thành thay vì dùng ngày trước đó đã đóng — khác với ý định "chốt lại mỗi lần
  đóng 1 NGÀY" ghi trong docstring của chính module. Backtest chạy 1 lần trên toàn bộ B không bị lỗi
  này (vì ngày nào cũng có gap thật để đóng), nhưng **live sẽ dính lỗi này liên tục** vì luôn ở trạng
  thái "vừa hết dữ liệu". ⇒ báo cáo này **chỉ dùng W_CLOSED** làm số chính thức; W_RUNNING (cấu hình
  SAU-G) chỉ để đối chiếu, không dùng để PASS/KILL.

## 3. P2/P3 — 7 cấu hình đã thử (≤10, còn 3 suất)

| # | Cấu hình | n | WR% | Tổng R | EV/lệnh | MDD | Ghi chú |
|---|---|---:|---:|---:|---:|---:|---|
| SAU-A | MinConfl=2, RR1.5, confirm=off | 3 | 33.3% | -0.5R | -0.167 | 2.0R | sụp — MinConfl=2 quá chặt cho pool 4 loại |
| SAU-B | **MinConfl=1**, RR1.5, confirm=off | **58** | 41.4% | +2.0R | **+0.034** | 11.5R | DUY NHẤT đạt n≥25 |
| SAU-C | MinConfl=2, RR3.0, confirm=off | 3 | 0.0% | -3.0R | -1.000 | 3.0R | sụp |
| SAU-D | MinConfl=2, RR1.5, confirm=ON | 1 | 0.0% | -1.0R | -1.000 | 1.0R | sụp — thêm gate lại càng ít lệnh |
| SAU-E | MinConfl=2, RR3.0, confirm=ON (đúng SPEC) | 1 | 0.0% | -1.0R | -1.000 | 1.0R | sụp |
| SAU-F | MinConfl=1, RR3.0, confirm=ON | 10 | 30.0% | +2.0R | +0.200 | 5.0R | n=10 <15 → KILL theo cỡ mẫu |
| SAU-G | như E, causal=running (⚠ chưa xác nhận nhân quả — xem P1) | 0 | — | — | — | — | 0 lệnh, không dùng |

**Đọc trung thực:** MỌI cấu hình giữ nguyên `MinConfluence=2` (giá trị đang ship) đều sụp về n=1-3.
Phải hạ hẳn xuống `MinConfluence=1` — mất lớp gate hợp lưu chứ không phải đơn giản hoá — mới có n dùng
được. Thêm nến xác nhận M1 (`ConfirmOn`) hoặc RR3 chỉ làm n sụp thêm, không cứu được vấn đề gốc: pool
CORVEN (4 loại vùng, ngày chỉ 0.6 HVN/ngày) quá thưa cho state-machine PLAY1/PLAY2 hiện tại.

Cấu hình sống sót duy nhất — **SAU-B** — bảng chi tiết:

```
TONG    n=58 WR=41.4% tổng=+2.0R  EV=+0.034 MDD=11.5R | 05:-4.5 06:-3.0 07:+9.5 ✗ | nửa1 -9.0R(n29) nửa2 +11.0R(n29)
LONG    n=33 WR=36.4% tổng=-3.0R  EV=-0.091 MDD= 8.0R
SHORT   n=25 WR=48.0% tổng=+5.0R  EV=+0.200 MDD= 4.5R
PLAY1 chạm-đảo  n=51 WR=41.2% tổng=+1.5R EV=+0.029 MDD=9.0R
PLAY2 phá-hồi   n= 7 WR=42.9% tổng=+0.5R EV=+0.071 MDD=4.0R
```

## 4. P4 — đối chứng ngẫu nhiên (trên SAU-B, MinConfl=1 RR1.5 confirm=off)

Dịch riêng các vùng **HVN tuần/ngày** đi ±3 giá (giữ nguyên VWAP — VWAP là công thức tính động, không
phải "vị trí vùng" chọn tuỳ ý; điều đang kiểm là vị trí HVN có mang thông tin không), 5 seed:

```
THẬT          n=58  EV=+0.034
seed=1 n=53  EV=-0.198   seed=2 n=66  EV=-0.280   seed=3 n=56  EV=-0.107
seed=4 n=59  EV=-0.195   seed=5 n=62  EV=+0.089
EV(ngẫu nhiên TB 5 seed) = -0.138
```

**Chênh = +0.034 − (−0.138) = +0.173R** — nằm trong vùng **"không rõ ràng"** (0.10 ≤ chênh < 0.25),
không đạt +0.25R để PASS. Không KILL tuyệt đối, nhưng không đủ để tuyên bố vị trí HVN mang thông tin.

## 5. P5 — chi phí giao dịch (trên SAU-B)

```
cost=0 tick  EV=+0.034   cost=1 tick  EV=+0.010   cost=2 tick  EV=-0.015 ← ÂM
cost=3 tick  EV=-0.040   cost=4 tick  EV=-0.064   cost=6 tick  EV=-0.114   cost=8 tick  EV=-0.163
```

**Chết ở đúng 2 tick/lượt** → KILL theo ngưỡng đã chốt trước khi đo ("chết ở ≤2 tick = KILL"). Vàng
giao dịch thực tế phí thường 2-3 tick — cấu hình này không sống nổi phí thật.

## 6. Đối chiếu — TRƯỚC (pool cũ) cũng đo lại random-control + cost cho công bằng

```
THẬT (pool cũ, MinConfl=2 RR1.5)   n=129  EV=+0.085
Ngẫu nhiên (dịch MỌI vùng ±3 giá, 5 seed):
  seed=1 n=144 EV=+0.059   seed=2 n=114 EV=+0.096   seed=3 n=138 EV=+0.123
  seed=4 n=122 EV=+0.107   seed=5 n=140 EV=+0.018
EV(ngẫu nhiên TB 5 seed) = +0.081   =>  chênh = +0.085 − 0.081 = +0.005R

Cost sweep 0-8 tick (n=129):
  cost=0 EV=+0.085   cost=1 EV=+0.061   cost=2 EV=+0.036   cost=3 EV=+0.012
  cost=4 EV=-0.013 ← ÂM   cost=6 EV=-0.062   cost=8 EV=-0.111
```

**Phát hiện đáng chú ý, không nằm trong phạm vi câu hỏi ban đầu nhưng phải nói:** ngay cả **pool CŨ
đang ship** cũng gần như không phân biệt được với vị trí vùng ngẫu nhiên trên dxFeed 5-7/2026 (chênh
chỉ **+0.005R**, thấp hơn nhiều so với chênh +0.173R của SAU-B). Sống tới phí 3 tick, chết ở 4 tick —
sát nhưng không đạt ngưỡng "dương ở ≥4 tick". Tức là: theo đúng phép đo này, edge "vị trí vùng" của
CHÍNH signal đang ship cũng chưa được chứng minh trên dxFeed — đây không phải kết luận về CORVEN, mà
là một giới hạn chung của phương pháp/dữ liệu cần người học biết, tách bạch khỏi câu hỏi "CORVEN có
tốt hơn không".

## 7. Bảng cuối (deliverable chính)

| Thông số | TRƯỚC (pool cũ, MinConfl=2) | SAU (SAU-B, MinConfl=1) | Δ |
|---|---:|---:|---:|
| Nguồn dữ liệu + cửa sổ | dxFeed 5-7/2026, warmup 5 ngày | dxFeed 5-7/2026, warmup 5 ngày | giống nhau |
| n (số lệnh) | 129 | 58 | −71 (−55%) |
| WR % | 43.4% | 41.4% | −2.0đ |
| Tổng R | +11.0R | +2.0R | −9.0R |
| EV / lệnh (R) | +0.085 | +0.034 | −0.051 |
| MDD (R) | 18.0R | 11.5R | −6.5R ↑ (tốt hơn, nhưng vì n ít hơn) |
| Tháng 5 (R) | +7.5 | −4.5 | −12.0 |
| Tháng 6 (R) | +8.5 | −3.0 | −11.5 |
| Tháng 7 (R) | −5.0 | +9.5 | +14.5 ↑ |
| Nửa kỳ 1 (R, n) | +16.0R (n64) | −9.0R (n29) | đảo dấu |
| Nửa kỳ 2 (R, n) | −5.0R (n65) | +11.0R (n29) | đảo dấu |
| LONG: n/WR/EV | 61 / 39.3% / −0.016 | 33 / 36.4% / −0.091 | LONG vẫn âm, âm sâu hơn |
| SHORT: n/WR/EV | 68 / 47.1% / +0.176 | 25 / 48.0% / +0.200 | tương đương |
| PLAY1 chạm-đảo: n/EV | 90 / +0.111 | 51 / +0.029 | giảm mạnh |
| PLAY2 phá-hồi: n/EV | 39 / +0.026 | 7 / +0.071 | n quá nhỏ để so |
| EV − EV(ngẫu nhiên, 5 seed) | +0.005 (không rõ ràng, rất yếu) | +0.173 (không rõ ràng) | SAU nhỉnh hơn nhưng cả 2 đều dưới ngưỡng PASS +0.25 |
| EV @ phí 2 tick | +0.036 | −0.015 (KILL) | TRƯỚC còn sống, SAU đã chết |
| EV @ phí 4 tick | −0.013 (chết, sát ngưỡng) | −0.064 (KILL) | cả 2 đều âm ở 4 tick |
| Số cấu hình đã thử | 1 (số ship, không sweep thêm ở phiên này) | 7 | /10 |
| KẾT LUẬN | — (không phải mục tiêu đổi ở phiên này) | **KILL / không đủ bằng chứng — không port sang C#** | — |

## 8. Cái gì KHÔNG đo được / chưa làm

- **Không port sang C#** (`CorvenZones` input) — đúng luật "P6 chỉ làm nếu P4 và P5 qua"; cả hai đều
  không qua ở đây. `EntrySignal.cs` giữ nguyên 100%.
- **W_RUNNING** không dùng làm số chính thức — bug nhân quả phát hiện ở P1 (mục 2), thuộc file dùng
  chung `zones_corven.py`, không tự sửa.
- **KB-C (follow order-flow)** không nằm trong phạm vi phiên này (chỉ làm PLAY1/PLAY2 tại vùng, đúng
  phạm vi `EntrySignal.cs`).
- Chưa thử thêm cấu hình (còn 3/10 suất) vì P4/P5 đã cho tín hiệu KILL rõ ràng trên ứng viên khả dĩ
  duy nhất — dò thêm cấu hình lúc này là "tìm cấu hình thứ 8 để cứu kết luận", đúng điều PHẦN 6 cấm.
- Cửa sổ 5-7/2026 vẫn là **một** regime, **một** hợp đồng, không có điểm out-of-sample nào
  (BASELINE.md §0) — áp dụng cho cả TRƯỚC lẫn SAU ở báo cáo này.

## 9. Trả lời thẳng

**Bộ vùng CORVEN có làm EntrySignal (M1) tốt hơn không?** Không — và hiện tại là **tệ hơn về mọi mặt
đo được** (n sụp gần hết trừ khi hạ gate hợp lưu; cấu hình sống sót duy nhất có EV gần bằng 0, chết ở
phí 2 tick, và đối chứng ngẫu nhiên không đạt ngưỡng để nói vị trí vùng mang thông tin thật). Nguyên
nhân gốc không phải "định nghĩa vùng sai" mà là **pool CORVEN quá thưa** cho state-machine hiện tại
(chỉ 4 loại vùng, vùng ngày trung bình 0.6/ngày) — nếu muốn cứu ý tưởng này, việc cần làm trước là dựng
lại chính state-machine PLAY1/PLAY2 cho phù hợp mật độ vùng mới, không phải chỉnh tham số gate.
