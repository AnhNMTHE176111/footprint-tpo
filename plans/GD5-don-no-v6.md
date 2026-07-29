# GĐ5 — Dọn nợ v6 + chốt baseline để so sánh

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | medium |
| **Cần trước** | — (chạy song song GĐ4 được) |
| **Chi phí** | thấp–trung bình |
| **Output** | `WyckoffRunner.cs` sạch nợ + `quantower-entry-signal/research/wyckoff/BASELINE.md` |

Phải xong **trước GĐ6/GĐ7**: không có baseline đóng băng thì không biết v7 cải thiện được bao nhiêu.
Việc ở đây đã được đặc tả sẵn từng dòng trong `WYCKOFF_V6_PLAN.md` → effort medium là đủ.

---

=== PROMPT ===

Việc của bạn: thực thi các bước còn lại của [WYCKOFF_V6_PLAN.md](../quantower-entry-signal/WYCKOFF_V6_PLAN.md) và **đóng băng baseline** để các pha sau so sánh. Đây là việc thi công theo plan có sẵn — **đọc plan và làm đúng theo đó**, không tự phát minh thêm bộ lọc mới.

## Đọc trước

- [WYCKOFF_V6_PLAN.md](../quantower-entry-signal/WYCKOFF_V6_PLAN.md) — **toàn bộ**. Các bước phải làm nằm ở
  §2 (khung giờ chết), §3 (chốt RR), §4 (A/B lọc thanh khoản), §5 (đòn bẩy phụ), §6 (dọn code chết nhánh
  QUAY_DAU), §7 (BREAK SẠCH cho QUAY_DAU). §9/§10/§11/§12 là ràng buộc: đừng làm lại việc đã chết, đừng hứa
  cái không kiểm được, luôn kèm giới hạn khi trích số, và tái lập số theo §12.
- [research/wyckoff/cbr_v6.py](../quantower-entry-signal/research/wyckoff/cbr_v6.py) và
  [final_table.py](../quantower-entry-signal/research/wyckoff/final_table.py) — engine + bảng số chuẩn.
- [WyckoffRunner.cs](../quantower-entry-signal/WyckoffRunner.cs) — file sẽ sửa.

## Thứ tự thực thi

### Bước 1 — SỬA LỖI KHUNG GIỜ CHẾT (ưu tiên cao nhất)
Làm đúng **phương án A** ở §2 của plan. Bản chất lỗi: cột thời gian là **UTC**, code lại cộng `TzOffset=7`
trước khi so với `DeadStart/DeadEnd` → cắt mất khung UTC 19–01 (khung mà lọc thanh khoản đã làm rỗng sẵn),
còn khối lỗ thật ở **UTC 02–08** thì không bị chặn.
- Thêm input mới (kiểm index chưa dùng trước khi chọn:
  `grep -oP 'InputParameter\("[^"]*",\s*\K\d+' WyckoffRunner.cs | sort -n | uniq -d` phải rỗng sau khi sửa).
- Sửa `InDeadWindow` dùng giờ UTC.
- Sửa cả **comment sai** về việc nhánh reversal được miễn lọc (plan §2 mục "Việc kèm theo").
- Build lại bằng `./build-wyckoff.sh`, yêu cầu **0 warning / 0 error**.

### Bước 2 — chốt RR (§3) và Bước 3 — A/B lọc thanh khoản (§4)
Chạy đúng thí nghiệm plan mô tả, in bảng theo định dạng chuẩn, rồi **chốt giá trị mặc định** kèm lý do.
Nếu kết quả không đủ dứt khoát để chốt → ghi rõ "giữ nguyên mặc định cũ vì chưa đủ bằng chứng", đừng đổi bừa.

### Bước 4 — dọn code chết & comment sai ở nhánh QUAY_DAU (§6)
Đã chứng minh: `RevApproachBars` là tautology (sweep 1→999 đều ra đúng 27 tín hiệu), `Cooldown` và `SlCapPts`
không ràng buộc, và comment nói `AbsDom` "nâng grade A" là **sai** (grade chỉ do `Cluster` đặt).
Trước khi xoá/sửa bất cứ gì: **tự chạy lại phép kiểm** để tự xác nhận, đừng tin plan mù quáng. Dán output.

### Bước 5 — dọn tài liệu sai
- Docstring nào ghi "148 lệnh" → số thật là **140**, sửa.
- `research/imp_reversal_sweep.py` dòng 7–8: nhận định về múi giờ **sai** → sửa theo sự thật (cột là UTC).
- `research/reversal_vwap.py`: ghi chú rõ đây là **prototype cũ**, không phải engine chuẩn.
- Header comment của `WyckoffRunner.cs` vẫn là text v5 → cập nhật cho đúng v6.
- Thêm một mục v6 vào `quantower-entry-signal/README.md`.

### Bước 6 — BREAK SẠCH cho nhánh QUAY_DAU (§7)
Đây là **đòn bẩy lớn nhất còn lại** và **chưa test**. Cơ chế có thể **ngược dấu** so với CBR (với setup đảo
chiều, có cú quét hụt trước đó có thể lại là dấu hiệu TỐT). Vì vậy:
- Test **cả hai chiều**: yêu cầu "sạch" và yêu cầu "có quét ngược".
- Trình **cả hai phía của phân hoạch**. Nếu nhóm bị loại KHÔNG tệ hơn rõ ràng → bộ lọc là nhiễu, **không áp**.
- Nếu ngược dấu → đó là cơ sở để **định tuyến nhánh** (CBR cần sạch, QUAY_DAU cần bẩn) — ghi lại kết luận này
  vào `BASELINE.md`, nó là input quan trọng cho GĐ4/GĐ6.

### Bước 7 — viết `research/wyckoff/BASELINE.md`
Đóng băng baseline để mọi pha sau so sánh:
- Bảng số **chuẩn** của từng nhánh (CBR, QUAY_DAU) và **portfolio gộp (1 vị thế tại một thời điểm)**,
  theo định dạng cố định:
  ```
  tag                          n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | 05:+N.N 06:+N.N 07:+N.N ✓/✗ | nua1 +N.NR(nNN) nua2 +N.NR(nNN)
  ```
- **Lệnh chính xác để tái lập** từng dòng (file + hàm + config), theo tinh thần §12 của plan.
- **Cấu hình mặc định đã chốt** sau GĐ5 (RR bao nhiêu, lọc thanh khoản bật/tắt, khung giờ chết ra sao).
- Mục **"số cũ đã lỗi thời"**: nêu rõ mọi số trích trước 2026-07-29 là stale (do 3 lỗi parity: trend tol=0,
  `avg_vma` look-ahead toàn chuỗi, gate áp ở nến phá thay vì nến vào).
- Mục **giới hạn** (copy tinh thần §11): cửa sổ 5–7/2026, dxFeed là proxy yếu, chưa mô hình spread/slippage,
  giả định SL trước TP trong cùng nến.

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **TUYỆT ĐỐI không bịa số.** Mọi con số là output thật của lệnh vừa chạy, dán kèm.
3. Trước khi gọi `cbr_v6.scan(...)`: **luôn** `V.prepare(B)` (thiếu → `KeyError: 'liqratio'`).
4. `n < 25` → ghi **"không kết luận"**, không gọi là cải thiện. Mọi bộ lọc phải trình **cả hai phía phân hoạch**.
5. Không thêm bộ lọc mới ngoài phạm vi plan. Muốn thêm → ghi vào mục "đề xuất cho GĐ4/GĐ6", không tự áp.
6. Repo **PUBLIC**: không hardcode token/chat_id.
7. Không publish lên Claude Artifacts.
8. Xong → **commit + push `origin main`**.
9. Trung thực: bước nào không làm được phải nói rõ lý do.

## Quy tắc DỪNG (chuyển lên Opus xhigh)

- Kết quả bước 6 (BREAK SẠCH cho QUAY_DAU) làm WR nhảy **>10 điểm** hoặc `n` tụt **>40%** → dừng, cần soi cơ chế.
- Phát hiện thêm lỗi parity/look-ahead trong `cbr_v6.py` → dừng, đây là loại lỗi đã từng làm sai toàn bộ số liệu.
- Số C# sau khi sửa khung giờ **không khớp** hướng mà Python dự đoán → dừng, là vấn đề parity.

## Xong khi nào

- [ ] `WyckoffRunner.cs` sửa xong khung giờ, build `./build-wyckoff.sh` → **0 warning / 0 error**, index `InputParameter` không trùng
- [ ] Bước 2, 3 đã chạy, có bảng số thật, đã chốt mặc định kèm lý do
- [ ] Code chết / comment sai ở nhánh QUAY_DAU đã dọn, **có output tự xác nhận** trước khi xoá
- [ ] Tài liệu sai đã sửa (148→140, múi giờ `imp_reversal_sweep.py`, nhãn prototype, header v5→v6, README)
- [ ] Bước 6 đã test **cả hai chiều** và có kết luận rõ ràng
- [ ] `BASELINE.md` có bảng chuẩn 3 dòng (CBR / QUAY_DAU / portfolio) + lệnh tái lập + mặc định đã chốt + giới hạn
- [ ] Đã commit + push

Cuối lượt báo: bảng baseline, mặc định đã chốt, kết luận BREAK SẠCH cho nhánh QUAY_DAU (cùng dấu hay ngược dấu), và việc nào chưa làm.
