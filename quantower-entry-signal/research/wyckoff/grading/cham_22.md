# Chấm bài #22 — Tích luỹ (ACC) · 2026-05-26 11:43 → 13:52 (129 nến M1)

**Điểm: 6/10** — bài tốt nhất nhì lô: khung đúng, tên đúng, cú rũ và SOS đều rơi vào cây volume thật. Cần sửa tên cú rũ, vị trí nhãn climax và bổ sung nhãn cho Phase B/D.

## Lỗi (nặng → nhẹ)

### 1. "Spring" thực chất là Shakeout — luật vi phạm: L5
- **Thuật toán gắn:** Spring 12:31 tại 4533.1, VSA 3.31×.
- **Đúng phải là:** Shakeout. Trên chart cụm nến nằm dưới biên chính dưới 4538.0 kéo dài rõ hơn 10 nến (khoảng 12:28 → 12:40) trước khi giá thu về trong range; L5 chốt Spring là **≤ 3-4 nến**.
- **Dấu hiệu quyết định trên chart:** Phase C dài 18 nến mà cú rũ nằm ở nến đầu tiên của nó — nghĩa là giá mất gần trọn Phase C mới quay về, đúng mô tả "một SOW thất bại".
- **Nghi phạm trong thuật toán:** mốc 4 nến (`Spring ↔ Shakeout`) có thể đang đếm từ nến đóng cửa đầu tiên quay lại phía trong biên **chính**, trong khi cú rũ này vượt biên phụ và đo phải tính từ nến đầu tiên thò ra.

### 2. Nhãn SC nằm ngoài khung range — luật vi phạm: L3 (mốc mở range)
- **Thuật toán gắn:** SC tại 11:35 (VSA 5.62×), range bắt đầu 11:43, biên chính dưới 4538.0 lấy từ nến 11:43 (VSA 2.71×).
- **Đúng phải là:** khung range phải bắt đầu tại cây mang nhãn climax. Trên ảnh nhãn SC đứng bên trái vạch Phase A 8 nến.
- **Nghi phạm trong thuật toán:** như bài #21 — cụm climax dời **mốc range** tiến theo cực trị giá nhưng giữ **nhãn** ở cây VSA cao nhất; hai mốc không được kẹp lại với nhau (vá v7 #4 mới kẹp một chiều).

### 3. Phase C (18 nến) dài hơn Phase D (13 nến) — luật vi phạm: L8
- Không nặng như #19/#21 nhưng vẫn ngược luật "C là phase ngắn nhất". Nguyên nhân gốc trùng lỗi 1: cú rũ được coi là Spring nên Phase C mở quá sớm.

### 4. Phase B 32 nến không có một nhãn nào — nhãn thiếu
- Không có UT[B] / ST[B] dù trên chart giá chạm biên chính trên 4548.4 ít nhất hai lần (khoảng 12:10 và 12:22). Đúng theo mục 5.4 phải ghi 1 UT[B]. Phase D 13 nến cũng không có LPS[D] dù có nhịp lùi rõ sau SOS.

### 5. Biên phụ trên 4556.8 do chính cú phá tạo ra — luật vi phạm: L3
- Mức 4556.8 chỉ đạt được ở ranh giới Phase D/E (~12:53), tức sau khi SOS đã thành công. Biên phụ phải là dấu vết của một nỗ lực phá **thất bại**; ghi nhận cú phá thành công thành biên phụ làm SOS 4552.5 trông như "chưa vượt biên phụ".

## Đạt
- L1: MOVE 23.0 giá / 52 nến, hiệu suất 0.60, climax là đáy thấp nhất cửa sổ, VSA 2.71× với 130 hợp đồng — mở range chính đáng.
- L2: đủ 3 lần đổi hướng; ST[A] 4536.0 thọc nhẹ dưới climax 4538.0 rồi bị chặn — đúng chất một cú test, và đúng luật L3 khi tạo biên phụ.
- L3: biên chính 4538.0–4548.4 = climax + AR, cố định suốt range.
- L4: SC + phá lên = Tích luỹ, khớp chart (giá đi tiếp lên 4561).
- L9: Phase B 32 nến — dài nhất trong A–D.
- L10: SOS 12:49 VSA 2.15× thân 0.67, Phase E 51 nến, giá rời hẳn range đi tìm vùng mới.
- **Vá v7 #1 chạy đúng:** er=1.54 ≥ 1 → gọi hấp thụ; đúng dấu.
