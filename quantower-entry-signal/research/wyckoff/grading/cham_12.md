# Chấm bài #12 — Tái phân phối (RE-DIST) · 2026-04-28 02:02 → 05:36 (78 nến M1)

**Điểm: 6/10** — Bài **đúng nhất lô**: Phase A chuẩn (đây là ST[A] duy nhất trong 6 bài thực sự test lại vùng climax), tên range đúng, SOW neo đúng cây VSA 12.38x, có LPSY[D] giữ được ngoài biên. Lỗi còn lại là **tỉ lệ Phase B/C bị đảo ngược** và mấy chỗ chú thích sai.

## Lỗi (nặng → nhẹ)

### 1. Phase C (24 nến) dài gấp 2,4 lần Phase B (10 nến) — luật vi phạm: L8 + L9 cùng lúc
- **Thuật toán gắn:** A=25 · **B=10** · **C=24** · D=9 · E=11.
- **Đúng phải là:** B dài nhất, C ngắn nhất. Phase B 10 nến nghĩa là "giai đoạn xây dựng nguyên nhân" gần như không tồn tại, trong khi "phase ngắn nhất" lại chiếm gần 1/3 range.
- **Đúng ra phải vẽ:** đoạn 03:28 → ~04:55 (giá trôi ngang rồi bò xuống dọc theo biên dưới) là **Phase B**; Phase C chỉ là nhịp hồi cuối cùng ngay trước cây SOW 05:06.
- **Dấu hiệu quyết định:** LPSY[C] gán tại 03:28 nhưng SOW mãi 05:06 — cách nhau 98 phút / 24 nến, trong đó giá còn đi ngang thêm cả một đoạn dài. Đúng lỗi Ca #8 nguồn 2.pdf: "Phase C của học viên vẽ quá rộng, bao cả phần cuối Phase B — Phase C chuẩn chỉ bắt đầu từ điểm test cuối cùng ngay trước SOS/SOW".
- **Nghi phạm trong thuật toán:** cùng nghi phạm với bài #07 — Phase C được mở tại nhãn LPSY[C] rồi kéo tới hết, không có ràng buộc "LPSY[C] phải là nhịp test **cuối cùng** trước cú phá". Cần: sau khi SOW xác nhận, **quét lại** tìm pivot ngược cuối cùng trong ~20 nến trước cây phá rồi dời mốc Phase C về đó.

### 2. Phiếu số liệu ghi mâu thuẫn về cây climax — lỗi trình bày/đo
- **Thuật toán ghi:** dòng đầu "Climax mở range: SC tại giá 4715.0, **VSA=0.92x**, biên độ nến 2.8 giá"; dòng dưới "Nhãn climax mang **VSA=5.07x**"; bảng sự kiện: `SC · 02:00 · 4715.8`.
- **Vấn đề:** nến mở range (02:02) là nến **XANH** (open 4715.0 → close 4717.8) với VSA 0.92x — **không đạt** cả hai điều kiện climax (VSA≥2.2x, biên độ ≥1.4× TB) và sai màu so với mục 3 điều kiện (3) "nến đỏ chặn move giảm".
- **Đúng phải là:** nến 02:00 (đỏ, VSA 5.07x, low 4715.8) mới là cây SC — và may là **nhãn đã đặt đúng ở đó**, bản vá #4 chạy đúng ở bài này. Nhưng dòng tiêu đề phiếu vẫn báo cáo cây 0.92x, gây hiểu nhầm là climax hỏng. Mức biên dưới 4715.0 lấy từ low nến 02:02 — chấp nhận được (cụm climax), nhưng phiếu cần in cả hai cho rõ.
- **Nghi phạm:** `render_range_for_grading.py` in `climax_bar` (nến mở range) thay vì `climax_ev` (nến mang nhãn) ở phần tóm tắt.

### 3. Chú thích "nỗ lực/kết quả cao nhất **trong Phase B**" lại chỉ vào nến của Phase D — lỗi đo
- **Thuật toán ghi:** "Nhịp nỗ lực/kết quả cao nhất trong Phase B: nến 25784..25792 (**05:06**), effort=2.60x, result=**66.87**, er=0.04".
- **Vấn đề:** 05:06 là đúng cây SOW, thuộc **Phase D** (05:06–05:17), không thuộc Phase B (03:00–03:25). Ngoài ra `result = biên độ/ATR = 66.87` là con số vô lý — ATR đang được tính trên phiên Á gần đứng yên nên mẫu số ≈0.
- **Nghi phạm:** chuỗi swing pivot dùng để tính chỉ số Phase B không bị kẹp trong biên thời gian của Phase B; và `result` cần chặn trần hoặc dùng ATR có sàn.

### 4. AR định nghĩa biên chính trên bằng một nến VSA 0.25x, thân 0.00
- **Thuật toán gắn:** AR 02:16, 4728.5, VSA 0.25x.
- **Đúng phải là:** cú bật ngược 13,5 giá mà nỗ lực bằng 1/4 trung bình thì tối thiểu phải gắn cờ "(yếu)". Lỗi lặp ở cả 4 bài #08/#10/#11/#12 — `ar_vsa` đã đo (v6 mục 9) nhưng chưa dùng.

### 5. Không có biên phụ nào (tỷ lệ 1.00x) nên tiêu chí "SOW phải bứt qua biên phụ" không kiểm được gì
Không phải lỗi — chỉ ghi nhận: cả range không có ai thò được ra ngoài biên chính trước cú phá, nên biên phụ trùng biên chính. Trường hợp này SOW vẫn hợp lệ vì đóng cửa dưới biên chính 13,6 giá và giữ được.

## Đạt
- **Mục 1 (L1):** MOVE giảm 33.1 giá / 58 nến, hiệu suất 0.43; cây 02:00 VSA 5.07x đúng là chỗ move bị chặn, đúng đáy. Chuẩn.
- **Mục 2 (L2) — đạt tốt nhất lô:** đủ 3 lần đổi hướng, và **ST[A] 02:59 tại 4717.4 chỉ cách climax 4715.0 đúng 2.4 giá (18% chiều cao)** — đây mới là một cú test lại vùng climax thật sự, khác hẳn bài #08/#09/#11. Phase A kết đúng tại ST[A].
- **Mục 3 (L3):** biên chính 4715.0–4728.5 cố định suốt range, không kéo theo giá.
- **Mục 4 (L4):** SC chặn move giảm + phá thật xuống ⇒ **Tái phân phối**. Đúng bảng 4 pattern; đây chính là ca mà bản cũ hay xoá oan.
- **Mục 7 (L10):** SOW 05:06 (VSA **12.38x**, thân 0.63) → LPSY[D] 05:10 hồi lên 4703.4 nhưng **giữ nguyên dưới biên** → Phase E giá đi tiếp xuống 4682. Đúng khuôn CBR.
- **Mục 8:** cây SOW là thanh volume cao nhất cả chart — effort khớp result, đọc được ngay trên panel.
- **Mục 6 (L8) về loại nhãn:** không có shock giả nào bị gán bừa thành Spring/UTAD; case khó xử lý bằng LPSY[C] gán ngược — đúng hướng, chỉ sai vị trí (lỗi 1).
