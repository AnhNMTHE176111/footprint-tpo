# TEST-UI-v2 — kiểm thử giao diện Trạm Đêm Vàng 2.0.0

Ngày: 2026-10-20 · Mã kiểm: commit `25e9dbc` (không sửa code) · Công cụ: Playwright Chromium chạy `index.html` qua `file://`, giờ cố định 21:30, mỗi lần mở là một context mới (localStorage trống, chỉ gieo dữ liệu mẫu từ `e2e/helpers.mjs`).
Khung hình: 1366×768, 1920×1080, 390×844, 360×740 · Chế độ tối và sáng · Ảnh: `docs/test-ui-v2/` (153 ảnh).

Tên ảnh: `<khung>-<chế độ>-t<tầng>.png` là ảnh nguyên trang từng tầng (trong ảnh nguyên trang, thanh đáy dính hiện ở vị trí màn hình đầu, đó là do cách chụp, không phải lỗi) · `zp-*` ô chọn loại vùng · `se-*` Setup Entry · `gl-*` Từ điển · `st-*` thanh trạng thái điện thoại · `card-*` thẻ phiên · `so-*` Sổ · `var-*` các trạng thái thanh đáy · `pages-1366.png` bản trên Pages.

## Những gì ĐẠT (đo bằng số, không phải nhìn)

- **Tràn ngang:** 0 phần tử vượt mép ở cả 32 tổ hợp (4 khung × 2 chế độ × 4 tầng); `scrollWidth` của trang luôn bằng bề rộng khung.
- **Chữ bị cắt** (có `overflow:hidden` hoặc dấu "…"): 0 chỗ.
- **Chữ thô ⟦…⟧:** 0. **Ảnh hỏng:** 0. **Lỗi hoặc cảnh báo trên console:** 0 (chạy qua `file://`, cả lần mở đầu khi localStorage trống). Bản Pages trả về 200, có đủ 4 tầng `0 Trước · 1 Vùng · 2 Setup Entry · 3 Sổ`, không có lỗi console ([pages-1366.png](test-ui-v2/pages-1366.png)).
- **Focus ring:** đi Tab 50 lần qua khối B ở cả 8 tổ hợp: mọi phần tử nhận focus đều có viền (2 px màu nhấn); không phần tử nào bị thanh nhảy hoặc thanh ENTRY che khi nhận focus.
- **Ô chọn loại vùng:** mở thì focus vào ô lọc; 18 loại; rê chuột lên dòng đầu, giữa, cuối đều hiện đúng định nghĩa và khung định nghĩa nằm trong màn hình (máy tính: khung bên phải từ x=385 đến 767 ở 1366; điện thoại: hiện ngay dưới dòng, x=53–337 ở 390). Home/End/↑/↓ chạy, xuống quá dòng cuối thì vòng về dòng đầu, End cuộn dòng cuối vào khung; gõ "poc" lọc còn 2 dòng; Enter chọn và trả focus về nút; Esc đóng và trả focus về nút; gõ chữ trên nút thì mở và điền chữ vào ô lọc; không khớp thì hiện "Không có loại vùng nào khớp."; bấm ra ngoài thì đóng; Tab đóng và đi tiếp ([zp-d1366-dark-hover-last.png](test-ui-v2/zp-d1366-dark-hover-last.png), [zp-m360-light-filter.png](test-ui-v2/zp-m360-light-filter.png)).
- **Setup Entry:** 4 khối xếp dọc, luôn mở; thanh nhảy dính ngay dưới thanh trạng thái (đỉnh thanh nhảy = đáy thanh trạng thái: 39 px máy tính, 43 px điện thoại); bấm A/B/C/D đều đưa đúng khối lên và tiêu đề khối không bị che; tiến độ đúng (`4/19 · 18/18 · 0/15 · 0/15`); khối B đủ thì có lớp `complete`, viền xanh; thanh ENTRY `position:fixed`, chữ `.ebig` = **32 px** ở cả 4 khung; thanh ENTRY chiếm 7–10 % chiều cao máy tính, 14–16 % điện thoại; cuộn tới đáy thì ô cuối khối D vẫn nằm trên thanh ENTRY (cách 53 px).
- **Từ điển:** mở, focus vào ô tìm, 41 mục, gõ "vwap" còn 4, Esc đóng; điện thoại hiện toàn màn hình ([gl-m390-dark.png](test-ui-v2/gl-m390-dark.png)).
- **Thẻ phiên điện thoại:** mở từ nút nổi, Esc đóng. **Thanh trạng thái điện thoại:** nút "Trạng thái" mở phần còn lại thành lớp phủ, không đẩy nội dung ([st-m360-dark-open.png](test-ui-v2/st-m360-dark-open.png)).
- **Sổ:** dòng lệnh mở nằm trên cùng; bấm "Chạm TP" điền sẵn giá thoát 4183,9 và R = 3; "Ghi kết quả" xóa dòng lệnh mở và thêm dòng vào bảng ([so-d1366-dark-tp.png](test-ui-v2/so-d1366-dark-tp.png)).

## Danh sách lỗi

### 1. [nặng] Nhãn ô chung "Không trong 3 nến M1 sau nến dài nhất phiên" bị bóp thành cột chữ dọc ở điện thoại 380–430 px
- **Đo được:** chiều rộng nhãn `label.tick36` trong `[data-common="longest"]` chỉ còn **22 px ở 390 px** (17 px ở 380, 37 px ở 420), cao 620 px: chữ xếp từng ký tự một theo chiều dọc, ô tick gần như không thấy. Quét bề rộng 360–1000 px: nhãn hẹp dưới 200 px từ **380 đến 730 px** và từ **910 px trở lên** (ở 1366 nhãn bị ép xuống 2 dòng dù còn cả khoảng trống bên phải). Ở 360 px thì không lỗi vì ô ghi chú rớt xuống dòng dưới. Bề rộng 390/393/414/428 là các iPhone phổ biến.
- **Ảnh:** [m390-dark-t2.png](test-ui-v2/m390-dark-t2.png) (phần đầu), [m390-light-t2.png](test-ui-v2/m390-light-t2.png), [d1366-dark-t2.png](test-ui-v2/d1366-dark-t2.png).
- **Nguyên nhân:** trong `.cm` (flex, wrap), `.tick36` có `flex: 1 1 0` (cơ sở 0) còn `.cm-why` rỗng vẫn chiếm `flex: 1 1 220px` ⇒ nhãn chỉ được chia phần thừa còn lại.
- **Sửa:**
  ```css
  .cm-why:empty { display: none; }
  .cm.manual .tick36 { flex: 1 1 260px; }
  .cm.manual .cm-why { flex-basis: 100%; }   /* lý do (nếu có) xuống dòng riêng */
  ```

### 2. [vừa] Ô chọn loại vùng: chuột đứng yên giành lại dòng đang chọn khi dùng phím ↑ ↓
- **Đo được:** để chuột nằm yên trên danh sách rồi bấm ↓ 12 lần, dòng được chọn đi `4,5,6,7,7,8,9,10,10,11,12,13`: hai lần bấm bị nuốt. Khi danh sách cuộn, dòng mới chạy tới dưới con trỏ, phát ra `mouseenter` và kéo dòng chọn về chỗ con trỏ. Trong lượt kiểm chính, Home rồi ↓↓ ra dòng số 7 ("LVN") thay vì dòng số 2, trong khi ở 1920 thì đúng.
- **Ảnh:** [zp-d1366-dark-hover-last.png](test-ui-v2/zp-d1366-dark-hover-last.png).
- **Sửa** (`js/ui/zonepick.js`): đổi `onmouseenter` thành `onmousemove` (chỉ chạy khi chuột thật sự di chuyển):
  ```js
  onmousemove: function () { if (k !== active) setActive(k, false); },
  ```

### 3. [vừa] Độ tương phản dưới chuẩn WCAG AA (đo màu thật sau khi trộn nền)
| Chế độ | Phần tử (selector) | Tỷ lệ | Cần |
|---|---|---|---|
| sáng | `.btn.primary` chữ `#1b1400` trên `#8a6100` ("Xong tầng 0", "Thêm vùng", "Kết phiên", "Ghi kết quả") | **3,31:1** | 4,5 |
| sáng | `.tierbtn.active .tnum`, `.skip` (chữ đen trên `#8a6100`) | 3,79:1 | 4,5 |
| sáng | chữ màu `--go #12894a` trên trắng (`.tickrow` đã tick, `.cm-mark ✓`, `.tdone`, `.kv .v.good`) và chữ trắng 17 px trên thanh ENTRY xanh | 4,47:1 | 4,5 |
| sáng | `.tdone ✓` trên nền tầng đang chọn `#fbeec4` | 3,85:1 | 4,5 |
| sáng | `.chip.dir-sell` "BIAS SELL" `#b45309` trên `#eef0f5` | 4,40:1 | 4,5 |
| tối | `.vbar.v-wait .btn.danger` "Vẫn vào (thiếu 1 ô — tính phá luật)" chữ trắng trên nền trộn `#957730` | 4,20:1 | 4,5 |
- **Ảnh:** [d1366-light-t0.png](test-ui-v2/d1366-light-t0.png), [d1366-light-t2.png](test-ui-v2/d1366-light-t2.png), [se-d1920-light-top.png](test-ui-v2/se-d1920-light-top.png), [d1366-dark-t2.png](test-ui-v2/d1366-dark-t2.png).
- **Sửa:**
  ```css
  :root[data-theme="light"] { --go: #0f7a41; --sell: #9a4508; }               /* 5,4:1 trên trắng, 4,7:1 trên #fbeec4 */
  :root[data-theme="light"] .btn.primary, :root[data-theme="light"] .btn.small.primary,
  :root[data-theme="light"] .tierbtn.active .tnum, :root[data-theme="light"] .skip { color: #fff; }   /* 5,5:1 */
  .vbar.v-wait .btn.danger { background: rgba(0, 0, 0, .5); }                  /* ≈ 7:1 */
  ```

### 4. [vừa] Ảnh ca thật "phóng to" trên điện thoại vẫn quá nhỏ để đọc; trên 1366 phải cuộn trong hộp mới thấy nút Đóng
- **Đo được:** ảnh gốc 1197×855; trong hộp chỉ hiện **316×226 ở 390 px** và 286×205 ở 360 px, chữ trên chart không đọc được và không có cách phóng thêm. Ở 1366×768 hộp cao 691 px, có thanh cuộn, nút "Đóng" nằm dưới mép (Esc và bấm nền vẫn đóng được).
- **Ảnh:** [se-m390-dark-img.png](test-ui-v2/se-m390-dark-img.png), [se-d1366-dark-img.png](test-ui-v2/se-d1366-dark-img.png).
- **Sửa** (`js/ui/tier2.js` + CSS): bọc ảnh trong `<a href="sc.img" target="_blank">` (mở ảnh gốc, chụm 2 ngón để phóng), và giới hạn chiều cao trên máy tính:
  ```css
  .scenimg.full { max-height: calc(90vh - 130px); object-fit: contain; cursor: zoom-in; }
  @media (max-width: 600px) { .modal:has(.imgdlg) { width: 100vw; max-height: 100vh; border-radius: 0; padding: 8px; } }
  ```

### 5. [vừa] Vùng bấm nhỏ hơn 36 px
| Selector | Kích thước | Ở đâu |
|---|---|---|
| `button.help` "?" | **28×28** | máy tính, tầng 1–3 (180 lần đếm) |
| `.btn.small`: "Xóa tick" `[data-testid^=clear-]`, nút ✕ xóa vùng | 69×30, 33×30 | mọi khung |
| `.statusbar .glossary-btn` "Từ điển" | 67×26 | máy tính |
| `.sbtoggle` "Trạng thái" | 97×30 | điện thoại |
| `.seg.small .opt` (Trên / Dưới / Sát ±2 giá) | 47×32 | mọi khung |
| `.vitem` (ô còn thiếu trên thanh CHỜ) | 143×28 | mọi khung |
| `label.tick` trong Sổ ("SL bị quét…") | 187×31 | mọi khung |
| `.fold > summary` "Thêm tay…" | 886×20 | tầng 0 |
| `input.filein` | 253×21 | Sổ |
| `.gclose` ✕ Từ điển | 32×32 | mọi khung |
- **Sửa:**
  ```css
  .help { width: 36px; height: 36px; }
  .btn.small, .statusbar .glossary-btn, .sbtoggle { min-height: 36px; }
  .seg.small .opt, .vitem { min-height: 36px; }
  .tick { min-height: 36px; align-items: center; }
  .fold > summary { padding: 8px 0; }
  .gclose { width: 36px; height: 36px; }
  ```

### 6. [nhẹ] Nhảy A·B·C·D: khối dừng cách thanh nhảy 75 px (máy tính) / 61 px (điện thoại); focus vẫn ở nút nhảy
- **Đo được:** đáy thanh nhảy 100 px, đỉnh khối 175 px (điện thoại 118 / 179). Hai độ lệch bị cộng dồn: `html { scroll-padding-top: 72px }` cộng `.blk { scroll-margin-top: calc(var(--sbh) + 64px) }`. Sau khi nhảy, `document.activeElement` vẫn là nút `[data-jump]`, nên Tab tiếp theo không đi vào khối.
- **Ảnh:** [se-d1366-dark-jumpC.png](test-ui-v2/se-d1366-dark-jumpC.png), [se-m390-dark-jumpC.png](test-ui-v2/se-m390-dark-jumpC.png).
- **Sửa:** đo thêm `--jbh` (chiều cao thanh nhảy) bằng `ResizeObserver` như `--sbh`, rồi `.blk { scroll-margin-top: calc(var(--sbh) + var(--jbh) + 8px - 72px); }`. Trong `app.jumpTo` thêm `t.setAttribute('tabindex', '-1'); t.focus({ preventScroll: true });`.

### 7. [nhẹ] Esc không đóng khung "?"
- **Đo được:** mở "?" ở dòng tick bằng Enter (1 khung mở), bấm Esc thì vẫn còn 1 khung mở. Từ điển, ảnh và thẻ phiên thì Esc đóng được.
- **Ảnh:** [se-d1366-dark-help.png](test-ui-v2/se-d1366-dark-help.png).
- **Sửa** (`js/main.js`, nhánh `Escape`): ẩn mọi `.pop:not([hidden])`, đặt `aria-expanded="false"` cho `.help`, trả focus về nút "?" vừa mở.

### 8. [nhẹ] Ô chọn loại vùng mở sát đáy màn hình thì tràn xuống dưới mép
- **Đo được:** ở 1920×1080, khung chọn kết thúc ở y=1179, thừa **99 px** dưới mép màn hình; trang phải cuộn mới thấy các dòng cuối.
- **Ảnh:** [zp-d1920-dark-hover-last.png](test-ui-v2/zp-d1920-dark-hover-last.png).
- **Sửa** (`zonepick.js`, trong `open()`): sau `pop.removeAttribute('hidden')` thêm `pop.scrollIntoView({ block: 'nearest' });` hoặc lật lên trên khi không đủ chỗ: `.zpick-pop.up { top: auto; bottom: calc(100% + 4px); }`.

### 9. [nhẹ] Thanh ENTRY / CHỜ và thanh trạng thái chỉ rộng 1280 px ở giữa màn hình rộng
- **Đo được:** ở 1920 px, `.vbar` chạy từ x=320 đến x=1600, hai bên là nền trang. Thanh trạng thái cũng vậy (từ 43 đến 1323 ở 1366).
- **Ảnh:** [se-d1920-light-jumpC.png](test-ui-v2/se-d1920-light-jumpC.png).
- **Sửa:** chuyển màu nền từ `.vbar` lên `#verdict` (`#verdict:has(.v-entry){background:var(--go)}` …) hoặc để `.vwrap { max-width: none; }` và giữ nội dung bên trong ở `max-width: 1280px; margin: 0 auto`.

### 10. [nhẹ] Tầng 1: nút "Sang Setup Entry" dính sát chữ "Sau chốt vẫn sửa được…"
- **Đo được:** khoảng cách bằng 0 px, chip "Đã chốt lúc 19:00", nút và câu chữ nối liền nhau.
- **Ảnh:** [d1366-dark-t1.png](test-ui-v2/d1366-dark-t1.png) (phần đáy).
- **Sửa:** `.lockbox { display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: center; }`.

### 11. [nhẹ] Thẻ phiên trên điện thoại có hai nút đóng chồng nhau
- **Đo được:** nút nổi "Đóng" (`#cardtoggle`) nằm ngay trên nút "✕" (`.cardclose`, 44×36).
- **Ảnh:** [card-m390-light.png](test-ui-v2/card-m390-light.png).
- **Sửa:** `body:has(.card.open) .cardtoggle { display: none; }`.

### 12. [nhẹ] Bảng Sổ ở 390 / 360 px cuộn ngang 8–38 px, cột "tên" gãy từng chữ
- **Đo được:** bảng rộng 332 px trong khung 324 px (390) và 294 px (360); "phá hồi" xuống 2 dòng.
- **Ảnh:** [so-m390-dark-open.png](test-ui-v2/so-m390-dark-open.png), [so-m360-dark-done.png](test-ui-v2/so-m360-dark-done.png).
- **Sửa:** `@media (max-width: 600px) { .journal th, .journal td { padding: 6px 4px; } .journal td:nth-child(3) { white-space: nowrap; } }`.

### 13. [nhẹ] Chữ gợi ý của ô gõ nhanh vùng bị cắt ở 360 px
- **Đo được:** chữ gợi ý hiện "…val 418" rồi bị cắt.
- **Ảnh:** [zp-m360-light-filter.png](test-ui-v2/zp-m360-light-filter.png).
- **Sửa:** chữ gợi ý ngắn hơn khi `innerWidth ≤ 600` (ví dụ "vwapw 4205, vah 4199"), hoặc `.quickzones::placeholder { font-size: 13px; }`.

### 14. [nhẹ] Sổ: dòng chú thích "R tự tính từ giá thoát…" lệch so với hai ô số
- **Đo được:** chú thích canh theo đỉnh nhãn, không canh theo ô số.
- **Ảnh:** [so-d1366-dark-tp.png](test-ui-v2/so-d1366-dark-tp.png).
- **Sửa:** `.opentrade .row.wrap { align-items: flex-end; }`.

## Điểm UI: **7/10**

Phần chạy đúng nhiều: không tràn ngang, không lỗi console, không chữ thô, focus ring đầy đủ, thanh dính không che phần tử đang focus, thanh nhảy và thanh ENTRY làm đúng thiết kế, ô chọn vùng đủ phím. Bị trừ điểm vì một lỗi bố cục làm hỏng ô tick ở chính các bề rộng iPhone phổ biến, bàn phím trong ô chọn vùng bị chuột giành, và chế độ sáng có nút chính dưới chuẩn tương phản.

## 3 việc nên sửa trước
1. **Mục 1:** nhãn ô chung bị bóp ở 380–730 px (thêm 3 dòng CSS `.cm-why:empty` / `.cm.manual .tick36`).
2. **Mục 3:** tương phản chế độ sáng (`--go`, `--sell`, chữ trắng cho `.btn.primary`) và nút "Vẫn vào" trên thanh CHỜ.
3. **Mục 2 + mục 5:** đổi `mouseenter` thành `mousemove` trong `zonepick.js`; nâng `.help`, `.btn.small`, `.seg.small .opt` và `.vitem` lên 36 px.
