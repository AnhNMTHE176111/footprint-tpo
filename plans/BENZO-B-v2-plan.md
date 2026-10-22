# BENZO-B-v2 — Setup B "Hấp thụ": mở từ 2 vùng VWAP lên 8 loại vùng (HVN/POC/VAH/VAL ngày + tuần)

Fable viết 2026-10-22, **chỉ đặc tả, không code**. Người làm theo: đọc `benzo-trader/research/setup_b_hap_thu.py` (thuật toán B hiện
tại, hàm `prepare` + `detect`), `kernel.py` (`_zones`, `_Ctx.week_hvn`, `zone_columns`, `control_sample`, `simulate`),
`zones_a_v4.py` (đã dựng mảng HVN_W/HVN_D/VAH_D/VAL_D theo nến cho A-v4 — **tái dùng**), `report/RESULTS-B.md` (vòng 1–2),
`report/BENZO-VCL.md` mục 0 (quy tắc đăng ký trước + đối chứng dời), `plans/BENZO-A-V4-plan.md` mục 2.1 + 3.3.

**Dữ liệu (QĐ-6):** CHỈ `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d{.csv,_bars.csv}` (= biến `D90`).
**KHÔNG chạy file 2 năm.** TRAIN = phiên ≤ 2026-09-15 (35 phiên sạch), TEST từ 2026-09-16 (26). 61 phiên sạch ⇒ chia "lệnh/ngày" cho 61.
Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL; 1 lệnh mở cùng lúc (`kernel.simulate`). 1 giá = 1 USD = 10 tick.

**Thuật ngữ:** *look-ahead* = nhìn trước (dùng số liệu chưa có tại thời điểm xét) · *bootstrap* = lấy mẫu lại có hoàn lại để ước khoảng
tin cậy (KTC) · *leave-one-out* = bỏ-một-vùng (chạy lại thiếu đúng một loại vùng để đo đóng góp của nó) · *parity* = khớp kết quả giữa hai bản cài.

---

## 0. Bối cảnh và kết quả đã biết (đọc trước khi mong đợi gì)

- B ô chính hiện tại (θ 0,5 · N 3 · TP 3R · 2 vùng VWAP tuần/ngày · mọi pha trừ OFF) trên 90d: **n = 11, WR 27,3 %, R TB 0,00**
  (RESULTS-B vòng 1; BENZO-VCL mục 1 đã tái tạo được). Đối chứng cùng vùng/chế độ: WR 27,8 %, R TB 0,00 ⇒ **≈ đối chứng**.
- HVN đã đo 474 phiên: **không phải mốc phản ứng** (`memory/hvn-khong-phai-moc-phan-ung.md`). VCL 5 vòng + SR-KET-QUA: **vị trí vùng không
  mang thông tin; xác suất chạm chỉ phụ thuộc khoảng cách** ⇒ mọi phép đo vùng mới **bắt buộc có đối chứng khớp khoảng cách** (mục 3.4).
- Vì vậy kỳ vọng hợp lý cho vòng này: **n tăng gần như chắc chắn, WR trôi về ~27 % (hoà vốn 3R)**, tức B v2 ≈ B cũ chạy ở nhiều chỗ hơn.
  Vòng này đo để **xác nhận hoặc bác** điều đó bằng số, không phải để "tìm cho ra" vùng tốt.

### 0.1 Trả lời câu hỏi: kernel đã có cột HVN/VAH/VAL/POC ngày/tuần chưa, có nhìn trước không?

| Thứ cần | Đã có ở đâu | Nhìn trước? |
|---|---|---|
| VAH_D / VAL_D / POC_D (**phiên đầy đủ gần nhất trước đó**, ≥ 300 nến, VA 70 % trên profile hàng 0,2 giá) | `kernel.zone_columns` cột `yd_vah / yd_val / yd_poc` — **cột theo nến, hằng suốt phiên** | KHÔNG (chỉ profile phiên đã đóng; `test_b_no_lookahead_zones` đã kiểm) |
| HVN_D (≤ 3, từ cùng profile hôm qua, cổng ×2,5) | `kernel._zones(...)['hvn_day']` (dict theo phiên, **chưa phải cột**); `zones_a_v4.build_zones` đã trải thành mảng `HVN_D1..3` | KHÔNG |
| HVN_W (≤ 3, gộp **3 tuần CME đã đóng** W−3..W−1, cổng ×2,5) | `kernel._Ctx.week_hvn` → `['hvn_week']['hvn']`; `zones_a_v4` trải thành `HVN_W1..3` (kèm dải; B v2 dùng **điểm đỉnh**) | KHÔNG (chỉ tuần `≤ W−1`). ⚠ không loại phiên `thin` (tuần đầu file mỏng) ⇒ cờ `partial`; báo số phiên bị ảnh hưởng |
| POC_W | **CHƯA CÓ** ở đâu cả — phải viết mới (mục 1.2) | — |
| VWAP_D / VWAP_W | `vwap_series` — cộng dồn **gồm nến hiện tại đã đóng** | KHÔNG |

Hai cờ hậu cần có nhìn trước nhẹ nhưng **chỉ để lọc dữ liệu, không phải tín hiệu**: `thin` (trung vị volume phiên tính trên cả file) và `splice`
(nhìn ±2 phiên quanh chỗ nối). Giữ nguyên; test cắt dữ liệu phải **sao chép cờ `thin` từ bản đầy đủ** (mục 4.3) chứ không tính lại.

---

## 1. TẬP VÙNG B v2 — 8 loại, tối đa 12 mức giá mỗi phiên

### 1.1 Bảng định nghĩa (giá trị tại nến i, mọi mức tính **chỉ từ nến ≤ i**)

| Mã (ztype) | Mức (name) | Nguồn | Cập nhật | Sẵn sàng từ | Ghi chú |
|---|---|---|---|---|---|
| `VWAP_W` | VWAP_W | `zc['vwap_w']` | động, mỗi nến | tuần đã ≥ 30 nến (`WARM`) | như B cũ |
| `VWAP_D` | VWAP_D | `zc['vwap_d']` | động | phiên đã ≥ 30 nến | như B cũ |
| `POC_D` | POC_D | `zc['yd_poc']` | cố định trong phiên | nến đầu phiên | POC phiên đầy đủ gần nhất trước đó |
| `VAH_D` | VAH_D | `zc['yd_vah']` | cố định | nến đầu phiên | |
| `VAL_D` | VAL_D | `zc['yd_val']` | cố định | nến đầu phiên | |
| `HVN_D` | HVN_D1..3 | `_zones['hvn_day']` (= `zones_a_v4.session_levels[s]['hvn_d']`) | cố định | nến đầu phiên | điểm; thứ tự = mạnh trước |
| `HVN_W` | HVN_W1..3 | `_zones['hvn_week']['hvn']` (= `session_levels[s]['hvn_w'][k][0]` — **lấy đỉnh, bỏ dải**) | cố định | nến đầu phiên | điểm |
| `POC_W` | POC_W | **mới**: POC của profile gộp **các phiên thuộc tuần CME W−1** (tuần đã đóng ngay trước), chỉ phiên ≥ 300 nến, **không thin**, sau chỗ nối; cần ≥ 3 phiên, không thì NaN | cố định | nến đầu phiên | xem 1.2 |

**"Ngày" = phiên CME đầy đủ gần nhất đã đóng, "tuần" = tuần CME đã đóng** (khoảng trống > 30 giờ tách tuần, `week_no`). Đây là lựa chọn
(a) giống A-v4 mục 2.1: **không dùng** VA/POC *đang hình thành* của phiên/tuần hiện tại làm vùng chính, vì (i) 1–2 giờ đầu phiên các mức này nhảy
hàng chục tick mỗi nến, "cụm hấp thụ tại Z" trên mức đang nhảy không có nghĩa; (ii) tránh hẳn mọi tranh cãi rò rỉ. Biến thể *đang hình thành*
(`POC_D_DEV/VAH_D_DEV/VAL_D_DEV`, tính tại nến cuối mỗi M5 đã đóng, chỉ khi phiên ≥ 120 nến — `zones_a_v4.dev_va` đã có, chỉ cần trả thêm POC) **đo thêm
như chỉ báo nếu còn thời gian, in bảng, không chọn**.

**Vùng là ĐIỂM, không có dải.** B đã có dung sai chạm riêng `TOUCH_TOL = 1,0` giá (|close − Z| ≤ 1 hoặc râu chạm) và `EXT_TOL = 0,5`; SL của B neo vào
**cực trị cụm**, không vào mép vùng ⇒ không cần dải như A-v4. HVN_W dùng đỉnh (`hvn_w[k][0]`), không dùng `lo/hi` của `peak_sharpness`.

### 1.2 POC_W — định nghĩa chọn và lý do

Hai cách hiểu "POC tuần": (A) POC của **profile 1 tuần đã đóng gần nhất** (= POC của profile tuần trên mọi phần mềm, dời sang tuần sau);
(B) POC của **profile gộp 3 tuần** (cùng profile `week_hvn`). Chọn **(A)** vì (B) gần như luôn trùng HVN_W1 (đỉnh làm mượt mạnh nhất ≈ hàng volume
thô lớn nhất) ⇒ không thêm thông tin, chỉ thêm trùng lặp. Báo thêm khoảng cách |POC_W − HVN_W1| để người học thấy.

Cài: hàm `week_poc(ctx, sno, sp)` trong file mới `zones_b_v2.py`, **sao chép** cách chọn phiên của `kernel._Ctx.week_hvn` nhưng `wk == W−1`
(thay vì `W−3..W−1`), thêm điều kiện `~st['thin']`, gộp bằng `kernel._agg_profiles`, lấy `kernel.value_area(...)[0]`. Thiếu phiên (< 3) ⇒ NaN.
Tuần đầu tiên của file không có tuần trước ⇒ NaN; tuần thứ hai dựng trên tuần 07-23…07-28 (mỏng, thin) ⇒ **NaN theo luật trên**. Báo số phiên có POC_W.

### 1.3 Không nhìn trước — cam kết từng loại

- Cố định (POC/VAH/VAL/HVN ngày, HVN/POC tuần): giá trị **gán từ nến đầu phiên** = kết quả của phiên/tuần **đã đóng trước đó**, không đổi trong phiên.
  Kiểm bằng test cắt dữ liệu (mục 4.3) — mảng trên `df[:i+1]` phải `allclose` với mảng đầy đủ trên `[0, i]`.
- Động (VWAP): gồm nến i (đã đóng). `detect` dùng `zv[i−1]` làm Z của cụm và `touch` dịch `j` nến — giữ nguyên.
- Thin/splice: như 0.1.

### 1.4 Nhiều vùng gần nhau / chồng nhau — luật xử lý (không gộp giá)

Tỉ lệ trùng sẽ cao (POC_D ≈ HVN_D1; VAH_D/VAL_D có thể = HVN_D2; VWAP_W ≈ HVN_W). Luật:

1. **Không gộp mức.** Mỗi mức giữ tên riêng để tách đóng góp được; "gần nhau" xử lý ở bước lệnh.
2. **Một nến xác nhận i ⇒ tối đa một lệnh.** `detect` duyệt vùng theo **thứ tự ưu tiên cố định**
   `VWAP_W, VWAP_D, POC_D, VAH_D, VAL_D, HVN_D1, HVN_D2, HVN_D3, POC_W, HVN_W1, HVN_W2, HVN_W3`; vùng đầu tiên khớp tại i thắng (`found[i]` như code
   hiện tại). Thứ tự VWAP trước là **cố ý**: bảo đảm *tập lệnh thô của B cũ là tập con của B v2* (mục 3.2 cần tính chất này). Lệnh ghi thêm
   `zones_hit = [mọi mức khớp tại i]` (để báo "bất kỳ vùng" ở 3.3) và `n_hit = len(zones_hit)`.
3. **Trần 2 lệnh / (ztype, phiên)** — khoá theo **loại** (`ztype`), không theo tên mức (nếu khoá theo tên, HVN_D1..3 cho 6 lệnh/phiên). Với
   VWAP `ztype == name` ⇒ bản cũ không đổi.
4. `one_at_a_time` của `simulate` giữ nguyên ⇒ lệnh ở vùng mới có thể **chặn** lệnh VWAP cũ mở sau nó. Báo số lệnh cũ bị chặn (3.2).
5. Báo **tỉ lệ trùng**: với mỗi phiên sạch, số cặp (mức, mức khác loại) cách nhau ≤ 1 giá / tổng số mức; và bảng khoảng cách trung vị giữa các loại.

### 1.5 Nối hợp đồng

File 90d là **GCZ26 một hợp đồng** ⇒ `df['splice_jump'].any()` phải là `False` — **assert** ngay khi nạp, in ra báo cáo. Nếu sau này chạy file
nối: `prepare` đã loại cả tuần có chỗ nối (`bad_w`), `week_hvn`/`week_poc` đã chỉ lấy phiên sau `sp = last_splice`, `_zones['yday']` đã bỏ qua phiên trước
chỗ nối (`q >= sp`). Không thêm gì.

---

## 2. THAY ĐỔI CODE — ít xâm lấn nhất

**Nguyên tắc:** không sửa `kernel.py`; sửa `setup_b_hap_thu.py` đúng 3 chỗ (giữ nguyên mọi hằng số, `main()`, vòng 2, file 2 năm); việc mới nằm ở
hai file mới. Sau sửa, chạy lại ô chính B cũ phải ra **đúng n = 11 / 27,3 % / 0,00** (test 4.1) trước khi chạy bất kỳ bảng nào.

### 2.1 `setup_b_hap_thu.py` — 3 sửa

1. `prepare(df, prof, extra_zones=None)`: thêm tham số `extra_zones: dict name → (mảng giá theo nến, ztype)`; nếu có, với mỗi mục:
   `P['Z'][name] = arr`, `P['touch'][name]` tính **cùng công thức** hiện có, `P['warm'][name] = np.ones(n, bool)` (vùng cố định sẵn từ đầu phiên),
   `P['ztype'][name] = ztype`. Với hai VWAP `P['ztype'] = {'VWAP_W': 'VWAP_W', 'VWAP_D': 'VWAP_D'}`. `P['Z']` phải là dict **giữ thứ tự chèn**
   (VWAP_W, VWAP_D trước, rồi extra theo thứ tự 1.4).
2. `detect(...)`: dòng `for name in ('VWAP_W', 'VWAP_D'):` ⇒ `for name in P['Z']:` (vẫn `if name not in zones: continue`). Entry thêm
   `ztype=P['ztype'][name]`, `zones_hit` (danh sách tên mức khớp tại i — thu bằng cách **không** `continue` khi `i in found` mà `found[i]['zones_hit'].append(name)`;
   lệnh đầu vẫn giữ). Trần cuối hàm: khoá `k = (e['ztype'], sno)` thay cho `(e['zone'], sno)`.
3. `detect2` (H2, vòng 2) — **không đụng** (không dùng trong vòng này). `run_cell`, `main_r1`, `main` — không đụng; default `zones=('VWAP_W','VWAP_D')`
   và `extra_zones=None` giữ hành vi cũ y nguyên.

Tổng cộng ~15 dòng thay đổi. Bất kỳ đổi hằng số nào (`MOVE_MIN, LOOKBACK, TOUCH_TOL, EXT_TOL, WARM, BIG_EXCL, RR, MAX_PER_ZONE_SESSION, THETAS, NS, MAIN`)
đều **cấm** trong vòng này.

### 2.2 `research/zones_b_v2.py` (mới, ~80 dòng)

```
ZONE_ORDER  = ('VWAP_W','VWAP_D','POC_D','VAH_D','VAL_D','HVN_D1','HVN_D2','HVN_D3','POC_W','HVN_W1','HVN_W2','HVN_W3')
ZTYPE_OF    = {name → ztype}   # HVN_D1..3 → 'HVN_D', HVN_W1..3 → 'HVN_W', còn lại = chính nó
ZTYPES_NEW  = ('POC_D','VAH_D','VAL_D','HVN_D','HVN_W','POC_W')
ZONES_OLD   = ('VWAP_W','VWAP_D');  ZONES_V2 = ZONE_ORDER
MIN_WEEK_SESSIONS = 3            # POC_W cần ≥ 3 phiên đầy đủ, không thin, trong tuần W−1

week_poc(ctx, sno, sp)               -> float | nan            (mục 1.2)
build_extra(df, prof, ctx=None)      -> dict name → (arr, ztype)   # dùng zones_a_v4.session_levels cho HVN_D/HVN_W/VAH/VAL,
                                                                 # zc['yd_poc'] cho POC_D, week_poc cho POC_W; trải theo phiên
zone_table(extra)                    -> DataFrame cột = name     (cho test cắt + đối chứng)
shifted(extra, P_or_zc, delta_by_sno)-> dict name → arr + δ[sno] (gồm cả VWAP: zc + δ)
overlap_stats(extra, zc, st)         -> dict (tỉ lệ cặp ≤ 1 giá, trung vị khoảng cách giữa loại, số phiên có từng mức)
```

### 2.3 `research/setup_b_v2.py` (mới) — toàn bộ pipeline đo, ghi `report/RESULTS-B-V2.md`

Hằng số ở đầu file, **commit trước khi chạy lần đầu**:
`MAIN = (0.5, 3)` · `RR = 3.0` · `SHIFT_LO, SHIFT_HI, REPS, SHIFT_SEED = 3.0, 15.0, 100, 20261024` (cùng ma trận δ với BENZO-VCL/A-v4) ·
`CTRL_DRAWS = 200` · `BOOT, BOOT_SEED = 10000, 0` · `MIN_N = 10` · `EXPECT_OLD = (11, 0.273, 0.00)` · `EXPECT_N_NEW = (20, 60)` (kỳ vọng đăng ký, mục 3.6).

Đối chứng "vào ngẫu nhiên tại vùng" (3.4-ĐC2) cần `kernel.control_sample` nhìn thấy cột vùng mới: `control_sample` tra `K.ZONE_NAME2COL` (biến module).
**Không sửa kernel**: trong `setup_b_v2.py` viết context manager `_patched_map(extra)` tạm `update` `K.ZONE_NAME2COL` với `{name: name}` và truyền
`zcols = pd.concat([zc, zone_table(extra)], axis=1)`; `finally` khôi phục dict cũ. Entry truyền vào có `zone = name` (tên mức, vd `HVN_D2`) ⇒ nến đối chứng
phải thoả |close − mức| ≤ 1 hoặc râu chạm **đúng mức đó** (đây chính là "khớp khoảng cách": lệnh thật và đối chứng đều ở khoảng cách ≤ 1 giá tới mức).

---

## 3. PHÉP ĐO — công bằng, tách đóng góp, đối chứng

Mọi bảng cùng cấu hình **θ 0,5 · N 3 · TP 3R · mono 'ends' · variant 'base' · bias False · mọi pha trừ OFF** (= ô chính vòng 1). Không chạy lưới θ×N
cho vùng mới (tránh chọn ô đẹp); lưới chỉ in **một** bảng độ nhạy 3×3 cho bản 8 vùng ở phụ lục, không chọn lại.

### 3.1 Bảng chính (bắt buộc)

| Cấu hình | Vùng | Mục đích |
|---|---|---|
| **B-cũ** | VWAP_W + VWAP_D | mốc, phải = 11 / 27,3 % / 0,00 |
| **B-v2** | 12 mức / 8 loại | bản đề xuất |
| B-mới-thôi | 6 loại mới, **không** VWAP | vùng mới tự đứng được không |
| B-cũ + k (6 bản) | VWAP + đúng một loại mới k | đóng góp **thêm-một** |
| B-v2 − k (6 bản) | 8 loại bỏ đúng loại k | đóng góp **bỏ-một** |

Mỗi hàng báo: n đã đóng · lệnh/ngày (÷ 61) · WR · R TB · KTC 95 % bootstrap (10 000, seed 0) · kỳ vọng giá/lệnh · tổng R · chuỗi thua · TRAIN n/WR/R ·
TEST n/WR/R · T8/T9/T10 (T8 gồm 29–31/7) · theo pha A/EU/US · BUY/SELL.
**Hàng cũ và hàng v2 đặt cạnh nhau, cột WR in đậm** — đây là hai con số người học hỏi.

### 3.2 Tách đóng góp ở mức LỆNH (không chỉ ở mức tổng)

Trước `simulate`, lấy `E_old = detect(zones=ZONES_OLD)`, `E_v2 = detect(zones=ZONES_V2)`; **assert** `{idx của E_old} ⊆ {idx của E_v2}` và các entry chung
có cùng side/entry/sl/tp (tính chất của thứ tự ưu tiên 1.4). Sau `simulate`:
- **Lệnh chung** (idx có ở cả hai bản đã mô phỏng): n, WR, R.
- **Lệnh chỉ-v2** (có ở v2, không ở cũ): n, WR, R — **đây là nhóm quyết định**: vùng mới có thêm lệnh *tốt* hay chỉ thêm lệnh.
- **Lệnh cũ bị mất** ở v2 (bị `one_at_a_time` chặn bởi lệnh vùng mới mở trước): n và R của chúng trong bản cũ.
- Theo loại vùng (ztype của lệnh v2): n, WR, R, **cả hai cách đếm**: *vùng thắng* (ztype ghi trên lệnh) và *bất kỳ vùng* (lệnh tính cho mọi mức trong
  `zones_hit`; tổng > n — ghi rõ). Loại n < 10 ⇒ chỉ in số, **không bình luận**.
- Phân phối `n_hit` (1 / 2 / ≥ 3 mức cùng khớp) và R theo `n_hit` — "hợp lưu" chỉ mô tả, không lọc.
- Phễu `funnel` của `detect` cho B-cũ và B-v2 cạnh nhau (bước 1→7) để thấy vùng mới mở rộng ở bước nào.

### 3.3 Công suất thống kê — in TRƯỚC bảng chính

Sai số WR ≈ √(p(1−p)/n): n = 11 ⇒ ±13,4 điểm; n = 40 ⇒ ±7; n = 60 ⇒ ±5,7. Chênh WR nhỏ nhất phát hiện được (80 %, hai phía) giữa B-cũ (n=11) và
B-v2 (n≈50) ≈ 2,8 × 0,45 × √(1/11 + 1/50) ≈ **42 điểm** ⇒ **so WR cũ↔mới trực tiếp gần như vô nghĩa**; phán quyết phải dựa vào (i) B-v2 so với
*dải 100 bản dời* và (ii) *lệnh chỉ-v2* so với hoà vốn 27 % + đối chứng. R TB: hiệu nhỏ nhất ≈ 2,8 × σ_R(≈1,3) × √(1/n₁+1/n₂) — in theo n thật.

### 3.4 Đối chứng (bắt buộc; dùng chung ma trận δ với BENZO-VCL/A-v4)

- **ĐC1 — dời bản đồ vùng, giữ hình dạng tín hiệu:** mọi mức của phiên (12 mức, **kể cả VWAP động: cộng hằng δ**) dời cùng δ[phiên, bản],
  |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, **100 bản, seed 20261024** (ma trận `(nS, REPS)` sinh y hệt `benzo_vcl.Data`). Chạy **nguyên** `detect` + `simulate`
  trên mảng dời (dùng `prepare(extra_zones=shifted(...))`; `touch` tính lại; các bộ lọc chế độ/VA Âu/IB **không** dời vì là lọc bối cảnh, không phải vùng).
  Trả cho B-cũ **và** B-v2: dải 5–95 % và TB của n, WR, R TB (toàn bộ, TRAIN, TEST, từng tháng). Đây là đối chứng **khớp khoảng cách theo xây dựng**:
  lệnh trên vùng dời cũng chạm vùng (dời) ≤ 1 giá, cùng cơ chế move→cụm→CF; chỉ **vị trí** khác. Thật ≈ dải dời ⇒ vị trí vùng không mang thông tin.
- **ĐC2 — vào ngẫu nhiên tại đúng vùng, cùng chế độ:** `kernel.control_sample` (không sửa) qua `_patched_map` (2.3); mỗi lệnh thật rút 1 nến cùng
  **mức** (|close − mức| ≤ 1 hoặc râu chạm), cùng chế độ kernel, cùng chiều, cùng R:R, SL = râu nến + 0,3; 200 lần; như RESULTS-B. Trả lời: cụm hấp thụ +
  CF thêm gì so với vào bừa tại cùng mức. Làm cho B-cũ, B-v2, và riêng nhóm **lệnh chỉ-v2**.
- **ĐC3 — chỉ-VWAP vs 8 vùng** = chính bảng 3.1 + 3.2 (hàng B-cũ vs B-v2, nhóm lệnh chỉ-v2).

**Ngưỡng "khác đối chứng" — NGUYÊN `PLAN-LAN-CHAM.md` mục 5 (đăng ký trước, không đổi):** thật nằm ngoài dải 5–95 % của đối chứng ở **cả TRAIN và TEST**,
cùng dấu, cùng dấu ở ≥ 2/3 tháng, VÀ |hiệu| > 2 sai số ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". **Chỉ áp dụng khi nhóm có ≥ 10 lệnh ở cả TRAIN và TEST**,
không thì ghi "không áp dụng (n nhỏ)" — không dùng chữ "có xu hướng".

Số phép so có phán quyết: B-v2 vs ĐC1, B-v2 vs ĐC2, chỉ-v2 vs ĐC2, 6 thêm-một, 6 bỏ-một ⇒ **15 phép so**. Ở mức 5 % kỳ vọng ~0,75 ô "vượt" do ngẫu nhiên;
ngưỡng nhiều điều kiện chặt hơn 5 %, nhưng **một ô vượt lẻ loi không phải bằng chứng**.

### 3.5 Tiêu chí phán quyết — đăng ký trước

Ba kết luận có thể, theo thứ tự kiểm:

1. **"Chỉ tăng số lượng"** (kỳ vọng mặc định): n(B-v2) > n(B-cũ) **và** B-v2 nằm **trong** dải 5–95 % của ĐC1 về WR và R TB ở TRAIN hoặc TEST,
   **hoặc** nhóm lệnh chỉ-v2 có WR ≤ 27 % + 1 sai số. Câu bắt buộc trong báo cáo: *"Vùng mới cho thêm lệnh nhưng không cho thêm lợi thế đo được; B v2 ≈ B cũ
   chạy ở nhiều chỗ hơn."*
2. **"Tệ đi"**: lệnh chỉ-v2 có R TB < mốc 5 % của ĐC1 hoặc < ĐC2 − 2 sai số ở cả TRAIN và TEST (n ≥ 10 mỗi bên); **hoặc** B-v2 làm mất ≥ 3 lệnh cũ
   thắng do chặn. ⇒ không ship, ghi rõ loại vùng nào kéo xuống (nếu bỏ-một chỉ ra được với n ≥ 10).
3. **"Cải thiện thật"** — **đồng thời**: (a) n(B-v2) ≥ 30 toàn bộ, ≥ 10 ở cả TRAIN và TEST; (b) R TB(B-v2) > 0 ở cả TRAIN và TEST; (c) lệnh chỉ-v2 có
   WR ≥ WR(B-cũ) **và** R TB > 0 ở cả TRAIN và TEST; (d) B-v2 **vượt ĐC1 và ĐC2** theo ngưỡng 3.4; (e) không loại vùng nào (n ≥ 10) có R TB < −0,5 mà việc bỏ nó
   làm tổng tốt lên quá 2 sai số (nếu có ⇒ "tập 8 vùng chưa đúng", không phải "có cải thiện").
   Với 61 phiên, (d) gần như chỉ đạt khi hiệu ≥ ~0,6R — nói rõ trong báo cáo. Đạt (a)(b)(c) nhưng trượt (d) ⇒ ghi **"ứng viên, chưa có lợi thế đo được;
   cần ≥ 3 tháng dữ liệu mới"**, không ghi "cải thiện".

### 3.6 Kỳ vọng trung thực đăng ký trước (ghi vào đầu `RESULTS-B-V2.md` trước khi chạy)

- n: 11 → **20–60** (6 loại mới, nhưng HVN_W/POC_W thường cách giá 20–80 giá ⇒ ít chạm; POC_D/VAH/VAL/HVN_D gần giá hơn ⇒ đóng góp chính).
  n không tăng ≥ 2× ⇒ bộ lọc cụm/θ đang là nút thắt, không phải vùng — vẫn báo.
- WR ở 3R: **25–35 %** (hoà vốn 27 %). Kỳ vọng hợp lý: **B-v2 ≈ dải ĐC1**.
- Không ép: không chọn ô độ nhạy đẹp; TP 2R không gộp vào kết luận; không thêm bộ lọc mới giữa chừng.

### 3.7 Ví dụ để soi chart

5 lệnh thắng + 5 thua của **nhóm chỉ-v2** (chọn cách đều theo thời gian, deterministic) kèm UTC/VN, loại vùng, Z, `zones_hit`, move, |Δ_CF|/max, SL/TP.
Vẽ bằng `_plot_run.py`, lưu `report/img/b_v2_*.png`. Mục đích: người học soi xem "hấp thụ tại POC hôm qua" trông có đúng ý họ không.

### 3.8 Thời gian chạy

`prepare` 1 lần (~10 s). `detect` 8 vùng ≈ 2–5 s ⇒ 15 cấu hình < 1 phút; ĐC1 100 bản × 2 cấu hình ≈ 10–15 phút; ĐC2 200 lần × 3 nhóm ≈ 2 phút.
Mục tiêu toàn bộ ≤ 20 phút; vượt ⇒ giảm REPS xuống 50 và **ghi rõ**. Không chạy 2 năm.

---

## 4. KẾ HOẠCH TEST — `research/test_b_v2.py` (pytest, chạy trước khi sinh báo cáo)

1. **Tái tạo gốc:** `setup_b_hap_thu.detect(P, 0.5, 3)` + `simulate` trên D90 ⇒ **n = 11, WR 27,3 %, R TB 0,00 (±0,005)** và danh sách `idx` khớp fixture
   `report/_b_old_idx.json` (ghi lần chạy đầu, commit). Lệch ⇒ dừng, báo. Chạy cả với `prepare(extra_zones=None)` lẫn `prepare(extra_zones=build_extra(...))`
   + `zones=ZONES_OLD` ⇒ phải cho cùng kết quả (thêm vùng không được đổi bản cũ).
2. **Tập con:** `idx(E_old) ⊆ idx(E_v2)`; entry chung giống hệt side/entry/sl/tp/zprice. Trần: ≤ 2 lệnh/(ztype, phiên) trong `E_v2` — kiểm bằng groupby.
3. **Không nhìn trước (cắt dữ liệu, mẫu `test_b_no_lookahead_zones`):** ≥ 5 vị trí cắt: giữa phiên, ngay sau đổi tuần (nến thứ 5 của tuần mới), ngay sau
   19:00 VN, cuối phiên, giữa một cụm hấp thụ của lệnh thật. Với mỗi i: `dfc = K._enrich(raw.iloc[:i+1])`, **`dfc['thin'] = df['thin'][:i+1]`** (cờ hậu cần, xem 0.1),
   `profc = build_profiles(dfc, lvc)`; `zone_table(build_extra(dfc, profc))` `allclose` (equal_nan) với bản đầy đủ trên `[0, i]`; và
   `detect(prepare(dfc, profc, extra))` trả **đúng** các entry có idx ≤ i của bản đầy đủ (so idx/side/sl/tp).
4. **POC_W tổng hợp:** df giả 4 tuần (khoảng trống > 30 h giữa tuần), mỗi tuần 4 phiên ≥ 300 nến; tuần 2 dồn volume ở giá X, tuần 3 ở giá Y ⇒ phiên tuần 3
   có `POC_W == X`, tuần 4 có `Y`, tuần 1–2 NaN; thêm một phiên `thin` vào tuần 3 có volume dồn ở Z ⇒ POC_W tuần 4 vẫn là Y (thin bị loại); tuần chỉ 2 phiên ⇒ NaN.
5. **Dedup + trần tổng hợp:** df giả có hai mức khác loại cùng giá (POC_D = HVN_D1) và một ca B hợp lệ ⇒ đúng 1 entry, `ztype == 'POC_D'`, `zones_hit == ['POC_D','HVN_D1']`;
   ba ca hợp lệ cùng phiên trên HVN_D1/HVN_D2/HVN_D3 ⇒ giữ 2.
6. **Dời vùng:** `shifted(extra, δ=0)` ⇒ detect y hệt thật; δ ≠ 0 ⇒ mọi mảng = thật + δ[sno] (gồm VWAP); ma trận δ sinh với seed 20261024 phải
   **bằng** `benzo_vcl.Data().dsh[:, 1:]` (cùng nS, REPS) — assert `allclose`.
7. **Đối chứng ĐC2:** sau `_patched_map`, mọi nến đối chứng của lệnh `zone='HVN_D2'` thoả |close − HVN_D2| ≤ 1 hoặc râu chạm; sau `with` dict `K.ZONE_NAME2COL`
   trở về như cũ (so bản sao).
8. **Hồi quy test cũ:** `pytest research/test_kernel.py` vẫn xanh (kernel không đổi).

---

## 5. RỦI RO / ĐIỂM MƠ HỒ — người làm phải báo lại từng mục

1. **Kết quả ≈ ĐC1** — khả năng cao nhất, khớp mọi phép đo S/R trước. Khi đó viết thẳng kết luận 3.5-1; **không** viết "vùng pro trader tốt hơn VWAP".
2. **n vẫn nhỏ** (< 30) ⇒ phần lớn phán quyết "không áp dụng"; đừng gộp rồi nói về từng loại vùng.
3. **HVN_W/POC_W xa giá** ⇒ n theo loại ≈ 0; tuần 2 của file không có POC_W (tuần 1 thin). Báo số phiên có từng mức và số phiên `hvn_w_partial`.
4. **Thứ tự ưu tiên VWAP-trước** làm thống kê "vùng thắng" nghiêng về VWAP khi trùng; vì vậy bắt buộc in cả "bất kỳ vùng" và bỏ-một. Không đổi sang
   "gần nhất thắng" giữa chừng (mất tính chất tập con).
5. **Chặn lệnh cũ** bởi `one_at_a_time`: nếu B-v2 mất lệnh cũ thắng, tổng có thể xấu đi dù vùng mới vô hại — tách rõ ở 3.2.
6. **Bộ lọc `trend_bad`/`edge_bad`** dùng VA Âu/IB (band chế độ) cho mọi vùng — pha A chế độ `NA` nên không lọc được; như B cũ. Không thêm lọc.
7. **HVN_D/VA của 07-29** dựng trên phiên thin 07-28 (kernel không loại thin ở `yday`) — 1 phiên, ghi chú, không sửa kernel.
8. **Biến thể "đang hình thành"** chỉ làm nếu còn thời gian; nếu làm, in riêng, không trộn vào bảng chính.
9. **Nhiều phép so (15)** ⇒ một ô vượt lẻ không đủ; cần (d) ở 3.5-3 đạt ở cả hai đối chứng.
10. Gặp ca chưa phủ (vd mức NaN giữa phiên, hai mức cùng loại cùng giá) ⇒ **dừng và hỏi**, không tự chế luật.

---

## 6. BÁO CÁO CUỐI CHO NGƯỜI HỌC — `report/_eval_b_v2.txt`, ≤ 12 dòng, tiếng Việt, không thuật ngữ lạ

1. **Số lệnh:** B cũ 11 (0,18/ngày) → B v2 **n** (**x/ngày**); trong đó lệnh chung …, lệnh chỉ-v2 …, lệnh cũ bị chặn ….
2. **WR (TP 3R, hoà vốn 27 %):** 27,3 % → **z %** (sai số ± …); lệnh chỉ-v2: … %.
3. **R TB:** 0,00 → **r** [KTC 95 %]; TRAIN r₁ (n) / TEST r₂ (n).
4. **Đối chứng dời vùng (100 bản):** B v2 nằm trong / ngoài dải 5–95 % (WR …–…, R …–…) — phán quyết theo ngưỡng.
5. **Vào ngẫu nhiên tại cùng mức:** … — phán quyết.
6. **Từng loại vùng:** một dòng mỗi loại có n ≥ 10 (n, WR, R, bỏ-một Δ); loại n < 10 gộp "chưa đủ mẫu".
7. **Công suất:** chênh WR nhỏ nhất thấy được với n này ≈ … điểm ⇒ "chưa thể nói gì về chênh dưới … điểm".
8. **Kết luận 3.5:** chỉ tăng số lượng / tệ đi / cải thiện thật (ứng viên). Câu bắt buộc nếu không đạt 3.5-3(d): **"chưa có lợi thế đo được trên 61 phiên"**.

Không viết "có xu hướng", không chọn ô độ nhạy đẹp, không ép số.

---

## 7. GIAO NỘP + THỨ TỰ COMMIT

1. Commit 1: `zones_b_v2.py` + sửa 3 chỗ `setup_b_hap_thu.py` + `test_b_v2.py` (test 1, 2, 4, 5, 6, 7, 8 xanh) + fixture `_b_old_idx.json`.
2. Commit 2: `setup_b_v2.py` với **hằng số + kỳ vọng 3.6** ghi sẵn, **chưa có kết quả**.
3. Chạy; test 3 (cắt dữ liệu) xanh; commit 3: `report/RESULTS-B-V2.md`, `report/_eval_b_v2.txt`, `report/img/b_v2_*.png`.
4. `git push origin main` sau mỗi commit, báo hash. Không đụng C# (`BenzoDetectors.cs`) trong vòng này — chỉ port khi đạt 3.5-3 và Fable duyệt số.
