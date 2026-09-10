# STACKED IMBALANCE → giá có đi tiếp theo chiều của nó không?

**Ngày đo:** 2026-09-10 · **Script:** `research/stack-imb-follow.py` · **Đặc trưng:** `research/stack_imb_feats.csv`
**Dữ liệu:** `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv` (583 MB, 11,4 triệu
dòng per-level) + file `_bars.csv` cùng tên → **724.179 nến M1** có đủ nền 100 nến.

Câu hỏi của người học: (1) đổi điều kiện khối lượng tối thiểu từ `>` sang `>=` thì được thêm bao nhiêu ca?
(2) sau một **stacked sell imbalance** giá có đi **xuống** tiếp không (và ngược lại với buy) — tức có đáng
code thành tín hiệu vào lệnh **theo chiều** của nó không?

Luật lấy đúng từ `quantower-orderflow-indicator/OrderFlowBubbles.cs`: chéo 300%, ≥3 mức liên tiếp,
`imbMinVol = max(5, trung vị volume/ô của nền)`, nền = 100 nến × **3 ô đậm nhất** mỗi nến (dòng 1061-1065).
Chống bẫy: loại mọi cửa sổ vắt qua bước nhảy giá >20 giá/nến (mã liên tục nối thô) hoặc khoảng nghỉ
>5 phút/nến; **tách đôi thời gian** nửa đầu / nửa sau.

## 1. Tần suất và ngưỡng thật

| Biến thể | ≥3 mức | ≥4 mức |
|---|---|---|
| sell, điều kiện `>` (hiện tại) | 2.832 nến — **0,39%** | 708 — 0,10% |
| sell, điều kiện `>=` | 4.903 nến — **0,68%** | 1.354 — 0,19% |
| buy, điều kiện `>` | 2.992 — 0,41% | 765 — 0,11% |
| buy, điều kiện `>=` | 5.058 — 0,70% | 1.439 — 0,20% |

⇒ Một dấu bằng làm số ca **tăng ~73%**, nhưng vẫn chỉ 0,7% số nến.

**`imbMinVol` thật (GC liên tục 2 năm): trung vị 11,0** · phân vị 10% = 5,0 · 90% = 23,0.
(Trên riêng `GCZ26` tháng 8/2026 đo được **8,0** — mã và giai đoạn khác nhau cho ngưỡng khác nhau.)

## 2. Giá sau đó — % số ca đi ĐÚNG CHIỀU của imbalance

Đối chứng bắt buộc: base rate của **mọi nến** cùng chiều (thị trường 2 năm nghiêng tăng nên
base rate xuống ≠ 50%).

| Sau k nến | SELL `>=` nửa đầu | nửa sau | **đối chứng: mọi nến, chiều xuống** |
|---|---|---|---|
| 5 | 46,2% | 46,1% | 47,2% / 48,7% |
| 10 | 47,1% | 46,3% | 47,5% / 48,6% |
| 20 | 47,9% | 46,6% | 47,4% / 48,7% |

| Sau k nến | BUY `>=` nửa đầu | nửa sau | **đối chứng: mọi nến, chiều lên** |
|---|---|---|---|
| 5 | 50,0% | 48,8% | 49,2% / 49,6% |
| 10 | 51,6% | 49,4% | 49,9% / 50,2% |
| 20 | 51,2% | 50,3% | 50,8% / 50,4% |

Trung vị dịch chuyển ở k=20: sell −0,10 / −0,40 giá (đối chứng −0,10 / −0,10); buy +0,10 / +0,10
(đối chứng +0,10 / +0,10). Siết lên **≥4 mức** không cứu được: sell 45,6% / 47,3%, buy 52,6% / 49,0%.

## 3. Kết luận

1. **Không có follow-through.** Sell imbalance đi xuống **kém hơn** nến ngẫu nhiên ở nửa sau
   (46,6% vs 48,7% = **−2,1 điểm**); buy imbalance bằng đúng base rate (+0,4 rồi −0,1 điểm).
2. **Không nhất quán giữa hai nửa** ⇒ ngay cả phần lệch dương nhỏ ở buy nửa đầu cũng không sống sót.
3. **Biên độ quá nhỏ để trả phí:** trung vị 0,1-0,4 giá sau 20 nến, trong khi spread + phí GC đã
   ăn hết mức đó.
4. ⛔ **Không code stacked imbalance thành tín hiệu vào lệnh theo chiều.** Việc nới `>` → `>=` chỉ
   làm ca nhiều hơn 73%, **không** làm tín hiệu tốt hơn (thậm chí sell nửa sau tệ hơn một chút).
5. Việc nới `>` → `>=` vẫn **đáng làm cho phần HIỂN THỊ** (đọc chart bằng mắt) — nó phục hồi đúng nhóm
   ca "một phe = 0" đang bị loại vô lý, như cây nến người học gửi. Nhưng chỉ để **nhìn**, không để bấm cò.
6. Hướng còn mở (chưa đo): stacked imbalance **có điều kiện theo vị trí** — chỉ tính khi nằm tại
   HVN / naked POC / biên vùng giá trị. Đây là phép đo khác, phải làm riêng.

## Lỗi đã sửa trong lượt này
Kết quả cũ trong `XANH-DAU-DO-DIT-KET-QUA.md` ghi "stacked imbalance chỉ nổ ở 0,0-0,1% số nến" — con số
đó là tỷ lệ **trong band 30% trên/dưới nến**, không phải toàn nến, và nền của script cũ nạp **mọi ô**
thay vì 3 ô đậm nhất (⇒ ngưỡng 5 thay vì 11). Số đúng cho toàn nến: **0,39%** (`>`) và **0,68%** (`>=`).
