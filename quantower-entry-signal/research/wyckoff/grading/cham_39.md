# Chấm bài #39 — Tích luỹ (ACC) · 2026-06-30 12:58 → 15:14 (136 nến M1)

**Điểm: 6/10** — khung range, biên, cú SOS và LPS[D] đều đúng; phải sửa 3 nhãn: SC bị gán lên một nến TĂNG, ST[A] rơi giữa range, và thiếu hẳn Phase C.

## Lỗi (nặng → nhẹ)

### 1. Nhãn SC gán lên một nến TĂNG volume cao — luật vi phạm: L1, spec mục 3(3), THEORY §3.3
- **Thuật toán gắn:** nhãn SC tại 13:00, giá 4022.9, VSA 3.33x. Nến 13:00 là **nến xanh**: O 4023.7 · H 4031.8 · L 4022.9 · C 4029.6, thân 0.66, volume 286.
- **Đúng phải là:** SC là **cao trào BÁN** — spec mục 3(3) ghi rõ "nến **đỏ** chặn một move giảm → SC, đánh dấu tại **đáy** nến". Nến 13:00 là cây cầu bật 7 giá lên khỏi đáy với volume cao nhất vùng — đó là nến **hấp thụ / khởi đầu AR**, không phải cao trào bán. Nhãn SC phải nằm ở nến 12:58 (đỏ, L 4022.1, VSA 2.60x) — đúng nơi mức biên chính dưới đang đứng.
- **Dấu hiệu quyết định trên chart:** trên ảnh nhãn SC nằm ở chân cụm nến, nhưng cây tương ứng nó là cây **xanh thân dài** đầu tiên của nhịp bật; thanh volume dưới cây đó màu xanh, không đỏ.
- **Nghi phạm trong thuật toán:** cơ chế "cây volume cao nhất trong cụm 8 nến" (v6) không ràng buộc cây được chọn phải **cùng hướng** với loại climax. Sửa: khi chọn cây mang nhãn trong cụm, chỉ xét các nến đỏ (với SC) / xanh (với BCLX).

### 2. Thiếu hoàn toàn Phase C — luật vi phạm: L8, mục 6 spec
- **Thuật toán gắn:** timeline A → B → D → E; bảng sự kiện chỉ có SC, AR, ST[A], SOS, LPS[D].
- **Đúng phải là:** SOS bắn 14:09 mà range chưa có Phase C thì phải gán ngược LPS[C]. Trên ảnh có một nhịp lùi rất rõ ngay trước cú bung: giá lên ~4046 khoảng 13:58 rồi lùi về ~4041 trong 4–5 nến (14:00–14:05) trước khi cây SOS nổ. Đó chính là **LPS[C]** — điểm hỗ trợ cuối trong range, và Phase C phải bắt đầu ở đó.
- **Dấu hiệu quyết định trên chart:** Phase B kết thúc 14:08, SOS ở 14:09 — không một nến nào thuộc Phase C.
- **Nghi phạm trong thuật toán:** lỗi lặp ở 4/5 bài lô này (#35, #36, #37, #39). Nhánh gán ngược Phase C (spec mục 6, cửa sổ min(60 nến, ½ Phase B), lấy swing pivot) không sinh nhãn. Nghi liên quan trực tiếp tới hai vá v6 "xoá LPS[C] mồ côi" và "Phase C kẹp trong range" — cần kiểm xem chúng có xoá luôn LPS[C] gán ngược hợp lệ hay không.

### 3. ST[A] rơi ở 43% chiều cao, không test vùng climax — luật vi phạm: L2
- **Thuật toán gắn:** ST[A] 13:24, giá 4033.0, chỉ **4 nến** sau AR (13:20, 4047.5).
- **Đúng phải là:** (4033.0−4022.1)/25.4 = **43% chiều cao** — giữa range. ST[A] phải quay về phía climax và bị chặn lần nữa ở đó. Nhịp đúng hơn là đáy 13:39 (~4027, tức 23% chiều cao), khi đó Phase A dài ~42 nến và có hình CHoCH thật.
- **Dấu hiệu quyết định trên chart:** nhãn ST[A] nằm lửng giữa hai đường cam; sau nó giá còn lùi tiếp xuống thấp hơn (~4027 ở 13:39) — tức nhịp mà máy chọn **không** phải điểm dừng của lần đổi hướng thứ 3.
- **Nghi phạm trong thuật toán:** mục 4.2 — swing pivot 5 nến + sàn 1.5× biên độ TB bắt nhịp lùi đầu tiên sau AR. Lỗi lặp 4/5 bài (48% · 68% · 62% · 43%). Cần thêm điều kiện tiệm cận vùng climax (ví dụ ≤1/3 chiều cao tính từ climax), chưa đạt thì Phase A chưa xong.

### 4. Chỉ số bias = 0 không khớp chart — lỗi ĐO của chỉ số mới (v6)
- **Thuật toán gắn:** bias = `+0`, chú giải "test CẢ HAI biên — ca THƯỜNG".
- **Đúng phải là:** trong Phase B (13:25–14:08) giá dao động khoảng 4027–4046: đỉnh cách biên trên 4047.5 chỉ ~1.5 giá, còn đáy cách biên dưới 4022.1 tới ~5 giá. Đó là bất đối xứng nghiêng lên — nên là **+1**, không phải 0. Chỉ số này sau đó lại khớp với kết cục (phá lên), tức nó đang bỏ mất chính thông tin hữu ích nhất của mình ở đây.
- **Nghi phạm trong thuật toán:** ngưỡng "chạm biên" (sai số 10 tick = 1 giá) khiến 1.5 giá bị coi là "không chạm" ngang hàng với 5 giá. Kiến nghị: in kèm **khoảng cách tiệm cận từng biên tính theo % chiều cao**, đừng chỉ trả 3 trạng thái −1/0/+1.

### 5. Chú giải nhịp nỗ lực/kết quả nói ngược dấu — lỗi trình bày chỉ số (v6)
- **Thuật toán gắn:** nhịp 14:00, effort 1.21x, result 2.16, er = 0.56 → in "vung hap thu NGHI VAN (volume nhieu, ket qua it)".
- **Đúng phải là:** effort 1.21x là volume hơi trên trung bình, result 2.16 là kết quả **lớn** → nỗ lực vừa mà kết quả lớn = **sức mạnh**, đúng với việc nhịp này nằm ngay trước cú SOS. Không có gì "nghi vấn". Chuỗi này in y hệt ở cả 5 bài lô này với er từ 0.13 tới 0.94 → hiện tại là chữ trang trí, không phải kết luận.
- **Nghi phạm trong thuật toán:** câu chú giải hardcode, thiếu ngưỡng phân loại theo er và thiếu chốt chiều của er.

### 6. SOT-dn báo "chớm" ở n=2, sớm hơn định nghĩa gốc — mục THEORY §7
- **Thuật toán gắn:** SOT-dn = `chớm`, n=2, thrust 0.52, volume 1.30 → "HẤP THỤ".
- **Đúng phải là:** THEORY §7 đòi **≥3 lần đẩy** mới bắt đầu tìm SOT. Ngoài ra ở bài này đáy thứ hai (~4027 ở 13:39) **sâu hơn** đáy thứ nhất (~4033 ở 13:24), tức chuỗi đáy không rút ngắn đơn điệu — cần in ra danh sách các mốc thrust đã dùng để kiểm được bằng mắt.

## Đạt
- Điều kiện mở range (L1): MOVE giảm **25.6 giá / 72 nến**, hiệu suất 0.37; trên ảnh là downtrend rõ từ 4050 (11:44) xuống 4022, và **mức** climax 4022.1 đúng là đáy chặn move (nhãn thì lệch — xem lỗi 1).
- AR 13:20 tại 4047.5, VSA 3.03x, thân 0.76 — cú bật ngược thật, 25.4 giá, neo vào thân nến chứ không râu.
- Biên chính = climax + AR, cố định suốt range; không có biên phụ (tỉ lệ 1.00x) — đúng L3, giá chưa từng thò ra ngoài biên chính trước cú phá nên không bịa nét đứt.
- **SOS 14:09 rất đúng bài:** giá 4058.0, VSA **4.17x** (thanh volume vàng cao nhất cả khung), thân 0.87, đóng cửa vượt biên trên 10.5 giá. Nhãn được neo hồi tố vào đúng cây phá, không rơi vào nến xác nhận thứ 3.
- LPS[D] 14:12 một điểm duy nhất (L7), giá 4051.6 vẫn **trên** biên trên 4047.5 → retest giữ được ngoài biên, đúng CBR của L10.
- Phase E (52 nến) đưa giá lên 4078, tức đi thêm ~30 giá > 1× chiều cao range 25.4 → đúng nghĩa "rời range đi tìm vùng giá mới".
- Phase B (44 nến) dài nhất trong nhóm A/B/D → thoả L9.
- Tên range đúng L4: origin SC + phá lên thật = Tích luỹ.
