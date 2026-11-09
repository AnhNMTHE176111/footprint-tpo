# Kết luận: cơ khí hoá setup "follow theo footprint" của CORVEN — dừng trước khi đưa vào indicator

> Fable viết cho người học, 2026-11-09. Số liệu do Opus đo, tôi kiểm lại. Dữ liệu: vàng GCZ26, nến 1 phút, 35 phiên (28/07 → 15/09/2026). 26 phiên còn lại (16/09 → 21/10) **chưa đụng tới** — giữ kín để kiểm tra ngoài mẫu, và theo luật đã đặt trước thì **chưa đủ điều kiện mở**.

## 1. Đã thử gì
Biến checklist 4 bước của anh (Bối cảnh → Mốc → Xác nhận ≥ 2 dấu hiệu → Lệnh) thành luật máy có số, rồi cho máy tự tìm lệnh trên 35 phiên:
- **Range** kẻ tự động bằng Range Box (bản đã đo khớp hộp CORVEN vẽ tay).
- **Hai thế:** A = fail break ở cạnh, đánh về cạnh đối diện; B = phá thật rồi hồi về cạnh / vùng stacked mới, đánh theo hướng phá.
- **5 dấu hiệu** đúng như trang chi tiết: delta to hoặc delta ngược giá · bóng đúng phe · phe ngược kiệt sức ở râu · stacked mới giữa thân · trap. Cần ≥ 2 loại trong 3 nến quanh mốc.
- **Lệnh:** vào ở giá đóng nến xác nhận (thân ≥ 40 %, đóng sát cực trị), SL sau cực trị cú thủng + 3 tick, chỉ vào khi tới mục tiêu được ≥ 1,7R, TP đặt 2R, 1 lệnh một lúc, trừ phí 0,2 giá mỗi lệnh, chạm SL và TP cùng nến thì tính thua.

## 2. Số chính (trên 35 phiên)
| | Số lệnh | Lệnh/ngày | Tỷ lệ thắng | Lãi/lỗ trung bình mỗi lệnh |
|---|---|---|---|---|
| Setup CORVEN cơ khí hoá (bộ gốc) | 97 | 2,8 | 27 % | **−0,29R** (khoảng tin cậy −0,55 … −0,02) |
| Hoà vốn cần | | | 36,5 % | 0 |
| **Đối chứng 1:** vào ở *mọi* nến xác nhận tại mốc, **không cần dấu hiệu nào** | 194 | 5,5 | 29 % | −0,24R |
| **Đối chứng 2:** vào **ngẫu nhiên** cùng phiên, cùng giờ, cùng hướng, cùng cỡ SL/TP | — | — | 34 % | −0,08R |

Đọc thế này: "R" là số tiền rủi ro một lệnh; −0,29R nghĩa là trung bình mỗi lệnh mất 29 % số tiền đặt cược. **Bước "≥ 2 dấu hiệu" không những không cải thiện mà còn kém hơn cả vào bừa tại mốc** (−0,29 so với −0,24 và −0,08).

Đã thử sửa từng thứ một (11 biến thể: nới/siết "gần", đòi stacked 4 mức, bóng gấp 4 lần, delta gấp 3 lần, đệm SL 2 hoặc 5 tick, cửa sổ 2 hoặc 4 nến, bỏ nhóm range đã phá 3 lần, đòi 3 dấu hiệu). **Không biến thể nào hơn được cả hai đối chứng.** Gần nhất: đệm SL 5 tick (−0,15R, bằng đối chứng 1 nhưng vẫn kém đối chứng 2); đòi 3 dấu hiệu (+0,01R, 38 lệnh, nhưng đối chứng ngẫu nhiên của chính nhóm đó là +0,22R — tức là nhóm đó rơi vào lúc thị trường dễ, không phải do dấu hiệu).

Hai giả thuyết đã kiểm và loại:
- *"SL quá sát nên bị quét rồi giá mới chạy đúng hướng"*: đúng ở vài ca nhìn bằng mắt, nhưng đo ra: sau khi dính SL, giá vẫn chạm TP cũ ở 37 % lệnh — mức nền (chọn nến bừa cùng giờ) đã là 31 %. Nới SL gấp 1,5–2 lần cũng không cứu (−0,25 … −0,29R). Đặt SL sau "đáy/đỉnh mới quét" như lời CORVEN thì **tệ hơn** (−0,36R, nhiều lệnh bị loại vì SL xa quá).
- *"Delta to phải so với nhịp vừa rồi"*: các lệnh có delta nhỏ hơn nhịp trước lại đỡ lỗ hơn (−0,18 so với −0,36). Không có cơ sở.

## 3. Vì sao dừng ở đây
Trước khi chạy, tôi đã viết sẵn luật: chỉ được chỉnh ≤ 3 vòng trên 35 phiên đầu; chỉ khi có một bộ tham số **hơn cả hai đối chứng** mới được mở 26 phiên giữ kín ra kiểm. Không bộ nào đạt. Nếu bây giờ nới luật ("thôi lấy bộ đỡ tệ nhất rồi mở TEST xem sao") thì kết quả trên 26 phiên kia không còn giá trị kiểm chứng — đó đúng là lỗi đã mắc ở 4 setup A/B/C/D cũ (mọi ô đẹp trên nửa đầu đều đổi dấu ở nửa sau).

Ý nghĩa thật của kết quả: **phần "nhìn chart" của CORVEN mà ta dịch được ra số (range, cạnh, ≥ 2 dấu hiệu order flow, nến xác nhận) chưa mang lợi thế trên nến 1 phút khi trừ phí.** Có thể vì (i) phần quyết định nằm ở chỗ chưa dịch được (ông chọn *range nào* đáng đánh, đọc "bối cảnh" đa khung, bỏ qua hàng chục ca máy vẫn đếm đủ 2 dấu hiệu); (ii) dữ liệu lịch sử không có lệnh đơn lớn và không có delta trong nến, nên "bóng" và "delta thẳng" của ta nghèo hơn cái ông nhìn; (iii) hoặc setup này thật sự không có lợi thế thống kê mà sống bằng kỹ năng chọn lọc của người đánh.

## 4. Phiên Âu — điều đáng chú ý, nhưng CHƯA dùng được
Chia theo phiên (giờ VN: Á 05:00–12:30, Âu 12:30–19:00, Mỹ 19:00–04:00): **phiên Á âm ở cả 12 biến thể, phiên Mỹ âm ở cả 12, phiên Âu ≥ 0 ở 10/12** (bộ gốc: Á −0,60 · Âu +0,14 · Mỹ −0,33, mỗi phiên khoảng 30 lệnh). Phí không giải thích được chênh này.

Phải nói thẳng: đây là **nhìn thấy sau khi đã có kết quả** (hậu kiểm). Với 30 lệnh mỗi phiên, chia 3 nhóm thì gần như luôn có một nhóm dương do may rủi. Nó là **giả thuyết mới**, chưa phải phát hiện. Đáng ghi lại thêm: ví dụ của CORVEN đều ở phiên Mỹ (19:00–01:00 VN) — chính phiên mà máy thua đều.

## 5. Lựa chọn — anh quyết
| | Làm gì | Tốn gì | Được gì |
|---|---|---|---|
| **A. Port vào Benzo, gắn nhãn "chưa có lợi thế", chạy forward test** | Opus port C# (~2–3 ngày việc), thay A/B/C/D, bắn mũi tên + Telegram như cũ | Công port + parity + test; và **rủi ro nhìn mũi tên rồi vào theo** dù số nói là lỗ | Thu số live để đối chiếu; thấy máy đếm dấu hiệu thế nào ngay trên chart |
| **B. Không bắn tín hiệu. Giữ Range Box + Order Flow Bubbles làm công cụ đọc chart, anh tự quyết lệnh** | Không tốn gì thêm; Benzo cũ tắt hết | Không có bot | Không bị một tín hiệu kém hơn vào bừa dẫn dắt; đúng tinh thần CORVEN "đọc bối cảnh mà đánh" |
| **C. Đăng ký trước giả thuyết "phiên Âu" rồi kiểm bằng dữ liệu MỚI** | Anh xuất thêm footprint GCZ26 22/10 → nay và tiếp tục xuất hằng tuần (GCG27 khi đổi hợp đồng) tới khi có ≥ 60 phiên mới; Opus chạy **đúng bộ gốc, chỉ phiên Âu, một lần duy nhất**, không chỉnh gì | Chờ ~2–3 tháng dữ liệu; mỗi tuần một lần xuất file | Nếu Âu vẫn dương trên dữ liệu chưa ai nhìn ⇒ có một luật thật để port; nếu âm ⇒ đóng hẳn câu chuyện, không tiếc |

**Khuyến nghị của tôi: B ngay bây giờ, kết hợp C chạy nền.** Lý do: một bot bắn tín hiệu kém hơn vào bừa thì có hại hơn không có bot (A); còn C rẻ (chỉ xuất file đều) và là cách duy nhất biến "phiên Âu" từ cảm giác thành bằng chứng. Nếu anh vẫn muốn A để quen mắt với cách máy đếm dấu hiệu, tôi sẽ làm, nhưng bảng trên chart phải ghi rõ "lỗ −0,29R/lệnh trong 35 phiên, kém vào ngẫu nhiên" ngay cạnh số lệnh.

Toàn bộ số, bảng, 30 ảnh lệnh và mã đo nằm ở `benzo-trader/research/report/RESULTS-CORVEN.md`, `_sweep_gd2v2.csv`, `corven_gd1_shots/`, `corven_gd2v1_shots/`. Luật đo đặt trước ở `plans/BENZO-CORVEN-plan.md` mục 3 và 7.4.
