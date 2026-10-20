// Kiểm thử đầu cuối vòng 3: click bị nuốt sau khi gõ số, hộp vốn lần đầu, QĐ-21, Từ điển, SL sau be, vừa một màn.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { launch, openPage, buildState, seg, fillNum, verdict, KEY } from './helpers.mjs';

const require = createRequire(import.meta.url);
const J = require('../js/journal.js');

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}
const NOW_2024 = '2026-10-13T13:24:00Z';   // 20:24 giờ VN (hè): trước 20:30 ⇒ cỡ ½
const stored = (page) => page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')));

async function walkB(page) {
  await page.click(seg('c1', 'B'));
  await page.click(seg('c3', 'z1'));
  await page.click(seg('c2', 'buy'));
  await page.click(seg('c4', 'same'));
  await page.click(seg('c5', 'near'));
  await page.click('[data-ctl="c7"] [data-v="flat"]');
  await fillNum(page, 'c6', '2');
  await page.waitForSelector('[data-ctl="b3"]');
  await page.click(seg('b1', 'U'));
  await page.click(seg('b2', 'down'));
  await page.click(seg('b3', 'ok'));
  await fillNum(page, 'entry', '4177');
  await fillNum(page, 'sl', '4174.7');
  await page.click(seg('b5', 'right'));
}

test('v3-1 · gõ số rồi bấm nút 3 trạng thái NGAY: ăn ở lần bấm đầu tiên (không cần Tab, không bấm lại)', async () => {
  await withPage(buildState('B'), null, async ({ page, errors }) => {
    await page.click('[data-tier-btn="3"]');
    await page.click(seg('c1', 'B')); await page.click(seg('c3', 'z1')); await page.click(seg('c2', 'buy')); await page.click(seg('c4', 'same')); await page.click(seg('c5', 'near'));
    await page.fill('[data-id="c6"]', '1,8');                 // gõ, KHÔNG rời ô
    await page.click('[data-ctl="c7"] [data-v="flat"]');      // bấm đúng một lần
    await page.waitForSelector('[data-ctl="b3"]');            // đủ Canh ⇒ tự sang Bấm
    const s = (await stored(page)).nights[KEY].setup;
    assert.equal(s.c6, 1.8); assert.deepEqual(s.c7, { dma: 'flat' });
    assert.equal(await verdict(page), 'WAIT');
    assert.deepEqual(errors, []);
  });
});
test('v3-2 · tầng 1: gõ "Giá hiện tại" rồi bấm thẳng sang ô "VWAP tuần": ô nhận chữ gõ; hai số đủ ⇒ tự chọn Trên / Dưới / Sát', async () => {
  await withPage(buildState('B', (n) => { n.card.lockedAt = null; n.card.answers = {}; }), null, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    await page.fill('[data-id="pricenow"]', '4184,5');
    await page.click('[data-id="vwapprice"]');                // chuyển ô bằng chuột, không Tab
    await page.keyboard.type('4181');
    assert.equal(await page.inputValue('[data-id="vwapprice"]'), '4181');
    assert.equal(await page.inputValue('[data-id="pricenow"]'), '4184,5');
    await page.keyboard.press('Tab');
    assert.equal(await page.getAttribute(seg('vwapW', 'above'), 'aria-pressed'), 'true');
    // Tab thẳng giữa hai ô cũng giữ con trỏ
    await page.fill('[data-id="pricenow"]', '4170'); await page.keyboard.press('Tab');
    await page.keyboard.type('4180');
    assert.equal(await page.inputValue('[data-id="vwapprice"]'), '4180');
  });
});

test('v3-3 · lần đầu mở: hộp hỏi vốn và % rủi ro (mặc định 2000 $ · 2 %); "để sau" không hỏi lại; lưu đổi được vốn', async () => {
  await withPage(null, null, async ({ page }) => {
    await page.waitForSelector('[data-testid="capital-dlg"]');
    assert.equal(await page.inputValue('[data-id="cap-dlg"]'), '2000'); assert.equal(await page.inputValue('[data-id="risk-dlg"]'), '2');
    await page.click('[data-testid="cap-later"]');
    assert.equal(await page.locator('[data-testid="capital-dlg"]').count(), 0);
    assert.equal((await stored(page)).settings.sizeAsked, true);
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.equal(await page.locator('[data-testid="capital-dlg"]').count(), 0);
  });
  await withPage(null, null, async ({ page }) => {
    await page.waitForSelector('[data-testid="capital-dlg"]');
    await page.fill('[data-id="cap-dlg"]', '3500'); await page.fill('[data-id="risk-dlg"]', '1,5');
    await page.click('[data-testid="cap-save"]');
    const st = await stored(page);
    assert.equal(st.settings.capital, 3500); assert.equal(st.settings.riskPct, 1.5); assert.equal(st.settings.sizeAsked, true);
  });
});
test('v3-4 · QĐ-21 với cài đặt mặc định: B lúc 20:24, SL 2,3 giá ⇒ ENTRY "1 hợp đồng = cỡ đầy, rủi ro 23 $"; vốn 1000 $ ⇒ KHÔNG VÀO nói SL tối đa, nút Đổi vốn sửa được', async () => {
  const st = buildState('B'); st.settings.capital = 1000;
  await withPage(st, { now: NOW_2024 }, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    assert.equal(await verdict(page), 'NO');
    const t = await page.textContent('[data-testid="verdict"]');
    assert.match(t, /SL tối đa 2,0 giá/); assert.match(t, /vốn 1000 \$/);
    await page.click('[data-testid="btn-capital"]');
    await page.fill('[data-id="cap-dlg"]', '2000'); await page.click('[data-testid="cap-save"]');
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="entry-text"]'), /1 hợp đồng = cỡ đầy, rủi ro 23 \$/);
  });
  await withPage(buildState('B'), { now: NOW_2024 }, async ({ page }) => {   // vốn mặc định 2000 $, không đổi gì
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="entry-text"]'), /1 hợp đồng = cỡ đầy, rủi ro 23 \$/);
  });
});

test('v3-5 · Từ điển: mở ở đầu, có ô tìm; "?" của câu hỏi mở đúng mục (cuộn + tô sáng); đủ mục R và hình dạng profile', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-testid="glossary-btn"]');
    const top = await page.evaluate(() => { const b = document.querySelector('.glossarybox'); const m = document.querySelector('.modal'); return [b.scrollTop, m.scrollTop]; });
    assert.deepEqual(top, [0, 0]);
    assert.equal(await page.evaluate(() => document.activeElement && document.activeElement.getAttribute('data-testid')), 'glossary-search');
    await page.fill('[data-testid="glossary-search"]', 'bong');
    const shown = await page.$$eval('.glossary dt:not([hidden])', (els) => els.map((e) => e.textContent));
    assert.ok(shown.includes('bong bóng') && shown.length >= 1 && shown.length < 10, shown.join('|'));
    await page.fill('[data-testid="glossary-search"]', 'xyzxyz');
    assert.equal(await page.locator('.glossarybox p.muted:not([hidden])').count() >= 1, true);
    await page.keyboard.press('Escape');
    // từ "?" của Q2a (Đỉnh hôm qua) ⇒ mục "mồi"
    await page.click('[data-tier-btn="1"]'); await page.click('[data-ctl="q2top"] .help'); await page.click('[data-ctl="q2top"] .pop .glossbtn');
    await page.waitForSelector('.glossary dt.hl');
    assert.equal(await page.textContent('.glossary dt.hl'), 'mồi');
    const vis = await page.evaluate(() => { const r = document.querySelector('.glossary dt.hl').getBoundingClientRect(); return r.top >= 0 && r.bottom <= innerHeight; });
    assert.equal(vis, true);
    await page.fill('[data-testid="glossary-search"]', '');
    const all = await page.$$eval('.glossary dt', (els) => els.map((e) => e.textContent));
    for (const w of ['R', 'hình dạng profile (D, P, b, B, thin, chữ nhật)', 'mồi', 'trap (bẫy)', 'bong bóng', 'DMA']) assert.ok(all.includes(w), w);
    const sorted = [...all].sort((a, b) => a.localeCompare(b, 'vi'));
    assert.deepEqual(all, sorted);
  });
});

test('v3-6 · A thiếu hướng chế độ ⇒ CHỜ "Chọn hướng ở tầng 2", bấm vào dẫn về tầng 2; bước 1 bị khóa tới khi chọn hướng và cạnh', async () => {
  await withPage(buildState('A', (n) => { n.regime = { mode: 'thin', thinDir: null, breakout: { dir: null, edgeZoneId: null, at: null, nth: 1, step1: false, step2: false }, longestBarUntil: null, log: [] }; }), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await page.click(seg('c1', 'A'));
    assert.equal(await verdict(page), 'WAIT');
    assert.match(await page.textContent('[data-testid="verdict"]'), /Chọn hướng ở tầng 2/);
    await page.click('[data-code="WAIT_REGIME_DIR"]');
    await page.waitForSelector('[data-tier="2"]');
    await page.click('.seg.big [data-v="broken"]');
    await page.click(seg('boStep1', 'true'), { force: true });
    assert.equal(await page.getAttribute(seg('boStep1', 'true'), 'aria-pressed'), 'false');
    await page.click(seg('boDir', 'down')); await page.click(seg('boEdge', 'z2'));
    await page.click(seg('boStep1', 'true'));
    assert.equal(await page.getAttribute(seg('boStep1', 'true'), 'aria-pressed'), 'true');
  });
});

test('v3-7 · dời be rồi "Chạm SL": giá thoát mặc định = giá vào, R = 0, chuỗi SL không tăng; "Giá hiện tại" còn sau khi tải lại', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    await page.click('[data-testid="btn-entry"]'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await fillNum(page, 'curprice', '4181');
    await page.reload(); await page.waitForSelector('[data-tier="4"]');
    assert.equal(await page.inputValue('[data-id="curprice"]'), '4181');
    await page.check('.beline input[type="checkbox"]');
    await page.click('[data-testid="btn-be"]');
    assert.match(await page.textContent('.seg.close'), /Chạm SL \(đã ở hòa vốn\)/);
    await page.click('.seg.close [data-v="SL"]');
    assert.equal(await page.inputValue('[data-id="exitprice"]'), '4177');
    await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForSelector('[data-tier="5"]');
    const n = (await stored(page)).nights[KEY];
    assert.equal(n.trades[0].r, 0); assert.equal(n.trades[0].exit.beStop, true);
    assert.match(await page.textContent('.statusbar'), /SL liên tiếp 0 trên 3/);
  });
});

test('v3-8 · kế hoạch ngược bias: cảnh báo vàng hiện ngay khi gõ, sát nút chốt; sao chép vùng từ đêm trước', async () => {
  const st = buildState('B', (n) => { n.card.lockedAt = null; n.card.zones = []; n.card.answers = { q1: 'D', q5: 'above', vwapW: 'above', q6: 'yes' }; });
  const prev = J.newNight('2026-10-12'); prev.card.lockedAt = '19:00'; prev.card.answers = { q1w: 'P' };
  prev.card.zones = [{ id: 'z1', type: 'vwapW', price: 4181 }, { id: 'z2', type: 'valEu', price: 4182 }, { id: 'z3', type: 'hvn3w', price: 4200 }];
  st.nights['2026-10-12'] = prev;
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-tier-btn="1"]');
    assert.equal(await page.locator('[data-testid="plan-conflict"]').count(), 0);
    await page.fill('.plans .field.txt >> nth=0', 'sell ở VAH Âu');        // KHÔNG rời ô
    await page.waitForSelector('[data-testid="plan-conflict"]');
    const adj = await page.evaluate(() => { const b = document.querySelector('[data-testid="plan-conflict"]'); const n = b.parentElement.nextElementSibling; return n && n.getAttribute('data-testid'); });
    assert.equal(adj, 'lock-card');
    await page.click('[data-testid="copy-prev"]');
    assert.equal(await page.locator('[data-zone]').count(), 2);
    const n = (await stored(page)).nights[KEY];
    assert.equal(n.card.answers.q1w, 'P'); assert.deepEqual(n.card.zones.map((z) => z.type), ['vwapW', 'hvn3w']);
  });
});

test('v3-9 · bước Bấm đã điền đủ vừa một màn 1366×768, ở 21:30 và ở 20:24 (thanh trạng thái gọn)', async () => {
  for (const now of [undefined, NOW_2024]) {
    await withPage(buildState('B'), now ? { now } : null, async ({ page }) => {
      await page.click('[data-tier-btn="3"]'); await walkB(page);
      assert.equal(await verdict(page), 'ENTRY');
      // chờ ResizeObserver cập nhật --vbar-h (đệm đáy theo chiều cao thanh phán quyết) rồi mới đo
      await page.waitForFunction(() => parseInt(getComputedStyle(document.documentElement).getPropertyValue('--vbar-h'), 10) === document.getElementById('verdict').offsetHeight);
      const [sh, ih, sbh] = await page.evaluate(() => [document.documentElement.scrollHeight, window.innerHeight, document.getElementById('status').offsetHeight]);
      const parts = await page.evaluate(() => ['#status', '#tiers', '#main', '.vbar', '.vnotes'].map((s) => { const e = document.querySelector(s); return s + '=' + (e ? e.offsetHeight : '-'); }).join(' ') + ' pad=' + getComputedStyle(document.getElementById('app')).paddingBottom);
      assert.ok(sh <= ih, `scrollHeight ${sh} > innerHeight ${ih} (now=${now}) ${parts}`);
      assert.ok(sbh <= 90, 'thanh trạng thái ' + sbh);
    });
  }
});

test('v3-10 · 20:24: thanh trên không in "Cú phá đáng tin" cạnh cảnh báo trước 20:30; chữ ngắn, "?" mở QĐ-19', async () => {
  await withPage(buildState('B'), { now: NOW_2024 }, async ({ page }) => {
    const bar = await page.textContent('.statusbar');
    assert.ok(!/Cú phá đáng tin/.test(bar), bar);
    assert.match(bar, /trước 20:30 · cỡ ½/);
    await page.click('.statusbar .help');
    assert.match(await page.textContent('.statusbar .pop'), /quyết định của công cụ, chưa đo/);
  });
  const wst = buildState('B'); wst.nights['2026-11-02'] = wst.nights[KEY];
  await withPage(wst, { now: '2026-11-02T13:24:00Z' }, async ({ page }) => {   // mùa đông Mỹ: 20:24 VN vẫn trước 21:30
    assert.match(await page.textContent('.statusbar'), /trước 21:30 · cỡ ½/);
  });
});

test('v3-11 · điện thoại 360 px: chip khung giờ cấm không bị nút "Thẻ phiên" đè, không bị cắt ngang', async () => {
  await withPage(buildState('B'), { viewport: { width: 360, height: 740 } }, async ({ page }) => {
    const r = await page.evaluate(() => {
      const t = document.getElementById('cardtoggle').getBoundingClientRect();
      const bar = document.querySelector('.statusbar');
      let overlap = false, clipped = false;
      bar.querySelectorAll('.chip').forEach((c) => {
        const b = c.getBoundingClientRect();
        if (b.width === 0) return;
        if (b.right > t.left + 1 && b.left < t.right && b.bottom > t.top && b.top < t.bottom) overlap = true;
        if (b.right > innerWidth + 1) clipped = true;
      });
      return { overlap, clipped, scrollW: document.documentElement.scrollWidth, cw: bar.scrollWidth, bw: bar.clientWidth };
    });
    assert.equal(r.overlap, false, JSON.stringify(r)); assert.equal(r.clipped, false); assert.ok(r.scrollW <= 360, JSON.stringify(r));
    assert.ok(r.cw <= r.bw + 1, JSON.stringify(r));
  });
});

test('v3-12 · lệnh qua đêm bằng giao diện: đêm sau tải lại vẫn về tầng 4, tầng 3 khóa; đóng lệnh ghi vào ĐÊM CŨ của lệnh', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    await page.click('[data-testid="btn-entry"]'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await page.clock.setFixedTime(new Date('2026-10-14T14:30:00Z'));      // đêm 14/10, lệnh vẫn mở từ đêm 13/10
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.equal(await page.locator('[data-tier="4"]').count(), 1);
    assert.match(await page.textContent('.statusbar'), /Lệnh mở 1 trên 1/);
    assert.equal(await page.getAttribute('[data-tier-btn="3"]', 'aria-disabled'), 'true');
    await page.click('.seg.close [data-v="TP"]'); await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForSelector('[data-tier="5"]');
    const st = await stored(page);
    assert.equal(st.nights[KEY].trades[0].exit.kind, 'TP');
    assert.equal(st.nights[KEY].open, null);
    assert.equal(!!(st.nights['2026-10-14'] && st.nights['2026-10-14'].trades.length), false);
  });
});
