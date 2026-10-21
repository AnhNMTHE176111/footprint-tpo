## Đánh giá trung thực (QĐ-6: chỉ file 90d GCZ26; bảng 2 năm cũ chỉ tham khảo)

**Kết luận cuối: D TẮT MẶC ĐỊNH, CHỈ ĐỌC CHART.** Không biến thể nào (vòng 1: delta, cell, V1, V2; vòng 2: V3, V4) cho kỳ vọng dương bền ở cả TRAIN lẫn TEST, và ở TEST luôn n < 30 hoặc âm.

1. **Số lệnh:** vòng 1 (cần vùng Z): 2–11 lệnh/90 ngày (≤0,18 lệnh/ngày), TEST chỉ 4–8 lệnh ⇒ chưa kết luận. Phễu: 216 lần bẫy tại Z → 22 có CF chặt → 7 lệnh. Vòng 2 (bỏ Z): V3 5/70% 31 lệnh (0,51/ngày), V4 3/70% 60 lệnh (0,98/ngày). Bỏ Z tăng n, nhưng vẫn xa mục tiêu 10–20 lệnh/ngày.
2. **Vòng 1, cấu hình 5/70%:** delta n=7 R +0,20 (TRAIN +0,94 n=3 / TEST −0,36 n=4); cell n=2, cả hai thua; V1 (CF mềm) n=10 R +0,12, TEST −0,24 (n=7); V2 n=11 R 0,00, TEST −0,35 (n=8). Mọi biến thể: TRAIN dương nhờ 2–3 lệnh, TEST âm — kiểu "tìm trên nửa đầu, chết ở nửa sau" mà plan 0 cảnh báo.
3. **V3 (không Z, loc sideway 60 nến ≥ 2u, 5/70%):** n=31, R +0,08, TRAIN +0,42 (n=16) / TEST −0,29 (n=15 < 30). Đối chứng 200 lần −0,05, P(đối chứng ≥ thật)=0,28 ⇒ không hơn ngẫu nhiên; khoảng tin cậy bootstrap ở bảng trên bao trùm 0 rất rộng. Theo phase: Á n=19 +0,18 · Âu n=6 +0,42 · Mỹ n=6 −0,58 (n quá nhỏ để tin). BUY −0,04 / SELL +0,28.
4. **V4 (3/70%):** n=60, R −0,29, TRAIN −0,32 / TEST −0,25 (n=25 < 30), đối chứng −0,10 (P=0,81: tệ hơn ngẫu nhiên). Cỡ move càng nhỏ (3→5 giá) R càng âm ở cả TRAIN và TEST: không ô nào của V4 dương ở cả hai nửa.
5. **Bộ lọc sideway đúng nguyên văn (biên độ 60 nến ≥ 2u) loại 0 ca** vì thỏa ở 99,9% số nến (biên độ 60 nến gần như luôn ≥ 2× biên độ trung vị 1 nến). Không nới/siết ngưỡng cho nó "có tác dụng" (sẽ thành tham số thứ ba). Nếu cần lọc sideway thật phải định nghĩa khác (vd biên độ 60 nến so với biên độ phiên trước).
6. **Ô nào bền cả hai nửa?** Không có. Ô V3 5/70% dương tổng (+0,08) nhưng TEST âm, hàng xóm 4 giá (−0,17) và 7 giá (−0,40) đều âm ⇒ khớp quá mức, không chọn.
7. **Bất đối xứng BUY/SELL:** quá nhiễu (n nhỏ), đảo chiều giữa các cấu hình; không kết luận.
8. **Đề xuất (chưa chạy, chỉ khi có thêm dữ liệu hợp lệ):** (a) lọc sideway bằng định nghĩa khác 60-nến/2u; (b) gộp D vào B vì cùng vùng VWAP; (c) thử move ≥7 giá khi có ≥100 lệnh. Hiện không có cơ sở bật D làm signal.
9. **Giới hạn:** hằng số tự chọn (move hình thành ≤30 nến, hồi ≤30 nến và ≥1 giá, CF trong 3 nến, Z cách cực trị ≤1 giá); 1 lệnh mở cùng lúc; bias lấy một lần đầu mỗi phase; mỗi cặp (đáy, đỉnh) zigzag vào tối đa 1 lệnh; 90 ngày chỉ là một hợp đồng, một thời kỳ giá. Bảng 2 năm trước QĐ-6 (cho kết luận cùng hướng: R −0,09 đến −0,26) nằm ở `RESULTS-D-2y-cu-tham-khao.md`, không dùng để quyết định.
