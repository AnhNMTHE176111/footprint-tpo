# RESULTS — VSA của NẾN VÀO LỆNH (runner, nhánh CBR) + luật thuận màu cho nhánh QUAY ĐẦU

> Ngày 2026-08-02. Khởi nguồn: người học soi chart và tố cáo *"runner signal vào lệnh ở rất nhiều nến
> có VSA < high, rất nhiều lệnh SL vì các entry này"*.
> Script: [`cbr_entry_vsa.py`](cbr_entry_vsa.py) (nhánh CBR), [`../rev_bodydir_ab.py`](../rev_bodydir_ab.py) /
> `ab2` / `ab3` (nhánh QUAY ĐẦU).
> Dữ liệu: dxFeed `_GCQ26XCEC` M1, cửa sổ đo 05-07/2026 (giai đoạn GCQ26 thật sự có thanh khoản).

---

## 0. Kết luận thẳng

| Việc | Phán quyết | Mặc định |
|---|---|---|
| **Gate VSA ở nến VÀO LỆNH (CBR)** — `ResumeVsa=0.80` | **NHẬN** — qua đối chứng ngẫu nhiên p=0.037 | **BẬT** |
| **Sửa cột VSA báo sai nến (CBR)** | **NHẬN** — lỗi hiển thị thuần, không cần bằng chứng thống kê | **BẬT** |
| **Luật "nến vào phải thuận màu" (QUAY ĐẦU)** — `RevRequireBodyDir` | **CHƯA NHẬN** — hoán vị p=0.288 ở RR đang ship | **TẮT** |

---

## 1. Tố cáo đúng — và đúng ở HAI mặt cùng lúc

Đọc code trước khi đo (`RunnerSignal.cs` / `WyckoffRunner.cs`, nhánh CBR):

- **Nến PHÁ** (bar `i`): bắt buộc `b.Vratio >= BreakVsa` = **2.0×** → luôn là nến mạnh.
- **Nến VÀO LỆNH** (bar `j`, nến tiếp diễn): chỉ đòi `bj.Brat >= ResumeBody (0.35)` và `vol >= VolFloor`.
  **Không có một điều kiện VSA nào.**
- `AddSig(raw, j, ..., b.Vratio, ...)` — truyền VSA của **nến phá** cho tín hiệu nằm ở **nến vào** `j`.

Mặt thứ hai này giải thích vì sao mâu thuẫn tồn tại lâu mà không ai thấy: **log trông rất đẹp**. Cột `VSA`
trong CSV/panel/Telegram lấy từ nến phá nên toàn 2.2–5.6× và gắn cờ "tím", trong khi nến vào lệnh trên
chart thì nhỏ. Người học nhìn chart, hệ thống nhìn log — hai bên nói về hai cây nến khác nhau.

Số đo (n=55 lệnh CBR, cấu hình v5 đang ship):

| | Trung vị | p10 | p90 |
|---|---:|---:|---:|
| VSA **nến vào lệnh** (thứ người học thấy) | **1.04×** | 0.38× | 2.52× |
| VSA **nến phá** (thứ log báo ra) | 2.86× | 2.18× | 6.39× |

- Nến vào có VSA **< 1.2× (dưới "high")**: **31/55 = 56%**
- Nến vào có VSA < 2.2× (dưới climax): 47/55 = 85%

## 2. Nến vào yếu có thật sự làm hỏng lệnh không?

| VSA nến vào | n | WR | Tổng R | EV |
|---|---:|---:|---:|---:|
| [0.0, 0.8) | 20 | **35.0%** | +8.0R | +0.400 |
| [0.8, 1.0) | 7 | 57.1% | +9.0R | +1.286 |
| [1.0, 1.2) | 4 | 50.0% | +4.0R | +1.000 |
| [1.2, 1.5) | 8 | 25.0% | +0.0R | +0.000 |
| [1.5, 2.2) | 8 | 50.0% | +8.0R | +1.000 |
| [2.2, ∞) | 8 | 87.5% | +20.0R | +2.500 |

Đọc trung thực: **nhóm VSA < 0.8 đúng là nhóm tệ nhất** (WR 35% so với 47% toàn bộ) — tố cáo có cơ sở.
Nhưng quan hệ **không đơn điệu**: ô [1.2, 1.5) còn tệ hơn (EV 0.000), và ngay cả nhóm tệ nhất vẫn dương.
Với n mỗi ô chỉ 4–20, đừng đọc từng ô như sự thật; chỉ có hai đầu (rất yếu / climax) là đủ rõ.

## 3. Thiết kế gate: CHỜ nến khác, đừng huỷ leg

Hai cách xử lý nến hồi yếu:

- **ABANDON** — bỏ luôn cả leg (giống chỗ code đang `break`). Mất lệnh thật.
- **WAIT** — bỏ qua nến đó, vòng lặp chạy tiếp trong cửa sổ `WaitBars`, bắt nến hồi khoẻ hơn.

WAIT thắng rõ, và đây là lý do gate **không mất tổng R**:

| Ngưỡng (WAIT) | n | WR | Tổng R | EV |
|---|---:|---:|---:|---:|
| không gate (v5) | 55 | 47.3% | +49.0R | +0.891 |
| 0.50 | 49 | 51.0% | +51.0R | +1.041 |
| 0.70 | 45 | 51.1% | +47.0R | +1.044 |
| **0.80** | **42** | **54.8%** | **+50.0R** | **+1.190** |
| 0.90 | 39 | 53.8% | +45.0R | +1.154 |
| 1.20 ("high") | 30 | 50.0% | +30.0R | +1.000 |
| 2.20 (climax) | 11 | 72.7% | +21.0R | +1.909 |

Chọn **0.80**: nằm giữa cao nguyên 0.5–0.9 (không phải đỉnh nhọn — 0.75 và 0.80 cho kết quả y hệt),
cả 3 tháng dương.

**Vì sao KHÔNG đặt 1.2 = "high" như trực giác?** Vì 1.2 cắt quá tay: tổng R rơi từ +50 xuống +30 mà EV
còn thấp hơn 0.8 (+1.000 vs +1.190). Cái giết lệnh là nến hồi **chết** (VSA 0.4), không phải nến hồi
**bình thường**. Ai muốn ít lệnh chất hơn thì chỉnh input lên 1.2 hoặc 2.2 — tham số đã mở.

## 4. Hai đối chứng (phần quan trọng nhất)

**(a) Đối chứng ngẫu nhiên** — gate bỏ 13/55 lệnh. Nếu bỏ **ngẫu nhiên** đúng 13 lệnh, 2000 lần:

```
ngẫu nhiên: EV trung vị +0.905   p95 +1.095
gate 0.8  : EV        +1.190              -> p = 0.037
```

Gate **chọn** chứ không chỉ làm mỏng. Đây là phép kiểm mà luật thuận màu ở §6 **trượt**.

**(b) Đối chứng "cắt cùng lượng lệnh bằng tiêu chí khác"** — siết `ResumeBody` thay vì VSA:

| ResumeBody | n | WR | Tổng R | EV |
|---|---:|---:|---:|---:|
| 0.35 (gốc) | 55 | 47.3% | +49.0R | +0.891 |
| 0.55 | 45 | 40.0% | +27.0R | **+0.600** |
| 0.65 | 33 | 39.4% | +19.0R | **+0.576** |

Siết thân nến làm **tệ đi**. Thông tin nằm ở **khối lượng** của nến vào, không ở hình dạng nó.

## 5. Ổn định qua các cấu hình khác (không chỉ đúng ở một bộ số)

| Cấu hình | gốc | +ResumeVsa 0.8 |
|---|---|---|
| v5 RunnerSignal (RR3, CLEAN tắt) | n55 WR47.3% +49R EV+0.891 | n42 WR54.8% +50R **EV+1.190** |
| WyckoffRunner (RR4, CLEAN bật) | n29 WR48.3% +41R EV+1.414 | n21 WR57.1% +39R **EV+1.857** |
| RR4, CLEAN tắt | n55 WR38.2% +50R EV+0.909 | n42 WR45.2% +53R **EV+1.262** |
| RR3, CLEAN bật | n29 WR58.6% +39R EV+1.345 | n21 WR71.4% +39R **EV+1.857** |
| RR2 | n55 WR50.9% +29R EV+0.527 | n42 WR54.8% +27R +0.643 |
| RR5 | n55 WR30.9% +47R EV+0.855 | n42 WR31.0% +36R +0.857 (hoà) |

EV cải thiện ở **6/6** cấu hình (RR5 hoà). Tổng R giảm ở RR2 và RR5 — nói rõ để không bán quá lời.

## 6. Nhánh QUAY ĐẦU — luật "nến vào phải THUẬN màu" (port từ EntrySignal): **CHƯA NHẬN**

Nhánh CBR **đã có sẵn** luật này (`bj.C > bj.O` / `bj.C < bj.O` nằm trong điều kiện `resume`) — không phải
sửa gì. Nhánh QUAY ĐẦU thì không kiểm thân nến, nên nến TRẮNG vẫn bắn SHORT, nến ĐỎ vẫn bắn LONG — đúng
loại lỗi đã sửa ở EntrySignal.

Bằng chứng ỦNG HỘ:

- **MFE trung vị: nến thuận màu 3.78R vs nến ngược màu 1.13R** (đo trực tiếp, không qua lựa chọn TP).
  Thuận màu đi được ≥3R: 7/14; ngược màu: 2/13.
- EV thuận màu > ngược màu ở **mọi RR** thử (1.0 / 1.5 / 2.0 / 3.0).
- Nhóm ngược màu có EV **âm** ở mọi RR ≥ 2.0 — chúng là cú bật kỹ thuật ngắn, không phải đảo chiều thật.

Bằng chứng BÁC BỎ (nặng hơn):

- **Kiểm định hoán vị: p = 0.288 ở RR 1.5** (RevRR đang ship) — không có ý nghĩa. Chỉ p≈0.07 ở RR 2–3,
  vẫn không qua ngưỡng 0.05.
- Ở RR 1.5, bật luật này **làm giảm tổng R**: +10.5R → +8.5R (cắt mất 13/27 lệnh).
- Tách theo phía thì mỗi ô còn n=6–8, và **SHORT ngược màu lại dương** (+0.667R) — mâu thuẫn nội bộ ⇒ nhiễu.
- `AUDIT_V7.md` §13 đã phán **cả nhánh QUAY ĐẦU là FAIL** (EV +0.389 = đúng p95 của null vào-lệnh-ngẫu-nhiên;
  điểm OOS duy nhất: n=9, WR 33%, EV −0.167R). Không nên tinh chỉnh một nhánh chưa chứng minh được là có edge.

⇒ Ship dưới dạng input `RevRequireBodyDir`, **mặc định TẮT**. Cùng một thước đo đã cho `ResumeVsa` đi qua
(p=0.037) thì cũng phải cho luật này ở lại (p=0.288) — không nới tiêu chuẩn cho giả thuyết mình thích.

## 7. Giới hạn phải nhớ

- **Một cửa sổ 3 tháng, một hợp đồng, một regime.** Không có điểm OOS nào. p=0.037 là **chưa hiệu chỉnh**
  cho số cấu hình đã thử — nếu Bonferroni theo ~9 ngưỡng đã quét thì p → 0.33, tức **không còn ý nghĩa**.
  Cơ sở thật để bật mặc định là: (1) lỗi cơ chế có thật và đọc được trong code, (2) hướng cải thiện nhất
  quán ở 6/6 cấu hình, (3) hai đối chứng độc lập cùng ủng hộ — chứ không phải riêng con số p.
- dxFeed **không có delta** ⇒ mọi thứ ở đây dùng volume/VSA, chưa kiểm imbalance per-level.
- Đổi cột VSA sang nến vào làm **cờ "tím"/climax trong CSV và Telegram đổi nghĩa**. Các file review cũ
  (`WyckoffRunner-lenh-dinh-SL.md`, `RunnerSignal-lenh-SL-review.md`) ghi VSA nến **phá** — không so
  trực tiếp với log mới được.
