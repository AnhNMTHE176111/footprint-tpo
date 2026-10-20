// Kiểm thử đầu cuối bản 2.1: ≤ 5 thao tác tới ghi lệnh, khối thu gọn, ô tự kiểm mới, kết quả lệnh trên thanh dưới, vùng bấm từ thẻ phiên,
// điện thoại chạm hai lần, tương phản sáng / tối, vùng bấm ≥ 36 px, nhãn không bị bóp, ↑↓ không bị chuột giành, ảnh ca thật, nhập sai.
import test from 'node:test';
import assert from 'node:assert/strict';
import { launch, openPage, buildState, blockB, ticksAll, tick, prog, fillNum, verdict, segIn, KEY } from './helpers.mjs';

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}
const stored = (page) => page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')));
const goT2 = (page) => page.click('[data-tier-btn="2"]');
const openB = (page) => page.click('[data-testid="toggle-B"]');

// khối B đã làm xong phần Bối cảnh + Kiểm tra, chỉ chờ nến xác nhận (kịch bản "làm sẵn lúc chờ nến")
function readyB(n) {
  const t = ticksAll('B'); delete t.ent1; delete t.sl1;
  n.se.blocks.B = { side: 'buy', zoneId: 'z1', ticks: t }; n.se.c6 = 2; n.se.last = 'B'; n.se.touch.B = 1; n.se.n = 1;
}
const SCREEN_H = 768;

test('v21-1 · từ nến xác nhận đóng tới ghi lệnh: 5 thao tác (tick nến xác nhận · giá vào + Enter · SL + Enter · tick ô SL · Enter ghi lệnh)', async () => {
  await withPage(buildState('B', readyB), {}, async ({ page, errors }) => {
    await goT2(page);
    assert.equal(await verdict(page), 'WAIT');
    let ops = 0;
    await page.click(tick('B', 'ent1')); ops++;                                    // 1. nến M1 xác nhận đã đóng: tick ô "Điểm vào"
    await page.waitForFunction(() => document.activeElement && document.activeElement.dataset.id === 'entry-B');   // máy tự nhảy vào ô Giá vào
    await page.keyboard.type('4177'); await page.keyboard.press('Enter'); ops++;   // 2. giá vào + Enter (nhảy sang SL)
    assert.equal(await page.evaluate(() => document.activeElement.dataset.id), 'sl-B');
    await page.keyboard.type('4174.7'); await page.keyboard.press('Enter'); ops++; // 3. SL + Enter (nhảy sang ô tick vị trí SL)
    assert.equal(await page.evaluate(() => document.activeElement.dataset.id), 'tick-B-sl1');
    assert.equal(await verdict(page), 'WAIT');
    await page.keyboard.press('Space'); ops++;                                      // 4. tick ô SL
    assert.equal(await verdict(page), 'ENTRY');
    assert.equal((await stored(page)).nights[KEY].trades.length, 0);
    await page.keyboard.press('Enter'); ops++;                                      // 5. Enter = Ghi lệnh
    const t = (await stored(page)).nights[KEY].trades[0];
    assert.deepEqual([t.side, t.scenario, t.entry, t.sl, t.tp, t.size], ['buy', 'B', 4177, 4174.7, 4183.9, 1]);
    assert.equal(ops, 5);
    assert.deepEqual(errors, []);
  });
  // cùng đường đi nhưng bằng chuột: 5 cú bấm / gõ (ô số tính một thao tác)
  await withPage(buildState('B', readyB), {}, async ({ page }) => {
    await goT2(page);
    await page.click(tick('B', 'ent1'));
    await page.fill('[data-id="entry-B"]', '4177');
    await page.fill('[data-id="sl-B"]', '4174,7');
    await page.click(tick('B', 'sl1'));
    assert.equal(await verdict(page), 'ENTRY');
    await page.click('[data-testid="btn-entry"]');
    assert.equal((await stored(page)).nights[KEY].trades.length, 1);
  });
});

test('v21-2 · khối thu gọn: trang Setup Entry ≤ 3 màn (1366×768) khi 3 khối thu gọn; ô chung gọn; bấm mục thiếu trên thanh dưới mở khối đang đóng', async () => {
  const st = buildState('B', (n) => { readyB(n); n.se.blocks.B.ticks = ticksAll('B'); n.se.blocks.B.entry = 4177; n.se.blocks.B.sl = 4174.7; });
  await withPage(st, {}, async ({ page }) => {
    await goT2(page);
    assert.equal(await verdict(page), 'ENTRY');
    const h = await page.evaluate(() => document.documentElement.scrollHeight);
    assert.ok(h <= 3 * SCREEN_H, 'trang cao ' + h + ' px = ' + (h / SCREEN_H).toFixed(2) + ' màn');
    const cm = await page.$eval('[data-testid="common"]', (e) => e.getBoundingClientRect().height);
    assert.ok(cm < 180, 'ô chung cao ' + cm);
    assert.equal(await page.locator('[data-common].bad').count(), 0);
    assert.match(await page.textContent('[data-testid="common-sum"]'), /4\/4 máy kiểm đạt/);
    const open = await page.locator('.blk:not(.collapsed)').count(); assert.equal(open, 1);
  });
  // khối đang làm bị đóng tay, thanh dưới liệt kê ô thiếu: bấm ô thiếu thì khối mở lại và cuộn tới ô
  const st2 = buildState('B', (n) => { readyB(n); });
  await withPage(st2, {}, async ({ page }) => {
    await goT2(page);
    await page.click('[data-testid="toggle-B"]');                                   // đóng B
    assert.equal(await page.getAttribute('[data-testid="toggle-B"]', 'aria-expanded'), 'false');
    await page.click('[data-testid="verdict"] .vitem >> nth=0');
    assert.equal(await page.getAttribute('[data-testid="toggle-B"]', 'aria-expanded'), 'true');
  });
});

test('v21-3 · ô tự kiểm: giá vào cách vùng (1–3 giá cần râu chạm vùng, > 3 giá là ở lưng); bias KHÔNG đỏ ở khối B; giờ phá của khối A', async () => {
  await withPage(buildState('B', (n) => { readyB(n); n.se.blocks.B.ticks = ticksAll('B'); }), {}, async ({ page }) => {
    await goT2(page);
    await fillNum(page, 'entry-B', '4177'); await fillNum(page, 'sl-B', '4174,7');
    assert.ok((await page.getAttribute('[data-block="B"] [data-auto="near"]', 'class')).includes('ok'));
    assert.equal(await page.locator('[data-testid="wick-B"]').isVisible(), false);
    await fillNum(page, 'entry-B', '4179'); await fillNum(page, 'sl-B', '4176,7');          // cách vùng 4176,5 là 2,5 giá
    const near = page.locator('[data-block="B"] [data-auto="near"]');
    assert.ok((await near.getAttribute('class')).includes('bad')); assert.match(await near.textContent(), /cách vùng 2,5 giá: chỉ đạt nếu râu nến xác nhận chạm vùng/);
    assert.equal(await verdict(page), 'WAIT');
    await page.click('[data-testid="wick-B"]');                                              // râu nến xác nhận chạm vùng
    assert.ok((await near.getAttribute('class')).includes('ok'));
    assert.equal(await verdict(page), 'ENTRY');
    await fillNum(page, 'entry-B', '4181'); await fillNum(page, 'sl-B', '4178,7');          // cách 4,5 giá: ở lưng, râu không cứu
    assert.ok((await near.getAttribute('class')).includes('bad')); assert.match(await near.textContent(), /quá 3 giá là ở lưng: bỏ kèo/);
    assert.equal(await verdict(page), 'WAIT');
  });
  // bias KHÔNG: khối B đỏ ô bias (chỉ C được), không ENTRY; vẫn tick được
  await withPage(buildState('B', (n) => { readyB(n); n.se.blocks.B.ticks = ticksAll('B'); n.se.blocks.B.entry = 4177; n.se.blocks.B.sl = 4174.7; n.card.answers = { q1: 'D', q5: 'below', vwapW: 'above', q6: 'yes' }; }), {}, async ({ page }) => {
    await goT2(page);
    const b = page.locator('[data-block="B"] [data-auto="bias"]');
    assert.ok((await b.getAttribute('class')).includes('bad')); assert.match(await b.textContent(), /Bias KHÔNG: chỉ fade hai cạnh VA Âu \(khối C\), mục tiêu 2R, cỡ ½\. Không phá hồi/);
    assert.equal(await verdict(page), 'WAIT');
  });
  // giờ phá khối A: tick ô nến M5 lúc 18:30 (trước COMEX 19:20) ⇒ đỏ; lúc 19:25 ⇒ đạt
  const stA = (hm) => buildState('A', (n) => { n.se.blocks.A = { side: 'sell', zoneId: 'z2', ticks: {} }; n.se.last = 'A'; n.se.touch.A = 1; n.se.n = 1; });
  await withPage(stA(), { now: '2026-10-13T11:30:00Z' }, async ({ page }) => {
    await goT2(page);
    assert.equal(await page.locator('[data-block="A"] [data-auto="breakHours"].bad').count(), 0);
    await page.click(tick('A', 'ctx1'));
    const bh = page.locator('[data-block="A"] [data-auto="breakHours"]');
    assert.ok((await bh.getAttribute('class')).includes('bad')); assert.match(await bh.textContent(), /Cú phá lúc 18:30 rơi vào 18:00–19:20/);
    assert.equal((await stored(page)).nights[KEY].se.blocks.A.ctx1At, 18 * 60 + 30);
  });
  await withPage(stA(), { now: '2026-10-13T12:25:00Z' }, async ({ page }) => {
    await goT2(page);
    await page.click(tick('A', 'ctx1'));
    assert.ok((await page.getAttribute('[data-block="A"] [data-auto="breakHours"]', 'class')).includes('ok'));
  });
});

test('v21-4 · thẻ phiên: bấm vùng ở cột phải điền vào khối đang làm; chạm đầu tiên điền hướng theo bias', async () => {
  await withPage(buildState('B'), {}, async ({ page }) => {
    await goT2(page);
    await page.click('[data-zone-pick="z2"]');                                       // chưa mở khối nào
    assert.match(await page.textContent('#toast'), /Mở một khối trước/);
    await openB(page);
    await page.click(tick('B', 'ctx1'));                                             // lần chạm đầu: hướng mặc định theo bias BUY
    let b = (await stored(page)).nights[KEY].se.blocks.B;
    assert.equal(b.side, 'buy');
    await page.click('[data-zone-pick="z2"]');
    b = (await stored(page)).nights[KEY].se.blocks.B;
    assert.equal(b.zoneId, 'z2');
    assert.equal(await page.getAttribute(segIn('B:zone', 'z2'), 'aria-pressed'), 'true');
    // bấm hướng đang chọn thì bỏ chọn, không bị hướng mặc định giành lại
    await page.click(segIn('B:side', 'buy'));
    b = (await stored(page)).nights[KEY].se.blocks.B;
    assert.equal(b.side, undefined);
  });
});

test('v21-5 · ô chung: nhãn "vừa có nến dài nhất" không bị bóp ở 360–1920 px; mặc định tắt (đạt); bật ⇒ đỏ, chưa ENTRY', async () => {
  for (const w of [360, 380, 390, 420, 600, 730, 1000, 1366, 1920]) {
    await withPage(buildState('B', readyB), { viewport: { width: w, height: 800 } }, async ({ page }) => {
      await goT2(page);
      const m = await page.$eval('[data-common="longest"] .tick36', (e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; });
      assert.ok(m[0] >= 200 || m[0] >= w - 80, `rộng ${m[0]} ở ${w}px`);
      assert.ok(m[1] < 80, `cao ${m[1]} ở ${w}px`);
    });
  }
  await withPage(buildState('B', (n) => { readyB(n); n.se.blocks.B.ticks = ticksAll('B'); n.se.blocks.B.entry = 4177; n.se.blocks.B.sl = 4174.7; }), {}, async ({ page }) => {
    await goT2(page);
    assert.equal(await page.isChecked('[data-testid="tick-common-longest"]'), false);
    assert.equal(await verdict(page), 'ENTRY');
    await page.click('[data-testid="tick-common-longest"]');
    assert.equal(await verdict(page), 'WAIT');
    assert.equal(await page.locator('[data-common="longest"].bad').count(), 1);
    assert.match(await page.textContent('[data-common="longest"]'), /Vừa có nến dài nhất phiên: chờ 3 nến M1/);
  });
});

test('v21-6 · thanh dưới khi có lệnh mở: SL, hòa, đóng tay (cần lý do) ngay tại Setup Entry', async () => {
  const mkOpen = (n) => { n.trades.push({ id: 'x1', time: '21:00', side: 'buy', scenario: 'B', zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, tp: 4183.9, rrPlanned: 3, size: 1, slDist: 2.3, flags: [], ruleCodes: [], missing: [], ticks: {}, exit: null, r: null }); n.se.last = 'A'; n.se.blocks.A = { ticks: {} }; };
  await withPage(buildState('B', mkOpen), {}, async ({ page }) => {
    await goT2(page);
    assert.equal(await verdict(page), 'OPEN');
    await page.click('[data-testid="bar-SL"]');
    await page.fill('[data-id="barprice"]', '4174,5');
    assert.match(await page.textContent('[data-testid="bar-r"]'), /R -1,09|R -1,1/);
    await page.click('[data-testid="bar-cancel"]');
    assert.equal((await stored(page)).nights[KEY].trades[0].exit, null);
    await page.click('[data-testid="bar-SL"]');
    await page.keyboard.press('Enter');                                              // Enter trong ô giá = ghi
    await page.waitForFunction(() => document.querySelector('[data-testid="verdict"]').dataset.verdict !== 'OPEN');
    let t = (await stored(page)).nights[KEY].trades[0];
    assert.equal(t.exit.kind, 'SL'); assert.equal(t.r, -1); assert.match(await page.textContent('.statusbar'), /SL liên tiếp 1 trên 3/);
  });
  await withPage(buildState('B', mkOpen), {}, async ({ page }) => {
    await goT2(page);
    await page.click('[data-testid="bar-MANUAL"]');
    await page.fill('[data-id="barprice"]', '4179,3');
    await page.click('[data-testid="bar-confirm"]');                                 // chưa chọn lý do
    assert.equal((await stored(page)).nights[KEY].trades[0].exit, null);
    await page.click('[data-testid="bar-reason-other"]');
    await page.click('[data-testid="bar-confirm"]');
    await page.waitForFunction(() => document.querySelector('[data-testid="verdict"]').dataset.verdict !== 'OPEN');
    const t = (await stored(page)).nights[KEY].trades[0];
    assert.equal(t.exit.kind, 'MANUAL'); assert.equal(t.exit.price, 4179.3); assert.ok(t.flags.includes('RULE_BREAK'));
  });
  await withPage(buildState('B', mkOpen), {}, async ({ page }) => {
    await goT2(page);
    await page.click('[data-testid="bar-BE"]');
    assert.equal(await page.inputValue('[data-id="barprice"]'), '4177');
    await page.click('[data-testid="bar-confirm"]');
    await page.waitForFunction(() => document.querySelector('[data-testid="verdict"]').dataset.verdict !== 'OPEN');
    assert.equal((await stored(page)).nights[KEY].trades[0].r, 0);
  });
});

// ---------- tương phản ----------
const CONTRAST_JS = () => {
  function parse(c) { const m = /rgba?\(([^)]+)\)/.exec(c); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return { r: p[0], g: p[1], b: p[2], a: p[3] === undefined ? 1 : p[3] }; }
  function over(top, bot) { const a = top.a + bot.a * (1 - top.a); return { r: (top.r * top.a + bot.r * bot.a * (1 - top.a)) / a, g: (top.g * top.a + bot.g * bot.a * (1 - top.a)) / a, b: (top.b * top.a + bot.b * bot.a * (1 - top.a)) / a, a }; }
  function bgOf(el) {
    const stack = [];
    for (let e = el; e; e = e.parentElement) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) { stack.push(c); if (c.a >= 1) break; } }
    let acc = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = stack.length - 1; i >= 0; i--) acc = over(stack[i], acc);
    return acc;
  }
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  return function ratio(el) {
    const fg0 = parse(getComputedStyle(el).color), bg = bgOf(el);
    const fg = over(fg0, bg);
    const l1 = lum(fg), l2 = lum(bg);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
};
test('v21-7 · tương phản chữ ≥ 4,5:1 ở chế độ sáng và tối cho các phần tử biên bản TEST-UI nêu', async () => {
  const checks = [];
  for (const theme of ['light', 'dark']) {
    // tầng 0: nút chính; tầng đang chọn
    const s0 = buildState('nocard'); s0.settings.theme = theme;
    await withPage(s0, {}, async ({ page }) => {
      await page.click('[data-tier-btn="0"]');
      const r = await page.evaluate((src) => { const ratio = eval('(' + src + ')')(); const q = (s) => [...document.querySelectorAll(s)].filter((e) => e.getBoundingClientRect().width > 0);
        return { primary: q('.btn.primary').map(ratio), tnum: q('.tierbtn.active .tnum').map(ratio), tdone: q('.tdone').map(ratio) }; }, CONTRAST_JS.toString());
      for (const k of Object.keys(r)) r[k].forEach((v) => checks.push([theme, 'tầng 0 ' + k, v]));
    });
    // Setup Entry: ENTRY, ô đã tick, chip bias SELL, nút "Vẫn vào"
    const s2 = buildState('A', (n) => { n.se.blocks.A = { side: 'sell', zoneId: 'z2', ticks: { ctx1: true, ctx2: true }, entry: 4193, sl: 4195.4 }; n.se.last = 'A'; n.se.touch.A = 1; n.se.n = 1; }); s2.settings.theme = theme;
    await withPage(s2, {}, async ({ page }) => {
      await goT2(page);
      const r = await page.evaluate((src) => { const ratio = eval('(' + src + ')')(); const q = (s) => [...document.querySelectorAll(s)].filter((e) => e.getBoundingClientRect().width > 0);
        return { sell: q('.chip.dir-sell').map(ratio), tick: q('.tickrow:has(input:checked) .tt').map(ratio), force: q('.vbar.v-wait .btn.danger').map(ratio), wait: q('.vbar.v-wait .vtext').map(ratio), cm: q('.cm-sum').map(ratio) }; }, CONTRAST_JS.toString());
      for (const k of Object.keys(r)) r[k].forEach((v) => checks.push([theme, 'Setup Entry ' + k, v]));
    });
    const s3 = buildState('B', (n) => { n.se.blocks.B = blockB(); n.se.last = 'B'; n.se.touch.B = 1; n.se.n = 1; }); s3.settings.theme = theme;
    await withPage(s3, {}, async ({ page }) => {
      await goT2(page);
      const r = await page.evaluate((src) => { const ratio = eval('(' + src + ')')(); const q = (s) => [...document.querySelectorAll(s)].filter((e) => e.getBoundingClientRect().width > 0);
        return { ebig: q('.vbar.v-entry .ebig, .vbar.v-entry .erest').map(ratio), write: q('.vbar.v-entry .btn.primary').map(ratio) }; }, CONTRAST_JS.toString());
      for (const k of Object.keys(r)) r[k].forEach((v) => checks.push([theme, 'ENTRY ' + k, v]));
    });
  }
  assert.ok(checks.length >= 20, 'chỉ đo được ' + checks.length + ' phần tử');
  const bad = checks.filter((c) => c[2] < 4.5);
  assert.deepEqual(bad.map((c) => c[0] + ' · ' + c[1] + ' · ' + c[2].toFixed(2)), []);
});

test('v21-8 · vùng bấm ≥ 36 px: nút "?", nút nhỏ, Từ điển, ô chọn nhỏ, mục thiếu, ô tick, tóm tắt "Thêm tay"', async () => {
  const minOf = async (page, sel) => page.$$eval(sel, (els) => els.map((e) => e.getBoundingClientRect()).filter((r) => r.width > 0 && r.height > 0).map((r) => r.height));
  // tầng 2
  await withPage(buildState('B', readyB), {}, async ({ page }) => {
    await goT2(page);
    for (const sel of ['button.help', '.btn.small', '.statusbar .glossary-btn', '.vitem', '[data-block="B"] .tick36', '[data-block="B"] .auto']) {
      const hs = await minOf(page, sel);
      assert.ok(hs.length > 0, 'không thấy ' + sel);
      assert.ok(Math.min(...hs) >= 35.5, sel + ' cao ' + Math.min(...hs));
    }
    const wk = await page.$$eval('button.help', (els) => els.map((e) => e.getBoundingClientRect()).filter((r) => r.width > 0).map((r) => Math.min(r.width, r.height)));
    assert.ok(Math.min(...wk) >= 36, '"?" ' + Math.min(...wk));
    await page.click('[data-testid="glossary-btn"]');
    const g = await page.$eval('.gclose', (e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; });
    assert.ok(g[0] >= 36 && g[1] >= 36, 'nút đóng Từ điển ' + g);
  });
  // tầng 1 và 3
  await withPage(buildState('nocard', (n) => { n.card.lockedAt = null; n.card.answers = { q1: 'D', q5: 'below' }; }), {}, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    for (const sel of ['.seg.small .opt', '.btn.small']) { const hs = await minOf(page, sel); assert.ok(hs.length > 0, sel); assert.ok(Math.min(...hs) >= 35.5, sel + ' ' + Math.min(...hs)); }
    await page.click('[data-tier-btn="0"]');
    const f = await minOf(page, '.fold > summary'); assert.ok(f.length > 0); assert.ok(Math.min(...f) >= 35.5, 'summary ' + Math.min(...f));
    await page.click('[data-tier-btn="3"]');
    const fi = await minOf(page, 'input.filein'); assert.ok(fi.length > 0); assert.ok(Math.min(...fi) >= 35.5, 'filein ' + Math.min(...fi));
  });
  await withPage(buildState('B', (n) => { n.trades.push({ id: 'x1', time: '21:00', side: 'buy', scenario: 'B', zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, tp: 4183.9, rrPlanned: 3, size: 1, slDist: 2.3, flags: [], ruleCodes: [], missing: [], ticks: {}, exit: { kind: 'TP', price: 4183.9, at: '21:30' }, r: 3 }); }), {}, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.click('details.fold > summary');
    const hs = await minOf(page, '.tx label.tick'); assert.ok(hs.length > 0); assert.ok(Math.min(...hs) >= 35.5, 'tick Sổ ' + Math.min(...hs));
  });
  // điện thoại
  await withPage(buildState('B', readyB), { viewport: { width: 390, height: 844 } }, async ({ page }) => {
    await goT2(page);
    const sb = await minOf(page, '.sbtoggle'); assert.ok(Math.min(...sb) >= 35.5, 'Trạng thái ' + sb);
  });
});

test('v21-9 · ô chọn vùng: chuột đứng yên không giành lại dòng khi dùng ↑↓; mở sát đáy màn hình thì cuộn cho vừa; Esc đóng khung "?"', async () => {
  await withPage(buildState('nocard', (n) => { n.card.lockedAt = null; n.card.zones = []; }), {}, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    await page.click('[data-testid="zone-type"]');
    const types = await page.$$eval('[data-testid="zone-list"] li[data-type]', (els) => els.map((e) => e.dataset.type));
    const li = page.locator('li[data-type]').nth(3);
    await li.hover();                                                               // chuột đứng yên trên dòng 4
    const act = () => page.$eval('li.active', (e) => e.dataset.type);
    assert.equal(await act(), types[3]);
    const seen = [];
    for (let i = 0; i < 12; i++) { await page.keyboard.press('ArrowDown'); seen.push(types.indexOf(await act())); }
    assert.deepEqual(seen, [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);           // mỗi lần bấm đi đúng 1 dòng, không bị nuốt
    await page.keyboard.press('Escape');
    // cuộn sát đáy rồi mở: khung nằm trong màn hình
    await page.evaluate(() => document.querySelector('.zform').scrollIntoView({ block: 'end' }));
    await page.click('[data-testid="zone-type"]');
    const b = await page.$eval('.zpick-pop', (e) => e.getBoundingClientRect().bottom);
    assert.ok(b <= 768 + 1, 'đáy khung ' + b);
    await page.keyboard.press('Escape');
    // Esc đóng khung "?"
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.click('button.help >> nth=0');
    assert.ok(await page.locator('.pop:visible').count() >= 1);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.pop:visible').count(), 0);
    assert.equal(await page.evaluate(() => document.activeElement.classList.contains('help')), true);
  });
});

test('v21-10 · điện thoại (cảm ứng): chạm lần đầu vào loại vùng chỉ hiện định nghĩa, chạm lần hai mới chọn', async () => {
  await withPage(buildState('nocard', (n) => { n.card.lockedAt = null; n.card.zones = []; }), { viewport: { width: 390, height: 844 }, hasTouch: true }, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    await page.tap('[data-testid="zone-type"]');
    const before = await page.textContent('[data-testid="zone-type"]');
    const row = page.locator('li[data-type="poorLow"]');
    await row.scrollIntoViewIfNeeded();
    await row.tap();
    assert.equal(await page.locator('.zpick-pop:visible').count(), 1);               // vẫn mở
    assert.equal(await page.textContent('[data-testid="zone-type"]'), before);       // chưa chọn
    assert.equal(await page.$eval('li.active', (e) => e.dataset.type), 'poorLow');
    assert.match(await page.textContent('li.active .zpick-inline'), /Đáy phẳng: mức giá thấp nhất có từ 2 TPO/);
    await row.tap();                                                                 // chạm lần hai
    assert.equal(await page.locator('.zpick-pop:visible').count(), 0);
    assert.match(await page.textContent('[data-testid="zone-type"]'), /Poor low/);
  });
});

test('v21-11 · ảnh ca thật: có liên kết mở ảnh gốc để phóng to; điện thoại hộp ảnh toàn màn hình; máy tính nút Đóng nằm trong màn hình', async () => {
  await withPage(buildState('B', readyB), { viewport: { width: 390, height: 844 } }, async ({ page }) => {
    await goT2(page);
    await page.click('[data-testid="thumb-B"]');
    const a = page.locator('.imgdlg a');
    assert.match(await a.getAttribute('href'), /kb-b-hap-thu\.png$/); assert.equal(await a.getAttribute('target'), '_blank');
    const m = await page.$eval('.modal', (e) => { const r = e.getBoundingClientRect(); return [r.width, r.height]; });
    assert.equal(m[0], 390);
    const w = await page.$eval('.scenimg.full', (e) => e.getBoundingClientRect().width); assert.ok(w >= 370, 'ảnh rộng ' + w);
  });
  await withPage(buildState('B', readyB), {}, async ({ page }) => {
    await goT2(page);
    await page.click('[data-testid="thumb-B"]');
    const r = await page.$eval('.imgdlg .actions .btn', (e) => e.getBoundingClientRect());
    assert.ok(r.bottom <= 768 && r.top >= 0, 'nút Đóng ở ' + r.top + '–' + r.bottom);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.imgdlg').count(), 0);
  });
});

test('v21-12 · nhập sai: chữ rác báo rõ và bị xóa; SL sai phía nói đúng nghĩa; thông báo không che nút tầng', async () => {
  await withPage(buildState('B', readyB), {}, async ({ page }) => {
    await goT2(page);
    await page.fill('[data-id="entry-B"]', 'abc'); await page.press('[data-id="entry-B"]', 'Tab');
    assert.equal(await page.inputValue('[data-id="entry-B"]'), '');
    assert.match(await page.textContent('#toast'), /Không đọc được số "abc" — đã xóa/);
    await fillNum(page, 'entry-B', '4181'); await fillNum(page, 'sl-B', '4182');
    assert.match(await page.textContent('[data-testid="calc-B"]'), /SL phải thấp hơn giá vào \(buy\)/);
    assert.doesNotMatch(await page.textContent('[data-testid="calc-B"]'), /Nhập hướng, giá vào và SL/);
    // thông báo nằm trên thanh dưới, không đè lên hàng nút tầng
    const tb = await page.$eval('#tiers', (e) => e.getBoundingClientRect());
    const t = await page.$eval('.toast-item', (e) => e.getBoundingClientRect());
    assert.ok(t.top > tb.bottom, 'thông báo ở ' + t.top + ', nút tầng tới ' + tb.bottom);
  });
});

test('v21-13 · 390 px: Setup Entry không tràn ngang với khối mở, thanh dưới lệnh mở ≤ 1/3 màn hình; thẻ phiên một nút đóng', async () => {
  const st = buildState('B', (n) => { readyB(n); n.trades.push({ id: 'x1', time: '21:00', side: 'buy', scenario: 'B', zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, tp: 4183.9, rrPlanned: 3, size: 1, slDist: 2.3, flags: [], ruleCodes: [], missing: [], ticks: {}, exit: null, r: null }); });
  await withPage(st, { viewport: { width: 390, height: 844 } }, async ({ page }) => {
    await page.click('[data-tier-btn="2"]');
    assert.equal(await verdict(page), 'OPEN');
    const w = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    assert.ok(w[0] <= w[1], 'rộng ' + w[0]);
    const vh = await page.$eval('#verdict', (e) => e.getBoundingClientRect().height);
    assert.ok(vh <= 844 / 3, 'thanh dưới cao ' + vh);
    await page.click('#cardtoggle');
    assert.equal(await page.isVisible('#cardtoggle'), false);
    assert.equal(await page.isVisible('.cardclose'), true);
  });
});
