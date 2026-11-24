"""Cửa sổ lịch sử dùng chung cho chấm và Big Trade: số nến ĐÃ ĐÓNG làm nền, theo số phút của một nến.
N = min(20, max(5, round(120 / phút)))  ->  M1 20 · M5 20 · M10 12 · M15 8 · M30 5 · H1 5 · H4 5.  round = làm tròn nửa lên."""
import numpy as np
WINDOW_MINUTES = 120
def nbase(minutes, win=WINDOW_MINUTES):
    if not (minutes > 0): return 20                    # nến không theo thời gian (tick, range...) -> 20
    return int(min(20, max(5, np.floor(win / minutes + 0.5))))
