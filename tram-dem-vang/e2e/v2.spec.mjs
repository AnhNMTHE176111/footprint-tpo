// Kiểm thử đầu cuối v2: Setup Entry (4 khối mở sẵn), ô chọn loại vùng có định nghĩa, ghi lệnh vào Sổ, nhập kết quả, "Vẫn vào", 390 px.
import test from 'node:test';
import assert from 'node:assert/strict';
import { launch, openPage, buildState, blockB, tick, prog, fillNum, verdict, seg, segIn, KEY } from './helpers.mjs';

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}
const stored = (page) => page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')));
const goT2 = (page) => page.click('[data-tier-btn="2"]');

// tick bằng chuột thật toàn bộ khối B + ô chung, gõ số
async function fillBlockB(page) {
  await page.click(segIn('B:side', 'buy'));
  await page.click(segIn('B:zone', 'z1'));
  for (const id of ['ctx1', 'ctx2', 'ctx3', 'ctx4', 'chk1', 'chk2', 'chk3', 'chk4', 'ent1', 'sl1']) await page.click(tick('B', id));
  await fillNum(page, 'entry-B', '4177');
  await fillNum(page, 'sl-B', '4174,7');
  await fillNum(page, 'c6-B', '2');
  await page.click('[data-testid="tick-common-longest"]');
}

test('v2-1 · bốn khối A–D luôn mở, xếp dọc; không khối nào có trạng thái "tắt" hay nút gập; thanh nhảy dính đầu', async () => {
  await withPage(buildState('B'), {}, async ({ page, errors }) => {
    await goT2(page);
    const boxes = await page.$$eval('[data-block]', (els) => els.map((e) => { const r = e.getBoundingClientRect(); return { id: e.dataset.block, h: r.height, top: r.top + window.scrollY, x: r.left }; }));
    assert.deepEqual(boxes.map((b) => b.id), ['A', 'B', 'C', 'D']);
    boxes.forEach((b) => assert.ok(b.h > 400, 'khối ' + b.id + ' cao ' + b.h));                    // đã xổ sẵn checkbox
    for (let i = 1; i < boxes.length; i++) assert.ok(boxes[i].top > boxes[i - 1].top + 400 && boxes[i].x === boxes[0].x, 'xếp dọc');
    assert.equal(await page.locator('[data-block] details').count(), 0);
    assert.equal(await page.locator('[data-block] button[aria-expanded="false"]:not(.help)').count(), 0);
    assert.equal(await page.locator('[data-block] [disabled], [data-block].off, [data-block].disabled').count(), 0);
    assert.equal(await page.locator('[data-block] input[type="checkbox"]').count(), 10 + 10 + 7 + 7);   // A 10, B 10, C 7, D 7
    // checkbox to dễ bấm: vùng bấm ≥ 36 px
    const hs = await page.$$eval('[data-block] .tick36', (els) => els.map((e) => e.getBoundingClientRect().height));
    assert.ok(Math.min(...hs) >= 36, 'vùng bấm nhỏ nhất ' + Math.min(...hs));
    // tiêu đề nhóm
    const grp = await page.$$eval('[data-block="A"] .grp-title', (els) => els.map((e) => e.textContent));
    assert.deepEqual(grp, ['Bối cảnh', 'Kiểm tra', 'Điểm vào', 'SL']);
    // thanh nhảy dính đầu khi cuộn
    await page.evaluate(() => window.scrollTo(0, 2200));
    const jt = await page.$eval('[data-testid="jumpbar"]', (e) => e.getBoundingClientRect().top);
    assert.ok(jt >= 0 && jt < 120, 'thanh nhảy ở ' + jt);
    await page.click('[data-jump="C"]');
    const ct = await page.$eval('#blk-C', (e) => e.getBoundingClientRect().top);
    assert.ok(ct > 40 && ct < 260, 'khối C ở ' + ct);
    assert.deepEqual(errors, []);
  });
});

test('v2-2 · tick đủ khối B bằng chuột thật ⇒ viền xanh, thanh ENTRY dính đáy hiện ENTRY BUY · kịch bản B, chữ ≥ 32 px', async () => {
  await withPage(buildState('B'), {}, async ({ page }) => {
    await goT2(page);
    assert.equal(await verdict(page), 'WAIT');
    assert.match(await page.textContent('[data-testid="verdict"]'), /CHỜ.*chọn một khối/);
    await fillBlockB(page);
    assert.equal(await prog(page, 'B'), '18/18');
    assert.equal(await verdict(page), 'ENTRY');
    assert.equal(await page.locator('[data-block="B"].complete').count(), 1);
    assert.equal(await page.locator('[data-block="A"].complete').count(), 0);
    const txt = await page.textContent('[data-testid="entry-text"]');
    assert.match(txt, /ENTRY BUY · kịch bản B/); assert.match(txt, /4177,0/); assert.match(txt, /SL 4174,7/); assert.match(txt, /1:3/);
    const fs = await page.$eval('.ebig', (e) => parseFloat(getComputedStyle(e).fontSize));
    assert.ok(fs >= 32, 'cỡ chữ ' + fs);
    const pos = await page.$eval('#verdict', (e) => getComputedStyle(e).position);
    assert.equal(pos, 'fixed');
    // bỏ một tick ⇒ lại CHỜ và nói ô còn thiếu
    await page.click(tick('B', 'chk3'));
    assert.equal(await verdict(page), 'WAIT');
    assert.match(await page.textContent('[data-testid="wait-text"]'), /khối B còn thiếu:.*DMA đi ngang/);
    assert.equal(await prog(page, 'B'), '17/18');
  });
});

test('v2-3 · Ghi lệnh: dòng Sổ đủ số, khối bỏ tick (giữ hướng, vùng), cuộn về đầu; lệnh mở chặn ô chung; nhập kết quả TP ngay trên dòng', async () => {
  await withPage(buildState('B'), {}, async ({ page }) => {
    await goT2(page);
    await fillBlockB(page);
    await page.evaluate(() => window.scrollTo(0, 1500));
    await page.click('[data-testid="btn-entry"]');
    const st = (await stored(page)).nights[KEY];
    assert.equal(st.trades.length, 1);
    const t = st.trades[0];
    assert.deepEqual([t.side, t.scenario, t.zoneId, t.entry, t.sl, t.tp, t.rrPlanned, t.size], ['buy', 'B', 'z1', 4177, 4174.7, 4183.9, 3, 1]);
    assert.equal(Object.keys(t.ticks).length, 10); assert.equal(t.exit, null);
    assert.deepEqual(st.se.blocks.B.ticks, {}); assert.equal(st.se.blocks.B.side, 'buy'); assert.equal(st.se.blocks.B.zoneId, 'z1');
    assert.equal(await page.evaluate(() => window.scrollY), 0);
    assert.equal(await prog(page, 'B'), '3/18');                        // chỉ còn hướng, vùng, ô "Đủ vốn"? không: hướng + vùng + lần ≤ 2
    assert.equal(await page.locator('[data-common="open"].bad').count(), 1);
    // sang Sổ: dòng lệnh mở ở trên cùng với nút kết quả
    await page.click('[data-testid="go-journal"]');
    await page.waitForSelector('[data-testid="open-trade"]');
    assert.match(await page.textContent('[data-testid="be-remind"]'), /\+1,5R.*4180,5.*nến M1 đóng ngoài vùng vào/);
    await page.click('[data-testid="open-trade"] [data-v="TP"]');
    assert.equal(await page.inputValue('[data-id="exitprice"]'), '4183,9');
    assert.equal(await page.inputValue('[data-id="exitr"]'), '3');
    await page.click('[data-testid="open-swept"]');
    await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForFunction(() => !document.querySelector('[data-testid="open-trade"]'));
    const t2 = (await stored(page)).nights[KEY].trades[0];
    assert.equal(t2.exit.kind, 'TP'); assert.equal(t2.r, 3); assert.equal(t2.sweptThenTP, true);
    assert.match(await page.textContent('[data-testid="journal"]'), /\+3/);
    await goT2(page);
    assert.equal(await page.locator('[data-common="open"].bad').count(), 0);
  });
});

test('v2-4 · kết quả sửa tay: R sửa được, đóng tay cần lý do, lý do "khác" tính phá luật', async () => {
  const st = buildState('B', (n) => { n.trades.push({ id: 'x1', time: '21:00', side: 'buy', scenario: 'B', zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, tp: 4183.9, rrPlanned: 3, size: 1, slDist: 2.3, flags: [], ruleCodes: [], missing: [], ticks: {}, exit: null, r: null }); });
  await withPage(st, {}, async ({ page }) => {
    await page.waitForSelector('[data-testid="open-trade"]');                       // có lệnh mở ⇒ mở thẳng Sổ
    await page.click('[data-testid="open-trade"] [data-v="MANUAL"]');
    await fillNum(page, 'exitprice', '4179,3');
    assert.equal(await page.inputValue('[data-id="exitr"]'), '1');
    await page.click('[data-testid="btn-close-confirm"]');                            // chưa chọn lý do
    assert.equal(await page.locator('[data-testid="open-trade"]').count(), 1);
    await page.click('[data-testid="open-trade"] [data-v="other"]');
    await fillNum(page, 'exitr', '0,8');
    await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForFunction(() => !document.querySelector('[data-testid="open-trade"]'));
    const t = (await stored(page)).nights[KEY].trades[0];
    assert.equal(t.r, 0.8); assert.ok(t.flags.includes('RULE_BREAK')); assert.deepEqual(t.ruleCodes, ['MANUAL_CLOSE']);
    assert.match(await page.textContent('[data-testid="journal"]'), /đóng tay lý do khác/);
  });
});

test('v2-5 · ô tự kiểm sai hiện đỏ kèm lý do: lần thứ 3 tại vùng, SL ngắn hơn nến, R:R dưới 1:2; không khóa gì', async () => {
  const two = (id) => ({ id, time: '20:00', side: 'buy', scenario: 'B', zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, flags: [], ruleCodes: [], missing: [], ticks: {}, exit: { kind: 'TP', price: 4183.9, at: '20:30' }, r: 3 });
  const st = buildState('B', (n) => { n.trades.push(two('a'), two('b')); n.se.blocks.B = blockB({ c6: 3.0, tp: 4180 }); });
  await withPage(st, {}, async ({ page }) => {
    await goT2(page);
    const z = page.locator('[data-block="B"] [data-item="B:zone2"]');
    assert.match(await z.textContent(), /Lần thứ 3 tại vùng/); assert.match(await z.textContent(), /Đã vào 2 lần ở vùng này/);
    assert.equal(await z.locator('.chip.bad').count(), 1);
    const fl = page.locator('[data-block="B"] [data-auto="slFloor"]');
    assert.ok((await fl.getAttribute('class')).includes('bad')); assert.match(await fl.textContent(), /SL 2,3 giá nhỏ hơn nến 3,0 giá/);
    const rr = page.locator('[data-block="B"] [data-auto="rr"]');
    assert.ok((await rr.getAttribute('class')).includes('bad')); assert.match(await rr.textContent(), /R:R 1:1,3 dưới 1:2/);
    // vẫn tick được tiếp
    await page.click(tick('B', 'sl1'));
    assert.equal(await page.isChecked(tick('B', 'sl1')), false);          // đang tick sẵn ⇒ bỏ
    // sửa số ⇒ ô tự kiểm cập nhật ngay, không cần rời ô
    await fillNum(page, 'c6-B', '2');
    assert.ok((await page.locator('[data-block="B"] [data-auto="slFloor"]').getAttribute('class')).includes('ok'));
    assert.match(await page.textContent('[data-testid="calc-B"]'), /SL 2,3 giá/);
  });
});

test('v2-6 · ngược bias: hiện ô lý do bắt buộc, gõ lý do thì ô thành đủ', async () => {
  await withPage(buildState('B', (n) => { n.se.blocks.B = blockB({ side: 'sell', entry: 4177, sl: 4179.3, tp: 4170.1 }); }), {}, async ({ page }) => {
    await goT2(page);
    const box = page.locator('[data-item="B:counter"]');
    assert.equal(await box.isVisible(), true); assert.match(await box.textContent(), /Ngược bias BUY/);
    assert.equal(await prog(page, 'B'), '18/19');
    await box.locator('input').fill('đỉnh có tail thật');
    assert.equal(await prog(page, 'B'), '19/19');
    await page.click(segIn('B:side', 'buy'));
    assert.equal(await page.locator('[data-item="B:counter"]').isVisible(), false);
  });
});

test('v2-7 · "Vẫn vào (thiếu n ô — tính phá luật)": hỏi xác nhận, dòng Sổ có cờ phá luật và danh sách ô thiếu; 2 lần ⇒ "Chưa tắt máy" đỏ', async () => {
  const st = buildState('B', (n) => { n.se.blocks.B = blockB(); delete n.se.blocks.B.ticks.chk3; delete n.se.blocks.B.ticks.ctx3; n.se.last = 'B'; n.se.touch.B = 1; n.se.n = 1; });
  await withPage(st, {}, async ({ page }) => {
    await goT2(page);
    assert.match(await page.textContent('[data-testid="btn-force"]'), /Vẫn vào \(thiếu 3 ô — tính phá luật\)/);   // ctx3, chk3 và ô chung "nến dài nhất" chưa tick
    await page.click('[data-testid="btn-force"]');
    await page.click('[data-testid="dlg-ok"]');
    let t = (await stored(page)).nights[KEY].trades[0];
    assert.ok(t.flags.includes('RULE_BREAK')); assert.deepEqual(t.missing, ['ctx3', 'chk3', 'common:longest']);
    assert.ok(t.missing.includes('ctx3') && t.missing.includes('chk3'));
    assert.match(await page.textContent('.statusbar'), /Phá luật 1 trên 2/);
    // đóng lệnh, vào thêm một lệnh phá luật nữa ⇒ tắt máy
    await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('tdv.v1')); const n = s.nights['2026-10-13'];
      n.trades[0].exit = { kind: 'TP', price: 4183.9, at: '21:40' }; n.trades[0].r = 3;
      n.se.blocks.B = { side: 'buy', zoneId: 'z2', entry: 4178, sl: 4175.7, tp: 4184.9, c6: 2, ticks: {} }; n.se.last = 'B'; n.se.touch.B = 2;
      localStorage.setItem('tdv.v1', JSON.stringify(s));
    });
    await page.reload(); await page.waitForSelector('#main .tier'); await goT2(page);
    await page.click('[data-testid="btn-force"]'); await page.click('[data-testid="dlg-ok"]');
    await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('tdv.v1')); const n = s.nights['2026-10-13'];
      n.trades[1].exit = { kind: 'SL', price: 4175.7, at: '21:50' }; n.trades[1].r = -1; localStorage.setItem('tdv.v1', JSON.stringify(s));
    });
    await page.reload(); await page.waitForSelector('#main .tier'); await goT2(page);
    assert.equal(await page.locator('[data-common="breaker"].bad').count(), 1);
    assert.match(await page.textContent('[data-common="breaker"]'), /Đã 2 lệnh phá luật trong đêm — tắt máy/);
    // không khóa: vẫn tick được
    await page.click(tick('A', 'ctx1')); assert.equal(await page.isChecked(tick('A', 'ctx1')), true);
  });
});

test('v2-8 · phím tắt: 1–4 nhảy tới khối, Enter ghi lệnh khi ENTRY, N xóa tick khối đang làm; tắt khi đang gõ', async () => {
  const st = buildState('B', (n) => { n.se.blocks.B = blockB(); n.se.common = { longest: true }; n.se.last = 'B'; n.se.touch.B = 1; n.se.n = 1; });
  await withPage(st, {}, async ({ page }) => {
    await goT2(page);
    assert.equal(await verdict(page), 'ENTRY');
    await page.click('body', { position: { x: 5, y: 300 } });
    await page.keyboard.press('3');
    const ct = await page.$eval('#blk-C', (e) => e.getBoundingClientRect().top);
    assert.ok(ct > 40 && ct < 260, 'C ở ' + ct);
    await page.focus('[data-id="entry-B"]');
    await page.keyboard.press('n');                                                 // đang gõ vào ô số: phím N không xóa tick
    assert.equal(Object.keys((await stored(page)).nights[KEY].se.blocks.B.ticks).length, 10);
    await page.fill('[data-id="entry-B"]', '4177'); await page.press('[data-id="entry-B"]', 'Tab');
    await page.keyboard.press('Escape');
    await page.keyboard.press('n');
    assert.equal(await prog(page, 'B'), '3/18');                                    // chỉ còn hướng, vùng, lần ≤ 2
    await page.click(tick('B', 'ctx1'));
    assert.equal(await verdict(page), 'WAIT');
  });
  await withPage(st, {}, async ({ page }) => {
    await goT2(page);
    await page.click('body', { position: { x: 5, y: 300 } });
    await page.keyboard.press('Enter');
    const n = (await stored(page)).nights[KEY];
    assert.equal(n.trades.length, 1); assert.equal(n.trades[0].scenario, 'B');
  });
});

test('v2-9 · ô chọn loại vùng: rê chuột hiện định nghĩa; phím ↑↓ hiện định nghĩa; gõ để lọc; Esc đóng; Enter chọn; định nghĩa cũng có trong Từ điển', async () => {
  await withPage(buildState('nocard', (n) => { n.card.lockedAt = null; }), {}, async ({ page, errors }) => {
    await page.click('[data-tier-btn="1"]');
    await page.click('[data-testid="zone-type"]');
    assert.equal(await page.locator('[data-testid="zone-list"] li').count(), 18);
    await page.hover('li[data-type="poorLow"]');
    let def = await page.textContent('[data-testid="zone-def"]');
    assert.match(def, /Poor low/); assert.match(def, /Đáy có từ 2 TPO: giá chưa bị từ chối dứt khoát/); assert.match(def, /Dùng thế nào:.*nợ/s);
    await page.hover('li[data-type="hvn3w"]');
    assert.match(await page.textContent('[data-testid="zone-def"]'), /Nút khối lượng cao trên TPO gộp 3 tuần/);
    const rank = await page.textContent('li[data-type="lvn"] .zrank'); assert.equal(rank, 'cấm fade');
    // phím: ô lọc nhận focus; ↓ đổi dòng và đổi định nghĩa
    assert.equal(await page.evaluate(() => document.activeElement.dataset.testid), 'zone-filter');
    await page.fill('[data-testid="zone-filter"]', 'poor');
    assert.equal(await page.locator('[data-testid="zone-list"] li[data-type]').count(), 2);
    assert.match(await page.textContent('[data-testid="zone-def"]'), /Poor high/);
    await page.keyboard.press('ArrowDown');
    assert.match(await page.textContent('[data-testid="zone-def"]'), /Đáy có từ 2 TPO/);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.zpick-pop:visible').count(), 0);
    assert.equal(await page.evaluate(() => document.activeElement.dataset.testid), 'zone-type');
    // mở lại bằng phím gõ chữ trên nút, chọn bằng Enter
    await page.keyboard.press('v');
    assert.equal(await page.inputValue('[data-testid="zone-filter"]'), 'v');
    await page.fill('[data-testid="zone-filter"]', 'naked');
    await page.keyboard.press('Enter');
    assert.match(await page.textContent('[data-testid="zone-type"]'), /Naked POC/);
    assert.match(await page.textContent('[data-testid="zone-type"]'), /chỉ mục tiêu/);
    // Từ điển cùng nguồn
    await page.click('[data-testid="glossary-btn"]');
    await page.fill('[data-testid="glossary-search"]', 'POC của phiên trước');
    assert.match(await page.textContent('[data-testid="glossary"] dl'), /POC của phiên trước mà giá chưa chạm lại\. Chỉ làm nam châm mục tiêu/);
    assert.deepEqual(errors, []);
  });
  // mọi loại vùng có mục trong Từ điển (cùng nguồn)
  await withPage(buildState('B'), {}, async ({ page }) => {
    await page.click('[data-testid="glossary-btn"]');
    const terms = await page.$$eval('[data-testid="glossary"] dt', (els) => els.map((e) => e.textContent));
    for (const t of ['VWAP tuần', 'VWAP ngày', 'VAH Âu', 'VAL Âu', 'Cụm POC', 'HVN tuần', 'HVN 3 tuần', 'LVN', 'High hôm qua', 'Low hôm qua', 'Single print', 'Naked POC', 'IB high', 'IB low', 'Cạnh range', 'Poor high', 'Poor low', 'HVN ngày']) {
      assert.ok(terms.some((x) => x.startsWith(t)), 'thiếu ' + t);
    }
  });
});

test('v2-10 · điện thoại: định nghĩa loại vùng hiện ngay dưới dòng đang chọn', async () => {
  await withPage(buildState('nocard', (n) => { n.card.lockedAt = null; }), { viewport: { width: 390, height: 800 } }, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    await page.click('[data-testid="zone-type"]');
    await page.keyboard.press('ArrowDown');
    const inline = page.locator('li.active .zpick-inline');
    assert.equal(await inline.isVisible(), true);
    assert.match(await inline.textContent(), /Dùng thế nào/);
    assert.equal(await page.locator('[data-testid="zone-def"]').isVisible(), false);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
  });
});

test('v2-11 · 390 px: không tràn ngang ở cả 4 tầng; thanh ENTRY không che quá 1/3 màn hình; "?" bấm được', async () => {
  const st = buildState('B', (n) => { n.se.blocks.B = blockB(); n.se.common = { longest: true }; n.se.last = 'B'; n.se.touch.B = 1; n.se.n = 1; });
  await withPage(st, { viewport: { width: 390, height: 800 } }, async ({ page, errors }) => {
    for (const t of [0, 1, 2, 3]) {
      await page.click(`[data-tier-btn="${t}"]`);
      const w = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      assert.ok(w[0] <= w[1], 'tầng ' + t + ' rộng ' + w[0]);
    }
    await goT2(page);
    assert.equal(await verdict(page), 'ENTRY');
    const vh = await page.$eval('#verdict', (e) => e.getBoundingClientRect().height);
    assert.ok(vh <= 800 / 3, 'thanh ENTRY cao ' + vh);
    const hb = await page.$eval('[data-block="B"] .help', (e) => e.getBoundingClientRect().width);
    assert.ok(hb >= 36, 'nút ? rộng ' + hb);
    await page.click('[data-block="B"] .help >> nth=0');
    assert.ok(await page.locator('.pop:visible').count() >= 1);
    assert.deepEqual(errors, []);
  });
});

test('v2-12 · mở bằng file:// không lỗi console ở 4 tầng, không có chữ thô ⟦…⟧; dữ liệu v1 cũ được nâng lên v2, lệnh mở cũ thành dòng Sổ chưa có kết quả', async () => {
  const v1 = { version: 1, settings: { theme: 'dark', guideLevel: 'new', capital: 2000, riskPct: 2, dstShift: true, shortcuts: true, lastExportAt: null, sizeAsked: true }, nights: { [KEY]: {
    t0: { alert: true, touched: true }, regime: { mode: 'broken', breakout: { dir: 'down', edgeZoneId: 'z2', step1: true, step2: true } }, setup: { scenario: 'A', zoneId: 'z2', b1: 'U' },
    card: { lockedAt: '19:00', answers: { q1: 'D', q5: 'below', vwapW: 'below', q6: 'yes' }, zones: [{ id: 'z1', type: 'vwapW', price: 4205 }, { id: 'z2', type: 'hvnW', price: 4195 }] },
    open: { tradeId: 't9', status: 'filled', beDone: false },
    trades: [{ id: 't9', time: '21:00', side: 'sell', scenario: 'A', mode: 'broken', zoneId: 'z2', zoneType: 'hvnW', entry: 4193, sl: 4195.4, tp: 4185.8, slDist: 2.4, rrPlanned: 3.33, size: 1, flags: [], ruleCodes: [], tests: {}, exit: null, r: null }] } } };
  await withPage(v1, {}, async ({ page, errors }) => {
    await page.waitForSelector('[data-testid="open-trade"]');                         // có lệnh mở ⇒ mở thẳng Sổ
    const s = await stored(page);
    assert.equal(s.version, 2);
    const n = s.nights[KEY]; assert.equal(n.regime, undefined); assert.equal(n.setup, undefined); assert.equal(n.open, undefined);
    assert.equal(n.card.lockedAt, '19:00'); assert.equal(n.trades.length, 1);
    for (const t of [0, 1, 2, 3]) {
      await page.click(`[data-tier-btn="${t}"]`);
      assert.doesNotMatch(await page.innerText('body'), /⟦/);
    }
    assert.deepEqual(errors, []);
  });
});
