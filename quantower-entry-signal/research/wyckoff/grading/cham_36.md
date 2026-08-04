# Chấm bài #36 — Tái phân phối (RE-DIST) · 2026-06-23 00:22 → 03:18 (176 nến M1)

**Điểm: 5/10** — khung range và tên gọi đúng, cú SOW đọc đúng; nhưng bỏ mất Phase C ngay tại cây quan trọng nhất của cả cấu trúc, và ST[A] chốt Phase A quá sớm.

## Lỗi (nặng → nhẹ)

### 1. Bỏ mất Phase C — chính cây mSOS mới là cú rũ của cấu trúc — luật vi phạm: L8, L3
- **Thuật toán gắn:** mSOS tại 01:00, giá 4216.0, VSA **5.23x**, thân **0.06** → xếp vào Phase B, timeline A → B → D → E, không có Phase C.
- **Đúng phải là:** trong một range tái phân phối, cú rũ ở Phase C nằm ở **biên trên**. Cây 01:00 vượt biên chính trên (4212.7) lên 4216.0 với volume 5.23× và **thân chỉ 6%** — toàn râu — rồi giá lộn cổ 30 giá liền sau đó. Đó là cú test cầu cuối cùng: **UTAD (hoặc UT + LPSY[C])**, và Phase C phải bắt đầu tại đây. Nếu không muốn gọi UTAD thì tối thiểu phải gán ngược LPSY[C] khi SOW bắn ra ở 01:37 (spec mục 6, case khó).
- **Dấu hiệu quyết định trên chart:** trên ảnh, thanh volume vàng cao nhất cả khung nằm đúng dưới cây 01:00, còn nến thì gần như chỉ có râu chọc lên trên đường nét đứt "biên phụ trên 4216.0". Nỗ lực cực lớn, kết quả bằng không — đúng định nghĩa Effort ≠ Result (THEORY §2.2).
- **Nghi phạm trong thuật toán:** bảng mục 5.1 quy định cú phá ở **cạnh AR** thì "không quyết định" cú rũ, chỉ được là mSOS/UA. Nhưng ở range xuất phát từ SC mà kết cục là phá **xuống**, cạnh AR chính là cạnh mà cú rũ phải xảy ra. Luật "chỉ cạnh climax mới sinh cú rũ" đúng cho tích luỹ/phân phối nhưng **sai cho tái tích luỹ/tái phân phối** — đây là lỗ hổng của L4 khi ánh xạ vào mục 5.1.

### 2. ST[A] không quay về vùng climax, Phase A chốt sớm — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] tại 00:50, giá 4207.3, chỉ **5 nến** sau AR (00:45, 4212.7).
- **Đúng phải là:** ST[A] là lần đổi hướng thứ 3, phải quay về **phía climax** (4196.0) và bị chặn lần nữa ở đó. 4207.3 = (4207.3−4196)/16.7 = **68% chiều cao**, tức chỉ lùi 5.4 giá từ AR. Đó là nhịp thở của cây AR, không phải một cú test.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn ST[A] dính sát nhãn AR, cùng một cụm nến; VSA nến ST[A] chỉ 0.48x, thân 0.21 — nến bé xíu, không phải một điểm dừng cấu trúc.
- **Nghi phạm trong thuật toán:** mục 4.2 — swing pivot 5 nến + sàn 1.5× biên độ TB bắt nhịp lùi đầu tiên. Ở đây sàn 1.5× ATR quá thấp so với range 16.7 giá nên một nhịp 5.4 giá đã qua. THEORY §5 có một dòng bảo lãnh nhẹ ("ST ở 1/3 nửa trên = phe mua rất mạnh") nhưng 68% chỉ vừa chạm mốc đó và L2 của người học đòi "test lại vùng climax" — vẫn tính là sai.

### 3. Phase D thiếu nhãn LPSY[D], dài 7 nến — luật vi phạm: L10, L7
- **Thuật toán gắn:** Phase D = 01:37 → 01:43 (7 nến), bảng sự kiện không có LPSY[D].
- **Đúng phải là:** CBR = phá → hồi retest **giữ được** ngoài biên → đi tiếp. Trên ảnh, sau SOW giá xuống ~4176 rồi bật lên ~4182 trước khi rơi tiếp — đó là nhịp retest, phải chấm LPSY[D] một điểm tại đỉnh nhịp bật đó và Phase D phải bao trọn nó. Phase D 7 nến ngắn hơn cả Phase A (29 nến).
- **Nghi phạm trong thuật toán:** LPS[D]/LPSY[D] đo bằng swing pivot 5 nến trong cửa sổ 25 nến (mục 7 câu 2); nhịp bật ở đây có thể chưa đủ 1.5× biên độ TB nên bị bỏ, và Phase E mở ngay khi giá đi đủ xa → Phase D không bao được nhịp retest như spec hứa.

### 4. Chỉ số SOT báo "chớm" ở n=2, sớm hơn định nghĩa gốc — mục THEORY §7
- **Thuật toán gắn:** SOT-up = `chớm`, n=2, thrust cuối/đầu 0.49, volume 1.02 → "HẤP THỤ".
- **Đúng phải là:** THEORY §7 nói rõ **cần ≥3 lần đẩy** trước khi SOT có ý nghĩa, "bắt đầu tìm SOT ở lần đẩy thứ 3-4 trở đi". n=2 chưa được phát ra thành trạng thái, dù chỉ là hiển thị — vì nó sẽ khiến người đọc chart tin có SOT ở nơi chỉ có 2 nhịp.
- **Ghi rõ:** đây là lỗi ĐO của chỉ số mới, không phải lỗi gate.

### 5. Chú giải nhịp nỗ lực/kết quả nói ngược — lỗi trình bày chỉ số (v6)
- **Thuật toán gắn:** nhịp 01:27, effort 1.18x, result 1.26, er = 0.94 → in "vung hap thu NGHI VAN (volume nhieu, ket qua it)".
- **Đúng phải là:** er = 0.94 là **nỗ lực ≈ kết quả**, tức cân bằng, không có gì đáng nghi. Đồng thời nhịp được chọn là nhịp **sai** — cây nỗ lực/kết quả lệch nhất cả Phase B là cây mSOS 01:00 (VSA 5.23x, thân 0.06) như đã nói ở lỗi 1.
- **Nghi phạm trong thuật toán:** chỉ số đo theo **nhịp** (trung bình VSA cả nhịp) nên một cây 5.23x bị pha loãng; và câu chú giải là chuỗi hardcode, in y hệt ở cả 5 bài lô này với er từ 0.13 tới 0.94.

## Đạt
- Điều kiện mở range (L1): MOVE giảm 17.6 giá / 44 nến, hiệu suất 0.43; trên ảnh là chuỗi nến đỏ bậc thang từ 4213 xuống 4196 — move thật, và nến climax 00:22 (đỏ, biên độ 4.3 giá, VSA 2.48x) đúng là cây chặn nó tại đáy.
- Biên chính = climax + AR (4196.0 / 4212.7), cố định, không kéo theo giá.
- Biên phụ đúng nghĩa L3: mỗi bên 1 cái, 4216.0 do mSOS tạo và 4188.0 do mSOW tạo — đều là cực trị xa nhất.
- Tên range đúng L4: origin SC + phá xuống thật = Tái phân phối.
- SOW (01:37, VSA 5.63x, thân 0.82) đóng cửa 4178.7 — **vượt qua biên phụ dưới 4188**, đúng yêu cầu "SOS/SOW mạnh phải bứt biên phụ" của L3.
- mSOW 01:21 xử lý đúng: cú phá xuống thất bại → ở lại Phase B, nới biên phụ, cú sau phải vượt qua chính nó.
- Bias = 0 khớp chart: range test cả hai biên (mSOS trên, mSOW dưới).
- Phase B (46 nến) dài nhất trong nhóm A/B/D — thoả L9 ở phần đo được.
