# Plan — "Trạm Đêm Vàng": công cụ checklist chạy theo Hệ thống Đêm Vàng

Bản 3 · 2026-10-20 · tác giả: Claude (Fable 5.1) · người dùng: người học (trader vàng GC/MGC phiên Mỹ)
Lịch sử: bản 1 → review 1 (39 mục) → bản 2 → review 2 (22 mục) → bản 3. Mục 11 và 12 cuối file ghi từng mục đã sửa thế nào.

> Mục tiêu một câu: một trang web tĩnh mở lúc 18:00, dẫn người dùng đi đúng thứ tự của hệ thống
> (kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ), **khóa tầng dưới khi tầng trên chưa xong**,
> và bật chữ **ENTRY** to rõ đúng lúc đủ điều kiện — để sau 20 phiên, hệ thống thành phản xạ.

Quy ước: **HT** = `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (trích theo số mục); **ST** = `so-tay-vang-mgc.html`; **RULES** = `daily-trading/RULES.md`. Chính tả theo HT: *hòa, khóa, tắt máy*. **Thao tác** = 1 click hoặc 1 ô số bắt buộc; ô tùy chọn, hộp lý do và giá trị gợi ý sẵn không tính.

---

## 0. Nguồn, thứ tự ưu tiên và các quyết định về chỗ nguồn mâu thuẫn

| Nguồn | Vai trò |
|---|---|
| HT (16/10/2026) | **Nguồn luật chính.** Mọi câu chữ checklist lấy từ đây. |
| ST (8/2026) | Cơ chế phụ: nhịp buổi tối, 4 chart, lịch tin + cửa sổ cấm, giờ mùa đông Mỹ, máy tính cỡ lệnh MGC, hủy kịch bản, settlement, Globex bảo trì. |
| RULES (29/9, bổ sung 15/10) | Không nhồi lệnh (1 lệnh mở); chưa be thì không sờ SL; đóng tay phải có lý do có tên. |
| REVIEW 15/10 + nhật ký | "Vì sao có luật này" trong trợ giúp "?" của từng ô. |

**HT thắng ST** khi mâu thuẫn: R:R sàn 1:2 (mục tiêu 3R cho A, B; 2R cho C, D) · ngắt mạch = 2 lệnh phá luật hoặc 3 SL liên tiếp · 4 bài kiểm tra cơ chế thay X1–X4 · checklist 8 câu · nền tảng Optimus Flow thời gian thực (bỏ "chế độ lệnh chờ" của ST).

**Quyết định của plan (mã QĐ-n; hiện trong trợ giúp "?" kèm chữ "quyết định của công cụ, chưa đo" khi HT không nói)**

| Mã | Vấn đề | Quyết định |
|---|---|---|
| QĐ-1 | B tại VWAP giữa range khi Cân bằng: HT 5·B "hoặc cạnh VA Âu khi đang cân bằng" vs HT 3 "giữa range không có lệnh nào". | Cân bằng ⇒ B chỉ tại **vùng loại cạnh**, hoặc **vùng hạng 1–2 trùng cạnh** (mép gần nhất của vùng cách mép cạnh ≤ 1 giá). Không có vùng loại cạnh trong thẻ ⇒ B và C đều tắt `DIS_NO_EDGE`. VWAP giữa range ⇒ `NO_MID_RANGE`. |
| QĐ-2 | LVN: "vùng kẻ" (ca 13/10) hay "vùng cấm" (thẻ phiên HT 8)? | LVN là **cấm fade** (B chặn; A, D theo chiều được). Ca 13/10: vùng để bám là cụm POC, LVN chỉ nói giá đi nhanh. |
| QĐ-3 | Câu 2 checklist đòi "hạng 1–2 hoặc cạnh VA Âu khi cân bằng", nhưng ca ĐÚNG 6/10 (A phá cụm POC) và 13/10 (B tại POC). | Câu 2 = "giá ở **vùng trong thẻ phiên**, ≤ 1 giá". **Riêng B** vùng phải: hạng 1 (VWAP tuần) · hạng 2 (VWAP ngày, HVN tuần — HT đã đo; **cụm POC** = ≥ 2 POC cách nhau ≤ 1 giá — chưa đo, bằng chứng 13/10, cỡ ½) · cạnh theo QĐ-1 · hoặc ngoại lệ QĐ-9. **POC hôm qua chưa bị chạm = naked POC: HT 2.3 đã đo 46,5 % ⇒ chỉ làm mục tiêu**, không có loại vùng "POC hôm qua" riêng. |
| QĐ-4 | "Không cản tàu" ở chế độ Vừa phá: B ngược chiều phá? HT chế độ 2 "hấp thụ theo chiều". | Vừa phá ⇒ B cùng chiều phá: được. B ngược chiều phá: **chỉ khi cùng chiều bias và vùng hạng 1 (VWAP tuần)** và vùng không phải cạnh vừa phá; mọi ca khác ⇒ `NO_FIGHT_BREAK`. Không hỏi lại "đang phá?" — engine suy từ chế độ + vùng + hướng. |
| QĐ-5 | HT 4.2 luật cứng "giảm dần qua 3 nến" vs ca ĐÚNG 5/10 "delta lẫn lộn". | Theo luật cứng: B cần "giảm dần"; "lẫn lộn" ⇒ CHỜ; "tăng dần" ⇒ `NO_MOMENTUM`. Ca 5/10 ghi là ngoại lệ chưa đo. |
| QĐ-6 | Cửa sổ cấm: HT 7 "đánh tin 19:30 / 20:30 / 21:00 = 0" không cho độ rộng; HT 3.2 nói cú phá đáng tin 20:20–21:30; ca mẫu 6/10 vào lúc 20:24–20:25. | 19:30 ±15′ ⇒ **KHÔNG VÀO** (hạng 1, ST). 21:00 ±5′ ⇒ **KHÔNG VÀO** (hạng 2, ST; ca 1/10 bị râu 21:00 quét). **20:30: chỉ cảnh báo** thanh vàng "NYSE mở — không đánh tin", không chặn. Mùa đông +1h. |
| QĐ-7 | Mốc giờ của luật có dịch theo giờ mùa đông không? HT không nói. | **Có.** Mỗi mốc trong `rules.js` mang múi gốc `ET` / `LONDON` / `VN`; `time.js` đổi sang giờ VN. London đổi 25/10/2026, Mỹ 01/11/2026, Mỹ trở lại 14/03/2027. Ngày 01/11 hiện thẻ một lần: "đổi neo session TPO / SessionZones 19:20 → 20:20, IB = 20:20–21:20". Công tắc tắt trong cài đặt. |
| QĐ-8 | "Cỡ nhỏ", "cỡ một nửa". | ½ cỡ chuẩn, **áp một lần, không nhân chồng**. |
| QĐ-9 | Ngược bias: HT 2.2 chỉ cho "hấp thụ buy tại đỉnh có tail thật hoặc single print cũ phía trên, cỡ nhỏ, 2R" (và gương). | Ngược bias ⇒ A, C, D: `NO_COUNTER_BIAS_SCENARIO`. **B được miễn điều kiện hạng** khi vùng mang cờ `tail` (High/Low hôm qua với Q2 = tail thật) hoặc `sp` (single print) **đúng phía** (sell ⇒ cờ ở phía trên; buy ⇒ phía dưới); TP ép 2R, cỡ ½, lý do bắt buộc. Thanh ENTRY in "ngược bias · 2R · ½". |
| QĐ-10 | Chuỗi SL liên tiếp: hòa có reset không? | Chỉ SL cộng chuỗi; TP và hòa reset về 0. |
| QĐ-11 | Hình "B" trong mẫu thẻ phiên HT 8 nhưng Q1 không định nghĩa. | Giữ; trợ giúp: "B = hai phân phối — HT không định nghĩa; chỉ để ghi hình". |
| QĐ-12 | Giá trên VWAP tuần nhưng Q1 = b (hoặc dưới và P): HT chỉ nói "profile không phải b" là điều kiện BUY. | ⇒ bias **KHÔNG** (chưa đo). |
| QĐ-13 | Trend thin: B cùng chiều trend ở nhịp hồi có phải "cản tàu"? | B tắt với lý do `DIS_USE_D` "cùng chiều ở nhịp hồi ⇒ gọi là D". |
| QĐ-14 | Cỡ ½ cho vùng hạng 2 áp cho kịch bản nào? | **Chỉ B.** A, D tại hạng 2 cỡ chuẩn (HT 5·B mới nói cỡ nhỏ). |
| QĐ-15 | HVN ngày (thường) không có hạng trong HT 2.3; HT 5·B cấm hấp thụ ở HVN ngày ngay sau phá cực trị. | HVN ngày: **B chặn** mọi lúc (sau phá nghiêng đi tiếp 43,5 %; lúc thường chưa đo); A, D được. |
| QĐ-16 | TP vượt quá vùng kế tiếp (HT 6: "3R, hoặc vùng kế tiếp nếu gần hơn"). | TP gợi ý = gần hơn giữa 3R (A, B) / 2R (C, D) và vùng kế tiếp theo hướng lệnh trong thẻ; người dùng sửa được nhưng TP vượt vùng kế tiếp quá 0,5 giá ⇒ `NO_TP_PAST_ZONE`; vùng kế tiếp cho R:R < 1:2 ⇒ `NO_RR` "vùng kế tiếp quá gần". |
| QĐ-17 | Cách đếm "lần thứ n tại vùng", chuỗi SL, phá luật. | n = số dòng `trades` trong đêm cùng `zoneId`, đã khớp, **kể cả** phá luật, **không kể** `paper` và limit đã hủy. `paper` không cộng chuỗi SL, không cộng phá luật, vào sổ với cờ. |
| QĐ-18 | C6 (nến cao nhất 5 nến) nhập lúc Canh, luật tính lúc Bấm. | Giữ ở Canh để Bấm nhẹ; bước Bấm hiện lại số với ô sửa tại chỗ (0 thao tác nếu không đổi). Chọn lựa có chủ đích. |

---

## 1. Người dùng, bối cảnh dùng, mục tiêu

- Một người dùng, đi làm ban ngày, trade 18:00 → 00:30 giờ VN, màn chính là Optimus Flow; công cụ mở ở màn phụ hoặc nửa màn, **chuột là chính**, bàn phím khi quen.
- Ban ngày liếc điện thoại (xem thẻ phiên, sổ). Phải dùng được trên điện thoại nhưng tối ưu cho máy tính.
- Dùng **hằng đêm, 20 phiên liên tiếp** → ít chữ, không bắt đọc lại, nhớ trạng thái, **mỗi sự thật chỉ hỏi một lần**.
- Mục tiêu đo được (HT 10): sau 20 phiên có **nhật ký 7 cột đầy đủ** để đếm "lệnh qua đủ 8 câu thắng bao nhiêu, thiếu câu nào thua bao nhiêu".

**Không làm (v1):** không đọc dữ liệu từ Optimus Flow, không tự nhận diện chart, không đồng bộ đám mây, không nhiều người dùng, không tiếng Anh.

---

## 2. Hình thức: trang web tĩnh, cài được như ứng dụng, mở được bằng file://

- HTML/CSS/JS thuần, **không framework, không bước build, không `type="module"`** (mở trực tiếp `index.html` bằng `file://` vẫn chạy — mục 5). Deploy GitHub Pages ở repo công khai mới `AnhNMTHE176111/tram-dem-vang` → `https://anhnmthe176111.github.io/tram-dem-vang/`.
- **PWA** (chỉ khi mở qua Pages): manifest + service worker để "Cài đặt" thành cửa sổ riêng và chạy không mạng. Mở bằng `file://` thì không có service worker, mọi tính năng khác vẫn chạy.
- **Dữ liệu ở máy**: `localStorage`; xuất / nhập JSON, xuất Markdown. Nhắc xuất file mỗi cuối tuần (một dòng).
- Mã nguồn trong repo `footprint-tpo` tại `tram-dem-vang/`; `deploy.sh` sao chép sang clone của repo Pages rồi push.

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

Khóa tầng: **1** luôn mở · **2** luôn mở · **3** mở khi thẻ phiên đã chốt **và** bias ≠ CHỜ **và** không có lệnh (chờ khớp hoặc đã khớp) · **4** mở khi có lệnh · **5** luôn mở. Khi có lệnh, tầng 3 khóa hẳn và giao diện tự nhảy sang tầng 4 (RULES A.3).

### Tầng 0 · Trước khi mở chart (18:00)
| # | Ô | Kiểu | Hệ quả |
|---|---|---|---|
| 0.1 | Tỉnh táo, không bực dọc, không mệt rã rời | có / không | Không ⇒ cả đêm **CHỈ XEM**: vẫn đi hết checklist; ENTRY hiện xám "ENTRY (chỉ xem)", nút thành "Ghi kèo luyện mắt" (vào sổ với cờ `paper`, QĐ-17). |
| 0.2 | Cửa sổ cấm tối nay | danh sách, bật/tắt từng dòng; thêm dòng tùy chỉnh (giờ · hạng 1/2 · phút trước/sau) | Mặc định: **21:00 ±5′** bật; **19:30 ±15′** bật vào **thứ Năm** (Jobless Claims) và khi tầng 0 chưa được chạm; **20:30** là dòng cảnh báo (QĐ-6), không tắt được. FOMC: 01:00/01:30, nhắc đóng sạch trước 00:45. Tắt một dòng ⇒ ghi vết "tắt cửa sổ 19:30 lúc hh:mm" (cần xác nhận). Ngày NFP/CPI ⇒ cờ "cỡ ½ cả đêm". Mùa đông +1h. |
| 0.3 | Kịch bản nền ban ngày (1 dòng, tùy chọn) | chữ | Hiện lại ở thẻ phiên. |

### Tầng 1 · Kẻ vùng trên chart A và chốt thẻ phiên (18:30–19:20; mùa đông 19:30–20:20)
**1a. Kẻ trên chart** (tick khi đã kẻ xong):
1. Chart A: TPO ngày neo giờ pit COMEX (19:20; mùa đông 20:20) + TPO gộp 3 tuần, bracket 30′.
2. 5 mức hôm qua: High · VAH · POC · VAL · Low.
3. VWAP tuần (hạng 1) và VWAP ngày (hạng 2).
4. HVN / LVN ngày và 3 tuần.
5. Nợ: single print chưa lấp, poor high / poor low.
6. Naked POC các phiên trước (chỉ mục tiêu).
7. Range Á / Âu: VAH Âu, VAL Âu; IB high / IB low khi đã có.

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

**1c. Bias** — ô *Giá hiện tại so với VWAP tuần*: trên · dưới · sát (±2 giá). Ma trận (HT 2.2 + QĐ-12):

| VWAP tuần | Q5 | Q1 | ⇒ Bias | Được làm gì |
|---|---|---|---|---|
| trên | trên hoặc trong | ≠ b | **BUY** | A buy · B (hấp thụ sell) tại vùng · C fade đáy VA Âu. Sell chỉ theo QĐ-9. |
| dưới | dưới hoặc trong | ≠ P | **SELL** | gương ngược |
| trên | dưới | — | **KHÔNG** | chỉ C hai cạnh VA Âu, 2R, cỡ ½; A, B, D tắt |
| dưới | trên | — | **KHÔNG** | như trên |
| trên | bất kỳ | b | **KHÔNG** | QĐ-12 |
| dưới | bất kỳ | P | **KHÔNG** | QĐ-12 |
| sát | bất kỳ | — | **CHỜ** | tầng 3 khóa; nút "Chốt lại bias" khi người dùng xác nhận "đã có 1 nến M5 đóng rõ: trên / dưới" ⇒ tính lại |

Bias tự động; **ghi đè** được với lý do bắt buộc (cờ "bias ghi đè").

**1d. Vùng đã kẻ (3–5; < 3 vẫn chốt được, cảnh báo vàng "mới có n/3 vùng", ghi vết)** — mỗi vùng: loại · giá (số hoặc khoảng "4181–4183"; so khoảng cách bằng mép gần nhất) · ghi chú. Hạng, vai và cờ tự suy:

| Loại | Hạng / vai | Kịch bản hợp lệ tại vùng | Cờ |
|---|---|---|---|
| VWAP tuần | hạng 1 | B, A, D | |
| VWAP ngày · HVN tuần | hạng 2 (HT đã đo) | B (½, QĐ-14), A, D | |
| cụm POC (≥ 2 POC cách ≤ 1 giá) | hạng 2 (chưa đo, QĐ-3) | B (½), A, D | |
| VAH Âu · VAL Âu · cạnh range · IB high · IB low | cạnh | C; B khi Cân bằng; A sau khi phá | `edge` |
| High hôm qua · Low hôm qua | cạnh (ngoài) | C, A, D; **B chỉ ngược bias theo QĐ-9** | `edge`; `tail` nếu Q2a/Q2b = tail thật |
| single print (chọn phía: trên / dưới) | nợ, mục tiêu ưa thích | TP; B ngược bias theo QĐ-9 | `sp` + phía |
| poor high / poor low | nợ, mục tiêu | TP | |
| naked POC (POC phiên trước chưa chạm) | **chỉ mục tiêu** (đã đo 46,5 %) | TP; A, D theo chiều khi là cạnh vừa phá | |
| HVN ngày | trung tính (QĐ-15) | A, D; **B chặn** | `banned` |
| HVN 3 tuần · LVN | **cấm fade** (QĐ-2) | A, D theo chiều; **B chặn** | `banned` |

**1e. Thẻ phiên** (cột phải) tự điền đúng mẫu HT 8: NGÀY · VWAP tuần · Đóng hôm qua · Hình hôm qua · BIAS · VÙNG · NỢ · VÙNG CẤM (gom các vùng `banned`) · **Kế hoạch 1 / Kế hoạch 2** ("nếu … thì …") · **Hủy kế hoạch khi …**. Nút **"Chốt thẻ phiên"**:
- Điều kiện: Q1, Q5, Q6, VWAP tuần đã trả lời; ≥ 1 vùng.
- Sau chốt vẫn sửa được. **Trước 19:20 (mùa đông 20:20)** sửa Q6 / vùng VA Âu / IB không ghi vết. Sau đó mỗi lần sửa ghi "sửa lúc hh:mm: …"; đang có kèo ở tầng 3 ⇒ cảnh báo "đang canh kèo — sửa thẻ lúc này là nắn kế hoạch", phải xác nhận.
- Chưa chốt ⇒ tầng 3 khóa: "Không có thẻ phiên thì không có lệnh."

### Tầng 2 · Chế độ thị trường (chart B, M30/M5)
- Chọn **chế độ**: Cân bằng · Vừa phá · Trend thin. Đổi lúc nào cũng được; mỗi lần ghi vào dòng thời gian của đêm.
- *Vừa phá* cần: hướng phá (lên / xuống) · **cạnh vừa phá** (chọn từ vùng `edge` hoặc vùng bất kỳ trong thẻ) · giờ phá (mặc định "bây giờ") · lần mấy (1 / 2) · hai bước acceptance (bước 3 của HT 3.1 nằm trong B3 của A):
  1. Có 1 nến M5 đóng ngoài cạnh đó.
  2. Nhịp hồi về cạnh giữ được: không nến M5 nào đóng ngược vào trong.
  Nút "Chui lại trong (phá hụt)" ⇒ về Cân bằng, lần phá kế tiếp mặc định là lần 2; nhắc "không đuổi, chờ lần 2".
- **Chế độ hiệu lực** (engine suy): `balanced` · `pending` (bước 1 có, bước 2 chưa — hiện "**chờ công nhận**") · `broken` (đủ 2 bước) · `thin`. Giờ phá trong 18:00–19:20 (mùa đông 19:00–20:20) ⇒ A `DIS_EARLY_BREAK`.
- **Bảng bật kịch bản** (4 thẻ A–D sáng / mờ, lý do mờ tra theo mã trong `content.js`):

| Điều kiện (thứ tự ưu tiên từ trên xuống) | A Phá hồi | B Hấp thụ | C Fade cạnh | D Trap |
|---|---|---|---|---|
| Bias CHỜ | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` |
| Khóa 3′ sau nến dài nhất | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` |
| Bias KHÔNG | `DIS_BIAS_NONE` | `DIS_BIAS_NONE` | **bật** 2R ½ | `DIS_BIAS_NONE` |
| Trước 20:30 (mùa đông 21:30) | `DIS_BEFORE_2030` | `DIS_BEFORE_2030` | bật, ½ | `DIS_BEFORE_2030` |
| `balanced` | `DIS_NOT_BROKEN` | bật tại cạnh (QĐ-1); không có cạnh ⇒ `DIS_NO_EDGE` | **bật**; không có cạnh ⇒ `DIS_NO_EDGE` | `DIS_NO_MOVE` |
| `pending` (chờ công nhận) | `DIS_PENDING_ACCEPT` | như `balanced`, nhưng tại cạnh vừa phá ⇒ `DIS_PENDING_ACCEPT` | tại cạnh vừa phá ⇒ `DIS_PENDING_ACCEPT`; cạnh khác: bật | `DIS_NO_MOVE` |
| `broken` | **bật** cùng chiều phá | bật cùng chiều; ngược chiều theo QĐ-4 | `DIS_M5_OUTSIDE` | bật cùng chiều phá |
| `thin` | bật ở nhịp hồi, cùng chiều | `DIS_USE_D` (QĐ-13) | `DIS_M5_OUTSIDE` | **bật** cùng chiều |

- Nút **"Vừa có nến dài nhất phiên"** ⇒ khóa tới **phút tròn kế tiếp + 3′**, hiện "mở lại 21:21"; sau đó nhắc "chờ hồi; không hồi thì bỏ".
- Dải giờ (HT 3.2) theo giờ thật: 18:00–19:20 "phá giả", 19:20–20:30 "mở ảo", 20:20–21:30 "cú phá đáng tin" (mùa đông +1h).

### Tầng 3 · Kèo trên M1 — hai bước **Canh** và **Bấm**, phán quyết sống
**Mỗi sự thật một điều khiển**, 3 trạng thái (tốt / xấu / không rõ; chưa chạm = chưa trả lời ⇒ CHỜ). Thứ suy được thì không hỏi (acceptance, giờ, chế độ, nến dài nhất, bias, hạng vùng, lần tại vùng, "đang phá?").

**3a. Canh — trước khi nến xác nhận đóng (A 5 · B 7 · C 5 · D 7 thao tác)**

| # | Điều khiển | Lựa chọn | Hệ quả |
|---|---|---|---|
| C1 | Kịch bản | A · B · C · D (chỉ thẻ đang bật) | |
| C2 | Hướng | buy · sell. **Tự điền**: A = chiều phá; D = chiều bias; C = theo cạnh (VAH / High / IB high ⇒ sell; VAL / Low / IB low ⇒ buy). B: người dùng chọn. Sửa được. | ngược bias ⇒ QĐ-9; hộp "Lý do ngược bias" bắt buộc (không tính thao tác) |
| C3 | Vùng | chọn từ thẻ phiên | hiện hạng, cờ, **lần thứ n** (QĐ-17; n = 3 ⇒ `NO_ZONE_3RD`); `banned` với B ⇒ `NO_BANNED_ZONE`; giữa range khi `balanced` ⇒ `NO_MID_RANGE`; cản tàu ⇒ `NO_FIGHT_BREAK` |
| C4 | 4.3 Bong bóng to gần nhất (10 nến, ở cực trị) | cùng phe · ngược phe còn giữ (vòng trắng) · ngược phe đã vỡ (mờ) · không có / ở giữa move · không rõ — ô số tùy chọn "±___" | "ngược còn giữ" ⇒ `NO_BUBBLE_AGAINST`; "không rõ" ⇒ `NO_UNCLEAR`. **B**: cần "cùng phe"; "không có" ⇒ CHỜ; "đã vỡ" ⇒ `NO_BUBBLE_AGAINST`. A, C, D: "không có / giữa move" ⇒ qua (HT 4.3 "bỏ qua") |
| C5 | 4.4 Giá cách vùng | ≤ 1 giá hoặc râu chạm · hơn 1, chưa tới 3 · từ 3 giá (ở lưng) | hơn 1 ⇒ CHỜ "chờ hồi về cạnh"; từ 3 ⇒ `NO_BACK` |
| C6 | Biên độ nến M1 cao nhất trong 5 nến (giá) | số | sàn nhiễu (QĐ-18) |
| C7 | Ô riêng | **B**: DMA — ngang · còn dốc ⇒ `NO_DMA_SLOPE`. **D**: "move vừa rồi: __ giá" (số; < 5 ⇒ `NO_D_NO_MOVE`) · "nhịp hồi đã quá 70 % move?" chưa · rồi ⇒ `NO_D_DEEP`. A, C: không có | |

**3b. Bấm — sau khi nến xác nhận đóng (A 5 · B 6 · C 4 · D 5 thao tác)**

| # | Điều khiển | Lựa chọn | Áp cho |
|---|---|---|---|
| B1 | 4.1 Nhịp hồi | **U** · **V** · không rõ (tiêu chí U/V hiện 2 dòng dưới nút) | A, B, D. V ⇒ `NO_V_PULLBACK`; không rõ ⇒ `NO_UNCLEAR`. C: ẩn |
| B2 | 4.2 Thân + \|delta\| 3 nến cuối | giảm dần · lẫn lộn · tăng dần · không rõ | **B**: giảm ⇒ qua; lẫn ⇒ CHỜ; tăng ⇒ `NO_MOMENTUM`; không rõ ⇒ `NO_UNCLEAR`. A, C, D: ẩn |
| B3 | "Nến xác nhận đạt chuẩn?" | đạt · chưa · không rõ — **tiêu chí hiện thành danh sách 2–4 dòng dưới nút** (`criteria[]` trong `content.js`, lint bỏ qua): **A** đóng theo chiều phá · thân ≥ nửa biên độ · delta cùng dấu · tại cạnh: delta cùng chiều phá hoặc hấp thụ phe ngược. **B** ngược chiều move · delta đảo dấu ≥ ½ nến lớn nhất của move. **C** râu xuyên cạnh rồi đóng lại trong · thân không ngắn, râu ngược không dài · delta ủng hộ. **D** đỉnh hồi có bong bóng hấp thụ phe hồi hoặc nến hồi delta thuận đóng dưới nửa thân · nến xác nhận đóng theo chiều cũ, thân dài, delta cùng dấu | tất cả. chưa ⇒ CHỜ; không rõ ⇒ `NO_UNCLEAR` |
| B4 | Giá vào · SL · TP | 3 số (nhận "4193.5" và "4193,5"); **TP gợi ý sẵn theo QĐ-16** (không tính thao tác nếu giữ) | |
| B5 | "SL đúng chỗ?" | đúng chỗ · chưa chắc · sai chỗ — tiêu chí 1 dòng theo kịch bản: **A** sau râu nến xác nhận hoặc mép xa vùng, cái xa hơn, + 0,3 · **B** sau cực trị cụm hấp thụ + 0,3, không ở giữa cụm · **C** sau râu phá hụt + 0,3 · **D** sau đỉnh nhịp hồi + 0,3 | chưa chắc ⇒ CHỜ; sai ⇒ `NO_SL_POS` |

Máy tính tự kiểm từ B4 + C6 (C6 hiện lại kèm ô sửa tại chỗ): khoảng SL ≥ nến cao nhất (`NO_SL_FLOOR`: "SL 2,1 < nến 3,3 — đẩy SL ra hoặc bỏ kèo") · ≤ 4 giá (`NO_SL_CAP`) · R:R ≥ 1:2 (`NO_RR`) · SL/TP đúng phía (`NO_SL_SIDE`) · TP không vượt vùng kế tiếp (`NO_TP_PAST_ZONE`). Thu gọn được: **cỡ lệnh MGC** (vốn, % rủi ro nhớ trong cài đặt; tick 0,1 = 1 $; số hợp đồng làm tròn xuống; ½ theo QĐ-8 khi: bias KHÔNG · C · ngược bias · ngày NFP/CPI · B tại hạng 2).

**3c. Phán quyết** (thanh dính đáy, tính lại sau mỗi click, theo thứ tự luật mục 5):
1. **TẮT MÁY** (đen) — ngắt mạch đã kích. Tầng 3 vẫn xem được để luyện mắt nhưng phán quyết tối đa là TẮT MÁY.
2. **KHÔNG VÀO** (đỏ) + tối đa 2 mã lý do đầu theo thứ tự luật.
3. **CHỜ** (vàng) — tối đa 3 ô còn thiếu theo thứ tự nên làm tiếp.
4. **ENTRY** (xanh, ≥ 32 px), ví dụ ca 6/10 cùng chiều bias: `ENTRY SELL 4193,0 · SL 4195,4 (2,4 giá) · TP 4185,0 · 1:3,3 · cỡ chuẩn` → nút **"Vào lệnh"** mở hộp: **market** (nhập giá khớp) / **limit** (giá chờ) ⇒ tầng 4.
- Nút phụ **"Tôi vẫn vào (phá luật)"** hiện ở **mọi** phán quyết trừ ENTRY (kể cả TẮT MÁY) — mở cùng hộp vào lệnh; dòng sổ mang cờ ⚠ phá luật + các mã đang vi phạm; tăng ngắt mạch (QĐ-17).
- **Tám chấm** (HT 9) ngay trên thanh, sáng theo dữ liệu: 1 thẻ phiên + cùng chiều bias (hoặc ngược bias hợp lệ QĐ-9) · 2 vùng trong thẻ ≤ 1 giá (B: hạng theo QĐ-3) · 3 chế độ bật kịch bản · 4 U (C: tự sáng) · 5 bong bóng cùng phe hoặc đã vỡ; A, C, D sáng cả khi "không có / giữa move"; B chỉ sáng khi "cùng phe" · 6 B (B2 giảm dần) / A, C, D (B3 đạt) · 7 B3 đạt và không trong 3′ sau nến dài nhất · 8 B5 đúng chỗ + sàn + trần + R:R + lần ≤ 2. Di chuột ⇒ câu đầy đủ.
- Không tự xóa; sau **10′** không thao tác hiện "đã 10′ — nến M1 đã khác, kiểm lại". **"Kèo mới"** xóa tầng 3 (giữ 0–2). Đổi kịch bản giữa chừng giữ C3–C6, tính lại C2, xóa C7 và bước Bấm.

### Tầng 4 · Lệnh (tối đa 1)
- **Chờ khớp** (limit): "Khớp rồi" (nhập giá khớp thật) · "Hủy — giá bỏ đi" (không vào sổ, không tăng đếm vùng).
- **Đã khớp**: hướng · giá vào thật · SL · TP · R dự kiến · size; ô "giá hiện tại" ⇒ R hiện tại. **Không có ô sửa SL** (RULES D). Mốc be tự tính: A/B **+1,5R** kèm ô "đã có 1 nến M1 đóng ngoài vùng vào" ⇒ nút "Đã dời về hòa" mở; C/D **+1R**.
- Cửa sổ cấm hạng 1 / FOMC sắp tới mà lệnh còn mở ⇒ đếm ngược "**đóng sạch trước hh:mm**" (19:15 / 00:45; mùa đông +1h). Đóng vì lý do này hợp lệ.
- **Đóng lệnh**: TP · SL · hòa · đóng tay (lý do: "hấp thụ ngược đe dọa TP" · "đóng sạch trước tin" · "khác" ⇒ cờ phá luật). Nhập giá thoát ⇒ R gợi ý, sửa được.
- Sau khi đóng: "SL bị quét rồi giá tới TP?" (tick sau) · ghi chú. Dòng sổ hoàn tất; ngắt mạch cập nhật (QĐ-10, QĐ-17). Lệnh còn mở qua mốc đêm mới ⇒ vẫn thuộc đêm vào lệnh; đêm mới mở ở tầng 4 và nhắc Globex bảo trì (04:00–05:00 hè; 05:00–06:00 đông).

### Tầng 5 · Sổ (đêm nay · tuần · xuất)
- **Đêm nay**: bảng 7 cột đúng mẫu HT 8 (`giờ | hướng | tên | chế độ | 4 kiểm tra | SL | R`); cột "4 kiểm tra" in "U · bb −129 giữ · Δ giảm · cạnh" từ B1 / C4 (+ số) / B2 hoặc B3 / C5 — cột Δ in "giảm" (B), "nến mạnh" (A, C, D khi B3 đạt), "—" nếu thiếu; dòng ⚠ nêu điều phá. Chân bảng: **"Máy cộng: x R"** cạnh **"Bạn cộng: __ R"** (cộng tay thật); lệch ⇒ đỏ; thêm lệnh phá luật · SL bị quét rồi tới TP. "Kết phiên" chỉ mở khi đã nhập "Bạn cộng"; sau kết vẫn sửa R có vết.
- **Tuần**: 4 con số HT 8 — phá luật/tổng · SL quét rồi tới TP · R theo tên kịch bản và theo loại vùng · lệnh ngược bias và kết quả; chuỗi đêm 0 phá luật.
- **Xuất**: Markdown (mẫu 7 cột + thẻ phiên) · JSON (sao lưu; nhập lại gộp theo đêm, không trùng) · CSV.

### Thanh trạng thái + đồng hồ
- Giờ VN; nhãn pha (ST §1; mỗi mốc theo múi gốc QĐ-7): Ban ngày · Chuẩn bị 18:00 (VN) · COMEX mở 19:20 (ET) · Tin 19:30 (ET) · NYSE 20:30 (ET) · Lõi giao thoa 21:00 (ET) – 22:30 (LONDON) · London đóng 22:30 (LONDON) · Mỏng dần sau 23:00 (VN) · Chốt giá ngày 00:30 (ET) · Globex bảo trì 04:00–05:00 (ET). Dòng "Mỹ đang giờ mùa đông: mốc +1h" từ 01/11; tuần 25/10–31/10 chỉ mốc London dịch.
- Đếm ngược tới cửa sổ cấm kế; trong cửa sổ: thanh đỏ "CỬA SỔ CẤM — không vào"; 20:30 ±5′: thanh vàng.
- Chip: phá luật n/2 · SL liên tiếp n/3 · lệnh mở 0/1 · vùng đang chọn n/2.
- **Khóa đêm** `nightKey(now)` = ngày hôm nay nếu đã qua mốc Globex mở (05:00 ET hè / 06:00 đông, giờ VN), ngược lại hôm qua.

---

## 4. Nguyên tắc UI/UX (bắt buộc với người implement)

1. **Một màn hình, một việc.** Tầng chưa mở hiện mờ với một câu lý do. Bước Bấm vừa một màn 1366×768 không cuộn.
2. **Phán quyết luôn thấy** ở tầng 3; màu cố định: xanh ENTRY · vàng CHỜ · đỏ KHÔNG VÀO · đen TẮT MÁY · xám CHỈ XEM.
3. **Nhãn chính ≤ 9 từ** (đếm theo khoảng trắng, bỏ ký hiệu toán và số); tiêu chí dài để trong `criteria[]` dưới nút; trợ giúp "?" ≤ 2 câu + link đúng mục trang HT (`…/he-thong-dem-vang/#id`: `sau-cau-hoi ma-tran-bias xep-hang-vung acceptance thoi-gian v-hay-u than-delta bong-bong-phe canh-hay-lung kb-a kb-b kb-c kb-d xung-dot ca-that luat-sl tp-be the-phien nhat-ky-lenh cuoi-tuan`). Mỗi kịch bản kèm ảnh ca thật (`img/kb-*.png`).
4. **Hai mức hướng dẫn**: *Mới* (trợ giúp + lý do nhật ký dưới mỗi ô) · *Quen* (chỉ nhãn). Nhớ lựa chọn.
5. **Nút chọn nhóm 3 trạng thái** cho mọi câu có đáp án xấu, đáp án xấu tô đỏ khi chọn; không checkbox.
6. **Không hộp thoại xác nhận** trừ: sửa thẻ phiên khi đang canh kèo (sau 19:20), "Tôi vẫn vào (phá luật)", xóa dữ liệu, tắt cửa sổ cấm.
7. **Bàn phím** (tầng 3, tắt khi focus trong ô nhập; `Esc` rời ô nhập): `1–4` kịch bản, `B`/`S` hướng, `U`/`V` câu 4.1, `Enter` nút chính, `N` kèo mới, `?` trợ giúp. Gợi ý phím nhỏ cạnh nút.
8. **Giao diện tối mặc định**, tương phản WCAG AA, có chế độ sáng. Font hệ thống. Số hiển thị dấu phẩy (4193,5); ô nhập nhận cả dấu chấm.
9. **Điện thoại ≥ 360 px**: tầng dọc, thẻ phiên thành ngăn trượt, thanh phán quyết dính đáy, không tràn ngang.
10. **Nhanh**: không thư viện ngoài, tải < 100 KB, thao tác < 50 ms, lưu ngay sau mỗi click.
11. **Ngôn ngữ**: tiếng Việt đủ dấu, câu ngắn. Giữ tiếng Anh: buy · sell · limit · market · sell limit · buy limit; thuật ngữ: TPO, VA, VAH, VAL, POC, HVN, LVN, VWAP, delta, DMA, IB, R, SL, TP, be, fade, trap, tail, single print, poor high/low, naked POC, bias, acceptance, move, retest, range, bracket, session, tick, thin, Trend thin, setup, profile, COMEX, NYSE, Globex, FOMC, NFP, CPI, Jobless Claims, ET, Markdown, JSON, CSV, Esc, Enter. Viết tiếng Việt thay cho: flat → "đóng sạch", settlement → "chốt giá ngày", overlap → "giao thoa", DST → "giờ mùa đông", paper → "luyện mắt". Cấm: "bán"/"mua" cho hướng lệnh, "lệnh chờ", "đập giá". Lint tự động (mục 6).

---

## 5. Kiến trúc kỹ thuật

```
tram-dem-vang/
  index.html                 # khung 1 trang; nạp js/*.js bằng <script> thường, đúng thứ tự
  manifest.webmanifest · sw.js · icons/ · img/kb-*.png
  css/app.css                # token màu (:root, [data-theme]), layout, thành phần
  js/content.js              # TOÀN BỘ chữ: nhãn, criteria[], trợ giúp, lý do theo mã — dữ liệu thuần
  js/rules.js                # DANH SÁCH LUẬT CÓ THỨ TỰ + hằng số (ma trận bias, bảng vùng, mốc giờ có múi, ngưỡng, APP_VERSION)
  js/time.js                 # giờ VN, giờ mùa đông Mỹ/London, pha, cửa sổ cấm, nightKey
  js/engine.js               # thuần: (night, now) → {verdict, reasons, missing, dots, order, enabled:{A,B,C,D: code|null}, regime}
  js/store.js                # localStorage, version + migrate, xuất/nhập
  js/journal.js              # dòng 7 cột, cộng, 4 con số tuần, Markdown/CSV
  js/ui/*.js · js/main.js    # render, sự kiện
  tests/*.test.js            # node:test, CommonJS (package.json không có "type":"module"), nạp js/*.js bằng require
  e2e/*.spec.mjs             # Playwright chromium
  scripts/lint-vi.mjs · deploy.sh · README.md
  docs/IMPL-n.md · REVIEW-n.md · USER-TEST-n.md
```

- **Không ES module** (file:// chặn module). Mỗi file JS dùng mẫu UMD nhỏ: `(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else (root.TDV = root.TDV || {}).engine = factory(); })(this, function () { … })`.
- **Service worker** (chỉ trên Pages): `scope` `./`, tên cache theo `APP_VERSION`, `skipWaiting` + `clients.claim`, thẻ "có bản mới — tải lại" khi SW mới kích hoạt. `deploy.sh` tăng `APP_VERSION` (ngày + hash ngắn).
- **Engine = danh sách luật có thứ tự** `[{code, scope: 'all'|'A'|'B'|'C'|'D', when(state, now) → bool, effect: 'OFF'|'NO'|'WAIT'|'DISABLE'}]`, chạy tuần tự, `reasons` giữ thứ tự. Thứ tự: `OFF_RULE_BREAKS`, `OFF_SL_STREAK` → lệnh mở → cửa sổ cấm (`NO_NEWS_WINDOW`) → `DIS_LONGEST_BAR` → thẻ phiên / `DIS_BIAS_WAIT` → `DIS_BIAS_NONE` → `DIS_BEFORE_2030` → chế độ × kịch bản (`DIS_*`) → hướng vs bias (`NO_COUNTER_BIAS_*`) → vùng (`NO_ZONE_3RD`, `NO_BANNED_ZONE`, `NO_MID_RANGE`, `NO_FIGHT_BREAK`, hạng cho B) → C4, C5 → C7 → B1, B2 → B3 → B5, SL / R:R / TP. `paper` không phải luật, là cờ hạ cấp ENTRY. Ví dụ thứ tự: ca 12/10 ra `NO_BUBBLE_AGAINST` rồi `NO_V_PULLBACK`.
- **Mô hình dữ liệu** `localStorage["tdv.v1"]`:
```
{ version: 1,
  settings: {theme, guideLevel, capital, riskPct, dstShift: true, shortcuts: true},
  nights: { "<nightKey>": {
     t0: {alert, touched, windows:[{id, kind, rank:1|2, at:'HH:MM', tz:'ET', minutesBefore, minutesAfter, on, offAt?}], halfSize, note},
     card: {answers:{q1,q1w,q2top,q2bot,q3,q4,q5,q6,vwapW}, bias:{auto, override, reason, rechecked},
            zones:[{id,type,price,priceTo?,side?,note,flags:['edge'|'tail'|'sp'|'banned']}], plan1, plan2, cancelWhen, lockedAt, edits:[{at,what}]},
     regime: {mode, breakout:{dir, edgeZoneId, at, nth, step1, step2}, longestBarUntil, log:[{at,mode}]},
     setup: {scenario, side, sideAuto, zoneId, counterBiasReason, c4, c4num, c5, c6, c7:{dma, moveSize, deep}, b1, b2, b3,
             calc:{entry, sl, tp, tpSuggested}, slPos, updatedAt},
     open: {status:'pending'|'filled', side, scenario, zoneId, entryPlanned, entry, sl, tp, rrPlanned, size,
            beAt, beDone, outsideZoneBar, openedAt} | null,
     trades:[{time, side, scenario, mode, zoneId, zoneType, tests:{b1,c4,c4num,b2,b3,c5}, entry, sl, tp, size,
              slDist, slPos, rrPlanned, exit:{kind, price, reason}, r, flags:['rule_break','counter_bias','paper','half'],
              counterBiasReason, ruleCodes:[], sweptThenTP, notes}],
     tally:{machine, manual, closedAt} } } }
```

---

## 6. Kiểm thử (người implement phải chạy, báo kết quả thật)

**Đơn vị (node:test, `npm test`)** — tối thiểu:
- Ma trận bias: 14 ca (7 hàng, ghi đè, CHỜ rồi chốt lại trên/dưới).
- Bật kịch bản: bias (CHỜ, KHÔNG, BUY) × chế độ hiệu lực (`balanced`, `pending`, `broken`, `thin`) × giờ (20:29 / 20:31 hè; 21:29 / 21:31 đông) × acceptance (đủ / thiếu bước 2 / phá 18:30) — ≥ 24 ca, mỗi ca kiểm `enabled` **và mã** `DIS_*`. Riêng: bước 1 có + bước 2 chưa + C tại cạnh đó ⇒ `DIS_PENDING_ACCEPT`; C tại cạnh khác ⇒ bật; thẻ không có vùng `edge` ⇒ `DIS_NO_EDGE`.
- Phán quyết, một mã mỗi ca: `NO_NEWS_WINDOW` (19:30 ±15′ khi bật; 21:00 ±5′) · **20:25 và 20:34 không bị chặn** (chỉ cảnh báo) · `DIS_LONGEST_BAR` tới phút tròn + 3 rồi hết · `NO_COUNTER_BIAS_SCENARIO` (A, C, D) · B ngược bias tại VWAP tuần (không cờ) ⇒ NO; **B sell ngược bias BUY tại High hôm qua cờ `tail`** ⇒ ENTRY 2R ½ với lý do đã ghi; cờ `sp` sai phía ⇒ NO · `NO_ZONE_3RD` · `NO_BANNED_ZONE` (HVN ngày, LVN, HVN 3 tuần với B) · `NO_MID_RANGE` · `NO_FIGHT_BREAK` (B ngược chiều phá tại hạng 2 trong `broken`) · B ngược chiều phá tại VWAP tuần cùng chiều bias ⇒ qua (QĐ-4) · `NO_BUBBLE_AGAINST` (còn giữ; B với "đã vỡ") · B "không có" ⇒ CHỜ · `NO_UNCLEAR` từ C4, B1, B2, B3 · `NO_BACK` · C5 hơn 1 ⇒ CHỜ · `NO_MOMENTUM` · B lẫn lộn ⇒ CHỜ · `NO_DMA_SLOPE` · `NO_D_NO_MOVE` (4,9 giá) · `NO_D_DEEP` · `NO_SL_POS` · `NO_SL_FLOOR` · `NO_SL_CAP` · `NO_RR` · `NO_SL_SIDE` · `NO_TP_PAST_ZONE` · lệnh mở ⇒ tầng 3 khóa · CHỜ với `missing` đúng thứ tự · ENTRY đúng số, đúng cỡ (QĐ-8, QĐ-14).
- **Ca thật tái hiện** (số cố định, `t0.touched = true`, cửa sổ 19:30 tắt trừ khi ghi khác): **12/10 21:27** B1 = V, C4 = ngược còn giữ ⇒ NO, `reasons = [NO_BUBBLE_AGAINST, NO_V_PULLBACK]` · **6/10 20:24** A sell, `broken` xuống, cạnh vừa phá = cụm POC, bias SELL, U, B3 đạt, B5 đúng, vào 4193,0 · SL 4195,4 · TP 4185,0 · C6 = 2,0 ⇒ ENTRY, SL 2,4, R:R 1:3,3, **cỡ chuẩn** · **1/10 20:47** sell 4192,7 · SL 4194,8 · C6 = 3,3 ⇒ `NO_SL_FLOOR` · **13/10 20:10** B buy, `balanced`, vùng cụm POC trùng VAL Âu (≤ 1 giá), bias BUY, B2 giảm (−49 → −40), C4 cùng phe ⇒ ENTRY ½; biến thể `broken` xuống cùng vùng ⇒ `NO_FIGHT_BREAK` (ghi chú: plan chọn luật, không chọn ca) · **5/10 19:25** B với B2 lẫn lộn ⇒ CHỜ (QĐ-5).
- Ngắt mạch (QĐ-10, QĐ-17): 2 phá luật ⇒ OFF; "Tôi vẫn vào" ×2 ⇒ OFF; 3 SL liên tiếp ⇒ OFF; hòa và TP reset chuỗi; đóng tay "khác" ⇒ phá luật; "đóng sạch trước tin" ⇒ không; `paper` không cộng chuỗi, không cộng phá luật, không tính lần tại vùng; limit hủy không tính lần.
- Tầng 4: mốc be +1,5R / +1R đúng với SL lẻ 0,1; lệnh mở qua mốc đêm mới thuộc đêm cũ.
- Thời gian: `nightKey` tại 00:30, 04:59 (đêm cũ), 05:00, 10:00 (đêm mới) ngày hè; **05:30 ngày 02/11/2026 (đêm cũ, Globex chưa mở)**; mốc giờ tại 24/10, 25/10 (London), 31/10, 01/11/2026, 13/03, 14/03/2027; pha; cửa sổ ±15′ / ±5′; thứ Năm bật 19:30.
- Thẻ phiên: sửa Q6 trước 19:20 không vết, sau có vết; sửa khi đang canh kèo ⇒ cần xác nhận.
- Sổ: cộng R, lệch máy/tay, 4 con số tuần, Markdown đúng mẫu 7 cột (so chuỗi), cột Δ cho A/B/C/D.
- Store: migrate version, nhập JSON gộp không trùng.

**Đầu cuối (Playwright, `npm run e2e`)**: (1) đường đi đầy đủ tới ENTRY và ghi sổ cho **A và B**, đếm thao tác Canh/Bấm theo định nghĩa (A 5/5, B 7/6); (2) tầng 3 khóa khi chưa chốt thẻ / bias CHỜ / có lệnh; (3) chọn V ⇒ KHÔNG VÀO đỏ; (4) tải lại trang giữ nguyên; (5) mở bằng `file://` không lỗi console; (6) 360 px không tràn ngang; (7) phím tắt 1–4, U/V, Enter, tắt trong ô nhập; (8) "Tôi vẫn vào" ×2 ⇒ TẮT MÁY.

**Lint chữ (`npm run lint:vi`)**: quét `content.js` (trừ `criteria[]`): từ cấm, từ tiếng Anh ngoài danh sách 4.11, nhãn > 9 từ, dấu chấm thập phân trong chuỗi hiển thị.

Tiêu chí "xong" mỗi vòng: `npm test`, `npm run e2e`, `npm run lint:vi` xanh (dán kết quả thật vào `docs/IMPL-n.md`); ảnh 3 màn (tầng 1, tầng 3 ENTRY, điện thoại); deploy Pages mở được.

---

## 7. Quy trình thực hiện (theo yêu cầu người dùng)

**Giai đoạn P — plan**: bản này → agent **Fable** review (tối đa 3 vòng) → sửa.

**Giai đoạn I — tối đa 4 vòng**, mỗi vòng:
1. **Sonnet implement + test**; ghi `docs/IMPL-n.md` (làm gì, kết quả test thật, gì chưa xong).
2. Song song: **Opus review** (đúng luật từng ô so với HT và plan, mã, test, UX) → `docs/REVIEW-n.md`; **Sonnet "trader 1 tháng kinh nghiệm order flow / TPO"** dùng thử bằng Playwright + đọc, ghi `docs/USER-TEST-n.md`: làm được việc không, chỗ phải đoán, chữ khó, số thao tác tới ENTRY, có muốn dùng đêm mai không (điểm /5).
3. **Sonnet sửa** theo hai biên bản (ưu tiên: sai luật > chặn đường đi > UX > mã), chạy lại test.
Dừng sớm khi review không còn "sai luật" / "chặn đường đi" và người dùng thử chấm ≥ 4/5.

Sau mỗi vòng: commit tiếng Việt + `git push origin main` + deploy Pages + cập nhật `progress.md`.

---

## 8. Câu hỏi mở (đã chọn mặc định, người dùng đổi được sau)

| # | Câu hỏi | Mặc định |
|---|---|---|
| 1 | Mốc giờ của luật dịch +1h mùa đông? | Có (QĐ-7), có công tắc. |
| 2 | 20:30 có chặn không? | Chỉ cảnh báo (QĐ-6). |
| 3 | Cụm POC là hạng 2 cho B? | Có, cỡ ½, "chưa đo" (QĐ-3). |
| 4 | Câu trả lời tầng 3 tự xóa? | Không; nhắc sau 10′. |
| 5 | Máy tính cỡ lệnh bắt buộc? | Không, thu gọn mặc định. |
| 6 | Tên công cụ | "Trạm Đêm Vàng" (đổi trong `content.js`). |

## 9. Đối chiếu review 1 → bản 2 (giữ để tra)

1 bias KHÔNG/CHỜ → trục bias trong bảng bật · 2 ngược bias → QĐ-9 · 3 SL theo kịch bản → B5 · 4 B giữa range → QĐ-1 · 5 LVN → QĐ-2 · 6 chấm 2 → QĐ-3 · 7 cửa sổ 20:30 → QĐ-6 · 8 4.4 → C5 ba nút · 9 B lẫn lộn → QĐ-5 · 10 B bong bóng → C4 · 11 D 2R · 12 3–5 vùng · 13 giờ mùa đông → QĐ-7 · 14 acceptance 2 bước · 15 limit/hủy → tầng 4 · 16 lệnh mở gặp tin · 17 không sửa SL · 18 ba ca biên → QĐ-10, nút phá luật mọi phán quyết, qua đêm · 19 dữ liệu sổ · 20 Q2a/b · 21 IB · 22 QĐ-11 · 23 Canh/Bấm · 24 B3 của B · 25 vết trước 19:20 · 26 Kế hoạch 1/2 · 27 Bạn cộng · 28 khóa tầng 3 · 29 QĐ-8 · 30 phút tròn + 3 · 31 phím tắt · 32–34 chữ, ngày · 35 file:// · 36 thứ tự luật · 37 nightKey · 38 test · 39 lint.

## 10. Đối chiếu review 2 → bản 3

| Mục | Sửa ở bản 3 |
|---|---|
| 1 fade bật lại sau M5 đóng ngoài | Chế độ hiệu lực `pending` + `DIS_PENDING_ACCEPT`; nút "Chui lại trong"; test riêng. |
| 2 POC hôm qua = naked POC | Bỏ loại "POC hôm qua"; naked POC chỉ TP, A/D khi là cạnh vừa phá; cụm POC định nghĩa ≥ 2 POC ≤ 1 giá; QĐ-3 ghi "đã đo 46,5 %". |
| 3 poor high mang cờ tail | Tách hàng: `sp` chỉ single print (có phía); poor high/low không cờ; `tail` chỉ từ Q2 = tail thật. |
| 4 QĐ-9 không chạy được | Luật "B ngược bias miễn điều kiện hạng khi cờ tail/sp đúng phía"; B thêm vào hàng High/Low hôm qua; test ghi rõ vùng + cờ. |
| 5 cửa sổ 20:30 chặn ca 6/10 | QĐ-6: 20:30 chỉ cảnh báo; test 20:25, 20:34 không chặn; 21:00 ±5′ giữ. |
| 6 QĐ-4 rộng, C7b trùng | QĐ-4 thu hẹp (cùng chiều bias + hạng 1); bỏ C7b và `NO_B_IS_BREAK`; `NO_FIGHT_BREAK` suy từ chế độ + vùng + hướng. |
| 7 mã DISABLE | Bảng bật ghi mã `DIS_*` từng ô; `enabled:{A..D: code|null}`. |
| 8 ví dụ ENTRY | Ca 6/10 cùng chiều bias, cỡ chuẩn. |
| 9 nhãn dài | `criteria[]` dưới nút, lint bỏ qua; nhãn chính ≤ 9 từ. |
| 10 "không rõ" | C4, B2, B3 ⇒ `NO_UNCLEAR`; chấm 5 ghi rõ A/C/D vs B. |
| 11 ba quyết định thiếu mã | QĐ-12, QĐ-13 (`DIS_USE_D`), QĐ-14; test 6/10 "cỡ chuẩn". |
| 12 HVN ngày | Hàng HVN ngày + QĐ-15. |
| 13 TP vùng kế tiếp | QĐ-16, `NO_TP_PAST_ZONE`. |
| 14 cách đếm | QĐ-17 + 3 test. |
| 15 thao tác | Định nghĩa ở đầu; C2 tự điền A/C/D; D "move: __ giá"; số đếm A 5/5 · B 7/6 · C 5/4 · D 7/5; e2e đếm A và B. |
| 16 B5 checkbox, C6 cũ | B5 ba nút + `NO_SL_POS`; QĐ-18. |
| 17 QĐ-1 ca thường gặp | `DIS_NO_EDGE`; mép gần nhất; mọi hạng 1–2 trùng cạnh. |
| 18 dữ liệu | `tests.b3`, cột Δ; `size`, `counterBiasReason`, `slPos`; `windows` có `rank`, `minutesBefore/After`, `tz`. |
| 19 múi gốc | Mốc mang `ET` / `LONDON` / `VN`; `nightKey` theo Globex mở; test 05:30 ngày 02/11. |
| 20 test mơ hồ | Thứ tự mã 12/10 ghi rõ; `t0.touched`; test CommonJS `.test.js`. |
| 21 từ Anh | Danh sách bổ sung + bảng thay chữ Việt. |
| 22 câu chữ | Ma trận bias tách hàng; C5 "hơn 1, chưa tới 3" / "từ 3"; "Thu gọn được"; đánh số lại mục 8–10. |
