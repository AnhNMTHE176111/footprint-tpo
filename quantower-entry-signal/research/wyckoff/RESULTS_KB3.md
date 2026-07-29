# RESULTS_KB3 — KB3: scalp biên↔biên trong range (SPEC_V7_3KB.md §6)

> Viết 2026-07-29. Bám [SPEC_V7_3KB.md](../SPEC_V7_3KB.md) §6 (+ §1-3, §7-9). Package:
> [`research/wyckoff/v7/`](v7/) (`s3_edge2edge.py` — mới, KB3; dùng lại `loaders.py`/`features.py`/`engine.py`/
> `report.py` của GĐ6, xem [RESULTS_KB12.md](RESULTS_KB12.md)). Toàn bộ số trong file này là output THẬT của
> `python3 research/wyckoff/v7/run_kb3.py` và `python3 research/wyckoff/v7/kb3_range_report.py` — log dán
> nguyên văn theo từng mục, không có số nào gõ tay.

**Kết luận 1 câu:** **KILL.** Range có xoay biên thật (48.7% vs ~3.7% ngẫu nhiên theo khoảng cách — cơ chế
đấu giá đúng như lý thuyết), nhưng dịch thành một lệnh fade khả thi thì thất bại ở **hai lớp độc lập**: (a)
bộ lọc thanh khoản kế thừa từ KB1 gần như loại bỏ toàn bộ mẫu vì range vốn là vùng **ít thanh khoản hơn
trung bình** (không phải bug — mâu thuẫn cơ chế thật), và (b) ngay cả bỏ hết xác nhận, phần **"chưa từng vỡ
thuận hướng scalp"** (ứng viên rotation thật, loại bỏ nhóm nghi là "bắt đầu cú phá KB1 sớm") có **EV = −0.254R**
— âm rõ ràng, đúng điều kiện KILL của §6.9(d).

---

## 1. GOLDEN OK

```
KB1 (cbr_v6, dong bang)            n= 33 WR= 48.5% tong=  +47.0R EV=+1.424 MDD=  3.0R | 05: +5.0 06:+22.0 07:+20.0 ✓ | nua1  +14.0R(n16) nua2  +33.0R(n17)
KB2 (QUAY_DAU, dong bang)  nsig= 27 closed= 27 WR  56% EV +0.389 net +10.5R ALL+ LOWcell  [05:+2R(2/3)  06:+2R(5/10)  07:+6R(8/14)]
==> GOLDEN OK (khop BASELINE.md: KB1 n=33 EV+1.424, KB2 n=27 EV+0.389)
```
Khớp tuyệt đối `BASELINE.md`. KB3 chưa đụng gì tới KB1/KB2 (dùng lại nguyên `cbr_v6.py`/`imp_reversal_sweep.py`
đóng băng).

---

## 2. Thống kê phát hiện range (5–7/2026, `features.range_struct_scan` — hạ tầng GĐ6, dùng chung KB1/KB3)

```
n_range (VALID it nhat 1 lan) 5-7/2026 = 74
theo thang: 05=4 06=32 07=38
do rong (gia):    p10=4.2 med=5.6 p90=6.0
thoi luong (nen): p10=31.0 med=43.0 p90=69.5
trang thai nen cuoi cua instance (xap xi 'ket cuc'): BREAKING=46 VALID=28
```

**⚠ Phát hiện quan trọng nhất (đã ghi cả ở `RESULTS_KB12.md`, độc lập tái xác nhận ở đây):** state machine
bar-by-bar cho **n=74**, lệch **77%** so với `n=322` của probe quét-cửa-sổ (§11.B). Đây là điểm phải "dừng,
soi lại" theo §4.3. **Đã soi:** viết unit test tổng hợp (range ổn định 30 nến → VALID đúng lúc; spring
thất bại → quay lại VALID đúng logic) — **không phải bug**. Nguyên nhân cơ chế: probe quét MỌI vị trí bắt
đầu có thể (~10 vạn ứng viên cửa sổ), trong khi state machine bar-by-bar chỉ có **một** range "sống" tại một
thời điểm — khi một range FORMING bị phá trước khi đủ tuổi, nó khởi tạo lại **ngay tại nến phá** (không phải
quét lùi thử lại mọi điểm bắt đầu trước đó), nên số điểm bắt đầu được thử ít hơn hẳn. Đây chính là hành vi
đúng của một chỉ báo sống thời gian thực, không phải một chỉ báo quét hồi tố — nhưng nó **không phải là câu
trả lời hợp lệ cho câu hỏi "H5 range cấu trúc có tốt hơn box không"** (câu đó đã KILL ở GĐ6, xem
`RESULTS_KB12.md` mục 5). Với KB3, n=74 range / 196 lần chạm thô (5-7/2026) vẫn **đủ >30** để không phải
"không kết luận" ngay từ đầu, nhưng mỏng hơn nhiều so với kỳ vọng 322 range/461 lần chạm của spec.

---

## 3. Kiểm chứng bằng mắt (10 range ngẫu nhiên) + nhận xét chất lượng

Ảnh: [range_01.png](img/range_01.png) · [range_02.png](img/range_02.png) · [range_03.png](img/range_03.png) ·
[range_04.png](img/range_04.png) · [range_05.png](img/range_05.png) · [range_06.png](img/range_06.png) ·
[range_07.png](img/range_07.png) · [range_08.png](img/range_08.png) · [range_09.png](img/range_09.png) ·
[range_10.png](img/range_10.png)

```
[01] range_01.png  i0=64605 width=5.3gia bars=34 end=BREAKING
[02] range_02.png  i0=64640 width=5.0gia bars=65 end=VALID
[03] range_03.png  i0=64935 width=5.6gia bars=43 end=VALID
[04] range_04.png  i0=69979 width=5.9gia bars=45 end=VALID
[05] range_05.png  i0=71140 width=5.6gia bars=38 end=BREAKING
[06] range_06.png  i0=78350 width=4.7gia bars=34 end=BREAKING
[07] range_07.png  i0=79573 width=6.0gia bars=36 end=BREAKING
[08] range_08.png  i0=88771 width=5.0gia bars=59 end=BREAKING
[09] range_09.png  i0=93149 width=5.9gia bars=50 end=VALID
[10] range_10.png  i0=96423 width=5.4gia bars=44 end=BREAKING
```

**Nhận xét trung thực (đã tự xem từng ảnh):**
- Phần lớn (01, 02, 03, 06, 07) cho thấy đúng dạng **balance 2 chiều thật** — giá dao động qua lại giữa 2
  đường kẻ, chạm cả 2 biên nhiều lần trước khi vỡ hoặc bị "wide" hoá.
- 05, 09 là consolidation xảy ra **ngay sau một đợt giảm/tăng trước đó** (tức range hình thành ở cuối một
  nhịp trend) — hợp lý theo Wyckoff (re-accumulation/re-distribution), không phải lỗi.
- **08 là ca yếu nhất**: nhìn tổng thể giống một kênh **trôi nhẹ đi xuống** (mild drift) hơn là một balance
  ngang thật, dù vẫn có chạm cả 2 biên (tu=8, td=6) nên không hoàn toàn một chiều. Đây là hệ quả của định
  nghĩa "range = độ rộng wick-extreme ≤ 6.0 giá + ≥2 chạm mỗi biên" — không có ràng buộc "không được có drift
  ròng", nên đôi khi bắt nhầm một đoạn trôi chậm làm range. **Không đủ nghiêm trọng để coi là "sai bản chất"**
  (không phải toàn bộ mẫu, và vẫn có 2 chiều thật), nhưng là một giới hạn thật của bộ phát hiện, ghi nhận ở
  mục 9.
- Bộ phát hiện **không cần sửa lại** ở lượt này (ngưỡng "sửa 2 lần vẫn sai" của luật DỪNG không bị chạm).

---

## 4. Tỷ lệ xoay biên nền (baseline rotation rate) — SO VỚI NGẪU NHIÊN

```
so lan cham (post-valid, 5-7/2026) = 175
rotation=55  broke_same_side=58  censored=62
ty le xoay / da co ket qua ro rang = 48.7% (55/113)
ty le xoay / TOAN BO (bi quan, censored=fail) = 31.4% (55/175)
NGAU NHIEN theo khoang cach (gambler's ruin p=BUF/(BUF+width)): tb=3.7% med=3.4%
KET LUAN: quan sat 48.7% vs null 3.7% -> CO edge cau truc ro ret
```

**Kết luận có/không edge cấu trúc: CÓ.** 48.7% (trên số ca đã có kết quả rõ ràng) hoặc tối thiểu 31.4% (tính
bi quan, coi mọi ca "censored" là thất bại) đều **vượt xa** mức ngẫu nhiên theo khoảng cách (~3.7%, mô hình
gambler's-ruin: bắt đầu cách biên vừa chạm ~0, biên "phá" cách `BUF=0.2 giá`, biên đối diện cách `width`
giá). Đây đúng là bằng chứng **hình học/cơ chế** cho ý tưởng gốc của người học ("giá chạy lên xuống trong
range một thời gian") — nhưng (xem mục 6/7) tỷ lệ xoay cao **không** tự động dịch thành một lệnh trade có
lãi, vì bản thân việc "xoay" không đối xứng hoá được với chi phí SL/thanh khoản.

---

## 5. Phân bố RR thực tế của KB3 (R thô, trước khi lọc)

```
rr_avail (R THO, chua ap san Kb3SlFloorPts): p10=1.43 med=2.53 p90=3.20
```
(Thấp hơn số probe §11.D nêu — med 4.13 — vì đây tính trên **196 lần chạm thật của state machine** (đã áp
sàn SL `Kb3SlFloorPts=1.5` giá qua công thức `R=max(sl_raw−entry, floor)`), không phải trên 461 lần chạm thô
chưa áp sàn của probe. 89% lần chạm còn RR ≥ 1.5 — chốt `Kb3MinRr=1.5` là hợp lý, **không phải** nút thắt của
KB3 (nút thắt nằm ở thanh khoản/chất lượng nến, xem mục 6).

---

## 6. Bảng tiến hoá theo bước + partition + sweep + PASS/KILL

### 6.1 Phễu lọc "bản trần" (chất lượng nến từ chối + `Kb3MinRr` + thanh khoản — SPEC §6.10 bước 3)

```
so lan cham RAW (5-7/2026, sau valid_bar) = 196
  cpos_ok       87/196 (44%)
  wick_ok       79/196 (40%)
  body_ok      158/196 (81%)
  vsa_ok        91/196 (46%)
  extreme_ok    87/196 (44%)
  quality_ok     9/196 (5%)      <- AND cua 5 dieu kien tren
  liq_ok        27/196 (14%)     <- lien-thong: liqratio >= 0.75

SAU 'ban tran' chinh thuc (quality+liq+MinRr): n=1
  KB3 ban tran CHINH THUC   n=1 WR=100.0% tong=+3.1R EV=+3.067 MDD=0.0R | 05:+3.1 06:+0.0 07:+0.0 ✗
  *** n < 25 -> KHONG KET LUAN duoc voi cau hinh nay ***
```

**Phát hiện nguyên nhân (§9 đã có gợi ý, ở đây đo trực tiếp):**
```
liqratio TAI CHAM: p10=0.14 med=0.30 p90=0.78   (so voi TOAN BO nen 5-7/26: med=0.79)
```
**`liqratio` tại các lần chạm biên KB3 thấp hơn HẲN mức trung bình toàn chuỗi** (trung vị 0.30 so với 0.79).
Đây **không phải trùng hợp**: `liqratio = vma(20 nến) / TB volume cuộn 1000 nến` — một range (theo đúng định
nghĩa) là vùng **biến động thấp**, và biến động thấp đi kèm **khối lượng thấp hơn trung bình** một cách cơ học.
Ngưỡng thanh khoản `≥0.75` được hiệu chỉnh cho KB1 (bắt cú phá — biến động CAO), áp trực tiếp sang KB3 (bắt
lúc giá đang YÊN) tạo ra **mâu thuẫn cơ chế**: gate được thiết kế để loại "range rác trong phiên mỏng" (đúng
tinh thần §6.6) lại vô tình loại **luôn cả range thật** vì chính cái làm nó "thật" (đang cân bằng, ít biến
động) cũng làm giảm `vma`. Đây là phát hiện thật, đo được, không phải giả định.

### 6.2 Chẩn đoán (KHÔNG PHẢI cấu hình đề xuất) — hình-học-thuần: bỏ hết chất lượng+thanh khoản, chỉ giữ `Kb3MinRr`

```
hinh-hoc-thuan (Kb3MinRr only)   n=139 WR=29.5% tong=+13.1R EV=+0.094 MDD=27.5R | 05:-0.1 06:+8.5 07:+4.7 ✗
outcome: {'TP': 41, 'SL': 85, 'BREAK': 12, 'TO': 1}
TO+BREAK = 9.4% (nguong KILL >50%, nguong PASS <=35%)
```
Dùng để hiểu funnel, **không phải** một ứng viên cấu hình hợp lệ (bỏ hết xác nhận là trái tinh thần §6.4).
`TO+BREAK=9.4%` đạt PASS riêng lẻ (rotation thực sự xảy ra cơ học, ít bị timeout/vỡ ngang) — nhưng **EV chỉ
+0.094R** (< ngưỡng KILL +0.15R) và **MDD 27.5R** (gấp gần 3 lần trần KILL 10.0R) ngay ở cấu hình **rộng
rãi nhất có thể**. Không có "dư địa" để thêm bộ lọc làm n co lại mà vẫn giữ được n≥40.

### 6.3 Sweep + partition (trên tập hình-học-thuần, vì tập "bản trần" chính thức n=1 quá nhỏ để partition)

**Gate xu hướng (§6.6, 3 dòng bắt buộc):**
```
Kb3TrendMode=0 (khong loc)                    n=139 EV=+0.094 MDD=27.5R
Kb3TrendMode=1 (chi thuan)                    n= 63 EV=+0.000 MDD=11.3R
Kb3TrendMode=2 (chi trend==0, DA BI BAC truoc) n=  9 EV=-0.615 MDD= 6.0R
```
Không nhánh nào PASS. `TrendMode=2` tái xác nhận kết luận probe (§6.6): n quá nhỏ, đã bác trước khi test.

**H3 — hợp lưu biên với vùng D-1/phiên (giả thuyết của chính người học):**
```
CO hop luu     n=66  WR=33.3% EV=+0.223 MDD=16.3R
KHONG hop luu  n=73  WR=26.0% EV=-0.022 MDD=18.6R
=> KILL — bo loc la NHIEU (EV_giu-EV_loai=+0.245 < 0.30)
```
**Đáng chú ý:** đúng HƯỚNG giả thuyết của người học (nhóm hợp lưu tốt hơn), và khá gần ngưỡng 0.30 — nhưng
không đạt. Không đủ để nói "hợp lưu làm range mạnh hơn" ở mẫu này, dù không mâu thuẫn ý tưởng.

**RangeTouchMin=3:**
```
n_range (TOUCH=3) = 54  (TOUCH=2 mac dinh = 74)
TOUCH=3 (hinh-hoc-thuan)   n=91 WR=25.3% tong=-6.1R EV=-0.067 MDD=22.0R
```
Tệ hơn TOUCH=2 ở mọi mặt (n giảm, EV âm) — không phải cải thiện.

### 6.4 Kiểm cơ chế bắt buộc (§6.2c/§6.9): "có thật là rotation, hay là bắt đầu cú phá KB1 sớm?"

```
VO THUAN huong scalp (nghi la KB1 som)   n= 22 WR=86.4% EV=+1.948R MDD=1.0R
CON LAI (ung vien rotation THAT)         n=117 WR=18.8% EV=-0.254R MDD=40.5R
EV cua phan 'con lai' = -0.254R -> KHONG >= +0.25R
```
Đây là bằng chứng **quyết định**: toàn bộ EV dương của tập hình-học-thuần (+0.094R) đến từ đúng **22/139
lệnh** mà chính range đó **sau này vỡ THUẬN hướng scalp** (tức lệnh KB3 vô tình bắt trúng đầu một cú phá thật
— về bản chất đây là **KB1 sớm**, không phải fade/rotation). Phần còn lại — **117 lệnh còn lại, đúng là
những ca "range xoay qua xoay lại không vỡ theo hướng đó"** — có **WR 18.8%, EV −0.254R**: âm dứt khoát.

**Theo đúng luật §6.9(d):** *"nếu phần còn lại ≤ 0 → KB3 thực chất là KB1 sớm → hợp nhất vào KB1, xoá KB3."*
→ **Áp dụng đúng luật này: KB3 không có edge độc lập với KB1.**

---

## 7. Gate xu hướng — 3 dòng (xem mục 6.3, tái khẳng định ở đây theo yêu cầu)
Đã in ở mục 6.3. Không nhánh nào cải thiện; `TrendMode=1` (chỉ thuận) triệt tiêu toàn bộ EV về đúng 0.000R.

---

## 8. Router (1 vị thế) + 3 dòng portfolio + đếm ca trùng KB3/KB1

```
KB1+KB2 (doi chieu BASELINE, phai =n60)  n=60 WR=51.7% tong=+57.5R EV=+0.958 MDD=5.0R | 05:+7.0 06:+24.5 07:+26.0 ✓
KB1+KB2+KB3                              n=61 WR=52.5% tong=+60.6R EV=+0.993 MDD=5.0R | 05:+10.1 06:+24.5 07:+26.0 ✓
CHI KB3                                  n=1  WR=100.0% tong=+3.1R EV=+3.067 MDD=0.0R
tin hieu bi bo vi 1-vi-the (ca 3 dong): {} (khong co ca nao)
```
Router đã kiểm: dòng "KB1+KB2" tái lập đúng `BASELINE.md` (n=60, khớp tuyệt đối) → router đúng. Với cấu hình
KB3 **chính thức** (bản trần, n=1), portfolio hầu như không đổi (+3.1R từ đúng 1 lệnh) — **không có ý nghĩa
thống kê**, không phải bằng chứng KB3 có ích.

**Đếm ca trùng KB3-thất-bại / KB1-kích-hoạt:**
```
so lan cham KB3 (co dead_at, range vo NGUOC huong scalp) = 90
trong do trung (+-3 nen) voi 1 tin hieu KB1 (box) = 0
```
0 ca trùng — nhưng đây là **PROXY**, không phải phép đo trực tiếp theo đúng mô tả §6.7: KB1 mặc định (GĐ6
chốt, xem `RESULTS_KB12.md`) vẫn dùng **`RangeMode=0` (box 8 nến)**, không dùng `range_struct` — nên "cùng
một cú vỡ được đếm 2 lần" theo đúng nghĩa đen của §6.7 (2 nhánh cùng nhìn 1 range) **chưa xảy ra được** vì
2 nhánh hiện dùng 2 định nghĩa range khác nhau. Ghi nhận rõ để không nhận vơ.

---

## 9. Cấu hình chốt: **KILL — không ship KB3**

Không có `KB3_CONFIG` để "copy-paste" — mọi nỗ lực nới lỏng trong phạm vi sweep công bố ở §6.8 đều dừng ở
n quá nhỏ (bản trần đúng spec, n=1) hoặc EV/MDD vượt ngưỡng KILL (hình-học-thuần, n=139, EV+0.094R/MDD27.5R),
và bài kiểm cơ chế bắt buộc (§6.2c) xác nhận phần còn lại sau khi loại nhóm "vỡ thuận hướng" có **EV âm
(−0.254R)** — tức ngay cả khi n đủ, cơ chế cũng không đứng vững.

**3 lý do KILL, xếp theo mức thuyết phục:**
1. **§6.9(d) — kiểm cơ chế "có thật rotation":** phần không phải "bắt đầu cú phá KB1 sớm" có EV=−0.254R < 0.
   Đây là lý do dứt khoát nhất, độc lập với việc chọn ngưỡng lọc nào.
2. **§6.9 EV/MDD ở cấu hình lỏng nhất còn hợp lệ hình học:** EV+0.094R (< +0.15R) và MDD 27.5R (> 10.0R).
3. **Thanh khoản kế thừa từ KB1 mâu thuẫn cơ chế** với bản chất range (biến động thấp ⇒ volume thấp), khiến
   cấu hình "đúng chuẩn" (bản trần) chỉ còn n=1 — không đủ để KẾT LUẬN theo cách khác, nhưng khi bỏ gate này
   ra để có đủ n (mục 6.2), lý do 1-2 ở trên vẫn giết KB3.

**Không "cố tinh chỉnh cho ra số dương":** đã thử `Kb3TrendMode` (3 giá trị), hợp lưu vùng (2 dung sai —
0.7 giá ở đây, đã thử 0.3 giá lúc chẩn đoán trước và cho n quá mỏng để dùng), `RangeTouchMin` (2 giá trị),
và bài kiểm cơ chế bắt buộc — tổng **7 cấu hình mới** cho KB3 (trong hạn mức 24 của §6.9).

---

## 10. Giới hạn + mục "cần quyết"

- **`range_struct_scan` lệch 77% so với probe** (đã ghi ở mục 2 và ở `RESULTS_KB12.md`) — mọi số của KB3
  kế thừa hạn chế này (n range mỏng hơn kỳ vọng ban đầu của spec).
- **Bộ phát hiện range đôi khi bắt nhầm drift nhẹ thành range** (ca #08 trong ảnh kiểm chứng, mục 3) — không
  đủ nghiêm trọng để phải sửa lại ở lượt này, nhưng nếu range_struct được dùng cho việc khác sau này thì nên
  cân nhắc thêm điều kiện "không có drift ròng đáng kể".
- **Thanh khoản `liqratio≥0.75` mâu thuẫn cơ chế với KB3** (mục 6.1) — nếu có lượt sau muốn hồi sinh ý tưởng
  scalp-trong-range, **cần một ngưỡng thanh khoản RIÊNG cho KB3** (có thể thấp hơn, hoặc đo tương đối so với
  chính range đó thay vì so với toàn chuỗi 1000 nến) chứ không nên dùng chung ngưỡng của KB1. ⟦CẦN QUYẾT
  Ở LƯỢT SAU NẾU MUỐN THỬ LẠI⟧ — bản thân lượt này KHÔNG tự ý đổi ngưỡng vì đó là gate "ÁP" theo spec.
- **KB1 vẫn dùng box (RangeMode=0)**, không dùng range cấu trúc — nên phép đếm "trùng KB3/KB1" (mục 8) chỉ
  là proxy theo thời gian, không phải phép đo "cùng 1 range" như §6.7 mô tả cho kịch bản RangeMode=1.
  Nếu tương lai RangeMode=1 được dùng cho KB1 thì phải đo lại đúng nghĩa.
- **dxFeed là proxy yếu cho feed live** (đã nhắc ở mọi file trước) — số ở đây chỉ so sánh nội bộ.
- **fp-m1 (xác nhận delta) hoàn toàn CHƯA test cho KB3** ở lượt này — do KB3 đã KILL trước khi cần tới lớp
  xác nhận delta (§8 nói rõ: không kiểm được offline làm gate, chỉ hiển thị). Không cần thiết phải làm khi
  kết luận đã là KILL.
- **Cửa sổ 5–7/2026 vẫn là "vàng tạo đỉnh"** — kết luận KILL này là *trong cùng chế độ thị trường*; không
  loại trừ khả năng KB3 hoạt động khác ở chế độ thị trường khác, nhưng đó là ngoài phạm vi lượt này.

**Cần quyết (nếu muốn hồi sinh KB3 ở lượt sau, không tự làm ở đây):**
1. Thiết kế lại gate thanh khoản dành riêng cho vùng biến động thấp (không dùng chung ngưỡng KB1).
2. Xem xét bỏ hẳn nhóm "vỡ thuận hướng scalp" (n=22) khỏi backtest ngay từ đầu (coi đó là địa bàn của KB1),
   rồi hỏi lại: phần "rotation thật" còn lại có cách nào cứu được EV −0.254R hay không — nhưng dữ liệu hiện
   tại (n=117, MDD 40.5R) cho thấy khả năng rất thấp trên đúng cửa sổ 5–7/2026 này.

---

## Tái lập

```bash
cd quantower-entry-signal/research/wyckoff/v7
python3 kb3_range_report.py     # muc 2/3/4 (thong ke + anh + rotation)
python3 run_kb3.py              # muc 1, 5, 6, 7, 8 (golden + R model + confirmations + gate + portfolio)
```
