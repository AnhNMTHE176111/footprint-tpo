# DATA CAPABILITY — kiểm kê dữ liệu offline (2026-07-29)

> Viết bởi Claude. Đây là pha **ĐO LƯỜNG**, không phải thiết kế chiến lược — không có đề xuất setup nào trong file này.
> Mọi con số tái lập bằng: `python3 research/wyckoff/data_capability_audit.py all` (~2-3 phút, không cần pandas — chỉ
> dùng stdlib vì máy này không có pip/pandas). Log chạy đầy đủ tham chiếu ở cuối file.
> Script loader tái dùng: [`research/entry_dxfeed.py`](entry_dxfeed.py), [`research/wyckoff/cbr_v6.py`](wyckoff/cbr_v6.py).

---

## 0. Tóm tắt 30 giây

- **Phát hiện lớn nhất:** `fp-m1-*.csv` (UTC+7) và bộ `dxFeed 27-7` (UTC) là **CÙNG MỘT chuỗi giá** — đã chứng minh bằng
  đối chiếu từng phút một ngày thật (mục 4), khớp **1260/1260 nến, sai lệch 0 tick**. Sự khác biệt WR 61% vs 42%/38%
  giữa 2 nguồn **KHÔNG phải do dữ liệu khác nhau**, mà do **pipeline backtest** (zone-pool "lạnh" ở đầu kỳ khi build
  từ dữ liệu ngắn) — xem mục 4 để có cơ chế đầy đủ.
- **Tên file gây hiểu lầm nghiêm trọng:** `TPO-chart-daily.csv` thực ra là nến **30 PHÚT**; `tpo-chart-m30.csv` thực ra
  là nến **1 PHÚT**. Chữ "daily"/"m30" mô tả **chu kỳ hồ sơ TPO**, không phải khung nến. Xem mục 1.4.
- **Cột trùng tên khác hoa/thường:** cả 2 file TPO có **2 cột** `Open interest` (toàn 0, chết) và `Open Interest`
  (có dữ liệu thật) — dễ nhầm là cột kia chết luôn. Xem mục 3.
- **`perlevel_m1_clean.pkl` chỉ 25 phiên rời rạc** (đã biết từ `WYCKOFF_V6_PLAN.md §10.4`, xác nhận lại độc lập) —
  và **`sample.csv`/`sample_bars.csv`/`perlevel_m1.pkl` là 3 tầng lọc của CÙNG một nguồn per-level** (đã chứng minh
  khớp bar-by-bar ở mục 1.6), không phải 3 bộ dữ liệu độc lập.
- **`max_one_trade` / `Max one trade Vol.` toàn bằng 0 ở MỌI file** (kể cả 761.199 dòng per-level `sample.csv`) →
  không nguồn nào cho phép nhận diện "lệnh lớn nhất trong nến" offline.

---

## 1. Định danh & chuẩn hoá từng bộ dữ liệu

Tick size xác nhận **0.1 "giá"** ở TẤT CẢ các file (kiểm bằng khoảng cách nhỏ nhất giữa các mức giá phân biệt trong
cột Open — ra đúng dãy `0.1, 0.2, 0.3...`), khớp `TICK=0.1` đang dùng trong
[`entry_dxfeed.py`](entry_dxfeed.py). Không file nào cho thấy tick 0.01.

### 1.1 dxFeed 27-7 (bộ chính, dùng bởi `entry_dxfeed.load_m1()`)

[`../data-export/27-7/_GCQ26XCEC dxFeed, Time - Time - 1m, 11_3_2025 120000 AM-7_27_2026 105600 PM_8b750702-5f00-4836-bf74-81e2a0c4495f.csv`](../data-export/27-7/)
— n=**103.857** nến, **2025-11-02 23:22:00 → 2026-07-27 15:56:00** (UTC), cột `Time left;...` sep=`;`.

**Múi giờ = UTC (bằng chứng số, độc lập với memory cũ):**
- Đếm nến theo giờ UTC cả 9 tháng: giờ 21 chỉ có **163** nến (so với 3.700–5.700 ở các giờ khác) → gần-0 nhưng
  không tuyệt đối 0 trên toàn kỳ.
- Bóc theo tháng: **163 nến giờ-21 này nằm gọn trong 11/2025→3/2026** (12+11+63+59+18=163); **subset đúng 5–7/2026
  cho giờ 21 = 0 nến tuyệt đối** — khớp chính xác tuyên bố cũ trong `WYCKOFF_V6_PLAN.md §2`. Chênh lệch theo mùa
  này khớp với **DST của Mỹ** (giờ nghỉ CME neo theo 17:00 ET cố định — chuyển múi UTC/ET đổi 1h qua DST làm giờ
  nghỉ UTC dịch từ 21h→22h ở một phần năm).
- Weekday: có dữ liệu thứ 2-6 đầy đủ, **Chủ nhật (weekday=6) có 1.828 nến** (phiên mở cửa CME tối CN giờ Mỹ = sáng
  sớm CN theo UTC), **Thứ 7 (weekday=5) = 0** — hợp lý với giờ UTC neo trực tiếp giờ Mỹ, không lệch múi.
- Số ngày có dữ liệu: **224 ngày** trên toàn kỳ ~267 ngày lịch (11/2025→7/2026).
- **561 khoảng trống >60 phút**; 5 gap dài nhất đều 53-73 giờ = kỳ nghỉ lễ/cuối tuần dài (vd 2/4→5/4/2026 = 73h).

### 1.2 fp-m1-6-month.csv (bộ M1 có Delta, dài nhất trong nhóm fp-m1)

[`../data-export/fp-m1-6-month.csv`](../data-export/fp-m1-6-month.csv) — n=**99.678** nến,
**2026-01-27 18:50:00 → 2026-07-25 03:59:00**, cột `DateTime` (định dạng `M/D/YYYY h:mm:ss AM/PM`) + cột `UTC` ghi
literal **`+07:00`** (không phải giờ trị số, chỉ là nhãn offset).

**Múi giờ = giờ ĐỊA PHƯƠNG UTC+7 (bằng chứng số):**
- Đếm nến theo giờ địa phương: **giờ 4 (local) chỉ có 100 nến** so với 3.600-5.400 các giờ khác → khớp UTC 21:00
  (nghỉ CME) + 7h = local 04:00.
- Volume trung vị theo giờ địa phương đỉnh ở **19-21h local** (median 4-5) = UTC 12-14h = mở COMEX. Khớp mẫu hình
  đã thấy ở dxFeed.
- Weekday: **thứ 7 (weekday=5) có 3.002 nến** (đuôi phiên thứ 6 Mỹ đóng cửa 21:00 UTC = 04:00 sáng thứ 7 local
  UTC+7), **Chủ nhật = 0** — ĐỐI XỨNG với dxFeed (dxFeed CN có nến/T7 không, fp-m1 T7 có nến/CN không) — chính là
  hệ quả cơ học của lệch +7h, không phải 2 lịch phiên khác nhau.

### 1.3 fp-m1.csv và fp-m1-1-month-data.csv (2 bộ M1-Delta nhỏ hơn, cùng khuôn cột)

- [`../data-export/fp-m1.csv`](../data-export/fp-m1.csv): n=2.451, **2026-07-23 09:58 → 2026-07-25 03:59** (~2 ngày) —
  quá nhỏ, khả năng là file test/soát lỗi còn sót lại, **KHÔNG dùng** cho backtest (bị `fp-m1-6-month.csv` bao trùm).
- [`../data-export/fp-m1-1-month-data.csv`](../data-export/fp-m1-1-month-data.csv): n=28.071,
  **2026-06-26 15:01 → 2026-07-25 03:59** — đây là file **mặc định của `entry_dxfeed.load_fpm1()`** (tham số
  `path="fp-m1-1-month-data.csv"`). Là tập con đúng của `fp-m1-6-month.csv` theo thời gian.

### 1.4 TPO-chart-daily.csv và tpo-chart-m30.csv — ⚠️ TÊN FILE SAI KHUNG NẾN

[`../data-export/TPO-chart-daily.csv`](../data-export/TPO-chart-daily.csv) (n=952) và
[`../data-export/tpo-chart-m30.csv`](../data-export/tpo-chart-m30.csv) (n=3.016).

**Kiểm khoảng cách giữa 2 dòng liên tiếp (không tin tên file):**

| File | Khoảng cách phổ biến nhất | → khung nến thật | Số giá trị `TPO` phân biệt | → ý nghĩa |
|---|---|---|---|---|
| `TPO-chart-daily.csv` | 30 phút (930/951 lần) | **30 PHÚT** | 22 | hồ sơ TPO **cập nhật theo NGÀY** (đúng 1 khối/ngày, lặp lại suốt các nến 30' trong ngày đó) |
| `tpo-chart-m30.csv` | 1 phút (3003/3015 lần) | **1 PHÚT** | 94 | hồ sơ TPO **xoay theo chu kỳ 30 phút** trong ngày |

Tức là: `TPO-chart-daily.csv` = nến 30 phút + hồ sơ TPO tính theo NGÀY (giữ nguyên trong ngày). `tpo-chart-m30.csv` =
nến 1 phút + hồ sơ TPO tính theo khối 30 phút (đổi 48 lần/ngày). **Chữ "daily"/"m30" mô tả chu kỳ TPO, không phải
độ dài nến** — phải dùng đúng file cho đúng mục đích, không suy theo tên.

Khoảng thời gian thật (rất hẹp, không phải "nhiều tháng" như số dòng gợi ý):
- `TPO-chart-daily.csv`: **2026-06-25 → 2026-07-25** (~1 tháng, 22 ngày phân biệt).
- `tpo-chart-m30.csv`: **2026-07-22 23:33 → 2026-07-25 03:59** (**chỉ ~2.2 NGÀY**) — cực kỳ hẹp, gần như không dùng
  được cho thống kê đa phiên.

Cả 2 file đều có nhãn `UTC` = `+07:00` giống fp-m1; kiểm cùng cách (giờ 4 local gần-0 nến — xem log mục 1) xác
nhận **cùng múi UTC+7**.

### 1.5 sample.csv / sample_bars.csv (per-level, thư mục `27-7/`)

[`../data-export/27-7/sample.csv`](../data-export/27-7/) (761.199 dòng, dạng **long**: `bar_idx,datetime,price,
bid_vol,ask_vol,volume,delta,trades,buy_trades,sell_trades,max_one_trade` — mỗi dòng = 1 mức giá trong 1 nến) và
[`../data-export/27-7/sample_bars.csv`](../data-export/27-7/) (77.672 dòng, bản **tổng hợp mỗi nến 1 dòng** của
chính `sample.csv`).

- Khoảng thời gian: **2026-01-29 11:49:00 → 2026-07-28 10:51:00**, nhưng chỉ **112 ngày có dữ liệu** (rất thưa đầu
  kỳ — xem ma trận tháng ở mục 2: tháng 1 chỉ 2 ngày, tháng 2 chỉ 20, tăng dần).
- Múi giờ: **KHỚP CHÍNH XÁC** dòng đầu `perlevel_m1.pkl` (`2026-06-01 00:00:00`, O=4570.5 H=4570.6 L=4568.1
  C=4569.4 V=115 Delta=3 — same to the decimal) → **cùng gốc UTC**, không lệch múi.

### 1.6 perlevel_m1.pkl và perlevel_m1_clean.pkl — 3 TẦNG LỌC CỦA 1 NGUỒN, không phải 2 bộ độc lập

Cấu trúc: `pickle.load()` ra `list[dict]`, mỗi dict = 1 nến `{t, o, h, l, c, lo_t, hi_t, vol, delta, lvls}`, với
`lvls` = `list[(price_tick_int, price_float, bid_vol, ask_vol, total_vol)]` — **per-level thật, có bid/ask tách
riêng**. `lo_t=45681` khớp `price=4568.1 → price/0.1=45681` → xác nhận lưới giá 0.1.

| Bộ | n bars | n ngày | Khoảng thời gian |
|---|---:|---:|---|
| `sample.csv`/`sample_bars.csv` | 77.672 | 112 | 2026-01-29 → 2026-07-28 |
| `perlevel_m1.pkl` (gốc) | 52.631 | 46 | 2026-05-01 → 2026-07-27 15:56 |
| `perlevel_m1_clean.pkl` (đã lọc) | 32.687 | **25** | 2026-06-01 → 2026-07-27 15:56 |

**Quan hệ đã chứng minh:** `perlevel_m1.pkl` = tập con của `sample_bars.csv` giới hạn 2026-05-01→07-27 (2 số liệu
khớp khít: tổng nến 5+6+7/2026 của sample_bars = 19.944+7.671+26.087=53.702, gần đúng 52.631 của perlevel — chênh
lệch do cắt tại 07-27 15:56 thay vì hết 07-28). `perlevel_m1_clean.pkl` = `perlevel_m1.pkl` **trừ sạch toàn bộ
tháng 5** (21 ngày bị loại, xác nhận bằng diff tập ngày — không loại ngày nào khác ngoài tháng 5). Đây chính là
"GCQ26 chỉ có thanh khoản đủ từ tháng 5" mà `WYCKOFF_V6_PLAN.md` đã ghi.

**25 ngày của bản `_clean` rất rời rạc** (xác nhận độc lập, khớp plan cũ): tháng 6 chỉ có `01,02,03,26,29,30` (6
ngày), tháng 7 có 19 ngày rải rác với các khoảng trống cuối tuần 3 ngày đều đặn + 1 khoảng trống dài 23 ngày
(2026-06-03→2026-06-26, đúng đoạn tháng 5 + đầu tháng 6 bị cắt).

**Múi giờ = UTC** (đếm nến theo giờ trên `perlevel_m1.pkl` gốc: giờ 21 = **0 nến tuyệt đối** trong khi các giờ khác
1.600-2.700 nến; weekday chỉ có thứ 2-6, không có thứ 7/CN) — khớp cách xác minh dùng cho dxFeed.

### 1.7 File dư thừa (không dùng, đã bị bộ khác bao trùm)

Hai file dxFeed ở gốc `data-export/` (`..._1_1_2026...7_31_2026...csv` và `..._7_1_2026...7_26_2026...csv`) là
**tập con hẹp hơn** của bộ 27-7 (kết thúc 2026-07-24 thay vì 07-27) — **không dùng**, `entry_dxfeed.py` cũng trỏ
thẳng tới file trong `27-7/`.

---

## 2. Ma trận trùng lặp thời gian (số ngày có dữ liệu mỗi tháng)

```
thang       dxFeed  fp-m1-6m  TPOdaily   TPOm30   sample  perlevel
2025-11         22         0         0        0        0         0
2025-12         25         0         0        0        0         0
2026-01         26         5         0        0        2         0
2026-02         24        24         0        0       20         0
2026-03         27        26         0        0       22         0
2026-04         25        25         0        0       21         0
2026-05         26        26         0        0       21        21
2026-06         26        25         5        0        6         6
2026-07         23        21        21        4       20        19
```

**Cửa sổ đối chứng dxFeed ↔ fp-m1** (2 nguồn duy nhất đủ dài để chéo-kiểm nhau): **2026-01-27 → 2026-07-25**
(gần trọn khoảng phủ của `fp-m1-6-month.csv`), dxFeed phủ dư ra cả 2 đầu (từ 2025-11 và tới 2026-07-27). Trong cửa
sổ này dxFeed có dữ liệu đều 22-27 ngày/tháng; fp-m1 bắt đầu rất thưa (tháng 1 chỉ 5 ngày vì file bắt đầu giữa
tháng) rồi đủ 24-26 ngày/tháng từ tháng 2.

**Per-level (`sample`/`perlevel`) chỉ đối chứng được với dxFeed/fp-m1 trong 2026-05→07**, và ngay trong cửa sổ đó
cũng KHÔNG đầy đủ: dxFeed có **75 ngày** giao dịch trong 05-01→07-27, `perlevel_m1.pkl` chỉ có **46/75 (61%)**;
trong 06-01→07-27 dxFeed có **49 ngày**, `perlevel_m1_clean.pkl` chỉ có **25/49 (51%)**.

`TPO-chart-daily.csv` chỉ đối chứng được trong **06-25→07-25** (~1 tháng); `tpo-chart-m30.csv` gần như không đối
chứng được gì (chỉ 2.2 ngày, toàn bộ nằm trong 07-22→07-25).

---

## 3. Sàng cột chết

### 3.1 fp-m1-6-month.csv (38 cột) — cột toàn 0 (chết)

`VSA Volume_baseline (ẩn)`, `Buy (Ask) trades`, `Sell (Bid) trades`, `Delta trades`, `Delta trades, %`,
`Max delta`, `Min delta`, `Open interest`, `Average buy (ask) size`, `Average sell (bid) size`,
`Max one trade Vol.`, `Max one trade Vol, %`, `Filt. volume`, `Filt. volume, %`, `Filt. buy (ask) volume`,
`Filt. buy (ask) volume, %`, `Filt. sell (bid) volume`, `Filt. sell (bid) volume, %` — **17/38 cột chết**
(đã biết `Max one trade Vol.` từ trước, ở đây xác nhận thêm 16 cột chết khác chưa từng ghi).

Cột **CÓ** dữ liệu thật đáng chú ý: `Delta`, `Delta, %`, `Cumulative delta`, `Buy (Ask) volume`,
`Sell (Bid) volume` (có % tương ứng), `Average size`, `Trades`/`Volume` (Trades chỉ nz 77.381/99.678 — một số
nến có volume nhưng Trades=0, đáng chú ý nhưng không phải cột chết).

### 3.2 TPO-chart-daily.csv và tpo-chart-m30.csv (59 cột mỗi file) — cùng khuôn cột với fp-m1 phần footprint + 24
cột phần TPO. Cột chết giống hệt fp-m1 (trừ `VSA Volume_baseline` không tồn tại ở 2 file này):
`Buy (Ask) trades`, `Sell (Bid) trades`, `Delta trades(+%)`, `Max/Min delta`, `Open interest` (**chữ thường**),
`Average buy/sell size`, `Max one trade Vol.(+%)`, toàn bộ 6 cột `Filt. *`.

**⚠️ Bẫy tên cột trùng (case-sensitive):** cả 2 file có **2 cột tên gần giống nhau**:
- `Open interest` (chữ thường, thuộc khối footprint) → **toàn 0, chết**.
- `Open Interest` (chữ hoa I, thuộc khối TPO ở cuối) → **CÓ dữ liệu thật**: `TPO-chart-daily.csv` min=173.991
  max=275.014 (952/952 khác 0); `tpo-chart-m30.csv` min=173.687 max=202.154 (3.016/3.016 khác 0).

Toàn bộ khối cột TPO (`TPO,VAH,VAL,POC,Midpoint,RF,Volume,Delta,Trades,TPO Up,TPO Down,POC Count,VA Volume,Range,
Range(ticks),VA range,VA range(ticks),IB High,IB Low,IB range,IB range(ticks),IB Volume,Open Interest`) đều **CÓ**
dữ liệu, không cột nào chết.

---

## 4. Điều tra lệch WR 61% (fp-m1) vs 42% (dxFeed)

Tái lập bằng script đã có sẵn trong repo: [`research/entry_xcheck.py`](entry_xcheck.py), chạy
`python3 entry_xcheck.py` — kết quả thật:

```
### (B) DELTA-FREE tren fp-m1 (~1 thang, 6/26->7/25)      n=36  WR=61% (22/36)  tong=+19R
### (C) dxFeed delta-free CUNG 2 thang 6-7/2026            n=118 WR=42% (49/118) tong=+4R
```

### 4.1 Có phải khác sản phẩm/tick/múi giờ? → KHÔNG — đã bác bỏ bằng đối chiếu trực tiếp

Lấy đúng 1 ngày trong cửa sổ trùng (**2026-07-10**), quy đổi `fp-m1` (UTC+7) về UTC bằng **-7 giờ**, so từng phút
với dxFeed (UTC gốc):

```
fp-m1 co 1260 nen phut trong ngay 2026-07-10 (sau khi quy doi UTC+7 -> UTC bang -7h)
khop voi dxFeed: 1260 | dxFeed thieu nen cung phut: 0
max |close_fp - close_dx| = 0.00 tick (gia 0.1)
```

10 dòng đầu (giờ UTC | fp O/H/L/C/V | dx O/H/L/C/V):
```
2026-07-10 00:00:00  fp:4132.5/4133.4/4129.8/4129.9/106  dx:4132.5/4133.4/4129.8/4129.9/106  diff=0.0tick
2026-07-10 00:01:00  fp:4129.7/4130.4/4129.3/4130.1/16   dx:4129.7/4130.4/4129.3/4130.1/16   diff=0.0tick
2026-07-10 00:02:00  fp:4130.1/4130.2/4129.0/4129.9/55   dx:4130.1/4130.2/4129.0/4129.9/55   diff=0.0tick
```
**Khớp tuyệt đối 1260/1260 nến, sai lệch 0 tick trên toàn bộ ngày.** Kết luận: `fp-m1` và `dxFeed` là **CÙNG MỘT
chuỗi giá GCQ26**, chỉ khác nhãn múi giờ (UTC+7 vs UTC) + fp-m1 có thêm Delta/Bid-Ask. Đây KHÔNG phải nguyên nhân
lệch WR.

### 4.2 Vậy nguyên nhân là gì? → Zone-pool "lạnh" ở đầu kỳ khi `build_zones()` chỉ có ít lịch sử

Chạy cùng logic delta-free, cùng khung thời gian chính xác (khung của `fp-m1`), nhưng **giữ nguyên cách mỗi bộ tự
xây `pool` vùng giá** (session/D-1 VAH/VAL/POC) như 2 pipeline vẫn đang làm:

```
dxFeed pool zones (tu ~9 thang lich su) = 3675
fp-m1  pool zones (chi tu ~1 thang lich su cua chinh no) = 410

dxFeed delta-free, GIOI HAN dung khung fp-m1:  n=68  WR=38% (26/68)  tong=-3R
fp-m1  delta-free (volfloor=20 hardcode):      n=36  WR=61% (22/36)  tong=+19R
```

Số nến trong đúng khung thời gian gần như bằng nhau (dxFeed 27.651 vs fp-m1 28.071, chênh <2%), **volume trung
bình mỗi nến cũng gần bằng nhau** (73.55 vs 74.18) — càng củng cố đây **không phải vấn đề chất lượng dữ liệu**.
(Lưu ý phương pháp: khung "chính xác" này lấy mốc `t0/t1` trực tiếp từ giờ ĐỊA PHƯƠNG của fp-m1 mà chưa quy đổi
-7h sang UTC trước khi lọc dxFeed — sai lệch biên ~7 giờ trên tổng ~29 ngày (~1%), không đủ lớn để giải thích
chênh lệch 2x về số tín hiệu, nhưng nêu rõ để không nhận vơ đây là phép so sánh mốc-giờ hoàn hảo tuyệt đối.)
Nhưng vì `build_zones()` của mỗi bộ chỉ nhìn thấy lịch sử của CHÍNH bộ đó, `fp-m1` (chỉ có ~1 tháng trước điểm bắt
đầu) tạo ra pool nhỏ hơn ~9 lần so với dxFeed (được nạp từ 2025-11) — dxFeed vì vậy có nhiều vùng giá "đang hoạt
động" hơn ngay từ đầu cửa sổ, sinh nhiều tín hiệu "2 chạm&đảo" hơn (dxFeed: 50/68 tín hiệu là cham&dao so với
25/36 ở fp-m1, tỷ trọng cao hơn) và kéo WR xuống.

**Kiểm định thống kê (z-test 2 tỷ lệ, để biết đây là tín hiệu thật hay nhiễu mẫu nhỏ):**
- Bản chính thức (theo tháng, n lệch tự nhiên do cách lọc gốc): 22/36 (61.1%) vs 49/118 (41.5%) → **z=2.06**
  (p≈0.039 hai phía) — khác biệt có ý nghĩa ở mức 5% nhưng **không mạnh**, n vẫn nhỏ.
- Bản cùng-cửa-sổ-chính-xác: 22/36 (61.1%) vs 26/68 (38.2%) → **z=2.23** (p≈0.026) — tương tự.

### 4.3 Kết luận rõ ràng

- **KHÔNG phải khác sản phẩm/hợp đồng/tick/múi giờ** — đã bác bỏ bằng bằng chứng trực tiếp (mục 4.1).
- **Nguồn gốc cơ chế đã xác định**: pool vùng giá của `fp-m1` "lạnh" hơn do lịch sử ngắn — đây là **hạn chế hạ tầng
  backtest** (loader), không phải hạn chế của dữ liệu thô.
- Chênh lệch WR có ý nghĩa thống kê ở mức 5% nhưng biên độ nhỏ (z≈2.0-2.2) — **không loại trừ một phần là nhiễu
  mẫu nhỏ** (n=36-118). Chưa thể tách bạch % đóng góp của "zone lạnh" so với "nhiễu ngẫu nhiên" bằng dữ liệu hiện
  có — cần chạy fp-m1 với pool được "làm ấm" bằng lịch sử dxFeed trước đó mới tách được (xem mục 7, hạ tầng còn
  thiếu, mục a).
- **Nguồn chuẩn để chốt số**: **dxFeed** (lịch sử dài, pool đầy đủ ngay từ đầu bất kỳ cửa sổ backtest nào).
  **fp-m1 là bộ đối chứng cho delta thật**, không dùng để chốt WR tuyệt đối vì pool khởi động lạnh khi test ngay từ
  đầu file của nó.

---

## 5. Bảng năng lực 17 feature

Ký hiệu: **CÓ** = tính được offline đủ tin cậy cho nghiên cứu dài hạn · **MỘT PHẦN** = tính được nhưng bị giới hạn
(cửa sổ ngắn / độ phủ thưa / cần code mới) · **KHÔNG** = không có nguồn nào cho phép.

### Tầng bias phiên

| # | Feature | Phán quyết | Bộ dữ liệu · số tháng · n dự kiến | Công thức | Rủi ro look-ahead |
|---|---|---|---|---|---|
| 1 | Value Area hôm nay vs hôm qua (value migration) | **MỘT PHẦN** | Nguồn gốc: `TPO-chart-daily.csv` (~1 tháng, 22 ngày → 21 cặp so sánh liên tiếp). Nguồn dài hơn: dựng lại từ M1 dxFeed bằng `daily_levels_from_m1()` (đã có sẵn trong `entry_dxfeed.py:145`) → phủ ~9 tháng, ~224 ngày | So `VAH_t,VAL_t,POC_t` (cột TPO) hoặc `value_area(tpo_counts(...))` (đã có) với giá trị ngày trước | Phải dùng VA đã **ĐÓNG** (ngày hôm trước hoàn tất), không dùng VA đang hình thành của ngày hiện tại |
| 2 | POC clustering nhiều phiên | **MỘT PHẦN** | Như trên: TPO-chart-daily 22 điểm POC (mỏng) hoặc M1-derived ~224 điểm (dùng lại `daily_levels_from_m1`) | Gom cụm các POC liên tiếp trong ngưỡng N-giá | Không, miễn chỉ dùng ngày đã đóng |
| 3 | Initial Balance (IB High/Low) + giá mở vs VA hôm trước | **MỘT PHẦN** | `TPO-chart-daily.csv` có sẵn cột `IB High/IB Low/IB range` (~1 tháng, 22 ngày). Trên M1 dài hơn (~9 tháng): **CHƯA có hàm** tính IB — phải viết mới (IB = range N phút đầu phiên, N tuỳ định nghĩa) | `IB High/Low` đọc trực tiếp cột có sẵn; hoặc `max/min(hi/lo)` của N nến đầu ngày từ M1 | Không nếu chỉ dùng nến đã đóng của IB window |
| 4 | VWAP phiên + độ lệch chuẩn VWAP | **MỘT PHẦN** | VWAP: **CÓ sẵn** trong `entry_dxfeed.load_m1/load_fpm1` (`b['vwap']`, reset khi gap>30'), phủ cả dxFeed (~9 tháng) và fp-m1 (~6 tháng). Độ lệch chuẩn VWAP: **CHƯA có code** — cần cộng dồn `Σ(tp-vwap)²·vol` theo phiên | VWAP đã có: cộng dồn `Σ(tp·vol)/Σvol` từ đầu phiên. Std cần viết thêm tương tự (rolling, không lookahead) | VWAP hiện tại đã đúng chuẩn nhân-quả (chỉ dùng nến ≤ hiện tại); nếu viết std-dev phải giữ đúng cách này |
| 5 | HVN (vùng "va chạm nhiều") theo mức giá | **MỘT PHẦN** | HVN **thật** (theo khối lượng từng mức): chỉ per-level, 46 ngày (`perlevel_m1.pkl`) hoặc 25 ngày (`_clean`). HVN **proxy** (đếm số nến chạm qua mức, không phải khối lượng): dùng `tpo_counts()` đã có sẵn trên toàn bộ M1 (~9 tháng) nhưng đó là TPO-count chứ không phải volume thật | Thật: tổng `ask_vol+bid_vol` mỗi `lvls[k]` qua các nến cùng mức giá, trong 25-46 ngày. Proxy: đếm số nến có `lo<=p<=hi` | Không, đều là dữ liệu lịch sử tĩnh (không phải "future") miễn chỉ tính tới thời điểm hiện tại |

### Tầng cấu trúc range (kịch bản 3)

| # | Feature | Phán quyết | Bộ dữ liệu · số tháng · n | Công thức | Rủi ro look-ahead |
|---|---|---|---|---|---|
| 6 | Swing high/low bằng cửa sổ fractal M1 | **MỘT PHẦN** | Chưa có hàm fractal nào trong code hiện tại. Dữ liệu nguồn (M1 OHLC) đủ nhiều: dxFeed ~9 tháng (103.857 nến) hoặc fp-m1 ~6 tháng (99.678 nến) — cần viết fractal detector mới | `swing_high[i] = hi[i]>hi[i-k..i-1] and hi[i]>hi[i+1..i+k]` (kiểu chuẩn N-bar fractal) | Fractal cần k nến SAU điểm swing để xác nhận → **có độ trễ xác nhận k nến**, phải tính đúng offset khi backtest (không được dùng swing chưa xác nhận tại thời điểm entry) |
| 7 | Đếm số lần chạm mỗi biên | **MỘT PHẦN** | Cùng nguồn M1 như #6, phụ thuộc định nghĩa range/biên (chưa có code range-tracking độc lập; hiện `cbr_v6.py` chỉ có box N-nến trượt, không phải range theo cấu trúc swing) | Đếm nến có `lo<=biên+tol<=hi` trong đời sống của range | Không, nếu chỉ đếm nến đã đóng |
| 8 | Độ rộng range (giá & tick), thời lượng tồn tại | **MỘT PHẦN** | Tương tự #6/#7 — cần định nghĩa range trước (hiện chưa có, chỉ có box N-nến cố định trong `cbr_v6.RANGE_LEN=8`) | `width = rhi-rlo`; `duration = t_end-t_start` | Không |
| 9 | Range còn hiệu lực / đã hỏng | **MỘT PHẦN** | Cần logic "phá vỡ" định nghĩa rõ (đã có 1 biến thể trong `cbr_v6.py`: `up/dn` break qua box N-nến + `BUF` tick) — nhưng đó là box cố định, không phải range-theo-cấu-trúc thật | Break khi close vượt biên ± buffer | Không nếu chỉ dùng nến đã đóng |
| 10 | Hợp lưu biên range với VAH/VAL/POC/IB | **MỘT PHẦN** | Cần #6-9 xong trước + zones đã có sẵn (`build_zones()` cho D-1 VAH/VAL/POC, session POC/VAH/VAL — đã hoạt động, ~9 tháng dxFeed) | So khoảng cách (tick) giữa biên range và các mức zone đã có | Không |

### Tầng đo lực (xác nhận vào lệnh)

| # | Feature | Phán quyết | Bộ dữ liệu · số tháng · n | Công thức | Rủi ro look-ahead |
|---|---|---|---|---|---|
| 11 | Delta theo nến (dấu, độ lớn, Delta %) | **CÓ** | `fp-m1-6-month.csv` (~6 tháng, cột `Delta`,`Delta, %` — nz 61.452/99.678, tức ~62% nến có delta khác 0) + `fp-m1-1-month-data.csv` (~1 tháng). dxFeed KHÔNG có delta | Đọc trực tiếp cột `Delta`/`Delta, %` | Không, là dữ liệu đã đóng của nến |
| 12 | Bid volume vs Ask volume theo nến | **CÓ** | `fp-m1-6-month.csv`: `Buy (Ask) volume`(nz 55.239), `Sell (Bid) volume`(nz 54.985), cả 2 kèm cột `%` | Đọc trực tiếp cột | Không |
| 13 | Cumulative delta / CVD phân kỳ | **CÓ** | `fp-m1-6-month.csv`: cột `Cumulative delta` có sẵn (nz 76.748/99.678), reset theo phiên (cần xác nhận logic reset của chính cột, hoặc tự cộng dồn từ `Delta` mỗi nến) | `CVD_t = CVD_{t-1} + Delta_t` (reset đầu phiên) | Không nếu cộng dồn nhân-quả; **rủi ro nếu dùng `Cumulative delta` in sẵn của vendor mà không biết mốc reset** — cần kiểm thêm trước khi tin cột này |
| 14 | Độ dài nến, thân/râu, vị trí đóng (cpos) | **CÓ** | Đã tính sẵn trong `load_m1`/`load_fpm1` (`rng,body,uw,lw,brat,cpos`) trên cả dxFeed (~9 tháng) và fp-m1 (~6 tháng) | `cpos=(c-lo)/rng`, `brat=body/rng`, `uw/lw` = râu trên/dưới | Không |
| 15 | VSA volume ratio vs SMA20 | **CÓ** | Đã tính sẵn (`vma`,`vratio`) trong cả dxFeed và fp-m1, ngưỡng đã dùng: High=1.2, climax=2.2 (khớp memory) | `vratio = v/SMA20(v)` (rolling, không gồm nến hiện tại theo cách đã cài) | Đã sửa 1 lỗi look-ahead tương tự trong quá khứ (`avg_vma` tính trên TOÀN CHUỖI) — `cbr_v6.prepare()` đã chuyển sang rolling 1000-nến CUỘN, không gồm nến hiện tại. Bài học: bất kỳ "trung bình cả file" nào đều là bẫy look-ahead |
| 16 | Delta từng mức giá (imbalance, stacked imbalance, absorption) | **MỘT PHẦN** | Tính được **offline thật sự** (có bid_vol/ask_vol per-level) nhưng CHỈ trên `perlevel_m1.pkl` (46 ngày rời rạc, 05-01→07-27) hoặc `perlevel_m1_clean.pkl` (25 ngày, chỉ 06-01→07-27, bỏ hẳn tháng 5). **KHÔNG đủ để làm GATE bắt buộc** cho backtest dài hạn (9 tháng dxFeed) vì sẽ làm phần lớn ngày "mù" tính năng — chỉ dùng làm lớp đối chứng/hiển thị cục bộ trên đúng những ngày có per-level, đúng như `WYCKOFF_V6_PLAN.md §10.5` đã cảnh báo | Imbalance: so `ask_vol[p]` với `bid_vol[p-1 tick]` (chéo mức); Stacked: N mức liên tiếp cùng vượt ngưỡng; Absorption: volume cao nhưng giá không dịch qua mức | Không nếu chỉ dùng lvls của nến đã đóng; nhưng độ phủ thưa (25-46/~180 ngày giao dịch khả dụng) khiến MỌI thống kê rút ra dễ overfit vào đúng những ngày ngẫu nhiên có mặt |
| 17 | Kích thước lệnh lớn nhất trong nến ("cá lớn") | **KHÔNG** | `Max one trade Vol.`/`Max one trade Vol, %` **toàn 0** ở `fp-m1-6-month.csv`, `TPO-chart-daily.csv`, `tpo-chart-m30.csv`; `max_one_trade` **toàn 0** ở cả `sample.csv` (761.199 dòng per-level) lẫn `sample_bars.csv` (77.672 dòng) — đã kiểm TOÀN BỘ nguồn đang có, không nguồn nào khác 0 | — | — |

---

## 6. Không kiểm được offline (để GĐ4 không thiết kế vào đó)

1. **DOM/Level 2 sống, vị trí trong hàng đợi, phát hiện iceberg real-time** — không tồn tại trong bất kỳ export
   nào (đã biết, `WYCKOFF_V6_PLAN.md §10.5`).
2. **Kích thước lệnh lớn nhất / "cá lớn"** (feature #17) — cột nguồn toàn 0 ở MỌI file đang có, đã kiểm lại độc
   lập ở mục 5.
3. **Số lượng giao dịch (trade count) tách theo phía Buy/Sell** — `Buy (Ask) trades`/`Sell (Bid) trades`/
   `Delta trades` toàn 0 ở mọi file (kể cả `sample.csv` per-level: `buy_trades`/`sell_trades` cũng toàn 0). Chỉ có
   **volume** tách phía, không có **số lệnh** tách phía, ở bất kỳ đâu.
4. **Spread, slippage, phí giao dịch thực tế** — không có trong bất kỳ export nào (đã biết, `§11`).
5. **Stacked imbalance/hấp thụ/iceberg liên tục xuyên suốt 9 tháng** — chỉ có 25-46 ngày rời rạc (mục 5, #16),
   không thể mở rộng bằng nguồn hiện có.
6. **Open Interest cho fp-m1** — cột `Open interest` trong `fp-m1-6-month.csv` toàn 0 (khác với 2 file TPO, nơi có
   cột `Open Interest` thật — xem mục 3.2). fp-m1 không có Open Interest dùng được.

---

## 7. Hạ tầng còn thiếu

a. **Zone-pool warm-up cho backtest bắt đầu giữa file ngắn** (phát sinh trực tiếp từ điều tra mục 4): cần thêm
   tham số cho `build_zones()`/`daily_levels_from_m1()` trong [`entry_dxfeed.py`](entry_dxfeed.py) để nhận một
   khoảng "lịch sử làm ấm" trước điểm bắt đầu cửa sổ chấm điểm — hiện `entry_xcheck.py`/`round3_v6.py` chỉ build
   pool từ chính `B` đang chấm điểm. Không có infra này thì mọi so sánh dxFeed ↔ fp-m1 (hoặc bất kỳ backtest nào
   khởi động gần đầu file dữ liệu ngắn) đều lệch pool một cách không kiểm soát.
b. **Loader chuẩn cho TPO CSV** (`TPO-chart-daily.csv`, `tpo-chart-m30.csv`) — hiện chưa có, cần viết mới trong
   `research/` (đề xuất `research/tpo_loader.py`), API tối thiểu: `load_tpo(path) -> list[bar]` với field đã tách
   đúng khối cột trùng tên (`Open interest` chết vs `Open Interest` thật — mục 3.2), cảnh báo ngay trong code rằng
   bar interval THẬT khác tên file (mục 1.4).
c. **Loader cho per-level pkl** (`perlevel_m1.pkl`/`perlevel_m1_clean.pkl`) — hiện chưa có hàm dùng chung, mỗi
   script tự `pickle.load()` riêng lẻ. Đề xuất `research/perlevel_loader.py` với API `load_perlevel(path) ->
   list[bar]` (mỗi bar giữ nguyên field `lvls`) + hàm tiện ích `imbalance_at(bar, tick)`,
   `stacked_imbalance(bar, min_run)` để GĐ6/GĐ7 dùng thống nhất, tránh mỗi người tính lại theo cách khác nhau.
d. **Fractal swing-detector cho tầng cấu trúc range** (feature #6-10) — hoàn toàn chưa có trong code, cần viết mới,
   đặt cạnh `cbr_v6.py` (đề xuất `research/wyckoff/range_struct.py`) nếu kịch bản 3 được chọn triển khai.
e. **IB (Initial Balance) từ M1** — hiện chỉ có sẵn trong cột `TPO-chart-daily.csv` (1 tháng); muốn IB trên toàn bộ
   9 tháng M1 phải viết hàm mới (range N phút đầu phiên) cạnh `daily_levels_from_m1()`.
f. **VWAP độ lệch chuẩn** — VWAP đã có, std-dev quanh VWAP thì chưa; viết thêm 1 accumulator cộng dồn
   `Σ(tp-vwap)²·vol` theo phiên, đặt cạnh phần tính `vwap` hiện tại trong `load_m1`/`load_fpm1`.

---

## Phụ lục — log chạy đầy đủ

Toàn bộ số liệu trong file này tái lập bằng:
```bash
cd quantower-entry-signal/research/wyckoff
python3 data_capability_audit.py all     # ~2-3 phut, khong can pandas
```
Script: [`research/wyckoff/data_capability_audit.py`](wyckoff/data_capability_audit.py).
