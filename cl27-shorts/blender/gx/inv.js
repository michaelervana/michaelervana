// Load the Night Cup game headless, wait for the stadium, list every mesh that is not the stadium model/crowd/players.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const FD = path.join(__dirname, 'fonts');
const face = (fam, w, st, file) => `@font-face{font-family:'${fam}';font-style:${st};font-weight:${w};font-display:block;src:url(http://localhost:8792/__fonts/${file}) format('woff2');}`;
let css = '';
for (const w of [400, 500, 600, 700]) css += face('Barlow', w, 'normal', `barlow-latin-${w}-normal.woff2`);
for (const w of [600, 700, 800, 900]) for (const st of ['normal', 'italic']) css += face('Barlow Condensed', w, st, `barlow-condensed-latin-${w}-${st}.woff2`);
module.exports.open = async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 480, height: 270 } });
  p.on('pageerror', e => console.log('PAGEERROR', String(e).slice(0, 200)));
  await p.route('https://fonts.googleapis.com/**', r => r.fulfill({ contentType: 'text/css', body: css }));
  await p.route('https://fonts.gstatic.com/**', r => r.abort());
  await p.route('http://localhost:8792/index.html', r => { let html = fs.readFileSync('/home/user/michaelervana/golazo-night-cup/index.html', 'utf8');
    const hook = "window.__GAME = { get G() { return G; }, get W3() { return W3; }, get SCN() { return SCN; }, get TEX() { return TEX; }, get TEAMS() { return TEAMS; }, buildStandFaces, buildLED, refreshWorldTeams, buildBoards3, buildRibbon3, drawBigScreen, setSel: (a, b) => { TEAMS_SEL = [a, b]; } };\n";
    const k = html.lastIndexOf('boot();'); html = html.slice(0, k) + hook + html.slice(k); r.fulfill({ body: html, contentType: 'text/html' }); });
  await p.route('http://localhost:8792/__fonts/**', r => r.fulfill({ path: path.join(FD, path.basename(r.request().url())), contentType: 'font/woff2' }));
  await p.route('https://cdn.jsdelivr.net/npm/three@0.147.0/**', r => { const rel = r.request().url().split('three@0.147.0/')[1]; let body = fs.readFileSync(path.join(__dirname, 'three', 'package', rel), 'utf8');
    if (rel.endsWith('three.min.js')) body += '\n;THREE.WebGLRenderer.prototype.render = function () {}; THREE.WebGLRenderer.prototype.compile = function () {};';
    r.fulfill({ body, contentType: 'application/javascript' }); });
  await p.goto('http://localhost:8792/index.html', { waitUntil: 'domcontentloaded', timeout: 600000 });
  for (let i = 0; i < 120; i++) {
    const st = await Promise.race([p.evaluate(() => { const g = window.__GAME; if (!g) return { s: 'nohook' }; return { s: g.G.state, m: !!g.W3.model, b: !!g.W3.bigScreens, l: !!g.W3.led, f: g.G.fontsOk }; }).catch(e => ({ s: 'ERR ' + String(e).slice(0, 60) })), new Promise(r => setTimeout(() => r({ s: 'busy' }), 9000))]);
    console.log('wait', i, JSON.stringify(st));
    if (st.m && st.b && st.l) break; await p.waitForTimeout(10000);
  }
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(2000);
  return { b, p };
};
if (require.main === module) (async () => {
  const { b, p } = await module.exports.open();
  const inv = await p.evaluate(() => {
    const out = []; SCN.updateMatrixWorld(true);
    SCN.traverse(o => {
      if (!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh || o === W3.model) return;
      let vis = true; for (let q = o; q; q = q.parent) if (!q.visible) vis = false;
      const g = o.geometry, n = g.attributes.position ? g.attributes.position.count : 0; g.computeBoundingBox && g.computeBoundingBox();
      const bb = new THREE.Box3().setFromObject(o); const mats = Array.isArray(o.material) ? o.material : [o.material];
      out.push({ name: o.name, type: g.type, n, vis, min: bb.min.toArray().map(v => +v.toFixed(1)), max: bb.max.toArray().map(v => +v.toFixed(1)),
        mats: mats.map(m => m.type + (m.map && m.map.image ? '[' + m.map.image.width + 'x' + m.map.image.height + ']' : '') + (m.transparent ? 'T' : '') + (m.blending === THREE.AdditiveBlending ? 'A' : '')) });
    });
    return { fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + f.weight).join(','), state: G.state, list: out };
  });
  console.log('fonts', inv.fonts, 'state', inv.state);
  for (const m of inv.list) console.log(JSON.stringify(m));
  await b.close();
})();
