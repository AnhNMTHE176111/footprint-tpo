# Quy tắc chi tiết (tách từ CLAUDE.md ngày 2026-11-22)

> CLAUDE.md chỉ giữ quy tắc cốt lõi. File này là phần chi tiết — đọc khi soạn bài giảng,
> bài tập, hoặc khi gặp ca biên. Bản CLAUDE.md đầy đủ cũ: xem git history trước commit 2026-11-22.

## 1. Giảng bài
- **Load trước, giảng sau (sự cố 2026-06-11):** mở toàn bộ tài liệu + ảnh cần dùng bằng các tool call
  liên tiếp, không viết nội dung giảng xen giữa. Toàn bộ bài giảng nằm trong **tin nhắn cuối lượt**.
  Bài dài thì chia nhiều lượt, mỗi lượt chờ người học trả lời.
- **Dạy bằng hình:** mở ảnh chart (`course/images/bai-N/pNNN.png`, `ebook/images/pNNN.png`) bằng Read,
  đọc số trực tiếp. Luôn kèm link Markdown tới mọi ảnh nhắc tới, vd `[p056.png](ebook/images/p056.png)`.
  Tên file = số trang PDF (có thể lệch số trang in) → bám tên file.
- **Đọc số thật trước khi diễn giải:** phóng to vùng cần đọc nếu ảnh nhỏ; chỉ nêu số đã nhìn rõ, không
  nặn số cho khớp lý thuyết. Phần tổng hợp riêng của Claude (không có trong tài liệu) phải nói rõ.
- **Thuật ngữ chuẩn:** hai PDF dịch máy sai thuật ngữ ("Đồng bằng" = Delta, "âm lượng" = khối lượng,
  "Nút âm lượng cao" = HVN, "Dấu chân" = Footprint, "quán bar" = nến, "Công việc chưa hoàn thành" =
  Unfinished Business). Tra `glossary.md`.
- **Bám cơ chế, không bám câu chữ (sự cố UB 2026-06-29):** phân biệt định nghĩa gốc với hệ quả điển hình.
  Vd UB: định nghĩa = "đỉnh soi Bid, đáy soi Ask"; "cả Bid lẫn Ask > 0" chỉ là ca điển hình → ô đỉnh 15×0
  vẫn là UB. Ra đề phải kiểm tính khả thi vật lý. Mâu thuẫn câu chữ → phân xử bằng cơ chế đấu giá.
- **Trung thực:** không bịa lỗi người học; khi họ đúng thì nhận sai ngay và chỉ đúng lỗi cụ thể của mình.
  Đọc lại nguyên văn câu người học trước khi chấm. Nghi mình đang chiều người học → mở lại tài liệu gốc.

## 2. Bài tập "săn bằng chứng" trên Optimus Flow (chốt 2026-08-11)
Chi tiết + bài từng buổi: `tpo/EVIDENCE-DRILLS.md`. Ba mức cho mỗi khái niệm:
1. **Nhận dạng** — tìm 1 ca thật.
2. **Đếm** — duyệt N phiên liên tiếp không chọn lọc; người học đếm bằng mắt, Claude đếm bằng số từ CSV.
   Lệch nhau = một bên hiểu sai định nghĩa → chỗ học được nhiều nhất.
3. **Phản chứng** — bắt buộc tìm 1 ca luật sai (tránh thiên kiến xác nhận).

Người học ghi phán đoán **trước**, Claude chấm **sau**. Ảnh phải đọc được mã · khung · ngày giờ · con số,
lưu ở `tpo/evidence/buoi-N/`. "Không tìm được" là câu trả lời hợp lệ. Luật chưa đo bằng số thì chỉ dùng
đọc chart, **không code thành signal** và không nói như đã kiểm định.

## 3. Lộ trình TPO (chốt 2026-08-11)
Khi người học nói "dạy tôi TPO" → dùng `tpo/SYLLABUS-TPO.md` (v2, 9 buổi).
- Thứ tự: **2 → 3 → 6 → 4 → 5 → 7 → 8 → 9** (Buổi 1 ôn lồng vào Buổi 2). Chưa dạy gì → bắt đầu Buổi 2.
- `tpo/text/00-tpo-loi-thuc-chien.md` và buoi-1/2/3 chỉ để tra khi đào sâu, không làm trục.
- ⚠️ Nhắc **Bài số 0** nếu chưa xong: chart TPO daily đang neo Globex ~05:00 VN thay vì pit COMEX ~19:20
  → IB sai, mọi luật dính IB vô nghĩa; mới có n=22 profile. Sửa mốc phiên + xuất ≥ 3 tháng trước khi đếm.

## 4. Quy ước đọc chart TPO trên Optimus Flow (chốt 2026-08-12)
- **Màu chữ TPO = thời gian** (tím → đỏ → cam → vàng → xanh lá → xanh biển = sớm → muộn), **không phải
  khối lượng**, kể cả khi bật "VOLUME ANALYSIS".
- Khối lượng nằm ở **cột số riêng bên phải** (histogram xanh + số).
- Ứng dụng: nhìn màu chữ theo giá để đọc trình tự giá đã đi qua mà không cần xem lại nến.

## 5. Code C# / Python
- Build `quantower-tpo-suite` bằng `./build-tpo.sh` (hoặc `daily`/`zones`); test ở `tests/`
  (`tests.csproj`, cần `.NET SDK` + `$HOME/quantower-libs/{TradingPlatform.BusinessLayer,System.Drawing.Common}.dll`).
- Máy Windows này đã có `.NET SDK 10.0.401`, các DLL trên, `qw-build.sh`, `qw-deploy.sh` (từ 2026-09-15).
  Thiếu gì thì tự cài (dotnet qua winget) / tự khôi phục DLL, không hỏi; chỉ báo nếu thật sự bất khả thi.

## 6. Dữ liệu
Tất cả nằm trong `data-export/`; **đọc `data-export/README.md`** (nguồn chuẩn, bẫy nối hợp đồng, phân loại
file bằng header, múi giờ). Tự tìm file rồi chạy, chỉ hỏi khi thật sự thiếu symbol/khung chưa từng xuất.
Giá giữa các file có thể là symbol khác nhau → kiểm trước khi gộp.
