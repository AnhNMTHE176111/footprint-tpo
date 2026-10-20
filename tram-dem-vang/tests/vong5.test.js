'use strict';
// Vòng 5: B5 tự kiểm (QĐ-25), Kèo mới giữ C1–C3 + C6, gõ nhanh vùng, kiểm giá nhập, không còn chữ thô "⟦"
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const J = require('../js/journal.js');
const R = require('../js/rules.js');
const { go, mk, run } = require('./helpers.js');

// ---------- B5 tự kiểm ----------
// Fixture A: bán ở vùng hvnW 4195, SL 4195,4 (qua mép + 0,3 = 4195,3) ⇒ đúng; fixture hiện có đặt slPos tay, ở đây bỏ đi để máy tự kiểm
const dropSlPos = (n) => { delete n.setup.slPos; };
const withCalc = (scen, calc, extra) => mk(scen, (n) => { dropSlPos(n); Object.assign(n.setup.calc, calc); if (extra) Object.assign(n.setup, extra); });

test('B5 tự kiểm A: SL qua mép xa của vùng + 0,3 ⇒ ENTRY; thiếu 0,1 ⇒ NO_SL_POS', () => {
  assert.equal(run('2026-10-13', '21:30', withCalc('A', { sl: 4195.4 })).verdict, 'ENTRY');
  assert.equal(run('2026-10-13', '21:30', withCalc('A', { sl: 4195.3 })).verdict, 'ENTRY');     // đúng 0,3 thì qua
  const r = run('2026-10-13', '21:30', withCalc('A', { sl: 4195.2 }));
  assert.equal(r.verdict, 'NO');
  assert.ok(r.reasons.indexOf('NO_SL_POS') >= 0);
  assert.equal(r.slPos, 'wrong');
});

test('B5 tự kiểm C: buy ở vùng 4175, SL phải ≤ 4174,7', () => {
  const ok = run('2026-10-13', '21:30', withCalc('C', { sl: 4173.6 }));
  assert.equal(ok.verdict, 'ENTRY');
  const bad = run('2026-10-13', '21:30', withCalc('C', { sl: 4174.9, entry: 4177 }));
  assert.ok(bad.reasons.indexOf('NO_SL_POS') >= 0);
});

test('B5 tự kiểm B, D: cần cực trị người dùng nhập ở Canh; thiếu ⇒ CHỜ; đủ ⇒ máy kiểm SL', () => {
  const noExt = run('2026-10-13', '21:30', withCalc('B', {}));
  assert.equal(noExt.verdict, 'WAIT');
  assert.ok(noExt.missing.indexOf('WAIT_B5') >= 0);
  assert.equal(run('2026-10-13', '21:30', withCalc('B', {}, { ext: 4175 })).verdict, 'ENTRY');          // buy: SL 4174,7 ≤ 4175 − 0,3
  const bad = run('2026-10-13', '21:30', withCalc('B', {}, { ext: 4174.8 }));                          // cực trị thấp hơn ⇒ SL nằm trong cụm
  assert.ok(bad.reasons.indexOf('NO_SL_POS') >= 0);
  assert.equal(run('2026-10-13', '21:30', withCalc('D', {}, { ext: 4195 })).verdict, 'ENTRY');          // sell: SL 4195,4 ≥ 4195 + 0,3
  assert.ok(run('2026-10-13', '21:30', withCalc('D', {}, { ext: 4195.3 })).reasons.indexOf('NO_SL_POS') >= 0);
});

test('B5: dữ liệu cũ có slPos tay (right / wrong / unsure) vẫn được tôn trọng; tám chấm chấm theo slPos hiệu lực', () => {
  const r = go('A');                                                     // fixture có slPos 'right'
  assert.equal(r.verdict, 'ENTRY'); assert.equal(r.dots[7], true);
  assert.equal(go('A', { setup: { slPos: 'wrong' } }).reasons[0], 'NO_SL_POS');
  const auto = run('2026-10-13', '21:30', withCalc('A', { sl: 4195.4 }));
  assert.equal(auto.dots[7], true);
  const wrong = run('2026-10-13', '21:30', withCalc('A', { sl: 4195.2 }));
  assert.equal(wrong.dots[7], false);
});

test('B5: sổ ghi slPos hiệu lực (kể cả tự kiểm)', () => {
  const n = withCalc('A', { sl: 4195.4 });
  const res = run('2026-10-13', '21:30', n);
  const t = J.createTrade(n, res, { kind: 'market', price: 4193, nowMs: 0, nowMin: 21 * 60 + 30 });
  assert.equal(t.slPos, 'right');
});

// ---------- Kèo mới ----------
test('Kèo mới giữ kịch bản, vùng, hướng của B và C6; xóa các câu quan sát', () => {
  const s0 = { scenario: 'B', zoneId: 'z1', side: 'buy', c6: 2, c4: 'same', c4num: -49, c5: 'near', c7: { dma: 'flat' }, b1: 'U', b2: 'down', b3: 'ok', ext: 4175, slPos: 'right', calc: { entry: 1 }, counterBiasReason: 'x', updatedAt: 5 };
  assert.deepEqual(J.newSetupKeep(s0), { scenario: 'B', zoneId: 'z1', side: 'buy', c6: 2 });
  assert.deepEqual(J.newSetupKeep(null), {});
});

// ---------- gõ nhanh vùng ----------
test('gõ nhanh vùng: mã + giá, khoảng giá, phía u / l, mục lạ báo lại', () => {
  const q = J.parseQuickZones('vwapw 4205, vah 4199; val 4185\nhvn 4195-4197, spu 4210, rel 4170, xx 5, high');
  assert.deepEqual(q.zones.map((z) => z.type), ['vwapW', 'vahEu', 'valEu', 'hvnW', 'sp', 'rangeEdge']);
  assert.equal(q.zones[3].priceTo, 4197);
  assert.deepEqual([q.zones[4].side, q.zones[5].side], ['upper', 'lower']);
  assert.deepEqual(q.bad, ['xx 5', 'high']);
  assert.deepEqual(J.parseQuickZones('').zones, []);
  assert.equal(J.parseQuickZones('vwapw 4205,5').zones[0].price, 4205);
});

// ---------- kiểm giá nhập ----------
test('kiểm giá limit / giá khớp: quá 6 chữ số hoặc lệch quá 20 giá ⇒ chặn', () => {
  assert.equal(J.priceProblem(41824182, 4182), 'priceDigits');
  assert.equal(J.priceProblem(4210, 4182), 'priceFar');
  assert.equal(J.priceProblem(4182, 4182), null);
  assert.equal(J.priceProblem(4202, 4182), null);          // lệch đúng 20 thì qua
  assert.equal(J.priceProblem(null, 4182), null);
});

// ---------- không còn chữ thô ⟦key⟧ ----------
test('mọi khóa chữ được gọi trong js/ui và js/main.js đều tồn tại (kể cả T(a ? "x" : "y")): chạy lint:vi', () => {
  const out = execFileSync(process.execPath, [path.resolve(__dirname, '../scripts/lint-vi.mjs')], { encoding: 'utf8' });
  assert.match(out, /Kết quả: 0 lỗi/);
  assert.doesNotMatch(out, /thiếu khóa chữ/);
});
test('có đủ chữ cho mọi mã luật và mọi ô điều khiển (không ⟦⟧)', () => {
  const C = require('../js/content.js');
  R.RULE_ORDER.forEach((c) => assert.ok((C.codes[c] && C.codes[c].text) || C.halfText[c], c));
  ['c8B', 'c8D', 'b3', 'b4'].forEach((k) => assert.ok(C.controls[k].label, k));
  Object.keys(C.ui).forEach((k) => assert.ok(!/⟦/.test(C.ui[k]), k));
});
