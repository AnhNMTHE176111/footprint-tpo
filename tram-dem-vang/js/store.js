/* Trạm Đêm Vàng — LƯU TRỮ: localStorage["tdv.v1"], migrate, xuất / nhập JSON (gộp theo trades.id). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(function (n) { return require('./' + n + '.js'); });
  else { root.TDV = root.TDV || {}; root.TDV.store = factory(function (n) { return root.TDV[n]; }); }
})(this, function (dep) {
  'use strict';
  var J = dep('journal');
  var KEY = 'tdv.v1';
  var VERSION = 1;

  function defaultSettings() {
    return { theme: 'dark', guideLevel: 'new', capital: 2000, riskPct: 2, dstShift: true, shortcuts: true, lastExportAt: null };
  }
  function defaultState() { return { version: VERSION, settings: defaultSettings(), nights: {} }; }

  // Nâng dữ liệu cũ lên bản hiện tại; không làm mất dữ liệu
  function migrate(raw) {
    if (!raw || typeof raw !== 'object') return defaultState();
    var out = { version: VERSION, settings: Object.assign(defaultSettings(), raw.settings || {}), nights: {} };
    var src = raw.nights && typeof raw.nights === 'object' ? raw.nights : {};
    Object.keys(src).forEach(function (k) { out.nights[k] = J.normalizeNight(src[k]); });
    return out;
  }

  function load(storage) {
    var text = null;
    try { text = storage.getItem(KEY); } catch (e) { return defaultState(); }
    if (!text) return defaultState();
    try { return migrate(JSON.parse(text)); }
    catch (e) {
      try { storage.setItem(KEY + '.hong', text); } catch (e2) { /* bộ nhớ đầy hoặc bị chặn */ }
      return defaultState();
    }
  }
  function save(storage, state) {
    try { storage.setItem(KEY, JSON.stringify(state)); return true; } catch (e) { return false; }
  }
  function exportJSON(state) { return JSON.stringify(state, null, 2); }

  // Gộp: đêm trùng giữ bản có tally.closedAt mới hơn (bằng nhau giữ bản hiện có), rồi bổ sung lệnh còn thiếu theo id
  function mergeNight(a, b) {
    var ta = (a.tally && a.tally.closedAt) || 0, tb = (b.tally && b.tally.closedAt) || 0;
    var base = tb > ta ? b : a, other = base === a ? b : a;
    var out = JSON.parse(JSON.stringify(base));
    var ids = {};
    out.trades.forEach(function (t) { ids[t.id] = true; });
    var added = 0;
    other.trades.forEach(function (t) { if (!ids[t.id]) { out.trades.push(JSON.parse(JSON.stringify(t))); added++; } });
    if (added) {
      out.trades.sort(function (x, y) { return String(x.time).localeCompare(String(y.time)); });
      J.recomputeTally(out, 0);
    }
    return { night: out, added: added };
  }
  function importMerge(state, text) {
    var parsed;
    try { parsed = JSON.parse(text); } catch (e) { return { ok: false, error: 'BAD_JSON' }; }
    if (!parsed || typeof parsed !== 'object' || typeof parsed.nights !== 'object' || parsed.nights === null) return { ok: false, error: 'NO_NIGHTS' };
    var inc = migrate(parsed);
    var out = JSON.parse(JSON.stringify(state));
    var nNew = 0, nMerged = 0, tradesAdded = 0;
    Object.keys(inc.nights).forEach(function (k) {
      if (!out.nights[k]) { out.nights[k] = inc.nights[k]; nNew++; tradesAdded += inc.nights[k].trades.length; }
      else {
        var have = {}; out.nights[k].trades.forEach(function (t) { have[t.id] = true; });
        var m = mergeNight(out.nights[k], inc.nights[k]); out.nights[k] = m.night; nMerged++;
        m.night.trades.forEach(function (t) { if (!have[t.id]) tradesAdded++; });
      }
    });
    return { ok: true, state: out, nightsNew: nNew, nightsMerged: nMerged, tradesAdded: tradesAdded };
  }

  return { KEY: KEY, VERSION: VERSION, defaultState: defaultState, defaultSettings: defaultSettings, migrate: migrate, load: load, save: save, exportJSON: exportJSON, importMerge: importMerge, mergeNight: mergeNight };
});
