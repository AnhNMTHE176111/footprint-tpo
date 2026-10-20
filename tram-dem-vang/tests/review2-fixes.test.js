'use strict';
// Test cho từng mục đã sửa ở vòng 3 (REVIEW-2 / USER-TEST-2). Vốn mặc định 2000 $ · 2 % (tests/helpers.js).
const test = require('node:test');
const assert = require('node:assert/strict');
const { mk, go, run, closed, trade, engine, time } = require('./helpers.js');
const J = require('../js/journal.js');
const C = require('../js/content.js');
const S = require('../js/store.js');
const { night, card } = require('./helpers.js');
function a1() {   // Phụ lục A, ca A1 (6/10 20:24), giống tests/fixtures.test.js
  return night({
    card: card({ q1: 'D', q1w: 'D', q2top: 'normal', q2bot: 'normal', q3: 'none', q4: 'mid', q5: 'below', q6: 'yes', vwapW: 'below' }, [
      { id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'pocCluster', price: 4195, priceTo: 4196 },
      { id: 'z3', type: 'vahEu', price: 4199 }, { id: 'z4', type: 'valEu', price: 4185 }]),
    regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '20:15', nth: 1, step1: true, step2: true } },
    setup: { scenario: 'A', zoneId: 'z2', c4: 'none', c5: 'near', c6: 2.0, b1: 'U', b3: 'ok', slPos: 'right', calc: { entry: 4193.0, sl: 4195.4, tp: 4185.0 } }
  });
}

const NOWMS = Date.UTC(2026, 9, 13, 14, 30);

// ---------- mục 1 · QĐ-21 cỡ lệnh ----------
test('mục 1 · A1 6/10 20:24 với vốn 2000 $ ⇒ ENTRY 1 hợp đồng (cỡ ½ không chia được)', () => {
  const r = run('2026-10-06', '20:24', a1());
  assert.equal(r.verdict, 'ENTRY');
  assert.equal(r.calc.sizeFull, 1); assert.equal(r.calc.size, 1); assert.equal(r.calc.sizeMinOne, true);
  assert.deepEqual(r.half.reasons, ['BEFORE_2030']);
});
test('mục 1 · mặc định 2000 $: C, kèo trước 20:30, ngày có tin đều ra 1 hợp đồng, không phải KHÔNG VÀO', () => {
  const c = go('C'); assert.equal(c.verdict, 'ENTRY'); assert.equal(c.calc.size, 1); assert.equal(c.calc.sizeMinOne, true);
  const early = go('B', null, '20:10'); assert.equal(early.verdict, 'ENTRY'); assert.equal(early.calc.size, 1);
  const news = go('A', { t0: { newsDay: true } }); assert.equal(news.verdict, 'ENTRY'); assert.equal(news.calc.size, 1);
});
test('mục 1 · cỡ chuẩn dưới 1 hợp đồng ⇒ NO_SIZE_ZERO kèm SL tối đa; vốn 1000 $, SL 2,4', () => {
  const r = run('2026-10-13', '21:30', mk('A'), { dstShift: true, capital: 1000, riskPct: 2 });
  assert.equal(r.verdict, 'NO'); assert.deepEqual(r.reasons, ['NO_SIZE_ZERO']);
  assert.equal(r.calc.sizeFull, 0); assert.equal(r.calc.maxSl, 2);
  assert.match(C.fill(C.codes.NO_SIZE_ZERO.text, { cap: 1000, pct: 2, max: '2,0' }), /vốn 1000 \$ · rủi ro 2 %, SL tối đa 2,0 giá/);
  assert.ok(!/giảm SL/.test(C.codes.NO_SIZE_ZERO.text));
});
test('mục 1 · vốn 2000 $ · 2 %: SL tối đa 4 giá, rủi ro chuẩn 40 $', () => {
  const r = go('A'); assert.equal(r.calc.maxSl, 4); assert.equal(r.calc.fullUsd, 40);
});

// ---------- mục 2 · C khi chờ công nhận ----------
const PEND = { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', at: '20:40', nth: 1, step1: true, step2: false } };
function cAt(type, zones) {
  const zs = zones || [{ id: 'z1', type, price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'valEu', price: 4160 }];
  return go('C', { zones: zs, regime: PEND, setup: { zoneId: 'z1', calc: { entry: 4176, sl: 4173.6, tp: 4180.8 } } });
}
test('mục 2 · C pending tại single print / poor low / VWAP / naked POC / LVN / HVN ⇒ NO_C_NOT_EDGE', () => {
  ['sp', 'poorLow', 'poorHigh', 'vwapW', 'nakedPoc', 'lvn', 'hvn3w', 'hvnDay'].forEach((type) => {
    const zones = [{ id: 'z1', type, price: 4175, side: 'lower' }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'valEu', price: 4160 }];
    const r = cAt(type, zones);
    assert.equal(r.regime.effective, 'pending', type);
    assert.equal(r.verdict, 'NO', type);
    assert.ok(r.reasons.includes('NO_C_NOT_EDGE'), type + ' ' + JSON.stringify(r.reasons));
  });
});
test('mục 2 · C pending tại VAL Âu khác cạnh vừa phá ⇒ qua; tại cạnh vừa phá ⇒ NO_PENDING_ACCEPT', () => {
  const ok = cAt('valEu'); assert.equal(ok.verdict, 'ENTRY', JSON.stringify([ok.reasons, ok.missing]));
  const bad = go('C', { regime: { mode: 'broken', breakout: Object.assign({}, PEND.breakout, { edgeZoneId: 'z1' }) } });
  assert.ok(bad.reasons.includes('NO_PENDING_ACCEPT'));
});
test('mục 2 · C cân bằng ở vùng không phải cạnh ⇒ NO_C_NOT_EDGE (thay NO_MID_RANGE)', () => {
  const r = go('C', { zones: [{ id: 'z1', type: 'vwapW', price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }] });
  assert.ok(r.reasons.includes('NO_C_NOT_EDGE')); assert.ok(!r.reasons.includes('NO_MID_RANGE'));
  assert.equal(C.codes.NO_C_NOT_EDGE.htRef, '5·C');
  assert.equal(C.codes.NO_C_NOT_EDGE.ctl, 'c3');
});
test('mục 2 · C ở cạnh ngoài (High / Low hôm qua) vẫn được', () => {
  const r = go('C', { zones: [{ id: 'z1', type: 'lowY', price: 4175 }, { id: 'z2', type: 'vahEu', price: 4190 }, { id: 'z3', type: 'vwapW', price: 4182 }] });
  assert.ok(!r.reasons.includes('NO_C_NOT_EDGE'), JSON.stringify(r.reasons));
});
test('mục 13 · A, D thiếu hướng chế độ ⇒ CHỜ WAIT_REGIME_DIR (về tầng 2), không phải "Chọn hướng"', () => {
  const r = go('A', { regime: { mode: 'thin', thinDir: null } });
  assert.equal(r.verdict, 'WAIT'); assert.ok(r.missing.includes('WAIT_REGIME_DIR')); assert.ok(!r.missing.includes('WAIT_SIDE'));
  const d = go('D', { regime: { mode: 'thin', thinDir: null } });
  assert.ok(d.missing.includes('WAIT_REGIME_DIR'));
  assert.ok(go('B', { setup: { side: null } }).missing.includes('WAIT_SIDE'));
});

// ---------- mục 3 · chạm SL sau khi dời hòa ----------
function openNight(beDone) {
  const n = J.newNight('2026-10-13');
  n.trades = [{ id: 't1', time: '21:00', side: 'sell', scenario: 'A', mode: 'broken', entry: 4193, sl: 4195.4, tp: 4185.8, size: 1, flags: [], ruleCodes: [], tests: {}, exit: null, r: null }];
  n.open = { tradeId: 't1', status: 'filled', beDone: beDone, beAt: null, outsideZoneBar: true, limitPrice: null };
  return n;
}
test('mục 3 · dời be rồi "Chạm SL" ⇒ giá thoát mặc định = giá vào, R = 0, không cộng chuỗi SL', () => {
  const n = openNight(true);
  const t = J.closeTrade(n, { kind: 'SL', price: null, nowMs: NOWMS, nowMin: 1300 });
  assert.equal(t.exit.beStop, true); assert.equal(t.exit.price, 4193); assert.equal(t.r, 0);
  assert.equal(engine.countTrades(n).slStreak, 0);
});
test('mục 3 · "Chạm SL" khi CHƯA be ⇒ −1R, cộng chuỗi', () => {
  const n = openNight(false);
  const t = J.closeTrade(n, { kind: 'SL', price: null, nowMs: NOWMS, nowMin: 1300 });
  assert.equal(t.exit.beStop, undefined); assert.equal(t.r, -1);
  assert.equal(engine.countTrades(n).slStreak, 1);
});
test('mục 3 · "Về hòa" trượt giá R trong [−0,2; +0,2] không cộng chuỗi; R ≤ −0,5 thì cộng', () => {
  const be = (r) => closed('BE', r);
  assert.equal(engine.countTrades({ trades: [be(-0.04)] }).slStreak, 0);
  assert.equal(engine.countTrades({ trades: [closed('SL', -1), closed('SL', -1), be(-0.2)] }).slStreak, 0);
  assert.equal(engine.countTrades({ trades: [closed('SL', -1), be(-0.5)] }).slStreak, 2);
  const sb = closed('SL', 0); sb.exit.beStop = true;
  assert.equal(engine.countTrades({ trades: [closed('SL', -1), closed('SL', -1), sb] }).slStreak, 0);
  assert.equal(engine.isSLTrade(closed('SL', null)), true);
});
test('mục 3 · ba lần dời be rồi chạm SL không TẮT MÁY oan', () => {
  const sb = () => { const t = closed('SL', 0); t.exit.beStop = true; return t; };
  const r = go('B', { trades: [sb(), sb(), sb()] });
  assert.equal(r.counts.slStreak, 0); assert.notEqual(r.verdict, 'OFF');
});

// ---------- mục 4 · TẮT MÁY + "Tôi vẫn vào" giữ mã luật thật ----------
test('mục 4 · tắt máy (2 lệnh phá luật) + kèo A có V ⇒ lệnh ghi cả OFF_RULE_BREAKS lẫn NO_V_PULLBACK; dòng ⚠ có 4.1', () => {
  const rb = () => trade({ flags: ['RULE_BREAK'], exit: { kind: 'TP' }, r: 1 });
  const n = mk('A', { setup: { b1: 'V' }, trades: [rb(), rb()] });
  const res = run('2026-10-13', '21:30', n);
  assert.equal(res.verdict, 'OFF'); assert.deepEqual(res.ruleReasons, ['NO_V_PULLBACK']);
  const t = J.createTrade(n, res, { kind: 'market', price: 4193, ruleBreak: true, nowMs: NOWMS, nowMin: 1290 });
  assert.ok(t.ruleCodes.includes('OFF_RULE_BREAKS')); assert.ok(t.ruleCodes.includes('NO_V_PULLBACK'));
  assert.match(J.warnLine(t), /4\.1/);
});
test('mục 4 · CHỜ + "Tôi vẫn vào" ghi mã CHỜ (missing)', () => {
  const n = mk('B', (x) => { delete x.setup.b2; });
  const res = run('2026-10-13', '21:30', n);
  assert.equal(res.verdict, 'WAIT');
  const t = J.createTrade(n, res, { kind: 'market', price: 4177, ruleBreak: true, nowMs: NOWMS, nowMin: 1290 });
  assert.ok(t.ruleCodes.includes('WAIT_B2'));
});

// ---------- mục 5 · nhập JSON qua nửa đêm ----------
test('mục 5 · gộp JSON: lệnh sau nửa đêm xếp theo thời gian đêm, chuỗi SL tính đúng', () => {
  const mkT = (id, tm, kind, r) => ({ id, time: tm, side: 'sell', scenario: 'A', flags: [], ruleCodes: [], tests: {}, exit: { kind, price: 0, at: tm }, r });
  const a = J.normalizeNight({ trades: [mkT('a1', '21:00', 'SL', -1)], tally: { closedAt: 1 } }, '2026-10-13');
  const b = J.normalizeNight({ trades: [mkT('b2', '23:50', 'SL', -1), mkT('b3', '00:20', 'TP', 3)], tally: { closedAt: 0 } }, '2026-10-13');
  const m = S.mergeNight(a, b).night;
  assert.deepEqual(m.trades.map((t) => t.id), ['a1', 'b2', 'b3']);
  assert.equal(engine.countTrades(m).slStreak, 0);
});

// ---------- mục 6 · chữ có giờ theo mùa ----------
test('mục 6 · chữ có giờ: mùa hè 20:30 / 19:20; ngày 02/11/2026 (mùa đông Mỹ) ra 21:30 / 20:20', () => {
  const summer = time.textVars('2026-10-13', true), winter = time.textVars('2026-11-02', true), off = time.textVars('2026-11-02', false);
  assert.deepEqual([summer.nyse, summer.comex, summer.fomcFlat], ['20:30', '19:20', '00:45']);
  assert.deepEqual([winter.nyse, winter.comex, winter.real1, winter.real2, winter.fomcFlat], ['21:30', '20:20', '21:20', '22:30', '01:45']);
  assert.equal(off.nyse, '20:30');
  const fill = (s) => C.fill(s, winter);
  assert.match(fill(C.warnText.WARN_BEFORE_2030), /Trước 21:30/);
  assert.match(fill(C.halfText.BEFORE_2030), /trước 21:30/);
  assert.match(fill(C.qd['QĐ-19']), /Trước 21:30/);
  assert.match(fill(C.codes.DIS_EARLY_BREAK.text), /18:00–20:20/);
  assert.match(fill(C.ui.t1CardHelp), /Sau 20:20/);
  assert.match(fill(C.ui.editAfterLock), /sau 20:20/);
  assert.match(fill(C.glossary.filter((g) => g.key === 'mo-ao')[0].def), /20:20 đến 21:30/);
  [C.warnText.WARN_BEFORE_2030, C.halfText.BEFORE_2030, C.qd['QĐ-19'], C.ui.t1CardHelp, C.ui.editAfterLock, C.ui.t0WinNote]
    .forEach((s) => assert.ok(!/20:30|19:20|00:45/.test(s), s));
  assert.ok(!/19:20|20:30/.test(C.codes.DIS_EARLY_BREAK.text));
});

// ---------- USER-TEST 5 · kế hoạch ngược bias (regex từng hỏng: ký tự lùi thay cho \b nên không bao giờ khớp) ----------
test('USER-TEST 5 · kế hoạch ngược bias: "sell ở VAH Âu" khi bias BUY ⇒ cảnh báo; buy ⇒ không; có cả hai ⇒ không', () => {
  assert.equal(J.planConflict({ plan1: 'sell ở VAH Âu' }, 'BUY'), true);
  assert.equal(J.planConflict({ plan1: 'Nếu giá hồi thì SELL tại VAH' }, 'BUY'), true);
  assert.equal(J.planConflict({ plan1: 'buy ở VAL Âu' }, 'BUY'), false);
  assert.equal(J.planConflict({ plan1: 'sell VAH', plan2: 'buy VAL' }, 'BUY'), false);
  assert.equal(J.planConflict({ plan1: 'buy ở VAL', plan2: '' }, 'SELL'), true);
  assert.equal(J.planConflict({ plan1: 'sell' }, 'KHÔNG'), false);
  assert.equal(J.planConflict({ plan1: 'buyer' }, 'SELL'), false);
});

// ---------- mục 7 · đánh số câu hỏi ----------
test('mục 7 · câu hỏi đánh số theo HT 2.1: Q1, Q1′, Q2a, Q2b, Q3, Q4, Q5, Q6; tiêu đề "Sáu câu hỏi"', () => {
  assert.deepEqual(C.questions.map((q) => q.num), ['Q1', 'Q1′', 'Q2a', 'Q2b', 'Q3', 'Q4', 'Q5', 'Q6']);
  assert.match(C.ui.t1Title2, /Sáu câu hỏi/);
  assert.match(C.ui.need_q5, /^Q5 /); assert.match(C.ui.need_q6, /^Q6 /);
});

// ---------- mục 8, 9 · chữ ----------
test('mục 8 · Từ điển: "mở ảo" tách HT / công cụ (QĐ-19); "hạng vùng" chỉ hấp thụ ½', () => {
  const g = (k) => C.glossary.filter((x) => x.key === k)[0].def;
  assert.match(g('mo-ao'), /Hệ thống:/); assert.match(g('mo-ao'), /Công cụ:.*QĐ-19/);
  assert.match(g('hang'), /hấp thụ đi cỡ ½/); assert.ok(!/cỡ lệnh nhỏ hơn/.test(g('hang')));
});
test('USER-TEST 4 · Từ điển có mục R và hình dạng profile; mồi / trap / bong bóng / DMA có ví dụ hoặc tên chỉ báo', () => {
  const keys = C.glossary.map((g) => g.key);
  ['r', 'hinh-dang', 'moi', 'trap', 'bong-bong', 'dma'].forEach((k) => assert.ok(keys.includes(k), k));
  const g = (k) => C.glossary.filter((x) => x.key === k)[0].def;
  assert.match(g('r'), /4195,4/); assert.match(g('hinh-dang'), /Chữ nhật/); assert.match(g('moi'), /Ví dụ/); assert.match(g('trap'), /Ví dụ/);
  assert.match(g('bong-bong'), /chart M1/); assert.match(g('dma'), /chart M1/);
  const refs = [];
  (function walk(o) { if (o && typeof o === 'object') { if (typeof o.gloss === 'string') refs.push(o.gloss); Object.keys(o).forEach((k) => walk(o[k])); } })(C);
  assert.ok(refs.length >= 6);
  refs.forEach((k) => assert.ok(keys.includes(k), 'gloss ' + k));
});

// ---------- USER-TEST 5 · sao chép từ đêm trước ----------
test('USER-TEST 5 · sao chép VWAP tuần, HVN 3 tuần và Q1′ từ đêm trước cùng tuần; không chép đêm tuần trước', () => {
  const st = { nights: {} };
  const mkN = (key, extra) => { const n = J.newNight(key); n.card.lockedAt = '19:00'; Object.assign(n.card, extra); return n; };
  st.nights['2026-10-12'] = mkN('2026-10-12', { answers: { q1w: 'D' }, zones: [{ id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'valEu', price: 4182 }, { id: 'z3', type: 'hvn3w', price: 4200 }] });
  st.nights['2026-10-09'] = mkN('2026-10-09', { answers: { q1w: 'P' }, zones: [{ id: 'z1', type: 'vwapW', price: 4100 }] });
  assert.equal(J.prevCardSource(st, '2026-10-13'), '2026-10-12');
  assert.equal(J.prevCardSource(st, '2026-10-12'), null);
  const cur = J.newNight('2026-10-13');
  const n = J.copyFromPrev(cur, st.nights['2026-10-12']);
  assert.equal(n, 3);
  assert.equal(cur.card.answers.q1w, 'D');
  assert.deepEqual(cur.card.zones.map((z) => [z.id, z.type, z.price]), [['z1', 'vwapW', 4181], ['z2', 'hvn3w', 4200]]);
  assert.equal(J.copyFromPrev(cur, st.nights['2026-10-12']), 0);
});

// ---------- mục 16 · bảng bật kịch bản: chế độ chờ công nhận / thin × bias KHÔNG / CHỜ (R34) ----------
test('mục 16 · bảng bật kịch bản: pending / thin × bias KHÔNG / CHỜ khóa đúng mã đầu tiên', () => {
  const { ANS_NONE, ANS_WAIT, clone } = require('./helpers.js');
  const PENDING = { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z3', at: '20:40', nth: 1, step1: true, step2: false } };
  const THIN = { mode: 'thin', thinDir: 'up' };
  const en = (reg, ans) => go('B', { answers: clone(ans), regime: reg }).enabled;
  assert.deepEqual(en(PENDING, ANS_NONE), { A: 'DIS_BIAS_NONE', B: 'DIS_BIAS_NONE', C: null, D: 'DIS_BIAS_NONE' });
  assert.deepEqual(en(PENDING, ANS_WAIT), { A: 'DIS_BIAS_WAIT', B: 'DIS_BIAS_WAIT', C: 'DIS_BIAS_WAIT', D: 'DIS_BIAS_WAIT' });
  assert.deepEqual(en(THIN, ANS_NONE), { A: 'DIS_BIAS_NONE', B: 'DIS_BIAS_NONE', C: 'DIS_THIN_NO_FADE', D: 'DIS_BIAS_NONE' });
  assert.deepEqual(en(THIN, ANS_WAIT), { A: 'DIS_BIAS_WAIT', B: 'DIS_BIAS_WAIT', C: 'DIS_BIAS_WAIT', D: 'DIS_BIAS_WAIT' });
});
