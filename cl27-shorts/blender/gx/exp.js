// Export the Night Cup game's boards, ribbons, screens, flags and banners (geometry in world space + textures) for Blender.
const fs = require('fs'); const path = require('path'); const { open } = require('./inv.js');
const PAIRS = [['che', 'tot', 'che_tot'], ['bar', 'mun', 'bar_mun']];
(async () => {
  const { b, p } = await open();
  for (const [h, a, tag] of PAIRS) {
    const dir = path.join(__dirname, 'export', tag), td = path.join(dir, 'tex'); fs.mkdirSync(td, { recursive: true });
    const res = await p.evaluate(([h, a]) => {
      const { G, W3, SCN, TEX, TEAMS, buildStandFaces, buildLED, refreshWorldTeams, buildBoards3, buildRibbon3, drawBigScreen, setSel } = window.__GAME;
      const T = id => TEAMS.find(t => t.id === id); const A = T(h), Bt = T(a); setSel(A, Bt);
      try { buildStandFaces(A, Bt); } catch (e) {}
      buildLED(A, Bt); try { refreshWorldTeams(); } catch (e) {} buildBoards3(); buildRibbon3();
      const st = G.state; G.state = 'play'; G.score = [0, 0]; G.dur = G.dur || 90; G.clock = G.dur * 0.7; G.half = 2; G.addMin = 0; G.scorers = []; G.stats = { passes: [312, 287], shots: [6, 3], poss: [55, 45] };
      drawBigScreen(true); G.state = st;
      SCN.updateMatrixWorld(true);
      const texId = new Map(), texData = {}, matId = new Map(), mats = {}, meshes = [];
      const roleOf = m => m === W3.ledMat ? 'led' : (W3.ledEndMats || []).includes(m) ? 'ledEnd' : (W3.screenMats || []).includes(m) ? 'screen' : (W3.ribbon || []).some(r => r.material === m) ? 'ribbon' : null;
      const tex = t => {
        if (!t || !t.image) return null; const im = t.image;
        if (texId.has(im)) return texId.get(im);
        const id = 't' + texId.size; texId.set(im, id);
        let c = im; if (!(im instanceof HTMLCanvasElement)) { c = document.createElement('canvas'); c.width = im.width || im.videoWidth; c.height = im.height || im.videoHeight; c.getContext('2d').drawImage(im, 0, 0); }
        try { texData[id] = c.toDataURL('image/png'); } catch (e) { texData[id] = null; }
        return id;
      };
      const mat = m => {
        if (matId.has(m)) return matId.get(m); const id = matId.size; matId.set(m, id);
        mats[id] = { type: m.type, color: m.color ? [m.color.r, m.color.g, m.color.b] : [1, 1, 1], map: m.map ? tex(m.map) : null, transparent: !!m.transparent, opacity: m.opacity,
          additive: m.blending === THREE.AdditiveBlending, side: m.side, repeat: m.map ? [m.map.repeat.x, m.map.repeat.y] : [1, 1], offset: m.map ? [m.map.offset.x, m.map.offset.y] : [0, 0], role: roleOf(m) };
        return id;
      };
      SCN.traverse(o => {
        if (!o.isMesh || o.isInstancedMesh || o.isSkinnedMesh || o === W3.model) return;
        for (let q = o; q; q = q.parent) if (!q.visible) return;
        const g = o.geometry; if (!g.attributes.position) return;
        const bb = new THREE.Box3().setFromObject(o), sz = bb.getSize(new THREE.Vector3());
        if (Math.max(sz.x, sz.y, sz.z) < 0.6) return;                                        // ball, small bits
        if (bb.max.y < 0.35 && Math.max(sz.x, sz.z) > 40) return;                            // pitch planes and lines
        if (sz.x > 300 || sz.z > 300) return;                                               // sky / ground
        if (Math.abs((bb.min.x + bb.max.x) / 2) > 49 && Math.abs((bb.min.x + bb.max.x) / 2) < 57 && Math.abs((bb.min.z + bb.max.z) / 2) < 5 && bb.max.y < 3.2) return; // goals
        const ms = Array.isArray(o.material) ? o.material : [o.material];
        if (ms.some(m => m.type === 'ShaderMaterial' || m.type === 'RawShaderMaterial')) return;
        const P = g.attributes.position, U = g.attributes.uv, v = new THREE.Vector3(), pos = [], uv = [];
        for (let i = 0; i < P.count; i++) { v.fromBufferAttribute(P, i).applyMatrix4(o.matrixWorld); pos.push(+v.x.toFixed(4), +(-v.z).toFixed(4), +v.y.toFixed(4)); if (U) uv.push(U.getX(i), U.getY(i)); }
        let idx = g.index ? Array.from(g.index.array) : [...Array(P.count).keys()];
        const det = o.matrixWorld.determinant(); if (det < 0) for (let i = 0; i < idx.length; i += 3) { const t = idx[i + 1]; idx[i + 1] = idx[i + 2]; idx[i + 2] = t; }
        const groups = g.groups && g.groups.length ? g.groups.map(gr => [gr.start, gr.count, mat(ms[gr.materialIndex] || ms[0])]) : [[0, idx.length, mat(ms[0])]];
        meshes.push({ name: o.name || g.type, pos, uv, idx, groups, size: [sz.x, sz.y, sz.z].map(x => +x.toFixed(1)) });
      });
      const pages = {}; TEX.led.pages.forEach((c, i) => pages['ledpage' + i] = c.toDataURL('image/png')); TEX.led.goalPages.forEach((c, i) => pages['goalpage' + i] = c.toDataURL('image/png'));
      pages['promo'] = W3.promoCanvas ? W3.promoCanvas.toDataURL('image/png') : null; pages['score'] = W3.bigCanvas.toDataURL('image/png');
      return { meshes, mats, texData, pages };
    }, [h, a]);
    const save = (name, data) => { if (data) fs.writeFileSync(path.join(td, name + '.png'), Buffer.from(data.split(',')[1], 'base64')); };
    for (const [id, d] of Object.entries(res.texData)) save(id, d);
    for (const [id, d] of Object.entries(res.pages)) save(id, d);
    fs.writeFileSync(path.join(dir, 'meshes.json'), JSON.stringify(res.meshes)); fs.writeFileSync(path.join(dir, 'materials.json'), JSON.stringify(res.mats, null, 1));
    console.log('EXPORTED', tag, res.meshes.length, 'meshes', Object.keys(res.mats).length, 'materials', Object.keys(res.texData).length, 'textures');
    for (const m of res.meshes) console.log('  ', m.name, m.pos.length / 3, 'v', JSON.stringify(m.size), m.groups.map(g => res.mats[g[2]].type + (res.mats[g[2]].role ? ':' + res.mats[g[2]].role : '')).join(','));
  }
  await b.close();
})();
