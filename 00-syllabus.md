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
- [ ] **P4:** Delta Reversal · chốt bài
- [ ] **Kiểm tra Bài 4**

## 📗 Bài 5 — Bài tập Delta & Tóm tắt *(trang 198–229)*
- [ ] Làm bài tập đọc chart
- [ ] Tổng ôn toàn khóa
- [ ] **Kiểm tra tổng hợp**

---

## 📙 Tham chiếu Ebook Order Flow *(đọc kèm khi cần đào sâu — `ebook/text/`)*
Các chủ đề chính (mục lục đầy đủ ở `ebook/text/00-muc-luc.md`):
- Thành phần thị trường: chủ động & thụ động
- Mô tả biểu đồ Footprint · ô xanh/đỏ · **HVN (High Volume Node)** · Delta
- **Volume Profile (Hồ sơ khối lượng)** · POC · Value Area · các hình dạng D/P/b/thin
- Tính năng: **Volume Cluster, Imbalance, Stacked Imbalance, Unfinished Business, Cumulative Delta**
- **5 setup giao dịch:** Volume Cluster · Multiple Nodes · Trade Filter · Stacked Imbalance · Unfinished Business
- **4 setup xác nhận:** Large Limit Orders · Absorption · Flow Orders & Delta · Cumulative Delta Divergence
- Chốt lời (theo volume / trailing) · Dừng lỗ · tìm Hỗ trợ/Kháng cự bằng Volume Profile

> Gợi ý ghép: học **Delta** ở khóa chính (Bài 1-3) → khi tới **setup** (Bài 4) thì mở ebook phần "5 setup giao dịch" + "4 setup xác nhận" để đối chiếu chi tiết.
