'use strict';
// Phụ lục A của plan: 5 ca fixture (số cố định)
const test = require('node:test');
const assert = require('node:assert/strict');
const { night, card, run } = require('./helpers.js');

function a1() {
  return night({
    card: card({ q1: 'D', q1w: 'D', q2top: 'normal', q2bot: 'normal', q3: 'none', q4: 'mid', q5: 'below', q6: 'yes', vwapW: 'below' }, [
      { id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'pocCluster', price: 4195, priceTo: 4196 },
      { id: 'z3', type: 'vahEu', price: 4199 }, { id: 'z4', type: 'valEu', price: 4185 }]),
    regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '20:15', nth: 1, step1: true, step2: true } },
    setup: { scenario: 'A', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2.0, b1: 'U', b3: 'ok', slPos: 'right', calc: { entry: 4193.0, sl: 4195.4, tp: 4185.0 } }
  });
}
test('A1 · 6/10 20:24 — A sell ⇒ ENTRY, cỡ ½ (QĐ-19)', () => {
  const r = run('2026-10-06', '20:24', a1());
  assert.equal(r.bias, 'SELL');
  assert.equal(r.regime.effective, 'broken');
  assert.equal(r.regime.dir, 'down');
  assert.equal(r.verdict, 'ENTRY');
  assert.deepEqual(r.reasons, []);
  assert.equal(r.calc.slDist, 2.4);
  assert.equal(r.calc.rr, 3.33);
  assert.equal(r.calc.tpSuggested, 4185.8);
  assert.deepEqual(r.half.reasons, ['BEFORE_2030']);
  assert.equal(r.dotsLit, 8);
  assert.equal(r.enabled.A, null);
  assert.equal(r.side, 'sell');
});

function a2() {
  return night({
    card: card({ q1: 'b', q5: 'below', vwapW: 'below', q6: 'yes' }, [
      { id: 'z1', type: 'hvnW', price: 4190 }, { id: 'z2', type: 'valEu', price: 4186 }, { id: 'z3', type: 'vahEu', price: 4196 }]),
    regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z1', at: '21:17', nth: 1, step1: true, step2: true } },
    setup: { scenario: 'A', zoneId: 'z1', c4: 'oppHold', c4num: 103, c5: 'near', c6: 2.0, b1: 'V', b3: 'ok', slPos: 'right', calc: { entry: 4188.0, sl: 4190.3, tp: 4181.0 } }
  });
}
test('A2 · 12/10 21:27 — A sell ⇒ KHÔNG VÀO [NO_BUBBLE_AGAINST, NO_V_PULLBACK, NO_RR, NO_TP_PAST_ZONE] (QĐ-20)', () => {
  const r = run('2026-10-12', '21:27', a2());
  assert.equal(r.bias, 'SELL');
  assert.equal(r.verdict, 'NO');
  assert.deepEqual(r.reasons, ['NO_BUBBLE_AGAINST', 'NO_V_PULLBACK', 'NO_RR', 'NO_TP_PAST_ZONE']);
  assert.deepEqual(r.reasons.slice(0, 2), ['NO_BUBBLE_AGAINST', 'NO_V_PULLBACK']);
  const wl = require('../js/journal.js').warnLine({ ruleCodes: r.reasons });
  assert.equal(wl, 'phạm 4.3, 4.1 và luật SL');
});

function a3(slPos) {
  return night({
    card: card({ q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' }, [
      { id: 'z1', type: 'vwapW', price: 4194.8 }, { id: 'z2', type: 'hvnDay', price: 4193 }, { id: 'z3', type: 'valEu', price: 4188 }]),
    regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '20:40', nth: 1, step1: true, step2: true } },
    setup: { scenario: 'A', zoneId: 'z2', c4: 'none', c5: 'near', c6: 3.3, b1: 'U', b3: 'ok', slPos, calc: { entry: 4192.7, sl: 4194.8, tp: 4182.7 } }
  });
}
test('A3a · 1/10 20:47 — A sell ⇒ KHÔNG VÀO [NO_SL_FLOOR, NO_TP_PAST_ZONE]', () => {
  const r = run('2026-10-01', '20:47', a3('right'));
  assert.equal(r.verdict, 'NO');
  assert.deepEqual(r.reasons, ['NO_SL_FLOOR', 'NO_TP_PAST_ZONE']);
  assert.equal(r.calc.slDist, 2.1);
});
test('A3b · 1/10 20:47 — biến thể SL sai chỗ ⇒ [NO_SL_POS, NO_SL_FLOOR, NO_TP_PAST_ZONE]', () => {
  const r = run('2026-10-01', '20:47', a3('wrong'));
  assert.deepEqual(r.reasons, ['NO_SL_POS', 'NO_SL_FLOOR', 'NO_TP_PAST_ZONE']);
});

function a4(regime) {
  return night({
    card: card({ q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' }, [
      { id: 'z1', type: 'valEu', price: 4175 }, { id: 'z2', type: 'pocCluster', price: 4175.5 },
      { id: 'z3', type: 'vahEu', price: 4184 }, { id: 'z4', type: 'lvn', price: 4172 }]),
    regime,
    setup: { scenario: 'B', zoneId: 'z2', side: 'buy', c4: 'same', c4num: -49, c5: 'near', c6: 2.0, c7: { dma: 'flat' }, b1: 'U', b2: 'down', b3: 'ok', slPos: 'right', calc: { entry: 4177.0, sl: 4174.7, tp: 4183.9 } }
  });
}
test('A4a · 13/10 20:10 — B buy cân bằng ⇒ ENTRY ½ (B_RANK2 + BEFORE_2030)', () => {
  const r = run('2026-10-13', '20:10', a4({ mode: 'balanced' }));
  assert.equal(r.bias, 'BUY');
  assert.equal(r.regime.effective, 'balanced');
  assert.equal(r.verdict, 'ENTRY');
  assert.deepEqual(r.reasons, []);
  assert.deepEqual(r.half.reasons, ['B_RANK2', 'BEFORE_2030']);
  assert.equal(r.calc.rr, 3);
  assert.equal(r.calc.tpSuggested, 4183.9);
  // vốn mặc định 2000 $ · 2 %: cỡ chuẩn 1 hợp đồng, cỡ ½ không chia được ⇒ 1 hợp đồng tối thiểu (QĐ-21)
  assert.equal(r.calc.size, 1); assert.equal(r.calc.sizeMinOne, true); assert.equal(r.calc.sizeFull, 1);
});
test('A4a với vốn 20000 $ ⇒ cỡ ½ = 8 hợp đồng (200 $ / 23 $)', () => {
  const r = run('2026-10-13', '20:10', a4({ mode: 'balanced' }), { dstShift: true, capital: 20000, riskPct: 2 });
  assert.equal(r.verdict, 'ENTRY'); assert.equal(r.calc.size, 8); assert.equal(r.calc.sizeMinOne, false);
});
test('A4a với vốn 1000 $ ⇒ cỡ chuẩn 0 ⇒ NO_SIZE_ZERO (QĐ-21)', () => {
  const r = run('2026-10-13', '20:10', a4({ mode: 'balanced' }), { dstShift: true, capital: 1000, riskPct: 2 });
  assert.equal(r.verdict, 'NO'); assert.deepEqual(r.reasons, ['NO_SIZE_ZERO']); assert.equal(r.calc.size, 0); assert.equal(r.calc.sizeFull, 0);
});
test('A4b · biến thể broken ⇒ NO_FIGHT_BREAK', () => {
  const r = run('2026-10-13', '20:10', a4({ mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z1', at: '20:00', step1: true, step2: true } }));
  assert.equal(r.verdict, 'NO');
  assert.deepEqual(r.reasons, ['NO_FIGHT_BREAK']);
});

test('A5 · 5/10 19:25 — B buy ⇒ CHỜ, missing[0] = WAIT_B2_MIXED', () => {
  const n = night({
    card: card({ q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' }, [
      { id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'valEu', price: 4182 }, { id: 'z3', type: 'vahEu', price: 4192 }]),
    regime: { mode: 'balanced' },
    setup: { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c4num: 25, c5: 'near', c6: 2.5, c7: { dma: 'flat' }, b1: 'U', b2: 'mixed', b3: 'ok', slPos: 'right', calc: { entry: 4183.0, sl: 4180.5, tp: 4190.5 } }
  });
  const r = run('2026-10-05', '19:25', n);
  assert.equal(r.verdict, 'WAIT');
  assert.deepEqual(r.reasons, []);
  assert.equal(r.missing[0], 'WAIT_B2_MIXED');
  assert.deepEqual(r.half.reasons, ['BEFORE_2030']);
});
module.exports = { a1, a2, a3, a4 };
