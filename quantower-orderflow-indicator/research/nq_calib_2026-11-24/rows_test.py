"""NQ: chart CORVEN gộp 8 tick (2,0 điểm) một hàng. Chạy luật chấm trên HÀNG 8 tick rồi so với chấm CORVEN theo hàng."""
import numpy as np, pandas as pd
from corven_nq_compare import corven_nq, corven_gc
from dots import dots
R = 8
C, cov, _ = corven_nq()
def rowify(F0, R):
    F = F0.copy(); F['tk'] = np.floor_divide(F.tk, R)
    F = F.groupby(['t', 'tk'])[['bid', 'ask', 'vol']].sum().reset_index()
    st = F.groupby('t').vol.median()
    B = st.shift(1).rolling(20, min_periods=5).mean()   # mức nền theo HÀNG, nến liền trước (chuỗi liên tục cả 90 ngày)
    F['B_med'] = F.t.map(B)
    return F
Fall = pd.read_pickle('F_NQ_m1.pkl')
Fr = rowify(Fall, R); Fr = Fr[Fr.t.isin(cov)]
print('B_med hàng (trung vị):', Fr.groupby('t').B_med.first().median())
def match_rows(C, Rr, sh):
    Cr = C.copy(); Cr['row'] = np.floor_divide(Cr.tk + sh, R)
    Cg = {t: g for t, g in Cr.groupby('t')}; Rg = {t: g for t, g in Rr.groupby('t')}
    hit = sum(1 for r in Cr.itertuples() if (g := Rg.get(r.t)) is not None and ((g if r.color == 'tim' else g[g.col == ('B' if r.color == 'xanh' else 'S')]).tk == r.row).any())
    hit2 = sum(1 for r in Rr.itertuples() if (g := Cg.get(r.t)) is not None and (g[g.color.isin(['tim', 'xanh' if r.col == 'B' else 'do'])].row == r.tk).any())
    rec, prec = hit / len(Cr), hit2 / max(len(Rr), 1)
    return rec, prec, 2 * rec * prec / (rec + prec) if rec + prec else 0
# tìm độ dịch pha bằng luật lỏng
Rl = dots(Fr, 1.5, 1, 1, -1)
sh = max(range(0, R), key=lambda s: match_rows(C, Rl, s)[2]); print('dịch pha tốt nhất', sh, match_rows(C, Rl, sh))
rows = []
for k in (1.5, 2.0, 2.4, 2.8, 3.2, 3.6):
    for w in (0, 1, 2, 3, 4):
        for h in (-1, 0, 1):
            for fl in (9, 20):
                Rr = dots(Fr, k, w, fl, h)
                rec, prec, f1 = match_rows(C, Rr, sh)
                rows.append(dict(k=k, w_hang=w, che_hang=h, san=fl, cham_nen=round(len(Rr) / len(cov), 2), do=round((Rr.col == 'S').sum() / len(cov), 2), xanh=round((Rr.col == 'B').sum() / len(cov), 2), recall=round(rec, 2), precision=round(prec, 2), F1=round(f1, 3)))
D = pd.DataFrame(rows)
print('CORVEN', round(len(C) / len(cov), 2), 'chấm/nến')
print(D.sort_values('F1', ascending=False).head(15).to_string(index=False))
print(D[(D.k == 2.8) & (D.w_hang == 4) & (D.san == 9)].to_string(index=False))
print(D[D.precision >= 0.9].sort_values('recall', ascending=False).head(10).to_string(index=False))
