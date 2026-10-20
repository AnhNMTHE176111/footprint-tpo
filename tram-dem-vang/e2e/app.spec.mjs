// Kiểm thử đầu cuối (Playwright, chromium, mở bằng file://). Chạy: npm run e2e
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { launch, openPage, buildState, seg, fillNum, verdict, openCanh, ROOT, KEY } from './helpers.mjs';

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}

// QĐ-25: Canh (nhìn được trước khi nến xác nhận đóng) gồm cả B1, B2 và cực trị; Bấm tối đa 3 thao tác: nến xác nhận, giá vào, SL
async function walkA(page) {
  let ops = 0;
  const click = async (sel) => { await page.click(sel); ops++; };
  await click(seg('c1', 'A'));                 // 1 kịch bản (vùng và hướng tự điền)
  await click(seg('c4', 'none'));              // 2 bong bóng
  await click(seg('c5', 'near'));              // 3 cách vùng
  await fillNum(page, 'c6', '2,0'); ops++;     // 4 nến M1 cao nhất
  await click(seg('b1', 'U'));                 // 5 nhịp hồi U  ⇒ Canh đủ, tự gập
  const canh = ops;
  await click(seg('b3', 'ok'));                // 1
  await fillNum(page, 'entry', '4193.0'); ops++;   // 2 (nhận dấu chấm)
  await fillNum(page, 'sl', '4195,4'); ops++;      // 3 (TP gợi ý sẵn, không tính; B5 máy tự kiểm)
  return { canh, bam: ops - canh };
}
async function walkB(page) {
  let ops = 0;
  const click = async (sel) => { await page.click(sel); ops++; };
  await click(seg('c1', 'B'));                 // 1
  await click(seg('c3', 'z1'));                // 2 vùng
  await click(seg('c2', 'buy'));               // 3 hướng
  await click(seg('c4', 'same'));              // 4
  await click(seg('c5', 'near'));              // 5
  await page.click('[data-ctl="c7"] [data-v="flat"]'); ops++;   // 6 DMA
  await fillNum(page, 'c6', '2'); ops++;       // 7
  await click(seg('b1', 'U'));                 // 8
  await click(seg('b2', 'down'));              // 9
  await fillNum(page, 'ext', '4175'); ops++;   // 10 cực trị cụm ⇒ Canh đủ, tự gập
  const canh = ops;
  await click(seg('b3', 'ok'));                // 1
  await fillNum(page, 'entry', '4177'); ops++; // 2
  await fillNum(page, 'sl', '4174.7'); ops++;  // 3
  return { canh, bam: ops - canh };
}

async function enterAndClose(page, kind) {
  await page.click('[data-testid="btn-entry"]');
  await page.click('[data-testid="enter-confirm"]');
  await page.waitForSelector('[data-tier="4"]');
  await page.click('.seg.close [data-v="' + kind + '"]');
  await page.click('[data-testid="btn-close-confirm"]');
  await page.waitForSelector('[data-tier="5"]');
}

test('1a · đường đi tới ENTRY và ghi sổ — kịch bản A (5 thao tác Canh + 3 Bấm)', async () => {
  await withPage(buildState('A'), null, async ({ page, errors }) => {
    const n = await walkA(page);
    assert.deepEqual(n, { canh: 5, bam: 3 });
    assert.equal(await verdict(page), 'ENTRY');
    const text = await page.textContent('[data-testid="entry-text"]');
    assert.match(text, /ENTRY SELL 4193,0 · SL 4195,4 \(2,4 giá\) · TP 4185,8 · 1:3 · cỡ đủ/);
    await enterAndClose(page, 'TP');
    const row = await page.textContent('[data-testid="journal"] tbody tr');
    assert.match(row, /phá hồi/); assert.match(row, /vừa phá/); assert.match(row, /U · bb không có · Δ nến mạnh · cạnh/); assert.match(row, /2,4/); assert.match(row, /\+3/);
    assert.match(await page.textContent('.jfoot'), /Máy cộng: \+3 R/);
    assert.deepEqual(errors, []);
  });
});

test('1b · đường đi tới ENTRY và ghi sổ — kịch bản B (10 thao tác Canh + 3 Bấm)', async () => {
  await withPage(buildState('B'), null, async ({ page, errors }) => {
    const n = await walkB(page);
    assert.deepEqual(n, { canh: 10, bam: 3 });
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="entry-text"]'), /ENTRY BUY 4177,0 · SL 4174,7 \(2,3 giá\) · TP 4183,9 · 1:3 · cỡ đủ/);
    await enterAndClose(page, 'SL');
    const row = await page.textContent('[data-testid="journal"] tbody tr');
    assert.match(row, /hấp thụ/); assert.match(row, /cân bằng/); assert.match(row, /U · bb -49 giữ|U · bb không có|U · bb giữ/); assert.match(row, /-1/);
    assert.deepEqual(errors, []);
  });
});

test('2 · tầng 3 khóa khi chưa chốt thẻ / bias CHỜ / có lệnh', async () => {
  await withPage(buildState('nocard'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]', { force: true });
    assert.equal(await page.locator('[data-tier="3"]').count(), 0);
    assert.match(await page.textContent('#toast'), /Chưa chốt thẻ phiên/);
  });
  await withPage(buildState('wait'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]', { force: true });
    assert.equal(await page.locator('[data-tier="3"]').count(), 0);
    assert.match(await page.textContent('#toast'), /Bias đang CHỜ/);
    assert.match(await page.textContent('[data-testid="card-bias"]'), /CHỜ/);
  });
  await withPage(buildState('B'), null, async ({ page }) => {
    await walkB(page);
    await page.click('[data-testid="btn-entry"]'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await page.click('[data-tier-btn="3"]', { force: true });
    assert.equal(await page.locator('[data-tier="4"]').count(), 1);          // vẫn ở tầng 4
    assert.match(await page.textContent('#toast'), /Đang có lệnh mở/);
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.equal(await page.locator('[data-tier="4"]').count(), 1);          // tải lại vẫn thấy lệnh mở
  });
});

test('3 · nhịp hồi V ⇒ KHÔNG VÀO màu đỏ', async () => {
  await withPage(buildState('A'), null, async ({ page }) => {
    await walkA(page);
    await openCanh(page); await page.click(seg('b1', 'V'));
    assert.equal(await verdict(page), 'NO');
    const bg = await page.$eval('[data-testid="verdict"]', (e) => getComputedStyle(e).backgroundColor);
    assert.equal(bg, 'rgb(214, 60, 66)');
    assert.match(await page.textContent('[data-testid="verdict"]'), /KHÔNG VÀO — Nhịp hồi hình V/);
  });
});

test('4 · tải lại giữ nguyên lựa chọn', async () => {
  await withPage(buildState('A'), null, async ({ page }) => {
    await page.click(seg('c1', 'A')); await page.click(seg('c4', 'oppBroken'));
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.equal(await page.getAttribute(seg('c1', 'A'), 'aria-pressed'), 'true');
    assert.equal(await page.getAttribute(seg('c4', 'oppBroken'), 'aria-pressed'), 'true');
    const saved = await page.evaluate(() => JSON.parse(localStorage.getItem('tdv.v1')).nights['2026-10-13'].setup.c4);
    assert.equal(saved, 'oppBroken');
  });
});

test('5 · mở bằng file:// không lỗi console ở mọi tầng, không thiếu chữ', async () => {
  await withPage(buildState('A', (n) => { n.setup = { scenario: 'A' }; }), null, async ({ page, errors }) => {
    for (const t of [0, 1, 2, 3, 5]) {
      await page.click(`[data-tier-btn="${t}"]`);
      await page.waitForSelector(`[data-tier="${t}"]`);
      const body = await page.textContent('body');
      assert.ok(!body.includes('⟦'), 'thiếu chữ ở tầng ' + t + ': ' + body.match(/⟦\w+⟧/));
    }
    assert.deepEqual(errors, []);
    assert.equal(await page.evaluate(() => location.protocol), 'file:');
  });
});

test('6 · 360 px không tràn ngang ở mọi tầng', async () => {
  const st = buildState('A', (n) => { n.setup = { scenario: 'A', c4: 'none', c5: 'near', c6: 2, b1: 'U', b3: 'ok', slPos: 'right', calc: { entry: 4193, sl: 4195.4 } }; });
  await withPage(st, { viewport: { width: 360, height: 740 } }, async ({ page }) => {
    const over = async (label) => {
      const [sw, iw] = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
      assert.ok(sw <= iw + 1, `${label}: scrollWidth ${sw} > ${iw}`);
    };
    for (const t of [0, 1, 2, 3, 5]) { await page.click(`[data-tier-btn="${t}"]`); await page.waitForSelector(`[data-tier="${t}"]`); await over('tầng ' + t); }
    await page.click('[data-tier-btn="3"]'); await page.click('[data-testid="btn-entry"]'); await over('hộp vào lệnh');
    await page.click('[data-testid="enter-confirm"]'); await page.waitForSelector('[data-tier="4"]'); await over('tầng 4');
    await page.click('#cardtoggle'); await over('ngăn thẻ phiên');
  });
});

test('7 · phím tắt chạy ở tầng 3 và tắt khi đang gõ vào ô nhập', async () => {
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await page.keyboard.press('2');
    assert.equal(await page.getAttribute(seg('c1', 'B'), 'aria-pressed'), 'true');
    await page.keyboard.press('b');
    assert.equal(await page.getAttribute(seg('c2', 'buy'), 'aria-pressed'), 'true');
    await page.keyboard.press('s');
    assert.equal(await page.getAttribute(seg('c2', 'sell'), 'aria-pressed'), 'true');
    // đang gõ vào ô số: phím 1 và n là chữ, không phải phím tắt
    await page.focus('[data-id="c6"]');
    await page.keyboard.type('1n');
    assert.equal(await page.inputValue('[data-id="c6"]'), '1n');
    assert.equal(await page.getAttribute(seg('c1', 'B'), 'aria-pressed'), 'true');
    await page.keyboard.press('Escape');
    assert.equal(await page.evaluate(() => document.activeElement.tagName), 'BODY');
    await page.keyboard.press('n');                               // kèo mới: GIỮ C1–C3 và C6 (QĐ-25), xóa câu quan sát
    assert.equal(await page.getAttribute(seg('c1', 'B'), 'aria-pressed'), 'true');
    assert.equal(await page.getAttribute(seg('c2', 'sell'), 'aria-pressed'), 'true');
    await page.click('[data-testid="clear-setup"]');              // Xóa hết
    assert.equal(await page.getAttribute(seg('c1', 'B'), 'aria-pressed'), 'false');
    await page.keyboard.press('1');                               // A đang tắt (cân bằng) ⇒ báo lý do, không chọn
    assert.equal(await page.getAttribute(seg('c1', 'A'), 'aria-pressed'), 'false');
    assert.match(await page.textContent('#toast'), /Chưa có cú phá/);
    await page.keyboard.press('?');
    assert.match(await page.textContent('.modal'), /Phím tắt/);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.modal').count(), 0);
  });
});

test('8 · "Tôi vẫn vào (phá luật)" hai lần ⇒ TẮT MÁY', async () => {
  await withPage(buildState('A'), null, async ({ page }) => {
    await walkA(page);
    await openCanh(page); await page.click(seg('b1', 'V'));       // V ⇒ KHÔNG VÀO
    assert.equal(await verdict(page), 'NO');
    for (let i = 0; i < 2; i++) {
      if (i > 0) { // lệnh đầu đã ghi ⇒ tầng 3 về "Kèo mới"; làm lại kèo
        await page.click('[data-tier-btn="3"]'); await page.waitForSelector(seg('c1', 'A'));
        assert.equal(await page.getAttribute(seg('c1', 'A'), 'aria-pressed'), 'false');
        await walkA(page); await openCanh(page); await page.click(seg('b1', 'V'));
        assert.equal(await verdict(page), 'NO');
      }
      await page.click('[data-testid="btn-force"]');
      await page.click('[data-testid="dlg-ok"]');
      await page.waitForSelector('[data-tier="4"]');
      assert.match(await page.textContent('[data-testid="clock"]'), /21:30 VN/);
      await page.click('.seg.close [data-v="SL"]');
      await page.click('[data-testid="btn-close-confirm"]');
      await page.waitForSelector('[data-tier="5"]');
    }
    assert.match(await page.textContent('[data-testid="journal"]'), /⚠ dòng/);
    await page.click('[data-tier-btn="3"]');
    await page.waitForSelector('[data-testid="verdict"]');
    assert.equal(await verdict(page), 'OFF');
    assert.match(await page.textContent('[data-testid="verdict"]'), /TẮT MÁY/);
    assert.match(await page.textContent('.statusbar'), /Phá luật 2 trên 2/);
    const bg = await page.$eval('[data-testid="verdict"]', (e) => getComputedStyle(e).backgroundColor);
    assert.equal(bg, 'rgb(0, 0, 0)');
  });
});

test('9b · chế độ chỉ xem: ENTRY xám, ghi kèo luyện mắt, không cộng phá luật / chuỗi SL', async () => {
  await withPage(buildState('A', (n) => { n.t0.alert = false; }), null, async ({ page, errors }) => {
    await walkA(page);
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="entry-text"]'), /ENTRY \(chỉ xem\) SELL/);
    const bg = await page.$eval('[data-testid="verdict"]', (e) => getComputedStyle(e).backgroundColor);
    assert.equal(bg, 'rgb(107, 114, 128)');
    await page.click('[data-testid="btn-paper"]');
    await page.waitForSelector('[data-tier="4"]');
    assert.match(await page.textContent('.statusbar'), /Lệnh mở 1 trên 1 \(luyện mắt\)/);
    await page.click('.seg.close [data-v="SL"]');
    await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForSelector('[data-tier="5"]');
    assert.match(await page.textContent('[data-testid="journal"] tbody tr'), /phá hồi \(luyện mắt\)/);
    assert.match(await page.textContent('.statusbar'), /SL liên tiếp 0 trên 3/);
    assert.match(await page.textContent('.jfoot'), /Máy cộng: 0 R/);
    assert.deepEqual(errors, []);
  });
});

test('9 · chụp ảnh: tầng 1, tầng 3 ENTRY, điện thoại 360 px', async () => {
  const dir = resolve(ROOT, 'docs', 'shots'); mkdirSync(dir, { recursive: true });
  await withPage(buildState('B', (n) => { n.card.plan1 = 'Nếu giá chạm VWAP tuần thì tìm hấp thụ buy'; n.card.zones.push({ id: 'z4', type: 'highY', price: 4190 }); }), null, async ({ page }) => {
    await page.click('[data-tier-btn="1"]'); await page.waitForSelector('[data-tier="1"]');
    await page.screenshot({ path: resolve(dir, 'tang1-vung.png'), fullPage: false });
    await page.click('[data-tier-btn="3"]');
    await walkB(page);
    assert.equal(await verdict(page), 'ENTRY');
    await page.screenshot({ path: resolve(dir, 'tang3-entry.png'), fullPage: false });
  });
  await withPage(buildState('B'), { viewport: { width: 360, height: 740 } }, async ({ page }) => {
    await page.click('[data-tier-btn="3"]');
    await walkB(page);
    assert.equal(await verdict(page), 'ENTRY');
    await page.screenshot({ path: resolve(dir, 'dien-thoai-360.png'), fullPage: false });
  });
});
