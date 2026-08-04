# Chấm bài #27 — Phân phối (DIST) · 2026-06-10 06:08 → 08:02 (114 nến M1)

**Điểm: 4/10** — Đọc đúng hướng (đỉnh rồi đổ), nhưng range chỉ cao 14.4 giá / 114 nến mà nhét đủ 5 phase: đây là một đoạn ĐẢO CHIỀU bị cắt thành range, không phải một vùng đấu giá.

## Lỗi (nặng → nhẹ)

### 1. Range quá vụn — 14.4 giá, 114 nến, đủ A→E — luật vi phạm: mục "khung quá thô / range quá vụn" (CHART_CASES), L9
- **Thuật toán gắn:** một TR hoàn chỉnh Phase A(20) B(30) C(13) D(25) E(27).
- **Đúng phải là:** không vẽ range ở đây. Nhìn ảnh: giá đi lên một mạch từ 4196 tới 4245 rồi đổ một mạch xuống 4180 — cái gọi là "range" chỉ là **vùng bo đỉnh** giữa hai chân xu hướng, rộng 0.34% giá. Trong 114 nến đó giá không hề đàm phán qua lại: nó chỉ trượt dốc đều xuống (nhìn chuỗi nến từ 06:28 tới 07:11 là một cầu thang đỏ liên tục).
- **Dấu hiệu quyết định trên chart:** biên chính 4231.1–4245.5 = **14.4 giá**; Phase B chỉ **30 nến** trong khi Phase E **27 nến** — Phase B gần bằng Phase E là dấu hiệu không có giai đoạn xây nguyên nhân nào cả. Theo L9 Phase B phải là phase dài nhất; ở đây nó thua Phase D+E cộng lại (52 nến).
- **Nghi phạm trong thuật toán:** người học chốt "không đặt sàn độ dài tối thiểu cho range" (quyết định 1, mục 0b) — nhưng không có sàn nào thì mọi cú đảo chiều có 1 nến VSA>2.2x đều thành range. Cần một guard kiểu "chiều cao biên chính ≥ N× biên độ TB 20 nến" hoặc "Phase B phải là phase dài nhất, nếu không thì bỏ range".

### 2. Cây BCLX không phải cây climax — climax thật là cây kế tiếp — luật vi phạm: L1 (climax phải CHẶN move), §4.2 THEORY
- **Thuật toán gắn:** BCLX tại 4245.5 lúc 06:08, VSA 2.77x.
- **Đúng phải là:** cây 06:08 có biên độ **2.9 giá**, thân/biên **0.21** — một cây do dự, không phải cây cao trào. Cây thật sự chặn move là **06:09**: VSA 2.04x, thân 0.79, mở 4242.8 đóng 4236.9, tức cây đảo chiều dứt khoát. Nếu phải chọn một mốc BCLX thì lấy đỉnh 4245.5 nhưng nhãn phải neo hành vi ở cây 06:09.
- **Dấu hiệu quyết định trên chart:** so 3 cây liền: −1 (2.04x, thân 0.64, **xanh, đóng ở đỉnh** 4243.1) → +0 (2.77x, thân 0.21) → +1 (2.04x, thân 0.79, **đỏ**). Cây có volume cao nhất lại là cây thân nhỏ nhất — nỗ lực lớn, kết quả không có, đúng bài effort↔result, nhưng thuật toán chỉ dùng nó làm mốc chứ không đọc ra điều đó.
- **Nghi phạm trong thuật toán:** điều kiện mở range mục 3(1) chỉ đòi "biên độ ≥1.4× TB + VSA ≥2.2x", không đòi thân nến hay đóng cửa. Cây 2.9 giá thân 0.21 lọt được vì TB biên độ 20 nến lúc đó rất nhỏ.

### 3. SOW quá yếu để gọi là phá thật — luật vi phạm: L3 (SOS/SOW mạnh phải bứt biên PHỤ) + §4.2 THEORY (Phase D cần spread+volume tăng)
- **Thuật toán gắn:** SOW tại 4224.8 lúc 07:11, VSA **1.60x**, mở Phase D.
- **Đúng phải là:** 1.60x là volume **dưới ngưỡng climax 2.2x** và chỉ nhỉnh hơn trung bình. Cây phá biên phụ (4228.6) mà volume không nổi thì đó là "phá vì hết người mua", chưa phải MAJOR SOW. Đáng chú ý: cây có VSA cao nhất cả range là **mSOW 06:44 (2.42x)** — thuật toán lại hạ nó xuống minor.
- **Dấu hiệu quyết định trên chart:** panel volume — cụm thanh vàng (≥2.2x) lớn nhất nằm ở 06:08 và 06:44, còn tại 07:11 (chỗ gắn SOW) thanh volume thấp hơn hẳn. Cú sụp volume thật chỉ nổ lúc **08:00** (thanh vàng cao nhất chart), tức **sau khi range đã đóng**.
- **Nghi phạm trong thuật toán:** mục 5.1 kết cục B đặt nhãn hồi tố vào "cây VSA cao nhất trong đoạn" — nhưng đoạn xét quá ngắn nên cây được chọn vẫn chỉ 1.60x. Nên thêm sàn: cây được gắn SOS/SOW phải có VSA ≥ ngưỡng nào đó, nếu không thì hạ cấp thành mSOW.

### 4. LPSY[C] và mSOW cách nhau 6.7 giá nhưng LPSY[C] cao hơn mSOW — thứ tự sự kiện ngược — luật vi phạm: L8
- **Thuật toán gắn:** mSOW 4228.6 (06:44) rồi LPSY[C] 4229.3 (06:58).
- **Đúng phải là:** LPSY[C] là "đợt phục hồi yếu" sau mSOW thì hợp lý về vai, nhưng nó chỉ hồi lên **0.7 giá** so với mSOW và VSA 0.48x thân 0.12. Hồi 0.7 giá trong một range cao 14.4 giá (4.9%) thì không phải một nhịp test, chỉ là nến đi ngang. Phase C ở đây thực chất không tồn tại.
- **Dấu hiệu quyết định trên chart:** 4229.3 − 4228.6 = **0.7 giá**; hai nhãn nằm chồng lên nhau trên ảnh.
- **Nghi phạm trong thuật toán:** thiếu ngưỡng tối thiểu cho độ lớn nhịp hồi khi gán LPS/LPSY (mục 6 chỉ nói "giá quay về test đúng vùng điểm rũ").

## Đạt
- Mục 1 phần MOVE (L1): MOVE tăng 38.0 giá / 83 nến / hiệu suất 0.38 — có move thật, climax nằm đúng đỉnh của cửa sổ. Phần này không sai.
- Mục 2 (L2): đủ 3 lần đổi hướng, ST[A] 4239.2 quay về phía climax rồi bị chặn, Phase A chốt tại ST[A]. Cấu trúc CHoCH đúng.
- Mục 3 (L3): biên chính cố định, biên phụ dưới 4228.6 duy nhất, không có biên phụ trên. Đúng luật.
- Mục 4 (L4): origin BCLX + phá xuống = **Phân phối**. Tên đúng.
- Mục 9: LPSY[C]/LPSY[D] tách đúng trước/sau SOW; không spam nhãn.

## Kết luận cấu trúc
**Không nên vẽ range ở đây.** Đây là một đỉnh xoay (rounding top) 114 nến trong một chart mà giá vừa chạy 38 giá lên rồi chạy 65 giá xuống. Nếu muốn giữ, phải hạ cấp: gọi nó là vùng phân phối cục bộ, bỏ Phase C, và không gọi cây 1.60x là SOW. Đúng tinh thần Ca #20 nguồn 7.pdf — đừng gò dữ liệu cho khớp đủ 5 phase.
