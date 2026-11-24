"""Bước 7: dựng R1-KET-QUA.md từ các file out_r1_*.csv (chỉ đọc số, không tính lại luật).
Phần "bất thường" và "chỗ PLAN chưa nói" viết tay ở NOTES bên dưới.
Chạy: python sa_report.py"""
import os, re, numpy as np, pandas as pd

C = lambda x, d=2: ('—' if x is None or (isinstance(x, float) and not np.isfinite(x)) else (f'{x:.{d}f}'.replace('.', ',') if isinstance(x, (float, np.floating)) else str(x)))


def num(s):
    """Lấy số đầu tiên sau chữ ĐẠT/TRƯỢT/BÁO trong ô kết luận."""
    m = re.search(r'(-?\d+(?:\.\d+)?(?:e-?\d+)?)', str(s))
    return float(m.group(1)) if m else np.nan


def vd(s):
    s = str(s)
    return 'Đ' if s.startswith('ĐẠT') else ('T' if s.startswith('TRƯỢT') else '·')


def md_table(df):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(cols) + ' |', '|' + '|'.join(['---'] * len(cols)) + '|']
    for _, r in df.iterrows():
        out.append('| ' + ' | '.join(str(r[c]) for c in cols) + ' |')
    return '\n'.join(out)


L = []
w = L.append
CELLS = [('GC', 1), ('GC', 5), ('GC', 15), ('NQ', 1), ('NQ', 5), ('NQ', 15)]
CRIT41 = ['khop_chung', 'khop_phien', 'khop_gio', 'khop_ngay']
CRIT42 = ['deu_phien', 'dau_phien', 'deu_khung']
CRIT43 = ['v_top20', 'v_top5', 'v_cuc_tri', 'v_khong_nhieu', 'v_ti_hon']
VN = {'khop_chung': 'Khớp chung', 'khop_phien': 'Khớp theo phiên', 'khop_gio': 'Khớp theo giờ', 'khop_ngay': 'Khớp theo ngày',
      'deu_phien': 'Không trống Á / không dồn Mỹ', 'dau_phien': 'Nến đầu phiên', 'deu_khung': 'Đều giữa các khung',
      'v_top20': 'Không sót 20 ô lớn nhất ngày', 'v_top5': 'Không sót 5 ô lớn nhất phiên', 'v_cuc_tri': 'Không sót cực trị rõ ràng',
      'v_khong_nhieu': 'Không nhiễu', 'v_ti_hon': 'Không chấm tí hon'}

st_dot = open('out_r1_dot_selftest.txt', encoding='utf-8').read(); st_bt = open('out_r1_bt_selftest.txt', encoding='utf-8').read()
w('# Vòng 1 — kết quả đo "Không theo CORVEN" (Opus chạy, 2026-11-25)')
w('')
w('> Số đo theo đúng PLAN.md (Fable). Opus **không** đề xuất tham số mặc định và **không** kết luận phương án nào thắng: việc đó của Fable ở vòng 2.')
w('> Mọi luật ở đây là **định nghĩa hiển thị** ("ô nào bất thường về volume"), **không phải lợi thế giao dịch đã kiểm định**. Không bước nào dùng giá chạy sau đó, không bước nào dùng chart CORVEN.')
w('> Bảng rút gọn chỉ lấy **đoạn kiểm**, khung **M1 / M5 / M15**, cả GC và NQ (trừ khi ghi khác). Số đầy đủ (mọi khung, mọi đoạn, theo giờ) nằm trong các file `out_r1_*.csv`.')
w('')
w('Cách đọc tên cấu hình: `cuon_T120_p1` = phân vị cuốn 120 phút, nhóm 1% ô lớn nhất; `lam0.5` = trung bình 0,5 ô vượt mỗi nến; `cung_gio_K10_lc` = cùng khung giờ 10 ngày trước, gộp thêm khung giờ liền trước và liền sau;'
  ' `lai_med_K20` = tỉ số volume / (TB trung vị mỗi ô N nến trước), tham chiếu cùng khung giờ 20 ngày; `lai_mean_cuon1380` = tỉ số với TB volume mỗi ô, tham chiếu 1.380 phút cuốn; `z_log_T240_z3` = điểm lệch chuẩn hóa theo trung vị trên log volume, cửa sổ 240 phút, ngưỡng 3;'
  ' `ky_luc_T240_q0.25` = kỷ lục theo nến, 240 phút, xác suất danh nghĩa một nến có chấm ≈ 0,25; `ky_luc_K10` = kỷ lục theo nến, tham chiếu cùng khung giờ 10 ngày. Mốc đối chứng: `dc_dang_chay_*` (UnifiedDots, sàn 9, có che), `dc_pct5/10/15` (≥ x% volume của chính nến đó).')
w('')

# ---------------- 0. điều kiện xong ----------------
w('## 0. Điều kiện xong vòng 1')
w('')
nb = re.search(r'GC M1 (\d+) \(chuẩn 87.362\), NQ M1 (\d+)', st_dot)
w(f'- Selftest chấm (`out_r1_dot_selftest.txt`): **{st_dot.strip().splitlines()[-1]}** ({st_dot.count("ĐẠT  ")} mục ĐẠT, {st_dot.count("TRƯỢT ")} mục TRƯỢT). Gồm: 11 ví dụ tính tay; bản nhanh = bản chuẩn từng nến cho 9 cấu hình (5 phương án) trên GC M5 và NQ M15, 10 ngày giao dịch đầu: lệch ngưỡng 0, lệch vượt 0, lệch chấm 0; cắt dữ liệu tại 6 điểm, 165 + 9 + 9 cấu hình, lệch 0.')
w(f'- Selftest Big Trade (`out_r1_bt_selftest.txt`): **{st_bt.strip().splitlines()[-1]}** ({st_bt.count("ĐẠT  ")} mục ĐẠT). Bản chuẩn được nạp thêm 1.290 (GC M5) / 220 (NQ M15) nến rỗng chèn vào mọi chỗ trống: nến rỗng không có vòng, không làm lệch ngưỡng (kiểm "nến không có số liệu không được nộp").')
w(f'- Số nến: GC M1 **{int(nb.group(1)):,}**, NQ M1 **{int(nb.group(2)):,}**; nhật ký GC **22.948**, NQ **8.340** nến M1 (khớp số chuẩn). GClive 5.517 nến M1.'.replace(',', '.'))
w('- Mốc đối chứng "luật đang chạy" ra lại đúng số cũ: GC M1 Không sót sàn 5 = **80.386**, Ít nhiễu sàn 9 = **39.918**, Không sót sàn 9 = **62.768**.')
files = sorted(f for f in os.listdir('.') if f.startswith('out_r1_'))
w('- File kết quả: ' + ', '.join(f'`{f}`' for f in files) + '.')
w('')

# ---------------- 1. mô tả ----------------
P = pd.read_csv('out_r1_profile.csv')
w('## 1. Bước 1 — mô tả dữ liệu (`sa_profile.py`)')
w('')
w('Giá trị bên > 0, gộp Bid + Ask, **đoạn kiểm**. p99 theo phiên Á / Âu / Mỹ; "p99 từng ngày" = phân vị 99 tính riêng mỗi ngày giao dịch rồi lấy phân vị 10 / 50 / 90 qua các ngày.')
w('')
rows = []
for sym, m in CELLS:
    X = P[(P.ma == sym) & (P.khung == m) & (P.doan == 'kiem')]
    a = X[X.pham_vi == 'tat_ca'].iloc[0]
    s = {r.pham_vi: r for _, r in X[X.pham_vi.str.startswith('phien')].iterrows()}
    H = X[X.pham_vi.str.startswith('gio')]
    rows.append({'Mã': sym, 'Khung': f'M{m}', 'Giá trị > 0 / nến': C(a.gt_moi_nen, 1), 'p50 / p90 / p99 / p99,9': f'{C(a.p50, 0)} / {C(a.p90, 0)} / {C(a.p99, 0)} / {C(a.p999, 0)}',
                 'p99 Á / Âu / Mỹ': ' / '.join(C(s[k].p99, 0) for k in ('phien_A', 'phien_Au', 'phien_My')),
                 'p99 theo giờ thấp nhất – cao nhất': f'{C(H.p99.min(), 0)} – {C(H.p99.max(), 0)}',
                 'p99 từng ngày p10 / p50 / p90': f'{C(a.p99_ngay_p10, 0)} / {C(a.p99_ngay_p50, 0)} / {C(a.p99_ngay_p90, 0)}',
                 'p99 Bid / Ask': f'{C(a.p99_bid, 0)} / {C(a.p99_ask, 0)}'})
w(md_table(pd.DataFrame(rows)))
nflag = int(P.co_lech_10.sum()); nflag_main = int(P[P.co_lech_10 & ~P.pham_vi.str.startswith('gio')].shape[0])
w('')
w(f'- Lệch Bid / Ask ở p99 quá 10%: **{nflag_main}** dòng trong các dòng toàn bộ / theo phiên (mọi mã, khung, đoạn); {nflag} / {len(P)} dòng nếu tính cả dòng theo từng giờ (dòng theo giờ ít mẫu hơn). Lệch lớn nhất ở dòng phiên: '
  f'{C(P[~P.pham_vi.str.startswith("gio")].lech_bid_ask.max(), 3)}. Gộp Bid + Ask theo PLAN không gặp trở ngại ở mức phiên.')
w('- Số giá trị > 0 mỗi nến (dùng để biết mức p nào giải được): xem cột thứ ba; ví dụ kiểu p 0,2% cần 2.500 mẫu tham chiếu, cuốn 60 phút ở GC M1 có khoảng 60 × 27 = 1.650 mẫu nên chưa đủ (đếm ở cột "chưa có ngưỡng" của calib).')
w('')

# ---------------- 2. selftest ----------------
w('## 2. Bước 2 — cài đặt và tự kiểm (`sa_dot_rules.py`, `sa_dot_selftest.py`)')
w('')
w('Mỗi phương án có bản chuẩn từng nến (`ref_run`: mảng đếm 0..4095 + hàng đợi nến, nộp đúng một lần khi nến đóng) và bản nhanh (`evaluate`: numba / numpy). Kết quả tự kiểm ở mục 0; chi tiết từng dòng trong `out_r1_dot_selftest.txt`.')
w('')

# ---------------- 3. khớp + độ đều ----------------
S = pd.read_csv('out_r1_dot_summary.csv')
S6 = S[S.khung.isin([1, 5, 15])]
w('## 3. Bước 3 — độ khớp mức danh nghĩa và độ đều (`sa_dot_eval.py`)')
w('')
w('### 3.1 Số cấu hình ĐẠT từng tiêu chí, đoạn kiểm (trên tổng số cấu hình của phương án)')
w('')
rows = []
for pa, G in S6[~S6.phuong_an.str.startswith('dc_')].groupby('phuong_an', sort=False):
    ncfg = G.cau_hinh.nunique()
    for sym, m in CELLS:
        X = G[(G.ma == sym) & (G.khung == m)]
        r = {'Phương án': f'{pa} ({ncfg})', 'Ô': f'{sym} M{m}'}
        for c in CRIT41 + CRIT42:
            r[VN[c]] = int(X[c].astype(str).str.startswith('ĐẠT').sum()) if X[c].astype(str).str.startswith(('ĐẠT', 'TRƯỢT')).any() else 'chỉ báo'
        rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
w('"chỉ báo": tiêu chí đó với kiểu p / z_log chỉ báo cáo, không có đạt / trượt (PLAN 4.2). Hai cột "Không trống Á / không dồn Mỹ" và "Đều giữa các khung" chỉ chấm đạt / trượt cho cấu hình kiểu λ và kỷ lục, nên ở cuon / cung_gio / lai số tối đa là số cấu hình kiểu λ (16 / 24 / 32), các cấu hình kiểu p chỉ báo cáo.')
w('')
w('### 3.2 Tỉ số khớp chung, đoạn kiểm — cấu hình tốt nhất mỗi phương án (ít TRƯỢT nhất ở 4.1 + 4.2 trên 6 ô)')
w('')
best = S6[~S6.phuong_an.str.startswith('dc_')].groupby(['phuong_an', 'cau_hinh']).so_truot_41_42.sum().reset_index().sort_values('so_truot_41_42')
rows = []
for pa, G in best.groupby('phuong_an', sort=False):
    for n in G.cau_hinh.head(3):
        X = S6[S6.cau_hinh == n]
        r = {'Cấu hình': n, 'Số TRƯỢT (4.1 + 4.2)': int(G[G.cau_hinh == n].so_truot_41_42.iloc[0])}
        for sym, m in CELLS:
            x = X[(X.ma == sym) & (X.khung == m)].iloc[0]
            r[f'{sym} M{m}: khớp chung · phiên Á/Âu/Mỹ · chấm/nến'] = f'{C(num(x.khop_chung))} · {str(x.khop_phien).split(" ", 1)[1].replace(".", ",")} · {C(x.cham_nen)}'
        rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
w('### 3.3 Độ đều sau gộp và tương quan với volume ngày (đoạn kiểm; cấu hình như 3.2 và mốc đối chứng)')
w('')
D = pd.read_csv('out_r1_dot_density.csv')
D0 = D[(D.doan == 'kiem') & (D.pham_vi == 'tat_ca') & D.khung.isin([1, 5, 15])]
names = list(dict.fromkeys([n for pa, G in best.groupby('phuong_an', sort=False) for n in G.cau_hinh.head(1)] + ['dc_dang_chay_khong_sot', 'dc_dang_chay_it_nhieu', 'dc_pct10']))
rows = []
for n in names:
    for sym, m in CELLS:
        x = D0[(D0.cau_hinh == n) & (D0.ma == sym) & (D0.khung == m)]
        if not len(x): continue
        x = x.iloc[0]
        ph = D[(D.doan == 'kiem') & (D.cau_hinh == n) & (D.ma == sym) & (D.khung == m) & D.pham_vi.str.startswith('phien')].set_index('pham_vi').cham_nen
        rows.append({'Cấu hình': n, 'Ô': f'{sym} M{m}', 'Chấm/nến (Á/Âu/Mỹ)': f'{C(x.cham_nen)} ({" / ".join(C(ph.get(k)) for k in ("phien_A", "phien_Au", "phien_My"))})',
                     'Chấm/giờ': C(x.cham_gio, 1), 'Nến không chấm': C(x.ti_le_nen_khong_cham), 'Chấm 1 nến p50/p95/max': f'{C(x.cham_1nen_p50, 0)}/{C(x.cham_1nen_p95, 0)}/{int(x.cham_1nen_max)}',
                     'Nến > 5 chấm': C(x.ti_le_nen_tren5, 3), 'Nến 22:00 / 07:00 / 13:30 / 14:30 so TB phiên': ' / '.join(C(x[f'nen_{k}_so_TB_phien']) for k in ('2200', '0700', '1330', '1430')),
                     'Tỉ lệ đỏ': C(x.ti_le_do), 'Tương quan chấm ngày ~ volume ngày tương đối': C(x.tuong_quan_cham_vol_ngay)})
w(md_table(pd.DataFrame(rows)))
w('')
w('Tương quan chỉ báo cáo, không có đạt / trượt (PLAN 4.2).')
w('')

# ---------------- 4. oracle ----------------
O = pd.read_csv('out_r1_dot_oracle.csv')
O6 = O[(O.doan == 'kiem') & O.khung.isin([1, 5, 15])]
w('## 4. Bước 4 — "không bỏ sót" / "không nhiễu" trên hai thước nhìn lại (`sa_dot_oracle.py`)')
w('')
npk = O.cau_hinh.nunique() - 5
w(f'Chọn cấu hình: đạt Khớp chung (0,8–1,25) ở **đoạn chọn** ở cả 6 ô (GC, NQ) × (M1, M5, M15) → **{npk} cấu hình** (≤ 40 nên lấy hết) + 5 mốc đối chứng. Chạy trên 10 ô × 3 đoạn.')
w('Mỗi ô của bảng: tỉ lệ được nổ (tính cả gộp) của 20 ô lớn nhất ngày / 5 ô lớn nhất phiên / cực trị chặt cả hai thước · tỉ lệ chấm nhiễu (ngoài cả hai thước lỏng) · tỉ lệ chấm ≤ 3 hợp đồng; cuối ô là số tiêu chí TRƯỢT (trên 5). Ngưỡng đạt: ≥ 0,99 / ≥ 0,97 / ≥ 0,97 · ≤ 0,05 · ≤ 0,02.')
w('')
rows = []
order = O6.groupby('cau_hinh').so_truot_43.sum().sort_values()
for n in order.index:
    r = {'Cấu hình': n, 'Tổng TRƯỢT': int(order[n])}
    for sym, m in CELLS:
        x = O6[(O6.cau_hinh == n) & (O6.ma == sym) & (O6.khung == m)]
        if not len(x): r[f'{sym} M{m}'] = '—'; continue
        x = x.iloc[0]
        r[f'{sym} M{m}'] = f'{C(x.top20_ngay_gop, 3)} / {C(x.top5_phien_gop, 3)} / {C(x.chat_ca_hai_gop, 3)} · {C(x.nhieu_ngoai_ca_hai, 3)} · {C(x.cham_le_3, 3)} → {int(x.so_truot_43)}'
    rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
w('Thêm (cùng file): bản "thô" (chỉ vượt ngưỡng, không tính gộp); "nhiễu" theo cách hiểu thứ hai (không là cực trị lỏng trên ít nhất một thước) ở cột `nhieu_khong_ca_hai`; phần chấm chỉ thuộc thước cùng giờ / chỉ thuộc thước quanh nó (`chi_cung_gio`, `chi_quanh_no`); tỉ lệ chấm ≤ 5 hợp đồng.')
x = O6[O6.cau_hinh.isin(order.index[:5])].groupby('cau_hinh')[['chi_cung_gio', 'chi_quanh_no', 'nhieu_khong_ca_hai', 'cham_le_5', 'p_hat']].mean()
w('')
w('Trung bình 6 ô (đoạn kiểm) của 5 cấu hình đứng đầu bảng:')
w('')
w(md_table(x.reset_index().rename(columns={'cau_hinh': 'Cấu hình', 'chi_cung_gio': 'Chỉ thuộc thước cùng giờ', 'chi_quanh_no': 'Chỉ thuộc thước quanh nó',
                                            'nhieu_khong_ca_hai': 'Nhiễu (cách hiểu 2)', 'cham_le_5': 'Chấm ≤ 5', 'p_hat': 'p̂'}).applymap(lambda v: C(v, 3) if isinstance(v, float) else v)))
w('')

# ---------------- 6. đạt hết + ba cấu hình trượt ít nhất ----------------
w('## 5. Danh sách cấu hình đạt hết tiêu chí có ngưỡng')
w('')
M = S6.merge(O6[['cau_hinh', 'ma', 'khung'] + CRIT43 + ['so_truot_43']], on=['cau_hinh', 'ma', 'khung'], how='left')
M = M[~M.phuong_an.str.startswith('dc_')]
def fails(r, crits):
    return [f'{VN[c]}' for c in crits if str(r[c]).startswith('TRƯỢT') or (c in CRIT43 and pd.isna(r[c]))]
M['f41'] = M.apply(lambda r: fails(r, CRIT41), axis=1)
M['f42'] = M.apply(lambda r: fails(r, CRIT42), axis=1)
M['f43'] = M.apply(lambda r: fails(r, CRIT43) if pd.notna(r['v_top20']) else ['(không vào bước 4)'], axis=1)
agg = M.groupby('cau_hinh').agg(pa=('phuong_an', 'first'), n41=('f41', lambda s: sum(len(x) for x in s)), n42=('f42', lambda s: sum(len(x) for x in s)),
                                 n43=('f43', lambda s: sum(len(x) for x in s)), co4=('v_top20', lambda s: s.notna().all()))
gate = agg[(agg.n41 == 0) & (agg.co4) & (agg.n43 == 0)]
allc = gate[gate.n42 == 0]
w(f'- Đạt **4.1 + 4.3** ở đoạn kiểm, cả GC lẫn NQ, cả M1 / M5 / M15 (cổng vào vòng 2 theo PLAN 4.5): **{len(gate)}** cấu hình' + (': ' + ', '.join(f'`{n}`' for n in gate.index) if len(gate) else '.'))
w(f'- Đạt thêm cả **4.2**: **{len(allc)}** cấu hình' + (': ' + ', '.join(f'`{n}`' for n in allc.index) if len(allc) else '.'))
w('')
w('## 6. Ba cấu hình trượt ít nhất của mỗi phương án (đoạn kiểm, 6 ô GC/NQ × M1/M5/M15; đếm 4.1 + 4.3, rồi 4.2)')
w('')
w('Phương án không có cấu hình nào vào bước 4 (không đạt Khớp chung ở đoạn chọn ở cả 6 ô) thì phần 4.3 ghi "không vào bước 4".')
w('')
rows = []
for pa, G in agg.groupby('pa', sort=False):
    G = G.assign(k=G.n41 + G.n43 + np.where(G.co4, 0, 99), k2=G.n42).sort_values(['k', 'k2'])
    for n in G.index[:3]:
        X = M[M.cau_hinh == n]
        det = []
        for _, r in X.iterrows():
            f = r.f41 + r.f42 + ([x for x in r.f43 if x != '(không vào bước 4)'])
            if f: det.append(f'{r.ma} M{r.khung}: ' + ', '.join(f))
        rows.append({'Phương án': pa, 'Cấu hình': n, 'TRƯỢT 4.1': int(G.loc[n, 'n41']), 'TRƯỢT 4.3': ('không vào bước 4' if not G.loc[n, 'co4'] else int(G.loc[n, 'n43'])),
                     'TRƯỢT 4.2': int(G.loc[n, 'n42']), 'Trượt cái gì (ô: tiêu chí)': '; '.join(det) if det else '—'})
w(md_table(pd.DataFrame(rows)))
w('')

# ---------------- 7. ca biên ----------------
E = pd.read_csv('out_r1_dot_edge.csv')
w('## 7. Bước 5 — ca biên (`sa_dot_edge.py`, toàn bộ dữ liệu)')
w('')
en = list(dict.fromkeys(E.cau_hinh))
w('Cấu hình: ' + ', '.join(f'`{n}`' for n in en) + '.')
w('')
def ev(n, sym, m, ca, cs):
    x = E[(E.cau_hinh == n) & (E.ma == sym) & (E.khung == m) & (E.ca_bien == ca) & (E.chi_so == cs)]
    if not len(x): return '—'
    v = x.gia_tri.iloc[0]
    try: return C(float(v))
    except Exception: return str(v)
rows = []
for n in en:
    for sym, m in [('GC', 1), ('GC', 5), ('GC', 15), ('NQ', 1), ('NQ', 5), ('NQ', 15)]:
        rows.append({'Cấu hình': n, 'Ô': f'{sym} M{m}',
                     '1. Nến đầu chưa có ngưỡng / tỉ lệ': f'{ev(n, sym, m, "1_dau_chart", "so_nen_dau_chua_co_nguong").split(",")[0]} / {ev(n, sym, m, "1_dau_chart", "ti_le_nen_chua_co_nguong")}',
                     '2. Trùng chấm 5 ngày cuối, nạp 3/7/15 ngày trước': ' / '.join(ev(n, sym, m, '2_lich_su_da_nap', f'trung_khi_nap_{L}_ngay_truoc') for L in (3, 7, 15)),
                     '3. Chấm/nến 20 nến đầu: thứ Hai / ngày khác (khớp)': f'{ev(n, sym, m, "3_sau_cuoi_tuan", "cham_nen_thu_hai")} / {ev(n, sym, m, "3_sau_cuoi_tuan", "cham_nen_ngay_khac")} ({ev(n, sym, m, "3_sau_cuoi_tuan", "khop_thu_hai")} / {ev(n, sym, m, "3_sau_cuoi_tuan", "khop_ngay_khac")})',
                     '4. Chưa có ngưỡng giờ 21 / 22 / 23': ' / '.join(ev(n, sym, m, '4_gio_nghi', f'gio_{h}_ti_le_nen_chua_co_nguong') for h in (21, 22, 23)),
                     '5. Giờ khớp 0,5–2: 26–30/10 · 02–06/11 · 12–23/10': ' · '.join(ev(n, sym, m, '5_doi_gio', f'{k}_so_gio_khop_0.5_2') for k in ('tuan_2610_3010', 'tuan_0211_0611', 'hai_tuan_truoc_1210_2310')),
                     '7. Nến ≤ 3 ô: có chấm / chấm ≤ 3': f'{ev(n, sym, m, "7_nen_mong", "ti_le_nen_mong_co_cham")} / {ev(n, sym, m, "7_nen_mong", "gia_tri_cham_le_3_ti_le")}',
                     '8. Ngày vắng: khớp / chấm/nến; ngày sau': f'{ev(n, sym, m, "8_ngay_vang", "khop_ngay_vang")} / {ev(n, sym, m, "8_ngay_vang", "cham_nen_ngay_vang")}; {ev(n, sym, m, "8_ngay_vang", "khop_ngay_lien_sau")} / {ev(n, sym, m, "8_ngay_vang", "cham_nen_ngay_lien_sau")}'})
w(md_table(pd.DataFrame(rows)))
w('')
lowd = E[(E.ca_bien == '8_ngay_vang') & (E.chi_so == 'cac_ngay')].groupby(['ma', 'khung']).gia_tri.first()
w('Ngày vắng (volume < 50% TB 10 ngày trước): ' + '; '.join(f'{k[0]} M{k[1]}: {v}' for k, v in lowd.items() if k[1] in (1,)) + '.')
w('')
w('Ca biên 6 — NQ chạy trên **toàn bộ** file từ 26/08 (trước 14/09 NQZ26 chưa là hợp đồng chính):')
w('')
rows = []
for n in en:
    for m in (1, 5):
        X = E[(E.cau_hinh == n) & (E.ma == 'NQfull') & (E.khung == m)]
        kd = X[X.chi_so.str.startswith('khop_ngay_')]
        v = pd.to_numeric(kd.gia_tri, errors='coerce')
        rows.append({'Cấu hình': n, 'Khung': f'M{m}', 'Khớp theo ngày 07/09–25/09: thấp nhất / trung vị / cao nhất': f'{C(v.min())} / {C(v.median())} / {C(v.max())}',
                     'Ngày đầu tiên khớp trong 0,5–2 ba ngày liền (từ 27/08)': ev(n, 'NQfull', m, '6_doi_hop_dong', 'ngay_dau_tien_khop_trong_0.5_2_ba_ngay_lien'),
                     'Số ngày từ 14/09': ev(n, 'NQfull', m, '6_doi_hop_dong', 'so_ngay_tu_1409_toi_khi_khop_ngay_trong_0.5_2_ba_ngay_lien'),
                     'Nến đầu chưa có ngưỡng': ev(n, 'NQfull', m, '1_dau_chart', 'so_nen_dau_chua_co_nguong')})
w(md_table(pd.DataFrame(rows)))
w('')

# ---------------- 8. Big Trade ----------------
w('## 8. Bước 6 — Big Trade (`sa_bt_rules.py`, `sa_bt_selftest.py`, `sa_bt_eval.py`, `sa_bt_oracle.py`)')
w('')
w('> **Dữ liệu yếu, phải đọc kèm:** GC 16 phiên (31/08–23/09; 10 phiên đầu = đoạn chọn, 6 phiên cuối = đoạn kiểm); **NQ 6 phiên, không có đoạn kiểm** (mọi số NQ là toàn bộ 6 phiên, kể cả số dùng để chọn); GClive 09–24/11 đứt quãng (mỗi ngày 19–937 nến M1), là đoạn kiểm thứ hai chỉ cho cuon và ky_luc.')
w('')
BP = pd.read_csv('out_r1_bt_profile.csv')
rows = []
for k in ('GC', 'NQ', 'GClive'):
    for m in (1, 5, 15):
        X = BP[(BP.ma == k) & (BP.khung == m) & (BP.doan == 'tat_ca')]
        a = X[X.pham_vi == 'tat_ca'].iloc[0]; s = X.set_index('pham_vi')
        rows.append({'Nhật ký': k, 'Khung': f'M{m}', 'Nến có số liệu': int(a.so_nen), 'Ô/nến': C(a.o_moi_nen, 1), 'p50 / p90 / p99 / p99,9': f'{C(a.p50, 0)} / {C(a.p90, 0)} / {C(a.p99, 0)} / {C(a.p999, 0)}',
                     'p99 Á / Âu / Mỹ': ' / '.join(C(s.p99.get(f'phien_{x}'), 0) for x in ('A', 'Au', 'My')), 'p99 từng ngày p10/p50/p90': f'{C(a.p99_ngay_p10, 0)} / {C(a.p99_ngay_p50, 0)} / {C(a.p99_ngay_p90, 0)}'})
w('### 8.1 Mô tả lệnh đơn lớn nhất của ô (`out_r1_bt_profile.csv`, toàn bộ)')
w('')
w(md_table(pd.DataFrame(rows)))
w('')
LV = pd.read_csv('out_r1_bt_level.csv')
w('### 8.2 Mặt bằng cho phương án lai (`out_r1_bt_level.csv`)')
w('')
w('Hệ số biến thiên (độ lệch chuẩn / trung bình, ddof 0) của p99 tính riêng từng (ngày × phiên) có ≥ 100 ô; "so mot thô" = hệ số của L / hệ số của mot thô; đạt khi ≤ 0,7. Tỉ số Mỹ / Á = p99 gộp phiên Mỹ / p99 gộp phiên Á.')
w('')
rows = []
for (k, m), G in LV.groupby(['ma', 'khung']):
    g = G.set_index('mat_bang')
    rows.append({'Mã': k, 'Khung': f'M{m}', 'Nhóm ngày×phiên': int(g.so_nhom_ngay_phien.iloc[0]), 'Hệ số mot thô (Mỹ/Á)': f'{C(g.loc["mot_tho", "he_so_bien_thien"])} ({C(g.loc["mot_tho", "ti_so_My_A"])})',
                 **{f'{L}: so mot thô (Mỹ/Á)': f'{C(g.loc[L, "so_voi_mot_tho"])} ({C(g.loc[L, "ti_so_My_A"])}) {"ĐẠT" if g.loc[L, "dat_giam_30"] == "ĐẠT" else ""}' for L in ('med', 'mean', 'sqrtvol', 'p90_120')}})
w(md_table(pd.DataFrame(rows)))
w('')
w('Không L nào đạt ở GC (mọi khung). Ở NQ, `sqrtvol` và `p90_120` đạt ở M1, M5, M15; `mean` ở M1, M5; `med` ở M5; không L nào đạt ở M30, H1. Vì có L đạt ở ít nhất một ô, phương án lai được đo tiếp với cả bốn L trên mọi khung của GC và NQ (để có so sánh); nhóm ngày × phiên của NQ chỉ có 19.')
w('')
BS = pd.read_csv('out_r1_bt_summary.csv')
B6 = BS[BS.khung.isin([1, 5, 15])]
w('### 8.3 Khớp + độ đều (`out_r1_bt_summary.csv`; GC đoạn kiểm, NQ toàn bộ 6 phiên, GClive)')
w('')
rows = []
for pa, G in B6[~B6.phuong_an.str.startswith('dc_')].groupby('phuong_an', sort=False):
    for k in ('GC', 'NQ', 'GClive'):
        for m in (1, 5, 15):
            X = G[(G.ma == k) & (G.khung == m)]
            if not len(X): continue
            r = {'Phương án': f'{pa} ({X.cau_hinh.nunique()})', 'Ô': f'{k} M{m}'}
            for c in CRIT41 + ['deu_phien', 'dau_phien']:
                r[VN[c]] = int(X[c].astype(str).str.startswith('ĐẠT').sum()) if X[c].astype(str).str.startswith(('ĐẠT', 'TRƯỢT')).any() else 'chỉ báo'
            rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
BO = pd.read_csv('out_r1_bt_oracle.csv')
w('### 8.4 Không sót / không nhiễu (`out_r1_bt_oracle.csv`)')
w('')
nbt = BO[~BO.phuong_an.str.startswith('dc_')].cau_hinh.nunique()
w(f'Chọn: đạt Khớp chung ở đoạn chọn GC (10 phiên đầu) ở cả M1, M5, M15: 94 cấu hình, lấy 40 có độ lệch khớp theo phiên nhỏ nhất ({nbt} cấu hình có mặt) + 2 mốc đối chứng. Ô bảng như mục 4 (vòng thay chấm, gộp theo g). '
  '"nan" = cấu hình không có ở nhật ký đó: NQ chỉ thử cùng giờ K 3 / 5 (nên `cung_gio_K10*` không có ở NQ); GClive không chạy cùng giờ và lai. '
  'Ở NQ, cùng giờ K 5 cần 3 ngày trước nên 3 / 6 ngày đầu chưa có ngưỡng: tỉ lệ được nổ ≈ 0,5 là do vậy, không phải do ngưỡng.')
w('')
rows = []
BK = BO[BO.khung.isin([1, 5, 15]) & (((BO.ma == 'GC') & (BO.doan == 'kiem')) | ((BO.ma == 'NQ') & (BO.doan == 'tat_ca')) | ((BO.ma == 'GClive') & (BO.doan == 'kiem')))]
order = BK[BK.ma == 'GC'].groupby('cau_hinh').so_truot_43.sum().sort_values()
for n in order.index:
    r = {'Cấu hình': n, 'TRƯỢT GC (3 ô)': int(order[n])}
    for k in ('GC', 'NQ', 'GClive'):
        for m in (1, 5, 15):
            x = BK[(BK.cau_hinh == n) & (BK.ma == k) & (BK.khung == m)]
            if not len(x): continue
            x = x.iloc[0]
            r[f'{k} M{m}'] = f'{C(x.top20_ngay_gop, 3)} / {C(x.top5_phien_gop, 3)} / {C(x.chat_ca_hai_gop, 3)} · {C(x.nhieu_ngoai_ca_hai, 3)} · {C(x.vong_le_3, 3)} → {int(x.so_truot_43)}'
    rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
BD = pd.read_csv('out_r1_bt_density.csv')
w('### 8.5 Số vòng mỗi nến (phân vị 50 / 95 / lớn nhất), để quyết có cần giới hạn số vòng')
w('')
rows = []
for n in list(dict.fromkeys([x for x in order.index if not x.startswith('dc_')][:6] + ['dc_codinh10', 'dc_dang_chay_thich_nghi'])):
    r = {'Cấu hình': n}
    for k, d in (('GC', 'kiem'), ('NQ', 'tat_ca'), ('GClive', 'kiem')):
        for m in (1, 5, 15):
            x = BD[(BD.cau_hinh == n) & (BD.ma == k) & (BD.khung == m) & (BD.doan == d) & (BD.pham_vi == 'tat_ca')]
            if len(x):
                x = x.iloc[0]; r[f'{k} M{m}'] = f'{C(x.vong_nen)} ({C(x.vong_1nen_p50, 0)}/{C(x.vong_1nen_p95, 0)}/{int(x.vong_1nen_max)})'
    rows.append(r)
w(md_table(pd.DataFrame(rows)))
w('')
w('Ô: vòng/nến (p50 / p95 / lớn nhất số vòng một nến).')
w('')
AV = pd.read_csv('out_r1_bt_avail.csv')
w('### 8.6 Dùng được ngoài đời: tỉ lệ nến có ngưỡng trên GClive (`out_r1_bt_avail.csv`)')
w('')
AV['nhom'] = AV.cau_hinh.str.replace(r'_(p|lam)[0-9.]+$', '', regex=True)
X = AV.groupby(['phuong_an', 'khung']).ti_le_nen_co_nguong.agg(['min', 'median', 'max']).reset_index()
rows = [{'Phương án': r.phuong_an, 'Khung': f'M{r.khung}', 'Tỉ lệ nến có ngưỡng: thấp nhất / trung vị / cao nhất qua các cấu hình': f'{C(r["min"])} / {C(r["median"])} / {C(r["max"])}'} for _, r in X.iterrows()]
w(md_table(pd.DataFrame(rows)))
w('')
BM = B6.merge(BK[['cau_hinh', 'ma', 'khung'] + CRIT43], on=['cau_hinh', 'ma', 'khung'], how='left')
BM = BM[~BM.phuong_an.str.startswith('dc_')]
BM['n41'] = BM.apply(lambda r: len(fails(r, CRIT41)), axis=1); BM['n43'] = BM.apply(lambda r: len(fails(r, CRIT43)) if pd.notna(r['v_top20']) else 99, axis=1)
BM['n42'] = BM.apply(lambda r: len(fails(r, ['deu_phien', 'dau_phien'])), axis=1)
g = BM[BM.ma == 'GC'].groupby('cau_hinh')[['n41', 'n43', 'n42']].sum()
ok = g[(g.n41 == 0) & (g.n43 == 0)]
w(f'- Big Trade, cấu hình đạt 4.1 + 4.3 ở đoạn kiểm GC, cả M1 / M5 / M15: **{len(ok)}**' + (': ' + ', '.join(f'`{n}`' for n in ok.index) if len(ok) else '') + '.')
gn = BM[BM.ma == 'NQ'].groupby('cau_hinh')[['n41', 'n43']].sum()
both = [n for n in ok.index if n in gn.index and gn.loc[n, 'n41'] == 0 and gn.loc[n, 'n43'] == 0]
w(f'- Trong số đó, đạt luôn trên NQ (6 phiên, không có đoạn kiểm): **{len(both)}**' + (': ' + ', '.join(f'`{n}`' for n in both) if both else '') + '.')
w('')
w('Ba cấu hình trượt ít nhất mỗi phương án (Big Trade; GC đoạn kiểm + NQ 6 phiên, M1/M5/M15; đếm 4.1 + 4.3 rồi 4.2):')
w('')
rows = []
for pa, G in BM.groupby('phuong_an', sort=False):
    gg = G[G.ma.isin(['GC', 'NQ'])].groupby('cau_hinh')[['n41', 'n43', 'n42']].sum()
    hasnq = G[G.ma == 'NQ'].cau_hinh.unique()
    gg = gg.assign(k=gg.n41 + gg.n43 + np.where(gg.index.isin(hasnq), 0, 1000)).sort_values(['k', 'n42'])
    for n in gg.index[:3]:
        det = []
        for _, r in G[(G.cau_hinh == n) & G.ma.isin(['GC', 'NQ'])].iterrows():
            f = fails(r, CRIT41) + fails(r, ['deu_phien', 'dau_phien']) + (fails(r, CRIT43) if pd.notna(r['v_top20']) else ['không vào bước 4.3'])
            if f: det.append(f'{r.ma} M{r.khung}: ' + ', '.join(f))
        if n not in hasnq: det.append('KHÔNG có số NQ (NQ chỉ thử K 3 / 5), chỉ tính trên GC')
        rows.append({'Phương án': pa, 'Cấu hình': n, 'TRƯỢT 4.1': int(gg.loc[n, 'n41']), 'TRƯỢT 4.3': int(gg.loc[n, 'n43']) if gg.loc[n, 'n43'] < 99 else 'không vào',
                     'TRƯỢT 4.2': int(gg.loc[n, 'n42']), 'Trượt cái gì': '; '.join(det) if det else '—'})
w(md_table(pd.DataFrame(rows)))
w('')
w(open('NOTES_R1.md', encoding='utf-8').read())
txt = '\n'.join(L) + '\n'
open('R1-KET-QUA.md', 'w', encoding='utf-8').write(txt)
open('r1_results.md', 'w', encoding='utf-8').write('# Kết quả vòng 1\n\nBản đầy đủ: [R1-KET-QUA.md](R1-KET-QUA.md) (cùng nội dung).\n\n' + txt)
print(f'ghi R1-KET-QUA.md ({len(txt)} ký tự)')
