// Kiểm tra chữ trong js/content.js (trừ criteria[]). Chạy: npm run lint:vi
//  (a) cấm "bán", "mua", "lệnh chờ", "đập giá"
//  (b) token chỉ gồm [A-Za-z] dài ≥ 3, hoặc toàn chữ hoa dài ≥ 2, so không phân biệt hoa/thường:
//      phải nằm trong danh sách 4.11 của plan hoặc trong scripts/vi-khong-dau.txt
//  (c) nhãn chính không quá 9 từ (bỏ ký hiệu toán và số)
//  (d) không dấu chấm thập phân trong chuỗi hiển thị (số mục kiểu "mục 4.1", "HT 3.2" được bỏ qua)
//  (e) mọi khóa chữ mà js/ui và js/main.js gọi T('...') đều có trong content.ui
import { createRequire } from 'node:module';
import { readFileSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, '..');
const C = require(resolve(root, 'js/content.js'));

// danh sách 4.11 (giữ tiếng Anh)
const LIST_411 = ('buy sell limit market ENTRY TPO VA VAH VAL POC HVN LVN VWAP delta DMA IB R SL TP be fade trap tail single print poor high low naked bias acceptance move ' +
  'retest range bracket session tick thin Trend setup profile COMEX NYSE Globex FOMC NFP CPI Jobless Claims ET Markdown JSON CSV Esc Enter').split(/\s+/).map((s) => s.toLowerCase());
const viFile = readFileSync(resolve(here, 'vi-khong-dau.txt'), 'utf8').split(/\r?\n/).map((l) => l.replace(/#.*$/, '').trim().toLowerCase()).filter(Boolean);
const ALLOW = new Set([...LIST_411, ...viFile]);

const SKIP_KEYS = new Set(['htRef', 'ctl', 'img', 'anchor', 'ref', 'v', 'HT_BASE', 'criteria', 'key', 'gloss', 'id', 'short']);
const LABEL_KEYS = /^(t\dTitle\d?|t0Alert|t0Note|vwapQ|recheck|boDir|boEdge|boAt|boStep\d|boNth|newsDay|thinDir|swept|entryL|slL|tpL|c6Again|curPrice|exitPrice|fillPrice|manualReason|outsideBar|yourSum|set[A-Z]\w*|kv[A-Z]\w*|jh\d|plan\d|cancelWhen|w[A-Z]\w*|card[A-Z]\w*|tab(Label|Canh|Bam)|t5(Tonight|Week|Export|Settings))$/;

const errors = [];
const strings = []; // {path, text, label}

function walk(node, path, inLabelCtx) {
  if (typeof node === 'string') { strings.push({ path, text: node, label: inLabelCtx }); return; }
  if (Array.isArray(node)) { node.forEach((x, i) => walk(x, path + '[' + i + ']', inLabelCtx)); return; }
  if (node && typeof node === 'object') {
    for (const k of Object.keys(node)) {
      if (SKIP_KEYS.has(k)) continue;
      const p = path ? path + '.' + k : k;
      let lab = false;
      if (k === 'label' || k === 'name') lab = true;                       // controls.*.label, option.label, tiers.name
      if (path.startsWith('ui') && LABEL_KEYS.test(k)) lab = true;
      if (typeof node[k] === 'string') strings.push({ path: p, text: node[k], label: lab });
      else walk(node[k], p, false);
    }
  }
}
walk(C, '', false);

const FORBIDDEN = /(^|[^\p{L}])(bán|mua|lệnh chờ|đập giá)(?![\p{L}])/iu;

function stripPlaceholders(s) { return s.replace(/\{\w+\}/g, ' '); }
function words(s) {
  return stripPlaceholders(s).split(/\s+/).filter((w) => /\p{L}/u.test(w) && !/^[\d.,:+\-−–±′%/·→⇒]+$/u.test(w));
}

for (const s of strings) {
  const t = s.text;
  // (a)
  const m = FORBIDDEN.exec(t);
  if (m) errors.push(`(a) ${s.path}: chứa "${m[2]}" — ${JSON.stringify(t)}`);
  // (b)
  for (const tok of stripPlaceholders(t).match(/[\p{L}\p{N}]+/gu) || []) {
    if (!/^[A-Za-z]+$/.test(tok)) continue;
    const isUpper = tok === tok.toUpperCase();
    if (tok.length >= 3 || (tok.length >= 2 && isUpper)) {
      if (!ALLOW.has(tok.toLowerCase())) errors.push(`(b) ${s.path}: từ "${tok}" không có trong danh sách 4.11 / vi-khong-dau.txt — ${JSON.stringify(t)}`);
    }
  }
  // (c)
  if (s.label && words(t).length > 9) errors.push(`(c) ${s.path}: nhãn ${words(t).length} từ (> 9) — ${JSON.stringify(t)}`);
  // (d)
  const noRef = stripPlaceholders(t).replace(/(HT|mục)\s*\d+(\.\d+)*/gi, ' ').replace(/QĐ-\d+/g, ' ');
  if (/\d\.\d/.test(noRef)) errors.push(`(d) ${s.path}: dấu chấm thập phân — ${JSON.stringify(t)}`);
}

// (e) khóa chữ
const uiFiles = readdirSync(resolve(root, 'js/ui')).filter((f) => f.endsWith('.js')).map((f) => resolve(root, 'js/ui', f)).concat(resolve(root, 'js/main.js'));
const used = new Set();
for (const f of uiFiles) {
  const src = readFileSync(f, 'utf8');
  for (const m of src.matchAll(/\bT\('([A-Za-z0-9_]+)'(?!\s*\+)/g)) used.add(m[1]);
}
// T(cond ? 'a' : 'b', ...): cả hai khóa đều được dùng và đều phải tồn tại (sự cố "⟦halfNoteMin⟧" 2026-10-20)
for (const f of uiFiles) {
  const src = readFileSync(f, 'utf8');
  for (const m of src.matchAll(/\bT\(\s*[^'")]*?\?\s*'([A-Za-z0-9_]+)'\s*:\s*'([A-Za-z0-9_]+)'/g)) { used.add(m[1]); used.add(m[2]); }
}
const dynamic = [];
['q1', 'q5', 'q6', 'vwapW', 'zones'].forEach((c) => dynamic.push('need_' + c));
for (let i = 0; i < 5; i++) dynamic.push('key' + i);
for (let i = 1; i <= 7; i++) dynamic.push('jh' + i);
dynamic.push('chipOpen', 'chipOpenPaper', 'copyShape');
dynamic.forEach((k) => used.add(k));
for (const k of used) if (!(k in C.ui)) errors.push(`(e) thiếu khóa chữ ui.${k} (được gọi trong js/ui hoặc js/main.js)`);
const unused = Object.keys(C.ui).filter((k) => !used.has(k));

console.log(`lint:vi — ${strings.length} chuỗi, ${Object.keys(C.ui).length} khóa ui, ${ALLOW.size} từ được phép`);
if (unused.length) console.log(`(thông tin) ${unused.length} khóa ui chưa dùng: ${unused.join(', ')}`);
if (errors.length) {
  errors.forEach((e) => console.log('LỖI ' + e));
  console.log(`\nKết quả: ${errors.length} lỗi`);
  process.exit(1);
}
console.log('Kết quả: 0 lỗi');
