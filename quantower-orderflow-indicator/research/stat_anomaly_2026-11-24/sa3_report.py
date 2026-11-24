"""Vòng 3: dựng R3-KET-QUA.md (và r3_results.md cùng nội dung) từ out_r3_*.csv và out_r3_selftest.txt; áp từng luật chọn viết trước (r2_review.md 6.2)
— chỉ áp và ghi kết quả, KHÔNG chọn mặc định. Chạy: python sa3_report.py"""
import numpy as np, pandas as pd

S = pd.read_csv('out_r3_dot_score.csv')
T5 = pd.read_csv('out_r3_dot_t5gio.csv')
SH = pd.read_csv('out_r3_dot_short.csv')
CO = pd.read_csv('out_r3_corven.csv')
CH = pd.read_csv('out_r3_chuan.csv')
ST = open('out_r3_selftest.txt', encoding='utf-8').read().strip().splitlines()

CFG_ORDER = ['nen_moi', 'sel_lmax', 'khong_lan_can', 'p1', 'p0.5', 'toi_thieu_1_ngay', 'dc_dang_chay_khong_sot', 'dc_dang_chay_it_nhieu']
CFG_VN = {'nen_moi': 'Nền mới (giờ Chicago, K 5, có lân cận, tối thiểu 2 ngày, T 120, p 2%, chọn tham lam)',
          'sel_lmax': 'Nền mới, chọn "lớn hơn hẳn" như vòng 2', 'khong_lan_can': 'Nền mới, không gộp khung lân cận',
          'p1': 'Nền mới, p = 1%', 'p0.5': 'Nền mới, p = 0,5%', 'toi_thieu_1_ngay': 'Nền mới, tối thiểu 1 ngày',
          'dc_dang_chay_khong_sot': 'Đối chứng: luật đang chạy, bộ "Không sót"', 'dc_dang_chay_it_nhieu': 'Đối chứng: luật đang chạy, bộ "Ít nhiễu"'}
DOAN_VN = {'chon': 'đoạn chọn', 'kiem': 'đoạn kiểm'}
CRIT_VN = {'khop_chung': 'Khớp chung', 'khop_phien': 'Khớp theo phiên', 'khop_gio': 'Khớp theo giờ', 'top20': '20 ô lớn nhất ngày', 'top5': '5 ô lớn nhất phiên',
           'cuc_tri': 'cực trị rõ', 'nhieu': 'nhiễu', 'ti_hon': 'chấm ≤ 3 hợp đồng'}
SIX = S.khung.isin([1, 5, 15])


def f(x, d=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return '–'
    s = f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',').replace(' ', '.')
    return s


def n0(x):
    return f'{int(x):,}'.replace(',', '.')


def pct(x, d=1):
    return '–' if not np.isfinite(x) else f(x * 100, d) + '%'


def vn_fail(s):
    if not isinstance(s, str) or not s: return ''
    out = []
    for part in s.split('; '):
        k, v = part.split(' ', 1)
        out.append(f'{CRIT_VN.get(k, k)} {v.replace(".", ",")}')
    return '; '.join(out)


L = []
w = L.append
w('# Kết quả vòng 3 — chế độ ngưỡng "Không theo CORVEN" (thống kê)')
w('')
w('> Opus đo theo `r2_review.md` mục 6. Chỉ Python, không sửa C#, không commit. Script: `sa3_lib.py`, `sa3_ref.py`, `sa3_selftest.py`, `sa3_dot_eval.py`, '
  '`sa3_corven.py`, `sa3_numbers.py`, `sa3_report.py`. Kết quả: `out_r3_*.csv`.')
w('> Mọi số ở đây là **định nghĩa hiển thị** (bóng = volume bất thường so với chính quá khứ của nó), không phải lợi thế giao dịch. Không dùng giá, không nhìn tương lai.')
w('> Opus **không** chọn mặc định; mục 9 chỉ áp từng luật chọn viết trước và ghi kết quả.')
w('')
w('Thuật ngữ trong bảng: **số cũ** = ô được tính khi vượt ngưỡng thô hoặc có chấm gần (cách vòng 2); **số "nhìn thấy"** = ô được tính chỉ khi cùng nến, cùng bên '
  'có chấm cách ≤ w tick (thứ người học thấy trên chart). Đạt / trượt của 20 ô lớn nhất ngày (≥ 99%), 5 ô lớn nhất phiên (≥ 97%), cực trị rõ (≥ 97%) tính trên số "nhìn thấy". '
  'Chọn "lớn hơn hẳn" = chấm khi ô lớn hơn hẳn mọi tick khác cùng bên trong ±w (vòng 2). Chọn tham lam = duyệt ô vượt ngưỡng từ lớn xuống, bằng nhau thì tick thấp trước, '
  'giữ ô nếu chưa có chấm nào cách ≤ w tick (giống `CellBigLogic.MergeAdjacent`).')
w('')

# ---------------- 1. tự kiểm
ok = sum(x.startswith('ĐẠT') for x in ST if not x.startswith('TỔNG'))
tot = sum(1 for x in ST if not x.startswith('TỔNG'))
w('## 1. Tự kiểm')
w('')
w(f'**{ok}/{tot} ĐẠT** (`out_r3_selftest.txt`). Gồm:')
w('- Tính tay chọn tham lam: hai ô 50 và 50 cách 1 tick → giữ ô tick thấp; chuỗi 60 / 55 / 52 ở tick 200 / 203 / 206 với w = 4 → chấm ở 200 và 206 '
  '(chọn "lớn hơn hẳn" chỉ ra 200, chọn mọi ô ra cả ba); hàm chọn trực tiếp với chuỗi 20 / 15 / 12 ở tick 0 / 3 / 6 → giữ tick 0 và 6. Cả bản nhanh lẫn bản chuẩn.')
w('- Khung lân cận bỏ trùng: khung 12 giờ (2 khung/ngày) lấy 400 mẫu, khung ngày (1 khung/ngày) lấy 200 mẫu (không cộng chính nó ba lần); bản chuẩn = bản nhanh.')
w('- Nến rỗng (không ô nào volume > 0) bị bỏ hẳn ở bản chuẩn: chèn 2 nến rỗng, dấu và số nến chính / dự phòng / chưa có y hệt.')
w('- Dữ liệu giả (nhiều giá trị bằng nhau) M1 / M30 / M720 × 3 cách chọn × có / không lân cận: bản chuẩn = bản nhanh.')
w('- Dữ liệu thật: bản chuẩn = bản nhanh từng dấu trên GC M5, GC H1, NQ M1, NQ M15 cho chọn tham lam và "lớn hơn hẳn" (thêm chọn mọi ô, không lân cận, p 1% trên GC M5 và NQ M15); '
  'cắt dữ liệu ở 60% số nến cho ngưỡng và chấm trước điểm cắt y hệt; nạp 8 ngày cuối (GC M5, NQ M15) bản chuẩn = bản nhanh. CSV của Golden không có nến rỗng nào.')
w('')
w('<details><summary>Từng dòng tự kiểm</summary>')
w('')
w('```')
L.extend(ST)
w('```')
w('</details>')
w('')

# ---------------- 2. tổng trượt
w('## 2. Bảng điểm: tổng số lần trượt (6 ô = GC, NQ × M1, M5, M15; 8 tiêu chí)')
w('')
w('| Cấu hình | Trượt đoạn chọn | Trượt đoạn kiểm | Tổng | Trượt cái gì |')
w('|---|---|---|---|---|')
for c in CFG_ORDER:
    x = S[SIX & (S.cau_hinh == c)]
    a = int(x[x.doan == 'chon'].so_truot.sum()); b = int(x[x.doan == 'kiem'].so_truot.sum())
    gi = '; '.join(f'{r.ma} M{r.khung} {DOAN_VN[r.doan]}: {vn_fail(r.truot_gi)}' for r in x[x.so_truot > 0].itertuples())
    if c.startswith('dc_'):
        gi = (f'mỗi ô trượt cả 3 tiêu chí không sót (20 ô lớn nhất ngày {f(x.top20_nt.min())}–{f(x.top20_nt.max())}; 5 ô lớn nhất phiên {f(x.top5_nt.min())}–{f(x.top5_nt.max())}; '
              f'cực trị rõ {f(x.cuc_tri_nt.min())}–{f(x.cuc_tri_nt.max())}); Khớp không áp dụng')
    w(f'| {CFG_VN[c]} | {a} | {b} | {a + b} | {gi or "không"} |')
w('')
w('Ô M30 và H1 (chỉ báo, không tính vào luật chọn):')
w('')
w('| Cấu hình | Trượt M30 + H1 (hai mã, hai đoạn) | Trượt cái gì |')
w('|---|---|---|')
for c in CFG_ORDER[:6]:
    x = S[~SIX & (S.cau_hinh == c)]
    gi = '; '.join(f'{r.ma} M{r.khung} {DOAN_VN[r.doan]}: {vn_fail(r.truot_gi)}' for r in x[x.so_truot > 0].itertuples())
    w(f'| {CFG_VN[c]} | {int(x.so_truot.sum())} | {gi or "không"} |')
w('')

# ---------------- 3. bảng điểm chi tiết
w('## 3. Bảng điểm chi tiết (số cũ → số "nhìn thấy")')
w('')
for c in CFG_ORDER:
    w(f'### {CFG_VN[c]}')
    w('')
    w('| Mã | Khung | Đoạn | Khớp chung | 20 ô lớn nhất ngày (cũ → nhìn thấy) | 5 ô lớn nhất phiên | cực trị rõ | nhiễu | chấm ≤ 3 HĐ | chấm/nến | Trượt |')
    w('|---|---|---|---|---|---|---|---|---|---|---|')
    x = S[S.cau_hinh == c].sort_values(['ma', 'khung', 'doan'])
    for r in x.itertuples():
        w(f'| {r.ma} | M{r.khung} | {DOAN_VN[r.doan]} | {f(r.khop_chung) if not c.startswith("dc_") else "–"} | {f(r.top20_cu)} → **{f(r.top20_nt)}** | {f(r.top5_cu)} → **{f(r.top5_nt)}** | '
          f'{f(r.cuc_tri_cu)} → **{f(r.cuc_tri_nt)}** | {pct(r.nhieu, 2)} | {pct(r.le3, 2)} | {f(r.cham_nen, 2)} | {vn_fail(r.truot_gi) or "0"} |')
    w('')

# ---------------- 4. mật độ
w('## 4. Mật độ: nền mới và chọn "lớn hơn hẳn"')
w('')
w('Chấm/nến tính trên nến có ngưỡng. "Vượt thô" = số ô vượt ngưỡng mỗi nến trước bước chọn (như nhau ở hai cách chọn). Theo ngày = chấm/nến của từng ngày giao dịch.')
w('')
w('| Mã | Khung | Đoạn | Cách chọn | Chấm/nến | Á | Âu | Mỹ | Một nến: P50 / P95 / lớn nhất | Vượt thô/nến (P95, lớn nhất) | Theo ngày: nhỏ nhất / P10 / P50 / P90 / lớn nhất |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
for (ma, kh, do), _ in S[S.cau_hinh == 'nen_moi'].groupby(['ma', 'khung', 'doan'], sort=True):
    for c, lab in (('nen_moi', 'tham lam'), ('sel_lmax', 'lớn hơn hẳn')):
        r = S[(S.cau_hinh == c) & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].iloc[0]
        w(f'| {ma} | M{kh} | {DOAN_VN[do]} | {lab} | {f(r.cham_nen, 2)} | {f(r.cham_nen_A, 2)} | {f(r.cham_nen_Au, 2)} | {f(r.cham_nen_My, 2)} | '
          f'{f(r.cham_1nen_p50, 0)} / {f(r.cham_1nen_p95, 0)} / {r.cham_1nen_max} | {f(r.vuot_tho_nen, 2)} ({f(r.vuot_tho_1nen_p95, 0)}, {r.vuot_tho_1nen_max}) | '
          f'{f(r.ngay_cham_nen_min, 2)} / {f(r.ngay_cham_nen_p10, 2)} / {f(r.ngay_cham_nen_p50, 2)} / {f(r.ngay_cham_nen_p90, 2)} / {f(r.ngay_cham_nen_max, 2)} |')
w('')
w('Tăng số chấm khi đổi "lớn hơn hẳn" sang tham lam (chấm/nến, %):')
w('')
w('| Mã | Đoạn | M1 | M5 | M15 | M30 | H1 |')
w('|---|---|---|---|---|---|---|')
for ma in ('GC', 'NQ'):
    for do in ('chon', 'kiem'):
        cells = []
        for kh in (1, 5, 15, 30, 60):
            a = S[(S.cau_hinh == 'nen_moi') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].cham_nen.iloc[0]
            b = S[(S.cau_hinh == 'sel_lmax') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].cham_nen.iloc[0]
            cells.append('+' + f(100 * (a / b - 1), 1) + '%')
        w(f'| {ma} | {DOAN_VN[do]} | ' + ' | '.join(cells) + ' |')
w('')
w('Ngưỡng theo phiên (hợp đồng, P50 và khoảng P10–P90 của ngưỡng mỗi nến; như nhau ở hai cách chọn):')
w('')
w('| Mã | Khung | Đoạn | Á | Âu | Mỹ | Nến có ngưỡng chính / dự phòng / chưa có |')
w('|---|---|---|---|---|---|---|')
for r in S[S.cau_hinh == 'nen_moi'].sort_values(['ma', 'khung', 'doan']).itertuples():
    w(f'| {r.ma} | M{r.khung} | {DOAN_VN[r.doan]} | {f(r.nguong_A_p50, 0)} ({f(r.nguong_A_p10, 0)}–{f(r.nguong_A_p90, 0)}) | {f(r.nguong_Au_p50, 0)} ({f(r.nguong_Au_p10, 0)}–{f(r.nguong_Au_p90, 0)}) | '
      f'{f(r.nguong_My_p50, 0)} ({f(r.nguong_My_p10, 0)}–{f(r.nguong_My_p90, 0)}) | {pct(r.ti_le_nen_chinh)} / {pct(r.ti_le_nen_du_phong)} / {pct(r.ti_le_nen_chua_co, 2)} |')
w('')

# ---------------- 5. top5 phiên theo giờ
w('## 5. "5 ô lớn nhất phiên" bị sót (số "nhìn thấy"), NQ M15 và M30, theo giờ UTC')
w('')
w('| Khung | Đoạn | Cấu hình | Tổng ô sót / tổng ô | Giờ UTC: số ô sót (trong số ô top 5 rơi vào giờ đó) |')
w('|---|---|---|---|---|')
for (kh, do, c), x in T5.groupby(['khung', 'doan', 'cau_hinh'], sort=True):
    x = x[x.o_sot > 0].sort_values('o_sot', ascending=False)
    tt = T5[(T5.khung == kh) & (T5.doan == do) & (T5.cau_hinh == c)].iloc[0]
    gi = ', '.join(f'{r.gio_utc}: {r.o_sot} ({r.o_top5_gio_nay})' for r in x.itertuples()) or 'không sót'
    w(f'| M{kh} | {DOAN_VN[do]} | {"có lân cận" if c == "nen_moi" else "không lân cận"} | {tt.tong_sot} / {tt.tong_o} | {gi} |')
w('')
w('13:00–13:30 UTC là nửa giờ ngay trước giờ mở cửa cổ phiếu Mỹ (13:30 UTC). Có lân cận thì khung này mượn mẫu của khung 13:30 (mở cửa) nên ngưỡng bị kéo lên; '
  'không lân cận thì gần như hết sót ở giờ đó nhưng trượt Khớp chung ở nhiều ô hơn (mục 2).')
w('')

# ---------------- 6. nạp ít ngày
w('## 6. Chart nạp ít ngày (nền mới; thêm tối thiểu 1 ngày và chọn "lớn hơn hẳn" để so)')
w('')
w('Tỉ lệ trùng = số chấm có ở cả hai / số chấm có ở ít nhất một, trên những ngày có trong bản nạp ít (so với khi nạp đủ 90 ngày).')
w('')
w('| Cấu hình | Nạp 3 ngày | Nạp 8 ngày | Nạp 15 ngày |')
w('|---|---|---|---|')
g = SH.groupby(['cau_hinh', 'so_ngay_nap'])[['chung', 'hop']].sum(); g['trung'] = g.chung / g.hop
for c in ('nen_moi', 'toi_thieu_1_ngay', 'sel_lmax'):
    w(f'| {CFG_VN[c]} | ' + ' | '.join(f(g.loc[(c, nd), 'trung']) for nd in (3, 8, 15)) + ' |')
w('')
w('| Mã | Khung | Số ngày nạp | Nền mới: trùng (ngày thấp nhất) | Tối thiểu 1 ngày | Chọn "lớn hơn hẳn" | Nền mới theo ngày |')
w('|---|---|---|---|---|---|---|')
for (ma, kh, nd), x in SH.groupby(['ma', 'khung', 'so_ngay_nap'], sort=True):
    a = x[x.cau_hinh == 'nen_moi'].iloc[0]; b = x[x.cau_hinh == 'toi_thieu_1_ngay'].iloc[0]; c_ = x[x.cau_hinh == 'sel_lmax'].iloc[0]
    w(f'| {ma} | M{kh} | {nd} | {f(a.trung)} ({f(a.ngay_thap_nhat)}) | {f(b.trung)} ({f(b.ngay_thap_nhat)}) | {f(c_.trung)} ({f(c_.ngay_thap_nhat)}) | '
      f'{a.theo_ngay.replace(".", ",") if nd <= 8 else "(xem CSV)"} |')
w('')
w('Ngày đầu tiên của bản nạp ít luôn thấp nhất: mọi khung giờ còn đang dùng ngưỡng dự phòng (120 phút gần nhất) vì chưa có ngày trước.')
w('')

# ---------------- 7. CORVEN
w('## 7. So tham khảo với chart CORVEN (M1, chỉ báo số, không chỉnh theo)')
w('')
w('| Mã | Cấu hình | Nến mẫu | Chấm CORVEN/nến | Chấm mình/nến | Bắt được chấm CORVEN | Chấm mình trùng CORVEN | F1 |')
w('|---|---|---|---|---|---|---|---|')
for r in CO.itertuples():
    w(f'| {r.ma} | {CFG_VN[r.cau_hinh]} | {r.so_nen_mau} | {f(r.cham_CORVEN_nen, 2)} | {f(r.cham_minh_nen, 2)} | {pct(r.recall)} | {pct(r.precision)} | {f(r.F1)} |')
w('')
w('NQ: chart CORVEN gộp hàng 8 tick nên so khớp kém tin cậy hơn GC.')
w('')

# ---------------- 8. số chuẩn
w('## 8. Số chuẩn cho C# (bản chuẩn `sa3_ref.py`, đọc đúng file của Golden)')
w('')
w('Theo ngày UTC: `out_r3_chuan_ngay.csv`. Lệnh, sha1 từng file đầu vào và đường dẫn file dấu: `out_r3_chuan.csv`.')
w('')
w('| Dòng | Số nến | Chấm đỏ (Bid) | Chấm xanh (Ask) | Big Trade | Nến ngưỡng chính / dự phòng / chưa có | sha1 footprint (8 ký tự đầu) |')
w('|---|---|---|---|---|---|---|')
for r in CH.itertuples():
    bt = '–' if pd.isna(r.big_trade) else n0(r.big_trade) + (f' (vòng 2: {n0(r.big_trade_vong2)}, {"khớp" if r.big_trade_khop_vong2 else "KHÁC"})' if 'big_trade_vong2' in CH and not pd.isna(r.big_trade_vong2) else '')
    btn = '' if pd.isna(r.big_trade) else f'; nến Big Trade có ngưỡng {n0(r.nen_bt_co_nguong)}, chưa có {n0(r.nen_bt_chua_co)}'
    w(f'| {r.dong} | {n0(r.so_nen)} | {n0(r.cham_do_Bid)} | {n0(r.cham_xanh_Ask)} | {bt} | {n0(r.nen_nguong_chinh)} / {n0(r.nen_du_phong)} / {n0(r.nen_chua_co)}{btn} | {r.sha1_footprint[:8]} |')
w('')
w('<details><summary>Lệnh đã chạy và sha1 đầy đủ</summary>')
w('')
for r in CH.itertuples():
    w(f'- `{r.dong}`: `{r.lenh}`  ')
    w(f'  sha1 footprint `{r.sha1_footprint}`, bars `{r.sha1_bars}`' + (f', nhật ký `{r.sha1_btlog}`' if isinstance(r.sha1_btlog, str) and r.sha1_btlog else ''))
w('</details>')
w('')

# ---------------- 9. luật chọn
w('## 9. Áp luật chọn viết trước (Opus chỉ áp, không chọn mặc định)')
w('')
key6 = [(ma, kh, do) for ma in ('GC', 'NQ') for kh in (1, 5, 15) for do in ('chon', 'kiem')]
g1, g2, g3 = [], [], []
for ma, kh, do in key6:
    a = S[(S.cau_hinh == 'nen_moi') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].iloc[0]
    b = S[(S.cau_hinh == 'sel_lmax') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].iloc[0]
    lab = f'{ma} M{kh} {DOAN_VN[do]}'
    if not (a.top20_nt >= b.top20_nt): g1.append(f'{lab} ({f(a.top20_nt)} < {f(b.top20_nt)})')
    if not (a.nhieu <= 0.05 and a.le3 <= 0.02): g2.append(f'{lab} (nhiễu {pct(a.nhieu, 2)}, ≤ 3 HĐ {pct(a.le3, 2)})')
    if not (a.cham_nen <= 1.15 * b.cham_nen): g3.append(f'{lab} (+{f(100 * (a.cham_nen / b.cham_nen - 1), 1)}%)')
inc = [100 * (S[(S.cau_hinh == 'nen_moi') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].cham_nen.iloc[0] /
              S[(S.cau_hinh == 'sel_lmax') & (S.ma == ma) & (S.khung == kh) & (S.doan == do)].cham_nen.iloc[0] - 1) for ma, kh, do in key6]
r1 = not (g1 or g2 or g3)
w(f'1. **Chọn tham lam thay "lớn hơn hẳn"**: {"ĐÚNG cả ba điều trên 12/12 ô → luật cho thay" if r1 else "SAI → luật không cho thay"}. '
  f'(a) 20 ô lớn nhất ngày nhìn thấy tham lam ≥ lớn hơn hẳn: {"đúng 12/12" if not g1 else "sai ở " + ", ".join(g1)}; '
  f'(b) nhiễu ≤ 5% và chấm ≤ 3 hợp đồng ≤ 2%: {"đúng 12/12" if not g2 else "sai ở " + ", ".join(g2)}; '
  f'(c) chấm/nến không cao hơn quá 15%: {"đúng 12/12 (tăng " + f(min(inc), 1) + "% – " + f(max(inc), 1) + "%)" if not g3 else "sai ở " + ", ".join(g3)}.')
t = {c: int(S[SIX & (S.cau_hinh == c)].so_truot.sum()) for c in CFG_ORDER}
w(f'2. **Không lân cận thay có lân cận** (chỉ khi tổng trượt hai đoạn ít hơn): không lân cận {t["khong_lan_can"]}, có lân cận (nền mới) {t["nen_moi"]} → '
  f'{"luật cho thay" if t["khong_lan_can"] < t["nen_moi"] else "giữ có lân cận"}.')
s8 = g.loc[('toi_thieu_1_ngay', 8), 'trung'] - g.loc[('nen_moi', 8), 'trung']
c3 = t['toi_thieu_1_ngay'] <= t['nen_moi'] and s8 >= 0.01
w(f'3. **Tối thiểu 1 ngày thay 2 ngày** (tổng trượt không nhiều hơn VÀ trùng nạp 8 ngày cao hơn ≥ 0,01): tổng trượt {t["toi_thieu_1_ngay"]} so với {t["nen_moi"]} '
  f'({"không nhiều hơn" if t["toi_thieu_1_ngay"] <= t["nen_moi"] else "NHIỀU HƠN"}); trùng nạp 8 ngày {f(g.loc[("toi_thieu_1_ngay", 8), "trung"])} so với '
  f'{f(g.loc[("nen_moi", 8), "trung"])} (chênh {f(s8)}) → {"luật cho thay" if c3 else "giữ tối thiểu 2 ngày"}.')
w(f'4. **Mức mặc định giữ 2%** (luật cố định). Để tham khảo: tổng trượt p 1% = {t["p1"]}, p 0,5% = {t["p0.5"]}, p 2% (nền mới) = {t["nen_moi"]}.')
w('')

# ---------------- 10. bất thường
w('## 10. Bất thường và chỗ chỉ dẫn chưa rõ')
w('')
A = []
x = S[(S.cau_hinh == 'nen_moi')]
same = bool(np.allclose(x.top20_cu, x.top20_nt) and np.allclose(x.top5_cu, x.top5_nt) and np.allclose(x.cuc_tri_cu.fillna(-1), x.cuc_tri_nt.fillna(-1)))
A.append(f'- Với chọn tham lam, số "nhìn thấy" {"bằng đúng" if same else "KHÔNG bằng"} số cũ ở mọi ô (đúng như dự kiến: theo cách dựng, mọi ô vượt ngưỡng đều là chấm hoặc cách một chấm ≤ w tick). '
         'Phần còn sót của nền mới vì vậy là sót **vì ngưỡng** (ô không vượt ngưỡng), không phải vì bước chọn.')
nm = S[SIX & (S.cau_hinh == 'nen_moi') & (S.so_truot > 0)]
for r in nm.itertuples():
    A.append(f'- Nền mới còn trượt một tiêu chí: {r.ma} M{r.khung} {DOAN_VN[r.doan]}: {vn_fail(r.truot_gi)} — gần hết ô sót nằm ở nến 13:00 và 13:15 UTC (mục 5), cùng cơ chế vòng 2 nêu.')
x = S[(S.cau_hinh == 'nen_moi') & (S.khung.isin([30, 60]))]
for r in x[x.so_truot > 0].itertuples():
    A.append(f'- Ngoài 6 ô: nền mới {r.ma} M{r.khung} {DOAN_VN[r.doan]} trượt {vn_fail(r.truot_gi)} (M30 / H1 không vào luật chọn, chỉ báo).')
A.append('- NQ M1 đoạn chọn nhiễu 1,2% và NQ M5 / M15 đoạn chọn 1,3–1,5%, cao hơn đoạn kiểm (0,3–0,4%) — vẫn dưới 5%. Đoạn chọn NQ có tuần chuyển hợp đồng (14/09).')
A.append('- Đối chứng luật đang chạy không có "Khớp" (không phải luật phân vị) nên ba tiêu chí Khớp ghi "không áp dụng"; chúng trượt cả ba tiêu chí không sót ở mọi ô, giống vòng 2.')
A.append('- Golden (`perf/Golden/Program.cs`) **chưa có tuỳ chọn `--from`**. Để C# chạy được dòng "nạp 8 ngày", `sa3_numbers.py` ghi sẵn cặp file đã cắt '
         '`tf/fp_GC_m5_nap8.csv`, `tf/fp_NQ_m15_nap8.csv` (+ `_bars.csv`) trong thư mục tạm; bản chuẩn đọc file cắt ra đúng bằng khi đọc file đủ với `--from` (có assert). '
         'Điểm bắt đầu là nến đầu của ngày giao dịch thứ 8 tính từ cuối theo giờ Chicago (GC M5: 2026-10-28 22:00 UTC; NQ M15: 2026-11-12 23:00 UTC), không phải 00:00.')
A.append('- Chỉ dẫn ghi tên script tiền tố `r3_` ở dòng "Yêu cầu" nhưng mục 6 của review và phần chỉ dẫn vòng 3 ghi `sa3_`; Opus dùng `sa3_` (khớp `out_r3_*`, `R3-KET-QUA.md`).')
A.append('- "Nến rỗng bỏ hẳn" không làm đổi số nào trên dữ liệu hiện có: CSV của Golden không có nến nào mà mọi ô volume = 0 (tự kiểm in "rỗng 0"). Điều này chỉ có tác dụng với dữ liệu sống.')
A.append('- Phép thử nạp 3 ngày trùng thấp (0,69 gộp): với 3 ngày, ngày đầu chạy hoàn toàn bằng dự phòng 120 phút và ngày thứ hai mới có 1 ngày trước (chưa đủ tối thiểu 2), '
         'nên chỉ ngày thứ ba dùng ngưỡng chính. Đây là hành vi đã định, không phải lỗi.')
c0 = CO[(CO.ma == 'GC') & (CO.cau_hinh == 'nen_moi')].iloc[0]
A.append(f'- So CORVEN (GC M1, {c0.so_nen_mau} nến mẫu): nền mới chỉ {f(c0.cham_minh_nen, 2)} chấm/nến so với CORVEN {f(c0.cham_CORVEN_nen, 2)}; bắt {pct(c0.recall)} chấm CORVEN, '
         f'nhưng {pct(c0.precision)} chấm của mình trùng CORVEN. Nghĩa là luật thống kê thưa hơn CORVEN nhiều ở M1; chỉ báo số, không chỉnh theo (đúng chỉ dẫn).')
L.extend(A)
w('')

txt = '\n'.join(L) + '\n'
open('R3-KET-QUA.md', 'w', encoding='utf-8').write(txt)
open('r3_results.md', 'w', encoding='utf-8').write(txt)
print('đã ghi R3-KET-QUA.md và r3_results.md', len(L), 'dòng')
