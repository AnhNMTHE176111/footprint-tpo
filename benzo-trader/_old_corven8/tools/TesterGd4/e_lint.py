# -*- coding: utf-8 -*-
"""
GĐ4 (e) — lint thuật ngữ trong MỌI chuỗi người học nhìn thấy: nhãn chart, bảng, caption Telegram, Settings, Description,
nhãn cổng CSV ứng viên, mô tả dấu hiệu, README.md của benzo-trader.
Luật (CLAUDE.md + plan 4e/10.3): buy/sell/limit/market giữ tiếng Anh — cấm "mua/bán", "lệnh chờ/lệnh giới hạn",
"lệnh thị trường", "đập giá", "giá chào"; cấm "volatility", "aggressive/passive"; từ Anh lạ phải có nghĩa tiếng Việt.
Chạy: PYTHONIOENCODING=utf-8 python benzo-trader/tools/TesterGd4/e_lint.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BT = os.path.normpath(os.path.join(HERE, '..', '..'))
CS = ['BenzoTrader.cs', 'BenzoCore.cs', 'BenzoCorven.cs', 'BenzoOrderFlow.cs', 'BenzoZones.cs']
BANNED = [
    (r'(?<![\wÀ-ỹ])mua(?![\wÀ-ỹ])', 'mua (phải viết buy)'),
    (r'(?<![\wÀ-ỹ])bán(?![\wÀ-ỹ])', 'bán (phải viết sell)'),
    (r'lệnh chờ|lệnh giới hạn', 'lệnh chờ/giới hạn (phải viết limit)'),
    (r'lệnh thị trường|đập giá', 'lệnh thị trường/đập giá (phải viết market)'),
    (r'giá chào', 'giá chào (phải viết sell limit/buy limit)'),
    (r'(?i)volatility', 'volatility'),
    (r'(?i)\baggressive\b|\bpassive\b', 'aggressive/passive (giữ "chủ động/thụ động")'),
]
# từ Anh xuất hiện trong chuỗi hiển thị — liệt kê để người duyệt quyết (đã dạy / cần giải thích)
EN_WORDS = re.compile(r'(?<![\w])([A-Za-z][a-z]{2,}(?:\s[a-z]{3,})?)(?![\w])')
KNOWN_OK = {'buy', 'sell', 'limit', 'market', 'stacked', 'trap', 'range', 'Backtest', 'Telegram', 'token', 'chat', 'id',
            'corven', 'CORVEN', 'Benzo', 'BENZO', 'Trader', 'Volume', 'Analysis', 'Optimus', 'Flow', 'chart', 'TEST', 'fail break',
            'fail', 'break', 'medΔ', 'Ask', 'Bid', 'GCZ26', 'canh'}

lit = re.compile(r'\$?@?"((?:[^"\\]|\\.)*)"')


def strings_cs(path):
    out = []
    for no, line in enumerate(open(path, encoding='utf-8'), 1):
        code = line.split('//')[0] if '"' not in line.split('//')[0] and '//' in line else line
        s = line.strip()
        if s.startswith('//') or s.startswith('///') or s.startswith('[DllImport'):
            continue
        for m in lit.finditer(line):
            t = m.group(1)
            if re.search(r'[À-ỹΔ⚠✓✗·→—]|[a-zà-ỹ]{3,} [a-zà-ỹ]{2,}', t):   # chỉ chuỗi người đọc (có chữ/ký hiệu hiển thị)
                out.append((no, t))
    return out


def main():
    bad, en = [], {}
    for f in CS:
        p = os.path.join(BT, f)
        for no, t in strings_cs(p):
            if 'api.telegram.org' in t or t.startswith('cache_') or t.endswith('.jsonl') or 'user32' in t:
                continue
            for rx, why in BANNED:
                if re.search(rx, t):
                    bad.append(f'{f}:{no}: [{why}] "{t[:120]}"')
            for w in EN_WORDS.findall(t):
                if w not in KNOWN_OK and w.split()[0] not in KNOWN_OK:
                    en.setdefault(w, set()).add(f'{f}:{no}')
    # README: chỉ phần chữ thường (không khối code)
    p = os.path.join(BT, 'README.md')
    incode = False
    for no, line in enumerate(open(p, encoding='utf-8'), 1):
        if line.strip().startswith('```'):
            incode = not incode
            continue
        if incode:
            continue
        txt = re.sub(r'`[^`]*`', '', line)
        for rx, why in BANNED:
            if re.search(rx, txt):
                bad.append(f'README.md:{no}: [{why}] "{line.strip()[:140]}"')
    print('== Vi phạm từ cấm:', len(bad))
    for b in bad:
        print('  ' + b)
    print('== Từ tiếng Anh trong chuỗi hiển thị C# (ngoài danh sách đã dạy) — để người duyệt xét:')
    for w, locs in sorted(en.items()):
        print(f'  {w}: {", ".join(sorted(locs))[:150]}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
