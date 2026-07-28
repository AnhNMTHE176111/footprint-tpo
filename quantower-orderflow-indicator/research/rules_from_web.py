"""Kiểm chứng các LUẬT ABSORPTION lấy từ research web, trên dữ liệu thật GCQ26 (M1/M5/M15).

Nguồn luật:
  - Orderflows (Mike Valtos): Extreme/Trapped/Momentum absorption + Swing filter + Delta Confirmation
    + Delta DIVERGENCE (mua khi delta ÂM) + Min bar volume
  - VSA stopping volume: volume rất cao + spread HẸP + close off low  + "test bar" xác nhận
  - ATAS: volume bất thường sát cực trị + giá không đi qua mức đó (xác nhận thành công/thất bại)
  - Bookmap: CVD tăng mà giá đứng (hấp thụ ẩn)
Tất cả chỉ dùng dữ liệu bar-level (export không có per-level) → đây là XẤP XỈ của các luật gốc.
"""
import csv, statistics as st

TICK = 0.1
HOR = 20


def load():
    rows = []
    for r in csv.DictReader(open('data-export/fp-m1-6-month.csv', encoding='utf-8-sig')):
        mm, dd, yy = r['DateTime'].split()[0].split('/')
        if yy != '2026' or int(mm) < 5:
            continue
        try:
            rows.append(dict(o=float(r['Open']), h=float(r['High']), l=float(r['Low']), c=float(r['Close']),
                             v=float(r['Volume']), d=float(r['Delta'])))
        except ValueError:
            pass
    return rows


def agg(rows, k):
    out = []
    for i in range(0, len(rows) - k + 1, k):
        g = rows[i:i + k]
        out.append(dict(o=g[0]['o'], h=max(x['h'] for x in g), l=min(x['l'] for x in g), c=g[-1]['c'],
                        v=sum(x['v'] for x in g), d=sum(x['d'] for x in g)))
    return out


def study(rows, label, target, lb=10):
    n = len(rows)
    medv = [0.0] * n; medr = [0.0] * n; cvd = [0.0] * n
    wv, wr = [], []
    for i in range(n):
        if len(wv) >= 30:
            medv[i] = st.median(wv); medr[i] = st.median(wr)
        wv.append(rows[i]['v']); wr.append(rows[i]['h'] - rows[i]['l'])
        if len(wv) > 100: wv.pop(0); wr.pop(0)
        cvd[i] = (cvd[i - 1] if i else 0) + rows[i]['d']

    rng = lambda i: max(rows[i]['h'] - rows[i]['l'], TICK)
    dp = lambda i: rows[i]['d'] / rows[i]['v'] if rows[i]['v'] > 0 else 0
    vr = lambda i: rows[i]['v'] / medv[i] if medv[i] > 0 else 0
    cp = lambda i: (rows[i]['c'] - rows[i]['l']) / rng(i)      # 1 = đóng ở đỉnh

    def outcome(i, short):
        ref = rows[i]['c']
        for j in range(i + 1, min(n, i + HOR + 1)):
            if short:
                if ref - rows[j]['l'] >= target: return 1
                if rows[j]['h'] - ref >= target: return 0
            else:
                if rows[j]['h'] - ref >= target: return 1
                if ref - rows[j]['l'] >= target: return 0
        return None

    def ext(i, top):
        if i < lb: return False
        return rows[i]['h'] >= max(rows[j]['h'] for j in range(i - lb, i)) if top \
            else rows[i]['l'] <= min(rows[j]['l'] for j in range(i - lb, i))

    def ev(name, cond, delay=0, need_ext=True):
        """delay = số nến chờ xác nhận; tín hiệu vào lệnh tại i+delay"""
        w = t = 0
        for i in range(lb, n - HOR - delay - 1):
            if medv[i] <= 0: continue
            for top in (True, False):
                if need_ext and not ext(i, top): continue
                if not cond(i, top): continue
                o = outcome(i + delay, short=top)
                if o is None: continue
                t += 1; w += o
        se = (0.25 / t) ** 0.5 * 100 if t else 0
        flag = ''
        if t >= 100:
            flag = ' ***' if 100 * w / t - BASE[label] > 2 * se else ''
        print(f"    {name:56s} n={t:5d} hit={100*w/max(t,1):5.1f}% ±{se:.1f}{flag}")

    # base
    w = t = 0
    for i in range(lb, n - HOR):
        if medv[i] <= 0: continue
        for top in (True, False):
            if not ext(i, top): continue
            o = outcome(i, short=top)
            if o is None: continue
            t += 1; w += o
    BASE[label] = 100 * w / t
    print(f"\n=== {label} | target {target} USD | BASE = {BASE[label]:.1f}% (n={t}) ===")

    # --- VSA stopping volume: vol rất cao + spread hẹp + close off extreme ---
    for vg in (2.0, 3.0):
        ev(f"VSA stopping vol: vol≥{vg}× & range≤0.9×med & close lùi>60%",
           lambda i, top, vg=vg: vr(i) >= vg and rng(i) <= 0.9 * max(medr[i], TICK) and
           (cp(i) <= 0.4 if top else cp(i) >= 0.6))
    # + test bar (nến sau volume THẤP, không phá cực trị) — xác nhận kiểu VSA
    ev("… + test bar (nến sau vol≤0.8×med & không phá cực trị)",
       lambda i, top: vr(i) >= 2.0 and rng(i) <= 0.9 * max(medr[i], TICK) and
       (cp(i) <= 0.4 if top else cp(i) >= 0.6) and
       rows[i+1]['v'] <= 0.8 * max(medv[i], 1e-9) and
       (rows[i+1]['h'] <= rows[i]['h'] if top else rows[i+1]['l'] >= rows[i]['l']), delay=1)

    # --- Valtos: Delta DIVERGENCE (tín hiệu mua khi delta ÂM tại đáy) ---
    for vg in (1.5, 2.5):
        ev(f"Valtos delta-divergence: vol≥{vg}× & delta NGƯỢC hướng đảo",
           lambda i, top, vg=vg: vr(i) >= vg and (dp(i) >= 0.10 if top else dp(i) <= -0.10))
    # --- Valtos: Delta CONFIRMATION (delta cùng hướng tín hiệu) ---
    for vg in (1.5, 2.5):
        ev(f"Valtos delta-confirmation: vol≥{vg}× & delta THUẬN hướng đảo",
           lambda i, top, vg=vg: vr(i) >= vg and (dp(i) <= -0.10 if top else dp(i) >= 0.10))

    # --- ATAS: xác nhận SAU — mức cực trị không bị phá trong 2 nến kế ---
    ev("ATAS xác nhận: vol≥2× & 2 nến sau KHÔNG phá cực trị",
       lambda i, top: vr(i) >= 2.0 and
       (max(rows[i+1]['h'], rows[i+2]['h']) <= rows[i]['h'] if top
        else min(rows[i+1]['l'], rows[i+2]['l']) >= rows[i]['l']), delay=2)

    # --- Bookmap: CVD đi ngược giá (hấp thụ ẩn) ---
    ev("Bookmap CVD-divergence: giá cực trị mới & CVD không xác nhận",
       lambda i, top: vr(i) >= 1.2 and i >= lb and
       ((cvd[i] <= max(cvd[i-lb:i])) if top else (cvd[i] >= min(cvd[i-lb:i]))))

    # --- Momentum absorption (CONTINUATION, không cần ở cực trị đảo) ---
    ev("Momentum abs (tiếp diễn): vol≥2× & delta thuận đà & đóng cửa mạnh",
       lambda i, top: vr(i) >= 2.0 and (dp(i) >= 0.20 and cp(i) >= 0.7 if top else dp(i) <= -0.20 and cp(i) <= 0.3),
       need_ext=True)


BASE = {}
raw = load()
study(raw, 'M1', 1.0)
study(agg(raw, 5), 'M5', 2.0)
study(agg(raw, 15), 'M15', 3.0)
print("\n*** = vượt BASE quá 2 sai số chuẩn (n≥100)")
