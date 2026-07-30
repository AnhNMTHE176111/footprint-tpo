# PLAN v2 — M30SessionZones chỉ hiện VÙNG QUAN TRỌNG

Viết 2026-07-31. Mục tiêu người dùng đặt ra: **"show ra cùng vùng quan trọng thôi"**.

Ba nguồn căn cứ: (1) lời trader pro trong ảnh chat, (2) ebook Order Flow,
(3) tài liệu công khai trên internet + số đo trên dữ liệu thật 26 ngày.

---

## A. Vấn đề đo được

Chạy thử trên dữ liệu thật (giá 4167.4, ngày 30/7):

| | Con số |
|---|---|
| Số vùng indicator sẽ vẽ | **~17** |
| Mật độ khuyến nghị (tài liệu) | **3–5** |
| Vùng **mạnh nhất** (HVN tuần #1, điểm 85) cách giá | **777 tick = 78 giá** |

Vùng mạnh nhất nằm ngoài tầm giao dịch trong ngày, nhưng vẫn được vẽ đậm nhất và
xếp đầu bảng. Đây là lỗi thiết kế: **điểm số hiện chỉ đo "vùng này về lý thuyết mạnh
cỡ nào", không đo "vùng này có dùng được HÔM NAY không"**.

Tài liệu nói thẳng: đánh dấu mọi VAH/VAL/POC các ngày trước làm chart thành *"cây thông
Noel"*, và *"3 đến 5 mức tham chiếu là mật độ đúng cho chart trong ngày"*.

---

## B. Đúc kết từ internet (khớp/bổ sung gì cho trader pro)

**Khớp hoàn toàn với lời trader pro:**

- HVN là vùng S/R mạnh nhất vì đó là nơi **có sự đồng thuận về giá trị hợp lý**; nhiều
  vị thế được mở ở đó nên người ta sẽ bảo vệ nó. Giá quay về HVN thì phản ứng/bật là
  "rất có khả năng".
- **POC khung lớn mạnh hơn khung nhỏ** — nên xem POC ở ngày/tuần/tháng.
- *"Một mức Volume Profile ngày là vô nghĩa nếu nó mâu thuẫn với cấu trúc tuần/tháng.
  Luôn kiểm khung lớn hơn để đối chiếu."*
- Khớp holding period với profile period: swing → tuần/tháng, intraday → phiên trước +
  phiên đang chạy. (Chính là ý "TPO m30 là scalp".)

**Bổ sung 3 thứ trader pro không nhắc, tài liệu nhấn mạnh:**

1. **LVN (Low Volume Node)** — ngược với HVN: nơi giá **xuyên qua rất nhanh**, không có
   gì đỡ. Dùng để (a) đặt SL phía sau, (b) biết chỗ nào KHÔNG nên kỳ vọng phản ứng,
   (c) LVN phân tách hai vùng phân phối. Indicator hiện **không có LVN**.
2. **Hợp lưu đa khung là tiêu chí xếp hạng số 1.** *"Mức đáng tin cậy nhất là nơi nhiều
   profile — neo ở các mốc khác nhau — cho ra mức chồng nhau."* Càng nhiều khung đồng ý,
   vùng càng mạnh.
3. **Naked POC bị xếp thấp hơn HVN.** Tài liệu OrderFlow Labs coi HVN/LVN là trọng tâm
   chính, POC chỉ là "điểm neo tham chiếu", không phải trigger vào lệnh.

**Đã kiểm hợp lưu đa khung trên dữ liệu thật:**

| Kiểm | Kết quả |
|---|---|
| HVN tuần có HVN ngày xác nhận (±1 giá) | **13/15 = 87 %** |

87 % là con số hai mặt: hợp lưu đa khung **có thật**, nhưng cũng nghĩa là nếu vẽ cả HVN
tuần lẫn HVN ngày thì **87 % là đường trùng nhau** → chart nhân đôi vô ích. Phải **gộp**
thành một vùng mạnh hơn, không vẽ song song.

---

## C. Nguyên tắc thiết kế v2

> **Điểm của vùng = độ mạnh cấu trúc × mức liên quan tới giá hiện tại.**
> Vùng xa giá không phải "vùng yếu", mà là **vùng chưa tới lượt** — không vẽ.

Bốn quy tắc:

1. **Lọc theo tầm với trước, xếp hạng sau.** Chỉ giữ vùng trong bán kính giao dịch được
   (theo ATR, không phải số tick cứng — vàng biến động khác nhau theo giai đoạn).
2. **Gộp hợp lưu đa khung thành MỘT vùng.** Tuần + ngày + phiên trùng nhau → một vùng
   điểm cao, nhãn ghi rõ "×3 khung", không phải 3 đường.
3. **Trần cứng số vùng hiển thị** (mặc định 5). Vượt thì cắt theo điểm.
4. **Cân đối trên/dưới giá.** Chỉ hiện toàn vùng trên hoặc toàn dưới là mù một phía —
   giữ tối thiểu mỗi phía 2 vùng (nếu có).

---

## D. Việc cụ thể

### D1 — Lọc theo tầm với (ưu tiên cao nhất)

Thêm `ZoneRangeAtr` (mặc định **3.0**): chỉ giữ vùng cách giá ≤ `3 × ATR20(M30)`.

Với dữ liệu 30/7 (ATR20 ≈ 16.7 giá) → bán kính ≈ 50 giá = 500 tick. HVN tuần #1 (777 t)
bị loại đúng như mong muốn; HVN ngày #1 (290 t) và #3 (204 t) được giữ.

Dùng ATR chứ không phải hằng số vì tháng 6 vàng crash biến động gấp nhiều lần tháng 7 —
bán kính cứng sẽ hoặc quá chật hoặc quá rộng tuỳ giai đoạn.

### D2 — Gộp hợp lưu đa khung, ghi rõ số khung

Hiện `MergeZones()` gộp trong 7 tick và cộng `max + 0.5×min`. Sửa:

- Dung sai gộp theo **ATR** (đề xuất `0.15 × ATR`, kẹp [7, 30] tick) thay vì 7 tick cứng.
  Lý do: 7 tick với range tuần 1300–2400 tick là quá chặt, HVN tuần và HVN ngày cách nhau
  0.3–0.8 giá (như 4090.0 vs 4089.7) sẽ không gộp dù rõ ràng là **một** vùng.
- Thêm trường `Frames` (số khung đồng ý) vào `Zone`. Nhãn: `"HVN ×3 khung (tuần+ngày+phiên)"`.
- Cộng điểm theo số khung: `+8` mỗi khung thêm, vì hợp lưu đa khung là tiêu chí xếp hạng
  số 1 theo tài liệu.

### D3 — Thêm LVN

`ProfileEngine.FindLvn()` — nghịch đảo `FindHvn()`: tìm **đáy** cực bộ của phân bố, giữ
điểm có trọng số ≤ `0.5 ×` trung bình.

Vẽ **khác hẳn HVN**: nét đứt mảnh, màu xám nhạt, nhãn "LVN (xuyên nhanh)". LVN **không
phải vùng canh vào lệnh** — nó là vùng *tránh* kỳ vọng phản ứng và là chỗ đặt SL. Phải
nhìn là phân biệt được ngay, không lẫn với HVN.

Không tính LVN vào trần 5 vùng của D1 (nó là thông tin khác loại), nhưng giới hạn riêng 2.

### D4 — Hạ cấp nhóm vùng trader pro không dùng

Hiện có 8 vùng từ biên VA + đỉnh/đáy của 2 phiên gần nhất — đúng thứ trader pro nói
"k quan tâm lắm", và chiếm nhiều khe nhất.

- Giảm từ **2 phiên → 1 phiên gần nhất** (giảm 8 → 4 vùng).
- Hạ điểm: `va_edge` 60 → **50**, `priorhl` 45 → **38**.
- **Không xoá hẳn**: chúng vẫn có giá trị làm mốc hợp lưu (D2) — khi trùng HVN thì nâng
  điểm HVN lên, dù bản thân chúng không được vẽ riêng.

### D5 — Trần số vùng + cân đối hai phía

`MaxZones` (mặc định **5**, đúng khuyến nghị "3–5"). Sau khi lọc D1 và gộp D2:

1. Xếp theo điểm giảm dần.
2. Đảm bảo tối thiểu 2 vùng mỗi phía (trên/dưới giá) nếu có đủ.
3. Cắt còn `MaxZones`.

### D6 — Panel phản ánh phân tầng

Trader pro: **"TPO m30 là scalp"** — tuần/ngày quyết định vùng, M30 để vào lệnh.
Panel hiện trộn lẫn. Đổi thành 2 nhóm rõ ràng:

```
VÙNG CANH (tuần/ngày):     ← chỗ chờ giá tới
  ⬥ 4138.4  HVN ×2 khung [87]  cách 29 giá
  ⬥ 4147.0  HVN ngày [73]      cách 20 giá
BỐI CẢNH PHIÊN (scalp):    ← chỉ để biết, không canh lệnh
  · VAH Âu 4142.0 · naked POC 4073.6
```

### D7 — VWAP (để sau, cần quyết định)

Trader pro xếp VWAP **ngang hàng** với TPO tuần/ngày. `M30SessionZones` không có VWAP;
`WyckoffRunner` đã có. Hai lựa chọn:

- (a) Thêm VWAP vào M30SessionZones → hai indicator vẽ trùng VWAP trên cùng chart.
- (b) Chỉ dùng VWAP làm **mốc hợp lưu** (cộng điểm cho vùng gần VWAP), không vẽ đường.

**Đề xuất (b)** — được lợi ích hợp lưu mà không vẽ trùng. Cần người dùng chốt.

---

## E. Thứ tự làm

| # | Việc | Vì sao trước/sau |
|---|---|---|
| 1 | **D1** lọc tầm với | Sửa được đúng vấn đề lớn nhất (vùng mạnh nhất cách 78 giá), ít rủi ro |
| 2 | **D5** trần 5 vùng | Đi kèm D1, cho ra ngay "chỉ vùng quan trọng" |
| 3 | **D2** gộp đa khung | Cần D1 xong mới thấy rõ vùng nào còn lại để gộp |
| 4 | **D4** hạ cấp vùng phiên | Nhỏ, an toàn |
| 5 | **D6** panel phân tầng | Sau khi tập vùng đã ổn định |
| 6 | **D3** LVN | Tính năng mới, làm sau khi phần lọc đã chạy đúng |
| 7 | **D7** VWAP | Chờ người dùng chốt (a) hay (b) |

---

## F. ⚠ Giới hạn phải nói rõ

- **Mọi điểm số vẫn là đặt tay, chưa backtest.** Kể cả `+8`/khung ở D2 và bán kính
  `3×ATR` ở D1. Chúng đến từ tài liệu và lý lẽ, không phải từ tối ưu trên dữ liệu.
- Khảo sát 26 ngày **không chứng minh được** HVN hơn biên VA (n = 4–6, ngang mức ngẫu
  nhiên — xem `HVN-VA-TRADER-PRO.md` §5). Con số 87 % hợp lưu là **đo được**, nhưng nó
  chỉ nói HVN các khung đồng ý với nhau, **không** nói HVN dự báo giá tốt.
- Đây là **indicator tầng BIAS**, không phải tín hiệu vào lệnh. Không có cấu hình đóng
  băng nào (v7 WyckoffRunner) bị đụng tới.
- Chưa chạy Quantower thật lần nào — mới build sạch trên Linux và kiểm logic bằng Python.

---

## Nguồn

- [OrderFlow Labs — Volume Profile: HVNs, LVNs, and Value](https://orderflowlabs.com/blogs/theblog/volume-profile-guide)
- [Trade With The Pros — Pre Market Level Marking](https://tradewiththepros.com/pre-market-level-marking/) (mật độ 3–5 mức, "cây thông Noel")
- [Equiti — Volume profile trading: high-volume and low-volume zones](https://www.equiti.com/sc-en/news/trading-ideas/volume-profile-trading-how-to-read-high-volume-and-low-volume-zones/)
- [TrendSpider — Volume Profile Trading Strategies](https://trendspider.com/learning-center/volume-profile-strategies/) (hợp lưu đa khung)
- [Quantum Algo — Volume Profile Trading Strategy](https://www.quantum-algo.com/blog/volume-profile-trading-strategy-guide/) (phân cấp khung thời gian)
- [TradingSim — Volume Profile Day Trading Strategies](https://www.tradingsim.com/blog/advanced-day-trading-strategies-using-volume-profile)
- Ebook Order Flow §HVN (tr.25), §Nhiều nút (tr.34), §Setup 2 (tr.54-55)
- Ảnh chat trader pro 2026-07-31 → `HVN-VA-TRADER-PRO.md`
