# PLAN-LAN-CHAM — định nghĩa "một lần chạm" + độ rộng vùng theo giá + nhãn mới cho Vùng Canh Lệnh

Fable viết 2026-10-22 cho Opus implement + backtest. Đọc trước: `PLAN.md`, `README.md`, `research/report/VCL-VONG-3.md` (bảng tra, đặc tả),
`VCL-VONG-4.md`, `MAP15.md`, `QUAY-LAI.md`, `M1-PHU.md`, `research/vcl4.py` (engine chuẩn), `VclCore.cs`, `benzo-trader/research/kernel.py`.

**Dữ liệu chính (đổi so với vòng 1–4):** `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d` (`.csv` + `_bars.csv`), giờ UTC,
86 333 nến M1, 65 phiên (2026-07-23 → 10-21), một hợp đồng GCZ26. Kernel gắn cờ `thin` (volume < 20% trung vị — 4 phiên đầu 07-23…07-27 chắc chắn
bị loại) và `splice` (±2 phiên quanh chỗ nối hợp đồng; GCZ26 là một hợp đồng nên kỳ vọng không có — Opus phải in số phiên bị cờ). **Ghi rõ số phiên còn lại.**
File 29 ngày (0816–0915) chỉ dùng **đối chiếu** với vòng 1–4, không làm nguồn chính.

## 0. Yêu cầu của người học (nguyên văn ý) và ràng buộc trung thực

- **(a) Nhãn mỗi vùng chỉ còn 4 thứ:** vùng bao nhiêu giá (lo–hi, độ rộng **bằng giá**) · số điểm · % chạm rồi **đảo chiều** · % bị **xuyên phá**.
  Bỏ hẳn ký hiệu loại mốc B/B15/C/D. Bỏ bảng ghim góc phải.
- **(b) ⭐ Một lần chạm:** *giá leo lên vùng, rồi NEO Ở LẠI trong/sát vùng vài nến, rồi mới bật và đi chỗ khác = MỘT lần chạm.*
  Không được coi "chạm" là 1 nến vừa chạm biên. (Mọi phép đếm cũ — vcl4 `touch`, MAP15, M1-PHU — đều đếm "giá đóng vào vùng từ ngoài", tức 1 nến.)
- **(c) Trung thực:** 3 lần đo độc lập (SR-KET-QUA 65 phiên, VCL v2 đối chứng khớp khoảng cách, MAP15 bản đồ dời) đều cho **% bảo vệ ≈ đối chứng**,
  **P(chạm) chỉ phụ thuộc khoảng cách**. Nhãn mới là **tần suất lịch sử mô tả**, KHÔNG hứa lợi thế. Kế hoạch phải sẵn sàng kết luận "≈ đối chứng".
- **(d) ⭐ Độ rộng vùng (bổ sung 2026-10-22):** người học scalp, **SL một lệnh ≤ 4 giá (USD)**. Vùng rộng 6–7 giá là quá rộng. Độ rộng vùng phải nằm trong
  **[2 giá, 5 giá] tuyệt đối theo USD**, không phình theo u; triết lý *vùng càng nhỏ vừa đủ càng tốt*. Engine hiện kẹp [1u, 4u] với u ≈ 1,7 (p90 = 3,1)
  ⇒ vùng có thể rộng tới 6,8–12 giá — vi phạm. Mọi ngưỡng của "lần chạm" cũng phải **tính bằng giá tuyệt đối**, không theo u.

Tham khảo ngoài (2 lượt tìm; không có định nghĩa học thuật nào về "neo" nhiều nến, chỉ quy ước thực hành):
- Osler 2000 / Chung & Bellotti 2021 (đã dùng ở `SR-KET-QUA.md`): "bật" = vào dải bằng giá đóng rồi thoát cùng phía; không gộp nhiều nến.
- Script thực hành (LuxAlgo, TradingView `zY9x29uS`): đỉnh/đáy mới trong dung sai của mức cũ = **một lần chạm thêm** của mức cũ — gộp theo khoảng cách giá.
  [luxalgo.com](https://www.luxalgo.com/library/concept/support-level.md) · [tradingview.com/script/zY9x29uS](https://vn.tradingview.com/script/zY9x29uS)
- NexusFi: "phá 1 lần đổi vai, phá lần 2 vô hiệu" — trùng luật `breaks ≥ 2 ⇒ chết` hiện có. [nexusfi.com](https://nexusfi.com/showthread.php?p=811339)
- Wikipedia: "nhiều lần chạm mà không xuyên", không nói cách đếm. [wikipedia](https://en.wikipedia.org/wiki/Support_and_resistance)

⇒ Không có chuẩn sẵn. Tự định nghĩa, biện luận bằng cơ chế, kiểm độ nhạy.

---

## 1. ĐỘ RỘNG VÙNG [2, 5] GIÁ — thay đổi engine (vcl5 = vcl4 + một luật kẹp)

Giữ nguyên ứng viên, gộp đơn liên kết ≤ 1,0u, đệm 0,5u mỗi phía, chọn bộ, chống nhấp nháy. **Chỉ đổi bước kẹp độ rộng** trong `build_zones`:

| Cũ (v4) | Mới (v5) |
|---|---|
| rộng < 1u ⇒ nới đều quanh tâm tới 1u | rộng < **2,0 giá** ⇒ nới đều quanh tâm tới 2,0 giá |
| rộng > 4u ⇒ tách tại khe lớn nhất (đệ quy) | rộng (đã đệm) > **5,0 giá** ⇒ tách tại khe lớn nhất (đệ quy) |
| 2 vùng kề chồng nhau ⇒ cắt giữa | như cũ |

**Chọn "tách tại khe lớn nhất", không chọn "giữ lõi dày nhất"**, vì:
1. Tách giữ **mọi mốc** (mỗi mốc vẫn thuộc một vùng); "giữ lõi" vứt mốc ngoài rìa, mà mốc đó vẫn là chỗ giá từng đảo chiều — người học mất mốc mà không biết.
2. Tách cho vùng **nhỏ hơn hoặc bằng** giữ-lõi: lõi dày nhất của một cụm rộng vẫn bị kẹp 5 giá; tách tại khe lớn nhất chia cụm thành các mảnh có khe trống ở giữa, mỗi mảnh gọn hơn.
3. Đã có sẵn trong Python lẫn C# (`_split`, `BuildZones`), có test; chỉ đổi hằng số ⇒ ít rủi ro lỗi port.
4. Luôn kết thúc: một mốc đơn sau đệm rộng 1u ≤ 3,1 giá (p90 u) < 5; hai mốc cách ≤ 1u + đệm = 2u ≤ 6,2 ⇒ tách thành 2 mốc đơn. (Nếu u > 5 — chưa từng thấy — mốc đơn sẽ rộng > 5: kẹp đều quanh mốc về 5 giá, ghi cảnh báo.)

Đệm 0,5u vẫn theo u (nhiễu nến lớn thì vùng cần đệm hơn), nhưng tổng độ rộng **không bao giờ vượt 5 giá** và **không dưới 2 giá**. Hệ quả cần đo (mục 4.1b):
phân phối độ rộng trước/sau (trung vị, p90, % vùng > 4 giá, % vùng = 2 giá do nới), số vùng hiển thị, đổi vùng/giờ, tuổi thọ (vệ sinh v4 có thể xấu đi vì nhiều vùng hơn).
Độ nhạy sàn/trần: **1,5–4 · 2–5 (chốt) · 2–6** — chỉ báo, không chọn lại.

⚠ Bài học MAP15: vùng rộng "giữ được" nhiều hơn chỉ vì rộng (va đập ≥5 lần: 48% vs bản đồ dời 51%). Vùng hẹp hơn ⇒ xuyên phá nhiều hơn là **hình học**, không phải vùng yếu.
Nhãn phải phản ánh đúng số, và README nói rõ điều này; **không** được để vùng rộng trông "mạnh" hơn.

---

## 2. ĐỊNH NGHĨA MỘT LẦN CHẠM (episode)

Mọi thứ tính **trên nến đã đóng**, chỉ dùng nến ≤ nến hiện tại. Cùng một luật cho Python (backtest) và C# (live).

Ký hiệu: vùng có biên `lo, hi` (biên HIỆN TẠI của vùng tại nến đó — cả Python lẫn C# dùng biên hiện tại ⇒ parity tự nhiên). Nến t có `O,H,L,C`;
`C₋` = giá đóng nến t−1 cùng phiên (nến đầu phiên: dùng `O` của chính nó).

Ba hằng số, **tính bằng giá (USD), chốt trước khi nhìn TEST**:

| Tên | Chọn | Ý nghĩa | Độ nhạy phải chạy |
|---|---|---|---|
| τ (dung sai chạm) | **0 giá** | râu chạm tới biên vùng là chạm | 0 · 0,5 giá |
| E (ngưỡng thoát) | **2,0 giá** | giá đóng cách biên ≥ 2 giá mới là "đã đi chỗ khác" | 1 · 2 · 3 giá |
| G (khoảng nghỉ xác nhận) | **5 nến** | thoát rồi mà chạm lại trong ≤ G nến ⇒ vẫn lần chạm cũ | 5 · 10 · 20 |

### 2.1 Bắt đầu (i)

Lần chạm **bắt đầu tại nến t** khi vùng chưa có lần chạm đang mở và **dải giá nến chạm vùng**:
`max(C₋, H) ≥ lo − τ` **và** `min(C₋, L) ≤ hi + τ`. ("Cầu" từ `C₋` tới nến t để không bỏ sót nến nhảy qua vùng.)

**Vì sao râu, không phải giá đóng?** (b) nói về NEO và ĐI CHỖ KHÁC — phần quan trọng là lúc KẾT THÚC; mở đầu chỉ cần sự kiện vật lý "giá đã tới vùng".
Nếu bắt đầu bằng giá đóng thì nến râu dài quét vào vùng rồi đóng xa (nến bật rõ nhất bằng mắt) **không bao giờ được đếm** — người học sẽ thấy máy đếm sai.
Dùng râu: nến đó = 1 lần chạm, kết thúc ngay (nếu đóng cách biên ≥ 2 giá) = đảo chiều.

**Vì sao τ = 0?** Vùng đã đệm 0,5u quanh mốc; "sát vùng" được xử lý ở phần neo (lân cận ±E). Thêm dung sai nữa là đệm hai lần. 0,5 giá chỉ chạy để xem có nhạy không.

**Vai của lần chạm = phía giá tới**, chốt tại nến bắt đầu, KHÔNG dùng `Side` của engine:
- `C₋ < lo` ⇒ tới từ dưới ⇒ vùng là **KHÁNG CỰ** trong lần chạm này; `C₋ > hi` ⇒ **HỖ TRỢ**;
- `lo ≤ C₋ ≤ hi` (vùng mới hiện đã ôm giá / biên vừa dịch trùm giá) ⇒ **không rõ phía**: vẫn theo dõi, đếm vào n, nhưng không xếp đảo/xuyên. Opus báo tỉ lệ.

⚠ Hai quy ước `side` trong code NGƯỢC nhau: ứng viên (`vcl.break_update`, `_side`) +1 = giá ở trên = hỗ trợ; vùng hiển thị (`VZone.Side`, `rec.side`) +1 = vùng trên giá = kháng cự.
**Không dùng cả hai cho lần chạm** — enum riêng `Vai { KhangCu, HoTro, KhongRo }`.

### 2.2 Đang mở — neo (iii, phần đầu)

Khi lần chạm đang mở, mỗi nến đóng xét **vùng lân cận** `[lo − E, hi + E]` (E = 2 giá):
- `C` trong vùng lân cận, hoặc dải nến chạm vùng ⇒ nến này **đang neo**; bộ đếm thoát = 0.
- `C < lo − E` ⇒ **đã thoát xuống** (tạm); `C > hi + E` ⇒ **đã thoát lên** (tạm). Bộ đếm thoát += 1; ghi phía thoát.

Râu vượt `hi + E` rồi đóng lại trong lân cận ⇒ **không phải thoát** (chỉ giá đóng quyết định — "râu quét qua rồi đóng lại").
Số nến neo (`dwell`) = từ nến bắt đầu tới nến thoát cuối (không tính G nến xác nhận). Không giới hạn trên; báo p50/85/95 và % > 120 nến.

### 2.3 Kết thúc (ii) và khoảng nghỉ (iii, phần sau)

Lần chạm **chốt** tại nến mà bộ đếm thoát đạt **G**: G nến liên tiếp đóng ngoài lân cận và không nến nào chạm lại vùng. Kết cục theo **phía thoát cuối** so với **phía tới**:
- thoát về **phía cũ** (kháng cự: xuống; hỗ trợ: lên) ⇒ **ĐẢO CHIỀU**; thoát sang **phía kia** ⇒ **XUYÊN PHÁ**.

Trong G nến chờ, có nến neo trở lại ⇒ bộ đếm về 0, vẫn là lần cũ (gộp). Hệ quả: "phá giả" (đóng trên `hi + 2` rồi 3 nến sau quay vào vùng rồi rơi dưới `lo − 2`) = **một lần chạm, đảo chiều**.

Ba phương án khoảng nghỉ đã cân nhắc:
1. Không có (chốt ngay nến thoát đầu) — giá lắc quanh `lo − 2` sinh 2–3 lần cho 1 cú va: đúng cái người học không muốn.
2. Chốt ngay rồi **rút lại** nếu chạm lại trong G nến — đúng ý nhưng nhãn live đổi số ngược xuôi, khó tin.
3. **Chốt sau G nến yên** (chọn) — không bao giờ rút lại; trả giá bằng nhãn trễ G phút. Scalp M1 chịu được 5 phút.

**Vì sao G = 5?** Không có lý thuyết; 5 phút là cỡ "thấy giá đã rời đi" trên M1, trùng k=5 swing M1 trong repo. Độ nhạy 5/10/20; lệch > 5 điểm % thì G là tham số nhạy, phải báo.

**Vì sao E = 2,0 giá?** (đổi từ 1,0u theo ràng buộc (d)) — (1) tuyệt đối, không phình khi u tăng; (2) = một nửa ngân sách SL 4 giá của người học: giá đi quá biên 2 giá là
nửa SL đã mất, hợp lý gọi là "đi chỗ khác"; (3) ≈ 1,2u ở u trung vị, lớn hơn một nến M1 thường (1,7) nên một nến nhiễu không kết thúc lần chạm; (4) 1 giá quá nhỏ (dưới 1 nến),
3 giá gần bằng cả SL. Lưu ý hình học: đảo chiều chỉ cần đi 2 giá từ biên gần, xuyên phá phải đi hết vùng (2–5 giá) + 2 ⇒ **% đảo chiều > 50% ngay cả với vùng ngẫu nhiên**, và
**vùng hẹp xuyên nhiều hơn vùng rộng** chỉ vì hình học. Con số tuyệt đối trên nhãn phần lớn là hình học; chỉ hiệu so với đối chứng cùng độ rộng có nghĩa.

⚠ Engine vẫn có luật chuyển vai riêng `BREAK_U = 1,0u` (giá đóng xuyên cả vùng ≥ 1u). Vòng này **không đổi** nó (đổi = đổi chọn bộ). Backtest 4.1c đo tỉ lệ hai luật bất đồng
(engine đã "xuyên" mà lần chạm kết cục đảo chiều, và ngược lại); nếu > 15% thì đề xuất vòng sau đổi `BREAK_U` thành 2 giá tuyệt đối cho nhất quán.

### 2.4 Lần chạm chưa kết thúc (iv)

| Tình huống | Backtest | Live (C#) |
|---|---|---|
| Hết phiên (khoảng trống > 30 phút) khi đang **neo** | **CHƯA RÕ**, tính vào mẫu số | như backtest |
| Hết phiên khi **đã thoát tạm** (đếm 1..G−1) | chốt theo phía thoát hiện có | như backtest |
| Vùng **rời bộ / chết / mất mã** khi đang mở | như hết phiên | như backtest; xoá trạng thái mã đó |
| Phiên bị cờ `thin`/`splice` hoặc lần chạm vắt qua phiên bị cờ | **bỏ** | — |
| **Hết dữ liệu** | bỏ | nhãn "đang chạm", chưa cộng vào n |

Bất biến: **% đảo + % xuyên + % chưa rõ + % không rõ phía = 100** trên mọi bảng. Nhãn hiện đảo/xuyên; phần còn lại trong README (hoặc trên nhãn nếu ≥ 10%, mục 3).

### 2.5 Vai vùng và đổi vai (v)

- Vai chốt **tại lúc bắt đầu theo phía giá tới** ⇒ vùng bị xuyên phá thì lần chạm kế tiếp **tự động** mang vai mới. Luật `breaks/side` của ứng viên vẫn chạy độc lập để chọn bộ.
- Lịch sử mỗi vùng ghi theo **mã vùng (eid)** và **vai**: `n, đảo, xuyên, chưa rõ` × {kháng cự, hỗ trợ}. Nhãn hiện tổng hai vai; backtest đo riêng (4.7).
- Giới hạn: **eid chỉ sống khi vùng trong bộ hiển thị**; rời bộ rồi quay lại ⇒ mã mới, lịch sử về 0. Chấp nhận vòng này (rủi ro 7.5).

### 2.6 Máy trạng thái (một bản, dùng cho cả Python và C#)

```
trạng thái mỗi (eid): NGOAI | MO(vai, batDau, phiaThoat ∈ {0,+1,−1}, demThoat)
mỗi nến đóng t, với mọi vùng đang hiển thị (lo, hi hiện tại):
  cham        = max(Cprev,H) ≥ lo−τ  và  min(Cprev,L) ≤ hi+τ
  trongLanCan = lo−E ≤ C ≤ hi+E
  NGOAI: nếu cham ⇒ MO(vai = Cprev<lo ? KhangCu : Cprev>hi ? HoTro : KhongRo, batDau=t, phiaThoat=0, demThoat=0); xử lý tiếp nến này như MO
  MO:    nếu cham hoặc trongLanCan ⇒ demThoat=0, phiaThoat=0
         ngược lại ⇒ phiaThoat = (C > hi ? +1 : −1); demThoat += 1
                     demThoat == G ⇒ CHỐT: ketCuc = (vai==KhangCu && phiaThoat==−1) || (vai==HoTro && phiaThoat==+1) ? DAO : XUYEN
                                           (vai==KhongRo ⇒ KHONG_RO_PHIA); cộng vào lịch sử eid; về NGOAI
  hết phiên / vùng rời bộ: MO với demThoat>0 ⇒ CHỐT theo phiaThoat; demThoat==0 ⇒ CHUA_RO; về NGOAI
nến đầu phiên: Cprev := O của nến đó.  Ca mơ hồ "cham đúng mà C ngoài lân cận" (râu cực dài): cham THẮNG — chưa thoát.
```

Thứ tự trong `Push`: chạy máy trạng thái **sau** khi đã chọn bộ (`Display`) của nến t, dùng `lo/hi` của bộ mới. Mã có trong `_prev` mà không còn trong `Display` ⇒ "rời bộ" trước khi xoá.

---

## 3. SỐ ĐO TRÊN NHÃN: % lấy từ đâu

- **A. Bảng toàn cục** (tần suất gộp theo pha phiên × bin độ rộng): số giống nhau cho mọi vùng cùng ô.
- **B. Lịch sử riêng từng vùng**: vùng sống trung vị ~1 giờ ⇒ n ≈ 1–3; % sẽ là 0/50/100% — nhiễu, và 100% bị đọc là "vùng mạnh".
- **C. Trộn Bayes** % = (a·p + số đảo)/(a + n): a = 20, n = 3 (2 đảo): 55,7% so với 54% — không nhúc nhích; C ≈ A thêm một tham số và ảo giác khác biệt.

**Chọn A** vì mọi phép đo trước cho thấy xác suất không phụ thuộc vùng nào. Nhưng nhãn vẫn hiện **bảng kê thô của riêng vùng** (n, số bật, số xuyên) — là sự thật đã xảy ra, không phải ước lượng.
Hai phần tách bạch: *% = lịch sử chung*, *n = lịch sử riêng*.

Quy định bảng toàn cục:
- Ô = **pha phiên** (Á/Âu/Mỹ, tại nến bắt đầu) × **bin độ rộng** (2–3 / 3–4 / 4–5 giá) — thêm bin độ rộng vì (d) và hình học ở 2.3: vùng hẹp xuyên nhiều hơn, nhãn phải nói đúng. Có ô "mọi pha" từng bin.
- Ô cần **n ≥ 100** lần chạm đã chốt; thiếu ⇒ ô "mọi pha" cùng bin; vẫn thiếu ⇒ "—". Không chia theo lần thứ k trừ khi 4.6 chứng minh trên TEST.
- Hiện `n` của vùng: **có**. Chưa chạm: "chưa chạm". Đang mở: "đang chạm (lần k)".
- Nếu chưa rõ ≥ 10% ở ô nào ⇒ nhãn hiện thêm "chưa rõ ≈z%" ở ô đó.
- Tiêu chí **đăng ký trước** để đổi sang C: trên TEST, trong các vùng có ≥ 2 lần chạm đã chốt, "lần kế tiếp đảo chiều" khi lịch sử riêng toàn đảo phải cao hơn bảng toàn cục
  **vượt dải 5–95% của đối chứng** ở CẢ TRAIN và TEST và cùng dấu ở ≥ 2/3 tháng. Không đạt ⇒ giữ A. Kỳ vọng trung thực: không đạt.

---

## 4. "SỐ ĐIỂM"

Điểm có phải độ mạnh không? **Chưa chứng minh.** Điểm hiện tại (Σ trọng số loại × suy giảm tuổi × (1 + 0,3·min(chạm,5)) × 0,7^xuyên) là **thứ tự ưu tiên chọn vùng xa** và phá hoà;
chưa phép đo nào cho thấy vùng điểm cao bật nhiều hơn. Hệ số "chạm" trong điểm vẫn dùng định nghĩa cũ (1 nến).

**Mặc định giữ nguyên điểm** (đổi điểm = đổi chọn bộ = đổi mọi thứ). Backtest 5.8 đo đảo chiều theo tam phân vị điểm; nếu ≈ đối chứng thì README ghi "điểm = thứ tự xếp hạng, không phải độ mạnh",
nhãn vẫn giữ số vì người học muốn thấy. Thay thế (chỉ nếu 5.6 chứng minh, vòng sau): điểm = số lần chạm đã được tôn trọng theo định nghĩa mới. MAP15 đã đo "va đập ≥5 lần: 48% vs dời 51%" ⇒ kỳ vọng không.

---

## 5. THIẾT KẾ BACKTEST (Opus, Python)

**File mới:** `research/vcl5.py` (= vcl4 + luật kẹp [2,5] giá, import vcl4, **không sửa** vcl.py…vcl4.py; `build_zones` mới viết trong vcl5, truyền vào engine bằng tham số hoặc monkey-patch có kiểm soát)
và `research/lan_cham.py` → `report/LAN-CHAM.md` + `report/lan_cham_episodes.csv.gz`. Nến/u/phiên/pha/cờ: `kernel.py`. Chỉ đo phiên không `thin`, không `splice`, không phải phiên 0.

**Chia dữ liệu — chốt trước:** TRAIN = phiên có ngày ≤ **2026-09-15**, TEST = từ 2026-09-16 (đúng `kernel.split_train_end`, cùng mốc SR-KET-QUA; ước ~36 / ~25 phiên).
Mọi bảng in **TRAIN / TEST / gộp** và **từng tháng 8 / 9 / 10** (tháng theo ngày phiên), kèm ± nhị thức.

**Ngưỡng "khác đối chứng có ý nghĩa" — chốt trước:** thật nằm ngoài dải 5–95% của đối chứng **ở cả TRAIN và TEST**, cùng dấu, **và** cùng dấu ở ≥ 2/3 tháng, **và** |hiệu| > 2 sai số nhị thức của thật.
Thiếu một điều kiện ⇒ "≈ đối chứng". Không dùng từ "có xu hướng".

**Cẩn thận bắt buộc:** không nhìn trước (vùng tại nến i chỉ dùng nến ≤ i — tự kiểm bằng `test_vcl.py` kiểu cắt dữ liệu tại i cho vcl5 và cho máy trạng thái); giờ UTC (pha tính qua kernel `sm`);
không trộn hợp đồng; lần chạm vắt qua phiên bị cờ bị loại; `u` kernel như cũ.

Hàm lõi: `episodes(rec, bars, tau, E, G) -> DataFrame[eid, vai, bat_dau, thoat_cuoi, chot, dwell, ket_cuc, pha, thang, split, k, score_bat_dau, w_gia]` — **đúng máy 2.6**, dùng lại cho parity C#.

### 5.1 Đếm theo định nghĩa mới (τ=0, E=2 giá, G=5) trên vcl5
- a) số lần chạm; phân bố lần chạm/vùng (0,1,2,3,≥4); dwell p50/85/95, % > 120 nến; % đảo/xuyên/chưa rõ/không rõ phía theo pha × bin rộng, mọi pha, theo vai. **Bảng nhúng C#.**
- b) **độ rộng**: phân phối rộng vùng v4 vs v5 (trung vị, p90, % > 4 giá, % > 5 giá, % = 2 giá do nới); vệ sinh v4 vs v5 (số vùng hiển thị, đổi vùng/giờ, tuổi thọ trung vị, % nến trong vùng).
  Độ nhạy sàn/trần 1,5–4 / 2–5 / 2–6: số vùng, rộng trung vị, % đảo. Và **% đảo theo bin rộng, thật vs đối chứng cùng bin** — để chứng minh/bác "hẹp hơn ⇒ xuyên nhiều hơn là hình học".
- c) tỉ lệ bất đồng giữa luật xuyên của engine (`BREAK_U` 1u) và kết cục lần chạm.
- d) **đối chiếu** với file 29 ngày: chạy y hệt trên 0816–0915, in cạnh kết quả 90 ngày trong cùng khoảng ngày để thấy khớp.

### 5.2 So với phép đếm cũ "chạm 1 nến"
Trên cùng bộ vùng: (a) `touch` kiểu vcl4; (b) MAP15 (vào vùng → bảo vệ ≥ 2u / phá, 120 nến). Báo tỉ số số lần (cũ/mới), % bảo vệ cũ vs % đảo mới, **số lần cũ trung bình nằm trong 1 lần mới** (mức đếm trùng người học phản đối).

### 5.3 Độ nhạy
τ ∈ {0; 0,5 giá} × E ∈ {1; 2; 3 giá} × G ∈ {5; 10; 20} = 18 tổ hợp: số lần, dwell p50, % đảo/xuyên/chưa rõ (gộp). Tổ hợp chốt in đậm. Nhận xét: tham số nào làm % đảo lệch > 5 điểm.

### 5.4 Đối chứng (bắt buộc cả hai)
- **Đ1 — dời bản đồ** (MAP15): bộ vùng hiển thị của phiên dời cùng δ, |δ| ∈ [3, 15] giá, dấu ngẫu nhiên, cố định trong phiên, 50 lần; vùng dời sống đúng khoảng nến vùng thật sống.
- **Đ2 — khớp khoảng cách + độ rộng** (bài học v2): vùng giả cùng độ rộng, đặt ngẫu nhiên trong biên phiên trước ±2 giá, 50 lần; **cân lại theo bin** (khoảng cách giá đóng → cạnh gần tại nến vùng hiện, bin v3) × (bin rộng 2–3/3–4/4–5).
- Dạng kết luận: "thật X% ±e · Đ1 Y% [5–95%] · Đ2 Z% [5–95%]" theo TRAIN/TEST/tháng. Áp ngưỡng đã chốt.

### 5.5 Bền theo thời gian — TRAIN/TEST và 3 tháng; |Δ| > 5 điểm đánh ⚠.

### 5.6 Lần chạm thứ k ("tôn trọng tới khi bị phá")
k = 1, 2, 3+ theo thứ tự chốt trong eid: % đảo thật vs Đ1 vs Đ2. Thêm: k ≥ 2 **và mọi lần trước đều đảo** → % đảo lần này vs toàn cục vs đối chứng. Tiêu chí đăng ký ở mục 3.

### 5.7 Đổi vai sau xuyên phá
Lần chạm **ngay sau** một lần xuyên phá cùng eid (tất yếu vai mới): % đảo vs (a) lần đầu của vùng mới, (b) Đ1/Đ2 cùng điều kiện. Báo n; n < 40 ⇒ "không đủ mẫu".

### 5.8 Điểm có dự báo không — % đảo theo tam phân vị điểm (cắt theo TRAIN), thật vs Đ2.

### 5.9 Đầu ra cho C#
`static readonly int[,,] EPISODE = { pha 0/1/2 × bin rộng 0/1/2 × {đảo, xuyên, chưaRõ} }`, `EPISODE_ALL[bin, 3]`, số nguyên %, −1 nếu n < 100. Thời gian chạy mục tiêu ≤ 3 phút (86k nến, đối chứng 2 × 50).

---

## 6. THIẾT KẾ C# (VclCore / VungCanhLenh)

### 6.1 Engine
- `Vcl.WminGia = 2.0, WmaxGia = 5.0` thay `WminU/WmaxU`; `BuildZones` kẹp theo giá. Test gộp/kẹp/tách cập nhật. Parity lại với `vcl5.py` (mục tiêu 100% như vòng 4).

### 6.2 Trạng thái lần chạm
- `EpState { Vai Vai; int BatDau, PhiaThoat, DemThoat; }` trong `Dictionary<int eid, EpState> _ep`; `ZoneHist { int N, Dao, Xuyen, ChuaRo, KhongRo; … theo vai }` trong `_hist`.
- Hằng: `EpTau = 0.0, EpExit = 2.0 (giá), EpGapBars = 5`.
- Cuối `Push` (sau `Display`): (1) eid trong `_prev` không còn trong `Display` ⇒ "rời bộ" rồi xoá; (2) `newSess` ⇒ "hết phiên" cho mọi `_ep` **trước** nến đầu phiên; (3) máy 2.6 cho từng vùng trong `Display`, `Cprev = Bars[i−1].C` (đầu phiên: `bar.O`).
- `VZone` thêm `EpOpen, EpK, N, Dao, Xuyen, WBin`. Bỏ dùng `Mask/Types()` trên nhãn (giữ trường cho test).
- `VclTables`: thêm `Episode`/`EpisodeAll` (5.9). **Bỏ** `Reach/Sweep/Revert2u` khỏi UI; bảng góc phải xoá; giữ **một dòng** cảnh báo thiếu Volume Analysis.

### 6.3 Parity
`tools/ReplayCsv` xuất thêm mỗi nến mỗi vùng: `eid, ep_open, ep_vai, dem_thoat, n, dao, xuyen, chua_ro`. `research/parity_lan_cham.py` so với `lan_cham.episodes` từng nến; mục tiêu 100%.
Test C# mới: râu chạm rồi đóng xa 2 giá = 1 lần đảo; phá giả = 1 lần đảo; thoát rồi chạm lại nến thứ 3 ⇒ gộp; 5 nến yên ⇒ chốt; hết phiên khi neo ⇒ chưa rõ; rời bộ khi đã thoát ⇒ chốt;
không rõ phía; kẹp [2,5] giá với u = 1,0 và u = 3,1; không nhìn trước.

### 6.4 Nhãn tiếng Việt
Định dạng: `lo–hi (rộng giá) · điểm · đảo chiều ≈x% · xuyên phá ≈y% · lịch sử riêng`

```
4447,6–4451,2 (3,6 giá) · 68 điểm · đảo chiều ≈57% · xuyên phá ≈36% · đã chạm 3 (bật 2 · xuyên 1)
4439,0–4441,0 (2,0 giá) · 2 điểm · đảo chiều ≈52% · xuyên phá ≈42% · chưa chạm
4428,2–4433,2 (5,0 giá) · 32 điểm · đảo chiều ≈61% · xuyên phá ≈31% · đang chạm (lần 2)
4408,8–4412,4 (3,6 giá) · 12 điểm · đảo chiều ≈57% · xuyên phá ≈36% (xa)
```
(Các % trên là ví dụ minh hoạ định dạng, KHÔNG phải số đo.)
- **≈** báo đây là ước lượng lịch sử chung (cùng số cho mọi vùng cùng pha và cùng cỡ rộng). README một câu: *"% là tần suất ~60 phiên GCZ26 theo pha và độ rộng, giống nhau cho mọi vùng
  cùng ô; vùng giả cùng cỡ cũng cho ≈ chừng ấy (xem LAN-CHAM.md); vùng hẹp xuyên nhiều hơn là do hình học. Phần 'đã chạm…' là lịch sử thật của riêng vùng. Nhãn cập nhật trễ 5 nến."* Không bảng ghim.
- Chưa rõ ≥ 10% ⇒ thêm `· chưa rõ ≈z%`.
- Nhãn quá dài (`MeasureString`): rút "lịch sử riêng" thành `· 3 lần (2 bật)`; ưu tiên giữ lo–hi > đảo/xuyên > điểm > lịch sử riêng.
- Setting thêm duy nhất: `Hiện lịch sử riêng của vùng`. Không thêm ngưỡng số nào.
- Từ ngữ UI: "đảo chiều", "xuyên phá", "bật", "đã chạm", "đang chạm", "giá". Không episode/touch/dwell.

---

## 7. RỦI RO / ĐIỂM MƠ HỒ — Opus phải báo lại từng mục

1. **Kết quả ≈ đối chứng** (khả năng cao): nhãn vẫn hợp lệ (mô tả), nhưng README không được viết "vùng được tôn trọng x%".
2. **Hình học E và độ rộng**: đảo cần 2 giá, xuyên cần rộng + 2 ⇒ % đảo cao sẵn và tăng theo độ rộng. Báo thêm biến thể E đối xứng (thoát cách TÂM ≥ rộng/2 + 2) chỉ để minh hoạ.
3. **Kẹp [2,5] giá làm vệ sinh xấu đi** (nhiều vùng nhỏ hơn, đổi vùng/giờ tăng): nếu đổi vùng/giờ > 4 hoặc tuổi thọ < 30 phút thì báo, không tự thêm luật vệ sinh.
4. **"Không rõ phía" / "chưa rõ" > 10%** ⇒ định nghĩa có lỗ hổng; nêu 3 ca điển hình (ngày+giờ UTC).
5. **eid mất khi vùng rời bộ** ⇒ lịch sử riêng về 0; lần chạm trước khi vào bộ không đếm. Gợi ý vòng sau: khoá lịch sử theo mức giá làm tròn 0,5 (như `quay_lai.py` `key`).
6. **Hai quy ước side ngược nhau** (2.1) — lỗi dễ mắc nhất khi port.
7. **Biên dịch** khi lần chạm đang mở; biên dịch trùm `C₋` ⇒ lần mới "không rõ phía". Báo tần suất.
8. **Nến nhảy qua vùng** ⇒ bắt đầu và thoát trong 1 nến. Báo số ca.
9. **Dwell rất dài** (cân bằng hàng giờ): p95 và 3 ca dài nhất.
10. **Hai định nghĩa "xuyên" cùng tồn tại** (engine 1u vs lần chạm 2 giá) và **hai định nghĩa "chạm"** (điểm dùng 1 nến) — chấp nhận vòng này, đo bất đồng (5.1c).
11. **Nến rộng chạm 2 vùng kề** ⇒ 2 lần cho 1 cú giá; ± đánh giá thấp. Báo tỉ lệ.
12. **Dữ liệu 90 ngày không đồng nhất**: tuần đầu mỏng, tháng 10 chưa trọn; phiên bị cờ phải in danh sách. Chỉ một hợp đồng, một mùa; không ngoại suy.
13. Ca chưa phủ trong máy 2.6 ⇒ dừng và hỏi, không tự chế.

## 8. Giao nộp
- `research/vcl5.py`, `research/lan_cham.py`, `report/LAN-CHAM.md` (bảng 5.1–5.9, nhận xét ≤ 15 dòng, trung thực), `report/lan_cham_episodes.csv.gz`, test không nhìn trước cho vcl5 + máy trạng thái.
- Sau khi Fable duyệt số: `VclCore.cs`, `VungCanhLenh.cs`, `tests/`, `tools/ReplayCsv`, `parity_lan_cham.py`, `README.md` (viết lại mục 2, bỏ mục bảng), build `dist/`.
- Commit + push từng bước (quy tắc repo).
