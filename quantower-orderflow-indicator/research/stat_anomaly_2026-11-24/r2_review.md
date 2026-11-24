# Review vòng 2 (Fable, 2026-11-25) — chế độ ngưỡng "Không theo CORVEN"

> Đọc `R2-KET-QUA.md`, các script `sa2_*.py`, code C# liên quan (`CellBigLogic.cs`, `OrderFlowBubbles.cs`, `SignalCache.cs`, `perf/Golden/Program.cs`), và tự chạy hai script kiểm: `rv2_chk1.py` (kết quả `out_rv2_chk1.txt`, `out_rv2_combo.csv`, `out_rv2_short.csv`, `out_rv2_tie.csv`) và `rv2_chk2.py` (`out_rv2_chk2.txt`).
> Kết luận: **chưa chốt spec**. Số vòng 2 tin được và không có rò rỉ tương lai, nhưng tôi tìm ra một lỗi phương pháp làm con số "không sót" đẹp hơn thực tế (mục 2), và tổ hợp tham số cuối chưa có số chuẩn (mục 3). Cần một vòng đo hẹp nữa (mục 6).
> Mọi thứ ở đây vẫn là **định nghĩa hiển thị**, không phải lợi thế giao dịch.

## 1. Số vòng 2 có tin được không

| Việc kiểm | Kết quả |
|---|---|
| Rò rỉ tương lai trong `sa2_ref.py` | Không thấy. Ngưỡng chính chỉ lấy các ngày giao dịch **trước** hôm nay (`e[0] < day`, cả khung lân cận); dự phòng và biên độ chỉ nộp sau khi nến đóng; nến cuối file không nộp gì. Tự kiểm cắt dữ liệu 60% trùng |
| Bản chuẩn có đúng cách C# đọc dữ liệu không | Khớp `Golden.LoadBars` (cột, giờ UTC, nến cuối là nến đang chạy), `BigTradeLog.CellsOf` (trùng tick giữ lệnh lớn hơn), `BigTradeAdaptive.MergeTicks` (biên độ các ô có lệnh đơn, N nến, cần 5) |
| Số có hợp lý không | Có. Ngưỡng theo phiên đúng thứ tự (NQ M1: Á 10, Âu 11, Mỹ 31 hợp đồng); chấm/nến tăng theo khung như đã báo trước; không có ngưỡng dưới 5 |
| Tôi chạy lại tổ hợp K = 5 bằng script riêng | Ra đúng các số Opus báo cho K = 5 (NQ M15 đoạn chọn: 5 ô lớn nhất phiên 0,920) |

Trả lời 8 vấn đề Opus ghi:
1. Tên file: chấp nhận. Vòng 3 dùng tiền tố `sa3_` / `out_r3_`, báo cáo `R3-KET-QUA.md` và `r3_results.md` cùng nội dung.
2. Thước chấm điểm giữ UTC cho mọi cấu hình: đúng, để so trên một thước.
3. Mốc 300 nến cho phép thử buổi tối: chấp nhận, mốc 400 là tôi đặt sai.
4. Hai luật chọn ra hai hướng: tôi phân xử ở mục 3.
5. Mục tự kiểm tính tay sai: không ảnh hưởng.
6. Các chỗ bản chuẩn phải đoán: chấp nhận hết, **trừ một chỗ phải đổi**: nến không có ô nào có volume > 0 thì **bỏ hẳn** (không tính là một nến của hàng đợi dự phòng, không đánh dấu khung giờ có xuất hiện), vì `AddToBaseline` của C# thoát sớm với nến như vậy. Nến có ô volume > 0 nhưng Bid = Ask = 0 vẫn là một nến (nộp 0 mẫu).
7, 8. File tạm và việc commit: agent chính lo.

## 2. Lỗi phương pháp: thước "không sót" tính cả ô vượt ngưỡng mà không được vẽ

PLAN 4.3 coi một ô là "đã được nổ" khi nó **vượt ngưỡng thô**, kể cả khi sau bước gộp không có chấm nào được vẽ. Bước gộp hiện tại ("lớn hơn hẳn mọi tick khác trong ±w", đúng `CellBigLogic.LocalMax`) có hai kiểu làm mất chấm:
- **Bằng nhau:** hai ô cùng bên, cách nhau ≤ w tick, cùng giá trị lớn nhất → **cả hai đều không được vẽ**.
- **Chuỗi che:** ô A 20 ở tick 0, ô B 15 ở tick 3, ô C 12 ở tick 6, w = 4. A được vẽ; B bị A che; C bị B che dù cách A tới 6 tick → quanh C không có chấm nào.

Số đo (`rv2_chk2.py`, cấu hình K = 5, tối thiểu 2 ngày; "nhìn thấy" = có chấm cùng nến, cùng bên, cách ≤ w tick):

| Ô | (nến, bên) có vượt ngưỡng nhưng không có chấm nào (tất cả do bằng nhau) | 20 ô lớn nhất ngày **nhìn thấy**: luật hiện tại → chọn tham lam | Số chấm tăng khi chọn tham lam |
|---|---|---|---|
| GC M1 kiểm | 172 / 10.130 | 0,996 → 1,000 | +4,0% |
| GC M5 kiểm | 76 / 4.436 | 0,987 → 1,000 | +5,7% |
| GC M15 kiểm | 29 / 2.203 | 0,989 → 1,000 | +6,2% |
| NQ M1 kiểm | 489 / 21.701 | 0,964 → 1,000 | +6,3% |
| NQ M5 kiểm | 174 / 7.256 | 0,964 → 1,000 | +8,5% |
| NQ M15 kiểm | 54 / 3.008 | 0,968 → 1,000 | +9,7% |
| NQ M15 chọn | 74 / 3.668 | 0,963 → 1,000 | +10,3% |

Đọc: con số "20 ô lớn nhất ngày 1,000" của vòng 2 là trên vượt ngưỡng thô. Thứ người học nhìn thấy trên chart chỉ đạt 0,96–0,99, tức ở NQ khoảng 3–4% số ô lớn nhất ngày **không có bóng nào quanh nó**. Người học yêu cầu "không bỏ sót", nên đây là lỗi phải sửa trước khi viết spec.

Cách sửa đề xuất, **chọn tham lam**: trong các ô vượt ngưỡng của một (nến, bên), duyệt giá trị giảm dần (bằng nhau thì tick thấp trước), giữ ô nếu chưa có ô đã giữ nào cách nó ≤ w tick. Theo cách dựng, mọi ô vượt ngưỡng đều là chấm hoặc cách một chấm ≤ w tick. C# đã có sẵn hàm này (`CellBigLogic.MergeAdjacent`), và Big Trade đang dùng đúng kiểu đó. Số trên là bản thử nhanh của tôi, chưa có bản chuẩn từng nến và chưa chấm lại nhiễu, nên vòng 3 phải đo đủ.

## 3. Phân xử hai luật chọn chấm

Vòng 2 chỉ đổi một yếu tố mỗi lần, nên tôi đo thêm tổ hợp (`rv2_chk1.py`, 6 ô × 2 đoạn):

| Cấu hình | Tổng trượt | Tỉ lệ chấm trùng khi chỉ nạp 8 ngày (gộp 6 ô) |
|---|---|---|
| gốc (K 10, tối thiểu 3 ngày, T 120) | 1 | 0,817 |
| K 5, tối thiểu 3 ngày, T 120 | 1 | 0,851 |
| K 5, tối thiểu 2 ngày, T 120 | 1 | 0,881 |
| K 5, tối thiểu 1 ngày, T 120 | **2** (thêm Khớp chung NQ M15 đoạn chọn 1,254) | 0,899 |
| K 5, tối thiểu 1 ngày, T 240 | **2** | 0,898 |

- Luật 1 (ít trượt hơn thì thay; K = 5 thắng khi bằng): **K = 5**. Thêm một lý do đo được: với K = 5, chart nạp ít ngày trùng với nạp đủ cao hơn K = 10 ở mọi tổ hợp (0,85–0,90 so với 0,81–0,85).
- Luật 2 chọn "tối thiểu 1 ngày", nhưng ghép với K = 5 thì trượt nhiều hơn gốc, trái luật 1. Tôi xếp luật 1 trên luật 2 (tiêu chí PLAN là chính, độ trùng khi nạp ít ngày là phụ). Trong các tổ hợp không trượt nhiều hơn gốc, trùng cao nhất là **tối thiểu 2 ngày, T = 120**.
- Đây là quyết định **sau khi xem số**, người đọc nên biết. T = 120 và T = 240 gần như không khác nhau (lệch 0,001–0,008).

Luật 3 (mức 2%): cấu hình gốc trượt "5 ô lớn nhất phiên" ở NQ M15 đoạn chọn (0,929). Tôi tách ô sót theo giờ: 38 / 39 ô nằm ở nến 13:00 và 13:15 UTC, tức nửa giờ ngay trước giờ mở cửa cổ phiếu Mỹ. Cơ chế: gộp khung giờ lân cận kéo ngưỡng của nửa giờ đó lên theo nửa giờ mở cửa (ngưỡng khoảng 110 hợp đồng, trong khi phiên Âu thường 27). Đây là điểm yếu thật của việc gộp lân cận, không phải của mức 2%. **Giữ 2% làm mặc định**; mức 1% trượt 4, mức 0,5% trượt 14. Vòng 3 đo lại "không lân cận" trên nền K = 5 để biết có bỏ lân cận được không.

Giờ Chicago: bằng chứng yếu hơn tôi nói ở vòng 1. Tuần đổi giờ 02–06/11 nó không cải thiện rõ số giờ đạt; tổng trượt chỉ hơn giờ UTC 1 lần (1 so với 2). Giữ giờ Chicago vì ít trượt hơn và đúng cơ chế (sàn CME chạy theo giờ Chicago), nhưng không được viết là "xóa hẳn lỗi đổi giờ".

## 4. Big Trade

- Áp luật chọn viết trước: **phân vị cuốn, cửa sổ A, 240 phút, mức 1%** (`cuon_A_T240_p1`). GC kiểm, NQ, GClive ở M1–M15: Khớp chung 1,05–1,18; 20 ô lớn nhất ngày 0,975–1,000; nhiễu ≤ 1,6%; không có vòng ≤ 3 hợp đồng. Bước gộp của Big Trade đã là chọn tham lam nên không dính lỗi mục 2.
- Điểm yếu phải viết cho người học:
  - **NQ, đầu phiên Á**: 4 giờ đầu còn dùng lệnh đơn của phiên Mỹ nên ít vòng (khớp phiên Á 0,68, phiên Âu 1,40; tỉ lệ cao / thấp 2,07, vượt mức 1,8 của PLAN). Cửa sổ 120 phút bám phiên tốt hơn (0,87 / 1,24) nhưng ở M15 chỉ 78% nến có ngưỡng và Khớp chung 1,26–1,28, nên luật chọn loại nó.
  - **NQ chỉ có 6 phiên**, không có đoạn kiểm. Kết luận Big Trade yếu hơn chấm.
  - Nhật ký chỉ có buổi tối: đầu buổi dùng lệnh đơn của buổi tối hôm trước (trung bình 1 nến M1 chưa có ngưỡng). Nếu lâu không mở chart, ngưỡng lấy từ dữ liệu cũ cho tới khi đủ 240 phút mới.
- Cửa sổ C bị loại (mỗi buổi phải chờ lại 22 nến M1). Mức 0,5% bị loại (M15 thiếu mẫu).
- Không cần đo thêm cho Big Trade; vòng 3 chỉ cần ra lại đúng số chuẩn 3.330 / 864 / 1.913 / 788.

## 5. Những gì đã đủ để viết spec (ghi lại để vòng 3 không phải bàn lại)

- Chế độ mới là một ô chọn "Chế độ ngưỡng: Theo CORVEN / Không theo CORVEN (thống kê)", **mặc định Theo CORVEN** cho tới khi người học duyệt; golden cũ không đổi.
- Chấm: khung giờ theo giờ Chicago, rộng `max(30, phút một nến)`; tập tham chiếu = 5 ngày giao dịch trước; mức 2% (cho chọn thêm 1% và 0,5%); dự phòng cuốn 120 phút khi khung giờ chưa đủ 2 ngày; không sàn, không che, không bộ số theo mã.
- Big Trade: như mục 4; nến chưa có ngưỡng thì không vẽ.
- Ô cũ khi chế độ mới bật: "Nổ ở mọi mức giá" vẫn có tác dụng (vẽ mọi ô vượt ngưỡng); sàn tối thiểu, bộ số, bộ Nasdaq, mật độ đích, sàn và giới hạn vòng của Big Trade bị bỏ qua.
- Điều còn thiếu: luật gộp chấm (mục 2), có gộp lân cận hay không (mục 3), và số chuẩn Python cho cấu hình cuối.

## 6. Việc vòng 3 (Opus; chỉ Python, không sửa C#, không commit)

Script mới tiền tố `sa3_`, kết quả `out_r3_*.csv`, báo cáo `R3-KET-QUA.md` (và `r3_results.md` cùng nội dung). Dùng lại `sa2_lib.py`, `sa2_ref.py` (sửa tại chỗ hoặc chép sang `sa3_`, tùy cách nào ít rủi ro hơn).

### 6.1 Sửa luật và bản chuẩn

- Thêm tham số **cách chọn chấm** vào bản nhanh và bản chuẩn (`--set sel=lmax|nms|all`):
  - `lmax`: như vòng 2 (lớn hơn hẳn mọi tick khác trong ±w).
  - `nms` (chọn tham lam): với từng (nến, bên), lấy các ô vượt ngưỡng, sắp giá trị giảm dần, bằng nhau thì tick thấp trước; giữ ô nếu chưa có ô đã giữ nào cách nó ≤ w tick. Đúng `CellBigLogic.MergeAdjacent`.
  - `all`: mọi ô vượt ngưỡng (ô "Nổ ở mọi mức giá").
- Bản chuẩn: nến không có ô nào volume > 0 thì bỏ hẳn (mục 1, điểm 6). Khung lân cận: lấy tập {khung − 1, khung + 1} quay vòng, **bỏ khung trùng nhau và trùng khung chính** (chỉ khác khi một ngày có dưới 3 khung, ví dụ nến ngày).
- **Cấu hình nền mới**: giờ Chicago, K = 5, có lân cận, tối thiểu 2 ngày, T = 120, p = 2%, `sel = nms`.
- Tự kiểm: ví dụ tính tay cho `nms` (hai ô bằng nhau 12 và 12 cách 1 tick → giữ ô tick thấp; chuỗi 20 ở tick 0, 15 ở tick 3, 12 ở tick 6, w = 4 → chấm ở tick 0 và tick 6); bản chuẩn = bản nhanh từng dấu trên GC M5, GC H1, NQ M1, NQ M15 cho `sel = nms` và `sel = lmax`; kiểm cắt dữ liệu; kiểm nạp 8 ngày cuối.

### 6.2 Bảng điểm (GC, NQ × M1 … H1, đoạn chọn và đoạn kiểm)

- Cấu hình, mỗi lần đổi một yếu tố so với nền mới: `sel = lmax`; không lân cận; p = 1%; p = 0,5%; tối thiểu 1 ngày. Cộng nền mới và hai mốc đối chứng luật đang chạy. Tổng 8.
- Thêm thước **"nhìn thấy"** cho ba tiêu chí không sót (20 ô lớn nhất ngày, 5 ô lớn nhất phiên, cực trị rõ): ô được tính khi cùng nến, cùng bên có chấm cách ≤ w tick (**không** tính vượt ngưỡng thô). Báo cả số cũ lẫn số "nhìn thấy". Đạt / trượt của ba tiêu chí này từ nay tính trên số "nhìn thấy"; ngưỡng đạt giữ nguyên (99% / 97% / 97%). Năm tiêu chí còn lại giữ nguyên.
- Mỗi cấu hình: số lần trượt trên 6 ô (GC, NQ × M1, M5, M15) của từng đoạn, kèm trượt cái gì; nhiễu; tỉ lệ chấm ≤ 3 hợp đồng.
- Mật độ cho nền mới và `sel = lmax`: chấm/nến chung và theo phiên, theo khung; phân vị 50 / 95 / lớn nhất số chấm một nến; vượt thô mỗi nến; chấm/nến từng ngày (nhỏ nhất / phân vị 10 / 50 / 90 / lớn nhất); ngưỡng theo phiên.
- "5 ô lớn nhất phiên" của NQ M15 và M30: bảng ô sót theo giờ UTC cho "có lân cận" và "không lân cận".
- Chart nạp ít ngày cho nền mới: cắt còn 3, 8, 15 ngày giao dịch cuối; tỉ lệ chấm trùng gộp và theo ngày.
- So tham khảo CORVEN cho nền mới (chỉ báo số).

**Luật chọn viết trước** (Fable áp ở vòng sau, không bàn lại):
- `nms` thay `lmax` khi cả ba điều sau đúng trên mọi ô trong 12 ô (6 ô × 2 đoạn): "20 ô lớn nhất ngày nhìn thấy" của `nms` ≥ của `lmax`; `nms` vẫn đạt nhiễu ≤ 5% và chấm ≤ 3 hợp đồng ≤ 2%; chấm/nến của `nms` không cao hơn `lmax` quá 15%. Nếu một điều sai thì báo rõ điều nào, ô nào.
- "Không lân cận" thay "có lân cận" chỉ khi tổng số lần trượt (hai đoạn cộng lại) **ít hơn**. Bằng nhau thì giữ có lân cận.
- "Tối thiểu 1 ngày" thay "tối thiểu 2 ngày" chỉ khi tổng số lần trượt không nhiều hơn nền mới **và** tỉ lệ chấm trùng ở phép thử nạp 8 ngày cao hơn từ 0,01 trở lên.
- Mức mặc định giữ 2%.

### 6.3 Số chuẩn cho C# (bản chuẩn đọc đúng file của Golden)

- Chấm đỏ / chấm xanh trên `tf/fp_{GC,NQ}_m{1,5,15,60}.csv` cho: nền mới (`sel = nms`); nền mới với `sel = lmax`; nền mới với p = 1%; nền mới với "không lân cận".
- `sel = all` trên GC M5 và NQ M15.
- Nạp ít ngày: `--from` đầu ngày thứ 8 tính từ cuối, trên GC M5 và NQ M15, nền mới.
- Big Trade `cuon_A_T240_p1` trên 4 nhật ký `btlog_{NQ_M1, NQ_M15, GC_M5, GC_M30}.csv` (chấm chạy cùng lúc theo nền mới); số vòng phải ra lại 3.330 / 864 / 1.913 / 788.
- Mỗi dòng: lệnh đã chạy, sha1 các file đầu vào, số nến ngưỡng chính / dự phòng / chưa có.
- Ghi thêm `out_r3_chuan_ngay.csv` **trong thư mục nghiên cứu** (không phải thư mục tạm): mỗi (dòng số chuẩn, ngày UTC) một dòng với số chấm đỏ, chấm xanh, vòng Big Trade, để khi C# lệch thì biết lệch từ ngày nào dù file dấu trong thư mục tạm đã mất.

### 6.4 Điều kiện xong vòng 3

- Mọi tự kiểm in ĐẠT.
- `R3-KET-QUA.md` có: bảng điểm 6.2 (hai đoạn, cả số cũ lẫn số "nhìn thấy"), bảng mật độ, bảng nạp ít ngày, bảng số chuẩn 6.3, mục bất thường, và kết quả áp từng luật chọn thành một dòng riêng. Opus **không** chọn mặc định.
