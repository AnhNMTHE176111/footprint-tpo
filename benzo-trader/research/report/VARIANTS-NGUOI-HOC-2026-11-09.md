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

## Sửa đổi 5 (corven-3): SL thế B mốc cạnh ngay sau cạnh vừa phá

Người học: "chỉ cần dưới range phá + buffer". Cũ: SL = min(đáy cửa sổ, cạnh − dung sai) − đệm ⇒ ca 11:26 SL 4128,0 (dưới cạnh 4129,4 thêm 1,05 dung sai).
Mới: SL = min(đáy cửa sổ, cạnh) − đệm ⇒ ca 11:26 SL 4129,1.

| | n | R TB | WR | nửa 1 / nửa 2 | vào ngẫu nhiên sau CF |
|---|---|---|---|---|---|
| corven-2 | 333 | −0,075 | 33 % | −0,05 / −0,10 | −0,08 |
| **corven-3** | **399** | **+0,02** | 37 % | 0,00 / +0,04 | −0,04 |

Lần đầu dương và hơn vào ngẫu nhiên, nhưng nhỏ và là hậu kiểm (12 tổ hợp) ⇒ chưa đủ chắc. Hệ quả trên ngày 09/11: corven-3 vào lệnh B sell 10:11 VN
(entry 4126,0, SL 4135,1 = cạnh 4134,6 + đệm, entry cách cạnh 8,6 giá vì sửa đổi 1 bỏ giới hạn khoảng cách) — dính SL 11:30 ⇒ ca 11:26 bị chặn bởi luật 1 lệnh mở.

## Lệnh sell 10:11 VN 09/11 — có nên giới hạn nhịp hồi? (đo TRAIN, `variants_corven3_gioihan.py`)

Lệnh 10:11: 22 nến sau nến đóng ngoài, entry cách cạnh 8,6 giá = 3,7 mbr, rủi ro 3,96 mbr (sát trần 4). corven-2 không vào vì SL cũ (trừ dung sai) vượt trần 4 mbr;
corven-3 kéo SL sát cạnh nên lọt trần. Không phải lỗi mã (Python = C#).

| Biến thể (chỉ nhánh "hồi không chạm") | n | R TB | nửa 1 / nửa 2 | ngẫu nhiên |
|---|---|---|---|---|
| corven-3 | 399 | +0,020 | 0,00 / +0,04 | −0,04 |
| CF cách cạnh ≤ 2 mbr | 319 | −0,057 | −0,12 / +0,01 | −0,08 |
| ≤ 2,5 mbr | 353 | −0,020 | −0,12 / +0,09 | −0,09 |
| ≤ 3 mbr | 377 | +0,001 | −0,07 / +0,07 | −0,09 |
| ≤ 10 nến sau phá | 393 | +0,014 | 0,00 / +0,03 | −0,06 |
| ≤ 15 nến sau phá | 399 | +0,029 | +0,01 / +0,05 | −0,07 |
| trần SL 3 mbr (mọi lệnh) | 317 | −0,023 | −0,13 / +0,09 | −0,11 |

Opus: không giới hạn nào cải thiện rõ; giới hạn khoảng cách làm xấu đi ⇒ giữ corven-3, không thêm luật từ một ca.

## corven-4: nhịp hồi không chạm cạnh phải thuộc cú phá (Opus quyết N = 5, Sonnet implement)

Luật: trong nhánh "hồi không cần chạm cạnh" (thế B), nến hồi đầu tiên phải cách nến phá (nến đóng ngoài range đầu tiên, `b.ref`) ≤ N = 5 nến: `min(pb) − b.ref ≤ 5`. Nhánh chạm cạnh, nhánh vùng stacked và SL: không đổi.
Cờ Python `hoi_trong_n_nen` (+ `hoi_max_nen = 5`), C# `CorvenParams.HoiTrongNNen / HoiMaxNen`; `CP()` mặc định và `CorvenCfg.V1()` giữ nguyên (cờ tắt).

| | n | R TB | WR | nửa 1 / nửa 2 | vào ngẫu nhiên sau CF (C2') |
|---|---|---|---|---|---|
| corven-3 | 399 | +0,020 | 37 % | 0,00 / +0,04 | −0,04 |
| **corven-4 (N=5)** | **374** (A 38, B 336) | **−0,023** | 35 % (130 TP / 241 SL / 3 TIME) | −0,054 / +0,007 | −0,047 |

Quét N (TRAIN, `research/variants_hoi_max_nen.py`, mã thật):

| N | n | R TB | nửa 1 | nửa 2 | C2' |
|---|---|---|---|---|---|
| 1 | 268 | −0,197 | −0,313 | −0,074 | −0,113 |
| 2 | 314 | −0,071 | −0,171 | +0,037 | −0,035 |
| 3 | 344 | −0,029 | −0,046 | −0,010 | −0,045 |
| 4 | 361 | −0,021 | −0,056 | +0,014 | −0,056 |
| **5** | **374** | **−0,023** | −0,054 | +0,007 | −0,047 |
| 6 | 383 | 0,000 | −0,047 | +0,047 | −0,060 |
| 7 | 385 | +0,007 | −0,028 | +0,042 | −0,062 |
| 8 | 392 | +0,032 | +0,023 | +0,040 | −0,049 |
| 10 | 395 | −0,005 | −0,017 | +0,006 | −0,072 |
| không giới hạn | 399 | +0,020 | 0,000 | +0,039 | −0,043 |

Opus chọn N=5: N1–N2 kém rõ; từ N3 trở lên chênh nhau trong mức nhiễu (sai số chuẩn ≈ 0,07R) ⇒ không chọn đỉnh N8 (chọn đỉnh trên TRAIN = tự lừa); N=5 là cận trên khoảng người học mô tả (1–5 nến), giữ được nến hồi ở nến 4–5, vẫn loại hồi muộn kiểu 22 nến.

Kết luận: ngang vào ngẫu nhiên, không có lợi thế đo được (hậu kiểm).
Ca 09/11: lệnh sell 10:11 VN (nhịp hồi xa cú phá) không còn; lệnh buy 11:26 VN vào: B buy 4132,3 · SL 4129,1 · TP 4138,7 · mốc cạnh · "trap hồi, bóng đỏ 20 @4131,3" (Python và C# khớp).


## corven-5: Break chỉ còn mốc cạnh vừa phá + gán lệnh cho range gần nhất (Opus quyết, người học duyệt; Sonnet implement)

1. **Bỏ nhánh "vùng stacked làm mốc" của Break.** Break chỉ còn mốc cạnh vừa phá (chạm cạnh như cũ, hoặc hồi không chạm trong ≤ 5 nến). Stacked vẫn là DẤU HIỆU (③d). Cờ Python `b_bo_moc_stacked`, C# `CorvenParams.BBoMocStacked`.
2. **Gán lệnh cho range gần nhất:** nhiều Break cùng nến xác nhận ⇒ xét range có nến đóng ngoài (ref) muộn nhất trước (Fail Break giữ thứ tự cũ). Cờ Python `gan_range_gan_nhat`, C# `GanRangeGanNhat`.

Đo TRAIN 35 phiên (`research/variants_vung_stacked.py`, hậu xử lý ứng viên, Opus):

| Biến thể (nhánh vùng stacked của Break) | n | R TB | nửa 1 | nửa 2 | C2' | lệnh mốc vùng | R lệnh vùng | R lệnh cạnh |
|---|---|---|---|---|---|---|---|---|
| corven-4 (hiện tại) | 374 | −0,023 | −0,054 | +0,007 | −0,047 | 116 | −0,057 | −0,008 |
| gán range gần nhất | 372 | −0,025 | −0,054 | +0,004 | −0,049 | 110 | −0,055 | −0,013 |
| vùng cách cạnh ≤ 0 biên độ | 267 | +0,012 | −0,018 | +0,040 | −0,012 | 1 | −1,100 | +0,017 |
| vùng cách cạnh ≤ 0.5 biên độ | 269 | −0,007 | −0,041 | +0,024 | −0,001 | 5 | −0,491 | +0,002 |
| vùng cách cạnh ≤ 1 biên độ | 278 | −0,009 | −0,088 | +0,064 | −0,009 | 12 | −0,334 | +0,006 |
| vùng cách cạnh ≤ 1.5 biên độ | 287 | −0,001 | −0,066 | +0,058 | −0,009 | 21 | −0,083 | +0,005 |
| vùng cách cạnh ≤ 2 biên độ | 303 | −0,010 | −0,042 | +0,021 | −0,045 | 38 | −0,070 | −0,002 |
| vùng cách cạnh ≤ 3 biên độ | 324 | −0,054 | −0,084 | −0,026 | −0,046 | 61 | −0,216 | −0,016 |
| vùng cách cạnh ≤ 4 biên độ | 345 | −0,049 | −0,074 | −0,024 | −0,061 | 83 | −0,163 | −0,012 |
| vùng cách cạnh ≤ 6 biên độ | 362 | −0,012 | −0,039 | +0,015 | −0,040 | 103 | −0,011 | −0,012 |
| vùng sinh ≤ 5 nến sau phá | 297 | −0,010 | −0,048 | +0,026 | −0,019 | 32 | −0,078 | −0,001 |
| vùng sinh ≤ 10 nến sau phá | 328 | −0,026 | −0,081 | +0,028 | −0,045 | 64 | −0,095 | −0,009 |
| có nến hồi chạm vùng trước nến vào | 310 | −0,026 | −0,069 | +0,016 | −0,038 | 46 | −0,123 | −0,009 |
| bỏ hẳn nhánh vùng stacked | 266 | +0,017 | −0,018 | +0,048 | −0,010 | 0 | — | +0,017 |

Opus chọn bỏ hẳn nhánh vùng stacked: cả nhánh âm (116 lệnh −0,06R); mọi mức giới hạn khoảng cách / tuổi vùng / nến hồi chạm vùng đều nằm giữa, không mức nào hơn bỏ hẳn; luật đơn giản nhất, đúng ý người học "mốc là cạnh vừa phá".

Mã thật (`cp_live()`): chỉ luật 1 = 266 lệnh, +0,0165R, nửa −0,018 / +0,048, C2' −0,0096 (khớp dòng "bỏ hẳn" ở trên đến chữ số cuối). **Luật 1 + 2 (corven-5): 266 lệnh (Fail Break 37, Break 229), R TB +0,016, WR 36 % (95 TP / 169 SL / 2 TIME), hai nửa −0,018 / +0,048, vào ngẫu nhiên sau CF −0,013** ⇒ hơn vào ngẫu nhiên nhưng nhỏ, chưa đủ chắc (hậu kiểm nhiều tổ hợp). Luật 2 gần như không đổi số (1 ca trong TRAIN: nến 36957, 01/09 07:29 UTC, SL 4477,8 thay vì 4479,9).

Ca thật: 09/11 07:43 VN (buy 4107,9 mốc stacked) và 06/11 23:08 VN (buy 4072,9 mốc stacked 4070,8–4071,0) không còn; 09/11 11:26 VN (buy 4132,3 · SL 4129,1 · TP 4138,7) vẫn còn — Python và C# khớp.


## corven-6: SL Break sát cạnh ∓ 3 tick + trần SL theo giá (người học yêu cầu; Opus đo; Sonnet implement)

1. **SL Break mốc cạnh = cạnh vừa phá ∓ 3 tick cố định** (buy: cạnh − 3 tick; sell: cạnh + 3 tick). Bỏ râu nhịp hồi và đệm 0,2 biên độ khỏi SL Break; sàn 1 biên độ giữ; Fail Break giữ SL cũ. Cờ Python `sl_b_canh_3tick`, C# `CorvenParams.SlBCanh3Tick`.
2. **Trần SL theo GIÁ** thay trần 4 biên độ: rủi ro (entry↔SL) > SlMaxGia giá ⇒ bỏ (cả Fail Break và Break). Mặc định 5,0, người dùng chỉnh trong Settings "SL tối đa (giá)" (≥ 0,5, bước 0,1). Python `sl_cap_gia`; cổng giữ tên `tran_sl`, nhãn hiển thị "SL > X giá".
3. **Settings** rút còn: Hiện range · Hiện bảng thống kê · Bật Fail Break · Bật Break · SL tối đa (giá) (+ Telegram, lệch giờ). Xoá: công tắc tổng, chặn giờ (luôn BẬT), hiện dấu hiệu (luôn hiện), đặt lại / hiện lại thống kê. Tắt một kiểu ⇒ không vào, không chiếm chỗ lệnh mở (Python `bat_fail_break`, `bat_break`).

Người học yêu cầu SL sát cạnh + trần 5 giá. Trên TRAIN cả hai làm kết quả xấu đi (+0,02 → −0,07R/lệnh, cả hai nửa đều xấu hơn ở SL sát cạnh); Opus đã báo người học, triển khai theo yêu cầu vì đây là luật quản lý rủi ro của người giao dịch.

Đo TRAIN 35 phiên (`research/variants_sl_canh.py`, Opus; hậu xử lý ứng viên corven-5):

| Biến thể | n | R TB | WR | nửa 1 | nửa 2 | C2' | ΣR | rủi ro trung vị (tick) | rủi ro max (tick) |
|---|---|---|---|---|---|---|---|---|---|
| corven-5 | 266 | +0,016 | 36 % | −0,018 | +0,048 | −0,013 | +4,372 | 3.6 | 18.8 |
| trần SL 5 giá | 217 | −0,013 | 35 % | +0,015 | −0,046 | −0,068 | −2,783 | 3.1 | 5.0 |
| SL = cạnh ± 3 tick | 271 | −0,040 | 34 % | −0,029 | −0,050 | −0,032 | −10,822 | 3.4 | 18.0 |
| SL = cạnh ± 3 tick + trần 5 giá | 224 | −0,076 | 33 % | +0,003 | −0,165 | −0,085 | −16,960 | 2.9 | 5.0 |
| … + bỏ sàn 1 biên độ | 224 | −0,077 | 33 % | +0,001 | −0,166 | −0,085 | −17,253 | 2.8 | 5.0 |
| … + bỏ trần 4 biên độ (chỉ trần 5 giá) | 232 | −0,068 | 34 % | +0,025 | −0,177 | −0,094 | −15,790 | 3.0 | 5.0 |
| SL cạnh ± 3 tick + trần 3 giá | 126 | −0,144 | 32 % | −0,130 | −0,162 | −0,078 | −18,146 | 2.2 | 3.0 |
| SL cạnh ± 3 tick + trần 4 giá | 184 | −0,068 | 34 % | −0,029 | −0,116 | −0,074 | −12,429 | 2.6 | 4.0 |
| SL cạnh ± 3 tick + trần 6 giá | 240 | −0,077 | 33 % | −0,055 | −0,100 | −0,064 | −18,470 | 3.0 | 6.0 |
| SL cạnh ± 3 tick + trần 8 giá | 260 | −0,033 | 35 % | −0,005 | −0,059 | −0,020 | −8,645 | 3.3 | 7.9 |

Mã thật (`cp_live()` = SL cạnh ∓ 3 tick + chỉ trần 5 giá): **232 lệnh (Fail Break 41, Break 191), R TB −0,068, WR 34 % (77 TP / 153 SL / 2 TIME), hai nửa +0,025 / −0,177, vào ngẫu nhiên sau CF −0,094** — khớp dòng "… + bỏ trần 4 biên độ (chỉ trần 5 giá)" đến chữ số cuối. Công tắc: tắt Break ⇒ 43 lệnh Fail Break (−0,399R); tắt Fail Break ⇒ 192 lệnh Break (−0,011R).

Ca thật (Python và C# khớp): 06/11 10:33 VN Break sell 4055,3 · SL 4058,8 · TP 4048,3 ⇒ TP; 06/11 12:07 VN Break buy 4058,6 · SL 4055,5; 09/11 11:26 VN Break buy 4132,3 · SL 4129,1 · TP 4138,7 vẫn còn.


### Settings "SL kiểu cũ" (tuỳ chọn, mặc định TẮT) và vì sao SL sát cạnh làm kết quả xấu

"SL kiểu cũ" BẬT = SL Break mốc cạnh + trần SL như corven-5 (Python `cp_live(sl_kieu_cu=True)` = `sl_b_canh_3tick` tắt, `sl_cap_gia` None; C# `CorvenCfg.KieuCu_`). LogicVersion vẫn `corven-6`; khoá cache thêm `-old<0|1>`; nhãn bảng + Telegram theo chế độ đang chạy (bật: "+0,02R/lệnh, hơn vào ngẫu nhiên (−0,01R) chưa đủ chắc"). Chế độ bật bỏ qua "SL tối đa (giá)".
TRAIN chế độ bật = đúng corven-5: 266 lệnh (Fail Break 37, Break 229), +0,016R, nửa −0,018 / +0,048, C2' −0,013 (95 TP / 169 SL / 2 TIME) — không lệch do luật 2. Chế độ tắt = corven-6, 232 lệnh. Parity C# ↔ Python đạt 100 % cho cả hai chế độ (`parity_corven.py` và `parity_corven.py --sl-kieu-cu`).

Vì sao SL sát cạnh làm kết quả xấu (Opus đo trên cùng 229 lệnh Break mốc cạnh của bản SL cũ): R TB +0,091 → +0,048, WR 38 % → 37 %; 5 lệnh TP → SL, 2 lệnh SL → TP. Toàn bộ chênh lệch nằm ở 43/229 lệnh mà râu nhịp hồi đã chọc qua mức SL mới trước khi vào (+0,27R → +0,05R); 186 lệnh còn lại gần như y hệt (+0,050 / +0,049).

## Đề xuất (chưa triển khai): Break không vào khi entry nằm trong một range khác còn sống

Người học gửi 2 ca 29/10 00:42 và 06:53 VN (cả hai SL, đều bị máy đánh dấu đúng là "entry trong range khác"). `variants_range_chong.py`
(xấp xỉ: range còn sống = đã sinh ≤ nến xác nhận < nến chết, biên = top/bottom cuối).

| Dữ liệu | SL | lệnh Break bị đánh dấu | WR | R TB | ΣR |
|---|---|---|---|---|---|
| TRAIN 35 phiên | mới | 18 | 61 % | +0,77 | +13,8 |
| TRAIN 35 phiên | cũ | 17 | 77 % | +1,24 | +21,1 |
| từ 22/10 | mới | 8 | 25 % | −0,50 | −4,0 |
| từ 22/10 | cũ | 9 | 22 % | −0,56 | −5,0 |

Thêm luật trên TRAIN: SL mới −0,07 → −0,14R/lệnh; SL cũ +0,02 → −0,07. Hai giai đoạn ngược chiều, mẫu nhỏ; gộp 26 lệnh vẫn dương
(+0,38R mới / +0,62R cũ). Opus: không triển khai, báo người học.


## corven-7: range bị phá thật rồi giá chạy XA ⇒ range kết thúc (DeadRunMult = 2)

Feedback người học (ca 29/10, range 4064,7–4068,5): range bị phá thật, giá chạy lên 4078,0 (2,3 × chiều cao range) rồi 09:10 VN ReEntry ⇒ range sống lại, còn FailBreak / BreakConfirmed trên chính range đó và hộp "Hiện range" bị kéo dài. Luật: `RangeParams.DeadRunMult` — range đang Broken mà cực trị High/Low kể từ nến phá vượt cạnh vừa phá ≥ mult × (top − bottom) ⇒ Dead ngay, đánh dấu Exhausted (không ReEntry, Merge không hồi sinh). Mặc định TẮT ở Range Box gốc; Benzo dùng 2,0 (`CorvenParams.DeadRunMult`; `V1()` tắt; Python `cp_live()` cả hai chế độ SL `dead_run_mult = 2.0`).

Quét TRAIN 35 phiên (`research/variants_dead_run.py`, `report/_variants_dead_run.csv`):

| Chế độ SL | DeadRunMult | n | Fail Break | Break | R TB | WR | nửa 1 | nửa 2 | C2' | ΣR |
|---|---|---|---|---|---|---|---|---|---|---|
| corven-6 (SL sát cạnh, trần 5 giá) | tắt | 232 | 41 | 191 | −0,068 | 34.1 % | +0,025 | −0,177 | −0,094 | −15,790 |
| corven-6 (SL sát cạnh, trần 5 giá) | 0.5 | 169 | 30 | 139 | −0,042 | 34.9 % | +0,082 | −0,176 | −0,057 | −7,061 |
| corven-6 (SL sát cạnh, trần 5 giá) | 1.0 | 199 | 43 | 156 | −0,066 | 34.2 % | −0,011 | −0,127 | −0,082 | −13,221 |
| corven-6 (SL sát cạnh, trần 5 giá) | 1.5 | 217 | 39 | 178 | −0,081 | 33.6 % | +0,034 | −0,214 | −0,133 | −17,635 |
| corven-6 (SL sát cạnh, trần 5 giá) | 2.0 | 229 | 43 | 186 | −0,068 | 34.1 % | +0,013 | −0,158 | −0,120 | −15,550 |
| corven-6 (SL sát cạnh, trần 5 giá) | 3.0 | 228 | 42 | 186 | −0,077 | 33.8 % | +0,028 | −0,198 | −0,084 | −17,544 |
| SL kiểu cũ (= corven-5) | tắt | 266 | 37 | 229 | +0,016 | 36.1 % | −0,018 | +0,048 | −0,013 | +4,372 |
| SL kiểu cũ (= corven-5) | 0.5 | 202 | 27 | 175 | +0,004 | 35.6 % | +0,006 | +0,002 | −0,024 | +0,799 |
| SL kiểu cũ (= corven-5) | 1.0 | 237 | 39 | 198 | +0,036 | 36.7 % | −0,015 | +0,079 | −0,010 | +8,502 |
| SL kiểu cũ (= corven-5) | 1.5 | 253 | 35 | 218 | +0,014 | 36.0 % | +0,020 | +0,008 | −0,035 | +3,448 |
| SL kiểu cũ (= corven-5) | 2.0 | 267 | 41 | 226 | +0,047 | 37.1 % | +0,024 | +0,066 | −0,029 | +12,424 |
| SL kiểu cũ (= corven-5) | 3.0 | 266 | 38 | 228 | +0,028 | 36.5 % | +0,015 | +0,040 | −0,010 | +7,427 |

Opus chọn 2: không mức nào cải thiện rõ ngoài nhiễu (±0,03R); mức 2 không làm xấu ở cả hai chế độ SL (mới −0,068 = tắt; cũ +0,047 vs +0,016), đủ để chặn ca 29/10 (giá vượt cạnh 2,3 × chiều cao), ít tác dụng phụ nhất (số lệnh gần như giữ nguyên); không chọn 0,5 dù tốt nhất ở SL mới vì nó cắt 27 % số lệnh và ngược chiều ở SL cũ.

Mã thật (`cp_live()`): **SL mới 229 lệnh (Fail Break 43, Break 186), −0,068R, WR 33 % (76 TP / 151 SL / 2 TIME), nửa +0,013 / −0,158, C2' −0,120; SL kiểu cũ 267 lệnh (41 / 226), +0,047R, WR 37 % (98 TP / 167 SL / 2 TIME), nửa +0,024 / +0,066, C2' −0,029** — khớp bảng quét. Nhãn: SL mới "−0,07R/lệnh, chưa có lợi thế (vào ngẫu nhiên −0,12R)"; SL cũ "+0,05R/lệnh, hơn vào ngẫu nhiên (−0,03R) chưa đủ chắc".
Ca 29/10: range chuyển Dead tại BreakConfirmed 08:53 VN, không ReEntry 09:10, không sự kiện nào sau đó; LiveRanges không còn range đó (hộp "Hiện range" không kéo dài); lệnh Break sell 09:10 VN (4067,8, TP) vẫn còn.
