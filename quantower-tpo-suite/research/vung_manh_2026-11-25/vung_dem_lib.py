#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vung_dem_lib.py — nạp dữ liệu cho phép đo vùng đệm (gc, nq25). Giá trong D đã chia SCALE (bước 0,1)."""
import os, sys, tempfile, importlib
import numpy as np

SCALE = {'gc': 1.0, 'nq25': 2.5, 'nq': 2.5}


def load(sym):
    os.environ['VM_CACHE'] = os.path.join(os.environ.get('VM_CACHE_DIR', tempfile.gettempdir()), 'vm1_%s.pkl' % sym)
    import vm
    importlib.reload(vm)
    if sym.startswith('nq'): vm.SPLICE_JUMP = 1e12       # một hợp đồng: bộ chặn chỗ nối tắt (PLAN 12.3)
    D = vm.Data(cache=os.environ['VM_CACHE'])
    if sym.startswith('nq'):
        def rows_over_nq(self, a, b, row=vm.ROW):
            tk, v = self.ticks_over(a, b)
            if len(tk) == 0: return np.array([]), np.array([])
            rid = np.round((tk * 0.25) / 0.5).astype(np.int64)
            u, inv = np.unique(rid, return_inverse=True)
            return u * row, np.bincount(inv, weights=v)
        type(D).rows_over = rows_over_nq
    import vung_manh as V
    importlib.reload(V)
    return D, vm, V
