# Sàn tối thiểu (hợp đồng) của chấm Bid/Ask: 9 hay lớn hơn? (2026-11-24)

> Ghi chú đo đạc + spec cho C#. Mọi con số ở đây là **khớp mật độ / vị trí hiển thị với chart CORVEN**, không phải lợi thế giao dịch đã kiểm định.
> Chưa sửa C#, chưa commit. Luật Python dùng lại đúng bản đã khớp C# từng chấm (`../adaptive_2026-11-24/dot_rule.py`); `check_lib.py` ra lại đúng 5 số chuẩn cũ (GC M1 80.386 / 39.918, NQ M1 106.953 / 47.895…), và NQ M1 bộ Không sót sàn 9 = **77.661**, trùng số trong commit sửa lỗi `074e236`.

Luật đang xét: ngưỡng = max(k × B, **SÀN**); B = trung bình (trên N nến trước) của trung vị volume mỗi ô; chấm phải lớn hơn hẳn cùng bên trong ±w tick, w = max(4, round(biên độ TB / 6)); che chấm xanh cách chấm đỏ ≤ h tick. Bộ số: Không sót k 2,0 · che 2; Trung gian k 2,4 · che 2; Ít nhiễu k 2,8 · che max(6; 0,75w). Sau commit `074e236` sàn luôn lấy từ ô "Sàn tối thiểu" của người dùng.

Dữ liệu: footprint 90 ngày một hợp đồng (GC 87.362 nến M1 từ 11/08; NQ 71.047 nến M1 từ 14/09), pickle của `../nq_calib_2026-11-24`. Phiên (UTC): Á 22:00–07:00, Âu 07:00–13:30, Mỹ 13:30–22:00.

## 0. Kết luận ngắn

1. **Sàn không nên lớn hơn 9.** Trên mẫu CORVEN GC M1 (885 chấm), chính các ô CORVEN vẽ chấm có volume trung vị 12 hợp đồng, phân vị 5 là 6 hợp đồng: 10% chấm CORVEN dưới 7, **27% dưới 9**, 49% dưới 12, 66% dưới 15. Sàn 12 đã tự loại một nửa số chấm của CORVEN trước khi xét bất cứ điều kiện nào khác.
2. **Đề xuất sàn mặc định = 7** (một số, mọi mã, mọi khung). So với sàn 5: recall GC M1 0,70 → 0,675 (mất 21/885 chấm), precision 0,85 → 0,87; chấm kiểu "6 Bid" biến mất. Sàn 9: recall còn 0,60 (mất 89 chấm), precision 0,90; mất chủ yếu ở phiên Á (0,68 → 0,43), phiên Âu/Mỹ mất ít (0,71 → 0,65 và 0,71 → 0,68). Giữ 9 là lựa chọn hiển thị chấp nhận được nếu chỉ xem phiên Âu/Mỹ.
3. **Sàn chỉ có tác dụng ở M1** (và một ít ở M5 phiên Á). Từ M15 trở lên, sàn nào ≤ 12 cũng cho số chấm y hệt (sàn 20 đổi dưới 4%). Không cần công thức sàn theo khung; muốn bớt chấm ở khung lớn thì đổi bộ số, không phải sàn.
4. **Thứ làm màn hình người học nhiễu nhất là ô "nổ ở mọi mức giá", không phải sàn.** Đúng đoạn chart chụp (NQ M1 24/11, 58 nến): bật ô này 344 chấm (5,9 chấm/nến); tắt còn 141; tắt + sàn 7 còn 116 (2,0/nến); tắt + sàn 9 còn 77 (1,33/nến). Ô này làm NQ M15 lên 13 chấm/nến, NQ H1 41 chấm/nến. Mặc định phải **tắt**.
5. Bộ số mặc định giữ **Không sót**. Nếu vẫn thấy dày trên vàng: chuyển **Trung gian + sàn 7** thay vì nâng sàn lên 9: trên GC M1 cùng mật độ (0,81 so với 0,83 chấm/nến) mà recall / precision 0,61 / 0,93 so với 0,60 / 0,90, và nó còn giảm chấm ở M15 trở lên (sàn thì không). Riêng NQ giờ thưa (phiên Á/Âu) thì sàn mới là thứ cắt chấm (đoạn chart 24/11: Trung gian · 7 còn 106 chấm, Không sót · 9 còn 77).
6. MGC / MNQ: **không có dữ liệu** footprint trong kho, chưa đo.

## 1. Sàn × bộ số × mã × khung (`floor_grid.py` → `out_floor_grid.csv`, `out_floor_grid.txt`)

File CSV có đủ 660 dòng: 11 sàn (0, 5, 7, 9, 10, 12, 15, 18, 20, 25, 30) × 3 bộ × 2 mã × 5 khung × tắt/bật "nổ ở mọi mức giá", mỗi dòng có chấm/nến từng phiên, tỉ lệ nến mà sàn quyết định (k × B < sàn) từng phiên, tỉ lệ chấm bị sàn cắt, k × B trung vị từng phiên.

### 1.1 Chấm/nến (mọi phiên), "nổ ở mọi mức giá" tắt

Bộ **Không sót**:

| Sàn | 5 | 7 | 9 | 10 | 12 | 15 | 18 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|
| GC M1 | 0,92 | 0,85 | 0,72 | 0,65 | 0,51 | 0,36 | 0,25 | 0,21 | 0,13 | 0,08 |
| GC M5 | 1,50 | 1,50 | 1,50 | 1,49 | 1,44 | 1,31 | 1,14 | 1,02 | 0,76 | 0,54 |
| GC M15 | 1,74 | 1,74 | 1,74 | 1,74 | 1,74 | 1,74 | 1,71 | 1,68 | 1,53 | 1,33 |
| GC M30 | 1,90 | 1,90 | 1,90 | 1,90 | 1,90 | 1,90 | 1,90 | 1,89 | 1,86 | 1,78 |
| GC H1 | 2,07 | 2,07 | 2,07 | 2,07 | 2,07 | 2,07 | 2,07 | 2,07 | 2,07 | 2,06 |
| NQ M1 | 1,50 | 1,34 | 1,09 | 0,99 | 0,82 | 0,67 | 0,57 | 0,53 | 0,43 | 0,34 |
| NQ M5 | 2,07 | 2,07 | 2,07 | 2,06 | 1,99 | 1,78 | 1,52 | 1,38 | 1,12 | 0,95 |
| NQ M15 | 2,34 | 2,34 | 2,34 | 2,34 | 2,34 | 2,33 | 2,30 | 2,26 | 2,05 | 1,75 |
| NQ M30 | 2,42 | 2,42 | 2,42 | 2,42 | 2,42 | 2,42 | 2,42 | 2,42 | 2,40 | 2,31 |
| NQ H1 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 | 2,58 |

Bộ **Trung gian** và **Ít nhiễu** (chỉ M1 và M5; từ M15 trở lên gần như không đổi theo sàn: Trung gian GC 1,26 / 1,36 / 1,50, NQ 1,77 / 1,84 / 2,05; Ít nhiễu GC 0,81 / 0,84 / 0,91, NQ 1,08 / 1,12 / 1,25):

| Sàn | 5 | 7 | 9 | 10 | 12 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| Trung gian GC M1 | 0,70 | 0,67 | 0,60 | 0,56 | 0,46 | 0,34 | 0,20 | 0,08 |
| Trung gian GC M5 | 1,11 | 1,11 | 1,10 | 1,10 | 1,09 | 1,04 | 0,87 | 0,51 |
| Trung gian NQ M1 | 1,11 | 1,06 | 0,91 | 0,83 | 0,68 | 0,54 | 0,42 | 0,29 |
| Trung gian NQ M5 | 1,56 | 1,56 | 1,56 | 1,56 | 1,54 | 1,46 | 1,18 | 0,79 |
| Ít nhiễu GC M1 | 0,49 | 0,48 | 0,46 | 0,44 | 0,38 | 0,29 | 0,18 | 0,08 |
| Ít nhiễu GC M5 | 0,74 | 0,74 | 0,74 | 0,74 | 0,74 | 0,73 | 0,65 | 0,43 |
| Ít nhiễu NQ M1 | 0,75 | 0,74 | 0,67 | 0,63 | 0,53 | 0,42 | 0,32 | 0,22 |
| Ít nhiễu NQ M5 | 0,99 | 0,99 | 0,99 | 0,99 | 0,99 | 0,97 | 0,86 | 0,59 |

### 1.2 Theo phiên (Á / Âu / Mỹ), bộ Không sót, "nổ ở mọi mức giá" tắt

Chấm/nến:

| Sàn | 5 | 7 | 9 | 12 | 15 | 20 |
|---|---|---|---|---|---|---|
| GC M1 | 0,90 / 0,99 / 0,89 | 0,76 / 0,95 / 0,87 | 0,56 / 0,83 / 0,81 | 0,33 / 0,59 / 0,66 | 0,21 / 0,40 / 0,49 | 0,11 / 0,24 / 0,30 |
| GC M5 | 1,58 / 1,70 / 1,23 | 1,58 / 1,70 / 1,23 | 1,58 / 1,70 / 1,23 | 1,45 / 1,69 / 1,22 | 1,16 / 1,63 / 1,21 | 0,72 / 1,28 / 1,15 |
| NQ M1 | 1,49 / 1,66 / 1,39 | 1,22 / 1,45 / 1,39 | 0,83 / 1,10 / 1,38 | 0,46 / 0,68 / 1,35 | 0,28 / 0,44 / 1,30 | 0,15 / 0,24 / 1,21 |
| NQ M5 | 1,87 / 2,46 / 1,98 | 1,87 / 2,46 / 1,98 | 1,86 / 2,46 / 1,98 | 1,74 / 2,35 / 1,98 | 1,42 / 2,03 / 1,97 | 0,87 / 1,38 / 1,95 |

Tỉ lệ nến mà **sàn quyết định** (k × B < sàn), % Á / Âu / Mỹ:

| Sàn | 5 | 7 | 9 | 12 | 15 | 20 |
|---|---|---|---|---|---|---|
| GC M1 Không sót | 23 / 2 / 4 | 71 / 31 / 18 | 91 / 66 / 40 | 99 / 90 / 75 | 100 / 97 / 91 | 100 / 99 / 98 |
| GC M1 Ít nhiễu | 1 / 0 / 0 | 23 / 2 / 4 | 60 / 20 / 13 | 89 / 60 / 35 | 97 / 83 / 62 | 100 / 96 / 89 |
| GC M5 Không sót | 0 / 0 / 0 | 0 / 0 / 0 | 7 / 0 / 0 | 44 / 4 / 1 | 78 / 28 / 9 | 97 / 79 / 32 |
| NQ M1 Không sót | 21 / 12 / 0 | 74 / 59 / 1 | 95 / 83 / 4 | 100 / 95 / 9 | 100 / 98 / 14 | 100 / 100 / 27 |
| NQ M1 Ít nhiễu | 1 / 0 / 0 | 21 / 12 / 0 | 62 / 48 / 1 | 93 / 80 / 3 | 99 / 92 / 7 | 100 / 98 / 13 |
| NQ M5 Không sót | 0 / 0 / 0 | 1 / 0 / 0 | 5 / 4 / 0 | 34 / 31 / 0 | 70 / 68 / 1 | 90 / 93 / 3 |
| M15 trở lên (mọi bộ, mọi mã, mọi phiên gộp) | 0 | 0 | 0 | 0 | ≤ 3 | ≤ 18 |

Mức k × B trung vị với k = 2,0 (Á / Âu / Mỹ): GC M1 6,0 / 8,0 / 9,8 · GC M5 12,4 / 16,8 / 22,8 · GC M15 22 / 29 / 41 · NQ M1 **6,0 / 6,5 / 25,0** · NQ M5 13,2 / 13,3 / 55,8 · NQ M15 23,5 / 22,5 / 94.

Cách đọc:
- Sàn là điều kiện của **M1**. Ở M5 sàn ≤ 9 gần như vô tác dụng (GC M5 phiên Á 7% số nến); từ M15 trở lên sàn ≤ 12 không đổi được chấm nào trên GC, 2 chấm trên NQ.
- NQ M1 phiên Mỹ: k × B đã là 25, sàn ≤ 20 gần như không đổi gì (1,39 → 1,21 chấm/nến). Sàn trên NQ chỉ cắt phiên Á và Âu (giờ thưa), đúng giờ người học chụp chart.
- Sàn càng cao thì ba bộ số càng giống nhau: từ sàn 15 trên GC M1, Không sót / Trung gian / Ít nhiễu = 0,36 / 0,34 / 0,29, tức bộ số mất nghĩa.

### 1.3 Ô "nổ ở mọi mức giá" (w = 0), bộ Không sót, chấm/nến mọi phiên

| | Tắt, sàn 5 | Bật, sàn 5 | Bật, sàn 7 | Bật, sàn 9 | Bật, sàn 12 | Bật, sàn 20 |
|---|---|---|---|---|---|---|
| GC M1 | 0,92 | 1,58 | 1,42 | 1,16 | 0,78 | 0,27 |
| GC M5 | 1,50 | 3,06 | 3,06 | 3,05 | 2,91 | 1,87 |
| GC M15 | 1,74 | 4,26 | 4,26 | 4,26 | 4,26 | 3,96 |
| GC H1 | 2,07 | 6,95 | 6,95 | 6,95 | 6,95 | 6,95 |
| NQ M1 | 1,50 | 3,30 | 2,81 | 2,19 | 1,64 | 1,08 |
| NQ M5 | 2,07 | 7,63 | 7,63 | 7,60 | 7,16 | 5,01 |
| NQ M15 | 2,34 | 13,40 | 13,40 | 13,40 | 13,39 | 12,69 |
| NQ M30 | 2,42 | 20,95 | 20,95 | 20,95 | 20,95 | 20,91 |
| NQ H1 | 2,58 | 41,43 | 41,43 | 41,43 | 41,43 | 41,43 |

- Bật ô này nhân số chấm 1,7 lần (GC M1) đến 16 lần (NQ H1). **Sàn không cứu được** ở M5 trở lên: NQ M15 vẫn 12,7 chấm/nến với sàn 20.
- NQ M5 phiên Mỹ bật ô này: 11 chấm/nến ở mọi sàn ≤ 15.
- Bật ô này còn làm lệch màu: chấm đỏ nổ ở mọi ô nên luật che xóa gần hết chấm xanh (NQ M30: 42.521 đỏ + 7.001 xanh; khi tắt là 3.010 + 2.712).
- Bộ Ít nhiễu + bật: NQ M15 4,94, NQ H1 19,8 chấm/nến — vẫn dày.

## 2. So với CORVEN (`floor_corven.py` → `out_floor_corven.csv`, `out_floor_corven.txt`)

Mẫu: GC M1 580 nến / 885 chấm (05–06/11; 148 nến Á, 288 Âu, 144 Mỹ; CORVEN 1,53 chấm/nến). NQ M1 534 nến / 1.205 chấm (06/11; 142 Á, 337 Âu, 55 Mỹ; 2,26 chấm/nến; chart gộp hàng 8 tick). GC M5 26 nến / 16 cụm (18/11). Cách khớp như `dot_recall3.py`: M1 cùng nến, cùng màu, cách ≤ 3 tick; M5 cụm có chấm cùng nến, cùng màu, cách tâm ≤ 5 tick.

### 2.1 Volume tại ô CORVEN vẽ chấm (GC M1) — đo trực tiếp "sàn của CORVEN"

Volume cùng bên (đỏ = Bid, xanh = Ask) lớn nhất trong ±3 tick quanh mỗi chấm CORVEN: phân vị 5 / 10 / 25 / 50 / 75 / 90 = **6 / 6 / 8 / 12 / 17 / 26** hợp đồng.

| Tỉ lệ chấm CORVEN có volume nhỏ hơn sàn | 5 | 7 | 9 | 10 | 12 | 15 | 18 | 20 | 25 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|
| Tất cả (885) | 2% | 10% | 27% | 35% | 49% | 66% | 78% | 81% | 88% | 92% |
| Phiên Á (228) | 2% | 25% | 54% | 67% | 76% | 85% | 90% | 93% | 97% | 97% |
| Phiên Âu (367) | 1% | 4% | 21% | 28% | 49% | 69% | 81% | 84% | 90% | 93% |
| Phiên Mỹ (290) | 3% | 7% | 15% | 19% | 29% | 47% | 65% | 70% | 80% | 87% |

Đây là **trần recall của từng sàn, không phụ thuộc k hay cửa sổ**: sàn 9 thì tối đa bắt được 73% chấm CORVEN, sàn 12 tối đa 51%. (Khớp ±1 tick: 3% / 13% / 32% / 40% / 55% dưới sàn 5 / 7 / 9 / 10 / 12.) Sàn "kiểu CORVEN" trên GC M1 nằm quanh 5–6 hợp đồng.

### 2.2 Recall / precision theo sàn, "nổ ở mọi mức giá" tắt

| Bộ · sàn | GC M1 chấm/nến | GC M1 recall / precision | recall Á / Âu / Mỹ | NQ M1 chấm/nến | NQ M1 recall / precision (chỉ tham khảo) | GC M5: chấm, cụm trùng |
|---|---|---|---|---|---|---|
| CORVEN | 1,53 | | | 2,26 | | khoảng 33, 16 cụm |
| Không sót · 5 | 1,04 | **0,70 / 0,85** | 0,68 / 0,71 / 0,71 | 2,17 | 0,39 / 0,33 | 49, 10/16 |
| Không sót · **7** | 0,97 | **0,675 / 0,87** | 0,61 / 0,70 / 0,69 | 1,56 | 0,34 / 0,40 | 49, 10/16 |
| Không sót · 9 | 0,83 | 0,60 / 0,90 | 0,43 / 0,65 / 0,68 | 1,10 | 0,28 / 0,46 | 49, 10/16 |
| Không sót · 10 | 0,74 | 0,55 / 0,92 | 0,32 / 0,60 / 0,66 | 0,96 | 0,25 / 0,47 | 49, 10/16 |
| Không sót · 12 | 0,57 | 0,45 / 0,96 | 0,24 / 0,46 / 0,61 | 0,70 | 0,21 / 0,52 | 49, 10/16 |
| Không sót · 15 | 0,38 | 0,31 / 0,98 | 0,15 / 0,28 / 0,47 | 0,50 | 0,17 / 0,59 | 49, 10/16 |
| Không sót · 20 | 0,22 | 0,18 / 0,98 | 0,07 / 0,15 / 0,29 | 0,25 | 0,10 / 0,63 | 49, 10/16 |
| Không sót · 30 | 0,09 | 0,08 / 1,00 | 0,03 / 0,07 / 0,13 | 0,12 | 0,04 / 0,66 | 40, 9/16 |
| Trung gian · 5 | 0,83 | 0,61 / 0,92 | 0,58 / 0,61 / 0,63 | 1,78 | 0,38 / 0,39 | 41, 9/16 |
| Trung gian · 7 | 0,81 | 0,61 / 0,93 | 0,56 / 0,61 / 0,63 | 1,45 | 0,34 / 0,42 | 41, 9/16 |
| Trung gian · 9 | 0,74 | 0,56 / 0,94 | 0,43 / 0,59 / 0,63 | 1,03 | 0,28 / 0,48 | 41, 9/16 |
| Ít nhiễu · 5 hoặc 7 | 0,59 | 0,48 / 0,98 | 0,44 / 0,49 / 0,50 | 1,22 / 1,13 | 0,30 / 0,44 và 0,28 / 0,44 | 30, 7/16 |
| Ít nhiễu · 9 | 0,57 | 0,46 / 0,98 | 0,39 / 0,47 / 0,49 | 0,88 | 0,24 / 0,48 | 30, 7/16 |

F1 trên GC M1 (bộ Không sót): sàn 5 **0,767** · 7 **0,761** · 9 0,719 · 10 0,685 · 12 0,611 · 15 0,470.

Cách đọc:
- Từ sàn 5 lên 7: mất 21 chấm CORVEN (recall −2,4 điểm), precision +2,5 điểm, F1 gần như giữ nguyên. Đây là bước nâng sàn duy nhất "gần như miễn phí".
- Từ 7 lên 9: mất thêm 68 chấm (recall −7,6 điểm) đổi lấy precision +2,7 điểm. Phiên Á chịu gần hết (0,61 → 0,43).
- Từ 12 trở lên: recall dưới 0,45; precision đã 0,96 nên không còn gì để mua.
- Ở sàn 5, precision đã 0,85: 85% chấm của indicator trùng chấm CORVEN. Trên GC M1, "nhiễu" (chấm CORVEN không vẽ) chỉ là 15%, và indicator vẫn **thưa hơn** CORVEN (1,04 so với 1,53 chấm/nến).
- **GC M5: sàn ≤ 20 không đổi một chấm nào** (49 chấm, 10/16 cụm). Mẫu chỉ 16 cụm trên một chart.
- **NQ M1 không kết luận được về vị trí** (chart CORVEN gộp 8 tick một hàng, indicator xét từng tick; precision 0,3–0,6 ở mọi sàn). Chỉ dùng mật độ: sàn 5 cho 2,17 chấm/nến, sát CORVEN 2,26; sàn 7 còn 1,56; sàn 9 còn 1,10, tức thưa bằng nửa CORVEN.
- Từ M15 trở lên **không có mẫu CORVEN**, và sàn cũng không có tác dụng ở đó.

### 2.3 "Nổ ở mọi mức giá" bật, so với CORVEN

| Bộ · sàn | GC M1 chấm/nến | GC M1 recall / precision | NQ M1 chấm/nến | GC M5: chấm, cụm trùng |
|---|---|---|---|---|
| CORVEN | 1,53 | | 2,26 | khoảng 33, 16 cụm |
| Không sót · 5 | 1,70 | 0,79 / 0,88 | **5,28** | **127**, 12/16 |
| Không sót · 7 | 1,53 | 0,755 / 0,89 | 3,25 | 127, 12/16 |
| Không sót · 9 | 1,18 | 0,64 / 0,91 | 2,00 | 127, 12/16 |
| Trung gian · 7 | 1,13 | 0,66 / 0,945 | 2,75 | 89, 10/16 |
| Ít nhiễu · 7 | 0,78 | 0,51 / 0,98 | 1,87 | 53, 7/16 |

- Riêng **GC M1**, bật ô này lại khớp CORVEN hơn: recall 0,70 → 0,79 và precision 0,85 → 0,88; với sàn 7 mật độ đúng bằng CORVEN (1,53). Tức ở M1 vàng, CORVEN vẽ cả các ô lớn nằm sát nhau.
- Nhưng ở **GC M5** nó cho 127 chấm trên 26 nến (CORVEN khoảng 33) để thêm 2 cụm; ở **NQ M1** 5,28 chấm/nến (gấp 2,3 lần CORVEN); ở khung lớn hơn thì bảng 1.3.
- Kết luận: ô này chỉ đáng bật khi xem **GC M1**, và khi bật thì nên đi cùng sàn 7–9. Không dùng làm mặc định.

## 3. Đúng đoạn chart người học chụp (`shot_check.py` → `out_shot_check.txt`)

NQ M1 ngày 24/11, 18:15–19:12 giờ chart (UTC+7) = 11:15–12:12 UTC, phiên Âu, 58 nến.
- File `fp_NQZ26_XCME_Time_20260826-20261124_90d.csv` chỉ đến 12:07 UTC (53/58 nến). Dùng `fp_NQZ26_XCME_Time_20261115-20261124_8d13h_2.csv` (đến 12:17 UTC, đủ 58/58).
- Trong cửa sổ: B trung vị **2,75** (2,35–3,65) → 2,0 × B = **5,5**, đúng dòng "ngưỡng 5.5" trên ảnh (xác nhận luôn giờ chart là UTC+7). 100% số nến có 2,0 × B < 9, 76% có 2,0 × B < 7: cả đoạn này **sàn là thứ quyết định ngưỡng**. Biên độ TB 88 tick, w = 15.
- Có **15 chấm đỏ "6 Bid (Ask 1)"** với cấu hình trên ảnh (Không sót, sàn bị ghi đè thành 5, nổ ở mọi mức giá), ngưỡng 5,0–5,6; ba chấm có ngưỡng đúng 5,5 ở 18:45 (26432,50), 18:47 (26446,50), 18:52 (26450,50) giờ chart. Xác nhận lỗi.
- Với cấu hình trên ảnh: 344 chấm, trong đó **231 chấm (67%) có volume dưới 9**, 117 chấm (34%) dưới 7.

Số chấm trong 58 nến (trong ngoặc: chấm/nến):

| Bộ · "mọi mức giá" | Sàn 5 | 7 | 9 | 10 | 12 | 15 | 20 | 30 |
|---|---|---|---|---|---|---|---|---|
| Không sót · **bật** (như ảnh) | **344 (5,93)** | 237 (4,09) | 130 (2,24) | 105 (1,81) | 69 (1,19) | 36 (0,62) | 13 (0,22) | 7 (0,12) |
| Không sót · tắt | 141 (2,43) | **116 (2,00)** | 77 (1,33) | 68 (1,17) | 46 (0,79) | 27 (0,47) | 11 (0,19) | 7 (0,12) |
| Trung gian · bật | 222 (3,83) | 203 (3,50) | 130 (2,24) | 105 (1,81) | 69 (1,19) | 36 (0,62) | 13 (0,22) | 7 (0,12) |
| Trung gian · tắt | 110 (1,90) | 106 (1,83) | 77 (1,33) | 68 (1,17) | 46 (0,79) | 27 (0,47) | 11 (0,19) | 7 (0,12) |
| Ít nhiễu · bật | 137 (2,36) | 137 (2,36) | 103 (1,78) | 91 (1,57) | 61 (1,05) | 34 (0,59) | 13 (0,22) | 7 (0,12) |
| Ít nhiễu · tắt | 82 (1,41) | 82 (1,41) | 66 (1,14) | 61 (1,05) | 43 (0,74) | 26 (0,45) | 11 (0,19) | 7 (0,12) |

Trong đoạn này: sửa lỗi sàn (5 → 9, vẫn bật mọi mức giá) giảm 344 → 130; **chỉ tắt "mọi mức giá"** giảm 344 → 141; tắt + sàn 7 → 116; tắt + sàn 9 → 77. Từ sàn 9 trở lên bộ Không sót và Trung gian cho số chấm y hệt, vì sàn đã thay hẳn k × B.

## 4. Kết luận và đánh đổi

Tiêu chí của người học: "không nhiễu, nhưng không bỏ sót". Quy thành số: chọn **sàn lớn nhất mà recall so với CORVEN (GC M1) mất không quá 3 điểm và F1 không giảm quá 0,01**. Ngưỡng 3 điểm / 0,01 là do người đo đặt, không phải số đo ra.

| Phương án ("mọi mức giá" tắt) | GC M1 recall / precision / F1 | GC M1 chấm/nến 90 ngày | NQ M1 chấm/nến 90 ngày | Đoạn chart 24/11 | Nhận xét |
|---|---|---|---|---|---|
| Không sót · sàn 5 | 0,70 / 0,85 / 0,767 | 0,92 | 1,50 | 141 | recall cao nhất; còn chấm 5–6 hợp đồng |
| **Không sót · sàn 7 (đề xuất)** | 0,675 / 0,87 / 0,761 | 0,85 | 1,34 | 116 | mất 21/885 chấm CORVEN; hết chấm "6 Bid" |
| Không sót · sàn 9 | 0,60 / 0,90 / 0,719 | 0,72 | 1,09 | 77 | mất 89/885; phiên Á recall 0,43; phiên Âu/Mỹ 0,65 / 0,68 |
| Không sót · sàn 12 | 0,45 / 0,96 / 0,611 | 0,51 | 0,82 | 46 | sót hơn nửa |
| Không sót · sàn 15 trở lên | ≤ 0,31 | ≤ 0,36 | ≤ 0,67 | ≤ 27 | bộ số mất nghĩa; không dùng |
| Trung gian · sàn 7 | 0,61 / 0,93 / 0,735 | 0,67 | 1,06 | 106 | cùng mật độ GC (mẫu CORVEN) với "Không sót · 9" nhưng recall, precision đều nhỉnh hơn; giảm cả khung lớn |

**Đo được:**
- CORVEN vẽ chấm ở ô 6–8 hợp đồng trên GC M1 (27% chấm dưới 9). Sàn > 9 chắc chắn sót nhiều.
- Sàn chỉ tác động M1 (và M5 phiên Á từ sàn 12). Không cần sàn theo khung, không cần sàn = c × B (đó chính là k).
- "Nổ ở mọi mức giá" là nguồn nhiễu chính ở NQ và ở mọi khung từ M5 trở lên.

**Là lựa chọn hiển thị (không đo ra được đáp án duy nhất):**
- 7 hay 9. Số liệu nghiêng về 7 theo tiêu chí trên; 9 hợp lý nếu chỉ xem phiên Âu/Mỹ và muốn thưa hơn (đổi 3–6 điểm recall phiên Âu/Mỹ lấy 3–4 điểm precision).
- Bộ số mặc định. Giữ Không sót vì recall; Trung gian là nấc giảm nhiễu kế tiếp.

**Chỗ mẫu yếu:**
- Recall / precision chỉ có ở **GC M1** (885 chấm, 2 ngày 05–06/11). Phiên Á 228 chấm.
- **NQ**: không có mốc vị trí đáng tin (chart gộp 8 tick), chỉ có mật độ 2,26 chấm/nến của một ngày, 55/534 nến là phiên Mỹ. Sàn 7 trên NQ là suy từ GC cộng mật độ, không phải đo recall.
- **GC M5**: 16 cụm; sàn không đổi kết quả nên không ảnh hưởng quyết định.
- **M15 trở lên**: không có mẫu CORVEN; sàn không có tác dụng.
- **MGC / MNQ**: kho `data-export/` không có footprint MGC hay MNQ, nhật ký `bigtrade-log` cũng chỉ có GC và NQ. Chưa đo. k × B tự co theo volume của mã, còn sàn tính bằng hợp đồng thì không; khi có export MGC/MNQ M1 cần chạy lại `floor_grid.py` (xem tỉ lệ nến mà sàn quyết định) trước khi tin sàn 7 trên hai mã này. Tạm thời dùng chung một ô.

## 5. Spec cho C# (Opus)

Không có công thức mới. Chỉ đổi mặc định và chữ trên ô cài đặt.

| Ô | Hiện tại | Đề xuất |
|---|---|---|
| `CellBigMinSide` "Sàn tối thiểu (hợp đồng)" | 9 | **7** |
| `CellDotFloorEnabled` "Dùng sàn tối thiểu" | bật | bật (giữ) |
| `CellDotPreset` "Bộ số chấm" | 0 (Không sót) | 0 (giữ) |
| `CellDotAllLevels` "Nổ ở mọi mức giá" | tắt | tắt (giữ) |

Chữ gợi ý cho ô:
- Sàn: "Sàn tối thiểu (hợp đồng) · chỉ có tác dụng ở M1; 7 = mất ít chấm CORVEN nhất, 9 = thưa hơn, trên 9 sót nhiều".
- Mọi mức giá: sửa "±4 tick" thành "±w tick" (w đã tự co theo khung) và thêm "· chỉ nên bật ở GC M1; khung M5 trở lên và NQ sẽ rất dày".
- Người học đang lưu sẵn sàn 9 và bật "mọi mức giá" trong cấu hình chart: đổi mặc định không đổi chart đang mở; cần báo người học tự tắt ô "mọi mức giá" và chọn 7 hoặc 9.
- Kiểm dấu vân tay cache có chứa giá trị sàn (`CellBigMinSide` đang nằm trong chuỗi) để đổi mặc định là cache tự làm lại.

### 5.1 Ví dụ nhỏ cho unit test (đã chạy đạt trong `floor_selftest.py`)

`unified(B, R, k, sàn, tỉ lệ che, che tối thiểu)` → (ngưỡng, w, h):

| B | R | k | Sàn | → ngưỡng, w, h | Ghi chú |
|---|---|---|---|---|---|
| 2,75 | 88 | 2,0 | 7 | 7,0 · 15 · 2 | đoạn chart 24/11: 5,5 < 7 |
| 2,75 | 88 | 2,0 | 9 | 9,0 · 15 · 2 | |
| 2,75 | 88 | 2,0 | 5 | 5,5 · 15 · 2 | lỗi cũ |
| 4,0 | 20 | 2,0 | 7 | 8,0 · 4 · 2 | k × B > sàn |
| 3,5 | 30 | 2,0 | 7 | 7,0 · 5 · 2 | k × B = sàn |
| 3,0 | 16 | 2,8 (Ít nhiễu) | 7 | 8,4 · 4 · 6 | |
| 2,0 | 16 | 2,8 (Ít nhiễu) | 7 | 7,0 · 4 · 6 | |
| 3,0 | 16 | 2,0 | 0 (tắt sàn) | 6,0 · 4 · 2 | |

Một nến, các ô (tick, Bid, Ask) = (100, 6, 1), (101, 1, 2), (106, 2, 7), (112, 9, 0), (113, 3, 8), (120, 1, 6); w = 4, che 2:

| Ngưỡng | Chấm xanh | Chấm đỏ | Ghi chú |
|---|---|---|---|
| 5,5 | 106, 120 | 100, 112 | xanh 113 (8) cách đỏ 112 là 1 tick → bị che |
| 7,0 | 106 | 112 | đỏ 100 (6 Bid) và xanh 120 (6) mất |
| 9,0 | (không) | 112 | |
| 7,0 với w = 0 | 106 | 112 | |

Các ô (100, 8, 0), (102, 9, 0), (103, 7, 0), (110, 0, 7), ngưỡng 7, che 2: w = 4 → xanh 110, đỏ 102; **w = 0 → xanh 110, đỏ 100, 102, 103**.

Chuỗi nến: 5 nến nền giống nhau, mỗi nến 13 ô tick 100…112 với (Bid 2, Ask 1, volume 3) → B = 3, R = 12. Nến xét (tick, Bid, Ask, volume) = (100, 6, 1, 7), (105, 7, 0, 7), (112, 1, 6, 7), (118, 0, 9, 9), bộ Không sót, N = 20:
- sàn 7 → ngưỡng 7,0, w 4, che 2 → xanh [118], đỏ [105];
- sàn 5 → ngưỡng 6,0 → xanh [112, 118], đỏ [100, 105].

### 5.2 Số chấm chuẩn để so C# = Python (`out_golden_counts.csv`; tổng (đỏ + xanh))

CSV dựng bằng `../nq_calib_2026-11-24/tf_csv.py <phút> <thư mục> <NQ|GC>`, chạy `perf/Golden stophunt` với `--set CellBigMinSide=<sàn> --set CellDotPreset=<0|1|2>`. "Nổ ở mọi mức giá" tắt:

| | Bộ | Sàn 5 | **Sàn 7** | Sàn 9 | Sàn 12 |
|---|---|---|---|---|---|
| GC M1 (87.362 nến) | Không sót | 80.386 (47.288 + 33.098) | **74.016 (43.378 + 30.638)** | 62.768 (36.495 + 26.273) | 44.902 (25.744 + 19.158) |
| | Trung gian | 60.884 (35.118 + 25.766) | 58.726 (33.816 + 24.910) | 52.783 (30.258 + 22.525) | 40.424 (22.983 + 17.441) |
| | Ít nhiễu | 42.827 (26.544 + 16.283) | 42.383 (26.253 + 16.130) | 39.918 (24.583 + 15.335) | 32.797 (19.936 + 12.861) |
| GC M15 | Không sót | 10.238 (5.727 + 4.511) | 10.238 | 10.238 | 10.238 |
| | Trung gian | 7.402 (4.054 + 3.348) | 7.402 | 7.402 | 7.402 |
| | Ít nhiễu | 4.747 (2.943 + 1.804) | 4.747 | 4.747 | 4.747 |
| NQ M1 (71.047 nến) | Không sót | 106.953 (58.967 + 47.986) | **95.244 (52.448 + 42.796)** | 77.661 (42.541 + 35.120) | 58.428 (31.896 + 26.532) |
| | Trung gian | 78.871 (42.981 + 35.890) | 75.173 (40.964 + 34.209) | 64.422 (34.943 + 29.479) | 48.408 (26.105 + 22.303) |
| | Ít nhiễu | 53.201 (31.667 + 21.534) | 52.519 (31.248 + 21.271) | 47.895 (28.365 + 19.530) | 37.388 (21.826 + 15.562) |
| NQ M15 | Không sót | 11.061 (5.906 + 5.155) | 11.061 | 11.061 | 11.059 (5.905 + 5.154) |
| | Trung gian | 8.357 (4.460 + 3.897) | 8.357 | 8.357 | 8.357 |
| | Ít nhiễu | 5.118 (3.356 + 1.762) | 5.118 | 5.118 | 5.118 |
| NQ M30 | Không sót | 5.722 (3.010 + 2.712) | 5.722 | 5.722 | 5.722 |
| | Trung gian | 4.356 (2.269 + 2.087) | 4.356 | 4.356 | 4.356 |
| | Ít nhiễu | 2.652 (1.733 + 919) | 2.652 | 2.652 | 2.652 |

"Nổ ở mọi mức giá" **bật** (`--set CellDotAllLevels=true`), bộ Không sót:

| | Sàn 7 | Sàn 9 |
|---|---|---|
| GC M1 | 124.016 (83.628 + 40.388) | 101.039 (67.241 + 33.798) |
| GC M15 | 25.033 (17.925 + 7.108) | 25.033 |
| NQ M1 | 199.616 (131.563 + 68.053) | 155.681 (102.824 + 52.857) |
| NQ M15 | 63.384 (51.482 + 11.902) | 63.384 |
| NQ M30 | 49.522 (42.521 + 7.001) | 49.522 |

- Bản nhanh đã so với bản chuẩn từng nến (`dot_rule.run_reference`) trên GC M1 và NQ M1, bộ Không sót, sàn 7: trùng từng chấm (74.016 và 95.244). Các ô khác trong bảng là bản nhanh.
- `out_golden_by_day.csv`: số chấm đỏ / xanh theo ngày (bộ Không sót, sàn 7, tắt mọi mức giá) cho 5 ô trên, để dò ngày lệch nếu C# khác.
- Số M15 / M30 không đổi theo sàn là đúng (k × B luôn lớn hơn sàn); NQ M15 sàn 12 lệch 2 chấm là thật.
- Số "mọi mức giá bật" chưa từng được so với C# (golden trước đây chỉ chạy chế độ tắt); nếu lệch, kiểm chỗ che vẫn tính theo w thật khi w dùng cho điều kiện lớn nhất là 0 (`UnifiedDots.Apply`).

## 6. Danh sách script (chạy trong thư mục này, `PYTHONIOENCODING=utf-8`)

| Script | Việc | Kết quả |
|---|---|---|
| `floor_lib.py` | dùng chung: tìm một lần các ô đạt k × B, rồi áp từng sàn + luật che | |
| `check_lib.py` | cách tính nhanh theo sàn ra đúng số chuẩn cũ | 5/5 đạt |
| `floor_grid.py` | sàn × bộ × mã × khung × phiên × mọi mức giá | `out_floor_grid.csv`, `out_floor_grid.txt` |
| `floor_corven.py` | recall / precision theo sàn; volume tại ô CORVEN vẽ chấm | `out_floor_corven.csv`, `out_floor_corven.txt` |
| `shot_check.py` | đoạn chart NQ M1 24/11 | `out_shot_check.txt` |
| `floor_selftest.py` | ví dụ unit test, bản nhanh = bản chuẩn, số chấm chuẩn | `out_floor_selftest.txt`, `out_golden_counts.csv`, `out_golden_by_day.csv` |

Cần pickle `F_/S_{GC,NQ}_m{1,5,15,30,60}.pkl` ở `../nq_calib_2026-11-24/` và `../corven_m5_2026-11-18/F_m5.pkl` (không commit).

## Đã implement (Opus, 2026-11-24)

- Mặc định sàn **giữ 9**, không đổi sang 7 như đề xuất: người học đang thấy nhiễu và hỏi sàn 9 hay lớn hơn; số đo cho thấy trên 9 sót nhiều, còn 7 hay 9 là lựa chọn hiển thị (7 → 9 mất 68/885 chấm CORVEN, chủ yếu phiên Á). Người học muốn ít sót hơn thì đặt 7.
- Đổi chữ ô sàn ("chỉ tác dụng ở M1 — 9 thưa, 7 ít sót, trên 9 sót nhiều") và ô "Nổ ở mọi mức giá" ("rất dày ở NQ và từ M5, nên tắt").
- C# = Python: GC M1 sàn 7 74.016 (43.378 + 30.638), sàn 9 62.768 (36.495 + 26.273); NQ M1 sàn 7 95.244 (52.448 + 42.796), sàn 9 77.661. Ví dụ nhỏ mục 5.1 nằm trong tests/AdaptiveTests.cs.
