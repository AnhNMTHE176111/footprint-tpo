// Chụp ảnh v2 vào docs/shots/: v2-tang1-dropdown, v2-setup-entry (1366×768), v2-setup-entry-390, v2-so. Chạy: node scripts/shots.mjs
import { launch, openPage, buildState, blockB, ticksAll, KEY } from '../e2e/helpers.mjs';
import { resolve } from 'node:path';
import { mkdirSync } from 'node:fs';

const OUT = resolve(import.meta.dirname, '../docs/shots');
mkdirSync(OUT, { recursive: true });
const browser = await launch();
async function shot(name, state, opts, fn) {
  const o = await openPage(browser, state, opts || {});
  try { if (fn) await fn(o.page); await o.page.waitForTimeout(300); await o.page.screenshot({ path: resolve(OUT, name + '.png') }); console.log('ok', name, o.errors.length ? o.errors : ''); }
  finally { await o.context.close(); }
}
const trade = (id, time, scen, r, exit) => ({ id, time, side: 'buy', scenario: scen, zoneId: 'z1', zoneType: 'vwapW', entry: 4177, sl: 4174.7, tp: 4183.9, rrPlanned: 3, size: 1, slDist: 2.3,
  flags: [], ruleCodes: [], missing: [], ticks: { chk1: true, chk2: true, chk4: true }, exit: exit || null, r: r === undefined ? null : r });
const setup = (n) => {
  n.se.blocks.B = blockB(); n.se.blocks.B.ticks = ticksAll('B'); n.se.common = { longest: true }; n.se.last = 'B'; n.se.touch.B = 2; n.se.n = 2;
  n.se.blocks.A = { side: 'sell', zoneId: 'z2', ticks: { ctx1: true, ctx2: true, chk1: true } }; n.se.touch.A = 1;
};

await shot('v2-tang1-dropdown', buildState('nocard', (n) => { n.card.lockedAt = null; n.card.zones = []; }), {}, async (p) => {
  await p.click('[data-tier-btn="1"]');
  await p.evaluate(() => document.querySelector('.zform').scrollIntoView({ block: 'start' }));
  await p.click('[data-testid="zone-type"]');
  await p.hover('li[data-type="poorLow"]');
});
await shot('v2-setup-entry', buildState('B', (n) => { setup(n); n.se.blocks.A.ticks = { ctx1: true, ctx2: true }; }), {}, async (p) => {
  await p.click('[data-tier-btn="2"]');
  await p.evaluate(() => document.getElementById('blk-B').scrollIntoView({ block: 'start' }));
  await p.evaluate(() => window.scrollBy(0, 40));
});
await shot('v2-setup-entry-390', buildState('B', setup), { viewport: { width: 390, height: 844 } }, async (p) => {
  await p.click('[data-tier-btn="2"]');
  await p.evaluate(() => document.getElementById('blk-B').scrollIntoView({ block: 'start' }));
  await p.evaluate(() => window.scrollBy(0, 150));
});
await shot('v2-so', buildState('B', (n) => {
  n.trades.push(trade('t1', '20:25', 'A', 3, { kind: 'TP', price: 4183.9, at: '20:50' }), trade('t2', '20:48', 'B', -1, { kind: 'SL', price: 4174.7, at: '20:55' }), trade('t3', '21:20', 'B'));
  n.tally = { machine: 2, manual: null, closedAt: null };
}), {}, async (p) => { await p.click('[data-tier-btn="3"]'); await p.click('[data-testid="open-trade"] [data-v="TP"]'); });
await browser.close();
