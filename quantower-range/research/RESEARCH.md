# Hồ sơ RANGE của CORVEN — bằng chứng để viết indicator "range theo cụm nến"

> Lập 2026-11-08 (agent nghiên cứu, chỉ đọc + đo). Dữ liệu đo nằm ở [corven_boxes.csv](corven_boxes.csv).
> Nguồn chính: buổi Meet 2026-11-07 ([transcript.md](../../corven-meet/2026-11-07/transcript.md),
> [transcript-raw/](../../corven-meet/2026-11-07/transcript-raw/), [frames/](../../corven-meet/2026-11-07/frames/))
> và video gốc `D:\record_video\bandicam *.mp4`. Tôi trích lại khung hình 1920×1080 từ video (ảnh
> trong `frames/` chỉ 1600×900), cứ 5 giây một khung cho các đoạn 0:00–0:20, 0:20–0:30, 0:30–1:10, rồi
> dò nét hồng (magenta) bằng máy để tìm mọi hộp CORVEN vẽ.
>
> ⚠️ Đây là **lời giảng và nét vẽ tay**, chưa phải luật đã kiểm chứng. Mọi con số ở mục 2–3 là **đo trên
> ảnh**, sai số ±2 tick (GC tick 0,1; 1 điểm = 10 tick) trừ khi ghi khác.

## 0. Tóm tắt 10 dòng

1. Tìm được **20 hộp range GC M1** do CORVEN vẽ (B01–B19 + B1) trên 2 phiên 2026-11-05/06, cộng **6 hộp NQ** và 3 hộp nhỏ
   đánh dấu. Ảnh chọn sẵn chỉ chứa 5 hộp; 15 hộp còn lại tìm thêm trong video.
2. Chiều cao: trung vị **45 tick** (25–94). Bề rộng hộp vẽ: trung vị **28 nến**; phần "lõi" (từ nến đầu tới trước nến phá)
   trung vị **20 nến**, ngắn nhất **8 nến**.
3. Chiều cao ≈ **2,5 lần biên độ nến M1 trung bình** bên trong hộp (trung vị; 1,6–5,9).
4. **Cạnh hộp KHÔNG đặt ở râu cực trị.** Ở 19/20 hộp có râu xuyên qua cạnh: trung vị 4–5 tick trên cạnh trên, 10 tick dưới
   cạnh dưới. Cạnh nằm ở **cụm đỉnh/đáy lặp lại** (hoặc đỉnh/đáy của thân nến).
5. **Mép trái** thường là chính **cây nến của nhịp vừa chạy vào vùng** (cây tăng/giảm mạnh), không phải sau N nến đi ngang.
6. **Mép phải** thường kéo **quá nến phá 3–9 nến** (có hộp quá 15–22 nến), một hộp được kéo dài 41 nến để làm "range dưới"
   (mục tiêu).
7. Range kết thúc bằng **nến đóng ngoài cạnh**; nhưng có **5 ca nến đóng ngoài rồi quay lại trong 2–4 nến** (fail break) —
   đúng chỗ CORVEN chỉ để đánh ngược ("fail break… đóng ngược lại vào range → sell").
8. Giờ trên chart Sierra của CORVEN = **giờ Việt Nam (UTC+7)**, trùng giờ Optimus Flow của người học. File data xuất là UTC ⇒
   trừ 7 giờ. **Data hiện có KHÔNG phủ 2026-11-05/06** (file mới nhất kết thúc 2026-10-21).
9. Range cũ (box 8 nến; state machine FORM=30 nến, rộng 2–6 giá) đã FAIL/KILL; theo số đo này, sàn 30 nến loại 16/20 hộp
   của CORVEN và trần 6 giá loại 4/20.
10. CORVEN **chưa** nói: cần mấy lần chạm, range tối thiểu mấy nến, phá bao nhiêu tick mới tính — xem mục 6.

---

## 1. Trích nguyên văn mọi câu CORVEN nói về range

Quy ước: `[h:mm:ss]` = giờ trong buổi Meet 11/7 (0:00 = 14:31:28 VN). "soát" = bản `transcript.md`; "máy" = bản
`transcript-raw/partNN.txt` (chỉ dẫn khi câu không có trong bản soát hoặc khác nghĩa). `[?]` = máy nghe không rõ.
Không phân biệt được giọng; câu có **HV:** là người học hỏi. Chữ trong `[...]` là tôi chèn để đọc được, không phải lời nói.

### (a) Range là gì / hình thành thế nào
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:12:56 | "Một vùng tích lũy đi ngang thôi là nó là range rồi." | máy: "Một cái vùng tích mỹ xay quay thôi là nó là rain rồi" |
| 0:13:01 (máy) | "Nó sẽ xay quay như thế này" | [?] "xay quay" ≈ đi ngang/sideway |
| 0:09:32 | "Có những range xấu, có những range đẹp thì dễ đánh như range này" | lúc chỉ hộp NQ N1 |
| 0:08:05 (máy) | "nó tạo ra cái tailing range này nha, xong rồi… nó break xuống" | [?] "tailing" có thể là "trading range" |
| 0:38:59 | "đoạn này đi kênh, đi range như thế này, chờ chờ xem nó phản ứng thế nào" | |
| 0:45:30 (máy) | "Nó lại đấu giá ở dưới này, không tiếp." | |
| 0:49:00 | "Mới bắt đầu nhìn thì phải nhìn được chỗ quan trọng — những chỗ thấy giá đi ngang / phản ứng." | nói về "mốc quan trọng", không nói thẳng "range" |
| 1:08:01 | "[range rất to] mà xuống phản ứng… đi chặn mấy lần" | máy: "Mà xuống phản trình... Đi chặn mấy lần" |
| chat 13.6 (Aug) | "Trong balance thì chop" / "Trong balance thì xác định range rồi 2 cạnh mà vả thôi" | [TRANSCRIPT.md](../../data-export/messages-with-pro-trader/TRANSCRIPT.md) §13.6 |
| chat §1 (Jan 21) | "big nó thường kê limit ở range để đỡ trượt giá" / "đa phần là thế" | TRANSCRIPT §1 |

### (b) Cạnh range đặt ở đâu
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:14:50 | "Cái cạnh range: chỗ nào nó phản ứng nhiều thì lấy làm cạnh." | máy: "Cả cái cạnh đúng chứ, cả cái cạnh chỗ nào nó phản ứng nhiều ấy" |
| 0:15:07–0:15:10 (máy) | "kéo sang bên, kéo sang bên phải" / "Kéo xuống một tí nữa" | đang hướng dẫn người học kéo hộp trên Optimus Flow (0:13–0:16) |
| 0:24:11–0:24:24 | "trên này đi range, thì thường người ta đặt SL trên đỉnh này một tí… quanh cạnh range bên trên một tí" | cạnh range = nơi có SL nằm ngay ngoài |
| 1:04:25–1:04:29 | "Đây cho đây range, range cho đây stop hunt — thấy mấy cái râu nhú nhú xuống không?" | chỉ hộp B02: râu thủng đáy hộp nhưng hộp vẫn vẽ ở trên các râu đó |
| chat §9 (Apr 13) | "Biên của chú to thế =)) Mà thôi. Vậy cũng đúng" (học viên: TR "tầm 15 giá"); "Thế thường TR chú bao nhiêu" | CORVEN không nói con số TR của mình |

### (c) Khung thời gian
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:13:54 (máy) | "Lâng khung lên" | ≈ "nâng khung lên" |
| 0:13:58–0:14:12 | "Range thì chắc phải khung 15 … Range dùng khung 15 thôi. M1 thì không dùng đâu, M1 dùng range nhỏ hơn." | máy nghe "khung 1 năm" ×3; "15" là suy theo ngữ cảnh 0:47:51/1:07:49 |
| 0:17:20 | "Dùng khung nào thì tìm cấu trúc của khung đấy thôi." | |
| 0:47:51–0:48:02 | "Nếu thấy rối quá thì phải lên khung 15 — vì nó rõ ràng hơn." | máy: "1-5 thật", "1-1, 1-5" |
| 0:48:07–0:48:18 | "Như đây là range nhỏ… Đây, đây là cái range nhỏ, thấy hông? Đến cái này vẫn chỉ tính là range thôi nhé." | lúc màn hình có B10 + B11 |
| 1:07:49–1:08:07 | "Đoạn này chắc phải dùng range 15 — range rất to… Range to đủ vào đây" | lúc màn hình có B01 (hộp này vẫn vẽ trên chart M1) |
| 1:08:40–1:08:52 | "Thường [dùng] range [lớn] nhưng trong đó có đấu giá của M1 … vẫn dùng range của M1" | máy: "Thường phúc ring nhưng trong đó có đấu giá của M1" — [?] |
| 1:08:57–1:09:01 (máy) | "Nếu dùng 2 nodes chỉ dùng để đánh dài thôi / Đánh không lớn ấy" | [?] bản soát hiểu là "dùng 2 range lồng nhau thì range lớn chỉ để đánh dài" |
| chat §9 (Apr 13) | "Tìm biên m1 xong et m1 luôn cũng đc chú" | vào lệnh M1 trên biên M1 |
| chat 13.7 | "Day scap nhìn tpo daily" | balance theo TPO ngày (không phải range M1) |

### (d) Gộp range chồng nhau
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:14:42–0:14:44 | "2 vùng đấy nó chồng nhau rồi gộp lại" / "gộp lại 1 vùng" | đang nói về range trên Optimus Flow của người học |
| 0:45:02–0:45:25 | "Đoạn này đi hơi xấu… nó range chồng range thì nó khó" | màn hình: B13 (03:14–03:45) và B14 (03:29–03:59) chung cạnh 4114.0 |
| 1:11:49–1:18:49 | "chồng nhau thì gộp lại một" / "Nếu nhiều vùng gần nhau quá thì chọn vùng lớn nhất" / "chồng nhau quá thì chọn vùng dưới cùng [?]" | nói về **HVN** trên volume profile, không phải range M1 |

### (e) Phá range / fail break / râu vs đóng nến
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:07:57 | "Vẽ range như thế này, xem nó breakout như thế nào, hay fail break như thế nào." | |
| 0:08:05–0:08:09 | "Đoạn này nó tạo ra range, xong break xuống. Nó không có dấu hiệu gì, đâm ngược lại vào → vẫn ở trong range." | |
| 0:08:16–0:08:19 | "Đoạn này nó lên, break ngược lên trên. Chưa vội buy luôn, vì chỗ này chưa có dấu hiệu gì." | |
| 0:08:29–0:08:37 | "Trap đỉnh ở đây, xong đẩy ngược vào lòng range, mà đẩy ngược vào range lại tạo ra stacked imbalance sell → tìm tín hiệu sell. Khi nó fail break thì tìm tín hiệu sell." | |
| 0:08:56 | "cẩn thận thì chờ 1–2 cây sau xem nó có giữ được trong range không" | máy: "hold được trong cái rain này" |
| 0:09:42–0:09:48 | "fail break đâm ngược vào, bóng xanh nổ, trap, sell, stop hunt, đẩy ngược vào → buy được" | hộp NQ N1 |
| 0:11:23–0:11:30 (máy) | "đoạn này nó cũng tạo ra range đấy / Thì xác định range lấy luôn / Xác định range này / Break range xuống, break phá range này" | |
| 0:12:39 | "đoạn này break range, buy chưa mạnh nhất, đoạn này mới confirm được buy, xong retest về, đáy bị kiệt sức, buy lên" | |
| 0:20:31–0:20:45 | "bối cảnh với range. Trap phá range đâm xuống, retest lên range, retest luôn cái stacked imbalance này → sell" | màn hình: B19 |
| 0:23:09–0:23:13 (máy) | "Đâm xuống, loại này phá range này / Loại này ở giữa range này / Loại phá range tạo stacked imbalance" | màn hình: B18 |
| 0:39:16–0:39:19 | "Mấy cái này không có trong [range] nữa thì bỏ — vì break range rồi" | |
| 0:40:04–0:40:16 | "nó tạo ra range và break range. Range ở dưới… nếu nó phá range này thì nó sẽ về range dưới này" | màn hình: B1 phá xuống; "range dưới" = B12 |
| 0:40:22–0:40:28 | **HV:** "phá vỡ cấu trúc của range hay của…?" — "Vừa phá vỡ cấu trúc, vừa phá vỡ range." | |
| 0:43:53–0:43:58 | "Nó phá thì phải giữ được ở [vùng] dưới thì mới tính. Phá mà rút râu luôn thì khả năng là fail." | nói về phá cấu trúc |
| 0:50:25 | "Nhiều lúc nó quét râu lên, không đóng nến lên nhưng vẫn quét râu." | lý do không đặt SL sát |
| 0:56:54–0:57:05 | "Lên đây yếu, fail break range… delta giảm dần, xong đóng ngược lại vào range → sell, SL trên đỉnh yếu này" | màn hình: B06 (fail lên 21:19–21:22, quay lại 21:23) |
| 1:03:48–1:04:23 | **HV:** "Phá thì cần râu phá một chút, hay phải cả thân nến phá?" — "Thân nến chứ — phải nến đóng cửa chứ. Dùng nến đóng cửa hết… Không dùng râu nến đâu, râu nến không quan trọng." | màn hình: B03 |
| 0:54:13 | "Quét qua là được rồi, không cần [đóng nến]" | ⚠️ về **vô hiệu kiệt sức**, KHÔNG phải phá range |
| chat §10 (May 5) | "Đc chú nhưng đừng đánh UT sớm" / "Sang D chú mới đánh thì đc" / "Đánh break thôi chú" / "SL 5 giá ổn đấy" | "đánh break" theo người học chốt (CAU_HOI C1, **lời người học, không phải CORVEN**): break ra khỏi vùng, chờ hồi + tín hiệu |

### (f) Dùng range để đánh
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:07:47–0:07:54 | "đánh thì kết hợp thêm range mà đánh, đừng đánh mỗi cái đấy. Kết hợp thêm bối cảnh, vẽ range mà đánh." | |
| 0:16:25 (máy) | "Cần range chỉ là xác nhận thôi" | bản soát: "Cần range, chỉ là [xác nhận] thôi" |
| 0:16:29–0:16:35 | "khi có dấu hiệu range → phải chờ đánh theo range; còn khi nó trend thì mới đánh theo trend" | |
| 0:16:19 (máy) | "vàng là hơi nhiều gray, vàng hơi..." | [?] có thể là "vàng hay đi range nhiều" — không chắc |
| 0:38:57–0:39:05 | "Đoạn này range mà đánh… Có dấu hiệu range thì kẻ range mà đánh." | |
| 0:46:48 | "Thấy cái range này không?" | màn hình: B14 + B12 kéo dài |
| 0:55:14 | "Đoạn range thì chỉ cần quét qua râu thôi là có người mua lại rồi, đánh lên được." | nói trong bối cảnh kiệt sức |
| 0:56:28–0:56:49 | "Không phải lúc nào cũng đánh theo cấu trúc. Đoạn này có thể đánh range, hoặc đánh bình thường cũng được, vì biên độ dao động cũng to… Đánh range thì đánh ở đây — đọc bối cảnh vào là đánh." | |
| 0:58:35–0:58:53 | "xác định từ chỗ vào đến [cạnh] range này 1,7R — sấp sỉ 2R rồi thì có thể… TP vẫn cứ đặt 2R" | cạnh đối diện của range = mốc tính R:R (B06) |
| 0:59:03 | "Đoạn này kẻ range rồi mà đánh." | màn hình: B05 |
| 0:59:16 (máy) | "Ranger, sửa tốt hơn nha" | [?] |
| 0:59:37–1:00:02 | **HV:** "Cây K23 sao không vào?" — "Vì nó vẫn ở ngoài range, mà tín hiệu mới có mỗi một cái." / **HV:** "Điều kiện là phải vào lòng range à?" — "Ừ, phải vào lòng range nữa." | B05 sau cú thủng đáy 20:30–20:34 |
| 1:00:09–1:00:27 | "chưa vào lòng range nhưng nó confirm lại lần 2 rồi — trap đáy một lần nữa và bị kiệt sức đáy → vào được" | |
| chat 13.6 | "Trong balance thì xác định range rồi 2 cạnh mà vả thôi" / "Thì cứ tăng mà delta âm là yếu" | |
| chat §10 | "Mà mẹ k cần nhãn nhiếc đâu / Xác định range thôi là đc / Rồi nhìn phân tích vol trong range là đc" | |
| video CROWCONCEP (file ghi cùng pro trader) | "Khi giá sideway biên rộng, cần chờ một nhịp phát lực break rõ ràng thì mới follow." / "nếu giá có dấu hiệu sideway biên hẹp thì DMA phải > 0 nếu muốn buy và < 0 nếu muốn sell" | [CROWCONCEP_DFT.md](../../data-export/messages-with-pro-trader/CROWCONCEP_DFT.md) — đã backtest ÂM |

### (g) Khi nào range hết hiệu lực
| Mốc | Nguyên văn | Ghi chú |
|---|---|---|
| 0:39:16–0:39:19 | "Mấy cái này không có trong [range] nữa thì bỏ — vì break range rồi" | |
| 0:40:12 | "nếu nó phá range này thì nó sẽ về range dưới này" | range cũ (B12) **vẫn dùng làm mục tiêu** sau 20+ nến |
| chat 13.5 | "Test lại balance hôm qua" | balance cũ vẫn là nơi giá quay lại test |
| 1:11:00–1:11:24 | "Nếu giá đang nằm trong 1 vùng này thì vùng này vẫn chưa có giá trị… Khi giá đi ra rồi thì vùng này mới bắt đầu có giá trị" | nói về **HVN**, không phải range M1 |

Không tìm thấy câu CORVEN nào về range trong `video-notes/` (chỉ có `orderflow_guide_v2.html/pdf`, không có chữ
"range" gắn với CORVEN) và `tpo/` (chỉ trích lại các câu chat 13.6/13.7 ở trên). Các câu "VA mà move khỏi range thì
chỉ có 2 mục đích: BREAK hoặc REJECT" trong `tpo/SYLLABUS-TPO.md` Buổi 7 lấy từ note `TPO.pdf`, **không ghi rõ là của CORVEN**.

---

## 2. Thống kê các hộp đã đo

Cách đo (chi tiết từng hộp trong CSV):
- Lấy khung 1920×1080 từ video; nội suy pixel→giá từ ≥2 nhãn trục giá (độ phân giải 1,7–3,9 pixel/tick tùy mức zoom),
  pixel→giờ từ nhãn con trỏ (crosshair) + khoảng cách nến đo bằng máy (13,4–21,9 pixel/nến).
- Cạnh hộp: dò nét magenta bằng máy (tâm nét, sai số ±1 pixel ≈ ±0,5 tick ở zoom lớn, ±1 tick ở zoom nhỏ).
- **Lõi** = từ nến thứ 2 của hộp tới nến trước nến phá cuối cùng (loại nến mép trái vì thường là cây chạy vào vùng, và
  loại phần hộp kéo quá điểm phá). `max_high_in_box`/`min_low_in_box` trong CSV là của **lõi** (có tính râu cú fail break).
- Râu/biên độ nến: máy dò nét đen theo cột nến, rồi tôi soát bằng mắt trên ảnh phóng to và sửa các chỗ bong bóng
  (bubble) che râu. `touches_*` = số nến lõi có râu cách cạnh ≤2 tick **hoặc** xuyên qua cạnh (đếm máy, ước lượng ±1–2).

Bảng 20 hộp GC M1 (B01–B19, B1):

| Chỉ số | min | p25 | trung vị | p75 | max |
|---|---|---|---|---|---|
| Chiều cao (tick) | 25 | 36 | **45** | 57 | 94 |
| Bề rộng hộp vẽ (nến) | 17 | 25 | **28,5** | 33 | 73 |
| Bề rộng lõi (nến) | 8 | 16 | **20,5** | 27 | 54 |
| Biên độ nến M1 TB trong lõi (tick) | 10,8 | 14 | **17,6** | 21 | 37,9 |
| Chiều cao / biên độ nến TB | 1,6 | 2,2 | **2,5** | 3,05 | 5,9 |
| Râu cao nhất − cạnh trên (tick) | 0 | 3 | **4,5** | 8 | 22 |
| Cạnh dưới − râu thấp nhất (tick) | 5 | 7 | **10** | 15 | 31 |
| Số nến chạm/xuyên cạnh trên | 0 | 3 | **4** | 5 | 9 |
| Số nến chạm/xuyên cạnh dưới | 1 | 3 | **5,5** | 6 | 11 |

- Hai giá trị lớn nhất của "râu vượt" là râu của **cú fail break** (B06 +22, B07 −31, B03 −22). Bỏ các cú đó, râu vượt
  cạnh trên trung vị ~4 tick, dưới ~9 tick.
- Hộp to bất thường (≥83 tick): B01 (85, CORVEN gọi "range 15"), B07 (83, biên độ nến TB 38 tick — giờ Mỹ),
  B16 (90, nến TB 33 tick), B11 (94, hộp to chồng lên B10). Tính theo **tỷ lệ với biên độ nến** thì B07/B16 vẫn bình
  thường (2,2/2,7); chỉ B01 (5,9) và B11 (5,6) là "range lớn" thật.
- Hộp NQ N1: 42,6 điểm, nến TB ~18 điểm ⇒ tỷ lệ 2,3 — cùng thang với GC.

---

## 3. Nhận xét ĐO ĐƯỢC

**3.1 Cạnh đặt ở đâu so với râu cực trị.**
- 19/20 hộp có ít nhất một râu vượt cạnh trên hoặc dưới ≥3 tick. Chỉ B17 có cạnh trên trùng râu cao nhất (0 tick);
  B07 cạnh trên trùng râu cao nhất trước cú 22:50.
- Ví dụ đo tay từng nến B1 ([0-40-40.jpg](../../corven-meet/2026-11-07/frames/0-40-40.jpg)): cạnh trên 4127.3, các đỉnh
  02:48 4127.6 · 02:49 4127.15 · 02:52 4127.4 · 02:53 4127.6 ⇒ cạnh nằm **giữa cụm 4 đỉnh**, không ở đỉnh cao nhất. Cạnh dưới
  4123.1: đáy 02:46 4123.1, bốn nến 02:45/02:49/02:58/02:59 ở ~4123.3 ⇒ cạnh ở **cụm đáy lặp lại**; ba râu 02:55–02:57
  thủng 6–16 tick không làm CORVEN hạ cạnh.
- B19: cạnh trên 4081.9 ≈ **đỉnh thân** của cụm nến 18:32–18:34, râu cùng cụm lên 4082.3–4082.7.
- B02 (lúc nói "râu nhú nhú xuống" 1:04:25): đáy hộp 4132.1, râu 16:54–17:30 xuống 4131.2–4131.7 (4–9 tick) — hộp
  vẽ ở **trên** các râu đó.
- ⇒ Đo được: cạnh ≈ vùng nhiều nến cùng chạm (đúng câu 0:14:50 "chỗ nào phản ứng nhiều"), râu đơn lẻ bị bỏ ra ngoài.

**3.2 Nến đầu tiên của hộp.**
- 11/20 hộp: mép trái nằm **đúng cây nến chạy vào vùng** (cây tăng/giảm dài kết thúc nhịp trước): B1, B12, B13, B08, B19
  (cây tăng), B03, B02, B06 (cây giảm), B11 (cây phá của B10), B14 (cây đầu nhịp phá B13), B01 (cây tạo đỉnh 4140.4).
- 4/20: mép trái là **nến ngay sau** cây chạy vào (B07, B15, B17, B10).
- 5/20 không xác định được (B04, B05, B09, B16, B18).
- ⇒ CORVEN **không** đợi N nến đi ngang rồi mới tính điểm bắt đầu; hộp bắt đầu từ điểm kết thúc nhịp trước.

**3.3 Hộp kéo tới đâu bên phải.**
- Đúng nến phá: B1, B01 (2/20). B12 ban đầu cũng vậy, sau đó được **kéo thêm 41 nến** (giữa 0:39:10 và 0:42:25) đúng lúc
  CORVEN nói "nếu phá range này thì nó về range dưới này" — và giá thực sự quay về vùng đó lúc 03:30–03:51.
- Quá nến phá 3–9 nến: 12/20. Quá 15–22 nến: B13, B17, B02, B18. B11 để mở.
- ⇒ Mép phải không phải một luật cứng; nó cho thấy hộp vẫn được giữ trên chart sau khi phá (để thấy cú retest).

**3.4 Cách range kết thúc.**
- Mọi hộp có phá đều kết thúc bằng **nến đóng ngoài cạnh** (5–45 tick). Phá lên 6, phá xuống 13 (B11 chưa phá).
- **Fail break có nến đóng ngoài** (rồi quay vào trong 2–4 nến): B03 (18:50 −8t → vào lại 18:53), B06 (21:19 +7t →
  21:23), B07 (22:46 −8t → 22:48), B05 (20:31 −10t → 20:35, sau đó phá chiều ngược lại), NQ N1 (20:11–20:13 → 20:14, rồi phá lên).
  ⇒ 5 ca. Riêng B06 và B05 là chỗ CORVEN chỉ để vào lệnh (0:56:54, 0:59:37–1:00:27).
- **Retest sau phá** thấy rõ ở 10/19 ca: râu quay lại chạm hoặc chui vào hộp 0–11 tick trong 2–9 nến (B04, B09, B13, B14,
  B15, B16, B17, B19, B02, B1→B12).
- Quãng đi sau phá (theo chiều cao hộp, nhiều ca bị khung ảnh cắt nên chỉ ghi "≥"): từ ≥0,6h tới 4,1h; phần lớn ≥0,9h.

**3.5 Quan hệ giữa các hộp (chuỗi).**
- B12 → B1 (lên) → B13 → B14 (xuống, **B13 và B14 chung cạnh 4114.0/4114.1**, chồng thời gian 03:29–03:45) → về lại
  B12 kéo dài. B04 → B05 nối bậc thang. B10 và B11 chồng thời gian 01:01–01:08.
- Đáy B09 (4127.3, 11-06 00:03) trùng cạnh trên B1 (4127.3, 02:44) — chỉ ghi nhận, chưa biết có chủ ý không.
- 3 hộp nhỏ (S1–S3, 6–10 tick, 2–6 nến) là **đánh dấu** (vùng retest / râu quét), không phải range.

**3.6 Hộp nào vẽ ngay trong buổi.** Thấy được nét đang hiện dần: B19 (0:20:20–0:20:35), B18 (~0:22:25), các hộp NQ
N2–N6 (0:11:25–0:12:50), B11 (0:48:15–0:48:35), S2 (~1:01:00), và việc kéo dài B12. Các hộp còn lại xuất hiện khi
CORVEN cuộn chart ⇒ **có thể đã vẽ từ trước buổi** (không chứng minh được).

---

## 4. Múi giờ và khả năng khớp với data

| Kiểm tra | Kết quả |
|---|---|
| Đồng hồ trên thanh tiêu đề Sierra | 08:12:28 khi Meet là 15:12 VN ⇒ đồng hồ này là UTC |
| Giờ của **nến** trên Sierra | **UTC+7 (giờ VN)** — 3 bằng chứng: (1) NQ có cây nổ volume lúc **20:30** ngày 11-06 = 08:30 ET, giờ ra tin Mỹ (dự đoán là bảng việc làm tháng 10 — chưa đối chiếu lịch); (2) nếu là UTC thì B07 (22:30–22:56) rơi vào giờ CME đóng cửa bảo trì và NQ có nến 23:06 tối thứ Sáu sau giờ đóng tuần — không thể; (3) Optimus Flow của người học (0:13:58, [0-13-58.jpg](../../corven-meet/2026-11-07/frames/0-13-58.jpg)) hiện giờ VN, đỉnh ~6:35 PM ≈ 4082.7, trùng đỉnh B19 18:32–18:33 4082.7 trên Sierra |
| Giá Sierra vs Optimus Flow (GCZ26) | trùng nhau ở vùng 18:2x–18:5x (không lệch giá) |
| Múi giờ file `data-export/data-footprint/*_bars.csv` | UTC ([data-export/README.md](../../data-export/README.md) mục "Múi giờ") ⇒ **giờ hộp − 7h** = giờ trong file; giờ nghỉ CME mùa đông là 22:00–23:00 UTC = 05:00–06:00 VN |
| Data có phủ 2026-11-05/06 không? | **KHÔNG.** File mới nhất `fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv` kết thúc 2026-10-21 13:44; đã quét đuôi mọi CSV trong `data-export/`, không có ngày 2026-11. Muốn đối chiếu số đo với data phải xuất thêm GCZ26 M1 từ ~2026-11-05 00:00 VN tới 2026-11-07 |

Đổi giờ các hộp sang UTC (để tra file khi có): 11-05 13:48 VN = 11-05 06:48 UTC … 11-06 18:58 VN = 11-06 11:58 UTC.

---

## 5. Range cũ đã thử và vì sao FAIL

Nguồn: [WyckoffRunner.cs](../../quantower-entry-signal/WyckoffRunner.cs) (đầu file), [README.md](../../quantower-entry-signal/README.md),
[SPEC_V7_3KB.md](../../quantower-entry-signal/SPEC_V7_3KB.md) §4.3, `research/wyckoff/RESULTS_KB3.md`, `RESULTS_KB12.md`, `AUDIT_V7.md`,
[WYCKOFF_RULES.md](../../data-export/wyckoff/WYCKOFF_RULES.md), [CHART_CASES.md](../../data-export/wyckoff/CHART_CASES.md).

1. **Box trượt 8 nến (KB1 CBR, đang dùng):** range = cực trị `RangeLen=8` nến trước nến phá, span 3,0–7,5 giá
   (`RangeMinPts/RangeMaxPts`); phá = nến đóng vượt cạnh + VSA ≥2,0 + thân mạnh. Đây là nhánh duy nhất "PASS có điều kiện",
   nhưng **không có điểm OOS nào** (OOS 2025-11→2026-04 chỉ 171 nến qua cổng thanh khoản).
2. **Range theo cấu trúc v7 (`range_struct.py`, RangeMode=1):** state machine FORMING→VALID→BREAKING→DEAD; FORM ≥30 nến,
   ≥2 lần chạm mỗi biên cách nhau ≥3 nến, dung sai chạm max(0,3 giá; 15% bề rộng), rộng 2,0–6,0 giá, tuổi ≤120 nến,
   biên mở rộng bằng **râu**, phá = close vượt biên + 0,2; quay lại trong ≤2 nến = phá hụt. Kết quả: 74 range VALID
   (5–7/2026), lệch 77% so với cách quét cửa sổ (322) vì máy trạng thái reset mỗi khi giá đóng vượt biên lúc đang FORMING;
   cắm vào KB1 cho **n=0 tín hiệu** ⇒ không PASS.
3. **KB3 scalp biên↔biên trong range = KILL:** nhóm "chưa vỡ thuận hướng" EV −0,254R; chết ở 2 tick phí (EV −0,036R);
   **0 range VALID trong 6 tháng OOS** (lý do chính là data mỏng/cổng thanh khoản, không hẳn do định nghĩa range).
   Bộ lọc thanh khoản loại gần hết mẫu vì range vốn là vùng ít thanh khoản.
4. **Sơ đồ Wyckoff tự động:** 10 agent giảng viên chấm 49 range, điểm trung vị 3/10 (cạnh đặt sai vì neo climax, Phase C
   quá dài…). Người học chốt khi đó: không sàn độ dài tối thiểu, chỉ M1, không sàn khối lượng tuyệt đối.
5. **So với số đo CORVEN ở trên (tôi đối chiếu, không phải kết luận backtest):** sàn FORM=30 nến loại 16/20 hộp
   (lõi trung vị 20,5 nến); trần 6,0 giá loại 4/20 (B01, B07, B16, B11); box 8 nến ngắn hơn hẳn mọi hộp CORVEN (ngắn nhất
   17 nến vẽ / 8 nến lõi); và việc **mở rộng biên bằng râu** đi ngược quan sát 3.1 (CORVEN để râu đơn lẻ nằm ngoài cạnh).

---

## 6. Câu hỏi mở (transcript không trả lời)

1. **Mấy lần chạm mỗi cạnh** thì thành range? (Đo được: trung vị 4 nến chạm/xuyên cạnh trên, 5,5 cạnh dưới, nhưng có
   hộp chỉ 1 nến chạm một cạnh — B09 dưới, B16 trên, B17 trên.)
2. **Tối thiểu bao nhiêu nến?** (Lõi ngắn nhất đo được 8 nến — B17; CORVEN không nói con số.)
3. **Chiều cao tối thiểu / tối đa**, theo tick hay theo biên độ nến? ("Biên của chú to thế" với TR 15 giá — CORVEN
   không cho con số của mình.)
4. Cạnh lấy theo **râu lặp lại** hay **thân nến**? Bao nhiêu râu thủng cạnh thì phải dời cạnh?
5. Phá range: nến đóng ngoài cạnh **bao nhiêu tick** mới tính? Một nến hay cần nến thứ 2 giữ ngoài? (Có 5 ca đóng
   ngoài rồi quay vào trong 2–4 nến.)
6. "Chờ 1–2 cây xem có giữ được trong range" (0:08:56) và "phải vào lòng range" (1:00:02): "vào lòng" là **đóng nến**
   trong cạnh hay chỉ chạm? Sâu bao nhiêu?
7. Range "khung 15" vẽ trên M1 (B01, có thể B11): xác định từ chart M15 thật hay chỉ là "range to" trên M1? Khi nào
   dùng range lớn, khi nào range M1 ("thường range lớn nhưng trong đó đấu giá M1 vẫn dùng range M1" — câu máy nghe không rõ)?
8. **Gộp range chồng nhau** (0:14:42) áp dụng thế nào khi hai hộp chỉ chung cạnh (B13/B14) hay chồng một phần (B10/B11)?
   Gộp thành hộp bao ngoài, hay giữ cả hai?
9. Range cũ **hết hiệu lực khi nào**? B12 vẫn được dùng làm "range dưới" sau khi bị phá 40+ nến; câu 0:39:16 lại nói
   "không có trong range nữa thì bỏ".
10. "Range xấu" (0:09:32, 0:45:02) khác "range đẹp" ở điểm nào đo được (độ chồng, số chạm, độ dốc)?
11. Mép trái có quy tắc không, hay chỉ là "bắt đầu từ cây chạy vào vùng" như quan sát 3.2?
12. Câu 0:13:08 (máy) "Cái rain này đáng cốt, … xem có auto hay không" — có phải người học hỏi CORVEN về việc
    code range tự động? Nếu đúng, CORVEN trả lời gì (đoạn sau bị máy bỏ trống)?

---

## Phụ lục — vị trí ảnh của từng hộp
Ảnh chọn sẵn: [0-09-42](../../corven-meet/2026-11-07/frames/0-09-42.jpg) (N1) · [0-40-40](../../corven-meet/2026-11-07/frames/0-40-40.jpg)
và [0-41-55](../../corven-meet/2026-11-07/frames/0-41-55.jpg) (B1, cạnh trên B13) · [0-46-05](../../corven-meet/2026-11-07/frames/0-46-05.jpg)
(B14 + B12 kéo dài) · [0-58-35](../../corven-meet/2026-11-07/frames/0-58-35.jpg) (B06) · [0-59-50](../../corven-meet/2026-11-07/frames/0-59-50.jpg)
(B05) · [1-04-00](../../corven-meet/2026-11-07/frames/1-04-00.jpg) (B03).
Các hộp còn lại lấy từ video: cột `meet_time` trong CSV là đoạn giờ Meet có hộp trên màn hình; cột `frame` ghi
`mH-MM-SS (pN_xxxx)` = khung 5 giây thứ xxxx của video part N (giờ trong part = (xxxx−1)×5 giây). Tôi không soát
riêng kho `D:\record_video\_extract\frames\` (cắt theo đổi cảnh) mà quét thẳng video 5 giây/khung cho 0:00–1:10, bao trùm
mọi đoạn nói về range được giao. Đoạn 1:10–1:21 (HVN/TPO) chưa quét.
