# Câu hỏi cần thống nhất — trước khi code thêm bất cứ gì

> Lập 2026-07-31 theo yêu cầu người học ("bạn có muốn hỏi tôi cái gì để thống nhất lại quan điểm ko").
> Người học tự trả lời được phần lớn (hiểu hệ thống + nói chuyện trực tiếp với CORVEN).
> **Cách dùng:** điền câu trả lời ngay dưới mỗi câu hỏi. Câu nào cần hỏi lại CORVEN thì ghi "→ hỏi CORVEN".
>
> Ký hiệu: **[CHẶN]** = không có câu trả lời thì không code được. **[LỆCH]** = tôi thấy có chỗ vênh
> giữa các nguồn, cần phân xử. **[KIỂM]** = tôi muốn kiểm lại xem tôi hiểu có đúng không.

---

## A. KB-A — nhánh vùng TUẦN, hold dài (vùng tối lớn nhất)

Cả 36 ảnh TRANSCRIPT + đoạn chat 3 kịch bản đều **không có một tiêu chí vào lệnh nào** cho nhánh này.
Mà đây là kịch bản CORVEN xếp *đầu tiên*.

**A1. [CHẶN] VWAP tuần neo từ mốc nào?** Mở tuần (CME mở lại Chủ nhật ~23:00 VN / 16:00 UTC)? Hay
rolling 5 ngày trượt? Hai cách cho ra hai đường khác nhau hẳn, code khác nhau hẳn.

> *Trả lời:*

**A2. [CHẶN] TPO tuần dựng thế nào?** Gộp cả 5 ngày thành **một** profile duy nhất? Dùng gì trong đó —
chỉ POC, hay cả VAH/VAL, hay cả HVN/LVN?

> *Trả lời:*

**A3. [CHẶN] "Hold dài" là bao lâu?** Trong ngày → đóng trước phiên Mỹ? Qua đêm? Vài ngày? Và RR mục
tiêu của nhánh này khoảng bao nhiêu?

> *Trả lời:*

**A4. [CHẶN] SL của KB-A neo đâu?** Chắc chắn không thể là 2-4 giá như R7 (nhánh scalp) — vùng tuần
thì nhiễu rộng hơn nhiều. Neo ngoài biên vùng? Theo ATR ngày?

> *Trả lời:*

**A5.** Chạm vùng tuần là **vào luôn**, hay vẫn phải chờ xác nhận M5/M1 như R8 ("thiếu mỗi xác nhận
trong m5, m1")?

> *Trả lời:*

**A6.** Nhánh này **một tuần ra mấy lệnh**? Nếu chỉ 1-2 lệnh/tuần thì backtest 3 tháng chỉ được ~20
lệnh — biết trước để khỏi kỳ vọng ý nghĩa thống kê.

> *Trả lời:*

---

## B. KB-C — scalp follow order flow ("ko cản tàu")

Có nhiều luật vi mô (R1 leg do lệnh chủ động, R3 loại stop-run, R9 chất lượng nến) nhưng **thiếu đúng
cái nút bấm**: tín hiệu vào lệnh.

**B1. [CHẶN] Tín hiệu VÀO cụ thể là gì?** Imbalance xếp tầng (stacked imbalance)? Delta bùng đột biến?
Bubble/khối lượng to bất thường tại một mức? Hay "thấy tàu đang chạy thì nhảy lên"?

> *Trả lời:*

**B2. [CHẶN] Nhận biết "tàu" bằng gì?** "Ko cản tàu" nghĩa là phải xác định được đang có tàu. Bằng CVD
dốc? Bằng chuỗi nến cùng chiều? Bằng delta liên tiếp cùng dấu?

> *Trả lời:*

**B3. [LỆCH] Số học của nhánh này không khớp.** RULES.md ghi CORVEN nói **RR 1:5–1:6** và **WR 65-70%**.
Nhưng KB-C là "**vài chục lệnh/ngày**". Nếu 30 lệnh/ngày mà WR 65% ở RR5 thì mỗi ngày ăn ~+95R —
không thực tế. Nên chắc là: **RR 5-6 chỉ dành cho vài lệnh đặc biệt (giờ động, SL siêu chặt)**, còn
phần lớn lệnh scalp ăn nhỏ (1-2R?), và **WR 65-70% là của nhánh nào**? Nhờ phân xử chỗ này.

> *Trả lời:*

**B4.** Lệnh KB-C giữ bao lâu — vài chục giây, vài phút? Và TP theo R cố định hay theo "hết lực thì ra"?

> *Trả lời:*

---

## C. Chỗ tôi thấy vênh, cần phân xử

**C1. [KIỂM] Tôi đọc W5 lại như sau, đúng không?** "Đánh break thôi chú" là nói về **biên range M1
trong KB-C** — cấm mean-revert ở biên range nhỏ. Nó **không** cấm fade tại **VWAP/TPO ngày** (KB-B),
vì chính CORVEN nói "Vwap ngày scap". Nếu tôi hiểu sai thì nhánh KB2 QUAY_DAU của mình sai từ gốc chứ
không chỉ sai số liệu.

> *Trả lời:*

**C2. [LỆCH] Quan trọng — CORVEN dùng HVN thế nào?** Tôi đo được kết quả **ngược** với cách indicator
M30SessionZones đang dán nhãn: fade tại HVN/POC/băng giá trị cho EV **âm** (HVN ngày −0.375R), còn biên
VA thì dương. Cơ chế: HVN là vùng giá **được chấp nhận** → giá vào đó rồi **đi tiếp**, không đảo.
Vậy CORVEN coi HVN là **vùng canh đảo chiều**, hay là **vùng giá sẽ đi qua / mục tiêu chốt lời**?
Đây là câu tôi cần nhất, vì nó quyết định có phải sửa nhãn "VÙNG CANH" của indicator hay không.

> *Trả lời:*

**C3.** CORVEN có dùng **HVN/LVN** không, hay chỉ dùng **POC / VAH / VAL / VWAP**? (Ghi chú cũ của mình
là "HVN tuần/ngày + VWAP", nhưng chat mới anh ấy chỉ nói VWAP và TPO, không nhắc chữ HVN.)

> *Trả lời:*

**C4. [KIỂM]** Ghi chú cũ: CORVEN "**không quan tâm lắm**" VAH/VAL/POC **từng phiên Á-Âu-Mỹ**, chỉ dùng
khung ngày/tuần. Còn đúng không? Nếu đúng thì indicator M30SessionZones vẽ vùng theo từng phiên là
**đang vẽ thứ anh ấy không dùng**.

> *Trả lời:*

**C5.** R5 nói "**mỗi phiên một bias, khoá theo phiên**". Với KB-A khung tuần thì có **bias tuần** tương
tự không? Hay bias vẫn tính theo phiên rồi chỉ dùng để chọn thời điểm vào?

> *Trả lời:*

---

## D. Mức hệ thống — để biết dồn sức vào đâu

**D1. [CHẶN cho việc ưu tiên] Trong 3 kịch bản, cái nào ra tiền chính?** Nếu KB-A đóng góp 70% lợi
nhuận thì mình đang xây sai chỗ hoàn toàn — cả 3 engine hiện tại đều là intraday, không có nhánh tuần.

> *Trả lời:*

**D2.** Con số **WR 65-70%** là từ **nhật ký lệnh thật** hay là cảm nhận/ước lượng? Và tính trên cả 3
kịch bản gộp hay riêng một nhánh? (Tôi hỏi không phải để bắt lỗi anh ấy — mà vì mình đang lấy số đó
làm mốc so sánh cho bot, nếu nó là ước lượng thì phải hạ trọng số.)

> *Trả lời:*

**D3.** CORVEN có bao giờ **không giao dịch cả ngày** không, và điều kiện nào thì anh ấy đứng ngoài?
(Hệ mình chưa có luật "hôm nay không đánh".)

> *Trả lời:*

**D4.** Anh ấy chạy Sierra Chart trên `GCQ26_FUT_CME`. Đến kỳ đáo hạn thì **đổi mã thế nào**, và có
đổi cách đọc vùng khi thanh khoản chuyển sang tháng sau không? (Liên quan trực tiếp: GCQ26 vừa qua
First Notice Day 31/07, data của mình đang xấu dần.)

> *Trả lời:*

---

## E. Một câu cho riêng người học (không cần hỏi CORVEN)

**E1.** Mục tiêu thật của bạn cho bot là gì — (a) **sao chép hệ CORVEN** càng giống càng tốt, hay
(b) **tìm bất cứ thứ gì có EV dương** kể cả khác cách anh ấy làm? Hai mục tiêu này dẫn tới hai hướng
làm việc khác nhau: (a) thì tôi phải xây KB-A dù chưa đo được; (b) thì tôi nên bỏ nhánh nào không
chứng minh được bằng số, bất kể pro trader nói gì.

> *Trả lời:*
