# PLAN-LICH-SU — làm lại chế độ "Hiện TẤT CẢ vùng trong lịch sử" của Vùng Canh Lệnh

Fable viết 2026-10-23 cho Opus implement. Đọc trước: `README.md` (mục chế độ lịch sử), `PLAN-LAN-CHAM.md` mục 2 (máy "lần chạm"),
`VclCore.cs` (`VSeg`, `VclSegMerge`, `VclCore.UpdateSegs`, `EpisodeTracker`), `VungCanhLenh.cs` (`PaintSegs`, `OnPaintChart`),
`tests/Program.cs` ([13] [14]), `tools/ReplayCsv/Program.cs`.

**Mục đích dùng (người học):** xem lại từng signal Benzo Trader — tại thời điểm signal có những kháng cự/hỗ trợ nào. Muốn chart như ảnh mẫu:
vài hình chữ nhật gọn, mỗi vùng hiệu lực trong một khoảng thời gian (từ lúc hình thành tới lúc giá không quay lại / bị phá), một màu, không chồng.

**Ràng buộc trung thực:** repo đã đo nhiều lần rằng vị trí vùng KHÔNG có lợi thế dự báo (P(chạm) chỉ theo khoảng cách). Chế độ lịch sử là
**công cụ quan sát**: không có khái niệm vùng "mạnh", không lọc theo "độ mạnh", README không được viết câu nào hàm ý vùng dự báo được gì.

---

## 0. Quyết định chính (tóm tắt)

| Việc | Chốt |
|---|---|
| Danh tính một vùng lịch sử | theo **dải giá cố định lúc tạo** (không theo mã vùng engine): vùng Display ở nến i thuộc về vùng lịch sử đang sống nếu dải chồng ≥ 50% dải hẹp hơn |
| Vai và màu | một vai suốt đời: **kháng cự** (giá đóng dưới vùng lúc tạo, đỏ) / **hỗ trợ** (trên, xanh); giá đang trong vùng ⇒ "chưa rõ", chốt ở nến đầu đóng ra ngoài. Bỏ màu cam, bỏ phân biệt gần/xa trong lớp lịch sử |
| Sống | mỗi nến có vùng Display khớp ⇒ `last = i` |
| Kết thúc | (a) **xuyên phá**: máy lần chạm (τ 0 · E 2 giá · G 5 nến — hằng đã có) chạy trên dải cố định, lần chạm chốt với phía thoát "sau lưng" vai ⇒ `end = nến neo cuối`; (b) **hết hạn**: không khớp Display quá **60 phút** ⇒ `end = last`; (c) còn khớp ở nến cuối ⇒ Live, vẽ tới mép phải |
| Chống chồng | vùng Display chồng một phần (> 0 nhưng < 50%) với vùng lịch sử đang sống ⇒ **không tạo** vùng mới (1,0% vùng-nến; vẫn vẽ ở lớp live) |
| Lớp tiêu điểm | các vùng lịch sử sống tại nến dưới con trỏ chuột (không có chuột ⇒ nến ở mép phải) vẽ đậm + nhãn; còn lại vẽ mờ, không nhãn |
| Lớp live trong chế độ lịch sử | **không** vẽ Display từ `FirstTime` nữa (nguồn chồng lớn nhất); vùng Live của lớp lịch sử chính là vùng live, nhãn hiện tại gắn vào nó |
| Nhãn khối lịch sử | chỉ `lo–hi` bên trong khối nếu vừa; khối sống < 15 phút không nhãn |
| Tham số mới | **0** cài đặt mới. Hằng: `LsOverlap = 0,5`, `LsGapMin = 60`, `LsLabelMin = 15` (phút); E/G dùng lại `EpExit`, `EpGapBars` |
| Bỏ | `VSeg`, `VclSegMerge`, `Segs`, `UpdateSegs`, test [13] [14] (thay bằng [15]) |

Kết quả mô phỏng trên dữ liệu thật (mục 1.3): **63 khối/phiên** (p90 81), **0,0% diện tích chồng**, phủ 97,8% vùng-nến live, tại 163 nến signal
Benzo có **6,7 vùng sống** (p10 6 · p90 8) ≈ 6,5 vùng live. Không có cách nào xuống "vài khối/ngày" mà vẫn trung thực — xem 1.4.

---

## 1. Chẩn đoán gốc — vì sao sau khi gộp vẫn vụn, chồng, nhiều màu

Đo bằng script Python trên `research/report/vcl5_cs_replay_v5.csv` (lõi C# v5 chạy 90 ngày GCZ26, 86 333 nến M1, 65 phiên, mỗi nến mỗi vùng
Display: `zone_id, lo, hi, role`) + `_bars.csv`; dựng lại `Segs` đúng luật `UpdateSegs` (đoạn mới khi `Id` mới hoặc `Lo/Hi/Side` đổi) rồi chạy
đúng `VclSegMerge.Merge`. Script tạm nằm ở scratchpad của Fable; Opus port lại thành `research/lich_su.py` (mục 5).

### 1.1 Đoạn sống thô (`Segs`)
- **1 707 đoạn/phiên (51/giờ)**; thời lượng p50 **1 phút**, p85 4, p95 13; 76% < 3 phút, 94% < 10 phút.
- Lý do mở đoạn mới: **biên đổi 93,5%** (103 767) · mã mới 3,8% (4 262) · đổi phía 2,6% (2 915).
- Biên đổi lệch bao nhiêu? **p50 0,03 giá, p85 0,05 giá, 97% ≤ 0,5 giá.** Nguyên nhân: biên vùng = mốc ± `PadU·u`, mà `u` = trung vị trượt 50 nến,
  **đổi mỗi nến** ⇒ `Lo/Hi` trôi vài phần trăm giá ⇒ `UpdateSegs` so `==` ⇒ đoạn mới. Đây là **rung biên** thuần kỹ thuật, không phải vùng đổi.
  (Không sửa engine: đổi parity Python↔C# và mọi số đã đo. Lớp lịch sử phải **hấp thụ** rung biên.)
- Ngoài ra bộ tính lại ~3 lần/giờ: vùng rời bộ (giá ra khỏi hành lang) rồi quay lại với **mã mới** ⇒ cùng dải giá lặp lại thành khối mới;
  đổi `Side` (vùng trên giá → giá đi lên → vùng dưới giá) ⇒ khối mới khác màu dù cùng dải.

### 1.2 `Merge` hiện tại (50% · 10 phút · bỏ < 3 phút)
- **85 khối/phiên** (p90 112, max 130), 2,55/giờ; thời lượng p50 50 phút.
- Cửa sổ 30 giờ bất kỳ (bằng ảnh chụp 3.png): **p50 86 khối, p90 127** — khớp cái người học thấy.
- Khối/khoá giá (tâm làm tròn 1 giá)/phiên: TB **2,33, max 14** ⇒ "4139–4141 lặp lại hàng chục khối" là thật.
- Diện tích chồng giữa các khối lịch sử: chỉ **0,3%**. Vậy "chồng chéo" trên ảnh đến từ chỗ khác:
  1. **Lớp live đè lên lớp lịch sử**: vùng Display đang sống vẽ từ `FirstTime` (lần đầu mã xuất hiện — có thể lùi hàng giờ) tới mép phải; các đoạn
     rung biên *đã đóng* của **cùng mã đó** lại được coi `!Live` và vẽ thành khối lịch sử ⇒ hai hình đè nhau suốt chiều dài sống của vùng.
  2. Khối cùng dải **đứng kề nhau khác màu** (đỏ → cam → xanh khi giá đi xuyên; `Merge` không gộp khác phía, phía 0 gộp với bất kỳ phía nào và
     khối lấy màu đoạn lâu nhất) ⇒ nhìn như một dải ba màu.
  3. **86 nhãn** trên một màn hình.
- Chỉnh tham số `Merge` không cứu được: khoảng trống 60 phút ⇒ 64 khối nhưng chồng 2,2%; khoảng trống ∞ ⇒ 8,6 khối/phiên nhưng chồng 16,6% và khối
  dài hàng tuần (không có luật kết thúc). Gốc: `Merge` **không có danh tính vùng và không có luật sống/chết**, chỉ dán đoạn.

### 1.3 Mô phỏng thiết kế mới (mục 2) trên cùng dữ liệu

| Biến thể | khối/phiên TB · p90 | khối thấy trong 24 h p50 · p90 | chồng diện tích | phủ Display | bắc cầu* | kết thúc xuyên / hết hạn |
|---|---|---|---|---|---|---|
| hết hạn 30 phút | 69 · 89 | 64 · 88 | 0,0% | 98,0% | 2,7% | 1 814 / 2 694 |
| **hết hạn 60 phút (chốt)** | **63 · 81** | **60 · 81** | **0,0%** | **97,8%** | **6,2%** | 1 903 / 2 195 |
| hết hạn 120 phút | 57 · 73 | 55 · 75 | 0,0% | 97,6% | 12,4% | 1 982 / 1 684 |
| hết hạn 240 phút | 52 · 67 | — | 0,0% | 97,4% | 19,7% | 2 057 / 1 319 |
| hết hạn = hết phiên | 53 · 70 | — | 0,0% | 97,6% | 35,3% | 2 105 / 1 343 |
| 60 + chỉ giữ ≥ 1 chạm lại | 39 · 52 | — | 0,0% | **68,6%** | 14,1% | — |
| 60 + bỏ khối < 15 phút | 55 · 67 | 54 · 71 | 0,0% | 96,9% | — | — |
| 120, dải = hợp các dải khớp | 54 · 69 | — | **1,4%** | 97,5% | 11,7% | — |
| 120, không chặn chồng một phần | 59 · 75 | — | 0,2% | 98,8% | 12,5% | — |
| 120, E = 1 / E = 3 / G = 10 | 60 / 54 / 52 | — | 0,0% | ≈97% | ≈12% | — |

\* bắc cầu = % thời-gian-vùng-lịch-sử mà live **không** hiện vùng cùng dải (vùng vẫn vẽ dù live đã bỏ nó khỏi bộ). Phủ Display = % vùng-nến live có vùng
lịch sử sống cùng dải.

Số đo khác của biến thể chốt: thời lượng khối p50 73 phút, p90 343; khối < 3 phút 2%, < 15 phút 13%; vùng sống mỗi nến TB 8,2 (p90 10, max 22);
tạo khi giá đang trong vùng (vai chưa rõ) 255/4 107 = 6%, chốt vai trễ p50 1 phút, p90 5 phút, không ca nào không chốt được; 64% khối có ≥ 1 lần chạm lại.
Khoảng trống giữa hai lần cùng dải xuất hiện: p50 1 phút, p95 19 phút, 96% ≤ 60 phút ⇒ 60 phút bao gần hết khoảng trống do rung/tính lại; phần còn lại là
"giá đi xa nhiều giờ rồi về" — cho **khối mới** là đúng ý ảnh mẫu (dải lặp lại thành hai khối tách nhau, không chồng).

### 1.4 Giới hạn vật lý — nói trước để không kỳ vọng sai
Trong 24 giờ giá vàng đi qua ~30–50 giá, dải 2–5 giá ⇒ ~15 dải, mỗi dải có thể là kháng cự rồi hỗ trợ (hai khối) và lặp khi giá về sau > 60 phút ⇒
**50–60 khối/24 h là sàn** nếu vẫn vẽ *mọi* vùng live từng hiện. Ảnh mẫu 2.png là một đoạn đi ngang đẹp, không phải một ngày bình thường.
Cách duy nhất để màn hình chỉ còn "vài khối" mà không bỏ thông tin: **lớp tiêu điểm theo thời điểm** (mục 2.5) — đúng nhu cầu review signal
(tại nến signal có 6–8 vùng sống).

---

## 2. Thiết kế mới

### 2.1 Đối tượng `VLichSu` (thay `VSeg`)
```
int Id;  double Lo, Hi;          // dải CỐ ĐỊNH từ lúc tạo
int Vai;                         // +1 kháng cự, −1 hỗ trợ, 0 chưa rõ (tạm)
int Start, Last, End;            // chỉ số nến; End = −1 khi còn sống
DateTime StartTime, EndTime;
string LyDo;                     // "xuyên phá" | "hết hạn" | "" (còn sống)
int NChamLai;                    // số lần chạm bắt đầu SAU nến tạo (chỉ để nhãn/thống kê, không lọc)
bool TungGan;                    // từng khớp vùng Slot K/N (để tuỳ chọn "Hiện vùng xa" tắt thì ẩn khối chỉ-từng-là-xa)
int MatchedId;                   // mã vùng Display đang khớp ở nến cuối (−1 nếu không) — để lấy nhãn live
EpState Ep;                      // lần chạm đang mở trên dải này (máy riêng, mục 2.4)
```
Lõi giữ `List<VLichSu> LichSu` (cũ → mới, sắp theo `Start`) và `List<VLichSu> _song` (đang sống).

### 2.2 Khớp và tạo (mỗi nến, SAU khi có `Display` của nến đó)
Với từng vùng Display `z` (duyệt theo thứ tự trong `Display`):
1. Tìm vùng lịch sử đang sống có `rel = chồng / min(rộng hai dải) ≥ 0,5`, chọn `rel` lớn nhất ⇒ **khớp**: `Last = i`, `MatchedId = z.Id`,
   `TungGan |= z.Slot != 'F'`. Một vùng lịch sử chỉ khớp **một** `z` mỗi nến (Display không chồng nhau nên tự nhiên thoả).
2. Không khớp nhưng có vùng lịch sử đang sống chồng `0 < rel < 0,5` ⇒ **không tạo** (chống chồng). Vùng `z` này vẫn là vùng live, vẽ ở lớp live (2.6).
3. Không chồng gì ⇒ **tạo** `VLichSu { Lo = z.Lo, Hi = z.Hi, Start = Last = i, Vai = C < Lo ? +1 : C > Hi ? −1 : 0 }`.

Vì sao 50% (không phải 30/70)? Dùng lại đúng ngưỡng `Merge` hiện có (đã có test), và rung biên thật chỉ 0,03–0,05 giá trên dải ≥ 2 giá (rel ≈ 98%);
ngưỡng chỉ cần tách "cùng dải" với "dải kề lệch nửa vùng". Không chạy độ nhạy ngưỡng này — không phải tham số nhạy.

### 2.3 Vai
- Chốt ở nến tạo theo **giá đóng so với dải** (không dùng `VZone.Side` — đã đo: hai cách cho cùng 3 697 vs 3 698 khối, nhưng giá đóng không phụ thuộc
  quy ước side của engine, và đúng ngay cả nến sau xuyên phá khi engine chưa đổi side).
- Giá đóng trong dải ⇒ `Vai = 0`; mỗi nến sau: `C < Lo ⇒ +1`, `C > Hi ⇒ −1`. (6% ca, trễ p50 1 phút.) Màu khối theo vai cuối — chấp nhận
  "nhìn trước" cỡ vài phút **chỉ ở màu**, ghi rõ README.
- Vai **không đổi** suốt đời: bị xuyên = kết thúc; dải đó với vai mới là **khối mới** (ảnh mẫu đúng như vậy).

### 2.4 Kết thúc
(a) **Xuyên phá** — máy trạng thái riêng trong `LichSuTracker`, cùng luật và hằng với `EpisodeTracker` (τ = `EpTau`, E = `EpExit`, G = `EpGapBars`),
chạy trên **dải cố định** của từng vùng lịch sử đang sống:
```
cham = max(C₋,H) ≥ Lo−τ và min(C₋,L) ≤ Hi+τ ;  neo = cham hoặc Lo−E ≤ C ≤ Hi+E
chưa mở và cham ⇒ mở (nếu i > Start thì NChamLai++)
đang mở: neo ⇒ dem = 0 ; không neo ⇒ phia = C > Hi ? +1 : −1, dem++
         dem == G ⇒ đóng lần chạm; nếu (Vai == +1 && phia == +1) || (Vai == −1 && phia == −1) ⇒ XUYÊN PHÁ: End = i − G, LyDo = "xuyên phá"
nến đầu phiên ⇒ đóng lần chạm đang mở (không kết thúc vùng)
```
Khác `EpisodeTracker` ở một điểm cố ý: xuyên tính theo **vai vùng**, không theo "phía giá tới" của lần chạm (lệch nhau 55/4 107 ca = 1,3%).
Không tái dùng `EpisodeTracker` vì nó đóng lần chạm khi mã "rời bộ" và không lộ `PhiaThoat` ra ngoài; viết máy 10 dòng, test riêng.

(b) **Hết hạn**: sau bước (a), nếu `phút(i) − phút(Last) > 60` ⇒ `End = Last`, `LyDo = "hết hạn"`. Thứ tự: khớp (2.2) → máy (a) → hết hạn (b)
để nến khớp lại đúng lúc không bị cắt oan. 60 phút: bảng 1.3 (điểm gãy giữa số khối và bắc cầu; = tuổi thọ trung vị vùng live 60 phút).

(c) Hết dữ liệu ⇒ `End = −1`, vẽ tới mép phải. Hết phiên **không** kết thúc vùng (biến thể "hết phiên" bắc cầu 35%).

Vùng kết thúc ⇒ rời `_song`; nến ngay sau, Display cùng dải (engine đã đổi side hoặc chưa) ⇒ tạo khối mới theo 2.2 — khối mới bắt đầu
sau `End` nên không chồng thời gian.

### 2.5 Lớp tiêu điểm (phần giải quyết nhu cầu review)
- Thời điểm tiêu điểm `tF` = giờ nến dưới con trỏ chuột trên chart; không có chuột trong chart ⇒ nến **mép phải** màn hình.
  API đã dùng trong repo: `CurrentChart.MouseMove` với `ChartMouseNativeEventArgs e.X` (`quantower-tpo-suite/ProfileEngine.cs`,
  `quantower-entry-signal/UiKit.cs`) + `CoordinatesConverter.GetTime(x)` (`quantower-askbid-delta/AskBidDeltaBars.cs`). Chỉ gắn sự kiện khi
  `ShowAllHistory` bật; gỡ khi tắt/`OnClear`/`Dispose`. Không `Handled`, chỉ `NeedRedraw` khi `tF` đổi nến.
- Vùng lịch sử **sống tại `tF`** (`StartTime ≤ tF` và (`End < 0` hoặc `tF ≤ EndTime`)): tô alpha 55, viền 150, nhãn `lo–hi` ở mép trái khối
  (nếu vừa) **và** một nhãn ở x của `tF` nếu khối dài. Vùng khác: tô alpha 18, viền 60, **không nhãn**.
- Một đường dọc mảnh tại `tF` (alpha 60) để biết đang soi nến nào. Không bảng, không chữ thêm.
- Người học review signal: rê chuột tới nến signal ⇒ thấy đúng 6–8 khối đậm = bộ vùng khi đó (đo: TB 6,7 ≈ 6,5 vùng live).

### 2.6 Lớp live khi bật chế độ lịch sử
- **Không** vẽ `rs.Zones` từ `FirstTime` nữa. Vùng Live của lớp lịch sử (End < 0) vẽ tới mép phải, nhãn live = `Label(z)` của vùng Display
  `MatchedId` (đặt ở mép phải như hiện nay).
- Vùng Display **bị chặn** (2.2 bước 2, ~1,0% vùng-nến): vẽ viền đứt không tô từ nến hiện tại tới mép phải + nhãn live, để không mất vùng live nào.
- Tắt chế độ lịch sử ⇒ vẽ y như cũ (không đụng).

### 2.7 Màu, nhãn, tuỳ chọn
- Màu: kháng cự = `ResColor`, hỗ trợ = `SupColor`, vai 0 = xám (chỉ tồn tại vài phút). Không dùng `TestColor` trong lớp lịch sử.
- Nhãn trong khối: `lo–hi` (định dạng `F`), chỉ khi `sống ≥ 15 phút` và vừa chiều rộng; font hiện có.
- `ShowFar` tắt ⇒ ẩn khối `!TungGan`. `ShowLabels` tắt ⇒ không nhãn trong khối, vẫn giữ nhãn live.
- **Không thêm cài đặt.** Hằng trong `Vcl`: `LsOverlap = 0.5`, `LsGapMin = 60.0`, `LsLabelMin = 15.0`.

### 2.8 Phương án đã cân nhắc và loại
| Phương án | Lý do loại |
|---|---|
| Giữ `Merge`, chỉnh khoảng trống/ngưỡng | không có danh tính và luật kết thúc: gap 60 ⇒ chồng 2,2%, gap ∞ ⇒ chồng 16,6%, khối dài hàng tuần |
| Danh tính theo `Id` engine | mã đổi khi rời bộ rồi quay lại; mã giữ nhưng biên rung ⇒ 93,5% đoạn vỡ |
| Dải = hợp các dải khớp (nới ≤ 5 giá) | chồng 1,4% vì dải phình lấn vùng kề; không gọn hơn; dải đổi theo tương lai |
| Lưới giá làm tròn 0,5 (như `quay_lai.py`) | dải cố định + chồng ≥ 50% làm cùng việc, không cần thêm lưới |
| Kết thúc theo phiên | bắc cầu 35% (vẽ vùng live đã bỏ hàng giờ) |
| Hết hạn 30 / 120 / 240 phút | 69 / 57 / 52 khối nhưng bắc cầu 2,7 / 12,4 / 19,7%; 60 là điểm gãy |
| E = 1 / 3, G = 10 | ±10% số khối; giữ **một** định nghĩa "xuyên phá" cho cả nhãn live lẫn lịch sử |
| Chỉ giữ vùng có ≥ 1 lần chạm lại | còn 39 khối nhưng phủ Display rớt 98 → 69%: mất chính vùng live có mặt lúc signal (vd mốc TP chưa chạm tới) |
| Bỏ khối < 15 phút | giảm 63 → 55 nhưng tồn tại của khối phụ thuộc tương lai; thay bằng "không nhãn" |
| Sửa engine hết rung biên (làm tròn đệm) | đổi parity Python↔C#, đổi mọi số đã đo; để vòng khác nếu cần |
| Vai theo `VZone.Side` | cùng kết quả nhưng phụ thuộc quy ước side (đã từng gây lỗi), và sai ở nến sau xuyên phá khi engine chưa đổi side |
| Tái dùng `EpisodeTracker` cho vùng lịch sử | đóng lần chạm khi mã "rời bộ", xuyên tính theo phía giá tới, không lộ `PhiaThoat` |

---

## 3. Tiêu chí nghiệm thu (đo trên replay 90 ngày `fp_GCZ26_XCEC_Time_20260723-20261021_90d`, in vào `report/LICH-SU.md`)

| # | Tiêu chí | Ngưỡng | Đã đo (mô phỏng) |
|---|---|---|---|
| 1 | khối/phiên TB · p90 | ≤ 65 · ≤ 85 | 63,2 · 81 |
| 2 | khối "thấy" trong cửa sổ 24 h (giao thời gian) p50 · p90 | ≤ 65 · ≤ 85 | 60 · 81 |
| 3 | diện tích chồng giữa các khối lịch sử cùng phiên (thời gian × giá) | **0%** (không có cặp nào giao) | 0,0% |
| 4 | chồng giữa lớp live và lớp lịch sử | 0 (cùng một đối tượng) | — |
| 5 | phủ Display: % vùng-nến live có vùng lịch sử sống cùng dải (≥ 50%) | ≥ 97% | 97,8% |
| 6 | bắc cầu | ≤ 8% | 6,2% |
| 7 | khối < 3 phút | ≤ 3% | 2% |
| 8 | khối/khoá giá (tâm làm tròn 1 giá)/phiên | TB ≤ 2 | 1,9 |
| 9 | tại nến signal Benzo (`benzo-trader/research/report/_replay_cs.csv`, 163 signal) số vùng sống | TB 6–8, p90 ≤ 9 | 6,7 · p90 8 |
| 10 | **không nhìn trước**: chạy lõi tới nến i, mọi vùng có `End < i` và `(Lo, Hi, Start)` của vùng đang sống y hệt chạy đủ dữ liệu; vai của vùng đã chốt vai trước i cũng y hệt | 100% | — |
| 11 | **tái lập**: `ReplayCsv` xuất `_lichsu.csv` (`id, start_utc, end_utc, lo, hi, vai, ly_do, n_cham_lai, tung_gan`); chạy hai lần giống nhau; `research/lich_su.py` (Python) ra cùng danh sách **từng dòng** | 100% | — |
| 12 | thời gian: `Push` thêm ≤ 10% so với hiện tại trên 86 333 nến (đo bằng `ReplayCsv` trước/sau) | ≤ +10% | — |
| 13 | ảnh thật từ Optimus Flow (người học chụp 2 ảnh: 1 ngày đi ngang, 1 ngày có xu hướng) — mỗi ảnh đếm được số khối, không có hai khối giao nhau, rê chuột tới một signal thấy ≤ 9 khối đậm | đạt | — |

Chỉ số 1–2 là **số đếm trung thực**, không phải mục tiêu "càng ít càng tốt": giảm thêm chỉ bằng cách bỏ vùng live đã hiện (vi phạm 5).

---

## 4. Test cụ thể cho Opus

### 4.1 Đơn vị (`tests/Program.cs`, mục [15] "Vùng lịch sử"; bỏ [13] [14])
Dùng lõi giả: hàm `LichSuTracker.Step(i, bar, cprev, newSess, display)` nhận danh sách `(id, lo, hi, slot)` thay vì chạy cả engine.
1. **Rung biên**: cùng mã, biên lệch ±0,05 giá qua 50 nến ⇒ đúng 1 vùng lịch sử, dải = dải nến đầu, `Last` = nến cuối.
2. **Mã mới cùng dải**: mã 7 (nến 0–20) rồi mã 9 (nến 21–40) cùng dải ⇒ 1 vùng.
3. **Rời bộ rồi về**: không hiện 30 phút rồi hiện lại cùng dải, giá không xuyên ⇒ 1 vùng (bắc cầu); không hiện 61 phút ⇒ 2 vùng, `End₁ = Last₁ < Start₂`.
4. **Xuyên phá**: vai +1 (giá đóng dưới), 5 nến liền đóng > Hi + 2 ⇒ `End = nến thoát đầu − 1`, `LyDo = "xuyên phá"`; Display nến sau cùng dải ⇒ vùng mới vai −1, `Start₂ > End₁`.
5. **Phá giả**: 3 nến đóng ngoài rồi quay vào ⇒ không kết thúc, `dem` về 0.
6. **Thoát về phía cũ** (vai +1, giá rơi xuống dưới Lo − 2 năm nến) ⇒ không kết thúc; lần chạm đóng; `NChamLai` đúng.
7. **Vai chưa rõ**: tạo khi `C` trong dải ⇒ `Vai = 0`; nến sau đóng trên Hi ⇒ `Vai = −1`; nến sau nữa không đổi dù giá đổi phía.
8. **Chống chồng**: Display chồng 30% với vùng sống ⇒ không tạo, vùng sống không đổi; 60% ⇒ khớp.
9. **Hết phiên**: lần chạm đang mở bị đóng, vùng vẫn sống, `Last` tiếp tục cập nhật.
10. **Không nhìn trước**: `Synthetic(3000)` cắt ở 2000 — như test [13] cũ nhưng cho `LichSu` (tiêu chí 10).
11. **Không chồng**: `Synthetic(3000)` ⇒ với mọi cặp vùng lịch sử, không có giao (thời gian × giá) kể cả vùng đang sống.
12. **Khớp live**: ở nến cuối, mỗi vùng Display hoặc có đúng một vùng lịch sử sống khớp (`MatchedId`) hoặc nằm trong danh sách "bị chặn".
13. `TungGan`: vùng chỉ từng là Slot 'F' ⇒ false; từng là 'N' ⇒ true.

### 4.2 Trên dữ liệu thật
- `tools/ReplayCsv`: thêm `_lichsu.csv` + in số khối, thời gian chạy. Chạy trên file 90 ngày và file 29 ngày (`20260816-20260915`).
- `research/lich_su.py`: port mô phỏng (đọc replay `vcl5_cs_replay_v5.csv` + bars; không chạy lại engine Python) ⇒ bảng tiêu chí 1–9 + so **từng dòng**
  với `_lichsu.csv` của C# (tiêu chí 11). Ghi `report/LICH-SU.md` (bảng + nhận xét ≤ 10 dòng, trung thực: nói rõ 63 khối/phiên là sàn vật lý, không phải "vài").
- `research/ve_lich_su.py`: vẽ 2 phiên (một đi ngang, một xu hướng) nến M1 + khối lịch sử + đánh dấu nến signal Benzo và các khối sống tại đó — để Fable nhìn trước khi deploy.

---

## 5. Việc làm theo thứ tự · file sửa

1. `VclCore.cs`: thêm hằng `LsOverlap/LsGapMin/LsLabelMin` vào `Vcl`; class `VLichSu`, `LichSuTracker` (khớp 2.2, vai 2.3, máy 2.4, danh sách `LichSu`, `Song`, `BiChan`);
   gọi trong `Push` ngay sau `Display = disp;` (cả nhánh `u` NaN: chỉ chạy hết hạn/máy, không tạo). **Xoá** `VSeg`, `VclSegMerge`, `Segs`, `_openSeg`, `UpdateSegs`.
2. `tests/Program.cs`: mục [15] (4.1); xoá [13] [14]; `dotnet run --project vung-canh-lenh/tests` xanh.
3. `tools/ReplayCsv/Program.cs`: xuất `_lichsu.csv`; chạy 90 ngày + 29 ngày.
4. `research/lich_su.py` + `ve_lich_su.py` → `report/LICH-SU.md`, `report/img/lich_su_*.png`. Parity từng dòng 100%; tiêu chí 1–9, 12.
5. `VungCanhLenh.cs`: `RenderState.Segs` → `List<VLichSu> LichSu` + `List<VZone> BiChan`; `PaintSegs` → `PaintLichSu` (2.5, 2.7); bắt/gỡ chuột; nhánh `ShowAllHistory` không vẽ `Zones` từ `FirstTime` (2.6). Build `./build.sh`, 0 cảnh báo.
6. `README.md`: viết lại mục "Chế độ Hiện TẤT CẢ vùng trong lịch sử" (định nghĩa khối, vai, kết thúc, tiêu điểm theo chuột, giới hạn: ~60 khối/24 h là bình thường, màu chốt trễ vài phút khi tạo trong vùng, khối xuyên phá "co lại" 5 nến sau khi chốt).
7. Commit + push từng bước; báo hash. Người học chạy Optimus Flow, chụp 2 ảnh (tiêu chí 13).

---

## 6. Rủi ro / chỗ dễ sai — Opus báo lại từng mục

1. **Sự kiện chuột Quantower**: `MouseMove` chạy luồng UI, `OnPaintChart` cũng vậy nhưng `Process()` thì không ⇒ `tF` để trong `_render` dưới `_sync`; chỉ gọi `RedrawBuffer` khi nến tiêu điểm đổi. Gỡ sự kiện khi tắt tuỳ chọn, `OnClear`, `Dispose`. Nếu API chuột không hoạt động trong Optimus Flow ⇒ dùng mép phải, ghi README, **không** thêm cài đặt "giờ xem lại".
2. **Thứ tự trong `Step`**: khớp → máy xuyên → hết hạn. Đảo thứ tự làm vùng khớp lại đúng phút 61 bị cắt, hoặc vùng vừa xuyên còn khớp tạo khối mới chồng thời gian.
3. **`End = i − G`** có thể < `Start` khi vùng tạo lúc giá đang trong dải rồi thoát ngay (vai 0 → chốt → xuyên trong < G nến): kẹp `End = max(Start, i − G)`; test.
4. **Khối Live "co lại"** 5 nến khi chốt xuyên phá (giống nhãn trễ 5 nến) — hiện tượng thật, không phải lỗi; ghi README.
5. **Màu chốt trễ** với vai 0 (6% khối): khối đổi màu sau 1–5 phút; không phải lỗi.
6. **`FirstTime` vẫn dùng ở chế độ gọn** (tắt lịch sử) — không đổi hành vi cũ.
7. **Reset lõi** (`VclFeeder`) dựng lại toàn bộ lịch sử từ đầu — xác định, nhưng danh sách `LichSu` phải xoá theo; đừng giữ danh sách cũ qua reset.
8. **Bộ nhớ/vẽ**: 90 ngày ≈ 4 100 khối; vẽ chỉ khối giao `clip`; tìm khối sống tại `tF` bằng duyệt tuyến tính là đủ (≤ 5 000 phần tử).
9. **Dải Display rộng hơn 2× dải vùng lịch sử** (vd vùng lịch sử 2 giá, Display 5 giá chồng trọn): rel = 1 ⇒ khớp, khối giữ dải 2 giá — nhãn live sẽ nói 5 giá. Chấp nhận (dải cố định), ghi README; đo tần suất `|rộng Display − rộng khối| > 1 giá` lúc khớp, báo số.
10. **Hai vùng lịch sử sống kề nhau cùng vai, giá rung ở khe** ⇒ máy lần chạm của cả hai mở/đóng độc lập — đúng thiết kế, nhưng `NChamLai` có thể đếm 2 cho một cú giá (giống rủi ro 11 PLAN-LAN-CHAM). Không lọc gì theo `NChamLai`.
11. **Replay dùng Display của C# v5 hiện tại** (`vcl5_cs_replay_v5.csv` sinh 2026-10-22): nếu engine đã đổi sau đó, chạy lại `ReplayCsv` trước khi so parity.
12. **Số đo có thể lệch nhỏ** giữa mô phỏng của Fable và C# ở ca nến không có Display (`u` NaN 10 nến đầu) và ca nến đầu phiên (`cprev = O`) — parity từng dòng sẽ lộ; sửa C# theo đặc tả này, không sửa đặc tả cho khớp số.
13. Ca chưa phủ ⇒ dừng và hỏi, không tự chế luật mới (đặc biệt: không thêm lọc "vùng mạnh").
