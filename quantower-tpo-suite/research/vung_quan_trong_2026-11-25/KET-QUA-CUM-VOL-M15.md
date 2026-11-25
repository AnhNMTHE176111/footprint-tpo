# Cụm khối lượng kiểu Trader Dale trên profile cố định ngày/tuần, đơn vị M15 (Opus, 2026-11-25)

Chỉ đo **phản ứng của giá tại vùng**, không giả lập lệnh. Script: `vc.py` (bộ máy đo) và `vong15.py` (các vòng).

Dữ liệu: NQZ26 từ 13/09 đến 25/11 (53 phiên), GCZ26 từ 28/07 đến 18/11 (74 phiên).

**Đơn vị U15** = biên độ trung bình một nến M15 của 5 phiên gần nhất. NQ khoảng 55 điểm, GC khoảng 8,2 giá.

## Cách vẽ vùng

**1. Profile cố định.** Dùng volume profile của từng phiên ngày đã đóng (và tuần trước, khi thử).

**2. Cụm khối lượng.**
- Profile được làm mượt ±0,1 U15.
- Một cụm là một đỉnh có khối lượng ≥ 1,5 lần trung bình hàng.
- Các cụm phải cách nhau ≥ 1 U15. Mỗi profile giữ các cụm nặng nhất.

**3. Dải cụm.** Nới từ đỉnh ra hai phía cho tới khi khối lượng còn < 70 % đỉnh. Bề rộng thường khoảng 0,6 U15.

**4. Luật Trader Dale.**
- Giá rời dải rồi đi xa ≥ 3 U15 trong ≤ 4 nến M15. Khi đó vùng được coi là "tươi".
- Rời lên thì thành **hỗ trợ**, rời xuống thì thành **kháng cự**.
- Chỉ chấm lần quay lại đầu tiên. Vòng 9 thử thêm lần thứ 2 và thứ 3.

**5. Gộp.** Cụm của các ngày khác nhau mà chồng nhau thì gộp thành một vùng hợp lưu (đúng cách người dùng vẽ).

**6. Chấm điểm.**
- Điểm đảo là cực trị khi giá bật ngược ≥ 1 U15.
- Phân loại theo vị trí điểm đảo: tại vùng, sớm (trước mép gần), hoặc phá.

**7. Đối chứng.**
- Cùng dải đó dời đi ±1,5–4 U15 và áp **đúng luật cũ**: cũng phải có cú rời đi mạnh, cũng chỉ chấm lần đầu.
- Như vậy phép so là: chỗ khối lượng dày so với một mức giá bất kỳ mà giá cũng đã bỏ đi mạnh.

## Kết quả từng vòng

Δ = % đảo tại vùng (thật) − % đảo tại vùng (đối chứng), theo điểm %, gộp NQ + GC. Khoảng [5–95 %] tính bằng bootstrap theo phiên.

| Vòng | Thử | % tại vùng thật / đối chứng | Δ | Kết luận |
|---|---|---|---|---|
| 1 | Cụm hôm qua, mọi lần chạm (cách đo cũ) | 31,6 / 33,1 | −1,5 [−3,9, +0,9] | HVN chạm bất kỳ lúc nào: bằng ngẫu nhiên, khớp kết quả cũ |
| 2 | Thêm luật Trader Dale (rời ≥ 3 U15 trong ≤ 4 nến M15, chỉ lần đầu) | 33,9 / 24,6 | **+9,3** [+0,2, +19,2] | có hiệu ứng, nhưng mẫu chỉ có 115 lần |
| 2 | Chỉ cần rời đi, không cần mạnh | 34,4 / 33,1 | +1,3 | điều kiện "rời đi **mạnh**" là cốt lõi |
| 2b | Cụm 3 ngày gần nhất (riêng), Dale | 30,5 / 24,1 | +6,4 [+0,4, +13,2] | dương ở cả NQ TRAIN, NQ TEST và GC |
| 2b | Cụm 5 ngày gần nhất | 28,2 / 25,8 | +2,4 | cụm cũ hơn 3 ngày thì yếu đi |
| 3 | Cú rời đi X = 2/3/4/5 U15, K = 2/4/8 nến | X = 2: ≈ 0; X ≥ 3: +6 đến +14 | | cú rời đi phải ≥ 3 U15 |
| 4 | Bề rộng dải (ngưỡng 50/70/85 %, hay chỉ một đường tại đỉnh) | 70 % (≈ 0,6 U15): +6,4; 50 % (≈ 1,3 U15): +3,8; 85 % / một đường: −2 | | **phải vẽ vùng ≈ 0,6 U15, không vẽ một đường** |
| 4 | Chỉ lấy cụm mạnh: tỉ lệ ≥ 2 lần trung bình, hoặc 1–2 cụm nặng nhất | 34,6 / 24,0 | **+10,6** [+4,9, +17,6] với 2 cụm/ngày | cụm nặng nhất tốt hơn; dương ở cả 3 tập (+4,6, +7,0, +15,0) |
| 5 | Cụm tuần trước | Dale: −3,2 (n 49); mọi lần chạm: +0,9 | | với scalp M15, cụm tuần **không** giúp |
| 6 | Gộp cụm 2–3 ngày chồng nhau (2 cụm/ngày) | 36,4 / 25,3 | **+11,1** [+3,3, +18,7] | gộp không làm hỏng; vùng chỉ có 1 nguồn: +14,8 |
| 6 | Vùng hợp lưu 2 ngày (mọi lần chạm) | 47,0 / 42,1 | +4,9 [−0,7, +10,4] | vùng rộng hơn (≈ 1,2 U15) nên % cao; Δ nhỏ; mẫu Dale quá ít (27 lần) |
| 6 | Vùng hợp lưu 3 ngày | n 9–33 | −13 | quá ít mẫu, chưa kết luận được |
| 7 | Nới mỗi mép 0,1/0,2/0,3 U15 | +3,6 / +7,0 / +0,9 | | nới ra không tốt hơn dải gốc (+10,6) |
| 8 | Ngưỡng bật 0,5/1/1,5/2 U15 | +1,0 / +10,6 / +9,0 / +5,6 | | hiệu ứng nằm ở cú bật 1–1,5 U15 (NQ 55–80 điểm, GC 8–12 giá); bật nhỏ 0,5 U15 thì như ngẫu nhiên |
| 9 | Lần chạm thứ 1/2/3 sau cú rời đi | +11,2 / +11,4 / −2,7 | | lần 1 và lần 2 còn tác dụng, **lần 3 hết** |

**Giá đảo ở đâu trong vùng** (bộ "gộp 3 ngày, 2 cụm/ngày", tính trên tổng số lần chạm):
- Đảo trong 0–0,3 U15 đầu tiên tính từ mép gần: **18,5 %** ở vùng thật, so với 9,6 % ở đối chứng. Đây là chỗ khác biệt rõ nhất.
- Quay đầu sớm, cách mép gần 0,2–0,6 U15: khoảng 36 % ở **cả** vùng thật lẫn đối chứng. Đây là đặc tính chung của mọi mức giá, không phải "chưa vẽ râu". Vì vậy nới vùng ra phía ngoài không giúp.

## Kết luận (chưa kiểm định)

1. Kiểu vùng của Trader Dale **có lợi thế đo được**, với đủ các điều kiện sau:
   - Dùng cụm khối lượng của 2–3 phiên ngày gần nhất, chỉ 1–2 cụm nặng nhất mỗi ngày.
   - Vẽ thành dải khoảng 0,6 U15 (NQ khoảng 30–35 điểm, GC khoảng 5 giá), không vẽ một đường.
   - Giá phải đã **rời cụm mạnh**: ≥ 3 U15 trong ≤ 4 nến M15 (≤ 1 giờ).
   - Rời lên thì là hỗ trợ, rời xuống thì là kháng cự.
   - Chỉ dùng cho lần chạm thứ 1 và thứ 2.
2. Kết quả: khoảng **35 % đảo tại vùng**, so với 24 % ở mức giá bất kỳ đã bị bỏ đi mạnh (Δ +10 đến +11 điểm %).
   - So với một mức chạm ngẫu nhiên thông thường (khoảng 31–33 %) thì vùng này chỉ nhỉnh hơn một chút.
   - Lợi thế thật nằm ở chỗ: khi giá quay về một vùng nó đã bỏ đi mạnh, **nếu ở đó có cụm khối lượng dày thì giá hay dừng ở mép gần**; nếu không có thì giá hay xuyên qua.
3. Gộp các cụm chồng nhau giữa các ngày không làm mất hiệu ứng. Nhưng vùng hợp lưu 2–3 ngày còn quá ít mẫu để nói là mạnh hơn.
4. Cụm tuần trước và cụm cũ hơn 3 ngày không giúp cho scalp M15.
5. Mẫu nhỏ: 160–180 lần chạm, khoảng [5–95 %] rộng. NQ TRAIN của một số cấu hình chỉ dương nhẹ. Cần thêm NQU26, NQM26, NQH26 để kiểm lại.

## Lệnh chạy lại

```bash
VM_CACHE_DIR=$TEMP/vmc python vong15.py 1 2 2b 3 4b 5b 6b 7 8 9
```
