# -*- coding: utf-8 -*-
"""VÙNG VCL cho setup A-v5 (plan `plans/BENZO-A-V5-plan.md` mục 2.2, 2.3, 2.9).

KHÔNG sửa kernel.py / zones_a_v4.py / benzo_vcl.py / mọi file trong vung-canh-lenh/ — chỉ IMPORT.

Nội dung:
  * `load_rec_checked(P)`  : nạp bộ vùng hiển thị VCL v5 bằng `benzo_vcl.load_rec` (cache `v5.pkl`) RỒI kiểm khớp chuỗi nến
                             với P.df (độ dài + datetime từng phần tử qua `vcl5.load` + `vcl5.prepare`). Sai ⇒ ValueError (dừng).
  * `VclSet(rec)`          : vùng THƯA theo eid (không tạo mảng dày 86 333 nến × 4 262 eid). `view(dl)` trả bản (có thể DỜI δ theo nến,
                             cho đối chứng ĐC3) với 2 cách tra: theo eid (`lo[off[e] + (i − b0[e])]`) và theo nến (`B_*`, các vùng đang hiển thị tại nến i).

Thuật ngữ: eid = mã vùng ổn định của VCL · slot K/N/F = vùng đang chứa giá / gần / xa · bộ hiển thị = các vùng VCL đang vẽ tại nến i.
Mã hoá slot: K = 0, N = 1, F = 2.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(os.path.dirname(HERE))
VCLR = os.path.join(ROOT, 'vung-canh-lenh', 'research')

SLOT_CODE = {'K': 0, 'N': 1, 'F': 2}
SLOT_NAME = {0: 'K', 1: 'N', 2: 'F'}


def load_rec_checked(P):
    """Bộ hiển thị VCL v5 + kiểm khớp chuỗi nến (plan 2.2: bắt buộc, dừng nếu sai — benzo_vcl chỉ kiểm độ dài, chưa đủ)."""
    if VCLR not in sys.path:
        sys.path.insert(1, VCLR)
    import benzo_vcl as BV
    import vcl5 as V5
    rec = BV.load_rec(P.df)
    bars, lv = V5.load(V5.BASE90)
    ctx = V5.prepare(bars, lv)
    d2 = ctx['df']
    if len(d2) != len(P.df):
        raise ValueError('chuoi nen VCL (%d) khac P.df (%d)' % (len(d2), len(P.df)))
    if not (d2['datetime'].to_numpy() == P.df['datetime'].to_numpy()).all():
        raise ValueError('datetime nen VCL khac P.df')
    return rec


class VclView:
    """Một bản (đã dời δ hoặc không) của bộ vùng VCL — mảng phẳng, tra theo eid hoặc theo nến."""
    __slots__ = ('ne', 'off', 'b0', 'ln', 'lo', 'hi', 'slot', 'd10', 'eid_of', 'bptr', 'B_eord', 'B_lo', 'B_hi')


class VclSet:
    def __init__(self, rec, n_bars):
        r = rec.sort_values(['eid', 'bar'], kind='stable').reset_index(drop=True)
        eid = r['eid'].to_numpy()
        bar = r['bar'].to_numpy()
        self.n_bars = int(n_bars)
        ue, first, cnt = np.unique(eid, return_index=True, return_counts=True)
        self.eid_of = ue.astype(np.int64)
        self.ne = len(ue)
        self.off = first.astype(np.int64)
        self.ln = cnt.astype(np.int64)
        self.b0 = bar[first].astype(np.int64)
        self.b1 = bar[first + cnt - 1].astype(np.int64)
        # liên tục: mỗi eid hiển thị ở các nến LIỀN NHAU (plan 1: "không eid nào biến mất rồi quay lại") — kiểm, không giả định
        if not np.all((self.b1 - self.b0 + 1) == self.ln):
            raise ValueError('co eid khong lien tuc (bien mat roi quay lai)')
        self.E_bar = bar.astype(np.int64)
        self.E_lo = r['lo'].to_numpy(float)
        self.E_hi = r['hi'].to_numpy(float)
        self.E_slot = np.array([SLOT_CODE[s] for s in r['slot'].to_numpy()], dtype=np.int8)
        self.E_d10 = r['d10'].to_numpy(bool)
        self.E_side = r['side'].to_numpy(np.int8)
        # thứ tự theo nến (nến lớn, eid nhỏ) — tra "các vùng đang hiển thị tại nến i"
        pos_in_eid_order = np.arange(len(r))
        o = np.lexsort((eid, bar))
        self.B_pos = pos_in_eid_order[o]                       # vị trí trong mảng theo-eid
        self.B_bar = bar[o].astype(np.int64)
        self.B_eord = np.searchsorted(ue, eid[o]).astype(np.int64)   # thứ tự eid (0..ne−1)
        self.bptr = np.searchsorted(self.B_bar, np.arange(self.n_bars + 1)).astype(np.int64)

    def view(self, dl=None):
        """dl = mảng δ theo nến (dời bản đồ VCL, ĐC3) hoặc None."""
        v = VclView()
        v.ne, v.off, v.b0, v.ln = self.ne, self.off, self.b0, self.ln
        v.eid_of = self.eid_of
        v.slot, v.d10 = self.E_slot, self.E_d10
        if dl is None:
            v.lo, v.hi = self.E_lo, self.E_hi
        else:
            d = np.asarray(dl, float)[self.E_bar]
            v.lo, v.hi = self.E_lo + d, self.E_hi + d
        v.bptr = self.bptr
        v.B_eord = self.B_eord
        v.B_lo = v.lo[self.B_pos]
        v.B_hi = v.hi[self.B_pos]
        return v

    def active_at(self, i):
        """[(eord, lo, hi)] các vùng hiển thị tại nến i (không dời) — dùng cho test/vẽ."""
        a, b = self.bptr[i], self.bptr[i + 1]
        return [(int(self.B_eord[k]), float(self.E_lo[self.B_pos[k]]), float(self.E_hi[self.B_pos[k]])) for k in range(a, b)]
