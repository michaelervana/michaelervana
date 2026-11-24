// Deterministic game-footage capture: requestAnimationFrame is driven by hand, one 50 ms game frame per screenshot (20 fps footage).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [,, outDir, which = 'all'] = process.argv; const W = 540, H = 960;
const threeDir = path.join(__dirname, '..', 'three', 'node_modules', 'three');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--mute-audio'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  const t0 = Date.now(), log = (...a) => console.log(((Date.now() - t0) / 1000).toFixed(0) + 's', ...a);
  p.on('pageerror', e => log('PAGEERROR', String(e).slice(0, 300)));
  await p.addInitScript(() => {
    const q = []; let T = 1000; window.requestAnimationFrame = cb => { q.push(cb); return q.length; }; window.cancelAnimationFrame = () => { };
    window.__tick = ms => { T += ms; const run = q.splice(0); for (const cb of run) cb(T); };
    window.__auto = setInterval(() => { if (!window.__manual) window.__tick(50); }, 30);
    const st = document.createElement('style'); st.textContent = '#hud,#touch,#cm,.cm,#banner,#hint,#toast,#scr-intro,#scr-select,#scr-vs,.bug,#ht,#rotate,#btn-sound-menu,#scr-pause,#replay-tag,#fade{display:none!important}';
    document.addEventListener('DOMContentLoaded', () => document.head.appendChild(st));
  });
  await p.route('https://cdn.jsdelivr.net/npm/three@0.147.0/**', r => { const f = path.join(threeDir, new URL(r.request().url()).pathname.replace('/npm/three@0.147.0/', '')); fs.existsSync(f) ? r.fulfill({ body: fs.readFileSync(f), contentType: 'application/javascript' }) : r.abort(); });
  await p.goto('http://localhost:8771/index.html#nointro', { waitUntil: 'domcontentloaded', timeout: 120000 });
  await p.waitForFunction('window.__golazo && __golazo.G.fontsOk && (__golazo.HDP.gltf || __golazo.HDP.loading === false) && (__golazo.HDR.gltf || __golazo.HDR.failed)', null, { timeout: 300000, polling: 1000 });
  log('booted');
  await p.evaluate(() => { window.__manual = true; clearInterval(window.__auto); });
  const tick = (n = 1) => p.evaluate(n => { for (let i = 0; i < n; i++) window.__tick(50); }, n);
  const start = async (a, b, tod, wx) => {
    await p.evaluate(([a, b, tod, wx]) => { const g = __golazo; g.G.myIdx = a; g.G.oppIdx = b; g.startMatch(); window.__tod = tod; window.__wx = wx; }, [a, b, tod, wx]);
    for (let i = 0; i < 40 && await p.evaluate(() => __golazo.G.state === 'menu'); i++) await tick(2);
    await p.evaluate(() => { const g = __golazo; g.wx(window.__wx); g.tod(window.__tod); g.setQuality(1); });
  };
  const rec = async (name, n, perFrame) => {
    const dir = path.join(outDir, name); fs.mkdirSync(dir, { recursive: true });
    for (let i = 0; i < n; i++) {
      if (perFrame) await p.evaluate(perFrame, { i, n });
      await tick(1);
      await p.screenshot({ path: path.join(dir, String(i).padStart(4, '0') + '.jpg'), type: 'jpeg', quality: 90 });
      await p.evaluate(() => __golazo.setQuality(1));
      if (i % 20 === 0) log(name, i, '/', n);
    }
  };
  const want = n => which === 'all' || which.split(',').includes(n);
  // 1. kick-off: smoke cannons along both touchlines, camera rising over the near touchline
  if (want('kick_smoke')) { await start(0, 4, 'night', 'clear'); await tick(2);
    await rec('kick_smoke', 100, ({ i, n }) => { const g = __golazo, k = i / n; g.DBG.cam = { free: 1, fp: [-20 + 26 * k, 6 + 5 * k, -52], ft: [0 + 8 * k, 6, 20], ffov: 0.95 }; g.G.camCut = 1; }); }
  // 2. broadcast camera on live play
  if (want('broadcast')) { await start(6, 5, 'night', 'clear'); await p.evaluate(() => { const g = __golazo; g.step(430); g.G.state = 'play'; g.DBG.cam = null; g.G.camCut = 1; }); await tick(40);
    await rec('broadcast', 110); }
  // 3. low camera chasing the ball
  if (want('ballcam')) { await start(3, 7, 'night', 'clear'); await p.evaluate(() => { const g = __golazo; g.step(430); g.G.state = 'play'; }); await tick(30);
    await rec('ballcam', 110, () => { const g = __golazo, b = g.ball; g.DBG.cam = { free: 1, fp: [b.x - 6.5, 2.1, b.z - 5.5], ft: [b.x + 1, 0.6, b.z + 0.8], ffov: 0.85 }; g.G.camCut = 1; }); }
  // 4. a shot spears the net, seen from beside the goal
  if (want('goal_net')) { await start(9, 10, 'night', 'clear'); await p.evaluate(() => { const g = __golazo; g.step(430); const b = g.ball; g.G.state = 'play'; b.owner = null; b.lastKicker = g.user; b.x = 44; b.z = 2.4; b.y = 0.6; b.vx = 24; b.vz = 0.05; b.vy = 4.6; g.DBG.cam = { free: 1, fp: [47.5, 1.7, 9.5], ft: [53.6, 1.2, -0.5], ffov: 0.85 }; g.G.camCut = 1; });
    await rec('goal_net', 80); }
  // 5. the tifos waving on the far stand
  if (want('tifo')) { await start(0, 3, 'night', 'clear'); await tick(4);
    await rec('tifo', 90, ({ i, n }) => { const g = __golazo, k = i / n; g.DBG.cam = { free: 1, fp: [-30 + 70 * k, 10, -12], ft: [-22 + 72 * k, 9, 52], ffov: 0.75 }; g.G.camCut = 1; }); }
  // 6. rain at night, low over the puddles
  if (want('rain')) { await start(1, 2, 'night', 'rain'); await p.evaluate(() => { const g = __golazo; g.step(430); g.G.state = 'play'; }); await tick(20);
    await rec('rain', 100, ({ i, n }) => { const g = __golazo, b = g.ball, k = i / n; g.DBG.cam = { free: 1, fp: [b.x - 9 + 3 * k, 1.5, b.z - 7], ft: [b.x, 0.4, b.z], ffov: 0.9 }; g.G.camCut = 1; }); }
  // 7. orbit over the stadium
  if (want('orbit')) { await start(5, 8, 'night', 'clear'); await p.evaluate(() => { const g = __golazo; g.step(430); g.G.state = 'play'; }); await tick(10);
    await rec('orbit', 110, ({ i, n }) => { const g = __golazo, a = -2.2 + 1.3 * i / n; g.DBG.cam = { free: 1, fp: [Math.cos(a) * 70, 34, Math.sin(a) * 52], ft: [0, 0, 0], ffov: 0.95 }; g.G.camCut = 1; }); }
  // 8. dolly past the line-up before kick-off
  if (want('players')) { await start(0, 9, 'night', 'clear'); await p.evaluate(() => { const g = __golazo, P = g.players; g.G.state = 'x_hold';
      const put = (q, x, z, f) => { q.x = x; q.z = z; q.tx = x; q.tz = z; q.f = f; q.vx = q.vz = 0; q.spd = 0; };
      [1, 2, 3, 4, 5, 6, 7, 8].forEach((k, i) => put(P[k], -7 + i * 1.7, 1.2, -Math.PI / 2)); [12, 13, 14, 15, 16, 17, 18, 19].forEach((k, i) => put(P[k], -7 + i * 1.7, 3.6, -Math.PI / 2)); });
    await rec('players', 90, ({ i, n }) => { const g = __golazo, k = i / n; g.DBG.cam = { free: 1, fp: [-8 + 12 * k, 1.55, -3.2], ft: [-6 + 12 * k, 1.35, 2.5], ffov: 0.62 }; g.G.camCut = 1; }); }
  log('done'); await b.close();
})().catch(e => { console.log('FATAL', String(e.stack || e).slice(0, 800)); process.exit(1); });
