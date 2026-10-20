// Sinh icon PNG từ icons/icon.svg bằng Playwright (chạy một lần: node scripts/gen-icons.mjs)
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const svg = readFileSync(resolve(root, 'icons/icon.svg'), 'utf8');
const browser = await chromium.launch();
async function render(size, file, inner) {
  const page = await browser.newPage({ viewport: { width: size, height: size } });
  const body = inner ? `<div style="width:${size}px;height:${size}px;background:#0e1014;display:grid;place-items:center"><div style="width:${size * 0.72}px;height:${size * 0.72}px">${svg}</div></div>` : `<div style="width:${size}px;height:${size}px">${svg}</div>`;
  await page.setContent(`<style>html,body{margin:0}svg{width:100%;height:100%;display:block}</style>${body}`);
  await page.screenshot({ path: resolve(root, 'icons', file), omitBackground: true });
  await page.close();
}
await render(192, 'icon-192.png');
await render(512, 'icon-512.png');
await render(512, 'icon-maskable-512.png', true);   // chừa vùng an toàn cho icon dạng mặt nạ
await browser.close();
console.log('xong');
