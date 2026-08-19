# Kết quả đo — mốc nào đáng vẽ (2026-08-18)

> ## ⛔ FILE NÀY ĐÃ LỖI THỜI — ĐỌC `MEASURE-DENSE-RESULTS.md` THAY THẾ (2026-08-19)
> Toàn bộ số liệu dưới đây chạy trên `Data_Footprint_Export.csv`, file này chỉ có
> **657 hợp đồng/phiên** — mỏng hơn dữ liệu thật **218 lần**. Profile dựng từ đó gần
> như là nhiễu, nên mọi kết luận ở dưới không đáng tin.
> Bản đo lại trên **474 phiên dày (143k hợp đồng/phiên)** nằm ở
> `MEASURE-DENSE-RESULTS.md`. Kết luận mới mạnh hơn và rõ hơn: HVN **không** phải mốc
> phản ứng, kiểm bằng 5 cách đo độc lập. Giữ file này chỉ để đối chiếu phương pháp.


Chạy `measure_levels.py` trên `data-export/Data_Footprint_Export.csv` +
`Data_Footprint_Export_bars.csv` (GCQ26, 128 phiên, 2026-02-03 → 07-31).
Giao thức cố định: **SL 3 giá / TP 4,5 giá / tối đa 60 nến M1** (PLAN §A0.3).
**Tiêu chí ĐẠT: n≥30 và biên dưới Wilson 95% > 40%.**

**Tổng số rổ đã thử: 21.** (PLAN §5 — rủi ro khớp quá mức: rổ nào ĐẠT phải kiểm lại
trên hợp đồng/khoảng thời gian khác trước khi lên chart.)

## A0 — nền so sánh

| | n | thắng | CI95 | verdict |
|---|---|---|---|---|
| Mua ngẫu nhiên | 5484 | 40,2% | [38,9%, 41,5%] | KHÔNG ĐẠT |
| Bán ngẫu nhiên | 5472 | 43,9% | [42,6%, 45,2%] | **ĐẠT** ⚠️ |

⚠️ **"Bán ngẫu nhiên đạt" không phải là một loại mốc — đừng hiểu nhầm thành edge.**
Với n rất lớn, khoảng tin cậy co hẹp nên chỉ cần lệch nhẹ khỏi 40% là "đạt" về mặt
thống kê, dù không ai vào lệnh "ngẫu nhiên" thật. Nó cho thấy market giai đoạn này
có hơi lệch xuống một chút (asymmetry SL3/TP4.5), KHÔNG chứng minh bất kỳ mốc nào
hữu ích. Giữ lại con số này để nhắc: **so sánh phải luôn đối chiếu CI, không chỉ %**.

## A2 — so sánh các loại mốc (chưa điều kiện hoá)

| Loại mốc | n | thắng | CI95 | verdict |
|---|---|---|---|---|
| HVN ngày hôm trước | 57 | 43,9% | [31,8%, 56,7%] | KHÔNG ĐẠT |
| POC theo THỜI GIAN (TPO) | 44 | 40,9% | [27,7%, 55,6%] | KHÔNG ĐẠT |
| naked POC gần nhất | 56 | 42,9% | [30,8%, 55,9%] | KHÔNG ĐẠT |
| Đỉnh phiên trước | 31 | 38,7% | [23,7%, 56,2%] | KHÔNG ĐẠT |
| Đáy phiên trước | 47 | 48,9% | [35,3%, 62,8%] | KHÔNG ĐẠT (gần nhất) |
| Số tròn $10 | 68 | 41,2% | [30,3%, 53,0%] | KHÔNG ĐẠT |
| Số tròn $50 | 63 | 41,3% | [30,0%, 53,6%] | KHÔNG ĐẠT |
| S/R thực nghiệm (≥2 ngày xác nhận) | 24 | 41,7% | [24,5%, 61,2%] | CHƯA ĐỦ CA |
| Đối chứng: giá đóng cửa hôm trước | 60 | 45,0% | [33,1%, 57,5%] | KHÔNG ĐẠT |
| Đối chứng: mức ngẫu nhiên trong range | 47 | 48,9% | [35,3%, 62,8%] | KHÔNG ĐẠT |

**Không loại mốc nào vượt ngưỡng.** Đáy phiên trước và mức ngẫu nhiên đều ra 48,9% —
tức mốc "có lý thuyết" không hơn gì mốc bốc đại. Đây là kết quả thứ ba (sau HVN
n=4-6 và n=51) củng cố cùng một điều: ở độ chính xác 3 giá, chưa loại mốc TPO/volume
nào tách khỏi nhiễu.

## A0.5 — đảo hướng

| | n | thắng | verdict |
|---|---|---|---|
| HVN ngày [đảo hướng — "đi tiếp"] | 57 | 36,8% | KHÔNG ĐẠT |

Cả hai chiều (bật lại và đi tiếp) đều dưới nền → HVN ngày, ở mẫu này, không mang
thông tin theo chiều nào cả — không phải mốc bật lại, cũng không phải mốc đi tiếp.

## A1 — điều kiện hoá theo chế độ (Buổi 6)

Phân bố 128 phiên: `khác`=102 · `balance`=17 · `sau_balance`=6.

| Chế độ | n | thắng | verdict |
|---|---|---|---|
| balance | 9 | 33,3% | CHƯA ĐỦ CA |
| sau_balance | 1 | 100% | CHƯA ĐỦ CA (vô nghĩa với n=1) |
| khác | 46 | 45,7% | KHÔNG ĐẠT |

**Không đo được** — định nghĩa "sau balance" (đòi 2 phiên `balance` liên tiếp rồi
rời hẳn) quá hiếm ở mẫu 128 phiên: chỉ 6 ca, sau khi ghép với mốc HVN chỉ còn 1.
Cần export dữ liệu dài hơn nhiều (ước ≥500 phiên) mới đủ số cho nhánh này, hoặc nới
định nghĩa balance (vd overlap ≥35% thay vì 50%) — **chưa làm, ghi lại làm việc dở**.

## A3 — độ nhọn

| | n | thắng | verdict |
|---|---|---|---|
| nhọn (nền ≤1 giá) | 56 | 44,6% | KHÔNG ĐẠT |
| vừa (nền 2-4 giá) | 1 | 0% | CHƯA ĐỦ CA |
| bẹt (nền >4 giá) | 0 | — | không có ca |

**Không đo được có ý nghĩa** — 84% phiên có nền ≤1 giá (đã biết từ trước), nên rổ
"vừa" và "bẹt" gần như trống. Độ nhọn không phân biệt được gì trong mẫu 128 phiên
này, không phải vì giả thuyết sai mà vì gần như mọi mốc HVN ngày đều đã nhọn sẵn.

## A4 — độ ổn định

Chỉ 1/56 ngày có HVN ổn định (≤2 giá đổi so với 2 phiên trước) → **không đo được**.
HVN ngày gần như luôn đổi >2 giá ngày này qua ngày khác — củng cố thêm rằng nó
KHÔNG phải mốc ổn định để canh nhiều phiên, chỉ tham chiếu trong ngày.

---

## Kết luận cho PLAN giai đoạn 3–4

1. **Không có cơ sở bật `SharpnessGate` làm mặc định** (A3 không đo được ý nghĩa
   với mẫu này) — để tắt, chỉ hiển thị con số như PLAN đã dự phòng.
2. **Không loại mốc nào được nâng cấp thành "đã kiểm định"**. Tất cả (HVN, naked
   POC, POC-theo-thời-gian, đỉnh/đáy, số tròn) giữ nguyên vị trí: **dùng để đọc
   chart, không sinh signal** (CLAUDE.md §5b).
3. **A1 (chế độ balance) chưa đo được vì thiếu dữ liệu**, không phải vì sai — đây
   là việc còn dang dở, không phải kết luận âm. Cần export dài hơn trước khi thử lại.
4. Tiến hành **B1–B4 (giai đoạn 1 của indicator)** không bị chặn bởi kết quả này —
   chúng là cải thiện hiển thị/lọc tầm với, không phụ thuộc việc mốc nào "thắng".
