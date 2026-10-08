// Paste into browser_console (expression) to audit a page without a vision provider.
// Returns font/layout/animation/overflow facts as JSON. Adapt selectors per page.
(() => {
  const body = getComputedStyle(document.body);
  const h1 = document.querySelector('h1');
  const hs = h1 ? getComputedStyle(h1) : null;
  const imgs = [...document.images].slice(0, 5).map((i) => {
    const r = i.getBoundingClientRect();
    return {
      src: i.src.split('/').pop(),
      natural: i.naturalWidth + 'x' + i.naturalHeight,
      rendered: Math.round(r.width) + 'x' + Math.round(r.height),
      loaded: i.complete && i.naturalWidth > 0,
      radius: getComputedStyle(i).borderRadius,
    };
  });
  const anims = [...document.querySelectorAll('*')]
    .map((el) => el.getAnimations().map((a) => ({ el: el.tagName + '.' + (el.className || '').toString().slice(0, 20), name: a.animationName, state: a.playState })))
    .flat()
    .slice(0, 10);
  const iw = window.innerWidth;
  const offenders = [];
  document.querySelectorAll('*').forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.right > iw + 1 || r.left < -1) {
      offenders.push({ tag: el.tagName, cls: (el.className || '').toString().slice(0, 60), right: Math.round(r.right) });
    }
  });
  return {
    bodyFont: body.fontFamily,
    bodyColor: body.color,
    h1: hs ? { size: hs.fontSize, weight: hs.fontWeight, color: hs.color } : null,
    fontsLoaded: {
      primary: document.fonts.check('16px ' + (hs ? hs.fontFamily.split(',')[0] : 'sans-serif')),
    },
    images: imgs,
    animationsHeld: anims.filter((a) => a.state === 'finished'),
    overflow: { scrollWidth: document.body.scrollWidth, innerWidth: iw, delta: document.body.scrollWidth - iw, offenders: offenders.slice(0, 5) },
    jsOn: document.documentElement.classList.contains('js'),
  };
})()
