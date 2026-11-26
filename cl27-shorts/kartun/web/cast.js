// Flat 2D bean-head cartoon characters drawn on canvas cards with plum outlines.
// Design canvas 400 x 700, soles at y = 690. Card height in the world: 1.9 m.
const INK = '#3b1e3a';
const OUTFITS = {
  worker: { shirt: '#d9cba8', vest: '#5a4636', pants: '#6b5a48', cap: 'flat', capCol: '#4a3c30', skin: '#f2c49b', hair: '#4a2f20' },
  worker2: { shirt: '#b8c6d6', vest: '#3e4b5a', pants: '#5a5048', cap: 'flat', capCol: '#3a3a3a', skin: '#e0a87e', hair: '#2a1d16', beard: true },
  worker3: { shirt: '#e2d3b5', pants: '#4f4438', cap: null, skin: '#c98d62', hair: '#1d1410' },
  boss: { shirt: '#f4f1e8', jacket: '#2f2f3a', pants: '#2f2f3a', cap: 'top', capCol: '#1d1d24', skin: '#f2c49b', hair: '#6b6b6b', moustache: true, belly: true },
  vicar: { shirt: '#1f1f26', jacket: '#1f1f26', pants: '#1f1f26', collar: true, cap: null, skin: '#f0c7a2', hair: '#9a9a9a' },
  lady: { dress: '#7d3f5a', skin: '#f0c7a2', hair: '#6a3a22', cap: 'bonnet', capCol: '#e8d9b8' },
  rowdy: { shirt: '#9c8a6a', pants: '#4a4038', cap: 'flat', capCol: '#5a5046', skin: '#e8b48e', hair: '#3a2a1a', patch: true },
};
// club kits (colours only, no crests)
const KITS = {
  arsenal: { shirt: '#d81e2a', sleeve: '#ffffff', shorts: '#ffffff', socks: '#d81e2a' },
  newtonheath: { shirt: '#2f8a3c', shirt2: '#f2c230', shorts: '#f4f1e8', socks: '#2a2a2a', halves: true },
  manutd: { shirt: '#d61f26', shorts: '#ffffff', socks: '#111111' },
  mancity: { shirt: '#6cabdd', shorts: '#ffffff', socks: '#6cabdd' },
  liverpool: { shirt: '#c8102e', shorts: '#c8102e', socks: '#c8102e' },
  everton: { shirt: '#1d46a0', shorts: '#ffffff', socks: '#1d46a0' },
  chelsea: { shirt: '#0a47c2', shorts: '#0a47c2', socks: '#ffffff' },
  fulham: { shirt: '#ffffff', shorts: '#111111', socks: '#ffffff' },
};
// arm poses in screen degrees (0 = right, 90 = down, -90 = up): [left upper, left fore, right upper, right fore]
const ARM = { hang: [105, 95, 75, 85], wave: [105, 95, -35, -100], cheer: [-125, -110, -55, -70], point: [105, 95, -5, -5],
  hip: [150, 40, 30, 140], think: [105, 95, 105, -125], shrug: [170, -125, 10, -55], hold: [65, 15, 115, 165], facepalm: [105, 95, 115, -110], run: [60, 120, 120, 60] };

function drawBean(g, o) {
  const k = o.kit ? KITS[o.kit] : null, of = OUTFITS[o.outfit || 'worker'] || OUTFITS.worker;
  const skin = o.skin || of.skin;
  const lw = 9; g.lineJoin = 'round'; g.lineCap = 'round'; g.strokeStyle = INK; g.lineWidth = lw;
  const cx = 200, bob = (o.bob || 0) * 8, sq = o.squash || 0;
  const torsoTop = 360 + bob, hip = 540 + bob;
  const shirt = k ? k.shirt : (of.jacket || of.shirt || of.dress || '#888'), pants = k ? k.shorts : (of.pants || of.dress || '#555');
  // legs
  const legLen = k ? 120 : 140, step = o.step || 0;
  [[-40, step], [40, -step]].forEach(([dx, st]) => {
    const fx = cx + dx + st * 30, fy = 690;
    g.fillStyle = k ? k.socks : pants; g.beginPath(); g.moveTo(cx + dx - 20, hip - 10); g.lineTo(fx - 20, fy - 30); g.lineTo(fx + 20, fy - 30); g.lineTo(cx + dx + 20, hip - 10); g.closePath(); g.fill(); g.stroke();
    if (k) { g.fillStyle = skin; g.beginPath(); g.rect(cx + dx - 18 + st * 10, hip + 30, 36, 28); g.fill(); }
    g.fillStyle = '#2b2226'; g.beginPath(); g.ellipse(fx + (dx < 0 ? -10 : 10), fy - 18, 38, 18, 0, 0, 7); g.fill(); g.stroke();
  });
  // torso
  g.fillStyle = shirt; g.beginPath(); g.roundRect(cx - 95, torsoTop, 190, hip - torsoTop + (of.dress ? 140 : 0), [60, 60, 30, 30]); g.fill();
  if (k && k.halves) { g.save(); g.clip(); g.fillStyle = k.shirt2; g.fillRect(cx, torsoTop, 100, 220); g.restore(); }
  if (k && k.sleeve) { g.save(); g.clip(); g.fillStyle = k.sleeve; g.fillRect(cx - 100, torsoTop, 36, 120); g.fillRect(cx + 64, torsoTop, 36, 120); g.restore(); }
  if (of.vest && !k) { g.fillStyle = of.vest; g.fillRect(cx - 70, torsoTop + 20, 140, hip - torsoTop - 30); }
  if (of.belly && !k) { g.fillStyle = shade(of.jacket, 1.4); g.beginPath(); g.ellipse(cx, torsoTop + 120, 70, 80, 0, 0, 7); g.fill(); }
  g.beginPath(); g.roundRect(cx - 95, torsoTop, 190, hip - torsoTop + (of.dress ? 140 : 0), [60, 60, 30, 30]); g.stroke();
  if (of.collar) { g.fillStyle = '#fff'; g.fillRect(cx - 22, torsoTop + 4, 44, 16); }
  if (k) { g.fillStyle = pants; g.beginPath(); g.roundRect(cx - 92, hip - 30, 184, 70, 14); g.fill(); g.stroke(); }
  if (o.num && k) { g.fillStyle = k.shirt === '#ffffff' ? INK : '#fff'; g.font = '900 70px "Barlow Condensed", Impact, sans-serif'; g.textAlign = 'center'; g.fillText(o.num, cx, torsoTop + 110); }
  // arms
  const P0 = ARM[o.pose || 'hang'] || ARM.hang, sw = (o.armSwing || 0) * 25, R = Math.PI / 180;
  [[-1, P0[0] + sw, P0[1] + sw], [1, P0[2] - sw, P0[3] - sw]].forEach(([s, a1, a2], i) => {
    const sx = cx + s * 88, sy = torsoTop + 40, L1 = 95, L2 = 85;
    const ex = sx + Math.cos(a1 * R) * L1, ey = sy + Math.sin(a1 * R) * L1, hx = ex + Math.cos(a2 * R) * L2, hy = ey + Math.sin(a2 * R) * L2;
    g.strokeStyle = INK; g.lineWidth = 40 + lw * 2; g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.lineTo(hx, hy); g.stroke();
    g.strokeStyle = k ? (k.sleeve || shirt) : shirt; g.lineWidth = 40; g.beginPath(); g.moveTo(sx, sy); g.lineTo(ex, ey); g.stroke();
    g.strokeStyle = k ? skin : shirt; g.beginPath(); g.moveTo(ex, ey); g.lineTo(hx, hy); g.stroke();
    g.strokeStyle = INK; g.lineWidth = lw; g.fillStyle = skin; g.beginPath(); g.arc(hx, hy, 24, 0, 7); g.fill(); g.stroke();
    if (i === 1 && o.prop) drawProp(g, o.prop, hx, hy);
  });
  // bean head
  const hy = torsoTop - 150 + (sq * 20), hw = 120 * (1 + sq * 0.15), hh = 150 * (1 - sq * 0.15);
  g.fillStyle = skin; g.beginPath(); g.ellipse(cx, hy, hw, hh, -0.12, 0, 7); g.fill();
  // hair
  g.fillStyle = o.hair || of.hair; g.beginPath(); g.ellipse(cx - 6, hy - 92, 104, 64, -0.12, Math.PI, 0); g.fill();
  g.strokeStyle = INK; g.lineWidth = lw; g.beginPath(); g.ellipse(cx, hy, hw, hh, -0.12, 0, 7); g.stroke();
  // face
  const ex2 = o.look || 0, ey = hy - 10, f = o.face || 'smile';
  const blink = o.blink;
  [[-44, 0], [44, 0]].forEach(([dx]) => {
    if (blink) { g.beginPath(); g.moveTo(cx + dx - 18, ey); g.lineTo(cx + dx + 18, ey); g.stroke(); return; }
    const r = f === 'shock' ? 30 : 24; g.fillStyle = '#fff'; g.beginPath(); g.ellipse(cx + dx, ey, r, r * 1.2, 0, 0, 7); g.fill(); g.stroke();
    g.fillStyle = INK; g.beginPath(); g.arc(cx + dx + ex2 * 8, ey + 4, f === 'shock' ? 8 : 11, 0, 7); g.fill();
  });
  g.lineWidth = lw; g.strokeStyle = INK;
  const brow = { angry: [12, -12], sad: [-10, 10], shock: [-14, -14], smug: [6, -8] }[f] || [0, 0];
  [[-44, brow[0]], [44, brow[1]]].forEach(([dx, t], i) => { g.beginPath(); g.moveTo(cx + dx - 22, ey - 44 + (i ? -t : t) * 0.5); g.lineTo(cx + dx + 22, ey - 44 + (i ? t : -t) * 0.5); g.stroke(); });
  const my = hy + 62, talk = o.talk || 0;
  g.fillStyle = '#7a2238';
  if (f === 'shock') { g.beginPath(); g.ellipse(cx, my, 24, 30, 0, 0, 7); g.fill(); g.stroke(); }
  else if (f === 'sad') { g.beginPath(); g.arc(cx, my + 20, 30, Math.PI * 1.15, Math.PI * 1.85); g.stroke(); }
  else if (f === 'angry') { g.beginPath(); g.moveTo(cx - 30, my + 6); g.lineTo(cx + 30, my); g.stroke(); }
  else if (f === 'laugh' || talk > 0.5) { g.beginPath(); g.moveTo(cx - 40, my - 6); g.quadraticCurveTo(cx, my + 50, cx + 40, my - 6); g.closePath(); g.fill(); g.stroke(); }
  else { g.beginPath(); g.arc(cx, my - 14, 36, Math.PI * 0.2, Math.PI * 0.8); g.stroke(); }
  if (of.moustache && !k) { g.fillStyle = '#5a5a5a'; g.beginPath(); g.ellipse(cx - 22, my - 22, 24, 9, 0.2, 0, 7); g.ellipse(cx + 22, my - 22, 24, 9, -0.2, 0, 7); g.fill(); }
  if (of.beard && !k) { g.fillStyle = of.hair; g.beginPath(); g.ellipse(cx, hy + 100, 70, 40, 0, 0, Math.PI); g.fill(); }
  if (of.patch && !k) { g.fillStyle = '#c96d5a'; g.beginPath(); g.ellipse(cx + 70, hy + 30, 14, 9, 0, 0, 7); g.fill(); }
  g.fillStyle = '#ff8a8a55'; g.beginPath(); g.ellipse(cx - 80, hy + 30, 18, 11, 0, 0, 7); g.ellipse(cx + 80, hy + 30, 18, 11, 0, 0, 7); g.fill();
  // headwear
  const cap = k ? null : of.cap;
  if (cap === 'flat') { g.fillStyle = of.capCol; g.beginPath(); g.ellipse(cx, hy - 108, 112, 42, -0.12, Math.PI, 0); g.fill(); g.stroke(); g.beginPath(); g.ellipse(cx + 40, hy - 100, 74, 18, -0.1, 0, Math.PI); g.fill(); g.stroke(); }
  if (cap === 'top') { g.fillStyle = of.capCol; g.beginPath(); g.ellipse(cx, hy - 128, 110, 18, -0.1, 0, 7); g.fill(); g.stroke(); g.beginPath(); g.roundRect(cx - 62, hy - 260, 124, 136, 10); g.fill(); g.stroke(); g.fillStyle = '#7a2238'; g.fillRect(cx - 62, hy - 150, 124, 16); }
  if (cap === 'bonnet') { g.fillStyle = of.capCol; g.beginPath(); g.ellipse(cx, hy - 80, 135, 100, -0.12, Math.PI * 1.02, Math.PI * 1.98); g.fill(); g.stroke(); }
  if (o.hat === 'party') { g.fillStyle = '#ffd23d'; g.beginPath(); g.moveTo(cx - 50, hy - 130); g.lineTo(cx + 10, hy - 270); g.lineTo(cx + 60, hy - 120); g.closePath(); g.fill(); g.stroke(); }
}
function drawProp(g, p, x, y) {
  g.lineWidth = 8; g.strokeStyle = INK;
  if (p === 'ball') { g.fillStyle = '#c98a4a'; g.beginPath(); g.arc(x + 20, y - 10, 38, 0, 7); g.fill(); g.stroke(); g.beginPath(); g.moveTo(x - 12, y - 10); g.lineTo(x + 52, y - 10); g.stroke(); }
  if (p === 'money') { g.fillStyle = '#c9a23a'; g.beginPath(); g.ellipse(x + 10, y + 20, 44, 52, 0, 0, 7); g.fill(); g.stroke(); g.fillStyle = INK; g.font = '900 52px Impact'; g.textAlign = 'center'; g.fillText('£', x + 10, y + 38); }
  if (p === 'paper') { g.fillStyle = '#f4efe0'; g.beginPath(); g.rect(x - 20, y - 70, 90, 120); g.fill(); g.stroke(); for (let i = 0; i < 5; i++) { g.beginPath(); g.moveTo(x - 6, y - 50 + i * 20); g.lineTo(x + 56, y - 50 + i * 20); g.stroke(); } }
  if (p === 'hammer') { g.fillStyle = '#7a5a3a'; g.fillRect(x - 6, y - 90, 14, 110); g.strokeRect(x - 6, y - 90, 14, 110); g.fillStyle = '#6c6f78'; g.fillRect(x - 36, y - 110, 74, 34); g.strokeRect(x - 36, y - 110, 74, 34); }
  if (p === 'leash') { g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + 80, y + 120, x + 150, y + 200); g.stroke(); }
}
function drawDog(g, o) { // St Bernard
  g.lineWidth = 9; g.strokeStyle = INK; g.lineJoin = 'round'; const b = (o.bob || 0) * 8, st = o.step || 0;
  g.fillStyle = '#f2e6d0'; [[90, st], [150, -st], [250, st], [310, -st]].forEach(([x, s]) => { g.beginPath(); g.roundRect(x - 18 + s * 16, 520 + b, 36, 170 - b, 14); g.fill(); g.stroke(); });
  g.fillStyle = '#a5562b'; g.beginPath(); g.ellipse(200, 470 + b, 150, 90, 0, 0, 7); g.fill(); g.stroke();
  g.fillStyle = '#f2e6d0'; g.beginPath(); g.ellipse(200, 520 + b, 90, 40, 0, 0, 7); g.fill();
  g.fillStyle = '#a5562b'; g.beginPath(); g.ellipse(330, 330 + b, 80, 74, 0, 0, 7); g.fill(); g.stroke();
  g.fillStyle = '#f2e6d0'; g.beginPath(); g.ellipse(352, 360 + b, 46, 36, 0, 0, 7); g.fill(); g.stroke();
  g.fillStyle = INK; g.beginPath(); g.arc(385, 345 + b, 10, 0, 7); g.fill(); g.beginPath(); g.arc(325, 312 + b, 9, 0, 7); g.fill();
  g.fillStyle = '#7a3b1c'; g.beginPath(); g.ellipse(280, 330 + b, 26, 48, 0.3, 0, 7); g.fill(); g.stroke();
  g.fillStyle = '#c9a23a'; g.beginPath(); g.rect(270, 390 + b, 40, 34); g.fill(); g.stroke(); // barrel
  g.beginPath(); g.moveTo(55, 450 + b); g.quadraticCurveTo(10, 380 + b + Math.sin((o.t || 0) * 12) * 30, 30, 340 + b); g.stroke();
}
// card factory: canvas texture redrawn only when the visible state key changes
const CARD_W = 400, CARD_H = 700;
function makeCard() {
  const c = document.createElement('canvas'); c.width = CARD_W; c.height = CARD_H; const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding;
  const mat = new THREE.MeshBasicMaterial({ map: t, transparent: true, alphaTest: 0.4, side: THREE.DoubleSide, fog: true });
  const H = 1.9, W = H * CARD_W / CARD_H, geo = new THREE.PlaneGeometry(W, H); geo.translate(0, H / 2 - H * (10 / CARD_H), 0);
  const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.userData = { c, t, key: '' };
  m.customDepthMaterial = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking, map: t, alphaTest: 0.4 });
  return m;
}
function paintCard(m, o) {
  const key = JSON.stringify(o, (k, v) => typeof v === 'number' ? Math.round(v * 10) / 10 : v);
  if (m.userData.key === key) return; m.userData.key = key;
  const g = m.userData.c.getContext('2d'); g.clearRect(0, 0, CARD_W, CARD_H);
  if (o.kind === 'dog') drawDog(g, o); else drawBean(g, o);
  m.userData.t.needsUpdate = true;
}
