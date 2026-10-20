'use strict';
// Sổ (ghi lệnh từ khối, nhập kết quả, cộng R, 4 con số tuần, Markdown, dòng ⚠) + store (migrate v1 → v2, nhập JSON gộp)
const test = require('node:test');
const assert = require('node:assert/strict');
const J = require('../js/journal.js');
const S = require('../js/store.js');
const { trade, closed, mk, run, ticksAll, vn, DATE } = require('./helpers.js');

const NOW = vn(DATE, '21:30');
const NOWMIN = 21 * 60 + 30;

function sampleNight() {
  const n = J.newNight();
  n.trades = [
    trade({ id: 'a1', time: '20:25', side: 'sell', scenario: 'A', zoneType: 'hvnW', ticks: { chk1: true, chk2: true, chk3: true }, slDist: 2.4, exit: { kind: 'TP', price: 4185.8, at: '20:50' }, r: 3 }),
    trade({ id: 'a2', time: '20:48', side: 'sell', scenario: 'B', zoneType: 'vwapW', ticks: { chk2: true }, slDist: 1.2, missing: ['chk1', 'chk2'],
      exit: { kind: 'SL', price: 0, at: '20:55' }, r: -1, flags: ['RULE_BREAK'] })
  ];
  return n;
}

// ---------- ghi lệnh từ khối ----------
test('ghi lệnh: dòng Sổ có giờ, hướng, kịch bản, vùng, R mục tiêu, các ô đã tick (không còn giá); khối chỉ xóa Điểm vào và ô SL', () => {
  const n = mk('B');
  const res = run(DATE, '21:30', n);
  const t = J.createTrade(n, res, { scen: 'B', nowMs: NOW.getTime(), nowMin: NOWMIN });
  assert.ok(t.id); assert.equal(t.exit, null); assert.equal(t.time, '21:30'); assert.equal(t.side, 'buy'); assert.equal(t.scenario, 'B');
  assert.equal(t.zoneId, 'z1'); assert.equal(t.zoneType, 'vwapW'); assert.equal(t.targetR, 3);
  assert.deepEqual([t.entry, t.sl, t.tp, t.size, t.rrPlanned], [null, null, null, null, null]);
  assert.deepEqual(t.ticks, ticksAll('B')); assert.deepEqual(t.flags, []); assert.deepEqual(t.missing, []);
  assert.equal(n.trades.length, 1);
  const bs = n.se.blocks.B;
  const keep = ticksAll('B'); ['ent1', 'sl1', 'sl2', 'sl3', 'sl4'].forEach((k) => delete keep[k]);
  assert.deepEqual(bs.ticks, keep); assert.equal(bs.side, 'buy'); assert.equal(bs.zoneId, 'z1');
  const after = run(DATE, '21:31', n);
  assert.equal(after.common.filter((x) => x.id === 'open')[0].ok, false);
});

test('ghi lệnh "Vẫn vào": cờ phá luật + danh sách ô thiếu; lệnh luyện mắt không phá luật', () => {
  const n = mk('A', (x) => { delete x.se.blocks.A.ticks.chk1; delete x.se.blocks.A.ticks.ctx2; });
  const res = run(DATE, '21:30', n);
  const t = J.createTrade(n, res, { scen: 'A', ruleBreak: true, missing: res.blocks.A.missing, nowMs: NOW.getTime(), nowMin: NOWMIN });
  assert.ok(t.flags.includes('RULE_BREAK')); assert.deepEqual(t.missing, ['ctx2', 'chk1']);
  assert.equal(J.warnLine(t), 'phá luật: thiếu 2 ô: Nhịp hồi về cạnh giữ được, không nến M5 nào đóng ngược vào trong; Hồi hình U, ≥ 3 nến, không phải V');
  const n2 = mk('A', (x) => { delete x.se.blocks.A.ticks.chk1; });
  const p = J.createTrade(n2, run(DATE, '21:30', n2), { scen: 'A', ruleBreak: true, paper: true, missing: ['chk1'], nowMs: NOW.getTime(), nowMin: NOWMIN });
  assert.ok(p.flags.includes('paper')); assert.ok(!p.flags.includes('RULE_BREAK'));
});
test('ghi lệnh: cờ ngược bias và cỡ ½ kèm lý do ngược bias', () => {
  const n = mk('C', (x) => { x.se.blocks.C.side = 'sell'; x.se.blocks.C.entry = 4176; x.se.blocks.C.sl = 4178.4; x.se.blocks.C.tp = 4171.2; x.se.blocks.C.reason = 'tail thật'; });
  const t = J.createTrade(n, run(DATE, '21:30', n), { scen: 'C', nowMs: NOW.getTime(), nowMin: NOWMIN });
  assert.ok(t.flags.includes('COUNTER_BIAS')); assert.ok(t.flags.includes('HALF')); assert.equal(t.counterBiasReason, 'tail thật');
});
test('khối: touchBlock đánh dấu khối chạm cuối; clearBlock chỉ xóa tick và số', () => {
  const n = J.newNight();
  J.block(n, 'A').side = 'buy'; J.touchBlock(n, 'A'); J.touchBlock(n, 'C');
  assert.equal(n.se.last, 'C'); assert.deepEqual(n.se.touch, { A: 1, C: 2 });
  J.block(n, 'A').ticks.ctx1 = true; J.block(n, 'A').sl = 4170;
  assert.equal(J.setupActive(n), true);
  J.clearBlock(n, 'A');
  assert.equal(J.setupActive(n), false); assert.equal(n.se.blocks.A.side, 'buy'); assert.equal(n.se.blocks.A.sl, undefined);
});

// ---------- nhập kết quả ngay trên dòng ----------
test('kết quả: TP / SL / hòa lấy R mặc định (TP = R mục tiêu, SL = -1, hòa = 0), R nhập tay ghi đè, cộng vào máy cộng', () => {
  const n = mk('A');
  const t = J.createTrade(n, run(DATE, '21:30', n), { scen: 'A', nowMs: NOW.getTime(), nowMin: NOWMIN });
  J.closeTrade(n, t.id, { kind: 'TP', nowMs: NOW.getTime(), nowMin: NOWMIN + 20 });
  assert.equal(t.r, 3); assert.equal(n.tally.machine, 3);
  const u = trade({ id: 'u', side: 'sell', scenario: 'C', targetR: 2 }); n.trades.push(u);
  J.closeTrade(n, 'u', { kind: 'TP', nowMs: NOW.getTime(), nowMin: NOWMIN + 25 });
  assert.equal(u.r, 2);
  const v = trade({ id: 'v', side: 'sell' }); n.trades.push(v);
  J.closeTrade(n, 'v', { kind: 'SL', nowMs: NOW.getTime(), nowMin: NOWMIN + 30 });
  assert.equal(v.r, -1);
  const w = trade({ id: 'w', side: 'sell' }); n.trades.push(w);
  J.closeTrade(n, 'w', { kind: 'BE', nowMs: NOW.getTime(), nowMin: NOWMIN + 40 });
  assert.equal(w.r, 0);
  const x = trade({ id: 'x2', side: 'sell' }); n.trades.push(x);
  J.closeTrade(n, 'x2', { kind: 'TP', r: 2.5, nowMs: NOW.getTime(), nowMin: NOWMIN + 50 });
  assert.equal(x.r, 2.5); assert.equal(n.tally.machine, 3 + 2 - 1 + 0 + 2.5);
  assert.equal(J.closeTrade(n, 'khong-co', { kind: 'TP' }), null);
  // dữ liệu cũ còn giá vào / SL: vẫn tính R từ giá thoát
  const old = trade({ id: 'old', side: 'sell', entry: 4193, sl: 4195.4 }); n.trades.push(old);
  J.closeTrade(n, 'old', { kind: 'MANUAL', price: 4190.6, reason: 'flat', nowMs: 1, nowMin: NOWMIN });
  assert.equal(old.r, 1); assert.equal(J.computeR(old, 4195.4), -1);
});

test('kết quả: đóng tay lý do "khác" ⇒ phá luật, hai lý do kia thì không; R nhập tay', () => {
  const mkTrade = () => { const n = J.newNight(); const t = trade({ id: 'x', side: 'sell' }); n.trades.push(t); return { n, t }; };
  let { n, t } = mkTrade();
  J.closeTrade(n, 'x', { kind: 'MANUAL', r: 1, reason: 'flat', nowMs: 1, nowMin: NOWMIN });
  assert.equal(t.r, 1); assert.ok(!t.flags.includes('RULE_BREAK'));
  ({ n, t } = mkTrade());
  J.closeTrade(n, 'x', { kind: 'MANUAL', r: 0.8, reason: 'absorb', nowMs: 1, nowMin: NOWMIN });
  assert.equal(t.r, 0.8); assert.ok(!t.flags.includes('RULE_BREAK'));
  ({ n, t } = mkTrade());
  J.closeTrade(n, 'x', { kind: 'MANUAL', r: 0.3, reason: 'other', nowMs: 1, nowMin: NOWMIN });
  assert.ok(t.flags.includes('RULE_BREAK')); assert.deepEqual(t.ruleCodes, ['MANUAL_CLOSE']);
  assert.equal(J.warnLine(t), 'phá luật: đóng tay lý do khác');
});

test('nhắc be theo kịch bản: A, B +1,5R và cần nến M1 đóng ngoài vùng; C, D +1R (không còn giá)', () => {
  const a = J.beInfo({ scenario: 'A' });
  assert.deepEqual([a.target, a.needBar, a.priceAt], [1.5, true, undefined]);
  const c = J.beInfo({ scenario: 'C' });
  assert.deepEqual([c.target, c.needBar], [1, false]);
  assert.equal(J.beInfo({ scenario: 'B' }).target, 1.5);
});

test('sổ: máy cộng R, lệch tay ⇒ mismatch', () => {
  const n = sampleNight();
  assert.equal(J.recomputeTally(n, 1000), 2);
  assert.equal(n.tally.closedAt, 1000);
  assert.equal(J.tallyMismatch(n), false);          // chưa nhập tay
  J.manualTally(n, 2); assert.equal(J.tallyMismatch(n), false);
  J.manualTally(n, 3); assert.equal(J.tallyMismatch(n), true);
});
test('sổ: lệnh luyện mắt và lệnh chưa đóng không vào máy cộng', () => {
  const n = sampleNight();
  n.trades.push(closed('TP', 3, { flags: ['paper'] }), trade({ exit: null }));
  assert.equal(J.recomputeTally(n), 2);
});
test('sổ: dòng ⚠ liệt kê tối đa 3 ô thiếu, nói số ô còn lại', () => {
  assert.equal(J.warnLine({ scenario: 'B', missing: ['chk1', 'chk2'], ruleCodes: [] }), 'phá luật: thiếu 2 ô: 3 nến cuối: thân và |delta| giảm dần, không cực trị mới; Bong bóng ở cực trị cùng phe với lệnh');
  const w = J.warnLine({ scenario: 'C', missing: ['side', 'zone', 'ent1', 'zone2', 'common:news'], ruleCodes: [] });
  assert.match(w, /^phá luật: thiếu 5 ô: Hướng; Vùng; Nến M1 đóng lại trong range; thân không ngắn, râu ngược không dài \(\+2\)$/);
  assert.equal(J.warnLine({ scenario: 'A', missing: [], ruleCodes: [] }), '');
  assert.equal(J.warnLine({ scenario: 'A', missing: ['common:news'], ruleCodes: [] }), 'phá luật: thiếu 1 ô: Không trong khung giờ cấm');
});
test('sổ: 7 cột — vùng thay chế độ, cột "4 kiểm tra" in các ô kiểm tra đã tick', () => {
  const base = { time: '20:00', side: 'sell', slDist: 2.4, exit: { kind: 'TP' }, r: 3, flags: [], ruleCodes: [], zoneType: 'hvnW' };
  const row = (scenario, ticks, o) => J.rowOf(trade(Object.assign({}, base, { scenario, ticks }, o || {})));
  assert.equal(row('A', { chk1: true, chk2: true, chk3: true }).checks, 'U · Δ · bb');
  assert.equal(row('B', { chk1: true, chk3: true, chk4: true }).checks, 'giảm dần · DMA · U');
  assert.equal(row('C', { chk1: true }).checks, 'phá hụt');
  assert.equal(row('D', {}).checks, '—');
  assert.equal(row('A', { ctx1: true, ent1: true }).checks, '—');           // chỉ in nhóm "Kiểm tra"
  assert.equal(row('A', {}).zone, 'HVN tuần');
  assert.equal(row('A', {}, { zoneType: 'pocCluster' }).zone, 'Cụm POC');
  assert.equal(row('A', {}).name, 'phá hồi'); assert.equal(row('B', {}).name, 'hấp thụ'); assert.equal(row('C', {}).name, 'fade cạnh'); assert.equal(row('D', {}).name, 'trap');
  assert.equal(row('A', {}, { exit: null, r: null }).r, '…');
});
test('sổ: Markdown đúng mẫu (so chuỗi)', () => {
  const n = sampleNight();
  J.recomputeTally(n, 5000); J.manualTally(n, 2);
  const want = [
    '# Sổ đêm 2026-10-06',
    '',
    '| giờ | hướng | tên | vùng | 4 kiểm tra | SL | R |',
    '|---|---|---|---|---|---|---|',
    '| 20:25 | sell | phá hồi | HVN tuần | U · Δ · bb | 2,4 | +3 |',
    '| 20:48 | sell | hấp thụ | VWAP tuần | bb | 1,2 | -1 ⚠ |',
    '',
    'Cột "4 kiểm tra": các ô kiểm tra đã tick lúc ghi lệnh (U nhịp hồi · bb bong bóng · Δ delta · cạnh · DMA).',
    '',
    '⚠ dòng 20:48 phá luật: thiếu 2 ô: 3 nến cuối: thân và |delta| giảm dần, không cực trị mới; Bong bóng ở cực trị cùng phe với lệnh',
    '',
    'Máy cộng: +2 R · Bạn cộng: +2 R · Lệnh phá luật: 1 · SL bị quét rồi tới TP: 0',
    ''
  ].join('\n');
  assert.equal(J.toMarkdown(n, '2026-10-06'), want);
});
test('sổ: Markdown khi chưa nhập "Bạn cộng"', () => {
  assert.match(J.toMarkdown(J.newNight(), '2026-10-06'), /Máy cộng: 0 R · Bạn cộng: — · Lệnh phá luật: 0/);
});
test('sổ: Markdown có thẻ phiên (bias, vùng) và không còn dòng chế độ', () => {
  const n = mk('B');
  const md = J.toMarkdown(n, DATE);
  assert.match(md, /## Thẻ phiên \(19:00\)/); assert.match(md, /BIAS: BUY/); assert.match(md, /z1 VWAP tuần 4176,5/); assert.doesNotMatch(md, /Chế độ/);
});
test('sổ: định dạng số dấu phẩy, ô nhập nhận cả dấu chấm', () => {
  assert.equal(J.fmt(2.4), '2,4'); assert.equal(J.fmt(null), '—'); assert.equal(J.fmtR(1.5), '+1,5'); assert.equal(J.fmtR(-1), '-1'); assert.equal(J.fmtR(0), '0');
  assert.equal(J.fmtTrim(3.333), '3,33');
  assert.equal(J.parseNum('4193.5'), 4193.5); assert.equal(J.parseNum('4193,5'), 4193.5); assert.equal(J.parseNum(' 2,4 '), 2.4);
  assert.equal(J.parseNum(''), null); assert.equal(J.parseNum('abc'), null); assert.equal(J.parseNum('-'), null);
});
test('sổ: CSV có đủ cột, in ô thiếu và thoát dấu phẩy', () => {
  const st = S.defaultState(); st.nights['2026-10-06'] = sampleNight();
  const lines = J.toCSV(st).trim().split('\n');
  assert.equal(lines.length, 3);
  assert.equal(lines[0].split(',').length, 11);
  assert.match(lines[2], /RULE_BREAK/); assert.match(lines[2], /chk1\|chk2/); assert.match(lines[1], /"U · Δ · bb"|U · Δ · bb/);
});
test('tuần: 4 con số HT 8 + chuỗi đêm 0 phá luật', () => {
  const st = S.defaultState();
  const night = (key, trades, locked) => { const n = J.newNight(); n.trades = trades; n.card.lockedAt = locked ? '19:00' : null; st.nights[key] = n; };
  night('2026-10-12', [closed('TP', 3, { scenario: 'A', zoneType: 'vwapW' }), closed('SL', -1, { scenario: 'B', zoneType: 'vwapW', sweptThenTP: true })], true);
  night('2026-10-13', [closed('SL', -1, { scenario: 'A', zoneType: 'hvnW', flags: ['RULE_BREAK'] }), closed('TP', 2, { scenario: 'B', zoneType: 'highY', flags: ['COUNTER_BIAS'] }), closed('TP', 5, { flags: ['paper'] })], true);
  night('2026-10-14', [closed('TP', 3, { scenario: 'A', zoneType: 'vwapW' })], true);
  night('2026-10-19', [closed('TP', 3, { scenario: 'A' })], true);                 // tuần khác
  const w = J.weekStats(st, '2026-10-14');
  assert.equal(w.week, '2026-10-12');
  assert.equal(w.trades, 5); assert.equal(w.ruleBreaks, 1); assert.equal(w.swept, 1);
  assert.deepEqual(w.byScenario.A, { n: 3, r: 5 }); assert.deepEqual(w.byScenario.B, { n: 2, r: 1 });
  assert.deepEqual(w.byZone.vwapW, { n: 3, r: 5 }); assert.deepEqual(w.counter, { n: 1, r: 2 });
  assert.equal(w.streak, 1);
  assert.equal(J.weekStats(st, '2026-10-12').streak, 1);
  assert.equal(J.weekStats(st, '2026-10-19').streak, 2);
});

// ---------- store ----------
function fakeStorage(init) {
  const m = Object.assign({}, init || {});
  return { getItem: (k) => (k in m ? m[k] : null), setItem: (k, v) => { m[k] = v; }, _m: m };
}
test('store: không có dữ liệu ⇒ trạng thái mặc định version 2; lưu rồi tải lại giữ nguyên', () => {
  const st = fakeStorage();
  const s0 = S.load(st);
  assert.equal(s0.version, 2); assert.equal(S.VERSION, 2); assert.equal(s0.settings.theme, 'dark'); assert.deepEqual(s0.nights, {});
  s0.nights['2026-10-06'] = sampleNight();
  assert.equal(S.save(st, s0), true);
  assert.deepEqual(S.load(st), S.migrate(s0));
});
test('store: migrate v1 → v2 giữ thẻ phiên, vùng, sổ; bỏ chế độ và kèo cũ; lệnh mở cũ thành dòng Sổ chưa có kết quả', () => {
  const v1 = { version: 1, settings: { capital: 3000 }, nights: { '2026-10-13': {
    t0: { alert: true, touched: true }, regime: { mode: 'broken', breakout: { dir: 'down' } }, setup: { scenario: 'A', zoneId: 'z2', b1: 'U' },
    card: { lockedAt: '19:00', answers: { q1: 'D', q5: 'below', vwapW: 'below' }, zones: [{ id: 'z1', type: 'vwapW', price: '4205' }, { id: 'z2', type: 'hvnW', price: 4195 }], plan1: 'sell nếu hồi' },
    open: { tradeId: 't9', status: 'filled', beDone: true },
    trades: [{ id: 't8', side: 'sell', scenario: 'A', mode: 'broken', entry: 4193, sl: 4195.4, exit: { kind: 'TP', price: 4185.8 }, r: 3, flags: [], ruleCodes: ['NO_V_PULLBACK'], tests: { b1: 'U' } },
      { id: 't9', side: 'sell', scenario: 'B', entry: 4190, sl: 4192, flags: ['HALF'] },
      { id: 't10', side: 'buy', scenario: 'B', entry: null, entryPlanned: 4180, sl: 4178, flags: [] }]
  } } };
  const m = S.migrate(v1);
  assert.equal(m.version, 2); assert.equal(m.settings.capital, 3000); assert.equal(m.settings.riskPct, 2);
  const n = m.nights['2026-10-13'];
  assert.equal(n.regime, undefined); assert.equal(n.setup, undefined); assert.equal(n.open, undefined);
  assert.deepEqual(n.se, { blocks: {}, common: {}, last: null, touch: {}, n: 0 });
  assert.equal(n.card.lockedAt, '19:00'); assert.equal(n.card.zones.length, 2); assert.equal(n.card.zones[0].price, 4205); assert.equal(n.card.plan1, 'sell nếu hồi');
  assert.equal(n.trades.length, 3); assert.equal(n.trades[0].r, 3); assert.deepEqual(n.trades[0].ruleCodes, ['NO_V_PULLBACK']);
  assert.deepEqual(n.trades.filter((t) => !t.exit).map((t) => t.id), ['t9', 't10']);     // lệnh mở cũ ⇒ dòng chưa có kết quả
  assert.equal(n.trades[2].entry, 4180);                                                   // limit chờ khớp lấy giá dự kiến
  assert.deepEqual(n.trades[1].ticks, {}); assert.deepEqual(n.trades[1].missing, []);
  // đêm sau còn thấy lệnh mở từ v1
  const r = run('2026-10-14', '21:30', mk('B'), null, m.nights);
  assert.equal(r.opens.length, 2); assert.equal(r.common.filter((x) => x.id === 'open')[0].ok, false);
  // đã là v2 thì chạy lại migrate không đổi gì
  assert.deepEqual(S.migrate(JSON.parse(JSON.stringify(m))), m);
});
test('store: migrate dữ liệu cũ không có version, thiếu trường', () => {
  const m = S.migrate({ nights: { '2026-10-01': { trades: [{ id: 'x', flags: [] }], card: { zones: [{ id: 'z1' }] } } }, settings: { capital: 3000 } });
  assert.equal(m.version, 2); assert.equal(m.settings.capital, 3000); assert.equal(m.settings.riskPct, 2); assert.equal(m.settings.dstShift, true);
  const n = m.nights['2026-10-01'];
  assert.equal(n.trades.length, 1); assert.deepEqual(n.card.answers, {}); assert.equal(n.t0.windows.length, 2);
  assert.equal(n.card.zones[0].id, 'z1');
});
test('store: JSON hỏng ⇒ mặc định, bản hỏng được giữ lại', () => {
  const st = fakeStorage({ 'tdv.v1': '{khong phai json' });
  const s = S.load(st);
  assert.deepEqual(s.nights, {}); assert.equal(st._m['tdv.v1.hong'], '{khong phai json');
});
test('store: localStorage ném lỗi ⇒ vẫn chạy', () => {
  const bad = { getItem() { throw new Error('chặn'); }, setItem() { throw new Error('chặn'); } };
  assert.deepEqual(S.load(bad).nights, {}); assert.equal(S.save(bad, S.defaultState()), false);
});
test('store: nhập JSON gộp theo trades.id, đêm trùng giữ bản có closedAt mới hơn', () => {
  const local = S.defaultState();
  const a = J.newNight(); a.trades = [closed('TP', 3, { id: 'a1', time: '20:25' })]; J.recomputeTally(a, 1000);
  local.nights['2026-10-06'] = a;
  const inc = S.defaultState();
  const b = J.newNight(); b.trades = [closed('TP', 3, { id: 'a1', time: '20:25' }), closed('SL', -1, { id: 'b2', time: '21:10' })]; J.recomputeTally(b, 2000); b.tally.manual = 2;
  inc.nights['2026-10-06'] = b;
  const c = J.newNight(); c.trades = [closed('TP', 2, { id: 'c3' })]; inc.nights['2026-10-07'] = c;
  const res = S.importMerge(local, S.exportJSON(inc));
  assert.equal(res.ok, true); assert.equal(res.nightsNew, 1); assert.equal(res.nightsMerged, 1); assert.equal(res.tradesAdded, 2);
  const n = res.state.nights['2026-10-06'];
  assert.deepEqual(n.trades.map((t) => t.id), ['a1', 'b2']);
  assert.equal(n.tally.manual, 2); assert.equal(n.tally.machine, 2);
  assert.equal(res.state.nights['2026-10-07'].trades[0].id, 'c3');
  const again = S.importMerge(res.state, S.exportJSON(inc));
  assert.equal(again.tradesAdded, 0); assert.equal(again.state.nights['2026-10-06'].trades.length, 2);
});
test('store: bản cũ hơn không đè bản mới; lệnh thiếu vẫn được bổ sung', () => {
  const local = S.defaultState(); const a = J.newNight(); a.trades = [closed('TP', 3, { id: 'a1' })]; J.recomputeTally(a, 5000); local.nights.k = a;
  const inc = S.defaultState(); const b = J.newNight(); b.trades = [closed('SL', -1, { id: 'zz', time: '23:00' })]; J.recomputeTally(b, 1000); inc.nights.k = b;
  const res = S.importMerge(local, S.exportJSON(inc));
  assert.equal(res.state.nights.k.tally.closedAt, 5000);
  assert.deepEqual(res.state.nights.k.trades.map((t) => t.id).sort(), ['a1', 'zz']);
});
test('store: tệp nhập sai ⇒ báo lỗi, không đụng dữ liệu', () => {
  const st = S.defaultState();
  assert.equal(S.importMerge(st, 'xx').ok, false);
  assert.equal(S.importMerge(st, '{"a":1}').ok, false);
});

// ---------- thẻ phiên ----------
test('thẻ phiên: chốt cần Q1, Q5, VWAP tuần, ≥ 1 vùng; Q6 suy từ vùng cạnh khi chốt', () => {
  const card = J.newNight().card;
  assert.deepEqual(J.canLockCard(card).missing, ['q1', 'q5', 'vwapW', 'zones']);
  Object.assign(card.answers, { q1: 'D', q5: 'in', vwapW: 'above' });
  card.zones.push({ id: 'z1', type: 'vwapW', price: 4180 });
  assert.equal(J.canLockCard(card).ok, true);
  const n = J.newNight(); n.card = card;
  J.lockCard(n, Date.UTC(2026, 9, 13, 11, 0));
  assert.equal(card.answers.q6, 'no');
  const n2 = J.newNight(); n2.card.answers = { q1: 'D', q5: 'in', vwapW: 'above' }; n2.card.zones = [{ id: 'z1', type: 'vahEu', price: 4190 }];
  J.lockCard(n2, Date.UTC(2026, 9, 13, 11, 0));
  assert.equal(n2.card.answers.q6, 'yes');
});
test('gõ nhanh vùng: mã + giá, khoảng giá, phía u / l, mục lạ báo lại', () => {
  const q = J.parseQuickZones('vwapw 4205, vah 4199; val 4185\nhvn 4195-4197, spu 4210, rel 4170, xx 5, high');
  assert.deepEqual(q.zones.map((z) => z.type), ['vwapW', 'vahEu', 'valEu', 'hvnW', 'sp', 'rangeEdge']);
  assert.equal(q.zones[3].priceTo, 4197);
  assert.deepEqual([q.zones[4].side, q.zones[5].side], ['upper', 'lower']);
  assert.deepEqual(q.bad, ['xx 5', 'high']);
  assert.deepEqual(J.parseQuickZones('').zones, []);
  assert.equal(J.parseQuickZones('vwapw 4205,5').zones[0].price, 4205);
});
