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
// ---------- Spanish story paintings: crests (cartoon renditions), flags, the 1899 newspaper notice ----------
(function () {
  const C = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
  const ink = '#3b1e3a', F = s => `900 ${s}px "Barlow Condensed", Impact, sans-serif`;
  P.plasterTint = base => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = base; g.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 700; i++) { g.fillStyle = `rgba(${Math.random() < .5 ? '0,0,0' : '255,255,255'},${.05 * Math.random()})`; g.fillRect(Math.random() * 256, Math.random() * 256, 3 + Math.random() * 8, 2 + Math.random() * 4); } return c; };
  P.cobbleWarm = () => P.stone('#b49a7a', '#5a4634');
  // Madrid FC monogram badge (1902 style), optional crown and purple band (later style)
  P.crestRM = (crown = false, band = false) => { const c = C(512, 640), g = c.getContext('2d'); const cx = 256, cy = crown ? 380 : 320, r = 210;
    g.lineJoin = 'round'; g.lineWidth = 16; g.strokeStyle = ink;
    g.fillStyle = '#ffffff'; g.beginPath(); g.arc(cx, cy, r, 0, 7); g.fill(); g.stroke();
    g.strokeStyle = '#e0b020'; g.lineWidth = 14; g.beginPath(); g.arc(cx, cy, r - 22, 0, 7); g.stroke();
    if (band) { g.save(); g.beginPath(); g.arc(cx, cy, r - 30, 0, 7); g.clip(); g.translate(cx, cy); g.rotate(-0.7); g.fillStyle = '#5b3e9a'; g.fillRect(-r, -34, 2 * r, 68); g.restore(); }
    g.fillStyle = '#e0b020'; g.strokeStyle = ink; g.lineWidth = 10; g.textAlign = 'center'; g.textBaseline = 'middle';
    g.font = `900 210px Georgia, serif`; g.strokeText('M', cx, cy + 6); g.fillText('M', cx, cy + 6);
    g.font = `900 150px Georgia, serif`; g.strokeText('C', cx - 70, cy + 10); g.fillText('C', cx - 70, cy + 10); g.strokeText('F', cx + 72, cy + 10); g.fillText('F', cx + 72, cy + 10);
    if (crown) { g.fillStyle = '#f2c230'; g.strokeStyle = ink; g.lineWidth = 14; g.beginPath(); g.moveTo(cx - 150, cy - r + 30); g.lineTo(cx - 170, cy - r - 110); g.lineTo(cx - 85, cy - r - 40); g.lineTo(cx, cy - r - 150); g.lineTo(cx + 85, cy - r - 40); g.lineTo(cx + 170, cy - r - 110); g.lineTo(cx + 150, cy - r + 30); g.closePath(); g.fill(); g.stroke();
      g.fillStyle = '#c8102e'; for (const dx of [-90, 0, 90]) { g.beginPath(); g.arc(cx + dx, cy - r - 4, 18, 0, 7); g.fill(); g.stroke(); } g.fillStyle = '#ffffff'; g.beginPath(); g.arc(cx, cy - r - 160, 20, 0, 7); g.fill(); g.stroke(); }
    return c; };
  // FC Barcelona-style shield (cartoon rendition): St George cross, Catalan stripes, FCB band, blaugrana stripes and ball
  P.crestFCB = () => { const c = C(512, 640), g = c.getContext('2d'); g.lineJoin = 'round';
    const shield = () => { g.beginPath(); g.moveTo(60, 70); g.quadraticCurveTo(256, 20, 452, 70); g.lineTo(452, 300); g.quadraticCurveTo(440, 520, 256, 610); g.quadraticCurveTo(72, 520, 60, 300); g.closePath(); };
    g.save(); shield(); g.clip();
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, 256, 230); g.fillStyle = '#d21f2b'; g.fillRect(126, 0, 44, 230); g.fillRect(0, 120, 256, 44);
    g.fillStyle = '#f6c21c'; g.fillRect(256, 0, 256, 230); g.fillStyle = '#d21f2b'; for (let i = 0; i < 4; i++) g.fillRect(286 + i * 44, 0, 22, 230);
    g.fillStyle = '#004d98'; g.fillRect(0, 290, 512, 400); g.fillStyle = '#a50044'; for (let x = 60; x < 460; x += 96) g.fillRect(x + 48, 290, 48, 400);
    g.fillStyle = '#f6c21c'; g.beginPath(); g.arc(256, 450, 62, 0, 7); g.fill(); g.strokeStyle = ink; g.lineWidth = 10; g.stroke(); g.beginPath(); g.moveTo(206, 420); g.quadraticCurveTo(256, 470, 306, 420); g.moveTo(206, 480); g.quadraticCurveTo(256, 430, 306, 480); g.stroke();
    g.fillStyle = '#ffffff'; g.fillRect(0, 230, 512, 60); g.strokeStyle = ink; g.lineWidth = 8; g.beginPath(); g.moveTo(0, 230); g.lineTo(512, 230); g.moveTo(0, 290); g.lineTo(512, 290); g.stroke();
    g.fillStyle = '#e0a020'; g.font = F(64); g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineWidth = 8; g.strokeText('F C B', 256, 262); g.fillText('F C B', 256, 262);
    g.restore(); g.strokeStyle = ink; g.lineWidth = 16; shield(); g.stroke(); g.strokeStyle = '#e0b020'; g.lineWidth = 8; g.save(); g.translate(256, 320); g.scale(0.94, 0.95); g.translate(-256, -320); shield(); g.stroke(); g.restore();
    return c; };
  P.swissFlag = () => { const c = C(256, 256), g = c.getContext('2d'); g.fillStyle = '#d52b1e'; g.fillRect(0, 0, 256, 256); g.fillStyle = '#fff'; g.fillRect(104, 48, 48, 160); g.fillRect(48, 104, 160, 48); return c; };
  P.stripesFlag = (a, b, n = 5) => { const c = C(384, 256), g = c.getContext('2d'); for (let i = 0; i < n; i++) { g.fillStyle = i % 2 ? b : a; g.fillRect(i * 384 / n, 0, 384 / n + 1, 256); } return c; };
  P.crestFlag = (crest, bg) => { const c = C(384, 256), g = c.getContext('2d'); g.fillStyle = bg; g.fillRect(0, 0, 384, 256); const k = crest(), kw = k.width || k.naturalWidth, kh = k.height || k.naturalHeight, sc = Math.min(210 / kw, 220 / kh); g.drawImage(k, 192 - kw * sc / 2, 128 - kh * sc / 2, kw * sc, kh * sc); return c; };
  // the 22 October 1899 notice in Los Deportes (paraphrased, Spanish)
  P.newspaper = () => { const c = C(640, 860), g = c.getContext('2d'); g.fillStyle = '#efe4c8'; g.fillRect(0, 0, 640, 860);
    for (let i = 0; i < 2500; i++) { g.fillStyle = `rgba(120,90,50,${Math.random() * .08})`; g.fillRect(Math.random() * 640, Math.random() * 860, 2, 2); }
    g.fillStyle = '#2a2420'; g.textAlign = 'center'; g.font = '900 92px Georgia, serif'; g.fillText('LOS DEPORTES', 320, 110); g.font = 'italic 26px Georgia, serif'; g.fillText('Barcelona · 22 de Octubre de 1899', 320, 152);
    g.fillRect(30, 170, 580, 6); g.fillRect(30, 182, 580, 2);
    for (let col = 0; col < 2; col++) for (let i = 0; i < 26; i++) { const x = 40 + col * 300, y = 210 + i * 24; if (col === 1 && i > 6 && i < 22) continue; g.fillStyle = 'rgba(42,36,32,.55)'; g.fillRect(x, y, 260 - (i % 5 === 4 ? 90 : Math.random() * 30), 9); }
    g.strokeStyle = '#2a2420'; g.lineWidth = 5; g.strokeRect(330, 370, 270, 356); g.fillStyle = '#fff8e0'; g.fillRect(333, 373, 264, 350);
    g.fillStyle = '#2a2420'; g.font = '900 40px Georgia, serif'; g.fillText('FOOT-BALL', 465, 420);
    g.font = '21px Georgia, serif'; g.textAlign = 'left'; ['Nuestro amigo el Sr. Hans', 'Gamper, deseoso de organizar', 'algunos partidos de foot-ball', 'en Barcelona, ruega a cuantos', 'sientan afición por dicho', 'deporte, se pongan en', 'relación con él.', '', '   ¡Se buscan jugadores!'].forEach((l, i) => g.fillText(l, 344, 460 + i * 28));
    g.strokeStyle = '#c8102e'; g.lineWidth = 8; g.beginPath(); g.ellipse(465, 548, 150, 196, 0.05, 0, 7); g.stroke();
    return c; };
  P.portrait = (title, bg = '#6a3a2a') => { const c = C(400, 520), g = c.getContext('2d'); g.fillStyle = bg; g.fillRect(0, 0, 400, 520); g.fillStyle = 'rgba(255,220,160,.25)'; g.beginPath(); g.ellipse(200, 230, 150, 200, 0, 0, 7); g.fill(); return c; };
})();
