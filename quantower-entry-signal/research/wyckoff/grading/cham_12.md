# Chấm bài #12 — Tái phân phối (RE-DIST) · 2026-04-28 02:02 → 05:36 (78 nến M1)

**Điểm: 7/10** — **bài đúng nhất trong lô 07-12.** Vùng cân bằng thật, Phase A chuẩn, biên không phình, SOW là cây phá đúng nghĩa. Chỉ thiếu Phase C và sai ở tầng chỉ số.

## Lỗi (nặng → nhẹ)

### 1. Thiếu hẳn Phase C dù có SOW — luật vi phạm: L8 + mục 6 (case khó bắt buộc gán ngược LPSY[C])
- **Thuật toán gắn:** dải phase A (25n) → B (34n) → **D** (9n) → E (11n). Không nhãn LPSY[C] nào.
- **Đúng phải là:** spec nói rõ khi SOW bắn ra mà range chưa có Phase C thì nhìn ngược lấy nhịp test cuối cùng (đỉnh cao nhất) làm **LPSY[C]**. Trên ảnh có ứng viên rõ: nhịp bò lên ~4720-4722 quanh **04:40-04:50** rồi trượt xuống 4713 trước khi cây SOW nổ — đó là đợt phục hồi yếu cuối cùng, đúng định nghĩa LPSY (THEORY §4.1: "đợt phục hồi yếu trên biên hẹp → nguồn cầu cạn kiệt, đợt bán cuối của CO").
- **Dấu hiệu quyết định trên chart:** đoạn 03:31 → 04:59 trên ảnh là dãy nến nhỏ **đỉnh thấp dần** (4726 → 4722 → 4718 → 4714) áp sát biên dưới 4715.0, volume co lại (panel dưới gần trống) — cung không cần nỗ lực mà giá vẫn trượt. Nhịp cuối của dãy đó là LPSY[C].
- **Nghi phạm trong thuật toán:** cửa sổ gán ngược = min(60, 1/2 Phase B) = min(60, 17) = **17 nến**, và bên trong đó còn phải có swing pivot xác nhận 5 nến với sàn 1.5× biên độ TB. Dãy đỉnh thấp dần ở phiên Á có nhịp chỉ 2-4 giá nên trượt sàn. Lỗi lặp ở #09, #11, #12 → **3/6 bài trong lô thiếu Phase C**: đây là lỗi hệ thống, không phải lỗi lẻ.

### 2. Mức climax lấy từ nến XANH, sai điều kiện màu — luật vi phạm: mục 3 điều kiện (3) của chính spec
- **Thuật toán gắn:** mức climax (biên chính dưới) = **4715.0**, lấy từ nến 02:02 — nến này O=4715.0 **C=4717.8**, tức nến **XANH**, VSA chỉ **0.92x**; nhãn SC thì đặt ở nến 02:00 (đỏ, VSA 5.07x, low 4715.8).
- **Đúng phải là:** cây quyết định là **02:00** (đỏ, volume 19 so với 2-7 của các nến quanh) — đó là cây chặn move. Việc lấy **low thấp nhất của cụm** (4715.0) làm mức là hợp lý về mặt biên; nhưng nến định mức đang là nến bật ngược đầu tiên, tức cơ chế "cụm climax" đang lan sang cả nhịp hồi. Sai lệch ở đây chỉ **0.8 giá** nên không ảnh hưởng kết luận — khác hẳn bài #08 nơi cùng cơ chế này gây lệch **23 giá**.
- **Dấu hiệu quyết định trên chart:** chấm SC nằm ở đúng chân cụm, sát đường "biên CHÍNH dưới 4715.0" — nhìn mắt thì đúng, chỉ sai về nến nào được dùng.
- **Nghi phạm trong thuật toán:** cửa sổ cụm climax 8 nến không ràng buộc màu nến / hướng. Vá cùng chỗ với lỗi #2 của bài #08.

### 3. Chỉ số nỗ lực/kết quả: mẫu số ATR phình vô nghĩa + nhãn đảo dấu — lỗi chỉ số
- **Thuật toán gắn:** effort 2.60x, **result (biên độ/ATR) = 66.87**, er = 0.04 → in nhãn "vùng hấp thụ **NGHI VẤN** (volume nhiều, kết quả ít)".
- **Đúng phải là:** hai lỗi cùng lúc. (a) result = **66.87 lần ATR** là con số không dùng được — ATR trong đoạn phiên Á trước đó gần 0 (nhiều nến biên độ 0-1 giá) nên tỷ số phình vỡ thang đo. (b) er = 0.04 nghĩa nỗ lực **rất nhỏ** mà kết quả **rất lớn** — đó là dấu hiệu **cạn nguồn cầu**, giá rơi không cần volume (THEORY §6.3), tức bằng chứng RE-DIST rất mạnh. Nhãn "volume nhiều, kết quả ít" nói **ngược lại**.
- **Nghi phạm trong thuật toán:** chuỗi diễn giải in cứng không phân ngưỡng er, và mẫu số ATR không có sàn tối thiểu. Lỗi lặp ở cả 6 bài lô này.

### 4. Chỉ có 78 nến M1 mà đủ A→E — cần kiểm bằng thời gian lịch, không bằng số nến — cảm nhận cá nhân có luật chống lưng một nửa (tiêu chí "range quá vụn")
- **Thuật toán gắn:** 78 nến với A=25, B=34, D=9, E=11.
- **Đúng phải là:** **ở bài này thì OK** — 78 nến trải **3,5 giờ lịch** và ảnh cho thấy giá thật sự đi ngang trong dải 4713-4728 suốt 3 giờ. Đây là vùng đấu giá thật, chỉ là dữ liệu thưa vì phiên Á. Nhưng phiếu số liệu không nói điều đó; nếu chỉ đọc "78 nến, đủ 4 phase" thì phải nghi nhiễu. **Đề nghị trình bày:** in thêm độ dài phase theo **phút lịch** cạnh số nến.
- **Nghi phạm trong thuật toán:** không phải lỗi logic, là lỗi phiếu số liệu / hiển thị.

## Đạt
- **Mục 1 (L1):** MOVE thật 33.1 giá / 58 nến, hiệu suất 0.43; đường xám trên ảnh đi từ 4748 xuống đúng chân SC, liên tục trong cùng phiên (**không** bắc khe như bài #11). Climax là đáy thấp nhất cửa sổ, đang chặn move.
- **Mục 2 (L2) — làm tốt nhất cả lô:** đủ đúng 3 lần đổi hướng và **ST[A] 02:59 tại 4717.4 test lại đúng vùng climax 4715.0** (cách 2.4 giá = 18% chiều cao range), VSA 0.59x (volume co lại đúng như THEORY §3.3 mô tả ST). Phase A kết thúc **đúng tại ST[A]**.
- **Mục 3 (L3):** biên chính = climax + AR = 4715.0-4728.5; **biên phụ trùng biên chính (tỷ lệ 1.00x)** — nghĩa là suốt 59 nến Phase A+B giá chưa một lần thò ra ngoài. Vẽ trung thực, không kéo biên theo giá.
- **Mục 4 (L4):** SC + phá **xuống** = **Tái phân phối**. Đúng — và đây chính là loại range mà bản trước v4 xoá oan (mục 5.2 tài liệu thuật toán).
- **Mục 5 (L9):** Phase B = 34 nến, dài nhất trong A/B/D/E. Đúng tỷ lệ.
- **Mục 7-8 (L10) — SOW mẫu mực:** SOW 05:06 tại 4701.4, **VSA 12.38x**, thân 0.63, đóng cửa **13.6 giá dưới biên** = **100% chiều cao range trong một nến**, và bứt qua cả biên phụ (biên phụ trùng biên chính). Effort **và** result đều nổ cùng lúc — đúng THEORY §2.2. Nhãn neo đúng cây phá, không rơi vào nến xác nhận thứ 3.
- **LPSY[D] 05:10 tại 4703.4** (VSA 0.47x): nhịp hồi nhỏ, volume co, **giữ được ở ngoài biên** rồi đi tiếp — đúng CBR, và đúng L7 (một điểm duy nhất, không vẽ vùng). Không lẫn vai với LPSY[C].
- **Phase E 11 nến:** giá đi từ 4701 xuống ~4672, tức **hơn 2× chiều cao range** → đóng range đúng luật, Phase E có độ dài thật (không còn 1 nến như lỗi J).
- **Chỉ số SOT + bias đo ĐÚNG bản chất:** SOT-up "chớm" n=2 (thrust ratio 0.52 = đỉnh rút ngắn còn nửa) kết hợp bias **-1** (chạm nổi biên dưới, không nổi biên trên) → hai chỉ số cùng chỉ về **cung áp đảo, sắp phá xuống**, và range đúng là phá xuống. Đây là ca cho thấy 3 chỉ số Phase B mới có giá trị thật khi mẫu số không bị phiên chết làm vỡ.
