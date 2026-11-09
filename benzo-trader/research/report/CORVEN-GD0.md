# Benzo CORVEN — Giai đoạn 0 (khung + port dấu hiệu, chạy tới hết bước ② trên TRAIN)

> Opus, 2026-11-09, theo `plans/BENZO-CORVEN-plan.md`. **Chỉ TRAIN** (phiên ≤ 2026-09-15): file nến bị cắt tại
> bar_idx 51318 (2026-09-15 20:59 UTC) trước khi đưa vào bất kỳ máy nào; TEST chưa hề được chạy hay đọc.
> Chưa có R, chưa có lệnh — GĐ0 chỉ đếm thế/mốc và tần suất dấu hiệu.

## 1. Đã làm
| File | Việc |
|---|---|
| `research/of_signals.py` | port y chữ `StackedImbalanceCalc` (Detect/Locate/Classify/CheckEnd/Follow) + `ExhaustionLogic` (Detect/IsSwept); mới: nền_ô (`cell_value`, `CellBaseline`), bóng (`bubbles`, `bubble_in_place`), `delta_strong`, `delta_divergence`, `trap` |
| `tools/OfSignalsDump/` | console C# biên dịch thẳng 2 file nguồn sản phẩm (không sửa dòng nào), xuất stacked/kiệt sức từng nến |
| `research/parity_of_signals.py` → `report/PARITY-OF-SIGNALS.md` | đối chiếu Python ↔ C# từng dòng |
| `research/setup_corven.py` | nạp TRAIN, `Step2Machine` (RangeEngine import nguyên trạng) → thế A/B, 1c, 2a/2b/2c, ngoại lệ lần 2; ghi `report/_corven_gd0.json` + `report/_corven_gd0_the.csv` (mỗi thế 1 dòng, giờ UTC, để soi chart) |
| `research/test_of_signals.py` | 25 test (port SI-1…SI-8, E1…E14; nền_ô/bóng/delta/trap; parity C# trên dữ liệu thật) — **25 PASS** |
| `research/test_setup_corven.py` | 14 test (plan mục 4 phần GĐ0: ReEntry huỷ B, CloseThrough huỷ mốc, tuổi 31, cửa sổ W=3, chạy cả mạch = chạy phần đầu; 2a A/B, 1c, mốc stacked đã chạm trước, ngoại lệ lần 2) — **14 PASS** |

## 2. Parity Python ↔ C# — **KHỚP 100 %**
51.319 nến (toàn bộ TRAIN, > 12.000 nến plan yêu cầu), 3 cấu hình stacked (250 %/3/1 = plan, 250 %/4/5, 300 %/3/1)
+ kiệt sức mặc định: **97.606 dòng, 0 dòng chỉ một bên, 0 dòng khác giá trị** (Lo/Hi, số mức, tỷ lệ yếu nhất, volume,
vị trí, Weak, Follow Touch/CloseThrough 300 nến, loại/mức/volume kiệt sức, chuỗi tooltip, nến bị quét). Chi tiết:
`PARITY-OF-SIGNALS.md`. Build tool C#: 0 cảnh báo.

## 3. Tần suất dấu hiệu trên TRAIN (35 phiên dày, 47.622 nến) so với plan mục 0
| Đại lượng | Plan mục 0 | TRAIN đo | Ghi chú |
|---|---|---|---|
| mbr trung vị | 1,5 giá | 1,6 | khớp |
| biên độ nến p25/50/75/90 | 1,0/1,6/2,4/3,5 | 1,1/1,7/2,5/3,7 | khớp |
| thân/biên độ p25/50/75 | 0,27/0,50/0,74 | 0,27/0,50/0,74 | khớp |
| nến tăng (H−C)/biên độ p50/p75 | 0,20/0,39 | 0,19/0,38 | khớp |
| \|Δ\| ≥ 2× / 3× medΔ | 26 % / 14 % | 26,1 % / 14,6 % | khớp |
| ô lớn nhất / nền_ô ≥ 3× / ≥ 4× | 17 % / 10 % | 18,2 % / 10,9 % | 3 cách tính nền cho cùng số (17,3–17,6 % khi thêm sàn 10 hợp đồng) |
| ô p90 | 9 hợp đồng | 9 | khớp |
| bóng (3× và ≥ 10) buy / sell / bất kỳ | — | 10,1 / 10,6 / 17,5 % | |
| stacked 250 %/≥3 mức | **32 %** nến | **55,4 %** nến (buy 31,8 % · sell 32,9 %) | **lệch 1,7×** — giải thích dưới |
| stacked ≥ 4 mức | 16 % | 29,4 % (buy 15,5 · sell 15,8) | như trên |
| stacked đủ điều kiện ③d (Body, không Weak, đóng phía S của vùng) | — | 30,7 % (run 4: 16,5 %) | |
| kiệt sức đỉnh / đáy | ≈ 9 % mỗi phía | 12,0 % / 12,0 % | 1,33× (< 1,5×) |
| max_one_trade = 0 | 100 % | 100 % | khớp |
| max_delta = min_delta = delta | — | **100 %** | xem điểm Q1 |
| range sinh/ngày | 19–20 | 24,7/phiên CME = **20,1/ngày lịch** | MEASURE.md chia theo ngày lịch (39+39 ngày) ⇒ khớp |

**Giải thích lệch stacked 1,7×:** con số 32 %/16 % của plan là tỷ lệ **theo từng phía** (buy 31,8 %, sell 32,9 %); tính
"nến có ít nhất một vùng bất kỳ phía" thì là 55 %/29 % (≈ 1 − 0,68² — hai phía gần độc lập). Định nghĩa và mã giống
hệt (parity 100 %), chỉ khác mẫu số. Hệ quả cho ③d: dấu hiệu chỉ tính vùng **phía S**, nên tỷ lệ thật mỗi hướng ≈ 32 %
(trước lọc vị trí) — đúng như plan dự tính; nhưng cho **mốc stacked** của thế B thì độ phổ biến này làm mốc gần như
luôn có (mục 4).

## 4. Bước ①–② trên TRAIN (bộ mặc định: gần 1,0 mbr · W=3 · tuổi 30 · 250 %/3/1)
| | Thế A (FailBreak) | Thế B (BreakConfirmed) |
|---|---|---|
| sự kiện engine | 1.681 FailBreak (bỏ 38 ca "whipsaw" trên toàn TRAIN — đóng lại xuyên luôn cạnh đối diện) | 1.727 BreakConfirmed (bỏ **326 = 19 %** làm range DEAD ngay vì hết lượt ReEntry — Q4) |
| số thế | **1.648 = 47,1/ngày** (min 26 · trung vị 49 · max 67) | **1.401 = 40,0/ngày** (min 30 · trung vị 41 · max 55) |
| qua ② (≥ 1 CF ứng viên) | **1.489 = 42,5/ngày (90,4 %)** | **1.353 = 38,7/ngày (96,6 %)** |
| bị loại 2a | 159 (9,6 %) — mọi CF ứng viên đóng xa > 1 mbr | 48 (3,4 %): 23 không test dải cạnh, 25 test nhưng đóng xa |
| bị loại 2b | (thế A: CF luôn đóng trong range theo định nghĩa) | 43 thế chết vì ReEntry trước khi qua ②; trong 12.694 vùng stacked ứng viên mốc, 6.742 bị loại vì đóng xuyên |
| mốc dùng | cạnh | cạnh 745 thế · stacked 1.179 thế · **chỉ nhờ stacked 608 thế** |
| CF ứng viên qua ② (theo nến) | 2.528 / 3.343 nến ứng viên | 10.035 / 16.285 nến được xét (≈ 287/ngày) |
| 1c (cấu trúc gãy ngược) | — | 722 thế bị tạm huỷ ≥ 1 lần; 5.294 nến-thế bị chặn |
- Kết thúc thế B: hết tuổi 531 · ReEntry 860 · hết phiên 9 · cuối file 1. Luật "không vắt qua phiên" gần như không
  có tác dụng (bỏ luật: A 1.648, B 1.401 như cũ).
- Theo nến thế B: 12.521 nến không chạm dải cạnh, 1.962 chạm nhưng đóng xa; trong số không qua: 355 không có vùng stacked
  nào, 3.204 vùng không chạm trong cửa sổ, 1.673 vùng đã bị chạm trước nhịp test, 1.018 vùng đã đóng xuyên.
- Độ nhạy "gần" (chỉ đếm thế, chưa có R): 0,5 mbr → A qua 1.198 (73 %), B 1.301 (93 %); 1,5 mbr → A 1.601 (97 %), B 1.363 (97 %).
- Ngoại lệ "xác nhận lần 2" (chỉ điều kiện giá, chưa đòi ≥ 2 dấu hiệu): **875 ứng viên = 25/ngày** — rất lỏng (Q12).
- Dấu hiệu theo ngữ cảnh trên 2.528 CF thế A qua ② (chỉ tần suất, chưa đếm ③): Δ ngược giá 631 (25 %), trap 75 (3 %).

**Nhận xét chính:** ② gần như **không lọc** — 90 % thế A và 97 % thế B qua. Lý do: thế A sinh ra từ fail break vốn đã
đóng sát cạnh (khoảng cách CF đầu trung vị 0,35 mbr); thế B có 27 nến để chờ test và mốc stacked xuất hiện ở hầu hết cú
phá (stacked mỗi phía ~32 % nến). Toàn bộ sức lọc sẽ dồn vào ③ (≥ 2 dấu hiệu) và ④ (CF, R ≥ 1,7).

## 5. Điểm spec mơ hồ / sai với dữ liệu — CẦN FABLE QUYẾT (đang chạy theo lựa chọn in đậm)
1. **Q1 — "Δ thẳng" không đo được trên lịch sử.** Trong `_bars.csv`, `max_delta = min_delta = delta` ở 100 % nến TRAIN
   (chỉ nến live cuối file khác) ⇒ điều kiện `delta ≥ 0,8 × max_delta` **luôn đúng** khi backtest, còn live (Volume
   Analysis có intrabar thật) sẽ lọc ⇒ Python/C# lệch nhau ở live và R đo được không đại diện. Chọn: bỏ "thẳng"? sửa
   Footprint Export ghi intrabar thật rồi xuất lại? **Đang: giữ công thức (no-op ở lịch sử).**
2. **Q2 — Tỷ lệ stacked 32 % là theo từng phía**, bất kỳ phía 55 % (mục 3). Ngưỡng "> 50 % số lệnh thì nâng run 4" vẫn
   dùng được, chỉ cần sửa câu ở mục 0.
3. **Q3 — ③d tự mâu thuẫn:** "Body **hoặc râu phía S** mà nến đóng phía S của vùng, Weak == false". Vùng ở râu phía S
   (buy ở râu trên) theo `StackedImbalance.Classify` **luôn** Weak, và điểm giữa vùng nằm trên thân nên không thể đóng ≥ Hi
   ⇒ nhánh râu không bao giờ xảy ra; thực chất ③d = **Body + đóng phía S của vùng**. Nếu ý là "ở đỉnh cũng được nếu các nến
   SAU giá đi tiếp" (0:03:40) thì cần luật khác (vd nến kế đóng vượt Hi). Tương tự ② mốc stacked cho phép "râu phía đẩy" =
   đúng các vùng Weak. **Đang: ③d = Body, không Weak, đóng phía S (cả Body cũng đòi đóng phía S); mốc = Body hoặc râu phía đẩy.**
4. **Q4 — BreakConfirmed làm range DEAD ngay** (lần phá thật thứ 3, MaxReEntry=2): 326/1.727 (19 %). Plan đòi "range
   BROKEN" ⇒ **đang KHÔNG lập thế B** (`CP.b_include_exhausted=False`); nếu tính: 1.727 thế, 1.671 qua ②.
5. **Q5 — Mốc stacked không có điều kiện khoảng cách CF.** Plan chỉ đòi râu trong cửa sổ chạm [Lo−tol, Hi+tol]; mốc cạnh
   thì đòi thêm CF đóng ≤ 1 mbr. Hậu quả: 608 thế B qua ② chỉ nhờ stacked. Có thêm "CF đóng ≤ gần × mbr từ mép gần của
   vùng" không? **Đang: theo chữ (không đòi).**
6. **Q6 — "Chưa từng bị chạm":** trước cửa sổ dùng chạm ĐÚNG vùng [Lo, Hi] (như `SiEndMode.Touch`), trong cửa sổ dùng
   [Lo−tol, Hi+tol] (như plan). Hai thước khác nhau — **đang theo chữ**.
7. **Q7 — tol:** cạnh range dùng `r.tol` của Range Box (chốt lúc sinh range); vùng stacked dùng tol hiện tại
   max(2 tick, 0,5 mbr). **Đang vậy.**
8. **Q8 — "Stacked hình thành SAU nến đóng ngoài":** ví dụ 2 nói vùng "trong cú phá" ⇒ **đang tính cả nến đóng ngoài**
   (bar ≥ ref). Cửa sổ test thế B không chứa nến đóng ngoài (chỉ ảnh hưởng W=4).
9. **Q9 — Δ ngược giá cần định nghĩa máy móc "nhịp 2–8 nến"** (plan chưa nói cách tìm điểm đầu nhịp). **Đang (Opus):**
   nến neo x = cực trị nhịp và râu x tới mốc (sell: H[x] ≥ cạnh − tol); điểm xuất phát s = đáy thấp nhất (sell) trong
   [x−8, x−2]; nhịp = s+1…x; biên độ L[s]→H[x] ≥ 1 mbr; ΣΔ(s+1…x) ≤ 0 (sell). Tần suất trên CF thế A: 25 %.
10. **Q10 — Trap (③e) không có sàn 10 hợp đồng** như bóng (③b), chỉ 3× nền_ô. **Đang theo chữ.**
11. **Q11 — nền_ô:** plan (trung vị của trung vị-top-3 mỗi nến) và kiểu OrderFlowBubbles (gộp side-volume của top-3 ô theo
    tổng volume) cho cùng tỷ lệ bóng (17,3–17,6 %). **Đang: cách plan, tính TRƯỚC nến hiện tại** (như OFB "baseline trước
    bar") — mbr và medΔ thì GỒM nến hiện tại (như Range Box / kernel).
12. **Q12 — Ngoại lệ "xác nhận lần 2" quá lỏng về giá:** viết như plan (râu quét cực trị cú thủng ≥ 1 tick, đóng lùi
    ≥ tol, vẫn ngoài range) ⇒ 25 ứng viên/ngày; plan không đòi có "lần 1" thất bại trước đó. ≥ 2 dấu hiệu (GĐ1) sẽ lọc,
    nhưng nên chốt có cần lần 1 (vd một CF/ứng viên trước đó bị loại) không.
13. **Q13 — FailBreak "whipsaw"** (đóng lại xuyên luôn cạnh đối diện, engine phát FailBreak + CloseOutside cùng nến):
    range không về ACTIVE ⇒ **đang không lập thế A** (38 ca).
14. **Q14 — Số phiên:** bỏ 4 phiên thưa đầu file ⇒ TRAIN = **35 phiên dày** (47.622 nến), không phải ≈ 40; TEST sẽ là 26.
    Plan mục 0 ghi "62 phiên dày, 82.390 nến" — đếm của tôi là 61 phiên dày (82.636 nến cả file); chênh nhỏ, không ảnh hưởng.
15. **Q15 — 1c:** chọn pivot ngược hướng D **gần nhất sau nến đóng ngoài và sau lần gãy trước**; tạm huỷ tới khi giá lập
    cực trị mới theo D (vượt cực trị cú đẩy tính tới lúc đó). 25 % nến-thế B bị chặn bởi luật này.

## 6. Tái lập
```bash
cd benzo-trader/research
PYTHONIOENCODING=utf-8 python parity_of_signals.py        # build + chạy C#, so 100 %  (~15 s)
PYTHONIOENCODING=utf-8 python setup_corven.py             # GĐ0 trên TRAIN → report/_corven_gd0.json, _corven_gd0_the.csv (~20 s)
PYTHONIOENCODING=utf-8 python -m pytest test_of_signals.py test_setup_corven.py -q   # 39 PASS
```
*Dừng theo plan — chờ Fable review trước GĐ1.*
