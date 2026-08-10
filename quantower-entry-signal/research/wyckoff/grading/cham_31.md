# Chấm bài #31 — Tái phân phối (RE-DIST) · 2026-06-10 14:58 → 22:02 (364 nến M1)

**Điểm: 5/10** — Range vẽ đúng chỗ, tên đúng, nhưng nửa sau bài hỏng: SOW gọi muộn 65 nến, mất hẳn Phase C, Phase D chỉ 1 nến.

## Lỗi (nặng → nhẹ)

### 1. SOW gán muộn 65 nến, vào cây yếu — vi phạm mục "Nỗ lực ↔ Kết quả" (THEORY §2.2) + L10
- **Thuật toán gắn:** mSOW 18:50 tại 4120.2 (VSA **7.75x**, thân 0.88) → rồi mới bắn **SOW 19:55 tại 4107.4, VSA chỉ 2.60x**.
- **Đúng phải là:** cây 18:50 chính là SOW. Sau nó giá **không một lần** đóng cửa lại trên biên chính dưới 4139.7 — nhịp bật cao nhất trong đoạn 19:10-19:40 chỉ tới ~4117. Đã phá và **giữ** được ngoài biên thì theo đúng định nghĩa v6 nó không còn là mSOW.
- **Dấu hiệu quyết định trên chart:** cây 17:29 (VSA 6.89x) mới đáng bị hạ cấp — sau nó giá hồi lên ~4145, tức vào lại trong range. Cây 18:50 thì không. Hai cây nỗ lực 6.89x/7.75x bị bỏ, nhãn rơi vào cây 2.60x thấp hơn 13 giá.
- **Nghi phạm trong thuật toán:** điều kiện xác nhận phá thật vẫn đo bằng **biên phụ** (3 nến đóng vượt biên phụ + 30 tick). Biên phụ 4126.6 nằm quá sát vùng probe nên cú 18:50 không "vượt đủ", phải chờ tới 19:55. Mục 5.1 nói đã đổi mốc so sánh sang biên chính cho việc **đặt nhãn hồi tố**, nhưng mốc **xác nhận** thì chưa đổi.

### 2. Thiếu hẳn Phase C — vi phạm L8
- **Thuật toán gắn:** dải phase A → B → D → E, không có C.
- **Đúng phải là:** phải có LPSY[C]. Nhịp hồi 19:10-19:40 (bật từ 4113 lên ~4128 rồi tắt) chính là **đợt phục hồi yếu trước cú giảm cuối** — đúng định nghĩa LPSY của THEORY §4.1.
- **Nghi phạm trong thuật toán:** luật gán ngược Phase C (v6 mục 1.5) bắt pivot phải nằm **trong range và đúng nửa trên** khi phá xuống. Tại 60 nến trước SOW giá đã ở 4110-4130, tức **dưới hẳn range** → không tìm được pivot nào → bỏ Phase C. Ràng buộc "nửa trên" này **ngược với lý thuyết**: LPSY là nhịp hồi yếu **ở biên dưới**, không phải ở nửa trên range. Nới cửa sổ 0.5x→0.8x (vá v7) không cứu được vì cửa sổ đã là 60 nến trần; lỗi nằm ở ràng buộc vị trí, không ở độ dài cửa sổ.

### 3. Phase D dài đúng 1 nến, không có LPSY[D] — vi phạm L10
- **Thuật toán gắn:** D = 1 nến (19:55), E = 67 nến, không nhãn hồi test nào.
- **Đúng phải là:** D phải bao trọn nhịp retest. Sau cây phá 18:50 có nguyên một nhịp hồi lên ~4128 rồi bị chặn — đó là LPSY[D], và Phase D phải trải hết nhịp đó.
- **Nghi phạm:** hệ quả kéo theo của lỗi #1 — vì SOW bắn muộn tại 19:55, nhịp retest thật đã nằm **trước** mốc SOW nên không còn gì để tìm trong cửa sổ 25 nến sau đó.

### 4. Biên phụ dưới không nới theo cú thăm dò sâu hơn — vi phạm L3
- **Thuật toán gắn:** biên phụ dưới **4126.6**, trong khi mSOW 18:50 đã chạm **4120.2**.
- **Đúng phải là:** L3 — "có điểm xa hơn thì biên phụ cũ biến mất, biên phụ mới nới ra". Biên phụ dưới phải là 4120.2.
- **Dấu hiệu quyết định:** trên ảnh, chấm mSOW thứ hai nằm **thấp hơn** đường nét đứt 4126.6 — mắt thường thấy ngay.
- **Nghi phạm:** vá v6 lỗi #2 ("phía đang test chỉ nới một lần sau khi biết kết cục") — nhánh nới sau kết cục hình như không chạy khi cú thăm dò bị hạ cấp thành mSOW.

### 5. Nhãn SC rơi ra ngoài khung range và nằm giữa vùng giá — lỗi neo nhãn (v7 vá #4 chưa ăn)
- **Thuật toán gắn:** SC tại **14:56**, giá 4147.9 — trong khi range bắt đầu ở nến **14:58** và biên chính dưới là 4139.7.
- **Đúng phải là:** nhãn climax phải nằm **trong** khung range và tại mức nó tạo ra (đáy 4139.7). Hiện chấm SC lơ lửng giữa range, cách biên nó sinh ra 8.2 giá.
- **Nghi phạm:** kẹp nhãn "theo nến mở range cố định" chỉ chặn nhãn **trượt về sau**, không chặn nhãn nằm **trước** nến mở range. Cùng lỗi lặp ở bài #32 và #35 → lỗi hệ thống, không phải ca lẻ.

### 6. Phase B 275 nến chỉ có 2 nhãn, thiếu UT[B]
- Chart cho thấy giá chạm biên trên 4159 ít nhất 2 lần (16:12, 16:53) và chỉ số bias=+0 tự khai là "test cả hai biên" — nhưng không có một nhãn UT[B] nào. Nhãn thiếu (L6 chỉ bỏ ST[B], không bỏ UT).

## Đạt
- **Mục 1 (L1):** MOVE 53.1 giá / 65 nến / hiệu suất 0.37, climax là đáy của cả cửa sổ — điều kiện CẦN thoả thật, nhìn trên ảnh là một đợt rơi rõ ràng bị chặn.
- **Mục 2 (L2):** đủ 3 lần đổi hướng, Phase A 22 nến gọn, kết thúc đúng tại ST[A]; ST[A] 4135.9 thủng nhẹ mức climax 3.8 giá — vẫn là test hợp lệ.
- **Mục 4 (L4):** origin SC + phá xuống thật = **Tái phân phối** — gọi tên đúng bảng L4.
- **Mục 5 (L9):** Phase B 275/364 nến, dài nhất — đúng.
- **Mục 8:** chú thích nỗ lực/kết quả đọc er=4.79 (effort 0.94x, result 0.20) và gọi "hấp thụ nghi vấn" — **đúng dấu**, lỗi hard-code của v6 đã hết.
