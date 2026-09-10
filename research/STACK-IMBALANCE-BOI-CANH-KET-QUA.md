# STACKED IMBALANCE trong BỐI CẢNH — có phải dấu hiệu của phe chủ động thật?

**Ngày đo:** 2026-09-10 · **Script:** `research/stack-imb-boi-canh.py` · **Log:** `research/_stack_boicanh_log.txt`
**Dữ liệu:** 724.279 nến M1 GC (2 năm, file per-level 583 MB → `research/stack_imb_feats.csv`), loại
**179 phiên** dính chỗ nối hợp đồng. Ngưỡng imbalance dùng biến thể `>=` (chéo 300%, ≥3 mức).

Người học chốt rõ: **không** biến thành signal, chỉ muốn biết stacked imbalance có phải **dấu hiệu phe
chủ động thật** khi đặt vào bối cảnh. Ba rule do người học đặt:

1. **Bias VWAP ngày** (reset 22:00 UTC = đầu phiên CME): trên VWAP chỉ xét **buy** imbalance, dưới VWAP
   chỉ xét **sell** imbalance.
2. **Kịch bản A — tiếp diễn sau nhịp hồi:** có move ≥2,0 giá theo chiều bias trong 20 nến trước, rồi hồi
   ≥30% biên độ move, rồi nến tín hiệu đi theo chiều move và có stacked imbalance cùng chiều.
3. **Kịch bản B — giữa move:** nến tín hiệu nằm trong chuỗi ≥3 nến liên tiếp cùng chiều, có stacked
   imbalance cùng chiều.

**Đối chứng (điểm cốt tử của phép đo):** cùng bias, cùng bối cảnh, cùng chiều nến — nhưng **không có**
stacked imbalance. Nó trả lời đúng câu "imbalance THÊM được gì so với chính bối cảnh đó".

## Kết quả — % số ca giá đi đúng chiều sau 20 nến (nửa đầu / nửa sau)

| Kịch bản | Chiều | CÓ imbalance | KHÔNG imbalance (đối chứng) | Lệch |
|---|---|---|---|---|
| A (sau nhịp hồi) | SELL | 52,6% / 50,0% (n=171/164) | 47,5% / 47,6% | **+5,1 / +2,4** |
| A (sau nhịp hồi) | BUY | 56,2% / 48,8% (n=162/172) | 51,4% / 49,9% | +4,8 / **−1,1** |
| **B (giữa move)** | **BUY** | **53,1% / 56,1%** (n=409/289) | 49,4% / 47,9% | **+3,7 / +8,2** |
| B (giữa move) | SELL | 45,9% / 46,4% (n=366/274) | 45,5% / 46,5% | +0,4 / −0,1 |
| Chỉ bias VWAP | BUY | 52,2% / 52,2% (n=1196/744) | 50,0% / 49,5% | **+2,2 / +2,7** |
| Chỉ bias VWAP | SELL | 47,9% / 45,9% (n=1060/669) | 46,6% / 47,5% | +1,3 / −1,6 |

Trung vị dịch chuyển 20 nến của ca **B-BUY**: **+0,20 / +0,70 giá** (đối chứng +0,00 / −0,20).

Chân trời ngắn (3-5 nến) **không có gì** ở mọi kịch bản: B-BUY k=3 chỉ +0,9/+2,7 và k=5 đổi dấu
(−1,4/+2,4); A-BUY k=3 nhìn rực rỡ ở nửa đầu (57,7% vs 48,0% = **+9,7**) nhưng nửa sau **−1,0** —
đúng cái bẫy mà phép tách đôi thời gian tồn tại để bắt.

## Kết luận

1. **Bối cảnh CÓ làm stacked imbalance có nghĩa** — khác hẳn phép đo trần trụi hôm nay
   (`STACK-IMBALANCE-FOLLOW-KET-QUA.md`: sell 46,6% vs đối chứng 48,7%, tức tệ hơn ngẫu nhiên).
2. **Nhưng chỉ một phía: phía MUA, trên VWAP ngày.** Bên bán dưới VWAP không có gì ở cả hai kịch bản
   (B-SELL +0,4/−0,1). Bất đối xứng này khớp với việc vàng 2 năm qua là xu hướng tăng — chưa thể tách
   "imbalance mua thật mạnh hơn" khỏi "thị trường tăng nên mọi thứ mua đều tốt hơn".
3. **Kịch bản B (GIỮA move) mạnh hơn kịch bản A (sau nhịp hồi)** — trái trực giác "chờ pullback rồi vào".
   Đây là ứng viên duy nhất **cùng dấu ở cả hai nửa với biên độ tăng dần** (+3,7 → +8,2).
4. Chỉ có nghĩa ở **chân trời ~20 nến**, không phải 3-5 nến. Tức nó là dấu hiệu **phe chủ động đang
   kiểm soát đoạn tới**, không phải cò bấm ngay.
5. ⚠️ **n nhỏ** (289-409 mỗi nửa ở B-BUY): +8,2 điểm với n=289 ≈ 2,8σ — **đáng theo dõi, chưa đủ để
   kết luận**. Muốn chắc phải mở rộng bằng mã khác hoặc kỳ dài hơn.
6. Trạng thái theo bảng ở `tpo/EVIDENCE-DRILLS.md`: **được dùng đọc chart** (đúng đúng mục đích người
   học nêu — dấu hiệu nhận biết phe chủ động), **chưa được code thành signal**.

---

# LẦN 2 — tách riêng đóng góp của BIAS VWAP

**Script:** `research/stack-imb-boi-canh-2.py` · **Log:** `research/_stack_boicanh2_log.txt` · 483.042 ca.

Lần 1 **đã** lồng bias VWAP vào cả A và B. Lần này chạy ba biến thể để thấy VWAP đóng góp bao nhiêu:
**THEO** (như lần 1) · **BỎ** (không xét VWAP) · **NGƯỢC** (buy dưới VWAP, sell trên VWAP).
Mỗi ô so với đối chứng **cùng kịch bản, cùng biến thể VWAP, cùng chiều nến, không có imbalance**.

## Lệch so với đối chứng (điểm phần trăm), nửa đầu / nửa sau

| Kịch bản · chiều | k | THEO VWAP | BỎ VWAP | NGƯỢC VWAP |
|---|---|---|---|---|
| **B · BUY** | 10 | +2,9 / +2,0 | +3,0 / +2,3 | +2,9 / +3,0 |
| **B · BUY** | 20 | **+3,7 / +8,1** | **+3,8 / +4,9** | +4,1 / −3,7 |
| B · SELL | 20 | +0,4 / −0,1 | +1,7 / −0,3 | +4,6 / −0,8 |
| A · SELL | 20 | +5,1 / +2,4 | +5,0 / +1,2 | +4,4 / −0,4 |
| A · BUY | 20 | +4,7 / −1,0 | −2,2 / −1,5 | −15,7 / −2,2 |

Số ca (B·BUY, k=20): THEO 409/289 · BỎ **566/396** · NGƯỢC 157/107.

## Kết luận lần 2

1. **Bias VWAP KHÔNG đóng góp gì.** Ở ô mạnh nhất (B·BUY, k=10) ba biến thể cho +2,9 / +3,0 / +2,9 —
   gần như trùng khít; k=20 nửa đầu cũng vậy (+3,7 / +3,8 / +4,1). Kể cả làm **ngược** VWAP vẫn ra lệch
   dương. Một điều kiện mà bật, tắt, hay đảo ngược đều cho cùng kết quả thì **không mang thông tin**.
2. **Cái thật sự mang lại lệch là "GIỮA MOVE + buy imbalance", chân trời 10-20 nến** — sống sót ở cả hai
   nửa thời gian trong cả THEO và BỎ.
3. **Bỏ VWAP còn tốt hơn về mặt thống kê:** cùng mức lệch nhưng n tăng ~38% (566/396 so với 409/289).
   Giữ VWAP chỉ làm mất một nửa số ca mà không mua thêm được độ tin cậy nào.
4. A·BUY sụp khi bỏ VWAP (+4,7 → −2,2) ⇒ phần "đẹp" của A·BUY lần 1 là **trùng hợp của tập con nhỏ**
   (n=162), không phải hiệu ứng.
5. A·SELL ổn định ~+5 nửa đầu ở cả ba biến thể nhưng nửa sau tụt (+2,4 / +1,2 / −0,4), và k=5-10 nửa sau
   âm ⇒ yếu hơn B·BUY, chưa đáng theo.

---

# LẦN 3 — chỉ đo 2,5 tháng gần nhất (2026-06-01 → 2026-08-19)

Người học yêu cầu đo riêng giai đoạn gần. Dữ liệu mới nhất trong repo dừng ở **19/8/2026**, nên khoảng
đo là **1/6 → 19/8/2026** (32.707 cây nến đi theo chiều).
Chạy: `python research/stack-imb-boi-canh-2.py 2026-06-01` (log `_stack_3thang_log.txt`) và bản gộp cả kỳ
(`_stack_3thang_gop.txt`).

## Số ca sụp xuống mức không đo được

| Nhóm (gộp cả kỳ, sau 20 phút, bỏ điều kiện VWAP) | Số ca | Đúng chiều | Đối chứng cùng hoàn cảnh | Chênh |
|---|---|---|---|---|
| Mua dồn giữa đợt tăng | 89 | 46,1% | 45,2% (3.399 ca) | +0,8 |
| Mua dồn giữa đợt tăng (giữ điều kiện VWAP) | 58 | 46,6% | 44,3% | +2,3 |
| Bán dồn giữa đợt giảm | 99 | 42,4% | 47,4% (3.500 ca) | **−5,0** |
| Mua dồn sau nhịp hồi | 32 | 53,1% | 50,1% | +3,0 |

Với 89 ca, sai số một lần đo đã là **±5 điểm** ⇒ không phân biệt được +0,8 với 0, mà cũng **không loại
trừ** được mức +4 đo trên hai năm.

## Kết luận lần 3

1. **2,5 tháng là quá ngắn để đo hiện tượng này.** Dồn ba mức chỉ xảy ra ở 0,7% số nến; thêm điều kiện
   bối cảnh thì còn vài chục ca. Không xác nhận cũng không phủ định được kết quả hai năm.
2. **Bối cảnh thị trường giai đoạn này khác rõ:** nến tăng nói chung chỉ tiếp tục lên **45 trên 100 lần**
   (hai năm là 49-50) ⇒ giai đoạn 6-8/2026 giá đảo qua đảo lại nhiều hơn, mọi dấu hiệu *tiếp diễn* đều
   kém đi. Đây là thông tin đáng giữ, độc lập với chuyện imbalance.
3. **Phía bán vẫn nghiêng ngược** (−5,0) — lặp lại đúng điều đã thấy trên hai năm.
4. Muốn đo được trên khoảng vài tháng thì phải **nới định nghĩa dồn xuống 2 mức liên tiếp** (số ca tăng
   khoảng 4-5 lần). Chưa chạy.
