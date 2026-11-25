# PLAN — định nghĩa lại Big Trade thành "lệnh cá mập" (một thuật toán, không ô chọn mật độ)

> Fable viết 2026-11-25. Opus đo theo mục 6; Fable review rồi viết `SPEC.md`.
> Đây là **định nghĩa hiển thị**, không phải lợi thế giao dịch đã kiểm định. Không bước nào dùng giá chạy sau. Không lấy chart CORVEN làm đích (chỉ in ra để tham khảo).
> Căn cứ từ internet: `RESEARCH.md`. Số xem nhanh: `out_bw0_profile.txt`, `out_bw0_quick.txt`, `out_bw0_quick2.txt`.

## 1. Vì sao hiện nay sai

- Người học: "big trade là phải thật sự lớn, mới thể hiện có cá mập lao vào; như thế này là quá dày và quá nhiễu" và "không tạo mode dày thưa nữa, đo luôn con số hợp lý, thuật toán áp theo, không chia mode".
- Chế độ "Không theo CORVEN": vòng nổ khi lệnh đơn lớn hơn 1% lớn nhất của 240 phút gần nhất. Trung vị lệnh đơn là 1, mức 1% chỉ khoảng 9, nên ngưỡng ra 6–10 trên vàng M1 và 5–10 trên NQ M1: **232 vòng mỗi ngày trên vàng M1, 698 vòng mỗi ngày trên NQ M1** (`out_bw0_quick.txt`, chưa gộp vòng sát nhau).
- Chế độ "Theo CORVEN": mật độ đích 1 vòng mỗi nến, sàn 5. Cũng không phải "cá mập".
- Hai lỗi gốc của cách cũ:
  1. **Mức hiếm tính theo phần trăm số ô.** Số ô mỗi ngày là hàng chục nghìn, nên 1% vẫn là hàng trăm ô. Và phần trăm số ô đổi theo khung (mức 1% ở M1 là 9, ở M15 là 16–22) dù các lệnh lớn nhất ở hai khung là **cùng một lệnh**.
  2. **Cửa sổ 240 phút.** Lệnh cá mập hiếm tới mức 4 giờ thường không có cái nào để so.

## 2. Số xem nhanh làm căn cứ (chưa phải kết quả đo)

- Nhật ký hiện có: vàng `_GC_XCEC` M1 và M5 (31/8–23/9, 16 ngày đủ), vàng `_GCZ26` M1 (9–24/11, ghi ngắt quãng, 449–939 nến mỗi ngày), M5, M15, M30 (ngắn); NQ `_NQZ26` M1 và M15 (26/10–2/11 đủ 6 ngày, thêm 24/11 nửa ngày, 3/11 và 25/11 là mẩu), M5 (4 nến, bỏ).
- Lệnh lớn nhất mỗi ngày: vàng 50–500, NQ 91–581. Rất nhiều lệnh tròn số (100, 99, 200).
- Thử luật "lớn hơn lệnh lớn thứ 10 × 5 trong 5 ngày nến gần nhất" (chưa gộp): vàng M1 ngưỡng giữa 47 (33–50), 8,7 vòng mỗi ngày; NQ M1 ngưỡng giữa 71 (63–78), 13 vòng mỗi ngày. **NQ M15 ra đúng ngưỡng 71 và 12,9 vòng mỗi ngày như M1**; vàng M5 ra 46 so với 47 ở M1. Xếp hạng theo thời gian gần như không đổi theo khung.
- Cùng luật đó: lệnh lớn nhất mỗi ngày đủ được nổ 100% trên vàng; lệnh lớn nhất **của từng phiên** chỉ được nổ 84% trên vàng, 57% phiên Á và 50% phiên Âu trên NQ. Đây là điểm phải quyết: cá mập theo nghĩa tuyệt đối hay so với giờ đó.
- Có ngày cá mập đánh dồn (vàng 20/11: 8 lệnh ≥ 100, trong đó 7 lệnh 130–352 dồn vào 02:00–02:30 UTC; NQ 30/10: 11 lệnh ≥ 100). Ngày như vậy được phép có nhiều vòng; ngày yên được phép không có vòng nào.

## 3. Các định nghĩa ứng viên

Quy ước chung cho mọi ứng viên:
- **Giá trị xét:** lệnh đơn lớn nhất của ô (`mot`), số nguyên, > 0.
- **Chỉ dùng nến đã đóng trước** để tính ngưỡng; nến đang xét không tự góp vào ngưỡng của nó.
- **Nổ khi lớn hơn hẳn ngưỡng** (`mot > ngưỡng`), để các lệnh tròn số bằng nhau không làm vượt ngân sách.
- **"Số phút nến có số liệu"** của một tập nến = số nến có ít nhất một ô `mot > 0` × phút một nến `m`. Một "ngày nến" = 1.380 phút (23 giờ). Tính theo số nến có số liệu, không theo lịch, để nhật ký ngắt quãng không làm lệch.
- **Hạng theo thời gian:** `K = max(1, rhu(R × số phút nến của tập tham chiếu / 1380))`, `rhu(x) = Floor(x + 0,5)`; ngưỡng = giá trị lớn thứ K của tập tham chiếu. `R` = số lệnh mỗi ngày nến mà tập tham chiếu cho phép vượt.
- **Gộp vòng sát nhau** giữ như hiện nay: `g = max(2, rhu(biên độ trung bình N nến / 8))`, chọn tham lam lệnh lớn trước. Không giới hạn số vòng mỗi nến, không sàn nhập tay.
- **Mảng đếm 4096 ô** cộng vào / trừ ra như `StatBigTrade`; giá trị > 4095 dồn vào ô cuối, so sánh dùng giá trị thật.

| Mã | Định nghĩa | Công thức ngưỡng của một nến | Tham số đo | Xử lý khung M1…H1 | Xử lý phiên Á / Âu / Mỹ | Chi phí C# |
|---|---|---|---|---|---|---|
| **A. Hạng nhiều ngày** | Cá mập = lệnh thuộc nhóm R lệnh lớn nhất mỗi ngày, tính trên D ngày nến gần nhất, mọi phiên gộp chung | Tập tham chiếu = `rhu(D × 1380 / m)` nến có số liệu gần nhất; ngưỡng = lớn thứ K | D ∈ {3, 5, 10}; R ∈ {3, 4, 6, 8, 10, 15, 20} | Không cần chỉnh: hạng theo thời gian không đổi theo khung (đã thấy ở mục 2) | Một ngưỡng cho cả ngày: phiên vắng có ít hoặc không có vòng | Hàng đợi D ngày nến + mảng đếm; M1 D=10 là 13.800 nến × vài chục số. Mỗi nến quét 4096 ô |
| **B. Hạng theo khung giờ** | Cá mập = lệnh lớn bất thường **so với cùng giờ** các ngày trước | Khung 30 phút theo giờ Chicago (`StatClock`); tập tham chiếu = khung đó và hai khung liền kề của D ngày giao dịch trước; ngưỡng = lớn thứ K với cùng công thức hạng theo thời gian; chưa đủ 2 ngày thì dùng A | D ∈ {5, 10}; R ∈ {4, 6, 10, 15} | Như A | Ngân sách chia đều theo giờ: phiên Á cũng có khoảng R × (số giờ / 23) vòng | Như `StatDots`: mỗi khung giữ D + 1 mảng đếm; ngưỡng tính một lần mỗi (ngày, khung) |
| **C. Bội số lệnh lớn thường gặp** | Cá mập = lệnh lớn gấp `k` lần "lệnh lớn thường gặp" | `L` = lệnh lớn thứ (1 lệnh mỗi `q` phút) của D ngày nến gần nhất, tức `K_L = rhu(số phút nến / q)`; ngưỡng = `rhu(k × L)` | q ∈ {5, 15, 30}; k ∈ {2, 3, 4, 5}; D = 5. Kèm một biến thể **cố ý sai** để so: `k × mức 1% số ô của 240 phút`, k ∈ {3, 5, 8} | `L` tính theo thời gian nên không đổi theo khung; biến thể phần trăm số ô thì đổi | `L` đổi chậm; một ngưỡng cả ngày | Như A |
| **D. Ngoại suy đuôi (lý thuyết cực trị)** | Coi đuôi là lũy thừa; ngưỡng = mức mà theo đường đuôi khớp được, mỗi ngày chỉ có R lệnh vượt | Lấy `k0` lệnh lớn nhất của D ngày nến; số mũ Hill `α = k0 / Σ ln(x_i / x_k0)`; ngưỡng = `x_k0 × (k0 / K)^(1/α)` với K như A | k0 ∈ {100, 200}; R ∈ {6, 10}; D = 5 | Như A | Như A | Thêm một lần duyệt k0 lệnh mỗi nến; phải giữ danh sách lệnh lớn đã sắp xếp. Đắt và khó giải thích nhất |
| **E. Sàn tuyệt đối theo mã** | Cá mập = lệnh ≥ một con số cố định của mã | Hằng số | vàng và NQ: {20, 25, 30, 40, 50, 75, 100, 150} | Không đổi | Không đổi | Gần như bằng 0. **Nhược điểm biết trước:** MGC, MNQ và mã khác không có số; phải tự bảo trì |
| **F. Chuẩn hóa theo volume thị trường** | Cá mập = một lệnh ăn hết một phần đáng kể volume một phút lúc đó | `V` = trung vị volume mỗi phút của các nến trong `T` phút nến gần nhất (volume nến = tổng buy + sell các ô trong nhật ký, chia `m`); ngưỡng = `rhu(f × V)` | T ∈ {120, 240}; `f` hiệu chỉnh trên đoạn chọn để ra 6, 10, 15 vòng mỗi ngày rồi **giữ nguyên** trên đoạn kiểm | Volume mỗi phút không đổi theo khung | Tự co theo phiên: phiên vắng ngưỡng thấp | Rẻ. **Nhược điểm biết trước:** phiên vắng ngưỡng tụt về mức lệnh thường, đúng cái người học chê |
| **G. Kỷ lục trượt** | Cá mập = lệnh phá (hoặc gần phá) kỷ lục của `T` phút gần nhất | Ngưỡng = lệnh lớn thứ `K` của `T` phút nến gần nhất, K cố định | T ∈ {240, 480, 1380}; K ∈ {1, 2, 3} | Không đổi theo khung | Sau một lệnh khổng lồ thì im lặng tới khi nó ra khỏi cửa sổ | Như A, cửa sổ ngắn |
| **H. Ghép A với B** (chỉ đo nếu vòng 1 cho thấy cần) | Nổ khi vượt ngưỡng A, **hoặc** vượt ngưỡng B và đồng thời ≥ `c` × ngưỡng A | — | c ∈ {0,5; 0,67} với cặp (A, B) tốt nhất | Như A | Bắt được cá mập phiên vắng mà không cho lệnh thường lọt | A + B |

**Phỏng đoán của Fable trước khi đo** (ghi lại để đối chiếu, không phải kết luận): A với D = 5 và R trong khoảng 6–10 sẽ đạt; B sẽ dày lên ở phiên Á bằng lệnh 20–30 (không phải cá mập); C phụ thuộc mạnh vào `q`; D không hơn A mà phức tạp hơn; E không dùng được cho mã chưa đo; F rớt ở phiên vắng; G không ổn định.

## 4. Tiêu chí (viết trước khi đo)

Mọi tiêu chí tính **sau khi gộp vòng sát nhau**, trên **ngày đủ** (ngày giao dịch theo 17:00 Chicago có ≥ 85% số phút nến của một ngày: ≥ 1.170 phút nến), bỏ khoảng khởi động của từng ứng viên. Không tiêu chí nào dùng giá sau đó.

| Mã | Tiêu chí | Cách tính | Mức đạt |
|---|---|---|---|
| **T1** | **Hiếm, nhìn là biết** | Số vòng mỗi ngày đủ | Trung vị **4–12** vòng mỗi ngày; không ngày nào quá **40**; mỗi phiên (Á / Âu / Mỹ) trung vị ≤ 6. Lý do: 4–12 vòng trên 23 giờ là khoảng 2–6 giờ một vòng; màn hình M1 (2–3 giờ) thấy 0–2 vòng, màn hình M15 (2 ngày) thấy 10–25 vòng. Ngày cá mập đánh dồn được phép vọt lên, nên chặn trên là 40 chứ không phải 12 |
| **T2** | **Lớn hơn hẳn lệnh thường cùng lúc** | Tỉ số = cỡ vòng / mức 1% lớn nhất của lệnh đơn (tính trên ô M1) cùng khung giờ 30 phút của 5 ngày trước | Vòng nhỏ nhất ≥ **3 lần**; trung vị ≥ **5 lần**. Với vàng thêm một mốc đối chiếu: vòng nhỏ nhất ≥ 25 (ngưỡng block của CME, `RESEARCH.md`) — chỉ in ra, không dùng để loại |
| **T3** | **Ổn định** | (a) Hệ số biến thiên của ngưỡng giữa các ngày; (b) số vòng mỗi ngày của đoạn kiểm so với đoạn chọn; (c) cùng một nhật ký, cùng những ngày, hai khung khác nhau (vàng M1 so M5; NQ M1 so M15): tỉ lệ vòng trùng nhau (cùng giá, cùng cỡ, giờ nằm trong nến khung lớn) | (a) ≤ 30%; (b) lệch ≤ 40%; (c) ≥ 85% |
| **T4** | **Không sót cá mập thật** | (a) Lệnh lớn nhất của mỗi ngày đủ có nổ; (b) ba lệnh lớn nhất mỗi ngày đủ có nổ; (c) lệnh lớn nhất của mỗi phiên có nổ, **chỉ tính phiên mà lệnh lớn nhất ≥ 5 lần mức 1% của phiên đó** | (a) **100%**; (b) ≥ 85%; (c) ≥ 80%, và in riêng từng phiên |
| **T5** | **Ca biên** | (a) Chart mới mở, nhật ký trống: sau bao nhiêu phút nến thì có ngưỡng, và trong ngày nến đầu tiên số vòng có vượt 2 lần mức ổn định không; (b) nhật ký ngắt quãng (`_GCZ26` M1 và M5); (c) ngày vắng (23–24/11 trên vàng); (d) ngày dồn (vàng 20/11, NQ 30/10); (e) đổi hợp đồng: nối `_GC_XCEC` (tháng 9) với `_GCZ26` (tháng 11) thành một chuỗi | (a) trong ngày nến đầu không có vòng nào < 3 lần mức 1% của chính ngày đó; (b), (c) không có vòng < 20 hợp đồng trên vàng và NQ; (d) số vòng ≤ 40; (e) ngưỡng sau chỗ nối lệch ≤ 30% so với tính riêng |
| **T6** | **Đơn giản** (để phân xử khi hòa) | Số tham số; có giải thích được bằng một câu trên tooltip không; có phải bảo trì hằng số theo mã không | Ít tham số hơn thắng; cần hằng số theo mã thì chỉ thắng khi mọi ứng viên tự co đều rớt |

**Chia đoạn chọn / kiểm theo ngày** (chọn tham số chỉ trên đoạn chọn, rồi khóa):
- Vàng `_GC_XCEC` M1 và M5: chọn = 1–11/9 (9 ngày đủ), kiểm = 14–23/9 (7 ngày đủ + 23/9 chưa đủ).
- NQ `_NQZ26` M1 và M15: chọn = 26–28/10 (3 ngày), kiểm = 29/10, 30/10, 2/11 (3 ngày) + 24/11 (nửa ngày, chỉ dùng cho ca biên). **Chỉ 6 ngày đủ: mọi kết luận về NQ phải ghi rõ số ngày.**
- Vàng `_GCZ26` (tháng 11): không dùng để chọn; dùng làm đoạn kiểm ngoài mẫu và ca biên.
- Khoảng khởi động D ngày nến ăn vào đoạn chọn: với D = 5 trên NQ chỉ còn 1 ngày có ngưỡng đầy đủ. Vì thế phải đo thêm chế độ **cửa sổ lớn dần** (đủ `W_min` phút nến là có ngưỡng, K co theo số phút nến đã có) với `W_min` ∈ {240, 690, 1380}, và báo riêng số vòng của những ngày ngưỡng chưa đủ D ngày.

**Luật chọn:** ứng viên đạt cả T1–T5 trên đoạn kiểm của **cả vàng và NQ với cùng một bộ tham số** thì vào vòng chốt; nhiều ứng viên đạt thì T6 phân xử. Không ứng viên nào đạt hết thì báo đúng tiêu chí nào rớt, Fable quyết ở vòng 2 (ứng viên H hoặc nới tiêu chí có ghi lý do). Không được chỉnh tham số theo đoạn kiểm.

## 5. Một thuật toán cho cả hai chế độ ngưỡng

- Big Trade tách khỏi "Chế độ ngưỡng": khối Big Trade trong `ComputeBar` gọi **một lớp mới duy nhất** ở cả hai chế độ, không còn nhánh `_statBt` / `_btAdapt`. Ô "Chế độ ngưỡng" từ nay chỉ điều khiển chấm Bid/Ask (đổi tên ô cho khớp).
- **Ô gỡ khỏi Settings** (dự kiến, chốt ở `SPEC.md`): "Big Trade · Ngưỡng tự thích nghi", "Big Trade · Mật độ đích", "Big Trade · Sàn", "Big Trade · Tối đa vòng mỗi nến". **Giữ:** "Big Trade (lệnh đơn) · Bật". Không thêm ô nào.
- **Giữ nguyên chấm Bid/Ask ở cả hai chế độ:** lớp mới chỉ đọc lệnh đơn và chỉ sinh vòng Big Trade. Kiểm bằng cách chạy `Golden.dll stophunt` trước và sau trên cùng dữ liệu, cả hai chế độ, rồi so file dấu **sau khi bỏ dòng Big Trade**: phải trùng từng byte. `Golden.dll golden` chỉ được đổi ở các dòng Big Trade; `inccheck` phải giống hệt.
- Dấu vân tay: đổi phần Big Trade (nhãn phiên bản mới) ở cả hai chế độ; phần còn lại không đổi.
- Stop hunt và các tín hiệu khác đang đọc vòng Big Trade: liệt kê trong `SPEC.md` chỗ nào bị ảnh hưởng khi số vòng giảm mạnh.
- Tooltip một câu, ví dụ với ứng viên A: `Big trade: 1 lệnh 86 hợp đồng (ngưỡng > 47: nhóm 10 lệnh lớn nhất mỗi ngày, tính trên 5 ngày gần nhất)`.

## 6. Việc đo vòng 1 (Opus)

Thư mục: `quantower-orderflow-indicator/research/bigtrade_whale_2026-11-25/`. Python, `PYTHONIOENCODING=utf-8`. Đầu vào duy nhất: `C:\Users\anhla\AppData\Roaming\OrderFlowBubbles\bigtrade-log\*.csv` (đọc thẳng, không dùng bản `btlog_*.csv` cũ trong thư mục tạm). Không sửa file C#.

### 6.1 `bw1_common.py`
- `load(tên file)`: bỏ dòng trùng `(time_ticks, price)` giữ dòng cuối; giờ UTC từ `time_iso`; giờ Chicago theo đúng luật của `StatClock` (xem `research/stat_anomaly_2026-11-24/SPEC.md` mục 1.5); ngày giao dịch; khung 30 phút; phiên (Á = 17:00–02:00, Âu = 02:00–08:30, Mỹ = 08:30–17:00 giờ Chicago); tick = `rhu(price / cỡ tick)` (vàng 0,1; NQ 0,25).
- `bars(d)`: danh sách nến theo thời gian, mỗi nến = (giờ, mảng tick, mảng mot, volume = tổng buy + sell).
- `gop(nến, ngưỡng, g)`: chọn tham lam y như `BigTradeAdaptive.Select(..., strict: true)`; `g` tính y như `StatBigTrade.MergeTicks` (đọc `StatThreshold.cs`).
- Bảng "ngày đủ" theo định nghĩa mục 4.
- Mỗi ứng viên là một lớp có `nguong(nến)` (chỉ đọc trạng thái từ nến đã đóng) và `nop(nến)`; một vòng lặp chung gọi `nguong` rồi `nop`.

### 6.2 `bw1_selftest.py` → `out_bw1_selftest.txt`
- Hàm hạng: 1.380 phút nến, R = 10 → K = 10; 690 phút → K = 5; 60 phút → K = 1 (không bao giờ 0).
- Lớn hơn hẳn: tập tham chiếu có 12 lệnh cỡ 100 và K = 10 → ngưỡng 100, lệnh 100 không nổ, lệnh 101 nổ.
- **Không nhìn trước:** với mỗi ứng viên, chạy trên một nhật ký, rồi xáo toàn bộ dữ liệu sau nến thứ `i`; mọi vòng trước và tại nến `i` phải giữ nguyên.
- Ứng viên A cấu hình (D = 5, R = 10) phải ra đúng các dòng `('rank', 5, 10)` trong `out_bw0_quick.txt` khi tắt gộp và dùng điều kiện khởi động 1 ngày nến.

### 6.3 `bw1_profile.py` → `out_bw1_profile.txt`, `out_bw1_tail.csv`
Với từng nhật ký và từng phiên: số ngày đủ; phân vị 50 / 90 / 99 / 99,9 / 99,99; số ô có lệnh đơn ≥ 10 / 20 / 30 / 50 / 100 / 200 **mỗi ngày đủ** (nhỏ nhất, trung vị, lớn nhất); lệnh lớn thứ 1, 3, 5, 10, 20, 50 của mỗi ngày đủ; số mũ Hill với k0 = 100, 200, 500 của từng đoạn 5 ngày; tỉ lệ lệnh tròn số (25, 50, 100, 200) trong nhóm ≥ 25; bảng theo giờ Chicago (24 dòng): mức 1%, lệnh lớn nhất trung vị, số lệnh ≥ 50. Thêm bảng so khung: 50 lệnh lớn nhất của vàng M1 có mặt trong M5 không, và NQ M1 trong M15 (cùng giá, cùng cỡ, giờ nằm trong nến).

### 6.4 `bw1_rules.py` → `out_bw1_grid.csv` và các file dấu `marks_<mã>_<cấu hình>_<nhật ký>.csv` (ghi vào thư mục tạm, không commit)
Chạy mọi cấu hình ở bảng mục 3 (A, B, C kèm biến thể cố ý sai, D, E, F, G; **chưa chạy H**) trên: vàng `_GC_XCEC` M1 và M5, NQ `_NQZ26` M1 và M15, vàng `_GCZ26` M1. Mỗi cấu hình chạy hai chế độ khởi động: "đủ D ngày nến mới có ngưỡng" và "cửa sổ lớn dần" với `W_min` ∈ {240, 690, 1380}. Kèm hai mốc so sánh: luật hiện tại của chế độ thống kê (1% của 240 phút) và, nếu dựng lại được không tốn công, luật `BigTradeAdaptive` mặc định.
Cột của `out_bw1_grid.csv`: nhật ký, khung, mã ứng viên, tham số, chế độ khởi động, đoạn (chọn / kiểm / ngoài mẫu), số ngày đủ, vòng mỗi ngày (nhỏ nhất, trung vị, lớn nhất), vòng mỗi phiên (trung vị Á / Âu / Mỹ), số ngày không có vòng, ngưỡng (phân vị 10 / 50 / 90), hệ số biến thiên ngưỡng giữa các ngày, cỡ vòng nhỏ nhất, cỡ vòng trung vị.

### 6.5 `bw1_score.py` → `out_bw1_score.csv`, `out_bw1_pick.txt`
Tính T1–T4 theo đúng mục 4 cho từng dòng của lưới; cột đạt / rớt từng tiêu chí; T3(c) so cặp khung. `out_bw1_pick.txt`: các cấu hình đạt T1–T4 trên đoạn chọn của cả vàng và NQ, kèm số của chúng trên đoạn kiểm và ngoài mẫu; nếu không có cấu hình nào đạt hết thì in 10 cấu hình rớt ít tiêu chí nhất và rớt ở đâu.

### 6.6 `bw1_edge.py` → `out_bw1_edge.txt`
Chỉ cho các cấu hình vào `out_bw1_pick.txt` (tối đa 6): từng ca T5(a)–(e) với số cụ thể; danh sách đầy đủ các vòng của vàng 20/11 và NQ 30/10; danh sách vòng của vàng 23–24/11; thời điểm có ngưỡng đầu tiên trên từng nhật ký.

### 6.7 `R1-KET-QUA.md` (Opus viết, tiếng Việt có dấu)
1. Số ngày đủ của từng nhật ký (đếm lại NQ).
2. Bảng hồ sơ đuôi rút gọn và câu trả lời: đuôi có điểm gãy rõ không (số mũ Hill có ổn định theo k0 không).
3. Mỗi ứng viên một bảng: cấu hình tốt nhất trên đoạn chọn, số trên đoạn kiểm, đạt / rớt T1–T5.
4. Bảng "trước và sau" cho 2–3 cấu hình tốt nhất: số vòng mỗi ngày và mỗi phiên, ngưỡng cụ thể ở phiên Á / Âu / Mỹ, so với luật hiện tại.
5. Những gì không đo được hoặc đo trên quá ít ngày, nói thẳng.
Opus **không chốt**; chỉ báo số và nêu chỗ nghi ngờ. Không viết câu nào ngụ ý vòng Big Trade dự báo được giá.

### 6.8 Giới hạn
- Không dùng giá sau vòng, không dùng chart CORVEN để chọn.
- Không commit, không push, không chép DLL.
- `.gitignore` của thư mục đã có `*.pkl`, `__pycache__/`; file đầu ra > 5MB thì ghi vào thư mục tạm.

## 7. Sau vòng 1

Fable review `R1-KET-QUA.md`: kiểm lại 2–3 con số bằng script riêng, quyết có cần vòng 2 (ứng viên H, hoặc đo thêm khi nhật ký NQ dài hơn), rồi viết `SPEC.md` gồm: công thức chốt với tham số cố định, bản Python tham chiếu từng nến, danh sách ô gỡ, ca biên, ví dụ cho unit test, cách kiểm C# = Python từng dấu.
