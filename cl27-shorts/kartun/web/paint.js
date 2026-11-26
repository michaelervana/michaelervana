// Painted canvas textures: flat colour fields with dark seams and a little hand-made noise.
const P = {};
(function () {
  const rnd = (s => () => (s = (s * 16807) % 2147483647) / 2147483647)(7);
  const C = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
  const tex = (c, rx = 1, ry = 1) => { const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(rx, ry); t.encoding = THREE.sRGBEncoding; t.anisotropy = 4; return t; };
  const speck = (g, w, h, n, a) => { for (let i = 0; i < n; i++) { g.fillStyle = `rgba(${rnd() < .5 ? '0,0,0' : '255,255,255'},${a * rnd()})`; g.fillRect(rnd() * w, rnd() * h, 2 + rnd() * 6, 2 + rnd() * 3); } };
  P.brick = (base = '#b5523b', seam = '#5a2a22') => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = seam; g.fillRect(0, 0, 256, 256);
    for (let y = 0; y < 8; y++) for (let x = -1; x < 5; x++) { const o = y % 2 ? 32 : 0; g.fillStyle = shade(base, 0.85 + rnd() * 0.3); g.fillRect(x * 64 + o + 3, y * 32 + 3, 58, 26); }
    speck(g, 256, 256, 300, .08); return c; };
  P.plank = (base = '#8a5a34', seam = '#3e2614') => { const c = C(256, 256), g = c.getContext('2d'); for (let i = 0; i < 6; i++) { g.fillStyle = shade(base, 0.85 + rnd() * 0.3); g.fillRect(0, i * 43, 256, 43); g.fillStyle = seam; g.fillRect(0, i * 43, 256, 4);
      for (let k = 0; k < 3; k++) { g.strokeStyle = 'rgba(0,0,0,.18)'; g.beginPath(); g.moveTo(0, i * 43 + 10 + k * 10); g.bezierCurveTo(80, i * 43 + 6 + k * 10, 170, i * 43 + 16 + k * 10, 256, i * 43 + 10 + k * 10); g.stroke(); } }
    return c; };
  P.stone = (base = '#9a9488', seam = '#4a463f') => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = seam; g.fillRect(0, 0, 256, 256);
    for (let y = 0; y < 5; y++) for (let x = -1; x < 4; x++) { const o = y % 2 ? 40 : 0; g.fillStyle = shade(base, 0.85 + rnd() * 0.3); g.beginPath(); g.roundRect(x * 80 + o + 4, y * 52 + 4, 72, 44, 10); g.fill(); } speck(g, 256, 256, 200, .08); return c; };
  P.grass = (a = '#4f9a3a', b = '#5fae45') => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = a; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 900; i++) { g.strokeStyle = rnd() < .5 ? b : shade(a, 0.8); g.lineWidth = 2; const x = rnd() * 256, y = rnd() * 256; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (rnd() - .5) * 6, y - 6 - rnd() * 6); g.stroke(); } return c; };
  P.pitch = (a = '#3f9a3c', b = '#4cae45') => { const c = C(512, 512), g = c.getContext('2d'); for (let i = 0; i < 8; i++) { g.fillStyle = i % 2 ? a : b; g.fillRect(i * 64, 0, 64, 512); } speck(g, 512, 512, 900, .05); return c; };
  P.mud = () => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = '#6f8a3a'; g.fillRect(0, 0, 256, 256); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(110,80,45,${.3 + rnd() * .4})`; g.beginPath(); g.ellipse(rnd() * 256, rnd() * 256, 10 + rnd() * 30, 6 + rnd() * 16, rnd() * 3, 0, 7); g.fill(); } speck(g, 256, 256, 300, .1); return c; };
  P.cobble = () => P.stone('#7d776d', '#3d3a34');
  P.roof = (base = '#5b3a33') => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = shade(base, .6); g.fillRect(0, 0, 256, 256);
    for (let y = 0; y < 8; y++) for (let x = -1; x < 9; x++) { g.fillStyle = shade(base, .85 + rnd() * .3); g.beginPath(); g.roundRect(x * 32 + (y % 2) * 16 + 2, y * 32 + 2, 28, 30, [0, 0, 10, 10]); g.fill(); } return c; };
  P.plaster = (base = '#e8dcc2') => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = base; g.fillRect(0, 0, 256, 256); speck(g, 256, 256, 500, .06); return c; };
  P.crowd = (cols) => { const c = C(512, 256), g = c.getContext('2d'); g.fillStyle = '#2b2440'; g.fillRect(0, 0, 512, 256);
    for (let y = 0; y < 12; y++) for (let x = 0; x < 40; x++) { const cx = x * 13 + (y % 2) * 6 + 4, cy = y * 21 + 10; g.fillStyle = cols[Math.floor(rnd() * cols.length)]; g.beginPath(); g.ellipse(cx, cy + 8, 6, 7, 0, 0, 7); g.fill(); g.fillStyle = '#f0c8a0'; g.beginPath(); g.arc(cx, cy, 4, 0, 7); g.fill(); } return c; };
  P.window = () => { const c = C(128, 128), g = c.getContext('2d'); g.fillStyle = '#2b2a38'; g.fillRect(0, 0, 128, 128); g.fillStyle = '#f6d27a'; g.fillRect(12, 12, 46, 46); g.fillRect(70, 12, 46, 46); g.fillRect(12, 70, 46, 46); g.fillRect(70, 70, 46, 46); return c; };
  // carved / painted sign board with text; reads left to right on the front face
  P.sign = (text, bg = '#e9dcb8', fg = '#3b1e3a', w = 512, h = 160) => { const c = C(w, h), g = c.getContext('2d'); g.fillStyle = bg; g.fillRect(0, 0, w, h); g.strokeStyle = fg; g.lineWidth = 10; g.strokeRect(8, 8, w - 16, h - 16);
    g.fillStyle = fg; g.textAlign = 'center'; g.textBaseline = 'middle'; let s = 96; g.font = `900 ${s}px "Barlow Condensed", Impact, sans-serif`; while (g.measureText(text).width > w - 50 && s > 20) { s -= 4; g.font = `900 ${s}px "Barlow Condensed", Impact, sans-serif`; } g.fillText(text, w / 2, h / 2 + 4); return c; };
  P.cloud = () => { const c = C(256, 128), g = c.getContext('2d'); g.fillStyle = '#fff'; [[70, 80, 46], [120, 62, 56], [180, 80, 44], [140, 92, 50]].forEach(([x, y, r]) => { g.beginPath(); g.arc(x, y, r, 0, 7); g.fill(); }); g.fillStyle = 'rgba(160,175,210,.45)'; g.fillRect(20, 96, 216, 40); g.globalCompositeOperation = 'destination-in'; g.beginPath(); [[70, 80, 46], [120, 62, 56], [180, 80, 44], [140, 92, 50]].forEach(([x, y, r]) => { g.moveTo(x + r, y); g.arc(x, y, r, 0, 7); }); g.fill(); return c; };
  P.tex = tex;
  P.smoke = () => { const c = C(128, 128), gr = c.getContext('2d').createRadialGradient(64, 64, 0, 64, 64, 64); gr.addColorStop(0, 'rgba(235,235,240,1)'); gr.addColorStop(.6, 'rgba(210,210,220,.7)'); gr.addColorStop(1, 'rgba(200,200,210,0)'); const g = c.getContext('2d'); g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return c; };
})();
function shade(hex, k) { const n = parseInt(hex.slice(1), 16), r = Math.min(255, ((n >> 16) & 255) * k) | 0, g = Math.min(255, ((n >> 8) & 255) * k) | 0, b = Math.min(255, (n & 255) * k) | 0; return `rgb(${r},${g},${b})`; }
