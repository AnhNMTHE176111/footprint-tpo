"""Bước 4: "không bỏ sót" và "không nhiễu" (PLAN 4.3) cho chấm, trên hai thước nhìn lại (sa_oracle_lib.py).
Chọn cấu hình (không nhìn đoạn kiểm): cấu hình đạt "Khớp chung" (0,8–1,25) trên ĐOẠN CHỌN ở cả 6 ô (GC, NQ) x (M1, M5, M15) — out_r1_dot_pick.csv;
nếu hơn 40 thì lấy 40 cấu hình có độ lệch khớp theo phiên (max |ln khớp phiên|, đoạn chọn) nhỏ nhất; cộng 5 mốc đối chứng.
Chạy trên 2 mã x 5 khung x 3 đoạn. "Được nổ": thô = vượt ngưỡng; gộp = vượt ngưỡng hoặc cùng nến cùng bên có chấm cách <= w tick.
Ra: out_r1_dot_oracle.csv"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, SYMS, TFS, DOANS, _cache
from sa_dot_rules import evaluate, all_configs, forget, BASELINES
from sa_oracle_lib import rulers, oracle_row


def pick_configs(path='out_r1_dot_pick.csv', nmax=40):
    P = pd.read_csv(path)
    X = P[P.khung.isin([1, 5, 15]) & ~P.phuong_an.str.startswith('dc_')].copy()
    X['ok'] = (X.khop_chung >= 0.8) & (X.khop_chung <= 1.25)
    X['dev'] = np.abs(np.log(X[['khop_phien_A', 'khop_phien_Au', 'khop_phien_My']].clip(lower=1e-6))).max(1)
    G = X.groupby('cau_hinh').agg(n_ok=('ok', 'sum'), dev=('dev', 'max'))
    G = G[G.n_ok == 6].sort_values('dev')
    return G.index[:nmax].tolist(), G


if __name__ == '__main__':
    names, G = pick_configs()
    print(f'{len(names)} cấu hình đạt Khớp chung ở đoạn chọn (cả 6 ô)')
    byname = {c['name']: c for c in all_configs()}
    cfgs = [byname[n] for n in names] + BASELINES
    rows = []; t0 = time.time()
    for sym in SYMS:
        for m in TFS:
            ds = load_dot(sym, m)
            Rr = rulers(ds)
            for cfg in cfgs:
                res = evaluate(ds, cfg)
                for doan in DOANS:
                    o = oracle_row(ds, res, Rr, ds.doan_mask(doan), ds.w)
                    rows.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], ma=sym, khung=m, doan=doan, **o))
            forget(ds); del _cache[(sym, m)]
            print(f'{sym} M{m} xong ({time.time() - t0:.0f} s)', flush=True)
    D = pd.DataFrame(rows)
    D.to_csv('out_r1_dot_oracle.csv', index=False, float_format='%.5g')
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
    K = D[(D.doan == 'kiem') & D.khung.isin([1, 5, 15])]
    print(K.groupby('cau_hinh').so_truot_43.sum().sort_values().to_string())
    print(K[['cau_hinh', 'ma', 'khung', 'p_hat', 'v_top20', 'v_top5', 'v_cuc_tri', 'v_khong_nhieu', 'v_ti_hon']].head(60).to_string(index=False))
