"""Bước 1: mô tả dữ liệu, chưa có luật nào (PLAN mục 5, bước 1).
Mỗi (mã, khung, đoạn, giờ UTC) và mỗi phiên: số nến; số ô mỗi nến; số giá trị bên > 0; phân vị 50/90/99/99,5/99,9 của giá trị bên (gộp Bid + Ask);
phân vị 99 riêng Bid / riêng Ask (lệch > 10% thì gắn cờ); phân vị 99 tính riêng từng ngày giao dịch rồi lấy phân vị 10/50/90 qua các ngày.
Ra: out_r1_profile.csv, out_r1_profile.txt"""
import numpy as np, pandas as pd
from sa_common import load_dot, SYMS, TFS, DOANS, SES_NAMES, SES_VN
pd.set_option('display.width', 250); pd.set_option('display.max_rows', 2000)


def prof(ds, bm):
    """bm: mặt nạ nến. Trả dict số liệu."""
    sm = bm[ds.sbar]
    v = ds.sval[sm]; side = ds.sside[sm]; day = ds.dayi[ds.sbar[sm]]
    nb = int(bm.sum())
    if nb == 0 or len(v) == 0: return None
    q = np.quantile(v, [.5, .9, .99, .995, .999])
    pb = np.quantile(v[side == 0], .99) if (side == 0).any() else np.nan
    pa = np.quantile(v[side == 1], .99) if (side == 1).any() else np.nan
    pd99 = pd.Series(v).groupby(day).quantile(.99)
    pd99 = pd99[pd.Series(v).groupby(day).size() >= 100]          # ngày quá ít mẫu (< 100) không tính phân vị 99 riêng
    dq = np.quantile(pd99.values, [.1, .5, .9]) if len(pd99) else [np.nan] * 3
    lech = abs(pb - pa) / max(min(pb, pa), 1e-9)
    return dict(so_nen=nb, o_moi_nen=round(ds.nl[bm].mean(), 1), so_gia_tri=int(len(v)), gt_moi_nen=round(len(v) / nb, 1),
                p50=q[0], p90=q[1], p99=q[2], p995=q[3], p999=q[4], p99_bid=pb, p99_ask=pa, lech_bid_ask=round(lech, 3), co_lech_10=bool(lech > 0.10),
                so_ngay=len(pd99), p99_ngay_p10=dq[0], p99_ngay_p50=dq[1], p99_ngay_p90=dq[2])


rows = []
for sym in SYMS:
    for m in TFS:
        ds = load_dot(sym, m)
        for doan in DOANS:
            dm = ds.doan_mask(doan)
            r = prof(ds, dm)
            rows.append(dict(ma=sym, khung=m, doan=doan, pham_vi='tat_ca', **r))
            for s, sn in enumerate(SES_NAMES):
                r = prof(ds, dm & (ds.ses == s))
                if r: rows.append(dict(ma=sym, khung=m, doan=doan, pham_vi='phien_' + sn, **r))
            for h in range(24):
                r = prof(ds, dm & (ds.hour == h))
                if r: rows.append(dict(ma=sym, khung=m, doan=doan, pham_vi=f'gio_{h:02d}', **r))
        print(sym, m, 'xong', flush=True)
D = pd.DataFrame(rows)
for c in ('p50', 'p90', 'p99', 'p995', 'p999', 'p99_bid', 'p99_ask', 'p99_ngay_p10', 'p99_ngay_p50', 'p99_ngay_p90'):
    D[c] = D[c].round(1)
D.to_csv('out_r1_profile.csv', index=False)
out = []
out.append('BƯỚC 1 — mô tả dữ liệu (giá trị bên > 0, gộp Bid + Ask). Đoạn = tat_ca trừ khi ghi khác.\n')
out.append('== Tóm tắt theo phiên (đoạn tất cả) ==')
T = D[(D.doan == 'tat_ca') & (D.pham_vi.str.startswith('phien') | (D.pham_vi == 'tat_ca'))]
out.append(T[['ma', 'khung', 'pham_vi', 'so_nen', 'o_moi_nen', 'gt_moi_nen', 'p50', 'p90', 'p99', 'p995', 'p999', 'p99_bid', 'p99_ask', 'lech_bid_ask', 'p99_ngay_p10', 'p99_ngay_p50', 'p99_ngay_p90']].to_string(index=False))
out.append('\n== Theo giờ UTC (đoạn tất cả): p99 gộp; p99 từng ngày p10/p50/p90 ==')
H = D[(D.doan == 'tat_ca') & D.pham_vi.str.startswith('gio')]
for (sym, m), G in H.groupby(['ma', 'khung']):
    out.append(f'{sym} M{m}: giờ thấp nhất p99 {G.p99.min():g} (giờ {G.loc[G.p99.idxmin(), "pham_vi"][4:]}), cao nhất {G.p99.max():g} (giờ {G.loc[G.p99.idxmax(), "pham_vi"][4:]}); '
               f'giá trị/nến {G.gt_moi_nen.min():g}..{G.gt_moi_nen.max():g}')
out.append('\n== Các dòng lệch Bid/Ask ở phân vị 99 > 10% ==')
L = D[D.co_lech_10]
out.append(f'{len(L)} / {len(D)} dòng; theo phạm vi tất cả/phiên: ' + str(len(L[~L.pham_vi.str.startswith("gio")])))
out.append(L[~L.pham_vi.str.startswith('gio')][['ma', 'khung', 'doan', 'pham_vi', 'p99_bid', 'p99_ask', 'lech_bid_ask']].to_string(index=False))
txt = '\n'.join(out)
print(txt)
open('out_r1_profile.txt', 'w', encoding='utf-8').write(txt + '\n')
