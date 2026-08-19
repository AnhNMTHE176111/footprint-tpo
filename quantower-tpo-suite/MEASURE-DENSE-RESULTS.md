# Kết quả đo trên dữ liệu DÀY 2 năm (2026-08-19)

Nguồn: `data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h.csv`
(+ `_bars.csv`) — /GC:XCEC, **529 phiên**, trung vị **143.142 hợp đồng/phiên**,
1.377 nến M1/phiên. Đây là lần đầu bộ đo chạy trên khối lượng thật.

So với lần đo cũ (`MEASURE-LEVELS-RESULTS.md`): file cũ chỉ **657 hợp đồng/phiên**
— mỏng hơn **218 lần**. Kết luận cũ vì thế coi như bỏ.

## 0. Ba việc phải làm đúng trước khi đo

**Chia phiên theo giờ nghỉ, không theo ngày lịch.** Ngày lịch UTC cắt đôi phiên
(2 tiếng đầu phiên bị tính sang hôm trước) — hỏng đúng đoạn mở cửa. `dense_prep.py`
chia phiên bằng khoảng trống > 30 phút và đặt tên phiên theo nến cuối, đúng quy ước CME.

**Loại chỗ nối hợp đồng.** Tìm được **8 chỗ nối** trong 2 năm, bước nhảy tới **+61,2 giá**,
luôn rơi vào giờ nghỉ 1 tiếng. Cộng 3 cửa sổ đổi hợp đồng mà bước nhảy quá nhỏ để bắt
(2024-11, 2025-01, 2026-03). Loại ±2 phiên quanh mỗi chỗ ⇒ **474 phiên sạch** để đo.

**Nền so sánh phải chạy nhiều lần.** Chỉ đổi hạt giống ngẫu nhiên, nền đã nhảy từ
33,8% lên 37,5%. Chạy 200 lần mới ra nền thật: **38,2% ± 5,2 điểm**. Một lần bốc là
vô nghĩa — đây là lỗi của bản đo cũ.

## 1. Phép đo thắng/thua (SL 3 giá / TP 4,5 giá / 60 nến M1, fade lần chạm đầu)

| Mốc | n | thắng | CI95 | kỳ vọng |
|---|---|---|---|---|
| Mức **ngẫu nhiên** (nền, 200 lần) | — | **38,2% ± 5,2** | — | — |
| HVN ngày ×1,5–2,0 | 200 | 36,5% | [30,1%, 43,4%] | −0,26 giá |
| HVN ngày ×2,0–2,5 | 255 | 36,9% | [31,2%, 42,9%] | −0,24 giá |
| HVN ngày ×2,5–3,0 | 148 | 35,8% | [28,5%, 43,8%] | −0,31 giá |
| HVN ngày ×3,0+ | 116 | 44,8% | [36,1%, 53,9%] | +0,36 giá |
| HVN ngày ×3,5+ | 67 | 49,3% | [37,7%, 60,9%] | +0,69 giá |
| HVN tuần ×2,5+ | 216 | 33,3% | [27,4%, 39,9%] | −0,50 giá |
| Giá đóng cửa phiên trước | 308 | 32,8% | [27,8%, 38,2%] | −0,54 giá |

Nhìn qua thì HVN ×3,5+ (49,3%) có vẻ là thứ đáng làm. **Nó không sống nổi qua kiểm định.**

## 2. Ba phép kiểm — và cái "có vẻ ăn" chết ở phép thứ hai

**Tách đôi thời gian** (luật thật phải có ở cả hai nửa):

| | nửa đầu (2024-08→2025-08) | nửa sau (2025-08→2026-08) |
|---|---|---|
| HVN ×3,0+ | 36,1% (nền cùng kỳ 35,1%) → **+1,0 điểm** | 48,8% (nền 40,2%) → +8,6 điểm |
| HVN ×3,5+ | 39,1% (nền cùng kỳ 37,6%) → **+1,5 điểm** | 54,5% (nền 39,8%) → +14,7 điểm |

Lợi thế **chỉ tồn tại ở nửa sau**. Nửa đầu bằng đúng mức bốc ngẫu nhiên. Đây là dấu
hiệu kinh điển của khớp quá mức, không phải luật thị trường.

## 3. Đổi sang phép đo LIÊN TỤC — nhạy hơn nhiều, và kết luận ngược lại

Phép thắng/thua quá thô: nó đo **một chiến lược cụ thể** (vào ngay lần chạm đầu, không
chờ xác nhận) mà người học không hề đánh như vậy. Đo trực tiếp **phản ứng của giá** trong
30 nến M1 sau khi chạm sẽ nhạy hơn hẳn:

| | n | đâm xuyên (trung vị) | bật lại (trung vị) | bật/xuyên |
|---|---|---|---|---|
| Mức ngẫu nhiên | 858 | 3,50 | 4,30 | 1,17 |
| HVN ngày ≥×1,5 | 876 | 3,10 | 3,80 | 1,18 |
| HVN ngày ≥×3,0 | 139 | 3,60 | 3,90 | 1,00 |
| HVN ngày ≥×3,5 | 78 | **4,90** | 3,90 | **0,95** |

So sánh **bắt cặp** (mỗi ca HVN ghép một mức ngẫu nhiên trong **cùng phiên**):

- đâm xuyên: HVN − ngẫu nhiên = **−0,44 giá**, z = −1,17 → không có ý nghĩa
- bật lại: HVN − ngẫu nhiên = **−0,62 giá**, z = **−2,15** → có ý nghĩa, **theo chiều XẤU**

Nghĩa là giá bật lại tại HVN **ít hơn** tại mức bốc đại. Và mốc "mạnh nhất" (≥×3,5)
là mốc bị đâm xuyên **sâu nhất**. Điều này mâu thuẫn thẳng với con số 49,3% ở mục 1 —
xác nhận đó là nhiễu.

## 4. Thử đúng cách người học đánh — vẫn không cứu được

**Hợp lưu HVN × VWAP** (mốc nằm trong 3 giá quanh VWAP phiên tại đúng lúc chạm):

| | n | thắng | bật/xuyên |
|---|---|---|---|
| HVN ngày + gần VWAP | 124 | 33,9% | 1,08 |
| HVN ngày + XA VWAP | 589 | 38,0% | 1,31 |
| HVN tuần + gần VWAP | 63 | 31,7% | 0,80 |
| HVN 3 tuần + gần VWAP | 35 | 37,1% | 1,47 |
| HVN 3 tuần + XA VWAP | 277 | 40,1% | 1,23 |

Hợp lưu với VWAP làm **tệ hơn**, không tốt hơn — nhất quán ở cả 3 khung.

**Vào ở lần chạm THỨ HAI** (retest, chỉ khi lần chạm đầu bật lên ≥2 giá — đúng luật
"retest giữ vùng" của người học):

| | n | thắng |
|---|---|---|
| Ngẫu nhiên [retest] | 511 | 39,3% |
| HVN ngày [retest] | 538 | 38,8% |
| HVN tuần [retest] | 325 | 40,9% |
| HVN 3 tuần [retest] | 235 | 40,9% |

Chênh +1,6 điểm so với nền — không đáng gì.

## 5. Kết luận

Trên 474 phiên dày, qua **năm cách đo độc lập** (thắng/thua theo bậc tỉ lệ · tách đôi
thời gian · phản ứng liên tục bắt cặp · hợp lưu VWAP · retest), kết quả đều như nhau:

> **HVN của phiên/tuần trước KHÔNG phải mốc phản ứng. Nó không hơn một mức giá bốc đại
> trong cùng biên độ.**

Đây là kết quả mạnh hơn lần đo cũ rất nhiều — không phải "chưa đủ dữ liệu để kết luận",
mà là "đủ dữ liệu và câu trả lời là không".

### Điều này KHÔNG chứng minh
- Rằng HVN vô dụng làm **bối cảnh** (biết chỗ đông người giao dịch) hay làm **vùng chốt lời**.
- Rằng HVN vô dụng khi kết hợp **dòng lệnh M1** (hấp thụ, mất cân bằng) tại chỗ — chưa đo.
- Rằng cách CORVEN dùng HVN là sai — họ còn đọc thêm nhiều thứ mà bộ đo này không có.

Cái nó chứng minh: **chạm HVN, tự nó, không phải lý do vào lệnh.**

## 6. Đã sửa gì trong indicator sau khi đo

- **B10 — chặn chỗ nối hợp đồng** (`ProfileEngine.LastSpliceIndex`): profile tuần/ngày
  vắt qua chỗ nối bị cắt bỏ phần trước chỗ nối, kèm cảnh báo cam trên bảng.
  13 test chạy thật trên Linux, gồm đối chiếu C# ↔ Python trên 724.279 nến (`tests/`).
- **Dòng nhắc mức bằng chứng** cuối bảng, để không ai đọc nhầm HVN thành tín hiệu vào lệnh.
- Giữ `SharpnessGate` TẮT (dữ liệu dày làm bướu nhọn hẳn, không còn rác để dọn).
- Giữ cổng ×2,5 — **thuần để đỡ rối mắt**, không phải vì mốc mạnh ăn tiền hơn.

## 7. Việc tiếp theo đáng làm
Đo tầng **dòng lệnh M1 tại mốc** (hấp thụ / mất cân bằng chồng) thay vì tự thân mốc.
Dữ liệu từng mức giá đã có sẵn trong chính file này — chưa dùng tới cột `bid_vol`/`ask_vol`.
