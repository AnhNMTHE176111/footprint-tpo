# GĐ6 — Implement + test KB1 (phá→hồi) và KB2 (chạm vùng→phản ứng)

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | high |
| **Cần trước** | GĐ4 (`SPEC_V7_3KB.md`), GĐ5 (`BASELINE.md`) |
| **Chi phí** | trung bình–cao (vòng lặp sweep) |
| **Output** | `research/wyckoff/v7/` + `research/wyckoff/RESULTS_KB12.md` |

Effort `high` chứ không `medium`: có sửa engine (tầng bias + tầng đo lực) nên rủi ro look-ahead thật.

---

=== PROMPT ===

Việc của bạn: implement và test **KB1** (phá range → chờ hồi → vào) và **KB2** (giá chạm vùng → phản ứng) theo đúng đặc tả, trên Python trước (chưa port C#). Output: package `research/wyckoff/v7/` + báo cáo `research/wyckoff/RESULTS_KB12.md`.

Bạn **thi công theo đặc tả**, không thiết kế lại. Gặp chỗ đặc tả thiếu/mâu thuẫn → ghi vào mục "cần quyết" của báo cáo và chọn phương án đơn giản nhất, **nói rõ đã chọn gì**, đừng im lặng tự sáng tạo.

## Đọc trước — chỉ những chỗ này

1. `quantower-entry-signal/SPEC_V7_3KB.md` — **§1 (quy ước), §2 (tầng bias), §3 (tầng đo lực), §4 (KB1),
   §5 (KB2), §7 (giả thuyết xếp hạng), §8 (không kiểm được offline), §9 (rủi ro overfit)**
2. `quantower-entry-signal/research/wyckoff/BASELINE.md` — số phải so với cái này
3. `quantower-entry-signal/research/wyckoff/cbr_v6.py` — engine baseline
4. `quantower-entry-signal/research/DATA_CAPABILITY.md` — mục **"hạ tầng còn thiếu"** (loader cần viết) và
   **"không kiểm được offline"**
5. `quantower-entry-signal/WYCKOFF_V6_PLAN.md` **§9** — 5 giả thuyết đã bị dữ liệu bác, **đừng làm lại**

## Kiến trúc bắt buộc

```
research/wyckoff/v7/
  __init__.py
  loaders.py     # loader TPO daily/m30, fp-m1 (delta theo nến); theo API mô tả trong DATA_CAPABILITY
  features.py    # tầng bias phiên + tầng đo lực; MỖI hàm có docstring ghi rõ "chỉ dùng dữ liệu tới nến i"
  engine.py      # engine v7: run/evaluate/scan; hỗ trợ RR cố định VÀ TP theo mức giá (chuẩn bị cho KB3)
  report.py      # in bảng theo ĐÚNG định dạng cố định + mdd + phân tháng + chia đôi OOS + partition
  run_kb12.py    # script chạy các thí nghiệm của lượt này
```

- **KHÔNG sửa `cbr_v6.py`.** Nó là baseline đóng băng. `engine.py` được phép import từ nó.
- Mọi hàm feature: nhận `(B, i, ...)` và **chỉ đọc `B[:i+1]`**. Cấm thống kê toàn chuỗi
  (lỗi `avg_vma` tính `mean` cả file đã từng làm sai toàn bộ số liệu). Nếu cần trung bình dài → **trung bình
  trượt tính tiến dần** như `prepare()` trong `cbr_v6.py`.
- Mọi gate phải áp ở **nến vào lệnh**, không phải nến phá (lỗi này đã xảy ra).

## Bước 0 — GOLDEN TEST (làm trước tiên, không được bỏ)

Chạy `engine.py` với **toàn bộ feature mới TẮT** → phải **tái lập chính xác** các số trong `BASELINE.md`
(đúng `n`, đúng WR, đúng tổng R, đúng MDD).

- Khớp → ghi `GOLDEN OK` kèm output cả 2 bên.
- **Không khớp → DỪNG toàn bộ.** Không đi tiếp, không "chắc do làm tròn". Tìm nguyên nhân, và nếu không tìm
  được thì báo lại người dùng. Engine không tái lập được baseline thì mọi số sau đó vô nghĩa.

## Bước 1..N — thêm feature MỘT CÁI MỘT LẦN

Theo thứ tự ưu tiên ở `SPEC §7`. Với **mỗi** feature:

1. Implement + docstring ghi rõ dùng dữ liệu tới nến nào.
2. In bảng theo định dạng cố định:
   ```
   tag                          n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | 05:+N.N 06:+N.N 07:+N.N ✓/✗ | nua1 +N.NR(nNN) nua2 +N.NR(nNN)
   ```
3. **Partition test bắt buộc**: in cả **nhóm được nhận** và **nhóm bị loại**. Nhóm bị loại phải tệ hơn rõ ràng.
   Không rõ ràng → feature là nhiễu → **bỏ**, ghi vào mục "đã thử và bỏ".
4. Đối chiếu ngưỡng **PASS/KILL** trong `SPEC` → ghi `PASS` / `KILL` / `không kết luận (n<25)`.
5. Sweep tham số quanh mặc định để xem có **vùng bằng phẳng** hay chỉ có một điểm đẹp. Chỉ có một điểm đẹp
   → dấu hiệu overfit → ghi rõ, **không chọn làm mặc định**.
6. Chỉ giữ lại (stack) feature đã PASS rồi mới sang feature sau.

## Bắt buộc riêng cho lượt này

- **Tầng bias TPO phải chống look-ahead cẩn thận**: VA/POC/IB của **phiên đang chạy** chỉ biết được khi phiên
  kết thúc. Bias hôm nay chỉ được dùng VA/POC **phiên trước**, còn IB chỉ dùng được **sau khi IB đóng**. Ghi rõ
  trong docstring và kiểm bằng một test nhỏ (in timestamp dữ liệu dùng vs timestamp nến ra quyết định).
- **A/B: bias TPO thay thế hay cộng thêm proxy xu hướng `close` vs `close[-480]`?** In 4 dòng:
  chỉ proxy / chỉ TPO / cả hai (AND) / không cái nào. Đây là câu hỏi có giá trị cao, đừng bỏ.
- **Feature chỉ có trên fp-m1 (delta theo nến)**: chạy trên fp-m1 và ghi rõ số đó **không so trực tiếp** được
  với số dxFeed. Nếu có thể, chạy cùng config trên cả 2 bộ ở cửa sổ trùng để làm đối chứng.
- Feature nằm trong `SPEC §8` (không kiểm được offline) → **implement được nhưng mặc định TẮT**, và không
  tính vào kết quả.

## `RESULTS_KB12.md` phải có

1. `GOLDEN OK` + output đối chiếu
2. Bảng **tiến hoá theo bước**: mỗi dòng một bước stack, cột theo định dạng cố định, và cột `PASS/KILL`
3. Mục **partition** cho từng bộ lọc (cả hai phía)
4. Mục **sweep** cho từng tham số (có vùng bằng phẳng hay không)
5. Mục **"đã thử và bỏ"** — feature nào không qua, số liệu chứng minh, để pha sau đừng làm lại
6. Mục **A/B bias TPO vs proxy xu hướng** — 4 dòng + kết luận
7. **Cấu hình chốt** của KB1 và KB2 sau lượt này (dạng dict copy-paste được)
8. Mục **giới hạn** (cửa sổ 5–7/2026, dxFeed proxy yếu, chưa có spread/slippage, SL-trước-TP trong cùng nến)
9. Mục **"cần quyết"** — chỗ đặc tả thiếu và bạn đã chọn gì

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **TUYỆT ĐỐI không bịa số.** Mọi con số là output thật, dán kèm output.
3. `n < 25` → **"không kết luận"**, không gọi là cải thiện.
4. Trước khi gọi engine dựa trên `cbr_v6`: **luôn** `prepare(B)`.
5. Repo **PUBLIC**: không hardcode token. Không commit `__pycache__` (đã có trong `.gitignore`).
6. Không publish lên Claude Artifacts.
7. Xong → **commit + push `origin main`**.
8. Trung thực: bước nào bỏ, feature nào chưa test phải nói rõ.

## Quy tắc DỪNG (chuyển lên Opus xhigh)

1. GOLDEN TEST không khớp.
2. WR nhảy **>10 điểm** hoặc `n` tụt **>40%** sau một thay đổi.
3. Phải **đổi định nghĩa** feature so với `SPEC` (không chỉ đổi tham số).
4. Kết quả **trái ngược** đặc tả ở mức phải quyết giữ/bỏ kịch bản.
5. Cách duy nhất nghĩ ra để cứu một tháng âm là **thêm tham số**.

## Xong khi nào

- [ ] `GOLDEN OK` — engine v7 (feature tắt) tái lập chính xác `BASELINE.md`
- [ ] Mọi feature trong `SPEC §7` thuộc phạm vi KB1/KB2 đã test, mỗi cái có partition + sweep + phán quyết PASS/KILL
- [ ] Có A/B bias TPO vs proxy xu hướng (4 dòng)
- [ ] Có cấu hình chốt KB1, KB2 dạng copy-paste được
- [ ] `RESULTS_KB12.md` đủ 9 mục
- [ ] Đã commit + push

Cuối lượt báo: bảng tiến hoá theo bước, cấu hình chốt, **feature nào PASS / KILL**, và mọi chỗ đã phải tự quyết.
