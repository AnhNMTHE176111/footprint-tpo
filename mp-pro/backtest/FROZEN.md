# Cấu hình chốt TRƯỚC khi chạy TEST (2026-11-22, sau vòng 3)
Chọn ô GIỮA vùng dương trên TRAIN, không chọn ô đỉnh.
- LVN (sách p66-71): r2.lvn(hours=72, smooth=5, SLm=0.7, tf=5, min_rr=1.0). TRAIN: n=19, +0.79R.
- FAKE (sách p90-92): r2.fake(tf=5, va='dev', wick=0.6, SLbuf=0.1, tgt='poc'). TRAIN: n=48, +0.23R.
TEST = phiên từ 2026-10-12 đến 2026-11-09, chưa từng chạy.
