# Cửu Âm Chân Kinh (web)

- **Nguồn nội dung:** `../cửu âm chân kinh.md` (chữ người học / bản tổng hợp CORVEN) + đặc tả `../plans/CUU-AM-CHAN-KINH-plan.md`; trích dẫn nguyên văn lấy từ `../corven-meet/2026-11-07/transcript.md` và `../data-export/messages-with-pro-trader/TRANSCRIPT.md`.
- **Trang:** `index.html` (nhìn nhanh, danh sách 2.2 tick được, không lưu) · `chi-tiet.html` (giải thích từng điều kiện, mỗi mục có `id` khớp link từ trang chính) · `style.css` dùng chung.
- **Ảnh:** `img/*.jpg` cắt từ `frames/`, chỉ vùng chart; toạ độ ghi ở `img/CROPS.md`. Thêm ảnh mới thì cắt giống vậy và mở kiểm không lộ webcam/tên.
- **Sửa nội dung:** 2.2 trang chính = bản rút gọn plan mục 2b; sửa 2.2 ở cả `index.html` lẫn `../cửu âm chân kinh.md` cho khớp; thêm điều kiện thì thêm mục cùng `id` trong `chi-tiet.html`.
- **Quy tắc chữ:** buy / sell / limit / market giữ tiếng Anh; câu CORVEN chép đúng mốc giờ; phần giải thích của Claude gắn nhãn "diễn giải".
- **Deploy:** `./deploy.sh` (tạo repo `AnhNMTHE176111/cuu-am-chan-kinh` nếu chưa có, chép file sang `$HOME/.cuu-am-chan-kinh-pages`, push, bật Pages).
- **Link:** https://anhnmthe176111.github.io/cuu-am-chan-kinh/
- Kiểm thử: `docs/TEST-1.md`, script `docs/test/` (check_quotes, check_22, check_html, ui, interact, shots2); ảnh: `docs/shots/` (8), `docs/shots-impl/` (4).
