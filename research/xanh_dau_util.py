import csv

KEYS = ("lv", "bot_bid", "bot_ask", "top_bid", "top_ask", "mid_bid", "mid_ask",
        "nbuy_top", "nsell_bot", "stk_buy_top", "stk_sell_bot", "loB", "loA", "hiB", "hiA", "poc_pos")


def load_feats(path, n):
    F = {k: [0] * n for k in KEYS}
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        hd = next(r)
        ix = {k: i for i, k in enumerate(hd)}
        for row in r:
            b = int(row[0])
            if b >= n:
                continue
            for k in KEYS:
                F[k][b] = int(row[ix[k]])
    return F
