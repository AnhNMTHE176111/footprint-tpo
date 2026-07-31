# RESULTS_KB2_ZONES — neo KB2 vào "VÙNG CANH" của M30SessionZones v2

> Viết 2026-07-31. Câu hỏi của người học: KB2 (`QUAY_DAU`) hiện chỉ neo vào **VWAP** (n=27, EV +0.389,
> FAIL audit vì mỏng). `M30SessionZones` v2 đã lọc ra nhóm **VÙNG CANH** có chấm điểm (HVN tuần 70-95,
> HVN ngày 64-88, naked POC 72, cụm POC 78, băng giá trị 55) + gộp hợp lưu đa khung. **Neo reversal vào
> các vùng đó thì có tăng số lệnh mà vẫn giữ EV không?**
>
> Script: [`kb2_zones.py`](kb2_zones.py). Mọi số dưới đây là output thật của
> `python3 quantower-entry-signal/research/wyckoff/kb2_zones.py` — không có số nào gõ tay.
> Dùng lại nguyên hàm của [`verify_zones_v2.py`](../../../quantower-tpo-suite/verify_zones_v2.py)
> (port 1-1 từ C#) và [`imp_reversal_sweep.py`](../imp_reversal_sweep.py) (replicator KB2 đúng).
> Mốc so: [BASELINE.md](BASELINE.md). Kỷ luật: [AUDIT_V7.md](AUDIT_V7.md).

**Kết luận 1 câu:** **Số lệnh tăng thật (27 → 65, ×2.4), nhưng EV sụp từ +0.389 về ≈0 và tổng R
giảm (+10.5R → −2.5R) — và đối chứng ngẫu nhiên bác bỏ toàn bộ: vùng thật KHÔNG hơn vùng bị dịch
ngẫu nhiên.** Không ship gì vào KB2.

---

## 0. GOLDEN OK

```
KB2 baseline (imp_reversal_sweep)  n= 27 closed= 27 WR  56% EV +0.389 net  +10.5R ALL+  [05:+2R(2/3)  06:+2R(5/10)  07:+6R(8/14)]
KB2 qua detect_zone(mode=vwap)     n= 27 closed= 27 WR  56% EV +0.389 net  +10.5R ALL+  [05:+2R(2/3)  06:+2R(5/10)  07:+6R(8/14)]
==> GOLDEN OK (trùng khớp từng lệnh: True)
```

`detect_zone()` là bản copy có chủ đích của `imp_reversal_sweep.detect()`, **chỉ thay mốc giá `vwap`
bằng `zone.center`**. Mọi gate khác (vol floor, warmup, râu 0.50, cpos ±0.05, body 0.30, VSA 1.8,
TrendOk 480 nến, SL buf 2t / cap 70t, cooldown 15, RR 1.5) giữ **y hệt hằng số LIVE của C#**.

## 1. Chuỗi vùng — tính CAUSAL

Vùng được chốt tại **mỗi lần đóng phiên** (chỉ dùng dữ liệu quá khứ tới hết phiên đó), rồi dùng suốt
phiên sau — đúng ngữ nghĩa "vùng canh của phiên" và không nhìn tương lai.

```
M1 bars=103857  2025-11-02 .. 2026-07-27     M30 bars=6665  phien=768
Chuoi vung CAUSAL: 764 lan chot     so vung/lan: ALL med=10  TOP5 med=5
phan bo loai vung (ALL): naked_poc=3117  hvn_week=1671  priorhl=997  hvn_day=981  va_edge=971
                         poc_cluster=181  value_band=138
```

Hai bộ vùng được đo song song: **ALL** = mọi vùng đã gộp (bỏ trần MaxZones + bỏ lọc tầm với, đo "phản
ứng tại vùng" thuần) và **TOP5** = đúng những gì indicator vẽ ra (lọc tầm với `3×ATR20` + trần 5 vùng).

## 2. Biến thể — cửa sổ 5-7/2026, RR 1.5

```
tag                                n=NNN closed WR   EV      net
Z1  zone-only ALL (mọi vùng)       n= 65 closed= 65 WR  38% EV -0.038 net   -2.5R  [05:-0R(3/8)  06:-0R(9/23)  07:-2R(13/34)]
Z1b zone-only, nhóm CHÍNH          n= 39 closed= 39 WR  36% EV -0.103 net   -4.0R  [05:-2R(1/4)  06:-4R(3/12)  07:+2R(10/23)]
Z1c zone-only, nhóm "NHIỄU"(va/hl) n= 26 closed= 26 WR  42% EV +0.058 net   +1.5R  [05:+1R(2/4)  06:+4R(6/11)  07:-4R(3/11)]
Z1d zone-only, điểm>=70            n= 44 closed= 44 WR  32% EV -0.205 net   -9.0R
Z1e zone-only, điểm>=85            n= 16 closed= 16 WR  31% EV -0.219 net   -3.5R
Z2  UNION vwap+zone(ALL)           n= 81 closed= 81 WR  40% EV -0.012 net   -1.0R
Z2b UNION vwap+zone(CHÍNH)         n= 58 closed= 58 WR  41% EV +0.034 net   +2.0R
Z2c UNION vwap+zone(điểm>=70)      n= 63 closed= 63 WR  38% EV -0.048 net   -3.0R
Z3  CẢ vwap VÀ zone (hợp lưu)      n= 11 closed= 11 WR  73% EV +0.818 net   +9.0R ALL+  [05:+2R(1/1)  06:+2R(2/3)  07:+6R(5/7)]
Z4  zone-only TOP5 (như chart)      n= 47 closed= 47 WR  38% EV -0.043 net   -2.0R
Z4b UNION vwap+TOP5                n= 67 closed= 67 WR  43% EV +0.082 net   +5.5R ALL+
```

**Trả lời trực tiếp câu hỏi:** có, số lệnh tăng — Z1 cho **×2.4** (27→65), Z2 cho **×3** (27→81).
Nhưng **không có biến thể nào giữ được EV**: cái tốt nhất còn dương và cả-3-tháng-dương là Z4b
(EV +0.082, +5.5R) — vẫn **thấp hơn baseline VWAP-only** cả về EV (+0.389) lẫn tổng R (+10.5R).

## 3. Phân hoạch — điểm quan trọng nhất: **thang điểm CHẠY NGƯỢC**

```
-- theo LOẠI vùng (Z1 zone-only ALL) --
   va_edge (VAH/VAL 1 phiên) n= 22 WR  41% EV +0.023 net   +0.5R
   naked_poc                 n= 16 WR  38% EV -0.062 net   -1.0R
   hvn_day                   n= 16 WR  25% EV -0.375 net   -6.0R
   hvn_week                  n=  7 WR  57% EV +0.429 net   +3.0R
   priorhl                   n=  4 WR  50% EV +0.250 net   +1.0R
-- theo ĐIỂM vùng --
   điểm<55                   n= 21 WR  52% EV +0.310 net   +6.5R
   điểm 70-85                n= 28 WR  32% EV -0.196 net   -5.5R
   điểm>=85                  n= 16 WR  31% EV -0.219 net   -3.5R
-- theo SỐ KHUNG hợp lưu --
   ×1 khung                  n= 47 WR  43% EV +0.064 net   +3.0R
   ×2 khung                  n= 14 WR  29% EV -0.286 net   -4.0R
   ×3 khung                  n=  4 WR  25% EV -0.375 net   -1.5R
-- theo PHÍA (SPEC §9 #1a, bắt buộc) --
   SHORT                     n= 37 WR  38% EV -0.054 net   -2.0R
   LONG                      n= 28 WR  39% EV -0.018 net   -0.5R
```

Giả thuyết của người học là "nhóm chính (HVN/POC/băng giá trị) sẽ tách được khỏi nhiễu VAH/VAL Á-Âu".
**Dữ liệu cho kết quả ngược hẳn:**

- Nhóm **CHÍNH** EV **−0.103**; nhóm bị coi là **NHIỄU** (`va_edge`/`priorhl`) EV **+0.058**.
- Điểm càng cao càng tệ: <55 → **+0.310**, 70-85 → **−0.196**, ≥85 → **−0.219** (đơn điệu giảm).
- Hợp lưu càng nhiều khung càng tệ: ×1 → **+0.064**, ×2 → **−0.286**, ×3 → **−0.375** (đơn điệu giảm).

**Đây là lần thứ hai, độc lập, thấy đúng hình mẫu này.** Header của
[`reversal_vwap.py`](../reversal_vwap.py) đã ghi từ 27/7 (trên 98 lệnh QUAY_DAU live, dùng bộ
confluence CŨ): `co_vung NGƯỢC: 0 zone=33%, 1=16%, 2=17%, 3=0%`. Hai phép đo khác nhau, hai bộ
vùng khác nhau, cùng một chiều nghịch.

**Cơ chế giải thích (khớp lý thuyết Market Profile):** HVN / POC / băng giá trị là vùng **CHẤP NHẬN
GIÁ** — nơi đã có nhiều giao dịch, giá vào đó thì đi ngang và bị hấp thụ rồi *tiếp tục*, chứ không bật
mạnh. Đảo chiều xảy ra ở **BIÊN** vùng giá trị (VAH/VAL) và ở LVN — nơi giá bị **từ chối**. Fade tại
HVN là fade sai chỗ về mặt cơ chế. Điều này giải thích tại sao `va_edge` (biên) lại là loại tốt nhất
và `hvn_day` là loại tệ nhất, dù thang điểm xếp ngược lại.

## 4. ⭐ ĐỐI CHỨNG NGẪU NHIÊN — phép kiểm bác bỏ tất cả

Bắt buộc phải có, vì [BACKTEST-ZONES-V2.md](../../../quantower-tpo-suite/BACKTEST-ZONES-V2.md) đã cho
thấy v2 không hơn ngẫu nhiên trên 26 ngày. Cách làm: dịch mỗi tâm vùng đi `±U(0.5,1.5)×3.0 giá`,
**giữ nguyên số lượng vùng và độ phân tán** — tức phá thông tin vị trí mà giữ mọi thứ khác. 5 seed.

```
Z1 zone-only ALL   THẬT: n= 65 EV=-0.038   NGẪU NHIÊN: n~50 EV=-0.053 (min -0.151 max +0.023)  chênh=+0.014
Z1b nhóm CHÍNH     THẬT: n= 39 EV=-0.103   NGẪU NHIÊN: n~33 EV=-0.054 (min -0.306 max +0.118)  chênh=-0.048
Z2 UNION ALL       THẬT: n= 81 EV=-0.012   NGẪU NHIÊN: n~67 EV=+0.078 (min +0.007 max +0.169)  chênh=-0.091
```

**Vùng thật không phân biệt được với vùng dịch ngẫu nhiên** — chênh +0.014 (nhiễu), và ở hai cấu hình
còn lại vùng **ngẫu nhiên còn tốt hơn** vùng thật. Kết luận bắt buộc: **vị trí của các VÙNG CANH
không mang thông tin cho lệnh quay đầu** trên cửa sổ này. Mọi con số dương ở mục 2-3 (kể cả +0.310
của "điểm<55") phải đọc là **nhiễu trong dải ngẫu nhiên**, không phải edge.

## 5. Còn Z3 (hợp lưu VWAP **VÀ** vùng) thì sao?

`n=11, WR 73%, EV +0.818, cả 3 tháng dương` — con số duy nhất trông hấp dẫn. **Không được dùng:**

1. **n=11** — dưới xa ngưỡng 25 của SPEC §5.9, và đã là chuẩn "KILL DỨT ĐIỂM" từng áp cho K2 (n=5).
2. Nó **giảm** số lệnh 27→11, tức đi ngược đúng mục tiêu người học đặt ra.
3. Nó là **kẻ sống sót của 11 cấu hình** thử trong chính lượt này, trên **cùng** cửa sổ 3 tháng mà KB2
   đã bị AUDIT_V7 §D kết luận là chết sau hiệu chỉnh đa phép thử (p 0.072 → >1).
4. Đối chứng ngẫu nhiên ở mục 4 đã bác bỏ tiền đề ("vị trí vùng mang thông tin") mà Z3 dựa vào.

## 6. Phán quyết & việc nên làm tiếp

| | |
|---|---|
| Có ship vùng vào KB2 không? | **KHÔNG** |
| KB2 sau lượt này | vẫn **FAIL** — không thay đổi, giữ `EnableReversal=false`, không cấp vốn |
| Giả thuyết "vùng chất lượng cao lọc được nhiễu VAH/VAL" | **BỊ BÁC BỎ** — chiều ngược lại, và cả hai chiều đều nằm trong dải ngẫu nhiên |

Việc đáng làm tiếp, theo thứ tự:

1. **Đừng sửa KB2 nữa bằng cửa sổ này.** Ba lần thử độc lập (K2 hợp lưu D-1, K1 ExtremeWin, và lượt
   này) đều KILL. Vấn đề không phải thiếu ý tưởng mà là **không có dữ liệu OOS** (AUDIT_V7 §F).
2. **Điểm ngược có giá trị cho chính indicator M30SessionZones**, không phải cho KB2: nếu HVN/POC là
   vùng *chấp nhận* thì nhãn "VÙNG CANH (canh lệnh ở đây)" đang **dạy sai cách dùng**. Hướng đúng:
   HVN = vùng **đi tiếp / mục tiêu chốt lời**; LVN + biên VA = vùng **canh đảo chiều**. Đây là giả
   thuyết mới, **chưa đo**, và phải đo có đối chứng ngẫu nhiên trước khi đổi nhãn.
3. Nếu muốn dùng vùng cho vào lệnh, thử ở nhánh **thuận xu hướng (KB1)** — chỗ HVN đóng vai
   "giá được chấp nhận rồi đi tiếp" đúng với cơ chế, chứ không phải ở nhánh fade.

## 7. Tái lập

```bash
python3 quantower-entry-signal/research/wyckoff/kb2_zones.py
```

Chạy ~4 phút. Không có tham số ngẫu nhiên nào ngoài `random.Random(1000+seed)` ở mục 4 (seed cố định).
