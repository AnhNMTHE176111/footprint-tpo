"""Sinh pickle khung M15, M30, H1 cho GC và NQ (dùng load.build)."""
import load
for s in ('GC', 'NQ'):
    for m in (15, 30, 60): load.build(s, m)
