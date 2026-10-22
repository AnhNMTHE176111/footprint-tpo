# BENZO-B-v3 — Setup B "Hấp thụ": thêm VÙNG HỖ TRỢ / KHÁNG CỰ (S/R) vào 8 loại vùng của B v2

Opus viết 2026-10-23, **chỉ đặc tả, không code**. Người làm (Sonnet) đọc trước: `plans/BENZO-B-v2-plan.md` (khung tái dùng — mọi luật
không nhắc lại ở đây thì **giữ y như v2**), `benzo-trader/research/{setup_b_hap_thu.py (prepare + detect), zones_b_v2.py, setup_b_v2.py,
test_b_v2.py, report/RESULTS-B-v2.md}`, `benzo-trader/research/benzo_vcl.py` (`load_rec`, `ZoneMap`, `verdict`, `band`, `rstat`),
`vung-canh-lenh/research/vcl5.py` (engine VCL v5) + `test_lan_cham.py::test_v5_va_lan_cham_khong_nhin_truoc`,
memory `vung-canh-lenh-sr-indicator.md`, `report/SR-KET-QUA.md`.

**Dữ liệu (cố định):** CHỈ `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d{.csv,_bars.csv}` (`SB.D90`).
TRAIN = phiên ≤ 2026-09-15 (35 phiên sạch), TEST từ 2026-09-16 (26). 61 phiên sạch ⇒ "lệnh/ngày" chia 61. Chi phí 0,2 giá/lệnh, nến chạm cả
SL lẫn TP ⇒ SL, 1 lệnh mở cùng lúc (`kernel.simulate`). **Không chạy file 2 năm.**

**Thuật ngữ:** *look-ahead* = nhìn trước · *slot* = khe (chỗ chứa cố định một vùng VCL trong mảng theo nến) · *eid* = mã định danh một vùng VCL
trong suốt đời sống của nó · *bootstrap* = lấy mẫu lại có hoàn lại để ước khoảng tin cậy (KTC) · *leave-one-out* = bỏ-một-loại-vùng.

---

## 0. Bối cảnh và kỳ vọng trung thực

| Mốc phải tái tạo (điều kiện tiên quyết, test 4.1–4.2) | n | WR | R TB |
|---|---|---|---|
| B cũ (2 VWAP) | 11 | 27,3 % | 0,00 |
| B v2 (12 mức / 8 loại) | 25 | 32,0 % | 0,19 |

- B v2 đã kết luận **"chỉ tăng số lượng"**: nằm trong dải đối chứng dời, TRAIN/TEST ngược dấu (−0,09 / +0,45).
- S/R đã đo **3 lần độc lập** (SR-KET-QUA 65 phiên, HVN 474 phiên, VCL 5 vòng): **vị trí vùng không mang thông tin; xác suất chạm chỉ phụ
  thuộc khoảng cách.** BENZO-VCL: trong 11 lệnh B cũ, 4 lệnh nằm trong vùng VCL, 7 ngoài — không khác nhau đo được.
- ⇒ Kỳ vọng mặc định của vòng này: **n tăng mạnh (VCL luôn có 6–7 vùng sát giá), WR trôi về ~27 % (hoà vốn 3R), B v3 ≈ dải đối chứng.**
  Vòng này đo để xác nhận hoặc bác điều đó bằng số, không phải để "tìm cho ra" vùng tốt.

---

## 1. CHỌN VÙNG S/R — cái gì vào, cái gì không, vì sao

### 1.1 Đã chọn: hai họ vùng mới

| Họ (ztype) | Tên mức | Là gì | Lý do chọn |
|---|---|---|---|
| **`VCL`** | `VCL_R1..7`, `VCL_S1..7` | vùng đang hiển thị của **Vùng Canh Lệnh v5** (rộng 2–5 giá; gộp swing M5, swing M15, mốc phiên trước, POC trần, số tròn) | người học yêu cầu ưu tiên; đây là bản đồ S/R đã dựng, đã kiểm không nhìn trước, đã có cache |
| **`PDHL`** | `PDH`, `PDL` | đỉnh / đáy của **phiên đầy đủ gần nhất đã đóng** (cùng phiên `q` mà kernel dùng cho VAH/VAL/POC hôm qua) | S/R "cổ điển" người học quen nhất; là ĐƯỜNG (điểm) như vùng v2 nên dùng nguyên cơ chế B; VCL có chứa đỉnh/đáy phiên trước nhưng chỉ hiển thị 2 gần + 1 xa mỗi phía và đã gộp/trôi trong dải ⇒ PDH/PDL nhiều lúc bị ẩn hoặc lệch. Rẻ, không thêm cơ chế |

### 1.2 Đã cân nhắc và LOẠI

| Ứng viên | Lý do loại |
|---|---|
| Swing M5 / M15 làm đường điểm riêng | đã là lõi của VCL (ứng viên B, B15); làm riêng = hàng trăm đường dao động, trùng lặp VCL |
| Số tròn 10/50/100 | đã có trong VCL (D); SR-KET-QUA: ≈ mức ngẫu nhiên |
| Giá đóng phiên trước | đã có trong VCL (C); không phải khái niệm S/R người học dùng |
| IB, VA phiên Âu | B đã dùng chúng làm **bộ lọc chế độ** (`edge_bad`) ⇒ dùng làm vùng là vòng tròn |
| Đỉnh/đáy tuần trước | xa giá như HVN_W (trung vị 90+ giá) ⇒ n ≈ 0, chỉ thêm phép so |
| VA/POC đang hình thành của phiên hiện tại | đã loại ở v2 mục 1.1 (nhảy mạnh đầu phiên); giữ nguyên |

### 1.3 VCL đưa vào cơ chế B ra sao — định nghĩa CHÍNH XÁC

B làm việc với **mảng giá Z theo nến** (một điểm mỗi nến cho mỗi tên mức). VCL là **tập dải [lo, hi] thay đổi theo nến** (bảng `rec`: cột
`bar, lo, hi, eid, side, slot, mask, …`; mỗi nến 3–7 vùng; đã đo trên cache: **4262 eid, mọi eid liền mạch không đứt quãng, đồng thời tối đa
7, tuổi thọ trung vị 60 nến, rộng trung vị 2,25 giá, cạnh `lo` trong cùng eid trôi trung vị 0,18 / p90 1,75 giá**). Chuyển đổi:

**(a) Nguồn.** `rec = benzo_vcl.load_rec(df)` (cache `vung-canh-lenh/research/report/cache_lc/v5.pkl`; thiếu thì tự chạy engine). `rec.bar` là
VỊ TRÍ nến trong df. **Assert căn hàng:** nạp `vcl5.load(vcl5.BASE90)`, `K._enrich(bars.sort_values('datetime'))` ⇒ cùng độ dài và cùng `datetime`
với `K.load_bars(D90 + '_bars.csv')` (đã kiểm tay: 86333 = 86333, khớp). Ghi md5 của file cache vào báo cáo.

**(b) Gán khe theo eid — thuật toán TRỰC TUYẾN (chỉ dùng nến ≤ t):** duyệt nến t tăng dần. Tại t: tập eid có mặt `E_t`. Khe nào đang giữ eid
không còn trong `E_t` ⇒ giải phóng. Eid mới (chưa từng thấy) sắp theo (`lo` tăng, rồi `eid` tăng) ⇒ mỗi cái nhận **khe trống có số nhỏ nhất**.
Eid đã giữ khe thì giữ nguyên tới hết đời. Eid xuất hiện lại sau khi đã biến mất ⇒ `raise` (đã đo: 0 ca). Số khe cần **K_VCL = 7**
(assert ≤ `VCL_SLOTS_MAX = 7`; vượt ⇒ dừng, báo). Vì gán khe chỉ phụ thuộc eid đã sinh ở nến ≤ t, kết quả trên [0, t] không đổi khi cắt dữ liệu.

**(c) Hai cạnh, hai vai, một chiều mỗi cạnh:**

| Tên | Z tại nến j | Chiều move cho phép | Lệnh | Nghĩa |
|---|---|---|---|---|
| `VCL_Rk` | `lo` của eid đang ở khe k | chỉ **M = +1** (giá đi LÊN tới Z) | SELL | chạm **cạnh dưới** của vùng phía trên = kháng cự, cạnh gần |
| `VCL_Sk` | `hi` của eid đang ở khe k | chỉ **M = −1** (giá đi XUỐNG tới Z) | BUY | chạm **cạnh trên** của vùng phía dưới = hỗ trợ, cạnh gần |

Khe trống ⇒ NaN. Lý do chọn **cạnh gần** thay vì tâm: B là "lệnh thụ động chặn ở mép" — cụm nến phải dừng trong Z + 0,5 (`EXT_TOL`); với tâm
dải 2–5 giá, giá được phép lún 1–2,5 giá vào vùng mà vẫn tính "hấp thụ", lệch ý nghĩa. Bảng tra VCL cũng đo theo **cạnh gần**. Lý do khoá một
chiều: cạnh `lo` bị chạm từ trên xuống nghĩa là giá đã xuyên qua cả vùng — không còn là vai hỗ trợ/kháng cự của vùng đó. Biến thể **tâm, hai
chiều** chỉ chạy ở phụ lục (mục 3.7), không vào phán quyết.

**(d) Điều kiện "ấm" (warm) cho khe VCL:** `runlen[k][j]` = số nến liên tiếp tới j mà khe k giữ CÙNG một eid. `warm[VCL_*k][j] = runlen[k][j] ≥
VCL_WARM = 4`. Vì `detect` đòi `warm` ở mọi nến cụm i−N..i−1, điều này bảo đảm **cả cụm và Z tại i−1 cùng thuộc một eid** (đúng cho N ≤ 4, tức
mọi ô của lưới độ nhạy). Không cần thêm điều kiện tuổi nào khác.

**(e) Trôi cạnh:** Z của khe là cạnh **tại từng nến** (như VWAP trôi). `detect` đã dùng `zv[i−1]` cho Z, `touch[j]` dùng `zv[j]` — giữ nguyên.

**(f) Không nhìn trước:** `rec` tại nến i chỉ dùng nến ≤ i (đã kiểm: `test_lan_cham.py::test_v5_va_lan_cham_khong_nhin_truoc`). Gán khe trực
tuyến (b) + runlen chỉ nhìn lùi ⇒ mảng VCL tại j chỉ dùng nến ≤ j. Vẫn kiểm lại bằng test cắt dữ liệu riêng (4.7).

### 1.4 PDH / PDL — định nghĩa chính xác

Với phiên s: `q` = phiên mà `kernel._zones(ctx, s, None, naked=False)['yday']['session_no']` trả (phiên trước đầy đủ ≥ 300 nến, có profile,
sau chỗ nối). `PDH = max(high[start_q : end_q])`, `PDL = min(low[start_q : end_q])`, gán hằng cho mọi nến phiên s. `yday` là None ⇒ NaN.
Cố định ⇒ `warm = True` từ nến đầu phiên. **Cả hai chiều M** (như mọi mức điểm của v2 — đỉnh cũ bị phá rồi giữ làm hỗ trợ là S/R hợp lệ).
`ztype = 'PDHL'` cho cả hai (một khái niệm "biên phiên trước" ⇒ trần 2 lệnh/phiên chung, ít phép so hơn).
Ghi chú: phiên 07-29 dựng trên phiên thin 07-28 — giống VAH/VAL/POC v2, ghi chú, không sửa kernel.

### 1.5 Thứ tự ưu tiên, trần, vùng chồng nhau

1. **Thứ tự cố định** (`ZONE_ORDER_V3`):
   `VWAP_W, VWAP_D, POC_D, VAH_D, VAL_D, HVN_D1..3, POC_W, HVN_W1..3` (= v2, y nguyên) → `PDH, PDL` → `VCL_R1..7` → `VCL_S1..7`.
   Mức điểm (PDHL) trước VCL vì chính xác và dễ diễn giải hơn dải trôi. Hai họ mới đều **sau** v2 ⇒ **B cũ ⊆ B v2 ⊆ B v3** ở mức lệnh thô
   (cùng idx/side/entry/sl/tp/zprice) — assert bắt buộc (4.3).
2. **Không gộp giá.** Một nến xác nhận i ⇒ tối đa 1 lệnh; mức khớp đầu tiên theo thứ tự thắng; mọi mức khớp khác ghi vào `zones_hit` (cơ chế v2
   sẵn có). VCL_R và VCL_S không thể cùng khớp tại i (khác chiều lệnh — nến xác nhận không thể đóng theo cả hai chiều).
   Giữa các khe VCL cùng vai: khe số nhỏ thắng — chỉ đổi tên/zprice ghi lại, không đổi lệnh (cùng ztype, entry/SL tính từ cụm).
3. **Trần 2 lệnh / (ztype, phiên)** — `VCL` là MỘT loại (14 tên, trần chung 2/phiên); `PDHL` một loại. Trần của 8 loại v2 không đổi.
   Báo số lệnh thô bị trần cắt theo loại (chạy `detect` thêm một lần với `SB.MAX_PER_ZONE_SESSION` tạm = 10**9 qua context manager, khôi phục ở
   `finally`; chỉ để đếm).
4. `one_at_a_time` giữ nguyên ⇒ lệnh vùng mới có thể chặn lệnh v2. Báo số lệnh v2 bị mất và R của chúng (mục 3.2).
5. **Báo trùng (mô tả, không lọc):** (i) với mỗi lệnh VCL/PDHL: khoảng cách |Z − mức v2 gần nhất| tại i; (ii) tỉ lệ nến chạm cạnh VCL mà cũng
   nằm ≤ 1 giá từ một mức v2; (iii) với lệnh VCL: `slot` (K/N/F), độ rộng vùng, các nguồn trong `mask` — n < 10 chỉ in số.

---

## 2. THAY ĐỔI CODE — tối thiểu

**Không sửa** `kernel.py`, `zones_b_v2.py`, `setup_b_v2.py`, mọi file VCL, mọi hằng số B (`MOVE_MIN, LOOKBACK, TOUCH_TOL, EXT_TOL, WARM,
BIG_EXCL, RR, MAX_PER_ZONE_SESSION, THETAS, NS, MAIN`). Không đụng C#.

### 2.0 Trước khi sửa bất cứ gì

Chạy code HIỆN TẠI (chưa sửa) ⇒ ghi fixture `benzo-trader/research/report/_b_v2_idx.json` = danh sách `[idx, side, entry, sl, tp, zone]` của
lệnh B v2 đã đóng (θ 0,5 · N 3 · TP 3R), kèm n/WR/R. Phải ra 25 / 32,0 % / 0,19; lệch ⇒ dừng, báo.

### 2.1 `setup_b_hap_thu.py` — 2 sửa (~8 dòng)

1. `prepare(..., extra_zones)`: mỗi mục nhận **tuple 2 hoặc 4 phần tử** `(arr, ztype[, warm, mdirs])`. 2 phần tử ⇒ hành vi cũ y nguyên
   (warm = True mọi nến, hai chiều). 4 phần tử: `warm` (mảng bool độ dài n, hoặc None ⇒ True mọi nến), `mdirs` (tuple con của `(1, -1)`, hoặc
   None ⇒ `(1, -1)`). Lưu `P['mdir'] = {name: mdirs}`; VWAP ⇒ `(1, -1)`.
2. `detect`: `for M in (1, -1):` ⇒ `for M in P.get('mdir', {}).get(name, (1, -1)):` (dùng `.get` để P dựng tay trong test cũ vẫn chạy).
   Không đổi gì khác. `detect2`, `run_cell`, `main*` không đụng.

### 2.2 `research/zones_b_v3.py` (mới, ~150 dòng)

```
import zones_b_v2 as ZB, benzo_vcl as BV, kernel as K
VCL_SLOTS_MAX = 7 ; VCL_WARM = 4
R_NAMES = ('VCL_R1',…,'VCL_R7') ; S_NAMES = ('VCL_S1',…,'VCL_S7')
ZONE_ORDER_V3 = ZB.ZONE_ORDER + ('PDH','PDL') + R_NAMES + S_NAMES
ZTYPE_OF_V3   = ZB.ZTYPE_OF ∪ {PDH,PDL→'PDHL'} ∪ {VCL_*→'VCL'}
ZTYPES_V2     = ('VWAP_W','VWAP_D') + ZB.ZTYPES_NEW          # 8 loại
ZTYPES_SR     = ('PDHL','VCL')
ZONES_OLD, ZONES_V2 = ZB.ZONES_OLD, ZB.ZONES_V2 ; ZONES_V3 = ZONE_ORDER_V3
names_of3(ztypes) -> tuple tên theo ZONE_ORDER_V3

check_align(df)                         -> None (assert 1.3a)
vcl_slots(rec, n)                       -> dict: lo[K,n], hi[K,n], eid[K,n] (−1 trống), runlen[K,n]      (1.3b, 1.3d)
pdhl(df, prof, ctx)                     -> (pdh[n], pdl[n])                                                 (1.4)
build_extra3(df, prof, ctx, lev, rec)   -> dict name -> (arr, ztype, warm, mdirs) theo ZONE_ORDER_V3[2:]
     # 10 mức v2: (arr, zt, None, None) lấy từ ZB.build_extra; PDH/PDL: (…, None, None);
     # VCL_Rk: (lo[k], 'VCL', runlen[k] >= VCL_WARM, (1,)); VCL_Sk: (hi[k], 'VCL', runlen[k] >= VCL_WARM, (-1,))
vcl_any(extra3, df)                     -> (r_any[n], s_any[n])  # cột cho ĐC2, xem 3.4
zone_table3(extra3, df)                 -> DataFrame: mọi tên mức + 'VCL_R_ANY','VCL_S_ANY'
shifted3(extra3, zc, delta_by_sno, sno) -> như ZB.shifted nhưng GIỮ warm và mdirs; VWAP cộng δ như v2
vcl_mid_extra(slots)                    -> 7 mức 'VCL_M1..7' = (lo+hi)/2, ztype 'VCL', warm runlen, hai chiều (chỉ phụ lục 3.7)
overlap3(...)                           -> số liệu mục 1.5.5
```

### 2.3 `research/setup_b_v3.py` (mới) — pipeline đo, ghi `report/RESULTS-B-v3.md` + `report/_eval_b_v3.txt`

`import setup_b_v2 as B2` và **tái dùng** `run, closed, gstats, rs, cmp_vs, bands_of, _patched_map, esc, f, pct, nwr, ci, plot_trade, cf_ratio`.
Viết mới chỉ: `Data3` (như `B2.Data` + `rec`, `extra3`, `P` dựng bằng `extra3`), `dc1_v3`, `dc2_v3`, `main`.

Hằng số đầu file, **commit trước khi chạy lần đầu**:
`MAIN=(0.5,3)` · `RR=3.0` · `SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024` (assert = `BV.*`) · `CTRL_DRAWS=200` ·
`BOOT, BOOT_SEED = 10000, 0` · `MIN_N=10` · `EXPECT_OLD=(11, 0.273, 0.00)` · `EXPECT_V2=(25, 0.320, 0.19)` · `EXPECT_N_V3=(40, 100)` ·
`BREAKEVEN_WR=0.27` · `VCL_WARM=4` · `EXPECT_TXT` = mục 3.6 nguyên văn.

---

## 3. PHÉP ĐO

Mọi cấu hình: **θ 0,5 · N 3 · TP 3R · mono 'ends' · variant 'base' · bias False · mọi pha trừ OFF** (ô chính, như v2). Không chạy lưới cho
vùng mới để chọn; lưới 3×3 θ×N chỉ in phụ lục cho B-v3, không chọn lại.

### 3.1 Ma trận cấu hình (bảng chính)

| # | Cấu hình | Vùng (`zones=`) | Mục đích | Có phán quyết? |
|---|---|---|---|---|
| 1 | **B-cũ** | VWAP_W, VWAP_D | mốc 11 / 27,3 % | — (mốc) |
| 2 | **B-v2** | 12 mức v2 | mốc 25 / 32,0 % | — (mốc) |
| 3 | **B-v3** | v2 + PDHL + VCL | bản đề xuất | ✔ |
| 4 | Chỉ-S/R | PDHL + VCL, **không** v2 | S/R tự đứng được không | ✔ |
| 5 | Chỉ-VCL | VCL | | mô tả |
| 6 | Chỉ-PDHL | PDH, PDL | | mô tả |
| 7 | B-v2 + VCL (= B-v3 bỏ PDHL) | | đóng góp riêng VCL | ✔ |
| 8 | B-v2 + PDHL (= B-v3 bỏ VCL) | | đóng góp riêng PDHL | ✔ |
| 9–16 | B-v3 bỏ k, k ∈ 8 loại v2 | | đóng góp từng loại cũ khi đã có S/R | mô tả |

Với chỉ 2 loại mới, "thêm-một vào v2" và "bỏ-một khỏi v3" **trùng nhau** (hàng 7, 8) — không chạy hai lần.
Mỗi hàng báo như v2 mục 3.1: n · lệnh/ngày · **WR** · R TB · KTC 95 % · kỳ vọng giá/lệnh · tổng R · chuỗi thua · TRAIN/TEST/T8/T9/T10
(`n · WR · R`) · A/EU/US · BUY/SELL. Hàng 1, 2, 3 đặt liền nhau, **cột WR in đậm**.

### 3.2 Tách đóng góp ở mức LỆNH

Trước `simulate`: `E_old, E_v2, E_v3 = detect(zones=ZONES_OLD / ZONES_V2 / ZONES_V3)` trên CÙNG một `P` (dựng bằng `extra3`). Assert chuỗi tập con
(4.3). Sau `simulate`:
- **Lệnh chung v2∩v3**; **lệnh chỉ-v3** (idx có ở v3, không ở v2) — **nhóm quyết định**; **lệnh v2 bị mất** ở v3 (bị chặn) — n, số thắng, R.
- Lệnh chỉ-v3 tách theo loại (`VCL` / `PDHL`), cả hai cách đếm "vùng thắng" và "bất kỳ vùng" (`zones_hit`). n < 10 ⇒ chỉ in số.
- Với lệnh VCL: SELL tại cạnh dưới vs BUY tại cạnh trên; slot K/N/F; độ rộng vùng (≤ 2,5 / > 2,5 giá). Chỉ mô tả.
- Phễu `funnel` B-v2 vs B-v3 (bước 1→7) cạnh nhau; số lệnh thô bị trần cắt theo loại (1.5.3).

### 3.3 Công suất thống kê — in TRƯỚC bảng chính

Sai số WR ≈ √(p(1−p)/n). Chênh WR nhỏ nhất phát hiện được (80 %, hai phía) giữa B-v2 (n=25) và B-v3 (n thật):
≈ 2,8 × √(p(1−p)) × √(1/25 + 1/n) — với n = 60 ⇒ ≈ **30 điểm**. Chênh R TB nhỏ nhất ≈ 2,8 × σ_R × √(1/25 + 1/n), σ_R đo thật. In theo n thật,
kèm câu: *"so WR v2 ↔ v3 trực tiếp gần như vô nghĩa; phán quyết dựa vào đối chứng và nhóm lệnh chỉ-v3."*

### 3.4 Đối chứng — bắt buộc, khớp khoảng cách

- **ĐC1 — dời bản đồ vùng (khớp khoảng cách tại điểm vào theo xây dựng).** Mọi mức của phiên (12 v2 + PDH/PDL + 14 cạnh VCL; VWAP động cộng
  hằng δ) dời cùng δ[phiên, bản], ma trận `ZB.shift_matrix(nS, 100, 3, 15, 20261024)` (= `benzo_vcl.Data().dsh[:, 1:]`). `warm` và `mdirs` **không
  đổi** (là danh tính vùng, không phải vị trí). Chạy nguyên `prepare(extra_zones=shifted3(...))` + `detect` + `simulate` cho các cấu hình **2, 3, 4,
  7, 8** mỗi bản (cần 2 để tính "chỉ-v3" của bản dời = v3 dời trừ v2 dời cùng bản). Bộ lọc chế độ/VA Âu/IB **không** dời.
  Mọi lệnh — thật hay dời — đều có cụm chạm Z ≤ 1 giá, cùng cơ chế move→cụm→CF ⇒ chỉ khác **vị trí**.
  ⚠ **Bẫy đã biết:** dời làm thay đổi phân phối khoảng cách vùng↔giá theo thời gian (VCL vốn chọn vùng SÁT giá; dời ±3–15 đẩy một số ra xa) ⇒
  **số lệnh n của bản dời KHÔNG so để phán quyết** (đó chính là bẫy "đối chứng xa giá hơn ⇒ ▼ giả"). Chỉ phán quyết trên **WR và R TB mỗi lệnh**
  (điều kiện theo chạm ⇒ khớp khoảng cách). n bản dời chỉ in để tham khảo, ghi rõ lý do.
- **ĐC2 — vào ngẫu nhiên tại cùng loại mức, cùng chế độ, cùng chiều** (`kernel.control_sample`, không sửa, qua `B2._patched_map` mở rộng cho
  `zone_table3`). Lệnh v2/PDHL: `zone` = tên mức (như v2). Lệnh VCL: `zone = 'VCL_R_ANY'` (SELL) / `'VCL_S_ANY'` (BUY), trong đó
  `VCL_R_ANY[j]` = trong các cạnh `VCL_Rk` **đang ấm** tại j mà nến j CHẠM (|close − Z| ≤ 1 hoặc râu chứa Z), lấy cạnh gần close nhất; không cạnh
  nào chạm ⇒ NaN. (Định nghĩa này làm mặt nạ chạm của `control_sample` đúng bằng "chạm một cạnh kháng cự VCL bất kỳ".) 200 lần. Làm cho B-v3,
  Chỉ-S/R, lệnh chỉ-v3, B-v2+VCL.
- **ĐC3 — v2 vs v3** = bảng 3.1 + 3.2.

**Ngưỡng "khác đối chứng" — nguyên `PLAN-LAN-CHAM.md` mục 5, dùng `benzo_vcl.verdict`:** thật ngoài dải 5–95 % ở **cả TRAIN và TEST**, cùng dấu,
cùng dấu ở ≥ 2/3 tháng, |hiệu| > 2 sai số ở cả hai nửa. Chỉ áp dụng khi nhóm có **≥ 10 lệnh ở cả TRAIN và TEST**; không thì "không áp dụng (n
nhỏ)". Không dùng chữ "có xu hướng".

**Số phép so có phán quyết (đăng ký trước, 9):** B-v3 vs ĐC1, B-v3 vs ĐC2, chỉ-v3 vs ĐC1, chỉ-v3 vs ĐC2, Chỉ-S/R vs ĐC1, Chỉ-S/R vs ĐC2,
B-v2+VCL vs ĐC1, B-v2+PDHL vs ĐC1, B-v2+VCL vs ĐC2. Ở mức 5 % kỳ vọng ~0,45 ô "vượt" do ngẫu nhiên ⇒ **một ô lẻ không phải bằng chứng.**

### 3.5 Tiêu chí phán quyết — đăng ký trước, kiểm theo thứ tự

1. **"Chỉ tăng số lượng"** (mặc định): n(B-v3) > n(B-v2) **và** [B-v3 nằm trong dải 5–95 % ĐC1 về WR hoặc R TB ở TRAIN hoặc TEST, **hoặc** lệnh
   chỉ-v3 có WR ≤ 27 % + 1 sai số]. Câu bắt buộc: *"Vùng S/R cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v3 ≈ B v2 chạy ở nhiều chỗ
   hơn."*
2. **"Tệ đi"**: lệnh chỉ-v3 có R TB < mốc 5 % của ĐC1 hoặc < ĐC2 − 2 sai số ở cả TRAIN và TEST (n ≥ 10 mỗi bên); **hoặc** B-v3 làm mất ≥ 3 lệnh
   v2 thắng do chặn. ⇒ không ship; ghi loại (VCL/PDHL) kéo xuống nếu hàng 7/8 chỉ ra được với n ≥ 10.
3. **"Cải thiện thật"** — **đồng thời**: (a) n(B-v3) ≥ 40, ≥ 10 ở cả TRAIN và TEST; (b) R TB(B-v3) > 0 ở cả TRAIN và TEST; (c) lệnh chỉ-v3 có
   WR ≥ WR(B-v2) **và** R TB > 0 ở cả TRAIN và TEST; (d) B-v3 **và** lệnh chỉ-v3 vượt **cả ĐC1 lẫn ĐC2** theo ngưỡng 3.4 (về R TB); (e) không
   loại mới nào (n ≥ 10) có R TB < −0,5 mà bỏ nó làm tổng tốt lên > 2 sai số.
   Đạt (a)(b)(c) mà trượt (d) ⇒ **"ứng viên, chưa có lợi thế đo được; cần ≥ 3 tháng dữ liệu mới"** — không viết "cải thiện".
   Nói rõ trong báo cáo: với 61 phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,5R.
4. Riêng **Chỉ-S/R** (hàng 4) có câu kết luận riêng theo cùng ngưỡng: "S/R tự đứng: khác / ≈ đối chứng / không áp dụng".

### 3.6 Kỳ vọng đăng ký trước (chép vào đầu `RESULTS-B-v3.md` TRƯỚC khi chạy)

- n(B-v3): 25 → **40–100**. Căn cứ: cạnh VCL bị chạm ~33 000 cặp (nến, vùng) mỗi vai trên 90d so với ~20 000 lượt chạm (hai chiều) của 12 mức
  v2; trần 2/phiên chặn trên ở 122 lệnh VCL. PDHL đóng góp nhỏ (0–5 lệnh; SR-KET-QUA chỉ ~960 lượt vào dải/65 phiên).
- n không tăng ≥ 1,6× ⇒ bộ lọc cụm/θ/chế độ là nút thắt, không phải vùng — vẫn báo.
- WR ở 3R: **24–33 %**, trôi về hoà vốn ~27 %. **B-v3 ≈ dải ĐC1; lệnh chỉ-v3 ≈ ĐC2.** (Ba lần đo S/R trước đều ra như vậy.)
- Không ép: không chọn ô độ nhạy đẹp; không chọn biến thể "tâm"; TP 2R không chạy; không thêm bộ lọc giữa chừng.

### 3.7 Phụ lục (in, KHÔNG phán quyết, KHÔNG chọn)

1. Lưới 3×3 θ ∈ {0,3; 0,5; 0,7} × N ∈ {2, 3, 4} cho B-v3 (n · WR · R).
2. Biến thể **VCL tâm hai chiều**: `zones = ZONES_V2 + VCL_M1..7` (dựng `prepare` riêng với `vcl_mid_extra`). In n · WR · R, TRAIN/TEST.
3. Lệnh chỉ-v3 theo pha A/EU/US.

### 3.8 Ví dụ soi chart

5 lệnh thắng + 5 lệnh thua của **nhóm chỉ-v3** (cách đều theo thời gian, xác định), kèm giờ UTC/VN, loại, Z, dải VCL [lo, hi] nếu là VCL,
`zones_hit`, move, |Δ_CF|/max, SL/TP. Vẽ bằng `B2.plot_trade` (truyền thêm dải VCL tô nhạt), lưu `report/img/b_v3_*.png`.

### 3.9 Thời gian chạy

`prepare` + `vcl_slots` 1 lần (~15 s). ĐC1: 100 bản × 5 cấu hình (28 tên mức) — ước 25–40 phút. Vượt 45 phút ⇒ giảm REPS xuống 50 **và ghi rõ
trong báo cáo** (ma trận δ lấy 50 cột đầu). ĐC2: 200 lần × 4 nhóm ≈ 3–5 phút.

---

## 4. UNIT TEST — `research/test_b_v3.py` (pytest; chạy xanh TRƯỚC khi sinh báo cáo)

1. **Tái tạo B cũ:** `detect(P3, 0.5, 3, zones=ZONES_OLD)` + `simulate` ⇒ n 11, WR 27,3 %, R 0,00 (±0,005), idx khớp `_b_old_idx.json`.
2. **Tái tạo B v2:** `detect(P3, 0.5, 3, zones=ZONES_V2)` ⇒ n 25, WR 32,0 %, R 0,19 (±0,005); `[idx, side, entry, sl, tp, zone]` khớp
   `_b_v2_idx.json` (ghi ở 2.0). Cả với `P` dựng bằng `ZB.build_extra` (2-tuple, code v2) lẫn `P3` dựng bằng `extra3` (4-tuple) ⇒ cùng kết quả.
3. **Chuỗi tập con + trần:** idx(E_old) ⊆ idx(E_v2) ⊆ idx(E_v3), entry chung giống hệt side/entry/sl/tp/zprice/zone; groupby (ztype, phiên) ≤ 2
   trong E_v3; mọi lệnh VCL có `ztype == 'VCL'`.
4. **Gán khe (tổng hợp):** `rec` giả 5 eid với vòng đời chồng nhau (tối đa 3 đồng thời) ⇒ K = 3; mỗi eid đúng một khe suốt đời; không hai eid cùng
   khe cùng nến; khe trống = NaN, eid = −1; khe giải phóng tại t được eid mới sinh tại t dùng lại; `runlen` đúng tay; ngay sau đổi eid trong khe,
   `warm` False ở 3 nến đầu (VCL_WARM − 1) rồi True. Eid xuất hiện lại sau khi biến mất ⇒ `raise`.
5. **Khoá chiều (tổng hợp, dùng `test_b_v2._pattern` — mẫu BUY, giá đi xuống tới Z):** `extra = {'VCL_S1': (Z, 'VCL', None, (-1,))}` ⇒ đúng 1 lệnh
   BUY, `zone == 'VCL_S1'`; `{'VCL_R1': (Z, 'VCL', None, (1,))}` ⇒ 0 lệnh; `{'VCL_R1': (Z, 'VCL', None, None)}` ⇒ 1 lệnh (chứng minh chính `mdirs`
   chặn). Warm False ở một nến cụm ⇒ 0 lệnh.
6. **Ưu tiên giữa họ (tổng hợp):** POC_D = PDH = cạnh VCL_S1 cùng giá ⇒ 1 lệnh, `ztype == 'POC_D'`, `zones_hit == ['POC_D','PDH','VCL_S1']`.
   3 ca hợp lệ cùng phiên trên VCL_S1/S2/S3 ⇒ giữ 2 (trần chung loại VCL); thêm 1 ca PDL cùng phiên ⇒ lệnh thứ 3 có (khác loại).
7. **Không nhìn trước (cắt dữ liệu):** dùng lát dữ liệu như `test_lan_cham._slice()` (đầu file 90d) để engine VCL chạy nhanh. Cắt tại ≥ 4 vị trí: giữa
   phiên, nến thứ 5 sau đổi tuần, ngay sau 19:00 VN, giữa một cụm của một lệnh VCL thật trong lát (nếu lát không có lệnh VCL ⇒ chọn nến có
   `runlen` vừa đạt 4). Với mỗi i: `rec_c = vcl5.run_engine(vcl5.prepare(cut))['rec']`; `dfc` như v2 test 3 (**sao chép cờ `thin` từ bản đầy đủ**);
   `zone_table3(build_extra3(dfc, …, rec_c))` `allclose(equal_nan)` với bản đầy đủ (lát) trên [0, i] — gồm cả runlen/eid; `detect(prepare(dfc, …))`
   trả đúng các lệnh idx ≤ i của bản đầy đủ (so idx/side/sl/tp/zone).
8. **PDH/PDL (tổng hợp):** 4 phiên, phiên 2 ngắn < 300 nến ⇒ phiên 3 lấy PDH/PDL của phiên 1; phiên đầu NaN; giá trị = max high / min low đúng phiên q.
9. **Dời:** `shifted3(δ=0)` ⇒ detect y hệt; δ ≠ 0 ⇒ mọi mảng (VWAP, v2, PDH/PDL, VCL) = thật + δ[sno]; `warm` và `mdirs` không đổi (so `is`/`array_equal`).
10. **ĐC2:** sau `_patched_map(zone_table3 cols)`, mọi nến đối chứng của một lệnh VCL SELL chạm ít nhất một cạnh `VCL_Rk` đang ấm; `VCL_R_ANY` NaN
    đúng khi không cạnh nào chạm; sau `with` `K.ZONE_NAME2COL` trở về như cũ.
11. **Căn hàng:** `check_align` qua trên D90; df giả lệch 1 nến ⇒ `AssertionError`.
12. **Hồi quy:** `pytest test_kernel.py test_b_v2.py` vẫn xanh (2-tuple cũ vẫn chạy; `_synth_P` dựng tay vẫn chạy nhờ `P.get('mdir', {})`).

---

## 5. RỦI RO / ĐIỂM MƠ HỒ — người làm báo lại từng mục

1. **Kết quả ≈ đối chứng** là khả năng cao nhất. Viết thẳng 3.5-1; **không** viết "S/R của VCL giúp B tốt hơn".
2. **VCL áp đảo:** VCL sát giá liên tục ⇒ lệnh chỉ-v3 gần như toàn VCL; PDHL n ≈ 0 ⇒ hàng 8 "không áp dụng". Bình thường, báo đúng vậy.
3. **Trần 2/phiên cho cả 14 cạnh VCL** sẽ cắt nhiều lệnh thô — đây là luật đã chốt, không nới. Báo số bị cắt; lệnh giữ = 2 lệnh SỚM nhất phiên.
4. **Bẫy n của ĐC1** (3.4) — chỉ phán quyết trên WR/R mỗi lệnh. Không diễn giải "n thật > n dời" thành "vùng thật hút giá".
5. **Cạnh trôi trong eid** (p90 1,75 giá): cụm có thể "chạm" vì cạnh trôi về phía giá. Báo tỉ lệ lệnh VCL mà |lo(i−1) − lo(i−N)| > 0,5 giá; chỉ mô tả.
6. **Cache VCL** phải là bản v5 trên 90d (BASE90). Nếu `load_rec` phải chạy lại engine ⇒ ghi thời gian + md5 mới; kết quả VCL vòng trước dùng cùng cache.
7. **Ca chưa phủ** (vd K_VCL > 7, eid đứt quãng, căn hàng lệch, PDH NaN giữa phiên) ⇒ **dừng và hỏi**, không tự chế luật.
8. Không chạy file 2 năm, không port C# (`BenzoDetectors.cs`) — chỉ khi đạt 3.5-3 và người học duyệt số.

---

## 6. BÁO CÁO CUỐI — `report/_eval_b_v3.txt` (tiếng Việt, không thuật ngữ lạ)

**Đúng MỘT bảng**, hàng = phiên bản setup, cột = số lệnh | winrate (TP 3R, hoà vốn ~27 %):

| Phiên bản setup | Số lệnh (lệnh/ngày) | Winrate |
|---|---|---|
| B cũ — 2 VWAP | 11 (0,18) | 27,3 % |
| B v2 — 8 loại vùng | 25 (0,41) | 32,0 % |
| **B v3 — v2 + đỉnh/đáy phiên trước + Vùng Canh Lệnh** | … | … |
| — trong đó lệnh chỉ có ở v3 | … | … |
| Chỉ S/R (đỉnh/đáy phiên trước + VCL, không vùng v2) | … | … |
| Chỉ Vùng Canh Lệnh | … | … |
| Chỉ đỉnh/đáy phiên trước | … | … |
| B v2 + Vùng Canh Lệnh | … | … |
| B v2 + đỉnh/đáy phiên trước | … | … |
| B v3 bỏ VWAP_W / VWAP_D / POC_D / VAH_D / VAL_D / HVN_D / POC_W / HVN_W (8 hàng) | … | … |
| B v3 trên bản đồ vùng DỜI 3–15 giá (100 bản): trung bình [5 %–95 %] | … (chỉ tham khảo) | … [… – …] |

Dưới bảng, tối đa 4 dòng: (1) R TB B v3 kèm TRAIN/TEST; (2) phán quyết ĐC1 + ĐC2 cho B v3 và nhóm chỉ-v3; (3) chênh WR nhỏ nhất thấy được với
n này; (4) kết luận 3.5 — câu bắt buộc nếu không đạt 3.5-3(d): **"chưa có lợi thế đo được trên 61 phiên"**.
`RESULTS-B-v3.md` chứa đầy đủ các bảng mục 3 (cùng bố cục RESULTS-B-v2.md) + phụ lục.

---

## 7. GIAO NỘP + THỨ TỰ COMMIT (mỗi commit: `git push origin main`, báo hash; chỉ `git add` đúng file của mình)

1. Commit 1: fixture `_b_v2_idx.json` (ghi từ code CHƯA sửa, mục 2.0) + 2 sửa `setup_b_hap_thu.py` + `zones_b_v3.py` + `test_b_v3.py`
   (test 1–6, 8–12 xanh) + `test_b_v2.py`/`test_kernel.py` vẫn xanh.
2. Commit 2: `setup_b_v3.py` với hằng số + kỳ vọng 3.6 ghi sẵn, **chưa có kết quả**.
3. Chạy; test 7 (cắt dữ liệu) xanh; commit 3: `report/RESULTS-B-v3.md`, `report/_eval_b_v3.txt`, `report/img/b_v3_*.png`.
