# GĐ10 — Deploy Windows + đối chiếu live với backtest

| | |
|---|---|
| **Model** | Sonnet 5 |
| **Effort** | medium |
| **Cần trước** | GĐ9 (parity ĐẠT hoặc đã có quy trình lấy CSV) |
| **Chi phí** | thấp mỗi lượt, nhưng lặp lại nhiều tuần |
| **Output** | `research/wyckoff/LIVE_LOG.md` (cập nhật dần) |

Pha này **lặp lại**: mỗi 1–2 tuần chạy lại cùng prompt này để đối chiếu thêm dữ liệu.
Đây cũng là pha duy nhất kiểm được những feature `SPEC §8` (chỉ chạy live).

---

=== PROMPT ===

Việc của bạn: hoàn tất việc đưa `WyckoffRunner.cs` v7 lên Quantower máy Windows, thu log tín hiệu thật, và **đối chiếu live với backtest**. Output: `quantower-entry-signal/research/wyckoff/LIVE_LOG.md` (append thêm mỗi lần chạy, không ghi đè).

## Đọc trước

1. `research/wyckoff/PARITY_V7.md` — parity đạt chưa, còn thiếu gì
2. `research/wyckoff/AUDIT_V7.md` — mục "cấu hình đóng băng" và "những gì audit không kiểm được"
3. `research/wyckoff/RESULTS_KB12.md`, `RESULTS_KB3.md` — số backtest để so
4. `LIVE_LOG.md` nếu đã tồn tại — biết đã đối chiếu tới đâu

## Việc phải làm

### 1. Hoàn tất parity nếu còn treo
Nếu `PARITY_V7.md` ghi **CHƯA ĐẠT** vì thiếu CSV từ máy Windows:
- Hướng dẫn người dùng lấy CSV (đúng tên file, đúng thư mục, đúng khoảng thời gian).
- Chạy `research/wyckoff/parity_v7.py`, cập nhật `PARITY_V7.md` thành ĐẠT/CHƯA ĐẠT với bảng thật.
- **Parity chưa đạt thì chưa được coi tín hiệu live là bằng chứng về chiến lược** — lúc đó mọi lệch nhau đều
  có thể do port sai, không phải do chiến lược. Nói rõ điều này.

### 2. Checklist deploy (hướng dẫn người dùng, từng bước)
- Copy `dist/WyckoffRunner.dll` sang thư mục indicator của Quantower trên Windows.
- Cấu hình input **đúng cấu hình đóng băng** — in ra bảng `tên input → giá trị` để người dùng đối chiếu tay.
- Telegram: token/chat_id **để người dùng tự điền**, tuyệt đối không hardcode vào repo (repo public).
- Bật chế độ dry-run trước (nếu có) để xác nhận không gửi lệnh thật ngoài ý muốn.
- Xác nhận múi giờ hiển thị của Quantower vs UTC — nhắc lại rằng mọi logic tính theo **UTC**.

### 3. Đối chiếu live ↔ backtest
Với CSV tín hiệu live thu được:
- Bảng theo định dạng cố định, tách theo kịch bản và **portfolio gộp**:
  ```
  tag                          n=NNN WR=NN.N% tong=+NN.NR EV=+N.NNN MDD=NN.NR | <từng tháng> ✓/✗
  ```
- So với số backtest tương ứng. Ghi **chênh lệch**, đừng làm mịn.
- `n` live nhỏ (thường < 15 trong 2 tuần) → **ghi rõ "không kết luận"**. Đây là điều quan trọng nhất của pha
  này: đừng kết luận sớm từ 5 lệnh.
- Tình huống phải soi riêng: tín hiệu live mà backtest không có, và ngược lại → mỗi ca ghi thời gian + nguyên
  nhân nghi ngờ.

### 4. Ghi nhận cái chỉ live mới thấy
- **Spread và slippage thực tế** trên vàng ở khung giờ vào lệnh → so với độ nhạy chi phí đã đo ở `AUDIT_V7.md`
  mục H. Nếu chi phí thực vượt ngưỡng mà edge sống được → **báo động, phải nói ngay**.
- Feature `SPEC §8` (per-level footprint, DOM, lệnh lớn): giờ đã có dữ liệu live → ghi quan sát định tính,
  chưa kết luận.
- Trượt giá khi vào lệnh, tín hiệu bị bỏ vì đang có vị thế, tín hiệu trùng nhau.

### 5. Cập nhật `LIVE_LOG.md`
Append một mục mới mỗi lần chạy:
```
## <ngày> — đối chiếu tuần thứ N
- Khoảng dữ liệu live: ...
- Bảng số live vs backtest: ...
- n = ... → kết luận được / không kết luận
- Ca lệch (live có, backtest không / ngược lại): ...
- Spread/slippage quan sát được: ...
- Việc cần làm tiếp: ...
```

## LUẬT CHUNG

1. Trả lời **tiếng Việt**. Mọi file nhắc đến phải có **link Markdown**.
2. **TUYỆT ĐỐI không bịa số.** Chưa có CSV live → nói chưa có, không suy đoán kết quả.
3. `n < 25` → **"không kết luận"**. Với live, `n` sẽ nhỏ rất lâu — kiên nhẫn, đừng kết luận sớm.
4. Repo **PUBLIC**: token/chat_id **người dùng tự điền tay**, không commit.
5. Không publish lên Claude Artifacts.
6. Xong → **commit + push `origin main`** (commit `LIVE_LOG.md`, không commit CSV live nếu > 5MB).
7. Trung thực: chưa deploy được / chưa đủ dữ liệu thì nói thẳng.

## Xong khi nào (cho mỗi lượt chạy)

- [ ] Parity đã ĐẠT, hoặc ghi rõ còn thiếu gì và hệ quả
- [ ] Có bảng input đóng băng để người dùng đối chiếu tay
- [ ] Có bảng live vs backtest (hoặc ghi rõ chưa có dữ liệu)
- [ ] Đã ghi nhận spread/slippage thực tế và so với ngưỡng chịu đựng ở `AUDIT_V7.md`
- [ ] `LIVE_LOG.md` có mục mới cho lượt này
- [ ] Đã commit + push

Cuối lượt báo: live so backtest thế nào, `n` đã đủ kết luận chưa, spread thực tế có ăn hết edge không, và việc cần làm tiếp.
