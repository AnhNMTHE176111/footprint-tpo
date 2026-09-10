"""STACKED IMBALANCE theo CAU TRUC SONG (khong dem nen) — 2,5 thang gan nhat.

Nguoi hoc: "khong ai dem duoc nen ca" -> phai mo ta boi canh bang thu NHIN THAY DUOC:
truoc nen tin hieu co MOVE khong, move dai bao nhieu GIA, gia dang HOI lai bao nhieu PHAN TRAM
cua move do, hay dang PHA dinh/day cua move truoc.

Cach lam: dung zigzag (nguong dao chieu tinh bang GIA, mac dinh 2,0 gia = 20 tick) de tim
dinh/day dao dong — dung cach mat nguoi nhin. Tai moi nen tin hieu, chi dung du lieu DEN nen do
(nhan qua), phan loai boi canh thanh 4 nhom mo ta duoc bang loi:

  A. TRONG NHIP HOI cua mot move CUNG CHIEU  (move da xong, gia dang hoi nguoc lai)
     -> chia tiep: hoi NONG (<33% move) / VUA (33-66%) / SAU (>66%)
  B. DANG CHAY CUNG CHIEU, chua hoi        (gia dang o gan cuc tri cua leg dang chay)
     -> chia tiep theo leg da di duoc bao nhieu % so voi move truoc: ngan / dai
  C. VUA PHA cuc tri cua move NGUOC truoc do (breakout)
  D. Chua co cau truc ro (chua du 2 dinh/day)

Chay: python research/stack-imb-cau-truc.py [nguong_gia] [YYYY-MM-DD]
      vd: python research/stack-imb-cau-truc.py 2.0 2026-06-01
"""
import os
import sys
import csv
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.path.join(ROOT, "data-export/data-footprint/fp_GC_XCEC_Time_20240801-20260819_748d9h_bars.csv")
FEATS = os.path.join(ROOT, "research/stack_imb_feats.csv")

RUN, HORIZON = 3, 20
MAX_JUMP, MAX_GAP_MIN = 20.0, 5.0
TH = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
DATE_FROM = datetime.strptime(sys.argv[2] if len(sys.argv) > 2 else "2026-06-01", "%Y-%m-%d")


def session_key(t):
    return (t + timedelta(hours=2)).date()


def load():
    rows = []
    with open(BARS, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append({"i": int(r["bar_idx"]),
                         "t": datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S"),
                         "o": float(r["open"]), "h": float(r["high"]),
                         "l": float(r["low"]), "c": float(r["close"])})
    rows.sort(key=lambda x: x["i"])
    feats = {}
    with open(FEATS, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["ready"] == "1":
                feats[int(r["bar_idx"])] = (int(r["s_ge"]), int(r["b_ge"]))
    bad, prev = set(), None
    for r in rows:
        if prev is not None and abs(r["c"] - prev) > MAX_JUMP:
            bad.add(session_key(r["t"]))
        prev = r["c"]
    bad |= {k + timedelta(days=1) for k in bad} | {k - timedelta(days=1) for k in bad}
    return rows, feats, bad


def zigzag_state(rows):
    """Chay zigzag NHAN QUA. Tra ve, cho tung nen: (chieu leg dang chay, cuc tri leg dang chay,
    gia pivot cuoi da xac nhan, gia pivot truoc do). None neu chua du cau truc."""
    out = [None] * len(rows)
    direction = 1
    ext = rows[0]["h"]
    piv = []          # danh sach gia pivot da xac nhan
    for i, r in enumerate(rows):
        if direction > 0:
            if r["h"] > ext:
                ext = r["h"]
            elif ext - r["l"] >= TH:
                piv.append(ext)
                direction = -1
                ext = r["l"]
        else:
            if r["l"] < ext:
                ext = r["l"]
            elif r["h"] - ext >= TH:
                piv.append(ext)
                direction = 1
                ext = r["h"]
        out[i] = (direction, ext, piv[-1] if piv else None, piv[-2] if len(piv) > 1 else None)
    return out


def phan_loai(state, c, sgn):
    """Mo ta boi canh truoc nen tin hieu bang loi. Tra ve (nhom, chi tiet)."""
    direction, ext, p1, p2 = state
    if p1 is None or p2 is None:
        return "D. chua co cau truc ro", ""
    move = abs(p1 - p2)                       # do lon move da xong gan nhat (gia)
    if move < 1e-9:
        return "D. chua co cau truc ro", ""
    move_dir = 1 if p1 > p2 else -1           # chieu cua move da xong

    if direction == -sgn:
        # leg dang chay NGUOC chieu tin hieu => dang la nhip hoi
        if move_dir == sgn:
            # move da xong CUNG chieu tin hieu -> dung kich ban "hoi lai roi di tiep"
            sau = abs(p1 - c) / move
            muc = "hoi NONG <33%" if sau < 0.33 else ("hoi VUA 33-66%" if sau < 0.66 else "hoi SAU >66%")
            return "A. trong nhip hoi cua move cung chieu", muc
        return "E. nhip hoi cua move nguoc chieu", ""
    # leg dang chay CUNG chieu tin hieu
    da_di = abs(c - p1) / move
    if move_dir == -sgn and abs(c - p2) > 1e-9 and ((c > p2) if sgn > 0 else (c < p2)):
        return "C. vua pha cuc tri cua move nguoc truoc", ""
    xa = abs(ext - c) / max(abs(ext - p1), 1e-9)
    vi_tri = "sat cuc tri leg" if xa < 0.25 else "da lui khoi cuc tri leg"
    manh = "leg da di >= move truoc" if da_di >= 1.0 else "leg con ngan hon move truoc"
    return "B. dang chay cung chieu, chua hoi xong", vi_tri + " · " + manh


def fwd(rows, i):
    pt, pc, c0 = rows[i]["t"], rows[i]["c"], rows[i]["c"]
    for j in range(i + 1, i + HORIZON + 1):
        if j >= len(rows):
            return None
        t, c = rows[j]["t"], rows[j]["c"]
        if abs(c - pc) > MAX_JUMP or (t - pt).total_seconds() / 60.0 > MAX_GAP_MIN:
            return None
        pt, pc = t, c
    return pc - c0


def main():
    rows, feats, bad = load()
    states = zigzag_state(rows)
    dem = {}
    tong = {"MUA": [0, 0], "BAN": [0, 0]}
    for i in range(1, len(rows) - HORIZON - 1):
        r = rows[i]
        if r["t"] < DATE_FROM or session_key(r["t"]) in bad:
            continue
        f = feats.get(r["i"])
        if f is None:
            continue
        for sgn, ten in ((1, "MUA"), (-1, "BAN")):
            if (f[1] if sgn > 0 else f[0]) < RUN:
                continue
            d = fwd(rows, i)
            if d is None or d == 0:
                continue
            nhom, chi_tiet = phan_loai(states[i], r["c"], sgn)
            thang = d * sgn > 0
            key = (ten, nhom, chi_tiet)
            if key not in dem:
                dem[key] = [0, 0]
            dem[key][0 if thang else 1] += 1
            tong[ten][0 if thang else 1] += 1

    print("Nguong dao chieu zigzag: %.1f gia | tu %s" % (TH, DATE_FROM.date()))
    for ten in ("MUA", "BAN"):
        w, l = tong[ten]
        print("\n" + "=" * 96)
        print("%s DON — %d ca | THANG %d | THUA %d  (%.1f%%)" % (ten, w + l, w, l, 100.0 * w / max(w + l, 1)))
        print("=" * 96)
        rws = [(k[1], k[2], v) for k, v in dem.items() if k[0] == ten]
        rws.sort(key=lambda x: (x[0], -(x[2][0] + x[2][1])))
        for nhom, ct, v in rws:
            s = v[0] + v[1]
            print("  %-44s %-34s %3d ca | thang %3d thua %3d = %4.1f%%"
                  % (nhom, ct, s, v[0], v[1], 100.0 * v[0] / max(s, 1)))


if __name__ == "__main__":
    main()
