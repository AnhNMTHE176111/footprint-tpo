# 3 prompt đổi tầng vùng theo CORVEN — hướng dẫn dùng

Lập 2026-08-01. Mục đích: chạy **3 session Claude song song**, mỗi session lo **một** signal,
đổi tầng neo vùng từ "7 loại vùng theo phiên" sang **đúng bộ vùng CORVEN dùng**
(HVN tuần/ngày + VWAP tuần/ngày), rồi loop test → cải thiện → báo bảng TRƯỚC/SAU/Δ.

| Session | Prompt | File signal sở hữu | Thư mục research sở hữu |
|---|---|---|---|
| 1 | [PROMPT-1-entry-signal.md](PROMPT-1-entry-signal.md) | `quantower-entry-signal/EntrySignal.cs` | `research/wyckoff/v8/entry/` |
| 2 | [PROMPT-2-runner-signal.md](PROMPT-2-runner-signal.md) | `quantower-entry-signal/RunnerSignal.cs` | `research/wyckoff/v8/runner/` |
| 3 | [PROMPT-3-wyckoff-runner.md](PROMPT-3-wyckoff-runner.md) | `quantower-entry-signal/WyckoffRunner.cs` | `research/wyckoff/v8/wyckoff/` |

## Cách dùng

1. Mở 3 session Claude Code trong repo này (3 tab/3 cửa sổ, **cùng thư mục** `footprint-tpo`).
2. Dán **toàn bộ nội dung** một file prompt vào một session. Không trộn 2 prompt vào 1 session.
3. Để cả 3 chạy. Mỗi session tự commit + push lên `main`, chỉ những file của nó.

Session 3 (`WyckoffRunner`) là nhánh có nhiều việc nhất — nó thực thi phần chính của
`PLAN_KB_ABC.md`. Nếu chỉ muốn chạy **một** session thì chạy session 3.

## Vì sao cả 3 đi chung nhánh `main` chứ không mỗi session một nhánh

3 session dùng **chung một working tree**. `git checkout -b` đổi file dưới chân 2 session kia →
số liệu đang đo bị đổi giữa lúc chạy. Nên: chung `main`, **file rời nhau**, và
`git pull --rebase --autostash origin main` trước khi push. Vì file rời nhau, rebase phải sạch;
nếu đụng độ nghĩa là có session vượt quyền ghi.

## Ranh giới quyền ghi (bắt buộc, để 3 session không đạp nhau)

Mỗi prompt đã ghi rõ. Tóm lại:

- **Đọc được hết repo.** Ghi thì chỉ được ghi file thuộc quyền của mình + `dist/` DLL của mình.
- **Không bao giờ `git add -A` / `git add .`** — sẽ nuốt việc đang dở của session khác.
- `quantower-tpo-suite/` (kể cả `ProfileEngine.cs`, `SessionZones.cs`) = **READ-ONLY cho cả 3.**
  Việc cắt `SessionZones` về `CorvenMode` (PLAN_KB_ABC §3.3) **không** thuộc 3 session này — làm sau,
  bằng một lượt riêng, khi đã biết bộ vùng nào thật sự có giá trị.
- `research/wyckoff/v8/zones_corven.py` = **đóng băng cho cả 3.** Session 3 là chủ danh nghĩa, nhưng
  vì dùng chung thư mục nên sửa nó = đổi số của 2 session kia giữa lúc đo. Ai cần sửa thì copy sang
  thư mục riêng của mình.
- `cbr_v6.py`, `entry_month.py`, `entry_dxfeed.py`, `imp_reversal_sweep.py`, `v7/*` = **READ-ONLY cho
  cả 3.** Cần đổi thì copy → chứng minh bản copy tái lập đúng số gốc (GOLDEN) → rồi mới sửa bản copy.
- `RunnerSignal.cs` = **bản đang chạy LIVE.** Session 2 được sửa nhưng mọi thứ mới phải nằm sau cờ
  **mặc định TẮT**.

## Ba điểm quan trọng nhất trong cả 3 prompt

1. **Cột "TRƯỚC" phải do chính session đó ĐO LẠI bằng đúng harness dùng để đo cột "SAU".**
   Không được lấy số trong `BASELINE.md`/memory làm cột TRƯỚC — số cũ đo bằng pipeline khác, cột Δ sẽ
   vô nghĩa. Đây là lỗi dễ mắc nhất và nó phá toàn bộ giá trị của bài này.
2. **Đối chứng ngẫu nhiên là cổng chặn, không phải phần bonus.** Dịch vùng ±3 giá, 5 seed; chênh EV
   `< +0.10R` → KILL. Bài học `BACKTEST-ZONES-V2.md`: bộ vùng nghe rất hợp lý vẫn có thể không hơn
   ngẫu nhiên.
3. **Kết quả âm là kết quả.** Cả 3 prompt đều nói rõ: nếu vùng CORVEN làm signal tệ hơn thì báo thẳng
   kèm số, không đi tìm cấu hình thứ 11 để cứu kết luận.
