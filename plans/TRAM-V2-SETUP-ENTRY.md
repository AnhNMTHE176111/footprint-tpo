# Trạm Đêm Vàng v2 — "Setup Entry": 4 checklist mở sẵn

2026-10-20 · theo review trực tiếp của người học trên bản 1.0.8. Bản này **thay** phần tầng 2, tầng 3, tầng 4 của `CHECKLIST-DEM-VANG-plan.md`. Các phần khác (tầng 0, tầng 1, sổ, lịch tin, giờ mùa đông, Từ điển) giữ nguyên trừ chỗ ghi dưới đây.

## 0. Ba yêu cầu của người học (nguyên văn ý)

1. **Vùng:** rê chuột vào một loại vùng trong danh sách thì hiện định nghĩa để đọc lại khi quên (poor low, high, …). Mọi định nghĩa đó cũng nằm trong Từ điển.
2. **Bỏ tầng 2 (Chế độ) và tầng 4 (Lệnh)** — "quá vô nghĩa".
3. **Tầng 3 đổi tên thành "Setup Entry".** Mở sẵn cả 4 kịch bản, không rule nào khóa. Người học tự chọn; tick đủ checkbox của một kịch bản thì vào ngay. 4 kịch bản xếp **dọc**, mỗi kịch bản **xổ sẵn** checkbox để nhìn và cuộn nhanh, không phải bấm vào từng kịch bản mới thấy chi tiết.

## 1. Thanh tầng mới

`0 Trước · 1 Vùng · 2 Setup Entry · 3 Sổ` (4 tab). Không còn tầng khóa. Thẻ phiên vẫn ở cột phải.

## 2. Tầng 1 Vùng — danh sách loại vùng có định nghĩa

- Bỏ `<select>` gốc (option của trình duyệt không hiện được chú thích khi rê chuột). Thay bằng **ô chọn tự vẽ**: bấm mở danh sách; mỗi dòng = tên + nhãn vai (hạng 1 · cạnh · cấm fade · chỉ mục tiêu · nợ). **Rê chuột hoặc dùng phím ↑↓** lên dòng nào thì khung bên phải danh sách (trên điện thoại: dưới dòng) hiện **định nghĩa 1–2 câu + "dùng thế nào" 1 câu**. Enter / click để chọn, Esc đóng, gõ chữ để lọc.
- Định nghĩa lấy chung một nguồn với Từ điển (`content.js` → `glossary`), mỗi loại vùng một mục: VWAP tuần, VWAP ngày, VAH Âu, VAL Âu, cụm POC, HVN tuần, HVN 3 tuần, LVN, High hôm qua, Low hôm qua, single print, naked POC, IB high, IB low, cạnh range, poor high, poor low, HVN ngày. Nội dung bám trang Hệ thống (Q2, Q3, Q4, bảng 2.3) và định nghĩa chuẩn Market Profile; chỗ trang Hệ thống không có thì ghi định nghĩa chuẩn ngắn, không bịa luật.
- Nhãn vai của từng loại giữ đúng bảng 2.3 của Hệ thống (QĐ-2, QĐ-3, QĐ-15 cũ).

## 3. Bỏ tầng Chế độ và tầng Lệnh

- **Chế độ** (cân bằng / vừa phá / trend thin, acceptance, nến dài nhất) không còn là một tầng. Những điều kiện đó chuyển thành **checkbox bối cảnh trong từng kịch bản** (mục 4). Thẻ phiên bỏ dòng "Chế độ".
- **Lệnh** không còn tầng riêng. Sau ENTRY, nút **"Ghi lệnh"** ghi thẳng một dòng vào Sổ (giờ, hướng, kịch bản, vùng, giá vào, SL, TP, R dự kiến, cỡ lệnh, các ô đã tick). Kết quả (TP · SL · hòa · đóng tay + lý do, R thực tế, "SL bị quét rồi tới TP?") nhập ngay trên dòng đó trong Sổ. Luật be (+1,5R cho A, B; +1R cho C, D) hiện thành một dòng nhắc trên dòng lệnh đang mở trong Sổ.
- Không còn "chỉ một lệnh mở" bằng khóa; thay bằng ô chung (mục 4.1).

## 4. Setup Entry — 4 checklist dọc, mở sẵn

Bố cục: một cột, 4 khối A → B → C → D xếp dọc, mỗi khối **luôn mở**, có tiêu đề lớn + mục tiêu R + ảnh ca thật thu nhỏ (bấm để phóng). Trên cùng một thanh nhảy nhanh `A · B · C · D` (dính đầu khi cuộn). Mỗi khối có tiến độ `7/11` ở tiêu đề. Khi một khối đủ ô thì khối đó viền xanh và thanh ENTRY dính đáy hiện **ENTRY BUY/SELL … · kịch bản B** của khối đó. Nhiều khối cùng đủ thì thanh hiện khối người dùng tick cuối.

Không có rule nào khóa khối. Engine chỉ: (a) chấm các ô tự kiểm từ số, (b) đếm ô đã tick, (c) tính SL/R:R/cỡ lệnh, (d) hiện cảnh báo chung.

### 4.1 Ô chung cho mọi kịch bản (hiện một lần trên đầu, áp cho cả 4 khối)
- Tự kiểm (máy điền, người không tick): **Đã chốt thẻ phiên** · **Không trong khung giờ cấm** (từ lịch tin) · **Chưa tắt máy** (phá luật < 2, SL liên tiếp < 3 trong đêm) · **Không có lệnh đang mở** (dòng Sổ chưa nhập kết quả).
- Người tick: **Không trong 3 nến M1 sau nến dài nhất phiên** (HT 7, xung đột).
- Ô tự kiểm sai thì hiện đỏ kèm lý do; nó tính là "chưa đủ" cho mọi khối nhưng **không khóa** khối (người học vẫn tick được phần còn lại để luyện mắt).

### 4.2 Trong mỗi khối
Thứ tự: **Hướng** (buy / sell, nút đôi) · **Vùng** (chọn từ thẻ phiên; hiện "lần thứ n tại vùng", n ≥ 3 ⇒ ô tự kiểm "Lần ≤ 2 tại vùng" đỏ) · các checkbox theo nhóm **Bối cảnh / Kiểm tra / Điểm vào** · **Giá vào · SL · TP · biên độ nến M1 cao nhất 5 nến** · các ô **SL** (một ô tick vị trí + 3 ô tự kiểm) · ô ngược bias (chỉ hiện khi hướng ngược bias: bắt buộc gõ lý do — HT 2.2 luật cứng).

Ô tự kiểm SL (HT 6, giữ nguyên): **SL ≥ biên độ nến M1 cao nhất 5 nến** · **SL ≤ 4 giá** · **R:R ≥ 1:2** (TP gợi ý theo QĐ-16 cũ: 3R cho A, B; 2R cho C, D; vùng kế tiếp nếu gần hơn).

### 4.3 Nội dung checkbox (bám HT mục 3.1, 4, 5, 6; mỗi ô ≤ 1 dòng, có "?" mở định nghĩa)

**A · Phá hồi — 3R**
- Bối cảnh: □ Có 1 nến M5 đóng ngoài cạnh (VA Âu, IB hoặc vùng đã kẻ) □ Nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào trong □ Bias cùng chiều phá □ Cú phá không rơi vào 18:00–19:20
- Kiểm tra: □ Hồi hình U, ≥ 3 nến, không phải V □ Tại cạnh: delta cùng chiều phá hoặc bong bóng hấp thụ phe ngược □ Bong bóng to gần nhất không ngược phe còn giữ □ Giá cách cạnh ≤ 1 giá
- Điểm vào: □ Nến M1 đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu
- SL: □ Sau râu nến xác nhận hoặc mép xa vùng (cái xa hơn) + 0,3 giá

**B · Hấp thụ — 3R** (vùng hạng 2 ⇒ cỡ ½)
- Bối cảnh: □ Giá tại VWAP tuần, VWAP ngày, HVN tuần, cụm POC, hoặc cạnh VA Âu khi đang cân bằng □ Không phải HVN 3 tuần, LVN, HVN ngày □ Không đang phá VWAP / cạnh theo chiều move (nếu có là phá hồi — dùng A) □ Không ngay sau nến dài nhất phiên
- Kiểm tra: □ 3 nến cuối: thân và |delta| giảm dần, không cực trị mới □ Bong bóng ở cực trị cùng phe với lệnh □ DMA đi ngang □ Giá cách vùng ≤ 1 giá
- Điểm vào: □ Nến xác nhận ngược chiều move, delta đảo dấu ≥ ½ delta nến lớn nhất của move
- SL: □ Sau cực trị của cụm hấp thụ + 0,3 giá, không ở giữa cụm

**C · Fade cạnh — 2R, cỡ ½**
- Bối cảnh: □ Giá ở đúng cạnh VA Âu / range (≤ 1 giá), không ở giữa range □ Chưa có nến M5 nào đóng ngoài cạnh
- Kiểm tra: □ Phá hụt: râu xuyên cạnh rồi đóng lại trong □ Delta ủng hộ chiều vào □ Bong bóng to gần nhất không ngược phe còn giữ
- Điểm vào: □ Nến M1 đóng lại trong range; thân không ngắn, râu ngược không dài
- SL: □ Sau râu phá hụt + 0,3 giá

**D · Trap — 2R**
- Bối cảnh: □ Có move rõ ≥ 5 giá cùng chiều bias □ Không đang đi ngang □ Nhịp hồi ngược tới một vùng, chưa quá 70 % move
- Kiểm tra: □ Đỉnh hồi có bong bóng hấp thụ phe hồi, hoặc nến hồi delta thuận mà đóng dưới nửa thân □ Hồi hình U, không phải V
- Điểm vào: □ Nến M1 đóng theo chiều move cũ, thân dài, delta cùng dấu
- SL: □ Sau đỉnh nhịp hồi + 0,3 giá

### 4.4 ENTRY, ghi lệnh, phá luật
- Thanh dính đáy: chưa đủ ⇒ "CHỜ — khối X còn thiếu: …" (liệt kê tối đa 3 ô thiếu của khối đang làm); đủ ⇒ **ENTRY** xanh, chữ ≥ 32 px, số giá + R:R + cỡ lệnh; nút "Ghi lệnh" (Enter).
- Thiếu ô mà vẫn muốn vào: nút phụ "Vẫn vào (thiếu n ô — tính phá luật)" ⇒ dòng Sổ có cờ phá luật + danh sách ô thiếu. Giữ ngắt mạch: 2 phá luật hoặc 3 SL liên tiếp ⇒ ô chung "Chưa tắt máy" đỏ (không khóa, chỉ báo).
- Cỡ lệnh: giữ máy tính MGC và QĐ-21 (½ không chia được ⇒ 1 hợp đồng, nói rõ rủi ro thật).
- Sau "Ghi lệnh": bỏ tick của khối đó (giữ hướng, vùng), cuộn về đầu.
- Phím: `1–4` nhảy tới khối, `Enter` ghi lệnh khi ENTRY, `N` xóa tick khối đang làm.

## 5. Sổ
- Dòng lệnh mở ở trên cùng với nút kết quả: TP · SL · Hòa · Đóng tay (lý do: hấp thụ ngược đe dọa TP · đóng sạch trước tin · khác ⇒ phá luật) + ô giá thoát (R tự tính, sửa được) + "SL bị quét rồi tới TP?". Nhắc be theo kịch bản.
- Bảng 7 cột HT 8 giữ; cột "chế độ" thay bằng "vùng"; cột "4 kiểm tra" in tóm tắt các ô kiểm tra đã tick.
- "Bạn cộng", Kết phiên, 4 con số tuần, xuất Markdown/JSON/CSV giữ.

## 6. Dữ liệu và mã
- `store` version 2, migrate từ v1: giữ thẻ phiên, vùng, sổ; bỏ `regime`, `setup` cũ, `open` cũ (lệnh mở cũ chuyển thành dòng Sổ chưa có kết quả).
- `engine` mới gọn: `evaluate(night, now, settings, news)` → `{ common:[{id, ok, auto, reason}], blocks:{A..D:{done, total, missing[], order, autoChecks}}, entry: {scen}|null, breaker }`. Bỏ danh sách luật DIS_/NO_ cũ; giữ hàm tính SL/R:R/cỡ lệnh, lịch tin, giờ mùa đông, nightKey.
- Test: viết lại test engine theo checklist (mỗi ô tự kiểm một test; ENTRY chỉ khi đủ; phá luật đếm đúng; migrate v1 → v2; 5 ca thật cũ A1–A5 thành 5 ca tick tay ra ENTRY / thiếu ô đúng). e2e: tick đủ khối B tới ENTRY bằng chuột thật; dropdown vùng hiện định nghĩa khi rê và khi dùng phím; 4 khối luôn mở, không khối nào có trạng thái "tắt"; 390 px không tràn.

## 7. Chốt sau 3 biên bản kiểm tra (20/10, người học chưa phản hồi — Claude chọn theo đề xuất, đổi được)
- **Ngược bias (HT 2.2 thắng HT 9):** chỉ khối B được ngược bias, và chỉ khi tick ô "vùng có tail thật hoặc single print đúng phía"; TP 2R, cỡ ½, lý do bắt buộc. Khối A, C, D ngược bias ⇒ ô tự kiểm "Cùng chiều bias" đỏ. Bias KHÔNG ⇒ A, B, D có ô tự kiểm đỏ "bias KHÔNG: chỉ fade cạnh"; bias CHỜ ⇒ cả 4 khối đỏ ô đó.
- **Khối B bắt buộc hồi hình U** (HT 9 câu 4 thắng chữ "ưu tiên" ở 5·B).
- **Ô tự kiểm thay tick tay** khi máy tính được: giá cách vùng ≤ 1 giá (từ giá vào + vùng), giờ phá ngoài 18:00–19:20 (giờ hiện tại khi tick ô nến M5), bias cùng chiều (từ hướng + bias), lần ≤ 2 tại vùng, SL sai phía. Giá vào cách vùng > 3 giá ⇒ đỏ "ở lưng".
- **Gọn hơn khi trade M1:** khối không làm thu gọn thành một dòng (bấm để mở; đang làm khối nào thì khối đó mở); ghi lệnh xong giữ vị trí cuộn và giữ tick bối cảnh, chỉ xóa nhóm Điểm vào + giá; lệnh đang mở có nút kết quả ngay trên thanh dưới (TP · SL · Hòa · Đóng tay) không phải sang Sổ.
- **Điện thoại:** chạm lần đầu vào loại vùng chỉ hiện định nghĩa, chạm lần hai mới chọn.
