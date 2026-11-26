// World pieces built from primitives with painted textures. Sets are cached and toggled per shot.
const WORLD = {};
(function () {
  const { add, tbox, toon, T } = E;
  const M = {
    brick: () => toon(0xffffff, T('brick', () => P.brick())), brick2: () => toon(0xffffff, T('brick2', () => P.brick('#9c4a3a', '#4a2620'))),
    plank: () => toon(0xffffff, T('plank', () => P.plank())), stone: () => toon(0xffffff, T('stone', () => P.stone())), plaster: () => toon(0xffffff, T('plaster', () => P.plaster())),
    roof: () => toon(0xffffff, T('roof', () => P.roof())), roofb: () => toon(0xffffff, T('roofb', () => P.roof('#4a4f63'))),
  };
  const mats = {}; const m = k => mats[k] || (mats[k] = M[k] ? M[k]() : toon(k));
  WORLD.m = m;
  function ground(g, key, size, rep, y = 0) { const t = T(key, { grass: () => P.grass(), mud: () => P.mud(), cobble: () => P.cobble(), pitch: () => P.pitch(), plank: () => P.plank() }[key], rep, rep);
    const p = add(g, new THREE.PlaneGeometry(size, size), toon(0xffffff, t), [0, y, 0], [-Math.PI / 2, 0, 0], false, false); p.receiveShadow = true; return p; }
  function hills(g, col = '#6aa84f') { for (let i = 0; i < 14; i++) { const a = i / 14 * Math.PI * 2, r = 120 + (i % 3) * 20; add(g, new THREE.SphereGeometry(30 + (i % 4) * 8, 16, 10), toon(col), [Math.cos(a) * r, -14, Math.sin(a) * r], [0, 0, 0], true, false); }
    for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + 0.3; const c = add(g, new THREE.ConeGeometry(40, 70, 8), toon('#7d8fae'), [Math.cos(a) * 200, 20, Math.sin(a) * 200], [0, 0, 0], true, false); add(c, new THREE.ConeGeometry(16, 28, 8), toon('#f4f6fb'), [0, 21, 0], [0, 0, 0], false, false); } }
  function house(g, x, z, w = 4, d = 4, h = 4, ry = 0, wall = 'brick', roof = 'roof') {
    const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp);
    tbox(grp, w, h, d, m(wall), [0, h / 2, 0], [0, 0, 0], 2.5);
    const rg = new THREE.CylinderGeometry(0.01, w * 0.75, d * 1.05, 4, 1); rg.rotateY(Math.PI / 4); const r = add(grp, new THREE.ConeGeometry(w * 0.78, 1.8, 4), m(roof), [0, h + 0.9, 0], [0, Math.PI / 4, 0]); r.scale.set(1, 1, d / w);
    const win = toon(0xffffff, T('window', P.window));
    for (const dx of [-w / 4, w / 4]) add(grp, new THREE.PlaneGeometry(0.9, 0.9), win, [dx, h * 0.62, d / 2 + 0.02], [0, 0, 0], false, false);
    add(grp, new THREE.BoxGeometry(0.9, 1.7, 0.1), toon('#5a3a26'), [0, 0.85, d / 2 + 0.03]);
    const ch = add(grp, new THREE.BoxGeometry(0.5, 1.4, 0.5), m('brick2'), [w / 3, h + 1.3, 0]);
    return grp;
  }
  function tree(g, x, z, s = 1, kind = 'round') { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.scale.setScalar(s); g.add(grp);
    add(grp, new THREE.CylinderGeometry(0.18, 0.26, 1.6, 7), toon('#6b4a2e'), [0, 0.8, 0]);
    if (kind === 'pine') add(grp, new THREE.ConeGeometry(1.1, 3.4, 8), toon('#2f7a3e'), [0, 3, 0]); else add(grp, new THREE.IcosahedronGeometry(1.3, 1), toon('#3f9a45'), [0, 2.6, 0]);
    return grp; }
  function sign(g, text, p, ry = 0, w = 3.2, h = 1, bg, fg) { const grp = new THREE.Group(); grp.position.set(...p); grp.rotation.y = ry; g.add(grp);
    const t = P.tex(P.sign(text, bg, fg)); add(grp, new THREE.BoxGeometry(w, h, 0.12), [toon('#7a5236'), toon('#7a5236'), toon('#7a5236'), toon('#7a5236'), toon(0xffffff, t), toon('#7a5236')], [0, 0, 0]);
    return grp; }
  function postSign(g, text, p, ry = 0) { const grp = sign(g, text, [p[0], 2.2, p[2]], ry); for (const dx of [-1.2, 1.2]) add(grp, new THREE.CylinderGeometry(0.08, 0.08, 2.2, 6), toon('#5a3a26'), [dx, -1.1, -0.1]); return grp; }
  function chimneyFactory(g, x, z, label, ry = 0) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp);
    tbox(grp, 14, 6, 7, m('brick'), [0, 3, 0], [0, 0, 0], 2.5); add(grp, new THREE.BoxGeometry(14.6, 0.6, 7.6), toon('#4a2f2a'), [0, 6.2, 0]);
    const win = toon(0xffffff, T('window', P.window)); for (let i = -2; i <= 2; i++) add(grp, new THREE.PlaneGeometry(1.6, 1.8), win, [i * 2.6, 3.6, 3.52], [0, 0, 0], false, false);
    const anchors = []; for (const cx of [-4.5, 4.5]) { add(grp, new THREE.CylinderGeometry(0.6, 0.8, 8, 10), m('brick2'), [cx, 10, -1.5]); anchors.push(new THREE.Vector3(cx, 14.2, -1.5)); }
    if (label) sign(grp, label, [0, 5.1, 3.62], 0, 5.2, 1.5);
    add(grp, new THREE.BoxGeometry(3, 3.6, 0.2), toon('#5a3a26'), [0, 1.8, 3.55]);
    grp.userData.smoke = anchors; return grp; }
  function cannon(g, x, z, ry = 0, s = 1) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; grp.scale.setScalar(s); g.add(grp);
    add(grp, new THREE.CylinderGeometry(0.22, 0.34, 2.2, 12), toon('#3d3f48'), [0, 0.75, 0.2], [Math.PI / 2 - 0.25, 0, 0]);
    for (const dx of [-0.45, 0.45]) add(grp, new THREE.CylinderGeometry(0.5, 0.5, 0.14, 14), toon('#7a5236'), [dx, 0.5, -0.1], [0, 0, Math.PI / 2]);
    return grp; }
  function goal(g, x, z, ry = 0, net = false) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp); const wm = toon('#f4f6fb');
    add(grp, new THREE.CylinderGeometry(0.07, 0.07, 2.44, 8), wm, [-3.66, 1.22, 0]); add(grp, new THREE.CylinderGeometry(0.07, 0.07, 2.44, 8), wm, [3.66, 1.22, 0]);
    add(grp, new THREE.CylinderGeometry(0.07, 0.07, 7.4, 8), wm, [0, 2.44, 0], [0, 0, Math.PI / 2]); return grp; }
  function stands(g, cols, rCol = '#3a3f66') { const crowd = toon(0xffffff, P.tex(P.crowd(cols), 6, 1));
    const side = (w, x, z, ry) => { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp);
      const s = add(grp, new THREE.BoxGeometry(w, 0.2, 9), crowd, [0, 4, 0], [0.55, 0, 0]); add(grp, new THREE.BoxGeometry(w, 1.2, 0.3), toon(rCol), [0, 0.6, -4]);
      add(grp, new THREE.BoxGeometry(w + 1, 0.5, 6), toon('#d8dde8'), [0, 10.2, 2.5]); for (let i = -2; i <= 2; i++) add(grp, new THREE.CylinderGeometry(0.15, 0.15, 10, 6), toon('#8a90a0'), [i * w / 5, 5, 4.6]); };
    side(54, 0, -22, 0); side(54, 0, 22, Math.PI); side(36, -33, 0, Math.PI / 2); side(36, 33, 0, -Math.PI / 2); }
  function floodlights(g) { for (const [x, z] of [[-30, -20], [30, -20], [-30, 20], [30, 20]]) { add(g, new THREE.CylinderGeometry(0.25, 0.35, 18, 8), toon('#8a90a0'), [x, 9, z]); add(g, new THREE.BoxGeometry(3, 1.6, 0.4), toon('#fff6c8'), [x, 18.5, z], [0, Math.atan2(-x, -z), 0]); } }
  function church(g, x, z, label, ry = 0) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp);
    tbox(grp, 6, 5, 11, m('stone'), [0, 2.5, 0], [0, 0, 0], 2.5); const r = add(grp, new THREE.ConeGeometry(4.6, 2.6, 4), m('roofb'), [0, 6.3, 0], [0, Math.PI / 4, 0]); r.scale.set(1, 1, 1.9);
    tbox(grp, 2.6, 10, 2.6, m('stone'), [0, 5, 6], [0, 0, 0], 2.5); add(grp, new THREE.ConeGeometry(1.9, 5, 4), m('roofb'), [0, 12.5, 6], [0, Math.PI / 4, 0]);
    add(grp, new THREE.BoxGeometry(0.18, 1.4, 0.18), toon('#e0c050'), [0, 15.6, 6]); add(grp, new THREE.BoxGeometry(0.8, 0.18, 0.18), toon('#e0c050'), [0, 15.8, 6]);
    add(grp, new THREE.BoxGeometry(1.4, 2.4, 0.2), toon('#5a3a26'), [0, 1.2, 7.35]); if (label) sign(grp, label, [0, 3.4, 7.45], 0, 4.2, 0.9); return grp; }
  function rails(g, z, len = 80) { for (const dx of [-0.7, 0.7]) add(g, new THREE.BoxGeometry(len, 0.12, 0.1), toon('#6b6f78'), [0, 0.12, z + dx], [0, 0, 0], false); for (let i = -len / 2; i < len / 2; i += 1.2) add(g, new THREE.BoxGeometry(0.3, 0.1, 2.2), toon('#5a3a26'), [i, 0.05, z], [0, 0, 0], false, false); }
  function loco(g) { const grp = new THREE.Group(); g.add(grp);
    add(grp, new THREE.CylinderGeometry(1, 1, 5, 14), toon('#2f6b3a'), [0, 1.9, 0], [0, 0, Math.PI / 2]); add(grp, new THREE.BoxGeometry(2.4, 3, 2.4), toon('#2f6b3a'), [-3.4, 2, 0]);
    add(grp, new THREE.CylinderGeometry(0.35, 0.45, 1.6, 10), toon('#2b2b2b'), [1.8, 3.4, 0]); add(grp, new THREE.BoxGeometry(2.8, 0.25, 2.8), toon('#7a2a2a'), [-3.4, 3.6, 0]);
    for (const x of [-3, -1, 1.2]) for (const z of [-1.05, 1.05]) add(grp, new THREE.CylinderGeometry(0.7, 0.7, 0.2, 16), toon('#8a2a2a'), [x, 0.7, z], [Math.PI / 2, 0, 0]);
    grp.userData.smoke = [new THREE.Vector3(1.8, 4.3, 0)]; return grp; }
  function coal(g, x, z) { for (let i = 0; i < 4; i++) add(g, new THREE.ConeGeometry(1.4 + i * 0.3, 1.8, 7), toon('#2b2b30'), [x + i * 2.5, 0.9, z + (i % 2)]); }
  function fence(g, x0, x1, z) { for (let x = x0; x <= x1; x += 1.6) add(g, new THREE.BoxGeometry(0.12, 1.1, 0.12), toon('#8a6a4a'), [x, 0.55, z]); add(g, new THREE.BoxGeometry(x1 - x0, 0.1, 0.08), toon('#8a6a4a'), [(x0 + x1) / 2, 0.85, z]); }
  function table(g, x, z) { add(g, new THREE.BoxGeometry(3, 0.15, 1.6), WORLD.m('plank'), [x, 1.05, z]); for (const [a, b] of [[-1.3, -0.6], [1.3, -0.6], [-1.3, 0.6], [1.3, 0.6]]) add(g, new THREE.BoxGeometry(0.12, 1, 0.12), toon('#5a3a26'), [x + a, 0.5, z + b]); }

  // ---------- sets ----------
  const SETS = {
    town: o => { const g = new THREE.Group(); ground(g, 'cobble', 120, 30); hills(g);
      for (let i = -3; i <= 3; i++) { house(g, i * 5.2, -7, 4.6, 4, 4 + (i % 2), 0, i % 3 ? 'brick' : 'plaster'); house(g, i * 5.2, 16, 4.6, 4, 4 + ((i + 1) % 2), Math.PI, i % 2 ? 'brick' : 'brick2'); }
      for (let i = -2; i <= 2; i++) add(g, new THREE.CylinderGeometry(0.06, 0.06, 3.2, 6), toon('#2b2b30'), [i * 7 + 2, 1.6, -4.4]);
      if (o.factory) { const f = chimneyFactory(g, 0, -24, o.factory); g.userData.smoke = f.userData.smoke.map(v => f.localToWorld(v.clone())); }
      if (o.sign) postSign(g, o.sign, [o.signX || 3, 0, -4.2]);
      return g; },
    factory: o => { const g = new THREE.Group(); ground(g, 'cobble', 120, 30); hills(g); const f = chimneyFactory(g, 0, -6, o.label);
      g.updateMatrixWorld(true); g.userData.smoke = f.userData.smoke.map(v => f.localToWorld(v.clone()));
      for (let i = 0; i < (o.cannons || 4); i++) cannon(g, (i % 2 ? 1 : -1) * (5 + Math.floor(i / 2) * 2.6), 2.6, (i % 2 ? -1 : 1) * 0.35);
      house(g, -18, -2, 5, 5, 4, 0.4); house(g, 18, -2, 5, 5, 5, -0.4, 'brick2'); return g; },
    pitch: o => { const g = new THREE.Group(); ground(g, o.mud ? 'mud' : 'grass', 140, 30); hills(g);
      goal(g, 0, -12); fence(g, -14, 14, 8); if (o.houses !== false) for (let i = -3; i <= 3; i++) house(g, i * 6, -26, 5, 4, 4 + (i % 2), 0, i % 2 ? 'brick' : 'brick2');
      if (o.factory) { const f = chimneyFactory(g, 22, -30, null, -0.4); g.updateMatrixWorld(true); g.userData.smoke = f.userData.smoke.map(v => f.localToWorld(v.clone())); }
      if (o.sign) postSign(g, o.sign, [-7, 0, 7.6]); for (const [x, z] of [[-16, -16], [16, -15], [-19, 3]]) tree(g, x, z, 1.2); return g; },
    stadium: o => { const g = new THREE.Group(); ground(g, 'grass', 220, 50); hills(g, '#5a8a48');
      add(g, new THREE.PlaneGeometry(64, 40), toon(0xffffff, T('pitch', P.pitch, 6, 1)), [0, 0.02, 0], [-Math.PI / 2, 0, 0], false, false);
      stands(g, o.crowd || ['#d81e2a', '#ffffff']); floodlights(g); goal(g, -29, 0, Math.PI / 2); goal(g, 29, 0, -Math.PI / 2);
      if (o.sign) sign(g, o.sign, [0, 12.6, -24.9], 0, 16, 2.6, o.signBg, o.signFg); if (o.empty) g.userData.empty = true; return g; },
    railway: o => { const g = new THREE.Group(); ground(g, 'cobble', 120, 30); hills(g); rails(g, 0); const l = loco(g); l.position.x = o.locoX || 0;
      g.updateMatrixWorld(true); g.userData.loco = l; tbox(g, 16, 0.6, 4, m('plank'), [0, 0.3, -4], [0, 0, 0], 2); for (let i = -2; i <= 2; i++) add(g, new THREE.CylinderGeometry(0.1, 0.1, 4, 6), toon('#2f6b3a'), [i * 3.5, 2.6, -5.6]);
      add(g, new THREE.BoxGeometry(18, 0.3, 4.6), toon('#7a2a2a'), [0, 4.7, -4.6], [0.15, 0, 0]); if (o.sign) sign(g, o.sign, [0, 3.6, -6.3], 0, 6, 1);
      house(g, -16, -12, 6, 5, 5); house(g, 14, -12, 6, 5, 4, 0, 'brick2'); return g; },
    church: o => { const g = new THREE.Group(); ground(g, 'grass', 140, 30); hills(g); church(g, 0, -8, o.label);
      for (const [x, z] of [[-9, -4], [9, -6], [-12, 4], [12, 3]]) tree(g, x, z, 1.1, 'pine'); fence(g, -8, 8, 4); return g; },
    street_night: o => SETS.town(o),
    room: o => { const g = new THREE.Group(); ground(g, 'plank', 30, 8); tbox(g, 14, 6, 0.3, m('plaster'), [0, 3, -4], [0, 0, 0], 2.5); tbox(g, 0.3, 6, 10, m('plaster'), [-7, 3, 1], [0, 0, 0], 2.5);
      table(g, 0, -1); const win = toon(0xffffff, T('window', P.window)); add(g, new THREE.PlaneGeometry(2.2, 2.2), win, [3.5, 3.4, -3.84], [0, 0, 0], false, false);
      if (o.sign) sign(g, o.sign, [-2.5, 3.8, -3.8], 0, 4, 1.1); for (let i = 0; i < 6; i++) add(g, new THREE.CylinderGeometry(0.22, 0.22, 0.08, 14), toon('#e0b84a'), [-0.6 + i * 0.25, 1.17 + (i % 2) * 0.08, -1 + (i % 3) * 0.2]); return g; },
    park: o => { const g = new THREE.Group(); ground(g, 'grass', 220, 45); hills(g);
      for (let i = 0; i < 16; i++) tree(g, -8 + (i % 4) * 5.5 + (i * 7) % 3, -6 + Math.floor(i / 4) * 5, 1 + (i % 3) * 0.15);
      const st = (x, col, label) => { const grp = new THREE.Group(); grp.position.set(x, 0, -6); g.add(grp); tbox(grp, 12, 7, 10, toon(col), [0, 3.5, 0], [0, 0, 0], 3); add(grp, new THREE.BoxGeometry(13, 0.6, 11), toon('#d8dde8'), [0, 7.3, 0]); if (label) sign(grp, label, [0, 5, 5.1], 0, 8, 1.4); };
      st(-24, o.leftCol || '#c8102e', o.left); st(24, o.rightCol || '#1d46a0', o.right); return g; },
    coalyard: o => { const g = new THREE.Group(); ground(g, 'cobble', 120, 30); hills(g, '#647a4a'); coal(g, -6, -4); rails(g, 4, 60); house(g, 10, -6, 6, 5, 4, -0.3, 'brick2'); return g; },
  };
  const cache = {}; let active = null;
  WORLD.use = (key, opts = {}) => { const k = key + JSON.stringify(opts); if (!cache[k]) { cache[k] = SETS[key](opts); cache[k].visible = false; E.scene.add(cache[k]); cache[k].updateMatrixWorld(true); }
    if (active && active !== cache[k]) active.visible = false; active = cache[k]; active.visible = true; return active; };
})();
