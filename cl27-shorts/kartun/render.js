// node render.js <id> <outDir> <frames: "a-b" or "a,b,c">  (RESUME=1 skips existing)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [,, id, out, spec] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 540, height: 960 } });
  p.on('pageerror', e => console.log('PAGEERROR', String(e.stack || e).slice(0, 500))); p.on('console', m => { if (m.type() === 'error') console.log('console.error', m.text().slice(0, 300)); });
  await p.goto(`http://localhost:8790/index.html?id=${id}`); await p.waitForFunction('window.ready', null, { timeout: 120000 });
  const total = await p.evaluate('window.TOTAL'); let frames = [];
  for (const part of (spec || `0-${total - 1}`).split(',')) { const [a, c] = part.split('-').map(Number); for (let f = a; f <= (isNaN(c) ? a : Math.min(c, total - 1)); f++) frames.push(f); }
  fs.mkdirSync(out, { recursive: true }); const t0 = Date.now();
  for (const [k, f] of frames.entries()) {
    const file = path.join(out, `f${String(f).padStart(4, '0')}.jpg`); if (process.env.RESUME && fs.existsSync(file)) continue;
    const data = await p.evaluate(f => { window.renderFrame(f); return document.getElementById('out').toDataURL('image/jpeg', 0.93); }, f);
    fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
    if (k % 60 === 0) console.log(id, f, '/', total, ((Date.now() - t0) / 1000 / (k + 1)).toFixed(2) + 's/frame');
  }
  console.log(id, 'DONE', total); await b.close();
})().catch(e => { console.log('FATAL', String(e.stack || e).slice(0, 600)); process.exit(1); });
