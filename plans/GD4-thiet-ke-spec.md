# GĐ4 ⭐ — THIẾT KẾ đặc tả 3 kịch bản (pha đắt nhất, chỉ chạy 1 lần)

| | |
|---|---|
| **Model** | **Opus 5** |
| **Effort** | **xhigh** |
| **Cần trước** | GĐ1, GĐ2, GĐ3 (GĐ5 nếu đã xong thì càng tốt) |
| **Chi phí** | cao — nhưng chỉ đọc bản chưng cất, không đọc raw |
| **Output** | `quantower-entry-signal/SPEC_V7_3KB.md` (duy nhất) |

**Không implement, không backtest chiến lược ở pha này.** Toàn bộ giá trị nằm ở chỗ: đặc tả phải chi tiết và
có ngưỡng số tới mức GĐ6/GĐ7 chạy được ở effort thấp mà không cần tự phán xét.

---

=== PROMPT ===

Bạn đang thiết kế **WyckoffRunner v7 = 3 kịch bản** cho hệ tín hiệu vào lệnh M1 trên vàng (GC futures, Quantower). Output duy nhất của lượt này là **một file đặc tả**: `quantower-entry-signal/SPEC_V7_3KB.md`.

**Không viết code sản phẩm, không chạy backtest chiến lược.** Bạn được phép chạy **tối đa ~10 lệnh đo read-only** để kiểm tính khả thi (xem mục "Probe được phép"). Ngoài ra chỉ đọc và thiết kế.

## Yêu cầu gốc của người học (nguyên văn — bám sát, đừng đổi phạm vi)

> tôi vừa mới bổ sung các file bài giảng wyckoff trong folder data-export/wyckoff.
> phần 1 đến phần 12 là lý thuyết
> File tổng hợp chart sẽ là nơi review các bài tập của các học viên.
> Tuy nhiên trong đây thì đang giúp cho mình xác định các phase và các mốc quan trọng, chưa cho kịch bản trade.
>
> Kết hợp với các phần của pro trader có nói, thì ta sẽ triển khai thêm kịch bản:
> **Kịch bản 1:** Vẫn là entry là phá range chờ hồi và vào, giống như kịch bản 1, và đây sẽ là setup mạnh của ta.
> **Kịch bản 2:** Giá chạm vùng rồi phản ứng (như cũ)
> **Kịch bản 3:** Dựa theo wyckoff, ta xác định được swing low và swing high, tức là 2 biên cùng vùng nén, là nếu
> nó va chạm ở 2 cạnh đồng thời xác nhận bằng các delta footprint thì ta có thể scalp ngắn từ biên này sang biên
> còn lại, trade trong range luôn. Thường swing low và high cũng sẽ hợp lưu với vùng nào đó thì nó cũng mạnh đấy,
> và giá cũng sẽ chạy lên xuống trong range đó 1 thời gian nhất định rồi sẽ phá mạnh ra và tạo thành 1 xu hướng
> (tại đây thì lại dùng kịch bản 1 là trade tiếp)
>
> Target vẫn sẽ cải tiến 3 setup đó, và sẽ kết hợp nhiều yếu tố lại với nhau:
> - sử dụng tpo footprint vwap hay các vùng va chạm nhiều của wyckofff để vẽ range, vùng, bias của phiên trong ngày
> - sử dụng footprint, delta, bid, ask, độ dài nến, thân, râu, vsa vol để đoán lực mạnh hay yếu, hay đủ để xác nhận vào lệnh.

## Đọc trước — CHỈ những file này, theo thứ tự

1. `data-export/wyckoff/THEORY.md` và `WYCKOFF_RULES.md` (GĐ1) — lý thuyết đã chưng cất
2. `data-export/wyckoff/CHART_CASES.md` (GĐ2) — **đặc biệt mục "Cách xác định biên range trong thực tế"** và
   "Lỗi gán nhãn hay gặp"
3. `data-export/messages-with-pro-trader/RULES.md` rồi `TRANSCRIPT.md` — luật của pro trader CORVEN
4. `quantower-entry-signal/research/DATA_CAPABILITY.md` (GĐ3) — **đây là ràng buộc cứng**: không thiết kế
   feature mà file này nói không kiểm được
5. `quantower-entry-signal/WYCKOFF_V6_PLAN.md` — **toàn bộ**, đặc biệt §9 (giả thuyết đã bị bác), §10
   (không kiểm được offline), §11 (giới hạn phải nói ra), §12 (cách tái lập số)
6. `quantower-entry-signal/research/wyckoff/cbr_v6.py` — engine backtest hiện tại: `cfg`, `prepare`,
   `counter_sweep`, `run`, `evaluate`, `scan`, `mdd`. Phải hiểu để đặc tả khớp engine.
7. `quantower-entry-signal/research/entry_dxfeed.py` — loader + `build_zones`, `value_area`, `tpo_counts`
8. `quantower-entry-signal/WyckoffRunner.cs` — chỉ đọc `Scan()`, `InDeadWindow()`, nhánh reversal, khối
   `InputParameter` (để biết index nào còn trống)
9. `quantower-entry-signal/research/wyckoff/BASELINE.md` nếu GĐ5 đã xong

**KHÔNG đọc:** PDF/PPTX gốc, ảnh gốc, các file `research/*.py` khác (phần lớn là thử nghiệm đã chết) — trừ
`research/imp_reversal_sweep.py` nếu cần xem mẫu replicator.

## Bối cảnh v6 (đã có, đừng thiết kế lại từ đầu)

- Nhánh **CBR** = phá range → hồi 60–100% → vào; gate: thuận xu hướng (proxy `close` vs `close[-480]`, tol 1.0),
  đúng phía VWAP, lọc thanh khoản (`vma ≥ 0.75×` trung bình trượt 1000 nến), VSA phá ≥ 2.0, lọc phiên chết.
- Nhánh **QUAY_DAU** = đảo chiều tại VWAP, TP 1.5R.
- Đòn bẩy mạnh nhất tìm được: **BREAK SẠCH** — bỏ cú phá nếu trong 20 nến trước có cú quét hụt cạnh **đối diện**
  rồi đóng lại (phân hoạch: SẠCH n=29 WR 58.6% MDD 2R vs CÓ QUÉT NGƯỢC n=26 WR 34.6% MDD 11R).
- **Giả thuyết Wyckoff hiểu theo nghĩa hẹp đã bị bác:** bắt buộc có spring/upthrust trước cú phá → n=26,
  WR 34.6%, tháng 6 âm. Luật đúng là **ngược lại**. Đọc §9 để không lặp lại 5 giả thuyết đã chết.
- Số v6 hiện tại (dxFeed, 5–7/2026, nhánh CBR): sau sửa khung giờ + BREAK SẠCH + retrace 60–100% + RR4 →
  n=33, WR 48.5%, +47R, EV +1.42, MDD 3R. Giữ RR3 thì WR 57.6%, +43R.

## Probe được phép (tối đa ~10 lệnh, read-only, phải dán output thật)

Chỉ để trả lời câu **"kịch bản này có đủ n để kết luận không"**, ví dụ:
- Trên dxFeed 5–7/2026: có bao nhiêu cửa sổ M1 dài 30–120 nến thoả "range" theo định nghĩa bạn dự định
  (≥2 lần chạm mỗi biên, độ rộng trong khoảng X)? → nếu đếm ra < 30 range thì kịch bản 3 không đủ n,
  phải nới định nghĩa hoặc mở rộng cửa sổ dữ liệu, và phải nói ra trong đặc tả.
- Phân bố độ rộng range (theo "giá") để chọn ngưỡng min/max hợp lý thay vì bốc số.
- Số phiên có IB / VA đọc được từ `TPO-chart-daily.csv`.

**Không** được chạy backtest chiến lược rồi đưa số WR vào đặc tả. Đặc tả nêu **ngưỡng cần đạt**, không nêu
kết quả dự đoán.

## `SPEC_V7_3KB.md` — nội dung bắt buộc

### §0. Tóm tắt 30 giây
3 kịch bản là gì, cái nào là setup chính, thứ tự implement, và **một câu** nói rõ đâu là rủi ro overfit lớn nhất.

### §1. Từ vựng & quy ước
- Đơn vị: **"giá"** (1 giá = 10 tick), tick = 0.1. Mọi ngưỡng phải ghi rõ đơn vị.
- Múi giờ: **UTC** trong mọi tính toán (dxFeed `Time left` là UTC — xem `DATA_CAPABILITY.md`).
- Mã kịch bản: `KB1`, `KB2`, `KB3`. ⚠ Cảnh báo: `research/kb3_climax_break.py` cũ dùng "KB3" với nghĩa **khác**
  (climax phá cụm) — đặc tả phải yêu cầu module mới đặt trong `research/wyckoff/v7/` với tên không trùng.
- Nến-đóng-only: mọi quyết định chỉ dùng dữ liệu tới hết nến `i`; nêu rõ quy tắc này áp cho từng feature.

### §2. Tầng BIAS phiên (dùng chung 3 kịch bản)
Đặc tả thuật toán dựng bias trong ngày từ **TPO daily/m30 + VWAP + vùng va chạm nhiều**:
- Input cột nào của file nào, cập nhật lúc nào trong phiên (chú ý: bias phải tính từ **phiên trước**, dùng
  VA/POC của phiên đang chạy là look-ahead).
- Đầu ra bias: dạng gì (`+1/0/−1`? kèm độ tin cậy?), và **dùng để làm gì** ở từng kịch bản.
- So sánh với proxy xu hướng hiện tại (`close` vs `close[-480]`): bias TPO **thay thế** hay **cộng thêm**?
  Phải nêu rõ và thiết kế thí nghiệm A/B để phân xử.

### §3. Tầng ĐO LỰC (dùng chung)
Bảng feature, mỗi dòng: `tên | công thức chính xác (cột/biến, cửa sổ) | ngưỡng đề xuất + khoảng sweep | bộ dữ liệu | dùng ở KB nào | look-ahead? `
Phải phủ: delta nến, `Delta %`, bid vs ask volume, CVD/phân kỳ, độ dài nến, thân/râu, `cpos`, VSA ratio,
và (nếu `DATA_CAPABILITY.md` cho phép) imbalance/absorption từng mức giá.
Nêu rõ **feature nào chỉ có trên fp-m1 (6 tháng)** → hệ quả: phải test trên fp-m1, và số không so trực tiếp
được với số dxFeed.

### §4, §5, §6 — mỗi kịch bản một mục, khuôn CỐ ĐỊNH

Với **KB1 (phá range → hồi → vào)**, **KB2 (chạm vùng → phản ứng)**, **KB3 (scalp biên↔biên trong range)**:

1. **Một câu định nghĩa bằng cơ chế đấu giá** (vì sao edge tồn tại), không phải mô tả hình dạng.
2. **Neo vào luật nào** — mã `WY##` / `R#` + **trích nguyên văn** câu của tài liệu/pro trader.
3. **Bối cảnh cần có** — range/vùng/bias: pseudocode chính xác, tên biến, cửa sổ, ngưỡng, đơn vị.
4. **Điều kiện kích hoạt (arm)** và **điều kiện vào (entry)**, tách rời, nến-đóng-only.
5. **SL / TP / cách tính R.** ⚠ KB3 có **R biến thiên** (TP là biên đối diện, không phải bội số R cố định) →
   phải đặc tả rõ: R = |entry − SL|, TP = biên đối diện trừ buffer, và **điều kiện bỏ qua lệnh nếu
   (khoảng cách tới biên đối diện)/R < ngưỡng tối thiểu**. Engine `cbr_v6` hiện dùng RR cố định → nêu rõ
   phải sửa `evaluate()` thế nào.
6. **Gate nào ÁP / gate nào MIỄN.** Chú ý: KB3 nghịch đà theo bản chất → gate "thuận xu hướng" của v6 sẽ
   giết sạch. Đề xuất cụ thể (ví dụ: KB3 chỉ chạy khi proxy xu hướng = 0) và **thí nghiệm để kiểm**.
7. **Định tuyến & loại trừ lẫn nhau.** Khi range vỡ, KB3 phải dừng và KB1 vào việc (đúng ý người học:
   "phá mạnh ra thành xu hướng → lại dùng kịch bản 1"). Đặc tả trạng thái range: `đang hình thành / hợp lệ /
   đang vỡ / đã vỡ`, và điều kiện chuyển. Nêu rõ **quy tắc 1 vị thế tại một thời điểm** cho backtest portfolio.
8. **Tham số**: bảng `tên | mặc định đề xuất | khoảng sweep | lý do chọn`. Mặc định phải có lý do từ cơ chế
   hoặc từ probe, **không bốc số**.
9. **PASS / KILL bằng số** — phần quan trọng nhất, GĐ6/GĐ7 sẽ dùng đúng ngưỡng này:
   - `n` tối thiểu để được kết luận (đề xuất ≥ 25; dưới đó ghi "không kết luận")
   - WR / EV/lệnh / MDD tối thiểu
   - **cả 3 tháng dương** hay được phép 1 tháng âm nhỏ? nêu rõ
   - **OOS thô**: chia đôi cửa sổ, cả 2 nửa phải dương
   - **Partition test bắt buộc**: mọi bộ lọc phải trình cả nhóm bị loại; nhóm bị loại phải tệ hơn rõ ràng,
     nếu không thì bộ lọc chỉ là nhiễu → KILL
   - Điều kiện **KILL dứt điểm** (bỏ hẳn kịch bản/feature, không tinh chỉnh thêm)
10. **Thứ tự implement + điểm dừng**: bước nào trước, sau mỗi bước phải in bảng gì, dừng lại khi nào.

### §7. Danh sách giả thuyết cần test, xếp hạng
Mỗi giả thuyết: phát biểu **có thể bác được**, cách test (config nào, so với gì), n dự kiến, và **kết quả nào
sẽ bác nó**. Xếp theo (giá trị kỳ vọng ÷ công sức). Đánh dấu rõ cái nào **đã bị bác trong v6** để đừng làm lại.

### §8. KHÔNG kiểm được offline
Feature/ý tưởng chỉ dùng được khi chạy live. Quy tắc: **không đưa vào mặc định**, chỉ để dạng tham số tắt sẵn.

### §9. Sổ rủi ro overfit
Ghi cụ thể: cửa sổ dữ liệu là 5–7/2026 (vàng đang tạo đỉnh → **chế độ thị trường**, không phải cấu trúc);
dxFeed là proxy YẾU; chưa mô hình spread/slippage; giả định SL trước TP trong cùng nến (bi quan). Với mỗi rủi ro:
**cách giảm thiểu cụ thể** (mở rộng cửa sổ dxFeed lên 9 tháng? đối chứng fp-m1? khoá tham số?).

### §10. Bản đồ port sang C#
Với mỗi feature mới: sẽ thành `InputParameter` index nào (kiểm index còn trống trong `WyckoffRunner.cs` —
lệnh kiểm trùng: `grep -oP 'InputParameter\("[^"]*",\s*\K\d+' WyckoffRunner.cs | sort -n | uniq -d`),
tên tiếng Việt hiển thị, mặc định, và **rủi ro parity** (chỗ Python và C# dễ lệch nhau).

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **Không bịa số.** Số nào trong đặc tả phải là (a) output probe vừa chạy, hoặc (b) trích từ `V6_PLAN`/
   `DATA_CAPABILITY.md` có ghi nguồn. Không có nguồn → ghi là **ngưỡng đề xuất cần kiểm**, không trình bày như dữ kiện.
3. Bám **cơ chế**, không bám câu chữ. Tách **định nghĩa gốc** vs **hệ quả điển hình** — đừng lấy mô tả ca điển
   hình làm điều kiện lọc (lỗi này đã làm hỏng giả thuyết Wyckoff lần trước).
4. Nếu tài liệu Wyckoff và luật pro trader **xung đột** → nói rõ xung đột, phân xử bằng cơ chế đấu giá, và
   thiết kế thí nghiệm để dữ liệu quyết, đừng chọn bên theo cảm tính.
5. Repo **PUBLIC**: không hardcode token.
6. Không publish lên Claude Artifacts.
7. Xong → **commit + push `origin main`**.
8. Trung thực: chỗ nào bạn không đủ cơ sở để chốt ngưỡng thì ghi `CẦN QUYẾT Ở GĐ6` kèm cách quyết, đừng bốc số cho đủ mục.

## Xong khi nào

- [ ] `SPEC_V7_3KB.md` có đủ §0–§10
- [ ] Cả 3 kịch bản có đủ khuôn 10 điểm, trong đó **PASS/KILL đều là số cụ thể**
- [ ] KB3 có đặc tả **R biến thiên** và nói rõ phải sửa `evaluate()` của `cbr_v6.py` thế nào
- [ ] Có đặc tả **định tuyến 3 kịch bản + quy tắc 1 vị thế**
- [ ] Có ≥ 6 giả thuyết xếp hạng, mỗi cái nêu rõ "kết quả nào sẽ bác nó"
- [ ] Có bảng port C# với index `InputParameter` **đã kiểm không trùng**
- [ ] Đã probe thật để chốt tính khả thi n của KB3 (dán output)
- [ ] Đã commit + push

Cuối lượt báo ngắn: 3 kịch bản chốt thế nào, **thứ tự implement**, giả thuyết số 1 đáng thử nhất, và rủi ro overfit lớn nhất.
