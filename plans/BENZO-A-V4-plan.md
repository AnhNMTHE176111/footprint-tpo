# BENZO-A-V4 — Setup A "Phá hồi": tập vùng mới + cú phá có đà (momentum) + bỏ cấm 18:00–19:20

Fable viết 2026-10-22 cho Opus implement + backtest. **Chỉ đặc tả, không code.** Đọc trước: `plans/BENZO-TRADER-plan.md`
(mục 2, 3-A, 4, QĐ-5…8), `benzo-trader/research/setup_a_pha_hoi.py` (thuật toán hiện tại), `kernel.py`, 3 báo cáo vòng cũ
(`report/RESULTS-A.md`, `_round1_A.md`, `_round12_A.md`, `_eval_a_r2.txt`, `_eval_a_r3.txt`, `MO-XE-SL-agent-chinh.md`),
`BenzoDetectors.cs` (DetectorA), `BenzoZones.cs`, `quantower-tpo-suite/ProfileEngine.cs` (FindHvn, PeakSharpness, ZonePolicy),
`SessionZones.cs` (HVN tuần/ngày, VWAP, VAH/VAL hiển thị thế nào), `vung-canh-lenh/PLAN-LAN-CHAM.md` mục 5 (ngưỡng đối chứng),
`vung-canh-lenh/research/report/LAN-CHAM.md` + `benzo-trader/research/report/BENZO-VCL.md` (bài học: "ở vùng" tự nó không có lợi thế).

**Dữ liệu (QĐ-6):** CHỈ `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d{.csv,_bars.csv}`. TRAIN = phiên ≤ 2026-09-15,
TEST từ 2026-09-16. Chi phí 0,2 giá/lệnh; nến chạm cả SL lẫn TP ⇒ SL (`kernel.simulate`). 61 phiên sạch (TRAIN 35 / TEST 26). 1 giá = 1 USD = 10 tick.

**Thuật ngữ dùng trong file:** *momentum* = đà (lực đẩy còn tiếp diễn sau cú phá) · *pullback / retest* = nhịp hồi về cạnh · *armed* = "đã đủ điều kiện
để canh" (tôi dịch là **đã trang bị**) · *look-ahead* = nhìn trước · *bootstrap* = lấy mẫu lại có hoàn lại để ước khoảng tin cậy (KTC) · *parity* = khớp Python ↔ C#.

---

## 0. Bối cảnh ngắn — vì sao làm vòng này

Ba vòng trước (hết hạn 30 nến, hợp lưu, thời gian, tường limit footprint) đều không cứu được A: ô chính V3 **n = 20, WR 10 %, R TB −0,68** (KTC 95 % [−1,09; −0,08]),
đối chứng cùng trạng thái phá −0,14R ⇒ lệnh thật **kém hơn** vào bừa trong cùng trạng thái. Mổ xẻ 18 lệnh SL: 13/18 bị **hồi xuyên** lại cạnh (cú phá không được chấp nhận),
không phải quét râu. Kết luận cũ: lỗi nằm ở **chỗ chọn cạnh** (VA Âu / VA hôm qua không phải cạnh cân bằng thật) và **cú phá quá yếu** (một nến M5 nhích ra ngoài).

Người học chỉ ra hai lỗi mô tả: (1) cạnh phải là **HVN tuần/ngày, VWAP ngày/tuần, VAH/VAL ngày** (vùng trader chuyên nghiệp canh), (2) "một nến M5 đóng ngoài" không phải cú phá —
cú phá thật có **đà đi tiếp**, rồi **đà chậm dần**, rồi mới hồi; và **18:00–19:20 VN không được cấm**.

Lịch sử phải nhớ khi đọc kết quả: HVN đã đo 474 phiên = **không phải mốc phản ứng** (ngang bốc ngẫu nhiên; `memory/hvn-khong-phai-moc-phan-ung.md`); mọi phép đo S/R trong repo
≈ đối chứng (SR-KET-QUA, VCL v2–v5, BENZO-VCL). Vùng mới **không được coi là đã có lợi thế**; vòng này đo xem **cơ chế phá-hồi** trên các vùng đó có khác đối chứng không.

---

## 1. TRẢ LỜI TRUNG THỰC: bản A hiện tại có xử lý "đi tiếp → chậm dần → hồi" không?

**Kết luận: MỘT PHẦN.** Phần theo dõi cực trị đúng; phần hết hạn, hủy, và "nến dài nhất move" sai; không có khái niệm "cú phá có đà". Dẫn chứng từng dòng trong `setup_a_pha_hoi.py` (bản C# `BenzoDetectors.cs` giống hệt, ghi kèm):

| # | Câu hỏi | Trả lời | Dòng |
|---|---|---|---|
| 1 | `pk_pos/pk_val` (cực trị của cú phá) có tiếp tục cập nhật khi giá còn đi xa hơn không? | **CÓ.** Mỗi nến M1 i trong trạng thái: nếu `hi[i] > pk_val` (phá lên) thì `pk_pos, pk_val = i, hi[i]` và `pbmax = 0`. Nhịp hồi đếm `npb = i − 1 − pk_pos`, tức **từ cực trị cuối**, không từ nến phá. Phần này đúng ý người học. | Python 139, 154–155 · C# 120, 142 |
| 2 | `expire` tính từ đâu? | **Từ nến phá `p0`** (nến M1 cuối của nến M5 đóng ngoài), KHÔNG từ cực trị: `q = min(q, p0 + expire + 1)`; C#: `if (i > _st.P0 + Expire) return null`. Hậu quả: cú phá nào có cực trị cuối đặt **sau nến phá hơn 30 nến** thì nhịp hồi + CF rơi ngoài cửa sổ ⇒ **mất hẳn**, dù mọi thứ khác đúng. | Python 118–119 · C# 70 |
| 3 | "Move phá" / `L` / `pbmax` định nghĩa thế nào? | `L` = biên độ lớn nhất của **đoạn lên tới nến phá** (`make_state`: lùi từ `lp` về nến cuối cùng đóng phía trong, tối đa 60 nến; `L = rng[leg].max()`), **không cập nhật** khi giá còn đi tiếp sau `p0`. `pbmax` = biên độ lớn nhất của các nến **sau** cực trị (các nến hồi), reset khi có cực trị mới. Điều kiện hồi hình U: `pbmax < L`. ⇒ Với cú phá đi tiếp dài, `L` lấy nhầm từ đoạn trước nến phá; nến đà lớn nhất (thường nằm **sau** p0) không được tính. | Python 160–166, 122–123, 157 · C# 90–102, 143 |
| 4 | Cú phá có bị hủy khi nến M5 đóng lại trong không? | **CÓ, hủy ngay khi M5 đóng lại trong dù chỉ 1 tick** (`out == 0 ⇒ scan(state, lp); state = None`). CF phải nằm trước nến M1 cuối của nến M5 đó. Không có "độ sâu chấp nhận". | Python 187–193 · C# 78–79 |
| 5 | Có điều kiện "cú phá đủ mạnh / đã trang bị" không? | **KHÔNG.** Một nến M5 đóng ngoài 1 tick là trạng thái phá. Không yêu cầu cực trị cách cạnh tối thiểu. | Python 188, 203–204 |
| 6 | Có dấu hiệu "đà chậm dần" không? | Chỉ gián tiếp: `npb ≥ n_min` (3 nến liền không lập cực trị mới). Không có tiêu chí biên độ/|Δ| giảm, không có "giá rời cực trị ≥ x". | Python 140 |
| 7 | Ca "phá dài 20–40 nến rồi mới hồi" thì sao? | (a) cực trị ở `p0+35`, hồi chạm E ở `p0+45` ⇒ `q` bị kẹp ở `p0+31` ⇒ **không quét tới, mất lệnh**. (b) cực trị ở `p0+20`, chạm ở `p0+28`, CF ở `p0+29` ⇒ được xét, nhưng `L` là của đoạn trước p0 (sai), và nếu bất kỳ nến M5 nào trong 29 nến đó đóng lại trong 1 tick ⇒ đã hủy từ trước. | — |

**Số đo (Fable tự chạy, script tạm `scratchpad/diag_a_momentum.py`, chỉ đọc dữ liệu; Opus phải chạy lại trong backtest và in ra):** trên 61 phiên sạch, với band cũ (VA Âu/IB/VA hôm qua) có **532 trạng thái phá** (mỗi lần M5 đóng ngoài sau khi ở trong = 1).
- Cực trị cuối đặt sau nến phá: **trung vị 7 nến, p75 28, p90 124**; **24 % (130/532) có cực trị sau p0 hơn 30 nến** ⇒ bị `expire=30` cắt.
- Khoảng cách cực trị tới cạnh: trung vị **7,1 giá**, p75 16; chỉ 12 % < 2 giá. Cú phá trên dữ liệu này đi rất xa so với SL 4 giá.
- **91 % (482/532) trạng thái kết thúc vì M5 đóng lại trong**, tuổi thọ trung vị 20 nến; 46 hết phiên; 4 đảo phía.
- 92 % có chạm lại E (|đóng−E| ≤ 1 hoặc râu) trước khi hủy, nhưng **lần chạm đầu trung vị chỉ 2 nến sau nến phá** ⇒ phần lớn "hồi" đo được là giá lắc ngay tại cạnh, không phải quay về sau một nhịp đà. Chỉ 256/532 chạm lại **sau** cực trị cuối. 16 % ca chạm lại lần đầu > 30 nến sau p0 (bị expire bỏ).
- Chỉ 15/532 bị hủy mà chưa từng chạm E (phá hụt thật).

⇒ Người học đúng ở cả hai điểm: thuật toán đo "nhịp hồi" trên những cú nhích 1 tick rồi lắc tại chỗ, và bỏ sót/đo sai những cú phá có đà thật.

---

## 2. ĐẶC TẢ A-v4 (viết để Python và C# cài giống nhau)

Ký hiệu: nến M1 `i` đã đóng, `O,H,L,C,rng=H−L,Δ`. `S ∈ {+1,−1}` chiều phá. Hằng cũ giữ nguyên: `ZONE_HALF = 1,0` (vùng chạm E ± 1), `n_min = 3`, thân CF 0,5, `kernel.confirm_bars`, `kernel.risk` (+0,3; sàn 5 nến; trần 4 giá), TP 3R, ≤ 2 lệnh/(phiên, vùng, chiều), loại 3 nến sau nến dài nhất phiên, pha OFF (04:00–05:00 VN) không vào, phiên `thin/splice` bỏ.

### 2.1 Tập vùng E

Mỗi vùng có **dải `[lo, hi]`** (vùng điểm: `lo = hi`). Giá trị **tại nến i** (không nhìn trước):

| Mã | Nguồn (kernel) | Kiểu | Cập nhật | Dải |
|---|---|---|---|---|
| `VWAP_W` | `vwap_series.vwap_w` (neo tuần CME, khoảng trống > 30 h) | **động** — đổi mỗi nến | mỗi nến | điểm |
| `VWAP_D` | `vwap_series.vwap_d` (neo phiên) | động | mỗi nến | điểm |
| `HVN_W` (≤ 3) | `zones_for_session(...)['hvn_week']['hvn']` — gộp **3 tuần CME đã đóng**, cổng ×2,5, tối đa 3 | cố định trong phiên | đầu phiên | **dải**: `peak_sharpness(profile tuần, đỉnh, 0,9)` (port `ProfileEngine.PeakSharpness`: nới từ đỉnh tới khi volume hàng < 90 % đỉnh), **kẹp rộng ≤ 2,0 giá** đối xứng quanh đỉnh |
| `HVN_D` (≤ 3) | `['hvn_day']` — profile **phiên đầy đủ gần nhất trước đó** (≥ 300 nến), cổng ×2,5, tối đa 3 | cố định | đầu phiên | điểm (như SessionZones B4: HVN ngày = mốc) |
| `VAH_D`, `VAL_D` | `['yday']['vah'/'val']` — VA 70 % của phiên đầy đủ gần nhất trước đó | cố định | đầu phiên | điểm |
| *(chỉ A-v4+)* `VAH_EU`,`VAL_EU` / `IB_H`,`IB_L` | như `band_arrays` hiện tại: pha Mỹ, VA Âu chốt 19:00 VN; chưa có thì IB chốt 20:20 | cố định sau khi chốt | 19:00 / 20:20 | điểm |

**Giải "VAH ngày / VAL ngày":** hai cách hiểu: (a) VA của **phiên CME trước** (hôm qua) — đã có trong kernel (`yday`), là thứ `DailyTpoBias`/syllabus gọi "VA hôm qua", và chính A cũ đã dùng (nguồn `Y`) cho pha Á/Âu;
(b) VA **đang hình thành** của phiên hiện tại tính dồn tới nến i (động như VWAP). Chọn **(a) làm chính**, vì: người học tách bạch "VA ngày" với "cạnh VA Âu" (tức không phải phiên con), và VA đang hình thành
trong 1–2 giờ đầu phiên nhảy hàng chục tick mỗi nến — "phá" nó không có nghĩa. (b) đo **thêm như biến thể chỉ báo** (rẻ: tích luỹ `dict hàng→volume` theo nến, tính VA tại nến cuối mỗi M5, chỉ dùng khi phiên đã ≥ 120 nến) — báo số, **không chọn lại**.
SessionZones trên chart hiện vẽ VAH/VAL của **phiên Âu đã đóng gần nhất** (`ZonePolicy.VaEdgeSessionIndex`, `VaEdgeEuropeOnly = true`) — đó là "cạnh VA Âu" của A-v4+, không phải "VA ngày". Ghi rõ điều này trong README để người học đối chiếu đúng đường trên chart.

**HVN là dải — cạnh nào là E?** Chiều phá quyết định: **phá lên ⇒ E = `hi`** (giá vượt lên trên dải, hồi xuống chạm mép trên); **phá xuống ⇒ E = `lo`**. Mép xa (để tính SL) = mép còn lại. Kẹp rộng ≤ 2 giá vì: SL ≤ 4 giá, SL phải nằm qua mép xa + 1 + 0,3 ⇒ dải rộng hơn 2 giá thì gần như mọi lệnh bị trần 4 giá loại; 2 giá = một nửa ngân sách SL, cùng lý do E = 2 giá của VCL. **Không phải tham số tự do** (dẫn từ trần SL); độ nhạy: HVN_W điểm (lo = hi = đỉnh) báo thêm.

**Không nhìn trước:** HVN_W chỉ từ tuần đã đóng (`week_hvn` đã làm: `wk ≤ W−1`); HVN_D/VAH_D/VAL_D từ phiên trước; VWAP gồm nến i (nến i đã đóng khi xét). Kiểm bằng test cắt dữ liệu (mục 3.6).

**Vệ sinh VWAP (mượn `Warm = 30` của setup B, không phải tham số mới):** `VWAP_D` chỉ được làm E khi phiên đã ≥ 30 nến; `VWAP_W` khi tuần đã ≥ 30 nến.

### 2.2 Máy trạng thái "cú phá có đà" — một bản cho mỗi cặp (vùng z, chiều S)

Ba tham số tự do **mới** (chọn trước, lý do cơ chế; độ nhạy báo thêm, không chọn lại):

| Tên | Giá trị | Lý do cơ chế | Độ nhạy |
|---|---|---|---|
| `D_MIN` | **2,0 giá** | cú phá chỉ "đã trang bị" khi cực trị cách cạnh ≥ nửa ngân sách SL (4 giá); nhích dưới 2 giá là lắc tại cạnh, không phải đà. Trùng E = 2 giá của VCL. Dữ liệu: 88 % trạng thái cũ vượt 2 giá, nên không phải lọc gắt | 1,5 · 3,0 |
| `T_HOI` | **30 nến tính từ CỰC TRỊ CUỐI** | giữ con số 30 của V3 nhưng neo lại đúng chỗ: nhịp hồi là thứ xảy ra **sau** đà kết thúc; 30 phút M1 là cỡ scalp. Hồi tới E chậm hơn 30 nến sau đỉnh = thị trường đã sang chế độ khác | 20 · 60 |
| `CANCEL_DEPTH` | **= `ZONE_HALF` = 1,0 giá** (tái dùng, không thêm số) | M5 đóng lại phía trong **sâu hơn vùng chạm** mới là "phá bị từ chối"; đóng trong ≤ 1 giá là giá đang chạm cạnh — chính cái ta chờ | 0,5 · 1,5 |

(Đếm: `D_MIN`, `T_HOI` là 2 tham số mới thật; `CANCEL_DEPTH` tái dùng hằng cũ. Còn 1 slot — **không dùng**, để tránh thêm bộ lọc "giảm dần" kiểu setup B đã chứng minh bắt nhầm cú trôi chậm.)

```
Trạng thái mỗi (z, S): NGU | PHA
PHA giữ: p0 (nến M1 cuối của M5 phá), brk_no, E_canh(i) (động), pk_pos, pk_val, L (biên độ lớn nhất của MOVE), pbmax, armed

Khi một nến M5 vừa đóng (nến M1 cuối = lp), với từng z có giá trị tại lp:
  canh_up = hi(lp), canh_dn = lo(lp)
  out = +1 nếu C_M5 > canh_up ; −1 nếu C_M5 < canh_dn ; 0 nếu trong
  (z,+1) ở NGU và out = +1  ⇒ PHA: p0 = lp; leg = các nến M1 lùi từ lp tới nến cuối cùng đóng ≤ canh (tối đa 60);
                                L = max rng(leg); pk = cực trị của leg; armed = (pk_val − canh_up) ≥ D_MIN; pbmax = max rng(nến sau pk trong leg)
  (z,−1) gương.  (Hai chiều của cùng z không cùng PHA: out chỉ có một dấu.)
  (z,S) ở PHA và M5 đóng phía trong sâu hơn CANCEL_DEPTH, tức S·(C_M5 − canh_S(lp)) < −ZONE_HALF ⇒ NGU ("phá bị từ chối")
  (z,S) ở PHA và M5 đóng ngoài phía ĐỐI DIỆN của dải (chỉ dải) ⇒ NGU
  (M5 đóng ngoài cùng phía: giữ nguyên PHA — không mở trạng thái mới.)

Mỗi nến M1 i đã đóng, cho từng (z,S) ở PHA, theo THỨ TỰ:
  1. E = canh_S(i)  (VWAP: giá trị tại i; cố định: không đổi)
  2. kiểm VÀO LỆNH (dùng pk_pos, L, pbmax của các nến < i):
       near  = |C_i − E| ≤ ZONE_HALF  hoặc  L_i ≤ E ≤ H_i
       npb   = i − 1 − pk_pos                       (số nến hồi, tính từ cực trị cuối)
       ok    = armed ∧ npb ≥ n_min ∧ (i − pk_pos) ≤ T_HOI ∧ pbmax < L ∧ near ∧ CF(S,i)
               ∧ count(phiên, z, S) < 2 ∧ pha(i) ≠ OFF ∧ ¬(1 ≤ nến_kể_từ_nến_dài_nhất_phiên ≤ 3) ∧ ¬thin/splice
       nếu ok: struct = S>0 ? min(L_i, lo(i) − ZONE_HALF) : max(H_i, hi(i) + ZONE_HALF)      (mép XA của dải; điểm ⇒ lo = hi = E)
               r = kernel.risk(i, S, struct, rr=3)  — None (SL > 4 giá) ⇒ không vào, trạng thái giữ nguyên
               vào ở C_i; count += 1; pk_pos = i, pk_val = S>0 ? H_i : L_i, pbmax = 0     (cho phép lệnh 2 sau nhịp hồi mới, như V3)
               ⇒ bỏ qua bước 3 cho nến này
  3. cập nhật đà:
       nếu S·(cực_trị_i − pk_val) > 0  ⇒ pk_pos = i; pk_val = cực_trị_i; L = max(L, rng_i); pbmax = 0; armed |= S·(pk_val − E) ≥ D_MIN
       ngược lại                      ⇒ pbmax = max(pbmax, rng_i)
  4. hết hạn: nếu (i − pk_pos) > T_HOI ⇒ NGU   (đà đã dừng > 30 nến mà chưa có CF hợp lệ; cú M5 ngoài kế tiếp sẽ mở PHA mới, brk_no + 1)
Hết phiên ⇒ mọi (z,S) về NGU; vùng cố định đổi giá trị đầu phiên (HVN/VA mới) ⇒ NGU.
Hai lệnh hợp lệ cùng nến i ở hai vùng khác nhau ⇒ chọn vùng có |C_i − E| nhỏ nhất; hoà ⇒ hạng VWAP_W > VWAP_D > HVN_W > HVN_D > VAH/VAL_D > VA Âu/IB.
```

**Những gì đã đổi so với V3 và vì sao (bám đúng 6 điểm người học yêu cầu):**
- (i) *Cú phá được công nhận*: **giữ "M5 đóng ngoài"** (không đổi sang M1 đóng ngoài ≥ x giá) vì: dùng chung với máy chế độ BALANCE/BREAK/TREND đã có, parity sẵn; M1 đóng ngoài thêm một ngưỡng x nữa và trên VWAP động sẽ bắn liên tục. Nhưng "công nhận" ≠ "được canh": **chỉ canh khi đã trang bị** (`D_MIN`). Đây là thay đổi cốt lõi — V3 canh mọi cú nhích 1 tick.
- (ii) *Đoạn đi tiếp*: giữ theo dõi cực trị (đúng sẵn), **thêm `L = max(L, rng_i)`** để "nến dài nhất của move" gồm cả đoạn đà sau p0.
- (iii) *Đà chậm dần*: định nghĩa đo được = **≥ `n_min` = 3 nến liền không lập cực trị mới** (tái dùng tham số cũ) — nhịp hồi tính **từ cực trị cuối**. Không thêm bộ lọc biên độ/|Δ| giảm dần (lý do ở trên).
- (iv) *Hết hạn/hủy*: `T_HOI` từ cực trị thay cho 30 nến từ nến phá; hủy khi M5 đóng trong **sâu hơn 1 giá** thay vì 1 tick; hết phiên; đổi vùng.
- (v) *Hồi hình U*: giữ `pbmax < L` nhưng `L` nay là của toàn move (gồm đà). `npb ≥ 3`.
- (vi) *CF, SL, TP*: giữ nguyên `confirm_bars`, SL = max(râu CF, mép xa dải + 1) + 0,3, trần 4 giá, **TP 3R giữ** (QĐ-3; hoà vốn sau phí ≈ 27 % WR). TP 2R chạy song song **như độ nhạy**, không chọn. QĐ-8 ("vào sau khi giá đã rời cạnh ≥ d") **không** đưa vào vòng này — đã đo n=148–193 R TB −0,03…−0,15 trên Trap, chưa ủng hộ; ghi ở mục 5 làm việc sau.

### 2.3 Khung giờ

- **Bỏ `SM_NOPHA` (780..859 = 18:00–19:20 VN)** khỏi logic. Thay bằng **báo cáo riêng**: lệnh có nến M5 phá **hoặc** nến CF rơi trong 780..859.
- **Luật cứng engine C# `BenzoCore.InVirtualOpen(sm) = 860 ≤ sm < 930` (19:20–20:30 VN; QĐ-7, luật duy nhất có số ủng hộ, đo trên C: −0,26 → −0,06) — KHÔNG đụng.** Tương tác sau thay đổi:
  cú phá lúc 18:30 + CF lúc 19:10 ⇒ **được vào** (trước đây bị cấm). Cú phá lúc 18:50 + CF lúc 19:40 ⇒ Python cho vào, **C# chặn** (engine chặn `TryDetect`, `Observe` vẫn chạy nên trạng thái A tiếp tục; CF 20:35 vẫn vào được).
  Vậy khung còn bị cấm **vào lệnh** sau vòng này chỉ là 19:20–20:30 VN (mùa đông Mỹ: 20:20–21:30 VN). Python phải có cờ `virtual_open_block=True/False` để báo cả hai bản và để parity so đúng bản có chặn.
- **Đo luật 19:20–20:30 trên 90 ngày (chỉ báo, không đổi engine vòng này):** với A-v4 và với cả 4 setup (gọi `detect` cũ của B/C/D): R TB và WR của lệnh có CF trong 860..929 vs ngoài; **đối chứng** = cùng phép so cho 24 cửa sổ 70 phút khác dời ±10 phút/bước (sm 580..1200), xem khung 19:20–20:30 có nằm ngoài dải 5–95 % của các cửa sổ khác không. n < 10 ⇒ ghi "không áp dụng". Lưu ý file 90d toàn mùa hè nên nhánh mùa đông chưa kiểm.

---

## 3. THIẾT KẾ BACKTEST (Opus, Python)

**File mới**, không sửa `setup_a_pha_hoi.py` (giữ để tái tạo gốc): `research/setup_a_v4.py` (máy trạng thái + pipeline), `research/zones_a_v4.py` (cột vùng mới + `peak_sharpness` + VA đang hình thành; nếu thêm vào `kernel.py` thì **chỉ thêm hàm**, không đổi hàm cũ, kèm test), `research/test_a_v4.py`, `report/RESULTS-A-V4.md`, `report/_eval_a_v4.txt` (đánh giá viết tay sau khi đọc số).
Mọi ngưỡng ghi là hằng ở đầu file **trước khi chạy lần đầu**; commit hằng trước, commit kết quả sau (lịch sử git là bằng chứng không chọn sau).

### 3.1 Gốc phải tái tạo được
Chạy `setup_a_pha_hoi.detect(..., expire=30)` ô chính ⇒ phải ra đúng **n = 20, WR 10,0 %, R TB −0,68** (BENZO-VCL mục 1 đã tái tạo được). Lệch ⇒ dừng, báo.

### 3.2 Các cấu hình (mỗi cấu hình một bảng, cùng seed)
Ba công tắc độc lập: `Z` (tập vùng: cũ = VA Âu/IB/VA hôm qua theo pha như V3 · mới = 6 loại mục 2.1 · mới+ = 6 loại + VA Âu/IB), `M` (logic: V3 · đà mục 2.2), `H` (18:00–19:20: cấm · không cấm).

| Tên | Z | M | H | Mục đích |
|---|---|---|---|---|
| **A-V3 gốc** | cũ | V3 | cấm | mốc so sánh (n=20) |
| (a) chỉ đổi vùng | mới | V3 | cấm | vùng tự nó đẩy n/WR không |
| (b) chỉ đổi logic đà | cũ | đà | cấm | logic tự nó |
| (c) chỉ bỏ cấm giờ | cũ | V3 | không | giờ tự nó |
| **(d) A-v4** | mới | đà | không | bản đề xuất |
| **A-v4+** | mới+ | đà | không | có đáng giữ VA Âu/IB không |
| (phụ) 2 ô còn lại của 2×2×2 | | | | in ở phụ lục để bảng tách đóng góp đủ 8 ô |

Với mỗi cấu hình báo: n (đã đóng), lệnh/ngày (÷ 61), WR, R TB, kỳ vọng giá/lệnh, chuỗi thua dài nhất, **KTC 95 % bootstrap 10 000 lần seed 0**, TRAIN n/R · TEST n/R, tháng T8/T9/T10 (T8 gồm 29–31/7), theo pha Á/Âu/Mỹ, **khung 18:00–19:20 riêng** (n, WR, R), khung 19:20–20:30 riêng, số tín hiệu thô trước luật 1 lệnh mở, số trạng thái PHA / số đã trang bị / số có CF (phễu), bản có/không `virtual_open_block`.
Với (d) và A-v4+: **tách theo loại vùng E** (VWAP_W, VWAP_D, HVN_W, HVN_D, VAH_D, VAL_D, [VA Âu, IB]) cùng các cột trên; tách theo `brk_no` (phá lần 1 / ≥ 2); tách theo khoảng cách cực trị (2–3 / 3–5 / > 5 giá) — **chỉ mô tả**, không lọc.
TP 2R chạy song song mọi cấu hình (độ nhạy). Độ nhạy `D_MIN` {1,5; 3,0} × `T_HOI` {20; 60} × `CANCEL_DEPTH` {0,5; 1,5} (đổi một tham số một lần quanh ô chính, không quét lưới toàn phần), HVN_W điểm vs dải, VA ngày đang hình thành — **in bảng, không chọn lại**.

### 3.3 Đối chứng (bắt buộc cả ba, cho (d) và A-v4+; (a)(b)(c) chỉ cần ĐC1)
- **ĐC1 — vào ngẫu nhiên cùng trạng thái:** hồ = mọi nến i mà có (z,S) ở PHA **đã trang bị**, `(i − pk_pos) ≤ T_HOI`, `near` đúng, hợp lệ (pha, thin, nến dài), **không cần** `npb ≥ 3`, `pbmax < L`, CF. Mỗi lệnh thật rút 1 nến cùng chiều, cùng vùng, cùng TRAIN/TEST; SL/TP y hệt công thức; 200 lần (như `control_state`). Trả lời: nhịp hồi U + CF thêm được gì so với vào bừa trong trạng thái.
- **ĐC2 — `kernel.control_sample`** (không sửa; nhưng `ZONE_NAME2COL` hiện **không có** HVN_D/HVN_W ⇒ điều kiện vùng bị bỏ qua ⇒ vô nghĩa). Opus thêm cột `hvn_d_1..3`, `hvn_w_1..3` vào bảng vùng của A-v4 và truyền map tên→cột qua tham số mới (hàm bọc trong `setup_a_v4.py`, không đổi chữ ký cũ). Mỗi lệnh thật 1 nến cùng vùng, cùng chế độ kernel, cùng chiều; 200 lần.
- **ĐC3 — dời bản đồ vùng:** mọi mức E của phiên (kể cả VWAP động: cộng hằng δ) dời cùng δ, |δ| ~ U[3, 15] giá, dấu ngẫu nhiên, cố định trong (phiên, bản); **100 bản, hạt giống 20261024, cùng ma trận δ** cho mọi cấu hình (như BENZO-VCL). Chạy nguyên máy trạng thái trên vùng dời. Trả lời: cơ chế phá-hồi có cần vùng **đúng chỗ** không, hay vùng nào cũng vậy.
- **Ngưỡng "khác đối chứng" — NGUYÊN `PLAN-LAN-CHAM.md` mục 5:** thật nằm ngoài dải 5–95 % của đối chứng ở **CẢ TRAIN và TEST**, cùng dấu, cùng dấu ở ≥ 2/3 tháng, VÀ |hiệu| > 2 sai số ở cả TRAIN và TEST. Thiếu một ⇒ "≈ đối chứng". **Chỉ áp dụng khi nhóm có ≥ 10 lệnh ở cả TRAIN và TEST**; không thì ghi "không áp dụng (n nhỏ)" — nói thẳng, không dùng chữ "có xu hướng".
- **Công suất thống kê:** in như BENZO-VCL 2.2: hiệu nhỏ nhất phát hiện được (80 %, hai phía) ≈ 2,8 × σ_R × √(1/n₁ + 1/n₂). Với n ≈ 40–80 và σ_R ≈ 1,3, chỉ chênh ≥ 0,5–0,8R mới thấy được. Người đọc phải thấy con số này **trước** bảng chính.

### 3.4 Kỳ vọng trung thực đăng ký trước
- n sẽ tăng (6 loại vùng thay 1 band; không cấm giờ; không hủy vì 1 tick) — ước **40–150 lệnh/61 phiên (0,7–2,5/ngày)**. Nếu n không tăng ≥ 2× thì logic đà đang lọc gắt hơn nó mở — vẫn báo.
- WR ở 3R kỳ vọng **25–35 %** (hoà vốn 27 %). Mọi phép đo S/R trước ≈ đối chứng; HVN không phải mốc phản ứng ⇒ kỳ vọng hợp lý là **(d) ≈ ĐC3** (dời vùng cũng ra chừng ấy). Nếu đúng vậy thì kết luận "cú phá có đà + hồi + CF là bộ lọc hình dạng, không cần vùng" — cũng là thông tin có ích.
- Không ép: không chọn ô độ nhạy đẹp; không gộp TP 2R vào kết luận chính.

### 3.5 Ví dụ bắt buộc để soi chart
5 lệnh thắng + 5 thua (chọn cách đều theo thời gian) kèm giờ UTC/VN, vùng, E, cực trị, số nến đà (pk_pos − p0), số nến hồi, L, pbmax. Thêm **5 ca "V3 bỏ sót mà A-v4 bắt"** (cực trị > 30 nến sau p0) và **5 ca "V3 vào mà A-v4 từ chối"** (chưa trang bị / hồi > T_HOI) — để người học soi bằng mắt xem định nghĩa mới có khớp ý họ không. Vẽ bằng `_plot_run.py` (Pillow/matplotlib có sẵn), lưu `report/img/a_v4_*.png`.

### 3.6 Kiểm không nhìn trước (test bắt buộc, `test_a_v4.py`)
1. **Cắt dữ liệu:** với ≥ 5 vị trí cắt i (giữa phiên, ngay sau 19:00, ngay sau đổi tuần, giữa nhịp hồi), `detect(df[:i+1])` phải cho **đúng** các lệnh có idx ≤ i của bản chạy đầy đủ, và bảng vùng cột (HVN, VA, VWAP) khớp `allclose` trên [0, i]. Mẫu: `test_b_no_lookahead_zones`.
2. Tổng hợp: cú phá đi tiếp 40 nến rồi hồi ⇒ A-v4 vào, V3 không; M5 đóng trong 0,5 giá ⇒ không hủy, 1,5 giá ⇒ hủy; cực trị 1,5 giá ⇒ chưa trang bị, 2,5 ⇒ trang bị; VWAP động: E tại nến vào = VWAP(i); HVN dải: phá lên dùng `hi`, SL qua `lo`; `L` cập nhật khi nến đà sau p0 lớn hơn leg; hết hạn `T_HOI` rồi M5 ngoài lần nữa ⇒ `brk_no = 2`; hai vùng cùng nến ⇒ chọn gần hơn.
3. Tái tạo gốc 3.1 là một test.

---

## 4. TIÊU CHÍ "ĐÁNG PORT C#" (đăng ký trước) + thiết kế C#

Hai tầng, quyết định theo (d) A-v4 (A-v4+ thay thế nếu người học chọn giữ VA Âu/IB sau khi xem bảng):

- **T1 — port để forward test (thay DetectorA, công tắc A bật như QĐ-7):** đồng thời (1) n(A-v4) ≥ 40 trên 61 phiên (≥ 2× gốc); (2) R TB TEST(A-v4) ≥ R TB TEST(A-V3 gốc, −0,08 trên n=8) **và** n TEST ≥ 15; (3) R TB TRAIN(A-v4) ≥ −0,30 (không tệ rõ hơn gốc); (4) **không** đối chứng nào cho "thật KÉM hơn đối chứng" theo ngưỡng mục 3.3; (5) test 3.6 xanh; (6) khung 18:00–19:20 không âm nặng hơn phần còn lại quá 0,5R với n ≥ 10 (nếu có, báo và đề xuất người học quyết, không tự cấm lại).
  Không đạt T1 ⇒ **không port**, giữ V3, README ghi kết quả. README trong mọi trường hợp ghi "**chưa có lợi thế đo được**" trừ khi đạt T2.
- **T2 — được viết "có lợi thế đo được":** TRAIN > 0 và TEST > 0, n TEST ≥ 30, vượt **cả ba** đối chứng theo ngưỡng mục 3.3. Với 61 phiên, T2 gần như chỉ đạt khi hiệu ≥ ~0,6R — nói rõ trong báo cáo.

**Thiết kế C# (chỉ làm sau khi Fable duyệt số và đạt T1):**
- `BenzoZones.cs`: lưu profile `_full` của **các phiên đã đóng** (hàng→volume, giữ ≥ 25 phiên) + `week_no` mỗi phiên (khoảng trống > 30 h); đầu phiên mới tính `HvnW` (gộp phiên thuộc 3 tuần đã đóng, ≥ 300 nến, `FindHvn` cổng 2,5, tối đa 3, dải `PeakSharpness` 0,9 kẹp 2 giá) và `HvnD` (phiên đầy đủ gần nhất). Port `find_hvn`/`peak_sharpness` vào `BenzoKernel` (BenzoZones **không** phụ thuộc ProfileEngine; copy công thức, kèm test số khớp Python trên 3 phiên mẫu). `YdVah/YdVal`, `VwapD/VwapW` đã có. `ZoneSnap` thêm mảng HVN + cờ VWAP đủ 30 nến.
- `DetectorA` v4: `Dictionary<(string zone, int side), St>`; `OnM5` mở/hủy theo 2.2; `Scan` theo thứ tự 1→4 của 2.2; `_count` khoá `(phiên, zone, side)`; bỏ `SmNoBreakFrom/To`; `Reason` tiếng Việt ghi: vùng, E, cực trị cách E x giá sau y nến, hồi z nến, CF Δ. Hằng mới: `DMin = 2.0, THoi = 30, CancelDepth = ZoneHalf`.
- Engine: giữ `InVirtualOpen`. `LogicVersion = "port-3-A-v4"`.
- **Parity:** `tools/ReplayCsv` xuất thêm cho A mỗi nến: `zone, side, state, armed, pk_pos, pk_val, L, pbmax, brk_no`; `parity_check.py` so với Python **bản `virtual_open_block=True`** từ 2026-07-29 (4 phiên thin đầu bỏ); mục tiêu khớp 100 % như `PARITY.md` hiện tại; mọi lệch phải giải thích được.
- Test C# (`tests/`): các ca tổng hợp của 3.6 (2) chạy y hệt bằng `BarData` giả; hồi quy số lệnh trên file 90d.

---

## 5. RỦI RO / ĐIỂM MƠ HỒ — Opus phải báo lại từng mục

1. **Kết quả ≈ đối chứng dời (ĐC3)** — khả năng cao nhất, khớp mọi phép đo S/R trước. Khi đó nói thẳng: vùng không phải thứ tạo lợi thế; không được viết "vùng pro trader tốt hơn VA Âu".
2. **VWAP động làm "cú phá" bắn liên tục** khi giá bò dọc VWAP (M5 đóng trên/dưới xen kẽ). `D_MIN` và `Warm 30` là hai cái phanh; nếu VWAP_D/VWAP_W chiếm > 70 % số trạng thái PHA nhưng < 30 % số lệnh, báo (phễu ở 3.2). Không tự thêm luật.
3. **Nhiều vùng gần nhau** (HVN_D trùng VAH_D, HVN_W trùng VWAP_W trong ±1 giá): hai trạng thái PHA song song cho một cú giá ⇒ cùng nến có thể 2 lệnh (đã có luật chọn gần nhất), nhưng vẫn có thể vào lệnh thứ 2 ở vùng kề 1–2 nến sau ⇒ `one_at_a_time` chặn. Báo tỉ lệ lệnh bị chặn và tỉ lệ vùng trùng ±1 giá.
4. **HVN tuần 3 tuần đã đóng có thể cách giá 20–80 giá** (SessionZones đã đo) ⇒ hiếm khi là E; n theo loại vùng sẽ lệch nặng về VWAP/VA ngày. Báo n từng loại; loại nào n < 10 thì không nói gì về nó.
5. **Tuần đầu file (07-23…07-28) thin** ⇒ HVN_W của 3 tuần đầu tháng 8 dựng trên < 3 tuần hoặc thiếu; kernel đã có cờ `partial`. Báo số phiên có HVN_W `partial`.
6. **`D_MIN` so với cạnh động:** với VWAP, "cực trị cách E ≥ 2 giá" dùng E tại nến cực trị hay tại nến hiện tại? **Chốt: tại nến hiện tại i** (`armed |= S·(pk_val − E(i)) ≥ D_MIN` ở bước 3) — đơn giản, cùng một E cho mọi phép so trong nến. Nếu Opus thấy ca cạnh trôi làm armed bật/tắt qua lại thì báo tần suất, không tự sửa.
7. **Hồi hình U với `L` gồm đà:** nến đà rất lớn (vd 6 giá) làm `pbmax < L` gần như luôn đúng ⇒ bộ lọc V mất tác dụng ở các cú phá mạnh. Báo phân phối `pbmax / L` của lệnh vào; đây là hệ quả của định nghĩa đúng, không phải lỗi — nhưng người học cần biết.
8. **Hai lệnh/vùng/phiên với vùng động:** khoá theo tên vùng, không theo giá; VWAP_D có thể cho lệnh 1 ở 4190 và lệnh 2 ở 4210 cùng phiên — chấp nhận, ghi rõ.
9. **n nhỏ ở TRAIN/TEST theo loại vùng** ⇒ phần lớn phán quyết theo loại sẽ "không áp dụng". Đừng dồn vào gộp rồi nói về từng loại.
10. **Mô phỏng `one_at_a_time` chung với B/C/D** không chạy ở đây (A đứng riêng như các RESULTS); ghi rõ. Khi gộp 4 setup thì n thực tế sẽ thấp hơn.
11. **Ca chưa phủ trong máy 2.2** (vd nến M1 đầu phiên chưa có VWAP; vùng xuất hiện giữa phiên — chỉ A-v4+ có VA Âu 19:00/IB 20:20: trạng thái mở sớm nhất ở M5 đầu tiên sau khi vùng chốt) ⇒ nếu gặp ca khác, **dừng và hỏi**, không tự chế.
12. **Luật 19:20–20:30** đo ở 2.3 chỉ là chỉ báo với đối chứng cửa sổ dời; n nhỏ (MO-XE: C 26 lệnh). Không đề xuất bỏ/giữ trong vòng này, chỉ báo số để người học quyết vòng sau.
13. **Thời gian chạy:** 6 loại vùng × máy trạng thái M1 × 100 bản dời ⇒ phải vector hoá phần vùng và chỉ chạy đối chứng dời cho (d) và A-v4+. Mục tiêu ≤ 10 phút toàn bộ; vượt thì giảm bản dời xuống 50 và ghi rõ.

---

## 6. BÁO CÁO CUỐI CHO NGƯỜI HỌC (Opus viết trong `_eval_a_v4.txt`, ≤ 12 dòng, tiếng Việt, không thuật ngữ lạ)

Dạng cố định:
1. **Số lệnh:** gốc 20 (0,33/ngày) → A-v4 **n** (**x/ngày**), tăng **+k lệnh / +y/ngày**; trong đó đóng góp: đổi vùng +…, logic đà +…, bỏ cấm giờ +… (từ (a)(b)(c)).
2. **WR:** 10 % → **z %** (**+p điểm**), ở TP 3R; hoà vốn 27 %.
3. **R TB:** −0,68 → **r** [KTC 95 %]; TRAIN r₁ (n) / TEST r₂ (n).
4. **Độ tin cậy:** so 3 đối chứng theo ngưỡng đã đăng ký — kết quả từng cái (KHÁC ▲ / ≈ / không áp dụng vì n nhỏ); hiệu nhỏ nhất phát hiện được với n này = … R ⇒ câu "chưa thể nói gì về chênh < …R".
5. **Khung 18:00–19:20:** n, WR, R — có đáng để mở không (chỉ số, người học quyết).
6. **Từng loại vùng:** một dòng mỗi loại có n ≥ 10; loại n < 10 gộp vào "chưa đủ mẫu".
7. **Kết luận T1/T2:** port hay không, và câu bắt buộc nếu không đạt T2: "**chưa có lợi thế đo được** trên 61 phiên; bật để forward test".
8. **VA Âu/IB có đáng giữ không:** A-v4+ so A-v4 một dòng; người học quyết.

Không viết "có xu hướng", không chọn ô độ nhạy đẹp, không ép số.

---

## 7. Nguồn tham khảo ngoài (2 lượt tìm; chỉ xác nhận quy ước thực hành, không có định nghĩa định lượng chuẩn cho "đà chậm dần")
- Phá-hồi (break and retest): vào ở nhịp hồi đầu tiên về mức vừa phá, hồi phải **yếu hơn** cú phá (hồi dốc bằng cú phá = phá hụt), hồi **ngắn**, SL dưới đáy hồi — [capital.com](https://capital.com/how-to-trade-the-break-retest), [atas.net](https://atas.net/blog/break-and-retest-strategy/), [chartingwithkr](https://chartingwithkr.substack.com/p/the-breakout-and-retest-strategy). Khớp: `pbmax < L`, `T_HOI`, SL qua mép xa.
- Al Brooks "second entry" / đếm H1-H2: lần hồi đầu hay thất bại, lần 2 đáng tin hơn — [luxalgo bar counting](https://www.luxalgo.com/library/concept/bar-counting-h1-h2.md), [tradingview 2nd entry](https://www.tradingview.com/scripts/2ndentry/), [NexusFi two-legged pullback](https://nexusfi.com/a/strategies/two-legged-pullback-trading). ⇒ lý do báo tách `brk_no` 1 / ≥ 2 (V5 cũ đã thử nhưng n=1; nay có thể đủ n).
- Không nguồn nào định nghĩa "momentum exhaustion" bằng số trên M1; định nghĩa `n_min` nến không lập cực trị mới + `D_MIN` là tự chọn, biện luận bằng cơ chế và kiểm độ nhạy (mục 2.2).

## 8. Giao nộp
`research/setup_a_v4.py`, `research/zones_a_v4.py` (hoặc hàm thêm vào kernel + test), `research/test_a_v4.py`, `report/RESULTS-A-V4.md`, `report/_eval_a_v4.txt`, `report/img/a_v4_*.png`.
Sau khi Fable duyệt số và đạt T1: `BenzoZones.cs`, `BenzoDetectors.cs`, `tests/`, `tools/ReplayCsv`, `parity_check.py`, `README.md`, build `dist/`. Commit + push từng bước (quy tắc repo).
