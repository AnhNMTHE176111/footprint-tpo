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

## 📕 Phụ lục TPO — Market Profile

> ## 🔴 **2026-08-11: DẠY LẠI TPO THEO BẢN V2 → [`tpo/SYLLABUS-TPO.md`](tpo/SYLLABUS-TPO.md)**
> Người học tự đánh giá "TPO chưa được học kỹ". Rà lại thì phát hiện **2 lỗ hổng lớn** và **1 nguồn chưa
> hề dùng**:
> - **Lỗ hổng 1 — HÌNH DẠNG profile (D/P/b/B/chữ nhật/thin) áp lên TPO:** bản cũ CẮT vì "P/b chỉ là hình
>   dạng", nhưng câu đầu tiên CORVEN nói khi mở chart là *"Tpo thành chữ D"* → hình dạng là **input số 1**.
> - **Lỗ hổng 2 — BALANCE vs SAU BALANCE:** công tắc quyết định bật play nào; cùng một phân kỳ delta mang
>   nghĩa **trái ngược** tuỳ chế độ. Chưa có buổi nào dạy.
> - **Nguồn chưa dùng — `TPO.pdf` (17tr note thực chiến vàng):** ~30 luật hành vi cụ thể (fixer profile,
>   tail-scam theo volume, LVN⇒trend/HVN⇒sideway, accept breakout, chuỗi Á→Âu→CME…). ⚠️ chưa backtest.
>
> V2 gồm **9 buổi** theo chuỗi 6 câu hỏi CORVEN thực chạy (hình dạng → tail → single print → HVN → chế độ
> balance → break/reject → entry M1), kèm bảng **5 mâu thuẫn giữa sách và CORVEN** đã phân xử.
> Thứ tự dạy: **2 → 3 → 6 → 4 → 5 → 7 → 8 → 9**.

> Nguồn: sách Keppler *Profit With the Market Profile* bản dịch + tuyển tập TraderViet (`Market Profile _Vn.pdf`) + **note thực chiến vàng `TPO.pdf` 17tr** + chat CORVEN. Ảnh chart `tpo/images/{keppler,tv,note}/` (tên file = trang PDF).
>
> *(Bản cũ 2026-07-13 giữ làm tham chiếu — trục là IB + giá mở vs VA theo Dalton/Keppler.)*
- [~] **🎯 Lõi thực chiến — `tpo/text/00-tpo-loi-thuc-chien.md`** (dạy từ đây): chu kỳ TPO đặt đúng (Daily→30′, IB=2 bracket đầu=60′; M30→M1 chỉ là micro-profile, soi 1′ thì dùng footprint/delta) · **3 câu hỏi mỗi phiên** (mở vs VA · IB có đấu giá/RE không · niềm tin mở: Drive/Rotation/Rejection-Reverse) · 6 setup giữ lại (80% rule · tái nhập VA thất bại · single print retest · bear trap · kỷ luật trend day · tails/poor high-low) · checklist 2′ + phiên tin. **[2026-07-14: §1 — cả 3 câu KHÓA (giá mở ✅ · IB break ✅ · niềm tin mở ✅) → đang dạy §2 6 setup.]** **[2026-07-22: Batch A (80% rule + tái nhập VA thất bại) — người học TỰ XÁC NHẬN đã hiểu (kèm 3 diagram Pillow + trang note riêng `batch-A-80-rule-va-tai-nhap.md`) → đang dạy Batch B = 4 setup còn lại (single print retest · bear trap · kỷ luật trend day · tails/poor high-low).]**
- [x] 📎 **Buổi 1** *(người học tự xác nhận đã nắm — 2026-07-13)* — chart TPO, TPO-POC vs VPOC, IB/RE/failed auction, tails, single print. `tpo/text/buoi-1-nen-tpo-ban-do-phien.md`
- [ ] 📎 **Buổi 2** *(tham chiếu)* — 3 kịch bản mở vs VA (chart ES thật), 80% rule, day types actionable. *(§2.2 "4 kiểu mở cửa" đã gọn còn 3 nhánh niềm tin; giữ nugget cực trị bracket A + Rejection-Reverse.)* `tpo/text/buoi-2-day-types-mo-cua-80.md`
- [~] 📎 **Buổi 3** *(nâng lên dạy 2026-07-22 — lõi §0-§2 đã xong, người học muốn tập trung chart/ví dụ)* — value migration + POC clustering, **note thực chiến vàng (2 ca GCQ23) ⭐**, kick-off thực hành (sizing 2%, SL cấu trúc, checklist). `tpo/text/buoi-3-da-phien-thuc-chien-vang.md`. **[2026-07-22: đang dạy §2 — Value Migration (4 quan hệ VA) + POC Clustering + Composite tuần/tháng + TPO-POC vs VPOC, tách trang riêng `value-migration-poc-clustering.md` (8 diagram tập nhìn). ⭐ Người học xác nhận đây là phần QUAN TRỌNG NHẤT của TPO (tạo bias mua/bán; entry M1 là việc của footprint). CÒN §3 (2 ca GCQ23 ⭐) + §4 (kick-off thực hành).]**
> **✂️ Đã cắt khỏi phần dạy** (còn trong file tham chiếu, không giảng): 4 *tên* kiểu mở cửa Latin · Normal/Normal Variation Day · 5 phân đoạn phiên ES · Big Smile/Frown · chiếu mục tiêu IB/ADR (dùng scaling-out VAH/POC/VAL thay thế).
