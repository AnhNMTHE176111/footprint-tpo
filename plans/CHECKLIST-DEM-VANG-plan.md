# Plan — "Trạm Đêm Vàng": công cụ checklist chạy theo Hệ thống Đêm Vàng

Bản 4 (chốt) · 2026-10-20 · tác giả: Claude (Fable 5.1) · người dùng: người học (trader vàng GC/MGC phiên Mỹ)
Lịch sử: bản 1 → review 1 (39 mục) → bản 2 → review 2 (22 mục) → bản 3 → review 3 (18 mục) → bản 4. Mục 9–11 cuối file ghi từng mục đã sửa thế nào. Phụ lục A là fixtures cho 5 ca test.

> Mục tiêu một câu: một trang web tĩnh mở lúc 18:00, dẫn người dùng đi đúng thứ tự của hệ thống
> (kẻ vùng → bias → chế độ → kịch bản → SL → ghi sổ), **khóa tầng dưới khi tầng trên chưa xong**,
> và bật chữ **ENTRY** to rõ đúng lúc đủ điều kiện — để sau 20 phiên, hệ thống thành phản xạ.

Quy ước: **HT** = `daily-trading/HE-THONG-DEM-VANG.html` v1.2 (trích theo số mục); **ST** = `so-tay-vang-mgc.html`; **RULES** = `daily-trading/RULES.md`. Chính tả theo HT: *hòa, khóa, tắt máy*. **Thao tác** = 1 click hoặc 1 ô số bắt buộc; ô tùy chọn, hộp lý do, giá trị tự điền và giá trị gợi ý sẵn không tính.

---

## 0. Nguồn, thứ tự ưu tiên và các quyết định về chỗ nguồn mâu thuẫn

| Nguồn | Vai trò |
|---|---|
| HT (16/10/2026) | **Nguồn luật chính.** Mọi câu chữ checklist lấy từ đây. |
| ST (8/2026) | Cơ chế phụ: nhịp buổi tối, 4 chart, lịch tin + khung giờ cấm, giờ mùa đông Mỹ, máy tính cỡ lệnh MGC, hủy kịch bản, settlement, Globex bảo trì. |
| RULES (29/9, bổ sung 15/10) | Không nhồi lệnh (1 lệnh mở); chưa be thì không sờ SL; đóng tay phải có lý do có tên. |
| REVIEW 15/10 + nhật ký | "Vì sao có luật này" trong trợ giúp "?" của từng ô. |

**HT thắng ST** khi mâu thuẫn: R:R sàn 1:2 (mục tiêu 3R cho A, B; 2R cho C, D) · ngắt mạch = 2 lệnh phá luật hoặc 3 SL liên tiếp · 4 bài kiểm tra cơ chế thay X1–X4 · checklist 8 câu · Optimus Flow thời gian thực (bỏ "chế độ lệnh chờ" của ST).

**Quyết định của plan (QĐ-n; hiện trong trợ giúp "?" kèm "quyết định của công cụ, chưa đo" khi HT không nói)**

| Mã | Vấn đề | Quyết định |
|---|---|---|
| QĐ-1 | B tại VWAP giữa range khi Cân bằng (HT 5·B vs HT 3). | Cân bằng ⇒ B chỉ tại **vùng cờ `edge`** (VAH/VAL Âu, cạnh range, IB), hoặc **vùng hạng 1–2 trùng cạnh** (mép gần nhất cách mép một vùng `edge` ≤ 1 giá). Thẻ không có vùng `edge` ⇒ B và C `DIS_NO_EDGE`. VWAP giữa range ⇒ `NO_MID_RANGE`. High/Low hôm qua là `edgeOuter`, không phải `edge` (B tại đó chỉ theo QĐ-9). |
| QĐ-2 | LVN: vùng kẻ hay vùng cấm? | LVN **cấm fade** (`banned`: B chặn; A, D theo chiều được). Ca 13/10: vùng để bám là POC, LVN chỉ nói giá đi nhanh. |
| QĐ-3 | Câu 2 checklist "hạng 1–2 hoặc cạnh VA Âu khi cân bằng" vs ca 6/10 (A tại cụm POC), 13/10 (B tại POC). | Câu 2 = "giá ở **vùng trong thẻ**, ≤ 1 giá". **Riêng B** vùng phải: hạng 1 (VWAP tuần) · hạng 2 (VWAP ngày, HVN tuần — đã đo; **cụm POC** = ≥ 2 POC cách nhau ≤ 1 giá — chưa đo, HT 13/10 ghi "POC hôm qua", chưa rõ là cụm; cỡ ½) · cạnh theo QĐ-1 · hoặc QĐ-9. Không đạt ⇒ `NO_B_RANK`. **POC phiên trước chưa chạm = naked POC: đã đo 46,5 % ⇒ chỉ mục tiêu.** |
| QĐ-4 | "Không cản tàu" ở `broken`: B ngược chiều phá? | B cùng chiều phá: được. B ngược chiều phá **chỉ khi cùng chiều bias, vùng hạng 1 (VWAP tuần), vùng ≠ cạnh vừa phá**; còn lại ⇒ `NO_FIGHT_BREAK`. Engine suy, không hỏi. |
| QĐ-5 | HT 4.2 luật cứng vs ca 5/10 "delta lẫn lộn". | B cần "giảm dần"; "lẫn lộn" ⇒ CHỜ; "tăng dần" ⇒ `NO_MOMENTUM`. Ca 5/10 là ngoại lệ chưa đo. |
| QĐ-6 | Khung giờ cấm (HT 7 không cho độ rộng; HT 3.2 cú phá đáng tin 20:20–21:30). | 19:30 ±15′ ⇒ `NO_NEWS_WINDOW` (hạng 1). 21:00 ±5′ ⇒ `NO_NEWS_WINDOW` (hạng 2). **20:30 ±5′: chỉ cảnh báo** vàng "NYSE mở — không đánh tin". Mùa đông +1h. |
| QĐ-7 | Mốc giờ của luật có dịch theo giờ mùa đông? | **Có.** Mỗi mốc mang múi gốc `ET` / `LONDON` / `VN`. London đổi 25/10/2026 và trở lại 28/03/2027; Mỹ 01/11/2026 và 14/03/2027. Ngày 01/11 hiện thẻ "đổi neo session TPO / SessionZones 19:20 → 20:20, IB = 20:20–21:20". Công tắc `settings.dstShift`. |
| QĐ-8 | "Cỡ nhỏ", "cỡ một nửa". | ½ cỡ chuẩn, **áp một lần**; `half.reasons[]` ghi mọi lý do nhưng chỉ nhân ½ một lần. |
| QĐ-9 | Ngược bias (HT 2.2 chỉ cho hấp thụ tại đỉnh có tail thật / single print, cỡ nhỏ, 2R). | Ngược bias ⇒ A, C, D: `NO_COUNTER_BIAS_SCENARIO`. **B miễn `NO_B_RANK`** khi vùng mang cờ `tail` (High/Low hôm qua với Q2 = tail thật) hoặc `sp` **đúng phía** (sell ⇒ cờ phía trên; buy ⇒ phía dưới); không cờ hoặc sai phía ⇒ `NO_COUNTER_BIAS_ZONE`. TP ép 2R, cỡ ½, lý do bắt buộc. ENTRY in "ngược bias · 2R · ½". |
| QĐ-10 | Chuỗi SL: hòa có reset? | Lệnh R ≤ −0,2 (hoặc kind SL chưa be) cộng chuỗi; R trong (−0,2; +0,2) là hòa, R ≥ +0,2 là thắng, cả hai reset về 0 (ngưỡng ±0,2R là quyết định của công cụ, chưa đo). Chuỗi SL, đếm phá luật, TẮT MÁY, lần tại vùng đều tính **trong một `nightKey`**; đêm mới về 0. |
| QĐ-11 | Hình "B" trong mẫu thẻ phiên. | Giữ; trợ giúp "B = hai phân phối — HT không định nghĩa". |
| QĐ-12 | Trên VWAP tuần nhưng Q1 = b (hoặc dưới và P). | Bias **KHÔNG** (chưa đo). |
| QĐ-13 | Trend thin: B có được không? | B tắt `DIS_USE_D`: chữ "Trend thin: cùng chiều ở nhịp hồi ⇒ dùng D; ngược chiều = cản tàu". C tắt `DIS_THIN_NO_FADE`. |
| QĐ-14 | Cỡ ½ cho hạng 2 áp cho ai? | **Chỉ B.** A, D tại hạng 2 cỡ chuẩn. |
| QĐ-15 | HVN ngày thường. | Cờ `noB` (B chặn `NO_BANNED_ZONE`; A, D được); không vào "VÙNG CẤM" của thẻ (thẻ chỉ gom `banned`). |
| QĐ-16 | TP vs vùng kế tiếp (HT 6). | TP gợi ý = gần hơn giữa R mục tiêu (3R A, B; 2R C, D; **2R cho B ngược bias**) và vùng kế tiếp theo hướng lệnh trong thẻ. TP vượt vùng kế tiếp quá 0,5 giá ⇒ `NO_TP_PAST_ZONE`; vùng kế tiếp cho R:R < 1:2 ⇒ `NO_RR`. |
| QĐ-17 | Cách đếm. | n = số dòng `trades` trong đêm cùng `zoneId`, đã khớp, **kể cả** phá luật, **không kể** `paper` và dòng đã hủy. Hiện "lần thứ n+1"; `NO_ZONE_3RD` khi n ≥ 2. `paper` đi đúng đường tầng 4 như lệnh thật (để có R), chip "lệnh mở (luyện mắt)", không cộng chuỗi SL, phá luật, lần tại vùng. |
| QĐ-18 | C6 nhập lúc Canh. | Giữ ở Canh; bước Bấm hiện lại với ô sửa tại chỗ. |
| QĐ-20 | (sau REVIEW-1) Cỡ lệnh ra 0 hợp đồng; vùng kế tiếp cho TP. | 0 hợp đồng ⇒ `NO_SIZE_ZERO` (ST §6 "không đủ 1 hợp đồng = bỏ kèo"); thanh ENTRY in số hợp đồng. "Vùng kế tiếp" (QĐ-16) bỏ qua vùng cùng cụm với vùng vào (cách ≤ 1 giá) và bỏ qua LVN (giá đi nhanh qua). Mọi luật `NO_*` luôn được xét để `ruleCodes` đủ; thanh phán quyết chỉ hiện 2 mã đầu. Fixture A2 kỳ vọng `[NO_BUBBLE_AGAINST, NO_V_PULLBACK, NO_RR, NO_TP_PAST_ZONE]`; A3a `[NO_SL_FLOOR, NO_TP_PAST_ZONE]`; A3b `[NO_SL_POS, NO_SL_FLOOR, NO_TP_PAST_ZONE]`. |
| QĐ-21 | (sau IMPL-2) Cỡ ½ làm tròn xuống ra 0 khi cỡ chuẩn chỉ 1 hợp đồng. | `NO_SIZE_ZERO` chỉ khi **cỡ chuẩn** < 1 hợp đồng. Khi cỡ chuẩn ≥ 1 mà ½ < 1 ⇒ size = 1 kèm chữ "cỡ ½ không chia được — 1 hợp đồng (tối thiểu)". Lần mở đầu tiên hỏi vốn và % rủi ro (mặc định 2 000 $, 2 %), đổi được ở cài đặt. Mã `NO_BIAS_NONE_EDGE` (bias KHÔNG chỉ fade VAH/VAL Âu, htRef 2.2) được công nhận. |
| QĐ-22 | (người học yêu cầu 20/10) Khung giờ cấm phải **tự lấy từ lịch Forex Factory** và tự cập nhật, không nhập tay. Feed `https://nfs.faireconomy.media/ff_calendar_thisweek.json` (+ `_nextweek`) không có CORS và chặn gọi dày (429). | **Nguồn:** GitHub Actions trong repo Pages `tram-dem-vang` chạy mỗi 15′ (cron) + chạy tay, tải 2 feed, giữ bản cũ nếu 429, ghi `data/ff.json` (gộp, kèm `fetchedAt`) và commit. **App** đọc `./data/ff.json` (cùng origin) lúc mở và mỗi 5′, chống cache bằng tham số thời gian; hiện "lịch tin cập nhật lúc hh:mm". **Luật chuyển tin → khung giờ cấm:** USD tác động High ⇒ hạng 1 ±15′ (KHÔNG VÀO); USD Medium ⇒ hạng 2 ±5′; EUR/GBP High ⇒ chỉ cảnh báo vàng; FOMC Statement / Press Conference / Fed Chair ⇒ hạng 1 + "đóng sạch trước giờ − 15′"; có NFP / CPI / Core CPI / FOMC trong đêm ⇒ `newsDay` tự bật (cỡ ½). Tin "Tentative"/"All Day" bỏ qua, ghi chú. **Có lịch thì chỉ tin thật tạo khung giờ cấm**: không còn 19:30, 21:00 mặc định và cảnh báo NYSE 20:30 (sửa 20/10 theo người học: "hôm nay không có tin đỏ sao vẫn báo 19:30, 20:30"); các mốc mặc định chỉ dùng khi không tải được lịch. Mở file local thì tải lịch từ Pages (CORS *). Người dùng vẫn tắt từng dòng (ghi lại giờ), vẫn thêm tay. **Hiển thị:** bảng "Tin tối nay" (giờ VN, tên, tác động, dự báo / kỳ trước / thực tế — thực tế cập nhật theo feed), đếm ngược tới tin kế ở thanh trạng thái. **Dự phòng:** không tải được hoặc `fetchedAt` cũ hơn 2 giờ ⇒ thanh đỏ "lịch tin chưa cập nhật — tự kiểm ForexFactory" và dùng mặc định cũ (19:30 thứ Năm, 21:00). Giờ feed có múi (ISO offset) ⇒ đổi sang VN; không dùng mùa đông/hè thủ công cho tin. Độ trễ "thực tế" tối đa ≈ 15′ do cron. |
| QĐ-23 | (người học yêu cầu 20/10) Tầng 0 và tầng 1 quá nhiều lựa chọn. | **Tầng 0** chỉ còn: "Tỉnh táo?" · danh sách "Tin tối nay" tự lấy từ lịch (QĐ-22, mỗi tin một công tắc) · ô kịch bản nền; thêm tay gập dưới "Thêm tay…"; `newsDay` tự suy. **Tầng 1** chỉ hỏi 3 thứ engine dùng: hình profile hôm qua (Q1) · giá đóng hôm qua vs VA (Q5) · giá vs VWAP tuần (2 ô số, tự suy); bỏ Q1′, Q2, Q3, Q4, Q6 khỏi màn hình: Q6 suy từ thẻ có vùng `edge`; nợ suy từ vùng single print / poor; cờ `tail` hỏi một ô nhỏ khi thêm vùng High/Low hôm qua. Danh sách 7 ô "đã kẻ" thành một dòng gợi ý. Kế hoạch 1/2/Hủy khi gộp thành một ô ghi chú tùy chọn, gập. Thẻ phiên ẩn dòng trống. Từ điển và hộp "?" có thanh cuộn mảnh, thẻ từ có đệm; chip trạng thái chỉ dùng màu khi cảnh báo. |
| QĐ-24 | (người học yêu cầu 20/10) Tầng 2 thừa: "Giờ phá", "lần mấy", dải giờ. | `breakout.at` = giờ lúc bấm "Vừa phá", không hiện, không sửa. Bỏ `nth` khỏi màn hình (chỉ còn dòng nhắc sau "Chui lại trong"). Bỏ dải giờ ở tầng 2 (có ở thanh trạng thái). Tầng 2 = 3 nút chế độ; Vừa phá thêm hướng · cạnh vừa phá · 2 công tắc acceptance; Trend thin thêm hướng; một nút "nến dài nhất". |
| QĐ-25 | (người học yêu cầu 20/10) M1 rất nhanh; bước Bấm phải cực gọn. | Bước Bấm ≤ 3 thao tác: nến xác nhận đạt? · giá vào · SL (TP tự gợi ý; Enter = vào lệnh). B1 (U/V) và B2 (thân + \|delta\|) chuyển sang bước Canh (nhìn được trên nhịp hồi trước khi nến đóng). B5 tự kiểm: A, C so SL với mép xa vùng/cạnh + 0,3 (vế "sau râu nến xác nhận" không kiểm bằng máy — ghi vào tiêu chí của B3 để người dùng tự nhìn; chấp nhận để giữ 3 thao tác); B, D hỏi một ô số "cực trị cụm / đỉnh hồi" ở Canh rồi máy tự so. Một màn, không tab: Canh gập thành dòng tóm tắt khi đủ, Bấm luôn hiện. "Kèo mới" giữ C1–C3, C6. |
| QĐ-19 | **Trước 20:30**: HT 3.2 / 5·C "chỉ fade cạnh" vs HT 0 "ba lệnh +3R tốt nhất" có 13/10 20:10 (B) và 6/10 20:24 (A). | **Không tắt A/B/D.** Thay bằng cảnh báo vàng "trước 20:30 — mở ảo (HT 3.2)" + **cỡ ½** cho A, B, D (`half.reasons` += `BEFORE_2030`). Mùa đông 21:30. Chưa đo. |

**Nguyên tắc mã:** `DIS_*` chỉ phụ thuộc (bias, chế độ, giờ, thẻ, khóa 3′) — tính được ở tầng 2 không cần vùng/hướng. Mọi luật cần vùng, hướng hay câu trả lời tầng 3 là `NO_*`. Mỗi mã có `htRef` (ví dụ `NO_V_PULLBACK → "4.1"`) để dòng ⚠ trong sổ in "phạm 4.1, 4.3 và luật SL" đúng mẫu HT 8.

---

## 1. Người dùng, bối cảnh dùng, mục tiêu

- Một người dùng, đi làm ban ngày, trade 18:00 → 00:30 giờ VN, màn chính là Optimus Flow; công cụ mở ở màn phụ hoặc nửa màn, **chuột là chính**, bàn phím khi quen.
- Ban ngày liếc điện thoại (thẻ phiên, sổ). Tối ưu cho máy tính, dùng được trên điện thoại.
- Dùng **hằng đêm, 20 phiên** → ít chữ, nhớ trạng thái, **mỗi sự thật chỉ hỏi một lần**.
- Mục tiêu đo được (HT 10): sau 20 phiên có **nhật ký 7 cột đầy đủ**.

**Không làm (v1):** không đọc dữ liệu từ Optimus Flow, không tự nhận diện chart, không đồng bộ đám mây, không nhiều người dùng, không tiếng Anh.

---

## 2. Hình thức: trang web tĩnh, cài được như ứng dụng, mở được bằng file://

- HTML/CSS/JS thuần, **không framework, không bước build, không `type="module"`**. Deploy GitHub Pages ở repo công khai mới `AnhNMTHE176111/tram-dem-vang` → `https://anhnmthe176111.github.io/tram-dem-vang/`.
- **PWA** (chỉ qua Pages): manifest + service worker để "Cài đặt" thành khung giờ riêng và chạy không mạng. Mở `file://` thì không có service worker, mọi tính năng khác vẫn chạy.
- **Dữ liệu ở máy**: `localStorage`; xuất / nhập JSON, xuất Markdown; nhắc xuất file cuối tuần.
- Mã nguồn trong repo `footprint-tpo` tại `tram-dem-vang/`; `deploy.sh` sao chép sang clone repo Pages rồi push.

---

## 3. Kiến trúc thông tin: 6 tầng, tầng dưới khóa khi tầng trên chưa xong

```
 ┌ Thanh trạng thái (luôn thấy) ────────────────────────────────────────────────────────┐
 │ 20:14 VN · NYSE sắp mở · khung giờ cấm kế: 21:00 (46′) · BIAS SELL · phá luật 0/2 · SL liên tiếp 1/3 · lệnh mở 0/1 │
 └──────────────────────────────────────────────────────────────────────────────────────┘
 [0 Trước] → [1 Vùng] → [2 Chế độ] → [3 Kèo: Canh | Bấm] → [4 Lệnh] → [5 Sổ]
 ┌ Nội dung tầng ────────────────────────────────┐ ┌ Thẻ phiên (cột phải, cố định) ─┐
 │ checklist của tầng đang mở                    │ │ bias · vùng · nợ · cấm · kế hoạch │
 └───────────────────────────────────────────────┘ └────────────────────────────────┘
 ┌ Thanh phán quyết (dính đáy, tầng 3) ─────────────────────────────────────────────────┐
 │ ●●●●○○○○  CHỜ — thiếu: nến xác nhận · SL     |  ENTRY SELL 4193,0 · SL 4195,4 (2,4) · TP 4185,0 · 1:3,3 · cỡ ½ │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

Khóa tầng: **1**, **2**, **5** luôn mở · **3** mở khi thẻ đã chốt **và** bias ≠ CHỜ **và** không có lệnh · **4** mở khi có lệnh (chờ khớp hoặc đã khớp, kể cả luyện mắt). Có lệnh ⇒ tầng 3 khóa hẳn, giao diện nhảy sang tầng 4 (RULES A.3).

### Tầng 0 · Trước khi mở chart (18:00)
| # | Ô | Kiểu | Hệ quả |
|---|---|---|---|
| 0.1 | Tỉnh táo, không bực dọc, không mệt rã rời | có / không | Không ⇒ cả đêm **CHỈ XEM**: ENTRY hiện xám "ENTRY (chỉ xem)", nút "Ghi kèo luyện mắt" ⇒ tầng 4 như lệnh thật, cờ `paper` (QĐ-17). |
| 0.2 | Khung giờ cấm tối nay | danh sách, bật/tắt từng dòng; thêm dòng tùy chỉnh (giờ · hạng 1/2 · phút trước/sau) | Mặc định: **21:00 ±5′** bật; **19:30 ±15′** bật vào **thứ Năm** và khi `t0.touched = false`; **20:30 ±5′** là dòng cảnh báo, không tắt được (QĐ-6). FOMC: 01:00/01:30, nhắc đóng sạch trước 00:45. Tắt một dòng ⇒ xác nhận + vết "tắt khung giờ 19:30 lúc hh:mm". Ngày NFP/CPI ⇒ `half.reasons` += `NEWS_DAY`. Mùa đông +1h. |
| 0.3 | Kịch bản nền ban ngày (1 dòng, tùy chọn) | chữ | Hiện lại ở thẻ phiên. |

### Tầng 1 · Kẻ vùng trên chart A và chốt thẻ phiên (18:30–19:20; mùa đông 19:30–20:20)
**1a. Kẻ trên chart** (tick khi đã kẻ xong): 1 Chart A: TPO ngày neo pit COMEX (19:20; mùa đông 20:20) + TPO gộp 3 tuần · 2 Năm mức hôm qua High · VAH · POC · VAL · Low · 3 VWAP tuần, VWAP ngày · 4 HVN / LVN ngày và 3 tuần · 5 Nợ: single print, poor high / low · 6 Naked POC · 7 VAH Âu, VAL Âu; IB high / low khi đã có.

**1b. Sáu câu hỏi** (chọn một; "?" mở đúng Q của HT):

| Q | Câu | Đáp án |
|---|---|---|
| Q1 | Hình dạng profile hôm qua | D · P · b · B · thin · chữ nhật |
| Q1′ | Hình dạng 3 tuần | như trên |
| Q2a | **Đỉnh** hôm qua | tail thật (1 TPO, volume thấp) · mồi (volume dày) · poor high · bình thường |
| Q2b | **Đáy** hôm qua | tail thật · mồi · poor low · bình thường |
| Q3 | Nợ chưa lấp | phía trên · phía dưới · cả hai · không |
| Q4 | Giá hiện tại đang ở | LVN · HVN · giữa |
| Q5 | Giá đóng hôm qua so với VA hôm qua | trên · trong · dưới |
| Q6 | Âu đã dựng range chưa | rồi · chưa |

**1c. Bias** — ô *Giá hiện tại so với VWAP tuần*: trên · dưới · sát (±2 giá). Ma trận (HT 2.2 + QĐ-12):

| VWAP tuần | Q5 | Q1 | ⇒ Bias | Được làm gì |
|---|---|---|---|---|
| trên | trên hoặc trong | ≠ b | **BUY** | A buy · B (hấp thụ sell) · C fade đáy VA Âu. Sell chỉ theo QĐ-9. |
| dưới | dưới hoặc trong | ≠ P | **SELL** | gương ngược |
| trên | dưới | — | **KHÔNG** | chỉ C hai cạnh VA Âu, 2R, cỡ ½ |
| dưới | trên | — | **KHÔNG** | như trên |
| trên | bất kỳ | b | **KHÔNG** | QĐ-12 |
| dưới | bất kỳ | P | **KHÔNG** | QĐ-12 |
| sát | bất kỳ | — | **CHỜ** | tầng 3 khóa; "Chốt lại bias" khi xác nhận "đã có 1 nến M5 đóng rõ: trên / dưới" ⇒ tính lại với `vwapW` mới |

Bias tự động; **ghi đè** được với lý do bắt buộc (cờ "bias ghi đè").

**1d. Vùng (3–5; < 3 vẫn chốt, cảnh báo vàng + vết)** — mỗi vùng: loại · giá (số hoặc khoảng; khoảng cách đo bằng mép gần nhất) · phía (bắt buộc với single print và cạnh range: trên / dưới) · ghi chú. Hạng, vai, cờ tự suy:

| Loại | Hạng / vai | Kịch bản hợp lệ | Cờ |
|---|---|---|---|
| VWAP tuần | hạng 1 | B, A, D | `r1` |
| VWAP ngày · HVN tuần | hạng 2 (đã đo) | B (½), A, D | `r2` |
| cụm POC (≥ 2 POC cách ≤ 1 giá) | hạng 2 (chưa đo) | B (½), A, D | `r2` |
| VAH Âu · VAL Âu · cạnh range (có phía) · IB high · IB low | cạnh | C; B khi `balanced`; A khi là cạnh vừa phá | `edge` |
| High hôm qua · Low hôm qua | cạnh ngoài | C, A, D; B chỉ QĐ-9 | `edgeOuter`; `tail` nếu Q2a/Q2b = tail thật |
| single print (có phía) | nợ, mục tiêu ưa thích | TP; B ngược bias QĐ-9 | `sp` |
| poor high / poor low | nợ, mục tiêu | TP | |
| naked POC | **chỉ mục tiêu** (đã đo) | TP; A, D khi là cạnh vừa phá | |
| HVN ngày | trung tính (QĐ-15) | A, D; B chặn | `noB` |
| HVN 3 tuần · LVN | **cấm fade** (QĐ-2) | A, D theo chiều; B chặn | `banned` |

**1e. Thẻ phiên** (cột phải) tự điền từ 1b–1d đúng mẫu HT 8: NGÀY · VWAP tuần · Đóng hôm qua · Hình hôm qua · BIAS · VÙNG · NỢ · VÙNG CẤM (gom `banned`). Ba ô người dùng gõ (tùy chọn): **Kế hoạch 1**, **Kế hoạch 2** ("nếu … thì …"), **Hủy kế hoạch khi …**. Nút **"Chốt thẻ phiên"**: cần Q1, Q5, Q6, VWAP tuần, ≥ 1 vùng. Sau chốt vẫn sửa: trước 19:20 (mùa đông 20:20) sửa Q6 / VA Âu / IB không vết; sau đó mỗi lần sửa ghi lại giờ sửa; đang có kèo tầng 3 ⇒ xác nhận "đang canh kèo — sửa thẻ lúc này là nắn kế hoạch". Chưa chốt ⇒ tầng 3 khóa: "Không có thẻ phiên thì không có lệnh."

### Tầng 2 · Chế độ thị trường (chart B, M30/M5)
- Chọn **chế độ**: Cân bằng · Vừa phá · Trend thin (bắt buộc chọn **hướng trend** `thinDir`). Mỗi lần đổi ghi `regime.log`.
- *Vừa phá*: hướng phá · **cạnh vừa phá** (`edgeZoneId`, chọn từ thẻ) · giờ phá (mặc định "bây giờ") · lần mấy (`nth`, chỉ hiển thị và nhắc "lần 1 chui lại ⇒ không đuổi, chờ lần 2" — HT 3.2) · bước 1 "có 1 nến M5 đóng ngoài cạnh" · bước 2 "nhịp hồi về cạnh giữ được, không nến M5 đóng ngược vào trong". Nút "Chui lại trong (phá hụt)" ⇒ về Cân bằng, `nth` kế = 2.
- **Chế độ đang áp dụng** `regime.effective`: `balanced` · `pending` (bước 1 có, bước 2 chưa: "chờ công nhận") · `broken` · `thin`. `regimeDir` = `breakout.dir` (broken/pending) hoặc `thinDir` (thin).
- **Bảng bật kịch bản** — **duyệt mọi hàng từ trên xuống; ô "bật" nghĩa là hàng này không tắt, xét tiếp; mã đầu tiên tắt là mã hiển thị trên thẻ.** Thứ tự khớp mục 5.

| Hàng | A Phá hồi | B Hấp thụ | C Fade cạnh | D Trap |
|---|---|---|---|---|
| Khóa 3′ sau nến dài nhất | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` | `DIS_LONGEST_BAR` |
| Thẻ chưa chốt | `DIS_NO_CARD` | `DIS_NO_CARD` | `DIS_NO_CARD` | `DIS_NO_CARD` |
| Bias CHỜ | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` | `DIS_BIAS_WAIT` |
| Bias KHÔNG | `DIS_BIAS_NONE` | `DIS_BIAS_NONE` | bật | `DIS_BIAS_NONE` |
| Thẻ không có vùng `edge` | bật | `DIS_NO_EDGE` | `DIS_NO_EDGE` | bật |
| `balanced` | `DIS_NOT_BROKEN` | bật (tại cạnh, QĐ-1) | bật | `DIS_NO_MOVE` |
| `pending` | `DIS_PENDING_ACCEPT` | bật ("trừ cạnh vừa phá") | bật ("trừ cạnh vừa phá") | `DIS_NO_MOVE` |
| `broken` | bật | bật | `DIS_M5_OUTSIDE` | bật |
| `thin` | bật | `DIS_USE_D` | `DIS_THIN_NO_FADE` | bật |
| `broken` / `thin` mà `regimeDir` ngược bias | `DIS_BREAK_AGAINST_BIAS` | bật (QĐ-4 / QĐ-9 xét ở tầng 3) | — | `DIS_BREAK_AGAINST_BIAS` |
| Trước 20:30 (mùa đông 21:30) | bật, ½ (QĐ-19) | bật, ½ | bật, ½ | bật, ½ |

- Nút **"Vừa có nến dài nhất phiên"** ⇒ `longestBarUntil` = phút tròn kế tiếp + 3′; hiện "mở lại 21:21"; sau đó nhắc "chờ hồi; không hồi thì bỏ".
- Dải giờ (HT 3.2) hiện một nhãn: 18:00–19:20 "phá giả" · 19:20–20:20 "mở ảo" · 20:20–21:30 "cú phá đáng tin" (mùa đông +1h).

### Tầng 3 · Kèo trên M1 — **Canh** rồi **Bấm**, phán quyết sống
**Mỗi sự thật một điều khiển**, 3 trạng thái (tốt / xấu / không rõ; chưa chạm ⇒ CHỜ). Thứ suy được thì không hỏi.

**3a. Canh — trước khi nến xác nhận đóng** (thao tác: A 4 khi `broken` / 5 khi `thin` · B 7 · C 5 · D 7)

| # | Điều khiển | Lựa chọn | Hệ quả |
|---|---|---|---|
| C1 | Kịch bản | A · B · C · D (chỉ thẻ đang bật) | |
| C3 | Vùng | A khi `broken`: **tự điền = `edgeZoneId`, không sửa**; A khi `thin`, B, C, D: chọn từ thẻ | hiện hạng, cờ, "lần thứ n+1" (QĐ-17; n ≥ 2 ⇒ `NO_ZONE_3RD`); B tại `noB`/`banned` ⇒ `NO_BANNED_ZONE`; `balanced` và vùng không đạt QĐ-1 ⇒ `NO_MID_RANGE`; `pending` và vùng = cạnh vừa phá (B, C) ⇒ `NO_PENDING_ACCEPT`; B không đạt hạng QĐ-3 ⇒ `NO_B_RANK`; cản tàu ⇒ `NO_FIGHT_BREAK` |
| C2 | Hướng | **Khóa, tự điền** cho A (= `regimeDir`), D (= `regimeDir`), C (= theo phía cạnh: VAH / High / IB high / cạnh range phía trên ⇒ sell; ngược lại buy; điền sau C3). **B: người dùng chọn** buy · sell | ngược bias ⇒ QĐ-9 (hộp "Lý do ngược bias", không tính thao tác); A, C, D ngược bias chỉ xảy ra khi bias ghi đè… ⇒ `NO_COUNTER_BIAS_SCENARIO` |
| C4 | 4.3 Bong bóng to gần nhất (10 nến, ở cực trị) | cùng phe · ngược phe còn giữ (vòng trắng) · ngược phe đã vỡ (mờ) · không có / ở giữa move · không rõ — ô số tùy chọn "±___" | ngược còn giữ ⇒ `NO_BUBBLE_AGAINST`; không rõ ⇒ `NO_UNCLEAR`. **B**: cần cùng phe; không có ⇒ CHỜ; đã vỡ ⇒ `NO_BUBBLE_AGAINST`. A, C, D: không có / giữa move ⇒ qua |
| C5 | 4.4 Giá cách vùng | ≤ 1 giá hoặc râu chạm · hơn 1, chưa tới 3 · từ 3 giá (ở lưng) | hơn 1 ⇒ CHỜ "chờ hồi về cạnh"; từ 3 ⇒ `NO_BACK` |
| C6 | Biên độ nến M1 cao nhất trong 5 nến (giá) | số | sàn nhiễu (QĐ-18) |
| C7 | Ô riêng | **B**: DMA ngang · còn dốc ⇒ `NO_DMA_SLOPE`. **D**: "move vừa rồi: __ giá" (< 5 ⇒ `NO_D_NO_MOVE`) · "nhịp hồi đã quá 70 % move?" chưa · rồi ⇒ `NO_D_DEEP`. A, C: không có | |

**3b. Bấm — sau khi nến xác nhận đóng** (thao tác: A 5 · B 6 · C 4 · D 5)

| # | Điều khiển | Lựa chọn | Áp cho |
|---|---|---|---|
| B1 | 4.1 Nhịp hồi | **U** · **V** · không rõ (tiêu chí 2 dòng dưới nút) | A, B, D. V ⇒ `NO_V_PULLBACK`; không rõ ⇒ `NO_UNCLEAR`. C: ẩn, sổ in "—" |
| B2 | 4.2 Thân + \|delta\| 3 nến cuối | giảm dần · lẫn lộn · tăng dần · không rõ | **B**: giảm ⇒ qua; lẫn ⇒ CHỜ; tăng ⇒ `NO_MOMENTUM`; không rõ ⇒ `NO_UNCLEAR`. A, C, D: ẩn |
| B3 | "Nến xác nhận đạt chuẩn?" | đạt · chưa · không rõ — tiêu chí `criteria[]` 2–4 dòng dưới nút: **A** đóng theo chiều phá · thân ≥ nửa biên độ · delta cùng dấu · tại cạnh: delta cùng chiều phá hoặc hấp thụ phe ngược. **B** ngược chiều move · delta đảo dấu ≥ ½ nến lớn nhất của move. **C** râu xuyên cạnh rồi đóng lại trong · thân không ngắn, râu ngược không dài · delta ủng hộ. **D** đỉnh hồi có bong bóng hấp thụ phe hồi hoặc nến hồi delta thuận đóng dưới nửa thân · nến xác nhận đóng theo chiều cũ, thân dài, delta cùng dấu | chưa ⇒ CHỜ; không rõ ⇒ `NO_UNCLEAR` |
| B4 | Giá vào · SL · TP | 3 số (nhận "." và ","); **TP gợi ý sẵn** theo QĐ-16 | |
| B5 | "SL đúng chỗ?" | đúng chỗ · chưa chắc · sai chỗ — tiêu chí 1 dòng theo kịch bản: **A** sau râu nến xác nhận hoặc mép xa vùng, cái xa hơn, + 0,3 · **B** sau cực trị cụm hấp thụ + 0,3, không ở giữa cụm · **C** sau râu phá hụt + 0,3 · **D** sau đỉnh nhịp hồi + 0,3 | chưa chắc ⇒ CHỜ; sai ⇒ `NO_SL_POS` |

Máy tính (B4 + C6, C6 hiện lại kèm ô sửa): `NO_SL_SIDE` · `NO_SL_FLOOR` ("SL 2,1 < nến 3,3 — đẩy SL ra hoặc bỏ kèo") · `NO_SL_CAP` (> 4 giá) · `NO_RR` (< 1:2) · `NO_TP_PAST_ZONE`. Thu gọn được: **cỡ lệnh MGC** (vốn, % rủi ro trong cài đặt; tick 0,1 = 1 $; số hợp đồng làm tròn xuống; ½ khi `half.reasons` ≠ ∅: `BIAS_NONE` · `SCENARIO_C` · `COUNTER_BIAS` · `NEWS_DAY` · `B_RANK2` · `BEFORE_2030`).

**3c. Phán quyết** (thanh dính đáy, tính lại sau mỗi click, theo thứ tự luật mục 5):
1. **TẮT MÁY** (đen) — ngắt mạch đã kích trong đêm. Tầng 3 vẫn xem được, phán quyết tối đa là TẮT MÁY.
2. **KHÔNG VÀO** (đỏ) + tối đa 2 mã đầu theo thứ tự luật.
3. **CHỜ** (vàng) — tối đa 3 ô còn thiếu theo thứ tự nên làm tiếp.
4. **ENTRY** (xanh, ≥ 32 px), ví dụ ca 6/10: `ENTRY SELL 4193,0 · SL 4195,4 (2,4 giá) · TP 4185,0 · 1:3,3 · cỡ ½` → nút **"Vào lệnh"** mở hộp **market** (giá khớp) / **limit** (giá chờ).
- **Khi bấm "Vào lệnh" hoặc "Tôi vẫn vào (phá luật)"** ⇒ tạo ngay dòng `trades` (có `id`, `exit: null`, chụp `tests`, `mode`, `flags`, `ruleCodes` đang vi phạm, `counterBiasReason`, `slDist`, `slPos`, `c6`) và `open = {tradeId, status, …}`. Hủy limit ⇒ xóa dòng đó.
- Nút **"Tôi vẫn vào (phá luật)"** hiện ở mọi phán quyết trừ ENTRY (kể cả TẮT MÁY); cờ ⚠ + mã; tăng ngắt mạch (QĐ-17).
- **Tám chấm** (HT 9): 1 thẻ + cùng chiều bias (hoặc QĐ-9 hợp lệ) · 2 vùng trong thẻ ≤ 1 giá (B: QĐ-3) · 3 kịch bản đang bật · 4 U (C: tự sáng) · 5 bong bóng: A, C, D sáng khi cùng phe / đã vỡ / không có; B chỉ khi cùng phe · 6 B2 giảm (B) / B3 đạt (A, C, D) · 7 B3 đạt và không khóa 3′ · 8 B5 đúng + sàn + trần + R:R + lần ≤ 2.
- Sau 10′ không thao tác: "đã 10′ — nến M1 đã khác, kiểm lại". **"Kèo mới"** xóa tầng 3. Đổi kịch bản giữ C4–C6, tính lại C2/C3, xóa C7 và bước Bấm.

### Tầng 4 · Lệnh (tối đa 1)
- **Chờ khớp** (limit): "Khớp rồi" (giá khớp thật) · "Hủy — giá bỏ đi" (xóa dòng sổ, không tăng đếm).
- **Đã khớp**: hướng · giá vào thật · SL · TP · R dự kiến · size; ô "giá hiện tại" ⇒ R hiện tại. **Không có ô sửa SL** (RULES D). Mốc be: A/B **+1,5R** + ô "đã có 1 nến M1 đóng ngoài vùng vào" ⇒ "Đã dời về hòa"; C/D **+1R**.
- Khung giờ hạng 1 / FOMC sắp tới mà lệnh còn mở ⇒ đếm ngược "**đóng sạch trước hh:mm**" (19:15 / 00:45; mùa đông +1h).
- **Đóng lệnh**: TP · SL · hòa · đóng tay (lý do: "hấp thụ ngược đe dọa TP" · "đóng sạch trước tin" · "khác" ⇒ cờ phá luật). Giá thoát ⇒ R gợi ý, sửa được. Sau đóng: "SL bị quét rồi giá tới TP?" · ghi chú. Dòng sổ hoàn tất; ngắt mạch cập nhật.
- Lệnh còn mở qua mốc đêm mới ⇒ thuộc đêm vào lệnh; engine nhận cả `nights` nên đêm mới vẫn thấy `open` của đêm trước (khóa tầng 3, mở tầng 4, nhắc Globex bảo trì 04:00–05:00 hè / 05:00–06:00 đông).

### Tầng 5 · Sổ
- **Đêm nay**: bảng 7 cột HT 8 (`giờ | hướng | tên | chế độ | 4 kiểm tra | SL | R`); cột "4 kiểm tra" = `B1 · bb <số> <trạng thái> · Δ <giảm | nến mạnh | —> · <cạnh | lưng>`; dòng ⚠ "phạm 4.1, 4.3 và luật SL" từ `htRef` của `ruleCodes`. Chân: **"Máy cộng: x R"** cạnh **"Bạn cộng: __ R"**, lệch ⇒ đỏ; lệnh phá luật; SL bị quét rồi tới TP. "Kết phiên" cần "Bạn cộng".
- **Tuần**: 4 con số HT 8 + chuỗi đêm 0 phá luật.
- **Xuất**: Markdown · JSON (nhập lại gộp theo `trades.id`; đêm trùng giữ bản có `tally.closedAt` mới hơn) · CSV.

### Thanh trạng thái + đồng hồ
- Giờ VN; nhãn pha (mỗi mốc mang múi gốc): Ban ngày · Chuẩn bị 18:00 VN · COMEX mở 19:20 ET · Tin 19:30 ET · NYSE 20:30 ET · Lõi giao thoa 21:00 ET – 22:30 LONDON · London đóng 22:30 LONDON · Mỏng dần 23:00 VN · Chốt giá ngày 00:30 ET · Globex bảo trì 04:00–05:00 ET-tương-đương (hè 04:00–05:00 VN). Dòng "Mỹ đang giờ mùa đông: mốc +1h" từ 01/11.
- Đếm ngược tới khung giờ cấm kế; trong khung giờ: thanh đỏ; 20:30 ±5′ và trước 20:30: thanh vàng.
- Chip: phá luật n/2 · SL liên tiếp n/3 · lệnh mở 0/1 (luyện mắt ghi rõ) · vùng đang chọn n/2.
- **`nightKey(now)`** = hôm nay nếu đã qua mốc Globex mở ngày mới (**18:00 ET** = 05:00 VN hè / 06:00 VN đông), ngược lại hôm qua.

---

## 4. Nguyên tắc UI/UX (bắt buộc với người implement)

1. **Một màn hình, một việc.** Tầng chưa mở hiện mờ với một câu lý do. Bước Bấm vừa một màn 1366×768 không cuộn.
2. **Phán quyết luôn thấy** ở tầng 3; màu cố định: xanh ENTRY · vàng CHỜ · đỏ KHÔNG VÀO · đen TẮT MÁY · xám CHỈ XEM.
3. **Nhãn chính ≤ 9 từ** (đếm theo khoảng trắng, bỏ ký hiệu toán và số); tiêu chí dài để trong `criteria[]`; trợ giúp "?" ≤ 2 câu + link đúng mục trang HT (`…/he-thong-dem-vang/#id`: `sau-cau-hoi ma-tran-bias xep-hang-vung acceptance thoi-gian v-hay-u than-delta bong-bong-phe canh-hay-lung kb-a kb-b kb-c kb-d xung-dot ca-that luat-sl tp-be the-phien nhat-ky-lenh cuoi-tuan`). Mỗi kịch bản kèm ảnh `img/kb-*.png`.
4. **Hai mức hướng dẫn**: *Mới* / *Quen*. Nhớ lựa chọn.
5. **Nút chọn nhóm 3 trạng thái** cho mọi câu có đáp án xấu; đáp án xấu tô đỏ khi chọn; không checkbox.
6. **Không hộp thoại xác nhận** trừ: sửa thẻ khi đang canh kèo (sau 19:20), "Tôi vẫn vào (phá luật)", xóa dữ liệu, tắt khung giờ cấm.
7. **Bàn phím** (tầng 3, tắt khi focus ô nhập; `Esc` rời ô): `1–4` kịch bản, `B`/`S` hướng (chỉ B), `U`/`V`, `Enter` nút chính, `N` kèo mới, `?` trợ giúp.
8. **Tối mặc định**, WCAG AA, có chế độ sáng. Font hệ thống. Số hiển thị dấu phẩy; ô nhập nhận cả dấu chấm.
9. **Điện thoại ≥ 360 px**: tầng dọc, thẻ phiên thành ngăn trượt, thanh phán quyết dính đáy, không tràn ngang.
10. **Nhanh**: không thư viện ngoài, tải < 100 KB, thao tác < 50 ms, lưu ngay sau mỗi click.
11. **Ngôn ngữ**: tiếng Việt đủ dấu, câu ngắn. Giữ tiếng Anh: buy · sell · limit · market · sell limit · buy limit · ENTRY; thuật ngữ: TPO, VA, VAH, VAL, POC, HVN, LVN, VWAP, delta, DMA, IB, R, SL, TP, be, fade, trap, tail, single print, poor high/low, naked POC, bias, acceptance, move, retest, range, bracket, session, tick, thin, Trend thin, setup, profile, COMEX, NYSE, Globex, FOMC, NFP, CPI, Jobless Claims, ET, Markdown, JSON, CSV, Esc, Enter. Viết tiếng Việt thay cho: flat → "đóng sạch", settlement → "chốt giá ngày", overlap → "giao thoa", DST → "giờ mùa đông", paper → "luyện mắt". **Cấm tuyệt đối trong `content.js`: "bán", "mua"** (viết "phe sell", "phe buy"), "lệnh chờ", "đập giá".

---

## 5. Kiến trúc kỹ thuật

```
tram-dem-vang/
  index.html · manifest.webmanifest · sw.js · icons/ · img/kb-*.png
  css/app.css
  js/content.js    # TOÀN BỘ chữ: nhãn, criteria[], trợ giúp, lý do theo mã + htRef — dữ liệu thuần
  js/rules.js      # DANH SÁCH LUẬT CÓ THỨ TỰ + hằng số (ma trận bias, bảng vùng, mốc giờ có múi, ngưỡng, APP_VERSION)
  js/time.js       # giờ VN, giờ mùa đông Mỹ/London, pha, khung giờ cấm, nightKey
  js/engine.js     # thuần: (nights, nightKey, now, settings) → {verdict, reasons, missing, dots, order, enabled:{A..D: code|null}, half:{reasons}, regime}
  js/store.js · js/journal.js · js/ui/*.js · js/main.js
  tests/*.test.js  # node:test, CommonJS, require js/*.js
  e2e/*.spec.mjs   # Playwright chromium
  scripts/lint-vi.mjs · scripts/vi-khong-dau.txt · deploy.sh · README.md
  docs/IMPL-n.md · REVIEW-n.md · USER-TEST-n.md
```

- **Không ES module.** Mỗi file JS dùng UMD nhỏ: `(function (root, factory) { if (typeof module === 'object' && module.exports) module.exports = factory(); else (root.TDV = root.TDV || {}).engine = factory(); })(this, function () { … })`.
- **Service worker** (Pages): `scope` `./`, cache theo `APP_VERSION`, `skipWaiting` + `clients.claim`, thẻ "có bản mới — tải lại". `deploy.sh` tăng `APP_VERSION`.
- **Engine = danh sách luật có thứ tự** `[{code, scope, when(ctx) → bool, effect: 'OFF'|'NO'|'WAIT'|'DISABLE'|'HALF'}]`, chạy tuần tự, `reasons` giữ thứ tự. **Thứ tự:** `OFF_RULE_BREAKS`, `OFF_SL_STREAK` → lệnh mở (khóa tầng 3) → `NO_NEWS_WINDOW` → `DIS_LONGEST_BAR` → `DIS_NO_CARD` → `DIS_BIAS_WAIT` → `DIS_BIAS_NONE` → `DIS_NO_EDGE` → chế độ (`DIS_NOT_BROKEN`, `DIS_PENDING_ACCEPT`, `DIS_NO_MOVE`, `DIS_M5_OUTSIDE`, `DIS_USE_D`, `DIS_THIN_NO_FADE`) → `DIS_BREAK_AGAINST_BIAS` → `DIS_EARLY_BREAK` (A, phá 18:00–19:20) → HALF (`BEFORE_2030`…) → hướng vs bias (`NO_COUNTER_BIAS_SCENARIO`, `NO_COUNTER_BIAS_ZONE`) → vùng (`NO_ZONE_3RD`, `NO_BANNED_ZONE`, `NO_MID_RANGE`, `NO_PENDING_ACCEPT`, `NO_B_RANK`, `NO_FIGHT_BREAK`) → C4, C5 → C7 → B1, B2 → B3 → B5, `NO_SL_SIDE`, `NO_SL_FLOOR`, `NO_SL_CAP`, `NO_RR`, `NO_TP_PAST_ZONE`. `paper` là cờ hạ cấp ENTRY, không phải luật.
- **Mô hình dữ liệu** `localStorage["tdv.v1"]`:
```
{ version: 1,
  settings: {theme, guideLevel, capital, riskPct, dstShift: true, shortcuts: true},
  nights: { "<nightKey>": {
     t0: {alert, touched, windows:[{id, kind, rank:1|2, at:'HH:MM', tz:'ET', minutesBefore, minutesAfter, on, offAt?}], newsDay, note},
     card: {answers:{q1,q1w,q2top,q2bot,q3,q4,q5,q6,vwapW}, bias:{auto, override, reason, rechecked},
            zones:[{id,type,price,priceTo?,side?,note,flags:[]}], plan1, plan2, cancelWhen, lockedAt, edits:[{at,what}]},
     regime: {mode, thinDir, breakout:{dir, edgeZoneId, at, nth, step1, step2}, longestBarUntil, log:[{at,mode}]},
     setup: {scenario, side, zoneId, counterBiasReason, c4, c4num, c5, c6, c7:{dma, moveSize, deep}, b1, b2, b3,
             calc:{entry, sl, tp, tpSuggested}, slPos, updatedAt},
     open: {tradeId, status:'pending'|'filled', beAt, beDone, outsideZoneBar} | null,
     trades:[{id, time, side, scenario, mode, zoneId, zoneType, tests:{b1,c4,c4num,b2,b3,c5}, c6, entryPlanned, entry, sl, tp, size,
              slDist, slPos, rrPlanned, exit:null|{kind, price, reason, at}, r, flags:[], counterBiasReason, ruleCodes:[], sweptThenTP, notes}],
     tally:{machine, manual, closedAt} } } }
```

---

## 6. Kiểm thử (người implement phải chạy, báo kết quả thật)

**Đơn vị (node:test, `npm test`)** — tối thiểu:
- Ma trận bias: 14 ca.
- Bật kịch bản: bias (CHỜ, KHÔNG, BUY) × `effective` (4) × giờ (20:29 / 20:31 hè; 21:29 / 21:31 đông ⇒ chỉ đổi `half`) × acceptance (đủ / thiếu bước 2 / phá 18:30) × `regimeDir` (cùng / ngược bias) — ≥ 28 ca, kiểm `enabled` **và mã** `DIS_*`; `thin` xuống + bias BUY ⇒ D `DIS_BREAK_AGAINST_BIAS`; `broken` xuống + bias BUY ⇒ A `DIS_BREAK_AGAINST_BIAS`; thẻ không có `edge` ⇒ B, C `DIS_NO_EDGE`.
- Phán quyết, một mã mỗi ca: `NO_NEWS_WINDOW` (19:30 ±15′ khi bật; 21:00 ±5′) · 20:25 và 20:34 không chặn · `DIS_LONGEST_BAR` tới phút tròn + 3 · `NO_COUNTER_BIAS_SCENARIO` (bias ghi đè ngược `regimeDir` cho A) · `NO_COUNTER_BIAS_ZONE` (B ngược bias tại VWAP tuần; `sp` sai phía) · **B sell ngược bias BUY tại High hôm qua cờ `tail`** ⇒ ENTRY 2R ½ · `NO_ZONE_3RD` (n = 2) · `NO_BANNED_ZONE` (HVN ngày, LVN, HVN 3 tuần với B) · `NO_MID_RANGE` · `NO_PENDING_ACCEPT` (C tại cạnh vừa phá khi `pending`; C tại cạnh khác ⇒ qua) · `NO_B_RANK` (B buy cùng bias tại Low hôm qua, `balanced`; B tại VAH Âu khi `broken`) · `NO_FIGHT_BREAK` (B ngược chiều phá tại hạng 2) · B ngược chiều phá tại VWAP tuần cùng bias ⇒ qua · `NO_BUBBLE_AGAINST` · B "không có" ⇒ CHỜ · `NO_UNCLEAR` từ C4, B1, B2, B3 · `NO_BACK` · C5 hơn 1 ⇒ CHỜ · `NO_MOMENTUM` · B lẫn lộn ⇒ CHỜ · `NO_DMA_SLOPE` · `NO_D_NO_MOVE` (4,9) · `NO_D_DEEP` · `NO_SL_POS` · `NO_SL_FLOOR` · `NO_SL_CAP` · `NO_RR` · `NO_SL_SIDE` · `NO_TP_PAST_ZONE` · lệnh mở ⇒ tầng 3 khóa · CHỜ với `missing` đúng thứ tự · ENTRY đúng số, đúng `half`.
- **Năm ca** theo Phụ lục A (fixtures đầy đủ).
- Ngắt mạch (QĐ-10, QĐ-17): 2 phá luật ⇒ OFF; "Tôi vẫn vào" ×2 ⇒ OFF; 3 SL liên tiếp ⇒ OFF; hòa và TP reset; đêm mới về 0; đóng tay "khác" ⇒ phá luật; "đóng sạch trước tin" ⇒ không; `paper` không cộng gì; limit hủy xóa dòng.
- Tầng 4: mốc be +1,5R / +1R với SL lẻ 0,1; lệnh mở qua đêm: engine với `nightKey` mới vẫn khóa tầng 3.
- Thời gian: `nightKey` tại 00:30, 04:59 (đêm cũ), 05:00, 10:00 (đêm mới) ngày hè; 05:30 ngày 02/11/2026 (đêm cũ); mốc giờ tại 24/10, 25/10, 31/10, 01/11/2026, 13/03, 14/03, 27/03, 28/03/2027; khung giờ ±15′ / ±5′; thứ Năm bật 19:30.
- Thẻ phiên: vết trước/sau 19:20; sửa khi đang canh kèo ⇒ cần xác nhận.
- Sổ: cộng R, lệch máy/tay, 4 con số tuần, Markdown đúng mẫu (so chuỗi), dòng ⚠ từ `htRef`, cột Δ và V/U cho 4 kịch bản.
- Store: migrate; nhập JSON gộp theo `trades.id`.

**Đầu cuối (Playwright, `npm run e2e`)**: (1) đường đi tới ENTRY và ghi sổ cho **A và B**, đếm thao tác (A 4/5, B 7/6); (2) tầng 3 khóa khi chưa chốt thẻ / bias CHỜ / có lệnh; (3) V ⇒ KHÔNG VÀO đỏ; (4) tải lại giữ nguyên; (5) `file://` không lỗi console; (6) 360 px không tràn ngang; (7) phím tắt, tắt trong ô nhập; (8) "Tôi vẫn vào" ×2 ⇒ TẮT MÁY.

**Lint chữ (`npm run lint:vi`)** trên `content.js` (trừ `criteria[]`): (a) chuỗi "bán", "mua", "lệnh chờ", "đập giá" ⇒ lỗi; (b) token chỉ gồm `[A-Za-z]` dài ≥ 3 hoặc toàn chữ hoa ≥ 2, **so không phân biệt hoa/thường**, không có trong danh sách 4.11 và không có trong `scripts/vi-khong-dau.txt` (từ Việt không dấu hay gặp; bổ sung khi lint báo sai) ⇒ lỗi; (c) nhãn > 9 từ; (d) dấu chấm thập phân trong chuỗi hiển thị.

Tiêu chí "xong" mỗi vòng: `npm test`, `npm run e2e`, `npm run lint:vi` xanh (dán kết quả thật vào `docs/IMPL-n.md`); ảnh 3 màn; deploy Pages mở được.

---

## 7. Quy trình thực hiện

**Giai đoạn P (xong)**: 3 vòng review Fable.

**Giai đoạn I — tối đa 4 vòng**: 1 Sonnet implement + test → `docs/IMPL-n.md` · 2 song song: Opus review → `docs/REVIEW-n.md`; Sonnet "trader 1 tháng kinh nghiệm" dùng thử → `docs/USER-TEST-n.md` (điểm /5) · 3 Sonnet sửa, chạy lại test. Dừng sớm khi hết "sai luật" / "chặn đường đi" và người dùng thử ≥ 4/5. Sau mỗi vòng: commit tiếng Việt + push + deploy Pages + `progress.md`.

## 8. Câu hỏi mở (mặc định đã chọn)

1 Mốc giờ dịch mùa đông: có (QĐ-7) · 2 20:30: chỉ cảnh báo (QĐ-6) · 3 trước 20:30: không tắt, ½ (QĐ-19) · 4 cụm POC hạng 2 cho B: có, ½ (QĐ-3) · 5 tự xóa tầng 3: không · 6 máy tính cỡ lệnh: thu gọn · 7 tên: "Trạm Đêm Vàng".

## 9. Đối chiếu review 1 → bản 2
1 trục bias · 2 QĐ-9 · 3 B5 theo kịch bản · 4 QĐ-1 · 5 QĐ-2 · 6 QĐ-3 · 7 QĐ-6 · 8 C5 ba nút · 9 QĐ-5 · 10 C4 với B · 11 D 2R · 12 3–5 vùng · 13 QĐ-7 · 14 acceptance 2 bước · 15 limit/hủy · 16 lệnh mở gặp tin · 17 không sửa SL · 18 QĐ-10, nút phá luật, qua đêm · 19 dữ liệu sổ · 20 Q2a/b · 21 IB · 22 QĐ-11 · 23 Canh/Bấm · 24 B3 của B · 25 vết trước 19:20 · 26 Kế hoạch 1/2 · 27 Bạn cộng · 28 khóa tầng 3 · 29 QĐ-8 · 30 phút tròn + 3 · 31 phím tắt · 32–34 chữ · 35 file:// · 36 thứ tự luật · 37 nightKey · 38 test · 39 lint.

## 10. Đối chiếu review 2 → bản 3
1 `pending` · 2 naked POC · 3 cờ `sp`/`tail` · 4 QĐ-9 chạy được · 5 20:30 cảnh báo · 6 QĐ-4 hẹp, bỏ C7b · 7 mã `DIS_*` · 8 ví dụ ENTRY · 9 `criteria[]` · 10 `NO_UNCLEAR` · 11 QĐ-12..14 · 12 HVN ngày · 13 QĐ-16 · 14 QĐ-17 · 15 thao tác · 16 B5 ba nút, QĐ-18 · 17 `DIS_NO_EDGE` · 18 dữ liệu · 19 múi gốc · 20 test rõ · 21 từ Anh · 22 câu chữ.

## 11. Đối chiếu review 3 → bản 4

| Mục | Sửa ở bản 4 |
|---|---|
| 1 `DIS_BEFORE_2030` giết 3 ca | QĐ-19: không tắt, cảnh báo + ½; hàng "trước 20:30" trong bảng bật thành HALF; test 6/10 ⇒ ENTRY ½. |
| 2 `DIS_PENDING_ACCEPT` phụ thuộc vùng | Nguyên tắc mã `DIS_*` / `NO_*`; `pending`: A `DIS_PENDING_ACCEPT`, B/C bật, D `DIS_NO_MOVE`; tầng 3 `NO_PENDING_ACCEPT`. |
| 3 ba luật không mã | `NO_B_RANK`, `NO_COUNTER_BIAS_ZONE`; C2 khóa cho A, C, D. |
| 4 thin không hướng | `regime.thinDir`, `regimeDir`; hàng `DIS_BREAK_AGAINST_BIAS`; C2 của D = `regimeDir`. |
| 5 ngữ nghĩa bảng | "Duyệt mọi hàng, mã đầu tiên tắt hiển thị"; thứ tự khớp mục 5 (khóa 3′ → thẻ → bias…). |
| 6 `edge` vs High/Low | `edgeOuter`; QĐ-1 viết rõ; test `NO_B_RANK` tại Low hôm qua. |
| 7 A đúng cạnh vừa phá | C3 của A tự điền `edgeZoneId` khi `broken`; đếm A 4/5. |
| 8 dữ liệu lệnh | Tạo dòng `trades` (có `id`) lúc vào lệnh, `open.tradeId`; engine `(nights, nightKey, now, settings)`; gộp theo `id`. |
| 9 fixtures | Phụ lục A; 1/10 có hai biến thể; 13/10 và 5/10 ghi "ca dựng". |
| 10 lint | Quy tắc phát hiện cụ thể; cấm tuyệt đối "bán"/"mua"; "ENTRY" vào danh sách. |
| 11 HVN ngày | Cờ `noB`; thẻ chỉ gom `banned`. |
| 12 mã ở thin | Chữ `DIS_USE_D`; `DIS_THIN_NO_FADE`. |
| 13 cạnh range | Có phía; C2 điền sau C3 (bảng 3a đổi thứ tự C3 → C2). |
| 14 đếm lệch | "lần thứ n+1", `NO_ZONE_3RD` khi n ≥ 2. |
| 15 theo đêm | QĐ-10 ghi phạm vi `nightKey`. |
| 16 `paper` | QĐ-17: đi tầng 4 như thật, không cộng gì. |
| 17 giờ | 18:00 ET; London 27/03, 28/03/2027; `nth` chỉ hiển thị. |
| 18 chữ | "Mục 9–11"; sơ đồ "21:00"; 1e ba ô người dùng gõ; QĐ-16 vế B ngược bias; "ENTRY" 4.11; dải giờ không chồng; sổ V/U "—" cho C; `htRef`. |

---

## Phụ lục A — Fixtures 5 ca test (số cố định)

Chung: `settings = {dstShift: true, capital: 2000, riskPct: 2}`; `t0 = {alert: true, touched: true, windows: [19:30 off, 21:00 on], newsDay: false}`; mọi ngày là 2026 (giờ hè Mỹ); `card.lockedAt = 19:00`; `regime.log` bỏ qua.

**A1 · 6/10 20:24 — A sell ⇒ ENTRY, cỡ ½ (QĐ-19)**
- card: q1 D · q1w D · q2top bình thường · q2bot bình thường · q3 không · q4 giữa · q5 dưới · q6 rồi · vwapW dưới ⇒ bias SELL.
- zones: z1 VWAP tuần 4205 · z2 cụm POC 4195–4196 · z3 VAH Âu 4199 · z4 VAL Âu 4185.
- regime: mode Vừa phá, breakout {dir down, edgeZoneId z2, at 20:15, nth 1, step1 true, step2 true} ⇒ `broken`, `regimeDir` down.
- now 20:24. setup: scenario A · zoneId z2 (tự) · side sell (tự) · c4 không có · c5 ≤ 1 · c6 2,0 · b1 U · b3 đạt · calc {entry 4193,0, sl 4195,4, tp 4185,0} · slPos đúng.
- tpSuggested: 3R = 4193,0 − 7,2 = 4185,8; vùng kế tiếp phía dưới = z4 4185 ⇒ gợi ý 4185,8 (gần hơn). TP 4185,0 không vượt z4 quá 0,5.
- Kỳ vọng: verdict ENTRY · reasons [] · slDist 2,4 · rr 3,33 (in "1:3,3") · half.reasons [`BEFORE_2030`] · dots 8/8 · enabled.A null.

**A2 · 12/10 21:27 — A sell ⇒ KHÔNG VÀO [NO_BUBBLE_AGAINST, NO_V_PULLBACK]**
- card: q1 b · q5 dưới · vwapW dưới · q6 rồi ⇒ bias SELL. zones: z1 HVN tuần 4190 · z2 VAL Âu 4186 · z3 VAH Âu 4196.
- regime: Vừa phá {down, edgeZoneId z1, at 21:17, nth 1, step1 true, step2 true}.
- now 21:27. setup: A · z1 (tự) · sell (tự) · c4 ngược phe còn giữ, c4num +103 · c5 ≤ 1 · c6 2,0 · b1 V · b3 đạt · calc {4188,0, 4190,3, 4181,0} · slPos đúng.
- Kỳ vọng: NO · reasons đúng thứ tự [`NO_BUBBLE_AGAINST`, `NO_V_PULLBACK`] · sổ (nếu "Tôi vẫn vào") in ⚠ "phạm 4.3, 4.1".

**A3 · 1/10 20:47 — A sell ⇒ KHÔNG VÀO [NO_SL_FLOOR]** (biến thể b: [NO_SL_POS, NO_SL_FLOOR])
- card: q1 D · q5 dưới · vwapW dưới · q6 rồi ⇒ SELL. zones: z1 VWAP tuần 4194,8 · z2 HVN ngày 4193 · z3 VAL Âu 4188.
- regime: Vừa phá {down, edgeZoneId z2, at 20:40, nth 1, step1 true, step2 true}.
- now 20:47. setup: A · z2 · sell · c4 không có · c5 ≤ 1 · c6 3,3 · b1 U · b3 đạt · calc {4192,7, 4194,8, 4182,7} · slPos **đúng** (a) / **sai** (b).
- Kỳ vọng (a): NO, reasons [`NO_SL_FLOOR`] (SL 2,1 < 3,3). (b): [`NO_SL_POS`, `NO_SL_FLOOR`].

**A4 · ca dựng từ 13/10 20:10 — B buy ⇒ ENTRY ½** (biến thể b: `broken` ⇒ NO_FIGHT_BREAK)
- card: q1 D · q5 trên · vwapW trên · q6 rồi ⇒ BUY. zones: z1 VAL Âu 4175 · z2 cụm POC 4175,5 · z3 VAH Âu 4184 · z4 LVN ngày 4172.
- regime (a): Cân bằng ⇒ `balanced`. (b): Vừa phá {down, edgeZoneId z1, at 20:00, step1 true, step2 true}.
- now 20:10. setup: B · z2 · side buy · c4 cùng phe, c4num −49 · c5 ≤ 1 · c6 2,0 · c7.dma ngang · b1 U · b2 giảm dần · b3 đạt · calc {4177,0, 4174,7, 4183,9} · slPos đúng.
- tpSuggested (a): 3R = 4183,9; vùng kế tiếp phía trên z3 4184 ⇒ 4183,9.
- Kỳ vọng (a): ENTRY · half.reasons [`B_RANK2`, `BEFORE_2030`] (nhân ½ một lần) · rr 3,0 · z2 đạt QĐ-1 vì |4175,5 − 4175| ≤ 1. (b): NO, reasons [`NO_FIGHT_BREAK`] (ngược chiều phá tại hạng 2).

**A5 · ca dựng từ 5/10 19:25 — B buy ⇒ CHỜ, missing[0] = b2**
- card: q1 D · q5 trên · vwapW trên · q6 rồi ⇒ BUY. zones: z1 VWAP tuần 4181 · z2 VAL Âu 4182 · z3 VAH Âu 4192.
- regime: Cân bằng. now 19:25 (khung giờ 19:30 tắt trong t0).
- setup: B · z1 (trùng cạnh z2, |4181 − 4182| ≤ 1) · buy · c4 cùng phe, +25 · c5 ≤ 1 · c6 2,5 · c7.dma ngang · b1 U · b2 lẫn lộn · b3 đạt · calc {4183,0, 4180,5, 4190,5} · slPos đúng.
- Kỳ vọng: WAIT · reasons [] · missing[0] = `WAIT_B2_MIXED` ("chưa đủ 3 nến giảm dần") · half.reasons [`BEFORE_2030`].
