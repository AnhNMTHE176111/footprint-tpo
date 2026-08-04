# Kế hoạch Wyckoff v6 — vá lỗi chấm v5 + Phase B (SOT / nỗ lực-kết quả / bias) + range sinh sau cú phá

> Lập 2026-08-04. Nguồn: vòng chấm v5 (47 phiếu `research/wyckoff/grading/cham_*.md`) + buổi bàn SOT/Phase B
> với người học. Hai file phải sửa **song song từng dòng**: `wyckoff_schematic.py` (Python, xe thiết kế)
> và `WyckoffRunner.cs` (C#, bản chạy thật).

---

## 0. Điểm xuất phát — số thật, không tô hồng

Điểm chấm của giảng viên, thang 10:

| Vòng | n | Trung vị | Trung bình | Phân bố |
|---|---|---|---|---|
| v4 | 49 | **3/10** | 3.41 | 4×1 · 13×2 · 12×3 · 11×4 · 2×5 · 3×6 · 3×7 · 1×8 |
| v5 | 47 | **3/10** | 3.57 | 9×1 · 9×2 · 6×3 · 7×4 · 6×5 · 6×6 · 3×7 · 1×8 |

**Kết luận thẳng: v5 gần như không cải thiện.** Trung vị đứng yên, trung bình nhích 0.16, và đuôi kém còn
tệ hơn (bài 1 điểm tăng từ 4 lên 9). Các lỗi A–K của v4 đúng là đã hết, nhưng chúng bị thay bằng một nhóm
lỗi mới — nặng nhất là **nhãn climax neo sai cây**. Nghĩa là: sửa đúng chỗ nhưng chưa đủ, và có chỗ sửa
xong lại sinh lỗi khác. v6 phải nhắm vào trung vị, không nhắm vào "hết lỗi cũ".

Mục tiêu v6: **trung vị ≥ 6/10, không còn bài 1–2 điểm.**

---

## 1. Bước 1 — Vá 9 lỗi vòng chấm v5 (không thêm khái niệm mới)

Làm trước vì đây là lỗi cơ học, không cần bàn lý thuyết, và chúng đang kéo tụt điểm nhiều nhất.

### 1.1 ⭐ Tách MỨC biên khỏi NHÃN climax (ưu tiên số 1 — gần như lô chấm nào cũng bắt)

**Hiện trạng** (`wyckoff_schematic.py:600-616`): trong cửa sổ cụm 8 nến, mỗi khi giá tạo cực trị mới cùng
phía, code dời **cả** `climax_ev['i']` lẫn `climax_price` sang cây đó, rồi `r.start_i = i` — tức đồng hồ
8 nến **được reset**. Hệ quả: nhãn SC/BCLX rơi vào cây VSA 0.2×–1.5× trong khi cây 4×–14× nằm ngay cạnh,
và cụm climax có thể trôi dài vô hạn.

**Sửa** (người học đã chốt: *"dời MỨC biên, giữ NHÃN ở cây volume cao nhất"*):

1. Neo cửa sổ cụm vào **cây climax ĐẦU TIÊN**, không reset: thêm `r.cx_i0` (bất biến), điều kiện cụm đổi
   thành `(i - r.cx_i0) <= CLIMAX_EXT_BARS`. `r.start_i` giữ nguyên `= r.cx_i0`.
2. `r.climax_price` vẫn dời theo **cực trị giá** (nó là mức biên chính).
3. `r.climax_ev['i']` = **argmax `vratio`** trên đoạn `[r.cx_i0 .. i]`, tính lại mỗi lần cụm mở rộng.
   `r.climax_ev['price']` = giá cực trị của **cây mang nhãn** (để mũi tên nhãn chỉ đúng cây), còn mức biên
   lấy từ `r.climax_price`.
4. Ghi lại `r.climax_vsa` = `vratio` của cây mang nhãn, `r.climax_ext_price` = cực trị cụm — để phiếu chấm
   và HTML hiển thị được cả hai.

**Kiểm chứng bắt buộc:** sau khi sửa, in bảng `|climax_ev.vratio|` của cả 47 range. Không được còn range
nào nhãn nằm trên cây có `vratio < VSA_CLIMAX (2.2)`.

### 1.2 Biên phụ — đo trước, rồi mới siết

Giảng viên đo được tỷ lệ **biên phụ / biên chính từ 2× đến 6.4×**. Trước khi sửa phải biết nó phình ở đâu,
vì theo luật người học chốt thì biên phụ **được phép** nới bởi mỗi cú thăm dò thất bại — nới là đúng, phình
gấp 6 lần mới là sai.

**(a) Đo:** log mỗi range một chuỗi `(i, outer_high, outer_low, solid_high, solid_low, sự_kiện_làm_nới)`.
Xuất `research/wyckoff/v8/wyckoff/out/outer_edge_growth.csv`, thống kê: tỷ lệ cuối cùng, số lần nới, và
**nới ở state nào** (`B`, `B_brk` thất bại, `C_pending`, `_fire_break` vô hiệu).

**(b) Sửa chỗ đã thấy rõ là bất nhất:** trong `C_pending` (`:828-831`) code cập nhật `r.low`/`r.high` mỗi
nến ở **cả hai phía**, trong khi ngưỡng phá `shock['out_edge']` lại bị đóng băng từ lúc tạo shock. Hệ quả:
shock hỏng → `_revert_to_B` → biên phụ giờ rộng hơn cái vừa được đem ra test. Sửa: trong `C_pending`
**ngừng nới biên phụ ở phía đang được test**; chỉ nới sau khi biết kết cục.

**(c) Guard tỷ lệ** (người học đã chốt): thêm `MAX_OUTER_RATIO = 1.8` (giữa 1.5 và 2.0). Khi
`(outer_high - outer_low) > MAX_OUTER_RATIO * (solid_high - solid_low)` → `DISCARDED` với lý do
*"biên phụ phình quá biên chính"*. Đặt guard này cạnh guard `too_tall` ở `:592`.

### 1.3 Mở rộng cửa sổ hồi tố neo nhãn SOS/SOW

`_anchor_break_bar(B, first_i, i, up, level)` chỉ quét đoạn `[first_i, i]` = đúng 3 nến xác nhận, và đòi
`close` vượt **biên phụ**. Cây phá thật (volume lớn nhất) thường nằm **trước** đó, hoặc đóng cửa vượt biên
chính nhưng chưa vượt biên phụ.

**Sửa:** gọi `_anchor_break_bar(B, k['start_i'], i, up, solid_edge)` — quét từ nến đầu tiên thò ra, và lấy
mốc so sánh là **biên chính**. Vẫn giữ 2 điều kiện còn lại (đúng hướng, `vratio` cao nhất).

### 1.4 Guard "climax không chặn được move" phải chạy suốt Phase A

Hiện chỉ chạy ở `state == 'A'` sau cửa sổ cụm (`:618-623`). Sang `state == 'A_st'` (tối đa
`STA_MAX_WAIT = 400` nến) thì tắt hẳn — `STA_MAX_OVERSHOOT` chỉ chặn được khi `span` nhỏ.

**Sửa:** đưa phép kiểm `beyond > CLIMAX_FAIL_ATR * avgr` thành một hàm dùng chung, gọi ở **cả `A` và
`A_st`**. Ở `state == 'B'` thì **không** gọi (thò qua climax lúc đó là Spring/UTAD hợp lệ).

### 1.5 Phase C gán ngược: kẹp điểm vào trong range và vào đúng nửa

`_retro_phase_c` lấy `_last_pivot` trong cửa sổ mà không ràng buộc vị trí → giảng viên bắt được điểm
LPS[C] nằm **ngoài range** hoặc **giữa range**.

**Sửa:**
- Lọc pivot: chỉ nhận `solid_low - tol <= price <= solid_high + tol`.
- Đúng nửa: LPS[C] (phá lên) phải nằm ở **nửa dưới** range; LPSY[C] (phá xuống) ở **nửa trên**.
- Siết cửa sổ để giữ L8 (*Phase C ngắn nhất trong A–D*):
  `win = min(RETRO_C_LOOKBACK, (sos_i - b_start) // 2, len_phase_A)`.
- Không tìm được pivot hợp lệ → **không vẽ Phase C** (thà thiếu còn hơn sai chỗ), Phase B chạy thẳng
  sang Phase D.

### 1.6 Xoá nhãn LPS[C] mồ côi

`_revert_to_B` (`:333`) chỉ pop các đoạn phase C/D/E, **không** xoá sự kiện. Trong `_fire_break` đường vô
hiệu, `_retro_phase_c` đã kịp phát nhãn `LPS[C]` rồi mới `_revert_to_B` → nhãn treo lại giữa Phase B.

**Sửa:** trong `_revert_to_B`, xoá mọi event có `phase in ('C','D','E')` và `label` thuộc họ
`LPS[C]/LPSY[C]/LPS[D]/LPSY[D]/SOS/SOW`. Sự kiện shock đã có `_demote_shock` lo riêng — không đụng.

### 1.7 Khe cuối tuần áp cho cửa sổ đo MOVE

`_find_move` nhìn lại `MOVE_LOOKBACK = 240` nến mà không kiểm khe thời gian → một "move" có thể bắc qua
cuối tuần.

**Sửa:** dừng vòng quét lùi tại nến đầu tiên có `gap > GAP_CUT_MIN`.

### 1.8 AR / ST[A] — thay ngưỡng tuyệt đối bằng ràng buộc TƯƠNG ĐỐI (nguyên lý CHoCH)

Giảng viên bác một CHoCH của học viên vì *"đoạn hồi không đủ lớn so với bối cảnh"*. Đó chính là thứ v5
đang thiếu: `PIVOT_MIN_ATR = 1.5` là ngưỡng tuyệt đối nên AR/ST[A] rơi vào nhịp hồi 4 nến trên cây VSA 0.25×.

**Sửa:**
1. Trong `_find_move`, tính thêm `max_pullback` = nhịp hồi ngược lớn nhất **bên trong move** vừa quét. Lưu
   `r.move_max_pullback`.
2. Điều kiện AR đổi thành
   `span >= max(PIVOT_MIN_ATR * avgr, AR_RETRACE_MULT * r.move_max_pullback)`, `AR_RETRACE_MULT = 1.0`.
   Nghĩa đen: **AR phải là nhịp hồi lớn nhất từ đầu move đến giờ** — đúng "đổi đặc tính lần 1".
3. Điều kiện ST[A] thêm `swing >= STA_MIN_AR_FRAC * |AR - climax|`, `STA_MIN_AR_FRAC` = **đo trước rồi chốt**
   (đề xuất khởi điểm 0.4).

**Đo trước khi chốt số:** in phân bố `span / max_pullback` và `swing / ar_span` của 47 range hiện tại, kèm
điểm chấm từng range, để xem ngưỡng nào cắt đúng các bài bị chê.

### 1.9 Chất lượng volume của AR / ST[A] (đo, chưa gate)

Lý thuyết: **ST[A] phải có volume THẤP hơn climax** — còn cao nghĩa là cung/cầu chưa cạn, chưa phải test.
Hiện code không kiểm gì.

**Bước này chỉ ĐO:** ghi `r.ar_vsa`, `r.sta_vsa`, tỷ lệ `sta_vsa / climax_vsa`; in phân bố. Nếu có một
nhóm rõ rệt `sta_vsa > climax_vsa` trùng với các bài bị chấm thấp → mới thêm guard ở v6.1.

---

## 2. Bước 2 — Ba chỉ số Phase B: ĐO và HIỂN THỊ, **không** dùng làm bộ lọc

Người học chốt: *"hãy đo, lấy và báo chỉ số"* và *"code thành 1 chỉ số và show SOT… để học máy và
indicator hiểu tốt nhất"*. Nên bước này **không được đổi một quyết định vẽ nào** — chỉ thêm dữ liệu.
Ngưỡng lọc bàn sau khi có số.

### 2.0 Hạ tầng chung: chuỗi swing pivot trong Phase B

Cả 3 chỉ số đều cần cùng một thứ: danh sách swing pivot **nhân quả** (không nhìn trước) bên trong Phase B.

- Dùng lại đúng bộ tham số của AR/ST[A]: `PIVOT_CONFIRM_BARS = 5`, `PIVOT_MIN_ATR = 1.5`.
- Chạy tăng dần mỗi nến khi `state in ('B', 'B_brk', 'C_pending')`, đẩy vào `r.pivots` =
  `[(i, price, kind)]` với `kind ∈ {'H','L'}`, xen kẽ H/L.
- **Nhân quả**: pivot chỉ được xác nhận sau `PIVOT_CONFIRM_BARS` nến → C# live dùng được y hệt Python.

### 2.1 SOT — Rút ngắn động lực (Shortening of the Thrust)

Lý thuyết (THEORY.md §7): mỗi điểm dừng mới đi được quãng **ngắn hơn** điểm dừng trước; cần **≥3 nhịp
đẩy**; volume **lớn** = hấp thụ (nỗ lực nhiều, kết quả ít → đảo chiều mạnh hơn), volume **nhỏ** = cạn kiệt
thật; **>4 nhịp** = xu hướng quá mạnh, đừng đánh ngược. Bản thân SOT không phải điểm vào lệnh.

Người học chốt: **đo cả hai phía**, bắt đầu đo khi nhận ra chuỗi lower-high / higher-low.

**Cách tính** (làm riêng cho phía trên và phía dưới):

- Phía TRÊN: từ `r.pivots` lấy các cặp (L→H) liên tiếp, `thrust_k = H_k − L_k` (quãng đẩy lên thứ k).
- Điều kiện khởi động: có ≥2 nhịp và `H_k < H_{k-1}` (lower high) — đúng ý *"khi nó tạo lower low, higher
  high… nhận ra điều đó thì bắt đầu đo"*.
- `sot_up.n` = số nhịp liên tiếp thoả `thrust_k < thrust_{k-1}`.
- `sot_up.ratio` = `thrust_cuối / thrust_đầu`.
- `sot_up.effort` = trung bình `vratio` các nến trong nhịp cuối ÷ trung bình `vratio` các nến nhịp đầu.
  - `effort >= 1.0` → **hấp thụ** (nỗ lực giữ nguyên/tăng, kết quả co lại) — tín hiệu đảo chiều mạnh hơn.
  - `effort < 1.0` → **cạn kiệt**.
- Trạng thái: `n < 2` → `none`; `n == 2` → `chớm`; `n >= 3` → `SOT`; `n > 4` → `xu hướng quá mạnh`.
- Phía DƯỚI: gương lại với các cặp (H→L), `thrust_k = H_k − L_k` đo xuống, điều kiện higher low.

**Hiển thị:** nhãn `SOT↑ n=3 (hấp thụ)` đặt tại swing cuối cùng, màu riêng (đề xuất tím `#AB47BC`), nằm
trong nhóm ẩn/hiện được của HTML. Ghi thêm vào phiếu `range_NN.md` một bảng nhịp đẩy: `k | i | giá |
thrust | vratio TB`.

### 2.2 Nỗ lực ↔ Kết quả từng nhịp — lấp khoảng trống Phase B

Giảng viên chê Phase B *"trống hàng trăm nến, không đọc gì"*. Chỉ số này lấp đúng chỗ đó.

Với mỗi đoạn giữa 2 pivot liên tiếp:
- `effort` = (tổng volume của đoạn ÷ số nến) ÷ volume TB 20 nến — tức `vratio` trung bình.
- `result` = |Δgiá của đoạn| ÷ `avgr` (biên độ TB 20 nến).
- `er = effort / result`.

Đoạn có `er` cao nhất trong Phase B = **vùng hấp thụ nghi vấn**; đánh dấu bằng một dải nền mờ trên chart
(không phải nhãn chữ, tránh rối) + ghi vào phiếu chấm.

**Chưa dùng để quyết định gì.** Chỉ để giảng viên nhìn và để dữ liệu huấn luyện có cột này.

### 2.3 Chỉ số bias từ bất đối xứng test

Người học nói rất rõ và điều này **đảo ngược trực giác thường thấy**: test **cả hai biên là ca THƯỜNG** —
tay to cố tình giấu hành vi. Bất đối xứng là ca **hiếm**, xảy ra khi họ lỡ để lộ ý đồ hoặc đang gấp. Nên
đây là **một** bias, *"chứ ko phải luôn luôn sẽ sử dụng đc nó"*.

**Cách tính**, chốt tại thời điểm Phase B kết thúc:
- `reach_hi` = (max high trong B − solid_low) / height; `reach_lo` = (solid_high − min low trong B) / height.
- `bias = +1` nếu `reach_hi >= 0.95` và `reach_lo < 0.75` (chạm biên trên, không với nổi biên dưới);
  `bias = −1` gương lại; còn lại `bias = 0`.

**Đo bắt buộc trước khi dùng:** trên 47 range, in bảng chéo `bias` × `hướng phá thật`. Nếu `bias ≠ 0` chỉ
xuất hiện ở <20% số range (đúng như người học mô tả) và tỷ lệ trúng hướng không hơn ngẫu nhiên rõ rệt →
**giữ nguyên chỉ số hiển thị, không đưa vào logic**. Báo số cho người học quyết.

Liên quan lý thuyết (p012.png): test ở biên trên + **không với nổi** biên dưới ⇒ lực mua ở đáy mạnh, cú phá
có thể xuất phát từ một LPS giữa cấu trúc *"mà **không cần** phát triển spring ở phần đáy"*. Đây là lý do
`bias` đáng đo: nó dự báo range sẽ **không có Spring**.

---

## 3. Bước 3 — Nhãn Phase B đúng chuẩn giảng viên

### 3.1 UT[B] / ST[B] thay cho UT / UA / DA

Đếm trong `CHART_CASES.md`: UT 156 · ST[B] 55 · UT[B] 23 · UA 7 · DA 1. UA/DA gần như không dùng.

**Luật mới** (người học chốt):

| Hành vi | Nhãn |
|---|---|
| Test / thò nhẹ **biên trên** rồi dội vào | `UT[B]` |
| Test / thò nhẹ **biên dưới** rồi dội vào | `ST[B]` |
| Phá hẳn ra ngoài rồi **thu về trong range**, hướng sang biên đối diện | `mSOS` / `mSOW` |

- **Tối đa 1 nhãn mỗi bên** (giữ cơ chế `_mark_outer` sẵn có, giữ điểm **xa nhất**). Người học xác nhận
  thực tế Phase B *"phần lớn cũng chỉ có 1 UT và 1 ST thôi"*.
- **Bỏ hẳn `UA` và `DA`** khỏi `_minor_label` và khỏi họ nhãn của `_mark_outer`.
- `ST[B]`: người học nói *"chỉ cần show lần đầu tiên thôi hoặc là cũng ko cần thiết"* → thêm checkbox
  `Ẩn ST[B]` trong HTML, **mặc định hiện**.

**Sửa `_minor_label`:** `strong → 'mSOS'/'mSOW'`; ngược lại `'UT[B]' if up_side else 'ST[B]'`. Bỏ hoàn toàn
nhánh `climax_side` và nhánh trả `None`.

⚠️ **Điểm cần người học xác nhận:** dùng `UT[B]`/`ST[B]` (rõ phase) hay `UT`/`ST` (giống chữ giảng viên hay
viết nhất)? Mặc định plan chọn `UT[B]`/`ST[B]`.

### 3.2 mSOS / mSOW — định nghĩa lại cho đúng

**Định nghĩa người học chốt:** mSOS/mSOW **CÓ phá hẳn ra ngoài** như SOS/SOW thật. Chúng thành "minor" vì
nhịp hồi sau đó **thu hẳn vào trong range** rồi đi sang biên bên kia. Khác biệt duy nhất so với SOS/SOW là
**nhịp hồi kết thúc ở đâu**, không phải "phá được hay không".

> Ghi chú giải mâu thuẫn: trước đó tôi từng ghi mSOS/mSOW là "thăm dò mạnh không phá nổi" (dựa Ca #16 và
> chart `pptx3/s016.png` có nhãn *Minor SOW [B]* nằm trong range). Người học đã sửa lại rõ ràng ở buổi này.
> **Theo định nghĩa mới.** Ca "minor SOS xảy ra hẳn trong range" sẽ được thể hiện bằng `UT[B]` + chỉ số
> nỗ lực/kết quả cao ở mục 2.2, **không** đẻ thêm nhãn.

**Sửa `_try_lps_and_phase_e`:** điều kiện `failed` hiện là `close` lui qua **biên phụ** (`level`) trừ
`fail_tol`. Đổi thành lui qua **biên chính** (`solid_high`/`solid_low`) — vùng giữa biên chính và biên phụ
là vùng **chưa kết luận**, tiếp tục chờ. Tác dụng kép: SOS/SOW thật đỡ bị vô hiệu oan, và mSOS/mSOW khi
được gán thì đúng nghĩa "đã thu hẳn vào range".

Thêm điều kiện thứ hai cho đúng vế *"hướng sang biên bên còn lại"*: sau khi thu vào, giá đi được ≥50%
chiều cao range về phía biên đối diện thì mới **chốt** nhãn mSOS/mSOW; chưa đi được thì để nhãn ở trạng
thái tạm và tiếp tục theo dõi trong Phase B.

---

## 4. Bước 4 — Cơ chế MỚI: range sinh ra từ một cú phá

### 4.1 Kịch bản

Người học mô tả: *"Giá phá xong mà đi ngang tại đó, thì range cũ ở dưới bị hủy, range mới hiện ra và tiếp
tục chờ các phase của wyckoff, chấp nhận ko có climax nhưng vẫn gắn điểm vào đấy để tạo range. Tuy nhiên
phải lưu ý là range mới phải đủ dài, nếu nó rất ngắn rồi bứt lên theo chiều phá range thì chỉ là nhịp hồi
thôi."*

Hiện `_try_lps_and_phase_e` chỉ có **2** kết cục. Thêm kết cục **thứ 3**:

| Sau khi SOS/SOW nổ | Kết cục | Xử lý |
|---|---|---|
| Giá đi tiếp, đạt mục tiêu Phase E | `TREND` | như hiện tại: Phase E, đóng range, đặt tên |
| Giá lui hẳn vào trong **biên chính** | `VOID` | hạ cấp thành mSOS/mSOW, `_revert_to_B` (mục 3.2) |
| Giá **giữ ngoài biên chính** nhưng **đi ngang**, không đạt mục tiêu Phase E | **`SIDEWAYS` (mới)** | huỷ range cũ, mở range mới tại đó |

### 4.2 Nhận diện `SIDEWAYS` — nhân quả, không nhìn trước

Bắt buộc không lookahead để C# chạy live giống hệt Python backtest.

Từ nến `sos_i`, theo dõi tới `NEW_RANGE_SEED = 30` nến để dựng dải mầm:
`seed_hi/seed_lo` = cực trị 30 nến đó, `seed_h = seed_hi − seed_lo`.

Vào trạng thái `SIDEWAYS` khi **cả 3** đúng:
1. Không nến nào đóng cửa lui qua biên chính của range cũ (nếu có → `VOID`).
2. Chưa đạt mục tiêu Phase E (`moved_far < PHASE_E_MULT × height` của range cũ).
3. `seed_h <= NEW_RANGE_SEED_MAX × height_cũ`, `NEW_RANGE_SEED_MAX = 0.6` — tức dải mầm hẹp hơn hẳn range
   cũ, đúng nghĩa "đi ngang tại đó".

### 4.3 Mở range mới

- `origin` = chiều move đi vào: phá **lên** → `origin = 'UP'` (bốn mẫu hình sẽ cho DIST nếu sau đó phá
  xuống, RE-ACC nếu phá tiếp lên). Phá **xuống** → `origin = 'DOWN'`.
- **Điểm neo thay climax**: cực trị đạt được trong cú phá (`peak`). Không có cao trào thật →
  **nhãn `BCLX?` / `SC?`** vẽ nét đứt, kèm chú thích *"neo từ cú phá, không có cao trào"*.
  ⚠️ Tên nhãn này cần người học duyệt.
- Bơm thẳng vào state machine hiện có: tạo `WyRange(start_i=peak_i, origin=…)`, gán `climax_price`,
  `climax_ev`, `state = 'A'`, **bỏ qua** `_find_move` (move đã biết chính là cú phá), đặt
  `r.born_from_break = True`.
- Từ đó chạy y hệt: AR = swing ngược đầu tiên, ST[A] = đổi hướng lần 3, đóng băng biên chính, sang Phase B.

### 4.4 Sàn "đủ dài" — phương án A, số nến tuyệt đối

Người học chọn **A (số nến tuyệt đối)**. Đề xuất `NEW_RANGE_MIN_BARS = 120` (2 giờ M1) — **con số này chưa
được đo, phải đo rồi chốt** (xem 4.6).

Range mới mang `status = 'provisional'`. Nó được **chuyển chính thức** khi sống đủ
`NEW_RANGE_MIN_BARS` nến kể từ `peak_i`. Trước mốc đó, nếu giá **bứt tiếp theo chiều cú phá** vượt
`peak ± NEW_RANGE_CONT_MULT × seed_h` (`NEW_RANGE_CONT_MULT = 1.0`) → đó **chỉ là nhịp hồi**:
- xoá range mới,
- khôi phục range cũ, kéo dài Phase E của nó tới nến hiện tại,
- đóng range cũ bình thường và đặt tên theo bốn mẫu hình.

### 4.5 "Range cũ bị huỷ" nghĩa là gì — ⚠️ CẦN NGƯỜI HỌC CHỐT

Hai cách hiểu, tôi **khuyến nghị (b)**:

- **(a) Xoá hẳn** khỏi chart. Sạch, đúng chữ "bị huỷ", nhưng mất luôn thông tin S/R lịch sử và mất luôn
  ngữ cảnh vì sao range mới ra đời.
- **(b) Giữ vẽ nhưng chuyển `status = 'superseded'`**, nét mờ/xám, **không đặt tên bốn mẫu hình** (vì cú
  phá không hoàn tất Phase E), kèm checkbox HTML để ẩn. Vẫn đúng tinh thần "hết vai trò", mà giữ được
  lịch sử.

Plan tạm thi công theo (b) vì nó đảo ngược được dễ; đổi sang (a) chỉ là một cờ render.

### 4.6 Đo trước khi chốt hai con số của bước 4

Trên toàn bộ dữ liệu dxFeed GCQ26 (103,857 nến M1, 2025-11-02 → 2026-07-27), in cho **mọi** cú phá đã nổ:
- phân bố số nến từ `sos_i` đến khi giá hoặc đạt mục tiêu Phase E, hoặc lui vào biên chính, hoặc đi ngang;
- trong nhóm "đi ngang", phân bố **độ dài đoạn đi ngang** → chọn `NEW_RANGE_MIN_BARS` ở chỗ phân bố tách
  đôi rõ (nhịp hồi ngắn vs range thật), **không** chọn 120 theo cảm tính;
- phân bố `seed_h / height_cũ` → chốt `NEW_RANGE_SEED_MAX`.

**Báo số cho người học trước khi cứng hoá.**

---

## 5. Bước 5 — Port C# và build

Sửa Python xong, chạy đối chiếu, rồi mới port. Danh sách điểm chạm trong `WyckoffRunner.cs`:

| Python | C# | Việc |
|---|---|---|
| hằng số mục 1–4 | `WY_*` (`:1189-1227`) | thêm `WY_MAX_OUTER_RATIO`, `WY_AR_RETRACE_MULT`, `WY_STA_MIN_AR_FRAC`, `WY_NEW_RANGE_*`, `WY_SOT_*` |
| `WyRange.__slots__` | `class WyRange` (`:622`) | thêm `CxI0`, `ClimaxVsa`, `MoveMaxPullback`, `Pivots`, `SotUp`, `SotDn`, `Bias`, `ErLegs`, `BornFromBreak`, `Provisional` |
| `_mark_outer` | `WyMarkOuter` (`:1315`) | bỏ `UA`/`DA` khỏi họ nhãn |
| `_minor_label` | `WyMinorLabel` (`:1336`) | luật `UT[B]`/`ST[B]` mới |
| `_revert_to_B` | `WyRevertToB` (`:1362`) | xoá event mồ côi |
| `_anchor_break_bar` | `WyAnchorBreakBar` (`:1378`) | mở cửa sổ + mốc biên chính |
| `_retro_phase_c` | `WyRetroPhaseC` (`:1412`) | kẹp trong range + đúng nửa |
| `_try_lps_and_phase_e` | `WyTryLpsAndPhaseE` (`:1447`) | 3 kết cục thay vì 2 |
| `_fire_break` | `WyFireBreak` (`:1516`) | nhánh `SIDEWAYS` |
| (mới) | `WyUpdatePivots`, `WyComputeSot`, `WyComputeEr`, `WyComputeBias` | hạ tầng mục 2 |
| `WyCat` | `WyCat` | thêm `"SOT"` → màu tím `#AB47BC` |

Build: `./build-wyckoff.sh` (nối `ProfileEngine.cs` + `UiKit.cs` + `WyckoffRunner.cs`, gọi
`~/quantower-libs/qw-build.sh`). Yêu cầu **0 warning / 0 error**. Nhắc lại luật đã vấp: mọi `using` phải
nằm **trong** `namespace`.

**Đối chiếu Python ↔ C#:** chạy cả hai trên cùng file M1, so số range mở / vẽ / loại, chiều cao, `kind`,
và chỉ số `i` của từng nhãn. Sai khác > 0 phải giải thích được, không được bỏ qua.

---

## 6. Bước 6 — Chấm lại vòng v6

1. Lưu vòng v5: `git mv research/wyckoff/grading research/wyckoff/grading_v5` (giữ nguyên như đã làm với
   `grading_v4`). ⚠️ Dùng đường dẫn **tuyệt đối** — vòng trước đã lỡ xoá 49 phiếu vì `cp ../../` sai gốc.
2. `render_range_for_grading.py`: bổ sung vào phiếu `.md` bảng nhịp đẩy SOT, bảng nỗ lực/kết quả, dòng
   `bias`, `climax_vsa`, tỷ lệ biên phụ/biên chính. PNG thêm nhãn SOT + dải nền vùng hấp thụ.
3. Render lại toàn bộ range.
4. Chấm bằng agent `wyckoff-giao-vien`, 10 agent song song, mỗi agent một lô.
5. Tổng hợp: trung vị, trung bình, phân bố, và **bảng đối chiếu v4/v5/v6**.
6. Cập nhật `rule-entry/wyckoff-thuat-toan-ve-giai-thich.md` lên v6 (mục 0b, 11 bảng tham số, 13.x thống kê).
7. Chụp lại ảnh minh hoạ trong `rule-entry/wyckoff-schematic-examples/`.

**Tiêu chí dừng:** trung vị ≥ 6/10 **và** không còn bài 1–2 điểm. Chưa đạt → lấy lỗi mới, lặp lại; đừng
tự cho là xong như v5.

---

## 7. Thứ tự thi công và điểm dừng báo cáo

| # | Việc | Nên chạy model/effort | Dừng báo cáo? |
|---|---|---|---|
| 1 | Bước 1 (9 vá lỗi) — Python | Sonnet, effort trung bình | ✔ báo bảng `climax_vsa` + tỷ lệ biên |
| 2 | Đo 1.8 / 1.9 / 2.3 / 4.6, **báo số** | Sonnet, effort thấp | ✔ **chốt ngưỡng cùng người học** |
| 3 | Bước 2 (SOT / nỗ lực-kết quả / bias) | Sonnet, trung bình | – |
| 4 | Bước 3 (nhãn Phase B) | Sonnet, thấp | ✔ chốt `UT[B]` hay `UT` |
| 5 | Bước 4 (range sinh từ cú phá) | **Opus, extended thinking** | ✔ chốt 4.5 (huỷ hay giữ mờ) |
| 6 | Bước 5 (port C#, build, đối chiếu) | Sonnet, trung bình | ✔ báo hash + kết quả build |
| 7 | Bước 6 (chấm lại + tài liệu) | Sonnet + agent giảng viên | ✔ báo bảng v4/v5/v6 |

Commit + push sau **mỗi** bước có sửa file (`git status` → `git add` → message tiếng Việt →
`git push origin main` tường minh → báo hash).

---

## 8. Ba câu cần người học chốt trước khi chạy bước tương ứng

1. **Nhãn Phase B**: `UT[B]`/`ST[B]` hay `UT`/`ST`? (mặc định plan: `UT[B]`/`ST[B]`)
2. **Range cũ khi bị thay thế**: xoá hẳn khỏi chart, hay giữ vẽ nét mờ `superseded`? (khuyến nghị: giữ mờ)
3. **Nhãn điểm neo của range sinh từ cú phá**: `BCLX?` / `SC?`, hay một tên khác?

Ba câu này **không chặn bước 1–3** — cứ chạy trước, hỏi khi tới bước 4.

## 9. Việc còn nợ, CỐ Ý chưa đưa vào v6

Ghi ra để không quên, không phải để làm ngay:

- **Chỉ MỘT range active tại một thời điểm** → range lồng/chồng nhau chưa vẽ được. Người học đã chốt
  *"chỉ vẽ range ở M1, chưa cần lồng"*.
- 36/47 range phải nhờ Phase C gán ngược mới có Phase C — tỷ lệ này cao bất thường, nhưng chưa rõ là lỗi
  hay là bản chất thị trường vàng M1.
- 10/47 range đóng ở trạng thái *"chưa rõ hướng"*.
- **Chưa hề backtest giá trị dự báo của cú phá.** Toàn bộ v4–v6 mới chỉ tối ưu cho *"giống bài giảng
  viên chấm"*, chưa chứng minh được là có tiền. Đây là việc phải làm sau khi trung vị đạt 6/10.
