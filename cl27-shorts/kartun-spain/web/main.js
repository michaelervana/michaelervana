// Story runtime: picks the shot for frame f, places the set, cards, props, photo pop-ups and effects, moves the camera, draws the HUSS gag.
(async function () {
  const S = STORIES[new URLSearchParams(location.search).get('id')];
  const TIMING = window.TIMING[S.id];
  const DUR = TIMING.dur, N = Math.round(DUR * FPS);
  // optional real photos in img/<key>.jpg|png (skipped quietly when missing)
  await Promise.all((S.photos || []).map(k => new Promise(res => { const tl = new THREE.TextureLoader(); let tried = 0; const exts = ['.jpg', '.png'];
    const next = () => { if (tried >= exts.length) return res(); tl.load(`img/${k}${exts[tried++]}`, t => { t.encoding = THREE.sRGBEncoding; WORLD.PHOTOS[k] = t; res(); }, undefined, next); }; next(); })));
  const has = k => !!WORLD.tex(k);
  const starts = S.shots.map((s, i) => { if (i === 0) return 0; const L = TIMING.lines[s.from];
    return s.half !== undefined ? L.t0 + (L.t1 - L.t0) * s.half : L.t0 - 0.12; });
  S.huss = S.huss.filter(h => h < DUR - 2.2);
  const cards = []; const getCard = i => cards[i] || (cards[i] = (() => { const m = makeCard(); E.scene.add(m); return m; })());
  const blob = new THREE.Mesh(new THREE.CircleGeometry(0.55, 20), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.25, depthWrite: false }));
  const blobs = []; const getBlob = i => blobs[i] || (blobs[i] = (() => { const b = blob.clone(); b.rotation.x = -Math.PI / 2; E.scene.add(b); E.mirrorHide.push(b); return b; })());
  const balls = []; const getBall = i => balls[i] || (balls[i] = (() => { const b = WORLD.obj('ball'); E.scene.add(b); return b; })());
  const smokeMat = new THREE.SpriteMaterial({ map: P.tex(P.smoke()), transparent: true, depthWrite: false, opacity: 0.85 });
  const smokes = []; for (let i = 0; i < 60; i++) { const s = new THREE.Sprite(smokeMat.clone()); s.visible = false; E.scene.add(s); smokes.push(s); }
  const coinMat = E.toon('#e8c050'); const coins = []; for (let i = 0; i < 40; i++) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.05, 14), coinMat); c.visible = false; E.scene.add(c); coins.push(c); }
  const conf = []; for (let i = 0; i < 90; i++) { const c = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.1), new THREE.MeshBasicMaterial({ color: (S.confetti || ['#ffd23d', '#ffffff', S.accent || '#d81e2a'])[i % 3], side: THREE.DoubleSide })); c.visible = false; E.scene.add(c); conf.push(c); }
  const objs = {}; const getObj = (kind, i) => { const k = kind + i; if (!objs[k]) { objs[k] = WORLD.obj(kind); E.scene.add(objs[k]); } return objs[k]; };
  const pops = {}; const getPop = (key, h, style) => { const k = key + h + style; if (!pops[k] && style === 'badge') { const g = new THREE.Group(); const b = WORLD.obj('badge_' + key); b.scale.setScalar(h); g.add(b); E.popGroup.add(g); pops[k] = g; }
    if (!pops[k]) { const g = new THREE.Group(); WORLD.frame(g, key, [0, 0, 0], 0, h, style || 'white');
      const sh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35, depthWrite: false })); const fr = g.children[0], w = h * (WORLD.tex(key).image.width / WORLD.tex(key).image.height);
      sh.scale.set(w + h * 0.2, h * 1.2, 1); sh.position.set(0.12 * h, -0.12 * h, -0.08); if (style !== 'none') g.add(sh); E.popGroup.add(g); pops[k] = g; } return pops[k]; };
  const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const val = (v, t, u) => typeof v === 'function' ? v(t, u) : v;
  const keyed = (arr, t, d) => { let r = d; for (const [k, v] of arr || []) if (t >= k) r = v; return r; };

  const hc = Object.assign(document.createElement('canvas'), { width: CARD_W * 2, height: CARD_H * 2 });
  function hussOverlay(g, t) {
    for (const h0 of S.huss) { const lt = t - h0; if (lt < 0 || lt > 2.2) continue;
      const pop = easeOut(clamp(lt / 0.25, 0, 1)) * (1 - easeOut(clamp((lt - 1.9) / 0.3, 0, 1)));
      const cg = hc.getContext('2d'); cg.setTransform(1, 0, 0, 1, 0, 0); cg.clearRect(0, 0, hc.width, hc.height); cg.setTransform(2, 0, 0, 2, 0, 0);
      const beat = (lt * 1.35) % 1, bounce = Math.abs(Math.sin(lt * Math.PI * 2.6));
      drawBean(cg, { kit: S.hussKit || S.kit, face: beat < 0.5 ? 'laugh' : 'smug', pose: 'hold', bob: bounce, squash: beat < 0.15 ? 0.6 : 0, hat: null });
      cg.fillStyle = '#c98a4a'; cg.strokeStyle = INK; cg.lineWidth = 8; cg.beginPath(); cg.arc(250, 600 - bounce * 120, 40, 0, 7); cg.fill(); cg.stroke();
      const w = 260 * SC * pop, h = w * CARD_H / CARD_W; g.drawImage(hc, W - w - 10 * SC, H - h + 40 * SC * (1 - pop) - 20 * SC, w, h);
      for (const b of [0.05, 0.75, 1.45]) { const k = lt - b; if (k < 0 || k > 0.6) continue; const s = back(clamp(k / 0.18, 0, 1)) * SC, a = 1 - clamp((k - 0.4) / 0.2, 0, 1);
        g.save(); g.globalAlpha = a; g.translate(W - (150 - (b * 40 - 30)) * SC, H - (330 + b * 60) * SC); g.rotate(-0.12 + b * 0.08); g.scale(s, s);
        g.font = '900 78px "Barlow Condensed", Impact, sans-serif'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 14; g.strokeStyle = INK; g.strokeText('HUSS!', 0, 0); g.fillStyle = '#ffd23d'; g.fillText('HUSS!', 0, 0); g.restore(); }
    }
  }

  const fwd = new THREE.Vector3(), up = new THREE.Vector3(), right = new THREE.Vector3();
  window.renderFrame = f => {
    const t = f / FPS; let si = 0; while (si + 1 < starts.length && t >= starts[si + 1]) si++;
    const shot = S.shots[si], lt = t - starts[si], len = (si + 1 < starts.length ? starts[si + 1] : DUR) - starts[si], u = clamp(lt / len, 0, 1);
    const set = WORLD.use(shot.set, shot.opts || {});
    E.light(shot.light || S.light || 'day', shot.focus || [0, 0, 0]);
    WORLD.waveFlags(set, t); E.reflect = !!set.userData.wet; (set.userData.wet || []).forEach(w => w.material.uniforms.time.value = t);
    const acts = shot.actors || []; cards.forEach(c => c.visible = false); blobs.forEach(b => b.visible = false); balls.forEach(b => b.visible = false);
    const camState = camFromKeys(shot.cam, lt, si); E.setCam(camState); const cam = E.cam;
    acts.forEach((a, i) => {
      const m = getCard(i); m.visible = true; let x = val(a.x, lt, u), z = val(a.z, lt, u), walking = false;
      if (a.walk) { const [x0, z0, x1, z1, t0, t1] = a.walk, k = clamp((lt - t0) / (t1 - t0), 0, 1); x = lerp(x0, x1, k); z = lerp(z0, z1, k); walking = k > 0 && k < 1; }
      const y = val(a.y || 0, lt, u), seed = i * 1.7 + si;
      const hop = a.hop ? Math.abs(Math.sin(lt * a.hop)) * 0.25 : 0, enter = a.pop !== undefined ? back(clamp((lt - a.pop) / 0.3, 0, 1)) : 1;
      m.position.set(x, y + hop, z); const sc = (a.scale || 1) * Math.max(0.001, enter); m.scale.setScalar(sc);
      m.rotation.y = Math.atan2(camState.pos[0] - x, camState.pos[2] - z);
      const bob = Math.sin(lt * (walking ? 9 : 2.6) + seed) * (walking ? 0.6 : 0.35), blink = ((lt + seed * 0.7) % 3.1) < 0.12;
      paintCard(m, { kind: a.kind || 'bean', outfit: a.outfit, kit: a.kit, num: a.num, hat: a.hat, prop: keyed(a.propAt, lt, a.prop), skin: a.skin, hair: a.hair,
        face: keyed(a.faceAt, lt, val(a.face || 'smile', lt, u)), pose: keyed(a.poseAt, lt, val(a.pose || 'hang', lt, u)), bob, blink: a.kind === 'dog' ? false : blink,
        step: walking ? Math.sin(lt * 9 + seed) : 0, armSwing: walking ? Math.sin(lt * 9 + seed) * 0.8 : Math.sin(lt * 1.8 + seed) * 0.15, look: Math.sin(lt * 0.8 + seed) * 0.6, t: lt });
      if (a.ball3d) { const bl = getBall(i), ph = lt * 4.2 + seed, kk = Math.abs(Math.sin(ph)); bl.visible = true; bl.position.set(x + 0.34 * sc, 0.22 + kk * 0.95 + hop, z + 0.2); bl.rotation.set(lt * 6, lt * 2, 0); }
      const b = getBlob(i); b.visible = true; b.position.set(x, 0.05, z); b.scale.setScalar(sc * (a.kind === 'dog' ? 1.6 : 1));
    });
    // animated 3D props
    Object.values(objs).forEach(o => o.visible = false);
    (shot.objs || []).forEach((o, i) => { const ob = getObj(o.kind, i); const s = (o.scale || 1) * (o.pop !== undefined ? back(clamp((lt - o.pop) / 0.35, 0, 1)) : 1); if (s <= 0.001) return;
      ob.visible = true; ob.position.set(...val(o.pos, lt, u)); ob.rotation.set(...(val(o.rot, lt, u) || [0, 0, 0])); ob.scale.setScalar(s); });
    // photo pop-ups attached to the camera (drawn crisp after depth of field)
    Object.values(pops).forEach(p => p.visible = false);
    cam.getWorldDirection(fwd); up.set(0, 1, 0).applyQuaternion(cam.quaternion); right.set(1, 0, 0).applyQuaternion(cam.quaternion);
    (shot.pop || []).forEach(p => { if (p.style === 'badge' ? !has('logo_' + p.key) : !has(p.key)) return; const k = lt - p.t0, kout = (p.t1 !== undefined ? p.t1 : len + 1) - lt; if (k < 0 || kout < -0.3) return;
      const g = getPop(p.key, p.h || 1, p.style); g.visible = true; const sIn = back(clamp(k / 0.32, 0, 1)), out = easeOut(clamp(-kout / 0.3 + 0, 0, 1)) || 0, outK = clamp(1 - kout / 0.3, 0, 1);
      const d = 3, x = (p.x || 0) + Math.sin(lt * 0.9) * 0.02, y = (p.y || 0) - outK * outK * 2.2 + Math.sin(lt * 1.3) * 0.02;
      g.position.copy(cam.position).addScaledVector(fwd, d).addScaledVector(right, x).addScaledVector(up, y);
      g.quaternion.copy(cam.quaternion); g.rotateZ((p.rot || 0) + (1 - sIn) * 0.5 + Math.sin(lt * 1.1) * 0.015); g.rotateY(p.spin ? (1 - easeOut(clamp(k / 1.3, 0, 1))) * Math.PI * 2 * Math.sign(p.spin) + Math.sin(k * 1.6) * 0.3 : Math.sin(lt * 0.8) * 0.12 + (p.yaw || 0)); g.scale.setScalar(Math.max(0.001, sIn));
    });
    // effects
    smokes.forEach(s => s.visible = false); coins.forEach(c => c.visible = false); conf.forEach(c => c.visible = false);
    const fx = shot.fx || [], F0 = shot.focus || [0, 0, 0];
    if (fx.includes('coins')) coins.forEach((c, i) => { const ph = (lt * 0.6 + rnd(i)) % 1; c.visible = true; c.position.set((rnd(i + 9) - 0.5) * 6 + F0[0], 6 - ph * 6.5, (rnd(i + 3) - 0.5) * 3 + F0[2]); c.rotation.set(lt * 5 + i, lt * 3, 0); });
    if (fx.includes('confetti')) conf.forEach((c, i) => { const ph = (lt * 0.4 + rnd(i)) % 1; c.visible = true; c.position.set((rnd(i + 5) - 0.5) * 12 + F0[0], 8 - ph * 8.5, (rnd(i + 7) - 0.5) * 7 + F0[2]); c.rotation.set(lt * 4 + i, lt * 6 + i * 2, 0); });
    E.rain(fx.includes('rain'), t);
    // lens flares: brightest on-screen light sources (set lamps, floodlights, the sun by day)
    const L = (set.userData.lights || []).map(l => ({ p: new THREE.Vector3(...l.p), c: l.c, i: l.i * (E.lightName === 'night' ? 1.3 : 0.55) }));
    if (!['night', 'palace', 'grey'].includes(E.lightName) && E.sunDir && !['palace', 'office', 'gym'].includes(shot.set)) L.push({ p: cam.position.clone().addScaledVector(E.sunDir, 300), c: [1, 0.92, 0.75], i: 0.9 });
    const cand = []; for (const l of L) { const v = l.p.clone().project(cam), dz = l.p.clone().applyMatrix4(cam.matrixWorldInverse).z; if (dz > -0.5) continue; const u = v.x * 0.5 + 0.5, w = v.y * 0.5 + 0.5;
      if (u < -0.1 || u > 1.1 || w < -0.1 || w > 1.1) continue; const edge = clamp(Math.min(u + 0.1, 1.1 - u, w + 0.1, 1.1 - w) * 8, 0, 1); cand.push({ u, w, z: -dz, i: l.i * edge * (shot.flare === undefined ? 1 : shot.flare), c: l.c }); }
    cand.sort((a, b) => b.i - a.i); const FL = E.post.uniforms.fl.value, FC = E.post.uniforms.flc.value;
    for (let k = 0; k < 4; k++) { const c = cand[k]; if (c && c.u >= 0 && c.u <= 1 && c.w >= 0 && c.w <= 1) { FL[k].set(c.u, c.w, c.z, c.i); FC[k].set(...c.c); } else FL[k].set(0, 0, 0, 0); }
    const flash = shot.flash ? clamp(1 - lt / 0.2, 0, 1) : 0;
    const g = E.draw(camState, shot.dof, flash);
    hussOverlay(g, t);
    return true;
  };
  window.TOTAL = N; window.ready = true;
})();
