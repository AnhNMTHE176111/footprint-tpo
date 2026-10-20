'use strict';
// Vòng 4 — sửa theo REVIEW-3 và USER-TEST-3 (phần logic). Giờ viết theo giờ VN.
const test = require('node:test');
const assert = require('node:assert/strict');
const { go, mk, run, closed, DATE, SETTINGS, ANS_BUY, ANS_SELL, clone, engine, time } = require('./helpers.js');
const J = require('../js/journal.js');
const R = require('../js/rules.js');
const C = require('../js/content.js');

const streak = (trades) => engine.countTrades({ trades }).slStreak;
const manual = (r) => closed('MANUAL', r);

test('mục 1 · chuỗi SL: R ≤ −0,2 cộng; (−0,2; +0,2) là hòa reset; R ≥ +0,2 thắng reset', () => {
  assert.equal(streak([closed('SL', -1), closed('SL', -1), manual(-0.45)]), 3);   // trước đây −0,45R reset chuỗi, lách được TẮT MÁY
  assert.equal(streak([closed('SL', -1), closed('SL', -1), manual(-0.2)]), 3);
  assert.equal(streak([closed('SL', -1), closed('SL', -1), manual(-0.19)]), 0);
  assert.equal(streak([closed('SL', -1), closed('SL', -1), manual(0.19)]), 0);
  assert.equal(streak([closed('SL', -1), closed('SL', -1), manual(0.2)]), 0);
  assert.equal(streak([closed('SL', -1), closed('SL', -1), closed('TP', 3)]), 0);
  assert.equal(streak([closed('TP', 3), closed('SL', -1), manual(-0.3)]), 2);
  const sb = closed('SL', 0); sb.exit.beStop = true;
  assert.equal(streak([closed('SL', -1), closed('SL', -1), sb]), 0);   // SL sau be = hòa
  const sbBad = closed('SL', -0.4); sbBad.exit.beStop = true;
  assert.equal(streak([closed('SL', -1), sbBad]), 2);                   // gõ giá thoát xấu sau be: vẫn là SL
});
test('mục 1 · ba lệnh −0,45R liên tiếp ⇒ TẮT MÁY (không còn lách được)', () => {
  const r = go('B', { trades: [manual(-0.45), manual(-0.45), manual(-0.45)] });
  assert.equal(r.verdict, 'OFF'); assert.ok(r.reasons.includes('OFF_SL_STREAK'));
});

function brokenNight(over) {
  return mk('A', (n) => { Object.assign(n.regime.breakout, over || {}); });
}
test('mục 2 · đổi hướng phá sau khi công nhận ⇒ xóa bước 1, 2, giờ phá về bây giờ, chế độ không còn "vừa phá"', () => {
  const n = brokenNight({ at: '20:40' });
  const now = Date.UTC(2026, 9, 13, 14, 30);   // 21:30 VN
  assert.equal(J.setBreakoutField(n, 'dir', 'up', now), true);
  const bo = n.regime.breakout;
  assert.deepEqual([bo.dir, bo.step1, bo.step2, bo.at], ['up', false, false, '21:30']);
  assert.equal(n.regime.log.length, 1);
  const r = run(DATE, '21:30', n);
  assert.notEqual(r.regime.effective, 'broken');
  assert.equal(r.enabled.A, 'DIS_NOT_BROKEN');
});
test('mục 2 · đổi cạnh vừa phá cũng xóa công nhận; chọn lại đúng giá trị cũ hoặc lần chọn đầu thì không', () => {
  const now = Date.UTC(2026, 9, 13, 14, 30);
  const n = brokenNight({});
  assert.equal(J.setBreakoutField(n, 'edgeZoneId', 'z2', now), false);   // cùng giá trị
  assert.equal(n.regime.breakout.step2, true);
  assert.equal(J.setBreakoutField(n, 'edgeZoneId', 'z4', now), true);
  assert.deepEqual([n.regime.breakout.edgeZoneId, n.regime.breakout.step1, n.regime.breakout.step2], ['z4', false, false]);
  const fresh = mk('A', (m) => { m.regime.breakout = { dir: null, edgeZoneId: null, at: '20:40', nth: 1, step1: false, step2: false }; });
  assert.equal(J.setBreakoutField(fresh, 'dir', 'down', now), false);     // lần chọn đầu: giữ giờ đã gõ
  assert.equal(fresh.regime.breakout.at, '20:40');
});

test('mục 5 · kịch bản đang tắt (DIS_*): mọi luật NO vẫn được xét, "Tôi vẫn vào" ghi đủ mã, phán quyết không đổi', () => {
  const r = go('A', { regime: { mode: 'balanced' }, setup: { c5: 'far', b1: 'V' } });
  assert.equal(r.verdict, 'NO');
  assert.deepEqual(r.reasons, ['DIS_NOT_BROKEN']);
  assert.deepEqual(r.ruleReasons, ['DIS_NOT_BROKEN', 'NO_BACK', 'NO_V_PULLBACK']);
  assert.deepEqual(J.forceCodes(r), ['DIS_NOT_BROKEN', 'NO_BACK', 'NO_V_PULLBACK']);
});

test('mục 6 · thiếu vốn hoặc % rủi ro ⇒ CHỜ "Cài vốn" (không còn ENTRY không số hợp đồng)', () => {
  const ok = run(DATE, '21:30', mk('B'), SETTINGS);
  assert.equal(ok.verdict, 'ENTRY');
  for (const bad of [{ capital: null }, { capital: 0 }, { riskPct: null }]) {
    const r = run(DATE, '21:30', mk('B'), Object.assign({}, SETTINGS, bad));
    assert.equal(r.verdict, 'WAIT', JSON.stringify(bad));
    assert.ok(r.missing.includes('WAIT_CAPITAL'));
    assert.ok(C.codes.WAIT_CAPITAL.text);
  }
});

test('mục 7 · ghi đè bias bằng đúng bias tự động không phải ghi đè: DIS_BREAK_AGAINST_BIAS vẫn tắt A ở tầng 2', () => {
  const b = R.effectiveBias({ answers: clone(ANS_BUY), bias: { override: 'BUY', reason: 'chắc chắn' } });
  assert.equal(b.value, 'BUY'); assert.equal(b.overridden, false);
  const b2 = R.effectiveBias({ answers: clone(ANS_BUY), bias: { override: 'SELL', reason: 'lý do' } });
  assert.equal(b2.value, 'SELL'); assert.equal(b2.overridden, true);
  const r = go('A', (n) => { n.card.bias = { override: 'SELL', reason: 'x' }; n.regime.breakout.dir = 'up'; });
  assert.equal(r.enabled.A, 'DIS_BREAK_AGAINST_BIAS');
});

test('USER-TEST-3 · DIS_EARLY_BREAK chỉ áp khi giờ phá trong 18:00 đến giờ COMEX theo mùa; giờ ngoài giờ giao dịch (trước 18:00) không tắt A', () => {
  const at = (hm, date) => run(date || DATE, '21:30', brokenNight({ at: hm }), SETTINGS).enabled.A;
  assert.equal(at('14:05'), null);
  assert.equal(at('17:59'), null);
  assert.equal(at('18:50'), 'DIS_EARLY_BREAK');
  assert.equal(at('19:19'), 'DIS_EARLY_BREAK');
  assert.equal(at('19:30'), null);                       // hè: COMEX 19:20
  assert.equal(at('19:30', '2026-11-03'), 'DIS_EARLY_BREAK');   // đông: COMEX 20:20
  assert.equal(at('20:19', '2026-11-03'), 'DIS_EARLY_BREAK');
  assert.equal(at('20:20', '2026-11-03'), null);
});

test('USER-TEST-3 · cỡ ½ không chia được: số rủi ro thật của 1 hợp đồng', () => {
  const r = run(DATE, '20:24', mk('B'), SETTINGS);   // trước 20:30 ⇒ cỡ ½; SL 2,3 giá
  assert.equal(r.calc.sizeMinOne, true); assert.equal(r.calc.size, 1);
  assert.equal(r.calc.realUsd, 23);
  assert.equal(r.calc.riskUsd, 20);   // ½ kế hoạch
});

test('USER-TEST-3 · sao chép vùng: VWAP tuần chép sang thì giá điền luôn vào ô bias; chỉ nhắc mục có thật; không ghi đè số đã gõ', () => {
  const src = J.newNight('2026-10-12'); src.card.lockedAt = '19:00'; src.card.answers = {};
  src.card.zones = [{ id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'hvn3w', price: 4200 }];
  const cur = J.newNight('2026-10-13');
  const d = J.copyFromPrevDetail(cur, src);
  assert.equal(d.n, 2);
  assert.deepEqual(d.items, ['VWAP tuần 4181,0', 'HVN 3 tuần 4200,0']);   // không có "hình 3 tuần" vì đêm trước không trả lời Q1′
  assert.equal(cur.card.answers.vwapPrice, 4181);
  const cur2 = J.newNight('2026-10-13'); cur2.card.answers.vwapPrice = 4170; cur2.card.answers.priceNow = 4190;
  J.copyFromPrevDetail(cur2, src);
  assert.equal(cur2.card.answers.vwapPrice, 4170);
  src.card.answers.q1w = 'P';
  const cur3 = J.newNight('2026-10-13');
  assert.equal(J.copyFromPrevDetail(cur3, src).items[0], 'hình 3 tuần');
  assert.equal(J.copyFromPrev(J.newNight('2026-10-13'), src), 3);   // bản cũ vẫn trả về số mục
});

test('mục 10 · giờ FOMC lấy từ time.js: 01:00 mùa hè, 02:00 mùa đông', () => {
  const f = (key) => time.fmtMin(time.markMin({ at: '01:00', tz: 'ET' }, key, true));
  assert.equal(f('2026-10-13'), '01:00'); assert.equal(f('2026-11-03'), '02:00');
});
