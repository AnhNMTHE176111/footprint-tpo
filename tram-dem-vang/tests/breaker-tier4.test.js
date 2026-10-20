'use strict';
// Ngắt mạch (QĐ-10, QĐ-17) + tầng 4 (mốc be, lệnh mở qua đêm)
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, run, go, trade, closed, vn, time } = require('./helpers.js');
const J = require('../js/journal.js');

const NOW = vn('2026-10-13', '21:30');
const NOWMIN = 21 * 60 + 30;

function evalNight(n, hm) { return run('2026-10-13', hm || '21:30', n); }
function enterVia(n, o) { // mô phỏng bấm "Vào lệnh" / "Tôi vẫn vào" từ phán quyết hiện tại
  const res = evalNight(n);
  return J.createTrade(n, res, Object.assign({ kind: 'market', nowMs: NOW.getTime(), nowMin: NOWMIN }, o || {}));
}

test('2 lệnh phá luật ⇒ TẮT MÁY (OFF_RULE_BREAKS), dù mọi thứ khác ENTRY', () => {
  const n = mk('A', { trades: [closed('SL', -1, { flags: ['RULE_BREAK'] }), closed('TP', 3, { flags: ['RULE_BREAK'] })] });
  const r = evalNight(n);
  assert.equal(r.verdict, 'OFF'); assert.deepEqual(r.reasons, ['OFF_RULE_BREAKS']);
});
test('1 lệnh phá luật chưa tắt máy', () => {
  assert.equal(evalNight(mk('A', { trades: [closed('TP', 3, { flags: ['RULE_BREAK'] })] })).verdict, 'ENTRY');
});
test('"Tôi vẫn vào" ×2 ⇒ TẮT MÁY (đi qua journal thật)', () => {
  const n = mk('A', { setup: { b1: 'V' } });
  const saved = JSON.parse(JSON.stringify(n.setup));
  const t1 = enterVia(n, { ruleBreak: true });
  assert.deepEqual(n.setup, {});                       // ghi lệnh xong ⇒ về "Kèo mới" (USER-TEST mục 3)
  assert.ok(t1.flags.includes('RULE_BREAK')); assert.deepEqual(t1.ruleCodes, ['NO_V_PULLBACK']);
  J.closeTrade(n, { kind: 'SL', nowMs: NOW.getTime(), nowMin: NOWMIN + 5 });
  assert.equal(evalNight(n).verdict, 'WAIT');          // setup trống ⇒ CHỜ chọn kịch bản
  n.setup = saved; n.setup.zoneId = 'z2';
  enterVia(n, { ruleBreak: true });
  J.closeTrade(n, { kind: 'BE', nowMs: NOW.getTime(), nowMin: NOWMIN + 9 });
  const r = evalNight(n);
  assert.equal(r.verdict, 'OFF'); assert.equal(r.counts.ruleBreaks, 2);
});
test('"Tôi vẫn vào" khi đang TẮT MÁY cũng ghi dòng sổ + mã', () => {
  const n = mk('A', { trades: [closed('SL', -1, { flags: ['RULE_BREAK'] }), closed('SL', -1, { flags: ['RULE_BREAK'] })] });
  const t = enterVia(n, { ruleBreak: true });
  assert.deepEqual(t.ruleCodes, ['OFF_RULE_BREAKS']);
});
test('3 SL liên tiếp ⇒ OFF_SL_STREAK; hòa và TP reset; chỉ SL cộng chuỗi', () => {
  const sl = () => closed('SL', -1);
  assert.equal(evalNight(mk('A', { trades: [sl(), sl(), sl()] })).reasons[0], 'OFF_SL_STREAK');
  assert.equal(evalNight(mk('A', { trades: [sl(), sl(), closed('TP', 3), sl()] })).counts.slStreak, 1);
  assert.equal(evalNight(mk('A', { trades: [sl(), sl(), closed('BE', 0), sl()] })).counts.slStreak, 1);
  assert.equal(evalNight(mk('A', { trades: [sl(), sl()] })).verdict, 'ENTRY');
  assert.equal(evalNight(mk('A', { trades: [sl(), sl(), trade({})] })).counts.slStreak, 2); // lệnh đang mở không tính
});
test('đêm mới về 0', () => {
  const prev = mk('A', { trades: [closed('SL', -1), closed('SL', -1), closed('SL', -1), closed('SL', -1, { flags: ['RULE_BREAK'] }), closed('SL', -1, { flags: ['RULE_BREAK'] })] });
  const r = run('2026-10-14', '21:30', mk('A'), null, { '2026-10-13': prev });
  assert.equal(r.verdict, 'ENTRY'); assert.equal(r.counts.slStreak, 0); assert.equal(r.counts.ruleBreaks, 0);
});
test('đóng tay "khác" ⇒ phá luật; "đóng sạch trước tin" và "hấp thụ ngược" ⇒ không', () => {
  const close = (reason) => {
    const n = mk('A'); enterVia(n);
    return J.closeTrade(n, { kind: 'MANUAL', price: 4192, reason, nowMs: NOW.getTime(), nowMin: NOWMIN + 3 });
  };
  assert.ok(close('other').flags.includes('RULE_BREAK'));
  assert.ok(!close('flat').flags.includes('RULE_BREAK'));
  assert.ok(!close('absorb').flags.includes('RULE_BREAK'));
});
test('luyện mắt (paper) không cộng chuỗi SL, phá luật, lần tại vùng', () => {
  const n = mk('A', { setup: { b1: 'V' } });
  const p = enterVia(n, { ruleBreak: true, paper: true });
  assert.ok(p.flags.includes('paper')); assert.ok(!p.flags.includes('RULE_BREAK'));
  J.closeTrade(n, { kind: 'SL', nowMs: NOW.getTime(), nowMin: NOWMIN + 4 });
  const paper = (k) => closed(k, -1, { flags: ['paper', 'RULE_BREAK'], zoneId: 'z2' });
  const r = evalNight(mk('A', { trades: [paper('SL'), paper('SL'), paper('SL')] }));
  assert.equal(r.verdict, 'ENTRY'); assert.equal(r.counts.slStreak, 0); assert.equal(r.counts.ruleBreaks, 0); assert.equal(r.counts.zoneN, 0);
  assert.equal(n.tally.machine, 0);
});
test('limit: hủy ⇒ xóa dòng, không tăng đếm; khớp ⇒ giá vào thật', () => {
  const n = mk('B');
  const t = enterVia(n, { kind: 'limit', price: 4176.5 });
  assert.equal(n.open.status, 'pending'); assert.equal(t.entry, null); assert.equal(n.trades.length, 1);
  J.cancelLimit(n);
  assert.equal(n.trades.length, 0); assert.equal(n.open, null); assert.equal(evalNight(n).counts.zoneN, 0);
  enterVia(n, { kind: 'limit', price: 4176.5 });
  J.fillLimit(n, 4176.4);
  assert.equal(n.open.status, 'filled'); assert.equal(n.trades[0].entry, 4176.4);
});
test('vào lệnh tạo dòng sổ có id, exit null, chụp tests/mode/flags', () => {
  const n = mk('B');
  const t = enterVia(n);
  assert.ok(t.id); assert.equal(t.exit, null); assert.equal(t.mode, 'balanced'); assert.equal(t.zoneType, 'vwapW');
  assert.deepEqual(t.tests, { b1: 'U', c4: 'same', c4num: -49, b2: 'down', b3: 'ok', c5: 'near' });
  assert.equal(n.open.tradeId, t.id); assert.equal(t.slDist, 2.3); assert.equal(t.rrPlanned, 3);
  assert.equal(evalNight(n).verdict, 'LOCKED');
});

// ---------- tầng 4 ----------
test('mốc be: A/B +1,5R cần nến M1 đóng ngoài vùng; C/D +1R', () => {
  const a = { scenario: 'A', side: 'sell', entry: 4193, sl: 4195.4 };
  assert.equal(J.beStatus(a, { outsideZoneBar: true }, 4189.4).reached, true);   // 3,6 / 2,4 = 1,5R
  assert.equal(J.beStatus(a, { outsideZoneBar: true }, 4189.5).reached, false);
  assert.equal(J.beStatus(a, { outsideZoneBar: false }, 4189.4).ready, false);
});
test('mốc be: SL lẻ 0,1 (risk 2,3): +1,5R chạm từ 4180,5; 4180,4 chưa', () => {
  const b = { scenario: 'B', side: 'buy', entry: 4177.0, sl: 4174.7 };
  assert.equal(J.beStatus(b, { outsideZoneBar: true }, 4180.4).reached, false);
  assert.equal(J.beStatus(b, { outsideZoneBar: true }, 4180.5).reached, true);
  assert.equal(J.beStatus(b, { outsideZoneBar: false }, 4180.5).ready, false);
  assert.equal(J.beStatus(b, { outsideZoneBar: true }, 4180.5).ready, true);
  assert.equal(J.beStatus(b, null, 4180.5).target, 1.5);
});
test('mốc be: C/D +1R, không cần nến', () => {
  const c = { scenario: 'C', side: 'sell', entry: 4193, sl: 4195.4 };
  assert.equal(J.beStatus(c, null, 4190.6).reached, true);
  assert.equal(J.beStatus(c, null, 4190.7).reached, false);
  assert.equal(J.beStatus(c, null, 4190.6).ready, true);
  const d = { scenario: 'D', side: 'buy', entry: 4177.0, sl: 4174.7 };
  assert.equal(J.beStatus(d, null, 4179.3).reached, true);
  assert.equal(J.beStatus(d, null, 4179.2).reached, false);
});
test('R: TP, SL, hòa, đóng tay', () => {
  const n = mk('A'); enterVia(n);
  const t = n.trades[0];
  assert.equal(J.computeR(t, 4185.8), 3);
  assert.equal(J.computeR(t, 4195.4), -1);
  assert.equal(J.computeR(t, 4193), 0);
  assert.equal(J.computeR(t, 4190.6), 1);
  J.closeTrade(n, { kind: 'TP', nowMs: NOW.getTime(), nowMin: NOWMIN + 20 });
  assert.equal(t.r, 3); assert.equal(n.tally.machine, 3); assert.equal(n.open, null);
});
test('lệnh mở qua mốc đêm mới: engine với nightKey mới vẫn khóa tầng 3', () => {
  const prev = mk('A'); enterVia(prev);
  const r = run('2026-10-14', '05:30', mk('A'), null, { '2026-10-13': prev });
  assert.equal(r.verdict, 'LOCKED'); assert.equal(r.open.trade.id, prev.trades[0].id);
});
test('đếm ngược "đóng sạch trước": 19:15 (cửa sổ hạng 1) và 00:45 (FOMC); mùa đông +1h', () => {
  const w = [{ id: 'w', kind: 'news', rank: 1, at: '19:30', tz: 'ET', minutesBefore: 15, minutesAfter: 15, on: true }, { id: 'f', kind: 'fomc', rank: 2, at: '01:00', tz: 'ET', minutesBefore: 0, minutesAfter: 30, on: true }];
  const dl = (key, min) => time.flatDeadline(w, min, key, true);
  assert.equal(time.fmtMin(dl('2026-10-13', 18 * 60).at), '19:15');
  assert.equal(time.fmtMin(dl('2026-10-13', 20 * 60).at), '00:45');
  assert.equal(time.fmtMin(dl('2026-11-10', 18 * 60).at), '20:15');
  assert.equal(time.fmtMin(dl('2026-11-10', 21 * 60).at), '01:45');
});
