# Plan — "Trạm Đêm Vàng": công cụ checklist chạy theo Hệ thống Đêm Vàng

Bản 2 · 2026-10-20 · tác giả: Claude (Fable 5.1) · người dùng: người học (trader vàng GC/MGC phiên Mỹ)
Bản 1 đã qua review 1 (`CHECKLIST-DEM-VANG-review-1.md`, 39 mục); mục 11 cuối file ghi từng mục đã sửa thế nào.

> Mục tiêu một câu: một trang web tĩnh mở lúc 18:00, dẫn người dùng đi đúng thứ tự của hệ thống
> (kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ), **khóa tầng dưới khi tầng trên chưa xong**,
> và bật chữ **ENTRY** to rõ đúng lúc đủ điều kiện — để sau 20 phiên, hệ thống thành phản xạ.

Quy ước trong plan: **HT** = `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (trích theo số mục); **ST** = `so-tay-vang-mgc.html`; **RULES** = `daily-trading/RULES.md`. Chính tả theo HT: *hòa, khóa, tắt máy*.

---

## 0. Nguồn, thứ tự ưu tiên và các quyết định về chỗ nguồn mâu thuẫn

| Nguồn | Vai trò |
|---|---|
| HT (16/10/2026) | **Nguồn luật chính.** Mọi câu chữ checklist lấy từ đây. |
| ST (8/2026) | Cơ chế phụ: nhịp buổi tối, 4 chart, lịch tin + cửa sổ cấm, giờ mùa đông Mỹ, máy tính cỡ lệnh MGC, hủy kịch bản, settlement, Globex bảo trì 04:00–05:00. |
| RULES (29/9, bổ sung 15/10) | Không nhồi lệnh (1 lệnh mở); chưa be thì không sờ SL; đóng tay phải có lý do có tên. |
| REVIEW 15/10 + nhật ký | "Vì sao có luật này" trong phần trợ giúp của từng ô. |

**HT thắng ST** khi mâu thuẫn: R:R sàn 1:2 (mục tiêu 3R cho A, B; 2R cho C, D) · ngắt mạch = 2 lệnh phá luật hoặc 3 SL liên tiếp · 4 bài kiểm tra cơ chế thay X1–X4 · checklist 8 câu · nền tảng Optimus Flow thời gian thực (bỏ "chế độ lệnh chờ" của ST).

**Chỗ HT tự mâu thuẫn hoặc không nói — quyết định của plan (mã QĐ-n, hiện trong trợ giúp "?" kèm chữ "chưa đo")**

| Mã | Vấn đề | Quyết định |
|---|---|---|
| QĐ-1 | B (hấp thụ) tại VWAP tuần nằm **giữa** range khi chế độ Cân bằng: HT 5·B cho "hoặc cạnh VA Âu khi đang cân bằng", HT 3 nói "giữa range không có lệnh nào". | Cân bằng ⇒ B chỉ tại cạnh VA Âu / cạnh range, hoặc VWAP tuần / VWAP ngày **trùng cạnh (≤ 1 giá)**. VWAP giữa range ⇒ KHÔNG VÀO `NO_MID_RANGE`. |
| QĐ-2 | LVN là "vùng kẻ" (ca 13/10) hay "vùng cấm" (thẻ phiên HT 8)? | LVN là **vùng cấm fade** (B chặn; A, D theo chiều được). Ca 13/10 là hợp lưu POC hôm qua + LVN: vùng để bám là POC. |
| QĐ-3 | Câu 2 checklist đòi "hạng 1–2 hoặc cạnh VA Âu khi cân bằng", nhưng ca ĐÚNG 6/10 vào tại cụm POC và 13/10 tại POC hôm qua. | Câu 2 = "giá ở **vùng đã ghi trong thẻ phiên**, ≤ 1 giá". **Riêng B**: vùng phải là hạng 1 (VWAP tuần), hạng 2 (VWAP ngày, HVN tuần, **POC hôm qua / cụm POC** — hai loại này chưa đo, chỉ có bằng chứng nhật ký 6/10 và 13/10, cỡ ½) hoặc cạnh VA Âu khi cân bằng. |
| QĐ-4 | "Không cản tàu" ở chế độ Vừa phá: B ngược chiều phá có bao giờ được không? HT xung đột: "Không cản tàu **khi tàu vừa qua cạnh**". | Vừa phá ⇒ B cùng chiều phá: được. B ngược chiều phá: **chỉ** khi vùng chọn **không phải cạnh vừa phá** (cách ≥ 3 giá) và là hạng 1–2 theo QĐ-3; tại cạnh vừa phá ⇒ KHÔNG VÀO `NO_FIGHT_BREAK`. |
| QĐ-5 | HT 4.2 luật cứng "chỉ gọi hấp thụ khi cả thân lẫn \|delta\| giảm dần qua 3 nến", nhưng ca ĐÚNG 5/10 ghi "delta lẫn lộn". | Theo luật cứng: B cần "giảm dần"; "lẫn lộn" ⇒ CHỜ; "tăng dần" ⇒ KHÔNG VÀO. Ca 5/10 ghi chú là ngoại lệ chưa đo. |
| QĐ-6 | Cửa sổ cấm quanh 20:30 (NYSE) và 21:00: HT 7 cấm "đánh tin 19:30 / 20:30 / 21:00" nhưng không cho độ rộng. | Mặc định: 19:30 ±15′ (hạng 1, theo ST), 20:30 ±5′, 21:00 ±5′ (hạng 2, theo ST). Độ rộng ±5′ cho 20:30 là **đề xuất của plan, chưa đo**. Mùa đông: +1h. |
| QĐ-7 | Mốc giờ của luật (19:20, 20:30, 18:00–19:20, 20:20–21:30) có dịch theo giờ mùa đông Mỹ không? HT không nói. | **Có.** Mọi mốc khai theo giờ ET trong `rules.js`, `time.js` đổi sang giờ VN. London đổi giờ 25/10, Mỹ 01/11/2026, Mỹ trở lại 14/03/2027. Ngày 01/11 hiện thẻ một lần: "đổi neo session TPO / SessionZones 19:20 → 20:20, IB = 20:20–21:20". Công tắc tắt trong cài đặt. |
| QĐ-8 | "Cỡ nhỏ", "cỡ một nửa" trong HT. | ½ cỡ chuẩn, **áp một lần, không nhân chồng** khi nhiều điều kiện cùng lúc. |
| QĐ-9 | Ngược bias: HT 2.2 chỉ cho "hấp thụ buy tại đỉnh có tail thật hoặc single print cũ phía trên, cỡ nhỏ, 2R" (và gương). | Ngược bias ⇒ A, D, C: KHÔNG VÀO `NO_COUNTER_BIAS_SCENARIO`. B: chỉ khi vùng chọn mang cờ **tail thật** hoặc **single print** đúng phía (lấy từ Q2 / loại vùng); TP ép 2R, cỡ ½, lý do bắt buộc (HT 2.2 luật cứng). Thanh ENTRY in "ngược bias · 2R · ½". |
| QĐ-10 | Chuỗi SL liên tiếp: lệnh hòa có reset không? | Chỉ SL cộng chuỗi; TP và hòa đều reset về 0. |
| QĐ-11 | Hình dạng "B" trong mẫu thẻ phiên HT 8 nhưng Q1 không định nghĩa. | Giữ, trợ giúp ghi "B = hai phân phối (double distribution) — HT không định nghĩa; chỉ dùng để ghi hình". |

---

## 1. Người dùng, bối cảnh dùng, mục tiêu

- Một người dùng, đi làm ban ngày, trade 18:00 → 00:30 giờ VN, màn chính là Optimus Flow; công cụ mở ở màn phụ hoặc nửa màn, **chuột là chính**, bàn phím khi quen.
- Ban ngày liếc điện thoại (xem thẻ phiên, sổ). Phải dùng được trên điện thoại nhưng tối ưu cho máy tính.
- Dùng **hằng đêm, 20 phiên liên tiếp** → ít chữ, không bắt đọc lại, nhớ trạng thái, **mỗi sự thật chỉ hỏi một lần**.
- Mục tiêu đo được (HT 10): sau 20 phiên có **nhật ký 7 cột đầy đủ** để đếm "lệnh qua đủ 8 câu thắng bao nhiêu, thiếu câu nào thua bao nhiêu".

**Không làm (v1):** không đọc dữ liệu từ Optimus Flow, không tự nhận diện chart, không đồng bộ đám mây, không nhiều người dùng, không tiếng Anh.

---

## 2. Hình thức: trang web tĩnh, cài được như ứng dụng, mở được bằng file://

- **Trang web tĩnh** HTML/CSS/JS thuần, **không framework, không bước build, không `type="module"`** (để mở trực tiếp `index.html` bằng `file://` vẫn chạy — xem mục 5). Deploy GitHub Pages ở repo công khai mới `AnhNMTHE176111/tram-dem-vang` → `https://anhnmthe176111.github.io/tram-dem-vang/`.
- **PWA** (chỉ hoạt động khi mở qua Pages): manifest + service worker để "Cài đặt" thành cửa sổ riêng trên Windows và chạy không mạng. Mở bằng `file://` thì không có service worker nhưng mọi tính năng khác vẫn chạy (localStorage theo origin `file://`).
- **Dữ liệu ở máy**: `localStorage`. Có **xuất / nhập JSON** và **xuất Markdown** (dán vào nhật ký). Nhắc xuất file mỗi cuối tuần (một dòng).
- Mã nguồn trong repo `footprint-tpo` tại `tram-dem-vang/`; `deploy.sh` sao chép sang clone của repo Pages rồi push (giống `he-thong-dem-vang`).

---

## 3. Kiến trúc thông tin: 6 tầng, tầng dưới khóa khi tầng trên chưa xong

```
 ┌ Thanh trạng thái (luôn thấy) ────────────────────────────────────────────────────────┐
 │ 21:14 VN · Lõi giao thoa · cửa sổ cấm kế: 00:00 (2h46′) · BIAS SELL · phá luật 0/2 · SL liên tiếp 1/3 · lệnh mở 0/1 │
 └──────────────────────────────────────────────────────────────────────────────────────┘
 [0 Trước] → [1 Vùng] → [2 Chế độ] → [3 Kèo: Canh | Bấm] → [4 Lệnh] → [5 Sổ]
 ┌ Nội dung tầng ────────────────────────────────┐ ┌ Thẻ phiên (cột phải, cố định) ─┐
 │ checklist của tầng đang mở                    │ │ bias · vùng · nợ · cấm · kế hoạch │
 └───────────────────────────────────────────────┘ └────────────────────────────────┘
 ┌ Thanh phán quyết (dính đáy, tầng 3) ─────────────────────────────────────────────────┐
 │ ●●●●○○○○  CHỜ — thiếu: nến xác nhận · SL     |  ENTRY SELL 4193,0 · SL 4195,4 (2,4) · TP 4185,0 · 1:3,3 │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

Khóa tầng: **1** luôn mở · **2** mở luôn (xem chế độ không cần thẻ) · **3** mở khi thẻ phiên đã chốt **và** bias ≠ CHỜ **và** không có lệnh mở · **4** mở khi có lệnh (đang chờ khớp hoặc đã khớp) · **5** luôn mở. Khi có lệnh mở, tầng 3 khóa hẳn và giao diện tự nhảy sang tầng 4 (RULES A.3 "nhồi lệnh = 0").

### Tầng 0 · Trước khi mở chart (18:00)
| # | Ô | Kiểu | Hệ quả |
|---|---|---|---|
| 0.1 | Tỉnh táo, không bực dọc, không mệt rã rời | có / không | Không ⇒ cả đêm **CHỈ XEM**: vẫn đi hết checklist để luyện mắt; ENTRY hiện màu xám "ENTRY (chỉ xem)", nút ghi thành "Ghi kèo luyện mắt" (vào sổ với cờ `paper`). |
| 0.2 | Cửa sổ cấm tối nay | danh sách có sẵn, bật/tắt từng dòng | Mặc định bật: **20:30 ±5′**, **21:00 ±5′**; **19:30 ±15′** bật sẵn vào **thứ Năm** (Jobless Claims) và khi người dùng chưa chạm vào tầng 0; thêm được: FOMC (01:00 / 01:30: nhắc đóng sạch trước 00:45), tin tùy chỉnh (giờ + hạng). Tắt một dòng ⇒ ghi vết "tắt cửa sổ 19:30 lúc hh:mm". Ngày có NFP/CPI ⇒ cờ "cỡ ½ cả đêm". Mùa đông: mọi mốc +1h. (QĐ-6, QĐ-7) |
| 0.3 | Kịch bản nền ban ngày (1 dòng, tùy chọn) | chữ | Hiện lại ở thẻ phiên. |

### Tầng 1 · Kẻ vùng trên chart A và chốt thẻ phiên (18:30–19:20; mùa đông 19:30–20:20)
**1a. Kẻ trên chart** (tick khi đã kẻ xong trên Optimus Flow):
1. Chart A: TPO ngày neo giờ pit COMEX (19:20; mùa đông 20:20) + TPO gộp 3 tuần, bracket 30′.
2. 5 mức hôm qua: High · VAH · POC · VAL · Low.
3. VWAP tuần (hạng 1) và VWAP ngày (hạng 2).
4. HVN / LVN ngày và 3 tuần (LVN: giá chạy nhanh qua, cấm fade; HVN 3 tuần: cấm fade).
5. Nợ: single print chưa lấp, poor high / poor low.
6. Naked POC các phiên trước (chỉ làm mục tiêu).
7. Range Á / Âu hôm nay: VAH Âu, VAL Âu; IB high / IB low khi đã có.

**1b. Sáu câu hỏi** (chọn một; "?" mở đúng Q của HT):

| Q | Câu | Đáp án |
|---|---|---|
| Q1 | Hình dạng profile hôm qua | D · P · b · B · thin · chữ nhật (QĐ-11) |
| Q1′ | Hình dạng 3 tuần | như trên |
| Q2a | **Đỉnh** hôm qua | tail thật (1 TPO, volume thấp) · mồi (volume dày) · poor high (nợ) · bình thường |
| Q2b | **Đáy** hôm qua | tail thật · mồi · poor low · bình thường |
| Q3 | Nợ chưa lấp | phía trên · phía dưới · cả hai · không |
| Q4 | Giá hiện tại đang ở | LVN · HVN · giữa |
| Q5 | Giá đóng hôm qua so với VA hôm qua | trên · trong · dưới |
| Q6 | Âu đã dựng range chưa | rồi · chưa |

**1c. Bias** — thêm ô *Giá hiện tại so với VWAP tuần*: trên · dưới · sát (±2 giá). Ma trận (HT 2.2):

| VWAP tuần | Q5 | Q1 | ⇒ Bias | Được làm gì |
|---|---|---|---|---|
| trên | trên hoặc trong | ≠ b | **BUY** | A buy · B (hấp thụ sell) tại vùng · C fade đáy VA Âu. Sell chỉ theo QĐ-9. Không sell tại HVN 3 tuần. |
| dưới | dưới hoặc trong | ≠ P | **SELL** | gương ngược |
| trên | dưới · hoặc dưới / trên | — | **KHÔNG** | chỉ C hai cạnh VA Âu, 2R, cỡ ½; **A, B, D tắt** |
| trên, Q1 = b · dưới, Q1 = P | — | — | **KHÔNG** | như trên |
| sát | bất kỳ | — | **CHỜ** | tầng 3 khóa; nút "Chốt lại bias" hiện khi người dùng xác nhận "đã có 1 nến M5 đóng rõ một phía: trên / dưới" ⇒ tính lại |

Bias tự động; **ghi đè** được nhưng phải gõ lý do (lưu vào thẻ, cờ "bias ghi đè").

**1d. Vùng đã kẻ (3–5; < 3 vẫn chốt được nhưng cảnh báo vàng "mới có n/3 vùng", ghi vết)** — mỗi vùng: loại · giá (số hoặc khoảng "4181–4183") · ghi chú. Hạng, vai và cờ tự suy:

| Loại | Hạng / vai | Kịch bản hợp lệ tại vùng | Cờ tự gán |
|---|---|---|---|
| VWAP tuần | hạng 1 | B, A, D | |
| VWAP ngày · HVN tuần | hạng 2 (cỡ ½) | B (½), A, D | |
| POC hôm qua · cụm POC | hạng 2 (chưa đo, cỡ ½; QĐ-3) | B (½), A, D | |
| VAH Âu · VAL Âu · cạnh range · IB high · IB low | cạnh | C; B khi cân bằng; A sau khi phá | |
| High hôm qua · Low hôm qua | cạnh (ngoài) | C, A, D | lấy cờ từ Q2a / Q2b: tail thật · poor · mồi |
| single print · poor high/low | nợ, mục tiêu ưa thích | TP; B ngược bias theo QĐ-9 | `tail/sp` |
| naked POC | **chỉ mục tiêu** | TP | |
| HVN 3 tuần · HVN ngày ngay sau phá cực trị · LVN | **cấm fade** (QĐ-2) | A, D theo chiều; **B chặn** | `banned` |

**1e. Thẻ phiên** (cột phải) tự điền đúng mẫu HT 8: NGÀY · VWAP tuần · Đóng hôm qua · Hình hôm qua · BIAS · VÙNG · NỢ · VÙNG CẤM (tự gom các vùng `banned`) · **Kế hoạch 1 / Kế hoạch 2** ("nếu … thì …", chữ tự do) · **Hủy kế hoạch khi …** (ST §7). Nút **"Chốt thẻ phiên"**:
- Điều kiện: Q1, Q5, Q6, VWAP tuần đã trả lời; ≥ 1 vùng.
- Sau chốt vẫn sửa được. **Trước 19:20 (mùa đông 20:20)** sửa Q6 / vùng VA Âu / IB không ghi vết (Âu chưa xong). Sau mốc đó, mỗi lần sửa ghi "sửa lúc hh:mm: …"; nếu đang có kèo ở tầng 3 ⇒ cảnh báo "đang canh kèo — sửa thẻ lúc này là nắn kế hoạch", phải xác nhận.
- Chưa chốt ⇒ tầng 3 khóa: "Không có thẻ phiên thì không có lệnh."

### Tầng 2 · Chế độ thị trường (chart B, M30/M5)
- Chọn **chế độ**: Cân bằng · Vừa phá · Trend thin. Đổi lúc nào cũng được; mỗi lần đổi ghi vào dòng thời gian của đêm.
- *Vừa phá* cần: hướng phá (lên / xuống) · **cạnh vừa phá** (chọn từ danh sách vùng: VA Âu / IB / một vùng đã kẻ) · giờ phá (mặc định "bây giờ") · phá lần mấy (1 / 2) · **acceptance = 2 bước** (bước 3 của HT 3.1 hỏi một lần ở tầng 3, ô A·Kiểm tra):
  1. Có 1 nến M5 đóng ngoài cạnh đó.
  2. Nhịp hồi về cạnh giữ được: không nến M5 nào đóng ngược vào trong.
  Thiếu bước 2 ⇒ hiện "**chạm, chưa phá**" và engine coi là Cân bằng. Lần 1 rồi chui lại ⇒ "không đuổi, chờ lần 2". Giờ phá trong 18:00–19:20 (mùa đông 19:00–20:20) ⇒ "nghi trước, tin sau", **A khóa**.
- **Bảng bật kịch bản** (4 thẻ A–D sáng / mờ kèm lý do mờ; thứ tự ưu tiên luật ở mục 5):

| Điều kiện | A Phá hồi | B Hấp thụ | C Fade cạnh | D Trap |
|---|---|---|---|---|
| Bias CHỜ | tắt | tắt | tắt | tắt |
| Bias KHÔNG | tắt "bias KHÔNG: chỉ fade cạnh" | tắt | **bật** 2R ½ | tắt |
| Trước 20:30 (mùa đông 21:30) | tắt "trước 20:30 chỉ fade cạnh" | tắt | bật, cỡ ½ | tắt |
| Cân bằng | tắt "chưa phá" | bật chỉ tại cạnh (QĐ-1) | **bật** | tắt "không có move rõ" |
| Vừa phá | **bật** cùng chiều phá | bật cùng chiều; ngược chiều theo QĐ-4 | tắt "đã có nến M5 đóng ngoài" | bật cùng chiều phá |
| Trend thin | bật ở nhịp hồi, cùng chiều | tắt "không cản tàu" | tắt | **bật** cùng chiều |

- Nút **"Vừa có nến dài nhất phiên"** ⇒ khóa cả 4 kịch bản tới **phút tròn kế tiếp + 3′** (3 nến M1 đóng xong), hiện "mở lại 21:21"; sau đó nhắc "chờ hồi; không hồi thì bỏ".
- Dải giờ (HT 3.2) hiện theo giờ thật: 18:00–19:20 "phá giả", 19:20–20:30 "mở ảo", 20:20–21:30 "cú phá đáng tin" (mùa đông +1h).

### Tầng 3 · Kèo trên M1 — hai bước **Canh** và **Bấm**, phán quyết sống
Nguyên tắc: **mỗi sự thật một điều khiển**, 3 trạng thái (tốt / xấu / không rõ; chưa chạm = chưa trả lời). Thứ "suy được" thì không hỏi lại (acceptance, giờ, chế độ, nến dài nhất, bias, hạng vùng, lần tại vùng đều tự điền).

**3a. Canh — điền trước khi nến xác nhận đóng (≤ 7 thao tác)**

| # | Điều khiển | Lựa chọn | Hệ quả |
|---|---|---|---|
| C1 | Kịch bản | A · B · C · D (chỉ thẻ đang bật) | |
| C2 | Hướng | buy · sell | ngược bias ⇒ QĐ-9; hộp "Lý do ngược bias" bắt buộc |
| C3 | Vùng | chọn từ thẻ phiên | hiện hạng, cờ, **lần thứ n** (n = 3 ⇒ KHÔNG VÀO `NO_ZONE_3RD`), cấm fade với B ⇒ `NO_BANNED_ZONE`, giữa range khi cân bằng ⇒ `NO_MID_RANGE` |
| C4 | 4.3 Bong bóng to gần nhất (10 nến, ở cực trị) | cùng phe · ngược phe còn giữ (vòng trắng) · ngược phe đã vỡ (mờ) · không có / ở giữa move — kèm ô số tùy chọn "±___" | "ngược còn giữ" ⇒ `NO_BUBBLE_AGAINST`. **B**: cần "cùng phe"; "không có" ⇒ CHỜ "hấp thụ mà không có bong bóng thì chưa có bằng chứng"; "đã vỡ" ⇒ KHÔNG VÀO |
| C5 | 4.4 Giá cách vùng | ≤ 1 giá / râu chạm · 1–3 giá, chưa về · ≥ 3 giá, ở lưng | 1–3 ⇒ CHỜ "chờ hồi về cạnh"; ≥ 3 ⇒ `NO_BACK` "không hồi thì bỏ" |
| C6 | Biên độ nến M1 cao nhất trong 5 nến (giá) | số | dùng cho sàn nhiễu |
| C7 | Ô riêng kịch bản | B: "DMA" ngang · còn dốc ⇒ `NO_DMA_SLOPE`; B: "giá đang phá VWAP / cạnh theo chiều move?" không · có ⇒ `NO_B_IS_BREAK` "đó là phá hồi — đổi sang A". D: "move ≥ 5 giá cùng chiều bias?" có · không ⇒ `NO_D_NO_MOVE`; D: "nhịp hồi đã quá 70 % move?" chưa · rồi ⇒ `NO_D_DEEP` | A, C: không có ô riêng ở bước Canh |

**3b. Bấm — sau khi nến xác nhận đóng (≤ 6 thao tác)**

| # | Điều khiển | Lựa chọn | Áp cho |
|---|---|---|---|
| B1 | 4.1 Nhịp hồi | **U** (≥ 3 nến ngắn, thoải, không nến hồi nào dài bằng nến dài nhất move trước) · **V** · không rõ | A, B, D. V ⇒ `NO_V_PULLBACK`; không rõ ⇒ `NO_UNCLEAR`. C: ẩn |
| B2 | 4.2 Thân + \|delta\| 3 nến cuối | giảm dần · lẫn lộn · tăng dần · không rõ | **B**: giảm ⇒ qua; lẫn ⇒ CHỜ; tăng ⇒ `NO_MOMENTUM` (QĐ-5). A, D: ẩn (thay bằng B3) |
| B3 | Nến xác nhận đạt chuẩn của kịch bản | đạt · chưa · không rõ — nhãn đổi theo kịch bản: **A** "đóng theo chiều phá, thân ≥ nửa biên độ, delta cùng dấu; tại cạnh có delta cùng chiều phá hoặc hấp thụ phe ngược" · **B** "ngược chiều move, delta đảo dấu ≥ ½ nến lớn nhất của move" · **C** "râu xuyên cạnh rồi đóng lại trong range; thân không ngắn, râu ngược không dài; delta ủng hộ" · **D** "ở đỉnh hồi có bong bóng hấp thụ phe hồi hoặc nến hồi delta thuận đóng dưới nửa thân; nến xác nhận đóng theo chiều cũ, thân dài, delta cùng dấu" | tất cả. "chưa" ⇒ CHỜ "chờ nến xác nhận" |
| B4 | Giá vào · SL · TP | 3 số (nhận cả "4193.5" và "4193,5") | TP gợi ý sẵn = vào ± 3R (A, B) / 2R (C, D); C: gợi ý thêm "cạnh đối diện / POC gần hơn" từ thẻ |
| B5 | Vị trí SL đúng kiểu kịch bản | tick — nhãn đổi theo kịch bản: **A** "sau râu nến xác nhận hoặc mép xa vùng (cái xa hơn) + 0,3" · **B** "sau cực trị của cụm hấp thụ + 0,3, không ở giữa cụm" · **C** "sau râu phá hụt + 0,3" · **D** "sau đỉnh nhịp hồi + 0,3" | |

Máy tính tự kiểm từ B4 + C6: khoảng SL ≥ nến cao nhất (`NO_SL_FLOOR`, in số: "SL 2,1 < nến 3,3 — đẩy SL ra hoặc bỏ kèo") · ≤ 4 giá (`NO_SL_CAP`) · R:R ≥ 1:2 (`NO_RR`) · hướng SL/TP đúng phía (`NO_SL_SIDE`). Gập: **cỡ lệnh MGC** (vốn, % rủi ro nhớ trong cài đặt; tick 0,1 = 1 $; số hợp đồng làm tròn xuống; ½ theo QĐ-8 khi: bias KHÔNG · C · ngược bias · ngày NFP/CPI · vùng hạng 2).

**3c. Phán quyết** (thanh dính đáy, tính lại sau mỗi click, theo thứ tự luật mục 5):
1. **TẮT MÁY** (đen) — ngắt mạch đã kích. Tầng 3 vẫn xem được để luyện mắt nhưng phán quyết tối đa là TẮT MÁY.
2. **KHÔNG VÀO** (đỏ) + lý do có mã, hiện tối đa 2 lý do đầu.
3. **CHỜ** (vàng) — liệt kê tối đa 3 ô còn thiếu theo thứ tự nên làm tiếp.
4. **ENTRY** (xanh, ≥ 32 px): `ENTRY SELL 4193,0 · SL 4195,4 (2,4 giá) · TP 4185,0 · 1:3,3 · cỡ ½ · ngược bias` → nút **"Vào lệnh"** mở hộp: **market** (nhập giá khớp) / **limit** (giá chờ) ⇒ tầng 4.
- Nút phụ **"Tôi vẫn vào (phá luật)"** hiện ở **mọi** phán quyết trừ ENTRY (kể cả TẮT MÁY) — mở cùng hộp vào lệnh, dòng sổ mang cờ ⚠ phá luật + mã lý do đang vi phạm, tăng ngắt mạch. Sổ trung thực quan trọng hơn ngăn bấm.
- **Tám chấm** (HT 9) ngay trên thanh, sáng theo dữ liệu: 1 thẻ phiên + cùng chiều bias (hoặc ngược bias hợp lệ) · 2 vùng trong thẻ ≤ 1 giá (B: hạng theo QĐ-3) · 3 chế độ bật kịch bản · 4 U (C: tự sáng) · 5 bong bóng cùng phe hoặc đã vỡ (B: cùng phe) · 6 B2 giảm dần (B) / B3 đạt (A, D) / B3 đạt (C) · 7 B3 đạt và không trong 3′ sau nến dài nhất · 8 SL 3 điều kiện + R:R + lần ≤ 2. Di chuột ⇒ câu đầy đủ.
- Không tự xóa; sau **10′** không thao tác hiện "đã 10′ — nến M1 đã khác, kiểm lại". Nút **"Kèo mới"** xóa tầng 3 (giữ 0–2). Chuyển kịch bản giữa chừng giữ C2–C6, xóa ô riêng và bước Bấm.

### Tầng 4 · Lệnh (tối đa 1)
- Trạng thái **chờ khớp** (limit): nút "Khớp rồi" (nhập giá khớp thật) · "Hủy — giá bỏ đi" (không tính là lệnh, không vào sổ, không tăng đếm vùng).
- **Đã khớp**: hướng · giá vào thật · SL · TP · R dự kiến; ô "giá hiện tại" ⇒ R hiện tại. **Không có ô sửa SL** (RULES D). Mốc be tự tính: A/B **+1,5R** kèm tick "đã có 1 nến M1 đóng ngoài vùng vào" ⇒ nút "Đã dời về hòa" mở; C/D **+1R**.
- Cửa sổ cấm hạng 1 / FOMC sắp tới mà lệnh còn mở ⇒ đếm ngược "**flat trước hh:mm**" (19:15 / 00:45; mùa đông +1h). Đóng vì lý do này là lý do hợp lệ có tên.
- **Đóng lệnh**: TP · SL · hòa · đóng tay (chọn lý do: "hấp thụ ngược đe dọa TP" · "flat trước tin" · "khác" ⇒ cờ phá luật). Nhập giá thoát ⇒ R gợi ý, sửa được.
- Sau khi đóng: ô "SL bị quét rồi giá tới TP?" (tick sau) · ghi chú. Dòng sổ 7 cột hoàn tất; ngắt mạch cập nhật (QĐ-10). Lệnh còn mở qua 05:00 ⇒ vẫn thuộc đêm vào lệnh; đêm mới mở với lệnh đó ở tầng 4 và nhắc Globex bảo trì 04:00–05:00.

### Tầng 5 · Sổ (đêm nay · tuần · xuất)
- **Đêm nay**: bảng 7 cột đúng mẫu HT 8 (`giờ | hướng | tên | chế độ | 4 kiểm tra | SL | R`; cột 4 kiểm tra in dạng "U · bb −129 giữ · Δ giảm · cạnh" từ C4/C5/B1/B2 và số bong bóng nếu có), dòng ⚠ nêu điều phá. Chân bảng: **"Máy cộng: x R"** cạnh ô **"Bạn cộng: __ R"** (cộng tay thật); lệch ⇒ đỏ. Thêm: lệnh phá luật · SL bị quét rồi tới TP. Nút "Kết phiên" chỉ mở khi đã nhập "Bạn cộng"; sau kết vẫn sửa R có ghi vết.
- **Tuần**: 4 con số HT 8 — phá luật/tổng · SL quét rồi tới TP · R theo tên kịch bản và theo loại vùng · lệnh ngược bias và kết quả; cộng chuỗi đêm 0 phá luật.
- **Xuất**: Markdown (mẫu 7 cột + thẻ phiên) · JSON (sao lưu, nhập lại gộp theo đêm, không trùng) · CSV.

### Thanh trạng thái + đồng hồ
- Giờ VN; nhãn pha (ST §1, tự +1h mùa đông; dòng "Mỹ đang giờ mùa đông: mốc +1h" từ 01/11; "London đóng" dịch từ 25/10): Ban ngày · Chuẩn bị 18:00 · COMEX mở 19:20 · Tin 19:30 · NYSE 20:30 · Lõi giao thoa 21:00–22:30 · London đóng 22:30 · Mỏng dần sau 23:00 · Settlement 00:30 · Globex bảo trì 04:00–05:00.
- Đếm ngược tới cửa sổ cấm kế; trong cửa sổ: thanh đỏ "CỬA SỔ CẤM — không vào".
- Chip: phá luật n/2 · SL liên tiếp n/3 · lệnh mở 0/1 · vùng đang chọn n/2.
- **Khóa đêm** = ngày của mốc 18:00 bắt đầu: `nightKey(now)` = ngày hôm nay nếu giờ ≥ 05:00, ngược lại hôm qua. Mở sau 05:00 ⇒ đêm mới ("đêm hôm qua đã lưu vào sổ").

---

## 4. Nguyên tắc UI/UX (bắt buộc với người implement)

1. **Một màn hình, một việc.** Tầng chưa mở hiện mờ với một câu lý do. Tầng 3 bước Bấm vừa một màn 1366×768 không cuộn.
2. **Phán quyết luôn thấy** ở tầng 3; màu cố định: xanh ENTRY · vàng CHỜ · đỏ KHÔNG VÀO · đen TẮT MÁY · xám CHỈ XEM.
3. **Mỗi ô ≤ 9 từ** nhãn chính (đếm theo khoảng trắng, bỏ ký hiệu toán và số); trợ giúp "?" ≤ 2 câu + link nhảy đúng mục trang HT (`…/he-thong-dem-vang/#id`: `sau-cau-hoi ma-tran-bias xep-hang-vung acceptance thoi-gian v-hay-u than-delta bong-bong-phe canh-hay-lung kb-a kb-b kb-c kb-d xung-dot ca-that luat-sl tp-be the-phien nhat-ky-lenh cuoi-tuan`). Mỗi kịch bản kèm ảnh ca thật (sao chép 4 ảnh `kb-*.png` vào app).
4. **Hai mức hướng dẫn**: *Mới* (trợ giúp + lý do từ nhật ký dưới mỗi ô) · *Quen* (chỉ nhãn). Nhớ lựa chọn.
5. **Nút chọn nhóm 3 trạng thái**, đáp án xấu tô đỏ khi chọn; không dùng checkbox cho câu có đáp án xấu.
6. **Không hộp thoại xác nhận** trừ: sửa thẻ phiên khi đang canh kèo (sau 19:20), "Tôi vẫn vào (phá luật)", xóa dữ liệu, tắt cửa sổ cấm.
7. **Bàn phím** (tầng 3, **tắt khi focus trong ô nhập**; `Esc` rời ô nhập): `1–4` kịch bản, `B`/`S` hướng, `U`/`V` câu 4.1, `Enter` nút chính của thanh phán quyết, `N` kèo mới, `?` trợ giúp. Gợi ý phím nhỏ cạnh nút.
8. **Giao diện tối mặc định**, tương phản WCAG AA, có chế độ sáng. Font hệ thống. Số hiển thị dấu phẩy thập phân (4193,5); ô nhập nhận cả dấu chấm.
9. **Điện thoại ≥ 360 px**: tầng dọc, thẻ phiên thành ngăn trượt, thanh phán quyết vẫn dính đáy, không tràn ngang.
10. **Nhanh**: không thư viện ngoài, tải < 100 KB, mọi thao tác < 50 ms, lưu ngay sau mỗi click.
11. **Ngôn ngữ**: tiếng Việt đủ dấu, câu ngắn. Giữ tiếng Anh: buy · sell · limit · market · sell limit · buy limit; thuật ngữ: TPO, VA, VAH, VAL, POC, HVN, LVN, VWAP, delta, DMA, IB, R, SL, TP, be, fade, trap, tail, single print, poor high/low, naked POC, bias, acceptance, move, retest, range, bracket, session, tick, thin, setup, profile, market, COMEX, NYSE, Globex, FOMC, NFP, CPI, ET. Cấm: "bán"/"mua" cho hướng lệnh, "lệnh chờ", "đập giá", "DST" (viết "giờ mùa đông"), "overlap" (viết "giao thoa"). Lint tự động (mục 6).

---

## 5. Kiến trúc kỹ thuật

```
tram-dem-vang/
  index.html                 # khung 1 trang; nạp js/*.js bằng <script> thường, đúng thứ tự
  manifest.webmanifest · sw.js · icons/ · img/kb-*.png
  css/app.css                # token màu (:root, [data-theme]), layout, thành phần
  js/content.js              # TOÀN BỘ chữ: nhãn, trợ giúp, lý do theo mã — dữ liệu thuần
  js/rules.js                # DANH SÁCH LUẬT CÓ THỨ TỰ + hằng số (ma trận bias, hạng vùng, mốc giờ ET, ngưỡng)
  js/time.js                 # giờ VN, giờ mùa đông Mỹ/EU, pha, cửa sổ cấm, nightKey
  js/engine.js               # thuần: (night, now) → {verdict, reasons, missing, dots, order, enabled}
  js/store.js                # localStorage, version + migrate, xuất/nhập
  js/journal.js              # dòng 7 cột, cộng, 4 con số tuần, Markdown/CSV
  js/ui/*.js · js/main.js    # render, sự kiện
  tests/*.test.mjs           # node:test, nạp js/*.js qua loader (xem dưới)
  e2e/*.spec.mjs             # Playwright chromium
  scripts/lint-vi.mjs · deploy.sh · README.md
  docs/IMPL-n.md · REVIEW-n.md · USER-TEST-n.md
```

- **Không ES module** (file:// chặn module). Mỗi file JS dùng mẫu UMD nhỏ: `(function (root, factory) { if (typeof module === 'object') module.exports = factory(); else (root.TDV = root.TDV || {}).engine = factory(); })(this, function () { … })`. Test node nạp qua `require` bình thường (`.js` CommonJS).
- **Service worker** (chỉ trên Pages): `scope` tương đối `./`, tên cache theo `APP_VERSION` trong `rules.js`, `skipWaiting` + `clients.claim`, thẻ "có bản mới — tải lại" khi SW mới kích hoạt. `deploy.sh` tăng `APP_VERSION` tự động (ngày + hash ngắn).
- **Engine = danh sách luật có thứ tự** `[{code, when(state, now) → bool, effect: 'OFF'|'NO'|'WAIT'|'DISABLE', scope}]`, chạy tuần tự, `reasons` giữ thứ tự. Thứ tự: `OFF_*` (ngắt mạch) → lệnh mở → cửa sổ cấm → khóa 3′ → thẻ phiên / bias CHỜ → bias KHÔNG → giờ trước 20:30 → chế độ × kịch bản → hướng vs bias → vùng (lần 3, cấm, giữa range, cạnh vừa phá) → C4, C5 → ô riêng (C7) → B1, B2 → B3 → SL / R:R. Chỉ xem (`paper`) không phải luật, là cờ hạ cấp ENTRY.
- **Mô hình dữ liệu** `localStorage["tdv.v1"]`:
```
{ version: 1,
  settings: {theme, guideLevel, capital, riskPct, dstShift: true, shortcuts: true},
  nights: { "<nightKey>": {
     t0: {alert, windows:[{id, kind, at, on, offAt?}], halfSize, note},
     card: {answers:{q1,q1w,q2top,q2bot,q3,q4,q5,q6,vwapW}, bias:{auto, override, reason, rechecked},
            zones:[{id,type,price,priceTo?,note,flags:[]}], plan1, plan2, cancelWhen, lockedAt, edits:[{at,what}]},
     regime: {mode, breakout:{dir, edgeZoneId, at, nth, step1, step2}, longestBarUntil, log:[{at,mode}]},
     setup: {scenario, side, zoneId, counterBiasReason, c4, c4num, c5, c6, c7:{}, b1, b2, b3,
             calc:{entry, sl, tp}, slPlaced, updatedAt},
     open: {status:'pending'|'filled', side, scenario, zoneId, entryPlanned, entry, sl, tp, rrPlanned,
            beAt, beDone, outsideZoneBar, openedAt} | null,
     trades:[{time, side, scenario, mode, zoneId, zoneType, tests:{b1,c4,c4num,b2,c5}, entry, sl, tp,
              slDist, rrPlanned, exit:{kind, price, reason}, r, flags:['rule_break','counter_bias','paper','half'],
              ruleCodes:[], sweptThenTP, notes}],
     tally:{machine, manual, closedAt} } } }
```

---

## 6. Kiểm thử (người implement phải chạy, báo kết quả thật)

**Đơn vị (node:test, `npm test`)** — tối thiểu:
- Ma trận bias: 12 ca (4 hàng, b/P, ghi đè, CHỜ rồi chốt lại trên/dưới).
- Bật kịch bản: ma trận bias (CHỜ, KHÔNG, BUY) × chế độ × giờ (20:29 / 20:31 hè; 21:29 / 21:31 đông) × acceptance (đủ / thiếu bước 2 / phá 18:30) — ≥ 20 ca, mỗi ca kiểm `enabled` và mã lý do mờ.
- Phán quyết, một mã mỗi ca: `NO_V_PULLBACK` · `NO_BUBBLE_AGAINST` · `NO_BACK` · CHỜ khi C5 = 1–3 giá · `NO_UNCLEAR` · `NO_ZONE_3RD` · `NO_BANNED_ZONE` · `NO_MID_RANGE` · `NO_FIGHT_BREAK` · `NO_COUNTER_BIAS_SCENARIO` (A, C, D) · B ngược bias không cờ tail/sp ⇒ NO; có cờ ⇒ ENTRY 2R ½ · `NO_MOMENTUM` · B lẫn lộn ⇒ CHỜ · B bong bóng "không có" ⇒ CHỜ, "đã vỡ" ⇒ NO · `NO_DMA_SLOPE` · `NO_B_IS_BREAK` · `NO_D_NO_MOVE` · `NO_D_DEEP` · `NO_SL_FLOOR` · `NO_SL_CAP` · `NO_RR` · `NO_SL_SIDE` · lệnh mở ⇒ tầng 3 khóa · cửa sổ cấm 20:30 ±5′ ⇒ NO · khóa 3′ tính tới phút tròn + 3 ⇒ NO rồi hết · CHỜ với `missing` đúng thứ tự · ENTRY đúng số.
- **Ca thật tái hiện** (số cố định): **12/10 21:27** V + bong bóng ngược còn giữ ⇒ NO với 2 mã đúng thứ tự · **6/10 20:24** A sell, mode vừa phá cụm POC, U, B3 đạt, vào 4193,0 · SL 4195,4 · TP 4185,0 · C6 = 2,0 ⇒ ENTRY, SL 2,4, R:R 1:3,3 · **1/10 20:47** sell 4192,7 · SL 4194,8 · C6 = 3,3 ⇒ `NO_SL_FLOOR` · **13/10 20:10** B buy tại POC hôm qua (hạng 2, QĐ-3), mode vừa phá xuống, vùng cách cạnh vừa phá ≥ 3 giá (QĐ-4), 4.2 giảm (−49 → −40), bong bóng cùng phe ⇒ ENTRY ½ · **5/10 19:25** B với 4.2 lẫn lộn ⇒ CHỜ (QĐ-5, ghi chú ngoại lệ).
- Ngắt mạch: 2 phá luật ⇒ OFF; "Tôi vẫn vào" ×2 ⇒ OFF; 3 SL liên tiếp ⇒ OFF; hòa và TP reset chuỗi (QĐ-10); đóng tay lý do "khác" ⇒ phá luật; "flat trước tin" ⇒ không phá luật.
- Tầng 4: mốc be +1,5R / +1R đúng với SL lẻ 0,1; limit hủy ⇒ không vào sổ, không tăng đếm vùng; lệnh mở qua 05:00 thuộc đêm cũ.
- Thời gian: `nightKey` ở 00:30 và 04:59 (đêm cũ), 05:00 và 10:00 (đêm mới); giờ mùa đông tại 24/10, 25/10 (London), 31/10, 01/11/2026, 13/03, 14/03/2027; pha; cửa sổ cấm ±15′ / ±5′; thứ Năm bật 19:30.
- Thẻ phiên: sửa Q6 trước 19:20 không ghi vết, sau 19:20 ghi vết; sửa khi đang canh kèo ⇒ cần xác nhận.
- Sổ: cộng R, lệch máy/tay, 4 con số tuần, Markdown đúng mẫu 7 cột (so chuỗi).
- Store: migrate version, nhập JSON gộp không trùng.

**Đầu cuối (Playwright, `npm run e2e`)**: (1) đường đi đầy đủ tới ENTRY và ghi sổ, đếm số click ở bước Bấm ≤ 6; (2) tầng 3 khóa khi chưa chốt thẻ / bias CHỜ / có lệnh mở; (3) chọn V ⇒ KHÔNG VÀO đỏ; (4) tải lại trang giữ nguyên; (5) mở bằng `file://` chạy không lỗi console; (6) 360 px không tràn ngang; (7) phím tắt 1–4, U/V, Enter, và bị tắt trong ô nhập; (8) "Tôi vẫn vào" ×2 ⇒ TẮT MÁY.

**Lint chữ (`npm run lint:vi`)**: quét `content.js`: từ cấm (mục 4.11), từ tiếng Anh ngoài danh sách cho phép, nhãn > 9 từ (cách đếm ở 4.3), số dùng dấu chấm thập phân trong chuỗi hiển thị. Lint không chạy trên ô nhập.

Tiêu chí "xong" mỗi vòng: `npm test`, `npm run e2e`, `npm run lint:vi` đều xanh (dán kết quả thật vào `docs/IMPL-n.md`); ảnh chụp 3 màn (tầng 1, tầng 3 ENTRY, điện thoại); deploy Pages mở được.

---

## 7. Quy trình thực hiện (theo yêu cầu người dùng)

**Giai đoạn P — plan**: bản này → agent **Fable** review (tối đa 3 vòng) → sửa.

**Giai đoạn I — tối đa 4 vòng**, mỗi vòng:
1. **Sonnet implement + test** theo plan; ghi `docs/IMPL-n.md` (làm gì, kết quả test thật, gì chưa xong).
2. Song song: **Opus review** (đúng luật từng ô so với HT, mã, test, UX) → `docs/REVIEW-n.md`; **Sonnet "trader 1 tháng kinh nghiệm order flow / TPO"** dùng thử bằng Playwright + đọc, ghi `docs/USER-TEST-n.md`: làm được việc không, chỗ phải đoán, chữ khó, số click tới ENTRY, có muốn dùng đêm mai không (điểm /5).
3. **Sonnet sửa** theo hai biên bản (ưu tiên: sai luật > chặn đường đi > UX > mã), chạy lại test.
Dừng sớm khi review không còn mục "sai luật" / "chặn đường đi" và người dùng thử chấm ≥ 4/5.

Sau mỗi vòng: commit tiếng Việt + `git push origin main` + deploy Pages + cập nhật `progress.md`.

---

## 8. Câu hỏi mở (đã chọn mặc định, người dùng đổi được sau)

| # | Câu hỏi | Mặc định |
|---|---|---|
| 1 | Mốc giờ của luật dịch +1h mùa đông? | Có (QĐ-7), có công tắc. |
| 2 | Độ rộng cửa sổ cấm 20:30 | ±5′ (QĐ-6, chưa đo). |
| 3 | POC hôm qua / cụm POC là hạng 2 cho B? | Có, cỡ ½, ghi "chưa đo" (QĐ-3). |
| 4 | Câu trả lời tầng 3 tự xóa? | Không; nhắc sau 10′. |
| 5 | Máy tính cỡ lệnh bắt buộc? | Không, gập mặc định. |
| 6 | Tên công cụ | "Trạm Đêm Vàng" (đổi trong `content.js`). |

---

## 11. Đối chiếu review 1 → bản 2

| Mục review | Sửa ở bản 2 |
|---|---|
| 1 bias KHÔNG/CHỜ | Bảng bật có trục bias: KHÔNG ⇒ chỉ C 2R ½; CHỜ ⇒ tất cả tắt, tầng 3 khóa, nút "Chốt lại bias". |
| 2 ngược bias | QĐ-9: A, C, D ⇒ NO; B chỉ với cờ tail/sp đúng phía, 2R, ½, lý do bắt buộc. |
| 3 SL theo kịch bản | B5 nhãn đổi theo kịch bản; B có "không ở giữa cụm". |
| 4 B giữa range | QĐ-1 + `NO_MID_RANGE`. |
| 5 LVN | QĐ-2: LVN vào hàng cấm fade. |
| 6 chấm 2 / cụm POC | QĐ-3; acceptance bước 1 nhận "một vùng đã kẻ" (chọn cạnh vừa phá từ danh sách). |
| 7 cửa sổ 20:30 | Tầng 0.2: 20:30 ±5′ và 21:00 ±5′ bật mặc định; 19:30 bật thứ Năm và khi chưa khai; tắt có vết (QĐ-6). |
| 8 4.4 hở 1–3 giá | C5 ba nút: ≤ 1 · 1–3 (CHỜ) · ≥ 3 (NO). |
| 9 B lẫn lộn | QĐ-5: lẫn ⇒ CHỜ, tăng ⇒ NO. |
| 10 B bong bóng | C4 với B: cần cùng phe; không có ⇒ CHỜ; đã vỡ ⇒ NO. |
| 11 D 2–3R | D: 2R, be +1R. |
| 12 ≥ 1 vùng | 3–5; < 3 cảnh báo + vết. |
| 13 giờ mùa đông | QĐ-7: mốc khai theo ET, London 25/10, thẻ nhắc đổi neo 01/11. |
| 14 acceptance bước 3 | Tầng 2 = 2 bước; bước 3 nằm trong B3 của A. |
| 15 limit / hủy | Tầng 4 trạng thái chờ khớp, "Khớp rồi" / "Hủy"; giá khớp thật vào sổ. |
| 16 lệnh mở gặp tin | Đếm ngược "flat trước hh:mm"; lý do đóng hợp lệ có tên. |
| 17 không sờ SL | Tầng 4 không có ô sửa SL. |
| 18 ba ca biên | QĐ-10; "Tôi vẫn vào" ở mọi phán quyết trừ ENTRY; lệnh qua 05:00 thuộc đêm cũ. |
| 19 dữ liệu sổ | `trades` có zoneId, zoneType, entry/sl/tp, rrPlanned, sweptThenTP, flags, ruleCodes; C4 có ô số bong bóng. |
| 20 Q2 đỉnh/đáy | Q2a, Q2b; High/Low hôm qua mang cờ. |
| 21 IB | Loại vùng IB high / IB low. |
| 22 hình B | QĐ-11. |
| 23 hỏi trùng | Tầng 3 tách Canh (≤ 7) / Bấm (≤ 6); mỗi sự thật một điều khiển; "loại bỏ" chỉ giữ thứ không suy được (C7). |
| 24 delta 50 % | Gộp vào B3 của B, 3 trạng thái, không nhập số. |
| 25 vết sửa Q6 | Trước 19:20 không ghi vết. |
| 26 "KỊCH BẢN A/B" | "Kế hoạch 1 / Kế hoạch 2" + "Hủy kế hoạch khi". |
| 27 cộng tay | Ô "Bạn cộng" cạnh "Máy cộng"; "Kết phiên" cần ô này. |
| 28 lệnh mở | Tầng 3 khóa hẳn, nhảy sang tầng 4. |
| 29 ½ chồng | QĐ-8. |
| 30 khóa 3′ | Tới phút tròn kế tiếp + 3′. |
| 31 phím tắt | Tắt trong ô nhập; Esc. |
| 32 từ Anh | Danh sách mở rộng; "Lõi giao thoa", "giờ mùa đông". |
| 33 chính tả | hòa, khóa theo HT; sửa tham chiếu 3c/3d. |
| 34 ngày đổi giờ | 25/10, 01/11/2026, 14/03/2027. |
| 35 file:// | Không module, UMD, SW scope tương đối + phiên bản + thẻ tải lại. |
| 36 thứ tự luật | Mục 5: danh sách luật có thứ tự, thứ tự ghi rõ. |
| 37 khóa đêm | `nightKey` theo mốc 05:00; test 00:30. |
| 38 ca test | Bổ sung đầy đủ ở mục 6, số cố định cho 6/10. |
| 39 lint | Cách đếm từ; lint không chạm ô nhập; ô nhập nhận dấu chấm. |
