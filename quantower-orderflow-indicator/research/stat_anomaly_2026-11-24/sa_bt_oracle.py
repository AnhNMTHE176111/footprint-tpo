"""Bước 6 (Big Trade): "không bỏ sót" / "không nhiễu" (PLAN 4.3) trên hai thước nhìn lại, thay chấm bằng vòng, gộp theo g.
Chọn cấu hình (không nhìn đoạn kiểm): đạt Khớp chung (0,8–1,25) ở ĐOẠN CHỌN của GC (10 phiên đầu) ở cả M1, M5, M15 (out_r1_bt_pick.csv);
hơn 40 thì lấy 40 có độ lệch khớp theo phiên nhỏ nhất; cộng 2 mốc đối chứng.
Chạy: GC (chon / kiem / tat_ca), NQ (tat_ca: 6 phiên, không có đoạn kiểm), GClive (kiem, chỉ cuon / ky_luc / đối chứng).
Ra: out_r1_bt_oracle.csv"""
import time, numpy as np, pandas as pd
from sa_common import load_dot, TFS, _cache
import sa_dot_rules as R
from sa_bt_rules import BtData, evaluate_bt, bt_configs, attach_L, LAI_L
from sa_oracle_lib import rulers, oracle_row
from bt_common import load_m1, to_tf

P = pd.read_csv('out_r1_bt_pick.csv')
X = P[P.khung.isin([1, 5, 15]) & ~P.phuong_an.str.startswith('dc_')].copy()
X['ok'] = (X.khop_chung >= 0.8) & (X.khop_chung <= 1.25)
X['dev'] = np.abs(np.log(X[['khop_phien_A', 'khop_phien_Au', 'khop_phien_My']].clip(lower=1e-6))).max(1)
G = X.groupby('cau_hinh').agg(n_ok=('ok', 'sum'), dev=('dev', 'max'))
G = G[G.n_ok == 3].sort_values('dev')
names = G.index[:40].tolist()
print(f'{len(G)} cấu hình đạt Khớp chung ở đoạn chọn GC (M1, M5, M15); chạy {len(names)}')
DO = {'GC': ('chon', 'kiem', 'tat_ca'), 'NQ': ('tat_ca',), 'GClive': ('kiem',)}
NOTE = {'GC': '', 'NQ': '6 phiên, không có đoạn kiểm', 'GClive': 'nhật ký sống đứt quãng'}
rows = []; t0 = time.time()
for key in ('GC', 'NQ', 'GClive'):
    M1 = load_m1(key)
    for m in TFS:
        bt = BtData(key, m, to_tf(M1, m))
        if key != 'GClive':
            attach_L(bt, load_dot(key, m)); _cache.pop((key, m), None)
        allc = {c['name']: c for c in bt_configs(key, LAI_L if key != 'GClive' else ())}
        # tên cấu hình cùng giờ khác nhau giữa GC (K 5/10) và NQ (K 3/5): với NQ dùng cấu hình cùng tên nếu có
        cfgs = [allc[n] for n in names if n in allc] + [allc['dc_codinh10'], allc['dc_dang_chay_thich_nghi']]
        if key == 'GClive':
            cfgs = [c for c in cfgs if c['pa'] in ('cuon', 'ky_luc') or c['pa'].startswith('dc_')]
        Rr = rulers(bt)
        for cfg in cfgs:
            res = evaluate_bt(bt, cfg)
            for doan in DO[key]:
                o = oracle_row(bt, res, Rr, bt.doan_mask(doan), bt.g)
                rows.append(dict(cau_hinh=cfg['name'], phuong_an=cfg['pa'], ma=key, khung=m, doan=doan, ghi_chu=NOTE[key], **o))
        R._memo.clear()
        print(f'{key} M{m} xong ({time.time() - t0:.0f} s)', flush=True)
D = pd.DataFrame(rows).rename(columns=lambda c: c.replace('cham', 'vong'))
D.to_csv('out_r1_bt_oracle.csv', index=False, float_format='%.5g')
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 300)
K = D[(D.doan == 'kiem') & (D.ma == 'GC') & D.khung.isin([1, 5, 15])]
print(K.groupby('cau_hinh').so_truot_43.sum().sort_values().to_string())
