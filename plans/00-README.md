# WyckoffRunner v7 — 3 kịch bản · BỘ PROMPT THEO GIAI ĐOẠN

Mục tiêu cuối: nâng `WyckoffRunner.cs` từ v6 (1 nhánh CBR + 1 nhánh quay đầu) lên **v7 = 3 kịch bản**,
có tầng bias phiên (TPO/VWAP/Wyckoff) và tầng đo lực (footprint/delta/VSA/hình nến).

Mỗi file `GDn-*.md` là **một prompt độc lập, dán nguyên vào phiên mới**. Phần meta ở đầu file cho biết
chọn model/effort nào; phần sau dòng `=== PROMPT ===` là nội dung dán.

---

## Bảng giai đoạn

| GĐ | Việc | Model | Effort | Cần trước | Output chính |
|---:|------|-------|--------|-----------|--------------|
| 0 | Trích xuất cơ học PDF/PPTX → text + ảnh | Sonnet 5 | low | — | `data-export/wyckoff/extracted/` + `EXTRACT_REPORT.md` |
| 1 | Chưng cất lý thuyết phần 1–12 | Sonnet 5 | medium | 0 | `data-export/wyckoff/THEORY.md`, `WYCKOFF_RULES.md` |
| 2 | Chưng cất journal 153 slide chart | Sonnet 5 | medium | 0 | `data-export/wyckoff/CHART_CASES.md` |
| 3 | Kiểm kê năng lực dữ liệu | Sonnet 5 | high | — | `quantower-entry-signal/research/DATA_CAPABILITY.md` |
| 4 | **THIẾT KẾ đặc tả 3 kịch bản** ⭐ | **Opus 5** | **xhigh** | 1,2,3 | `quantower-entry-signal/SPEC_V7_3KB.md` |
| 5 | Dọn nợ v6 + chốt baseline | Sonnet 5 | medium | — | v6 done + `research/wyckoff/BASELINE.md` |
| 6 | Implement + test KB1, KB2 | Sonnet 5 | high | 4,5 | `research/wyckoff/v7/` + `RESULTS_KB12.md` |
| 7 | Implement + test KB3 (mới) | Sonnet 5 | high | 4,5 | `RESULTS_KB3.md` |
| 8 | **Audit chống overfit / look-ahead** 🚦 | **Opus 5** | **xhigh** | 6,7 | `AUDIT_V7.md` (cổng chặn) |
| 9 | Port sang C# + kiểm parity | Opus 5 | high | 8 PASS | `WyckoffRunner.cs` v7 + `PARITY_V7.md` |
| 10 | Deploy Windows + đối chiếu live | Sonnet 5 | medium | 9 | `research/wyckoff/LIVE_LOG.md` |

## Thứ tự & song song

```
GĐ0 ──┬─> GĐ1 ─┐
      └─> GĐ2 ─┤
GĐ3 ───────────┴─> GĐ4 (Opus xhigh) ─┬─> GĐ6 ─┐
GĐ5 (chạy song song bất kỳ lúc nào) ─┘        ├─> GĐ8 (cổng) ─> GĐ9 ─> GĐ10
                                     └─> GĐ7 ─┘
```

- GĐ0 → 1,2: bắt buộc tuần tự (1,2 cần file đã trích xuất).
- GĐ3 và GĐ5 độc lập, chạy lúc nào cũng được, nhưng **GĐ5 phải xong trước GĐ6/GĐ7** vì nó chốt baseline để so.
- GĐ8 là **cổng chặn**: FAIL thì quay lại GĐ6/GĐ7, không được port sang C#.

## Vì sao chia thế này

- **Việc đọc tách khỏi việc nghĩ.** 623 trang + 188 slide không nhét được vào 1 context, và cũng không
  đáng cho Opus xhigh đọc raw. GĐ0–2 là trích xuất/chưng cất — Sonnet làm tốt và rẻ.
- **Chỉ 1 pha thiết kế đắt.** GĐ4 nhận toàn bộ bản chưng cất + năng lực dữ liệu, nhả ra đặc tả có
  **ngưỡng PASS/KILL bằng số**. Có ngưỡng số thì GĐ6–7 mới chạy được ở effort thấp mà không tự diễn giải kết quả.
- **Có cổng audit trước khi port.** Ngày 2026-07-29 đã có 3 lỗi parity (look-ahead `avg_vma`, trend tol=0,
  gate áp sai nến) tự sinh ra trong engine backtest. Effort thấp sẽ tái tạo loại lỗi này → phải có 1 pha
  Opus xhigh soi riêng, trước khi số liệu đi vào code live.
- **Parity C#↔Python cần effort cao.** Đây là chỗ lỗi im lặng nhất: Python nói WR 58%, C# bắn tín hiệu khác.

## Quy tắc leo thang (áp cho GĐ6, GĐ7)

DỪNG và chuyển sang Opus xhigh khi gặp bất kỳ điều nào:
1. WR nhảy **>10 điểm** hoặc `n` tụt **>40%** sau một thay đổi → nghi overfit/look-ahead, cần soi cơ chế.
2. Phải **đổi định nghĩa** một feature (không chỉ đổi tham số) so với `SPEC_V7_3KB.md`.
3. Kết quả **trái ngược** đặc tả (ví dụ KB3 âm ở cả 3 tháng) → cần quyết định giữ/bỏ, không phải tinh chỉnh.
4. Có tháng âm mà cách sửa duy nhất nghĩ ra được là thêm tham số.

## LUẬT CHUNG (đã nhúng trong từng prompt, ghi lại ở đây cho tiện tra)

1. Trả lời **tiếng Việt**. Mọi file/ảnh nhắc đến phải có **link Markdown** ngay tại chỗ nhắc.
2. **TUYỆT ĐỐI không bịa số.** Mọi con số phải là output thật của lệnh vừa chạy, dán kèm output. Chưa đo → ghi "chưa đo".
3. Đọc `WYCKOFF_V6_PLAN.md` **§9 (giả thuyết đã bị bác)** trước khi đề xuất — đừng làm lại việc đã chết.
4. Repo **PUBLIC**: không hardcode token/chat_id. Không commit **ảnh render** sinh ra từ trích xuất, và không
   commit 83MB ảnh chat gốc (`data-export/messages-with-pro-trader/Message with pro trader-.../` — đang untracked,
   cố ý). Lưu ý: 79MB PDF/PPTX Wyckoff **đã được người dùng commit** ở `15be47d` — đừng tự gỡ khỏi tracking.
5. **Không** publish bất cứ gì lên Claude Artifacts.
6. Xong việc → **commit + push `origin main`**, message tiếng Việt.
7. Báo cáo trung thực: phần nào chưa làm / không làm được phải nói rõ, không im lặng thu hẹp phạm vi.
8. Trước khi gọi `cbr_v6.scan(...)`: **luôn** `V.prepare(B)` (thiếu → `KeyError: 'liqratio'`).

## Định dạng báo cáo kết quả CỐ ĐỊNH (GĐ5–8 đều dùng)

```
tag                          n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | 05:+N.N 06:+N.N 07:+N.N ✓/✗ | nua1 +N.NR(nNN) nua2 +N.NR(nNN)
```

Chuẩn tối thiểu để được kết luận:
- `n < 25` → ghi **"không kết luận"**, không được gọi là cải thiện.
- Mọi bộ lọc phải trình **cả hai phía của phân hoạch** (nhóm bị lọc bỏ tệ hơn rõ ràng), không chỉ nhóm đẹp.
- Tháng âm bất kỳ → phải nói ra, không được gộp vào tổng cho đẹp.
- Số portfolio (gộp 3 KB, **1 vị thế tại một thời điểm**) mới là số cuối; số riêng từng KB chỉ để chẩn đoán.

## Bối cảnh gốc (yêu cầu của người học, giữ nguyên văn)

> Kịch bản 1: Vẫn là entry là phá range chờ hồi và vào — đây sẽ là setup mạnh của ta.
> Kịch bản 2: Giá chạm vùng rồi phản ứng (như cũ).
> Kịch bản 3: Dựa theo wyckoff, ta xác định được swing low và swing high, tức là 2 biên cùng vùng nén,
> nếu nó va chạm ở 2 cạnh đồng thời xác nhận bằng các delta footprint thì ta có thể scalp ngắn từ biên này
> sang biên còn lại, trade trong range luôn. Thường swing low và high cũng sẽ hợp lưu với vùng nào đó thì
> nó cũng mạnh, và giá cũng sẽ chạy lên xuống trong range đó 1 thời gian nhất định rồi sẽ phá mạnh ra và
> tạo thành 1 xu hướng (tại đây thì lại dùng kịch bản 1 là trade tiếp).
>
> Target vẫn sẽ cải tiến 3 setup đó, và sẽ kết hợp nhiều yếu tố lại với nhau:
> - sử dụng tpo footprint vwap hay các vùng va chạm nhiều của wyckoff để vẽ range, vùng, bias của phiên trong ngày
> - sử dụng footprint, delta, bid, ask, độ dài nến, thân, râu, vsa vol để đoán lực mạnh hay yếu, hay đủ để xác nhận vào lệnh.
