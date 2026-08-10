# Chấm bài #01 — Chưa rõ (SC) (ACC?) · 2025-12-29 15:22 → 2025-12-31 21:55 (118 nến M1)

**Điểm: 1/10** — không nên vẽ range ở đây; và kể cả có vẽ thì nhãn SC đang nằm sai chỗ tới 134 giá.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC nằm NGOÀI range, cao hơn cả AR — luật vi phạm: L3 + THEORY §3.3 (SC = đáy)
- **Thuật toán gắn:** SC tại 2025-12-29 **13:42**, giá **4545.6**, VSA 3.64x.
- **Đúng phải là:** nến mở range là 15:22, đáy **4411.4** — đó mới là mức climax và là chỗ phải đặt nhãn SC.
- **Dấu hiệu quyết định trên chart:** nhãn SC vẽ **bên trái hẳn khung range**, ở giữa thân move giảm 107.8 giá, và ở giá **4545.6 > AR 4511.7**. Một "cao trào bán" nằm cao hơn đỉnh của cú bật ngược là mâu thuẫn logic hoàn toàn. Lệch **134.2 giá** so với biên chính dưới mà chính nó tạo ra.
- **Nghi phạm trong thuật toán:** nhánh "nhãn climax dời theo cây VSA cao nhất trong cụm" (v6 lỗi #1) — phiếu tự thú: *"Nhan climax mang VSA=3.64x ... KHONG can trung voi cuc tri gia"*. Cửa sổ cụm 8 nến đáng lẽ chỉ chạy **xuôi** từ nến mở range, ở đây nó quét **ngược** về quá khứ 100 phút. Đây đúng là lỗi #4 mà v7 tuyên bố đã kẹp cố định — **chưa vá được**.

### 2. Range không phải vùng đấu giá thật — chỉ là khe nghỉ lễ cuối năm — luật vi phạm: L1
- **Thuật toán gắn:** range 118 nến, cao 100.3 giá (2.27%), mở bằng nến volume **7 hợp đồng** (VSA 3.33x).
- **Đúng phải là:** không mở range. 118 nến M1 nhưng trải **2 ngày 6 giờ lịch** (29/12 → 31/12) — mật độ ~1 nến/28 phút, phần lớn nến volume 1-2 lot, biên độ 0. Bảng 12 nến quanh climax: volume 1,2,1,1,2,1 / climax 7 / rồi 1,1,1,1,1.
- **Dấu hiệu quyết định trên chart:** panel volume gần như phẳng suốt cả range, chỉ nổ vàng ở phần **sau khi range đã đóng** (01-02, 01-05). Một "cao trào" 7 lot không phải cao trào.
- **Nghi phạm:** người học đã chốt không dùng sàn khối lượng tuyệt đối (mục 12.1). Nhưng ở đây điều kiện **khe > 4 giờ cắt range** cũng không bắn dù range trải 2 ngày rưỡi — nên kiểm lại phép đo khe (có thể do dữ liệu có nến rải rác nên khe từng cặp < 4h).

### 3. Phase C (25n) DÀI HƠN Phase B (21n), Phase A (73n) dài nhất — luật vi phạm: L8 + L9
- **Thuật toán gắn:** A=73 · B=21 · C=25.
- **Đúng phải là:** B phải là phase dài nhất, C ngắn nhất. Ở đây A chiếm 62% cả range và C > B.
- **Dấu hiệu quyết định trên chart:** vạch tím Phase B nằm mãi tận 12-30 23:25, tức 3/4 chiều ngang khung là Phase A.
- **Nghi phạm:** AR chốt ở 12-30 12:22 (21 giờ sau climax) vì cơ chế swing pivot 5 nến trên dữ liệu thưa; không có trần độ dài Phase A tương đối so với Phase B.

### 4. ST[A] rơi lửng giữa range — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 4450.2, VSA 0.78x.
- **Đúng phải là:** ST[A] phải test lại **vùng climax 4411.4**. 4450.2 nằm ở **38.7% chiều cao** tính từ đáy, còn cách climax 38.8 giá.
- **Dấu hiệu quyết định:** hồi từ AR = 61.5/100.3 = 0.61× — **qua** ngưỡng mới 0.4 nhưng vẫn dừng giữa range. Ngưỡng mới siết sai chiều: nó ràng buộc khoảng cách tới **AR**, trong khi cái cần ràng buộc là khoảng cách tới **climax**.
- **Nghi phạm:** `STA_MIN_AR_FRAC` 0.2→0.4. Cần thêm điều kiện ngược: ST[A] phải nằm trong ~25-30% chiều cao tính từ mức climax.

### 5. Spring gán trên nến 1 lot, để pending rồi đóng range — luật vi phạm: L5 + L8
- **Thuật toán gắn:** Spring 4383.6, VSA **0.50x**, thân 0.00, trạng thái `pending`; range vẫn ghi `completed`.
- **Đúng phải là:** một cú rũ phải có dấu vết nỗ lực. VSA 0.50x (volume 1) không rũ được ai. Và một shock chưa xác nhận thì range chưa xong — không được đóng ở trạng thái "completed".
- **Dấu hiệu quyết định trên chart:** chấm Spring nằm ngay trên biên phụ nét đứt 4383.6, cây nến đó là một vạch đỏ mảnh không thân.

## Đạt
- Chú thích nỗ lực/kết quả: bài này không in dòng đó (Phase B không đủ pivot) — không sai.
- Biên phụ dưới 4383.6 do đúng cực trị xa nhất tạo ra, tỷ lệ 1.28x, mỗi bên đúng 1 cái (L3 đạt về hình thức).
- Cú phá tạo biên phụ vượt biên chính 27.8 giá (278 tick) — không còn ca "phá vài tick" như v6.
- Không đặt tên ép: giữ "Chưa rõ (SC)" khi chưa có SOS/SOW — trung thực (L4).

## Cần hỏi người học
- Có nên đặt sàn **mật độ dữ liệu** (số nến/giờ lịch) để chặn hẳn các range dựng trên phiên nghỉ lễ? Luật hiện có chỉ chặn khe > 4 giờ, không chặn được chuỗi nến thưa đều.
