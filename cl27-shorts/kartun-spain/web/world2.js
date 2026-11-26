// Spanish sets (Madrid / Barcelona plazas, palace, newsroom, gym, Swiss Alps), photo frames, waving flags and 3D props.
(function () {
  const { add, tbox, toon, T } = E, H = WORLD.h, SETS = WORLD.SETS;
  const plasterM = col => toon(0xffffff, T('pl' + col, () => P.plasterTint(col)));
  const TEXC = {}; // canvas-texture cache by key (painted or loaded photo)
  WORLD.tex = key => { if (TEXC[key]) return TEXC[key]; const src = WORLD.PHOTOS[key] || (WORLD.PAINT[key] && WORLD.PAINT[key]()); if (!src) return null;
    const t = src.isTexture ? src : P.tex(src); t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.repeat.set(1, 1); return (TEXC[key] = t); };
  WORLD.PHOTOS = {};
  WORLD.PAINT = { crestRM: () => P.crestRM(false, false), crestRMcrown: () => P.crestRM(true, false), crestRMmod: () => P.crestRM(true, true), crestFCB: () => P.crestFCB(),
    swiss: () => P.swissFlag(), newspaper: () => P.newspaper(), flagRM: () => P.crestFlag(() => (WORLD.PHOTOS.logo_rma || {}).image || P.crestRM(true, true), '#ffffff'), flagFCB: () => P.crestFlag(() => (WORLD.PHOTOS.logo_bar || {}).image || P.crestFCB(), '#004d98'),
    blaugrana: () => P.stripesFlag('#a50044', '#004d98'), senyera: () => P.stripesFlag('#f6c21c', '#d21f2b', 9) };
  const aspect = key => { const t = WORLD.tex(key), im = t && t.image; return im ? im.width / im.height : 0.8; };
  // framed picture: gold or wood moulding with ink, picture plane in front
  WORLD.frame = (g, key, p, ry = 0, h = 2, style = 'gold', rz = 0) => { const grp = new THREE.Group(); grp.position.set(...p); grp.rotation.set(0, ry, rz); g.add(grp);
    const w = h * aspect(key), b = h * 0.08, col = style === 'gold' ? '#d9a520' : style === 'white' ? '#f4f1e8' : '#7a5236';
    if (style !== 'none') { const fm = toon(col); add(grp, new THREE.BoxGeometry(w + 2 * b, b, 0.12), fm, [0, h / 2 + b / 2, 0]); add(grp, new THREE.BoxGeometry(w + 2 * b, b, 0.12), fm, [0, -h / 2 - b / 2, 0]);
      add(grp, new THREE.BoxGeometry(b, h, 0.12), fm, [-w / 2 - b / 2, 0, 0]); add(grp, new THREE.BoxGeometry(b, h, 0.12), fm, [w / 2 + b / 2, 0, 0]); add(grp, new THREE.BoxGeometry(w, h, 0.04), toon('#2a2024'), [0, 0, -0.04], [0, 0, 0], false); }
    const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: WORLD.tex(key), transparent: true, alphaTest: 0.05, toneMapped: false })); pic.position.z = 0.02; grp.add(pic); grp.userData.pic = pic; return grp; };
  WORLD.easel = (g, key, p, ry = 0, h = 1.6) => { const grp = new THREE.Group(); grp.position.set(...p); grp.rotation.y = ry; g.add(grp);
    for (const dx of [-0.5, 0.5]) add(grp, new THREE.CylinderGeometry(0.05, 0.05, 2.6, 6), toon('#7a5236'), [dx, 1.2, 0], [-0.12, 0, dx * 0.2]); add(grp, new THREE.CylinderGeometry(0.05, 0.05, 2.4, 6), toon('#7a5236'), [0, 1.1, -0.45], [0.35, 0, 0]);
    WORLD.frame(grp, key, [0, 1.15 + h / 2, 0.12], 0, h, 'gold', 0); return grp; };
  // flag on a pole; cloth vertices are waved each frame by main.js
  WORLD.flag = (g, key, p, ry = 0, w = 2.4, h = 1.6, pole = 6) => { const grp = new THREE.Group(); grp.position.set(...p); grp.rotation.y = ry; g.add(grp);
    add(grp, new THREE.CylinderGeometry(0.07, 0.09, pole, 8), toon('#c9ccd4'), [0, pole / 2, 0]); add(grp, new THREE.SphereGeometry(0.14, 10, 8), toon('#e0b020'), [0, pole + 0.1, 0]);
    const geo = new THREE.PlaneGeometry(w, h, 20, 4); geo.translate(w / 2, 0, 0); const cloth = new THREE.Mesh(geo, new THREE.MeshToonMaterial({ map: WORLD.tex(key), side: THREE.DoubleSide, gradientMap: null }));
    cloth.position.set(0.08, pole - h / 2 - 0.1, 0); cloth.castShadow = true; grp.add(cloth); cloth.userData.base = geo.attributes.position.array.slice(); cloth.userData.w = w;
    (g.userData.flags || (g.userData.flags = [])).push(cloth); return grp; };
  WORLD.waveFlags = (set, t) => { for (const c of set.userData.flags || []) { const a = c.geometry.attributes.position, b = c.userData.base;
    for (let i = 0; i < a.count; i++) { const x = b[i * 3], y = b[i * 3 + 1], k = x / c.userData.w; a.array[i * 3 + 2] = Math.sin(x * 2.2 - t * 6 + y * 0.6) * 0.22 * k; a.array[i * 3 + 1] = y - k * k * 0.12; } a.needsUpdate = true; c.geometry.computeVertexNormals(); } };

  // ---------- pieces ----------
  function block(g, x, z, w, h, d, ry, col, opts = {}) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.rotation.y = ry; g.add(grp);
    tbox(grp, w, h, d, plasterM(col), [0, h / 2, 0], [0, 0, 0], 3); add(grp, new THREE.BoxGeometry(w + 0.4, 0.4, d + 0.4), toon(opts.cornice || '#f4ecd8'), [0, h + 0.2, 0]);
    add(grp, new THREE.BoxGeometry(w + 0.2, 0.25, d + 0.2), toon('#c8693e'), [0, h + 0.52, 0]);
    const shut = toon(opts.shutter || '#2f6b5a'), glass = toon('#30344a'), rail = toon('#2a2420'); const cols = Math.max(2, Math.floor(w / 1.7)), floors = Math.max(1, Math.floor((h - 1.2) / 2.3));
    for (let f = 0; f < floors; f++) for (let i = 0; i < cols; i++) { const wx = -w / 2 + (i + 0.5) * w / cols, wy = 1.4 + f * 2.3 + (f ? 0.6 : 0);
      if (f === 0 && i === Math.floor(cols / 2)) { add(grp, new THREE.BoxGeometry(1.1, 2.2, 0.1), toon(opts.door || '#6a3a22'), [wx, 1.1, d / 2 + 0.05]); continue; }
      add(grp, new THREE.BoxGeometry(0.7, 1.3, 0.06), glass, [wx, wy, d / 2 + 0.03], [0, 0, 0], false, false);
      for (const s of [-1, 1]) add(grp, new THREE.BoxGeometry(0.36, 1.3, 0.06), shut, [wx + s * 0.55, wy, d / 2 + 0.05], [0, 0, 0], true, false);
      if (f > 0) { add(grp, new THREE.BoxGeometry(1.4, 0.1, 0.55), toon('#f4ecd8'), [wx, wy - 0.7, d / 2 + 0.28]); for (let k = -3; k <= 3; k++) add(grp, new THREE.BoxGeometry(0.04, 0.55, 0.04), rail, [wx + k * 0.2, wy - 0.38, d / 2 + 0.52], [0, 0, 0], false, false);
        add(grp, new THREE.BoxGeometry(1.4, 0.05, 0.05), rail, [wx, wy - 0.1, d / 2 + 0.52], [0, 0, 0], false, false);
        if ((i + f) % 3 === 0) add(grp, new THREE.SphereGeometry(0.22, 8, 6), toon((i + f) % 2 ? '#d8344a' : '#f08a2a'), [wx - 0.4, wy - 0.45, d / 2 + 0.4], [0, 0, 0], true, false); } }
    return grp; }
  function palm(g, x, z, s = 1, lean = 0.15) { const grp = new THREE.Group(); grp.position.set(x, 0, z); grp.scale.setScalar(s); grp.rotation.y = x * 1.7; g.add(grp); const bark = toon('#8a6a46');
    let px = 0, py = 0; for (let i = 0; i < 7; i++) { add(grp, new THREE.CylinderGeometry(0.17 - i * 0.012, 0.2 - i * 0.012, 0.95, 8), bark, [px, py + 0.47, 0], [0, 0, -lean * (i / 7)]); py += 0.92; px += lean * 0.9 * (i / 7); }
    const leaf = toon('#3f9a45'); for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; const l = add(grp, new THREE.ConeGeometry(0.32, 2.6, 4), leaf, [px + Math.cos(a) * 1.1, py + 0.1, Math.sin(a) * 1.1], [0, 0, 0]); l.rotation.set(Math.sin(a) * 1.25, 0, -Math.cos(a) * 1.25); l.scale.set(1, 1, 0.25); }
    add(grp, new THREE.SphereGeometry(0.28, 8, 6), toon('#7a5a2a'), [px, py - 0.1, 0]); return grp; }
  function lamp(g, x, z) { add(g, new THREE.CylinderGeometry(0.07, 0.1, 3.6, 8), toon('#2a2a30'), [x, 1.8, z]); add(g, new THREE.BoxGeometry(0.45, 0.55, 0.45), new THREE.MeshBasicMaterial({ color: '#fff2c0' }), [x, 3.85, z]); add(g, new THREE.ConeGeometry(0.4, 0.35, 4), toon('#2a2a30'), [x, 4.3, z], [0, Math.PI / 4, 0]); }
  function fountain(g, x, z) { add(g, new THREE.CylinderGeometry(2.2, 2.4, 0.6, 20), toon('#d8cfc0'), [x, 0.3, z]); add(g, new THREE.CylinderGeometry(1.9, 1.9, 0.1, 20), toon('#5ab0d8'), [x, 0.56, z], [0, 0, 0], false);
    add(g, new THREE.CylinderGeometry(0.25, 0.35, 1.6, 10), toon('#d8cfc0'), [x, 1.2, z]); add(g, new THREE.CylinderGeometry(0.9, 0.5, 0.3, 14), toon('#d8cfc0'), [x, 2.05, z]); }
  function chalet(g, x, z, ry = 0) { const grp = H.house(g, x, z, 5, 4.4, 3.6, ry, 'plank', 'roof'); return grp; }
  function wallbars(g, x, z, w = 4) { for (let i = 0; i <= w / 0.5; i++) add(g, new THREE.BoxGeometry(0.08, 3.4, 0.08), toon('#c8955a'), [x - w / 2 + i * 0.5, 1.7, z], [0, 0, 0], true, false); for (let k = 0; k < 9; k++) add(g, new THREE.CylinderGeometry(0.035, 0.035, w, 6), toon('#c8955a'), [x, 0.3 + k * 0.38, z + 0.06], [0, 0, Math.PI / 2], false, false); }
  function room(g, wall, floor = 'plank') { H.ground(g, floor, 30, 8); tbox(g, 16, 6.5, 0.3, wall, [0, 3.25, -4], [0, 0, 0], 2.5); tbox(g, 0.3, 6.5, 12, wall, [-8, 3.25, 2], [0, 0, 0], 2.5); tbox(g, 0.3, 6.5, 12, wall, [8, 3.25, 2], [0, 0, 0], 2.5);
    add(g, new THREE.BoxGeometry(16, 0.5, 0.4), toon('#f4ecd8'), [0, 0.25, -3.8]); }

  // ---------- sets ----------
  SETS.plaza = o => { const g = new THREE.Group(); H.ground(g, 'cobble', 140, 34); H.hills(g, '#9ab05a');
    const cols = o.palette || ['#e8b86a', '#f1e3c4', '#d9825b', '#f0d6a8', '#e9c48a'];
    for (let i = -3; i <= 3; i++) block(g, i * 6.2, -9, 6, 7 + (i % 2 === 0 ? 2.3 : 0), 5, 0, cols[(i + 3) % cols.length], { shutter: o.shutter });
    for (let i = -3; i <= 3; i++) block(g, i * 6.2, 18, 6, 7 + (i % 2 ? 2.3 : 0), 5, Math.PI, cols[(i + 5) % cols.length], { shutter: o.shutter });
    for (const x of [-9, 9]) lamp(g, x, -4.8); if (o.fountain !== false) fountain(g, o.fx || -6, 3.5);
    if (o.palms) for (const [x, z] of [[-12, -4], [12, -4.5], [-15, 6], [15, 7], [4.5, -5.2]]) palm(g, x, z, 1.05);
    if (o.sign) H.postSign(g, o.sign, [o.signX || 4, 0, -4.4]);
    if (o.flags) o.flags.forEach((k, i) => WORLD.flag(g, k, [-6 + i * 12, 6.6, -6.4], 0, 2.2, 1.5, 3));
    (o.frames || []).forEach(f => WORLD.frame(g, f.key, f.p, f.ry || 0, f.h || 2, f.style || 'gold'));
    (o.easels || []).forEach(f => WORLD.easel(g, f.key, f.p, f.ry || 0, f.h || 1.6));
    return g; };
  SETS.palace = o => { const g = new THREE.Group(); room(g, plasterM('#a8323a'), 'plank');
    add(g, new THREE.PlaneGeometry(3, 10), toon('#c8102e'), [0, 0.03, 1], [-Math.PI / 2, 0, 0], false, false);
    for (const x of [-6, -2.2, 2.2, 6]) { add(g, new THREE.CylinderGeometry(0.3, 0.35, 6.5, 12), toon('#f2e6c8'), [x, 3.25, -3.5]); add(g, new THREE.BoxGeometry(0.9, 0.3, 0.9), toon('#e0b020'), [x, 6.3, -3.5]); }
    add(g, new THREE.BoxGeometry(16, 0.35, 0.5), toon('#e0b020'), [0, 6.2, -3.7]);
    // throne
    const th = new THREE.Group(); th.position.set(0, 0, -2.4); g.add(th); add(th, new THREE.BoxGeometry(1.8, 0.4, 1.4), toon('#e0b020'), [0, 0.2, 0]); add(th, new THREE.BoxGeometry(1.4, 0.5, 1.1), toon('#c8102e'), [0, 0.65, 0]);
    add(th, new THREE.BoxGeometry(1.5, 2.6, 0.25), toon('#e0b020'), [0, 1.9, -0.55]); add(th, new THREE.BoxGeometry(1.1, 2.0, 0.1), toon('#c8102e'), [0, 1.9, -0.4]); for (const s of [-1, 1]) add(th, new THREE.BoxGeometry(0.25, 0.7, 1.1), toon('#e0b020'), [s * 0.8, 1.1, 0]);
    add(th, new THREE.SphereGeometry(0.25, 10, 8), toon('#e0b020'), [0, 3.4, -0.55]);
    (o.frames || []).forEach(f => WORLD.frame(g, f.key, f.p, f.ry || 0, f.h || 2, f.style || 'gold'));
    (o.easels || []).forEach(f => WORLD.easel(g, f.key, f.p, f.ry || 0, f.h || 1.6));
    if (o.flags) o.flags.forEach((k, i) => WORLD.flag(g, k, [i ? 4.2 : -5.4, 0, -3.2], 0, 1.3, 0.9, 4.2));
    return g; };
  SETS.office = o => { const g = new THREE.Group(); room(g, plasterM('#e8dcc2')); H.table(g, 0, -1);
    for (let i = 0; i < 4; i++) add(g, new THREE.BoxGeometry(0.9, 0.08 + i * 0.05, 0.65), toon('#efe4c8'), [-1 + i * 0.25, 1.17 + i * 0.03, -1.2 + (i % 2) * 0.1], [0, i * 0.3, 0]);
    // printing press
    const pr = new THREE.Group(); pr.position.set(5, 0, -2); g.add(pr); add(pr, new THREE.BoxGeometry(2.2, 1.6, 1.6), toon('#3a3f4a'), [0, 0.8, 0]); add(pr, new THREE.CylinderGeometry(0.45, 0.45, 2.3, 16), toon('#6b6f78'), [0, 1.9, 0], [0, 0, Math.PI / 2]);
    add(pr, new THREE.CylinderGeometry(0.7, 0.7, 0.12, 20), toon('#8a2a2a'), [1.25, 1.9, 0], [0, 0, Math.PI / 2]);
    H.sign(g, o.sign || 'LOS DEPORTES', [-2.5, 4.3, -3.8], 0, 5, 1.2, '#2a2420', '#efe4c8');
    (o.frames || []).forEach(f => WORLD.frame(g, f.key, f.p, f.ry || 0, f.h || 2, f.style || 'wood'));
    return g; };
  SETS.gym = o => { const g = new THREE.Group(); room(g, plasterM('#dcd2b8')); wallbars(g, -4, -3.7, 5); wallbars(g, 4.5, -3.7, 4);
    for (const x of [-1.2, 1.2]) { add(g, new THREE.CylinderGeometry(0.02, 0.02, 3, 4), toon('#5a4636'), [x, 4.8, 0], [0, 0, 0], false); add(g, new THREE.TorusGeometry(0.22, 0.05, 6, 14), toon('#c8955a'), [x, 3.2, 0]); }
    H.sign(g, o.sign || 'GIMNASIO SOLÉ', [0, 5.3, -3.8], 0, 5.6, 1.1);
    (o.frames || []).forEach(f => WORLD.frame(g, f.key, f.p, f.ry || 0, f.h || 2, f.style || 'wood'));
    if (o.flags) o.flags.forEach((k, i) => WORLD.flag(g, k, [i ? 6.4 : -7, 0, -3.1], 0, 1.4, 1, 4.4));
    return g; };
  SETS.alps = o => { const g = new THREE.Group(); H.ground(g, 'grass', 220, 45);
    for (let i = 0; i < 7; i++) { const x = -60 + i * 20, z = -70 - (i % 2) * 20, s = 1 + (i % 3) * 0.35; const c = add(g, new THREE.ConeGeometry(18 * s, 40 * s, 7), toon('#7d8fae'), [x, 20 * s - 4, z], [0, i, 0], true, false); add(c, new THREE.ConeGeometry(7.2 * s, 16 * s, 7), toon('#f4f6fb'), [0, 12 * s, 0], [0, 0, 0], false, false); }
    for (const [x, z, r] of [[-12, -10, 0.3], [11, -12, -0.4], [-20, 2, 0.8]]) chalet(g, x, z, r);
    for (let i = 0; i < 10; i++) H.tree(g, -24 + i * 5.3, -20 - (i % 3) * 3, 1.1, 'pine');
    if (o.goal !== false) H.goal(g, 0, -8); H.fence(g, -12, 12, 6);
    WORLD.flag(g, 'swiss', [6, 0, -4], 0, 1.8, 1.8, 5);
    if (o.sign) H.postSign(g, o.sign, [-5, 0, -3.6]);
    return g; };

  // ---------- wet ground: puddles with mirror reflections, rain ripples, damp darkening (glossy only indoors) ----------
  WORLD.wetMat = (rain, gloss) => new THREE.ShaderMaterial({ transparent: true, depthWrite: false,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor,
    uniforms: { tRef: { value: E.reflTex }, mVP: { value: E.mVP }, time: { value: 0 }, rain: { value: rain }, gloss: { value: gloss } },
    vertexShader: 'varying vec3 wp; void main(){ vec4 w = modelMatrix * vec4(position, 1.); wp = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `uniform sampler2D tRef; uniform mat4 mVP; uniform float time, rain, gloss; varying vec3 wp;
      float h21(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3. - 2. * f); return mix(mix(h21(i), h21(i + vec2(1, 0)), f.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), f.x), f.y); }
      float fbm(vec2 p){ return vn(p) * .55 + vn(p * 2.1 + 3.7) * .3 + vn(p * 4.3 + 9.1) * .15; }
      void main(){
        float n = fbm(wp.xz * 0.32), puddle = mix(1., smoothstep(0.5, 0.58, n), step(0.01, rain));
        vec2 rip = vec2(0.);
        for (int L = 0; L < 2; L++) { vec2 q = wp.xz * (1.7 + float(L) * 0.9) + float(L) * 7.3, id = floor(q), f = fract(q) - 0.5; float h = h21(id + float(L));
          vec2 o = vec2(h21(id + 3.1), h21(id + 5.7)) - 0.5; vec2 d = f - o * 0.6; float tt = fract(time * 0.8 + h), r = length(d), wv = r - tt * 0.5;
          rip += normalize(d + 1e-4) * sin(wv * 70.) * smoothstep(0.05, 0., abs(wv)) * (1. - tt) * rain; }
        vec4 p = mVP * vec4(wp, 1.); vec2 uv = p.xy / p.w * 0.5 + 0.5 + rip * 0.006;
        vec3 refl = vec3(0.); for (int i = 0; i < 5; i++) refl += texture2D(tRef, uv + vec2(0., (float(i) - 2.) * (0.003 + rain * 0.004))).rgb; refl /= 5.;
        vec3 V = normalize(cameraPosition - wp); float fres = 0.3 + 0.7 * pow(1. - abs(V.y), 2.5);
        float fade = smoothstep(70., 25., length(cameraPosition - wp));
        float a = clamp((puddle * (0.7 + 0.3 * rain) + gloss) * fres, 0., 0.92) * fade;
        float dark = clamp(a + rain * 0.22 * (1. - puddle) * fade, 0., 0.95);
        gl_FragColor = vec4(refl * a, dark); }` });
  WORLD.wet = (g, size, rain = 1, gloss = 0, y = 0.04) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), WORLD.wetMat(rain, gloss)); m.rotation.x = -Math.PI / 2; m.position.y = y; m.renderOrder = 1; g.add(m); E.mirrorHide.push(m); (g.userData.wet || (g.userData.wet = [])).push(m); return m; };
  // add wet layers + flare lights to every set when it is first built
  const wrap = (key, size, rain, gloss, lights) => { const f = SETS[key]; SETS[key] = o => { const g = f(o); WORLD.wet(g, size, o.dry ? 0 : rain, gloss); g.userData.lights = (g.userData.lights || []).concat(lights(o)); return g; }; };
  const flood = () => [[-30, 18.5, -20], [30, 18.5, -20], [-30, 18.5, 20], [30, 18.5, 20]].map(p => ({ p, c: [1, 0.95, 0.85], i: 1 }));
  wrap('stadium', 150, 1, 0, flood); wrap('plaza', 110, 1, 0, () => [[-9, 3.85, -4.8], [9, 3.85, -4.8]].map(p => ({ p, c: [1, 0.8, 0.5], i: 0.8 })));
  wrap('pitch', 110, 1, 0, () => []); wrap('alps', 110, 0.6, 0, () => []);
  wrap('palace', 30, 0, 0.35, () => [{ p: [-6, 6.2, -3.4], c: [1, 0.8, 0.5], i: 0.6 }, { p: [6, 6.2, -3.4], c: [1, 0.8, 0.5], i: 0.6 }]);
  wrap('office', 30, 0, 0.18, () => []); wrap('gym', 30, 0, 0.25, () => []);

  // ---------- animated 3D props ----------
  WORLD.obj = kind => { const g = new THREE.Group();
    if (kind === 'crown') { const gold = toon('#f2c230'); add(g, new THREE.CylinderGeometry(0.62, 0.55, 0.36, 20, 1, true), gold, [0, 0.18, 0]);
      for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2; add(g, new THREE.ConeGeometry(0.13, 0.55, 6), gold, [Math.cos(a) * 0.55, 0.6, Math.sin(a) * 0.55]); add(g, new THREE.SphereGeometry(0.08, 8, 6), toon(i % 2 ? '#c8102e' : '#2f6bd8'), [Math.cos(a) * 0.6, 0.2, Math.sin(a) * 0.6]); }
      add(g, new THREE.SphereGeometry(0.5, 14, 10, 0, 7, 0, 1.4), toon('#c8102e'), [0, 0.32, 0]); add(g, new THREE.BoxGeometry(0.08, 0.38, 0.08), gold, [0, 1.05, 0]); add(g, new THREE.BoxGeometry(0.26, 0.08, 0.08), gold, [0, 1.1, 0]); }
    if (kind === 'trophy') { const sil = toon('#e4e8f0'); const pts = [[0, 0], [0.42, 0], [0.42, 0.22], [0.16, 0.3], [0.12, 0.7], [0.2, 0.85], [0.5, 1.4], [0.55, 1.75], [0.52, 1.8]].map(([x, y]) => new THREE.Vector2(x, y));
      add(g, new THREE.LatheGeometry(pts, 20), sil, [0, 0, 0]); for (const s of [-1, 1]) add(g, new THREE.TorusGeometry(0.42, 0.06, 6, 18, Math.PI * 1.3), sil, [s * 0.62, 1.25, 0], [0, 0, s > 0 ? -1.2 : 1.2 + Math.PI * 0.7]);
      add(g, new THREE.CylinderGeometry(0.45, 0.48, 0.12, 20), toon('#6a4a32'), [0, 0.06, 0]); }
    if (kind === 'ball') { const t = T('leather', () => { const c = document.createElement('canvas'); c.width = 256; c.height = 128; const x = c.getContext('2d'); x.fillStyle = '#a8662e'; x.fillRect(0, 0, 256, 128);
        x.strokeStyle = '#4a2a14'; x.lineWidth = 3; for (let r = 0; r < 4; r++) { x.beginPath(); x.moveTo(0, 16 + r * 32); x.lineTo(256, 16 + r * 32); x.stroke(); for (let k = 0; k < 6; k++) { const xx = k * 43 + (r % 2) * 21; x.beginPath(); x.moveTo(xx, 16 + r * 32 - 32); x.lineTo(xx, 16 + r * 32); x.stroke(); } }
        x.fillStyle = 'rgba(0,0,0,.18)'; for (let k = 0; k < 6; k++) x.fillRect(k * 43 + 6, 20, 30, 24); x.strokeStyle = '#f0e0c0'; x.lineWidth = 2; for (let k = 0; k < 6; k++) { x.beginPath(); x.moveTo(120 + k * 5, 58); x.lineTo(126 + k * 5, 70); x.stroke(); }
        x.fillStyle = 'rgba(255,230,190,.35)'; x.fillRect(0, 20, 256, 14); return c; }); add(g, new THREE.SphereGeometry(0.2, 24, 16), toon(0xffffff, t), [0, 0, 0]); }
    if (kind.startsWith('badge_')) { const k = kind.slice(6), pts = window.BADGES[k]; const sh = new THREE.Shape(pts.map(([x, y]) => new THREE.Vector2(x, y)));
      const geo = new THREE.ExtrudeGeometry(sh, { depth: 0.09, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.018, bevelSegments: 3, curveSegments: 4 }); geo.translate(0, 0, -0.045); { const P2 = geo.attributes.position, U = geo.attributes.uv, g0 = geo.groups[0]; for (let i = g0.start; i < g0.start + g0.count; i++) if (P2.getZ(i) < 0) U.setX(i, -U.getX(i)); U.needsUpdate = true; }
      const base = WORLD.tex('logo_' + k), tex = base.clone(); tex.needsUpdate = true; tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping; tex.offset.set(0.5, 0.5); tex.repeat.set(1, 1);
      const face = new THREE.MeshToonMaterial({ map: tex, gradientMap: null }), rim = toon(k === 'rma' ? '#e8c040' : '#e0a820');
      add(g, geo, [face, rim], [0, 0, 0]); }
    if (kind === 'paperstack') { for (let i = 0; i < 6; i++) add(g, new THREE.BoxGeometry(0.9, 0.06, 0.65), toon('#efe4c8'), [0, i * 0.065, 0], [0, i * 0.2, 0]); }
    if (kind === 'newspaper') { const t = WORLD.tex('newspaper'); const m = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.48), new THREE.MeshBasicMaterial({ map: t, side: THREE.DoubleSide, toneMapped: false })); g.add(m); const hull = add(g, new THREE.BoxGeometry(1.12, 1.5, 0.01), toon('#efe4c8'), [0, 0, -0.012]); }
    return g; };
})();
