# GĐ9 — Port sang `WyckoffRunner.cs` v7 + kiểm parity C# ↔ Python

| | |
|---|---|
| **Model** | **Opus 5** |
| **Effort** | **high** |
| **Cần trước** | GĐ8 phán quyết **CÓ ĐƯỢC PORT: CÓ** |
| **Chi phí** | trung bình |
| **Output** | `WyckoffRunner.cs` v7 (build sạch) + `research/wyckoff/PARITY_V7.md` |

Effort cao vì đây là chỗ **lỗi im lặng nhất**: Python nói WR 58%, C# bắn tín hiệu khác, và không ai biết cho
tới khi mất tiền. Không phải việc "dịch code" — là việc **chứng minh hai bên ra cùng tín hiệu**.

---

=== PROMPT ===

Việc của bạn: port cấu hình đã được GĐ8 đóng băng vào `quantower-entry-signal/WyckoffRunner.cs` (v7, 3 kịch bản) và **chứng minh parity** với engine Python. Output: file C# build sạch + `research/wyckoff/PARITY_V7.md`.

## Điều kiện tiên quyết
Mở `research/wyckoff/AUDIT_V7.md` trước. Nếu phán quyết là **KHÔNG được port** → **dừng ngay**, báo lại người
dùng, không port. Nếu PASS → **chỉ port đúng cấu hình đã đóng băng**, không tinh chỉnh thêm gì ở pha này.

## Đọc trước

1. `research/wyckoff/AUDIT_V7.md` — cấu hình đóng băng
2. `quantower-entry-signal/SPEC_V7_3KB.md` **§10 (bản đồ port sang C#)**
3. `research/wyckoff/v7/` — nguồn chân lý về thuật toán
4. `quantower-entry-signal/WyckoffRunner.cs` — file đích; đọc `Scan()`, `InDeadWindow()`, nhánh reversal,
   khối `InputParameter`, hàm ghi CSV tín hiệu
5. `quantower-entry-signal/build-wyckoff.sh`

## Việc phải làm

### 1. Port
- Thêm feature/kịch bản theo `SPEC §10`. Giữ **tên tiếng Việt** cho `InputParameter` như phong cách file hiện có.
- **Kiểm index `InputParameter` không trùng** — bắt buộc chạy và dán output:
  ```
  grep -oP 'InputParameter\("[^"]*",\s*\K\d+' WyckoffRunner.cs | sort -n | uniq -d
  ```
  Phải rỗng. (Đã từng trùng index 50–53 ngày 2026-07-29.)
- Feature thuộc `SPEC §8` (không kiểm được offline) → thêm được, nhưng **mặc định TẮT**, và ghi rõ trong
  comment là chưa từng được backtest.
- Cập nhật header comment của file cho đúng v7. Cập nhật `quantower-entry-signal/README.md`.
- Build: `./build-wyckoff.sh` → **0 warning / 0 error**. Không PASS thì chưa xong.

### 2. Parity — phần chính

**Phương pháp:** dùng đường xuất CSV tín hiệu đã có trong indicator (xem hàm ghi CSV trong `WyckoffRunner.cs`,
cột `nhanh=CBR/QUAY_DAU`) và so **từng tín hiệu** với output Python trên **cùng chuỗi nến**.

- Nếu chạy được C# trên Linux với dữ liệu file (theo cách `build-wyckoff.sh` + lõi test đã dùng trước đây) →
  làm trực tiếp.
- Nếu bắt buộc phải chạy trên Quantower Windows → viết sẵn **quy trình từng bước** cho người dùng làm trên
  máy Windows, kèm đúng tên file CSV cần lấy về và script so sánh đã viết sẵn ở
  `research/wyckoff/parity_v7.py`. Nói rõ với người dùng là parity **chưa hoàn tất** cho tới khi có CSV đó —
  không được tuyên bố parity dựa trên suy luận đọc code.

**Bảng so sánh phải có** (mỗi tín hiệu một dòng): `thời gian | phía | entry | SL | TP | kịch bản`, và cột
`khớp / chỉ có ở Python / chỉ có ở C# / lệch giá trị`.

**Tiêu chí:**
- Số tín hiệu lệch = **0** là mục tiêu.
- Lệch ≤ 2 tín hiệu trên ~30: được, nhưng **phải giải thích từng cái** (thường là biên warmup, reset VWAP,
  hoặc làm tròn tick).
- Lệch > 10% số tín hiệu → **FAIL**, phải tìm nguyên nhân, không được ship.

### 3. Các chỗ dễ lệch — kiểm riêng từng cái, ghi kết quả
1. **Múi giờ**: C# dùng `tUtc` hay `tUtc.AddHours(TzOffset)`? Python dùng UTC. Đây đúng là lỗi của v5.
2. **Warmup**: `VsaPeriod`, cửa sổ trend 480 nến, cửa sổ thanh khoản 1000 nến — hai bên bắt đầu tính từ nến nào?
3. **Reset VWAP theo phiên**: điều kiện gap (v5: gap > 30 phút) có giống nhau?
4. **Trung bình trượt thanh khoản**: cùng độ dài cửa sổ, cùng cách tính tiến dần?
5. **VSA ratio**: SMA20 có **bao gồm nến hiện tại** hay không? (v5: có).
6. **Làm tròn tick** và đơn vị "giá" (1 giá = 10 tick) — chỗ nào dùng tick, chỗ nào dùng giá.
7. **Nến-đóng-only**: C# có bắn khi nến chưa đóng không?
8. **Dedup / cooldown**: cùng quy tắc, cùng thứ tự áp?
9. **Dữ liệu nến**: C# đọc từ Quantower (có thể lọc nến rác khác dxFeed) — nêu rõ rủi ro này.

### 4. `PARITY_V7.md` phải có
1. Bảng so sánh từng tín hiệu + tổng kết (khớp / lệch / lý do)
2. Bảng 9 chỗ dễ lệch ở trên, mỗi dòng: `Python làm gì | C# làm gì | khớp?`
3. Output build (0 warning / 0 error) và output kiểm trùng index
4. Bảng `InputParameter` mới: index, tên hiển thị, mặc định, thuộc kịch bản nào, đã backtest chưa
5. Phán quyết: **parity ĐẠT / CHƯA ĐẠT**; nếu chưa đạt thì thiếu gì (thường là cần CSV từ máy Windows)
6. Mục **"khác biệt đã biết và chấp nhận"** — ghi rõ, đừng che

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **Không tuyên bố parity dựa trên đọc code.** Phải có bảng so sánh tín hiệu thật. Chưa có dữ liệu → ghi
   **"CHƯA ĐẠT — đang chờ CSV từ máy Windows"**.
3. **Không tinh chỉnh tham số ở pha này.** Chỉ port cấu hình đã đóng băng. Muốn đổi → quay lại GĐ6/GĐ7/GĐ8.
4. Repo **PUBLIC**: **token/chat_id Telegram để trống, người dùng tự điền tay** — không hardcode.
5. Không publish lên Claude Artifacts.
6. Xong → **commit + push `origin main`**.
7. Trung thực: chưa test live thì phải nói "chưa test live".

## Xong khi nào

- [ ] `WyckoffRunner.cs` v7 build `./build-wyckoff.sh` → **0 warning / 0 error**
- [ ] `grep` kiểm trùng index `InputParameter` → rỗng (dán output)
- [ ] Có bảng so sánh parity từng tín hiệu (hoặc quy trình + script sẵn sàng và ghi rõ CHƯA ĐẠT)
- [ ] Đã kiểm riêng **9 chỗ dễ lệch**
- [ ] Feature không kiểm được offline đều **mặc định TẮT** và có comment cảnh báo
- [ ] Header comment + README cập nhật lên v7
- [ ] `PARITY_V7.md` đủ 6 mục
- [ ] Đã commit + push

Cuối lượt báo: parity ĐẠT hay CHƯA ĐẠT (và thiếu gì), danh sách input mới, và các khác biệt đã biết & chấp nhận.
