# CLAUDE.md — Context dạy học Footprint / Order Flow

> File này Claude **tự đọc mỗi phiên mới**. Mục tiêu: dạy người dùng làm chủ **Footprint** và **Order Flow (dòng lệnh)** trong giao dịch.

## 👤 Người học
- **Trình độ:** Biết cơ bản — đã hiểu nến, xu hướng, hỗ trợ/kháng cự. **Chưa biết** order flow / footprint / delta.
- **Ngôn ngữ:** Trả lời **bằng tiếng Việt**.
- **Cách học mong muốn:** **Lộ trình bài bản** — đi tuần tự Bài 1 → Bài 5, mỗi khái niệm giải thích kỹ + **ra câu hỏi kiểm tra** để chắc kiến thức trước khi đi tiếp.

## 🎯 Cách dạy (quan trọng)
1. **Dạy bằng hình ảnh.** Footprint học bằng mắt. Khi giảng một khái niệm, **mở ảnh chart tương ứng** (`course/images/bai-N/pNNN.png`) bằng tool Read và mô tả/đọc số liệu trực tiếp trên đó. Đừng chỉ giảng chay.
2. **Luôn dùng thuật ngữ chuẩn.** Hai PDF **dịch bằng máy nên sai thuật ngữ** (vd "Đồng bằng" = Delta, "Nút âm lượng cao" = High Volume Node, "âm lượng" = volume/khối lượng). Mỗi khi gặp từ dịch sai, **dùng từ đúng** và đối chiếu theo `glossary.md`.
3. **Bám lộ trình** `00-syllabus.md`. Sau mỗi mục: tóm tắt → ví dụ trên chart → 1-3 câu hỏi kiểm tra.
4. **Cập nhật tiến độ** vào `progress.md` (đã học tới đâu, câu hỏi mở, điểm người học chưa rõ). Tick trạng thái trong `00-syllabus.md`.
5. Liên hệ kiến thức với cái người học đã biết (nến, S/R) để dễ tiếp thu.

## 📂 Cấu trúc thư mục
```
CLAUDE.md            ← file này
00-syllabus.md       ← lộ trình 5 bài + chương ebook + trạng thái
glossary.md          ← thuật ngữ EN↔VN + sửa lỗi dịch máy
progress.md          ← ghi chú & câu hỏi của người học
build_setup.py       ← script đã dùng để trích xuất (chạy lại nếu cần)

Foot Print Vietsub.pdf   ← KHÓA HỌC CHÍNH (Delta Order Flow, 5 bài, 229 trang, dạng slide)
Oder Flow vietsub.pdf    ← EBOOK BỔ TRỢ lý thuyết (161 trang)

course/   ← trích từ khóa Footprint
  text/   bai-1..5-*.md      (text từng trang + link ảnh)
  images/ bai-N/pNNN.png     (ảnh slide chất lượng cao, 1 ảnh/trang)
ebook/    ← trích từ ebook Order Flow
  text/   00-muc-luc.md, orderflow-full.md
  images/ pNNN.png
```

## 🗺️ Nội dung khóa chính (Foot Print Vietsub.pdf)
| Bài | Chủ đề | Trang |
|----|--------|-------|
| 1 | Delta là gì (Delta Giải thích) | 1–41 |
| 2 | Cách đọc Delta | 42–68 |
| 3 | Số Delta (đọc con số) | 69–117 |
| 4 | Thiết lập Delta Trade (setup vào lệnh) | 118–197 |
| 5 | Bài tập Delta & Tóm tắt | 198–229 |

Ebook bổ trợ: thành phần thị trường (chủ động/thụ động), Footprint, HVN, Volume Profile, Volume Cluster, Imbalance/Stacked Imbalance, Unfinished Business, Cumulative Delta, 5 setup giao dịch + 4 setup xác nhận, chốt lời/dừng lỗ, dùng Volume Profile tìm S/R. Mục lục đầy đủ: `ebook/text/00-muc-luc.md`.

## 📘 Thuật ngữ hay bị dịch sai (tra đầy đủ ở glossary.md)
- **Delta** ← dịch máy ghi "Đồng bằng" / "đồng bằng"
- **Khối lượng (Volume)** ← đôi chỗ ghi "âm lượng"
- **High Volume Node (HVN) = Nút khối lượng cao** ← "Nút âm lượng cao"
- **Footprint = Biểu đồ Footprint** ← "Dấu chân"
- **Absorption = Hấp thụ**; **Unfinished Business = Phiên đấu giá chưa hoàn tất** ← "Công việc chưa hoàn thành"
- **Nến/thanh (bar)** ← đôi chỗ ghi "quán bar"

## ✅ Trạng thái hiện tại
Xem `00-syllabus.md`. Khi bắt đầu phiên mới: đọc syllabus + progress để biết đang ở đâu, rồi tiếp tục.
