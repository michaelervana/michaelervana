// Cartoon 3D engine: toon world with ink hulls, painted textures, bean-head cards, gliding cameras, depth of field.
// Everything is a pure function of the frame number: window.renderFrame(f) draws frame f.
const W = 540, H = 960, FPS = 30;
const E = {};
(function () {
  const canvas = document.getElementById('gl'), out = document.getElementById('out'), ox = out.getContext('2d');
  const R = new THREE.WebGLRenderer({ canvas, antialias: false, preserveDrawingBuffer: true });
  R.setSize(W, H, false); R.setPixelRatio(1); R.outputEncoding = THREE.sRGBEncoding; R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
  const cam = new THREE.PerspectiveCamera(40, W / H, 0.1, 600);
  const rt = new THREE.WebGLRenderTarget(W, H, { samples: 4 }); rt.depthTexture = new THREE.DepthTexture(W, H); rt.depthTexture.type = THREE.UnsignedIntType;
  // toon ramp: 2 steps + highlight
  const ramp = new THREE.DataTexture(new Uint8Array([90, 90, 90, 255, 175, 175, 175, 255, 255, 255, 255, 255]), 3, 1, THREE.RGBAFormat); ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
  const texCache = {};
  const T = (name, fn, rx = 1, ry = 1) => { const k = name + rx + 'x' + ry; return texCache[k] || (texCache[k] = P.tex(fn(), rx, ry)); };
  E.T = T;
  E.toon = (col, map) => new THREE.MeshToonMaterial({ color: col || 0xffffff, map: map || null, gradientMap: ramp });
  const inkMat = new THREE.MeshBasicMaterial({ color: 0x241226, side: THREE.BackSide, fog: false });
  // add a mesh with an ink hull (back faces, pushed out along the normals in view space so the line keeps its width)
  inkMat.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', `vec4 mvPosition = modelViewMatrix * vec4(transformed, 1.0);
    vec3 nv = normalize(normalMatrix * normal); mvPosition.xyz += nv * (0.035 * max(1.0, -mvPosition.z * 0.09));
    gl_Position = projectionMatrix * mvPosition;`); };
  E.add = (parent, geo, mat, p = [0, 0, 0], r = [0, 0, 0], ink = true, shadow = true) => {
    const m = new THREE.Mesh(geo, mat); m.position.set(...p); m.rotation.set(...r); m.castShadow = shadow; m.receiveShadow = true; parent.add(m);
    if (ink) { const h = new THREE.Mesh(geo, inkMat); m.add(h); }
    return m;
  };
  // box with texture repeated at constant texel density (1 repeat per `d` metres)
  E.tbox = (parent, w, h, d, mat, p, r, dens = 2) => {
    const g = new THREE.BoxGeometry(w, h, d), uv = g.attributes.uv, pos = g.attributes.position, nrm = g.attributes.normal;
    for (let i = 0; i < uv.count; i++) { const nx = Math.abs(nrm.getX(i)), ny = Math.abs(nrm.getY(i)); const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
      if (nx > 0.5) uv.setXY(i, z / dens, y / dens); else if (ny > 0.5) uv.setXY(i, x / dens, z / dens); else uv.setXY(i, x / dens, y / dens); }
    return E.add(parent, g, mat, p, r);
  };
  // scene, sky, light
  const scene = new THREE.Scene(); E.scene = scene;
  const hemi = new THREE.HemisphereLight(0xcfe3ff, 0x5a6b3a, 0.65); scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1d6, 1.15); sun.castShadow = true; sun.shadow.mapSize.set(1024, 1024); sun.shadow.bias = -0.0008; sun.shadow.normalBias = 0.03;
  Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 120 }); scene.add(sun, sun.target);
  const skyU = { top: { value: new THREE.Color() }, hor: { value: new THREE.Color() } };
  const sky = new THREE.Mesh(new THREE.SphereGeometry(400, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, uniforms: skyU,
    vertexShader: 'varying vec3 vP; void main(){ vP = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
    fragmentShader: 'uniform vec3 top, hor; varying vec3 vP; void main(){ float h = clamp(normalize(vP).y, 0., 1.); gl_FragColor = vec4(mix(hor, top, pow(h, .6)), 1.); }' }));
  sky.renderOrder = -1; scene.add(sky);
  scene.fog = new THREE.Fog(0xcfe3ff, 40, 220);
  const LIGHTS = {
    day: { top: '#4f8fe0', hor: '#cfe6ff', sun: '#fff1d6', si: 1.15, hemi: 0.65, az: -0.8, el: 0.9, sat: 1.12, gain: 1.0 },
    golden: { top: '#5c6fbf', hor: '#ffc98a', sun: '#ffc07a', si: 1.25, hemi: 0.5, az: 0.9, el: 0.35, sat: 1.18, gain: 1.0 },
    night: { top: '#0d1640', hor: '#3a4a8a', sun: '#9fb4ff', si: 0.7, hemi: 0.45, az: -0.4, el: 0.8, sat: 1.05, gain: 1.05 },
    grey: { top: '#6c7a8c', hor: '#c9ced3', sun: '#f0ece0', si: 0.9, hemi: 0.7, az: -0.6, el: 0.9, sat: 0.95, gain: 1.0 },
  };
  let grade = LIGHTS.day;
  E.light = (name, focus) => { const L = LIGHTS[name] || LIGHTS.day; grade = L; skyU.top.value.set(L.top); skyU.hor.value.set(L.hor); scene.fog.color.set(L.hor);
    sun.color.set(L.sun); sun.intensity = L.si; hemi.intensity = L.hemi; hemi.color.set(L.hor);
    const c = focus || [0, 0, 0]; sun.target.position.set(c[0], 0, c[2]); sun.position.set(c[0] + Math.cos(L.az) * 40 * Math.cos(L.el), 40 * Math.sin(L.el) + 5, c[2] + Math.sin(L.az) * 40 * Math.cos(L.el)); sun.target.updateMatrixWorld(); };
  // painted cloud billboards
  const clouds = new THREE.Group(); scene.add(clouds);
  for (let i = 0; i < 9; i++) { const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: T('cloud', P.cloud), fog: false, depthWrite: false })); const a = i / 9 * Math.PI * 2;
    s.position.set(Math.cos(a) * 160, 45 + (i % 3) * 14, Math.sin(a) * 160); s.scale.set(70, 35, 1); clouds.add(s); }
  E.clouds = clouds;
  // post: depth of field (per-sample circle of confusion test) + grade + vignette + flash
  const post = new THREE.ShaderMaterial({ uniforms: { tC: { value: rt.texture }, tD: { value: rt.depthTexture }, near: { value: 0.1 }, far: { value: 600 }, focus: { value: 6 }, coc: { value: 8 }, sat: { value: 1.1 }, gain: { value: 1 }, flash: { value: 0 }, px: { value: new THREE.Vector2(1 / W, 1 / H) } },
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }',
    fragmentShader: `uniform sampler2D tC, tD; uniform float near, far, focus, coc, sat, gain, flash; uniform vec2 px; varying vec2 vUv;
      float lin(float d){ float z = d * 2. - 1.; return 2. * near * far / (far + near - z * (far - near)); }
      float cocAt(vec2 uv){ float z = lin(texture2D(tD, uv).r); return clamp(abs(z - focus) / max(z, 0.5) * coc, 0., coc); }
      void main(){
        float c0 = cocAt(vUv); vec3 acc = texture2D(tC, vUv).rgb; float wsum = 1.;
        if (coc > 0.5) for (int i = 0; i < 24; i++) { float a = float(i) * 2.39996, r = sqrt(float(i) / 24.) * c0; vec2 o = vec2(cos(a), sin(a)) * r * px;
          float ci = cocAt(vUv + o); float w = smoothstep(r - 1., r + 1., ci + 0.5); acc += texture2D(tC, vUv + o).rgb * w; wsum += w; }
        vec3 c = acc / wsum * gain; float l = dot(c, vec3(.299,.587,.114)); c = mix(vec3(l), c, sat);
        vec2 d = vUv - .5; c *= 1. - dot(d, d) * .55; c = mix(c, vec3(1.), flash);
        gl_FragColor = vec4(c, 1.); }` });
  const pScene = new THREE.Scene(), pCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1); pScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), post));
  // rendering one frame
  E.draw = (camState, dof, flash) => {
    cam.position.set(...camState.pos); cam.fov = camState.fov || 40; cam.updateProjectionMatrix(); cam.lookAt(...camState.target);
    if (camState.roll) cam.rotateZ(camState.roll);
    clouds.position.set(cam.position.x * 0.9, 0, cam.position.z * 0.9);
    post.uniforms.focus.value = dof ? dof.focus : 10; post.uniforms.coc.value = dof ? dof.coc : 0; post.uniforms.sat.value = grade.sat; post.uniforms.gain.value = grade.gain; post.uniforms.flash.value = flash || 0;
    R.setRenderTarget(rt); R.render(scene, cam); R.setRenderTarget(null); R.render(pScene, pCam);
    ox.drawImage(canvas, 0, 0, W, H);
    return ox;
  };
  E.cam = cam; E.W = W; E.H = H;
})();

// ---------- motion helpers ----------
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const smoother = t => { t = clamp(t, 0, 1); return t * t * t * (t * (t * 6 - 15) + 10); };
const easeOut = t => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
const back = t => { t = clamp(t, 0, 1); const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const lerp = (a, b, t) => a + (b - a) * t, lerp3 = (a, b, t) => a.map((v, i) => lerp(v, b[i], t));
// camera keys [{t, pos, target, fov}] in shot-local seconds; smootherstep glide between keys plus a slow creep so nothing is static
function camFromKeys(keys, t, seed = 0) {
  let i = 0; while (i < keys.length - 1 && t > keys[i + 1].t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)], u = b === a ? 0 : smoother((t - a.t) / Math.max(0.01, b.t - a.t));
  const pos = lerp3(a.pos, b.pos, u), target = lerp3(a.target, b.target, u), fov = lerp(a.fov || 40, b.fov || 40, u);
  pos[0] += Math.sin(t * 0.7 + seed) * 0.06; pos[1] += Math.sin(t * 0.9 + seed * 2) * 0.04;
  return { pos, target, fov, roll: lerp(a.roll || 0, b.roll || 0, u) };
}
