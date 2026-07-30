# HVN tuần/ngày — cách trader chuyên nghiệp canh vùng

Ghi ngày 2026-07-31. Nguồn: ảnh chat của người dùng với một trader chuyên nghiệp
(bạn của người dùng), đối chiếu với ebook Order Flow.

---

## 1. Trader pro nói gì

Nguyên văn từ ảnh chat:

| Người dùng hỏi | Trader pro trả lời |
|---|---|
| "Sau mỗi phiên Á, Âu chú có quan tâm giá đóng mở không? VAH VAL POC của từng phiên?" | **"K quan tâm lắm."** |
| "Ở thế thường chú nhìn gì để canh giá phản ứng? Vùng nào?" | **"Nhìn TPO tuần ngày. Với VWAP."** |
| "TPO là VA với POC à?" | **"HVN chú."** |
| "TPO m30 là chỉ ngày trước chú đánh dài à?" | **"TPO m30 là scalp."** |

Bối cảnh: người này vừa vào một lệnh mua rất đẹp, vùng canh mua là **HVN weekly**.

Tóm lại ba ý:
1. **Không** dùng VAH/VAL/POC/giá đóng-mở của từng phiên Á/Âu.
2. Canh giá ở **HVN của TPO tuần và ngày**, cộng **VWAP**.
3. TPO M30 dùng cho **scalp**; tuần/ngày dùng cho khung lớn.

---

## 2. Sách nói gì (ebook Order Flow)

Sách xác nhận đúng cơ chế đó, không mâu thuẫn:

> "Có thể vị trí **quan trọng nhất** trong bất kỳ footprint nào là Nút khối lượng cao (HVN).
> Nó đại diện nơi có khối lượng giao dịch lớn nhất, nơi mà **các tổ chức tích cực nhất**."
> — §HVN, trang 25

> "Một mức **cực kỳ mạnh** được hình thành khi hai hoặc nhiều HVN gặp nhau cùng một mức giá
> theo các nến liên tiếp… chúng thường đại diện cho các vùng **Hỗ trợ và Kháng cự mạnh**."
> — §Nhiều nút, trang 34

Setup giao dịch số 2 "Nhiều nút" (trang 54-55) còn ghi rõ:
- **"Khung thời gian ưa thích của tôi là biểu đồ 30 phút."** ← trùng khung M30SessionZones
- Cần ≥2 nến nguyên vẹn hình thành SAU khi Nhiều nút xuất hiện
- Chờ pullback về Nhiều nút, **chỉ giao dịch ở lần chạm đầu tiên**
- Chạm từ trên → mua; chạm từ dưới → bán

---

## 3. Vấn đề: indicator đang làm NGƯỢC LẠI

`M30SessionZones` trước bản sửa này sinh 6 loại vùng:

| Loại | Điểm | Trader pro có dùng? |
|---|---:|---|
| cụm POC | 78 | gián tiếp (POC ≠ HVN) |
| naked POC | 72 | không nhắc |
| **biên VA phiên (VAH/VAL)** | 60 | ❌ **"K quan tâm lắm"** |
| **đỉnh/đáy phiên** | 45 | ❌ không nhắc |
| băng giá trị | 55 | gián tiếp |
| **HVN** | — | ✅ **cái họ dùng chính — KHÔNG HỀ CÓ** |

Nói cách khác: nhóm vùng chiếm **nhiều khe nhất** (biên VA + đỉnh/đáy của 2 phiên gần
nhất = 8 vùng) lại đúng là thứ trader pro nói không quan tâm; còn thứ họ dùng để canh
lệnh thì indicator không tính.

**Comment đầu `ProfileEngine.cs` ghi là có HVN nhưng KHÔNG có dòng code nào tính HVN** —
comment nói dối, đã sửa.

---

## 4. Đã sửa gì

**`ProfileEngine.FindHvn()`** — hàm mới. HVN khác POC: POC chỉ có **một** (đỉnh cao nhất
của phân bố), HVN có thể có **nhiều** — mỗi nơi khối lượng tụ thành nút.

Cách tìm: làm mượt phân bố (cửa sổ ±5 tick) → lấy đỉnh cực bộ → giữ đỉnh có trọng số
≥1.5× trung bình → gộp đỉnh quá gần nhau.

**`ProfileEngine.RowsOver()`** — hàm mới, gộp hàng giá trên nhiều phiên để dựng profile
tuần/ngày (trước đây chỉ dựng được profile từng phiên).

**`M30SessionZones`** — thêm 2 loại vùng, đặt điểm **cao hơn** biên VA phiên:

| Loại mới | Công thức điểm | Trần | Nét vẽ |
|---|---|---:|---|
| `hvn_week` | `70 + tỉ_lệ × 6` | 95 | cam, dày 2.4 |
| `hvn_day` | `64 + tỉ_lệ × 6` | 88 | cam, dày 1.8 |

`tỉ_lệ` = trọng số nút / trọng số trung bình → nút càng nổi so với nền, điểm càng cao.
Tham số mới: `ShowHvn` (mặc định bật), `MaxHvn` (mặc định 3), `HvnColor`.

Sách dùng màu **vàng** cho Nhiều nút, nhưng vàng đã dành cho naked POC → HVN dùng **cam**.

**Một lỗi đã bắt được khi kiểm trên dữ liệu thật:** khoảng cách tối thiểu giữa 2 HVN cố
định 20 tick khiến profile tuần (range ~1300–2400 tick) tách **một** nút thành **ba** HVN
sát nhau (4085.3 / 4089.7 / 4095.0) — phí cả 3 khe. Đã sửa thành co giãn **8 % độ rộng
profile**, kẹp trong [20, 120] tick. Sau khi sửa, tuần 27/7 cho 4089.7 / 4102.5 / 4135.0 —
các vùng thực sự khác nhau.

---

## 5. ⚠ Cái CHƯA chứng minh được

Tôi đã thử đo bằng số xem HVN tuần có phản ứng tốt hơn biên VA không
(`hvn_research2.py`, dữ liệu 26 ngày). **Kết quả không kết luận được:**

| Vùng | n | thuận | nghịch | chênh | chặn được |
|---|---:|---:|---:|---:|---:|
| HVN tuần #1 | 6 | 2.16 | 1.39 | +0.77 | 50 % |
| HVN tuần #2 | 6 | 1.85 | 1.15 | +0.70 | 50 % |
| HVN tuần #3 | 4 | 2.81 | 1.02 | +1.79 | 50 % |
| POC tuần | 6 | 1.16 | 1.28 | −0.12 | 50 % |
| VAH tuần | 6 | 2.13 | 1.77 | +0.36 | 67 % |
| VAL tuần | 5 | 2.55 | 2.79 | −0.24 | 60 % |
| **~ngẫu nhiên (đối chứng)** | 24 | 2.39 | 1.94 | **+0.45** | **62 %** |

n = 4–6 mỗi vùng, và **mức ngẫu nhiên ngang ngửa hoặc hơn phần lớn vùng thật**. Đây là
nhiễu, không phải bằng chứng. 26 ngày / 4 cặp tuần là quá ít.

*(Lần đo đầu tiên `hvn_research.py` cho 100 % ở mọi ô — đó là phép đo hỏng: đo "giá bật
bao xa trong 8 nến M30" chính là đo biến động thị trường, không đo sức chặn của vùng.
Giữ lại file để đối chiếu.)*

**Vậy căn cứ để sửa là gì?** Không phải bảng số trên. Là ba điều khác:
1. Một trader chuyên nghiệp đang giao dịch thật nói rõ họ dùng HVN, không dùng biên VA phiên.
2. Sách gọi HVN là "vị trí quan trọng nhất" và dành hẳn một setup cho nó, đúng khung M30.
3. Indicator **thiếu hẳn** một loại vùng mà chính comment của nó tuyên bố là có.

Thêm một loại vùng còn thiếu ≠ tinh chỉnh tham số cho khớp dữ liệu. Không có cấu hình
đóng băng nào bị đụng tới.

---

## 6. Việc còn lại

- **Chưa chạy Quantower thật** — mới build sạch trên Linux (0 lỗi, 0 cảnh báo) và kiểm
  logic bằng Python trên dữ liệu thật. Cần deploy Windows xem vùng vẽ ra có hợp lý không.
- Điểm `70 + tỉ_lệ×6` và `64 + tỉ_lệ×6` là **đặt tay**, chưa backtest — giống hệt tình
  trạng của 78/72/60/55/45 cũ.
- Cần ≥3 tháng dữ liệu M30 mới đo được HVN có thật sự hơn biên VA hay không.
- **Chưa làm:** trader pro còn nhắc **VWAP** như thành phần ngang hàng với TPO tuần/ngày.
  `M30SessionZones` hiện không có VWAP (chỉ `WyckoffRunner` có). Đáng cân nhắc thêm.
- Câu **"TPO m30 là scalp"** gợi ý phân tầng: tuần/ngày → bias và vùng canh; M30 → vào lệnh.
  Trùng với kiến trúc 2 tầng đã ghi trong memory, nhưng chưa phản ánh vào panel.
