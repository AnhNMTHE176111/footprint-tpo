// Kiểm thử đầu cuối vòng 2: đi từ dữ liệu TRỐNG bằng giao diện thật (không nạp sẵn), và từng lỗi đã sửa.
import test from 'node:test';
import assert from 'node:assert/strict';
import { launch, openPage, buildState, seg, fillNum, verdict } from './helpers.mjs';

let browser;
test.before(async () => { browser = await launch(); });
test.after(async () => { await browser.close(); });

async function withPage(state, opts, fn) {
  const o = await openPage(browser, state, opts);
  try { await fn(o); } finally { await o.context.close(); }
}

async function walkA(page) {
  await page.click(seg('c1', 'A'));
  await page.click(seg('c4', 'none'));
  await page.click(seg('c5', 'near'));
  await fillNum(page, 'c6', '2,0');
  await page.waitForSelector('[data-ctl="b3"]');
  await page.click(seg('b1', 'U'));
  await page.click(seg('b3', 'ok'));
  await fillNum(page, 'entry', '4193.0');
  await fillNum(page, 'sl', '4195,4');
  await page.click(seg('b5', 'right'));
}
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
async function addZone(page, type, price) {
  await page.selectOption('.zform select', type);
  await page.fill('[data-id="zprice"]', price);
  await page.press('[data-id="zprice"]', 'Tab');
  await page.click('.zform .btn.primary');
}

test('v2-1 · từ dữ liệu trống: tầng 0 → 1 → 2 (cú phá mới) → ENTRY → ghi lệnh → tải lại về Kèo mới', async () => {
  await withPage(null, null, async ({ page, errors }) => {
    // lần đầu mở: hộp hỏi vốn (QĐ-21), bấm "Lưu" với mặc định 2000 $ · 2 %
    await page.waitForSelector('[data-testid="capital-dlg"]');
    await page.click('[data-testid="cap-save"]');
    // tầng 0
    await page.click('[data-ctl="t0alert"] [data-v="true"]');
    await page.click('button:has-text("Xong tầng 0")');
    await page.waitForSelector('[data-tier="1"]');
    // tầng 1: tám câu hỏi có số, VWAP tuần chọn bằng hai ô số
    assert.match(await page.textContent('[data-ctl="q1"] .ctl-label'), /^Q1 · Hình dạng profile hôm qua/);
    assert.equal(await page.locator('[data-ctl="q6"]').count(), 0);   // QĐ-23: Q6 không còn hỏi
    await page.click(seg('q1', 'D')); await page.click(seg('q5', 'below'));
    await fillNum(page, 'pricenow', '4200'); await fillNum(page, 'vwapprice', '4210');
    assert.equal(await page.getAttribute(seg('vwapW', 'below'), 'aria-pressed'), 'true');
    assert.match(await page.textContent('[data-testid="bias-big"]'), /SELL/);
    await addZone(page, 'vwapW', '4205'); await addZone(page, 'hvnW', '4195'); await addZone(page, 'valEu', '4185'); await addZone(page, 'vahEu', '4199');
    assert.equal(await page.locator('[data-zone]').count(), 4);
    assert.equal(await page.inputValue('[data-id="zprice"]'), '');   // ô giá về rỗng sau khi thêm (REVIEW mục 21)
    // kế hoạch ngược bias: chỉ cảnh báo, vẫn chốt được
    await page.click('.plans summary');
    const plan1 = page.locator('[data-testid="plan-note"]');
    await plan1.fill('buy ở VWAP tuần'); await plan1.press('Tab');
    await page.click('[data-testid="lock-card"]');
    await page.waitForSelector('[data-tier="2"]');
    // tầng 2: Vừa phá chưa công nhận ⇒ hiệu lực cân bằng; công nhận 2 bước ⇒ vừa phá
    await page.click('.seg.big [data-v="broken"]');
    assert.match(await page.textContent('[data-testid="regime-eff"]'), /cân bằng/);
    await page.click(seg('boDir', 'down')); await page.click(seg('boEdge', 'z2'));
    await page.click(seg('boStep1', 'true')); await page.click(seg('boStep2', 'true'));
    assert.match(await page.textContent('[data-testid="regime-eff"]'), /vừa phá · xuống/);
    // lỗi REVIEW mục 1: về Cân bằng rồi Vừa phá lại ⇒ phải công nhận lại từ đầu
    await page.click('.seg.big [data-v="balanced"]'); await page.click('.seg.big [data-v="broken"]');
    assert.match(await page.textContent('[data-testid="regime-eff"]'), /cân bằng/);
    await page.click(seg('boDir', 'down')); await page.click(seg('boEdge', 'z2'));
    await page.click(seg('boStep1', 'true')); await page.click(seg('boStep2', 'true'));
    assert.match(await page.textContent('[data-testid="regime-eff"]'), /vừa phá · xuống/);
    // tầng 3
    await page.click('button:has-text("Sang tầng 3")');
    await page.waitForSelector('[data-ctl="c1"]');
    await walkA(page);
    assert.equal(await verdict(page), 'ENTRY');
    assert.match(await page.textContent('[data-testid="entry-text"]'), /1 hợp đồng/);
    await page.click('[data-testid="btn-entry"]'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await page.reload(); await page.waitForSelector('#main .tier');
    assert.equal(await page.locator('[data-tier="4"]').count(), 1);
    await page.click('.seg.close [data-v="TP"]'); await page.click('[data-testid="btn-close-confirm"]');
    await page.waitForSelector('[data-tier="5"]');
    // USER-TEST mục 3: lệnh đã ghi xong, tải lại không hiện ENTRY cũ
    await page.reload(); await page.waitForSelector('#main .tier');
    await page.click('[data-tier-btn="3"]'); await page.waitForSelector('[data-ctl="c1"]');
    assert.equal(await page.locator('[data-testid="verdict"][data-verdict="ENTRY"]').count(), 0);
    assert.equal(await page.getAttribute(seg('c1', 'A'), 'aria-pressed'), 'false');
    assert.deepEqual(errors, []);
  });
});

test('v2-2 · điện thoại 360 px: mở và đóng ngăn thẻ phiên (nút, ✕, chạm ngoài, Esc); hai thanh dính ≤ 35 % màn hình', async () => {
  await withPage(buildState('B'), { viewport: { width: 360, height: 740 } }, async ({ page }) => {
    const open = () => page.evaluate(() => document.getElementById('card').classList.contains('open'));
    await page.click('#cardtoggle'); assert.equal(await open(), true);
    await page.click('#cardtoggle'); assert.equal(await open(), false);
    await page.click('#cardtoggle'); await page.click('.cardclose'); assert.equal(await open(), false);
    await page.click('#cardtoggle'); await page.mouse.click(10, 400); assert.equal(await open(), false);
    await page.click('#cardtoggle'); await page.keyboard.press('Escape'); assert.equal(await open(), false);
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    const [sh, vh, ih] = await page.evaluate(() => [document.getElementById('status').offsetHeight, document.getElementById('verdict').offsetHeight, window.innerHeight]);
    assert.ok((sh + vh) / ih <= 0.35, `thanh dính ${sh}+${vh} / ${ih}`);
  });
});

test('v2-3 · Từ điển mở từ thanh trạng thái và từ nút "?"; 0 hợp đồng ⇒ KHÔNG VÀO (NO_SIZE_ZERO)', async () => {
  const st = buildState('B'); st.settings.capital = 500;
  await withPage(st, null, async ({ page }) => {
    await page.click('[data-testid="glossary-btn"]');
    const g = await page.textContent('[data-testid="glossary"]');
    for (const w of ['bias', 'naked POC', 'tail thật', 'be (hòa vốn)', 'acceptance']) assert.ok(g.includes(w), w);
    await page.keyboard.press('Escape');
    await page.click('[data-tier-btn="1"]'); await page.click('[data-ctl="q1"] .help'); await page.click('[data-ctl="q1"] .pop .glossbtn');
    assert.equal(await page.locator('[data-testid="glossary"]').count(), 1);
    await page.keyboard.press('Escape');
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    assert.equal(await verdict(page), 'NO');
    assert.match(await page.textContent('[data-testid="verdict"]'), /chưa đủ 1 hợp đồng/);
  });
});

test('v2-4 · ban ngày thanh trên không vàng; "Về hòa" chỉ chọn được sau khi dời SL về hòa vốn', async () => {
  await withPage(buildState('B'), { now: '2026-10-13T03:00:00Z' }, async ({ page }) => {   // 10:00 giờ VN
    const cls = await page.getAttribute('.statusbar', 'class');
    assert.ok(!/warn|bad/.test(cls), cls);
  });
  await withPage(buildState('B'), null, async ({ page }) => {
    await page.click('[data-tier-btn="3"]'); await walkB(page);
    await page.click('[data-testid="btn-entry"]'); await page.click('[data-testid="enter-confirm"]');
    await page.waitForSelector('[data-tier="4"]');
    await page.click('.seg.close [data-v="BE"]', { force: true });
    assert.equal(await page.getAttribute('.seg.close [data-v="BE"]', 'aria-pressed'), 'false');
  });
});
