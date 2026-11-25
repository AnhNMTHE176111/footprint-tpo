(function () {
  const SEL = '[aria-label="Advertisement"], .bv-bitmedia-strip';
  const hide = el => el.style.setProperty('display', 'none', 'important');
  const scan = root => {
    if (root.matches && root.matches(SEL)) hide(root);
    if (root.querySelectorAll) root.querySelectorAll(SEL).forEach(hide);
  };
  const start = () => {
    scan(document);
    new MutationObserver(muts => {
      for (const m of muts) {
        if (m.type === 'attributes') { if (m.target.matches(SEL)) hide(m.target); }
        else m.addedNodes.forEach(n => n.nodeType === 1 && scan(n));
      }
    }).observe(document.documentElement, {
      childList: true, subtree: true,
      attributes: true, attributeFilter: ['style', 'class', 'aria-label']
    });
  };
  if (document.documentElement) start();
  else document.addEventListener('DOMContentLoaded', start);
})();
