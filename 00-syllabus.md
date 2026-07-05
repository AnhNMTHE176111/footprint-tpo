# 00 — Lộ trình học Footprint / Order Flow

> Học tuần tự. Đánh dấu `[x]` khi hoàn thành. Mỗi mục: **học → xem chart ví dụ → trả lời câu hỏi kiểm tra**.
> Ảnh chart: `course/images/bai-N/pNNN.png` · Text: `course/text/bai-N-*.md`

## 🧱 Bài 0 — Nền tảng (làm rõ nhanh trước khi vào Bài 1)
*(Người học đã biết nến/xu hướng/S-R. Phần này chỉ chốt các viên gạch của order flow.)*
- [x] Bid vs Ask (chào mua / chào bán) — giá khớp ở đâu
- [x] Lệnh **thị trường (market)** = chủ động vs lệnh **giới hạn (limit)** = thụ động
- [x] Vì sao "luôn có người mua = người bán" nhưng giá vẫn di chuyển (ai là người *chủ động*)
- [x] Một **ô (cell) Footprint** đọc thế nào: `Bid x Ask`

## 📗 Bài 1 — Delta Giải thích *(trang 1–41)*
- [x] Delta là gì: `Delta = KL mua chủ động (ở Ask) − KL bán chủ động (ở Bid)`
- [x] Delta dương / âm nói lên điều gì
- [x] Delta của 1 nến vs toàn thị trường
- [x] Tại sao Delta "kể câu chuyện" đằng sau cây nến
- [x] **Kiểm tra Bài 1** — Đạt 4/5 (2026-06-08)

## 📗 Bài 2 — Cách đọc Delta *(trang 42–68)*
- [x] Đọc Delta theo 2 tầm: 1 nến đơn vs chuỗi nhiều nến
- [x] 4 kiểu hiển thị Delta: ở-đáy · Nến Delta · Delta Footprint · Diagonal Footprint
- [x] Diagonal Footprint dùng để lọc Imbalance (mất cân đối)
- [x] **Kiểm tra Bài 2** — Đạt 3/3 + khởi động đúng (2026-06-09)

## 📗 Bài 3 — Số Delta *(trang 69–117)*
- [x] 5 con số Delta: Delta · Max Delta · Min Delta · Cumulative · Delta/Volume
- [x] Delta "sống" khi nến chưa đóng → không vào lệnh sớm
- [x] Đọc Max/Min vs Delta cuối để biết phe nào thống trị
- [x] Cumulative Delta là chỉ báo chậm — đừng dùng làm công tắc vào lệnh
- [x] Delta/Volume ≈0 = hấp thụ/đi ngang; >0,05 = mạnh
- [x] **Kiểm tra Bài 3** — Đạt 4/4 (2026-06-09)

## 📗 Bài 4 — Thiết lập Delta Trade *(trang 118–197)* — 7 setup, chia 4 phần
- [x] **P1:** Tổng quan 7 setup · Delta Surge · Delta Divergence (2026-06-10)
- [x] **P2:** Delta Flip · Delta Transition (2026-06-10)
- [x] **P3:** Delta Tails · Delta Bulges (2026-06-11)
- [x] **P4:** Delta Reversal · chốt bài (2026-06-15) — + đọc ô Footprint (Bid×Ask)
- [x] **Kiểm tra Bài 4** (tổng hợp 7 setup) — Đạt (2026-06-20)

## 📗 Bài 5 — Bài tập Delta & Tóm tắt *(trang 198–229)*
- [x] Khung tư duy tổng kết: 3 trạng thái delta–giá (xác nhận / hấp thụ / đuối-đảo) (2026-06-21)
- [x] Làm bài tập đọc chart — Exercise #3 (climax→Flip→đảo) + Exercise #5 (downtrend xác nhận + absorption) (2026-06-21)
- [x] Tổng ôn toàn khóa (2026-06-21)
- [x] Exercise #1 (delta xác nhận uptrend + Sell Reversal đỉnh) + #2 (V-bottom: climax→absorption→Flip) (2026-06-21)
- [ ] (tùy chọn) Làm thêm exercise #4/#6 để luyện mắt
- [ ] **Kiểm tra tổng hợp** (có thể gộp khi học ebook)

---

## 📙 Tham chiếu Ebook Order Flow *(đọc kèm khi cần đào sâu — `ebook/text/`)*
Các chủ đề chính (mục lục đầy đủ ở `ebook/text/00-muc-luc.md`):
- Thành phần thị trường: chủ động & thụ động
- Mô tả biểu đồ Footprint · ô xanh/đỏ · **HVN (High Volume Node)** · Delta
- **Volume Profile (Hồ sơ khối lượng)** · POC · Value Area · HVN/LVN ✅ *(P1)* · các hình dạng D/P/b/thin ✅ *(P2 — 2026-06-22)* · **3 setup VP (tích lũy/xu hướng/từ chối) ✅ *(2026-06-24)***
- Tính năng: Volume Cluster · **Imbalance ✅ · Stacked Imbalance ✅ *(2026-06-25)*** · Unfinished Business · Cumulative Delta
- **5 setup giao dịch:** Volume Cluster ✅ · Multiple Nodes ✅ · Trade Filter ✅ · Stacked Imbalance ✅ · Unfinished Business ✅ *(2026-06-29 — XONG cả 5)*
- **4 setup xác nhận ✅ XONG (2026-07-01):** Large Limit Orders ✅ · Absorption ✅ · Flow Orders & Delta ✅ · Cumulative Delta Divergence ✅
- **Quản lý lệnh ✅ XONG (2026-07-02):** Chốt lời theo volume ✅ · Chốt lời trailing (+ tín hiệu cảnh báo) ✅ · Dừng lỗ với order flow (3 cách + 10–20% ADR/ATR) ✅ · (Volume Profile tìm S/R đã học) → 🎉 **HẾT LÝ THUYẾT EBOOK → chuyển Giai đoạn 2: screen time**

> Gợi ý ghép: học **Delta** ở khóa chính (Bài 1-3) → khi tới **setup** (Bài 4) thì mở ebook phần "5 setup giao dịch" + "4 setup xác nhận" để đối chiếu chi tiết.

---

## 📕 Phụ lục TPO — Market Profile *(3 buổi nén, học ngay trước/đầu giai đoạn thực hành — soạn 2026-07-05)*
> Nguồn: sách Keppler *Profit With the Market Profile* bản dịch (`TPO - Market ProFile.pdf`) + tuyển tập TraderViet (`Market Profile _Vn.pdf`) + note thực chiến vàng 17 trang (`TPO.pdf`). Giáo trình đã soạn sẵn tại `tpo/text/`, ảnh chart tại `tpo/images/{keppler,tv,note}/` (tên file = trang PDF). Kiến thức trùng Volume Profile/order flow đã lược bỏ — chỉ còn phần MỚI.
- [ ] **Buổi 1 — Nền TPO & bản đồ trong phiên:** auction theory tinh gọn · cơ chế chart TPO (bracket 30', TPO-POC vs VPOC) · Initial Balance + Range Extension + chiếu mục tiêu IB/ADR · Tails + Single Print + playbook chờ retest · poor high/low (= UB nhìn bằng TPO) — `tpo/text/buoi-1-nen-tpo-ban-do-phien.md`
- [ ] **Buổi 2 — Hôm nay là ngày gì:** 6 day types + tiêu chí định lượng (A>B>C>D, quy tắc 5 TPO, bẫy DD vs Neutral) · 3 kịch bản giá mở vs VA hôm trước + 4 kiểu mở cửa Dalton · quy tắc 80% · xử lý phiên tin — `tpo/text/buoi-2-day-types-mo-cua-80.md`
- [ ] **Buổi 3 — Đa phiên & thực chiến vàng:** overnight/gap + quy giờ VN + logic Á→Âu→CME · value migration + POC clustering + composite · note thực chiến (fix profile, break 2 lần, delta fresh/tested, 2 ca GCQ23) · kick-off thực hành (sizing 2%, scaling out, SL cấu trúc, checklist trước phiên, nhật ký backtest) — `tpo/text/buoi-3-da-phien-thuc-chien-vang.md`
