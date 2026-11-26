// Story runtime: picks the shot for frame f, places the set, cards and effects, moves the camera, draws the HUSS gag.
(function () {
  const S = STORIES[new URLSearchParams(location.search).get('id')];
  const TIMING = window.TIMING[S.id];
  const DUR = TIMING.dur, N = Math.round(DUR * FPS);
  // shot start times: first shot at 0, others just before their first line
  const starts = S.shots.map((s, i) => { if (i === 0) return 0; const L = TIMING.lines[s.from];
    return s.half !== undefined ? L.t0 + (L.t1 - L.t0) * s.half : L.t0 - 0.12; });
  S.huss = S.huss.filter(h => h < DUR - 2.2);
  const cards = []; const getCard = i => cards[i] || (cards[i] = (() => { const m = makeCard(); E.scene.add(m); return m; })());
  const blob = new THREE.Mesh(new THREE.CircleGeometry(0.55, 20), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.25, depthWrite: false }));
  const blobs = []; const getBlob = i => blobs[i] || (blobs[i] = (() => { const b = blob.clone(); b.rotation.x = -Math.PI / 2; E.scene.add(b); return b; })());
  const smokeMat = new THREE.SpriteMaterial({ map: P.tex(P.smoke()), transparent: true, depthWrite: false, opacity: 0.85 });
  const smokes = []; for (let i = 0; i < 60; i++) { const s = new THREE.Sprite(smokeMat.clone()); s.visible = false; E.scene.add(s); smokes.push(s); }
  const coinMat = E.toon('#e8c050'); const coins = []; for (let i = 0; i < 40; i++) { const c = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.05, 14), coinMat); c.visible = false; E.scene.add(c); coins.push(c); }
  const conf = []; for (let i = 0; i < 70; i++) { const c = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.1), new THREE.MeshBasicMaterial({ color: ['#ffd23d', '#ffffff', S.accent || '#d81e2a'][i % 3], side: THREE.DoubleSide })); c.visible = false; E.scene.add(c); conf.push(c); }
  const rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
  const val = (v, t, u) => typeof v === 'function' ? v(t, u) : v;
  const keyed = (arr, t, d) => { let r = d; for (const [k, v] of arr || []) if (t >= k) r = v; return r; };

  function hussOverlay(g, t) {
    for (const h0 of S.huss) { const lt = t - h0; if (lt < 0 || lt > 2.2) continue;
      const pop = easeOut(clamp(lt / 0.25, 0, 1)) * (1 - easeOut(clamp((lt - 1.9) / 0.3, 0, 1)));
      const c = hussOverlay.c || (hussOverlay.c = Object.assign(document.createElement('canvas'), { width: CARD_W, height: CARD_H }));
      const cg = c.getContext('2d'); cg.clearRect(0, 0, CARD_W, CARD_H);
      const beat = (lt * 1.35) % 1, bounce = Math.abs(Math.sin(lt * Math.PI * 2.6));
      drawBean(cg, { kit: S.hussKit || S.kit, face: beat < 0.5 ? 'laugh' : 'smug', pose: 'hold', bob: bounce, squash: beat < 0.15 ? 0.6 : 0, hat: null });
      cg.fillStyle = '#c98a4a'; cg.strokeStyle = INK; cg.lineWidth = 8; cg.beginPath(); cg.arc(250, 600 - bounce * 120, 40, 0, 7); cg.fill(); cg.stroke(); // dribbled ball
      const w = 260 * pop, h = w * CARD_H / CARD_W; g.drawImage(c, W - w - 10, H - h + 40 * (1 - pop) - 20, w, h);
      // HUSS! pops on each beat
      for (const b of [0.05, 0.75, 1.45]) { const k = lt - b; if (k < 0 || k > 0.6) continue; const s = back(clamp(k / 0.18, 0, 1)), a = 1 - clamp((k - 0.4) / 0.2, 0, 1);
        g.save(); g.globalAlpha = a; g.translate(W - 150 + (b * 40 - 30), H - 330 - b * 60); g.rotate(-0.12 + b * 0.08); g.scale(s, s);
        g.font = '900 78px "Barlow Condensed", Impact, sans-serif'; g.textAlign = 'center'; g.lineJoin = 'round'; g.lineWidth = 14; g.strokeStyle = INK; g.strokeText('HUSS!', 0, 0); g.fillStyle = '#ffd23d'; g.fillText('HUSS!', 0, 0); g.restore(); }
    }
  }

  window.renderFrame = f => {
    const t = f / FPS; let si = 0; while (si + 1 < starts.length && t >= starts[si + 1]) si++;
    const shot = S.shots[si], lt = t - starts[si], len = (si + 1 < starts.length ? starts[si + 1] : DUR) - starts[si], u = clamp(lt / len, 0, 1);
    const set = WORLD.use(shot.set, shot.opts || {});
    E.light(shot.light || 'day', shot.focus || [0, 0, 0]);
    // set animation hooks (locomotive moving, etc.)
    if (set.userData.loco && shot.locoX) set.userData.loco.position.x = val(shot.locoX, lt, u);
    // actors
    const acts = shot.actors || []; cards.forEach(c => c.visible = false); blobs.forEach(b => b.visible = false);
    const camState = camFromKeys(shot.cam, lt, si);
    acts.forEach((a, i) => {
      const m = getCard(i); m.visible = true; let x = val(a.x, lt, u), z = val(a.z, lt, u), walking = false;
      if (a.walk) { const [x0, z0, x1, z1, t0, t1] = a.walk, k = clamp((lt - t0) / (t1 - t0), 0, 1); x = lerp(x0, x1, k); z = lerp(z0, z1, k); walking = k > 0 && k < 1; }
      const y = val(a.y || 0, lt, u), seed = i * 1.7 + si;
      const hop = a.hop ? Math.abs(Math.sin(lt * a.hop)) * 0.25 : 0;
      m.position.set(x, y + hop, z); const sc = a.scale || 1; m.scale.setScalar(sc);
      m.rotation.y = Math.atan2(camState.pos[0] - x, camState.pos[2] - z);
      const bob = Math.sin(lt * (walking ? 9 : 2.6) + seed) * (walking ? 0.6 : 0.35), blink = ((lt + seed * 0.7) % 3.1) < 0.12;
      paintCard(m, { kind: a.kind || 'bean', outfit: a.outfit, kit: a.kit, num: a.num, hat: a.hat, prop: a.prop, skin: a.skin, hair: a.hair,
        face: keyed(a.faceAt, lt, val(a.face || 'smile', lt, u)), pose: keyed(a.poseAt, lt, val(a.pose || 'hang', lt, u)), bob, blink: a.kind === 'dog' ? false : blink,
        step: walking ? Math.sin(lt * 9 + seed) : 0, armSwing: walking ? Math.sin(lt * 9 + seed) * 0.8 : Math.sin(lt * 1.8 + seed) * 0.15, look: Math.sin(lt * 0.8 + seed) * 0.6, t: lt });
      const b = getBlob(i); b.visible = true; b.position.set(x, 0.03, z); b.scale.setScalar(sc * (a.kind === 'dog' ? 1.6 : 1));
    });
    // effects
    smokes.forEach(s => s.visible = false); coins.forEach(c => c.visible = false); conf.forEach(c => c.visible = false);
    const fx = shot.fx || [];
    if (fx.includes('smoke')) { const anchors = []; set.updateMatrixWorld(true); set.traverse(o => { if (o !== set && o.userData.smoke) o.userData.smoke.forEach(v => anchors.push(o.localToWorld(v.clone()))); });
      anchors.forEach((p, ai) => { for (let k = 0; k < 10; k++) { const s = smokes[ai * 10 + k]; if (!s) break; const ph = ((t * 0.35 + k / 10 + ai * 0.13) % 1);
        s.visible = true; s.position.set(p.x + ph * 3 + Math.sin(k + t) * 0.4, p.y + ph * 7, p.z - ph * 1.5); s.scale.setScalar(1 + ph * 4); s.material.opacity = 0.8 * (1 - ph); } }); }
    if (fx.includes('coins')) coins.forEach((c, i) => { const ph = (lt * 0.6 + rnd(i)) % 1; c.visible = true; c.position.set((rnd(i + 9) - 0.5) * 6 + (shot.focus || [0])[0], 6 - ph * 6.5, (rnd(i + 3) - 0.5) * 3 + (shot.focus || [0, 0, 0])[2]); c.rotation.set(lt * 5 + i, lt * 3, 0); });
    if (fx.includes('confetti')) conf.forEach((c, i) => { const ph = (lt * 0.4 + rnd(i)) % 1; c.visible = true; c.position.set((rnd(i + 5) - 0.5) * 10 + (shot.focus || [0])[0], 7 - ph * 7.5, (rnd(i + 7) - 0.5) * 6 + (shot.focus || [0, 0, 0])[2]); c.rotation.set(lt * 4 + i, lt * 6 + i * 2, 0); });
    const flash = shot.flash ? clamp(1 - lt / 0.2, 0, 1) : 0;
    const g = E.draw(camState, shot.dof, flash);
    hussOverlay(g, t);
    return true;
  };
  window.TOTAL = N; window.ready = true;
})();
