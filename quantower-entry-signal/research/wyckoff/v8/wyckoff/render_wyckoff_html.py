#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_wyckoff_html.py — ve nen M1 THAT cua thang 7/2026 (GCQ26, dxFeed) ra 1 file HTML
DUY NHAT (khong CDN, mo bang trinh duyet la chay), roi ap DUNG thuat toan Wyckoff cua
indicator len do (wyckoff_schematic.detect — ban Python song song voi ScanWyckoff() trong
WyckoffRunner.cs) va ve schematic giong het cach DrawWyckoff() ve tren Quantower.

Muc dich: nguoi hoc scroll/zoom xem lai TUNG range trong qua khu de tu cham diem thuat toan.

Nguon du lieu: data-export/27-7/_GCQ26XCEC dxFeed ... 11_3_2025 -> 7_27_2026 (entry_dxfeed.load_m1)
  -> dxFeed CHI xuat toi 2026-07-27 15:56 UTC. Khong noi them file footprint export vi do la
     HOP DONG KHAC (gia lech ~59 diem: 4080 vs 4138) — noi vao se tao gap gia.

Parity voi C#: sau load_m1() phai TINH LAI b['trend'] voi tol = TrendTolPts = 1.0 (entry_dxfeed
dung tol = 0). Moi tham so Wyckoff khac lay nguyen tu wyckoff_schematic.py.

Chay: python3 render_wyckoff_html.py
"""
import os
import sys
import json
import calendar
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
V8 = os.path.dirname(HERE)
WYCK = os.path.dirname(V8)
RESEARCH = os.path.dirname(WYCK)
REPO = os.path.dirname(os.path.dirname(RESEARCH))
sys.path.insert(0, RESEARCH)
sys.path.insert(0, HERE)

import entry_dxfeed as E          # noqa: E402
import wyckoff_schematic as W     # noqa: E402

TREND_TOL_PTS = 1.0               # khop WyckoffRunner.cs TrendTolPts
TREND_LB = E.BASE['TREND_LB']     # 480
MONTH_FROM = datetime(2026, 7, 1)
MONTH_TO = datetime(2026, 8, 1)
OUT = os.path.join(REPO, 'rule-entry', 'wyckoff-chart-thang7.html')


def fix_trend(B):
    """entry_dxfeed dung tol=0; WyckoffRunner.cs dung TrendTolPts=1.0 -> tinh lai cho khop."""
    for i, b in enumerate(B):
        j = i - TREND_LB
        if j < 0:
            b['trend'] = 0
            continue
        d = b['c'] - B[j]['c']
        b['trend'] = 1 if d > TREND_TOL_PTS else (-1 if d < -TREND_TOL_PTS else 0)


def main():
    print('Nap M1 dxFeed ...')
    B = E.load_m1()
    fix_trend(B)
    print(f'  {len(B)} nen  {B[0]["dt"]} -> {B[-1]["dt"]}')

    print('Chay ScanWyckoff (ban Python) tren TOAN BO lich su ...')
    ranges = W.detect(B)
    drops = [(r, why, di) for (r, why, di) in W.DISCARDED]
    print(f'  tong {len(ranges)} range GIU LAI + {len(drops)} ung vien BI BO tren toan bo lich su')

    def in_july(si, ei):
        return B[ei]['dt'] >= MONTH_FROM and B[si]['dt'] < MONTH_TO

    keep = [r for r in ranges
            if in_july(r.start_i, r.end_i if r.end_i is not None else len(B) - 1)]
    dkeep = [(r, why, di) for (r, why, di) in drops if in_july(r.start_i, di)]
    print(f'  thang 7/2026: {len(keep)} range duoc ve, {len(dkeep)} ung vien bi bo')

    # cua so nen de ve: tu min(dau range som nhat, 1/7) lui 60 nen, toi het du lieu thang 7
    i_july = next(i for i, b in enumerate(B) if b['dt'] >= MONTH_FROM)
    i_from = min([i_july] + [r.start_i for r in keep] + [r.start_i for r, _, _ in dkeep])
    i_from = max(0, i_from - 60)
    i_to = len(B) - 1
    while i_to > 0 and B[i_to]['dt'] >= MONTH_TO:
        i_to -= 1
    print(f'  ve nen {i_from}..{i_to}  ({i_to - i_from + 1} nen)  '
          f'{B[i_from]["dt"]} -> {B[i_to]["dt"]}')

    # ---------------- dong goi du lieu (int tick de file nho) ----------------
    tick = E.TICK
    base = round(min(B[i]['lo'] for i in range(i_from, i_to + 1)) / tick)
    # dxFeed ghi gio UTC nhung datetime la NAIVE -> .timestamp() se hieu la gio may (UTC+7) va lech
    # 7 tieng. Dung calendar.timegm de ep hieu dung UTC.
    def epmin(dt):
        return calendar.timegm(dt.timetuple()) // 60

    t0 = epmin(B[i_from]['dt'])

    def q(p):
        return int(round(p / tick)) - base

    o, h, l, c, v, t = [], [], [], [], [], []
    for i in range(i_from, i_to + 1):
        b = B[i]
        o.append(q(b['o'])); h.append(q(b['hi'])); l.append(q(b['lo'])); c.append(q(b['c']))
        v.append(int(b['v']))
        t.append(epmin(b['dt']) - t0)

    def rel(i):
        return i - i_from

    def pack(r, end_i, why=None):
        e = min(end_i, i_to)
        phases = [{'p': ph[0], 's': rel(max(ph[1], i_from)),
                   'e': rel(min(ph[2] if ph[2] is not None else e, i_to))}
                  for ph in r.phases if ph[1] <= i_to]
        evs = [{'i': rel(ev['i']), 'p': q(ev['price']), 'l': ev['label'],
                'st': ev['status'] or ''} for ev in r.events if i_from <= ev['i'] <= i_to]
        d = {
            'k': r.kind, 'kvn': r.kind_vn,
            's': rel(r.start_i), 'e': rel(e),
            'lo': q(r.low) if r.low is not None else q(B[r.start_i]['lo']),
            'hi': q(r.high) if r.high is not None else q(B[r.start_i]['hi']),
            'done': r.status == 'completed',
            'ph': phases, 'ev': evs,
            # v3/v4: biên CHÍNH (nét liền) = mức climax + mức AR, cố định sau Phase A;
            # 'lo'/'hi' là biên PHỤ (nét đứt), chỉ vẽ khi thật sự rộng hơn biên chính.
            'slo': q(r.solid_low) if r.solid_low is not None else None,
            'shi': q(r.solid_high) if r.solid_high is not None else None,
        }
        if why:
            d['why'] = why
        return d

    rs = [pack(r, r.end_i if r.end_i is not None else i_to) for r in keep]
    ds = [pack(r, di, why) for (r, why, di) in dkeep]
    rs.sort(key=lambda x: -x['s'])
    ds.sort(key=lambda x: -x['s'])

    payload = {
        'tick': tick, 'base': base, 't0': t0,
        'o': o, 'h': h, 'l': l, 'c': c, 'v': v, 't': t,
        'ranges': rs, 'drops': ds,
        'src': os.path.basename(E.DXFILE),
        'first': B[i_from]['dt'].strftime('%Y-%m-%d %H:%M'),
        'last': B[i_to]['dt'].strftime('%Y-%m-%d %H:%M'),
    }
    js = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)

    html = HTML_TMPL.replace('/*__DATA__*/', js)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'==> {OUT}  ({os.path.getsize(OUT) / 1024 / 1024:.2f} MB)')

    # thong ke in ra terminal de doi chieu nhanh
    def dump(title, arr, show_why):
        print(f'\n{title}:')
        for x in arr:
            ph = ''.join(p['p'] for p in x['ph'])
            print(f"  {x['k']:<4} {B[i_from + x['s']]['dt']} -> {B[i_from + x['e']]['dt']} "
                  f"({x['e'] - x['s']:>5} nen)  "
                  f"{(x['lo'] + base) * tick:.1f}-{(x['hi'] + base) * tick:.1f}  "
                  f"Phase {ph:<10} {len(x['ev']):>2} moc  "
                  + (x.get('why', '') if show_why else ('xong' if x['done'] else 'DANG CHAY')))

    dump('RANGE DUOC VE trong thang 7', rs, False)
    dump('UNG VIEN BI BO trong thang 7', ds, True)


HTML_TMPL = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Wyckoff tháng 7/2026 — GCQ26 M1</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:#14161c;color:#dfe4ee;
  font:13px/1.45 "Segoe UI",Roboto,system-ui,sans-serif;overflow:hidden}
#wrap{display:flex;height:100%}
#side{width:390px;min-width:390px;border-right:1px solid #2b3040;display:flex;flex-direction:column;background:#171a22}
#head{padding:10px 12px;border-bottom:1px solid #2b3040}
#head h1{margin:0 0 4px;font-size:15px;font-weight:600}
#head .sub{font-size:11.5px;color:#8b93a7;line-height:1.6}
#head code{font:11px/1.6 monospace;color:#a8b6d8}
#btnAll{background:#242a38;color:#cfd6e6;border:1px solid #333b4d;border-radius:4px;
  padding:2px 9px;font-size:11.5px;cursor:pointer;font-family:inherit}
#btnAll:hover{background:#2e3546}
#tools{padding:8px 12px;border-bottom:1px solid #2b3040;display:flex;flex-wrap:wrap;gap:10px;font-size:12px}
#tools label{display:flex;align-items:center;gap:5px;cursor:pointer;user-select:none}
#tabs{display:flex;border-bottom:1px solid #2b3040}
.tab{flex:1;background:none;border:none;border-bottom:2px solid transparent;color:#8b93a7;
  padding:8px 4px;font-size:12px;cursor:pointer;font-family:inherit}
.tab:hover{background:#1e2230;color:#cfd6e6}
.tab.on{color:#dfe4ee;border-bottom-color:#7aa2f7;background:#1c2130}
#listhead{padding:7px 12px;font-size:11.5px;color:#8b93a7;border-bottom:1px solid #2b3040;
  display:flex;justify-content:space-between}
.why{color:#e8a35a;font-size:11px;margin-top:2px}
#list{flex:1;overflow-y:auto;overflow-x:hidden}
.row{padding:7px 12px;border-bottom:1px solid #232733;cursor:pointer}
.row:hover{background:#232838}
.row.sel{background:#2c3550;box-shadow:inset 3px 0 0 #7aa2f7}
.row .l1{font-weight:600;font-size:12.5px;display:flex;align-items:center;gap:6px}
.row .l2{color:#9aa3b8;font-size:11.5px;margin-top:2px}
.row .l3{color:#7d879c;font-size:11px;margin-top:2px;word-break:break-word}
.tag{font-size:10.5px;padding:1px 6px;border-radius:8px;font-weight:600}
.acc{background:#1e3a24;color:#7ddc8c}
.dist{background:#3d2020;color:#f08b8b}
.run{background:#3a3320;color:#e8c46a}
.grade{margin-top:5px;display:flex;gap:5px}
.grade button{background:#242a38;color:#9aa3b8;border:1px solid #333b4d;border-radius:4px;
  padding:1px 8px;font-size:11px;cursor:pointer}
.grade button:hover{background:#2e3546}
.grade button.on[data-g="ok"]{background:#1e5c2c;color:#fff;border-color:#2c8f42}
.grade button.on[data-g="bad"]{background:#7a2323;color:#fff;border-color:#b33}
.grade button.on[data-g="hm"]{background:#7a5f1e;color:#fff;border-color:#c99a2e}
#main{flex:1;position:relative;min-width:0}
canvas{display:block;width:100%;height:100%}
#hint{position:absolute;left:10px;top:8px;font-size:11.5px;color:#8b93a7;pointer-events:none;
  background:rgba(20,22,28,.75);padding:4px 8px;border-radius:4px}
#tip{position:absolute;pointer-events:none;background:rgba(16,18,24,.95);border:1px solid #39405a;
  border-radius:5px;padding:6px 9px;font-size:11.5px;display:none;white-space:pre;z-index:5}
#foot{padding:8px 12px;border-top:1px solid #2b3040;font-size:11.5px;color:#8b93a7}
#foot button{background:#242a38;color:#cfd6e6;border:1px solid #333b4d;border-radius:4px;
  padding:3px 9px;font-size:11.5px;cursor:pointer}
#dump{width:100%;height:90px;margin-top:6px;display:none;background:#0f1116;color:#cfd6e6;
  border:1px solid #333b4d;border-radius:4px;font:11px monospace}
</style>
</head>
<body>
<div id="wrap">
  <div id="side">
    <div id="head">
      <h1>Wyckoff — GCQ26 M1, tháng 7/2026</h1>
      <div class="sub" id="meta"></div>
    </div>
    <div id="tools">
      <label><input type="checkbox" id="cbEv" checked> Nhãn sự kiện</label>
      <label><input type="checkbox" id="cbPh" checked> Vạch Phase</label>
      <label><input type="checkbox" id="cbOnly"> Chỉ range đang chọn</label>
      <label><input type="checkbox" id="cbVol" checked> Khối lượng</label>
      <label><input type="checkbox" id="cbDrop"> Vẽ cả ứng viên bị bỏ (xám)</label>
      <label><input type="checkbox" id="cbNoST" checked> Ẩn nhãn UA/UT/DA (đỡ rối)</label>
      <button id="btnAll">Xem cả tháng</button>
    </div>
    <div id="tabs">
      <button class="tab on" data-t="keep"></button>
      <button class="tab" data-t="drop"></button>
    </div>
    <div id="listhead"><span id="lhTitle">DANH SÁCH RANGE</span><span id="cnt"></span></div>
    <div id="list"></div>
    <div id="foot">
      <button id="btnDump">Xuất ghi chú chấm điểm</button>
      <textarea id="dump" readonly></textarea>
    </div>
  </div>
  <div id="main">
    <canvas id="cv"></canvas>
    <div id="hint">Lăn chuột = phóng to/thu nhỏ · Kéo = trượt ngang · Bấm dòng bên trái = nhảy tới range đó</div>
    <div id="tip"></div>
  </div>
</div>
<script>
const D = /*__DATA__*/;
const TICK = D.tick, BASE = D.base, T0 = D.t0;
const N = D.o.length;
function px(q){ return (q + BASE) * TICK; }            // tick-int -> giá thật
function tm(i){ return new Date((T0 + D.t[i]) * 60000); }
const MON = ['01','02','03','04','05','06','07','08','09','10','11','12'];
function fmtT(d){
  const p = n => String(n).padStart(2,'0');
  return p(d.getUTCDate())+'/'+p(d.getUTCMonth()+1)+' '+p(d.getUTCHours())+':'+p(d.getUTCMinutes());
}
function fmtP(v){ return v.toFixed(1); }

// ---------------- màu: khớp DrawWyckoff() trong WyckoffRunner.cs ----------------
const C_ACC = '#4CAF50', C_DIST = '#E53935', C_PHASE = '#9696DC';
// v4: đủ 4 pattern. Tái tích lũy / tái phân phối dùng cùng gam nhưng nhạt hơn để phân biệt.
const C_KIND = {'ACC':'#4CAF50','RE-ACC':'#8BC34A','DIST':'#E53935','RE-DIST':'#FF7043',
                'ACC?':'#78909C','DIST?':'#78909C'};
function kcol(k){ return C_KIND[k] || '#78909C'; }
const CAT = {
  climax:'#FF5252', ar:'#81C784', st:'#B0BEC5', shake:'#FFCA28',
  break:'#42A5F5', lpsc:'#26C6A8', lpsd:'#BA68C8'
};
const CAT_VN = [['climax','SC / BCLX — cao trào'],['ar','AR / ST[A] — bật ngược, chốt Phase A'],
  ['st','UA / UT / DA — test nhẹ, chỉ nới biên phụ'],['shake','Spring / Shakeout / UTAD — cú rũ (Phase C)'],
  ['break','SOS / SOW — phá vỡ'],['lpsc','LPS[C] / LPSY[C] — test cuối trước phá vỡ'],
  ['lpsd','LPS[D] / LPSY[D] — hồi retest sau phá vỡ']];
function catOf(lbl){
  let b = lbl.endsWith(')') ? lbl.slice(0, lbl.indexOf('(')).trim() : lbl;
  if (b==='SC'||b==='BCLX') return 'climax';
  if (b==='AR' || b==='ST[A]') return 'ar';   // ST[A] thuộc Phase A, đọc chung màu với AR
  if (b==='ST'||b==='UA'||b==='DA'||b==='UT') return 'st';
  if (b==='Spring'||b==='Shakeout'||b==='UTAD') return 'shake';
  if (b==='SOS'||b==='SOW') return 'break';
  if (b==='LPS[C]'||b==='LPSY[C]') return 'lpsc';
  if (b==='LPS[D]'||b==='LPSY[D]') return 'lpsd';
  return 'st';
}

// ---------------- state ----------------
const cv = document.getElementById('cv'), ctx = cv.getContext('2d');
let W=0, H=0, DPR=1;
const PADR = 62, PADB = 26, PADT = 10, PADL = 8;
let bw = 6;              // px mỗi nến
let i0 = Math.max(0, N - 400);   // nến trái cùng
let tab = 'keep';        // 'keep' = range được vẽ | 'drop' = ứng viên bị bỏ
let sel = -1;            // chỉ số trong danh sách của tab đang mở
const grades = JSON.parse(localStorage.getItem('wyGrades7') || '{}');
function curList(){ return tab === 'keep' ? D.ranges : D.drops; }

function plot(){ return {x:PADL, y:PADT, w:W-PADL-PADR, h:H-PADT-PADB}; }
function visCount(){ return Math.max(2, Math.floor(plot().w / bw)); }
function clampI0(){ i0 = Math.max(-visCount()*0.15, Math.min(N - visCount()*0.85, i0)); }

function resize(){
  DPR = window.devicePixelRatio || 1;
  const r = cv.parentElement.getBoundingClientRect();
  W = r.width; H = r.height;
  cv.width = Math.round(W*DPR); cv.height = Math.round(H*DPR);
  ctx.setTransform(DPR,0,0,DPR,0,0);
  draw();
}
window.addEventListener('resize', resize);

// ---------------- vẽ ----------------
function draw(){
  const pl = plot();
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle = '#14161c'; ctx.fillRect(0,0,W,H);
  clampI0();
  const a = Math.max(0, Math.floor(i0)), b = Math.min(N-1, Math.ceil(i0 + visCount()));
  if (b <= a) return;

  // thang giá: cực trị nến hiện trong khung + biên các range hiện trong khung
  let lo = 1e18, hi = -1e18;
  for (let i=a;i<=b;i++){ if (D.l[i]<lo) lo=D.l[i]; if (D.h[i]>hi) hi=D.h[i]; }
  for (const r of D.ranges.concat(document.getElementById('cbDrop').checked ? D.drops : [])){
    if (r.e < a || r.s > b) continue;
    if (r.lo < lo) lo = r.lo; if (r.hi > hi) hi = r.hi;
  }
  const pad = Math.max(1,(hi-lo)*0.08); lo -= pad; hi += pad;
  const volH = document.getElementById('cbVol').checked ? Math.min(70, pl.h*0.16) : 0;
  const ph = pl.h - volH;
  const X = i => pl.x + (i - i0 + 0.5) * bw;
  const Y = q => pl.y + ph - (q - lo) / (hi - lo) * ph;

  // lưới ngang + trục giá phải
  ctx.font = '11px "Segoe UI",sans-serif'; ctx.textBaseline='middle';
  const stepQ = niceStep((hi-lo)*TICK/6)/TICK;
  ctx.strokeStyle='#20242f'; ctx.lineWidth=1;
  for (let q=Math.ceil(lo/stepQ)*stepQ; q<=hi; q+=stepQ){
    const y = Y(q);
    ctx.beginPath(); ctx.moveTo(pl.x, y+.5); ctx.lineTo(pl.x+pl.w, y+.5); ctx.stroke();
    ctx.fillStyle='#7d879c'; ctx.textAlign='left';
    ctx.fillText(fmtP(px(q)), pl.x+pl.w+6, y);
  }
  // lưới dọc theo ngày
  ctx.textAlign='center'; ctx.textBaseline='top';
  let lastDay = -1, lastLx = -1e9;
  for (let i=a;i<=b;i++){
    const d = tm(i);
    if (d.getUTCDate() !== lastDay){
      lastDay = d.getUTCDate();
      const x = X(i);
      if (x - lastLx < 36) continue;      // hai ngày quá sát nhau -> bỏ nhãn, tránh chữ chồng
      lastLx = x;
      if (x>pl.x && x<pl.x+pl.w){
        ctx.strokeStyle='#262b38'; ctx.beginPath();
        ctx.moveTo(x+.5,pl.y); ctx.lineTo(x+.5,pl.y+pl.h); ctx.stroke();
        ctx.fillStyle='#8b93a7';
        // ghim nhãn trong khung để không bị cắt mất chữ số ở mép trái/phải
        const lx = Math.max(pl.x+18, Math.min(pl.x+pl.w-18, x));
        ctx.fillText(String(d.getUTCDate()).padStart(2,'0')+'/'+MON[d.getUTCMonth()], lx, pl.y+pl.h+5);
      }
    }
  }

  // khối lượng
  if (volH > 3){
    let vmax = 1;
    for (let i=a;i<=b;i++) if (D.v[i]>vmax) vmax = D.v[i];
    const vy = pl.y + pl.h;
    for (let i=a;i<=b;i++){
      const x = X(i), w = Math.max(1, bw*0.72);
      const hh = D.v[i]/vmax*(volH-4);
      ctx.fillStyle = D.c[i]>=D.o[i] ? 'rgba(38,166,154,.45)' : 'rgba(239,83,80,.45)';
      ctx.fillRect(x-w/2, vy-hh, w, hh);
    }
  }

  // nến
  const thin = bw < 2.2;
  if (thin){
    // gộp theo cột pixel khi quá nhỏ
    let col = -1, cl=1e18, ch=-1e18, co=0, cc=0;
    const flush = () => {
      if (col < 0) return;
      ctx.strokeStyle = cc>=co ? '#26A69A' : '#EF5350';
      ctx.beginPath(); ctx.moveTo(col+.5, Y(ch)); ctx.lineTo(col+.5, Y(cl)); ctx.stroke();
    };
    for (let i=a;i<=b;i++){
      const x = Math.round(X(i));
      if (x !== col){ flush(); col=x; cl=D.l[i]; ch=D.h[i]; co=D.o[i]; }
      if (D.l[i]<cl) cl=D.l[i]; if (D.h[i]>ch) ch=D.h[i];
      cc = D.c[i];
    }
    flush();
  } else {
    for (let i=a;i<=b;i++){
      const x = X(i), up = D.c[i] >= D.o[i];
      const col = up ? '#26A69A' : '#EF5350';
      ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(Math.round(x)+.5, Y(D.h[i])); ctx.lineTo(Math.round(x)+.5, Y(D.l[i])); ctx.stroke();
      const y1 = Y(Math.max(D.o[i],D.c[i])), y2 = Y(Math.min(D.o[i],D.c[i]));
      ctx.fillRect(x - bw*0.36, y1, Math.max(1, bw*0.72), Math.max(1, y2-y1));
    }
  }

  drawWyckoff(pl, ph, X, Y, a, b);
  drawLegend(pl);
}

function niceStep(v){
  const p = Math.pow(10, Math.floor(Math.log10(v)));
  const n = v/p;
  return (n<1.5?1:n<3?2:n<7?5:10)*p;
}

// tránh nhãn đè nhau — cùng cách WyLabelBox() bên C#
let boxes = [];
function labelBox(x, y, text, color){
  ctx.font = '11px "Segoe UI",sans-serif';
  const w = ctx.measureText(text).width + 8, h = 15;
  const pl0 = plot();
  let bx = Math.max(pl0.x + 1, Math.min(x, pl0.x + pl0.w - w - 1)), by = y, guard = 0;
  const hit = () => boxes.some(o => bx < o.x+o.w && bx+w > o.x && by < o.y+o.h && by+h > o.y);
  // dồn lên để tránh đè; chạm mép trên thì quay xuống dồn xuống (nếu không nhãn bay khỏi khung)
  while (guard < 40 && hit() && by - h - 2 >= PADT){ by -= h + 2; guard++; }
  while (guard < 80 && hit()){ by += h + 2; guard++; }
  boxes.push({x:bx,y:by,w,h});
  ctx.fillStyle = 'rgba(20,20,24,.92)';
  ctx.strokeStyle = color; ctx.lineWidth = 1;
  roundRect(bx, by, w, h, 4); ctx.fill(); ctx.stroke();
  ctx.fillStyle = color; ctx.textAlign='left'; ctx.textBaseline='top';
  ctx.fillText(text, bx+4, by+2);
}
function roundRect(x,y,w,h,r){
  ctx.beginPath();
  ctx.moveTo(x+r,y); ctx.arcTo(x+w,y,x+w,y+h,r); ctx.arcTo(x+w,y+h,x,y+h,r);
  ctx.arcTo(x,y+h,x,y,r); ctx.arcTo(x,y,x+w,y,r); ctx.closePath();
}

function drawWyckoff(pl, ph, X, Y, a, b){
  boxes = [];
  const showEv = document.getElementById('cbEv').checked;
  const showPh = document.getElementById('cbPh').checked;
  const only = document.getElementById('cbOnly').checked;
  const noST = document.getElementById('cbNoST').checked;
  ctx.save();
  ctx.beginPath(); ctx.rect(pl.x, pl.y, pl.w, ph); ctx.clip();
  // danh sách vẽ: range được giữ + (tuỳ chọn) ứng viên bị bỏ, vẽ mờ để phân biệt
  const items = D.ranges.map((r,k) => ({r, k, dim:false, list:'keep'}));
  if (document.getElementById('cbDrop').checked || tab === 'drop')
    for (let k=0;k<D.drops.length;k++) items.push({r:D.drops[k], k, dim:true, list:'drop'});
  for (const it of items){
    const r = it.r, k = it.k, dim = it.dim;
    const isSel = (it.list === tab) && (k === sel);
    if (only && !isSel) continue;
    if (r.e < a-2 || r.s > b+2) continue;
    if (dim && !isSel && !document.getElementById('cbDrop').checked) continue;
    const col = dim ? (isSel ? '#c8a34a' : '#6b6f7d') : kcol(r.k);
    const x0 = X(r.s), x1 = X(r.e);
    const xa = Math.max(x0, pl.x), xb = Math.min(x1, pl.x+pl.w);
    const yL = Y(r.lo), yH = Y(r.hi);
    if (isSel){ ctx.fillStyle = hexA(col, .07); ctx.fillRect(xa, yH, Math.max(1,xb-xa), yL-yH); }
    // BIÊN CHÍNH (nét liền, quan trọng nhất) = mức climax và mức AR.
    // BIÊN NỚI RỘNG (nét đứt) = biên làm việc khi ST[A]/Spring/UT đã đẩy ra ngoài mức climax.
    const sLo = (r.slo==null) ? r.lo : r.slo;
    const sHi = (r.shi==null) ? r.hi : r.shi;
    ctx.strokeStyle = col; ctx.lineWidth = isSel ? 3 : 2;
    ctx.beginPath();
    ctx.moveTo(xa, Y(sLo)); ctx.lineTo(xb, Y(sLo));
    ctx.moveTo(xa, Y(sHi)); ctx.lineTo(xb, Y(sHi));
    ctx.stroke();
    ctx.lineWidth = isSel ? 2 : 1.4; ctx.setLineDash([6,4]);
    ctx.beginPath();
    if (r.lo < sLo - 0.5){ ctx.moveTo(xa, yL); ctx.lineTo(xb, yL); }
    if (r.hi > sHi + 0.5){ ctx.moveTo(xa, yH); ctx.lineTo(xb, yH); }
    ctx.stroke();
    // mép trái/phải mờ để thấy range bắt đầu/kết thúc ở đâu
    ctx.lineWidth = 1; ctx.setLineDash([3,3]); ctx.strokeStyle = hexA(col,.55);
    ctx.beginPath(); ctx.moveTo(x0, yH); ctx.lineTo(x0, yL);
    ctx.moveTo(x1, yH); ctx.lineTo(x1, yL); ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = '11px "Segoe UI",sans-serif'; ctx.fillStyle = col;
    ctx.textAlign='left'; ctx.textBaseline='bottom';
    ctx.fillText(r.kvn + (dim?' — BỊ BỎ':''),
                 Math.min(xb+5, pl.x+pl.w-110), yH-2);

    if (showPh && (!dim || isSel)){
      ctx.strokeStyle = C_PHASE; ctx.lineWidth = 1.5; ctx.setLineDash([5,4]);
      for (const p of r.ph){
        const xp = X(p.s);
        if (xp < pl.x || xp > pl.x+pl.w) continue;
        ctx.beginPath(); ctx.moveTo(xp, yH); ctx.lineTo(xp, yL); ctx.stroke();
        labelBox(xp+3, yH-24, 'Phase '+p.p, C_PHASE);
      }
      ctx.setLineDash([]);
    }

    for (const ev of r.ev){
      const xe = X(ev.i);
      if (xe < pl.x-30 || xe > pl.x+pl.w+30) continue;
      const ye = Y(ev.p);
      const cat = catOf(ev.l);
      const cc = (dim && !isSel) ? '#6b6f7d' : (ev.st === 'failed' ? '#8c8c8c' : CAT[cat]);
      ctx.beginPath(); ctx.arc(xe, ye, 3.5, 0, 6.2832);
      ctx.fillStyle = cc; ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = ev.st==='confirmed' ? 2 : 1;
      ctx.setLineDash(ev.st==='pending' ? [2,2] : []);
      ctx.stroke(); ctx.setLineDash([]);
      if (showEv && (!dim || isSel) && !(noST && cat==='st')){
        const above = cat==='ar'||cat==='st'||cat==='break';
        labelBox(xe-9, above ? ye-24 : ye+8, ev.l, cc);
      }
    }
  }
  ctx.restore();
}
function hexA(hex, a){
  const n = parseInt(hex.slice(1),16);
  return `rgba(${n>>16&255},${n>>8&255},${n&255},${a})`;
}

function drawLegend(pl){
  const w = 272, x = pl.x + pl.w - w - 6, y = pl.y + 6;
  const h = CAT_VN.length*16 + 10;
  ctx.fillStyle = 'rgba(16,18,24,.88)'; ctx.strokeStyle = '#2f3648'; ctx.lineWidth = 1;
  roundRect(x, y, w, h, 5); ctx.fill(); ctx.stroke();
  ctx.font = '11px "Segoe UI",sans-serif'; ctx.textAlign='left'; ctx.textBaseline='top';
  let ly = y + 5;
  for (const [k, d] of CAT_VN){
    ctx.fillStyle = CAT[k];
    ctx.beginPath(); ctx.arc(x+11, ly+6, 4, 0, 6.2832); ctx.fill();
    ctx.fillStyle = '#c3cadb'; ctx.fillText(d, x+22, ly);
    ly += 16;
  }
}

// ---------------- tương tác chart ----------------
let drag = null;
cv.addEventListener('mousedown', e => { drag = {x:e.clientX, i0}; });
window.addEventListener('mouseup', () => drag = null);
cv.addEventListener('mousemove', e => {
  if (drag){ i0 = drag.i0 - (e.clientX - drag.x)/bw; draw(); return; }
  showTip(e);
});
cv.addEventListener('mouseleave', () => document.getElementById('tip').style.display='none');
cv.addEventListener('wheel', e => {
  e.preventDefault();
  const pl = plot();
  const at = i0 + (e.clientX - cv.getBoundingClientRect().left - pl.x)/bw;
  const f = e.deltaY < 0 ? 1.18 : 1/1.18;
  bw = Math.max(0.06, Math.min(40, bw*f));
  i0 = at - (e.clientX - cv.getBoundingClientRect().left - pl.x)/bw;
  draw();
}, {passive:false});

function showTip(e){
  const pl = plot(), tip = document.getElementById('tip');
  const rect = cv.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  const i = Math.round(i0 + (mx - pl.x)/bw - 0.5);
  if (i < 0 || i >= N || mx < pl.x || mx > pl.x+pl.w){ tip.style.display='none'; return; }
  const d = tm(i), vn = new Date(d.getTime() + 7*3600000);
  let s = fmtT(d)+' UTC  (VN '+fmtT(vn)+')\n'
        + 'O '+fmtP(px(D.o[i]))+'   H '+fmtP(px(D.h[i]))+'\n'
        + 'L '+fmtP(px(D.l[i]))+'   C '+fmtP(px(D.c[i]))+'\n'
        + 'Vol '+D.v[i];
  for (const r of D.ranges) for (const ev of r.ev) if (ev.i === i) s += '\n▸ '+ev.l+(ev.st?' ('+ev.st+')':'');
  tip.textContent = s;
  tip.style.display = 'block';
  tip.style.left = Math.min(mx+14, W-160)+'px';
  tip.style.top  = Math.min(my+14, H-90)+'px';
}

// ---------------- danh sách range ----------------
function gotoRange(k){
  const r = curList()[k];
  sel = k;
  const span = Math.max(20, r.e - r.s);
  bw = Math.max(0.06, Math.min(40, plot().w / (span*1.4)));
  i0 = (r.s + r.e)/2 - visCount()/2;
  renderList(); draw();
}
function renderList(){
  const el = document.getElementById('list');
  const L = curList();
  el.innerHTML = '';
  if (!L.length){
    el.innerHTML = '<div style="padding:16px 12px;color:#7d879c">Không có mục nào.</div>';
  }
  L.forEach((r, k) => {
    const div = document.createElement('div');
    div.className = 'row' + (k===sel ? ' sel' : '');
    const t1 = fmtT(tm(r.s)), t2 = fmtT(tm(r.e));
    const phs = r.ph.map(p=>p.p).join('→') || '—';
    const evs = r.ev.map(e=>e.l+(e.st==='failed'?'✗':e.st==='confirmed'?'✓':'')).join(' · ') || '—';
    const key = tab + k, g = grades[key] || '';
    const slo = r.slo==null ? r.lo : r.slo, shi = r.shi==null ? r.hi : r.shi;
    const kcls = r.k.indexOf('ACC')>=0 ? 'acc' : r.k.indexOf('DIST')>=0 ? 'dist' : 'run';
    div.innerHTML =
      `<div class="l1"><span class="tag ${kcls}">${r.kvn.toUpperCase()}</span>`
      + `<span>${t1} → ${t2}</span><span style="color:#7d879c;font-weight:400">${r.e-r.s} nến</span>`
      + (r.why || r.done ? '' : '<span class="tag run">đang chạy</span>') + `</div>`
      + `<div class="l2">biên chính ${fmtP(px(slo))} – ${fmtP(px(shi))} `
      + `(${((shi-slo)*TICK).toFixed(1)} giá)`
      + ((r.lo<slo-0.5||r.hi>shi+0.5) ? ` · phụ ${fmtP(px(r.lo))} – ${fmtP(px(r.hi))}` : '')
      + ` · Phase ${phs} · ${r.ev.length} mốc</div>`
      + (r.why ? `<div class="why">↳ bỏ vì: ${r.why}</div>` : '')
      + `<div class="l3">${evs}</div>`
      + `<div class="grade">`
      + `<button data-g="ok"  class="${g==='ok'?'on':''}">✓ đúng</button>`
      + `<button data-g="hm"  class="${g==='hm'?'on':''}">? ngờ</button>`
      + `<button data-g="bad" class="${g==='bad'?'on':''}">✗ sai</button></div>`;
    div.addEventListener('click', ev => {
      const bt = ev.target.closest('button');
      if (bt){
        ev.stopPropagation();
        const g = bt.dataset.g;
        if (grades[key] === g) delete grades[key]; else grades[key] = g;
        localStorage.setItem('wyGrades7', JSON.stringify(grades));
        renderList();
        return;
      }
      gotoRange(k);
    });
    el.appendChild(div);
  });
  document.getElementById('cnt').textContent = L.length + ' mục';
  document.getElementById('lhTitle').textContent =
    tab === 'keep' ? 'RANGE ĐƯỢC VẼ' : 'ỨNG VIÊN BỊ BỎ (không vẽ trên Quantower)';
  document.querySelectorAll('.tab').forEach(b =>
    b.classList.toggle('on', b.dataset.t === tab));
}
document.querySelectorAll('.tab').forEach(b => b.addEventListener('click', () => {
  if (tab === b.dataset.t) return;
  tab = b.dataset.t; sel = -1; renderList(); draw();
  if (curList().length) gotoRange(0);
}));

document.getElementById('btnDump').addEventListener('click', () => {
  const ta = document.getElementById('dump');
  const one = (r,k,t) => ({
    nhom: t==='keep'?'được vẽ':'bị bỏ', n: k+1, loai: r.k,
    tu: fmtT(tm(r.s)), den: fmtT(tm(r.e)),
    gia: fmtP(px(r.lo))+'-'+fmtP(px(r.hi)),
    phase: r.ph.map(p=>p.p).join(''), boVi: r.why || '',
    cham: grades[t+k] || '(chưa chấm)'
  });
  const out = D.ranges.map((r,k)=>one(r,k,'keep')).concat(D.drops.map((r,k)=>one(r,k,'drop')));
  ta.value = JSON.stringify(out, null, 1);
  ta.style.display = 'block'; ta.select();
});
for (const id of ['cbEv','cbPh','cbOnly','cbVol','cbDrop','cbNoST'])
  document.getElementById(id).addEventListener('change', draw);

document.getElementById('meta').innerHTML =
  D.first + ' → ' + D.last + ' (UTC) · ' + N.toLocaleString('vi') + ' nến M1<br>'
  + 'Nguồn: dxFeed GCQ26 · thuật toán y hệt ScanWyckoff() trong WyckoffRunner.cs';
document.querySelector('.tab[data-t="keep"]').textContent = 'Được vẽ (' + D.ranges.length + ')';
document.querySelector('.tab[data-t="drop"]').textContent = 'Bị bỏ (' + D.drops.length + ')';

function viewAll(){ bw = Math.max(0.02, plot().w / N); i0 = 0; draw(); }
document.getElementById('btnAll').addEventListener('click', viewAll);

renderList();
resize();
viewAll();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    main()
