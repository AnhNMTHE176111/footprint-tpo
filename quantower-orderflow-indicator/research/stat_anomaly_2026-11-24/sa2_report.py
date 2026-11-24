"""Viết R2-KET-QUA.md (và bản sao r2_results.md) từ các file out_r2_*.csv. Chạy sau sa2_selftest, sa2_dot_eval, sa2_bt_eval, sa2_corven, sa2_numbers."""
import numpy as np, pandas as pd

S = pd.read_csv('out_r2_dot_score.csv'); DST = pd.read_csv('out_r2_dot_dst.csv'); SH = pd.read_csv('out_r2_dot_short.csv')
RO = pd.read_csv('out_r2_dot_roll.csv'); OD = pd.read_csv('out_r2_dot_oddtf.csv'); CO = pd.read_csv('out_r2_corven.csv')
B = pd.read_csv('out_r2_bt_score.csv'); E = pd.read_csv('out_r2_bt_evening.csv'); CH = pd.read_csv('out_r2_chuan.csv')
ST = open('out_r2_selftest.txt', encoding='utf-8').read().strip().splitlines()
PICK = open('out_r2_bt_pick.txt', encoding='utf-8').read().strip().splitlines()
O = []
w = O.append


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return '—'
    if isinstance(x, (int, np.integer)): return f'{x:,}'.replace(',', '.')
    return f'{x:.{d}f}'.replace('.', ',')


def tbl(head, rows):
    w('| ' + ' | '.join(head) + ' |'); w('|' + '---|' * len(head))
    for r in rows: w('| ' + ' | '.join(str(x) for x in r) + ' |')
    w('')


CFG_VN = {'goc': 'gốc (Chicago, K 10, lân cận, tối thiểu 3 ngày, T 120, p 2%)', 'gio_utc': 'giờ UTC', 'K5': 'K = 5', 'K20': 'K = 20', 'khong_lan_can': 'không lân cận',
          'toi_thieu_1_ngay': 'tối thiểu 1 ngày', 'toi_thieu_2_ngay': 'tối thiểu 2 ngày', 'T240': 'dự phòng T = 240', 'p1': 'p = 1%', 'p0.5': 'p = 0,5%',
          'dc_dang_chay_khong_sot': 'đối chứng: luật đang chạy, bộ Không sót (sàn 9, che)', 'dc_dang_chay_it_nhieu': 'đối chứng: luật đang chạy, bộ Ít nhiễu (sàn 9, che)'}
CRIT_VN = {'khop_chung': 'Khớp chung', 'khop_phien': 'Khớp theo phiên', 'khop_gio': 'Khớp theo giờ', 'top20': '20 ô lớn nhất ngày', 'top5': '5 ô lớn nhất phiên',
           'cuc_tri': 'cực trị rõ', 'nhieu': 'nhiễu', 'ti_hon': 'chấm tí hon'}
ORDER = [c for c in CFG_VN]

w('# Kết quả vòng 2 — chế độ ngưỡng "Không theo CORVEN" (Opus chạy, 2026-11-25)')
w('')
w('> Làm theo `r1_review.md` mục 6. Chỉ Python, chưa sửa C#, chưa commit. Mọi con số là **định nghĩa hiển thị** (ô nào đáng nổ bóng theo thống kê volume), '
  '**không phải lợi thế giao dịch**. Không dùng giá chạy sau đó ở bất cứ bước nào; chart CORVEN chỉ được so ở mục 7 để tham khảo.')
w('> Opus không chọn mặc định; mục 11 chỉ ghi kết quả áp ba luật chọn đã viết trước.')
w('')
w('Script (cùng thư mục): `sa2_lib.py` (giờ Chicago, luật chấm bản nhanh, cửa sổ Big Trade A/B/C, thước có chia lý do sót), `sa2_ref.py` (bản chuẩn từng nến đọc CSV của Golden), '
  '`sa2_selftest.py`, `sa2_dot_eval.py`, `sa2_bt_eval.py`, `sa2_corven.py`, `sa2_numbers.py`, `sa2_report.py`. Kết quả: `out_r2_*.csv`, `out_r2_selftest.txt`, `out_r2_bt_pick.txt`.')
w('')

# ---------------- 1. tự kiểm
npass = sum(l.startswith('ĐẠT') for l in ST if l[:4] in ('ĐẠT ', 'TRƯỢ'))
w('## 1. Tự kiểm')
w('')
w(f'`out_r2_selftest.txt`: {ST[-1]}')
w('')
w('Gồm: ví dụ tính tay (ngưỡng chính, dự phòng, "lớn hơn hẳn" + gộp ±w, cửa sổ Big Trade A/B/C); bản chuẩn `sa2_ref.py` (đọc đúng CSV mà `Golden stophunt --levels` đọc) = bản nhanh **từng dấu** '
  'trên GC M5, GC H1 (7 cấu hình), NQ M1 (gốc, p 1%), NQ M15 (7 cấu hình); Big Trade trên `btlog_{NQ_M1, NQ_M15, GC_M5, GC_M30}` (3 tổ hợp mỗi file, có cả B và C); '
  'cắt dữ liệu ở 60% số nến (ngưỡng và dấu trước điểm cắt y hệt); nạp 8 ngày cuối (bản chuẩn đọc từ đầu ngày thứ 8 = bản nhanh trên dữ liệu cắt, GC M5 và NQ M15).')
w('')
bad = [l for l in ST if l.startswith('TRƯỢT')]
if bad:
    w('Mục TRƯỢT:'); [w('- ' + l) for l in bad]; w('')

# ---------------- 2. bảng điểm chấm
w('## 2. Chấm Bid/Ask — số lần trượt trên 6 ô (GC, NQ × M1, M5, M15)')
w('')
w('Tiêu chí có ngưỡng (8): Khớp chung 0,8–1,25 · Khớp theo phiên · Khớp theo giờ (≥ 20 giờ trong 0,5–2) · 20 ô lớn nhất ngày ≥ 99% · 5 ô lớn nhất phiên ≥ 97% · '
  'cực trị rõ ≥ 97% · nhiễu ≤ 5% · chấm ≤ 3 hợp đồng ≤ 2%. "Khớp theo ngày" và "Nến đầu phiên" chỉ báo cáo (có trong `out_r2_dot_score.csv`, cột `v_khop_ngay`, `v_dau_phien`). '
  'Đoạn: GC chọn 11/08–04/10, kiểm 05/10–09/11; NQ chọn 14/09–25/10, kiểm 26/10–24/11. Thước, ngày chấm điểm, phiên, giờ giữ như vòng 1 (UTC) cho mọi cấu hình.')
w('')
s6 = S[S.khung.isin([1, 5, 15])]
rows = []
for c in ORDER:
    g = s6[s6.cau_hinh == c]
    a = int(g[g.doan == 'chon'].so_truot.sum()); b = int(g[g.doan == 'kiem'].so_truot.sum())
    det = '; '.join(f'{r.ma} M{r.khung} {"chọn" if r.doan == "chon" else "kiểm"}: ' + ', '.join(f'{CRIT_VN[k]} {r["v_" + k].split(" ", 1)[1] if k not in ("ti_hon",) else r.v_ti_hon.split(" ", 1)[1]}' for k in r.truot_gi.split(';'))
                    for _, r in g[g.so_truot > 0].iterrows())
    rows.append((CFG_VN[c], a, b, a + b, det or '—'))
tbl(['Cấu hình', 'Trượt đoạn chọn', 'Trượt đoạn kiểm', 'Tổng', 'Trượt cái gì'], rows)

w('### 2.1 Cấu hình gốc, từng ô (M1 … H1, hai đoạn)')
w('')
g = S[S.cau_hinh == 'goc']
rows = []
for _, r in g.sort_values(['ma', 'khung', 'doan']).iterrows():
    rows.append((r.ma, f'M{r.khung}' if r.khung < 60 else 'H1', 'chọn' if r.doan == 'chon' else 'kiểm', f(r.khop_chung, 2), f'{f(r.khop_A, 2)} / {f(r.khop_Au, 2)} / {f(r.khop_My, 2)}',
                 r.v_khop_gio.split(' ', 1)[1].split(' (')[0], f(r.top20), f(r.top5), f(r.cuc_tri), f(r.nhieu), f(r.le3), r.so_truot))
tbl(['Mã', 'Khung', 'Đoạn', 'Khớp chung', 'Khớp Á / Âu / Mỹ', 'Giờ đạt', '20 lớn nhất ngày', '5 lớn nhất phiên', 'Cực trị rõ', 'Nhiễu', '≤ 3 hợp đồng', 'Số trượt'], rows)
w('Ô "20 lớn nhất ngày" / "5 lớn nhất phiên" bị sót chia hai loại trong `out_r2_dot_score.csv` (`*_sot_chua_nguong`, `*_sot_vi_nguong`). Cấu hình gốc:')
w('')
rows = []
for _, r in g[g.khung.isin([1, 5, 15])].sort_values(['ma', 'khung', 'doan']).iterrows():
    rows.append((r.ma, f'M{r.khung}', 'chọn' if r.doan == 'chon' else 'kiểm', f'{r.top20_sot_chua_nguong} / {r.top20_sot_vi_nguong} (trên {r.top20_so_o})',
                 f'{r.top5_sot_chua_nguong} / {r.top5_sot_vi_nguong} (trên {r.top5_so_o})', f'{r.cuc_tri_sot_chua_nguong} / {r.cuc_tri_sot_vi_nguong} (trên {r.cuc_tri_so_o})'))
tbl(['Mã', 'Khung', 'Đoạn', '20 lớn nhất ngày: sót chưa ngưỡng / vì ngưỡng', '5 lớn nhất phiên', 'Cực trị rõ'], rows)

w('### 2.2 Mật độ (cấu hình gốc)')
w('')
rows = []
for _, r in g.sort_values(['ma', 'khung', 'doan']).iterrows():
    rows.append((r.ma, f'M{r.khung}' if r.khung < 60 else 'H1', 'chọn' if r.doan == 'chon' else 'kiểm', f(r.cham_nen, 2), f'{f(r.cham_nen_A, 2)} / {f(r.cham_nen_Au, 2)} / {f(r.cham_nen_My, 2)}',
                 f'{f(r.cham_1nen_p50, 0)} / {f(r.cham_1nen_p95, 0)} / {r.cham_1nen_max}', f'{f(r.vuot_tho_nen, 2)} (p95 {f(r.vuot_tho_1nen_p95, 0)}, max {r.vuot_tho_1nen_max})',
                 f'{f(r.ngay_cham_nen_min, 2)} / {f(r.ngay_cham_nen_p10, 2)} / {f(r.ngay_cham_nen_p50, 2)} / {f(r.ngay_cham_nen_p90, 2)} / {f(r.ngay_cham_nen_max, 2)}',
                 f'{r.ngay_it_nhat[5:]} · {r.ngay_nhieu_nhat[5:]}', f(r.ti_le_do, 2)))
tbl(['Mã', 'Khung', 'Đoạn', 'Chấm/nến', 'Á / Âu / Mỹ', 'Chấm 1 nến p50 / p95 / max', 'Vượt thô/nến', 'Chấm/nến theo ngày: min / p10 / p50 / p90 / max', 'Ngày ít · nhiều nhất', 'Tỉ lệ đỏ'], rows)

w('Chấm/nến đoạn kiểm theo khung và cấu hình (M1 / M5 / M15 / M30 / H1):')
w('')
rows = []
for c in ORDER:
    for sym in ('GC', 'NQ'):
        x = S[(S.cau_hinh == c) & (S.ma == sym) & (S.doan == 'kiem')].sort_values('khung')
        rows.append((CFG_VN[c].split(' (')[0], sym, ' / '.join(f(v, 2) for v in x.cham_nen)))
tbl(['Cấu hình', 'Mã', 'Chấm/nến M1 / M5 / M15 / M30 / H1'], rows)

w('### 2.3 Ngưỡng theo phiên (cấu hình gốc, phân vị 10 / 50 / 90 của ngưỡng mỗi nến, hợp đồng) và tỉ lệ nến có ngưỡng < 5')
w('')
rows = []
for _, r in g.sort_values(['ma', 'khung', 'doan']).iterrows():
    rows.append((r.ma, f'M{r.khung}' if r.khung < 60 else 'H1', 'chọn' if r.doan == 'chon' else 'kiểm',
                 *[f'{f(r[f"nguong_{s}_p10"], 0)} / {f(r[f"nguong_{s}_p50"], 0)} / {f(r[f"nguong_{s}_p90"], 0)}' for s in ('A', 'Au', 'My')], f(r.ti_le_nen_nguong_duoi5, 4),
                 f'{f(r.ti_le_nen_chinh, 3)} / {f(r.ti_le_nen_du_phong, 3)} / {f(r.ti_le_nen_chua_co, 4)}'))
tbl(['Mã', 'Khung', 'Đoạn', 'Á', 'Âu', 'Mỹ', 'Nến ngưỡng < 5', 'Nến: ngưỡng chính / dự phòng / chưa có'], rows)

# ---------------- 3. đổi giờ
w('## 3. Tuần đổi giờ: số giờ (UTC) có tỉ số khớp trong 0,5–2')
w('')
w('26–30/10: châu Âu đã đổi, Mỹ chưa (giờ Chicago và UTC cho cùng khung giờ nên hai cột trùng nhau). 02–06/11: Mỹ đã đổi. Kèm hai tuần trước mỗi tuần để so. Giờ lệch ghi dạng giờ:tỉ số.')
w('')
rows = []
for sym in ('GC', 'NQ'):
    for m in (1, 5, 15):
        for t in ('26-30/10', '02-06/11', '2 tuần trước 26/10', '2 tuần trước 02/11'):
            a = DST[(DST.cau_hinh == 'goc') & (DST.ma == sym) & (DST.khung == m) & (DST.tuan == t)]
            b = DST[(DST.cau_hinh == 'gio_utc') & (DST.ma == sym) & (DST.khung == m) & (DST.tuan == t)]
            if not len(a): continue
            a = a.iloc[0]; b = b.iloc[0]
            rows.append((sym, f'M{m}', t, f'{a.so_gio_dat}/{a.so_gio_co_nen}', f'{b.so_gio_dat}/{b.so_gio_co_nen}', a.gio_lech if isinstance(a.gio_lech, str) else '—', b.gio_lech if isinstance(b.gio_lech, str) else '—'))
tbl(['Mã', 'Khung', 'Tuần', 'Giờ Chicago (gốc)', 'Giờ UTC', 'Giờ lệch (Chicago)', 'Giờ lệch (UTC)'], rows)

# ---------------- 4. chuyển hợp đồng
w('## 4. Chuyển hợp đồng (NQ toàn bộ file từ 26/08, cấu hình gốc)')
w('')
rows = []
for d in sorted(RO.ngay.unique()):
    a = RO[(RO.ngay == d) & (RO.khung == 1)]; b = RO[(RO.ngay == d) & (RO.khung == 5)]
    rows.append((d[5:], f(a.cham_nen.iloc[0], 2) if len(a) else '—', f(a.ti_so_khop.iloc[0], 2) if len(a) else '—', f(b.cham_nen.iloc[0], 2) if len(b) else '—', f(b.ti_so_khop.iloc[0], 2) if len(b) else '—'))
tbl(['Ngày', 'M1 chấm/nến', 'M1 tỉ số khớp', 'M5 chấm/nến', 'M5 tỉ số khớp'], rows)

# ---------------- 5. nạp ít ngày
w('## 5. Chart nạp ít ngày (cắt còn 8 ngày giao dịch cuối, theo ngày Chicago)')
w('')
w('Tỉ lệ trùng = số chấm chung / số chấm hợp, so với khi nạp toàn bộ, trên 8 ngày đó. Các tham số khác như gốc. Lưu ý: kể cả ngày cuối cũng không thể trùng 1,0 vì nạp ít ngày thì ngưỡng chính chỉ có ≤ 7 ngày trước (K = 10).')
w('')
rows = []
for (mi, T), gg in SH.groupby(['toi_thieu', 'T']):
    per = ' · '.join(f'{r.ma} M{r.khung} {f(r.trung)}' for _, r in gg.iterrows())
    rows.append((mi, T, f(gg.chung.sum() / gg.hop.sum(), 4), f(gg.ngay_thap_nhat.min()), per))
tbl(['Tối thiểu (ngày)', 'T dự phòng', 'Trùng gộp 6 ô', 'Ngày thấp nhất', 'Từng ô'], rows)
w('Tỉ lệ trùng theo ngày (cấu hình gốc = tối thiểu 3, T 120):')
w('')
for _, r in SH[(SH.toi_thieu == 3) & (SH['T'] == 120)].iterrows():
    w(f'- {r.ma} M{r.khung}: {r.theo_ngay}')
w('')

# ---------------- 6. khung lạ
w('## 6. Khung lạ (dựng từ bảng M1, cấu hình gốc)')
w('')
rows = [(r.ma, {3: 'M3', 10: 'M10', 240: 'H4'}[r.khung], {'chon': 'chọn', 'kiem': 'kiểm', 'tat_ca': 'tất cả'}[r.doan], f(r.so_nen), f(r.ti_le_nen_co_nguong, 4),
         f'{f(r.ti_le_nen_chinh)} / {f(r.ti_le_nen_du_phong)}', f(r.cham_nen, 2), f(r.khop_chung, 2), f'{f(r.khop_A, 2)} / {f(r.khop_Au, 2)} / {f(r.khop_My, 2)}') for _, r in OD.iterrows()]
tbl(['Mã', 'Khung', 'Đoạn', 'Số nến', 'Nến có ngưỡng', 'Chính / dự phòng', 'Chấm/nến', 'Khớp chung', 'Khớp Á / Âu / Mỹ'], rows)

# ---------------- 7. CORVEN
w('## 7. So tham khảo với chart CORVEN (chỉ báo số, không chỉnh theo)')
w('')
w('Cách khớp của `../dot_floor_2026-11-24/floor_corven.py`: cùng nến, cùng màu (tím = cả hai), cách ≤ 3 tick. NQ: chart CORVEN gộp hàng 8 tick, chỉ tham khảo.')
w('')
rows = [(r.ma, f'M{r.khung}', CFG_VN.get(r.cau_hinh, r.cau_hinh).split(' (')[0] if not r.cau_hinh.startswith('dc_') else CFG_VN[r.cau_hinh], r.so_nen_mau, f(r.cham_CORVEN_nen, 2), f(r.cham_minh_nen, 2),
         f(r.recall), f(r.precision)) for _, r in CO.iterrows()]
tbl(['Mã', 'Khung', 'Cấu hình', 'Nến mẫu', 'CORVEN chấm/nến', 'Mình chấm/nến', 'Recall (chấm CORVEN được bắt)', 'Precision'], rows)

# ---------------- 8. Big Trade
w('## 8. Big Trade — phân vị cuốn trên lệnh đơn, cửa sổ A / B / C')
w('')
w('A = max(5, T/phút) nến có số liệu gần nhất; B = như A, thiếu 5/p mẫu thì lấy thêm nến cũ hơn, tối đa 1.380 phút; C = như B, bỏ nến cũ hơn 720 phút. '
  'Thước đã sửa: 20 ô lớn nhất ngày chỉ tính ngày ≥ 400 nến M1; 5 ô lớn nhất phiên chỉ (ngày × phiên) ≥ 60 nến M1; Khớp theo giờ đạt khi ≥ 5/6 số giờ có nến trong 0,5–2. '
  'NQ chỉ 6 phiên, không có đoạn kiểm; GClive đứt quãng. Kết luận Big Trade vẫn yếu hơn chấm.')
w('')
key_rows = [('GC', 'chon'), ('GC', 'kiem'), ('NQ', 'tat_ca'), ('GClive', 'kiem')]
names = [n for n in B.cau_hinh.unique()]
w('### 8.1 Tóm tắt M1 / M5 / M15 (giá trị theo thứ tự M1 / M5 / M15)')
w('')
rows = []
for nm in names:
    for k, d in key_rows:
        x = B[(B.cau_hinh == nm) & (B.ma == k) & (B.doan == d) & B.khung.isin([1, 5, 15])].sort_values('khung')
        if not len(x): continue
        j = lambda col, dd=3: ' / '.join(f(v, dd) for v in x[col])
        rows.append((nm, k, {'chon': 'chọn', 'kiem': 'kiểm', 'tat_ca': 'tất cả'}[d], j('ti_le_nen_co_nguong'), j('khop_chung', 2), j('top20'), j('top5'), j('cuc_tri'), j('nhieu', 4), j('vong_nen', 2),
                     ' / '.join(str(v).split(' ')[0] for v in x.v_khop_gio)))
tbl(['Tổ hợp', 'Nhật ký', 'Đoạn', 'Nến có ngưỡng', 'Khớp chung', '20 lớn nhất ngày', '5 lớn nhất phiên', 'Cực trị rõ', 'Nhiễu', 'Vòng/nến', 'Khớp theo giờ'], rows)
w('### 8.2 Sót chia lý do: "20 lớn nhất ngày" (chưa có ngưỡng / vì ngưỡng, trên số ô), M1 / M5 / M15')
w('')
rows = []
for nm in names:
    cells = []
    for k, d in key_rows:
        x = B[(B.cau_hinh == nm) & (B.ma == k) & (B.doan == d) & B.khung.isin([1, 5, 15])].sort_values('khung')
        cells.append(' · '.join(f'{a}/{b} ({c})' for a, b, c in zip(x.top20_sot_chua_nguong, x.top20_sot_vi_nguong, x.top20_so_o)))
    rows.append((nm, *cells))
tbl(['Tổ hợp', 'GC chọn', 'GC kiểm', 'NQ', 'GClive'], rows)
w('### 8.3 Vòng/nến theo phiên, phân vị số vòng một nến, ngưỡng theo phiên (tổ hợp `cuon_A_T240_p1`, mọi khung)')
w('')
rows = []
x = B[B.cau_hinh == 'cuon_A_T240_p1'].sort_values(['ma', 'doan', 'khung'])
for _, r in x.iterrows():
    rows.append((r.ma, {'chon': 'chọn', 'kiem': 'kiểm', 'tat_ca': 'tất cả'}[r.doan], f'M{r.khung}' if r.khung < 60 else 'H1', f'{f(r.vong_nen_A, 2)} / {f(r.vong_nen_Au, 2)} / {f(r.vong_nen_My, 2)}',
                 f'{f(r.vong_1nen_p50, 0)} / {f(r.vong_1nen_p95, 0)} / {r.vong_1nen_max}', f'{f(r.khop_A, 2)} / {f(r.khop_Au, 2)} / {f(r.khop_My, 2)}',
                 *[f'{f(r[f"nguong_{s}_p10"], 0)} / {f(r[f"nguong_{s}_p50"], 0)} / {f(r[f"nguong_{s}_p90"], 0)}' for s in ('A', 'Au', 'My')]))
tbl(['Nhật ký', 'Đoạn', 'Khung', 'Vòng/nến Á / Âu / Mỹ', 'Vòng 1 nến p50 / p95 / max', 'Khớp Á / Âu / Mỹ', 'Ngưỡng Á p10/50/90', 'Âu', 'Mỹ'], rows)
w('Toàn bộ tổ hợp, mọi khung, có trong `out_r2_bt_score.csv` (cùng cột).')
w('')
w('### 8.4 Nhật ký chỉ có buổi tối (12:00–18:00 UTC mỗi ngày)')
w('')
w('"Trùng" = vòng chung / vòng hợp so với khi có nhật ký đầy đủ, trên các nến có trong cả hai. "20 lớn nhất ngày" ở đây tính trên ngày có ≥ 300 nến M1 (xem mục 10).')
w('')
rows = []
for nm in names:
    for k in ('GC', 'NQ'):
        x = E[(E.cau_hinh == nm) & (E.ma == k) & E.khung.isin([1, 5, 15])].sort_values('khung')
        if not len(x): continue
        rows.append((nm, k, x.so_buoi.iloc[0], ' / '.join(f'{f(a, 1)} (max {b})' for a, b in zip(x.nen_dau_chua_nguong_tb, x.nen_dau_chua_nguong_max)),
                     ' / '.join(f(v) for v in x.trung), ' / '.join(f(v) for v in x.top20), ' / '.join(f'{a}/{b}' for a, b in zip(x.top20_sot_chua_nguong, x.top20_sot_vi_nguong))))
tbl(['Tổ hợp', 'Nhật ký', 'Số buổi', 'Nến đầu buổi chưa có ngưỡng TB (max), M1 / M5 / M15', 'Trùng', '20 lớn nhất ngày', 'Sót chưa ngưỡng / vì ngưỡng'], rows)

# ---------------- 9. số chuẩn
w('## 9. Số chuẩn cho C# (bản chuẩn `sa2_ref.py`, đọc đúng file của Golden)')
w('')
w('Thư mục tạm `SCR` = `C:\\Users\\anhla\\AppData\\Local\\Temp\\claude\\39bcbe610c8d657f\\ce3fca11-3030-4b09-9b13-33a6dd7ee683\\scratchpad`. '
  '`tf/fp_GC_m1.csv` được dựng mới bằng `python ../nq_calib_2026-11-24/tf_csv.py 1 SCR/tf GC` (các file khác có sẵn). File dấu: `SCR/marks_r2_*.csv` (định dạng `--marks` của Golden).')
w('')
rows = []
for _, r in CH.iterrows():
    nm = {'goc': 'gốc', 'p1': 'p = 1%'}.get(r.cau_hinh, r.cau_hinh)
    btv = '' if pd.isna(r.big_trade) else f(int(r.big_trade))
    rows.append((r.ma, f'M{int(r.khung)}' if r.khung < 60 else 'H1', nm, f(int(r.so_nen)), f(int(r.cham_do_Bid)), f(int(r.cham_xanh_Ask)), btv or '—',
                 f'{int(r.nen_nguong_chinh)} / {int(r.nen_du_phong)} / {int(r.nen_chua_co)}', r.sha1_footprint[:12], r.sha1_bars[:12], (r.sha1_btlog[:12] if isinstance(r.sha1_btlog, str) and r.sha1_btlog else '—')))
tbl(['Mã', 'Khung', 'Cấu hình', 'Số nến', 'Chấm đỏ (Bid)', 'Chấm xanh (Ask)', 'Vòng Big Trade', 'Nến ngưỡng chính / dự phòng / chưa có', 'sha1 levels', 'sha1 bars', 'sha1 btlog'], rows)
w('Lệnh đã chạy (mỗi dòng bảng trên một lệnh; sha1 đầy đủ trong `out_r2_chuan.csv`):')
w('')
w('```')
for _, r in CH.iterrows(): w(r.lenh)
w('```')
w('')
w('Lệnh Golden tương ứng (vòng 3, khi C# có chế độ mới): `dotnet .../Golden.dll stophunt --tick <0.1|0.25> [--symbol NQZ26] --minutes <phút> --levels <file> --work <tạm> --marks <file> '
  '[--zeromot --btlog <nhật ký>] --set <ô chế độ>=...`. So theo (giờ nến, loại, tick), vì giá chấm C# là `tick × cỡ tick` (có thể ra 4419.200000000001).')
w('')
w('### 9.1 Chỗ bản chuẩn phải đoán hành vi C#')
w('')
for s in [
    'Volume không nguyên: bản chuẩn lấy phần nguyên (floor) của Bid / Ask trước khi đếm. Trên mọi file đã chạy không có giá trị không nguyên (cột `gia_tri_khong_nguyen` = 0), nên chưa thử được.',
    'Nến không có ô nào: C# ComputeBar thoát sớm (không dấu). Bản chuẩn: nến như vậy vẫn là một nến đóng — nộp 0 mẫu vào hàng đợi dự phòng, tính là một nến, và đánh dấu (ngày, khung) có xuất hiện. Các file đã chạy không có nến như vậy (đã kiểm GC M5 / H1, NQ M15 / H1: 0 nến không có ô), nên chưa thử được; C# cần chốt một cách.',
    'Ô có volume nhưng Bid = Ask = 0 (GC M5 có 2.582 ô, GC H1 227, NQ 8): không nộp mẫu nào, nhưng vẫn tính vào biên độ nến (w) như `CellBigLogic.BarRangeTicks` (ô Vol > 0).',
    'Nến có ô nhưng không có giá trị bên nào > 0: vẫn là nến trong hàng đợi dự phòng và vẫn đánh dấu (ngày, khung) có xuất hiện (vòng 1 đã làm vậy; GC M1 có 11 nến).',
    'Lần xuất hiện của khung giờ = (ngày luật, khung) có ít nhất một nến ĐÃ ĐÓNG; nến đang chạy (nến cuối file) không nộp gì.',
    'Ngưỡng chính tính một lần khi bước sang (ngày, khung) mới; trong cùng (ngày, khung) các nến đóng chỉ cộng vào "hôm nay" nên không làm đổi ngưỡng chính. Ngưỡng dự phòng tính lại mỗi nến.',
    'Big Trade: nến có ô trong nhật ký nhưng không có trong footprint bị bỏ (C# chỉ đi các nến của chart); ô trùng tick giữ lệnh lớn hơn (`CellsOf`). Hàng đợi chỉ gồm nến có số liệu; cửa sổ C so giờ mở nến (bỏ nến có giờ mở < giờ mở nến đang xét − 720 phút).',
    'Biên độ cho g (Big Trade) = tick lớn nhất − nhỏ nhất của các ô có lệnh đơn của nến (như `BigTradeAdaptive.AddClosedBar`), trung bình N nến có số liệu trước, cần ≥ 5.',
    'Giờ Chicago tính từ cột datetime của CSV coi là UTC (data-export/README: export mới ghi UTC); nếu chart C# chạy múi giờ khác, phải đổi TimeLeft về UTC trước khi áp luật.',
]: w('- ' + s)
w('')

# ---------------- 10. bất thường
w('## 10. Bất thường và chỗ chỉ dẫn chưa nói rõ (đã chọn cách làm)')
w('')
sh = SH.groupby(['toi_thieu', 'T'])[['chung', 'hop']].sum()
for s in [
    'Tên file: chỉ dẫn vòng 2 (r1_review mục 6) đặt tiền tố `sa2_`, `out_r2_*.csv`, `R2-KET-QUA.md`; lệnh giao việc nói tiền tố `r2_` và `r2_results.md`. Đã giữ tên theo r1_review và ghi thêm `r2_results.md` cùng nội dung.',
    'Thước chấm điểm (ngày chấm điểm = UTC + 2 giờ, khung thước cùng giờ theo UTC, phiên, giờ UTC) giữ nguyên vòng 1 cho MỌI cấu hình, kể cả cấu hình giờ Chicago; chỉ luật bên trong đổi ngày / khung. Nếu đổi thước sang giờ Chicago thì số "cực trị rõ" và "Khớp theo giờ" có thể khác.',
    'Tuần đổi giờ: giờ Chicago KHÔNG cải thiện rõ "Khớp theo giờ" trong tuần 02–06/11 trên thước giờ UTC (mục 3; Chicago so với UTC): NQ M1 20/23 so với 18/23, NQ M5 16/23 = 16/23, NQ M15 14/23 so với 15/23, GC M1 21/23 so với 23/23, GC M5 20/23 = 20/23, GC M15 19/23 so với 17/23. Phần lệch chủ yếu là các giờ 16–19 và 21 UTC có tỉ số 0,2–0,4 ở CẢ HAI cách, tức tuần đó volume giờ Mỹ thấp hơn 10 ngày trước, không phải lỗi khung giờ.',
    'Chuyển hợp đồng (mục 4): ngày 14/09 tỉ số khớp 16,4 (M1) và 21,3 (M5), chấm/nến 1,74 và 3,12; về trong 0,5–2 từ 22/09 (M1) và 22/09 (M5), cao hơn 2 tới 21/09. Khớp với nhận xét vòng 1 (khoảng 6 ngày).',
    'Chart nạp ít ngày: với K = 10, 8 ngày nạp không bao giờ trùng 1,0 kể cả ngày cuối (ngưỡng chính chỉ có ≤ 7 ngày). Ngày thứ 3 sau khi mở chart (khi tối thiểu 3 ngày bắt đầu dùng ngưỡng chính) có tỉ lệ trùng thấp nhất của cấu hình gốc (GC M15 0,47–0,56; NQ M5 0,60–0,62).',
    'Big Trade, phép thử buổi tối: mốc "ngày ≥ 400 nến M1" không ngày nào đạt (buổi tối tối đa 360 nến M1), nên đã dùng mốc ≥ 300 nến M1 cho riêng phép thử này (GC 16 ngày, NQ 6 ngày đạt). Luật chọn 6.3 dùng số này.',
    'Big Trade, phép thử buổi tối: cửa sổ A và B không có giới hạn thời gian nên đầu mỗi buổi dùng luôn lệnh đơn của buổi tối hôm trước (nến đầu buổi chưa có ngưỡng TB khoảng 1 nến M1, chỉ buổi đầu tiên mới chờ). Cửa sổ C bỏ dữ liệu cũ hơn 720 phút nên mỗi buổi phải chờ lại (GC M1 TB 22 nến).',
    'Big Trade A và B cho kết quả gần như trùng nhau ở T = 240, p 1% (B chỉ khác khi cửa sổ A thiếu 500 mẫu, chuyện rất hiếm ở T = 240).',
    'Big Trade GClive "Khớp theo giờ" giờ tính trên số giờ có nến (≥ 5/6), không còn lỗi 19/24 của vòng 1.',
    'So CORVEN: chỉ có mẫu M1 (GC 580 nến, NQ 534 nến). Cấu hình gốc vẽ ít chấm hơn hẳn CORVEN (GC 0,32 so với 1,53 chấm/nến) nên recall thấp (0,25) nhưng precision 0,99. Không chỉnh gì theo số này.',
    'Khung lạ H4: số nến ít (GC 398, NQ 320), khớp theo phiên lệch (GC kiểm Mỹ 0,52; NQ kiểm Á 0,41) — 6 khung giờ một ngày, mỗi khung chỉ 1 nến/ngày nên tập tham chiếu nhỏ.',
]: w('- ' + s)
w('')

# ---------------- 11. luật chọn
w('## 11. Kết quả áp các luật chọn viết trước (Opus không tự chọn mặc định)')
w('')
tot = {c: int(s6[s6.cau_hinh == c].so_truot.sum()) for c in ORDER if not c.startswith('dc_')}
g0 = tot['goc']
better = [c for c in tot if c != 'goc' and tot[c] < g0]
k5 = tot['K5'] == g0
w(f'- **Luật 1 (biến thể thay gốc khi tổng trượt hai đoạn ít hơn gốc; bằng nhau giữ gốc, riêng K = 5 thắng khi bằng):** gốc trượt {g0} lần (hai đoạn cộng lại). '
  + ('Tổng trượt từng biến thể: ' + ', '.join(f'{CFG_VN[c].split(" (")[0]} {v}' for c, v in tot.items() if c != 'goc') + '. ')
  + (f'Biến thể ít hơn gốc: {", ".join(better)}. ' if better else 'Không biến thể nào trượt ít hơn gốc. ')
  + ('K = 5 trượt BẰNG gốc → theo luật, **K = 5 thay K = 10**; các yếu tố khác giữ như gốc.' if k5 and not better else ''))
best = sh.assign(r=sh.chung / sh.hop).r
mx = best.max(); tie = best[best >= mx - 0.01]
pick = (3, 120) if (3, 120) in tie.index else best.idxmax()
w(f'- **Luật 2 (số ngày tối thiểu và T: tỉ lệ chấm trùng cao nhất ở phép thử nạp ít ngày; lệch dưới 0,01 thì 3 ngày, T = 120):** tỉ lệ trùng gộp 6 ô: '
  + ', '.join(f'tối thiểu {a} ngày T {b}: {f(v, 4)}' for (a, b), v in best.items()) + f'. Cao nhất {f(mx, 4)} ({best.idxmax()[0]} ngày, T {best.idxmax()[1]}); các tổ hợp lệch dưới 0,01: '
  + ', '.join(f'({a} ngày, T {b})' for a, b in tie.index) + f'. (3 ngày, T 120) {"nằm" if (3, 120) in tie.index else "KHÔNG nằm"} trong nhóm đó → theo luật: **tối thiểu {pick[0]} ngày, T = {pick[1]}**.')
gfail = s6[(s6.cau_hinh == 'goc') & (s6.so_truot > 0)]
w('- **Luật 3 (mức mặc định 2% nếu gốc không trượt gì ngoài hai tiêu chí chỉ báo cáo):** '
  + ('gốc không trượt tiêu chí nào → mức 2%.' if not len(gfail) else 'gốc CÓ trượt: ' + '; '.join(f'{r.ma} M{r.khung} {"chọn" if r.doan == "chon" else "kiểm"} — ' + ', '.join(CRIT_VN[k] for k in r.truot_gi.split(';')) for _, r in gfail.iterrows())
     + ' → báo để Fable quyết (Opus không đổi mức).'))
w('- **Luật Big Trade (6.3):** ' + ' / '.join(PICK[-1:]))
w('')
w('Chi tiết áp luật Big Trade (`out_r2_bt_pick.txt`):')
w('')
for l in PICK: w('- ' + l)
w('')
txt = '\n'.join(O) + '\n'
open('R2-KET-QUA.md', 'w', encoding='utf-8').write(txt)
open('r2_results.md', 'w', encoding='utf-8').write(txt)
print('đã ghi R2-KET-QUA.md và r2_results.md', len(O), 'dòng')
