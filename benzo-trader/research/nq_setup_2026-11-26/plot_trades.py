# -*- coding: utf-8 -*-
"""Vẽ từng lệnh để đối chiếu tay (SPEC 4.1): nến, chấm Ask/Bid, Big Trade, kiệt sức, vùng stacked, mốc, SL/TP."""
import os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from nq_setup import *

def plot(m, t, path):
    b = m.b; s = m.s
    a, z = max(0, t.sig - 45), min(len(b.t) - 1, max(t.exit_i, t.sig) + 8)
    fig, ax = plt.subplots(figsize=(14, 7))
    for k in range(a, z + 1):
        x = k - a; col = "#1e88e5" if b.c[k] >= b.o[k] else "#e53935"
        ax.plot([x, x], [b.l[k], b.h[k]], color=col, lw=0.8)
        ax.add_patch(Rectangle((x - 0.3, min(b.o[k], b.c[k])), 0.6, max(abs(b.c[k] - b.o[k]), 0.05), color=col))
        for p in s.dotB.get(k, []): ax.plot(x, p, "o", ms=3, color="blue", alpha=.6)
        for p in s.dotS.get(k, []): ax.plot(x, p, "o", ms=3, color="red", alpha=.6)
        for p, sd in s.bt.get(k, []): ax.plot(x, p, "o", ms=10, mfc="none", color="blue" if sd > 0 else "red")
        if k in s.exhT: ax.plot(x, b.h[k] + 1, "v", color="orange")
        if k in s.exhB: ax.plot(x, b.l[k] - 1, "^", color="orange")
        for sd, lo, hi in s.zones.get(k, []):
            ax.add_patch(Rectangle((x, lo), min(30, z - k), hi - lo, color="cyan" if sd > 0 else "pink", alpha=.35))
        for sd, lv in s.sh.get(k, ()): ax.plot(x, lv, "s", color="purple")
        ax.text(x, b.l[k] - 3, f"{b.d[k]:.0f}", fontsize=5, ha="center", rotation=90)
    x0 = t.sig - a
    ax.hlines(t.edge, x0 - 25, x0, colors="k", linestyles="--", lw=1)
    if t.room: ax.hlines(t.room, x0 - 25, x0, colors="gray", linestyles="--", lw=1)
    ax.hlines([t.entry], x0 + 1, t.exit_i - a, colors="k"); ax.hlines([t.sl], x0 + 1, t.exit_i - a, colors="r")
    ax.hlines([t.tp], x0 + 1, t.exit_i - a, colors="g")
    ax.axvline(x0, color="gray", lw=.5); ax.axvline(t.touch - a, color="gray", lw=.5, ls=":")
    ax.set_title(f"{b.key[t.sig]} UTC  {t.kind} {'buy' if t.side>0 else 'sell'}  2nd={t.second}  {t.how} R={t.r:.2f}  bias={t.bias} {t.note}")
    ax.set_xticks(range(0, z - a + 1, 5)); ax.set_xticklabels([b.key[k][11:] for k in range(a, z + 1, 5)], fontsize=7)
    fig.tight_layout(); fig.savefig(path, dpi=90); plt.close(fig)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    bars, sig = build(); m = Machine(bars, sig)
    m.run(datetime(2026, 9, 14, tzinfo=timezone.utc), until=datetime(2026, 10, 24, tzinfo=timezone.utc))
    pick = [int(x) for x in sys.argv[2].split(",")]
    for j in pick:
        plot(m, m.trades[j], os.path.join(out, f"t{j:03d}.png"))
