# Cửu Âm Chân Kinh — plan (Fable, 2026-11-08)

> Yêu cầu người học (nguyên văn rút gọn): chuyển `cửu âm chân kinh.md` thành HTML đẹp, deploy GitHub Pages;
> trích setup **"follow theo footprint"** của CORVEN (range, phá vỡ, điều kiện, thế nào là đủ để entry) → brainstorm
> → cập nhật vào mục **2.2**. Hai phần: **(1) trang chính** = nhìn nhanh, 2.2 là **danh sách điều kiện ngắn** để check với
> chart khi trade; **(2) trang chi tiết** (nút "Chi tiết" cuối trang 1) = giải thích, ví dụ, ảnh, để đọc lại khi quên.
> Brainstorm / research / review = Fable. Implement + test (nội dung + UI) = Opus.

## 0. Nguồn đã đọc (research)
| Nguồn | Dùng cho |
|---|---|
| `cửu âm chân kinh.md` (người học viết, = `data-export/messages-with-pro-trader/CORVEN_TONG_HOP.md` do CORVEN tổng hợp 2026-11-02) | khung 3 kịch bản, lưu ý HVN, 2 ghi chú cuối |
| `corven-meet/2026-11-07/transcript.md` (26 mục, mốc giờ) + `frames/` | toàn bộ setup follow: range, phá, fail break, stacked, kiệt sức, bóng, delta, SL, R:R |
| `data-export/messages-with-pro-trader/TRUONG_LINH_3_KICH_BAN.md`, `CORVEN_SPEC_V1.md` §4 KB-C, `RULES.md` (R1 R3 R5 R7 R8 R9 R13 R14 W3 C3) | định nghĩa "move", nến đẩy chủ động (bóng 30 % dưới nến, delta xanh, thân đẹp), SL, bias phiên, "trong balance thì vả 2 cạnh / break ra là follow" |
| `quantower-range/research/RESEARCH.md` | 20 hộp range CORVEN vẽ: phá = đóng nến, râu = stop hunt |
| `daily-trading/HE-THONG-DEM-VANG.html`, `tram-dem-vang/deploy.sh`, memory `he-thong-dem-vang-pages` | mẫu giao diện + cách deploy Pages đã dùng |

## 1. Brainstorm — setup "follow theo footprint" của CORVEN là gì
CORVEN không có một "setup" đóng khung; ông đánh theo **bối cảnh → mốc → xác nhận → lệnh**. Ghép mọi câu lại thì ra
**một quy trình 4 bước + danh sách cấm**. Hai "thế" cùng nằm trong 2.2 vì cùng dùng footprint:
- **Thế A — TRONG range:** đánh 2 cạnh. Tín hiệu = fail break (đóng ngoài rồi đóng lại trong) + order flow tại cạnh → về cạnh đối diện.
  ("Trong balance thì xác định range rồi 2 cạnh mà vả thôi" — Messenger 8/2026; Meet 0:08:29, 0:56:49, 1:00:02.)
- **Thế B — SAU khi phá range / phá cấu trúc:** follow theo hướng phá, **không cản tàu**; vào ở nhịp hồi về mốc gần
  (cạnh vừa phá, stacked imbalance mới, đỉnh/đáy vừa gãy) khi order flow xác nhận. ("Giờ break ra là follow theo" — Messenger;
  Meet 0:17:58, 0:18:21, 0:20:31, 0:39:16.)

**Điều phân biệt "đủ để entry" (CORVEN nhấn nhiều lần):** không bao giờ một dấu hiệu đơn lẻ. Ông nói "kết hợp thêm cả bóng"
(0:07:01), "kết hợp với trap" (0:07:38), "kết hợp thêm range mà đánh" (0:07:47), "chơi những đoạn có nhiều tín hiệu cùng lúc"
(1:05:57), "đừng nhìn mỗi cái đấy… quan trọng phải phá được cấu trúc" (0:36:21). ⇒ Luật chốt: **bối cảnh đúng + giá ở mốc + ≥ 2 dấu
hiệu order flow cùng phe + nến đóng xác nhận + đủ 2R**.

### Mâu thuẫn trong nguồn và cách chốt (ghi vào trang chi tiết, không giấu)
| Vấn đề | Nguồn cũ | Nguồn mới | Chốt |
|---|---|---|---|
| R:R | 7/2026: "mỗi kịch bản cố định 1:3" (SPEC §1) | Meet 11/07 0:58:13–0:58:49: "không 2R thì không chơi… 1,7R được, TP vẫn 2R" | **Tối thiểu 2R (1,7R chấp nhận), TP đặt 2R.** Ghi chú bản 7/2026 nói 1:3. |
| SL | R7: 2–4 giá dưới cây M1 | Meet 0:50:25: "đặt gần thì dễ bị quét… đặt dưới cái đáy mới quét"; 0:51:16 "SL xa quá thì thôi" | **SL sau mốc quan trọng gần nhất (đáy/đỉnh vừa quét, cạnh range); không sát; xa quá không đủ 1,7R thì bỏ.** |
| Fail break | W3 (5/2026): "đừng đánh UT sớm, sang D mới đánh" | Meet: fail break → tìm tín hiệu ngược, "chờ 1–2 cây xem giữ được trong range không" (0:08:46), "phải vào lòng range" (1:00:02) | **Fail break một mình chưa đủ**: cần đóng lại trong range + xác nhận order flow + 2R tới cạnh đối diện. |
| Follow khi nào | "không cản tàu" | trong range thì không follow giữa lòng range (R13) | Follow chỉ **sau khi đã phá** (đóng nến + giữ được); trong range chỉ đánh cạnh. |

## 2. NỘI DUNG CHỐT — trang 1 (`index.html`), người học đọc khi đang nhìn chart
Giữ nguyên chữ của người học ở các mục 1, 2.1, lưu ý, ghi chú cuối (không viết lại ý của họ). Mục 2.2 thay bằng danh sách dưới.
Mỗi dòng là **một điều kiện kiểm được bằng mắt**, có thể tick; bấm vào dòng → nhảy tới mục tương ứng trang chi tiết.

**2.2 Follow theo Orderflow (không cản tàu)**

**① Bối cảnh — biết mình đang ở thế nào**
- [ ] Đã kẻ range của khung đang xem (rối thì lên M15). Biết giá đang **trong range** hay **đã phá** (phá = nến **đóng** ngoài cạnh, râu không tính).
- [ ] Trong range → chỉ đánh **2 cạnh**. Đã phá và giữ được 1–2 nến → chỉ **follow theo hướng phá**. Không follow giữa lòng range.
- [ ] Cấu trúc gần nhất còn giữ đúng hướng mình đánh (chưa có nến đóng qua đỉnh/đáy cấu trúc ngược lại).

**② Mốc — không đuổi giá, chờ giá về mốc gần**
- [ ] Giá đang ở **mốc gần**: cạnh range (hoặc cạnh vừa phá, retest), stacked imbalance **mới tạo** cùng hướng, đỉnh/đáy cấu trúc vừa gãy. Mốc xa / stacked đã bị chạm nhiều lần → bỏ.
- [ ] Nhịp test **không quá sâu**: không xuyên qua vùng stacked, không đóng ngược lại qua cạnh vừa phá. Đánh fail break thì giá phải **đã đóng lại trong lòng range**.

**③ Xác nhận tại mốc — cần ≥ 2 dấu hiệu cùng phe**
- [ ] **Delta đồng thuận và có lực**: cùng chiều giá, to và thẳng; delta nhỏ lình xình hoặc ngược giá → không vào.
- [ ] **Bóng đúng phe nổ ở mốc**: bóng xanh ở đáy nhịp hồi (buy) / bóng đỏ ở đỉnh nhịp hồi (sell), nằm ở phần nến phía mình đẩy.
- [ ] **Phe ngược kiệt sức** ở râu nến tại mốc (đáy: Bid ≈ 0 → buy; đỉnh: Ask ≈ 0 → sell) và chưa bị râu quét qua.
- [ ] **Stacked imbalance mới** cùng hướng vừa hình thành ở mốc (nằm giữa thân nến, giá đi tiếp sau đó).
- [ ] **Trap / stop hunt phe ngược** vừa xảy ra: râu quét mốc quan trọng + nổ bóng, rồi đẩy ngược về.
- [ ] **Nến xác nhận đã đóng**: thân vừa đủ, đóng sát cực trị, không rút râu dài. Sau fail break chờ 1–2 nến giữ được trong range.

**④ Lệnh**
- [ ] SL **sau mốc quan trọng gần nhất** (dưới đáy vừa quét / trên đỉnh yếu), không đặt sát.
- [ ] Từ điểm vào tới mục tiêu (cạnh đối diện / mốc kế) **≥ 2R** (1,7R chấp nhận). TP đặt 2R. Không đủ → không chơi, kể cả 1R.
- [ ] Đóng trong ngày, không nhồi lệnh.

**⛔ Không vào khi**
- Delta nhỏ, "buy không vào" (không có bóng) · Kiệt sức đang chống lại hướng mình đánh · Tín hiệu còn ngoài range
- Nhịp đẩy do quét stop (chạy mạnh, không đi xa) · Range chồng range, đoạn đi xấu · Đấu giá vừa xong (profile nhọn, đều 2 cạnh) → chờ break

Cuối trang: nút lớn **"Chi tiết 2.2 → ví dụ & ảnh"** → `chi-tiet.html`. Thêm nút nhỏ "Xoá tick" (tick không lưu).

### 2b. BẢN RÚT GỌN (chốt sau TEST-1, 2026-11-08) — THAY THẾ danh sách trên ở trang 1 và file md
Tester đo: bản trên chiếm ~3 màn hình điện thoại, không đọc được trong 30 giây. Rút mỗi dòng còn 1–2 dòng điện thoại;
phần giải thích dài chuyển hết sang trang chi tiết (trang 2 giữ nguyên chữ dài làm "điều kiện đầy đủ" ở đầu mỗi mục).
Giữ lại 2 câu gốc của CORVEN ngay dưới tiêu đề 2.2 (tester nhắc đúng: đó là chữ của người học, không được bỏ).

**2.2 Follow theo Orderflow (không cản tàu)**
> CORVEN: *khi follow phải để ý momentum · giá không được phép test quá sâu.*

**① Bối cảnh**
- [ ] Đã kẻ range (rối → M15). Trong range hay đã phá? Phá = nến **đóng** ngoài cạnh.
- [ ] Trong range → chỉ đánh 2 cạnh. Đã phá, giữ 1–2 nến → chỉ follow hướng phá.
- [ ] Cấu trúc gần nhất chưa gãy ngược hướng đánh.

**② Mốc — không đuổi giá**
- [ ] Giá ở **mốc gần**: cạnh range / cạnh vừa phá / stacked mới / đỉnh-đáy vừa gãy. Mốc xa → bỏ.
- [ ] Test **không quá sâu**: chưa xuyên stacked, chưa đóng ngược qua cạnh. Fail break: đã đóng lại trong range (hoặc xác nhận lần 2).

**③ Xác nhận tại mốc — cần ≥ 2**
- [ ] **Delta** cùng chiều, to và thẳng (nhỏ, lình xình, ngược giá → không).
- [ ] **Bóng** đúng phe nổ tại mốc (xanh ở đáy hồi → buy; đỏ ở đỉnh hồi → sell).
- [ ] **Phe ngược kiệt sức** ở râu (đáy Bid ≈ 0 → buy; đỉnh Ask ≈ 0 → sell), chưa bị quét qua.
- [ ] **Stacked imbalance mới** cùng hướng, nằm giữa thân nến.
- [ ] **Trap / stop hunt** phe ngược vừa xảy ra rồi đẩy ngược.

**④ Vào lệnh**
- [ ] **Nến xác nhận đã đóng**: thân đủ, đóng sát cực trị, không rút râu. Sau fail break chờ 1–2 nến.
- [ ] SL **sau mốc quan trọng gần nhất**, không đặt sát.
- [ ] Tới mục tiêu **≥ 2R** (1,7R chấp nhận), TP 2R. Không đủ → không chơi.
- [ ] Trong ngày, không nhồi.

**⛔ Không vào:** delta nhỏ / "buy không vào" · kiệt sức chống hướng đánh · tín hiệu còn ngoài range · nhịp đẩy do quét stop ·
range chồng range · đấu giá vừa xong → chờ break

Thay bộ đếm "x/14" bằng **phán quyết**: ① đủ 3 + ② đủ 2 + ③ ≥ 2 + ④ đủ 4 ⇒ huy hiệu xanh "ĐỦ ĐIỀU KIỆN"; chưa đủ ⇒ ghi thiếu gì
(vd "③ thiếu 1 dấu hiệu", "④ chưa có nến xác nhận"). Dòng ⛔ là chữ thường (không gạch chân), chỉ có một link nhỏ "›" cuối dòng.

## 3. NỘI DUNG CHỐT — trang 2 (`chi-tiet.html`), đọc lại khi quên
Cấu trúc: mục lục dính; mỗi điều kiện ở trang 1 là một mục cùng id (`#b1-range`, `#b2-moc`, `#b3-delta`…), gồm:
**Nguyên văn CORVEN** (chép đúng dòng trong `transcript.md`, kèm mốc giờ; không thêm ý) → **Cơ chế** (2–4 câu, ghi "diễn giải" nếu
không phải lời CORVEN) → **Nhìn trên chart** (ảnh cắt từ `frames/`, chú thích đọc số thật) → **Lỗi hay gặp** (1–2 dòng).

Mục bắt buộc và ảnh:
| Mục | Nguyên văn (mốc) | Ảnh (cắt vùng chart) |
|---|---|---|
| Range: kẻ thế nào, cạnh ở đâu, phá = đóng nến | 0:12:56, 0:14:50, 0:14:42, 0:13:58, 1:04:00, 1:04:25 | 0-40-40, 1-04-00 |
| Hai thế: trong range vả 2 cạnh / sau phá follow | Messenger "Trong balance… 2 cạnh mà vả", "Giờ break ra là follow theo" (TRANSCRIPT.md §13); Meet 0:16:29, 0:39:16, 0:40:00 | 0-46-05 |
| Fail break → tìm tín hiệu ngược; phải vào lòng range; chờ 1–2 nến | 0:08:05–0:08:46, 0:56:49, 0:59:37–1:00:09 | 0-07-55, 0-58-35, 0-59-50 |
| Cấu trúc: 1 nến đủ, phá phải giữ, rút râu = fail | 0:42:23, 0:43:09, 0:43:53, 0:40:46, 1:04:00 | 0-41-55 |
| Mốc gần: stacked imbalance làm mốc, dùng gần bỏ xa, vị trí trong nến | 0:06:54, 0:17:58–0:18:39, 0:19:38, 0:20:12, 1:05:32 | 0-18-00, 0-19-30 |
| Delta: đồng thuận, to thẳng, ngược giá = hấp thụ/kiệt sức | 0:31:42, 0:35:42–0:35:55, 0:45:48, 0:46:13 | 0-31-20, 0-35-50 |
| Bóng: đúng phe tại mốc; 3 hành vi của lệnh chủ động (bóng xanh không luôn = mua) | 0:46:03–0:46:13, 0:26:48, 0:27:22, 0:24:28 | 0-46-05, 0-25-10 |
| Kiệt sức: đỉnh Ask / đáy Bid, lấy ở râu, vô hiệu khi râu quét qua | 0:10:25, 0:33:14, 0:54:05–0:54:43 | 0-10-25, 0-53-30 |
| Trap / stop hunt | 0:23:45–0:24:34, 0:07:38, 0:09:42 | 0-24-15, 0-09-42 |
| SL | 0:50:18–0:51:25 | 0-50-25 |
| R:R 2R | 0:58:13–0:58:49 (+ ghi chú 1:3 bản 7/2026) | 0-58-35 |
| Ví dụ trọn vẹn 1: fail break đỉnh → sell (B06 21:04–21:33 ngày 05/11) | 0:56:49–0:58:49 | 0-58-35 |
| Ví dụ trọn vẹn 2: phá range → retest + stacked + đỉnh kiệt sức → sell | 0:20:31 | 0-19-30 |
| Ví dụ trọn vẹn 3: chưa vào lòng range → không vào; confirm lần 2 → vào | 0:59:37–1:00:09 | 0-59-50 |
| Bảng mâu thuẫn & cách chốt (mục 1 plan) | | |

⚠️ **Ảnh:** frames gốc có webcam + tên người (góc phải, thanh tab trình duyệt). Trang Pages là **công khai** ⇒ **chỉ cắt vùng chart**
(Sierra: khoảng x 48–1176, y 150–755 trên khung 1600×900; kiểm từng ảnh), **không để lộ mặt / tên / tab**. Ảnh Optimus Flow
(0-13-58) cắt bỏ thanh taskbar. Xuất JPG ≤ 250 KB, rộng 1128 px, đặt `img/<tên>.jpg`.

## 4. Thiết kế giao diện
- Hai file HTML tĩnh độc lập, dùng chung `style.css`; kiểu chữ/màu kế thừa `HE-THONG-DEM-VANG.html` (biến `--bg/--paper/--accent/--buy/--sell`,
  dark mode theo hệ thống, font Be Vietnam Pro + Archivo + JetBrains Mono). Rộng đọc 72ch, mobile 16 px gutter, không cuộn ngang.
- Trang 1: tiêu đề "Cửu Âm Chân Kinh" + dòng phụ "3 kịch bản đánh — theo CORVEN"; các khối: Lưu ý · KB1 · KB2 (2.1, **2.2 nổi bật**: nền
  accent nhạt, 4 nhóm ①–④ + ⛔, mỗi dòng có ô tick lớn ≥ 44 px, tap để tick, không lưu); ghi chú cuối; nút Chi tiết dính đáy trên
  điện thoại. Chữ 2.2 phải đọc được trong 30 giây: **≤ 18 dòng**, mỗi dòng ≤ 2 dòng màn hình điện thoại.
- Trang 2: mục lục dính, nút "← Trang chính" cố định, mỗi mục có `id` khớp link từ trang 1, ảnh có `loading="lazy"`, chú thích dưới ảnh.
- Thuật ngữ: tiếng Việt; **buy / sell / limit / market / sell limit / buy limit** giữ tiếng Anh; Ask/Bid khi nói cột footprint; không
  dùng "volatility", "aggressive/passive" (= chủ động/thụ động). Số dùng dấu phẩy thập phân (4.123,2 viết 4123,2).

## 5. Deploy
- Nguồn trong repo: `cuu-am-chan-kinh/` (`index.html`, `chi-tiet.html`, `style.css`, `img/`, `deploy.sh`, `.nojekyll`).
- Pages: repo công khai mới `AnhNMTHE176111/cuu-am-chan-kinh`, nhánh `main`, link dự kiến `https://anhnmthe176111.github.io/cuu-am-chan-kinh/`.
  `deploy.sh` theo mẫu `tram-dem-vang/deploy.sh` (clone vào `$HOME/.cuu-am-chan-kinh-pages`, chép file, commit, push).
- ⚠️ GitHub hiện chặn push (403 chưa xác minh email) ⇒ implement xong vẫn chạy deploy; nếu 403 thì báo người học, không làm gì khác.
- Cập nhật cả `cửu âm chân kinh.md` (mục 2.2 = danh sách ở mục 2 plan, dạng Markdown) để file gốc của người học khớp web.

## 6. Kiểm thử (agent tester Opus, độc lập với agent implement)
**Nội dung:** (a) mọi trích dẫn trong trang 2 phải tìm thấy **nguyên văn** trong `transcript.md` hoặc `TRANSCRIPT.md` đúng mốc giờ (script
so chuỗi); (b) 2.2 trang 1 khớp từng dòng mục 2 plan và khớp `cửu âm chân kinh.md`; (c) lint thuật ngữ: không có "mua/bán" thay cho
buy/sell ở nghĩa lệnh, không "volatility", không "aggressive"; (d) mục 1, 2.1, lưu ý, ghi chú cuối giữ đúng chữ người học;
(e) bảng mâu thuẫn có đủ 4 dòng; (f) ảnh: không ảnh nào chứa vùng webcam/tên (kiểm kích thước cắt + xem từng ảnh), mỗi ảnh ≤ 250 KB.
**UI:** Chrome headless chụp desktop 1280 và điện thoại 390 (nhúng iframe như memory ghi) cho cả 2 trang, sáng + tối; kiểm: không cuộn
ngang, chữ ≥ 14 px, ô tick bấm được (Playwright hoặc puppeteer nếu có; không có thì kiểm DOM bằng node + jsdom), mọi link
`index → chi-tiet#id` trỏ tới id tồn tại, nút quay lại hoạt động, ảnh tải được (không 404), HTML hợp lệ (không thẻ mở sai).
Biên bản: `cuu-am-chan-kinh/docs/TEST-1.md` + ảnh chụp `docs/shots/`.

## 7. Thứ tự làm
1. Opus implement theo plan (mục 2–5) → báo cáo. 2. Opus tester (mục 6) → TEST-1.md. 3. Fable review nội dung + ảnh chụp → sửa →
4. deploy + commit + push (báo 403 nếu có).
