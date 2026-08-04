# Chấm bài #28 — Tái phân phối (RE-DIST) · 2026-06-05 13:00 → 14:24 (84 nến M1)

**Điểm: 5/10** — Bài tốt nhất của lô: mở range đúng, tên đúng, cú SOW là cú phá thật đi rất xa. Nhưng nhãn SC vẽ lệch trọn một chiều cao range, Phase B chỉ 5 nến và thiếu hẳn Phase C — sửa nhãn, giữ range.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC vẽ ở 4446.6 = đúng mức AR, cách mức climax thật 21.4 giá — luật vi phạm: L3 (biên chính = mức climax), CHART_CASES Ca #12 nguồn 7.pdf (nhầm mốc gốc làm sai cả chuỗi)
- **Thuật toán gắn:** nhãn **SC** tại 12:52, giá 4446.6, VSA 4.58x — trong khi **mức** climax là 4425.2 (nến 13:00).
- **Đúng phải là:** nhãn cao trào phải nằm trong cụm cao trào ở **đáy**. 4446.6 trùng đúng mức **AR** (biên chính trên), tức nhãn SC được dán lên biên đối diện — cách mức nó tạo ra **trọn 100% chiều cao range**. Cây 12:52 nằm ở phần giữa move giảm, chưa phải cao trào; cụm cao trào thật là 12:59–13:00 (VSA 1.71x và 2.57x, volume 840 và 1421 — hai thanh volume lớn nhất đoạn).
- **Dấu hiệu quyết định trên chart:** nhãn đỏ "SC" nằm **trên** đường biên chính trên 4446.6, cao hơn cả AR, trong khi đường "biên CHÍNH dưới 4425.2" nằm ở đáy chart — chart tự nói nhãn sai chỗ.
- **Nghi phạm trong thuật toán:** cơ chế v6 "nhãn climax = cây volume cao nhất trong cụm, không cần trùng cực trị" có cửa sổ cụm nhìn **lùi quá xa** (tới nến −8), nên bắt được cây volume thuộc thân move. Cần chặn: nhãn climax chỉ được lấy trong các nến có cực trị nằm trong ~25% chiều cao range tính từ mức climax.

### 2. Phase B dài 5 nến — B là phase NGẮN NHẤT — luật vi phạm: L9
- **Thuật toán gắn:** A 32 · **B 5** · D 19 · E 29.
- **Đúng phải là:** L9 — Phase B dài nhất, là giai đoạn đọc nỗ lực ↔ kết quả. Ở đây B chỉ 5 nến, ngắn hơn cả Phase E. Nói cách khác cấu trúc này **không có Phase B**: giá chốt ST[A] xong là rơi luôn. Đọc đúng thì đây là một **nhịp pullback trong xu hướng giảm** (hồi 21 giá sau khi rơi 42 giá), rồi giảm tiếp — chỉ có Phase A rồi phá.
- **Dấu hiệu quyết định trên chart:** hai vạch tím "Phase B (5n)" và "Phase D (19n)" gần như chồng lên nhau; toàn bộ vùng đi ngang 4430–4446 nằm trong **Phase A (32 nến)**, tức nhịp đàm phán bị đóng khung sai vào Phase A.
- **Nghi phạm trong thuật toán:** ST[A] được xác nhận quá muộn (13:31, ngay sát cú phá 13:37) nên Phase A ăn hết đoạn đi ngang. Cây 13:31 là **cây thọc xuống 4423.3 VSA 2.34x thân 0.76** — đó không phải một cú *test* nhẹ, nó là cây khởi động cú sụp. Gọi nó ST[A] khiến A phình và B teo.

### 3. Có SOW mà không có Phase C — luật vi phạm: L8
- **Thuật toán gắn:** timeline A → B → **D**, không có dòng C.
- **Đúng phải là:** case khó thì phải gán ngược. Nhịp test cuối trước cú phá là đỉnh ~4436 lúc 13:33–13:35 (đợt hồi hụt sau khi mất 4440) — đó là **LPSY[C]**, Phase C từ đó tới nến SOW 13:37.
- **Dấu hiệu quyết định trên chart:** cụm 3 nến quanh 13:33 bật lên rồi bị chặn hẳn dưới vùng giữa range, ngay trước cây SOW thân 0.97.
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = min(60 nến, **1/2 độ dài Phase B**) = 2 nến. Phase B teo (lỗi 2) làm cửa sổ teo theo → không tìm nổi pivot. Nên dùng số nến tuyệt đối, đừng buộc vào độ dài Phase B.

### 4. Phase D 19 nến nhưng không có LPSY[D] nào — luật vi phạm: L10, L7
- **Thuật toán gắn:** Phase D 13:37→13:55, danh sách sự kiện chỉ có SOW.
- **Đúng phải là:** L10 (CBR) đòi có nhịp hồi retest **giữ được ngoài biên**. Trên chart, sau SOW có nhịp hồi lên vùng 4420–4423 (đúng biên phụ dưới 4423.3) quanh 13:41–13:45 rồi bị đạp tiếp — đó chính là **LPSY[D]**, và nó là bằng chứng đẹp nhất của bài này (retest đúng biên phụ, giữ được ở dưới, rồi đi tiếp). Bỏ mất nó là bỏ mất chỗ vào lệnh.
- **Nghi phạm trong thuật toán:** LPS[D]/LPSY[D] chỉ nhận **swing pivot 5 nến không cực trị mới**; nhịp hồi này bị cắt vì trong 5 nến đó giá vẫn tạo đáy mới. Nên nới: pivot 3 nến, hoặc lấy nhịp hồi **cao nhất** trong 25 nến cửa sổ.

### 5. Nhãn "AR (yếu)" hiển thị sai lý do — lỗi trình bày
- **Thuật toán gắn:** "AR (yếu)" tại 13:16, VSA 0.59x, thân 0.04.
- **Đúng phải là:** theo mục 4.1 tài liệu, nhãn "(yếu)" nghĩa là AR rơi vào **1–2 nến sát climax**. Ở đây AR cách climax **16 nến** và nhịp hồi tới 21.4 giá = một cú bật ngược rất thật. Cảnh báo "(yếu)" ở đây gây hiểu sai; nếu ý là "cây AR có thân mỏng/volume thấp" thì phải ghi lý do đó.
- **Nghi phạm trong thuật toán:** điều kiện gắn nhãn "(yếu)" đang xét sai đại lượng (thân/VSA của cây pivot thay vì khoảng cách tới climax), hoặc nhãn dùng chung cho hai trường hợp khác nhau.

### 6. Chỉ số nỗ lực/kết quả in nhãn ngược nghĩa (lỗi ĐO — lặp cả 5 bài)
- **Thuật toán gắn:** nến 13:37, effort 1.35x, result 4.30, er=0.31 → "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** er=0.31 = kết quả lớn hơn nỗ lực nhiều lần → đó là **cú phá trơn**, đúng vai SOW, không phải hấp thụ. Ngoài ra nến 13:37 chính là nến **SOW thuộc Phase D**, không thuộc Phase B — cửa sổ đo lấn phase.
- **Nghi phạm trong thuật toán:** chuỗi mô tả er in cứng không so ngưỡng; biên phải cửa sổ Phase B lấy mốc SOS/SOW thay vì mốc kết B.

## Đạt
- **L1 (mở range) — tốt nhất lô:** move giảm 42.2 giá / 40 nến, hiệu suất **0.68**, climax là đáy thật của cửa sổ, nến 13:00 volume 1421 (VSA 2.57x) chặn đứng move và bật ngay 12 giá ở nến sau. Điều kiện CẦN thoả rất rõ.
- **L2:** đủ 3 lần đổi hướng, Phase A kết đúng tại ST[A].
- **L3:** biên chính = climax 4425.2 + AR 4446.6, cố định. ST[A] thọc xuống 4423.3 tạo **biên phụ dưới 4423.3** — đúng luật "ST[A] vượt qua mức climax cũng tạo biên phụ", mỗi bên tối đa 1.
- **L4:** SC + phá xuống → **Tái phân phối**, đúng bảng 4 pattern. Đây đúng là "chỗ nghỉ giữa đợt giảm".
- **L5 / L10 (cú phá thật):** SOW đóng cửa **dưới biên phụ** 4423.3, VSA 2.92x, thân 0.97, và sau đó giá đi thêm ~58 giá (≈2.7× chiều cao range) xuống 4365 mà **không lần nào quay lại trong biên**. Đây là cú phá thật, Phase D/E hợp lệ.
- **Chỉ số bias = −1** (chỉ nới được biên dưới) khớp đúng hướng phá xuống. Đo đúng.
