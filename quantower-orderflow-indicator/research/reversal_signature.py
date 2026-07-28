"""Chữ ký order-flow tại các điểm ĐẢO CHIỀU lớn (M1, GCQ26, tháng 5-7/2026).

Câu hỏi: tại "vùng quan trọng" (đỉnh/đáy đảo chiều thật), order flow trông như:
  (a) ABSORPTION  = phe chủ động THUẬN đà vẫn mạnh nhưng giá không đi tiếp (bị nuốt)
  (b) AGGRESSIVE  = phe NGƯỢC đà đập vào (delta lật dấu ngay tại cực trị)
  (c) TWO-SIDED   = volume lớn, delta ~0 (định nghĩa absorption của ebook: to ở CẢ bid lẫn ask)
  (d) QUIET       = volume không có gì bất thường
"""
import csv, statistics as st

TICK = 0.1
PATH = 'data-export/fp-m1-6-month.csv'

rows = []
for r in csv.DictReader(open(PATH, encoding='utf-8-sig')):
    d = r['DateTime'].split()[0]
    mm, dd, yy = d.split('/')
    if yy != '2026' or int(mm) < 5:      # chỉ lấy giai đoạn GCQ26 đã lỏng
        continue
    try:
        rows.append(dict(
            t=r['DateTime'],
            o=float(r['Open']), h=float(r['High']), l=float(r['Low']), c=float(r['Close']),
            v=float(r['Volume']), d=float(r['Delta']),
            buy=float(r['Buy (Ask) volume']), sell=float(r['Sell (Bid) volume']),
        ))
    except ValueError:
        pass

n = len(rows)
print(f"nến dùng: {n}")

# ---- baseline volume: median 100 nến trước ----
med100 = [0.0] * n
win = []
for i in range(n):
    med100[i] = st.median(win) if len(win) >= 30 else 0.0
    win.append(rows[i]['v'])
    if len(win) > 100:
        win.pop(0)

K = 15          # nửa cửa sổ swing
MOVE = 2.0      # biên độ tối thiểu trước & sau (USD = 20 tick)
AFTER = 20      # số nến đo cú đảo


def swings():
    hi, lo = [], []
    for i in range(K, n - max(K, AFTER)):
        b = rows[i]
        if med100[i] <= 0:
            continue
        hs = [rows[j]['h'] for j in range(i - K, i + K + 1)]
        ls = [rows[j]['l'] for j in range(i - K, i + K + 1)]
        if b['h'] >= max(hs):
            up = b['h'] - min(rows[j]['l'] for j in range(i - K, i))
            dn = b['h'] - min(rows[j]['l'] for j in range(i + 1, i + AFTER + 1))
            if up >= MOVE and dn >= MOVE:
                hi.append(i)
        if b['l'] <= min(ls):
            dn2 = max(rows[j]['h'] for j in range(i - K, i)) - b['l']
            up2 = max(rows[j]['h'] for j in range(i + 1, i + AFTER + 1)) - b['l']
            if dn2 >= MOVE and up2 >= MOVE:
                lo.append(i)
    return hi, lo


def cluster(i, half=1):
    """gộp nến i-half..i+half (absorption thường kéo dài vài nến)"""
    v = d = buy = sell = 0.0
    hh = -1e9; ll = 1e9
    for j in range(max(0, i - half), min(n, i + half + 1)):
        v += rows[j]['v']; d += rows[j]['d']
        buy += rows[j]['buy']; sell += rows[j]['sell']
        hh = max(hh, rows[j]['h']); ll = min(ll, rows[j]['l'])
    return v, d, buy, sell, hh, ll


def classify(i, is_high, half):
    v, d, buy, sell, hh, ll = cluster(i, half)
    base = med100[i] * (2 * half + 1)
    vr = v / base if base > 0 else 0
    dp = d / v if v > 0 else 0
    if not is_high:
        dp = -dp                       # chuẩn hoá: dp>0 = phe THUẬN đà cũ vẫn chủ động
    hot = vr >= 1.5
    if not hot:
        return 'QUIET', vr, dp
    if dp >= 0.15:
        return 'ABSORPTION', vr, dp    # thuận đà vẫn đập mà giá quay đầu -> bị hấp thụ
    if dp <= -0.15:
        return 'AGGRESSIVE', vr, dp    # phe ngược đập ngay tại cực trị
    return 'TWO_SIDED', vr, dp


hi, lo = swings()
print(f"swing high: {len(hi)} | swing low: {len(lo)}\n")

for half, tag in ((0, 'chỉ nến cực trị'), (1, 'cụm 3 nến'), (2, 'cụm 5 nến')):
    print(f"--- {tag} ---")
    for name, idxs, is_high in (('ĐỈNH', hi, True), ('ĐÁY', lo, False)):
        cnt = {}
        vrs = []
        for i in idxs:
            k, vr, dp = classify(i, is_high, half)
            cnt[k] = cnt.get(k, 0) + 1
            vrs.append(vr)
        tot = len(idxs)
        s = '  '.join(f"{k}={100*c/tot:4.1f}%" for k, c in sorted(cnt.items(), key=lambda x: -x[1]))
        print(f"  {name} (n={tot})  volRatio median={st.median(vrs):.2f}  |  {s}")
    print()

# ---- so sánh với nến BẤT KỲ (baseline: vùng quan trọng có khác gì không?) ----
print("--- baseline: TẤT CẢ nến (giả định 'đà cũ' = hướng nến trước) ---")
cnt = {}
vrs = []
for i in range(K, n - K):
    if med100[i] <= 0:
        continue
    is_high = rows[i]['c'] >= rows[i]['o']
    k, vr, dp = classify(i, is_high, 1)
    cnt[k] = cnt.get(k, 0) + 1
    vrs.append(vr)
tot = sum(cnt.values())
print(f"  n={tot}  volRatio median={st.median(vrs):.2f}  |  " +
      '  '.join(f"{k}={100*c/tot:4.1f}%" for k, c in sorted(cnt.items(), key=lambda x: -x[1])))
