#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User: hinh dang + moc thoi gian 2 feed tuong tu, chi khac gia. Check tai MOC ~19:20 futures:
  1) co cau truc short (hoi lower-high sat truoc roi do) khong?
  2) neu short o 19:20-19:24, gia chay toi dau (bao nhieu R)? co toi 6R nhu CFD khong?
In: local-high ngay truoc cu do (de dat SL), entry, day thap nhat sau do + thoi diem, va R dat duoc
theo tung kieu SL. Keo dai sang 07/24 sang som.
"""
import sys
sys.path.insert(0, "/home/asl86/Documents/footprint-tpo/quantower-entry-signal/research")
import entry_month as em
TICK = em.TICK
B = em.load_m1()

# index cac moc
def at(day, hh, mm):
    return next((i for i, b in enumerate(B) if b['dt'].strftime('%m/%d') == day and b['dt'].hour == hh and b['dt'].minute == mm), None)

i1915 = at('07/23', 19, 15); i1920 = at('07/23', 19, 20); i1924 = at('07/23', 19, 24)

# local high ngay truoc 19:20 (nhip hoi gan nhat, 19:05-19:19) de dat SL kieu "ngoai nhip hoi"
seg_pull = B[at('07/23', 19, 5):i1920]
pull_hi = max(x['hi'] for x in seg_pull)
pull_hi_bar = max(seg_pull, key=lambda x: x['hi'])
print("=" * 92)
print(f"MOC 19:20 futures — cau truc short?")
print(f"  Nhip hoi 19:05-19:19: dinh cao nhat = {pull_hi:.1f} luc {pull_hi_bar['dt']:%H:%M}")
for tag, i in [("19:20", i1920), ("19:24 (impulse ban)", i1924)]:
    b = B[i]
    print(f"  {tag}: close {b['c']:.1f}  (SL 'ngoai dinh hoi' = {pull_hi:.1f}+0.2 = {pull_hi+0.2:.1f} -> risk {(pull_hi+0.2-b['c'])/TICK/10:.1f} gia)")

# do cu do: day thap nhat tu 19:20 den 07/24 12:00 + thoi diem
end = at('07/24', 12, 0) or len(B) - 1
after = B[i1920 + 1:end]
low = min(after, key=lambda x: x['lo'])
print(f"\n  Day THAP NHAT sau 19:20: {low['lo']:.1f} luc {low['dt']:%m/%d %H:%M}  (cach 19:20 {(i1920 - 0)}... {(after.index(low)+1)} nen ~ {(after.index(low)+1)/60:.1f}h)")

# R dat duoc theo 2 kieu SL, tinh 'khong bi quet SL truoc'
def max_R_before_sl(i_entry, entry, sl):
    """R lon nhat dat duoc (theo day) TRUOC khi cham SL. SHORT."""
    risk = sl - entry
    bestR = 0.0; hit_sl_at = None
    for j in range(i_entry + 1, end + 1):
        b = B[j]
        fav = (entry - b['lo']) / risk
        bestR = max(bestR, fav)
        if b['hi'] >= sl:
            hit_sl_at = B[j]['dt']; break
    return bestR, hit_sl_at

print(f"\n  Cu short chay bao nhieu R (truoc khi bi quet SL):")
for tag, i, slmode in [("19:20", i1920, 'pull'), ("19:20 SL 5.8 gia (nhu ban)", i1920, 5.8),
                       ("19:24", i1924, 'pull')]:
    b = B[i]; entry = b['c']
    sl = (pull_hi + 0.2) if slmode == 'pull' else entry + slmode
    risk = (sl - entry) / TICK / 10
    R, slat = max_R_before_sl(i, entry, sl)
    print(f"    {tag:<28}: entry {entry:.1f} SL {sl:.1f} (risk {risk:.1f} gia) -> max {R:.1f}R"
          + (f", SL bi quet luc {slat:%m/%d %H:%M}" if slat else ", KHONG bi quet"))
print("=" * 92)
