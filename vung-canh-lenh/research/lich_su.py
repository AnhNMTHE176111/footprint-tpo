# -*- coding: utf-8 -*-
"""Vùng lịch sử (chế độ "Hiện TẤT CẢ vùng trong lịch sử" của Vùng Canh Lệnh) — port Python của LichSuTracker (VclCore.cs),
đặc tả PLAN-LICH-SU.md mục 2. KHÔNG chạy lại engine: đọc bộ Display từng nến từ replay C# (tools/ReplayCsv) + nến M1.

(1) Parity TỪNG DÒNG với <replay>_lichsu.csv của C# (tiêu chí 11).
(2) Bảng tiêu chí 1–9 (PLAN-LICH-SU mục 3) trên file 90 ngày + số đo phụ (rủi ro 9, thời lượng, lý do kết thúc...).
Chạy:  python3 lich_su.py            (tự build + chạy ReplayCsv cho file 90 ngày và 29 ngày, rồi đo)
       python3 lich_su.py --no-run   (dùng replay đã có trong report/)
Kết quả in ra màn hình; report/LICH-SU.md do người viết chép bảng (không tự ghi đè nhận xét)."""
import os, sys, subprocess, collections
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
REPO = os.path.abspath(os.path.join(ROOT, '..'))
DATA = os.path.join(REPO, 'data-export', 'data-footprint')
BASE90 = os.path.join(DATA, 'fp_GCZ26_XCEC_Time_20260723-20261021_90d')
BASE29 = os.path.join(DATA, 'fp_GCZ26_XCEC_Time_20260816-20260915_29d2h')
REP = os.path.join(HERE, 'report')
SIGNALS = os.path.join(REPO, 'benzo-trader', 'research', 'report', '_replay_cs.csv')

# hằng — khớp Vcl trong VclCore.cs
GAP_MINUTES = 30          # khoảng trống > 30 phút ⇒ phiên mới
EP_TAU, EP_EXIT, EP_GAP = 0.0, 2.0, 5
LS_OVERLAP, LS_GAP_MIN, LS_LABEL_MIN = 0.5, 60.0, 15.0


def run_replay(base, out):
    env = dict(os.environ, PATH=os.path.expanduser('~/.dotnet') + ':' + os.environ['PATH'], DOTNET_CLI_TELEMETRY_OPTOUT='1', DOTNET_NOLOGO='1')
    subprocess.run(['dotnet', 'run', '-c', 'Release', '--project', os.path.join(ROOT, 'tools', 'ReplayCsv'), '--', base, out], check=True, env=env)


def load(base, replay):
    bars = pd.read_csv(base + '_bars.csv', usecols=['bar_idx', 'datetime', 'open', 'high', 'low', 'close'])
    t = pd.to_datetime(bars['datetime']).to_numpy()
    rep = pd.read_csv(replay, usecols=['bar_idx', 'zone_id', 'lo', 'hi', 'role'])
    disp = collections.defaultdict(list)
    for b, zid, lo, hi, role in zip(rep['bar_idx'].to_numpy(), rep['zone_id'].to_numpy(), rep['lo'].to_numpy(), rep['hi'].to_numpy(), rep['role'].to_numpy()):
        slot = 'K' if role == 'K' else ('F' if role.endswith('F') else 'N')
        disp[int(b)].append((int(zid), float(lo), float(hi), slot))
    return dict(t=t, O=bars['open'].to_numpy(float), H=bars['high'].to_numpy(float), L=bars['low'].to_numpy(float),
                C=bars['close'].to_numpy(float), disp=disp, n=len(bars))


def track(D):
    """Port 1-1 của LichSuTracker.Step (VclCore.cs). Trả danh sách vùng (dict) theo thứ tự tạo + thống kê."""
    t, O, H, L, C, disp, n = D['t'], D['O'], D['H'], D['L'], D['C'], D['disp'], D['n']
    mins = ((t - t[0]) / np.timedelta64(1, 'm')).astype(float)
    allz, song = [], []
    st = collections.Counter()
    wdiff = 0; nmatch = 0
    for i in range(n):
        new_sess = i == 0 or (mins[i] - mins[i - 1]) > GAP_MINUTES
        cprev = O[i] if new_sess else C[i - 1]
        for h in song:
            h['matched'] = -1
        # (1) khớp / tạo
        for (zid, lo, hi, slot) in disp.get(i, ()):
            best = None; best_rel = 0.0; anyov = False; taken = False
            for h in song:
                ov = min(h['hi'], hi) - max(h['lo'], lo)
                if ov <= 0:
                    continue
                anyov = True
                rel = ov / max(1e-9, min(h['hi'] - h['lo'], hi - lo))
                if h['matched'] >= 0:
                    if rel >= LS_OVERLAP:
                        taken = True
                    continue
                if rel >= LS_OVERLAP and rel > best_rel:
                    best = h; best_rel = rel
            if best is not None:
                best['last'] = i; best['matched'] = zid; best['tung_gan'] |= slot != 'F'
                nmatch += 1
                if abs((hi - lo) - (best['hi'] - best['lo'])) > 1.0:
                    wdiff += 1
                continue
            if anyov:
                st['bị chặn'] += 1
                if taken:
                    st['bị chặn vì vùng lịch sử đã khớp vùng Display khác'] += 1
                continue
            vai = 1 if C[i] < lo else (-1 if C[i] > hi else 0)
            h = dict(id=len(allz), lo=lo, hi=hi, vai=vai, start=i, last=i, end=-1, ly_do='', n_cham_lai=0, tung_gan=slot != 'F',
                     matched=zid, ep=None, vai_at=i if vai != 0 else None)
            allz.append(h); song.append(h)
            st['tạo'] += 1
            if vai == 0:
                st['tạo khi giá trong vùng'] += 1
        # (2) hết phiên, vai, máy xuyên phá; (3) hết hạn
        if new_sess:
            for h in song:
                h['ep'] = None
        still = []
        for h in song:
            lo, hi = h['lo'], h['hi']
            if h['vai'] == 0:
                if C[i] < lo:
                    h['vai'] = 1; h['vai_at'] = i
                elif C[i] > hi:
                    h['vai'] = -1; h['vai_at'] = i
            cham = max(cprev, H[i]) >= lo - EP_TAU and min(cprev, L[i]) <= hi + EP_TAU
            neo = cham or (lo - EP_EXIT <= C[i] <= hi + EP_EXIT)
            if h['ep'] is None and cham:
                h['ep'] = [0, 0]                 # [đếm thoát, phía thoát]
                if i > h['start']:
                    h['n_cham_lai'] += 1
            ket = False
            e = h['ep']
            if e is not None:
                if neo:
                    e[0] = 0; e[1] = 0
                else:
                    e[1] = 1 if C[i] > hi else -1
                    e[0] += 1
                    if e[0] >= EP_GAP:
                        phia = e[1]
                        h['ep'] = None
                        if (h['vai'] == 1 and phia == 1) or (h['vai'] == -1 and phia == -1):
                            h['end'] = max(h['start'], i - EP_GAP); h['ly_do'] = 'xuyên phá'; ket = True
            if not ket and mins[i] - mins[h['last']] > LS_GAP_MIN:
                h['end'] = h['last']; h['ly_do'] = 'hết hạn'; ket = True
            if ket:
                if h['matched'] >= 0:
                    st['chết khi đang khớp'] += 1
                h['matched'] = -1; h['ep'] = None
                continue
            still.append(h)
        song = still
    st['khớp'] = nmatch; st['khớp lệch rộng > 1 giá'] = wdiff
    return allz, st, mins


def fmt_t(t):
    return pd.Timestamp(t).strftime('%Y-%m-%d %H:%M:%S')


def parity(allz, D, cs_path):
    """So TỪNG DÒNG với _lichsu.csv của C#: id, start_utc, end_utc, lo, hi (so số thực chính xác), vai, ly_do, n_cham_lai, tung_gan."""
    t = D['t']
    py = [(h['id'], fmt_t(t[h['start']]), '' if h['end'] < 0 else fmt_t(t[h['end']]), h['lo'], h['hi'], h['vai'], h['ly_do'],
           h['n_cham_lai'], 1 if h['tung_gan'] else 0) for h in allz]
    cs = pd.read_csv(cs_path, keep_default_na=False, dtype={'end_utc': str, 'ly_do': str})
    csr = [(int(r.id), r.start_utc, r.end_utc, float(r.lo), float(r.hi), int(r.vai), r.ly_do, int(r.n_cham_lai), int(r.tung_gan))
           for r in cs.itertuples(index=False)]
    same = sum(1 for a, b in zip(py, csr) if a == b)
    first_bad = next((k for k, (a, b) in enumerate(zip(py, csr)) if a != b), None)
    return dict(py=len(py), cs=len(csr), same=same, first_bad=first_bad,
                bad=(py[first_bad], csr[first_bad]) if first_bad is not None else None)


def metrics(allz, D, mins, st):
    n = D['n']; disp = D['disp']
    dt = np.diff(mins, prepend=mins[0])
    sess = np.cumsum(dt > GAP_MINUTES)
    nsess = int(sess[-1]) + 1
    ends = np.array([h['end'] if h['end'] >= 0 else n - 1 for h in allz])
    starts = np.array([h['start'] for h in allz])
    lo = np.array([h['lo'] for h in allz]); hi = np.array([h['hi'] for h in allz])
    R = {}
    # 1. khối/phiên (phiên của nến tạo)
    cnt = np.bincount(sess[starts], minlength=nsess)
    R['k_phien'] = (cnt.mean(), np.percentile(cnt, 90), cnt.max())
    # 2. khối thấy trong cửa sổ 24 h (giao thời gian), bước 6 giờ
    ms, me = mins[starts], mins[ends]
    win = [int(((ms < s + 1440) & (me >= s)).sum()) for s in range(0, int(mins[-1]) - 1440, 360)]
    R['k_24h'] = (np.percentile(win, 50), np.percentile(win, 90), max(win))
    # 3. diện tích chồng (thời gian phút × giá) giữa MỌI cặp khối (mạnh hơn "cùng phiên")
    order = np.argsort(starts, kind='stable')
    tot = float(((me - ms + 1) * (hi - lo)).sum()); ov = 0.0; npairs = 0; active = []
    for k in order:
        active = [j for j in active if me[j] >= ms[k]]
        for j in active:
            tm = min(me[j], me[k]) - max(ms[j], ms[k]) + 1
            pr = min(hi[j], hi[k]) - max(lo[j], lo[k])
            if tm > 0 and pr > 0:
                ov += tm * pr; npairs += 1
        active.append(k)
    R['chong'] = (ov / tot * 100, npairs)
    # 5–6. phủ Display và bắc cầu (định nghĩa như mô phỏng PLAN mục 1.3)
    ev = collections.defaultdict(list)
    for k in range(len(allz)):
        ev[starts[k]].append((1, k)); ev[ends[k] + 1].append((-1, k))
    cur = set(); cov = 0; totD = 0; bridged = 0; totH = 0; alive_n = np.zeros(n, int)
    for i in range(n):
        for (s, k) in ev.get(i, ()):
            (cur.add if s > 0 else cur.discard)(k)
        Dz = disp.get(i, ())
        totD += len(Dz); totH += len(cur); alive_n[i] = len(cur)
        matched = set()
        for (zid, zl, zh, slot) in Dz:
            ok = False
            for k in cur:
                o = min(hi[k], zh) - max(lo[k], zl)
                if o > 0 and o / max(1e-9, min(hi[k] - lo[k], zh - zl)) >= LS_OVERLAP:
                    ok = True; matched.add(k)
            cov += ok
        bridged += len(cur) - len(matched)
    R['phu'] = cov / totD * 100
    R['bac_cau'] = bridged / max(1, totH) * 100
    R['song_moi_nen'] = (alive_n.mean(), np.percentile(alive_n, 90), alive_n.max())
    R['zone_bars'] = totD
    # 7. khối < 3 phút
    dur = me - ms
    R['lt3'] = (dur < 3).mean() * 100
    R['lt15'] = (dur < LS_LABEL_MIN).mean() * 100
    R['dur'] = (np.percentile(dur, 50), np.percentile(dur, 90))
    # 8. khối / khoá giá (tâm làm tròn 1 giá) / phiên
    keyc = collections.Counter((int(sess[s]), round((a + b) / 2)) for s, a, b in zip(starts, lo, hi))
    kv = np.array(list(keyc.values()))
    R['khoa'] = (kv.mean(), kv.max())
    # 9. vùng sống tại nến signal Benzo (StartTime ≤ tF ≤ EndTime; vùng còn sống ⇒ tới mép phải)
    sig = pd.read_csv(SIGNALS)
    stt = pd.to_datetime(sig['time_utc']).to_numpy()
    stt = stt[(stt >= D['t'][0]) & (stt <= D['t'][-1])]          # chỉ signal nằm trong khoảng dữ liệu
    idx = np.searchsorted(D['t'], stt)                               # nến có giờ mở ≥ giờ signal (đầu tiên)
    at = np.array([int(((starts <= i) & (ends >= i)).sum()) for i in idx])
    live_at = np.array([len(disp.get(int(i), ())) for i in idx])
    R['signal'] = (len(stt), at.mean(), np.percentile(at, 10), np.percentile(at, 90), at.max(), live_at.mean())
    # phụ
    why = collections.Counter(h['ly_do'] or 'còn sống' for h in allz)
    R['why'] = dict(why)
    delay = np.array([mins[h['vai_at']] - mins[h['start']] for h in allz if h['vai_at'] is not None and h['vai_at'] > h['start']])
    R['vai0'] = (st['tạo khi giá trong vùng'], len(allz), np.percentile(delay, 50) if len(delay) else 0, np.percentile(delay, 90) if len(delay) else 0,
                 sum(1 for h in allz if h['vai'] == 0))
    R['cham_lai'] = np.mean([h['n_cham_lai'] >= 1 for h in allz]) * 100
    R['tung_gan'] = np.mean([h['tung_gan'] for h in allz]) * 100
    R['clamp'] = sum(1 for h in allz if h['ly_do'] == 'xuyên phá' and h['end'] == h['start'])
    R['st'] = dict(st)
    R['n_khoi'] = len(allz); R['n_phien'] = nsess; R['n'] = n
    return R


def show(name, R, P):
    p = lambda x: f'{x:.1f}'.replace('.', ',')
    print(f"\n=== {name}: {R['n']} nến, {R['n_phien']} phiên, {R['n_khoi']} khối ===")
    print(f"parity từng dòng: Python {P['py']} · C# {P['cs']} · trùng {P['same']}" + (f" · lệch đầu tiên dòng {P['first_bad']}: {P['bad']}" if P['bad'] else ''))
    print(f"1. khối/phiên TB {p(R['k_phien'][0])} · p90 {R['k_phien'][1]:.0f} · max {R['k_phien'][2]}")
    print(f"2. khối thấy trong 24 h p50 {R['k_24h'][0]:.0f} · p90 {R['k_24h'][1]:.0f} · max {R['k_24h'][2]}")
    print(f"3. diện tích chồng {R['chong'][0]:.3f}% · số cặp giao {R['chong'][1]}")
    print(f"5. phủ Display {p(R['phu'])}%   6. bắc cầu {p(R['bac_cau'])}%")
    print(f"7. khối < 3 phút {p(R['lt3'])}% (< 15 phút {p(R['lt15'])}%) · thời lượng p50 {R['dur'][0]:.0f} p90 {R['dur'][1]:.0f} phút")
    print(f"8. khối/khoá giá/phiên TB {R['khoa'][0]:.2f} · max {R['khoa'][1]}")
    s = R['signal']
    print(f"9. {s[0]} signal: vùng sống TB {p(s[1])} · p10 {s[2]:.0f} · p90 {s[3]:.0f} · max {s[4]} (Display live TB {p(s[5])})")
    print(f"vùng sống mỗi nến TB {p(R['song_moi_nen'][0])} p90 {R['song_moi_nen'][1]:.0f} max {R['song_moi_nen'][2]} · kết thúc {R['why']}")
    v = R['vai0']
    print(f"tạo khi giá trong vùng {v[0]}/{v[1]} · chốt vai trễ p50 {v[2]:.0f} p90 {v[3]:.0f} phút · vai 0 tới cuối {v[4]} · ≥1 chạm lại {p(R['cham_lai'])}%"
          f" · từng gần {p(R['tung_gan'])}% · End kẹp = Start {R['clamp']}")
    st = R['st']
    print(f"vùng-nến Display {R['zone_bars']} · khớp {st.get('khớp', 0)} · bị chặn {st.get('bị chặn', 0)} ({100 * st.get('bị chặn', 0) / R['zone_bars']:.2f}%)"
          f" — trong đó vì vùng lịch sử đã khớp vùng Display khác {st.get('bị chặn vì vùng lịch sử đã khớp vùng Display khác', 0)}"
          f" · chết khi đang khớp {st.get('chết khi đang khớp', 0)} · khớp lệch rộng > 1 giá {st.get('khớp lệch rộng > 1 giá', 0)}"
          f" ({100 * st.get('khớp lệch rộng > 1 giá', 0) / max(1, st.get('khớp', 0)):.2f}% lần khớp)")


def main():
    run = '--no-run' not in sys.argv
    for name, base, rp in [('90 ngày', BASE90, os.path.join(REP, 'vcl5_cs_replay_v5.csv')), ('29 ngày', BASE29, os.path.join(REP, 'vcl5_cs_replay_v5_29d.csv'))]:
        if run:
            run_replay(base, rp)
        D = load(base, rp)
        allz, st, mins = track(D)
        P = parity(allz, D, rp[:-4] + '_lichsu.csv')
        R = metrics(allz, D, mins, st)
        show(name, R, P)


if __name__ == '__main__':
    main()
