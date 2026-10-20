// Chụp ảnh vòng 5 vào docs/shots/: tang0-tin, tang0-moi, tang1-moi, tang2-moi, tang3-moi, tu-dien. Chạy: node scripts/shots.mjs
import { launch, openPage, buildState, seg, fillNum, KEY } from '../e2e/helpers.mjs';
import { resolve } from 'node:path';
import { mkdirSync } from 'node:fs';

const OUT = resolve(import.meta.dirname, '../docs/shots');
mkdirSync(OUT, { recursive: true });
const FEED = {
  fetchedAt: '2026-10-13T11:20:00.000Z',
  events: [
    { title: 'CPI m/m', country: 'USD', date: '2026-10-13T08:30:00-04:00', impact: 'High', forecast: '0.3%', previous: '0.4%', actual: '' },
    { title: 'Core CPI m/m', country: 'USD', date: '2026-10-13T08:30:00-04:00', impact: 'High', forecast: '0.3%', previous: '0.3%', actual: '' },
    { title: 'ECB Press Conference', country: 'EUR', date: '2026-10-13T08:45:00-04:00', impact: 'High', forecast: '', previous: '', actual: '' },
    { title: 'ISM Services PMI', country: 'USD', date: '2026-10-13T10:00:00-04:00', impact: 'Medium', forecast: '52.0', previous: '51.6', actual: '' },
    { title: 'FOMC Statement', country: 'USD', date: '2026-10-13T14:00:00-04:00', impact: 'High', forecast: '', previous: '', actual: '' }
  ]
};
const browser = await launch();
async function shot(name, state, opts, fn) {
  const o = await openPage(browser, state, Object.assign({ feed: FEED, now: '2026-10-13T11:30:00Z' }, opts || {}));
  try { if (fn) await fn(o.page); await o.page.waitForTimeout(250); await o.page.screenshot({ path: resolve(OUT, name + '.png') }); console.log('ok', name, o.errors.length ? o.errors : ''); }
  finally { await o.context.close(); }
}
await shot('tang0-tin', buildState('B', (n) => { n.t0.touched = false; n.t0.alert = null; }), null, (p) => p.click('[data-tier-btn="0"]'));
await shot('tang0-moi', buildState('B', (n) => { n.t0.touched = false; n.t0.alert = true; }), null, (p) => p.click('[data-tier-btn="0"]'));
await shot('tang1-moi', buildState('B', (n) => { n.card.lockedAt = null; n.card.zones = n.card.zones.slice(); n.card.zones.push({ id: 'z4', type: 'highY', price: 4210 }); n.card.answers.q2top = 'tail'; }), { now: '2026-10-13T12:00:00Z' }, (p) => p.click('[data-tier-btn="1"]'));
await shot('tang2-moi', buildState('A'), null, (p) => p.click('[data-tier-btn="2"]'));
await shot('tang3-moi', buildState('B', (n) => { n.setup = { scenario: 'B', zoneId: 'z1', side: 'buy', c4: 'same', c5: 'near', c6: 2, c7: { dma: 'flat' }, b1: 'U', b2: 'down', ext: 4175, b3: 'ok', calc: { entry: 4177, sl: 4174.7 } }; }), { now: '2026-10-13T14:30:00Z', feed: Object.assign({}, FEED, { fetchedAt: '2026-10-13T14:20:00.000Z' }) }, (p) => p.click('[data-tier-btn="3"]'));
await shot('tu-dien', buildState('B'), null, async (p) => { await p.click('[data-testid="glossary-btn"]'); });
await browser.close();
