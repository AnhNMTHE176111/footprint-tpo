"""Biến thể thứ 4: thêm dấu hiệu 'trap trong nhịp hồi' (thế B): ô ngược phe ≥ 3× nền_ô và ≥ 10 trong các nến trước CF
của cửa sổ, CF đóng vượt qua giá ô đó theo hướng S. Đo trên TRAIN cùng 3 sửa đổi."""
import sys, os
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import setup_corven as SC, variants_nguoihoc as VU
ORIG_FS = SC.find_signs
def fs2(c, f, cp):
    sg = ORIG_FS(c, f, cp)
    if c.the != 'B' or 'trap' in sg:
        return sg
    S, cf = c.S, c.cf
    best = None
    for k in range(c.w0, cf):
        bs = f.base[k]
        if not np.isfinite(bs) or bs <= 0: continue
        for (p, bv, av, v) in f.bars[k].levels:
            vol = bv if S > 0 else av
            if vol >= 3 * bs and vol >= 10 and (f.C[cf] - p) * S > 0:
                if best is None or vol > best[0]: best = (vol, k, p)
    if best:
        sg['trap'] = (f"trap hồi {'bóng đỏ' if S > 0 else 'bóng xanh'} {best[0]:.0f} @{best[2]/10:.1f}", best[1], best[2])
    return sg
if __name__ == '__main__':
    cut = SC.train_cut()
    bars, df = SC.load_train(cut=cut)
    good = (~df['thin'].to_numpy()) & (~df['splice'].to_numpy()) & (df['split'].to_numpy() == 'TRAIN')
    sg_ = sorted(set(df['session_id'].to_numpy()[good]))
    SC.find_signs = fs2
    rows = []
    for v in [(0,0,0),(1,0,0),(1,1,1)]:
        R = VU.run(bars, df, good, *v)
        s = VU.summ(R, sg_); s.update(hoi=v[0], bo_qs=v[1], bo_rmin=v[2], trap_hoi=1); rows.append(s)
    print(pd.DataFrame(rows).round(3).to_string())
