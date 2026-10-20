'use strict';
// Phán quyết: một mã mỗi ca + CHỜ + ENTRY
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, go, run, trade, closed, vn, ANS_BUY, ANS_NONE, clone, time } = require('./helpers.js');

const first = (r) => r.reasons[0];
const BRK = (dir, edge, step2) => ({ mode: 'broken', breakout: { dir, edgeZoneId: edge || 'z2', at: '20:40', nth: 1, step1: true, step2: step2 !== false } });

test('nền A / B / C / D đều ra ENTRY', () => {
  ['A', 'B', 'C', 'D'].forEach((s) => {
    const r = go(s);
    assert.equal(r.verdict, 'ENTRY', s + ' ' + JSON.stringify(r.reasons) + JSON.stringify(r.missing));
    assert.equal(r.dotsLit, 8, s);
  });
});

// ---------- cửa sổ cấm ----------
test('NO_NEWS_WINDOW: 19:30 ±15′ khi bật', () => {
  const on = { windows: [{ id: 'w1930', kind: 'news', rank: 1, at: '19:30', tz: 'ET', minutesBefore: 15, minutesAfter: 15, on: true }] };
  const at = (hm) => run('2026-10-13', hm, mk('B', { t0: on })).reasons;
  assert.equal(at('19:15')[0], 'NO_NEWS_WINDOW');
  assert.equal(at('19:30')[0], 'NO_NEWS_WINDOW');
  assert.equal(at('19:45')[0], 'NO_NEWS_WINDOW');
  assert.notEqual(at('19:14')[0], 'NO_NEWS_WINDOW');
  assert.notEqual(at('19:46')[0], 'NO_NEWS_WINDOW');
});
test('NO_NEWS_WINDOW: tắt cửa sổ 19:30 thì không chặn', () => {
  assert.ok(!go('B', null, '19:30').reasons.includes('NO_NEWS_WINDOW'));
});
test('NO_NEWS_WINDOW: 21:00 ±5′; 20:55 và 21:05 chặn, 20:54 và 21:06 không', () => {
  assert.equal(go('B', null, '20:55').reasons[0], 'NO_NEWS_WINDOW');
  assert.equal(go('B', null, '21:05').reasons[0], 'NO_NEWS_WINDOW');
  assert.ok(!go('B', null, '20:54').reasons.includes('NO_NEWS_WINDOW'));
  assert.ok(!go('B', null, '21:06').reasons.includes('NO_NEWS_WINDOW'));
});
test('20:25 và 20:34 không chặn (20:30 ±5′ chỉ cảnh báo)', () => {
  assert.ok(!go('B', null, '20:25').reasons.includes('NO_NEWS_WINDOW'));
  assert.ok(!go('B', null, '20:34').reasons.includes('NO_NEWS_WINDOW'));
  assert.ok(go('B', null, '20:28').warnings.includes('WARN_NYSE'));
  assert.ok(!go('B', null, '20:40').warnings.includes('WARN_NYSE'));
});
test('NO_NEWS_WINDOW mùa đông dịch +1h: 22:00 ±5′', () => {
  assert.equal(go('B', null, '22:00', '2026-11-10').reasons[0], 'NO_NEWS_WINDOW');
  assert.ok(!go('B', null, '21:00', '2026-11-10').reasons.includes('NO_NEWS_WINDOW'));
});
test('DIS_LONGEST_BAR tới phút tròn kế tiếp + 3', () => {
  const now = vn('2026-10-13', '21:17'); // 21:17:00 → phút tròn kế tiếp 21:18, +3 = 21:21
  const until = time.longestBarUntil(now.getTime() + 30000);
  assert.equal(until, vn('2026-10-13', '21:21').getTime());
  const n = (hm) => run('2026-10-13', hm, mk('B', { regime: { mode: 'balanced', longestBarUntil: until } }));
  assert.equal(n('21:20').reasons[0], 'DIS_LONGEST_BAR');
  assert.ok(!n('21:21').reasons.includes('DIS_LONGEST_BAR'));
});

// ---------- ngược bias ----------
test('NO_COUNTER_BIAS_SCENARIO: bias ghi đè ngược regimeDir cho A', () => {
  const r = go('A', (n) => { n.card.bias = { override: 'BUY', reason: 'thử' }; });
  assert.deepEqual(r.reasons, ['NO_COUNTER_BIAS_SCENARIO']);
});
test('NO_COUNTER_BIAS_SCENARIO: C ngược bias (fade đỉnh khi bias BUY)', () => {
  const r = go('C', { setup: { zoneId: 'z2', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } });
  assert.equal(first(r), 'NO_COUNTER_BIAS_SCENARIO');
});
test('NO_COUNTER_BIAS_ZONE: B sell ngược bias BUY tại VWAP tuần', () => {
  const r = go('B', { setup: { side: 'sell', calc: { entry: 4175.0, sl: 4177.4, tp: 4167.8 } } });
  assert.deepEqual(r.reasons, ['NO_COUNTER_BIAS_ZONE']);
});
test('NO_COUNTER_BIAS_ZONE: single print sai phía (sell cần cờ phía trên)', () => {
  const r = go('B', { zones: [{ id: 'z1', type: 'sp', price: 4175, side: 'lower' }, { id: 'z2', type: 'valEu', price: 4170 }, { id: 'z3', type: 'vahEu', price: 4190 }],
    setup: { side: 'sell', counterBiasReason: 'sp cũ', calc: { entry: 4175.0, sl: 4177.4, tp: 4170.2 } } });
  assert.equal(first(r), 'NO_COUNTER_BIAS_ZONE');
});
test('B sell ngược bias BUY tại High hôm qua cờ tail ⇒ ENTRY, 2R, cỡ ½', () => {
  const r = go('B', { answers: Object.assign(clone(ANS_BUY), { q2top: 'tail' }),
    zones: [{ id: 'z1', type: 'highY', price: 4190 }, { id: 'z2', type: 'vahEu', price: 4196 }, { id: 'z3', type: 'valEu', price: 4170 }],
    setup: { side: 'sell', counterBiasReason: 'tail thật ở High', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } });
  assert.equal(r.verdict, 'ENTRY', JSON.stringify(r.reasons) + JSON.stringify(r.missing));
  assert.equal(r.calc.tpSuggested, 4184.2);
  assert.equal(r.calc.rr, 2);
  assert.deepEqual(r.half.reasons, ['COUNTER_BIAS']);
  assert.equal(r.exempt9, true);
});
test('B ngược bias nhưng thiếu lý do ⇒ CHỜ (WAIT_COUNTER_REASON)', () => {
  const r = go('B', { answers: Object.assign(clone(ANS_BUY), { q2top: 'tail' }),
    zones: [{ id: 'z1', type: 'highY', price: 4190 }, { id: 'z2', type: 'vahEu', price: 4196 }, { id: 'z3', type: 'valEu', price: 4170 }],
    setup: { side: 'sell', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } });
  assert.equal(r.verdict, 'WAIT');
  assert.ok(r.missing.includes('WAIT_COUNTER_REASON'));
});
test('High hôm qua không có tail thật ⇒ ngược bias không được', () => {
  const r = go('B', { answers: Object.assign(clone(ANS_BUY), { q2top: 'bait' }),
    zones: [{ id: 'z1', type: 'highY', price: 4190 }, { id: 'z2', type: 'vahEu', price: 4196 }, { id: 'z3', type: 'valEu', price: 4170 }],
    setup: { side: 'sell', counterBiasReason: 'x', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } });
  assert.equal(first(r), 'NO_COUNTER_BIAS_ZONE');
});

// ---------- vùng ----------
test('NO_ZONE_3RD: đã 2 lệnh cùng vùng (kể cả phá luật), không kể luyện mắt', () => {
  const two = [trade({ zoneId: 'z1' }), trade({ zoneId: 'z1', flags: ['RULE_BREAK'] })];
  assert.equal(first(go('B', { trades: two })), 'NO_ZONE_3RD');
  assert.equal(go('B', { trades: [trade({ zoneId: 'z1' })] }).verdict, 'ENTRY'); // lần thứ 2 vẫn được
  assert.equal(go('B', { trades: [trade({ zoneId: 'z1' }), trade({ zoneId: 'z1', flags: ['paper'] })] }).verdict, 'ENTRY');
  assert.equal(go('B', { trades: [trade({ zoneId: 'z9' }), trade({ zoneId: 'z9' })] }).verdict, 'ENTRY');
});
test('NO_BANNED_ZONE: B tại HVN ngày, LVN, HVN 3 tuần', () => {
  ['hvnDay', 'lvn', 'hvn3w'].forEach((type) => {
    const r = go('B', { zones: [{ id: 'z1', type, price: 4175 }, { id: 'z2', type: 'valEu', price: 4175.5 }, { id: 'z3', type: 'vahEu', price: 4184 }] });
    assert.equal(first(r), 'NO_BANNED_ZONE', type);
  });
});
test('HVN ngày: A, D vẫn được (cờ noB chỉ chặn B)', () => {
  const r = go('A', { zones: [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnDay', price: 4195 }, { id: 'z3', type: 'valEu', price: 4185 }] });
  assert.equal(r.verdict, 'ENTRY');
});
test('NO_MID_RANGE: B tại VWAP giữa range khi cân bằng', () => {
  const r = go('B', { zones: [{ id: 'z1', type: 'vwapW', price: 4180 }, { id: 'z2', type: 'valEu', price: 4170 }, { id: 'z3', type: 'vahEu', price: 4190 }],
    setup: { calc: { entry: 4181.0, sl: 4178.7, tp: 4187.9 } } });
  assert.equal(first(r), 'NO_MID_RANGE');
});
test('B tại vùng hạng 1 trùng cạnh (cách ≤ 1 giá) ⇒ qua QĐ-1', () => {
  assert.equal(go('B').verdict, 'ENTRY'); // vwapW 4175 / VAL Âu 4175,5
});
test('NO_PENDING_ACCEPT: C tại cạnh vừa phá khi pending; C tại cạnh khác ⇒ qua', () => {
  const pend = { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z1', at: '20:40', step1: true, step2: false } };
  const r = go('C', { answers: clone(ANS_NONE), regime: pend });
  assert.equal(first(r), 'NO_PENDING_ACCEPT');
  const r2 = go('C', { answers: clone(ANS_NONE), regime: pend, setup: { zoneId: 'z2', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } });
  assert.ok(!r2.reasons.includes('NO_PENDING_ACCEPT'));
  assert.equal(r2.verdict, 'ENTRY', JSON.stringify(r2.reasons));
});
test('NO_B_RANK: B buy cùng bias tại Low hôm qua khi cân bằng', () => {
  const r = go('B', { zones: [{ id: 'z1', type: 'lowY', price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }] });
  assert.deepEqual(r.reasons, ['NO_B_RANK']);
});
test('NO_B_RANK: B tại VAH Âu khi broken (cạnh chỉ có giá trị khi cân bằng)', () => {
  const r = go('B', { zones: [{ id: 'z1', type: 'vahEu', price: 4175 }, { id: 'z2', type: 'valEu', price: 4160 }, { id: 'z3', type: 'vwapW', price: 4190 }],
    regime: BRK('up', 'z2') });
  assert.equal(first(r), 'NO_B_RANK');
});
test('NO_FIGHT_BREAK: B ngược chiều phá tại hạng 2; tại VWAP tuần cùng bias, khác cạnh phá ⇒ qua', () => {
  const zones = [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'hvnW', price: 4176 }, { id: 'z3', type: 'valEu', price: 4160 }, { id: 'z4', type: 'vahEu', price: 4184 }];
  const reg = BRK('down', 'z3');
  assert.deepEqual(go('B', { zones, regime: reg, setup: { zoneId: 'z2' } }).reasons, ['NO_FIGHT_BREAK']);
  const ok = go('B', { zones, regime: reg, setup: { zoneId: 'z1' } });
  assert.equal(ok.verdict, 'ENTRY', JSON.stringify(ok.reasons) + JSON.stringify(ok.missing));
});
test('B cùng chiều phá: được', () => {
  const zones = [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4160 }, { id: 'z3', type: 'vahEu', price: 4190 }];
  assert.equal(go('B', { zones, regime: BRK('up', 'z3') }).verdict, 'ENTRY');
});
test('QĐ-4: B ngược chiều phá nhưng ngược bias ⇒ không được', () => {
  const zones = [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'valEu', price: 4160 }, { id: 'z3', type: 'vahEu', price: 4190 }];
  const r = go('B', { zones, regime: BRK('up', 'z3'), setup: { side: 'sell', counterBiasReason: 'x', calc: { entry: 4175, sl: 4177.4, tp: 4170.2 } } });
  assert.deepEqual(r.reasons, ['NO_COUNTER_BIAS_ZONE', 'NO_FIGHT_BREAK']);   // khóa thứ tự luật (REVIEW-2 mục 16)
});

// ---------- C4 – C7 ----------
test('NO_BUBBLE_AGAINST: ngược phe còn giữ; với B cả ngược phe đã vỡ', () => {
  assert.equal(first(go('A', { setup: { c4: 'oppHold', c4num: 103 } })), 'NO_BUBBLE_AGAINST');
  assert.equal(go('A', { setup: { c4: 'oppBroken' } }).verdict, 'ENTRY');
  assert.equal(first(go('B', { setup: { c4: 'oppBroken' } })), 'NO_BUBBLE_AGAINST');
});
test('B: bong bóng "không có" ⇒ CHỜ', () => {
  const r = go('B', { setup: { c4: 'none' } });
  assert.equal(r.verdict, 'WAIT');
  assert.equal(r.missing[0], 'WAIT_C4_SAME');
});
test('NO_UNCLEAR từ C4, B1, B2, B3', () => {
  assert.equal(first(go('B', { setup: { c4: 'unclear' } })), 'NO_UNCLEAR');
  assert.equal(first(go('A', { setup: { b1: 'unclear' } })), 'NO_UNCLEAR');
  assert.equal(first(go('B', { setup: { b2: 'unclear' } })), 'NO_UNCLEAR');
  assert.equal(first(go('A', { setup: { b3: 'unclear' } })), 'NO_UNCLEAR');
  assert.equal(go('A', { setup: { c4: 'unclear', b1: 'unclear', b3: 'unclear' } }).reasons.filter((c) => c === 'NO_UNCLEAR').length, 1);
});
test('NO_BACK (từ 3 giá); C5 "hơn 1" ⇒ CHỜ chờ hồi về cạnh', () => {
  assert.equal(first(go('A', { setup: { c5: 'far' } })), 'NO_BACK');
  const r = go('A', { setup: { c5: 'mid' } });
  assert.equal(r.verdict, 'WAIT'); assert.equal(r.missing[0], 'WAIT_C5_BACK');
});
test('NO_MOMENTUM (tăng dần); B lẫn lộn ⇒ CHỜ', () => {
  assert.equal(first(go('B', { setup: { b2: 'up' } })), 'NO_MOMENTUM');
  const r = go('B', { setup: { b2: 'mixed' } });
  assert.equal(r.verdict, 'WAIT'); assert.equal(r.missing[0], 'WAIT_B2_MIXED');
});
test('NO_DMA_SLOPE (B)', () => assert.equal(first(go('B', { setup: { c7: { dma: 'sloped' } } })), 'NO_DMA_SLOPE'));
test('NO_D_NO_MOVE (4,9 giá); 5 giá thì qua', () => {
  assert.equal(first(go('D', { setup: { c7: { moveSize: 4.9, deep: 'no' } } })), 'NO_D_NO_MOVE');
  assert.equal(go('D', { setup: { c7: { moveSize: 5, deep: 'no' } } }).verdict, 'ENTRY');
});
test('NO_D_DEEP (hồi quá 70 %)', () => assert.equal(first(go('D', { setup: { c7: { moveSize: 8, deep: 'yes' } } })), 'NO_D_DEEP'));
test('NO_V_PULLBACK', () => assert.equal(first(go('A', { setup: { b1: 'V' } })), 'NO_V_PULLBACK'));
test('B3 "chưa" ⇒ CHỜ', () => {
  const r = go('C', { setup: { b3: 'not' } });
  assert.equal(r.verdict, 'WAIT'); assert.equal(r.missing[0], 'WAIT_B3_NOT');
});

// ---------- SL / R:R / TP ----------
test('NO_SL_POS', () => assert.deepEqual(go('A', { setup: { slPos: 'wrong' } }).reasons, ['NO_SL_POS']));
test('B5 "chưa chắc" ⇒ CHỜ', () => assert.equal(go('A', { setup: { slPos: 'unsure' } }).missing[0], 'WAIT_B5'));
test('NO_SL_FLOOR: SL 2,4 < nến 3,3', () => assert.deepEqual(go('A', { setup: { c6: 3.3 } }).reasons, ['NO_SL_FLOOR']));
test('NO_SL_FLOOR: SL đúng bằng nến thì qua', () => assert.equal(go('A', { setup: { c6: 2.4 } }).verdict, 'ENTRY'));
test('NO_SL_CAP: SL 4,1 giá; 4,0 thì qua', () => {
  assert.equal(go('A', { setup: { calc: { entry: 4193, sl: 4197.1, tp: 4180 } } }).reasons[0], 'NO_SL_CAP');
  assert.equal(go('A', { setup: { calc: { entry: 4193, sl: 4197.0, tp: 4185 } } }).verdict, 'ENTRY');
});
test('NO_RR: R:R dưới 1:2', () => assert.deepEqual(go('A', { setup: { calc: { entry: 4193, sl: 4195.4, tp: 4189 } } }).reasons, ['NO_RR']));
test('NO_RR: vùng kế tiếp cho R:R < 1:2', () => {
  const r = go('A', { zones: [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4189 }],
    setup: { calc: { entry: 4193, sl: 4195.4, tp: 4189 } } });
  assert.deepEqual(r.reasons, ['NO_RR']);
});
test('NO_SL_SIDE: sell mà SL nằm dưới giá vào', () => {
  const r = go('A', { setup: { calc: { entry: 4193, sl: 4190.6, tp: 4185.8 } } });
  assert.ok(r.reasons.includes('NO_SL_SIDE'));
});
test('NO_TP_PAST_ZONE: TP vượt vùng kế tiếp quá 0,5 giá', () => {
  assert.deepEqual(go('A', { setup: { calc: { entry: 4193, sl: 4195.4, tp: 4180 } } }).reasons, ['NO_TP_PAST_ZONE']);
  assert.equal(go('A', { setup: { calc: { entry: 4193, sl: 4195.4, tp: 4184.5 } } }).verdict, 'ENTRY'); // vượt đúng 0,5
});
test('TP trống ⇒ dùng TP gợi ý; gợi ý kéo về vùng kế tiếp nếu gần hơn', () => {
  const r = go('A', { setup: { calc: { entry: 4193, sl: 4195.4, tp: null } } });
  assert.equal(r.calc.tpSuggested, 4185.8); assert.equal(r.calc.tpUsed, 4185.8); assert.equal(r.verdict, 'ENTRY');
  const near = go('A', { zones: [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4186 }], setup: { calc: { entry: 4193, sl: 4195.4, tp: null } } });
  assert.equal(near.calc.tpSuggested, 4186);
});
test('R:R luôn được xét dù đã có mã NO khác (QĐ-20)', () => {
  const r = go('A', { setup: { b1: 'V', calc: { entry: 4193, sl: 4195.4, tp: 4189 } } });
  assert.equal(r.reasons[0], 'NO_V_PULLBACK');
  assert.ok(r.reasons.includes('NO_RR'));
});

// ---------- khóa, CHỜ, ENTRY ----------
test('lệnh mở ⇒ tầng 3 khóa (LOCKED)', () => {
  const r = go('B', (n) => { n.open = { tradeId: 't1', status: 'filled' }; n.trades = [trade({ id: 't1', entry: 4177 })]; });
  assert.equal(r.verdict, 'LOCKED'); assert.equal(r.locks.tier3, 'OPEN_TRADE'); assert.deepEqual(r.reasons, ['LOCK_OPEN_TRADE']);
});
test('lệnh mở ở đêm trước vẫn khóa đêm mới (engine nhận cả nights)', () => {
  const prev = mk('B', (n) => { n.open = { tradeId: 't9', status: 'filled' }; n.trades = [trade({ id: 't9', entry: 4177 })]; });
  const r = run('2026-10-14', '21:30', mk('B'), null, { '2026-10-13': prev });
  assert.equal(r.verdict, 'LOCKED'); assert.equal(r.open.nightKey, '2026-10-13');
});
test('tầng 3 khóa khi chưa chốt thẻ / bias CHỜ', () => {
  assert.equal(go('B', (n) => { n.card.lockedAt = null; }).locks.tier3, 'NO_CARD');
  assert.equal(go('B', { answers: { q1: 'D', q5: 'above', vwapW: 'near', q6: 'yes' } }).locks.tier3, 'BIAS_WAIT');
  assert.equal(go('B').locks.tier3, null);
});
test('CHỜ: missing đúng thứ tự nên làm', () => {
  const r = go('B', { setup: { c4: null, c5: null, c6: null, c7: {}, b1: null, b2: null, b3: null, slPos: null, calc: {} } });
  assert.equal(r.verdict, 'WAIT');
  assert.deepEqual(r.missing, ['WAIT_C4', 'WAIT_C5', 'WAIT_C6', 'WAIT_C7_DMA', 'WAIT_B1', 'WAIT_B2', 'WAIT_B3', 'WAIT_CALC', 'WAIT_B5']);
});
test('CHỜ: chưa chọn kịch bản; chưa chọn vùng', () => {
  assert.deepEqual(go('B', { setup: { scenario: null } }).missing, ['WAIT_SCENARIO']);
  assert.equal(go('B', { setup: { zoneId: null } }).missing[0], 'WAIT_ZONE');
});
test('ENTRY: số liệu, cỡ lệnh, half', () => {
  const r = go('A');
  assert.equal(r.verdict, 'ENTRY');
  assert.equal(r.calc.slDist, 2.4); assert.equal(r.calc.rr, 3.0);
  assert.deepEqual(r.half.reasons, []);
  const big = run('2026-10-13', '21:30', mk('A'), { capital: 5000, riskPct: 2 });
  assert.equal(big.calc.size, 4); // 100 $ / (2,4 × 10 $) = 4,17 ⇒ 4
  const half = run('2026-10-13', '20:10', mk('A'), { capital: 5000, riskPct: 2 });
  assert.deepEqual(half.half.reasons, ['BEFORE_2030']); assert.equal(half.calc.size, 2);
});
test('NEWS_DAY và BIAS_NONE vào half.reasons, chỉ nhân ½ một lần', () => {
  const r = go('C', { answers: clone(ANS_NONE), t0: { newsDay: true }, setup: { zoneId: 'z2', calc: { entry: 4189.0, sl: 4191.4, tp: 4184.2 } } }, '20:10');
  assert.deepEqual(r.half.reasons, ['BIAS_NONE', 'SCENARIO_C', 'NEWS_DAY', 'BEFORE_2030']);
  assert.equal(r.verdict, 'ENTRY');
});
test('chế độ chỉ xem (t0.alert = false) ⇒ ENTRY mang cờ paper', () => {
  const r = go('A', { t0: { alert: false } });
  assert.equal(r.verdict, 'ENTRY'); assert.equal(r.paper, true);
});
test('cảnh báo: dưới 3 vùng; trước 20:30', () => {
  assert.ok(go('A', { zones: [{ id: 'z2', type: 'hvnW', price: 4195 }, { id: 'z3', type: 'valEu', price: 4185 }] }).warnings.includes('WARN_FEW_ZONES'));
  assert.ok(go('A', null, '20:00').warnings.includes('WARN_BEFORE_2030'));
});
test('mọi mã trong RULE_ORDER đều có chữ trong content', () => {
  const C = require('../js/content.js'); const R = require('../js/rules.js');
  R.RULE_ORDER.filter((c) => /^(OFF|LOCK|NO|DIS|WAIT)_/.test(c)).forEach((c) => assert.ok(C.codes[c] && C.codes[c].text, c));
});
