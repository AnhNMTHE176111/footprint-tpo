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
