# Review vòng 3 (Fable, 2026-11-25) — chế độ ngưỡng "Không theo CORVEN"

> Đọc `r3_results.md`, các script `sa3_*.py`, code C# liên quan (`CellBigLogic.cs`, `OrderFlowBubbles.cs`, `perf/Golden/Program.cs`, `tests-dll/Program.cs`), và tự chạy `rv3_chk1.py` (kết quả `out_rv3_chk1.txt`).
> Kết luận: **đủ để chốt**. Spec cuối cho C# ở `SPEC.md`.
> Mọi thứ ở đây vẫn là **định nghĩa hiển thị** ("ô nào lớn bất thường so với chính quá khứ của nó"), **không phải lợi thế giao dịch**. Không bước nào dùng giá chạy sau, không bước nào lấy chart CORVEN làm đích.

## 1. Số vòng 3 có tin được không

| Việc kiểm | Kết quả |
|---|---|
| Tôi cài lại luật **độc lập** (`rv3_chk1.py`: không dùng thư viện của Opus; giờ Chicago lấy từ `zoneinfo` thay cho luật tự viết; ngưỡng bằng sắp xếp danh sách thay cho mảng đếm; không có giới hạn 4095) | Trùng từng con số: GC H1 1.646 / 1.662, GC M15 4.342 / 4.425, NQ M15 5.512 / 5.494, NQ H1 mức 1% 1.295 / 1.329, GC H1 không lân cận 1.771 / 1.805, nạp 8 ngày GC M5 956 / 959 và NQ M15 1.097 / 1.028; Big Trade GC M30 788, NQ M15 864, GC M5 1.913. Số nến ngưỡng chính / dự phòng / chưa có cũng trùng |
| Luật giờ Chicago tự viết có đúng không | Đúng trên dữ liệu: kết quả trùng với `zoneinfo`, và dữ liệu có chứa lần đổi giờ 01/11/2026 |
| Giới hạn 4095 của mảng đếm có ảnh hưởng không | Không. Giá trị bên lớn nhất trong dữ liệu là 2.299 (NQ H1). Khung lớn hơn H1 chưa đo |
| Rò rỉ tương lai trong `sa3_ref.py` | Không thấy. Ngưỡng chính chỉ lấy ngày giao dịch **trước** hôm nay (`e[0] < day`, kể cả khung lân cận); dự phòng, biên độ, hàng đợi Big Trade chỉ nộp sau khi nến đóng; nến cuối file không nộp. Tự kiểm cắt dữ liệu 60% trùng |
| Ngưỡng của nến đang chạy có đổi khi nến đóng không | Không: ngưỡng và cửa sổ gộp chỉ phụ thuộc nến đã đóng trước. Chấm trên nến đang chạy vẫn có thể hiện rồi mất khi ô bên cạnh lớn lên; đó là bước chọn, chế độ cũ cũng vậy |
| Ví dụ tính tay cho unit test | Tôi dựng 4 nến M30 giả, tính tay, rồi chạy `sa3_ref.py`: ra đúng (ghi ở `SPEC.md` mục 8) |
| Số có hợp lý không | Có. Ngưỡng theo phiên đúng thứ tự (NQ M1: Á 10, Âu 11, Mỹ 31; GC M5: 18 / 24 / 27). Chấm/nến ba phiên chênh không quá 1,7 lần. Với chọn tham lam, số "nhìn thấy" bằng đúng số cũ, đúng như cách dựng |

Trả lời 8 vấn đề Opus ghi:
1. Golden chưa có `--from`: chấp nhận cách dùng file cắt sẵn. File nằm trong thư mục tạm nên có thể mất; chạy lại `python sa3_numbers.py` là có lại.
2. Tên `sa3_`: đúng.
3. Nến rỗng không có trong dữ liệu: chấp nhận, giữ trong spec vì dữ liệu sống có thể có.
4. Khớp chung vượt 1,25 ở M30 / H1: xem mục 3.
5. Thưa hơn CORVEN 5 lần ở GC M1: xem mục 3. Không chỉnh theo.
6. Nhiễu NQ đoạn chọn 1,2–1,5%: dưới mức 5%. Đoạn chọn NQ chứa tuần chuyển hợp đồng.
7, 8. File tạm và commit: agent chính lo.

## 2. Áp luật chọn viết trước (không bàn lại)

| Luật | Kết quả | Chốt |
|---|---|---|
| Chọn tham lam thay "lớn hơn hẳn" | Đúng cả ba điều trên 12 / 12 ô; chấm tăng 3,9–10,3% | **Chọn tham lam** |
| Không lân cận thay có lân cận | 7 lần trượt so với 1 | **Giữ có lân cận** |
| Tối thiểu 1 ngày thay 2 ngày | 2 lần trượt so với 1 | **Giữ tối thiểu 2 ngày** |
| Mức mặc định | Luật cố định | **2%** |

Cấu hình cuối cho chấm: giờ Chicago · 5 ngày giao dịch trước · gộp khung giờ lân cận · khung chính cần ít nhất 2 ngày · dự phòng 120 phút · nhóm 2% lớn nhất · chọn tham lam.
Trên 6 ô (GC, NQ × M1, M5, M15) × 2 đoạn × 8 tiêu chí: **trượt 1 lần, 0 lần ở đoạn kiểm**. Hai luật đang chạy (bộ "Không sót", bộ "Ít nhiễu") trượt 36 lần mỗi bộ trên cùng thước; điều đó chỉ nói chúng không phải luật phân vị, không nói chúng kém.

Big Trade: phân vị cuốn 240 phút, nhóm 1% lớn nhất (chốt từ vòng 2); vòng 3 ra lại đúng 3.330 / 864 / 1.913 / 788.

## 3. Điểm yếu còn lại (phải viết cho người học, không sửa bằng cách chỉnh số sau khi xem)

1. **Nửa giờ trước giờ mở cửa cổ phiếu Mỹ (13:00–13:30 UTC), NQ từ M15 trở lên.** Khung này mượn mẫu của khung mở cửa nên ngưỡng bị kéo lên. NQ M15 đoạn chọn: 38 / 39 ô sót của "5 ô lớn nhất phiên" nằm ở đây (đạt 0,913, mức yêu cầu 0,97); đoạn kiểm 0,978 (đạt). Bỏ lân cận thì hết sót ở giờ đó nhưng nổ quá mức danh nghĩa ở nhiều ô hơn (7 lần trượt). Tôi không ghép hai cách sau khi đã xem số.
2. **Khung càng lớn, tỉ lệ nổ thật càng cao hơn 2%.** Khớp chung: M1 0,94–1,11; M15 0,93–1,24; M30 / H1 tới 1,25–1,31 ở đoạn chọn. Nghĩa là ở H1 thực tế khoảng 2,5% số ô vượt ngưỡng. Nguyên nhân: tập tham chiếu gộp 5 ngày × 3 khung giờ có mặt bằng khác nhau. M30 / H1 không nằm trong luật chọn; đây là số báo cáo.
3. **Thưa hơn hẳn chế độ theo CORVEN ở M1.** GC M1: 0,28 chấm/nến, CORVEN 1,53, luật đang chạy bộ "Không sót" 0,83. 99,4% chấm thống kê trùng chấm CORVEN nhưng chỉ bắt 22,3% chấm CORVEN. "Không sót" ở chế độ này nghĩa là không sót **ô thuộc nhóm 2% lớn nhất**; nó không hứa vẽ lại mọi chấm CORVEN vẽ. Mức dày hơn 2% (ví dụ 5%) **chưa đo**, nên không đưa vào ô chọn.
4. **Hai ngày đầu của chart.** Khung giờ chưa có 2 ngày trước thì dùng dự phòng 120 phút. Nạp 8 ngày: hai ngày đầu trùng với nạp đủ 0,43–0,70, ngày 3–5 là 0,82–0,995, **từ ngày thứ 6 trùng 1,000**. Vậy chart cần nạp ít nhất 6 ngày giao dịch thì chấm mới không phụ thuộc lượng lịch sử.
5. **Thước "không nhiễu" lỏng.** Một chấm chỉ bị tính là nhiễu khi nằm ngoài nhóm 2 × tỉ lệ nổ trên **cả hai** thước nhìn lại. Nhiễu ≤ 1,5% vì vậy là điều kiện tối thiểu, không phải bằng chứng mạnh.
6. **Big Trade yếu hơn chấm**: NQ chỉ 6 phiên nhật ký, không có đoạn kiểm; đầu phiên Á của NQ ít vòng (khớp 0,68) vì 4 giờ trước đó là phiên Mỹ; chart mới mở phải chờ đủ 500 lệnh đơn mới có ngưỡng.
7. **Chưa đo**: MGC, MNQ, khung dưới M1, khung trên H1, nến không theo thời gian.

## 4. Quyết định cho spec

- Ô chọn chế độ, **mặc định "Theo CORVEN"**. Lý do: (a) bản niêm phong và chuẩn golden cũ giữ nguyên; (b) ở M1 chế độ mới thưa hơn khoảng 3 lần so với chấm người học đang thấy, đổi như vậy phải do người học tự bật; (c) Big Trade NQ mới có 6 phiên.
- Ô "Mức hiếm": 2% (mặc định) / 1% / 0,5%. Chỉ 2% đạt tiêu chí; 1% trượt 7, 0,5% trượt 16 (chủ yếu sót ô lớn nhất ngày). Hai mức sau là lựa chọn "thưa hơn", ghi rõ trong tên ô.
- Big Trade giữ 1% cố định (0,5% bị loại ở vòng 2 vì M15 thiếu mẫu), không gắn với ô "Mức hiếm".
- Khi chế độ mới bật: bỏ qua sàn, bộ số, bộ Nasdaq, luật che, mật độ / sàn / giới hạn vòng của Big Trade. Ô "Nổ ở mọi mức giá" vẫn có tác dụng.
- Nến không theo thời gian hoặc số phút không nguyên: chế độ mới không chạy, indicator dùng chế độ theo CORVEN (chưa đo thì không vẽ như đã đo).

## 5. Việc tiếp theo

Opus viết C# theo `SPEC.md`, test, so từng dấu với số chuẩn (mục 9 của spec). Sau đó Fable đọc lại code và số (vòng 4 của PLAN).
