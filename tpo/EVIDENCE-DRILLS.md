# 🔬 SĂN BẰNG CHỨNG — cơ chế luyện mắt trên Optimus Flow

> **Người học chốt 2026-08-11:** *"nghĩ cách ra cho tôi luyện mắt với các khái niệm bài giảng, để biết
> được rằng các kiến thức ko chỉ là khái niệm đơn thuần mà nó có thật."*
>
> Từ nay **mọi buổi TPO đều kèm bài săn bằng chứng**. Không có bằng chứng thì coi như chưa học xong mục đó.

---

## 🚨 VIỆC PHẢI LÀM TRƯỚC TIÊN — chart TPO hiện tại đang neo SAI phiên

Tôi đã chạy thử đếm trên `data-export/TPO-chart-daily.csv`. Kết quả **không kết luận được gì**, và lý do
quan trọng hơn bản thân con số:

**Mốc bắt đầu mỗi profile trong file anh export:**
```
6/25 23:00   6/26 05:00   6/29 07:00   6/30 05:00   7/1 05:00 …
```
→ Profile đang neo vào **Globex (~05:00 VN)**, không phải phiên pit COMEX, và **mốc còn không nhất quán**
(23:00 / 05:00 / 07:00). Hệ quả: **IB (2 bracket đầu) đang lấy ở 05:00 sáng VN** — tức lúc thị trường vàng
mỏng nhất, lệch ~14 tiếng so với chỗ đáng đọc. **Mọi luật dính IB đều vô nghĩa với dữ liệu này.**

Đếm ra được (n = 22 profile, quá ít, chỉ để minh hoạ cơ chế — **đừng tin số**):

| Luật | Kết quả | Đọc thế nào |
|---|---|---|
| IB range ≤1% ⇒ phiên sau breakout | IB range **trung vị chỉ 0,27%**, max 1,43% | **Ngưỡng "1%" vô dụng với vàng** — gần như MỌI phiên đều ≤1% nên luật không phân loại được gì. Luật này viết cho thị trường khác thang giá. Phải đổi sang **phân vị** (vd IB thuộc 25% hẹp nhất) |
| VA nằm trong IB ⇒ phiên sau có trend | chỉ có **1 ca** VA-trong-IB | n=1, không nói được gì |
| Giá đóng ngoài VA ⇒ VA không hợp lệ | **10/22 = 45%** phiên đóng ngoài VA | 45% là quá cao cho một trạng thái "bất thường" → dấu hiệu nữa cho thấy profile đang dựng sai phiên |

**⇒ BÀI SỐ 0 (làm trước mọi buổi):**
1. Trong Optimus Flow, sửa session của chart TPO Daily để **bracket A khởi ~19:20 VN** (pit COMEX), rồi
   chụp lại ảnh cấu hình session cho tôi kiểm.
2. Export lại **≥ 3 tháng** TPO daily (n ≥ 60 phiên) — n=22 không đủ để đếm bất cứ luật nào.
3. Xong 2 việc này thì mọi bài "Mức 2 — ĐẾM" bên dưới mới chạy được.

> Đây chính là ví dụ cho điều anh muốn: một luật nghe rất chắc ("IB ≤1% ⇒ hôm sau breakout") **hoá ra
> không áp được vào vàng** vì ngưỡng lấy từ thị trường khác. Nếu không đếm thì không bao giờ biết.

---

## 🎯 Cơ chế 3 MỨC — áp cho mọi khái niệm

Mỗi khái niệm học xong phải đi qua 3 mức. Ba mức trả lời ba câu khác nhau:

### Mức 1 — NHẬN DẠNG *(“cái này có thật trên chart của tôi”)*
Tìm **1 ca** khái niệm đó trên Optimus Flow, chụp ảnh, ghi số.
→ Chứng minh khái niệm **tồn tại trên chart của chính anh**, không phải hình vẽ trong sách.

### Mức 2 — ĐẾM *(“nó đúng bao nhiêu phần trăm”)*
Duyệt **N phiên liên tiếp** (không chọn lọc — cứ N phiên gần nhất), đếm **khớp / không khớp**.
→ Biến khái niệm thành **một tỷ lệ**. Đây là mức biến "kiến thức" thành "cược được".

**Hai kênh chạy song song, rồi so nhau:**
- **Anh đếm bằng MẮT** trên Optimus Flow → ghi vào bảng.
- **Tôi đếm bằng SỐ** từ CSV export → chạy script.
- **Lệch nhau ⇒ một trong hai đang hiểu sai định nghĩa** → đó là lúc học được nhiều nhất.

### Mức 3 — PHẢN CHỨNG *(“nó sai ở đâu”)*
Tìm **1 ca luật SAI**.
→ **Bắt buộc**, vì nếu chỉ đi tìm ca khớp thì anh sẽ luôn tìm được (thiên kiến xác nhận). Chỉ khi biết luật
sai ở hoàn cảnh nào thì mới dám cược tiền theo nó.

---

## 📐 Bằng chứng phải đạt — không đạt thì tôi không chấm

1. Ảnh đọc được: **mã · khung · ngày+giờ · các con số liên quan**. Ảnh mờ/thiếu số = không tính (tôi cũng
   phải **đọc số trên ảnh**, không được đoán — CLAUDE.md #7).
2. **Anh ghi phán đoán TRƯỚC, tôi chấm SAU.** Không được để tôi nói trước rồi anh gật — như thế thì bài
   tập vô nghĩa.
3. Lưu vào `tpo/evidence/buoi-N/`, kèm `README.md` ghi phán đoán của anh.
4. **Nói "không tìm được" là một câu trả lời hợp lệ** — và là thông tin tốt (khái niệm đó hiếm, hoặc chart
   đang cấu hình sai). Đừng cố nặn ra một ca cho đủ bài.

---

## ⚙️ Setup Optimus Flow cần có (làm một lần)

| Chart | Cấu hình | Dùng cho buổi |
|---|---|---|
| **A. TPO Daily** | period **30′**, session neo **pit COMEX (bracket A ~19:20 VN)** | 2, 3, 6, 7 |
| **B. TPO composite** | **gộp 3 tuần**, period vẫn **30′** (cấu hình thật của CORVEN) | 5 |
| **C. Volume Profile** | bật **cạnh** chart TPO, cùng khung | 3, 5 |
| **D. Footprint + Delta M1** | đã có sẵn | 8 |
| **E. Indicator tự viết** | `DailyTpoBias`, `SessionZones` (đã deploy) | 5, 6 |

> ⭐ **Vì sao bắt buộc có chart C:** **TPO đo THỜI GIAN, không đo VOLUME.** Mà luật "tail volume dày = scam"
> lại cần volume. Nhìn TPO một mình **không thể** phân biệt tail xịn / tail scam — phải đặt Volume Profile
> cạnh nó. Đây không phải chi tiết vụn: nó là lý do nhiều người đọc TPO sai ở cực trị.

---

## 📗 Buổi 2 — HÌNH DẠNG PROFILE

| Mức | Bài | Bằng chứng phải giao |
|---|---|---|
| **1** | Chụp **5 phiên liên tiếp** gần nhất trên chart A. Tự gắn tên hình dạng từng phiên: **D / P / b / B / chữ nhật / thin** | 5 ảnh + 5 nhãn (ghi trước khi tôi chấm) |
| **1b** | Tìm bằng được **1 ca chữ B (double distribution)** và chỉ ra **vệt mỏng ở giữa** | 1 ảnh, khoanh vùng mỏng, ghi mức giá của nó |
| **2** | Duyệt **20 phiên** gần nhất, đếm mỗi hình dạng bao nhiêu ca | bảng 6 dòng. *Sách nói "Normal Day (P/b) hay gặp nhất" — với vàng có đúng không?* |
| **2b** | *"Sau bell curve là có trend"*: sau mỗi phiên hình **D**, phiên **sau** Range có lớn hơn trung vị không? | anh đếm bằng mắt; tôi đếm từ CSV (`Range`) rồi so |
| **3** | Tìm **1 phiên anh KHÔNG gọi được tên hình dạng** | 1 ảnh — ca biên, mang lên tôi phân xử bằng cơ chế đấu giá |
| **chốt sổ** | Với mỗi phiên: giá **ĐÓNG** nằm trong hay ngoài VA? | cột thêm vào bảng Mức 2 — luật *"đóng ngoài VA ⇒ VA không hợp lệ"* |

## 📗 Buổi 3 — CHECK TAIL

| Mức | Bài | Bằng chứng phải giao |
|---|---|---|
| **1** | Trên chart A **+ C**: tìm **1 tail volume THẤP** và **1 tail volume DÀY**, đặt cạnh nhau | 2 ảnh + ghi **volume tại mức tail** của từng ca |
| **1b** | Tìm **1 poor high hoặc poor low** (cực trị có **≥2 TPO**) | 1 ảnh + đếm rõ số TPO ở mức cực trị |
| **2** | **15 phiên**: mỗi phiên ghi đỉnh & đáy là **tail đơn** hay **poor**. Rồi xem **phiên sau có test lại mức đó không** | bảng 15 dòng × 3 cột. Luật dự đoán: poor ⇒ bị test lại |
| **3** | Tìm **1 ca tail volume DÀY mà giá VẪN đảo chiều thật** | 1 ảnh — chứng minh luật tail-scam chỉ là xác suất, không phải định luật |

## 📗 Buổi 6 — BALANCE vs SAU BALANCE

| Mức | Bài | Bằng chứng phải giao |
|---|---|---|
| **1** | Tìm **1 phiên "đẹp"**: IB **bao trọn** VA + giá mở & đóng **đều trong IB** + biên độ thấp. Rồi chụp **phiên NGAY SAU** nó | 2 ảnh cạnh nhau + 4 số: IBH, IBL, VAH, VAL |
| **1b** | Tìm **1 ca "vừa ra khỏi balance"**: profile đã xong (D/chữ nhật) rồi giá break ra | 1 ảnh + đánh dấu cây break |
| **2** | ⭐ Bài mạnh nhất — **tôi đếm bằng script** trên CSV (đã có sẵn `IB High/IB Low/VAH/VAL/Range/Open/Close`): «VA trong IB ⇒ phiên sau trend?» và «IB hẹp ⇒ phiên sau breakout?» | anh chỉ cần **export ≥3 tháng** (Bài số 0). Anh cũng đếm 15 phiên bằng mắt để so |
| **3** | Tìm **1 ca IB hẹp mà phiên sau vẫn sideway** | 1 ảnh |
| **nối delta** | Trong 1 ca "sau balance": leg đầu tiên có **tăng mà delta âm** không? Nếu có, sau đó **có squeeze** không? | ảnh chart D + đường delta — kiểm luật R12 của CORVEN |

## 📗 Buổi 4 / 5 / 7 / 8 — (soạn chi tiết khi tới, giữ đúng 3 mức)

- **Buổi 4 (single print / fixer):** tìm 1 SP chưa fix → theo dõi **bao lâu mới được fix**, fix có **sạch**
  không, và market fix **theo đúng thứ tự tuần tự** không.
- **Buổi 5 (LVN/HVN):** dựng chart B (gộp 3 tuần). Đếm: giá vào **LVN** thì phiên đó Range lớn hay nhỏ?
  vào **HVN** thì sao? → kiểm luật «LVN⇒trend, HVN⇒sideway» bằng số.
- **Buổi 7 (break/reject):** đếm luật **break 2 lần** — trong N ca VA rời range, bao nhiêu ca lần 1 bị từ
  chối rồi lần 2 mới là clean break?
- **Buổi 8 (entry):** vùng hấp thụ đọc bằng cột delta trên TPO → khi giá quay lại, đếm tỷ lệ **phản ứng**.

---

## 📊 Bảng theo dõi — luật nào ĐÃ đo, luật nào CHƯA

| Luật | Trạng thái | Số |
|---|---|---|
| IB range ≤1% ⇒ phiên sau breakout | ❌ **ngưỡng không áp được cho vàng** (IB trung vị 0,27%) | n=22, cần đổi sang phân vị |
| VA trong IB ⇒ phiên sau trend | ⏳ chưa đủ ca (n=1) | cần ≥60 phiên |
| Giá đóng ngoài VA ⇒ VA không hợp lệ | ⏳ 45% — nghi do neo sai phiên | cần export lại |
| HVN là vùng canh lệnh tốt | ❌ **đã đo, ngang mức ngẫu nhiên** (n=4–6) | cần n lớn hơn |
| Tail volume dày = scam | ⏳ chưa đo | cần per-level, có `fp_*.csv` |
| LVN ⇒ trend / HVN ⇒ sideway | ⏳ chưa đo | |
| Break 2 lần: lần 2 là clean break | ⏳ chưa đo | |
| Poor high/low ⇒ bị test lại | ⏳ chưa đo | đếm được từ CSV `TPO Up/Down` + High/Low |

> Quy tắc: luật ở trạng thái ⏳ hoặc ❌ thì **được dùng để đọc chart**, nhưng **không được code thành
> signal** và tôi **không được nói như thể đã kiểm định**.
