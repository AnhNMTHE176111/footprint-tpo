# Range Box — brainstorm luật (Fable, 2026-11-08)

> Mục tiêu: indicator Quantower/Optimus Flow **tự kẻ RANGE theo cụm nến** đúng cách CORVEN kẻ tay,
> chạy trên khung nào thì dùng nến khung đó (M1, M5, M15…). Đây là **công cụ BỐI CẢNH**, không phải
> máy bắn tín hiệu — CORVEN 0:16:25: *"Cần range, chỉ là [xác nhận] thôi."*
> Nguồn: `corven-meet/2026-11-07/transcript.md` + ảnh `frames/`. Hồ sơ đo đạc chi tiết do agent
> nghiên cứu viết ở `research/RESEARCH.md` + `research/corven_boxes.csv`.

## 1. CORVEN nói gì (trích, kèm mốc giờ)
| # | Mốc | Lời | Rút ra luật |
|---|---|---|---|
| 1 | 0:12:56 | "Một vùng tích lũy đi ngang thôi là nó là range rồi." | Range = **cụm nến đi ngang**, không cần mẫu hình đặc biệt. |
| 2 | 0:14:50 | "Cái cạnh range: chỗ nào nó phản ứng nhiều thì lấy làm cạnh." | Cạnh = **mức giá có nhiều lần chạm/quay đầu**, **không phải** râu cực trị. |
| 3 | 0:14:42 | "2 vùng chồng nhau thì gộp lại 1 vùng." | Hai range chồng giá → **gộp**. |
| 4 | 0:13:58, 0:47:51, 1:07:44, 1:08:40 | Range dùng khung 15; M1 dùng range nhỏ hơn; trong range lớn vẫn có range M1. | **Mỗi khung có range của khung đó**. Indicator chạy theo nến của chart đang mở; muốn range to thì mở M15. |
| 5 | 1:04:00 | "Thân nến chứ — phải nến đóng cửa. Không dùng râu nến." | **Phá range = nến ĐÓNG ngoài cạnh.** Râu ra ngoài không tính là phá. |
| 6 | 1:04:25 | "Range cho đây stop hunt — thấy mấy cái râu nhú nhú xuống không?" | Râu nhô ra ngoài cạnh = **stop hunt** (quét SL), là chuyện bình thường của range. |
| 7 | 0:08:05, 0:56:49 | Break xuống không có dấu hiệu gì, đâm ngược lại vào → vẫn trong range. Fail break: đóng ngược lại vào range → sell. | **Fail break = ra ngoài rồi ĐÓNG trở lại trong range.** Đây là chỗ tìm tín hiệu. |
| 8 | 0:08:46 | "Chờ 1–2 cây sau xem nó có giữ được trong range không." | Sau khi đóng ngoài, **chờ 1–2 nến** mới kết luận phá thật hay fail. |
| 9 | 0:43:53 | "Nó phá thì phải giữ được ở dưới thì mới tính. Phá mà rút râu luôn thì khả năng là fail." | Phá thật = **giữ được** ngoài range; nến phá mà rút râu dài → nghi fail. |
| 10 | 0:39:16, 0:40:00 | Break range rồi thì mấy cái trong range bỏ; phá range này thì về range dưới. | Range đã phá → **thôi dùng làm cạnh**, nhưng còn là **mốc tham chiếu** (giá hay về range kế). |
| 11 | 0:59:37–1:00:09 | Cây ngoài range không vào; phải vào lòng range, hoặc confirm lần 2. | Tín hiệu chỉ có giá trị **khi giá ở trong range** (hoặc quay lại lần 2). |
| 12 | 0:16:29 | Có dấu hiệu range → chờ đánh theo range; trend thì đánh theo trend. | Indicator phải nói rõ **đang có range hay không** — trend thì không vẽ. |
| 13 | 0:42:23 | "Chỉ cần một cái nến thôi." (cấu trúc) | Đỉnh/đáy cấu trúc = **pivot 1 nến** (3 nến), không cần fractal rộng. |
| 14 | 0:45:02 | "Range chồng range thì khó." | Range lồng/chồng là ca khó → không cố "giải", chỉ vẽ cả hai. |
| 15 | tin nhắn cũ | "Trong balance thì xác định range rồi 2 cạnh mà vả thôi." | Cách dùng: **đánh 2 cạnh** khi đang trong range. |

## 2. Hộp CORVEN vẽ tay (đọc từ ảnh, sai số ±2 tick — số chính xác ở `research/corven_boxes.csv`)
| Ảnh | Khoảng giờ | Rộng (nến) | Cao | Râu nhô ngoài cạnh | Kết thúc |
|---|---|---|---|---|---|
| 0-40-40 / 0-41-55 | 06/11 02:43–02:59 | ~16 | ~4123,2–4127,5 (43 tick) | dưới ~5 tick | đóng dưới 02:59 → rơi 4 điểm |
| 0-46-05 | 06/11 03:29–03:58 | ~30 | ~4108,5–4114,3 (58 tick) | có | đóng dưới 03:58 → rơi 3 điểm |
| 0-58-35 | 05/11 21:04–21:26 | ~22 | ~4131,5–4136 (45 tick) | dưới ~10 tick (nến −69), trên ~15 tick | đóng dưới → rơi 12 điểm |
| 0-59-50 | 05/11 20:19–20:37 | ~18 | ~4123–4126,5 (35 tick) | dưới ~20 tick (3–4 nến) rồi quay vào → lên 8 điểm | fail break đáy (confirm lần 2) |
| 1-04-00 | 05/11 18:27–18:54 | ~27 | ~4143–4146,5 (35 tick) | trên ~7, dưới ~5 | đóng dưới 18:55 → hồi test cạnh dưới → rơi 9 điểm |

Điều **đo được, không suy diễn**: (a) cao 35–60 tick ≈ **4–6 lần biên độ nến M1**; rộng **16–30 nến**;
(b) cạnh KHÔNG đặt ở râu cực trị — râu nhô ngoài 5–20 tick ở cả hai phía; (c) hộp bắt đầu ngay nến
đầu tiên chạm cạnh sau một nhịp đẩy, và kéo sang phải tới nến đóng ngoài cạnh.

## 3. Ba cách tìm range — chọn cách nào
| Cách | Ý tưởng | Ưu | Nhược |
|---|---|---|---|
| A. Cửa sổ cố định | N nến gần nhất, (max−min) ≤ k×ATR | dễ | cạnh = cực trị (sai luật #2); không biết range bắt đầu đâu; **đã thử trong WyckoffRunner KB3 → 0 range hợp lệ, EV −0,04R** |
| B. Hồi quy/độ dốc | độ dốc ≈ 0 + biên độ nhỏ | lọc trend tốt | vẫn không có cạnh "phản ứng nhiều" |
| **C. Cụm pivot (chọn)** | gom các đỉnh pivot gần nhau thành cạnh trên, các đáy pivot gần nhau thành cạnh dưới; cần ≥2 lần chạm mỗi cạnh | đúng luật #2, #13; tự có mốc bắt đầu; râu nhô ngoài tự thành stop hunt | nhiều tham số hơn → **phải đo bằng dữ liệu** |

Chọn **C**, thêm bộ lọc kiểu B (tỷ lệ nến đóng trong lòng range) để không vẽ range lên đoạn trend.
Lý do bác A/B: hai cách đó lấy cạnh = cực trị, trái thẳng luật #2 và đã đo là không ra range dùng được.

## 4. Đặc tả thuật toán (máy trạng thái, logic THUẦN — tách file `RangeLogic.cs`, test được không cần Quantower)
Đơn vị chuẩn hoá: **mbr** = median biên độ (high−low) của 100 nến gần nhất trên khung đang xem → mọi
ngưỡng tính theo mbr để cùng code chạy đúng M1/M5/M15 và GC/MGC. Tick lấy từ symbol.

1. **Pivot 1 nến** (luật #13): đỉnh pivot khi `high[i] > high[i−1]` và `high[i] ≥ high[i+1]` (xác nhận trễ 1 nến); đáy ngược lại.
2. **Cụm cạnh**: một cạnh là tập pivot cùng phía có giá nằm trong ±`tol` quanh **median** của tập. `tol` mặc định = max(2 tick, 0,8×mbr). Pivot nhô ngoài cụm quá `tol` **không** vào cụm (đó là râu stop hunt), cạnh không bị kéo theo.
3. **Range ứng viên** = 1 cụm đỉnh + 1 cụm đáy, mỗi cụm **≥ 2 pivot** cách nhau ≥ 2 nến, đan xen theo thời gian (đỉnh–đáy–đỉnh hoặc đáy–đỉnh–đáy); `top` = median cụm đỉnh, `bottom` = median cụm đáy.
4. **Điều kiện hợp lệ**: `height = top − bottom` trong [`Hmin`, `Hmax`] (mặc định 2,5×mbr … 8×mbr — **đo rồi chốt**); span từ pivot đầu tới nến hiện tại ≥ `MinBars` (mặc định 10); ≥ `InsideRatio` (0,85) số nến trong span **đóng** trong [bottom−tol, top+tol]; không có nến nào trong span đóng ngoài cạnh quá `tol` (nếu có → span bắt đầu sau nến đó).
5. **Nến bắt đầu** = nến pivot sớm nhất thuộc 2 cụm. Hộp kéo sang phải tới nến hiện tại khi còn hiệu lực.
6. **Cập nhật cạnh**: pivot mới trong ±tol của cạnh → thêm vào cụm, cạnh = median mới; cạnh không được dịch quá `tol` so với giá trị lúc range được công bố (tránh hộp "trôi").
7. **Sự kiện trong lúc hiệu lực** (chỉ xét nến đã đóng):
   - **Râu quét** (stop hunt): high > top (hoặc low < bottom) ≥ 1 tick nhưng **đóng trong** lòng range.
   - **Đóng ngoài**: close > top hoặc close < bottom → range sang trạng thái **chờ xác nhận** (luật #8), đếm `K` nến.
   - **Fail break**: trong `K` nến (mặc định 2) có nến **đóng trở lại** trong lòng → phát sự kiện FailBreak(phía), range **tiếp tục hiệu lực**.
   - **Phá thật**: hết `K` nến mà chưa đóng lại trong lòng → BreakConfirmed(phía) tại nến đóng ngoài đầu tiên; range **ngừng** (hộp kết thúc ở nến đó).
   - **Quay lại muộn** (ca 0-59-50): range đã phá nhưng trong `G` nến (mặc định 30) có nến đóng lại trong lòng → ReEntry(phía) và range **sống lại** (vẫn hộp cũ, nối tiếp). CORVEN coi ca này là "confirm lần 2".
8. **Gộp** (luật #3): range mới có `top/bottom` nằm trong ±tol của range đang hiệu lực → cùng range, nối dài; chồng giá ≥ 50 % chiều cao range nhỏ hơn → gộp thành hợp (union) nếu hợp vẫn ≤ Hmax, không thì giữ riêng (luật #14).
9. **Tính tất định**: chạy một mạch toàn bộ lịch sử và chạy từng nến live phải cho **cùng kết quả** (Quantower gọi lại từ đầu khi đổi Settings).

## 5. Đo bằng dữ liệu trước khi code C# (Python mẫu trước, port sau, đối chiếu 1:1)
Dữ liệu: `data-export/data-footprint/fp_GCZ26_XCEC_Time_20260723-20261021_90d_bars.csv` (86 k nến M1,
chính) + `fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv` (kiểm chéo; ⚠️ mã liên tục nối thô, bước
nhảy giả +61,2 điểm 2026-07-29 20:59→22:00 — bỏ mọi cửa sổ vắt qua). Múi giờ xem `data-export/README.md`.
Thử thêm trên nến gộp M5/M15 (resample từ M1) để chắc ngưỡng theo mbr dùng chung được.

Số cần đo (chia đôi 90 ngày để chống khớp quá tay; tham số phải giữ được ở cả 2 nửa + file 748 ngày):
1. Số range/ngày; phân bố chiều cao (tick) và bề rộng (nến). **Mục tiêu**: trung vị rơi vào vùng CORVEN
   vẽ (35–60 tick, 16–30 nến trên M1) — không ép, chỉ so.
2. Tần suất râu quét / fail break / phá thật mỗi range.
3. **Sau fail break ở cạnh E**: xác suất giá chạm cạnh đối diện trước khi phá thật cạnh E; R sẵn có =
   (khoảng tới cạnh đối diện) / (khoảng từ giá đóng trở lại tới râu cực trị + 1 tick). Tỷ lệ R ≥ 1,7
   (luật 2R của CORVEN, 0:58:49). **Đây là hàm mục tiêu chính** khi quét tham số.
4. **Sau phá thật**: xác suất giá đi tiếp ≥ 1× chiều cao range trước khi đóng lại trong lòng
   (CORVEN: "phá range này thì về range dưới").
5. Quét: `MinBars` {8,10,12,15}, `Hmin` {2,2.5,3}×mbr, `Hmax` {6,8,10}×mbr, `tol` {0.5,0.8,1.0}×mbr,
   `K` {1,2,3}, `G` {0,15,30}. Chọn bộ **đơn giản nhất** giữ được (3) ở cả hai nửa; ghi bảng kết quả.
6. **Chuẩn vàng**: 5 hộp CORVEN (05–06/11/2026) — dữ liệu hiện có chỉ tới 21/10 ⇒ cần người học xuất
   thêm GCZ26 M1 03→07/11 bằng Footprint Export rồi so IoU hộp máy vs hộp tay. Chưa có thì ghi "chưa so".

⚠️ Trung thực: WyckoffRunner từng đo "scalp biên↔biên trong range" EV âm với định nghĩa range cũ (cửa
sổ cố định). Kết quả đo mục (3) có thể lại xấu — khi đó **vẫn giao indicator** (vì là công cụ bối cảnh
CORVEN yêu cầu) nhưng README phải nói rõ con số, không được viết như đã có lợi thế.

## 6. Giao diện (ít tuỳ chọn — người học không chỉnh số)
- **Settings chỉ 3 ô bật/tắt**: `Hiện range đã phá` (mặc định bật), `Đánh dấu fail break` (bật),
  `Đánh dấu râu quét cạnh` (tắt). Mọi con số/màu là hằng trong code.
- Hộp đang hiệu lực: viền 1 px xanh lơ nhạt, nền alpha ~25/255, kéo tới nến hiện tại.
  Hộp đã phá: chỉ viền xám đứt, kết thúc ở nến phá; cạnh bị phá kẻ thêm nét chấm `G` nến về bên phải
  (mốc tham chiếu, luật #10).
- Fail break: tam giác nhỏ **chỉ vào lòng range** tại nến đóng trở lại (▼ ở cạnh trên = tìm sell, ▲ ở
  cạnh dưới = tìm buy). Râu quét: chấm rỗng nhỏ ở đầu râu. Không chữ trong hộp.
- Tooltip rê chuột, **ngắn**: `Range 4123,2–4127,5 · 16 nến` / `Fail break đỉnh` / `Phá xuống` / `Râu quét đáy`.
  Khung chữ nền đặc + viền màu như Order Flow Bubbles (người học chốt 2026-11-08).
- Không cần Volume Analysis (chỉ OHLC) → không dính lỗi vòng đời `VolumeAnalysisData_Loaded`.

## 7. Kiểm thử (agent tester làm, tôi duyệt)
- Unit test logic thuần (`tests/`): range sạch 2 chạm/cạnh; râu quét không đổi cạnh; fail break K=2;
  phá thật rồi quay lại trong G; đoạn trend không ra range; gộp 2 range chồng; quá thấp/quá cao bị loại;
  nhân giá ×10 (MGC↔GC) ra cùng kết quả; **chạy một mạch = chạy từng nến**.
- Đối chiếu Python ↔ C# trên 90 ngày: danh sách sự kiện (nến, loại, phía, top, bottom) **giống 100 %**,
  file đối chiếu commit vào `research/` (lần trước file đối chiếu kiệt sức bị mất — không lặp lại).
- Kiểm tra DLL bằng phản chiếu (như `quantower-orderflow-indicator/tests-dll`): đúng 3 ô Settings, mặc định đúng.
- **UI**: tách hàm vẽ nhận `Graphics` + bộ đổi toạ độ giả → render kịch bản tổng hợp ra PNG
  (`tests/ui-out/*.png`) để tôi xem bằng mắt: hộp không đè nhau sai, tam giác đúng phía, chữ không tràn mép.
- Build 0 cảnh báo; deploy bằng `~/quantower-libs/qw-deploy.sh`; cmp khớp.

## 7b. CHỐT LẠI sau khi có `research/RESEARCH.md` (20 hộp GC M1 đo từ video — ghi đè mục 4 ở chỗ khác nhau)
Số đo thật khác ước lượng ban đầu của tôi ở mục 2 (tôi chỉ xem 5 hộp, agent đo 20 hộp): chiều cao hộp
chỉ bằng **2,5 lần** biên độ nến trung bình (dải 1,6–5,9), không phải 4–6 lần. Sửa mặc định:
| Tham số | Mục 4 cũ | **Chốt mới** | Căn cứ |
|---|---|---|---|
| `Hmin` / `Hmax` | 2,5 / 8 × mbr | **1,3 / 6 × mbr** (quét {1,1.3,1.6} / {5,6,8}) | tỷ lệ cao/biên độ nến: p25 2,2 · trung vị 2,5 · max 5,9 |
| `MinBars` (lõi) | 10 | **8** (quét {6,8,10,12}) | lõi ngắn nhất 8 nến (B17), trung vị 20 |
| Số pivot mỗi cạnh | ≥2 mỗi cạnh | **mỗi cạnh ≥1, tổng ≥3, ít nhất một cạnh ≥2** (quét cả "≥2 mỗi cạnh") | 3/20 hộp có một cạnh chỉ 1 nến chạm (B09, B16, B17) |
| `tol` | 0,8 × mbr | **0,5 × mbr** (quét {0.3,0.5,0.8}) | râu nhô ngoài cạnh trung vị 4–5 tick trên, 10 tick dưới, biên độ nến ~17 tick → tol 8 tick loại được râu đơn lẻ |
| `K` (nến chờ sau đóng ngoài) | 2 | **3** (quét {2,3,4}) | 5 ca fail break đóng ngoài rồi quay vào sau 2–4 nến |
| Nến bắt đầu | pivot sớm nhất | **cây "chạy vào vùng"**: lùi từ pivot đầu về trước, lấy nến sớm nhất trong chuỗi liên tiếp có close ∈ [bottom−tol, top+tol] | 15/20 hộp mép trái = cây đẩy mạnh vào vùng hoặc nến ngay sau |
| Gộp | chồng ≥50 % → hợp | **chỉ gộp khi cả 2 cạnh trong ±tol** (cùng range nối dài); chồng một phần hay chung cạnh → **giữ cả hai** | B13/B14 chung cạnh, B10/B11 chồng: CORVEN giữ cả hai |
| Hộp sau khi phá | kết thúc ở nến phá | kết thúc ở nến phá **+ vẽ mờ thêm `G`=30 nến** (mốc retest) | 16/20 hộp kéo quá nến phá 3–22 nến; retest thấy ở 10/19 ca; B12 được kéo dài để làm "range dưới" |
Giữ nguyên: phá = nến ĐÓNG ngoài (20/20 ca); râu ngoài cạnh = stop hunt không dời cạnh (19/20 hộp);
ReEntry trong `G` nến làm range sống lại. Múi giờ: hộp CORVEN = giờ VN, file data = UTC (trừ 7 giờ).
Chuẩn vàng 20 hộp nằm ở `research/corven_boxes.csv` — chưa có data 05–06/11 nên chưa so được.

## 8. Việc còn mở (cần dữ liệu hoặc người học)
- Xuất GCZ26 M1 03→07/11/2026 để so với 5 hộp CORVEN (mục 5.6).
- Range khung lớn vẽ chồng lên chart M1 (CORVEN dùng range M15 làm bối cảnh): để v2, sau khi v1 đúng.
