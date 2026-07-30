# Backtest v1 vs v2 — kết quả trung thực, 2026-07-31

Đã implement đủ D1-D6 của `PLAN-ZONES-V2.md`, build sạch (0 lỗi 0 cảnh báo), và
walk-forward backtest trên 26 ngày dữ liệu thật (`data-export/tpo-data/tpo-daily.csv`,
thực tế là bar M30). Script: `verify_zones_v2.py` (port logic C#→Python) +
`backtest_zones_v1v2.py` (đo sức chặn, walk-forward theo ngày).

---

## 1. Đã implement (D1-D6)

| # | Việc | Trạng thái |
|---|---|---|
| D1 | Lọc vùng theo tầm với `ZoneRangeAtr × ATR20` | ✅ |
| D2 | Gộp hợp lưu đa khung (dung sai theo ATR, +8 điểm/khung, nhãn `×N khung`) | ✅ |
| D3 | Thêm LVN (`FindLvn`, màu xám nhạt nét đứt, tách khỏi trần MaxZones) | ✅ |
| D4 | Hạ cấp `va_edge`/`priorhl`: 2 phiên→1 phiên, điểm 60/45→50/38 | ✅ |
| D5 | Trần `MaxZones=5`, cân đối tối thiểu 2 vùng/phía | ✅ |
| D6 | Panel phân tầng "VÙNG CANH" vs "Bối cảnh phiên" vs "LVN" | ✅ |
| D7 | VWAP | Chưa làm — chờ người dùng chốt (a)/(b) |

Build: `./build-tpo.sh m30` → 0 Warning, 0 Error.

Ví dụ thật (giá 4167.4, 30/7): v1 vẽ **9 vùng**, vùng mạnh nhất cách 100 giá.
v2 vẽ **5 vùng**, và cụm POC + HVN tuần + băng giá trị **tự gộp thành một vùng
điểm 100** ("cụm POC ×2 + HVN tuần ×1.6 + băng giá trị ×3 (×3 khung)") — đúng
cơ chế hợp lưu đa khung D2 được thiết kế để làm.

---

## 2. Backtest walk-forward — KẾT QUẢ KHÔNG NHƯ MONG ĐỢI

Cách đo (sửa lỗi của lần đo trước — xem §4): mỗi ngày trong 26 ngày, chỉ dùng dữ liệu
**quá khứ** tới hết ngày trước để tính vùng (không nhìn tương lai), rồi đo sức chặn
trong ngày đó. So với mức giá **ngẫu nhiên cùng ngày** làm đối chứng — quan trọng vì
loại được yếu tố "ngày biến động mạnh thì vùng nào cũng thắng".

| Bản | n (tổng lần chạm) | chênh thuận−nghịch | % thắng | Đối chứng ngẫu nhiên (cùng ngày) | Hơn ngẫu nhiên? |
|---|---:|---:|---:|---|---|
| **v1** | 117 | +0.14 | 58% | +0.13 (n=104) | **CÓ, nhưng cách biệt rất nhỏ** |
| **v2** | 102 | +0.01 | 57% | +0.11 (n=69) | **KHÔNG** |

**Nói thẳng: v2 không chứng minh được là tốt hơn ngẫu nhiên trên 26 ngày này.**
v1 nhích hơn ngẫu nhiên một chút nhưng cách biệt (+0.14 vs +0.13) gần như không có
ý nghĩa gì. Cả hai bản đều yếu khi đo bằng phương pháp có đối chứng.

Từng loại vùng của v2:

| Loại | n | chênh | % thắng | Đọc |
|---|---:|---:|---:|---|
| HVN tuần | 11 | **+0.31** | 64% | khá nhất, nhưng n=11 quá nhỏ để tin |
| LVN | 23 | +0.14 | 57% | ngang mức chung |
| va_edge (1 phiên) | 23 | +0.03 | 57% | yếu |
| HVN ngày | 17 | +0.04 | 53% | yếu |
| **priorhl** | 16 | **−0.68** | 62% | tệ nặng — đã truy, xem §3 |
| poc_cluster | 10 | +0.11 | 50% | quá nhỏ |
| value_band | 2 | +1.62 | 50% | n=2, vô nghĩa |

---

## 3. Đã truy: `priorhl` chênh −0.68 có phải bug đo không?

Không. In ra 16 lần chạm thật: có 2–3 outlier rất mạnh (nghịch = 10.95, 5.90, 4.71 lần
ATR — giá xuyên thẳng qua đỉnh/đáy phiên trước rồi đi tiếp rất xa) đủ để kéo trung bình
xuống âm nặng trên mẫu chỉ 16 điểm. Đây là **nhiễu thống kê thật, không phải lỗi code**.
Kết luận thực tế: đỉnh/đáy của 1 phiên trước gần như không cản được giá trong dữ liệu
này — càng ủng hộ quyết định D4 hạ cấp nhóm này.

---

## 4. Vì sao khác kết quả "87% hợp lưu" đã báo trước đó

Con số 87% (HVN tuần có HVN ngày xác nhận trong ±1 giá) và bảng backtest này đo
**hai thứ khác nhau**, không mâu thuẫn:

- 87% đo **các khung có đồng ý với nhau không** (structural agreement).
- Bảng ở §2 đo **vùng có dự báo được giá hay không** (predictive power).

Hai câu hỏi độc lập. HVN tuần và HVN ngày hoàn toàn có thể đồng ý với nhau (cùng
nhìn thấy một nút khối lượng) mà nút đó vẫn không đủ mạnh để chặn giá trên 26 ngày
dữ liệu ít biến cố này.

---

## 5. Kết luận trung thực

- **Cấu trúc D1-D6 đã làm đúng như plan, build sạch, logic khớp Python↔dự kiến.**
  Đây là việc kỹ thuật đã hoàn thành.
- **Chưa chứng minh được v2 tạo ra vùng dự báo tốt hơn v1 hoặc tốt hơn ngẫu nhiên.**
  26 ngày, ~100 lần chạm mỗi bản — quá ít để tách tín hiệu khỏi nhiễu. Cần vài tháng
  dữ liệu để nói được điều này một cách nghiêm túc.
- **Việc sửa vẫn có giá trị độc lập với con số trên**, vì căn cứ ban đầu không phải
  "vùng v2 thắng nhiều hơn" — mà là ba điều đã nêu ở `PLAN-ZONES-V2.md`: lời trader
  pro, sách, và chart bị "cây thông Noel" với vùng mạnh nhất ngoài tầm với. Ba điều
  đó vẫn đúng bất kể bảng backtest này ra sao.
- **Không được dùng bảng này để tuyên bố v2 "tốt hơn"** trong bất kỳ tài liệu nào —
  đó sẽ là bịa số. Nói đúng: v2 gọn hơn, đúng ý trader pro hơn, nhưng **hiệu quả dự
  báo chưa đo được đủ tin cậy.**
- **Việc còn lại:** chạy Quantower thật, xem vùng vẽ có hợp lý bằng mắt; gom thêm dữ
  liệu vài tháng mới đo lại backtest có ý nghĩa; D7 (VWAP) chờ chốt.
