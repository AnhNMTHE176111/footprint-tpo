# 4 sửa đổi của người học cho corven-1 — đo trên TRAIN (2026-11-09)

Nguồn: ca bỏ lỡ 11:26 VN 09/11 (buy, vào 4132,3). Đo **chỉ trên TRAIN ≤ 15/9 (35 phiên dày)**; TEST khoá; dữ liệu ≥ 22/10 không dùng để quyết.
Script: `variants_nguoihoc.py` (3 sửa đổi, 8 tổ hợp), `variants_nguoihoc_trap.py` (thêm sửa đổi 4).

Sửa đổi:
1. **Hồi không cần chạm cạnh** (thế B): cửa sổ 3 nến có ≥ 1 nến hồi (đóng ngược hướng so với nến trước hoặc nến ngược màu), mọi nến đóng ngoài range, CF đóng vượt giá đóng cao nhất của nến hồi; bỏ giới hạn "CF đóng ≤ 1 mbr từ cạnh".
2. **Bỏ ⛔ nhịp đẩy do quét stop** — luật do agent tự diễn giải (plan corven mục 3: "gần đúng"), phần ΣΔ ≤ 0 mâu thuẫn trực tiếp với dấu hiệu trap (trap sell tạo delta âm).
3. **Bỏ 4c R ≥ 1,7 cho thế B** (đã phá range ⇒ TP 2R); thế A giữ.
4. **Dấu hiệu "trap trong nhịp hồi"** (thế B): ô ngược phe ≥ 3× nền_ô và ≥ 10 hợp đồng ở nến trước CF trong cửa sổ, CF đóng vượt giá ô đó.

| Tổ hợp | n | R TB | WR | nửa 1 / nửa 2 | vào ngẫu nhiên sau CF |
|---|---|---|---|---|---|
| corven-1 gốc | 97 | −0,29 | 27 % | −0,31 / −0,28 | −0,08 |
| chỉ 1 | 106 | −0,13 | 32 % | −0,33 / +0,05 | −0,03 |
| chỉ 2 | 105 | −0,24 | 29 % | −0,29 / −0,18 | −0,09 |
| chỉ 3 | 217 | −0,23 | 29 % | −0,32 / −0,14 | −0,11 |
| 1+2+3 | 323 | −0,07 | 33 % | −0,04 / −0,10 | −0,04 |
| 1+2+3+4 | 333 | −0,075 | 33 % | −0,05 / −0,10 | −0,08 |

Kết luận: cả 4 sửa đổi cùng chiều cải thiện (−0,29 → −0,07R) nhưng **vẫn âm và ngang vào ngẫu nhiên** ⇒ chưa có lợi thế. Đã thử 11 tổ hợp trên TRAIN ⇒ hậu kiểm.
Ca 11:26 với 1+2+3+4: được vào (dấu hiệu stacked buy 4131,7–4132,0 + trap hồi bóng đỏ 20 @4131,3), SL 4128,0, TP 4140,9 ⇒ TP +1,95R. Đây là dữ liệu mới, chỉ xác nhận cơ chế, không tính làm bằng chứng.
