# GĐ8 🚦 — Audit chống overfit / look-ahead (CỔNG CHẶN trước khi port C#)

| | |
|---|---|
| **Model** | **Opus 5** |
| **Effort** | **xhigh** |
| **Cần trước** | GĐ6, GĐ7 |
| **Chi phí** | trung bình (đọc code + chạy lại thí nghiệm phản biện) |
| **Output** | `quantower-entry-signal/research/wyckoff/AUDIT_V7.md` với **phán quyết PASS/FAIL** |

Vì sao phải có pha này: ngày 2026-07-29 đã tự sinh ra **3 lỗi làm sai toàn bộ số liệu** (trend tol=0,
`avg_vma` tính `mean` toàn chuỗi = look-ahead, gate áp ở nến phá thay vì nến vào). Cả 3 đều "chạy được,
ra số đẹp". Effort thấp sẽ tái tạo đúng loại lỗi này. **FAIL thì không được port sang C#.**

---

=== PROMPT ===

Vai của bạn ở lượt này là **phản biện, không phải xây dựng**. Nhiệm vụ: cố **bác bỏ** kết quả của GĐ6/GĐ7. Mặc định là **nghi ngờ**: một kết quả chỉ được PASS khi bạn đã thử bác mà không bác được.

Output: `quantower-entry-signal/research/wyckoff/AUDIT_V7.md`, kết thúc bằng phán quyết **PASS / FAIL** cho từng kịch bản.

**Không sửa code sản phẩm để "cứu" kết quả.** Bạn được viết script kiểm riêng trong `research/wyckoff/audit/`.
Tìm ra lỗi thì ghi lỗi + cách sửa, việc sửa để GĐ6/GĐ7 làm lại.

## Đọc trước

1. `research/wyckoff/RESULTS_KB12.md` và `RESULTS_KB3.md` — cái cần bác
2. `research/wyckoff/BASELINE.md` — mốc so
3. `research/wyckoff/v7/` — **đọc toàn bộ code**: `features.py`, `engine.py`, `kb3.py`, `loaders.py`, `report.py`
4. `quantower-entry-signal/SPEC_V7_3KB.md` §9 (sổ rủi ro overfit) và §8
5. `quantower-entry-signal/WYCKOFF_V6_PLAN.md` §9, §10, §11
6. `research/DATA_CAPABILITY.md`

## Danh sách kiểm — làm hết, mỗi mục ghi phán quyết + bằng chứng

### A. Look-ahead (nghiêm ngặt nhất)
Với **từng** hàm trong `features.py`, `kb3.py`, `engine.py`:
1. Nó có đọc `B[j]` với `j > i` không? (đọc code, không tin docstring)
2. Có thống kê **toàn chuỗi** không (`mean`/`std`/`percentile` tính trên cả file rồi dùng ở giữa chuỗi)?
   → đây chính là lỗi `avg_vma`.
3. Gate áp ở **nến vào lệnh** hay nến phá? (lỗi cũ)
4. TPO: có dùng VA/POC/IB của **phiên đang chạy** không? IB có được dùng trước khi IB đóng không?
5. VWAP: reset phiên đúng chỗ? có dùng VWAP cuối phiên cho quyết định giữa phiên?
6. Trung bình trượt thanh khoản: có tính tiến dần hay dùng cửa sổ ôm cả tương lai?
7. Dedup / cooldown: có dùng thông tin lệnh sau để loại lệnh trước?

**Cách kiểm mạnh nhất (bắt buộc làm ít nhất 1 lần):** chạy engine trên **dữ liệu bị cắt** — cắt chuỗi tại nến
`i` rồi tính feature, so với giá trị tính trên chuỗi đầy đủ tại cùng `i`. **Khác nhau = look-ahead.**
Làm cho ≥ 5 feature quan trọng nhất, dán bảng so sánh.

### B. Tái lập độc lập
Tự chạy lại GOLDEN TEST và ≥ 3 dòng số quan trọng nhất trong 2 báo cáo. **Không tin bảng trong báo cáo** —
tự chạy, tự đối chiếu. Lệch → ghi lệch bao nhiêu và vì sao.

### C. Partition — tự tính lại
Với mỗi bộ lọc được tuyên bố PASS: **tự** chia phân hoạch và tính lại cả hai phía. Nhóm bị loại không tệ
hơn rõ ràng → bộ lọc là nhiễu → **FAIL** bộ lọc đó.

### D. Số lần thử (multiple comparisons)
Đếm: để chọn ra cấu hình cuối, đã thử **bao nhiêu** cấu hình? (đếm từ script + báo cáo). Với `n ≈ 30` lệnh và
hàng chục cấu hình được sweep, cấu hình tốt nhất **gần như chắc chắn** đẹp một phần do may. Ghi rõ con số này
và hệ quả: kỳ vọng thực tế phải **chiết khấu** so với số trong bảng. Nếu số cấu hình đã thử > ~20 cho một
quyết định mà `n < 40` → ghi cảnh báo **overfit cao**.

### E. Vùng bằng phẳng vs điểm nhọn
Với mỗi tham số chốt: kết quả quanh mặc định có bằng phẳng không? Chỉ một điểm đẹp, lệch 1 bước là sụp →
**FAIL** tham số đó (phải chọn giá trị trong vùng bằng phẳng).

### F. ⭐ OOS THẬT — cửa sổ chưa từng dùng
Đây là phép kiểm **giá trị nhất** của cả pha này. dxFeed có dữ liệu từ **2025-11-02**, nhưng toàn bộ v6 và
GĐ6/GĐ7 chỉ tinh chỉnh trên **2026-05 → 2026-07**. Vậy **2025-11 → 2026-04 là out-of-sample thật sự,
chưa bị nhìn**.
- Chạy cấu hình chốt của KB1, KB2, KB3 và portfolio trên **2025-11 → 2026-04**, không tinh chỉnh gì.
- In theo định dạng cố định, **từng tháng**.
- Phán quyết: OOS dương và cùng hướng với in-sample → tín hiệu mạnh. OOS âm hoặc EV sụt >50% → **FAIL**,
  và nói rõ đây là *chế độ thị trường* hay *overfit*.
- Nếu có tháng nào dữ liệu quá mỏng/thiếu nến → nói ra, đừng gộp im lặng.

### G. Đối chứng 2 nguồn
Chạy cấu hình chốt trên **fp-m1** (cửa sổ trùng) và so với dxFeed. Lệch lớn → ghi rõ, và nhắc lại rằng đã từng
có chênh lệch WR 61% vs 42% giữa 2 nguồn (xem `DATA_CAPABILITY.md`).

### H. Chi phí giao dịch
Backtest hiện **chưa mô hình spread/slippage**. Thêm chi phí cố định mỗi lệnh (thử 1, 2, 3 tick) rồi tính lại
EV. Edge chết ở mức chi phí thực tế của vàng → **FAIL**. Ghi rõ ngưỡng chi phí mà edge còn sống.

### I. Giả định trong nến
Engine giả định **SL trước TP** khi cả hai nằm trong cùng một nến (bi quan). Kiểm: bao nhiêu lệnh bị ảnh hưởng
bởi giả định này? Nếu tỷ lệ cao thì kết quả rất phụ thuộc giả định → ghi cảnh báo.
Thử cả chiều ngược (TP trước SL) để biết **biên độ bất định**.

### J. Portfolio
- Có 2 lệnh nào chồng thời gian không? (phải = 0)
- Có lệnh nào bị đếm 2 lần ở 2 kịch bản?
- Tổng R của portfolio có bằng tổng các lệnh thực sự vào không?

### K. Trung thực báo cáo
Đối chiếu: báo cáo GĐ6/GĐ7 có nêu đủ giới hạn? có tháng âm nào bị gộp vào tổng cho đẹp? có `n < 25` nào bị
gọi là "cải thiện"? Có feature thuộc `SPEC §8` (không kiểm được offline) bị bật mặc định?

## `AUDIT_V7.md` phải có

1. **Bảng phán quyết** ở đầu file: mỗi hạng mục A–K → `PASS / FAIL / CẢNH BÁO` + một câu lý do
2. Với mỗi FAIL: **lỗi cụ thể, ở file:dòng nào, cách sửa, và số liệu nào phải chạy lại**
3. Bảng **OOS 2025-11 → 2026-04** đầy đủ theo tháng (mục F)
4. Bảng **độ nhạy chi phí** (mục H) và **biên độ bất định trong nến** (mục I)
5. Bảng **số cấu hình đã thử** cho từng quyết định (mục D) + mức chiết khấu kỳ vọng
6. **Phán quyết cuối cho từng kịch bản**: `KB1 = PASS/FAIL`, `KB2 = ...`, `KB3 = ...`, và
   **`CÓ ĐƯỢC PORT SANG C# KHÔNG: CÓ/KHÔNG`**
7. Nếu PASS: danh sách **cấu hình đã đóng băng** để GĐ9 port (không được đổi ở GĐ9)
8. Mục **"những gì audit này KHÔNG kiểm được"** — trung thực về giới hạn của chính pha audit

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file/dòng code nhắc đến phải có **link Markdown** dạng `file.py:123`.
2. **TUYỆT ĐỐI không bịa số.** Tự chạy, dán output. Không tin bảng của pha trước.
3. **Không sửa code sản phẩm.** Script kiểm đặt riêng ở `research/wyckoff/audit/`.
4. Được phép — và nên — kết luận **FAIL**. FAIL là kết quả tốt nếu đó là sự thật; PASS sai làm mất tiền thật.
5. Không dựng người rơm: bác đúng cái báo cáo nói, đọc đúng nguyên văn trước khi phản biện.
6. Repo **PUBLIC**: không hardcode token.
7. Không publish lên Claude Artifacts.
8. Xong → **commit + push `origin main`**.

## Xong khi nào

- [ ] Đủ 11 hạng mục A–K, mỗi mục có phán quyết + bằng chứng số
- [ ] Đã làm phép kiểm **cắt chuỗi** cho ≥ 5 feature (mục A)
- [ ] Đã chạy **OOS thật 2025-11 → 2026-04** (mục F) — đây là mục không được bỏ
- [ ] Đã đo độ nhạy chi phí và biên độ bất định trong nến
- [ ] Có phán quyết cuối từng kịch bản + **quyết định có port C# hay không**
- [ ] Đã commit + push

Cuối lượt báo: bảng phán quyết A–K, **kết quả OOS thật**, phán quyết từng kịch bản, và **có được port sang C# hay không**.
