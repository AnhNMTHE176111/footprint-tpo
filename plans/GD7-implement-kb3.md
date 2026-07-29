# GĐ7 — Implement + test KB3: scalp biên↔biên trong range (kịch bản MỚI)

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | high |
| **Cần trước** | GĐ4 (`SPEC_V7_3KB.md`), GĐ5 (`BASELINE.md`), nên có GĐ6 xong trước |
| **Chi phí** | cao (code mới nhiều nhất) |
| **Output** | `research/wyckoff/v7/kb3.py` + `research/wyckoff/RESULTS_KB3.md` + ảnh kiểm chứng range |

Đây là kịch bản **mới hoàn toàn**, và cũng là chỗ dễ tự lừa nhất: một bộ phát hiện range tồi vẫn cho ra số đẹp.
Vì vậy có 2 yêu cầu đặc biệt: **kiểm chứng bằng mắt** và **đo tỷ lệ xoay biên nền** trước khi bàn tới lệnh.

---

=== PROMPT ===

Việc của bạn: implement và test **KB3 — scalp ngắn từ biên này sang biên kia bên trong range** (theo Wyckoff: swing low và swing high = 2 biên vùng nén), theo đúng `SPEC_V7_3KB.md §6`.

Ý người học, nguyên văn:

> Kịch bản 3: Dựa theo wyckoff, ta xác định được swing low và swing high, tức là 2 biên cùng vùng nén, là nếu
> nó va chạm ở 2 cạnh đồng thời xác nhận bằng các delta footprint thì ta có thể scalp ngắn từ biên này sang biên
> còn lại, trade trong range luôn. Thường swing low và high cũng sẽ hợp lưu với vùng nào đó thì nó cũng mạnh đấy,
> và giá cũng sẽ chạy lên xuống trong range đó 1 thời gian nhất định rồi sẽ phá mạnh ra và tạo thành 1 xu hướng
> (tại đây thì lại dùng kịch bản 1 là trade tiếp)

## Đọc trước — chỉ những chỗ này

1. `quantower-entry-signal/SPEC_V7_3KB.md` — **§1, §2, §3, §6 (KB3), §7, §8, §9**
2. `data-export/wyckoff/CHART_CASES.md` — mục **"Cách xác định biên range trong thực tế"** (biên neo vào gì /
   bao nhiêu lần chạm / hỏng khi nào). Bộ phát hiện range phải khớp với cách giảng viên vẽ, không phải cách
   bạn tự nghĩ.
3. `research/wyckoff/BASELINE.md` và `RESULTS_KB12.md` (nếu GĐ6 xong)
4. `research/wyckoff/v7/` — dùng lại `loaders.py`, `features.py`, `engine.py`, `report.py` của GĐ6
5. `research/DATA_CAPABILITY.md` — mục per-level footprint: **chỉ 25 phiên** → xác nhận "delta footprint" ở
   mức nào là kiểm được

⚠ **Cảnh báo tên:** `research/kb3_climax_break.py` cũ dùng "KB3" với nghĩa **khác hẳn** (climax phá cụm).
Code mới đặt ở `research/wyckoff/v7/kb3.py`, không sửa file cũ, không import từ nó.

## Bước 0 — GOLDEN TEST
Với KB3 **tắt**, portfolio phải tái lập đúng kết quả của GĐ6 / `BASELINE.md`. Không khớp → **DỪNG**.

## Bước 1 — Bộ phát hiện range (làm cho đúng trước khi bàn tới lệnh)

Implement theo `SPEC §6` mục "bối cảnh cần có". Sau đó **bắt buộc** làm 3 việc kiểm chứng:

**(a) Thống kê phát hiện.** In: số range phát hiện được trong 5–7/2026 (và cả 9 tháng dxFeed nếu chạy được),
phân bố **độ rộng** (theo "giá"), phân bố **thời lượng** (số nến), phân bố **số lần chạm mỗi biên**.
→ Nếu số range < 30 thì **không đủ n** để kết luận về KB3; phải nói ra và mở rộng cửa sổ dữ liệu thay vì
nới lỏng định nghĩa cho ra nhiều range hơn.

**(b) Kiểm chứng BẰNG MẮT.** Vẽ **8–10 range** ngẫu nhiên (không chọn cái đẹp) ra PNG: nến M1, 2 đường biên,
các điểm chạm, mốc range vỡ. Dùng Pillow, lưu vào `quantower-entry-signal/research/wyckoff/img/range_NN.png`,
và **đặt link Markdown trong báo cáo** để người học click xem.
→ Nếu ảnh cho thấy "range" thực chất là đoạn xu hướng nghiêng hoặc nhiễu → sửa bộ phát hiện, đừng đi tiếp.

**(c) Tỷ lệ xoay biên NỀN (baseline rotation rate).** Trước khi thêm bất kỳ xác nhận nào, đo: khi giá chạm
một biên trong range hợp lệ, **bao nhiêu % lần** nó đi tới biên đối diện trước khi phá biên vừa chạm?
→ Đây là **edge nền** của KB3. Nếu tỷ lệ này không hơn rõ rệt so với mức "coin flip theo khoảng cách"
(tức xấp xỉ tỷ lệ mà một bước đi ngẫu nhiên cũng đạt được), thì KB3 **không có edge cấu trúc**, và mọi WR đẹp
sau đó chỉ đến từ bộ lọc — phải nói thẳng điều đó trong báo cáo.

## Bước 2 — Mô hình lệnh (R BIẾN THIÊN — khác hẳn KB1/KB2)

- `R = |entry − SL|`, SL đặt ngoài biên vừa chạm theo `SPEC`.
- `TP` = **biên đối diện trừ buffer**, không phải bội số R cố định → `RR` mỗi lệnh mỗi khác.
- **Bỏ qua lệnh nếu `RR_khả_dụng < ngưỡng tối thiểu`** trong `SPEC` (range quá hẹp so với SL thì không đáng đánh).
- `engine.py` của GĐ6 phải hỗ trợ TP theo mức giá; nếu chưa thì bổ sung (đừng hack riêng cho KB3).
- In thêm **phân bố RR thực tế** của tập lệnh KB3 — vì WR của KB3 sẽ cao hơn KB1 nhưng R nhỏ hơn, so WR trực
  tiếp giữa 2 kịch bản là **sai**; chỉ EV/lệnh và tổng R mới so được.

## Bước 3 — Xác nhận vào lệnh
Thêm **từng cái một** theo `SPEC §3` + `§6`: phản ứng nến tại biên (râu, `cpos`, thân), delta nến ngược hướng
phá, VSA, hợp lưu biên với VAH/VAL/POC/IB. Mỗi cái: bảng theo định dạng cố định + **partition (cả hai phía)** +
sweep + phán quyết PASS/KILL theo ngưỡng `SPEC`.

## Bước 4 — Gate xu hướng
KB3 **nghịch đà theo bản chất** → gate "thuận xu hướng" của v6 sẽ giết sạch. Test 3 dòng:
`không gate` / `chỉ chạy khi proxy xu hướng = 0 (đi ngang)` / `gate thuận đà như v6`.
Kết luận phải dựa vào số, không vào lý lẽ.

## Bước 5 — Định tuyến & portfolio (phần dễ sai nhất)

- Trạng thái range: `đang hình thành → hợp lệ → đang vỡ → đã vỡ`. KB3 chỉ chạy ở `hợp lệ`; khi `đã vỡ` thì
  **KB1 vào việc** (đúng ý người học).
- **Quy tắc 1 vị thế tại một thời điểm** cho toàn portfolio: khi đang có lệnh, tín hiệu mới bị bỏ.
  Phải kiểm bằng một test: không có 2 lệnh nào chồng thời gian.
- In **3 dòng portfolio**: chỉ KB1+KB2 (bằng GĐ6) / thêm KB3 / chỉ KB3. Con số quyết định là dòng **KB1+KB2+KB3**.
- Cẩn thận **đếm trùng**: một cú phá range có thể vừa là "KB3 thất bại" vừa là "KB1 kích hoạt" — đặc tả xử lý
  thế nào thì làm đúng thế, và in số lần xảy ra tình huống này.

## `RESULTS_KB3.md` phải có

1. `GOLDEN OK`
2. Thống kê phát hiện range (số lượng, phân bố độ rộng/thời lượng/số lần chạm)
3. **Link ảnh 8–10 range kiểm chứng bằng mắt** + nhận xét trung thực về chất lượng bộ phát hiện
4. **Tỷ lệ xoay biên nền** + so với mức ngẫu nhiên + kết luận "có edge cấu trúc hay không"
5. Phân bố RR thực tế của KB3
6. Bảng tiến hoá theo bước (mỗi xác nhận một dòng) + partition + sweep + PASS/KILL
7. Kết quả gate xu hướng (3 dòng)
8. **3 dòng portfolio** + kiểm không chồng lệnh + số ca trùng KB3/KB1
9. Cấu hình chốt KB3 (dict copy-paste được), hoặc kết luận **KILL** kèm số liệu
10. Giới hạn + mục "cần quyết"

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file/ảnh nhắc đến phải có **link Markdown**.
2. **TUYỆT ĐỐI không bịa số.** Mọi con số là output thật, dán kèm.
3. `n < 25` → **"không kết luận"**.
4. Mọi hàm feature chỉ đọc `B[:i+1]`. Cấm thống kê toàn chuỗi. Gate áp ở **nến vào lệnh**.
5. Repo **PUBLIC**: không hardcode token. Ảnh kiểm chứng nhẹ (<200KB/ảnh) thì commit được.
6. Không publish lên Claude Artifacts.
7. Xong → **commit + push `origin main`**.
8. **Được phép kết luận KILL.** Nếu KB3 không có edge, nói thẳng — đó là kết quả có giá trị, đừng cố tinh chỉnh
   cho ra số dương.

## Quy tắc DỪNG (chuyển lên Opus xhigh)

1. GOLDEN TEST không khớp.
2. Ảnh kiểm chứng cho thấy bộ phát hiện range sai bản chất mà sửa 2 lần vẫn chưa đúng.
3. Tỷ lệ xoay biên nền không hơn mức ngẫu nhiên (cần quyết có bỏ KB3 hay đổi cách tiếp cận).
4. WR nhảy **>10 điểm** hoặc `n` tụt **>40%** sau một thay đổi.
5. Phải đổi **định nghĩa range** so với `SPEC`.

## Xong khi nào

- [ ] `GOLDEN OK`
- [ ] Bộ phát hiện range có thống kê + **ảnh kiểm chứng bằng mắt** + nhận xét chất lượng
- [ ] Đã đo **tỷ lệ xoay biên nền** và kết luận có/không edge cấu trúc
- [ ] Mô hình R biến thiên chạy đúng, có phân bố RR thực tế
- [ ] Các xác nhận đã test từng cái, đủ partition + sweep + PASS/KILL
- [ ] Có kết quả gate xu hướng 3 dòng
- [ ] Có 3 dòng portfolio + kiểm không chồng lệnh
- [ ] `RESULTS_KB3.md` đủ 10 mục
- [ ] Đã commit + push

Cuối lượt báo: KB3 **có edge hay không** (kèm tỷ lệ xoay biên nền), số portfolio 3 dòng, cấu hình chốt hoặc lý do KILL, và link ảnh kiểm chứng range.
