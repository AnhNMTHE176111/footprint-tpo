# Kho ghi hình buổi học Meet với CORVEN — NGUỒN DỮ LIỆU CHÍNH

> Người học chốt 2026-11-07: *"ghi chép đầy đủ làm nguồn data chính… sau này cứ dựa vào nguồn data
> đấy để chắt lọc thông tin, tóm tắt"*. ⇒ Mọi tóm tắt / rút luật từ buổi học Meet phải **trích từ
> đây, kèm mốc giờ**, không viết theo trí nhớ.

## Cấu trúc mỗi buổi: `corven-meet/YYYY-MM-DD/`
| File | Nội dung | Ghi chú |
|---|---|---|
| `README.md` | thông tin buổi: giờ, người dạy, chart đang chia sẻ, danh sách video gốc | |
| `transcript-raw/partNN.txt` | bản chép lời **máy** (faster-whisper `medium`), mỗi dòng `[h:mm:ss] câu` | **không sửa tay** — giữ làm bản gốc |
| `transcript.md` | bản đã soát: gộp các part, sửa thuật ngữ máy nghe nhầm, chèn link ảnh | dùng bản này để đọc / tóm tắt |
| `frames/hh-mm-ss.jpg` | ảnh chọn lọc tại mốc thầy vẽ / chỉ chart | mốc giờ = giờ trong buổi (0:00 = đầu video 1) |

Mốc giờ `[h:mm:ss]` tính **liên tục từ đầu video đầu tiên** (mỗi video Bandicam dài 10 phút ⇒ part N bắt đầu ở (N−1)×10 phút).

## Dữ liệu gốc (KHÔNG commit — quá nặng)
- Video: `D:\record_video\bandicam *.mp4`
- Âm thanh 16 kHz mono: `D:\record_video\_extract\audio\partNN.wav`
- Toàn bộ ảnh cắt theo thay đổi màn hình: `D:\record_video\_extract\frames\pNN_<số khung>.jpg`
  (số khung ÷ 30 = giây trong part đó)

## Cách trích lại (nếu cần)
- Tiếng: `faster-whisper` model `medium`, `language="vi"`, `beam_size=5`,
  `condition_on_previous_text=False`, **KHÔNG** dùng `vad_filter` và **KHÔNG** dùng `initial_prompt`
  — hai tuỳ chọn đó làm máy bịa câu kiểu "hãy đăng ký kênh" (đã thử 2026-11-07).
- Ảnh: `ffmpeg -vf "select='gt(scene,0.02)+not(mod(n\,1800))'" -vsync vfr -frame_pts 1`.

## Thuật ngữ máy hay nghe nhầm (cập nhật dần)
| Máy ghi | Đúng là |
|---|---|
| Stomp hẳn / Stompean | stop hunt |
| quét L / đặt L | quét SL / đặt SL (dừng lỗ) |
| bi-stop | buy-stop |
| nổ bóng | nổ bóng (bong bóng volume trên chart) — giữ nguyên |

## Danh sách buổi
- [2026-11-07](2026-11-07/README.md) — ~82 phút, chart BTCUSD 30m (TradingView), stop hunt / range / breakout
