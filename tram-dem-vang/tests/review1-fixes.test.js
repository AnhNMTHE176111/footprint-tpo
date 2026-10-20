'use strict';
// Test cho từng lỗi đã sửa ở vòng 2 (REVIEW-1 / USER-TEST-1)
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, go, ANS_NONE, run, closed, trade, engine, SETTINGS } = require('./helpers.js');
const J = require('../js/journal.js');
const R = require('../js/rules.js');

const NOWMS = Date.UTC(2026, 9, 13, 14, 30);

test('mục 1 · cân bằng rồi vừa phá lại ⇒ cú phá mới, chưa được công nhận', () => {
  const n = J.newNight('2026-10-13');
  J.setRegimeMode(n, 'broken', NOWMS);
  Object.assign(n.regime.breakout, { dir: 'down', edgeZoneId: 'z1', step1: true, step2: true });
  assert.equal(R.effectiveRegime(n.regime).effective, 'broken');
  J.setRegimeMode(n, 'balanced', NOWMS);
  J.setRegimeMode(n, 'broken', NOWMS);
  assert.equal(n.regime.breakout.step1, false); assert.equal(n.regime.breakout.step2, false);
  assert.equal(n.regime.breakout.dir, null); assert.equal(n.regime.breakout.edgeZoneId, null);
  assert.equal(n.regime.breakout.at, '21:30');
  assert.equal(R.effectiveRegime(n.regime).effective, 'balanced');
});
test('mục 1 · cú phá cũ không làm A bị tắt oan: giờ phá cũ bị xóa khi chui lại', () => {
  const n = J.newNight('2026-10-13');
  J.setRegimeMode(n, 'broken', NOWMS);
  Object.assign(n.regime.breakout, { dir: 'down', edgeZoneId: 'z1', at: '18:30', step1: true, step2: true });
  J.breakoutFailed(n, NOWMS);
  const bo = n.regime.breakout;
  assert.deepEqual([bo.dir, bo.edgeZoneId, bo.at, bo.nth, n.regime.mode], [null, null, null, 2, 'balanced']);
});

test('mục 3 · bias KHÔNG: C chỉ ở VAH / VAL Âu', () => {
  const zs = (type) => [{ id: 'z1', type, price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'vwapW', price: 4182 }];
  const bad = go('C', { answers: ANS_NONE, zones: zs('lowY') });
  assert.equal(bad.verdict, 'NO'); assert.ok(bad.reasons.includes('NO_BIAS_NONE_EDGE'));
  const bad2 = go('C', { answers: ANS_NONE, zones: zs('ibLow') });
  assert.ok(bad2.reasons.includes('NO_BIAS_NONE_EDGE'));
  const ok = go('C', { answers: ANS_NONE, zones: zs('valEu') });
  assert.equal(ok.verdict, 'ENTRY'); assert.ok(ok.half.reasons.includes('BIAS_NONE'));
});

test('mục 4 · chuỗi SL cộng cả khi đóng "Về hòa" ở giá lỗ; hòa thật thì reset', () => {
  const sl = () => closed('SL', -1);
  assert.equal(engine.countTrades({ trades: [sl(), sl(), closed('BE', -1)] }).slStreak, 3);
  assert.equal(engine.countTrades({ trades: [sl(), sl(), closed('BE', 0)] }).slStreak, 0);
  assert.equal(engine.countTrades({ trades: [sl(), closed('TP', 1, {}), sl()] }).slStreak, 1);
});

test('mục 5 · cửa sổ 19:30 mặc định: bật thứ Năm; chưa qua tầng 0 hoặc ngày tin thì tự bật', () => {
  assert.equal(J.newNight('2026-10-15').t0.windows[0].on, true);    // thứ Năm
  assert.equal(J.newNight('2026-10-13').t0.windows[0].on, false);   // thứ Ba
  const w = (t0) => R.effectiveWindows(Object.assign({ windows: R.defaultWindows(false) }, t0), '2026-10-13')[0].on;
  assert.equal(w({ touched: false }), true);
  assert.equal(w({ touched: true }), false);
  assert.equal(w({ touched: true, newsDay: true }), true);
  assert.equal(w({ touched: false, windows: [Object.assign(R.defaultWindows(false)[0], { offAt: '18:10' })] }), false);
  // engine: thứ Hai 19:25, chưa qua tầng 0 ⇒ chặn; đã qua tầng 0 ⇒ ca ĐÚNG 5/10 không bị chặn
  const blocked = run('2026-10-05', '19:25', mk('B', (n) => { n.t0.windows = R.defaultWindows(false); n.t0.touched = false; }));
  assert.ok(blocked.verdict === 'NO' && blocked.reasons[0] === 'NO_NEWS_WINDOW');
  const free = run('2026-10-05', '19:25', mk('B', (n) => { n.t0.windows = R.defaultWindows(false); n.t0.touched = true; }));
  assert.notEqual(free.reasons[0], 'NO_NEWS_WINDOW');
});

test('mục 7 · vùng kế tiếp bỏ vùng cùng cụm và LVN', () => {
  const r = go('B', { zones: [{ id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'valEu', price: 4182 }, { id: 'z4', type: 'lvn', price: 4186 }, { id: 'z3', type: 'vahEu', price: 4195 }],
    setup: { zoneId: 'z1', calc: { entry: 4181.5, sl: 4179, tp: null } } });
  assert.ok(!r.reasons.includes('NO_RR'), JSON.stringify(r.reasons));
  assert.equal(r.calc.nextZone.id, 'z3');
});

test('mục 8 · NO_MID_RANGE không bắn khi pending (B tại VWAP tuần)', () => {
  const r = go('B', { regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z3', at: '20:40', nth: 1, step1: true, step2: false } } });
  assert.equal(r.regime.effective, 'pending');
  assert.ok(!r.reasons.includes('NO_MID_RANGE'), JSON.stringify(r.reasons));
});

test('QĐ-20 · 0 hợp đồng ⇒ NO_SIZE_ZERO, htRef ST §6; ENTRY in số hợp đồng khi ≥ 1', () => {
  const r = run('2026-10-13', '21:30', mk('B'), { dstShift: true, capital: 500, riskPct: 2 });
  assert.equal(r.verdict, 'NO'); assert.equal(r.reasons[r.reasons.length - 1], 'NO_SIZE_ZERO');
  assert.equal(require('../js/content.js').codes.NO_SIZE_ZERO.htRef, 'ST §6');
  assert.equal(go('B').calc.size >= 1, true);
});

test('mục 9 · cửa sổ tự thêm múi VN không cộng 1 giờ mùa đông', () => {
  const time = require('../js/time.js');
  const w = { id: 'x', at: '21:00', tz: 'VN', minutesBefore: 5, minutesAfter: 5, on: true };
  assert.equal(time.windowRange(w, '2026-11-10', true).center, 21 * 60);
  assert.equal(time.windowRange({ at: '21:00', tz: 'ET' }, '2026-11-10', true).center, 22 * 60);
  assert.match(require('../js/content.js').ui.timePh, /VN/);
});
