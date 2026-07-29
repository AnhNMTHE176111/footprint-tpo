# 00 — ĐỌC TRƯỚC KHI REVIEW

Bộ file để bạn chấm tay từng lệnh. Sinh lại bằng: `python3 need-review/build_review.py`

---

## ⚠ Trước hết: 3 file indicator nhưng chỉ có 2 bộ dữ liệu

Bạn yêu cầu "cả 3 kịch bản của 3 file". Thực tế trong repo:

| File indicator | Có export CSV? | Trong bộ review |
|---|---|---|
| `WyckoffRunner.cs` (v7) | ✅ có | file 1, 2, 3, 4 |
| `RunnerSignal.cs` (v5) | ✅ có | file 4, 5 |
| `EntrySignal.cs` (scalp 1.5R) | ❌ **KHÔNG CÓ** | — |

**`EntrySignal` chưa bao giờ xuất CSV** — nó không có hàm `ExportSignals()`. Tôi không dựng file review cho
nó vì sẽ phải bịa số. Muốn review nó thì phải thêm code xuất CSV vào `EntrySignal.cs` rồi chạy lại trên
Windows — nói nếu bạn muốn tôi làm.

Còn "3 kịch bản": KB3 (biên↔biên) **không có dòng code nào** trong bất kỳ DLL nào (đã KILL), nên n=0, không
có gì để review. Thực chất có **2 kịch bản** có dữ liệu: **CBR** và **QUAY ĐẦU**.

---

## 5 file, xếp theo thứ tự nên làm

| # | File | n | Thống kê | Vì sao review |
|---|---|---:|---|---|
| **1** | `1-v7-CBR-DA-VAO-ma-THUA.csv` | **18** | WR 0% · −18.0R | ⭐ **LÀM CÁI NÀY TRƯỚC.** Tiền thật sẽ mất |
| 2 | `2-v7-CBR-BO-SOT-(v5-co-v7-khong).csv` | 89 | WR 22.5% · −9.0R · EV −0.101 | Lệnh v7 bỏ qua — **có bẫy, đọc §Bẫy** |
| 3 | `3-v7-CBR-toan-bo.csv` | 34 | WR 47.1% · +46.0R · EV +1.353 | Xem tổng thể, so WIN vs LOSS |
| 4 | `4-QUAY_DAU-(v5-va-v7-GIONG-HET).csv` | 28 | WR 57.1% · +12.0R · EV +0.429 | Kịch bản đang TẮT — hiểu vì sao yếu |
| 5 | `5-v5-CBR-toan-bo.csv` | 112 | WR 28.6% · +16.0R · EV +0.143 | Bản cũ, để đối chiếu |

Cột trống để bạn điền: **`CHAM_1_5`** (chấm 1–5 điểm setup) · **`LOI_GI`** · **`CO_CHE_NGHI_NGO`** · **`GHI_CHU`**

Cột có sẵn để đọc nhanh: `gio_VN` (giờ VN = UTC+7) · `giu_bao_lau` · `gia_pha` · `retrace_%` · `leg_gia` ·
`VSA` · `climax` · `hop_luu` · `grade` · `tp_vuong_vung`.

---

## 🔴 Bẫy của file 2 — đọc kỹ trước khi mở

File 2 là 89 lệnh mà v5 bắt nhưng v7 không bắt. Cả nhóm: **WR 22.5%, EV −0.101R** → **v7 loại là đúng.**

Nhưng trong 89 lệnh đó **có 20 lệnh WIN**. Rất dễ chỉ vào chúng và nói "đáng lẽ v7 phải bắt, +80R!". **Đó là
con số ảo** — bạn chọn được chúng vì đã biết kết quả.

Bằng chứng bằng số:

| Cách | Kết quả |
|---|---|
| v7 hiện tại (loại hết 89) | EV **+1.353R** |
| Nhận **cả** 89 lệnh vào (RR 4.0) | EV **+0.124R** ← tệ hơn 10 lần |
| Chỉ nhận 20 lệnh WIN | +80R ← **không thể làm được thật** |

**Quy tắc:** chỉ ghi nhận một lệnh ở file 2 nếu bạn nêu được **dấu hiệu nhìn thấy TRƯỚC khi vào lệnh** —
và dấu hiệu đó, khi áp lên cả 89 lệnh, phải lọc ra nhóm tốt hơn EV +0.124R. Nếu lý do là "nhìn chart thì
thấy nó sẽ chạy" thì đó không phải quy tắc.

---

## Quy tắc vàng: tìm CƠ CHẾ, không tìm lệnh

| ✅ Nên viết vào `CO_CHE_NGHI_NGO` | ❌ Không nên |
|---|---|
| "Cả 5 cú thua này vào trong 15' sau giờ tin Mỹ" | "Lệnh này đáng lẽ thắng" |
| "Thua khi `leg_gia` > 8 giá — phá quá xa, hết đà" | "Chart nhìn xấu" |
| "Thua khi `giu_bao_lau` < 3 phút — vào lúc còn nhiễu" | "Nên vào muộn hơn 2 nến" |
| "T6 nhóm bị loại −15.0R, T7 +4.0R → v7 chặt quá lúc thị trường êm" | "Thêm điều kiện cho khớp 20 lệnh WIN" |

Cơ chế tốt là cơ chế **kiểm được trên dữ liệu khác**. Nếu quy tắc chỉ đúng trên đúng 3 tháng này thì nó là
nhiễu, không phải edge.

---

## ⚠ Giới hạn cứng: KHÔNG sửa cấu hình đóng băng từ review này

Cấu hình v7 hiện tại là **kẻ sống sót của ≥94 cấu hình** thử trên **đúng cửa sổ 5–7/2026 này**. Sau hiệu
chỉnh Bonferroni, KB1 chỉ *vừa* sống (p 0.0003 → **0.028**, ngưỡng 0.05).

Nghĩa là: **thêm vài lần thử nữa lên cùng dữ liệu này là nó chết** — và ta sẽ không nhìn thấy, vì bảng số
vẫn đẹp. Đó là lý do mọi thứ rút ra từ review này chỉ được xếp vào **GIẢ THUYẾT**.

Đường đi hợp lệ:

```
review  →  ghi giả thuyết vào need-review/GIA-THUYET.md  →  đợi dữ liệu tháng 8 (forward)
        →  kiểm giả thuyết trên tháng 8  →  qua thì mới sửa cấu hình
```

Đường đi **không** hợp lệ: review → thêm gate cho khớp → bảng số đẹp hơn → tưởng đã cải thiện.

Chi tiết: [AUDIT_V7.md](../quantower-entry-signal/research/wyckoff/AUDIT_V7.md) §D ·
[BASELINE.md](../quantower-entry-signal/research/wyckoff/BASELINE.md) §0

---

## Ngữ cảnh: v7 hơn v5 ở đâu (đã đo, cùng cửa sổ, cùng kịch bản CBR)

| | v5 RunnerSignal | v7 WyckoffRunner |
|---|---:|---:|
| n | 112 | 34 |
| WR | 28.6% | **47.1%** |
| Tổng R | +16.0R | **+46.0R** |
| EV/lệnh | +0.143R | **+1.353R** |
| MDD | 20.0R | **3.0R** |
| RR mục tiêu | 3.0 | 4.0 |

Khác biệt lớn nhất là **BREAK SẠCH** (bỏ cú phá ngay sau khi vừa quét hụt cạnh đối diện). Nhóm 89 lệnh bị
loại ở tháng 6 (tháng vàng crash) là **−15.0R** — bộ lọc cứu đúng tháng xấu.

⚠ Cả hai cột đều là **in-sample**. Điểm ngoài mẫu của v7 hiện chỉ có **n=2** → chưa kết luận được gì.
